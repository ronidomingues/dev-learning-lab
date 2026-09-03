# 12 · A matemática do zero — exatamente a que se usa, na ordem em que se usa

`Nível: iniciante → intermediário` · `Atualizado em: 14/08/2026`

Este é o arquivo mais importante para quem perguntou *"o que de matemática se deve
aprender?"*. Ele não é um curso de matemática genérico: é **a fatia que o
processamento de sinais realmente usa**, com cada conceito amarrado a onde ele
aparece.

Regra de leitura: **em cada seção, o item marcado 🔑 é o que você não pode pular.**
O resto pode ser aprendido sob demanda.

---

## Mapa da dependência

```
        Aritmética + logaritmo (§1)
                  │
                  ▼
        Trigonometria circular (§2) ─────┐
                  │                      │
                  ▼                      ▼
     🔑 Números complexos + Euler (§3)   Somatórios e séries (§4)
                  │                      │
                  └──────────┬───────────┘
                             ▼
                    Fourier, DFT, filtros
                             ▲
              ┌──────────────┼──────────────┐
              │              │              │
        Cálculo (§5)   Álgebra linear (§6)  Probabilidade (§7)
        (sinais         (a visão que        (ruído, estimação,
         contínuos)      simplifica tudo)    filtro adaptativo)
```

Se você só tem tempo para uma coisa: **§3, números complexos.**

---

## §1 · Aritmética de sobrevivência: potências, logaritmos e decibéis

### O que saber

| Item | Regra | Onde usa |
|---|---|---|
| Potência | aᵐ·aⁿ = a^{m+n}; (aᵐ)ⁿ = a^{mn} | tudo |
| Logaritmo | log(ab) = log a + log b; log(aⁿ) = n·log a | dB, escala musical |
| Mudança de base | log₂ x = ln x / ln 2 = log₁₀x / log₁₀2 | bits, oitavas |
| Exponencial natural | e ≈ 2,71828; eˣ é sua própria derivada | 🔑 tudo em §3 e §5 |

### Por que logaritmo é onipresente aqui

Porque a percepção humana é logarítmica (lei de Weber-Fechner) e porque os sinais
têm faixa dinâmica enorme. Um áudio vai de 10⁻⁵ a 1 em amplitude; num gráfico
linear você vê uma linha reta em zero. Em dB, vê tudo.

**Decibel:**

```
dB de amplitude = 20·log₁₀(A/A_ref)
dB de potência  = 10·log₁₀(P/P_ref)
```

Por que 20 e 10? Porque potência ∝ amplitude², e log(A²) = 2·log(A). É a **mesma**
fórmula; o fator 2 vem da física, não de convenção.

**Tabela para decorar** (vale mais que a fórmula na hora do aperto):

| Razão de amplitude | dB | Razão de potência | dB |
|---|---|---|---|
| ×2 | +6,02 | ×2 | +3,01 |
| ×10 | +20 | ×10 | +10 |
| ×√2 = 1,414 | +3,01 | ×1,414 | +1,5 |
| ×0,5 | −6,02 | ×0,5 | −3,01 |
| ×1000 | +60 | ×1000 | +30 |

**Exercício resolvido.** Um filtro atenua um tom de amplitude 1,0 para 0,001.
Quantos dB? 20·log₁₀(0,001) = 20·(−3) = **−60 dB**. E quanto sobrou de potência?
0,001² = 10⁻⁶ = **−60 dB** também — em potência a conta é 10·log₁₀(10⁻⁶) = −60.
As duas dão o mesmo número porque é o mesmo fenômeno. Confundir 20 e 10 quando
você tem só um dos dois em mãos é que erra por fator 2.

### Escala musical: logaritmo com nome próprio

Uma oitava = ×2 em frequência. Um semitom = ×2^{1/12}. Um cent = ×2^{1/1200}.

```
diferença em cents = 1200·log₂(f₂/f₁)
```

O afinador do [`07-projeto-modelo/`](07-projeto-modelo/README.md) é exatamente
esta linha.

