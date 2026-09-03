# 14 · Fourier — série, transformada e as propriedades que fazem o trabalho

`Nível: intermediário` · `Atualizado em: 14/08/2026`

O [`10 §8`](10-fundamentos.md) apresentou os quatro pares de transformada. Aqui
vemos os três "de papel" (série, FT, DTFT); o computável (DFT/FFT) tem capítulo
próprio, [`16`](16-dft-e-fft.md).

O que realmente se usa deste capítulo, no dia a dia, é a **tabela de propriedades**
da §4. Ela resolve mais problemas do que qualquer cálculo direto.

---

## 1 · Série de Fourier — sinal periódico contínuo

Todo sinal periódico de período T₀ (frequência f₀ = 1/T₀) se escreve como:

```
x(t) = Σ_{k=−∞}^{∞} c_k · e^{j2πkf₀t}          (forma exponencial, a útil)

c_k = (1/T₀) ∫_{T₀} x(t)·e^{−j2πkf₀t} dt
```

Ou, para sinal real, na forma trigonométrica:

```
x(t) = a₀ + Σ_{k=1}^{∞} [a_k·cos(2πkf₀t) + b_k·sen(2πkf₀t)]
```

**Leia c_k como "quanto do sinal se parece com a k-ésima harmônica"** — é
literalmente um produto interno (projeção) contra e^{j2πkf₀t}. É a §6 de
[`12`](12-matematica-do-zero.md) em ação.

**O espectro é discreto**: só existem componentes em múltiplos de f₀. Um Lá de
110 Hz numa corda de violão tem energia em 110, 220, 330, ... e em nada mais. É
por isso que "harmônico" e "múltiplo inteiro" viraram sinônimos em música.

### Exemplo canônico: a onda quadrada

Uma onda quadrada de amplitude ±1 tem apenas harmônicos **ímpares**, com amplitude
4/(πk):

```python
import numpy as np
from scipy import signal

fs = 10000; t = np.arange(fs)/fs; f0 = 50
x = signal.square(2*np.pi*f0*t)
X = np.abs(np.fft.rfft(x*np.hanning(len(t))))/(len(t)/4)
f = np.fft.rfftfreq(len(t), 1/fs)
for k in [1, 2, 3, 5, 7, 9]:
    i = np.argmin(np.abs(f - k*f0))
    teoria = 4/(np.pi*k) if k % 2 else 0
    print(f"  harmônico {k}: medido {X[i]:.4f}   teoria {teoria:.4f}")
```

Saída real:

```
  harmônico 1: medido 1.2731   teoria 1.2732
  harmônico 2: medido 0.0040   teoria 0.0000
  harmônico 3: medido 0.4243   teoria 0.4244
  harmônico 5: medido 0.2545   teoria 0.2546
  harmônico 7: medido 0.1817   teoria 0.1819
  harmônico 9: medido 0.1412   teoria 0.1415
```

Quatro casas decimais de acordo com a teoria. Os harmônicos pares dão 0,004 (o
vazamento residual da janela), ou seja, **zero**.

**Por que só ímpares?** Porque a onda quadrada tem **simetria de meia onda**:
x(t + T/2) = −x(t). Qualquer sinal com essa simetria só tem harmônicos ímpares. Não
é coincidência da quadrada — vale para a triangular também, e é por isso que
distorção simétrica (um amplificador push-pull bem casado, ou o clipping simétrico
de um pedal de guitarra) gera harmônicos ímpares, que soam "ásperos", enquanto
distorção assimétrica (válvula em classe A) gera pares, que soam "quentes". A
diferença de timbre entre válvula e transistor tem, em parte, esta explicação
matemática.

**E a taxa de decaimento diz a suavidade.** Quadrada: 1/k (descontinuidade no
valor). Triangular: 1/k² (descontinuidade só na derivada). Regra geral: se a
p-ésima derivada é a primeira descontínua, os coeficientes decaem como 1/k^{p+1}.
Olhando um espectro, você deduz a suavidade do sinal sem olhar a forma de onda.

---

## 2 · Transformada de Fourier — sinal contínuo aperiódico

Deixe T₀ → ∞. As raias se juntam, e o somatório vira integral:

```
X(f) = ∫_{−∞}^{∞} x(t)·e^{−j2πft} dt              (análise)
x(t) = ∫_{−∞}^{∞} X(f)·e^{+j2πft} df              (síntese)
```

**Espectro contínuo.** Um sinal que não se repete tem energia em todas as
frequências, não em raias.

> **Cuidado com convenções:** existem três formas de escrever, com f ou ω, e com o
> fator 1/2π em lugares diferentes. Livros diferentes dão fórmulas "diferentes"
> para a mesma coisa. A versão em **f (Hz)** acima é a mais limpa porque não tem
> fator nenhum na frente. Ao comparar duas fontes, confira a convenção antes de
> concluir que uma está errada.

### Pares que vale conhecer de cor

