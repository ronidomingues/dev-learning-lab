# 05 · Manual de uso — referência consultável

`Nível: intermediário` · `Atualizado em: 14/08/2026`
`Base: SciPy 1.15.3 / NumPy 2.2.6 · notas de obsolescência conferidas contra a documentação instalada`

Referência de consulta, **organizada por tarefa**, não por ordem alfabética.
Duas metades:

- **Parte I — notação:** como se lê a linguagem escrita do campo (símbolos, convenções).
- **Parte II — API:** o que chamar em Python para cada coisa.

---

# Parte I · Notação: como ler a linguagem do campo

Sem isso, todo livro e todo paper parecem hieróglifo. Com isso, viram legíveis
em uma tarde.

## Símbolos

| Símbolo | Lê-se | Significa |
|---|---|---|
| `x(t)` | "xis de tê" | sinal **contínuo**. Parênteses ⇒ tempo contínuo |
| `x[n]` | "xis de ene" | sinal **discreto**. Colchetes ⇒ índice inteiro. **A convenção mais importante da notação** |
| `δ(t)`, `δ[n]` | delta | impulso. No discreto: 1 em n=0, 0 no resto. No contínuo: distribuição de área 1 |
| `u(t)`, `u[n]` | degrau | 0 antes de 0, 1 a partir de 0 |
| `h[n]` | "agá de ene" | **resposta ao impulso** do sistema. A letra é sempre h |
| `y[n]` | saída | resposta do sistema à entrada x |
| `*` | "convoluído com" | convolução. `y = x * h`. **Não é multiplicação** |
| `X(f)`, `X(ω)` | maiúscula | transformada de Fourier de x. Maiúscula = domínio da frequência |
| `X(e^{jω})` | — | transformada de Fourier de **tempo discreto** (DTFT) |
| `X[k]` | — | **DFT**: espectro discreto, k = índice do bin |
| `X(z)`, `H(z)` | — | transformada Z |
| `H(s)` | — | transformada de Laplace (mundo analógico) |
| `f` | frequência | em hertz (ciclos por segundo) |
| `ω` (ômega) | frequência angular | ω = 2πf, em rad/s |
| `Ω` ou `ω̂` | frequência **normalizada** | rad/amostra, no intervalo (−π, π]. π ⇔ Nyquist |
| `fs`, `Fs`, `f_s` | taxa de amostragem | em Hz. `T = 1/fs` é o período de amostragem |
| `N` | comprimento | número de amostras do bloco/DFT |
| `j` | unidade imaginária | engenharia usa **j** (o **i** é corrente elétrica). Matemática usa i |
| `*` sobrescrito (`x*`) | conjugado | troca o sinal da parte imaginária |
| `⌊·⌋`, `⌈·⌉` | piso, teto | arredondar para baixo/cima |
| `E{·}` | valor esperado | média estatística (não temporal) |
| `R_xx[k]` | autocorrelação | correlação do sinal com ele mesmo atrasado de k |
| `S_xx(f)` | densidade espectral de potência | quanto de potência por hertz |
| `∘—•` ou `↔` | par de transformada | "isto no tempo corresponde àquilo na frequência" |

## Convenções que confundem e por quê

**Três frequências diferentes, todas chamadas de "frequência":**

| Nome | Unidade | Faixa útil | Onde aparece |
|---|---|---|---|
| f | Hz | 0 a fs/2 | especificação, cliente, gráfico |
| ω = 2πf | rad/s | 0 a π·fs | livros de sinais contínuos |
| Ω = ω/fs = 2πf/fs | rad/amostra | 0 a π | livros de DSP, transformada Z |
| f/(fs/2) | "normalizada por Nyquist" | 0 a 1 | **SciPy e MATLAB**, quando você não passa `fs` |

Converter é trivial, confundir é catastrófico. A última linha é a que mais causa
estrago porque é a convenção *da ferramenta*, não da teoria. Regra prática: **passe
sempre `fs=` explicitamente na SciPy** e o problema desaparece.

