"""Doppler: o efeito que atrapalha a comunicação e mede a velocidade.

O EFEITO
--------
Se emissor e receptor se aproximam com velocidade radial v, a frequência
recebida sobe. Se se afastam, desce.

    f_rx = f_tx · (1 − v_r/c)        [v_r > 0 = afastando; aproximação não relativística]

A aproximação vale enquanto v ≪ c. Para uma sonda a 20 km/s, v/c = 6,7e−5, e o
termo relativístico de segunda ordem (v²/2c² ≈ 2e−9) só importa em experimentos
de relatividade — que a DSN de fato faz.

POR QUE ISSO É INSTRUMENTO, E NÃO SÓ ESTORVO
--------------------------------------------
O rastreamento Doppler de DUAS VIAS (a Terra transmite, a sonda devolve
coerentemente, a Terra compara) mede a velocidade radial com precisão de fração
de milímetro por segundo. Com isso a NASA:

- determinou a massa e a estrutura interna de luas e planetas, medindo como a
  gravidade acelera a sonda (é assim que se descobriu o oceano de Europa e a
  estrutura interna de Ganimedes);
- mediu o campo gravitacional da Lua com o GRAIL (2011–2012), com duas naves
  medindo a distância entre si;
- testou a Relatividade Geral pelo atraso de Shapiro, com a Cassini em 2002,
  confirmando o parâmetro γ = 1 dentro de 2,3e−5;
- reconstruiu a trajetória da Voyager por décadas.

A "anomalia da Pioneer" — uma aceleração inesperada que intrigou a física por
20 anos e alimentou propostas de gravidade modificada — foi detectada e depois
EXPLICADA (2012) por análise Doppler: era radiação térmica anisotrópica da
própria sonda. Um resultado de processamento de sinais fechando um debate de
física fundamental.
"""

from __future__ import annotations

import numpy as np

from .constantes import C_LUZ


def desvio_doppler(f_tx_hz: float, v_radial_ms: float) -> float:
    """Desvio de frequência, em Hz. `v_radial_ms` positivo = AFASTANDO.

        Δf = −f_tx · v_r / c

    Sinal negativo para v>0: afastar-se BAIXA a frequência (redshift).

    Escala para calibrar a intuição: na banda X da DSN (8,42 GHz), cada km/s de
    velocidade radial desloca 28 kHz. Uma sonda a 20 km/s desloca 561 kHz — muito
    maior que a largura de banda do laço de rastreamento de portadora, que é de
    alguns hertz. Por isso o receptor precisa PREDIZER o Doppler a partir da
    efeméride antes de tentar travar; procurar às cegas seria inviável.
    """
    return -f_tx_hz * v_radial_ms / C_LUZ


def velocidade_a_partir_do_desvio(f_tx_hz: float, desvio_hz: float) -> float:
    """Inverte: dado o desvio medido, qual a velocidade radial (m/s)?

    É a medida científica propriamente dita. Toda a navegação de espaço profundo
    se apoia nesta linha, e a precisão dela é a precisão da órbita.
    """
    if f_tx_hz <= 0:
        raise ValueError("frequência de transmissão deve ser positiva")
    return -desvio_hz * C_LUZ / f_tx_hz


def doppler_duas_vias(f_tx_hz: float, v_radial_ms: float) -> float:
    """Doppler de ida e volta — o dobro do de uma via.

    POR QUE DOBRA: o sinal sofre Doppler ao chegar na sonda (que o vê deslocado)
    e de novo ao voltar (porque a sonda, em movimento, retransmite de um
    referencial que se move em relação à Terra). Os dois efeitos se somam.

    A DSN usa duas vias porque assim a referência de frequência é o MASER DE
    HIDROGÊNIO EM TERRA, não o oscilador da sonda — que é pequeno, envelhece e
    sofre variação térmica. Trocar o relógio de lugar melhora a precisão em
    ordens de grandeza. É uma decisão de arquitetura de sistema, não de
    algoritmo, e é a que mais importa.
    """
    return 2.0 * desvio_doppler(f_tx_hz, v_radial_ms)


