"""
contagem.py — O censo de portas.

Este arquivo existe para responder, com número MEDIDO, a pergunta que originou
todo este curso: quantas portas lógicas há num computador, e onde elas estão?

Ele mede o custo em portas NAND de cada bloco do computador de 4 bits deste
projeto e, ao final, faz a ponte para as ordens de grandeza de um chip real.

Rode com:  python3 contagem.py
"""

from nand import zerar_contador, custo, Medidor
from portas import NOT, AND, OR, NOR, XOR, XNOR, BUFFER
from combinacional import (
    meio_somador, somador_completo, somador4, subtrator4, mux2, mux2_bus,
    mux4, mux8, decodificador2x4, decodificador4x16, igual4, eh_zero, ula4,
    int_para_bits, ULA_SOMA,
)
from sequencial import LatchSR, latch_d, FlipFlopD, Registrador4, Contador4
from computador import Computador, PROGRAMA_MULTIPLICA

A = int_para_bits(11)
B = int_para_bits(6)
DOIS_BITS = [1, 0]


def medir(nome, funcao, *args):
    zerar_contador()
    with Medidor() as m:
        funcao(*args)
    return nome, m.total


def linha(nome, valor, nota=""):
    print(f"  {nome:.<44} {valor:>8}  {nota}")


def cabecalho(texto):
    print()
    print(f"  {texto}")
    print("  " + "─" * 64)


