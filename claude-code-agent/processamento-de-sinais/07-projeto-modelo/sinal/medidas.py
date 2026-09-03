"""Medidas de nível, ruído e distorção.

Tudo aqui cabe em uma linha de matemática, e tudo aqui é onde se erra na prática:
confundir pico com RMS, esquecer a referência do dB, medir SNR na banda errada.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

# Piso numérico para não fazer log10(0) = -inf. -400 dBFS é muito abaixo do
# piso de qualquer conversor real (24 bits ≈ -144 dBFS), então é seguro.
_EPS = 1e-20


@dataclass
class Niveis:
    pico: float           # amplitude máxima absoluta, em escala [0, 1]
    pico_dbfs: float      # o mesmo em dBFS (0 dBFS = fundo de escala)
    rms: float
    rms_dbfs: float
    fator_de_crista_db: float   # pico/RMS: 3,01 dB para senoide, ~12 dB para fala
    amostras_ceifadas: int
    dc: float             # componente contínua: deveria ser ~0


def db(x: float | np.ndarray) -> float | np.ndarray:
    """Amplitude → decibel de amplitude (20·log10). Use 10·log10 para potência."""
    return 20.0 * np.log10(np.maximum(np.abs(x), _EPS))


def rms(x: np.ndarray) -> float:
    """Valor eficaz: raiz da média dos quadrados. É a energia que o sinal
    entrega — o que aquece o alto-falante, não o pico."""
    return float(np.sqrt(np.mean(np.asarray(x, dtype=np.float64) ** 2)))


def medir_niveis(x: np.ndarray, limiar_clip: float = 0.999) -> Niveis:
    x = np.asarray(x, dtype=np.float64)
    pico = float(np.max(np.abs(x))) if x.size else 0.0
    r = rms(x)
    return Niveis(
        pico=pico,
        pico_dbfs=float(db(pico)),
        rms=r,
        rms_dbfs=float(db(r)),
        fator_de_crista_db=float(db(pico) - db(r)),
        amostras_ceifadas=int(np.sum(np.abs(x) >= limiar_clip)),
        dc=float(np.mean(x)),
    )


def snr_db(sinal: np.ndarray, ruido: np.ndarray) -> float:
    """SNR quando você tem o sinal limpo e o ruído separados (caso de teste)."""
    p_s = float(np.mean(np.asarray(sinal) ** 2))
    p_n = float(np.mean(np.asarray(ruido) ** 2))
    return 10.0 * np.log10(max(p_s, _EPS) / max(p_n, _EPS))


def thd_db(x: np.ndarray, taxa: int, f0: float, n_harmonicos: int = 5,
           largura_hz: float = 8.0) -> float:
    """Distorção harmônica total, em dB relativos à fundamental.

    Mede a energia em f0 e nos harmônicos 2..N somando o espectro numa
    janelinha em torno de cada um — porque a raia nunca cai exatamente num
    bin, e pegar só o bin central subestima a energia (vazamento espectral).
    """
    x = np.asarray(x, dtype=np.float64)
    n = len(x)
    janela = np.hanning(n)
    X = np.abs(np.fft.rfft(x * janela))
    freqs = np.fft.rfftfreq(n, 1 / taxa)

    def energia_em(f: float) -> float:
        faixa = np.abs(freqs - f) <= largura_hz
        return float(np.sum(X[faixa] ** 2))

    p_fund = energia_em(f0)
    p_harm = sum(energia_em(k * f0) for k in range(2, n_harmonicos + 1)
                 if k * f0 < taxa / 2)
    if p_fund <= _EPS:
        return float("nan")
    return 10.0 * np.log10(max(p_harm, _EPS) / p_fund)


def energia_em_faixa(x: np.ndarray, taxa: int, f_baixa: float, f_alta: float
                     ) -> float:
    """Fração da energia total contida na faixa [f_baixa, f_alta].

    Usada para detectar zumbido de rede: se 10 % da energia está entre 55 e
    65 Hz numa gravação de voz, você tem um problema de aterramento, não de voz.
    """
    x = np.asarray(x, dtype=np.float64)
    n = len(x)
    X = np.abs(np.fft.rfft(x * np.hanning(n))) ** 2
    freqs = np.fft.rfftfreq(n, 1 / taxa)
    total = float(np.sum(X))
    if total <= _EPS:
        return 0.0
    faixa = (freqs >= f_baixa) & (freqs <= f_alta)
    return float(np.sum(X[faixa]) / total)
