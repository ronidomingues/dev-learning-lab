"""Medidas de posição, dispersão e forma — todas escritas do zero.

Convenções adotadas (e o motivo de cada uma):

* variância e desvio padrão são **amostrais** (divisor n-1) por padrão,
  porque o caso normal é ter uma amostra, não a população;
* quantis usam o **tipo 7** de Hyndman & Fan (1996), que é o padrão do
  NumPy, do pandas, do R e do Excel PERCENTIL.INC — assim os números deste
  programa batem com os das ferramentas que o leitor vai usar depois;
* a variância é calculada pelo algoritmo de Welford, numericamente estável.
"""

from __future__ import annotations

import math
from collections import Counter

__all__ = [
    "media", "media_aparada", "media_geometrica", "media_harmonica",
    "mediana", "moda", "quantil", "quartis", "amplitude",
    "variancia", "desvio_padrao", "erro_padrao", "coef_variacao",
    "iqr", "mad", "assimetria", "curtose_excesso", "escore_z",
    "resumo_cinco_numeros", "cobertura_1dp",
]


class ErroDeMedida(ValueError):
    """Erro de uso de uma medida: dados insuficientes ou domínio inválido."""


def _validar(dados, minimo=1):
    if not isinstance(dados, (list, tuple)):
        dados = list(dados)
    if len(dados) < minimo:
        raise ErroDeMedida(
            f"são necessários pelo menos {minimo} valores; recebidos {len(dados)}"
        )
    return dados


# ---------------------------------------------------------------- posição

def media(dados):
    """Média aritmética. Usa math.fsum: soma exata, sem erro acumulado."""
    d = _validar(dados, 1)
    return math.fsum(d) / len(d)


def media_aparada(dados, proporcao=0.10):
    """Média descartando `proporcao` das menores e das maiores observações.

    Compromisso entre média (usa tudo, frágil) e mediana (robusta, ignora
    magnitude). É o que o IPCA usa no núcleo por médias aparadas.
    """
    d = sorted(_validar(dados, 1))
    if not 0 <= proporcao < 0.5:
        raise ErroDeMedida("proporcao deve estar em [0; 0,5)")
    k = int(len(d) * proporcao)
    miolo = d[k:len(d) - k] if len(d) - 2 * k > 0 else d
    return media(miolo)


def media_geometrica(dados):
    """Média geométrica — para grandezas que se multiplicam (taxas, fatores).

    Calculada em escala logarítmica para não estourar o expoente com muitos
    valores. Exige todos os valores estritamente positivos.
    """
    d = _validar(dados, 1)
    if any(x <= 0 for x in d):
        raise ErroDeMedida("média geométrica exige todos os valores > 0")
    return math.exp(math.fsum(math.log(x) for x in d) / len(d))


def media_harmonica(dados):
    """Média harmônica — para razões com numerador fixo (km/h, itens/hora)."""
    d = _validar(dados, 1)
    if any(x <= 0 for x in d):
        raise ErroDeMedida("média harmônica exige todos os valores > 0")
    return len(d) / math.fsum(1.0 / x for x in d)


def mediana(dados):
    """Mediana. Com n par, interpola entre os dois valores centrais."""
    d = sorted(_validar(dados, 1))
    n = len(d)
    meio = n // 2
    return d[meio] if n % 2 else (d[meio - 1] + d[meio]) / 2


def moda(dados):
    """Todas as modas (pode haver empate) e a frequência delas."""
    d = _validar(dados, 1)
    cont = Counter(d)
    maior = max(cont.values())
    return sorted(v for v, c in cont.items() if c == maior), maior


def quantil(dados, p):
    """Quantil de ordem p em [0;1], tipo 7 de Hyndman & Fan.

    h = (n-1)*p; interpola linearmente entre os vizinhos de h.
    """
    d = sorted(_validar(dados, 1))
    if not 0.0 <= p <= 1.0:
        raise ErroDeMedida("p deve estar em [0; 1]")
    n = len(d)
    if n == 1:
        return float(d[0])
    h = (n - 1) * p
    lo = math.floor(h)
    hi = math.ceil(h)
    if lo == hi:
        return float(d[lo])
    return d[lo] + (h - lo) * (d[hi] - d[lo])


