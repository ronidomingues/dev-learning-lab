# 95 · Referências — papers, specs, documentação e pessoas

`Nível: todos` · `Atualizado em: 19/08/2026`

Diferente da [`90-bibliografia.md`](90-bibliografia.md) (livros), aqui estão as
**fontes primárias**: artigos seminais, normas, documentação oficial e código.

---

## 1 · Os papers que fundaram o campo

| Ano | Autor | Trabalho | Por que ler |
|---|---|---|---|
| 1822 | J. Fourier | *Théorie analytique de la chaleur* | a origem. **Domínio público** |
| 1928 | H. Nyquist | "Certain Topics in Telegraph Transmission Theory", *Trans. AIEE* | o limite banda × taxa |
| 1928 | J. B. Johnson / H. Nyquist | ruído térmico (dois artigos, *Phys. Rev.*) | medida e teoria do ruído de Johnson-Nyquist |
| 1933 | V. Kotelnikov | teorema da amostragem (em russo) | prioridade ignorada no Ocidente ([`11`](11-historia.md)) |
| **1948** | **C. E. Shannon** | **"A Mathematical Theory of Communication"**, *Bell System Technical Journal* | 🔑 **o artigo mais importante do século em engenharia.** Cria bit, entropia e capacidade |
| 1949 | C. E. Shannon | "Communication in the Presence of Noise", *Proc. IRE* | a forma canônica do teorema da amostragem |
| 1960 | R. E. Kálmán | "A New Approach to Linear Filtering and Prediction Problems", *J. Basic Eng.* | o filtro de Kalman |
| 1960 | B. Widrow, M. E. Hoff | "Adaptive Switching Circuits" | **o LMS** — e o gradiente estocástico, 30 anos antes do SGD virar moda |
| **1965** | **J. W. Cooley, J. W. Tukey** | **"An Algorithm for the Machine Calculation of Complex Fourier Series"**, *Math. Comp.* 19(90) | 🔑 a FFT. Seis páginas que mudaram tudo |
| 1972 | T. W. Parks, J. H. McClellan | projeto ótimo de FIR (Remez/minimax) | o algoritmo de [`18 §4`](18-filtros-fir.md) |
| 1978 | F. J. Harris | "On the Use of Windows for Harmonic Analysis with the DFT", *Proc. IEEE* | 🔑 **a** referência sobre janelas. Tabelas usadas até hoje |
| 1981 | A. V. Oppenheim, J. S. Lim | "The Importance of Phase in Signals", *Proc. IEEE* | o experimento de trocar magnitude e fase ([`27 §7`](27-imagens-e-2d.md)) |
| 1984 | Heideman, Johnson, Burrus | "Gauss and the History of the FFT", *IEEE ASSP Magazine* | mostra que Gauss chegou lá em 1805 |
| 1989 | S. Mallat | "A Theory for Multiresolution Signal Decomposition", *IEEE PAMI* | a DWT como banco de filtros |
| 1988 | I. Daubechies | wavelets ortogonais de suporte compacto, *Comm. Pure Appl. Math.* | as db-N |
| 1993 | C. Berrou, A. Glavieux, P. Thitimajshima | códigos turbo, *ICC* | primeiro a chegar perto do limite de Shannon |
| 1962/1996 | R. Gallager / MacKay & Neal | LDPC — inventado e **redescoberto** | 30 anos esquecido por falta de computação |
| **2006** | Candès, Romberg, Tao / Donoho | **compressive sensing**, *IEEE Trans. Inf. Theory* | 🔑 reformula a pergunta "quantas amostras?" |
| 2012 | Hassanieh, Indyk, Katabi, Price | Sparse FFT, *STOC/SODA* | O(k log N) para espectros esparsos |
| 2020 | Engel et al. (Google) | **DDSP: Differentiable Digital Signal Processing**, *ICLR* | 🔑 o clássico dentro da rede ([`29 §4`](29-dsp-e-aprendizado-de-maquina.md)) |
| 2019 | R. Zhang | "Making Convolutional Networks Shift-Invariant Again", *ICML* | aliasing em *stride*: o teorema da amostragem consertando redes |

