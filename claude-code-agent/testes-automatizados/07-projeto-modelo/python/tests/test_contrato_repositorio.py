"""Teste de contrato: a MESMA bateria roda contra o fake e contra o real.

Este é o antídoto para o maior risco de usar dublês: o fake mentir. Se
`RepositorioMemoria` se comportar diferente de `RepositorioSQLite`, os testes
unitários passam e a produção quebra. Com uma suíte parametrizada pela
implementação, qualquer divergência aparece imediatamente.

Padrão em inglês: *contract test* / *verified fake*.
"""

from __future__ import annotations

from datetime import date, timedelta

import pytest

from assinaturas.assinatura import Assinatura, Estado
from assinaturas.plano import CATALOGO
from assinaturas.repositorio import RepositorioMemoria, RepositorioSQLite

HOJE = date(2026, 8, 12)


@pytest.fixture(params=["memoria", "sqlite"])
def repositorio(request):
    """Fixture parametrizada: cada teste abaixo roda DUAS vezes, uma por implementação."""
    if request.param == "memoria":
        yield RepositorioMemoria()
    else:
        r = RepositorioSQLite(":memory:")
        yield r
        r.fechar()


def nova(id: str, dias: int = 0, estado: Estado = Estado.ATIVA) -> Assinatura:
    a = Assinatura.criar(id, f"{id}@ex.br", CATALOGO["pro"], HOJE)
    a.proxima_cobranca = HOJE + timedelta(days=dias)
    a.estado = estado
    return a


def test_busca_devolve_none_para_id_desconhecido(repositorio):
    assert repositorio.buscar("fantasma") is None


def test_salvar_e_buscar_preserva_os_campos(repositorio):
    original = nova("a1")
    original.tentativas_falhas = 2
    original.ciclos_pagos = 7
    repositorio.salvar(original)

    lida = repositorio.buscar("a1")

    assert lida is not None
    assert (lida.id, lida.cliente, lida.plano.codigo) == ("a1", "a1@ex.br", "pro")
    assert (lida.estado, lida.tentativas_falhas, lida.ciclos_pagos) == (Estado.ATIVA, 2, 7)
    assert (lida.inicio, lida.proxima_cobranca) == (original.inicio, original.proxima_cobranca)


def test_salvar_duas_vezes_o_mesmo_id_nao_duplica(repositorio):
    repositorio.salvar(nova("a1"))
    repositorio.salvar(nova("a1"))
    assert len(repositorio.listar_vencidas(HOJE)) == 1


def test_vencidas_incluem_o_proprio_dia(repositorio):
    repositorio.salvar(nova("a1", dias=0))
    assert [a.id for a in repositorio.listar_vencidas(HOJE)] == ["a1"]


def test_vencidas_excluem_o_futuro(repositorio):
    repositorio.salvar(nova("a1", dias=1))
    assert repositorio.listar_vencidas(HOJE) == []


@pytest.mark.parametrize("estado", [Estado.PAUSADA, Estado.CANCELADA])
def test_vencidas_excluem_pausada_e_cancelada(repositorio, estado):
    repositorio.salvar(nova("a1", dias=-10, estado=estado))
    assert repositorio.listar_vencidas(HOJE) == []


def test_vencidas_incluem_inadimplente(repositorio):
    repositorio.salvar(nova("a1", dias=-10, estado=Estado.INADIMPLENTE))
    assert len(repositorio.listar_vencidas(HOJE)) == 1


def test_vencidas_vem_ordenadas_por_id(repositorio):
    for id_ in ("c", "a", "b"):
        repositorio.salvar(nova(id_))
    assert [a.id for a in repositorio.listar_vencidas(HOJE)] == ["a", "b", "c"]


def test_repositorio_vazio_devolve_lista_vazia_nao_none(repositorio):
    assert repositorio.listar_vencidas(HOJE) == []
