# Glossário

**Data:** 14/08/2026 · ~140 termos

Termos em inglês estão indicados quando é assim que o campo os usa. Ordem alfabética
portuguesa. O arquivo onde o termo é tratado a fundo está indicado entre colchetes.

---

## A

**AC⁰** — Classe de complexidade: circuitos de profundidade constante, tamanho polinomial e
fan-in ilimitado. Provadamente **não** contém a paridade. [`60`]

**Adiabática (lógica)** — Estilo de circuito que recupera parte da energia em vez de
dissipá-la, comutando lentamente. Pesquisa, não produto. [`60`]

**Álgebra booleana** — Sistema algébrico com operações ∧, ∨, ¬ sobre {0,1}. Descreve toda
lógica digital. [`10`]

**AOI / OAI** — *AND-OR-Invert* / *OR-AND-Invert*. Células CMOS compostas que fazem em 6
transistores o que três portas separadas fariam em 12+. Muito usadas por ferramentas de
síntese. [`50`]

**ASIC** — *Application-Specific Integrated Circuit*. Chip fabricado sob medida, em oposição
à FPGA configurável.

**Ativo em baixo** (*active low*) — Sinal cuja função ocorre quando vale 0. Notado
`RESET_n`, `/RESET`, `RESET#` ou com barra em cima. [`05`, `75`]

**Atraso de propagação** (*propagation delay*, t_pd) — Tempo entre a mudança da entrada e a
da saída de uma porta. Vem de carregar capacitâncias. [`12`]

## B

**Backside power delivery** — Alimentação do chip pela parte de trás do wafer, separada dos
fios de sinal. Em produção desde 2025 (Intel PowerVia). [`65`]

**Barrel shifter** — Deslocador por quantidade variável em um único ciclo. Custa n·log n
muxes. [`20`]

**BCD** — *Binary-Coded Decimal*. Cada dígito decimal em 4 bits.

**BDD / ROBDD** — *(Reduced Ordered) Binary Decision Diagram*. Representação canônica de
função booleana; base de verificação formal. [`10`, `60`]

**Bit** — Menor unidade de informação: 0 ou 1. De *binary digit*.

**Buffer** — Porta que repete o valor de entrada. Logicamente inútil, eletricamente
essencial: reforça o sinal. [`01`]

**Byte** — 8 bits.

## C

**Caminho crítico** — O caminho mais longo (em atraso) entre dois elementos de memória.
Determina a frequência máxima. [`30`]

**Carry** (vai-um) — O "1" que passa de uma casa para a seguinte numa soma. [`20`]

**Carry-lookahead** — Somador que calcula todos os vai-uns em paralelo, com profundidade
constante por bloco. [`20`]

**Célula padrão** (*standard cell*) — Bloco pré-projetado de uma biblioteca da foundry:
uma porta com layout, área, atraso e potência caracterizados. [`40`, `50`]

**CFET** — *Complementary FET*: transistor N empilhado sobre o P. Próximo grande salto de
densidade; não em produção em 2026. [`65`]

**Chiplet** — Die pequeno que compõe, com outros, um produto final. Melhora rendimento e
permite misturar nós de fabricação. [`65`]

**Clock** (relógio) — Sinal periódico que sincroniza um circuito. Define os instantes de
captura. [`30`]

**Clock enable** — Sinal que habilita a captura de um flip-flop sem alterar o relógio.
A forma correta de "desacelerar" um circuito. [`75`]

**Clock gating** — Desligar o relógio de blocos ociosos para economizar potência dinâmica.

**CMOS** — *Complementary Metal-Oxide-Semiconductor*. Tecnologia dominante desde os anos
1980: usa transistores N e P complementares, com consumo estático quase nulo. [`12`]

**Codificador de prioridade** — Devolve o índice da entrada ativa de maior prioridade.
Base de controladores de interrupção. [`20`]

**Complemento de dois** — Representação de números negativos: inverta os bits e some 1.
Permite que o mesmo somador some e subtraia. [`20`]

**Completude funcional** — Propriedade de um conjunto de portas com que se constrói qualquer
função booleana. NAND sozinha tem; {AND, OR} não tem. [`10`]

**CPP** — *Contacted Poly Pitch*. Métrica real de densidade, ao contrário do nome do nó. [`65`]

**CRC** — *Cyclic Redundancy Check*. Detecção de erro por divisão polinomial; em hardware,
um registrador de deslocamento com XORs. [`06`]

## D

**Datapath** (caminho de dados) — A parte do processador que move e transforma dados:
registradores, ULA, muxes. [`40`]

