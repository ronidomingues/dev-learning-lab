# 50 · Quantas portas lógicas tem um computador — a resposta longa

**Nível:** avançado · **Data:** 14/08/2026
**Este é o arquivo que responde à pergunta que originou o curso.**

---

## 1. A pergunta precisa ser dividida em três

A pergunta *"quantas portas lógicas tem um computador?"* tem **três** respostas legítimas,
e a maior parte das discussões confusas sobre o tema é gente respondendo perguntas
diferentes achando que discorda.

| Pergunta | Resposta curta | Onde está a conta |
|---|---|---|
| **A. Quantos tipos de porta existem?** | **7 clássicos** (8 com o buffer); **16** funções possíveis de 2 entradas | §2 |
| **B. Quantas unidades de porta há num chip?** | Da ordem de **bilhões** num chip moderno; ~1.000 no primeiro microprocessador | §4–§6 |
| **C. Quantas portas são precisas para fazer X?** | Números exatos, medidos | §3 |

E há uma quarta, implícita e mais importante que as três: **para que elas servem** — §8.

---

## 2. Resposta A — quantos tipos

### 2.1 Os sete clássicos

NOT, AND, OR, NAND, NOR, XOR, XNOR. Alguns catálogos contam o **buffer** como oitavo.

Esse número é **convenção de engenharia**, não lei da natureza. As sete foram escolhidas
por serem úteis, baratas de fabricar e frequentes.

### 2.2 As dezesseis matemáticas

Com 2 entradas binárias, a tabela-verdade tem 4 linhas, e cada linha pode dar 0 ou 1:
**2⁴ = 16 funções possíveis**. As outras nove são constantes, cópias, negações simples e
implicações — existem, mas não valem um símbolo próprio ([`05`](05-manual-de-uso.md), §2).

### 2.3 A resposta que um projetista de chip daria

Numa **biblioteca de células padrão** real — o catálogo que a foundry entrega ao projetista —
há tipicamente de **300 a 1.500 células diferentes**. Não são 1.500 funções lógicas: são as
mesmas dezenas de funções em variantes de tamanho de acionamento (*drive strength*), de
limiar de tensão (rápida-e-vazadora, lenta-e-econômica) e de altura de célula.

Um catálogo típico inclui:

| Categoria | Exemplos | Quantidade típica |
|---|---|---|
| Portas simples | NAND2/3/4, NOR2/3/4, INV, BUF | dezenas de funções × 5–10 tamanhos |
| Portas compostas ("AOI/OAI") | AND-OR-Invert, OR-AND-Invert | dezenas |
| Aritméticas | meio somador, somador completo, majoritário | poucas |
| Sequenciais | flip-flop D com/sem reset, set, scan, latch | dezenas |
| Especiais | buffers de relógio, células de isolamento, células de preenchimento | dezenas |

As **AOI/OAI** merecem menção: `AOI21 = ¬((A·B) + C)` custa 6 transistores e faz o trabalho
de três portas separadas (12+ transistores). Elas existem porque em CMOS qualquer função
que caiba numa rede série-paralelo pode virar **uma única célula inversora**. Ferramentas de
síntese as adoram, e é por isso que a netlist real de um chip não se parece nada com o
diagrama que você desenharia à mão.

**Portanto:** "sete tipos" é a resposta didática, "dezesseis funções" é a resposta
matemática, e "algumas centenas de células" é a resposta industrial. As três estão certas.

---

## 3. Resposta C — quantas portas para fazer cada coisa

Números **medidos** pelo [projeto-modelo](07-projeto-modelo/README.md) (contando portas
NAND de 2 entradas):

| Função | Portas NAND | Observação |
|---|---|---|
| Inverter um bit | 1 | |
| E lógico | 2 | |
| OU lógico | 3 | |
| Comparar dois bits (XNOR) | 5 | |
| **Somar 1 bit com vai-um** | **9** | a peça central da aritmética |
| Escolher entre dois valores (mux 1 bit) | 4 | a peça mais repetida de uma CPU |
| Somar dois números de 4 bits | 36 | |
| Subtrair 4 bits | 40 | reusa o somador |
| Comparar dois números de 4 bits | 26 | |
| Detectar zero (a flag do `if`) | 10 | |
| Decodificar 4 bits em 16 linhas | 100 | cresce exponencialmente |
| ULA de 4 bits, 8 operações | 242 | ~60 por bit de largura |
| Lembrar 1 bit (latch SR) | 2 | |
| Flip-flop D | 9 | |
| Registrador de 4 bits | 52 | |
| Contador de 4 bits | 88 | |
| Memória de 4 palavras × 4 bits | 266 | **~66 portas por bit** |
| **Computador de 4 bits completo** | **829** | 13 instruções, executa programas |
| Deslocar por uma quantidade fixa | **0** | é só refiação |

