"""
combinacional.py — Circuitos SEM memória: a saída depende só das entradas de agora.

Ordem de leitura recomendada: meio somador → somador completo → somador de 4 bits
→ multiplexador → decodificador → comparador → ULA.

CONVENÇÃO DE BITS deste projeto
-------------------------------
Um número de 4 bits é uma lista Python de 4 elementos, do MENOS significativo
para o MAIS significativo (little-endian de bits):

    [1, 1, 0, 1]  =  1·1 + 1·2 + 0·4 + 1·8  =  11

Escolhi essa ordem porque é a que o somador percorre naturalmente (o "vai um"
anda do bit 0 para cima), e é como o hardware é desenhado. Ao imprimir para
humanos, a ordem é invertida — ver `bits_para_texto`.
"""

from nand import nand
from portas import NOT, AND, OR, XOR, XNOR, AND_n, OR_n

LARGURA = 4  # este computador é de 4 bits (um "nibble")


# ---------------------------------------------------------------------------
# Conversões (utilidades de teste — NÃO fazem parte do hardware)
# ---------------------------------------------------------------------------

def int_para_bits(n, largura=LARGURA):
    """13 -> [1, 0, 1, 1]  (LSB primeiro). Aceita 0..2^largura-1."""
    if not 0 <= n < 2 ** largura:
        raise ValueError(f"{n} não cabe em {largura} bits")
    return [(n >> i) & 1 for i in range(largura)]


def bits_para_int(bits):
    """[1, 0, 1, 1] -> 13"""
    return sum(bit << i for i, bit in enumerate(bits))


def bits_para_texto(bits):
    """[1, 0, 1, 1] -> '1101'  (MSB primeiro, como se escreve no papel)."""
    return "".join(str(b) for b in reversed(bits))


# ---------------------------------------------------------------------------
# 1. Somadores
# ---------------------------------------------------------------------------

def meio_somador(a, b):
    """Soma dois bits. Devolve (soma, vai_um). CUSTO: 6 NANDs (XOR 4 + AND 2).

        a b | soma vai_um
        0 0 |  0     0
        0 1 |  1     0
        1 0 |  1     0
        1 1 |  0     1     <- 1+1 = 2 = binário "10"

    "Meio" porque não aceita um vai-um vindo da casa anterior. Serve só para
    o bit menos significativo.
    """
    return XOR(a, b), AND(a, b)


def somador_completo(a, b, vem_um):
    """Soma três bits (dois operandos + o vai-um da casa anterior).
    Devolve (soma, vai_um). CUSTO: 9 NANDs.

    Esta é A peça mais importante da aritmética de computadores. Implementação
    direta em NAND, mais barata que juntar dois meio-somadores (que custaria 15):

        n1 = NAND(a, b)
        n2 = NAND(a, n1)          n3 = NAND(b, n1)
        s1 = NAND(n2, n3)         # s1 = a XOR b
        n4 = NAND(s1, vem_um)
        n5 = NAND(s1, n4)         n6 = NAND(vem_um, n4)
        soma  = NAND(n5, n6)      # soma = a XOR b XOR vem_um
        vai_um = NAND(n1, n4)     # = a·b + (a XOR b)·vem_um
    """
    n1 = nand(a, b)
    n2 = nand(a, n1)
    n3 = nand(b, n1)
    s1 = nand(n2, n3)
    n4 = nand(s1, vem_um)
    n5 = nand(s1, n4)
    n6 = nand(vem_um, n4)
    soma = nand(n5, n6)
    vai_um = nand(n1, n4)
    return soma, vai_um


def somador4(a, b, vem_um=0):
    """Somador de 4 bits por PROPAGAÇÃO DE VAI-UM (ripple-carry).
    Devolve (lista de 4 bits, vai_um final). CUSTO: 36 NANDs (4 × 9).

    Limitação importante: o bit 3 só pode calcular depois que o vai-um
    atravessou os bits 0, 1 e 2. O atraso cresce LINEARMENTE com a largura —
    é por isso que ninguém faz somador de 64 bits assim. A alternativa
    (carry-lookahead) está em ../20-circuitos-combinacionais.md.
    """
    soma = []
    vai = vem_um
    for i in range(LARGURA):
        s, vai = somador_completo(a[i], b[i], vai)
        soma.append(s)
    return soma, vai