**Tempo de estudo: 2 dias** se você já viu logaritmo alguma vez.

---

## §2 · Trigonometria circular — não a do triângulo

### A mudança de ponto de vista

Esqueça "cateto oposto sobre hipotenusa". A definição útil aqui:

> Um ponto gira no círculo de raio 1. Seu ângulo com o eixo x é θ.
> **cos θ é a coordenada horizontal. sen θ é a vertical.**

```
              y
              │      ● (cos θ, sen θ)
              │     ╱│
              │    ╱ │ sen θ
              │  1╱  │
              │  ╱θ  │
    ──────────┼─────────── x
              │  cos θ
```

Daí saem, sem decorar:
- sen²θ + cos²θ = 1 (Pitágoras no círculo de raio 1)
- cos é par (cos(−θ) = cos θ), sen é ímpar (sen(−θ) = −sen θ)
- período 2π
- cos θ = sen(θ + π/2) — o cosseno é o seno adiantado de 90°

### O sinal senoidal completo

```
x(t) = A·cos(2π·f·t + φ)
        │        │      └── fase inicial, em radianos
        │        └── frequência, em Hz
        └── amplitude
```

`ω = 2πf` (rad/s) e o argumento é `ωt + φ`. Um ciclo completo = 2π radianos.
Se f = 440 Hz, o ponto dá 440 voltas por segundo.

**Interpretação que vale ouro:** a fase φ é um **atraso disfarçado**.
cos(ω(t − t₀)) = cos(ωt − ωt₀), então φ = −ω·t₀. Um atraso fixo t₀ produz uma fase
**proporcional à frequência** — é exatamente por isso que "fase linear" significa
"atraso constante para todas as frequências", e por que fase não linear distorce a
forma de onda ([`18`](18-filtros-fir.md)).

### 🔑 As três identidades que você vai usar de verdade

```
(1)  cos(A ± B) = cos A·cos B ∓ sen A·sen B
(2)  sen(A ± B) = sen A·cos B ± cos A·sen B
(3)  cos A·cos B = ½[cos(A−B) + cos(A+B)]        ← produto vira soma
```

**A (3) é o coração do rádio.** Multiplicar dois senos de frequências f₁ e f₂
produz a **soma** e a **diferença** das frequências. É isso, e só isso, que faz um
misturador (mixer) funcionar: para descer um sinal de 100 MHz para 10 MHz, você
multiplica por um oscilador de 90 MHz e filtra a diferença. Rádio inteiro,
numa identidade trigonométrica.

Verificação em código:

```python
import numpy as np
fs = 10000; t = np.arange(fs)/fs
y = np.cos(2*np.pi*1000*t) * np.cos(2*np.pi*1200*t)
X = np.abs(np.fft.rfft(y)); f = np.fft.rfftfreq(len(t), 1/fs)
picos = f[np.argsort(X)[-2:]]
print(sorted(picos))       # [200.0, 2200.0]  ← a diferença e a soma
```

Saída real: `[np.float64(200.0), np.float64(2200.0)]`. 1200−1000 = 200 e
1200+1000 = 2200. A identidade não é abstrata; ela aparece no espectro.

**Tempo: 1 semana** para ficar confortável.

---

## §3 · 🔑 Números complexos — o pré-requisito que trava todo mundo

### Por que existem

Resolver x² = −1. A resposta "não existe" é uma escolha; a matemática decidiu
**inventar** um número j tal que j² = −1 e ver o que acontece. O que acontece é que
tudo passa a fechar: toda equação polinomial de grau n tem exatamente n raízes, e
rotação vira multiplicação.

> Em engenharia usa-se **j**, não *i*, porque *i* já significa corrente elétrica.
> Python usa `1j`.

### Forma retangular e forma polar

```
z = a + jb              (retangular: coordenadas no plano)
z = r·e^{jθ}            (polar: raio e ângulo)

r = |z| = √(a² + b²)          θ = ∠z = atan2(b, a)
a = r·cos θ                    b = r·sen θ
```