Extrapolando para larguras reais (regra prática: aritmética escala linearmente,
decodificação escala exponencialmente no número de bits de endereço):

| Peça | 8 bits | 32 bits | 64 bits |
|---|---|---|---|
| Somador ripple | ~72 | ~290 | ~580 |
| Somador rápido (lookahead/prefixo) | ~150 | ~800 | ~2.000 |
| ULA básica | ~500 | ~2.000 | ~4.000 |
| Multiplicador | ~1.500 | ~25.000 | ~100.000 |
| Barrel shifter | ~200 | ~1.500 | ~4.000 |
| Banco de 32 registradores | — | ~20.000 | ~40.000 |

*(Ordens de grandeza. Implementações reais variam por um fator de 2 a 3 conforme a
prioridade dada a área, velocidade ou consumo.)*

---

## 4. Resposta B — a metodologia de contagem

Aqui está a parte que quase nenhum texto explica, e que é a diferença entre um número
honesto e um número inventado.

### 4.1 O que a indústria realmente conta: *gate equivalent* (GE)

Como as portas de um chip têm tamanhos diferentes, a indústria não conta portas — conta
**equivalentes de porta**:

> **1 GE = a área de uma porta NAND de 2 entradas com acionamento mínimo, na tecnologia em
> questão.**

É uma medida de **área normalizada**, não de contagem física. Um flip-flop D vale ~5–8 GE;
um somador completo, ~5–7 GE; uma célula AOI21, ~1,5 GE.

Consequências que precisam ficar claras:

1. **GE depende da tecnologia.** "500k GE" significa coisas fisicamente diferentes em
   180 nm e em 3 nm.
2. **GE não é contagem de portas.** É "quanto silício isto ocupa, medido em NANDs".
3. É o número que aparece nas fichas técnicas de IP: *"núcleo Cortex-M0: ~12k portas"*.

### 4.2 A conversão transistor → porta, e por que ela engana

A tentação é dividir a contagem de transistores por 4 (o custo de um NAND2). Isso está
errado, por três motivos independentes, e cada um deles vale um fator:

**Erro 1 — nem todo transistor é lógica.**
Uma célula SRAM tem 6 transistores e **não computa nada**. Ela armazena. Contá-la como
1,5 porta é categoricamente errado, do mesmo modo que contar prateleiras como funcionários.

**Erro 2 — a média de transistores por porta não é 4.**
NAND2 tem 4, mas um projeto real é uma mistura: inversores (2), buffers (4–8), AOI (6),
flip-flops (20–26), portas de acionamento reforçado (2× a 8× o tamanho). A média fica na
faixa de **6 a 10 transistores por célula**, não 4.

**Erro 3 — há transistores que não são nem lógica nem memória.**
Blocos analógicos (PLLs, PHYs de memória e de USB/PCIe, reguladores de tensão, sensores
térmicos), células de preenchimento (*fill cells*, que existem só para uniformizar a
densidade da fabricação), redundância de fabricação, e a rede de alimentação.

**Conclusão metodológica:** transistores → portas exige três correções, todas estimadas.
Por isso qualquer resposta a "quantas portas tem este chip" que não venha do relatório de
síntese do projetista é, necessariamente, uma **estimativa com barra de erro larga**.

Quem afirma "o M4 tem exatamente N portas" está inventando. Eu não vou fazer isso; vou
mostrar a conta e as suposições.

---

## 5. A régua histórica — transistores (números publicados)

Estes números **são publicados** e verificáveis. Fonte: Wikipedia, *Transistor count*,
consultada em 14/08/2026 (a página compila anúncios dos fabricantes e análises de terceiros).

