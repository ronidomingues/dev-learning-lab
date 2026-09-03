# 13 · Tokens de versão — o que carimbar e por quê

`Nível: intermediário → avançado` · `Atualizado em: 14/08/2026`

O token de versão é a peça central. Escolher mal produz sistemas que **parecem** protegidos e
não estão. Este arquivo enumera as opções, o que cada uma garante de fato, e como cada uma
falha.

---

## 1. O contrato de um token

Um valor `t` serve como token de versão de um dado `x` se, e somente se:

| Propriedade | Enunciado | O que quebra se faltar |
|---|---|---|
| **P1 · Muda a cada escrita** | toda escrita aceita produz `t' ≠ t` | duas escritas parecem uma; conflito não detectado |
| **P2 · Não se repete** | nenhum `t` já usado volta a ocorrer | **problema ABA** (seção 4) |
| **P3 · Gerado pelo detentor** | quem guarda o dado gera o token, nunca quem escreve | dois clientes podem escolher o mesmo valor |
| **P4 · Comparável por igualdade** | basta `=`; ordem é opcional | — |
| **P5 · Observável na leitura** | quem lê recebe o token junto | não há o que devolver na escrita |

Ordem (`t' > t`) **não** é exigida. Ela é conveniente para diagnóstico ("o cliente estava 3
versões atrás") e desnecessária para correção.

**P2 é a que quase todo mundo esquece.** É ela que o `updated_at` viola quando duas escritas
caem no mesmo milissegundo, e é ela que o `xmin` do PostgreSQL viola quando o contador de
transações dá a volta.

---

## 2. As opções, comparadas

| Token | P1 | P2 | Ordem | Vaza volume? | Custo | Onde é a escolha certa |
|---|---|---|---|---|---|---|
| **Inteiro incremental** | ✔ | ✔ (até estourar) | ✔ | **sim** | 4–8 bytes, `+1` | padrão para uso interno |
| **Timestamp de atualização** | ~ | **✘** | ✔ | sim | grátis se já existe | nunca como token único |
| **UUID por escrita** | ✔ | ✔ | ✘ | não | 16 bytes, gerar | ETag público |
| **Hash do conteúdo** | ~ | ✔ | ✘ | não | CPU + canonicalização | ETag público, sincronização |
| **`xmin` (PostgreSQL)** | ✔ | ~ | ~ | sim | zero | uso interno e efêmero |
| **`rowversion` (SQL Server)** | ✔ | ✔ | ✔ | sim (do banco) | zero | uso interno no SQL Server |
| **Sequência global / Snowflake** | ✔ | ✔ | ✔ | parcialmente | contenção na sequência | quando é preciso ordenar entre linhas |
| **Vetor de versões / vector clock** | ✔ | ✔ | parcial | sim | O(nº de réplicas) | multi-mestre, offline-first |

Legenda: ✔ garante · ~ garante com ressalva · ✘ não garante.

---

## 3. Cada uma em detalhe

### 3.1 Inteiro incremental — o padrão

```sql
version INTEGER NOT NULL DEFAULT 1
...
UPDATE t SET ..., version = version + 1 WHERE id = ? AND version = ?
```

**Vantagens:** trivial, ordenável, legível em log, barato de indexar, e a diferença entre
`versao_lida` e `versao_atual` diz **quantas** escritas você perdeu de vista — um dado
excelente de diagnóstico.

**O que checar:** o incremento tem de ser calculado **pelo banco** (`version = version + 1`),
não pelo cliente. Se o cliente enviar `version = 8`, dois clientes podem enviar `8` e o
próximo conflito passa despercebido.

**Estouro:** com `INTEGER` de 32 bits com sinal, o limite é 2.147.483.647 escritas na
**mesma linha**. Uma linha com 100 escritas por segundo ininterruptas levaria ~680 anos.
Não é um risco real, mas use `BIGINT` se o custo for irrelevante — e ele é.

**O que vaza:** o número diz quantas vezes o recurso foi escrito. Num ETag público, isso é
informação de negócio (quantas vezes um pedido foi alterado, quanto um documento é editado).
Se isso importa, vá para hash ou UUID.

### 3.2 Timestamp — a armadilha mais popular

```sql
-- NÃO FAÇA ISTO como proteção principal
UPDATE t SET ..., updated_at = now() WHERE id = ? AND updated_at = ?
```

Parece elegante — a coluna já existe. Quatro modos de falha, todos reais:

1. **Resolução.** Duas escritas no mesmo instante representável recebem o mesmo timestamp.
   Com resolução de segundo (o caso de `If-Unmodified-Since`, e de vários bancos), é
   trivialmente reproduzível.
2. **Relógio para trás.** NTP corrige o relógio da máquina, o horário de verão muda, a VM
   é migrada. Um timestamp menor que o anterior faz a guarda aceitar escritas que deveria
   recusar.
3. **Relógio de quem?** Se o timestamp vier da aplicação e houver várias instâncias, você
   está comparando relógios diferentes. Use `now()`/`CURRENT_TIMESTAMP` **do banco**, sempre.
4. **Precisão na viagem.** O timestamp passa por JSON, por um driver, por um `DateTime` de
   linguagem — e perde microssegundos no caminho. A comparação de igualdade falha para
   sempre, e o sintoma (412 eterno) não sugere a causa.

**Quando é aceitável:** como token **secundário**, junto de um inteiro, para diagnóstico.
Ou quando a resolução é de nanossegundos e há um único escritor lógico. Não é o seu caso.

### 3.3 UUID por escrita

```sql
etag UUID NOT NULL DEFAULT gen_random_uuid()
...
UPDATE t SET ..., etag = gen_random_uuid() WHERE id = ? AND etag = ?
```

**Vantagem:** não vaza nada, não colide na prática (2⁻¹²² por sorteio), e é um ETag público
perfeito — opaco por construção, exatamente o que a RFC 9110 diz que um ETag deve ser.

**Desvantagem:** você perde a capacidade de dizer "o cliente estava 3 versões atrás". Perde
também a ordem, o que atrapalha depuração e certos algoritmos de sincronização.

**Recomendação:** se o token sai para fora do sistema, guarde **os dois** — um inteiro para
você e um UUID para o mundo.

### 3.4 Hash do conteúdo

```javascript
const etag = sha256(serializacaoCanonica(registro)).slice(0, 16);
```

Único token com uma propriedade que os outros não têm: **regravar conteúdo idêntico não muda
o token**. Isso significa que um salvamento inócuo (usuário abriu o formulário e clicou em
salvar sem mudar nada) **não invalida a leitura de mais ninguém**. Em sistemas com muitos
salvamentos redundantes, isso derruba a taxa de conflito de forma significativa.

Três exigências para funcionar:

1. **Serialização canônica.** Ordem de campos fixa, sem espaços variáveis, sem depender da
   ordem de chaves de um mapa. Sem isso, o mesmo conteúdo gera hashes diferentes e tudo vira
   conflito. Este é o erro que estraga a maioria das implementações.
2. **Escolher o que entra no hash.** Se `updated_at` entrar, a propriedade da seção acima se
   perde — o timestamp muda mesmo quando o conteúdo não muda.
3. **Custo de CPU.** Hashear a cada leitura e a cada escrita não é grátis. Guarde o hash numa
   **coluna**, atualizada por trigger ou pela aplicação, e volte a comparar com `WHERE hash = ?`
   — que é atômico, ao contrário de "ler, hashear, comparar, gravar".

Exemplo executável e a discussão do defeito de atomicidade:
[`06-exemplos.md` § 6](06-exemplos.md#6--token-por-hash-de-conteúdo).

### 3.5 `xmin` do PostgreSQL

Toda linha no PostgreSQL carrega, num campo de sistema, o ID da transação que a criou:

```sql
SELECT id, saldo, xmin FROM conta WHERE id = 1;
```

```sql
UPDATE conta SET saldo = 150 WHERE id = 1 AND xmin = 12345;
```

**Vantagem:** zero manutenção, zero coluna, zero risco de esquecer o `version = version + 1`.
O EF Core tem suporte de primeira classe (`UseXminAsConcurrencyToken()`).

**Onde falha, e é sério:**

- O `xmin` é um contador de 32 bits que **dá a volta** (*wraparound*). Depois do congelamento
  feito pelo `VACUUM`, linhas antigas recebem um valor especial. Um token guardado por muito
  tempo perde o significado.
- `VACUUM FULL`, `CLUSTER`, `pg_upgrade`, `pg_dump`/`restore` e replicação lógica **não
  preservam** o `xmin`. Depois de qualquer um deles, todos os tokens de todos os clientes
  ficam inválidos de uma vez.
- É **específico do PostgreSQL**. Você amarra a aplicação ao banco.

**Veredito, e é opinião fundamentada:** ótimo para janelas curtas dentro de uma requisição;
**não use** como ETag público, nem em qualquer token que sobreviva a uma manutenção.

### 3.6 `rowversion` do SQL Server

Um `binary(8)` mantido pelo banco, monotônico no **banco inteiro** (não por linha), atualizado
automaticamente em qualquer escrita.

**Vantagem:** impossível esquecer de incrementar — é a maior fonte de bug do inteiro manual.
**Ressalva:** é o tipo mais próximo do ideal, mas amarra você ao SQL Server, e o valor precisa
ser transportado como base64 se sair em JSON.

### 3.7 Vector clocks e o multi-mestre

Todos os tokens acima pressupõem **uma autoridade**: existe um lugar que sabe qual é a versão
atual. Quando há vários escritores independentes que se sincronizam depois (aplicativo offline,
replicação multi-mestre, dispositivos), essa premissa cai.

A generalização é o **relógio vetorial** (*vector clock*): em vez de um número, um mapa
`{réplica → contador}`. Comparando dois vetores você distingue três casos, em vez de dois:

```
A = {r1: 3, r2: 1}     B = {r1: 3, r2: 2}     ->  B descende de A  (sem conflito)
A = {r1: 4, r2: 1}     B = {r1: 3, r2: 2}     ->  CONCORRENTES     (conflito real)
A = {r1: 3, r2: 2}     B = {r1: 3, r2: 2}     ->  iguais
```

O ganho é exatamente esse terceiro estado: um contador único não consegue distinguir
"você está atrasado" de "nós divergimos". O custo é o tamanho (cresce com o número de
réplicas) e a complexidade de poda de réplicas mortas. Aprofundamento em
[`18-sistemas-distribuidos.md`](18-sistemas-distribuidos.md).

---

## 4. O problema ABA

Vem da programação lock-free e transfere-se inteiro para o OCC.

```
Estado inicial:  x = A,  token = 7

Ana lê:          x = A,  token = 7
                                         Bruno escreve: x = B, token = 8
                                         Carla escreve: x = A, token = 7  ← token REUTILIZADO
Ana grava com token 7:                   ACEITO (!)
```

Ana acha que nada mudou desde a leitura dela. Mudou duas vezes e voltou. Se a decisão dela
dependia de "ninguém mexeu nisso" — e não apenas de "o valor é A" —, ela acabou de tomar a
decisão errada.

**Quando isso é possível:**

- token que **volta atrás**: timestamp com relógio corrigido, `xmin` após wraparound;
- token derivado só do **valor**, com um conjunto pequeno de valores possíveis (hash de um
  booleano, por exemplo);
- versão **reiniciada** por migração, restore de backup ou recriação da linha com o mesmo id.

**Quando não é possível:** inteiro estritamente crescente que nunca reinicia, `rowversion`,
UUID novo por escrita. É a razão de P2 estar no contrato.

**Correção geral:** garanta monotonicidade estrita, ou combine o token com algo que não volta
(`(version, id_da_transacao)`, ou um contador global). Em CAS de hardware a solução análoga é
o *tagged pointer*, que anexa um contador ao ponteiro exatamente para impedir o ABA.

---

## 5. Granularidade: onde colocar a versão

Decisão tão importante quanto o tipo do token, e muito menos discutida.

| Granularidade | Exemplo | Conflitos falsos | Conflitos não detectados |
|---|---|---|---|
| **Por campo** | uma versão para `telefone`, outra para `endereco` | mínimos | os que envolvem a coerência **entre** campos |
| **Por linha** | uma coluna `version` na tabela | médios | os que envolvem várias linhas |
| **Por agregado** | versão no `pedido`, incrementada por qualquer item | mais | poucos |
| **Por documento** | versão do JSON inteiro | muitos | quase nenhum, dentro do documento |

O critério não é técnico, é de domínio:

> **A unidade de versionamento deve ser a unidade de consistência do negócio.**

Se a regra é "o total do pedido tem de bater com a soma dos itens", a unidade de consistência
é **o pedido** — e é nele que a versão precisa estar, ainda que o item seja outra tabela.
É a definição de *agregado* do Domain-Driven Design, e é a mesma razão pela qual o JPA
oferece `OPTIMISTIC_FORCE_INCREMENT`.

Erro comum na outra direção: versionar por linha uma tabela de "configurações"
(`chave, valor, version`) em que cada linha é independente. Aí a versão por linha é
exatamente certa, e versionar o conjunto inteiro criaria conflitos falsos entre configurações
que nada têm a ver uma com a outra.

---

## 6. Recomendação prática

Se você não quer pensar em cada caso, use esta política. Ela é defensável em 90% dos sistemas:

1. **`BIGINT version`** na tabela, incrementado no `UPDATE`, sempre pelo banco.
2. **Granularidade no agregado** que o negócio reconhece — não necessariamente a linha editada.
3. **ETag público derivado, não igual**: se o token sai numa API, exponha
   `sha256(id + ":" + version)` truncado, ou um UUID separado. Assim você pode trocar a
   representação interna sem quebrar clientes.
4. **Nunca** `updated_at` como guarda única. Mantenha-o para auditoria.
5. **Meça** `conflitos / escritas` por tabela. É essa métrica que vai dizer se a granularidade
   está errada, muito antes de qualquer usuário reclamar.

---

## Autoteste

1. Enuncie as cinco propriedades de um token e diga qual delas o `updated_at` viola.
2. Descreva o problema ABA com um exemplo que não seja o do texto.
3. Por que o `xmin` do PostgreSQL não serve como ETag público?
4. Qual propriedade única o hash de conteúdo tem, e por que ela reduz a taxa de conflito?
5. O que é serialização canônica e por que ela é indispensável no hash?
6. Quando um relógio vetorial é necessário, e o que ele distingue que um contador não distingue?
7. Você tem `pedido` e `item_pedido`. A regra é "o total bate com a soma dos itens". Onde vai
   a versão? Justifique.
8. Por que expor `version` diretamente como ETag público pode ser um problema no futuro?
