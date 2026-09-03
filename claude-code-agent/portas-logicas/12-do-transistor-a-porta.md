# 12 · Do transistor à porta — a mecânica interna

**Nível:** intermediário · **Data:** 14/08/2026

Aqui a caixa-preta é aberta. Ao final você saberá, transistor por transistor, por que
NAND custa 4 e XOR custa 12, o que significa "atraso de propagação", e por que existe um
limite para quantas portas se pode ligar numa saída.

Você **não** precisa de eletrônica prévia. O mínimo necessário é construído aqui.

---

## 1. O transistor, no nível de detalhe que basta

Um **transistor MOSFET** é uma chave controlada por tensão. Três terminais:

```
            porta (gate)
               │
        ┌──────┴──────┐
   ─────┤             ├─────
    fonte           dreno
   (source)         (drain)
```

- **Fonte** e **dreno**: o caminho por onde a corrente pode passar.
- **Porta** (*gate*): o controle. Uma tensão aqui abre ou fecha o caminho — **sem contato
  elétrico com ele**, porque há uma camada isolante de óxido no meio. Daí o nome:
  Metal-Óxido-Semicondutor.

> **Cuidado com a palavra "porta".** Em português, *porta lógica* (logic **gate**) e
> *porta do transistor* (transistor **gate**) usam a mesma palavra para coisas diferentes.
> Em inglês são as duas *gate*, o que também confunde. Neste arquivo, sempre digo
> "porta do transistor" quando for o terminal.

Existem dois tipos, e eles são espelhos um do outro:

| Tipo | Conduz quando a porta está em… | Bom para puxar a saída para… | Símbolo mnemônico |
|---|---|---|---|
| **NMOS** (tipo N) | **1** (tensão alta) | **0** (terra) | sem bolinha |
| **PMOS** (tipo P) | **0** (tensão baixa) | **1** (VDD) | **com bolinha** na porta |

**Por que cada um só é bom para um lado?** Por física do dispositivo: um NMOS conduz bem
quando precisa transmitir um 0, mas transmite um 1 "fraco" (perde uma tensão de limiar no
caminho). O PMOS é o contrário. Usar cada um só para o lado em que é forte é o princípio
do CMOS — o "C" é de **complementar**.

---

## 2. A regra de construção do CMOS

Toda porta CMOS estática tem exatamente duas redes de transistores:

```
              VDD (o "1")
               │
        ┌──────┴──────┐
        │  REDE PMOS  │   ← puxa a saída para 1 (rede pull-up)
        └──────┬──────┘
               ├──────────► SAÍDA
        ┌──────┴──────┐
        │  REDE NMOS  │   ← puxa a saída para 0 (rede pull-down)
        └──────┬──────┘
               │
              GND (o "0")
```

**As três regras, e delas sai tudo:**

1. As duas redes são **complementares**: quando uma conduz, a outra não. Nunca as duas.
2. **Série no NMOS ⇒ paralelo no PMOS**, e vice-versa.
3. A saída é sempre **invertida** em relação à função das entradas na rede NMOS.

A regra 3 é a razão pela qual NAND e NOR são as portas naturais do CMOS, e AND e OR são as
portas caras. É um fato de física que determina economia.

---

## 3. Construindo cada porta, transistor por transistor

### 3.1 Inversor (NOT) — 2 transistores

```
        VDD
         │
       ──┤ PMOS  (conduz quando A=0)
    A ───┤
       ──┤ NMOS  (conduz quando A=1)
         │
        GND         saída no meio
```

| A | PMOS | NMOS | Saída |
|---|---|---|---|
| 0 | conduz | corta | **1** (ligada ao VDD) |
| 1 | corta | conduz | **0** (ligada ao GND) |

Dois transistores. É a porta mais barata que existe.

### 3.2 NAND de 2 entradas — 4 transistores

```
             VDD
        ┌─────┴─────┐
      ──┤P(A)     P(B)├──      PMOS em PARALELO
        └─────┬─────┘
              ├──────────► SAÍDA
            ──┤ N(A)           NMOS em SÉRIE
            ──┤ N(B)
              │
             GND
```

