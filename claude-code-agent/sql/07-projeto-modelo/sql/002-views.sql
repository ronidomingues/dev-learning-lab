-- ============================================================================
-- 002-views.sql — Camada semântica
--
-- Uma view é uma consulta com nome. Ela não guarda dado (no SQLite nunca; em
-- Postgres/Oracle existe MATERIALIZED VIEW, que guarda). Serve para três
-- coisas, nesta ordem de importância:
--
--   1. dar nome a uma regra que senão seria copiada e colada errada
--      (ex.: "leitura válida" = qualidade BOA E valor não nulo);
--   2. esconder junções que todo mundo erra (ex.: ligar leitura a batelada
--      por intervalo de tempo);
--   3. servir de interface estável para quem consome (Power BI, Excel, Python),
--      permitindo mudar a tabela por baixo sem quebrar o relatório de ninguém.
--
-- Executar com:  sqlite3 planta.db < sql/002-views.sql
-- ============================================================================

-- ----------------------------------------------------------------------------
-- v_leitura_boa — a regra de "dado confiável", em UM lugar só.
--
-- Por que isso importa mais do que parece: se cada engenheiro escrever seu
-- próprio filtro, um vai esquecer `qualidade`, outro vai esquecer o NULL, e os
-- dois relatórios vão dar números diferentes na reunião. A discussão vira
-- "de quem é o número certo" em vez de "o que fazer com o número".
-- ----------------------------------------------------------------------------
CREATE VIEW v_leitura_boa AS
SELECT tag_id, ts, valor
  FROM leitura
 WHERE qualidade = 'BOA'
   AND valor IS NOT NULL;

-- ----------------------------------------------------------------------------
-- v_batelada — acrescenta as grandezas derivadas que todo relatório recalcula:
-- duração e rendimento.
--
-- Rendimento = massa de produto / massa de carga. Aqui é rendimento mássico
-- global (não estequiométrico): serve para acompanhamento de produção, não
-- para fechar balanço de reação.
--
-- `* 1.0` força divisão de ponto flutuante — no SQLite dois inteiros dividem
-- como inteiros (7/2 = 3). No Postgres é igual. É a fonte nº 1 de "meu
-- rendimento deu 0%".
-- ----------------------------------------------------------------------------
CREATE VIEW v_batelada AS
SELECT b.batelada_id,
       b.produto,
       b.equipamento_id,
       b.ts_inicio,
       b.ts_fim,
       b.status,
       b.operador,
       b.carga_kg,
       b.produzido_kg,
       -- julianday devolve dias fracionários; ×24 dá horas.
       ROUND((julianday(b.ts_fim) - julianday(b.ts_inicio)) * 24.0, 2) AS duracao_h,
       ROUND(100.0 * b.produzido_kg / b.carga_kg, 2)                   AS rendimento_pct
  FROM batelada b;

-- ----------------------------------------------------------------------------
-- v_leitura_batelada — a junção temporal.
--
-- Esta é a junção que separa quem sabe SQL de quem decora SELECT. A condição
-- não é igualdade: é "o instante da leitura cai dentro do intervalo da
-- batelada". Em álgebra relacional é uma theta-junção; na prática o otimizador
-- precisa de um índice em batelada(ts_inicio, ts_fim) para não fazer produto
-- cartesiano.
--
-- Note o `>=` no início e `<` no fim: intervalo semiaberto [início, fim).
-- Usar `<=` nos dois lados faria a leitura do instante exato de virada
-- pertencer a duas bateladas e o total somaria mais que 100%.
-- ----------------------------------------------------------------------------
CREATE VIEW v_leitura_batelada AS
SELECT b.batelada_id,
       b.produto,
       l.tag_id,
       l.ts,
       l.valor
  FROM batelada b
  JOIN v_leitura_boa l
    ON l.ts >= b.ts_inicio
   AND l.ts <  COALESCE(b.ts_fim, '9999-12-31')
 WHERE b.equipamento_id = (SELECT equipamento_id FROM tag WHERE tag_id = l.tag_id);

