# 04 · Resultados e validação — o que o código entrega, e como sei que está certo

`Nível: intermediário` · `Executado em: 19/08/2026`
`Base: Python 3.10.12 · NumPy 2.2.6 · SciPy 1.15.3 · Ubuntu 22.04.5`

Todas as saídas deste arquivo são **reais**, copiadas da execução. Onde a medida
não bateu com a teoria, o desacordo está registrado e investigado — inclusive uma
hipótese que testei e **rejeitei** antes de achar a causa certa.

---

## 0 · Suíte de testes

```bash
cd 08-projeto-espacial
python -m unittest discover -s tests
```

```
Ran 56 tests in 0.606s

OK
```

**56 testes, todos passando.** Divididos assim:

| Grupo | Testes | O que verificam |
|---|---|---|
| `TestConstantes` | 3 | valores exatos do SI e a convenção de K_DISPERSAO |
| `TestRuido` | 10 | k·T·B, radiômetro, escalas com √τ e √n_pol, geração |
| `TestDispersao` | 8 | atraso à mão, lei 1/f², ida e volta, dedispersão |
| `TestPulsar` | 8 | perfil circular, folding, sensibilidade ao período |
| `TestDoppler` | 8 | sinais, valores de mão, frequência negativa, deriva |
| `TestAquisicao` | 7 | Golomb, LFSR, aquisição 2-D, acumulação |
| `TestDeteccao` | 6 | valores clássicos de σ, múltiplas tentativas |
| `TestCLI` | 5 | os quatro pipelines rodam e devolvem o código certo |
| **Wall clock** | — | 0,6 s para tudo |

---

## 1 · Radiômetro

```
$ python -m cosmos radiometro
```

```
ORÇAMENTO DE RUÍDO
  receptor (LNA) .........    20.00 K
  céu (fundo + Galáxia) ..     3.00 K
  atmosfera ..............     2.00 K
  solo (spillover) .......     5.00 K
  T_sys TOTAL ............    30.00 K

potência de ruído .......... 4.1419e-14 W   (-103.8 dBm)
largura de banda ........... 100.0 MHz
tempo de integração ........ 60.0 s
amostras independentes ..... 6.000e+09

SENSIBILIDADE (1 sigma) .... 0.2739 mK
  a 5 sigma detecta ........ 1.3693 mK

  tempo p/ detectar  10.000 mK a 5 sigma:        1.1 s  (0.00 h)
  tempo p/ detectar   1.000 mK a 5 sigma:      112.5 s  (0.03 h)
```

**Validação à mão:**

- P = 1,380649×10⁻²³ × 30 × 10⁸ = 4,1419×10⁻¹⁴ W ✓
- ΔT = 30/√(2 × 10⁸ × 60) = 30/√(1,2×10¹⁰) = 30/109 545 = 2,739×10⁻⁴ K ✓
- τ para 1 mK a 5σ = (5×30/10⁻³)²/(2×10⁸) = (1,5×10⁵)²/(2×10⁸) = 112,5 s ✓

**O que ler nesses números:** 41 femtowatts de ruído, e ainda assim conseguimos
resolver 0,27 mK — uma parte em 110 000 do próprio ruído. É integração fazendo o
trabalho, exatamente como a §2 do [`01`](01-o-problema-cientifico.md) descreve.

E repare no custo: detectar 1 mK leva 112 s; detectar 0,1 mK levaria **11 250 s**
(3,1 h). Dez vezes mais fraco, cem vezes mais tempo.

---

## 2 · Dispersão

```
$ python -m cosmos dispersao
```

```
DISPERSÃO INTERESTELAR   (K = 4148.808 MHz² pc⁻¹ cm³ s)
  DM ..................... 50.000 pc·cm⁻³
  banda .................. 400.0 – 800.0 MHz

  atraso entre as pontas . 0.972377 s
  DM recuperado do atraso  50.000000 pc·cm⁻³

  atraso absoluto por canal (em relação a frequência infinita):
      400.0 MHz ->   1.2965 s
      500.0 MHz ->   0.8298 s
      600.0 MHz ->   0.5762 s
      700.0 MHz ->   0.4233 s
      800.0 MHz ->   0.3241 s

  com 64 canais de 6.250 MHz e pulso de 20.0 ms:
    DM máximo sem borrar dentro do canal: 83.3 pc·cm⁻³
```

