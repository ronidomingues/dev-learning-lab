# 17 — Tipos, `NULL` e a lógica de três valores

Nível: intermediário · Data: 13/08/2026 · Todas as saídas **executadas** em SQLite 3.37.2

Este arquivo é sobre as coisas que não dão erro e estão erradas. É o mais
denso do curso em armadilhas por linha.

---

## 1. Tipos de dado

### Os tipos do padrão

| Categoria | Tipos | Notas |
|---|---|---|
| Inteiro | `SMALLINT`, `INTEGER`, `BIGINT` | 2, 4, 8 bytes |
| Exato | `NUMERIC(p,s)`, `DECIMAL(p,s)` | **Exato**. Para dinheiro |
| Aproximado | `REAL`, `DOUBLE PRECISION`, `FLOAT` | IEEE 754. Para grandeza física |
| Texto | `CHAR(n)`, `VARCHAR(n)`, `TEXT`, `CLOB` | |
| Data/hora | `DATE`, `TIME`, `TIMESTAMP`, `TIMESTAMP WITH TIME ZONE`, `INTERVAL` | |
| Booleano | `BOOLEAN` | Aceita `TRUE`, `FALSE` e **`UNKNOWN`** |
| Binário | `BLOB`, `BYTEA` | |
| JSON | `JSON` | Nativo desde SQL:2016/2023 |

### O SQLite é diferente, e você precisa saber disso

O SQLite tem **cinco classes de armazenamento** (`NULL`, `INTEGER`, `REAL`,
`TEXT`, `BLOB`) e **tipagem dinâmica**: o tipo pertence ao **valor**, não à
coluna.

```sql
CREATE TABLE frouxa (v REAL);
INSERT INTO frouxa VALUES ('quente');       -- aceito!
SELECT v, typeof(v) FROM frouxa;
-- ('quente', 'text')
```

Uma coluna declarada `REAL` guardando a palavra "quente". Isso é decisão de
projeto de 2000, não bug — mas é armadilha.

**A correção existe desde a 3.37 (2021): tabelas `STRICT`.**

```sql
CREATE TABLE rigida (v REAL) STRICT;
INSERT INTO rigida VALUES ('quente');
-- IntegrityError: cannot store TEXT value in REAL column rigida.v

INSERT INTO rigida VALUES (5);
SELECT v, typeof(v) FROM rigida;    -- (5.0, 'real')  ← converteu inteiro→real
```

**Use `STRICT` em toda tabela nova.** É a única forma de ter tipagem de verdade
no SQLite, e o [projeto-modelo](07-projeto-modelo/) usa em todas as tabelas.

⚠️ Em `STRICT` os tipos permitidos são só `INT`, `INTEGER`, `REAL`, `TEXT`,
`BLOB` e `ANY`. Nada de `VARCHAR(50)` — o que, aliás, sempre foi decorativo no
SQLite.

---

## 2. Ponto flutuante: o que morde

```sql
SELECT 0.1 + 0.2;          -- 0.30000000000000004
SELECT 0.1 + 0.2 = 0.3;    -- 0   (FALSO)
```

Não é bug do SQL: é IEEE 754. `0,1` não tem representação exata em binário,
como `1/3` não tem em decimal. Vale para Python, C, Excel e sua calculadora.

**Consequências práticas:**

1. **Nunca compare ponto flutuante por igualdade.**
   ```sql
   WHERE ABS(a - b) < 1e-9        -- ✅
   WHERE a = b                    -- ❌
   ```
   *(Exceção legítima: comparar um valor com **ele mesmo** copiado, como na
   detecção de sensor travado do projeto-modelo — ali o número é literalmente
   o mesmo bit a bit.)*

2. **Nunca use ponto flutuante para dinheiro.** Some R$ 0,10 dez mil vezes e o
   centavo desaparece. Use inteiro em centavos, ou `NUMERIC`.

