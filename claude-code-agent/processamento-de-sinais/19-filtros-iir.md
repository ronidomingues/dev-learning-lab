# 19 · Filtros IIR — eficiência, estabilidade e o preço da fase

`Nível: intermediário → avançado` · `Medições feitas em: 14/08/2026`
`Base: SciPy 1.15.3`

IIR = *Infinite Impulse Response*. Tem realimentação:

```
y[n] = Σ b_k·x[n−k] − Σ a_k·y[n−k]
```

A saída depende das saídas anteriores. Isso muda tudo: eficiência enorme,
estabilidade condicional, fase não linear, e sensibilidade numérica.

---

## 1 · O ganho de eficiência, medido

Mesma especificação para todos: passa até 1000 Hz com no máximo 1 dB de ripple,
rejeita a partir de 1500 Hz com pelo menos 60 dB, fs = 8 kHz.

```python
from scipy import signal
fs, wp, ws = 8000, 1000, 1500
for nome, ordfn in [('Butterworth', signal.buttord), ('Chebyshev I', signal.cheb1ord),
                    ('Chebyshev II', signal.cheb2ord), ('Elíptico', signal.ellipord)]:
    N, Wn = ordfn(wp, ws, 1, 60, fs=fs)
    print(f"  {nome:14s} ordem {N:3d}")
n, beta = signal.kaiserord(60, width=(ws-wp)/(fs/2))
print(f"  FIR (Kaiser)   {n:3d} taps")
```

Saída real:

```
  Butterworth    ordem  16
  Chebyshev I    ordem   8
  Chebyshev II   ordem   8
  Elíptico       ordem   6
  FIR (Kaiser)    60 taps
```

**Custo por amostra:** um IIR de ordem 6 em SOS são 3 seções × ~5 multiplicações =
**15 multiplicações**. O FIR equivalente são **60** (30 com simetria). O elíptico é
**2 a 4× mais barato** — e a diferença cresce muito quando a transição é estreita,
porque o custo do FIR é inversamente proporcional à largura da transição, enquanto
o do IIR cresce logaritmicamente.

Em transições muito estreitas (um notch de 2 Hz em 60 Hz a 44,1 kHz), o IIR ganha
por **duas ordens de grandeza**: 6 coeficientes contra ~88 000 taps.

---

## 2 · As famílias — e como escolher

| Família | Banda passante | Banda de rejeição | Transição | Fase | Ordem p/ mesma spec |
|---|---|---|---|---|---|
| **Butterworth** | plana (maximamente plana) | monotônica | **a pior** | melhor das quatro | 16 |
| **Chebyshev I** | ripple | monotônica | boa | pior que Butter | 8 |
| **Chebyshev II** | plana | ripple | boa | pior que Butter | 8 |
| **Elíptico (Cauer)** | ripple | ripple | **a melhor** | **a pior** | 6 |
| **Bessel** | plana | ruim | péssima | **quase linear** | ~20+ |

```
Butterworth        Chebyshev I         Elíptico
─────╮             ∼∼∼∼╮               ∼∼∼∼╮
     ╲                 ╲                   │
      ╲                 ╲                  │
       ╲___              ╲___              ╰∼∼∼∼
   (suave, lento)   (ripple, rápido)  (ripple nos dois, o mais rápido)
```

**Como eu escolho, na prática:**

| Situação | Escolha |
|---|---|
| Uso geral, "quero um passa-baixa" | **Butterworth** — previsível, sem surpresa |
| Preciso de seletividade e tolero ripple na passante | Chebyshev I |
| Preciso de banda passante limpa e tolero ripple na rejeição | Chebyshev II |
| Ordem mínima é crítica (embarcado, tempo real) | Elíptico |
| Preciso preservar a **forma de onda** (pulsos, ECG) | **Bessel** ou, melhor, FIR de fase linear |
| Preciso matar uma frequência específica | `iirnotch` |
| Áudio: equalizador, shelving, peaking | biquads de Robert Bristow-Johnson (*RBJ cookbook*) |

⚠️ **Elíptico tem a pior fase de todas**, e o atraso de grupo dele dispara perto do
corte. Se você usa elíptico num sinal com transiente, o transiente sai deformado.
Ordem mínima nem sempre é a melhor escolha.

---

## 3 · 🔑 SOS, sempre — a demonstração

A mesma função de transferência pode ser implementada de várias formas. Elas são
matematicamente idênticas e **numericamente muito diferentes**.

| Forma | Estrutura | Robustez |
|---|---|---|
| Direta I / II (`b, a`) | um polinômio grande | **ruim** em ordem alta |
| Direta II transposta | idem, melhor arredondamento | média |
| **Cascata de biquads (SOS)** | produto de seções de 2ª ordem | **boa** ← use esta |
| Paralela | soma de seções | boa |
| Treliça (lattice) | estrutura reflexiva | excelente, usada em ponto fixo |

