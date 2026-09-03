# 01 · O problema científico — o que se quer descobrir, e por quê

`Nível: iniciante` · `Atualizado em: 19/08/2026`

Antes de qualquer fórmula. Este arquivo responde à pergunta que você fez e que
quase nenhum material técnico responde: **para que serve isso, afinal?**

---

## 1 · O que é, de fato, um "sinal do espaço"

Quando um radiotelescópio aponta para o céu, o que chega à antena é uma onda
eletromagnética — a mesma coisa física que o sinal de uma rádio FM, só que
vinda de muito mais longe e muito mais fraca.

A grandeza que se mede chama-se **densidade de fluxo**, e a unidade é o
**jansky**: 1 Jy = 10⁻²⁶ W·m⁻²·Hz⁻¹.

Para dar escala a esse número:

| Fonte | Fluxo aproximado |
|---|---|
| Uma emissora de FM local | ~10¹⁵ Jy |
| O Sol calmo em 1 GHz | ~10⁶ Jy |
| Cassiopeia A (resto de supernova, a mais brilhante do céu) | ~2 000 Jy |
| Um pulsar típico | 0,1 a 10 mJy |
| Uma galáxia distante em rádio | ~0,01 mJy |
| Sinal da Voyager 1 na antena de 70 m | ~10⁻⁷ Jy |

**Toda a energia de rádio já coletada por todos os radiotelescópios da história,
somada, é comparável à energia de um floco de neve caindo.** A frase é uma
estimativa repetida na área desde os anos 1970 e serve ao propósito: a ordem de
grandeza do problema é essa.

E a dificuldade real não é o sinal ser fraco — é ele ser **mais fraco que o
ruído do próprio instrumento**. Amplificar não adianta: amplifica o ruído junto.

---

## 2 · A ideia que resolve: integração coerente

Todo este projeto é uma variação de **um único truque**, e vale entendê-lo antes
de qualquer código.

Suponha que você tem N medidas do mesmo sinal, cada uma afogada em ruído:

```
medida_i = sinal + ruído_i
```

Some as N medidas:

- O **sinal** é o mesmo em todas. Somando N vezes, ele fica **N vezes maior**.
- O **ruído** é diferente e independente em cada uma. Ruídos independentes não
  somam em amplitude: somam em **variância**. A amplitude resultante cresce
  com **√N**.

Logo, a razão sinal-ruído cresce com **N/√N = √N**.

```
   N = 1        N = 100                N = 10 000
   ▁▂▁▃▂▁       ▁▂▃▄▅▄▃▂▁              ▁▂▃▅█▅▃▂▁
   (nada)       (talvez algo?)         (inequívoco)
   SNR = 1      SNR = 10               SNR = 100
```

**Este é o motivo de tudo mais.** Cada um dos quatro pipelines deste projeto é
uma forma diferente de conseguir muitas medidas do mesmo sinal:

| Pipeline | O que se soma | Ganho |
|---|---|---|
| Radiômetro | amostras no tempo | √(B·τ) |
| Dedispersão | canais de frequência | √n_canais |
| Folding de pulsar | rotações da estrela | √n_giros |
| Correlação PN | chips do código | √N_chips |

E há um preço, sempre o mesmo: para somar coerentemente, você precisa **saber
como alinhar** as medidas. Alinhar exige conhecer o atraso (dispersão), o
período (pulsar), a fase (Doppler). Quando não se conhece, **procura-se** — e é
daí que vem todo o custo computacional da astronomia moderna.

---

## 3 · Os quatro problemas, e a ciência de cada um

### 3.1 · Radiômetro: quanto tempo de telescópio comprar

**A pergunta prática.** Você quer observar uma fonte que estima ter 5 mK de
temperatura de antena. Tem um receptor com T_sys = 30 K e 100 MHz de banda.
Quantas horas de telescópio pedir no edital?

