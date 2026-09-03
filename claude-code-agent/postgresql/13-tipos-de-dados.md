# 13 · Tipos de dados — a riqueza que distingue o PostgreSQL

`Nível: intermediário → avançado` · `Última atualização: 11/08/2026`

A variedade e a qualidade dos tipos é uma das grandes vantagens do PostgreSQL sobre concorrentes.
Escolher o tipo certo é uma decisão de correção e de desempenho — não um detalhe.

---

## 1. Números — e a regra sagrada do dinheiro

| Tipo | Tamanho | Faixa / precisão | Use para |
|---|---|---|---|
| `SMALLINT` | 2 bytes | ±32 mil | Valores pequenos e certos |
| `INTEGER` | 4 bytes | ±2,1 bilhões | Inteiros comuns |
| `BIGINT` | 8 bytes | ±9,2 quintilhões | Ids, contadores que crescem muito |
| `NUMERIC(p,s)` | variável | **exato**, até 1000 dígitos | **Dinheiro**, quantidades exatas |
| `REAL` | 4 bytes | ~6 dígitos, **aproximado** | Ciência, sensores |
| `DOUBLE PRECISION` | 8 bytes | ~15 dígitos, **aproximado** | Ciência |

> ### ⚠️ A regra que não se negocia: dinheiro é `NUMERIC`, nunca `float`
> ```sql
> SELECT 0.1::real + 0.2::real;       -- 0.3 ... mas internamente 0.30000001
> SELECT 0.1::numeric + 0.2::numeric; -- 0.3 exato
> SELECT sum(valor) FROM (VALUES (0.1::float),(0.2),(0.3)) v(valor); -- pode dar 0.6000000000000001
> ```
> Ponto flutuante (`real`/`double`) representa números em base 2, e frações decimais como 0.1 não
> têm representação exata em base 2 — o mesmo motivo pelo qual 1/3 não tem representação decimal
> exata. Some milhares de valores e os centavos derretem. **Para qualquer coisa contada em
> dinheiro, use `NUMERIC`.** O tipo `money` existe, mas depende de locale e é inflexível — prefira
> `NUMERIC`.

Ids: **prefira `BIGINT ... GENERATED ALWAYS AS IDENTITY`** a `INTEGER`. O custo extra é mínimo, e
estourar um `INTEGER` (2,1 bi) em produção é um incidente clássico e evitável.

---

## 2. Texto

| Tipo | Comportamento | Recomendação |
|---|---|---|
| `TEXT` | Comprimento ilimitado | **Padrão. Use este.** |
| `VARCHAR(n)` | Limita a `n` caracteres | Só se `n` for regra de negócio real |
| `VARCHAR` (sem n) | Igual a `TEXT` | Redundante |
| `CHAR(n)` | Preenche com espaços até `n` | **Evite** — quase nunca é o que se quer |

> **Mito comum:** "`VARCHAR(50)` é mais rápido/menor que `TEXT`". **Falso** no PostgreSQL: os três
> usam o mesmo armazenamento interno (varlena), e o limite de `VARCHAR(n)` é só uma constraint
> checada na escrita. Use `TEXT` e, se precisar limitar, um `CHECK (length(x) <= 50)` — que é mais
> fácil de alterar depois que um `ALTER TYPE`.

**Collation** (ordenação e comparação): controla como o texto é ordenado e comparado (sensível a
acento? a maiúscula?). Importante para nomes e buscas:
```sql
SELECT nome FROM clientes ORDER BY nome COLLATE "pt-BR-x-icu";
-- Collation não determinística permite igualdade insensível a maiúsculas/acentos
CREATE COLLATION sem_acento (provider = icu, locale = 'pt-BR', deterministic = false);
```

---

## 3. Data e hora — sempre `TIMESTAMPTZ`

| Tipo | O que guarda | Quando |
|---|---|---|
| `DATE` | Só a data | Aniversários, vencimentos |
| `TIME` | Só a hora | Horários recorrentes |
| `TIMESTAMP` | Data + hora, **sem fuso** | **Quase nunca** — você perde a referência |
| `TIMESTAMPTZ` | Data + hora, **com fuso** | **Sempre**, para instantes reais |
| `INTERVAL` | Uma duração | "3 dias", "2 horas" |

> ### A regra: use `TIMESTAMPTZ` para todo instante do mundo real
> `TIMESTAMPTZ` **não guarda** o fuso; ele guarda o instante em UTC e **converte** na entrada e na
> saída conforme o fuso da sessão. Isso significa que "agora" gravado no Brasil e lido no Japão é o
> mesmo instante, corretamente exibido em cada lugar. `TIMESTAMP` (sem tz) guarda "10:00" sem saber
> 10:00 de onde — e quando o servidor, o cliente ou o horário de verão mudam, você tem bugs
> impossíveis de depurar. **`TIMESTAMP` sem tz só serve para "hora de parede" abstrata** (o horário
> de uma farmácia que abre 08:00 em qualquer fuso).

