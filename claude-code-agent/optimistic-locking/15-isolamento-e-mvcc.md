# 15 · Isolamento, MVCC e o que o banco já faz por você

`Nível: avançado` · `Atualizado em: 14/08/2026`
`Referência: PostgreSQL 18.6 · MySQL 8.4/9.x (InnoDB) · Oracle 23ai · SQL Server 2022`

A pergunta que este arquivo responde: **se o banco tem níveis de isolamento, para que serve a
coluna de versão?**

Resposta curta: porque o isolamento protege **dentro de uma transação**, e o problema real
acontece **entre transações diferentes**, separadas por uma requisição HTTP e pelo tempo de
pensar de um ser humano. Nenhum nível de isolamento cobre isso — e nunca poderia.

---

## 1. Os quatro níveis e o que cada um proíbe

O SQL-92 definiu os níveis pelas anomalias que **proíbem**:

| Nível | Leitura suja | Leitura não repetível | Fantasma |
|---|---|---|---|
| `READ UNCOMMITTED` | permitida | permitida | permitida |
| `READ COMMITTED` | proibida | permitida | permitida |
| `REPEATABLE READ` | proibida | proibida | permitida |
| `SERIALIZABLE` | proibida | proibida | proibida |

**Repare no que não está na tabela: *lost update*.** O padrão SQL-92 simplesmente não o
menciona. Foi a crítica central de Berenson, Bernstein, Gray, Melton, O'Neil e O'Neil em
*"A Critique of ANSI SQL Isolation Levels"* (1995): a definição por anomalias é incompleta e
ambígua, e deixa de fora justamente o problema mais comum na prática.

Consequência direta: **o nível padrão do seu banco não protege contra lost update.**

| Banco | Nível padrão | Protege contra lost update no padrão? |
|---|---|---|
| PostgreSQL | `READ COMMITTED` | **não** |
| MySQL/InnoDB | `REPEATABLE READ` | **não** (ver seção 3) |
| Oracle | `READ COMMITTED` | **não** |
| SQL Server | `READ COMMITTED` | **não** |
| SQLite | serializado por escritor único | sim, por acidente de arquitetura |

---

## 2. MVCC em uma página

**MVCC** (*multiversion concurrency control*, controle de concorrência multiversão) é a
técnica pela qual o banco mantém **várias versões de cada linha** simultaneamente, para que
leitores nunca bloqueiem escritores e vice-versa.

No PostgreSQL, cada linha física (*tuple*) carrega dois campos de sistema:

- `xmin` — o ID da transação que criou aquela versão;
- `xmax` — o ID da transação que a apagou ou substituiu (`0` se ainda viva).

Um `UPDATE` **não altera a linha**: ele cria uma versão nova e marca a antiga como morta.

```
UPDATE conta SET saldo = 150 WHERE id = 1;

antes:  [id=1, saldo=100, xmin=100, xmax=0  ]
depois: [id=1, saldo=100, xmin=100, xmax=205]   <- versão antiga, agora morta
        [id=1, saldo=150, xmin=205, xmax=0  ]   <- versão nova
```

Cada transação carrega um **instantâneo** (*snapshot*): a lista de transações que já haviam
confirmado quando ela começou (ou, em `READ COMMITTED`, quando o comando começou). Ao ler uma
linha, o banco escolhe a versão visível segundo esse instantâneo.

Três consequências que valem para o dia a dia:

1. **Leitura nunca bloqueia escrita.** É a razão de o MVCC ter vencido.
2. **Versões mortas ocupam espaço** até o `VACUUM` recolher — é a origem do *bloat* e da
   necessidade de manutenção no PostgreSQL.
