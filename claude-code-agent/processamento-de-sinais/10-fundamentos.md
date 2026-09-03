# 10 · Fundamentos — vocabulário e modelos mentais

`Nível: iniciante → intermediário` · `Atualizado em: 14/08/2026`

Aqui as palavras ganham definição precisa. Tudo que vem depois usa este vocabulário.
Termo que aparece em **negrito** está definido no [`GLOSSARIO.md`](GLOSSARIO.md).

---

## 1 · Sinal

**Definição.** Um **sinal** é uma função que associa um valor a cada ponto de uma
variável independente, e que carrega informação.

Formalmente: x: D → C, onde D é o domínio (tempo, espaço, ...) e C o contradomínio
(reais, complexos, vetores).

### Classificações que mudam a matemática que você usa

| Eixo | Tipos | Consequência |
|---|---|---|
| Domínio | **contínuo** `x(t)` × **discreto** `x[n]` | integral × somatório; Fourier × DFT |
| Amplitude | contínua × **quantizada** | análise exata × ruído de quantização |
| Determinismo | **determinístico** × **estocástico** | fórmula fechada × estatística |
| Periodicidade | periódico × aperiódico | série de Fourier × transformada de Fourier |
| Duração | finita × infinita × **causal** (nulo para n<0) | o que existe fisicamente é finito e causal |
| Energia | **energia finita** (Σx² < ∞) × **potência finita** | transiente × sinal contínuo em regime |
| Dimensão | 1D (áudio) × 2D (imagem) × 3D (vídeo, volume) | mesma teoria, mais índices |
| Valores | real × **complexo** (I/Q) | rádio moderno é complexo por natureza |

**Nomenclatura combinada** (fonte eterna de confusão):

|  | Tempo contínuo | Tempo discreto |
|---|---|---|
| **Amplitude contínua** | analógico | *sampled-data* (raro na prática) |
| **Amplitude quantizada** | quantizado no tempo contínuo (raro) | **digital** |

"Digital" = discreto **nos dois** eixos. É o que existe dentro do computador.

### Sinais elementares — os tijolos

```python
import numpy as np
n = np.arange(-5, 10)

impulso = (n == 0).astype(float)              # δ[n]
degrau  = (n >= 0).astype(float)              # u[n]
rampa   = n*degrau                            # r[n]
exp_real = 0.8**n * degrau                    # a^n·u[n]
exp_complexa = np.exp(2j*np.pi*0.1*n)         # e^{jΩn} ← a mais importante
```

**Por que a exponencial complexa é a mais importante:** porque ela é o
**autovetor** de todo sistema LTI. Colocar e^{jΩn} na entrada de qualquer sistema
LTI devolve o *mesmo* e^{jΩn} na saída, multiplicado por um número complexo. Nenhum
outro sinal tem essa propriedade. Toda a teoria de Fourier existe para explorá-la.
Isso é demonstrado na seção 5 deste arquivo.

### Duas propriedades do impulso que você vai usar sempre

**1. Amostragem (peneiração):** `x[n]·δ[n−k] = x[k]·δ[n−k]`.
Multiplicar por um impulso extrai um valor.

**2. Decomposição:** todo sinal é uma soma de impulsos deslocados e escalados:

```
x[n] = Σ_k x[k]·δ[n−k]
```

Parece trivial e é a chave de tudo: se você souber o que o sistema faz com **um**
impulso, e se ele for linear e invariante, você sabe o que ele faz com **qualquer**
sinal. Essa frase é a convolução, e está provada na seção 6.

---

## 2 · Sistema

**Definição.** Um **sistema** é um operador T que transforma um sinal em outro:
`y[n] = T{x[n]}`.

Exemplos: um amplificador, um filtro, o ar entre a boca e o ouvido, uma sala com
eco, um cabo, um algoritmo.

### Propriedades — e por que cada uma importa

