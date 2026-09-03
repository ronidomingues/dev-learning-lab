# 21 · Multitaxa e bancos de filtros — mudar a taxa sem estragar o sinal

`Nível: intermediário → avançado` · `Medições feitas em: 19/08/2026`
`Base: SciPy 1.15.3`

Processamento multitaxa é a arte de trabalhar com **mais de uma taxa de
amostragem dentro do mesmo sistema**. Parece um detalhe de conversão de formato.
Não é: é o que torna viável quase todo sistema real de DSP, porque **processar na
taxa mais baixa possível é a maior economia disponível**.

---

## 1 · As duas operações elementares

### Decimação (baixar a taxa por M)

Duas etapas, **nesta ordem**:

1. **Filtrar** passa-baixa em fs/(2M) — o anti-aliasing digital.
2. **Descartar** M−1 de cada M amostras.

Inverter a ordem é o erro clássico, e ele não dá erro nenhum:

```python
import numpy as np
from scipy import signal
fs = 8000; t = np.arange(fs)/fs
x = np.sin(2*np.pi*300*t) + 0.5*np.sin(2*np.pi*3000*t)

def pico(v, f):
    X = np.abs(np.fft.rfft(v)); fr = np.fft.rfftfreq(len(v), 1/f)
    return sorted([round(float(fr[i]), 1) for i in np.argsort(X)[-2:]])

print("original a 8000 Hz .............", pico(x, 8000))
print("x[::4] SEM filtro (2000 Hz) ....", pico(x[::4], 2000))
print("decimate(x,4) COM filtro .......", pico(signal.decimate(x, 4, ftype='fir'), 2000))
```

Saída real:

```
original a 8000 Hz ............. [300.0, 3000.0]
x[::4] SEM filtro (2000 Hz) .... [300.0, 1000.0]  <- 3000 Hz virou alias
decimate(x,4) COM filtro ....... [300.0, 827.0]
```

**O tom de 3000 Hz virou 1000 Hz.** A nova Nyquist é 1000 Hz; 3000 = 4×1000 − 1000
dobra para 1000. Nenhum aviso, nenhuma exceção — só um número errado.
Com `decimate`, o tom some (o segundo pico vira ruído em 827 Hz).

**Regra:** nunca `x[::M]`. Sempre `signal.decimate(x, M)`.

### Interpolação (subir a taxa por L)

Também duas etapas, nesta ordem:

1. **Inserir** L−1 zeros entre amostras (*upsampling*).
2. **Filtrar** passa-baixa em fs/(2L), com ganho L.

**Por que inserir zeros e não repetir a amostra:** inserir zeros *não altera* o
espectro — apenas cria **imagens** (cópias) do espectro original em múltiplos da
taxa antiga. O filtro remove as imagens. Repetir a amostra seria aplicar um
sample-and-hold, que multiplica o espectro por uma sinc e introduz o *droop*
de [`15 §7`](15-amostragem-e-quantizacao.md).

**Por que o ganho L:** ao inserir zeros, a energia média cai por L. O filtro com
ganho L a devolve.

### Taxa racional L/M

Para 44,1 kHz → 48 kHz: L/M = 160/147. Interpola por 160, filtra, decima por 147.

**Nunca faça as duas etapas de filtro:** um único filtro passa-baixa com corte em
min(fs/2L, fs/2M) serve para as duas funções. É o que `resample_poly` faz.

---

## 2 · A identidade nobre e o ganho polifásico

### O desperdício óbvio

Ao decimar por M, você filtra tudo e depois joga fora M−1 de cada M saídas.
**Calculou e jogou fora.**

```python
fs, M = 48000, 4
h = signal.firwin(241, fs/(2*M), fs=fs)
```

```
filtrar a 48 kHz e depois decimar por 4: 241 mult/amostra de ENTRADA
polifásico (só calcula o que sobrevive):  60 mult/amostra de entrada -> ganho 4×
```

### A decomposição polifásica

Divida os coeficientes do filtro em M subfiltros, pegando um a cada M:

```
h = [h0 h1 h2 h3 h4 h5 h6 h7 ...]        M = 4

E0 = [h0 h4 h8 ...]      E1 = [h1 h5 h9 ...]
E2 = [h2 h6 h10 ...]     E3 = [h3 h7 h11 ...]
```