**De Morgan (leis de)** — `¬(A·B) = ¬A + ¬B` e `¬(A+B) = ¬A·¬B`. Permite converter qualquer
circuito em só-NAND ou só-NOR. [`05`, `10`]

**Decodificador** — Converte um número de k bits em 2ᵏ linhas, uma só ativa (*one-hot*).
Base do endereçamento de memória. [`20`]

**Dennard (escala de)** — Lei de 1974: encolher o transistor mantinha a densidade de
potência constante. **Morreu por volta de 2005.** [`11`]

**Die** — O pedaço de silício de um chip, antes do encapsulamento.

**DRAM** — Memória dinâmica: 1 transistor + 1 capacitor por bit; precisa ser recarregada
periodicamente. [`30`]

**DRC / LVS** — Verificações físicas do layout: regras de desenho e correspondência com o
esquemático. [`40`]

## E

**ECC** — *Error-Correcting Code*. Em memória de servidor, tipicamente SECDED: corrige 1
erro e detecta 2. Feito de árvores de XOR. [`06`]

**ECL** — *Emitter-Coupled Logic*. Família bipolar dez vezes mais rápida que TTL; extinta
por consumo. [`12`]

**EDA** — *Electronic Design Automation*. As ferramentas de projeto de chips.

## F

**Fan-in** — Número de entradas de uma porta. Alto fan-in é lento (transistores em série).

**Fan-out** — Número de entradas alimentadas por uma saída. Cada uma acrescenta
capacitância e atraso. [`12`]

**FinFET** — Transistor com canal em forma de aleta, envolvido pela porta em três lados.
Em produção de 2011 a ~2024. [`65`]

**Flip-flop** — Elemento de memória sensível à **borda** do relógio. O elemento padrão de
todo hardware síncrono. [`30`]

**Fórmula** — Circuito em que toda porta tem fan-out 1 (uma árvore). Não reaproveita
subresultados. [`60`]

**FPGA** — *Field-Programmable Gate Array*. Chip reconfigurável, feito de LUTs, flip-flops
e interconexão programável. [`03`, `80`]

**Foundry** — Fábrica de semicondutores (TSMC, Samsung, Intel Foundry, GlobalFoundries).

## G

**GAA / nanosheet** — *Gate-All-Around*: a porta envolve o canal pelos quatro lados.
Em produção desde 2025. [`65`]

**Gate equivalent (GE)** — Unidade de área normalizada: 1 GE = área de um NAND2 mínimo.
**É o que a indústria conta, e não portas.** [`50`]

**Glitch** — Pulso espúrio causado por caminhos com atrasos diferentes. Invisível para a
álgebra booleana. [`12`, `20`]

**Gray (código)** — Codificação em que valores consecutivos diferem em um único bit. Usado
em mapas de Karnaugh e em cruzamento de domínios de relógio. [`20`, `30`]

## H

**Hazard** — Ver *glitch*. Classificado em estático-0, estático-1, dinâmico e funcional. [`20`]

**HBM** — *High Bandwidth Memory*. Pilha de DRAM ligada ao processador por interposer.

**HDL** — *Hardware Description Language*. Verilog, SystemVerilog, VHDL. [`05`]

**Hold (t_hold)** — Tempo mínimo que o dado deve permanecer estável **depois** da borda.
Violação não se corrige baixando a frequência. [`30`]

## I

**IC / CI** — Circuito integrado.

**IR drop** — Queda de tensão na rede de alimentação devido à resistência dos fios. Um dos
motivos do backside power. [`65`]

## K

**Karnaugh (mapa de)** — Tabela-verdade reorganizada em código de Gray, para minimização
visual. Útil até 4 variáveis; **ferramenta pedagógica, não profissional**. [`20`, `75`]

**Kogge-Stone** — Somador de prefixo paralelo de profundidade O(log n); rápido e caro em
fios. [`20`]

## L

**Landauer (limite de)** — Apagar 1 bit dissipa no mínimo `k_B·T·ln 2` ≈ 2,85×10⁻²¹ J a
300 K. Estamos ~30.000× acima disso em 2026. [`60`]

**Latch** — Elemento de memória sensível a **nível** (transparente enquanto habilitado).
Diferente de flip-flop. [`30`]

**Latch acidental** — Latch inferido sem intenção pelo sintetizador, por caminho sem
atribuição num bloco combinacional. **O bug nº 1 em Verilog.** [`75`]

**LFSR** — *Linear Feedback Shift Register*. Registrador de deslocamento com XORs na
realimentação; base de CRC e de geradores pseudoaleatórios. [`06`]

**LUT** — *Look-Up Table*. A célula lógica da FPGA: um mux com memória, capaz de
implementar qualquer função de k entradas. [`20`]

