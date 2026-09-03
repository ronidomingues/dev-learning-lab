# 10 · Fundamentos — vocabulário, modelos mentais e a ideia central

`Nível: iniciante → intermediário` · `Última atualização: 12/08/2026`

Aqui os termos ganham definição precisa. Tudo que vem depois no Bloco B assume este arquivo.
Se um termo aparecer sem definição em qualquer arquivo do curso, ele está no
[GLOSSARIO.md](GLOSSARIO.md) — e isso é um erro meu, não seu.

---

## 1 · O problema que todo modelo de linguagem resolve

Computador só sabe fazer aritmética. Texto não é aritmética. A pergunta fundadora do campo é:

> **Como transformar palavras em números, de forma que a aritmética sobre esses números
> corresponda a algo do significado?**

Toda a história do PLN (Processamento de Linguagem Natural) é uma sequência de respostas cada
vez melhores a essa pergunta. Quatro gerações:

| Geração | Como representa "gato" | Problema que resolve | Problema que deixa |
|---|---|---|---|
| **One-hot** (anos 1960–2000) | `[0,0,...,1,...,0]` — 1 na posição do gato | é simples e exato | "gato" e "felino" são igualmente distantes de tudo |
| **Contagem / TF-IDF** (1970–2010) | frequências no documento | busca funciona | ignora ordem e sinônimo |
| **Embedding estático** (2013, word2vec) | `[0.2, -0.7, 0.1, ...]` — 300 números fixos | sinônimos ficam próximos | "banco" tem **um** vetor para os dois sentidos |
| **Embedding contextual** (2018, ELMo/BERT) | 768 números **que mudam conforme a frase** | resolve ambiguidade | caro; janela limitada |

BERT é a quarta geração feita direito. Toda a discussão técnica deste curso é sobre **como**
ele produz o vetor contextual e **por que** isso funciona tão bem.

---

## 2 · Os treze termos que você precisa

Definições operacionais. Cada uma com exemplo imediatamente depois.

### **Token**
A menor unidade que o modelo enxerga. Não é palavra, não é letra — é o que o tokenizador
decidiu. Pode ser uma palavra inteira, um pedaço dela, ou um sinal de pontuação.

```
"O paralelepípedo caiu" → ['O', 'paral', '##ele', '##p', '##íp', '##ed', '##o', 'caiu']
```

### **Vocabulário**
A lista fechada de todos os tokens que o modelo conhece. Tem tamanho fixo, definido antes do
pré-treino. BERT-base inglês: 30.522 entradas. BERTimbau: 29.794. Nada fora dessa lista
existe para o modelo — texto novo é sempre decomposto em pedaços que estão nela.

### **Embedding**
Um vetor de números reais que representa alguma coisa. "Embedding de token" = vetor de um
token. A dimensão é uma escolha de projeto: 768 no BERT-base, 1024 no BERT-large.

```
'gato' → [0.11, -0.42, 0.87, ..., 0.03]      ← 768 números
```

