# Glossário — todos os termos técnicos do curso

`Atualizado em: 19/08/2026`

Termos em **inglês** aparecem entre parênteses quando é assim que o campo os usa.
O número entre colchetes indica o capítulo onde o termo é tratado a fundo.

---

## A

**Aliasing** (serrilhamento, dobramento) — fenômeno em que uma frequência acima de
Nyquist aparece, após a amostragem, como uma frequência mais baixa que não existe
no sinal original. **Não gera erro**: gera um número errado e convincente.
Irreversível. [15]

**Amostragem** (*sampling*) — medir o valor de um sinal contínuo em instantes
discretos. [15]

**Analítico (sinal)** — sinal complexo x + j·x̂ construído pela transformada de
Hilbert, cujo módulo é a envoltória e a derivada da fase é a frequência
instantânea. [06, 25]

**Anti-aliasing** — filtro **analógico** aplicado antes do conversor A/D para
remover frequências acima de Nyquist. Não pode ser feito em digital. [15]

**AR (autorregressivo)** — modelo em que a amostra atual é combinação linear das
anteriores mais ruído. Espectro todo-polos. [22]

**Atraso de grupo** (*group delay*) — −d∠H/dΩ. O atraso da **envoltória** do sinal;
é o que se percebe. Constante ⟺ fase linear. [13]

**Atraso de fase** — −∠H/Ω. O atraso da portadora. Diferente do atraso de grupo. [13]

**Autocorrelação** — R[k] = E{x[n]·x[n+k]}. Mede quanto o sinal se parece consigo
mesmo atrasado de k. Sua transformada de Fourier é a DEP. [22]

**Autovetor / autovalor** — em DSP: as exponenciais complexas são os autovetores de
todo sistema LTI, e H(e^{jΩ}) são os autovalores. É **a** razão de Fourier
funcionar. [10, 12]

---

## B

**Banco de filtros** (*filter bank*) — conjunto de filtros que divide um sinal em
sub-bandas. Base de codecs, wavelets e equalizadores. [21]

**Bandpass sampling** (subamostragem intencional) — amostrar um sinal de faixa
[f₁,f₂] com fs > 2·(f₂−f₁), usando o aliasing de propósito. [15]

**BIBO** (*Bounded Input, Bounded Output*) — critério de estabilidade: entrada
limitada ⟹ saída limitada. Equivale a Σ|h[n]| < ∞. [13]

**Bin** — cada uma das N raias em que a DFT divide o espectro. Largura = fs/N. [16]

**Biquad** — seção de filtro IIR de 2ª ordem. Unidade atômica do áudio digital:
5 multiplicações, 4 estados. [19]

**Borboleta** (*butterfly*) — operação elementar da FFT: E ± W^k·O. [16]

---

## C

**Causal** — sistema cuja saída depende só do presente e do passado. Obrigatório em
tempo real. [13]

**Cent** — 1/100 de semitom; 1200·log₂(f₂/f₁). O ouvido treinado detecta ~5. [12]

**CIC** (*Cascaded Integrator-Comb*) — filtro de decimação **sem multiplicadores**,
feito de integradores e diferenciadores. Depende de transbordo em complemento de
dois. [21, 28]

**Cepstro** — transformada do log do espectro. Separa fonte de filtro na fala. [25]

**Coerente (integração)** — somar mantendo a fase alinhada: sinal cresce com N.
Contrasta com **não coerente** (soma de módulos), que cresce com √N. [08-espacial]

**COLA** (*constant overlap-add*) — condição sobre janela e salto que garante que a
soma dos quadros seja constante. 50 % para Hann. [20]

**Compressive sensing** (amostragem compressiva) — reconstruir sinais **esparsos**
com menos amostras que Nyquist exigiria. Não viola Nyquist: muda a hipótese. [11, 60]

**Convolução** — y[n] = Σ x[k]·h[n−k]. A operação que todo sistema LTI realiza.
Consequência obrigatória de linearidade + invariância. [10]

**Convolução circular** — o que a FFT faz por padrão; a cauda "dá a volta". Fonte
de artefato, e explorada de propósito no OFDM. [16, 26]

**Correlação** — parecida com convolução, **sem** inverter o segundo sinal. Usada
para procurar padrão. Não é comutativa. [10]

**CRB** (*Cramér-Rao bound*) — limite inferior para a variância de um estimador não
enviesado. Diz o melhor possível antes de escrever código. [60]