def main():
    print("=" * 70)
    print("  CENSO DE PORTAS — quanto custa cada peça, em portas NAND")
    print("=" * 70)

    cabecalho("1. AS SETE PORTAS CLÁSSICAS (a partir de NAND)")
    for nome, fn, args in [
        ("NOT", NOT, (1,)),
        ("AND", AND, (1, 1)),
        ("OR", OR, (1, 0)),
        ("NOR", NOR, (1, 0)),
        ("XOR", XOR, (1, 0)),
        ("XNOR", XNOR, (1, 0)),
        ("BUFFER", BUFFER, (1,)),
    ]:
        _, n = medir(nome, fn, *args)
        linha(nome, n, "NANDs")

    cabecalho("2. ARITMÉTICA")
    for nome, fn, args, nota in [
        ("meio somador (1 bit)", meio_somador, (1, 1), ""),
        ("somador completo (1 bit)", somador_completo, (1, 1, 1), "a peça central"),
        ("somador de 4 bits", somador4, (A, B), "4 × 9"),
        ("subtrator de 4 bits", subtrator4, (A, B), "reusa o somador"),
    ]:
        _, n = medir(nome, fn, *args)
        linha(nome, n, nota)

    cabecalho("3. SELEÇÃO E ENDEREÇAMENTO")
    for nome, fn, args, nota in [
        ("mux 2→1 (1 bit)", mux2, (1, 0, 1), "a peça mais repetida de uma CPU"),
        ("mux 2→1 (4 bits)", mux2_bus, (A, B, 1), ""),
        ("mux 4→1", mux4, ([1, 0, 1, 0], 1, 0), ""),
        ("mux 8→1", mux8, ([1, 0, 1, 0, 1, 1, 0, 0], 1, 0, 1), ""),
        ("decodificador 2→4", decodificador2x4, (1, 0), ""),
        ("decodificador 4→16", decodificador4x16, (A,), "cresce exponencialmente"),
    ]:
        _, n = medir(nome, fn, *args)
        linha(nome, n, nota)

    cabecalho("4. COMPARAÇÃO")
    for nome, fn, args, nota in [
        ("igualdade de 4 bits", igual4, (A, B), ""),
        ("detector de zero (flag Z)", eh_zero, (A,), "faz o 'if' funcionar"),
    ]:
        _, n = medir(nome, fn, *args)
        linha(nome, n, nota)

    cabecalho("5. A ULA COMPLETA (8 operações)")
    _, n_ula = medir("ula", ula4, A, B, ULA_SOMA)
    linha("ULA de 4 bits", n_ula, "calcula as 8 e joga 7 fora")
    linha("  → por bit de largura", n_ula // 4, "escala ~linear")

    cabecalho("6. MEMÓRIA (onde a conta desanda)")
    zerar_contador()
    latch = LatchSR()
    with Medidor() as m:
        latch.passo(0, 1)
    linha("latch SR — avaliações até assentar", m.total, "físico: 2 portas")

    zerar_contador()
    l2 = LatchSR()
    with Medidor() as m:
        latch_d(1, 1, l2)
    linha("latch D — avaliações", m.total, "físico: 4 portas")

    zerar_contador()
    ff = FlipFlopD()
    with Medidor() as m:
        ff.passo(1, 0)
        ff.passo(1, 1)
    linha("flip-flop D — avaliações por ciclo", m.total, "físico: 9 portas")

    zerar_contador()
    reg = Registrador4()
    with Medidor() as m:
        reg.ciclo(A, 1)
    linha("registrador de 4 bits — avaliações", m.total, "físico: 52 portas")

    zerar_contador()
    cont = Contador4()
    with Medidor() as m:
        cont.incrementar()
    linha("contador de 4 bits — avaliações", m.total, "físico: 88 portas")

    print()
    print("  ⚠  Em circuito COMBINACIONAL, avaliações = portas físicas.")
    print("     Em circuito SEQUENCIAL, não: a realimentação obriga o simulador")
    print("     a reavaliar as mesmas portas até o circuito assentar. O silício")
    print("     faz isso de graça, em picossegundos. Ver ../30-circuitos-sequenciais.md")

    cabecalho("7. O COMPUTADOR INTEIRO")
    pc = Computador(PROGRAMA_MULTIPLICA)
    saida = pc.rodar()
    linha("resultado do programa (3 × 5)", str(saida), "")
    linha("instruções executadas", pc.ciclos, "")
    linha("avaliações de NAND no total", f"{pc.nands_gastos:,}".replace(",", "."), "")
    linha("média por instrução", f"{pc.nands_gastos // pc.ciclos:,}".replace(",", "."), "")

    # Estimativa estrutural (portas físicas, contadas uma vez cada)
    estrutura = {
        "ULA de 4 bits": n_ula,
        "registrador A (4 bits)": 52,
        "contador de programa (4 bits)": 88,
        "flag Z (1 flip-flop)": 9,
        "decodificador de instrução 4→16": 100,
        "lógica de controle (estimada)": 40,
        "multiplexadores de escrita": 32,
        "RAM 4×4 de flip-flops": 266,
    }
    print()
    print("  INVENTÁRIO ESTRUTURAL (portas físicas, cada uma contada uma vez):")
    print()
    for nome, valor in estrutura.items():
        linha(nome, valor)
    total = sum(estrutura.values())
    print("  " + "─" * 64)
    linha("TOTAL do computador de 4 bits", total, "portas NAND")

    cabecalho("8. A PONTE PARA UM COMPUTADOR DE VERDADE")
    print(f"""
  Este computador: {total} portas, 4 bits, 13 instruções, 16 bytes de programa.

  Compare com a régua histórica (transistores conforme a Wikipédia,
  'Transistor count', consultada em 14/08/2026; portas são estimativa):

    Intel 4004    (1971)  2.250 transistores   ~500-800 portas ← mesma ordem
    Intel 8086    (1978)     29.000 transistores ~10.000 portas   que este projeto
    Pentium       (1993)  3.100.000 transistores ~1 milhão de portas
    Apple M4      (2024)   28 bilhões            ~2,5 a 5 bilhões de portas
    Nvidia Rubin  (2026)  336 bilhões            dezenas de bilhões

  Repare: as {total} portas deste projeto estão na MESMA ORDEM DE GRANDEZA do
  primeiro microprocessador comercial da história. Não é coincidência — é o
  tamanho natural de uma máquina de 4 bits com acumulador. O 4004 era mais
  capaz (45 instruções, 12 bits de endereço, BCD), mas o esqueleto é este.
  Um Apple M4 tem, por estimativa, cerca de quatro milhões de vezes mais portas.

  Por que "estimativa" e não número exato: a maior parte dos transistores de um
  chip moderno é CACHE (células SRAM de 6 transistores), que NÃO são portas
  lógicas. A conta completa está em ../50-quantas-portas-tem-um-computador.md.

  A lição do item 6 acima, em uma frase: guardar 16 bits com flip-flops custou
  266 portas — cerca de 66 portas por bit. É por isso que memória grande NUNCA
  é feita de flip-flops, e por isso que a pergunta "quantas portas tem um
  computador" não se responde dividindo transistores por quatro.
""")


if __name__ == "__main__":
    main()
