# 13 · Expressões — a linguagem dentro dos campos

`Nível: intermediário` · `Verificado em n8n 2.36.9, 01/09/2026`

---

Uma expressão é um pedaço de JavaScript avaliado no meio de um campo de parâmetro.
É o que transforma um fluxo estático em um programa.

---

## 1. Mecânica: o que acontece quando você digita `{{ }}`

Um campo de nó tem dois modos: **Fixed** (valor literal) e **Expression**.
No JSON do workflow, um campo em modo expressão é uma string **começando por `=`**:

```json
"responseBody": "={{ JSON.stringify($json) }}"
```

E o `=` pode preceder texto misto:

```json
"fileName": "=/files/relatorio-{{ $now.toFormat('yyyy-LL-dd') }}.csv"
```

> Ao editar JSON de workflow à mão, **esquecer o `=` é o erro nº 1**: o campo passa
> a valer literalmente `{{ ... }}`, e o sintoma é um nome de arquivo com chaves
> dentro, ou uma URL com `{{` no meio.

### Onde a expressão roda

O n8n 2.x avalia expressões num **isolado V8** — um contexto JavaScript separado,
sem acesso a `require`, a disco ou a rede. Isso é proposital: uma expressão é um
*valor calculado*, não um lugar para efeitos colaterais. É também por isso que
existe uma variável de ambiente para configurar o pool de isolados
(`expression-engine`) em instâncias com carga alta.

### Uma expressão é avaliada **por item**

Se o nó recebe 5 itens, a expressão é avaliada 5 vezes, e `$json` é diferente a
cada vez. É o que faz "criar 5 cards" funcionar sem laço.

---

## 2. As variáveis, agrupadas por intenção

### 2.1 "Quero o dado que está entrando"

| Expressão | Devolve |
|---|---|
| `$json` | O item atual (o `json` dele) |
| `$binary` | Os binários do item atual |
| `$input.all()` | Todos os itens de entrada |
| `$input.first()` / `.last()` | Primeiro/último |
| `$input.item` | O item atual (equivalente a `{json: $json}`) |
| `$itemIndex` | Índice do item atual (**não existe no Code node**) |

### 2.2 "Quero dado de um nó anterior"

| Expressão | Devolve |
|---|---|
| `$('Nome do Nó').item` | O item **correspondente** (usa `pairedItem`) |
| `$('Nome do Nó').first()` / `.last()` | Primeiro/último item daquele nó |
| `$('Nome do Nó').all()` | Todos |
| `$('Nome do Nó').all(0, 1)` | Todos, de uma saída e execução específicas |
| `$('Nome do Nó').params` | Os **parâmetros** daquele nó, não os dados |
| `$('Nome do Nó').isExecuted` | Se aquele nó chegou a rodar |
| `$prevNode.name` | Nome do nó que alimentou este |

> **Armadilha:** `$('Nó')` casa pelo **nome**. Renomear o nó quebra todas as
> expressões que o citam, e o n8n **não** as atualiza. Renomeie cedo ou nunca.

### 2.3 "Quero saber sobre o ambiente"

| Expressão | Devolve |
|---|---|
| `$workflow.id` / `.name` / `.active` | Sobre o fluxo |
| `$execution.id` | ID desta execução — **use nos logs** |
| `$execution.mode` | `test` ou `production` |
| `$execution.resumeUrl` | URL para retomar um Wait |
| `$execution.customData` | Metadados pesquisáveis na lista de execuções |
| `$runIndex` | Quantas vezes este nó já rodou (base 0) — essencial em laços |
| `$nodeVersion` | `typeVersion` do nó atual |
| `$vars.X` | Variáveis do ambiente (recurso licenciado) |
| `$env.X` | Variável de ambiente do processo (**bloqueável**) |
| `$secrets.cofre.chave` | Cofre externo (Enterprise) |

### 2.4 "Quero guardar estado entre execuções"

```javascript
const s = $getWorkflowStaticData('global');   // ou 'node'
```

O único estado persistente sem banco. Salvo junto ao workflow, **só em execuções de
produção**. Bom para marca-d'água de sincronização; **ruim** para qualquer coisa
que precise de garantia sob concorrência. Ver [18-erros-e-confiabilidade.md](18-erros-e-confiabilidade.md).

---

## 3. Os métodos estendidos (data transformation functions)

O n8n acrescenta métodos aos tipos nativos. Eles existem **no editor de expressões**;
no Code node, você tem JavaScript puro.

```
{{ $json.email.isEmail() }}                     → true/false
{{ $json.texto.removeTags().trim() }}           → HTML limpo
{{ $json.doc.replaceAll(/\D/g, '') }}           → só dígitos
{{ $json.valores.sum() }}                       → soma do array
{{ $json.valores.unique().length }}             → distintos
{{ $json.lista.pluck('nome') }}                 → extrai uma coluna
{{ $json.obj.hasField('cpf') }}                 → existe a chave?
{{ $json.id.hash('sha256') }}                   → chave de deduplicação
{{ $if($json.valor > 100, 'alto', 'baixo') }}   → ternário legível
{{ $ifEmpty($json.nome, 'sem nome') }}          → valor padrão
{{ $jmespath($json, "itens[?qtd>`2`].sku") }}   → consulta em JSON aninhado
```

