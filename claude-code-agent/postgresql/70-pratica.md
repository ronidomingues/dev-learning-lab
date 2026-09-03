# 70 · Prática — laboratórios progressivos

`Nível: todos` · `Última atualização: 11/08/2026`

SQL se aprende com as mãos. Cada laboratório tem **objetivo**, **passos**, **critério de
aprovação** e o **conceito que consolida**. Use qualquer ambiente do
[03-instalacao.md](03-instalacao.md) — inclusive uma nuvem gratuita ou o
[projeto-modelo](07-projeto-modelo/README.md).

---

## Lab 1 — Sobrevivência: CRUD (45 min)

**Objetivo:** criar tabela, inserir, consultar, atualizar, remover.

```sql
CREATE TABLE tarefas (
    id SERIAL PRIMARY KEY,
    titulo TEXT NOT NULL,
    feita BOOLEAN DEFAULT false,
    criada TIMESTAMPTZ DEFAULT now()
);
INSERT INTO tarefas (titulo) VALUES ('Estudar SQL'), ('Fazer o lab 1');
SELECT * FROM tarefas WHERE feita = false;
UPDATE tarefas SET feita = true WHERE id = 1;
DELETE FROM tarefas WHERE id = 2;
```

**Critério:**
- [ ] Criou a tabela e inseriu linhas.
- [ ] Consultou com `WHERE`, atualizou com `WHERE`, removeu com `WHERE`.
- [ ] Explica por que `UPDATE`/`DELETE` sem `WHERE` é perigoso.

**Consolida:** CRUD, constraints básicas.

---

## Lab 2 — Modelagem: uma lojinha (1 h)

**Objetivo:** modelar clientes, pedidos e itens com chaves estrangeiras.

```sql
CREATE TABLE clientes (id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nome TEXT NOT NULL, email TEXT UNIQUE NOT NULL);
CREATE TABLE pedidos (id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    cliente_id BIGINT NOT NULL REFERENCES clientes(id),
    criado TIMESTAMPTZ DEFAULT now());
CREATE TABLE itens (
    pedido_id BIGINT NOT NULL REFERENCES pedidos(id) ON DELETE CASCADE,
    produto TEXT NOT NULL,
    qtd INT NOT NULL CHECK (qtd > 0),
    preco NUMERIC(10,2) NOT NULL CHECK (preco >= 0),
    PRIMARY KEY (pedido_id, produto));
```

Insira dados e tente violar as regras:
```sql
INSERT INTO pedidos (cliente_id) VALUES (999);        -- deve FALHAR (FK)
INSERT INTO itens VALUES (1, 'x', -1, 10);            -- deve FALHAR (CHECK qtd)
```

**Critério:**
- [ ] O banco recusou o pedido para cliente inexistente.
- [ ] O banco recusou quantidade negativa.
- [ ] Você entende a chave primária composta de `itens`.

**Consolida:** modelagem, FK, CHECK, chave composta.

---

## Lab 3 — Consultas: JOINs e agregação (1 h)

Com os dados do Lab 2:
```sql
-- Total de cada pedido
SELECT pedido_id, SUM(qtd * preco) AS total FROM itens GROUP BY pedido_id;

-- Nome do cliente ao lado do total
SELECT c.nome, SUM(i.qtd * i.preco) AS total
FROM clientes c
JOIN pedidos p ON p.cliente_id = c.id
JOIN itens i ON i.pedido_id = p.id
GROUP BY c.nome
ORDER BY total DESC;

-- Clientes SEM pedidos (LEFT JOIN)
SELECT c.nome FROM clientes c
LEFT JOIN pedidos p ON p.cliente_id = c.id
WHERE p.id IS NULL;
```

**Critério:**
- [ ] Fez um JOIN de três tabelas.
- [ ] Agregou com `GROUP BY` e `SUM`.
- [ ] Encontrou clientes sem pedidos com `LEFT JOIN ... IS NULL`.

