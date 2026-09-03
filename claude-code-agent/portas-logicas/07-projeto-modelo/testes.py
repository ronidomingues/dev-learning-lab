"""
testes.py — Suíte de testes do computador de 4 bits.

Sem dependência externa: nem pytest, nem unittest. Um projeto de ensino não
deve exigir que você instale nada para verificar que funciona.

Rode com:  python3 testes.py

Três tipos de teste convivem aqui, e a distinção importa:

  1. FUNCIONAIS  — o circuito produz a saída certa? Vários são EXAUSTIVOS:
     percorrem todas as entradas possíveis. Circuitos pequenos permitem esse
     luxo, e essa é a diferença mais bonita entre testar hardware e testar
     software: com 8 bits de entrada, "todos os casos" são 256 casos.

  2. DE CUSTO    — o circuito gasta exatamente o número de portas prometido no
     docstring? Se alguém "melhorar" o código e a conta mudar, o teste acusa.
     Documentação que se verifica sozinha é a única que não apodrece.

  3. DE FALHA    — o circuito reage certo a entrada inválida e a condição
     patológica (o estado proibido do latch SR).
"""

from nand import nand, zerar_contador, Medidor, ErroDeSinal, custo
from portas import NOT, AND, OR, NOR, XOR, XNOR, BUFFER, AND_n, OR_n, XOR_n
from combinacional import (
    meio_somador, somador_completo, somador4, subtrator4, complemento_dois,
    mux2, mux2_bus, mux4, mux8, decodificador2x4, decodificador4x16,
    igual4, eh_zero, maior_ou_igual4, ula4, desloca_esquerda, desloca_direita,
    int_para_bits, bits_para_int, bits_para_texto,
    ULA_SOMA, ULA_SUB, ULA_AND, ULA_OR, ULA_XOR, ULA_NOT_A, ULA_PASSA_A, ULA_PASSA_B,
)
from sequencial import (
    LatchSR, latch_d, FlipFlopD, Registrador4, Contador4, BancoDeRegistradores,
)
from computador import (
    Computador, PROGRAMA_MULTIPLICA, LDI, ADD, SUB, OUT, HLT, JMP, JZ, STA, LDA,
    XOR_, AND_, OR_,
)

# ---------------------------------------------------------------------------
# Micro-framework de teste
# ---------------------------------------------------------------------------
_TESTES = []
_FALHAS = []


def teste(descricao):
    def decorador(fn):
        _TESTES.append((descricao, fn))
        return fn
    return decorador


def igual(obtido, esperado, contexto=""):
    if obtido != esperado:
        raise AssertionError(
            f"esperado {esperado!r}, obtido {obtido!r}"
            + (f"  [{contexto}]" if contexto else "")
        )


def medir(fn, *args):
    zerar_contador()
    with Medidor() as m:
        fn(*args)
    return m.total


BITS = (0, 1)
NUMEROS = range(16)


# ===========================================================================
# 1. A porta primitiva e as sete clássicas
# ===========================================================================

@teste("nand: tabela-verdade completa")
def _():
    igual([nand(a, b) for a in BITS for b in BITS], [1, 1, 1, 0])


@teste("nand: recusa sinal que não seja 0 ou 1")
def _():
    for invalido in (2, -1, "1", None, 0.5):
        try:
            nand(invalido, 1)
        except ErroDeSinal:
            continue
        raise AssertionError(f"aceitou sinal inválido {invalido!r}")


@teste("NOT: tabela-verdade")
def _():
    igual([NOT(a) for a in BITS], [1, 0])


@teste("AND: tabela-verdade")
def _():
    igual([AND(a, b) for a in BITS for b in BITS], [0, 0, 0, 1])


@teste("OR: tabela-verdade")
def _():
    igual([OR(a, b) for a in BITS for b in BITS], [0, 1, 1, 1])


@teste("NOR: tabela-verdade")
def _():
    igual([NOR(a, b) for a in BITS for b in BITS], [1, 0, 0, 0])


@teste("XOR: tabela-verdade (1 quando diferentes)")
def _():
    igual([XOR(a, b) for a in BITS for b in BITS], [0, 1, 1, 0])


