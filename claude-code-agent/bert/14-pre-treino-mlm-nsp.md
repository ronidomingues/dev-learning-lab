# 14 · Pré-treino — como o BERT aprendeu a língua

`Nível: intermediário → avançado` · `Última atualização: 12/08/2026`

Como um modelo aprende português (ou inglês) sem que ninguém lhe ensine nada, a partir de
texto cru. E por que a tarefa artificial escolhida funciona tão bem.

---

## 1 · O problema de treinar sem rótulo

Aprendizado supervisionado exige pares (entrada, resposta certa). Rotular custa caro:
anotar 100 mil frases com sentimento custa dezenas de milhares de reais e semanas.

Texto cru, por outro lado, é praticamente gratuito e existe aos terabytes.

A saída é o **aprendizado auto-supervisionado**: inventar uma tarefa cuja resposta certa já
está no próprio texto. Você esconde parte do dado e pede para o modelo reconstruí-la. O
"rótulo" é o que foi escondido. Custo de anotação: zero.

BERT usou duas dessas tarefas ao mesmo tempo — uma que funcionou espetacularmente e outra que
o campo descartou em um ano.

---

## 2 · MLM — Masked Language Modeling

### A regra dos 80/10/10

O procedimento é mais sutil do que "esconda 15% e adivinhe". Para cada token sorteado (15%
do total):

```
80% das vezes → troca por [MASK]
                "o gato subiu no telhado"  →  "o gato [MASK] no telhado"

10% das vezes → troca por uma palavra ALEATÓRIA
                "o gato subiu no telhado"  →  "o gato banana no telhado"

10% das vezes → mantém a palavra ORIGINAL
                "o gato subiu no telhado"  →  "o gato subiu no telhado"

Em TODOS os três casos, o modelo tem que prever "subiu" naquela posição.
```

### Por que essa complicação? (o raciocínio é bonito)

**Por que não mascarar 100% das vezes?**
Porque cria uma **discrepância entre treino e uso** (*train/test mismatch*): o token `[MASK]`
existe no pré-treino e **nunca** aparece quando você usa o modelo de verdade. O modelo
aprenderia "só preciso trabalhar direito nas posições marcadas com `[MASK]`" — e no
afinamento, sem nenhum `[MASK]`, essa habilidade não se transfere bem.

**Por que 10% com palavra aleatória?**
Para forçar o modelo a manter uma representação **de todos os tokens**, o tempo todo. Se ele
soubesse que tokens não mascarados estão sempre corretos, poderia simplesmente copiá-los. O
ruído aleatório o obriga a verificar cada token contra o contexto — o que é exatamente a
habilidade útil para detectar erro de digitação, OCR ruim e incoerência.

**Por que 10% mantendo o original?**
Para que o modelo tenha que produzir uma boa representação mesmo quando o token está certo,
já que ele não sabe distinguir esse caso do caso "aleatório".

**Por que 15% no total?**
Aqui a resposta honesta é: escolha empírica, sem derivação. O artigo não justifica. A
intuição é o equilíbrio entre sinal e destruição de contexto — pouco demais desperdiça
computação, muito demais deixa a tarefa impossível. Trabalhos posteriores (Wettig et al.,
2023, *"Should You Mask 15% in Masked Language Modeling?"*) mostraram que **40% funciona
melhor** em modelos maiores. Ou seja: era um chute razoável, e um chute subótimo.
**Parada legítima: convenção empírica, hoje sabidamente não ótima.**

### A perda

Só as posições mascaradas entram no cálculo. As demais recebem `-100` e são ignoradas:

$$\mathcal{L}_{\text{MLM}} = -\sum_{i \in M} \log P(x_i \mid x_{\setminus M})$$

Traduzindo: para cada posição escondida, o modelo produz uma distribuição de probabilidade
sobre as ~30 mil palavras do vocabulário, e a perda é o log negativo da probabilidade que ele
deu à palavra certa. Acertar com 90% de confiança custa pouco; acertar com 1% custa muito.

### O custo escondido do MLM

Só 15% dos tokens geram sinal de aprendizado. **85% do trabalho computacional é jogado fora.**
Esse foi o alvo do ELECTRA (2020), que substituiu o objetivo: em vez de adivinhar a máscara,
o modelo classifica **cada token** como "original" ou "substituído". Todos os tokens geram
sinal, e o ELECTRA atinge a qualidade do BERT com cerca de 1/4 do cálculo.

Por que o ELECTRA não virou o padrão, então? Opinião profissional: porque exige treinar dois
modelos juntos (um gerador e um discriminador), o que complica a receita, e porque em
2020 a comunidade já estava migrando para decoders. É um caso claro de tecnologia melhor que
perdeu por atrito de adoção e timing.

---

## 3 · NSP — Next Sentence Prediction (e por que morreu)

A segunda tarefa: dadas duas frases A e B, dizer se B **realmente** segue A no documento
original, ou se foi sorteada de outro lugar.

```
50% dos casos:  A = "O gato subiu no telhado."   B = "De lá, observou o quintal."   → IsNext
50% dos casos:  A = "O gato subiu no telhado."   B = "A taxa Selic caiu 0,5%."      → NotNext
```

