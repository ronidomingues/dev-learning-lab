# 05 — Manual de uso: referência consultável

Nível: iniciante → avançado · Data: 13/08/2026

Referência organizada **por tarefa**, não por ordem alfabética. A pergunta é
sempre "eu quero fazer X, como se escreve?".

Sintaxe base: **SQL padrão (ISO/IEC 9075)**, com anotação de dialeto quando
diverge. Exemplos testados em **SQLite 3.37.2**. Diferenças completas entre
bancos: [23-dialetos.md](23-dialetos.md).

**Convenção:** `MAIÚSCULA` = palavra-chave do SQL; `minúscula` = nome seu;
`[colchetes]` = opcional; `a | b` = escolha.

---

## Índice rápido

| Quero… | Seção |
|---|---|
| Ver o que existe no banco | [1](#1-descobrir-o-que-ha-no-banco) |
| Escolher linhas e colunas | [2](#2-selecionar-select) |
| Filtrar | [3](#3-filtrar-where) |
| Ordenar e limitar | [4](#4-ordenar-e-limitar) |
| Cruzar tabelas | [5](#5-juntar-tabelas-join) |
| Resumir e agrupar | [6](#6-agregar-e-agrupar) |
| Cálculo sobre linhas vizinhas | [7](#7-funcoes-de-janela-over) |
| Consulta dentro de consulta | [8](#8-subconsultas-e-ctes) |
| Trabalhar com texto | [9](#9-texto) |
| Trabalhar com número | [10](#10-numeros) |
| Trabalhar com data e hora | [11](#11-data-e-hora) |
| Condicional (`SE… ENTÃO`) | [12](#12-condicionais) |
| Lidar com `NULL` | [13](#13-null) |
| Criar/alterar tabela | [14](#14-criar-e-alterar-ddl) |
| Inserir/atualizar/apagar | [15](#15-inserir-atualizar-apagar-dml) |
| Transação | [16](#16-transacoes) |
| Índice e desempenho | [17](#17-indices-e-plano) |
| Comandos do cliente `sqlite3` | [18](#18-comandos-do-cliente-sqlite3) |
| O que está obsoleto | [19](#19-obsoleto-e-o-que-usar-no-lugar) |

---

## 1. Descobrir o que há no banco

| Objetivo | SQLite | PostgreSQL | Padrão ISO |
|---|---|---|---|
| Listar tabelas | `.tables` ou `SELECT name FROM sqlite_master WHERE type='table'` | `\dt` | `SELECT table_name FROM information_schema.tables` |
| Ver colunas | `PRAGMA table_info(t)` | `\d t` | `SELECT * FROM information_schema.columns WHERE table_name='t'` |
| Ver o DDL original | `SELECT sql FROM sqlite_master WHERE name='t'` | `\d+ t` | — |
| Listar índices | `PRAGMA index_list(t)` | `\di` | — |
| Contar linhas | `SELECT COUNT(*) FROM t` | idem | idem |
| Espiar o conteúdo | `SELECT * FROM t LIMIT 10` | idem | idem |

**Sempre faça isto antes de escrever qualquer consulta:**

```sql
SELECT * FROM leitura LIMIT 10;      -- como o dado se parece?
SELECT COUNT(*) FROM leitura;        -- qual o tamanho?
```

O segundo evita que você rode uma consulta pesada por engano sobre 400 milhões
de linhas.

---

## 2. Selecionar (`SELECT`)

```sql
SELECT [DISTINCT] coluna1, coluna2 AS apelido, expressão
  FROM tabela;
```

| Forma | O que faz | Observação |
|---|---|---|
| `SELECT *` | Todas as colunas | Cômodo para explorar; **evite em produção** — quebra quando a tabela ganha coluna |
| `SELECT t.*` | Todas de uma tabela específica | Útil em `JOIN` |
| `SELECT DISTINCT a` | Valores únicos | Ordena/agrupa por baixo; custa |
| `SELECT a AS "Temperatura (°C)"` | Renomeia a coluna de saída | Aspas **duplas** para nome com espaço |
| `SELECT 1` | Constante | Idiomático em `EXISTS` |
| `SELECT a * 1.8 + 32` | Expressão calculada | °C → °F |

**`AS` é opcional** (`SELECT a media` funciona), mas escreva sempre. Sem ele,
uma vírgula esquecida vira apelido silencioso: `SELECT a b, c` devolve duas
colunas onde você queria três.

---

## 3. Filtrar (`WHERE`)

### Operadores

| Operador | Significado | Exemplo |
|---|---|---|
| `= <> != < <= > >=` | Comparação | `valor > 195` |
| `AND OR NOT` | Lógica | `tag_id='TI-101' AND valor > 195` |
| `BETWEEN a AND b` | Faixa **inclusiva nos dois lados** | `valor BETWEEN 175 AND 185` |
| `IN (a, b, c)` | Pertence à lista | `tag_id IN ('TI-101','PI-101')` |
| `NOT IN` | Não pertence | ⚠️ **quebra com `NULL` na lista** — ver [13](#13-null) |
| `LIKE 'TI-%'` | Padrão de texto: `%`=qualquer sequência, `_`=um caractere | `descricao LIKE '%reator%'` |
| `IS NULL` / `IS NOT NULL` | Ausência de valor | única forma correta |
| `EXISTS (subconsulta)` | Existe pelo menos uma linha | ver [8](#8-subconsultas-e-ctes) |

### Precedência

`NOT` > `AND` > `OR`. Isto é errado com frequência:

```sql
WHERE tag_id = 'TI-101' OR tag_id = 'PI-101' AND valor > 195
-- lê-se: TI-101  OU  (PI-101 E valor>195)     ← quase nunca é o que se quer
```
```sql
WHERE (tag_id = 'TI-101' OR tag_id = 'PI-101') AND valor > 195   -- correto
```

**Use parênteses sempre que misturar `AND` e `OR`.** Não é falta de
conhecimento; é higiene.

### Armadilhas de `WHERE` que valem decorar

| Escreva | Não escreva | Por quê |
|---|---|---|
| `ts >= '2026-07-01' AND ts < '2026-08-01'` | `BETWEEN '2026-07-01' AND '2026-07-31'` | `BETWEEN` perde o dia 31 depois das 00:00:00 |
| `valor IS NULL` | `valor = NULL` | Sempre desconhecido, nunca verdadeiro |
| `ts >= '2026-07-10' AND ts < '2026-07-11'` | `substr(ts,1,10) = '2026-07-10'` | Função na coluna impede o índice: 50× mais lento ([medido](07-projeto-modelo/README.md)) |
| `valor > 195` | `CAST(valor AS TEXT) LIKE '19%'` | Idem, e ainda está errado |

---

## 4. Ordenar e limitar

```sql
SELECT ... ORDER BY coluna [ASC|DESC] [NULLS FIRST|LAST], coluna2 ...
 LIMIT n [OFFSET m];
```

| Recurso | Nota |
|---|---|
| `ORDER BY 2` | Ordena pela 2ª coluna do `SELECT`. Funciona, mas quebra quando alguém mexe no `SELECT`. Evite |
| `ORDER BY apelido` | **Funciona** (o `ORDER BY` roda depois do `SELECT`) |
| `NULLS LAST` | Padrão ISO. PostgreSQL e Oracle têm; **SQLite tem desde 3.30**; MySQL não |
| `LIMIT n OFFSET m` | SQLite, PostgreSQL, MySQL, DuckDB |
| `OFFSET m ROWS FETCH NEXT n ROWS ONLY` | Sintaxe **padrão ISO**; SQL Server, Oracle 12c+, PostgreSQL |
| `TOP n` | Só SQL Server: `SELECT TOP 10 * FROM t` |

⚠️ **Sem `ORDER BY`, a ordem das linhas não é garantida** — nem quando parece
estável. O banco pode mudar o plano e a ordem muda junto. Se a ordem importa,
escreva `ORDER BY`.

⚠️ `OFFSET` grande é lento: o banco lê e descarta as `m` primeiras linhas.
Para paginar dado grande, use paginação por chave
(`WHERE ts > :ultimo_ts ORDER BY ts LIMIT 100`).

---

## 5. Juntar tabelas (`JOIN`)

```sql
SELECT ...
  FROM a
  JOIN b ON b.chave = a.chave;
```

| Tipo | Devolve | Uso típico em planta |
|---|---|---|
| `[INNER] JOIN` | Só o que casa dos dois lados | Leitura × cadastro do tag |
| `LEFT [OUTER] JOIN` | Tudo da esquerda; `NULL` onde não casa | Bateladas × análises de lab (nem toda batelada tem laudo) |
| `RIGHT JOIN` | Espelho do `LEFT` | Raro; ⚠️ **SQLite só desde 3.39** |
| `FULL [OUTER] JOIN` | Tudo dos dois lados | Conciliar duas fontes; ⚠️ SQLite só desde 3.39 |
| `CROSS JOIN` | Produto cartesiano (n × m) | Gerar combinações; anexar um escalar a todas as linhas |
| `NATURAL JOIN` | Junta por colunas de mesmo nome | ⚠️ **Não use.** Quebra sozinho quando alguém adiciona coluna |
| `SELF JOIN` | Tabela com ela mesma | Comparar linha com a anterior (mas prefira `LAG` — ver [7](#7-funcoes-de-janela-over)) |

### Formas de escrever a condição

```sql
JOIN b ON b.tag_id = a.tag_id             -- explícita: sempre funciona
JOIN b USING (tag_id)                     -- quando a coluna tem o mesmo nome
JOIN b ON b.ts >= a.inicio AND b.ts < a.fim   -- theta-join: junção por intervalo
```

`ON ... >= ... <` é a **junção temporal**, a mais importante para dado de
processo: ligar uma leitura à batelada que estava rodando naquele instante.
Ver [13-juncoes.md](13-juncoes.md) e a view `v_leitura_batelada` do
[projeto-modelo](07-projeto-modelo/sql/002-views.sql).

### Diagnóstico rápido de `JOIN`

```sql
SELECT COUNT(*) FROM a;                          -- antes
SELECT COUNT(*) FROM a JOIN b ON ...;            -- depois
```

| Depois | Diagnóstico |
|---|---|
| **Igual** | Relação 1:1 — provavelmente correto |
| **Menor** | `INNER JOIN` descartou linhas sem par. Era isso que você queria? Se não, use `LEFT JOIN` |
| **Maior** | O lado direito tem duplicatas na chave. Suas somas vão estar **infladas** |

---

## 6. Agregar e agrupar

| Função | Faz | `NULL`? |
|---|---|---|
| `COUNT(*)` | Conta **linhas** | Conta todas |
| `COUNT(col)` | Conta valores não nulos | **Ignora `NULL`** |
| `COUNT(DISTINCT col)` | Valores distintos não nulos | Ignora |
| `SUM`, `AVG` | Soma, média | Ignoram `NULL` |
| `MIN`, `MAX` | Extremos | Ignoram `NULL` |
| `GROUP_CONCAT(col, ',')` | Concatena (SQLite/MySQL) | `STRING_AGG` em Postgres/SQL Server; `LISTAGG` em Oracle |
| `stddev_samp`, `var_samp` | Desvio, variância | ⚠️ **Não existem no SQLite** — ver [14-agregacao](14-agregacao-e-grupos.md) |
| `corr(y,x)` | Correlação de Pearson | PostgreSQL e DuckDB; não SQLite |
| `percentile_cont(0.5)` | Mediana | PostgreSQL, Oracle, DuckDB; não SQLite |

```sql
SELECT tag_id, COUNT(*) AS n, AVG(valor) AS media
  FROM leitura
 WHERE qualidade = 'BOA'          -- filtra LINHAS, antes do agrupamento
 GROUP BY tag_id
HAVING COUNT(*) > 100             -- filtra GRUPOS, depois do agrupamento
 ORDER BY media DESC;
```

### Agregação condicional

Duas formas de "contar só os que satisfazem X":

```sql
COUNT(*) FILTER (WHERE valor > 195)                  -- padrão ISO, mais legível
SUM(CASE WHEN valor > 195 THEN 1 ELSE 0 END)         -- funciona em todo lugar
```

`FILTER` existe em **SQLite ≥ 3.30, PostgreSQL, DuckDB**. **Não existe** em
Oracle, SQL Server nem MySQL — lá use `CASE`.

### `GROUP BY` estendido

| Sintaxe | Faz | Onde |
|---|---|---|
| `GROUP BY ROLLUP(a, b)` | Subtotais hierárquicos + total geral | PostgreSQL, Oracle, SQL Server, DuckDB. ⚠️ Não no SQLite |
| `GROUP BY CUBE(a, b)` | Todas as combinações | Idem |
| `GROUPING SETS ((a),(b),())` | Conjuntos escolhidos a dedo | Idem |

---

## 7. Funções de janela (`OVER`)

O recurso mais importante do SQL analítico. Calcula sobre linhas vizinhas
**sem colapsar** as linhas.

```sql
funcao() OVER (
    [PARTITION BY col]        -- refaz o cálculo por grupo
    [ORDER BY col]            -- define a ordem dentro da janela
    [ROWS|RANGE BETWEEN ...]  -- define a moldura (frame)
)
```

| Função | Devolve |
|---|---|
| `ROW_NUMBER()` | 1, 2, 3… sem empate |
| `RANK()` | 1, 2, 2, 4 — empate consome posição |
| `DENSE_RANK()` | 1, 2, 2, 3 — empate não consome |
| `NTILE(4)` | Quartil (1 a 4) |
| `LAG(col, n, padrão)` | Valor de `n` linhas atrás |
| `LEAD(col, n, padrão)` | Valor de `n` linhas à frente |
| `FIRST_VALUE` / `LAST_VALUE` | Primeiro/último da moldura |
| `NTH_VALUE(col, n)` | n-ésimo da moldura |
| `SUM/AVG/MIN/MAX(col) OVER (...)` | Agregação móvel ou acumulada |
| `PERCENT_RANK()`, `CUME_DIST()` | Posição relativa |

### Molduras (o que mais se erra)

| Cláusula | Janela |
|---|---|
| *(sem `ORDER BY`)* | **Toda a partição** — use para "total geral em cada linha" |
| `ORDER BY x` (sem `ROWS`) | `RANGE UNBOUNDED PRECEDING` → **acumulado**, não móvel |
| `ROWS BETWEEN 4 PRECEDING AND CURRENT ROW` | Média móvel de 5, causal (só o passado) |
| `ROWS BETWEEN 2 PRECEDING AND 2 FOLLOWING` | Média móvel centrada (usa o futuro) |
| `ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW` | Acumulado explícito |

**A pegadinha:** `AVG(x) OVER (ORDER BY ts)` **não** é média móvel — é média
acumulada. Sem a cláusula `ROWS`, o padrão é `RANGE UNBOUNDED PRECEDING AND
CURRENT ROW`. Isto derruba muita gente boa.

**Nomear a janela** evita repetir:

```sql
SELECT ts,
       LAG(valor) OVER j  AS anterior,
       LEAD(valor) OVER j AS proximo
  FROM leitura
WINDOW j AS (PARTITION BY tag_id ORDER BY ts);
```
`WINDOW` existe em SQLite ≥ 3.28, PostgreSQL, DuckDB, Oracle, MySQL 8.

Detalhe em [16-funcoes-de-janela.md](16-funcoes-de-janela.md).

---

## 8. Subconsultas e CTEs

| Forma | Onde aparece | Exemplo |
|---|---|---|
| **Escalar** | Onde caberia um valor | `WHERE valor > (SELECT AVG(valor) FROM leitura)` |
| **Lista** | `IN` / `NOT IN` | `WHERE tag_id IN (SELECT tag_id FROM tag WHERE grandeza='temperatura')` |
| **Correlacionada** | Referencia a consulta externa | `WHERE EXISTS (SELECT 1 FROM lab l WHERE l.batelada_id = b.batelada_id)` |
| **Derivada** | No `FROM` | `FROM (SELECT ...) AS x` |
| **CTE** | Antes da consulta, com `WITH` | ver abaixo |

### CTE — *Common Table Expression*

```sql
WITH bom AS (
    SELECT * FROM leitura WHERE qualidade = 'BOA'
),
media AS (
    SELECT tag_id, AVG(valor) AS m FROM bom GROUP BY tag_id
)
SELECT * FROM media WHERE m > 100;
```

Por que usar CTE em vez de subconsulta aninhada: **legibilidade**. Uma consulta
com quatro níveis de aninhamento é ilegível; a mesma coisa com quatro CTEs
nomeadas lê-se de cima para baixo, como um procedimento.

**CTE recursiva** — hierarquias, séries geradas, explosão de estrutura:

```sql
WITH RECURSIVE serie(n) AS (
    SELECT 1                          -- caso base
    UNION ALL
    SELECT n + 1 FROM serie WHERE n < 10   -- passo
)
SELECT n FROM serie;
```

Uso típico em planta: gerar todos os instantes de um intervalo para descobrir
os que **faltam** no historiador. Ver [18-series-temporais.md](18-series-temporais.md).

⚠️ **Toda CTE recursiva precisa de condição de parada.** Sem ela, o banco roda
até estourar a memória.

### `UNION`, `INTERSECT`, `EXCEPT`

| Operador | Faz | Nota |
|---|---|---|
| `UNION` | Une e **remove duplicatas** | Custa uma ordenação |
| `UNION ALL` | Une sem remover | **Mais rápido**; use quando não há duplicata |
| `INTERSECT` | Só o que está nos dois | |
| `EXCEPT` | O que está no primeiro e não no segundo | `MINUS` no Oracle |

As colunas precisam ser **em mesmo número e tipos compatíveis**, na mesma ordem.

---

## 9. Texto

| Função | Faz | Dialeto |
|---|---|---|
| `a \|\| b` | Concatena | Padrão ISO. SQL Server usa `+`; MySQL exige `CONCAT()` |
| `LENGTH(s)` | Comprimento | `LEN()` no SQL Server |
| `UPPER` / `LOWER` | Caixa | ⚠️ SQLite só converte ASCII — `UPPER('ação')` = `'AÇãO'` |
| `TRIM` / `LTRIM` / `RTRIM` | Remove espaços | |
| `SUBSTR(s, ini, n)` | Recorte (base 1) | `SUBSTRING` no padrão |
| `REPLACE(s, de, para)` | Substitui | |
| `INSTR(s, sub)` | Posição, 0 se não achou | `POSITION`/`STRPOS`/`CHARINDEX` |
| `LIKE` | Padrão simples | Sensível a maiúsculas varia por banco |
| `REGEXP` | Expressão regular | ⚠️ SQLite **não tem** por padrão. Postgres: `~`. MySQL: `REGEXP` |
| `printf('%.2f', x)` | Formata | `FORMAT` / `TO_CHAR` em outros |

**Armadilha de acentuação:** `LIKE '%acao%'` não acha "ação". O SQLite não
normaliza acento sem a extensão ICU; o PostgreSQL resolve com `unaccent`.
Para tag de planta (ASCII puro), nunca é problema; para descrição em
português, é.

---

## 10. Números

| Função | Faz | Nota |
|---|---|---|
| `ABS`, `ROUND(x, n)`, `CEIL`, `FLOOR` | Básicas | `CEILING` em alguns |
| `sqrt`, `exp`, `ln`, `log(b,x)`, `pow(x,y)` | Matemáticas | SQLite exige compilação com `SQLITE_ENABLE_MATH_FUNCTIONS` (padrão desde 3.35) |
| `MOD(a,b)` ou `a % b` | Resto | |
| `CAST(x AS REAL)` | Converte tipo | |
| `MIN(a,b)` / `MAX(a,b)` | Escalar, dois argumentos | ⚠️ No SQLite a **mesma palavra** é agregação com 1 argumento e escalar com 2. Em Postgres é `LEAST`/`GREATEST` |

### As três armadilhas numéricas

```sql
SELECT 7 / 2;          --  3     divisão inteira!
SELECT 7.0 / 2;        --  3.5   correto
SELECT 100.0 * a / b;  --  força ponto flutuante desde o início
```

```sql
SELECT 0.1 + 0.2 = 0.3;   --  0 (falso!) em ponto flutuante binário
SELECT ROUND(0.1 + 0.2, 10) = ROUND(0.3, 10);   -- 1 (verdadeiro)
```

```sql
SELECT a / b FROM t;             -- explode ou dá NULL se b = 0
SELECT a / NULLIF(b, 0) FROM t;  -- devolve NULL em vez de erro
```

**Nunca use ponto flutuante para dinheiro.** Use inteiro em centavos, ou
`NUMERIC/DECIMAL` onde existir. Para variável de processo, `REAL` está certo —
o sensor tem 0,1% de incerteza, e 15 dígitos significativos são de sobra. Ver
[17-tipos-e-nulos.md](17-tipos-e-nulos.md).

---

## 11. Data e hora

Esta é a área de **maior divergência entre bancos** de todo o SQL.

### SQLite (não tem tipo de data; usa TEXT, REAL ou INTEGER)

| Expressão | Devolve |
|---|---|
| `date('now')` | `2026-08-13` |
| `datetime('now')` | `2026-08-13 16:04:00` (**UTC**) |
| `datetime('now','localtime')` | hora local |
| `strftime('%Y-%m-%d %H:%M:%S', ts)` | formatação livre |
| `strftime('%Y-%m', ts)` | mês, bom para `GROUP BY` |
| `strftime('%s', ts)` | segundos desde 1970 |
| `date(ts, '+1 day')` | aritmética |
| `julianday(a) - julianday(b)` | **diferença em dias** (fracionários) |
| `unixepoch(ts)` | ⚠️ só SQLite ≥ 3.38 |

**Idioma essencial no SQLite:** diferença em minutos =
`(julianday(a) - julianday(b)) * 1440`. Em horas, `* 24`. Em segundos, `* 86400`.

### Tradução entre dialetos

| Tarefa | SQLite | PostgreSQL | Oracle | SQL Server |
|---|---|---|---|---|
| Agora | `datetime('now')` | `now()` | `SYSTIMESTAMP` | `SYSDATETIME()` |
| Truncar na hora | `substr(ts,1,13)\|\|':00:00'` | `date_trunc('hour', ts)` | `TRUNC(ts,'HH')` | `DATETRUNC(hour, ts)` |
| Somar 1 dia | `date(ts,'+1 day')` | `ts + INTERVAL '1 day'` | `ts + 1` | `DATEADD(day,1,ts)` |
| Diferença em min | `(julianday(a)-julianday(b))*1440` | `EXTRACT(EPOCH FROM a-b)/60` | `(a-b)*1440` | `DATEDIFF(minute,b,a)` |
| Extrair ano | `strftime('%Y',ts)` | `EXTRACT(YEAR FROM ts)` | idem | `YEAR(ts)` |
| Bucket de 15 min | aritmética manual | `date_bin('15 min', ts, '2000-01-01')` | `TRUNC` + aritmética | `DATE_BUCKET` (2022+) |

**DuckDB tem `time_bucket(INTERVAL '1 hour', ts)`**, que é o mais direto de
todos para dado de sensor.

### As regras de ouro de tempo

1. **Guarde em UTC.** Converta só na exibição. Horário de verão cria uma hora
   que acontece duas vezes e outra que não existe; se o dado de planta for
   local, uma dessas horas corrompe o balanço todo ano.
2. **Formato ISO-8601** (`YYYY-MM-DD HH:MM:SS`) sempre — a ordem alfabética
   coincide com a cronológica.
3. **Intervalo semiaberto** `[início, fim)`, nunca `BETWEEN` com `23:59:59`.
4. **Nunca aplique função na coluna do `WHERE`** se quer usar índice.

---

## 12. Condicionais

```sql
CASE WHEN condição THEN valor
     WHEN condição THEN valor
     ELSE valor
END
```

```sql
CASE coluna WHEN 'A' THEN 1 WHEN 'B' THEN 2 ELSE 0 END   -- forma abreviada
```

| Função | Faz | Dialeto |
|---|---|---|
| `COALESCE(a, b, c)` | Primeiro não nulo | **Padrão, use esta** |
| `IFNULL(a, b)` | Dois argumentos | SQLite, MySQL |
| `NVL(a, b)` | Idem | Oracle |
| `ISNULL(a, b)` | Idem | SQL Server (⚠️ no MySQL `ISNULL` é outra coisa) |
| `NULLIF(a, b)` | `NULL` se `a = b` | Padrão. O idioma de divisão segura |
| `IIF(c, a, b)` | Ternário | SQLite ≥ 3.32, SQL Server |

**Sem `ELSE`, o `CASE` devolve `NULL`** quando nada casa. Isso é fonte
silenciosa de erro em soma: escreva o `ELSE`.

---

## 13. `NULL`

`NULL` não é zero, não é string vazia, não é falso. É **"desconhecido"**.

| Expressão | Resultado |
|---|---|
| `NULL = NULL` | `NULL` (não é verdadeiro!) |
| `NULL <> NULL` | `NULL` |
| `NULL + 1` | `NULL` |
| `NULL AND FALSE` | `FALSE` |
| `NULL AND TRUE` | `NULL` |
| `NULL OR TRUE` | `TRUE` |
| `COUNT(*)` | conta a linha |
| `COUNT(col)` | **não** conta |
| `SUM`/`AVG` | ignoram |
| `'a' \|\| NULL` | `NULL` (o texto inteiro some!) |

**A armadilha do `NOT IN`:**

```sql
SELECT * FROM t WHERE x NOT IN (1, 2, NULL);   -- SEMPRE zero linhas
```
Porque `x <> NULL` é desconhecido, e a conjunção nunca é verdadeira. Use
`NOT EXISTS`, que não tem esse problema.

**Comparação segura para `NULL`:**

| Sintaxe | Onde |
|---|---|
| `a IS NOT DISTINCT FROM b` | **Padrão ISO**; PostgreSQL, DuckDB |
| `a IS b` | SQLite |
| `a <=> b` | MySQL |

---

## 14. Criar e alterar (DDL)

```sql
CREATE TABLE leitura (
    tag_id    TEXT    NOT NULL REFERENCES tag(tag_id),
    ts        TEXT    NOT NULL,
    valor     REAL    CHECK (valor BETWEEN -273.15 AND 10000),
    qualidade TEXT    NOT NULL DEFAULT 'BOA'
                      CHECK (qualidade IN ('BOA','DUVIDOSA','RUIM')),
    PRIMARY KEY (tag_id, ts)
) STRICT;                      -- SQLite ≥ 3.37: tipagem de verdade
```

| Restrição | Garante |
|---|---|
| `PRIMARY KEY` | Único e não nulo; identifica a linha |
| `UNIQUE` | Único (permite um `NULL` na maioria dos bancos) |
| `NOT NULL` | Valor obrigatório |
| `CHECK (expr)` | Regra de domínio |
| `REFERENCES t(c)` | Chave estrangeira; o valor tem de existir lá |
| `DEFAULT v` | Valor quando omitido |
| `GENERATED ALWAYS AS (expr)` | Coluna calculada (SQLite ≥ 3.31) |

⚠️ **No SQLite, chave estrangeira só é verificada com `PRAGMA foreign_keys = ON`**,
e o PRAGMA vale **por conexão**. Sem ele, todo `REFERENCES` é decoração.

### `ALTER TABLE`

| Comando | SQLite | Outros |
|---|---|---|
| `ADD COLUMN` | ✅ | ✅ |
| `RENAME TO` | ✅ | ✅ |
| `RENAME COLUMN` | ✅ (≥ 3.25) | ✅ |
| `DROP COLUMN` | ✅ (≥ 3.35) | ✅ |
| `ALTER COLUMN TYPE` | ❌ | ✅ |
| `ADD CONSTRAINT` | ❌ | ✅ |

No SQLite, mudar tipo ou acrescentar restrição exige o padrão
**"criar nova, copiar, apagar, renomear"** — dentro de uma transação.

---

## 15. Inserir, atualizar, apagar (DML)

```sql
INSERT INTO t (a, b) VALUES (1, 2), (3, 4);           -- várias de uma vez
INSERT INTO t (a, b) SELECT x, y FROM outra;          -- a partir de consulta

UPDATE t SET b = b * 1.1 WHERE a = 1;
DELETE FROM t WHERE a = 1;
```

### `UPSERT` (inserir ou atualizar)

```sql
-- SQLite ≥ 3.24, PostgreSQL ≥ 9.5, DuckDB
INSERT INTO leitura (tag_id, ts, valor) VALUES ('TI-101','2026-07-01 10:00:00', 180.1)
ON CONFLICT (tag_id, ts) DO UPDATE SET valor = excluded.valor;
```

```sql
-- MERGE: padrão ISO; Oracle, SQL Server, PostgreSQL ≥ 15
MERGE INTO leitura t USING nova n ON (t.tag_id=n.tag_id AND t.ts=n.ts)
WHEN MATCHED THEN UPDATE SET valor = n.valor
WHEN NOT MATCHED THEN INSERT (tag_id, ts, valor) VALUES (n.tag_id, n.ts, n.valor);
```

### `RETURNING`

```sql
DELETE FROM leitura WHERE ts < '2020-01-01' RETURNING tag_id, ts;
```
Devolve as linhas afetadas. SQLite ≥ 3.35, PostgreSQL, Oracle, DuckDB.
**Use sempre em `DELETE` grande** — você fica com o registro do que apagou.

### A regra que evita desastre

```sql
-- 1) escreva como SELECT primeiro
SELECT * FROM leitura WHERE ts < '2020-01-01';   -- confira quantas linhas!
-- 2) só então troque por DELETE
```

`UPDATE`/`DELETE` **sem `WHERE`** atinge a tabela inteira. Não existe
"desfazer" fora de uma transação aberta.

---

## 16. Transações

```sql
BEGIN;                              -- ou BEGIN TRANSACTION
UPDATE conta SET saldo = saldo - 100 WHERE id = 1;
UPDATE conta SET saldo = saldo + 100 WHERE id = 2;
COMMIT;                             -- confirma tudo
-- ROLLBACK;                        -- desfaz tudo
```

**ACID:**

| Letra | Significa |
|---|---|
| **A**tomicidade | Tudo ou nada |
| **C**onsistência | As restrições continuam válidas ao fim |
| **I**solamento | Transações concorrentes não se atrapalham |
| **D**urabilidade | Depois do `COMMIT`, sobrevive a queda de energia |

| Nível de isolamento | Impede |
|---|---|
| `READ UNCOMMITTED` | nada |
| `READ COMMITTED` | leitura suja (padrão em Postgres, Oracle, SQL Server) |
| `REPEATABLE READ` | + leitura não repetível (padrão do MySQL/InnoDB) |
| `SERIALIZABLE` | + leitura fantasma (**padrão do SQLite**, que é sempre serializável) |

**Desempenho:** inserir 345 mil linhas com um `COMMIT` por linha leva minutos;
com um `COMMIT` só, leva segundos. Cada `COMMIT` força um `fsync` no disco.
Ver [20-dml-e-transacoes.md](20-dml-e-transacoes.md).

---

## 17. Índices e plano

```sql
CREATE INDEX ix_leitura_ts ON leitura(ts);
CREATE UNIQUE INDEX ux_tag_nome ON tag(descricao);
CREATE INDEX ix_parcial ON leitura(ts) WHERE qualidade = 'RUIM';  -- índice parcial
DROP INDEX ix_leitura_ts;
```

| Objetivo | SQLite | PostgreSQL |
|---|---|---|
| Ver o plano | `EXPLAIN QUERY PLAN <consulta>` | `EXPLAIN <consulta>` |
| Plano + medição real | — | `EXPLAIN (ANALYZE, BUFFERS) <consulta>` |
| Atualizar estatísticas | `ANALYZE` | `ANALYZE` (e o autovacuum faz sozinho) |

**Como ler a saída do SQLite:**

| Aparece | Significa |
|---|---|
| `SCAN t` | Leu a tabela inteira. Ruim, se a tabela é grande |
| `SEARCH t USING INDEX ix (...)` | Usou índice. Bom |
| `SEARCH t USING PRIMARY KEY (...)` | Usou a chave primária. Ótimo |
| `USING COVERING INDEX` | Respondeu **só com o índice**, sem tocar na tabela. Ótimo |
| `USE TEMP B-TREE FOR ORDER BY` | Ordenou na memória. Um índice na ordem certa eliminaria |

**Regras práticas de índice:**

1. Coluna do `WHERE` e do `JOIN` — sim. Coluna que você só exibe — não.
2. Índice composto: a ordem é a ordem das perguntas. `(tag_id, ts)` serve para
   "tag e faixa de tempo" e para "só tag"; **não** serve para "só tempo".
3. Índice acelera leitura e **atrasa escrita**. Cada `INSERT` atualiza todos os
   índices da tabela.
4. **Função na coluna mata o índice.** `WHERE substr(ts,1,10)='2026-07-10'`
   não usa o índice em `ts`; `WHERE ts>='2026-07-10' AND ts<'2026-07-11'` usa.
   Medido no projeto-modelo: 5,0 ms → 0,1 ms.

Detalhe em [21-indices-e-desempenho.md](21-indices-e-desempenho.md).

---

## 18. Comandos do cliente `sqlite3`

Começam com ponto e **não são SQL** — não funcionam em nenhum outro banco.

| Comando | Faz |
|---|---|
| `.help` | Lista tudo |
| `.tables` | Lista tabelas |
| `.schema [t]` | Mostra o DDL |
| `.mode box` \| `table` \| `csv` \| `json` \| `markdown` | Formato de saída |
| `.headers on` | Mostra nome das colunas |
| `.timer on` | Mostra o tempo de cada consulta |
| `.import arq.csv tabela --csv` | Importa CSV |
| `.output arq.csv` | Manda a saída para arquivo (`.output stdout` volta) |
| `.read arq.sql` | Executa um arquivo |
| `.backup arq.db` | Backup **a quente**, consistente |
| `.dump` | Exporta tudo como SQL |
| `.quit` | Sai |

**Configuração permanente** — crie `~/.sqliterc`:
```
.headers on
.mode box
.timer on
```

**Exportar CSV em uma linha, do shell:**
```bash
sqlite3 -header -csv planta.db "SELECT * FROM v_batelada;" > bateladas.csv
```

---

## 19. Obsoleto, e o que usar no lugar

| Obsoleto | Problema | Use |
|---|---|---|
| `FROM a, b WHERE a.id = b.id` | Junção implícita: esquecer o `WHERE` gera produto cartesiano silencioso | `FROM a JOIN b ON ...` |
| `NATURAL JOIN` | Junta por nome; quebra quando alguém adiciona coluna | `JOIN ... ON` explícito |
| `(+)` do Oracle, `*=` do SQL Server | Sintaxe proprietária de junção externa; ambígua | `LEFT JOIN` |
| `SELECT ... INTO` (SQL Server) | Cria tabela implicitamente | `CREATE TABLE AS SELECT` |
| `COUNT(1)` | Mito de que é mais rápido que `COUNT(*)` | `COUNT(*)`, idêntico em todo banco moderno |
| `ORDER BY 1, 2` | Quebra quando o `SELECT` muda | Nome da coluna |
| `WHERE ... IN (subconsulta)` com `NOT` | `NOT IN` quebra com `NULL` | `NOT EXISTS` |
| Cursor em laço para atualizar linha a linha | Milhares de vezes mais lento | Um `UPDATE ... FROM` só |
| `sqlite3_get_table`, `mysql_*` do PHP | APIs mortas | Drivers atuais |
| MySQL `utf8` | São 3 bytes; não cabe emoji nem alguns caracteres | `utf8mb4` |

---

## Autoteste

1. Qual a diferença entre `WHERE` e `HAVING`, e por que ela existe?
2. Por que `AVG(x) OVER (ORDER BY ts)` **não** é média móvel?
3. Você fez um `JOIN` e o número de linhas aumentou. O que isso significa?
4. Escreva as duas formas de "contar só as leituras acima de 195" e diga em
   quais bancos cada uma funciona.
5. Por que `x NOT IN (1, 2, NULL)` nunca devolve linha?
6. Qual índice serve para "tag X entre as datas A e B"? E serve para "todos os
   tags no instante T"?
7. Traduza `date_trunc('hour', ts)` do PostgreSQL para SQLite.
8. Por que `SELECT 7/2` dá 3, e como corrigir?
9. O que significa `USING COVERING INDEX` num plano de execução?
10. Cite três coisas desta lista de obsoletos e o que as substituiu.

---

*Próximo: [06-exemplos.md](06-exemplos.md).*
