"""Persistência em SQLite.

Decisões:
- SQLite para o projeto rodar sem nenhum serviço externo. A forma do código é a
  mesma com Postgres; só muda o driver.
- Toda consulta é PARAMETRIZADA. Nunca formatamos SQL com f-string, porque parte
  dos valores vem, em última instância, de texto que um modelo escreveu a partir
  de algo que um usuário digitou.
- `emprestar` e `devolver` são transações com condição na cláusula WHERE, para que
  duas chamadas concorrentes não emprestem o mesmo exemplar duas vezes. Esse é o
  mesmo raciocínio de travamento otimista.
"""
from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import date, timedelta
from typing import Iterator

DIAS_DE_EMPRESTIMO = 14

ESQUEMA = """
CREATE TABLE IF NOT EXISTS livros (
    isbn        TEXT PRIMARY KEY,
    titulo      TEXT NOT NULL,
    autor       TEXT NOT NULL,
    ano         INTEGER NOT NULL,
    exemplares  INTEGER NOT NULL CHECK (exemplares >= 0),
    disponiveis INTEGER NOT NULL CHECK (disponiveis >= 0 AND disponiveis <= exemplares)
);

CREATE TABLE IF NOT EXISTS emprestimos (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    isbn        TEXT NOT NULL REFERENCES livros(isbn),
    leitor      TEXT NOT NULL,
    emprestado  TEXT NOT NULL,
    devolver_ate TEXT NOT NULL,
    devolvido   TEXT
);

CREATE INDEX IF NOT EXISTS idx_emprestimos_abertos
    ON emprestimos(isbn, leitor) WHERE devolvido IS NULL;
"""

SEMENTE = [
    ("9788535902778", "Grande Sertão: Veredas", "João Guimarães Rosa", 1956, 3, 3),
    ("9788535914849", "Vidas Secas", "Graciliano Ramos", 1938, 2, 2),
    ("9788525406958", "Memórias Póstumas de Brás Cubas", "Machado de Assis", 1881, 4, 4),
    ("9788573264234", "O Cortiço", "Aluísio Azevedo", 1890, 2, 2),
    ("9788576570271", "A Hora da Estrela", "Clarice Lispector", 1977, 1, 1),
    ("9788535911992", "Capitães da Areia", "Jorge Amado", 1937, 3, 3),
]


@contextmanager
def conectar(caminho: str, somente_leitura: bool = False) -> Iterator[sqlite3.Connection]:
    """Abre uma conexão. Em modo somente-leitura a garantia é do driver, não do código."""
    if somente_leitura:
        con = sqlite3.connect(f"file:{caminho}?mode=ro", uri=True)
    else:
        con = sqlite3.connect(caminho, isolation_level=None)
        con.execute("PRAGMA foreign_keys = ON")
    con.row_factory = sqlite3.Row
    try:
        yield con
    finally:
        con.close()


def criar_esquema(caminho: str, com_semente: bool = True) -> None:
    with conectar(caminho) as con:
        con.executescript(ESQUEMA)
        if com_semente:
            con.executemany(
                "INSERT OR IGNORE INTO livros VALUES (?, ?, ?, ?, ?, ?)", SEMENTE
            )


def buscar(caminho: str, termo: str, limite: int) -> list[dict]:
    """Busca por título ou autor. `ORDER BY` fixo: ordem determinística."""
    padrao = f"%{termo}%"
    with conectar(caminho, somente_leitura=True) as con:
        linhas = con.execute(
            "SELECT isbn, titulo, autor, ano, exemplares, disponiveis "
            "FROM livros WHERE titulo LIKE ? OR autor LIKE ? "
            "ORDER BY titulo LIMIT ?",
            (padrao, padrao, limite + 1),  # +1 para detectar truncamento
        ).fetchall()
    return [dict(l) for l in linhas]


def obter(caminho: str, isbn: str) -> dict | None:
    with conectar(caminho, somente_leitura=True) as con:
        linha = con.execute(
            "SELECT isbn, titulo, autor, ano, exemplares, disponiveis "
            "FROM livros WHERE isbn = ?",
            (isbn,),
        ).fetchone()
    return dict(linha) if linha else None


