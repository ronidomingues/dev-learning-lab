# 11 · História — de onde o BERT veio e que problema ele resolveu

`Nível: iniciante → intermediário` · `Última atualização: 12/08/2026`

História técnica não é enfeite. Quase toda decisão estranha do BERT — 512 tokens, 15% de
máscara, vocabulário de 30 mil, a tarefa NSP que depois se mostrou inútil — só faz sentido
sabendo contra o que ele estava competindo em 2018.

---

## Linha do tempo

```
1948  Shannon: entropia da língua inglesa. Nasce a ideia de modelo de linguagem estatístico.
1966  ELIZA. Casamento de padrões; nada de aprendizado.
1980s IBM: modelos n-grama para reconhecimento de fala. "Contar palavras" domina 25 anos.
1997  LSTM (Hochreiter & Schmidhuber). Redes que "lembram" — mas quase ninguém liga ainda.
2003  Bengio et al.: primeiro modelo de linguagem neural com embeddings.
2013  word2vec (Mikolov, Google). Embeddings viram commodity. "rei − homem + mulher ≈ rainha"
2014  GloVe (Stanford). Seq2seq com LSTM. Atenção aparece em tradução (Bahdanau).
2015  Atenção vira peça central da tradução automática neural.
2017  ►► "Attention Is All You Need" (Vaswani et al., Google). O TRANSFORMER.
2018  fev · ELMo (AI2): embeddings contextuais com LSTM bidirecional. Ganha tudo.
      jun · GPT-1 (OpenAI): Transformer decoder + pré-treino + fine-tuning.
      out · ►► BERT (Devlin et al., Google). Quebra 11 benchmarks de uma vez.
2019  fev · GPT-2. jul · RoBERTa (Meta): "o BERT foi mal treinado". set · ALBERT, DistilBERT.
      out · Google põe BERT na busca. dez · BERTimbau (NeuralMind/Unicamp) para português.
2020  ELECTRA, DeBERTa, T5, Sentence-BERT amadurece. GPT-3 (175 B): o foco começa a migrar.
2021  Encoders viram infraestrutura silenciosa. A imprensa só fala de modelos generativos.
2022  nov · ChatGPT. O campo inteiro é sugado para decoders.
2023  RAG explode — e recoloca encoders no centro, como o motor de recuperação.
2024  dez · ►► ModernBERT (Answer.AI + LightOn): o primeiro sucessor real do BERT em 6 anos.
2025  fev · NeoBERT. set · mmBERT (multilíngue, 1.800+ línguas). Renascimento dos encoders.
2026  Encoders e decoders convivem por divisão de trabalho, não por competição.
```

---

## Ato 1 · O mundo antes: cada tarefa começava do zero

Até 2017, um projeto de PLN era assim:

1. Coletar dados **da sua tarefa**.
2. Pagar humanos para rotular 20, 50, 100 mil exemplos.
3. Projetar *features* à mão (n-gramas, listas de palavras, regras morfológicas).
4. Treinar um modelo do zero, só com esses dados.
5. Conseguir 80% de acurácia e comemorar.

Cada tarefa nova recomeçava tudo. Um classificador de sentimento não ajudava em nada um
sistema de NER. **O conhecimento não se transferia.**

O gargalo era claro e caro: **anotação humana**. Existiam bilhões de palavras de texto grátis
na internet, e nenhuma forma boa de aproveitá-las.

### A primeira brecha: word2vec (2013)

Mikolov e colegas, no Google, mostraram que dava para aprender vetores de palavras a partir de
texto cru, com uma tarefa boba: prever as palavras vizinhas. O resultado ficou famoso pela
aritmética:

```
vetor("rei") − vetor("homem") + vetor("mulher") ≈ vetor("rainha")
```

Isso foi um choque em 2013: significado capturado por álgebra, sem supervisão humana.
Word2vec virou peça padrão em todo sistema de PLN por cinco anos.

**Mas tinha um teto duro:** um vetor por palavra, fixo. "banco" da praça e "banco" da agência
compartilhavam o mesmo vetor, uma média confusa dos dois sentidos. E a ordem das palavras não
entrava na conta.

---

## Ato 2 · O Transformer (2017) — a peça que faltava

O artigo "Attention Is All You Need" foi escrito para resolver um problema específico e
mundano: **tradução automática estava lenta demais para treinar**.

Os modelos da época (LSTM com atenção) processavam texto palavra por palavra, em sequência. A
palavra 500 só podia ser calculada depois da 499. Isso torra uma GPU, que tem milhares de
núcleos esperando trabalho paralelo.

