# 16 — Funções de janela (`OVER`)

Nível: intermediário → avançado · Data: 13/08/2026 · Saídas **executadas**

O recurso mais importante do SQL analítico moderno, e o que separa quem
consegue analisar série temporal de quem exporta para o Excel. Está no padrão
desde **SQL:2003**; só virou universal por volta de 2012 (MySQL só ganhou na
versão 8, em 2018).

---

## 1. A ideia

`GROUP BY` **colapsa** linhas: 43.080 leituras viram uma média, e você perde o
detalhe.

`OVER` **preserva** linhas: cada leitura ganha uma coluna nova calculada sobre
suas vizinhas, e você fica com as 43.080 linhas **e** o cálculo.

```
GROUP BY                          OVER
┌────┬─────┐                      ┌────┬─────┬───────┐
│ t1 │ 180 │                      │ t1 │ 180 │ 180.0 │
│ t2 │ 181 │  →  ┌───────┐        │ t2 │ 181 │ 180.5 │
│ t3 │ 179 │     │ 180.0 │        │ t3 │ 179 │ 180.0 │
│ t4 │ 180 │     └───────┘        │ t4 │ 180 │ 180.0 │
└────┴─────┘                      └────┴─────┴───────┘
   perde o detalhe                    mantém tudo
```

---

## 2. Anatomia

```sql
funcao(args) OVER (
    PARTITION BY col        -- opcional: reinicia o cálculo por grupo
    ORDER BY col            -- opcional: define a ordem dentro da janela
    ROWS|RANGE BETWEEN ...  -- opcional: define a moldura (frame)
)
```

| Parte | Sem ela |
|---|---|
| `PARTITION BY` | A janela é a tabela inteira |
| `ORDER BY` | Não há ordem; a moldura é a partição inteira |
| moldura | O padrão depende de haver `ORDER BY` (ver seção 4) |

---

## 3. O catálogo

### Numeração e posição

| Função | Devolve | Empates (1, 2, 2, 3) |
|---|---|---|
| `ROW_NUMBER()` | 1, 2, 3, 4 | ignora empate; ordem arbitrária entre iguais |
| `RANK()` | 1, 2, 2, **4** | empate consome posição |
| `DENSE_RANK()` | 1, 2, 2, **3** | empate não consome |
| `NTILE(n)` | 1..n | divide em n baldes de tamanho parecido |
| `PERCENT_RANK()` | 0..1 | posição relativa |
| `CUME_DIST()` | 0..1 | distribuição acumulada |

Verificado (dados 1, 2, 2, 3):

```
v   | RANK | DENSE_RANK | ROW_NUMBER
1.0 |    1 |          1 |          1
2.0 |    2 |          2 |          2
2.0 |    2 |          2 |          3
3.0 |    4 |          3 |          4
```

⚠️ `ROW_NUMBER()` com empate no `ORDER BY` dá ordem **não determinística**:
duas execuções podem trocar as linhas 2 e 3. Se o resultado precisa ser
estável (e num relatório precisa), desempate com uma segunda coluna:
`ORDER BY valor DESC, ts`.

### Acesso a outras linhas

| Função | Devolve |
|---|---|
| `LAG(col, n, padrão)` | Valor de `n` linhas atrás (padrão n=1) |
| `LEAD(col, n, padrão)` | Valor de `n` linhas à frente |
| `FIRST_VALUE(col)` | Primeiro valor **da moldura** |
| `LAST_VALUE(col)` | Último valor **da moldura** ⚠️ ver armadilha |
| `NTH_VALUE(col, n)` | n-ésimo da moldura |

### Agregações como janela

Qualquer agregação (`SUM`, `AVG`, `COUNT`, `MIN`, `MAX`, e no PostgreSQL
`stddev`, `corr`…) funciona com `OVER`.

---

## 4. Moldura (*frame*): onde mora o erro

