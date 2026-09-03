# 23 · Estimação e filtragem adaptativa — filtros que aprendem

`Nível: avançado` · `Medições feitas em: 19/08/2026`

Até aqui, você projetava o filtro. Aqui o filtro **se projeta sozinho**, ajustando
os coeficientes a partir dos próprios dados. É o que existe dentro do seu fone com
cancelamento de ruído, do viva-voz sem eco, do modem e do GPS.

Pré-requisito: [`22`](22-ruido-e-processos-estocasticos.md) e a §6 de
[`12-matematica-do-zero.md`](12-matematica-do-zero.md) (mínimos quadrados).

---

## 1 · O problema, em forma canônica

```
        d[n] (desejado)
             │
   x[n] ──►[ w ]──► y[n] ──►(−)──► e[n] (erro)
          filtro         ▲
          adaptativo     │
             ▲           │
             └───────────┘
              ajusta w para minimizar e
```

Quatro configurações cobrem quase tudo:

| Configuração | d[n] é | x[n] é | Aplicação |
|---|---|---|---|
| **Identificação de sistema** | saída do sistema desconhecido | entrada dele | cancelamento de eco, modelagem de sala |
| **Cancelamento de ruído** | sinal + ruído | referência do ruído | fone ANC, ECG fetal, cabine de avião |
| **Predição linear** | x[n] | x[n−1..n−p] | codificação de voz (LPC), compressão |
| **Equalização inversa** | sinal original (ou decisão) | sinal recebido | modem, canal de rádio, leitura de disco |

**A percepção que organiza tudo:** em todos os quatro, o objetivo é o mesmo —
achar o vetor **w** que minimiza E{e²}. Muda só o que se chama de d e de x.

---

## 2 · A solução ótima: filtro de Wiener

Minimizar E{e²} = E{(d − wᵀx)²} derivando em relação a w e igualando a zero dá
as **equações normais**:

```
R·w = p          →          w_opt = R⁻¹·p
```

- **R** = matriz de autocorrelação da entrada (L×L)
- **p** = correlação cruzada entre entrada e desejado

Isto é **exatamente** mínimos quadrados, e é a mesma equação da regressão linear.
Se você entendeu projeção sobre subespaço em álgebra linear, entendeu Wiener.

### Verificação: o filtro recupera um caminho desconhecido

Um ruído passa por um caminho acústico desconhecido (31 coeficientes) e vaza para
o microfone junto com a voz. O adaptativo tem só o ruído de referência.

```
coef estimados (5 primeiros):     [ 0.0015  0.0008 -0.0016 -0.0052 -0.0067]
caminho verdadeiro (5 primeiros): [ 0.0017  0.0012 -0.0009 -0.0042 -0.0054]
erro relativo do vetor completo:  0.035
potência do resíduo: -35.0 dB
```

(Saída real.) **3,5 % de erro no vetor inteiro**, e o resíduo é a própria voz —
que é o que se queria preservar. O filtro **descobriu a resposta ao impulso de um
sistema que nunca viu**, só observando entrada e saída.

### Por que não usar sempre a solução fechada

| Problema | Consequência |
|---|---|
| Precisa de R e p, que exigem estatísticas | raramente conhecidas *a priori* |
| Inverter L×L custa O(L³) | com L=1000 (eco acústico), inviável |
| Assume estacionaridade | o mundo muda: a pessoa se move, a sala muda |

Daí os algoritmos **adaptativos**: aproximam w_opt iterativamente, com custo baixo
e capacidade de acompanhar mudanças.

---

## 3 · LMS — o algoritmo mais usado do mundo

```
y[n] = wᵀ·x[n]
e[n] = d[n] − y[n]
w    ← w + 2μ·e[n]·x[n]          ← esta linha é o algoritmo inteiro
```

**A ideia:** em vez do gradiente verdadeiro (que exige as estatísticas), use o
gradiente **instantâneo** de e². É ruidoso, mas em média aponta na direção certa.
Chama-se *gradiente estocástico* — e sim, é o mesmo princípio do SGD que treina
redes neurais. Widrow e Hoff, 1960; redescoberto em aprendizado de máquina décadas
depois.

