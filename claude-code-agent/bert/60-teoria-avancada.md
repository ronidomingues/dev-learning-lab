# 60 · Teoria avançada — matemática, provas e limites

`Nível: pesquisa` · `matemática à frente: álgebra linear, cálculo, probabilidade`
`Última atualização: 12/08/2026`

Este arquivo é opcional para quem quer usar BERT, e obrigatório para quem quer criar algo
novo ou ler papers com senso crítico. Todo resultado citado tem fonte.

---

## 1 · A atenção como operação matemática

### Formulação completa

Para uma sequência de $n$ tokens com representações $X \in \mathbb{R}^{n \times d}$:

$$Q = XW^Q,\quad K = XW^K,\quad V = XW^V, \qquad W^Q, W^K \in \mathbb{R}^{d \times d_k},\ W^V \in \mathbb{R}^{d \times d_v}$$

$$\text{Attn}(X) = \underbrace{\text{softmax}\!\left(\frac{QK^\top}{\sqrt{d_k}}\right)}_{A \in \mathbb{R}^{n\times n}} V$$

Propriedades de $A$:
- **Estocástica por linhas**: $A_{ij} \ge 0$ e $\sum_j A_{ij} = 1$. Cada linha é uma
  distribuição de probabilidade sobre as posições.
- **Não simétrica**: $A_{ij} \neq A_{ji}$ em geral. "Ele" atender a "João" não implica o
  contrário — o que é linguisticamente correto.
- **Posto limitado**: como $d_k = 64 < n$ tipicamente, a matriz $QK^\top$ tem posto no máximo
  $d_k$. Isso restringe formalmente quais padrões de atenção são representáveis por uma
  cabeça (Bhojanapalli et al., 2020) — e é um dos argumentos formais a favor de multi-cabeça.

### Por que $\sqrt{d_k}$: a derivação

Sejam $q, k \in \mathbb{R}^{d_k}$ com componentes i.i.d., média 0 e variância 1. Então

$$\mathbb{E}[q \cdot k] = 0, \qquad \operatorname{Var}(q \cdot k) = \sum_{i=1}^{d_k} \operatorname{Var}(q_i k_i) = d_k$$

O desvio padrão é $\sqrt{d_k}$. Sem normalizar, as entradas do softmax crescem como
$\sqrt{d_k}$; com $d_k = 64$, isso é ±8, e o softmax satura.

**Por que saturar é fatal:** o jacobiano do softmax é
$\partial p_i/\partial z_j = p_i(\delta_{ij} - p_j)$. Quando $p_i \to 1$ e os demais $\to 0$,
todas as derivadas tendem a 0 — gradiente nulo, aprendizado paralisado. Dividir por
$\sqrt{d_k}$ mantém $\operatorname{Var} \approx 1$ e o gradiente vivo.

**Esta é uma parada legítima: uma razão matemática, não uma convenção.**

---

## 2 · Complexidade

| Operação | Tempo | Memória |
|---|---|---|
| $QK^\top$ | $O(n^2 d)$ | $O(n^2)$ |
| $AV$ | $O(n^2 d)$ | $O(nd)$ |
| Feed-forward | $O(n d^2)$ | $O(nd)$ |
| **Camada completa** | $O(n^2 d + n d^2)$ | $O(n^2 + nd)$ |

Ponto de equilíbrio: a atenção domina a FFN quando $n > d$. Com $d = 768$, sequências abaixo
de ~768 tokens são dominadas pela **FFN**, não pela atenção — contrariando a intuição comum.
É por isso que otimizar a atenção rende pouco em textos curtos, e muito em textos longos.

**Limite inferior condicional:** sob a hipótese SETH (*Strong Exponential Time Hypothesis*),
não existe algoritmo de atenção exata em tempo subquadrático quando as entradas têm magnitude
não limitada (Keles, Wijewardena & Hedge, 2022). Aproximações em tempo quase linear existem
sob a hipótese adicional de entradas limitadas (Alman & Song, 2023).

**Consequência conceitual:** Flash Attention **não** quebra a barreira quadrática — ela
continua $O(n^2)$ em tempo. O que ela evita é materializar a matriz $n \times n$ na memória
lenta da GPU, reduzindo o custo de $O(n^2)$ para $O(n)$ em memória e ganhando muito em prática
por ser *IO-aware*. É um ganho de constante e de memória, não de classe de complexidade — e
essa distinção é frequentemente perdida em discussões informais.

