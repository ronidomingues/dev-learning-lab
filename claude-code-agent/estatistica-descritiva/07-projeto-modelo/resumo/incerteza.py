"""Erro, intervalos de confiança e bootstrap.

Este módulo existe porque um número sem sua incerteza é uma opinião com
aparência de fato. Ele implementa, sem SciPy:

* a distribuição t de Student (função quantílica), via função beta
  incompleta regularizada em fração continuada;
* o intervalo de confiança da média pelo método t (correto para n pequeno);
* o intervalo de confiança percentílico por bootstrap, que serve para
  qualquer medida — inclusive as sem fórmula fechada, como a mediana.
"""

from __future__ import annotations

import math
import random

from .medidas import desvio_padrao, media, mediana

__all__ = [
    "z_critico", "t_critico", "ic_media_t", "ic_media_z",
    "bootstrap", "ic_bootstrap", "n_para_margem",
]

_SQRT2 = math.sqrt(2.0)


# ------------------------------------------------------------ normal padrão

def _phi(x):
    """Função de distribuição acumulada da normal padrão."""
    return 0.5 * (1.0 + math.erf(x / _SQRT2))


def z_critico(confianca=0.95):
    """Quantil bicaudal da normal padrão. z_critico(0.95) -> 1.959964..."""
    if not 0.0 < confianca < 1.0:
        raise ValueError("confianca deve estar em (0; 1)")
    alvo = 1.0 - (1.0 - confianca) / 2.0
    lo, hi = 0.0, 40.0
    for _ in range(200):                      # bissecção: 200 passos = exato em float
        meio = (lo + hi) / 2.0
        if _phi(meio) < alvo:
            lo = meio
        else:
            hi = meio
    return (lo + hi) / 2.0


# ---------------------------------------------------------- t de Student

def _betacf(a, b, x, iteracoes=300, eps=3e-16):
    """Fração continuada de Lentz para a função beta incompleta."""
    tiny = 1e-300
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c = 1.0
    d = 1.0 - qab * x / qap
    if abs(d) < tiny:
        d = tiny
    d = 1.0 / d
    h = d
    for m in range(1, iteracoes + 1):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        if abs(d) < tiny:
            d = tiny
        c = 1.0 + aa / c
        if abs(c) < tiny:
            c = tiny
        d = 1.0 / d
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        if abs(d) < tiny:
            d = tiny
        c = 1.0 + aa / c
        if abs(c) < tiny:
            c = tiny
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < eps:
            break
    return h


def _betai(a, b, x):
    """Beta incompleta regularizada I_x(a, b)."""
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    ln = (math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
          + a * math.log(x) + b * math.log1p(-x))
    frente = math.exp(ln)
    if x < (a + 1.0) / (a + b + 2.0):
        return frente * _betacf(a, b, x) / a
    return 1.0 - frente * _betacf(b, a, 1.0 - x) / b


def t_cdf(t, gl):
    """P(T <= t) para a t de Student com `gl` graus de liberdade."""
    if gl <= 0:
        raise ValueError("graus de liberdade devem ser > 0")
    x = gl / (gl + t * t)
    meia_cauda = 0.5 * _betai(gl / 2.0, 0.5, x)
    return 1.0 - meia_cauda if t > 0 else meia_cauda


def t_critico(confianca=0.95, gl=None):
    """Quantil bicaudal da t de Student.

    t_critico(0.95, 9)  -> 2.2622  (o valor clássico das tabelas impressas)
    Com gl -> infinito, converge para z_critico.
    """
    if gl is None or gl > 5000:
        return z_critico(confianca)
    if gl <= 0:
        raise ValueError("graus de liberdade devem ser > 0")
    alvo = 1.0 - (1.0 - confianca) / 2.0
    lo, hi = 0.0, 1e4
    for _ in range(300):
        meio = (lo + hi) / 2.0
        if t_cdf(meio, gl) < alvo:
            lo = meio
        else:
            hi = meio
    return (lo + hi) / 2.0


# --------------------------------------------------- intervalos da média

def ic_media_t(dados, confianca=0.95):
    """IC da média pela t de Student. É o método correto para n pequeno."""
    n = len(dados)
    if n < 2:
        raise ValueError("IC da média exige pelo menos 2 observações")
    m = media(dados)
    ep = desvio_padrao(dados) / math.sqrt(n)
    t = t_critico(confianca, gl=n - 1)
    return (m - t * ep, m + t * ep)


def ic_media_z(dados, confianca=0.95):
    """IC da média pela normal. Só é adequado com n grande (>= 30)."""
    n = len(dados)
    m = media(dados)
    ep = desvio_padrao(dados) / math.sqrt(n)
    z = z_critico(confianca)
    return (m - z * ep, m + z * ep)


# ------------------------------------------------------------- bootstrap

def bootstrap(dados, estatistica=None, repeticoes=2000, semente=42):
    """Distribuição bootstrap de uma estatística qualquer.

    Reamostra `dados` COM REPOSIÇÃO, do mesmo tamanho, `repeticoes` vezes.
    A semente é obrigatória por padrão: simulação sem semente registrada
    não é reprodutível, e o que não é reprodutível não é evidência.
    """
    if estatistica is None:
        estatistica = mediana
    n = len(dados)
    if n < 2:
        raise ValueError("bootstrap exige pelo menos 2 observações")
    rng = random.Random(semente)
    saida = []
    for _ in range(repeticoes):
        reamostra = [dados[rng.randrange(n)] for _ in range(n)]
        try:
            saida.append(estatistica(reamostra))
        except Exception:            # reamostra degenerada (todos iguais)
            continue
    return saida


def ic_bootstrap(dados, estatistica=None, confianca=0.95,
                 repeticoes=2000, semente=42):
    """IC percentílico por bootstrap: (limite_inferior, limite_superior, EP)."""
    dist = sorted(bootstrap(dados, estatistica, repeticoes, semente))
    if len(dist) < 2:
        raise ValueError("bootstrap não produziu amostras suficientes")
    a = (1.0 - confianca) / 2.0
    lo = dist[max(0, int(a * len(dist)))]
    hi = dist[min(len(dist) - 1, int((1.0 - a) * len(dist)) - 1)]
    return lo, hi, desvio_padrao(dist)


def n_para_margem(margem, p=0.5, confianca=0.95):
    """Tamanho de amostra para uma margem de erro alvo, em proporções.

    p = 0,5 é o pior caso (maximiza a variância) — é o que institutos usam
    quando não se sabe nada de antemão.
    """
    if not 0 < margem < 1:
        raise ValueError("margem deve estar em (0; 1)")
    z = z_critico(confianca)
    return math.ceil(p * (1 - p) * (z / margem) ** 2)
