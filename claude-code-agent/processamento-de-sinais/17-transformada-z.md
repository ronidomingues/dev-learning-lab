# 17 · Transformada Z — polos, zeros e a geometria dos filtros

`Nível: intermediário → avançado` · `Atualizado em: 14/08/2026`

A transformada Z está para o tempo discreto como Laplace está para o contínuo:
ela transforma equação de diferenças em álgebra, e transforma "o filtro é estável?"
numa pergunta **geométrica** que se responde olhando um desenho.

---

## 1 · Definição

```
X(z) = Σ_{n=−∞}^{∞} x[n]·z^{−n},        z ∈ ℂ
```

Compare com a DTFT: `X(e^{jΩ}) = Σ x[n]·e^{−jΩn}`.

> **A DTFT é a transformada Z avaliada no círculo unitário** (z = e^{jΩ}).

Essa frase é o mapa inteiro. A transformada Z estende a DTFT para **todo o plano
complexo**, e é essa extensão que permite falar de convergência, estabilidade e
polos — conceitos que na DTFT não têm onde morar.

```
          Im(z)
            │      ╭───────╮
            │    ╱    ●p    ╲       ● polos (raízes do denominador)
            │   │  ○         │      ○ zeros (raízes do numerador)
     ───────┼───┼──────●─────┼──── Re(z)
            │   │           │
            │    ╲    ○    ╱       ─── círculo unitário |z|=1
            │      ╰───────╯           (onde vive a resposta em frequência)
```

### Região de convergência (ROC)

A série só converge para alguns z. Para h[n] = aⁿ·u[n] (causal):

```
H(z) = Σ aⁿz^{−n} = 1/(1 − az^{−1}),        para |z| > |a|
```

É a soma geométrica de [`12 §4`](12-matematica-do-zero.md), e a ROC é literalmente
"onde a razão tem módulo menor que 1".

**A ROC é parte da resposta, não um detalhe.** A mesma expressão algébrica
1/(1 − az^{−1}) corresponde a **dois sinais diferentes**:

| ROC | Sinal | Causal? |
|---|---|---|
| \|z\| > \|a\| | aⁿ·u[n] | sim |
| \|z\| < \|a\| | −aⁿ·u[−n−1] | não (anticausal) |

Dar H(z) sem a ROC é ambíguo. Na prática, quando alguém diz "H(z) = ..." em DSP,
está subentendido "causal", e a ROC é o exterior do polo mais distante.

**Regras rápidas:**
- Sistema **causal** ⟺ ROC é o exterior de um círculo.
- Sistema **estável** ⟺ ROC **contém o círculo unitário**.
- Causal **e** estável ⟺ **todos os polos dentro do círculo unitário.**

Esta última linha é a que você usa todo dia.

---

## 2 · Função de transferência, polos e zeros

Da equação de diferenças ([`13 §1`](13-sinais-e-sistemas-lti.md)), aplicando a Z:

```
H(z) = Y(z)/X(z) = (b₀ + b₁z⁻¹ + ... + b_M z^{−M}) / (1 + a₁z⁻¹ + ... + a_N z^{−N})
```

Fatorando:

```
H(z) = k · Π(z − z_i) / Π(z − p_i)
```

- **zeros** z_i: onde H = 0. O filtro **mata** aquela frequência.
- **polos** p_i: onde H = ∞. O filtro **ressoa** naquela frequência.

```python
import numpy as np
from scipy import signal
b, a = signal.butter(4, 0.2)
z, p, k = signal.tf2zpk(b, a)
print("zeros:", np.round(z, 4))
print("polos:", np.round(p, 4))
print("|polos|:", np.round(np.abs(p), 4))
```

Saída real:

```
zeros: [-1.0002+0.j  -1.+0.0002j  -1.-0.0002j  -0.9998+0.j]
polos: [0.6605+0.4433j 0.6605-0.4433j 0.5243+0.1458j 0.5243-0.1458j]
|polos|: [0.7954 0.7954 0.5442 0.5442]
```

Leitura completa deste filtro só olhando os números:

- **Quatro zeros em z = −1.** E z = −1 é o ponto do círculo unitário em Ω = π, ou
  seja, **Nyquist**. Quatro zeros ali ⟹ atenuação total e acentuada em fs/2. É a
  assinatura de um passa-baixa Butterworth: ele empilha todos os zeros em Nyquist.
- **Polos com módulo 0,795 e 0,544** — ambos < 1, logo **estável**.
- Os polos estão em pares conjugados, condição necessária para os coeficientes
  serem reais.
