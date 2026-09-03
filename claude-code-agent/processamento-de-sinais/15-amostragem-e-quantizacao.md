# 15 · Amostragem e quantização — a ponte entre os dois mundos

`Nível: intermediário` · `Atualizado em: 14/08/2026`

Este é o capítulo que mais separa quem sabe de quem acha que sabe. Praticamente
todo bug irreparável de um sistema de sinais nasce aqui — e é irreparável porque
informação perdida na aquisição não volta, por mais sofisticado que seja o
processamento depois.

---

## 1 · Amostragem: o teorema

**Enunciado (Nyquist–Shannon–Kotelnikov).** Se x(t) é limitado em banda, com
X(f) = 0 para |f| > B, então x(t) é **completamente determinado** pelas amostras
tomadas a fs > 2B, e pode ser reconstruído exatamente por:

```
x(t) = Σ_n x[n]·sinc((t − nT)/T),        T = 1/fs
```

Três palavras que carregam tudo:

- **"limitado em banda"** — a hipótese. Nenhum sinal real é rigorosamente limitado
  em banda (um sinal de duração finita não pode ser, por dualidade). Na prática,
  força-se com um filtro anti-aliasing analógico.
- **"> 2B"** — estritamente maior. Em fs = 2B exato, uma senoide em exatamente B Hz
  pode ser amostrada toda vez no zero e sumir.
- **"exatamente"** — não é aproximação. É igualdade, com a interpolação sinc.

**fs/2 é a frequência de Nyquist.** 2B é a *taxa* de Nyquist. Livros trocam os dois
nomes o tempo todo; ao ler, confira pelo contexto.

### Por que funciona — a explicação em uma linha

Amostrar = multiplicar por um pente de impulsos. Multiplicar no tempo = **convoluir
na frequência** ([`14 §4`](14-fourier.md)). O espectro do pente é outro pente,
espaçado de fs. Logo, o espectro amostrado é o espectro original **repetido a cada
fs**:

```
        espectro original            espectro depois de amostrar
                                   ...  ╱‾╲   ╱‾╲   ╱‾╲  ...
             ╱‾╲                       ╱   ╲ ╱   ╲ ╱   ╲
      ──────╱───╲──────           ────╯     X     X     ╰────
          -B  0  B                   -fs    0    fs
```

Se as cópias **não** se sobrepõem (fs > 2B), basta um passa-baixa para recuperar a
original: nada se perdeu. Se elas se sobrepõem, as partes somadas ficam
inseparáveis para sempre. **Isso é aliasing.**

---

## 2 · Aliasing: a fórmula do dobramento

Uma frequência f, amostrada a fs, aparece em:

```
f_alias = |f − fs·round(f/fs)|
```

```python
import numpy as np
fs = 1000
for fr in [100, 400, 600, 900, 1400, 1600]:
    print(f"  {fr:5d} Hz -> {abs(fr - fs*round(fr/fs)):5.0f} Hz")
```

Saída real:

```
    100 Hz ->   100 Hz
    400 Hz ->   400 Hz
    600 Hz ->   400 Hz
    900 Hz ->   100 Hz
   1400 Hz ->   400 Hz
   1600 Hz ->   400 Hz
```

Visualmente, o eixo de frequência **dobra como um acordeão** em 0 e em fs/2:

```
verdadeiro:  0 ──── 250 ──── 500 ──── 750 ──── 1000 ──── 1250 ...
aparente:    0 ──── 250 ──── 500 ──── 250 ────    0 ────  250 ...
                                 ↑                  ↑
                             Nyquist              fs
```

### Como aliasing aparece na vida real

| Sintoma | Onde |
|---|---|
| roda de carroça girando para trás | cinema, 24 quadros/s |
| moiré em tecido listrado | foto digital (aliasing **espacial**) |
| som "metálico" ou tons fantasma | áudio mal reamostrado, síntese ingênua |
| escada em linha diagonal | gráficos sem antialiasing |
| leitura de rotação errada | tacômetro estroboscópico |
| "batimento" que não existe | vibração de máquina medida com taxa baixa |

**Nunca há mensagem de erro.** O sistema devolve, com convicção, uma frequência
que não existe. Este é o ponto mais importante do capítulo.

### A defesa: filtro anti-aliasing

Um filtro analógico **antes** do conversor A/D, cortando acima de fs/2. Tem de ser
analógico: depois de amostrar já é tarde.

E aqui está a razão de os 44,1 kHz não serem 40 kHz: um filtro analógico não corta
em vertical. Precisa de espaço para a transição entre 20 kHz (fim da banda útil) e
22,05 kHz (Nyquist). **A folga entre 2B e fs é o orçamento de transição do filtro.**

Quanto mais folga, mais barato o filtro. É por isso que conversores modernos usam
**sobreamostragem**: amostrar a 64× e filtrar em digital, onde filtro é barato,
permite um anti-aliasing analógico de 1ª ordem, quase de graça.

---

## 3 · Amostragem passa-faixa (bandpass sampling)

Uma sutileza que quase todo curso omite e que vale ouro em rádio.