**Por que a forma direta degrada:** os coeficientes de um polinômio de grau 16 são
números enormes e sensíveis. Um erro de arredondamento no coeficiente move as raízes
(os polos) de forma imprevisível — e mover um polo para fora do círculo unitário
transforma o filtro em oscilador. Em SOS, cada seção tem só 2 polos, e um erro
pequeno move pouco.

Em **float64**, com corte em 0,1 e ordens até 16, as duas formas dão praticamente o
mesmo resultado — é honesto dizer isso. O problema aparece em **float32**, que é o
que rodam DSPs, GPUs e código embarcado:

```python
import numpy as np
from scipy import signal
imp = signal.unit_impulse(3000).astype(np.float32)
for N in [4, 8, 12, 16]:
    b, a = signal.butter(N, 0.1); sos = signal.butter(N, 0.1, output='sos')
    y1 = signal.lfilter(b.astype(np.float32), a.astype(np.float32), imp)
    y2 = signal.sosfilt(sos.astype(np.float32), imp)
    ref = signal.sosfilt(sos, imp.astype(np.float64))
    print(f"  ordem {N:2d}: erro max ba = {np.max(np.abs(y1-ref)):10.3e}"
          f"   erro max sos = {np.max(np.abs(y2-ref)):10.3e}")
```

Saída real:

```
  ordem  4: erro max ba =  9.592e-07   erro max sos =  1.191e-07
  ordem  8: erro max ba =  3.814e-03   erro max sos =  1.507e-07
  ordem 12: erro max ba =        nan   erro max sos =  1.385e-07
  ordem 16: erro max ba =        nan   erro max sos =  1.075e-07
```

**Leia a coluna do meio.** Em ordem 8, a forma direta já erra 3,8×10⁻³ — audível.
Em ordem 12, dá **NaN**: o filtro divergiu numericamente e destruiu o sinal. A
coluna do SOS fica em ~10⁻⁷ (o épsilon do float32) em **todas** as ordens.

Não é sutileza acadêmica: é a diferença entre funcionar e não funcionar.
**`output='sos'` e `sosfilt`/`sosfiltfilt`. Sempre.** Se você recebeu `b, a` de
terceiros: `sos = signal.tf2sos(b, a)`.

---

## 4 · Estabilidade na prática

Teoria em [`17`](17-transformada-z.md): todos os polos com |p| < 1. Na prática:

```python
sos = signal.butter(8, 0.1, output='sos')
z, p, k = signal.sos2zpk(sos)
print("maior |polo|:", np.abs(p).max())
```

**Três armadilhas reais:**

1. **Polo muito perto do círculo.** Um corte muito baixo em relação a fs (por
   exemplo, passa-alta em 0,1 Hz a 48 kHz) empurra os polos para |p| ≈ 0,99999. Em
   float32 isso instabiliza. **Solução:** decimar antes de filtrar, ou usar
   aritmética de precisão dupla nas seções críticas.
2. **Quantização de coeficiente em ponto fixo.** O polo projetado em 0,998 pode ser
   arredondado para 1,001 e o filtro oscila. **Solução:** estruturas com sensibilidade
   baixa (acoplada, treliça) e verificar os polos **depois** de quantizar
   ([`28`](28-implementacao-ponto-fixo-e-hardware.md)).
3. **Ciclos limites (limit cycles).** Um IIR em ponto fixo pode entrar em oscilação
   de baixa amplitude sustentada pelo próprio arredondamento, mesmo com polos
   estáveis. **Solução:** dither interno ou arredondamento por magnitude truncada.

**Regras que eu sigo:** ordem ≤ 8 por seção de projeto; polos com |p| < 0,999; e
**sempre** verificar `np.abs(p).max()` antes de embarcar.

---

## 5 · Fase zero via `filtfilt` — e por que não serve em tempo real

`filtfilt` filtra para frente, inverte, filtra de novo, inverte de novo:

| Propriedade | Efeito |
|---|---|
| Fase | **exatamente zero** — nenhum atraso, nenhuma distorção de fase |
| Magnitude | **elevada ao quadrado**: |H|² |
| Ordem efetiva | dobrada |
| Causalidade | **destruída** |

Duas consequências que pegam quase todo mundo:

1. **A atenuação dobra em dB.** Um projeto de −3 dB no corte vira −6 dB. Se você
   quer −3 dB depois do `filtfilt`, projete para −1,5 dB. A SciPy não corrige isso
   para você.
2. **Precisa do sinal inteiro.** É análise offline, ponto. Num afinador, num fone
   com cancelamento de ruído ou num controlador, é fisicamente impossível.

Foi medido em [`13 §5`](13-sinais-e-sistemas-lti.md) e testado no
[`07-projeto-modelo/`](07-projeto-modelo/README.md): o teste
`test_filtfilt_tem_fase_zero` verifica que o pico do impulso **não se moveu**, e
`test_sosfilt_causal_atrasa` verifica que se moveu.

### Tempo real: processar em blocos com estado

