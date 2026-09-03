"""
sequencial.py — Circuitos COM memória: a saída depende também do passado.

O pulo do gato deste arquivo cabe em uma frase: LIGUE A SAÍDA DE VOLTA NA
ENTRADA. Toda a memória de todos os computadores do mundo sai daí.

Um circuito combinacional é uma função matemática: mesmas entradas, mesma saída,
sempre. Um circuito sequencial é uma máquina: a mesma entrada pode produzir
saídas diferentes, porque ele tem estado.

Sobre a simulação
-----------------
Realimentação num simulador digital exige um laço: avalia-se o circuito
repetidamente até ele parar de mudar ("assentar"). Em silício isso acontece
sozinho, em picossegundos, porque a eletricidade não espera ninguém. Aqui é
explícito — e o laço revela dois fenômenos reais que nenhum livro consegue
mostrar tão bem:

  1. o custo em avaliações é MAIOR que o número de portas físicas;
  2. existem entradas para as quais o circuito NUNCA assenta. Isso se chama
     METAESTABILIDADE, é um problema de verdade em hardware real, e mata
     sistemas em produção. Ver ../30-circuitos-sequenciais.md.
"""

from nand import nand
from portas import NOT, AND, OR
from combinacional import mux2, decodificador2x4, somador4, int_para_bits, LARGURA


class LatchSR:
    """Trava SR de portas NAND (entradas ATIVAS EM NÍVEL BAIXO).
    CUSTO FÍSICO: 2 NANDs. Custo em avaliações: 2 a 8, conforme assenta.

        s_bar r_bar | efeito
          1     1   | mantém o que estava (MEMÓRIA)
          0     1   | grava 1
          1     0   | grava 0
          0     0   | PROIBIDO: q e q_bar ficam ambos em 1, e ao sair
                    | desse estado o circuito pode oscilar para sempre

    Duas portas. É literalmente a menor memória possível em lógica estática.
    """

    def __init__(self):
        self.q = 0
        self.q_bar = 1
        self.instavel = False

    def passo(self, s_bar, r_bar, max_iteracoes=12):
        """Avalia o par cruzado até estabilizar. Devolve q."""
        self.instavel = True
        for _ in range(max_iteracoes):
            q_novo = nand(s_bar, self.q_bar)
            qb_novo = nand(r_bar, self.q)
            estavel = (q_novo == self.q and qb_novo == self.q_bar)
            self.q, self.q_bar = q_novo, qb_novo
            if estavel:
                self.instavel = False
                break
        return self.q


def latch_d(d, habilita, latch):
    """Trava D transparente ("gated D latch"). CUSTO FÍSICO: 4 NANDs.

    Enquanto `habilita` = 1, a saída acompanha `d` (é transparente, como um fio).
    Quando `habilita` volta a 0, ela congela o último valor.

    Resolve o defeito do SR: é impossível pedir o estado proibido, porque
    s_bar e r_bar são derivados do MESMO sinal d e nunca ficam ambos em 0.
    """
    a = nand(d, habilita)
    b = nand(a, habilita)
    return latch.passo(a, b)


class FlipFlopD:
    """Flip-flop D mestre-escravo, disparado na SUBIDA do relógio.
    CUSTO FÍSICO: 9 NANDs (4 + 4 + 1 inversor).

    Por que dois latches em vez de um? Porque um latch transparente é perigoso:
    enquanto está aberto, mudanças na entrada atravessam na hora e podem dar
    duas voltas no circuito num mesmo ciclo ("race"). O truque mestre-escravo
    garante que a captura acontece num INSTANTE (a borda do relógio), não
    durante um intervalo:

        clk = 0 : mestre aberto (olha d), escravo fechado (segura a saída)
        clk = 1 : mestre fechado (congela d), escravo aberto (mostra o congelado)

    Nenhum caminho fica aberto de ponta a ponta em momento algum. É por isso que
    quase todo hardware síncrono do mundo usa flip-flop, não latch.
    """

    def __init__(self):
        self.mestre = LatchSR()
        self.escravo = LatchSR()

    def passo(self, d, clk):
        n_clk = NOT(clk)
        q_mestre = latch_d(d, n_clk, self.mestre)
        return latch_d(q_mestre, clk, self.escravo)

    @property
    def q(self):
        return self.escravo.q