@teste("XNOR: tabela-verdade (1 quando iguais)")
def _():
    igual([XNOR(a, b) for a in BITS for b in BITS], [1, 0, 0, 1])


@teste("BUFFER: não altera o valor lógico")
def _():
    igual([BUFFER(a) for a in BITS], [0, 1])


@teste("custo das sete portas bate com o documentado")
def _():
    igual(medir(NOT, 1), 1, "NOT")
    igual(medir(AND, 1, 1), 2, "AND")
    igual(medir(OR, 1, 1), 3, "OR")
    igual(medir(NOR, 1, 1), 4, "NOR")
    igual(medir(XOR, 1, 1), 4, "XOR")
    igual(medir(XNOR, 1, 1), 5, "XNOR")
    igual(medir(BUFFER, 1), 2, "BUFFER")


@teste("De Morgan verificado sobre todas as entradas")
def _():
    for a in BITS:
        for b in BITS:
            igual(NOT(AND(a, b)), OR(NOT(a), NOT(b)), f"¬(a·b) = ¬a+¬b  a={a} b={b}")
            igual(NOT(OR(a, b)), AND(NOT(a), NOT(b)), f"¬(a+b) = ¬a·¬b  a={a} b={b}")


@teste("AND_n de 4 entradas: só 1 quando todas são 1")
def _():
    for n in NUMEROS:
        bits = int_para_bits(n)
        igual(AND_n(*bits), 1 if n == 15 else 0, f"n={n}")


@teste("OR_n de 4 entradas: 0 só quando todas são 0")
def _():
    for n in NUMEROS:
        igual(OR_n(*int_para_bits(n)), 0 if n == 0 else 1, f"n={n}")


@teste("XOR_n de 4 entradas é o bit de paridade")
def _():
    for n in NUMEROS:
        bits = int_para_bits(n)
        igual(XOR_n(*bits), sum(bits) % 2, f"n={n}")


@teste("custo em árvore: AND_n(4) = 2·(N-1) = 6 NANDs")
def _():
    igual(medir(AND_n, 1, 1, 1, 1), 6)
    igual(medir(OR_n, 1, 1, 1, 1), 9)


# ===========================================================================
# 2. Aritmética
# ===========================================================================

@teste("meio somador: tabela-verdade completa")
def _():
    esperado = {(0, 0): (0, 0), (0, 1): (1, 0), (1, 0): (1, 0), (1, 1): (0, 1)}
    for (a, b), alvo in esperado.items():
        igual(meio_somador(a, b), alvo, f"a={a} b={b}")


@teste("meio somador custa 6 NANDs")
def _():
    igual(medir(meio_somador, 1, 1), 6)


