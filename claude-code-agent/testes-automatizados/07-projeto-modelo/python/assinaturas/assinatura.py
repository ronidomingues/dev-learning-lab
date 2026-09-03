"""A máquina de estados da assinatura.

Uma máquina de estados é o objeto mais recompensador de testar: o espaço de
casos é finito e enumerável, então dá para cobrir **todas** as transições —
as válidas e as proibidas — com `pytest.mark.parametrize`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import Enum

from .plano import Plano, proxima_cobranca


class Estado(str, Enum):
    ATIVA = "ativa"
    PAUSADA = "pausada"
    INADIMPLENTE = "inadimplente"
    CANCELADA = "cancelada"


class TransicaoInvalida(Exception):
    """Erro de domínio: essa mudança de estado não é permitida."""


MAX_TENTATIVAS = 3


@dataclass(slots=True)
class Assinatura:
    id: str
    cliente: str
    plano: Plano
    inicio: date
    proxima_cobranca: date
    estado: Estado = Estado.ATIVA
    tentativas_falhas: int = 0
    ciclos_pagos: int = 0
    historico: list[str] = field(default_factory=list)

    @classmethod
    def criar(cls, id: str, cliente: str, plano: Plano, hoje: date) -> Assinatura:
        return cls(
            id=id,
            cliente=cliente,
            plano=plano,
            inicio=hoje,
            proxima_cobranca=proxima_cobranca(hoje, plano.dias_ciclo),
        )

    # ---- consultas -------------------------------------------------------

    def esta_vencida(self, hoje: date) -> bool:
        """Vence **no** dia da próxima cobrança, não no dia seguinte."""
        return self.estado in (Estado.ATIVA, Estado.INADIMPLENTE) and hoje >= self.proxima_cobranca

    # ---- transições ------------------------------------------------------

    def pausar(self) -> None:
        if self.estado is not Estado.ATIVA:
            raise TransicaoInvalida(f"só dá para pausar assinatura ativa, está {self.estado.value}")
        self.estado = Estado.PAUSADA
        self.historico.append("pausada")

    def retomar(self, hoje: date) -> None:
        if self.estado is not Estado.PAUSADA:
            raise TransicaoInvalida(f"só dá para retomar assinatura pausada, está {self.estado.value}")
        self.estado = Estado.ATIVA
        # ao retomar, o ciclo recomeça de hoje: o cliente não paga pelo tempo pausado
        self.proxima_cobranca = proxima_cobranca(hoje, self.plano.dias_ciclo)
        self.historico.append("retomada")

    def cancelar(self) -> None:
        if self.estado is Estado.CANCELADA:
            raise TransicaoInvalida("assinatura já está cancelada")
        self.estado = Estado.CANCELADA
        self.historico.append("cancelada")

    def registrar_pagamento(self, hoje: date) -> None:
        if self.estado not in (Estado.ATIVA, Estado.INADIMPLENTE):
            raise TransicaoInvalida(f"não se cobra assinatura {self.estado.value}")
        self.estado = Estado.ATIVA
        self.tentativas_falhas = 0
        self.ciclos_pagos += 1
        self.proxima_cobranca = proxima_cobranca(hoje, self.plano.dias_ciclo)
        self.historico.append(f"pago em {hoje.isoformat()}")

    def registrar_falha(self) -> None:
        """Falha de cobrança. Na terceira, cancela — regra de negócio explícita."""
        if self.estado not in (Estado.ATIVA, Estado.INADIMPLENTE):
            raise TransicaoInvalida(f"não se cobra assinatura {self.estado.value}")
        self.tentativas_falhas += 1
        self.historico.append(f"falha {self.tentativas_falhas}")
        if self.tentativas_falhas >= MAX_TENTATIVAS:
            self.estado = Estado.CANCELADA
            self.historico.append("cancelada por inadimplência")
        else:
            self.estado = Estado.INADIMPLENTE