def complemento_dois(a):
    """Devolve -a na representação de complemento de dois. CUSTO: 4 NOTs + somador4.

    Regra: inverta todos os bits e some 1. Por que funciona está explicado em
    ../20-circuitos-combinacionais.md, seção 2.
    """
    invertido = [NOT(bit) for bit in a]
    resultado, _ = somador4(invertido, int_para_bits(0), 1)
    return resultado


def subtrator4(a, b):
    """a - b em complemento de dois. Devolve (resultado, nao_houve_emprestimo).

    Truque de projeto: NÃO se constrói um subtrator. Reaproveita-se o somador,
    invertendo b e entrando com vai_um=1. Uma ULA real faz exatamente isso —
    o mesmo silício soma e subtrai, e o bit de controle escolhe.
    """
    b_invertido = [NOT(bit) for bit in b]
    return somador4(a, b_invertido, 1)


# ---------------------------------------------------------------------------
# 2. Seleção: multiplexadores
# ---------------------------------------------------------------------------

def mux2(a, b, s):
    """Multiplexador 2→1. Deixa passar `a` se s=0, `b` se s=1. CUSTO: 4 NANDs.

        saída = (a · ¬s) + (b · s)

    Implementado direto em NAND:
        NAND( NAND(a, ¬s), NAND(b, s) )

    O mux é a peça mais repetida de um processador. Cada "escolha" do hardware
    — qual registrador ler, qual resultado gravar, de onde vem o próximo
    endereço — é um mux.
    """
    ns = NOT(s)
    return nand(nand(a, ns), nand(b, s))


def mux2_bus(a, b, s):
    """Mux 2→1 sobre 4 bits. CUSTO: 4 NOTs + 12 NANDs = 16 NANDs.
    (O inversor de `s` poderia ser compartilhado; deixei explícito por clareza.)"""
    return [mux2(a[i], b[i], s) for i in range(LARGURA)]


def mux4(entradas, s0, s1):
    """Multiplexador 4→1 sobre bits soltos. CUSTO: 3 muxes = 12 NANDs.
    `entradas` é uma lista de 4 bits; (s1,s0) escolhe qual passa."""
    baixo = mux2(entradas[0], entradas[1], s0)
    alto = mux2(entradas[2], entradas[3], s0)
    return mux2(baixo, alto, s1)


def mux8(entradas, s0, s1, s2):
    """Multiplexador 8→1. CUSTO: 7 muxes = 28 NANDs."""
    baixo = mux4(entradas[0:4], s0, s1)
    alto = mux4(entradas[4:8], s0, s1)
    return mux2(baixo, alto, s2)


# ---------------------------------------------------------------------------
# 3. Endereçamento: decodificadores
# ---------------------------------------------------------------------------

def decodificador2x4(a0, a1):
    """Transforma um número de 2 bits em "acione UMA linha entre 4".
    CUSTO: 2 NOTs + 4 ANDs = 10 NANDs.

        (a1,a0) = 00 -> [1,0,0,0]
        (a1,a0) = 10 -> [0,0,1,0]

    É o circuito que encontra a palavra certa dentro de uma memória. Numa
    memória de 4 GB são 32 bits de endereço e um decodificador gigantesco —
    construído em árvore, nunca de uma vez.
    """
    n0, n1 = NOT(a0), NOT(a1)
    return [
        AND(n1, n0),   # linha 0
        AND(n1, a0),   # linha 1
        AND(a1, n0),   # linha 2
        AND(a1, a0),   # linha 3
    ]


def decodificador4x16(endereco):
    """Endereço de 4 bits -> 16 linhas, uma só ativa.
    CUSTO: 4 NOTs + 16 ANDs de 4 entradas = 4 + 16·6 = 100 NANDs."""
    n = [NOT(bit) for bit in endereco]
    linhas = []
    for alvo in range(16):
        termos = []
        for i in range(LARGURA):
            termos.append(endereco[i] if (alvo >> i) & 1 else n[i])
        linhas.append(AND_n(*termos))
    return linhas


# ---------------------------------------------------------------------------
# 4. Comparação
# ---------------------------------------------------------------------------

