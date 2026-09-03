# Projeto-modelo — Um computador de 4 bits feito só de portas NAND

**Nível:** intermediário · **Linguagem:** Python 3.9+ · **Dependências externas:** nenhuma
**Estado:** executado e verificado em 14/08/2026 (Python 3.10.12, Ubuntu 22.04.5 LTS) —
76 testes, 76 aprovados, em 0,3 s.

---

## O que é

Um computador inteiro — unidade lógica e aritmética, registradores, memória, contador de
programa, decodificador de instruções e um conjunto de 13 instruções — construído a partir
de **uma única função primitiva**: `nand(a, b)`.

Nenhum arquivo deste projeto usa `and`, `or`, `not`, `+` ou `-` para calcular um valor
lógico. Tudo sai de NAND. E cada chamada é **contada**, o que faz este projeto responder,
com número medido, à pergunta que originou o curso: *quantas portas lógicas são necessárias
para fazer isso?*

**Resposta medida: 829 portas NAND** para o computador de 4 bits completo — a mesma
ordem de grandeza do Intel 4004 de 1971 (2.250 transistores, estimados ~500 a 800 portas).

---

## Como rodar

```bash
cd portas-logicas/07-projeto-modelo
```

**1. Ver o computador executando um programa** (multiplica 3 × 5 por somas sucessivas):
```bash
python3 computador.py
```
Saída esperada: um traço de 46 instruções, terminando em
```
  Saída do programa ......... [15]   (esperado: [15])
  Instruções executadas ..... 46
  Avaliações de NAND ........ 39.678
```

**2. Ver o censo de portas** — quanto custa cada peça:
```bash
python3 contagem.py
```

**3. Rodar os testes:**
```bash
python3 testes.py
```
Saída esperada na última linha:
```
  76 testes, 76 aprovados, 0 falhas
```

Não há `pip install`, não há ambiente virtual, não há `requirements.txt` com conteúdo.
Isso é deliberado: um projeto de ensino não deve exigir que você instale nada para
verificar que ele funciona.

---

## Estrutura

```
07-projeto-modelo/
├── nand.py            A ÚNICA porta primitiva + o contador de portas.
│                      Comece por aqui: são 60 linhas e explicam o projeto todo.
├── portas.py          As sete portas clássicas, cada uma construída de NANDs.
│                      NOT=1, AND=2, OR=3, NOR=4, XOR=4, XNOR=5, BUFFER=2.
├── combinacional.py   Circuitos sem memória: somador, subtrator, multiplexador,
│                      decodificador, comparador, deslocador e a ULA de 8 operações.
├── sequencial.py      Circuitos com memória: latch SR, latch D, flip-flop D,
│                      registrador, contador e um banco de 4 palavras.
├── computador.py      O computador: busca, decodifica, executa. Roda um programa.
├── contagem.py        O censo de portas — o relatório que responde à pergunta.
├── testes.py          76 testes, vários EXAUSTIVOS (todas as entradas possíveis).
└── README.md          este arquivo
```

Ordem de leitura recomendada: `nand.py` → `portas.py` → `combinacional.py` →
`sequencial.py` → `computador.py`. Cada arquivo só usa o anterior.

---

## O que cada decisão de projeto ensina

### Decisão 1 — Uma única primitiva, e ela é NAND

**Por quê:** demonstra na prática a **completude funcional**. Se NAND basta para tudo,
então todo o computador é uma consequência dela. Também é o que fábricas reais fazem:
em CMOS, NAND custa 4 transistores e é a porta mais rápida da biblioteca padrão
(ver [`../12-do-transistor-a-porta.md`](../12-do-transistor-a-porta.md)).

**O que se aprende no caminho:** que OR custa 3 NANDs e AND custa 2. Essa assimetria
não é curiosidade — ela reaparece em cada decisão de projeto de hardware real.

### Decisão 2 — Contar cada porta, sempre

**Por quê:** porque a pergunta do curso é "quantas?". Números medidos derrotam estimativas.

