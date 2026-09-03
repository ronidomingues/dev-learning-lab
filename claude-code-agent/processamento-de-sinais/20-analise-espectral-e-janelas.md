# 20 · Análise espectral e janelas — como medir um espectro sem se enganar

`Nível: intermediário → avançado` · `Medições feitas em: 18/08/2026`
`Base: SciPy 1.15.3`

A FFT ([`16`](16-dft-e-fft.md)) devolve números. Este capítulo é sobre transformar
esses números numa **medida confiável** — e sobre as três formas de se enganar:
vazamento, festonamento e variância.

---

## 1 · O problema, em uma frase

Você quer o espectro de um sinal que dura para sempre. Você tem N amostras.
Pegar N amostras **é** multiplicar por um retângulo, e multiplicar no tempo é
**convoluir** na frequência ([`14 §4`](14-fourier.md)).

> **Você nunca mede o espectro do sinal. Você mede o espectro do sinal convoluído
> com o espectro da janela.**

Toda a arte está em escolher uma janela cujo espectro atrapalhe menos o que você
precisa medir.

---

## 2 · Vazamento espectral — o experimento decisivo

Dois tons: um forte em 100,3 Hz e um **70 dB mais fraco** em 108,3 Hz, separados
por 8 bins. Ambos em frequências não inteiras de bin (o caso realista).

```python
import numpy as np
from scipy import signal

fs, N = 1000, 1024
t = np.arange(N)/fs
f1, f2 = 100.3, 108.3
x = np.sin(2*np.pi*f1*t) + 10**(-70/20)*np.sin(2*np.pi*f2*t)

for j in ['boxcar', 'hann', 'hamming', 'blackmanharris']:
    w = signal.get_window(j, N)
    X = np.abs(np.fft.rfft(x*w)); X /= X.max()
    f = np.fft.rfftfreq(N, 1/fs)
    i2 = np.argmin(np.abs(f - f2))
    print(f"  {j:16s} nível medido no tom fraco: "
          f"{20*np.log10(X[i2-2:i2+3].max()):7.1f} dB   (verdadeiro -70.0 dB)")
```

Saída real:

```
  boxcar           nível medido no tom fraco:   -26.9 dB   (verdadeiro -70.0 dB)
  hann             nível medido no tom fraco:   -59.2 dB   (verdadeiro -70.0 dB)
  hamming          nível medido no tom fraco:   -45.5 dB   (verdadeiro -70.0 dB)
  blackmanharris   nível medido no tom fraco:   -70.1 dB   (verdadeiro -70.0 dB)
```

**Este é o resultado mais importante do capítulo.** O tom fraco existe em −70 dB.

- **Retangular:** mede −26,9 dB. **Erro de 43 dB.** O que você "vê" ali não é o tom
  fraco: é a saia do tom forte. Se você usasse esse número, reportaria um sinal
  200× mais forte do que ele é.
- **Hamming:** −45,5 dB. Ainda 25 dB errado. Repare que a Hamming, apesar de ter
  lóbulo lateral *próximo* melhor que a Hann (−42 vs −31 dB), sai **pior** aqui —
  porque a cauda dela decai devagar, e o que contamina a 8 bins de distância é a
  cauda, não o primeiro lóbulo.
- **Blackman-Harris:** −70,1 dB. **Erro de 0,1 dB.** Correto.

**A lição de projeto:** não escolha janela pelo nome nem pelo primeiro lóbulo
lateral. Escolha pela **taxa de decaimento da cauda** quando houver sinais fracos
longe de sinais fortes, e pelo **lóbulo principal estreito** quando os sinais forem
próximos e de amplitude parecida.

---

## 3 · Festonamento (*scalloping*) — o erro de amplitude

O outro erro que a janela controla: se a frequência cair **entre** dois bins, a
amplitude medida sai baixa. Quanto?

```python
for j in ['boxcar', 'hann', 'hamming', 'flattop']:
    w = signal.get_window(j, N)
    ganhos = []
    for d in np.linspace(0, 0.5, 11):           # desloca de 0 a meio bin
        xx = np.sin(2*np.pi*(100+d)*(fs/N)*t)
        X = np.abs(np.fft.rfft(xx*w))
        ganhos.append(X.max()/(np.sum(w)/2))
    print(f"  {j:10s} ganho de {min(ganhos):.4f} a {max(ganhos):.4f}"
          f"  -> perda máxima {20*np.log10(min(ganhos)/max(ganhos)):6.2f} dB")
```

Saída real:

```
  boxcar     ganho de 0.6380 a 1.0000  -> perda máxima  -3.90 dB
  hann       ganho de 0.8488 a 1.0000  -> perda máxima  -1.42 dB
  hamming    ganho de 0.8176 a 1.0000  -> perda máxima  -1.75 dB
  flattop    ganho de 0.9989 a 1.0003  -> perda máxima  -0.01 dB
```

