# 60 · Teoria avançada — provas, limites e o que está em aberto

`Nível: pesquisa` · `Atualizado em: 19/08/2026`

Este capítulo trata do que sustenta formalmente o campo. Não é necessário para
trabalhar; é necessário para **provar**, para publicar, e para saber quando uma
afirmação é teorema e quando é folclore.

---

## 1 · O arcabouço: espaços de Hilbert

Toda a teoria de Fourier vive num **espaço de Hilbert**: um espaço vetorial com
produto interno, completo (toda sequência de Cauchy converge).

- **L²(ℝ)** — funções de energia finita, ∫|x|² < ∞.
- **ℓ²(ℤ)** — sequências de energia finita.

**Por que isso importa e não é pedantismo:**

1. **Ortogonalidade e projeção ficam bem definidas.** "O coeficiente de Fourier é a
   projeção sobre a exponencial" é uma afirmação precisa nesse arcabouço, e é a
   base de [`12 §6`](12-matematica-do-zero.md).
2. **Completude garante que a série converge para o sinal** — em norma L², que é o
   sentido em que Fourier realmente funciona.
3. **Bases ortonormais** (Fourier, wavelets, DPSS) são todas o mesmo objeto:
   conjuntos completos ortonormais num Hilbert.

**A sutileza que separa L² de pontual:** a série de Fourier converge em L², **mas
não necessariamente ponto a ponto**. Nas descontinuidades ela converge para a
média dos limites laterais, e o **fenômeno de Gibbs** ([`13 §6`](13-sinais-e-sistemas-lti.md))
mostra que a convergência não é uniforme. Foi exatamente essa distinção que
Lagrange não tinha em 1807 ([`11`](11-historia.md)) — e o rigor levou um século
para chegar (Carleson, 1966, provou convergência quase sempre para L²).

---

## 2 · O teorema da amostragem, com rigor

**Enunciado.** Seja x ∈ L²(ℝ) com X(f) = 0 para |f| > B. Então, para T ≤ 1/(2B),

```
x(t) = Σ_n x(nT)·sinc((t − nT)/T)
```

com convergência em L² e uniforme em compactos.

**Esboço da prova.** X é suportada em [−B, B]; expanda X em série de Fourier nesse
intervalo. Os coeficientes dessa série são exatamente as amostras x(nT). Aplique a
transformada inversa, troque soma e integral (justificado pela convergência
dominada), e a integral de cada termo é a sinc. ∎

**As hipóteses e o que acontece sem elas:**

| Hipótese | Se falhar |
|---|---|
| Banda limitada | aliasing — irreversível ([`15`](15-amostragem-e-quantizacao.md)) |
| x ∈ L² | a série pode não convergir |
| Amostragem uniforme | vale a teoria de **frames** (§4); reconstrução ainda possível sob condições |

**O paradoxo escondido:** um sinal de banda limitada é **analítico**, logo não pode
ter suporte compacto no tempo. Ou seja, **nenhum sinal real satisfaz a hipótese
exatamente** — todo sinal físico começa e termina. Na prática, "banda limitada"
significa "energia desprezível acima de B", e o filtro anti-aliasing é o que
torna a aproximação válida.

### Generalizações

| Extensão | Ideia |
|---|---|
| **Amostragem passa-faixa** | fs > 2B basta, com condição de posicionamento ([`15 §3`](15-amostragem-e-quantizacao.md)) |
| **Taxa de inovação finita (FRI)** | sinais com poucos graus de liberdade por segundo (pulsos, splines) podem ser amostrados abaixo de Nyquist |
| **Compressive sensing** | sinais esparsos em alguma base, com medidas incoerentes |
| **Shift-invariant spaces** | reconstrução em espaços gerados por deslocamentos de um núcleo qualquer |

**A unificação conceitual:** todas dizem a mesma coisa em graus diferentes —
o número de amostras necessárias é o número de **graus de liberdade** do sinal,
não a largura de banda. Nyquist é o caso em que os graus de liberdade são 2B por
segundo. Se o sinal tiver menos, precisa de menos.

