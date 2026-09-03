# 75 · Armadilhas, erros clássicos e mitos

**Nível:** todos · **Data:** 14/08/2026

Vinte erros que se repetem há décadas e oito mitos que continuam sendo ensinados.
Alguns deles vêm de professores; digo isso sem desrespeito, mas com franqueza.

---

## Parte 1 — Armadilhas conceituais

### 1. Confundir o "ou" do português com o OR lógico

**O erro.** "Café **ou** chá" exclui a possibilidade de tomar os dois. O OR lógico **inclui**.

**Sintoma.** Seu circuito responde 1 quando as duas entradas estão ligadas e você esperava 0.

**Correção.** Você queria **XOR**. É a primeira armadilha que todo mundo tropeça, e é
linguística, não técnica.

### 2. Achar que uma porta é "um transistor"

**O erro.** Contar transistores como se fossem portas.

**Realidade.** NOT = 2, NAND = 4, XOR = 8 a 12, flip-flop = 20 a 26, célula SRAM = 6 (e não
é porta nenhuma). A conversão exige três correções ([`50`](50-quantas-portas-tem-um-computador.md), §4.2).

### 3. Achar que a maioria dos transistores de um chip faz lógica

**O erro.** Dividir 28 bilhões por 4 e anunciar 7 bilhões de portas.

**Realidade.** ~20% dos transistores estão em memória SRAM, ~10% não são lógica digital, e
a média é ~6 transistores por porta, não 4.

### 4. Ignorar o tempo

**O erro.** Achar que, porque `¬(A·B) = ¬A + ¬B` algebricamente, os dois circuitos são
intercambiáveis.

**Realidade.** Eles têm custos, atrasos e consumos diferentes, e podem produzir glitches
diferentes. A álgebra descreve **o que**, nunca **quando**.

### 5. Achar que profundidade e tamanho são a mesma coisa

**O erro.** "Meu circuito tem 7 portas, logo o atraso é 7."

**Realidade.** Sete portas em cadeia dão atraso 7; sete em árvore dão atraso 3. O que
determina a velocidade é o **caminho crítico**, não o total.

### 6. Achar que um `if` em hardware economiza tempo

**O erro.** Transportar a intuição de software: "se a condição for falsa, esse ramo não
executa".

**Realidade.** Os dois ramos são calculados **sempre**, e um mux descarta um deles. Em
hardware, `if` **custa** um mux; ele não economiza nada. Essa é a diferença mental mais
difícil para quem vem de software.

### 7. Esquecer que uma entrada flutuante não é zero

**O erro.** Deixar uma entrada CMOS sem ligar, achando que "não conectado = 0".

**Realidade.** A entrada capta ruído, oscila entre 0 e 1, e faz o chip esquentar. É a
causa nº 1 do circuito "que funciona quando encosto o dedo".

**Correção.** Ligue **toda** entrada não usada em VCC ou GND. Em placas, use resistores de
pull-up ou pull-down.

### 8. Confundir ativo em alto com ativo em baixo

**O erro.** Tratar `RESET_n` como se fosse `RESET`.

**Realidade.** O sufixo `_n` (ou `/`, ou `#`, ou a barra em cima) significa que a função
acontece com **0**. Inverter isso inverte o comportamento do circuito inteiro.

**Onde dói mais:** o CI 74138 (decodificador 3→8) tem saídas ativas em baixo. Gente perde
tardes com isso.

### 9. Achar que "2 nm" mede 2 nanômetros

**O erro.** Comparar chips pelo nome do nó.

**Realidade.** O nome é marketing desde ~2000. O comprimento de porta real num nó "2 nm"
está na casa de 12–20 nm. Compare **MTr/mm²** ou altura de célula.

### 10. Achar que memória é feita de flip-flops

**O erro.** Extrapolar do projeto-modelo ("guardei 16 bits com 266 portas") para uma DRAM.

**Realidade.** Flip-flop custa ~26 transistores por bit; SRAM, 6; DRAM, 1 + capacitor. A
hierarquia de memória inteira é consequência dessa diferença de ~100×.

---

## Parte 2 — Armadilhas de projeto (as que quebram circuitos)

### 11. Latch acidental em Verilog

**O erro.**
```verilog
always @(*) begin
    if (sel) y = a;        // e se sel for 0? Não foi dito.
end
```

**O que acontece.** O sintetizador conclui: "quando `sel` for 0, `y` mantém o valor
anterior" — e infere um **latch**. Você queria lógica combinacional e ganhou memória.

**Correção.** Atribua um valor padrão antes, ou cubra todos os casos:
```verilog
always_comb begin
    y = 1'b0;              // valor padrão: elimina o latch
    if (sel) y = a;
end
```
E use `always_comb` (SystemVerilog): ele **erra na compilação** se um latch for inferido,
em vez de gerar silenciosamente.

**Este é o bug nº 1 de quem escreve Verilog há menos de um ano.**

### 12. Usar `=` onde devia usar `<=`

**A regra sem exceção:**

| Contexto | Operador | Descreve |
|---|---|---|
| `always_ff @(posedge clk)` | `<=` (não bloqueante) | flip-flops |
| `always_comb` | `=` (bloqueante) | lógica combinacional |