```
        Im
         │
       b ┤        ● z = a + jb
         │      ╱ │
         │   r╱   │
         │   ╱θ   │
    ─────┼──╱─────┴──── Re
         │        a
```

Em Python:

```python
import numpy as np
z = 3 + 4j
print(abs(z), np.angle(z), np.angle(z, deg=True))
# 5.0  0.9272952180016122  53.13010235415598
```

(Saída real, verificada.) Módulo 5 porque 3-4-5 é terno pitagórico.

### 🔑 A fórmula de Euler — a equação central do campo

```
e^{jθ} = cos θ + j·sen θ
```

**O que ela diz, em palavras:** e^{jθ} é o ponto do círculo unitário no ângulo θ.
Elevar e à potência imaginária **é girar**.

De onde vem: expanda eˣ, cos e sen em série de Taylor e substitua x = jθ. Os termos
reais reproduzem a série do cosseno, os imaginários a do seno. Não é coincidência
nem definição arbitrária — é consequência das séries.

**Corolários que você vai usar todo dia:**

| Fórmula | Significado |
|---|---|
| e^{jπ} = −1 | meia volta |
| e^{j2π} = 1 | volta completa: **e^{jθ} é periódica em 2π** |
| e^{jπ/2} = j | quarto de volta |
| cos θ = (e^{jθ} + e^{−jθ})/2 | **decompõe o cosseno em duas exponenciais** |
| sen θ = (e^{jθ} − e^{−jθ})/(2j) | idem |
| \|e^{jθ}\| = 1 | sempre no círculo unitário |
| (e^{jθ})* = e^{−jθ} | conjugar = girar ao contrário |

A linha do cosseno explica **por que o espectro de um sinal real é espelhado**: um
cosseno é a soma de uma frequência positiva e uma negativa, de amplitude ½ cada.
Frequência negativa não é misticismo: é a exponencial girando no sentido horário.

### 🔑 Multiplicação = rotação + escala

```
(r₁e^{jθ₁})·(r₂e^{jθ₂}) = (r₁r₂)·e^{j(θ₁+θ₂)}
```

Módulos multiplicam, ângulos **somam**. Toda a intuição de filtro está aqui:

- Um filtro tem resposta H(e^{jΩ}) = |H|·e^{j∠H} em cada frequência.
- Filtrar = multiplicar cada componente por esse número complexo.
- **|H| escala a amplitude, ∠H gira a fase (ou seja, atrasa).**

E multiplicar por e^{jΩ₀n} no tempo desloca o espectro em Ω₀ — é a modulação. O
mesmo fato, visto do outro lado.

### Conjugado e simetria hermitiana

Se x[n] é **real**, então X[−k] = X[k]*. Consequências práticas:

1. Metade do espectro é redundante ⟹ `np.fft.rfft` devolve N/2+1 valores.
2. A magnitude é **par** (espelhada) e a fase é **ímpar**.
3. Se você modificar um espectro à mão e quiser um sinal real de volta, tem de
   preservar essa simetria — senão a IFFT devolve um sinal complexo. Este é o bug
   nº 1 de quem tenta filtrar "editando o espectro".

### Raízes da unidade: os bins da DFT

As N soluções de z^N = 1 são `W_N^k = e^{j2πk/N}`, k = 0..N−1: N pontos igualmente
espaçados no círculo unitário.

**Isso é literalmente a DFT.** Cada bin k testa a componente na frequência
correspondente à k-ésima raiz da unidade. E a soma de todas as N raízes é zero —
propriedade que faz a ortogonalidade da DFT funcionar (§6).

```python
N = 8
raizes = np.exp(2j*np.pi*np.arange(N)/N)
print(np.abs(np.sum(raizes)))     # 3.4e-16  ← zero numérico
```

### Roteiro de estudo (5 dias)