| x(t) | X(f) | Comentário |
|---|---|---|
| δ(t) | 1 | impulso tem todas as frequências igualmente |
| 1 | δ(f) | constante só tem DC |
| cos(2πf₀t) | ½[δ(f−f₀)+δ(f+f₀)] | duas raias, positiva e negativa |
| retângulo de largura T | T·sinc(fT) | 🔑 **o par mais importante** |
| sinc(t/T) | retângulo de largura 1/T | o mesmo par, ao contrário |
| gaussiana | gaussiana | a única forma que é sua própria transformada |
| pente de impulsos (período T) | pente de impulsos (período 1/T) | 🔑 a chave da amostragem |
| e^{−at}u(t), a>0 | 1/(a + j2πf) | decaimento exponencial ⟷ filtro de 1 polo |

**O par retângulo ⟷ sinc é o que mais aparece na prática**, porque cortar um sinal
num bloco *é* multiplicar por um retângulo. Verificação:

```python
N = 1024; x = np.zeros(N); x[:32] = 1.0        # pulso de 32 amostras
X = np.abs(np.fft.rfft(x))
print([k for k in range(1, 200) if X[k] < 0.05][:5])
```

Saída real: `[32, 64, 96, 128, 160]` — nulos exatamente em múltiplos de N/L =
1024/32 = 32. **Pulso mais estreito ⟹ lóbulos mais largos.** Inversamente
proporcional, sempre.

---

## 3 · DTFT — sinal discreto, espectro contínuo e periódico

```
X(e^{jΩ}) = Σ_{n=−∞}^{∞} x[n]·e^{−jΩn}
x[n] = (1/2π) ∫_{−π}^{π} X(e^{jΩ})·e^{jΩn} dΩ
```

Duas diferenças cruciais em relação ao caso contínuo:

1. **X é periódica em Ω com período 2π.** Consequência direta de e^{−j(Ω+2π)n} =
   e^{−jΩn} (n é inteiro!). É a assinatura matemática do aliasing.
2. **A integral de síntese vai só de −π a π** — não há mais nada além disso, porque
   se repete.

A DTFT é o objeto teórico correto para sinal digital. Ela não é computável (a soma
é infinita e Ω é contínuo), e a DFT é sua versão amostrada e finita — daí boa parte
dos "artefatos" do capítulo [`16`](16-dft-e-fft.md).

---

## 4 · 🔑 Propriedades — a tabela que resolve problemas

Estas valem, com pequenas adaptações, para todas as versões de Fourier. **Decore o
sentido, não a fórmula.**

| Propriedade | Tempo | Frequência | Uso prático |
|---|---|---|---|
| **Linearidade** | a·x + b·y | a·X + b·Y | analisar componentes separadamente |
| **Deslocamento no tempo** | x(t − t₀) | X(f)·e^{−j2πft₀} | **atrasar só mexe na fase**, não na magnitude |
| **Deslocamento em freq.** | x(t)·e^{j2πf₀t} | X(f − f₀) | **modulação**: multiplicar desloca o espectro |
| **Escala** | x(at) | (1/\|a\|)·X(f/a) | 🔑 comprimir no tempo = esticar na frequência |
| **🔑 Convolução** | x * h | X · H | filtrar = multiplicar espectros |
| **🔑 Multiplicação** | x · w | X * W | **janelar = borrar o espectro** ⇒ vazamento |
| **Conjugação** | x*(t) | X*(−f) | sinal real ⟹ espectro hermitiano |
| **Derivada** | dx/dt | j2πf·X(f) | derivar amplifica agudos |
| **Integral** | ∫x | X(f)/(j2πf) | integrar amplifica graves |
| **Parseval** | ∫\|x\|²dt | ∫\|X\|²df | energia se conserva |
| **Dualidade** | se x ⟷ X | então X(t) ⟷ x(−f) | cada par vale nos dois sentidos, de graça |

### As duas que explicam quase tudo

**Convolução ⟷ multiplicação.** Verificação:

```python
rng = np.random.default_rng(0)
x, h = rng.standard_normal(64), rng.standard_normal(16)
direto = np.convolve(x, h)
N = 64 + 16 - 1
viafft = np.fft.irfft(np.fft.rfft(x, N)*np.fft.rfft(h, N), N)
print(f"erro máximo: {np.max(np.abs(direto - viafft)):.2e}")
```

Saída real: `erro máximo: 5.33e-15`. Idênticos até a precisão da máquina.
O `N = 64+16-1` é obrigatório: com N menor, a FFT faz convolução **circular** e a
cauda "dá a volta" e contamina o começo. Esse é o erro clássico de quem implementa
convolução rápida à mão.

**Multiplicação ⟷ convolução.** É a propriedade que explica:

- **Vazamento espectral:** cortar o sinal num bloco = multiplicar por um retângulo
  = **convoluir** o espectro verdadeiro com uma sinc. A raia infinitamente fina
  vira o formato da sinc. ([`20`](20-analise-espectral-e-janelas.md))
