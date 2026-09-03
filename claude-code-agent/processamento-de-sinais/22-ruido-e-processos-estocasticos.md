# 22 · Ruído e processos estocásticos — quando o sinal é aleatório

`Nível: avançado` · `Medições feitas em: 19/08/2026`

Até aqui os sinais eram determinísticos: uma fórmula produzia cada amostra.
Ruído não é assim. Ele exige outra linguagem — a da estatística — e essa mudança
de linguagem é o que separa o DSP de laboratório do DSP de campo.

---

## 1 · O que muda quando o sinal é aleatório

Um sinal aleatório **não tem transformada de Fourier** no sentido usual: a
integral não converge, porque o sinal não tem energia finita (ele não acaba).

E, mais importante: **não faz sentido perguntar o valor de x[n]**. Faz sentido
perguntar a distribuição, a média, a variância, e como amostras vizinhas se
relacionam.

| Determinístico | Estocástico |
|---|---|
| x[n] é um número | x[n] é uma variável aleatória |
| transformada de Fourier X(f) | **densidade espectral de potência** S(f) |
| energia Σ\|x\|² | **potência** média E{\|x\|²} |
| convolução dá a saída exata | dá a saída **em média** |
| um sinal | uma **família** (ensemble) de sinais possíveis |

---

## 2 · Vocabulário mínimo

| Termo | Definição | Por que importa |
|---|---|---|
| **Média** | μ = E{x[n]} | nível DC |
| **Variância** | σ² = E{(x−μ)²} | **potência** do sinal aleatório |
| **Autocorrelação** | R[k] = E{x[n]·x[n+k]} | estrutura de repetição |
| **Autocovariância** | R[k] − μ² | idem, sem o DC |
| **Estacionário (WSS)** | μ e R[k] não dependem de n | sem isso, "o espectro" não existe |
| **Ergódico** | média temporal = média estatística | permite medir tudo de **uma** gravação |
| **DEP / PSD** | S(f) = 𝓕{R[k]} | o "espectro" de um sinal aleatório |

### Estacionaridade e ergodicidade: duas hipóteses, não dois fatos

**Estacionário**: as estatísticas não mudam com o tempo. Fala **não é**
estacionária — por isso se analisa em janelas de 20–30 ms, dentro das quais ela é
aproximadamente estacionária. É a justificativa formal do espectrograma.

**Ergódico**: você pode trocar "média sobre muitas realizações" por "média sobre
o tempo de uma realização". Sem essa hipótese, medir qualquer coisa exigiria
repetir o universo.

⚠️ **As duas são hipóteses que você assume, e ambas podem ser falsas.** Assumir
estacionaridade onde ela não vale é uma das fontes mais comuns de resultado
errado publicado — e o sintoma é sempre o mesmo: um espectro médio que não
descreve nenhum instante real do sinal.

---

## 3 · Ruído branco e ruído colorido

**Branco** = autocorrelação nula fora de k=0, ou seja, espectro plano.
**Colorido** = amostras correlacionadas, espectro não plano.

```python
import numpy as np
from scipy import signal
rng = np.random.default_rng(0); n = 200000
b = rng.standard_normal(n)
r = signal.lfilter([1], [1, -0.9], b)          # AR(1): ruído "colorido"

for nome, v in [('branco', b), ('AR(1) a=0.9', r)]:
    ac = np.correlate(v-v.mean(), v-v.mean(), 'full')[n-1:n+4]; ac /= ac[0]
    print(f"{nome:12s} autocorrelação k=0..4:", np.round(ac, 3))
```

Saída real:

```
branco       autocorrelação k=0..4: [ 1.    -0.004  0.002 -0.001 -0.004]
AR(1) a=0.9  autocorrelação k=0..4: [1.    0.9    0.81   0.729  0.656]
```

**O AR(1) reproduz exatamente a teoria:** R[k] = a^k. 0,9¹ = 0,900;
0,9² = 0,810; 0,9³ = 0,729; 0,9⁴ = 0,656. Quatro casas. E o branco dá zero
dentro do erro estatístico (~1/√n = 0,002).