Cada subfiltro tem N/M coeficientes e roda na taxa **baixa**. O ganho é exatamente
M, e ele é **estrutural**: nenhuma aproximação, mesmo resultado, M vezes menos
operações.

### As identidades nobres

```
  x ──►[ H(z^M) ]──►[ ↓M ]──►  ≡  ──►[ ↓M ]──►[ H(z) ]──►
  x ──►[ ↑L ]──►[ H(z^L) ]──►  ≡  ──►[ H(z) ]──►[ ↑L ]──►
```

Traduzindo: **um filtro que só usa coeficientes espaçados de M pode ser movido
para o lado de baixa taxa**. É o teorema que justifica o polifásico, e é a razão
de "identidade nobre" ser um nome sério na literatura.

### Conversão em vários estágios

Decimar por 100 de uma vez exige um filtro com transição de 1/200 da taxa —
milhares de taps ([`18 §3`](18-filtros-fir.md)). Decimar por 10, depois por 10 de
novo, exige dois filtros muito mais curtos.

**Regra prática:** fatore M em estágios, começando pelo fator maior. Reduções de
custo de 5 a 20× são rotina. É por isso que todo conversor sigma-delta decima em
cascata.

---

## 3 · O filtro CIC — decimação sem multiplicador

Cascata de N integradores na taxa alta, um decimador, e N diferenciadores na taxa
baixa. **Nenhuma multiplicação**: só somas e subtrações.

```
  ─►[∫]─►[∫]─►[∫]─►[ ↓R ]─►[Δ]─►[Δ]─►[Δ]─►
     N integradores        N comb (diferenciadores)
```

Resposta em magnitude:

```
|H(f)| = | sen(πRf) / (R·sen(πf)) |^N
```

Medido:

```
  R= 8 N=1: droop na borda  -0.90 dB | pior alias  -10.33 dB
  R= 8 N=3: droop na borda  -2.69 dB | pior alias  -30.99 dB
  R= 8 N=5: droop na borda  -4.49 dB | pior alias  -51.64 dB
  R=32 N=3: droop na borda  -2.73 dB | pior alias  -31.34 dB
```

(Saída real. "Banda útil" = metade da nova Nyquist; "pior alias" = pior caso da
faixa que dobra para dentro dela.)

**Leia a tabela como projeto:**

- Cada estágio N acrescenta ~**10,3 dB** de rejeição de alias. Linear em N,
  e barato.
- Cada estágio também acrescenta ~**0,9 dB** de *droop* na borda da banda. É o
  preço, e é previsível.
- **O droop quase não depende de R** (2,69 dB para R=8, 2,73 para R=32): ele é
  determinado por N e pela fração da banda que você usa.

**Por isso o CIC domina o front-end:** em ASIC/FPGA, multiplicador custa área e
energia; somador não. O CIC decima por 32 ou 64 logo na entrada, sem multiplicar,
e um FIR curto na taxa baixa corrige o droop e faz o corte fino.

⚠️ **A armadilha do CIC:** os integradores têm polo em z=1 (ganho infinito em DC)
e **transbordam por projeto**. Só funciona porque a aritmética é de complemento de
dois com largura suficiente (B_saída ≥ B_entrada + N·log₂R bits) e o transbordo se
cancela exatamente no comb. Implementar CIC em ponto flutuante ou com saturação
**quebra** essa propriedade. É um dos raros lugares em que *overflow* é correto.

---

## 4 · Bancos de filtros

Um **banco de filtros** divide o sinal em sub-bandas, processa cada uma, e
reconstrói.

```
        ┌─►[H0]─►[↓M]─► sub-banda 0 ─►[↑M]─►[G0]─┐
  x ────┼─►[H1]─►[↓M]─► sub-banda 1 ─►[↑M]─►[G1]─┼──►(+)──► x̂
        └─►[H2]─►[↓M]─► sub-banda 2 ─►[↑M]─►[G2]─┘
          análise                       síntese
```

**Por que fazer isso:**

