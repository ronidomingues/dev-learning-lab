# 90 · Bibliografia comentada

`Nível: todos` · **Edições verificadas na web em: 14 e 19/08/2026**

Regra deste arquivo: **nada inventado**. Onde não confirmei a edição, cito só
autor e título e digo que não confirmei. Onde o livro é **legalmente gratuito**,
está marcado com 🆓.

---

## Comece por aqui

| Se você é... | Comece por |
|---|---|
| Iniciante que programa | 🆓 **Think DSP** (Downey) |
| Iniciante que quer intuição | 🆓 **The Scientist and Engineer's Guide** (Smith) |
| Estudante de engenharia | **Oppenheim & Schafer** (o padrão) ou **Lyons** (mais amigável) |
| Praticante que quer aplicar | **Lyons** |
| Quem quer a visão de álgebra linear | 🆓 **Vetterli, Kovačević & Goyal** |
| Áudio | 🆓 **Julius O. Smith III** (série CCRMA) |
| Pesquisa em estimação/detecção | **Kay**, volumes I e II |

---

## Parte I · Gratuitos e legais 🆓

### Smith, Steven W. — *The Scientist and Engineer's Guide to Digital Signal Processing*
California Technical Publishing, 1997 (2ª ed. 1999). **Capítulos completos e
gratuitos em dspguide.com**, com autorização do autor. Também distribuído pela
Analog Devices.

- **Nível:** iniciante a intermediário.
- **O que faz melhor que os outros:** intuição. Explica convolução, filtros e FFT
  com o mínimo de formalismo e o máximo de figura. Se um conceito não entrou pelo
  Oppenheim, entra por aqui.
- **Envelheceu?** **Nas ferramentas, sim** (exemplos em BASIC e C antigos, e o
  capítulo de hardware está datado). **Nos conceitos, não.** Continua excelente.

### Downey, Allen B. — *Think DSP: Digital Signal Processing in Python*
O'Reilly, 2016. **Livre sob Creative Commons (BY-NC)**; PDF e código em
greenteapress.com e no GitHub (`AllenDowney/ThinkDSP`).

- **Nível:** iniciante.
- **O que faz melhor:** inverte a ordem — programa primeiro, formaliza depois.
  É a mesma filosofia deste curso, e funciona muito bem para quem já programa.
- **Limitação honesta:** é uma **introdução**. Não cobre projeto de filtro com
  especificação, estatística, nem multitaxa a sério.
- **Envelheceu?** Pouco. As APIs mudaram um pouco desde 2016; os notebooks
  continuam rodando com ajustes menores.

### Vetterli, M.; Kovačević, J.; Goyal, V. K. — *Foundations of Signal Processing*
Cambridge University Press, 2014. **PDF gratuito e legal** (versão 1.1, 2014) em
`fourierandwavelets.org`, sob licença Creative Commons BY-NC-ND.

- **Nível:** intermediário a avançado.
- **O que faz melhor que todos:** trata processamento de sinais como **álgebra
  linear em espaços de Hilbert** desde a primeira página. É exatamente a visão
  defendida em [`12 §6`](12-matematica-do-zero.md) e em [`60`](60-teoria-avancada.md).
  Se a frase "Fourier é uma mudança de base" fizer sentido para você, este é o
  seu livro.
- **Para quem não serve:** quem quer receita rápida. É matemática de verdade.

### Smith, Julius O. III — série de livros do CCRMA/Stanford
Quatro livros abertos em `ccrma.stanford.edu/~jos/`:
*Mathematics of the Discrete Fourier Transform*, *Introduction to Digital
Filters*, *Physical Audio Signal Processing*, *Spectral Audio Signal Processing*.

- **Nível:** intermediário a avançado, com foco em **áudio e música**.
- **O que faz melhor:** é a referência aberta mais completa de áudio digital.
  Modelagem física de instrumentos, análise espectral de música, filtros para
  áudio.
- **Formato:** HTML navegável; versões impressas à venda.

---

## Parte II · Os clássicos pagos

### Oppenheim, A. V.; Schafer, R. W. (com Buck, J. R.) — *Discrete-Time Signal Processing*
Prentice Hall / Pearson. **3ª edição, 2010** (verificado; não localizei edição
posterior em agosto de 2026).

