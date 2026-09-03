# 90 · Bibliografia comentada

**Nível:** todos · **Data de verificação das edições: 14/08/2026**

Nada aqui foi inventado. Onde não tive certeza de ISBN ou de edição, cito apenas autor,
título e editora. Onde o livro é **legalmente gratuito**, isso está marcado com 🆓.

---

## Se você só for ler um

| Perfil | Livro |
|---|---|
| Leigo curioso | **Petzold, *Code*** |
| Quer construir | **Nisan & Schocken, *The Elements of Computing Systems*** 🆓 (parcial) |
| Estudante de engenharia | **Harris & Harris, *Digital Design and Computer Architecture*, RISC-V Edition** |
| Estudante brasileiro | **Idoeta & Capuano, *Elementos de Eletrônica Digital*** |
| Quer o silício | **Weste & Harris, *CMOS VLSI Design*** |
| Quer a teoria | **Arora & Barak, *Computational Complexity*** 🆓 (rascunho) |

---

## 1. Para leigos e curiosos

### Petzold, Charles. *Code: The Hidden Language of Computer Hardware and Software*
Microsoft Press · **2ª edição, 2022** (1ª de 1999)

O melhor livro de divulgação já escrito sobre computação. Começa com uma lanterna e o
código Morse e chega, sem pular etapas e sem exigir nada do leitor, a um computador
funcionando. A 2ª edição acrescentou capítulos e melhorou os diagramas.

**Nível:** leigo absoluto. **Envelheceu?** Não — trata de fundamentos.
**Em português:** existe *Código: os bastiores da linguagem de computadores* (edição
brasileira mais antiga); confirme a edição antes de comprar, pois a 2ª edição inglesa é
substancialmente melhor.

**Por que ler:** é o único livro que consegue ser rigoroso e acessível ao mesmo tempo.
Se você gostou do [`01`](01-introducao-leigo.md) deste curso, este livro é a versão de 500
páginas dele.

### Nisan, Noam & Schocken, Shimon. *The Elements of Computing Systems: Building a Modern Computer from First Principles*
MIT Press · **2ª edição, 2021** (1ª de 2005) · 🆓 **os primeiros capítulos e todos os
projetos e ferramentas estão livres em https://www.nand2tetris.org/**

O livro do Nand2Tetris. Você constrói, na ordem: portas a partir de NAND, ULA, memória,
CPU, montador, máquina virtual, compilador e sistema operacional.

**Nível:** iniciante a intermediário, sem pré-requisitos.
**O que faz melhor que os outros:** é o único que fecha o ciclo inteiro, e o faz com você
construindo cada peça. Ler sobre uma ULA e implementar uma são experiências
incomparáveis.
**Limitação:** não trata de eletrônica (transistor, CMOS, timing) nem de desempenho real.
É lógica pura. Este curso cobre justamente o que falta lá.

---

## 2. Livros-texto universitários

### Harris, David & Harris, Sarah. *Digital Design and Computer Architecture*
Morgan Kaufmann · **RISC-V Edition, 2021** (ISBN 978-0-12-820064-3) · também há
*ARM Edition* (2015) e *2nd Edition*, baseada em MIPS (2012)

**Na minha opinião, o melhor livro-texto do assunto em atividade.** Vai de portas lógicas
até um microprocessador RISC-V com pipeline, com Verilog **e** VHDL lado a lado em todos os
exemplos, e uma escrita com bom humor — o que é raríssimo na área.

**Nível:** universitário, 1º–3º ano. **Envelheceu?** Não; a edição RISC-V é atual.
**Qual edição escolher:** a **RISC-V** se você está começando agora (é a arquitetura do
futuro e a mais simples de entender). A ARM se você trabalha com sistemas embarcados
comerciais. A de MIPS só se seu curso exigir.

### Mano, M. Morris & Ciletti, Michael D. *Digital Design: With an Introduction to the Verilog HDL, VHDL, and SystemVerilog*
Pearson · **6ª edição, 2018**

O clássico absoluto. Muitas gerações aprenderam Karnaugh, formas normais e projeto
sequencial aqui. Metódico, completo, e um pouco árido.

