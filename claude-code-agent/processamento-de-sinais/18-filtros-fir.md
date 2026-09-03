# 18 · Filtros FIR — projeto, custo e fase linear

`Nível: intermediário → avançado` · `Medições feitas em: 14/08/2026`
`Base: SciPy 1.15.3`

FIR = *Finite Impulse Response*. Sem realimentação: a saída é uma soma ponderada
das últimas N entradas, e nada mais.

```
y[n] = Σ_{k=0}^{N−1} h[k]·x[n−k]
```

É a convolução do [`10 §3`](10-fundamentos.md) escrita como código. Os `h[k]` são
os **coeficientes** ou **taps**.

---

## 1 · Por que escolher FIR

| Vantagem | Consequência |
|---|---|
| **Sempre estável** | não há polos (todos em z=0). Impossível explodir |
| **Fase linear exata** | se h for simétrico. Atraso igual para todas as frequências |
| Erro de arredondamento **não** realimenta | seguro em ponto fixo |
| Projeto direto e previsível | você especifica, a ferramenta entrega |
| Fácil de paralelizar / vetorizar | é um produto interno |

| Desvantagem | Consequência |
|---|---|
| **Muitos coeficientes** | 10 a 100× mais que um IIR equivalente |
| Atraso grande | (N−1)/2 amostras. Pode inviabilizar tempo real |
| Custo de CPU e memória | proporcional a N |

**A regra de bolso que decide:** se você precisa de fase linear ou de garantia
absoluta de estabilidade, FIR. Se precisa de corte agudo com pouquíssimas operações
e tolera distorção de fase, IIR ([`19`](19-filtros-iir.md)).

---

## 2 · 🔑 Fase linear — a propriedade que só o FIR tem

Se `h[k] = h[N−1−k]` (simétrico), então:

```
H(e^{jΩ}) = e^{−jΩ(N−1)/2} · A(Ω),      com A(Ω) REAL
```

A fase é `−Ω(N−1)/2`: uma reta. Atraso de grupo constante = **(N−1)/2 amostras**,
igual para todas as frequências. O sinal atrasa **inteiro**, sem deformar.

Foi medido em [`13 §5`](13-sinais-e-sistemas-lti.md): FIR de 51 taps deu atraso de
grupo 25,00 amostras do início ao fim da banda, enquanto um Butterworth de mesma
ordem variou de 3,8 a 6,6.

### Os quatro tipos de FIR de fase linear

Isto parece burocracia e **não é**: escolher o tipo errado torna o filtro
impossível de projetar.

| Tipo | Simetria | N | H(z=1) (DC) | H(z=−1) (Nyquist) | Serve para |
|---|---|---|---|---|---|
| **I** | par (h[k]=h[N−1−k]) | ímpar | livre | livre | qualquer filtro |
| **II** | par | par | livre | **forçado a 0** | só passa-baixa |
| **III** | ímpar (h[k]=−h[N−1−k]) | ímpar | **0** | **0** | Hilbert, diferenciador |
| **IV** | ímpar | par | **0** | livre | Hilbert, diferenciador, passa-alta |

**Traduzindo o que importa:**

- Tipo II tem um **zero obrigatório em Nyquist**. Um passa-alta precisa de ganho em
  Nyquist. Logo: **passa-alta com N par é impossível.** É por isso que a SciPy
  reclama e por isso o `07-projeto-modelo/` recusa `n_taps` par.
- Tipos III e IV têm zero obrigatório em DC, o que os torna inúteis para passa-baixa
  e perfeitos para diferenciador (que deve ter ganho 0 em DC) e para transformador
  de Hilbert.

**Regra prática que evita o assunto inteiro:** use **N ímpar** (tipo I). Serve para
tudo e dá atraso de grupo inteiro, o que permite compensar o atraso com um simples
deslocamento de índice.

---

## 3 · Método 1: janelamento

O mais intuitivo, e o que ensina mais.

**Passo 1.** A resposta ao impulso do passa-baixa **ideal** é uma sinc infinita:

```
h_ideal[n] = 2·f_c·sinc(2·f_c·n),      n ∈ (−∞, ∞)
```

**Passo 2.** Truncar em N pontos. Isso já dá um filtro — e dá o **ripple de Gibbs**
que vimos em [`13 §6`](13-sinais-e-sistemas-lti.md): rejeição de apenas ~−21 dB,
que não melhora com N.

**Passo 3.** Multiplicar por uma **janela** que vai suavemente a zero nas bordas.
A rejeição melhora dramaticamente; a transição fica mais larga.

```python
import numpy as np
from scipy import signal
h = signal.firwin(101, 1000, fs=8000, window='hamming')
```

### As janelas, medidas

Propriedades reais, medidas com N = 64 e 128× de zero-padding:

```
janela            lobo lateral  largura -3dB  ganho coerente
boxcar                  -13.3 dB         0.89          1.000
hann                    -31.5 dB         1.45          0.500
hamming                 -42.4 dB         1.31          0.540
blackman                -58.1 dB         1.66          0.420
blackmanharris          -92.0 dB         1.91          0.359
flattop                 -88.2 dB         3.73          0.216
kaiser(8.6)             -63.4 dB         1.64          0.421
```