**Validação à mão:** 4148,808 × 50 × (1/400² − 1/800²) = 4148,808 × 50 ×
4,6875×10⁻⁶ = **0,972377 s** ✓ (o teste exige 9 casas decimais).

**Verificação da lei 1/f²:** 1,2965/0,3241 = 4,0000. Dobrar a frequência divide
o atraso por exatamente 4 ✓

**O aviso que o programa dá:** com esses 64 canais, DM acima de 83,3 borraria o
pulso dentro de cada canal e nenhum processamento posterior o recuperaria. É a
razão de o CHIME usar 16 384 canais.

---

## 3 · Pulsar — o pipeline completo

```
$ python -m cosmos pulsar
```

```
SÍNTESE DA OBSERVAÇÃO
  64 canais × 60000 amostras (60 s a 1.00 ms)
  período 0.714000 s -> 84.0 giros observados
  amplitude do pulso / sigma do ruído = 0.050 (-26.0 dB) — invisível a olho nu

BUSCA EM DM
  51 valores testados de 0 a 100 pc·cm⁻³
  melhor DM .............. 52.00 pc·cm⁻³   (verdadeiro 50.00)
  SNR nesse DM ........... 12.81 sigma
  SNR em DM = 0 .......... 2.42 sigma   <- se este fosse o maior, seria RFI, não astronomia

GANHO DE CADA ETAPA
  somando canais SEM dedispersar ...   2.42 sigma
  com dedispersão correta ..........  12.81 sigma   (5.3× melhor)
  √n_canais (limite teórico) .......   8.00×

VEREDITO ESTATÍSTICO
  tentativas independentes (limite superior) .. 3264
  probabilidade de falso alarme ............... 2.216e-34
  limiar p/ 1 % de falso alarme ............... 4.52 sigma
  >>> DETECÇÃO
```

**O resultado central do projeto está na primeira e na terceira seções:**
um pulso **26 dB abaixo do ruído** em cada canal, individualmente invisível,
detectado a **12,81 σ**.

**Por que o melhor DM saiu 52 e não 50:** a grade tem passo 2, e a curva de
resposta em DM é larga o suficiente para que a flutuação de ruído desloque o
máximo em um passo. Não é erro de código — é a **precisão** da medida, e o
gráfico `curva_dm.png` mostra isso: o pico é claro, mas tem largura. Uma medida
de DM séria ajustaria uma parábola ao pico e citaria uma barra de erro.

**Por que 5,3× e não 8×:** ver a §6 deste arquivo, onde investigo exatamente isso.

### A curva de resposta em DM

O gráfico gerado com `--figuras` mostra a assinatura clássica: pico agudo em
DM ≈ 50, decaindo dos dois lados, e valor baixo em DM = 0.

**É esse formato que distingue astronomia de interferência.** RFI terrestre não
atravessa o meio interestelar, logo não sofre dispersão, logo tem seu máximo em
DM = 0 e decai monotonicamente. Um candidato cujo melhor DM é zero é RFI até
prova em contrário — o teste de triagem mais usado em busca de FRBs, e cabe numa
linha da saída do programa.

---

## 4 · Enlace de espaço profundo

```
$ python -m cosmos enlace
```

```
ENLACE DE ESPAÇO PROFUNDO — banda X (8.42 GHz)
  8,42 GHz — o cavalo de batalha da DSN (Voyager, MRO, Cassini)

DOPPLER
  velocidade radial ...... +20.000 km/s  (afastando)
  desvio de uma via ...... -561.722 kHz
  desvio de duas vias .... -1123.444 kHz
  sensibilidade .......... 28.086 Hz por (m/s)
  velocidade recuperada .. +20000.000 m/s

CÓDIGO PSEUDOALEATÓRIO
  grau do LFSR ........... 10  ->  N = 1023 chips
  autocorrelação: pico 1023, lateral máx -1.000  <- exatamente −1: propriedade de Golomb
  ganho de processamento . 30.10 dB

AQUISIÇÃO com SNR de entrada = -20.0 dB
  períodos acumulados .... 4
  atraso estimado ........ 317 chips   (real 317)
  Doppler estimado ....... +1500.0 Hz   (real +1500.0)
  pico / piso ............ 3.10
  >>> AQUISIÇÃO BEM-SUCEDIDA
```

**Validações à mão:**

