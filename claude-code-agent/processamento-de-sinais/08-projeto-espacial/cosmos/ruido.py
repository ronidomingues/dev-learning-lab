"""Ruído térmico e a equação do radiômetro.

O CONCEITO CENTRAL DESTE ARQUIVO
--------------------------------
Em radioastronomia não se mede potência em watts: mede-se em KELVIN. A razão é
prática — a potência de ruído de um resistor a temperatura T, numa banda B, é
P = k·T·B. Como todo receptor tem ruído, é natural exprimir QUALQUER potência
pela temperatura de um resistor que produziria a mesma coisa.

Assim, "a fonte tem 0,5 K de temperatura de antena" significa "a fonte entrega
tanta potência quanto um resistor a 0,5 K". É uma unidade de potência disfarçada
de temperatura, e ela deixa as contas de sensibilidade triviais.
"""

from __future__ import annotations

import numpy as np

from .constantes import K_BOLTZMANN, T_CMB


def potencia_de_ruido(t_sys_k: float, banda_hz: float) -> float:
    """Potência de ruído térmico, em watts.

        P = k · T_sys · B

    Parâmetros
    ----------
    t_sys_k   : temperatura de sistema, em kelvin.
    banda_hz  : largura de banda do receptor, em hertz.

    Exemplo numérico para calibrar a intuição: T_sys = 25 K e B = 100 MHz dão
    P = 1,38e-23 × 25 × 1e8 = 3,45e-14 W. Trinta e quatro femtowatts. É por isso
    que o primeiro amplificador de um radiotelescópio é criogênico: qualquer
    ruído que ele acrescente é comparável a tudo que se quer medir.
    """
    if t_sys_k <= 0 or banda_hz <= 0:
        raise ValueError("temperatura e banda devem ser positivas")
    return K_BOLTZMANN * t_sys_k * banda_hz


def temperatura_de_sistema(
    t_receptor_k: float,
    t_ceu_k: float = T_CMB,
    t_atmosfera_k: float = 0.0,
    t_solo_k: float = 0.0,
) -> float:
    """Soma as contribuições de ruído que entram na antena.

    T_sys = T_receptor + T_céu + T_atmosfera + T_solo(spillover)

    POR QUE SOMAR DIRETO: potências de fontes de ruído independentes somam-se
    linearmente (não em quadratura — isso vale para AMPLITUDES de sinais
    aleatórios, não para potências). Cada termo já é uma potência disfarçada de
    temperatura, então a soma é imediata.

    De onde vem cada termo, na prática:
    - t_receptor : ruído do primeiro amplificador (LNA). É o que se compra com
                   dinheiro e criogenia. Um LNA de 4 K custa uma fortuna.
    - t_ceu      : mínimo de 2,725 K (fundo cósmico) mais emissão da Galáxia,
                   que domina abaixo de ~1 GHz e cresce como f^-2,7.
    - t_atmosfera: oxigênio e vapor d'água. Desprezível em 1 GHz, dominante em
                   22 GHz (linha da água) e em 60 GHz (oxigênio).
    - t_solo     : o que a antena "vê" do chão pelas bordas do refletor
                   (spillover). O chão está a ~290 K, então até 1 % de vazamento
                   já acrescenta 2,9 K — comparável a todo o fundo cósmico.
    """
    for nome, v in [("t_receptor", t_receptor_k), ("t_ceu", t_ceu_k),
                    ("t_atmosfera", t_atmosfera_k), ("t_solo", t_solo_k)]:
        if v < 0:
            raise ValueError(f"{nome} não pode ser negativa")
    return t_receptor_k + t_ceu_k + t_atmosfera_k + t_solo_k


def radiometro(t_sys_k: float, banda_hz: float, tau_s: float,
               n_polarizacoes: int = 1) -> float:
    """A EQUAÇÃO DO RADIÔMETRO — a mais importante da radioastronomia prática.

        ΔT_min = T_sys / √(n_pol · B · τ)

    Devolve a menor variação de temperatura de antena detectável (1 sigma), em
    kelvin, com banda B e tempo de integração τ.

    POR QUE A RAIZ QUADRADA (e este é o "porquê" que vale o arquivo inteiro):

    B·τ é o número de amostras independentes que você coleta. Pelo teorema da
    amostragem, um sinal de banda B tem 2B graus de liberdade por segundo; em τ
    segundos, são ~2Bτ amostras reais, ou Bτ amostras complexas.

    Ao promediar N amostras de ruído, a MÉDIA do ruído não muda (é zero), mas o
    DESVIO PADRÃO da média cai por √N — porque variâncias de variáveis
    independentes somam, e a variância da média é σ²/N.

    Logo: mais tempo melhora a sensibilidade, mas com retorno decrescente.
    Dobrar a sensibilidade custa QUATRO vezes mais tempo de telescópio. É por
    isso que propostas de observação brigam por horas, e por que se investe em
    T_sys menor (criogenia) e em B maior (banda larga) antes de investir em τ:
    esses dois entram sem raiz quadrada, ou entram uma vez só.

    n_polarizacoes = 2 quando o receptor mede as duas polarizações e você as
    soma — é como observar duas vezes ao mesmo tempo, e ganha √2.
    """
    if t_sys_k <= 0:
        raise ValueError("T_sys deve ser positiva")
    if banda_hz <= 0 or tau_s <= 0:
        raise ValueError("banda e tempo de integração devem ser positivos")
    if n_polarizacoes not in (1, 2):
        raise ValueError("n_polarizacoes deve ser 1 ou 2")
    return t_sys_k / np.sqrt(n_polarizacoes * banda_hz * tau_s)


