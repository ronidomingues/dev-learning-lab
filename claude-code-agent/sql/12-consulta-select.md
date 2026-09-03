# 12 — A consulta: `SELECT` por dentro

Nível: iniciante · Data: 13/08/2026

Se você entender **uma** coisa deste curso com precisão, que seja este arquivo.
A ordem de execução do `SELECT` explica a maior parte dos erros de iniciante e
metade dos problemas de desempenho.

---

## 1. As sete cláusulas

```sql
SELECT   colunas          -- 5º a executar
  FROM   tabelas          -- 1º
  JOIN   ... ON ...       -- 1º (junto com o FROM)
 WHERE   condição         -- 2º
 GROUP   BY colunas       -- 3º
HAVING   condição         -- 4º
 ORDER   BY colunas       -- 6º
 LIMIT   n OFFSET m       -- 7º
```

**A ordem em que se escreve não é a ordem em que roda.** Esta é a ordem
lógica de execução, e é definida pelo padrão:

```
 FROM/JOIN  →  WHERE  →  GROUP BY  →  HAVING  →  SELECT  →  ORDER BY  →  LIMIT
     │           │          │           │          │           │          │
  de onde     quais      como       quais      o que        em que    quantas
   vêm as     linhas    agrupar    grupos     mostrar        ordem     linhas
   linhas
```

*(Funções de janela — `OVER` — rodam entre o `HAVING` e o `SELECT`. É por isso
que você pode usar `OVER` no `SELECT` e no `ORDER BY`, mas não no `WHERE`.)*

---

## 2. As cinco consequências práticas

### 2.1 O apelido não existe no `WHERE`

```sql
SELECT valor * 1.8 + 32 AS temp_F
  FROM leitura
 WHERE temp_F > 350;              -- ERRO: no such column: temp_F
```

Quando o `WHERE` roda, o `SELECT` ainda não aconteceu. O apelido não existe.

**Saídas, em ordem de preferência:**

```sql
-- 1. repetir a expressão (feio, sempre funciona)
WHERE valor * 1.8 + 32 > 350

-- 2. CTE (legível, sem custo — o otimizador reescreve)
WITH conv AS (SELECT valor * 1.8 + 32 AS temp_F FROM leitura)
SELECT * FROM conv WHERE temp_F > 350;

-- 3. simplificar a matemática (melhor de todas)
WHERE valor > (350 - 32) / 1.8   -- e agora o índice em `valor` funciona
```

A terceira é a boa: mover a operação para o **lado da constante** deixa a
coluna limpa, e coluna limpa usa índice. Ver
[21-indices-e-desempenho.md](21-indices-e-desempenho.md).

### 2.2 O apelido **existe** no `ORDER BY`

```sql
SELECT valor * 1.8 + 32 AS temp_F FROM leitura ORDER BY temp_F DESC;   -- ✅
```

Porque o `ORDER BY` roda depois do `SELECT`. Não é inconsistência: é a ordem.

### 2.3 `WHERE` filtra linhas, `HAVING` filtra grupos

```sql
SELECT tag_id, AVG(valor)
  FROM leitura
 WHERE qualidade = 'BOA'          -- descarta LINHAS ruins antes de agrupar
 GROUP BY tag_id
HAVING COUNT(*) > 1000;           -- descarta GRUPOS pequenos depois
```

Trocar os dois de lugar dá erro ou resultado errado. E há uma implicação de
desempenho: **`WHERE` é sempre mais barato**, porque descarta linhas antes de
o banco gastar trabalho agrupando. Se a condição pode ser expressa como
`WHERE`, ela deve ser.

### 2.4 `LIMIT` roda por último

```sql
SELECT * FROM leitura ORDER BY valor DESC LIMIT 10;
```
Isso ordena **as 344 mil linhas** e devolve dez. Não é "pegue dez e ordene".

*(Bons otimizadores fazem "top-N sort" e não ordenam tudo de verdade — mas o
resultado lógico é este, e é o que você deve raciocinar.)*

### 2.5 `SELECT DISTINCT` roda depois de tudo, menos ordem e limite

```sql
SELECT DISTINCT tag_id FROM leitura;    -- precisa varrer/ordenar tudo
```

Se o `DISTINCT` está "consertando" duplicatas que apareceram num `JOIN`, ele
está escondendo um bug de cardinalidade, não resolvendo. Ver
[13-juncoes.md](13-juncoes.md).

---

## 3. `SELECT`: escolher colunas

```sql
SELECT *                               -- todas
SELECT l.*                             -- todas de uma tabela
SELECT tag_id, valor                   -- escolhidas
SELECT valor * 1.8 + 32 AS temp_F      -- calculada, com apelido
SELECT DISTINCT tag_id                 -- valores únicos
SELECT 'constante' AS origem           -- literal
```

### Por que não usar `SELECT *` em produção

