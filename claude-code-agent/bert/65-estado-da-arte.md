# 65 · Estado da arte — onde os encoders estão em agosto de 2026

`Nível: avançado` · `Pesquisa na web feita em 12/08/2026` ·
`Este arquivo envelhece rápido. Reveja a cada 6 meses.`

---

## Resumo em cinco frases

1. Encoders passaram por um **renascimento** entre dezembro de 2024 e 2026, depois de seis
   anos de estagnação.
2. **ModernBERT** (2024) é o novo padrão em inglês; **mmBERT** (2025) em multilíngue;
   **moBERTo** (junho de 2026) é a novidade em português.
3. A divisão de trabalho com LLMs se consolidou: encoders para tarefas fechadas e de alto
   volume, LLMs para tarefas abertas e de baixo volume.
4. O argumento decisivo virou **custo e energia**, não qualidade: a diferença é de uma a duas
   ordens de grandeza, com literatura recente medindo isso de forma sistemática.
5. O padrão emergente é **híbrido**: LLM rotula ou decide o caso difícil, encoder serve o
   volume.

---

## 1 · A linha do tempo do renascimento

| Data | Modelo | O que trouxe |
|---|---|---|
| dez/2024 | **ModernBERT** (Answer.AI + LightOn) | RoPE, atenção local/global, Flash Attention, 8.192 tokens, 2 T tokens de treino, código no corpus. Base 149 M / large 395 M. Apache 2.0 |
| fev/2025 | **NeoBERT** | 250 M, 2,1 T tokens, contexto 4.096, razão profundidade/largura otimizada, Pre-RMSNorm. Forte em MTEB para o porte |
| mar/2025 | **EuroBERT** | encoders multilíngues para línguas europeias, 210 M a 2,1 B. Bom em recuperação de código |
| set/2025 | **mmBERT** | ModernBERT multilíngue: 1.833 línguas, 3 T tokens, tokenizador do Gemma 2 (256 mil), currículo de introdução progressiva de línguas |
| 2025–2026 | Adaptações nacionais | TabiBERT (turco), encoders modernos para letão, e outros — o padrão "continuar o pré-treino do ModernBERT na minha língua" se espalhou |
| **jun/2026** | **moBERTo** | ModernBERT-base continuado em **60 bilhões de tokens em português**. Melhor nDCG@10 médio em três benchmarks de recuperação em PT e melhor resultado no PLUE-PT. Pesos em `Tropic-AI/moBERTo` |

**Para o leitor brasileiro, a notícia relevante é a última.** Até meados de 2026, a
recomendação para português era BERTimbau (2019) por falta de opção moderna. Com o moBERTo,
existe pela primeira vez um encoder em português com arquitetura de 2024, 8.192 tokens de
contexto e treino em escala moderna.

**Recomendação atualizada para português, agosto de 2026:**

- **Padrão seguro:** `neuralmind/bert-base-portuguese-cased` (BERTimbau) — maduro, muito
  usado, MIT, farta documentação e derivados.
- **Candidato forte:** `Tropic-AI/moBERTo` — arquitetura moderna, contexto longo, melhores
  números publicados em recuperação em PT. É novo (junho/2026), então tem menos rodagem em
  produção. **Meça nos seus dados antes de trocar** — e verifique a licença no model card.
- **Multilíngue:** `jhu-clsp/mmBERT-base`, se você lida com mais de uma língua.

Este curso continua usando BERTimbau nos exemplos por maturidade e reprodutibilidade; o
código todo funciona trocando uma linha (`MODELO_BASE`).

---

## 2 · Encoder × LLM: o debate se resolveu por economia

A pergunta "encoders ainda fazem sentido?" foi respondida com medição, e a resposta é mais
enfática do que se esperava.

Um estudo de 2026 sobre seleção de modelo com consciência de custo (IMDB, SST-2, AG News,
DBPedia) concluiu que **encoders afinados atingem desempenho competitivo, e frequentemente
superior, a uma ou duas ordens de grandeza menos de custo e latência** que LLMs em zero e
few-shot. Os autores recomendam explicitamente evitar o uso indiscriminado de LLMs para
classificação de texto padrão.

