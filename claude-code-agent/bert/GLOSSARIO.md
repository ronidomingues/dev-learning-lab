# Glossário

`Todos os termos técnicos usados neste curso` · `Última atualização: 12/08/2026`

Termo em português, com o original em inglês entre parênteses quando o campo usa o inglês.
Ordem alfabética.

---

## A

**Ablação (*ablation*)** — remover uma parte do sistema para medir sua contribuição. "Ablação de entrada": apagar metade do texto e ver se a acurácia cai.

**Acurácia (*accuracy*)** — fração de previsões corretas sobre o total. Enganosa com classes desbalanceadas. Ver [18](18-avaliacao-e-benchmarks.md).

**AdamW** — otimizador padrão para Transformers. Variante do Adam que aplica o decaimento de peso diretamente aos pesos, em vez de somá-lo ao gradiente. Ver [60](60-teoria-avancada.md).

**Afinamento (*fine-tuning*)** — continuar o treino de um modelo pré-treinado numa tarefa específica, com dados rotulados. Minutos a horas. Ver [15](15-fine-tuning.md).

**Alinhamento de rótulos** — em NER, associar corretamente os rótulos das palavras aos subtokens gerados pelo tokenizador. Ver [06, ex. 9](06-exemplos.md).

**Anisotropia** — propriedade do espaço de embeddings do BERT em que os vetores ocupam um cone estreito, fazendo tudo parecer parecido com tudo. Ver [16](16-embeddings-e-busca-semantica.md).

**Atenção (*attention*)** — mecanismo em que cada token calcula pesos sobre todos os outros tokens e agrega informação deles. O coração do Transformer. Ver [13](13-arquitetura-encoder.md).

**Atenção esparsa** — variantes que limitam quais pares de tokens se atendem, para reduzir o custo quadrático (Longformer, BigBird).

**Atenção local/global** — alterna camadas com janela restrita e camadas com visão completa. Usada pelo ModernBERT.

**`attention_mask`** — vetor de 0 e 1 que diz ao modelo quais posições são tokens reais e quais são preenchimento. Esquecê-la degrada a qualidade em silêncio.

**Autoteste** — as perguntas ao final de cada arquivo deste curso.

**AUC-PR / AUC-ROC** — áreas sob as curvas precisão-recall e ROC. Medem a qualidade da separação independentemente do limiar. Ver [18](18-avaliacao-e-benchmarks.md).

**Auto-supervisionado (*self-supervised*)** — aprendizado em que o rótulo vem do próprio dado (ex.: a palavra escondida). Sem anotação humana. Ver [14](14-pre-treino-mlm-nsp.md).

## B

**Baseline burro** — modelo trivial (classe majoritária, TF-IDF + regressão logística) usado como piso de comparação. Obrigatório. Ver [18](18-avaliacao-e-benchmarks.md).

**BERT** — *Bidirectional Encoder Representations from Transformers*. Google, 2018.

**BERTimbau** — BERT pré-treinado em português do Brasil (NeuralMind/Unicamp, 2019). Licença MIT.

**BERTologia** — subcampo dedicado a investigar o que o BERT aprende internamente. Ver [20](20-interpretabilidade-e-bertologia.md).

**Bi-encoder** — arquitetura que codifica dois textos separadamente e compara os vetores. Rápido e indexável. Ver [10](10-fundamentos.md).

**Bidirecional** — que vê o contexto dos dois lados de cada token ao mesmo tempo. Característica definidora do BERT.

**BIO** — esquema de rotulação para NER: `B-` (início), `I-` (interior), `O` (fora de entidade).

**BM25** — algoritmo clássico de busca lexical por palavras. Complemento obrigatório da busca vetorial. Ver [16](16-embeddings-e-busca-semantica.md).

**BPE (*Byte Pair Encoding*)** — algoritmo de tokenização por subpalavra que funde os pares mais frequentes. Usado por GPT-2, RoBERTa, ModernBERT.

