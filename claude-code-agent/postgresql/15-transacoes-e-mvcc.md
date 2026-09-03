# 15 · Transações, MVCC e isolamento

`Nível: avançado` · `Última atualização: 11/08/2026`

Como o PostgreSQL deixa milhares de pessoas mexerem nos mesmos dados ao mesmo tempo sem que uma
atrapalhe a outra — e sem trancar tudo. Este é um dos assuntos mais elegantes e mais mal
compreendidos do banco.

---

## 1. O problema da concorrência

Duas pessoas tentam comprar o **último** ingresso ao mesmo tempo:

```
   Transação A                    Transação B
   lê: restam 1 ingresso
                                  lê: restam 1 ingresso
   vende, escreve: restam 0
                                  vende, escreve: restam 0
   ── vendeu 2 ingressos que não existiam ──
```

Sem controle de concorrência, os dados se corrompem. As soluções clássicas eram **travar** (uma
transação bloqueia a outra) — o que é correto mas lento, porque cria filas. O PostgreSQL usa uma
abordagem mais sofisticada: **MVCC**.

---

## 2. MVCC — múltiplas versões, o coração do PostgreSQL

**MVCC** = *Multi-Version Concurrency Control*. A ideia:

> Em vez de sobrescrever uma linha ao atualizá-la, o PostgreSQL **cria uma nova versão** dela. As
> versões antigas continuam existindo enquanto alguma transação ainda pode precisar vê-las. Cada
> transação enxerga uma **foto consistente** (*snapshot*) do banco no instante em que começou (ou
> em que cada comando começou).

A consequência é o lema que você deve memorizar:

> **"Leitores não bloqueiam escritores; escritores não bloqueiam leitores."**

Uma consulta longa (um relatório de 10 minutos) **não trava** quem está inserindo, porque a
consulta vê a foto de quando começou, e as escritas criam versões novas que ela simplesmente
ignora. E quem lê não espera quem escreve. Isso é o que faz o PostgreSQL escalar em concorrência
alta.

### Como funciona por dentro

Cada linha física (tupla) carrega dois carimbos ocultos: **`xmin`** (o id da transação que a
criou) e **`xmax`** (o id da que a apagou/substituiu, se houver). Cada transação tem um id
(`xid`) e um snapshot que diz "quais transações eu enxergo como concluídas".

```sql
SELECT xmin, xmax, * FROM pedidos WHERE id = 1;   -- veja os carimbos ocultos
SELECT txid_current();                             -- o id da transação atual
```

Uma linha é **visível** para uma transação se `xmin` já estava concluído no snapshot dela e `xmax`
não estava (ou não existe). Assim:
- `UPDATE` não sobrescreve: marca a versão antiga com `xmax` e insere uma nova.
- `DELETE` não apaga fisicamente: só marca `xmax`.
- `SELECT` filtra automaticamente as versões que seu snapshot não deve ver.

### O preço do MVCC: linhas mortas e o VACUUM

As versões antigas (*dead tuples*) não somem sozinhas — elas ficam ocupando espaço até que
**nenhuma** transação possa mais precisar delas. Limpá-las é o trabalho do **VACUUM**:

```sql
VACUUM pedidos;              -- marca o espaço das linhas mortas como reutilizável
VACUUM ANALYZE pedidos;      -- + atualiza estatísticas para o planejador
VACUUM FULL pedidos;         -- reescreve a tabela compactando (⚠️ trava a tabela!)
```

O **autovacuum** faz isso automaticamente em segundo plano, e é uma das coisas mais importantes de
manter saudável em produção. Se ele não acompanha o ritmo das escritas, a tabela **incha**
(*bloat*): fica cheia de espaço morto, e as consultas ficam lentas. Ver
[21-administracao-e-operacao.md](21-administracao-e-operacao.md).

> **A consequência que surpreende:** `DELETE FROM tabela` **não** libera espaço em disco de volta
> ao sistema — só marca as linhas como mortas, e o VACUUM as torna reutilizáveis (pela própria
> tabela, não pelo SO). Para devolver espaço ao SO, é preciso `VACUUM FULL` (que trava) ou recriar
> a tabela. Este é um dos fatos operacionais mais importantes sobre o PostgreSQL.