**Por que isso é ciência, e não engenharia.** Tempo em telescópio grande é o
recurso mais disputado da astronomia. O ALMA e o VLA aprovam uma fração pequena
das propostas; James Webb é ainda mais concorrido. Uma proposta que subestima o
tempo necessário produz uma não detecção inútil; uma que superestima é rejeitada
por desperdício. **A equação do radiômetro é o instrumento de decisão.**

**O que se descobre com isso.** Levantamentos de céu (surveys) inteiros são
projetados por esta equação: quanto tempo por apontamento, quantos apontamentos,
que sensibilidade final. Foi assim que se planejou o mapeamento da linha de
21 cm do hidrogênio neutro, que traça a estrutura da Via Láctea e, em
levantamentos de intensidade como o brasileiro **BINGO** (em construção na
Paraíba), a expansão do universo.

### 3.2 · Dispersão: medir a distância de algo que você não vê

**A pergunta prática.** Um pulso de rádio chegou. A que distância está a fonte?

**O truque.** O espaço interestelar é um plasma tênue. Ondas de rádio de
frequência menor viajam um pouco mais devagar nele. Um pulso emitido
simultaneamente em toda a banda chega **varrido no tempo**: primeiro os agudos,
depois os graves. Medindo esse atraso, mede-se a **coluna de elétrons** no
caminho — o DM. Com um modelo da distribuição de elétrons na Galáxia (NE2001,
YMW16), o DM vira distância.

**O que se descobriu com isso — e é grande.** Em 2007 detectou-se o primeiro
*fast radio burst*: um pulso de milissegundos com DM muito maior que qualquer
coisa que a Via Láctea poderia produzir. A conclusão foi inescapável: **a fonte
é extragaláctica**. Hoje as FRBs são um dos campos mais ativos da astrofísica, e
já servem para "pesar" o gás difuso entre galáxias — o problema dos **bárions
desaparecidos**, resolvido em 2020 com FRBs justamente porque o DM mede matéria
que nenhum telescópio óptico consegue ver.

Um atraso de chegada virou um censo da matéria do universo.

### 3.3 · Pulsares: relógios para testar a gravidade

**O objeto.** Uma estrela de nêutrons: mais massa que o Sol comprimida em ~20 km,
girando até 716 vezes por segundo, com um feixe de rádio que varre o espaço.

**A pergunta prática.** Cada pulso é invisível — some no ruído. Como detectar?

**A resposta.** Somar milhares de rotações alinhadas pelo período (folding).

**O que se descobriu com isso:**

- **Nobel de 1993** (Hulse e Taylor): o pulsar binário PSR B1913+16 perde energia
  orbital exatamente na taxa que a Relatividade Geral prevê para emissão de ondas
  gravitacionais. Foi a primeira evidência — indireta, mas decisiva — de que
  ondas gravitacionais existem, 40 anos antes do LIGO detectá-las diretamente.
- **Evidência de um fundo de ondas gravitacionais (2023)**: NANOGrav, EPTA, PPTA
  e CPTA usaram redes de pulsares de milissegundo como um detector do tamanho da
  Galáxia. Ondas gravitacionais de período de anos — provavelmente de pares de
  buracos negros supermassivos — alteram minuciosamente o tempo de chegada dos
  pulsos, de forma correlacionada entre pulsares em direções diferentes.
- **Navegação autônoma no espaço profundo (XNAV)**: a NASA demonstrou em 2018,
  com o instrumento NICER/SEXTANT na Estação Espacial, posicionamento usando
  pulsares de raios X como faróis — um "GPS galáctico" que não depende da Terra.
- **Física de matéria em densidade nuclear**: a massa máxima de estrelas de
  nêutrons medida por timing restringe a equação de estado da matéria nuclear,
  algo que nenhum acelerador na Terra consegue reproduzir.

### 3.4 · Enlace de espaço profundo: conversar com uma sonda e pesar um planeta

**A pergunta prática.** A Voyager 1 está a mais de 24 bilhões de km e transmite
com ~20 W. Como se recebe isso?

**A resposta.** Antena de 70 m, receptor criogênico, **código pseudoaleatório**
correlacionado, e rastreamento de **Doppler**.

