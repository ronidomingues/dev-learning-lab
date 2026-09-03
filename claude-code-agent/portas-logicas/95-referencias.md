# 95 · Referências — papers, specs, ferramentas e pessoas

**Nível:** todos · **Data de verificação: 14/08/2026**

Referências primárias e verificáveis. Onde não tive certeza da referência completa, indiquei
apenas autor, título e ano.

---

## 1. Papers seminais

### Fundação

| Referência | Por que importa |
|---|---|
| **Boole, George.** *An Investigation of the Laws of Thought* (1854) | funda a álgebra que descreve todo circuito digital. Domínio público. |
| **Shannon, Claude E.** *A Symbolic Analysis of Relay and Switching Circuits* — dissertação de mestrado, MIT, 1937 (publicada em *Transactions of the AIEE*, 1938) | **liga álgebra booleana a circuitos**. Torna o projeto de circuitos uma disciplina matemática. Leia o original: ~70 páginas, claríssimo. |
| **Shannon, Claude E.** *The Synthesis of Two-Terminal Switching Circuits* — *Bell System Technical Journal*, 1949 | contém o **argumento de contagem**: quase toda função booleana exige circuito de tamanho ~2ⁿ/n. Ver [`60`](60-teoria-avancada.md), §2. |
| **Shannon, Claude E.** *A Mathematical Theory of Communication* — BSTJ, 1948 | funda a teoria da informação. Não é sobre portas, mas é o outro pilar da era digital. |

### Complexidade de circuitos

| Referência | Resultado |
|---|---|
| **Furst, Saxe & Sipser** (1981) e **Håstad** (1986) | **paridade não está em AC⁰**; o *switching lemma* de Håstad é a técnica |
| **Razborov, A.** (1985) | limite inferior superpolinomial para **circuitos monótonos** (problema do clique) |
| **Tardos, É.** (1988) | mostra que a lacuna monótono/geral é exponencial — fecha aquele caminho |
| **Razborov & Rudich** — *Natural Proofs* (STOC 1994; JCSS 1997) | **a barreira**: técnicas conhecidas não podem separar P de NP se existirem funções pseudoaleatórias fortes |
| **Karp & Lipton** (1980) | se NP ⊆ P/poly, a hierarquia polinomial colapsa |
| **Ajtai, Komlós & Szemerédi** (1983) | rede de ordenação de profundidade O(log n) — ótima e praticamente inútil |
| **Bryant, R.** *Graph-Based Algorithms for Boolean Function Manipulation* — IEEE ToC, 1986 | introduz os **ROBDDs**; base de ferramentas industriais de verificação |

### Física e limites

| Referência | Resultado |
|---|---|
| **Landauer, R.** *Irreversibility and Heat Generation in the Computing Process* — IBM Journal of R&D, 1961 | apagar 1 bit dissipa ao menos `k_B·T·ln 2` |
| **Bennett, C. H.** *Logical Reversibility of Computation* — IBM Journal of R&D, 1973 | mostra como computar sem apagar: compute, copie, desfaça |
| **Fredkin & Toffoli** *Conservative Logic* — Int. J. Theor. Phys., 1982 | portas reversíveis universais |
| **Bérut et al.** — *Nature*, 2012 | **verificação experimental** do princípio de Landauer |
| **Dennard, R. et al.** *Design of Ion-Implanted MOSFETs with Very Small Physical Dimensions* — IEEE JSSC, 1974 | a **escala de Dennard**, morta por volta de 2005 |
| **Moore, G.** *Cramming More Components onto Integrated Circuits* — *Electronics*, 1965 | a Lei de Moore, no artigo original |

### Arquitetura

| Referência | Resultado |
|---|---|
| **von Neumann, J.** *First Draft of a Report on the EDVAC* (1945) | o modelo de programa armazenado |
| **Kogge & Stone** (1973) | somador de prefixo paralelo de profundidade O(log n) |
| **Brent & Kung** (1982) | somador de prefixo com menos fios |
| **Wallace, C. S.** *A Suggestion for a Fast Multiplier* (1964) | árvore de redução para multiplicação |
| **Booth, A. D.** (1951) | codificação que reduz produtos parciais |
| **Tomasulo, R.** (1967) | execução fora de ordem — a base dos processadores modernos |
| **Esmaeilzadeh et al.** *Dark Silicon and the End of Multicore Scaling* (ISCA 2011) | formaliza o **silício escuro** |

---