| Propriedade | Definição | Por que importa |
|---|---|---|
| **Linear** | T{a·x₁ + b·x₂} = a·T{x₁} + b·T{x₂} | permite analisar uma frequência de cada vez e somar |
| **Invariante no tempo** | atrasar a entrada só atrasa a saída | permite descrever o sistema por **uma** função h[n] |
| **Causal** | y[n] depende só de x[n], x[n−1], ... | obrigatório em tempo real: o futuro não chegou |
| **Estável** (BIBO) | entrada limitada ⇒ saída limitada | não explode. Equivale a Σ\|h[n]\| < ∞ |
| **Memória** | y[n] depende de valores passados | sem memória = só de x[n] |
| **Invertível** | existe T⁻¹ | equalização, desconvolução |

**LTI = Linear + Invariante no Tempo.** É o coração do campo. Quase toda a teoria
clássica trata de sistemas LTI, e isso é uma escolha, não uma limitação da
natureza — sistemas reais raramente são LTI perfeitos, mas são bem aproximados por
LTI numa faixa de operação, e a teoria LTI é a única que fecha em forma analítica.

Teste rápido de linearidade em código:

```python
import numpy as np
from scipy import signal

def sistema_A(x): return signal.lfilter([0.5, 0.5], 1, x)   # média de dois
def sistema_B(x): return x**2                                 # quadrador

rng = np.random.default_rng(0)
x1, x2 = rng.standard_normal(100), rng.standard_normal(100)
a, b = 2.0, -3.0

for nome, S in [("A (média)", sistema_A), ("B (quadrado)", sistema_B)]:
    esq = S(a*x1 + b*x2)
    dir = a*S(x1) + b*S(x2)
    print(f"{nome:14s} erro de linearidade: {np.max(np.abs(esq-dir)):.2e}")
```

Saída real (executada em 14/08/2026):

```
A (média)      erro de linearidade: 8.88e-16
B (quadrado)   erro de linearidade: 9.06e+01
```

O primeiro é zero numérico: linear. O segundo não é, e por isso a teoria de
Fourier **não** se aplica a ele — um quadrador cria frequências novas
(2·f a partir de f), e criar frequência nova é a assinatura da não linearidade.

---

## 3 · Convolução — a operação central

**Definição.**

```
y[n] = (x * h)[n] = Σ_k x[k]·h[n−k]
```

**Derivação em quatro linhas** (a única prova que eu insisto que se leia):

1. `x[n] = Σ_k x[k]·δ[n−k]` — todo sinal é soma de impulsos (seção 1).
2. Pela **linearidade**: `y[n] = T{Σ_k x[k]·δ[n−k]} = Σ_k x[k]·T{δ[n−k]}`.
3. Pela **invariância no tempo**: `T{δ[n−k]} = h[n−k]`, onde `h = T{δ}`.
4. Logo: `y[n] = Σ_k x[k]·h[n−k]`. ∎

Ou seja: **linearidade + invariância no tempo ⇒ convolução, obrigatoriamente.**
A convolução não foi escolhida por conveniência; ela é o que sobra.

### Interpretação mecânica

Inverta h, deslize sobre x, multiplique ponto a ponto, some. A cada deslocamento,
um valor da saída.

```
x:      1  2  3
h:      1  1               (média móvel de 2)

n=0:  [1]              →  1·1               = 1
n=1:  [1  2]           →  1·1 + 2·1         = 3
n=2:     [2  3]        →  2·1 + 3·1         = 5
n=3:        [3]        →  3·1               = 3

y = [1, 3, 5, 3]     ← comprimento len(x)+len(h)-1 = 4
```

```python
np.convolve([1,2,3], [1,1])     # array([1, 3, 5, 3])
```

### Propriedades

| Propriedade | Fórmula | Uso prático |
|---|---|---|
| Comutativa | x*h = h*x | tanto faz quem é sinal e quem é filtro |
| Associativa | (x*h₁)*h₂ = x*(h₁*h₂) | **filtros em cascata viram um só**: h = h₁*h₂ |
| Distributiva | x*(h₁+h₂) = x*h₁ + x*h₂ | filtros em paralelo somam |
| Identidade | x*δ = x | o impulso é o elemento neutro |
| Comprimento | N + M − 1 | por isso o sinal "cresce" ao ser filtrado |
| **Teorema da convolução** | x*h ⟷ X·H | **convolução no tempo = multiplicação na frequência** |

