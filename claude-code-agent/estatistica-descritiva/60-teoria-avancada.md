# 60. Teoria avançada — o que sustenta as medidas

`Nível: pesquisa` · `Última atualização: 20/08/2026`
`Pré-requisitos: cálculo, probabilidade básica, notação de esperança`

> Aqui as afirmações dos arquivos anteriores viram demonstrações. Se você chegou até aqui
> praticando, este arquivo amarra tudo. Se pulou direto para cá, volte ao
> [10-fundamentos.md](10-fundamentos.md) — o vocabulário é pressuposto.

---

## 60.1 Estimadores: as quatro propriedades

Um **estimador** é uma função da amostra, `θ̂ = T(X₁,…,Xₙ)`, usada para estimar um parâmetro `θ`.

| Propriedade | Definição | Leitura |
|---|---|---|
| **Não viesado** | `E[θ̂] = θ` | acerta na média |
| **Consistente** | `θ̂ →ᵖ θ` quando `n → ∞` | converge com dados suficientes |
| **Eficiente** | atinge a menor variância possível | não desperdiça informação |
| **Suficiente** | `P(X \| T(X))` não depende de `θ` | não descarta informação sobre `θ` |

**São independentes entre si.** Um estimador pode ser não viesado e inconsistente (por exemplo,
usar apenas `X₁` como estimativa de `μ`: acerta na média, nunca converge). E pode ser
enviesado e consistente — o que é frequentemente **preferível**.

### O critério que realmente importa: erro quadrático médio

```
EQM(θ̂) = E[(θ̂ − θ)²] = Var(θ̂) + [Viés(θ̂)]²
```

**Demonstração.** Some e subtraia `E[θ̂]`:

```
E[(θ̂ − θ)²] = E[(θ̂ − E[θ̂] + E[θ̂] − θ)²]
             = E[(θ̂ − E[θ̂])²] + 2·E[(θ̂ − E[θ̂])]·(E[θ̂] − θ) + (E[θ̂] − θ)²
             = Var(θ̂)          + 0                            + Viés²
```

O termo cruzado zera porque `E[θ̂ − E[θ̂]] = 0`. ∎

> **Consequência que contraria o ensino padrão:** perseguir "não viesado" é otimizar um dos
> dois termos ignorando o outro. Um estimador com viés pequeno e variância muito menor tem
> **EQM menor** — erra menos, de fato. É o fundamento de ridge, lasso, encolhimento
> hierárquico e da regularização em geral.

---

## 60.2 A correção de Bessel, demonstrada

**Afirmação.** Com `X₁,…,Xₙ` iid, média `μ` e variância `σ²`:

```
      ⎡  n            ⎤
   E  ⎢  Σ (Xᵢ − X̄)²  ⎥ = (n − 1)·σ²
      ⎣ i=1           ⎦
```

**Demonstração.** Expanda em torno de `μ`:

```
Σ(Xᵢ − X̄)² = Σ[(Xᵢ − μ) − (X̄ − μ)]²
            = Σ(Xᵢ − μ)² − 2(X̄ − μ)Σ(Xᵢ − μ) + n(X̄ − μ)²
```

Como `Σ(Xᵢ − μ) = n(X̄ − μ)`, o termo do meio vale `−2n(X̄ − μ)²`, e portanto:

```
Σ(Xᵢ − X̄)² = Σ(Xᵢ − μ)² − n(X̄ − μ)²
```

Tomando esperanças, com `E[(Xᵢ − μ)²] = σ²` e `E[(X̄ − μ)²] = Var(X̄) = σ²/n`:

```
E[Σ(Xᵢ − X̄)²] = n·σ² − n·(σ²/n) = (n − 1)·σ²      ∎
```

Logo `s² = Σ(Xᵢ − X̄)²/(n−1)` é não viesado, e dividir por `n` subestima por um fator
`(n−1)/n` — exatamente a metade quando `n = 2`, como medido em
[13-medidas-de-dispersao.md](13-medidas-de-dispersao.md).

**A intuição geométrica.** O vetor de resíduos `(X − X̄·1)` vive no subespaço ortogonal a
`1 = (1,…,1)`, que tem dimensão `n − 1`. Você projetou um vetor de `ℝⁿ` num subespaço de
dimensão `n−1`; a norma quadrada esperada é proporcional à dimensão. **"Grau de liberdade" é,
literalmente, dimensão de subespaço.**

