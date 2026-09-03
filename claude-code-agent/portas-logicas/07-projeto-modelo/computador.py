"""
computador.py — Um computador de 4 bits inteiro, feito só de portas NAND.

Arquitetura: máquina de ACUMULADOR (a mesma do Intel 4004 de 1971 e de quase
todo computador anterior a 1980). Há um único registrador de trabalho, chamado
A, e toda operação usa A como um dos operandos e guarda o resultado em A.

    ┌──────────────────────────────────────────────────────────┐
    │                                                          │
    │   ┌────┐  endereço   ┌───────────┐  instrução            │
    │   │ PC ├────────────►│ ROM (16×8)├──────────┐            │
    │   └──▲─┘             └───────────┘          │            │
    │      │                                      ▼            │
    │      │                              ┌───────────────┐    │
    │      │  salto                       │ DECODIFICADOR │    │
    │      └──────────────────────────────┤    4 → 16     │    │
    │                                     └───────┬───────┘    │
    │                                    sinais de controle    │
    │   ┌────┐        ┌─────┐                     │            │
    │   │ A  ├───────►│     │                     ▼            │
    │   └──▲─┘        │ ULA ├──► resultado ──► [MUX] ──► A     │
    │      │  operando│     │                     ▲            │
    │      │  ───────►└──┬──┘                     │            │
    │      │             │ flag Z            RAM (4×4)         │
    │      └─────────────┴────────────────────────┘            │
    └──────────────────────────────────────────────────────────┘

O QUE É FEITO DE PORTAS DE VERDADE (contado pelo simulador):
    - registrador A, contador de programa, flag Z  → flip-flops de NANDs
    - ULA (8 operações)                            → NANDs
    - decodificador de instrução 4→16              → NANDs
    - lógica de controle (habilitações, saltos)    → NANDs
    - RAM de dados 4×4                             → flip-flops de NANDs

O QUE É MODELADO EM PYTHON (e por quê):
    - a ROM de programa. Uma ROM real é um decodificador de endereço mais uma
      matriz de conexões; simular isso porta a porta não ensinaria nada de novo
      e multiplicaria o tempo de execução. A estimativa de custo dela está no
      relatório de `contagem.py`.
    - o laço "enquanto não parou", que no hardware é o próprio relógio.

Isso é declarado aqui em vez de escondido porque o valor deste projeto é o
número honesto, não o número bonito.
"""

from nand import Medidor
from portas import NOT, AND, OR, OR_n
from combinacional import (
    ula4, mux2_bus, decodificador4x16, int_para_bits, bits_para_int,
    bits_para_texto, LARGURA,
)
from sequencial import Registrador4, Contador4, FlipFlopD, BancoDeRegistradores

# --- Conjunto de instruções (ISA) ------------------------------------------
NOP, LDI, ADD, SUB, AND_, OR_, XOR_, JMP, JZ, STA, LDA, OUT, HLT = range(13)

NOMES = {
    NOP: "NOP", LDI: "LDI", ADD: "ADD", SUB: "SUB", AND_: "AND", OR_: "OR",
    XOR_: "XOR", JMP: "JMP", JZ: "JZ", STA: "STA", LDA: "LDA", OUT: "OUT",
    HLT: "HLT",
}

# Mapa de opcode → código de operação da ULA (ver combinacional.ULA_*)
# ADD→000  SUB→001  AND→010  OR→011  XOR→100


