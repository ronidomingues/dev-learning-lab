# 60 · Teoria avançada — complexidade de circuitos

**Nível:** pesquisa · **Data:** 14/08/2026
**Pré-requisito:** [`10-fundamentos.md`](10-fundamentos.md) e alguma familiaridade com
notação assintótica (O grande). Nada além disso.

Este arquivo trata da pergunta que a engenharia não responde: **qual é o menor circuito
possível para calcular uma função?** É uma das áreas mais bonitas — e mais frustrantes —
da ciência da computação teórica.

---

## 1. As duas medidas de um circuito

**Definição.** Um **circuito booleano** é um grafo acíclico dirigido cujos nós são portas
(de um conjunto de base fixo, tipicamente `{AND, OR, NOT}` com fan-in 2) e cujas folhas são
as variáveis de entrada.

| Medida | Definição | Significado físico |
|---|---|---|
| **Tamanho** (*size*) | número de portas | área, custo, energia |
| **Profundidade** (*depth*) | comprimento do caminho mais longo da entrada à saída | atraso, latência |

Uma função tem uma **complexidade de circuito**: o menor tamanho (ou profundidade) entre
todos os circuitos que a computam. Denotamos `C(f)` e `D(f)`.

**Diferença crucial em relação a algoritmos:** um circuito trabalha com **entrada de
tamanho fixo**. Para falar de uma função sobre entradas de qualquer tamanho, usa-se uma
**família de circuitos** `{C_n}`, um para cada n. Isso dá aos circuitos um poder estranho,
tratado no §5.

---

## 2. O argumento de contagem de Shannon (1949)

O resultado mais impressionante da área, e a demonstração é elementar.

**Teorema (Shannon).** *Quase toda* função booleana de n variáveis exige circuitos de
tamanho pelo menos `2ⁿ/n` (aproximadamente).

**Demonstração (esboço completo, por contagem):**

1. **Quantas funções existem?** Já sabemos: `2^(2ⁿ)`.

2. **Quantos circuitos de tamanho s existem?** Cada porta escolhe seu tipo (constante) e
   duas entradas entre as `n + s` possibilidades (variáveis ou saídas de portas
   anteriores). Um limite superior grosseiro:
   ```
   número de circuitos de tamanho ≤ s  ≤  (c · (n+s)²)^s
   ```
   que é aproximadamente `2^(O(s log s))`.

3. **Compare.** Para que os circuitos de tamanho s cubram todas as funções, é preciso
   `2^(O(s log s)) ≥ 2^(2ⁿ)`, ou seja, `s log s ≥ 2ⁿ`, o que dá `s ≳ 2ⁿ/n`.

4. **Conclusão:** existem muito mais funções do que circuitos pequenos. Logo, a esmagadora
   maioria das funções **não cabe** em nenhum circuito pequeno. ∎

**Por que isso é impressionante.** O teorema diz que funções difíceis são a **regra**, não
a exceção. Escolha uma função booleana de 100 variáveis ao acaso: com probabilidade
esmagadora, o menor circuito que a computa tem mais portas do que há átomos no universo.

**E aqui vem a parte que enlouquece a área há 75 anos:**

> **Ninguém conseguiu exibir uma função explícita que exija circuitos superpolinomiais.**

Sabemos que quase todas as funções são difíceis. Não conseguimos apontar **uma**.
O melhor limite inferior conhecido para uma função explícita em NP, para circuitos gerais,
está na casa de `(3 + ε)·n` — **linear**. Estamos a uma distância astronômica do
`2ⁿ/n` que sabemos existir.

Isso é o análogo, em circuitos, do problema P vs NP — e o motivo pelo qual provar limites
inferiores é considerado o problema em aberto mais difícil da área.

---

## 3. Classes de complexidade de circuitos

