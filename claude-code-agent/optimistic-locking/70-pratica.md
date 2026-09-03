# 70 · Prática — 12 laboratórios

`Nível: iniciante → pesquisa` · `Atualizado em: 14/08/2026`
`Testado em: Node v24.18.0, Ubuntu 22.04.5, 14/08/2026`

Doze laboratórios em ordem crescente. Cada um tem **objetivo**, **o que fazer**,
**resultado esperado** e **o que você deve concluir**.

Os labs 1–7 e 11–12 rodam só com Node. Os labs 8–10 precisam de PostgreSQL
(via Docker, ver [`03 §6.1`](03-instalacao.md#61-via-docker-recomendado--nada-fica-no-sistema)).

| Lab | Tema | Precisa de |
|---|---|---|
| [1](#lab-1--ver-o-bug) | Ver o lost update acontecer | Node |
| [2](#lab-2--consertar-e-medir) | Consertar e medir o custo | Node |
| [3](#lab-3--retentar-sem-reler) | Provar por que reler é obrigatório | Node |
| [4](#lab-4--o-jitter-importa) | Medir o efeito do jitter | Node |
| [5](#lab-5--versão-vs-delta) | Comparar as duas técnicas | Node |
| [6](#lab-6--merge-de-três-vias) | Implementar merge campo a campo | Node |
| [7](#lab-7--etagif-match) | O ciclo HTTP completo | Node + curl |
| [8](#lab-8--níveis-de-isolamento) | Ver o comportamento de cada nível | PostgreSQL |
| [9](#lab-9--write-skew) | Produzir a anomalia que o OCC não pega | PostgreSQL |
| [10](#lab-10--serializable-e-40001) | Retentativa em `40001` | PostgreSQL |
| [11](#lab-11--a-curva-de-vazão) | Encontrar o joelho do OCC | Node |
| [12](#lab-12--auditar-um-sistema-real) | Aplicar ao seu código | seu projeto |

---

## Lab 1 — Ver o bug

**Objetivo.** Produzir um lost update e comprovar que ele não gera erro nenhum.

**Faça:**

```bash
cd 07-projeto-modelo && npm run demo:perde
```

Depois, rode com 5, 50 e 100 clientes:

```bash
node test/demo-corrida.js inseguro 5
node test/demo-corrida.js inseguro 50
node test/demo-corrida.js inseguro 100
```

**Esperado.** Com 20 clientes, cerca de metade das edições desaparece (na execução de
referência: 10 de 20). Nenhum erro em lugar nenhum.

**Conclua.**
1. A fração perdida **não** cresce proporcionalmente ao número de clientes — investigue por quê
   (dica: quantos clientes conseguem ler antes da primeira escrita?).
2. A versão final foi 21 nas duas execuções. Escreva, com suas palavras, por que isso torna a
   coluna `version` inútil sem o `WHERE`.

---

## Lab 2 — Consertar e medir

**Objetivo.** Quantificar o custo da correção.

**Faça:**

```bash
node test/demo-corrida.js seguro 5
node test/demo-corrida.js seguro 20
node test/demo-corrida.js seguro 50
```

Monte a tabela:

| Clientes | Perdidas | Escritas/edição | Tempo |
|---|---|---|---|
| 5 | | | |
| 20 | | | |
| 50 | | | |

**Esperado.** Zero perdas em todos. Escritas por edição crescendo com o número de clientes
(referência: 3,35× com 20 clientes).

**Conclua.** O custo não é constante — ele cresce com a contenção. Estime, extrapolando, em
que número de clientes o custo se tornaria inaceitável para uma requisição interativa
(orçamento de 800 ms). Compare com o modelo de [`14 §2`](14-otimista-vs-pessimista.md#2-o-cálculo).

---

## Lab 3 — Retentar sem reler

**Objetivo.** Provar experimentalmente que reler faz parte da retentativa.

**Faça.** Em `src/cliente.js`, mova a leitura para **fora** do bloco retentado:

```javascript
// versão QUEBRADA, só para o laboratório
async function editarQuebrado(id, transformar, opts = {}) {
  const { produto, etag } = await obter(id);        // <<< lê UMA vez, fora do retry
  return comRetentativa(() => salvar(id, etag, transformar(produto), opts.autor), opts);
}
```

Use-a na demonstração e rode com 20 clientes.

**Esperado.** As tentativas se esgotam e a operação falha, por mais que você aumente
`tentativas`. Aumente para 500 e observe que continua falhando.

**Conclua.** O número de tentativas é irrelevante se o estado de entrada não muda.
Escreva a regra em uma frase e guarde-a — é o erro nº 2 de [`04 §6`](04-como-comecar.md#erro-2--retentar-sem-reler).

---

## Lab 4 — O jitter importa

**Objetivo.** Medir o efeito do sorteio no atraso.

**Faça.** Em `src/retry.js`, substitua o atraso com jitter por um atraso fixo:

```javascript
// const teto = Math.min(tetoMs, baseMs * 2 ** i);
// await dormir(Math.floor(aleatorio() * teto));
await dormir(Math.min(tetoMs, baseMs * 2 ** i));    // sem jitter
```

Rode `node test/demo-corrida.js seguro 20` cinco vezes com e cinco vezes sem jitter, e
compare a média de "escritas HTTP gastas" e de tempo.

**Esperado.** Sem jitter, os clientes tendem a se sincronizar em rodadas: o número de
tentativas e a variância entre execuções aumentam.

**Conclua.** Por que sortear o atraso quebra a sincronização? Relacione com o efeito manada
de [`19 §2.1`](19-retentativa-e-idempotencia.md#21-recuo-exponencial-com-jitter).

**Restaure o código antes de seguir.**

---

## Lab 5 — Versão vs. delta

**Objetivo.** Ver por que usar versão em contador é um erro.

**Faça.** Escreva um script que, sobre `07-projeto-modelo`, execute 100 baixas de 1 unidade
de duas formas:

(a) pela rota `POST /produtos/:id/baixa` (delta atômico);
(b) por leitura-modificação-escrita com `If-Match` (versão).

Compare: escritas totais, tempo, e quantas foram recusadas.

```javascript
// esqueleto — complete
const rs = await Promise.all(Array.from({length: 100}, () => cliente.baixarEstoque(id, 1)));
// vs.
const rs2 = await Promise.all(Array.from({length: 100}, () =>
  cliente.editar(id, (p) => ({ estoque: p.estoque - 1 }), { tentativas: 200, baseMs: 1 })));
```

**Esperado.** O delta atômico faz 100 escritas e zero conflitos. A versão faz muito mais
escritas, gasta muito mais tempo, e chega ao mesmo resultado.

**Conclua.** Enuncie o critério de escolha entre as duas técnicas e aplique-o a três campos
do seu próprio sistema.

---

## Lab 6 — Merge de três vias

**Objetivo.** Transformar conflito falso em não-conflito.

**Faça.** Parta de [`06 §7`](06-exemplos.md#7--merge-campo-a-campo-em-vez-de-recusar) e
estenda:

1. Adicione **grupos atômicos**: `['preco_centavos', 'moeda']` devem conflitar juntos.
2. Adicione um campo `contador_acessos` que seja **excluído** da checagem (equivalente ao
   `@OptimisticLock(excluded = true)`).
3. Escreva testes para: campos diferentes (mescla), mesmo campo com valor igual (não é
   conflito), mesmo campo com valor diferente (conflito), campo do grupo atômico (conflito
   arrasta o grupo).

**Esperado.** Quatro testes passando.

**Conclua.** Quantos dos "conflitos" do lab 2 seriam evitados por merge? Meça, marcando quais
tentativas teriam sido mescláveis.

---

## Lab 7 — ETag/If-Match

**Objetivo.** Exercitar o protocolo na mão e ver todos os códigos de status.

**Faça.** Com `npm start` rodando, produza cada uma destas respostas com `curl`:
`200`, `400` (ETag fraco), `404`, `409` (estoque insuficiente), `412`, `428`.

**Esperado.** As seis. A sequência verificada está em
[`06 §8`](06-exemplos.md#8--etagif-match-ponta-a-ponta).

**Depois:** modifique o servidor para devolver ETag **fraco** (`W/"7"`) e observe o cliente
falhar com 412 para sempre. Este é o bug que o Express produz por padrão.

**Conclua.** Escreva, em três linhas, o contrato que um cliente precisa cumprir para usar sua
API com segurança. Esse texto deveria estar na sua documentação de API.

---

## Lab 8 — Níveis de isolamento

**Precisa de PostgreSQL.**

```bash
docker run -d --name pg-lab -e POSTGRES_PASSWORD=segredo -e POSTGRES_DB=lab -p 5432:5432 postgres:18
```

```bash
docker exec -it pg-lab psql -U postgres -d lab -c \
  "CREATE TABLE conta (id INT PRIMARY KEY, saldo INT); INSERT INTO conta VALUES (1, 100);"
```

**Faça.** Abra dois terminais com `docker exec -it pg-lab psql -U postgres -d lab` e execute,
alternando, para cada nível (`READ COMMITTED`, `REPEATABLE READ`, `SERIALIZABLE`):

```sql
-- sessão A                                  -- sessão B
BEGIN ISOLATION LEVEL <nível>;               BEGIN ISOLATION LEVEL <nível>;
SELECT saldo FROM conta WHERE id=1;          SELECT saldo FROM conta WHERE id=1;
UPDATE conta SET saldo=90 WHERE id=1;
COMMIT;
                                             UPDATE conta SET saldo=90 WHERE id=1;
                                             COMMIT;
SELECT saldo FROM conta WHERE id=1;
```

Anote, para cada nível: o valor final e a mensagem de erro (se houver).

**Esperado.** `READ COMMITTED` → 90, sem erro (lost update). `REPEATABLE READ` e
`SERIALIZABLE` → `ERROR: could not serialize access due to concurrent update`.

**Conclua.** Qual é o nível padrão do PostgreSQL? O que isso significa para uma aplicação que
não configura nada?

---

## Lab 9 — Write skew

**Precisa de PostgreSQL.**

```sql
CREATE TABLE medico (nome TEXT PRIMARY KEY, de_plantao BOOLEAN, version INT DEFAULT 1);
INSERT INTO medico VALUES ('ana', true, 1), ('bruno', true, 1);
```

**Faça.** Em `READ COMMITTED`, alternando entre as duas sessões:

```sql
-- sessão A                                       -- sessão B
BEGIN;
SELECT count(*) FROM medico WHERE de_plantao;     BEGIN;
-- 2, posso sair                                  SELECT count(*) FROM medico WHERE de_plantao;
                                                  -- 2, posso sair
UPDATE medico SET de_plantao=false, version=version+1
 WHERE nome='ana' AND version=1;
COMMIT;
                                                  UPDATE medico SET de_plantao=false, version=version+1
                                                   WHERE nome='bruno' AND version=1;
                                                  COMMIT;
SELECT count(*) FROM medico WHERE de_plantao;     -- 0
```

**Esperado.** Zero médicos de plantão. **As duas guardas de versão funcionaram perfeitamente**
— cada `UPDATE` afetou 1 linha.

**Conclua.** Explique por que o OCC por linha não podia ter detectado isso. Relacione com
`RS(T)` de tamanho 1 em [`60 §2.3`](60-teoria-avancada.md#23-o-update--where-version---como-validação).
Proponha duas correções diferentes.

---

## Lab 10 — `SERIALIZABLE` e `40001`

**Precisa de PostgreSQL.**

**Faça.** Repita o lab 9 com `BEGIN ISOLATION LEVEL SERIALIZABLE` nas duas sessões.

**Esperado.** A segunda a confirmar recebe:

```
ERROR:  could not serialize access due to read/write dependencies among transactions
DETAIL:  Reason code: ...
HINT:  The transaction might succeed if retried.
```

**Depois:** escreva, em Node ou Python, um cliente que execute a transação inteira com
retentativa em `40001`, e verifique que ele converge para o resultado correto (um médico
permanece de plantão).

**Conclua.** O que exatamente o SSI detectou que a coluna de versão não detectava?
Qual é o custo dessa proteção (releia [`15 §4`](15-isolamento-e-mvcc.md#custos-reais-do-serializable))?

---

## Lab 11 — A curva de vazão

**Objetivo.** Encontrar experimentalmente o joelho do OCC.

**Faça.** Rode `node test/demo-corrida.js seguro N` para N = 2, 5, 10, 20, 40, 80, 160.
Para cada um, calcule a **vazão útil**: `N / tempo_total_em_segundos`.

Monte o gráfico (pode ser ASCII):

```
vazão útil (edições/s)
 │
 │        ╭──╮
 │      ╭─╯  ╰─╮
 │    ╭─╯      ╰──╮
 │  ╭─╯            ╰────
 └──┴──┴──┴──┴──┴──┴──┴──  N
```

**Esperado.** A vazão cresce, atinge um máximo e depois **cai**. Anote o `N` do máximo.

**Conclua.** Compare com a previsão teórica de
[`60 §4.4`](60-teoria-avancada.md#44-o-limite-de-vazão-do-occ-sob-contenção). Que decisão de
arquitetura o formato dessa curva justifica? (Dica: limitar concorrência na entrada.)

---

## Lab 12 — Auditar um sistema real

**Objetivo.** Aplicar tudo ao seu próprio código. É o laboratório que importa.

**Faça, na ordem:**

1. Rode as quatro buscas de [`12 §5`](12-anatomia-do-lost-update.md#5-onde-procurar-no-seu-código-hoje)
   no seu repositório. Liste os candidatos.
2. Ligue o log de SQL e leia o `UPDATE` gerado por uma edição típica. Tem `AND version = ?`?
3. Liste todas as rotas de escrita. Quantas exigem `If-Match`?
4. Liste os caminhos de escrita que **não** passam pelo ORM (SQL cru, jobs em lote,
   importações, scripts). Esses têm guarda?
5. Escolha o registro mais disputado do sistema e estime a taxa de conflito com a fórmula de
   [`12 §4`](12-anatomia-do-lost-update.md#4-quanto-custa-a-matemática-da-janela).
6. Adicione **uma** métrica: contador de conflitos por rota. Só isso.
7. Escreva um relatório de uma página: onde há risco, qual é o mais grave, e qual é a correção
   mais barata.

**Esperado.** Você vai encontrar pelo menos um caminho desprotegido. Praticamente todo sistema
tem — normalmente num job em lote ou numa rota de "correção manual".

**Conclua.** Comece pelo passo 6. Sem medir, qualquer prioridade que você definir é chute.

---

## Autoavaliação

Marque o que você consegue fazer **sem consultar**:

- [ ] Reproduzir um lost update de forma determinística.
- [ ] Escrever a guarda otimista correta em SQL, de cabeça.
- [ ] Explicar por que retentar exige reler.
- [ ] Explicar por que o jitter é necessário.
- [ ] Escolher entre versão e delta atômico para um campo qualquer.
- [ ] Implementar merge de três vias com grupos atômicos.
- [ ] Produzir `412` e `428` numa API e dizer quando cada um é correto.
- [ ] Dizer o que cada nível de isolamento faz com o cenário do lab 8.
- [ ] Produzir e explicar um write skew.
- [ ] Tratar `40001` corretamente.
- [ ] Explicar por que a vazão do OCC tem um máximo.
- [ ] Auditar um sistema desconhecido e apontar os riscos.

Doze marcados: você domina o assunto no nível de aplicação. Para o nível de pesquisa, vá para
[`60`](60-teoria-avancada.md) e [`95-referencias.md`](95-referencias.md).