1. **Quebra silenciosamente.** Alguém adiciona uma coluna e o seu código
   Python que faz `for tag, ts, valor in cursor` passa a receber quatro
   valores.
2. **Traz dado que você não usa** pela rede e para a memória.
3. **Impede índice de cobertura.** Se sua consulta pede só `(tag_id, ts)` e há
   um índice com essas colunas, o banco responde sem tocar na tabela. Com `*`,
   ele sempre vai à tabela. Medido no projeto-modelo: 17,8 ms → 0,5 ms.

Em exploração interativa, `SELECT *` é ótimo. Em código que roda sozinho, é
dívida.

---

## 4. `FROM`: de onde vêm as linhas

```sql
FROM leitura                            -- tabela
FROM leitura AS l                       -- com apelido
FROM v_batelada                         -- view (uma consulta com nome)
FROM (SELECT ... ) AS x                 -- subconsulta derivada
FROM a JOIN b ON ...                    -- junção
```

**Use apelido curto sempre que houver mais de uma tabela**, e use o apelido em
todas as colunas. `l.valor` e `t.descricao` deixam explícito de onde vem cada
coisa; sem isso, uma coluna com o mesmo nome nos dois lados gera
`ambiguous column name` — ou, pior, pega a errada silenciosamente.

---

## 5. `WHERE`: quais linhas

### Operadores e precedência

`NOT` > `AND` > `OR`. **Parênteses sempre que misturar.**

```sql
-- ERRADO (quase certamente não é o que se quer)
WHERE tag_id = 'TI-101' OR tag_id = 'PI-101' AND valor > 195

-- CERTO
WHERE (tag_id = 'TI-101' OR tag_id = 'PI-101') AND valor > 195

-- MELHOR
WHERE tag_id IN ('TI-101', 'PI-101') AND valor > 195
```

### As comparações que enganam

| Escreva | Não escreva | Por quê |
|---|---|---|
| `valor IS NULL` | `valor = NULL` | Nunca é verdadeiro |
| `ts >= 'A' AND ts < 'B'` | `ts BETWEEN 'A' AND 'B'` | `BETWEEN` é inclusivo nos dois lados; perde a última fração de segundo |
| `NOT EXISTS (...)` | `NOT IN (...)` com possível `NULL` | `NOT IN` devolve zero linhas se houver um `NULL` na lista |
| `ts >= '2026-07-10' AND ts < '2026-07-11'` | `substr(ts,1,10) = '2026-07-10'` | Função na coluna impede índice |
| `valor > 32` | `CAST(valor AS TEXT) LIKE '3%'` | Idem, e está errado (pega 3, 30, 300…) |

### `LIKE`: casamento de padrão

| Padrão | Casa com |
|---|---|
| `'TI-%'` | Qualquer coisa que comece com `TI-` |
| `'%reator%'` | Contém "reator" |
| `'TI-1_1'` | `TI-101`, `TI-111`, `TI-121`… (`_` = **um** caractere) |
| `'100\%' ESCAPE '\'` | Literalmente `100%` |

⚠️ `LIKE '%algo'` (curinga no início) **não usa índice** — o banco precisa
olhar todas as linhas. `LIKE 'algo%'` usa. É a diferença entre 0,1 ms e 18 ms.

⚠️ Sensibilidade a maiúsculas varia: SQLite é insensível para ASCII em `LIKE`
(mas sensível em `=`); PostgreSQL é sensível em `LIKE` e tem `ILIKE` para o
contrário.

---

## 6. `ORDER BY`: em que ordem

```sql
ORDER BY ts                              -- crescente (ASC é o padrão)
ORDER BY valor DESC                      -- decrescente
ORDER BY tag_id, ts DESC                 -- várias chaves
ORDER BY valor DESC NULLS LAST           -- onde ficam os nulos
ORDER BY CASE fase                       -- ordem personalizada
           WHEN 'carga' THEN 1
           WHEN 'aquecimento' THEN 2
           WHEN 'reacao' THEN 3
           ELSE 4 END
```

**Onde ficam os `NULL`?** O padrão deixa em aberto. SQLite e PostgreSQL põem
os nulos **primeiro** em `ASC`; Oracle e SQL Server põem por **último**. Se
importa, escreva `NULLS FIRST` / `NULLS LAST`.

**Ordem de texto**: comparação por *collation*. `'Ácido' < 'Bomba'`? Depende.
Em SQLite com a *collation* padrão (`BINARY`), compara bytes UTF-8 e `'Á'`
vem **depois** de `'Z'`. Em PostgreSQL com locale `pt_BR`, vem no lugar
"certo" do alfabeto. Isso morde em relatório ordenado por nome de equipamento
com acento.

---

## 7. `LIMIT` e paginação

```sql
LIMIT 10                -- as 10 primeiras
LIMIT 10 OFFSET 20      -- da 21ª à 30ª
```