Trocar produz circuitos que simulam de um jeito e sintetizam de outro — o pior tipo de bug,
porque a simulação diz que está tudo bem.

### 13. Realimentação combinacional acidental

**O erro.** Fechar um ciclo de portas sem flip-flop no caminho.

**O que acontece.** O circuito oscila (um "anel de oscilação") ou trava num estado
indefinido. Ferramentas de síntese avisam; iniciantes ignoram o aviso.

**Correção.** Todo ciclo precisa passar por pelo menos um elemento de memória.

### 14. Esquecer o reset

**O erro.** Assumir que os flip-flops começam em 0.

**Realidade.** Numa FPGA há inicialização pelo bitstream; num ASIC, **não**. Ao energizar,
cada flip-flop cai aleatoriamente em 0 ou 1.

**Correção.** Registradores de **controle** (FSM, contadores, flags) sempre precisam de
reset. Registradores de **dados** frequentemente não — e resetar tudo engorda desnecessariamente
a rede de reset, que já é uma das maiores do chip.

### 15. Cruzar domínios de relógio sem sincronizador

**O erro.** Ligar um sinal do domínio A direto num flip-flop do domínio B.

**O que acontece.** Metaestabilidade. O bug é raro, não reprodutível e aparece no cliente.

**Correção.** Dois flip-flops em série para sinais de controle de 1 bit; FIFO assíncrono ou
código Gray para barramentos. **Nunca** sincronize os bits de um barramento
individualmente — eles podem chegar em ciclos diferentes e formar um valor que nunca existiu.

### 16. Usar sinal externo sem anti-repique

**O erro.** Ligar um botão diretamente a um contador.

**O que acontece.** Um aperto conta 7.

**Correção.** Sincronizador **e** filtro de repique. São coisas diferentes: o sincronizador
resolve metaestabilidade (nanossegundos), o anti-repique resolve ruído mecânico
(milissegundos). Precisa dos dois.

### 17. Gerar relógio com lógica combinacional

**O erro.**
```verilog
assign clk_lento = contador[3];    // usar um bit do contador como relógio
```

**O que acontece.** Esse "relógio" tem glitches, não passa pela árvore de relógio dedicada,
e a ferramenta de análise de timing não sabe analisá-lo.

**Correção.** Use um **clock enable**: mantenha o relógio único e habilite o flip-flop
periodicamente.
```verilog
always_ff @(posedge clk) if (pulso_lento) contador <= contador + 1;
```

### 18. Violação de hold descoberta tarde

**O erro.** Achar que baixar a frequência resolve qualquer problema de timing.

**Realidade.** Baixar a frequência resolve violação de **setup**. Violação de **hold** é
independente da frequência — e frequentemente só aparece no silício.

### 19. Confundir simulação com síntese

**O erro.** Usar construções que simulam bem e não sintetizam: laços `while` sem limite,
atrasos `#10`, `initial` para inicializar registradores em ASIC, divisão por variável.

**Correção.** Aprenda o **subconjunto sintetizável** da linguagem. Rode a síntese cedo,
não só no fim. "Simulou" não significa "existe em hardware".

### 20. Não testar exaustivamente quando dá

**O erro.** Testar um somador de 4 bits com "alguns casos".

**Realidade.** São 256 casos. Testá-los **todos** custa milissegundos e transforma o teste
em prova. Em hardware pequeno, a verificação exaustiva é um luxo disponível — use.

---

## Parte 3 — Mitos

### Mito 1: "Karnaugh é uma habilidade profissional"

**Verdade parcial.** É uma ferramenta pedagógica excelente e uma ferramenta profissional
obsoleta desde os anos 1980. Nenhum projeto de produção é minimizado à mão.

**Por que persiste:** ementas universitárias mudam devagar, e Karnaugh é fácil de avaliar
em prova. Aprenda — mas saiba que a habilidade profissional é escrever RTL correto e
verificá-lo, não desenhar retângulos.

### Mito 2: "Existem 7 portas lógicas, ponto final"

**Verdade.** Sete é convenção. Matematicamente há 16 funções de 2 entradas; numa biblioteca
de células industrial há **centenas** de células, incluindo AOI/OAI compostas que não têm
nome didático.

### Mito 3: "NAND é a porta mais rápida porque é a mais simples"

**Verdade parcial.** NAND e NOR têm o mesmo número de transistores (4). NAND é preferida
porque empilha **NMOS** em série, e o NMOS conduz 2 a 3× melhor que o PMOS. É física de
mobilidade de portadores, não simplicidade.

### Mito 4: "A Lei de Moore acabou"

**Impreciso.** O que **morreu** (por volta de 2005) foi a **escala de Dennard** — a promessa
de mais velocidade sem mais potência. A Lei de Moore desacelerou, mas a densidade continua
crescendo; o que mudou é que o custo por transistor parou de cair como antes.

Confundir as duas é o erro mais comum em textos de divulgação sobre semicondutores.

### Mito 5: "Computadores quânticos vão substituir os clássicos"

