# 05 · Manual de uso — referência consultável

`Nível: intermediário` · `Organizado por tarefa` · `Última atualização: 11/08/2026`

Referência de bolso. Não se lê de ponta a ponta — se consulta. Cada seção responde a "como eu
faço X".

---

## Índice

1. [psql — o terminal](#1-psql--o-terminal)
2. [Criar e alterar estruturas (DDL)](#2-criar-e-alterar-estruturas-ddl)
3. [Manipular dados (DML)](#3-manipular-dados-dml)
4. [Consultar (SELECT)](#4-consultar-select)
5. [JOINs](#5-joins)
6. [Agregação e janelas](#6-agregação-e-funções-de-janela)
7. [Tipos de dados essenciais](#7-tipos-de-dados-essenciais)
8. [JSON e JSONB](#8-json-e-jsonb)
9. [Índices](#9-índices)
10. [Transações e bloqueios](#10-transações-e-bloqueios)
11. [Funções, gatilhos, views](#11-funções-gatilhos-e-views)
12. [Usuários e permissões](#12-usuários-e-permissões)
13. [Backup e restauração](#13-backup-e-restauração)
14. [Inspeção e catálogo](#14-inspeção-e-catálogo)
15. [Obsoleto — o que não usar mais](#15-obsoleto--o-que-não-usar-mais)
16. [Atalhos que só quem usa há anos conhece](#16-atalhos-que-só-quem-usa-há-anos-conhece)

---

## 1. psql — o terminal

| Comando | Faz |
|---|---|
| `\l` | Lista bancos |
| `\c banco [usuario]` | Conecta a outro banco |
| `\dt` / `\dt+` | Lista tabelas / com tamanho |
| `\d tabela` | Descreve tabela (colunas, tipos, índices, constraints) |
| `\d+ tabela` | Idem, com mais detalhe (armazenamento, comentários) |
| `\di` / `\dv` / `\df` / `\dn` | Índices / views / funções / esquemas |
| `\du` | Roles (usuários) |
| `\dp` / `\z` | Privilégios das tabelas |
| `\x [on\|off\|auto]` | Exibição expandida (uma coluna por linha) |
| `\timing on` | Mede o tempo de cada consulta |
| `\e` | Edita a última query no `$EDITOR` |
| `\i arquivo.sql` | Executa um arquivo |
| `\o arquivo` | Redireciona a saída para um arquivo |
| `\copy` | Importa/exporta CSV pelo CLIENTE (não precisa de superusuário) |
| `\watch 2` | Reexecuta a última query a cada 2s |
| `\set` / `\echo` | Variáveis do psql |
| `\conninfo` | Mostra a conexão atual |
| `\errverbose` | Detalha o último erro |
| `\h COMANDO_SQL` | Sintaxe de um comando SQL |
| `\? ` | Ajuda dos comandos `\` |
| `\q` | Sai |

Invocação da linha de comando:
```bash
psql -h HOST -p 5432 -U USUARIO -d BANCO          # conectar
psql "postgresql://usuario:senha@host:5432/banco"  # por URL de conexão
psql -c "SELECT now();"                            # rodar um comando e sair
psql -f script.sql                                 # rodar um arquivo
psql -At -c "SELECT id FROM x" | ...               # -A sem alinhamento, -t só tuplas (para pipes)
psql -v ON_ERROR_STOP=1 -f migracao.sql            # abortar no primeiro erro (essencial em scripts)
```

---

## 2. Criar e alterar estruturas (DDL)

```sql
CREATE DATABASE loja;
CREATE SCHEMA vendas;                       -- namespace dentro do banco

CREATE TABLE clientes (
    id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,  -- forma moderna, melhor que SERIAL
    nome        TEXT NOT NULL,
    email       TEXT UNIQUE NOT NULL,
    ativo       BOOLEAN NOT NULL DEFAULT true,
    metadados   JSONB DEFAULT '{}',
    criado_em   TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Alterar
ALTER TABLE clientes ADD COLUMN telefone TEXT;
ALTER TABLE clientes ALTER COLUMN telefone SET NOT NULL;
ALTER TABLE clientes RENAME COLUMN nome TO nome_completo;
ALTER TABLE clientes DROP COLUMN telefone;

-- Restrições
ALTER TABLE pedidos ADD CONSTRAINT valor_positivo CHECK (valor >= 0);
ALTER TABLE pedidos ADD CONSTRAINT fk_cliente
    FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE;

DROP TABLE pedidos;
DROP TABLE IF EXISTS pedidos CASCADE;       -- CASCADE remove o que depende dela
TRUNCATE pedidos;                           -- esvazia rápido (não dá para ROLLBACK em alguns casos)
TRUNCATE pedidos RESTART IDENTITY CASCADE;  -- + zera contadores + tabelas dependentes
```

### Restrições (constraints) — a defesa da integridade

| Restrição | Garante |
|---|---|
| `PRIMARY KEY` | Identidade única e não-nula |
| `UNIQUE` | Sem valores repetidos |
| `NOT NULL` | Sempre preenchido |
| `CHECK (cond)` | Uma condição arbitrária (ex.: `valor >= 0`) |
| `FOREIGN KEY ... REFERENCES` | Aponta para linha existente em outra tabela |
| `DEFAULT valor` | Valor automático quando não informado |
| `GENERATED ... AS (expr)` | Coluna calculada (no PG 18, virtual por padrão) |

Ações de chave estrangeira: `ON DELETE CASCADE` (apaga os filhos), `ON DELETE RESTRICT` (impede
apagar o pai), `ON DELETE SET NULL`.

---

## 3. Manipular dados (DML)

```sql
INSERT INTO clientes (nome, email) VALUES ('Ana', 'ana@x.com');
INSERT INTO clientes (nome, email) VALUES ('Ana','a@x'), ('Bruno','b@x');  -- várias de uma vez
INSERT INTO clientes (nome, email) VALUES ('Ana','a@x') RETURNING id;      -- devolve o id gerado

-- UPSERT: insere, ou atualiza se já existir (pela chave única)
INSERT INTO clientes (email, nome) VALUES ('ana@x.com', 'Ana Nova')
ON CONFLICT (email) DO UPDATE SET nome = EXCLUDED.nome;

INSERT INTO clientes (email, nome) VALUES ('ana@x.com', 'Ana')
ON CONFLICT (email) DO NOTHING;             -- ignora se já existe

UPDATE pedidos SET valor = valor * 1.1 WHERE criado_em < '2026-01-01';
UPDATE pedidos SET status = 'pago' WHERE id = 5 RETURNING *;

DELETE FROM pedidos WHERE status = 'cancelado';

-- PG 18: RETURNING pode acessar valores ANTIGOS e NOVOS
UPDATE contas SET saldo = saldo - 100 WHERE id = 1
RETURNING OLD.saldo AS antes, NEW.saldo AS depois;
```

### Importar/exportar CSV

```sql
\copy clientes FROM 'clientes.csv' WITH (FORMAT csv, HEADER true);   -- pelo cliente
\copy (SELECT * FROM pedidos WHERE valor > 100) TO 'caros.csv' WITH (FORMAT csv, HEADER true);

-- COPY (comando SQL) roda no SERVIDOR e exige superusuário/permissão; \copy roda no cliente
COPY clientes FROM '/caminho/no/servidor/clientes.csv' WITH (FORMAT csv, HEADER true);
```

---

## 4. Consultar (SELECT)

```sql
SELECT coluna1, coluna2
FROM tabela
WHERE condicao
GROUP BY coluna1
HAVING condicao_de_grupo
ORDER BY coluna1 [ASC|DESC] [NULLS LAST]
LIMIT n OFFSET m;
```

Filtros úteis:
```sql
WHERE idade BETWEEN 18 AND 65
WHERE status IN ('pago', 'enviado')
WHERE nome LIKE 'A%'          -- A no começo (sensível a maiúsculas)
WHERE nome ILIKE '%silva%'    -- contém "silva", INsensível a maiúsculas
WHERE nome ~ '^A.*a$'         -- expressão regular
WHERE email IS NOT NULL
WHERE criado_em >= now() - INTERVAL '7 days'
WHERE (status, tipo) = ('pago', 'online')   -- comparação de tupla
```

Subconsultas e CTEs:
```sql
-- Subconsulta
SELECT * FROM clientes
WHERE id IN (SELECT cliente_id FROM pedidos WHERE valor > 100);

-- CTE (Common Table Expression): nomeia uma consulta intermediária. Mais legível
WITH clientes_vip AS (
    SELECT cliente_id, SUM(valor) AS total
    FROM pedidos GROUP BY cliente_id HAVING SUM(valor) > 500
)
SELECT c.nome, v.total
FROM clientes_vip v JOIN clientes c ON c.id = v.cliente_id;

-- CTE recursiva: hierarquias (organograma, categorias aninhadas)
WITH RECURSIVE subordinados AS (
    SELECT id, nome, chefe_id FROM funcionarios WHERE id = 1
    UNION ALL
    SELECT f.id, f.nome, f.chefe_id
    FROM funcionarios f JOIN subordinados s ON f.chefe_id = s.id
)
SELECT * FROM subordinados;
```

Operações de conjunto:
```sql
SELECT email FROM clientes UNION SELECT email FROM prospects;   -- une (sem duplicatas)
SELECT email FROM clientes UNION ALL SELECT ...;                -- une (com duplicatas, mais rápido)
SELECT email FROM clientes INTERSECT SELECT email FROM ativos;  -- interseção
SELECT email FROM clientes EXCEPT SELECT email FROM banidos;    -- diferença
```

---

## 5. JOINs

```sql
SELECT c.nome, p.descricao
FROM clientes c
[INNER] JOIN pedidos p ON p.cliente_id = c.id;   -- só com correspondência
LEFT  JOIN pedidos p ON p.cliente_id = c.id;     -- todos os clientes
RIGHT JOIN ...                                   -- todos os pedidos
FULL  JOIN ...                                   -- todos dos dois lados
CROSS JOIN ...                                   -- todas as combinações

-- USING quando as colunas têm o mesmo nome
SELECT * FROM pedidos JOIN clientes USING (cliente_id);

-- LATERAL: a subconsulta da direita vê as colunas da esquerda (ótimo para "top N por grupo")
SELECT c.nome, ult.descricao
FROM clientes c
CROSS JOIN LATERAL (
    SELECT descricao FROM pedidos p
    WHERE p.cliente_id = c.id ORDER BY criado_em DESC LIMIT 1
) ult;
```

---

## 6. Agregação e funções de janela

```sql
-- Agregação clássica: colapsa grupos em uma linha
SELECT cliente_id, COUNT(*), SUM(valor), AVG(valor), MIN(valor), MAX(valor)
FROM pedidos GROUP BY cliente_id;

-- FILTER: agregar só um subconjunto
SELECT COUNT(*) FILTER (WHERE status = 'pago') AS pagos,
       COUNT(*) FILTER (WHERE status = 'cancelado') AS cancelados
FROM pedidos;

-- string_agg / array_agg: juntar valores de um grupo
SELECT cliente_id, string_agg(descricao, ', ') FROM pedidos GROUP BY cliente_id;

-- Funções de janela: agregam SEM colapsar as linhas
SELECT
    descricao, valor,
    SUM(valor)  OVER ()                          AS total_geral,
    RANK()      OVER (ORDER BY valor DESC)       AS posicao,
    valor - LAG(valor) OVER (ORDER BY criado_em) AS diferenca_do_anterior,
    AVG(valor)  OVER (PARTITION BY cliente_id)   AS media_do_cliente
FROM pedidos;
```

| Função de janela | Faz |
|---|---|
| `ROW_NUMBER()` | Número sequencial |
| `RANK()` / `DENSE_RANK()` | Posição (com/sem pular empates) |
| `LAG(x)` / `LEAD(x)` | Valor da linha anterior/seguinte |
| `SUM/AVG/... OVER (...)` | Agregação acumulada ou por partição |
| `FIRST_VALUE` / `LAST_VALUE` / `NTH_VALUE` | Valores em posições da janela |
| `NTILE(n)` | Divide em n baldes (quartis, percentis) |

---

## 7. Tipos de dados essenciais

| Categoria | Tipos | Quando |
|---|---|---|
| **Inteiro** | `SMALLINT`, `INTEGER`, `BIGINT` | `BIGINT` para ids que podem crescer muito |
| **Identidade** | `GENERATED ALWAYS AS IDENTITY`, `SERIAL` (legado), `uuid` + `uuidv7()` | Chaves primárias |
| **Decimal exato** | `NUMERIC(p,s)` | **Dinheiro**, quantidades exatas |
| **Ponto flutuante** | `REAL`, `DOUBLE PRECISION` | Ciência, nunca dinheiro |
| **Texto** | `TEXT`, `VARCHAR(n)`, `CHAR(n)` | Prefira `TEXT`; `VARCHAR(n)` só se o limite for regra |
| **Booleano** | `BOOLEAN` | `true`/`false`/`NULL` |
| **Data/hora** | `DATE`, `TIME`, `TIMESTAMP`, `TIMESTAMPTZ`, `INTERVAL` | **Sempre `TIMESTAMPTZ`** para instantes |
| **JSON** | `JSON`, `JSONB` | **`JSONB`** quase sempre (ver seção 8) |
| **Array** | `INTEGER[]`, `TEXT[]` | Listas simples embutidas |
| **UUID** | `UUID` | Ids distribuídos, não-sequenciais |
| **Rede** | `INET`, `CIDR`, `MACADDR` | Endereços de rede, com operadores próprios |
| **Geométrico** | `POINT`, `POLYGON` (e PostGIS `geometry`) | Geolocalização |
| **Intervalo** | `INT4RANGE`, `TSRANGE`, `DATERANGE` | Faixas (reservas, períodos) |
| **Enumerado** | `CREATE TYPE ... AS ENUM (...)` | Conjunto fixo de valores |
| **Vetor** | `vector` (extensão pgvector) | IA / busca por similaridade |

```sql
-- Conversão (cast)
SELECT '42'::integer, now()::date, '2026-01-01'::timestamptz;
SELECT CAST('3.14' AS numeric);

-- Datas
SELECT now(), current_date, now() - INTERVAL '1 month';
SELECT date_trunc('month', criado_em), extract(year FROM criado_em) FROM pedidos;
SELECT age('2026-08-11', '1990-01-01');    -- diferença legível

-- Arrays
SELECT ARRAY[1,2,3], '{a,b,c}'::text[];
SELECT * FROM t WHERE 5 = ANY(tags);       -- 5 está no array?
```

Detalhes completos em [13-tipos-de-dados.md](13-tipos-de-dados.md).

---

## 8. JSON e JSONB

`JSONB` é o formato binário, indexável e mais rápido para consultar. Use-o (não o `JSON` textual)
salvo se precisar preservar a formatação exata do original.

```sql
CREATE TABLE eventos (id BIGINT GENERATED ALWAYS AS IDENTITY, dados JSONB);
INSERT INTO eventos (dados) VALUES ('{"tipo":"clique","user":42,"tags":["a","b"]}');

-- Acessar
SELECT dados->>'tipo'         FROM eventos;          -- ->> devolve TEXTO
SELECT dados->'user'          FROM eventos;          -- ->  devolve JSONB
SELECT dados#>>'{tags,0}'     FROM eventos;          -- caminho aninhado, como texto

-- Filtrar
SELECT * FROM eventos WHERE dados->>'tipo' = 'clique';
SELECT * FROM eventos WHERE dados @> '{"user":42}';  -- @> = "contém" (usa índice GIN)
SELECT * FROM eventos WHERE dados ? 'tags';          -- a chave existe?

-- Modificar
UPDATE eventos SET dados = dados || '{"visto":true}';         -- mescla
UPDATE eventos SET dados = jsonb_set(dados, '{user}', '99');  -- altera um caminho
UPDATE eventos SET dados = dados - 'tags';                    -- remove uma chave

-- Índice para consultas @>
CREATE INDEX idx_eventos_dados ON eventos USING GIN (dados);

-- Expandir para linhas/tabela
SELECT jsonb_array_elements_text(dados->'tags') FROM eventos;
SELECT * FROM jsonb_to_recordset('[{"a":1},{"a":2}]') AS x(a int);
```

| Operador | Faz |
|---|---|
| `->` | Acessa por chave/índice, devolve JSONB |
| `->>` | Acessa por chave/índice, devolve texto |
| `#>` / `#>>` | Acessa por caminho (array de chaves) |
| `@>` / `<@` | Contém / está contido (indexável por GIN) |
| `?` `?\|` `?&` | Chave existe / alguma / todas |
| `\|\|` | Concatena/mescla |
| `-` `#-` | Remove chave / caminho |

---

## 9. Índices

```sql
CREATE INDEX idx_pedidos_cliente ON pedidos (cliente_id);          -- B-tree (padrão)
CREATE UNIQUE INDEX idx_clientes_email ON clientes (email);
CREATE INDEX idx_pedidos_status_data ON pedidos (status, criado_em);  -- composto
CREATE INDEX idx_pedidos_pagos ON pedidos (criado_em) WHERE status='pago';  -- parcial
CREATE INDEX idx_clientes_lower ON clientes (lower(email));        -- por expressão
CREATE INDEX idx_eventos_dados ON eventos USING GIN (dados);       -- JSONB, arrays, full-text
CREATE INDEX idx_geo ON locais USING GIST (posicao);              -- geometria, ranges
CREATE INDEX idx_serie ON metricas USING BRIN (timestamp);         -- grandes tabelas ordenadas

CREATE INDEX CONCURRENTLY idx_x ON grande (col);   -- não bloqueia escrita (produção!)
DROP INDEX idx_x;
REINDEX INDEX idx_x;
```

| Tipo | Para |
|---|---|
| **B-tree** (padrão) | Igualdade e ordenação (`=`, `<`, `>`, `BETWEEN`, `ORDER BY`) |
| **GIN** | JSONB, arrays, busca textual (`@>`, contém) |
| **GiST** | Geometria, ranges, vizinhança |
| **BRIN** | Tabelas enormes e naturalmente ordenadas (séries temporais) — índice minúsculo |
| **Hash** | Só igualdade (`=`); raramente melhor que B-tree |
| **SP-GiST** | Dados não balanceados (quadtrees, telefones) |

Tudo sobre índices em [14-indices.md](14-indices.md).

---

## 10. Transações e bloqueios

```sql
BEGIN;
    -- ... operações ...
    SAVEPOINT antes_do_risco;
    -- ... algo que pode falhar ...
    ROLLBACK TO antes_do_risco;    -- desfaz só até o savepoint
COMMIT;   -- ou ROLLBACK;

-- Níveis de isolamento
BEGIN ISOLATION LEVEL READ COMMITTED;   -- padrão
BEGIN ISOLATION LEVEL REPEATABLE READ;
BEGIN ISOLATION LEVEL SERIALIZABLE;     -- o mais rigoroso

-- Bloqueios explícitos
SELECT * FROM contas WHERE id = 1 FOR UPDATE;         -- trava a linha para escrita
SELECT * FROM contas WHERE id = 1 FOR UPDATE SKIP LOCKED;  -- filas de trabalho
LOCK TABLE contas IN SHARE MODE;
```

Detalhes e níveis de isolamento em [15-transacoes-e-mvcc.md](15-transacoes-e-mvcc.md).

---

## 11. Funções, gatilhos e views

```sql
-- Função (PL/pgSQL)
CREATE OR REPLACE FUNCTION total_do_cliente(p_cliente_id BIGINT)
RETURNS NUMERIC LANGUAGE plpgsql AS $$
DECLARE resultado NUMERIC;
BEGIN
    SELECT COALESCE(SUM(valor), 0) INTO resultado
    FROM pedidos WHERE cliente_id = p_cliente_id;
    RETURN resultado;
END;
$$;
SELECT total_do_cliente(1);

-- Gatilho (trigger): executa automaticamente
CREATE OR REPLACE FUNCTION marca_atualizacao() RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN NEW.atualizado_em = now(); RETURN NEW; END;
$$;
CREATE TRIGGER trg_atualiza BEFORE UPDATE ON clientes
    FOR EACH ROW EXECUTE FUNCTION marca_atualizacao();

-- View: consulta salva, usada como tabela
CREATE VIEW pedidos_pagos AS SELECT * FROM pedidos WHERE status = 'pago';
SELECT * FROM pedidos_pagos;

-- Materialized view: resultado ARMAZENADO (rápido para ler, precisa atualizar)
CREATE MATERIALIZED VIEW faturamento_mensal AS
    SELECT date_trunc('month', criado_em) AS mes, SUM(valor) AS total
    FROM pedidos GROUP BY 1;
REFRESH MATERIALIZED VIEW CONCURRENTLY faturamento_mensal;   -- sem bloquear leitura
```

---

## 12. Usuários e permissões

```sql
CREATE ROLE app LOGIN PASSWORD 'senha';        -- role que pode conectar
CREATE ROLE somente_leitura;                    -- role sem login (grupo)
GRANT somente_leitura TO app;                   -- app herda os privilégios

GRANT CONNECT ON DATABASE loja TO app;
GRANT USAGE ON SCHEMA public TO app;
GRANT SELECT, INSERT, UPDATE ON clientes TO app;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO somente_leitura;
ALTER DEFAULT PRIVILEGES IN SCHEMA public       -- vale para tabelas FUTURAS
    GRANT SELECT ON TABLES TO somente_leitura;

REVOKE INSERT ON clientes FROM app;
ALTER ROLE app PASSWORD 'nova';
DROP ROLE app;

-- Row-Level Security: filtra linhas por usuário
ALTER TABLE pedidos ENABLE ROW LEVEL SECURITY;
CREATE POLICY meus_pedidos ON pedidos
    USING (cliente_id = current_setting('app.cliente_id')::bigint);
```

Segurança completa em [20-seguranca.md](20-seguranca.md).

---

## 13. Backup e restauração

```bash
# Backup lógico de UM banco
pg_dump -U usuario -d loja -Fc -f loja.dump          # -Fc = formato custom (comprimido, flexível)
pg_dump -U usuario -d loja > loja.sql                # formato SQL puro (texto)
pg_dump -U usuario -d loja -t clientes -Fc -f c.dump # só uma tabela

# Backup de TODOS os bancos + roles globais
pg_dumpall -U postgres > tudo.sql

# Restaurar
pg_restore -U usuario -d loja_nova loja.dump         # do formato custom
psql -U usuario -d loja_nova -f loja.sql             # do formato SQL
pg_restore -U usuario -d loja --jobs=4 loja.dump     # paralelo (mais rápido)

# Backup FÍSICO (para PITR — recuperação a um ponto no tempo)
pg_basebackup -U replicador -D /backup/base -Fp -Xs -P
```

> **Lógico vs. físico:** `pg_dump` (lógico) é portátil entre versões e seletivo, mas lento em
> bancos grandes. `pg_basebackup` (físico) + WAL permite recuperar a um instante exato (PITR), mas
> é da mesma major. Detalhes em [21-administracao-e-operacao.md](21-administracao-e-operacao.md).

---

## 14. Inspeção e catálogo

```sql
SELECT version();
SELECT current_database(), current_user, inet_server_addr();
SHOW ALL;                                    -- todos os parâmetros de configuração
SHOW work_mem;

-- Tamanhos
SELECT pg_size_pretty(pg_database_size('loja'));
SELECT pg_size_pretty(pg_total_relation_size('pedidos'));   -- tabela + índices + toast
SELECT relname, pg_size_pretty(pg_total_relation_size(oid))
FROM pg_class WHERE relkind='r' ORDER BY pg_total_relation_size(oid) DESC LIMIT 10;

-- Atividade e conexões
SELECT pid, usename, state, query FROM pg_stat_activity WHERE state != 'idle';
SELECT pg_terminate_backend(PID);            -- mata uma conexão travada

-- Estatísticas de uso
SELECT * FROM pg_stat_user_tables;           -- seq scans, index scans, tuplas vivas/mortas
SELECT * FROM pg_stat_user_indexes;          -- uso dos índices (idx_scan=0 → índice inútil)

-- Planejamento
EXPLAIN SELECT * FROM pedidos WHERE cliente_id = 1;
EXPLAIN (ANALYZE, BUFFERS) SELECT ...;       -- executa e mostra tempo e I/O reais
```

---

## 15. Obsoleto — o que não usar mais

| Obsoleto / desencorajado | Prefira | Por quê |
|---|---|---|
| `SERIAL` / `BIGSERIAL` | `GENERATED ALWAYS AS IDENTITY` | Padrão SQL, permissões mais limpas, sem sequência "solta" |
| `md5` no `pg_hba.conf` | `scram-sha-256` | md5 é criptograficamente fraco |
| `CHAR(n)` para textos | `TEXT` | `CHAR` preenche com espaços; raramente é o que se quer |
| `money` (tipo) | `NUMERIC` | `money` depende de locale e é inflexível |
| `TIMESTAMP` (sem tz) para instantes | `TIMESTAMPTZ` | Sem fuso, você perde a referência de tempo |
| `WITH OIDS` | (removido) | Descontinuado há muitas versões |
| `password` (autenticação em texto puro) | `scram-sha-256` | Nunca envie senha em claro |
| Trigger em C para tudo | `GENERATED`, `DEFAULT`, constraints | Muitas vezes o banco já faz declarativamente |

---

## 16. Atalhos que só quem usa há anos conhece

```sql
-- Ver a query mais lenta em execução agora
SELECT pid, now()-query_start AS duracao, query FROM pg_stat_activity
WHERE state='active' ORDER BY duracao DESC;

-- Gerar séries (ótimo para testes e relatórios sem buracos)
SELECT generate_series('2026-01-01'::date, '2026-12-01', '1 month');
SELECT generate_series(1, 1000000) AS n;     -- um milhão de linhas para testar

-- COALESCE: primeiro valor não-nulo
SELECT COALESCE(apelido, nome, 'Anônimo') FROM clientes;

-- DISTINCT ON: uma linha por grupo (o "último pedido de cada cliente")
SELECT DISTINCT ON (cliente_id) *
FROM pedidos ORDER BY cliente_id, criado_em DESC;

-- Atualizar a partir de outra tabela
UPDATE pedidos p SET regiao = c.regiao FROM clientes c WHERE c.id = p.cliente_id;

-- INSERT ... SELECT: copiar dados
INSERT INTO arquivo_pedidos SELECT * FROM pedidos WHERE criado_em < '2025-01-01';

-- Formatar saída
SELECT to_char(valor, 'L999G999D99') FROM pedidos;   -- R$ 1.234,56
SELECT to_char(now(), 'DD/MM/YYYY HH24:MI');

-- Contar rápido (aproximado) numa tabela enorme
SELECT reltuples::bigint FROM pg_class WHERE relname = 'pedidos';

-- Ver e matar bloqueios
SELECT * FROM pg_locks WHERE NOT granted;

-- \gexec: gerar e executar SQL dinamicamente (ex.: dropar todas as tabelas de um esquema)
SELECT format('DROP TABLE %I CASCADE;', tablename) FROM pg_tables WHERE schemaname='temp' \gexec

-- Medir o cache hit ratio (deve ser > 99% num banco bem configurado)
SELECT sum(heap_blks_hit)*100/nullif(sum(heap_blks_hit+heap_blks_read),0) AS hit_pct
FROM pg_statio_user_tables;
```

---

## Autoteste

1. Qual é a diferença entre `\copy` e `COPY`, e por que `\copy` costuma ser mais prático?
2. Escreva um UPSERT que insere um cliente ou atualiza o nome se o e-mail já existir.
3. Qual é a diferença entre `->` e `->>` no acesso a JSONB?
4. Quando você usaria um índice GIN em vez de B-tree?
5. O que uma função de janela faz que um `GROUP BY` não faz?
6. Qual é a diferença entre uma view e uma materialized view?
7. Por que `GENERATED ALWAYS AS IDENTITY` é preferível a `SERIAL` hoje?
8. Qual comando mostra o plano de execução real (com tempos) de uma consulta?
9. Como você mata uma conexão travada, e como a encontra primeiro?
10. Escreva a query que pega o último pedido de cada cliente usando `DISTINCT ON`.
