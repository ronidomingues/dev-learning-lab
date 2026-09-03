# 95 · Referências — documentação, papers, código e pessoas

**Nível:** todos · **Conferido em:** 19/08/2026

Fonte primária primeiro. Blog de terceiro é atalho, não referência.

---

## 95.1 · Documentação oficial (leia antes de qualquer tutorial)

| Fonte | O que tem | Link |
|---|---|---|
| **Anthropic — visão geral de prompt** | ponto de entrada; aponta para as boas práticas vivas | <https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/overview> |
| **Anthropic — boas práticas por modelo** | ajuste específico dos modelos atuais; é a referência viva | <https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices> |
| **Anthropic — definir critério de sucesso e avaliações** | a parte que quase todo tutorial pula | <https://platform.claude.com/docs/en/test-and-evaluate/develop-tests> |
| **Claude Cookbooks** | receitas executáveis, inclusive o gerador de prompt (metaprompt) | <https://github.com/anthropics/claude-cookbooks> |
| **OpenAI — guia de prompt** | outra família de modelo; útil para comparar | <https://platform.openai.com/docs/guides/prompt-engineering> |
| **Google — documentação Gemini** | idem | <https://ai.google.dev/gemini-api/docs> |

---

## 95.2 · Tutoriais e guias abertos

| Recurso | O que é | Link |
|---|---|---|
| **Tutorial interativo de prompt (Anthropic)** | 9 capítulos com exercícios; versão em Google Sheets | <https://github.com/anthropics/prompt-eng-interactive-tutorial> |
| **Prompt Engineering Guide (DAIR.AI)** | catálogo de técnicas ligado aos papers originais | <https://www.promptingguide.ai/> · <https://github.com/dair-ai/Prompt-Engineering-Guide> |
| **Learn Prompting** | curso aberto, +60 módulos, com versão em português | <https://learnprompting.org/pt/docs/introduction> |
| **Anthropic Academy** | trilhas oficiais com certificado gratuito (desde 02/03/2026) | <https://anthropic.skilljar.com> |

---

## 95.3 · Papers seminais

Ordem cronológica. Os identificadores abaixo foram conferidos.

| Ano | Trabalho | ID | Por que importa |
|---|---|---|---|
| 2017 | Vaswani et al., *Attention Is All You Need* | arXiv:1706.03762 | a arquitetura |
| 2020 | Brown et al., *Language Models are Few-Shot Learners* | arXiv:2005.14165 | nasce o prompt como interface |
| 2022 | Wei et al., *Chain-of-Thought Prompting* | arXiv:2201.11903 | a técnica mais citada da década |
| 2022 | Ouyang et al., *InstructGPT* | arXiv:2203.02155 | por que o modelo obedece |
| 2022 | Yao et al., *ReAct* | arXiv:2210.03629 | raciocínio + ação: o ancestral dos agentes |
| 2023 | Liu et al., *Lost in the Middle* | arXiv:2307.03172 | posição da informação no contexto |
| 2023 | Khattab et al., *DSPy* | arXiv:2310.03714 | prompt como programa compilável |
| 2025–26 | Agrawal et al., *GEPA: Reflective Prompt Evolution…* | arXiv:2507.19457 | **ICLR 2026 (oral)**; otimização por reflexão |

Sem identificador conferido (procure por autor e título):

- Shin et al., *AutoPrompt*, 2020
- Lu et al., *Fantastically Ordered Prompts and Where to Find Them*, 2021
- Xie et al., *An Explanation of In-context Learning as Implicit Bayesian Inference*, 2021
- Olsson et al., *In-context Learning and Induction Heads*, Anthropic, 2022
- Min et al., *Rethinking the Role of Demonstrations*, 2022
- von Oswald et al., *Transformers Learn In-Context by Gradient Descent*, 2023
- Wang et al., *Self-Consistency Improves Chain of Thought Reasoning*, 2022
- Yao et al., *Tree of Thoughts*, 2023
- Sclar et al., *Quantifying Language Models' Sensitivity to Spurious Features in Prompt Design*, 2023
- Merrill & Sabharwal, *The Expressive Power of Transformers with Chain of Thought*, 2023–2024

