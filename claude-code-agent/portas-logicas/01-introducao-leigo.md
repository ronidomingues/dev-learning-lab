# 01 · O que é uma porta lógica — para quem nunca ouviu falar

**Nível:** iniciante absoluto · **Pré-requisito:** nenhum · **Data:** 14/08/2026

Neste arquivo não há uma fórmula sequer. Nenhum jargão aparece sem explicação.
Se em algum momento você ler uma palavra que não foi explicada antes, isso é um defeito
do texto, não seu.

---

## 1. Comece por um interruptor de luz

Você tem uma lâmpada e um interruptor. Duas situações possíveis: **aceso** ou **apagado**.
Não existe meio-aceso nesse mundo. É um mundo de duas opções.

Guarde essa ideia, porque ela é o computador inteiro. Não é uma simplificação didática —
é literalmente assim que a máquina na sua mesa funciona. Tudo que ela faz, ela faz
com bilhões de coisas que só sabem estar **ligadas** ou **desligadas**.

Damos nomes curtos a esses dois estados:

| Estado físico | Nome comum | Nome numérico | Nome lógico |
|---|---|---|---|
| Sem tensão elétrica | desligado | **0** | falso |
| Com tensão elétrica | ligado | **1** | verdadeiro |

São quatro nomes para a mesma coisa. Vou usar **0** e **1** daqui em diante porque é mais curto.

---

## 2. Agora dois interruptores

Coloque **dois** interruptores no caminho da mesma lâmpada, um em seguida do outro:

```
  [fonte] ──── /A ──── /B ──── (lâmpada) ──── [terra]
```

A corrente só chega na lâmpada se **os dois** estiverem fechados. Se A estiver fechado
mas B aberto, a corrente para em B. A lâmpada acende **só quando A e B estão ligados**.

Isso é uma **porta E** (em inglês, *AND gate*). É uma peça que olha para duas entradas
e responde uma saída, seguindo uma regra fixa: *"só digo 1 se as duas entradas forem 1"*.

A regra inteira cabe numa tabelinha. Chamamos isso de **tabela-verdade** — uma lista de
todas as combinações possíveis de entrada e o que a peça responde em cada uma:

| A | B | saída (A E B) |
|---|---|---|
| 0 | 0 | 0 |
| 0 | 1 | 0 |
| 1 | 0 | 0 |
| 1 | 1 | **1** |

Quatro linhas. É tudo que existe para saber sobre uma porta E. Não há nada escondido.

---

## 3. Mude a ligação e você tem outra peça

Coloque os dois interruptores **lado a lado** em vez de em sequência — dois caminhos
paralelos para a mesma lâmpada:

```
              ┌── /A ──┐
  [fonte] ────┤        ├──── (lâmpada) ──── [terra]
              └── /B ──┘
```

Agora basta **um** dos dois estar fechado para a corrente passar. A lâmpada acende
se A **ou** B estiver ligado (ou os dois).

Isso é uma **porta OU** (*OR gate*):

| A | B | saída (A OU B) |
|---|---|---|
| 0 | 0 | 0 |
| 0 | 1 | **1** |
| 1 | 0 | **1** |
| 1 | 1 | **1** |

> **Cuidado com o "ou" do português.** No dia a dia, "café ou chá" costuma significar
> *um dos dois, não os dois*. Na lógica, "ou" inclui o caso dos dois. O "ou" exclusivo
> (um **ou** o outro, mas não ambos) também existe e ganhou peça própria — a **porta XOR**,
> que aparece na seção 5. Essa diferença é a primeira armadilha da área.

---

## 4. A peça que discorda de você

A terceira peça básica tem uma entrada só, e faz a coisa mais simples possível:
**responde o contrário do que recebe**.

| A | saída (NÃO A) |
|---|---|
| 0 | **1** |
| 1 | **0** |

É a **porta NÃO** (*NOT gate*, também chamada de **inversor**). Parece inútil. Não é:
sem ela, você não consegue construir a maior parte das coisas interessantes, porque
E e OU sozinhos só sabem "empilhar" condições, nunca negá-las.

---

## 5. As sete peças que ganharam nome

Combinando essas três ideias — e, ou, não — chegamos ao conjunto que a engenharia
adotou. **São sete peças com nome e símbolo próprios:**