Outra medição citada na literatura de 2026 quantifica a diferença energética: inferência
completa em minutos e ~0,01 kWh para encoders, contra dezenas a centenas de minutos e
0,2–2,1 kWh para abordagens com LLM — algo entre 15× e 250× em velocidade e 20× a 200× em
energia, dependendo da configuração.

**Como isso deve mudar sua decisão:**

| Situação | Escolha em 2026 |
|---|---|
| Classificação fechada, alto volume | **encoder afinado** — não há discussão |
| Extração de entidades conhecidas | **encoder** |
| Recuperação e reranking | **encoder** (bi + cross) |
| Categorias mudam toda semana | LLM ou zero-shot |
| Tarefa aberta, geração, raciocínio | LLM |
| Poucos dados rotulados, baixo volume | LLM (e use-o para rotular e destilar) |
| Volume alto **e** poucos rótulos | **híbrido**: LLM rotula 2 mil, encoder serve o resto |

O último padrão é o mais importante da tabela e o que mais cresceu: **destilação assimétrica**
— pagar caro uma vez pelo rótulo e barato para sempre pela inferência.

---

## 3 · O que mudou tecnicamente nos encoders modernos

| Componente | BERT (2018) | Encoder moderno (2024–2026) |
|---|---|---|
| Posição | embeddings aprendidos, 512 fixos | **RoPE** — extrapola |
| Normalização | post-LN (exige warmup) | **pre-LN / Pre-RMSNorm** |
| Atenção | densa, quadrática | **Flash Attention + local/global alternada** |
| Padding | tokens `[PAD]` computados | **unpadding** — não computa o que não existe |
| Viés nas lineares | sim | não (economiza parâmetros sem perda) |
| FFN | Linear-GELU-Linear | **GeGLU** |
| Contexto | 512 | 4.096 a 8.192 |
| Dados | 3,3 bilhões de palavras | 2 a 3 **trilhões** de tokens, com código |
| Tokenizador | WordPiece, 30 mil | BPE/Unigram, 50 mil a 256 mil |
| Objetivo | MLM 15% + NSP | MLM (taxa variável), **sem NSP** |

Praticamente tudo veio de descobertas feitas em LLMs entre 2020 e 2024 e reaplicadas ao
encoder. É um caso claro de **transferência de engenharia entre linhagens**: nenhuma dessas
ideias exigia um decoder, mas todas foram descobertas lá, porque era lá que o dinheiro estava.

---

## 4 · Debates em aberto

### "Encoders vão desaparecer?"

**Argumento a favor:** LLMs pequenos (1 a 8 B) ficam mais baratos a cada ano; embeddings de
LLMs decoder já competem em benchmarks de recuperação; manter duas pilhas custa caro.

**Argumento contra:** duas ordens de grandeza de custo não somem por evolução incremental; a
bidirecionalidade é uma vantagem estrutural para compreensão; a energia por inferência importa
cada vez mais, técnica e regulatoriamente.

**Minha opinião profissional, declarada como opinião:** encoders continuarão existindo, mas
serão cada vez mais **produzidos por destilação a partir de LLMs** em vez de pré-treinados do
zero. O caminho "LLM ensina, encoder serve" é economicamente dominante, e já é o padrão em
times maduros.

### "Contexto longo resolve a fatiação?"

8.192 tokens cobrem um documento de ~20 páginas. Mas atenção é quadrática: processar 8.192 de
uma vez custa muito mais que 16 janelas de 512. Para recuperação, evidências indicam que
fatias menores continuam funcionando melhor — a granularidade ajuda a busca. **Contexto longo
é útil para classificar documento inteiro, não necessariamente para recuperar.**

### "Modelo específico da língua ainda vale?"

