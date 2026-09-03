# 85 · Cursos gratuitos e certificações

**Nível:** todos
**Data da pesquisa na web: 14/08/2026**
**Links podem expirar.** O ano de publicação de cada curso está indicado quando conhecido.

---

## Antes da lista: a recomendação, em três linhas

1. **Se você tem 2 horas:** https://nandgame.com/ — construa um computador do zero, jogando.
2. **Se você tem 3 meses:** **Nand2Tetris**, na Coursera (auditoria gratuita) ou no site
   oficial. É o melhor material do mundo neste assunto, sem concorrente próximo.
3. **Se você quer em português:** as aulas de **Sistemas Digitais / Circuitos Lógicos** da
   USP (e-Aulas) e da UNIVESP, gratuitas e completas.

O resto deste arquivo detalha, compara e é franco sobre o que não vale o tempo.

---

## 1. Português (Brasil e Portugal)

### 1.1 e-Aulas da USP — Sistemas Digitais I (PCS3115)

| | |
|---|---|
| **Instituição** | Escola Politécnica da USP |
| **Plataforma** | e-Aulas USP — https://eaulas.usp.br/ |
| **Formato** | vídeos de aulas presenciais, gratuitos, sem cadastro |
| **Nível** | universitário (1º ou 2º ano de engenharia) |
| **Certificado** | não |
| **Vale o tempo?** | **Sim, se você quer profundidade.** É aula universitária de verdade, no ritmo de uma disciplina real, com o rigor que isso implica. Não é "curso rápido de YouTube". |
| **Cuidado** | ritmo de sala de aula, com pausas e interações; exige disciplina para acompanhar |

Busque por "Sistemas Digitais" no portal. Há também material de Circuitos Digitais em outras
unidades da USP.

### 1.2 UNIVESP — Circuitos Lógicos / Circuitos Digitais

| | |
|---|---|
| **Instituição** | Universidade Virtual do Estado de São Paulo |
| **Plataforma** | YouTube (canal oficial da UNIVESP) |
| **Formato** | disciplina completa do curso de Engenharia de Computação, em vídeos |
| **Conteúdo** | conceitos de circuitos digitais, famílias CMOS/NMOS/BiCMOS e TTL, lógica sequencial, memórias, temporização, conversores DAC/ADC, dispositivos lógicos programáveis |
| **Certificado** | **não** — o material é aberto, mas sem emissão de certificado |
| **Vale o tempo?** | **Sim.** É a alternativa em português mais próxima de uma disciplina formal completa, com estrutura de bimestres e exercícios. |

Busque "UNIVESP Circuitos Lógicos" ou "UNIVESP Circuitos Digitais" no YouTube — as playlists
são organizadas por semana/bimestre.

### 1.3 Bóson Treinamentos — Eletrônica Digital

| | |
|---|---|
| **Autor** | Fábio dos Reis |
| **Plataforma** | YouTube — https://www.youtube.com/@bosontreinamentos |
| **Formato** | série de vídeos curtos |
| **Nível** | iniciante |
| **Certificado** | não |
| **Vale o tempo?** | **Sim, para começar.** Didática clara e direta, em português brasileiro, para quem quer entender portas, álgebra booleana e Karnaugh sem o formalismo universitário. Não substitui um curso completo, mas é uma excelente porta de entrada. |

### 1.4 Cursou / Cursa / Learncafe — cursos "com certificado gratuito"

| | |
|---|---|
| **Plataformas** | cursou.com.br, cursa.app, learncafe.com |
| **Conteúdo** | sistemas de numeração, álgebra booleana, portas, Karnaugh, flip-flops, contadores |
| **Certificado** | varia: alguns emitem certificado digital gratuito, outros cobram pela emissão |
| **Vale o tempo?** | **Parcialmente.** O conteúdo é raso e frequentemente é reempacotamento de material de terceiros. Servem para revisão ou para quem precisa de um comprovante de horas complementares. **Não** servem como formação. |

> **Franqueza sobre certificados dessas plataformas:** eles não têm valor de mercado. Nenhum
> recrutador de hardware vai valorizá-los. Servem, no máximo, para computar horas
> complementares em faculdade — o que é um uso legítimo, desde que você saiba que é isso.

### 1.5 Documentação e material aberto em português

| Recurso | O que é |
|---|---|
| Apostilas de Sistemas Digitais de universidades federais (UFRJ, UFMG, UFSC, UFRGS) | PDFs abertos, geralmente encontráveis buscando "sistemas digitais apostila site:.br" |
| Material do CEDERJ (Sala de Estudos / CompCEDERJ) | conteúdo aberto de disciplinas de computação |
| Wikipédia em português — "Porta lógica", "Álgebra booliana" | bom ponto de partida; verifique contra fonte primária |

