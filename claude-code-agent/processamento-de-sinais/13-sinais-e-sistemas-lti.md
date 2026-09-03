# 13 · Sinais e sistemas LTI — a mecânica por dentro

`Nível: intermediário` · `Atualizado em: 14/08/2026`

O [`10`](10-fundamentos.md) definiu LTI e convolução. Aqui abrimos a caixa: como
esses sistemas se comportam, como se descrevem por equação de diferenças, o que é
estabilidade de verdade, e por que causalidade custa caro.

---

## 1 · Equação de diferenças: a forma como o sistema é implementado

Todo sistema LTI realizável em hardware ou software se escreve como:

```
y[n] = b₀x[n] + b₁x[n−1] + ... + b_M x[n−M]      ← parte "para frente" (FIR)
       − a₁y[n−1] − ... − a_N y[n−N]              ← realimentação (torna IIR)
```

- Se todos os `a` forem zero: **FIR** — resposta ao impulso finita, sem realimentação.
- Se algum `a` for não nulo: **IIR** — resposta infinita, porque a saída realimenta.

Isto **é** o código:

```python
# y[n] = 0.5·x[n] + 0.5·x[n-1] - 0.8·y[n-1]
y = np.zeros(len(x))
for n in range(len(x)):
    y[n] = 0.5*x[n] + (0.5*x[n-1] if n>0 else 0) - (0.8*y[n-1] if n>0 else 0)
```

E `signal.lfilter(b, a, x)` com `b=[0.5,0.5]`, `a=[1,0.8]` faz exatamente isso,
mas em C e com a convenção de sinal já embutida (repare: o `a₁` positivo na lista
vira `−a₁` na equação).

⚠️ **A convenção de sinal do `a` é fonte perene de bug.** Na SciPy e no MATLAB,
`a = [1, a₁, a₂, ...]` e a equação é `Σa_k·y[n−k] = Σb_k·x[n−k]`. Ou seja, o que
está na lista aparece com sinal **trocado** quando você isola y[n]. Muita gente
implementa um IIR à mão com o sinal invertido e obtém um filtro instável.
E `a[0]` tem de ser 1 (ou a SciPy normaliza por ele).

---

## 2 · Resposta ao impulso: FIR × IIR

```python
import numpy as np
from scipy import signal

d = signal.unit_impulse(20)
print("FIR:", np.round(signal.lfilter([0.5, 0.5], 1, d), 4)[:6])
print("IIR:", np.round(signal.lfilter([1], [1, -0.8], d), 4)[:6])
```

Saída real:

```
FIR: [0.5 0.5 0.  0.  0.  0. ]
IIR: [1.     0.8    0.64   0.512  0.4096 0.3277]
```

O FIR acaba em 2 amostras. O IIR nunca acaba — decai como 0,8ⁿ, e teoricamente só
zera no infinito. Na prática, `0.8**n < 2**-16` em n ≈ 50, e aí ele "acabou" para
efeitos de 16 bits.

**Consequência de projeto:** um IIR entrega uma resposta em frequência acentuada
com pouquíssimas operações (ver [`19`](19-filtros-iir.md)), mas carrega estado, pode
instabilizar, e distorce fase. Um FIR é sempre estável e pode ter fase linear, mas
custa muitos coeficientes. **Todo o capítulo 18 e 19 é essa troca.**

---

## 3 · Estabilidade — a definição prática

**BIBO** (Bounded Input, Bounded Output): toda entrada limitada produz saída
limitada.

**Critério:** um sistema LTI é BIBO estável ⟺ `Σ_n |h[n]| < ∞` (a resposta ao
impulso é absolutamente somável).

**Por quê:** |y[n]| = |Σ h[k]x[n−k]| ≤ max|x| · Σ|h[k]|. Se a soma converge, a
saída é limitada. E existe uma entrada (o sinal dos sinais de h) que atinge esse
limite, então a condição também é necessária.

Para um IIR de um polo, h[n] = aⁿ·u[n], a soma é geométrica (§4 de
[`12`](12-matematica-do-zero.md)) e converge se e só se **|a| < 1** — o polo dentro
do círculo unitário. É o critério inteiro de [`17`](17-transformada-z.md), derivado
em uma linha.