O teorema da convolução é o resultado mais lucrativo do campo: transforma uma
operação O(N·M) numa multiplicação O(N) mais duas FFTs O(N log N). É a base do
`fftconvolve` e a razão de a FFT valer ouro.

### Correlação — parecida, e diferente

```
r_xy[k] = Σ_n x[n]·y[n+k]        (correlação)
y[n]    = Σ_k x[k]·h[n−k]        (convolução)
```

Correlação **não** inverte o segundo sinal. Convolução inverte.
Consequência: correlação **não** é comutativa (`r_xy[k] = r_yx[−k]`).

**Quando usar cada uma:** convolução quando você está *aplicando um sistema*;
correlação quando está *procurando um padrão*. Como `correlate(x,h) = convolve(x, h[::-1])`,
implementações reais frequentemente usam a mesma rotina — mas os significados são
opostos, e trocá-los inverte o resultado no tempo.

---

## 4 · Resposta ao impulso e resposta em frequência

`h[n] = T{δ[n]}` é a **resposta ao impulso**: a assinatura completa de um sistema LTI.
Meça-a e você sabe tudo sobre o sistema.

Isso é literalmente feito na prática: a **resposta ao impulso de uma sala** é medida
estourando um balão (ou tocando uma varredura), e convoluir uma gravação seca com
ela põe a gravação "dentro" daquela sala. É como funciona a reverberação por
convolução em estúdio.

A **resposta em frequência** H(e^{jΩ}) é a transformada de Fourier de h[n]:

- `|H|` — quanto cada frequência é amplificada ou atenuada (magnitude)
- `∠H` — quanto cada frequência é atrasada (fase)

```python
import numpy as np
from scipy import signal

h = np.ones(5)/5                      # média móvel de 5
w, H = signal.freqz(h, fs=1000)
for f in [0, 100, 200, 400]:
    k = np.argmin(np.abs(w - f))
    print(f"{f:4d} Hz: |H| = {np.abs(H[k]):.4f}  ({20*np.log10(max(abs(H[k]),1e-12)):+7.2f} dB)")
```

Saída real:

```
   0 Hz: |H| = 1.0000  (  +0.00 dB)
 100 Hz: |H| = 0.6497  (  -3.75 dB)
 200 Hz: |H| = 0.0010  ( -59.63 dB)
 400 Hz: |H| = 0.0013  ( -57.79 dB)
```

Zeros em 200 Hz e 400 Hz — ou seja, em fs/5 e 2·fs/5 — exatamente onde a teoria da
média móvel de 5 prevê. (Não são exatamente −∞ dB porque a grade de `freqz` não cai
em cima do zero; −60 dB aqui é "zero" para todo efeito prático.)

Previsão feita antes de rodar, confirmada depois: é assim que se estuda DSP.

---

## 5 · Por que senoides? — os autovetores dos sistemas LTI

Ponha `x[n] = e^{jΩn}` na convolução:

```
y[n] = Σ_k h[k]·e^{jΩ(n−k)} = e^{jΩn} · Σ_k h[k]·e^{−jΩk} = e^{jΩn} · H(e^{jΩ})
                              └──────── não depende de n ────────┘
```

A saída é **a mesma exponencial**, multiplicada por um número complexo. Em álgebra
linear, isso é a definição de autovetor: o operador não muda a "direção", só escala.

**Consequências, e cada uma é um pilar do campo:**

1. Se você decompuser qualquer sinal em exponenciais complexas, saberá a saída
   imediatamente — basta multiplicar cada componente por H. **É por isso que
   Fourier existe.**
2. Um sistema LTI **nunca cria frequência nova**. Entrou 440 Hz, sai 440 Hz, com
   outra amplitude e outra fase. Se apareceu 880 Hz na saída, o sistema não é LTI
   (é não linear, ou variante no tempo).
3. O teste de um sistema pode ser feito uma frequência de cada vez — e é assim que
   se mede resposta em frequência em laboratório.

Verificação numérica:

```python
import numpy as np
from scipy import signal
h = signal.firwin(31, 0.3)
n = np.arange(200); Omega = 0.2*np.pi
x = np.exp(1j*Omega*n)
y = signal.lfilter(h, 1, x)
H = np.sum(h*np.exp(-1j*Omega*np.arange(len(h))))
razao = y[100]/x[100]
print(f"y/x no regime = {razao:.6f}")
print(f"H(e^jΩ)       = {H:.6f}")
```

Saída real:

```
y/x no regime = -0.987448-0.000000j
H(e^jΩ)       = -0.987448-0.000000j
```

Idênticos até a sexta casa. A teoria funciona.

**Bônus escondido nesse número.** Por que a razão deu um real **negativo**, e não
um complexo qualquer? Porque `firwin` produz um FIR de **fase linear**: seus 31
coeficientes são simétricos, e para esse filtro
H(e^{jΩ}) = e^{−jΩ(N−1)/2}·(algo real). Com N=31 e Ω=0,2π:
o expoente vale −0,2π·15 = −3π, e e^{−j3π} = −1. O sinal de menos é um atraso de
15 amostras disfarçado de inversão de sinal. Se você tropeçar em "meu filtro
inverteu o sinal", quase sempre é isso — [`18`](18-filtros-fir.md) detalha.

---

## 6 · Frequência — três formas de dizer a mesma coisa

| Grandeza | Símbolo | Unidade | Faixa útil |
|---|---|---|---|
| Frequência | f | Hz | 0 a fs/2 |
| Frequência angular | ω = 2πf | rad/s | 0 a π·fs |
| Frequência normalizada | Ω = 2πf/fs | rad/amostra | 0 a π |

**Por que Ω vai só até π:** porque com fs amostras por segundo, o sinal mais rápido
que você distingue alterna a cada amostra (+1, −1, +1, −1...), o que dá meia volta
por amostra = π rad/amostra = fs/2 Hz. Acima disso, indistinguível de algo mais
lento. **Isso é Nyquist visto pelo ângulo da frequência normalizada.**

Consequência que confunde iniciantes: no discreto, o espectro é **periódico** com
período 2π. Ω = 0,1π e Ω = 2,1π são o **mesmo sinal**, não parecidos: idênticos,
amostra por amostra. No contínuo isso não acontece.

```python
n = np.arange(10)
print(np.allclose(np.exp(1j*0.1*np.pi*n), np.exp(1j*2.1*np.pi*n)))   # True
```

---

## 7 · Energia, potência e decibel

| Grandeza | Fórmula | Quando faz sentido |
|---|---|---|
| Energia | E = Σ \|x[n]\|² | sinal transiente, que acaba |
| Potência média | P = lim (1/N)·Σ \|x[n]\|² | sinal contínuo, que não acaba |
| RMS | √P | o valor "eficaz" — o que aquece o alto-falante |
| Fator de crista | pico/RMS | mede o quão "picudo" é. Senoide: √2 (3,01 dB) |

**Teorema de Parseval:** a energia é a mesma nos dois domínios.

```
Σ_n |x[n]|² = (1/N)·Σ_k |X[k]|²
```

Não é curiosidade: é o que permite medir potência por banda no domínio da
frequência e saber que a conta fecha. Todo medidor de espectro depende disso.

```python
x = np.random.default_rng(0).standard_normal(1024)
X = np.fft.fft(x)
print(np.sum(x**2), np.sum(np.abs(X)**2)/len(x))
# 969.6664686193726  969.6664686193728   ← iguais até o último bit representável
```

---

## 8 · Os quatro pares de transformada

Este é o mapa que organiza toda a teoria. Guarde-o.

| Sinal | Transformada | Espectro é | Uso |
|---|---|---|---|
| contínuo, periódico | **Série de Fourier** | discreto, infinito | análise de onda periódica |
| contínuo, aperiódico | **Transformada de Fourier (FT)** | contínuo, infinito | teoria analógica |
| discreto, aperiódico | **DTFT** | contínuo, periódico (2π) | teoria digital |
| **discreto, finito** | **DFT / FFT** | **discreto, finito** | **o que roda no computador** |