| Classe | Definição | Exemplo de problema |
|---|---|---|
| **AC⁰** | profundidade **constante**, tamanho polinomial, fan-in **ilimitado** | OR de n bits, AND de n bits |
| **AC⁰[p]** | AC⁰ mais portas MOD-p | contagem módulo p |
| **TC⁰** | AC⁰ mais portas de **maioria** (limiar) | multiplicação, divisão, redes neurais |
| **NC¹** | profundidade **O(log n)**, fan-in 2, tamanho polinomial | fórmulas booleanas, aritmética |
| **NC^k** | profundidade O(logᵏ n) | — |
| **NC** | união de todos os NC^k | "eficientemente paralelizável" |
| **P/poly** | tamanho polinomial, profundidade livre | tudo que é computável em tempo polinomial, e mais |

Sabemos que `AC⁰ ⊊ AC⁰[p] ⊊ TC⁰ ⊆ NC¹ ⊆ NC ⊆ P/poly`.
As primeiras duas inclusões são **estritas** e demonstradas. As demais são conjecturas.

### 3.1 O resultado que se conseguiu provar: paridade não está em AC⁰

**Teorema (Furst–Saxe–Sipser 1981; Håstad 1986).** A função **paridade** (XOR de n bits)
não pode ser computada por circuitos de profundidade constante e tamanho polinomial.
Mais precisamente, profundidade d exige tamanho `2^Ω(n^(1/(d−1)))`.

**Por que isso importa fora da teoria:** paridade é a função *mais simples que se possa
imaginar* — é um XOR. E ainda assim é provadamente impossível calculá-la em profundidade
constante. Sabemos, portanto, que **profundidade tem um preço real e demonstrável**.

A técnica de prova — o **lema de troca de Håstad** (*switching lemma*), que mostra que
fixar aleatoriamente parte das variáveis "achata" um circuito AC⁰ mas não achata a
paridade — é uma das mais elegantes da área e reaparece em criptografia e em aprendizado
de máquina teórico.

**Consequência de engenharia direta:** um somador de n bits não pode ter profundidade
constante, porque o bit mais significativo da soma depende da paridade dos vai-uns. O
limite `Ω(log n)` de profundidade dos somadores de prefixo do
[`20`](20-circuitos-combinacionais.md) não é falta de criatividade dos engenheiros — é um
teorema.

### 3.2 A barreira das provas naturais

**Razborov e Rudich (1994)** provaram algo desconcertante: quase todas as técnicas
conhecidas para provar limites inferiores de circuitos pertencem a uma classe que eles
chamaram de "provas naturais" — e **se existirem funções pseudoaleatórias fortes (base de
toda a criptografia moderna), nenhuma prova natural pode separar P de NP.**

Ou seja: as ferramentas que temos são provadamente insuficientes, a menos que a
criptografia moderna esteja errada. Foi um resultado que redirecionou a área inteira, e é
uma das três "barreiras" conhecidas (junto com relativização e algebrização).

---

## 4. Circuitos monótonos — onde a teoria venceu

**Definição.** Um circuito é **monótono** se usa apenas AND e OR, sem NOT.

Já vimos ([`10`](10-fundamentos.md), §6.4) que `{AND, OR}` não é funcionalmente completo:
só computa funções monótonas. Mas para essas funções, é possível provar limites inferiores
fortes.

**Teorema (Razborov, 1985).** Determinar se um grafo tem um clique de tamanho k exige
circuitos monótonos de tamanho `n^Ω(√k)` — **superpolinomial**.

Foi um marco: o primeiro limite inferior superpolinomial para um problema natural em NP,
em um modelo de circuito restrito.

**E a decepção que veio junto:** logo depois se mostrou (Tardos, 1988) que existem funções
monótonas em P que exigem circuitos monótonos exponenciais. Ou seja, **a negação é
genuinamente poderosa**, e resultados sobre circuitos monótonos não se transferem para
circuitos gerais. O caminho estava fechado.

---

## 5. Uniformidade — por que circuitos são estranhos

Uma família de circuitos `{C_n}` pode ser **não uniforme**: nada exige que exista um
algoritmo que construa `C_n` a partir de n. Cada circuito pode ser um objeto arbitrário,
"dado de presente".