**Demonstração numérica do que é instabilidade:**

```python
for a in [0.99, 1.0, 1.01]:
    h = signal.lfilter([1], [1, -a], signal.unit_impulse(500))
    print(f"a={a}: |h[499]| = {abs(h[-1]):.3e}   soma|h| = {np.sum(np.abs(h)):.3e}")
```

Saída real:

```
a=0.99: |h[499]| = 6.637e-03   soma|h| = 9.934e+01
a=1.0: |h[499]| = 1.000e+00   soma|h| = 5.000e+02
a=1.01: |h[499]| = 1.433e+02   soma|h| = 1.438e+04
```

- a = 0,99: decai, soma finita (≈ 1/(1−0,99) = 100). **Estável.**
- a = 1,00: não decai. Soma cresce sem limite. **Marginalmente estável** — é o
  integrador puro, e ele acumula qualquer DC para sempre.
- a = 1,01: cresce exponencialmente. Em 500 amostras já multiplicou por 145.
  **Instável.** Em áudio a 44,1 kHz isso estoura em ~10 ms.

**Na prática, evite polos com |a| > 0,999.** Em ponto flutuante você chega perto do
círculo; em ponto fixo, o arredondamento do coeficiente pode empurrar o polo para
fora e transformar um filtro projetado como estável num oscilador
([`28`](28-implementacao-ponto-fixo-e-hardware.md)).

---

## 4 · Causalidade — e o que ela custa

**Causal:** y[n] só depende de x[n], x[n−1], ... — nunca do futuro.
Equivale a `h[n] = 0` para n < 0.

Obrigatório em tempo real. Opcional em processamento de arquivo.

**O que a causalidade custa:** o teorema de **Paley-Wiener** diz que um filtro
causal e estável **não pode** ter resposta em magnitude nula numa faixa de
frequências de medida não nula. Ou seja:

> **Um filtro ideal (corte perfeitamente abrupto, atenuação infinita na banda de
> rejeição) é fisicamente irrealizável.**

Não é limitação de tecnologia; é teorema. A resposta ao impulso do filtro ideal é
uma `sinc` infinita em ambas as direções — precisa do futuro **e** do passado
infinito. Todo projeto de filtro é uma negociação sobre **como** aproximar o ideal:
truncar (janela), otimizar o erro máximo (Parks-McClellan), otimizar o erro
quadrático (`firls`), ou aceitar realimentação (IIR).

**Relação de Hilbert:** em sistemas causais, magnitude e fase **não são
independentes** — uma determina a outra (a menos de fatores passa-tudo). Você não
pode pedir "esta magnitude e fase linear" simultaneamente num sistema causal
qualquer. Só a estrutura FIR simétrica escapa disso, e ela escapa pagando com
atraso.

---

## 5 · Fase, atraso de fase e atraso de grupo

Três coisas diferentes que costumam ser confundidas:

| Grandeza | Fórmula | Significa |
|---|---|---|
| Fase | ∠H(e^{jΩ}) | deslocamento angular naquela frequência |
| Atraso de fase | −∠H(Ω)/Ω | atraso da **portadora** |
| **Atraso de grupo** | −d∠H(Ω)/dΩ | atraso da **envoltória** — é o que se ouve/vê |

**Fase linear** ⟺ ∠H = −αΩ ⟺ atraso de grupo **constante** = α amostras para todas
as frequências. Resultado: o sinal atrasa inteiro, sem deformar.

Fase **não** linear ⟹ frequências diferentes chegam em tempos diferentes ⟹ a forma
de onda muda mesmo que a magnitude esteja perfeita.