**O que se aprende:** que em circuito **combinacional** as avaliações contadas são
exatamente as portas físicas, e em circuito **sequencial** não são — a realimentação
obriga o simulador a reavaliar até assentar. Um latch SR tem 2 portas físicas e gasta 6
avaliações. Essa diferença é a versão discreta de um fenômeno físico real, e leva direto
ao conceito de **atraso de propagação**.

### Decisão 3 — O somador completo direto em 9 NANDs, não em 2 meio-somadores

**Por quê:** juntar dois meio-somadores custaria 15 NANDs (6+6+3). O arranjo direto custa 9.

**O que se aprende:** que compor blocos prontos é claro mas caro, e otimizar é feio mas
barato. Esse é o dilema central da engenharia de hardware, e a razão de existirem
ferramentas de síntese — elas fazem essa otimização por você, e fazem melhor.

### Decisão 4 — A ULA calcula as 8 operações ao mesmo tempo e joga 7 fora

**Por quê:** é o que o hardware real faz. Calcular tudo em paralelo e escolher com um
multiplexador é mais rápido e mais simples que ligar e desligar blocos.

**O que se aprende:** que hardware **desperdiça trabalho de propósito** para ganhar tempo.
Essa é a diferença mental mais difícil para quem vem de software, onde não executar é
sempre mais barato. Em hardware, o circuito está lá, e o silício consome energia
independentemente de você usar o resultado. Foi só quando energia virou o gargalo (anos
2000) que apareceram *clock gating* e *power gating*.

### Decisão 5 — A memória é feita de flip-flops, e isso é caro de propósito

**Por quê:** para você **ver** o preço. Guardar 16 bits custou 266 portas — cerca de
66 portas por bit.

**O que se aprende:** por que memória grande nunca é feita assim. Uma célula SRAM real usa
6 transistores por bit (≈1,5 portas equivalentes) e uma célula DRAM usa 1 transistor +
1 capacitor. Esse número é a chave para entender por que a maioria dos transistores de um
chip moderno **não é porta lógica** — a conta completa está em
[`../50-quantas-portas-tem-um-computador.md`](../50-quantas-portas-tem-um-computador.md).

### Decisão 6 — A ROM de programa é modelada em Python, e isso é declarado

**Por quê:** simular a matriz de uma ROM porta a porta não ensina nada novo e multiplicaria
o tempo de execução por dez.

**O que se aprende:** que um bom modelo declara o que **não** modela. O número 829 é
honesto porque a fronteira está escrita. Projeto de engenharia que esconde a fronteira do
modelo produz número bonito e errado.

### Decisão 7 — Testes exaustivos onde eles cabem

**Por quê:** o somador de 4 bits tem 256 entradas possíveis. Testá-las **todas** é viável,
e então a corretude não é uma amostra: é uma prova por enumeração.

**O que se aprende:** a diferença mais bonita entre verificar hardware e verificar
software. É também o começo da ideia de **verificação formal** — quando o espaço cresce
demais para enumerar (um somador de 64 bits tem 2¹²⁸ entradas), a indústria parte para
provadores automáticos. Ver [`../60-teoria-avancada.md`](../60-teoria-avancada.md).

### Decisão 8 — Tratamento de erro real

`nand()` recusa qualquer sinal que não seja 0 ou 1, com uma exceção própria (`ErroDeSinal`).
Em hardware, um valor entre 0 e 1 é uma tensão intermediária: o circuito não decide,
consome corrente e esquenta. O simulador se recusa a fingir que isso é normal.

O computador também tem um **limite de instruções** (`limite=500`): um laço infinito é
detectado em vez de travar o processo. Hardware real tem o equivalente — o *watchdog timer*.

---

## O conjunto de instruções (ISA)

Cada instrução tem 8 bits: 4 de opcode e 4 de operando.