| Chip | Ano | Transistores | Nó |
|---|---|---|---|
| Intel 4004 | 1971 | **2.250** | 10.000 nm |
| Intel 8086 | 1978 | 29.000 | 3.000 nm |
| Intel 80386 | 1985 | 275.000 | 1.500 nm |
| Intel Pentium | 1993 | 3.100.000 | 800 nm |
| Apple M1 | 2020 | 16.000.000.000 | 5 nm |
| Apple M2 | 2022 | 20.000.000.000 | 5 nm |
| Apple M3 | 2023 | 25.000.000.000 | 3 nm |
| **Apple M4** | 2024 | **28.000.000.000** | 3 nm |
| Apple M5 | 2025 | ~28.000.000.000 | 3 nm (N3E) |
| Nvidia Vera (CPU) | 2026 | 227.000.000.000 | — |
| **Nvidia Rubin** (GPU) | 2026 | **336.000.000.000** | N3P customizado |
| Micron V-NAND 2 TB (flash) | 2023 | 5.300.000.000.000 | — |

A última linha é uma memória flash: **5,3 trilhões de transistores**, e **nenhum deles é
porta lógica**. É a ilustração mais extrema do erro nº 1.

**A escala do salto:** do 4004 ao Rubin são 55 anos e um fator de **150 milhões**.

---

## 6. A conta, feita às claras

Vamos estimar as portas de um SoC de notebook com **28 bilhões de transistores**
(a escala do Apple M4/M5). Cada suposição está declarada, e você pode discordar de
qualquer uma e refazer a conta.

### Passo 1 — Descontar a memória embarcada

Quanto de SRAM tem um SoC assim? Somando caches L1/L2, cache de sistema, registradores da
GPU e buffers da NPU, uma faixa razoável para essa classe de produto é **40 a 120 MB**.

Aritmética da SRAM:
```
1 MB = 8 × 2²⁰ bits = 8.388.608 bits
Célula 6T: 8.388.608 × 6 ≈ 50,3 milhões de transistores por MB
+ periferia (decodificadores, sense amplifiers, drivers): +25 a 40%
≈ 65 milhões de transistores por MB, na prática
```

| Se o chip tiver… | Transistores em memória | % de 28 bi |
|---|---|---|
| 40 MB | ~2,6 bilhões | 9% |
| 80 MB | ~5,2 bilhões | 19% |
| 120 MB | ~7,8 bilhões | 28% |

Tomemos o caso do meio: **~5 bilhões em SRAM (≈19%)**.

### Passo 2 — Descontar o que não é lógica digital

| Categoria | Estimativa | Justificativa |
|---|---|---|
| Blocos analógicos e mistos (PLLs, PHYs, reguladores) | ~5% | PHYs de DRAM e de E/S de alta velocidade são grandes |
| Células de preenchimento, redundância, rede de energia | ~5% | exigência do processo de fabricação |

**≈ 10%, ou ~2,8 bilhões de transistores.**

### Passo 3 — O que sobra é lógica

```
28,0 bi  (total)
− 5,0 bi (SRAM)
− 2,8 bi (analógico, fill, redundância)
──────────
≈ 20,2 bilhões de transistores em lógica digital
```

### Passo 4 — Converter para portas

Aqui a suposição mais delicada: **quantos transistores, em média, por porta?**

| Suposição | Transistores/porta | Portas resultantes |
|---|---|---|
| Otimista (quase tudo NAND2 mínimo) | 4 | **~5,0 bilhões** |
| Realista (mistura típica com flip-flops e buffers) | **6** | **~3,4 bilhões** |
| Conservadora (muitos flip-flops, muito buffer de relógio) | 8 | **~2,5 bilhões** |

### Resultado, com a barra de erro que ele merece

> **Um SoC de notebook de 2026, com 28 bilhões de transistores, tem da ordem de
> 2,5 a 5 bilhões de portas lógicas — sendo ~3,4 bilhões a estimativa central.**
>
> Cerca de **20% dos transistores** estão em memória, que não é porta nenhuma, e
> outros **10%** não são lógica digital.

Refazendo para a régua histórica, com a mesma metodologia (6 transistores por porta, e
descontando memória quando relevante):

| Chip | Transistores | Portas (estimativa) |
|---|---|---|
| Intel 4004 | 2.250 | **~500 a 800** (PMOS, não CMOS — a razão transistor/porta era diferente) |
| Intel 8086 | 29.000 | ~5.000 a 9.000 |
| Intel 80386 | 275.000 | ~50.000 |
| Pentium | 3,1 milhões | ~500.000 (já com ~30% em cache) |
| Apple M4 | 28 bilhões | **~2,5 a 5 bilhões** |
| Nvidia Rubin | 336 bilhões | **~20 a 60 bilhões** (GPUs têm proporção de memória ainda maior) |

