# 05 · Como as instituições fazem de verdade

`Nível: intermediário` · `Pesquisado na web em: 19/08/2026`

O `cosmos/` é didático: 64 canais, 60 segundos, uma máquina. Este arquivo mostra
a distância entre isso e um instrumento real — e o que exatamente muda quando a
escala aumenta cinco ordens de grandeza.

---

## 1 · NASA / JPL — a Deep Space Network

**O que é.** Três complexos de antenas separados por ~120° de longitude —
**Goldstone** (Califórnia), **Madri** (Espanha) e **Canberra** (Austrália) — de
modo que qualquer sonda esteja sempre visível de pelo menos um deles enquanto a
Terra gira. Antenas de 34 m e de 70 m.

**O que fazem que este projeto não faz:**

| Aspecto | `cosmos` | DSN real |
|---|---|---|
| Predição de Doppler | busca em grade | efeméride orbital calculada com dias de antecedência; a busca cobre só o **erro residual** |
| Referência de frequência | implícita | **maser de hidrogênio**, estabilidade ~10⁻¹⁵ |
| Rastreamento | estimativa em bloco | PLL de 2ª/3ª ordem, largura de laço de poucos Hz |
| Correção de erro | nenhuma | códigos **turbo** e **LDPC** dos padrões CCSDS, a fração de dB do limite de Shannon |
| Compensação atmosférica | nenhuma | modelo de troposfera e ionosfera, calibração por radiômetro de vapor d'água |
| Combinação de antenas | uma | *arraying*: várias antenas somadas coerentemente |
| Referencial de tempo | nenhum | correção baricêntrica, relatividade geral e especial |

**A decisão de arquitetura que mais importa** — e que o [`02 §5`](02-a-fisica-do-sinal.md)
já destacou: o Doppler de **duas vias** põe o relógio de referência em Terra.
Um maser de hidrogênio de bancada é incomparavelmente melhor que qualquer
oscilador que caiba numa sonda e sobreviva a 40 anos de radiação. Trocar o
relógio de lugar vale mais que qualquer melhoria de algoritmo.

**O número que dá escala:** o sinal da Voyager 1 chega com potência da ordem de
10⁻¹⁹ W. A antena de 70 m com receptor criogênico e ganho de processamento de
correlação torna isso legível. É o link mais tênue jamais mantido pela
humanidade, e está funcionando desde 1977.

**Onde estudar em detalhe:** o *DSN Telecommunications Link Design Handbook*
(documento 810-005 do JPL) é público e é a referência definitiva de orçamento de
enlace de espaço profundo.

---

## 2 · Radiotelescópios — busca de pulsares e FRBs

### CHIME (Canadá) — o caso que mais se parece com este projeto

Quatro cilindros de 20×100 m, sem partes móveis: o céu passa por cima. Foi
projetado para mapear hidrogênio neutro e virou **a máquina de FRBs do mundo**.

| Parâmetro | `cosmos` | CHIME |
|---|---|---|
| Canais de frequência | 64 | **16 384** |
| Banda | 400–800 MHz | 400–800 MHz (a mesma!) |
| Resolução temporal | 1 ms | ~1 ms |
| DMs testados por busca | 51 | milhares |
| Volume de dados | ~30 MB | **~13 Tb/s** na entrada do correlacionador |
| Hardware | um laptop | centenas de FPGAs e GPUs |

A banda deste projeto foi escolhida igual à do CHIME de propósito: os números de
dispersão que você calcula aqui são os mesmos que a máquina real enfrenta.

**O que eles fazem que aqui não é feito:**

- **Excisão de RFI** — interferência de telefonia, radar, satélites e até fornos
  de micro-ondas. Não é gaussiana: tem caudas pesadíssimas. É a maior fonte de
  falsos positivos e consome mais engenharia que a detecção em si.
- **Dedispersão em tempo real** com algoritmos dedicados (tree dedispersion,
  FDMT) — a busca por força bruta do `plano_dm_tempo` seria inviável.