**Nível:** universitário. **Envelheceu?** Parcialmente: a ênfase em minimização manual
reflete uma época em que isso era ofício. Continua excelente como referência de
fundamentos.
**Em português:** há edições anteriores traduzidas como *Projeto Digital* (Prentice Hall/
Pearson). Tradução aceitável; confira qual edição está sendo vendida.

### Tocci, Ronald J.; Widmer, Neal S. & Moss, Gregory L. *Sistemas Digitais: Princípios e Aplicações*
Pearson · **12ª edição, edição brasileira de 2018** (ISBN 978-85-430-2501-8)

O livro-texto mais adotado nos cursos brasileiros de engenharia e nos cursos técnicos.
Cobre do sistema de numeração aos dispositivos programáveis, com VHDL e AHDL, e a 12ª
edição retirou tecnologias obsoletas e acrescentou material sobre diagnóstico de defeitos
em circuitos prototipados.

**Nível:** técnico e universitário inicial. **Tradução:** boa, revisada por professores
brasileiros (Sérgio Nascimento e Renato Giacomini na 12ª).
**Por que considerar:** se você está numa faculdade brasileira, provavelmente é o livro
adotado, e ter o mesmo livro do professor facilita a vida.

### Idoeta, Ivan Valeije & Capuano, Francisco Gabriel. *Elementos de Eletrônica Digital*
Érica · **42ª edição** (o livro tem edições sucessivas desde os anos 1980) · 687 páginas

O clássico brasileiro. Sistemas de numeração, portas, álgebra de Boole, simplificação,
circuitos combinacionais, codificadores, aritméticos, flip-flops, registradores, contadores
síncronos e assíncronos, conversores A/D e D/A, multiplex, memórias e famílias lógicas.

**Nível:** técnico e universitário inicial. **Envelheceu?** Nos fundamentos, não. Na
tecnologia (famílias lógicas, dispositivos), sim — trata de um mundo de CIs discretos que
já não é o da indústria. **Mas** é exatamente por isso que continua ótimo para quem vai
montar circuitos na bancada.
**Ponto forte:** a quantidade de exercícios resolvidos. É o livro que mais ensina "pela
mão" em português.

### Wakerly, John F. *Digital Design: Principles and Practices*
Pearson · **5ª edição, 2018**

Mais orientado à prática de engenharia que o Mano: trata de questões reais de temporização,
famílias lógicas, ruído e implementação. Bom **segundo** livro.

---

## 3. Arquitetura de computadores (o passo seguinte)

### Patterson, David A. & Hennessy, John L. *Computer Organization and Design: The Hardware/Software Interface — RISC-V Edition*
Morgan Kaufmann · **2ª edição, 2020**

A continuação natural do [`40`](40-da-porta-ao-computador.md) deste curso. Caminho de dados,
pipeline, hierarquia de memória, paralelismo — com RISC-V.

**Nível:** universitário intermediário.
**Em português:** há edições traduzidas das versões MIPS/ARM (*Organização e Projeto de
Computadores*, Elsevier/Campus). A edição RISC-V é a que recomendo, mesmo em inglês.

### Hennessy, John L.; Patterson, David A. & Kozyrakis, Christos. *Computer Architecture: A Quantitative Approach*
Morgan Kaufmann · **7ª edição, publicada em 24/10/2025** (ISBN 978-0-443-15406-5)

A bíblia da arquitetura de computadores, em atividade há quase 30 anos. A 7ª edição
acrescentou Christos Kozyrakis como autor e foi revisada com os desenvolvimentos recentes
em processadores e sistemas.

**Nível:** pós-graduação e profissional. **Não comece por aqui.**

---

## 4. Silício, transistores e VLSI

### Weste, Neil H. E. & Harris, David Money. *CMOS VLSI Design: A Circuits and Systems Perspective*
Pearson/Addison-Wesley · **4ª edição, 2010**

A referência sobre como portas viram silício: dimensionamento, atraso, potência, layout,
árvores de relógio, memórias.

**Nível:** avançado. **Envelheceu?** Nos nós de fabricação, sim (é anterior ao FinFET em
produção). **Nos princípios, não** — dimensionamento lógico, modelos de atraso e análise de
potência continuam válidos, e não há substituto de mesma qualidade.

### Rabaey, Jan M.; Chandrakasan, Anantha & Nikolić, Borivoje. *Digital Integrated Circuits: A Design Perspective*
Pearson · **2ª edição, 2003**