**Dois "N" diferentes:** N como comprimento do sinal e N como ordem do filtro. Em
FIR, `numtaps = ordem + 1`. Livros divergem; a SciPy usa `numtaps` para FIR e
`N = ordem` para IIR (`butter(N, ...)`). Sim, é inconsistente.

**dB de amplitude × dB de potência:** 20·log₁₀ para amplitude/tensão,
10·log₁₀ para potência/energia. Errar dá fator 2 no expoente — 6 dB viram 3 dB.

| Referência | Nome | Uso |
|---|---|---|
| 1,0 em escala digital | **dBFS** | áudio digital; 0 dBFS é o máximo, tudo é negativo |
| 1 V | dBV | equipamento |
| 0,775 V | dBu | áudio profissional |
| 1 mW em 600 Ω | dBm | RF e telecom |
| 20 µPa | dB SPL | acústica; o silêncio audível é 0 dB SPL |

**Números que vale decorar:**

| Valor | Significado |
|---|---|
| 3,01 dB | fator de crista de uma senoide; também "metade da potência" |
| 6,02 dB | um bit de resolução, ou o dobro da amplitude |
| 6,02·B + 1,76 dB | SNR máxima de um quantizador de B bits |
| −13 dB | maior lóbulo lateral da janela retangular |
| −31 dB | idem, janela Hann |
| 1200·log₂(f₂/f₁) | diferença em **cents** entre duas frequências |
| 2^(1/12) ≈ 1,0595 | um semitom |

---

# Parte II · API: o que chamar para cada tarefa

Convenção usada abaixo:

```python
import numpy as np
from scipy import signal, fft
```

## Criar sinais

| Tarefa | Chamada |
|---|---|
| vetor de tempo | `t = np.arange(N)/fs` |
| senoide | `np.sin(2*np.pi*f0*t)` |
| exponencial complexa | `np.exp(2j*np.pi*f0*t)` |
| varredura linear/log | `signal.chirp(t, f0, t1, f1, method='linear'\|'logarithmic')` |
| impulso | `signal.unit_impulse(N)` ou `x=np.zeros(N); x[0]=1` |
| quadrada / dente de serra | `signal.square(2*np.pi*f0*t)`, `signal.sawtooth(...)` |
| ruído branco gaussiano | `np.random.default_rng(42).standard_normal(N)` |
| pulso gaussiano | `signal.gausspulse(t, fc=1000, bw=0.5)` |

⚠️ `signal.square` e `signal.sawtooth` geram a onda **ideal**, com harmônicos acima
de Nyquist — ou seja, com aliasing. Para síntese de áudio séria use forma
antisserrilhada (PolyBLEP, ou soma de harmônicos limitada em banda).

## Transformadas

| Tarefa | Chamada | Observação |
|---|---|---|
| FFT de sinal real | `fft.rfft(x)` / `np.fft.rfft(x)` | devolve `N//2+1` valores. **Use esta** para sinal real |
| inversa | `fft.irfft(X, n=N)` | passe `n` explicitamente ou perde a última amostra em N ímpar |
| FFT complexa | `fft.fft(x)`, `fft.ifft(X)` | para sinal I/Q, banda-base |
| eixo de frequências | `np.fft.rfftfreq(N, 1/fs)` | **sempre use isto** |
| reordenar espectro complexo | `fft.fftshift(X)`, `fftfreq` + `fftshift` | põe DC no centro |
| DCT (usada em JPEG/MP3) | `fft.dct(x, type=2, norm='ortho')` | tipo 2 é a "a DCT" |
| Hilbert / envoltória | `signal.hilbert(x)` → sinal analítico | `np.abs(...)` = envoltória, `np.angle` = fase instantânea |
| tamanho ótimo de FFT | `fft.next_fast_len(N)` | acelera bastante quando N é primo |

`scipy.fft` é mais rápido que `numpy.fft` (pocketfft, multithread, aceita
`workers=-1`). Prefira `scipy.fft` em código de produção.

## Janelas