A saída só é puxada para 0 quando **A e B** conduzem os dois NMOS em série — ou seja,
quando ambos são 1. Em qualquer outro caso, ao menos um PMOS em paralelo puxa para 1.

Isso é exatamente `¬(A·B)` = **NAND**, com **4 transistores**.

### 3.3 NOR de 2 entradas — 4 transistores

O espelho: PMOS em série, NMOS em paralelo. Também 4 transistores.

**Detalhe prático que separa teoria de silício:** apesar de terem a mesma contagem, o
**NAND é preferido**. Motivo: transistores PMOS conduzem pior que NMOS (a mobilidade das
lacunas é ~2 a 3× menor que a dos elétrons), então empilhá-los em série — o que o NOR faz —
custa caro em velocidade ou em área. O NAND empilha os NMOS, que são os bons. Essa
assimetria física é a razão de bibliotecas de células reais terem NAND por padrão.

### 3.4 AND — 6 transistores

Não existe AND CMOS estático "nativo". Faz-se **NAND (4) + inversor (2) = 6**.

E aqui está o número mais consequente deste arquivo: **AND custa 50% mais que NAND, e é
mais lento**, porque tem um estágio a mais. Todo projeto otimizado empurra as inversões
para onde elas somem — a técnica se chama "propagação de bolhas" e é De Morgan aplicado
ao desenho.

### 3.5 OR — 6 transistores

NOR (4) + inversor (2).

### 3.6 XOR — 8 a 12 transistores

Não há arranjo série-paralelo simples que produza XOR. As opções reais:

| Implementação | Transistores | Observação |
|---|---|---|
| Portas de transmissão (*transmission gates*) | 8 | compacta; a mais usada |
| Estática pura (a partir de NANDs) | 12–16 | mais robusta |
| Lógica passiva (*pass transistor*) | 6 | menor, mas o sinal degrada — precisa de reforço |

**Consequência prática:** XOR é a porta cara. E o somador é feito de XORs. É por isso que
a soma é uma das operações mais caras em área e atraso do caminho de dados, e por isso que
há 70 anos de pesquisa em somadores rápidos ([`20`](20-circuitos-combinacionais.md)).

### 3.7 A tabela que resume tudo

| Porta | Transistores CMOS | NANDs equivalentes | Comentário |
|---|---|---|---|
| NOT | 2 | 1 | a mais barata |
| **NAND** | **4** | 1 | **a porta natural do CMOS** |
| NOR | 4 | 4 | mesma contagem, mais lenta (PMOS em série) |
| AND | 6 | 2 | NAND + inversor |
| OR | 6 | 3 | NOR + inversor |
| XOR | 8–12 | 4 | sem forma série-paralelo direta |
| XNOR | 8–12 | 5 | idem |
| Flip-flop D | ~20–26 | 9 | a peça de memória |
| Célula SRAM (1 bit) | **6** | — | **não é porta**: armazena, não computa |

Guarde a última linha. Ela é a chave do
[`50-quantas-portas-tem-um-computador.md`](50-quantas-portas-tem-um-computador.md).

---

## 4. Por que uma porta demora — atraso de propagação

A álgebra booleana é instantânea. O silício não.

**Definição.** O **atraso de propagação** (t_pd) é o tempo entre a mudança da entrada e a
mudança correspondente da saída, medido tipicamente a 50% da excursão de tensão.

**De onde vem o atraso?** De uma coisa só: **carregar capacitâncias**.

A porta de cada transistor é, fisicamente, um capacitor (duas placas condutoras separadas
por óxido). Para mudar a saída de 0 para 1, os transistores precisam **encher de carga**
todos os capacitores ligados a ela: as portas dos transistores seguintes, mais a
capacitância do próprio fio.

O modelo mais simples que ainda é útil:

```
t_pd ≈ R_on × C_carga
```

- `R_on` — resistência do transistor quando conduz. Menor se o transistor for mais largo.
- `C_carga` — capacitância total pendurada na saída. Cresce com o número de portas ligadas.