---

## 3. Transações na prática

```sql
BEGIN;
    UPDATE contas SET saldo = saldo - 100 WHERE id = 1;
    UPDATE contas SET saldo = saldo + 100 WHERE id = 2;
COMMIT;   -- as duas valem, atômica e duravelmente
```

```sql
BEGIN;
    DELETE FROM pedidos WHERE cliente_id = 5;
    -- errei o cliente!
ROLLBACK;   -- nada aconteceu
```

**Savepoints** — rollback parcial dentro de uma transação:
```sql
BEGIN;
    INSERT INTO log VALUES ('início');
    SAVEPOINT s1;
    UPDATE arriscado SET x = 1;         -- pode falhar
    ROLLBACK TO s1;                      -- desfaz só o UPDATE, mantém o INSERT
    INSERT INTO log VALUES ('continuei');
COMMIT;
```

> **Transações implícitas:** todo comando solto (`INSERT`, `UPDATE`) roda em sua própria transação
> automática. Ele é atômico e durável por padrão. Você usa `BEGIN`/`COMMIT` explícito quando várias
> operações dependem umas das outras.

---

## 4. Os níveis de isolamento

O "I" de ACID tem graus. Quanto mais rigoroso, mais garantias — e mais chance de conflito entre
transações. Os fenômenos que podem (ou não) ocorrer:

| Fenômeno | O que é |
|---|---|
| **Dirty read** | Ler dados de uma transação **não confirmada** |
| **Non-repeatable read** | Ler a mesma linha duas vezes e obter valores diferentes (alguém a alterou e confirmou no meio) |
| **Phantom read** | Rodar a mesma consulta duas vezes e a segunda trazer **linhas novas** |
| **Serialization anomaly** | O resultado de transações concorrentes difere de qualquer ordem serial delas |

Os níveis, e o que cada um previne no PostgreSQL:

| Nível | Dirty read | Non-repeatable | Phantom | Anomalia serial |
|---|---|---|---|---|
| `READ UNCOMMITTED` | (no PG, = READ COMMITTED) | possível | possível | possível |
| **`READ COMMITTED`** (padrão) | **impedido** | possível | possível | possível |
| `REPEATABLE READ` | impedido | **impedido** | **impedido** (no PG) | possível |
| `SERIALIZABLE` | impedido | impedido | impedido | **impedido** |

> **Peculiaridade do PostgreSQL:** ele nunca permite *dirty reads* (não existe `READ UNCOMMITTED`
> de verdade), e seu `REPEATABLE READ` já previne *phantom reads* (mais forte que o padrão SQL
> exige). O `SERIALIZABLE` do PostgreSQL usa **SSI** (*Serializable Snapshot Isolation*), uma
> técnica que dá o rigor total sem os bloqueios pesados das implementações clássicas.

```sql
BEGIN ISOLATION LEVEL SERIALIZABLE;
    -- ... operações ...
COMMIT;   -- pode falhar com "could not serialize access" → sua app deve RETENTAR
```

**A regra prática:** `READ COMMITTED` (padrão) serve para a maioria. Use `SERIALIZABLE` quando a
correção sob concorrência é crítica (financeiro, estoque) e você prepara a aplicação para
**retentar** transações que falham com erro de serialização — porque sob `SERIALIZABLE`, o banco
aborta transações que criariam anomalias, e a app deve tentar de novo.

---

## 5. O último ingresso, resolvido de três formas

**Forma 1 — bloqueio pessimista (`FOR UPDATE`):**
```sql
BEGIN;
    SELECT quantidade FROM ingressos WHERE evento_id = 1 FOR UPDATE;  -- trava a linha
    -- ninguém mais lê-para-atualizar essa linha até o COMMIT
    UPDATE ingressos SET quantidade = quantidade - 1 WHERE evento_id = 1;
COMMIT;
```
A segunda transação **espera** a primeira terminar. Simples e correto; pode criar filas sob
contenção alta.

**Forma 2 — atualização atômica com condição (otimista):**
```sql
UPDATE ingressos SET quantidade = quantidade - 1
WHERE evento_id = 1 AND quantidade > 0
RETURNING quantidade;
-- se retornou 0 linhas, não havia ingresso. Uma instrução, atômica, sem BEGIN explícito.
```
Frequentemente a mais elegante: o próprio `UPDATE` é atômico, e a condição `quantidade > 0` impede
a venda a descoberto.

