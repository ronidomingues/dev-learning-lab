-- ============================================================================
-- 001-esquema.sql — Historiador de planta química (DDL)
--
-- Alvo: SQLite >= 3.37 (STRICT exige 3.37; funções de janela exigem 3.25).
-- Executar com:  sqlite3 planta.db < sql/001-esquema.sql
--
-- Decisões de projeto estão comentadas em cada bloco. Leia os comentários:
-- eles são metade do material didático deste projeto.
-- ============================================================================

-- Integridade referencial NÃO é ligada por padrão no SQLite (compatibilidade
-- com bancos antigos). Sem esta linha, todas as FOREIGN KEY abaixo são
-- decoração. Precisa ser reexecutada a cada conexão.
PRAGMA foreign_keys = ON;

-- WAL: leitores não bloqueiam o escritor. Em um historiador (escrita contínua
-- do coletor + leitura contínua dos relatórios) isso é obrigatório.
PRAGMA journal_mode = WAL;

-- ----------------------------------------------------------------------------
-- Cadastro (dados mestres) — mudam raramente, são referenciados por tudo.
-- ----------------------------------------------------------------------------

-- STRICT (SQLite >= 3.37): sem ele, o SQLite aceita 'abacaxi' numa coluna REAL.
-- É o único jeito de ter tipagem de verdade no SQLite.
CREATE TABLE equipamento (
    equipamento_id TEXT PRIMARY KEY,          -- TAG ISA-5.1: R-101, E-201, P-301
    nome           TEXT NOT NULL,
    tipo           TEXT NOT NULL
        CHECK (tipo IN ('reator','trocador','bomba','tanque','coluna','centrifuga')),
    area           TEXT NOT NULL,             -- área da planta (100, 200, 300)
    capacidade_kg  REAL CHECK (capacidade_kg IS NULL OR capacidade_kg > 0)
) STRICT;

-- Um "tag" é um ponto de medição. O nome vem da instrumentação: TI-101 é
-- Temperature Indicator, malha 101. FI = Flow, PI = Pressure, LI = Level,
-- AI = Analyzer, SI = Speed. Essa nomenclatura é a ISA-5.1, e é a razão de
-- o identificador ser TEXT e não um inteiro: o número já existe na planta,
-- está pintado no equipamento, e o operador conhece o tag por esse nome.
CREATE TABLE tag (
    tag_id         TEXT PRIMARY KEY,
    equipamento_id TEXT NOT NULL REFERENCES equipamento(equipamento_id),
    descricao      TEXT NOT NULL,
    grandeza       TEXT NOT NULL
        CHECK (grandeza IN ('temperatura','pressao','vazao','nivel','rotacao','ph')),
    unidade        TEXT NOT NULL,             -- degC, bar, kg/h, %, rpm, pH
    lim_inf_op     REAL,                      -- faixa normal de operação
    lim_sup_op     REAL,
    lim_inf_alarme REAL,                      -- limites de alarme configurados no SDCD
    lim_sup_alarme REAL,
    periodo_s      INTEGER NOT NULL DEFAULT 60
        CHECK (periodo_s > 0),
    CHECK (lim_inf_op IS NULL OR lim_sup_op IS NULL OR lim_inf_op < lim_sup_op)
) STRICT;

-- ----------------------------------------------------------------------------
-- Série temporal — a tabela que cresce para sempre.
-- ----------------------------------------------------------------------------

-- Três decisões que definem o desempenho deste banco:
--
-- 1) PRIMARY KEY (tag_id, ts) — nesta ordem. Praticamente toda consulta de
--    processo é "um tag, um intervalo de tempo". Com a chave nessa ordem, essa
--    consulta é uma varredura de faixa contígua. Com (ts, tag_id) seria uma
--    varredura do período inteiro filtrando por tag. Diferença de 100x.
--
-- 2) WITHOUT ROWID — a tabela É o índice da chave primária (índice
--    agrupado/clustered). Evita guardar a linha duas vezes e evita o salto
--    do índice para a tabela. Vale exatamente quando a chave é a forma de
--    acesso dominante, que é o caso aqui.
--
-- 3) ts como TEXT ISO-8601 UTC 'YYYY-MM-DD HH:MM:SS'. Ordem lexicográfica ==
--    ordem cronológica, e as funções date/strftime do SQLite entendem direto.
--    Alternativa: INTEGER epoch (menor e mais rápido, ilegível a olho nu).
--    Em Postgres a resposta certa seria timestamptz — o SQLite não tem tipo
--    de data, então a escolha é do projetista. UTC, sempre: o horário de
--    verão já apagou dados de planta no Brasil (duas 00:30 no mesmo dia).
CREATE TABLE leitura (
    tag_id    TEXT NOT NULL REFERENCES tag(tag_id),
    ts        TEXT NOT NULL,                  -- UTC 'YYYY-MM-DD HH:MM:SS'
    valor     REAL,                           -- NULL = leitura perdida de verdade
    qualidade TEXT NOT NULL DEFAULT 'BOA'
        CHECK (qualidade IN ('BOA','DUVIDOSA','RUIM')),
    PRIMARY KEY (tag_id, ts)
) STRICT, WITHOUT ROWID;

