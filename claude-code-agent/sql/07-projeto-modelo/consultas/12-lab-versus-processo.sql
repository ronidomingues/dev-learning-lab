-- 12 — Correlação entre condição de processo e resultado de laboratório.
--
-- Conceitos: junção de duas fontes com granularidades diferentes, correlação
-- de Pearson calculada em SQL puro, cuidado com causalidade.
--
-- Esta é A consulta que justifica ter um historiador. O laboratório diz que a
-- viscosidade saiu alta; o historiador diz o que o reator estava fazendo
-- naquela batelada. Ligar os dois é o trabalho.
--
-- A correlação de Pearson em SQL:
--     r = [n·Σxy − Σx·Σy] / sqrt([n·Σx² − (Σx)²]·[n·Σy² − (Σy)²])
-- PostgreSQL tem corr(y, x) pronto; SQLite não tem, então vai na fórmula.
--
-- AVISO PROFISSIONAL, e o mais importante deste arquivo: r alto NÃO é causa.
-- Aqui a correlação existe porque o gerador de dados foi construído com ela.
-- Numa planta real, temperatura de pico e viscosidade estarão correlacionadas
-- também com carga, com lote de matéria-prima, com turno e com o dia da
-- semana — todas correlacionadas entre si. Concluir "abaixe a temperatura"
-- a partir de um r de 0,9 já custou muito dinheiro a muita gente. O SQL
-- entrega a correlação; o entendimento do processo entrega a causa.

WITH condicao AS (
    SELECT batelada_id,
           MAX(valor) AS pico_C,
           AVG(valor) AS media_C
      FROM v_leitura_fase
     WHERE tag_id = 'TI-101' AND fase = 'reacao'
     GROUP BY batelada_id
),
resultado AS (
    SELECT batelada_id,
           MAX(CASE WHEN parametro = 'viscosidade'   THEN valor END) AS viscosidade,
           MAX(CASE WHEN parametro = 'indice_acidez' THEN valor END) AS acidez
      FROM analise_lab
     GROUP BY batelada_id
),
pares AS (
    SELECT c.batelada_id, c.pico_C AS x, r.viscosidade AS y, r.acidez,
           b.rendimento_pct
      FROM condicao c
      JOIN resultado r USING (batelada_id)
      JOIN v_batelada b USING (batelada_id)
     WHERE r.viscosidade IS NOT NULL
)
SELECT COUNT(*)                                                    AS n_bateladas,
       ROUND(AVG(x), 2)                                            AS pico_medio_C,
       ROUND(AVG(y), 1)                                            AS viscosidade_media_cP,
       ROUND((COUNT(*) * SUM(x * y) - SUM(x) * SUM(y))
             / (sqrt(COUNT(*) * SUM(x * x) - SUM(x) * SUM(x))
                * sqrt(COUNT(*) * SUM(y * y) - SUM(y) * SUM(y))), 4)
                                                                   AS r_pico_viscosidade,
       ROUND((COUNT(*) * SUM(x * rendimento_pct) - SUM(x) * SUM(rendimento_pct))
             / (sqrt(COUNT(*) * SUM(x * x) - SUM(x) * SUM(x))
                * sqrt(COUNT(*) * SUM(rendimento_pct * rendimento_pct)
                       - SUM(rendimento_pct) * SUM(rendimento_pct))), 4)
                                                                   AS r_pico_rendimento
  FROM pares;