## 2. Especificações e normas

| Documento | Onde |
|---|---|
| **IEEE 1364** — Verilog HDL | padrão histórico (2001/2005), hoje absorvido pelo 1800 |
| **IEEE 1800** — SystemVerilog | o padrão atual de HDL |
| **IEEE 1076** — VHDL | |
| **IEEE 91/91a** — símbolos gráficos para diagramas lógicos | define os símbolos "distintivos" (as formas de D e escudo) e os retangulares da IEC |
| **IEC 60617-12** | símbolos retangulares, com notação `&`, `≥1`, `=1` — comuns na Europa |
| **RISC-V ISA Specifications** | https://riscv.org/technical/specifications/ — livres, e legíveis |
| **JEDEC** — padrões de memória (DDR, LPDDR) | https://www.jedec.org/ |
| **IEEE 754** — aritmética de ponto flutuante | o que a FPU implementa em portas |

---

## 3. Datasheets e catálogos

| Recurso | Uso |
|---|---|
| **Texas Instruments — série 74HC/74HCT/74LVC** | https://www.ti.com/ — datasheets dos CIs; a fonte primária de tempos, tensões e fan-out |
| **Nexperia — portfólio de lógica** | https://www.nexperia.com/ — outro grande fabricante da série 74 |
| Bibliotecas de células abertas (SKY130, GF180, IHP SG13G2) | **veja como é uma biblioteca real**: cada célula com área, atraso, potência e layout |
| **Datasheets do Logisim** (documentação interna) | referência dos componentes do simulador |

**Sugestão prática:** abra o datasheet do **74HC00** uma vez na vida e leia inteiro. Vinte
páginas ensinam mais sobre a realidade de uma porta lógica — tempos, correntes, faixas de
tensão, condições absolutas máximas — que qualquer capítulo de livro.

---

## 4. Ferramentas — repositórios oficiais

| Ferramenta | Repositório |
|---|---|
| Logisim-evolution | https://github.com/logisim-evolution/logisim-evolution |
| Digital (hneemann) | https://github.com/hneemann/Digital |
| Icarus Verilog | https://github.com/steveicarus/iverilog |
| Verilator | https://github.com/verilator/verilator |
| GTKWave | https://github.com/gtkwave/gtkwave |
| Surfer | https://surfer-project.org/ |
| Yosys | https://github.com/YosysHQ/yosys |
| nextpnr | https://github.com/YosysHQ/nextpnr |
| OpenROAD | https://github.com/The-OpenROAD-Project/OpenROAD |
| OpenLane / OpenLane2 | https://github.com/efabless/openlane2 |
| SKY130 PDK | https://github.com/google/skywater-pdk |
| IHP Open PDK (SG13G2) | https://github.com/IHP-GmbH/IHP-Open-PDK |
| Amaranth (HDL em Python) | https://github.com/amaranth-lang/amaranth |
| cocotb (testbench em Python) | https://github.com/cocotb/cocotb |

---

## 5. Sites e comunidades

| Recurso | O que é |
|---|---|
| **nandgame.com** | construir um computador do relé à CPU, jogando |
| **CircuitVerse.org** | simulador no navegador, com biblioteca comunitária de circuitos |
| **falstad.com/circuit** | simulador analógico+digital; mostra corrente fluindo |
| **HDLBits** (cs.stevens/hdlbits) | exercícios de Verilog com correção automática |
| **EDA Playground** | rodar HDL no navegador em simuladores profissionais |
| **DigitalJS Online** (digitaljs.tilk.eu) | sintetiza Verilog e **desenha o circuito resultante** |
| **Tiny Tapeout** (tinytapeout.com) | fabricar seu próprio chip por ~€ 70 |
| **open-source-silicon.dev** | comunidade de silício aberto (Slack/fórum) |
| **r/FPGA, r/chipdesign** (Reddit) | comunidades ativas e de bom nível técnico |
| **WikiChip** (wikichip.org) | dados técnicos de microarquiteturas comerciais |
| **AnandTech (arquivo), Chips and Cheese, SemiAnalysis** | análise técnica aprofundada de chips |

---

## 6. Pessoas a acompanhar

Não por celebridade — por qualidade consistente do que publicam.

