# 14 · Índices — como o banco encontra dados rápido

`Nível: intermediário → avançado` · `Última atualização: 11/08/2026`

Índice é o assunto que mais separa "meu banco está lento" de "meu banco voa". Este arquivo explica
o que é um índice, os tipos, e a arte de escolher.

---

## 1. A intuição: o índice de um livro

Sem índice, achar "MVCC" num livro de 500 páginas significa ler página por página. Com o índice
remissivo no fim, você vai direto: "MVCC ... p. 213". Um índice de banco é exatamente isso — uma
estrutura auxiliar que aponta para onde os dados estão, para o banco não ter que ler a tabela
inteira.

```sql
-- Sem índice: SEQ SCAN — lê a tabela toda
SELECT * FROM pedidos WHERE cliente_id = 42;   -- percorre 10 milhões de linhas

CREATE INDEX ix_pedidos_cliente ON pedidos (cliente_id);

-- Com índice: INDEX SCAN — vai direto às linhas do cliente 42
SELECT * FROM pedidos WHERE cliente_id = 42;   -- lê ~10 linhas
```

**O custo do índice:** ele não é grátis. Cada `INSERT`/`UPDATE`/`DELETE` precisa **atualizar
também o índice**, e ele ocupa disco. Índice acelera leitura e **desacelera escrita**. Por isso a
regra: **indexe o que você consulta, não tudo.**

---

## 2. Como o banco decide usar (ou não) um índice

O planejador **não usa** um índice só porque ele existe. Ele estima o custo e escolhe. Um índice é
ignorado quando:

- **A consulta traz muitas linhas.** Se você vai ler 40% da tabela, ler tudo em sequência (seq
  scan) é mais rápido que pular entre índice e tabela milhares de vezes.
- **A coluna tem baixa cardinalidade** (poucos valores distintos, ex.: um booleano). Indexar
  `ativo` (só true/false) raramente ajuda.
- **As estatísticas estão desatualizadas** e o banco estima errado. `ANALYZE` corrige.
- **A condição não "combina" com o índice** (ex.: `WHERE lower(email)=...` sem índice em
  `lower(email)`).

Verifique com `EXPLAIN` (ver [16-consultas-e-planejador.md](16-consultas-e-planejador.md)):
```sql
EXPLAIN SELECT * FROM pedidos WHERE cliente_id = 42;
-- "Index Scan using ix_pedidos_cliente" → está usando
-- "Seq Scan on pedidos" → não está (falta índice, ou o planejador achou melhor não usar)
```

---

## 3. Os tipos de índice do PostgreSQL

Esta variedade é uma vantagem enorme sobre bancos que só têm B-tree.

### B-tree — o padrão, para 90% dos casos

```sql
CREATE INDEX ix_x ON t (coluna);   -- B-tree implícito
```
Serve para: `=`, `<`, `>`, `<=`, `>=`, `BETWEEN`, `IN`, `ORDER BY`, `LIKE 'prefixo%'` (prefixo
fixo). É o índice de igualdade e de **faixa/ordenação**. Balanceado, eficiente, o que você usa por
padrão.

### GIN — para "contém": JSONB, arrays, busca textual

```sql
CREATE INDEX ON eventos USING GIN (dados);          -- JSONB @>
CREATE INDEX ON posts   USING GIN (tags);           -- array @>
CREATE INDEX ON artigos USING GIN (busca);          -- tsvector @@ (busca textual)
```
GIN (*Generalized Inverted Index*) indexa **os elementos internos** de um valor composto — as
chaves de um JSONB, os itens de um array, as palavras de um texto. É o que torna `@>`, `?` e `@@`
rápidos. Mais lento para atualizar que B-tree.

### GiST — para geometria, ranges, vizinhança

```sql
CREATE INDEX ON reservas USING GIST (periodo);         -- ranges, sobreposição &&
CREATE INDEX ON locais   USING GIST (posicao);         -- geometria, "mais próximo"
```
GiST (*Generalized Search Tree*) suporta "está perto", "se sobrepõe", "contém geometricamente". É a
base da busca geográfica (PostGIS) e das restrições `EXCLUDE`.

### BRIN — para tabelas gigantes e ordenadas

```sql
CREATE INDEX ON metricas USING BRIN (timestamp);
```
BRIN (*Block Range Index*) guarda só o **valor mínimo e máximo por bloco** de disco. É
**minúsculo** (kilobytes para gigabytes de tabela) e brilha quando os dados são naturalmente
ordenados no disco (séries temporais inseridas em ordem). Troca precisão por tamanho: perfeito para
"logs do último mês" numa tabela de bilhões de linhas.

