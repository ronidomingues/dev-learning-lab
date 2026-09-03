# 15 · Fine-tuning — adaptar o modelo à sua tarefa

`Nível: intermediário` · `Última atualização: 12/08/2026`

O que você vai fazer 95% do tempo. Este arquivo é a teoria e a prática do afinamento: o que
acontece por dentro, como escolher hiperparâmetros, o que fazer quando não funciona.

---

## 1 · O que é, mecanicamente

```
     BERT pré-treinado                  seu modelo
   ┌──────────────────┐              ┌──────────────────┐
   │  12 blocos       │              │  12 blocos       │  ← pesos continuam mudando,
   │  (110 M pesos)   │   +  seus    │  (110 M ajustados)│    só que pouco
   ├──────────────────┤     dados    ├──────────────────┤
   │ cabeça de MLM    │   ────────►  │ cabeça de        │  ← trocada e treinada
   │ (descartada)     │              │ classificação    │    do zero
   └──────────────────┘              └──────────────────┘
```

Três coisas acontecem:

1. **A cabeça antiga é jogada fora** e uma nova, aleatória, é criada — daí o aviso
   `classifier.weight | MISSING`.
2. **Tudo é treinado junto**, com taxa de aprendizado pequena: a cabeça aprende do zero, o
   tronco se ajusta suavemente.
3. **Poucas épocas.** 2 a 4 no caso típico. Mais que isso costuma piorar.

**Por que a taxa de aprendizado é tão pequena (2e-5 a 5e-5, contra 1e-3 típico)?**
Porque o tronco já sabe português. Passos grandes o empurrariam para longe do que aprendeu —
o fenômeno chamado *catastrophic forgetting* (esquecimento catastrófico). Você quer um
empurrão, não uma reconstrução.

---

## 2 · A receita padrão (que continua sendo o melhor ponto de partida)

Do próprio artigo do BERT, Apêndice A.3, e ainda válida em 2026:

| Hiperparâmetro | Valor recomendado | Faixa segura |
|---|---|---|
| Taxa de aprendizado | **3e-5** | 2e-5, 3e-5, 5e-5 |
| Lote | **16** ou 32 | 8 a 64 |
| Épocas | **3** | 2 a 4 (mais, se o conjunto for pequeno) |
| Otimizador | AdamW | — |
| Warmup | 6% a 10% dos passos | — |
| Weight decay | 0,01 | — |
| `max_length` | o menor que couber seus textos | 128 quase sempre |

**Como ajustar quando não funciona**, em ordem de o que tentar primeiro:

```
Não converge / perda não cai      → taxa de aprendizado ALTA demais. Divida por 3.
Perda cai e a métrica não sobe    → problema nos dados ou na métrica, não no modelo.
Treino ótimo, teste ruim          → overfitting. Menos épocas, mais dados, mais dropout.
Treino e teste ruins              → underfitting. Mais épocas, taxa maior, modelo maior.
Resultado varia muito entre runs  → conjunto pequeno demais. Use validação cruzada.
Estoura a memória                 → lote menor + gradient_accumulation_steps.
```

---

## 3 · Quantos dados eu preciso?

A pergunta que todo mundo faz. A resposta honesta depende da dificuldade da tarefa, mas há
ordens de grandeza confiáveis:

| Exemplos **por classe** | O que esperar |
|---|---|
| < 20 | nada confiável. Use zero-shot ou few-shot com LLM |
| 50–100 | funciona para tarefas fáceis e bem separadas; resultado instável |
| 200–500 | **o joelho da curva** — é onde a maioria dos projetos deveria mirar |
| 1.000–5.000 | resultado sólido; ganhos ainda visíveis |
| 10.000+ | retornos decrescentes; ganho vem de qualidade, não de quantidade |