### E por que `s` continua enviesado

Pela desigualdade de Jensen, com `g(x) = √x` côncava e `Var(s²) > 0`:

```
E[s] = E[√(s²)] < √(E[s²]) = σ
```

Para dados normais o viés é exato:

```
E[s] = c₄(n)·σ,     c₄(n) = √(2/(n−1)) · Γ(n/2)/Γ((n−1)/2)
```

`c₄(2) = √(2/π) ≈ 0,7979` — o 11,96 medido contra `σ = 15`. `c₄(10) ≈ 0,9727`,
`c₄(25) ≈ 0,9896`.

> **Lição geral:** *não viesamento não sobrevive a transformações não lineares.* Se `θ̂` é não
> viesado para `θ`, `f(θ̂)` em geral não é para `f(θ)`. Vale para raiz, log, inverso,
> exponencial — e é a origem de erros silenciosos ao mudar de escala.

---

## 60.3 Informação de Fisher e o limite de Cramér-Rao

A **informação de Fisher** mede quanto uma observação informa sobre `θ`:

```
I(θ) = E[ (∂/∂θ log f(X; θ))² ] = −E[ ∂²/∂θ² log f(X; θ) ]
```

**Limite de Cramér-Rao.** Sob condições de regularidade, qualquer estimador não viesado
satisfaz:

```
              1
Var(θ̂) ≥ ─────────
           n·I(θ)
```

Existe um **piso** para a precisão alcançável. Um estimador que o atinge é dito **eficiente**.

**Exemplo.** Para a normal com `σ` conhecido, `I(μ) = 1/σ²`, logo `Var(μ̂) ≥ σ²/n`. A média
amostral tem exatamente `σ²/n`: é eficiente, e **nenhum estimador não viesado pode fazer
melhor**. É a justificativa formal para o domínio da média sob normalidade.

### Eficiência relativa assintótica (ARE)

```
ARE(T₁, T₂) = lim Var(T₂)/Var(T₁)
```

Para estimar o centro de uma **normal**:

| Estimador | Variância assintótica | ARE vs média | Ponto de ruptura |
|---|---|---|---|
| média | `σ²/n` | 1,000 | 0% |
| **Hodges-Lehmann** | `σ²/n · (3/π)⁻¹` | **0,955** | ~29% |
| média aparada 10% | ≈ `σ²/n · 1,06` | ≈0,94 | 10% |
| **mediana** | `π·σ²/(2n)` | **2/π = 0,637** | 50% |

A variância assintótica da mediana é `1/(4n·f(m)²)`, com `f` a densidade no ponto mediano.
Para a normal, `f(m) = 1/(σ√(2π))`, o que dá `πσ²/(2n)` — daí o **64%** citado no
[arquivo 12](12-medidas-de-posicao.md).

Para estimar a **escala** de uma normal:

| Estimador | ARE | Ponto de ruptura |
|---|---|---|
| desvio padrão `s` | 1,000 | 0% |
| **Qₙ** (Rousseeuw-Croux, 1993) | **0,82** | 50% |
| Sₙ (Rousseeuw-Croux, 1993) | 0,58 | 50% |
| **MAD** | **0,37** | 50% |

> **Qₙ é a melhor escolha de escala robusta que existe**, e quase ninguém a conhece: mesmo
> ponto de ruptura do MAD com **mais que o dobro** da eficiência. É o 25º percentil das
> distâncias `|xᵢ − xⱼ|` entre todos os pares, vezes uma constante. Se você está escrevendo
> código de detecção de anomalia hoje, use Qₙ, não MAD.

**A troca é sempre a mesma:** eficiência sob o modelo × resistência à violação do modelo.
Não há almoço grátis, e a escolha depende de quanto você confia no modelo.

---

## 60.4 Máxima verossimilhança

```
θ̂_MV = argmax_θ  L(θ) = argmax_θ  Π f(xᵢ; θ)     (na prática: maximiza-se log L)
```

**Propriedades assintóticas** (sob regularidade):

