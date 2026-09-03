-- Executado UMA VEZ, no primeiro boot do contêiner do Postgres.
-- Se voce alterar este arquivo depois, precisa recriar o volume:
--   docker compose down -v && docker compose up -d      (⚠️ apaga os dados)

CREATE TABLE IF NOT EXISTS pedidos (
    -- pedido_id vem de fora (do sistema que chama). E a chave de idempotencia:
    -- e por causa deste UNIQUE que reenviar o mesmo webhook nao duplica nada.
    pedido_id    TEXT PRIMARY KEY,
    cliente      TEXT        NOT NULL,
    valor        NUMERIC(12,2) NOT NULL CHECK (valor > 0),
    itens        JSONB       NOT NULL,
    recebido_em  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- O relatorio filtra por janela de tempo; sem indice isso vira varredura completa.
CREATE INDEX IF NOT EXISTS idx_pedidos_recebido_em ON pedidos (recebido_em DESC);

CREATE TABLE IF NOT EXISTS erros (
    id            BIGSERIAL PRIMARY KEY,
    workflow_nome TEXT,
    execucao_id   TEXT,
    execucao_url  TEXT,
    ultimo_no     TEXT,
    mensagem      TEXT,
    quando        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
