"""Constantes físicas, com unidade e fonte declaradas.

REGRA DESTE PROJETO: nenhuma constante mágica no meio do código. Toda grandeza
física mora aqui, com (a) o valor, (b) a unidade explícita no nome ou no
comentário, e (c) de onde veio. Em pesquisa, uma constante sem fonte é um erro
esperando para acontecer — e um erro de unidade já custou uma missão inteira
(Mars Climate Orbiter, 1999: libra-força-segundo contra newton-segundo).
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Constantes exatas do Sistema Internacional (SI, redefinição de 2019).
# "Exatas" aqui significa: definem a unidade, não são medidas. Não têm incerteza.
# ---------------------------------------------------------------------------

C_LUZ = 299_792_458.0
"""Velocidade da luz no vácuo, em m/s. Valor EXATO por definição do metro (SI)."""

K_BOLTZMANN = 1.380_649e-23
"""Constante de Boltzmann, em J/K. Valor EXATO por definição do kelvin (SI 2019).

É a ponte entre temperatura e potência de ruído: um resistor a T kelvin entrega
k·T watts por hertz de banda. Toda a radioastronomia usa temperatura como unidade
de potência por causa desta constante.
"""

# ---------------------------------------------------------------------------
# Constantes astronômicas
# ---------------------------------------------------------------------------

PARSEC_EM_M = 3.085_677_581_491_367e16
"""Um parsec, em metros. Definido a partir da unidade astronômica e do arcsec."""

UA_EM_M = 1.495_978_707e11
"""Unidade astronômica (distância média Terra-Sol), em metros. Exata por definição
da IAU desde 2012."""

# ---------------------------------------------------------------------------
# Constante de dispersão do plasma interestelar
# ---------------------------------------------------------------------------

K_DISPERSAO = 4.148_808e3
"""Constante de dispersão, em MHz²·pc⁻¹·cm³·s.

De onde vem: da frequência de plasma. Num plasma frio de densidade eletrônica
n_e, a velocidade de grupo de uma onda de rádio depende da frequência, e o atraso
extra acumulado ao longo do caminho é

    Δt = (e² / (2π·m_e·c)) · ∫n_e·dl / f²

O fator e²/(2π·m_e·c), convertido para as unidades práticas da radioastronomia
(f em MHz, ∫n_e·dl em pc·cm⁻³), vale 4148,808.

⚠️ NOTA DE HONESTIDADE CIENTÍFICA: este valor é uma CONVENÇÃO da comunidade de
pulsares, não a melhor medida física. O valor exato derivado das constantes
fundamentais atuais é ligeiramente diferente (~4148,806), mas a literatura de
timing de pulsares fixou 4148,808 (ou, em alguns códigos, 1/2,41e-4 = 4149,38)
para que medidas de DM feitas em décadas diferentes sejam comparáveis entre si.
Trocar a constante mudaria todos os DMs publicados. É um caso claro de convenção
arbitrária mantida por compatibilidade — e é preciso declarar qual se usou.
Referência: Manchester & Taylor, "Pulsars" (1977); handbook de Lorimer & Kramer.
"""

# ---------------------------------------------------------------------------
# Referências de engenharia
# ---------------------------------------------------------------------------

T_CMB = 2.725
"""Temperatura da radiação cósmica de fundo, em K (COBE/FIRAS, Mather et al. 1999).

É o piso absoluto de ruído de qualquer antena apontada para o céu: mesmo com um
receptor perfeito a 0 K, o próprio universo entrega 2,725 K de ruído.
"""

BANDAS_DSN = {
    # nome: (frequência típica de descida em Hz, comentário)
    "S": (2.29e9, "2,29 GHz — missões antigas e proximidade da Terra"),
    "X": (8.42e9, "8,42 GHz — o cavalo de batalha da DSN (Voyager, MRO, Cassini)"),
    "Ka": (32.0e9, "32 GHz — mais banda, mais sensível à chuva"),
}
"""Bandas de frequência da Deep Space Network da NASA, com a frequência de
descida (espaçonave → Terra) típica. Fonte: DSN Telecommunications Link Design
Handbook (810-005), JPL.
"""