---

## D

**dBFS** — decibel relativo ao fundo de escala digital. 0 dBFS é o máximo; tudo é
negativo. [05]

**DDSP** (DSP diferenciável) — blocos clássicos (osciladores, filtros) embutidos
numa rede neural como componentes treináveis. [29, 65]

**Decibel (dB)** — 20·log₁₀ para amplitude, 10·log₁₀ para potência. [12]

**Decimação** — reduzir a taxa por M. Exige **filtrar antes**. [21]

**Dedispersão** — desfazer o atraso dependente da frequência causado pelo plasma
interestelar, canal a canal. [08-espacial]

**DEP / PSD** (densidade espectral de potência) — distribuição de potência por
hertz. Para sinal aleatório, é a transformada da autocorrelação. [22]

**DFT** (transformada discreta de Fourier) — a transformada computável: N amostras
entram, N números complexos saem. [16]

**Dispersão (DM)** — *dispersion measure*: coluna de elétrons livres entre a fonte
e o observador, em pc·cm⁻³. Medida pelo atraso ∝ 1/f². [08-espacial]

**Dither** — ruído adicionado **de propósito** antes de quantizar, para
descorrelacionar o erro e recuperar sinais abaixo de 1 LSB. [15]

**Droop** — atenuação progressiva causada pelo sample-and-hold (resposta sinc) ou
por um CIC. Corrigida com filtro 1/sinc. [15, 21]

**DTFT** — transformada de Fourier de tempo discreto. Espectro **contínuo e
periódico** em 2π. Objeto teórico, não computável. [14]

**DWT** — transformada wavelet discreta, implementada como banco de filtros em
cascata. Não redundante, reconstrução perfeita. [24]

---

## E

**ENBW** (largura de banda equivalente de ruído) — largura de um filtro retangular
ideal que deixaria passar a mesma potência de ruído. **Diferente** da largura a
−3 dB. [20, 22]

**ENOB** (bits efetivos) — resolução real de um conversor, sempre menor que o
número nominal de bits. [15]

**Equiripple** — resposta cujo ripple tem amplitude constante. Resultado do
Parks-McClellan (critério minimax). [18]

**Ergodicidade** — hipótese de que média temporal = média estatística. Permite
medir tudo de uma só gravação. **É hipótese, não fato.** [22]

**Espectrograma** — |STFT|², mostrando como o espectro varia no tempo. [20, 24]

**Estacionário (WSS)** — processo cuja média e autocorrelação não mudam com o
tempo. Fala **não é**; por isso se analisa em janelas curtas. [22]

---

## F

**Fase linear** — ∠H = −αΩ. Atraso constante para todas as frequências ⟹ nenhuma
deformação de forma de onda. Só FIR simétrico consegue. [13, 18]

**Fase mínima** — sistema com todos os zeros dentro do círculo unitário. Único tipo
que tem **inverso causal e estável**. [17]

**Festonamento** (*scalloping*) — perda de amplitude quando a frequência cai entre
dois bins. Até −3,9 dB com janela retangular. [20]

**FFT** — **algoritmo** rápido para calcular a DFT, em O(N log N). Não é uma
transformada diferente. [16]

**FIR** (*Finite Impulse Response*) — filtro sem realimentação. Sempre estável,
pode ter fase linear, exige muitos coeficientes. [18]

**Filtro casado** (*matched filter*) — correlacionar com uma cópia do sinal
procurado. Detector **ótimo** em ruído branco gaussiano. [06, 18]

**filtfilt** — filtragem para frente e para trás: fase zero, atenuação dobrada,
**não causal**. Proibido em tempo real. [19]

**Folding (de época)** — somar muitas repetições de um sinal periódico alinhadas
pela fase. Ganho de SNR √N. [08-espacial]

**Formante** — ressonância do trato vocal. Carrega o conteúdo fonético. [25]

**Frame** — família redundante que ainda permite reconstrução estável. Generaliza
base. [60]

---

## G

**Gibbs (fenômeno de)** — sobressinal de ~8,95 % na reconstrução de uma
descontinuidade. Não diminui com mais termos. [13]

**Goertzel** — algoritmo que calcula **um** bin da DFT em O(N), com 2 variáveis de
estado. Usado em DTMF. [06]

