"""Fixtures compartilhadas.

`conftest.py` é descoberto automaticamente pelo pytest: as fixtures aqui ficam
visíveis para todos os testes desta pasta e das subpastas, **sem import**.
Isso é conveniente e perigoso — fixture usada por 40 testes e definida num
arquivo que ninguém abre é a maior fonte de "por que esse teste falhou?".
Regra do projeto: fixture só sobe para o `conftest.py` quando é usada por
**dois ou mais arquivos** de teste.
"""

from __future__ import annotations

from datetime import date

import pytest

from assinaturas.assinatura import Assinatura
from assinaturas.gateway import GatewayFalso
from assinaturas.plano import CATALOGO, Cupom
from assinaturas.relogio import RelogioFixo
from assinaturas.repositorio import RepositorioMemoria
from assinaturas.servico import NotificadorEspiao, ServicoRenovacao

HOJE = date(2026, 8, 12)


@pytest.fixture
def hoje() -> date:
    """Data fixa do projeto. Nenhum teste chama `date.today()`."""
    return HOJE


@pytest.fixture
def relogio(hoje: date) -> RelogioFixo:
    return RelogioFixo(hoje)


@pytest.fixture
def gateway() -> GatewayFalso:
    return GatewayFalso()


@pytest.fixture
def notificador() -> NotificadorEspiao:
    return NotificadorEspiao()


@pytest.fixture
def assinatura_vencida(hoje: date) -> Assinatura:
    """Assinatura Pro cujo vencimento é exatamente hoje."""
    a = Assinatura.criar("a1", "ana@exemplo.br", CATALOGO["pro"], hoje)
    a.proxima_cobranca = hoje
    return a


@pytest.fixture
def cupons(hoje: date) -> dict[str, Cupom]:
    return {
        "BEMVINDO10": Cupom("BEMVINDO10", 10, validade=date(2026, 12, 31), usos_maximos=1),
        "EXPIRADO": Cupom("EXPIRADO", 50, validade=date(2026, 8, 11), usos_maximos=99),
        "CORTESIA": Cupom("CORTESIA", 100, validade=date(2026, 12, 31), usos_maximos=3),
    }


@pytest.fixture
def servico(
    assinatura_vencida: Assinatura,
    gateway: GatewayFalso,
    relogio: RelogioFixo,
    notificador: NotificadorEspiao,
    cupons: dict[str, Cupom],
) -> ServicoRenovacao:
    """Serviço montado com dublês. Nenhuma dependência real — roda em microssegundos."""
    repo = RepositorioMemoria([assinatura_vencida])
    return ServicoRenovacao(repo, gateway, relogio, notificador, cupons)