class Computador:
    def __init__(self, programa, tracar=False):
        """programa: lista de tuplas (opcode, operando), até 16 posições."""
        self.rom = list(programa) + [(HLT, 0)] * (16 - len(programa))
        self.a = Registrador4()
        self.pc = Contador4()
        self.flag_z = FlipFlopD()
        self.ram = BancoDeRegistradores()
        self.saida = []
        self.tracar = tracar
        self.ciclos = 0
        self.nands_gastos = 0

    # -- um ciclo de instrução ---------------------------------------------
    def passo(self):
        """Executa UMA instrução. Devolve False quando encontra HLT."""
        with Medidor() as medidor:
            parou = self._executar()
        self.nands_gastos += medidor.total
        self.ciclos += 1
        return parou

    def _executar(self):
        # ---- BUSCA (fetch) -------------------------------------------------
        endereco = bits_para_int(self.pc.ler())
        opcode, operando = self.rom[endereco]
        oper_bits = int_para_bits(operando)

        # ---- DECODIFICAÇÃO: decodificador 4→16 feito de portas -------------
        linha = decodificador4x16(int_para_bits(opcode))
        # `linha[k]` vale 1 exatamente quando opcode == k. "One-hot".

        usa_ula = OR_n(linha[ADD], linha[SUB], linha[AND_], linha[OR_], linha[XOR_])
        # Código da ULA montado com portas a partir das linhas one-hot:
        ula_b0 = OR(linha[SUB], linha[OR_])     # SUB=001, OR=011
        ula_b1 = OR(linha[AND_], linha[OR_])    # AND=010, OR=011
        ula_b2 = linha[XOR_]                    # XOR=100
        ula_op = ula_b0 | (ula_b1 << 1) | (ula_b2 << 2)

        carrega_a = OR_n(linha[LDI], linha[LDA], usa_ula)
        escreve_ram = linha[STA]
        salta = OR(linha[JMP], AND(linha[JZ], self.flag_z.q))
        para = linha[HLT]

        # ---- EXECUÇÃO ------------------------------------------------------
        a_atual = self.a.ler()
        resultado, _vai, zero = ula4(a_atual, oper_bits, ula_op)

        endereco_ram = oper_bits[0:2]     # RAM tem 4 palavras: 2 bits de endereço
        dado_ram = self.ram.ler(endereco_ram)

        # Multiplexadores encadeados escolhem o que entra em A:
        #   ULA → (se LDI) operando imediato → (se LDA) dado da RAM
        valor = mux2_bus(resultado, oper_bits, linha[LDI])
        valor = mux2_bus(valor, dado_ram, linha[LDA])

        # ---- ESCRITA (write-back) -----------------------------------------
        self.a.ciclo(valor, carrega=carrega_a)
        self.flag_z.passo(zero, 0)
        self.flag_z.passo(zero, usa_ula)      # a flag só muda em operação da ULA
        if escreve_ram:
            self.ram.escrever(endereco_ram, a_atual)
        if linha[OUT]:
            self.saida.append(bits_para_int(a_atual))

        if self.tracar:
            print(f"  PC={endereco:2d}  {NOMES[opcode]:3s} {operando:2d}"
                  f"   A={bits_para_int(self.a.ler()):2d}"
                  f" ({bits_para_texto(self.a.ler())})  Z={self.flag_z.q}")

        # ---- PRÓXIMO ENDEREÇO ---------------------------------------------
        if para:
            return False
        if salta:
            self.pc.carregar(oper_bits)
        else:
            self.pc.incrementar()
        return True

    def rodar(self, limite=500):
        while self.passo():
            if self.ciclos >= limite:
                raise RuntimeError(f"programa não parou em {limite} instruções")
        return self.saida


# ---------------------------------------------------------------------------
# Programa de demonstração: 3 × 5 por somas sucessivas
# ---------------------------------------------------------------------------
# Não existe instrução de multiplicar — como no 4004, e como em qualquer
# processador simples. Multiplicação vira um laço de somas, e é por isso que
# multiplicar era caríssimo até os multiplicadores em hardware ficarem baratos.

PROGRAMA_MULTIPLICA = [
    (LDI, 5),    #  0  A = 5           (contador de repetições)
    (STA, 0),    #  1  RAM[0] = A
    (LDI, 0),    #  2  A = 0
    (STA, 1),    #  3  RAM[1] = 0      (acumulador do produto)
    (LDA, 1),    #  4  A = RAM[1]      <-- início do laço
    (ADD, 3),    #  5  A = A + 3
    (STA, 1),    #  6  RAM[1] = A
    (LDA, 0),    #  7  A = RAM[0]
    (SUB, 1),    #  8  A = A - 1       (e atualiza a flag Z)
    (STA, 0),    #  9  RAM[0] = A
    (JZ, 12),    # 10  se Z, vá para 12
    (JMP, 4),    # 11  senão, repita o laço
    (LDA, 1),    # 12  A = RAM[1]      (o produto)
    (OUT, 0),    # 13  imprime A
    (HLT, 0),    # 14  para
]


def main():
    print("=" * 68)
    print("  COMPUTADOR DE 4 BITS — feito exclusivamente de portas NAND")
    print("=" * 68)
    print("\nPrograma: multiplicar 3 × 5 por somas sucessivas\n")

    pc = Computador(PROGRAMA_MULTIPLICA, tracar=True)
    saida = pc.rodar()

    print("\n" + "-" * 68)
    print(f"  Saída do programa ......... {saida}   (esperado: [15])")
    print(f"  Instruções executadas ..... {pc.ciclos}")
    print(f"  Avaliações de NAND ........ {pc.nands_gastos:,}".replace(",", "."))
    print(f"  Média por instrução ....... {pc.nands_gastos // pc.ciclos:,}"
          .replace(",", "."))
    print("-" * 68)
    print("\nPara o inventário de portas do circuito, rode:  python3 contagem.py")


if __name__ == "__main__":
    main()
