"""Formatação para olhos brasileiros.

Por que não usar `locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')`:
o locale pode não estar gerado no contêiner (é o caso da imagem `python:slim`),
`setlocale` é global e não é seguro em ambiente com várias threads — e o
Streamlit atende sessões em threads. Formatar à mão é chato e é o certo.
"""

from __future__ import annotations

from datetime import date


def _milhar(inteiro: int) -> str:
    return f"{inteiro:,}".replace(",", ".")


def brl(centavos: int | float, *, com_simbolo: bool = True) -> str:
    """1234567 -> 'R$ 12.345,67'. Recebe CENTAVOS, não reais."""
    centavos = int(round(centavos))
    sinal = "-" if centavos < 0 else ""
    centavos = abs(centavos)
    inteiro, resto = divmod(centavos, 100)
    texto = f"{sinal}{_milhar(inteiro)},{resto:02d}"
    return f"R$ {texto}" if com_simbolo else texto


def brl_compacto(centavos: int | float) -> str:
    """Para KPI: 'R$ 1,2 mi'. Painel executivo não quer contar zeros."""
    reais = abs(centavos) / 100
    sinal = "-" if centavos < 0 else ""
    for limite, sufixo in ((1e9, " bi"), (1e6, " mi"), (1e3, " mil")):
        if reais >= limite:
            return f"{sinal}R$ {reais / limite:.1f}".replace(".", ",") + sufixo
    return brl(centavos)


def numero(valor: int | float) -> str:
    return _milhar(int(round(valor)))


def percentual(fracao: float | None, casas: int = 1) -> str | None:
    """0.1234 -> '+12,3%'. None entra e None sai: 'sem base de comparação'."""
    if fracao is None:
        return None
    sinal = "+" if fracao >= 0 else ""
    return f"{sinal}{fracao * 100:.{casas}f}".replace(".", ",") + "%"


def data_br(d: date) -> str:
    return d.strftime("%d/%m/%Y")