- **Amostragem:** amostrar = multiplicar por um pente de impulsos = convoluir o
  espectro com um pente ⟹ **cópias repetidas do espectro** a cada fs. Se as cópias
  se sobrepõem, é aliasing. ([`15`](15-amostragem-e-quantizacao.md))
- **Modulação AM:** multiplicar por cos(2πf_c t) = convoluir com duas raias =
  **deslocar** o espectro para ±f_c. Rádio AM, inteiro, numa linha de tabela.

**Escala.** Comprimir no tempo por 2 estica o espectro por 2 (e reduz a amplitude
pela metade). É o motivo físico de um som acelerado ficar agudo — e o motivo de um
pulso curto exigir banda larga. Um radar que quer resolver 15 cm precisa de um
pulso de 1 ns, que ocupa ~1 GHz de banda. **Resolução espacial custa espectro.**
Não há como contornar; só há como disfarçar (é o que a compressão de pulso por
chirp faz — mesma banda, mais energia).

---

## 5 · O princípio da incerteza — o preço que nunca muda

```
Δt · Δf ≥ 1/(4π)          (com Δ = desvio padrão da distribuição de energia)
```

É **o mesmo teorema** do princípio de Heisenberg da mecânica quântica. Lá, posição
e momento; aqui, tempo e frequência. A matemática é idêntica porque em ambos os
casos as duas grandezas são pares de Fourier.

**Consequências que você encontra toda semana:**

| Você quer | Você paga |
|---|---|
| saber *quando* algo aconteceu (janela curta) | resolução de frequência ruim |
| saber *em que frequência* (janela longa) | não sabe quando |
| filtro com corte abrupto | resposta ao impulso longa ⟹ atraso e ringing |
| resposta rápida (atraso curto) | corte suave, seletividade ruim |
| pulso de radar curto (boa resolução em distância) | banda larga, mais ruído captado |

**A gaussiana é o único formato que atinge a igualdade** — a incerteza mínima. É
por isso que a janela gaussiana aparece na transformada de Gabor e nas wavelets de
Morlet ([`24`](24-tempo-frequencia-e-wavelets.md)): entre todas as janelas, ela é a
que menos borra os dois eixos ao mesmo tempo.

**Isso é uma lei matemática**, não uma limitação de ferramenta. Nenhum algoritmo,
nenhum hardware, nenhuma rede neural muda esse limite. O que técnicas modernas
(reatribuição, superresolução, métodos paramétricos) fazem é **usar informação
extra** — a hipótese de que o sinal é uma soma de poucas senoides, por exemplo —
para contornar o problema sob essa hipótese. Se a hipótese for falsa, o resultado é
lixo com aparência de precisão. Desconfie sempre de "resolução além de Fourier"
sem que a hipótese esteja explícita.

---

## Os cinco porquês: por que vazamento espectral existe?

1. **Por que uma senoide pura não dá uma raia única na FFT?** Porque você não
   analisou uma senoide pura: analisou um *pedaço* dela.
2. **Por que o pedaço muda o resultado?** Porque pegar um pedaço é multiplicar por
   um retângulo, e multiplicar no tempo é **convoluir** na frequência (tabela §4).
3. **Por que a convolução espalha?** Porque o espectro do retângulo é uma sinc,
   que tem lóbulos laterais decaindo devagar (só 1/f). A raia é "carimbada" com
   esse formato.
4. **Por que a sinc decai só com 1/f?** Porque o retângulo tem descontinuidades
   abruptas nas bordas, e descontinuidade no tempo ⟹ cauda pesada na frequência
   (a regra do decaimento da §1, ao contrário).
5. **Por que então não usar uma janela sem descontinuidade?** É exatamente o que se
   faz — Hann, Hamming, Blackman. E aí a cauda cai muito mais rápido, ao preço de
   um lóbulo principal mais largo. **Parada legítima: um trade-off matemático
   inescapável** — a energia tem de ir para algum lugar; você escolhe se ela fica
   concentrada perto (lóbulo largo) ou espalhada longe (cauda pesada).

---

## Autoteste

1. Por que a onda quadrada só tem harmônicos ímpares?
2. Um espectro cujos coeficientes decaem como 1/k² indica o quê sobre o sinal?
3. Qual é a diferença entre o espectro de um sinal periódico e o de um aperiódico?
4. Por que a DTFT é periódica em 2π, e o que isso significa fisicamente?
5. Enuncie as duas propriedades que explicam vazamento, aliasing e modulação AM.
6. Ao convoluir via FFT, por que N deve ser ≥ len(x)+len(h)−1?
7. Um radar quer resolver 15 cm. Que banda ele precisa, e por quê?
8. Por que a gaussiana é especial no princípio da incerteza?
9. Alguém afirma ter "resolução além do limite de Fourier". Que pergunta você faz?