- 8,42×10⁹ × 1000/299 792 458 = **28 086,1 Hz por km/s** ✓
- 20 km/s → 561,722 kHz ✓; duas vias → exatamente o dobro ✓
- Velocidade recuperada: 20 000,000 m/s — ida e volta exata ✓
- 10·log₁₀(1023) = **30,0988 dB** ✓
- Autocorrelação lateral **exatamente −1,000** em todos os 1022 atrasos, para
  graus 5 e 10 ✓ — a propriedade de Golomb nº 2, verificada numericamente

**O resultado que importa:** sinal **20 dB abaixo do ruído**, atraso recuperado
com **erro zero** (317 de 317 chips) e Doppler dentro de um passo da grade.

---

## 5 · Limiar de aquisição — quanto de acumulação é preciso

Varredura de SNR de entrada contra número de períodos acumulados:

```
  SNR  -15 dB -> M=1: OK   M=4: OK   M=16: OK
  SNR  -18 dB -> M=1: OK   M=4: OK   M=16: OK
  SNR  -20 dB -> M=1: nao  M=4: OK   M=16: OK
  SNR  -23 dB -> M=1: nao  M=4: OK   M=16: OK
```

(Saída real.) O limiar de um único período fica entre −18 e −20 dB; com quatro
períodos acumulados, −23 dB ainda funciona.

**É exatamente o que acontece quando o GPS do celular "demora para pegar sinal"**:
o receptor está acumulando mais períodos porque o sinal está fraco (dentro de um
prédio, sob folhagem). Aquisição a frio leva mais tempo pela mesma razão.

---

## 6 · O escalonamento com √N — uma investigação honesta

Aqui está a parte mais instrutiva deste arquivo, porque envolveu **rejeitar uma
hipótese antes de achar a causa certa**.

### Primeira medida: parecia errado

A teoria diz que a SNR cresce com √duração e com √n_canais. Medindo com **uma
realização por ponto**:

```
    15 s: SNR   8.59   esperada   8.59   razão 1.000
    30 s: SNR   9.22   esperada  12.14   razão 0.759
    60 s: SNR  15.47   esperada  17.18   razão 0.900
   240 s: SNR  26.44   esperada  34.35   razão 0.770
```

Razões pulando entre 0,76 e 0,90, sem padrão. **Metodologia errada** — a mesma
armadilha do capítulo 20 do curso: uma realização única não estima uma média.

### Segunda medida: Monte Carlo, 12 realizações por ponto

```
== SNR x duração ==
    15 s: SNR =   7.24 +- 1.40   teoria   7.24   razão 1.000
    30 s: SNR =  11.08 +- 1.21   teoria  10.23   razão 1.082
    60 s: SNR =  14.00 +- 1.96   teoria  14.47   razão 0.967
   120 s: SNR =  18.98 +- 2.58   teoria  20.47   razão 0.927

== SNR x n_canais ==
     4 canais: SNR =   4.86 +- 1.05   teoria   4.86   razão 1.000
    16 canais: SNR =   7.87 +- 1.29   teoria   9.71   razão 0.811
    64 canais: SNR =  13.55 +- 1.97   teoria  19.42   razão 0.698
   256 canais: SNR =  25.94 +- 2.35   teoria  38.85   razão 0.668
```

Com a duração, as razões oscilam em torno de 1 dentro da barra de erro — **√τ
confirmado**. Mas com os canais o desvio é **monotônico**: 1,00 → 0,81 → 0,70 →
0,67. Monotônico não é ruído. Havia algo real.

### Hipótese 1 (rejeitada): contaminação da linha de base

Suspeitei que, com SNR alta, as asas do pulso entrassem na região usada para
estimar a linha de base, inflando o desvio padrão. Testei variando o parâmetro
`fracao_pulso`:

```
  fracao_pulso=0.15: razões = 1.000 0.811 0.698 0.668
  fracao_pulso=0.30: razões = 1.000 0.831 0.716 0.687
  fracao_pulso=0.50: razões = 1.000 0.825 0.711 0.671
```

**Praticamente nenhuma mudança. Hipótese rejeitada.**

### Hipótese 2 (confirmada): o estimador tem um piso

Medi a SNR que o estimador reporta em **ruído puro**, com `amplitude_pulso = 0`:

```
== SNR medida em RUÍDO PURO ==
  média 3.22 +- 0.71  <- este é o PISO do estimador, sem sinal nenhum
```

**Aí está.** O estimador `(máximo − base) / σ_base` reporta **3,22 σ mesmo sem
sinal nenhum**, porque o máximo de 64 bins de ruído gaussiano já fica ~3 σ acima
da média por puro acaso. Não é defeito do código: é propriedade da **estatística
de valores extremos**.

