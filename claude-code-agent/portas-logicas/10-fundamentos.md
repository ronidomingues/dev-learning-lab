# 10 · Fundamentos — a álgebra por trás das portas

**Nível:** iniciante → intermediário · **Data:** 14/08/2026

Aqui o assunto deixa de ser intuição e passa a ser matemática. Nada do que vem a seguir é
difícil; é apenas preciso. Todo termo é definido antes de ser usado.

---

## 1. O objeto de estudo

**Definição.** Uma **função booleana** de n variáveis é uma função

```
f : {0,1}ⁿ → {0,1}
```

Ou seja: recebe n valores que são 0 ou 1, e devolve um valor que é 0 ou 1. Nada mais.

**Exemplo concreto.** `f(a,b) = 1 se a e b forem ambos 1, senão 0`. É o AND.

**Definição.** Uma **porta lógica** é a realização física de uma função booleana:
um dispositivo cujas tensões de entrada e saída representam 0 e 1 segundo essa função.

A separação importa: a *função* é matemática e eterna; a *porta* é física, feita de relé,
válvula, transistor ou fóton, e envelhece. Ao longo de 90 anos a mesma função AND foi
implementada de cinco maneiras completamente diferentes ([`11-historia.md`](11-historia.md)).

---

## 2. Quantas funções existem?

Esta conta responde à primeira metade da pergunta que originou o curso.

Uma função de n variáveis é definida por sua tabela-verdade. A tabela tem **2ⁿ linhas**
(todas as combinações de entrada). Cada linha pode receber 0 ou 1 na coluna de saída, de
forma independente. Logo:

```
número de funções booleanas de n variáveis = 2^(2ⁿ)
```

| n | Linhas na tabela (2ⁿ) | Funções possíveis (2^2ⁿ) |
|---|---|---|
| 0 | 1 | 2 (as constantes 0 e 1) |
| 1 | 2 | **4** (identidade, NOT, sempre-0, sempre-1) |
| 2 | 4 | **16** |
| 3 | 8 | 256 |
| 4 | 16 | 65.536 |
| 5 | 32 | 4.294.967.296 |
| 6 | 64 | ≈ 1,8 × 10¹⁹ |

**Duas leituras deste crescimento, e as duas são importantes:**

1. Para 2 entradas há 16 funções; sete ganharam nome (as portas clássicas). É por isso que
   a resposta "quantos tipos de porta existem" é *sete por convenção, dezesseis por
   matemática*.
2. O número de funções cresce **duplamente exponencial**. Já com 6 variáveis há mais
   funções booleanas do que estrelas na galáxia. Esse crescimento é a raiz do resultado
   mais surpreendente da teoria de circuitos, no [`60-teoria-avancada.md`](60-teoria-avancada.md):
   **quase toda função booleana exige um circuito astronomicamente grande** — e ninguém
   consegue apontar uma delas explicitamente.

---

## 3. As 16 funções de duas variáveis, e por que sete bastaram

A lista completa está no [`05-manual-de-uso.md`](05-manual-de-uso.md), §2. O que interessa
aqui é o critério de seleção. Das 16:

| Grupo | Quantas | Por que não viraram porta |
|---|---|---|
| Constantes (sempre 0, sempre 1) | 2 | não dependem da entrada; em circuito, é um fio no terra ou no VCC |
| Transferência (copia A, copia B) | 2 | é um fio |
| Negação de uma só variável | 2 | é o NOT, que já existe com 1 entrada |
| Inibições e implicações | 4 | úteis em lógica formal, raras em circuito; fáceis de montar com as outras |
| **AND, OR, XOR, NAND, NOR, XNOR** | 6 | **estas viraram portas** |

Somando o NOT (função de 1 variável), temos as **sete portas clássicas**. Não há nada de
sagrado nesse número: é engenharia, não matemática. A escolha se justifica por três
critérios simultâneos — a função é útil, é barata de fabricar, e aparece com frequência.

---

## 4. Formas de representar uma função

Uma mesma função tem várias representações, e trocar de representação é a operação básica
do projeto digital.

### 4.1 Tabela-verdade

Completa e sem ambiguidade, mas cresce exponencialmente. Acima de 5 variáveis, inútil para
humanos.

### 4.2 Expressão booleana

```
f(a,b,c) = a·b + ¬a·c
```

Compacta e manipulável algebricamente. É a forma que se simplifica.

### 4.3 Circuito (netlist)

O desenho, ou a lista de portas e conexões. É o que se fabrica.

### 4.4 Diagrama de decisão binária (BDD)