| Nº | Nome | Lê-se | Responde 1 quando… | Analogia do mundo real |
|---|---|---|---|---|
| 1 | **NOT** (NÃO) | "não A" | a entrada é 0 | o teimoso: diz sempre o contrário |
| 2 | **AND** (E) | "A e B" | **todas** as entradas são 1 | duas chaves para abrir o cofre |
| 3 | **OR** (OU) | "A ou B" | **pelo menos uma** entrada é 1 | duas portas para entrar na sala |
| 4 | **NAND** (NÃO-E) | "não (A e B)" | **não** são todas 1 | alarme: dispara se falta alguma condição |
| 5 | **NOR** (NÃO-OU) | "não (A ou B)" | **nenhuma** entrada é 1 | silêncio total: só 1 se ninguém falou |
| 6 | **XOR** (OU exclusivo) | "A ou B, mas não os dois" | as entradas são **diferentes** | detector de desacordo |
| 7 | **XNOR** (coincidência) | "A igual a B" | as entradas são **iguais** | comparador: "vocês concordam?" |

Repare que 4, 5 e 7 são apenas 2, 3 e 6 com um NÃO na saída. NAND é "AND negado".
NOR é "OR negado". XNOR é "XOR negado". Ou seja: são três ideias e suas três negações,
mais o inversor. Sete peças.

Há quem conte uma oitava, o **buffer**: uma peça que responde exatamente o que recebe
(1 vira 1, 0 vira 0). Parece a mais inútil de todas, e num sentido lógico é mesmo —
ela não decide nada. Serve para **reforçar o sinal elétrico**, como um repetidor num
cabo longo. É uma peça elétrica disfarçada de peça lógica.

### Os símbolos que você vai ver nos diagramas

```
        ┌──┐                  ___                     ___
  A ────┤  ╲                 ╱   ╲                   ╱   ╲
        │   ╲──── S     A ──┤     ╲──── S      A ──┤     ╲o── S
  B ────┤   ╱             B ─┤  ╱ ╱                B ─┤  ╱ ╱
        └──┘                 ‾‾‾                     ‾‾‾
        AND                   OR                     NOR
     (D reto)           (frente curva)        (curva + bolinha)
```

A regra visual é simples e vale sempre:

- **corpo em forma de D** (reto atrás) = AND
- **corpo em forma de escudo curvo** = OR
- **corpo triangular** = NOT ou buffer
- **bolinha (○) na saída** = "inverta o resultado". É ela que transforma AND em NAND,
  OR em NOR, XOR em XNOR, e buffer em NOT.

A bolinha se chama *bubble* e é a notação mais econômica da eletrônica: um único
círculo evita desenhar uma peça inteira.

---

## 6. Duas surpresas que mudam tudo

### Surpresa 1: uma peça só basta

Você não precisa das sete. **A porta NAND sozinha constrói todas as outras.** Todas.
E, por consequência, constrói o computador inteiro.

Veja como se faz um NÃO usando só um NAND — basta ligar a mesma entrada nos dois pinos:

| A | A | NAND(A, A) | é o mesmo que… |
|---|---|---|---|
| 0 | 0 | 1 | NÃO 0 = 1 ✔ |
| 1 | 1 | 0 | NÃO 1 = 0 ✔ |

Funcionou: NAND com as duas entradas juntas **é** um inversor.

E o E? É só inverter o NÃO-E: `A E B = NÃO(A NÃO-E B)`. Como já sabemos fazer NÃO com
NAND, temos AND com dois NANDs. O OU sai de três NANDs. O XOR, de quatro. Está tudo
provado com tabelas no [`10-fundamentos.md`](10-fundamentos.md) e implementado, em
código que roda, no [projeto-modelo](07-projeto-modelo/README.md).

Isso não é curiosidade acadêmica: fábricas de chip realmente preferem NAND, porque em
silício ela é a porta **mais barata e mais rápida** de construir. O porquê está no
[`12-do-transistor-a-porta.md`](12-do-transistor-a-porta.md).

O nome disso é **completude funcional**: um conjunto de peças com que se constrói
qualquer regra imaginável. NAND sozinha é funcionalmente completa. NOR sozinha também.
AND sozinha **não** é (sem inversor, você nunca produz um 1 a partir de dois 0s).

### Surpresa 2: um circuito consegue lembrar

Até aqui, toda peça responde imediatamente ao que entra, e esquece. Se você desligar
as entradas, a saída some. Um computador precisa **guardar** coisas.