| Dia | Faça |
|---|---|
| 1 | Retangular, polar, módulo, fase, conjugado. Plote 20 números complexos |
| 2 | Multiplicação como rotação. Multiplique por j quatro vezes e veja voltar |
| 3 | Euler. Plote `np.exp(1j*2*np.pi*np.arange(100)/100)` e reconheça o círculo |
| 4 | Decomponha cos e sen em exponenciais. Confirme numericamente |
| 5 | Raízes da unidade e sua relação com os bins da DFT |

**Teste de saída:** explique, sem consultar, por que multiplicar um sinal por
e^{jΩ₀n} desloca o espectro. Se conseguir, siga.

---

## §4 · Somatórios e séries — o cavalo de batalha do discreto

### Notação

```
Σ_{n=0}^{N−1} x[n]  =  x[0] + x[1] + ... + x[N−1]
```

Propriedades que você usa sem perceber: linearidade (`Σ(a·x+b·y) = a·Σx + b·Σy`),
troca de variável (`n → n−k`), e troca de ordem em somatório duplo — esta última é
o passo central na prova do teorema da convolução.

### 🔑 A soma geométrica

```
Σ_{n=0}^{N−1} rⁿ = (1 − r^N)/(1 − r),   para r ≠ 1
Σ_{n=0}^{∞}   rⁿ = 1/(1 − r),           para |r| < 1
```

**Uma fórmula, quatro usos centrais:**

1. **Resposta em frequência da média móvel.** Com r = e^{−jΩ}:
   Σ e^{−jΩn} = (1 − e^{−jΩN})/(1 − e^{−jΩ}), que dá a função **sinc digital**
   (kernel de Dirichlet), com zeros em Ω = 2πk/N. Foi o que vimos em
   [`10 §4`](10-fundamentos.md): a média móvel de 5 tem zeros em fs/5 e 2fs/5.
2. **Estabilidade de IIR.** Um filtro com h[n] = aⁿ·u[n] é estável se e só se
   Σ|a|ⁿ converge, ou seja **|a| < 1** — o polo tem de estar dentro do círculo
   unitário. Todo o critério de estabilidade de [`17`](17-transformada-z.md) é
   esta linha.
3. **Transformada Z de uma exponencial:** Σ aⁿz^{−n} = 1/(1 − az^{−1}), para |z| > |a|.
   A "região de convergência" é literalmente onde a série geométrica converge.
4. **Ortogonalidade da DFT:** Σ_{n} e^{j2π(k−m)n/N} = N se k=m, 0 caso contrário —
   soma geométrica com razão e^{j2π(k−m)/N}, cujo numerador zera.

**Se você entender bem essa única fórmula, três capítulos deste curso ficam fáceis.**

**Tempo: 3 dias.**

---

## §5 · Cálculo — só o que se usa

### Derivada

Taxa de variação instantânea. Em DSP:

| Conceito | Uso |
|---|---|
| d/dt e^{at} = a·e^{at} | 🔑 a exponencial é autofunção da derivada. É **a razão** de Fourier funcionar |
| derivada de senoide = senoide adiantada de 90° | derivar = multiplicar por jω na frequência |
| diferença finita `x[n]−x[n−1]` | a derivada discreta. É um filtro passa-**alta** de resposta `1−z⁻¹` |
| máximo tem derivada zero | interpolação parabólica de pico ([`16`](16-dft-e-fft.md)), otimização de filtro |

**Fato que organiza tudo:** no domínio da frequência, **derivar é multiplicar por
jω**. Por isso derivada amplifica altas frequências — e por isso derivar um sinal
ruidoso é péssima ideia: o ruído está em cima, e você o multiplica por ω.

### Integral

Área acumulada. Em DSP:

| Conceito | Uso |
|---|---|
| ∫ de senoide num período = 0 | 🔑 base da ortogonalidade e de toda análise de Fourier |
| ∫ x(t)·e^{−j2πft} dt | **é** a transformada de Fourier: correlação com uma exponencial |
| soma acumulada `y[n]=y[n−1]+x[n]` | a integral discreta. Filtro `1/(1−z⁻¹)`, polo em z=1 |
| energia = ∫\|x\|² | Parseval |

