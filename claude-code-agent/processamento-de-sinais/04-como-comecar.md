# 04 · Como começar — do ambiente pronto ao primeiro resultado

`Nível: iniciante` · `Todas as saídas abaixo foram executadas em 14/08/2026`
`Base: Python 3.10.12 · NumPy 2.2.6 · SciPy 1.15.3`

Pressupõe o ambiente do [`03-instalacao.md`](03-instalacao.md) pronto — ou o Colab
aberto, que dá na mesma. **Não instale nada aqui.**

Objetivo desta página: em vinte minutos, você terá criado um sinal, visto o
espectro dele, filtrado uma frequência e provocado aliasing de propósito. Depois
disso a teoria dos capítulos seguintes tem onde se agarrar.

---

## Passo 1 · O "hello world" do DSP: ver uma frequência

Crie `primeiro.py`:

```python
import numpy as np

taxa = 8000                      # amostras por segundo (Hz)
dur  = 1.0                       # segundos
t = np.arange(int(taxa*dur))/taxa   # vetor de instantes: 0, 1/8000, 2/8000, ...

# um Lá de 440 Hz somado a um tom de 1200 Hz com metade da amplitude
x = np.sin(2*np.pi*440*t) + 0.5*np.sin(2*np.pi*1200*t)

X = np.abs(np.fft.rfft(x))            # espectro de magnitude
f = np.fft.rfftfreq(len(x), 1/taxa)   # a que frequência corresponde cada bin

k = np.argsort(X)[-2:]                # índices dos dois maiores valores
print("amostras:", len(x), " resolução:", taxa/len(x), "Hz/bin")
print("dois maiores picos:", sorted(f[k]))
```

```bash
python primeiro.py
```

**Saída real:**

```
amostras: 8000  resolução: 1.0 Hz/bin
dois maiores picos: [np.float64(440.0), np.float64(1200.0)]
```

Pronto: você acabou de fazer análise espectral. Sete linhas úteis.

**O que cada linha faz, e por quê:**

| Linha | O que é |
|---|---|
| `t = np.arange(N)/taxa` | os instantes de amostragem. `t` está em **segundos** |
| `2*np.pi*440*t` | a fase, em radianos. 440 ciclos por segundo × 2π radianos por ciclo |
| `np.fft.rfft` | FFT para sinal **real**. Devolve só metade do espectro (a outra metade é o espelho conjugado — ver [16](16-dft-e-fft.md)) |
| `np.abs(...)` | o resultado é complexo: módulo = amplitude, ângulo = fase |
| `np.fft.rfftfreq` | traduz índice de bin para Hz. **Use sempre** — calcular na mão é a fonte nº 1 de gráficos com eixo errado |

**Resolução de 1,0 Hz/bin** porque `taxa/N = 8000/8000`. Guarde esta fórmula: ela
manda em tudo que você vai fazer.

---

## Passo 2 · Ver o espectro sem depender de gráfico

Antes de usar Matplotlib, vale ver o espectro em texto — funciona por SSH, dentro
de contêiner, e obriga você a pensar no eixo.

```python
import numpy as np
taxa = 8000
t = np.arange(taxa)/taxa
x = np.sin(2*np.pi*440*t) + 0.5*np.sin(2*np.pi*1200*t)
X = np.abs(np.fft.rfft(x)); f = np.fft.rfftfreq(len(x), 1/taxa)

passo = 40                                  # agrupa 40 bins por linha
for i in range(0, 2000, passo):
    bloco = X[i:i+passo]
    print(f"{i:5d}-{i+passo-1:4d} Hz | {'#'*int(50*bloco.max()/X.max())}")
```

**Saída real (trecho):**

```
  360- 399 Hz |
  400- 439 Hz |
  440- 479 Hz | ##################################################
  480- 519 Hz |
  ...
 1160-1199 Hz |
 1200-1239 Hz | #########################
 1240-1279 Hz |
```

Duas raias, e a segunda com metade do tamanho da primeira — exatamente o `0.5` que
escrevemos. **A leitura do espectro bate com o que você construiu.** Sempre que um
resultado bater com uma previsão sua, anote: é assim que a intuição se forma.

Com gráfico é mais bonito e igualmente simples:

```python
import matplotlib
matplotlib.use("Agg")           # sem isso, falha em servidor/WSL sem X
import matplotlib.pyplot as plt

plt.plot(f, 20*np.log10(np.maximum(X, 1e-12)))   # o maximum evita log10(0)
plt.xlabel("frequência (Hz)"); plt.ylabel("dB")
plt.xlim(0, 2000); plt.grid(alpha=.3)
plt.savefig("espectro.png", dpi=110)
print("gravado espectro.png")
```

---

## Passo 3 · Filtrar: tirar os 1200 Hz e manter os 440

