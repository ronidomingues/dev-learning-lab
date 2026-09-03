# 27 · Imagens e sinais 2-D — a mesma teoria, um índice a mais

`Nível: intermediário → avançado` · `Medições feitas em: 19/08/2026`

Uma imagem é um sinal de duas variáveis **espaciais**. Toda a teoria dos capítulos
anteriores vale — convolução, Fourier, amostragem, filtros — com um índice a mais
e um vocabulário levemente diferente.

---

## 1 · O dicionário 1-D → 2-D

| 1-D | 2-D | Observação |
|---|---|---|
| x[n] | x[m, n] | linha, coluna |
| tempo (s) | espaço (mm, pixels) | |
| frequência (Hz) | **frequência espacial** (ciclos/mm, ciclos/pixel) | |
| taxa de amostragem | resolução (pixels/mm, dpi) | |
| aliasing temporal | **moiré** | mesma matemática |
| filtro FIR | **kernel** / máscara | |
| convolução | convolução 2-D | |
| FFT | FFT 2-D (separável) | |

**A frequência espacial** é a chave da intuição: baixa frequência = variação lenta
no espaço (regiões suaves, gradientes); alta frequência = variação rápida (bordas,
texturas, ruído). É por isso que borrar = passa-baixa e realçar = passa-alta.

---

## 2 · Separabilidade — a otimização que muda tudo

Um kernel 2-D é **separável** se h[m,n] = h₁[m]·h₂[n]. Nesse caso, a convolução
2-D vira duas convoluções 1-D: primeiro nas linhas, depois nas colunas.

```
imagem  512x512, kernel 15x15: 2D direto   0.059 Gmult | separável   0.008 Gmult | ganho  7.5x
imagem 1024x1024, kernel 31x31: 2D direto   1.008 Gmult | separável   0.065 Gmult | ganho 15.5x
imagem 2048x2048, kernel 63x63: 2D direto  16.647 Gmult | separável   0.528 Gmult | ganho 31.5x
```

(Saída real.) **O ganho é K/2**, e cresce com o tamanho do kernel. Um desfoque
gaussiano 63×63 fica **31 vezes mais barato**.

**Quais kernels são separáveis:** gaussiano (sempre), média (sempre), Sobel (sim),
e qualquer um cuja matriz tenha **posto 1**. Verificação prática: calcule a SVD do
kernel; se só houver um valor singular não nulo, é separável. Se houver dois ou
três dominantes, dá para aproximar por uma soma de 2–3 separáveis, o que ainda
compensa.

**Por que o gaussiano é separável:** porque e^{−(x²+y²)/2σ²} = e^{−x²/2σ²}·e^{−y²/2σ²}.
A exponencial transforma soma em produto — a mesma propriedade algébrica que
sustenta Fourier ([`10`](10-fundamentos.md), cinco porquês).

A FFT 2-D também é separável: FFT das linhas, depois das colunas. É assim que
`np.fft.fft2` funciona internamente.

---

## 3 · Filtros clássicos e o que cada um é

| Kernel | O que faz | Em linguagem de DSP |
|---|---|---|
| Média (box) | borra | passa-baixa com resposta sinc 2-D |
| **Gaussiano** | borra suavemente | passa-baixa sem lóbulos laterais |
| **Sobel / Prewitt** | detecta borda | derivada + suavização perpendicular |
| **Laplaciano** | detecta borda (2ª derivada) | passa-alta isotrópico |
| **LoG / DoG** | borda multiescala | passa-faixa; base do SIFT |
| **Unsharp mask** | realça | original + k·(original − borrado) = passa-alta somado |
| **Mediana** | tira "sal e pimenta" | **não linear** — Fourier não se aplica |
| **Bilateral** | borra preservando bordas | **não linear**, pesa por similaridade |

**Por que o gaussiano é preferido ao box:** o box tem resposta sinc, com lóbulos
laterais a −13 dB ([`18 §6`](18-filtros-fir.md)), e produz artefatos de ringing e
"blocos". O gaussiano não tem lóbulos.

**Por que Sobel e não só a diferença:** derivar amplifica alta frequência, e ruído
é alta frequência ([`12 §5`](12-matematica-do-zero.md)). O Sobel embute uma
suavização na direção perpendicular à derivada, o que reduz o ruído sem borrar a
borda que se quer detectar.

⚠️ **Mediana e bilateral são não lineares.** Nada de superposição, nada de resposta
em frequência, nada de teorema da convolução. Eles funcionam **por isso**: apenas
um filtro não linear consegue remover ruído impulsivo sem borrar bordas. É o
limite da teoria LTI — ver [`13 §7`](13-sinais-e-sistemas-lti.md).

---

## 4 · Amostragem espacial, moiré e reconstrução

O teorema da amostragem vale igual, em duas dimensões. Violá-lo produz **moiré** —
o padrão de interferência que aparece ao fotografar um tecido listrado ou a tela
de um monitor.

**As defesas:**

1. **Filtro óptico anti-aliasing (OLPF)** — uma camada birrefringente na frente do
   sensor que borra levemente. Câmeras modernas de alta resolução frequentemente
   **removem** esse filtro: quando a densidade de pixels supera a resolução da
   lente, a própria lente já faz o papel de passa-baixa.
2. **Sobreamostrar e reduzir depois**, com filtro adequado.
3. **Nunca** redimensionar por decimação ingênua (`img[::2, ::2]`) — é o
   `x[::M]` de [`21 §1`](21-multitaxa-e-bancos-de-filtros.md), com o mesmo defeito.

