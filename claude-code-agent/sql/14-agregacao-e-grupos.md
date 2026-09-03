# 14 — Agregação e agrupamento

Nível: iniciante → intermediário · Data: 13/08/2026

Agregar é **colapsar muitas linhas em uma**. É o que transforma 344 mil
leituras em um relatório de uma página — e é onde se perde informação sem
perceber.

---

## 1. As funções de agregação

| Função | Devolve | Trata `NULL` como |
|---|---|---|
| `COUNT(*)` | Número de **linhas** | conta a linha, sempre |
| `COUNT(coluna)` | Número de **valores não nulos** | **ignora** |
| `COUNT(DISTINCT coluna)` | Valores distintos não nulos | ignora |
| `SUM(coluna)` | Soma | ignora (e devolve `NULL` se todos forem nulos) |
| `AVG(coluna)` | Média = `SUM/COUNT` dos **não nulos** | ignora |
| `MIN` / `MAX` | Extremos | ignoram |
| `GROUP_CONCAT(col, sep)` | Concatenação | ignora |
| `TOTAL(coluna)` | Como `SUM`, mas devolve `0.0` em vez de `NULL` | ignora — específico do SQLite |

### A diferença que muda relatório

```sql
SELECT COUNT(*)      AS linhas,          -- 43080
       COUNT(valor)  AS com_valor,       -- 43060
       AVG(valor)    AS media            -- média de 43060, não de 43080
  FROM leitura WHERE tag_id = 'LI-101';
```

Vinte leituras nulas. Se o relatório diz "média de 43.080 amostras", está
mentindo — a média foi de 43.060. **`AVG` ignora `NULL` silenciosamente.**

**Quando isso importa de verdade:** se o sensor falha justamente quando o
processo está em condição extrema (e falha, porque é aí que ele satura,
esquenta ou entope), os nulos **não são aleatórios**. Ignorá-los enviesa a
média para o lado bonito. Este é o mesmo problema de dado faltante não
aleatório (*MNAR*) da estatística, e o SQL não te avisa.

**Sempre traga `COUNT(*)` junto com toda média.**

---

## 2. `GROUP BY`

```sql
SELECT tag_id, COUNT(*), AVG(valor)
  FROM leitura
 GROUP BY tag_id;
```

Regra do padrão: **toda coluna do `SELECT` que não está dentro de uma função
de agregação tem de estar no `GROUP BY`.**

```sql
SELECT tag_id, ts, AVG(valor) FROM leitura GROUP BY tag_id;   -- inválido
```
Qual `ts`? Há 43 mil deles no grupo. A pergunta não faz sentido.

⚠️ **SQLite e MySQL aceitam isso e devolvem um valor arbitrário** — no SQLite,
o da última linha processada. PostgreSQL, Oracle e SQL Server recusam com
erro. **A permissividade é pior**, porque produz resultado errado sem avisar.
Escreva sempre como se estivesse no PostgreSQL.

*(Há uma exceção documentada e útil no SQLite: com `MIN()` ou `MAX()` sozinhos,
as demais colunas vêm da linha que tem o mínimo/máximo. Isso resolve
"em que instante ocorreu o pico" sem `ROW_NUMBER`. É extensão, não padrão.)*

### Agrupar por expressão

```sql
GROUP BY substr(ts, 1, 13)            -- por hora (SQLite)
GROUP BY date_trunc('hour', ts)       -- por hora (PostgreSQL)
GROUP BY CASE WHEN valor > 195 THEN 'alto' ELSE 'normal' END
```

### `HAVING`

```sql
 WHERE qualidade = 'BOA'      -- filtra LINHAS   (antes do agrupamento)
 GROUP BY tag_id
HAVING COUNT(*) > 1000        -- filtra GRUPOS   (depois)
```

**Se dá para escrever no `WHERE`, escreva no `WHERE`** — é mais barato: o
banco descarta a linha antes de gastar trabalho agrupando-a.

---

## 3. Agregação condicional

Como contar/somar só um subconjunto, dentro do mesmo `GROUP BY`.

```sql
-- padrão ISO — SQLite ≥3.30, PostgreSQL, DuckDB
COUNT(*)   FILTER (WHERE valor > 195)
SUM(valor) FILTER (WHERE fase = 'reacao')

-- universal — funciona em Oracle, SQL Server, MySQL também
SUM(CASE WHEN valor > 195 THEN 1 ELSE 0 END)
SUM(CASE WHEN fase = 'reacao' THEN valor ELSE 0 END)
```

Isto substitui subconsulta e é muito mais rápido — uma passada só.