**Consolida:** JOINs, agregação, o padrão "sem correspondência".

---

## Lab 4 — NULL e as armadilhas (30 min)

```sql
CREATE TABLE t (id INT, valor INT);
INSERT INTO t VALUES (1, 10), (2, NULL), (3, 20);

SELECT * FROM t WHERE valor = NULL;         -- 0 linhas! (armadilha)
SELECT * FROM t WHERE valor IS NULL;        -- id 2
SELECT count(*), count(valor) FROM t;       -- 3 e 2 (count(coluna) ignora NULL)
SELECT sum(valor), avg(valor) FROM t;       -- 30, 15 (ignoram NULL)
SELECT id, COALESCE(valor, 0) FROM t;       -- substitui NULL por 0
```

**Critério:**
- [ ] Entende por que `= NULL` não funciona.
- [ ] Sabe a diferença entre `count(*)` e `count(coluna)`.
- [ ] Usou `COALESCE`.

**Consolida:** a lógica de três valores.

---

## Lab 5 — Índices e EXPLAIN (1 h)

```sql
-- Crie uma tabela grande
CREATE TABLE eventos (id BIGINT GENERATED ALWAYS AS IDENTITY, user_id INT, dado TEXT);
INSERT INTO eventos (user_id, dado)
SELECT (random()*1000)::int, 'x' FROM generate_series(1, 1000000);

-- Antes do índice
EXPLAIN ANALYZE SELECT * FROM eventos WHERE user_id = 42;   -- Seq Scan, lento

CREATE INDEX ix_eventos_user ON eventos (user_id);
ANALYZE eventos;

-- Depois
EXPLAIN ANALYZE SELECT * FROM eventos WHERE user_id = 42;   -- Index Scan, rápido
```

**Critério:**
- [ ] Viu "Seq Scan" virar "Index Scan".
- [ ] Comparou o `Execution Time` antes e depois.
- [ ] Entende por que o índice ajudou aqui (filtro seletivo).

**Consolida:** índices, EXPLAIN ANALYZE.

---

## Lab 6 — Transações e concorrência (45 min)

Abra **duas** sessões `psql` lado a lado.

```sql
-- Sessão 1
CREATE TABLE contas (id INT PRIMARY KEY, saldo NUMERIC);
INSERT INTO contas VALUES (1, 100), (2, 100);
BEGIN;
UPDATE contas SET saldo = saldo - 50 WHERE id = 1;   -- NÃO commitou ainda

-- Sessão 2 (ao mesmo tempo)
SELECT saldo FROM contas WHERE id = 1;   -- ainda vê 100 (MVCC: não vê o não-commitado)

-- Sessão 1
COMMIT;

-- Sessão 2
SELECT saldo FROM contas WHERE id = 1;   -- agora vê 50
```

**Critério:**
- [ ] Confirmou que a sessão 2 não viu a mudança não-commitada.
- [ ] Viu a mudança aparecer após o `COMMIT`.
- [ ] Testou `ROLLBACK` e confirmou que desfaz.

**Consolida:** MVCC, isolamento, atomicidade.

---

## Lab 7 — JSONB (45 min)

```sql
CREATE TABLE produtos (id BIGINT GENERATED ALWAYS AS IDENTITY, nome TEXT, attr JSONB);
INSERT INTO produtos (nome, attr) VALUES
 ('Camiseta', '{"cor":"azul","tam":"M"}'),
 ('Livro', '{"paginas":300,"idioma":"pt"}');

SELECT nome, attr->>'cor' FROM produtos;
SELECT * FROM produtos WHERE attr @> '{"cor":"azul"}';
SELECT nome FROM produtos WHERE (attr->>'paginas')::int > 200;
CREATE INDEX ix_prod_attr ON produtos USING GIN (attr);
```