| Pessoa | O que faz | Onde |
|---|---|---|
| **Ben Eater** | constrói computadores em protoboard, explicando cada fio | YouTube, eater.net |
| **Sarah Harris & David Harris** | autores do livro-texto de referência; material aberto | pages.hmc.edu/harris |
| **Matt Venn** | criador do Tiny Tapeout; democratizou o tapeout | tinytapeout.com, Zero to ASIC |
| **Claire Wolf (Clifford Wolf)** | criou o Yosys e a cadeia aberta de FPGA | YosysHQ |
| **Onur Mutlu** | aulas de arquitetura de computadores, todas abertas | YouTube, ETH Zurich |
| **David Patterson** | RISC, RISC-V, os livros-texto | Berkeley, RISC-V International |
| **Shimon Schocken & Noam Nisan** | Nand2Tetris | nand2tetris.org |
| **Bunnie Huang** | engenharia reversa de hardware, hardware aberto | bunniestudios.com |

---

## 7. Como verificar um número sobre chips

Metodologia, já que este curso insiste em números com fonte:

| Pergunta | Fonte confiável | Fonte a evitar |
|---|---|---|
| Quantos transistores tem o chip X? | anúncio do fabricante; Wikipedia *Transistor count* (que compila e cita) | posts de blog sem fonte |
| Qual a área do die? | análise de *die shot* (TechInsights, ChipRebel); às vezes o fabricante | estimativas de fórum |
| Qual a densidade do nó? | material técnico da foundry; IEEE Spectrum; SemiAnalysis | material de marketing |
| Quantas portas tem o núcleo X? | ficha técnica do IP (a ARM publica "~12k portas" para o Cortex-M0) | **quase sempre não existe** |
| Qual o consumo real? | medições independentes | TDP de fabricante (é limite térmico, não consumo) |

**Regra que uso:** se um número sobre semicondutores aparece sem data, sem fonte e sem nó
de fabricação, trate-o como decorativo.

---

## 8. Referências deste curso

Onde cada número deste material foi obtido:

| Número | Fonte |
|---|---|
| Contagens de portas do projeto-modelo (829, 242, 36, 9…) | **medidas** por `07-projeto-modelo/contagem.py`, executado em 14/08/2026 |
| Contagens de transistores (4004, 8086, Pentium, M1–M4, Rubin, Vera) | Wikipedia, *Transistor count*, consultada em 14/08/2026 |
| Versões de ferramentas (Logisim 4.1.0, Digital 0.31, iverilog 13.0) | API do GitHub, consultada em 14/08/2026 |
| Nós de fabricação e datas (N2, 18A, A16, A14, CFET) | TSMC, IEEE Spectrum, SemiAnalysis, SemiWiki, Tom's Hardware (roteiro da imec), 14/08/2026 |
| Preços (Tiny Tapeout, FPGAs, câmbio) | páginas oficiais e levantamento de mercado, 14/08/2026 |
| Cursos (PT/EN/FR) | pesquisa na web em 14/08/2026; links no [`85`](85-cursos-e-certificacoes.md) |
| Edições de livros | páginas de editoras e livrarias, 14/08/2026; ver [`90`](90-bibliografia.md) |
| Estimativas de composição de SoC e de portas por chip comercial | **minhas**, com as premissas declaradas em [`50`](50-quantas-portas-tem-um-computador.md), §6 |

---

## Autoteste

1. Qual paper de 1937 transformou projeto de circuitos em matemática aplicada?
2. Onde está o argumento de contagem que prova que quase toda função é difícil?
3. Qual paper de 1994 mostrou que as técnicas conhecidas de limite inferior são insuficientes?
4. Quanto vale o limite de Landauer, e em que paper de 1961 ele aparece?
5. Qual norma define os símbolos gráficos das portas lógicas?
6. Qual datasheet vale a pena ler inteiro uma vez na vida, e por quê?
7. Onde encontrar uma biblioteca de células real, aberta, para ver como é?
8. Como verificar a contagem de transistores de um chip comercial?

*(Respostas: 1 — a dissertação de Shannon no MIT; 2 — Shannon, *The Synthesis of
Two-Terminal Switching Circuits*, BSTJ 1949; 3 — Razborov & Rudich, *Natural Proofs*;
4 — k_B·T·ln 2, no artigo de Landauer no IBM Journal of R&D; 5 — IEEE 91/91a e
IEC 60617-12; 6 — o do 74HC00, porque mostra a realidade elétrica de uma porta;
7 — nos PDKs abertos SKY130, GF180 ou IHP SG13G2; 8 — anúncio do fabricante, ou a página
*Transistor count* da Wikipedia, que compila e cita as fontes.)*