O truque é quase indecente de tão simples: **ligue a saída de volta na entrada.**

```
        ┌──────────────────────┐
   R ──┤ NOR ├──┬───────────────┼── Q
        └─────┘  │              │
                 └──┐        ┌──┘
                    │        │
        ┌─────┐     │        │
   S ──┤ NOR ├──────┴────────┴──── Q̄  (Q barrado = o oposto de Q)
        └─────┘
```

Duas portas NOR, cada uma alimentando a outra. O resultado é um circuito que **se
sustenta**: se Q está em 1, ele mantém Q em 1 sozinho, mesmo depois que as entradas
voltam ao repouso. Ele **lembra** um bit.

Isso se chama **latch** (trava), e é a origem de toda a memória do computador —
registradores, cache, RAM. A ideia de que memória é feita de portas ligadas em círculo
é uma das mais bonitas da engenharia. O detalhe todo está no
[`30-circuitos-sequenciais.md`](30-circuitos-sequenciais.md).

---

## 7. Então, quantas portas tem um computador?

Agora a pergunta que trouxe você aqui. Ela precisa ser dividida.

### 7.1 Quantos *tipos* de porta?

**Sete tipos clássicos** (oito, se contar o buffer). Esse número é uma escolha humana,
não uma lei da natureza: são as combinações que ganharam nome porque são úteis.

Se quisermos ser exatos, com **duas entradas** de 0/1 existem exatamente
**16 regras possíveis** — 16 maneiras diferentes de preencher aquela coluna de saída
de quatro linhas. Sete delas viraram peças famosas. As outras nove são coisas como
"copie A e ignore B" ou "responda sempre 1", que existem mas raramente merecem um símbolo.
A conta que dá 16 está no [`10-fundamentos.md`](10-fundamentos.md).

### 7.2 Quantas *unidades* de porta?

Aqui os números ficam grandes. Ordens de grandeza reais:

| Máquina | Ano | Transistores | Portas (ordem de grandeza estimada) |
|---|---|---|---|
| Intel 4004 (primeiro microprocessador) | 1971 | 2.250 | ~500 a 800 |
| Intel 8086 (o avô do PC) | 1978 | 29.000 | ~10.000 |
| Pentium | 1993 | 3.100.000 | ~1 milhão |
| Apple M4 (chip de notebook) | 2024 | 28.000.000.000 | **~2,5 a 5 bilhões** |
| Nvidia Rubin (acelerador de IA) | 2026 | 336.000.000.000 | dezenas de bilhões |

*(Contagens de transistores: página "Transistor count" da Wikipédia, consultada em
14/08/2026 — fontes no rodapé. As contagens de portas são estimativas minhas e o método
está explicado no [`50`](50-quantas-portas-tem-um-computador.md).)*

Por que "estimativa" e não número exato? Duas razões honestas:

1. **Nem todo transistor é porta.** A maior parte do silício de um chip moderno é
   **memória cache**, feita de células de 6 transistores que **não são portas lógicas**.
   Dividir transistores por 4 e chamar de portas dá um número errado — geralmente
   errado por um fator de 3 a 5.
2. **Os fabricantes não publicam contagem de portas.** Publicam transistores, porque é
   número de marketing. Contagem de portas é informação interna de projeto.

Uma imagem que ajuda: se cada porta lógica do seu notebook fosse um grão de arroz,
você teria **cerca de 68 toneladas de arroz** — uns dois caminhões cheios. Tudo isso
cabe num quadrado de silício menor que uma unha e consome menos energia que uma lâmpada.

---

## 8. E para que elas servem?

Uma porta sozinha faz algo ridículo de simples. O poder vem de **quantas** e de
**como estão ligadas**. Estes são os seis trabalhos que elas fazem:

### 8.1 Decidir
Ligar condições: *"se o arquivo existe **e** o usuário tem permissão **e** o disco não
está cheio"*. Cada "e", cada "ou", cada "não" de qualquer programa acaba, lá no fundo,
executado por portas AND, OR e NOT reais.

### 8.2 Contar e somar
Somar dois bits é exatamente uma porta XOR (o resultado) mais uma porta AND (o "vai um").
Cinco portas fazem um **somador completo** de uma casa. Enfileire 64 deles e você soma
números de 64 bits — a operação mais executada de qualquer computador. Detalhes em
[`20-circuitos-combinacionais.md`](20-circuitos-combinacionais.md).

