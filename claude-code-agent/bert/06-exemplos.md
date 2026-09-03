# 06 · Exemplos — 12 receitas completas e executáveis

`Nível: intermediário` · `Todos executados em 12/08/2026, CPU, sem GPU` ·
`transformers 5.15.0 · torch 2.13.0+cpu · sentence-transformers 5.7.0`

Cada exemplo é **problema → código completo → saída real → explicação**. Nada de `...`
escondendo parte do código: tudo aqui foi rodado e a saída mostrada é a que apareceu.

| # | Exemplo | Precisa treinar? |
|---|---|---|
| [1](#1--completar-lacuna) | Completar lacuna (MLM) | não |
| [2](#2--análise-de-sentimento-sem-treinar) | Sentimento com modelo pronto | não |
| [3](#3--classificar-em-categorias-suas-sem-treinar-zero-shot) | Zero-shot: categorias suas, sem treinar | não |
| [4](#4--ner--extrair-pessoas-organizações-e-lugares) | NER: pessoas, organizações, lugares | não |
| [5](#5--pergunta-e-resposta-extrativa-sem-pipeline) | QA extrativo (sem pipeline, removido na v5) | não |
| [6](#6--busca-semântica-em-uma-base-de-perguntas) | Busca semântica | não |
| [7](#7--a-mesma-palavra-com-dois-sentidos) | Polissemia: "banco" em dois contextos | não |
| [8](#8--classificador-próprio-em-30-linhas) | Classificador próprio (fine-tuning) | **sim** |
| [9](#9--ner-próprio-com-rótulos-alinhados-a-subtokens) | NER próprio, com alinhamento de rótulos | **sim** |
| [10](#10--produção-1-classificar-500-mil-textos-sem-esperar-um-dia) | Produção: 500 mil textos em lote | não |
| [11](#11--produção-2-adaptação-ao-domínio-com-mlm-contínuo) | Produção: adaptação de domínio (MLM contínuo) | **sim** |
| [12](#12--medir-o-quanto-uma-frase-é-natural-pseudo-perplexidade) | Pseudo-perplexidade: frase natural? | não |

---

## 1 · Completar lacuna

**Problema:** ver o BERT fazendo o que foi treinado para fazer, e usar isso para sondar o que
ele "sabe".

```python
from transformers import pipeline

completar = pipeline("fill-mask", model="neuralmind/bert-base-portuguese-cased")

testes = [
    "O Brasil é o maior país da América do [MASK].",
    "A capital da França é [MASK].",
    "Ele foi ao banco para [MASK] dinheiro.",
]

for frase in testes:
    print(frase)
    for r in completar(frase)[:3]:
        print(f"   {r['score']:.3f}  {r['token_str']}")
```

**Saída real:**

```
O Brasil é o maior país da América do [MASK].
   0.955  Sul
   0.042  Norte
   0.002  sul
A capital da França é [MASK].
   0.826  Paris
   0.095  Cannes
   0.044  Nice
Ele foi ao banco para [MASK] dinheiro.
   0.448  pegar
   0.281  pedir
   0.036  conseguir
```

**Explicação.** O modelo nunca foi ensinado geografia. Ele aprendeu que, em textos da
Wikipédia em português, depois de "capital da França é" quase sempre vem "Paris". É
correlação estatística massiva, não conhecimento estruturado — por isso "Cannes" e "Nice"
aparecem em seguida: são as outras cidades francesas que o corpus associa a esse contexto.
No terceiro caso, o modelo desambiguou "banco" (instituição, não assento) usando a palavra
*dinheiro*, que vem **depois** — algo que um modelo unidirecional como o GPT não poderia usar
naquela posição.

---

## 2 · Análise de sentimento sem treinar

**Problema:** classificar avaliações de clientes em positivo/neutro/negativo, hoje, sem ter
dados rotulados.

```python
from transformers import pipeline

sentimento = pipeline(
    "text-classification",
    model="lxyuan/distilbert-base-multilingual-cased-sentiments-student",
    top_k=None,           # devolve todas as classes, não só a vencedora
)

for texto in ["o produto chegou quebrado e o suporte não respondeu",
              "entrega rápida, recomendo demais"]:
    resultado = sentimento(texto)[0]
    print(texto)
    print("   ", [(d["label"], round(d["score"], 3)) for d in resultado])
```

**Saída real:**

```
o produto chegou quebrado e o suporte não respondeu
    [('negative', 0.6), ('neutral', 0.329), ('positive', 0.071)]
entrega rápida, recomendo demais
    [('positive', 0.846), ('neutral', 0.096), ('negative', 0.058)]
```

**Explicação.** Alguém já afinou um DistilBERT multilíngue para sentimento e publicou. Você
herda o trabalho. Note a diferença de confiança: 0,60 na reclamação contra 0,85 no elogio —
o modelo é menos seguro em texto negativo com estrutura mais complexa. Em produção, esse
0,60 é exatamente o tipo de caso que deveria ir para revisão humana.

**Cuidado:** o `label` varia entre modelos (`positive`/`POSITIVE`/`LABEL_2`/`5 stars`).
Nunca deduza — leia o *model card* e confirme com `modelo.config.id2label`.

---

## 3 · Classificar em categorias suas, sem treinar (zero-shot)

**Problema:** você tem categorias específicas (`financeiro`, `suporte técnico`, `vendas`,
`cancelamento`) e nenhum dado rotulado. Ainda não dá para afinar nada.

```python
from transformers import pipeline

classificador = pipeline(
    "zero-shot-classification",
    model="MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7",
)

resultado = classificador(
    "O boleto não chegou e o vencimento é amanhã",
    candidate_labels=["financeiro", "suporte técnico", "vendas", "cancelamento"],
)
print([(rot, round(nota, 3)) for rot, nota in zip(resultado["labels"], resultado["scores"])])
```

**Saída real:**

```
[('financeiro', 0.826), ('cancelamento', 0.089), ('vendas', 0.068), ('suporte técnico', 0.018)]
```

**Explicação — o truque é lindo.** O modelo não conhece suas categorias. Ele foi treinado em
**NLI** (*natural language inference*): dado um par (premissa, hipótese), dizer se a segunda
decorre da primeira. O pipeline transforma cada categoria numa hipótese —
*"Este exemplo é financeiro."* — e pergunta ao modelo se ela decorre do seu texto. A nota de
"decorre" vira a nota da categoria.

**Quando usar:** dia 1 de um projeto, para rotular os primeiros exemplos rápido, ou quando as
categorias mudam toda semana.
**Quando não usar:** volume alto (é ~50× mais lento que um classificador afinado, porque roda
o modelo uma vez por categoria) ou quando a acurácia importa — com algumas centenas de
exemplos rotulados, um modelo afinado ganha com folga. O caminho profissional é usar
zero-shot para rotular os primeiros 300 exemplos, revisar à mão, e então afinar
(exemplo 8).

---

## 4 · NER — extrair pessoas, organizações e lugares

**Problema:** extrair entidades de textos livres para alimentar um banco de dados.

```python
from transformers import pipeline

ner = pipeline(
    "token-classification",
    model="Babelscape/wikineural-multilingual-ner",
    aggregation_strategy="simple",   # junta 'Pe','##tro','##bras' numa entidade só
)

texto = "Maria Silva assinou o contrato com a Petrobras em São Paulo no dia 12 de março."

for e in ner(texto):
    print(f"{e['entity_group']:6s} {e['score']:.3f} {e['word']!r}")
```

**Saída real:**

```
PER    0.999 'Maria Silva'
ORG    0.998 'Petrobras'
LOC    1.000 'São Paulo'
```

**Explicação.** Sem `aggregation_strategy="simple"`, a saída viria fragmentada em subtokens
com rótulos `B-PER`, `I-PER` (*Begin* e *Inside*) — o esquema **BIO**, padrão do campo.
A agregação faz a costura. Repare que a data (12 de março) **não** foi capturada: este modelo
só conhece PER/ORG/LOC/MISC. Para datas, valores e CPF, o certo é regex — não gaste um
transformer para achar `\d{2}/\d{2}/\d{4}`.

**Uso real de produção:** anonimização de documentos (LGPD). Rode o NER, substitua cada PER
por `[NOME]`, e você tem um pipeline de despersonalização. Cuidado: modelo genérico erra em
nomes brasileiros pouco comuns — meça antes de confiar em algo com implicação legal.

---

## 5 · Pergunta e resposta extrativa (sem pipeline)

**Problema:** dado um documento, achar **onde** está a resposta a uma pergunta.
O `pipeline("question-answering")` **foi removido no transformers 5**, então este exemplo
mostra o caminho manual — que é o que você vai precisar de qualquer forma.

```python
import torch
from transformers import AutoTokenizer, AutoModelForQuestionAnswering

M = "pierreguillou/bert-base-cased-squad-v1.1-portuguese"
tok = AutoTokenizer.from_pretrained(M)
modelo = AutoModelForQuestionAnswering.from_pretrained(M).eval()

contexto = ("O Pantanal é a maior planície alagável do mundo, com cerca de 150 mil "
            "quilômetros quadrados, distribuídos entre Brasil, Bolívia e Paraguai.")

for pergunta in ["Qual a área do Pantanal?", "Quais países dividem o Pantanal?"]:
    entrada = tok(pergunta, contexto, return_tensors="pt",
                  truncation="only_second", max_length=384)
    with torch.no_grad():
        saida = modelo(**entrada)

    # A cabeça de QA dá duas notas por token: "começa aqui" e "termina aqui".
    inicio = int(saida.start_logits.argmax())
    fim = int(saida.end_logits.argmax())
    resposta = tok.decode(entrada["input_ids"][0][inicio : fim + 1])
    print("P:", pergunta)
    print("R:", resposta)
```

**Saída real:**

```
P: Qual a área do Pantanal?
R: 150 mil quilômetros quadrados
P: Quais países dividem o Pantanal?
R: Brasil, Bolívia e Paraguai
```

**Explicação.** `truncation="only_second"` corta o *contexto* se o par não couber, nunca a
pergunta — cortar a pergunta seria absurdo. A resposta é sempre um **trecho literal** do
contexto: o modelo só sabe apontar dois índices. Isso é uma limitação e ao mesmo tempo a
maior virtude dessa abordagem frente a um LLM: **ele não pode alucinar**. Se a resposta não
está no texto, ele aponta para algum lugar errado (e o `start_logits` fica baixo, o que dá
para usar como limiar), mas nunca inventa um fato novo.

Em documento longo (> 384 tokens), o padrão do campo é fatiar com sobreposição (`stride`) e
ficar com a janela de maior nota.

---

## 6 · Busca semântica em uma base de perguntas

**Problema:** o usuário digita com as palavras dele; a sua base de ajuda usa outras.
Busca por palavra-chave falha; busca por significado resolve.

```python
# pip install sentence-transformers
from sentence_transformers import SentenceTransformer, util

modelo = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

base = [
    "Como cancelar minha assinatura",
    "Alterar forma de pagamento",
    "Redefinir senha de acesso",
    "Emitir segunda via do boleto",
    "Horário de atendimento",
]
emb_base = modelo.encode(base, normalize_embeddings=True, convert_to_tensor=True)

for consulta in ["quero encerrar meu plano", "esqueci minha senha"]:
    emb = modelo.encode(consulta, normalize_embeddings=True, convert_to_tensor=True)
    achados = util.semantic_search(emb, emb_base, top_k=2)[0]
    print(f"{consulta!r} ->",
          " | ".join(f"{base[a['corpus_id']]} ({a['score']:.3f})" for a in achados))
```

**Saída real:**

```
'quero encerrar meu plano' -> Como cancelar minha assinatura (0.531) | Horário de atendimento (0.370)
'esqueci minha senha'      -> Como cancelar minha assinatura (0.583) | Redefinir senha de acesso (0.430)
```

**Explicação — e a lição está no erro.** A primeira consulta funcionou: "encerrar meu plano"
achou "cancelar minha assinatura" sem uma palavra em comum. Isso é exatamente o que busca
lexical não faz.

A segunda **errou feio**: "esqueci minha senha" deveria casar com "Redefinir senha de acesso"
(que tem a palavra *senha*!), e o modelo colocou "cancelar assinatura" na frente, com nota
maior. Não editei este resultado — ele é a saída real, e ensina três coisas de uma vez:

1. **Modelo multilíngue pequeno (MiniLM) é fraco em português.** É rápido e leve, e paga por
   isso. Para busca séria em PT, avalie modelos maiores e específicos, e **meça** com as suas
   consultas antes de escolher.
2. **Nunca confie em busca semântica pura.** O padrão de produção é **híbrido**: combinar
   BM25 (lexical, que acertaria na hora pela palavra "senha") com vetores, e reordenar com um
   *cross-encoder*. Ver [16-embeddings-e-busca-semantica.md](16-embeddings-e-busca-semantica.md).
3. **Cosseno alto não é sinônimo de relevante.** 0,583 e 0,531 são notas parecidas para
   resultados de qualidade muito diferente. Limiar absoluto de similaridade é armadilha.

Para comparação, o mesmo modelo em frases mais claramente distintas se comporta bem:

```
sim("quero cancelar minha assinatura", "desejo encerrar meu plano")  = 0.567
sim("quero cancelar minha assinatura", "qual o horário de funcionamento") = 0.200
```

Contra 0,672 × 0,504 do BERTimbau cru ([04-como-comecar.md](04-como-comecar.md)): a
**separação** entre relevante e irrelevante triplicou, mesmo com o número absoluto menor.
É a separação que importa, não o valor.

---

## 7 · A mesma palavra com dois sentidos

**Problema:** demonstrar, com números, a afirmação central sobre o BERT — que o vetor de uma
palavra depende do contexto.

```python
import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModel

M = "neuralmind/bert-base-portuguese-cased"
tok = AutoTokenizer.from_pretrained(M)
modelo = AutoModel.from_pretrained(M).eval()

def vetor_da_palavra(frase: str, palavra: str) -> torch.Tensor:
    """Devolve o vetor contextual da primeira ocorrência de `palavra` na frase."""
    entrada = tok(frase, return_tensors="pt")
    tokens = tok.convert_ids_to_tokens(entrada["input_ids"][0])
    i = tokens.index(palavra)                       # posição do token na sequência
    with torch.no_grad():
        h = modelo(**entrada).last_hidden_state[0, i]
    return F.normalize(h, dim=-1)

praca      = vetor_da_palavra("Sentei no banco da praça para descansar", "banco")
agencia    = vetor_da_palavra("Fui ao banco sacar dinheiro na agência", "banco")
emprestimo = vetor_da_palavra("O banco aprovou meu empréstimo hoje", "banco")

print(f"praça × agência     : {praca @ agencia:.3f}")
print(f"agência × empréstimo: {agencia @ emprestimo:.3f}")
```

**Saída real:**

```
praça × agência     : 0.667
agência × empréstimo: 0.860
```

**Explicação.** A mesma sequência de letras, `banco`, produziu vetores diferentes. Os dois
sentidos financeiros ficaram próximos (0,860); o sentido de assento ficou claramente mais
distante (0,667). Com word2vec (2013), os três valores seriam **1,000** — havia um único
vetor por palavra, para sempre. Essa é, em uma medição, a diferença entre a geração anterior
e o BERT. Ver [11-historia.md](11-historia.md).

Note também que 0,667 não é "longe". Vetores do BERT são todos razoavelmente parecidos entre
si — o espaço é *anisotrópico*, um fenômeno estudado e explicado em
[20-interpretabilidade-e-bertologia.md](20-interpretabilidade-e-bertologia.md).

---

## 8 · Classificador próprio, em 30 linhas

**Problema:** você tem seus dados rotulados e quer um modelo especializado.
Esta é a versão mínima; a versão de produção completa está em
[07-projeto-modelo/](07-projeto-modelo/README.md).

```python
import numpy as np
from datasets import Dataset
from sklearn.metrics import f1_score
from transformers import (AutoModelForSequenceClassification, AutoTokenizer,
                          DataCollatorWithPadding, Trainer, TrainingArguments, set_seed)

set_seed(42)
M = "neuralmind/bert-base-portuguese-cased"

textos = ["meu boleto não chegou", "não consigo fazer login", "quero contratar mais licenças",
          "a fatura veio errada", "o sistema está fora do ar", "qual o preço do plano anual"]
rotulos = [0, 1, 2, 0, 1, 2]                        # 0=financeiro 1=técnico 2=comercial
nomes = {0: "FINANCEIRO", 1: "TECNICO", 2: "COMERCIAL"}

tok = AutoTokenizer.from_pretrained(M)
ds = Dataset.from_dict({"text": textos, "labels": rotulos}).map(
    lambda b: tok(b["text"], truncation=True, max_length=128), batched=True,
    remove_columns=["text"])

modelo = AutoModelForSequenceClassification.from_pretrained(
    M, num_labels=3, id2label=nomes, label2id={v: k for k, v in nomes.items()})

trainer = Trainer(
    model=modelo,
    args=TrainingArguments(output_dir="./saida", num_train_epochs=8,
                           per_device_train_batch_size=4, learning_rate=5e-5,
                           report_to="none", logging_steps=5, seed=42),
    train_dataset=ds,
    processing_class=tok,                            # v5: era tokenizer=
    data_collator=DataCollatorWithPadding(tok),
)
trainer.train()
trainer.save_model("./meu-classificador")
tok.save_pretrained("./meu-classificador")
```

Usando:

```python
from transformers import pipeline
p = pipeline("text-classification", model="./meu-classificador")
print(p("a cobrança deste mês está errada"))
```

**Explicação e alerta.** Isto roda e produz um modelo. Mas com 6 exemplos e sem conjunto de
teste, o resultado **não significa nada** — o modelo decorou. Serve para verificar que a
mecânica funciona, não para avaliar qualidade. O mínimo defensável é ~50 exemplos por classe
e três conjuntos separados; a medição empírica dessa diferença está no
[README do projeto-modelo](07-projeto-modelo/README.md#experimentos-reais-deste-projeto-e-a-lição-que-vale-mais-que-o-código).

---

## 9 · NER próprio, com rótulos alinhados a subtokens

**Problema:** treinar NER no seu domínio. O detalhe difícil aqui não é o treino — é que
**uma palavra vira vários tokens**, e os rótulos precisam ser realinhados.

```python
from transformers import AutoTokenizer

tok = AutoTokenizer.from_pretrained("neuralmind/bert-base-portuguese-cased")

palavras = ["Maria", "trabalha", "na", "Braskem"]
rotulos  = ["B-PER", "O",        "O",  "B-ORG"]        # esquema BIO
etiqueta2id = {"O": 0, "B-PER": 1, "I-PER": 2, "B-ORG": 3, "I-ORG": 4}

entrada = tok(palavras, is_split_into_words=True, truncation=True, max_length=128)
ids_palavra = entrada.word_ids()          # v5: era .words()

alinhados, anterior = [], None
for wid in ids_palavra:
    if wid is None:                       # [CLS] e [SEP]
        alinhados.append(-100)            # -100 = "ignore na perda"
    elif wid != anterior:                 # primeiro subtoken da palavra
        alinhados.append(etiqueta2id[rotulos[wid]])
    else:                                 # subtokens seguintes da MESMA palavra
        alinhados.append(-100)
    anterior = wid

print(list(zip(tok.convert_ids_to_tokens(entrada["input_ids"]), alinhados)))
```

**Saída real:**

```
[('[CLS]', -100), ('Maria', 1), ('trabalha', 0), ('na', 0),
 ('Bras', 3), ('##ke', -100), ('##m', -100), ('[SEP]', -100)]
```

**Explicação.** "Braskem" virou três tokens. Rotular o primeiro com `B-ORG` (id 3) e marcar
os demais com `-100` é a convenção padrão (a alternativa — repetir `I-ORG` nos subtokens
seguintes — também é usada; mude só se souber por quê). Pular esse alinhamento é o bug nº 1
de quem treina NER pela primeira vez: o modelo treina, a perda cai, e as previsões saem
sistematicamente deslocadas.

Detalhe que ensina sobre tokenização: nesse mesmo modelo, `Petrobras` e `Localiza` são **um
token só**, porque aparecem muito no corpus brasileiro em que o BERTimbau foi pré-treinado.
Já `Nubank` vira `['Nu', '##ban', '##k']` — a empresa é recente demais para o corpus. O
vocabulário é um retrato datado do texto de treino. Ver
[12-tokenizacao-wordpiece.md](12-tokenizacao-wordpiece.md).

No treino, use `DataCollatorForTokenClassification`, que preenche **rótulos** além de tokens,
e `AutoModelForTokenClassification`.

---

## 10 · Produção 1: classificar 500 mil textos sem esperar um dia

**Problema:** você precisa rodar o classificador sobre a base histórica inteira.

```python
import time
from transformers import pipeline

M = "neuralmind/bert-base-portuguese-cased"
textos = [f"chamado de teste número {i} sobre cobrança" for i in range(64)]

p = pipeline("feature-extraction", model=M)

t0 = time.perf_counter(); [p(t) for t in textos]; t1 = time.perf_counter()
p(textos, batch_size=32);                          t2 = time.perf_counter()

print(f"um a um: {t1-t0:.2f}s | em lote(32): {t2-t1:.2f}s | ganho {(t1-t0)/(t2-t1):.1f}x")
```

**Saída real (CPU, sem GPU):**

```
um a um: 2.12s | em lote(32): 0.49s | ganho 4.3x
```

**Explicação.** 4,3× **sem trocar de hardware nem de modelo** — só agrupando. A GPU (e a CPU
moderna) fica ociosa esperando dados quando você manda um texto por vez; o custo fixo por
chamada domina. Em GPU, o ganho costuma passar de 20×.

Empilhando as otimizações da [tabela do manual](05-manual-de-uso.md#9--desempenho-e-memória),
para uma carga de 500 mil textos:

| Estratégia | Tempo estimado (CPU) |
|---|---|
| um a um, `max_length=512` | ~46 h |
| em lote 32, `max_length=512` | ~11 h |
| em lote 32, `max_length=128` | ~3 h |
| + ONNX Runtime, int8 | ~1 h |
| + DistilBERT no lugar do BERT-base | ~30 min |

Os números são extrapolações da medição acima, não medições diretas de 500 mil itens — mas as
ordens de grandeza são as que se veem na prática. O ponto: **decisões de engenharia valem
duas ordens de grandeza**, mais do que qualquer troca de modelo. Detalhes em
[19-producao-e-otimizacao.md](19-producao-e-otimizacao.md).

Ganho adicional fácil: **ordene os textos por comprimento antes de agrupar**. Lotes
homogêneos desperdiçam muito menos padding.

---

## 11 · Produção 2: adaptação ao domínio com MLM contínuo

**Problema:** seu texto é jurídico, médico ou de um nicho industrial, cheio de vocabulário
que a Wikipédia não tem. O BERT genérico tokeniza "petição de embargos infringentes" em
pedaços sem sentido e classifica mal.

**Solução:** antes de afinar para a tarefa, continue o **pré-treino** (MLM) no seu texto cru
— que você tem em abundância e **não precisa rotular**. O campo chama isso de *domain-adaptive
pretraining* (Gururangan et al., 2020, "Don't Stop Pretraining"), e costuma render de 1 a 5
pontos de F1 na tarefa final.

```python
from datasets import Dataset
from transformers import (AutoModelForMaskedLM, AutoTokenizer,
                          DataCollatorForLanguageModeling, Trainer, TrainingArguments)

M = "neuralmind/bert-base-portuguese-cased"
tok = AutoTokenizer.from_pretrained(M)
modelo = AutoModelForMaskedLM.from_pretrained(M)     # note: MaskedLM, não Classification

# Seu texto CRU, sem rótulo nenhum. Na vida real: dezenas de milhares de documentos.
corpus = [
    "O contribuinte apresentou petição de embargos infringentes ao acórdão.",
    "A apuração do ICMS-ST considerou a margem de valor agregado do protocolo.",
    "O laudo pericial concluiu pela insalubridade em grau médio.",
]
ds = Dataset.from_dict({"text": corpus}).map(
    lambda b: tok(b["text"], truncation=True, max_length=256),
    batched=True, remove_columns=["text"])

trainer = Trainer(
    model=modelo,
    args=TrainingArguments(output_dir="./mlm", num_train_epochs=3,
                           per_device_train_batch_size=8, learning_rate=5e-5,
                           report_to="none", seed=42),
    train_dataset=ds,
    processing_class=tok,
    # Este collator mascara 15% dos tokens A CADA ÉPOCA, de forma diferente.
    # É o mesmo objetivo do pré-treino original — você está continuando o treino do Google.
    data_collator=DataCollatorForLanguageModeling(tok, mlm=True, mlm_probability=0.15),
)
trainer.train()
trainer.save_model("./bert-juridico")     # agora afine ESTE para a sua tarefa
```

**Explicação.** Depois disso, use `./bert-juridico` como `MODELO_BASE` no exemplo 8 ou no
projeto-modelo. Quando vale a pena: quando você tem **muito** texto do domínio (ordem de
dezenas de MB) e o vocabulário é realmente distante do português comum. Com 3 frases, como
acima, não muda nada — o exemplo mostra a mecânica.

**Detalhe importante:** o mascaramento é **dinâmico** aqui (posições diferentes a cada
época). O BERT original mascarava uma vez só, de forma estática; o RoBERTa mostrou em 2019
que o dinâmico é melhor, e virou padrão. Ver [14-pre-treino-mlm-nsp.md](14-pre-treino-mlm-nsp.md).

---

## 12 · Medir o quanto uma frase é "natural" (pseudo-perplexidade)

**Problema:** ordenar frases por fluência — útil para escolher entre saídas de um sistema,
detectar texto corrompido por OCR, ou filtrar corpus.

```python
import torch
from transformers import AutoModelForMaskedLM, AutoTokenizer

M = "neuralmind/bert-base-portuguese-cased"
tok = AutoTokenizer.from_pretrained(M)
modelo = AutoModelForMaskedLM.from_pretrained(M).eval()

def pseudo_log_verossimilhanca(frase: str) -> float:
    """Mascara um token por vez e soma o log da probabilidade do token correto."""
    ids = tok(frase, return_tensors="pt")["input_ids"]
    total = 0.0
    for i in range(1, ids.shape[1] - 1):              # pula [CLS] e [SEP]
        copia = ids.clone()
        alvo = int(copia[0, i])
        copia[0, i] = tok.mask_token_id
        with torch.no_grad():
            logits = modelo(copia).logits[0, i]
        total += float(torch.log_softmax(logits, -1)[alvo])
    return total / (ids.shape[1] - 2)                 # média por token

for frase in ["O gato subiu no telhado.",
              "O telhado subiu no gato.",
              "Gato o subiu telhado no."]:
    print(f"{pseudo_log_verossimilhanca(frase):7.3f}  {frase}")
```

**Saída real:**

```
 -1.842  O gato subiu no telhado.
 -4.820  O telhado subiu no gato.
 -8.785  Gato o subiu telhado no.
```

**Explicação.** Quanto maior (menos negativo), mais "esperada" a frase é para o modelo. A
ordem saiu exatamente como se esperava: gramatical e plausível (−1,84), gramatical mas
semanticamente absurda (−4,82), e agramatical (−8,79). O modelo separa **gramática** de
**plausibilidade semântica** — e as duas quedas são de tamanho parecido, o que diz algo sobre
como o MLM codifica as duas coisas juntas. Note o custo: **uma passada do modelo por token**,
então é caro — não use isso em escala sem pensar.

Por que "pseudo"? Um modelo autorregressivo (GPT) calcula a verossimilhança verdadeira da
frase em uma passada, pela regra da cadeia. O BERT não pode: ele é bidirecional, e a
probabilidade de cada token já viu os outros. O que se calcula aqui é a *pseudo*-log-
verossimilhança (Salazar et al., 2020) — uma aproximação bem-comportada, mas não a
probabilidade da frase. A discussão formal está em
[60-teoria-avancada.md](60-teoria-avancada.md).

---

## Autoteste

1. No exemplo 3, como o modelo classifica em categorias que nunca viu? Qual é o truque?
2. Por que o `pipeline("question-answering")` não existe mais, e como se faz QA hoje?
3. No exemplo 5, por que `truncation="only_second"` e não `truncation=True`?
4. No exemplo 6, o modelo errou "esqueci minha senha". Cite duas correções de arquitetura de busca.
5. Por que a similaridade entre os dois "bancos financeiros" deu 0,860 e não 1,000?
6. No exemplo 9, por que alguns rótulos viram `-100`?
7. Qual foi o ganho medido de processar em lote, e por que ele é maior em GPU?
8. Quando compensa fazer MLM contínuo antes de afinar? E quando é desperdício?
9. Por que se chama *pseudo*-perplexidade e não perplexidade?
10. Nos exemplos 2 e 3, você conseguiu resultado sem nenhum dado rotulado. Por que ainda assim vale a pena afinar?

---

*Anterior: [05-manual-de-uso.md](05-manual-de-uso.md) · Próximo: [07-projeto-modelo/](07-projeto-modelo/README.md)*