```sql
SELECT now();                                    -- instante atual, com fuso
SELECT now() AT TIME ZONE 'America/Sao_Paulo';   -- convertido para um fuso
SELECT '2026-08-11 10:00'::timestamptz;
SELECT now() - INTERVAL '7 days';
SELECT date_trunc('month', now());               -- primeiro dia do mês
SELECT extract(dow FROM now());                  -- dia da semana (0=domingo)
SELECT age(now(), '1990-01-01');                 -- diferença legível
SELECT generate_series('2026-01-01'::date, '2026-12-01', '1 month');  -- série de datas
```

---

## 4. Booleano e enumerados

```sql
-- Booleano: true / false / NULL
SELECT true, false, null::boolean;
-- Aceita 't','f','yes','no','1','0' na entrada

-- ENUM: conjunto fixo e ordenado de valores
CREATE TYPE status_pedido AS ENUM ('novo', 'pago', 'enviado', 'entregue', 'cancelado');
CREATE TABLE p (status status_pedido NOT NULL DEFAULT 'novo');
-- Ordenação segue a ordem de declaração: 'novo' < 'pago' < ...
```

> **ENUM vs. tabela de referência vs. `CHECK`:** ENUM é compacto e ordenado, mas **adicionar** um
> valor exige `ALTER TYPE` (e remover é difícil). Uma tabela de referência (`status_pedido(id,
> nome)`) é mais flexível (adiciona linha) e permite metadados, ao custo de um JOIN. Um
> `CHECK (status IN (...))` é o meio-termo simples. Escolha por quanto o conjunto muda: fixo →
> ENUM; evolui → tabela.

---

## 5. JSON e JSONB — documentos dentro do relacional

