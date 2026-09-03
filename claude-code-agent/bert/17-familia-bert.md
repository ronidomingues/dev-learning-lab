# 17 · A família BERT — qual variante usar e por quê

`Nível: intermediário` · `Última atualização: 12/08/2026`

Existem milhares de modelos "tipo BERT" no Hugging Face Hub. Este arquivo é o mapa: o que cada
linhagem mudou, o que isso te dá, e qual escolher para o seu caso.

---

## 1 · A árvore genealógica

```
                        Transformer (2017)
                               │
                    ┌──────────┴──────────┐
                 ENCODER                DECODER
                    │                      │
                 BERT (2018)            GPT (2018) ──► LLMs de hoje
                    │
     ┌──────┬───────┼────────┬────────┬─────────┬──────────┐
     │      │       │        │        │         │          │
 RoBERTa ALBERT DistilBERT ELECTRA DeBERTa   XLM-R    domínio/língua
  (2019)  (2019)  (2019)   (2020)  (2020)   (2019)    (BioBERT, BERTimbau…)
     │                                │
     └────────────┬───────────────────┘
                  │
           ModernBERT (2024) ──► NeoBERT, mmBERT, EuroBERT (2025)
```

---

## 2 · As melhorias, por eixo

Toda variante mexe em um destes cinco eixos. Entender o eixo é mais útil que decorar nomes.

| Eixo | Quem atacou | Como | Resultado |
|---|---|---|---|
| **Treinar melhor** | RoBERTa | 10× mais dados, mais tempo, sem NSP, máscara dinâmica | +2 a 4 pontos de GLUE, mesma arquitetura |
| **Ficar menor** | DistilBERT, ALBERT, MiniLM | destilação, compartilhamento de pesos, fatoração | 40–90% menor, perda pequena |
| **Objetivo melhor** | ELECTRA | detectar token trocado em vez de adivinhar máscara | 4× mais eficiente por FLOP |
| **Posição melhor** | DeBERTa, ModernBERT | atenção desemaranhada; RoPE | +1 a 3 pontos, extrapola comprimento |
| **Contexto maior** | Longformer, BigBird, ModernBERT | atenção esparsa/local, Flash Attention | 512 → 4.096 → 8.192 tokens |

---

## 3 · Tabela de decisão — qual usar em agosto de 2026

| Se você... | Use | Parâmetros | Licença |
|---|---|---|---|
| trabalha em **português** | `neuralmind/bert-base-portuguese-cased` | 110 M | MIT |
| precisa de mais qualidade em PT e aguenta o custo | `neuralmind/bert-large-portuguese-cased` | 335 M | MIT |
| trabalha em **inglês**, projeto novo | `answerdotai/ModernBERT-base` | 149 M | Apache 2.0 |
| precisa de **muitas línguas** | `jhu-clsp/mmBERT-base` ou `FacebookAI/xlm-roberta-base` | 307 M / 278 M | MIT / MIT |
| precisa que caiba em CPU fraca | `distilbert-base-multilingual-cased` | 135 M | Apache 2.0 |
| precisa de **texto longo** (> 512 tokens) | `answerdotai/ModernBERT-base` | 149 M | Apache 2.0 |
| quer **embeddings/busca** | `sentence-transformers/*` ou `BAAI/bge-m3` | varia | Apache 2.0/MIT |
| quer o **melhor** em benchmark de compreensão em inglês | `microsoft/deberta-v3-large` | 435 M | MIT |
| está reproduzindo um paper antigo | `bert-base-uncased` | 110 M | Apache 2.0 |
| trabalha em domínio biomédico | BioBERT, PubMedBERT, ClinicalBERT | 110 M | varia |

> **Sempre confira a licença no model card antes de usar comercialmente.** A maioria é
> permissiva (MIT/Apache 2.0), mas há exceções com cláusula não-comercial, e o custo de
> descobrir isso depois é alto. Ver [80-custos-e-licencas.md](80-custos-e-licencas.md).

---

## 4 · As variantes, uma a uma

### RoBERTa (Meta, 2019) — "o BERT foi mal treinado"

Mesma arquitetura. Mudou o treino: 160 GB de texto (contra 16 GB), lotes de 8.000 (contra
256), máscara dinâmica, **sem NSP**, tokenizador byte-BPE (nunca produz `[UNK]`).

**Quando usar:** em inglês, ainda é uma escolha sólida e muito bem suportada.
**Pegadinha:** usa `<mask>`, não `[MASK]`; não tem `token_type_ids`.

### DistilBERT (Hugging Face, 2019) — o professor e o aluno

**Destilação de conhecimento**: um modelo pequeno (6 camadas) é treinado para imitar as
*distribuições de saída* do modelo grande (12 camadas), não só os rótulos certos.

