"""Pulsares: extrair um sinal periódico que é individualmente invisível.

O OBJETO
--------
Um pulsar é uma estrela de nêutrons — 1,4 massa solar comprimida em ~20 km de
diâmetro — girando entre uma vez a cada 8 segundos e 716 vezes por segundo, com
um feixe de rádio que varre o espaço como um farol. Cada vez que o feixe cruza a
Terra, chega um pulso.

POR QUE ISSO IMPORTA CIENTIFICAMENTE
------------------------------------
1. São laboratórios de física extrema: densidade nuclear, campos magnéticos de
   10¹² gauss, gravidade forte. O pulsar binário de Hulse-Taylor deu o Nobel de
   1993 ao mostrar perda de energia por ondas gravitacionais — exatamente como
   a Relatividade Geral prevê.
2. São relógios. Pulsares de milissegundo rivalizam com relógios atômicos em
   estabilidade de longo prazo. Uma rede deles (Pulsar Timing Array) funciona
   como um detector de ondas gravitacionais do tamanho da Galáxia; em 2023
   NANOGrav, EPTA, PPTA e CPTA anunciaram evidência de um fundo estocástico.
3. São sondas do meio interestelar (via DM, ver dispersao.py) e potenciais
   sistemas de navegação autônoma para espaçonaves (XNAV, testado pela NASA na
   ISS com o instrumento NICER/SEXTANT em 2018).

O PROBLEMA DE PROCESSAMENTO
---------------------------
Um pulso individual está tipicamente MUITO abaixo do ruído do receptor. Somar
milhares de rotações no período correto (**folding**) faz o perfil emergir.
É integração coerente: sinal cresce com N, ruído com √N, SNR com √N.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from . import dispersao


def perfil_gaussiano(n_fase: int, largura_fracao: float = 0.03,
                     fase_pico: float = 0.35) -> np.ndarray:
    """Perfil de pulso: uma gaussiana estreita dentro de um período.

    `n_fase` é o número de bins em que se divide UM giro do pulsar.
    `largura_fracao` é a largura (sigma) como fração do período — pulsares reais
    têm ciclo de trabalho de 1 % a 10 %, por isso o padrão de 3 %.
    `fase_pico` é onde o pulso cai dentro do período; 0,35 e não 0,5 de propósito,
    para que os testes detectem um erro de alinhamento que um valor simétrico
    esconderia.

    Perfis reais são mais complexos (múltiplos componentes, assimetria), mas a
    gaussiana única captura o essencial e tem largura conhecida — o que permite
    verificar o resultado.
    """
    if n_fase < 8:
        raise ValueError("n_fase pequeno demais para representar um perfil")
    fase = np.arange(n_fase) / n_fase          # eixo de fase: 0 a 1 (um giro)
    d = fase - fase_pico
    # Distância circular: o perfil é periódico, então a 0,98 de distância 0,02
    # é MAIS PERTO que 0,98. Sem isto, o pulso seria cortado na borda do período.
    d = np.minimum(np.abs(d), 1.0 - np.abs(d))
    return np.exp(-0.5 * (d / largura_fracao) ** 2)


def sintetizar_observacao(
    periodo_s: float = 0.714,
    dm: float = 50.0,
    duracao_s: float = 60.0,
    dt_s: float = 1e-3,
    f_baixa_mhz: float = 400.0,
    f_alta_mhz: float = 800.0,
    n_canais: int = 64,
    amplitude_pulso: float = 0.05,
    sigma_ruido: float = 1.0,
    largura_fracao: float = 0.03,
    semente: int = 42,
) -> tuple[np.ndarray, np.ndarray]:
    """Cria um espectro dinâmico realista: pulsos dispersos afogados em ruído.

    Devolve (espectro (n_canais, n_amostras), freqs_mhz).

    Os padrões reproduzem uma observação plausível de radiotelescópio na banda
    de 400–800 MHz (a banda do CHIME, no Canadá, principal máquina de FRBs) com
    resolução de 1 ms.

    `amplitude_pulso = 0.05` com `sigma_ruido = 1.0` significa que **cada pulso
    individual está 26 dB abaixo do ruído** em cada canal. É invisível a olho nu
    e continuará invisível em qualquer gráfico da série bruta. Só o folding o
    revela — que é exatamente o ponto pedagógico.
    """
    if periodo_s <= 0 or duracao_s <= 0 or dt_s <= 0:
        raise ValueError("período, duração e passo devem ser positivos")
    if f_alta_mhz <= f_baixa_mhz:
        raise ValueError("f_alta deve ser maior que f_baixa")

    n_amostras = int(round(duracao_s / dt_s))
    # linspace inclui as duas pontas: a convenção varia entre instrumentos, e o
    # que importa é usar as MESMAS frequências na síntese e na análise.
    freqs = np.linspace(f_baixa_mhz, f_alta_mhz, n_canais)

    # 1) trem de pulsos limpo, idêntico em todos os canais (espectro plano).
    t = np.arange(n_amostras) * dt_s
    fase = (t / periodo_s) % 1.0                     # fase de rotação, 0 a 1
    n_fase = 1024
    perfil = perfil_gaussiano(n_fase, largura_fracao)
    # Amostra o perfil na fase de cada instante. É uma interpolação por vizinho
    # mais próximo — suficiente porque n_fase (1024) é muito maior que a
    # resolução efetiva em fase (período/dt ≈ 714 amostras por giro).
    trem = perfil[(fase * n_fase).astype(int) % n_fase] * amplitude_pulso
    limpo = np.tile(trem, (n_canais, 1))

    # 2) o meio interestelar dispersa o sinal.
    disperso = dispersao.aplicar_dispersao(limpo, freqs, dm, dt_s)

    # 3) o receptor acrescenta ruído térmico, independente em cada canal.
    rng = np.random.default_rng(semente)
    ruido = rng.standard_normal((n_canais, n_amostras)) * sigma_ruido

    return disperso + ruido, freqs


def dobrar(serie: np.ndarray, periodo_s: float, dt_s: float,
           n_fase: int = 64) -> np.ndarray:
    """FOLDING DE ÉPOCA — o coração da detecção de pulsar.

    Corta a série temporal em pedaços de um período e soma todos, alinhados pela
    fase. Devolve o perfil médio com `n_fase` bins.

    O ALGORITMO, PASSO A PASSO:
      1. para cada amostra i, calcule o instante t = i·dt;
      2. calcule a fase φ = (t / P) mod 1 — onde ela cai dentro do giro;
      3. converta φ em um bin de 0 a n_fase−1;
      4. acumule o valor da amostra nesse bin;
      5. divida cada bin pelo número de amostras que caíram nele.

    A implementação usa np.bincount, que faz os passos 4 e 5 em C, vetorizado.
    Um laço Python sobre 60 000 amostras levaria ~50 ms; o bincount leva ~0,5 ms.

    POR QUE FUNCIONA: as amostras que caem no mesmo bin de fase estão separadas
    por múltiplos exatos do período. Se o sinal é periódico com esse período,
    elas contêm o MESMO valor de sinal e valores INDEPENDENTES de ruído. Somar N
    delas multiplica o sinal por N e o ruído por √N.

    SENSIBILIDADE AO PERÍODO — e este é o ponto que costuma escapar: se o período
    usado estiver errado por δP, o pulso "escorrega" em fase ao longo da
    observação. Depois de T segundos, o escorregamento total é T·δP/P períodos.
    Para não borrar, é preciso δP/P < 1/(número de giros). Com 60 s e P = 0,714 s
    são 84 giros, exigindo precisão relativa melhor que ~1 %. Numa observação de
    horas, a exigência vira parte em 10⁻⁸ — e é por isso que timing de pulsar
    mede períodos com 15 casas decimais.
    """
    serie = np.asarray(serie, dtype=np.float64)
    if periodo_s <= 0 or dt_s <= 0:
        raise ValueError("período e passo devem ser positivos")
    if n_fase < 4:
        raise ValueError("n_fase deve ser >= 4")

    t = np.arange(len(serie)) * dt_s
    bins = ((t / periodo_s) % 1.0 * n_fase).astype(int) % n_fase

    soma = np.bincount(bins, weights=serie, minlength=n_fase)
    conta = np.bincount(bins, minlength=n_fase)
    if np.any(conta == 0):
        raise ValueError(
            f"observação curta demais: com {len(serie)} amostras e n_fase="
            f"{n_fase}, alguns bins de fase ficaram vazios. Reduza n_fase.")
    return soma / conta


def snr_perfil(perfil: np.ndarray, fracao_pulso: float = 0.15) -> float:
    """SNR do perfil dobrado, com a linha de base estimada dos bins FORA do pulso.

    Método (é o padrão da área, e o detalhe importa):
      1. ordena os bins e assume que os `1 − fracao_pulso` menores são só ruído;
      2. estima média e desvio padrão DESSES bins — a linha de base;
      3. SNR = (pico − linha de base) / desvio.

    POR QUE NÃO USAR TODOS OS BINS para estimar o ruído: o próprio pulso
    inflaria o desvio padrão e faria a SNR parecer menor — o sinal se
    autossabotaria. Excluir a região do pulso é obrigatório, e é um caso
    particular de estimação robusta.

    `fracao_pulso = 0.15` é conservador para pulsares de ciclo de trabalho baixo.
    Para um perfil largo, aumente — senão parte do pulso entra na linha de base.
    """
    perfil = np.asarray(perfil, dtype=np.float64)
    n_ruido = max(4, int(len(perfil) * (1.0 - fracao_pulso)))
    base = np.sort(perfil)[:n_ruido]
    sigma = base.std()
    if sigma <= 0:
        raise ValueError("linha de base sem dispersão — sinal sem ruído?")
    return float((perfil.max() - base.mean()) / sigma)


@dataclass
class ResultadoBusca:
    """Resultado de uma busca cega, com tudo que se precisa para decidir."""
    dm: float
    periodo_s: float
    snr: float
    perfil: np.ndarray


def buscar_dm(espectro: np.ndarray, freqs_mhz: np.ndarray, dms: np.ndarray,
              periodo_s: float, dt_s: float, n_fase: int = 64) -> ResultadoBusca:
    """Varre uma grade de DM, dobra em cada um, devolve o melhor.

    É o caso em que se conhece o período (pulsar já catalogado) e se quer medir
    ou refinar o DM. A curva SNR × DM tem um pico agudo no valor verdadeiro; a
    largura desse pico é a incerteza da medida.
    """
    melhor = None
    for dm in dms:
        serie = dispersao.dedispersar(espectro, freqs_mhz, dm, dt_s)
        perfil = dobrar(serie, periodo_s, dt_s, n_fase)
        snr = snr_perfil(perfil)
        if melhor is None or snr > melhor.snr:
            melhor = ResultadoBusca(dm=float(dm), periodo_s=periodo_s,
                                    snr=snr, perfil=perfil)
    if melhor is None:
        raise ValueError("grade de DM vazia")
    return melhor


def buscar_periodo(serie: np.ndarray, periodos: np.ndarray, dt_s: float,
                   n_fase: int = 64) -> ResultadoBusca:
    """Varre uma grade de períodos numa série já dedispersada.

    Complementa `buscar_dm`: aqui o DM é conhecido e o período não. Uma busca
    cega de verdade varre os DOIS ao mesmo tempo — um plano 2-D — e é por isso
    que procurar pulsares consome supercomputador.
    """
    melhor = None
    for p in periodos:
        perfil = dobrar(serie, p, dt_s, n_fase)
        snr = snr_perfil(perfil)
        if melhor is None or snr > melhor.snr:
            melhor = ResultadoBusca(dm=float("nan"), periodo_s=float(p),
                                    snr=snr, perfil=perfil)
    if melhor is None:
        raise ValueError("grade de períodos vazia")
    return melhor