Se o sinal ocupa a faixa [f₁, f₂] com largura B = f₂ − f₁, você **não** precisa de
fs > 2f₂. Basta fs > 2B, desde que a taxa seja escolhida para as cópias caírem em
lugares livres. Faixas válidas:

```
2f₂/(m+1) ≤ fs ≤ 2f₁/m,     para m inteiro, 1 ≤ m ≤ ⌊f₂/B⌋
```

**Exemplo.** Um sinal de FM comercial em 100–100,2 MHz tem B = 200 kHz. Amostrar a
2×100,2 MHz = 200,4 MHz seria caro e desnecessário. Com bandpass sampling, ~500 kHz
bastam — e o aliasing, em vez de defeito, é usado **de propósito** para trazer o
sinal para banda-base. Chama-se *undersampling* ou *subamostragem intencional*.

O preço: o *jitter* do relógio passa a ser julgado pela frequência **da portadora**,
não pela taxa (§6), e o ruído de todas as faixas dobradas se soma na banda útil —
por isso um filtro passa-faixa de entrada continua obrigatório.

---

## 4 · Quantização

Arredondar cada amostra para um de 2^B níveis. Passo Δ = FS/2^B, onde FS é o fundo
de escala.

**Modelo padrão:** o erro de quantização e[n] = q[n] − x[n] é tratado como ruído
uniforme em [−Δ/2, Δ/2], de variância Δ²/12. Disso sai:

```
SNR_max = 6,02·B + 1,76 dB          (para senoide de fundo de escala)
```

Verificado experimentalmente no exemplo 9 de [`06`](06-exemplos.md): 26,2 / 49,9 /
98,1 dB medidos contra 25,8 / 49,9 / 98,1 teóricos, para 4, 8 e 16 bits.

| Bits | SNR | Onde se usa |
|---|---|---|
| 8 | 49,9 dB | telefonia antiga (μ-law dá ~equivalente a 12 lineares) |
| 12 | 74 dB | instrumentação, microcontrolador |
| 16 | 98 dB | CD, áudio de consumo |
| 24 | 146 dB (teórico) | estúdio — na prática o ruído analógico limita em ~120 dB |
| 32 float | ~1500 dB de faixa | processamento interno; **não** existe conversor assim |

⚠️ **24 bits reais não existem.** Nenhum conversor comercial entrega 146 dB; o
ruído térmico do próprio circuito domina bem antes. A especificação honesta é
**ENOB** (bits efetivos), tipicamente 19–21 num "conversor de 24 bits". Fabricante
que só publica "24 bits" está vendendo o tamanho da palavra, não o desempenho.

### O modelo de ruído falha quando o sinal é pequeno

A hipótese "erro uniforme e descorrelacionado" só vale se o sinal cruzar muitos
níveis. Com sinal fraco, o erro fica **correlacionado com o sinal** e vira
**distorção harmônica**, que o ouvido detecta muito melhor que ruído. No limite,
o sinal desaparece por completo — foi o que medimos em [`06 §9`](06-exemplos.md):
um tom de −66 dBFS em 8 bits sumiu (−240 dBFS) e voltou com dither (−65,9 dBFS).

### Dither

Somar ruído de ~1 LSB **antes** de quantizar:

| Sem dither | Com dither |
|---|---|
| erro correlacionado ⟹ distorção | erro descorrelacionado ⟹ ruído branco |
| sinais abaixo de 1 LSB somem | sinais **muito** abaixo de 1 LSB sobrevivem |
| "granulação" audível, tons fantasma | um chiado suave e constante |

Tipos: **RPDF** (retangular, 1 LSB), **TPDF** (triangular, 2 LSB — o padrão de
áudio, porque elimina também a modulação de ruído), e **com formatação de ruído**
(*noise shaping*), que empurra o ruído do dither para frequências onde o ouvido é
menos sensível, comprando ~15 dB de SNR percebida sem mudar bit nenhum.

**Regra prática:** sempre que reduzir a profundidade de bits (24 → 16 numa
masterização, float → int16 num arquivo), use dither TPDF. Custa uma linha.

---

## 5 · Sobreamostragem: comprar bits com taxa

O ruído de quantização tem potência total fixa (Δ²/12), **espalhada por toda a
banda até fs/2**. Se você amostra M vezes mais rápido e filtra de volta à banda
útil, joga fora (M−1)/M do ruído:

```
ganho de SNR = 10·log₁₀(M) dB       ⟹  +3 dB por dobrar, ou meio bit
```

Medido:

```python
# 8 bits, tom de 997 Hz, ruído filtrado de volta à banda de 22,05 kHz
  M= 1 (fs= 44100): SNR na banda =  49.9 dB   ganho teórico  0.0 dB
  M= 2 (fs= 88200): SNR na banda =  52.6 dB   ganho teórico  3.0 dB
  M= 4 (fs=176400): SNR na banda =  56.4 dB   ganho teórico  6.0 dB
  M= 8 (fs=352800): SNR na banda =  59.3 dB   ganho teórico  9.0 dB
  M=16 (fs=705600): SNR na banda =  61.2 dB   ganho teórico 12.0 dB
```

