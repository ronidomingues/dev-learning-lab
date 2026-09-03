# 24 · Tempo-frequência e wavelets — quando o espectro muda

`Nível: avançado` · `Medições feitas em: 19/08/2026`

Fourier pressupõe que o espectro **não muda**. Fala, música, sinais biomédicos,
sísmica, radar — nada disso é estacionário. Este capítulo é sobre analisar sinais
cujo conteúdo espectral varia com o tempo, e sobre o preço inevitável disso.

---

## 1 · O problema com Fourier puro

A transformada de Fourier de um sinal inteiro diz **quais frequências existem**,
mas não **quando**.

Dois sinais completamente diferentes — um dó seguido de um sol, e um sol seguido
de um dó — têm **exatamente o mesmo espectro de magnitude**. A diferença está toda
na fase, num arranjo que ninguém consegue ler.

A saída é analisar em pedaços. E aí bate a lei do capítulo [`14 §5`](14-fourier.md).

---

## 2 · STFT — o compromisso, medido

Corte o sinal em janelas, faça a FFT de cada uma. Simples, e é 90 % do que se usa.

**O experimento decisivo:** um sinal com dois tons próximos (1000 e 1050 Hz, para
exigir resolução em frequência) e um estalo de 10 ms (para exigir resolução em
tempo). Nenhuma janela consegue as duas coisas.

```python
import numpy as np
from scipy import signal
fs = 8000
t = np.arange(2*fs)/fs
x = np.sin(2*np.pi*1000*t) + np.sin(2*np.pi*1050*t)
x[fs:fs+80] += 5.0                                  # estalo em t = 1 s

for L in [128, 512, 2048]:
    w = signal.get_window('hann', L)
    S = signal.ShortTimeFFT(w, hop=L//4, fs=fs, scale_to='magnitude')
    M = np.abs(S.stft(x))
    ...
```

Saída real:

```
  janela   128 (  16.0 ms): resolução   62.5 Hz -> separa 1000/1050? não | estalo espalhado por   16.0 ms
  janela   512 (  64.0 ms): resolução   15.6 Hz -> separa 1000/1050? SIM | estalo espalhado por   48.0 ms
  janela  2048 ( 256.0 ms): resolução    3.9 Hz -> separa 1000/1050? SIM | estalo espalhado por  128.0 ms
```

**A troca, em números:**

- Janela de 16 ms localiza o estalo com precisão de 16 ms, mas **não separa** dois
  tons a 50 Hz de distância.
- Janela de 256 ms separa tons a 3,9 Hz, mas **borra o estalo por 128 ms** — oito
  vezes mais do que ele dura.

Não existe janela que faça as duas. **Não é limitação da SciPy, é teorema**
(Δt·Δf ≥ 1/4π). Qualquer método que prometa contornar isso está usando informação
adicional — e você precisa saber qual.

### Escolher a janela na prática

| Sinal | Janela típica | Por quê |
|---|---|---|
| Fala | 20–30 ms | dentro disso a fala é quase estacionária (fonema) |
| Música (análise harmônica) | 50–100 ms | precisa resolver semitons graves |
| Transiente / percussão | 5–10 ms | localizar o ataque |
| Vibração de máquina | 1–10 s | resolver raias muito próximas |
| EEG | 1–4 s | as bandas de interesse são estreitas |

**Sobreposição:** 50 % para Hann é o mínimo (condição COLA); 75 % suaviza a
imagem. Sem sobreposição suficiente, energia se perde entre quadros.

---

## 3 · A ideia das wavelets: resolução proporcional

A STFT usa **a mesma janela** para todas as frequências. Isso é estranho: para
analisar 50 Hz você precisa de janela longa; para 5 kHz, uma janela longa é
desperdício e borra os transientes.

**Wavelets usam janela proporcional à escala:** curta em altas frequências, longa
em baixas. É a **análise de Q constante** — largura de banda proporcional à
frequência central.