**Consequências diretas, e todas contraintuitivas para quem vem de software:**

1. Uma porta **não** tem atraso fixo. O mesmo NAND é mais lento se alimentar 10 portas do
   que se alimentar 1.
2. Transistores mais largos são mais rápidos (menor R) **e** mais lentos para quem os
   alimenta (maior C). Dimensionar isso é um problema de otimização real, chamado
   *gate sizing*.
3. **Fio longo é lento.** Em chips modernos, o atraso de interconexão frequentemente supera
   o das portas. A partir de ~130 nm, o fio virou o gargalo — não o transistor.

### 4.1 Fan-out — quantas portas cabem numa saída

**Definição.** **Fan-out** é o número de entradas que uma saída alimenta.

Cada entrada acrescenta capacitância. Dobrar o fan-out ≈ dobrar o atraso. Regras práticas
da indústria:

| Contexto | Fan-out típico máximo |
|---|---|
| Biblioteca de células ASIC | 4 a 8 |
| CI 74HC (bancada) | ~10 entradas do mesmo tipo |
| Sinal de relógio de um chip inteiro | milhares — por isso existe a **árvore de relógio** |

Quando o fan-out é inevitável (como no relógio, que precisa chegar a todos os flip-flops),
a solução é uma **árvore de buffers**: em vez de uma saída alimentar 1.000 entradas, ela
alimenta 4 buffers, que alimentam 4 cada, e assim por diante. A árvore de relógio de um
processador moderno pode consumir 20 a 40% da potência total do chip — só para entregar o
mesmo sinal em toda parte, no mesmo instante.

### 4.2 Profundidade lógica — o que realmente determina a velocidade

O atraso total de um circuito combinacional é o do **caminho crítico**: a sequência mais
longa de portas entre uma entrada e uma saída.

```
Cadeia:  A─[&]─[&]─[&]─[&]─[&]─[&]─[&]─► saída       7 portas, profundidade 7
Árvore:  A─┬[&]┐                                     7 portas, profundidade 3
           └[&]┴[&]┐
                   └[&]─► saída
```

**Mesma quantidade de portas, menos da metade do atraso.** É por isso que este curso
insiste em montar tudo em árvore. Essa distinção entre **tamanho** (número de portas) e
**profundidade** (atraso) vira, no [`60-teoria-avancada.md`](60-teoria-avancada.md), uma
divisão inteira de classes de complexidade.

---

## 5. Consumo de energia — de onde vem o calor

A potência de um circuito CMOS tem três parcelas:

```
P_total = P_dinâmica + P_curto-circuito + P_estática
```

### 5.1 Potência dinâmica — o custo de mudar de ideia

```
P_dinâmica = α × C × V² × f
```

| Símbolo | Significado | Como reduzir |
|---|---|---|
| α | atividade: fração de ciclos em que o sinal muda | desligar blocos ociosos (*clock gating*) |
| C | capacitância total comutada | células menores, fios mais curtos |
| **V** | tensão de alimentação | **reduzir V — efeito quadrático!** |
| f | frequência de relógio | reduzir f |

O **V²** é o detalhe mais importante da eletrônica digital moderna. Cortar a tensão pela
metade reduz a potência dinâmica a **um quarto**. Foi por isso que a tensão dos chips caiu
de 5 V (1990) para ~0,7 V (2026). E é por isso que essa fonte de economia está se
esgotando: abaixo de ~0,5 V o transistor deixa de chavear de forma confiável, porque a
tensão de limiar não escala junto.

### 5.2 Potência estática — a fuga

Idealmente, um CMOS parado não consome nada. Na prática, transistores muito pequenos
**vazam**: a camada de óxido é tão fina (poucos átomos) que elétrons a atravessam por
tunelamento quântico, e o canal conduz um pouco mesmo desligado.

Essa fuga é a causa direta da morte da escala de Dennard
([`11-historia.md`](11-historia.md), §8) e a razão de existirem o *power gating* (cortar a
alimentação de blocos inteiros) e o **silício escuro**.

