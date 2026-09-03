"""Gateway de pagamento: o contrato e seus dublês.

Este é o ponto do sistema que **não pode** ser exercitado em teste unitário:
cobrar de verdade custa dinheiro, exige rede e é irreversível. Então o
definimos como um `Protocol` e escrevemos implementações falsas para os testes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from .dinheiro import Dinheiro


@dataclass(frozen=True, slots=True)
class Cobranca:
    aprovada: bool
    id_transacao: str
    motivo: str | None = None


class Gateway(Protocol):
    def cobrar(self, cliente: str, valor: Dinheiro) -> Cobranca: ...


class GatewayHttp:
    """Implementação real (esqueleto). Só é exercitada em teste de integração.

    Deixada deliberadamente magra: toda a lógica de decisão vive em
    `servico.py`, que é testável. O que sobra aqui é I/O — e I/O sem lógica
    é o tipo de código que se pode cobrir com um único teste de integração.
    """

    def __init__(self, base_url: str, token: str, timeout: float = 5.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.timeout = timeout

    def cobrar(self, cliente: str, valor: Dinheiro) -> Cobranca:  # pragma: no cover
        import json
        import urllib.request

        corpo = json.dumps({"cliente": cliente, "centavos": valor.centavos}).encode()
        req = urllib.request.Request(
            f"{self.base_url}/cobrancas",
            data=corpo,
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.token}"},
        )
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            dados = json.load(resp)
        return Cobranca(
            aprovada=bool(dados["aprovada"]),
            id_transacao=str(dados["id"]),
            motivo=dados.get("motivo"),
        )


@dataclass
class GatewayFalso:
    """**Fake**: implementação funcional, em memória, do contrato inteiro.

    Diferença em relação a um *mock*: este objeto tem comportamento real
    (guarda as cobranças, aprova ou recusa segundo uma regra), e o teste
    verifica o **estado** dele depois — não a sequência de chamadas.
    """

    aprovar: bool = True
    motivo_recusa: str = "cartão sem limite"
    cobrancas: list[tuple[str, Dinheiro]] = field(default_factory=list)
    falhar_para: set[str] = field(default_factory=set)

    def cobrar(self, cliente: str, valor: Dinheiro) -> Cobranca:
        self.cobrancas.append((cliente, valor))
        n = len(self.cobrancas)
        if not self.aprovar or cliente in self.falhar_para:
            return Cobranca(False, f"tx-{n}", self.motivo_recusa)
        return Cobranca(True, f"tx-{n}")


class GatewayQueExplode:
    """Dublê de sabotagem: simula indisponibilidade do provedor.

    Testar o caminho triste é metade do valor de uma suíte. Sem este dublê,
    ninguém sabe o que o serviço faz quando o gateway cai — e ele **vai** cair.
    """

    def __init__(self, erro: Exception | None = None) -> None:
        self.erro = erro or TimeoutError("gateway indisponível")

    def cobrar(self, cliente: str, valor: Dinheiro) -> Cobranca:
        raise self.erro