```python
import numpy as np
from scipy import signal

h_fir = signal.firwin(51, 0.3)                       # fase linear
sos    = signal.butter(6, 0.3, output='sos')         # fase não linear
b, a   = signal.butter(6, 0.3)

w1, gd1 = signal.group_delay((h_fir, 1))
w2, gd2 = signal.group_delay((b, a))
faixa = (w1 > 0.05) & (w1 < 0.25*np.pi)
print(f"FIR  : atraso de grupo min={gd1[faixa].min():.2f} max={gd1[faixa].max():.2f} amostras")
faixa2 = (w2 > 0.05) & (w2 < 0.25*np.pi)
print(f"IIR  : atraso de grupo min={gd2[faixa2].min():.2f} max={gd2[faixa2].max():.2f} amostras")
```

Saída real:

```
FIR  : atraso de grupo min=25.00 max=25.00 amostras
IIR  : atraso de grupo min=3.80 max=6.61 amostras
```

Leia com cuidado, porque isto é o compromisso central:

- **FIR:** atraso rigorosamente constante de 25 amostras = (51−1)/2. Nenhuma
  distorção de fase. Mas 25 amostras é bastante — a 48 kHz, 0,52 ms.
- **IIR:** atraso muito menor (3,8 a 6,6 amostras) mas **variável**: as frequências
  perto do corte atrasam 74 % mais que as baixas. A forma de onda **muda**.

**Quando cada um importa:**

| Aplicação | Fase importa? |
|---|---|
| Áudio para escuta casual | pouco — o ouvido é relativamente insensível à fase de sinais estacionários |
| Áudio com transiente (bateria, ataque) | **sim** — fase não linear borra o ataque |
| ECG, EEG | **muito** — a morfologia da onda **é** o diagnóstico |
| Comunicação digital | **muito** — ISI (interferência entre símbolos) vem de fase não linear |
| Medição de tempo de chegada | **muito** — atraso variável estraga a estimativa |
| Controle em malha fechada | **crítico** — atraso é margem de fase perdida, e instabilidade |

---

## 6 · A resposta ao degrau e o que ela revela

A resposta ao degrau é a soma acumulada da resposta ao impulso. Ela mostra três
coisas que o gráfico de magnitude esconde:

- **tempo de subida** — ligado à largura de banda (produto banda × tempo ≈ 0,35)
- **sobressinal (overshoot)** — Gibbs, para FIR truncado
- **oscilação (ringing)** — quanto mais abrupto o corte, mais toca

```python
import numpy as np
from scipy import signal

degrau = np.concatenate([np.zeros(1000), np.ones(2000)])
print(f'{"janela":10s} {"sobressinal(tempo)":>18s} {"rejeição(freq)":>16s}')
for jan in ['boxcar', 'hamming', 'blackman']:
    h = signal.firwin(401, 0.1, window=jan)
    y = signal.lfilter(h, 1, degrau)
    w, H = signal.freqz(h, worN=8192)
    rej = 20*np.log10(np.max(np.abs(H[w > 0.15*np.pi])))
    print(f'{jan:10s} {100*(y.max()-1):17.2f}% {rej:15.1f} dB')
```

Saída real:

```
janela     sobressinal(tempo)   rejeição(freq)
boxcar                  9.46%           -41.7 dB
hamming                 8.86%           -64.3 dB
blackman                8.76%           -95.4 dB
```

**Este resultado surpreende quase todo mundo, inclusive quem já projetou filtro.**
A expectativa comum é "a janela mata o Gibbs". Olhe os números:

- Na **frequência**, a janela faz um estrago enorme no ripple: de −42 dB para
  −95 dB de rejeição. Ganho de 54 dB. É para isso que ela serve.
- No **tempo**, o sobressinal quase não muda: 9,46 % → 8,76 %. **Continua lá.**

Por quê? Porque são dois fenômenos diferentes com o mesmo nome de família:

1. O ripple na **banda de rejeição** vem de **truncar** a resposta ao impulso.
   Isso a janela conserta, porque ela suaviza justamente as pontas truncadas.
2. O sobressinal na **resposta ao degrau** é propriedade do **passa-baixa abrupto
   em si**, e não do truncamento. O passa-baixa ideal, sem truncamento nenhum, tem
   resposta ao degrau igual à integral de uma `sinc` — a função seno-integral —
   cujo máximo é Si(π)/π = 1,0895, ou seja **8,95 % de sobressinal**. Compare com
   o 8,76 % medido do Blackman: a janela apenas aproxima o comportamento ideal.

