# 16 · DFT e FFT — a única transformada que roda no computador

`Nível: intermediário → avançado` · `Atualizado em: 14/08/2026`

A DFT é a versão finita e discreta de Fourier. A FFT é um **algoritmo** para
calculá-la depressa — não uma transformada diferente. Confundir os dois é o
equívoco de vocabulário mais comum do campo.

---

## 1 · Definição

```
X[k] = Σ_{n=0}^{N−1} x[n]·e^{−j2πkn/N},      k = 0, 1, ..., N−1
x[n] = (1/N)·Σ_{k=0}^{N−1} X[k]·e^{+j2πkn/N}
```

N amostras entram, N números complexos saem. Nada de infinito, nada de contínuo:
**computável**.

**O que cada bin k significa:** a componente na frequência

```
f_k = k·fs/N        (Hz), para k = 0 .. N/2
```

E para k > N/2, a interpretação é de **frequência negativa**: f_k = (k−N)·fs/N.
`np.fft.fftfreq` já faz essa conta; `np.fft.rfftfreq` devolve só a metade positiva.

**Interpretação em uma frase:** X[k] é o produto interno de x com a k-ésima
exponencial da base — ou seja, "o quanto x se parece com aquela frequência",
em módulo (amplitude) e ângulo (fase). É a §6 de
[`12-matematica-do-zero.md`](12-matematica-do-zero.md), literalmente.

### As duas hipóteses escondidas

A DFT não sabe que seu sinal tem começo e fim. Ela assume:

1. **O bloco se repete periodicamente para sempre.** Daí o vazamento espectral: se
   o fim não emenda com o começo, a DFT "vê" uma descontinuidade que você não pôs
   ali.
2. **A convolução via DFT é circular**, não linear. A cauda dá a volta.

Praticamente todo artefato estranho da FFT sai de uma dessas duas.

---

## 2 · 🔑 Resolução: o que zero-padding faz e o que não faz

```
resolução = fs/N          (com N = número de amostras REAIS, não o tamanho da FFT)
```

Este é o teste decisivo. Dois tons em 100 e 103 Hz, separados por 3 Hz:

```python
import numpy as np
from scipy import signal

fs = 1000; f1, f2 = 100.0, 103.0
for N in [256, 1024]:
    t = np.arange(N)/fs
    x = np.sin(2*np.pi*f1*t) + np.sin(2*np.pi*f2*t)
    for nfft in [N, 8192]:
        X = np.abs(np.fft.rfft(x*np.hanning(N), n=nfft))
        f = np.fft.rfftfreq(nfft, 1/fs)
        m = (f > 90) & (f < 115)
        pk, _ = signal.find_peaks(X[m], prominence=X[m].max()*0.05)
        print(f"  N={N:5d} nfft={nfft:5d} res={fs/N:5.2f} Hz/bin"
              f" -> {len(pk)} pico(s) em {np.round(f[m][pk], 2)}")
```

Saída real:

```
  N=  256 nfft=  256 res= 3.91 Hz/bin -> 1 pico(s) em [101.56]
  N=  256 nfft= 8192 res= 3.91 Hz/bin -> 1 pico(s) em [103.76]
  N= 1024 nfft= 1024 res= 0.98 Hz/bin -> 2 pico(s) em [ 99.61 102.54]
  N= 1024 nfft= 8192 res= 0.98 Hz/bin -> 2 pico(s) em [ 99.98 103.03]
```

**Leia as quatro linhas em pares.**

- Com **N = 256** (resolução 3,91 Hz > separação de 3 Hz): **um** pico. Fazer a FFT
  com 8192 pontos — 32× mais zero-padding — continua dando **um** pico. Zero-padding
  não criou informação; só desenhou a mesma montanha com mais pontos.
- Com **N = 1024** (resolução 0,98 Hz < 3 Hz): **dois** picos. E aí sim o
  zero-padding ajuda: as estimativas melhoram de 99,61/102,54 para 99,98/103,03,
  muito mais perto dos verdadeiros 100 e 103.

**A regra, então:**

| Zero-padding **melhora** | Zero-padding **não melhora** |
|---|---|
| a precisão da estimativa de um pico isolado | a capacidade de separar dois picos próximos |
| a aparência do gráfico (interpola) | a informação contida no sinal |
| a localização do máximo na grade | a resolução, que é fs/N com N real |

**Para separar duas frequências separadas por Δf, você precisa gravar por pelo
menos 1/Δf segundos.** Sem exceção, sem truque. Para 1 Hz de resolução, 1 segundo.
Isto é o princípio da incerteza ([`14 §5`](14-fourier.md)) na forma mais prática
que existe.

---

## 3 · Interpolação de pico: precisão de graça

Se você só quer *a frequência de um pico isolado* (não separar dois), há um truque
barato: ajustar uma parábola nos três bins em torno do máximo, **em dB**.

```
d = 0,5·(a − c)/(a − 2b + c),    onde a,b,c = magnitudes em dB dos bins k−1, k, k+1
f = (k + d)·fs/N
```