(Saída real.) De M=1 a M=16, ganho medido de 11,3 dB contra 12,0 teóricos — a
diferença é a banda de transição do passa-baixa de 8ª ordem usado na medida.

**Isso é a base do conversor sigma-delta**, que domina o mercado: 1 bit de
resolução a 64× ou 256× a taxa, mais **formatação de ruído** (que empurra o ruído
para longe da banda útil, dando muito mais que os 3 dB por oitava), resultando em
20 bits efetivos. Um conversor de áudio de US$ 2 faz isso.

O ponto conceitual: **taxa de amostragem e resolução são intercambiáveis.** Você
pode comprar bits com velocidade. Essa troca é o que tornou o áudio digital barato.

---

## 6 · Jitter — o erro que ninguém procura

Amostrar não é só *quantos* pontos, é *quando*. Se o relógio treme, você mede o
valor certo no instante errado — que é matematicamente igual a medir o valor errado
no instante certo.

```
SNR_jitter = −20·log₁₀(2π·f·t_j)
```

| f do sinal | Jitter RMS | SNR máxima possível |
|---|---|---|
| 1 kHz | 1 ns | 104 dB |
| 1 kHz | 1 ps | 164 dB |
| 20 kHz | 1 ns | **78 dB** ← pior que 16 bits! |
| 20 kHz | 100 ps | 98 dB |

(Valores calculados pela fórmula, verificados em 14/08/2026.)

**Leia a terceira linha.** Com 1 ns de jitter — que é bastante razoável para um
oscilador barato — você não consegue passar de 78 dB em 20 kHz, por mais que o
conversor tenha 24 bits. **O relógio é o gargalo, não o conversor.** É por isso que
áudio profissional gasta com clock e que sistemas de RF usam osciladores de
referência caros.

E note a dependência com **f**: quanto mais alta a frequência do sinal, pior. Numa
subamostragem passa-faixa (§3), quem manda é a frequência da portadora, não a taxa —
motivo pelo qual undersampling exige clock muito melhor do que parece.

---

## 7 · Reconstrução: do digital de volta ao analógico

A teoria manda interpolar com sinc. Sinc é infinita e não causal, logo
irrealizável. O que se faz de fato:

1. **Sample-and-hold** — segurar cada valor até o próximo. Simples, e introduz um
   erro sistemático: multiplica o espectro por `sinc(f/fs)`.

| f | Atenuação do S&H |
|---|---|
| 0,10·fs | −0,14 dB |
| 0,25·fs | −0,91 dB |
| 0,50·fs | **−3,92 dB** |
| 0,90·fs | −19,23 dB |

(Calculado.) Ou seja, em 20 kHz com fs = 44,1 kHz você perde ~3 dB só pelo
segurador. Todo DAC decente compensa isso com um filtro de correção `1/sinc`,
chamado **droop compensation**.

2. **Filtro de reconstrução analógico** — remove as cópias em torno de fs.
3. **Sobreamostragem digital antes do DAC** — o padrão moderno: interpola 8× em
   digital, e aí o filtro analógico pode ser simples e suave.

---

## Os cinco porquês: por que aliasing é irreversível?

1. **Por que não dá para desfazer aliasing?** Porque duas frequências diferentes
   produziram exatamente a mesma sequência de amostras.
2. **Por que produzem a mesma sequência?** Porque e^{j2π(f+kfs)nT} = e^{j2πfnT}
   quando T = 1/fs: o expoente extra é múltiplo inteiro de 2π, e e^{j2πk} = 1.
3. **Por que isso vale para qualquer k inteiro?** Porque n é inteiro — é a
   discretização do tempo que cria a ambiguidade. No contínuo ela não existe.
4. **Por que a informação some?** Porque a soma de duas contribuições num único
   número é uma equação com duas incógnitas: sem informação adicional, não tem
   solução única.
5. **Existe "informação adicional" que salve?** Sim, e é exatamente o que
   compressive sensing e a separação de fontes exploram: se você souber *a priori*
   que o sinal é esparso, ou que só ocupa certas faixas, o sistema volta a ter
   solução única. **Parada legítima: um limite matemático de contagem de graus de
   liberdade** — não é falta de tecnologia, é falta de equações.

---

## Autoteste

1. Enuncie o teorema da amostragem incluindo a hipótese, e diga por que ela nunca é
   exatamente verdadeira.
2. Um seno de 30 kHz é amostrado a 44,1 kHz. Em que frequência aparece?
3. Explique aliasing usando a propriedade "multiplicar no tempo = convoluir na
   frequência".
4. Por que 44,1 kHz e não 40 kHz? Que componente do sistema justifica a folga?
5. Um sinal ocupa 100,0–100,2 MHz. Qual a menor taxa teoricamente utilizável?
6. Quantos dB de SNR tem um conversor de 12 bits, e por que "24 bits" é enganoso?
7. Como um tom abaixo de 1 LSB pode ser recuperado, e por que isso não viola nada?
8. Quanto de SNR se ganha sobreamostrando 4×? Deduza a fórmula.
9. Um conversor de 24 bits com clock de 1 ns de jitter: qual a SNR real em 20 kHz?
10. O que é droop e como se corrige?