**Leia como uma tabela de troca, porque é exatamente isso:**

- **Retangular:** lóbulo principal mais estreito de todos (0,89 bin) e lóbulo
  lateral péssimo (−13 dB). Máxima resolução, mínima rejeição.
- **Blackman-Harris:** rejeição de −92 dB e lóbulo 2,1× mais largo. O contrário.
- **Hamming** é o meio-termo clássico: −42 dB com lóbulo estreito (1,31 — mais
  estreito que a Hann!). É o padrão do `firwin` por bom motivo.
- **Flattop** tem lóbulo enorme (3,73) de propósito: ela é feita para medir
  **amplitude** com exatidão, não frequência. Use quando o número que importa é
  "quantos volts tem esse tom", não "em que frequência ele está".
- **Kaiser(β)** é ajustável: β=0 vira retangular, β≈8,6 fica próxima da Blackman.
  Um parâmetro contínuo em vez de um catálogo — por isso é a preferida em projeto.

O **ganho coerente** é a média da janela. Ele é a razão de você precisar dividir por
`sum(w)` e não por `N` ao normalizar amplitude ([`16 §6`](16-dft-e-fft.md)): com
Hann, esquecer isso dá exatamente 6 dB de erro (0,5 → −6,02 dB).

### Quantos taps? A fórmula de Kaiser

```python
from scipy import signal
fs = 8000
for rip in [40, 60, 80]:
    n, beta = signal.kaiserord(rip, width=200/(fs/2))
    print(f"  rejeição {rip} dB, transição 200 Hz -> {n} taps, beta={beta:.3f}")
```

Saída real:

```
  rejeição 40 dB, transição 200 Hz -> 91 taps, beta=3.395
  rejeição 60 dB, transição 200 Hz -> 147 taps, beta=5.653
  rejeição 80 dB, transição 200 Hz -> 202 taps, beta=7.857
```

**Cada 20 dB de rejeição a mais custa ~55 taps**, com a transição fixa. E a relação
com a transição é inversa: metade da largura de transição, o dobro dos taps.

Verificação da regra de bolso `N ≈ 4·fs/Δf`:

```
     21 taps: transição -1dB→-60dB =  1075.9 Hz   regra 4·fs/N =  1523.8 Hz
    101 taps: transição -1dB→-60dB =   208.3 Hz   regra 4·fs/N =   316.8 Hz
    401 taps: transição -1dB→-60dB =    51.5 Hz   regra 4·fs/N =    79.8 Hz
   1601 taps: transição -1dB→-60dB =    12.9 Hz   regra 4·fs/N =    20.0 Hz
```

(Saída real, `firwin` com Hamming, fs = 8 kHz, corte em 1 kHz.)

**Honestidade sobre a regra:** ela superestima em ~50 % com esta definição de
transição (−1 dB até −60 dB). O que a regra acerta, e é o que importa, é a
**proporcionalidade exata**: quadruplicar N dividiu a transição por ~4 em todos os
casos (1075,9 → 208,3 → 51,5 → 12,9). Use a regra para estimar a ordem de grandeza
e depois meça. **Nunca entregue um filtro que você não plotou.**

---

## 4 · Método 2: Parks–McClellan (equiripple) — o ótimo

O método da janela é simples e **não é ótimo**: ele gasta rejeição demais longe do
corte e de menos perto. O algoritmo de Parks–McClellan (Remez) resolve o problema
certo: *minimizar o erro máximo* (critério minimax) para uma dada ordem.

```python
h = signal.remez(101, [0, 900, 1200, 4000], [1, 0], fs=8000)
```

Comparação direta, mesmos 101 taps:

```
  firwin/hamming  rejeição máxima na banda de corte: -56.2 dB
  remez           rejeição máxima na banda de corte: -66.1 dB
```

(Saída real.) **10 dB de graça**, mesma ordem, mesmo custo de CPU. Por isso
Parks–McClellan é o padrão profissional desde 1972.

O preço: o ripple é **equiripple** — oscila com amplitude constante em toda a banda,
em vez de decair. Se sua especificação for "erro máximo", isso é ótimo. Se for
"erro quadrático médio", use `firls`.

| Função | Critério | Quando |
|---|---|---|
| `firwin` | truncar+janelar | rápido, previsível, bom o suficiente |
| `remez` | **minimax** (erro máximo mínimo) | quando a especificação é "nunca pior que X dB" |
| `firls` | **mínimos quadrados** | quando importa a energia do erro, não o pico |

⚠️ `remez` pode **não convergir** para especificações difíceis (bandas muito
estreitas, ordem muito baixa). Ele avisa com `RuntimeError`; a correção é aumentar
a ordem ou alargar a transição.

---

## 5 · Implementação: custo e como reduzi-lo

Custo direto: **N multiplicações e N adições por amostra de saída.**

Para áudio a 48 kHz com N=401: 401 × 48000 = **19,2 milhões de multiplicações por
segundo**, por canal. É muito para um microcontrolador e nada para um PC.

