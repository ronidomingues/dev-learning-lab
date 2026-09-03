# 12 · Modelo relacional e SQL a fundo

`Nível: intermediário → avançado` · `Última atualização: 11/08/2026`

SQL você aprende rápido; SQL **bem** feito leva anos. Este arquivo é sobre a diferença: JOINs por
dentro, normalização, a ordem real de execução, e as armadilhas de agregação.

---

## 1. A ordem real de execução de uma consulta

Você **escreve** o SQL numa ordem, mas o banco o **executa** em outra. Entender isso resolve metade
das confusões (como "por que não posso usar o apelido do SELECT no WHERE?").

```
   Você escreve:            O banco executa (conceitualmente):
   SELECT   ...             5. SELECT   (escolhe e calcula as colunas)
   FROM     ...             1. FROM + JOIN   (monta o conjunto de linhas)
   WHERE    ...             2. WHERE    (filtra linhas)
   GROUP BY ...             3. GROUP BY (agrupa)
   HAVING   ...             4. HAVING   (filtra grupos)
   ORDER BY ...             6. ORDER BY (ordena)
   LIMIT    ...             7. LIMIT    (corta)
```

Consequências que confundem todo iniciante:

```sql
-- ❌ ERRO: o apelido 'total' ainda não existe no WHERE (SELECT roda depois)
SELECT valor * 1.1 AS total FROM pedidos WHERE total > 100;

-- ✅ repita a expressão, ou use uma subconsulta/CTE
SELECT valor * 1.1 AS total FROM pedidos WHERE valor * 1.1 > 100;

-- ✅ o apelido JÁ existe no ORDER BY (que roda depois do SELECT)
SELECT valor * 1.1 AS total FROM pedidos ORDER BY total;

-- ❌ ERRO: não pode filtrar agregação no WHERE (agregação acontece no GROUP BY, depois)
SELECT cliente_id FROM pedidos WHERE SUM(valor) > 500 GROUP BY cliente_id;

-- ✅ filtre grupos no HAVING
SELECT cliente_id FROM pedidos GROUP BY cliente_id HAVING SUM(valor) > 500;
```

> **Regra de ouro:** `WHERE` filtra **linhas** (antes de agrupar); `HAVING` filtra **grupos**
> (depois de agregar). Confundir os dois é o erro de agregação nº 1.

---

## 2. JOINs, de verdade

Um JOIN combina linhas de duas tabelas segundo uma condição. Visualize com dois conjuntos:

```
   INNER JOIN         LEFT JOIN          FULL JOIN
   só a interseção    tudo da esquerda   tudo dos dois
      ┌───┐               ┌───┐             ┌───┐
     (│ ∩ │)             (███│ ∩ │)        (███│███│███)
      └───┘               └───┘             └───┘
```

```sql
-- Dados
-- clientes: Ana(1), Bruno(2), Carla(3)   ·   pedidos: p1→Ana, p2→Ana, p3→Bruno

SELECT c.nome, p.id
FROM clientes c INNER JOIN pedidos p ON p.cliente_id = c.id;
-- Ana/p1, Ana/p2, Bruno/p3    (Carla some: não tem pedido)

SELECT c.nome, p.id
FROM clientes c LEFT JOIN pedidos p ON p.cliente_id = c.id;
-- Ana/p1, Ana/p2, Bruno/p3, Carla/NULL    (Carla aparece com pedido nulo)
```

### O erro clássico de LEFT JOIN + WHERE

```sql
-- ❌ Isto vira um INNER JOIN sem querer!
SELECT c.nome, p.id
FROM clientes c LEFT JOIN pedidos p ON p.cliente_id = c.id
WHERE p.status = 'pago';        -- p.status é NULL para a Carla → ela é filtrada fora

-- ✅ Coloque a condição da tabela direita no ON, não no WHERE
SELECT c.nome, p.id
FROM clientes c LEFT JOIN pedidos p ON p.cliente_id = c.id AND p.status = 'pago';
```