```python
sos = signal.butter(4, 1000, btype='high', fs=48000, output='sos')
zi = signal.sosfilt_zi(sos) * primeiro_bloco[0]      # condição inicial
for bloco in fluxo:
    y, zi = signal.sosfilt(sos, bloco, zi=zi)        # o zi ATRAVESSA os blocos
```

**Esquecer de guardar `zi` entre blocos produz um clique na fronteira de cada
bloco** — o defeito mais comum em código de áudio ao vivo. E inicializar `zi` com a
primeira amostra (em vez de zero) evita o transiente de partida.

---

## 6 · Biquads: a unidade de conta do áudio

Uma seção de 2ª ordem:

```
y[n] = b₀x[n] + b₁x[n−1] + b₂x[n−2] − a₁y[n−1] − a₂y[n−2]
```

Cinco multiplicações, quatro somas, quatro registradores de estado. É a unidade
atômica de todo equalizador, e todo DSP de áudio tem contagem de "quantos biquads
por canal" como especificação.

**Os tipos do cookbook de Robert Bristow-Johnson** (o documento mais copiado da
história do áudio digital) são: passa-baixa, passa-alta, passa-faixa, notch,
passa-tudo, **peaking EQ** (realce/corte em torno de f₀ com ganho e Q) e
**shelving** (low/high shelf, realce de tudo abaixo/acima de f₀). Um equalizador
paramétrico de 10 bandas são 10 biquads em cascata — 50 multiplicações por amostra,
trivial para qualquer processador moderno.

**Q e largura de banda:** Q = f₀/Δf(−3 dB). Q=0,707 é o máximo sem sobressinal
(Butterworth de 2ª ordem); Q=30 num notch de 60 Hz dá 2 Hz de largura; Q > 100 toca
por muitos ciclos e imita um sinal que não existe.

---

## 7 · FIR ou IIR: a tabela de decisão

| Critério | FIR | IIR |
|---|---|---|
| Estabilidade | garantida | condicional |
| Fase linear | **sim, exata** | impossível (só via `filtfilt`, offline) |
| Coeficientes p/ mesma spec | 60 | **6** |
| Atraso | (N−1)/2 = 30 amostras | poucas amostras |
| Ponto fixo | seguro | exige cuidado |
| Ruído de arredondamento | não realimenta | acumula |
| Projeto | direto | precisa entender polos |
| Modificar em tempo real (varrer o corte) | difícil (recalcular tudo) | fácil (5 coeficientes) |
| Emular um circuito analógico | difícil | **natural** (bilinear) |
| Convolução com resposta de sala medida | **natural** | impossível |

**Meu resumo profissional:** comece com IIR Butterworth SOS para tarefas comuns.
Vá para FIR quando a fase importar (biomédico, comunicação, transientes) ou quando
a resposta desejada não for uma das famílias clássicas. Vá para elíptico quando cada
multiplicação custar dinheiro.

---

## Os cinco porquês: por que a forma direta de ordem alta falha?

1. **Por que a forma direta perde precisão em ordem alta?** Porque os coeficientes
   do polinômio de grau N crescem muito e se cancelam na soma, e cancelamento é onde
   o ponto flutuante perde dígitos significativos.
2. **Por que o cancelamento é fatal aqui?** Porque a saída é uma diferença de
   números grandes que resulta num número pequeno; os dígitos significativos do
   resultado vêm dos *últimos* bits das parcelas — exatamente os menos confiáveis.
3. **Por que isso move os polos?** Porque os polos são as raízes do polinômio
   denominador, e a sensibilidade das raízes aos coeficientes cresce
   **exponencialmente** com o grau. É o fenômeno do "polinômio de Wilkinson", um
   resultado clássico de análise numérica de 1963.
4. **Por que biquads não sofrem disso?** Porque cada seção é um polinômio de grau 2,
   cujas raízes têm sensibilidade limitada e conhecida aos dois coeficientes.
5. **Por que ninguém usa ordem 1 então, se é ainda melhor?** Porque um par de polos
   complexos conjugados (necessário para qualquer coisa ressonante) exige grau 2 com
   coeficientes reais. **Parada legítima: é o teorema fundamental da álgebra** —
   raízes complexas de polinômios reais vêm em pares, e o menor fator real que as
   contém tem grau 2. O biquad é o átomo indivisível por razão algébrica.

---

## Autoteste

1. Mesma especificação: quantas ordens para Butterworth, Chebyshev I e elíptico?
2. Por que o elíptico, sendo o mais eficiente, não é a escolha padrão?
3. Em float32, o que acontece com um Butterworth de ordem 12 em forma direta?
4. Como converter um `(b, a)` recebido de terceiros para algo confiável?
5. `filtfilt` num filtro projetado para −3 dB no corte entrega quantos dB? Por quê?
6. O que é `zi` no `sosfilt` e qual o sintoma de esquecê-lo?
7. Quantas multiplicações e quantos estados tem um biquad?
8. Q = 30 num notch de 60 Hz corresponde a que largura de banda?
9. Por que o biquad (2ª ordem) é a unidade mínima, e não a 1ª ordem?