- **Classificação por aprendizado de máquina** dos candidatos, porque o volume de
  candidatos plausíveis excede a capacidade humana de inspecionar.
- **Confirmação com outro instrumento** antes de qualquer anúncio.

### FAST (China), MeerKAT (África do Sul), SKA (em construção)

FAST é o maior prato único (500 m). MeerKAT é precursor do **SKA**, que quando
completo produzirá algo da ordem de exabytes por ano — e cujo maior desafio
declarado não é a antena: é o **processamento de sinais**.

---

## 3 · Brasil — o que existe e onde entra o ITA

### BINGO — o projeto de maior porte

**BINGO** (*Baryon Acoustic Oscillations from Integrated Neutral Gas
Observations*) está em construção no sertão da Paraíba, no município de Aguiar,
em área escolhida pela baixa interferência eletromagnética.

- **Liderança brasileira:** INPE, UFCG (Universidade Federal de Campina Grande) e
  USP, com parceiros do Reino Unido e da China.
- **Objetivo científico:** mapear a emissão de **hidrogênio neutro** (linha de
  21 cm) e usar as **oscilações acústicas de bárions** como régua padrão para
  medir a expansão do universo — ou seja, atacar energia escura.
- **Status em agosto de 2026:** em construção, com fundação concluída e montagem
  das estruturas dos espelhos em andamento. A previsão mais otimista aponta
  operação experimental em **novembro de 2026**; o cronograma conservador,
  **janeiro de 2027**.
- **Nota de contexto:** em março de 2026, um relatório do Congresso dos EUA
  levantou preocupações sobre a participação da estatal chinesa CETC 54 no
  fornecimento da estrutura. Registro o fato porque ele é público e afeta o
  ambiente do projeto; não afeta a física.

**Por que o BINGO é relevante para este curso:** a técnica dele — *intensity
mapping* de 21 cm — depende inteiramente de calibração e de controle de ruído
sistemático. A equação do radiômetro do [`02 §2`](02-a-fisica-do-sinal.md) é a
ferramenta central de projeto do instrumento.

### Outras frentes

- **INPE** — além do BINGO, opera o **Rádio Observatório de Itapetinga** (Atibaia,
  SP) e mantém programas de clima espacial e monitoramento ionosférico. O
  **EMBRACE** foi um demonstrador brasileiro de tecnologia de agrupamento
  faseado (*phased array*), na linha do SKA.
- **CRAAM / Mackenzie** — rádio-astronomia solar, com instrumentos em altitude
  nos Andes.
- **LLAMA** — projeto Brasil–Argentina de antena de 12 m em Salta, para ondas
  milimétricas e submilimétricas, com foco em VLBI.
- **ON / MCTI** — Observatório Nacional, geodésia espacial e tempo.

### Onde o ITA entra

O **Instituto Tecnológico de Aeronáutica** não é um observatório astronômico —
é uma escola de engenharia aeroespacial, e o processamento de sinais aparece lá
em outra vertente, igualmente exigente:

| Área do ITA | Onde o conteúdo deste projeto se aplica |
|---|---|
| **Telecomunicações espaciais** | orçamento de enlace, modulação, codificação, DSSS — o pipeline `enlace` |
| **Radar** | filtro casado, compressão de pulso por chirp, ambiguidade atraso × Doppler — a mesma matriz de `adquirir` |
| **GNSS e navegação** | aquisição e rastreamento de código PN, cintilação ionosférica — literalmente o mesmo algoritmo do GPS |
| **Guerra eletrônica** | detecção sob ruído, estatística de falso alarme — o `deteccao.py` |
| **Sensoriamento remoto** | SAR (radar de abertura sintética), que é processamento de sinais 2-D |
| **Controle e telemetria de satélite** | filtragem, estimação de estado, Kalman |

**A matriz atraso × Doppler que o `adquirir` produz é, em radar, a "função de
ambiguidade"** — o objeto central do projeto de forma de onda. Mesmo objeto
matemático, dois nomes, duas comunidades.

