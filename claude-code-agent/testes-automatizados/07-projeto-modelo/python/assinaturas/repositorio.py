"""Persistência: um contrato, duas implementações.

`RepositorioMemoria` é usado pelos testes unitários (rápido, sem I/O).
`RepositorioSQLite` é o de produção e tem seus **próprios** testes de
integração. A mesma bateria de testes de contrato roda contra os dois —
é assim que se garante que o fake não mentiu (ver `tests/test_contrato_repositorio.py`).
"""

from __future__ import annotations

import sqlite3
from datetime import date
from typing import Iterable, Protocol

from .assinatura import Assinatura, Estado
from .plano import CATALOGO


class Repositorio(Protocol):
    def salvar(self, assinatura: Assinatura) -> None: ...
    def buscar(self, id: str) -> Assinatura | None: ...
    def listar_vencidas(self, hoje: date) -> list[Assinatura]: ...


class RepositorioMemoria:
    """Fake em memória. Guarda os objetos, não cópias — cuidado explicado abaixo.

    Armadilha conhecida: como guardamos referências, mutar a assinatura fora do
    repositório "salva" sem chamar `salvar()`. Isso faz o fake ser **mais
    permissivo** que o SQLite, e um teste pode passar aqui e falhar em produção.
    Por isso a suíte de contrato existe.
    """

    def __init__(self, assinaturas: Iterable[Assinatura] = ()) -> None:
        self._dados: dict[str, Assinatura] = {a.id: a for a in assinaturas}

    def salvar(self, assinatura: Assinatura) -> None:
        self._dados[assinatura.id] = assinatura

    def buscar(self, id: str) -> Assinatura | None:
        return self._dados.get(id)

    def listar_vencidas(self, hoje: date) -> list[Assinatura]:
        return sorted(
            (a for a in self._dados.values() if a.esta_vencida(hoje)),
            key=lambda a: a.id,
        )


ESQUEMA = """
CREATE TABLE IF NOT EXISTS assinaturas (
    id                TEXT PRIMARY KEY,
    cliente           TEXT NOT NULL,
    plano             TEXT NOT NULL,
    inicio            TEXT NOT NULL,
    proxima_cobranca  TEXT NOT NULL,
    estado            TEXT NOT NULL,
    tentativas_falhas INTEGER NOT NULL DEFAULT 0,
    ciclos_pagos      INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_vencimento
    ON assinaturas (proxima_cobranca, estado);
"""


class RepositorioSQLite:
    """Implementação real. `caminho=":memory:"` serve para teste de integração."""

    def __init__(self, caminho: str = "assinaturas.db") -> None:
        self._con = sqlite3.connect(caminho)
        self._con.row_factory = sqlite3.Row
        self._con.executescript(ESQUEMA)

    def fechar(self) -> None:
        self._con.close()

    def __enter__(self) -> RepositorioSQLite:
        return self

    def __exit__(self, *_exc: object) -> None:
        self.fechar()

    def salvar(self, assinatura: Assinatura) -> None:
        self._con.execute(
            """
            INSERT INTO assinaturas
                (id, cliente, plano, inicio, proxima_cobranca, estado,
                 tentativas_falhas, ciclos_pagos)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                cliente=excluded.cliente,
                plano=excluded.plano,
                inicio=excluded.inicio,
                proxima_cobranca=excluded.proxima_cobranca,
                estado=excluded.estado,
                tentativas_falhas=excluded.tentativas_falhas,
                ciclos_pagos=excluded.ciclos_pagos
            """,
            (
                assinatura.id,
                assinatura.cliente,
                assinatura.plano.codigo,
                assinatura.inicio.isoformat(),
                assinatura.proxima_cobranca.isoformat(),
                assinatura.estado.value,
                assinatura.tentativas_falhas,
                assinatura.ciclos_pagos,
            ),
        )
        self._con.commit()

    def _hidratar(self, linha: sqlite3.Row) -> Assinatura:
        return Assinatura(
            id=linha["id"],
            cliente=linha["cliente"],
            plano=CATALOGO[linha["plano"]],
            inicio=date.fromisoformat(linha["inicio"]),
            proxima_cobranca=date.fromisoformat(linha["proxima_cobranca"]),
            estado=Estado(linha["estado"]),
            tentativas_falhas=linha["tentativas_falhas"],
            ciclos_pagos=linha["ciclos_pagos"],
        )

    def buscar(self, id: str) -> Assinatura | None:
        linha = self._con.execute("SELECT * FROM assinaturas WHERE id = ?", (id,)).fetchone()
        return self._hidratar(linha) if linha else None

    def listar_vencidas(self, hoje: date) -> list[Assinatura]:
        linhas = self._con.execute(
            """
            SELECT * FROM assinaturas
             WHERE proxima_cobranca <= ?
               AND estado IN ('ativa', 'inadimplente')
             ORDER BY id
            """,
            (hoje.isoformat(),),
        ).fetchall()
        return [self._hidratar(linha) for linha in linhas]