**BrWaC** — *Brazilian Web as Corpus*, corpus em que o BERTimbau foi treinado.

## C

**Cabeça (*head*)** — 1) camada final que adapta o modelo a uma tarefa; 2) uma das 12 atenções paralelas de cada camada. O contexto desambigua.

**Calibração** — grau em que a confiança do modelo corresponde à sua taxa de acerto. Redes modernas são sistematicamente superconfiantes. Ver [18](18-avaliacao-e-benchmarks.md).

**`[CLS]`** — token especial na primeira posição; seu vetor de saída é usado como resumo da sequência em classificação.

**Colab** — Google Colaboratory. Notebooks com GPU gratuita no navegador.

**Contextual (embedding)** — vetor calculado em função da frase inteira, portanto diferente para a mesma palavra em contextos diferentes. Oposto de estático.

**Corpus** — conjunto de textos usado para treino. Plural: *corpora*.

**Cross-encoder** — arquitetura que processa dois textos juntos numa única passada. Preciso e caro. Ver [10](10-fundamentos.md).

## D

**DeBERTa** — variante da Microsoft com atenção desemaranhada (conteúdo e posição separados).

**Deriva (*drift*)** — mudança gradual na distribuição dos dados de entrada que degrada o modelo silenciosamente. Ver [19](19-producao-e-otimizacao.md).

**Destilação (*knowledge distillation*)** — treinar um modelo pequeno (aluno) para imitar as distribuições de saída de um grande (professor). Origem do DistilBERT.

**DistilBERT** — BERT destilado: 6 camadas, ~40% menor, ~60% mais rápido, ~97% da qualidade.

**Dropout** — regularização que desliga neurônios ao acaso durante o treino. Precisa ser desligado na inferência com `model.eval()`.

## E

**ELECTRA** — variante cujo objetivo é detectar tokens substituídos, e não adivinhar máscaras. Muito mais eficiente por FLOP.

**ELMo** — modelo de 2018 com embeddings contextuais via LSTM bidirecional. Antecessor do BERT (e origem da piada de nomes da Vila Sésamo).

**Embedding** — representação vetorial de um token, frase ou documento.

**Encoder** — metade do Transformer que lê e representa. É o BERT.

**Entropia cruzada (*cross-entropy*)** — função de perda padrão para classificação.

**Época (*epoch*)** — uma passada completa pelos dados de treino.

**Esquecimento catastrófico (*catastrophic forgetting*)** — perda do conhecimento pré-treinado por afinamento agressivo demais.

**Estático (embedding)** — um vetor fixo por palavra, independente de contexto (word2vec, GloVe).

**Estratificação** — dividir os dados mantendo a proporção das classes em cada parte.

## F

**F1** — média harmônica entre precisão e recall.

**F1 macro** — média das F1 calculadas por classe; dá o mesmo peso a todas. Padrão para multiclasse desbalanceada.

**F1 micro** — agrega os acertos antes de calcular; equivale à acurácia em classificação de rótulo único.

**FAISS** — biblioteca da Meta para busca vetorial eficiente.

**Feed-forward (FFN)** — rede densa de duas camadas dentro de cada bloco Transformer. Contém ~2/3 dos parâmetros do modelo.

**Fertilidade (do tokenizador)** — média de tokens por palavra. Quanto menor, melhor o tokenizador lida com o seu vocabulário. Ver [12](12-tokenizacao-wordpiece.md).

**Flash Attention** — implementação da atenção que evita materializar a matriz `n×n` na memória. Ganho grande de constante, não de complexidade.

## G

**GELU** — função de ativação usada no Transformer; versão suave da ReLU.

**GLUE** — conjunto de 9 tarefas de compreensão em inglês. Referência histórica, hoje saturado.

**Gradiente** — vetor de derivadas usado para atualizar os pesos no treino.

**Gradient accumulation** — acumular gradientes de vários lotes pequenos antes de atualizar, simulando um lote grande.

