# 70 · Prática — 12 laboratórios progressivos

**Nível:** todos · **Data:** 14/08/2026

Cada laboratório tem: **objetivo**, **ferramenta**, **passos**, **critério objetivo de
"deu certo"** e **o que você aprendeu**. Faça na ordem — cada um usa o anterior.

Tempo total estimado: **25 a 40 horas** para os doze, fazendo com atenção.

| Lab | Assunto | Tempo | Ferramenta |
|---|---|---|---|
| 1 | As sete portas | 45 min | navegador ou Logisim |
| 2 | De Morgan na prática | 30 min | Logisim |
| 3 | Tudo a partir de NAND | 1 h | Logisim ou Python |
| 4 | Meio somador e somador completo | 1 h | Logisim |
| 5 | Somador de 4 bits hierárquico | 1,5 h | Logisim |
| 6 | Multiplexador e decodificador | 1 h | Logisim |
| 7 | Karnaugh no mundo real | 2 h | papel + Logisim |
| 8 | Latch e flip-flop | 2 h | Logisim |
| 9 | Contador e display | 2 h | Logisim |
| 10 | Do desenho ao Verilog | 3 h | Icarus Verilog |
| 11 | Máquina de estados | 4 h | Verilog |
| 12 | Estenda o projeto-modelo | 6 h+ | Python |

---

## Lab 1 — As sete portas, na mão

**Objetivo.** Construir e testar cada uma das sete portas clássicas, e nunca mais precisar
consultar a tabela.

**Ferramenta.** https://circuitverse.org/simulator (ou Logisim).

**Passos.**
1. Monte um circuito com 2 entradas e 7 saídas — uma para cada porta — todas alimentadas
   pelas mesmas entradas.
2. Rotule cada saída com o nome da porta.
3. Percorra as quatro combinações de entrada e anote as sete saídas.

**Deu certo se** sua tabela de 4 linhas × 7 colunas coincide com esta:

| A | B | AND | OR | NAND | NOR | XOR | XNOR | NOT A |
|---|---|---|---|---|---|---|---|---|
| 0 | 0 | 0 | 0 | 1 | 1 | 0 | 1 | 1 |
| 0 | 1 | 0 | 1 | 1 | 0 | 1 | 0 | 1 |
| 1 | 0 | 0 | 1 | 1 | 0 | 1 | 0 | 0 |
| 1 | 1 | 1 | 1 | 0 | 0 | 0 | 1 | 0 |

**O que você aprendeu.** Que NAND, NOR e XNOR são literalmente as colunas de AND, OR e XOR
invertidas. Uma vez visto lado a lado, não se esquece.

---

## Lab 2 — De Morgan com os próprios olhos

**Objetivo.** Verificar experimentalmente a identidade mais usada da eletrônica digital.

**Passos.**
1. Monte `¬(A·B)` — um AND seguido de um NOT.
2. Ao lado, monte `¬A + ¬B` — dois NOTs seguidos de um OR.
3. Ligue as mesmas duas entradas nos dois circuitos.
4. Acrescente um **XOR** comparando as duas saídas, com um LED/saída chamado "DIFERENÇA".

**Deu certo se** a saída "DIFERENÇA" fica em **0 nas quatro combinações**. Se acender em
alguma, há erro de fiação.

**Bônus.** Conte as portas dos dois circuitos. Qual é mais barato? (Resposta: o primeiro:
AND+NOT = 3 NANDs; o segundo: 2 NOTs + OR = 5 NANDs. De Morgan preserva a função, não o
custo — e é por isso que a escolha entre as formas é uma decisão de projeto.)

**O que você aprendeu.** Que "provar" e "verificar" são coisas diferentes, e que o
comparador por XOR é a forma padrão de testar equivalência de circuitos — a mesma ideia que
os SAT solvers industriais usam ([`60`](60-teoria-avancada.md), §7).

---

## Lab 3 — Tudo a partir de NAND

**Objetivo.** Provar, com as mãos, a completude funcional.

**Passos.** Usando **apenas portas NAND**, construa e teste:
1. NOT (1 NAND)
2. AND (2)
3. OR (3)
4. NOR (4)
5. XOR (4)
6. XNOR (5)

Para cada um, valide contra a tabela do Lab 1.

**Deu certo se** as seis tabelas batem **e** as contagens de portas batem com os números
entre parênteses.

**Variante em Python** (se preferir código a mouse):
```bash
cd portas-logicas/07-projeto-modelo
python3 -c "
from nand import custo
from portas import NOT, AND, OR, NOR, XOR, XNOR
for nome, fn, args in [('NOT',NOT,(1,)), ('AND',AND,(1,1)), ('OR',OR,(1,1)),
                       ('NOR',NOR,(1,1)), ('XOR',XOR,(1,1)), ('XNOR',XNOR,(1,1))]:
    print(nome, custo(fn, *args))
"
```