**E o [projeto-modelo](07-projeto-modelo/README.md) deste curso: 829 portas.** Um M4 tem
cerca de **quatro milhões de vezes** mais.

---

## 7. Uma perspectiva que ajuda a sentir o número

- Se cada porta lógica do seu notebook fosse **um grão de arroz** (≈0,02 g), você teria
  ~3,4 bilhões de grãos: cerca de **68 toneladas** — dois caminhões-baú cheios.
- Se cada porta fosse **uma pessoa**, seriam ~3,4 bilhões: quase metade da humanidade,
  dentro de um quadrado de silício menor que uma unha.
- Se você contasse as portas **uma por segundo**, sem dormir, levaria **108 anos**.
- Se cada porta fosse **um metro quadrado**, cobririam 3.400 km² — mais que a área do
  Distrito Federal.

E todas comutam em ~5 picossegundos, consumindo, juntas, menos que uma lâmpada.

---

## 8. Para que elas servem — a taxonomia funcional

Esta é a metade da pergunta que os números não respondem. Toda porta de um computador está
fazendo **uma destas seis coisas**:

### 8.1 Decidir (lógica de controle)

AND, OR, NOT combinando condições. Todo `if`, `while` e `&&` do seu código termina, no
fundo, em portas físicas avaliando condições.

**Onde:** unidade de controle, lógica de habilitação, verificação de permissões e exceções.
**Quanto:** ~10% das portas de um núcleo.

### 8.2 Calcular (aritmética e lógica)

XOR e AND formam somadores; somadores formam multiplicadores; tudo isso vira a ULA.

**Onde:** ULA, unidade de ponto flutuante, unidades vetoriais.
**Quanto:** ~20% de um núcleo simples; mais em aceleradores.

### 8.3 Escolher (multiplexação)

Cada bifurcação do caminho de dados é um mux. "Qual registrador ler", "de onde vem este
operando", "qual resultado gravar", "qual o próximo endereço".

**Onde:** por todo o caminho de dados, e nas redes de bypass do pipeline.
**Quanto:** ~10–15%, e é a peça individualmente mais repetida.

### 8.4 Endereçar (decodificação)

Transformar um número num "acione exatamente esta linha". É como a memória encontra um byte
entre bilhões e como o processador identifica qual instrução executar.

**Onde:** decodificadores de memória, decodificação de instruções, seleção de dispositivos.
**Quanto:** ~10%.

### 8.5 Lembrar (memória)

Portas realimentadas: latch, flip-flop, registrador. E, na forma otimizada (que já não é
porta), a célula SRAM.

**Onde:** registradores, buffers de pipeline, filas, caches.
**Quanto:** ~40% das portas de um núcleo — e a maior parte da **área** de um chip inteiro.

### 8.6 Vigiar (comparação e verificação)

XOR comparando, paridade detectando erro, comparadores testando igualdade, CRCs protegendo
transmissões.

**Onde:** ECC de memória, CRC de barramentos, comparadores de tag de cache (a cada acesso
ao cache, dezenas de comparadores rodam em paralelo), *watchdogs*.
**Quanto:** ~5–10%, e cresce com a exigência de confiabilidade.

### 8.7 O resumo em uma frase

> **Uma porta decide uma coisa trivial. Bilhões delas, ligadas na ordem certa e
> sincronizadas por um relógio, formam uma máquina que busca uma instrução, decide o que
> fazer, faz, guarda o resultado e repete — bilhões de vezes por segundo. Não há nada
> além disso dentro de um computador.**

---

## 9. Perguntas relacionadas que aparecem sempre

**"Quantas portas tem um smartphone?"**
Somando SoC principal, modem, controlador de energia, controlador de tela, sensores e o
controlador do armazenamento: da ordem de **5 a 10 bilhões** de portas equivalentes.

**"Quantas portas tem a internet inteira?"**
Impossível responder com honestidade. Como referência de ordem de grandeza: se houver
~30 bilhões de dispositivos computacionais no mundo, com média de 10⁷ a 10⁹ portas cada,
chega-se a algo entre 10¹⁷ e 10¹⁹ portas. Trate como um exercício de imaginação, não como
um dado.

**"Meu processador tem 8 núcleos. As portas se dividem por 8?"**
Não. Cada núcleo tem seu conjunto completo, mas cache L3, controlador de memória,
interconexão e blocos de E/S são compartilhados — e frequentemente somam mais que os
núcleos juntos.