**Falso.** Portas quânticas resolvem uma lista **curta** de problemas com vantagem
comprovada. Para somar dois números, um chip de US$ 0,50 vence qualquer computador quântico
existente por ordens de magnitude. Coexistência, não substituição.

### Mito 6: "Circuitos digitais são exatos, então não têm erro"

**Falso em dois sentidos.** Primeiro, a exatidão vem da **margem de ruído** e da
regeneração de sinal a cada porta — é uma propriedade projetada, não intrínseca. Segundo,
erros existem: raios cósmicos causam *soft errors* (por isso servidores usam ECC),
transistores envelhecem, e a metaestabilidade nunca chega a probabilidade zero.

### Mito 7: "Mais portas = mais rápido"

**Falso.** Mais portas em **paralelo** (menos profundidade) é mais rápido. Mais portas em
série é mais lento. O Kogge-Stone usa mais portas que o ripple-carry e é muito mais rápido;
mas um circuito mal projetado pode usar mais portas e ser mais lento.

### Mito 8: "O processador é a parte principal do chip"

**Falso em área.** Num SoC moderno, os núcleos de CPU ocupam 10–20% da área. Caches ocupam
30–50%. GPU e aceleradores costumam ocupar mais que as CPUs. A maior parte do seu chip é
memória e infraestrutura para alimentar o processador com dados.

---

## Parte 4 — Armadilhas de bancada (se você for montar com CIs)

| Armadilha | Consequência | Correção |
|---|---|---|
| Sem capacitor de desacoplamento | comutação causa queda de tensão local; o circuito trava aleatoriamente | 100 nF entre VCC e GND **de cada CI**, o mais perto possível dos pinos |
| Misturar 5 V e 3,3 V | níveis incompatíveis; pode danificar o CI | use conversor de nível, ou famílias compatíveis (74LVC tolera 5 V nas entradas) |
| Protoboard em alta frequência | capacitância parasita, contatos ruins | acima de ~10 MHz, protoboard não funciona; use PCB |
| Alimentar antes de conferir a pinagem | CI queima em segundos | confira o pino 1 (chanfro/ponto) **duas vezes** |
| LED sem resistor | queima o LED e possivelmente a saída do CI | 220–470 Ω em série, sempre |
| Achar que o CI está queimado | quase sempre é fiação | troque só depois de conferir alimentação, GND e entradas flutuantes |

---

## Parte 5 — Erros de estudo

### "Vou entender depois, agora só copio o circuito"

Funciona por dois laboratórios e desmorona no terceiro. Este assunto é **cumulativo**: um
somador de 4 bits é impossível de depurar sem entender o somador completo.

### "Vou aprender pelo simulador, sem a teoria"

Você chega ao Lab 9 e trava. Sem entender setup/hold e realimentação, circuitos sequenciais
parecem magia intermitente.

### "Vou aprender a teoria e depois praticar"

Também não funciona. Ninguém internaliza "a saída realimentada sustenta o estado" lendo
sobre isso. Alterne: leia um arquivo, faça o laboratório correspondente.

### "Vou comprar uma FPGA e aprender com ela"

Instalar 80 GB de ferramentas para acender um LED faz muita gente desistir. Faça o curso no
simulador. Compre hardware **depois** de saber o que quer fazer com ele.

---

## Autoteste

1. Qual é a armadilha linguística mais comum, e qual porta a resolve?
2. Por que uma entrada CMOS não usada não pode ficar solta?
3. Como se produz um latch acidental em Verilog, e como evitá-lo?
4. Quando se usa `<=` e quando se usa `=`?
5. Por que baixar a frequência não conserta violação de hold?
6. Qual a diferença entre anti-repique e sincronizador? Preciso dos dois?
7. Por que não se deve gerar relógio com lógica combinacional? O que usar no lugar?
8. A Lei de Moore acabou? Explique o que realmente morreu.
9. Por que NAND é preferida a NOR, se ambas têm 4 transistores?
10. "Mais portas = mais rápido" — verdadeiro ou falso? Justifique com um exemplo.
11. Que fração da área de um SoC moderno é ocupada pelos núcleos de CPU?
12. Por que capacitor de desacoplamento é obrigatório em bancada?

*(Respostas: 1 — confundir "ou" com OR; a porta correta costuma ser XOR; 2 — capta ruído,
oscila e aquece; 3 — deixando um caminho sem atribuição num bloco combinacional; evita-se
com valor padrão e `always_comb`; 4 — `<=` em `always_ff`, `=` em `always_comb`; 5 — hold
depende de o caminho ser rápido demais, não do período; 6 — anti-repique filtra ruído
mecânico em milissegundos, sincronizador evita metaestabilidade; sim, precisa dos dois;
7 — tem glitches e não passa pela árvore de relógio; use clock enable; 8 — não; o que morreu
foi a escala de Dennard, por volta de 2005; 9 — porque NAND empilha NMOS, que conduzem
melhor que PMOS; 10 — falso: depende da profundidade, não do total — árvore contra cadeia;
11 — 10 a 20%; 12 — a comutação causa quedas locais de tensão que travam o circuito.)*