Consequência bizarra e verdadeira: **P/poly contém problemas indecidíveis.**

Tome qualquer linguagem unária indecidível `L ⊆ {1}*`. Para cada n, o circuito `C_n` é a
constante 0 ou a constante 1 — uma porta. Tamanho 1, polinomial. A família decide L.
Mas L é indecidível por máquina de Turing.

**A moral:** circuitos escondem a dificuldade em *construir* o circuito. Por isso a teoria
distingue famílias **uniformes** (construíveis por um algoritmo eficiente) das gerais.
Na prática, tudo que se fabrica é uniforme — a síntese lógica é justamente o algoritmo que
constrói o circuito.

**Um teorema que conecta os dois mundos** (Karp–Lipton, 1980): se `NP ⊆ P/poly`, então a
hierarquia polinomial colapsa no segundo nível. Como se acredita que ela não colapsa,
acredita-se que NP **não** tem circuitos de tamanho polinomial — mas ninguém provou.

---

## 6. Fórmulas versus circuitos

**Definição.** Uma **fórmula** é um circuito em que cada porta tem fan-out 1 — ou seja, uma
árvore. Nenhum resultado intermediário pode ser reaproveitado.

| | Circuito | Fórmula |
|---|---|---|
| Reaproveitamento | permitido | proibido |
| Medida | tamanho | tamanho da fórmula |
| Relação | `L(f) ≥ C(f)` | pode ser exponencialmente maior |

**Teorema (Spira).** Uma fórmula de tamanho s pode ser convertida em uma de profundidade
`O(log s)`. Consequência: fórmulas de tamanho polinomial = NC¹.

**A intuição de engenharia:** fan-out é reaproveitamento, e reaproveitar cálculos
intermediários é o que faz um circuito ser menor que uma fórmula. É a mesma diferença entre
programação dinâmica e recursão ingênua. Em silício, fan-out custa capacitância — o
reaproveitamento é grátis em portas e caro em tempo.

---

## 7. Verificação formal — a teoria que virou produto

Como saber se dois circuitos computam a mesma função? Ingenuamente, comparando 2ⁿ linhas.
Para 64 bits, impossível.

| Técnica | Como funciona | Onde é usada |
|---|---|---|
| **ROBDD** | forma canônica: mesma função ⇒ mesmo grafo | equivalência, análise de alcançabilidade |
| **SAT solver** | testa se `f ⊕ g` é satisfazível; se não, são iguais | verificação de equivalência industrial |
| **Model checking** | verifica propriedades temporais de FSMs | protocolos, coerência de cache |
| **Provadores de teoremas** | prova assistida por humano (Coq, ACL2, Isabelle) | somadores, FPU, microcódigo |

**O caso que mudou a indústria:** o **bug da divisão do Pentium (FDIV, 1994)** — cinco
entradas erradas numa tabela de consulta de 1.066 causaram erro na divisão de ponto
flutuante. Custou à Intel **US$ 475 milhões** em recall e uma crise de reputação.

Depois disso, verificação formal deixou de ser pesquisa e virou obrigação: hoje, unidades
de ponto flutuante de grandes fabricantes são **provadas formalmente corretas** antes do
tapeout. Foi um caso raro em que um resultado de ciência da computação teórica passou
diretamente para o processo industrial, por pressão econômica.

**Ironia notável:** SAT — o problema NP-completo canônico, o exemplo padrão de
"computacionalmente intratável" — é a ferramenta prática que se usa para verificar
circuitos. Solvers modernos (CDCL, com aprendizado de cláusulas) resolvem rotineiramente
instâncias com **milhões** de variáveis. O pior caso é exponencial; os casos que aparecem
na prática, não. Essa lacuna entre pior caso e caso prático é um dos fatos mais úteis e
menos discutidos da computação.

---

## 8. Os limites físicos: Landauer e a computação reversível

### 8.1 O princípio de Landauer (1961)

**Apagar** um bit de informação dissipa, no mínimo, `k_B · T · ln 2` de energia em calor.