E há um ponto pouco lembrado: o Brasil tem programa de **lançadores e satélites**
(INPE/AEB, com a família CBERS em parceria com a China e a base de Alcântara). Um
satélite exige, obrigatoriamente, enlace de telemetria e comando — que é
exatamente o pipeline `enlace` deste projeto, com correção de erro por cima.

---

## 4 · O que muda quando a escala aumenta

| Dimensão | Didático | Real | Consequência |
|---|---|---|---|
| Volume | 30 MB | TB/dia a Tb/s | não cabe em memória; processa-se em fluxo |
| Canais | 64 | 10³–10⁴ | dedispersão vira o gargalo; exige algoritmo dedicado |
| Hardware | CPU | FPGA + GPU | o algoritmo é escolhido pelo que o silício faz bem |
| Ruído | gaussiano | **não gaussiano** | limiares teóricos são otimistas; calibra-se empiricamente |
| RFI | inexistente | dominante | mais engenharia que a própria detecção |
| Calibração | perfeita | deriva com temperatura, ganho, apontamento | fontes de calibração e injeção de ruído |
| Validação | teste unitário | **injeção cega de sinal** | equipes de análise às cegas |
| Confirmação | uma execução | outro instrumento, outra equipe | anúncio só depois |

**A diferença mais importante não é computacional: é epistemológica.** Num
exercício, você sabe a resposta. Numa observação real, você não sabe — e todo o
método existe para não se enganar. Daí a injeção cega, a confirmação
independente, o limiar conservador e a desconfiança sistemática do próprio
resultado.

---

## 5 · Se você quiser seguir esse caminho

**Ferramentas reais, todas livres:**

| Ferramenta | Para quê |
|---|---|
| **PRESTO** | busca de pulsares — o pacote mais usado da área |
| **DSPSR / PSRCHIVE** | processamento e arquivamento de dados de pulsar |
| **TEMPO2 / PINT** | timing de precisão, com correção baricêntrica e relativística |
| **GNU Radio** | prototipagem de receptores SDR (ver [`03-instalacao.md`](../03-instalacao.md)) |
| **Astropy** | núcleo de astronomia em Python: tempo, coordenadas, unidades |
| **CASA** | redução de dados de interferometria (ALMA, VLA) |

**Dados públicos reais para praticar:**

- **CHIME/FRB Open Data** — catálogo público de *fast radio bursts*.
- **ATNF Pulsar Catalogue** — parâmetros de milhares de pulsares, incluindo P e DM.
  Use-os para alimentar o `cosmos pulsar --periodo ... --dm ...` com valores reais.
- **NASA PDS** (Planetary Data System) — dados de missões, incluindo rádio-ciência.
- **GNSS-SDR / dados de GPS brutos** — para exercitar aquisição com sinal real.

**Caminho acadêmico no Brasil:** INPE (pós-graduação em Astrofísica e em
Engenharia e Tecnologia Espaciais), ITA (Engenharia Eletrônica, com ênfase em
telecomunicações e radar), USP/IAG, UFRGS, UFCG.

---

## Autoteste

1. Por que a DSN tem três complexos separados por ~120° de longitude?
2. Qual decisão de arquitetura da DSN vale mais que qualquer algoritmo, e por quê?
3. Quantos canais o CHIME usa, e por que tantos?
4. Qual é a maior fonte de falsos positivos numa busca real, e por que ela não
   aparece neste projeto?
5. O que o BINGO pretende medir, e qual equação deste curso é central no projeto dele?
6. Cite três áreas do ITA em que o conteúdo deste projeto se aplica diretamente.
7. Que nome o radar dá à matriz atraso × Doppler?
8. Qual é a diferença epistemológica entre este exercício e uma observação real?

---

## Fontes consultadas

- BINGO: status de construção e cronograma — Governo da Paraíba / FAPESQ e
  cobertura de imprensa, consultado em 19/08/2026. Liderança INPE/UFCG/USP.
- DSN: *DSN Telecommunications Link Design Handbook* (810-005), JPL/NASA.
- CHIME: parâmetros do instrumento conforme documentação pública do projeto.
- Os números de comparação de escala são ordens de grandeza declaradas como tal.