-- ----------------------------------------------------------------------------
-- v_leitura_fase — deduz a FASE da batelada a partir do tempo decorrido.
--
-- A planta não grava "estou na fase de reação" em lugar nenhum: o SDCD grava
-- números e horários. A fase é uma interpretação. Aqui ela é reconstruída pelo
-- minuto decorrido desde o início da batelada, que é o método que se usa
-- quando a receita é fixa. Quando a receita é variável (S88/ISA-88), a fase
-- vem de uma tabela de eventos de estado — e aí esta view vira uma junção.
--
-- (julianday(a) - julianday(b)) * 1440 = diferença em minutos.
-- ----------------------------------------------------------------------------
CREATE VIEW v_leitura_fase AS
SELECT lb.batelada_id,
       lb.tag_id,
       lb.ts,
       lb.valor,
       CAST((julianday(lb.ts) - julianday(b.ts_inicio)) * 1440.0 AS INTEGER)
           AS minuto,
       CASE
         WHEN (julianday(lb.ts) - julianday(b.ts_inicio)) * 1440.0 <  45 THEN 'carga'
         WHEN (julianday(lb.ts) - julianday(b.ts_inicio)) * 1440.0 < 120 THEN 'aquecimento'
         WHEN (julianday(lb.ts) - julianday(b.ts_inicio)) * 1440.0 < 300 THEN 'reacao'
         WHEN (julianday(lb.ts) - julianday(b.ts_inicio)) * 1440.0 < 345 THEN 'resfriamento'
         ELSE 'descarga'
       END AS fase
  FROM v_leitura_batelada lb
  JOIN batelada b USING (batelada_id);

-- ----------------------------------------------------------------------------
-- v_hora_tag — reamostragem (downsampling) para 1 hora.
--
-- Ninguém plota 345 mil pontos. O padrão de historiador é reduzir por bucket
-- guardando média, mínimo e máximo — média sozinha esconde o pico, e é o pico
-- que estoura o alarme e queima o produto.
--
-- substr(ts,1,13) || ':00:00' trunca a hora. Feio, e proposital: é o que
-- funciona em SQLite. Em Postgres seria date_trunc('hour', ts); em DuckDB,
-- time_bucket(INTERVAL '1 hour', ts). Ver 23-dialetos.md.
-- ----------------------------------------------------------------------------
CREATE VIEW v_hora_tag AS
SELECT tag_id,
       substr(ts, 1, 13) || ':00:00' AS hora,
       COUNT(*)  AS n,
       ROUND(AVG(valor), 3) AS media,
       ROUND(MIN(valor), 3) AS minimo,
       ROUND(MAX(valor), 3) AS maximo
  FROM v_leitura_boa
 GROUP BY tag_id, substr(ts, 1, 13);

-- ----------------------------------------------------------------------------
-- v_estat_tag_batelada — estatística descritiva por tag e por batelada.
--
-- O SQLite não tem STDDEV (o Postgres tem: stddev_samp). A fórmula usada aqui
-- é a "de um passo": s² = (Σx² − nx̄²)/(n−1). Ela é numericamente instável
-- quando a média é grande e a variância pequena (cancelamento catastrófico:
-- dois números quase iguais subtraídos perdem dígitos significativos).
-- Para temperatura de reator (x̄≈180, s≈2) e float de 64 bits está folgado.
-- Para um sinal com x̄=1e6 e s=1e-3, não estaria. Ver 75-armadilhas.md.
--
-- MAX(..., 0) protege contra variância negativa por erro de arredondamento —
-- que acontece de verdade quando o sinal é constante.
-- ----------------------------------------------------------------------------
CREATE VIEW v_estat_tag_batelada AS
SELECT batelada_id,
       tag_id,
       COUNT(*)                    AS n,
       ROUND(AVG(valor), 3)        AS media,
       ROUND(MIN(valor), 3)        AS minimo,
       ROUND(MAX(valor), 3)        AS maximo,
       ROUND(
         sqrt(
           MAX(
             (SUM(valor * valor) - COUNT(*) * AVG(valor) * AVG(valor))
             / (COUNT(*) - 1.0),
             0.0)
         ), 4)                     AS desvio_padrao
  FROM v_leitura_batelada
 GROUP BY batelada_id, tag_id
HAVING COUNT(*) > 1;

-- ----------------------------------------------------------------------------
-- v_lab_conforme — resultado de laboratório com o veredito de especificação.
--
-- A lógica ternária do SQL aparece aqui inteira: se lim_sup é NULL (parâmetro
-- sem limite superior), `valor > lim_sup` é NULL, não FALSE. Por isso o
-- COALESCE explícito — senão amostras sem limite sumiriam do relatório de
-- conformidade sem ninguém notar.
-- ----------------------------------------------------------------------------
CREATE VIEW v_lab_conforme AS
SELECT a.*,
       CASE
         WHEN COALESCE(a.valor < a.lim_inf, 0) THEN 'ABAIXO'
         WHEN COALESCE(a.valor > a.lim_sup, 0) THEN 'ACIMA'
         ELSE 'CONFORME'
       END AS veredito
  FROM analise_lab a;
