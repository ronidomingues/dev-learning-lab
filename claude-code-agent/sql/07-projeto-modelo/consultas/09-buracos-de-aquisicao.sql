-- 09 — Buracos de aquisição e cobertura de dados por tag.
--
-- Conceitos: LEAD, comparação contra o período nominal do tag, cobertura.
--
-- Antes de qualquer análise, esta é a consulta que se roda. Um relatório de
-- rendimento feito sobre um período com 8% dos dados faltando não está errado
-- por 8% — pode estar errado por 100%, se o que faltou foi justamente o pico.
-- "Cobertura" é o primeiro número que um engenheiro deve olhar, e quase
-- ninguém olha.
--
-- Método: para cada leitura, calcule quanto tempo falta até a próxima
-- (LEAD). Se for maior que ~1,5 × o período nominal, houve buraco.
-- O fator 1,5 é uma tolerância arbitrária para jitter do coletor — e está
-- escrito aqui, e não escondido.

WITH intervalos AS (
    SELECT l.tag_id,
           l.ts                                       AS ts_antes,
           LEAD(l.ts) OVER (PARTITION BY l.tag_id ORDER BY l.ts) AS ts_depois,
           t.periodo_s
      FROM leitura l
      JOIN tag t ON t.tag_id = l.tag_id
),
buracos AS (
    SELECT tag_id, ts_antes, ts_depois,
           ROUND((julianday(ts_depois) - julianday(ts_antes)) * 86400.0, 0) AS lacuna_s,
           periodo_s
      FROM intervalos
     WHERE ts_depois IS NOT NULL
       AND (julianday(ts_depois) - julianday(ts_antes)) * 86400.0 > periodo_s * 1.5
)
SELECT tag_id,
       COUNT(*)                                   AS n_buracos,
       ROUND(SUM(lacuna_s) / 3600.0, 2)           AS horas_perdidas,
       MIN(ts_antes)                              AS primeiro_buraco,
       MAX(ts_depois)                             AS ultimo_retorno,
       ROUND(100.0 * (1 - SUM(lacuna_s)
             / (30.0 * 86400.0)), 3)              AS cobertura_pct
  FROM buracos
 GROUP BY tag_id
 ORDER BY horas_perdidas DESC;