Regra: condições sobre a tabela **preservada** (esquerda) vão no `WHERE`; condições sobre a tabela
**opcional** (direita) vão no `ON`, ou você anula o efeito do LEFT JOIN.

### Auto-join (a tabela consigo mesma)

```sql
-- Cada funcionário com o nome do seu chefe (mesma tabela, dois papéis)
SELECT f.nome AS funcionario, chefe.nome AS chefe
FROM funcionarios f
LEFT JOIN funcionarios chefe ON chefe.id = f.chefe_id;
```

### LATERAL (a subconsulta que vê a linha da esquerda)

```sql
-- Os 3 últimos pedidos de CADA cliente (top-N por grupo)
SELECT c.nome, p.id, p.criado_em
FROM clientes c
CROSS JOIN LATERAL (
    SELECT id, criado_em FROM pedidos
    WHERE cliente_id = c.id           -- ← enxerga c.id, o que um JOIN normal não faz
    ORDER BY criado_em DESC LIMIT 3
) p;
```

---

## 3. Normalização — organizar para não se contradizer

Normalização é o processo de estruturar tabelas para **eliminar redundância** e, com ela, a
possibilidade de os dados se contradizerem. A intuição, sem o formalismo assustador:

**O problema (tabela não normalizada):**
```
pedidos_ruim
┌────┬────────────┬──────────────────┬─────────┐
│ id │ cliente    │ email_cliente    │ produto │
├────┼────────────┼──────────────────┼─────────┤
│  1 │ Ana Silva  │ ana@x.com        │ Caderno │
│  2 │ Ana Silva  │ ana@x.com        │ Caneta  │
│  3 │ Ana Silva  │ ana@xis.com  ←ERRO  │ Mochila │
└────┴────────────┴──────────────────┴─────────┘
```
O e-mail da Ana está repetido em cada pedido. Um dia alguém atualiza um e esquece os outros — e
agora a Ana tem dois e-mails. Qual é o certo? O banco não sabe. Isso é uma **anomalia de
atualização**.

**A solução (normalizado):** cada fato mora em **um** lugar.
```
clientes                          pedidos
┌────┬───────────┬───────────┐    ┌────┬────────────┬─────────┐
│ id │ nome      │ email     │    │ id │ cliente_id │ produto │
├────┼───────────┼───────────┤    ├────┼────────────┼─────────┤
│  1 │ Ana Silva │ ana@x.com │    │  1 │     1      │ Caderno │
└────┴───────────┴───────────┘    │  2 │     1      │ Caneta  │
                                  └────┴────────────┴─────────┘
```
O e-mail da Ana existe em **uma** linha. Atualizar é mudar um lugar. Impossível se contradizer.

### As formas normais, em linguagem humana

| Forma | Regra | Em português |
|---|---|---|
| **1FN** | Valores atômicos; sem grupos repetidos | Uma célula, um valor. Nada de "telefone1, telefone2, telefone3" |
| **2FN** | 1FN + cada coluna depende da chave **inteira** | Em chave composta, nenhuma coluna depende de só parte dela |
| **3FN** | 2FN + colunas dependem **só** da chave, não de outras colunas | O e-mail depende do cliente, não do pedido → tabela separada |
| **BCNF** | 3FN mais rigorosa | Casos raros de chaves candidatas sobrepostas |

Para 95% dos casos, **"chegue à 3FN"** é o conselho: cada tabela descreve **uma** coisa, e cada
fato aparece **uma** vez.

### Quando **desnormalizar** de propósito

Normalização é o padrão, mas não é dogma. Você desnormaliza deliberadamente quando:
- **Leitura domina e o JOIN custa caro** — guardar um total pré-calculado, um contador.
- **Relatórios e análise** — tabelas "achatadas" para BI leem mais rápido.
- **JSONB** — encapsular dados genuinamente variáveis que não se consulta relacionalmente.