**Lacuna honesta do português:** não existe, até onde pesquisei em 14/08/2026, um curso em
português com a qualidade e a completude do Nand2Tetris. Se você lê inglês razoavelmente,
o ganho de fazer o material em inglês é grande neste assunto específico.

---

## 2. Inglês

### 2.1 Nand2Tetris — *Build a Modern Computer from First Principles* ⭐

| | |
|---|---|
| **Instituição** | Universidade Hebraica de Jerusalém (Noam Nisan e Shimon Schocken) |
| **Plataforma** | Coursera (2 partes) + site oficial https://www.nand2tetris.org/ |
| **Custo** | **auditoria gratuita** na Coursera; todo o material e o software são gratuitos no site oficial |
| **Duração** | 6 módulos; ~2–3 h de vídeo por módulo e 5–10 h por projeto; ~6 semanas no ritmo sugerido, mas é autoinstrucional |
| **Pré-requisito** | **nenhum** — é autocontido, e não pressupõe computação nem engenharia |
| **Hardware necessário** | **nenhum** — o simulador é fornecido |
| **Certificado** | pago na Coursera; o conhecimento e os projetos, gratuitos |
| **Vale o tempo?** | **É o melhor material existente sobre este assunto, em qualquer idioma.** Você constrói, na ordem: portas a partir de NAND → ULA → memória → CPU → montador → máquina virtual → compilador → sistema operacional. Ao final você entende a pilha inteira. |
| **Cuidado** | a Parte I (hardware) é o que interessa a este curso; a Parte II é software. Faça a I primeiro. |

**Comparação com este curso:** o Nand2Tetris vai **mais longe para cima** (chega ao
compilador e ao SO). Este material vai **mais fundo para baixo** (transistor, CMOS, timing,
complexidade de circuitos, contagem real de portas em chips comerciais). São complementares,
e recomendo fazer os dois.

### 2.2 MIT 6.004 — *Computation Structures*

| | |
|---|---|
| **Instituição** | MIT |
| **Plataforma** | MIT OpenCourseWare — https://ocw.mit.edu/ |
| **Custo** | gratuito |
| **Nível** | universitário, exigente |
| **Conteúdo** | de MOSFETs e portas CMOS até um processador RISC-V com pipeline |
| **Certificado** | não |
| **Vale o tempo?** | **Sim, se você quer o nível de engenharia.** É a disciplina que cobre exatamente a trajetória deste curso, com o rigor do MIT. Laboratórios em Minispec/BSV. |

### 2.3 Berkeley CS61C — *Great Ideas in Computer Architecture*

Gratuito, com vídeos e material aberto. Foco em arquitetura RISC-V e na ponte entre C e
hardware. Menos ênfase em portas, mais em arquitetura — bom **depois** do
[`40`](40-da-porta-ao-computador.md).

### 2.4 Ben Eater — *Build an 8-bit computer from scratch* ⭐

| | |
|---|---|
| **Plataforma** | YouTube — canal Ben Eater; site https://eater.net/8bit |
| **Custo** | vídeos **gratuitos**; os kits de hardware são pagos (opcionais) |
| **Formato** | ~44 vídeos construindo um computador de 8 bits em protoboard, com CIs 74LS |
| **Vale o tempo?** | **Absolutamente.** É a melhor série de vídeos de eletrônica digital já feita, na minha opinião. Ele constrói tudo à mão, explicando cada decisão, e mostra os problemas reais (repique, ruído, fiação) que simuladores escondem. |
| **Cuidado** | usa família 74LS, hoje legado; use 74HC se for reproduzir |

Se você tiver que escolher **um só** recurso em vídeo neste assunto, escolha este.

### 2.5 Outros recursos em inglês que valem

| Recurso | O que é | Custo |
|---|---|---|
| **nandgame.com** | jogo de construir um computador de um relé até a CPU | gratuito |
| **Digital Design and Computer Architecture** (Harris & Harris) — vídeos de apoio | acompanha o livro; ver [`90`](90-bibliografia.md) | vídeos gratuitos |
| **Zero to ASIC Course** (Matt Venn) | do RTL ao chip fabricado, com Tiny Tapeout | material pago; muito conteúdo gratuito no canal |
| **CMU 18-447 / ETH Zurich (Onur Mutlu)** | arquitetura de computadores, aulas gravadas | gratuito no YouTube |
| **FPGA4Fun, Nandland (Russell Merrick)** | tutoriais práticos de Verilog/VHDL e FPGA | gratuito |
| **Chipdev.io** | exercícios de Verilog no navegador | gratuito |
| **HDLBits** | **exercícios de Verilog com correção automática** | gratuito |