Mais focado em circuito e menos em sistema que o Weste & Harris. É o livro se você quiser
entender a **física** da porta.

**Nível:** avançado. **Envelheceu?** Na tecnologia, muito. Nos princípios elétricos, não.

### Sedra, Adel S. & Smith, Kenneth C. *Microelectronic Circuits*
Oxford University Press · **8ª edição, 2019**

Não é sobre lógica digital, e sim sobre eletrônica em geral. Entra aqui porque é onde se
aprende o que é um MOSFET de verdade, se o [`12`](12-do-transistor-a-porta.md) tiver
deixado você com vontade de mais.
**Em português:** há edição traduzida (*Microeletrônica*, Pearson).

---

## 5. Verilog, VHDL e verificação

| Livro | Comentário |
|---|---|
| **Chu, Pong P. — *FPGA Prototyping by SystemVerilog Examples*** (Wiley, 2018) | prático, orientado a projeto, com placas reais |
| **Harris & Harris** (§2) | os capítulos de HDL são suficientes para 90% das necessidades |
| **Meyer-Baese, Uwe — *Digital Signal Processing with FPGAs*** (Springer) | se o destino for processamento de sinais |
| **Spear, Chris — *SystemVerilog for Verification*** (Springer, 3ª ed. 2012) | referência de verificação com UVM; nível profissional |

**Opinião:** para aprender Verilog, livro é o meio menos eficiente. **HDLBits** (exercícios
com correção automática, ver [`85`](85-cursos-e-certificacoes.md)) ensina mais rápido, e o
livro serve como referência ao lado.

---

## 6. Teoria e complexidade

### Arora, Sanjeev & Barak, Boaz. *Computational Complexity: A Modern Approach*
Cambridge University Press · **2009** · 🆓 **rascunho disponível gratuitamente pelos
autores em https://theory.cs.princeton.edu/complexity/**

A referência moderna. Os capítulos sobre complexidade de circuitos cobrem AC⁰, NC, P/poly,
limites inferiores e a barreira das provas naturais — tudo o que está no
[`60`](60-teoria-avancada.md), em profundidade.

**Nível:** pós-graduação. Pré-requisito: matemática discreta e alguma maturidade em provas.

### Jukna, Stasys. *Boolean Function Complexity: Advances and Frontiers*
Springer · **2012**

O tratado especializado em complexidade de funções booleanas. Denso, completo, e o lugar
para onde ir se o [`60`](60-teoria-avancada.md) despertou interesse genuíno.
O autor manteve por muito tempo um rascunho acessível em sua página; verifique.

### Savage, John E. *Models of Computation: Exploring the Power of Computing*
Addison-Wesley, 1998 · 🆓 **o autor liberou o PDF em https://cs.brown.edu/people/jsavage/book/**

Trata circuitos como modelo de computação de primeira classe, e não como apêndice. Fonte
excelente para a relação entre circuitos e máquinas de Turing.

### Sipser, Michael. *Introduction to the Theory of Computation*
Cengage · **3ª edição, 2012**

Não é sobre circuitos, mas é o livro que ensina a pensar formalmente sobre computação.
Leitura de base antes do Arora & Barak.
**Em português:** *Introdução à Teoria da Computação* (Cengage). Tradução aceitável.

---

## 7. História

| Livro | Comentário |
|---|---|
| **Shannon, Claude. *A Symbolic Analysis of Relay and Switching Circuits*** (dissertação, MIT, 1937) 🆓 | **leia o original.** Tem ~70 páginas, é claríssimo, e está disponível no repositório do MIT. Poucos textos fundadores são tão legíveis. |
| **Boole, George. *An Investigation of the Laws of Thought*** (1854) 🆓 domínio público | de interesse histórico; a notação é datada e a leitura, difícil |
| **Isaacson, Walter. *Os Inovadores*** (Companhia das Letras, 2014, em português) | história ampla e bem escrita da computação; leve com a precisão técnica |
| **Riordan & Hoddeson. *Crystal Fire*** (1997) | a história do transistor no Bell Labs, com as pessoas envolvidas |
| **Berlin, Leslie. *The Man Behind the Microchip*** (2005) | biografia de Robert Noyce; explica a economia do circuito integrado |

---

## 8. O que está legalmente gratuito