| Opcode | Nome | Efeito |
|---|---|---|
| 0 | `NOP` | não faz nada |
| 1 | `LDI n` | A = n (carrega imediato) |
| 2 | `ADD n` | A = A + n |
| 3 | `SUB n` | A = A − n |
| 4 | `AND n` | A = A E n (bit a bit) |
| 5 | `OR n` | A = A OU n |
| 6 | `XOR n` | A = A XOU n |
| 7 | `JMP n` | desvia para o endereço n |
| 8 | `JZ n` | desvia para n se a flag Z estiver acesa |
| 9 | `STA n` | RAM[n] = A |
| 10 | `LDA n` | A = RAM[n] |
| 11 | `OUT` | imprime A |
| 12 | `HLT` | para |

Só as operações da ULA (`ADD`, `SUB`, `AND`, `OR`, `XOR`) atualizam a flag Z — exatamente
como num processador de verdade. É por isso que, no programa de exemplo, o `STA` entre o
`SUB` e o `JZ` não estraga o salto.

### O programa de demonstração

```python
PROGRAMA_MULTIPLICA = [
    (LDI, 5),    #  0  A = 5           contador de repetições
    (STA, 0),    #  1  RAM[0] = A
    (LDI, 0),    #  2  A = 0
    (STA, 1),    #  3  RAM[1] = 0      acumulador do produto
    (LDA, 1),    #  4  A = RAM[1]      <-- início do laço
    (ADD, 3),    #  5  A = A + 3
    (STA, 1),    #  6  RAM[1] = A
    (LDA, 0),    #  7  A = RAM[0]
    (SUB, 1),    #  8  A = A - 1       e atualiza a flag Z
    (STA, 0),    #  9  RAM[0] = A
    (JZ, 12),    # 10  se Z, saia do laço
    (JMP, 4),    # 11  senão, repita
    (LDA, 1),    # 12  A = RAM[1]      o produto
    (OUT, 0),    # 13  imprime
    (HLT, 0),    # 14  para
]
```

Não existe instrução de multiplicar — como no 4004, e como em qualquer processador
simples. Multiplicação vira um laço de somas. É por isso que multiplicar era caríssimo
até multiplicadores em hardware ficarem baratos, e por isso que um `for` inocente em
software podia custar uma fortuna nos anos 1970.

---

## O inventário de portas (saída de `contagem.py`)

| Bloco | Portas NAND |
|---|---|
| ULA de 4 bits (8 operações) | 242 |
| Registrador A (4 bits) | 52 |
| Contador de programa (4 bits) | 88 |
| Flag Z (1 flip-flop) | 9 |
| Decodificador de instrução 4→16 | 100 |
| Lógica de controle | ~40 |
| Multiplexadores de escrita | 32 |
| RAM 4×4 de flip-flops | 266 |
| **TOTAL** | **829** |

E o custo de cada peça isolada:

| Peça | NANDs | Observação |
|---|---|---|
| NOT | 1 | NAND com as entradas juntas |
| AND | 2 | NAND + NOT |
| OR | 3 | De Morgan: 2 NOTs + 1 NAND |
| XOR | 4 | arranjo clássico |
| XNOR | 5 | XOR + NOT |
| meio somador | 6 | |
| **somador completo** | **9** | a peça mais importante da aritmética |
| somador de 4 bits | 36 | 4 × 9 |
| subtrator de 4 bits | 40 | reusa o somador |
| mux 2→1 | 4 | a peça mais repetida de uma CPU |
| decodificador 2→4 | 10 | |
| decodificador 4→16 | 100 | cresce exponencialmente |
| comparador de igualdade (4 bits) | 26 | |
| detector de zero | 10 | é o que faz `if (x == 0)` funcionar |
| deslocamento | **0** | é só refiação — não gasta porta |
| latch SR | 2 físicas | 6 avaliações até assentar |
| flip-flop D | 9 físicas | 26 avaliações por ciclo |

---

## Exercícios sobre este projeto

Em ordem de dificuldade. Os quatro primeiros cabem em uma tarde.

