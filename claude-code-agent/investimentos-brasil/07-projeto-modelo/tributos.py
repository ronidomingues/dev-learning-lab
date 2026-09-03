"""
tributos.py — imposto de renda, IOF e come-cotas na renda fixa brasileira.

Base legal (vigente em 20/08/2026):
  * IR regressivo: Lei 11.033/2004, art. 1o.
  * IOF regressivo de ate 30 dias: Decreto 6.306/2007, Anexo I.
  * Come-cotas: Lei 10.892/2004 / IN RFB 1.585/2015 — maio e novembro.
  * Isencao de LCI/LCA/CRI/CRA/debentures incentivadas para pessoa fisica:
    Leis 11.033/2004, 11.076/2004 e 12.431/2011. A MP 1.303/2025, que
    tributaria esses papeis em 5%, CADUCOU em outubro de 2025 sem virar lei.

Todo imposto de renda fixa incide sobre o RENDIMENTO, nunca sobre o principal.
"""

from typing import Iterable

# Lei 11.033/2004: tabela regressiva por prazo de aplicacao, em dias corridos.
TABELA_IR = (
    (180, 0.225),
    (360, 0.200),
    (720, 0.175),
    (float("inf"), 0.150),
)

# Decreto 6.306/2007, Anexo I: percentual do RENDIMENTO retido como IOF,
# por dia corrido decorrido. A partir do 30o dia, zero.
TABELA_IOF = {
    1: 0.96, 2: 0.93, 3: 0.90, 4: 0.86, 5: 0.83, 6: 0.80, 7: 0.76,
    8: 0.73, 9: 0.70, 10: 0.66, 11: 0.63, 12: 0.60, 13: 0.56, 14: 0.53,
    15: 0.50, 16: 0.46, 17: 0.43, 18: 0.40, 19: 0.36, 20: 0.33, 21: 0.30,
    22: 0.26, 23: 0.23, 24: 0.20, 25: 0.16, 26: 0.13, 27: 0.10, 28: 0.06,
    29: 0.03,
}

ALIQUOTA_COME_COTAS_LONGO = 0.15   # fundos de longo prazo (carteira > 365 dias)
ALIQUOTA_COME_COTAS_CURTO = 0.20   # fundos de curto prazo


def aliquota_ir(dias: int) -> float:
    """Aliquota de IR sobre o rendimento, pelo prazo em dias corridos.

    >>> aliquota_ir(180)
    0.225
    >>> aliquota_ir(181)
    0.2
    >>> aliquota_ir(721)
    0.15
    """
    if dias < 0:
        raise ValueError("dias nao pode ser negativo")
    for limite, aliquota in TABELA_IR:
        if dias <= limite:
            return aliquota
    raise AssertionError("tabela de IR mal formada")  # pragma: no cover


def fator_iof(dias: int) -> float:
    """Fracao do rendimento retida como IOF. Zero a partir do 30o dia.

    >>> fator_iof(1)
    0.96
    >>> fator_iof(30)
    0.0
    """
    if dias < 0:
        raise ValueError("dias nao pode ser negativo")
    return TABELA_IOF.get(dias, 0.0)


def imposto_renda(rendimento: float, dias: int, isento: bool = False) -> float:
    """IR devido sobre um rendimento, ja considerando o IOF cobrado antes.

    A ordem legal importa: o IOF e cobrado PRIMEIRO e reduz a base do IR.
    Rendimento negativo nao gera imposto (nao existe IR a pagar em prejuizo).
    """
    if isento or rendimento <= 0:
        return 0.0
    base = rendimento - iof(rendimento, dias)
    return base * aliquota_ir(dias)


def iof(rendimento: float, dias: int) -> float:
    """IOF devido sobre um rendimento resgatado em `dias` dias corridos."""
    if rendimento <= 0:
        return 0.0
    return rendimento * fator_iof(dias)


def liquido(rendimento: float, dias: int, isento: bool = False) -> float:
    """Rendimento apos IOF e IR."""
    return rendimento - iof(rendimento, dias) - imposto_renda(rendimento, dias, isento)


def datas_come_cotas(dias: int) -> int:
    """Quantos eventos de come-cotas ocorrem em `dias` (maio e novembro).

    Aproximacao deliberada: um evento a cada 6 meses (182 dias). O calculo
    exato depende da data do aporte; para comparacao entre produtos a
    diferenca e de segunda ordem, e a direcao do efeito e a mesma.
    """
    return dias // 182


def equivalente_isento(taxa_isenta: float, dias: int) -> float:
    """Quanto um produto TRIBUTADO precisa render para empatar com um ISENTO.

    A pergunta que resolve a duvida 'LCI a 90% do CDI e melhor que CDB a 105%?'.

    >>> round(equivalente_isento(0.10, 365), 4)
    0.1212
    """
    return taxa_isenta / (1 - aliquota_ir(dias))


def percentual_cdi_equivalente(pct_cdi_isento: float, dias: int) -> float:
    """Um produto isento a X% do CDI equivale a quantos % do CDI tributado?

    >>> round(percentual_cdi_equivalente(0.90, 365), 4)
    1.0909
    """
    return pct_cdi_isento / (1 - aliquota_ir(dias))


def resumo_tabela_ir() -> Iterable[str]:
    """Linhas legiveis da tabela regressiva, para exibicao."""
    rotulos = ("ate 180 dias", "181 a 360 dias", "361 a 720 dias", "acima de 720 dias")
    for rotulo, (_, aliq) in zip(rotulos, TABELA_IR):
        yield f"{rotulo:<20} {aliq:>6.1%}"
