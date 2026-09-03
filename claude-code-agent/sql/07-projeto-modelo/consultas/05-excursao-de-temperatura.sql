-- 05 — Excursão de temperatura: quanto tempo cada batelada passou fora da faixa.
--
-- Conceitos: agregação condicional, junção com o cadastro para pegar o limite,
-- "tempo acima de X" a partir de amostras discretas.
--
-- ATENÇÃO ao que "tempo acima do limite" significa aqui: contamos AMOSTRAS
-- acima do limite e multiplicamos pelo período de amostragem. Isso supõe que
-- o valor se manteve constante até a próxima amostra (interpolação
-- degrau/ZOH, zero-order hold). É a suposição padrão de historiador, e é
-- CONSERVADORA para picos estreitos e OTIMISTA para picos entre amostras:
-- um pico de 40 s entre duas amostras de 60 s simplesmente não existe neste
-- banco. Se a segurança do processo depende disso, o período de amostragem
-- está errado — não a consulta.
--
-- A forma correta de somar tempo com amostragem irregular é usar a diferença
-- para a amostra seguinte, com LEAD() — está na consulta 07.

SELECT f.batelada_id,
       ROUND(MAX(f.valor), 2)                                    AS pico_C,
       t.lim_sup_op                                              AS lim_operacional,
       t.lim_sup_alarme                                          AS lim_alarme,
       COUNT(*) FILTER (WHERE f.valor > t.lim_sup_op)            AS amostras_acima_op,
       COUNT(*) FILTER (WHERE f.valor > t.lim_sup_alarme)        AS amostras_acima_alarme,
       ROUND(COUNT(*) FILTER (WHERE f.valor > t.lim_sup_alarme)
             * t.periodo_s / 60.0, 1)                            AS minutos_em_alarme,
       -- "Grau-minuto acima do limite": integral do excesso. É a grandeza que
       -- de fato se correlaciona com degradação térmica do produto — 1 °C
       -- acima por 60 min não é o mesmo dano que 60 °C acima por 1 min, mas
       -- a contagem de amostras trata os dois igual.
       ROUND(SUM(MAX(f.valor - t.lim_sup_op, 0.0))
             * t.periodo_s / 60.0, 1)                            AS grau_minuto_acima
  FROM v_leitura_fase f
  JOIN tag t ON t.tag_id = f.tag_id
 WHERE f.tag_id = 'TI-101'
   AND f.fase IN ('reacao', 'aquecimento')
 GROUP BY f.batelada_id, t.lim_sup_op, t.lim_sup_alarme, t.periodo_s
HAVING amostras_acima_op > 0
 ORDER BY grau_minuto_acima DESC;
