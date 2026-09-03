"""
portas.py — As sete portas clássicas, todas construídas a partir de NAND.

Cada função abaixo tem, no docstring, o CUSTO em portas NAND. Esse número é
medido pelos testes, não chutado: se você alterar a implementação e o custo
mudar, `testes.py` acusa.

Resumo dos custos (medidos):

    porta   | NANDs | por quê
    --------|-------|-------------------------------------------------
    NOT     |   1   | NAND com as duas entradas ligadas juntas
    AND     |   2   | NAND seguido de NOT
    OR      |   3   | De Morgan: A+B = NAND(¬A, ¬B) → 2 NOTs + 1 NAND
    NOR     |   4   | OR seguido de NOT
    XOR     |   4   | arranjo clássico de 4 NANDs
    XNOR    |   5   | XOR seguido de NOT
    BUFFER  |   2   | NOT duplo

Note que OR custa 50% mais que AND, e XOR custa o dobro. Isso não é curiosidade:
é a razão de somadores serem caros e de projetistas evitarem XOR em caminhos
críticos. Custo de porta é custo de área, de energia e de tempo.
"""

from nand import nand


def NOT(a):
    """Inversor. CUSTO: 1 NAND.

    Truque: NAND(a, a) = ¬(a·a) = ¬a.
    """
    return nand(a, a)


def AND(a, b):
    """CUSTO: 2 NANDs. AND = NOT(NAND). É a prova de que NAND é AND ao contrário."""
    return NOT(nand(a, b))


def OR(a, b):
    """CUSTO: 3 NANDs.

    Por De Morgan:  a + b = ¬(¬a · ¬b) = NAND(¬a, ¬b).
    Gasta 2 inversores e 1 NAND.
    """
    return nand(NOT(a), NOT(b))


def NOR(a, b):
    """CUSTO: 4 NANDs. NOR = NOT(OR)."""
    return NOT(OR(a, b))


def XOR(a, b):
    """CUSTO: 4 NANDs. Responde 1 quando as entradas são DIFERENTES.

    Arranjo clássico:
        n1 = NAND(a, b)
        n2 = NAND(a, n1)
        n3 = NAND(b, n1)
        s  = NAND(n2, n3)
    """
    n1 = nand(a, b)
    n2 = nand(a, n1)
    n3 = nand(b, n1)
    return nand(n2, n3)


def XNOR(a, b):
    """CUSTO: 5 NANDs. Responde 1 quando as entradas são IGUAIS.
    É o comparador de um bit."""
    return NOT(XOR(a, b))


def BUFFER(a):
    """CUSTO: 2 NANDs. Não muda o valor lógico; existe para reforçar o sinal
    elétrico. Num simulador é inútil; em silício é essencial."""
    return NOT(NOT(a))


# ---------------------------------------------------------------------------
# Versões de várias entradas — construídas em ÁRVORE, não em cadeia
# ---------------------------------------------------------------------------
# Por que em árvore? Porque o atraso de um circuito é o número de portas que o
# sinal atravessa (a PROFUNDIDADE), não o número total de portas. Ligar 8
# entradas em cadeia dá profundidade 7; em árvore, dá 3. Mesmo custo em portas,
# menos da metade do atraso. Ver ../20-circuitos-combinacionais.md.

def AND_n(*entradas):
    """AND de N entradas, em árvore. CUSTO: 2·(N-1) NANDs."""
    if len(entradas) < 2:
        raise ValueError("AND_n precisa de ao menos 2 entradas")
    nivel = list(entradas)
    while len(nivel) > 1:
        proximo = []
        for i in range(0, len(nivel) - 1, 2):
            proximo.append(AND(nivel[i], nivel[i + 1]))
        if len(nivel) % 2 == 1:          # sobrou um ímpar: sobe para o próximo nível
            proximo.append(nivel[-1])
        nivel = proximo
    return nivel[0]


def OR_n(*entradas):
    """OR de N entradas, em árvore. CUSTO: 3·(N-1) NANDs."""
    if len(entradas) < 2:
        raise ValueError("OR_n precisa de ao menos 2 entradas")
    nivel = list(entradas)
    while len(nivel) > 1:
        proximo = []
        for i in range(0, len(nivel) - 1, 2):
            proximo.append(OR(nivel[i], nivel[i + 1]))
        if len(nivel) % 2 == 1:
            proximo.append(nivel[-1])
        nivel = proximo
    return nivel[0]


def XOR_n(*entradas):
    """XOR de N entradas = bit de PARIDADE. Responde 1 se o número de 1s for
    ímpar. CUSTO: 4·(N-1) NANDs.

    É assim que memórias e redes detectam erro de um bit."""
    if len(entradas) < 2:
        raise ValueError("XOR_n precisa de ao menos 2 entradas")
    resultado = entradas[0]
    for e in entradas[1:]:
        resultado = XOR(resultado, e)
    return resultado
