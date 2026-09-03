"""Dispersão pelo meio interestelar — como um atraso vira uma medida de distância.

O FENÔMENO
----------
O espaço entre as estrelas não é vazio: é um plasma muito rarefeito (~0,03
elétrons por cm³). Uma onda de rádio atravessando plasma viaja mais devagar, e
o efeito depende da frequência: **as frequências baixas chegam depois**.

Um pulso emitido simultaneamente em todas as frequências chega à Terra
"varrido": primeiro o topo da banda, depois a base. Num gráfico de frequência
por tempo (o "espectro dinâmico", ou cascata), o pulso aparece como uma curva.

    freq
     alta │  ●
          │   ╲
          │    ╲___          ← o pulso chega mais tarde nas frequências baixas
     baixa│        ╲___●        segundo a lei 1/f²
          └──────────────── tempo

POR QUE ISSO É ÚTIL, E NÃO APENAS UM ESTORVO
--------------------------------------------
A curvatura mede a quantidade de elétrons no caminho — o DM (dispersion
measure), em pc·cm⁻³. Com um modelo da distribuição de elétrons livres na
Galáxia (NE2001, YMW16), converte-se DM em DISTÂNCIA. É a régua padrão para
pulsares, e foi o argumento decisivo para mostrar que as *fast radio bursts*
têm DM alto demais para serem galácticas — logo, vêm de outras galáxias.

O sinal que atrapalha é o mesmo que mede. Isso é comum em sensoriamento remoto:
o Doppler atrapalha a comunicação e mede a velocidade; a cintilação ionosférica
atrapalha o GPS e mede a ionosfera.
"""

from __future__ import annotations

import numpy as np

from .constantes import K_DISPERSAO


def atraso_dispersao(dm: float, f_mhz: float, f_ref_mhz: float | None = None
                     ) -> float:
    """Atraso de chegada, em segundos, na frequência `f_mhz` em relação a `f_ref_mhz`.

        Δt = K · DM · (1/f² − 1/f_ref²)          [K = 4148,808 MHz² pc⁻¹ cm³ s]

    Parâmetros
    ----------
    dm         : dispersion measure, em pc·cm⁻³ (coluna de elétrons livres).
    f_mhz      : frequência de interesse, em MHz.
    f_ref_mhz  : referência. Se None, usa infinito — isto é, o atraso absoluto
                 em relação a um fóton de frequência infinita, que não sofre
                 dispersão nenhuma. É a convenção da literatura de pulsares,
                 porque torna o atraso independente da banda do instrumento.

    Verificação à mão (usada no teste): DM = 50, de 800 para 400 MHz.
        Δt = 4148,808 × 50 × (1/400² − 1/800²)
           = 4148,808 × 50 × (6,25e−6 − 1,5625e−6)
           = 4148,808 × 50 × 4,6875e−6
           = 0,97237 s
    Quase um segundo de atraso entre o topo e a base da banda. Não é um detalhe
    fino: é a diferença entre ver um pulso e ver ruído.
    """
    if dm < 0:
        raise ValueError("DM não pode ser negativo (não existe coluna negativa "
                         "de elétrons)")
    if f_mhz <= 0:
        raise ValueError("frequência deve ser positiva, em MHz")
    termo_ref = 0.0 if f_ref_mhz is None else 1.0 / f_ref_mhz ** 2
    return K_DISPERSAO * dm * (1.0 / f_mhz ** 2 - termo_ref)


def dm_a_partir_do_atraso(atraso_s: float, f1_mhz: float, f2_mhz: float) -> float:
    """Inverte: dado o atraso medido entre dois canais, qual o DM?

    É esta a operação que transforma uma MEDIDA em CIÊNCIA. O observador não
    conhece o DM; ele mede o atraso e deduz o DM — e daí, a distância.

        DM = Δt / (K · (1/f1² − 1/f2²))
    """
    if f1_mhz == f2_mhz:
        raise ValueError("as duas frequências têm de ser diferentes, senão não "
                         "há atraso relativo a medir")
    denom = K_DISPERSAO * (1.0 / f1_mhz ** 2 - 1.0 / f2_mhz ** 2)
    return atraso_s / denom


def dispersao_maxima_tolerada(banda_mhz: float, f_centro_mhz: float,
                              largura_pulso_s: float) -> float:
    """Maior DM que o instrumento suporta sem borrar o pulso DENTRO de um canal.

    O PROBLEMA QUE ESTA FUNÇÃO EXPÕE: a dedispersão incoerente corrige o atraso
    ENTRE canais, mas dentro de cada canal ainda há dispersão residual, porque o
    canal tem largura finita. Se esse borrão residual ficar maior que a largura
    do pulso, o pulso se apaga e nenhum processamento posterior o recupera.

    Este é o motivo de instrumentos modernos usarem milhares de canais, e de
    existir a dedispersão COERENTE (que corrige a fase, não só o atraso, e não
    tem esse limite — ao preço de exigir os dados brutos em tensão, muito mais
    volumosos).
    """
    if banda_mhz <= 0 or f_centro_mhz <= 0 or largura_pulso_s <= 0:
        raise ValueError("banda, frequência e largura devem ser positivas")
    # Δt ≈ 2·K·DM·Δf/f³ (derivada de K·DM/f² em relação a f, vezes a largura)
    return largura_pulso_s * f_centro_mhz ** 3 / (2 * K_DISPERSAO * banda_mhz)