**Se você ler apenas dois:** Shannon 1948 e Cooley-Tukey 1965.
**Se ler apenas um artigo prático:** Harris 1978, sobre janelas.

---

## 2 · Normas e especificações

| Norma | Assunto |
|---|---|
| **ITU-T G.711 / G.722 / G.729** | codecs de voz de telefonia (μ-law, A-law, banda larga) |
| **ISO/IEC 11172-3** | MPEG-1 Layer III (MP3) |
| **ISO/IEC 14496-3** | MPEG-4 Audio (AAC) |
| **RFC 6716** | **Opus** — codec livre de royalties |
| **AES17** | medição de equipamento de áudio digital |
| **ITU-R BS.1770** | medição de *loudness* (a base do LUFS, usado em streaming) |
| **IEC 61672** | medidores de nível sonoro |
| **IEEE 1057 / IEEE 1241** | caracterização de digitalizadores e conversores A/D (ENOB, SINAD) |
| **IEC 60601-2-25** | eletrocardiógrafos — inclui a exigência de corte em 0,05 Hz ([`06 §4`](06-exemplos.md)) |
| **AHA/ACC/HRS** | recomendações de filtragem de ECG para diagnóstico |
| **CCSDS** | padrões de telemetria e codificação para espaço (turbo, LDPC) |
| **ITU-R / Anatel** | uso do espectro; no Brasil, a Anatel regula transmissão |
| **DO-178C / ISO 26262** | certificação de software em aviação e automotivo |

**Por que isso importa:** em setor regulado, a norma **define** o projeto do
filtro. O caso do ECG é o exemplo mais afiado: a escolha entre 0,5 e 0,05 Hz não
é preferência técnica, é conformidade — e tem consequência clínica.

---

## 3 · Documentação oficial (o que consultar no dia a dia)

| Recurso | URL | Uso |
|---|---|---|
| **SciPy Signal** | `docs.scipy.org/doc/scipy/reference/signal.html` | a referência que você abrirá todo dia |
| SciPy — tutoriais de STFT | idem, seção `ShortTimeFFT` | a API atual ([`05`](05-manual-de-uso.md)) |
| NumPy FFT | `numpy.org/doc/stable/reference/routines.fft.html` | convenções e normalização |
| Matplotlib | `matplotlib.org` | figuras |
| PyWavelets | `pywavelets.readthedocs.io` | wavelets (substitui `scipy.signal.cwt`, removida) |
| GNU Radio | `wiki.gnuradio.org` | SDR |
| CMSIS-DSP | `arm-software.github.io/CMSIS-DSP/` | DSP em Cortex-M |
| Astropy | `docs.astropy.org` | tempo, coordenadas, unidades (para o projeto espacial) |
| **DSN Link Design Handbook (810-005)** | JPL/NASA, público | enlace de espaço profundo |
| ATNF Pulsar Catalogue | `atnf.csiro.au/research/pulsar/psrcat` | parâmetros reais de pulsares |
| PhysioNet | `physionet.org` | bases públicas de sinais biomédicos (ECG, EEG) |

---

## 4 · Código-fonte que vale ler

Ler implementação madura ensina o que nenhum livro ensina.

| Projeto | O que aprender |
|---|---|
| **`scipy/signal/_filter_design.py`** | como se projeta filtro de verdade, com todos os casos de borda |
| **`scipy/signal/_short_time_fft.py`** | a API moderna de STFT, e por que a antiga foi aposentada |
| **`pocketfft`** (dentro da SciPy) | FFT de produção: radix misto, Bluestein, threads |
| **FFTW** | o estado da arte em FFT (⚠️ GPL — ver [`80`](80-custos-e-licencas.md)) |
| **GNU Radio** (`gr-filter`, `gr-digital`) | blocos de rádio reais, com estado e streaming |
| **PRESTO** | pipeline real de busca de pulsares |
| **RNNoise / DeepFilterNet** | híbrido DSP + rede pequena para realce de fala |
| **libopus** | codec de produção, com todos os compromissos reais |

