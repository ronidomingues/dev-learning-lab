# 05 · Manual de uso — referência consultável

**Nível:** referência · **Data:** 14/08/2026

Organizado **por tarefa**, não por ordem alfabética. Use o índice abaixo e volte aqui
sempre que precisar de um símbolo, uma identidade, um número de CI ou um operador.

| Preciso de… | Seção |
|---|---|
| símbolo e tabela de uma porta | [§1](#1-as-portas--tabela-de-referência) |
| todas as funções possíveis de 2 entradas | [§2](#2-as-16-funções-de-duas-variáveis) |
| identidades para simplificar expressão | [§3](#3-álgebra-booleana--identidades) |
| como se lê a notação (∧, ·, +, ⊕, ¬, ') | [§4](#4-notação--como-se-lê) |
| número do chip TTL/CMOS para montar na bancada | [§5](#5-série-7400--o-catálogo-clássico) |
| operadores de Verilog e VHDL | [§6](#6-verilog-e-vhdl--operadores) |
| atalhos do Logisim | [§7](#7-logisim-evolution--atalhos-e-truques) |
| blocos prontos (mux, decodificador, somador) | [§8](#8-blocos-combinacionais-de-catálogo) |
| flip-flops e suas tabelas | [§9](#9-flip-flops--tabela-de-referência) |
| o que está obsoleto | [§10](#10-obsoleto--e-o-que-usar-no-lugar) |

---

## 1. As portas — tabela de referência

| Porta | Expressão | Símbolo ASCII | Tabela (00,01,10,11) | Custo em NAND | Custo em transistores CMOS |
|---|---|---|---|---|---|
| **NOT** | ¬A | `─▷o─` | 1,0 (1 entrada) | 1 | 2 |
| **BUFFER** | A | `─▷─` | 0,1 (1 entrada) | 2 | 4 |
| **AND** | A·B | `─D─` | 0,0,0,1 | 2 | 6 |
| **OR** | A+B | `─)─` | 0,1,1,1 | 3 | 6 |
| **NAND** | ¬(A·B) | `─Do─` | 1,1,1,0 | **1** | **4** |
| **NOR** | ¬(A+B) | `─)o─` | 1,0,0,0 | 4 | 4 |
| **XOR** | A⊕B | `─))─` | 0,1,1,0 | 4 | 8–12 |
| **XNOR** | ¬(A⊕B) | `─))o─` | 1,0,0,1 | 5 | 8–12 |

**Como ler o símbolo desenhado:**

| Elemento visual | Significa |
|---|---|
| corpo em D (traseira reta) | família AND |
| corpo em escudo curvo | família OR |
| triângulo | buffer ou inversor |
| **bolinha ○ na saída** | inverta o resultado (AND→NAND, OR→NOR) |
| bolinha ○ na **entrada** | esta entrada é ativa em nível **baixo** |
| linha dupla curva atrás | XOR (distingue de OR) |

**Anote as duas linhas mais úteis desta página:** NAND custa **4 transistores** e XOR custa
**8 a 12**. Toda decisão econômica de projeto digital começa nessa assimetria.

### Portas com mais de 2 entradas

Existem fisicamente (AND de 3, 4, 8 entradas), mas há um limite: quanto mais entradas
em série num transistor CMOS, mais lenta a porta fica. Na prática, bibliotecas param em
4 entradas e árvores são montadas a partir daí.

| Construção | Portas | Profundidade (atraso) |
|---|---|---|
| AND de 8 entradas em **cadeia** | 7 | 7 |
| AND de 8 entradas em **árvore** | 7 | 3 |

Mesmo custo, menos da metade do atraso. **Sempre em árvore.**

---

## 2. As 16 funções de duas variáveis

Com 2 entradas há 4 linhas na tabela-verdade; cada linha pode dar 0 ou 1; logo
2⁴ = **16 funções possíveis**. Elas são todas:

| # | Saída (00,01,10,11) | Nome | Expressão |
|---|---|---|---|
| 0 | 0000 | **FALSO** (constante 0) | 0 |
| 1 | 0001 | **AND** | A·B |
| 2 | 0010 | inibição | A·¬B |
| 3 | 0011 | transferência de A | A |
| 4 | 0100 | inibição inversa | ¬A·B |
| 5 | 0101 | transferência de B | B |
| 6 | 0110 | **XOR** | A⊕B |
| 7 | 0111 | **OR** | A+B |
| 8 | 1000 | **NOR** | ¬(A+B) |
| 9 | 1001 | **XNOR** / equivalência | ¬(A⊕B) |
| 10 | 1010 | negação de B | ¬B |
| 11 | 1011 | **implicação** B→A | A+¬B |
| 12 | 1100 | negação de A | ¬A |
| 13 | 1101 | **implicação** A→B | ¬A+B |
| 14 | 1110 | **NAND** | ¬(A·B) |
| 15 | 1111 | **VERDADE** (constante 1) | 1 |

Sete delas ganharam símbolo próprio (1, 6, 7, 8, 9, 14, e o NOT de uma entrada). As outras
existem, aparecem em lógica formal e em SystemVerilog Assertions, mas raramente ganham peça.

**Só duas dessas 16 são funcionalmente completas sozinhas: a nº 8 (NOR) e a nº 14 (NAND).**
A prova está em [`10-fundamentos.md`](10-fundamentos.md).

---

## 3. Álgebra booleana — identidades

Consulte esta tabela para simplificar expressões à mão. Cada linha economiza portas reais.

### Leis básicas

| Nome | Forma com · e + | Dual |
|---|---|---|
| Identidade | A·1 = A | A+0 = A |
| Elemento nulo | A·0 = 0 | A+1 = 1 |
| Idempotência | A·A = A | A+A = A |
| Complemento | A·¬A = 0 | A+¬A = 1 |
| Involução | ¬(¬A) = A | — |
| Comutativa | A·B = B·A | A+B = B+A |
| Associativa | (A·B)·C = A·(B·C) | (A+B)+C = A+(B+C) |
| Distributiva | A·(B+C) = A·B + A·C | A + B·C = (A+B)·(A+C) ⚠️ |

⚠️ A segunda distributiva **não** tem paralelo na álgebra dos números. É a que mais
confunde quem vem da matemática comum, e a que mais simplifica circuitos.

### Leis de simplificação (as que valem dinheiro)

| Nome | Identidade | Economia típica |
|---|---|---|
| **Absorção** | A + A·B = A | elimina uma porta AND inteira |
| Absorção dual | A·(A+B) = A | idem |
| **Absorção com negação** | A + ¬A·B = A + B | elimina um inversor e um AND |
| **De Morgan** | ¬(A·B) = ¬A + ¬B | converte AND↔OR |
| De Morgan dual | ¬(A+B) = ¬A·¬B | idem |
| **Consenso** | A·B + ¬A·C + B·C = A·B + ¬A·C | elimina o termo redundante B·C |
| Redundância | A·B + A·¬B = A | elimina uma variável |

**De Morgan em uma frase:** *"quebre a barra e troque o sinal"*. É a identidade mais usada
da eletrônica digital, porque permite converter qualquer circuito para só-NAND ou só-NOR.

### XOR — identidades próprias

| Identidade | Uso |
|---|---|
| A⊕0 = A | XOR com 0 não muda nada |
| A⊕1 = ¬A | **XOR com 1 inverte** — é o inversor controlado |
| A⊕A = 0 | é assim que se zera um registrador |
| A⊕B⊕B = A | XOR é sua própria inversa → base da cifra de Vernam e do RAID |
| A⊕B = (A+B)·¬(A·B) | "ou, mas não os dois" |

A linha `A⊕1 = ¬A` é a razão de somadores conseguirem subtrair: basta um XOR por bit
controlado pelo sinal de operação. Ver [`20-circuitos-combinacionais.md`](20-circuitos-combinacionais.md).

---

## 4. Notação — como se lê

O mesmo conceito tem notações diferentes por área. Todas aparecem na literatura:

| Operação | Engenharia | Matemática/lógica | Programação (C, Java, Python) | Verilog |
|---|---|---|---|---|
| NÃO | ¬A, A', Ā | ¬A, ~A | `!a` (lógico), `~a` (bit a bit) | `!a`, `~a` |
| E | A·B, AB | A ∧ B | `a && b`, `a & b` | `&&`, `&` |
| OU | A+B | A ∨ B | `a \|\| b`, `a \| b` | `\|\|`, `\|` |
| OU-exclusivo | A⊕B | A ⊻ B | `a ^ b` | `^` |
| NAND | (A·B)' | A ↑ B (barra de Sheffer) | — | `~&` (redução) |
| NOR | (A+B)' | A ↓ B (seta de Peirce) | — | `~\|` (redução) |

**Armadilhas de leitura:**

- `A+B` em engenharia é **OU**, não soma aritmética. `1+1 = 1` na álgebra booleana.
- `AB` justaposto significa **A E B** (o ponto é omitido, como na multiplicação).
- A **barra em cima** (`Ā`) e o **apóstrofo** (`A'`) são o mesmo NÃO. Livros antigos usam barra.
- Em C/Java, `&&` e `&` são diferentes: `&&` avalia em curto-circuito, `&` opera bit a bit.
  Em hardware **não existe curto-circuito** — todas as entradas são sempre avaliadas,
  porque o circuito está fisicamente lá.

**Precedência** (da mais forte para a mais fraca): `¬` → `·` → `⊕` → `+`.
Ou seja, `A + B·C` significa `A + (B·C)`. Na dúvida, ponha parênteses; ninguém vai reclamar.

### Ativo em nível alto e ativo em nível baixo

| Notação | Significado |
|---|---|
| `RESET` | ativo em **alto**: a função acontece quando o sinal vale 1 |
| `RESET_n`, `nRESET`, `/RESET`, `RESET#`, `R̅E̅S̅E̅T̅` | ativo em **baixo**: a função acontece quando vale **0** |

O sufixo `_n` é a convenção moderna. Confundir isso inverte o comportamento do circuito
inteiro e é uma das armadilhas do [`75-armadilhas.md`](75-armadilhas.md).

---

## 5. Série 7400 — o catálogo clássico

Os circuitos integrados que ensinaram eletrônica digital ao mundo. Lançados pela Texas
Instruments em 1964, ainda fabricados, ainda baratos, ainda ótimos para bancada.

### Portas básicas (os que valem ter)

| CI | Conteúdo | Pinos |
|---|---|---|
| **7400** | 4× NAND de 2 entradas | 14 |
| **7402** | 4× NOR de 2 entradas | 14 |
| **7404** | 6× inversor | 14 |
| **7408** | 4× AND de 2 entradas | 14 |
| **7432** | 4× OR de 2 entradas | 14 |
| **7486** | 4× XOR de 2 entradas | 14 |
| 7410 | 3× NAND de 3 entradas | 14 |
| 7420 | 2× NAND de 4 entradas | 14 |
| 7430 | 1× NAND de 8 entradas | 14 |

**Se for comprar só um CI, compre o 7400.** Com quatro NANDs você faz qualquer coisa —
é o argumento do projeto-modelo, em plástico.

### Blocos funcionais

| CI | O que faz |
|---|---|
| **7483** | somador completo de 4 bits (com carry lookahead) |
| **74138** | decodificador 3→8 |
| **74151** | multiplexador 8→1 |
| **74157** | quádruplo multiplexador 2→1 |
| **7474** | 2× flip-flop D com preset e clear |
| **7476** | 2× flip-flop JK |
| **74161** | contador binário de 4 bits |
| **74595** | registrador de deslocamento com saída paralela (o queridinho do Arduino) |
| **7485** | comparador de magnitude de 4 bits |

### Famílias — as letras no meio do código

`74LS00`, `74HC00`, `74HCT00`… a letra muda a tecnologia interna:

| Sufixo | Nome | Tensão | Consumo | Velocidade | Situação em 2026 |
|---|---|---|---|---|---|
| (nenhum) | TTL original | 5 V | alto | média | obsoleto |
| **LS** | Low-power Schottky | 5 V | médio | boa | legado; ainda se acha |
| **HC** | High-speed CMOS | 2–6 V | **baixíssimo** | boa | **use este** |
| **HCT** | HC compatível com TTL | 5 V | baixo | boa | para conviver com TTL antigo |
| AC / ACT | Advanced CMOS | 2–6 V | baixo | alta | quando precisar de velocidade |
| LVC | Low-voltage CMOS | 1,65–3,6 V | baixo | alta | para 3,3 V (Raspberry Pi, ESP32) |

**Recomendação:** para bancada e protoboard em 5 V, `74HC`. Para conviver com
microcontrolador de 3,3 V, `74LVC`. Nunca mais compre `74LS` novo — consome dez vezes mais
e não oferece vantagem.

**Regra de ouro do CI 7400 que quase todo iniciante esquece:** entrada CMOS **não pode
ficar solta**. Uma entrada flutuante capta ruído, oscila e faz o chip esquentar. Ligue toda
entrada não usada em VCC ou em GND. Isso não é preciosismo — é a causa nº 1 de circuito
"que funciona quando encosto o dedo".

---

## 6. Verilog e VHDL — operadores

### Verilog / SystemVerilog

| Operador | Significado | Exemplo |
|---|---|---|
| `&` | AND bit a bit | `y = a & b;` |
| `\|` | OR bit a bit | `y = a \| b;` |
| `^` | XOR bit a bit | `y = a ^ b;` |
| `~` | NOT bit a bit | `y = ~a;` |
| `~&`, `~\|`, `~^` | NAND, NOR, XNOR | `y = ~(a & b);` |
| `&a` | **redução**: AND de todos os bits de `a` | `y = &a;` → 1 se todos os bits são 1 |
| `\|a` | redução OR | `y = \|a;` → 1 se algum bit é 1 (detector de "não-zero") |
| `^a` | redução XOR = **paridade** | `y = ^a;` |
| `&&`, `\|\|`, `!` | lógicos (resultado de 1 bit) | `if (a && b)` |
| `{a, b}` | concatenação | `{carry, soma} = a + b;` |
| `{4{1'b1}}` | replicação | vale `4'b1111` |
| `a ? b : c` | multiplexador! | `y = sel ? b : a;` |

**O idioma mais útil do Verilog**, que resume meio curso:
```verilog
assign {vai_um, soma} = a + b + vem_um;   // somador completo em uma linha
```
A ferramenta de síntese transforma isso nas 9 portas NAND que o
[projeto-modelo](07-projeto-modelo/README.md) escreve à mão.

| Construção | Quando usar |
|---|---|
| `assign` | lógica combinacional simples |
| `always @(*)` | lógica combinacional com `if`/`case` |
| `always @(posedge clk)` | **lógica sequencial** (flip-flops) |
| `always_comb`, `always_ff` | SystemVerilog: dizem a intenção e o compilador cobra. **Prefira estes.** |
| `reg` / `wire` | tipos do Verilog clássico |
| `logic` | SystemVerilog: substitui os dois. **Use `logic`.** |

### VHDL — equivalências rápidas

| Verilog | VHDL |
|---|---|
| `a & b` | `a and b` |
| `a \| b` | `a or b` |
| `a ^ b` | `a xor b` |
| `~a` | `not a` |
| `assign y = ...` | `y <= ...;` |
| `always @(posedge clk)` | `process(clk) begin if rising_edge(clk) then` |

VHDL é mais verboso e muito mais rígido com tipos. Isso pega erros que o Verilog deixa
passar — e é a razão de setores como aeroespacial e ferroviário preferirem VHDL.

---

## 7. Logisim-evolution — atalhos e truques

| Atalho | Ação |
|---|---|
| `Ctrl+0` | ferramenta **Select** (montar e ligar) |
| `Ctrl+1` | ferramenta **Poke** (testar, clicar em entradas) |
| `Ctrl+2` | ferramenta **Edit tool** |
| `Ctrl+3` | ferramenta **Text** (rótulos) |
| `Ctrl+K` | **iniciar/parar a simulação** |
| `Ctrl+T` | **um passo (tick)** do relógio — indispensável em circuito sequencial |
| `Ctrl+R` | resetar a simulação |
| `Alt+seta` | girar o componente selecionado |
| `Ctrl+D` | duplicar |
| `Ctrl+Z` / `Ctrl+Y` | desfazer / refazer (na 4.1.0 o histórico ficou completo) |

**Menus que valem conhecer:**

| Caminho | O que faz |
|---|---|
| *Project → Analyze Circuit* | extrai a tabela-verdade e a expressão booleana do seu circuito **e** faz o caminho inverso |
| *Project → Add Circuit* | cria um **subcircuito** — a defesa contra a complexidade |
| *Simulate → Tick Frequency* | velocidade do relógio |
| *Simulate → Logging* | grava os valores ao longo do tempo em CSV |
| *File → Export Image* | exporta o diagrama em PNG/SVG (para relatório) |
| *File → Export Verilog/VHDL* | gera HDL a partir do desenho — ponte para a FPGA |

**Propriedades que resolvem 90% dos problemas:**

| Propriedade | Onde | Para quê |
|---|---|---|
| **Data Bits** | qualquer componente | 1 para bit solto, 4/8/16 para barramento |
| **Number of Inputs** | portas | padrão é 5; quase sempre você quer 2 |
| **Output?** | Pin | transforma entrada em saída |
| **Label** | tudo | nomear é depurar |
| **Negate** | portas | inverte uma entrada específica (a bolinha) |

---

## 8. Blocos combinacionais de catálogo

| Bloco | Entradas | Saídas | Para que serve | Custo (NANDs, 4 bits) |
|---|---|---|---|---|
| **Meio somador** | 2 | soma, vai-um | somar o bit menos significativo | 6 |
| **Somador completo** | 3 | soma, vai-um | somar uma casa qualquer | 9 |
| **Somador ripple** | 2n+1 | n+1 | somar números | 36 |
| **Multiplexador (mux)** n→1 | n + log₂n | 1 | **escolher** uma entre n entradas | 4 (2→1) |
| **Demultiplexador** | 1 + log₂n | n | mandar uma entrada para uma de n saídas | ~10 |
| **Decodificador** k→2ᵏ | k | 2ᵏ | transformar número em "acione a linha X" | 10 (2→4), 100 (4→16) |
| **Codificador** 2ᵏ→k | 2ᵏ | k | o inverso: qual linha está ativa? | ~20 |
| **Comparador** | 2n | =, <, > | comparar números | 26 (igualdade) |
| **Deslocador (shifter)** | n + controle | n | multiplicar/dividir por potência de 2 | **0**, se for fixo |
| **Barrel shifter** | n + log₂n | n | deslocar por uma quantidade variável, em 1 ciclo | n·log₂n muxes |
| **Gerador de paridade** | n | 1 | detecção de erro de 1 bit | 4(n−1) |
| **ULA** | 2n + controle | n + flags | somar, subtrair, operar bit a bit | 242 (4 bits, 8 ops) |

Os números da última coluna são **medidos** pelo [projeto-modelo](07-projeto-modelo/README.md),
não estimados.

### O multiplexador é o canivete suíço

Um mux 2ⁿ→1 pode implementar **qualquer** função booleana de n variáveis: ligue as
entradas de dados às constantes da tabela-verdade e as de seleção às variáveis. É por isso
que FPGAs são feitas de tabelas de consulta (LUTs), que são muxes com memória.

---

## 9. Flip-flops — tabela de referência

| Tipo | Entradas | Comportamento | Custo (NANDs) | Uso hoje |
|---|---|---|---|---|
| **Latch SR** | S, R | grava/apaga; S=R=1 é proibido | 2 | evitado; base histórica |
| **Latch D** | D, enable | transparente enquanto habilitado | 4 | usado em ASIC de baixo consumo |
| **Flip-flop D** | D, clk | captura D na **borda** do relógio | 9 | **o padrão absoluto** |
| **Flip-flop JK** | J, K, clk | como SR, mas J=K=1 **inverte** | ~12 | legado; ensinado, pouco usado |
| **Flip-flop T** | T, clk | T=1 inverte a cada borda | ~10 | contadores |

### Tabelas de excitação (para projetar máquinas de estado)

| Transição de Q | D | J K | T |
|---|---|---|---|
| 0 → 0 | 0 | 0 × | 0 |
| 0 → 1 | 1 | 1 × | 1 |
| 1 → 0 | 0 | × 1 | 1 |
| 1 → 1 | 1 | × 0 | 0 |

(× = tanto faz, o que dá liberdade na simplificação.)

**Opinião profissional:** aprenda JK porque cai em prova e aparece em livro antigo, mas
projete tudo com flip-flop D. A indústria inteira padronizou em D — bibliotecas de células
modernas às vezes nem oferecem JK, porque ele custa mais e não faz nada que um D com um
pouco de lógica na entrada não faça.

### Parâmetros de tempo (os que quebram projetos)

| Parâmetro | Definição | Se violado |
|---|---|---|
| **t_setup** | o dado precisa estar estável X antes da borda | captura errada ou metaestabilidade |
| **t_hold** | o dado precisa continuar estável X depois da borda | captura errada |
| **t_cq** (clock-to-Q) | atraso da borda até a saída mudar | limita a frequência |
| **t_pd** | atraso de propagação da lógica combinacional | limita a frequência |

A frequência máxima do circuito é:

```
f_max = 1 / (t_cq + t_pd + t_setup + desvio_do_relógio)
```

Essa fórmula é o coração do que engenheiros chamam de "fechar o timing", e é a diferença
entre um projeto que funciona no simulador e um que funciona no silício. Detalhe em
[`30-circuitos-sequenciais.md`](30-circuitos-sequenciais.md).

---

## 10. Obsoleto — e o que usar no lugar

| Obsoleto | Por quê | Use no lugar |
|---|---|---|
| Logisim original (2.7.1) | abandonado em 2014 | **Logisim-evolution** 4.x |
| Família 74LS | consome ~10× mais que CMOS | **74HC** ou **74LVC** |
| Lógica RTL, DTL, ECL | superadas por CMOS em consumo | CMOS |
| Flip-flop JK em projeto novo | custa mais, não faz mais | flip-flop **D** |
| `reg`/`wire` do Verilog clássico | ambíguos, geram erro silencioso | `logic` (SystemVerilog) |
| `always @(posedge clk)` sem `_ff` | não declara intenção | `always_ff` / `always_comb` |
| Mapas de Karnaugh acima de 4 variáveis | ilegíveis; erro humano garantido | Quine–McCluskey, Espresso, ou deixar a ferramenta de síntese fazer |
| Minimização manual em projeto profissional | a ferramenta faz melhor e mais rápido | síntese lógica (Yosys, Design Compiler) |
| PROM/PAL/GAL | substituídos | CPLD, FPGA |
| Contagem de "portas" como métrica de venda | ninguém publica | contagem de transistores, ou área em mm² |

> **Sobre Karnaugh:** ele continua **indispensável para aprender** — é o que faz a
> minimização parar de ser mágica. Mas ninguém, em nenhuma empresa séria, minimiza um
> circuito de produção à mão desde os anos 1980. Se seu professor insistir que é
> habilidade profissional, ele está descrevendo 1975. Como ferramenta pedagógica, porém,
> não há substituto: essa é minha opinião, e é a de quase todo mundo que projeta hardware.

---

## Autoteste

1. Quantos transistores CMOS custa um NAND? E um XOR? Qual a consequência de projeto?
2. Escreva a lei de De Morgan nas duas formas e diga para que ela serve na prática.
3. Quanto vale `A + ¬A·B`? Quantas portas isso economiza?
4. Em `A + B·C`, quem tem precedência?
5. Qual CI da série 7400 tem quatro portas NAND? E qual tem quatro XOR?
6. Por que uma entrada CMOS não usada não pode ficar solta?
7. O que `^a` faz em Verilog, sendo `a` um barramento de 8 bits?
8. Escreva a fórmula da frequência máxima de um circuito síncrono.
9. Por que se recomenda flip-flop D e não JK em projeto novo?
10. Cite três coisas desta página que estão obsoletas e o que as substituiu.

*(Respostas: 1 — 4 e 8–12; XOR é caro, então evita-se em caminho crítico; 2 — ¬(A·B)=¬A+¬B
e ¬(A+B)=¬A·¬B; serve para converter qualquer circuito em só-NAND ou só-NOR; 3 — vale A+B,
economiza um inversor e um AND; 4 — `·` antes de `+`, logo A+(B·C); 5 — 7400 e 7486;
6 — capta ruído, oscila e aquece o chip; 7 — calcula a paridade dos 8 bits; 8 — f_max =
1/(t_cq + t_pd + t_setup + skew); 9 — D custa menos e a indústria padronizou nele;
10 — Logisim 2.7.1→evolution, 74LS→74HC, JK→D, reg/wire→logic, Karnaugh manual→síntese.)*