**Recomendação:** conheça `$if`, `$ifEmpty` e `$jmespath` de cor. Os três eliminam
a maior parte dos nós Code que a gente escreve por reflexo.

---

## 4. Datas: Luxon, e a pegadinha do Code node

O n8n usa **Luxon**. `$now` e `$today` já são objetos `DateTime`.

```
{{ $now.toISO() }}                                  2026-09-01T10:15:00.000-03:00
{{ $now.toFormat('dd/MM/yyyy HH:mm') }}             01/09/2026 10:15
{{ $now.startOf('day') }}                           hoje 00:00
{{ $now.minus(1, 'month').toFormat('yyyy-LL') }}    2026-08
{{ $json.data.toDateTime().diffNow('days').days }}  dias até a data
{{ DateTime.fromFormat($json.d, 'dd/MM/yyyy').toISO() }}
```

> **A pegadinha documentada.** No **editor de expressões**, `plus(7, 'days')`
> funciona porque o n8n estende o Luxon. No **node Code**, roda o Luxon nativo, e
> a assinatura é `plus({ days: 7 })`. O detalhe cruel: `plus(7, 'days')` no Code
> node **não dá erro** — simplesmente não faz o que você quer. Sempre que um cálculo
> de data der resultado estranho dentro do Code node, suspeite disso primeiro.

**Fuso.** O fuso padrão vem de `GENERIC_TIMEZONE`; o workflow pode sobrescrever.
Regra que economiza noites: **armazene sempre em UTC (`toISO()`), formate só na
saída (`setZone(...).toFormat(...)`)**.

---

## 5. Padrões prontos

**Valor com fallback em cascata:**
```
{{ $json.apelido || $json.nome || 'Cliente' }}
```

**Acesso seguro a caminho profundo:**
```
{{ $json.pedido?.entrega?.cep ?? 'sem cep' }}
```

**Montar corpo JSON completo:**
```
{{ JSON.stringify({ id: $json.id, total: $json.itens.sum(), quando: $now.toISO() }) }}
```

**Idempotência: chave determinística a partir do conteúdo:**
```
{{ (String($json.cliente) + '|' + String($json.valor)).hash('sha256') }}
```

**Nome de arquivo com data e ID de execução (rastreável):**
```
=/files/export-{{ $now.toFormat('yyyyLLdd') }}-{{ $execution.id }}.csv
```

**Somente no primeiro item de um lote (evita notificação repetida):**
```
{{ $itemIndex === 0 ? 'sim' : 'nao' }}
```

---

## 6. Depurar expressão

1. **O painel de expressão mostra o resultado ao vivo**, com o item corrente.
   Se está `undefined`, o caminho está errado — não o valor.
2. **Arraste o campo da coluna INPUT** em vez de digitar. O n8n gera o caminho
   certo, inclusive com colchetes onde é preciso.
3. **Erro comum nº 1:** dado de webhook está em `$json.body.x`, não `$json.x`.
4. **Erro comum nº 2:** o nó anterior devolveu um array de um item; você quer
   `$json.dados[0].x`, não `$json.dados.x`.
5. **Erro comum nº 3:** tipo. `"10" > 9` é `true`, mas `"10" > "9"` é `false`
   (comparação de string). Converta explicitamente: `Number($json.valor)`.
6. **Quando a expressão fica com mais de duas linhas, ela deveria ser um node Code.**
   Expressão longa não tem como ser testada nem lida.

---

## 7. Segurança de expressões

Uma expressão é código executado pelo servidor n8n. Três consequências:

- **`$env` expõe as variáveis do processo** — inclusive senha do banco e chave de
  criptografia. Em instância com mais de uma pessoa, ligue
  `N8N_BLOCK_ENV_ACCESS_IN_NODE=true`. Foi o que fizemos no
  [projeto-modelo](07-projeto-modelo/README.md).
- **Nunca interpole entrada externa em SQL, shell ou HTML.** Use os parâmetros
  do nó (`$1`, `$2` no Postgres). Ver [22-seguranca.md](22-seguranca.md).
- **Quem pode editar um workflow executa código no servidor.** "Acesso de edição"
  é, na prática, acesso de execução de código. Trate as permissões com esse peso.

---

## Autoteste

1. Como um campo em modo expressão aparece no JSON do workflow?
2. Uma expressão com 5 itens de entrada é avaliada quantas vezes?
3. Qual a diferença entre `$('Nó').item` e `$('Nó').first()`?
4. Por que renomear um nó é arriscado?
5. Escreva a expressão que devolve `'alto'` se `valor > 100`, senão `'baixo'`.
6. Por que `plus(7, 'days')` falha silenciosamente no Code node?
7. Onde armazenar datas e onde formatá-las? Por quê?
8. `"10" > "9"` dá o quê, e por quê? Como corrigir?
9. Cite duas razões de segurança para bloquear `$env`.
10. Quando uma expressão deve virar um node Code?

---

*Anterior: [12-o-modelo-de-dados.md](12-o-modelo-de-dados.md) · Próximo: [14-nos-e-integracoes.md](14-nos-e-integracoes.md)*
