# 75 · Armadilhas, mitos e más práticas

`Nível: todos` · `Última atualização: 11/08/2026`

O catálogo dos erros que todo mundo comete, por que persistem e como sair de cada um. Organizado
por frequência na vida real.

---

## Parte 1 — Os erros que travam o iniciante

### 1. `WHERE x = NULL` nunca retorna nada
`NULL` é "desconhecido", e nada é "igual" a desconhecido. Use `IS NULL` / `IS NOT NULL`. Ver
[10-fundamentos.md](10-fundamentos.md#5-null-o-valor-que-não-é-um-valor).

### 2. Aspas simples vs. duplas
```sql
WHERE nome = "Ana"   -- ❌ "Ana" é um IDENTIFICADOR (coluna/tabela), dá erro
WHERE nome = 'Ana'   -- ✅ 'Ana' é TEXTO
```
Simples para valores; duplas para nomes de objeto. O erro de sintaxe nº 1.

### 3. `UPDATE`/`DELETE` sem `WHERE`
Muda/apaga a tabela **inteira**. Sem desfazer fora de transação. Hábito que salva carreiras: rode o
`WHERE` num `SELECT` primeiro, ou trabalhe dentro de `BEGIN` ... `COMMIT`.

### 4. Float para dinheiro
```sql
SELECT 0.1::float + 0.2::float;   -- 0.30000000000000004
```
Use `NUMERIC` para dinheiro. Ver [13-tipos-de-dados.md](13-tipos-de-dados.md#1-números--e-a-regra-sagrada-do-dinheiro).

### 5. Esquecer o `;`
O `psql` espera até o `;`. Se o prompt vira `banco-#`, ele quer o resto do comando.

### 6. `LEFT JOIN` que vira `INNER` por causa do `WHERE`
Condição sobre a tabela direita no `WHERE` filtra as linhas sem correspondência. Ponha no `ON`.
Ver [12-modelo-relacional-e-sql.md](12-modelo-relacional-e-sql.md#o-erro-clássico-de-left-join--where).

### 7. `NOT IN` com subconsulta que tem `NULL`
Retorna vazio silenciosamente. Use `NOT EXISTS`.

### 8. Confundir `TIMESTAMP` com `TIMESTAMPTZ`
Sem fuso, você perde a referência de tempo e ganha bugs de horário de verão. Use `TIMESTAMPTZ`.

---

## Parte 2 — Os mitos, e a realidade

| Mito | Realidade |
|---|---|
| "`VARCHAR(50)` é mais rápido/menor que `TEXT`" | Mesmo armazenamento; `TEXT` é o padrão. Ver [13](13-tipos-de-dados.md) |
| "SELECT * é conveniente e inofensivo" | Traz colunas demais, impede index-only scan, quebra ao mudar o esquema. Liste as colunas |
| "Índice sempre acelera" | Acelera leitura, **desacelera escrita** e ocupa disco. Indexe o que consulta |
| "Mais índices = mais rápido" | Índices demais tornam a escrita lenta e enchem o disco |
| "`DELETE` libera espaço em disco" | Não: MVCC deixa linhas mortas; só `VACUUM` recupera (para a tabela), `VACUUM FULL` para o SO. Ver [15](15-transacoes-e-mvcc.md) |
| "Seq Scan é sempre ruim" | Ler a tabela toda é ótimo quando você quer a maioria das linhas |
| "Postgres é lento comparado a NoSQL" | Para a maioria das cargas, não. E dá garantias que o NoSQL não dá |
| "Preciso de um banco separado para JSON/vetores/busca" | JSONB, pgvector, tsvector fazem isso no Postgres. Ver [65](65-estado-da-arte.md) |
| "UUID como PK é sempre ruim" | UUIDv4 fragmenta índice; `uuidv7()` (PG 18) resolve. Ver [13](13-tipos-de-dados.md) |
| "Transação deixa tudo lento" | MVCC: leitores não bloqueiam escritores. Transações são baratas |
| "`ORM` me poupa de saber SQL" | Até gerar uma consulta N+1 ou um plano ruim. Você ainda precisa entender SQL |
| "Autovacuum é opcional / posso desligar" | Desligar leva a bloat e wraparound (o banco **para**). Nunca desligue |

---

## Parte 3 — Más práticas que persistem (e por quê)

### App conecta como superusuário
**Por que persiste:** "funciona" e é o usuário que já existe. **Por que é ruim:** um SQL injection
ou bug pode `DROP TABLE`, criar usuários. **Correção:** role de privilégio mínimo. Ver
[20-seguranca.md](20-seguranca.md).

### Concatenar entrada na SQL (injeção)
**Por que persiste:** parece mais simples que parametrizar. **Por que é ruim:** SQL injection, a
vulnerabilidade que vaza bancos. **Correção:** consultas parametrizadas (`$1`), sempre.

### `SELECT *` em produção
**Por que persiste:** conveniência. **Por que é ruim:** transfere dados demais, impede index-only
scan, e o código quebra quando alguém adiciona uma coluna. **Correção:** liste as colunas.

### Não ter índice nas chaves estrangeiras
**Por que persiste:** a PK referenciada é indexada; parece que basta. **Por que é ruim:** a coluna
FK **não** é indexada automaticamente — `JOIN`s e `ON DELETE CASCADE` viram seq scans.
**Correção:** indexe suas colunas FK.

### Banco exposto na internet
**Por que persiste:** facilita o acesso durante o desenvolvimento. **Por que é ruim:** comprometido
em horas por varreduras. **Correção:** rede privada, SSH/VPN. Ver [20](20-seguranca.md).

### Guardar tudo em JSONB
**Por que persiste:** flexibilidade sedutora. **Por que é ruim:** joga fora tipos, constraints e
índices do relacional. **Correção:** JSONB só para o genuinamente variável; o resto é coluna.

### Ignorar o autovacuum
**Por que persiste:** roda sozinho, então "não é problema meu". **Por que é ruim:** em tabelas
quentes ele atrasa, e o bloat/wraparound aparece no pior momento. **Correção:** monitore
`n_dead_tup` e `age(datfrozenxid)`; ajuste o autovacuum por tabela. Ver [21](21-administracao-e-operacao.md).

### Backup nunca testado
**Por que persiste:** o backup "existe", então parece resolvido. **Por que é ruim:** um backup que
não restaura não é backup. **Correção:** teste a restauração periodicamente.

### Migração destrutiva num deploy
**Por que persiste:** parece mais direto renomear/dropar de uma vez. **Por que é ruim:** clientes na
versão antiga quebram; travamento de tabela. **Correção:** *expand/contract*, `CONCURRENTLY`, `NOT
VALID`. Ver [21](21-administracao-e-operacao.md#5-migrações-de-esquema--evoluir-sem-quebrar).

### `work_mem` gigante "para ir rápido"
**Por que persiste:** parece que mais memória = mais rápido. **Por que é ruim:** é por operação, por
conexão — multiplica e derruba o servidor. **Correção:** valor moderado, ciente da concorrência.

---

## Parte 4 — Armadilhas de desempenho

| Sintoma | Causa provável | Correção |
|---|---|---|
| "Ficou lento do nada" | Estatísticas velhas | `ANALYZE tabela` |
| Consulta lenta específica | Falta índice / plano ruim | `EXPLAIN ANALYZE`; criar índice `CONCURRENTLY` |
| Escrita lenta | Índices demais; `fsync` a cada commit | Remover índices inúteis; agrupar em transações |
| Disco enchendo | Bloat; `pg_wal/` crescendo; transação zumbi | `VACUUM`; checar replicação/archive; matar `idle in transaction` |
| "too many clients" | Sem pool; conexões vazando | Pool na app; PgBouncer; corrigir vazamento |
| Consulta trava | Bloqueio; deadlock | `pg_locks`, `pg_stat_activity`; ordem de bloqueio consistente |
| N+1 (mil consultas por página) | ORM buscando um a um | `JOIN` ou `IN`; carregar em lote |
| Paginação lenta em páginas altas | `OFFSET` grande | Keyset. Ver [06](06-exemplos.md#2-paginação-correta) |
| Função na coluna do `WHERE` | Impede o índice | Reescrever, ou índice por expressão |

---

## Parte 5 — Referência rápida de diagnóstico

```sql
-- Por que a consulta está lenta?
EXPLAIN (ANALYZE, BUFFERS) <consulta>;
-- Compare rows estimado vs real. Muito diferente → ANALYZE

-- Consultas mais caras do sistema
SELECT calls, round(mean_exec_time::numeric,2), query
FROM pg_stat_statements ORDER BY total_exec_time DESC LIMIT 10;

-- Tabelas com bloat / autovacuum atrasado
SELECT relname, n_dead_tup, last_autovacuum FROM pg_stat_user_tables ORDER BY n_dead_tup DESC;

-- Transações zumbis
SELECT pid, now()-xact_start AS dur, state, query FROM pg_stat_activity
WHERE state='idle in transaction' ORDER BY dur DESC;

-- Bloqueios
SELECT * FROM pg_locks WHERE NOT granted;

-- Wraparound (perigo)
SELECT datname, age(datfrozenxid) FROM pg_database ORDER BY 2 DESC;

-- Índices nunca usados
SELECT relname, indexrelname, idx_scan FROM pg_stat_user_indexes WHERE idx_scan=0;

-- Disco por tabela
SELECT relname, pg_size_pretty(pg_total_relation_size(oid))
FROM pg_class WHERE relkind='r' ORDER BY pg_total_relation_size(oid) DESC LIMIT 10;
```

---

## Parte 6 — O anti-checklist

Se você faz **qualquer** um destes, pare e corrija:

- [ ] App conectando como superusuário
- [ ] Entrada do usuário concatenada na SQL (não parametrizada)
- [ ] Banco exposto na internet
- [ ] `SELECT *` em código de produção
- [ ] Colunas de chave estrangeira sem índice
- [ ] Float/`real` para dinheiro
- [ ] `TIMESTAMP` sem fuso para instantes
- [ ] Autovacuum desligado ou ignorado
- [ ] Backup nunca testado com restauração
- [ ] `UPDATE`/`DELETE` sem `WHERE` (sem transação de segurança)
- [ ] Migração destrutiva direto em produção
- [ ] Tudo em JSONB, sem colunas de verdade
- [ ] `work_mem` gigante com muitas conexões
- [ ] Senha no código ou no Git

---

## Autoteste

1. Por que `WHERE x = NULL` não funciona, e qual é a forma correta?
2. Aspas simples vs. duplas: qual é para valor e qual para nome de objeto?
3. Por que `DELETE` não libera espaço em disco, e o que libera?
4. Por que `SELECT *` é problemático em produção?
5. Por que a coluna de chave estrangeira precisa de índice, se a PK já tem?
6. Explique como um `LEFT JOIN` vira `INNER JOIN` por acidente.
7. Por que desligar o autovacuum é perigoso? O que pode acontecer no limite?
8. Por que `work_mem` alto pode derrubar o servidor?
9. O que é uma consulta N+1, e como evitá-la?
10. Passe pelo anti-checklist e identifique o que você já fez.
