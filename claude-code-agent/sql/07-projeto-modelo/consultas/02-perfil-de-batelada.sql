-- 02 — Perfil de uma batelada: a "curva de batelada" que se leva para a reunião.
--
-- Conceitos: junção temporal, pivô (pivot) manual com CASE, reamostragem.
--
-- O resultado é uma linha por intervalo de 10 minutos e uma COLUNA por tag —
-- o formato "largo" (wide) que o Excel e o gráfico esperam. No banco os dados
-- estão no formato "longo" (long/tidy): uma linha por (tag, instante).
-- Girar de longo para largo é o "pivô".
--
-- SQLite e PostgreSQL não têm PIVOT nativo: faz-se com
-- MAX(CASE WHEN tag = 'X' THEN valor END). SQL Server e Oracle têm PIVOT;
-- DuckDB tem PIVOT desde a 0.10. Ver 23-dialetos.md.
--
-- Por que MAX e não AVG dentro do CASE? Porque só existe um valor por tag em
-- cada bucket depois do GROUP BY por bucket... exceto que aqui há 10 leituras
-- por bucket, então AVG é o certo para média e MAX é o certo para o pico.
-- Usamos AVG — e é por isso que o pico da excursão aparece suavizado.
-- Esse é o preço da reamostragem, e a razão de historiadores guardarem
-- média, mínimo E máximo. Ver a view v_hora_tag.

WITH bucket AS (
    SELECT batelada_id,
           tag_id,
           (minuto / 10) * 10 AS minuto_10,   -- divisão inteira: 0,10,20,...
           AVG(valor)         AS media,
           MAX(valor)         AS pico
      FROM v_leitura_fase
     WHERE batelada_id = 'B-2026-0057'        -- uma das bateladas com excursão
     GROUP BY batelada_id, tag_id, minuto / 10
)
SELECT minuto_10                                            AS min,
       ROUND(MAX(CASE WHEN tag_id = 'TI-101' THEN media END), 1) AS temp_C,
       ROUND(MAX(CASE WHEN tag_id = 'TI-101' THEN pico  END), 1) AS temp_pico,
       ROUND(MAX(CASE WHEN tag_id = 'PI-101' THEN media END), 2) AS press_bar,
       ROUND(MAX(CASE WHEN tag_id = 'LI-101' THEN media END), 1) AS nivel_pct,
       ROUND(MAX(CASE WHEN tag_id = 'AI-101' THEN media END), 2) AS pH,
       ROUND(MAX(CASE WHEN tag_id = 'SI-101' THEN media END), 0) AS agit_rpm
  FROM bucket
 GROUP BY minuto_10
 ORDER BY minuto_10;