**Integrar é dividir por jω** na frequência — atenua agudos, amplifica graves.
E o polo em z = 1 (em cima do círculo unitário) explica por que um integrador
digital é **marginalmente estável**: qualquer nível DC na entrada faz a saída
crescer sem limite. Todo integrador prático tem vazamento (`y = 0.999·y + x`)
justamente por isso.

### O que NÃO precisa

Técnicas de integração por partes exóticas, séries de Taylor formais, épsilon-delta,
integrais múltiplas, EDPs. Se um dia precisar, aprende.

### Uma sutileza honesta: o delta de Dirac

δ(t) não é função: é uma **distribuição**, definida pelo que faz dentro de uma
integral (∫f(t)δ(t−a)dt = f(a)). Tratá-la como "função infinita num ponto" funciona
para engenharia e é o que todo livro de DSP faz. A formalização rigorosa (teoria
das distribuições de Schwartz) só importa em matemática. **Você pode usar sem
culpa** — mas saiba que é uma abreviação, para não se surpreender quando um
matemático objetar.

**Tempo: 3–4 semanas.** Pode ser feito em paralelo com o resto do curso.

---

## §6 · Álgebra linear — a visão que simplifica tudo

Se este arquivo tem uma seção subestimada, é esta.

### Sinal é vetor

Um sinal de N amostras **é** um vetor em ℝᴺ (ou ℂᴺ). Isso não é analogia: é
identidade. Consequências imediatas:

| Operação de sinal | O que é em álgebra linear |
|---|---|
| energia Σx[n]² | norma ao quadrado, ‖x‖² |
| correlação Σx[n]y[n] | **produto interno** ⟨x, y⟩ |
| filtrar | multiplicar por uma matriz (Toeplitz, no caso LTI) |
| Fourier | **mudança de base** |
| projetar filtro ótimo | mínimos quadrados |

### 🔑 Produto interno e ortogonalidade

```
⟨x, y⟩ = Σ_n x[n]·y[n]*        (conjuga o segundo, no caso complexo)
```

Dois sinais são **ortogonais** se ⟨x, y⟩ = 0. Interpretação: não têm nada em comum,
não se "misturam".

**O fato central de Fourier:** as exponenciais complexas e^{j2πkn/N}, para
k = 0..N−1, são **mutuamente ortogonais**. Prova: o produto interno vira uma soma
geométrica (§4) que dá 0 para k ≠ m e N para k = m.

Por isso o espectro é bem definido: cada bin mede uma componente que **não** é
contaminada pelas outras. Se a base não fosse ortogonal, "a energia em 440 Hz" não
teria significado único.

```python
N = 64
def e(k): return np.exp(2j*np.pi*k*np.arange(N)/N)
print(abs(np.vdot(e(3), e(3))), abs(np.vdot(e(3), e(7))))
# 64.0  2.4e-15   ← ortogonais
```

### 🔑 Base e mudança de base — Fourier em cinco palavras

Uma **base** é um conjunto de vetores em que todo sinal se escreve de forma única.

- **Base canônica** (impulsos δ[n−k]): as coordenadas são as próprias amostras.
  Diz **quando** as coisas acontecem.
- **Base de Fourier** (exponenciais): as coordenadas são os X[k]. Diz **em que
  frequência**.

> **A Transformada de Fourier é uma mudança de base ortogonal.**

Nada mais. A DFT é uma matriz N×N cujas linhas são as exponenciais; a IDFT é sua
inversa (que, sendo a base ortonormal a menos de escala, é só a transposta
conjugada dividida por N). A FFT é um jeito esperto de **fatorar essa matriz** em
log N matrizes esparsas.

```python
N = 8
F = np.exp(-2j*np.pi*np.outer(np.arange(N), np.arange(N))/N)   # matriz da DFT
x = np.random.default_rng(0).standard_normal(N)
print(np.allclose(F @ x, np.fft.fft(x)))    # True
```

Saída real: `True`. A DFT literalmente é um produto matriz-vetor.

### Matriz como transformação

