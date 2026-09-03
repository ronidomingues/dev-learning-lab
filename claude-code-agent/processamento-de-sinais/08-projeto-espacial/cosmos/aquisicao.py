"""Códigos pseudoaleatórios e aquisição — como se acha um sinal abaixo do ruído.

O PROBLEMA
----------
A Voyager 1 está a mais de 24 bilhões de km. O sinal que chega à antena de 70 m
da DSN tem potência da ordem de 10⁻¹⁹ W — cerca de um bilionésimo de bilionésimo
de watt, dezenas de dB ABAIXO do ruído térmico do próprio receptor.

Não há amplificador que resolva isso: amplificar o sinal amplifica o ruído
junto. A solução é outra: **ganho de processamento por correlação**.

A IDEIA
-------
Em vez de transmitir cada bit de informação diretamente, multiplica-se cada bit
por uma sequência longa e conhecida de ±1 (o código PN, de *pseudo-noise*). O
sinal transmitido parece ruído — ocupa muita banda e tem pouca potência por
hertz. No receptor, correlaciona-se com a MESMA sequência: o sinal se acumula
coerentemente (fator N) e o ruído incoerentemente (fator √N).

    Ganho de processamento = 10·log₁₀(N) dB

Com N = 1023 (o código C/A do GPS), são 30 dB. Com os códigos muito mais longos
da DSN, bem mais. É por isso que o GPS funciona dentro de um carro, com o sinal
do satélite ~20 dB abaixo do ruído térmico.

É a mesma matemática do filtro casado e do folding de pulsar. Todo este projeto
é uma variação do mesmo princípio de integração coerente.
"""

from __future__ import annotations

import numpy as np


def lfsr_sequencia_m(grau: int, taps: tuple[int, ...] | None = None,
                     estado_inicial: int | None = None) -> np.ndarray:
    """Gera uma sequência-m (máximo comprimento) com um LFSR.

    Devolve um vetor de 0s e 1s de comprimento 2^grau − 1.

    O QUE É UM LFSR: *Linear Feedback Shift Register*. Um registrador de
    deslocamento em que a entrada é o XOR de algumas posições (os "taps"). Com
    taps escolhidos corretamente — os que correspondem a um POLINÔMIO PRIMITIVO
    sobre GF(2) — o registrador percorre TODOS os 2^grau − 1 estados não nulos
    antes de repetir. Daí "máximo comprimento".

    POR QUE NÃO PODE VALER ZERO: se o estado for todo zero, o XOR devolve zero
    para sempre e o registrador trava. Por isso a sequência tem 2^n − 1 e não 2^n
    elementos, e por isso o estado inicial padrão é todo 1.

    AS TRÊS PROPRIEDADES QUE TORNAM A SEQUÊNCIA ÚTIL (Golomb):
      1. Balanceamento: exatamente 2^(n−1) uns e 2^(n−1) − 1 zeros. Média ~zero.
      2. Autocorrelação de dois níveis: vale N no atraso zero e exatamente −1
         em TODOS os outros. Ou seja: um pico perfeito e um piso plano. É o que
         permite achar o atraso sem ambiguidade.
      3. Propriedade de janela: qualquer subsequência de n bits é única.

    A propriedade 2 é a razão de existir este arquivo. Uma sequência aleatória
    de verdade teria autocorrelação lateral flutuando em ±√N; a sequência-m tem
    exatamente −1. Determinismo bem escolhido bate aleatoriedade.

    `taps` são as posições realimentadas (contadas a partir de 1). Os padrões
    abaixo são polinômios primitivos clássicos e verificados.
    """
    # Polinômios primitivos por grau, na notação de posições de tap.
    # Grau 10 é o do código C/A do GPS.
    PADROES = {3: (3, 2), 4: (4, 3), 5: (5, 3), 6: (6, 5), 7: (7, 6),
               9: (9, 5), 10: (10, 7), 11: (11, 9)}
    if taps is None:
        if grau not in PADROES:
            raise ValueError(f"não tenho polinômio primitivo padrão para grau "
                             f"{grau}; passe `taps` explicitamente")
        taps = PADROES[grau]
    if grau < 2:
        raise ValueError("grau deve ser >= 2")

    n = 2 ** grau - 1
    # estado como lista de bits; todo-1 é a escolha padrão (nunca todo-zero)
    reg = [1] * grau if estado_inicial is None else \
        [(estado_inicial >> i) & 1 for i in range(grau)]
    if not any(reg):
        raise ValueError("estado inicial não pode ser todo zero (o LFSR travaria)")

    saida = np.empty(n, dtype=np.int8)
    for i in range(n):
        saida[i] = reg[-1]                       # bit que sai pela ponta
        # realimentação: XOR das posições de tap (índice 1-based -> 0-based)
        realim = 0
        for t in taps:
            realim ^= reg[t - 1]
        reg = [realim] + reg[:-1]                # desloca e insere na frente
    return saida