⚠️ **`OFFSET` grande é lento.** `OFFSET 100000` faz o banco produzir e
descartar 100 mil linhas. E é **incorreto** se o dado muda entre as páginas:
uma linha inserida desloca todas as seguintes e você pula um registro.

**Paginação por chave (*keyset pagination*)** — o jeito certo:

```sql
-- primeira página
SELECT * FROM leitura WHERE tag_id='TI-101' ORDER BY ts LIMIT 1000;

-- próxima: use o último ts recebido
SELECT * FROM leitura
 WHERE tag_id='TI-101' AND ts > '2026-07-01 16:39:00'
 ORDER BY ts LIMIT 1000;
```

Custo constante por página, e imune a inserções.

---

## 8. Como o banco realmente executa

O que descrevi é a ordem **lógica** — a semântica. A ordem **física** é
escolhida pelo otimizador, e pode ser bem diferente, desde que o resultado
seja o mesmo.

Exemplo real, do [projeto-modelo](07-projeto-modelo/):

```sql
EXPLAIN QUERY PLAN
SELECT tag_id, AVG(valor) FROM leitura
 WHERE tag_id='TI-101' AND ts>='2026-07-10' AND ts<'2026-07-11'
 GROUP BY tag_id;
```
```
SEARCH leitura USING PRIMARY KEY (tag_id=? AND ts>? AND ts<?)
```

O banco **não** leu 344 mil linhas para depois filtrar: ele foi direto ao
trecho do índice, leu ~1.440 linhas e agregou. Semanticamente é
"leia tudo, depois filtre"; fisicamente é outra coisa. Esse é o valor de uma
linguagem declarativa — e a razão de duas consultas logicamente idênticas
poderem diferir mil vezes em tempo.

**Transformações que o otimizador faz sozinho:**

| Transformação | Exemplo |
|---|---|
| *Predicate pushdown* | Empurra o `WHERE` para dentro de subconsultas e views |
| Reordenar junções | Começa pela tabela que filtra mais |
| Eliminar subconsulta | Reescreve `IN (SELECT ...)` como junção |
| Achatar view | Substitui a view pelo texto dela |
| Escolher índice | Baseado em estatísticas (`ANALYZE`) |

**O que ele *não* faz por você:**

- Consertar função aplicada na coluna (`substr(ts,1,10) = ...`).
- Adivinhar que seu `LEFT JOIN` deveria ser `INNER`.
- Criar o índice que falta.
- Corrigir cardinalidade errada de junção.

---

## 9. Estilo: como escrever consulta que outra pessoa lê

Não é vaidade. Consulta de 60 linhas mal formatada é impossível de revisar, e
consulta que ninguém revisa é consulta com bug.

```sql
-- Rendimento das bateladas do mês, por operador.
-- Fonte: v_batelada. Autor: fulano, 13/08/2026.
SELECT b.operador,
       COUNT(*)                     AS bateladas,
       ROUND(AVG(b.rendimento_pct), 2) AS rendimento_medio,
       ROUND(MIN(b.rendimento_pct), 2) AS pior
  FROM v_batelada AS b
 WHERE b.status = 'CONCLUIDA'
   AND b.ts_inicio >= '2026-07-01 00:00:00'
   AND b.ts_inicio <  '2026-08-01 00:00:00'
 GROUP BY b.operador
HAVING COUNT(*) >= 5
 ORDER BY rendimento_medio DESC;
```

Regras que valem a pena:

1. **Palavra-chave em maiúscula**, nome de coisa em minúscula. Diferencia o
   que é linguagem do que é seu.
2. **Uma coluna por linha** quando são mais de três.
3. **Alinhe à direita as palavras-chave** (o "estilo rio"), ou alinhe à
   esquerda — escolha uma e mantenha.
4. **Apelido de tabela sempre**, e use-o em todas as colunas.
5. **Comentário no topo** com a pergunta que a consulta responde e a data.
6. **Vírgula no fim da linha**, não no início (guerra santa; escolha e mantenha).
7. **Intervalo de data explícito e semiaberto**, sempre.

---

## Autoteste

1. Escreva a ordem lógica de execução das sete cláusulas.
2. Por que `WHERE temp_F > 350` falha se `temp_F` é apelido, mas
   `ORDER BY temp_F` funciona?
3. Dê a **melhor** das três soluções para o problema do apelido no `WHERE`, e
   diga por que é a melhor.
4. Qual a diferença de custo entre `WHERE` e `HAVING` para a mesma condição?
5. Cite três razões para não usar `SELECT *` em código de produção.
6. Por que `LIKE '%reator'` não usa índice e `LIKE 'reator%'` usa?
7. Por que `OFFSET 100000` é lento **e** possivelmente incorreto?
8. Cite três transformações que o otimizador faz e três que ele não faz.
9. `ORDER BY` com acento pode dar ordem diferente em dois bancos. Por quê?

---

*Próximo: [13-juncoes.md](13-juncoes.md) — onde a maioria das pessoas trava.*