**Golomb (propriedades de)** — balanceamento, autocorrelação de dois níveis e
propriedade de janela das sequências-m. [08-espacial]

---

## H

**Hilbert (transformada de)** — desloca todas as frequências em −90°; constrói o
sinal analítico. [06, 25]

---

## I

**I/Q** — representação complexa (em fase / quadratura) de um sinal de rádio. [26]

**IIR** (*Infinite Impulse Response*) — filtro com realimentação. Muito eficiente,
estabilidade condicional, fase não linear. [19]

**Impulso (resposta ao)** — h[n] = resposta do sistema a δ[n]. Descreve
completamente um sistema LTI. [10]

**Interpolação** — aumentar a taxa: inserir zeros e filtrar. [21]

**ISI** (interferência entre símbolos) — símbolos vizinhos interferindo. Evitada
pelo critério de Nyquist com pulso RRC. [26]

---

## J

**Janela** (*window*) — função que suaviza as bordas de um bloco antes da FFT,
reduzindo vazamento. Hann, Hamming, Blackman-Harris, flattop, Kaiser. [20]

**Jitter** — instabilidade do instante de amostragem. Limita a SNR:
−20·log₁₀(2πf·t_j). Frequentemente o gargalo real. [15]

---

## K

**Kalman (filtro de)** — estimador ótimo recursivo para sistema linear com ruído
gaussiano e modelo de estado. [23]

---

## L

**LFSR** (*Linear Feedback Shift Register*) — registrador que gera sequências
pseudoaleatórias de máximo comprimento. [08-espacial]

**LMS** (*Least Mean Squares*) — algoritmo adaptativo de gradiente estocástico
(Widrow-Hoff, 1960). É o mesmo princípio do SGD. [23]

**LPC** (predição linear) — modela o sinal como saída de um filtro todo-polos.
Base da codificação de voz. [25]

**LSB** (bit menos significativo) — o passo de quantização. [15]

**LTI** — Linear e Invariante no Tempo. A classe para a qual existe teoria
completa. [10]

---

## M

**MDCT** — transformada de cosseno modificada, com sobreposição e reconstrução
perfeita, amostragem crítica. Núcleo dos codecs de áudio. [21, 25]

**Mel (escala)** — escala perceptual de altura: 2595·log₁₀(1+f/700). [25]

**MFCC** — coeficientes cepstrais em escala mel. Padrão clássico em fala. [25]

**Multitaxa** — processar com mais de uma taxa de amostragem no mesmo sistema. [21]

---

## N

**NLMS** — LMS normalizado pela energia da entrada. Estabilidade independente do
nível. [23]

**Nyquist (frequência de)** — fs/2. Maior frequência representável. **Taxa de
Nyquist** é 2B — os dois nomes são trocados o tempo todo. [15]

---

## O

**OFDM** — divide a banda em centenas de subportadoras ortogonais via IFFT, com
prefixo cíclico. Wi-Fi, LTE, 5G. [26]

**Ortogonalidade** — produto interno nulo. As exponenciais complexas são
ortogonais, e é por isso que o espectro é bem definido. [12]

**Overlap-add / overlap-save** — técnicas para convoluir sinais longos em blocos
via FFT, sem convolução circular. [16]

---

## P

**Parks-McClellan** — projeto ótimo de FIR por critério minimax (`remez`). [18]

**Parseval (teorema de)** — a energia é a mesma nos dois domínios. [10]

**Periodograma** — |FFT|²/N. Estimador de DEP **não consistente**: mais dados não
reduzem a variância. [20]

**Polifásico** — decomposição que evita calcular amostras que serão descartadas na
decimação. Ganho exato de M. [21]

**Polo** — raiz do denominador de H(z). Dentro do círculo unitário ⟹ estável. [17]

**Ponto fixo** — aritmética inteira com escala implícita (notação Q). [28]

---

## Q

**Q (fator)** — f₀/Δf(−3 dB). Mede a seletividade de um filtro ressonante. [19]

**Q (notação)** — Qm.n: m bits inteiros, n fracionários. [28]

**Quantização** — arredondar a amplitude para um número finito de níveis.
SNR máxima = 6,02·B + 1,76 dB. [15]

---

## R

**Radiômetro (equação do)** — ΔT_min = T_sys/√(n_pol·B·τ). Decide tempo de
telescópio. [08-espacial]