- **Nível:** intermediário a avançado. É **o** livro-texto do campo.
- **O que faz melhor:** rigor e completude. Sinais e sistemas discretos,
  transformada Z, projeto de filtros, DFT, análise espectral — tudo com o cuidado
  formal que os outros não têm.
- **Envelheceu?** **Não na teoria**, que é definitiva. Sim no que não cobre:
  ferramentas modernas e aplicações de aprendizado de máquina.
- **Aviso honesto:** é **denso**. Muita gente compra, trava no capítulo 3 e
  desiste. Recomendo usá-lo como **referência** ao lado de um texto mais
  didático, não como primeiro contato. Foi o erro que descrevi em
  [`02-pre-requisitos.md`](02-pre-requisitos.md).
- **Em português:** houve edição brasileira de *Sinais e Sistemas* (o irmão deste
  livro) pela Pearson/Prentice Hall Brasil. **Não confirmei** disponibilidade nem
  qualidade da tradução em 2026.

### Oppenheim, A. V.; Willsky, A. S.; Nawab, S. H. — *Signals and Systems*
Prentice Hall, **2ª edição, 1996**.

- **Nível:** intermediário. Cobre **contínuo e discreto** lado a lado.
- **Quando usar:** se você precisa da parte contínua (Laplace, filtros analógicos)
  que o *Discrete-Time* pressupõe.
- **Há edição em português** (*Sinais e Sistemas*, Pearson). Tradução geralmente
  considerada aceitável; confira antes de comprar.

### Lyons, Richard G. — *Understanding Digital Signal Processing*
Prentice Hall, **3ª edição, 2010**.

- **Nível:** iniciante a intermediário.
- **O que faz melhor:** é o livro do **praticante**. Explica o que os outros
  assumem, tem dicas de implementação reais, e trata de armadilhas numéricas que
  livros acadêmicos ignoram.
- **Minha recomendação pessoal:** se você vai comprar **um** livro de DSP e não é
  para um curso formal, compre este.

### Proakis, J. G.; Manolakis, D. G. — *Digital Signal Processing: Principles, Algorithms, and Applications*
Pearson, **4ª edição, 2006**.

- **Nível:** intermediário a avançado. Alternativa ao Oppenheim, com mais
  algoritmos e aplicações.
- **Diferença prática:** Proakis é mais extenso em estimação espectral e
  aplicações; Oppenheim é mais elegante na teoria.

### Bracewell, R. N. — *The Fourier Transform and Its Applications*
McGraw-Hill, **3ª edição, 2000**.

- **Nível:** intermediário. Sobre **Fourier**, não sobre DSP.
- **O que faz melhor:** intuição sobre a transformada, com um "dicionário" visual
  de pares de transformada que vale o livro inteiro. Clássico que continua valendo.

---

## Parte III · Especializados

| Área | Livro | Nota |
|---|---|---|
| **Estimação e detecção** | Kay, S. M. — *Fundamentals of Statistical Signal Processing*, Vol. I (Estimation, 1993) e Vol. II (Detection, 1998), Prentice Hall | **A** referência. Cramér-Rao, ML, detecção ótima. Rigoroso e legível |
| **Filtragem adaptativa** | Haykin, S. — *Adaptive Filter Theory*, Pearson (5ª ed., 2013) | Padrão para LMS, RLS, Kalman |
| **Multitaxa e bancos de filtros** | Vaidyanathan, P. P. — *Multirate Systems and Filter Banks*, Prentice Hall, 1993 | Definitivo. Denso |
| **Multitaxa (mais prático)** | Crochiere, R. E.; Rabiner, L. R. — *Multirate Digital Signal Processing*, 1983 | Clássico, mais aplicado |
| **Wavelets** | Mallat, S. — *A Wavelet Tour of Signal Processing*, Academic Press (3ª ed., 2008) | A referência. Exigente |
| **Análise espectral** | Percival, D. B.; Walden, A. T. — *Spectral Analysis for Physical Applications*, Cambridge, 1993 | Rigor estatístico; multitaper |
| **Fala** | Rabiner, L. R.; Schafer, R. W. — *Theory and Applications of Digital Speech Processing*, 2010 | Referência de fala |
| **Imagem** | Gonzalez, R. C.; Woods, R. E. — *Digital Image Processing*, Pearson (4ª ed., 2018) | Padrão; **há edição em português** |
| **Comunicações** | Proakis, J. G.; Salehi, M. — *Digital Communications*, McGraw-Hill (5ª ed., 2007) | Padrão da área |
| **Rádio/SDR** | Collins, T. F. et al. — *Software-Defined Radio for Engineers*, Analog Devices, 2018 | 🆓 **gratuito** em PDF no site da Analog Devices |
| **Pulsares / radioastronomia** | Lorimer, D. R.; Kramer, M. — *Handbook of Pulsar Astronomy*, Cambridge, 2005 | Referência do [`08-projeto-espacial/`](08-projeto-espacial/README.md) |
| **Radioastronomia geral** | Condon, J. J.; Ransom, S. M. — *Essential Radio Astronomy*, Princeton, 2016 | 🆓 versão online no site do NRAO |
| **Adaptativos (histórico)** | Widrow, B.; Stearns, S. D. — *Adaptive Signal Processing*, Prentice Hall, 1985 | O original do LMS |