**HDLBits merece destaque:** é o "LeetCode do Verilog". Centenas de exercícios com
verificação automática, do inversor à máquina de estados. É a forma mais eficiente de
adquirir fluência em HDL que eu conheço.

---

## 3. Francês

### 3.1 OpenClassrooms — *Faites vos premiers pas dans le monde de l'électronique numérique*

| | |
|---|---|
| **Plataforma** | OpenClassrooms (projeto OpenINSA) |
| **Conteúdo** | sistemas de numeração incluindo binário, funções lógicas elementares e sua implementação física com transistores, até a síntese de funções lógicas combinatórias |
| **Custo** | **acesso gratuito ao conteúdo**; os percursos diplomantes é que são pagos |
| **Nível** | iniciante |
| **Vale o tempo?** | **Sim, para francófonos.** Cobre exatamente a trajetória do [`10`](10-fundamentos.md) ao [`20`](20-circuitos-combinacionais.md), com a didática clara que caracteriza a plataforma. |

Há também o módulo complementar *"Concevez vos premiers circuits combinatoires"*, do mesmo
projeto OpenINSA.

### 3.2 FUN-MOOC — France Université Numérique

| | |
|---|---|
| **Plataforma** | https://www.fun-mooc.fr/ |
| **O que é** | a plataforma de referência para cursos gratuitos de universidades francesas (Sorbonne, Polytechnique, Sciences Po, entre outras) |
| **Custo** | cursos gratuitos; certificado verificado às vezes pago |
| **Sobre eletrônica digital** | a oferta **varia por temporada**. Busque por "électronique numérique", "logique combinatoire" e "architecture des ordinateurs" no catálogo. A temporada 2025–2026 programou 55 sessões de formação profissional. |
| **Vale o tempo?** | **Sim**, mas confira o calendário: muitos cursos do FUN abrem em sessões datadas, não em fluxo contínuo. |

### 3.3 Recursos francófonos abertos

| Recurso | O que é |
|---|---|
| **elektronique.fr** — cours sur les portes logiques | curso aberto sobre portas lógicas, com vídeos |
| Vídeos "Électronique numérique : les portes logiques" no YouTube | séries de professores francófonos, gratuitas |
| Polycopiés de universidades francesas (Sorbonne, INSA, IUT) | PDFs abertos de excelente qualidade; busque "polycopié électronique numérique filetype:pdf" |
| **clicours.com** | compilação de cursos abertos, incluindo álgebra de Boole e operadores lógicos |

---

## 4. Certificações

### 4.1 A verdade franca sobre certificação neste assunto

> **Não existe certificação reconhecida de mercado especificamente em "portas lógicas" ou
> "eletrônica digital".** Isso não é uma lacuna do mercado — é reflexo de como a área
> contrata: **por portfólio e por entrevista técnica**, não por certificado.

Um projeto seu num repositório público — um processador em Verilog, um chip no Tiny Tapeout,
uma FPGA fazendo algo real — vale infinitamente mais que qualquer certificado que exista.

### 4.2 Certificações relacionadas, e o que valem de fato

| Certificação | Emissor | Custo | Vale? |
|---|---|---|---|
| **Coursera / Nand2Tetris** | Universidade Hebraica | pago (o conteúdo é gratuito) | **valor simbólico**; o que vale é ter feito os projetos |
| **AMD/Xilinx Certified** (FPGA) | AMD | pago; treinamento caro | **algum valor** em empresas do ecossistema Xilinx |
| **Intel FPGA Technical Training** | Intel/Altera | alguns módulos gratuitos | **algum valor**, mesmo escopo |
| **Certificações de VLSI de institutos privados** (comuns na Índia) | vários | pago | **valor baixo fora do contexto local**; qualidade muito variável |
| **Diploma técnico em Eletrônica** (SENAI, ETEC, IFs) | instituições públicas e paraestatais | gratuito ou baixo custo em instituições públicas | **valor real**, especialmente no Brasil, para vagas técnicas |
| Certificados de plataformas de "cursos livres" | vários | grátis ou baixo | **valor nulo** no mercado técnico; servem para horas complementares |

### 4.3 Certificadores gratuitos que existem de verdade

| Emissor | O que oferece | Realmente gratuito? |
|---|---|---|
| **UNIVESP** | disciplina completa, aberta | conteúdo sim; **sem certificado** |
| **e-Aulas USP** | aulas universitárias | sim; sem certificado |
| **Cursa / Learncafe / Cursou** | certificado digital de curso livre | alguns sim; **valor de mercado nulo** |
| **FUN-MOOC** | atestado de acompanhamento em alguns cursos | frequentemente sim; certificado verificado às vezes pago |
| **Coursera (modo audit)** | acesso ao conteúdo | conteúdo sim; certificado pago |
| **Fundação Bradesco (Escola Virtual)** | cursos de informática com certificado | **sim, gratuito de verdade**, mas a oferta em eletrônica digital é limitada |