def aplicar_dispersao(espectro: np.ndarray, freqs_mhz: np.ndarray, dm: float,
                      dt_s: float, f_ref_mhz: float | None = None) -> np.ndarray:
    """Aplica dispersão a um espectro dinâmico limpo — o SIMULADOR do meio.

    `espectro` tem forma (n_canais, n_amostras): uma linha por canal de
    frequência, uma coluna por instante. É exatamente o formato que sai de um
    banco de filtros de radiotelescópio (e o formato dos arquivos PSRFITS/filterbank).

    Cada canal é deslocado no tempo pelo seu próprio atraso, arredondado para o
    número inteiro de amostras mais próximo.

    LIMITAÇÃO DECLARADA: arredondar para amostra inteira introduz erro de até
    meia amostra por canal. Para simulação didática é irrelevante; para timing
    de precisão (que mede atrasos em nanossegundos) seria inaceitável, e usa-se
    deslocamento por fase no domínio da frequência.
    """
    espectro = np.asarray(espectro, dtype=np.float64)
    freqs_mhz = np.asarray(freqs_mhz, dtype=np.float64)
    if espectro.shape[0] != len(freqs_mhz):
        raise ValueError(f"espectro tem {espectro.shape[0]} canais mas foram "
                         f"dadas {len(freqs_mhz)} frequências")

    saida = np.zeros_like(espectro)
    for i, f in enumerate(freqs_mhz):
        # np.roll desloca circularmente. Aqui isso é aceitável e até desejável:
        # simula uma observação contínua, em que o pulso anterior "entra" pela
        # borda. Num pipeline real de arquivo finito, usaríamos deslocamento com
        # preenchimento por ruído, não circular.
        n_desloca = int(round(atraso_dispersao(dm, f, f_ref_mhz) / dt_s))
        saida[i] = np.roll(espectro[i], n_desloca)
    return saida


def dedispersar(espectro: np.ndarray, freqs_mhz: np.ndarray, dm: float,
                dt_s: float, f_ref_mhz: float | None = None) -> np.ndarray:
    """DEDISPERSÃO INCOERENTE: desfaz o atraso canal a canal e soma tudo.

    Devolve uma série temporal 1-D — a soma dos canais já alinhados.

    O ALGORITMO, EM UMA FRASE: se o canal `i` chegou `k` amostras atrasado,
    adiante-o `k` amostras; depois some todos os canais. Se o DM usado for o
    verdadeiro, os pulsos de todos os canais coincidem e somam-se COERENTEMENTE
    (a amplitude cresce com o número de canais). O ruído, sendo independente
    entre canais, soma-se INCOERENTEMENTE (cresce com a raiz). Ganho de SNR:
    √n_canais.

    É a mesma matemática do filtro casado e do folding de pulsar. Este projeto
    inteiro é, no fundo, três aplicações do mesmo princípio.

    Se o DM usado estiver errado, os pulsos não coincidem, a soma os borra, e o
    pico desaparece — é exatamente essa sensibilidade que permite MEDIR o DM,
    testando muitos valores e escolhendo o que maximiza o pico.
    """
    espectro = np.asarray(espectro, dtype=np.float64)
    freqs_mhz = np.asarray(freqs_mhz, dtype=np.float64)
    if espectro.shape[0] != len(freqs_mhz):
        raise ValueError("número de canais não bate com o de frequências")

    acumulador = np.zeros(espectro.shape[1], dtype=np.float64)
    for i, f in enumerate(freqs_mhz):
        n_desloca = int(round(atraso_dispersao(dm, f, f_ref_mhz) / dt_s))
        # sinal NEGATIVO: aqui desfazemos o atraso que `aplicar_dispersao` pôs.
        acumulador += np.roll(espectro[i], -n_desloca)
    return acumulador


def plano_dm_tempo(espectro: np.ndarray, freqs_mhz: np.ndarray,
                   dms: np.ndarray, dt_s: float,
                   f_ref_mhz: float | None = None) -> np.ndarray:
    """Dedispersa para MUITOS valores de DM — a busca cega por uma fonte nova.

    Devolve matriz (n_dms, n_amostras). Cada linha é a série dedispersada para
    um DM candidato.

    POR QUE ISTO EXISTE: ao procurar uma fonte desconhecida (uma FRB, um pulsar
    ainda não catalogado), não se sabe o DM. Testa-se uma grade inteira. O DM
    verdadeiro é o que produz o maior pico.

    CUSTO: é O(n_dms × n_canais × n_amostras) — a operação mais cara de todo o
    pipeline de busca, e a razão de existirem algoritmos dedicados (tree
    dedispersion, FDMT) e aceleração em GPU/FPGA. Uma busca real varre milhares
    de DMs sobre terabytes por noite.
    """
    return np.vstack([dedispersar(espectro, freqs_mhz, dm, dt_s, f_ref_mhz)
                      for dm in dms])
