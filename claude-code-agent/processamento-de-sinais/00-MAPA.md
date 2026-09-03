# Processamento de Sinais — Mapa do Assunto

`Nível: do zero absoluto ao de pesquisa` · `Última atualização: 19/08/2026`
`Base: Python 3.10.12 · NumPy 2.2.6 · SciPy 1.15.3 · Matplotlib 3.10.9 · Ubuntu 22.04.5`

> **Status: ✅ COMPLETO.** Todos os cinco blocos escritos e verificados.
> 36 documentos, 2 projetos-modelo executáveis, 81 testes passando, zero links quebrados.

---

## A pergunta que originou o material

*"Processamento de Sinais: como fazer do zero? Por onde começar? O que de
matemática se deve aprender?"*

Resposta curta, para não esperar a leitura:

- **Por onde começar:** por um sinal real na tela, hoje, sem instalar quase nada —
  [`04-como-comecar.md`](04-como-comecar.md). Não espere a matemática ficar pronta.
- **Que matemática:** números complexos (🔑 o único bloqueante), trigonometria
  circular, somatórios/série geométrica, cálculo básico, álgebra linear básica,
  probabilidade básica. **Nesta ordem.** O curso inteiro dessa fatia está em
  [`12-matematica-do-zero.md`](12-matematica-do-zero.md); os prazos honestos, em
  [`02-pre-requisitos.md`](02-pre-requisitos.md).
- **Tempo realista:** 1 tarde para o primeiro resultado; 4–6 semanas para uso
  funcional; 4–6 meses para praticante sólido.

---

## Roteiros de leitura

| Caminho | Sequência |
|---|---|
| **Rápido** (uma tarde) | `01` → `03` → `04` → `07-projeto-modelo/` |
| **Pesquisa espacial** | `01` → `04` → `15` → `16` → **`08-projeto-espacial/`** (curso próprio, do problema científico ao código) |
| **Praticante** (4–6 semanas) | `01` → `02` → `03` → `04` → `06` → `07` → `10` → `15` → `16` → `18` → `75` |
| **Com a matemática junto** | `01` → `02` → `12` (§1–§4) → `10` → `13` → `14` → `12` (§5–§7) → `16` |
| **Áudio** | `04` → `06` → `07` → `15` → `20` → `25` |
| **Quem decide compra** | `01` → `11` → `80` → `65` |

---

## Arquivos

### BLOCO A · Porta de entrada — ✅ completo

| Arquivo | Nível | Conteúdo |
|---|---|---|
| [01-introducao-leigo.md](01-introducao-leigo.md) | iniciante | O que é, zero jargão. As 5 ideias que sustentam o campo |
| [02-pre-requisitos.md](02-pre-requisitos.md) | iniciante | **A resposta sobre matemática**, tempos realistas, rota de resgate |
| [03-instalacao.md](03-instalacao.md) | iniciante | Manual de campo: Linux/macOS/Windows/WSL2, PATH, proxy, 12 erros literais |
| [04-como-comecar.md](04-como-comecar.md) | iniciante | Do ambiente pronto ao espectro na tela. Aliasing provocado de propósito |
| [05-manual-de-uso.md](05-manual-de-uso.md) | intermediário | Notação do campo + referência da API por tarefa + equivalência MATLAB |
| [06-exemplos.md](06-exemplos.md) | int./avançado | **12 exemplos executados**, incl. DTMF, ECG, filtro casado, dither |
| [07-projeto-modelo/](07-projeto-modelo/README.md) | intermediário | `sinal`: afinador e filtrador completo. **25 testes passando** |
| [08-projeto-espacial/](08-projeto-espacial/README.md) | int./avançado | `cosmos`: **sinais do espaço profundo** — radiômetro, dispersão interestelar, pulsar por folding, enlace com a DSN. Curso aplicado de 6 documentos + **56 testes passando** |

### BLOCO B · Núcleo — ✅ completo

