# Projeto-modelo II — `cosmos`: sinais do espaço profundo

`Nível: intermediário → avançado` · `Executado e verificado em: 19/08/2026`
`Base: Python 3.10.12 · NumPy 2.2.6 · SciPy 1.15.3 · Matplotlib 3.10.9 · Ubuntu 22.04.5`
`Estado: ✅ COMPLETO — 56 testes passando, 4 pipelines executando`

Segundo projeto-modelo do curso de [Processamento de Sinais](../00-MAPA.md), voltado
à **pesquisa cósmica e espacial** — o tipo de processamento feito no JPL/NASA, nos
radiotelescópios, no INPE e nas disciplinas de telecomunicações e sensoriamento
do ITA.

O primeiro projeto ([`07-projeto-modelo/`](../07-projeto-modelo/README.md)) ensina
o **ofício**: amostragem, FFT, filtros, estimação de frequência. Este ensina o
**propósito**: por que alguém aponta uma antena para o céu, o que exatamente ela
mede, e como se extrai ciência de um sinal que chega **muito abaixo do ruído**.

---

## A pergunta que este projeto responde

> Um sinal que viajou 1000 anos-luz chega à antena com potência de 10⁻²⁶ W/m²/Hz,
> **enterrado dezenas de decibéis abaixo do ruído térmico do próprio receptor**.
> Como é possível não só detectá-lo, mas medir dele a distância da fonte, a
> velocidade da nave, a densidade de elétrons do espaço interestelar e o período
> de rotação de uma estrela de nêutrons?

A resposta curta: **integração coerente**. O ruído soma-se de forma incoerente
(cresce com √N) e o sinal de forma coerente (cresce com N). A razão cresce com √N,
e N pode ser 10⁶. Esse é o truque que sustenta toda a astronomia de rádio e toda a
comunicação de espaço profundo — e é o fio condutor deste projeto.

---

## Os quatro problemas reais que o projeto resolve

Cada um é um comando da CLI, com física verdadeira e verificação contra valor conhecido.

### 1 · Radiômetro — quanto ruído existe e o que dá para ver através dele

**Finalidade científica.** Antes de detectar qualquer coisa, um radioastrônomo
precisa saber o **piso**. A equação do radiômetro,

```
ΔT_min = T_sys / √(B·τ)
```

diz a menor variação de temperatura de antena detectável com largura de banda `B`
e tempo de integração `τ`. Ela decide **quanto tempo de telescópio** um projeto
precisa — ou seja, decide orçamento, e é por isso que aparece em toda proposta de
observação submetida a ALMA, VLA ou FAST.

**O que ensina de DSP:** ruído gaussiano, densidade espectral de potência,
integração como filtro passa-baixa, e por que √(B·τ) e não B·τ.

### 2 · Dispersão interestelar — medir a densidade do espaço vazio

**Finalidade científica.** O meio interestelar é um plasma tênue. Um pulso de rádio
que o atravessa chega **mais tarde nas frequências baixas**, com atraso

```
Δt = 4,148808×10³ · DM · (1/f₁² − 1/f₂²) segundos      [f em MHz]
```

onde **DM** (*dispersion measure*) é a coluna de elétrons livres entre nós e a
fonte, em pc·cm⁻³. Medindo o atraso, mede-se o DM; com um modelo da Galáxia,
converte-se DM em **distância**. É assim que se estima a que distância está um
pulsar — e foi assim que se mostrou que as *fast radio bursts* vêm de fora da
Via Láctea, resultado que rendeu grande parte da radioastronomia da última década.

**O que ensina de DSP:** atraso dependente da frequência (fase não linear com uma
causa física), banco de canais, e **dedispersão** — que é literalmente aplicar o
atraso inverso, canal a canal.

### 3 · Pulsar — extrair um sinal periódico enterrado no ruído

**Finalidade científica.** Um pulsar é uma estrela de nêutrons que gira com
regularidade de relógio atômico. Cada pulso individual é invisível: some no ruído.
Somando (**folding**) milhares de rotações no período correto, o perfil emerge.
Pulsares de milissegundo são hoje usados como uma rede de relógios espalhada pela
Galáxia (*Pulsar Timing Arrays*) para detectar ondas gravitacionais de baixíssima
frequência — a evidência anunciada em 2023 por NANOGrav, EPTA, PPTA e CPTA.

**O que ensina de DSP:** integração coerente, filtro casado, ganho de processamento
√N, busca em grade de parâmetros (período × DM), e estatística de detecção
(limiar, taxa de falso alarme, número de tentativas independentes).

### 4 · Enlace de espaço profundo — falar com uma sonda

**Finalidade científica.** A Deep Space Network da NASA recebe da Voyager 1, a mais
de 24 bilhões de km, um sinal de potência recebida da ordem de 10⁻¹⁹ W. Isso só
funciona com três coisas: antena enorme, **código pseudoaleatório** correlacionado
no receptor, e rastreamento do **Doppler**. E o Doppler não é só um problema a
corrigir: ele **é o instrumento** — o rastreamento Doppler de duas vias mede a
velocidade da sonda com precisão de fração de mm/s, e foi assim que se pesaram
luas e se mapeou o campo gravitacional de planetas.

**O que ensina de DSP:** correlação como detector ótimo, sequências PN geradas por
LFSR, deriva de frequência e rampa Doppler, aquisição em grade
tempo × frequência, e por que o GPS funciona.

---

## Instalar e rodar — comandos exatos

```bash
cd processamento-de-sinais/08-projeto-espacial

python3 -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python -m unittest discover -s tests  # deve dar 56 OK
```