---

## 5 · Pessoas para acompanhar

**Fundadores e clássicos:** Alan V. Oppenheim (MIT), Ronald Schafer, Lawrence
Rabiner (fala), Bernard Widrow (adaptativos), P. P. Vaidyanathan (multitaxa),
Ingrid Daubechies e Stéphane Mallat (wavelets), Martin Vetterli (EPFL),
Emmanuel Candès e David Donoho (compressive sensing), Julius O. Smith III (áudio).

**Comunicadores que vale seguir:**
- **3Blue1Brown** — intuição visual de Fourier e álgebra linear
- **Richard Lyons** — artigos práticos, muitos em `dsprelated.com`
- **Wireless Pi** — comunicações digitais explicadas com clareza
- **Julius Smith** — os livros abertos do CCRMA

---

## 6 · Onde acompanhar a fronteira

| Conferência | Foco | Quando |
|---|---|---|
| **ICASSP** | geral — a principal da área | anual (2026: tema "Where Signals Meet Intelligence") |
| **EUSIPCO** | geral, europeia | anual (2026: Bruges, 31/08–04/09) |
| **APSIPA** | geral, Ásia-Pacífico | anual (2026: Bancoc, 09–12/11) |
| **Interspeech** | fala | anual |
| **DAFx** | efeitos de áudio digital | anual |
| **WASPAA** | aplicações de áudio e acústica | bienal |
| **ISMIR** | recuperação de informação musical | anual |

**Periódicos:** *IEEE Transactions on Signal Processing*, *IEEE/ACM TASLP*
(áudio e fala), *IEEE Signal Processing Magazine* (tutoriais excelentes e
legíveis), *Signal Processing* (Elsevier).

**Pré-prints:** arXiv — `eess.SP` (processamento de sinais), `eess.AS` (áudio e
fala), `cs.SD` (som), `astro-ph.IM` (instrumentação astronômica).

**Comunidades:** `dsp.stackexchange.com` (a melhor fonte de respostas técnicas
específicas), `r/DSP`, listas do GNU Radio.

---

## 7 · Fontes usadas na construção deste curso

Todas as afirmações datadas deste material foram verificadas na web nas datas
indicadas em cada arquivo. As principais:

- Versões de software (Python 3.14.7, NumPy 2.5.2, SciPy 1.18.0, Octave 11.3.0,
  Audacity 3.7.8, GNU Radio 3.10.12/4.0-RC1) — consultadas em 14/08/2026 nos sites
  oficiais.
- Preços de MATLAB e de hardware SDR — consultados em 14/08/2026.
- Cursos em PT/EN/FR e programa educacional do IEEE SPS — consultados em 14 e
  19/08/2026.
- Edições de livros e disponibilidade gratuita — consultadas em 14 e 19/08/2026.
- Estado da arte e ICASSP 2026 — consultado em 19/08/2026.
- Status do radiotelescópio BINGO — consultado em 19/08/2026.

**Todo bloco de código deste curso foi executado** na máquina de referência
(Ubuntu 22.04.5, Python 3.10.12, NumPy 2.2.6, SciPy 1.15.3, Matplotlib 3.10.9), e
as saídas publicadas são reais. Onde a medição contrariou o que se costuma repetir
na área, o material registra a medição — ver a nota de verificação no
[`00-MAPA.md`](00-MAPA.md).

---

## Autoteste

1. Se você lesse apenas dois papers da lista, quais seriam e por quê?
2. Qual artigo prático de 1978 continua sendo a referência sobre janelas?
3. Que norma define o corte de 0,05 Hz para ECG de diagnóstico, e por que isso
   importa mais que a preferência do engenheiro?
4. Qual paper de 2019 mostra o teorema da amostragem consertando redes neurais?
5. Qual código-fonte você leria para entender projeto de filtro de verdade?
6. Onde procurar o estado da arte: livro, norma, documentação ou pré-print?
7. Por que ler `pocketfft` ensina algo que nenhum livro de FFT ensina?
