"""
indicadores.py — fotografia do mercado brasileiro numa data.

TODO NÚMERO AQUI TEM DATA E FONTE. Indicador sem data é desinformação:
a Selic de 2020 (2,00% a.a.) e a de 2026 (14,00% a.a.) levam a decisões
opostas com a mesma lógica.

Para atualizar: troque os valores, troque DATA_REFERENCIA e rode os testes.
Os testes NÃO checam o valor dos indicadores (eles mudam), checam a
coerência entre eles.
"""

from dataclasses import dataclass

DATA_REFERENCIA = "2026-08-20"

# --- Juros -----------------------------------------------------------------

#: Meta Selic definida pelo Copom em 05/08/2026 (280a reuniao). Fonte: BCB.
SELIC_META = 0.1400

#: Selic efetiva ("Selic over"): fica alguns centesimos abaixo da meta.
#: E ela, e nao a meta, que remunera o Tesouro Selic.
SELIC_OVER = 0.1390

#: CDI (taxa DI de um dia). Historicamente colada na Selic over.
#: Fonte: B3/BCB, 18/08/2026 -> 13,90% a.a.
CDI = 0.1390

# --- Inflacao --------------------------------------------------------------

#: IPCA acumulado em 12 meses ate julho/2026. Fonte: IBGE.
IPCA_12M = 0.0444

#: IPCA esperado para 2026 pelo mercado. Fonte: Boletim Focus de 17/08/2026.
IPCA_ESPERADO = 0.0502

#: TR mensal aproximada em 2026. Entra no calculo da poupanca.
TR_MENSAL = 0.0017

# --- Poupanca --------------------------------------------------------------

#: Regra vigente desde a Lei 12.703/2012:
#:   Selic > 8,5% a.a.  -> 0,5% ao mes + TR
#:   Selic <= 8,5% a.a. -> 70% da Selic + TR
POUPANCA_LIMITE_SELIC = 0.085
POUPANCA_TETO_MENSAL = 0.005
POUPANCA_FATOR_SELIC = 0.70

# --- Custos institucionais -------------------------------------------------

#: Taxa de custodia da B3 no Tesouro Direto (a.a.).
TAXA_CUSTODIA_B3 = 0.0020

#: Isencao da custodia da B3 para Tesouro Selic ate este valor por investidor.
ISENCAO_CUSTODIA_TESOURO_SELIC = 10_000.00

#: Cobertura do Fundo Garantidor de Creditos, por CPF e por instituicao.
FGC_LIMITE_POR_INSTITUICAO = 250_000.00

#: Teto global do FGC por CPF numa janela movel de 4 anos.
FGC_TETO_QUADRIENIO = 1_000_000.00

# --- Convencoes de mercado -------------------------------------------------

#: CDI e Selic sao cotados em base 252 dias uteis; IPCA+ e prefixado em 252
#: tambem. Titulos indexados a indice de preco usam 252. Usamos 252 como
#: padrao e convertemos dias corridos -> uteis pela razao media do ano.
DIAS_UTEIS_ANO = 252
DIAS_CORRIDOS_ANO = 365


@dataclass(frozen=True)
class Fonte:
    indicador: str
    valor: str
    origem: str
    data: str


FONTES = (
    Fonte("Selic meta", "14,00% a.a.", "Copom/BCB, 280a reuniao", "05/08/2026"),
    Fonte("Selic over", "13,90% a.a.", "BCB (SGS 1178), aproximado", "18/08/2026"),
    Fonte("CDI", "13,90% a.a.", "B3/BCB", "18/08/2026"),
    Fonte("IPCA 12 meses", "4,44%", "IBGE, IPCA de julho/2026", "07/2026"),
    Fonte("IPCA esperado 2026", "5,02%", "Boletim Focus/BCB", "17/08/2026"),
    Fonte("Custodia B3 Tesouro Direto", "0,20% a.a.", "B3", "2026"),
    Fonte("FGC", "R$ 250 mil por CPF/instituicao; R$ 1 mi/4 anos", "FGC", "2026"),
)


def poupanca_mensal() -> float:
    """Rendimento mensal da poupanca sob a regra vigente."""
    if SELIC_META > POUPANCA_LIMITE_SELIC:
        return POUPANCA_TETO_MENSAL + TR_MENSAL
    return (1 + POUPANCA_FATOR_SELIC * SELIC_META) ** (1 / 12) - 1 + TR_MENSAL


def juro_real(nominal: float, inflacao: float = IPCA_12M) -> float:
    """Equacao de Fisher exata: (1+i)/(1+pi) - 1. NAO e i - pi."""
    return (1 + nominal) / (1 + inflacao) - 1