A previsão sai do vetor do `[CLS]`. A motivação era razoável: QA e inferência textual são
tarefas de par, e um objetivo que ensine relação entre frases parecia útil.

**Por que foi descartada:**

1. **Fácil demais.** Distinguir uma continuação real de uma frase sorteada de outro documento
   quase sempre se resolve por **tópico** — vocabulário completamente diferente. O modelo
   aprendia "estas duas frases falam do mesmo assunto?", não coerência discursiva.
2. **Roubava capacidade.** O RoBERTa (2019) mostrou empiricamente que **remover** NSP melhora
   os resultados nas tarefas finais.
3. **Substituída por algo melhor.** O ALBERT trocou por **SOP** (*Sentence Order Prediction*):
   as duas frases são sempre consecutivas, e a tarefa é dizer se estão na ordem certa ou
   trocadas. Isso elimina o atalho de tópico e força coerência de verdade. Funcionou melhor.

**Lição transferível:** quando você projeta uma tarefa auto-supervisionada, pergunte-se
**qual é o atalho mais fácil para resolvê-la**. O modelo vai encontrar esse atalho. Se o
atalho for burro, o aprendizado será burro. Isso vale para qualquer tarefa proxy que você
inventar, inclusive fora de PLN.

Consequência prática hoje: o `token_type_ids` e o *pooler* continuam existindo no BERT por
compatibilidade, mas o pooler é aquele peso que aparece como `UNEXPECTED` quando você carrega
o modelo para outra tarefa — ver [04-como-comecar.md](04-como-comecar.md).

---

## 4 · Os dados do pré-treino

### BERT original (2018)

| Corpus | Palavras | Por que |
|---|---|---|
| BooksCorpus | 800 M | livros: texto longo, coerente, narrativo |
| Wikipédia em inglês | 2.500 M | texto expositivo, factual, limpo |
| **Total** | **3,3 bilhões** | |

A escolha por **documentos longos** em vez de frases soltas foi deliberada e importante: o
modelo precisa ver contexto contínuo para aprender dependências longas.

### Escala comparada — e como o campo mudou

| Modelo | Ano | Tokens de pré-treino | Contexto |
|---|---|---|---|
| BERT | 2018 | ~3,3 bilhões de palavras | 512 |
| RoBERTa | 2019 | ~30 bilhões | 512 |
| BERTimbau | 2019 | BrWaC (~2,7 bilhões de tokens em PT-BR) | 512 |
| ModernBERT | 2024 | **2 trilhões** | 8.192 |
| NeoBERT | 2025 | **2,1 trilhões** | 4.096 |
| mmBERT | 2025 | **3 trilhões** (1.800+ línguas) | 8.192 |

Três ordens de grandeza em seis anos, com o mesmo tamanho de modelo. É a demonstração mais
clara de que o BERT original estava **subtreinado** — a conclusão central do RoBERTa.

### O custo real

| | BERT-base (2018) | Refazer hoje (estimativa) |
|---|---|---|
| Hardware | 4 Cloud TPUs (16 chips), 4 dias | ~8 GPUs A100 por ~4 dias |
| Custo estimado | — | **US$ 2.000 a 10.000** |
| ModernBERT-base (2 T tokens) | — | ordem de **US$ 100 mil+** |

É por isso que você **não** pré-treina. Você baixa. O pré-treino é um bem público financiado
por quem tem escala, e usá-lo é o modelo econômico inteiro do campo.

---

## 5 · Os hiperparâmetros do pré-treino original

| Parâmetro | Valor | Comentário |
|---|---|---|
| Passos | 1.000.000 | ~40 épocas sobre o corpus |
| Lote | 256 sequências | 256 × 512 = 131.072 tokens por passo |
| Otimizador | Adam, `β₁=0,9`, `β₂=0,999` | padrão da época |
| Taxa de aprendizado | 1e-4, com warmup de 10.000 passos | pico, depois decaimento linear |
| Weight decay | 0,01 | |
| Dropout | 0,1 | em todas as camadas |
| Ativação | GELU | |
| Comprimento | 128 nos primeiros 90%, 512 nos últimos 10% | **truque de custo**: o quadrático só entra no fim |

Aquele último item é engenharia esperta que quase ninguém nota: treinar 90% do tempo com
sequências curtas e só depois estender economiza uma fortuna, porque o custo da atenção é
quadrático no comprimento.

---

## 6 · Pré-treino contínuo: o que você *pode* fazer

Você não vai pré-treinar do zero, mas **continuar** o pré-treino no seu domínio é acessível e
frequentemente lucrativo. O nome no campo é *domain-adaptive pretraining* (DAPT), do artigo
"Don't Stop Pretraining" (Gururangan et al., 2020).

```
BERT genérico → [MLM contínuo no seu texto cru] → BERT do seu domínio → [afinar] → modelo final
   (grátis)          (horas de GPU, sem rótulo)                          (minutos)
```

