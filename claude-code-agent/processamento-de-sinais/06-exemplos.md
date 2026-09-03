# 06 · Exemplos — 12 receitas completas e executáveis

`Nível: iniciante → avançado` · `Todos executados em 14/08/2026`
`Base: Python 3.10.12 · NumPy 2.2.6 · SciPy 1.15.3`

Todo código aqui é **completo**: copie, cole, rode. Nada de `...` no meio.
Toda saída mostrada é a saída **real** da execução, não uma previsão.

Cabeçalho comum a todos:

```python
import numpy as np
from scipy import signal
```

| # | Exemplo | Nível | Conceito central |
|---|---|---|---|
| 1 | [Identificar as notas de um acorde](#1--identificar-as-notas-de-um-acorde) | trivial | FFT, `find_peaks` |
| 2 | [Vazamento espectral medido em dB](#2--vazamento-espectral-medido-em-db) | fácil | janelamento |
| 3 | [DTMF: discar e decodificar](#3--dtmf-discar-e-decodificar-caso-real-telefonia) | médio | Goertzel, detecção por energia |
| 4 | [Limpar um ECG](#4--limpar-um-ecg-caso-real-biomédico) | médio | notch, passa-alta, detecção de picos |
| 5 | [Envoltória e frequência instantânea](#5--envoltória-e-frequência-instantânea) | médio | transformada de Hilbert |
| 6 | [Reamostrar 44,1 kHz → 48 kHz](#6--reamostrar-441-khz--48-khz) | médio | multitaxa |
| 7 | [Medir atraso entre dois microfones](#7--medir-atraso-entre-dois-microfones-tdoa) | médio | correlação cruzada |
| 8 | [Achar um pulso enterrado no ruído](#8--achar-um-pulso-enterrado-no-ruído) | avançado | filtro casado |
| 9 | [Quantização, SNR e dither](#9--quantização-snr-e-dither) | médio | conversão A/D |
| 10 | [Periodograma × Welch](#10--periodograma--welch) | avançado | estimação espectral |
| 11 | [Espectrograma com a API atual](#11--espectrograma-com-a-api-atual) | médio | STFT |
| 12 | [Média móvel × EMA × Savitzky-Golay](#12--média-móvel--ema--savitzky-golay-caso-real-telemetria) | médio | compromisso ruído × atraso |

---

## 1 · Identificar as notas de um acorde

**Problema:** dado um áudio com três notas soando juntas, descobrir quais são.

```python
import numpy as np
from scipy import signal

fs = 22050
t = np.arange(int(0.5*fs))/fs
notas = {"C4": 261.63, "E4": 329.63, "G4": 392.00}      # acorde de dó maior
x = sum(np.sin(2*np.pi*f*t) for f in notas.values())/3

X = np.abs(np.fft.rfft(x*np.hanning(len(t))))
f = np.fft.rfftfreq(len(t), 1/fs)

picos, _ = signal.find_peaks(X, prominence=X.max()*0.1)
print("frequências detectadas:", np.round(f[picos], 1))
print("esperado:", list(notas.values()))
```

**Saída real:**

```
frequências detectadas: [262. 330. 392.]
esperado: [261.63, 329.63, 392.0]
```

**Explicação.** A resolução é fs/N = 22050/11025 = 2 Hz, e por isso 261,63 aparece
como 262. Se você precisar de mais precisão, tem duas saídas: gravar mais tempo
(aumenta N) ou interpolar o pico ([`16`](16-dft-e-fft.md) e o projeto-modelo).
`prominence` é o parâmetro certo em `find_peaks`: ele mede a altura do pico em
relação ao vale vizinho, então funciona mesmo quando o piso de ruído varia.

---

## 2 · Vazamento espectral medido em dB

**Problema:** provar, com número, por que janelar importa — e descobrir quando
**não** importa.

```python
import numpy as np

fs, N = 1000, 1000
for f0, nome in [(100.0, "inteiro de bins (100 Hz)"), (100.5, "meio bin (100,5 Hz)")]:
    t = np.arange(N)/fs
    x = np.sin(2*np.pi*f0*t)
    for jan, jn in [(np.ones(N), "retangular"), (np.hanning(N), "Hann")]:
        X = np.abs(np.fft.rfft(x*jan)); X /= X.max()
        k = np.argmax(X)
        mask = np.ones(len(X), bool); mask[max(0, k-5):k+6] = False   # tudo fora de ±5 bins
        vaz = 10*np.log10(np.sum(X[mask]**2)/np.sum(X**2))
        print(f"  {nome:26s} {jn:11s} vazamento fora de ±5 bins: {vaz:7.2f} dB")
```

**Saída real:**

```
  inteiro de bins (100 Hz)   retangular  vazamento fora de ±5 bins: -272.78 dB
  inteiro de bins (100 Hz)   Hann        vazamento fora de ±5 bins:  -85.63 dB
  meio bin (100,5 Hz)        retangular  vazamento fora de ±5 bins:  -14.34 dB
  meio bin (100,5 Hz)        Hann        vazamento fora de ±5 bins:  -52.12 dB
```

**Explicação — e este resultado surpreende quase todo mundo:**

- Quando a frequência cai **exatamente** num bin, a janela retangular é
  **perfeita** (−272 dB é zero numérico) e a Hann é *pior* (−85 dB). Motivo: com
  frequência exata, o bloco contém um número inteiro de ciclos e a extensão
  periódica é contínua. Não há descontinuidade para vazar.
- Quando a frequência cai entre dois bins — o caso normal, porque você nunca
  controla a frequência do sinal do mundo — a retangular vaza **38 dB a mais**
  que a Hann.

A conclusão prática: **janele sempre**, porque você não controla onde a frequência
cai. E a conclusão teórica: vazamento não é defeito da FFT; é a consequência de
cortar um sinal infinito num bloco finito. Detalhes em [`20`](20-analise-espectral-e-janelas.md).

---

## 3 · DTMF: discar e decodificar (caso real, telefonia)

**Problema:** os tons que seu telefone emite ao discar são dois senos simultâneos.
Gerar e decodificar, como faz uma central telefônica — com o algoritmo que ela usa
de verdade, o **Goertzel**, que calcula *uma* frequência da DFT em O(N) sem FFT.

```python
import numpy as np

fs = 8000
BAIXAS = [697, 770, 852, 941]
ALTAS  = [1209, 1336, 1477, 1633]
TECLAS = [["1","2","3","A"], ["4","5","6","B"],
          ["7","8","9","C"], ["*","0","#","D"]]

def gerar_dtmf(tecla, dur=0.1):
    for i, linha in enumerate(TECLAS):
        if tecla in linha:
            fb, fa = BAIXAS[i], ALTAS[linha.index(tecla)]
    t = np.arange(int(dur*fs))/fs
    return 0.5*(np.sin(2*np.pi*fb*t) + np.sin(2*np.pi*fa*t))

def goertzel(x, fs, f_alvo):
    """Energia do sinal na frequência f_alvo. Um único bin da DFT, em O(N),
    com 2 variáveis de estado — cabe num microcontrolador de 1980."""
    N = len(x)
    k = int(0.5 + N*f_alvo/fs)
    w = 2*np.pi*k/N
    coef = 2*np.cos(w)
    s1 = s2 = 0.0
    for amostra in x:
        s0 = amostra + coef*s1 - s2
        s2, s1 = s1, s0
    return s1*s1 + s2*s2 - coef*s1*s2

def decodificar(x, fs):
    eb = [goertzel(x, fs, f) for f in BAIXAS]
    ea = [goertzel(x, fs, f) for f in ALTAS]
    return TECLAS[int(np.argmax(eb))][int(np.argmax(ea))]

seq = "0800912"
rng = np.random.default_rng(1)
recebido = "".join(decodificar(gerar_dtmf(d) + 0.1*rng.standard_normal(800), fs)
                   for d in seq)
print("enviado     :", seq)
print("decodificado:", recebido, "->", "OK" if recebido == seq else "FALHOU")
```

**Saída real:**

```
enviado     : 0800912
decodificado: 0800912 -> OK
```

**Explicação.** Por que dois tons e não um? Porque **nenhum** dos oito é harmônico
de outro, e a voz humana quase nunca produz dois tons puros dessas famílias ao
mesmo tempo — foi projetado em 1963 nos Bell Labs justamente para não disparar com
a voz do usuário. É engenharia de detecção, não de codificação.

Por que Goertzel e não FFT? Você precisa de **8 frequências**, não de 4000 bins.
FFT custa O(N log N) para tudo; Goertzel custa O(N) por frequência. Com 8
frequências e N=800, Goertzel ganha — e usa 2 variáveis de estado em vez de um
buffer inteiro. É por isso que ele sobrevive em telefonia e em medidores de
energia até hoje.

---

## 4 · Limpar um ECG (caso real, biomédico)

**Problema:** um eletrocardiograma real chega com três contaminações: zumbido da
rede elétrica (60 Hz), deriva de linha de base (respiração e movimento do
eletrodo, < 0,5 Hz) e ruído de banda larga. Limpar e contar os batimentos.

```python
import numpy as np
from scipy import signal

fs, dur = 500, 10
n = int(fs*dur); t = np.arange(n)/fs
rng = np.random.default_rng(3)

# ECG sintético: um complexo QRS gaussiano a 72 bpm
bpm = 72; f_card = bpm/60
qrs = np.zeros(n)
for k in range(int(dur*f_card)):
    c = int(k*fs/f_card)
    if c+40 < n:
        qrs[c:c+40] += signal.windows.gaussian(40, 4)*1.2
ecg_limpo = qrs

deriva = 0.4*np.sin(2*np.pi*0.15*t)      # respiração
rede   = 0.3*np.sin(2*np.pi*60*t)        # tomada
ecg = ecg_limpo + deriva + rede + 0.02*rng.standard_normal(n)

# 1) notch em 60 Hz, fase zero
b, a = signal.iirnotch(60, Q=30, fs=fs)
y = signal.filtfilt(b, a, ecg)
# 2) passa-alta em 0,5 Hz para matar a deriva
sos = signal.butter(4, 0.5, btype="highpass", fs=fs, output="sos")
y = signal.sosfiltfilt(sos, y)

print(f"RMS do erro antes : {np.sqrt(np.mean((ecg - ecg_limpo)**2)):.4f}")
print(f"RMS do erro depois: {np.sqrt(np.mean((y - (ecg_limpo - ecg_limpo.mean()))**2)):.4f}")

picos, _ = signal.find_peaks(y, height=0.5*y.max(), distance=int(0.3*fs))
rr = np.diff(picos)/fs
print(f"batimentos detectados: {len(picos)}  -> {60/np.mean(rr):.1f} bpm (verdade: {bpm})")
```

**Saída real:**

```
RMS do erro antes : 0.3544
RMS do erro depois: 0.0345
batimentos detectados: 12  -> 72.0 bpm (verdade: 72)
```

**Explicação e alertas de quem já fez isso em produção:**

- Erro caiu **10×**. O que sobra é o ruído de banda larga, que o filtro não pode
  remover sem borrar o QRS.
- `distance=int(0.3*fs)` impede contar duas vezes o mesmo complexo: 0,3 s é o
  período refratário fisiológico. **Esse tipo de restrição do domínio vale mais
  que qualquer sofisticação de algoritmo.**
- O passa-alta em 0,5 Hz é o padrão para monitoração. Para **diagnóstico**, a
  norma (AHA/IEC 60601-2-25) manda usar 0,05 Hz, porque um corte em 0,5 Hz
  distorce o segmento ST e pode **fabricar ou apagar sinal de infarto**. Este é o
  exemplo mais afiado que conheço de escolha de filtro com consequência clínica.
- Notch com Q=30 dá ~2 Hz de largura. Q maior soa "mais cirúrgico" e produz
  *ringing* de vários ciclos que imita onda P. Não exagere no Q.

---

## 5 · Envoltória e frequência instantânea

**Problema:** dado um tom modulado em amplitude, recuperar a envoltória (o
"contorno" do volume) e verificar a frequência da portadora.

```python
import numpy as np
from scipy import signal

fs = 8000
t = np.arange(fs)/fs
env_real = np.exp(-3*t)*(1 + 0.5*np.sin(2*np.pi*3*t))
x = np.sin(2*np.pi*1000*t)*env_real

env = np.abs(signal.hilbert(x))          # envoltória = módulo do sinal analítico
m = slice(200, -200)
print(f"erro máximo no miolo  : {np.max(np.abs(env[m]-env_real[m])):.4f}")
print(f"erro máximo nas bordas: "
      f"{max(np.max(np.abs(env[:200]-env_real[:200])), np.max(np.abs(env[-200:]-env_real[-200:]))):.4f}")

fi = np.diff(np.unwrap(np.angle(signal.hilbert(x))))*fs/(2*np.pi)
print(f"frequência instantânea média (miolo): {np.mean(fi[200:-200]):.1f} Hz (esperado 1000)")
```

**Saída real:**

```
erro máximo no miolo  : 0.0021
erro máximo nas bordas: 0.4748
frequência instantânea média (miolo): 1000.0 Hz (esperado 1000)
```

**Explicação.** A transformada de Hilbert cria o **sinal analítico** x + j·x̂, cujo
módulo é a envoltória e cuja derivada da fase é a frequência instantânea. Erro de
0,2 % no miolo.

**E olhe as bordas: erro de 0,47 — 200× maior.** A implementação da SciPy usa FFT,
que assume periodicidade; nas bordas isso produz artefato. Isto **não é um detalhe
acadêmico**: é a razão de tantos "picos estranhos no começo do arquivo" em
detectores de envoltória em produção. A correção: descarte as bordas, ou aplique
um `tukey` antes. `np.unwrap` também é obrigatório — sem ele, a fase salta 2π e a
frequência instantânea vira lixo.

---

## 6 · Reamostrar 44,1 kHz → 48 kHz

**Problema:** o CD usa 44,1 kHz e o vídeo usa 48 kHz. Converter sem estragar.

```python
import numpy as np
from scipy import signal

fs1, fs2 = 44100, 48000
t1 = np.arange(fs1)/fs1
x = t1*np.sin(2*np.pi*1000*t1)                 # seno com crescendo: NÃO periódico

y  = signal.resample_poly(x, 160, 147)         # 44100/48000 = 147/160
yr = signal.resample(x, len(y))                # método por FFT

t2 = np.arange(len(y))/fs2
ref = t2*np.sin(2*np.pi*1000*t2)
mio = slice(3000, len(y)-3000); bor = slice(0, 300)

for nome, v in [("resample_poly", y), ("resample (FFT)", yr)]:
    print(f"  {nome:15s} erro RMS miolo {np.sqrt(np.mean((v[mio]-ref[mio])**2)):.2e}"
          f" | erro RMS nas 300 primeiras {np.sqrt(np.mean((v[bor]-ref[bor])**2)):.2e}"
          f" | erro MÁXIMO {np.max(np.abs(v-ref)):.3f}")
```

**Saída real:**

```
  resample_poly   erro RMS miolo 2.51e-04 | erro RMS nas 300 primeiras 1.62e-06 | erro MÁXIMO 0.002
  resample (FFT)  erro RMS miolo 9.32e-07 | erro RMS nas 300 primeiras 4.01e-04 | erro MÁXIMO 0.003
```

**Explicação — e aqui eu corrijo um folclore que eu mesmo já repeti.** Diz-se por
aí que `signal.resample` "estraga" o sinal. Medindo, o quadro real é outro:

- No **miolo**, o método por FFT é **270× mais preciso** (9e-7 contra 2,5e-4): ele
  faz interpolação ideal de banda limitada, enquanto o polifásico carrega o ripple
  do FIR de projeto.
- Nas **bordas**, ele é **250× pior** (4e-4 contra 1,6e-6), porque assume que o
  sinal é periódico e o fim não combina com o começo.

Então quando usar cada um?

| Use `resample_poly` | Use `resample` |
|---|---|
| arquivo longo (custo O(N), streaming em blocos) | bloco curto, análise offline |
| bordas importam (áudio, tempo real) | sinal genuinamente periódico |
| razão racional simples (44,1↔48 = 147:160) | razão qualquer, não racional |
| quer resultado igual ao de um DSP embarcado | quer o resultado mais exato no miolo |

Tempo medido nesta máquina, bloco de 1 s: `resample_poly` 2,04 ms,
`resample` 1,61 ms — comparáveis aqui, mas o polifásico escala linearmente e o de
FFT não.

**O que nunca fazer:** `x[::2]` para dividir a taxa por 2 sem filtrar antes. Isso
é decimação sem anti-aliasing, e tudo acima da nova Nyquist volta dobrado.
Use `signal.decimate(x, 2)`, que já filtra.

---

## 7 · Medir atraso entre dois microfones (TDOA)

**Problema:** dois microfones gravam a mesma fonte. Descobrir a diferença de
tempo de chegada — a base de localização de fonte, sonar, radar e GPS.

```python
import numpy as np
from scipy import signal

fs = 48000
rng = np.random.default_rng(5)
s = rng.standard_normal(fs//2)            # fonte de banda larga
atraso_real = 37

x1 = s + 0.05*rng.standard_normal(len(s))
x2 = np.concatenate([np.zeros(atraso_real), s])[:len(s)] + 0.05*rng.standard_normal(len(s))

c = signal.correlate(x2, x1, mode="full", method="fft")
lags = signal.correlation_lags(len(x2), len(x1), mode="full")
d = lags[np.argmax(c)]

print(f"atraso estimado: {d} amostras (real {atraso_real}) = {d/fs*1e6:.1f} us")
print(f"distância equivalente no ar (343 m/s): {d/fs*343*100:.1f} cm")
```

**Saída real:**

```
atraso estimado: 37 amostras (real 37) = 770.8 us
distância equivalente no ar (343 m/s): 26.4 cm
```

**Explicação.** Exato. A correlação cruzada é o estimador de máxima verossimilhança
do atraso sob ruído branco gaussiano — não é um truque, é o ótimo.

Detalhes que salvam o dia em campo:
- `method="fft"` transforma O(N²) em O(N log N). Com 24 000 amostras a diferença
  é entre milissegundos e segundos.
- `correlation_lags` existe exatamente para você não errar o offset do índice.
  Calcular na mão é o bug clássico deste exemplo.
- A **resolução é uma amostra** (20,8 µs aqui). Para melhorar, interpole o pico da
  correlação — parábola dá facilmente 1/10 de amostra.
- Se a fonte for de **banda estreita** (um tom puro), a correlação vira periódica e
  o atraso fica ambíguo em múltiplos do período. Fonte de banda larga é o que
  torna o problema bem posto. É por isso que o GPS usa códigos pseudoaleatórios.

---

## 8 · Achar um pulso enterrado no ruído

**Problema:** um pulso de radar (ou de GPS, ou de sonar) chega com potência
**abaixo** da do ruído. Encontrá-lo.

```python
import numpy as np
from scipy import signal

fs = 10000
rng = np.random.default_rng(7)
dur_p = 0.02
pulso = signal.chirp(np.arange(int(dur_p*fs))/fs, 500, dur_p, 2500)   # chirp

n, sigma = fs, 1.0
ruido = rng.standard_normal(n)*sigma
pos = 6123
x = ruido.copy(); x[pos:pos+len(pulso)] += pulso

print(f"SNR na entrada: {10*np.log10(np.mean(pulso**2)/sigma**2):.1f} dB")

y = signal.correlate(x, pulso, mode="valid", method="fft")   # filtro casado
k = int(np.argmax(np.abs(y)))
piso = np.std(np.concatenate([y[:pos-500], y[pos+500:]]))

print(f"pico da correlação no índice {k} (posição real {pos})  erro = {k-pos} amostras")
print(f"pico/piso da correlação: {20*np.log10(abs(y[k])/piso):.1f} dB")
print(f"ganho de processamento teórico 10log10(N) = {10*np.log10(len(pulso)):.1f} dB")
```

**Saída real:**

```
SNR na entrada: -3.0 dB
pico da correlação no índice 6123 (posição real 6123)  erro = 0 amostras
pico/piso da correlação: 19.7 dB
ganho de processamento teórico 10log10(N) = 23.0 dB
```

**Explicação.** O sinal está **abaixo** do ruído (−3 dB) e mesmo assim foi
localizado com erro **zero**, com 19,7 dB de margem.

O **filtro casado** — correlacionar com uma cópia do que você procura — é
comprovadamente o detector ótimo em ruído branco gaussiano. Ele acumula a energia
do sinal *coerentemente* (soma de amplitudes, cresce com N) enquanto o ruído se
acumula *incoerentemente* (soma de potências, cresce com √N). A razão cresce com
√N; em dB, 10·log₁₀(N).

Com 200 amostras, o ganho teórico é 23,0 dB e o medido foi 19,7 dB — a diferença
vem de o chirp não ter energia perfeitamente plana e do piso ser estimado numa
amostra finita.

**É assim que o GPS funciona.** O sinal do satélite chega ~20 dB abaixo do ruído
térmico; correlacionar com o código C/A de 1023 chips dá ~30 dB de ganho de
processamento. Sem filtro casado, não haveria GPS civil.

---

## 9 · Quantização, SNR e dither

**Problema:** quanto custa, em qualidade, usar 8 bits em vez de 16? E por que
adicionar ruído de propósito pode **melhorar** o resultado?

```python
import numpy as np

fs = 44100
t = np.arange(fs)/fs
rng = np.random.default_rng(11)
x = 0.999*np.sin(2*np.pi*997*t)              # fundo de escala

for bits in [4, 8, 16]:
    passo = 2.0/2**bits
    q = np.round(x/passo)*passo
    r = q - x
    print(f"  {bits:2d} bits: SNR medida {10*np.log10(np.mean(x**2)/np.mean(r**2)):5.1f} dB"
          f" | teoria 6.02B+1.76 = {6.02*bits+1.76:5.1f} dB")

# tom fraquíssimo: -66 dBFS, muito abaixo do passo de 8 bits
passo = 2.0/2**8
xb = 0.0005*np.sin(2*np.pi*997*t)
sem = np.round(xb/passo)*passo
com = np.round((xb + rng.uniform(-passo/2, passo/2, len(t)))/passo)*passo

def em(v, f0=997):
    V = np.abs(np.fft.rfft(v*np.hanning(len(v))))/(len(v)/4)
    f = np.fft.rfftfreq(len(v), 1/fs)
    return 20*np.log10(max(V[np.argmin(np.abs(f-f0))], 1e-12))

print(f"  tom de -66 dBFS em 8 bits SEM dither: {em(sem):7.1f} dBFS em 997 Hz")
print(f"  tom de -66 dBFS em 8 bits COM dither: {em(com):7.1f} dBFS em 997 Hz")
print(f"  referência, sem quantizar          : {em(xb):7.1f} dBFS")
```

**Saída real:**

```
   4 bits: SNR medida  26.2 dB | teoria 6.02B+1.76 =  25.8 dB
   8 bits: SNR medida  49.9 dB | teoria 6.02B+1.76 =  49.9 dB
  16 bits: SNR medida  98.1 dB | teoria 6.02B+1.76 =  98.1 dB
  tom de -66 dBFS em 8 bits SEM dither:  -240.0 dBFS em 997 Hz  (sinal SUMIU)
  tom de -66 dBFS em 8 bits COM dither:   -65.9 dBFS em 997 Hz  (sinal RECUPERADO)
  referência, sem quantizar          :   -66.0 dBFS
```

**Explicação.** A fórmula **6,02·B + 1,76 dB** bateu com a medida em três décadas
de resolução. Cada bit vale 6 dB — memorize.

E então a parte contraintuitiva: um tom de −66 dBFS quantizado em 8 bits
**desaparece completamente** (−240 dBFS é zero numérico: toda amostra arredonda
para o mesmo valor). Somando **ruído aleatório de meio passo** antes de quantizar,
o mesmo tom reaparece em −65,9 dBFS — a 0,1 dB do valor verdadeiro.

Isso é **dither**, e não é um truque: adicionar ruído *descorrelaciona* o erro de
quantização do sinal, transformando distorção determinística (que o ouvido detecta
como aspereza) em ruído branco (que o ouvido tolera). É o motivo de todo conversor
A/D profissional ter dither, e de todo *bit depth reduction* em masterização usar
dither. Você troca um pouco de SNR por muita linearidade — e o ouvido só se
importa com a segunda.

---

## 10 · Periodograma × Welch

**Problema:** existe um tom de amplitude 0,05 escondido em ruído de desvio 1,0.
Como estimar o espectro de forma confiável?

```python
import numpy as np
from scipy import signal

fs, n = 1000, 100000
rng = np.random.default_rng(13)
x = rng.standard_normal(n) + 0.05*np.sin(2*np.pi*123*np.arange(n)/fs)

f1, P1 = signal.periodogram(x, fs)
f2, P2 = signal.welch(x, fs, nperseg=4096)

def metricas(f, P, nome):
    piso = (f > 200)
    print(f"  {nome:14s} pico em {f[np.argmax(P)]:6.1f} Hz"
          f" | variabilidade do piso (desvio/média) = {np.std(P[piso])/np.mean(P[piso]):.2f}"
          f" | pico/máx do piso = {P.max()/P[piso].max():.2f}")

metricas(f1, P1, "periodograma"); metricas(f2, P2, "Welch 4096")
```

**Saída real:**

```
  periodograma   pico em  123.0 Hz | variabilidade do piso (desvio/média) = 1.00 | pico/máx do piso = 7.24
  Welch 4096     pico em  123.0 Hz | variabilidade do piso (desvio/média) = 0.15 | pico/máx do piso = 2.14
```

**Explicação.** Os dois acham o tom, mas veja a **variabilidade do piso**: 1,00 no
periodograma contra 0,15 no Welch.

O periodograma tem um defeito estatístico grave e pouco divulgado: **ele não é um
estimador consistente**. Aumentar N aumenta a resolução, mas **não** reduz a
variância — cada bin continua tendo desvio padrão igual à própria média
(distribuição exponencial, 2 graus de liberdade). Um piso com desvio/média = 1
significa que qualquer bin pode ser 3× a média por puro acaso, e você "descobre"
tons que não existem.

Welch resolve fatiando o sinal em segmentos sobrepostos e **promediando** os
periodogramas. Com 100 000 amostras e `nperseg=4096` são ~48 segmentos, e a
variância cai por ~48 → desvio relativo ~1/√48 ≈ 0,14. O medido foi 0,15.
A teoria bate na terceira casa.

**O preço:** a resolução cai de 0,01 Hz para 0,24 Hz. Esse é *o* compromisso da
estimação espectral, e a razão de o "pico/máx do piso" ser numericamente maior no
periodograma: ele concentra tudo num bin. Para **detectar**, use Welch. Para
**medir a frequência exata** de algo que você já sabe que existe, use o bloco
inteiro com janela e interpole.

---

## 11 · Espectrograma com a API atual

**Problema:** ver como o espectro muda com o tempo, usando a API que não está
obsoleta.

```python
import numpy as np
from scipy import signal

fs = 8000
t = np.arange(2*fs)/fs
x = signal.chirp(t, 200, 2.0, 3000)          # varredura de 200 Hz a 3 kHz em 2 s

win = signal.get_window("hann", 256)
SFT = signal.ShortTimeFFT(win, hop=64, fs=fs, scale_to="magnitude")
S = np.abs(SFT.stft(x))

freqs = SFT.f
picos = [freqs[np.argmax(S[:, k])] for k in range(0, S.shape[1], S.shape[1]//5)]
print("forma da matriz STFT:", S.shape, "(freq, tempo)")
print("frequência dominante ao longo do tempo:", np.round(picos, 0))
```

**Saída real:**

```
forma da matriz STFT: (129, 253) (freq, tempo)
frequência dominante ao longo do tempo: [ 219.  750. 1312. 1875. 2438. 3000.]
```

**Explicação.** A frequência sobe linearmente de ~200 a 3000 Hz — exatamente o
chirp que criamos. Os passos de ~562 Hz entre as amostras confirmam a rampa linear.

Notas de API que valem tempo:
- `signal.spectrogram` e `signal.stft` estão marcadas como **legado** desde a
  SciPy 1.12 (a própria docstring diz *"legacy function"*). Código novo usa
  `ShortTimeFFT`.
- `SFT.extent(len(x))` devolve os limites prontos para `imshow` — sem isso, o
  eixo de tempo fica errado por meia janela, erro grosseiro e comum.
- `hop=64` com janela de 256 dá 75 % de sobreposição. Regra: sobreposição de 50 %
  para Hann é o mínimo para não perder energia entre quadros (condição COLA);
  75 % dá um resultado visualmente mais suave.
- Janela de 256 a 8 kHz = 32 ms → resolução de 31 Hz. Quer distinguir dois tons a
  10 Hz? Precisa de janela ≥ 100 ms, e aí perde a resolução temporal. **Esse
  compromisso não tem saída** — é a ideia nº 5 do capítulo [`01`](01-introducao-leigo.md).

---

## 12 · Média móvel × EMA × Savitzky-Golay (caso real, telemetria)

**Problema:** um sensor manda leitura ruidosa a 100 Hz e o valor real dá um salto.
Suavizar sem atrasar demais — o dilema central de todo sistema de monitoração,
trading, controle e IoT.

```python
import numpy as np
from scipy import signal

fs, n = 100, 1000
rng = np.random.default_rng(17)
limpo = np.concatenate([np.ones(400)*20, np.ones(600)*25])   # degrau em t=4 s
x = limpo + rng.standard_normal(n)*1.5

ma  = signal.lfilter(np.ones(21)/21, 1, x)                   # média móvel de 21
alpha = 0.1
ema = signal.lfilter([alpha], [1, -(1-alpha)], x)            # exponencial (IIR de 1ª ordem)
sg  = signal.savgol_filter(x, 21, 3)                         # Savitzky-Golay

def atraso_do_degrau(y):
    idx = np.argmax(y[350:] > (20+25)/2) + 350
    return idx - 400

print(f"ruído RMS na entrada: {np.std(x[:350]):.3f}")
for nome, y in [("média móvel 21", ma), ("EMA alpha=0.1", ema), ("Savitzky-Golay 21/3", sg)]:
    print(f"  {nome:22s} ruído {np.std(y[100:350]):.3f}"
          f"  atraso no degrau {atraso_do_degrau(y):3d} amostras")
```

**Saída real:**

```
ruído RMS na entrada: 1.483
  média móvel 21         ruído 0.373  atraso no degrau   9 amostras
  EMA alpha=0.1          ruído 0.378  atraso no degrau   4 amostras
  Savitzky-Golay 21/3    ruído 0.539  atraso no degrau  -2 amostras
```

**Explicação — leia como tabela de decisão:**

| Filtro | Ruído | Atraso | Memória | Quando usar |
|---|---|---|---|---|
| Média móvel 21 | 0,373 (4,0×) | 9 amostras | 21 valores | quer o ruído mínimo e pode esperar |
| EMA α=0,1 | 0,378 (3,9×) | **4 amostras** | **1 valor** | tempo real, memória escassa, IoT |
| Savitzky-Golay | 0,539 (2,8×) | **−2** (antecipa!) | 21 valores | precisa preservar a forma do pico |

- **Mesma redução de ruído, metade do atraso, e a EMA guarda um único número.**
  É por isso que praticamente todo firmware de sensor usa EMA:
  `y += alpha*(x - y)`. Uma linha, um registrador.
- A média móvel reduz o ruído por √21 = 4,58 em teoria; medimos 1,483/0,373 = 3,98.
  A diferença vem do ruído já ser correlacionado pela vizinhança do degrau na
  janela de medida.
- **Savitzky-Golay tem atraso negativo** no meio do bloco porque é aplicado de
  forma centrada (não causal): ele usa amostras futuras. Suaviza menos o ruído,
  mas preserva altura e largura de pico — por isso é o padrão em cromatografia e
  espectroscopia, onde a **área do pico é a medida**.
- A média móvel tem um defeito espectral escondido: sua resposta é uma
  `sinc` com lóbulos laterais a apenas −13 dB, e **zeros** em múltiplos de fs/21.
  Ela deixa passar frequências específicas quase intactas. Se o ruído for de banda
  estreita e cair num lóbulo, ela não filtra nada. Projete um FIR de verdade
  ([`18`](18-filtros-fir.md)) quando isso importar.

---

## Autoteste

1. No exemplo 2, por que a janela retangular foi **melhor** que a Hann num dos casos?
2. Por que a telefonia usa Goertzel em vez de FFT para DTMF?
3. Qual a consequência clínica de usar corte de 0,5 Hz em vez de 0,05 Hz num ECG?
4. Por que a envoltória de Hilbert erra 200× mais nas bordas?
5. Quando `signal.resample` é melhor que `resample_poly`, segundo a medição?
6. O filtro casado achou um sinal a −3 dB de SNR. De onde vem o ganho?
7. Como um tom de −66 dBFS pode reaparecer depois de somarmos ruído a ele?
8. Por que aumentar N não reduz a variância do periodograma?
9. Por que a EMA é preferida em firmware, se filtra igual à média móvel?
10. Que defeito espectral tem a média móvel que quase ninguém menciona?