Uma matriz leva vetores em vetores. Um filtro LTI corresponde a uma matriz de
**convolução** (Toeplitz: constante ao longo das diagonais). Invariância no tempo =
diagonais constantes. É bonito ver a propriedade abstrata virar geometria da matriz.

### 🔑 Autovalores e autovetores — por que Fourier "funciona"

`A·v = λ·v`: a matriz não muda a direção de v, só a escala.

**Toda matriz de convolução circular tem as exponenciais complexas como
autovetores, e os valores da DFT da resposta ao impulso como autovalores.**

Traduzindo: diagonalizar um sistema LTI **é** fazer Fourier. A frase de
[`10 §5`](10-fundamentos.md) — "senoides são os autovetores dos sistemas LTI" —
é isto, dito em álgebra linear. E é por isso que na base de Fourier a convolução
vira multiplicação: numa base de autovetores, todo operador é diagonal.

Se você absorver só esta ideia deste arquivo inteiro, já valeu.

### Mínimos quadrados

Achar x que minimiza ‖Ax − b‖². Solução: `x = (AᵀA)⁻¹Aᵀb` (equações normais).
Onde aparece:

- **Filtro de Wiener** ([`23`](23-estimacao-e-filtragem-adaptativa.md)): melhor
  filtro linear no sentido do erro quadrático médio.
- **`firls`**: projeto de FIR por mínimos quadrados.
- **Savitzky-Golay**: ajusta um polinômio por mínimos quadrados a cada janela.
- **Predição linear (LPC)**: prever x[n] a partir dos p anteriores — a base da
  codificação de voz em todo celular.

**Tempo: 3–4 semanas** para o essencial. Assista *Essence of Linear Algebra*
(3Blue1Brown) num fim de semana para a intuição, e depois formalize.

---

## §7 · Probabilidade — porque o mundo tem ruído

### O básico

| Conceito | Fórmula | Em DSP |
|---|---|---|
| Média (valor esperado) | μ = E{X} | nível DC |
| Variância | σ² = E{(X−μ)²} | **potência** do ruído |
| Desvio padrão | σ | amplitude RMS do ruído |
| Gaussiana | densidade e^{−(x−μ)²/2σ²} | ruído térmico, pelo teorema central do limite |
| Independência | p(x,y) = p(x)p(y) | amostras de ruído branco |
| Covariância / correlação | E{(X−μx)(Y−μy)} | quanto dois sinais "andam juntos" |

**Por que gaussiana em toda parte:** teorema central do limite. Ruído térmico é a
soma de bilhões de contribuições independentes de elétrons; a soma tende à
gaussiana independentemente da distribuição de cada uma. Não é conveniência
matemática — é consequência.

### Processo estocástico

Um sinal aleatório é uma **família** de sinais possíveis. Você observa uma
realização, quer concluir sobre a família.

| Conceito | O que significa | Por que importa |
|---|---|---|
| **Estacionário** (WSS) | média e autocorrelação não mudam com o tempo | sem isso, "o espectro" não está definido |
| **Ergódico** | média temporal = média estatística | permite estimar tudo de **uma** gravação |
| **Autocorrelação** R[k] | E{x[n]·x[n+k]} | estrutura de repetição do sinal |
| **DEP / PSD** S(f) | Fourier de R[k] (**Wiener-Khinchin**) | "espectro" de sinal aleatório |
| **Ruído branco** | R[k] = σ²δ[k] | espectro plano; amostras descorrelacionadas |

⚠️ **Ergodicidade é uma hipótese, não um fato.** Quase toda medição prática assume
que você pode estimar a estatística de um processo a partir de uma gravação. Fala
não é estacionária (por isso se analisa em janelas de 20–30 ms). Assumir
estacionaridade onde ela não vale é a origem de um número enorme de resultados
errados publicados — e é a razão de o espectrograma existir.

**Wiener-Khinchin** é o que conecta os dois mundos: para sinal aleatório, a
transformada de Fourier da autocorrelação **é** a densidade espectral de potência.
É o que permite falar de espectro de ruído, coisa que a transformada de Fourier
comum não consegue (ruído não tem energia finita).