def codigo_pn(grau: int = 10) -> np.ndarray:
    """Sequência-m convertida para ±1 — o formato usado na modulação.

    Converter 0/1 para +1/−1 (mapeamento BPSK) é o que torna a correlação uma
    soma com sinal, e é o que faz o piso da autocorrelação ser −1 em vez de algo
    positivo. A conta é `1 - 2*bit`: bit 0 vira +1, bit 1 vira −1.
    """
    return (1 - 2 * lfsr_sequencia_m(grau).astype(np.float64))


def autocorrelacao_circular(codigo: np.ndarray) -> np.ndarray:
    """Autocorrelação circular do código, via FFT.

    Circular (e não linear) porque o código é transmitido repetidamente: o fim
    emenda com o começo. É exatamente o caso em que a convolução circular da FFT
    é o que se QUER, e não o artefato a evitar.

    Usa o teorema de Wiener-Khinchin: a autocorrelação é a transformada inversa
    do módulo ao quadrado do espectro. Custo O(N log N) em vez de O(N²).
    """
    c = np.asarray(codigo, dtype=np.float64)
    C = np.fft.fft(c)
    return np.real(np.fft.ifft(C * np.conj(C)))


def modular_bpsk(bits: np.ndarray, codigo: np.ndarray,
                 amostras_por_chip: int = 1) -> np.ndarray:
    """Espalha cada bit de dado multiplicando pelo código PN inteiro (DSSS).

    DSSS = *Direct Sequence Spread Spectrum*. Cada bit de informação vira N chips
    do código. A banda ocupada cresce N vezes e a densidade espectral de potência
    cai N vezes — o sinal se esconde sob o ruído, o que é bom para robustez
    (e, historicamente, para discrição militar: a técnica nasceu assim).

    `amostras_por_chip` sobreamostra cada chip, como faz um receptor real que
    digitaliza a uma taxa maior que a de chip para permitir sincronismo fino.
    """
    bits = np.asarray(bits, dtype=np.float64)
    if not np.all(np.isin(bits, (-1.0, 1.0))):
        raise ValueError("bits devem estar em formato ±1 (use 1-2*b)")
    espalhado = np.outer(bits, codigo).ravel()
    if amostras_por_chip > 1:
        espalhado = np.repeat(espalhado, amostras_por_chip)
    return espalhado


def adquirir(recebido: np.ndarray, codigo: np.ndarray, fs_hz: float,
             faixa_doppler_hz: float, passo_doppler_hz: float
             ) -> tuple[int, float, float, np.ndarray]:
    """AQUISIÇÃO 2-D: busca simultânea em ATRASO e em DOPPLER.

    Devolve (atraso em amostras, doppler em Hz, pico/ruído, matriz de busca).

    POR QUE 2-D — e este é o ponto conceitual do arquivo:

    A correlação só acumula coerentemente se o código local estiver alinhado
    **em tempo** com o recebido. Mas se houver Doppler, a fase do sinal gira
    durante a correlação, e a soma se cancela — mesmo com o atraso correto.

    Exemplo concreto: com 1 ms de integração, um Doppler de 1 kHz gira a fase um
    ciclo inteiro dentro da janela, e a correlação vai a zero. Por isso é preciso
    testar hipóteses de Doppler: para cada uma, remove-se a rotação e correlaciona-se.

    O resultado é uma matriz atraso × Doppler com um pico agudo na célula certa.
    É literalmente o que faz o chip de GPS do seu celular ao ligar ("aquisição
    a frio"), e o que a DSN faz para encontrar a portadora de uma sonda.

    IMPLEMENTAÇÃO: a correlação em cada hipótese é feita por FFT (teorema da
    correlação), o que custa O(N log N) em vez de O(N²) por hipótese.
    """
    x = np.asarray(recebido, dtype=np.complex128)
    c = np.asarray(codigo, dtype=np.float64)
    n = len(c)
    if len(x) < n:
        raise ValueError(f"sinal recebido ({len(x)}) menor que o código ({n})")
    x = x[:n]                                   # um período de código

    dopplers = np.arange(-faixa_doppler_hz, faixa_doppler_hz + passo_doppler_hz,
                         passo_doppler_hz)
    t = np.arange(n) / fs_hz
    C_conj = np.conj(np.fft.fft(c))             # calculado UMA vez, reusado

    matriz = np.empty((len(dopplers), n))
    for i, fd in enumerate(dopplers):
        # remove a hipótese de Doppler antes de correlacionar
        desgirado = x * np.exp(-2j * np.pi * fd * t)
        correl = np.fft.ifft(np.fft.fft(desgirado) * C_conj)
        matriz[i] = np.abs(correl)

    idx = np.unravel_index(np.argmax(matriz), matriz.shape)
    pico = matriz[idx]

    # Piso de ruído: mediana de tudo. A mediana (e não a média) porque é robusta
    # à presença do próprio pico e de eventuais lóbulos laterais fortes.
    piso = np.median(matriz)
    razao = float(pico / piso) if piso > 0 else float("inf")

    return int(idx[1]), float(dopplers[idx[0]]), razao, matriz