### As cores

| Nome | S(f) ∝ | Onde aparece |
|---|---|---|
| **Branco** | f⁰ | ruído térmico, quantização (idealizado) |
| **Rosa** (1/f) | f⁻¹ | ruído de cintilação (*flicker*), deriva de osciladores, música, tráfego |
| **Browniano** (vermelho) | f⁻² | passeio aleatório; integral de ruído branco |
| **Azul** | f¹ | erro de quantização com *noise shaping* |
| **Violeta** | f² | derivada de ruído branco |

⚠️ **Ruído branco é uma idealização.** Potência infinita se a banda fosse
infinita. Na prática significa "plano na banda que me interessa".

**Ruído 1/f é a praga real.** Ele não tem média bem definida no longo prazo, não
some com integração (a variância da média não cai como 1/N), e é o que limita a
estabilidade de longo prazo de osciladores, sensores e amplificadores. Onde há
1/f, **integrar mais tempo pode piorar** — e é por isso que existe a técnica de
*chopping* (modular o sinal para longe do 1/f, medir, e demodular).

---

## 4 · 🔑 Wiener-Khinchin: o teorema que salva o espectro

```
S(f) = 𝓕{ R[k] }
```

**A densidade espectral de potência é a transformada de Fourier da
autocorrelação.** Isso resolve o problema da §1: a transformada de x não existe,
mas a de R[k] existe, porque R[k] decai.

### Verificação numérica

Para um AR(1), a teoria dá S(ω) = σ²/|1 − a·e^{−jω}|². Comparando com o
estimador de Welch:

```
correlação Welch × teoria: 0.9827
razão média Welch/teoria:  2.001
```

(Saída real.) A **correlação de 0,98** confirma o formato; a **razão de 2,001** é
esperada e não é erro: `signal.welch` devolve densidade **unilateral** (toda a
potência dobrada no lado positivo), e a fórmula teórica é bilateral. Fator 2 exato.

**Guarde o hábito:** ao comparar sua medida com uma fórmula de livro, confira
primeiro a **convenção** (unilateral × bilateral, ω × f, RMS × pico). Metade dos
"desacordos" da literatura são fatores 2 ou 2π de convenção.

---

## 5 · Ruído através de um sistema LTI

Entra ruído com DEP S_x(f), sai ruído com

```
S_y(f) = |H(f)|² · S_x(f)
```

**Módulo ao quadrado**, porque potência. A fase de H **não afeta** a DEP da saída
— ela mexe na forma de onda, não na distribuição de potência.

Consequências práticas:

- **Ruído branco filtrado vira colorido**, com a cor da resposta do filtro.
  É assim que se sintetiza ruído com espectro arbitrário: filtre branco.
- A **potência total** de saída é ∫|H|²S_x df. Para ruído branco de densidade N₀,
  isso vira N₀ × (largura de banda equivalente de ruído do filtro).
- **Largura de banda equivalente de ruído (ENBW)** ≠ largura a −3 dB. Para um
  filtro RC de 1 polo, ENBW = (π/2)·f₃dB ≈ 1,57·f₃dB. Confundir os dois é erro de
  ~2 dB no orçamento de ruído — e é um erro comum em folha de especificação.

---

## 6 · As fontes físicas de ruído

| Fonte | Origem | DEP | Como reduzir |
|---|---|---|---|
| **Térmico (Johnson-Nyquist)** | agitação térmica dos portadores | branca, 4kTR V²/Hz | **resfriar**; reduzir R |
| **Shot** | quantização da carga elétrica | branca, 2qI A²/Hz | mais corrente não ajuda (cresce com √I) |
| **1/f (flicker)** | armadilhas e defeitos no material | 1/f | *chopping*, escolha de processo |
| **Quantização** | arredondamento do A/D | ~branca, Δ²/12 | mais bits, dither, sobreamostragem |
| **Interferência (RFI/EMI)** | outros sistemas | qualquer coisa | blindagem, aterramento, filtragem |