def gerar_portadora_com_doppler(
    n_amostras: int,
    fs_hz: float,
    f0_hz: float,
    deriva_hz_por_s: float = 0.0,
    amplitude: float = 1.0,
    fase_inicial: float = 0.0,
) -> np.ndarray:
    """Portadora complexa cuja frequência varia linearmente no tempo (rampa Doppler).

    Devolve um sinal COMPLEXO (I + jQ), que é como todo receptor de rádio
    moderno representa o sinal em banda base. Usar complexo não é sofisticação:
    é necessário para distinguir frequência positiva de negativa, ou seja, para
    saber se a sonda se aproxima ou se afasta.

    A MATEMÁTICA DA RAMPA — e aqui está o erro nº 1 de quem implementa isto:

    A frequência instantânea é f(t) = f0 + k·t. A fase NÃO é 2π·f(t)·t: a fase é
    a INTEGRAL da frequência,

        φ(t) = 2π·∫f(t)dt = 2π·(f0·t + k·t²/2)

    Esquecer o fator ½ produz uma rampa com o dobro da inclinação, e o receptor
    nunca trava. É o mesmo ½ do chirp em `geracao.varredura` do projeto anterior.

    `deriva_hz_por_s` é a aceleração convertida em frequência: para a banda X,
    uma aceleração radial de 1 m/s² produz 28 Hz/s de deriva.
    """
    if fs_hz <= 0:
        raise ValueError("taxa de amostragem deve ser positiva")
    t = np.arange(n_amostras) / fs_hz
    fase = 2 * np.pi * (f0_hz * t + 0.5 * deriva_hz_por_s * t ** 2) + fase_inicial
    return amplitude * np.exp(1j * fase)


def corrigir_doppler(sinal: np.ndarray, fs_hz: float, f_estimada_hz: float,
                     deriva_hz_por_s: float = 0.0) -> np.ndarray:
    """Desfaz o Doppler multiplicando pela conjugada da rampa estimada.

    Multiplicar por e^{−jφ(t)} desloca o espectro de volta para a banda base.
    É a propriedade de deslocamento em frequência da tabela de Fourier, usada
    como ferramenta em vez de sofrida como efeito.

    Se a estimativa estiver certa, o resultado é uma portadora quase parada em
    0 Hz, e aí um filtro passa-baixa estreitíssimo (poucos hertz) pode ser
    aplicado — e é ESSE estreitamento que dá o ganho de SNR final. O sinal da
    Voyager é recuperado assim.
    """
    correcao = np.conj(gerar_portadora_com_doppler(
        len(sinal), fs_hz, f_estimada_hz, deriva_hz_por_s))
    return np.asarray(sinal) * correcao


def estimar_frequencia(sinal: np.ndarray, fs_hz: float,
                       n_fft: int | None = None) -> float:
    """Estima a frequência de uma portadora complexa por FFT + interpolação.

    Devolve a frequência em Hz, podendo ser NEGATIVA (o sinal é complexo, e o
    espectro não é simétrico — esta é justamente a vantagem).

    Usa a mesma interpolação parabólica em dB do capítulo 16 do curso, que dá
    precisão muito melhor que a resolução do bin.
    """
    x = np.asarray(sinal)
    n = len(x)
    n_fft = n_fft or int(2 ** np.ceil(np.log2(n)))
    if n_fft < n:
        raise ValueError("n_fft não pode ser menor que o sinal (truncaria dados)")

    janela = np.hanning(n)
    X = np.abs(np.fft.fft(x * janela, n=n_fft))
    k = int(np.argmax(X))

    # interpolação parabólica em dB, com vizinhos circulares (espectro é periódico)
    a, b, c = (20 * np.log10(max(X[(k + d) % n_fft], 1e-30)) for d in (-1, 0, 1))
    denom = a - 2 * b + c
    d = 0.5 * (a - c) / denom if abs(denom) > 1e-30 else 0.0

    freqs = np.fft.fftfreq(n_fft, 1 / fs_hz)
    passo = fs_hz / n_fft
    return float(freqs[k] + d * passo)


def estimar_deriva(sinal: np.ndarray, fs_hz: float, n_blocos: int = 8
                   ) -> tuple[float, float]:
    """Estima (frequência no instante central, deriva em Hz/s) por regressão.

    MÉTODO: fatia o sinal em blocos, estima a frequência de cada um, e ajusta uma
    reta por mínimos quadrados. A inclinação é a deriva.

    COMPROMISSO EXPLÍCITO: mais blocos dão melhor amostragem da rampa e pior
    estimativa por bloco (menos amostras ⟹ resolução pior). Oito é um meio-termo
    razoável; num receptor real isso é um parâmetro sintonizado por simulação.

    Receptores de verdade usam um laço fechado (PLL de 2ª ou 3ª ordem) que
    rastreia continuamente em vez de estimar em bloco. A estimativa em bloco é a
    fase de AQUISIÇÃO, que precede o travamento do laço.
    """
    x = np.asarray(sinal)
    if n_blocos < 2:
        raise ValueError("são necessários ao menos 2 blocos para estimar deriva")
    n_por_bloco = len(x) // n_blocos
    if n_por_bloco < 16:
        raise ValueError("blocos curtos demais para estimar frequência")

    tempos, freqs = [], []
    for i in range(n_blocos):
        bloco = x[i * n_por_bloco:(i + 1) * n_por_bloco]
        tempos.append((i + 0.5) * n_por_bloco / fs_hz)   # centro do bloco
        freqs.append(estimar_frequencia(bloco, fs_hz))

    deriva, intercepto = np.polyfit(tempos, freqs, 1)
    t_central = len(x) / (2 * fs_hz)
    return float(intercepto + deriva * t_central), float(deriva)