À temperatura ambiente (300 K), isso dá **≈ 2,85 × 10⁻²¹ J** por bit apagado —
cerca de 0,018 eV.

**Por que apagar custa e calcular não:** apagar reduz o número de estados possíveis do
sistema, ou seja, **reduz entropia**. A segunda lei da termodinâmica exige que essa entropia
apareça em outro lugar: como calor no ambiente.

Uma porta AND comum **apaga** informação: das quatro combinações de entrada, três levam à
saída 0. Sabendo só a saída, você não recupera a entrada. Cada operação dessas tem um
custo termodinâmico mínimo irremovível.

**Onde estamos em 2026:** uma comutação de porta custa da ordem de **10⁻¹⁶ J**, ou seja,
cerca de **30.000 vezes** o limite de Landauer. Há muita margem física, mas ela vem
diminuindo — e a verificação experimental do princípio já foi feita
(Bérut et al., *Nature*, 2012, mediram a dissipação prevista em um sistema de partícula
única).

### 8.2 Computação reversível

Se apagar custa, **não apague**. Uma porta reversível tem tantas saídas quanto entradas e é
uma bijeção — dá para rodar para trás.

| Porta | Entradas/saídas | Universal? |
|---|---|---|
| **Toffoli** (CCNOT) | 3/3 | sim, para lógica clássica reversível |
| **Fredkin** (troca controlada) | 3/3 | sim, e preserva o número de 1s |
| **CNOT** | 2/2 | não sozinha |

Um circuito reversível pode, em princípio, computar dissipando energia arbitrariamente
próxima de zero — desde que rode devagar (**adiabaticamente**) e que os bits intermediários
("lixo") sejam desfeitos em vez de apagados. O truque de **Bennett** (1973) mostra como:
compute, copie o resultado, e rode o cálculo ao contrário para limpar o lixo.

**Situação prática:** lógica adiabática existe em protótipos e em nichos de ultrabaixo
consumo. Não é competitiva em uso geral — o custo em área e a lentidão superam a economia
de energia, e há um trade-off fundamental entre velocidade e dissipação. **É pesquisa
séria, não é produto.** Isso pode mudar se a energia se tornar o limite absoluto.

E há uma conexão direta com o próximo tópico: **computação quântica é obrigatoriamente
reversível**, porque a evolução unitária é reversível. É por isso que portas quânticas
lembram Toffoli e Fredkin, e não AND e OR.

---

## 9. Portas quânticas — outro objeto matemático

Não são portas booleanas com "mais estados". São **matrizes unitárias** agindo sobre
vetores de amplitudes complexas.

| Porta clássica | Porta quântica análoga |
|---|---|
| NOT | X (Pauli-X) |
| — | H (Hadamard): cria superposição |
| — | Z, S, T: fases |
| XOR/cópia | CNOT: emaranha dois qubits |
| Toffoli | CCNOT quântico |

Diferenças que impedem qualquer comparação direta:

| | Porta clássica | Porta quântica |
|---|---|---|
| Estado | 0 ou 1 | vetor em ℂ² de norma 1 |
| Reversível? | não | **sempre** |
| Copiável? | sim | **não** (teorema da não clonagem) |
| Erro | ~10⁻¹⁸ por operação | **10⁻³ a 10⁻⁴** em 2026 |
| Contagem típica em 2026 | bilhões por chip | centenas a milhares de qubits; correção de erro consome a maior parte |

**Conjunto universal:** `{H, T, CNOT}` é universal para computação quântica, no sentido de
aproximar qualquer unitária com precisão arbitrária (teorema de Solovay–Kitaev).

**Advertência franca, e é opinião profissional:** não faz sentido dizer que "um computador
quântico tem N portas" em comparação com um clássico. São modelos diferentes, com vantagens
demonstradas apenas para uma lista **curta** de problemas (fatoração, simulação de sistemas
quânticos, alguns problemas de álgebra linear estruturada). Para somar dois números, um
processador quântico é ordens de magnitude pior que um chip de US$ 0,50.

---

## 10. Redes de ordenação — um recanto elegante