Os quatro pipelines:

```bash
python -m cosmos radiometro                      # sensibilidade e orçamento de ruído
python -m cosmos dispersao  --dm 50              # atraso do plasma interestelar
python -m cosmos pulsar     --figuras saida/     # detecção completa de pulsar
python -m cosmos enlace     --figuras saida/     # Doppler + aquisição de código PN
```

### O resultado que resume o projeto

```
$ python -m cosmos pulsar

  amplitude do pulso / sigma do ruído = 0.050 (-26.0 dB) — invisível a olho nu
  ...
  somando canais SEM dedispersar ...   2.42 sigma
  com dedispersão correta ..........  12.81 sigma   (5.3× melhor)
  ...
  probabilidade de falso alarme ............... 2.216e-34
  >>> DETECÇÃO
```

Um pulso **26 dB abaixo do ruído**, individualmente invisível, detectado a
12,81 σ — porque 84 rotações da estrela foram somadas em fase, e 64 canais de
frequência foram realinhados antes. Saídas completas e validação em
[`04-resultados-e-validacao.md`](04-resultados-e-validacao.md).

---

## Roteiro de leitura

| Se você quer... | Leia nesta ordem |
|---|---|
| **Entender a finalidade** (por que isso existe) | `README` → `01` → `05` |
| **Entender a física** | `01` → `02` → `04` |
| **Entender o código** | `03` com o `.py` aberto ao lado → `04` |
| **Praticar** | `06`, do nível 1 ao 4 |
| **Caminho completo** | `01` → `02` → `03` → `04` → `05` → `06` |

Pré-requisitos do curso principal: capítulos [10](../10-fundamentos.md) (LTI e
convolução), [14](../14-fourier.md) (propriedades), [16](../16-dft-e-fft.md)
(DFT/FFT) e [20](../20-analise-espectral-e-janelas.md) (estimação espectral).
A matemática necessária está em [`12-matematica-do-zero.md`](../12-matematica-do-zero.md).

---

## Estrutura

```
08-projeto-espacial/
├── README.md                         você está aqui — mapa e finalidade científica
├── 01-o-problema-cientifico.md       a ciência: o que se quer descobrir e por quê
├── 02-a-fisica-do-sinal.md           de onde vem cada fórmula, e quando ela falha
├── 03-o-codigo-linha-a-linha.md      cada função explicada, com a matemática ao lado
├── 04-resultados-e-validacao.md      saídas reais e a investigação de um desacordo
├── 05-como-as-instituicoes-fazem.md  DSN, CHIME, BINGO, INPE, ITA
├── 06-exercicios.md                  quatro níveis, do reproduzir ao investigar
├── requirements.txt
├── cosmos/
│   ├── __init__.py
│   ├── constantes.py       constantes físicas, com fonte e unidade declaradas
│   ├── ruido.py            ruído térmico, T_sys, equação do radiômetro
│   ├── dispersao.py        atraso do plasma, dedispersão incoerente
│   ├── pulsar.py           síntese, folding de época, perfil, SNR, busca
│   ├── doppler.py          desvio, rampa, correção, medida de velocidade
│   ├── aquisicao.py        LFSR, sequências PN, aquisição por correlação 2-D
│   ├── deteccao.py         limiar, falso alarme, penalidade de múltiplas buscas
│   ├── graficos.py         cascata, perfil dobrado, curva de DM, plano de aquisição
│   └── __main__.py         CLI: radiometro | dispersao | pulsar | enlace
└── tests/
    └── test_cosmos.py      56 testes contra valores calculáveis à mão
```

---

## Princípio de projeto deste código

**Toda função devolve uma grandeza física com unidade declarada, e todo teste
compara com um valor que se pode calcular à mão.** Em pesquisa espacial não
existe "parece certo": existe fechar com a teoria dentro da barra de erro. É por
isso que a suíte verifica que o atraso de dispersão bate em 9 casas decimais e
que a autocorrelação do código PN vale exatamente −1 — números que vêm de
fórmula publicada, não de execução anterior.

Um teste que só compara com "o que o código deu ontem" não protege contra erro de
constante nem de unidade. E erro de unidade já derrubou sonda: o Mars Climate
Orbiter se perdeu em 1999 por libra-força-segundo contra newton-segundo.

---

## O que este projeto descobriu ao ser validado

A [§6 do `04`](04-resultados-e-validacao.md) documenta uma investigação real: o
escalonamento da SNR com o número de canais parecia violar a lei √N. A primeira
hipótese (contaminação da linha de base) foi **testada e rejeitada**. A causa
verdadeira era outra — o estimador de SNR tem **piso de 3,22 σ mesmo em ruído
puro**, porque o máximo de 64 bins gaussianos já fica ~3 σ acima da média por
acaso.

Fica registrado com o percurso completo do diagnóstico, porque é assim que
validação funciona de verdade, e porque a lição é geral: **todo estimador de SNR
baseado em máximo tem viés positivo, e quem não mede o piso chama ruído de
detecção.**

---

## Autoteste conceitual

1. Por que a razão sinal-ruído cresce com √N e não com N?
2. O que a equação do radiômetro decide, na prática, num projeto de observação?
3. Como um atraso de chegada vira uma medida de distância?
4. Por que um pulso isolado de pulsar é invisível e mil deles não são?
5. Em que sentido o Doppler é instrumento e não problema?
6. Por que um candidato cujo melhor DM é zero é suspeito?
7. Por que "5 sigma" pode não significar nada?