Uma árvore em que cada nó pergunta o valor de uma variável. Com regras de redução (fundir
nós idênticos, pular nós irrelevantes) vira um **ROBDD**, que tem uma propriedade notável:
para uma dada ordem de variáveis, **a forma reduzida é única**. Isso transforma "estas duas
funções são iguais?" num teste barato, e é a base de ferramentas industriais de verificação
formal de equivalência.

**As quatro representam a mesma coisa**, e o trabalho de um projetista é escolher a
representação certa para cada tarefa: tabela para especificar, expressão para simplificar,
circuito para fabricar, BDD para verificar.

---

## 5. Formas normais: como ir da tabela ao circuito, sempre

**Problema:** você tem uma tabela-verdade arbitrária. Como construir *algum* circuito que a
realize? Existe um método que sempre funciona.

### 5.1 Soma de produtos (SOP), ou forma normal disjuntiva

**Receita:**
1. Olhe apenas as linhas em que a saída é **1**.
2. Para cada uma, escreva um AND de todas as variáveis, negando as que valem 0 nessa linha.
   Esse termo se chama **mintermo**, e ele vale 1 **exatamente** naquela linha.
3. Ligue todos os mintermos com OR.

**Exemplo completo.** Função "maioria" de três entradas (vale 1 se ao menos duas forem 1) —
que é justamente o `vai_um` do somador completo:

| a | b | c | f |
|---|---|---|---|
| 0 | 0 | 0 | 0 |
| 0 | 0 | 1 | 0 |
| 0 | 1 | 0 | 0 |
| 0 | 1 | 1 | **1** |
| 1 | 0 | 0 | 0 |
| 1 | 0 | 1 | **1** |
| 1 | 1 | 0 | **1** |
| 1 | 1 | 1 | **1** |

Quatro linhas em 1, quatro mintermos:

```
f = ¬a·b·c + a·¬b·c + a·b·¬c + a·b·c
```

Custo direto: 4 ANDs de 3 entradas + 1 OR de 4 entradas + 3 inversores.

**Simplificando** (usando `a·b·c + a·b·¬c = a·b`, e repetindo o termo `a·b·c` — o que é
legítimo, porque `x + x = x`):

```
f = a·b + a·c + b·c
```

De 4 termos com 3 variáveis para 3 termos com 2. **Redução de quase metade das portas, e a
função é exatamente a mesma.** É isso que minimização significa em dinheiro.

### 5.2 Produto de somas (POS), ou forma normal conjuntiva

O espelho: olhe as linhas em que a saída é **0**, escreva um OR por linha (negando as
variáveis que valem 1), e ligue tudo com AND.

**Quando usar cada uma:** se a função tem poucos 1s, SOP fica menor. Se tem poucos 0s, POS
fica menor. Na prática, ferramentas de síntese testam as duas e mais algumas.

### 5.3 A garantia

**Toda** função booleana tem uma forma SOP e uma POS. Portanto:

> **Toda função booleana pode ser implementada com AND, OR e NOT.**

Isso já responde "as portas bastam?". Mas dá para fazer melhor.

---

## 6. Completude funcional — por que NAND sozinha basta

**Definição.** Um conjunto de portas é **funcionalmente completo** quando toda função
booleana pode ser construída só com elas.

Já sabemos que `{AND, OR, NOT}` é completo (seção 5). A pergunta seguinte é: dá para
reduzir?

### 6.1 `{AND, NOT}` é completo

Por De Morgan, `a + b = ¬(¬a · ¬b)`. Ou seja, OR pode ser eliminado. Análogo para
`{OR, NOT}`.

### 6.2 `{NAND}` sozinha é completa — a prova

Basta construir NOT e AND só com NAND (e então, pelo item anterior, temos tudo):

**NOT com um NAND:**

| a | NAND(a,a) | ¬a |
|---|---|---|
| 0 | 1 | 1 ✔ |
| 1 | 0 | 0 ✔ |

Justificativa algébrica: `NAND(a,a) = ¬(a·a) = ¬a` (idempotência).

**AND com dois NANDs:**

```
AND(a,b) = NOT(NAND(a,b)) = NAND(NAND(a,b), NAND(a,b))
```

| a | b | NAND(a,b) | NOT disso | a·b |
|---|---|---|---|---|
| 0 | 0 | 1 | 0 | 0 ✔ |
| 0 | 1 | 1 | 0 | 0 ✔ |
| 1 | 0 | 1 | 0 | 0 ✔ |
| 1 | 1 | 0 | 1 | 1 ✔ |

Como `{AND, NOT}` é completo e ambos saem de NAND, **`{NAND}` é funcionalmente completo**. ∎