@teste("somador completo: 8 casos, soma e vai-um corretos")
def _():
    for a in BITS:
        for b in BITS:
            for c in BITS:
                soma, vai = somador_completo(a, b, c)
                total = a + b + c
                igual(soma, total % 2, f"soma a={a} b={b} c={c}")
                igual(vai, total // 2, f"vai-um a={a} b={b} c={c}")


@teste("somador completo custa 9 NANDs (mais barato que 2 meio-somadores)")
def _():
    igual(medir(somador_completo, 1, 1, 1), 9)
    assert 9 < 2 * 6 + 3, "o arranjo direto deveria ser mais barato"


@teste("somador de 4 bits: EXAUSTIVO, todos os 256 pares")
def _():
    for x in NUMEROS:
        for y in NUMEROS:
            soma, vai = somador4(int_para_bits(x), int_para_bits(y))
            igual(bits_para_int(soma) + 16 * vai, x + y, f"{x}+{y}")


@teste("somador de 4 bits custa 36 NANDs")
def _():
    igual(medir(somador4, int_para_bits(7), int_para_bits(9)), 36)


@teste("somador de 4 bits: vai-um marca o transbordo (overflow)")
def _():
    _, vai = somador4(int_para_bits(15), int_para_bits(1))
    igual(vai, 1, "15+1 transborda")
    _, vai = somador4(int_para_bits(7), int_para_bits(8))
    igual(vai, 0, "7+8=15 não transborda")


@teste("complemento de dois: -x + x = 0 para todo x")
def _():
    for x in NUMEROS:
        neg = complemento_dois(int_para_bits(x))
        soma, _ = somador4(int_para_bits(x), neg)
        igual(bits_para_int(soma), 0, f"x={x}")


@teste("subtrator de 4 bits: EXAUSTIVO, todos os 256 pares")
def _():
    for x in NUMEROS:
        for y in NUMEROS:
            resultado, sem_emprestimo = subtrator4(int_para_bits(x), int_para_bits(y))
            igual(bits_para_int(resultado), (x - y) % 16, f"{x}-{y}")
            igual(sem_emprestimo, 1 if x >= y else 0, f"empréstimo em {x}-{y}")


# ===========================================================================
# 3. Seleção e endereçamento
# ===========================================================================

@teste("mux 2→1: escolhe a entrada certa em todos os casos")
def _():
    for a in BITS:
        for b in BITS:
            igual(mux2(a, b, 0), a, f"s=0 a={a} b={b}")
            igual(mux2(a, b, 1), b, f"s=1 a={a} b={b}")


@teste("mux 2→1 custa 4 NANDs")
def _():
    igual(medir(mux2, 1, 0, 1), 4)


@teste("mux de 4 bits (barramento) escolhe o número inteiro")
def _():
    a, b = int_para_bits(10), int_para_bits(5)
    igual(bits_para_int(mux2_bus(a, b, 0)), 10)
    igual(bits_para_int(mux2_bus(a, b, 1)), 5)


@teste("mux 4→1: as quatro seleções")
def _():
    entradas = [1, 0, 0, 1]
    for i, (s1, s0) in enumerate([(0, 0), (0, 1), (1, 0), (1, 1)]):
        igual(mux4(entradas, s0, s1), entradas[i], f"seleção {i}")


@teste("mux 8→1: as oito seleções")
def _():
    entradas = [1, 0, 1, 1, 0, 0, 1, 0]
    for i in range(8):
        s0, s1, s2 = i & 1, (i >> 1) & 1, (i >> 2) & 1
        igual(mux8(entradas, s0, s1, s2), entradas[i], f"seleção {i}")


@teste("decodificador 2→4: exatamente uma linha ativa (one-hot)")
def _():
    for n in range(4):
        a0, a1 = n & 1, (n >> 1) & 1
        linhas = decodificador2x4(a0, a1)
        igual(sum(linhas), 1, f"n={n}: mais de uma linha ativa")
        igual(linhas[n], 1, f"n={n}: linha errada")


@teste("decodificador 4→16: uma linha ativa entre 16, para os 16 endereços")
def _():
    for n in NUMEROS:
        linhas = decodificador4x16(int_para_bits(n))
        igual(sum(linhas), 1, f"n={n}")
        igual(linhas[n], 1, f"n={n}")


@teste("decodificador 4→16 custa 100 NANDs")
def _():
    igual(medir(decodificador4x16, int_para_bits(9)), 100)


# ===========================================================================
# 4. Comparação
# ===========================================================================

@teste("igualdade de 4 bits: EXAUSTIVO")
def _():
    for x in NUMEROS:
        for y in NUMEROS:
            igual(igual4(int_para_bits(x), int_para_bits(y)),
                  1 if x == y else 0, f"{x} == {y}")


@teste("detector de zero: só o zero acende")
def _():
    for n in NUMEROS:
        igual(eh_zero(int_para_bits(n)), 1 if n == 0 else 0, f"n={n}")


@teste("maior ou igual: EXAUSTIVO")
def _():
    for x in NUMEROS:
        for y in NUMEROS:
            igual(maior_ou_igual4(int_para_bits(x), int_para_bits(y)),
                  1 if x >= y else 0, f"{x} >= {y}")


# ===========================================================================
# 5. Deslocamento
# ===========================================================================

@teste("deslocar à esquerda multiplica por 2 (mod 16)")
def _():
    for n in NUMEROS:
        igual(bits_para_int(desloca_esquerda(int_para_bits(n))), (n * 2) % 16, f"n={n}")


@teste("deslocar à direita divide por 2 (inteiro)")
def _():
    for n in NUMEROS:
        igual(bits_para_int(desloca_direita(int_para_bits(n))), n // 2, f"n={n}")


@teste("deslocar não gasta porta nenhuma — é refiação")
def _():
    igual(medir(desloca_esquerda, int_para_bits(5)), 0)
    igual(medir(desloca_direita, int_para_bits(5)), 0)


# ===========================================================================
# 6. A ULA
# ===========================================================================

@teste("ULA · SOMA: EXAUSTIVO nos 256 pares")
def _():
    for x in NUMEROS:
        for y in NUMEROS:
            r, _, _ = ula4(int_para_bits(x), int_para_bits(y), ULA_SOMA)
            igual(bits_para_int(r), (x + y) % 16, f"{x}+{y}")


@teste("ULA · SUB: EXAUSTIVO nos 256 pares")
def _():
    for x in NUMEROS:
        for y in NUMEROS:
            r, _, _ = ula4(int_para_bits(x), int_para_bits(y), ULA_SUB)
            igual(bits_para_int(r), (x - y) % 16, f"{x}-{y}")


@teste("ULA · AND bit a bit")
def _():
    for x in NUMEROS:
        for y in NUMEROS:
            r, _, _ = ula4(int_para_bits(x), int_para_bits(y), ULA_AND)
            igual(bits_para_int(r), x & y, f"{x}&{y}")


@teste("ULA · OR bit a bit")
def _():
    for x in NUMEROS:
        for y in NUMEROS:
            r, _, _ = ula4(int_para_bits(x), int_para_bits(y), ULA_OR)
            igual(bits_para_int(r), x | y, f"{x}|{y}")


@teste("ULA · XOR bit a bit")
def _():
    for x in NUMEROS:
        for y in NUMEROS:
            r, _, _ = ula4(int_para_bits(x), int_para_bits(y), ULA_XOR)
            igual(bits_para_int(r), x ^ y, f"{x}^{y}")


@teste("ULA · NOT A")
def _():
    for x in NUMEROS:
        r, _, _ = ula4(int_para_bits(x), int_para_bits(0), ULA_NOT_A)
        igual(bits_para_int(r), 15 - x, f"~{x}")


@teste("ULA · passa A e passa B")
def _():
    for x in NUMEROS:
        y = (x * 7) % 16
        ra, _, _ = ula4(int_para_bits(x), int_para_bits(y), ULA_PASSA_A)
        rb, _, _ = ula4(int_para_bits(x), int_para_bits(y), ULA_PASSA_B)
        igual(bits_para_int(ra), x)
        igual(bits_para_int(rb), y)


@teste("ULA: a flag Z acende exatamente quando o resultado é zero")
def _():
    for x in NUMEROS:
        for y in NUMEROS:
            r, _, z = ula4(int_para_bits(x), int_para_bits(y), ULA_SUB)
            igual(z, 1 if bits_para_int(r) == 0 else 0, f"{x}-{y}")


@teste("ULA: vai-um da soma marca transbordo")
def _():
    _, vai, _ = ula4(int_para_bits(9), int_para_bits(9), ULA_SOMA)
    igual(vai, 1, "9+9 = 18 transborda em 4 bits")


@teste("ULA custa 242 NANDs (documentado no docstring)")
def _():
    igual(medir(ula4, int_para_bits(11), int_para_bits(6), ULA_SOMA), 242)


# ===========================================================================
# 7. Memória
# ===========================================================================

@teste("latch SR: grava 1")
def _():
    l = LatchSR()
    igual(l.passo(0, 1), 1)
    igual(l.instavel, False)


@teste("latch SR: grava 0")
def _():
    l = LatchSR()
    l.passo(0, 1)
    igual(l.passo(1, 0), 0)


@teste("latch SR: MANTÉM o valor quando as duas entradas repousam")
def _():
    l = LatchSR()
    l.passo(0, 1)              # grava 1
    for _ in range(5):
        igual(l.passo(1, 1), 1, "deveria continuar lembrando")


@teste("latch SR: o estado proibido (0,0) leva à instabilidade detectada")
def _():
    l = LatchSR()
    l.passo(0, 0)              # estado proibido: q e q_bar sobem juntos
    l.passo(1, 1)              # soltar as duas ao mesmo tempo: oscila
    igual(l.instavel, True, "o simulador deveria detectar a não convergência")


@teste("latch D: transparente quando habilitado")
def _():
    l = LatchSR()
    for d in (1, 0, 1, 1, 0):
        igual(latch_d(d, 1, l), d, f"d={d}")


@teste("latch D: congela quando desabilitado")
def _():
    l = LatchSR()
    latch_d(1, 1, l)
    for d in (0, 1, 0):
        igual(latch_d(d, 0, l), 1, "deveria manter o 1 congelado")


@teste("flip-flop D: captura na SUBIDA do relógio")
def _():
    ff = FlipFlopD()
    ff.passo(1, 0)             # clk baixo: mestre olha o dado
    igual(ff.passo(1, 1), 1)   # clk sobe: escravo publica
    ff.passo(0, 0)
    igual(ff.passo(0, 1), 0)


@teste("flip-flop D: ignora mudanças com o relógio parado em alto")
def _():
    ff = FlipFlopD()
    ff.passo(1, 0)
    ff.passo(1, 1)
    for d in (0, 1, 0):
        igual(ff.passo(d, 1), 1, "com clk alto, o mestre está fechado")


@teste("registrador de 4 bits: carrega quando load=1")
def _():
    reg = Registrador4()
    for n in (13, 0, 7, 15):
        igual(bits_para_int(reg.ciclo(int_para_bits(n), 1)), n, f"n={n}")


@teste("registrador de 4 bits: preserva quando load=0")
def _():
    reg = Registrador4()
    reg.ciclo(int_para_bits(9), 1)
    for n in (0, 15, 3):
        igual(bits_para_int(reg.ciclo(int_para_bits(n), 0)), 9, "não deveria mudar")


@teste("contador de 4 bits: conta 0..15 e dá a volta")
def _():
    c = Contador4()
    for esperado in list(range(1, 16)) + [0]:
        igual(bits_para_int(c.incrementar()), esperado, f"esperava {esperado}")


@teste("contador de 4 bits: carga forçada é o salto (JMP)")
def _():
    c = Contador4()
    c.incrementar()
    c.incrementar()
    igual(bits_para_int(c.carregar(int_para_bits(12))), 12)
    igual(bits_para_int(c.incrementar()), 13)


@teste("banco de registradores: escreve e lê as 4 palavras")
def _():
    ram = BancoDeRegistradores()
    valores = [3, 9, 15, 0]
    for endereco, valor in enumerate(valores):
        ram.escrever([endereco & 1, (endereco >> 1) & 1], int_para_bits(valor))
    for endereco, valor in enumerate(valores):
        lido = ram.ler([endereco & 1, (endereco >> 1) & 1])
        igual(bits_para_int(lido), valor, f"palavra {endereco}")


@teste("banco de registradores: escrever numa palavra não afeta as outras")
def _():
    ram = BancoDeRegistradores()
    ram.escrever([0, 0], int_para_bits(7))
    ram.escrever([1, 0], int_para_bits(2))
    igual(bits_para_int(ram.ler([0, 0])), 7, "palavra 0 foi corrompida")
    igual(bits_para_int(ram.ler([1, 0])), 2)


# ===========================================================================
# 8. O computador inteiro
# ===========================================================================

@teste("computador: multiplica 3 × 5 e imprime 15")
def _():
    pc = Computador(PROGRAMA_MULTIPLICA)
    igual(pc.rodar(), [15])


@teste("computador: o programa de multiplicação leva 46 instruções")
def _():
    pc = Computador(PROGRAMA_MULTIPLICA)
    pc.rodar()
    igual(pc.ciclos, 46)


@teste("computador: LDI, ADD e OUT no caminho mais curto")
def _():
    pc = Computador([(LDI, 4), (ADD, 5), (OUT, 0), (HLT, 0)])
    igual(pc.rodar(), [9])


@teste("computador: SUB e a aritmética circular de 4 bits")
def _():
    pc = Computador([(LDI, 2), (SUB, 5), (OUT, 0), (HLT, 0)])
    igual(pc.rodar(), [13], "2-5 = -3, que em 4 bits é 13")


@teste("computador: operações lógicas AND, OR e XOR")
def _():
    pc = Computador([
        (LDI, 12), (AND_, 10), (OUT, 0),     # 1100 & 1010 = 1000 = 8
        (LDI, 12), (OR_, 10), (OUT, 0),      # 1100 | 1010 = 1110 = 14
        (LDI, 12), (XOR_, 10), (OUT, 0),     # 1100 ^ 1010 = 0110 = 6
        (HLT, 0),
    ])
    igual(pc.rodar(), [8, 14, 6])


@teste("computador: JZ não salta quando a flag Z está apagada")
def _():
    pc = Computador([(LDI, 1), (SUB, 0), (JZ, 5), (OUT, 0), (HLT, 0), (LDI, 0), (OUT, 0), (HLT, 0)])
    igual(pc.rodar(), [1], "1-0=1, Z=0, não deveria saltar")


@teste("computador: JZ salta quando a flag Z está acesa")
def _():
    pc = Computador([(LDI, 3), (SUB, 3), (JZ, 5), (OUT, 0), (HLT, 0), (LDI, 9), (OUT, 0), (HLT, 0)])
    igual(pc.rodar(), [9], "3-3=0, Z=1, deveria saltar para 5")


@teste("computador: STA e LDA guardam e recuperam pela RAM")
def _():
    pc = Computador([
        (LDI, 6), (STA, 2), (LDI, 0), (LDA, 2), (OUT, 0), (HLT, 0),
    ])
    igual(pc.rodar(), [6])


@teste("computador: JMP fecha um laço, e o laço termina")
def _():
    pc = Computador([
        (LDI, 3),            # 0
        (SUB, 1),            # 1
        (JZ, 4),             # 2
        (JMP, 1),            # 3
        (OUT, 0),            # 4
        (HLT, 0),            # 5
    ])
    igual(pc.rodar(), [0])


@teste("computador: programa sem HLT explícito para no fim da ROM")
def _():
    pc = Computador([(LDI, 5), (OUT, 0)])
    igual(pc.rodar(), [5], "as posições não usadas da ROM são HLT")


@teste("computador: laço infinito é detectado pelo limite de segurança")
def _():
    pc = Computador([(JMP, 0)])
    try:
        pc.rodar(limite=50)
    except RuntimeError:
        return
    raise AssertionError("deveria ter levantado RuntimeError")


@teste("computador: o custo total de execução é medido, não estimado")
def _():
    pc = Computador(PROGRAMA_MULTIPLICA)
    pc.rodar()
    assert pc.nands_gastos > 30000, f"gastou só {pc.nands_gastos} NANDs?"
    assert pc.nands_gastos < 50000, f"gastou {pc.nands_gastos} NANDs — regrediu?"


@teste("conversões de bits são consistentes nos dois sentidos")
def _():
    for n in NUMEROS:
        igual(bits_para_int(int_para_bits(n)), n, f"n={n}")
    igual(bits_para_texto(int_para_bits(11)), "1011")
    igual(int_para_bits(13), [1, 0, 1, 1])


@teste("int_para_bits recusa número que não cabe na largura")
def _():
    for invalido in (16, -1, 100):
        try:
            int_para_bits(invalido)
        except ValueError:
            continue
        raise AssertionError(f"aceitou {invalido}")


# ===========================================================================
# Execução
# ===========================================================================

def main():
    print("=" * 70)
    print("  SUÍTE DE TESTES — computador de 4 bits feito de NANDs")
    print("=" * 70)
    print()
    largura = max(len(d) for d, _ in _TESTES)
    for descricao, fn in _TESTES:
        try:
            zerar_contador()
            fn()
            print(f"  ok   {descricao}")
        except AssertionError as erro:
            _FALHAS.append((descricao, str(erro)))
            print(f"  FALHA {descricao}")
            print(f"         └─ {erro}")
        except Exception as erro:                     # noqa: BLE001
            _FALHAS.append((descricao, f"{type(erro).__name__}: {erro}"))
            print(f"  ERRO  {descricao}")
            print(f"         └─ {type(erro).__name__}: {erro}")

    print()
    print("=" * 70)
    total = len(_TESTES)
    aprovados = total - len(_FALHAS)
    print(f"  {total} testes, {aprovados} aprovados, {len(_FALHAS)} falhas")
    print("=" * 70)
    return 0 if not _FALHAS else 1


if __name__ == "__main__":
    raise SystemExit(main())