- **consistente**: `θ̂ →ᵖ θ`;
- **assintoticamente normal**: `√n(θ̂ − θ) →ᵈ N(0, 1/I(θ))`;
- **assintoticamente eficiente**: atinge o limite de Cramér-Rao;
- **equivariante**: `f(θ)` é estimado por `f(θ̂)` — mas isso é justamente o que quebra o não
  viesamento.

**Exemplo — normal.** Maximizando a log-verossimilhança obtém-se `μ̂ = x̄` e
`σ̂² = Σ(xᵢ − x̄)²/n` — o divisor `n`, **enviesado**. A máxima verossimilhança prefere
eficiência a não viesamento, e é por isso que `np.std` (herdeiro da tradição de MV) usa
`ddof=0` enquanto `statistics.stdev` (herdeiro da tradição de inferência amostral) usa
`ddof=1`. **A discordância entre bibliotecas do [arquivo 05](05-manual-de-uso.md) é uma
discordância entre escolas.**

**Onde a MV falha:** com `n` pequeno pode ser muito enviesada; para modelos com muitos
parâmetros pode não existir ou divergir; e a equivariância transporta viés para qualquer
transformação.

---

## 60.5 Método delta

Como propagar variância através de uma função não linear?

Se `√n(θ̂ − θ) →ᵈ N(0, σ²)` e `g` é diferenciável com `g'(θ) ≠ 0`:

```
√n(g(θ̂) − g(θ)) →ᵈ N(0, [g'(θ)]²·σ²)
```

**Demonstração (esboço).** Taylor de primeira ordem: `g(θ̂) ≈ g(θ) + g'(θ)(θ̂ − θ)`.
O termo linear domina, e variância de uma constante vezes uma variável é a constante ao
quadrado vezes a variância. ∎

Isto **é** a fórmula de propagação de incerteza do [arquivo 15](15-erro-e-incerteza.md),
com nome de teorema. Casos comuns:

| `g` | Variância aproximada de `g(θ̂)` |
|---|---|
| `log θ` | `σ²/θ²` — a variância do log é a variância relativa |
| `1/θ` | `σ²/θ⁴` |
| `√θ` | `σ²/(4θ)` |
| `θ²` | `4θ²σ²` |

**Limite importante:** a aproximação exige `g'(θ) ≠ 0` e que a variância seja pequena em
relação à curvatura. Para razões cujo denominador pode chegar perto de zero, ela falha
completamente — é o caso da Cauchy ([arquivo 14](14-forma-e-distribuicoes.md)).

---

## 60.6 Teoria da robustez: função de influência

**Hampel (1968, 1974)** formalizou robustez com a **função de influência**: o efeito de uma
contaminação infinitesimal em `x` sobre o funcional `T`:

```
                T((1−ε)F + ε·δₓ) − T(F)
IF(x; T, F) = lim ────────────────────────
              ε→0            ε
```

| Funcional | Função de influência | Limitada? |
|---|---|---|
| média | `x − μ` | ❌ **cresce sem limite** |
| mediana | `sinal(x − m)/(2f(m))` | ✅ limitada |
| variância | `(x − μ)² − σ²` | ❌ cresce **ao quadrado** |
| M-estimador de Huber | `ψ_c(x − μ)` | ✅ limitada por construção |

**Aqui está a robustez, formalizada:** um estimador é robusto se sua função de influência é
**limitada**. A da média é `x − μ`, que cresce linearmente — um único ponto suficientemente
distante move o resultado arbitrariamente. A da mediana só depende do **sinal**, e por isso é
limitada, exatamente como a derivada da soma dos módulos mostrou no
[arquivo 12](12-medidas-de-posicao.md).

### M-estimadores

Generalizam a média: minimize `Σ ρ(xᵢ − θ)` para uma função de perda `ρ`.

| `ρ(u)` | Estimador |
|---|---|
| `u²` | média |
| `\|u\|` | mediana |
| **Huber:** `u²/2` se `\|u\| ≤ c`; `c\|u\| − c²/2` caso contrário | **estimador de Huber** |
| Tukey bisquare (redescendente) | rejeita totalmente valores muito distantes |

O **Huber** é quadrático no centro (eficiente sob normalidade) e linear nas caudas (robusto).
Com `c = 1,345σ` obtém-se **95% de eficiência** sob normalidade **com** função de influência
limitada. É o compromisso padrão, e o motivo de a *Huber loss* ser onipresente em aprendizado
de máquina — a mesma ideia, com outro nome.