| Chamada | Quando usar |
|---|---|
| `signal.get_window('hann', N)` | padrão para análise geral. Comece por ela |
| `'hamming'` | lóbulo lateral próximo menor; cauda decai mais devagar |
| `'blackmanharris'` | quando um sinal fraco está perto de um forte (−92 dB) |
| `'flattop'` | quando você precisa da **amplitude** correta, não da frequência |
| `'kaiser', beta` | ajustável: β=0 retangular, β≈8,6 ≈ Blackman |
| `'boxcar'` (retangular) | transiente, ou quando o bloco é exatamente periódico |
| `'tukey', alpha` | quer só suavizar as bordas |
| `'dpss'` | análise multitaper, estimação espectral de baixa variância |

`sym=False` (padrão em `get_window`) para **análise**; `sym=True` para **projeto de
filtro**. A diferença é uma amostra e a consequência é vazamento a mais.

## Análise espectral

| Tarefa | Chamada | Status |
|---|---|---|
| PSD por Welch | `signal.welch(x, fs, nperseg=1024)` | ✅ atual e recomendado |
| espectro cruzado | `signal.csd(x, y, fs, ...)` | ✅ |
| coerência | `signal.coherence(x, y, fs, ...)` | ✅ |
| periodograma simples | `signal.periodogram(x, fs)` | ✅ mas ruidoso — prefira Welch |
| **STFT/espectrograma** | `signal.ShortTimeFFT(win, hop, fs)` | ✅ **API atual (SciPy ≥ 1.12)** |
| espectrograma | `signal.spectrogram(...)` | ⚠️ **legado** — a própria docstring diz "legacy function" |
| STFT / ISTFT | `signal.stft(...)`, `signal.istft(...)` | ⚠️ **legado**, idem |
| Lomb-Scargle (amostragem irregular) | `signal.lombscargle(t, x, w)` | ✅ para dados sem taxa fixa |
| achar picos | `signal.find_peaks(X, height=, distance=, prominence=)` | `prominence` é o parâmetro que resolve 90 % dos casos |

Uso moderno do espectrograma:

```python
win = signal.get_window('hann', 1024)
SFT = signal.ShortTimeFFT(win, hop=256, fs=fs, scale_to='magnitude')
S = SFT.stft(x)                   # matriz complexa [freq, tempo]
S_db = 20*np.log10(np.abs(S) + 1e-12)
extent = SFT.extent(len(x))       # já devolve os limites certos para imshow
```

## Projeto de filtros FIR

| Tarefa | Chamada |
|---|---|
| passa-baixa por janela | `signal.firwin(numtaps, cutoff, fs=fs)` |
| passa-alta | `signal.firwin(numtaps, cutoff, fs=fs, pass_zero=False)` |
| passa-faixa | `signal.firwin(numtaps, [f1, f2], fs=fs, pass_zero=False)` |
| rejeita-faixa | `signal.firwin(numtaps, [f1, f2], fs=fs, pass_zero=True)` |
| ótimo equiripple (Parks–McClellan) | `signal.remez(numtaps, bands, desired, fs=fs)` |
| mínimos quadrados | `signal.firls(numtaps, bands, desired, fs=fs)` |
| estimar ordem necessária | `signal.kaiserord(ripple_db, largura_normalizada)` |
| resposta em frequência | `w, H = signal.freqz(h, fs=fs)` |
| atraso de grupo | `signal.group_delay((h, 1), fs=fs)` |

`numtaps` **ímpar** para passa-alta e rejeita-faixa — com número par o filtro é
obrigado a ter zero em Nyquist e o projeto falha (a SciPy avisa).

## Projeto de filtros IIR

| Tarefa | Chamada |
|---|---|
| Butterworth | `signal.butter(N, Wn, btype, fs=fs, output='sos')` |
| Chebyshev I / II | `signal.cheby1(N, rp, ...)`, `cheby2(N, rs, ...)` |
| Elíptico | `signal.ellip(N, rp, rs, ...)` |
| Bessel (fase quase linear) | `signal.bessel(N, Wn, ..., norm='phase')` |
| ordem mínima para uma spec | `signal.buttord(wp, ws, gpass, gstop, fs=fs)` (e `cheb1ord`, `ellipord`) |
| notch / peak | `signal.iirnotch(w0, Q, fs=fs)`, `signal.iirpeak(...)` |
| projeto genérico | `signal.iirdesign(wp, ws, gpass, gstop, output='sos')` |
| analógico → digital | `signal.bilinear_zpk`, `signal.bilinear` |
| resposta | `signal.sosfreqz(sos, fs=fs)` |