| Quando compensa | Quando não compensa |
|---|---|
| jargão pesado (jurídico, médico, industrial) | texto comum, notícias, conversa de cliente |
| você tem **muito** texto cru do domínio (dezenas de MB+) | poucos documentos |
| a fertilidade do tokenizador é alta no seu texto | tokenização já é boa |
| a tarefa final tem poucos rótulos | você tem 100 mil exemplos rotulados |

Ganho típico relatado: 1 a 5 pontos de F1 na tarefa final. Código funcional em
[06-exemplos.md, exemplo 11](06-exemplos.md#11--produção-2-adaptação-ao-domínio-com-mlm-contínuo).

Modelos que nasceram assim e viraram padrão nos seus nichos: **BioBERT** (artigos do PubMed),
**SciBERT** (papers), **LegalBERT** (jurisprudência), **FinBERT** (relatórios financeiros).
Antes de treinar o seu, procure no Hub — pode já existir.

---

## 7 · Máscara estática × dinâmica

Detalhe de implementação que virou padrão e vale entender:

- **BERT original (estática):** o mascaramento foi feito **uma vez**, no pré-processamento.
  Cada frase era duplicada 10 vezes com máscaras diferentes, mas ao longo de 40 épocas o
  modelo via cada padrão 4 vezes.
- **RoBERTa (dinâmica):** a máscara é sorteada **na hora**, a cada vez que a frase aparece.
  Nenhum padrão se repete.

A dinâmica é melhor (mais variedade, menos memorização) e é praticamente de graça. Virou
padrão. Na prática, é o que o `DataCollatorForLanguageModeling` do `transformers` faz.

---

## 8 · Por que isso tudo funciona? (a pergunta profunda)

Por que resolver "adivinhe a palavra escondida" produz representações úteis para classificar
sentimento, extrair entidades e medir similaridade?

**A hipótese distribucional**, formulada pelo linguista J. R. Firth em 1957:

> *"You shall know a word by the company it keeps."*
> (Você conhecerá uma palavra pelas companhias que ela mantém.)

Se duas palavras aparecem nos mesmos contextos, elas têm significados relacionados. O MLM é
a versão levada ao extremo dessa ideia: para prever a palavra escondida com boa precisão, é
preciso modelar quase tudo que determina qual palavra cabe ali — sintaxe, semântica,
correferência, fatos sobre o mundo, registro, e até a intenção do autor.

**Continuando a pergunta:** por que a hipótese distribucional é verdadeira?
Porque a linguagem é um sistema de comunicação sob pressão de eficiência: palavras com usos
distintos precisam ocorrer em ambientes distintos, senão a comunicação falharia. O contexto
carrega a informação porque é *função* dele carregá-la.

Chegamos a uma parada legítima — mas cabe honestidade: **a explicação completa de por que o
MLM em escala produz representações tão gerais ainda é um problema em aberto**. Existem
resultados parciais (ver [60-teoria-avancada.md](60-teoria-avancada.md)), mas a teoria está
atrás da prática. Quem disser que sabe exatamente por que funciona está exagerando.

---

## Autoteste

1. Por que o pré-treino é chamado de auto-supervisionado, e onde está o "rótulo"?
2. Explique a regra 80/10/10. Qual problema cada uma das três fatias resolve?
3. Por que mascarar 100% das vezes seria pior, se a tarefa é adivinhar a máscara?
4. De onde vem o número 15%, e o que trabalhos posteriores descobriram?
5. Que fração do cálculo do MLM é desperdiçada, e como o ELECTRA resolveu isso?
6. Por que a tarefa NSP foi descartada? Qual era o atalho que o modelo usava?
7. Qual é a lição transferível sobre projetar tarefas auto-supervisionadas?
8. Quantos tokens o BERT viu no pré-treino, e quantos o ModernBERT? O que essa diferença prova?
9. Por que o BERT foi treinado com 128 tokens em 90% dos passos?
10. Quando vale a pena fazer MLM contínuo no seu domínio, e quando é desperdício?
11. O que é a hipótese distribucional, e por que ela é verdadeira?

---

## Fontes

- Devlin et al. (2019). *BERT*. Seções 3.1 e Apêndice A. [aclanthology.org/N19-1423](https://aclanthology.org/N19-1423/)
- Liu et al. (2019). *RoBERTa*. [arXiv:1907.11692](https://arxiv.org/abs/1907.11692)
- Clark et al. (2020). *ELECTRA*. [arXiv:2003.10555](https://arxiv.org/abs/2003.10555)
- Lan et al. (2019). *ALBERT* (SOP). [arXiv:1909.11942](https://arxiv.org/abs/1909.11942)
- Gururangan et al. (2020). *Don't Stop Pretraining*. [arXiv:2004.10964](https://arxiv.org/abs/2004.10964)
- Wettig et al. (2023). *Should You Mask 15% in Masked Language Modeling?* [arXiv:2202.08005](https://arxiv.org/abs/2202.08005)
- Firth, J. R. (1957). *A synopsis of linguistic theory 1930–1955*.

---

*Anterior: [13-arquitetura-encoder.md](13-arquitetura-encoder.md) · Próximo: [15-fine-tuning.md](15-fine-tuning.md)*