**O que você aprendeu.** Que a economia das portas é assimétrica: OR custa 50% mais que AND.
Essa assimetria vai reaparecer em toda decisão de projeto daqui em diante.

---

## Lab 4 — Meio somador e somador completo

**Objetivo.** Construir a peça mais executada da computação.

**Passos.**
1. Monte o meio somador (XOR + AND). Teste as 4 linhas.
2. Monte o somador completo com 5 portas (2 XOR, 2 AND, 1 OR). Teste as **8** linhas.
3. Use *Project → Analyze Circuit* no Logisim para extrair a tabela-verdade automaticamente
   e compare com a sua.

**Deu certo se** as 8 linhas do somador completo batem com:

| a b c | soma vai_um |
|---|---|
| 0 0 0 | 0 0 |
| 0 0 1 | 1 0 |
| 0 1 0 | 1 0 |
| 0 1 1 | 0 1 |
| 1 0 0 | 1 0 |
| 1 0 1 | 0 1 |
| 1 1 0 | 0 1 |
| 1 1 1 | 1 1 |

**O que você aprendeu.** Que `soma` é a paridade das três entradas e `vai_um` é o voto por
maioria. Duas funções clássicas escondidas dentro de uma operação aritmética banal.

---

## Lab 5 — Somador de 4 bits hierárquico

**Objetivo.** Aprender a usar subcircuitos — a defesa contra a complexidade.

**Passos.**
1. No Logisim: *Project → Add Circuit…*, chame de `somador_completo`.
2. Monte o somador completo lá dentro, com pinos de entrada `a`, `b`, `cin` e saída
   `soma`, `cout`.
3. Volte ao circuito principal. O `somador_completo` agora aparece na árvore da esquerda.
4. Arraste **quatro** cópias e ligue `cout` de cada uma ao `cin` da seguinte.
5. Use *splitters* (Wiring → Splitter) para separar os barramentos de 4 bits em bits
   individuais.
6. Teste com pelo menos: 3+5, 7+8, 15+1, 9+9.

**Deu certo se:**

| Entrada | Saída esperada |
|---|---|
| 3 + 5 | 8, cout=0 |
| 7 + 8 | 15, cout=0 |
| 15 + 1 | 0, **cout=1** (transbordo) |
| 9 + 9 | 2, **cout=1** |

**Desafio.** Meça o caminho crítico: quantas portas um sinal atravessa da entrada do bit 0
até o `cout` final? (Resposta: ~8, dois níveis por estágio — o problema do ripple-carry.)

**O que você aprendeu.** Hierarquia. E, ao ver 15+1 dar 0, o que é transbordo silencioso —
o comportamento padrão de hardware e a origem de muitos bugs de software.

---

## Lab 6 — Multiplexador e decodificador

**Objetivo.** Construir as duas peças de infraestrutura de qualquer processador.

**Passos.**
1. Monte um **mux 2→1** com portas (não use o componente pronto do Logisim). Teste.
2. Monte um **mux 4→1** usando três muxes 2→1.
3. Monte um **decodificador 2→4** com 2 inversores e 4 ANDs.
4. Confirme que o decodificador é *one-hot*: exatamente uma saída ativa por vez.

**Deu certo se:**
- o mux 4→1 seleciona corretamente nas 4 combinações;
- o decodificador nunca tem duas saídas em 1 simultaneamente.

**Desafio.** Implemente a função `f(a,b) = a XOR b` usando **apenas** um mux 4→1 e as
constantes 0 e 1. (Dica: ligue as entradas de dados aos valores da tabela-verdade.)
Isso demonstra por que uma LUT de FPGA é um mux.

**O que você aprendeu.** Que o mux é universal, e por que as FPGAs são feitas de LUTs.

---

## Lab 7 — Karnaugh no mundo real

**Objetivo.** Fazer uma minimização que vale a pena, e depois ver a ferramenta fazer melhor.

**O problema.** Projete o decodificador BCD→7 segmentos, mas apenas para os segmentos
`a` e `g` (os dois traços horizontais, de cima e do meio).

**Passos.**
1. Monte a tabela-verdade de 4 entradas (dígitos 0–9) para o segmento `a`.
   Os dígitos 10–15 são **"não importa" (X)** — use-os a seu favor.
