-- 10 — OEE do reator e Pareto das causas de parada.
--
-- Conceitos: agregação sobre intervalos, soma acumulada (running total),
-- percentual sobre o total com janela vazia OVER ().
--
-- OEE (Overall Equipment Effectiveness) = Disponibilidade × Desempenho × Qualidade.
--   Disponibilidade = tempo produzindo / tempo calendário
--   Desempenho      = produção real / produção teórica no tempo produzindo
--   Qualidade       = massa aprovada / massa produzida
-- É a métrica de manufatura mais usada e mais mal calculada do mundo. O erro
-- clássico é escolher o denominador do jeito que faz o número ficar bonito:
-- "tempo calendário" vira "tempo programado", e a parada de manutenção some.
-- Aqui usamos calendário puro, 30 dias, e o número fica feio. É o honesto.
--
-- A regra 80/20 de Pareto sobre causas de parada é o método padrão de
-- priorização de manutenção. `SUM(...) OVER (ORDER BY ...)` dá o acumulado;
-- `SUM(...) OVER ()` — janela sem ORDER BY nem PARTITION — dá o total geral
-- em cada linha, que é como se calcula percentual sobre o total sem
-- subconsulta.

WITH paradas AS (
    SELECT categoria,
           COUNT(*)                                                    AS ocorrencias,
           SUM((julianday(COALESCE(ts_fim, ts_inicio))
                - julianday(ts_inicio)) * 24.0)                        AS horas
      FROM parada
     WHERE equipamento_id = 'R-101'
     GROUP BY categoria
)
SELECT categoria,
       ocorrencias,
       ROUND(horas, 1)                                                 AS horas,
       ROUND(100.0 * horas / SUM(horas) OVER (), 1)                    AS pct,
       ROUND(100.0 * SUM(horas) OVER (ORDER BY horas DESC
                                      ROWS UNBOUNDED PRECEDING)
             / SUM(horas) OVER (), 1)                                  AS pct_acumulado
  FROM paradas
 ORDER BY horas DESC;