**Critério:**
- [ ] Extraiu um campo com `->>`.
- [ ] Filtrou com `@>`.
- [ ] Criou um índice GIN.
- [ ] Sabe dizer o que deveria ser coluna de verdade em vez de JSONB.

**Consolida:** JSONB, GIN.

---

## Lab 8 — Funções de janela (45 min)

```sql
CREATE TABLE vendas (vendedor TEXT, mes INT, valor NUMERIC);
INSERT INTO vendas VALUES ('Ana',1,100),('Ana',2,150),('Bruno',1,200),('Bruno',2,120);

SELECT vendedor, mes, valor,
       RANK() OVER (ORDER BY valor DESC) AS posicao,
       SUM(valor) OVER (PARTITION BY vendedor ORDER BY mes) AS acumulado
FROM vendas;
```

**Critério:**
- [ ] Entende que a janela não colapsa as linhas.
- [ ] Usou `PARTITION BY` e `ORDER BY` na janela.

**Consolida:** funções de janela.

---

## Lab 9 — Backup e restauração (30 min)

```bash
pg_dump -Fc -d SEU_BANCO -f backup.dump
# apague uma tabela de propósito
psql -d SEU_BANCO -c "DROP TABLE tarefas;"
# restaure só ela
pg_restore -d SEU_BANCO -t tarefas backup.dump
psql -d SEU_BANCO -c "SELECT count(*) FROM tarefas;"   # voltou
```

**Critério:**
- [ ] Fez um dump, apagou dados, restaurou.
- [ ] Verificou que os dados voltaram.

**Consolida:** backup lógico.

---

## Lab 10 — Do zero à aplicação (projeto integrador, 3 h)

**Objetivo:** pegar o [projeto-modelo](07-projeto-modelo/README.md) (ou modelar o seu) e levar a um
estado completo.

1. **Modelar** um domínio real (biblioteca, blog, loja) com 4+ tabelas, FKs e constraints.
   - [ ] Toda tabela tem PK; regras no banco (CHECK, UNIQUE, FK).
2. **Popular** com dados de exemplo (`generate_series` ajuda).
3. **Consultar** — 5 consultas úteis com JOIN, agregação, janela.
4. **Indexar** — rode `EXPLAIN ANALYZE` numa consulta lenta e crie o índice certo.
   - [ ] Mostrou "Seq Scan" virar "Index Scan".
5. **Transação** — uma operação de negócio tudo-ou-nada (empréstimo, transferência).
6. **Segurança** — crie um role de aplicação com privilégio mínimo (não superusuário).
7. **Backup** — dump verificado, e teste de restauração.

**Critério final:**
- [ ] Outra pessoa entende o modelo lendo o esquema.
- [ ] Você explica cada índice, constraint e transação.
- [ ] A aplicação (se houver) usa consultas **parametrizadas** e um role restrito.

**Consolida:** tudo.

---

## Autoavaliação final

Se você faz o Lab 10 sem consultar, você **sabe PostgreSQL** no nível de desenvolvedor produtivo. O
que falta é administração em escala ([21](21-administracao-e-operacao.md)),
replicação ([19](19-replicacao-e-alta-disponibilidade.md)) e o interno
([15](15-transacoes-e-mvcc.md), [16](16-consultas-e-planejador.md),
[17](17-arquitetura-interna.md), [60](60-teoria-avancada.md)).

Erros que você deveria diagnosticar em menos de um minuto ao final:
1. `WHERE x = NULL` não retorna nada.
2. A consulta ficou lenta → estatísticas ou índice.
3. `UPDATE`/`DELETE` sem `WHERE`.
4. Float para dinheiro dá centavos errados.
5. `LEFT JOIN` que virou `INNER` por causa do `WHERE`.
6. "too many clients" → falta pool.
7. Disco enchendo → bloat/autovacuum.
8. Aspas simples vs. duplas.

Se algum te trava, volte ao arquivo correspondente. As respostas estão em
[75-armadilhas.md](75-armadilhas.md).