> **Use `output='sos'` sempre.** Em forma direta (`b, a`), IIR de ordem ≥ 6 perde
> precisão e pode ficar instável em float64 — e vai ficar, em float32. Se você
> receber `b, a` de terceiros: `sos = signal.tf2sos(b, a)`.

## Aplicar filtros

| Tarefa | Chamada | Causal? |
|---|---|---|
| FIR ou IIR, forma direta | `signal.lfilter(b, a, x)` | sim |
| IIR em SOS | `signal.sosfilt(sos, x)` | sim |
| **fase zero** | `signal.filtfilt(b, a, x)` / `signal.sosfiltfilt(sos, x)` | **não** (offline) |
| FIR longo, rápido | `signal.fftconvolve(x, h, mode='same')` | sim (com atraso) |
| escolha automática | `signal.oaconvolve(x, h)` (overlap-add) | sim |
| **processar em blocos** (streaming) | `zi = signal.sosfilt_zi(sos)*x[0]`; depois `y, zi = signal.sosfilt(sos, bloco, zi=zi)` | sim |
| condição inicial FIR | `signal.lfilter_zi(b, a)` | — |

O padrão de streaming acima é o que você usa em tempo real: **guarde o `zi` entre
os blocos**. Esquecer disso produz um clique na fronteira de cada bloco.

## Reamostragem (multitaxa)

| Tarefa | Chamada | Observação |
|---|---|---|
| taxa racional (ex. 44,1k → 48k) | `signal.resample_poly(x, up=160, down=147)` | ✅ **melhor opção geral**: polifásico, sem artefato de borda |
| via FFT | `signal.resample(x, num)` | assume o sinal **periódico**; produz artefato nas bordas |
| decimar (com filtro) | `signal.decimate(x, q, ftype='fir')` | nunca use `x[::q]` sem filtrar |
| interpolar | `signal.upfirdn(h, x, up, down)` | controle total |

44100 → 48000: `up=160, down=147` (porque 44100/48000 = 147/160).

## Correlação e detecção

| Tarefa | Chamada |
|---|---|
| correlação cruzada | `signal.correlate(x, y, mode='full', method='fft')` |
| eixo de atrasos | `signal.correlation_lags(len(x), len(y), mode='full')` |
| autocorrelação | `signal.correlate(x, x, ...)`, ou via FFT (mais rápido) |
| envoltória | `np.abs(signal.hilbert(x))` |
| detectar picos | `signal.find_peaks(...)` |
| casar com um modelo | correlação = **filtro casado**, ótimo em ruído branco gaussiano |

## Utilidades que economizam horas

| Chamada | O que faz |
|---|---|
| `signal.detrend(x)` | remove média ou tendência linear (antes de FFT, quase sempre útil) |
| `signal.medfilt(x, 5)` | mediana móvel: mata *spike* sem borrar a borda |
| `signal.savgol_filter(x, 51, 3)` | Savitzky-Golay: suaviza preservando pico e largura |
| `signal.hilbert(x)` | sinal analítico |
| `signal.zpk2sos`, `tf2sos`, `sos2tf` | conversão entre representações |
| `signal.freqz_zpk`, `signal.tf2zpk` | polos e zeros |
| `signal.dlti`, `signal.dimpulse`, `signal.dstep` | sistema discreto: resposta ao impulso e ao degrau |
| `np.unwrap(np.angle(H))` | fase sem os saltos de 2π. **Sempre** ao plotar fase |

## Padrões que só quem usa há anos conhece

1. **`fs=` em tudo.** Toda função de projeto e de resposta aceita `fs`. Passe.
   Você elimina de uma vez a classe inteira de bugs de normalização.
2. **`prominence` em vez de `height`** no `find_peaks`. Altura absoluta falha quando
   o piso varia; proeminência é relativa ao vale vizinho e funciona quase sempre.
3. **`method='fft'`** no `correlate` para sinais longos: O(N log N) contra O(N²).
   A partir de ~1000 amostras a diferença é de segundos para milissegundos.