3. **Você já tem um número de versão de graça** — o `xmin`. Com as ressalvas de
   [`13`](13-tokens-de-versao.md#35-xmin-do-postgresql).

Aprofundamento no funcionamento interno:
[`../postgresql/15-transacoes-e-mvcc.md`](../postgresql/15-transacoes-e-mvcc.md).

---

## 3. O mesmo nome, comportamentos diferentes

Este é o ponto em que muita gente se queima ao migrar de banco. Cenário:

```
T1: BEGIN; SELECT saldo FROM conta WHERE id=1;   -- 100
T2: BEGIN; SELECT saldo FROM conta WHERE id=1;   -- 100
T1: UPDATE conta SET saldo=90 WHERE id=1; COMMIT;
T2: UPDATE conta SET saldo=90 WHERE id=1; COMMIT;
```

| Banco / nível | O que acontece com T2 |
|---|---|
| PostgreSQL `READ COMMITTED` | o `UPDATE` espera T1, depois **reexecuta o `WHERE`** sobre a versão nova e grava. Lost update **acontece** |
| PostgreSQL `REPEATABLE READ` | **aborta** com `ERROR: could not serialize access due to concurrent update` (`40001`) |
| PostgreSQL `SERIALIZABLE` | aborta com `40001` (por SSI) |
| MySQL/InnoDB `REPEATABLE READ` | **não aborta**: o `UPDATE` lê a versão mais recente (*current read*) e grava. Lost update **acontece** |
| Oracle `SERIALIZABLE` | aborta com `ORA-08177` |
| SQL Server `SNAPSHOT` | aborta com erro 3960 (*update conflict*) |

**O `REPEATABLE READ` do MySQL e o do PostgreSQL não são a mesma coisa.** Um aborta, o outro
não. Código que dependia do aborto do PostgreSQL passa a perder atualizações em silêncio
depois de migrar para o MySQL, sem nenhum erro que denuncie a mudança.

> Esta é uma das razões, e uma opinião minha bem firme, para **não delegar a correção do lost
> update ao nível de isolamento**: você passa a depender de um comportamento que varia entre
> bancos, entre versões e entre configurações. A guarda explícita `AND version = ?` funciona
> igual em todos.

---

## 4. `SERIALIZABLE` e o SSI do PostgreSQL

O `SERIALIZABLE` do PostgreSQL, desde a versão 9.1 (2011), usa **SSI** — *Serializable
Snapshot Isolation*, do trabalho de Cahill, Röhm e Fekete. É, ele próprio, um mecanismo
**otimista**: nada é bloqueado; o banco rastreia dependências de leitura-escrita e aborta uma
transação quando detecta uma estrutura que não teria equivalente sequencial.

```sql
BEGIN ISOLATION LEVEL SERIALIZABLE;
  -- ... suas leituras e escritas ...
COMMIT;
-- pode falhar com:
-- ERROR: could not serialize access due to read/write dependencies among transactions
-- HINT: The transaction might succeed if retried.
```

A documentação oficial é explícita:

> *"When an application receives this error message, it should abort the current transaction
> and retry the whole transaction from the beginning."*
> — [PostgreSQL, Transaction Isolation](https://www.postgresql.org/docs/current/transaction-iso.html)

**O que o SSI resolve e a coluna de versão não resolve:** *write skew* e anomalias que
envolvem **várias linhas ou faixas**. O exemplo dos médicos de plantão
([`10`](10-fundamentos.md#21-write-skew-o-buraco-que-ninguém-vê)) é detectado pelo SSI e
invisível para a versão de linha.

**O que a coluna de versão resolve e o SSI não resolve:** a janela **entre** transações. O
`SERIALIZABLE` não tem opinião sobre o que aconteceu entre o `GET` e o `PUT` do usuário —
são duas transações diferentes, separadas por minutos, e serializá-las nessa ordem é
perfeitamente serializável e perfeitamente errado do ponto de vista do negócio.

### Custos reais do `SERIALIZABLE`

Antes de adotá-lo como bala de prata:

| Custo | Detalhe |
|---|---|
| Retentativa **obrigatória** | todo caminho de escrita precisa saber tratar `40001`. Não é opcional |
| Falsos positivos | o SSI aborta transações que teriam sido seguras; a taxa depende dos padrões de acesso |
| Memória de predicate locks | o rastreamento consome memória; sob pressão ele **degrada a granularidade** (de linha para página para tabela), aumentando os falsos positivos |
| Não funciona em réplica hot standby | `SERIALIZABLE` em réplica exige `SERIALIZABLE READ ONLY DEFERRABLE`, com ressalvas |
| Interação com trabalho externo | uma transação que chamou uma API e depois é abortada precisa desfazer o efeito externo |

**Minha recomendação, e é opinião:** use `SERIALIZABLE` deliberadamente, em transações
específicas onde a invariante é sobre um conjunto (escala de plantão, dupla reserva, limite
agregado). Não o ligue globalmente "por segurança" sem antes ter a retentativa implementada
em **todo** caminho de escrita — o resultado costuma ser uma enxurrada de erros 500 no primeiro
pico de tráfego.

---

## 5. `SELECT ... FOR UPDATE` e seus modos

O lado pessimista, para completar o mapa:

```sql
BEGIN;
SELECT saldo FROM conta WHERE id = 1 FOR UPDATE;   -- adquire lock exclusivo de linha
-- ninguém mais consegue alterar a linha 1 até o COMMIT
UPDATE conta SET saldo = 90 WHERE id = 1;
COMMIT;
```

| Cláusula | Efeito |
|---|---|
| `FOR UPDATE` | lock exclusivo; outros leitores com `FOR UPDATE` esperam |
| `FOR NO KEY UPDATE` | mais fraco; permite chaves estrangeiras que apontam para a linha |
| `FOR SHARE` | vários leitores simultâneos, nenhum escritor |
| `FOR KEY SHARE` | o mais fraco; usado internamente por FKs |
| `NOWAIT` | falha imediatamente (`55P03`) em vez de esperar — ótimo para dizer ao usuário "está ocupado" |
| `SKIP LOCKED` | ignora as linhas travadas — a base para implementar **fila de trabalho** em SQL |

Duas aplicações que valem por si:

```sql
-- Fila de trabalho sem broker: cada worker pega itens diferentes, sem esperar.
BEGIN;
SELECT * FROM tarefa WHERE estado = 'pendente'
 ORDER BY criada_em
 LIMIT 10 FOR UPDATE SKIP LOCKED;
-- ... processa ...
UPDATE tarefa SET estado = 'feita' WHERE id = ANY(...);
COMMIT;
```

```sql
-- "Está sendo editado por outra pessoa" — sem enfileirar o usuário
SELECT * FROM documento WHERE id = 1 FOR UPDATE NOWAIT;
-- 55P03 -> mostre "Ana está editando este documento"
```

**Regra inegociável:** `FOR UPDATE` só dentro de uma transação **curta e inteiramente no
servidor**. Segurá-lo durante uma interação com o usuário é o antipadrão que fez o
optimistic locking ser inventado.

---

## 6. Locks consultivos: exclusão mútua sem tabela

Quando você precisa de exclusão mútua sobre algo que não é uma linha (um job, um recurso
externo, uma seção crítica):

```sql
-- lock de sessão: liberado no fim da sessão ou por unlock explícito
SELECT pg_advisory_lock(hashtext('importacao-diaria'));
-- ... só uma instância chega aqui ...
SELECT pg_advisory_unlock(hashtext('importacao-diaria'));
```

```sql
-- lock de transação: liberado automaticamente no COMMIT/ROLLBACK. Prefira este.
SELECT pg_advisory_xact_lock(hashtext('importacao-diaria'));
```

```sql
-- versão não bloqueante: retorna false se já estiver tomado
SELECT pg_try_advisory_xact_lock(hashtext('importacao-diaria'));
```

Cuidados: o lock é **por identificador numérico**, sem espaço de nomes — duas partes do
sistema podem colidir sem perceber. Mantenha uma tabela de constantes documentando cada
identificador usado. E `pg_advisory_lock` (de sessão) vaza se a conexão for reaproveitada por
um *pool* sem limpeza — mais uma razão para preferir a variante `xact`.

---

## 7. A tabela que resume tudo

| Problema | Isolamento resolve? | Versão resolve? | O que usar |
|---|---|---|---|
| Leitura suja | sim (≥ `READ COMMITTED`) | não | o padrão do banco já basta |
| Leitura não repetível | sim (≥ `REPEATABLE READ`) | não | isolamento |
| Fantasma | sim (`SERIALIZABLE`) | não | isolamento |
| Lost update **na mesma transação** | depende do banco (§3) | sim | versão, por portabilidade |
| Lost update **entre requisições HTTP** | **não, jamais** | **sim** | versão + `If-Match` |
| Write skew | sim (`SERIALIZABLE`) | **não** | `SERIALIZABLE` ou materializar a invariante |
| Exclusão mútua de processo | não | não | lock consultivo / lease |
| Contador sob alta contenção | não | mal | `UPDATE x = x ± n` |

A linha em negrito é a razão de este curso existir. Nenhum avanço em isolamento vai cobri-la,
porque as duas requisições **não são a mesma transação** e não há como serem.

---

## 8. Combinando as duas coisas

Elas não são alternativas; são camadas. Um sistema bem-feito usa as duas:

```
┌─────────────────────────────────────────────────────────┐
│ CLIENTE                                                 │
│   guarda o ETag recebido no GET                         │
└───────────────┬─────────────────────────────────────────┘
                │ PUT + If-Match: "7"
┌───────────────▼─────────────────────────────────────────┐
│ APLICAÇÃO                                               │
│   OCC entre requisições  → coluna version / ETag        │
│   retentativa com jitter → converte conflito em latência│
└───────────────┬─────────────────────────────────────────┘
                │ BEGIN ... COMMIT
┌───────────────▼─────────────────────────────────────────┐
│ BANCO                                                   │
│   isolamento dentro da transação → READ COMMITTED       │
│   SERIALIZABLE onde a invariante é sobre um conjunto    │
│   restrições declarativas → UNIQUE, CHECK, EXCLUDE      │
└─────────────────────────────────────────────────────────┘
```

A camada de baixo é a última linha de defesa e a única que nunca falha por esquecimento:
**se a regra couber numa restrição declarativa, ela deve estar lá**, mesmo que já esteja
protegida acima. `UNIQUE (evento, fileira, numero)` custa um índice e impede a dupla venda
mesmo quando todo o resto falhar.

---

## Autoteste

1. Por que o padrão SQL-92 não menciona lost update? Qual publicação apontou isso?
2. Explique `xmin`/`xmax` e o que um `UPDATE` realmente faz no PostgreSQL.
3. Reproduza o cenário da seção 3 e diga o que acontece em PostgreSQL `REPEATABLE READ` e em
   MySQL `REPEATABLE READ`. Por que a diferença é perigosa numa migração?
4. Em que sentido o SSI é um mecanismo otimista?
5. Cite um problema que o `SERIALIZABLE` resolve e a coluna de versão não, e um problema onde
   é o contrário.
6. Para que serve `SKIP LOCKED`, e que padrão de arquitetura ele viabiliza?
7. Por que preferir `pg_advisory_xact_lock` a `pg_advisory_lock`?
8. Sua equipe propõe ligar `SERIALIZABLE` globalmente. Quais três perguntas você faz antes?

---

## Fontes consultadas (14/08/2026)

- [PostgreSQL — Transaction Isolation (doc corrente)](https://www.postgresql.org/docs/current/transaction-iso.html) — níveis, mensagens de erro literais e a orientação de retentativa
- [PostgreSQL 18.6 e demais versões, 13/08/2026](https://www.postgresql.org/about/news/postgresql-186-1711-1615-1519-1424-and-19-beta-3-released-3365/)
- Berenson, Bernstein, Gray, Melton, O'Neil, O'Neil — *A Critique of ANSI SQL Isolation Levels*, SIGMOD 1995
- Cahill, Röhm, Fekete — *Serializable Isolation for Snapshot Databases*, SIGMOD 2008
- [Larson et al. — *High-Performance Concurrency Control Mechanisms for Main-Memory Databases*](https://arxiv.org/pdf/1201.0228)