| Obra | Onde |
|---|---|
| Nand2Tetris — projetos, ferramentas e capítulos iniciais | https://www.nand2tetris.org/ |
| Arora & Barak — rascunho completo | https://theory.cs.princeton.edu/complexity/ |
| Savage — *Models of Computation* | https://cs.brown.edu/people/jsavage/book/ |
| Dissertação de Shannon (1937) | repositório do MIT (DSpace) |
| Boole (1854) | Project Gutenberg, Archive.org |
| MIT OCW 6.004 — notas e slides | https://ocw.mit.edu/ |
| Especificações do RISC-V | https://riscv.org/technical/specifications/ |
| Documentação do Yosys, OpenROAD, Verilator | repositórios oficiais |

> **Sobre PDFs "gratuitos" de livros pagos** que aparecem em buscas: existem em quantidade,
> inclusive de todos os títulos desta página. Não são legais. Registro isso porque o preço
> de livros técnicos no Brasil é uma barreira real — e a saída honesta existe: **bibliotecas
> universitárias**, o programa **Minha Biblioteca** (adotado por muitas instituições),
> edições anteriores usadas na Estante Virtual (frequentemente por menos de R$ 50), e os
> títulos legalmente gratuitos listados acima. Este curso inteiro foi escrito de modo a não
> exigir a compra de nenhum livro.

---

## 9. O que **não** recomendo

Com fundamentação, e é opinião profissional:

| Categoria | Por quê |
|---|---|
| Apostilas de "eletrônica digital" sem autor identificado | frequentemente com erros e diagramas incorretos copiados entre si |
| Livros de eletrônica digital anteriores a ~1995 como texto principal | tratam de famílias lógicas extintas (RTL, DTL, ECL) como se fossem escolha atual |
| Livros que ensinam VHDL/Verilog **antes** dos fundamentos | produz gente que escreve código que sintetiza mal e não sabe por quê |
| "Domine VLSI em 30 dias" e similares | não existe |

---

## Autoteste

1. Qual livro você daria a alguém que nunca ouviu falar de computação?
2. Qual edição do Harris & Harris escolher em 2026, e por quê?
3. O que o Nand2Tetris **não** cobre?
4. Qual o clássico brasileiro do assunto, e qual sua limitação?
5. Qual livro ler para entender como uma porta vira silício?
6. Onde está, legalmente gratuito, o texto de referência em complexidade de circuitos?
7. Por que ler a dissertação de Shannon de 1937 em vez de um resumo dela?
8. Quais são as saídas honestas para quem não pode comprar livros técnicos?

*(Respostas: 1 — *Code*, do Petzold; 2 — a RISC-V Edition (2021), por ser a arquitetura
mais simples e mais promissora; 3 — eletrônica, transistor, timing e desempenho real;
4 — Idoeta & Capuano, cuja limitação é tratar de um mundo de CIs discretos; 5 — Weste &
Harris, *CMOS VLSI Design*; 6 — Arora & Barak, rascunho na página de Princeton; 7 — tem 70
páginas, é claríssima, e ver a ideia sendo formulada pela primeira vez ensina mais que o
resumo; 8 — bibliotecas universitárias, Minha Biblioteca, edições usadas, e os títulos
legalmente gratuitos.)*

---

### Verificações feitas na web (14/08/2026)

- Harris & Harris, *Digital Design and Computer Architecture, RISC-V Edition*, Morgan
  Kaufmann, ISBN 978-0-12-820064-3, publicada em 12/07/2021.
- Hennessy, Patterson & Kozyrakis, *Computer Architecture: A Quantitative Approach*,
  **7ª edição publicada em 24/10/2025**, ISBN 978-0-443-15406-5.
- Tocci, Widmer & Moss, *Sistemas Digitais: Princípios e Aplicações*, 12ª edição, Pearson
  Brasil, 2018, ISBN 978-85-430-2501-8.
- Idoeta & Capuano, *Elementos de Eletrônica Digital*, Érica, **42ª edição**, 687 páginas.
- Nisan & Schocken, *The Elements of Computing Systems*, MIT Press, 2ª edição, 2021.
- Petzold, *Code*, Microsoft Press, 2ª edição, 2022.
- Demais edições conferidas nas páginas das editoras; onde não houve confirmação, a edição
  foi omitida em vez de estimada.
