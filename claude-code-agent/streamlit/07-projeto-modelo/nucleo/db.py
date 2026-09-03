"""Conexão e esquema do banco (SQLite).

Duas decisões que valem para qualquer banco, não só SQLite:

1. **Migração versionada.** O esquema evolui por passos numerados guardados na
   própria tabela `schema_versao`. Rodar `migrar()` duas vezes não faz nada na
   segunda. Isso é o mínimo para uma app que vai para produção.
2. **Dinheiro em inteiro.** Todo valor monetário é guardado em *centavos*, num
   INTEGER. `float` não representa 0,1 exatamente; somar 1.000 pedidos em float
   erra centavos, e erro de centavo em relatório financeiro custa reunião.
"""

from __future__ import annotations

import sqlite3
import threading
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

# SQLite exige cuidado com threads: o Streamlit atende cada sessão em uma thread
# do servidor. Guardamos uma conexão POR THREAD em vez de compartilhar uma só.
_local = threading.local()


def _conectar(caminho: Path) -> sqlite3.Connection:
    con = sqlite3.connect(caminho, check_same_thread=False, timeout=10.0)
    con.row_factory = sqlite3.Row          # linhas viram dict-like: linha["nome"]
    con.execute("PRAGMA foreign_keys = ON")  # SQLite desliga FK por padrão (!)
    con.execute("PRAGMA journal_mode = WAL")  # leitores não bloqueiam o escritor
    con.execute("PRAGMA busy_timeout = 5000")
    return con


def conexao(caminho: Path) -> sqlite3.Connection:
    """Devolve a conexão desta thread, criando na primeira chamada."""
    chave = f"con::{caminho}"
    con = getattr(_local, chave, None)
    if con is None:
        con = _conectar(caminho)
        setattr(_local, chave, con)
    return con


@contextmanager
def transacao(caminho: Path) -> Iterator[sqlite3.Connection]:
    """Bloco atômico: ou tudo grava, ou nada grava."""
    con = conexao(caminho)
    try:
        yield con
        con.commit()
    except Exception:
        con.rollback()
        raise


# --------------------------------------------------------------------------
# Migrações. Cada item da lista é um passo; a posição é o número da versão.
# NUNCA edite um passo já publicado — acrescente outro no fim.
# --------------------------------------------------------------------------
MIGRACOES: list[str] = [
    # 1
    """
    CREATE TABLE usuarios (
        id          INTEGER PRIMARY KEY,
        email       TEXT NOT NULL UNIQUE,
        nome        TEXT NOT NULL,
        papel       TEXT NOT NULL CHECK (papel IN ('admin','analista','leitor')),
        senha_hash  BLOB NOT NULL,
        salt        BLOB NOT NULL,
        iteracoes   INTEGER NOT NULL,
        ativo       INTEGER NOT NULL DEFAULT 1,
        criado_em   TEXT NOT NULL
    );
    CREATE TABLE clientes (
        id        INTEGER PRIMARY KEY,
        nome      TEXT NOT NULL,
        segmento  TEXT NOT NULL,
        uf        TEXT NOT NULL,
        criado_em TEXT NOT NULL
    );
    CREATE TABLE produtos (
        id             INTEGER PRIMARY KEY,
        nome           TEXT NOT NULL,
        categoria      TEXT NOT NULL,
        preco_centavos INTEGER NOT NULL CHECK (preco_centavos > 0)
    );
    CREATE TABLE pedidos (
        id             INTEGER PRIMARY KEY,
        cliente_id     INTEGER NOT NULL REFERENCES clientes(id),
        produto_id     INTEGER NOT NULL REFERENCES produtos(id),
        quantidade     INTEGER NOT NULL CHECK (quantidade > 0),
        valor_centavos INTEGER NOT NULL CHECK (valor_centavos >= 0),
        status         TEXT NOT NULL CHECK (status IN ('rascunho','confirmado','faturado','cancelado')),
        canal          TEXT NOT NULL,
        data           TEXT NOT NULL
    );
    CREATE INDEX idx_pedidos_data   ON pedidos(data);
    CREATE INDEX idx_pedidos_status ON pedidos(status);
    CREATE TABLE auditoria (
        id      INTEGER PRIMARY KEY,
        quando  TEXT NOT NULL,
        ator    TEXT NOT NULL,
        acao    TEXT NOT NULL,
        detalhe TEXT NOT NULL
    );
    """,
    # 2 — exemplo de evolução de esquema sem quebrar o que já existe
    """
    ALTER TABLE clientes ADD COLUMN observacao TEXT NOT NULL DEFAULT '';
    """,
]


def versao_atual(con: sqlite3.Connection) -> int:
    con.execute("CREATE TABLE IF NOT EXISTS schema_versao (versao INTEGER NOT NULL)")
    linha = con.execute("SELECT MAX(versao) AS v FROM schema_versao").fetchone()
    return linha["v"] or 0


def migrar(caminho: Path) -> int:
    """Aplica as migrações pendentes. Devolve a versão final. Idempotente."""
    with transacao(caminho) as con:
        atual = versao_atual(con)
        for numero, script in enumerate(MIGRACOES, start=1):
            if numero <= atual:
                continue
            con.executescript(script)
            con.execute("INSERT INTO schema_versao (versao) VALUES (?)", (numero,))
        return len(MIGRACOES)
