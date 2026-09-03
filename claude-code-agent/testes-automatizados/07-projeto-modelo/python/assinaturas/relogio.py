"""O tempo como dependência injetada.

Motivo: `date.today()` chamado no meio da regra de negócio torna o código
**intestável** — o resultado do teste passa a depender do dia em que ele roda.
Em vez de congelar o tempo com bibliotecas de macaco-patch (`freezegun`),
o tempo aqui é um **colaborador explícito**: quem chama decide qual relógio usar.

Isso é injeção de dependência (DI) na sua forma mais simples: um parâmetro.
"""

from __future__ import annotations

from datetime import date
from typing import Protocol


class Relogio(Protocol):
    """Contrato mínimo: sei dizer que dia é hoje."""

    def hoje(self) -> date: ...


class RelogioDoSistema:
    """Implementação de produção. A única que toca o mundo real."""

    def hoje(self) -> date:
        return date.today()


class RelogioFixo:
    """Dublê de teste (stub) — devolve sempre a mesma data.

    Vive no pacote de produção **de propósito**: quem consome esta biblioteca
    precisa dele para testar o próprio código. Trade-off: um punhado de linhas
    de código de teste vai para o pacote publicado. Vale a pena.
    """

    def __init__(self, data: date) -> None:
        self._data = data

    def hoje(self) -> date:
        return self._data

    def avancar(self, dias: int) -> None:
        """Permite simular a passagem do tempo dentro de um mesmo teste."""
        from datetime import timedelta

        self._data = self._data + timedelta(days=dias)
