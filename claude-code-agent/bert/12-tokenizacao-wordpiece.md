# 12 · Tokenização — como texto vira número

`Nível: intermediário` · `Exemplos executados em 12/08/2026 com BERTimbau`

O assunto mais subestimado do campo. Ninguém acha tokenização interessante, e ela é a origem
de uma fração enorme dos bugs, dos custos e das limitações que você vai encontrar.

---

## 1 · O problema

Você precisa converter texto em números. Três abordagens ingênuas, e por que todas falham:

| Abordagem | Como | Por que falha |
|---|---|---|
| **Por caractere** | 'g'=1, 'a'=2, 't'=3... | vocabulário minúsculo (~100), mas sequências enormes: uma frase de 50 palavras vira 300 tokens. Custo da atenção é quadrático → inviável |
| **Por palavra** | 'gato'=157, 'cachorro'=891... | vocabulário infinito. Português tem milhões de formas flexionadas ("andaríamos", "pré-vestibulandos"). Toda palavra nova vira `[UNK]` |
| **Por raiz morfológica** | análise linguística | exige gramática por língua, quebra com erro de digitação e gíria, e não escala |

**A saída: unidades de subpalavra.** Palavras comuns viram um token só; palavras raras são
quebradas em pedaços conhecidos. O vocabulário fica fixo (~30 mil) e nada fica de fora.

```
"gato"                  → ['gato']                                   1 token
"paralelepípedo"        → ['paral','##ele','##p','##íp','##ed','##o'] 6 tokens
"asdfghjkl"             → ['as','##df','##g','##h','##j','##k','##l'] 7 tokens (nunca [UNK])
```

O prefixo `##` significa "cola no anterior, sem espaço". É como o texto é reconstruído.

---

## 2 · WordPiece: o algoritmo do BERT

BERT usa **WordPiece**, criado no Google em 2012 para reconhecimento de fala em japonês e
coreano — línguas sem espaço entre palavras. O treino do vocabulário funciona assim:

```
1. Comece com o vocabulário = todos os caracteres do corpus.
2. Repita até atingir o tamanho alvo (ex.: 30.000):
     a. Para cada par adjacente de unidades no corpus, calcule uma pontuação.
     b. Junte o par de maior pontuação numa unidade nova.
```

A pontuação é o que diferencia WordPiece de seu primo BPE:

```
                    freq(AB)
WordPiece:  score = ─────────────────      ← razão: junta o que é MUTUAMENTE informativo
                    freq(A) × freq(B)

BPE:        score = freq(AB)               ← frequência pura: junta o que é comum
```

A diferença prática: BPE juntaria "de" + "s" só por serem frequentes. WordPiece só junta se a
combinação for **mais** frequente do que se esperaria pelo acaso — o que produz pedaços com
mais cara de morfema (`##mente`, `##ção`, `##ismo`).

**Por que essa fórmula?** É a *pointwise mutual information* (informação mútua pontual), da
teoria da informação: quanto uma unidade prevê a outra além do acaso. Chegamos a uma parada
legítima: uma medida matemática bem-definida, não uma convenção arbitrária.

### Como o texto é tokenizado depois (inferência)

WordPiece usa **casamento guloso do prefixo mais longo** (*longest-match-first*):

```
Palavra: "telhados"
  Vocabulário tem "telhados"?  não
  "telhado"?                    sim  → emite 'telhado', sobra "s"
  Sobra "s" com prefixo ##:  "##s"?  sim → emite '##s'
Resultado: ['telhado', '##s']
```

Se em algum ponto nenhum prefixo casar, a palavra **inteira** vira `[UNK]`. Como todos os
caracteres do corpus estão no vocabulário, isso quase nunca acontece — exceto com caracteres
de outra escrita (chinês num modelo só-português) ou emojis.

---

## 3 · A família de tokenizadores (e por que você precisa saber)

| Algoritmo | Usado por | Característica |
|---|---|---|
| **WordPiece** | BERT, DistilBERT, BERTimbau, ELECTRA | prefixo `##`; junta por informação mútua |
| **BPE** | GPT-2, RoBERTa, ModernBERT | junta por frequência; opera sobre bytes |
| **Byte-level BPE** | GPT-2+, RoBERTa | opera em bytes UTF-8: **nunca** produz `[UNK]`, cobre qualquer caractere do planeta |
| **SentencePiece / Unigram** | XLM-R, ALBERT, T5, mmBERT (Gemma 2) | trata o espaço como caractere (`▁`); não precisa de pré-tokenização por espaço — essencial em japonês, chinês, tailandês |

**Consequência prática que pega todo mundo:** o token de máscara e os tokens especiais mudam
entre famílias.