def quartis(dados):
    """(Q1, Q2, Q3)."""
    return (quantil(dados, 0.25), quantil(dados, 0.50), quantil(dados, 0.75))


def amplitude(dados):
    d = _validar(dados, 1)
    return max(d) - min(d)


# --------------------------------------------------------------- dispersão

def variancia(dados, ddof=1):
    """Variância pelo algoritmo de Welford (uma passada, estável).

    ddof=1 -> amostral (padrão);  ddof=0 -> populacional.

    A forma ingênua, sum(x**2)/n - media**2, sofre cancelamento
    catastrófico quando a média é grande e a dispersão pequena — pode até
    devolver variância negativa. Welford não tem esse problema.
    """
    d = _validar(dados, ddof + 1)
    n = 0
    m = 0.0
    m2 = 0.0
    for x in d:
        n += 1
        delta = x - m
        m += delta / n
        m2 += delta * (x - m)
    return m2 / (n - ddof)


def desvio_padrao(dados, ddof=1):
    return math.sqrt(variancia(dados, ddof))


def erro_padrao(dados):
    """Erro padrão da média: s/sqrt(n). Dispersão DA MÉDIA, não dos dados."""
    d = _validar(dados, 2)
    return desvio_padrao(d) / math.sqrt(len(d))


def coef_variacao(dados):
    """CV = s / média. Só faz sentido em escala de razão e com média != 0."""
    d = _validar(dados, 2)
    m = media(d)
    if m == 0:
        raise ErroDeMedida("CV indefinido: a média é zero")
    return desvio_padrao(d) / abs(m)


def iqr(dados):
    q1, _, q3 = quartis(dados)
    return q3 - q1


def mad(dados, escalado=True):
    """Desvio absoluto mediano (Median Absolute Deviation).

    Com escalado=True multiplica por 1,4826 para que, em dados normais, o
    MAD estime o mesmo que o desvio padrão — tornando os dois comparáveis.
    A constante é 1/Phi^-1(0,75).
    """
    d = _validar(dados, 1)
    md = mediana(d)
    bruto = mediana([abs(x - md) for x in d])
    return bruto * 1.4826 if escalado else bruto


# ------------------------------------------------------------------- forma

def assimetria(dados):
    """Assimetria amostral ajustada (G1) — a mesma do Excel e do SAS.

    0 = simétrica; > 0 = cauda à direita; < 0 = cauda à esquerda.
    """
    d = _validar(dados, 3)
    n = len(d)
    m = media(d)
    s = desvio_padrao(d, ddof=1)
    if s == 0:
        raise ErroDeMedida("assimetria indefinida: dispersão zero")
    soma = math.fsum(((x - m) / s) ** 3 for x in d)
    return (n / ((n - 1) * (n - 2))) * soma


def curtose_excesso(dados):
    """Curtose em excesso amostral (G2). Normal = 0.

    ATENÇÃO: curtose mede PESO DE CAUDA, não 'achatamento' — ver o arquivo
    14 do curso. Valor alto significa outliers prováveis, não pico agudo.
    """
    d = _validar(dados, 4)
    n = len(d)
    m = media(d)
    s = desvio_padrao(d, ddof=1)
    if s == 0:
        raise ErroDeMedida("curtose indefinida: dispersão zero")
    soma = math.fsum(((x - m) / s) ** 4 for x in d)
    a = (n * (n + 1)) / ((n - 1) * (n - 2) * (n - 3))
    b = (3 * (n - 1) ** 2) / ((n - 2) * (n - 3))
    return a * soma - b


def escore_z(valor, dados):
    return (valor - media(dados)) / desvio_padrao(dados)


def resumo_cinco_numeros(dados):
    d = _validar(dados, 1)
    q1, q2, q3 = quartis(d)
    return {"min": min(d), "q1": q1, "mediana": q2, "q3": q3, "max": max(d)}


def cobertura_1dp(dados):
    """Fração de observações a menos de 1 desvio padrão da média.

    Numa distribuição normal isso vale ~0,6827. Medir a cobertura real é o
    teste de sanidade mais barato que existe contra supor normalidade.
    """
    d = _validar(dados, 2)
    m, s = media(d), desvio_padrao(d)
    if s == 0:
        return 1.0
    return sum(1 for x in d if abs(x - m) <= s) / len(d)