**Custo: 2L multiplicações por amostra.** Nada mais barato existe.

### O parâmetro μ é tudo

```python
for mu in [0.001, 0.01, 0.05]:
    ...  # NLMS com normalização pela energia do buffer
```

Saída real (cancelamento de ruído, 20 000 amostras, filtro de 32 taps):

```
  mu=0.001: erro residual inicial   -5.6 dB -> final  -15.4 dB   (redução   9.9 dB)
  mu=0.010: erro residual inicial   -5.6 dB -> final  -27.9 dB   (redução  22.3 dB)
  mu=0.050: erro residual inicial   -5.6 dB -> final  -19.1 dB   (redução  13.5 dB)
```

**A curva em U é a assinatura do LMS e vale memorizar:**

- **μ pequeno demais** (0,001): converge devagar. Em 20 000 amostras ainda não
  chegou lá — só 9,9 dB.
- **μ certo** (0,01): 22,3 dB de redução.
- **μ grande demais** (0,05): converge rápido mas fica "agitado" em torno do
  ótimo, e o desajuste (*misadjustment*) residual custa 9 dB.

**Condição de estabilidade:** 0 < μ < 1/(L·P_x), onde P_x é a potência da entrada.
Como P_x varia, usa-se o **NLMS** (LMS normalizado), que divide pelo próprio nível:

```
w ← w + 2μ·e[n]·x[n] / (xᵀx + ε)
```

Com NLMS, μ vira adimensional entre 0 e 2, e a estabilidade deixa de depender do
volume do sinal. **É o que se usa na prática** — foi o usado na medição acima.
O ε evita divisão por zero no silêncio.

### Os compromissos do LMS

| Aumentar μ | Efeito |
|---|---|
| convergência | mais rápida |
| desajuste residual | **maior** |
| capacidade de rastrear mudanças | melhor |
| risco de instabilidade | maior |

Não há escolha ótima universal: depende de quão rápido o ambiente muda. Sistemas
sérios usam **μ variável** — grande no começo, pequeno depois de convergir.

---

## 4 · RLS — convergência rápida, custo alto

O **RLS** (mínimos quadrados recursivos) resolve exatamente as equações normais a
cada amostra, atualizando R⁻¹ recursivamente (lema de inversão de matriz).

| | LMS/NLMS | RLS |
|---|---|---|
| Custo por amostra | O(L) | **O(L²)** |
| Convergência | dezenas de L amostras | ~2L amostras |
| Sensível ao espalhamento de autovalores da entrada | **muito** | não |
| Estabilidade numérica | robusta | **problemática** em precisão finita |
| Uso típico | quase tudo | quando convergência rápida vale o custo |

**O ponto que decide na prática:** o LMS converge devagar quando a entrada é
"colorida" (autovalores de R muito diferentes) — e fala é extremamente colorida.
O RLS não se importa. Mas o RLS pode divergir numericamente, e existem variantes
estabilizadas (QR-RLS, *lattice*) justamente por isso.

---

## 5 · Kalman — quando existe um modelo de estado

O filtro de Kalman é o estimador ótimo (mínimo erro quadrático) para um sistema
linear com ruído gaussiano descrito por:

```
estado:    s[n] = A·s[n−1] + ruído de processo
medida:    z[n] = H·s[n]   + ruído de medida
```

O ciclo é sempre o mesmo, e é bonito:

```
   PREDIZER ─────────────► CORRIGIR ─────────► (repete)
   usa o modelo            usa a medida
   (o que deveria ser)     (o que se mediu)
                    ▲
              o ganho K decide em quem confiar mais:
              muito ruído de medida → confie no modelo
              muito ruído de processo → confie na medida
```

**Onde aparece:** navegação inercial, GPS (fusão com odometria), rastreamento de
alvos em radar, controle de atitude de satélite, previsão do tempo, rastreamento
de objetos em vídeo, e o pouso do Apollo.

**Relação com o resto:** Kalman é Wiener com um modelo dinâmico explícito e
solução recursiva. Se o estado for constante e o modelo trivial, Kalman **vira**
o filtro de Wiener. Se o sistema for não linear, usa-se EKF (lineariza), UKF
(propaga pontos sigma) ou filtro de partículas (Monte Carlo) — cada um trocando
custo por generalidade.