**A virada conceitual.** O Doppler parece um problema — desloca a portadora e
dificulta o travamento. Mas ele **é o instrumento principal de navegação e de
ciência gravitacional**:

- Mede a velocidade radial da sonda com precisão de fração de mm/s.
- Como a gravidade dos corpos altera essa velocidade, o Doppler **pesa** planetas
  e luas. Foi assim que se inferiu o oceano subsuperficial de Europa e a
  estrutura interna de Ganimedes.
- A missão **GRAIL** (2011–2012) mapeou o campo gravitacional da Lua com duas
  naves medindo a distância entre si por rádio.
- A **Cassini** testou a Relatividade Geral em 2002 pelo atraso de Shapiro,
  confirmando o parâmetro γ = 1 com incerteza de 2,3×10⁻⁵ — um dos testes mais
  precisos já feitos.
- A **anomalia da Pioneer**, que por 20 anos alimentou propostas de gravidade
  modificada, foi detectada por análise Doppler e **explicada** em 2012 pela
  mesma técnica: radiação térmica anisotrópica da própria sonda. Processamento
  de sinais fechando um debate de física fundamental.

E o mesmo princípio de correlação com código PN é o que faz **o GPS do seu
celular funcionar**, com o sinal do satélite ~20 dB abaixo do ruído térmico.

---

## 4 · Por que esse conjunto e não outro

Os quatro problemas foram escolhidos porque, juntos, cobrem o ciclo completo de
um instrumento científico:

```
   MEDIR O PISO         →  radiômetro     (o que é ruído?)
   CORRIGIR O MEIO      →  dispersão      (o que o caminho fez com o sinal?)
   EXTRAIR O SINAL      →  folding        (como somar coerentemente?)
   DECIDIR              →  estatística    (isso é descoberta ou acaso?)
   COMUNICAR            →  enlace         (como fechar o elo com a máquina?)
```

E todos têm **verdade conhecida**: como sintetizamos os dados, sabemos a resposta
certa e podemos verificar cada etapa contra ela. Em pesquisa isso se chama
**teste com injeção de sinal**, e é padrão obrigatório em qualquer colaboração
séria: antes de confiar num pipeline, injeta-se um sinal falso de propriedades
conhecidas e verifica-se se o pipeline o recupera. O LIGO faz isso com
*blind injections* — inclusive sem contar à própria equipe de análise.

---

## 5 · O que este projeto **não** faz, e é honesto declarar

| Não faz | Por quê | Onde se estuda |
|---|---|---|
| Dedispersão **coerente** | exige dados brutos em tensão (voltagem), volume enorme | `dispersao.py`, docstring |
| Excisão de RFI real | interferência real não é gaussiana; exige heurísticas e dados reais | `05-como-as-instituicoes-fazem.md` |
| Timing de precisão (ns) | exige efemérides, correção baricêntrica, modelo relativístico | TEMPO2, PINT |
| Interferometria / VLBI | exige duas ou mais antenas e correlacionador | literatura de síntese de abertura |
| Correção de erro (LDPC, turbo) | é o elo seguinte do enlace | padrões CCSDS |
| Ruído não gaussiano | o modelo assume gaussiano; a realidade tem caudas pesadas | `deteccao.py`, seção de avisos |

Nenhuma dessas ausências invalida o que está aqui — mas passar de um exercício
para um instrumento real significa, em grande medida, atacar essa lista.

---

## Autoteste

1. Por que amplificar não resolve o problema do sinal fraco?
2. Explique, sem fórmula, por que a SNR cresce com √N e não com N.
3. O que os quatro pipelines têm em comum, no fundo?
4. Como um atraso de chegada vira uma medida de distância?
5. Qual foi a evidência que rendeu o Nobel de 1993, e o que ela mediu?
6. Cite dois resultados científicos obtidos com rastreamento Doppler.
7. O que é um teste com injeção de sinal e por que colaborações sérias o fazem?
8. Por que a equação do radiômetro é um instrumento de decisão orçamentária?
