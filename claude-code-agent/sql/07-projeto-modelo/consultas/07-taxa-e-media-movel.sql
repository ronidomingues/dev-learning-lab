-- 07 — Taxa de variação (°C/min) e média móvel de uma rampa de aquecimento.
--
-- Conceitos: LAG, LEAD, moldura de janela, derivada numérica em SQL,
-- integração por trapézio, tempo entre amostras irregular.
--
-- Duas coisas que todo engenheiro de processo quer e não sabe pedir ao banco:
--
--   1. dT/dt  — a taxa de aquecimento. Em SQL é a diferença para a leitura
--      anterior dividida pelo intervalo de tempo. LAG(valor) pega o valor
--      anterior NA ORDEM DA JANELA. Sem LAG, isto exige auto-junção.
--
--   2. o intervalo REAL entre amostras. Nunca suponha que é o período nominal:
--      há buracos de aquisição (ver consulta 09). Calcule com LEAD(ts).
--
-- A média móvel de 5 pontos suaviza o ruído do termopar. Note que ela ATRASA
-- o sinal se a janela for só do passado (ROWS BETWEEN 4 PRECEDING AND CURRENT
-- ROW) e NÃO atrasa se for centrada (2 PRECEDING AND 2 FOLLOWING) — mas a
-- centrada é impossível em tempo real, porque olha o futuro. Filtro de
-- processo em tempo real é sempre atrasado. Não existe almoço grátis.

SELECT ts,
       ROUND(valor, 2)                                       AS temp_C,
       ROUND(LAG(valor) OVER j, 2)                           AS anterior,
       ROUND((julianday(LEAD(ts) OVER j) - julianday(ts))
             * 1440.0, 2)                                    AS delta_t_min,
       ROUND((valor - LAG(valor) OVER j)
             / NULLIF((julianday(ts) - julianday(LAG(ts) OVER j))
                      * 1440.0, 0), 3)                       AS taxa_C_por_min,
       ROUND(AVG(valor) OVER (
                 ORDER BY ts ROWS BETWEEN 4 PRECEDING AND CURRENT ROW), 2)
                                                             AS mm5_causal,
       ROUND(AVG(valor) OVER (
                 ORDER BY ts ROWS BETWEEN 2 PRECEDING AND 2 FOLLOWING), 2)
                                                             AS mm5_centrada
  FROM v_leitura_boa
 WHERE tag_id = 'TI-101'
   AND ts >= '2026-07-01 00:45:00'
   AND ts <  '2026-07-01 02:10:00'
WINDOW j AS (ORDER BY ts)          -- cláusula WINDOW: nomeia a janela e evita repetição
 ORDER BY ts;
