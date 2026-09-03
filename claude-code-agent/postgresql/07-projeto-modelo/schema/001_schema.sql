-- 001_schema.sql — estrutura da biblioteca.
--
-- Filosofia: o BANCO defende a integridade. Toda regra que pode ser garantida aqui
-- (chaves, unicidade, CHECK, exclusão) é garantida aqui — não na aplicação, que pode
-- ter bugs, ser reescrita ou ganhar um segundo cliente que esquece a regra.
--
-- Idempotente na medida do possível: começa limpando, para poder rodar de novo no estudo.

BEGIN;

DROP TABLE IF EXISTS emprestimos CASCADE;
DROP TABLE IF EXISTS livros_autores CASCADE;
DROP TABLE IF EXISTS exemplares CASCADE;
DROP TABLE IF EXISTS livros CASCADE;
DROP TABLE IF EXISTS autores CASCADE;
DROP TABLE IF EXISTS membros CASCADE;
DROP VIEW IF EXISTS livros_disponiveis CASCADE;

-- ---------------------------------------------------------------------------
-- autores
-- ---------------------------------------------------------------------------
CREATE TABLE autores (
    id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nome        TEXT NOT NULL,
    nascimento  DATE,
    criado_em   TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ---------------------------------------------------------------------------
-- livros — a OBRA (o título), não o objeto físico. O objeto físico é o exemplar.
-- ---------------------------------------------------------------------------
CREATE TABLE livros (
    id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    -- ISBN é único quando existe, mas pode faltar em livros antigos: UNIQUE permite vários NULL.
    isbn        TEXT UNIQUE,
    titulo      TEXT NOT NULL,
    ano         INTEGER CHECK (ano BETWEEN 1400 AND EXTRACT(YEAR FROM now())::int + 1),
    -- Metadados que variam de livro para livro ficam em JSONB, com garantia de ser um objeto.
    dados       JSONB NOT NULL DEFAULT '{}' CHECK (jsonb_typeof(dados) = 'object'),
    criado_em   TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Relação MUITOS-PARA-MUITOS: um livro tem vários autores; um autor, vários livros.
CREATE TABLE livros_autores (
    livro_id  BIGINT NOT NULL REFERENCES livros(id)  ON DELETE CASCADE,
    autor_id  BIGINT NOT NULL REFERENCES autores(id) ON DELETE CASCADE,
    PRIMARY KEY (livro_id, autor_id)     -- impede o mesmo par duas vezes
);

-- ---------------------------------------------------------------------------
-- exemplares — cada CÓPIA FÍSICA de um livro. É o que se empresta.
-- ---------------------------------------------------------------------------
CREATE TABLE exemplares (
    id           BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    livro_id     BIGINT NOT NULL REFERENCES livros(id) ON DELETE CASCADE,
    codigo       TEXT NOT NULL UNIQUE,   -- etiqueta física, ex.: "BIB-000123"
    aposentado   BOOLEAN NOT NULL DEFAULT false,   -- danificado/perdido: não empresta mais
    criado_em    TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ---------------------------------------------------------------------------
-- membros — quem pega emprestado.
-- ---------------------------------------------------------------------------
CREATE TABLE membros (
    id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nome        TEXT NOT NULL,
    email       TEXT NOT NULL UNIQUE,
    ativo       BOOLEAN NOT NULL DEFAULT true,
    criado_em   TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ---------------------------------------------------------------------------
-- emprestimos — o coração das regras de negócio.
-- ---------------------------------------------------------------------------
CREATE TABLE emprestimos (
    id            BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    exemplar_id   BIGINT NOT NULL REFERENCES exemplares(id) ON DELETE RESTRICT,
    membro_id     BIGINT NOT NULL REFERENCES membros(id)    ON DELETE RESTRICT,
    emprestado_em TIMESTAMPTZ NOT NULL DEFAULT now(),
    vence_em      DATE NOT NULL,
    devolvido_em  TIMESTAMPTZ,           -- NULL = ainda emprestado
    -- A data de devolução, quando existe, não pode ser anterior ao empréstimo.
    CONSTRAINT devolucao_coerente CHECK (devolvido_em IS NULL OR devolvido_em >= emprestado_em)
);

-- A REGRA DE OURO, garantida pelo banco:
-- um exemplar não pode ter DOIS empréstimos em aberto ao mesmo tempo.
-- Índice único PARCIAL: só vale para as linhas onde devolvido_em IS NULL.
CREATE UNIQUE INDEX ix_um_emprestimo_aberto_por_exemplar
    ON emprestimos (exemplar_id)
    WHERE devolvido_em IS NULL;

-- ---------------------------------------------------------------------------
-- Índices para os padrões de consulta reais.
-- ---------------------------------------------------------------------------
CREATE INDEX ix_livros_autores_autor ON livros_autores (autor_id);
CREATE INDEX ix_exemplares_livro     ON exemplares (livro_id);
CREATE INDEX ix_emprestimos_membro   ON emprestimos (membro_id);
CREATE INDEX ix_emprestimos_abertos  ON emprestimos (vence_em) WHERE devolvido_em IS NULL;
-- Busca por metadados do livro (ex.: dados @> '{"genero":"ficção"}')
CREATE INDEX ix_livros_dados         ON livros USING GIN (dados);
-- Busca por título sem diferenciar maiúsculas/acentos comuns
CREATE INDEX ix_livros_titulo_lower  ON livros (lower(titulo));

-- ---------------------------------------------------------------------------
-- View: exemplares disponíveis para empréstimo agora.
-- ---------------------------------------------------------------------------
CREATE VIEW livros_disponiveis AS
SELECT
    l.id            AS livro_id,
    l.titulo,
    e.id            AS exemplar_id,
    e.codigo
FROM exemplares e
JOIN livros l ON l.id = e.livro_id
WHERE e.aposentado = false
  AND NOT EXISTS (
      SELECT 1 FROM emprestimos em
      WHERE em.exemplar_id = e.id AND em.devolvido_em IS NULL
  );

COMMIT;