A proposta foi radical: **jogar fora a recorrência inteira**. Ficar só com a atenção, que
compara todos os tokens com todos os tokens de uma vez, em uma multiplicação de matrizes.

O ganho não foi só de qualidade — foi de **velocidade de treino**, o que permitiu, pela
primeira vez, treinar em corpora enormes num prazo razoável. E isso destravou tudo o que veio
depois.

O Transformer original tinha duas metades:

```
    ENCODER  (lê o alemão)  ────►  DECODER  (escreve o inglês)
    bidirecional                   autorregressivo
```

Em 2018, o campo percebeu que as metades funcionavam sozinhas — e se dividiu:

- **OpenAI ficou com o decoder** → GPT → ChatGPT.
- **Google ficou com o encoder** → BERT.

Duas equipes, o mesmo artigo de origem, dois caminhos que só voltaram a se encontrar em 2023.

---

## Ato 3 · ELMo e GPT-1: a corrida de 1918... digo, 2018

**Fevereiro de 2018 — ELMo** (*Embeddings from Language Models*, Allen Institute). A primeira
resposta boa ao problema do "banco": embeddings **contextuais**, produzidos por duas LSTMs, uma
lendo da esquerda e outra da direita, cujas saídas eram **concatenadas**.

Funcionou — melhorou o estado da arte em seis tarefas. Mas era uma bidirecionalidade
"grudada", não genuína: cada direção era treinada separadamente, sem que uma visse a outra
durante a leitura. Uma palavra nunca era processada com o contexto completo dos dois lados
ao mesmo tempo.

**Junho de 2018 — GPT-1** (OpenAI). Transformer decoder, pré-treinado para prever a próxima
palavra, depois afinado por tarefa. Estabeleceu a receita *pré-treinar → afinar* que domina
até hoje. Mas era unidirecional: cada token só via os anteriores.

Os dois deixaram o mesmo prêmio na mesa: **um Transformer genuinamente bidirecional**.
O obstáculo era conceitual, não de engenharia — como treinar um modelo que vê os dois lados
sem que a tarefa vire trapaça?

---

## Ato 4 · Outubro de 2018: BERT

Devlin, Chang, Lee e Toutanova (Google AI Language) publicam
*"BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding"*.

A ideia que destravou tudo, emprestada de um teste de proficiência linguística dos anos 1950
chamado **Cloze test**: se você não pode pedir "preveja a próxima palavra" (o modelo veria a
resposta à direita), então **esconda 15% das palavras e peça para adivinhá-las**. Agora o
modelo pode olhar os dois lados livremente, porque a resposta não está em lado nenhum.

Os números do lançamento explicam o abalo:

| Benchmark | Melhor anterior | BERT-large | Salto |
|---|---|---|---|
| GLUE (média) | 75,1 | **80,5** | +5,4 pontos |
| SQuAD v1.1 (F1) | 91,6 | **93,2** | acima do humano (91,2) |
| SQuAD v2.0 (F1) | 78,0 | **83,1** | +5,1 |
| MultiNLI | 82,1 | **86,7** | +4,6 |

Em PLN, 5 pontos de GLUE de uma vez é um terremoto — a norma eram ganhos de 0,5 a 1 ponto por
artigo. E o mais importante: **o Google publicou os pesos**, de graça, sob licença Apache 2.0.
Em semanas, todo mundo tinha estado da arte em tarefa própria com algumas horas de GPU.

Foi a "virada do ImageNet" do processamento de linguagem: o momento em que *transfer learning*
deixou de ser promessa e virou o modo padrão de trabalhar.

---

## Ato 5 · A explosão de variantes (2019–2020)

O BERT foi treinado uma vez, com escolhas tomadas sob prazo. O campo passou dois anos
descobrindo quais delas eram boas e quais eram acidente.

| Modelo | Ano | O que mudou | Lição |
|---|---|---|---|
| **RoBERTa** (Meta) | 2019 | mais dados, mais tempo, lotes maiores, **sem NSP**, máscara dinâmica | o BERT estava **subtreinado**; a tarefa NSP atrapalhava |
| **ALBERT** (Google) | 2019 | compartilha parâmetros entre camadas, fatora embeddings | dá para reduzir muito o tamanho com pouca perda |
| **DistilBERT** (HF) | 2019 | destilação: aluno de 6 camadas imita o professor de 12 | 40% menor, 60% mais rápido, ~97% da qualidade |
| **ELECTRA** (Google) | 2020 | em vez de adivinhar máscara, detectar token trocado | aprende com **todos** os tokens, não só 15% → muito mais eficiente |
| **DeBERTa** (Microsoft) | 2020 | atenção desemaranhada (conteúdo × posição separados) | melhor posicional; foi SOTA em GLUE por anos |
| **Sentence-BERT** | 2019 | treino siamês para similaridade de frases | o BERT cru **não** serve para cosseno |
| **XLM-R** (Meta) | 2019 | 100 línguas, 2,5 TB de CommonCrawl | um modelo multilíngue bate os monolíngues fracos |
| **BERTimbau** (Unicamp) | 2019 | BERT treinado em BrWaC (português brasileiro) | modelo da língua ganha do multilíngue genérico em PT |

