# 90 · Bibliografia comentada

**Nível:** todos · Verificado em 13/08/2026

**Aviso de honestidade.** Agentes de IA como assunto têm menos de dois anos de
maturidade prática. **Não existe, em agosto de 2026, um livro-texto canônico
sobre agentes de LLM** — e desconfie de quem afirmar o contrário. O que existe
é: livros clássicos sobre agentes *como conceito*, livros sobre os
fundamentos que sustentam a prática, e material primário (papers e
documentação) que é onde o assunto realmente vive.

Os livros abaixo são reais e verificáveis. Onde não tenho certeza da edição,
cito só autor e título — conforme a regra deste repositório.

---

## 1. Agentes como conceito (os clássicos que continuam valendo)

### Russell, S. & Norvig, P. — *Artificial Intelligence: A Modern Approach*
Pearson, 4ª ed., 2020.

**Nível:** intermediário. **Leia:** capítulo 2 (agentes inteligentes) e
capítulo 17 (decisão sob incerteza).

O livro-texto da área. O capítulo 2 define agente — percepção, atuação,
racionalidade, tipos de ambiente — e essa definição **não envelheceu**: ela
descreve um agente de LLM tão bem quanto descrevia um robô em 1995. Ler o
capítulo 2 depois de usar o Claude Code por um mês é uma experiência
esclarecedora.

O resto do livro (busca, lógica, planejamento clássico) está datado como
prática e continua excelente como formação.

**Em português:** *Inteligência Artificial* (tradução da 3ª ed., Elsevier /
GEN LTC). Tradução aceitável, edição anterior — sem o material moderno de
aprendizado profundo. Se você lê inglês, prefira a 4ª.

### Wooldridge, M. — *An Introduction to MultiAgent Systems*
Wiley, 2ª ed., 2009.

**Nível:** intermediário. **Envelheceu?** Como tecnologia, sim; como teoria,
não.

A referência de sistemas multiagente pré-LLM: coordenação, negociação,
protocolos, teoria dos jogos aplicada a agentes. Vale para quem quer entender
por que "muitos agentes" é difícil de um jeito que não depende do modelo —
uma boa vacina contra o entusiasmo de 2026 com multiagente
([16](16-subagentes-e-orquestracao.md)).

### Bratman, M. — *Intention, Plans, and Practical Reason*
Harvard University Press, 1987.

**Nível:** filosofia. Origem do modelo BDI (crença–desejo–intenção). Leitura
opcional, e a única do curso que trata de agência sem falar de computador.
Muda a forma como você lê a palavra "plano".

---

## 2. Fundamentos que sustentam a prática

