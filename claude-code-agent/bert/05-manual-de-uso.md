# 05 · Manual de uso — referência consultável

`Nível: intermediário` · `Base: transformers 5.15.0 · torch 2.13.0` · `Última atualização: 12/08/2026`

Organizado **por tarefa**, não em ordem alfabética. Use o índice; ninguém lê manual de cabo a rabo.

- [Escolher a classe certa (`AutoModelFor...`)](#1-escolher-a-classe-certa)
- [Tokenizador: todas as opções que importam](#2-tokenizador)
- [Carregar e salvar modelos](#3-carregar-e-salvar)
- [Pipelines](#4-pipelines)
- [Inferência manual](#5-inferência-manual)
- [Treinar com o `Trainer`](#6-treinar-com-o-trainer)
- [`TrainingArguments` — os parâmetros que você vai mexer](#7-trainingarguments)
- [CLI `hf` e cache](#8-cli-hf-e-cache)
- [Desempenho e memória](#9-desempenho-e-memória)
- [Tabela de modelos: qual usar](#10-qual-modelo-usar)
- [Obsoleto — o que não usar mais](#11-obsoleto)

---

## 1 · Escolher a classe certa

A regra de ouro da biblioteca: **a classe define a "cabeça"** colocada em cima do tronco BERT.
Escolher a errada é o erro estrutural mais comum.

| Classe | O que a cabeça faz | Saída | Use para |
|---|---|---|---|
| `AutoModel` | nenhuma cabeça | `(lote, tokens, 768)` | embeddings, extrair representações |
| `AutoModelForSequenceClassification` | 1 vetor por **texto** | `(lote, n_classes)` | sentimento, triagem, spam, NLI |
| `AutoModelForTokenClassification` | 1 vetor por **token** | `(lote, tokens, n_classes)` | NER, part-of-speech, anonimização |
| `AutoModelForMaskedLM` | prevê o token escondido | `(lote, tokens, vocab)` | preencher lacuna, pré-treino contínuo |
| `AutoModelForQuestionAnswering` | 2 vetores por token (início/fim) | 2× `(lote, tokens)` | QA extrativo |
| `AutoModelForMultipleChoice` | 1 nota por alternativa | `(lote, n_opções)` | escolher entre alternativas |
| `AutoModelForNextSentencePrediction` | binária de par | `(lote, 2)` | quase nada hoje (ver `14`) |

```python
from transformers import AutoModelForSequenceClassification

modelo = AutoModelForSequenceClassification.from_pretrained(
    "neuralmind/bert-base-portuguese-cased",
    num_labels=4,
    id2label={0: "FINANCEIRO", 1: "TECNICO", 2: "COMERCIAL", 3: "CANCELAMENTO"},
    label2id={"FINANCEIRO": 0, "TECNICO": 1, "COMERCIAL": 2, "CANCELAMENTO": 3},
)
```

> **Sempre preencha `id2label`/`label2id`.** Sem eles, o modelo salvo devolve `LABEL_0`,
> `LABEL_1`... e seis meses depois ninguém sabe qual é qual. Custa uma linha e evita um
> incidente.

**Regressão** (nota contínua em vez de classe): use `SequenceClassification` com
`num_labels=1` — a biblioteca troca a função de perda para MSE automaticamente.

---

## 2 · Tokenizador

### Chamada básica

```python
tok(texto)                                    # um texto
tok([t1, t2, t3])                             # lote
tok(pergunta, contexto)                       # par de segmentos
```

### Opções, por frequência de uso real

| Opção | Valores | O que faz | Quando usar |
|---|---|---|---|
| `truncation` | `True`, `"longest_first"`, `"only_second"` | corta o que passa do limite | **sempre** |
| `max_length` | inteiro | limite de tokens | **sempre** — 128 para frases, 512 no máximo do BERT |
| `padding` | `True`/`"longest"`, `"max_length"`, `False` | completa com `[PAD]` | `True` em lote; `False` + `DataCollator` no treino |
| `return_tensors` | `"pt"`, `"np"`, `None` | formato da saída | `"pt"` para alimentar o modelo |
| `return_offsets_mapping` | `True`/`False` | posição de cada token no texto original | NER, destacar trecho na tela |
| `add_special_tokens` | `True`/`False` | inserir `[CLS]`/`[SEP]` | quase sempre `True` |
| `return_token_type_ids` | `True`/`False` | ids de segmento | pares de frases |
| `stride` | inteiro | sobreposição ao dividir texto longo | QA em documento longo |

### O que volta

| Chave | Conteúdo |
|---|---|
| `input_ids` | os números do vocabulário |
| `attention_mask` | `1` = token real, `0` = preenchimento (o modelo ignora os `0`) |
| `token_type_ids` | `0` = primeiro segmento, `1` = segundo |
| `offset_mapping` | `(início, fim)` em caracteres — só com `return_offsets_mapping=True` |

### Métodos úteis

```python
tok.tokenize("texto")                    # → lista de tokens (strings)
tok.convert_ids_to_tokens(ids)           # ids → tokens
tok.convert_tokens_to_ids(tokens)        # tokens → ids
tok.decode(ids)                          # ids → texto (v5: unificado, aceita lote)
tok.decode(ids, skip_special_tokens=True)  # sem [CLS]/[SEP]/[PAD]
enc = tok("texto")                       # BatchEncoding
enc.word_ids()                           # token → índice da palavra original (v5: era .words())
enc.tokens()                             # tokens do resultado
```

### Tokens especiais e seus ids

```python
tok.cls_token, tok.cls_token_id          # '[CLS]', 101
tok.sep_token, tok.sep_token_id          # '[SEP]', 102
tok.pad_token, tok.pad_token_id          # '[PAD]', 0
tok.mask_token, tok.mask_token_id        # '[MASK]', 103
tok.unk_token                            # '[UNK]'
tok.vocab_size                           # 29794 no BERTimbau; 30522 no bert-base-uncased
```

> Os ids 101/102/0/103 valem para BERT/WordPiece. **RoBERTa, DeBERTa e ModernBERT usam outros
> tokens e outros ids** (`<s>`, `</s>`, `<mask>`). Nunca escreva `101` no código — use
> `tok.cls_token_id`.

### Adicionar vocabulário próprio

```python
tok.add_tokens(["ICMS", "SPED", "eSocial"])          # termos do seu domínio
modelo.resize_token_embeddings(len(tok))             # OBRIGATÓRIO depois de adicionar
```

Sem o `resize`, o próximo token novo vira um índice fora da tabela → `IndexError`.
Vale a pena? Só se o termo aparece muito e o WordPiece o está estraçalhando. Ver
[12-tokenizacao-wordpiece.md](12-tokenizacao-wordpiece.md).

---

## 3 · Carregar e salvar

```python
from transformers import AutoModel, AutoTokenizer

# do Hub
m = AutoModel.from_pretrained("neuralmind/bert-base-portuguese-cased")

# de pasta local (ambiente sem internet)
m = AutoModel.from_pretrained("./meu-modelo")

# revisão fixa — recomendado em produção: o autor pode atualizar o modelo sem avisar
m = AutoModel.from_pretrained("bert-base-uncased", revision="86b5e0934494bd15c9632b12f734a8a67f723594")

# precisão e dispositivo
m = AutoModel.from_pretrained(M, dtype=torch.float16, device_map="auto")
```

| Parâmetro de `from_pretrained` | Para quê |
|---|---|
| `revision` | fixar um commit do Hub (reprodutibilidade e segurança) |
| `dtype` | `torch.float32`/`float16`/`bfloat16`/`"auto"` — **v5: era `torch_dtype`** |
| `device_map` | `"auto"`, `"cuda"`, `"cpu"` — onde alocar |
| `num_labels`, `id2label`, `label2id` | configurar a cabeça de classificação |
| `token` | token do Hub para modelos privados — **v5: era `use_auth_token`** |
| `cache_dir` | cache alternativo (ou use `HF_HOME`) |
| `attn_implementation` | `"eager"` (permite `output_attentions`), `"sdpa"`, `"flash_attention_2"` |
| `local_files_only=True` | proíbe acesso à rede |
| `trust_remote_code=True` | **executa código Python do repositório** — só para fonte confiável |

```python
# salvar
modelo.save_pretrained("./meu-modelo")
tok.save_pretrained("./meu-modelo")      # SEMPRE salve o tokenizador junto do modelo

# publicar no Hub
modelo.push_to_hub("usuario/meu-modelo")
tok.push_to_hub("usuario/meu-modelo")
```

> **Salvar o modelo sem o tokenizador** é a maneira mais eficiente de tornar seu trabalho
> inútil: os ids não significam nada sem o vocabulário que os gerou.

---

## 4 · Pipelines

Atalho para inferência. Ótimo para explorar e para tarefas simples; limitado quando você
precisa de controle fino.

```python
from transformers import pipeline

p = pipeline("text-classification", model="./modelo-treinado")
p("meu boleto não chegou")
# [{'label': 'FINANCEIRO', 'score': 0.966}]

p("texto", top_k=None)          # todas as classes com suas probabilidades
p(["t1", "t2"], batch_size=16)  # lote — muito mais rápido que um a um
p = pipeline(..., device=0)     # GPU 0; device=-1 força CPU
```

### Pipelines úteis para a família BERT em 2026

| Tarefa | Existe na v5? | Observação |
|---|---|---|
| `fill-mask` | sim | tarefa nativa do BERT |
| `text-classification` | sim | apelido: `sentiment-analysis` |
| `token-classification` | sim | apelido: `ner`; use `aggregation_strategy="simple"` |
| `feature-extraction` | sim | devolve os vetores crus |
| `zero-shot-classification` | sim | usa modelo de NLI; não precisa treinar |
| `question-answering` | **REMOVIDO na v5** | faça manualmente — ver [06-exemplos.md](06-exemplos.md) |
| `summarization`, `translation` | **REMOVIDOS na v5** | não eram tarefa de encoder mesmo |

```python
# NER com agrupamento: junta os pedaços "Pe","##tro","##bras" numa entidade só
ner = pipeline("token-classification", model="<modelo-ner>", aggregation_strategy="simple")
```

---

## 5 · Inferência manual

Quando o pipeline não basta (você quer as probabilidades, o vetor, ou controlar o lote):

```python
import torch

modelo.eval()                                    # 1. desliga dropout
entradas = tok(textos, padding=True, truncation=True, max_length=128, return_tensors="pt")
entradas = {k: v.to(modelo.device) for k, v in entradas.items()}   # 2. mesmo dispositivo

with torch.no_grad():                            # 3. sem grafo de gradiente
    logits = modelo(**entradas).logits

probs = torch.softmax(logits, dim=-1)            # 4. logits → probabilidades
classe = probs.argmax(dim=-1)
nomes = [modelo.config.id2label[int(i)] for i in classe]
```

Os quatro passos numerados são obrigatórios; pular qualquer um gera um bug clássico
(respostas instáveis, erro de dispositivo, memória estourada, ou "probabilidade" que não
soma 1).

**Logits × probabilidades:** `logits` são notas cruas, de −∞ a +∞. `softmax` as transforma em
probabilidades que somam 1. Para **multirrótulo** (um texto pode ter várias classes ao mesmo
tempo), use `torch.sigmoid` em vez de `softmax`, e limiar por classe.

---

## 6 · Treinar com o `Trainer`

```python
from transformers import Trainer, TrainingArguments, DataCollatorWithPadding

trainer = Trainer(
    model=modelo,
    args=TrainingArguments(...),
    train_dataset=ds_treino,
    eval_dataset=ds_val,
    processing_class=tok,                       # v5: era `tokenizer=`
    data_collator=DataCollatorWithPadding(tok),
    compute_metrics=calcular_metricas,
)

trainer.train()                                 # treina
trainer.evaluate()                              # avalia no eval_dataset
saida = trainer.predict(ds_teste)               # prevê: .predictions, .label_ids, .metrics
trainer.save_model("./modelo-final")
trainer.train(resume_from_checkpoint=True)      # retomar — v5: era `model_path=`
```

### Collators

| Collator | Para quê |
|---|---|
| `DataCollatorWithPadding` | classificação — preenche até o maior do lote |
| `DataCollatorForTokenClassification` | NER — preenche **também os rótulos**, com −100 |
| `DataCollatorForLanguageModeling(mlm=True, mlm_probability=0.15)` | pré-treino contínuo com MLM: mascara na hora |

> `-100` é o valor mágico do PyTorch para "ignore esta posição no cálculo da perda". Aparece
> em NER (subtokens) e em MLM (tokens não mascarados).

### Dataset: o que o `Trainer` espera

Um `datasets.Dataset` (ou `torch.utils.data.Dataset`) cujos itens tenham `input_ids`,
`attention_mask` e **`labels`** — no plural, exatamente esse nome. `label` no singular
funciona em alguns caminhos e falha em outros; use `labels`.

---

## 7 · TrainingArguments

Os que você realmente ajusta, na ordem em que importam:

| Parâmetro | Padrão | Faixa útil | Comentário |
|---|---|---|---|
| `learning_rate` | `5e-5` | `1e-5` a `5e-5` | **o mais importante**. Acima de `1e-4` o modelo "esquece" o pré-treino |
| `num_train_epochs` | `3.0` | 2 a 10 | 2–4 no paper; conjunto pequeno pede mais |
| `per_device_train_batch_size` | `8` | 8 a 32 | limitado pela VRAM |
| `gradient_accumulation_steps` | `1` | 1 a 16 | simula lote maior sem mais memória (`lote_efetivo = lote × acumulação × n_gpus`) |
| `warmup_steps` | `0` | `0.06`–`0.1` | float < 1 = **proporção**. **v5: `warmup_ratio` foi removido** |
| `weight_decay` | `0.0` | `0.01` | regularização padrão do BERT |
| `eval_strategy` | `"no"` | `"epoch"` | **v5: era `evaluation_strategy`** |
| `save_strategy` | `"steps"` | `"epoch"` | precisa casar com `eval_strategy` se usar `load_best_model_at_end` |
| `load_best_model_at_end` | `False` | `True` | recupera o melhor checkpoint em vez do último |
| `metric_for_best_model` | `None` | `"f1_macro"` | nome da chave devolvida por `compute_metrics` |
| `save_total_limit` | `None` | `1` a `3` | sem isto, o disco enche de checkpoints |
| `bf16` / `fp16` | `False` | `True` em GPU | ~2× mais rápido. `bf16` em Ampere+; `fp16` em GPUs antigas |
| `gradient_checkpointing` | `False` | `True` | troca ~30% de velocidade por muita memória economizada |
| `report_to` | tudo instalado | `"none"` | evita W&B pedir login no meio do treino |
| `seed` | `42` | — | reprodutibilidade |
| `logging_steps` | `500` | 10 a 100 | conjunto pequeno precisa de log frequente |

**Removidos na v5** (se estiverem no seu script antigo, ele quebra):
`warmup_ratio`, `overwrite_output_dir`, `logging_dir`, `tpu_num_cores`, `past_index`,
`jit_mode_eval`, `ray_scope`, `mp_parameters`, `no_cuda` (→ `use_cpu`),
`per_gpu_train_batch_size` (→ `per_device_train_batch_size`).

---

## 8 · CLI `hf` e cache

```bash
hf auth login                       # autenticar
hf auth whoami                      # quem sou eu
hf download <repo>                  # baixar para o cache
hf download <repo> --local-dir ./m  # baixar para uma pasta (ambiente offline)
hf upload <repo> ./pasta            # publicar
hf cache scan                       # o que ocupa espaço
hf cache delete                     # apagar revisões interativamente
hf repo create <nome>               # criar repositório
```

| Variável | Efeito |
|---|---|
| `HF_HOME` | raiz do cache e do token |
| `HF_TOKEN` | autenticação sem arquivo (CI, container) |
| `HF_HUB_OFFLINE=1` | proíbe rede; usa só o cache |
| `HF_ENDPOINT` | espelho do Hub |
| `TRANSFORMERS_VERBOSITY` | `error`, `warning`, `info`, `debug` |
| `TOKENIZERS_PARALLELISM` | `false` silencia o aviso de fork |

---

## 9 · Desempenho e memória

### Truques que quem usa há anos aplica sem pensar

| Situação | O que fazer | Ganho típico |
|---|---|---|
| Inferência em lote | `padding=True` só até o maior do lote + ordenar por comprimento | 2–4× |
| Sequências curtas | `max_length=128` em vez de 512 | ~4× (atenção é quadrática) |
| GPU moderna | `bf16=True` | ~2× e metade da memória |
| CPU em produção | exportar para ONNX + quantização int8 | 2–4× |
| Estourou a VRAM | `gradient_accumulation_steps` + `gradient_checkpointing` | cabe onde não cabia |
| Muitos textos curtos | agrupar por tamanho (`group_by_length=True`) | 20–40% no treino |
| Modelo grande demais | trocar por DistilBERT/MiniLM | 2–6× mais rápido, −1 a −3 pontos de F1 |

### Memória, na conta do guardanapo

```
Inferência:  ~ n_parâmetros × bytes_por_parâmetro  (BERT-base fp32 ≈ 440 MB)
Treino:      ~ 4 × isso  (pesos + gradientes + 2 estados do Adam) + ativações
             BERT-base fp32 ≈ 1,8 GB + ativações → ~6 GB de VRAM com lote 16 e seq 128
```

Ativações crescem com `lote × comprimento²`. Dobrar o comprimento quadruplica essa parte —
é por isso que 512 tokens custa tão mais caro que 128.

---

## 10 · Qual modelo usar

Recomendação de agosto de 2026. Justificativa completa em
[17-familia-bert.md](17-familia-bert.md) e [65-estado-da-arte.md](65-estado-da-arte.md).

| Situação | Modelo | Por quê |
|---|---|---|
| **Português, uso geral** | `neuralmind/bert-base-portuguese-cased` (BERTimbau) | melhor relação qualidade/tamanho em PT-BR; licença MIT |
| Português, precisa de mais qualidade | `neuralmind/bert-large-portuguese-cased` | 3× maior e mais lento |
| Inglês, uso geral | `answerdotai/ModernBERT-base` | sucessor real do BERT: 8.192 tokens, mais rápido e melhor |
| Multilíngue | `jhu-clsp/mmBERT-base` ou `FacebookAI/xlm-roberta-base` | 1.800+ e 100 línguas, respectivamente |
| Precisa ser pequeno/rápido | `distilbert-base-multilingual-cased` | ~40% menor, ~60% mais rápido, ~97% da qualidade |
| Embeddings e busca semântica | `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` | treinado para similaridade — o BERT cru não serve |
| Reranking de busca | um cross-encoder (`ms-marco-MiniLM`) | lê pergunta e documento juntos: mais preciso, mais caro |
| Só experimentando | `distilbert-base-uncased` | baixa rápido, roda em qualquer coisa |
| **Não use** | `bert-base-uncased` em produção nova | 2018; RoBERTa/ModernBERT ganham em tudo. Serve para reproduzir papers |

---

## 11 · Obsoleto

| Obsoleto | Substituto | Desde |
|---|---|---|
| `TFBertModel`, `FlaxBertModel` | só PyTorch | transformers 5.0 |
| `pipeline("question-answering")` | inferência manual | transformers 5.0 |
| `Trainer(tokenizer=...)` | `processing_class=` | transformers 4.46 (removido na 5.0) |
| `evaluation_strategy` | `eval_strategy` | transformers 4.41 |
| `warmup_ratio` | `warmup_steps` com float | transformers 5.0 |
| `torch_dtype=` | `dtype=` | transformers 5.0 |
| `use_auth_token=` | `token=` | transformers 4.35 |
| `huggingface-cli` | `hf` | huggingface_hub 1.0 |
| `TRANSFORMERS_CACHE` | `HF_HOME` | transformers 5.0 |
| `AutoModelWithLMHead` | `AutoModelForMaskedLM` | transformers 4.x |
| `tokenizer.encode_plus()` | `tokenizer()` | transformers 5.0 |
| Objetivo NSP no pré-treino | descartado (RoBERTa mostrou que atrapalha) | 2019 |
| `bert-base-uncased` para produção nova | ModernBERT / RoBERTa / BERTimbau | ~2023 |

---

## Autoteste

1. Qual classe usar para NER, e por que não `SequenceClassification`?
2. O que faz `attention_mask`, e o que acontece se você esquecer de passá-lo num lote com padding?
3. Por que `id2label` deve ser preenchido na criação do modelo?
4. Qual é o valor mágico que diz ao PyTorch "ignore esta posição na perda"?
5. Como simular lote 64 numa GPU que só aguenta 8?
6. Três parâmetros de `TrainingArguments` que mudaram de nome (ou sumiram) na v5.
7. Por que `max_length=128` é ~4× mais barato que 512, e não 4× exatamente proporcional?
8. Quando usar `sigmoid` em vez de `softmax` na saída?
9. Por que fixar `revision=` ao carregar um modelo em produção?

---

*Anterior: [04-como-comecar.md](04-como-comecar.md) · Próximo: [06-exemplos.md](06-exemplos.md)*