```python
BERT:      '[CLS]'  '[SEP]'  '[MASK]'  '[PAD]'  '[UNK]'
RoBERTa:   '<s>'    '</s>'   '<mask>'  '<pad>'  '<unk>'
```

Código que escreve `"[MASK]"` como texto literal quebra silenciosamente ao trocar de modelo —
o modelo interpreta como texto comum, e você recebe resultados sem sentido em vez de um erro.

```python
mascara = tok.mask_token          # ✓ sempre certo
mascara = "[MASK]"                # ✗ quebra em RoBERTa, DeBERTa, ModernBERT
```

---

## 4 · O vocabulário é um retrato datado do corpus

Medição real, com BERTimbau (treinado em textos até ~2019):

```python
for w in ["Petrobras", "Localiza", "Braskem", "Nubank", "Hapvida"]:
    print(w, tok.tokenize(w))
```

```
Petrobras ['Petrobras']                 ← 1 token: empresa antiga, muito citada
Localiza  ['Localiza']                  ← 1 token
Braskem   ['Bras', '##ke', '##m']       ← 3 tokens
Nubank    ['Nu', '##ban', '##k']        ← 3 tokens: recente demais para o corpus
Hapvida   ['Ha', '##p', '##vida']       ← 3 tokens
```

Isso tem três consequências que importam:

1. **Custo.** Se o seu domínio está cheio de termos que o modelo estraçalha, seus textos
   consomem 2 a 3× mais tokens. Como a atenção é quadrática, isso é caro.
2. **Qualidade.** Um termo dividido em pedaços sem sentido semântico é mais difícil de
   aprender. "ICMS-ST" virando `['IC','##MS','-','ST']` não ajuda ninguém.
3. **Data de validade.** O vocabulário congela o mundo no momento do pré-treino. Nenhum
   afinamento cria tokens novos.

### Testando o seu domínio antes de escolher o modelo

Faça isto **antes** de decidir qual modelo usar — leva dois minutos e evita meses de
frustração:

```python
from transformers import AutoTokenizer

termos = ["embargos infringentes", "ICMS-ST", "eSocial", "hemograma", "estenose aórtica"]

for M in ["neuralmind/bert-base-portuguese-cased",
          "distilbert-base-multilingual-cased",
          "FacebookAI/xlm-roberta-base"]:
    tok = AutoTokenizer.from_pretrained(M)
    total = sum(len(tok.tokenize(t)) for t in termos)
    print(f"{total:3d} tokens  {M}")
    print("          ", tok.tokenize(termos[1]))
```

**Menos tokens = o modelo entende melhor o seu jargão.** Essa métrica simples (*fertilidade*
do tokenizador: tokens por palavra) prevê razoavelmente bem qual modelo vai se sair melhor no
seu domínio.

### Adicionar termos próprios

```python
tok.add_tokens(["ICMS-ST", "eSocial", "SPED"])
modelo.resize_token_embeddings(len(tok))    # OBRIGATÓRIO
```

