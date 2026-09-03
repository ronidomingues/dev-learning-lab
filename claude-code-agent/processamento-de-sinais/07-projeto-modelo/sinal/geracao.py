"""Síntese de sinais de teste.

Um analisador só é confiável se você puder alimentá-lo com um sinal cuja
resposta correta você já conhece. Este módulo fabrica esse sinal.
"""

from __future__ import annotations

import numpy as np


def tom(
    f0: float,
    duracao: float,
    taxa: int,
    harmonicos: int = 1,
    decaimento: float = 0.6,
    fase: float = 0.0,
) -> np.ndarray:
    """Soma de senoides harmônicas: f0, 2·f0, 3·f0, ... com amplitude decrescente.

    Um instrumento real não produz uma senoide pura — produz uma fundamental
    mais harmônicos. É por isso que um dó de violino e um dó de flauta têm a
    mesma altura (pitch) e timbres diferentes: mesma f0, envelopes de
    harmônicos diferentes.

    Levanta ValueError se algum harmônico violar Nyquist (f > taxa/2), porque
    silenciosamente ele voltaria dobrado no espectro (aliasing) e o "sinal de
    teste com resposta conhecida" deixaria de ter resposta conhecida.
    """
    if f0 <= 0:
        raise ValueError("f0 deve ser positiva")
    if harmonicos * f0 >= taxa / 2:
        raise ValueError(
            f"harmônico {harmonicos} em {harmonicos * f0:.1f} Hz viola Nyquist "
            f"({taxa / 2:.1f} Hz). Aumente a taxa ou reduza os harmônicos."
        )

    n = int(round(duracao * taxa))
    t = np.arange(n) / taxa
    x = np.zeros(n)
    for k in range(1, harmonicos + 1):
        x += (decaimento ** (k - 1)) * np.sin(2 * np.pi * k * f0 * t + fase)
    return x / np.max(np.abs(x))


def envelope_adsr(
    n: int, taxa: int, ataque: float = 0.01, decaimento: float = 0.1,
    sustentacao: float = 0.7, relaxamento: float = 0.2
) -> np.ndarray:
    """Envelope ADSR simples, para o tom não começar e terminar em degrau.

    Cortar um seno no meio cria uma descontinuidade, e descontinuidade no
    tempo é energia espalhada por todo o espectro — o mesmo fenômeno que
    justifica janelamento na análise.
    """
    env = np.ones(n)
    n_a = max(1, int(ataque * taxa))
    n_d = max(1, int(decaimento * taxa))
    n_r = max(1, int(relaxamento * taxa))
    env[:n_a] = np.linspace(0, 1, n_a)
    env[n_a:n_a + n_d] = np.linspace(1, sustentacao, n_d)
    env[n_a + n_d:] = sustentacao
    if n_r < n:
        env[-n_r:] *= np.linspace(1, 0, n_r)
    return env


def ruido_branco(n: int, rms: float, semente: int = 0) -> np.ndarray:
    """Ruído gaussiano com RMS alvo. Semente fixa = teste reprodutível."""
    rng = np.random.default_rng(semente)
    r = rng.standard_normal(n)
    return r * (rms / np.sqrt(np.mean(r ** 2)))


def zumbido(n: int, taxa: int, freq: float, amplitude: float) -> np.ndarray:
    """Zumbido de rede: a fundamental mais o 3º harmônico, que é o perfil
    típico de captação por transformador (a saturação do núcleo gera ímpares).
    """
    t = np.arange(n) / taxa
    return amplitude * (np.sin(2 * np.pi * freq * t)
                        + 0.3 * np.sin(2 * np.pi * 3 * freq * t))


def sinal_de_teste(
    f0: float = 440.0,
    duracao: float = 2.0,
    taxa: int = 44100,
    harmonicos: int = 5,
    rms_ruido: float = 0.02,
    freq_rede: float = 60.0,
    amp_rede: float = 0.05,
    semente: int = 0,
) -> np.ndarray:
    """Nota com harmônicos + envelope + ruído branco + zumbido de rede.

    É de propósito um sinal *sujo*: um analisador que só funciona com senoide
    limpa não serve para nada fora do slide de aula.
    """
    n = int(round(duracao * taxa))
    x = tom(f0, duracao, taxa, harmonicos=harmonicos)
    x *= envelope_adsr(n, taxa)
    x += ruido_branco(n, rms_ruido, semente=semente)
    x += zumbido(n, taxa, freq_rede, amp_rede)
    pico = np.max(np.abs(x))
    return 0.9 * x / pico  # deixa 0.9 dBFS de folga: sem clipping


def varredura(f_inicial: float, f_final: float, duracao: float, taxa: int
              ) -> np.ndarray:
    """Varredura (chirp) linear — o sinal de teste para medir resposta em
    frequência de um filtro "na marra": aplique o filtro e olhe o resultado.

    A fase é a integral da frequência instantânea; por isso o t²/2.
    """
    n = int(round(duracao * taxa))
    t = np.arange(n) / taxa
    k = (f_final - f_inicial) / duracao
    fase = 2 * np.pi * (f_inicial * t + 0.5 * k * t ** 2)
    return np.sin(fase)