O RoBERTa merece destaque: seu artigo é essencialmente um **estudo de replicação** que
mostrou que o BERT original tinha sido mal treinado, e que as melhorias arquiteturais que o
campo vinha publicando eram, em boa parte, ruído em cima de um baseline mal ajustado. É um
dos artigos mais honestos e influentes da década — e a lição vale para qualquer área:
**antes de inventar arquitetura nova, verifique se a antiga foi bem treinada.**

---

## Ato 6 · O eclipse (2020–2023) e o renascimento (2024–2026)

Com GPT-3 (2020) e ChatGPT (2022), a atenção do mundo — e o dinheiro — migrou inteiramente
para modelos generativos. Encoders ficaram "resolvidos" e sem glamour. Entre 2020 e 2024,
praticamente **nenhum encoder novo relevante** foi lançado. O BERT-base de 2018 continuou
sendo o padrão de fato por seis anos, o que é uma eternidade neste campo.

Enquanto isso, silenciosamente, encoders passaram a rodar em escala industrial: busca do
Google, moderação de conteúdo, classificação de e-mail, extração de documentos.

O que trouxe encoders de volta ao debate técnico foi o **RAG**. Para um LLM responder com
base nos seus documentos, alguém precisa **encontrar** os documentos certos — e quem faz
isso, em quase toda implementação, é um encoder. De repente a qualidade da recuperação virou
o gargalo de sistemas caríssimos de LLM, e a comunidade percebeu que estava usando uma peça
de 2018 no meio de uma pilha de 2024.

**Dezembro de 2024 — ModernBERT** (Answer.AI + LightOn). O primeiro sucessor sério: seis anos
de avanços de LLM aplicados de volta ao encoder — RoPE em vez de posições aprendidas,
atenção local/global alternada, sem viés nas camadas lineares, Flash Attention, treino em
2 trilhões de tokens (contra 3,3 bilhões de palavras do BERT), 8.192 tokens de contexto.
Mais rápido **e** melhor: um ganho de Pareto, coisa rara.

**2025 — NeoBERT** (250 M de parâmetros, 2,1 trilhões de tokens, contexto de 4.096) e
**mmBERT** (multilíngue, 1.800+ línguas, 3 trilhões de tokens, tokenizador do Gemma 2).
O campo dos encoders voltou a se mexer depois de meia década parada.

Detalhes e recomendações atuais: [65-estado-da-arte.md](65-estado-da-arte.md).

---

## Por que o BERT é como é — cinco decisões e suas razões

Aplicando a regra dos cinco porquês às escolhas que mais confundem:

### Por que 512 tokens, e não 1.000 ou 2.048?

O custo da atenção cresce com o **quadrado** do comprimento. Em 2018, com o hardware
disponível, 512 era o que cabia num orçamento razoável de treino. **Não há nada de especial no
número** — é uma potência de 2 (conveniência de hardware) na faixa que o orçamento permitia.
ModernBERT, com Flash Attention e atenção local, chega a 8.192 pelo mesmo custo relativo.
**Parada legítima: trade-off econômico da época.**

### Por que 15% de máscara?

O artigo diz, com franqueza incomum, que é um valor escolhido empiricamente. A intuição:
mascarar pouco torna o treino ineficiente (poucos sinais por frase); mascarar muito destrói
tanto contexto que a tarefa fica impossível. Trabalhos posteriores (Wettig et al., 2023)
mostraram que **40% funciona melhor em modelos grandes** — ou seja, os 15% eram um chute
razoável, não um ótimo. **Parada legítima: convenção empírica, e hoje sabemos que era
subótima.**

### Por que existia a tarefa NSP (*Next Sentence Prediction*)?

Porque QA e inferência lidam com **pares** de frases, e os autores quiseram um objetivo que
ensinasse relação entre frases. Fazia sentido no papel. Na prática, RoBERTa mostrou em 2019
que remover NSP **melhora** o modelo: a tarefa era fácil demais (detectar mudança de tópico
resolve a maioria dos casos) e roubava capacidade do MLM. É um dos raros casos em que uma
peça central de um artigo seminal foi publicamente descartada em 12 meses.
**Parada legítima: hipótese razoável que os dados refutaram.**