---

## 3 · Incerteza tempo-frequência, formalmente

**Teorema.** Para x ∈ L² com ‖x‖ = 1, definindo as dispersões em torno das médias:

```
Δt² · Δf² ≥ 1/(16π²)        ⟺        Δt·Δf ≥ 1/(4π)
```

**Prova (esboço).** Aplique Cauchy-Schwarz a ⟨t·x, x'⟩, integre por partes, e use
a propriedade da transformada da derivada. A igualdade em Cauchy-Schwarz exige que
os dois vetores sejam colineares, o que dá a equação diferencial x' = −c·t·x, cuja
solução é a **gaussiana**. ∎

**Consequência:** a gaussiana é a única minimizadora. Daí a wavelet de Morlet, a
transformada de Gabor e a janela gaussiana serem o que são.

**Versões relacionadas, mais fortes em certos sentidos:**

- **Hardy:** se x e X decaem os dois mais rápido que e^{−πt²}, então x ≡ 0.
- **Benedicks:** se os suportes de x e X têm **os dois** medida finita, x ≡ 0.
- **Donoho-Stark:** versão para concentração aproximada (ε-concentração), que é a
  ponte formal para compressive sensing.

**Benedicks é a formalização exata** do que se diz o tempo todo neste curso:
não existe sinal simultaneamente limitado no tempo e na frequência.

---

## 4 · Frames — bases sem a rigidez de base

Uma **frame** é uma família {φ_k} tal que, para todo x,

```
A·‖x‖² ≤ Σ_k |⟨x, φ_k⟩|² ≤ B·‖x‖²,      0 < A ≤ B < ∞
```

**Por que existem:** bases ortonormais são rígidas demais. Frames permitem
**redundância**, e redundância compra robustez a ruído, a perda de coeficientes e
a erro de quantização.

| Objeto | É frame? |
|---|---|
| STFT com sobreposição | sim, redundante |
| CWT | sim, muito redundante |
| DWT ortogonal | frame **justa** com A=B=1 (é base) |
| Bancos de filtros com reconstrução perfeita | frames |

**A relação A/B é o número de condição** da reconstrução: quanto mais perto de 1,
mais estável numericamente. Frames justas (A=B) reconstroem com a transposta
conjugada, exatamente como bases ortonormais.

Frames são o arcabouço que unifica STFT, wavelets e bancos de filtros num objeto
só — e é o vocabulário em que a literatura moderna de análise tempo-frequência é
escrita.

---

## 5 · Limites de estimação: Cramér-Rao

**Teorema.** Para um estimador **não enviesado** θ̂ de um parâmetro θ,

```
Var(θ̂) ≥ 1 / I(θ)          I = informação de Fisher
```

**O que ele dá de concreto** — e por isso é a ferramenta prática desta seção:
antes de escrever qualquer código, você sabe o melhor que é possível fazer.

**Exemplo canônico: estimar a frequência de uma senoide em ruído branco.**

```
Var(f̂) ≥ 6·σ² / (A²·(2π)²·N(N²−1)·T²)
```

O termo **N³** é o resultado importante: a variância cai com **N³**, não com N.
Ou seja, o desvio padrão do erro cai com N^{3/2}. Dobrar o tempo de observação
melhora a estimativa de frequência por 2,8×, não por 1,4×.

**Por que N³:** porque a informação sobre frequência está na **fase acumulada**,
que cresce linearmente com o tempo. É a mesma razão de o timing de pulsares
([`08-projeto-espacial/02`](08-projeto-espacial/02-a-fisica-do-sinal.md)) alcançar
15 casas decimais com anos de dados.

**Aplicações:** decidir se vale melhorar o algoritmo (você está longe do CRB?) ou
se o problema é físico (você já está no limite, precisa de mais SNR ou mais tempo).