### Sutton, R. & Barto, A. — *Reinforcement Learning: An Introduction*
MIT Press, 2ª ed., 2018.
**📖 Legalmente gratuito:** [incompleteideas.net/book/the-book.html](http://incompleteideas.net/book/the-book.html)

**Nível:** avançado (exige cálculo e probabilidade). **Leia:** capítulos 1 e 3;
e a seção sobre atribuição de crédito.

Onde estão os conceitos que explicam por que agentes de trajetória longa são
difíceis: recompensa esparsa, atribuição de crédito, exploração × explotação.
Não é preciso ler inteiro; os capítulos iniciais já reenquadram o problema.
Base do [60](60-teoria-avancada.md).

### Sipser, M. — *Introduction to the Theory of Computation*
Cengage, 3ª ed., 2012.

**Nível:** intermediário. **Leia:** capítulo 5 (redutibilidade), para o
problema da parada e o teorema de Rice.

É a fundamentação de "não existe verificador geral de correção" — a afirmação
mais consequente do [60](60-teoria-avancada.md), e a que mais gente contesta
sem ter lido a demonstração.

### Jurafsky, D. & Martin, J. — *Speech and Language Processing*
3ª edição, rascunho público.
**📖 Legalmente gratuito:** [web.stanford.edu/~jurafsky/slp3/](https://web.stanford.edu/~jurafsky/slp3/)

**Nível:** intermediário. Referência de PLN, atualizada com transformers e
LLMs. Consulte por capítulo; não leia linearmente. Ver também o assunto
[`bert`](../bert/00-MAPA.md) desta pasta.

### Goodfellow, I., Bengio, Y. & Courville, A. — *Deep Learning*
MIT Press, 2016.
**📖 Legalmente gratuito:** [deeplearningbook.org](https://www.deeplearningbook.org/)

**Nível:** avançado. **Envelheceu?** Nos detalhes de arquitetura, sim — é
anterior aos transformers. Nos fundamentos (otimização, regularização,
generalização), não.

---

## 3. Engenharia de sistemas com LLM

### Huyen, C. — *AI Engineering: Building Applications with Foundation Models*
O'Reilly, 2025.

**Nível:** intermediário. **O livro mais próximo do assunto deste curso** que
existe em forma de livro. Cobre avaliação, seleção de modelo, RAG, uso de
ferramentas, otimização de custo e o ciclo de desenvolvimento. Não é sobre
Claude Code, e é a melhor base de engenharia disponível hoje.

Se você vai comprar **um** livro por causa deste curso, é este.

### Huyen, C. — *Designing Machine Learning Systems*
O'Reilly, 2022.

**Nível:** intermediário. Anterior à era dos LLMs, e continua o melhor livro
sobre a parte que ninguém quer fazer: monitoramento, dados, deriva, o que
quebra em produção. As lições transferem inteiras para agentes.

### Kleppmann, M. — *Designing Data-Intensive Applications*
O'Reilly, 2017.

**Nível:** intermediário → avançado. Não é sobre IA. Está aqui porque a
maioria dos problemas de agente em produção é problema de sistema
distribuído: idempotência, tentativa de novo, consistência, falha parcial.
**Em português:** *Projetando Aplicações Intensivas em Dados* (Novatec) —
tradução boa.

---

## 4. Material primário — onde o assunto realmente vive

Em uma área que se move nesta velocidade, o livro está sempre atrasado. A
ordem certa de leitura é:

1. **[Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents)**
   (Anthropic, dez/2024). Vinte minutos. Se você lê só uma coisa desta página,
   leia esta.
2. **[Documentação do Claude Code](https://code.claude.com/docs/)** —
   completa, atualizada, e melhor que a maioria dos cursos pagos.
3. **[Especificação do MCP](https://modelcontextprotocol.io/)**.
4. **Os papers** de [95-referencias.md](95-referencias.md) — ReAct, SWE-bench,
   SWE-agent, Reflexion, Voyager, Toolformer.
5. **O código-fonte** dos agentes abertos: [Aider](https://github.com/Aider-AI/aider),
   [OpenHands](https://github.com/All-Hands-AI/OpenHands),
   [smolagents](https://github.com/huggingface/smolagents). Ler o laço de
   outra pessoa ensina mais que qualquer tutorial.

---

## 5. O que **não** ler

- **Livros de "prompt engineering" de 2023.** A prática mudou: o que rendia em
  GPT-3.5 (repetição, ênfase, "pense passo a passo") hoje causa
  sobre-disparo e piora o resultado. Ver
  [75](75-armadilhas.md) e o efeito da instrução literal nos modelos atuais.
- **Livros sobre AutoGPT.** O padrão não sobreviveu.
- **Qualquer coisa com "domine agentes de IA em 7 dias" no título.** Não é
  snobismo: o assunto tem uma parte que só se aprende medindo, e nenhum livro
  mede por você.
- **Livros sobre frameworks específicos** (LangChain 2023 etc.) — a API muda
  mais rápido que a impressão.

---

## 6. Trilha de leitura por objetivo

| Objetivo | Leia |
|---|---|
| **Usar bem** | *Building Effective Agents* → documentação oficial → este curso |
| **Construir** | Huyen, *AI Engineering* → papers ReAct e SWE-agent → código do smolagents |
| **Entender a fundo** | Russell & Norvig cap. 2 → Sutton & Barto cap. 1 e 3 → Sipser cap. 5 |
| **Operar em produção** | Kleppmann → Huyen, *Designing ML Systems* → [17](17-hooks-permissoes-seguranca.md) e [20](20-avaliacao-e-benchmarks.md) |
| **Pesquisar** | todos os papers de [95](95-referencias.md), em ordem cronológica |

---

## Autoteste

1. Por que não existe livro-texto canônico sobre agentes de LLM em 2026?
2. Qual capítulo de Russell & Norvig continua valendo integralmente, e por quê?
3. Cite três livros legalmente gratuitos desta lista.
4. Por que Kleppmann está numa bibliografia de agentes?
5. Qual é o único livro que você compraria, se comprasse um?
6. Por que livros de prompt engineering de 2023 podem **piorar** o seu
   resultado hoje?
7. Qual é a ordem certa de leitura de material primário?