2. Desenhe o mapa de Karnaugh 4×4 e agrupe.
3. Escreva a expressão minimizada.
4. Monte no Logisim e verifique contra a tabela original.
5. Use *Project → Analyze Circuit* e compare com o que a ferramenta produz.

**Deu certo se** o seu circuito acerta os 10 dígitos válidos.

**O que você aprendeu.** Que condições "não importa" são grátis e reduzem muito o circuito.
E, provavelmente, que a ferramenta achou uma expressão tão boa quanto a sua em um segundo —
que é exatamente por que ninguém minimiza à mão em produção
([`20`](20-circuitos-combinacionais.md), §5.3).

---

## Lab 8 — Latch e flip-flop

**Objetivo.** Ver um circuito lembrar, e ver a diferença entre nível e borda.

**Passos.**
1. Monte um **latch SR com dois NANDs** cruzados. Teste `set`, `reset` e `manter`.
2. Tente o estado proibido (as duas entradas em 0) e depois solte as duas ao mesmo tempo.
   Observe.
3. Monte um **latch D** (4 NANDs). Verifique a transparência: com `enable=1`, a saída
   acompanha D.
4. Monte um **flip-flop D mestre-escravo** com dois latches D e um inversor.
5. Com o flip-flop, mude D várias vezes com o relógio em nível alto. **A saída não deve
   mudar.**

**Deu certo se:**
- o latch mantém o valor com as duas entradas em repouso;
- o latch D é transparente com `enable=1` e congela com `enable=0`;
- o flip-flop **só** muda na borda de subida do relógio.

**O que você aprendeu.** A diferença entre sensível a nível e sensível a borda — que é a
razão de todo hardware síncrono do mundo usar flip-flop, não latch.

---

## Lab 9 — Contador com display

**Objetivo.** Um circuito sequencial completo, visível.

**Passos.**
1. Use o componente **Clock** do Logisim (Wiring → Clock).
2. Monte um contador de 4 bits com 4 flip-flops D (ou use o pronto, se a montagem manual
   já tiver sido feita no Lab 8).
3. Ligue a saída de 4 bits a um **Hex Digit Display** (Input/Output).
4. Habilite a simulação (`Ctrl+K`) e observe.
5. Acrescente um botão de **reset**.
6. Acrescente uma entrada de **habilitação** que congela a contagem.

**Deu certo se** o display conta 0→F e volta a 0, o reset zera imediatamente, e a
habilitação congela sem perder o valor.

**Desafio.** Faça o contador contar só até 9 e voltar a 0 (contador BCD). Dica: detecte o
valor 10 com um AND e use-o para acionar o reset. Depois pergunte-se: o que acontece
durante o instante em que o valor 10 existe antes de ser apagado? (Resposta: um glitch —
e é por isso que contadores BCD reais usam a comparação para inibir a contagem, não para
resetar depois do fato.)

**O que você aprendeu.** Relógio, reset, habilitação — e a primeira armadilha real de
circuito sequencial.

---

## Lab 10 — Do desenho ao Verilog

**Objetivo.** Migrar do mouse para o texto, que é como se trabalha de verdade.

**Pré-requisito.** Icarus Verilog instalado ([`03`](03-instalacao.md), §5), ou
https://www.edaplayground.com/ no navegador.

**Passos.**
1. Reescreva o somador de 4 bits do Lab 5 em Verilog (o código está no
   [`06-exemplos.md`](06-exemplos.md), exemplo 3).
2. Escreva o testbench exaustivo (256 casos).
3. Compile e rode.
4. Gere o arquivo `.vcd` e abra no GTKWave.
5. Agora **substitua** todo o corpo por uma única linha:
   ```verilog
   assign {vai_um, soma} = a + b + vem_um;
   ```
6. Rode o **mesmo** testbench.

**Deu certo se** as duas versões passam nos 256 casos com 0 erros.

**O que você aprendeu.** Que descrever comportamento é radicalmente mais produtivo que
desenhar estrutura — e que o testbench é o que permite confiar na troca. Este é o momento em
que a maioria das pessoas entende por que a indústria abandonou o desenho de esquemáticos.

**Bônus.** Se tiver o Yosys instalado, rode `yosys -p "read_verilog somador4.v; synth; stat"`
e veja **quantas portas** a ferramenta gerou. Compare com as 36 NANDs do projeto-modelo.

---

## Lab 11 — Máquina de estados

**Objetivo.** Projetar um circuito sequencial não trivial, do diagrama ao código.

**O problema.** Um detector de sequência: a saída vai a 1 quando a entrada serial produz o
padrão `1011`, permitindo sobreposição (`1011011` dispara duas vezes).

**Passos.**
1. Desenhe o diagrama de estados no papel. (Serão 5 estados: nada, viu `1`, viu `10`,
   viu `101`, viu `1011`.)