*Opinião profissional:* **normalize primeiro, desnormalize por evidência.** Desnormalizar cedo,
"por performance", sem medir, cria as anomalias de volta e raramente é o gargalo real. Meça, depois
otimize.

---

## 4. Cardinalidade das relações

Três formas de duas tabelas se relacionarem:

| Relação | Como se modela | Exemplo |
|---|---|---|
| **Um-para-muitos** (1:N) | Chave estrangeira na tabela "muitos" | Um cliente, muitos pedidos → `pedidos.cliente_id` |
| **Um-para-um** (1:1) | FK única, ou mesma PK | Um usuário, um perfil |
| **Muitos-para-muitos** (N:M) | **Tabela de junção** com as duas FKs | Alunos e cursos → `matriculas(aluno_id, curso_id)` |

A tabela de junção é o padrão que todo iniciante precisa internalizar: **N:M sempre vira uma
terceira tabela**. Ver o `livros_autores` do
[projeto-modelo](07-projeto-modelo/README.md).

---

## 5. Subconsultas, CTEs e quando usar cada

```sql
-- Subconsulta escalar (retorna um valor)
SELECT nome, (SELECT count(*) FROM pedidos p WHERE p.cliente_id = c.id) AS qtd
FROM clientes c;

-- Subconsulta em WHERE
SELECT * FROM clientes WHERE id IN (SELECT cliente_id FROM pedidos WHERE valor > 100);

-- EXISTS (frequentemente melhor que IN para "existe algum?")
SELECT * FROM clientes c WHERE EXISTS (SELECT 1 FROM pedidos p WHERE p.cliente_id = c.id);

-- CTE: nomeia etapas, deixa legível
WITH vip AS (
    SELECT cliente_id, SUM(valor) t FROM pedidos GROUP BY cliente_id HAVING SUM(valor) > 500
)
SELECT c.nome, vip.t FROM vip JOIN clientes c ON c.id = vip.cliente_id;
```

**`IN` vs `EXISTS` vs `JOIN`:** os três podem dar o mesmo resultado. `EXISTS` costuma ser o mais
eficiente para "existe pelo menos um" (para no primeiro achado); `JOIN` quando você precisa dos
dados dos dois lados; `IN` para listas pequenas. **Cuidado com `NOT IN` e `NULL`:** se a subconsulta
retorna algum `NULL`, `NOT IN` retorna vazio silenciosamente — use `NOT EXISTS`. É uma das
armadilhas mais insidiosas do SQL.

> **CTE e otimização:** até o PostgreSQL 11, CTEs eram uma "barreira de otimização" (materializadas
> sempre). Desde a 12, o planejador pode "inline" a CTE, como faria com uma subconsulta — a menos
> que você force `MATERIALIZED`. Bom saber ao ler conselhos antigos que dizem "CTE é lenta".

---

## 6. Agregação sem armadilhas

```sql
SELECT
    cliente_id,
    count(*)                              AS qtd_pedidos,
    count(desconto)                       AS com_desconto,   -- IGNORA NULLs
    sum(valor)                            AS total,
    avg(valor)                            AS media,
    sum(valor) FILTER (WHERE status='pago') AS pago,         -- agrega um subconjunto
    array_agg(id ORDER BY criado_em)      AS ids,            -- junta em array
    string_agg(descricao, ', ')           AS descricoes,     -- junta em texto
    percentile_cont(0.5) WITHIN GROUP (ORDER BY valor) AS mediana
FROM pedidos
GROUP BY cliente_id;
```

Armadilhas:
- **`count(*)` conta linhas; `count(coluna)` ignora NULLs.** Números diferentes, propósitos
  diferentes.
- **Toda coluna do `SELECT` não-agregada precisa estar no `GROUP BY`** (ou ser funcionalmente
  dependente da PK, o que o Postgres permite).
- **`avg`, `sum` ignoram NULLs**, mas `avg` sobre zero linhas é `NULL`, não `0` — use `COALESCE`.