### Por que vocabulário de exatamente 30.522 entradas?

30.000 é a ordem de grandeza que equilibra: vocabulário pequeno demais quebra tudo em pedaços
minúsculos (sequências longas, caras); grande demais infla a matriz de embeddings (30.522 ×
768 ≈ 23 M de parâmetros só aí, ~21% do modelo). O número exato, 30.522, é o resultado do
algoritmo WordPiece rodando até o alvo, mais os tokens especiais. **Parada legítima:
trade-off, com o valor exato sendo arbitrário.**

### Por que "BERT" e não um nome sério?

Porque o modelo que ele destronou se chamava **ELMo**, e a piada da Vila Sésamo pegou. Depois
vieram ERNIE, Grover, KERMIT, Big Bird, RoBERTa. Isso é sintoma de uma comunidade pequena e
autoconsciente, em que uma brincadeira interna virou convenção por cinco anos.
**Parada legítima: convenção arbitrária, e assumidamente arbitrária.**

---

## O que a história ensina para hoje

Três lições que se aplicam ao seu trabalho, não só à cultura geral:

1. **A ideia nova quase nunca é a peça nova.** O Transformer é de 2017; o Cloze test é de
   1953. O BERT foi a combinação certa de peças existentes, com escala. A maior parte do
   progresso é recombinação, não invenção.
2. **Baseline mal treinado gera literatura falsa.** O RoBERTa mostrou que dois anos de
   "melhorias arquiteturais" sobre o BERT eram, em boa medida, correções de um treino
   malfeito. Antes de acreditar num ganho, pergunte se o baseline foi bem ajustado.
3. **Tecnologia "resolvida" pode ficar parada seis anos e depois avançar de repente.** Entre
   2018 e 2024, ninguém melhorou o encoder — não porque fosse impossível, mas porque a
   atenção do campo estava em outro lugar. Quando o RAG criou pressão econômica, o ModernBERT
   apareceu em meses. **Onde a atenção vai, o progresso segue.**

---

## Autoteste

1. Qual era o gargalo do PLN antes de 2018, e por que texto cru não resolvia?
2. O que word2vec conseguiu, e qual era seu teto?
3. Por que o Transformer foi criado — qual problema prático o motivou?
4. Qual a diferença entre a bidirecionalidade do ELMo e a do BERT?
5. De onde veio a ideia de mascarar palavras, e por que ela destravou o problema?
6. O que o RoBERTa provou sobre o BERT original, e por que esse artigo é importante além do modelo?
7. Por que o limite é 512 tokens? A resposta é técnica, econômica ou arbitrária?
8. O que aconteceu com a tarefa NSP, e o que isso ensina sobre ler papers seminais?
9. Por que encoders ficaram seis anos sem evolução, e o que os trouxe de volta em 2024?

---

## Fontes

- Vaswani et al. (2017). *Attention Is All You Need*. [arXiv:1706.03762](https://arxiv.org/abs/1706.03762)
- Devlin, Chang, Lee & Toutanova (2019). *BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding*. NAACL-HLT 2019, pp. 4171–4186. [aclanthology.org/N19-1423](https://aclanthology.org/N19-1423/)
- Peters et al. (2018). *Deep Contextualized Word Representations* (ELMo). [arXiv:1802.05365](https://arxiv.org/abs/1802.05365)
- Liu et al. (2019). *RoBERTa: A Robustly Optimized BERT Pretraining Approach*. [arXiv:1907.11692](https://arxiv.org/abs/1907.11692)
- Mikolov et al. (2013). *Efficient Estimation of Word Representations in Vector Space*. [arXiv:1301.3781](https://arxiv.org/abs/1301.3781)
- Souza, Nogueira & Lotufo (2020). *BERTimbau: Pretrained BERT Models for Brazilian Portuguese*. [github.com/neuralmind-ai/portuguese-bert](https://github.com/neuralmind-ai/portuguese-bert)
- Warner et al. (2024). *Smarter, Better, Faster, Longer* (ModernBERT). [answer.ai/posts/2024-12-19-modernbert.html](https://www.answer.ai/posts/2024-12-19-modernbert.html)
- Le Breton et al. (2025). *NeoBERT: A Next-Generation BERT*. [arXiv:2502.19587](https://arxiv.org/abs/2502.19587)

*Consulta feita em 12/08/2026.*

---

*Anterior: [10-fundamentos.md](10-fundamentos.md) · Próximo: [12-tokenizacao-wordpiece.md](12-tokenizacao-wordpiece.md)*
