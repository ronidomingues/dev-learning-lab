"""Fixtures dos testes.

Cada teste ganha um banco novo em diretório temporário. Testes que compartilham
banco falham em ordem aleatória — e o pytest embaralha mais do que se imagina.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))       # permite `from nucleo import ...` sem instalar

from nucleo import config, seed  # noqa: E402


@pytest.fixture()
def banco(tmp_path: Path) -> Path:
    """Banco populado, pequeno e rápido. Hash barato: teste não é produção."""
    caminho = tmp_path / "teste.db"
    seed.popular(caminho, dias=120, pedidos=300, iteracoes_hash=100_000, semente=7)
    return caminho


@pytest.fixture()
def cfg(banco: Path) -> config.Config:
    return config.carregar({"PAINEL_BANCO": str(banco), "PAINEL_HASH_ITER": "100000"})


@pytest.fixture()
def banco_vazio_em_governo(monkeypatch, tmp_path: Path) -> Path:
    """Banco em que o segmento 'Governo' existe no cadastro mas não tem pedido.

    Serve para exercitar o estado vazio da interface de forma DETERMINÍSTICA —
    'provavelmente não vai ter linha' não é teste, é sorte.
    """
    from nucleo.db import transacao

    caminho = tmp_path / "vazio.db"
    seed.popular(caminho, dias=120, pedidos=300, iteracoes_hash=100_000, semente=7)
    with transacao(caminho) as con:
        con.execute(
            "DELETE FROM pedidos WHERE cliente_id IN "
            "(SELECT id FROM clientes WHERE segmento = 'Governo')"
        )
    monkeypatch.setenv("PAINEL_BANCO", str(caminho))
    monkeypatch.setenv("PAINEL_HASH_ITER", "100000")
    return caminho