**Interpolação ao ampliar:** vizinho mais próximo (rápido, serrilhado), bilinear,
bicúbica, **Lanczos** (sinc janelada — a melhor das clássicas). Todas são
aproximações da interpolação sinc ideal; Lanczos é a que mais se aproxima, ao
preço de leve ringing perto de bordas fortes.

---

## 5 · Transformadas e compressão

### Por que a DCT e não a DFT no JPEG

A DCT tem **compactação de energia** superior para sinais reais e correlacionados,
e não sofre a descontinuidade de borda que a DFT sofre (a DFT assume periodicidade;
a DCT assume simetria par, que emenda melhor).

Medindo num bloco 8×8 típico (suave, com um gradiente e ruído):

```
 1 de 64 coeficientes DCT retém  96.42% da energia
 4 de 64 coeficientes DCT retém  99.98% da energia
 8 de 64 coeficientes DCT retém  99.98% da energia
16 de 64 coeficientes DCT retém  99.99% da energia
```

(Saída real.) **Quatro de sessenta e quatro coeficientes carregam 99,98 % da
energia.** Os outros 60 podem ser quantizados grosseiramente ou zerados.

⚠️ **Leitura honesta:** o primeiro coeficiente sozinho retém 96 %, e ele é o
**DC** — a média do bloco. Isso é característico de imagens reais, e é exatamente
por isso que o JPEG trata o DC separadamente (codifica a **diferença** entre
blocos vizinhos, com DPCM) e os 63 coeficientes AC de outro jeito (varredura em
ziguezague + Huffman). Um exemplo bonito de o formato do arquivo espelhar a
estatística dos dados.

### O pipeline do JPEG

```
RGB → YCbCr → subamostra croma (4:2:0) → blocos 8×8 → DCT →
quantização (a tabela é onde mora a perda) → ziguezague → RLE + Huffman
```

**A subamostragem de croma** merece destaque: o olho tem muito mais resolução para
luminância que para cor (há ~20× mais bastonetes que cones na periferia). Jogar
fora 3/4 da resolução de cor é quase invisível e economiza 50 % antes de qualquer
transformada. É psicofísica virando engenharia, como no áudio ([`25 §2`](25-audio-e-fala.md)).

### Alternativas

| Formato | Transformada | Nota |
|---|---|---|
| JPEG | DCT 8×8 | universal; artefato de bloco em taxa baixa |
| **JPEG2000** | wavelet | sem bloco, escalável; nunca pegou na web |
| WebP / AVIF / HEIC | preditiva + transformada (de codecs de vídeo) | melhor compressão; AVIF é livre |
| PNG | nenhuma (predição + Deflate) | **sem perda** |

---

## 6 · Imagem médica e científica — onde o DSP é o instrumento

| Modalidade | O papel do DSP |
|---|---|
| **Ressonância magnética (MRI)** | a máquina mede o **espaço k**, que é literalmente a transformada de Fourier 2-D/3-D da imagem. A imagem é obtida por IFFT. Sem Fourier, não há MRI |
| **Tomografia (CT)** | retroprojeção filtrada; o teorema da fatia central liga projeções ao espectro 2-D |
| **Ultrassom** | *beamforming*, filtro casado, Doppler para fluxo sanguíneo |
| **Radar SAR** | compressão de pulso em duas dimensões; a "abertura sintética" é processamento, não antena |
| **Astronomia** | deconvolução da PSF, síntese de abertura (interferometria) |
| **Microscopia** | deconvolução 3-D, super-resolução |

**MRI merece a frase:** a máquina **não** mede a imagem. Ela mede coeficientes de
Fourier, um a um, e a imagem é reconstruída. Preencher o espaço k mais depressa é
o que **compressive sensing** ([`11`](11-historia.md)) permitiu — e isso encurtou
exames em uso clínico hoje. Um resultado de processamento de sinais que se traduz
em menos tempo de paciente dentro do tubo.

---

## 7 · O que muda de 1-D para 2-D

| Aspecto | Diferença |
|---|---|
| Custo | O(N²) pixels; kernels grandes exigem separabilidade ou FFT |
| Orientação | filtros podem ser anisotrópicos; existe direção |
| Bordas | quatro bordas, e a política de preenchimento importa muito mais |
| Fase | **crítica**: a fase da FFT 2-D carrega a estrutura da imagem |
| Não linearidade | mediana e bilateral são padrão, não exceção |
| Percepção | luminância × croma têm resoluções diferentes |

**Sobre a fase em 2-D:** um experimento clássico — troque a magnitude do espectro
de duas imagens mantendo as fases. **Você reconhece a imagem cuja fase foi
mantida**, não a da magnitude. A fase carrega onde estão as bordas; a magnitude,
quanto de cada frequência existe. É a demonstração mais convincente de que
descartar fase (como se faz rotineiramente em áudio) seria catastrófico aqui.

---

## Autoteste

1. O que é frequência espacial, e como ela se relaciona com bordas?
2. Qual o ganho de separar um kernel 63×63, e por que o gaussiano é separável?
3. Como verificar se um kernel qualquer é separável?
4. Por que o filtro gaussiano é preferido ao de média?
5. Por que Sobel embute suavização perpendicular?
6. Por que mediana e bilateral escapam da teoria LTI, e por que isso é útil?
7. `img[::2, ::2]` está errado por quê?
8. Quantos coeficientes DCT de 64 retêm ~99,98 % da energia, e qual a ressalva?
9. Por que o JPEG subamostra croma e não luminância?
10. Por que não existe MRI sem transformada de Fourier?
11. Ao trocar magnitude e fase de duas imagens, qual você reconhece?