**Este é o ponto do arquivo.** A moldura define quais linhas entram no cálculo,
e o padrão não é o que se espera.

| O que você escreve | Moldura efetiva | Resultado |
|---|---|---|
| `AVG(v) OVER ()` | toda a partição | média geral, repetida em toda linha |
| `AVG(v) OVER (ORDER BY ts)` | `RANGE UNBOUNDED PRECEDING` | **média ACUMULADA**, não móvel |
| `AVG(v) OVER (ORDER BY ts ROWS BETWEEN 4 PRECEDING AND CURRENT ROW)` | 5 linhas | média móvel causal |
| `... ROWS BETWEEN 2 PRECEDING AND 2 FOLLOWING` | 5 linhas centradas | média móvel centrada |
| `... ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING` | tudo | como `OVER ()` |

### A demonstração, executada

```sql
SELECT ts, ROUND(valor,2) AS v,
       ROUND(AVG(valor) OVER (ORDER BY ts), 2)                    AS sem_rows,
       ROUND(AVG(valor) OVER (ORDER BY ts
                              ROWS BETWEEN 4 PRECEDING
                                       AND CURRENT ROW), 2)        AS mm5
  FROM v_leitura_boa
 WHERE tag_id='TI-101'
   AND ts >= '2026-07-01 00:45:00' AND ts < '2026-07-01 00:53:00'
 ORDER BY ts;
```

```
ts                  | v     | sem_rows | mm5
2026-07-01 00:45:00 | 40.46 |    40.46 | 40.46
2026-07-01 00:46:00 | 41.51 |    40.99 | 40.99
2026-07-01 00:47:00 | 43.89 |    41.95 | 41.95
2026-07-01 00:48:00 | 45.46 |    42.83 | 42.83
2026-07-01 00:49:00 | 48.11 |    43.89 | 43.89
2026-07-01 00:50:00 | 49.16 |    44.76 | 45.62   ← divergem a partir daqui
2026-07-01 00:51:00 | 51.49 |    45.72 | 47.62
2026-07-01 00:52:00 | 52.92 |    46.62 | 49.43
```

As cinco primeiras linhas são idênticas — a janela ainda não encheu. **Da sexta
em diante elas divergem**, e a divergência cresce: numa rampa de aquecimento, a
média acumulada fica cada vez mais para trás, enquanto a móvel acompanha.

Se você quer média móvel e escreve `OVER (ORDER BY ts)`, o gráfico sai
plausível, suave, e **errado**. Esse é o tipo de erro que sobrevive à revisão.

### `ROWS` × `RANGE`

- `ROWS` conta **linhas físicas**.
- `RANGE` conta **valores lógicos**: linhas com o mesmo valor de `ORDER BY`
  entram todas juntas.

Verificado (dados 1, 2, 2, 3, acumulando):

```
v   | ROWS | RANGE
1.0 |  1.0 |   1.0
2.0 |  3.0 |   5.0   ← RANGE já somou os DOIS "2"
2.0 |  5.0 |   5.0
3.0 |  8.0 |   8.0
```

**Use `ROWS` quase sempre.** `RANGE` só quando o empate deve ser tratado em
bloco — e em série temporal com timestamp único, os dois coincidem.

*(O padrão define `RANGE` com valores — `RANGE BETWEEN INTERVAL '5 minutes'
PRECEDING AND CURRENT ROW`, que é a média móvel **por tempo** e não por
contagem. PostgreSQL ≥ 11 tem; SQLite e MySQL, não. É o recurso que mais faz
falta no SQLite para série temporal com amostragem irregular.)*

### A armadilha do `LAST_VALUE`

```sql
LAST_VALUE(valor) OVER (ORDER BY ts)          -- devolve a PRÓPRIA linha!
```
Porque a moldura padrão termina em `CURRENT ROW`. O correto:

```sql
LAST_VALUE(valor) OVER (ORDER BY ts
                        ROWS BETWEEN UNBOUNDED PRECEDING
                                 AND UNBOUNDED FOLLOWING)
```
`FIRST_VALUE` não sofre disso, porque a moldura padrão já começa no início.

---

## 5. Padrões que valem decorar

### Média móvel e taxa de variação

```sql
SELECT ts, valor,
       ROUND(AVG(valor) OVER (ORDER BY ts
                              ROWS BETWEEN 4 PRECEDING AND CURRENT ROW), 2) AS mm5,
       ROUND((valor - LAG(valor) OVER (ORDER BY ts))
             / NULLIF((julianday(ts) - julianday(LAG(ts) OVER (ORDER BY ts)))
                      * 1440.0, 0), 3)                                      AS taxa_por_min
  FROM v_leitura_boa WHERE tag_id = 'TI-101';
```

Sempre divida pelo Δt **real** (com `LAG(ts)`), nunca pelo período nominal.
Ver [18-series-temporais.md](18-series-temporais.md).

### Top-N por grupo

```sql
WITH r AS (
  SELECT *, ROW_NUMBER() OVER (PARTITION BY tag_id, substr(ts,1,10)
                               ORDER BY valor DESC) AS rn
    FROM v_leitura_boa)
SELECT * FROM r WHERE rn <= 3;
```

### Total geral e percentual, sem subconsulta

```sql
SELECT categoria, horas,
       ROUND(100.0 * horas / SUM(horas) OVER (), 1)                     AS pct,
       ROUND(100.0 * SUM(horas) OVER (ORDER BY horas DESC
                                      ROWS UNBOUNDED PRECEDING)
             / SUM(horas) OVER (), 1)                                   AS pct_acum
  FROM paradas;
```
`SUM(x) OVER ()` — sem `ORDER BY` nem `PARTITION` — é o total geral em cada
linha. É o idioma do Pareto.

### *Gaps and islands* — blocos contíguos

```sql
WITH m AS (SELECT ts, valor, CASE WHEN valor > 195 THEN 1 ELSE 0 END AS alto
             FROM v_leitura_boa WHERE tag_id='TI-101'),
     b AS (SELECT *, ROW_NUMBER() OVER (ORDER BY ts)
                   - ROW_NUMBER() OVER (PARTITION BY alto ORDER BY ts) AS grp
             FROM m)
SELECT MIN(ts) AS inicio, MAX(ts) AS fim, COUNT(*) AS minutos
  FROM b WHERE alto = 1 GROUP BY grp;
```

**Por que funciona:** dentro de um bloco contíguo, as duas numerações avançam
juntas, e a diferença é constante. Entre blocos, a global avança e a por-grupo
não, e a diferença muda. Essa constante é o identificador do bloco.

Variante para sensor travado (blocos de valor idêntico):

```sql
CASE WHEN valor IS LAG(valor) OVER (PARTITION BY tag_id ORDER BY ts)
     THEN 0 ELSE 1 END                    -- marca início de bloco
→ SUM(...) OVER (PARTITION BY tag_id ORDER BY ts ROWS UNBOUNDED PRECEDING)
```

### Comparar com o grupo sem perder a linha

```sql
SELECT batelada_id, operador, rendimento_pct,
       AVG(rendimento_pct) OVER (PARTITION BY operador) AS media_operador,
       rendimento_pct - AVG(rendimento_pct) OVER (PARTITION BY operador) AS desvio
  FROM v_batelada;
```

### Preencher lacuna com o último valor (LOCF)

```sql
-- last observation carried forward
SELECT ts,
       COALESCE(valor,
                LAST_VALUE(valor) OVER (
                    ORDER BY ts
                    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)) AS preenchido
  FROM leitura WHERE tag_id = 'TI-101';
```
⚠️ No SQLite, `LAST_VALUE` **não** ignora `NULL`, então este idioma exige
cuidado. PostgreSQL tem o mesmo problema; o `IGNORE NULLS` do padrão só existe
em Oracle e SQL Server 2022+. A saída portátil é *gaps and islands*:
`MAX(CASE WHEN valor IS NOT NULL THEN ts END) OVER (...)` para achar o último
instante com valor e juntar.