### Hash — só igualdade

```sql
CREATE INDEX ON t USING HASH (coluna);
```
Só serve para `=`. Raramente vence o B-tree (que também faz `=` e muito mais). Use só se medir
vantagem.

### Resumo

| Tipo | Para | Tamanho | Escrita |
|---|---|---|---|
| **B-tree** | `=`, `<`, `>`, ordenação, prefixo | médio | rápida |
| **GIN** | JSONB, arrays, full-text (`@>`, `@@`) | grande | lenta |
| **GiST** | geometria, ranges, "próximo" | médio | média |
| **BRIN** | tabelas enormes e ordenadas | minúsculo | rápida |
| **Hash** | só `=` | médio | rápida |
| **HNSW/IVFFlat** (pgvector) | similaridade de vetores | grande | lenta |

---

## 4. Índices que fazem mais: compostos, parciais, por expressão, covering

### Composto (multicoluna)

```sql
CREATE INDEX ON pedidos (cliente_id, criado_em);
```
Serve para consultas que filtram por `cliente_id`, ou por `cliente_id` **e** `criado_em`. **A ordem
importa:** este índice ajuda `WHERE cliente_id = 1` e `WHERE cliente_id = 1 AND criado_em > x`, mas
**não** `WHERE criado_em > x` sozinho (a coluna líder é `cliente_id`).

> **Novidade do PG 18 — skip scan:** antes, o índice `(status, criado_em)` era inútil para uma
> consulta que filtrava só por `criado_em`. O PG 18 permite ao planejador "pular" pelos valores
> distintos da coluna líder (`status`) e usar o índice mesmo assim, quando a coluna líder tem
> **poucos valores**. Um índice serve mais consultas do que antes.

### Parcial — indexa só um subconjunto

```sql
CREATE INDEX ON pedidos (criado_em) WHERE status = 'pendente';
```
Só indexa as linhas pendentes. Menor, mais rápido, e perfeito quando você quase sempre consulta um
subconjunto (os pendentes, os ativos, os não-deletados). É a técnica por trás da regra "um
empréstimo aberto por exemplar" do projeto-modelo.

### Por expressão — indexa o resultado de uma função

```sql
CREATE INDEX ON clientes (lower(email));
-- agora ISTO usa o índice:
SELECT * FROM clientes WHERE lower(email) = 'ana@x.com';
```
Sem o índice na **expressão**, `WHERE lower(email)=...` faz seq scan, porque o índice em `email`
não conhece `lower(email)`.

### Covering (INCLUDE) — evita ir à tabela

```sql
CREATE INDEX ON pedidos (cliente_id) INCLUDE (valor, status);
-- SELECT valor, status FROM pedidos WHERE cliente_id = 1
-- pode ser respondido SÓ pelo índice (index-only scan), sem ler a tabela
```
Guarda colunas extras no índice para que certas consultas sejam respondidas sem tocar na tabela.

---

## 5. Criar índice em produção sem travar

```sql
-- ❌ Bloqueia ESCRITAS na tabela enquanto constrói (ruim numa tabela grande em produção)
CREATE INDEX ix ON grande (col);

-- ✅ Não bloqueia escritas (mais lento, mas seguro)
CREATE INDEX CONCURRENTLY ix ON grande (col);
```
`CONCURRENTLY` constrói o índice sem travar a tabela. Custa: é mais lento, não pode rodar dentro de
transação, e se falhar deixa um índice inválido (que você dropa e recria). Em produção, **sempre**
`CONCURRENTLY`.

---

## 6. Manutenção e diagnóstico

```sql
-- Índices que NUNCA são usados (candidatos a remover — cada um custa na escrita e no disco)
SELECT schemaname, relname, indexrelname, idx_scan,
       pg_size_pretty(pg_relation_size(indexrelid)) AS tamanho
FROM pg_stat_user_indexes
WHERE idx_scan = 0
ORDER BY pg_relation_size(indexrelid) DESC;

-- Tamanho dos índices de uma tabela
SELECT indexrelname, pg_size_pretty(pg_relation_size(indexrelid))
FROM pg_stat_user_indexes WHERE relname = 'pedidos';

-- Índices duplicados/redundantes (mesmo conjunto de colunas)
-- (o índice em (a) é redundante se já existe um em (a,b) para prefixo)

-- Reconstruir um índice inchado (sem bloquear)
REINDEX INDEX CONCURRENTLY ix_pedidos_cliente;

-- Encontrar tabelas com muitos seq scans (podem precisar de índice)
SELECT relname, seq_scan, idx_scan
FROM pg_stat_user_tables WHERE seq_scan > idx_scan ORDER BY seq_scan DESC;
```

