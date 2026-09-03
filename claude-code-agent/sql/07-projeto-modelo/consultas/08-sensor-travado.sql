-- 08 — Detecção de sensor travado (frozen / flatline).
--
-- Conceitos: "gaps and islands", soma acumulada como marcador de grupo,
-- duas janelas encadeadas em CTEs.
--
-- Um sensor travado é o pior tipo de falha de instrumento: ele não dá erro,
-- não levanta alarme, e o valor parece plausível. O operador confia. É assim
-- que se opera horas com um transmissor entupido. Detectá-lo é procurar
-- sequências de leituras com valor IDÊNTICO — algo que ruído analógico
-- praticamente nunca produz por muitos minutos seguidos.
--
-- O padrão "gaps and islands" é o truque mais útil de SQL analítico e vale
-- decorar:
--   1. marque com 1 toda linha que INICIA um bloco novo (valor != anterior);
--   2. a soma acumulada dessas marcas é um IDENTIFICADOR DE BLOCO;
--   3. agrupe por esse identificador.
-- O mesmo padrão resolve: detectar paradas contínuas, sessões de usuário,
-- períodos em alarme, e intervalos de operação acima de um limite.
--
-- Cuidado com a comparação de REAL: `valor = LAG(valor)` compara ponto
-- flutuante por igualdade exata. Aqui funciona porque o dado travado é
-- literalmente o mesmo número repetido. Para "praticamente igual" use
-- ABS(valor - anterior) < epsilon. Ver 17-tipos-e-nulos.md.

WITH marcado AS (
    SELECT tag_id, ts, valor,
           CASE WHEN valor IS LAG(valor) OVER (PARTITION BY tag_id ORDER BY ts)
                THEN 0 ELSE 1 END AS inicia_bloco
      FROM v_leitura_boa
     WHERE tag_id IN ('TI-101', 'TI-201', 'PI-101', 'FI-201')
),
blocos AS (
    SELECT tag_id, ts, valor,
           SUM(inicia_bloco) OVER (PARTITION BY tag_id ORDER BY ts
                                   ROWS UNBOUNDED PRECEDING) AS id_bloco
      FROM marcado
)
SELECT tag_id,
       valor                                                  AS valor_travado,
       MIN(ts)                                                AS inicio,
       MAX(ts)                                                AS fim,
       COUNT(*)                                               AS amostras,
       ROUND((julianday(MAX(ts)) - julianday(MIN(ts))) * 1440.0, 0) AS minutos
  FROM blocos
 GROUP BY tag_id, id_bloco, valor
HAVING COUNT(*) >= 10          -- 10 min de sinal analógico idêntico já é suspeito
 ORDER BY amostras DESC;