---

## 6. `WINDOW`: nomear a janela

```sql
SELECT ts,
       LAG(valor)  OVER j AS anterior,
       LEAD(valor) OVER j AS proximo,
       AVG(valor)  OVER (j ROWS BETWEEN 4 PRECEDING AND CURRENT ROW) AS mm5
  FROM v_leitura_boa
 WHERE tag_id = 'TI-101'
WINDOW j AS (PARTITION BY tag_id ORDER BY ts);
```

Evita repetir a definição e evita o erro de escrever `PARTITION BY` em três
lugares e esquecer no quarto. SQLite ≥ 3.28, PostgreSQL, Oracle, MySQL 8,
DuckDB.

---

## 7. Desempenho

Funções de janela custam **ordenação**. Cada `OVER` com `ORDER BY` diferente é
uma ordenação a mais.

| Situação | Custo |
|---|---|
| Janela na mesma ordem de um índice existente | Barato — lê em ordem, sem ordenar |
| Janela em outra ordem | Ordenação de tudo |
| Várias janelas com a mesma definição | Uma ordenação só (use `WINDOW`) |
| Várias janelas com definições diferentes | Uma ordenação para cada |

**Filtre antes.** Uma janela sobre 344 mil linhas para depois pegar 10 é
desperdício. Coloque o `WHERE` na CTE de dentro — mas **cuidado**: filtrar
antes muda o resultado da janela, porque as linhas filtradas deixam de ser
vizinhas. Se você quer a média móvel dentro do dia 10, precisa das linhas do
dia 9 na janela para os primeiros pontos. Não há atalho: pense na fronteira.

⚠️ **Não se pode filtrar por função de janela no `WHERE`** — a janela é
calculada depois. Envolva numa CTE e filtre fora:

```sql
WITH r AS (SELECT *, ROW_NUMBER() OVER (...) AS rn FROM t)
SELECT * FROM r WHERE rn = 1;      -- ✅
```

---

## 8. Compatibilidade

| Banco | Desde |
|---|---|
| PostgreSQL | 8.4 (2009) |
| Oracle | 8i (1999) — foi o primeiro |
| SQL Server | 2005 (parcial), 2012 (completo) |
| **SQLite** | **3.25 (2018)**; `WINDOW` na 3.28; `FILTER` na 3.30 |
| MySQL | **8.0 (2018)** — antes disso, não havia |
| MariaDB | 10.2 (2017) |
| DuckDB | desde sempre |

Se você encontrar código com auto-junções correlacionadas fazendo o trabalho de
`LAG`, provavelmente é anterior a essas datas — ou de alguém que aprendeu antes
delas.

---

## Autoteste

1. Qual a diferença fundamental entre `GROUP BY` e `OVER`?
2. `AVG(v) OVER (ORDER BY ts)` é média móvel? Se não, o que é?
3. A partir de qual linha as duas colunas do exemplo divergem, e por quê?
4. Diferença entre `ROWS` e `RANGE`. Quando importa?
5. Por que `LAST_VALUE(v) OVER (ORDER BY ts)` devolve a própria linha?
6. Explique o truque das duas `ROW_NUMBER()` do *gaps and islands*.
7. O que `SUM(x) OVER ()` devolve, e para que serve?
8. Por que `WHERE rn = 1` não funciona diretamente, e qual a solução?
9. `ROW_NUMBER()` com empate: por que o resultado pode mudar entre execuções?
10. Qual o custo de desempenho de uma função de janela, e como reduzi-lo?

---

*Próximo: [17-tipos-e-nulos.md](17-tipos-e-nulos.md).*