**Vale a pena?** Opinião profissional: raramente. Os embeddings novos começam aleatórios e
precisam de muito dado para aprender algo — com poucos milhares de exemplos, o modelo aprende
menos sobre `ICMS-ST` como token novo do que já sabia sobre os pedaços. Vale quando: o termo
aparece milhares de vezes, você vai fazer MLM contínuo (ver
[06-exemplos.md, exemplo 11](06-exemplos.md#11--produção-2-adaptação-ao-domínio-com-mlm-contínuo)),
e a divisão atual é claramente ruim.

---

## 5 · As três matrizes de entrada

Antes da primeira camada, cada token vira a **soma** de três vetores de 768 dimensões:

```
      token 'gato'          posição 2            segmento A
    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
    │ E_token[15997]│  + │ E_pos[2]      │  + │ E_seg[0]      │   →  vetor de entrada
    └──────────────┘    └──────────────┘    └──────────────┘
       aprendido           aprendido            aprendido
     29.794 × 768          512 × 768             2 × 768
```

**Por que somar e não concatenar?** Concatenar triplicaria a dimensão e o custo. Somar mantém
768 e funciona porque o espaço de 768 dimensões é gigantesco — as três informações ocupam
"direções" diferentes e a rede aprende a separá-las. É contraintuitivo e é assim mesmo.

**Por que embeddings de posição *aprendidos*, se o Transformer original usava senoides?**
Os autores testaram os dois e o resultado foi equivalente; escolheram o aprendido por
simplicidade. O custo dessa escolha é rígido: a tabela tem exatamente 512 linhas, então
**o modelo não pode processar nem um token a mais**, jamais. Foi exatamente isso que o
ModernBERT corrigiu, adotando RoPE (posições rotacionais), que extrapola.

Depois da soma vêm `LayerNorm` e `dropout`, e o resultado entra na camada 1.

---

## 6 · Os tokens especiais e para que servem de verdade

| Token | id (BERT) | Função |
|---|---|---|
| `[CLS]` | 101 | primeira posição. Seu vetor de saída é usado como "resumo da sequência" na classificação |
| `[SEP]` | 102 | separa segmentos e marca o fim |
| `[PAD]` | 0 | preenchimento para igualar comprimentos no lote. Ignorado via `attention_mask` |
| `[MASK]` | 103 | o buraco a ser preenchido no pré-treino |
| `[UNK]` | 100 | token desconhecido. Raro em WordPiece, impossível em byte-BPE |

**Por que o `[CLS]` funciona como resumo?** Ele não tem significado próprio — é um token
vazio, sempre igual. Justamente por isso é um bom recipiente: durante o pré-treino da tarefa
NSP e durante o afinamento de classificação, os gradientes ensinam a atenção a **empurrar
para essa posição** a informação relevante da frase inteira.

**Mas cuidado:** num BERT que nunca foi afinado para classificação, o vetor do `[CLS]` **não**
é um bom embedding de frase. Ele foi treinado só para a tarefa NSP, que é fraca. Isso está
medido em [04-como-comecar.md](04-como-comecar.md): o `[CLS]` cru dá similaridades piores que
a média simples dos tokens.

---

## 7 · Os bugs de tokenização, e como se manifestam

| Sintoma | Causa | Correção |
|---|---|---|
| `IndexError: index out of range in self` | mais de 512 tokens | `truncation=True, max_length=512` |
| NER com rótulos deslocados | subtokens não alinhados aos rótulos | usar `word_ids()` — ver [06-exemplos.md, exemplo 9](06-exemplos.md#9--ner-próprio-com-rótulos-alinhados-a-subtokens) |
| Modelo ignora seu `[MASK]` | modelo usa `<mask>` | `tok.mask_token` |
| Acurácia despenca ao trocar de modelo | tokenizador diferente do modelo | tokenizador e modelo **sempre** do mesmo repositório |
| `IndexError` após `add_tokens` | faltou `resize_token_embeddings` | chamar após adicionar |
| Texto em maiúsculas classifica diferente | modelo `cased` | ou normalize a entrada, ou use um modelo `uncased` |
| Emojis e acentos viram `[UNK]` | WordPiece sem cobertura | use um modelo com byte-BPE, ou limpe a entrada |
| Custo/latência 3× maior que o esperado | fertilidade alta do tokenizador no seu domínio | meça a fertilidade e troque de modelo |

### `cased` × `uncased`

- **`uncased`**: converte tudo para minúsculas e **remove acentos**. `João` → `joao`.
  Vocabulário mais eficiente, mas destrói informação: para NER, maiúscula é um sinal forte
  ("Silva" é sobrenome; "silva" é vegetação).
- **`cased`**: preserva. É o certo para português (acentos distinguem palavras) e para NER.

O BERTimbau é `cased` — e essa é a escolha certa para a língua.

---

## 8 · Quanto custa cada token

Regra de bolso para planejar recursos:

```
Português comum:        1 palavra ≈ 1,3 a 1,6 tokens
Jargão técnico:         1 palavra ≈ 2 a 4 tokens
Código-fonte:           1 linha   ≈ 10 a 20 tokens
Documento A4 (~500 palavras) ≈ 700 a 800 tokens  → cabe em 1 janela de 512? NÃO
```

Um contrato de 10 páginas tem ~8.000 tokens: **16 janelas** de BERT, ou **1 janela** de
ModernBERT. É a razão prática mais forte para migrar para um encoder moderno quando o texto é
longo.

---

## Autoteste

1. Por que não tokenizar por caractere? E por palavra?
2. Qual é a diferença de fórmula entre WordPiece e BPE, e que efeito ela tem nos pedaços gerados?
3. O que significa `##` e por que ele é necessário?
4. Por que `"[MASK]"` escrito à mão é um bug em potencial?
5. Por que `Nubank` vira 3 tokens no BERTimbau e `Petrobras` vira 1?
6. Como você decidiria, em 2 minutos, qual modelo lida melhor com o jargão do seu domínio?
7. Por que os três embeddings de entrada são somados, e não concatenados?
8. Por que o limite de 512 é rígido no BERT e não no ModernBERT?
9. Quando `cased` é obrigatório?
10. Por que o vetor do `[CLS]` num BERT não afinado é um embedding de frase ruim?

---

*Anterior: [11-historia.md](11-historia.md) · Próximo: [13-arquitetura-encoder.md](13-arquitetura-encoder.md)*