Coberto em [05-manual-de-uso.md, seção 8](05-manual-de-uso.md#8-json-e-jsonb). O essencial:

| | `JSON` | `JSONB` |
|---|---|---|
| Armazenamento | Texto literal | **Binário decomposto** |
| Preserva formatação/ordem/espaços | Sim | Não |
| Velocidade de consulta | Lenta (parse a cada vez) | **Rápida** |
| Indexável (GIN) | Não | **Sim** |
| Recomendação | Só se precisar do texto exato | **Quase sempre** |

```sql
CREATE TABLE t (dados JSONB);
INSERT INTO t VALUES ('{"user":42,"tags":["a","b"]}');
SELECT dados->>'user', dados->'tags'->>0 FROM t;
SELECT * FROM t WHERE dados @> '{"user":42}';         -- "contém", usa índice GIN
CREATE INDEX ON t USING GIN (dados);
CREATE INDEX ON t USING GIN (dados jsonb_path_ops);   -- menor, só para @>
```

> **A tentação a resistir:** JSONB é tão bom que dá vontade de jogar **tudo** nele e virar um
> "banco de documentos". Não faça. O que é sempre consultado, filtrado, ordenado ou tem regra de
> negócio deve ser **coluna de verdade**, com tipo, índice e constraint. JSONB é para o
> **genuinamente variável e semiestruturado**. Um esquema todo em JSONB joga fora as garantias que
> te fizeram escolher o PostgreSQL.

---

## 6. Arrays

O PostgreSQL permite arrays de qualquer tipo numa coluna:

```sql
CREATE TABLE posts (id BIGINT, tags TEXT[]);
INSERT INTO posts VALUES (1, ARRAY['sql','banco']), (2, '{tutorial,sql}');
SELECT * FROM posts WHERE 'sql' = ANY(tags);          -- contém 'sql'?
SELECT * FROM posts WHERE tags @> ARRAY['sql'];       -- contém (indexável por GIN)
SELECT unnest(tags) FROM posts;                        -- expande em linhas
SELECT array_length(tags, 1) FROM posts;
CREATE INDEX ON posts USING GIN (tags);
```

> **Array ou tabela de junção?** Arrays são ótimos para **listas simples, pequenas e sem metadados
> próprios** (tags de um post). Se cada item precisa de atributos (data em que a tag foi aplicada,
> quem aplicou) ou você precisa de FK para outra tabela, use uma **tabela de junção** normal. Array
> é conveniência, não substituto do relacional.

---

## 7. UUID e o `uuidv7()` do PostgreSQL 18

```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";   -- (para gen_random_uuid em versões antigas)
SELECT gen_random_uuid();     -- UUIDv4: aleatório
SELECT uuidv7();              -- PG 18: UUIDv7, ORDENADO POR TEMPO
```

| Chave | Vantagens | Desvantagens |
|---|---|---|
| `BIGINT IDENTITY` | Compacto (8 bytes), rápido, ordenado | Revela volume; ruim em sistemas distribuídos |
| `UUID` v4 (aleatório) | Global, opaco, gerável no cliente | 16 bytes; **aleatoriedade fragmenta o índice** (páginas cheias em toda parte) |
| **`uuidv7()`** (PG 18) | Global, opaco, **ordenado por tempo** | 16 bytes (maior que BIGINT) |

> **Por que `uuidv7` importa:** o problema do UUIDv4 como chave primária é que valores aleatórios
> caem em **posições aleatórias** do índice B-tree, o que espalha as escritas e fragmenta o índice
> (páginas parciais por toda parte, mais I/O, cache pior). O `uuidv7` embute um timestamp no início,
> então valores novos ficam **próximos** no índice, como um sequencial — mantendo a localidade de
> escrita **e** a globalidade/opacidade do UUID. É a razão pela qual muita gente que evitava UUID
> como PK voltou a considerá-lo no PG 18.

---

## 8. Ranges — intervalos como valor de primeira classe

```sql
SELECT '[10,20)'::int4range;                     -- de 10 (inclusive) a 20 (exclusive)
SELECT '[2026-08-01, 2026-09-01)'::daterange;
SELECT '[10,20)'::int4range @> 15;               -- 15 está no intervalo?
SELECT '[10,20)'::int4range && '[15,25)';        -- os intervalos se sobrepõem?
```

Ranges brilham em reservas, períodos de validade, faixas de preço — e habilitam a restrição
`EXCLUDE` que impede sobreposições (ver
[06-exemplos.md, exemplo 9](06-exemplos.md#9-evitar-reserva-em-dobro-com-exclusão)). Tipos:
`int4range`, `int8range`, `numrange`, `tsrange`, `tstzrange`, `daterange`, e *multirange*
(conjuntos de intervalos) desde o PG 14.

---

## 9. Tipos especializados

| Tipo | Para | Extensão |
|---|---|---|
| `INET`, `CIDR`, `MACADDR` | Endereços de rede, com operadores (`<<` "está na sub-rede") | nativo |
| `POINT`, `LINE`, `POLYGON`, `CIRCLE` | Geometria plana | nativo |
| `geometry`, `geography` | GIS de verdade (mapas, distâncias no globo) | **PostGIS** |
| `vector` | Embeddings para IA | **pgvector** |
| `tsvector`, `tsquery` | Busca textual | nativo |
| `bytea` | Dados binários (evite guardar arquivos grandes; prefira storage de objetos) | nativo |
| `bit`, `bit varying` | Máscaras de bits | nativo |
| Tipos compostos | `CREATE TYPE endereco AS (rua TEXT, cep TEXT)` | nativo |
| Domínios | `CREATE DOMAIN email AS TEXT CHECK (VALUE ~ '@')` — um tipo com regra | nativo |

Domínios são subutilizados e ótimos: um `CREATE DOMAIN cpf AS TEXT CHECK (...)` centraliza a regra
de validação num tipo reutilizável.

---

## 10. Conversões (casts) e coerção

```sql
SELECT '42'::integer, 42::text, '2026-01-01'::date;
SELECT CAST('3.14' AS numeric);
SELECT '{"a":1}'::jsonb;
SELECT 'true'::boolean;
```

Cuidado com casts implícitos e com a **precisão perdida** ao converter (`numeric` → `real`). Seja
explícito quando importa.

---

## Autoteste

1. Por que `NUMERIC` e não `float` para dinheiro? Explique a causa em base 2.
2. `VARCHAR(50)` é mais eficiente que `TEXT` no PostgreSQL? Justifique.
3. Por que usar `TIMESTAMPTZ` e não `TIMESTAMP`? O que `TIMESTAMPTZ` realmente guarda?
4. Quando `TIMESTAMP` sem fuso é a escolha certa?
5. `JSON` ou `JSONB`? E quando NÃO usar JSONB, mesmo podendo?
6. Quando um array é melhor que uma tabela de junção, e quando não?
7. Que problema o `uuidv7()` do PG 18 resolve em relação ao UUIDv4 como chave primária?
8. Para que serve um tipo `range`, e que restrição especial ele habilita?
9. ENUM, tabela de referência ou `CHECK`: como você decide?
10. O que é um `DOMAIN` e por que ele é útil?