**"Quantas portas por segundo um computador aciona?"**
Se ~10% das portas comutam por ciclo (uma taxa de atividade plausível) e o chip roda a
4 GHz: `0,1 × 3,4×10⁹ × 4×10⁹ ≈ 1,4 × 10¹⁸` comutações por segundo. Mais de um
**quintilhão** de decisões binárias a cada segundo, na sua mesa.

**"E os computadores quânticos?"**
Portas quânticas são outra coisa: operam sobre amplitudes complexas, são reversíveis, e
não têm tabela-verdade. Um processador quântico de 2026 tem da ordem de **centenas a
poucos milhares de qubits** e um número modesto de portas por circuito — não são
comparáveis, e nem competem no mesmo terreno.
Ver [`65-estado-da-arte.md`](65-estado-da-arte.md).

---

## 10. Resumo executivo

| Pergunta | Resposta |
|---|---|
| Quantos **tipos** de porta? | **7** clássicos (8 com buffer); **16** funções de 2 entradas possíveis; **centenas de células** numa biblioteca industrial |
| Quantas **unidades** num notebook de 2026? | **~2,5 a 5 bilhões** de portas equivalentes (28 bi de transistores) |
| Quantas no primeiro microprocessador (1971)? | **~500 a 800** (2.250 transistores) |
| Quantas no computador do projeto-modelo? | **829**, medidas |
| Por que não é transistores ÷ 4? | ~20% dos transistores são memória, ~10% não são lógica digital, e a média é ~6 transistores por porta — não 4 |
| **Para que servem?** | decidir · calcular · escolher · endereçar · lembrar · vigiar |

---

## Autoteste

1. Por que a pergunta do título tem três respostas legítimas?
2. O que é um *gate equivalent*, e por que a indústria conta assim?
3. Cite os três erros de dividir transistores por 4.
4. Quantos transistores tem 1 MB de SRAM? Mostre a conta.
5. Refaça a estimativa do §6 supondo 120 MB de cache e 8 transistores por porta. Qual o resultado?
6. Por que a contagem de portas de um chip comercial não é publicada?
7. Quantas portas custa lembrar 1 bit com flip-flops? E com uma célula SRAM? Qual a consequência arquitetural?
8. Quais são os seis trabalhos que as portas fazem, e qual deles consome mais delas?
9. Um chip de flash tem 5,3 trilhões de transistores. Quantas portas lógicas ele tem?
10. Por que portas quânticas não entram nessa contagem?

*(Respostas: 1 — tipos, unidades e "quantas para fazer X"; 2 — a área de um NAND2, porque
portas têm tamanhos diferentes e o que importa é área normalizada; 3 — memória não é porta,
a média não é 4 transistores por porta, e há transistores analógicos/fill/redundância;
4 — 8×2²⁰×6 ≈ 50,3 milhões, ~65 milhões com periferia; 5 — 28 − 7,8 − 2,8 ≈ 17,4 bi de
lógica ÷ 8 ≈ 2,2 bilhões de portas; 6 — é informação interna do relatório de síntese, muda a
cada compilação e depende da biblioteca; 7 — ~66 portas por bit com flip-flops contra ~1,5
com SRAM, o que gera a hierarquia de memória; 8 — decidir, calcular, escolher, endereçar,
lembrar e vigiar; lembrar consome mais; 9 — praticamente nenhuma: são células de
armazenamento, não portas; 10 — porque são reversíveis, operam sobre amplitudes complexas
e não têm tabela-verdade.)*

---

### Fontes consultadas (14/08/2026)

- Wikipedia, *Transistor count* — https://en.wikipedia.org/wiki/Transistor_count — contagens
  de Intel 4004 (2.250), 8086 (29.000), 80386 (275.000), Pentium (3,1 M), Apple M1–M4
  (16/20/25/28 bilhões), Nvidia Rubin (336 bilhões, 2026), Nvidia Vera (227 bilhões, 2026),
  Micron V-NAND 2 TB (5,3 trilhões).
- Contagens de portas do [projeto-modelo](07-projeto-modelo/README.md): **medidas** pela
  execução de `contagem.py` em 14/08/2026.
- As estimativas de composição de SoC (fração de SRAM, analógico e preenchimento) são
  **minhas**, com as suposições declaradas no §6. Não são dados de fabricante — nenhum
  fabricante publica essa decomposição.