class Registrador4:
    """Registrador de 4 bits com carga controlada ("load enable").
    CUSTO FÍSICO: 4 flip-flops (36) + 4 muxes (16) = 52 NANDs.

    O mux na entrada é o que permite ao registrador GUARDAR: se load=0, ele
    realimenta o próprio valor; se load=1, aceita o novo. Sem esse mux, o
    registrador engoliria o barramento a cada ciclo de relógio.
    """

    def __init__(self, largura=LARGURA):
        self.bits = [FlipFlopD() for _ in range(largura)]
        self.largura = largura

    def ler(self):
        return [ff.q for ff in self.bits]

    def ciclo(self, entrada, carrega=1):
        """Um ciclo completo de relógio: borda de descida, depois de subida."""
        atual = self.ler()
        alvo = [mux2(atual[i], entrada[i], carrega) for i in range(self.largura)]
        for i, ff in enumerate(self.bits):
            ff.passo(alvo[i], 0)     # clk baixo: mestre captura
        for i, ff in enumerate(self.bits):
            ff.passo(alvo[i], 1)     # clk sobe:  escravo publica
        return self.ler()


class Contador4:
    """Contador crescente de 4 bits (0→15→0). CUSTO: registrador (52) + somador4 (36) = 88.

    É o Program Counter de qualquer processador: um registrador que soma 1 em si
    mesmo a cada ciclo. Note que ele "dá a volta" no 15 e não avisa — overflow
    silencioso é o comportamento padrão de hardware, e a origem de uma classe
    inteira de bugs de software.
    """

    def __init__(self):
        self.reg = Registrador4()
        self._um = int_para_bits(1)

    def ler(self):
        return self.reg.ler()

    def incrementar(self):
        proximo, _ = somador4(self.reg.ler(), self._um)
        return self.reg.ciclo(proximo, carrega=1)

    def carregar(self, valor):
        """Salto: força um valor. É o que uma instrução JMP faz."""
        return self.reg.ciclo(valor, carrega=1)


class BancoDeRegistradores:
    """Memória de 4 palavras × 4 bits, feita de portas de verdade.
    CUSTO FÍSICO: decodificador 2x4 (10) + 4 registradores (208) + mux de leitura (~48)
                  ≈ 266 NANDs para guardar 16 bits.

    Guarde este número: 266 portas para 16 bits de memória, ou ~66 portas por bit.
    É por isso que NINGUÉM constrói memória grande com flip-flops. Uma célula
    SRAM de verdade usa 6 transistores por bit (≈1,5 "portas equivalentes"),
    e a DRAM usa 1 transistor + 1 capacitor. A conta está em
    ../50-quantas-portas-tem-um-computador.md, e é a razão de a maior parte dos
    transistores de um chip moderno NÃO ser porta lógica.
    """

    def __init__(self):
        self.palavras = [Registrador4() for _ in range(4)]

    def ler(self, endereco):
        """endereco: lista de 2 bits [a0, a1]."""
        selecao = decodificador2x4(endereco[0], endereco[1])
        saida = []
        for bit in range(LARGURA):
            candidatos = [self.palavras[p].ler()[bit] for p in range(4)]
            # mux 4→1 usando a seleção "one-hot" do decodificador:
            valor = 0
            for p in range(4):
                valor = OR(valor, AND(candidatos[p], selecao[p]))
            saida.append(valor)
        return saida

    def escrever(self, endereco, dado):
        selecao = decodificador2x4(endereco[0], endereco[1])
        for p in range(4):
            self.palavras[p].ciclo(dado, carrega=selecao[p])
        return self.ler(endereco)