def tempo_necessario(t_sys_k: float, banda_hz: float, delta_t_alvo_k: float,
                     n_sigma: float = 5.0, n_polarizacoes: int = 1) -> float:
    """Inverte a equação do radiômetro: quantos segundos para detectar a n sigma?

    Esta é a forma da equação que aparece de fato numa proposta de observação:
    "quero detectar uma fonte de 1 mK com 5 sigma; de quanto tempo preciso?"

        τ = (n_sigma · T_sys / ΔT_alvo)² / (n_pol · B)

    Repare no QUADRADO: pedir 5 sigma em vez de 3 não custa 1,7× mais tempo,
    custa 2,8× mais. Rigor estatístico é caro, literalmente.
    """
    if delta_t_alvo_k <= 0:
        raise ValueError("a temperatura alvo deve ser positiva")
    return (n_sigma * t_sys_k / delta_t_alvo_k) ** 2 / (n_polarizacoes * banda_hz)


def gerar_ruido(n_amostras: int, t_sys_k: float, banda_hz: float,
                semente: int = 0) -> np.ndarray:
    """Gera ruído gaussiano branco com a POTÊNCIA correta para (T_sys, B).

    Devolve amostras cuja variância é exatamente k·T_sys·B (em watts).

    POR QUE GAUSSIANO: o ruído térmico é a soma de contribuições de um número
    enorme de portadores de carga independentes. Pelo teorema central do limite,
    a soma tende à gaussiana qualquer que seja a distribuição individual. Não é
    uma escolha de conveniência — é uma consequência.

    POR QUE BRANCO: as contribuições são descorrelacionadas no tempo em escalas
    muito maiores que o tempo de colisão dos portadores (~10⁻¹³ s), então dentro
    de qualquer banda de rádio o espectro é plano.

    A semente fixa torna toda a análise REPRODUTÍVEL — em pesquisa, um resultado
    que não se reproduz não é resultado.
    """
    if n_amostras <= 0:
        raise ValueError("n_amostras deve ser positivo")
    rng = np.random.default_rng(semente)
    potencia = potencia_de_ruido(t_sys_k, banda_hz)
    # standard_normal tem variância 1; multiplicar por √P dá variância P.
    return rng.standard_normal(n_amostras) * np.sqrt(potencia)


def integrar(x: np.ndarray, fator: int) -> np.ndarray:
    """Promedia blocos de `fator` amostras consecutivas (integração/binning).

    É o passo mais banal e mais poderoso do pipeline: reduz o volume de dados por
    `fator` e melhora a SNR por √fator, ao preço de resolução temporal.

    Implementado por reshape+mean, que é O(N) e vetorizado. As amostras que
    sobram no fim (N não múltiplo de `fator`) são DESCARTADAS explicitamente —
    truncar em silêncio é preferível a preencher com zeros, que criaria um degrau
    artificial no fim da série e um transiente espúrio na análise seguinte.
    """
    if fator < 1:
        raise ValueError("fator deve ser >= 1")
    if fator == 1:
        return np.asarray(x, dtype=np.float64)
    x = np.asarray(x, dtype=np.float64)
    n_util = (len(x) // fator) * fator
    if n_util == 0:
        raise ValueError(f"sinal com {len(x)} amostras é curto demais para "
                         f"integrar de {fator} em {fator}")
    return x[:n_util].reshape(-1, fator).mean(axis=1)


def snr_radiometrica(sinal_k: float, t_sys_k: float, banda_hz: float,
                     tau_s: float, n_polarizacoes: int = 1) -> float:
    """Quantos sigmas uma fonte de `sinal_k` kelvin produz nesta observação."""
    return sinal_k / radiometro(t_sys_k, banda_hz, tau_s, n_polarizacoes)