---

## 6 · Aplicações reais e suas armadilhas

### Cancelamento de eco acústico (viva-voz, videoconferência)

O alto-falante toca, o microfone capta de volta. O adaptativo estima o caminho
acústico e subtrai.

**Por que é difícil:** a resposta de uma sala tem 200–400 ms de cauda. A 16 kHz,
são **3 200 a 6 400 taps**. E a sala muda quando alguém se mexe.

**As soluções reais:**
- Adaptação em **sub-bandas** ([`21`](21-multitaxa-e-bancos-de-filtros.md)):
  filtros curtos por banda, na taxa baixa.
- **Detector de fala dupla** (*double-talk*): quando os dois lados falam ao mesmo
  tempo, a adaptação **precisa congelar** — senão o filtro "aprende" a voz local e
  destrói tudo. Este é o problema mais difícil da área, e é lógica, não matemática.
- Supressão residual não linear no fim da cadeia.

### Cancelamento ativo de ruído (fone ANC)

Mede o ruído externo e emite o oposto.

**A restrição dura é a latência:** o som leva ~30 µs para percorrer 1 cm. Todo o
processamento — A/D, filtro, D/A — tem de caber nesse orçamento. É por isso que
ANC funciona bem em graves (comprimento de onda grande, sobra tempo) e mal em
agudos.

### ECG fetal

O eletrodo no abdome capta o coração da mãe (forte) e o do feto (fraco). Um
segundo eletrodo no tórax dá a referência materna. O adaptativo subtrai a mãe e
revela o feto. É um dos exemplos clássicos de Widrow, e continua em uso.

### Equalização de canal

O canal distorce; o equalizador inverte. **Se o canal não for de fase mínima**
([`17 §4`](17-transformada-z.md)), o inverso é instável — daí o equalizador com
atraso, ou o DFE (com realimentação de decisão), ou o OFDM, que evita o problema
dividindo a banda em pedaços onde o canal é aproximadamente plano.

---

## Os cinco porquês: por que o gradiente instantâneo funciona?

1. **Por que usar o gradiente de uma única amostra em vez do verdadeiro?**
   Porque o verdadeiro exige E{·}, que exige estatísticas que você não tem.
2. **Por que a aproximação não estraga tudo?** Porque o gradiente instantâneo é um
   **estimador não enviesado** do verdadeiro: em média, aponta na direção certa.
3. **Por que "em média" basta?** Porque μ é pequeno, então cada passo é pequeno, e
   o efeito acumulado de muitos passos ruidosos aproxima o efeito de poucos passos
   exatos. O ruído dos passos se cancela; o viés (que seria fatal) não existe.
4. **Então por que sobra o desajuste residual?** Porque o ruído dos passos nunca
   some: perto do ótimo, o gradiente verdadeiro é zero mas o instantâneo não é, e
   o filtro fica "chacoalhando" numa vizinhança. O tamanho dessa vizinhança é
   proporcional a μ — daí a curva em U medida na §3.
5. **Dá para ter convergência rápida e desajuste baixo ao mesmo tempo?**
   Não com μ fixo. **Parada legítima: é um trade-off matemático** entre variância
   e velocidade de adaptação — o mesmo dilema, com outra roupa, do viés × variância
   em estatística e da taxa de aprendizado em redes neurais. A saída de engenharia
   é μ variável no tempo.

---

## Autoteste

1. Quais são as quatro configurações canônicas, e o que muda entre elas?
2. Escreva as equações normais e diga a que operação de álgebra linear equivalem.
3. Por que não se usa sempre a solução fechada de Wiener?
4. Escreva a linha de atualização do LMS e explique cada fator.
5. Explique a curva em U de μ, com os números medidos.
6. O que o NLMS conserta em relação ao LMS?
7. Quando o RLS vale o custo O(L²)?
8. Em que caso o filtro de Kalman se reduz ao de Wiener?
9. Por que a adaptação precisa congelar durante *double-talk*?
10. Por que ANC funciona melhor em graves que em agudos?
