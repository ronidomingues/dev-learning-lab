"""Configuração vinda do ambiente.

Por que um módulo só para isto: o servidor precisa ser configurável sem editar
código (o host lança o processo com `env`), e o teste precisa apontar para um
banco temporário sem tocar no de verdade.
"""
from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    caminho_db: str
    nivel_log: str
    max_linhas: int

    @staticmethod
    def do_ambiente() -> "Config":
        try:
            max_linhas = int(os.environ.get("BIBLIOTECA_MAX_LINHAS", "25"))
        except ValueError:
            max_linhas = 25
        # Teto do teto: nem o operador pode configurar algo que estoure o contexto.
        max_linhas = max(1, min(max_linhas, 100))
        return Config(
            caminho_db=os.environ.get("BIBLIOTECA_DB", "biblioteca.db"),
            nivel_log=os.environ.get("BIBLIOTECA_LOG", "INFO").upper(),
            max_linhas=max_linhas,
        )
