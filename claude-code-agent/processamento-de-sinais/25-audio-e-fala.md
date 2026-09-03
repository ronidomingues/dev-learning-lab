# 25 · Áudio e fala — o domínio onde o ouvido é a especificação

`Nível: intermediário → avançado` · `Medições feitas em: 19/08/2026`

Áudio é o campo em que o **receptor final é humano**, e isso muda a engenharia:
o critério de qualidade não é erro quadrático, é percepção. Um sistema que
minimiza o erro numérico pode soar pior que um que erra mais, mas erra onde o
ouvido não escuta.

---

## 1 · O ouvido como especificação

| Propriedade | Valor | Consequência de projeto |
|---|---|---|
| Faixa de frequência | 20 Hz – 20 kHz (cai com a idade) | fs = 44,1 ou 48 kHz |
| Faixa dinâmica | ~120 dB | 16 bits (96 dB) basta para consumo; 24 para produção |
| Resolução de frequência | ~0,3 % (≈ 5 cents) em tons médios | afinadores precisam de 1 cent |
| Resolução temporal | ~2 ms para transientes | latência de ANC e de monitoração ao vivo |
| Sensibilidade à fase | **baixa** para sinais estacionários | IIR é aceitável em muitos casos |
| Sensibilidade à fase | **alta** para transientes | fase linear importa em percussão |
| Mascaramento | um tom forte esconde vizinhos mais fracos | **a base de todos os codecs** |

**Curvas isofônicas (Fletcher-Munson / ISO 226):** a sensibilidade depende da
frequência **e do nível**. Em volume baixo, graves e agudos somem primeiro — é
por isso que existe o botão "loudness" e por que mixagens devem ser conferidas em
vários volumes.

---

## 2 · Mascaramento e codecs perceptuais

**O fenômeno:** um tom de 1 kHz a 60 dB torna inaudível um tom de 1,1 kHz a 40 dB.
O segundo está lá, mas o ouvido não o detecta. Há mascaramento **simultâneo** (em
frequência) e **temporal** (até ~5 ms antes e ~100 ms depois de um som forte —
sim, *antes*, porque o processamento neural não é causal no sentido ingênuo).

**A exploração:** se não se ouve, não precisa codificar.

```
   1. banco de filtros (MDCT) divide em sub-bandas
   2. modelo psicoacústico calcula o LIMIAR DE MASCARAMENTO por banda
   3. quantiza cada banda com ruído JUSTO ABAIXO do limiar
   4. codificação entrópica (Huffman/aritmética) comprime o resultado
```

O passo 3 é a inversão conceitual: em vez de minimizar o ruído, o codec **coloca
ruído de propósito**, na maior quantidade que passa despercebida. Isso permite
12:1 de compressão com perda inaudível.

| Codec | Ano | Nota |
|---|---|---|
| MP3 | 1993 | banco de filtros híbrido + MDCT; patentes expiradas em 2017 |
| AAC | 1997 | MDCT pura; melhor que MP3 na mesma taxa |
| **Opus** | 2012 | **RFC 6716, livre de royalties**; voz e música, 6–510 kbit/s, latência baixa |
| FLAC / ALAC | — | **sem perda**: ~50 % com predição linear + Rice |

**Recomendação:** para projeto novo, **Opus**. É livre, é melhor que MP3 e AAC na
maioria dos pontos de operação, tem latência configurável e é padrão em WebRTC.

---

## 3 · Análise de fala

### O modelo fonte-filtro

```
   [ fonte ]  ──►  [ filtro do trato vocal ]  ──►  fala
   pregas vocais    ressonâncias (formantes)
   (vozeado) ou
   turbulência
   (não vozeado)
```

Este modelo, de 1960, sustenta praticamente toda a tecnologia de voz até hoje.
**A separação é o ponto:** f0 (a fonte) carrega entonação e identidade; as
formantes (o filtro) carregam o **conteúdo fonético**.

### LPC — predição linear

Modela o trato vocal como um filtro todo-polos: prever x[n] a partir das p
amostras anteriores. Os coeficientes descrevem as ressonâncias.

**Verificação:** sintetizei uma vogal com formantes em 700, 1220 e 2600 Hz e
apliquei LPC de ordem 16:

```
formantes verdadeiras:          [700, 1220, 2600]
formantes estimadas por LPC-16: [711. 1209. 1632. 2606.]
```

(Saída real.) Erro de **1,6 %, 0,9 % e 0,2 %**. O LPC recuperou o trato vocal
só observando a saída.

⚠️ **Note o 1632 Hz**, que não existe no sinal original. Ordem 16 dá 8 pares de
polos para 3 formantes; os polos sobrando se acomodam onde puderem e produzem
**formantes espúrias**. É a armadilha clássica do LPC: ordem alta demais inventa
ressonâncias. Regra de bolso: **p ≈ fs/1000 + 2** (18 para 16 kHz), e sempre
verificar os polos, não só confiar no número.

