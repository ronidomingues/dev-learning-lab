"""Estatística de detecção — quando um pico é descoberta e quando é acaso.

A PERGUNTA QUE ESTE ARQUIVO RESPONDE
------------------------------------
Você varreu 10 000 combinações de DM e período e achou um pico de 6 sigma.
Isso é um pulsar novo, ou é o maior valor que 10 000 sorteios de ruído
produziriam de qualquer forma?

Essa distinção separa descoberta de constrangimento público. Vários "sinais"
famosos morreram aqui — e o caso mais instrutivo é o **BICEP2 (2014)**, que
anunciou ondas gravitacionais primordiais e depois se mostrou poeira galáctica:
não foi erro de estatística, mas de modelo de fundo. A lição vale igual: o piso
precisa ser entendido antes de o pico ser celebrado.
"""

from __future__ import annotations

import numpy as np
from scipy import special, stats


def probabilidade_falso_alarme(limiar_sigma: float, n_tentativas: int = 1
                               ) -> float:
    """Probabilidade de que RUÍDO PURO produza ao menos um pico acima do limiar.

    Para uma única tentativa e ruído gaussiano, a probabilidade de exceder n
    sigmas (de um lado só) é Q(n) = ½·erfc(n/√2).

    Com N tentativas independentes, a probabilidade de ao menos uma exceder é

        P = 1 − (1 − Q)^N

    ESTE É O "PROBLEMA DAS COMPARAÇÕES MÚLTIPLAS" (em física de partículas
    chama-se *look-elsewhere effect*), e é onde mais se erra na prática.

    Números que valem memorizar:
      3 sigma, 1 tentativa      -> 1 em 741        (nada demais)
      5 sigma, 1 tentativa      -> 1 em 3,5 milhões
      5 sigma, 10⁶ tentativas   -> ~25 % !!!       (nem um pouco convincente)

    Ou seja: **"5 sigma" não significa nada sem dizer quantas tentativas foram
    feitas.** É por isso que buscas de pulsar exigem 8 a 10 sigma, e por que
    física de partículas fixou 5 sigma para uma busca com poucos graus de
    liberdade.
    """
    if limiar_sigma < 0:
        raise ValueError("limiar em sigma não pode ser negativo")
    if n_tentativas < 1:
        raise ValueError("n_tentativas deve ser >= 1")

    q = 0.5 * special.erfc(limiar_sigma / np.sqrt(2.0))
    # Para q·N pequeno, 1−(1−q)^N sofre cancelamento catastrófico em ponto
    # flutuante. expm1/log1p calculam a mesma coisa com precisão total.
    return float(-np.expm1(n_tentativas * np.log1p(-q)))


def limiar_para_falso_alarme(pfa_alvo: float, n_tentativas: int = 1) -> float:
    """Inverte: que limiar em sigma garante a taxa de falso alarme desejada?

    É a forma usada ao PROJETAR um pipeline: "quero no máximo 1 % de chance de
    um falso positivo em toda a busca; a partir de quantos sigmas eu reporto?"

    Resolve q = 1 − (1 − pfa)^(1/N) e inverte a gaussiana.
    """
    if not 0 < pfa_alvo < 1:
        raise ValueError("a probabilidade alvo deve estar em (0, 1)")
    if n_tentativas < 1:
        raise ValueError("n_tentativas deve ser >= 1")
    q = -np.expm1(np.log1p(-pfa_alvo) / n_tentativas)
    return float(stats.norm.isf(q))


def tentativas_independentes_busca(n_dms: int, n_periodos: int,
                                   n_fase: int = 1) -> int:
    """Estimativa do número de tentativas independentes numa busca em grade.

    AVISO DE HONESTIDADE — e ele é importante: o produto n_dms × n_periodos ×
    n_fase SUPERESTIMA o número de tentativas independentes, porque células
    vizinhas da grade são CORRELACIONADAS (um DM errado por pouco ainda produz
    parte do pico). O número efetivo é menor, e determiná-lo com rigor exige
    simulação Monte Carlo com ruído puro — que é exatamente o que colaborações
    seriamente fazem antes de anunciar.

    Esta função devolve o limite superior. Usá-lo torna o teste CONSERVADOR:
    você exigirá mais sigma do que o estritamente necessário. Em busca de
    descoberta, errar para o conservador é a direção certa de errar.
    """
    for nome, v in [("n_dms", n_dms), ("n_periodos", n_periodos),
                    ("n_fase", n_fase)]:
        if v < 1:
            raise ValueError(f"{nome} deve ser >= 1")
    return int(n_dms) * int(n_periodos) * int(n_fase)


def snr_necessaria(sinal_relativo: float, n_amostras: int) -> float:
    """SNR de saída após integração coerente de n amostras.

        SNR_saída = SNR_entrada · √n          (em razão de amplitude)

    Reescrito em dB: ganho = 10·log₁₀(n) em potência.

    Serve para responder "quanto tempo preciso integrar?" antes de gastar tempo
    de telescópio — a mesma pergunta que a equação do radiômetro responde, aqui
    na forma de contagem de amostras.
    """
    if n_amostras < 1:
        raise ValueError("n_amostras deve ser >= 1")
    return sinal_relativo * np.sqrt(n_amostras)


def resumo_deteccao(snr_medida: float, n_tentativas: int) -> dict:
    """Empacota o veredito de uma detecção, pronto para relatório.

    Devolve dicionário com a SNR, o número de tentativas, a probabilidade de
    falso alarme corrigida, e uma classificação verbal.

    Os cortes usados (marginal / candidato / detecção) seguem a prática de busca
    de pulsares, em que se exige folga por causa de interferência de rádio (RFI),
    que não é gaussiana e produz caudas muito mais pesadas que a teoria prevê.
    Em dados reais, o piso NUNCA é tão bem comportado quanto o modelo.
    """
    pfa = probabilidade_falso_alarme(snr_medida, n_tentativas)
    if pfa > 0.05:
        veredito = "ruído — compatível com acaso"
    elif pfa > 1e-3:
        veredito = "marginal — precisa de mais integração"
    elif pfa > 1e-6:
        veredito = "candidato — exige confirmação em outra observação"
    else:
        veredito = "detecção"
    return {
        "snr_sigma": float(snr_medida),
        "tentativas": int(n_tentativas),
        "prob_falso_alarme": pfa,
        "veredito": veredito,
    }