```sql
SELECT tag_id,
       COUNT(*)                                    AS amostras,
       COUNT(*) FILTER (WHERE valor > 195)         AS acima_do_limite,
       ROUND(100.0 * COUNT(*) FILTER (WHERE valor > 195)
             / COUNT(*), 2)                        AS pct_acima
  FROM v_leitura_boa
 GROUP BY tag_id;
```

⚠️ Cuidado com `COUNT(CASE WHEN c THEN 1 ELSE 0 END)` — conta **tudo**, porque
`0` não é `NULL`. O correto é `SUM(CASE ... THEN 1 ELSE 0 END)` ou
`COUNT(CASE WHEN c THEN 1 END)` (sem `ELSE`, para virar `NULL`).

---

## 4. Estatística descritiva em SQL

### O que existe onde

| Estatística | SQLite | PostgreSQL | DuckDB | Oracle | SQL Server |
|---|---|---|---|---|---|
| Média, soma, min, máx | ✅ | ✅ | ✅ | ✅ | ✅ |
| `stddev_samp` / `stddev_pop` | ❌ | ✅ | ✅ | ✅ | `STDEV`/`STDEVP` |
| `var_samp` / `var_pop` | ❌ | ✅ | ✅ | ✅ | `VAR`/`VARP` |
| `percentile_cont` (mediana) | ❌ | ✅ | `quantile_cont` | ✅ | ✅ |
| `corr(y,x)` | ❌ | ✅ | ✅ | ✅ | ❌ |
| `regr_slope`, `regr_r2` | ❌ | ✅ | ✅ | ✅ | ❌ |
| `mode()` | ❌ | ✅ | ✅ | ✅ | ❌ |

### Desvio padrão sem `STDDEV`

```sql
sqrt( (SUM(x*x) - COUNT(*) * AVG(x) * AVG(x)) / (COUNT(*) - 1.0) )
```

Isto é a fórmula "de um passo": s² = (Σx² − n·x̄²)/(n−1).

**Ela tem um problema numérico real e vale entender**, porque não é
pedantismo — é a diferença entre um número certo e um `NaN` na produção.

Quando a média é grande e a variância pequena, `Σx²` e `n·x̄²` são dois números
enormes e quase iguais. Subtraí-los **cancela os dígitos significativos** —
é o *cancelamento catastrófico*. Exemplo concreto: 1000 leituras de uma vazão
com média 1.000.000 e desvio 0,001. `Σx²` ≈ 1e15; a diferença verdadeira é
~1e-3. Em `double` (≈15–16 dígitos decimais), essa diferença está no limite do
ruído do próprio formato, e o resultado pode sair negativo — daí o
`MAX(..., 0)` antes do `sqrt` nas views do
[projeto-modelo](07-projeto-modelo/sql/002-views.sql).

**Para temperatura de reator** (x̄≈180, s≈0,35) está folgadíssimo e a fórmula é
perfeitamente adequada.

**Alternativa correta:** o algoritmo de Welford (dois passos ou atualização
incremental), que não sofre cancelamento. É o que `stddev_samp` do PostgreSQL
usa por dentro. Em SQL puro, o equivalente é fazer dois passos:

```sql
WITH m AS (SELECT AVG(valor) AS media FROM leitura WHERE tag_id='TI-101')
SELECT sqrt(SUM((valor - media)*(valor - media)) / (COUNT(*) - 1.0))
  FROM leitura, m WHERE tag_id = 'TI-101';
```
Mais lento (duas passadas) e numericamente estável. **Recomendação:** use a
forma de um passo por padrão; se a razão x̄/s passar de ~10⁶, use a de dois.

### Amostral × populacional

`stddev_samp` divide por (n−1); `stddev_pop` divide por n. Use **amostral**
quase sempre — você tem uma amostra do processo, não a população de todas as
bateladas que a planta já fez e fará. A diferença some para n grande e importa
para n < 30.

---

## 5. `GROUP BY` estendido: `ROLLUP`, `CUBE`, `GROUPING SETS`

Subtotais em uma consulta só.

```sql
-- PostgreSQL, Oracle, SQL Server, DuckDB — NÃO no SQLite
SELECT area, equipamento_id, SUM(horas_parada)
  FROM parada
 GROUP BY ROLLUP (area, equipamento_id);
```

```
area | equipamento_id | sum
100  | R-101          | 233.5
100  | P-301          |   8.0
100  | NULL           | 241.5    ← subtotal da área 100
NULL | NULL           | 241.5    ← total geral
```

