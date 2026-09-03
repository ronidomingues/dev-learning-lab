# 95 · Referências — papers, documentação, código e pessoas

`Nível: todos` · `Verificado em 12/08/2026`

Fontes primárias. Tudo aqui é verificável; nenhum link foi inventado.

---

## 1 · Os papers que você precisa ler

Em ordem de importância, não cronológica. Os cinco primeiros são o núcleo.

| # | Paper | Ano | Por que ler |
|---|---|---|---|
| 1 | [**Attention Is All You Need**](https://arxiv.org/abs/1706.03762) — Vaswani et al. | 2017 | a arquitetura. Curto, denso, ainda legível |
| 2 | [**BERT: Pre-training of Deep Bidirectional Transformers**](https://aclanthology.org/N19-1423/) — Devlin, Chang, Lee & Toutanova | 2019 | o modelo. Leia inclusive o Apêndice A (hiperparâmetros) |
| 3 | [**RoBERTa**](https://arxiv.org/abs/1907.11692) — Liu et al. | 2019 | o estudo de replicação que mostrou que o BERT estava subtreinado |
| 4 | [**Sentence-BERT**](https://arxiv.org/abs/1908.10084) — Reimers & Gurevych | 2019 | a base de toda busca semântica e RAG |
| 5 | [**A Primer in BERTology**](https://arxiv.org/abs/2002.12327) — Rogers, Kovaleva & Rumshisky | 2020 | resumo de tudo que se descobriu sobre o que o BERT aprende |

### Arquitetura e pré-treino

- [ELMo — *Deep Contextualized Word Representations*](https://arxiv.org/abs/1802.05365) · Peters et al., 2018
- [GPT-1 — *Improving Language Understanding by Generative Pre-Training*](https://cdn.openai.com/research-covers/language-unsupervised/language_understanding_paper.pdf) · Radford et al., 2018
- [ALBERT](https://arxiv.org/abs/1909.11942) · Lan et al., 2019
- [DistilBERT](https://arxiv.org/abs/1910.01108) · Sanh et al., 2019
- [ELECTRA](https://arxiv.org/abs/2003.10555) · Clark et al., 2020
- [DeBERTa](https://arxiv.org/abs/2006.03654) · He et al., 2021
- [XLM-R](https://arxiv.org/abs/1911.02116) · Conneau et al., 2020
- [*Should You Mask 15% in Masked Language Modeling?*](https://arxiv.org/abs/2202.08005) · Wettig et al., 2023 — a resposta: não, 40% é melhor
- [*Don't Stop Pretraining*](https://arxiv.org/abs/2004.10964) · Gururangan et al., 2020 — adaptação de domínio

### A geração moderna (2024–2026)

- [**ModernBERT**](https://www.answer.ai/posts/2024-12-19-modernbert.html) · Warner et al., dez/2024 · [modelo](https://huggingface.co/answerdotai/ModernBERT-base)
- [**NeoBERT**](https://arxiv.org/abs/2502.19587) · Le Breton et al., fev/2025
- [**mmBERT**](https://arxiv.org/html/2509.06888v1) · Marone et al., set/2025 · [código](https://github.com/jhu-clsp/mmBERT)
- [**moBERTo — encoder moderno para português**](https://arxiv.org/abs/2606.22722) · Laitz, Sales Almeida, Alves Santos & Bonás, 21/06/2026 · pesos: `Tropic-AI/moBERTo`
- [*ModernBERT or DeBERTaV3?*](https://arxiv.org/pdf/2504.08716) · 2025 — arquitetura versus dados
- [*Return of the Encoder*](https://arxiv.org/pdf/2501.16273) · 2025 — eficiência de parâmetro em modelos pequenos
- [*Cost-Aware Model Selection for Text Classification*](https://arxiv.org/html/2602.06370v1) · 2026 — encoder afinado versus prompting de LLM, com custo medido

### Interpretabilidade

- [*BERT Rediscovers the Classical NLP Pipeline*](https://arxiv.org/abs/1905.05950) · Tenney et al., 2019
- [*What Does BERT Look At?*](https://arxiv.org/abs/1906.04341) · Clark et al., 2019
- [*Are Sixteen Heads Really Better than One?*](https://arxiv.org/abs/1905.10650) · Michel et al., 2019
- [*A Structural Probe for Finding Syntax*](https://aclanthology.org/N19-1419/) · Hewitt & Manning, 2019
- [*Designing and Interpreting Probes with Control Tasks*](https://arxiv.org/abs/1909.03368) · Hewitt & Liang, 2019
- [*Attention is not Explanation*](https://arxiv.org/abs/1902.10186) · Jain & Wallace, 2019
- [*Attention is not not Explanation*](https://arxiv.org/abs/1908.04626) · Wiegreffe & Pinter, 2019
- [*Right for the Wrong Reasons* (HANS)](https://arxiv.org/abs/1902.01007) · McCoy et al., 2019
- [*Transformer Feed-Forward Layers Are Key-Value Memories*](https://arxiv.org/abs/2012.14913) · Geva et al., 2021

### Teoria e limites

- [*Theoretical Limitations of Self-Attention*](https://arxiv.org/abs/1906.06755) · Hahn, 2020
- [*On the Turing Completeness of Modern Neural Network Architectures*](https://arxiv.org/abs/1901.03429) · Pérez et al., 2019
- [*The Parallelism Tradeoff: Limitations of Log-Precision Transformers*](https://arxiv.org/abs/2207.00729) · Merrill & Sabharwal, 2023
- [*On the Computational Complexity of Self-Attention*](https://arxiv.org/abs/2209.04881) · Keles et al., 2022
- [*FlashAttention*](https://arxiv.org/abs/2205.14135) · Dao et al., 2022
- [*On Layer Normalization in the Transformer Architecture*](https://arxiv.org/abs/2002.04745) · Xiong et al., 2020
- [*Decoupled Weight Decay Regularization* (AdamW)](https://arxiv.org/abs/1711.05101) · Loshchilov & Hutter, 2019
- [*Masked Language Model Scoring*](https://arxiv.org/abs/1910.14659) · Salazar et al., 2020
- [*How Contextual are Contextualized Word Representations?*](https://arxiv.org/abs/1909.00512) · Ethayarajh, 2019
- [*Understanding Contrastive Representation Learning*](https://arxiv.org/abs/2005.10242) · Wang & Isola, 2020
- [*Training Compute-Optimal LLMs* (Chinchilla)](https://arxiv.org/abs/2203.15556) · Hoffmann et al., 2022

### Avaliação e prática

- [GLUE](https://arxiv.org/abs/1804.07461) · Wang et al., 2018
- [SQuAD](https://rajpurkar.github.io/SQuAD-explorer/) · Rajpurkar et al., 2016/2018
- [MTEB](https://arxiv.org/abs/2210.07316) · Muennighoff et al., 2022 · [placar](https://huggingface.co/spaces/mteb/leaderboard)
- [*On Calibration of Modern Neural Networks*](https://arxiv.org/abs/1706.04599) · Guo et al., 2017
- [*Fine-Tuning Pretrained Language Models*](https://arxiv.org/abs/2002.06305) · Dodge et al., 2020 — a instabilidade entre sementes
- [*How to Fine-Tune BERT for Text Classification?*](https://arxiv.org/abs/1905.05583) · Sun et al., 2019
- [*Distilling the Knowledge in a Neural Network*](https://arxiv.org/abs/1503.02531) · Hinton, Vinyals & Dean, 2015

### Português

- [**BERTimbau**](https://github.com/neuralmind-ai/portuguese-bert) · Souza, Nogueira & Lotufo, 2020 · [modelo](https://huggingface.co/neuralmind/bert-base-portuguese-cased)
- [**ASSIN 2**](https://sites.google.com/view/assin2) — similaridade e implicação em português
- [**BrWaC**](https://www.inf.ufrgs.br/pln/wiki/index.php?title=BrWaC) — o corpus em que o BERTimbau foi treinado

---

## 2 · Documentação oficial

| Recurso | Link | Para quê |
|---|---|---|
| **transformers** | [huggingface.co/docs/transformers](https://huggingface.co/docs/transformers) | referência da API |
| **Guia de migração v5** | [MIGRATION_GUIDE_V5.md](https://github.com/huggingface/transformers/blob/main/MIGRATION_GUIDE_V5.md) | o que mudou da v4 |
| **datasets** | [huggingface.co/docs/datasets](https://huggingface.co/docs/datasets) | carregar e transformar dados |
| **tokenizers** | [huggingface.co/docs/tokenizers](https://huggingface.co/docs/tokenizers) | tokenização em Rust |
| **sentence-transformers** | [sbert.net](https://sbert.net/) | embeddings e busca |
| **PEFT / LoRA** | [huggingface.co/docs/peft](https://huggingface.co/docs/peft) | afinamento eficiente |
| **Optimum** | [huggingface.co/docs/optimum](https://huggingface.co/docs/optimum) | ONNX, quantização |
| **accelerate** | [huggingface.co/docs/accelerate](https://huggingface.co/docs/accelerate) | treino distribuído |
| **PyTorch** | [pytorch.org/docs](https://pytorch.org/docs/stable/index.html) | o motor |
| **scikit-learn — avaliação** | [scikit-learn.org/stable/modules/model_evaluation.html](https://scikit-learn.org/stable/modules/model_evaluation.html) | métricas |

---

## 3 · Código-fonte que vale ler

Ler implementação é a melhor forma de fechar a lacuna entre paper e prática.

| Repositório | Por que ler |
|---|---|
| [google-research/bert](https://github.com/google-research/bert) | a implementação original, em TensorFlow 1.x. Histórica, mas é a fonte |
| [huggingface/transformers — `modeling_bert.py`](https://github.com/huggingface/transformers/blob/main/src/transformers/models/bert/modeling_bert.py) | a implementação que você realmente usa. **Leia esta** |
| [huggingface/transformers — `modeling_modernbert.py`](https://github.com/huggingface/transformers/blob/main/src/transformers/models/modernbert/modeling_modernbert.py) | compare com a de cima e veja 6 anos de evolução |
| [karpathy/minGPT](https://github.com/karpathy/minGPT) | ~300 linhas, um Transformer inteiro. Didático como poucos |
| [rasbt/LLMs-from-scratch](https://github.com/rasbt/LLMs-from-scratch) | do zero, comentado, em PyTorch |
| [UKPLab/sentence-transformers](https://github.com/UKPLab/sentence-transformers) | como o treino siamês é implementado de verdade |
| [neuralmind-ai/portuguese-bert](https://github.com/neuralmind-ai/portuguese-bert) | como se pré-treina um BERT para uma língua |
| [jhu-clsp/mmBERT](https://github.com/jhu-clsp/mmBERT) | receita moderna e completa de pré-treino multilíngue |

**Sugestão concreta:** abra o `modeling_bert.py` e procure a classe `BertSelfAttention`.
Compare com a implementação de [13-arquitetura-encoder.md](13-arquitetura-encoder.md). São
a mesma coisa, com nomes diferentes e otimizações.

---

## 4 · Modelos de referência no Hub

| Modelo | Uso |
|---|---|
| [`neuralmind/bert-base-portuguese-cased`](https://huggingface.co/neuralmind/bert-base-portuguese-cased) | português, padrão deste curso |
| [`neuralmind/bert-large-portuguese-cased`](https://huggingface.co/neuralmind/bert-large-portuguese-cased) | português, maior |
| [`answerdotai/ModernBERT-base`](https://huggingface.co/answerdotai/ModernBERT-base) | inglês, geração atual |
| [`jhu-clsp/mmBERT-base`](https://huggingface.co/jhu-clsp/mmBERT-base) | multilíngue moderno |
| [`FacebookAI/xlm-roberta-base`](https://huggingface.co/FacebookAI/xlm-roberta-base) | multilíngue clássico |
| [`distilbert-base-multilingual-cased`](https://huggingface.co/distilbert-base-multilingual-cased) | pequeno e rápido |
| [`microsoft/deberta-v3-large`](https://huggingface.co/microsoft/deberta-v3-large) | topo em classificação em inglês |
| [`sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`](https://huggingface.co/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2) | embeddings multilíngues |
| [`Babelscape/wikineural-multilingual-ner`](https://huggingface.co/Babelscape/wikineural-multilingual-ner) | NER multilíngue |
| [`pierreguillou/bert-base-cased-squad-v1.1-portuguese`](https://huggingface.co/pierreguillou/bert-base-cased-squad-v1.1-portuguese) | QA extrativo em português |

---

## 5 · Pessoas para acompanhar

Não como celebridades — como fontes cujo trabalho define a direção do campo.

| Pessoa | Por quê |
|---|---|
| **Jacob Devlin** | autor principal do BERT |
| **Ashish Vaswani** e coautores | autores do Transformer |
| **Thomas Wolf**, **Lewis Tunstall**, **Leandro von Werra** | Hugging Face; livro e biblioteca |
| **Nils Reimers** | Sentence-BERT; referência em recuperação |
| **Sebastian Raschka** | didática de ML e LLM, com material aberto |
| **Jeremy Howard** | fast.ai e Answer.AI (ModernBERT) |
| **Anna Rogers** | *A Primer in BERTology*; crítica metodológica da área |
| **Andrej Karpathy** | didática de arquitetura, minGPT, vídeos |
| **Rodrigo Nogueira**, **Roberto Lotufo** (Unicamp/NeuralMind) | BERTimbau e PLN em português |

---

## 6 · Onde acompanhar o campo

| Fonte | O que traz |
|---|---|
| [arXiv cs.CL](https://arxiv.org/list/cs.CL/recent) | tudo, cru e em tempo real |
| [Hugging Face Papers](https://huggingface.co/papers) | curadoria diária com discussão |
| [ACL Anthology](https://aclanthology.org/) | papers das conferências da área (ACL, EMNLP, NAACL) |
| [Hugging Face Blog](https://huggingface.co/blog) | anúncios e tutoriais de qualidade |
| [Answer.AI](https://www.answer.ai/) | origem do ModernBERT |
| [Papers With Code](https://paperswithcode.com/) | paper + implementação juntos |
| [MTEB Leaderboard](https://huggingface.co/spaces/mteb/leaderboard) | estado da arte em embeddings |

**Conferências que importam:** ACL, EMNLP, NAACL (PLN); NeurIPS, ICML, ICLR (aprendizado de
máquina em geral). Os anais de todas são abertos.

---

## 7 · Ferramentas mencionadas neste curso

| Ferramenta | Para quê | Link |
|---|---|---|
| **doccano**, **Label Studio** | anotar dados | [doccano](https://github.com/doccano/doccano) · [Label Studio](https://labelstud.io/) |
| **FAISS** | índice vetorial local | [github.com/facebookresearch/faiss](https://github.com/facebookresearch/faiss) |
| **pgvector** | vetores no PostgreSQL | [github.com/pgvector/pgvector](https://github.com/pgvector/pgvector) |
| **ONNX Runtime** | inferência otimizada | [onnxruntime.ai](https://onnxruntime.ai/) |
| **rank_bm25** | busca lexical em Python | [github.com/dorianbrown/rank_bm25](https://github.com/dorianbrown/rank_bm25) |
| **MLflow** | rastrear experimentos | [mlflow.org](https://mlflow.org/) |
| **uv** | gerenciar Python e dependências | [github.com/astral-sh/uv](https://github.com/astral-sh/uv) |

---

## Autoteste

1. Quais são os cinco papers do núcleo, e o que cada um contribuiu?
2. Qual arquivo de código você abriria para ver a implementação real da atenção do BERT?
3. Onde acompanhar o estado da arte em embeddings?
4. Qual paper mostrou que 15% de mascaramento não era o ótimo?
5. Qual é a novidade de 2026 em encoders para português, e onde estão os pesos?
6. Quais duas referências deste arquivo tratam da instabilidade do afinamento e da calibração?

---

*Anterior: [90-bibliografia.md](90-bibliografia.md) · Próximo: [GLOSSARIO.md](GLOSSARIO.md)*