O aparecimento do moBERTo é evidência a favor: a receita "continuar o pré-treino de um bom
modelo em inglês na minha língua" custa muito menos que treinar do zero e produz resultados
melhores que o multilíngue genérico. Espere ver isso se repetir em mais línguas.

---

## 5 · O que observar nos próximos 12 meses

1. **Adoção real do moBERTo** em português — se aparecerem derivados (versões para NER,
   sentence-transformers, rerankers), ele vira o novo padrão em PT.
2. **ModernBERT-large e sucessores** disputando o topo com DeBERTa-v3 em classificação.
3. **Encoders destilados de LLMs** como categoria própria, com receitas públicas.
4. **Rerankers multilíngues** de qualidade — hoje ainda é o elo fraco do RAG em português.
5. **Regulação de eficiência energética** de IA na UE e no Brasil, que pode transformar a
   vantagem de custo dos encoders em vantagem de conformidade.

---

## 6 · Como manter este arquivo vivo

Fontes que valem acompanhar (e que foram usadas aqui):

- [Hugging Face Blog](https://huggingface.co/blog) e [Papers](https://huggingface.co/papers)
- [MTEB Leaderboard](https://huggingface.co/spaces/mteb/leaderboard)
- [Answer.AI blog](https://www.answer.ai/) — origem do ModernBERT
- arXiv, categoria [cs.CL](https://arxiv.org/list/cs.CL/recent)
- [Papers With Code — Language Modelling](https://paperswithcode.com/)

---

## Autoteste

1. Por que os encoders ficaram parados entre 2018 e 2024, e o que os destravou?
2. Qual é a recomendação para português em agosto de 2026, e qual a ressalva sobre a novidade?
3. Cite quatro mudanças técnicas do ModernBERT em relação ao BERT e o efeito de cada uma.
4. Qual é a ordem de grandeza da diferença de custo entre encoder afinado e LLM em classificação?
5. Descreva o padrão híbrido de destilação assimétrica e por que ele é economicamente dominante.
6. Contexto de 8.192 tokens elimina a necessidade de fatiar documentos em RAG? Justifique.
7. Por que a receita "continuar o pré-treino em outra língua" se espalhou em 2025–2026?

---

## Fontes consultadas (12/08/2026)

- Warner et al. (2024). *ModernBERT*. [answer.ai/posts/2024-12-19-modernbert.html](https://www.answer.ai/posts/2024-12-19-modernbert.html) · [huggingface.co/answerdotai/ModernBERT-base](https://huggingface.co/answerdotai/ModernBERT-base)
- Le Breton et al. (2025). *NeoBERT: A Next-Generation BERT*. [arXiv:2502.19587](https://arxiv.org/abs/2502.19587)
- Marone et al. (2025). *mmBERT: A Modern Multilingual Encoder*. [arXiv:2509.06888](https://arxiv.org/html/2509.06888v1) · [github.com/jhu-clsp/mmBERT](https://github.com/jhu-clsp/mmBERT)
- Laitz, Sales Almeida, Alves Santos & Bonás (21/06/2026). *moBERTo: A Modern Encoder for Portuguese via Continued Pretraining of ModernBERT*. [arXiv:2606.22722](https://arxiv.org/abs/2606.22722) · pesos: `Tropic-AI/moBERTo`
- *Cost-Aware Model Selection for Text Classification: Multi-Objective Trade-offs Between Fine-Tuned Encoders and LLM Prompting in Production* (2026). [arXiv:2602.06370](https://arxiv.org/html/2602.06370v1)
- *ModernBERT or DeBERTaV3? Examining Architecture and Data Influence* (2025). [arXiv:2504.08716](https://arxiv.org/pdf/2504.08716)
- *Return of the Encoder: Maximizing Parameter Efficiency for SLMs* (2025). [arXiv:2501.16273](https://arxiv.org/pdf/2501.16273)

---

*Anterior: [60-teoria-avancada.md](60-teoria-avancada.md) · Próximo: [70-pratica.md](70-pratica.md)*
