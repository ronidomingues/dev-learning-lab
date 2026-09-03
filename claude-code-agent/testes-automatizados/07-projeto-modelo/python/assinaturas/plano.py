"""Planos e cupons de desconto."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

from .dinheiro import Dinheiro


@dataclass(frozen=True, slots=True)
class Plano:
    codigo: str
    nome: str
    preco: Dinheiro
    dias_ciclo: int

    def __post_init__(self) -> None:
        if self.dias_ciclo <= 0:
            raise ValueError("dias_ciclo deve ser positivo")


CATALOGO: dict[str, Plano] = {
    "basico": Plano("basico", "Básico", Dinheiro.de_reais("19,90"), 30),
    "pro": Plano("pro", "Pro", Dinheiro.de_reais("49,90"), 30),
    "anual": Plano("anual", "Pro Anual", Dinheiro.de_reais("499,00"), 365),
}


class CupomInvalido(Exception):
    """Erro de domínio: cupom não pode ser aplicado nesta situação."""


@dataclass(frozen=True, slots=True)
class Cupom:
    codigo: str
    percentual: int
    validade: date
    usos_maximos: int = 1

    def preco_com_desconto(self, preco: Dinheiro, hoje: date, usos_atuais: int) -> Dinheiro:
        """Aplica o cupom ou explode com o motivo exato.

        Regras, todas testadas em `tests/test_cupom.py`:
        - vale **no** dia da validade (inclusive) — a fronteira mais errada do mundo;
        - esgotado quando `usos_atuais >= usos_maximos`;
        - 100% de desconto é permitido (cortesia), 0% é permitido (cupom inócuo).
        """
        if hoje > self.validade:
            raise CupomInvalido(f"cupom {self.codigo} expirou em {self.validade:%d/%m/%Y}")
        if usos_atuais >= self.usos_maximos:
            raise CupomInvalido(f"cupom {self.codigo} esgotado ({usos_atuais}/{self.usos_maximos})")
        return preco.aplicar_desconto(self.percentual)


def proxima_cobranca(base: date, dias_ciclo: int, ciclos: int = 1) -> date:
    """Data da n-ésima cobrança contada a partir de `base`.

    Usamos ciclo em **dias**, não em "mês", justamente para não ter de decidir
    o que é "31 de janeiro + 1 mês". Essa é uma decisão de projeto que troca
    fidelidade ao calendário por ausência de casos patológicos — e está aqui
    documentada porque um leitor futuro vai perguntar.
    """
    if ciclos < 0:
        raise ValueError("ciclos não pode ser negativo")
    return base + timedelta(days=dias_ciclo * ciclos)