- Os pequenos desvios nos zeros (−1,0002) são erro de arredondamento da conversão
  `tf2zpk`. Em ordem alta esse erro cresce muito, e é exatamente o motivo de se usar
  SOS ([`19`](19-filtros-iir.md)).

### A regra geométrica que substitui a conta

Para saber |H| numa frequência Ω, vá até o ponto z = e^{jΩ} no círculo unitário e:

```
|H(e^{jΩ})| = k · (produto das distâncias aos ZEROS) / (produto das distâncias aos POLOS)
```

Daí sai toda a intuição de projeto:

- Zero **em cima** do círculo ⟹ distância zero ⟹ **nulo perfeito** naquela frequência.
  É como se projeta um notch: ponha um zero exatamente em e^{±jΩ₀}.
- Polo **perto** do círculo ⟹ distância pequena ⟹ **pico agudo**. Quanto mais perto,
  mais agudo e mais longo o "toque" (ringing).
- Polo **em cima** do círculo ⟹ oscilador (marginalmente estável).
- Polo **fora** ⟹ instável, saída explode.

**Projetar filtro é posicionar polos e zeros.** Todo o resto — Butterworth,
Chebyshev, elíptico — são receitas de onde pôr.

---

## 3 · Do analógico para o digital: a transformada bilinear

Grande parte do conhecimento de filtros nasceu analógica (Butterworth 1930,
Chebyshev, Cauer). O caminho padrão para reaproveitar é mapear o plano s no plano z:

```
s = (2/T)·(1 − z⁻¹)/(1 + z⁻¹)          (transformada bilinear)
```

**Propriedades:**
- Mapeia o semiplano esquerdo de s (estável no analógico) **exatamente** no interior
  do círculo unitário (estável no digital). **Estabilidade é preservada sempre.**
- Mapeia o eixo jω inteiro (−∞ a +∞) no círculo unitário (−π a π). Comprime o
  infinito num intervalo finito — e é aí que aparece o preço.

### Warping: a distorção de frequência

```
Ω_digital = 2·arctan(ω_analógica·T/2)
```

Não linear. Medido, para fs = 1000 Hz:

```
  digital  50 Hz  <- analógico    50.42 Hz  (razão 1.008)
  digital 100 Hz  <- analógico   103.43 Hz  (razão 1.034)
  digital 200 Hz  <- analógico   231.27 Hz  (razão 1.156)
  digital 400 Hz  <- analógico   979.66 Hz  (razão 2.449)
  digital 490 Hz  <- analógico 10128.78 Hz  (razão 20.671)
```

(Saída real.) Em baixa frequência, quase nenhuma distorção (0,8 %). Perto de
Nyquist, o mapeamento explode: 490 Hz digitais correspondem a 10 kHz analógicos.

**Consequência prática:** se você projeta um analógico com corte em 400 Hz e aplica
a bilinear ingenuamente com fs = 1000, o corte digital sai em ~200 Hz, não em 400.
A correção chama-se **pré-distorção (prewarping)**: você projeta o analógico na
frequência distorcida, de modo que o warping o traga de volta ao lugar certo.

**A boa notícia:** `signal.butter(N, Wn, fs=fs)` **já faz o prewarping por você**.
Você só precisa saber disso quando implementar o mapeamento à mão, ou quando ler
um filtro analógico de datasheet e traduzir.

### Alternativas de mapeamento

| Método | Preserva | Não preserva |
|---|---|---|
| **Bilinear** | estabilidade, forma da resposta | escala de frequência (warping) |
| Invariância ao impulso | forma da resposta ao impulso | pode ter aliasing se o analógico não for limitado em banda |
| Casamento de polos e zeros | posição de polos/zeros | ganho, às vezes |
| Euler / diferença regressiva | simplicidade | tudo o mais; só serve para fs ≫ banda |

Na prática, use bilinear salvo se você precisar especificamente da resposta ao
impulso idêntica (simulação de circuito, emulação de amplificador valvulado).

---

## 4 · Sistemas de fase mínima, máxima e passa-tudo

| Tipo | Zeros | Propriedade |
|---|---|---|
| **Fase mínima** | todos **dentro** do círculo | atraso de grupo mínimo entre todos com a mesma magnitude; **inversível de forma estável** |
| Fase máxima | todos fora | atraso máximo |
| Fase mista | uns dentro, outros fora | o caso comum |
| **Passa-tudo** | zero em 1/p* para cada polo p | \|H\| = 1 em todas as frequências, só mexe na fase |

**Por que fase mínima importa:** só um sistema de fase mínima tem inverso causal e
estável. Isso é a base de:

- **Equalização de canal:** para desfazer a distorção do canal, você precisa
  inverter H. Se o canal não for de fase mínima, o inverso é instável, e você tem
  de usar um equalizador com atraso (ou um DFE).
- **Desconvolução sísmica:** o pulso da fonte é modelado como fase mínima
  justamente para poder ser invertido.
- **Decomposição canônica:** todo sistema = (fase mínima) × (passa-tudo). Você pode
  corrigir a magnitude com um e a fase com o outro, separadamente.

**Filtros passa-tudo** parecem inúteis (não mudam magnitude nenhuma) e são
extremamente úteis: reverberação artificial, equalização só de fase, filtros de
atraso fracionário, e bancos de filtros com reconstrução perfeita.

---

## 5 · Transformada Z inversa — três caminhos

| Método | Quando |
|---|---|
| **Frações parciais** | H(z) racional; o caminho padrão à mão. `signal.residuez` |
| Divisão longa | quer só as primeiras amostras de h[n] |
| Inspeção com tabela | reconhece a forma; o mais rápido na prática |
| Integral de contorno | rigor formal; exige análise complexa (resíduos de Cauchy) |

**Na prática você quase nunca inverte à mão.** `signal.dimpulse` ou
`lfilter(b, a, impulso)` dá h[n] numericamente em uma linha. A transformada Z
inversa analítica importa para *provar* propriedades, não para calcular.

### Tabela mínima

| x[n] | X(z) | ROC |
|---|---|---|
| δ[n] | 1 | todo z |
| δ[n−k] | z^{−k} | z ≠ 0 |
| u[n] | 1/(1 − z⁻¹) | \|z\| > 1 |
| aⁿu[n] | 1/(1 − az⁻¹) | \|z\| > \|a\| |
| n·aⁿu[n] | az⁻¹/(1 − az⁻¹)² | \|z\| > \|a\| |
| cos(Ω₀n)u[n] | (1 − cosΩ₀·z⁻¹)/(1 − 2cosΩ₀·z⁻¹ + z⁻²) | \|z\| > 1 |

### Propriedades

| Propriedade | Efeito |
|---|---|
| Atraso: x[n−k] | z^{−k}·X(z) — **z⁻¹ é o operador atraso**. Toda a notação vem disso |
| Convolução: x*h | X(z)·H(z) |
| Modulação: aⁿx[n] | X(z/a) |
| Diferenciação em z | −z·dX/dz ⟷ n·x[n] |
| Valor inicial | x[0] = lim_{z→∞} X(z) |
| Valor final | lim x[n] = lim_{z→1} (1−z⁻¹)X(z), se estável |

---

## Os cinco porquês: por que "polo dentro do círculo" significa estável?

1. **Por que polo dentro ⟹ estável?** Porque a ROC de um sistema causal é o
   exterior do polo mais distante; se todos os polos têm |p| < 1, a ROC inclui o
   círculo unitário.
2. **Por que a ROC incluir o círculo importa?** Porque a DTFT é a Z avaliada no
   círculo; se a série não converge lá, a resposta em frequência não existe — e não
   existir resposta em frequência é a versão espectral de "explode".
3. **Por que a convergência lá equivale à estabilidade BIBO?** Porque convergir em
   |z|=1 é exatamente Σ|h[n]| < ∞ (a série absolutamente convergente), que é o
   critério BIBO de [`13 §3`](13-sinais-e-sistemas-lti.md).
4. **Por que a resposta ao impulso de um polo em p decai como pⁿ?** Porque a
   inversa de 1/(1 − pz⁻¹) é pⁿu[n] — a série geométrica de novo.
5. **Por que a série geométrica converge só com |p| < 1?** Porque a soma parcial é
   (1−p^N)/(1−p), e p^N só tende a zero se |p| < 1. **Parada legítima: é aritmética
   de limites.** Todo o critério de estabilidade digital reduz-se a "|p|^N → 0".

---

## Autoteste

1. Que relação existe entre a transformada Z e a DTFT?
2. Por que dar H(z) sem a ROC é ambíguo? Dê o exemplo dos dois sinais.
3. Enuncie a condição de estabilidade para um sistema causal.
4. Um filtro tem quatro zeros em z = −1. O que isso diz sobre ele?
5. Explique a regra geométrica das distâncias e use-a para projetar um notch.
6. O que é warping e por que ele quase não incomoda em baixa frequência?
7. Por que só sistemas de fase mínima podem ser invertidos de forma estável?
8. Para que serve um filtro passa-tudo, se ele não altera magnitude?
9. Por que z⁻¹ significa "atrasar uma amostra"?