### **Embedding estático × contextual**
- **Estático** (word2vec, GloVe): um vetor por palavra, gravado numa tabela. Consulta.
- **Contextual** (BERT): o vetor é **calculado** a cada uso, olhando a frase inteira.
  Mesma palavra, frases diferentes, vetores diferentes — medido em
  [06-exemplos.md, exemplo 7](06-exemplos.md#7--a-mesma-palavra-com-dois-sentidos).

### **Parâmetro (peso)**
Um número que o modelo aprendeu durante o treino e usa em suas contas. "BERT-base tem 110
milhões de parâmetros" quer dizer: 110 milhões de números ajustáveis. É o tamanho do modelo.

### **Atenção (*attention*)**
O mecanismo pelo qual cada token olha para todos os outros e decide de quais vai "puxar"
informação para se descrever melhor. É a peça central; o cálculo está em
[13-arquitetura-encoder.md](13-arquitetura-encoder.md).

Intuição: ao processar "ele" em *"João chegou tarde porque **ele** perdeu o ônibus"*, o token
"ele" presta muita atenção em "João" e pouca em "ônibus". O resultado é que o vetor de "ele"
passa a carregar informação sobre João.

### **Encoder × Decoder**
- **Encoder**: lê a sequência inteira de uma vez, cada token vê todos os outros
  (bidirecional). É o BERT.
- **Decoder**: lê da esquerda para a direita, cada token só vê os anteriores (causal,
  autorregressivo). É o GPT.
- **Encoder-decoder**: os dois juntos. É o T5, e era o Transformer original de 2017.

### **Pré-treino (*pre-training*)**
A fase cara: o modelo aprende a língua em bilhões de palavras de texto cru, sem rótulo humano,
resolvendo uma tarefa artificial (para o BERT: adivinhar palavras escondidas). Feito uma vez,
por quem tem dinheiro, e distribuído para todo mundo.

### **Afinamento (*fine-tuning*)**
A fase barata: pegar o modelo pré-treinado e continuar treinando por pouco tempo na **sua**
tarefa, com **seus** dados rotulados. Minutos a horas. É o que você vai fazer.

### **Cabeça (*head*)**
A camada final, pequena, que converte os vetores do BERT no formato da sua tarefa. Uma cabeça
de classificação com 4 classes é uma matriz 768×4 — cerca de 3.000 parâmetros, contra 110
milhões do tronco. Trocar de tarefa = trocar a cabeça.

### **Logit**
A saída crua da cabeça, antes de virar probabilidade. Varia de −∞ a +∞. `softmax` converte
logits num conjunto de probabilidades que soma 1.

### **Perda (*loss*)**
Um número que mede o quanto o modelo errou. Treinar = ajustar os parâmetros para reduzi-lo.
Para classificação, a perda padrão é a **entropia cruzada**.

### **Época (*epoch*)**
Uma passada completa por todos os dados de treino. "3 épocas" = o modelo viu cada exemplo
três vezes.

---

## 3 · O modelo mental central: a fábrica de vetores em 12 andares

Guarde esta imagem. Ela é suficiente para 90% do trabalho prático.

```
                       ENTRADA: "O gato subiu no telhado"
                                     │
      ┌──────────────────────────────▼──────────────────────────────┐
      │ TOKENIZADOR: texto → ids                                     │
      │ [CLS] O gato subiu no telhado [SEP]  →  101 231 15997 ...     │
      └──────────────────────────────┬──────────────────────────────┘
                                     │
      ┌──────────────────────────────▼──────────────────────────────┐
      │ EMBEDDING: id → vetor de 768, SEM contexto ainda              │
      │ + posição (onde está na frase) + segmento (frase A ou B)      │
      └──────────────────────────────┬──────────────────────────────┘
                                     │
      ╔══════════════════════════════▼══════════════════════════════╗
      ║ CAMADA 1  · atenção (12 cabeças) + rede feed-forward          ║
      ║ CAMADA 2  · idem                          cada camada REESCREVE║
      ║   ...                                     o vetor de cada token║
      ║ CAMADA 12 · idem                          com mais contexto    ║
      ╚══════════════════════════════╤══════════════════════════════╝
                                     │
                     SAÍDA: 768 números POR TOKEN, agora contextuais
                                     │
              ┌──────────────────────┼──────────────────────┐
              ▼                      ▼                      ▼
        vetor do [CLS]        vetor de cada token      média dos tokens
              │                      │                      │
       classificar a frase      NER, QA (por token)   embedding de frase
```

Três consequências práticas dessa imagem:

1. **O tronco não muda quando você troca de tarefa.** Só a cabeça no fim. É por isso que
   afinar é barato.
2. **A informação flui de baixo para cima, enriquecendo.** As camadas de baixo capturam
   sintaxe e morfologia; as de cima, semântica e tarefa. Isso foi medido, não é intuição —
   ver [20-interpretabilidade-e-bertologia.md](20-interpretabilidade-e-bertologia.md).
3. **Cada camada olha para a sequência inteira.** É por isso que o custo cresce com o
   **quadrado** do número de tokens, e por isso que 512 é o limite do BERT original.

---

## 4 · Por que "bidirecional" é a palavra-chave

O ponto que separa BERT de tudo que veio antes.

```
Frase: "O advogado abriu o processo contra o [MASK]."

Modelo unidirecional (esquerda→direita, tipo GPT):
   vê: "O advogado abriu o processo contra o"
   → precisa adivinhar sem saber o que vem depois

Modelo bidirecional (BERT):
   vê: "O advogado abriu o processo contra o [____] porque houve fraude no balanço."
                                                     └──────── também vê isto ────────┘
   → "banco" fica muito mais provável que "vizinho"
```

**Por que não fazer todos os modelos bidirecionais, então?** Porque para *gerar* texto é
impossível: ao escrever a palavra seguinte, o futuro ainda não existe. A bidirecionalidade
é o que se ganha ao abrir mão de gerar.

**E por que não treinar um modelo bidirecional com a tarefa "adivinhe a próxima palavra"?**
Porque seria trivial: o modelo veria a resposta. Ela está do lado direito, que ele pode olhar.
Ele aprenderia a copiar, não a entender. Este é *o* problema que os autores do BERT tiveram
que resolver, e a solução — esconder palavras — é o assunto de
[14-pre-treino-mlm-nsp.md](14-pre-treino-mlm-nsp.md).

---

## 5 · Os cinco porquês da ideia central

Aplicando a regra do curso ao conceito mais importante: **por que mascarar palavras funciona?**

**1. Por que mascarar palavras ensina alguma coisa?**
Porque para acertar a palavra escondida é preciso usar todo o resto da frase. O modelo é
forçado a construir uma representação do contexto.

**2. Por que essa representação serve para outras tarefas, como classificar sentimento?**
Porque a informação necessária para prever palavras — quem faz o quê, com que polaridade, em
que relação — é praticamente a mesma informação necessária para as tarefas de compreensão.
A tarefa artificial é um *proxy* muito bom da compreensão.

**3. Por que isso não era feito antes de 2018, se a ideia é simples?**
Porque não havia arquitetura capaz de olhar a sequência inteira em paralelo com custo
tolerável. Redes recorrentes (LSTM) processam um token por vez e não paralelizam bem — treinar
em bilhões de palavras levaria tempo demais. O Transformer (2017) removeu esse gargalo, e o
BERT apareceu 12 meses depois. **A ideia esperava o hardware e a arquitetura.**

**4. Por que o Transformer paraleliza e a LSTM não?**
Porque a LSTM tem uma dependência sequencial embutida: o estado no passo *t* depende do estado
em *t−1*, então não dá para calcular os passos ao mesmo tempo. A atenção calcula todas as
relações entre todos os pares de tokens de uma vez, com multiplicações de matriz — a operação
que a GPU faz melhor que qualquer outra.

**5. Por que a GPU faz multiplicação de matriz tão bem?**
Porque foi projetada nos anos 1990 para rasterizar triângulos em jogos 3D, o que é
multiplicação de matriz em massa. É uma **contingência histórica**: a arquitetura de hardware
que viabilizou o deep learning existia porque o mercado de videogames a financiou por vinte
anos. Chegamos a uma parada legítima — uma decisão histórica documentada, não uma
necessidade lógica.

---

## 6 · Vocabulário de tarefas

Como os problemas do mundo real são nomeados no campo. Saber o nome é metade do caminho para
achar o modelo pronto.

| Nome no campo | O que é | Cabeça | Exemplo |
|---|---|---|---|
| *Sequence classification* | um rótulo por texto | `SequenceClassification` | sentimento, spam, triagem |
| *Token classification* | um rótulo por token | `TokenClassification` | NER, POS, anonimização |
| *Extractive QA* | achar o trecho da resposta | `QuestionAnswering` | busca em documento |
| *NLI / textual entailment* | a frase B decorre da A? | `SequenceClassification` (par) | verificação de fato, zero-shot |
| *STS* (*semantic textual similarity*) | quão parecidas são A e B | bi-encoder ou cross-encoder | deduplicação, busca |
| *Reranking* | ordenar candidatos por relevância | cross-encoder | segunda etapa de busca |
| *Retrieval* | achar documentos relevantes | bi-encoder | primeira etapa de busca, RAG |
| *Multi-label* | vários rótulos ao mesmo tempo | `SequenceClassification` + sigmoid | tags de artigo |

---

## 7 · Bi-encoder × cross-encoder (a distinção que mais confunde)

Duas formas de usar BERT para comparar dois textos. Escolher errado custa caro ou custa
qualidade.

```
BI-ENCODER (dois passes independentes)
  "quero cancelar"  → BERT → vetor A ─┐
                                       ├→ cosseno(A, B) = 0.87
  "encerrar plano"  → BERT → vetor B ─┘

  ✓ Vetores podem ser calculados UMA VEZ e guardados num índice
  ✓ Busca em 10 milhões de documentos em milissegundos
  ✗ Menos preciso: os dois textos nunca "se olham"

CROSS-ENCODER (um passe conjunto)
  "[CLS] quero cancelar [SEP] encerrar plano [SEP]" → BERT → nota 0.94

  ✓ Muito mais preciso: a atenção cruza os dois textos, palavra por palavra
  ✗ Impossível pré-calcular: precisa rodar o modelo para CADA par
  ✗ 10 milhões de documentos = 10 milhões de execuções
```

**A arquitetura padrão de busca em 2026 usa os dois:** bi-encoder para trazer 100 candidatos
de milhões (rápido), cross-encoder para reordenar esses 100 (preciso). Detalhes e código em
[16-embeddings-e-busca-semantica.md](16-embeddings-e-busca-semantica.md).

---

## 8 · Os números do BERT que vale memorizar

| | BERT-base | BERT-large |
|---|---|---|
| Camadas (blocos Transformer) | 12 | 24 |
| Dimensão do vetor (`hidden size`) | 768 | 1024 |
| Cabeças de atenção por camada | 12 | 16 |
| Dimensão da rede interna (FFN) | 3072 | 4096 |
| Parâmetros | 110 M | 340 M |
| Tokens máximos | 512 | 512 |
| Tamanho em disco (fp32) | ~440 MB | ~1,3 GB |
| Custo de pré-treino original (2018) | 4 dias em 4 Cloud TPUs | 4 dias em 16 Cloud TPUs |

Relações que não são coincidência:
- `768 = 12 cabeças × 64` — cada cabeça trabalha num subespaço de 64 dimensões.
- `3072 = 4 × 768` — a razão 4× da FFN é convenção herdada do Transformer original, mantida
  por quase todos os modelos desde então (e sem justificativa teórica forte; ver
  [60-teoria-avancada.md](60-teoria-avancada.md)).

---

## 9 · O que o BERT **não** faz

Lista curta e importante, porque cada item é uma expectativa frustrada comum:

- **Não gera texto.** Nem uma frase. Não é limitação de tamanho — é de arquitetura.
- **Não conversa.** Não tem noção de turno, instrução ou papel.
- **Não raciocina em passos.** Não existe "vamos pensar passo a passo" num encoder.
- **Não lê mais de 512 tokens** (o original; ModernBERT vai a 8.192). Documento longo precisa
  ser fatiado.
- **Não sabe o que não sabe.** Sempre devolve uma classe, com confiança alta, mesmo para
  entrada fora do domínio — demonstrado no
  [projeto-modelo](07-projeto-modelo/README.md#o-que-este-modelo-não-faz-bem-limitações-honestas).
- **Não aprende sozinho depois do treino.** Nada de "ele vai melhorando com o uso" — isso
  exige um novo treino, com dados novos.
- **Não conhece nada posterior ao seu corpus.** BERTimbau foi treinado em texto até ~2019.
  Nubank nem sequer é uma palavra no seu vocabulário.

---

## 10 · Mapa dos arquivos do Bloco B

Ordem sugerida de leitura e o que cada um responde:

| Arquivo | Responde |
|---|---|
| [11-historia.md](11-historia.md) | de onde isso veio e por quê |
| [12-tokenizacao-wordpiece.md](12-tokenizacao-wordpiece.md) | como texto vira número |
| [13-arquitetura-encoder.md](13-arquitetura-encoder.md) | como a atenção funciona, no detalhe |
| [14-pre-treino-mlm-nsp.md](14-pre-treino-mlm-nsp.md) | como ele aprendeu a língua |
| [15-fine-tuning.md](15-fine-tuning.md) | como você o adapta |
| [16-embeddings-e-busca-semantica.md](16-embeddings-e-busca-semantica.md) | como virou a base de RAG |
| [17-familia-bert.md](17-familia-bert.md) | RoBERTa, DistilBERT, DeBERTa, ModernBERT: qual usar |
| [18-avaliacao-e-benchmarks.md](18-avaliacao-e-benchmarks.md) | como saber se está bom |
| [19-producao-e-otimizacao.md](19-producao-e-otimizacao.md) | como colocar em pé e barato |
| [20-interpretabilidade-e-bertologia.md](20-interpretabilidade-e-bertologia.md) | o que ele realmente aprendeu |
| [60-teoria-avancada.md](60-teoria-avancada.md) | a matemática e os limites |
| [65-estado-da-arte.md](65-estado-da-arte.md) | onde o campo está em 2026 |

---

## Autoteste

1. Qual é a diferença entre embedding estático e contextual? Dê um exemplo em que ela importa.
2. Quantos parâmetros tem BERT-base, e qual fração deles pertence à cabeça de classificação?
3. Por que um modelo bidirecional não pode gerar texto?
4. Por que treinar um modelo bidirecional com "preveja a próxima palavra" não funcionaria?
5. Explique a diferença entre pré-treino e afinamento, e por que um custa milhares de dólares e o outro, centavos.
6. Quando usar bi-encoder e quando usar cross-encoder? Por que a busca moderna usa os dois?
7. Por que `768 = 12 × 64` não é coincidência?
8. Cite três coisas que BERT não faz, e explique por que cada uma é impossível para a arquitetura.
9. Por que a ideia do BERT só apareceu em 2018, se ela é simples?

---

*Anterior: [07-projeto-modelo/](07-projeto-modelo/README.md) · Próximo: [11-historia.md](11-historia.md)*
