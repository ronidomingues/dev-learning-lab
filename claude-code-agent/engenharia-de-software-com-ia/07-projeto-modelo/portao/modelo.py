"""Tipos compartilhados por todas as regras.

Uma regra recebe um `Diff` e devolve um `Resultado`. Nada mais.
Esse contrato estreito é o que permite acrescentar regra nova sem
tocar em nenhuma outra parte do programa.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Severidade(str, Enum):
    """Severidade de um achado.

    BLOQUEIA reprova o portão; AVISA aparece no relatório e não reprova.
    A distinção existe porque um portão que reprova por tudo é desligado
    na primeira semana — e aí não há portão nenhum.
    """

    BLOQUEIA = "bloqueia"
    AVISA = "avisa"


@dataclass(frozen=True)
class Achado:
    arquivo: str
    linha: int | None
    mensagem: str
    severidade: Severidade = Severidade.BLOQUEIA
    detalhe: str = ""

    def como_dict(self) -> dict:
        return {
            "arquivo": self.arquivo,
            "linha": self.linha,
            "mensagem": self.mensagem,
            "severidade": self.severidade.value,
            "detalhe": self.detalhe,
        }


@dataclass
class Resultado:
    regra: str
    achados: list[Achado] = field(default_factory=list)
    pulada: bool = False
    motivo_pulada: str = ""

    @property
    def bloqueios(self) -> list[Achado]:
        return [a for a in self.achados if a.severidade is Severidade.BLOQUEIA]

    @property
    def avisos(self) -> list[Achado]:
        return [a for a in self.achados if a.severidade is Severidade.AVISA]

    @property
    def aprovado(self) -> bool:
        return not self.bloqueios

    def como_dict(self) -> dict:
        return {
            "regra": self.regra,
            "aprovado": self.aprovado,
            "pulada": self.pulada,
            "motivo_pulada": self.motivo_pulada,
            "achados": [a.como_dict() for a in self.achados],
        }