Uma **rede de ordenação** é um circuito que ordena n números usando apenas comparadores
(cada um pega dois valores e devolve o menor e o maior), com o padrão de comparações
**fixo** — não depende dos dados.

| Rede | Comparadores | Profundidade |
|---|---|---|
| Bubble/insertion | O(n²) | O(n) |
| **Batcher (bitônica)** | O(n log²n) | **O(log²n)** |
| **AKS (1983)** | O(n log n) | **O(log n)** — ótimo |

A rede AKS atinge o ótimo assintótico, mas a constante escondida é tão gigantesca que ela
é **inútil na prática para qualquer n imaginável**. É o exemplo canônico de "assintoticamente
ótimo e praticamente irrelevante" — um lembrete de que O grande esconde constantes que às
vezes decidem tudo.

Redes de Batcher, por outro lado, são usadas de verdade: em GPUs e em hardware de rede,
onde o padrão fixo de comparações é o que permite paralelismo total.

---

## 11. Os problemas em aberto

| Problema | Estado em 2026 |
|---|---|
| Existe função explícita em NP com circuitos superpolinomiais? | **aberto** — o maior problema da área |
| `NP ⊆ P/poly`? | acredita-se que não; sem prova |
| `NC = P`? (tudo é paralelizável?) | acredita-se que não; sem prova |
| `TC⁰ ⊊ NC¹`? | aberto |
| Limite inferior melhor que `(3+ε)n` para circuitos gerais | aberto há décadas |
| Como contornar a barreira das provas naturais | linha ativa de pesquisa |

**Uma honestidade sobre o campo:** o progresso em limites inferiores foi extraordinariamente
lento. Entre 1949 (Shannon) e 2026, o melhor limite para funções explícitas passou de
linear para... linear com uma constante melhor. Isso não é falta de esforço — é indício de
que falta uma ideia fundamentalmente nova.

---

## Autoteste

1. Qual a diferença entre tamanho e profundidade, e a que corresponde cada um fisicamente?
2. Reproduza o argumento de contagem de Shannon em três passos.
3. Qual é o paradoxo entre o teorema de Shannon e o estado da arte em limites inferiores?
4. O que o teorema de Håstad diz sobre a paridade, e qual a consequência para somadores?
5. Por que resultados sobre circuitos monótonos não se transferem para circuitos gerais?
6. Como P/poly pode conter problemas indecidíveis?
7. Qual a diferença entre fórmula e circuito? A que conceito de software isso corresponde?
8. Qual bug histórico transformou verificação formal em prática industrial obrigatória?
9. Qual a ironia do uso de SAT solvers em verificação?
10. Quanto vale o limite de Landauer, e quantas vezes acima dele estamos em 2026?
11. Por que computação quântica é obrigatoriamente reversível?
12. Por que a rede de ordenação AKS é assintoticamente ótima e praticamente inútil?

*(Respostas: 1 — número de portas (área/custo) e caminho mais longo (atraso); 2 — há
2^(2ⁿ) funções, ~2^(O(s log s)) circuitos de tamanho s, logo s ≳ 2ⁿ/n; 3 — sabemos que
quase toda função é difícil, mas não conseguimos exibir uma única função explícita difícil;
4 — paridade não está em AC⁰, logo somadores não podem ter profundidade constante;
5 — porque a negação é genuinamente poderosa: há funções monótonas em P com circuitos
monótonos exponenciais; 6 — porque famílias não uniformes não precisam ser construíveis por
algoritmo; 7 — fórmula tem fan-out 1, ou seja, não reaproveita subresultados, como recursão
ingênua contra programação dinâmica; 8 — o FDIV do Pentium, em 1994; 9 — o problema
NP-completo canônico é a ferramenta prática, porque instâncias reais não são o pior caso;
10 — k_B·T·ln2 ≈ 2,85×10⁻²¹ J, e estamos ~30.000 vezes acima; 11 — porque a evolução
unitária da mecânica quântica é reversível; 12 — porque a constante escondida no O grande é
astronômica.)*