**Índice inchado (*bloat*):** por causa do MVCC (ver [15](15-transacoes-e-mvcc.md)), índices
acumulam entradas mortas com o tempo. `REINDEX CONCURRENTLY` os compacta. O PG moderno reduziu
muito isso (deduplicação de B-tree desde a 13), mas em tabelas muito atualizadas ainda importa.

---

## 7. A arte de escolher índices — heurísticas

1. **Indexe colunas de `WHERE`, `JOIN` e `ORDER BY` frequentes.** Comece pelas que aparecem nas
   consultas lentas.
2. **Chaves estrangeiras raramente têm índice automático** (a PK referenciada tem; a coluna FK
   **não**). Indexe suas colunas FK — sem isso, `JOIN`s e `ON DELETE CASCADE` viram seq scans.
3. **Coluna de baixa cardinalidade sozinha, não vale.** `ativo` (bool) → use índice parcial
   (`WHERE ativo`) em vez de índice na coluna.
4. **Ordem no índice composto:** coluna de igualdade primeiro, faixa/ordenação depois.
   `(cliente_id, criado_em)` para `WHERE cliente_id=? ORDER BY criado_em`.
5. **Índice parcial** quando você quase sempre filtra o mesmo subconjunto.
6. **Índice por expressão** quando você filtra por `func(coluna)`.
7. **Meça, não adivinhe.** `EXPLAIN ANALYZE` antes e depois. `pg_stat_user_indexes` para achar os
   inúteis.
8. **Menos é mais.** Cada índice custa na escrita. Um índice que serve várias consultas é melhor
   que cinco específicos.

> **O anti-padrão nº 1:** indexar tudo "por segurança". Dez índices numa tabela muito escrita
> multiplicam o custo de cada `INSERT` e enchem o disco. Índice é investimento com custo de
> manutenção — invista onde há retorno medido.

---

## 8. Os cinco porquês: por que um índice acelera a busca?

**1. Por que `WHERE cliente_id = 42` é mais rápido com índice?**
Porque sem índice o banco lê todas as linhas (seq scan); com índice B-tree, ele desce uma árvore
ordenada e chega às linhas certas em poucos passos.

**2. Por que a árvore B-tree encontra em poucos passos?**
Porque é balanceada e ordenada: cada nó divide o espaço de busca, então o número de passos cresce
com o **logaritmo** do número de linhas, não linearmente. Um bilhão de linhas → ~30 passos.

**3. Por que logarítmico, e não constante como um hash?**
Porque a B-tree preserva a **ordem**, o que permite não só `=` mas também `<`, `>`, faixas e
ordenação. Um hash daria `=` em tempo constante, mas não faria faixas — e faixas/ordenação são
metade das consultas reais. É um **trade-off de projeto**: a B-tree troca a constância do hash pela
generalidade de suportar ordem.

**4. Por que essa generalidade vale a pena a ponto de a B-tree ser o padrão?**
Porque a maioria das consultas reais precisa de ordem (paginação, "últimos N", faixas de data,
`ORDER BY`), e ter **um** índice que serve igualdade **e** ordem é mais valioso que dois índices
especializados. É uma decisão de engenharia validada por 50 anos de uso.

**5. Por que o banco não indexa tudo automaticamente, então?**
Aqui chega-se a um **trade-off econômico explícito**: cada índice acelera leitura mas **desacelera
escrita** e ocupa disco. Indexar tudo tornaria as escritas proibitivamente lentas. Não existe
"grátis" — só a decisão de onde investir o custo de manutenção. Por isso a escolha de índices é
uma decisão humana, informada por medição, e não um automatismo.

---

## Autoteste

1. Por que um índice acelera a leitura e desacelera a escrita?
2. Cite três razões pelas quais o planejador **ignora** um índice existente.
3. Quando você usaria GIN em vez de B-tree? E BRIN?
4. No índice composto `(cliente_id, criado_em)`, quais consultas ele ajuda e qual não?
5. O que o *skip scan* do PG 18 mudou sobre índices compostos?
6. Para que serve um índice parcial? Dê um exemplo do projeto-modelo.
7. Por que `WHERE lower(email)=...` não usa o índice em `email`, e como corrigir?
8. Por que você deve indexar as colunas de chave estrangeira, se a PK já é indexada?
9. Por que criar índice em produção com `CONCURRENTLY`, e qual é o custo disso?
10. Percorra os cinco porquês de "por que um índice acelera a busca?" até a parada econômica.
