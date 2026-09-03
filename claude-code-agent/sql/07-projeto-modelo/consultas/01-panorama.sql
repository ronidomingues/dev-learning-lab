-- 01 — Panorama do período: o "bom dia" do engenheiro de processo.
--
-- Conceitos: agregação, FILTER, CASE, divisão segura, NULLIF.
--
-- FILTER (WHERE ...) é SQL padrão desde o SQL:2003 e existe em SQLite >= 3.30,
-- PostgreSQL e DuckDB. Em Oracle, SQL Server e MySQL não existe: lá se escreve
-- SUM(CASE WHEN cond THEN 1 ELSE 0 END). Ver 23-dialetos.md.
--
-- NULLIF(x, 0) devolve NULL quando x é 0 — e dividir por NULL dá NULL em vez
-- de erro. É o idioma padrão de "divisão que não explode quando não houve
-- produção nenhuma".

SELECT
    COUNT(*)                                              AS bateladas,
    COUNT(*) FILTER (WHERE status = 'CONCLUIDA')          AS concluidas,
    COUNT(*) FILTER (WHERE status = 'ABORTADA')           AS abortadas,
    ROUND(SUM(carga_kg) / 1000.0, 1)                      AS carga_t,
    ROUND(SUM(produzido_kg) / 1000.0, 1)                  AS produzido_t,
    ROUND(100.0 * SUM(produzido_kg)
          / NULLIF(SUM(carga_kg), 0), 2)                  AS rendimento_global_pct,
    ROUND(AVG(rendimento_pct), 2)                         AS rendimento_medio_pct,
    MIN(ts_inicio)                                        AS primeiro,
    MAX(ts_fim)                                           AS ultimo
FROM v_batelada;
