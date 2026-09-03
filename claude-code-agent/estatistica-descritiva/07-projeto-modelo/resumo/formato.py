"""Formatação numérica em padrão brasileiro, sem depender de locale.

`locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')` falha em contêiner enxuto,
em CI e em máquina de colega — e falha só na hora de rodar. Formatar à mão
é dez linhas e nunca quebra.
"""

from __future__ import annotations

import math

__all__ = ["num", "pct"]


def num(v, casas=None):
    """Número em padrão pt-BR: milhar com '.', decimal com ','.

    Se `casas` for None, escolhe automaticamente: valores grandes ficam
    inteiros, valores pequenos ganham casas suficientes para não sumirem.
    """
    if v is None:
        return "—"
    if isinstance(v, int) or (isinstance(v, float) and v.is_integer() and abs(v) < 1e15):
        v = int(v)
        return f"{v:,}".replace(",", ".")
    if not math.isfinite(v):
        return "—"
    if casas is None:
        a = abs(v)
        if a >= 1000:
            casas = 2
        elif a >= 1:
            casas = 4
        elif a >= 0.001:
            casas = 6
        else:
            return f"{v:.3e}".replace(".", ",")
    texto = f"{v:,.{casas}f}"
    inteiro, _, dec = texto.partition(".")
    inteiro = inteiro.replace(",", ".")
    dec = dec.rstrip("0")
    return f"{inteiro},{dec}" if dec else inteiro


def pct(v, casas=1):
    """Fração (0..1) em porcentagem."""
    if v is None or not math.isfinite(v):
        return "—"
    return f"{v*100:.{casas}f}".replace(".", ",") + "%"
