-- 11 — OEE consolidado do reator R-101 no período de 30 dias.
--
-- Conceitos: CTEs independentes combinadas com CROSS JOIN, subconsulta
-- escalar, cuidado com o denominador.
--
-- Definições usadas (e elas PRECISAM estar escritas, senão o número não
-- significa nada):
--   Tempo calendário   = 30 dias × 24 h = 720 h.
--   Tempo produzindo   = soma das durações de bateladas CONCLUÍDAS.
--   Ciclo teórico      = 360 min (6 h) por batelada, da receita.
--   Produção teórica   = nº de bateladas possíveis no tempo produzindo × carga média.
--   Qualidade          = massa de bateladas aprovadas no lab / massa produzida total.
--
-- Uma batelada ABORTADA conta como tempo perdido, não como tempo produzindo:
-- é a decisão que mais muda o OEE e a que mais gente esconde.

WITH calendario AS (
    SELECT 30.0 * 24.0 AS horas_calendario
),
producao AS (
    SELECT SUM((julianday(ts_fim) - julianday(ts_inicio)) * 24.0) AS horas_produzindo,
           COUNT(*)                                               AS n_bateladas,
           SUM(produzido_kg)                                      AS kg_produzidos
      FROM batelada
     WHERE status = 'CONCLUIDA'
),
reprovadas AS (
    -- Batelada com qualquer parâmetro fora de especificação é reprovada.
    SELECT COALESCE(SUM(b.produzido_kg), 0) AS kg_reprovados
      FROM batelada b
     WHERE b.status = 'CONCLUIDA'
       AND EXISTS (SELECT 1 FROM v_lab_conforme v
                    WHERE v.batelada_id = b.batelada_id
                      AND v.veredito <> 'CONFORME')
)
SELECT ROUND(c.horas_calendario, 1)                               AS horas_calendario,
       ROUND(p.horas_produzindo, 1)                               AS horas_produzindo,
       p.n_bateladas,
       ROUND(p.kg_produzidos / 1000.0, 1)                         AS toneladas,
       ROUND(100.0 * p.horas_produzindo / c.horas_calendario, 1)  AS disponibilidade_pct,
       ROUND(100.0 * (p.n_bateladas * 6.0) / p.horas_produzindo, 1)
                                                                  AS desempenho_pct,
       ROUND(100.0 * (p.kg_produzidos - r.kg_reprovados)
             / p.kg_produzidos, 1)                                AS qualidade_pct,
       ROUND(100.0
             * (p.horas_produzindo / c.horas_calendario)
             * ((p.n_bateladas * 6.0) / p.horas_produzindo)
             * ((p.kg_produzidos - r.kg_reprovados) / p.kg_produzidos), 1)
                                                                  AS oee_pct
  FROM calendario c
 CROSS JOIN producao p
 CROSS JOIN reprovadas r;
