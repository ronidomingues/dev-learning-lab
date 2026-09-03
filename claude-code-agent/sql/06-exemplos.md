# 06 — Exemplos

Nível: iniciante → avançado · Data: 13/08/2026

**Todos os 15 exemplos foram executados** contra o banco do
[projeto-modelo](07-projeto-modelo/). As saídas mostradas são as reais.

Para acompanhar:

```bash
cd 07-projeto-modelo
python3 scripts/gerar_dados.py     # cria planta.db, ~5 s
sqlite3 planta.db                  # ou use Python, ver exemplo 0
```

Cada exemplo segue a mesma forma: **problema → consulta → resultado →
o que se aprende**.

| # | Problema | Recurso |
|---|---|---|
| [0](#exemplo-0--rodar-uma-consulta-de-dentro-do-python) | Rodar SQL do Python | `sqlite3` da biblioteca padrão |
| [1](#exemplo-1--media-horaria-de-um-instrumento) | Média horária | `GROUP BY` com truncamento de tempo |
| [2](#exemplo-2--o-pico-de-cada-dia-por-instrumento) | Pico diário por tag | `ROW_NUMBER` + `PARTITION BY` |
| [3](#exemplo-3--ligar-a-leitura-a-batelada-que-estava-rodando) | Junção temporal | `JOIN ... ON` com desigualdade |
| [4](#exemplo-4--um-relatorio-largo-uma-coluna-por-instrumento) | Pivô | `AVG(CASE WHEN ...)` |
| [5](#exemplo-5--tempo-real-acima-do-limite) | Tempo acima do limite | `LEAD` e integração |
| [6](#exemplo-6--periodos-continuos-de-excursao) | Períodos contínuos | *gaps and islands* |
| [7](#exemplo-7--comparar-cada-batelada-com-a-media-do-operador) | Comparar com o grupo | `AVG() OVER (PARTITION BY)` |
| [8](#exemplo-8--achar-o-instrumento-mentiroso-z-score) | Outlier por z-score | subconsulta escalar |
| [9](#exemplo-9--cruzar-laboratorio-com-processo) | Lab × processo | subconsulta correlacionada |
| [10](#exemplo-10--regressao-linear-em-sql-puro) | Regressão linear | mínimos quadrados em SQL |
| [11](#exemplo-11--descobrir-os-instantes-que-faltam) | Dado faltante | CTE **recursiva** |
| [12](#exemplo-12--quartis-e-mediana-sem-funcao-de-percentil) | Mediana sem `percentile` | `ROW_NUMBER` + `CASE` |
| [13](#exemplo-13--caso-real-relatorio-de-liberacao-de-lote) | **Caso real:** liberação de lote | relatório de auditoria |
| [14](#exemplo-14--caso-real-carga-incremental-idempotente) | **Caso real:** carga incremental | `UPSERT` + transação |
| [15](#exemplo-15--o-mesmo-em-duckdb-sobre-csv-e-parquet) | O mesmo em DuckDB | CSV/Parquet sem carga |

---

## Exemplo 0 — Rodar uma consulta de dentro do Python

**Problema:** você quer o resultado num script, não na tela do terminal.

```python
import sqlite3

con = sqlite3.connect("planta.db")

# ATENÇÃO: parâmetro vai com ?, NUNCA com formatação de string.
# "... WHERE tag_id = '" + tag + "'"  é injeção de SQL esperando acontecer,
# e além disso quebra sozinho quando o valor tem apóstrofo.
sql = """
SELECT COUNT(*) AS n, ROUND(AVG(valor), 2) AS media
  FROM leitura
 WHERE tag_id = ?
   AND ts >= ? AND ts < ?
"""
n, media = con.execute(sql, ("TI-101",
                             "2026-07-01 00:00:00",
                             "2026-07-02 00:00:00")).fetchone()
print(f"{n} leituras, média {media} °C")
con.close()
```

```
1440 leituras, média 109.56 °C
```

**O que se aprende:** três linhas de Python e você tem SQL programável. E a
regra que não se negocia: **parâmetros com `?`**, nunca concatenando texto.
Ver [24-sql-com-python.md](24-sql-com-python.md).

---

## Exemplo 1 — Média horária de um instrumento

**Problema:** o historiador guarda um ponto por minuto. Você quer o gráfico
horário do primeiro turno.

```sql
SELECT substr(ts, 1, 13) || ':00'     AS hora,
       COUNT(*)                       AS n,
       ROUND(AVG(valor), 2)           AS media,
       ROUND(MIN(valor), 2)           AS minimo,
       ROUND(MAX(valor), 2)           AS maximo
  FROM leitura
 WHERE tag_id = 'TI-101'
   AND qualidade = 'BOA'
   AND ts >= '2026-07-01 00:00:00'
   AND ts <  '2026-07-01 08:00:00'
 GROUP BY substr(ts, 1, 13)
 ORDER BY hora;
```

```
hora             | n  | media  | minimo | maximo
2026-07-01 00:00 | 60 |  41.31 |  34.27 |  65.63
2026-07-01 01:00 | 60 | 123.09 |  67.74 | 178.25
2026-07-01 02:00 | 60 | 180.05 | 179.13 | 180.99
2026-07-01 03:00 | 59 | 180.06 | 179.53 | 180.75
2026-07-01 04:00 | 60 | 180.03 |  179.2 | 180.63
2026-07-01 05:00 | 60 |  83.40 |   49.8 | 180.41
2026-07-01 06:00 | 60 |  47.47 |   40.8 |  57.84
2026-07-01 07:00 | 60 |  38.22 |  34.78 |  41.69
```

**O que se aprende:**

1. **Sempre traga `n`, `min` e `max` junto com a média.** Olhe a hora das
   05:00: média 83,4 °C, mas o intervalo vai de 49,8 a 180,4. A média sozinha
   diria "o reator estava a 83 °C", o que é uma descrição de um reator que não
   existe — ele estava resfriando. Média de dado transiente é ficção.
2. A hora das 03:00 tem **n = 59**, não 60. Uma amostra foi descartada pelo
   filtro de qualidade. Se você não trouxesse a contagem, não saberia.
3. `substr(ts,1,13)` funciona porque o formato é ISO-8601. Em PostgreSQL seria
   `date_trunc('hour', ts)`; em DuckDB, `time_bucket(INTERVAL '1 hour', ts)`.
   Ver [23-dialetos.md](23-dialetos.md).

---

## Exemplo 2 — O pico de cada dia, por instrumento

**Problema:** "top-N por grupo" — a pergunta que subconsulta não resolve bem e
função de janela resolve em três linhas.

```sql
WITH ranqueado AS (
    SELECT tag_id,
           substr(ts, 1, 10)  AS dia,
           ts,
           valor,
           ROW_NUMBER() OVER (PARTITION BY tag_id, substr(ts, 1, 10)
                              ORDER BY valor DESC) AS rn
      FROM leitura
     WHERE qualidade = 'BOA' AND valor IS NOT NULL
)
SELECT dia, tag_id, ts, ROUND(valor, 2) AS pico
  FROM ranqueado
 WHERE rn = 1
   AND tag_id IN ('TI-101', 'PI-101')
   AND dia <= '2026-07-04'
 ORDER BY dia, tag_id;
```

```
dia        | tag_id | ts                  | pico
2026-07-01 | PI-101 | 2026-07-01 11:54:00 |    2.8
2026-07-01 | TI-101 | 2026-07-01 10:33:00 | 181.52
2026-07-02 | PI-101 | 2026-07-02 04:52:00 |   2.82
2026-07-02 | TI-101 | 2026-07-02 04:02:00 | 182.27
2026-07-03 | PI-101 | 2026-07-03 14:58:00 |   2.84
2026-07-03 | TI-101 | 2026-07-03 06:12:00 | 183.07
2026-07-04 | PI-101 | 2026-07-04 15:47:00 |   2.83
2026-07-04 | TI-101 | 2026-07-04 13:44:00 | 183.43
```

**O que se aprende:** `MAX(valor)` daria o valor do pico, mas **não o instante
em que ele aconteceu** — e é o instante que você leva para investigar. Esse é
exatamente o caso em que `GROUP BY` não serve e `ROW_NUMBER()` serve.

Troque `rn = 1` por `rn <= 3` e você tem os três maiores de cada dia. Tente
fazer isso com `GROUP BY`.

---

## Exemplo 3 — Ligar a leitura à batelada que estava rodando

**Problema:** o historiador não sabe o que é uma batelada; o sistema de
produção não sabe o que é uma leitura. Ligar os dois é a junção mais
importante deste curso.

```sql
SELECT b.batelada_id,
       b.produto,
       COUNT(*)              AS leituras,
       ROUND(AVG(l.valor),2) AS temp_media
  FROM batelada b
  JOIN leitura  l ON l.ts >= b.ts_inicio      -- semiaberto: [início, fim)
                 AND l.ts <  b.ts_fim
 WHERE l.tag_id = 'TI-101'
   AND l.qualidade = 'BOA'
 GROUP BY b.batelada_id, b.produto
 ORDER BY b.batelada_id
 LIMIT 5;
```

```
batelada_id | produto                | leituras | temp_media
B-2026-0001 | Resina alquídica AR-40 |      355 |      132.0
B-2026-0002 | Resina alquídica AR-40 |      388 |      125.4
B-2026-0003 | Resina alquídica AR-40 |      355 |     132.24
B-2026-0004 | Resina alquídica AR-40 |      388 |     125.44
B-2026-0005 | Resina alquídica AR-40 |      372 |     128.43
```

**O que se aprende:**

1. `JOIN ... ON` **não precisa ser igualdade**. Aqui a condição é um intervalo.
   Isso se chama *theta-join*, e é como se liga qualquer coisa a uma janela de
   tempo: batelada, turno, campanha, parada.
2. `>=` no início e `<` no fim. Com `<=` dos dois lados, a leitura do instante
   exato da virada pertenceria a **duas** bateladas — e os totais passariam de
   100%. Há um teste no projeto-modelo que verifica isso.
3. A temperatura média de **toda** a batelada (125–132 °C) é bem menor que o
   setpoint (180 °C), porque inclui carga, aquecimento e resfriamento. Se você
   quer "temperatura de reação", precisa filtrar a fase — ver a view
   `v_leitura_fase` e o exemplo 9.

---

## Exemplo 4 — Um relatório "largo": uma coluna por instrumento

**Problema:** o banco guarda no formato longo (uma linha por tag e instante);
o gráfico e o Excel querem o formato largo (uma coluna por tag).

```sql
SELECT substr(ts, 1, 13) || ':00'                              AS hora,
       ROUND(AVG(CASE WHEN tag_id = 'TI-101' THEN valor END), 1) AS temp_C,
       ROUND(AVG(CASE WHEN tag_id = 'PI-101' THEN valor END), 2) AS press_bar,
       ROUND(AVG(CASE WHEN tag_id = 'AI-101' THEN valor END), 2) AS pH,
       ROUND(AVG(CASE WHEN tag_id = 'FI-201' THEN valor END), 0) AS agua_kg_h
  FROM v_leitura_boa
 WHERE ts >= '2026-07-01 00:00:00' AND ts < '2026-07-01 06:00:00'
 GROUP BY substr(ts, 1, 13)
 ORDER BY hora;
```

```
hora             | temp_C | press_bar | pH   | agua_kg_h
2026-07-01 00:00 |   41.3 |      0.46 | 7.2  |    6008.0
2026-07-01 01:00 |  123.1 |       1.8 | 7.2  |    6020.0
2026-07-01 02:00 |  180.0 |      2.75 | 6.19 |   14944.0
2026-07-01 03:00 |  180.1 |      2.74 | 5.15 |   15034.0
2026-07-01 04:00 |  180.0 |      2.74 | 4.78 |   15010.0
2026-07-01 05:00 |   83.4 |      1.15 | 4.81 |   12578.0
```

**O que se aprende:** o `CASE` dentro do `AVG` é o pivô manual. `AVG` ignora
`NULL`, então cada coluna só agrega as linhas do seu tag — é por isso que
funciona sem precisar de subconsulta.

Repare que o relatório **conta a história do processo**: às 02:00 a
temperatura chega ao patamar, a água de resfriamento pula de 6.000 para 15.000
kg/h (o reator passou a ser exotérmico) e o pH começa a cair — a esterificação
consumindo ácido. Às 05:00 tudo desce: descarga.

⚠️ **Limite do pivô em SQL:** as colunas são fixas, escritas à mão. Para 200
tags você não escreve 200 `CASE`. Aí, ou gera o SQL por programa, ou usa
`PIVOT` (SQL Server, Oracle, DuckDB), ou faz o pivô no Python/Power BI.

---

## Exemplo 5 — Tempo real acima do limite

**Problema:** "quanto tempo o reator ficou acima de 195 °C?" A resposta ingênua
é contar amostras. A correta é somar os intervalos.

```sql
WITH s AS (
    SELECT ts, valor,
           LEAD(ts) OVER (ORDER BY ts) AS prox_ts
      FROM v_leitura_boa
     WHERE tag_id = 'TI-101'
       AND ts >= '2026-07-22 00:00:00' AND ts < '2026-07-22 12:00:00'
)
SELECT ROUND(SUM(CASE WHEN valor > 195
                      THEN (julianday(prox_ts) - julianday(ts)) * 1440.0
                      ELSE 0 END), 2)           AS min_acima_real,
       COUNT(*) FILTER (WHERE valor > 195)      AS amostras_acima
  FROM s
 WHERE prox_ts IS NOT NULL;
```

```
min_acima_real | amostras_acima
          47.0 |             47
```

**O que se aprende:** aqui os dois números batem — 47 minutos, 47 amostras —
**porque não houve falha de aquisição nesse período**. Rode a mesma consulta
no dia 14/07, que tem duas horas de buraco, e eles divergem.

Contar amostras supõe que o período de amostragem é constante. Ele **não é**:
o coletor perde pacote, a rede cai, o servidor reinicia. Somar
`LEAD(ts) - ts` é a forma correta, e é o que separa um número que sobrevive à
auditoria de um que não sobrevive.

**A pergunta que fica**, e que o SQL não responde sozinho: se o pico durou 40
segundos entre duas amostras de 60 segundos, ele **não existe neste banco**.
Nenhuma consulta o encontra. A solução é instrumentação (amostragem mais
rápida, ou registro por exceção com banda morta), não SQL.

---

## Exemplo 6 — Períodos contínuos de excursão

**Problema:** não interessa "47 amostras acima de 195". Interessa "houve **um**
evento de 47 minutos" ou "houve **47 eventos** de 1 minuto" — são coisas
completamente diferentes para a investigação.

```sql
WITH m AS (
    SELECT ts, valor,
           CASE WHEN valor > 195 THEN 1 ELSE 0 END AS alto
      FROM v_leitura_boa
     WHERE tag_id = 'TI-101'
),
b AS (
    SELECT ts, valor, alto,
           ROW_NUMBER() OVER (ORDER BY ts)
         - ROW_NUMBER() OVER (PARTITION BY alto ORDER BY ts) AS grp
      FROM m
)
SELECT MIN(ts)             AS inicio,
       MAX(ts)             AS fim,
       COUNT(*)            AS minutos,
       ROUND(MAX(valor),2) AS pico
  FROM b
 WHERE alto = 1
 GROUP BY grp
 ORDER BY inicio;
```

```
inicio              | fim                 | minutos | pico
2026-07-09 05:25:00 | 2026-07-09 05:25:00 |       1 | 195.05
2026-07-09 05:27:00 | 2026-07-09 05:57:00 |      31 | 197.29
2026-07-22 01:03:00 | 2026-07-22 01:49:00 |      47 | 199.05
```

**O que se aprende:** este é o padrão ***gaps and islands***, e é o truque de
SQL analítico que mais vale decorar. A diferença entre duas numerações — uma
global, outra por grupo — é **constante dentro de cada bloco contíguo** e muda
entre blocos. Essa constante vira o identificador do bloco.

O mesmo padrão resolve: períodos de parada, sessões de operador, campanhas de
produção, blocos de sensor travado (consulta 08 do projeto-modelo), tempo em
alarme.

**E olhe o resultado:** o primeiro evento tem 1 minuto e o segundo, 31 — mas
começam com 2 minutos de diferença. É *um* distúrbio que o critério `>195`
partiu em dois porque a temperatura oscilou em torno do limite. Isso se chama
*chattering*, e é por isso que sistemas de alarme reais usam **banda morta**
(*deadband*) e **atraso de acionamento** (*on-delay*). A correção em SQL seria
agrupar eventos separados por menos de N minutos — mais um `LAG`.

---

## Exemplo 7 — Comparar cada batelada com a média do operador

**Problema:** o rendimento caiu. Foi o operador, foi a matéria-prima, ou foi
a batelada?

```sql
SELECT batelada_id,
       operador,
       rendimento_pct,
       ROUND(AVG(rendimento_pct) OVER (PARTITION BY operador), 2)
                                                      AS media_operador,
       ROUND(rendimento_pct
             - AVG(rendimento_pct) OVER (PARTITION BY operador), 2)
                                                      AS desvio
  FROM v_batelada
 WHERE status = 'CONCLUIDA'
 ORDER BY desvio
 LIMIT 6;
```

```
batelada_id | operador    | rendimento_pct | media_operador | desvio
B-2026-0023 | A. Ferreira |          86.08 |          91.58 |  -5.50
B-2026-0057 | J. Duarte   |          86.45 |          91.58 |  -5.13
B-2026-0019 | C. Rocha    |          90.91 |          91.95 |  -1.04
B-2026-0008 | C. Rocha    |          91.07 |          91.95 |  -0.88
B-2026-0059 | C. Rocha    |          91.15 |          91.95 |  -0.80
B-2026-0033 | M. Nakagawa |          90.89 |          91.66 |  -0.77
```

**O que se aprende:**

1. `AVG(x) OVER (PARTITION BY operador)` calcula a média do grupo **e mantém
   todas as linhas**. Com `GROUP BY` você perderia a linha da batelada.
2. As duas piores bateladas são de **operadores diferentes**, e as médias dos
   quatro operadores são praticamente iguais (91,58 a 91,95). **A conclusão é
   que não é o operador.** As duas piores são exatamente as duas com excursão
   de temperatura — a causa é o controle, não a pessoa.

Esta é a análise que impede a pior reunião de fábrica que existe: aquela em que
se conclui que "o turno da noite trabalha mal" a partir de duas bateladas.
Sempre compare contra a variação do próprio grupo.

---

## Exemplo 8 — Achar o instrumento mentiroso (z-score)

**Problema:** existe alguma leitura fisicamente impossível?

```sql
WITH est AS (
    SELECT AVG(valor) AS m,
           sqrt((SUM(valor*valor) - COUNT(*)*AVG(valor)*AVG(valor))
                / (COUNT(*) - 1.0)) AS s
      FROM v_leitura_fase
     WHERE tag_id = 'PI-101' AND fase = 'reacao'
)
SELECT ts,
       ROUND(valor, 3)         AS valor,
       ROUND((valor - m)/s, 1) AS z
  FROM v_leitura_fase, est
 WHERE tag_id = 'PI-101' AND fase = 'reacao'
   AND ABS(valor - m)/s > 5
 ORDER BY ABS(valor - m)/s DESC
 LIMIT 6;
```

```
ts                  | valor | z
2026-07-07 03:06:00 |   9.9 | 63.4
2026-07-13 20:15:00 |   9.9 | 63.4
2026-07-16 23:40:00 |   9.9 | 63.4
```

**O que se aprende:**

1. Três leituras de 9,9 bar num reator que opera a 2,7 bar, cada uma com
   **z = 63**. Um desvio de 63 sigmas não é processo; é falha de instrumento.
   E as três estão marcadas com **qualidade BOA** no banco.
2. O `FROM v_leitura_fase, est` é uma junção cruzada (`CROSS JOIN`) com uma
   linha só — o idioma de "anexar um escalar a todas as linhas". Legal e
   comum.
3. **Cuidado com a estatística:** média e desvio são calculados **incluindo os
   outliers**, o que infla o desvio e mascara os desvios menores. Para detecção
   séria, use estatística robusta (mediana e MAD) ou calcule as estatísticas
   excluindo o que já se sabe ser ruim. Com z = 63 tanto faz; com z = 4,
   faria diferença.

---

## Exemplo 9 — Cruzar laboratório com processo

**Problema:** as bateladas mais viscosas — o que o reator estava fazendo nelas?

```sql
WITH lab AS (
    SELECT batelada_id, ts_resultado, valor AS visc
      FROM analise_lab WHERE parametro = 'viscosidade'
)
SELECT b.batelada_id,
       b.ts_fim,
       (SELECT ROUND(AVG(valor), 2)
          FROM v_leitura_fase f
         WHERE f.batelada_id = b.batelada_id
           AND f.tag_id = 'TI-101'
           AND f.fase   = 'reacao')                             AS temp_reacao,
       ROUND(l.visc, 1)                                         AS viscosidade,
       ROUND((julianday(l.ts_resultado) - julianday(b.ts_fim))*24, 1)
                                                                AS atraso_lab_h
  FROM v_batelada b
  JOIN lab l USING (batelada_id)
 ORDER BY l.visc DESC
 LIMIT 5;
```

```
batelada_id | ts_fim              | temp_reacao | viscosidade | atraso_lab_h
B-2026-0057 | 2026-07-22 04:25:00 |      189.38 |       743.7 |          5.3
B-2026-0072 | 2026-07-28 14:45:00 |      180.17 |       650.9 |          4.6
B-2026-0007 | 2026-07-03 09:06:00 |      181.91 |       641.6 |          5.3
B-2026-0044 | 2026-07-17 03:11:00 |      180.60 |       636.0 |          4.2
B-2026-0069 | 2026-07-27 02:44:00 |      179.48 |       620.3 |          5.1
```

**O que se aprende, e é a lição mais importante do arquivo:**

A primeira linha confirma a hipótese: temperatura de reação 189 °C (nove graus
acima do normal) e viscosidade 744 cP, muito fora da especificação de 400–600.

**As quatro linhas seguintes a destroem.** Viscosidade de 620 a 651 cP, também
fora de especificação, com temperatura de reação **perfeitamente normal**
(179–182 °C). A temperatura explica *uma* batelada ruim, não as outras quatro.

Se você parasse na primeira linha — e é o que a maioria faz — sairia da reunião
com "temos que controlar melhor a temperatura", implantaria uma ação, e o
problema continuaria em 80% dos casos. A causa das outras quatro está em outro
lugar: lote de matéria-prima, tempo de reação, pureza do anidrido, calibração
do viscosímetro. O SQL te deu a tabela; **quem elimina a hipótese é você**.

A coluna `atraso_lab_h` é a outra lição: o resultado do laboratório chega de
**4 a 5 horas depois** de a batelada terminar. Nesse intervalo, a planta já
está fazendo a batelada seguinte com os mesmos parâmetros. É por isso que
controle de qualidade baseado só em laboratório é sempre reativo, e é o
argumento econômico dos analisadores em linha e dos "sensores virtuais"
(*soft sensors*).

---

## Exemplo 10 — Regressão linear em SQL puro

**Problema:** quantos por cento de rendimento se perde por grau acima do
setpoint?

Mínimos quadrados: `inclinação = (nΣxy − ΣxΣy) / (nΣx² − (Σx)²)`,
`intercepto = (Σy − inclinação·Σx) / n`.

```sql
WITH p AS (
    SELECT (SELECT AVG(valor) FROM v_leitura_fase f2
             WHERE f2.batelada_id = f.batelada_id
               AND f2.tag_id = 'TI-101' AND f2.fase = 'reacao') AS x,
           b.rendimento_pct                                     AS y
      FROM v_batelada b
      JOIN v_leitura_fase f ON f.batelada_id = b.batelada_id
     WHERE b.status = 'CONCLUIDA'
     GROUP BY b.batelada_id
)
SELECT COUNT(*) AS n,
       ROUND((COUNT(*)*SUM(x*y) - SUM(x)*SUM(y))
             / (COUNT(*)*SUM(x*x) - SUM(x)*SUM(x)), 4)          AS inclinacao,
       ROUND((SUM(y) - ((COUNT(*)*SUM(x*y) - SUM(x)*SUM(y))
                        / (COUNT(*)*SUM(x*x) - SUM(x)*SUM(x))) * SUM(x))
             / COUNT(*), 2)                                     AS intercepto
  FROM p;
```

```
n  | inclinacao | intercepto
77 |    -0.3652 |     157.54
```

**Interpretação:** cada grau Celsius a mais na temperatura média de reação
custa **0,37 ponto percentual de rendimento**. Sobre uma batelada de 5.000 kg,
são ~18 kg de produto por grau. Se o produto vale R$ 12/kg e a planta faz 78
bateladas por mês, cada grau de desvio médio custa cerca de **R$ 17 mil por
mês**. Esse é o número que se leva para a reunião de investimento em controle.

**O que se aprende:**

1. Regressão linear cabe em SQL, sem exportar nada.
2. **Mas** o SQL te deu a inclinação e nada mais: sem R², sem intervalo de
   confiança, sem análise de resíduo, sem teste de significância. O
   intercepto de 157,54% é fisicamente absurdo — é extrapolação para 0 °C, e
   só mostra que o modelo linear vale dentro da faixa observada e em lugar
   nenhum fora dela.
3. PostgreSQL tem `regr_slope(y,x)`, `regr_intercept`, `regr_r2` e `corr`
   prontos. DuckDB também. SQLite não — daí a fórmula na mão.
4. **Quando parar de usar SQL:** no momento em que você precisar de R²,
   resíduo ou regressão múltipla, leve o dado para Python
   ([24-sql-com-python.md](24-sql-com-python.md)). O SQL é para trazer e
   agregar; o modelo é do `statsmodels`.

---

## Exemplo 11 — Descobrir os instantes que faltam

**Problema:** o `SELECT` só mostra o que existe. Como achar o que **não**
existe?

```sql
WITH RECURSIVE esperado(ts) AS (
    SELECT '2026-07-14 02:00:00'                      -- caso base
    UNION ALL
    SELECT datetime(ts, '+1 minute')                  -- passo
      FROM esperado
     WHERE ts < '2026-07-14 06:00:00'                 -- PARADA — obrigatória
)
SELECT COUNT(*) AS instantes_faltando,
       MIN(e.ts) AS de,
       MAX(e.ts) AS ate
  FROM esperado e
 WHERE NOT EXISTS (SELECT 1 FROM leitura l
                    WHERE l.tag_id = 'TI-101' AND l.ts = e.ts);
```

```
instantes_faltando | de                  | ate
               120 | 2026-07-14 03:00:00 | 2026-07-14 04:59:00
```

**O que se aprende:**

1. A CTE recursiva **gera** um calendário completo; o `NOT EXISTS` compara com
   o que existe. É a única forma de encontrar ausência: você precisa saber o
   que *deveria* estar lá.
2. **A cláusula de parada não é opcional.** Sem `WHERE ts < ...`, isto roda até
   estourar a memória. Sempre escreva a parada antes de rodar.
3. PostgreSQL faria isto com `generate_series('2026-07-14 02:00'::timestamp,
   '2026-07-14 06:00', '1 minute')` — uma linha. DuckDB idem. O SQLite
   compilado com a extensão também tem `generate_series`, mas **não é o caso
   da versão que vem no Python**, confirmado nesta máquina.
4. Compare com a consulta `09-buracos-de-aquisicao.sql` do projeto-modelo, que
   resolve o mesmo problema por outro caminho (`LEAD`) e não precisa saber o
   período de antemão. **Duas soluções, trade-off real:** a recursiva acha o
   instante exato de cada falta, mas exige gerar o calendário inteiro; a de
   `LEAD` é muito mais rápida, mas só diz onde há lacuna, não quais instantes.

---

## Exemplo 12 — Quartis e mediana sem função de percentil

**Problema:** o SQLite não tem `percentile_cont`. E você precisa da mediana.

```sql
WITH ord AS (
    SELECT rendimento_pct AS v,
           ROW_NUMBER() OVER (ORDER BY rendimento_pct) AS rn,
           COUNT(*)       OVER ()                      AS n
      FROM v_batelada
     WHERE status = 'CONCLUIDA'
)
SELECT ROUND(MIN(v), 2)                                   AS p0,
       ROUND(MAX(CASE WHEN rn <= n*0.25 THEN v END), 2)   AS q1,
       ROUND(MAX(CASE WHEN rn <= n*0.50 THEN v END), 2)   AS mediana,
       ROUND(MAX(CASE WHEN rn <= n*0.75 THEN v END), 2)   AS q3,
       ROUND(MAX(v), 2)                                   AS p100
  FROM ord;
```

```
p0    | q1    | mediana | q3    | p100
86.08 | 91.23 |   91.82 | 92.26 | 92.92
```

**O que se aprende:**

1. Mediana 91,82 contra média 90,65 (exemplo do arquivo 01): a **média é
   puxada para baixo** pelas poucas bateladas ruins. Metade das bateladas
   rende acima de 91,8%. Para dado de processo com cauda, **relate a mediana**
   — ou as duas.
2. `COUNT(*) OVER ()` — janela sem `PARTITION` nem `ORDER BY` — devolve o total
   geral em cada linha. É o idioma de "percentual sobre o total" sem
   subconsulta.
3. Este é um percentil **discreto** (pega um valor existente). `percentile_cont`
   interpola entre os dois vizinhos. Para n = 77 a diferença é irrelevante;
   para n = 5, não é.
4. PostgreSQL: `percentile_cont(0.5) WITHIN GROUP (ORDER BY v)`.
   DuckDB: `quantile_cont(v, 0.5)` — mostrado no exemplo 15.

---

## Exemplo 13 — CASO REAL: relatório de liberação de lote

**Contexto:** este é um relatório que existe em toda planta regulada (ANVISA,
FDA, ISO 9001) e que costuma ser feito à mão, lote por lote, por alguém do
laboratório. É o exemplo que mais paga o tempo de aprender SQL.

**Problema:** quais lotes têm algum ensaio fora de especificação, e qual
exatamente?

```sql
SELECT b.batelada_id,
       b.ts_fim,
       COUNT(*)                                          AS ensaios,
       COUNT(*) FILTER (WHERE v.veredito <> 'CONFORME')  AS fora_de_spec,
       GROUP_CONCAT(
           CASE WHEN v.veredito <> 'CONFORME'
                THEN v.parametro || '=' || ROUND(v.valor,1)
                     || ' (' || v.veredito || ')'
           END, '; ')                                     AS detalhe,
       CASE WHEN COUNT(*) FILTER (WHERE v.veredito <> 'CONFORME') = 0
            THEN 'LIBERADO' ELSE 'RETIDO' END             AS decisao
  FROM v_batelada b
  JOIN v_lab_conforme v USING (batelada_id)
 GROUP BY b.batelada_id, b.ts_fim
HAVING fora_de_spec > 0
 ORDER BY b.ts_fim;
```

```
batelada_id | ts_fim              | ensaios | fora_de_spec | detalhe                     | decisao
B-2026-0007 | 2026-07-03 09:06:00 |       4 |            1 | viscosidade=641.6 (ACIMA)   | RETIDO
B-2026-0023 | 2026-07-09 08:34:00 |       4 |            1 | viscosidade=605.6 (ACIMA)   | RETIDO
B-2026-0035 | 2026-07-13 14:14:00 |       4 |            1 | viscosidade=606.9 (ACIMA)   | RETIDO
B-2026-0044 | 2026-07-17 03:11:00 |       4 |            1 | viscosidade=636.0 (ACIMA)   | RETIDO
B-2026-0057 | 2026-07-22 04:25:00 |       4 |            1 | viscosidade=743.7 (ACIMA)   | RETIDO
B-2026-0069 | 2026-07-27 02:44:00 |       4 |            1 | viscosidade=620.3 (ACIMA)   | RETIDO
B-2026-0072 | 2026-07-28 14:45:00 |       4 |            1 | viscosidade=650.9 (ACIMA)   | RETIDO
```

**7 lotes retidos em 77 — 9,1% de reprovação, todos por viscosidade.** Isso é
um sinal de processo, não de sorte: um único parâmetro reprovando sozinho
aponta para uma causa comum.

**O que se aprende, além do SQL:**

1. **O critério de conformidade está numa view** (`v_lab_conforme`), não
   espalhado em sete planilhas. Muda a especificação? Muda em um lugar, e
   todos os relatórios acompanham. Isso é *governança de dado*, e é o que o
   auditor pergunta.
2. `COUNT(*) FILTER (...)` conta ensaios reprovados **e** ensaios totais na
   mesma passada.
3. `GROUP_CONCAT` monta a justificativa legível na própria consulta. O `CASE`
   sem `ELSE` devolve `NULL` para os conformes, e o `GROUP_CONCAT` **ignora
   `NULL`** — é por isso que a coluna `detalhe` só traz o que reprovou. Esse
   uso deliberado do `NULL` é elegante e vale conhecer.
4. **Reprodutibilidade e auditoria.** Este relatório é um texto de 20 linhas,
   versionável no git, que qualquer pessoa pode reexecutar e obter o mesmo
   resultado. A planilha equivalente não é auditável, e você não consegue
   provar o que ela fazia em março.

**O que falta para produção** (e falta de propósito, para não esconder):
assinatura eletrônica, trilha de auditoria de quem liberou, controle de versão
da especificação vigente na data do lote (a spec de hoje não vale para um lote
de 2024), e retenção de registro. Isso é 21 CFR Part 11 e não cabe numa
consulta — cabe num sistema. Mas o **cálculo** é este.

---

## Exemplo 14 — CASO REAL: carga incremental idempotente

**Contexto:** todo dia às 6h um arquivo CSV chega do historiador. Você precisa
carregá-lo. Duas coisas vão dar errado, garantidamente: o processo vai rodar
duas vezes (e não pode duplicar), e um arquivo vai vir corrigido (e precisa
sobrescrever).

**Idempotente** = rodar duas vezes tem o mesmo efeito de rodar uma. É a
propriedade mais importante de qualquer processo de carga, e a que mais falta.

```python
import sqlite3

con = sqlite3.connect("historico.db")
con.executescript("""
CREATE TABLE IF NOT EXISTS leitura (
    tag_id TEXT, ts TEXT, valor REAL, carregado_em TEXT,
    PRIMARY KEY (tag_id, ts)
) STRICT;

CREATE TABLE IF NOT EXISTS carga (
    id INTEGER PRIMARY KEY,
    arquivo TEXT UNIQUE,          -- a UNIQUE é o que impede a carga dupla
    ts TEXT, linhas INTEGER
) STRICT;
""")

def carregar(arquivo, linhas):
    with con:                     # transação: tudo ou nada
        if con.execute("SELECT 1 FROM carga WHERE arquivo=?", (arquivo,)).fetchone():
            return f"{arquivo}: já carregado, ignorado"
        con.executemany("""
            INSERT INTO leitura VALUES (?, ?, ?, datetime('now'))
            ON CONFLICT (tag_id, ts) DO UPDATE
               SET valor = excluded.valor,
                   carregado_em = datetime('now')
        """, linhas)
        con.execute("INSERT INTO carga(arquivo, ts, linhas) VALUES (?, datetime('now'), ?)",
                    (arquivo, len(linhas)))
        return f"{arquivo}: {len(linhas)} linhas carregadas"

lote = [('TI-101', '2026-07-01 10:00:00', 178.4),
        ('TI-101', '2026-07-01 10:01:00', 179.9)]

print(carregar("2026-07-01.csv", lote))
print(carregar("2026-07-01.csv", lote))                        # de novo!
print("linhas:", con.execute("SELECT COUNT(*) FROM leitura").fetchone()[0])

# arquivo corrigido: mesmo instante, valor novo
print(carregar("2026-07-01-corrigido.csv",
               [('TI-101', '2026-07-01 10:00:00', 178.9)]))
print("valor:", con.execute(
    "SELECT valor FROM leitura WHERE ts='2026-07-01 10:00:00'").fetchone()[0])
print("linhas:", con.execute("SELECT COUNT(*) FROM leitura").fetchone()[0])
```

```
2026-07-01.csv: 2 linhas carregadas
2026-07-01.csv: já carregado, ignorado
linhas: 2
2026-07-01-corrigido.csv: 1 linhas carregadas
valor: 178.9
linhas: 2
```

**O que se aprende:**

1. **`with con:` é a transação.** Se o `executemany` falhar na linha 400 mil,
   nada é gravado e o registro em `carga` também não — a próxima execução
   recomeça limpa. Sem transação, você fica com meia carga e nenhum jeito de
   saber onde parou.
2. **`ON CONFLICT DO UPDATE`** (o *upsert*) resolve a correção: mesma chave,
   valor novo, uma linha só. `excluded` é a linha que **teria** sido inserida.
   Sintaxe do SQLite ≥ 3.24, PostgreSQL ≥ 9.5 e DuckDB; em Oracle/SQL Server é
   `MERGE`.
3. **A `UNIQUE` em `arquivo`** é a segunda linha de defesa: mesmo que a
   verificação em Python falhe por concorrência, o banco recusa.
4. **`carregado_em`** é a trilha: quando este dado entrou, e por qual carga.
   Sem isso, "por que este número mudou?" é uma pergunta sem resposta.

Esse padrão — transação + chave natural + upsert + log de carga — é o
esqueleto de qualquer ETL sério, dos 10 MB do seu CSV aos terabytes de um
data warehouse. É a mesma coisa, na mesma ordem.

---

## Exemplo 15 — O mesmo em DuckDB, sobre CSV e Parquet

**Contexto:** seu historiador exporta CSV. Você não quer criar banco, não quer
importar, não quer esperar. Quer só perguntar.

```bash
pip install duckdb
```

```python
import duckdb

print(duckdb.sql("""
    SELECT tag_id,
           count(*)                       AS n,
           round(avg(valor), 3)           AS media,
           round(stddev_samp(valor), 3)   AS desvio,
           round(quantile_cont(valor, 0.5), 3) AS mediana
      FROM read_csv('/tmp/leitura.csv')
     WHERE qualidade = 'BOA'
     GROUP BY 1 ORDER BY 1 LIMIT 4
"""))
```

```
┌─────────┬───────┬──────────┬──────────┬──────────┐
│ tag_id  │   n   │  media   │  desvio  │ mediana  │
│ varchar │ int64 │  double  │  double  │  double  │
├─────────┼───────┼──────────┼──────────┼──────────┤
│ AI-101  │ 42655 │     6.22 │    1.053 │    6.955 │
│ FI-102  │ 42996 │  542.206 │ 1821.708 │      0.0 │
│ FI-201  │ 43000 │ 8613.121 │ 5356.543 │ 6047.378 │
│ LI-101  │ 42950 │   49.934 │   39.964 │   84.274 │
└─────────┴───────┴──────────┴──────────┴──────────┘
```
`153 ms`, sobre um CSV de **13,3 MB e 344 mil linhas**, sem carregar nada.

Convertendo para Parquet (formato colunar comprimido):

```python
duckdb.sql("COPY (SELECT * FROM read_csv('/tmp/leitura.csv')) "
           "TO '/tmp/leitura.parquet' (FORMAT parquet)")

print(duckdb.sql("""
    SELECT time_bucket(INTERVAL '1 hour', ts::TIMESTAMP) AS hora,
           round(avg(valor), 2) AS media,
           round(max(valor), 2) AS pico
      FROM '/tmp/leitura.parquet'
     WHERE tag_id = 'TI-101' AND qualidade = 'BOA'
     GROUP BY 1 ORDER BY 1 LIMIT 4
"""))
```

```
┌─────────────────────┬────────┬────────┐
│        hora         │ media  │  pico  │
├─────────────────────┼────────┼────────┤
│ 2026-07-01 00:00:00 │  41.31 │  65.63 │
│ 2026-07-01 01:00:00 │ 123.09 │ 178.25 │
│ 2026-07-01 02:00:00 │ 180.05 │ 180.99 │
│ 2026-07-01 03:00:00 │ 180.06 │ 180.75 │
└─────────────────────┴────────┴────────┘
```
`21 ms`. E o Parquet tem **3,3 MB** contra 13,3 MB do CSV — **4× menor**, com
tipos preservados.

**Comparação honesta, medida nesta máquina:**

| Operação | Tempo | Observação |
|---|---|---|
| SQLite, mesma agregação, banco já pronto | **41 ms** | `SCAN leitura` sobre 344 mil linhas |
| DuckDB, direto no CSV | 153 ms | inclui **analisar o CSV inteiro** a cada consulta |
| DuckDB, sobre Parquet | **21 ms** | colunar: lê só as colunas usadas |

**O que se aprende, sem torcida:**

- DuckDB **não é magicamente mais rápido**. Lendo CSV cru ele perde para um
  SQLite já carregado, porque analisar texto custa. Sobre Parquet ele ganha,
  porque lê só as três colunas de que precisa em vez das quatro, já
  comprimidas e com estatísticas por bloco.
- O ganho real do DuckDB para engenheiro químico **não é velocidade, é atrito
  zero**: `SELECT ... FROM 'arquivo.csv'` sem criar tabela, sem importar, sem
  esquema. Do CSV à resposta em 30 segundos.
- DuckDB tem `stddev_samp`, `quantile_cont`, `corr`, `regr_slope`,
  `time_bucket` e `PIVOT` — tudo que falta no SQLite.
- Quando usar cada um: **SQLite** quando o dado é escrito aos poucos e lido por
  chave (é um banco transacional); **DuckDB** quando o dado já existe em
  arquivo e você quer varrer e agregar (é um banco analítico). Ver
  [23-dialetos.md](23-dialetos.md).

---

## Autoteste

1. No exemplo 1, por que a hora das 05:00 tem média 83,4 °C com máximo de
   180,4? O que a média sozinha esconderia?
2. Por que `ROW_NUMBER()` resolve "top-N por grupo" e `GROUP BY` não?
3. No exemplo 3, o que aconteceria se a condição fosse `l.ts <= b.ts_fim`?
4. No exemplo 5, quando o número de amostras acima do limite deixa de ser igual
   ao tempo acima do limite?
5. Explique o truque das duas `ROW_NUMBER()` do exemplo 6 com suas palavras.
6. No exemplo 7, por que a conclusão é "não é o operador"?
7. No exemplo 9, por que as quatro últimas linhas derrubam a hipótese da
   temperatura?
8. No exemplo 10, por que o intercepto de 157,54% não é absurdo — ou é?
9. Por que uma CTE recursiva precisa de condição de parada?
10. No exemplo 14, o que exatamente torna a carga idempotente? Cite os três
    mecanismos.
11. Por que o DuckDB perdeu para o SQLite lendo CSV e ganhou lendo Parquet?

---

*Próximo: [07-projeto-modelo/](07-projeto-modelo/README.md) — a aplicação
inteira. Ou [10-fundamentos.md](10-fundamentos.md) para a base teórica.*
