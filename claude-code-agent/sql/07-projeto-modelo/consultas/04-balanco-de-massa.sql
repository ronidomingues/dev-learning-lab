-- 04 — Fechamento de balanço de massa por batelada.
--
-- Conceitos: agregação de tabela filha, HAVING, ABS, tolerância explícita.
--
-- O balanço de massa é a primeira coisa que um engenheiro químico aprende e a
-- última que ele confia. Entra = sai + acumula. Aqui a comparação é entre a
-- soma dos insumos apontados (consumo_insumo) e a carga registrada na
-- batelada. Se os dois não batem, ou o operador errou o apontamento, ou a
-- balança está descalibrada, ou houve perda não registrada.
--
-- A tolerância é EXPLÍCITA (0,5%) e está escrita na consulta, não escondida
-- num "arredonda que fica igual". Todo balanço de planta fecha com erro; o que
-- separa um dado útil de um dado inútil é saber qual erro é aceitável.
--
-- Por que HAVING e não WHERE: WHERE filtra linhas ANTES de agrupar; HAVING
-- filtra grupos DEPOIS de agregar. `SUM(...)` só existe depois do GROUP BY,
-- então o filtro sobre ele tem de ser HAVING. Ver 14-agregacao-e-grupos.md.

SELECT b.batelada_id,
       b.status,
       b.carga_kg                                            AS carga_apontada,
       ROUND(SUM(i.massa_kg), 1)                             AS soma_insumos,
       ROUND(SUM(i.massa_kg) - b.carga_kg, 1)                AS diferenca_kg,
       ROUND(100.0 * (SUM(i.massa_kg) - b.carga_kg)
             / b.carga_kg, 3)                                AS erro_pct,
       -- Onde está a discrepância: qual insumo destoa da proporção de receita.
       ROUND(100.0 * MAX(CASE WHEN i.insumo = 'solvente'
                              THEN i.massa_kg END)
             / SUM(i.massa_kg), 2)                           AS solvente_pct
  FROM batelada b
  JOIN consumo_insumo i ON i.batelada_id = b.batelada_id
 GROUP BY b.batelada_id, b.status, b.carga_kg
HAVING ABS(100.0 * (SUM(i.massa_kg) - b.carga_kg) / b.carga_kg) > 0.5
 ORDER BY ABS(erro_pct) DESC;