4. **`signal.resample_poly`, nunca `signal.resample`**, salvo se o sinal for
   genuinamente periódico e você souber o período.
5. **`sosfiltfilt` em análise offline, `sosfilt` com `zi` em tempo real.** Escolher
   errado é o defeito mais comum em código de DSP que "funcionava no notebook".
6. **`np.maximum(np.abs(X), 1e-12)` antes de todo `log10`.** Bin exatamente zero
   existe e produz `-inf`, que envenena o gráfico inteiro.
7. **`fft.next_fast_len(N)`** antes de FFTs em lote. Um N primo pode ser 50× mais
   lento que o próximo N "bonito".
8. **`workers=-1`** em `scipy.fft.rfft` para usar todos os núcleos.
9. **`float32` para dados, `float64` para coeficientes.** Metade da memória e da
   banda com precisão sobrando para o sinal; coeficiente de IIR em float32 é que
   dá problema.
10. **`x -= x.mean()` antes de qualquer análise espectral.** DC vaza para os bins
    vizinhos e polui a faixa baixa, exatamente onde costuma estar seu sinal.

## Obsoleto ou legado — o que evitar

| Não use | Use no lugar | Por quê |
|---|---|---|
| `signal.spectrogram` | `signal.ShortTimeFFT(...).spectrogram()` | marcado como *legacy* desde a SciPy 1.12 |
| `signal.stft` / `istft` | `ShortTimeFFT.stft/istft` | idem; a nova trata bordas e escala corretamente |
| `output='ba'` em ordem alta | `output='sos'` | instabilidade numérica |
| `scipy.signal.hanning` | `np.hanning` / `signal.get_window('hann')` | removida na SciPy 1.13 |
| `np.fft` em código quente | `scipy.fft` | pocketfft, multithread |
| `signal.resample` genérico | `signal.resample_poly` | artefato de periodicidade |
| `scipy.signal.cwt`, `morlet`, `ricker` | PyWavelets (`pywt.cwt`) | removidas da SciPy 1.15 |
| MATLAB `filter` traduzido cru | `sosfilt` | o `filter` do MATLAB é forma direta II transposta |

## Equivalência MATLAB ↔ SciPy

| MATLAB | SciPy |
|---|---|
| `fft(x)` | `np.fft.fft(x)` |
| `fir1(n, Wn)` | `signal.firwin(n+1, Wn)` ← **atenção ao +1** |
| `butter(n, Wn)` | `signal.butter(n, Wn)` |
| `filter(b, a, x)` | `signal.lfilter(b, a, x)` |
| `filtfilt(b, a, x)` | `signal.filtfilt(b, a, x)` |
| `freqz(b, a)` | `signal.freqz(b, a)` |
| `conv(x, h)` | `np.convolve(x, h)` |
| `xcorr(x, y)` | `signal.correlate(x, y)` |
| `resample(x, p, q)` | `signal.resample_poly(x, p, q)` |
| `pwelch(x)` | `signal.welch(x)` |
| `hann(N)` | `np.hanning(N)` ← MATLAB `hann` é simétrica; `hanning` do MATLAB não é |

⚠️ No MATLAB, `Wn` é normalizada por Nyquist (0 a 1) — igual à SciPy sem `fs`.
Mas `fir1(n, ...)` gera **n+1** coeficientes, e `firwin(numtaps, ...)` gera
`numtaps`. Traduções literais erram por um.

---

## Autoteste

1. Qual a diferença entre `x(t)`, `x[n]`, `X[k]` e `X(e^{jω})`?
2. Um corte de 1 kHz a 48 kHz: qual o valor normalizado por Nyquist?
3. Por que `output='sos'` e não `'ba'`?
4. Quando usar `flattop` em vez de `hann`?
5. Qual função usar para converter 44,1 kHz em 48 kHz, e por quê essa e não a outra?
6. O que `zi` faz no `sosfilt` e o que acontece se você esquecer dele?
7. Cite três funções da SciPy marcadas como legado e o que as substitui.
8. `fir1(40, 0.3)` do MATLAB equivale a que chamada em SciPy?