### Ponto de ruptura, formalmente

```
ε*(T, X) = min{ m/n : sup_{X'} |T(X') − T(X)| = ∞ }
```

onde `X'` difere de `X` em `m` observações arbitrárias. Nenhum estimador equivariante por
translação pode ter `ε* > 1/2`: acima disso, os contaminados são maioria e não há critério
para distingui-los.

---

## 60.7 Teoria do bootstrap

**O princípio de plug-in.** Um parâmetro é um **funcional** da distribuição: `θ = T(F)`.
A estimativa natural é `θ̂ = T(F̂ₙ)`, onde `F̂ₙ` é a distribuição empírica (massa `1/n` em cada
observação).

O bootstrap estima a distribuição de `θ̂ − θ` pela distribuição de `θ̂* − θ̂`, onde `θ̂*` vem de
uma amostra de `F̂ₙ`.

**Por que funciona.** Pelo teorema de Glivenko-Cantelli, `F̂ₙ → F` uniformemente e quase
certamente. Se `T` for suficientemente suave (diferenciável no sentido de Hadamard), a
substituição de `F` por `F̂ₙ` é assintoticamente válida.

**Quando NÃO funciona** — e é uma lista curta que vale decorar:

| Caso | Por quê |
|---|---|
| **máximo / mínimo** | o funcional não é suave; o bootstrap é inconsistente |
| **parâmetros na fronteira** | idem |
| variância infinita | não há limite normal |
| `n` muito pequeno | `F̂ₙ` é péssima aproximação de `F` |
| dados dependentes | viola a suposição de iid — use *block bootstrap* |

**Refinamentos.**
- **Percentílico simples**: erro de cobertura de ordem `O(n^(−1/2))`.
- **BCa** (corrigido por viés e acelerado, Efron 1987): erro `O(n⁻¹)`, e é **equivariante a
  transformações**. É o que se deve usar quando a assimetria importa.
- **Bootstrap-t**: erro `O(n⁻¹)`, mas exige uma estimativa de variância dentro de cada
  reamostra (bootstrap duplo, caro).

---

## 60.8 Desigualdades de concentração

Quão rápido a média converge? Em ordem crescente de força (e de suposições):

| Desigualdade | Enunciado | Exige |
|---|---|---|
| **Markov** | `P(X ≥ a) ≤ E[X]/a` | `X ≥ 0` |
| **Chebyshev** | `P(\|X−μ\| ≥ kσ) ≤ 1/k²` | variância finita |
| **Hoeffding** | `P(\|X̄−μ\| ≥ t) ≤ 2exp(−2nt²/(b−a)²)` | variáveis **limitadas** em `[a,b]` |
| **Bernstein** | usa a variância; melhor quando `σ² ≪ (b−a)²` | limitadas + variância |
| **McDiarmid** | para funções com diferenças limitadas | além de médias |

**Chebyshev dá decaimento polinomial** (`1/k²`); **Hoeffding dá decaimento exponencial**
(`e^(−2nt²)`). A diferença é enorme, e o preço é a suposição de que os dados são limitados.

Hoeffding é a base dos limites de generalização em aprendizado estatístico e dos algoritmos
de bandidos (UCB). E ele explica formalmente por que `n` grande "resolve": a probabilidade de
a média amostral errar por mais de `t` cai **exponencialmente** em `n`.

---

## 60.9 L-momentos: momentos que não explodem

Momentos convencionais de ordem alta (assimetria, curtose) são péssimos estimadores com cauda
pesada, como medido no [arquivo 14](14-forma-e-distribuicoes.md).

**L-momentos** (Hosking, 1990) são combinações lineares de **estatísticas de ordem**:

```
λ₁ = E[X₍₁:₁₎]                              (posição — é a média)
λ₂ = ½·E[X₍₂:₂₎ − X₍₁:₂₎]                   (escala)
λ₃ = ⅓·E[X₍₃:₃₎ − 2X₍₂:₃₎ + X₍₁:₃₎]         (assimetria)
λ₄ = …                                      (curtose)
```

Vantagens concretas:

- existem sempre que a **média** existe — não exigem momentos de ordem 3 ou 4;
- muito menos enviesados com amostras pequenas;
- muito mais robustos a outliers;
- as razões `τ₃ = λ₃/λ₂` e `τ₄ = λ₄/λ₂` são limitadas, ao contrário de assimetria e curtose.

