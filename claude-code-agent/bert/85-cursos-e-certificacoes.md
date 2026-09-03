# 85 · Cursos gratuitos e certificações

`Nível: todos` · `**Pesquisado na web em 12/08/2026**` ·
`Links podem expirar — o ano de publicação está marcado em cada item`

Ordem de prioridade deste arquivo: **português → inglês → francês**, como manda o preset.

> **Aviso honesto sobre certificação, logo de cara:** não existe, em agosto de 2026,
> nenhuma certificação de BERT ou PLN com valor de mercado comparável a AWS, Google Cloud
> ou Salesforce. O que o mercado dessa área realmente avalia é **portfólio**: repositórios
> com projetos que rodam, modelos publicados no Hugging Face Hub, e a capacidade de
> explicar decisões. Detalhes na seção 4.

---

## 1 · Cursos gratuitos em **português**

### 1.1 · Processamento Neural de Linguagem Natural em Português — IME-USP ⭐

- **Autor:** Prof. Marcelo Finger, com Alan Barzilay · **Instituição:** IME-USP
- **Onde:** [canal do IME-USP no YouTube](https://www.youtube.com/@imeusp) ·
  também no [Coursera](https://www.coursera.org/learn/processamento-neural-linguagem-natural-em-portugues-i) ·
  materiais em [nlportugues.ime.usp.br](https://nlportugues.ime.usp.br/)
- **Publicado:** novembro de 2023 · **Duração:** 6 módulos
- **Nível:** iniciante (pede só Python básico)
- **Conteúdo:** linguística computacional, redes neurais, representação de palavras,
  word2vec, redes recorrentes, seq2seq, LSTM e GRU.
- **Vale o tempo?** **Sim, e é o melhor material acadêmico em português da área.** É o
  caminho ideal *antes* deste curso se você não tem base de redes neurais. Duas ressalvas
  honestas: usa **TensorFlow** (este curso usa PyTorch — os conceitos transferem, o código
  não) e **para antes dos Transformers**, cobrindo a geração RNN/LSTM. É a fundação, não o
  destino.
- **Gratuito de verdade?** Sim no YouTube. No Coursera, assistir é grátis; o certificado é pago.

### 1.2 · Hugging Face LLM Course (antigo NLP Course)

- **Onde:** [huggingface.co/learn](https://huggingface.co/learn) — a interface tem seletor
  de idioma, e a tradução para português existe mas está **incompleta** (capítulos iniciais
  traduzidos; os avançados, em inglês)
- **Duração:** 13 capítulos · **Nível:** iniciante a intermediário
- **Vale o tempo?** **É o material prático mais importante desta lista.** Os capítulos 1 a 4
  cobrem exatamente o que este curso usa: arquitetura Transformer, tokenizadores, Hub,
  fine-tuning. Se você fizer só uma coisa desta página, faça esses quatro capítulos.
- **Certificado:** há certificados **por capítulo**, gratuitos. Valor simbólico, não de mercado.
- **Gratuito de verdade?** Sim, sem anúncios. Você paga só se usar GPU paga para os exercícios.

### 1.3 · Google Machine Learning Crash Course — em português

- **Onde:** [developers.google.com/machine-learning/crash-course?hl=pt-br](https://developers.google.com/machine-learning/crash-course?hl=pt-br)
- **Duração:** ~15 h · **Nível:** iniciante
- **Vale o tempo?** Sim, se você não sabe ML supervisionado. Cobre treino/validação/teste,
  overfitting e métricas — exatamente os pré-requisitos que faltam em quem trava no
  [75-armadilhas.md](75-armadilhas.md). Não é sobre BERT; é sobre o chão embaixo dele.

### 1.4 · Transformer Models and BERT Model — Google Cloud (dublado em PT-BR)

- **Onde:** [Coursera, versão em português brasileiro](https://www.coursera.org/learn/transformer-models-and-bert-model---portugus-brasileiro)
- **Duração:** ~1 h · **Nível:** iniciante · **Publicado:** 2023, com atualizações
- **Vale o tempo?** Como panorama de 45 minutos, sim. É superficial e usa TensorFlow/Vertex AI.
  Não substitui os capítulos 1–4 do Hugging Face.
- **Gratuito de verdade?** Assistir sim (modo *audit*); certificado exige assinatura do Coursera.

### 1.5 · Curso de Extensão em PLN — UNICAMP

- **Onde:** [ic.unicamp.br/~nlp](https://www.ic.unicamp.br/~nlp/) · 4 módulos, ~40 h
- **Cobre modelos atencionais e Transformers**, o que o curso do IME não alcança.
- **Atenção:** é curso de extensão com oferta periódica e **nem sempre gratuito** — confira
  as condições da turma corrente antes de contar com ele.

### 1.6 · Canais brasileiros no YouTube

Consistência e qualidade variam; use como complemento, não como trilha:

- **Data Science Academy** — publica material introdutório gratuito em PT; os cursos
  completos são pagos.
- Vídeos avulsos sobre BERT e Transformers em PT existem em quantidade. Critério para
  filtrar: **veja a data**. Qualquer vídeo em português anterior a 2023 provavelmente
  mostra API do `transformers` incompatível com a v5 usada aqui
  ([03-instalacao.md](03-instalacao.md#o-que-mudou-do-transformers-4-para-o-5)).

---

## 2 · Cursos gratuitos em **inglês**

### 2.1 · Stanford CS224N — NLP with Deep Learning ⭐⭐

- **Instituição:** Stanford · **Onde:**
  [playlist Spring 2024 no YouTube](https://www.youtube.com/playlist?list=PLoROMvodv4rOaMFbaqxPDoLWjDaRAdP9D) ·
  site com slides e trabalhos: [web.stanford.edu/class/cs224n](https://web.stanford.edu/class/cs224n/)
- **Duração:** ~20 h de aula, mais os trabalhos · **Nível:** avançado
- **Vale o tempo?** **É a melhor formação teórica gratuita que existe na área, sem
  concorrente próximo.** A aula sobre atenção e Transformers é a fonte de metade das
  explicações que circulam pela internet. Os trabalhos práticos são exigentes e valem mais
  que os vídeos.
- **Pré-requisitos reais:** álgebra linear, cálculo, Python. Não comece por aqui.
- **Gratuito?** Vídeos, slides e enunciados: sim. Correção, crédito e certificado: não
  (a versão paga é o programa profissional XCS224N).

### 2.2 · Hugging Face LLM Course (versão original, em inglês)

- **Onde:** [huggingface.co/learn/llm-course](https://huggingface.co/learn/llm-course)
- Mais completo e mais atual que a tradução para PT. Capítulos 5 a 8 (datasets,
  tokenizadores, tarefas clássicas de PLN, depuração de treino) só existem em inglês.
- Certificados por capítulo, gratuitos.

### 2.3 · Jay Alammar — The Illustrated Transformer / The Illustrated BERT

- **Onde:** [jalammar.github.io](https://jalammar.github.io/illustrated-transformer/)
- **Duração:** ~1 h de leitura · **Publicado:** 2018, ainda o padrão de referência
- **Vale o tempo?** **Sim — leia antes de [13-arquitetura-encoder.md](13-arquitetura-encoder.md).**
  São as ilustrações que praticamente todo mundo no campo tem na cabeça ao pensar em atenção.

### 2.4 · fast.ai — Practical Deep Learning for Coders

- **Onde:** [course.fast.ai](https://course.fast.ai/) · **Nível:** iniciante a intermediário
- Abordagem "código primeiro, teoria depois". Ótimo para quem programa e trava na
  matemática. Cobre PLN entre outros domínios; não é específico de BERT.

### 2.5 · Documentação do Hugging Face como trilha

- [huggingface.co/docs/transformers](https://huggingface.co/docs/transformers) — guias por
  tarefa (classificação, NER, QA) com código completo.
- [sbert.net](https://sbert.net/) — a trilha de referência para embeddings e busca semântica,
  material do [16-embeddings-e-busca-semantica.md](16-embeddings-e-busca-semantica.md).

---

## 3 · Cursos gratuitos em **francês**

### 3.1 · Hugging Face — Cours de NLP en français ⭐

- **Onde:** [huggingface.co/learn/nlp-course/fr/chapter1/1](https://huggingface.co/learn/nlp-course/fr/chapter1/1)
- **É a tradução francesa mais completa que existe da lista toda** — bem mais avançada que
  a tradução para português. Se você lê francês, é a melhor opção não anglófona.
- Gratuito, sem anúncios.

### 3.2 · CNAM — RCP217 : BERT, BART et les Transformers

- **Autor:** Serge Rosmorduc · **Instituição:** CNAM (Conservatoire national des arts et métiers)
- **Onde:** [material do curso em PDF](https://cedric.cnam.fr/vertigo/cours/RCP217/) —
  procure o módulo `cours-tal-04.pdf`
- **Nível:** intermediário a avançado. Material universitário francês, gratuito, específico
  sobre BERT e BART. Slides sem vídeo.

### 3.3 · France Université Numérique (FUN-MOOC)

- **Onde:** [fun-mooc.fr](https://www.fun-mooc.fr/) — busque "TAL", "apprentissage profond"
  ou "intelligence artificielle"
- MOOCs de universidades francesas, gratuitos para assistir, com certificado pago. A oferta
  muda a cada semestre; verifique o catálogo corrente.

---

## 4 · Certificações — a conversa franca

### Não existe certificação de BERT

Nenhuma organização — nem Google, nem Meta, nem Hugging Face — oferece uma certificação
específica em BERT ou em modelos encoder. Isso não é lacuna do mercado: é sinal de que a
área avalia por outra coisa.

### O que existe, e o que vale

| Certificação | Emissor | Custo | Valor real de mercado |
|---|---|---|---|
| **Certificados por capítulo do LLM Course** | Hugging Face | grátis | **simbólico**. Bom para o LinkedIn, ignorado em entrevista técnica |
| **Certificado do Coursera** (curso do IME-USP, Google Cloud) | Coursera | assinatura mensal | baixo a moderado. O do IME-USP tem peso acadêmico em contexto brasileiro |
| **Google Cloud Professional ML Engineer** | Google | US$ 200 | **moderado a alto**, mas é sobre Vertex AI e MLOps, não sobre BERT |
| **AWS Certified Machine Learning – Specialty** | AWS | US$ 300 | **moderado a alto**, idem para o ecossistema AWS |
| **DeepLearning.AI Specializations** | Coursera | assinatura | moderado como aprendizado; baixo como credencial |
| Certificados de plataformas genéricas | vários | varia | **próximo de zero** |

### O que realmente é avaliado em processo seletivo

Opinião profissional, declarada como opinião, e consistente com o que se vê em entrevistas
da área:

1. **Repositório no GitHub com um projeto que roda.** Um único projeto sério — com README,
   testes, avaliação honesta e model card — vale mais que dez certificados. O
   [projeto-modelo](07-projeto-modelo/README.md) deste curso é literalmente esse formato.
2. **Modelo publicado no Hugging Face Hub**, com model card decente. É gratuito e é a
   credencial mais específica da área que existe.
3. **Saber explicar suas decisões.** "Por que F1 macro e não acurácia?", "como você sabe que
   não há vazamento?", "por que não usou um LLM?" — quem responde isso com naturalidade
   demonstra mais do que qualquer prova.
4. **Kaggle**, se você gosta de competição. Uma medalha em competição de PLN tem peso real.

**Se você tem orçamento para exatamente uma certificação paga**, e trabalha ou quer
trabalhar com nuvem, escolha a do provedor que sua empresa usa (Google Cloud ou AWS). Ela
certifica a plataforma, não o modelo — e é a plataforma que aparece nas vagas.

---

## 5 · Trilha sugerida, juntando tudo

**Se você não tem base de ML:**

```
Google ML Crash Course (PT, 15h)
   → IME-USP, PLN Neural em Português (PT, 6 módulos)
   → Hugging Face LLM Course, caps. 1–4 (PT/EN)
   → este curso, do 01 ao 19
```

**Se você já programa e conhece ML:**

```
Hugging Face LLM Course, caps. 1–4
   → este curso: 03 → 04 → 07-projeto-modelo → 10 a 19
   → The Illustrated Transformer
   → CS224N (aulas de atenção e Transformers)
```

**Se você quer profundidade de pesquisa:**

```
CS224N completo, com os trabalhos
   → este curso: 60 e 65
   → papers de 95-referencias.md, em ordem cronológica
   → reproduzir um resultado publicado
```

---

## Autoteste

1. Qual é o melhor curso acadêmico gratuito em português, e quais são suas duas limitações?
2. Qual material desta lista é o mais importante na prática, e por quê?
3. Existe certificação de BERT? O que o mercado avalia no lugar?
4. Os certificados do Hugging Face têm valor de mercado? Seja honesto.
5. Se você tem orçamento para uma certificação paga, qual escolher e por quê?
6. Por que desconfiar de vídeo em português sobre BERT publicado antes de 2023?
7. Qual é a trilha certa para quem não tem base de machine learning?

---

## Fontes consultadas (12/08/2026)

- [IME-USP — Processamento Neural de Linguagem Natural em Português](https://www.ime.usp.br/ime-usp-oferece-curso-de-processamento-neural-de-linguagem-natural-em-portugues-i-no-coursera/) · [Jornal da USP sobre a liberação no YouTube](https://jornal.usp.br/universidade/curso-da-usp-sobre-processamento-neural-e-disponibilizado-gratuitamente-no-youtube/) · [nlportugues.ime.usp.br](https://nlportugues.ime.usp.br/)
- [Hugging Face — Learn](https://huggingface.co/learn) · [LLM Course](https://huggingface.co/learn/llm-course) · [versão francesa](https://huggingface.co/course/fr/chapter1/1)
- [Stanford CS224N](https://web.stanford.edu/class/cs224n/) · [playlist Spring 2024](https://www.youtube.com/playlist?list=PLoROMvodv4rOaMFbaqxPDoLWjDaRAdP9D)
- [Google ML Crash Course (PT-BR)](https://developers.google.com/machine-learning/crash-course?hl=pt-br)
- [Coursera — Transformer Models and BERT Model (PT-BR)](https://www.coursera.org/learn/transformer-models-and-bert-model---portugus-brasileiro)
- [UNICAMP — NLP](https://www.ic.unicamp.br/~nlp/)
- [CNAM RCP217 — BERT, BART et les Transformers](https://cedric.cnam.fr/vertigo/cours/RCP217/)
- [FUN-MOOC](https://www.fun-mooc.fr/) · [fast.ai](https://course.fast.ai/) · [jalammar.github.io](https://jalammar.github.io/illustrated-transformer/) · [sbert.net](https://sbert.net/)

---

*Anterior: [80-custos-e-licencas.md](80-custos-e-licencas.md) · Próximo: [90-bibliografia.md](90-bibliografia.md)*
