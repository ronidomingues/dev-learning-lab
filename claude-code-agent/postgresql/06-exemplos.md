# 06 · Exemplos — 14 receitas completas e executáveis

`Nível: intermediário` · `Todo SQL é completo — nada de "..."` · `Última atualização: 11/08/2026`

Cada exemplo: **problema → solução → explicação**. Os últimos quatro são casos reais de produção.
Copie, cole no `psql`, veja funcionar.

| # | Exemplo | Nível |
|---|---|---|
| [1](#1-modelar-um-blog-do-zero) | Modelar um blog do zero | básico |
| [2](#2-paginação-correta) | Paginação correta (e a errada) | básico |
| [3](#3-relatório-de-vendas-com-group-by) | Relatório de vendas | básico |
| [4](#4-upsert-contador-de-acessos) | UPSERT: contador de acessos | básico |
| [5](#5-busca-textual-em-português) | Busca textual em português | intermediário |
| [6](#6-jsonb-catálogo-de-produtos-flexível) | JSONB: catálogo flexível | intermediário |
| [7](#7-hierarquia-com-cte-recursiva) | Hierarquia com CTE recursiva | intermediário |
| [8](#8-janelas-ranking-e-média-móvel) | Janelas: ranking e média móvel | intermediário |
| [9](#9-evitar-reserva-em-dobro-com-exclusão) | Evitar reserva em dobro | avançado |
| [10](#10-auditoria-automática-com-gatilho) | Auditoria com gatilho | avançado |
| [11](#11-fila-de-trabalho-com-skip-locked) | Fila de trabalho | avançado |
| [12](#12-produção--particionamento-por-data) | **Produção:** particionamento | avançado |
| [13](#13-produção--busca-por-similaridade-com-pgvector) | **Produção:** pgvector (IA) | avançado |
| [14](#14-produção--diagnóstico-de-consulta-lenta) | **Produção:** consulta lenta | avançado |

---

## 1. Modelar um blog do zero

**Problema:** autores escrevem posts; posts têm tags; leitores comentam.

```sql
CREATE TABLE autores (
    id     BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nome   TEXT NOT NULL,
    email  TEXT UNIQUE NOT NULL
);

CREATE TABLE posts (
    id         BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    autor_id   BIGINT NOT NULL REFERENCES autores(id) ON DELETE CASCADE,
    titulo     TEXT NOT NULL,
    corpo      TEXT NOT NULL,
    publicado  BOOLEAN NOT NULL DEFAULT false,
    criado_em  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE tags (
    id    BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nome  TEXT UNIQUE NOT NULL
);

-- Relação MUITOS-PARA-MUITOS: um post tem várias tags, uma tag em vários posts
CREATE TABLE posts_tags (
    post_id  BIGINT NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    tag_id   BIGINT NOT NULL REFERENCES tags(id)  ON DELETE CASCADE,
    PRIMARY KEY (post_id, tag_id)          -- chave composta: evita a mesma tag duas vezes
);

CREATE TABLE comentarios (
    id         BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    post_id    BIGINT NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    autor_nome TEXT NOT NULL,
    corpo      TEXT NOT NULL,
    criado_em  TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

**Explicação.** A **tabela de junção** `posts_tags` é o padrão para relações muitos-para-muitos:
ela não guarda dados próprios, só o par de chaves. A chave primária composta `(post_id, tag_id)`
garante que um post não receba a mesma tag duas vezes. Os `ON DELETE CASCADE` fazem os
comentários e as ligações de tag sumirem quando o post é apagado — sem deixar órfãos. Este é o
esqueleto de metade das aplicações web que existem.

---

## 2. Paginação correta

**Problema:** mostrar resultados de 20 em 20, sem repetir nem pular itens.

```sql
-- ❌ A forma ingênua (OFFSET): fica LENTA em páginas altas e pode pular/repetir
SELECT * FROM posts ORDER BY criado_em DESC LIMIT 20 OFFSET 10000;
--    o banco lê e descarta 10.000 linhas para devolver 20

-- ✅ Paginação por keyset (cursor): rápida e estável
SELECT * FROM posts
WHERE (criado_em, id) < ('2026-08-01 10:00:00', 5000)   -- "depois do último visto"
ORDER BY criado_em DESC, id DESC
LIMIT 20;
```

**Explicação.** `OFFSET 10000` obriga o banco a percorrer e jogar fora 10 mil linhas a cada
página — o custo cresce com a profundidade. A **paginação por keyset** guarda a chave do último
item da página anterior e pede "os próximos a partir daqui", usando o índice. Some `id` ao
critério de ordenação para desempatar linhas com o mesmo `criado_em`. Para feeds infinitos e APIs
sérias, keyset é o padrão; `OFFSET` só serve para poucas páginas.

---

## 3. Relatório de vendas com GROUP BY

**Problema:** faturamento por mês e por categoria, com totais.

```sql
-- Dados de apoio
CREATE TABLE vendas (
    id         BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    categoria  TEXT NOT NULL,
    valor      NUMERIC(10,2) NOT NULL,
    data       DATE NOT NULL
);
INSERT INTO vendas (categoria, valor, data) VALUES
 ('livros', 45.00, '2026-01-15'), ('livros', 30.00, '2026-02-10'),
 ('eletrônicos', 500.00, '2026-01-20'), ('eletrônicos', 800.00, '2026-02-05');

-- Faturamento por mês e categoria, com subtotais e total geral (ROLLUP)
SELECT
    date_trunc('month', data)::date AS mes,
    categoria,
    SUM(valor) AS total
FROM vendas
GROUP BY ROLLUP (date_trunc('month', data), categoria)
ORDER BY mes NULLS LAST, categoria NULLS LAST;
```

**Explicação.** `date_trunc('month', data)` "arredonda" a data para o primeiro dia do mês,
agrupando por período. `ROLLUP` gera, além dos grupos normais, **linhas de subtotal** (por mês,
somando categorias) e o **total geral** (linha com `mes` e `categoria` nulos). É o que uma
planilha dinâmica faz — em uma linha de SQL. Para tabelas cruzadas completas, veja `CUBE` e
`GROUPING SETS`.

---

## 4. UPSERT: contador de acessos

**Problema:** contar visitas por página. Se a página é nova, cria com 1; se já existe, soma.

```sql
CREATE TABLE acessos (
    pagina    TEXT PRIMARY KEY,
    total     BIGINT NOT NULL DEFAULT 0,
    ultimo    TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Uma linha resolve os dois casos
INSERT INTO acessos (pagina, total) VALUES ('/home', 1)
ON CONFLICT (pagina) DO UPDATE
SET total = acessos.total + 1,
    ultimo = now();
```

**Explicação.** `ON CONFLICT (pagina)` diz "se bater na chave única `pagina`, não dê erro — faça
isto". `EXCLUDED` referencia a linha que você *tentou* inserir; `acessos.total` é o valor *atual*
na tabela. Sem UPSERT, você precisaria de um `SELECT` para verificar e então `INSERT` ou `UPDATE`
— duas idas ao banco e uma condição de corrida entre elas. O UPSERT é **atômico**: correto mesmo
com mil requisições simultâneas.

---

## 5. Busca textual em português

**Problema:** buscar artigos por palavra, ignorando acentos, plurais e palavras comuns ("de",
"a", "os").

```sql
CREATE TABLE artigos (
    id       BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    titulo   TEXT NOT NULL,
    corpo    TEXT NOT NULL,
    -- coluna gerada com o "documento de busca", com pesos (título vale mais que corpo)
    busca    TSVECTOR GENERATED ALWAYS AS (
        setweight(to_tsvector('portuguese', titulo), 'A') ||
        setweight(to_tsvector('portuguese', corpo),  'B')
    ) STORED
);
CREATE INDEX idx_artigos_busca ON artigos USING GIN (busca);

INSERT INTO artigos (titulo, corpo) VALUES
 ('Cultivo de tomates', 'Os tomateiros precisam de sol e água regular.'),
 ('Receita de molho',   'Tomate, cebola e manjericão fazem um bom molho.');

-- Buscar "tomate" acha "tomates" e "tomateiros" (mesma raiz)
SELECT titulo, ts_rank(busca, query) AS relevancia
FROM artigos, to_tsquery('portuguese', 'tomate') query
WHERE busca @@ query
ORDER BY relevancia DESC;
```

**Explicação.** `to_tsvector('portuguese', ...)` quebra o texto em radicais (*stemming*),
removendo acentos e palavras irrelevantes (*stop words*) segundo as regras do português — por isso
"tomate" encontra "tomateiros". `@@` é o operador de correspondência; `ts_rank` ordena por
relevância; `setweight` dá mais peso ao título. O índice **GIN** torna isso rápido em milhões de
documentos. É busca de qualidade decente **sem** instalar Elasticsearch — e para muitos projetos,
é o suficiente.

---

## 6. JSONB: catálogo de produtos flexível

**Problema:** produtos com atributos que variam por categoria (uma camiseta tem tamanho e cor; um
livro tem autor e páginas). Sem criar 50 colunas.

```sql
CREATE TABLE produtos (
    id         BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nome       TEXT NOT NULL,
    preco      NUMERIC(10,2) NOT NULL,
    atributos  JSONB NOT NULL DEFAULT '{}'
);
CREATE INDEX idx_produtos_attr ON produtos USING GIN (atributos);

INSERT INTO produtos (nome, preco, atributos) VALUES
 ('Camiseta', 49.90, '{"tamanho":"M","cor":"azul","material":"algodão"}'),
 ('Livro SQL', 89.00, '{"autor":"Fulano","paginas":320,"idioma":"pt"}');

-- Buscar por atributo (usa o índice GIN)
SELECT nome, preco FROM produtos WHERE atributos @> '{"cor":"azul"}';

-- Filtrar por número dentro do JSON
SELECT nome FROM produtos WHERE (atributos->>'paginas')::int > 300;

-- Extrair um atributo como coluna
SELECT nome, atributos->>'material' AS material FROM produtos;
```

**Explicação.** JSONB dá a flexibilidade de um banco de documentos **dentro** do relacional: você
mantém as colunas fixas (`nome`, `preco`) com todas as garantias, e joga o que varia em
`atributos`. O operador `@>` ("contém") usa o índice GIN e é rápido. **Cuidado com o exagero:** o
que é sempre consultado, filtrado ou tem regra de negócio deve ser **coluna de verdade** — JSONB é
para o genuinamente variável. Colocar tudo em JSONB joga fora metade do valor do PostgreSQL. Ver
[13-tipos-de-dados.md](13-tipos-de-dados.md).

---

## 7. Hierarquia com CTE recursiva

**Problema:** um organograma (funcionário → chefe → chefe do chefe). Listar toda a cadeia sob
alguém.

```sql
CREATE TABLE funcionarios (
    id       BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nome     TEXT NOT NULL,
    chefe_id BIGINT REFERENCES funcionarios(id)   -- aponta para a própria tabela
);
INSERT INTO funcionarios (nome, chefe_id) VALUES
 ('CEO', NULL), ('Diretora', 1), ('Gerente', 2), ('Analista', 3), ('Estagiário', 4);

-- Toda a cadeia abaixo da Diretora (id=2), com o nível de profundidade
WITH RECURSIVE cadeia AS (
    SELECT id, nome, chefe_id, 1 AS nivel
    FROM funcionarios WHERE id = 2               -- caso base: o ponto de partida
  UNION ALL
    SELECT f.id, f.nome, f.chefe_id, c.nivel + 1
    FROM funcionarios f JOIN cadeia c ON f.chefe_id = c.id   -- passo recursivo
)
SELECT repeat('  ', nivel-1) || nome AS organograma, nivel FROM cadeia ORDER BY nivel;
```

**Explicação.** A CTE recursiva tem duas partes unidas por `UNION ALL`: o **caso base** (a linha
inicial) e o **passo recursivo** (que se junta ao resultado acumulado até não achar mais filhos). É
a forma padrão de percorrer árvores e grafos em SQL — organogramas, categorias aninhadas, listas de
materiais, dependências. Sem recursão, isso exigiria um número desconhecido de JOINs. Cuidado com
ciclos: em grafos com laços, use `UNION` (sem `ALL`) ou uma cláusula `CYCLE`.

---

## 8. Janelas: ranking e média móvel

**Problema:** para cada vendedor, sua posição no ranking do mês e a média móvel de 3 dias das
vendas.

```sql
CREATE TABLE vendas_diarias (
    vendedor TEXT NOT NULL,
    dia      DATE NOT NULL,
    valor    NUMERIC(10,2) NOT NULL
);
INSERT INTO vendas_diarias VALUES
 ('Ana','2026-08-01',100),('Ana','2026-08-02',150),('Ana','2026-08-03',120),
 ('Bruno','2026-08-01',200),('Bruno','2026-08-02',180);

SELECT
    vendedor, dia, valor,
    RANK() OVER (ORDER BY valor DESC) AS posicao_geral,
    SUM(valor) OVER (PARTITION BY vendedor ORDER BY dia) AS acumulado_do_vendedor,
    AVG(valor) OVER (
        PARTITION BY vendedor ORDER BY dia
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ) AS media_movel_3d
FROM vendas_diarias
ORDER BY vendedor, dia;
```

**Explicação.** Funções de janela calculam sobre um conjunto de linhas **sem colapsá-las** — cada
linha mantém sua identidade e ganha colunas calculadas. `PARTITION BY` cria "grupos" independentes
(um por vendedor); `ORDER BY` define a ordem dentro da janela; `ROWS BETWEEN 2 PRECEDING AND
CURRENT ROW` define a "moldura" da média móvel (esta linha e as duas anteriores). É o ferramental
de análise que substitui exportar tudo para uma planilha.

---

## 9. Evitar reserva em dobro com exclusão

**Problema:** um sistema de reservas de sala. Duas pessoas não podem reservar horários que se
sobrepõem — e a checagem precisa ser à prova de concorrência.

```sql
CREATE EXTENSION IF NOT EXISTS btree_gist;   -- permite misturar '=' e ranges no índice

CREATE TABLE reservas (
    id       BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    sala_id  BIGINT NOT NULL,
    periodo  TSRANGE NOT NULL,
    -- A MÁGICA: o banco recusa duas reservas da mesma sala com períodos que se cruzam
    EXCLUDE USING GIST (sala_id WITH =, periodo WITH &&)
);

INSERT INTO reservas (sala_id, periodo) VALUES (1, '[2026-08-11 10:00, 2026-08-11 11:00)');

-- Esta falha, porque sobrepõe a anterior na mesma sala:
INSERT INTO reservas (sala_id, periodo) VALUES (1, '[2026-08-11 10:30, 2026-08-11 11:30)');
-- ERROR: conflicting key value violates exclusion constraint "reservas_sala_id_periodo_excl"
```

**Explicação.** A **restrição de exclusão** (`EXCLUDE`) é uma joia pouco conhecida do PostgreSQL:
ela generaliza o `UNIQUE`. Em vez de "não pode haver dois valores iguais", diz "não pode haver dois
valores que satisfaçam esta relação" — aqui, `&&` (sobreposição de intervalos) na mesma sala. O
banco garante isso mesmo com mil inserções simultâneas, sem você escrever nenhuma lógica de
bloqueio. Fazer isso na aplicação seria propenso a condições de corrida; no banco, é uma linha.

---

## 10. Auditoria automática com gatilho

**Problema:** registrar automaticamente toda alteração numa tabela de salários — quem, quando, de
quanto para quanto.

```sql
CREATE TABLE salarios (
    id           BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    funcionario  TEXT NOT NULL,
    valor        NUMERIC(10,2) NOT NULL
);

CREATE TABLE salarios_auditoria (
    id           BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    salario_id   BIGINT,
    valor_antigo NUMERIC(10,2),
    valor_novo   NUMERIC(10,2),
    usuario      TEXT NOT NULL DEFAULT current_user,
    quando       TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE OR REPLACE FUNCTION audita_salario() RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    INSERT INTO salarios_auditoria (salario_id, valor_antigo, valor_novo)
    VALUES (NEW.id, OLD.valor, NEW.valor);
    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_audita_salario
    AFTER UPDATE OF valor ON salarios       -- só dispara se 'valor' mudar
    FOR EACH ROW WHEN (OLD.valor IS DISTINCT FROM NEW.valor)
    EXECUTE FUNCTION audita_salario();

UPDATE salarios SET valor = 6000 WHERE id = 1;   -- gera uma linha de auditoria sozinha
```

**Explicação.** Um **gatilho** (*trigger*) executa código automaticamente em resposta a
`INSERT`/`UPDATE`/`DELETE`. Aqui, toda mudança de salário grava um registro de auditoria — sem
depender de a aplicação lembrar de fazê-lo, e capturando também mudanças feitas direto no `psql`.
`OLD` e `NEW` são as versões antiga e nova da linha; `IS DISTINCT FROM` compara tratando `NULL`
corretamente. *Ressalva profissional:* gatilhos são poderosos e **invisíveis** — lógica escondida
que surpreende quem lê só a aplicação. Use com moderação e documente.

---

## 11. Fila de trabalho com SKIP LOCKED

**Problema:** vários *workers* consomem tarefas de uma fila. Cada tarefa só pode ser pega por um
worker, e um worker não pode ficar esperando outro.

```sql
CREATE TABLE fila (
    id       BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tarefa   TEXT NOT NULL,
    status   TEXT NOT NULL DEFAULT 'pendente',
    criado   TIMESTAMPTZ NOT NULL DEFAULT now()
);
INSERT INTO fila (tarefa) SELECT 'processar ' || n FROM generate_series(1,5) n;

-- Cada worker roda isto: pega UMA tarefa livre, sem colidir com os outros
BEGIN;
    SELECT id, tarefa FROM fila
    WHERE status = 'pendente'
    ORDER BY criado
    FOR UPDATE SKIP LOCKED        -- trava a linha; pula as que outros já travaram
    LIMIT 1;
    -- ... processa ...
    UPDATE fila SET status = 'feito' WHERE id = <id_pego>;
COMMIT;
```

**Explicação.** `FOR UPDATE` trava as linhas selecionadas até o fim da transação. `SKIP LOCKED`
diz "se uma linha já está travada por outra transação, **pule-a** em vez de esperar". Assim, dez
workers rodando a mesma query pegam dez tarefas **diferentes**, sem coordenação externa e sem
bloqueio mútuo. É como se implementa uma fila de trabalho confiável usando só o PostgreSQL — antes
de recorrer a um sistema de filas dedicado (RabbitMQ, SQS), muitas aplicações resolvem isso aqui.

---

## 12. PRODUÇÃO — particionamento por data

**Problema real:** uma tabela de logs cresce para bilhões de linhas. Consultas e a manutenção
(apagar dados antigos) ficam lentas. Solução: dividir a tabela por mês.

```sql
-- Tabela PARTICIONADA por faixa de data
CREATE TABLE logs (
    id        BIGINT GENERATED ALWAYS AS IDENTITY,
    nivel     TEXT NOT NULL,
    mensagem  TEXT NOT NULL,
    criado_em TIMESTAMPTZ NOT NULL DEFAULT now()
) PARTITION BY RANGE (criado_em);

-- Uma partição por mês (cada uma é uma tabela física separada)
CREATE TABLE logs_2026_08 PARTITION OF logs
    FOR VALUES FROM ('2026-08-01') TO ('2026-09-01');
CREATE TABLE logs_2026_09 PARTITION OF logs
    FOR VALUES FROM ('2026-09-01') TO ('2026-10-01');

-- Índice em cada partição (herda a definição)
CREATE INDEX ON logs (criado_em);

INSERT INTO logs (nivel, mensagem) VALUES ('info', 'começou');
-- vai para a partição do mês certo automaticamente

-- Consultar um mês: o planejador lê SÓ a partição relevante (partition pruning)
EXPLAIN SELECT * FROM logs WHERE criado_em >= '2026-08-01' AND criado_em < '2026-09-01';

-- Apagar dados antigos: instantâneo — solta a tabela inteira, não apaga linha a linha
ALTER TABLE logs DETACH PARTITION logs_2026_08;
DROP TABLE logs_2026_08;
```

**Explicação.** O **particionamento** divide uma tabela lógica em várias físicas por um critério
(aqui, faixa de data). Ganhos: consultas que filtram por data leem só as partições relevantes
(*partition pruning*); apagar um período é um `DROP TABLE` instantâneo, não um `DELETE` de milhões
de linhas (que geraria imensa carga de VACUUM); e a manutenção (VACUUM, REINDEX) roda por
partição. Ferramentas como `pg_partman` automatizam a criação e o descarte de partições. É a
técnica-chave para séries temporais e logs em escala.

---

## 13. PRODUÇÃO — busca por similaridade com pgvector

**Problema real:** uma aplicação de IA precisa encontrar documentos "parecidos" com uma pergunta,
por significado (não por palavra exata) — a base de RAG (*Retrieval-Augmented Generation*).

```sql
CREATE EXTENSION IF NOT EXISTS vector;    -- pgvector

CREATE TABLE documentos (
    id        BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    conteudo  TEXT NOT NULL,
    embedding VECTOR(1536)                 -- o "significado" como vetor (ex.: OpenAI ada = 1536 dim)
);

-- Índice HNSW: busca aproximada de vizinhos mais próximos, rápida em milhões de vetores
CREATE INDEX ON documentos USING hnsw (embedding vector_cosine_ops);

-- Você gera os embeddings na aplicação (com um modelo) e insere:
-- INSERT INTO documentos (conteudo, embedding) VALUES ('texto...', '[0.1, 0.2, ...]');

-- Encontrar os 5 documentos mais próximos de uma pergunta (também vetorizada)
SELECT conteudo, 1 - (embedding <=> '[0.15, 0.19, ...]') AS similaridade
FROM documentos
ORDER BY embedding <=> '[0.15, 0.19, ...]'    -- <=> = distância do cosseno
LIMIT 5;
```

**Explicação.** Um *embedding* é uma lista de números que representa o **significado** de um texto:
textos parecidos ficam "próximos" nesse espaço. O `pgvector` adiciona o tipo `VECTOR` e operadores
de distância (`<=>` cosseno, `<->` euclidiana, `<#>` produto interno). O índice **HNSW** torna a
busca dos vizinhos mais próximos rápida mesmo com milhões de vetores. *Por que isto importa:*
significa que você pode fazer busca semântica e a recuperação de contexto para LLMs **dentro do seu
banco relacional**, ao lado dos dados de negócio, sem um banco vetorial separado. Foi um dos
maiores motores de adoção do PostgreSQL em 2024–2026. Ver
[65-estado-da-arte.md](65-estado-da-arte.md).

---

## 14. PRODUÇÃO — diagnóstico de consulta lenta

**Problema real:** uma consulta que era rápida ficou lenta em produção. Como descobrir por quê e
corrigir.

```sql
-- 1) Veja o plano REAL de execução (executa a query e mede)
EXPLAIN (ANALYZE, BUFFERS, VERBOSE)
SELECT c.nome, COUNT(p.id)
FROM clientes c LEFT JOIN pedidos p ON p.cliente_id = c.id
WHERE c.criado_em > '2026-01-01'
GROUP BY c.nome;
```

O que procurar na saída:
```
Seq Scan on pedidos  (cost=... rows=... actual time=... rows=2000000 ...)
  ↑ "Seq Scan" numa tabela grande + filtro seletivo = provável FALTA DE ÍNDICE
Rows Removed by Filter: 1999900
  ↑ leu 2 milhões, descartou quase todas = índice resolveria
```

```sql
-- 2) Crie o índice que o filtro/join precisa (sem bloquear a tabela, em produção)
CREATE INDEX CONCURRENTLY idx_pedidos_cliente ON pedidos (cliente_id);
CREATE INDEX CONCURRENTLY idx_clientes_criado ON clientes (criado_em);

-- 3) Reexecute o EXPLAIN ANALYZE e compare: "Seq Scan" deve virar "Index Scan"

-- 4) Ache as consultas mais custosas do sistema (exige a extensão)
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;   -- (adicionar em shared_preload_libraries)
SELECT
    round(total_exec_time::numeric, 1) AS tempo_total_ms,
    calls,
    round(mean_exec_time::numeric, 2) AS media_ms,
    query
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 10;

-- 5) Estatísticas desatualizadas enganam o planejador — atualize
ANALYZE pedidos;

-- 6) Índices que nunca são usados (candidatos a remover — cada índice custa na escrita)
SELECT schemaname, relname, indexrelname, idx_scan
FROM pg_stat_user_indexes WHERE idx_scan = 0 ORDER BY relname;
```

**Explicação.** `EXPLAIN ANALYZE` é a ferramenta nº 1 de desempenho: mostra **como** o banco
executou a consulta e **onde** gastou o tempo. `Seq Scan` (varredura sequencial) numa tabela grande
com um filtro seletivo quase sempre indica falta de índice. `pg_stat_statements` revela quais
consultas consomem mais tempo **no sistema todo** — muitas vezes o gargalo não é a query que você
está olhando. `CONCURRENTLY` cria o índice sem travar a tabela (essencial em produção). E `ANALYZE`
mantém as estatísticas que o planejador usa para decidir — estatísticas velhas geram planos ruins.
Tudo isso em [16-consultas-e-planejador.md](16-consultas-e-planejador.md).

---

## Autoteste

1. Por que a paginação por `OFFSET` fica lenta em páginas altas, e o que a substitui?
2. O que é uma tabela de junção, e por que a chave primária dela é composta?
3. Explique o UPSERT (`ON CONFLICT`) e por que ele é melhor que "SELECT depois INSERT ou UPDATE".
4. No exemplo 5, por que buscar "tomate" encontra "tomateiros"?
5. Quando você deve usar uma coluna JSONB e quando deve usar uma coluna de verdade?
6. Descreva as duas partes de uma CTE recursiva.
7. O que uma restrição `EXCLUDE` garante que um `UNIQUE` não garante?
8. Como `FOR UPDATE SKIP LOCKED` permite uma fila de trabalho sem coordenação externa?
9. Quais são os dois maiores ganhos do particionamento por data?
10. Na saída de `EXPLAIN ANALYZE`, o que "Seq Scan" numa tabela grande com filtro seletivo
    costuma indicar?