**Consequência prática séria:** se seu sistema não tolera sobressinal (controle,
instrumentação, detecção de limiar), **não adianta trocar de janela** — você tem
de suavizar o *corte* do filtro. Filtro abrupto ⟹ toque no tempo. Sempre. É o
mesmo princípio da incerteza de novo, vestido de outra roupa.

E o valor 8,95 % é literalmente o fenômeno de Gibbs de 1899, o mesmo que levou
Lagrange a rejeitar Fourier em 1807 ([`11`](11-historia.md)) — 220 anos depois,
aparecendo em três casas decimais na sua tela.

---

## 7 · Sistemas não LTI — o que existe fora da teoria

Nem tudo é LTI, e é honesto dizer o que fica de fora.

| Tipo | Exemplo | Por que a teoria de Fourier não basta |
|---|---|---|
| **Não linear sem memória** | clipping, compressor, distorção de guitarra | cria harmônicos e intermodulação |
| **Variante no tempo** | filtro com corte que muda, AGC | resposta em frequência depende de *quando* |
| **Não linear com memória** | Volterra, histerese, alto-falante em excursão alta | precisa de séries de Volterra ou de modelos de estado |
| **Estatisticamente adaptativo** | LMS, RLS, Kalman | o próprio sistema aprende. Ver [`23`](23-estimacao-e-filtragem-adaptativa.md) |
| **Não linear aprendido** | rede neural | sem teoria fechada; garantias empíricas |

**A estratégia padrão do campo, e ela é pragmática:** aproximar localmente por LTI.
Um compressor de áudio é tratado como LTI dentro de cada janela curta; um sistema
variante no tempo, como uma sequência de sistemas LTI ("quasi-estacionário"). Essa
aproximação sustenta praticamente toda a engenharia de sinais — e falha exatamente
quando o sinal muda rápido demais dentro da janela. Saber onde ela falha é o que
separa quem entende de quem repete receita.

---

## Os cinco porquês: por que a realimentação (IIR) é tão eficiente?

1. **Por que um IIR faz com 4 coeficientes o que um FIR precisa de 200?**
   Porque a realimentação reaproveita a saída anterior, que já contém a soma
   ponderada de todo o passado.
2. **Por que isso equivale a "todo o passado"?** Porque a resposta ao impulso é
   infinita: y[n] depende de x[n−k] para todo k, com peso aᵏ.
3. **Por que o peso decai geometricamente?** Porque cada volta pela realimentação
   multiplica por a. É uma progressão geométrica, e sua soma é finita se |a|<1.
4. **Por que o FIR não pode fazer o mesmo?** Porque sem realimentação cada amostra
   de resposta exige um coeficiente próprio armazenado. Para emular um decaimento de
   200 amostras, precisa de 200 números.
5. **Então por que alguém usa FIR?** Porque a realimentação tem três preços
   inescapáveis: pode instabilizar (o polo pode sair do círculo), a fase não pode
   ser linear (ver §4, Paley-Wiener/Hilbert), e o erro de arredondamento realimenta
   e se acumula em vez de se dissipar. **A troca é eficiência contra controle.**
   Parada legítima: é um **trade-off matemático**, não uma limitação tecnológica.

---

## Autoteste

1. Escreva a equação de diferenças de `b=[1,2]`, `a=[1,-0.5]` e diga se é FIR ou IIR.
2. Qual é o critério exato de estabilidade BIBO e como ele vira "|a| < 1"?
3. Por que o filtro ideal é irrealizável? Cite o teorema.
4. Diferencie atraso de fase de atraso de grupo, e diga qual você ouve.
5. Um FIR de 101 taps tem que atraso de grupo? E por quê constante?
6. A janela reduz o ripple na banda de rejeição mas quase não reduz o sobressinal
   da resposta ao degrau. Por que os dois efeitos se separam?
7. De onde sai o número 8,95 %, e o que ele implica para um sistema que não tolera
   sobressinal?
8. Cite duas aplicações em que fase não linear é inaceitável, e por quê.