**Tempo: 2–3 semanas.** Pode ficar para depois do capítulo 20.

---

## §8 · O que fica para depois (e só se você for para pesquisa)

| Assunto | Quando você vai precisar |
|---|---|
| Análise complexa (resíduos, Cauchy) | derivação rigorosa da Z inversa |
| Espaços de Hilbert, L² | formalização de Fourier e wavelets |
| Teoria da medida / Lebesgue | provas de convergência |
| Otimização convexa | projeto ótimo de filtro, compressive sensing |
| Teoria da informação | codificação, limites de compressão |
| Álgebra abstrata (grupos) | FFT em índices não potência de 2, transformadas em corpos finitos |
| Estatística bayesiana | filtro de partículas, inferência moderna |

**Nada disso bloqueia começar. Nada disso bloqueia trabalhar.**

---

## Roteiro completo com prazos

Para 6–8 h/semana. Faça **em paralelo** com os capítulos de DSP indicados.

| Semanas | Matemática | Estude junto |
|---|---|---|
| 1 | §1 logaritmo e dB, §2 trigonometria | [`01`](01-introducao-leigo.md), [`04`](04-como-comecar.md) |
| 2–3 | **§3 números complexos e Euler** 🔑 | [`10`](10-fundamentos.md) |
| 3 | §4 somatórios e série geométrica | [`13`](13-sinais-e-sistemas-lti.md) |
| 4–7 | §5 cálculo essencial | [`14`](14-fourier.md), [`15`](15-amostragem-e-quantizacao.md) |
| 6–9 | §6 álgebra linear | [`16`](16-dft-e-fft.md), [`18`](18-filtros-fir.md) |
| 10–12 | §7 probabilidade | [`22`](22-ruido-e-processos-estocasticos.md), [`23`](23-estimacao-e-filtragem-adaptativa.md) |

**Total: ~3 meses de matemática, feitos simultaneamente com ~3 meses de DSP.**
Não são 6 meses em série. Estudar os dois juntos é mais rápido *e* mais eficaz,
porque cada conceito matemático chega junto com o problema que o justifica.

---

## Onde estudar cada coisa (gratuito)

| Assunto | Português | Inglês |
|---|---|---|
| Trigonometria, logaritmo | Khan Academy PT-BR; Univesp (YouTube) | Khan Academy |
| Números complexos | Univesp, Matemática Universitária (YouTube) | *Imaginary Numbers Are Real* (Welch Labs) |
| Cálculo | Khan Academy PT-BR; Univesp Cálculo I | MIT OCW 18.01 |
| Álgebra linear | Univesp Álgebra Linear; IMPA (canal) | **3Blue1Brown, *Essence of Linear Algebra*** ← comece por aqui |
| Probabilidade | Univesp; Khan Academy PT-BR | MIT OCW 6.041 / *Seeing Theory* (Brown) |
| Fourier (intuição) | — | 3Blue1Brown, "But what is the Fourier Transform?" |

Links, durações e avaliação honesta de cada um em
[`85-cursos-e-certificacoes.md`](85-cursos-e-certificacoes.md).

---

## Autoteste

1. Um sinal cai de amplitude 1,0 para 0,25. Quantos dB em amplitude? E em potência?
2. Por que a identidade cos A·cos B = ½[cos(A−B)+cos(A+B)] é a base do rádio?
3. Explique geometricamente por que e^{jπ} = −1.
4. Por que o espectro de um sinal real é espelhado? Use a decomposição do cosseno.
5. Escreva a soma geométrica e mostre como ela dá o critério |a|<1 de estabilidade.
6. Complete: "A Transformada de Fourier é uma ______ de ______ ortogonal".
7. O que são os autovetores de um sistema LTI, e o que isso tem a ver com Fourier?
8. Por que ruído térmico é gaussiano?
9. O que é ergodicidade e por que assumi-la indevidamente causa erro?
10. Qual é o único pré-requisito matemático que eu trataria como bloqueante?