---

## Parte IV · Em português

O mercado editorial brasileiro em DSP é **magro**, e é honesto dizer isso.

| Livro | Situação |
|---|---|
| Traduções da Pearson (*Sinais e Sistemas*, *Processamento Digital de Imagens*) | existem; qualidade de tradução variável |
| Diniz, P. S. R.; da Silva, E. A. B.; Netto, S. L. — *Digital Signal Processing: System Analysis and Design*, Cambridge | escrito por autores **brasileiros** (UFRJ), publicado em inglês. Excelente e pouco conhecido |
| Apostilas e notas de aula de USP, UFMG, UFSC, UNICAMP | frequentemente **gratuitas** e de boa qualidade — ver [`85`](85-cursos-e-certificacoes.md) |

**Recomendação prática:** para material em português, as **notas de aula
universitárias** e este curso cobrem melhor que o mercado editorial. Para
profundidade, aceite ler em inglês — é onde o campo está escrito.

---

## Parte V · O que envelheceu e o que não

### Continua valendo integralmente
- Toda a **teoria** de LTI, Fourier, transformada Z, amostragem, projeto de filtros.
- Oppenheim & Schafer, Bracewell, Kay, Vaidyanathan, Mallat.
- Nyquist (1928), Shannon (1948), Cooley-Tukey (1965) nos originais.

### Envelheceu
- **Capítulos de hardware** de qualquer livro anterior a ~2010 (DSPs específicos,
  memória, benchmarks).
- **Exemplos de código** em BASIC, Fortran e C antigo.
- **Recomendações de ferramenta** — o ecossistema Python não existia quando os
  clássicos foram escritos.
- Tudo que trate de **aprendizado de máquina** antes de ~2015.

### Nunca existiu num livro
- O ecossistema atual (SciPy, PyTorch, GNU Radio) — está na documentação oficial.
- O estado da arte pós-2020 — está em papers ([`95`](95-referencias.md)) e no
  [`65-estado-da-arte.md`](65-estado-da-arte.md).

---

## Como eu montaria uma estante mínima

**Orçamento zero (e é sério — cobre até o intermediário):**
1. 🆓 Think DSP (Downey) — para começar programando
2. 🆓 dspguide.com (Smith) — para a intuição
3. 🆓 Foundations of Signal Processing (Vetterli et al.) — para o rigor
4. 🆓 Julius O. Smith (CCRMA) — se o foco for áudio

**Se puder comprar um:** Lyons, *Understanding DSP*.

**Se for para curso formal ou pesquisa:** Oppenheim & Schafer + Kay.

---

## Autoteste

1. Cite quatro livros legalmente gratuitos e o que cada um faz melhor.
2. Por que eu não recomendo o Oppenheim como primeiro contato?
3. Qual livro trata DSP como álgebra linear desde o começo?
4. Se você fosse comprar apenas um livro, qual e por quê?
5. O que envelheceu nos clássicos e o que não envelheceu?
6. Qual a situação da bibliografia em português, honestamente?

---

## Nota sobre verificação

Edições confirmadas na web em 14 e 19/08/2026: Oppenheim & Schafer (3ª ed., 2010);
disponibilidade gratuita e legal de dspguide.com, Think DSP (CC BY-NC),
*Foundations of Signal Processing* (CC BY-NC-ND, v1.1 2014) e dos livros do
CCRMA. **Não confirmei** ISBNs individuais nem a existência/qualidade de todas as
traduções brasileiras — onde há dúvida, o texto diz.
