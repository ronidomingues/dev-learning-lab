"""O caso de uso: renovar as assinaturas vencidas.

Este é o objeto que **orquestra** — e é o teste dele que dá mais retorno,
porque cobre a regra de negócio inteira sem tocar em rede, banco ou relógio.
Todas as quatro dependências entram pelo construtor.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from .assinatura import Assinatura
from .dinheiro import ZERO, Dinheiro
from .gateway import Gateway
from .plano import Cupom, CupomInvalido
from .relogio import Relogio
from .repositorio import Repositorio


class Notificador(Protocol):
    def avisar(self, cliente: str, assunto: str, corpo: str) -> None: ...


@dataclass
class NotificadorEspiao:
    """**Spy**: registra as chamadas para o teste inspecioná-las depois."""

    mensagens: list[tuple[str, str, str]] = field(default_factory=list)

    def avisar(self, cliente: str, assunto: str, corpo: str) -> None:
        self.mensagens.append((cliente, assunto, corpo))

    def assuntos_de(self, cliente: str) -> list[str]:
        return [a for c, a, _ in self.mensagens if c == cliente]


@dataclass(frozen=True, slots=True)
class Relatorio:
    cobradas: int = 0
    recusadas: int = 0
    canceladas: int = 0
    com_erro: int = 0
    total_arrecadado: Dinheiro = ZERO

    def __str__(self) -> str:
        return (
            f"{self.cobradas} cobradas ({self.total_arrecadado}), "
            f"{self.recusadas} recusadas, {self.canceladas} canceladas, "
            f"{self.com_erro} com erro"
        )


class ServicoRenovacao:
    def __init__(
        self,
        repositorio: Repositorio,
        gateway: Gateway,
        relogio: Relogio,
        notificador: Notificador,
        cupons: dict[str, Cupom] | None = None,
    ) -> None:
        self._repo = repositorio
        self._gateway = gateway
        self._relogio = relogio
        self._notificador = notificador
        self._cupons = cupons or {}

    def preco_a_cobrar(self, assinatura: Assinatura, codigo_cupom: str | None = None) -> Dinheiro:
        preco = assinatura.plano.preco
        if not codigo_cupom:
            return preco
        cupom = self._cupons.get(codigo_cupom)
        if cupom is None:
            raise CupomInvalido(f"cupom {codigo_cupom} não existe")
        return cupom.preco_com_desconto(preco, self._relogio.hoje(), assinatura.ciclos_pagos)

    def renovar_vencidas(self) -> Relatorio:
        hoje = self._relogio.hoje()
        cobradas = recusadas = canceladas = com_erro = 0
        arrecadado = ZERO

        for assinatura in self._repo.listar_vencidas(hoje):
            try:
                resultado = self._gateway.cobrar(assinatura.cliente, assinatura.plano.preco)
            except Exception as erro:
                # Falha de infraestrutura **não** conta como falha do cliente:
                # não incrementa tentativas, não cancela ninguém. Tenta de novo amanhã.
                com_erro += 1
                self._notificador.avisar(
                    assinatura.cliente,
                    "Não conseguimos processar sua cobrança hoje",
                    f"Erro técnico: {erro}. Tentaremos novamente.",
                )
                continue

            if resultado.aprovada:
                assinatura.registrar_pagamento(hoje)
                cobradas += 1
                arrecadado = arrecadado + assinatura.plano.preco
                self._notificador.avisar(
                    assinatura.cliente,
                    "Pagamento confirmado",
                    f"{assinatura.plano.nome}: {assinatura.plano.preco} "
                    f"(transação {resultado.id_transacao})",
                )
            else:
                assinatura.registrar_falha()
                recusadas += 1
                from .assinatura import Estado

                if assinatura.estado is Estado.CANCELADA:
                    canceladas += 1
                    self._notificador.avisar(
                        assinatura.cliente,
                        "Assinatura cancelada",
                        f"Após {assinatura.tentativas_falhas} tentativas: {resultado.motivo}",
                    )
                else:
                    self._notificador.avisar(
                        assinatura.cliente,
                        "Pagamento recusado",
                        f"Tentativa {assinatura.tentativas_falhas}: {resultado.motivo}",
                    )

            self._repo.salvar(assinatura)

        return Relatorio(cobradas, recusadas, canceladas, com_erro, arrecadado)