São **o padrão em hidrologia** para estimar cheias extremas, exatamente porque os momentos
convencionais fracassam com dados de eventos raros. Fora dessa área, são pouco conhecidos —
**opinião: injustamente**.

---

## 60.10 Estimação em fluxo (dados que não cabem na memória)

Quando os dados chegam continuamente e não podem ser armazenados:

| Estatística | Algoritmo | Custo |
|---|---|---|
| média, variância | **Welford** (usado no projeto-modelo) | `O(1)` memória, exato |
| média/variância em paralelo | **Chan-Golub-LeVeque** | combina parciais |
| **quantis aproximados** | **t-digest** (Dunning), **KLL**, GK | `O(log n)` memória, erro controlado |
| cardinalidade distinta | HyperLogLog | ~1,5 KB para bilhões, erro ~2% |
| itens mais frequentes | Count-Min Sketch | erro controlado |

**A mediana exata é impossível em uma passada com memória sublinear** — é um resultado
clássico (Munro & Paterson, 1980): qualquer algoritmo de `p` passadas precisa de `Ω(n^(1/p))`
memória. Por isso o **t-digest** existe e é o que roda por trás de todo painel de p99 em
produção: ele erra pouco justamente nas caudas, que é onde os percentis interessam.

---

## 60.11 Decisão estatística: a moldura que unifica tudo

Escolher um estimador é escolher uma **função de perda**:

| Perda `L(θ, a)` | Estimador ótimo (bayesiano) |
|---|---|
| `(θ − a)²` | **média** a posteriori |
| `\|θ − a\|` | **mediana** a posteriori |
| `1[θ ≠ a]` | **moda** a posteriori |
| assimétrica (pinball) | **quantil** correspondente |

**Isto fecha o círculo do [arquivo 10](10-fundamentos.md):** média, mediana e moda não são
três medidas concorrentes de "centro". São **as respostas ótimas a três perguntas diferentes**
sobre como o erro deve ser punido.

E a **perda pinball** — assimétrica, com pesos `τ` e `1−τ` — é o que gera regressão quantílica
e previsão de quantis em aprendizado de máquina. Se errar para baixo custa mais que errar para
cima (estoque, capacidade, seguro), o estimador ótimo **não é a média**, é um quantil
específico determinado pela razão dos custos. Essa é a resposta estatística correta para
"quanto estoque manter", e é conhecida como o problema do jornaleiro.

**Admissibilidade e o paradoxo de Stein.** Um estimador é **inadmissível** se existe outro com
EQM menor ou igual para todo `θ`, e estritamente menor em algum ponto.

Charles Stein provou em 1956 um resultado que a comunidade recebeu com incredulidade: para
estimar simultaneamente `p ≥ 3` médias normais independentes, **a média amostral é
inadmissível**. O estimador de James-Stein, que "encolhe" todas as médias na direção de um
centro comum, tem EQM menor **sempre** — mesmo que as quantidades estimadas não tenham
absolutamente nada a ver umas com as outras (o exemplo clássico: média de trigo no Kansas,
consumo de chá em Taiwan e peso de bebês).

> **Por que isso importa fora da teoria:** o encolhimento de Stein é o antepassado direto da
> regularização, dos modelos hierárquicos bayesianos e do *empirical Bayes*. É o argumento
> formal de por que "juntar informação de casos relacionados" melhora as estimativas
> individuais — a base de ranquear hospitais, escolas, jogadores ou lojas com `n` pequeno em
> cada um. Ranquear por média bruta é, comprovadamente, pior.

---

## 60.12 Mapa das demonstrações deste curso