---

## 3 · Expressividade

### Transformers são Turing-completos (com ressalvas)

Pérez, Marinković & Barceló (2019) provaram que Transformers com atenção *hard* e precisão
arbitrária são Turing-completos. A prova depende de duas hipóteses irrealistas: precisão
infinita e número ilimitado de passos de decodificação.

Com precisão **finita** e profundidade **constante** — o caso real — o quadro muda: Hahn
(2020) mostrou que Transformers de atenção suave não conseguem reconhecer certas linguagens
formais simples, como PARITY (a paridade do número de 1s numa cadeia) e a linguagem de
parênteses balanceados, de forma robusta com o crescimento do comprimento.

**Resultado mais forte e mais recente:** Merrill & Sabharwal (2023) mostraram que
Transformers de profundidade constante com precisão logarítmica são simuláveis em
$\mathsf{TC}^0$ — uma classe de circuitos muito restrita, que **não** contém problemas
$\mathsf{NC}^1$-completos como avaliação de fórmulas booleanas.

**Tradução:** um encoder de profundidade fixa **não pode**, por construção, resolver problemas
que exijam computação sequencial profunda. Contar sem limite, avaliar expressões aninhadas
arbitrariamente, seguir uma cadeia longa de deduções — nada disso está no alcance de uma
passada de 12 camadas. Não é questão de treinar melhor ou de ter mais dados: é limitação de
classe de complexidade.

Isso explica formalmente por que "cadeia de pensamento" ajuda modelos generativos: gerar
tokens intermediários dá ao modelo **profundidade computacional adaptativa**, o que uma única
passada de encoder não tem. E explica por que essa técnica **não tem análogo** no BERT.

---

## 4 · MLM como estimador: pseudo-verossimilhança

Um modelo autorregressivo fatora a probabilidade conjunta exatamente:

$$\log P(x_1,\dots,x_n) = \sum_{i=1}^n \log P(x_i \mid x_{<i})$$

O MLM **não** fornece essa fatoração. O que ele estima são as condicionais
$P(x_i \mid x_{\setminus i})$, e o objeto natural é a **pseudo-log-verossimilhança**:

$$\text{PLL}(x) = \sum_{i=1}^n \log P(x_i \mid x_{\setminus i})$$

Isso é uma pseudo-verossimilhança no sentido de Besag (1975). Fatos relevantes:

- **Não é** $\log P(x)$, e em geral não é proporcional a ela.
- Sob condições de regularidade, o estimador de máxima pseudo-verossimilhança é **consistente**
  — converge para o parâmetro verdadeiro com dados suficientes. Essa é a justificativa
  estatística formal do MLM.
- É **menos eficiente** que a máxima verossimilhança: exige mais dados para a mesma precisão.
- Wang & Cho (2019) mostraram que um MLM define um **campo aleatório de Markov** sobre a
  sequência, e que amostrar dele é possível, embora custoso e mal comportado.
- Salazar et al. (2020) formalizaram o uso da PLL para reordenar hipóteses, e mostraram que
  ela funciona bem empiricamente — apesar de não ser uma verossimilhança de verdade.

**A ligação entre "estimar condicionais" e "produzir boas representações" é onde a teoria
ainda é fraca.** Existem resultados parciais; ver seção 6.

---

## 5 · Geometria do espaço de representações

### Anisotropia

Ethayarajh (2019) mediu a similaridade cosseno **esperada entre palavras aleatórias** nas
representações contextuais. Se o espaço fosse isotrópico (direções uniformemente ocupadas),
esse valor seria próximo de 0. Nos modelos, é alto — e cresce nas camadas superiores.

Consequências:
1. O cosseno cru é uma medida enviesada de similaridade — tudo parece parecido.
2. Isso explica formalmente por que o BERT cru é ruim em busca semântica
   ([16-embeddings-e-busca-semantica.md](16-embeddings-e-busca-semantica.md)).
3. Correções propostas: remoção das componentes principais dominantes (*all-but-the-top*),
   normalização por fluxo (BERT-flow), branqueamento (BERT-whitening) e — o que funcionou
   melhor — treinamento contrastivo (SimCSE, Sentence-BERT).

### Por que o contrastivo corrige a geometria