**Por que imitar a distribuição funciona melhor que treinar do zero?** Porque a distribuição
do professor carrega "conhecimento escuro": ao classificar um gato, o professor dá 0,9 para
gato, 0,08 para lince e 0,001 para caminhão. Essa ordenação relativa entre as classes erradas
ensina a estrutura do problema, e o rótulo puro (1 para gato, 0 para todo o resto) esconde.

Resultado: 40% menor, 60% mais rápido, ~97% da qualidade.
**Quando usar:** produção com restrição de latência ou custo; primeira parada quando o
BERT-base é lento demais.

### ALBERT (Google, 2019) — menor, não mais rápido

Dois truques: (1) **fatoração dos embeddings** — em vez de `30.000 × 768`, faz
`30.000 × 128` e `128 × 768`; (2) **compartilhamento de parâmetros entre camadas** — todas as
12 camadas usam **os mesmos pesos**.

ALBERT-base tem 12 M de parâmetros contra 110 M do BERT. Mas atenção à armadilha:
**ele não é mais rápido**. As 12 camadas ainda são executadas; só ocupam menos memória.
Muita gente escolhe ALBERT esperando velocidade e se decepciona.

### ELECTRA (Google, 2020) — o objetivo mais eficiente

Um gerador pequeno substitui tokens; o discriminador (o modelo que você fica) classifica cada
token como original ou substituído. **Todos** os tokens geram sinal, não só 15%.

ELECTRA-small alcança qualidade comparável ao BERT-base com cerca de 1/4 do cálculo de
pré-treino. Tecnicamente superior; perdeu por adoção e timing.

### DeBERTa (Microsoft, 2020) — atenção desemaranhada

Separa a representação de **conteúdo** e de **posição** e calcula a atenção entre os quatro
pares (conteúdo-conteúdo, conteúdo-posição, etc.). Acrescenta um decodificador de máscara com
posições absolutas.

Foi o primeiro modelo a superar o desempenho humano no SuperGLUE, e o `deberta-v3-large`
ainda é referência em tarefas de classificação em inglês em 2026. **Custo:** mais lento que
um BERT do mesmo tamanho.

### XLM-RoBERTa (Meta, 2019) — 100 línguas

RoBERTa treinado em 2,5 TB de CommonCrawl filtrado, 100 línguas, vocabulário SentencePiece de
250 mil.

O achado importante: a **transferência entre línguas** funciona. Você pode afinar em inglês
(onde há dados rotulados) e o modelo funciona razoavelmente em português (onde não há). Isso
resolve muitos problemas práticos em línguas de poucos recursos.

**Trade-off honesto:** um modelo específico da língua (BERTimbau) costuma ganhar do XLM-R em
português puro, porque não divide capacidade com outras 99 línguas — a chamada "maldição da
multilingualidade".

### BERTimbau (NeuralMind/Unicamp, 2019) — o BERT brasileiro

BERT treinado do zero em **BrWaC** (Brazilian Web as Corpus), 1 milhão de passos, com
mascaramento de palavra inteira. É estado da arte em NER, similaridade textual e implicação
para PT-BR entre os modelos abertos dessa geração. Licença MIT.

**É o padrão para português neste curso**, e a recomendação para a maioria dos projetos em
PT-BR: o vocabulário tem tokens brasileiros de verdade (Petrobras, Localiza são um token só —
ver [12-tokenizacao-wordpiece.md](12-tokenizacao-wordpiece.md)).

Limitação real: corpus até ~2019. Nada posterior existe no seu vocabulário.

### ModernBERT (Answer.AI + LightOn, dez/2024) — o sucessor

Seis anos de avanços de LLM aplicados ao encoder:

| Mudança | Efeito |
|---|---|
| RoPE (posições rotacionais) | contexto de 8.192, com extrapolação |
| Atenção local/global alternada | custo aceitável em sequência longa |
| Flash Attention + unpadding | mais rápido que o BERT mesmo com 16× mais contexto |
| Sem viés nas camadas lineares, pre-LN | treino mais estável |
| 2 trilhões de tokens, incluindo **código** | muito melhor em texto técnico e recuperação de código |
| GeGLU no lugar da FFN clássica | pequeno ganho de qualidade |

Tamanhos: base (149 M) e large (395 M). Apache 2.0. Requer `transformers` ≥ 4.48.

**Limitação para o leitor brasileiro:** treinado em **inglês e código**. Para português, não
substitui o BERTimbau. Para PT, prefira mmBERT ou espere/procure um ModernBERT em português.

### NeoBERT e mmBERT (2025)

- **NeoBERT** — 250 M, 2,1 trilhões de tokens, contexto 4.096, razão profundidade/largura
  otimizada. Estado da arte em MTEB entre modelos do seu porte, sob afinamento idêntico.
- **mmBERT** — ModernBERT multilíngue: 1.833 línguas, 3 trilhões de tokens, vocabulário de
  256 mil do tokenizador do Gemma 2, currículo de "annealed language learning" que introduz
  línguas progressivamente. Ganhos de 8 a 15 pontos em línguas de poucos recursos.
  **É o candidato mais interessante para português em 2026** — meça contra o BERTimbau no
  seu caso antes de decidir.

