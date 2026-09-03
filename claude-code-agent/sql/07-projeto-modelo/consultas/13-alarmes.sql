-- 13 — Racionalização de alarmes (base EEMUA 191 / ISA-18.2).
--
-- Conceitos: LEFT JOIN para achar ausências, agregação com FILTER, taxa por
-- unidade de tempo, junção contra a série temporal para classificar o alarme.
--
-- A norma ISA-18.2 e o guia EEMUA 191 dão uma meta prática: no máximo
-- ~1 alarme a cada 10 minutos por operador em regime normal (6/h), e menos de
-- 10 alarmes nos 10 minutos seguintes a um distúrbio. Acima disso o operador
-- deixa de ler os alarmes — e o acidente de Texas City (2005) e o de Milford
-- Haven (1994) mostraram o que vem depois. Alarme demais é o mesmo que
-- alarme nenhum, com a diferença de que a auditoria diz que estava alarmado.
--
-- Esta consulta classifica cada alarme em três categorias que decidem a ação:
--   • FUGAZ (< 2 min, não reconhecido)  → provável espícula de instrumento.
--     São os "chattering alarms". Corrige-se com banda morta (deadband) e
--     filtro no SDCD, NUNCA desligando o alarme.
--   • REAL                              → excursão de processo de verdade.
--   • NÃO RECONHECIDO longo             → alarme que ficou tocando; ou o
--     operador ignorou, ou o limite está mal ajustado.

SELECT a.tag_id,
       t.descricao,
       a.tipo,
       COUNT(*)                                                     AS n,
       ROUND(COUNT(*) / 30.0, 2)                                    AS por_dia,
       COUNT(*) FILTER (WHERE a.ts_reconhecimento IS NULL)          AS nao_reconhecidos,
       ROUND(AVG((julianday(a.ts_normalizacao)
                  - julianday(a.ts)) * 1440.0), 1)                  AS dur_media_min,
       COUNT(*) FILTER (
           WHERE (julianday(a.ts_normalizacao) - julianday(a.ts)) * 1440.0 < 2
             AND a.ts_reconhecimento IS NULL)                       AS fugazes,
       ROUND(100.0 * COUNT(*) FILTER (
           WHERE (julianday(a.ts_normalizacao) - julianday(a.ts)) * 1440.0 < 2
             AND a.ts_reconhecimento IS NULL) / COUNT(*), 0)        AS pct_fugaz,
       MIN(a.ts)                                                    AS primeiro,
       MAX(a.ts)                                                    AS ultimo
  FROM evento_alarme a
  JOIN tag t ON t.tag_id = a.tag_id
 GROUP BY a.tag_id, t.descricao, a.tipo
 ORDER BY n DESC;