---

## 95.4 · Código para ler

| Repositório | Por que vale abrir | Link |
|---|---|---|
| `anthropics/prompt-eng-interactive-tutorial` | o material didático oficial | <https://github.com/anthropics/prompt-eng-interactive-tutorial> |
| `anthropics/claude-cookbooks` | padrões reais: RAG, ferramentas, avaliação, metaprompt | <https://github.com/anthropics/claude-cookbooks> |
| `promptfoo/promptfoo` | como se estrutura um arnês de avaliação sério (MIT) | <https://github.com/promptfoo/promptfoo> |
| `stanfordnlp/dspy` | prompt como programa; leia os otimizadores | <https://github.com/stanfordnlp/dspy> |
| `dair-ai/Prompt-Engineering-Guide` | catálogo com ligação para os papers | <https://github.com/dair-ai/Prompt-Engineering-Guide> |
| `rasbt/LLMs-from-scratch` | o modelo por dentro, em PyTorch | <https://github.com/rasbt/LLMs-from-scratch> |
| **este curso** | arnês mínimo em stdlib, 23 testes | [07-projeto-modelo](07-projeto-modelo/README.md) |

---

## 95.5 · Pessoas que vale acompanhar

Critério: publicam com dado, corrigem-se em público, e não vendem curso como
atividade principal. **Opinião minha; a lista envelhece.**

| Pessoa | Por quê | Onde |
|---|---|---|
| **Simon Willison** | o melhor registro contínuo da área; cunhou o enquadramento da "trinca letal" | <https://simonwillison.net/> |
| **Chip Huyen** | engenharia de sistemas de IA, com rigor | <https://huyenchip.com/> |
| **Jay Alammar** | explicações visuais do interior dos modelos | <https://jalammar.github.io/> |
| **Sebastian Raschka** | implementação e pesquisa, sem hype | <https://sebastianraschka.com/> |
| **Andrej Karpathy** | enquadramentos que se tornam vocabulário da área | <https://karpathy.ai/> |
| **Equipe de pesquisa da Anthropic** | interpretabilidade e avaliação | <https://www.anthropic.com/research> |

---

## 95.6 · Outros assuntos desta pasta

| Assunto | Relação |
|---|---|
| [agentes-de-ia](../agentes-de-ia/00-MAPA.md) | onde o prompt vive em 2026 |
| [claude-code](../claude-code/00-MAPA.md) | um agente maduro, para estudar com as mãos |
| [apis](../apis/00-MAPA.md) | a base de HTTP e API que você vai usar todo dia |
| [variaveis-de-ambiente-e-segredos](../variaveis-de-ambiente-e-segredos/00-MAPA.md) | como guardar a chave sem vazar |
| [testes-automatizados](../testes-automatizados/00-MAPA.md) | a mentalidade do conjunto de avaliação |
| [postgresql](../postgresql/00-MAPA.md) · [sql](../sql/00-MAPA.md) | para o exemplo 6 e para RAG sobre banco |
| [ethical-hacking](../ethical-hacking/00-MAPA.md) | mentalidade adversarial para o [35](35-seguranca-e-injecao.md) |

---

## 95.7 · Como verificar uma referência (e este curso)

1. **Todo número tem data e fonte?** Preço, salário, benchmark sem data é
   desinformação.
2. **O link é primário?** Documentação e paper valem mais que resumo de blog.
3. **O autor mostra quantos casos mediu e em qual modelo?** Sem isso, é opinião.
4. **A técnica tem ano?** Técnica sem ano provavelmente é de 2023.
5. **O ISBN existe?** Confira na editora, não em agregador.

Aplique isto a este curso também. Os números publicados aqui vêm de execuções
reais, com data e ambiente declarados — e você pode reproduzi-los:
`cd 07-projeto-modelo && python3 avaliar.py`.