⚠️ **Ressalva honesta:** o CRB vale para estimadores não enviesados e é assintótico.
Estimadores enviesados podem ter variância menor (compensando com viés); é o
princípio do *shrinkage* e da regularização.

---

## 6 · Complexidade computacional

| Problema | Melhor conhecido | Limite inferior |
|---|---|---|
| DFT de N pontos | O(N log N) | não se conhece limite geral melhor |
| DFT esparsa (k não nulos) | **O(k log N)** (Sparse FFT, MIT 2012) | Ω(k) trivialmente |
| Convolução de N | O(N log N) via FFT | idem |
| Multiplicação de inteiros | O(n log n) (Harvey–van der Hoeven, 2019) | conjecturado ótimo |
| Autovalores N×N | O(N³) prático | em aberto |

**A pergunta em aberto:** existe algoritmo para a DFT assintoticamente melhor que
N log N? **Não se sabe.** Há limites inferiores sob modelos restritos (circuitos
lineares com coeficientes limitados, Morgenstern 1973), mas nada geral.

Provar limites inferiores em complexidade aritmética é notoriamente difícil — é
parente do problema P vs NP. É uma parada legítima do tipo "problema em aberto da
matemática".

---

## 7 · Onde a teoria LTI acaba

| Classe | Ferramenta | Estado |
|---|---|---|
| LTI | Fourier, Z, Laplace | **teoria completa e fechada** |
| Linear variante no tempo | operadores pseudo-diferenciais, tempo-frequência | teoria parcial |
| Não linear com memória fraca | **séries de Volterra** | funciona para não linearidade suave; explode em complexidade |
| Não linear com histerese | Preisach, modelos de estado | específico do domínio |
| Caótico | expoentes de Lyapunov, embedding | descritivo, não construtivo |
| Aprendido (redes) | teoria de aproximação, otimização | **garantias fracas**; empírico |

**O ponto honesto:** a teoria fechada existe **só** para LTI. Tudo além é
aproximação, caso particular, ou empirismo. A estratégia dominante do campo —
aproximar localmente por LTI e tratar o resto como perturbação — é pragmática e
frequentemente correta, mas é uma escolha, não uma verdade.

Saber **onde** ela falha (transientes rápidos, não linearidade forte, sinais não
estacionários em escala comparável à janela) é o que distingue quem entende de
quem aplica receita.

---

## 8 · Problemas em aberto

1. **Limite inferior da DFT.** Existe algo melhor que N log N?
2. **Recuperação de fase** (*phase retrieval*): reconstruir um sinal só do módulo
   do espectro. Central em cristalografia e óptica; garantias ainda limitadas.
3. **Separação de fontes** com uma única gravação, sem treino, com garantias.
4. **Amostragem ótima para sinais aprendidos**: quantas medidas para reconstruir
   sinais de uma distribuição aprendida? (Ponte entre CS e modelos generativos.)
5. **Garantias para redes**: robustez, generalização, comportamento fora da
   distribuição de treino.
6. **Análise tempo-frequência sem termos cruzados e sem perda de resolução**:
   sincrossqueeze e reatribuição melhoraram muito, mas sob hipóteses.
7. **Quantização ótima** para restrições conjuntas de taxa, latência e computação
   — exatamente o tema do desafio de codecs de baixo recurso do ICASSP 2026.

---

## Autoteste

1. Em que sentido a série de Fourier converge, e por que a distinção importa?
2. Enuncie o teorema da amostragem com as hipóteses, e diga o paradoxo escondido.
3. O que Benedicks formaliza, e que afirmação deste curso ele torna teorema?
4. Prove (em esboço) que a gaussiana minimiza o produto de incerteza.
5. O que é uma frame e o que a redundância compra?
6. Por que a variância da estimativa de frequência cai com N³?
7. O que o CRB permite decidir antes de escrever código?
8. Qual é a situação do limite inferior da DFT?
9. Para que classe de sistemas existe teoria fechada, e o que se faz fora dela?