**Reconstrução perfeita** — propriedade de um banco de filtros cujos aliases se
cancelam exatamente na síntese. [21]

**RFI** (interferência de radiofrequência) — interferência terrestre. Não é
gaussiana; domina na prática e não tem modelo. [08-espacial, 22]

**Ripple** — ondulação na resposta em magnitude, na banda passante ou de
rejeição. [18, 19]

**RLS** (mínimos quadrados recursivos) — adaptativo de convergência rápida, custo
O(L²). [23]

**RMS** (valor eficaz) — √(média dos quadrados). A "energia" que o sinal entrega.
[05]

**ROC** (região de convergência) — onde a série da transformada Z converge. Parte
essencial da resposta, não detalhe. [17]

---

## S

**Sequência-m** — sequência de máximo comprimento gerada por LFSR, com
autocorrelação de dois níveis. [08-espacial]

**Sinc** — sen(πx)/(πx). Transformada do pulso retangular; núcleo da interpolação
ideal. [14]

**SOS** (*second-order sections*) — implementação de IIR como cascata de biquads.
**Requisito**, não recomendação, em precisão finita. [19, 28]

**STFT** — transformada de Fourier de tempo curto: FFT em janelas deslizantes. [20]

---

## T

**Toeplitz** — matriz constante ao longo das diagonais. A matriz de um sistema
LTI. [12, 23]

**Transformada Z** — generalização da DTFT para todo o plano complexo. A DTFT é a
Z avaliada no círculo unitário. [17]

**THD** (distorção harmônica total) — energia nos harmônicos relativa à
fundamental. [05]

---

## V

**Vazamento espectral** (*spectral leakage*) — espalhamento da energia de uma raia
por bins vizinhos, causado por cortar o sinal num bloco finito. [20]

**Volterra (série de)** — extensão da convolução para sistemas não lineares com
memória. Explode em complexidade. [60]

---

## W

**Welch (método de)** — estimador de DEP por média de periodogramas de segmentos
sobrepostos. Troca resolução por variância. [20]

**Wiener (filtro de)** — filtro linear ótimo no sentido do erro quadrático médio.
Solução: R·w = p. [23]

**Wiener-Khinchin (teorema de)** — a DEP é a transformada de Fourier da
autocorrelação. Permite falar de espectro de sinal aleatório. [22]

**Warping** — distorção não linear do eixo de frequências introduzida pela
transformada bilinear. Corrigida por pré-distorção. [17]

---

## Z

**Zero** — raiz do numerador de H(z). Zero no círculo unitário ⟹ nulo perfeito
naquela frequência. [17]

**Zero-padding** — completar o bloco com zeros antes da FFT. **Interpola** o
espectro; **não** melhora a resolução. [16]

**zi** — vetor de estado de um filtro, que deve ser propagado entre blocos no
processamento em tempo real. Esquecê-lo produz clique em cada fronteira. [19]

---

## Símbolos

| Símbolo | Significa |
|---|---|
| x(t) / x[n] | sinal contínuo / discreto |
| δ[n] / u[n] | impulso / degrau |
| h[n] | resposta ao impulso |
| ∗ | convolução (**não** multiplicação) |
| X(f), X(e^{jΩ}), X[k], X(z) | Fourier, DTFT, DFT, transformada Z |
| f / ω / Ω | Hz / rad/s / rad/amostra |
| fs, T = 1/fs | taxa e período de amostragem |
| j | unidade imaginária (engenharia usa j, não i) |
| x* | conjugado complexo |
| E{·} | valor esperado |
| R[k] / S(f) | autocorrelação / densidade espectral de potência |
| σ² | variância (= potência de ruído) |

---

## Autoteste

Defina, sem consultar o glossário:

1. A diferença entre **frequência de Nyquist** e **taxa de Nyquist**.
2. A diferença entre **atraso de fase** e **atraso de grupo** — e qual você percebe.
3. Por que **aliasing** é irreversível e **vazamento espectral** não é.
4. O que **ergodicidade** permite fazer, e por que ela é hipótese e não fato.
5. A diferença entre **DFT** e **FFT**.
6. O que **SOS** significa e por que é requisito, não recomendação.
7. Por que **zero-padding** interpola mas não resolve.
8. O que **Wiener-Khinchin** torna possível.
9. O que **fase mínima** garante que os outros sistemas não garantem.
10. Por que **dither** melhora um sinal ao adicionar ruído a ele.