| Forma | Produz |
|---|---|
| `ROLLUP(a,b)` | `(a,b)`, `(a)`, `()` — hierárquico |
| `CUBE(a,b)` | `(a,b)`, `(a)`, `(b)`, `()` — todas as combinações |
| `GROUPING SETS ((a),(b),())` | Exatamente os que você listar |

⚠️ Os `NULL` das linhas de subtotal são indistinguíveis de `NULL` de dado.
Use `GROUPING(a)` (devolve 1 se é linha de subtotal) para diferenciar.

**No SQLite**, emule com `UNION ALL` de duas consultas.

---

## 6. Erros clássicos de agregação

| Erro | Sintoma | Correção |
|---|---|---|
| Média de médias | Número errado quando os grupos têm tamanhos diferentes | Some numerador e denominador separados |
| `COUNT(*)` depois de `JOIN` 1:N | Contagem multiplicada | Conte antes de juntar, ou `COUNT(DISTINCT chave)` |
| `AVG` de dado transiente | "O reator estava a 83 °C" (não estava) | Filtre por fase/regime; traga min e máx |
| `SUM` de valor instantâneo | Somar temperatura não significa nada | Some vazão×tempo, não vazão |
| Esquecer o filtro de qualidade | Média contaminada por dado ruim | Use uma view canônica de "dado bom" |
| `HAVING` no lugar de `WHERE` | Lento | Mova para o `WHERE` |

### A média de médias, com número

```sql
-- ERRADO
SELECT AVG(rendimento_pct) FROM v_batelada;             -- 90.65

-- CERTO (rendimento global, ponderado pela carga)
SELECT 100.0*SUM(produzido_kg)/SUM(carga_kg) FROM v_batelada;   -- 90.60
```

Aqui a diferença é de 0,05 ponto porque as cargas são parecidas. Com uma
batelada de 500 kg e outra de 50.000 kg, a diferença seria enorme — e a
primeira forma daria peso igual às duas.

**Regra:** média de razões ≠ razão de somas. Para rendimento, disponibilidade,
OEE, taxa de refugo — **quase sempre você quer a razão de somas.**

### Somar o que não se soma

Este é erro de engenheiro, não de programador, e por isso é fácil de cometer:

- **Temperatura** é intensiva: `SUM(temperatura)` não significa nada.
- **Vazão** é taxa: some `vazão × Δt`, que dá massa.
- **Nível** é estado: use o último valor, ou a diferença entre início e fim.
- **Massa e energia** são extensivas: essas, sim, somam.

O SQL calcula qualquer coisa que você pedir. Ele não sabe termodinâmica.

---

## 7. Desempenho da agregação

| Situação | Custo |
|---|---|
| `COUNT(*)` sem `WHERE` | SQLite: varre o índice menor. PostgreSQL: varre a tabela (por causa do MVCC) |
| `GROUP BY` sobre coluna indexada, na ordem do índice | Barato: agrupa em fluxo |
| `GROUP BY` sobre expressão | Precisa de hash ou ordenação: mais caro |
| `COUNT(DISTINCT x)` | Caro: precisa guardar todos os valores vistos |
| `GROUP BY` com muitos grupos | Pode estourar a memória e usar disco |

**Truque que vale ouro:** agregue em duas etapas quando o dado é enorme.
Primeiro reduza para nível horário (uma vez, gravado numa tabela), depois
agregue o horário. É o que todo historiador faz por dentro, e é a razão de o
PI System guardar dados "resumidos" além dos brutos. Ver
[18-series-temporais.md](18-series-temporais.md).

---

## Autoteste

1. Qual a diferença entre `COUNT(*)` e `COUNT(coluna)`, e quando isso muda um
   relatório?
2. Por que `AVG` ignorar `NULL` pode enviesar o resultado num sensor de planta?
3. Por que `SELECT tag_id, ts, AVG(valor) ... GROUP BY tag_id` é inválido, e
   por que o SQLite aceitar isso é pior que recusar?
4. Escreva "contar amostras acima de 195" nas duas formas e diga onde cada uma
   funciona.
5. Por que `COUNT(CASE WHEN c THEN 1 ELSE 0 END)` está errado?
6. Explique o cancelamento catastrófico da fórmula de um passo do desvio
   padrão. Quando ele importa e quando não importa?
7. Média de médias × razão de somas: dê um exemplo em que diferem muito.
8. Cite três grandezas de processo que **não** se deve somar, e o que somar no
   lugar.
9. Por que `HAVING` no lugar de `WHERE` é mais lento?

---

*Próximo: [15-subconsultas-e-ctes.md](15-subconsultas-e-ctes.md).*