**Onde o LPC vive:** codecs de voz de telefonia (CELP, AMR, e o núcleo do Opus em
modo voz), síntese, reconhecimento clássico, e **compressão sem perda** de áudio
(FLAC usa predição linear).

### MFCC e a escala mel

A escala **mel** aproxima a percepção de altura, que é aproximadamente
logarítmica:

```
mel(f) = 2595·log₁₀(1 + f/700)
```

```
    100 Hz ->   150.5 mel      2000 Hz ->  1521.4 mel
    500 Hz ->   607.4 mel      4000 Hz ->  2146.1 mel
   1000 Hz ->  1000.0 mel      8000 Hz ->  2840.0 mel

razão mel(8000)/mel(1000) = 2.84   (linear seria 8.0)
```

(Saída real.) Oito vezes mais em hertz é só **2,84 vezes mais** em percepção.

**MFCC** (coeficientes cepstrais em escala mel), o cálculo em cinco passos:

```
1. janela (25 ms, salto de 10 ms)
2. |FFT|²
3. banco de ~26 filtros triangulares espaçados em mel
4. log da energia de cada banda
5. DCT  →  ficam os primeiros ~13 coeficientes
```

**Por que a DCT no fim** — e esta é a pergunta que quase ninguém responde: as
energias das bandas são fortemente correlacionadas entre si. A DCT as
descorrelaciona (aproxima a transformada de Karhunen-Loève para esse tipo de
dado), o que permite modelar com matrizes de covariância diagonais. Era essencial
na era dos HMMs com gaussianas.

**Status em 2026:** MFCC continua útil e barato, mas modelos neurais modernos
preferem **mel-espectrograma em log** cru — a DCT joga fora informação que a rede
sabe usar. Ver [`29`](29-dsp-e-aprendizado-de-maquina.md).

---

## 4 · Efeitos e processamento musical

| Efeito | Como funciona |
|---|---|
| **Equalizador** | cascata de biquads peaking/shelving ([`19 §6`](19-filtros-iir.md)) |
| **Compressor** | ganho variável controlado pela envoltória; ataque e relaxamento |
| **Reverberação por convolução** | convolui com a resposta ao impulso medida de uma sala |
| **Reverberação algorítmica** | rede de atrasos com realimentação (Schroeder, FDN) |
| **Pitch shift** | phase vocoder (STFT com correção de fase) ou PSOLA |
| **Time stretch** | mesmo maquinário, mudando a taxa de síntese |
| **Distorção** | não linearidade **de propósito** — cria harmônicos ([`13 §7`](13-sinais-e-sistemas-lti.md)) |
| **Auto-tune** | detecção de f0 + pitch shift para a nota mais próxima |

**Sobre reverberação por convolução:** medir a resposta ao impulso de uma sala
(estourando um balão, ou com uma varredura senoidal) e convoluir uma gravação
seca com ela põe a gravação **dentro** daquela sala. É a aplicação mais direta e
mais bonita do conceito de resposta ao impulso de [`10 §4`](10-fundamentos.md) —
e a razão de existir mercado para "impulsos de igrejas famosas".

⚠️ **A armadilha do phase vocoder:** ao mudar o tamanho do salto entre análise e
síntese, a fase de cada bin precisa ser **propagada coerentemente**, senão o som
fica "metálico" e desfocado (perda de coerência de fase vertical entre bins). É o
defeito característico de pitch shift malfeito, e o motivo de algoritmos como
*phase locking* existirem.

---

## 5 · Latência: o orçamento que decide arquitetura

| Aplicação | Latência tolerável |
|---|---|
| Cancelamento ativo de ruído | < 1 ms (física do som) |
| Monitoração ao vivo (músico) | < 10 ms |
| Videoconferência | < 150 ms (ida e volta) |
| Streaming | segundos (buffer) |

**O que consome latência:** buffer de E/S (o maior, tipicamente), tamanho do bloco
da FFT, atraso de grupo dos filtros ([`18 §2`](18-filtros-fir.md)), *look-ahead*
do compressor, e o codec.

Este orçamento é o que **proíbe** `filtfilt`, força FIR curto ou IIR, e às vezes
obriga a abandonar processamento em blocos por processamento amostra a amostra.
Muitas escolhas "estranhas" de código de áudio profissional são consequência
direta desta tabela.

---

## Autoteste

1. Por que um codec adiciona ruído de propósito?
2. Explique o modelo fonte-filtro e o que cada parte carrega de informação.
3. O LPC-16 achou uma formante em 1632 Hz que não existia. Por quê, e como evitar?
4. Por que existe uma DCT no fim do cálculo dos MFCC?
5. Por que modelos neurais modernos preferem mel-espectrograma a MFCC?
6. 8 kHz é quantas vezes mais "agudo" que 1 kHz na escala mel?
7. Como se põe uma gravação seca "dentro" de uma catedral?
8. Que restrição física limita o cancelamento ativo de ruído em agudos?
9. Qual codec você recomendaria para um projeto novo, e por quê?