1. **Fácil.** Escreva um programa que calcule 2⁴ usando `ADD` (dobrar quatro vezes) e
   confirme que a saída é 0 — porque 16 não cabe em 4 bits. Explique o resultado.
2. **Fácil.** Meça, com `nand.custo()`, quanto custa um `XOR_n` de 8 entradas. Compare
   com a fórmula 4·(N−1) do docstring.
3. **Médio.** Acrescente a instrução `NOT` (A = ¬A) ao computador. A ULA já sabe fazer —
   você só precisa ligar o opcode ao código de operação. Escreva o teste antes.
4. **Médio.** Implemente a flag de vai-um (carry) como um flip-flop, e a instrução `JC`
   (saltar se houve transbordo). Quantas portas isso custou?
5. **Difícil.** Troque o somador de propagação por um somador **carry-lookahead** de 4 bits.
   Meça as duas coisas: portas gastas e profundidade lógica (o caminho mais longo). Você
   deve encontrar mais portas e menos profundidade — é o trade-off área × tempo em pessoa.
   Teoria em [`../20-circuitos-combinacionais.md`](../20-circuitos-combinacionais.md).
6. **Difícil.** Amplie tudo para 8 bits. Meça o novo total de portas e verifique se cresce
   linearmente. (A ULA cresce linearmente; o decodificador de endereço, não.)
7. **Muito difícil.** Escreva um montador (*assembler*) que traduza texto
   (`LDI 5 / ADD 3 / OUT`) para a lista de tuplas. É o primeiro degrau da cadeia de
   ferramentas que termina num compilador.

---

## Limitações declaradas

Um projeto de ensino honesto declara o que não faz:

- **Não há noção de tempo real.** Não se modela atraso de propagação em nanossegundos,
  então não dá para calcular frequência máxima de relógio. O simulador tem um modelo de
  *ordem*, não de *duração*.
- **A ROM é Python**, como explicado na Decisão 6.
- **Não há sinal de reset**, então o estado inicial é o que o construtor definiu. Hardware
  real precisa de reset, e esquecê-lo é uma armadilha clássica
  (ver [`../75-armadilhas.md`](../75-armadilhas.md)).
- **A RAM tem 4 palavras.** É pouco de propósito: com 16 palavras, ler a saída de
  `contagem.py` deixaria de caber na cabeça.
- **Não é sintetizável.** Isto é um simulador em Python, não Verilog. Para levar um
  projeto destes a uma FPGA, o caminho é reescrevê-lo em Verilog — há um esqueleto em
  [`../06-exemplos.md`](../06-exemplos.md), exemplo 11.

---

## Autoteste

1. Por que o projeto usa NAND como única primitiva, e não AND/OR/NOT?
2. Por que o somador completo direto custa 9 NANDs e não 15?
3. Explique por que um latch SR tem 2 portas físicas mas gasta 6 avaliações no simulador.
4. Por que a ULA calcula todas as 8 operações e descarta 7?
5. Quantas portas custou guardar 16 bits? Por que memória de verdade não é feita assim?
6. Por que a ROM ser modelada em Python **não** invalida o número 829?
7. O que um teste exaustivo prova que um teste por amostragem não prova?
8. O programa de multiplicação usa 46 instruções para calcular 3 × 5. O que isso diz sobre
   processadores sem multiplicador em hardware?

*(Respostas: 1 — completude funcional demonstrada na prática, e é o que o silício faz;
2 — compor dois meio-somadores repete lógica que o arranjo direto compartilha;
3 — a realimentação exige reavaliação até estabilizar, o que o silício faz sozinho;
4 — porque escolher com mux é mais rápido e simples que ligar/desligar blocos;
5 — 266 portas, ~66 por bit; SRAM usa 6 transistores por bit, ~40× mais barato;
6 — porque a fronteira do modelo está declarada e o custo da ROM é estimado à parte;
7 — corretude por enumeração completa, não por amostra;
8 — que multiplicar era caríssimo, e por isso multiplicadores em hardware mudaram o jogo.)*