def emprestar(caminho: str, isbn: str, leitor: str) -> dict:
    """Empresta um exemplar.

    O decremento acontece com `AND disponiveis > 0` na cláusula WHERE: se duas
    chamadas concorrerem pelo último exemplar, a segunda afeta zero linhas e nós
    detectamos, em vez de deixar `disponiveis` ficar negativo.
    """
    hoje = date.today()
    ate = hoje + timedelta(days=DIAS_DE_EMPRESTIMO)
    with conectar(caminho) as con:
        con.execute("BEGIN IMMEDIATE")
        try:
            existe = con.execute(
                "SELECT titulo FROM livros WHERE isbn = ?", (isbn,)
            ).fetchone()
            if existe is None:
                con.execute("ROLLBACK")
                return {"ok": False, "motivo": "inexistente"}

            ja = con.execute(
                "SELECT id FROM emprestimos WHERE isbn = ? AND leitor = ? AND devolvido IS NULL",
                (isbn, leitor),
            ).fetchone()
            if ja is not None:
                con.execute("ROLLBACK")
                return {"ok": False, "motivo": "ja_emprestado_para_este_leitor"}

            cur = con.execute(
                "UPDATE livros SET disponiveis = disponiveis - 1 "
                "WHERE isbn = ? AND disponiveis > 0",
                (isbn,),
            )
            if cur.rowcount == 0:
                con.execute("ROLLBACK")
                return {"ok": False, "motivo": "sem_exemplar"}

            con.execute(
                "INSERT INTO emprestimos (isbn, leitor, emprestado, devolver_ate) "
                "VALUES (?, ?, ?, ?)",
                (isbn, leitor, hoje.isoformat(), ate.isoformat()),
            )
            con.execute("COMMIT")
        except Exception:
            con.execute("ROLLBACK")
            raise
    return {
        "ok": True,
        "isbn": isbn,
        "titulo": existe["titulo"],
        "leitor": leitor,
        "devolver_ate": ate.isoformat(),
    }


def devolver(caminho: str, isbn: str, leitor: str) -> dict:
    with conectar(caminho) as con:
        con.execute("BEGIN IMMEDIATE")
        try:
            cur = con.execute(
                "UPDATE emprestimos SET devolvido = ? "
                "WHERE id = (SELECT id FROM emprestimos "
                "            WHERE isbn = ? AND leitor = ? AND devolvido IS NULL "
                "            ORDER BY id LIMIT 1)",
                (date.today().isoformat(), isbn, leitor),
            )
            if cur.rowcount == 0:
                con.execute("ROLLBACK")
                return {"ok": False, "motivo": "sem_emprestimo_aberto"}
            con.execute(
                "UPDATE livros SET disponiveis = disponiveis + 1 "
                "WHERE isbn = ? AND disponiveis < exemplares",
                (isbn,),
            )
            con.execute("COMMIT")
        except Exception:
            con.execute("ROLLBACK")
            raise
    return {"ok": True, "isbn": isbn, "leitor": leitor}


def emprestimos_do_leitor(caminho: str, leitor: str, limite: int) -> list[dict]:
    with conectar(caminho, somente_leitura=True) as con:
        linhas = con.execute(
            "SELECT e.isbn, l.titulo, e.emprestado, e.devolver_ate "
            "FROM emprestimos e JOIN livros l ON l.isbn = e.isbn "
            "WHERE e.leitor = ? AND e.devolvido IS NULL "
            "ORDER BY e.devolver_ate LIMIT ?",
            (leitor, limite),
        ).fetchall()
    return [dict(l) for l in linhas]


def estatisticas(caminho: str) -> dict:
    with conectar(caminho, somente_leitura=True) as con:
        titulos = con.execute("SELECT COUNT(*) AS n FROM livros").fetchone()["n"]
        exemplares = con.execute(
            "SELECT COALESCE(SUM(exemplares), 0) AS n FROM livros"
        ).fetchone()["n"]
        abertos = con.execute(
            "SELECT COUNT(*) AS n FROM emprestimos WHERE devolvido IS NULL"
        ).fetchone()["n"]
        atrasados = con.execute(
            "SELECT COUNT(*) AS n FROM emprestimos "
            "WHERE devolvido IS NULL AND devolver_ate < ?",
            (date.today().isoformat(),),
        ).fetchone()["n"]
    return {
        "titulos": titulos,
        "exemplares": exemplares,
        "emprestimos_abertos": abertos,
        "atrasados": atrasados,
    }