Medido sobre 21 frequências entre 1000 e 1010 Hz, com N=1024 a 8 kHz:

```
  resolução do bin: 7.812 Hz
  erro médio SEM interpolação: 1.735 Hz  (pior 3.812)
  erro médio COM interpolação: 0.079 Hz  (pior 0.125)
```

(Saída real.) **Erro 22× menor**, e o pior caso caiu de meio bin para 1/62 de bin.
Três linhas de código.

**Por que em dB e não em linear?** Porque o topo do lóbulo principal de uma janela
Hann, em escala logarítmica, é quase exatamente uma parábola. Em escala linear o
ajuste é pior. Isso não é folclore: é consequência de a Hann ter transformada com
formato aproximadamente gaussiano perto do pico, e log(gaussiana) = parábola.

O afinador do [`07-projeto-modelo/`](07-projeto-modelo/README.md) usa exatamente
isso para chegar a 0,1 cent de erro com bin de 1 Hz.

---

## 4 · A FFT: por que N·log N

A DFT direta custa N² multiplicações complexas. A ideia de Cooley-Tukey
(**divide e conquista**):

Separe as amostras pares e ímpares:

```
X[k] = Σ_{par} x[2m]·W^{2mk} + W^k·Σ_{ímpar} x[2m+1]·W^{2mk}
     = E[k] + W^k·O[k]                    onde W = e^{−j2π/N}
```

E, pela periodicidade,

```
X[k + N/2] = E[k] − W^k·O[k]
```

**Duas DFTs de N/2 resolvem uma de N**, com N/2 multiplicações extras. Repita
log₂N vezes até chegar a DFTs de 1 ponto (que são a identidade). Custo total:
(N/2)·log₂N multiplicações complexas.

A operação `E ± W^k·O` é a **borboleta** (*butterfly*) — o diagrama que dá nome ao
grafo de fluxo da FFT.

```
  E[k] ──●─────────────► E[k] + W^k·O[k]
          ╲    ╱
           ╲  ╱
            ╳
           ╱  ╲
          ╱    ╲
  O[k] ──●──×W^k──────► E[k] − W^k·O[k]
```

### O ganho, medido

```python
import numpy as np, time
for N in [512, 2048, 8192]:
    x = np.random.default_rng(0).standard_normal(N) + 0j
    W = np.exp(-2j*np.pi*np.outer(np.arange(N), np.arange(N))/N)
    t0 = time.perf_counter(); [W @ x for _ in range(10)]; td = (time.perf_counter()-t0)/10
    t0 = time.perf_counter(); [np.fft.fft(x) for _ in range(200)]; tf = (time.perf_counter()-t0)/200
    print(f"  N={N:6d}: matriz {td*1000:8.3f} ms | FFT {tf*1000:7.4f} ms"
          f" | ganho medido {td/tf:6.0f}x | N/log2(N) = {N/np.log2(N):6.0f}")
```

Saída real:

```
  N=   512: matriz    0.032 ms | FFT  0.0246 ms | ganho medido      1x | N/log2(N) =     57
  N=  2048: matriz    2.582 ms | FFT  0.0575 ms | ganho medido     45x | N/log2(N) =    186
  N=  8192: matriz   39.505 ms | FFT  0.2346 ms | ganho medido    168x | N/log2(N) =    630
```

**Honestidade sobre esta medida:** o ganho medido é bem menor que N/log₂N em todos
os casos, e em N=512 é ~1×. Motivo: o produto matriz-vetor do NumPy roda em BLAS
otimizada (vetorizada, com bom uso de cache), enquanto a FFT tem overhead de
chamada. A **contagem de operações** favorece a FFT por N/log₂N; o **tempo real**
depende de constantes de implementação. A tendência, porém, está clara e é o que
importa: de N=512 para N=8192 (16×), a matriz ficou 1200× mais lenta (≈16², como
previsto) e a FFT ficou 10× (≈16·log-ratio). **A assintótica manda; para N grande
não há competição.** Para N = 1 milhão, a DFT direta é inviável e a FFT leva
milissegundos.

### Variantes que importam

| Algoritmo | Quando |
|---|---|
| radix-2 / radix-4 | N potência de 2. O caso clássico e o mais rápido |
| split-radix | menor contagem de operações para potências de 2 |
| **Bluestein / chirp-Z** | N primo ou arbitrário — transforma em convolução |
| Rader | N primo, via teoria dos números |
| **`rfft`** | sinal real: metade do trabalho e da memória |
| Goertzel | quando você quer **poucos** bins ([`06 §3`](06-exemplos.md)) |

O NumPy e a SciPy escolhem sozinhos. Mas o N importa:

```python
from scipy import fft
fft.next_fast_len(10007)     # 10080  ← 5-smooth, muito mais rápido que o primo
```

**Um N primo pode ser dezenas de vezes mais lento** que o próximo N "bonito". Se
você processa em lote, `next_fast_len` é dinheiro no bolso.

---

## 5 · Convolução circular — o artefato nº 1

