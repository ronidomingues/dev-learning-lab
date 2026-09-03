"""Figuras: forma de onda, espectro e espectrograma.

matplotlib é importado dentro da função de propósito: quem só quer a análise
em texto (num servidor, num CI) não deve pagar o custo de importar a
biblioteca gráfica nem precisar dela instalada.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from scipy import signal


def painel(x: np.ndarray, taxa: int, caminho_png: str | Path,
           titulo: str = "Análise de sinal", f_max_plot: float = 5000.0) -> Path:
    """Gera um PNG com três painéis: onda, espectro em dB e espectrograma."""
    import matplotlib
    matplotlib.use("Agg")  # backend sem tela: funciona em servidor e em CI
    import matplotlib.pyplot as plt

    x = np.asarray(x, dtype=np.float64)
    t = np.arange(len(x)) / taxa

    fig, eixos = plt.subplots(3, 1, figsize=(10, 9))

    eixos[0].plot(t, x, linewidth=0.5)
    eixos[0].set_xlabel("tempo (s)")
    eixos[0].set_ylabel("amplitude")
    eixos[0].set_title(f"{titulo} — forma de onda")
    eixos[0].grid(alpha=0.3)

    # Espectro com janela Hann. Normalizamos pela soma da janela para que a
    # amplitude lida no gráfico corresponda à amplitude real da senoide.
    janela = np.hanning(len(x))
    X = np.abs(np.fft.rfft(x * janela)) / (np.sum(janela) / 2)
    freqs = np.fft.rfftfreq(len(x), 1 / taxa)
    eixos[1].plot(freqs, 20 * np.log10(np.maximum(X, 1e-12)), linewidth=0.7)
    eixos[1].set_xlim(0, min(f_max_plot, taxa / 2))
    eixos[1].set_ylim(-120, 5)
    eixos[1].set_xlabel("frequência (Hz)")
    eixos[1].set_ylabel("magnitude (dB)")
    eixos[1].set_title("Espectro (janela Hann)")
    eixos[1].grid(alpha=0.3)

    f, tt, Sxx = signal.spectrogram(x, fs=taxa, nperseg=1024, noverlap=768,
                                    window="hann")
    eixos[2].pcolormesh(tt, f, 10 * np.log10(np.maximum(Sxx, 1e-14)),
                        shading="gouraud")
    eixos[2].set_ylim(0, min(f_max_plot, taxa / 2))
    eixos[2].set_xlabel("tempo (s)")
    eixos[2].set_ylabel("frequência (Hz)")
    eixos[2].set_title("Espectrograma (1024 amostras, 75 % de sobreposição)")

    fig.tight_layout()
    caminho_png = Path(caminho_png)
    caminho_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(caminho_png, dpi=110)
    plt.close(fig)
    return caminho_png