**Com janela retangular, a mesma senoide pode ser medida com 3,9 dB de diferença
dependendo de onde ela cai na grade** — quase 40 % de erro de amplitude, sem nada
de errado no sinal.

E aqui está a razão de existir a **flattop**: 0,01 dB de erro. Ela foi projetada
com lóbulo principal deliberadamente largo e chato justamente para que a amplitude
medida não dependa da posição. É a janela dos analisadores de espectro de bancada
quando o modo é "medir nível".

**Regra:**

| Você quer medir | Use |
|---|---|
| **frequência** (onde está o pico) | Hann, ou Blackman-Harris se houver sinal fraco perto |
| **amplitude** (quanto vale o pico) | **flattop** |
| ambos com precisão | Hann + interpolação parabólica ([`16 §3`](16-dft-e-fft.md)) |

---

## 4 · Variância — e como validar um estimador sem se enganar

O periodograma tem um defeito estatístico grave: **não é consistente**. Aumentar N
melhora a resolução e **não** reduz a variância — cada bin continua com desvio
padrão igual à própria média ([`06 §10`](06-exemplos.md)).

**Welch** conserta promediando K segmentos: a variância cai por ~K, o desvio por √K.

### Como eu quase publiquei um número errado

Minha primeira medição comparou "desvio/média **ao longo da frequência**" com a
teoria 1/√K e deu discrepância de 3,6× para K grande. Parecia um achado.
Não era: a **metodologia** estava errada. Bins vizinhos de um espectro janelado são
correlacionados, então a dispersão ao longo do eixo de frequência não estima a
variância do estimador.

A medida correta é **Monte Carlo**: fixe um bin, repita o experimento com
realizações independentes de ruído, e meça a dispersão **entre realizações**.

```python
import numpy as np
from scipy import signal
fs, n = 1000, 200000
for nper in [256, 1024, 4096]:
    vals = []
    for s in range(60):
        x = np.random.default_rng(s).standard_normal(n)
        f, P = signal.welch(x, fs, nperseg=nper)
        vals.append(P[len(P)//3])                 # um bin fixo
    vals = np.array(vals)
    nseg = (n - nper//2)//(nper//2)
    print(f"  nperseg={nper:5d}: nseg={nseg:5d}  desvio/média (Monte Carlo) = "
          f"{vals.std()/vals.mean():.4f}   1/sqrt(nseg)={1/np.sqrt(nseg):.4f}")
```

Saída real:

```
  nperseg=  256: nseg= 1561  desvio/média (Monte Carlo) = 0.0264   1/sqrt(nseg)=0.0253
  nperseg= 1024: nseg=  389  desvio/média (Monte Carlo) = 0.0563   1/sqrt(nseg)=0.0507
  nperseg= 4096: nseg=   96  desvio/média (Monte Carlo) = 0.1113   1/sqrt(nseg)=0.1021
```

Agora bate: 0,0264 contra 0,0253 previsto. A pequena sobra (~5–10 %) é esperada e
tem explicação — os segmentos com 50 % de sobreposição **não são independentes**,
então o número efetivo de graus de liberdade é um pouco menor que K.

**Guarde as duas lições:**
1. Welch troca resolução por variância, na proporção exata 1/√K.
2. **Para validar um estimador, varie a realização, não o índice.** Medir dispersão
   ao longo de um eixo correlacionado é uma armadilha silenciosa — e ela produz
   números plausíveis, que é o pior tipo de erro.

---

## 5 · O compromisso completo do Welch

Com um sinal de N amostras totais e segmentos de L:

| Aumenta L | Efeito |
|---|---|
| resolução (fs/L) | **melhora** |
| número de segmentos K ≈ 2N/L | **piora** |
| variância | **piora** (∝ 1/K) |

Não há como melhorar os dois. Só há como escolher.

**Como eu escolho:**

- **Detectar** um tom desconhecido em ruído: segmentos curtos, muitos, variância
  baixa. O tom aparece consistentemente acima do piso.
- **Medir** a frequência de um tom que você já sabe que existe: bloco único, o mais
  longo possível, janela Hann, interpolação parabólica.
- **Caracterizar** ruído (piso de um conversor, DEP de vibração): Welch com
  `nperseg` entre 1024 e 8192 e sobreposição de 50 %.

**Sobreposição:** 50 % é o padrão para Hann e Hamming, porque satisfaz a condição
COLA (*constant overlap-add*) — a soma das janelas deslocadas é constante e nenhuma
amostra é subponderada. 75 % dá resultado visualmente mais suave com pouco ganho
estatístico real, e custa o dobro de FFTs.

