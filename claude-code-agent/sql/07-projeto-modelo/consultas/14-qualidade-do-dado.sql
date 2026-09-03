-- 14 — O impacto de filtrar (ou não) por qualidade do dado.
--
-- Conceitos: agregação condicional comparando dois universos, o efeito de
-- NULL em funções de agregação.
--
-- Este é o arquivo que mais rende discussão numa auditoria. A tabela `leitura`
-- guarda um flag de qualidade vindo do coletor. Se ninguém filtrar, dados
-- marcados como RUIM entram na média e mudam o resultado. Se todo mundo
-- filtrar, mas cada um de um jeito, os relatórios divergem.
--
-- Repare no comportamento do NULL: COUNT(*) conta linhas; COUNT(valor) conta
-- valores não nulos; AVG(valor) IGNORA nulos silenciosamente. É a diferença
-- entre "média de 43.080 amostras" e "média das 43.060 que existem" — e o
-- relatório vai dizer 43.080 se você escrever COUNT(*). Ver 17-tipos-e-nulos.md.

SELECT l.tag_id,
       t.unidade,
       COUNT(*)                                              AS linhas,
       COUNT(l.valor)                                        AS valores_nao_nulos,
       COUNT(*) - COUNT(l.valor)                             AS nulos,
       COUNT(*) FILTER (WHERE l.qualidade = 'RUIM')          AS ruins,
       COUNT(*) FILTER (WHERE l.qualidade = 'DUVIDOSA')      AS duvidosas,
       ROUND(AVG(l.valor), 3)                                AS media_sem_filtro,
       ROUND(AVG(CASE WHEN l.qualidade = 'BOA' THEN l.valor END), 3)
                                                             AS media_so_boa,
       ROUND(AVG(l.valor)
             - AVG(CASE WHEN l.qualidade = 'BOA' THEN l.valor END), 4)
                                                             AS vies
  FROM leitura l
  JOIN tag t ON t.tag_id = l.tag_id
 GROUP BY l.tag_id, t.unidade
 ORDER BY ABS(COALESCE(vies, 0)) DESC;
