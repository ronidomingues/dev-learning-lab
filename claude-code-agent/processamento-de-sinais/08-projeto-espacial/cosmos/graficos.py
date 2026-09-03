"""Figuras do pipeline: cascata, perfil dobrado, plano de busca, aquisição.

matplotlib é importado DENTRO de cada função, de propósito: o pipeline de
análise deve rodar em servidor sem tela e em CI sem a biblioteca gráfica
instalada. Só quem pede figura paga o custo.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np


def _preparar():
    """Configura o matplotlib para backend sem tela e devolve o pyplot."""
    import matplotlib
    matplotlib.use("Agg")          # sem isto, falha em SSH/contêiner/CI
    import matplotlib.pyplot as plt
    return plt


def cascata(espectro: np.ndarray, freqs_mhz: np.ndarray, dt_s: float,
            caminho: str | Path, titulo: str = "Espectro dinâmico",
            t_max_s: float | None = None) -> Path:
    """Cascata (waterfall): frequência × tempo, com a intensidade em cor.

    É COMO O RADIOASTRÔNOMO OLHA OS DADOS BRUTOS. Um pulso disperso aparece
    como uma curva varrendo de cima para baixo; interferência terrestre (RFI)
    aparece como linha vertical (banda larga, instantânea) ou horizontal
    (frequência fixa, persistente). Saber distinguir os três padrões a olho é
    metade do ofício.
    """
    plt = _preparar()
    espectro = np.asarray(espectro, dtype=np.float64)
    n_amostras = espectro.shape[1]
    n_plot = n_amostras if t_max_s is None else min(n_amostras,
                                                    int(t_max_s / dt_s))

    fig, ax = plt.subplots(figsize=(11, 5))
    ax.imshow(
        espectro[:, :n_plot], aspect="auto", origin="lower", cmap="viridis",
        extent=[0, n_plot*dt_s, float(freqs_mhz[0]), float(freqs_mhz[-1])])
    ax.set_xlabel("tempo (s)")
    ax.set_ylabel("frequência (MHz)")
    ax.set_title(titulo)
    fig.tight_layout()
    caminho = Path(caminho); caminho.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(caminho, dpi=110); plt.close(fig)
    return caminho


def perfil(perfil_dobrado: np.ndarray, caminho: str | Path,
           titulo: str = "Perfil integrado") -> Path:
    """Perfil de pulso dobrado, com dois giros lado a lado.

    DOIS GIROS, e não um: é a convenção da área. Se o pulso cair perto da borda
    do período, com um giro só ele fica cortado ao meio e ilegível. Repetir o
    perfil deixa sempre um pulso inteiro visível.
    """
    plt = _preparar()
    p = np.asarray(perfil_dobrado, dtype=np.float64)
    duplo = np.concatenate([p, p])
    fase = np.arange(len(duplo)) / len(p)

    fig, ax = plt.subplots(figsize=(9, 4))
    ax.plot(fase, duplo, lw=1.2)
    ax.axvline(1.0, color="gray", ls="--", lw=0.8)   # fronteira entre os giros
    ax.set_xlabel("fase de rotação (dois giros)")
    ax.set_ylabel("intensidade (u.a.)")
    ax.set_title(titulo)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    caminho = Path(caminho); caminho.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(caminho, dpi=110); plt.close(fig)
    return caminho


def curva_dm(dms: np.ndarray, snrs: np.ndarray, dm_verdadeiro: float | None,
             caminho: str | Path) -> Path:
    """SNR em função do DM testado — a assinatura de uma detecção real.

    COMO SE LÊ: uma fonte astronômica verdadeira produz um pico ESTREITO no DM
    correto e cai dos dois lados. Interferência terrestre não sofre dispersão,
    então produz o máximo em DM = 0 e decai monotonicamente. **Um candidato cujo
    melhor DM é zero é RFI até prova em contrário** — este é o teste de triagem
    mais usado em busca de FRBs.
    """
    plt = _preparar()
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.plot(dms, snrs, "o-", lw=1.2, ms=3)
    if dm_verdadeiro is not None:
        ax.axvline(dm_verdadeiro, color="crimson", ls="--", lw=1,
                   label=f"DM verdadeiro = {dm_verdadeiro:g}")
        ax.legend()
    ax.set_xlabel("DM testado (pc·cm⁻³)")
    ax.set_ylabel("SNR do perfil (sigma)")
    ax.set_title("Curva de resposta em DM")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    caminho = Path(caminho); caminho.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(caminho, dpi=110); plt.close(fig)
    return caminho


def plano_aquisicao(matriz: np.ndarray, faixa_doppler_hz: float,
                    passo_doppler_hz: float, caminho: str | Path) -> Path:
    """Plano atraso × Doppler da aquisição — o que o receptor de GPS "vê".

    O pico único e agudo é o sinal encontrado. O resto é o piso de ruído.
    A altura relativa do pico é o ganho de processamento em ação.
    """
    plt = _preparar()
    m = np.asarray(matriz, dtype=np.float64)
    dopplers = np.arange(-faixa_doppler_hz,
                         faixa_doppler_hz + passo_doppler_hz, passo_doppler_hz)

    fig, ax = plt.subplots(figsize=(10, 5))
    im = ax.imshow(m, aspect="auto", origin="lower", cmap="magma",
                   extent=[0, m.shape[1], dopplers[0], dopplers[-1]])
    ax.set_xlabel("atraso (chips)")
    ax.set_ylabel("Doppler (Hz)")
    ax.set_title("Plano de aquisição — correlação em atraso × Doppler")
    fig.colorbar(im, ax=ax, label="|correlação|")
    fig.tight_layout()
    caminho = Path(caminho); caminho.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(caminho, dpi=110); plt.close(fig)
    return caminho