```python
x = np.array([1., 2., 3., 4.]); h = np.array([1., 1., 1.])
print("linear   :", np.convolve(x, h))
print("circular4:", np.round(np.fft.irfft(np.fft.rfft(x,4)*np.fft.rfft(h,4), 4), 6))
print("circular6:", np.round(np.fft.irfft(np.fft.rfft(x,6)*np.fft.rfft(h,6), 6), 6))
```

Saída real:

```
linear   : [1. 3. 6. 9. 7. 4.]
circular4: [8. 7. 6. 9.]
circular6: [1. 3. 6. 9. 7. 4.]
```

Com N = 4, a cauda `[7, 4]` **deu a volta** e somou no começo: 1+7 = 8, 3+4 = 7.
Resultado completamente errado, **sem nenhum aviso**.

**Regra:** para convolução linear via FFT, use `N ≥ len(x) + len(h) − 1`.
Com N = 6, o resultado é idêntico ao `np.convolve`.

Para sinais longos (um arquivo de áudio inteiro), usa-se **overlap-add** ou
**overlap-save**: processar em blocos com zero-padding suficiente e emendar.
`signal.oaconvolve` e `signal.fftconvolve` já fazem isso corretamente. **Use-as**
em vez de implementar à mão.

---

## 6 · Escalonamento e normalização — de onde vem o "meu pico deu 512"

O NumPy não normaliza a FFT direta (`norm=None` divide só na inversa). Consequência:
uma senoide de amplitude 1,0 com N = 1024 dá pico de **512**, não 1.

Para recuperar amplitude física:

| Objetivo | Conta |
|---|---|
| amplitude de senoide (sem janela) | `2*np.abs(X)/N` |
| amplitude de senoide (com janela w) | `2*np.abs(X)/np.sum(w)` ← **o correto** |
| densidade espectral de potência | use `signal.welch`, que já normaliza |
| verificação por Parseval | `np.sum(x**2) == np.sum(np.abs(X)**2)/N` |

**O fator 2** existe porque metade da energia está na frequência negativa, que a
`rfft` descarta. Não aplique o 2 ao bin de DC nem ao de Nyquist — eles não têm par.

Erro clássico: dividir por N em vez de por `sum(w)` ao usar janela. A Hann tem
soma ≈ N/2, então o resultado sai **6 dB baixo** e a pessoa passa uma tarde
procurando o ganho perdido no filtro.

---

## 7 · Custo real e escolhas de implementação

| Truque | Ganho |
|---|---|
| `rfft` em vez de `fft` para sinal real | ~2× em tempo e memória |
| `scipy.fft` em vez de `numpy.fft` | pocketfft, aceita `workers=-1` (multithread) |
| `next_fast_len` | até dezenas de vezes se N era primo |
| `float32` nos dados | ~2× em memória e banda; precisão sobra para áudio |
| planejar/reusar buffers | evita alocação em laço quente |
| `overwrite_x=True` (SciPy) | economiza uma cópia |

---

## Os cinco porquês: por que N·log N e não menos?

1. **Por que a FFT é N·log N?** Porque divide o problema pela metade log N vezes,
   e cada nível custa O(N).
2. **Por que dá para dividir pela metade?** Porque W^{2mk} = e^{−j2πmk/(N/2)}: a
   raiz da unidade de ordem N ao quadrado é a raiz de ordem N/2. É **simetria
   algébrica** das raízes da unidade, não um truque de programação.
3. **Por que essa simetria existe?** Porque as raízes da unidade formam um **grupo
   cíclico** sob multiplicação, e o subgrupo de índice 2 são as raízes de ordem
   N/2. A FFT é, no fundo, uma fatoração de grupo.
4. **Dá para fazer melhor que N·log N?** Não se conhece algoritmo assintoticamente
   melhor para a DFT geral, e há resultados de limite inferior sob modelos
   restritos de computação (circuitos lineares com coeficientes limitados). No
   caso **esparso** — poucos bins não nulos — existe a **Sparse FFT**, com custo
   sublinear O(k·log N), que é um resultado de 2012 do MIT.
5. **Por que ninguém provou um limite inferior geral?** Porque provar limites
   inferiores em complexidade aritmética é notoriamente difícil — é primo de
   P vs NP. **Parada legítima: problema em aberto da matemática.** Se você resolver,
   avise.

---

## Autoteste

1. Qual a diferença entre DFT e FFT?
2. Um bloco de 2048 amostras a 48 kHz: qual a resolução? E se eu fizer FFT de 65536?
3. Preciso separar 440,0 de 441,0 Hz. Quanto tempo de gravação, no mínimo?
4. O que a interpolação parabólica melhora, quantitativamente, e por que em dB?
5. Escreva a borboleta da FFT e diga de onde vem o fator 2 de economia.
6. Por que uma FFT com N = 10007 pode ser muito mais lenta que com N = 10080?
7. Meu resultado de convolução via FFT tem lixo no começo. Diagnóstico e correção?
8. Uma senoide de amplitude 1 janelada com Hann, N=1024. Que pico eu espero na
   `rfft` sem normalizar, e como converto para amplitude física?
9. Quais são as duas hipóteses escondidas da DFT?