### 8.3 Escolher um caminho
Um **multiplexador** é um circuito de portas que funciona como um seletor de canais:
"entre estas 8 entradas, deixe passar a de número 5". É assim que o processador escolhe
qual registrador ler, e é uma das peças mais repetidas dentro de um chip.

### 8.4 Encontrar um endereço
Um **decodificador** transforma o número 5 em "acione exatamente a linha 5, e só ela".
É como a memória acha o byte que você pediu entre bilhões.

### 8.5 Lembrar
O latch da seção 6. Registradores, cache, RAM estática — memória é porta realimentada.

### 8.6 Vigiar e comparar
XOR responde "estes dois bits são diferentes?" — com isso se compara valores e se
detecta erro de transmissão (**bit de paridade**). Sua rede e seu SSD fazem isso o
tempo todo, e você nunca percebe.

Junte os seis, coloque um relógio para dar o compasso, e você tem uma máquina que
busca instruções, decide o que fazer, faz, guarda o resultado e repete —
bilhões de vezes por segundo. Isso é um computador, e não há nada além disso lá dentro.

---

## 9. O que **não** é uma porta lógica

Para fechar o conceito, delimite a fronteira:

| Não é porta | O que é de fato |
|---|---|
| Transistor | O **componente elétrico** com que se constrói a porta. 2 a 12 transistores por porta. |
| Célula de memória SRAM (6 transistores) | Armazenamento, não decisão. Não computa nada. |
| Porta USB, porta HDMI | Palavra "porta" em outro sentido (conector físico). Coincidência do português — em inglês são *port* e *gate*, palavras diferentes. |
| Porta de rede TCP 443 | Número de identificação de serviço. Nada a ver. |
| Porta quântica (qubit) | Existe, mas obedece a outras regras — é reversível e opera sobre estados contínuos. Ver [`65-estado-da-arte.md`](65-estado-da-arte.md). |

Essa confusão com "porta" no português é real e vale ter em mente ao pesquisar:
o termo em inglês é **logic gate**, e buscar por ele traz resultados muito melhores.

---

## 10. Para onde ir agora

- Quer **ver funcionando** sem instalar nada? → [`03-instalacao.md`](03-instalacao.md), seção "Sem instalar nada".
- Quer **entender a matemática** por trás? → [`10-fundamentos.md`](10-fundamentos.md).
- Quer o **número** com todas as contas? → [`50-quantas-portas-tem-um-computador.md`](50-quantas-portas-tem-um-computador.md).
- Quer **construir um computador**? → [`07-projeto-modelo/`](07-projeto-modelo/README.md).

---

## Autoteste

1. Descreva, sem usar tabela, quando uma porta AND responde 1.
2. Qual é a diferença entre o "ou" do português falado e o OR da lógica? Que peça representa o "ou" do português falado?
3. O que a bolinha (○) no símbolo de uma porta significa?
4. Mostre como fazer uma porta NOT usando uma única porta NAND.
5. Por que um circuito com realimentação consegue lembrar, e um sem realimentação não?
6. Por que não se pode estimar o número de portas de um chip dividindo os transistores por 4?
7. Cite três dos seis trabalhos que portas lógicas fazem num computador.
8. Um chip tem 28 bilhões de transistores. Isso significa 28 bilhões de portas? Justifique.

*(Respostas: 1 — quando todas as entradas são 1; 2 — o OR lógico inclui o caso "os dois", o "ou" falado costuma excluir; a peça é XOR; 3 — inverta a saída; 4 — ligue A nas duas entradas do NAND; 5 — porque a saída realimentada sustenta o próprio estado depois que a entrada some; 6 — porque a maioria dos transistores é memória SRAM, não porta; 7 — decidir, somar, escolher, endereçar, lembrar, comparar; 8 — não: transistores ≠ portas, e boa parte deles é memória.)*

---

### Fontes consultadas

- Wikipedia, *Transistor count* — https://en.wikipedia.org/wiki/Transistor_count — consultado em 14/08/2026 (Intel 4004: 2.250 · 8086: 29.000 · Pentium: 3.100.000 · Apple M4: 28 bilhões).
- Wikipedia/notícias de mercado sobre Nvidia Rubin (336 bilhões de transistores, 2026) — consultado em 14/08/2026.