3. **Para grandeza de processo, `REAL` está certo.** Um termopar tipo K tem
   incerteza de ±1,5 °C; `double` tem ~15 dígitos significativos. Preocupar-se
   com o 15º dígito de uma medida com 3 dígitos confiáveis é ruído. **Mas**
   ainda assim não compare por igualdade, e cuidado ao **acumular**: somar um
   milhão de valores acumula erro. Ver o cancelamento catastrófico em
   [14-agregacao-e-grupos.md](14-agregacao-e-grupos.md).

### Divisão inteira

```sql
SELECT 7 / 2;      -- 3     ← inteiro / inteiro = inteiro
SELECT -7 / 2;     -- -3    ← trunca em direção a zero (não é piso!)
SELECT 7.0 / 2;    -- 3.5
SELECT 1 / 3;      -- 0     ← e typeof é 'integer'
```

O idioma correto para percentual:

```sql
100.0 * a / b      -- ✅ o 100.0 promove tudo a real desde o início
100 * a / b        -- ❌ se a<b, a divisão inteira já zerou antes
```

### Arredondamento

```sql
SELECT ROUND(2.5);     --  3.0
SELECT ROUND(3.5);     --  4.0
SELECT ROUND(-2.5);    -- -3.0
```

O SQLite arredonda **meio para longe do zero**. Python usa "meio para o par"
(bankers' rounding): `round(2.5)` em Python é `2`. **O mesmo dado agregado em
SQL e em Python pode diferir no último centavo**, e isso já gerou discussões
de fechamento contábil. Saiba qual regra o seu banco usa.

---

## 3. Conversão implícita: onde o dado some

```sql
SELECT '1' = 1;      -- 0  (FALSO) — texto nunca é igual a número no SQLite
SELECT 1 = 1.0;      -- 1  (verdadeiro) — inteiro e real comparam por valor
```

**Isso significa que uma junção pode devolver zero linhas sem erro** se um lado
guarda `'101'` (texto) e o outro `101` (número). É a causa nº 3 do "meu JOIN
não casa" (depois de espaço em branco e de `NULL`).

```sql
SELECT CAST('12abc' AS INTEGER);   -- 12   ← lê até parar
SELECT CAST('abc'   AS INTEGER);   --  0   ← e NÃO dá erro
```

O `CAST` do SQLite é permissivo até o absurdo: `'abc'` vira `0`. PostgreSQL
recusaria com erro. **Consequência:** um CSV com a coluna trocada carrega
zeros silenciosamente e o seu balanço fecha com uma tonelada a menos.

**Diagnóstico:**
```sql
SELECT typeof(valor), COUNT(*) FROM leitura GROUP BY 1;
-- se aparecer 'text' numa coluna numérica, achou o problema
```

### Comparação de texto ≠ comparação de número

```sql
SELECT '10' < '9';     -- 1  (verdadeiro!)  ordem alfabética
SELECT  10  <  9;      -- 0  (falso)        ordem numérica
```

E o caso que morde em planta:

```sql
SELECT 'TI-101' < 'TI-99';   -- 1 (verdadeiro)
```

`TI-101` vem antes de `TI-99` na ordem de texto, porque `'1' < '9'`. Se os tags
da sua planta são ordenados por nome, `TI-9` aparece depois de `TI-101`. A
correção é preencher com zero à esquerda no cadastro (`TI-099`), não na
consulta.

---

## 4. `NULL` e a lógica de três valores

`NULL` **não é** zero, string vazia, `FALSE` ou "sem valor". É
**"desconhecido"**.

O SQL tem três valores lógicos: `TRUE`, `FALSE` e `UNKNOWN`.

### Tabela-verdade

| A | B | `A AND B` | `A OR B` |
|---|---|---|---|
| T | T | T | T |
| T | F | F | T |
| T | **N** | **N** | **T** |
| F | **N** | **F** | **N** |
| N | N | N | N |

Repare nas duas linhas que salvam: `FALSE AND NULL` = `FALSE` (não importa o
desconhecido, já é falso) e `TRUE OR NULL` = `TRUE`.

### Comparações, verificadas

```sql
SELECT NULL = NULL;     -- NULL     ← não é verdadeiro!
SELECT NULL IS NULL;    -- 1        ← a forma correta
SELECT 1 IS NULL;       -- 0
SELECT 'a' || NULL;     -- NULL     ← o texto inteiro some
```

**Só linhas que avaliam para `TRUE` entram no resultado.** `UNKNOWN` é
descartado igual a `FALSE` — e é por isso que `WHERE valor = NULL` devolve zero
linhas sem erro nenhum.

### `NULL` nas agregações

| Função | Comportamento |
|---|---|
| `COUNT(*)` | Conta a linha |
| `COUNT(col)` | **Ignora** |
| `SUM`, `AVG`, `MIN`, `MAX` | Ignoram; `SUM` de tudo nulo devolve `NULL`, não `0` |
| `GROUP BY` | `NULL` forma **um grupo** (aqui `NULL` casa com `NULL`!) |
| `ORDER BY` | Posição varia por banco |
| `DISTINCT` | `NULL` é considerado igual a `NULL` |
| `UNION` | Idem |

A inconsistência é gritante e histórica: `NULL = NULL` é desconhecido, mas
`GROUP BY` e `DISTINCT` tratam nulos como iguais. O padrão define assim. Não há
lógica; há comitê.

### A armadilha do `NOT IN`, verificada

```sql
SELECT 3 IN     (1, 2, NULL);   -- NULL
SELECT 3 NOT IN (1, 2, NULL);   -- NULL     ← nunca é verdadeiro
```

`3 NOT IN (1,2,NULL)` é `3<>1 AND 3<>2 AND 3<>NULL` = `T AND T AND N` = `N`.
A linha nunca entra.

**Isto significa que `NOT IN (SELECT coluna_anulavel FROM ...)` devolve
sempre zero linhas.** Um filtro que silenciosamente não filtra nada — devolve
vazio, e a pessoa conclui "não há nenhum caso". Sempre use `NOT EXISTS`.

### Comparação segura para `NULL`

| Sintaxe | Onde |
|---|---|
| `a IS NOT DISTINCT FROM b` | **Padrão ISO**; PostgreSQL, DuckDB |
| `a IS b` | SQLite |
| `a <=> b` | MySQL |
| `EXISTS (SELECT a INTERSECT SELECT b)` | portátil e feio |

---

## 5. Domar o `NULL`

| Função | Faz |
|---|---|
| `COALESCE(a, b, c)` | Primeiro não nulo. **Padrão — prefira esta** |
| `IFNULL(a, b)` | SQLite, MySQL |
| `NVL(a, b)` | Oracle |
| `ISNULL(a, b)` | SQL Server |
| `NULLIF(a, b)` | `NULL` se `a = b`; o idioma da divisão segura |

```sql
SELECT a / NULLIF(b, 0);            -- NULL em vez de erro/infinito
SELECT COALESCE(produzido_kg, 0);   -- trata "sem apontamento" como zero
```

⚠️ **Mas pense antes de usar `COALESCE(x, 0)`.** "Não medimos" e "medimos zero"
são coisas diferentes. Transformar nulo em zero numa média puxa o resultado
para baixo e apaga a informação de que faltou dado. **Em dado de processo, o
padrão certo quase sempre é deixar `NULL` e relatar a cobertura**, não
preencher com zero.

---

## 6. `NULL` × zero × vazio: um caso de planta

Um transmissor de vazão. O que cada valor significa:

| Registro | Significado | Como tratar |
|---|---|---|
| `0.0`, qualidade BOA | Vazão medida e é zero. A bomba está parada | Entra na média |
| `NULL`, qualidade RUIM | O coletor não recebeu leitura | **Não** entra. Conta como falta |
| `0.0`, qualidade RUIM | O transmissor caiu e mandou zero | Não entra — é falso zero |
| linha inexistente | Nem houve tentativa de leitura | Buraco de aquisição ([18](18-series-temporais.md)) |
| `-9999` | O historiador legado marcava falha assim | **Converter para `NULL` na carga** |

Os dois últimos são os que mais causam estrago:

- **Linha inexistente ≠ `NULL`.** `COUNT(*)` não vê o que não está lá. Só uma
  série de referência (calendário gerado) revela a ausência.
- **`-9999`, `-999`, `999999` como código de falha** é herança de sistemas
  antigos sem `NULL`. Uma média que inclua `-9999` é lixo, e o número sai
  plausível o suficiente para passar. **Trate na carga**, com
  `NULLIF(valor, -9999)`, e documente.

---

## 7. Booleano

| Banco | Como é |
|---|---|
| PostgreSQL | Tipo `BOOLEAN` de verdade: `TRUE`/`FALSE`/`NULL` |
| **SQLite** | **Não existe.** `TRUE`=1, `FALSE`=0 desde a 3.23 |
| MySQL | `BOOLEAN` é apelido de `TINYINT(1)` |
| Oracle | Não tinha até a **23c** (2023). Usava-se `CHAR(1)` com `'Y'/'N'` |
| SQL Server | `BIT` (0/1/`NULL`) |

Em SQLite, `SELECT valor > 195` devolve `1` ou `0`, e `SUM()` disso conta
quantas vezes foi verdadeiro. É idiomático e funciona.

---

## 8. Checklist de defesa

Antes de confiar em qualquer número que saia de uma consulta:

```sql
-- 1. Há nulos onde não deveria?
SELECT COUNT(*) - COUNT(valor) AS nulos FROM leitura;

-- 2. Há tipo errado escondido?
SELECT typeof(valor), COUNT(*) FROM leitura GROUP BY 1;

-- 3. Há código de falha legado?
SELECT COUNT(*) FROM leitura WHERE valor IN (-9999, -999, 9999, 999999);

-- 4. Há valor fisicamente impossível?
SELECT COUNT(*) FROM leitura l JOIN tag t USING (tag_id)
 WHERE t.grandeza = 'temperatura' AND (l.valor < -273.15 OR l.valor > 2000);

-- 5. Há texto com espaço sobrando na chave?
SELECT COUNT(*) FROM leitura WHERE tag_id <> TRIM(tag_id);

-- 6. A cobertura temporal é o que você acha que é?
SELECT COUNT(*), MIN(ts), MAX(ts) FROM leitura WHERE tag_id = 'TI-101';
```

Seis consultas, dois minutos. Elas já pegaram, na experiência de muita gente,
mais erro de análise do que toda a modelagem estatística que veio depois.

---

## Autoteste

1. Por que `0.1 + 0.2 = 0.3` é falso, e em que casos isso importa de verdade?
2. Por que `REAL` é adequado para temperatura e inadequado para dinheiro?
3. O que `CAST('abc' AS INTEGER)` devolve no SQLite, e por que isso é perigoso
   numa carga de CSV?
4. Por que `'TI-101' < 'TI-99'` é verdadeiro? Qual a correção, e onde ela deve
   ser feita?
5. Complete: `FALSE AND NULL` = ___, `TRUE OR NULL` = ___.
6. Por que `x NOT IN (1, 2, NULL)` nunca devolve linha? Mostre a expansão.
7. Qual a inconsistência entre `NULL = NULL` e `GROUP BY` com nulos?
8. Diferencie: `0.0` com qualidade BOA, `NULL`, e linha inexistente.
9. Por que `COALESCE(valor, 0)` costuma ser errado em dado de processo?
10. O que é `STRICT` no SQLite e por que usar sempre?

---

*Próximo: [18-series-temporais.md](18-series-temporais.md).*