**Gradient checkpointing** — recomputar ativações em vez de guardá-las; troca velocidade por memória.

## H

**Hugging Face** — empresa e plataforma (o *Hub*) onde modelos e datasets são publicados; autora da biblioteca `transformers`.

**Hiperparâmetro** — valor escolhido antes do treino (taxa de aprendizado, épocas, lote), em oposição aos parâmetros aprendidos.

## I

**Inferência** — usar o modelo treinado para obter previsões. Oposto de treino.

**Isotropia** — distribuição uniforme dos vetores no espaço. O oposto de anisotropia.

## L

**LayerNorm** — normalização aplicada dentro de cada token, independente do lote. Padrão em Transformers.

**Limiar (*threshold*)** — corte de probabilidade que transforma a saída do modelo em decisão. Decisão de negócio, não de engenharia.

**Logit** — saída crua da última camada, antes do `softmax`.

**LoRA** — afinamento eficiente por adaptadores de baixo posto. Essencial em LLMs, raramente necessário em BERT-base.

**Lote (*batch*)** — conjunto de exemplos processados juntos.

**LSTM** — arquitetura recorrente anterior ao Transformer. Sequencial, difícil de paralelizar.

## M

**`[MASK]`** — token especial que representa a palavra escondida no pré-treino.

**Máscara dinâmica** — sortear as posições mascaradas a cada época (RoBERTa), em vez de uma vez só (BERT original).

**Matriz de confusão** — tabela verdadeiro × previsto. Obrigatória em qualquer avaliação séria.

**Mean pooling** — média dos vetores de todos os tokens (ignorando padding) para obter um vetor de frase.

**MLM (*Masked Language Modeling*)** — objetivo de pré-treino do BERT: prever tokens escondidos.

**ModernBERT** — sucessor do BERT (dez/2024): RoPE, atenção local/global, Flash Attention, 8.192 tokens.

**moBERTo** — ModernBERT com pré-treino continuado em 60 bilhões de tokens em português (jun/2026).

**MTEB** — *Massive Text Embedding Benchmark*, referência para modelos de embedding.

**Multi-cabeça (*multi-head*)** — várias atenções em paralelo, cada uma num subespaço da representação.

**Multirrótulo (*multi-label*)** — um exemplo pode ter várias classes ao mesmo tempo; usa `sigmoid`, não `softmax`.

## N

**NER (*Named Entity Recognition*)** — reconhecimento de entidades nomeadas: pessoas, organizações, lugares.

**NLI (*Natural Language Inference*)** — dada uma premissa e uma hipótese, dizer se há implicação, contradição ou neutralidade. Base do zero-shot.

**NSP (*Next Sentence Prediction*)** — segundo objetivo de pré-treino do BERT, descartado depois do RoBERTa.

## O

**ONNX** — formato intermediário para modelos; permite execução otimizada fora do PyTorch.

**Overfitting (sobreajuste)** — o modelo decora o treino e generaliza mal.

## P

**`[PAD]`** — token de preenchimento para igualar comprimentos dentro de um lote.

**Parâmetro** — número aprendido durante o treino. BERT-base tem ~110 milhões.

**pgvector** — extensão do PostgreSQL para busca vetorial.

**Pooling** — reduzir uma matriz de vetores por token a um único vetor de frase.

**Pré-treino (*pre-training*)** — fase cara e única em que o modelo aprende a língua em texto cru.

**Precisão (*precision*)** — dos casos que o modelo apontou como positivos, quantos eram.

**Probing (sondagem)** — treinar um classificador simples sobre representações congeladas para descobrir que informação elas contêm.

**Pseudo-perplexidade** — medida de "naturalidade" de uma frase para um MLM, calculada mascarando um token por vez.

## Q

**QA extrativo** — encontrar no texto o trecho que responde a uma pergunta. O modelo aponta, não escreve.

**Quantização** — reduzir a precisão numérica dos pesos (fp32 → int8) para economizar memória e ganhar velocidade.

