"""Leitura e escrita de WAV usando só a biblioteca padrão + NumPy.

Por que não usar `soundfile`/`librosa`? Porque ler um WAV PCM é 30 linhas e
entender essas 30 linhas ensina mais sobre quantização do que qualquer capítulo:
aqui você vê, explicitamente, o inteiro de 16 bits virar float em [-1, 1).
"""

from __future__ import annotations

import wave
from pathlib import Path

import numpy as np


class ErroDeAudio(Exception):
    """Problema de leitura/escrita de arquivo de áudio."""


# Fator de normalização por profundidade de bits.
# Dividimos por 2**(bits-1) — 32768 para 16 bits — e não por 32767:
# assim o passo de quantização vira exatamente 2^-15 e o zero digital
# continua sendo o zero analógico. É a convenção de fato da indústria.
_ESCALA = {1: 2 ** 7, 2: 2 ** 15, 4: 2 ** 31}


def ler_wav(caminho: str | Path) -> tuple[np.ndarray, int]:
    """Lê um WAV PCM e devolve (amostras float64 em [-1, 1), taxa em Hz).

    Estéreo é convertido para mono pela média dos canais — soma coerente,
    o que pode cancelar sinais fora de fase; para análise de afinação é
    aceitável, para masterização não seria.
    """
    caminho = Path(caminho)
    if not caminho.exists():
        raise ErroDeAudio(f"arquivo não encontrado: {caminho}")

    try:
        with wave.open(str(caminho), "rb") as w:
            n_canais = w.getnchannels()
            largura = w.getsampwidth()
            taxa = w.getframerate()
            n_quadros = w.getnframes()
            bruto = w.readframes(n_quadros)
    except wave.Error as e:
        raise ErroDeAudio(
            f"{caminho} não é um WAV PCM legível ({e}). "
            "Converta com: ffmpeg -i entrada.mp3 -acodec pcm_s16le saida.wav"
        ) from e

    if largura not in (1, 2, 4):
        raise ErroDeAudio(f"profundidade de {largura * 8} bits não suportada")

    tipo = {1: np.uint8, 2: np.int16, 4: np.int32}[largura]
    x = np.frombuffer(bruto, dtype=tipo).astype(np.float64)

    if largura == 1:
        # WAV de 8 bits é *unsigned*: 128 é o silêncio. Herança do PC-speaker.
        x = x - 128.0

    x /= _ESCALA[largura]

    if n_canais > 1:
        x = x.reshape(-1, n_canais).mean(axis=1)

    if x.size == 0:
        raise ErroDeAudio(f"{caminho} não contém amostras")

    return x, taxa


def escrever_wav(caminho: str | Path, x: np.ndarray, taxa: int) -> None:
    """Escreve amostras float em [-1, 1) como WAV PCM 16 bits mono.

    O `clip` antes da conversão é obrigatório: um float 1.4 viraria 45875,
    que estoura o int16 e "dá a volta" para um valor negativo — o estalo
    mais famoso do áudio digital (wrap-around em vez de saturação).
    """
    if taxa <= 0:
        raise ErroDeAudio(f"taxa de amostragem inválida: {taxa}")

    x = np.clip(np.asarray(x, dtype=np.float64), -1.0, 1.0 - 2 ** -15)
    inteiros = np.round(x * _ESCALA[2]).astype(np.int16)

    caminho = Path(caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(caminho), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(int(taxa))
        w.writeframes(inteiros.tobytes())