Medição real e reprodutível dessa curva, feita neste curso: dobrar de 25 para 45 exemplos por
classe levou a F1 macro de ~0,70 para ~0,91 — enquanto **nenhum** ajuste de hiperparâmetro
tirou o modelo de ~0,70 com os dados menores. Detalhes na
[tabela de experimentos do projeto-modelo](07-projeto-modelo/README.md#experimentos-reais-deste-projeto-e-a-lição-que-vale-mais-que-o-código).

**Regra prática:** se o modelo está ruim, sua primeira hipótese deve ser *"faltam dados ou os
rótulos estão inconsistentes"*, não *"a taxa de aprendizado está errada"*.

### Como conseguir dados quando você não tem

Em ordem crescente de esforço:

1. **Zero-shot para pré-rotular**, e um humano só revisa
   ([06-exemplos.md, exemplo 3](06-exemplos.md#3--classificar-em-categorias-suas-sem-treinar-zero-shot)).
   Revisar é 5 a 10× mais rápido que rotular do zero.
2. **LLM como rotulador**: peça a um modelo grande para rotular 2 mil exemplos, revise uma
   amostra, e afine um BERT nisso. É destilação na prática — o LLM caro rotula uma vez, o BERT
   barato serve para sempre. Este é hoje o padrão de fato em 2026 quando não há dados.
3. **Aprendizado ativo**: rotule 200 exemplos, treine, e depois rotule só aqueles em que o
   modelo tem menos confiança. Rende muito mais por hora de anotação que rotular aleatório.
4. **Aumento de dados**: retrotradução (PT→EN→PT), troca de sinônimos. Ganho modesto e
   arriscado — pode introduzir ruído de rótulo.

---

## 4 · Cabeças por tarefa

O que muda concretamente entre as tarefas:

### Classificação de sequência

```
[CLS] o boleto não chegou [SEP]
  ↓ (vetor 768 da posição do [CLS])
  Linear(768 → n_classes)
  ↓
  logits → softmax → probabilidades
```

Multirrótulo (várias classes ao mesmo tempo): mesma cabeça, mas com `sigmoid` no lugar de
`softmax` e perda `BCEWithLogitsLoss`. Configure com
`problem_type="multi_label_classification"`.

### Classificação de token (NER)

```
[CLS] Maria trabalha na Bras ##ke ##m [SEP]
        ↓       ↓      ↓    ↓
     Linear(768 → n_tags) aplicado a CADA token
        ↓       ↓      ↓    ↓
     B-PER     O      O   B-ORG
```

O desafio está no alinhamento de rótulos com subtokens — ver
[06-exemplos.md, exemplo 9](06-exemplos.md#9--ner-próprio-com-rótulos-alinhados-a-subtokens).

### QA extrativo

Duas cabeças lineares (768 → 1) por token: uma para "a resposta começa aqui", outra para
"termina aqui". A resposta é o par (início, fim) de maior soma de logits, com `fim ≥ início`.

### Similaridade de frases

Duas arquiteturas, com trade-off explicado em
[10-fundamentos.md](10-fundamentos.md#7--bi-encoder--cross-encoder-a-distinção-que-mais-confunde):
bi-encoder (rápido, indexável) e cross-encoder (preciso, caro).

---

## 5 · Congelar camadas: quando e por quê

Você pode congelar parte do modelo (não atualizar seus pesos):

```python
# congela os embeddings e as 6 primeiras camadas
for nome, p in modelo.named_parameters():
    if nome.startswith("bert.embeddings") or any(f"encoder.layer.{i}." in nome for i in range(6)):
        p.requires_grad = False

treinaveis = sum(p.numel() for p in modelo.parameters() if p.requires_grad)
print(f"treináveis: {treinaveis/1e6:.1f}M de {sum(p.numel() for p in modelo.parameters())/1e6:.1f}M")
```

| Estratégia | Quando usar | Custo |
|---|---|---|
| **Afinar tudo** (padrão) | caso normal; é o que dá melhor resultado | maior memória |
| Congelar embeddings | conjunto pequeno; evita destruir o vocabulário | pequena economia |
| Congelar metade das camadas | dados escassos, ou hardware limitado | −40% de memória, −1 a 3 pontos |
| Congelar tudo (só a cabeça treina) | *feature extraction*; quando você precisa reusar o mesmo tronco para muitas tarefas | muito rápido, resultado bem pior |

**Recomendação:** comece afinando tudo. Congelar é otimização, e otimização prematura aqui
custa qualidade. A exceção real é quando você vai servir 20 tarefas diferentes com um tronco
compartilhado — aí congelar é decisão de arquitetura, não de treino.

### LoRA e PEFT: vale para BERT?

LoRA (adaptadores de baixo posto) revolucionou o afinamento de LLMs de bilhões de parâmetros,
onde treinar tudo é impossível. Para BERT-base, **normalmente não compensa**: 110 M de
parâmetros cabem inteiros em qualquer GPU moderna, e o afinamento completo dá resultado
melhor. Vale considerar quando: você precisa manter dezenas de variantes da mesma base (LoRA
pesa alguns MB por tarefa em vez de 440 MB), ou está usando um encoder grande de verdade.

---

## 6 · O que dá errado, e o que fazer

### Esquecimento catastrófico

Taxa de aprendizado alta destrói o conhecimento pré-treinado. Sintoma: a perda de treino cai
bem, mas o modelo generaliza pior que antes de treinar. Correção: `learning_rate ≤ 5e-5`,
warmup, e menos épocas.

### Instabilidade em conjuntos pequenos

Com poucos milhares de exemplos, o afinamento do BERT é **notoriamente instável**: trocar só a
semente aleatória pode mudar a F1 em vários pontos. Isso está documentado na literatura
(Dodge et al., 2020) e foi reproduzido neste curso.

O que fazer:
- rode **3 a 5 sementes** e reporte média ± desvio (não o melhor resultado — isso é fraude
  estatística involuntária);
- use validação cruzada de 5 folds em vez de uma divisão única;
- prefira mais épocas com warmup a poucas épocas agressivas.

### Desbalanceamento de classes

Se 95% dos exemplos são de uma classe, o modelo aprende a responder sempre ela e acerta 95%.

| Solução | Comentário |
|---|---|
| Pesos na perda (`class_weight`) | primeira tentativa, barata; sobrescreva `compute_loss` |
| Subamostrar a classe grande | joga dados fora, mas funciona |
| Sobreamostrar a pequena | risco de overfitting nos poucos exemplos repetidos |
| **Trocar a métrica** para F1 macro | obrigatório de qualquer forma |
| Ajustar o limiar de decisão | frequentemente o que mais rende, e o mais esquecido |

### Vazamento de dados

Duplicatas entre treino e teste, ou um identificador que "entrega" a resposta (ex.: o número
do protocolo correlacionado com o setor). Sintoma: resultado bom demais. Se a acurácia passou
de 98% numa tarefa difícil, **procure o vazamento antes de comemorar** — ele está lá.

### Rótulos inconsistentes

O limite superior do seu modelo é a concordância entre os anotadores humanos. Se dois humanos
concordam em 80% dos casos, nenhum modelo passa muito disso — e a diferença entre 78% e 82%
de acurácia é ruído do rótulo, não do modelo. Meça a concordância antes de perseguir décimos.

---

## 7 · Checklist de um afinamento bem feito

- [ ] Três conjuntos: treino, validação, teste — e o teste usado **uma vez só**
- [ ] Divisão estratificada, sem duplicatas entre conjuntos
- [ ] Semente fixa e registrada
- [ ] Métrica adequada ao desbalanceamento (F1 macro, não acurácia)
- [ ] `load_best_model_at_end=True` com `metric_for_best_model`
- [ ] Matriz de confusão inspecionada, não só o número agregado
- [ ] Os 20 erros de maior confiança lidos, um por um
- [ ] Resultado de 3+ sementes, reportado como média ± desvio
- [ ] Modelo **e** tokenizador salvos na mesma pasta
- [ ] `id2label` preenchido
- [ ] Um baseline burro medido para comparação (classe majoritária, ou TF-IDF + regressão logística)

**O último item é o mais ignorado e o mais valioso.** Se um TF-IDF com regressão logística —
que treina em 2 segundos — chega a 0,89 e o seu BERT chega a 0,91, o BERT provavelmente não
vale a complexidade operacional. Meça sempre o baseline burro. Ele às vezes ganha.

---

## Autoteste

1. O que exatamente é descartado do modelo pré-treinado durante o afinamento?
2. Por que a taxa de aprendizado do afinamento é 20× menor que a de um treino do zero?
3. Quantos exemplos por classe é o "joelho da curva", e o que isso significa na prática?
4. Cite três formas de conseguir dados rotulados quando você não tem nenhum.
5. Por que a instabilidade entre sementes é um problema, e como reportar resultado honestamente?
6. Você tem 95% de uma classe e 5% de outra. Liste quatro correções possíveis.
7. Quando congelar camadas ajuda, e quando é otimização prematura?
8. Por que LoRA raramente compensa em BERT-base?
9. Qual é o baseline burro, e por que ele deve ser sempre medido?
10. Acurácia de 99% numa tarefa difícil. O que você suspeita primeiro?

---

## Fontes

- Devlin et al. (2019). *BERT*, Apêndice A.3 (hiperparâmetros de fine-tuning).
- Dodge et al. (2020). *Fine-Tuning Pretrained Language Models: Weight Initializations, Data Orders, and Early Stopping*. [arXiv:2002.06305](https://arxiv.org/abs/2002.06305)
- Sun et al. (2019). *How to Fine-Tune BERT for Text Classification?* [arXiv:1905.05583](https://arxiv.org/abs/1905.05583)
- Hu et al. (2021). *LoRA*. [arXiv:2106.09685](https://arxiv.org/abs/2106.09685)

---

*Anterior: [14-pre-treino-mlm-nsp.md](14-pre-treino-mlm-nsp.md) · Próximo: [16-embeddings-e-busca-semantica.md](16-embeddings-e-busca-semantica.md)*