```
   STFT: resolução uniforme          Wavelet: resolução proporcional
   f                                  f
   │ ┌──┬──┬──┬──┬──┐                 │ ┌┬┬┬┬┬┬┬┬┐   ← agudos: bom no tempo
   │ ├──┼──┼──┼──┼──┤                 │ ├──┼──┼──┤
   │ ├──┼──┼──┼──┼──┤                 │ ├─────┼───┤
   │ └──┴──┴──┴──┴──┘                 │ └─────────┘  ← graves: bom na frequência
   └──────────────── t                └──────────────── t
```

**Por que isso é natural:** é assim que o ouvido funciona (a cóclea é um banco de
filtros de Q aproximadamente constante), e é assim que a música é organizada (uma
oitava é sempre um fator 2, não um número fixo de hertz).

⚠️ **Wavelets não violam a incerteza.** Elas **redistribuem** o compromisso ao
longo do eixo de frequência, em vez de aplicá-lo uniformemente. O produto Δt·Δf
continua limitado em cada célula.

---

## 4 · CWT e DWT

### CWT (contínua) — para analisar e ver

Correlaciona o sinal com versões escaladas e deslocadas de uma wavelet-mãe:

```
W(a, b) = (1/√a)·∫ x(t)·ψ*((t−b)/a) dt
```

- **a** = escala (inverso da frequência), **b** = deslocamento no tempo.
- Redundante (mais coeficientes que amostras), boa para **visualizar**.

| Wavelet-mãe | Uso |
|---|---|
| **Morlet** | análise tempo-frequência geral; é uma gaussiana modulada — incerteza mínima |
| Mexican hat (Ricker) | detecção de picos, sísmica |
| Gaussiana de ordem n | detecção de descontinuidades |

⚠️ **`scipy.signal.cwt`, `morlet` e `ricker` foram REMOVIDAS na SciPy 1.15.**
Use **PyWavelets** (`pip install PyWavelets`, depois `pywt.cwt`). Código antigo
que importa esses nomes quebra — está registrado em
[`05-manual-de-uso.md`](05-manual-de-uso.md).

### DWT (discreta) — para comprimir e processar

Implementada como um **banco de filtros em cascata**
([`21 §4`](21-multitaxa-e-bancos-de-filtros.md)):

```
  x ──┬─►[passa-alta]─►[↓2]──► detalhe nível 1
      └─►[passa-baixa]─►[↓2]──┬─►[passa-alta]─►[↓2]──► detalhe nível 2
                              └─►[passa-baixa]─►[↓2]──► aproximação
```

Cada nível divide a banda restante ao meio. Com N amostras entram, **N
coeficientes saem** (não redundante) e a reconstrução é **perfeita**.

| Família | Propriedade |
|---|---|
| **Haar** | a mais simples: média e diferença. Descontínua |
| **Daubechies (dbN)** | suporte compacto, N momentos nulos, ortogonal |
| **Symlets, Coiflets** | quase simétricas — melhor fase |
| **Biortogonais (bior)** | simetria exata; usadas no **JPEG2000** |

**"Momentos nulos" traduzido:** uma wavelet com N momentos nulos dá coeficiente
**zero** para qualquer trecho do sinal que seja um polinômio de grau < N. É por
isso que a DWT comprime bem: sinais reais são localmente suaves, os coeficientes
de detalhe ficam quase todos perto de zero, e zeros comprimem.

---

## 5 · Aplicações onde wavelets ganham

| Aplicação | Por que wavelet e não Fourier |
|---|---|
| **JPEG2000** | sem artefato de bloco (o JPEG usa DCT em blocos 8×8) |
| **Remoção de ruído por limiar** | limiarizar coeficientes de detalhe preserva bordas; passa-baixa as borra |
| **Detecção de descontinuidade** | wavelet responde localmente; Fourier espalha por todo o espectro |
| **Compressão de impressão digital** | o FBI adota WSQ, baseado em wavelets, desde os anos 1990 |
| **Sísmica, ECG** | eventos transientes em fundo colorido |
| **Análise multiescala** | quando o fenômeno tem estrutura em várias escalas |

### E onde wavelets **não** ganham

Vale ser franco, porque houve muito exagero nos anos 1990:

- **Análise harmônica de sinais quase estacionários**: Fourier é melhor e mais
  interpretável. Uma raia é uma raia.