`GROUPING SETS`, `ROLLUP`, `CUBE` geram subtotais em uma consulta (ver
[06-exemplos.md](06-exemplos.md#3-relatório-de-vendas-com-group-by)).

---

## 7. Boas práticas de modelagem, condensadas

1. **Toda tabela tem chave primária.** Sem exceção defensável.
2. **Prefira chave substituta** (`IDENTITY`/`uuidv7`) a chave natural.
3. **Nomeie consistente:** `snake_case`, tabelas no plural (`clientes`), FKs como
   `<tabela_singular>_id` (`cliente_id`). Escolha uma convenção e não a quebre.
4. **`NOT NULL` por padrão;** permita `NULL` só quando "ausente" for um estado real.
5. **Restrinja no banco:** `CHECK`, `UNIQUE`, `FK`. Regra no banco = regra que não se esquece.
6. **`TIMESTAMPTZ`, não `TIMESTAMP`,** para instantes.
7. **`TEXT`, não `VARCHAR(n)`,** salvo se o limite for regra de negócio real.
8. **`NUMERIC` para dinheiro.** Nunca `float`.
9. **Chegue à 3FN; desnormalize só por evidência medida.**
10. **N:M sempre vira tabela de junção.**

---

## 8. Os cinco porquês: por que SQL, e não uma API de "buscar/salvar"?

**1. Por que consultamos dados com uma linguagem declarativa (SQL) e não com métodos como
`buscarPedidosDoCliente(id)`?**
Porque as perguntas que se quer fazer aos dados são **imprevisíveis e infinitas**. Nenhum conjunto
de métodos pré-escritos cobre "faturamento por mês por região dos clientes que compraram X mas não
Y".

**2. Por que não dá para prever as perguntas?**
Porque o valor dos dados está justamente em cruzá-los de formas novas, conforme o negócio muda. Uma
API fixa engessa isso: cada pergunta nova vira um pedido de desenvolvimento.

**3. Por que uma linguagem declarativa resolve isso melhor que uma procedural?**
Porque separando **o quê** (a pergunta) do **como** (a execução), qualquer pergunta expressável em
lógica de conjuntos pode ser feita **sem** programar o algoritmo de busca — e o banco escolhe o
algoritmo eficiente sozinho.

**4. Por que o banco consegue escolher o algoritmo melhor que o programador?**
Porque ele conhece o que o programador não conhece em tempo de escrita: o tamanho atual das
tabelas, a distribuição dos valores, quais índices existem, quanta memória há. O otimizador decide
com dados que só existem em tempo de execução.

**5. Por que essa abordagem venceu a alternativa (navegação manual dos bancos pré-relacionais)?**
Aqui chegamos à mesma parada de [10-fundamentos.md](10-fundamentos.md): um **trade-off econômico**.
SQL é, às vezes, menos eficiente que um algoritmo escrito à mão para um caso específico — mas é
dramaticamente mais barato em tempo humano, e adapta-se a perguntas novas sem reprogramação. Quando
o tempo de gente ficou mais caro que o de máquina, o declarativo venceu. É a mesma razão pela qual
usamos linguagens de alto nível em vez de assembly.

---

## Autoteste

1. Por que você não pode usar um apelido do `SELECT` no `WHERE`, mas pode no `ORDER BY`?
2. Qual é a diferença entre `WHERE` e `HAVING`?
3. Mostre como um `LEFT JOIN` vira um `INNER JOIN` por acidente, e como evitar.
4. Explique a anomalia de atualização que a normalização elimina, com um exemplo.
5. O que é a 3FN em linguagem humana, e por que "chegue à 3FN" é bom conselho?
6. Quando desnormalizar de propósito? Dê dois casos.
7. Como se modela uma relação muitos-para-muitos?
8. Por que `NOT IN` com uma subconsulta que contém `NULL` é perigoso, e o que usar?
9. Qual é a diferença entre `count(*)` e `count(coluna)`?
10. Percorra os cinco porquês de "por que SQL declarativo?" até a parada econômica.