| Afirmação | Onde foi usada | Demonstrada em |
|---|---|---|
| média minimiza a soma dos quadrados | [12](12-medidas-de-posicao.md) | §12.2 (derivada) |
| mediana minimiza a soma dos módulos | [12](12-medidas-de-posicao.md) | §12.3 (derivada de sinal) |
| `E[Σ(xᵢ−x̄)²] = (n−1)σ²` | [13](13-medidas-de-dispersao.md) | §60.2 |
| `s` é enviesado mesmo com `n−1` | [13](13-medidas-de-dispersao.md) | §60.2 (Jensen) |
| `EP = σ/√n` | [15](15-erro-e-incerteza.md), [17](17-amostragem-lgn-tcl.md) | §17.5 |
| mediana tem 64% de eficiência | [12](12-medidas-de-posicao.md) | §60.3 |
| ponto de ruptura ≤ 50% | [19](19-robustez-e-outliers.md) | §60.6 |
| propagação em quadratura | [15](15-erro-e-incerteza.md) | §60.5 (método delta) |
| bootstrap funciona | [17](17-amostragem-lgn-tcl.md) | §60.7 (plug-in + Glivenko-Cantelli) |
| média/mediana/moda como perdas | [10](10-fundamentos.md) | §60.11 |

---

## Autoteste

1. Demonstre `EQM = Var + Viés²`.
2. Demonstre a correção de Bessel.
3. Por que "grau de liberdade" é literalmente uma dimensão?
4. `s²` é não viesado mas `s` não é. Qual desigualdade explica, e qual é `c₄(2)`?
5. Enuncie o limite de Cramér-Rao. Por que a média é ótima sob normalidade?
6. A mediana tem ARE de 2/π sob normalidade. De onde vem esse número?
7. O que caracteriza formalmente um estimador robusto?
8. Por que o estimador de Huber é o compromisso padrão?
9. Cite dois casos em que o bootstrap é inconsistente.
10. Diferença entre Chebyshev e Hoeffding — e o preço da segunda.
11. Por que L-momentos são preferíveis em hidrologia?
12. O que o paradoxo de Stein implica para ranquear escolas com `n` pequeno?

<details><summary>Respostas</summary>

1. Some e subtraia `E[θ̂]` dentro do quadrado; o termo cruzado zera porque `E[θ̂ − E[θ̂]] = 0`,
   restando `Var(θ̂) + Viés²`.
2. `Σ(Xᵢ−X̄)² = Σ(Xᵢ−μ)² − n(X̄−μ)²`; tomando esperança, `nσ² − n(σ²/n) = (n−1)σ²`.
3. Porque o vetor de resíduos vive no subespaço ortogonal a `1`, de dimensão `n−1`. A norma
   quadrada esperada é proporcional à dimensão do subespaço.
4. **Desigualdade de Jensen** (a raiz é côncava, logo `E[√X] < √E[X]`).
   `c₄(2) = √(2/π) ≈ 0,7979`.
5. `Var(θ̂) ≥ 1/(n·I(θ))` para estimadores não viesados. Para a normal com σ conhecido,
   `I(μ) = 1/σ²`, e a média tem exatamente `σ²/n`: atinge o piso.
6. Da variância assintótica da mediana, `1/(4n f(m)²)`. Para a normal, `f(m) = 1/(σ√(2π))`,
   o que dá `πσ²/(2n)`; a razão com `σ²/n` é `2/π ≈ 0,637`.
7. Ter **função de influência limitada**. A da média é `x−μ` (ilimitada); a da mediana depende
   só do sinal (limitada).
8. Porque é quadrático no centro (eficiente sob normalidade, ~95% com `c = 1,345σ`) e linear
   nas caudas (função de influência limitada). Consegue quase toda a eficiência sem a
   fragilidade.
9. Estatísticas de **máximo/mínimo** (funcional não suave) e parâmetros na **fronteira** do
   espaço. Também: variância infinita, `n` minúsculo, dados dependentes.
10. Chebyshev dá decaimento **polinomial** (`1/k²`) exigindo só variância finita; Hoeffding dá
    decaimento **exponencial** (`e^(−2nt²)`) mas exige variáveis **limitadas**.
11. Porque existem sempre que a média existe, são muito menos enviesados com `n` pequeno e são
    robustos a outliers — exatamente o cenário de eventos extremos raros, em que assimetria e
    curtose convencionais fracassam.
12. Que ranquear por **média bruta** é inadmissível: encolher as estimativas na direção de uma
    média comum (modelo hierárquico / empirical Bayes) reduz o erro total, especialmente para
    as escolas com `n` pequeno, que são justamente as que ocupam os extremos de qualquer
    ranking ingênuo.

</details>

---

**Próximo:** [65-estado-da-arte.md](65-estado-da-arte.md) — onde o campo está em 2026.