### 5.3 A ordem de grandeza que dá perspectiva

Uma comutação de porta em 2026 custa da ordem de **0,1 femtojoule** (10⁻¹⁶ J).
Um processador de 5 GHz com 1 bilhão de portas, se todas comutassem a cada ciclo,
consumiria centenas de quilowatts. Ele consome ~100 W porque **α é pequeno**: a esmagadora
maioria das portas não muda de estado na maioria dos ciclos.

**Um computador funciona porque quase todo ele está parado quase o tempo todo.**

---

## 6. Níveis lógicos e margem de ruído

0 e 1 são idealizações. Fisicamente há tensões, e é preciso decidir onde uma vira a outra.

```
   VDD ┬─────────────────  ← 1 garantido
       │   V_OH  (saída alta mínima)
       ├─────────────────
       │   V_IH  (entrada alta mínima)   ─┐ margem de ruído alta
       ├─────────────────                 │
       │   ZONA PROIBIDA — nenhum         │  ← nenhum circuito deve
       │   circuito deve ficar aqui       │     ficar aqui em repouso
       ├─────────────────                 │
       │   V_IL  (entrada baixa máxima)  ─┘ margem de ruído baixa
       ├─────────────────
       │   V_OL  (saída baixa máxima)
   GND ┴─────────────────  ← 0 garantido
```

**Definição.** A **margem de ruído** é a diferença entre o que uma saída garante produzir e
o que uma entrada garante aceitar. É a folga que o circuito tem para sobreviver a ruído
elétrico, queda em fio, acoplamento entre trilhas e interferência.

É essa margem — e não a matemática — que faz o digital ser confiável. Um sinal analógico
degrada a cada estágio, acumulando erro. Um sinal digital é **regenerado** a cada porta:
qualquer coisa acima de V_IH vira um 1 limpo na saída. É por isso que se pode encadear um
bilhão de portas sem que o sinal se perca, e por que música digital copiada mil vezes é
idêntica à original.

**A propriedade que torna computação possível não é a lógica; é a regeneração do sinal.**
Esta é, na minha opinião profissional, a ideia mais subestimada de toda a eletrônica digital.

---

## 7. Famílias lógicas — o que a letra do CI significa

| Família | Década | Tensão | Consumo estático | Atraso típico | Situação em 2026 |
|---|---|---|---|---|---|
| RTL, DTL | 1960 | 3–5 V | alto | ~50 ns | extintas |
| **TTL** (74xx) | 1964 | 5 V | alto | 10 ns | obsoleta |
| **TTL LS** (74LSxx) | 1976 | 5 V | médio | 10 ns | legado |
| **ECL** | 1960–90 | −5 V | altíssimo | **1 ns** | extinta (usada em supercomputadores) |
| **CMOS HC** (74HCxx) | 1982 | 2–6 V | ~0 | 8 ns | **padrão de bancada** |
| **CMOS LVC** | 1990s | 1,65–3,6 V | ~0 | 4 ns | padrão em 3,3 V |
| CMOS em chip (2 nm) | 2026 | ~0,7 V | fuga relevante | ~5 ps | estado da arte |

A ECL merece uma nota: era **dez vezes mais rápida** que o TTL e foi a tecnologia dos
supercomputadores Cray. Perdeu porque consumia corrente constante, independentemente de
estar comutando — inviável em alta densidade. **É o mesmo enredo do CMOS contra o bipolar,
que se repete a cada geração: a tecnologia mais rápida perde para a mais eficiente assim
que a densidade cresce.**

---

## 8. Glitches — o que a álgebra não vê

Considere `f = a·b + ¬a·c`, com `b = c = 1`. Algebricamente, `f = a + ¬a = 1`, sempre.
A saída **nunca deveria mudar**.

Na prática, quando `a` cai de 1 para 0:
- o termo `a·b` desliga imediatamente;
- o termo `¬a·c` só liga **depois** que o inversor de `a` responder.

