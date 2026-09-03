"""Tipos do domínio.

São `dataclass` puras: não sabem de banco, não sabem de tela. Servem para o
editor autocompletar, para o `mypy` reclamar antes do usuário reclamar, e para
deixar explícito o vocabulário do negócio.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

STATUS = ("rascunho", "confirmado", "faturado", "cancelado")
PAPEIS = ("admin", "analista", "leitor")
CANAIS = ("site", "telefone", "parceiro", "representante")


@dataclass(frozen=True)
class Usuario:
    id: int
    email: str
    nome: str
    papel: str

    def pode_editar(self) -> bool:
        return self.papel in ("admin", "analista")

    def pode_administrar(self) -> bool:
        return self.papel == "admin"


@dataclass(frozen=True)
class Cliente:
    id: int
    nome: str
    segmento: str
    uf: str
    observacao: str = ""


@dataclass(frozen=True)
class Produto:
    id: int
    nome: str
    categoria: str
    preco_centavos: int


@dataclass(frozen=True)
class Pedido:
    id: int
    cliente_id: int
    produto_id: int
    quantidade: int
    valor_centavos: int
    status: str
    canal: str
    data: date


@dataclass(frozen=True)
class KPIs:
    """O bloco de números do topo do painel, com a variação contra o período anterior."""
    receita_centavos: int
    pedidos: int
    ticket_medio_centavos: int
    clientes_ativos: int
    var_receita: float | None       # variação relativa; None quando não há base
    var_pedidos: float | None
    var_ticket: float | None
    var_clientes: float | None