## M

**Máquina de estados (FSM)** — Circuito sequencial formalizado: estados, transições e
saídas. Variedades **Moore** (saída depende só do estado) e **Mealy** (depende também da
entrada). [`30`]

**Margem de ruído** — Folga entre o que uma saída garante produzir e o que uma entrada
garante aceitar. **É a propriedade que torna a computação digital confiável.** [`12`]

**Metaestabilidade** — Estado indefinido de um flip-flop cujo dado violou setup/hold. Não se
elimina; reduz-se a probabilidade com sincronizadores. [`30`]

**Mintermo** — Termo AND que vale 1 em exatamente uma linha da tabela-verdade. [`10`]

**Monótona (função)** — Função em que trocar uma entrada de 0 para 1 nunca faz a saída cair
de 1 para 0. É tudo que {AND, OR} consegue produzir. [`10`, `60`]

**MOSFET** — Transistor de efeito de campo com porta isolada por óxido. O componente básico
de tudo. [`12`]

**MTr/mm²** — Milhões de transistores por milímetro quadrado. **A métrica que faz sentido**,
ao contrário do nome do nó. [`65`]

**Multiplexador (mux)** — Seleciona uma entre n entradas. A peça mais repetida de um
processador; é o `if` do hardware. [`20`]

## N

**NAND** — NÃO-E. Custa 4 transistores em CMOS, é a porta mais barata e é **funcionalmente
completa sozinha**. [`10`, `12`]

**NC¹, NC** — Classes de circuitos de profundidade O(log n) e polilogarítmica. "Eficientemente
paralelizável". [`60`]

**Nibble** — 4 bits.

**Nó de fabricação** (*process node*) — "2 nm", "3 nm". **Nome comercial desde ~2000**;
nada mede isso fisicamente. [`65`]

**NOR** — NÃO-OU. Também funcionalmente completa sozinha. O computador da Apollo foi feito
só com ela. [`10`]

## O

**One-hot** — Codificação em que exatamente um bit está ativo. Saída de decodificadores e
codificação preferida de FSM em FPGA. [`30`]

**Overflow** (transbordo) — O resultado não cabe na largura. Detecção diferente para números
com e sem sinal. [`20`]

## P

**P/poly** — Classe de problemas com famílias de circuitos de tamanho polinomial. Contém
problemas indecidíveis, por não exigir uniformidade. [`60`]

**Paridade** — XOR de todos os bits: 1 se o número de 1s for ímpar. Detecção de erro de 1
bit. Provadamente fora de AC⁰. [`06`, `60`]

**PDK** — *Process Design Kit*. O conjunto de regras, modelos e bibliotecas de uma foundry.
Normalmente sob NDA; há versões abertas (SKY130, GF180, IHP SG13G2). [`80`]

**Pipeline** — Cortar a lógica em estágios separados por flip-flops. **Aumenta a vazão, não
reduz a latência.** [`30`, `40`]

**Place & route** — Etapa que decide onde cada célula fica e por onde cada fio passa. [`40`]

**PLL** — *Phase-Locked Loop*. Circuito analógico que gera e multiplica relógios.

**Power gating** — Cortar a alimentação de blocos inteiros, contra corrente de fuga.

**Profundidade** (*depth*) — Comprimento do caminho mais longo de um circuito. Corresponde
ao atraso. [`60`]

**Pull-up / pull-down** — Resistor que define o nível de um sinal que ficaria flutuante. [`75`]

## Q

**Qubit** — Unidade quântica de informação; estado é um vetor em ℂ². Portas quânticas são
matrizes unitárias, sempre reversíveis. [`60`, `65`]

**Quine–McCluskey** — Algoritmo tabular de minimização. Correto para qualquer número de
variáveis, exponencial no pior caso. [`20`]

## R

**RAS / CAS** — *Row/Column Address Strobe*. Consequência direta da decodificação de memória
em dois níveis. [`20`]

**Registrador** — Conjunto de flip-flops que guarda uma palavra. [`30`]

**Reset** — Sinal que leva o circuito a um estado conhecido. Assíncrono na aplicação e
síncrono na soltura é o padrão da indústria. [`30`, `75`]

**Reversível (lógica)** — Circuito bijetivo, que não apaga informação e, em princípio, pode
dissipar energia arbitrariamente pequena. Portas Toffoli e Fredkin. [`60`]

**Ripple-carry** — Somador em que o vai-um percorre os estágios em série. Simples e lento
(atraso O(n)). [`20`]

**RTL** — *Register-Transfer Level*. Nível de descrição em que se escreve Verilog/VHDL. [`40`]

## S

