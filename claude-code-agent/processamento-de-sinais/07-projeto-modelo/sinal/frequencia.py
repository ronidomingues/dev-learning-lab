"""Estimação da frequência fundamental (f0) por três métodos independentes.

Três, e não um, de propósito: cada método falha de um jeito diferente, e
comparar as três respostas é o teste de sanidade mais barato que existe.

- FFT + interpolação parabólica → rápido, mas confunde harmônico com fundamental.
- HPS (Harmonic Product Spectrum)  → resolve o harmônico, erra em sinal de
  banda estreita sem harmônicos.
- Autocorrelação                    → robusto a ruído, tende a oitavar para baixo.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

# La central (A4) = 440 Hz é a referência ISO 16:1975. Orquestras europeias
# frequentemente afinam em 442 ou 443 Hz; música antiga usa 415 Hz.
A4_PADRAO = 440.0

_NOMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


@dataclass
class Nota:
    nome: str          # ex.: "A4"
    freq_ideal: float  # frequência exata dessa nota na afinação usada
    desvio_cents: float  # quanto o sinal está acima (+) ou abaixo (-) dela


def nota_mais_proxima(f: float, a4: float = A4_PADRAO) -> Nota:
    """Converte Hz em nome de nota + desvio em cents.

    Um semitom é 2^(1/12) em frequência; um cent é 1/100 de semitom, ou seja
    2^(1/1200). Ouvido humano treinado detecta ~5 cents; ~10 cents já soa
    desafinado num acorde sustentado.
    """
    if f <= 0:
        raise ValueError("frequência deve ser positiva")
    # 69 é o número MIDI do A4. Fórmula padrão MIDI.
    midi_real = 69 + 12 * np.log2(f / a4)
    midi = int(round(midi_real))
    cents = (midi_real - midi) * 100
    nome = f"{_NOMES[midi % 12]}{midi // 12 - 1}"
    ideal = a4 * 2 ** ((midi - 69) / 12)
    return Nota(nome=nome, freq_ideal=float(ideal), desvio_cents=float(cents))


def _tamanho_fft(n: int, pedido: int | None) -> int:
    """Resolve o tamanho da FFT.

    ARMADILHA que este código evita: `np.fft.rfft(x, n=8192)` com len(x)=88200
    **descarta** 80 008 amostras — o NumPy trunca, não avisa, e você acaba
    analisando só o ataque da nota. Aqui `n_fft` é sempre um piso: o mínimo é
    a próxima potência de 2 acima do comprimento do sinal, e o excedente é
    zero-padding (que interpola o espectro, mas não cria resolução nova —
    ver 16-dft-e-fft.md).
    """
    minimo = int(2 ** np.ceil(np.log2(max(n, 2))))
    return max(minimo, int(pedido)) if pedido else minimo


def segmento_estavel(x: np.ndarray, taxa: int, segundos: float = 1.0
                     ) -> np.ndarray:
    """Recorta o trecho central do sinal.

    Estimador de f0 pressupõe estacionaridade: a frequência não muda durante a
    janela analisada. O centro de uma nota é a parte mais estável — o ataque
    tem transiente de banda larga e a cauda tem relação sinal-ruído ruim.
    """
    n_alvo = int(round(segundos * taxa))
    if len(x) <= n_alvo:
        return np.asarray(x, dtype=np.float64)
    inicio = (len(x) - n_alvo) // 2
    return np.asarray(x[inicio:inicio + n_alvo], dtype=np.float64)


def _interpolar_pico(mag: np.ndarray, k: int) -> float:
    """Interpolação parabólica em torno do bin k, em dB.

    Sem isso, a resolução da estimativa é a do bin (taxa/N). Com isso, o erro
    cai uma ordem de grandeza — é o truque mais barato de toda a análise
    espectral, e o motivo é geométrico: o topo do lóbulo principal de uma
    janela Hann em dB é quase exatamente uma parábola.
    """
    if k <= 0 or k >= len(mag) - 1:
        return float(k)
    a, b, c = (20 * np.log10(max(v, 1e-20)) for v in (mag[k - 1], mag[k], mag[k + 1]))
    denom = a - 2 * b + c
    if abs(denom) < 1e-30:
        return float(k)
    return k + 0.5 * (a - c) / denom


def f0_por_fft(x: np.ndarray, taxa: int, f_min: float = 40.0,
               f_max: float = 2000.0, n_fft: int | None = None) -> float:
    """Maior raia espectral dentro da faixa, com interpolação parabólica."""
    x = np.asarray(x, dtype=np.float64)
    n = len(x)
    n_fft = _tamanho_fft(n, n_fft)
    janela = np.hanning(n)
    mag = np.abs(np.fft.rfft(x * janela, n=n_fft))
    freqs = np.fft.rfftfreq(n_fft, 1 / taxa)

    valida = (freqs >= f_min) & (freqs <= f_max)
    if not np.any(valida):
        raise ValueError("faixa de busca vazia para esta taxa de amostragem")
    mag_busca = np.where(valida, mag, 0.0)
    k = int(np.argmax(mag_busca))
    return float(_interpolar_pico(mag, k) * taxa / n_fft)


def f0_por_hps(x: np.ndarray, taxa: int, f_min: float = 40.0,
               f_max: float = 2000.0, n_harmonicos: int = 5,
               n_fft: int | None = None, piso_relativo: float = 1e-3) -> float:
    """Harmonic Product Spectrum: multiplica o espectro por versões dele
    comprimidas em 2×, 3×, ... N×.

    A ideia: na fundamental, todas as versões comprimidas têm energia (porque
    todo harmônico k·f0 cai sobre f0 quando comprimido por k). Num harmônico
    isolado, não. O produto reforça f0 e apaga o resto — é o antídoto clássico
    para o erro de oitava para CIMA.

    O `piso_relativo` conserta o erro de oitava para BAIXO, que é a armadilha
    menos conhecida e que quase todo tutorial de HPS tem: sem piso, o produto
    em f0/4 vale (quase-zero)³ × (pico em f0), e o produto em f0 vale
    (pico) × (quase-zero)⁴ — numericamente comparáveis, e o ruído decide qual
    ganha. Com um piso em -60 dB do máximo nas cópias comprimidas, o termo
    mag[i] do próprio bin passa a dominar e o sub-harmônico deixa de vencer.
    Descobri isso porque o teste com senoide pura falhou devolvendo 110 Hz
    para um sinal de 440 Hz — está no `tests/test_sinal.py`.
    """
    x = np.asarray(x, dtype=np.float64)
    n = len(x)
    n_fft = _tamanho_fft(n, n_fft)
    mag = np.abs(np.fft.rfft(x * np.hanning(n), n=n_fft))

    # Só podemos avaliar índices i tais que i·N ainda cabe no espectro.
    limite = len(mag) // n_harmonicos
    if limite < 4:
        raise ValueError("espectro curto demais para HPS")

    piso = piso_relativo * float(np.max(mag))
    hps = mag[:limite].copy()
    for k in range(2, n_harmonicos + 1):
        hps *= np.maximum(mag[::k][:limite], piso)

    freqs = np.fft.rfftfreq(n_fft, 1 / taxa)[:limite]
    valida = (freqs >= f_min) & (freqs <= f_max)
    if not np.any(valida):
        raise ValueError(
            f"faixa [{f_min}, {f_max}] Hz não cabe no HPS com {n_harmonicos} "
            f"harmônicos (o teto é Nyquist/{n_harmonicos} = "
            f"{taxa / 2 / n_harmonicos:.0f} Hz)")
    idx = int(np.argmax(np.where(valida, hps, 0.0)))
    return float(_interpolar_pico(hps, idx) * taxa / n_fft)


def f0_por_autocorrelacao(x: np.ndarray, taxa: int, f_min: float = 40.0,
                          f_max: float = 2000.0) -> float:
    """Autocorrelação via FFT (teorema de Wiener-Khinchin) e busca do primeiro
    pico fora da origem.

    A autocorrelação de um sinal periódico tem máximo no atraso igual ao
    período. Calculá-la pela FFT custa O(N log N) em vez de O(N²) — este é o
    exemplo canônico de por que a FFT importa além de "ver o espectro".
    """
    x = np.asarray(x, dtype=np.float64)
    x = x - np.mean(x)  # remover DC: senão o pico em atraso 0 domina tudo
    n = len(x)
    n_fft = int(2 ** np.ceil(np.log2(2 * n)))  # zero-padding evita a
    X = np.fft.rfft(x, n=n_fft)                # autocorrelação *circular*
    r = np.fft.irfft(X * np.conj(X), n=n_fft)[:n]

    if r[0] <= 0:
        raise ValueError("sinal com energia nula")
    r = r / r[0]

    atraso_min = max(1, int(taxa / f_max))
    atraso_max = min(n - 1, int(taxa / f_min))
    if atraso_max <= atraso_min:
        raise ValueError("sinal curto demais para a faixa de f0 pedida")

    trecho = r[atraso_min:atraso_max]
    k = int(np.argmax(trecho)) + atraso_min

    # Interpolação parabólica no domínio do atraso, mesmo truque de antes.
    if 0 < k < n - 1:
        a, b, c = r[k - 1], r[k], r[k + 1]
        denom = a - 2 * b + c
        if abs(denom) > 1e-30:
            k = k + 0.5 * (a - c) / denom
    return float(taxa / k)


@dataclass
class EstimativaF0:
    fft: float
    hps: float
    autocorrelacao: float
    consenso: float
    concordam: bool


def estimar_f0(x: np.ndarray, taxa: int, f_min: float = 40.0,
               f_max: float = 2000.0, n_fft: int | None = None,
               segundos: float = 1.0) -> EstimativaF0:
    """Roda os três métodos sobre o trecho central e devolve a mediana.

    `concordam` é True se os três caem dentro de 2 % um do outro. Quando é
    False, desconfie do resultado: normalmente significa sinal não harmônico,
    ruidoso, ou dois tons simultâneos.

    A mediana de três, e não a média, porque a falha típica é um método errar
    a oitava (fator 2, um erro enorme) enquanto os outros dois acertam. Média
    seria contaminada pelo destoante; mediana o ignora. Esse é o argumento
    geral para estatística robusta em estimação — ver 22-ruido-e-processos.
    """
    x = segmento_estavel(x, taxa, segundos)
    a = f0_por_fft(x, taxa, f_min, f_max, n_fft)
    b = f0_por_hps(x, taxa, f_min, f_max, n_fft=n_fft)
    c = f0_por_autocorrelacao(x, taxa, f_min, f_max)
    vals = np.array([a, b, c])
    consenso = float(np.median(vals))
    espalhamento = float(np.max(np.abs(vals - consenso)) / consenso)
    return EstimativaF0(fft=a, hps=b, autocorrelacao=c, consenso=consenso,
                        concordam=bool(espalhamento < 0.02))