2. Escreva a tabela de transição.
3. Implemente em Verilog como uma FSM de **Moore**, com codificação one-hot.
4. Escreva um testbench que alimente a sequência `0110110111011` e verifique os disparos
   nos instantes certos.
5. Gere as ondas e confirme visualmente.

**Deu certo se** os disparos ocorrem exatamente nas posições esperadas e não há disparo
espúrio.

**Desafio.** Reimplemente como Mealy e compare: quantos estados a menos? A saída fica um
ciclo mais cedo? Ela tem glitch?

**O que você aprendeu.** O ciclo completo de projeto sequencial: especificação → diagrama →
tabela → código → verificação. É esse ciclo, e não a sintaxe, que constitui a habilidade.

---

## Lab 12 — Estenda o computador de 4 bits

**Objetivo.** Trabalhar dentro de um projeto existente, como se faz na vida real.

**Base.** [`07-projeto-modelo/`](07-projeto-modelo/README.md).

**Tarefas, em ordem de dificuldade:**

1. **Acrescente a instrução `NOT`** (A = ¬A). A ULA já sabe; falta ligar o opcode.
   **Escreva o teste antes de implementar.**
2. **Acrescente a flag de carry** como um flip-flop, e a instrução `JC` (saltar se houve
   transbordo). Meça quantas portas isso custou com `contagem.py`.
3. **Escreva um programa** que calcule a sequência de Fibonacci módulo 16 e imprima os
   primeiros 6 termos.
4. **Troque o somador ripple por um carry-lookahead** de 4 bits. Meça as duas coisas:
   portas gastas **e** profundidade lógica. Você deve encontrar mais portas e menos
   profundidade.
5. **Amplie para 8 bits.** Verifique se o custo total cresce linearmente. (A ULA cresce;
   o decodificador de endereço, não.)
6. **Escreva um montador**: um programa Python que traduza texto (`LDI 5\nADD 3\nOUT`)
   para a lista de tuplas.

**Deu certo se** `python3 testes.py` continua passando **e** os seus novos testes passam.

**O que você aprendeu.** Que modificar um sistema existente com testes que o protegem é uma
experiência completamente diferente de modificar um sem. E o que a contagem de portas
revela sobre o custo real de cada funcionalidade acrescentada — uma intuição que quase
nenhum programador tem.

---

## Como saber que você aprendeu

Sem consultar nada, você deve conseguir:

- [ ] Desenhar as 7 tabelas-verdade de memória.
- [ ] Construir qualquer porta a partir de NAND.
- [ ] Projetar um somador de n bits e explicar por que ele é lento.
- [ ] Explicar por que um circuito com realimentação lembra.
- [ ] Explicar a diferença entre latch e flip-flop, e por que a indústria usa flip-flop.
- [ ] Escrever a equação de f_max e explicar cada termo.
- [ ] Explicar por que dividir transistores por 4 não dá o número de portas.
- [ ] Escrever um módulo Verilog combinacional e um sequencial, corretamente.
- [ ] Dizer onde as portas de um processador são gastas, em ordem de quantidade.

Se marcou todos, você cobriu uma disciplina universitária inteira de Sistemas Digitais e
boa parte da seguinte.

---

## Autoteste

1. No Lab 2, os dois circuitos são logicamente equivalentes. Eles custam o mesmo?
2. No Lab 5, por que 15+1 dá 0 e não 16?
3. No Lab 6, como um mux 4→1 implementa qualquer função de 2 variáveis?
4. No Lab 7, por que as condições "não importa" reduzem o circuito?
5. No Lab 8, o que acontece ao soltar simultaneamente as duas entradas do estado proibido?
6. No Lab 9, por que um contador BCD que reseta ao detectar 10 tem um glitch?
7. No Lab 10, por que a versão de uma linha passa nos mesmos 256 testes?
8. No Lab 12, por que o custo em portas de ampliar de 4 para 8 bits não é exatamente o dobro?

*(Respostas: 1 — não: 3 NANDs contra 5; 2 — 4 bits só representam 0–15, e o transbordo vai
para o cout; 3 — ligando as entradas de dados às quatro saídas da tabela-verdade;
4 — porque permitem escolher o valor que forma grupos maiores no mapa; 5 — o circuito pode
oscilar de forma imprevisível; 6 — o valor 10 existe por um instante antes de ser apagado;
7 — porque o `+` do Verilog é sintetizado exatamente no mesmo somador; 8 — a aritmética
escala linearmente, mas a decodificação de endereço escala exponencialmente no número de
bits de endereço.)*