---

## 6 · Normalização: o que o eixo Y significa

Quatro coisas diferentes chamadas de "espectro":

| Grandeza | Unidade | Quando |
|---|---|---|
| Magnitude da DFT | adimensional | quase nunca útil crua |
| **Espectro de amplitude** | mesma do sinal (V) | ler amplitude de senoide: `2·abs(X)/sum(w)` |
| **DEP / PSD** | V²/Hz | ruído e sinais aleatórios. `signal.welch(..., scaling='density')` |
| **Espectro de potência** | V² | tons discretos. `scaling='spectrum'` |

**A regra que decide:** se o sinal for **tonal** (energia concentrada em raias), use
espectro de amplitude/potência — o valor não deve depender da resolução. Se for
**ruído** (energia distribuída), use DEP — aí o valor por hertz é que é invariante.

Sintoma de erro: você muda `nperseg` e o "nível do ruído" muda. Isso significa que
você está lendo potência onde deveria ler densidade.

**ENBW** (largura de banda equivalente de ruído) é o fator que converte um no outro:
`ENBW = N·Σw² / (Σw)²`, em bins. Vale 1,00 para retangular, 1,50 para Hann, 1,36
para Hamming. A SciPy já cuida disso no `welch`; você precisa saber quando fizer a
conta à mão.

---

## 7 · Além de Fourier: métodos paramétricos

Quando você **sabe** algo sobre o sinal, dá para fazer melhor que a resolução fs/N.

| Método | Hipótese | Ganho | Risco |
|---|---|---|---|
| **AR / Yule-Walker / Burg** | o sinal é saída de um filtro todo-polos | espectro liso com poucos dados | ordem errada inventa picos |
| **MUSIC** | soma de K senoides + ruído branco | resolução muito acima de fs/N | precisa saber K |
| **ESPRIT** | idem | idem, sem busca em grade | idem |
| **Multitaper (DPSS)** | nenhuma além de estacionaridade | menor variância sem perder tanta resolução | mais caro |
| **Compressive sensing** | espectro esparso | menos amostras que Nyquist | esparsidade tem de ser real |

**Aviso profissional, e é sério:** métodos de "superresolução" produzem gráficos
lindos com picos finíssimos. Se a hipótese estiver errada — se houver 4 senoides e
você pediu 2, ou se o sinal não for realmente uma soma de senoides — o resultado é
**confiantemente falso**. Fourier é honesto: ele borra, mas não inventa. Métodos
paramétricos não borram e **podem** inventar.

Minha recomendação: use Fourier como referência **sempre**, e paramétrico só quando
puder justificar a hipótese e validar contra a referência.

---

## Os cinco porquês: por que não existe janela perfeita?

1. **Por que toda janela tem lóbulos laterais?** Porque o espectro dela é a
   transformada de uma função de suporte finito, e suporte finito no tempo implica
   suporte infinito na frequência.
2. **Por que suporte finito implica espectro infinito?** Porque uma função não pode
   ser simultaneamente de banda limitada e de duração limitada — é um teorema, não
   uma limitação prática.
3. **Por que esse teorema vale?** Porque uma função de banda limitada é analítica
   (é a integral de uma exponencial), e uma função analítica que é zero num
   intervalo é zero em toda parte. Zero num intervalo + não nula ⟹ contradição.
4. **Então não dá para melhorar os dois eixos?** Não. Só dá para redistribuir: você
   escolhe se a energia indesejada fica perto (lóbulo largo) ou longe (cauda pesada).
   É o produto Δt·Δf ≥ constante ([`14 §5`](14-fourier.md)).
5. **E a Kaiser, que "otimiza"?** Ela resolve o problema exato: maximizar a energia
   concentrada no lóbulo principal para uma dada largura. A solução são as
   **sequências esferoidais achatadas** (DPSS), e a Kaiser é uma aproximação delas.
   **Parada legítima: é um problema de otimização com solução conhecida e ótima** —
   melhor que isso, matematicamente, não existe.

---

## Autoteste

1. Por que você nunca mede o espectro do sinal, mas outra coisa?
2. Um tom 70 dB abaixo de outro, 8 bins ao lado: que erro a janela retangular comete?
3. Por que a Hamming saiu pior que a Hann nesse teste, apesar do lóbulo lateral menor?
4. Sua medição de amplitude varia 3,9 dB de um tom para outro. Diagnóstico e correção?
5. Qual janela para medir amplitude com exatidão, e por quê ela existe?
6. Por que o periodograma não é um estimador consistente?
7. Como validar corretamente a variância de um estimador espectral?
8. Você dobrou `nperseg` e o "nível de ruído" mudou. O que está errado?
9. Quando um método de superresolução é perigoso, e como se protege?