| Aplicação | Motivo |
|---|---|
| MP3, AAC, Opus | quantizar cada banda conforme a sensibilidade do ouvido |
| JPEG2000 | wavelets = banco de filtros em cascata |
| Cancelamento de eco | adaptar um filtro curto por banda em vez de um longo |
| Equalizador gráfico | ganho por banda |
| Rádio por canais | separar canais adjacentes |

### Reconstrução perfeita

O desafio: cada sub-banda é decimada, logo sofre aliasing. Um banco de
**reconstrução perfeita** escolhe H e G de modo que os aliases das bandas
vizinhas **se cancelem exatamente** na soma.

| Família | Propriedade |
|---|---|
| **QMF** (Quadrature Mirror Filters) | 2 bandas; cancela alias; reconstrução quase perfeita |
| **CQF / ortogonal** | reconstrução perfeita e ortogonalidade (Daubechies) |
| **MDCT** | usada em MP3/AAC/Vorbis; *lapped transform* com reconstrução perfeita |
| **Cosseno modulado** | M bandas a partir de um protótipo único |

A **MDCT** merece nota: ela produz **metade** dos coeficientes que amostras de
entrada (crítica em amostragem) e ainda assim reconstrói perfeitamente, graças
ao *time-domain alias cancellation* — o alias de um bloco cancela com o do bloco
vizinho na sobreposição. É a peça central de praticamente todo codec de áudio
moderno, e é multitaxa puro.

---

## 5 · Onde multitaxa aparece sem você perceber

| Sistema | Uso |
|---|---|
| Conversor sigma-delta | decimação em cascata de 64× a 256×, começando por CIC |
| DAC de áudio | sobreamostragem 8× antes do conversor, para filtro analógico simples |
| Receptor SDR | decimação da taxa de ADC (dezenas de MHz) para a do sinal (kHz) |
| Codec de voz | processa em 8 kHz o que foi capturado em 48 kHz |
| Reverberação, análise de fala | processa em banda estreita para economizar |
| Espectrograma | o *hop* é uma decimação disfarçada |

**A economia real:** processar áudio de voz em 8 kHz em vez de 48 kHz é 6× menos
operações — e a fala não tem informação útil acima de 4 kHz. Multitaxa é a
diferença entre caber e não caber no orçamento de CPU.

---

## Os cinco porquês: por que inserir zeros e não repetir amostras?

1. **Por que zeros?** Porque inserir zeros **não muda o espectro**; só o replica.
2. **Por que não muda?** Porque a soma da DTFT sobre a sequência com zeros é
   idêntica à original — os zeros não contribuem com nada. O que muda é a
   *interpretação* do eixo: a mesma sequência agora dura L vezes mais, então o
   espectro aparece comprimido e repetido L vezes.
3. **Por que repetir a amostra seria pior?** Porque repetir equivale a convoluir
   com um pulso retangular de L amostras, cujo espectro é uma sinc. Você
   multiplica o espectro por essa sinc — atenua o topo da banda e não remove
   direito as imagens.
4. **Por que a sinc é ruim aqui?** Porque ela cai só com 1/f: as imagens ficam
   atenuadas, mas não o suficiente, e a banda útil sofre *droop*.
5. **Então o filtro depois dos zeros é obrigatório?** Sim, e ele *é* o interpolador.
   O que ele faz, exatamente, é reconstruir os valores que deveriam estar no lugar
   dos zeros — no limite ideal, com a sinc do teorema da amostragem.
   **Parada legítima: é o teorema da amostragem aplicado ao caso discreto.**
   Interpolar corretamente é reconstruir, e reconstruir é filtrar.

---

## Autoteste

1. Por que `x[::4]` está errado e o que acontece exatamente com um tom de 3 kHz?
2. Qual a ordem correta das duas etapas de decimação? E de interpolação?
3. Explique o ganho polifásico: de onde vêm os 4× medidos?
4. O que dizem as identidades nobres, em uma frase?
5. Por que decimar por 100 em dois estágios é mais barato que em um?
6. Quanto de rejeição de alias cada estágio de CIC acrescenta, e a que custo?
7. Por que o CIC transborda de propósito, e por que isso é correto?
8. O que a MDCT consegue que uma DFT com sobreposição não consegue?
9. Por que se insere zeros em vez de repetir a amostra?