| Arquivo | Nível | Conteúdo |
|---|---|---|
| [10-fundamentos.md](10-fundamentos.md) | iniciante/int. | Sinal, sistema, LTI, convolução, autovetores, os 4 pares de transformada |
| [11-historia.md](11-historia.md) | iniciante | 1822 a 2026. De onde vêm os 44,1 kHz e por que a FFT esperou 160 anos |
| [12-matematica-do-zero.md](12-matematica-do-zero.md) | iniciante/int. | 🔑 **A matemática exata que se usa**, com roteiro de 3 meses |
| [13-sinais-e-sistemas-lti.md](13-sinais-e-sistemas-lti.md) | intermediário | Equação de diferenças, estabilidade, fase, Gibbs medido |
| [14-fourier.md](14-fourier.md) | intermediário | Série, FT, DTFT, tabela de propriedades, princípio da incerteza |
| [15-amostragem-e-quantizacao.md](15-amostragem-e-quantizacao.md) | intermediário | Nyquist, aliasing, bandpass sampling, dither, jitter, droop |
| [16-dft-e-fft.md](16-dft-e-fft.md) | int./avançado | Resolução × zero-padding, borboleta, convolução circular, normalização |
| [17-transformada-z.md](17-transformada-z.md) | avançado | ROC, polos e zeros, regra geométrica, bilinear e warping, fase mínima |
| [18-filtros-fir.md](18-filtros-fir.md) | int./avançado | Fase linear, 4 tipos, janelas medidas, Kaiser, Parks-McClellan |
| [19-filtros-iir.md](19-filtros-iir.md) | int./avançado | Famílias comparadas, **SOS × forma direta em float32**, biquads |
| [20-analise-espectral-e-janelas.md](20-analise-espectral-e-janelas.md) | avançado | Vazamento medido, festonamento, variância de Welch, paramétricos |

| [21-multitaxa-e-bancos-de-filtros.md](21-multitaxa-e-bancos-de-filtros.md) | avançado | Decimação, polifásico, identidades nobres, CIC medido, bancos e MDCT |
| [22-ruido-e-processos-estocasticos.md](22-ruido-e-processos-estocasticos.md) | avançado | Estacionaridade, ergodicidade, Wiener-Khinchin, as cores do ruído |
| [23-estimacao-e-filtragem-adaptativa.md](23-estimacao-e-filtragem-adaptativa.md) | avançado | Wiener, LMS/NLMS com a curva em U medida, RLS, Kalman, eco e ANC |
| [24-tempo-frequencia-e-wavelets.md](24-tempo-frequencia-e-wavelets.md) | avançado | STFT com o compromisso medido, CWT/DWT, Wigner-Ville e seus termos cruzados |
| [25-audio-e-fala.md](25-audio-e-fala.md) | int./avançado | Mascaramento, codecs, fonte-filtro, LPC com formantes recuperadas, MFCC |
| [26-comunicacoes-e-sdr.md](26-comunicacoes-e-sdr.md) | avançado | I/Q, modulações, sincronismo, OFDM, codificação, hardware SDR |
| [27-imagens-e-2d.md](27-imagens-e-2d.md) | int./avançado | Separabilidade medida, kernels, moiré, DCT e JPEG, MRI e espaço k |
| [28-implementacao-ponto-fixo-e-hardware.md](28-implementacao-ponto-fixo-e-hardware.md) | avançado | Notação Q, **polo saindo do círculo com 16 bits**, CIC, MCU/DSP/FPGA |
| [29-dsp-e-aprendizado-de-maquina.md](29-dsp-e-aprendizado-de-maquina.md) | avançado | O que foi absorvido, o que não foi, DDSP, codecs neurais |
| [60-teoria-avancada.md](60-teoria-avancada.md) | pesquisa | Hilbert, amostragem com rigor, incerteza provada, frames, Cramér-Rao |
| [65-estado-da-arte.md](65-estado-da-arte.md) | pesquisa | Onde o campo está em ago/2026, debates abertos, o que não mudou |