**Setup (t_setup)** — Tempo mínimo que o dado deve estar estável **antes** da borda. [`30`]

**Silício escuro** (*dark silicon*) — Parte do chip que não pode ser ligada simultaneamente
sem derreter. Consequência do fim da escala de Dennard. [`11`]

**Sincronizador** — Dois flip-flops em série que reduzem a probabilidade de metaestabilidade
ao cruzar domínios de relógio. **Obrigatório.** [`30`, `75`]

**Síntese lógica** — Transformar descrição comportamental em rede de portas de uma
biblioteca. É onde as portas efetivamente aparecem. [`40`]

**Skew** (do relógio) — Diferença de tempo de chegada do relógio a flip-flops distintos.
Entra na equação de f_max. [`30`]

**SOP / POS** — *Sum of Products* / *Product of Sums*. Formas normais que garantem que toda
função tem implementação. [`10`]

**SRAM** — Memória estática: 6 transistores por bit. **Não é porta lógica** — é a razão de
não se poder dividir transistores por 4 para contar portas. [`30`, `50`]

**SystemVerilog** — Extensão do Verilog (IEEE 1800). Traz `logic`, `always_ff`,
`always_comb` e recursos de verificação. [`05`]

## T

**Tabela-verdade** — Lista de todas as combinações de entrada com a saída correspondente.
A definição completa de uma função booleana. [`01`, `10`]

**Tamanho** (*size*) — Número de portas de um circuito. Corresponde a área e custo. [`60`]

**Tapeout** — Envio do projeto final para fabricação. Custa de € 70 (Tiny Tapeout) a dezenas
de milhões de dólares (nó avançado). [`80`]

**TC⁰** — Classe de circuitos de profundidade constante com portas de limiar (maioria).
Contém multiplicação e é o modelo natural de redes neurais. [`60`]

**Termo de consenso** — Termo logicamente redundante acrescentado para eliminar um glitch.
[`12`, `20`]

**Toffoli (porta)** — Porta reversível universal de 3 entradas e 3 saídas. [`60`]

**Transistor** — Chave controlada por tensão. 2 a 12 por porta; **não** é sinônimo de porta.
[`12`]

**TTL** — *Transistor-Transistor Logic*. Família da série 7400 original. Obsoleta;
substituída por CMOS (74HC, 74LVC). [`12`]

## U

**ULA / ALU** — Unidade Lógica e Aritmética. Soma, subtrai e opera bit a bit, com um mux
escolhendo o resultado. [`20`]

**Uniformidade** — Propriedade de uma família de circuitos construível por algoritmo
eficiente. Sem ela, circuitos decidem problemas indecidíveis. [`60`]

## V

**Verificação formal** — Provar matematicamente que um circuito satisfaz uma
especificação, em vez de testá-lo por amostragem. Virou obrigatória depois do bug FDIV do
Pentium (1994). [`60`]

**Verilog** — HDL mais usada na indústria (IEEE 1364, hoje absorvida pelo 1800). [`05`]

**VHDL** — HDL mais verbosa e mais rígida com tipos (IEEE 1076). Preferida em setores
críticos. [`05`]

## X

**XOR** — OU exclusivo: 1 quando as entradas diferem. Custa 8–12 transistores (é a porta
cara). Base de somadores, paridade, CRC e criptografia. [`05`, `06`]

**XNOR** — Negação do XOR: 1 quando as entradas são iguais. É o comparador de 1 bit. [`05`]

## Y

**Yosys** — Ferramenta livre de síntese lógica. Transforma Verilog em rede de portas. [`80`]

---

## Termos que confundem — as distinções que mais importam

| Par | Diferença |
|---|---|
| **Porta lógica × porta do transistor** | a primeira é a peça lógica (*logic gate*); a segunda é o terminal de controle do MOSFET (*transistor gate*) |
| **Transistor × porta** | 2 a 12 transistores formam uma porta; e 6 transistores de SRAM não formam porta nenhuma |
| **Latch × flip-flop** | sensível a nível × sensível a borda |
| **Lei de Moore × escala de Dennard** | densidade × densidade de potência; só a segunda morreu |
| **Setup × hold** | dado estável antes × depois da borda; só a violação de setup se corrige com frequência |
| **Tamanho × profundidade** | número de portas × atraso |
| **Sincronizador × anti-repique** | metaestabilidade (ns) × ruído mecânico (ms); precisa dos dois |
| **OR × XOR** | "ou" inclusivo × "ou" exclusivo — a primeira armadilha de todo iniciante |
| **`=` × `<=` em Verilog** | combinacional × sequencial |
| **Overflow com sinal × sem sinal** | `c_n ⊕ c_{n−1}` × vai-um final |
