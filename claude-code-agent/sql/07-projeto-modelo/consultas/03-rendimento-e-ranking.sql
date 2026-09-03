-- 03 — Rendimento por batelada, com ranking e comparação contra a média móvel.
--
-- Conceitos: funções de janela (window functions) — RANK, AVG OVER, LAG,
-- moldura (frame) ROWS BETWEEN.
--
-- A pergunta do gerente é "quais bateladas renderam mal?". A pergunta certa é
-- "quais renderam mal COMPARADAS COM AS VIZINHAS?", porque matéria-prima,
-- turno e clima variam ao longo do mês e uma média global esconde tendência.
--
-- A diferença entre GROUP BY e OVER:
--   GROUP BY  colapsa linhas   → uma linha por grupo, perde-se o detalhe.
--   OVER      preserva linhas  → cada linha ganha um número calculado sobre
--                                uma "janela" de linhas vizinhas.
-- Antes das funções de janela (SQL:2003, difundidas só a partir de ~2012)
-- isso exigia auto-junção correlacionada, lenta e ilegível. É o recurso que
-- mais muda a vida de quem analisa dado de processo.
--
-- ROWS BETWEEN 4 PRECEDING AND CURRENT ROW = média das 5 últimas bateladas.
-- Sem a cláusula ROWS, o padrão é RANGE UNBOUNDED PRECEDING, que dá média
-- acumulada — não é o que se quer, e é o erro mais comum aqui.

SELECT batelada_id,
       operador,
       ts_inicio,
       carga_kg,
       produzido_kg,
       rendimento_pct,
       duracao_h,
       RANK() OVER (ORDER BY rendimento_pct DESC)          AS posicao,
       ROUND(AVG(rendimento_pct) OVER (
                 ORDER BY ts_inicio
                 ROWS BETWEEN 4 PRECEDING AND CURRENT ROW), 2) AS media_movel_5,
       ROUND(rendimento_pct - LAG(rendimento_pct)
                 OVER (ORDER BY ts_inicio), 2)             AS delta_anterior,
       NTILE(4) OVER (ORDER BY rendimento_pct)             AS quartil
  FROM v_batelada
 WHERE status = 'CONCLUIDA'
 ORDER BY rendimento_pct ASC
 LIMIT 15;