O ponto de referência (4 canais, SNR 4,86) estava, portanto, **inflado**: quase
todo o seu valor era o piso. Corrigindo por soma em quadratura,
SNR_real = √(SNR_medida² − piso²):

```
     4 canais: bruta   4.86  corrigida   3.64   teoria   3.64   razão 1.000
    16 canais: bruta   7.87  corrigida   7.19   teoria   7.27   razão 0.988
    64 canais: bruta  13.55  corrigida  13.16   teoria  14.55   razão 0.905
   256 canais: bruta  25.94  corrigida  25.74   teoria  29.09   razão 0.885
```

De 0,67 para **0,885–1,00**. O grosso do desvio era o viés do estimador.

### O que sobra, e o que isso ensina

Sobram ~10 % de déficit em contagens altas de canais, provavelmente porque o
pulso ocupa vários bins de fase e o pico de um único bin não captura toda a
energia (a soma correta pesaria os bins pelo perfil — é o que um filtro casado em
fase faria). Fica registrado como limitação conhecida.

**Três lições, e valem para qualquer trabalho experimental:**

1. **Valide com Monte Carlo, não com uma realização.** Uma medida com barra de
   erro de 20 % não confirma nem refuta um desvio de 10 %.
2. **Meça o piso do seu estimador com sinal zero.** Todo estimador de SNR baseado
   em máximo tem viés positivo. Se você não conhece o piso, vai chamar ruído de
   detecção — e é literalmente por isso que buscas de pulsar exigem 8–10 σ e não 3.
3. **Uma hipótese plausível pode estar errada.** A contaminação da linha de base
   era razoável, e o teste a matou em uma execução. Testar é mais barato que
   argumentar.

---

## 7 · Tabela-resumo da validação

| Grandeza | Valor de mão / teoria | Medido | Confere |
|---|---|---|---|
| P = k·T·B (30 K, 100 MHz) | 4,14190×10⁻¹⁴ W | idem | ✓ exato |
| ΔT_min (30 K, 100 MHz, 60 s, 2 pol) | 2,739×10⁻⁴ K | idem | ✓ exato |
| τ para 1 mK a 5σ | 112,5 s | 112,5 s | ✓ exato |
| Atraso DM=50, 400↔800 MHz | 0,9723768750 s | idem | ✓ 9 casas |
| Lei 1/f² (400 vs 800 MHz) | 4,0000 | 4,0000 | ✓ exato |
| DM recuperado do atraso | 50,000000 | 50,000000 | ✓ exato |
| Doppler banda X por km/s | 28 086,1 Hz | idem | ✓ exato |
| Doppler duas vias / uma via | 2,0 | 2,0 | ✓ exato |
| Autocorrelação lateral (grau 5 e 10) | −1 exato | −1,000 ± 10⁻⁶ | ✓ |
| Balanceamento de Golomb (grau 10) | 512 uns | 512 | ✓ exato |
| Ganho de processamento N=1023 | 30,0988 dB | idem | ✓ exato |
| P(falso alarme), 5σ, 1 tentativa | 2,8665×10⁻⁷ | idem | ✓ 10 casas |
| P(falso alarme), 5σ, 10⁶ tentativas | ~25 % | 24,9 % | ✓ |
| SNR ∝ √τ | razão 1,0 | 0,93–1,08 | ✓ dentro do erro |
| SNR ∝ √n_canais | razão 1,0 | 0,885–1,00 (corrigida) | ~ ver §6 |
| Atraso de código recuperado a −20 dB | 317 chips | 317 | ✓ exato |

---

## Autoteste

1. Confira à mão que ΔT = 30/√(2×10⁸×60) dá 2,739×10⁻⁴ K.
2. Por que detectar um sinal 10× mais fraco custa 100× mais tempo?
3. O melhor DM saiu 52 e o verdadeiro era 50. Isso é erro de código? Justifique.
4. Como o formato da curva SNR × DM separa astronomia de interferência?
5. Por que a primeira medição de escalonamento parecia errada?
6. Qual hipótese foi rejeitada, e como o teste a rejeitou em uma execução?
7. Por que um estimador de SNR baseado em máximo tem piso maior que zero?
8. Que valor esse piso teve, e por que ele explica o desvio observado?
9. Por que buscas de pulsar exigem 8–10 σ em vez de 3 σ?