def adquirir_acumulado(recebido: np.ndarray, codigo: np.ndarray, fs_hz: float,
                       faixa_doppler_hz: float, passo_doppler_hz: float,
                       n_periodos: int) -> tuple[int, float, float, np.ndarray]:
    """Aquisição com ACUMULAÇÃO NÃO COERENTE de vários períodos de código.

    Quando um único período não basta, somam-se os MÓDULOS das matrizes de
    correlação de períodos sucessivos.

    POR QUE SOMAR MÓDULOS E NÃO OS COMPLEXOS: somar os complexos seria integração
    coerente, que dá ganho maior (N em vez de √N) — mas exige que a fase se
    mantenha alinhada de um período para o outro. Com Doppler residual ou
    oscilador instável, ela não se mantém, e a soma coerente CANCELA em vez de
    acumular. Tomar o módulo primeiro descarta a fase e torna a soma imune a
    isso, ao preço de um ganho menor. É a troca clássica entre coerente e não
    coerente, e todo receptor de GPS a faz.

    MEDIDO NESTE PROJETO (código de grau 10, SNR de entrada −20 dB):
        M =  1 período  -> FALHOU (achou atraso 955, o verdadeiro era 317)
        M =  4 períodos -> acertou atraso e Doppler
        M = 16, 64      -> acertou, com margem estável
    Ou seja: quatro períodos (4 ms) resolvem um caso em que um período não
    resolve. É exatamente o que um receptor faz ao "demorar para pegar sinal".
    """
    x = np.asarray(recebido, dtype=np.complex128)
    n = len(codigo)
    if n_periodos < 1:
        raise ValueError("n_periodos deve ser >= 1")
    if len(x) < n * n_periodos:
        raise ValueError(f"são necessárias {n*n_periodos} amostras para "
                         f"{n_periodos} períodos; recebi {len(x)}")

    acumulador = None
    for m in range(n_periodos):
        trecho = x[m * n:(m + 1) * n]
        _, _, _, matriz = adquirir(trecho, codigo, fs_hz, faixa_doppler_hz,
                                   passo_doppler_hz)
        acumulador = matriz if acumulador is None else acumulador + matriz

    dopplers = np.arange(-faixa_doppler_hz, faixa_doppler_hz + passo_doppler_hz,
                         passo_doppler_hz)
    idx = np.unravel_index(np.argmax(acumulador), acumulador.shape)
    piso = np.median(acumulador)
    razao = float(acumulador[idx] / piso) if piso > 0 else float("inf")
    return int(idx[1]), float(dopplers[idx[0]]), razao, acumulador


def ganho_de_processamento_db(n_chips: int) -> float:
    """Ganho de processamento em dB: 10·log₁₀(N).

    Traduzindo: com N = 1023 chips, 30,1 dB. Significa que um sinal 20 dB abaixo
    do ruído sai da correlação 10 dB acima dele — de indetectável a confortável.

    LIMITE HONESTO: este ganho só vale se a integração for COERENTE, isto é, se
    a fase se mantiver alinhada durante todos os N chips. Doppler não compensado,
    instabilidade de oscilador ou movimento da plataforma quebram a coerência e
    o ganho real fica abaixo do teórico. É por isso que a função `adquirir`
    precisa da dimensão Doppler.
    """
    if n_chips < 1:
        raise ValueError("número de chips deve ser >= 1")
    return 10.0 * np.log10(n_chips)