| Técnica | Ganho | Custo |
|---|---|---|
| **Simetria** (h[k]=h[N−1−k]) | **metade** das multiplicações | nenhum: some os pares antes de multiplicar |
| **FFT (overlap-add/save)** | O(log N) por amostra em vez de O(N) | latência de um bloco; vale a partir de N≈64 |
| **Multitaxa** (decimar → filtrar → interpolar) | pode dar 10× ou mais | complexidade de projeto ([`21`](21-multitaxa-e-bancos-de-filtros.md)) |
| **Coeficientes esparsos / potências de 2** | troca multiplicação por deslocamento | resposta pior |
| **Cascata de filtros curtos** | às vezes mais barato que um longo | projeto mais difícil |

O truque da simetria é grátis e quase ninguém usa em código próprio:

```
y[n] = Σ_{k=0}^{N/2−1} h[k]·(x[n−k] + x[n−N+1+k])      # metade das multiplicações
```

`signal.fftconvolve` e `signal.oaconvolve` já fazem a versão por FFT corretamente,
inclusive o zero-padding que evita a convolução circular de
[`16 §5`](16-dft-e-fft.md). **Use-as** em vez de escrever a sua.

---

## 6 · Casos especiais que valem conhecer

### Média móvel — o FIR mais barato do mundo

`h = [1/N, 1/N, ..., 1/N]`. Implementável **sem nenhuma multiplicação**, com um
acumulador corrente:

```python
y[n] = y[n-1] + (x[n] - x[n-N])/N     # 1 soma, 1 subtração, por amostra
```

Custo O(1) independente de N. É por isso que ela sobrevive em firmware. O defeito,
já mencionado em [`06 §12`](06-exemplos.md): resposta em sinc, lóbulos laterais a
apenas −13 dB, e **zeros** em múltiplos de fs/N — ela deixa passar quase intacta
qualquer coisa que caia entre os zeros.

### Filtro CIC (Cascaded Integrator-Comb)

Cascata de integradores e diferenciadores, **sem multiplicador nenhum**. É o filtro
de decimação padrão dentro de todo conversor sigma-delta e de todo receptor SDR.
Detalhe em [`21`](21-multitaxa-e-bancos-de-filtros.md).

### Transformador de Hilbert

FIR tipo III/IV que desloca todas as frequências em −90°. Gera o sinal analítico
usado para envoltória e frequência instantânea ([`06 §5`](06-exemplos.md)) e para
modulação de banda lateral única.

### Filtro casado

`h[n] = s[N−1−n]` — a própria coisa que você procura, invertida no tempo.
Comprovadamente ótimo para detecção em ruído branco gaussiano. É o exemplo 8 de
[`06`](06-exemplos.md), que achou um pulso a −3 dB de SNR com erro zero.

### Interpolador de atraso fracionário

Para atrasar por 0,3 amostra (necessário em sincronização de símbolo, correção de
tempo, *beamforming*), usa-se um FIR que aproxima a sinc deslocada — tipicamente
Lagrange de 3ª ordem ou Farrow.

---

## Os cinco porquês: por que fase linear exige simetria?

1. **Por que h simétrico dá fase linear?** Porque a soma dos pares
   h[k]·(e^{−jΩk} + e^{−jΩ(N−1−k)}) fatora em e^{−jΩ(N−1)/2}·2cos(...), e o que
   sobra é real.
2. **Por que "o que sobra é real" significa fase linear?** Porque a fase de um
   número real é 0 ou π; toda a variação angular está no fator exponencial, que é
   linear em Ω por construção.
3. **Por que o expoente é exatamente (N−1)/2?** Porque é o **centro** do filtro. A
   simetria é em torno desse ponto, e o centro de simetria é o atraso.
4. **Por que um IIR não consegue?** Porque fase linear exige h simétrico, e simetria
   exige h finito — um h infinito não tem centro. Um IIR causal e estável tem h
   infinito por definição.
5. **Por que não fazer um IIR "quase simétrico"?** É o que o `filtfilt` faz: rodar
   o IIR para frente e para trás produz fase exatamente zero. **E o preço é a
   causalidade** — você precisa do sinal inteiro, incluindo o futuro. **Parada
   legítima: um trade-off matemático.** Fase linear, causalidade e resposta infinita:
   escolha dois.

---

## Autoteste

1. Por que um FIR é sempre estável?
2. Qual é o atraso de grupo de um FIR simétrico de 201 taps, em amostras e em ms a
   48 kHz?
3. Por que um passa-alta FIR de fase linear com N par é impossível?
4. Você precisa distinguir dois tons próximos, um forte e um fraco. Qual janela, e
   por quê?
5. Você precisa medir a amplitude de um tom com exatidão. Qual janela?
6. Quantos taps para 60 dB de rejeição e 200 Hz de transição a 8 kHz?
7. Mesma ordem: quanto o `remez` ganha sobre o `firwin`, medido?
8. Como cortar pela metade o custo de um FIR simétrico, sem perder nada?
9. Por que a média móvel é O(1) e por que, mesmo assim, ela é um filtro ruim?
