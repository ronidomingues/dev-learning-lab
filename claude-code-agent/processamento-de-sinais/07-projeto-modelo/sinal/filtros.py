"""Projeto e aplicação de filtros — FIR por janela, IIR por Butterworth e notch.

Regras de bolso que o código abaixo materializa:

- Frequência de corte SEMPRE normalizada por Nyquist (taxa/2), nunca pela taxa.
  Errar isso é o bug nº 1 de quem começa, e o filtro simplesmente sai no dobro
  da frequência pretendida.
- IIR de ordem alta em forma direta é instável em ponto flutuante. Use SOS
  (second-order sections). O SciPy oferece `output="sos"`; use sempre.
- `filtfilt` roda o filtro duas vezes (para frente e para trás): fase zero,
  ordem efetiva dobrada, e nenhuma causalidade — logo, NÃO serve para tempo real.
"""

from __future__ import annotations

import numpy as np
from scipy import signal


class ErroDeFiltro(ValueError):
    """Especificação de filtro impossível ou perigosa."""


def _normalizar(f: float, taxa: int, nome: str) -> float:
    nyq = taxa / 2
    if not 0 < f < nyq:
        raise ErroDeFiltro(
            f"{nome}={f} Hz fora de (0, {nyq}) Hz. Lembre: o limite é "
            f"Nyquist = taxa/2, não a taxa."
        )
    return f / nyq


def fir_passa_baixa(f_corte: float, taxa: int, n_taps: int = 201,
                    janela: str = "hamming") -> np.ndarray:
    """FIR projetado pelo método da janela.

    n_taps ímpar dá atraso de grupo inteiro ((n-1)/2 amostras), o que permite
    compensar o atraso com um simples deslocamento de índice. Com n par o
    atraso é meio-amostra e a compensação exige interpolação.

    Regra de bolso do comprimento: n_taps ≈ 4·taxa / largura_da_transição.
    Transição de 100 Hz a 44,1 kHz pede ~1764 taps. Não existe almoço grátis:
    corte abrupto custa comprimento, que custa atraso e CPU.
    """
    if n_taps < 3:
        raise ErroDeFiltro("n_taps mínimo é 3")
    if n_taps % 2 == 0:
        raise ErroDeFiltro("use n_taps ímpar para atraso de grupo inteiro")
    return signal.firwin(n_taps, _normalizar(f_corte, taxa, "f_corte"),
                         window=janela)


def fir_passa_faixa(f_baixa: float, f_alta: float, taxa: int,
                    n_taps: int = 401, janela: str = "hamming") -> np.ndarray:
    if f_alta <= f_baixa:
        raise ErroDeFiltro("f_alta deve ser maior que f_baixa")
    wn = [_normalizar(f_baixa, taxa, "f_baixa"), _normalizar(f_alta, taxa, "f_alta")]
    return signal.firwin(n_taps, wn, pass_zero=False, window=janela)


def aplicar_fir(x: np.ndarray, h: np.ndarray, compensar_atraso: bool = True
                ) -> np.ndarray:
    """Convolução do sinal com a resposta ao impulso h.

    `mode="same"` mantém o comprimento; a compensação de atraso alinha a saída
    com a entrada, o que é indispensável se você vai subtrair um do outro.
    """
    y = signal.fftconvolve(x, h, mode="full")
    atraso = (len(h) - 1) // 2
    if compensar_atraso:
        return y[atraso:atraso + len(x)]
    return y[:len(x)]


def sos_passa_alta(f_corte: float, taxa: int, ordem: int = 4) -> np.ndarray:
    """Butterworth passa-alta em seções de segunda ordem.

    Butterworth: resposta maximamente plana na banda passante, transição lenta.
    Se precisar de transição rápida e tolerar ripple, use Chebyshev I; se
    tolerar ripple nos dois lados e quiser a transição mais curta possível,
    elíptico. Ordem igual, o elíptico ganha em seletividade e perde em fase.
    """
    return signal.butter(ordem, _normalizar(f_corte, taxa, "f_corte"),
                         btype="highpass", output="sos")


def sos_passa_baixa(f_corte: float, taxa: int, ordem: int = 4) -> np.ndarray:
    return signal.butter(ordem, _normalizar(f_corte, taxa, "f_corte"),
                         btype="lowpass", output="sos")


def notch(freq: float, taxa: int, q: float = 30.0) -> tuple[np.ndarray, np.ndarray]:
    """Filtro rejeita-faixa estreito (notch) IIR de 2ª ordem.

    Q = freq / largura_de_banda_a_-3dB. Q=30 em 60 Hz dá 2 Hz de largura.
    Q alto demais (>100) toca em problemas numéricos e produz um "toque"
    (ringing) audível de vários ciclos, porque o polo fica quase em cima do
    círculo unitário.
    """
    if q <= 0:
        raise ErroDeFiltro("Q deve ser positivo")
    return signal.iirnotch(_normalizar(freq, taxa, "freq"), q)


def remover_zumbido(x: np.ndarray, taxa: int, freq_rede: float = 60.0,
                    n_harmonicos: int = 3, q: float = 30.0) -> np.ndarray:
    """Cascata de notches na rede e seus harmônicos, com filtfilt (fase zero).

    Por que fase zero importa aqui: um notch causal introduz um salto de fase
    de quase 180° em torno da rejeição. Em análise offline isso é evitável de
    graça; em tempo real, não.
    """
    y = np.asarray(x, dtype=np.float64)
    for k in range(1, n_harmonicos + 1):
        f = k * freq_rede
        if f >= taxa / 2:
            break
        b, a = notch(f, taxa, q)
        y = signal.filtfilt(b, a, y)
    return y


def aplicar_sos(x: np.ndarray, sos: np.ndarray, fase_zero: bool = True
                ) -> np.ndarray:
    """fase_zero=True → filtfilt (offline). False → sosfilt (causal, tempo real)."""
    if fase_zero:
        return signal.sosfiltfilt(sos, x)
    return signal.sosfilt(sos, x)


def resposta_em_frequencia(h: np.ndarray, taxa: int, n: int = 4096
                           ) -> tuple[np.ndarray, np.ndarray]:
    """(frequências em Hz, magnitude em dB) de um FIR. Use para conferir o
    projeto antes de aplicar — nunca confie num filtro que você não plotou."""
    w, H = signal.freqz(h, worN=n, fs=taxa)
    return w, 20 * np.log10(np.maximum(np.abs(H), 1e-12))