-- Índice secundário para as consultas "o que aconteceu na planta às 03:14?",
-- que atravessam todos os tags em um instante. Custa espaço e escrita; sem ele
-- essa pergunta varre a tabela inteira.
CREATE INDEX ix_leitura_ts ON leitura(ts);

-- ----------------------------------------------------------------------------
-- Produção (batelada) — o "contexto" que dá sentido à série temporal.
-- ----------------------------------------------------------------------------

CREATE TABLE batelada (
    batelada_id    TEXT PRIMARY KEY,          -- B-2026-0001
    produto        TEXT NOT NULL,
    equipamento_id TEXT NOT NULL REFERENCES equipamento(equipamento_id),
    ts_inicio      TEXT NOT NULL,
    ts_fim         TEXT,                      -- NULL = ainda rodando
    carga_kg       REAL NOT NULL CHECK (carga_kg > 0),
    produzido_kg   REAL CHECK (produzido_kg IS NULL OR produzido_kg >= 0),
    status         TEXT NOT NULL
        CHECK (status IN ('EM_ANDAMENTO','CONCLUIDA','ABORTADA')),
    operador       TEXT,
    -- Regra de negócio no banco, não no aplicativo: o banco é o único ponto
    -- por onde todo mundo passa. Validação só no app é validação opcional.
    CHECK (ts_fim IS NULL OR ts_fim > ts_inicio),
    CHECK ((status = 'EM_ANDAMENTO') = (ts_fim IS NULL))
) STRICT;

CREATE INDEX ix_batelada_periodo ON batelada(ts_inicio, ts_fim);

-- Entradas de massa por batelada — a base do balanço de massa.
CREATE TABLE consumo_insumo (
    batelada_id TEXT NOT NULL REFERENCES batelada(batelada_id),
    insumo      TEXT NOT NULL,
    massa_kg    REAL NOT NULL CHECK (massa_kg >= 0),
    PRIMARY KEY (batelada_id, insumo)
) STRICT;

-- ----------------------------------------------------------------------------
-- Laboratório (LIMS) — a verdade sobre a qualidade, mas atrasada e esparsa.
-- ----------------------------------------------------------------------------

-- Repare no contraste com `leitura`: aqui os dados são poucos, chegam horas
-- depois da coleta, e cada linha custa caro (um técnico, um reagente, um
-- equipamento). O modelo é "chave-valor" (parametro/valor) e não uma coluna
-- por parâmetro, porque a lista de parâmetros muda por produto e por norma.
-- Trade-off assumido: perde-se a tipagem por parâmetro, ganha-se não ter que
-- rodar ALTER TABLE toda vez que o cliente pede um ensaio novo.
CREATE TABLE analise_lab (
    amostra_id  INTEGER PRIMARY KEY,
    batelada_id TEXT NOT NULL REFERENCES batelada(batelada_id),
    ts_coleta   TEXT NOT NULL,
    ts_resultado TEXT NOT NULL,               -- quando o laudo ficou pronto
    parametro   TEXT NOT NULL
        CHECK (parametro IN ('viscosidade','indice_acidez','umidade','pureza')),
    valor       REAL NOT NULL,
    unidade     TEXT NOT NULL,
    lim_inf     REAL,                         -- especificação do produto
    lim_sup     REAL,
    metodo      TEXT,                         -- ASTM D445, etc.
    CHECK (ts_resultado >= ts_coleta)
) STRICT;

CREATE INDEX ix_lab_batelada ON analise_lab(batelada_id, parametro);

-- ----------------------------------------------------------------------------
-- Alarmes e paradas — a operação real, com seus problemas.
-- ----------------------------------------------------------------------------

CREATE TABLE evento_alarme (
    evento_id         INTEGER PRIMARY KEY,
    tag_id            TEXT NOT NULL REFERENCES tag(tag_id),
    ts                TEXT NOT NULL,
    tipo              TEXT NOT NULL
        CHECK (tipo IN ('ALTO','ALTO_ALTO','BAIXO','BAIXO_BAIXO')),
    prioridade        INTEGER NOT NULL CHECK (prioridade BETWEEN 1 AND 3),
    ts_reconhecimento TEXT,                   -- quando o operador reconheceu
    ts_normalizacao   TEXT                    -- quando a variável voltou à faixa
) STRICT;

CREATE INDEX ix_alarme_ts ON evento_alarme(ts);

CREATE TABLE parada (
    parada_id      INTEGER PRIMARY KEY,
    equipamento_id TEXT NOT NULL REFERENCES equipamento(equipamento_id),
    ts_inicio      TEXT NOT NULL,
    ts_fim         TEXT,
    categoria      TEXT NOT NULL
        CHECK (categoria IN ('PROGRAMADA','FALHA','SETUP','FALTA_INSUMO','QUALIDADE')),
    causa          TEXT,
    CHECK (ts_fim IS NULL OR ts_fim > ts_inicio)
) STRICT;

-- ----------------------------------------------------------------------------
-- Metadados do próprio banco — quem carregou o quê e quando.
-- Um historiador sem isso vira um mistério em seis meses.
-- ----------------------------------------------------------------------------
CREATE TABLE carga_log (
    carga_id   INTEGER PRIMARY KEY,
    ts         TEXT NOT NULL,
    descricao  TEXT NOT NULL,
    linhas     INTEGER NOT NULL,
    semente    INTEGER                        -- semente do gerador, p/ reprodutibilidade
) STRICT;