Wang & Isola (2020) decompuseram a perda contrastiva em dois termos com interpretação
geométrica clara:

- **Alinhamento**: pares positivos devem ficar próximos.
- **Uniformidade**: as representações devem se espalhar uniformemente na hipersfera.

O segundo termo é literalmente um antídoto contra a anisotropia — ele penaliza a concentração.
Não é acidente que o treino contrastivo resolva o problema: ele otimiza exatamente a
propriedade que faltava.

---

## 6 · Por que o pré-treino funciona? (teoria parcial)

O problema teórico central do campo, e ainda em aberto. Três linhas de ataque:

**1. Teoria de aprendizado contrastivo** (Arora et al., 2019). Sob a hipótese de que os dados
vêm de classes latentes e que pares positivos vêm da mesma classe, é possível **provar** que
a perda contrastiva limita superiormente o erro de um classificador linear treinado depois.
É o resultado formal mais próximo de uma explicação — mas as hipóteses são fortes e não se
verificam em texto real.

**2. Hipótese distribucional formalizada.** Se o significado é uma função do contexto de
ocorrência, e o MLM modela exatamente a distribuição condicional dada o contexto, então a
representação suficiente para o MLM é suficiente para tarefas que dependem do significado.
O argumento é sedutor e circular na medida em que assume o que quer provar.

**3. Escala e leis de potência.** Kaplan et al. (2020) e Hoffmann et al. (2022, "Chinchilla")
mostraram que a perda decai como lei de potência em parâmetros, dados e cálculo. São leis
**empíricas** notavelmente robustas, sem derivação a partir de princípios. Chinchilla é
particularmente relevante aqui: mostrou que os modelos da época estavam **subtreinados em
dados** para seu tamanho — exatamente o diagnóstico que o RoBERTa fizera para o BERT três
anos antes, agora com uma lei quantitativa.

**Estado honesto da questão:** sabemos *que* funciona, sabemos *como escalar*, e não sabemos
*por que* as representações transferem tão bem. Desconfie de qualquer texto que afirme o
contrário.

---

## 7 · Detalhes de otimização que a teoria explica

### Por que warmup é necessário no BERT

O BERT usa **post-LN** (normalização depois da soma residual). Xiong et al. (2020) mostraram
que, nessa configuração, a norma esperada do gradiente nas camadas de saída cresce com a
profundidade na inicialização. Passos grandes no início desestabilizam irreversivelmente o
treino. O warmup — subir a taxa de aprendizado gradualmente — contorna isso.

Com **pre-LN**, os autores provaram que os gradientes ficam bem comportados na inicialização,
e **o warmup se torna desnecessário**. É por isso que os modelos modernos (inclusive o
ModernBERT) adotaram pre-LN: não é moda, é consequência de um resultado.

### AdamW e o desacoplamento do weight decay

Loshchilov & Hutter (2019) mostraram que, no Adam, a regularização L2 adicionada ao gradiente
**não** é equivalente ao decaimento de peso, porque o gradiente é dividido pela raiz da média
quadrática — parâmetros com gradiente grande recebem menos regularização, o que não é o que se
quer. AdamW desacopla: aplica o decaimento diretamente ao peso. É a razão de todo treino de
Transformer usar AdamW e não Adam.

---

## 8 · Limites fundamentais, resumidos

| Limite | Origem | É superável? |
|---|---|---|
| Atenção exata é $\Omega(n^2)$ | SETH (Keles et al., 2022) | não, sem aproximar |
| Profundidade constante ⊆ $\mathsf{TC}^0$ | Merrill & Sabharwal (2023) | não, para profundidade fixa |
| Não conta nem reconhece PARITY robustamente | Hahn (2020) | parcialmente, com arquitetura diferente |
| Vocabulário fixo no pré-treino | design | não, sem retreinar embeddings |
| PLL ≠ verossimilhança | Besag (1975) | não, é propriedade do objetivo |
| Sem raciocínio multi-passo | consequência de $\mathsf{TC}^0$ | não em uma passada; sim com iteração externa |

---

## 9 · Problemas em aberto

1. **Teoria da transferência.** Por que representações de MLM transferem para tarefas tão
   diversas? Não há resposta satisfatória.
2. **Por que 15% (ou 40%)?** Não existe derivação do nível ótimo de mascaramento a partir de
   princípios; só medição.
