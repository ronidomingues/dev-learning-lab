"""Gestão de assinaturas recorrentes — projeto-modelo de testes automatizados.

Camadas (de dentro para fora):

    dinheiro, plano, assinatura   ← domínio puro: zero I/O, 100% testável
    relogio, gateway, repositorio ← contratos (Protocol) + implementações + dublês
    servico                       ← caso de uso, recebe tudo por injeção
    cli                           ← borda: só monta os objetos e imprime
"""

from .assinatura import Assinatura, Estado, TransicaoInvalida
from .dinheiro import Dinheiro, ValorInvalido
from .gateway import Cobranca, GatewayFalso, GatewayHttp, GatewayQueExplode
from .plano import CATALOGO, Cupom, CupomInvalido, Plano, proxima_cobranca
from .relogio import RelogioDoSistema, RelogioFixo
from .repositorio import RepositorioMemoria, RepositorioSQLite
from .servico import NotificadorEspiao, Relatorio, ServicoRenovacao

__all__ = [
    "Assinatura",
    "CATALOGO",
    "Cobranca",
    "Cupom",
    "CupomInvalido",
    "Dinheiro",
    "Estado",
    "GatewayFalso",
    "GatewayHttp",
    "GatewayQueExplode",
    "NotificadorEspiao",
    "Plano",
    "Relatorio",
    "RelogioDoSistema",
    "RelogioFixo",
    "RepositorioMemoria",
    "RepositorioSQLite",
    "ServicoRenovacao",
    "TransicaoInvalida",
    "ValorInvalido",
    "proxima_cobranca",
]
__version__ = "1.0.0"