**Query, Key, Value (Q, K, V)** — as três projeções de cada token na atenção: consulta, chave e valor.

## R

**RAG (*Retrieval-Augmented Generation*)** — arquitetura em que documentos recuperados alimentam um LLM. O encoder faz a recuperação.

**Recall (revocação)** — de tudo que era positivo, quanto o modelo encontrou.

**Reranking** — reordenar candidatos de busca com um modelo mais preciso (cross-encoder).

**Residual (conexão)** — somar a entrada de volta à saída de uma sub-camada. Torna redes profundas treináveis.

**RoBERTa** — BERT retreinado com mais dados, mais tempo e sem NSP. Melhor em tudo.

**RoPE (*Rotary Position Embedding*)** — codificação posicional rotacional; extrapola para além do comprimento visto no treino.

**RRF (*Reciprocal Rank Fusion*)** — forma simples e robusta de combinar dois rankings.

## S

**Semente (*seed*)** — valor que fixa a aleatoriedade e torna o treino reproduzível.

**Sentence-BERT** — BERT treinado em arquitetura siamesa para produzir embeddings de frase comparáveis por cosseno.

**`[SEP]`** — token especial que separa segmentos e marca o fim da sequência.

**Sigmoid** — função que mapeia cada logit para (0,1) independentemente. Usada em multirrótulo.

**Similaridade cosseno** — cosseno do ângulo entre dois vetores; medida padrão de proximidade semântica.

**Softmax** — converte logits em uma distribuição de probabilidade que soma 1.

**SOP (*Sentence Order Prediction*)** — substituto do NSP no ALBERT: dizer se duas frases consecutivas estão na ordem certa.

**Subtoken** — pedaço de palavra produzido pelo tokenizador (`##ele`, `##ção`).

## T

**Taxa de aprendizado (*learning rate*)** — tamanho do passo de atualização dos pesos. O hiperparâmetro mais importante.

**TF-IDF** — representação clássica por frequência de termos. Baseline obrigatório.

**Token** — a menor unidade que o modelo enxerga.

**Tokenizador** — programa que converte texto em tokens e ids.

**`token_type_ids`** — indica a qual segmento (frase A ou B) cada token pertence.

**Transfer learning (aprendizado por transferência)** — reaproveitar conhecimento de um modelo pré-treinado em outra tarefa.

**Transformer** — arquitetura de 2017 baseada inteiramente em atenção.

**Truncation (truncamento)** — cortar o texto que passa do comprimento máximo.

## U

**`[UNK]`** — token desconhecido. Raro em WordPiece, impossível em BPE de bytes.

**Unpadding** — remover os tokens de preenchimento antes do cálculo, em vez de computá-los à toa.

## V

**Validação (conjunto de)** — parte dos dados usada para escolher checkpoint e hiperparâmetros. Não é o teste.

**Vazamento de dados (*data leakage*)** — informação do teste que chega ao treino, inflando as métricas.

**Viés (*bias*)** — 1) parâmetro aditivo de uma camada linear; 2) preconceito social aprendido do corpus. O contexto desambigua; este curso trata do segundo em [20](20-interpretabilidade-e-bertologia.md).

**Vocabulário** — a lista fechada de tokens que o modelo conhece.

## W

**Warmup** — aumentar a taxa de aprendizado gradualmente no início do treino. Necessário no BERT por causa do post-LN.

**Weight decay** — regularização que empurra os pesos para zero.

**WordPiece** — algoritmo de tokenização por subpalavra usado pelo BERT; funde pares por informação mútua.

**word2vec** — modelo de 2013 que popularizou embeddings estáticos.

## X

**XLM-RoBERTa (XLM-R)** — RoBERTa multilíngue treinado em 100 línguas.

## Z

**Zero-shot** — classificar em categorias que o modelo nunca viu no treino, usando um modelo de NLI.

---

*Volta para o [00-MAPA.md](00-MAPA.md)*
