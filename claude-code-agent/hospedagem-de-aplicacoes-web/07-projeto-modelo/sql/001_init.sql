-- Esquema do encurtador.
--
-- Decisões e o porquê de cada uma:
--   bigserial      → int8 vai até 9,2 quintilhões; int4 estoura em 2,1 bilhões,
--                    e "acabaram os IDs" já derrubou sistemas famosos.
--   slug UNIQUE    → a fonte da verdade sobre colisão é o banco, não o código.
--   citext não     → mantemos case-sensitive de propósito: "aB3" e "Ab3" são links diferentes,
--                    é o que dobra o espaço de chaves.
--   timestamptz    → SEMPRE com fuso. `timestamp` sem fuso é uma armadilha em sistema global.
--   cliques bigint → contador com default 0 e NOT NULL: nada de NULL em contador.

CREATE TABLE IF NOT EXISTS link (
  id        bigserial   PRIMARY KEY,
  slug      text        NOT NULL UNIQUE,
  destino   text        NOT NULL,
  cliques   bigint      NOT NULL DEFAULT 0,
  criado_em timestamptz NOT NULL DEFAULT now(),

  CONSTRAINT link_slug_tamanho   CHECK (char_length(slug) BETWEEN 3 AND 32),
  CONSTRAINT link_destino_http   CHECK (destino ~* '^https?://')
);

-- Índice para o ranking de /api/stats. Sem ele, o ORDER BY cliques DESC
-- faz varredura sequencial + ordenação a cada chamada.
CREATE INDEX IF NOT EXISTS idx_link_cliques ON link (cliques DESC, id DESC);

-- Índice para relatórios por período.
CREATE INDEX IF NOT EXISTS idx_link_criado_em ON link (criado_em DESC);