**Nota honesta:** os quatro primeiros são físicos e têm modelo. O quinto — a
interferência — é o que **domina** na prática, não tem modelo, não é gaussiano, e
consome mais engenharia que todos os outros somados. Todo modelo de detecção
deste curso assume ruído gaussiano; dados reais têm caudas muito mais pesadas, e
é por isso que limiares práticos são bem mais conservadores que os teóricos
(ver [`08-projeto-espacial/02`](08-projeto-espacial/02-a-fisica-do-sinal.md)).

---

## 7 · Estimar as estatísticas

| Grandeza | Estimador | Cuidado |
|---|---|---|
| média | `x.mean()` | erro ∝ σ/√N |
| variância | `x.var(ddof=1)` | **`ddof=1`**: com ddof=0 o estimador é enviesado |
| autocorrelação | `signal.correlate(x, x)` | dividir por N (enviesado, suave) ou por N−k (não enviesado, ruidoso nas caudas) |
| DEP | `signal.welch` | ver [`20 §4`](20-analise-espectral-e-janelas.md) |
| histograma | `np.histogram` | verifique a gaussianidade antes de assumi-la |

**Duas verificações que quase ninguém faz e que economizam meses:**

1. **Plote o histograma** do seu "ruído" e compare com a gaussiana. Se tiver
   caudas pesadas ou assimetria, todo o cálculo de limiar está otimista.
2. **Plote a autocorrelação.** Se ela não cair rápido, suas amostras não são
   independentes, e todo N que você usou em "√N" está errado — o **número
   efetivo** de amostras independentes é menor.

O segundo ponto é sutil e caro: com amostras correlacionadas, promediar N delas
**não** reduz o ruído por √N. O ganho real usa N_efetivo = N/(1 + 2Σρ[k]).

---

## Os cinco porquês: por que o ruído térmico é gaussiano e branco?

1. **Por que gaussiano?** Porque é a soma das contribuições de um número enorme
   de portadores de carga independentes.
2. **Por que a soma tende à gaussiana?** **Teorema central do limite**: a soma de
   muitas variáveis independentes de variância finita converge para a gaussiana,
   qualquer que seja a distribuição individual.
3. **Por que branco?** Porque as contribuições são descorrelacionadas em escalas
   de tempo muito maiores que o tempo médio entre colisões dos portadores (~10⁻¹³ s
   em metais).
4. **Por que essa escala importa?** Porque o espectro só "sente" a correlação em
   frequências comparáveis a 1/(tempo de correlação) — ou seja, ~10 THz. Abaixo
   disso, plano.
5. **Então ruído branco existe de verdade?** Não exatamente: acima de ~10 THz o
   espectro cai, e a mecânica quântica impõe o fator de Planck
   hf/(e^{hf/kT}−1) em vez de kT. **Parada legítima: uma lei física.** "Branco"
   significa "plano na banda que me interessa", e essa é a única definição
   operacional honesta.

---

## Autoteste

1. Por que um sinal aleatório não tem transformada de Fourier, e o que se usa?
2. Enuncie estacionaridade e ergodicidade, e diga por que são hipóteses.
3. A autocorrelação de um AR(1) com a=0,9 vale quanto em k=3? Confirme.
4. Enuncie Wiener-Khinchin e diga que problema ele resolve.
5. Sua medida deu o dobro da fórmula do livro. Qual a primeira coisa a conferir?
6. Como se sintetiza ruído com espectro arbitrário?
7. Por que ENBW ≠ largura a −3 dB, e qual o erro típico ao confundir?
8. Por que integrar mais tempo pode não ajudar contra ruído 1/f?
9. Suas amostras são correlacionadas. O que isso faz com o ganho √N?
10. Qual fonte de ruído domina na prática e por que ela não tem modelo?
