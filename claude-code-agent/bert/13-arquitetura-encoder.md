# 13 · Arquitetura — a mecânica interna, sem caixa-preta

`Nível: intermediário → avançado` · `matemática à frente: álgebra linear básica`
`Números conferidos com PyTorch em 12/08/2026`

Este é o arquivo que abre o modelo. Ao final você deve conseguir calcular uma camada de
atenção **no papel** e explicar por que cada peça está lá.

Pré-requisito real: saber o que é multiplicação de matrizes. Se não souber, veja
[3Blue1Brown, capítulos 3 e 4](https://www.3blue1brown.com/topics/linear-algebra) (30 min) e volte.

---

## 1 · Visão de cima

```
                  entrada: 8 tokens
                        │
        [ Embeddings: token + posição + segmento ]   →  matriz 8 × 768
                        │
   ┌────────────────────▼────────────────────┐
   │  BLOCO 1                                 │
   │   ┌──────────────────────────────────┐  │
   │   │ Atenção multi-cabeça (12 cabeças)│  │
   │   └──────────────┬───────────────────┘  │
   │       + residual → LayerNorm             │
   │   ┌──────────────▼───────────────────┐  │
   │   │ Feed-Forward (768→3072→768)      │  │
   │   └──────────────┬───────────────────┘  │
   │       + residual → LayerNorm             │
   └────────────────────┬────────────────────┘
                        │  saída: matriz 8 × 768 (mesma forma!)
                  ... ×12 blocos ...
                        │
                  saída final: 8 × 768
```

**O fato mais importante da arquitetura:** cada bloco recebe uma matriz `n × 768` e devolve
uma matriz `n × 768`. A forma nunca muda. Por isso os blocos podem ser empilhados à vontade —
12, 24, 48 — sem redesenhar nada. Cada bloco **reescreve** a descrição de cada token,
enriquecendo-a com contexto.

---

## 2 · Atenção: a intuição antes da fórmula

Cada token faz três perguntas, e para isso projeta seu vetor em três papéis diferentes:

| Papel | Símbolo | Pergunta que representa | Analogia de busca |
|---|---|---|---|
| **Query** (consulta) | Q | "o que eu preciso saber?" | o que digito na busca |
| **Key** (chave) | K | "que informação eu ofereço?" | o título indexado de cada documento |
| **Value** (valor) | V | "o conteúdo que entrego" | o conteúdo do documento |

O processo, em uma frase: **cada token compara sua *query* com as *keys* de todos os tokens,
usa o resultado como peso, e soma as *values* ponderadas.**

```
"O gato que estava com medo subiu no telhado"
        ↑                              ↑
     query de "subiu": "quem é meu sujeito?"
     key de "gato": "sou um substantivo, sujeito plausível"
     → produto alto → "subiu" puxa muito do value de "gato"
     key de "telhado": "sou lugar" → produto médio
     key de "com": "sou preposição" → produto baixo
```

---

## 3 · A fórmula, e um exemplo numérico completo

$$\text{Attention}(Q,K,V) = \text{softmax}\!\left(\frac{QK^\top}{\sqrt{d_k}}\right)V$$

Vamos calcular com números pequenos. Três tokens, dimensão 4 (no BERT real seriam 64 por
cabeça — a mecânica é idêntica).

```python
import torch, math

Q = torch.tensor([[1.,0.,1.,0.],     # token 1
                  [0.,1.,0.,1.],     # token 2
                  [1.,1.,0.,0.]])    # token 3
K = Q.clone()                        # simplificação didática
V = torch.tensor([[10.,0.,0.,0.],
                  [0.,10.,0.,0.],
                  [0.,0.,10.,0.]])
```

### Passo 1 — pontuações brutas: `Q @ Kᵀ`

Cada célula `(i,j)` é o produto escalar entre a query de *i* e a key de *j*: **quanto o token
*i* se interessa pelo token *j***.

```
QKᵀ = [[2., 0., 1.],
       [0., 2., 1.],
       [1., 1., 2.]]
```

Leitura: o token 1 tem afinidade 2 consigo mesmo, 0 com o token 2 (vetores ortogonais) e 1
com o token 3.

### Passo 2 — escala: dividir por `√d_k`

```
QKᵀ/√4 = [[1.000, 0.000, 0.500],
          [0.000, 1.000, 0.500],
          [0.500, 0.500, 1.000]]
```

### Passo 3 — `softmax` por linha: pontuações viram pesos que somam 1

```
A = [[0.506, 0.186, 0.307],
     [0.186, 0.506, 0.307],
     [0.274, 0.274, 0.452]]
```

Esta é **a matriz de atenção** — a mesma que você imprimiu em
[04-como-comecar.md](04-como-comecar.md) com `output_attentions=True`. Cada linha soma 1.

### Passo 4 — média ponderada dos values: `A @ V`

```
A@V = [[5.065, 1.863, 3.072, 0.000],
       [1.863, 5.065, 3.072, 0.000],
       [2.741, 2.741, 4.519, 0.000]]
```

Pronto: essa é a saída da atenção. O token 1, que era `[1,0,1,0]`, agora carrega uma mistura
de informação dos três tokens, dominada por si mesmo (5,07) mas com contribuição real dos
outros. **Ele deixou de ser uma palavra isolada e virou uma palavra-em-contexto.**

### Por que dividir por `√d_k`? (a pergunta que separa quem entendeu de quem decorou)

Sem a divisão, a mesma conta dá:

```
softmax(QKᵀ) = [[0.665, 0.090, 0.245],
                [0.090, 0.665, 0.245],
                [0.212, 0.212, 0.576]]
```

Mais concentrado. Com `d_k` pequeno como 4 é inofensivo, mas o problema cresce com a dimensão:
o produto escalar de dois vetores aleatórios de dimensão *d* tem desvio padrão proporcional a
`√d`. Com `d=64`, as pontuações ficam na casa de ±8; com `d=768`, ±28. E o `softmax` satura:

```python
torch.softmax(torch.tensor([[10., 2., 1.]]), -1)      # → [1.000, 0.000, 0.000]
torch.softmax(torch.tensor([[10., 2., 1.]])/8, -1)    # → [0.591, 0.217, 0.192]
```

Saturado, o `softmax` vira um "máximo duro": um token recebe peso 1, os outros 0. O gradiente
nessa região é ~0, e **o modelo para de aprender**. Dividir por `√d_k` mantém a variância das
pontuações em torno de 1, independentemente da dimensão, e o gradiente vivo.

Cinco porquês encerrados numa **razão matemática**: é normalização de variância, não escolha
estética.

---

## 4 · Multi-cabeça: 12 atenções em paralelo

Uma única atenção calcula **uma** noção de relevância. Mas relações linguísticas são de vários
tipos: sujeito-verbo, substantivo-adjetivo, correferência, proximidade. Uma matriz só teria
que representar tudo ao mesmo tempo.

A solução: dividir as 768 dimensões em 12 fatias de 64, e rodar 12 atenções independentes.

```
entrada (n × 768)
   │
   ├── cabeça 1  : W_Q¹,W_K¹,W_V¹ (768×64) → atenção → n × 64
   ├── cabeça 2  : ...                                → n × 64
   ├── ...
   └── cabeça 12 : ...                                → n × 64
                                       │
                   concatena as 12 → n × 768
                                       │
                   projeta com W_O (768×768) → n × 768
```

Custo total: **igual** ao de uma única atenção de 768 dimensões (12 × 64 = 768). Você ganha
diversidade de graça. Essa é a elegância do desenho.

Estudos de interpretabilidade mostraram que cabeças diferentes de fato se especializam —
uma segue o token seguinte, outra liga verbo ao objeto direto, outra rastreia correferência.
Também mostraram que **muitas cabeças são redundantes**: dá para podar boa parte sem perda
significativa (Michel et al., 2019). Ver
[20-interpretabilidade-e-bertologia.md](20-interpretabilidade-e-bertologia.md).

### Contagem de parâmetros da atenção (por bloco)

```
W_Q, W_K, W_V:  3 × (768 × 768)  = 1.769.472
W_O:                768 × 768    =   589.824
vieses:             4 × 768      =     3.072
                                  ───────────
                                   2.362.368  ≈ 2,36 M por bloco
```

---

## 5 · A camada feed-forward: onde mora o conhecimento

Depois da atenção, cada token passa **sozinho** (sem olhar os outros) por uma rede de duas
camadas:

$$\text{FFN}(x) = W_2 \cdot \text{GELU}(W_1 x + b_1) + b_2$$

```
768 →  W₁ (768×3072)  → 3072 → GELU → W₂ (3072×768) → 768
        expande 4×                      comprime de volta
```

Parâmetros: `768×3072 + 3072×768 ≈ 4,72 M` por bloco — **o dobro da atenção**. Somando os 12
blocos, a FFN é cerca de 2/3 de todo o modelo.

**Isso é contraintuitivo e importante:** a atenção é a parte famosa, mas a maior parte da
capacidade do BERT está nessas camadas densas. Trabalhos de 2021–2022 (Geva et al.)
mostraram evidência de que as FFNs funcionam como **memórias associativas chave-valor**: cada
neurônio da camada de 3072 dispara para um padrão específico de entrada e escreve um conjunto
de informações na saída. É provavelmente ali que ficam guardados os fatos ("a capital da
França é Paris").

**Por que expandir 4×?** Herança do Transformer original, sem justificativa teórica forte.
Testes posteriores mostraram que a razão importa pouco entre 2× e 8×. É uma **convenção
arbitrária**, e vale dizer isso em vez de inventar uma razão.

**Por que GELU e não ReLU?** GELU (*Gaussian Error Linear Unit*) é uma versão suave da ReLU:
em vez de zerar bruscamente os negativos, ela os amortece de forma contínua. Na prática rende
um ganho pequeno e consistente; a justificativa teórica é fraca, e a adoção foi empírica.

---

## 6 · Conexões residuais e LayerNorm

Cada sub-camada é embrulhada assim:

```
x → sub-camada → soma com x (residual) → LayerNorm
```

### Residual: `saída = x + f(x)`

**Por que somar a entrada de volta?** Sem isso, uma rede de 12 blocos não treina: o gradiente
precisa atravessar 24 sub-camadas de trás para frente, e a cada uma ele é multiplicado por
algo — se esse algo for menor que 1, o produto some (*vanishing gradient*).

Com a conexão residual, a derivada de `x + f(x)` em relação a `x` é `1 + f'(x)`. Aquele **1**
é uma via expressa por onde o gradiente passa intacto até as camadas de baixo. É a ideia da
ResNet (visão computacional, 2015) transplantada para linguagem, e é o que torna redes
profundas treináveis.

**Outra leitura, mais bonita:** o residual faz cada bloco *editar* a representação em vez de
*substituí-la*. A informação original nunca se perde; cada camada adiciona uma correção. Isso
sustenta a metáfora do "fluxo residual" usada em interpretabilidade moderna.

### LayerNorm

Normaliza cada vetor de token para média 0 e desvio 1, e depois aplica escala e deslocamento
aprendidos:

$$\text{LN}(x) = \gamma \cdot \frac{x - \mu}{\sqrt{\sigma^2 + \epsilon}} + \beta$$

Impede que os valores explodam ou encolham ao longo de 12 blocos, e estabiliza o treino.

**Por que LayerNorm e não BatchNorm?** BatchNorm normaliza pela estatística do *lote*, o que
exige lotes grandes e comportamento diferente entre treino e inferência. Pior: em texto, os
exemplos do lote têm comprimentos diferentes, cheios de padding, e a estatística fica
corrompida. LayerNorm normaliza **dentro de cada token**, é independente do lote, e se
comporta igual em treino e em produção. Para sequências, a escolha é praticamente forçada.

### Post-LN × Pre-LN (detalhe que aparece nos modelos modernos)

```
BERT (2018), post-LN:   x → LN(x + Atenção(x))
Modelos modernos, pre-LN: x → x + Atenção(LN(x))
```

Post-LN precisa de *warmup* na taxa de aprendizado, senão diverge — é por isso que o BERT tem
`warmup_steps`. Pre-LN é mais estável e treina sem warmup, e virou padrão a partir de ~2020.
ModernBERT usa pre-LN.

---

## 7 · O bloco inteiro, em código executável

Implementação didática de um bloco, com PyTorch puro. Roda:

```python
import torch, torch.nn as nn, math

class Atencao(nn.Module):
    def __init__(self, d=768, cabecas=12):
        super().__init__()
        self.h, self.dk = cabecas, d // cabecas
        self.q, self.k, self.v, self.o = (nn.Linear(d, d) for _ in range(4))

    def forward(self, x, mascara=None):
        B, N, D = x.shape
        # (B,N,D) → (B, cabeças, N, dk)
        forma = lambda t: t.view(B, N, self.h, self.dk).transpose(1, 2)
        q, k, v = forma(self.q(x)), forma(self.k(x)), forma(self.v(x))

        pont = (q @ k.transpose(-2, -1)) / math.sqrt(self.dk)     # (B,h,N,N)
        if mascara is not None:
            # -inf nas posições de padding: viram 0 depois do softmax
            pont = pont.masked_fill(mascara[:, None, None, :] == 0, float("-inf"))
        att = pont.softmax(-1)

        y = (att @ v).transpose(1, 2).reshape(B, N, D)            # junta as cabeças
        return self.o(y)

class Bloco(nn.Module):
    def __init__(self, d=768, cabecas=12, ffn=3072):
        super().__init__()
        self.att, self.ln1 = Atencao(d, cabecas), nn.LayerNorm(d)
        self.ffn = nn.Sequential(nn.Linear(d, ffn), nn.GELU(), nn.Linear(ffn, d))
        self.ln2 = nn.LayerNorm(d)

    def forward(self, x, mascara=None):
        x = self.ln1(x + self.att(x, mascara))    # post-LN, como no BERT original
        x = self.ln2(x + self.ffn(x))
        return x

# teste
bloco = Bloco()
entrada = torch.randn(2, 10, 768)                 # 2 frases, 10 tokens, 768 dims
print(bloco(entrada).shape)
print(f"{sum(p.numel() for p in bloco.parameters())/1e6:.2f}M parâmetros no bloco")
```

**Saída real:**

```
torch.Size([2, 10, 768])
7.09M parâmetros no bloco
```

Os 7,09 M conferem com a tabela da seção 10: 2,36 M da atenção + 4,72 M da FFN.

Empilhe 12 desses, acrescente os embeddings da seção 5 de
[12-tokenizacao-wordpiece.md](12-tokenizacao-wordpiece.md), e você tem um BERT. Não é mais do
que isso.

---

## 8 · A máscara de atenção (e por que ela é obrigatória)

Num lote, textos têm comprimentos diferentes e os curtos ganham `[PAD]`. Sem intervenção, os
tokens reais prestariam atenção no lixo do padding.

```
"o sistema caiu"                → [CLS] o sistema caiu [SEP] [PAD] [PAD]
attention_mask                  →   1   1    1      1     1     0     0
```

O truque de implementação: somar `-inf` às pontuações das posições mascaradas **antes** do
softmax. `softmax(-inf) = 0`, então o peso vira exatamente zero.

Esquecer a `attention_mask` num lote com padding é um bug clássico: o modelo funciona, não
lança erro, e a qualidade cai de forma inexplicável. Passar sempre `**entradas` (com todas as
chaves do tokenizador) evita isso.

---

## 9 · O custo quadrático — de onde vem e o que fazer

A matriz `QKᵀ` tem forma `n × n`. Com 12 cabeças e 12 camadas, são `144 × n²` valores.

| Tokens | Células por cabeça | Memória relativa |
|---|---|---|
| 128 | 16.384 | 1× |
| 256 | 65.536 | 4× |
| 512 | 262.144 | **16×** |
| 8.192 (ModernBERT) | 67.108.864 | 4.096× |

É por isso que dobrar `max_length` mais que dobra o custo, e por que o BERT parou em 512.

**As saídas encontradas pelo campo:**

| Técnica | Ideia | Quem usa |
|---|---|---|
| **Flash Attention** | não materializa a matriz `n×n` na memória; calcula por blocos | ModernBERT, todos os modelos modernos |
| **Atenção local** | cada token só olha uma janela de ±128 vizinhos | Longformer, ModernBERT (alterna local e global) |
| **Atenção esparsa** | padrões fixos (blocos, aleatório, global) | BigBird |
| **Aproximação de baixo posto** | aproxima a matriz por fatoração | Linformer, Performer |
| **Unpadding** | remove tokens de padding antes de computar | ModernBERT |

O ModernBERT combina Flash Attention + local/global + unpadding, e é por isso que consegue
8.192 tokens com velocidade **maior** que a do BERT em 512.

---

## 10 · Onde estão os 110 milhões de parâmetros

| Componente | Conta | Parâmetros | % |
|---|---|---|---|
| Embeddings de token | 30.522 × 768 | 23,4 M | 21% |
| Embeddings de posição | 512 × 768 | 0,4 M | 0,4% |
| Embeddings de segmento | 2 × 768 | 0,002 M | ~0% |
| Atenção (12 blocos) | 12 × 2,36 M | 28,3 M | 26% |
| Feed-forward (12 blocos) | 12 × 4,72 M | 56,7 M | **52%** |
| LayerNorms, pooler | — | ~0,6 M | 0,6% |
| **Total** | | **~109,5 M** | 100% |

Duas surpresas para quem só conhece a fama da atenção:

1. **A FFN é metade do modelo.** A atenção mistura informação; a FFN a processa e armazena.
2. **A tabela de embeddings é 1/5 do modelo** e é pura consulta — nenhuma computação. Foi
   exatamente aí que o ALBERT atacou, fatorando essa matriz para reduzir o tamanho.

---

## Autoteste

1. Por que a saída de cada bloco tem exatamente a mesma forma da entrada, e por que isso importa?
2. Explique Q, K e V com a analogia de busca.
3. Calcule à mão: com `Q·Kᵀ = [[2,0],[0,2]]` e `d_k = 4`, qual é a matriz de atenção após escala e softmax?
4. O que acontece com o gradiente se você remover a divisão por `√d_k`?
5. Por que 12 cabeças de 64 custam o mesmo que 1 cabeça de 768?
6. Qual componente tem mais parâmetros: atenção ou feed-forward? Por quanto?
7. Por que a conexão residual é o que permite empilhar 12 blocos?
8. Por que LayerNorm e não BatchNorm em texto? Dê dois motivos.
9. Como a `attention_mask` é implementada matematicamente, e o que quebra se você esquecê-la?
10. Por que passar de 128 para 512 tokens custa 16× mais na atenção, e não 4×?

---

## Fontes

- Vaswani et al. (2017). *Attention Is All You Need*. [arXiv:1706.03762](https://arxiv.org/abs/1706.03762)
- Devlin et al. (2019). *BERT*. [aclanthology.org/N19-1423](https://aclanthology.org/N19-1423/)
- Michel, Levy & Neubig (2019). *Are Sixteen Heads Really Better than One?* [arXiv:1905.10650](https://arxiv.org/abs/1905.10650)
- Geva et al. (2021). *Transformer Feed-Forward Layers Are Key-Value Memories*. [arXiv:2012.14913](https://arxiv.org/abs/2012.14913)
- Dao et al. (2022). *FlashAttention*. [arXiv:2205.14135](https://arxiv.org/abs/2205.14135)
- Alammar. *The Illustrated Transformer*. [jalammar.github.io](https://jalammar.github.io/illustrated-transformer/)

---

*Anterior: [12-tokenizacao-wordpiece.md](12-tokenizacao-wordpiece.md) · Próximo: [14-pre-treino-mlm-nsp.md](14-pre-treino-mlm-nsp.md)*