### 4.4 O que fazer no lugar de colecionar certificados

Em ordem de retorno sobre o tempo investido:

1. **Um repositório público** com um processador simples em Verilog, com testbench que passa.
2. **Um chip fabricado** pelo Tiny Tapeout (€ 70). É um diferencial que quase ninguém tem,
   e é uma história que se conta em entrevista.
3. **Contribuições** a projetos abertos: Yosys, OpenROAD, um núcleo RISC-V, o próprio
   Logisim-evolution.
4. **HDLBits completo.** Não emite certificado, mas produz fluência — que é o que a
   entrevista técnica mede.
5. **Um artigo ou uma série de posts** explicando algo que você construiu. Ensinar é a
   prova mais convincente de que se entendeu.

---

## 5. Roteiro sugerido, combinando tudo

| Fase | Duração | O que fazer |
|---|---|---|
| **Semana 1** | 5 h | nandgame.com inteiro + [`01`](01-introducao-leigo.md) e [`10`](10-fundamentos.md) deste curso |
| **Semanas 2–4** | 15 h | Nand2Tetris Parte I (projetos 1–5) + labs 1–7 do [`70`](70-pratica.md) |
| **Semanas 5–8** | 20 h | Ben Eater (série de 8 bits, assistindo) + [`20`](20-circuitos-combinacionais.md) e [`30`](30-circuitos-sequenciais.md) + labs 8–9 |
| **Semanas 9–12** | 25 h | HDLBits + labs 10–12 + [`40`](40-da-porta-ao-computador.md) |
| **Depois** | — | MIT 6.004 ou Berkeley CS61C; ou uma FPGA; ou Tiny Tapeout |

Ao final desse roteiro, você tem mais base prática que a maioria dos formandos em
engenharia da computação — o que não é elogio ao roteiro, e sim uma crítica ao quanto
dessas disciplinas costuma ficar só no papel.

---

## Autoteste

1. Qual é o melhor material do mundo neste assunto, e por quê?
2. O que este curso cobre que o Nand2Tetris não cobre, e vice-versa?
3. Existe certificação de mercado em portas lógicas? O que vale no lugar?
4. Qual é a melhor série de vídeos para quem quer ver hardware físico funcionando?
5. Qual recurso usar para adquirir fluência em Verilog?
6. Que curso em francês cobre exatamente do binário à síntese combinatória?
7. Qual a lacuna honesta do material em português?
8. O que fazer com € 70 que vale mais que qualquer certificado?

*(Respostas: 1 — Nand2Tetris, porque é autocontido, gratuito, e leva de NAND ao sistema
operacional; 2 — este vai mais fundo em transistor, timing, contagem real e teoria de
circuitos; o Nand2Tetris vai mais alto, até compilador e SO; 3 — não existe; vale portfólio,
projeto público e chip fabricado; 4 — a série de 8 bits do Ben Eater; 5 — HDLBits;
6 — o da OpenClassrooms/OpenINSA, *Faites vos premiers pas dans le monde de l'électronique
numérique*; 7 — não há equivalente ao Nand2Tetris em português; 8 — fabricar seu próprio
chip pelo Tiny Tapeout.)*

---

### Fontes consultadas na web (14/08/2026)

- Nand2Tetris: https://www.coursera.org/learn/build-a-computer (inscrição gratuita/audit;
  6 módulos; ~2–3 h de vídeo e 5–10 h de projeto por módulo; sem pré-requisitos; simulador
  fornecido) e https://www.nand2tetris.org/
- e-Aulas da USP: https://eaulas.usp.br/ — disciplina PCS3115 Sistemas Digitais I.
- UNIVESP: canal oficial no YouTube; disciplina de Circuitos Lógicos/Digitais do curso de
  Engenharia de Computação, aberta e **sem** emissão de certificado.
- Bóson Treinamentos (Fábio dos Reis): https://www.youtube.com/@bosontreinamentos
- Plataformas de curso livre em PT verificadas: cursou.com.br, cursa.app, learncafe.com.
- OpenClassrooms / OpenINSA: *Faites vos premiers pas dans le monde de l'électronique
  numérique* e *Concevez vos premiers circuits combinatoires* — via my-mooc.com e
  project-tic.fr/openinsa (consultados em 14/08/2026).
- FUN-MOOC: https://www.fun-mooc.fr/ — plataforma de universidades francesas; temporada
  2025–2026 com 55 sessões programadas.
- elektronique.fr — *Cours sur les Portes Logiques*.
- Ben Eater: https://eater.net/8bit · MIT OCW 6.004 · HDLBits · nandgame.com.