### BLOCO C · Prática e erros — ✅ completo

| Arquivo | Nível | Conteúdo |
|---|---|---|
| [70-pratica.md](70-pratica.md) | todos | **14 laboratórios** progressivos, do espectro caseiro a reproduzir um paper |
| [75-armadilhas.md](75-armadilhas.md) | todos | **30 armadilhas + 10 mitos**, com sintoma → causa → correção, e tabela de diagnóstico |

### BLOCO D · Economia e ecossistema — ✅ completo

| Arquivo | Nível | Conteúdo |
|---|---|---|
| [80-custos-e-licencas.md](80-custos-e-licencas.md) | todos | Custo zero para o curso; BSD × GPL; MATLAB 2026; SDR; custos ocultos |
| [85-cursos-e-certificacoes.md](85-cursos-e-certificacoes.md) | todos | Cursos gratuitos em **PT, EN e FR**, pesquisados; a verdade sobre certificações |

### BLOCO E · Fontes — ✅ completo

| Arquivo | Nível | Conteúdo |
|---|---|---|
| [90-bibliografia.md](90-bibliografia.md) | todos | Livros comentados, com **4 gratuitos e legais** que cobrem até o intermediário |
| [95-referencias.md](95-referencias.md) | todos | Papers seminais, normas, documentação, código para ler, onde acompanhar |
| [GLOSSARIO.md](GLOSSARIO.md) | todos | ~130 termos definidos, com o capítulo de referência de cada um |

---

## O que você saberá ao final

- Instalar todo o ambiente em qualquer SO, ou começar sem instalar nada.
- Carregar áudio, calcular espectro, achar frequências e amplitudes corretamente.
- Projetar filtros FIR e IIR com especificação, e saber qual escolher e por quê.
- Reconhecer aliasing, vazamento, festonamento e instabilidade **pelo sintoma**.
- Estimar frequência fundamental com precisão de 0,1 cent.
- Mudar taxa de amostragem sem estragar o sinal, e saber quanto isso custa.
- Tratar ruído com a estatística certa, e validar um estimador sem se enganar.
- Fazer um filtro **aprender** os próprios coeficientes (Wiener, LMS, Kalman).
- Escolher entre STFT e wavelets sabendo o que cada uma compra e paga.
- Levar um projeto para ponto fixo sem que o filtro vire oscilador.
- Explicar o que o aprendizado profundo absorveu do DSP e o que não absorveu.
- Ler a notação de qualquer livro ou paper da área, e saber onde procurar.
- Saber exatamente que matemática estudar, em que ordem e em quanto tempo.
- Detectar um sinal 26 dB **abaixo** do ruído — e decidir se é descoberta ou acaso.

---

## Números do material

| | |
|---|---|
| Documentos | **36** |
| Projetos-modelo executáveis | **2** (`sinal` e `cosmos`) |
| Testes automatizados | **81** (25 + 56), todos passando |
| Exemplos completos executados | 12 no `06` + os de cada capítulo |
| Laboratórios propostos | 14 no `70` + 4 níveis no `08` |
| Armadilhas e mitos catalogados | 30 + 10 |
| Termos no glossário | ~130 |
| Links internos quebrados | **0** |

---

## Nota sobre verificação

Todo bloco de código deste curso foi **executado** na máquina de referência, e as
saídas mostradas são as saídas reais. Onde a medição contrariou o que se costuma
repetir na área, o material registra a medição — e não o folclore. Três exemplos:

- O sobressinal de ~9 % na resposta ao degrau **não** é eliminado por janelamento
  ([`13 §6`](13-sinais-e-sistemas-lti.md)).
- `signal.resample` é mais preciso que `resample_poly` no miolo e pior nas bordas —
  a recomendação usual é imprecisa ([`06 §6`](06-exemplos.md)).
- Medir a variância de um estimador espectral ao longo da frequência dá resultado
  errado; é preciso Monte Carlo ([`20 §4`](20-analise-espectral-e-janelas.md)).