---

## 5 · Como escolher, na prática (o processo, não a tabela)

Ordem que eu sigo, e recomendo:

1. **Sua língua tem um modelo próprio bom?** Se sim, é o primeiro candidato.
2. **Seu domínio tem um modelo próprio?** (BioBERT, LegalBERT, FinBERT.) Procure no Hub antes
   de treinar qualquer coisa.
3. **Meça a fertilidade do tokenizador** nos seus termos — 2 minutos, e prevê bem o resultado
   ([12-tokenizacao-wordpiece.md](12-tokenizacao-wordpiece.md#testando-o-seu-domínio-antes-de-escolher-o-modelo)).
4. **Afine 2 ou 3 candidatos** nos seus dados e compare com a sua métrica. Isso custa uma
   tarde e vale mais que qualquer leaderboard.
5. **Só então** pense em tamanho e latência: o menor modelo que atinge a qualidade necessária.

**O que não fazer:** escolher pelo topo do MTEB ou do GLUE. Esses placares medem médias em
tarefas em inglês que provavelmente não se parecem com a sua.

---

## 6 · Tabela comparativa de custo

Valores aproximados para inferência de um texto curto (~50 tokens), CPU moderna, `float32`.
Use como ordem de grandeza, não como medição precisa.

| Modelo | Parâmetros | Disco | Latência relativa | Qualidade relativa |
|---|---|---|---|---|
| MiniLM-L6 | 22 M | 90 MB | 0,2× | 0,90 |
| DistilBERT | 66 M | 265 MB | 0,4× | 0,97 |
| ALBERT-base | 12 M | 45 MB | 1,0× | 0,97 |
| **BERT-base** | 110 M | 440 MB | **1,0×** | **1,00** (referência) |
| ModernBERT-base | 149 M | 600 MB | 0,7× | 1,05 |
| DeBERTa-v3-base | 184 M | 740 MB | 1,6× | 1,06 |
| BERT-large | 340 M | 1,3 GB | 3,2× | 1,03 |

Duas leituras que importam:

- **BERT-large raramente compensa.** 3× o custo por ~3% de qualidade. ModernBERT-base é
  melhor e mais rápido que BERT-large em inglês.
- **ALBERT ocupa 10× menos disco e não é mais rápido** — a armadilha citada acima.

---

## Autoteste

1. Quais são os cinco eixos de melhoria da família BERT? Dê um representante de cada.
2. O que o RoBERTa mudou em relação ao BERT, e o que isso provou?
3. Por que a destilação (DistilBERT) funciona melhor que treinar um modelo pequeno do zero?
4. Por que o ALBERT é 10× menor mas não mais rápido?
5. Qual é o truque do ELECTRA e por que ele é mais eficiente por FLOP?
6. O que é a "maldição da multilingualidade", e quando um modelo específico da língua ganha?
7. Cite três mudanças do ModernBERT em relação ao BERT e o efeito de cada uma.
8. Para um projeto novo em português em 2026, quais são os dois candidatos, e como você decidiria?
9. Por que escolher modelo pelo topo do MTEB é má ideia?
10. Quando BERT-large compensa?

---

## Fontes

- Liu et al. (2019). *RoBERTa*. [arXiv:1907.11692](https://arxiv.org/abs/1907.11692)
- Sanh et al. (2019). *DistilBERT*. [arXiv:1910.01108](https://arxiv.org/abs/1910.01108)
- Lan et al. (2019). *ALBERT*. [arXiv:1909.11942](https://arxiv.org/abs/1909.11942)
- Clark et al. (2020). *ELECTRA*. [arXiv:2003.10555](https://arxiv.org/abs/2003.10555)
- He et al. (2021). *DeBERTa*. [arXiv:2006.03654](https://arxiv.org/abs/2006.03654)
- Conneau et al. (2020). *XLM-R*. [arXiv:1911.02116](https://arxiv.org/abs/1911.02116)
- Souza et al. (2020). *BERTimbau*. [huggingface.co/neuralmind](https://huggingface.co/neuralmind/bert-base-portuguese-cased)
- Warner et al. (2024). *ModernBERT*. [huggingface.co/answerdotai/ModernBERT-base](https://huggingface.co/answerdotai/ModernBERT-base)
- Le Breton et al. (2025). *NeoBERT*. [arXiv:2502.19587](https://arxiv.org/abs/2502.19587)
- Marone et al. (2025). *mmBERT*. [github.com/jhu-clsp/mmBERT](https://github.com/jhu-clsp/mmBERT)

*Consulta feita em 12/08/2026.*

---

*Anterior: [16-embeddings-e-busca-semantica.md](16-embeddings-e-busca-semantica.md) · Próximo: [18-avaliacao-e-benchmarks.md](18-avaliacao-e-benchmarks.md)*
