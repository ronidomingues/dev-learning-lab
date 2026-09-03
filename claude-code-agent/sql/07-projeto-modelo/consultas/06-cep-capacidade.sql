-- 06 — Controle estatístico de processo: carta X̄ e índices de capacidade.
--
-- Conceitos: CTE encadeada, agregação de agregação, subconsulta escalar,
-- desvio padrão sem função STDDEV.
--
-- O que se calcula:
--   x̄_i   média da temperatura de reação da batelada i  (ponto da carta X̄)
--   x̄̄    média das médias                               (linha central, CL)
--   s     desvio padrão das médias das bateladas         (variação entre bateladas)
--   LSC   x̄̄ + 3s, LIC = x̄̄ − 3s                          (limites de controle)
--   Cp    (LSE − LIE) / 6σ                               (capacidade potencial)
--   Cpk   min(LSE − μ, μ − LIE) / 3σ                     (capacidade real, com desvio de centro)
--
-- ATENÇÃO conceitual, e este é o erro mais caro do CEP:
-- LIMITE DE CONTROLE ≠ LIMITE DE ESPECIFICAÇÃO.
--   • Especificação (LIE/LSE) vem do cliente e do projeto. É o que o produto
--     precisa ser. Aqui: 175–185 °C.
--   • Controle (LIC/LSC) vem do próprio processo — são ±3σ da variação
--     natural. É o que o processo CONSEGUE ser.
-- Colocar limite de especificação numa carta de controle é o mito nº 1 do
-- CEP mal aplicado: leva a "ajustar" o processo a cada ponto fora da spec,
-- o que aumenta a variância (é o experimento do funil, de Deming).
--
-- SQLite não tem STDDEV. A fórmula usada é s² = (Σx² − nx̄²)/(n−1).
-- Em PostgreSQL: stddev_samp(x). Em Oracle e SQL Server: STDEV/STDDEV.
-- Ver 75-armadilhas.md sobre a instabilidade numérica dessa fórmula.

WITH por_batelada AS (
    SELECT batelada_id,
           AVG(valor)              AS media,
           COUNT(*)                AS n,
           SUM(valor * valor)      AS soma_q
      FROM v_leitura_fase
     WHERE tag_id = 'TI-101'
       AND fase = 'reacao'
     GROUP BY batelada_id
),
com_sigma AS (
    SELECT batelada_id,
           media,
           n,
           sqrt(MAX((soma_q - n * media * media) / (n - 1.0), 0.0)) AS sigma_intra
      FROM por_batelada
),
global AS (
    SELECT AVG(media)                                     AS cl,
           sqrt(MAX((SUM(media * media)
                     - COUNT(*) * AVG(media) * AVG(media))
                    / (COUNT(*) - 1.0), 0.0))             AS s_entre,
           AVG(sigma_intra)                               AS sigma_medio
      FROM com_sigma
)
SELECT b.batelada_id,
       ROUND(b.media, 2)                                  AS media_C,
       ROUND(b.sigma_intra, 3)                            AS sigma_intra,
       ROUND(g.cl, 2)                                     AS linha_central,
       ROUND(g.cl + 3 * g.s_entre, 2)                     AS LSC,
       ROUND(g.cl - 3 * g.s_entre, 2)                     AS LIC,
       CASE WHEN b.media > g.cl + 3 * g.s_entre
             OR b.media < g.cl - 3 * g.s_entre
            THEN 'FORA DE CONTROLE' ELSE 'ok' END         AS regra_1_nelson,
       -- Capacidade contra a ESPECIFICAÇÃO de processo 175–185 °C,
       -- usando o sigma de curto prazo (dentro da batelada).
       ROUND((185.0 - 175.0) / (6 * g.sigma_medio), 2)    AS Cp,
       ROUND(MIN(185.0 - g.cl, g.cl - 175.0)
             / (3 * g.sigma_medio), 2)                    AS Cpk
  FROM com_sigma b
 CROSS JOIN global g
 ORDER BY ABS(b.media - g.cl) DESC
 LIMIT 12;