def igual4(a, b):
    """Responde 1 se os dois números de 4 bits forem iguais.
    CUSTO: 4 XNORs (5 cada) + AND de 4 entradas (6) = 26 NANDs.

    Cada XNOR pergunta "estes dois bits batem?"; o AND exige que TODOS batam."""
    coincidencias = [XNOR(a[i], b[i]) for i in range(LARGURA)]
    return AND_n(*coincidencias)


def eh_zero(a):
    """Responde 1 se o número for zero. CUSTO: OR de 4 entradas (9) + NOT (1) = 10.

    É a flag Z (zero) de qualquer processador — a que faz `if (x == 0)` funcionar."""
    return NOT(OR_n(*a))


def maior_ou_igual4(a, b):
    """a >= b, sem sinal. CUSTO: subtrator4 (40) + nada mais.

    Truque: em complemento de dois, o vai-um final da subtração a-b vale 1
    exatamente quando NÃO houve empréstimo, ou seja, quando a >= b.
    """
    _, vai_um = subtrator4(a, b)
    return vai_um


# ---------------------------------------------------------------------------
# 5. A ULA — Unidade Lógica e Aritmética
# ---------------------------------------------------------------------------

# Códigos de operação da ULA (3 bits de controle)
ULA_SOMA = 0b000
ULA_SUB = 0b001
ULA_AND = 0b010
ULA_OR = 0b011
ULA_XOR = 0b100
ULA_NOT_A = 0b101
ULA_PASSA_A = 0b110
ULA_PASSA_B = 0b111


def ula4(a, b, op):
    """A ULA de 4 bits: 8 operações, escolhidas por 3 bits de controle.

    Devolve (resultado, flag_vai_um, flag_zero).
    CUSTO medido: 242 NANDs — cerca de 60 por bit de largura.
    (`testes.py` verifica esse número; se você mudar a implementação e ele
    mudar, o teste acusa.)

    O ponto de projeto mais importante aqui: a ULA calcula TODAS as oito
    operações ao mesmo tempo, o tempo todo, e um multiplexador joga fora sete
    resultados. Parece desperdício absurdo — e é, em energia. Mas é mais rápido
    e mais simples que ligar e desligar blocos, e o mux escolhe em profundidade
    3. Processadores reais fazem exatamente isso; a técnica de desligar o que
    não se usa (clock gating, power gating) só apareceu quando energia virou o
    gargalo, nos anos 2000. Ver ../40-da-porta-ao-computador.md.
    """
    s0, s1, s2 = op & 1, (op >> 1) & 1, (op >> 2) & 1

    soma, vai_soma = somador4(a, b, 0)
    sub, vai_sub = subtrator4(a, b)
    e_bit = [AND(a[i], b[i]) for i in range(LARGURA)]
    ou_bit = [OR(a[i], b[i]) for i in range(LARGURA)]
    xor_bit = [XOR(a[i], b[i]) for i in range(LARGURA)]
    nao_a = [NOT(a[i]) for i in range(LARGURA)]

    resultado = []
    for i in range(LARGURA):
        candidatos = [
            soma[i],      # 000
            sub[i],       # 001
            e_bit[i],     # 010
            ou_bit[i],    # 011
            xor_bit[i],   # 100
            nao_a[i],     # 101
            a[i],         # 110
            b[i],         # 111
        ]
        resultado.append(mux8(candidatos, s0, s1, s2))

    vai_um = mux2(vai_soma, vai_sub, s0)   # só faz sentido em SOMA/SUB
    zero = eh_zero(resultado)
    return resultado, vai_um, zero


# ---------------------------------------------------------------------------
# 6. Deslocador (shifter)
# ---------------------------------------------------------------------------

def desloca_esquerda(a):
    """Multiplica por 2. CUSTO: 0 NANDs — é só refiação!

    Deslocar não gasta porta nenhuma: basta ligar o fio do bit 0 na posição 1.
    É por isso que `x * 2` é infinitamente mais barato que `x * 3` em hardware,
    e por que compiladores trocam multiplicações por potências de 2 por shifts.
    """
    return [0] + a[:LARGURA - 1]


def desloca_direita(a):
    """Divide por 2 (sem sinal). CUSTO: 0 NANDs."""
    return a[1:] + [0]