Nesse intervalo de poucos picossegundos, os dois termos estão em 0 e a saída **cai para 0**.
É um **glitch**: um pulso espúrio que a álgebra booleana não prevê.

```
  a  ──┐____
       
  f  ─────‾‾‾  esperado
  f  ──┐_┌───  real: um pulso para baixo
```

**Por que isso importa:**

- Se um flip-flop capturar durante o glitch, ele guarda o valor errado — bug intermitente,
  o pior tipo.
- Glitches consomem energia (cada transição custa `C·V²`), e em circuitos aritméticos
  podem responder por 10–20% do consumo dinâmico.
- Em lógica assíncrona, um glitch pode disparar um evento inteiro por engano.

**Soluções:** projeto síncrono (só olhar as saídas depois que tudo assentou — a solução
dominante), acrescentar o **termo de consenso** ao circuito (`+ b·c` no exemplo, que é
logicamente redundante mas elimina o glitch), ou lógica insensível a atraso.

O termo de consenso é uma bela ironia da engenharia: **acrescentar uma porta logicamente
inútil para corrigir um defeito que a lógica não enxerga.**

---

## 9. Além do CMOS estático

Nem todo circuito real segue as regras da seção 2:

| Estilo | Como funciona | Onde se usa |
|---|---|---|
| **Lógica de transmissão** | transistores passam o sinal em vez de acionar VDD/GND | XOR, mux — economiza área |
| **Lógica dinâmica (domino)** | pré-carrega a saída e depois a descarrega conforme a entrada | caminhos críticos de CPUs de alto desempenho |
| **Lógica assíncrona** | sem relógio; sinais de "pronto" | baixa potência, segurança contra ataques de canal lateral |
| **Lógica de limiar** | soma ponderada com limiar | aceleradores de rede neural |
| **Lógica reversível/adiabática** | não apaga informação; recupera energia | pesquisa; ver [`60`](60-teoria-avancada.md) |

Todos calculam as mesmas funções booleanas. A álgebra é a mesma; a física, e portanto a
economia, é diferente.

---

## Autoteste

1. Quantos transistores tem um inversor CMOS? E um NAND de 2 entradas? E um AND?
2. Por que não existe uma porta AND CMOS estática "nativa"?
3. Por que se prefere NAND a NOR, se ambos custam 4 transistores?
4. De onde vem, fisicamente, o atraso de propagação?
5. O que é fan-out, e por que ele afeta a velocidade?
6. Sete portas em cadeia e sete em árvore têm o mesmo custo. O que muda?
7. Na fórmula da potência dinâmica, qual variável tem efeito quadrático, e o que isso causou historicamente?
8. Por que um chip com 1 bilhão de portas não consome centenas de quilowatts?
9. O que é margem de ruído, e por que ela é a propriedade que torna a computação digital possível?
10. O que é um glitch, e por que a álgebra booleana não o prevê?
11. Por que a ECL, dez vezes mais rápida, perdeu para o CMOS?
12. Quantos transistores tem uma célula SRAM de 1 bit, e por que isso importa para contar portas?

*(Respostas: 1 — 2, 4 e 6; 2 — o CMOS estático é naturalmente inversor, então AND é
NAND+inversor; 3 — o NOR empilha PMOS em série, e o PMOS conduz pior; 4 — de carregar as
capacitâncias das portas seguintes e dos fios; 5 — número de entradas alimentadas por uma
saída, cada uma acrescenta capacitância; 6 — a profundidade cai de 7 para 3, e é ela que
determina o atraso; 7 — a tensão V, o que levou a tensões caindo de 5 V para ~0,7 V;
8 — porque a atividade α é baixíssima: quase tudo está parado quase sempre; 9 — a folga
entre o que a saída garante e o que a entrada aceita, que permite regenerar o sinal a cada
porta; 10 — um pulso espúrio causado por caminhos com atrasos diferentes, invisível para a
álgebra porque ela não modela tempo; 11 — consumia corrente constante, inviável em alta
densidade; 12 — 6 transistores, e ela não é porta lógica, o que invalida dividir
transistores por 4 para contar portas.)*