3. **Instabilidade do afinamento.** Documentada, sem teoria.
4. **Encoder × decoder para compreensão.** Em que condições um encoder bidirecional é
   provavelmente superior? Há intuição, não teorema.
5. **Localização de conhecimento.** Onde um fato está armazenado, e por que a edição de
   conhecimento às vezes falha catastroficamente?
6. **Emergência de estrutura sintática.** Por que a hierarquia de camadas replica o pipeline
   clássico de PLN? É propriedade dos dados, do objetivo, ou da arquitetura?

---

## Autoteste

1. Derive a variância do produto escalar de dois vetores aleatórios de dimensão $d_k$ e explique o fator $1/\sqrt{d_k}$.
2. Por que o gradiente do softmax desaparece quando ele satura? Escreva o jacobiano.
3. Para $d = 768$, a partir de que comprimento a atenção domina a FFN em custo?
4. Flash Attention quebra a barreira quadrática? Justifique.
5. O que significa dizer que Transformers de profundidade constante estão em $\mathsf{TC}^0$?
6. Por que "cadeia de pensamento" ajuda decoders e não tem análogo em encoders?
7. O que é pseudo-verossimilhança, e qual propriedade estatística justifica o MLM?
8. O que é anisotropia, e como o treino contrastivo a corrige — formalmente?
9. Por que o post-LN exige warmup e o pre-LN não?
10. Por que AdamW e não Adam?
11. Cite dois problemas genuinamente em aberto na teoria do pré-treino.

---

## Fontes

- Vaswani et al. (2017). *Attention Is All You Need*. [arXiv:1706.03762](https://arxiv.org/abs/1706.03762)
- Hahn (2020). *Theoretical Limitations of Self-Attention*. [arXiv:1906.06755](https://arxiv.org/abs/1906.06755)
- Pérez, Marinković & Barceló (2019). *On the Turing Completeness of Modern Neural Network Architectures*. [arXiv:1901.03429](https://arxiv.org/abs/1901.03429)
- Merrill & Sabharwal (2023). *The Parallelism Tradeoff: Limitations of Log-Precision Transformers*. [arXiv:2207.00729](https://arxiv.org/abs/2207.00729)
- Keles, Wijewardena & Hedge (2022). *On the Computational Complexity of Self-Attention*. [arXiv:2209.04881](https://arxiv.org/abs/2209.04881)
- Dao et al. (2022). *FlashAttention*. [arXiv:2205.14135](https://arxiv.org/abs/2205.14135)
- Besag (1975). *Statistical Analysis of Non-Lattice Data*.
- Wang & Cho (2019). *BERT has a Mouth, and It Must Speak*. [arXiv:1902.04094](https://arxiv.org/abs/1902.04094)
- Salazar et al. (2020). *Masked Language Model Scoring*. [arXiv:1910.14659](https://arxiv.org/abs/1910.14659)
- Ethayarajh (2019). *How Contextual are Contextualized Word Representations?* [arXiv:1909.00512](https://arxiv.org/abs/1909.00512)
- Wang & Isola (2020). *Understanding Contrastive Representation Learning through Alignment and Uniformity*. [arXiv:2005.10242](https://arxiv.org/abs/2005.10242)
- Arora et al. (2019). *A Theoretical Analysis of Contrastive Unsupervised Representation Learning*. [arXiv:1902.09229](https://arxiv.org/abs/1902.09229)
- Xiong et al. (2020). *On Layer Normalization in the Transformer Architecture*. [arXiv:2002.04745](https://arxiv.org/abs/2002.04745)
- Loshchilov & Hutter (2019). *Decoupled Weight Decay Regularization* (AdamW). [arXiv:1711.05101](https://arxiv.org/abs/1711.05101)
- Hoffmann et al. (2022). *Training Compute-Optimal Large Language Models* (Chinchilla). [arXiv:2203.15556](https://arxiv.org/abs/2203.15556)
- Bhojanapalli et al. (2020). *Low-Rank Bottleneck in Multi-head Attention Models*. [arXiv:2002.07028](https://arxiv.org/abs/2002.07028)

---

*Anterior: [20-interpretabilidade-e-bertologia.md](20-interpretabilidade-e-bertologia.md) · Próximo: [65-estado-da-arte.md](65-estado-da-arte.md)*