**OR com três NANDs**, para completar o quadro:
`a + b = ¬(¬a·¬b) = NAND(NAND(a,a), NAND(b,b))`.

O [projeto-modelo](07-projeto-modelo/README.md) é essa prova em código executável: um
computador inteiro em que a única primitiva é `nand()`.

### 6.3 `{NOR}` sozinha também é completa

Mesmo argumento, com o dual: `NOR(a,a) = ¬a`, e daí sai tudo.

**Curiosidade histórica com consequência real:** o computador de bordo da Apollo (AGC,
1966) foi construído **inteiramente com portas NOR de 3 entradas** — cerca de 5.600 delas,
num único tipo de circuito integrado. A razão foi industrial, não estética: usar um único
componente simplificava a compra, o teste e a confiabilidade, que era o critério dominante
numa missão tripulada.

### 6.4 Quais conjuntos **não** são completos

| Conjunto | Completo? | Por quê |
|---|---|---|
| {NAND} | ✅ | provado acima |
| {NOR} | ✅ | dual |
| {AND, OR} | ❌ | **sem negação, nunca se produz 1 a partir de duas entradas 0**. Funções monótonas apenas. |
| {AND, NOT} | ✅ | De Morgan gera OR |
| {XOR} | ❌ | XOR só gera funções lineares (afins) sobre GF(2) |
| {XOR, AND} | ✅ | é a base do "anel de Reed–Muller" — a forma polinomial |
| {MUX 2→1} | ✅ | com constantes 0 e 1 nas entradas de dados |
| {IMPLICAÇÃO, 0} | ✅ | resultado clássico da lógica |

O caso `{AND, OR}` merece atenção: essas duas portas só produzem **funções monótonas** —
aquelas em que trocar uma entrada de 0 para 1 nunca faz a saída cair de 1 para 0.
A ideia de circuito monótono virou uma das poucas áreas onde a teoria conseguiu provar
limites inferiores fortes ([`60-teoria-avancada.md`](60-teoria-avancada.md)).

---

## 7. Os cinco porquês: por que NAND é a porta preferida?

Aplicando a regra dos cinco porquês do preset a um fato que todo livro afirma e poucos
explicam.

**Fato:** fábricas de circuitos integrados preferem NAND. Bibliotecas de células têm mais
variantes de NAND que de qualquer outra porta.

**1. Por quê?** Porque em CMOS, NAND custa 4 transistores, contra 6 de um AND.

**2. Por que AND custa mais?** Porque a lógica CMOS estática é **naturalmente inversora**.
Um arranjo de transistores produz `¬(alguma coisa)`; para obter AND, é preciso montar o
NAND e acrescentar um inversor (mais 2 transistores).

**3. Por que CMOS é naturalmente inversora?** Porque uma porta CMOS tem duas redes: a de
transistores tipo P puxando para o 1 (VDD) e a de tipo N puxando para o 0 (terra). O
transistor N conduz quando a entrada é **alta**; ligar entradas altas ao terra produz saída
**baixa**. A negação está na física do dispositivo.

**4. Por que o transistor N conduz com entrada alta e o P com entrada baixa?** Porque
suas portas de controle respondem a portadores de carga opostos (elétrons no N, lacunas
no P). É física de semicondutor: a tensão positiva na porta atrai elétrons e forma o canal
do tipo N. É a mesma razão pela qual não existe um transistor "não inversor" trivial.

**5. E por que se usam os dois tipos juntos, então?** Porque a combinação **complementar**
(daí o "C" de CMOS) garante que, em repouso, **exatamente uma** das redes está conduzindo,
e nunca as duas. Isso significa **corrente estática praticamente zero**. Foi essa
propriedade — e não velocidade, em que o CMOS perdia para a lógica bipolar nos anos 1970 —
que fez o CMOS varrer todas as alternativas quando a densidade dos chips cresceu e o calor
virou o limite físico.

**Parada legítima alcançada:** física de semicondutores + um trade-off econômico
documentado (consumo estático versus velocidade), resolvido pelo mercado por volta de 1980.

Continuação em [`12-do-transistor-a-porta.md`](12-do-transistor-a-porta.md).

---

## 8. Álgebra booleana como estrutura matemática

Para quem quer o nome formal das coisas: uma **álgebra de Boole** é um conjunto com duas
operações binárias (∧, ∨), uma unária (¬) e dois elementos distinguidos (0, 1), satisfazendo
comutatividade, associatividade, distributividade em ambos os sentidos, absorção,
identidade e complemento.

Fatos que valem saber:

- **O princípio da dualidade.** Toda identidade continua verdadeira se você trocar
  ∧↔∨ e 0↔1 simultaneamente. É por isso que a tabela do [`05`](05-manual-de-uso.md) tem
  uma coluna "dual" — cada lei vem de graça em par. Isso não é coincidência notacional: é
  uma simetria estrutural da álgebra.
- **Teorema de Stone (1936).** Toda álgebra de Boole finita é isomorfa à álgebra dos
  subconjuntos de um conjunto finito. Consequência: toda álgebra de Boole finita tem 2ⁿ
  elementos, e "conjuntos" e "lógica" são a mesma matemática vestida de roupas diferentes.
- **Não é a álgebra dos números.** `1 + 1 = 1` aqui. Se você trouxer intuições da
  aritmética, elas vão falhar exatamente na distributiva `a + b·c = (a+b)·(a+c)`, que é
  verdadeira aqui e falsa nos reais.

---

## 9. Circuitos combinacionais e sequenciais — a divisão fundamental

| | Combinacional | Sequencial |
|---|---|---|
| A saída depende de… | só das entradas atuais | entradas atuais **e** do estado |
| É uma função matemática? | sim | não — é uma máquina de estados |
| Tem ciclos no grafo? | **não** | **sim** (realimentação) |
| Exemplos | somador, mux, decodificador, ULA | latch, flip-flop, registrador, contador, CPU inteira |
| Como se testa | tabela-verdade | sequência de entradas ao longo do tempo |
| Arquivo | [`20`](20-circuitos-combinacionais.md) | [`30`](30-circuitos-sequenciais.md) |

**A fronteira é exatamente uma coisa: existe caminho de realimentação?** Um circuito
combinacional é um grafo acíclico dirigido (DAG) de portas. Assim que se fecha um ciclo,
o circuito ganha memória — e ganha, junto, todos os problemas de tempo (metaestabilidade,
oscilação, corridas) que o [`30`](30-circuitos-sequenciais.md) trata.

---

## 10. O que a álgebra booleana esconde

Uma advertência que raramente aparece em livro-texto e vale mais que um capítulo:

A álgebra booleana descreve **o que** o circuito calcula, jamais **quando**. Nela, a
igualdade `¬(a·b) = ¬a + ¬b` é exata. No silício, os dois circuitos:

- gastam números diferentes de transistores;
- respondem em tempos diferentes;
- consomem energias diferentes;
- e, durante a transição, passam por valores **intermediários e transitórios** que a
  álgebra não prevê. Esses transitórios se chamam **glitches**, são reais, e podem ser
  capturados por um flip-flop se caírem na borda errada.

Toda a dificuldade profissional de projeto digital mora nessa lacuna entre a álgebra e a
física. Quem só sabe a álgebra projeta circuitos que estão corretos e não funcionam.

---

## Autoteste

1. Quantas funções booleanas de 3 variáveis existem? Mostre a conta.
2. Por que existem 16 funções de 2 variáveis, mas só 7 portas clássicas?
3. Escreva a forma SOP da função "exatamente uma das três entradas é 1".
4. Prove que NAND é funcionalmente completa. (Duas construções bastam.)
5. Por que `{AND, OR}` **não** é funcionalmente completo?
6. Qual é o princípio da dualidade, e para que ele serve na prática?
7. Qual é a diferença exata entre circuito combinacional e sequencial, em termos de grafo?
8. Por que `a + b·c = (a+b)·(a+c)` é verdadeiro aqui e falso na aritmética comum?
9. Aplicando os cinco porquês: por que CMOS é naturalmente inversor?
10. O que a álgebra booleana não consegue descrever sobre um circuito real?

*(Respostas: 1 — 2^(2³) = 2⁸ = 256; 2 — as outras 9 são constantes, cópias, negações
simples e implicações, que não valem uma peça própria; 3 — `¬a·¬b·c + ¬a·b·¬c + a·¬b·¬c`;
4 — NAND(a,a) = ¬a e NAND(NAND(a,b),NAND(a,b)) = a·b, e {AND,NOT} é completo; 5 — sem
negação só se produzem funções monótonas, e nunca 1 a partir de todas as entradas em 0;
6 — trocar ∧↔∨ e 0↔1 preserva a validade, o que dá cada lei em par; 7 — combinacional é
grafo acíclico, sequencial tem ciclo de realimentação; 8 — porque a estrutura é um reticulado
distributivo em ambos os sentidos, não um corpo numérico; 9 — porque a rede de transistores
N conduz com entrada alta e liga a saída ao terra, o que nega; 10 — o tempo: atraso,
glitches, consumo e a ordem em que os sinais chegam.)*