```python
import numpy as np
from scipy import signal

taxa = 8000
t = np.arange(taxa)/taxa
x = np.sin(2*np.pi*440*t) + 0.5*np.sin(2*np.pi*1200*t)

# passa-baixa FIR: 101 coeficientes, corte em 800 Hz
h = signal.firwin(numtaps=101, cutoff=800, fs=taxa)
y = signal.lfilter(h, 1.0, x)

def pico(sig):
    X = np.abs(np.fft.rfft(sig)); f = np.fft.rfftfreq(len(sig), 1/taxa)
    top = np.argsort(X)[-2:]
    return [(round(float(f[k]),1), round(float(X[k]/len(sig)*2),4)) for k in sorted(top)]

print("antes :", pico(x))
print("depois:", pico(y))
print("atraso de grupo:", (len(h)-1)//2, "amostras =", (len(h)-1)/2/taxa*1000, "ms")
```

**Saída real:**

```
antes : [(440.0, 1.0), (1200.0, 0.5)]
depois: [(436.0, 0.0064), (440.0, 0.9951)]
atraso de grupo: 50 amostras = 6.25 ms
```

Leia com atenção — há três lições aqui:

1. **O tom de 1200 Hz sumiu.** Ele nem aparece mais entre os dois maiores picos: o
   segundo lugar agora é o vizinho de 436 Hz, com 0,0064 de amplitude.
2. **O de 440 Hz sobreviveu quase intacto:** 0,9951 em vez de 1,0. Os 0,5 % que
   faltam são a atenuação do filtro na banda passante — o preço de existir.
3. **O filtro atrasou o sinal em 6,25 ms.** Todo filtro FIR de fase linear atrasa
   (N−1)/2 amostras. Isso não é bug: é o custo da fase linear, e é o que você tem
   de somar ao orçamento de latência de um sistema em tempo real.

> `fs=taxa` no `firwin` deixa você escrever o corte em Hz. Sem isso, a SciPy espera
> a frequência **normalizada por Nyquist** (800/4000 = 0,2), e trocar as duas
> convenções é o erro clássico que põe seu filtro no dobro da frequência.

---

## Passo 4 · Provocar aliasing de propósito

Esta é a experiência que mais ensina no dia um.

```python
import numpy as np
taxa = 1000
for f_real in [100, 300, 700, 900, 1100]:
    t = np.arange(taxa)/taxa
    x = np.sin(2*np.pi*f_real*t)
    X = np.abs(np.fft.rfft(x))
    f_medida = np.argmax(X) * taxa/len(x)
    print(f"seno de {f_real:5d} Hz amostrado a {taxa} Hz -> aparece em {f_medida:6.1f} Hz")
```

**Saída real:**

```
seno de   100 Hz amostrado a 1000 Hz -> aparece em  100.0 Hz
seno de   300 Hz amostrado a 1000 Hz -> aparece em  300.0 Hz
seno de   700 Hz amostrado a 1000 Hz -> aparece em  300.0 Hz
seno de   900 Hz amostrado a 1000 Hz -> aparece em  100.0 Hz
seno de  1100 Hz amostrado a 1000 Hz -> aparece em  100.0 Hz
```

Pare e olhe. **700 Hz virou 300 Hz. 900 virou 100. 1100 virou 100.**

Nyquist aqui é 500 Hz. Tudo acima disso se disfarça:
- 700 = 1000 − 300 → aparece em 300 (reflexão em torno de Nyquist)
- 900 = 1000 − 100 → aparece em 100
- 1100 = 1000 + 100 → aparece em 100 (repetição a cada `taxa`)

A fórmula geral está em [`15-amostragem-e-quantizacao.md`](15-amostragem-e-quantizacao.md),
mas o essencial você acabou de ver: **nenhum erro foi emitido**. O programa
respondeu com convicção uma frequência que não existe. Aliasing não avisa. Por isso
todo conversor A/D decente tem um filtro analógico antes dele.

---

## O ciclo de trabalho do dia a dia

```
    ┌──────────────────────────────────────────────────┐
    │  1. gere ou carregue um sinal COM RESPOSTA        │
    │     CONHECIDA (senoide de f conhecida)            │
    └───────────────────────┬──────────────────────────┘
                            ▼
    ┌──────────────────────────────────────────────────┐
    │  2. aplique o processamento                       │
    └───────────────────────┬──────────────────────────┘
                            ▼
    ┌──────────────────────────────────────────────────┐
    │  3. PLOTE. Sempre. Onda e espectro.               │
    └───────────────────────┬──────────────────────────┘
                            ▼
    ┌──────────────────────────────────────────────────┐
    │  4. compare com o que você PREVIU antes de rodar  │
    └───────────────────────┬──────────────────────────┘
                            ▼
              bateu? ──não──► entenda a diferença
                 │              (é aí que se aprende)
                sim
                 ▼
    ┌──────────────────────────────────────────────────┐
    │  5. SÓ ENTÃO aplique ao sinal real                │
    └──────────────────────────────────────────────────┘
```

Três hábitos que separam quem avança de quem sofre:

1. **Sinal sintético antes de sinal real.** Se seu código não acha 440 Hz num seno
   de 440 Hz, o problema é o código — não o microfone, não o paciente, não a antena.
2. **Plote tudo.** DSP é a área em que "parece certo no número e está errado no
   gráfico" acontece toda semana. Um espectrograma custa três linhas.
3. **Escreva a taxa de amostragem em toda variável e todo nome de arquivo.**
   `sinal_44k1.wav`. Metade dos bugs desta área é taxa errada silenciosamente
   propagada de uma função para outra.

---

## Os cinco primeiros erros de uso (não de instalação)

### 1. Confundir frequência normalizada com frequência em Hz

```python
signal.firwin(101, 800)              # ERRADO: 800 é interpretado como 800×Nyquist
signal.firwin(101, 800, fs=8000)     # certo: 800 Hz
signal.firwin(101, 0.2)              # também certo: 0,2 × Nyquist = 800 Hz a 8 kHz
```
Sintoma: filtro que não filtra nada, ou erro `Invalid cutoff frequency`.
**Regra:** sempre passe `fs=`. É explícito e não deixa dúvida.

### 2. Esquecer que a saída da FFT é complexa

```python
X = np.fft.rfft(x)
plt.plot(X)          # ERRADO: joga fora a fase com um aviso e plota só a parte real
plt.plot(np.abs(X))  # certo
```
Sintoma: `ComplexWarning: Casting complex values to real discards the imaginary part`.

### 3. Achar que zero-padding melhora a resolução

```python
X = np.fft.rfft(x, n=1_000_000)   # espectro liso e bonito
```
Ele **interpola** o espectro, deixa o gráfico suave e melhora a localização de um
pico isolado. Ele **não** separa duas raias próximas: isso depende só de `taxa/N`
com N = número de amostras **reais**. Detalhe em [`16`](16-dft-e-fft.md).

### 4. Não janelar e culpar o algoritmo

```python
X = np.fft.rfft(x)                 # janela retangular implícita
X = np.fft.rfft(x*np.hanning(len(x)))   # quase sempre o que você quer
```
Sintoma: uma senoide pura vira uma montanha larga com "saias" que somem devagar.
Isso é **vazamento espectral** ([`20`](20-analise-espectral-e-janelas.md)), causado
pelo corte abrupto nas bordas do bloco, e não pela FFT.

### 5. Usar `filtfilt` em tempo real

`signal.filtfilt` filtra para frente e para trás: fase zero, resultado lindo — e
**precisa do sinal inteiro, inclusive do futuro**. Num sistema ao vivo, isso é
fisicamente impossível. Use `lfilter`/`sosfilt` com estado (`zi`) e aceite o atraso.
Sintoma: "funcionou no notebook e no equipamento ficou estranho".

**Bônus, o erro nº 6:** `lfilter` com IIR de ordem alta em forma direta explode
numericamente. Use `sos`: `signal.butter(8, 0.2, output="sos")` +
`signal.sosfilt`. Vale desde a ordem ~6.

---

## Verificação: você está pronto para seguir?

Consegue fazer estes quatro sem consultar?

```bash
# 1. gerar 2 s de um Lá 440 a 44,1 kHz e salvar em WAV
# 2. carregar, calcular o espectro e imprimir a frequência do pico
# 3. filtrar tudo acima de 1 kHz
# 4. dizer, antes de rodar, quantas amostras de atraso o filtro vai introduzir
```

Se sim, siga para [`06-exemplos.md`](06-exemplos.md).
Se não, refaça os passos 1 a 4 desta página trocando os números — outra taxa,
outras frequências. Repetição com variação é o que fixa.

---

## Para onde ir agora

| Se você quer... | Vá para |
|---|---|
| Mais receitas prontas, do trivial ao real | [`06-exemplos.md`](06-exemplos.md) |
| Um programa inteiro que funciona | [`07-projeto-modelo/`](07-projeto-modelo/README.md) |
| Entender **por que** aquilo tudo funcionou | [`10-fundamentos.md`](10-fundamentos.md) |
| A matemática que falta | [`12-matematica-do-zero.md`](12-matematica-do-zero.md) |
| Referência de comandos | [`05-manual-de-uso.md`](05-manual-de-uso.md) |
| Não repetir erro de principiante | [`75-armadilhas.md`](75-armadilhas.md) |

---

## Autoteste

1. Qual é a resolução em Hz de uma FFT de 4096 amostras a 48 kHz?
2. Por que `np.fft.rfft` devolve `N/2+1` valores e não `N`?
3. Um seno de 3 kHz amostrado a 5 kHz aparece em que frequência? Mostre a conta.
4. Quantas amostras de atraso um FIR de 201 taps de fase linear introduz?
5. Por que `plt.plot(np.fft.rfft(x))` está errado?
6. Zero-padding melhora o quê, exatamente, e não melhora o quê?
7. Cite o motivo pelo qual `filtfilt` é proibido num processador ao vivo.