- **Codecs de áudio modernos**: usam MDCT, não wavelets. A MDCT ganhou a disputa.
- **Interpretação física**: "energia em 440 Hz" é claro; "coeficiente de detalhe
  no nível 3 da db4" não é.
- A escolha da wavelet-mãe é **arbitrária** e muda o resultado. Fourier não tem
  esse grau de liberdade — o que é uma desvantagem em flexibilidade e uma
  vantagem em objetividade.

**Minha opinião profissional:** wavelets são excelentes para **compressão,
remoção de ruído preservando bordas e detecção de transientes**. Para análise
espectral de sinal estacionário, use Fourier. A onda de entusiasmo dos anos 1990
tratou wavelets como substituto universal de Fourier; elas não são, e a poeira
assentou nesse lugar.

---

## 6 · Outras representações tempo-frequência

| Método | Ideia | Vantagem | Custo |
|---|---|---|---|
| **STFT / espectrograma** | janela fixa | simples, interpretável | resolução uniforme |
| **Wavelet (CWT)** | janela proporcional | multiescala | escolha da mãe é arbitrária |
| **Wigner-Ville** | distribuição quadrática | resolução ótima em tempo **e** frequência | **termos cruzados** espúrios |
| **Espectrograma reatribuído** | move a energia para o centro de massa local | imagem muito mais nítida | não inverte |
| **Transformada S** | híbrida STFT/wavelet | fase absoluta preservada | custo |
| **Modo empírico (EMD/HHT)** | decompõe em modos oscilatórios | adaptativa, não linear | sem base teórica sólida |
| **Sincrossqueeze** | reatribui só em frequência | nítida **e** invertível | hipóteses sobre o sinal |

**Sobre Wigner-Ville, porque é a armadilha clássica:** ela realmente atinge
resolução superior ao limite da STFT. E produz, para qualquer sinal com dois
componentes, um **termo cruzado** entre eles — energia aparente onde não há
sinal nenhum, exatamente no meio do caminho. Com três componentes, três termos
cruzados. As versões suavizadas (pseudo-Wigner) reduzem os termos cruzados
**perdendo** a resolução que era a razão de usá-la. É o exemplo perfeito de
"não existe almoço grátis" na análise tempo-frequência.

---

## Os cinco porquês: por que existe o limite tempo × frequência?

1. **Por que não posso ter resolução perfeita nos dois eixos?** Porque tempo e
   frequência são pares de Fourier, e o produto das dispersões é limitado:
   Δt·Δf ≥ 1/(4π).
2. **Por que esse produto é limitado?** Porque estreitar uma função no tempo
   necessariamente alarga sua transformada — é a propriedade de escala
   ([`14 §4`](14-fourier.md)): x(at) ⟷ (1/|a|)X(f/a).
3. **Por que a propriedade de escala vale?** Porque ela decorre diretamente de uma
   mudança de variável na integral da transformada. É álgebra, não física.
4. **Então por que se fala em "princípio de Heisenberg"?** Porque é literalmente o
   mesmo teorema. Em mecânica quântica, posição e momento são pares de Fourier, e
   a desigualdade é a mesma. A física acrescenta ħ; a matemática é idêntica.
5. **Alguma função atinge a igualdade?** Sim, e só uma: a **gaussiana**. É por isso
   que a wavelet de Morlet é uma gaussiana modulada e que a janela gaussiana
   aparece na transformada de Gabor. **Parada legítima: é um teorema de análise
   funcional** — a gaussiana é a única minimizadora do produto, e isso está
   provado desde os anos 1920.

---

## Autoteste

1. Por que dois sinais com as mesmas notas em ordem diferente têm o mesmo espectro?
2. Com os números medidos: qual janela separa 1000 de 1050 Hz, e o que ela custa?
3. O que significa "Q constante" e por que é natural para áudio?
4. Wavelets violam o princípio da incerteza? Explique com precisão.
5. O que são momentos nulos e por que eles fazem a DWT comprimir bem?
6. Cite duas aplicações em que wavelets ganham e duas em que perdem.
7. Que funções da SciPy foram removidas na 1.15 e o que usar no lugar?
8. O que são termos cruzados na distribuição de Wigner-Ville?
9. Qual é a única função que atinge a igualdade na desigualdade da incerteza?