**A regra que gera a tabela inteira:** discreto num domínio ⟺ periódico no outro.

- Sinal discreto no tempo ⟹ espectro periódico na frequência.
- Espectro discreto (bins) ⟹ sinal periódico no tempo (a DFT *assume* que seu bloco
  se repete para sempre — e é daí que vem o vazamento espectral).

Só a última linha é computável: precisa ser discreta e finita nos dois lados.
Todas as outras são ferramentas de papel. Quando você faz FFT de um áudio, está
usando a última linha para *aproximar* a terceira. Saber disso explica quase todos
os "artefatos estranhos" que aparecem na prática.

---

## 9 · Modelos mentais que valem mais que fórmulas

**1. Sinal é vetor.** Um sinal de N amostras é um ponto em ℝᴺ. Correlação é produto
interno. Filtrar é aplicar uma matriz. Fourier é trocar de base. Se você pensar
assim, [`23`](23-estimacao-e-filtragem-adaptativa.md) fica trivial.

**2. Fourier é uma mudança de base.** A base canônica (impulsos) diz *quando* as
coisas acontecem. A base de Fourier (senoides) diz *em que frequência*. Nenhuma é
mais verdadeira; são pontos de vista. Escolha o que torna seu problema fácil.

**3. Multiplicar num domínio = convoluir no outro.** Este par explica: vazamento
espectral (multiplicar por janela = convoluir com o espectro dela), aliasing
(amostrar = multiplicar por pente = convoluir com pente na frequência), modulação
AM (multiplicar por portadora = deslocar o espectro).

**4. Não existe almoço grátis, e o preço é sempre o mesmo:** resolução em tempo ×
resolução em frequência; nitidez do corte × comprimento do filtro; ruído baixo ×
atraso baixo. Toda escolha de projeto em DSP é uma dessas três trocas disfarçada.

**5. Se você não plotou, não sabe.** Nenhuma exceção que eu tenha visto em anos.

---

## Os cinco porquês — por que senoides, e não outra coisa?

1. **Por que decompor sinais em senoides?** Porque sistemas LTI as preservam
   (seção 5): entra seno, sai seno.
2. **Por que sistemas LTI preservam senoides?** Porque a convolução com e^{jΩn}
   fatora em e^{jΩn}·(constante) — é a propriedade da exponencial de que
   e^{a(n−k)} = e^{an}·e^{−ak}.
3. **Por que essa fatoração acontece só com a exponencial?** Porque a exponencial é
   a única função (a menos de escala) que transforma soma em produto:
   f(a+b) = f(a)·f(b). É uma **propriedade algébrica**, não uma escolha.
4. **Por que isso importa fisicamente?** Porque muitos sistemas físicos são
   descritos por equações diferenciais lineares de coeficientes constantes, cujas
   soluções naturais são exponenciais. Massa-mola, circuito RLC, linha de
   transmissão — todos.
5. **Por que a natureza é assim?** Aqui a cadeia para em duas paradas legítimas:
   (a) uma **lei matemática** — a exponencial é autofunção do operador derivada,
   d/dt e^{at} = a·e^{at}, e é a única; (b) uma **aproximação de engenharia** —
   sistemas reais não são exatamente lineares, e nós os tratamos como lineares numa
   faixa restrita **porque essa é a única classe para a qual temos teoria completa**.
   Fora dela, o campo é muito mais fraco, e isso é honesto dizer.

---

## Autoteste

1. Defina sinal digital de forma que o distinga de "discreto" e de "quantizado".
2. Prove, em quatro passos, que LTI implica convolução.
3. Por que a exponencial complexa é o autovetor de todo sistema LTI?
4. Um sistema recebe 1 kHz e devolve 1 kHz + 2 kHz. O que se pode afirmar?
5. Qual dos quatro pares de transformada é computável, e por quê?
6. Enuncie a regra "discreto num domínio ⟺ periódico no outro" e dê duas
   consequências práticas.
7. Uma média móvel de 5 tem zero em que frequência? Deduza sem rodar código.
8. Convolução e correlação: qual inverte o sinal e qual não é comutativa?