**Forma 3 — `SERIALIZABLE`:**
```sql
BEGIN ISOLATION LEVEL SERIALIZABLE;
    SELECT quantidade FROM ingressos WHERE evento_id = 1;
    -- lógica na aplicação...
    UPDATE ingressos SET quantidade = quantidade - 1 WHERE evento_id = 1;
COMMIT;   -- se houve conflito, falha; a app retenta
```

---

## 6. Bloqueios (locks) e deadlocks

O PostgreSQL usa vários tipos de bloqueio internamente. Os que você controla:

```sql
SELECT ... FOR UPDATE;         -- trava linhas para escrita
SELECT ... FOR NO KEY UPDATE;  -- trava mais fraca (permite FKs)
SELECT ... FOR SHARE;          -- trava compartilhada (outros leem, ninguém escreve)
SELECT ... FOR UPDATE SKIP LOCKED;  -- pula linhas já travadas (filas)
SELECT ... FOR UPDATE NOWAIT;       -- falha na hora em vez de esperar
LOCK TABLE t IN EXCLUSIVE MODE;     -- trava a tabela inteira (raro)
```

**Deadlock** (abraço mortal): A trava a linha 1 e quer a 2; B trava a 2 e quer a 1. Ambas esperam
para sempre. O PostgreSQL **detecta** deadlocks automaticamente e aborta uma das transações:
```
ERROR: deadlock detected
```
**Como evitar:** faça as transações adquirirem bloqueios **sempre na mesma ordem** (ex.: sempre
trave a conta de menor id primeiro). A maioria dos deadlocks vem de ordens de acesso inconsistentes.

```sql
-- Ver bloqueios ativos e quem espera quem
SELECT * FROM pg_locks WHERE NOT granted;
SELECT pid, state, wait_event_type, query FROM pg_stat_activity WHERE wait_event_type = 'Lock';
```

---

## 7. Wraparound do XID — o perigo que o VACUUM previne

Os ids de transação (`xid`) são de 32 bits — dão a volta (*wraparound*) depois de ~4 bilhões. Se
isso acontecesse sem controle, transações antigas pareceriam do futuro e dados sumiriam. O VACUUM
"congela" (*freeze*) linhas muito antigas para evitar isso.

Se o autovacuum não acompanha, o PostgreSQL emite avisos cada vez mais graves e, no limite, **para
de aceitar escritas** para se proteger:
```
WARNING: database "x" must be vacuumed within N transactions
```
É um dos poucos jeitos de o PostgreSQL travar sozinho, e é **sempre** consequência de autovacuum
desconfigurado ou de transações abertas por tempo demais. Monitorar `age(datfrozenxid)` é
obrigatório em produção de alto volume. Ver [21](21-administracao-e-operacao.md).

> **A transação zumbi:** uma transação deixada **aberta** (um `BEGIN` sem `COMMIT`, uma conexão de
> app que travou) impede o VACUUM de limpar qualquer linha morta criada desde que ela começou —
> porque o banco não sabe se ela ainda vai precisar vê-las. Uma única transação esquecida por
> horas pode inchar o banco inteiro. Monitore `pg_stat_activity` por transações `idle in
> transaction` antigas.

---

## Autoteste

1. Explique MVCC em uma frase, e o lema que dele decorre.
2. O que são `xmin` e `xmax`, e como determinam a visibilidade de uma linha?
3. Por que um `UPDATE` cria uma nova versão em vez de sobrescrever?
4. Por que `DELETE FROM tabela` não libera espaço em disco, e o que libera?
5. O que o VACUUM faz, e o que acontece se o autovacuum não acompanha as escritas?
6. Liste os quatro níveis de isolamento e o que cada um previne no PostgreSQL.
7. O que há de peculiar no `READ COMMITTED` e no `REPEATABLE READ` do PostgreSQL?
8. Resolva o problema do "último ingresso" de duas formas diferentes.
9. O que é um deadlock, como o PostgreSQL reage, e como você o evita?
10. Como uma única transação esquecida aberta pode inchar o banco inteiro?
