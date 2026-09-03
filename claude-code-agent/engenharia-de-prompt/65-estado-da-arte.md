# 65 · Estado da arte — onde a área está em agosto de 2026

**Nível:** avançado → pesquisa · **Escrito em:** 19/08/2026
**Este arquivo envelhece rápido.** Reavalie a cada 6 meses. Pesquisado na web
em 19/08/2026; fontes no rodapé.

---

## 65.1 · As três eras, e onde estamos

| Era | Período | Pergunta central | Artefato |
|---|---|---|---|
| **Engenharia de prompt** | 2022–2024 | como escrevo esta instrução? | uma string |
| **Engenharia de contexto** | 2025 | o que deve estar na janela agora? | um pipeline de montagem de contexto |
| **Engenharia de arnês** (*harness*) | 2026 | como monto o sistema que dá autonomia ao modelo com segurança? | uma arquitetura: ferramentas, políticas, avaliadores, limites |

A palavra "prompt" continua no nome da profissão por inércia. **O objeto de
trabalho mudou duas vezes em quatro anos.** Quem estagnou na primeira era está
resolvendo um problema que os modelos resolvem sozinhos desde 2025.

---

## 65.2 · O que está consolidado (não é mais fronteira)

| Prática | Situação |
|---|---|
| Saída estruturada com garantia no decodificador | padrão da indústria |
| Cache de prompt como decisão de arquitetura | padrão |
| Suíte de avaliação em CI, com portão | esperado em vaga sênior |
| Pensamento estendido nativo com nível de esforço | padrão nos modelos de fronteira |
| Uso de ferramentas / laço agêntico | padrão |
| Janelas de ~1 M tokens | disponível nos principais modelos |
| Multimodal (imagem, PDF, áudio) na mesma chamada | disponível |
| Recuperação híbrida + reordenação em RAG | prática recomendada |

Se algum item acima ainda é novidade no seu trabalho, **é aí que está o maior
retorno imediato** — não na fronteira.

---

## 65.3 · A fronteira ativa

### Otimização automática de prompt

O trabalho mais influente é o **GEPA** (arXiv:2507.19457), aceito como *oral*
no **ICLR 2026**: reflexão em linguagem natural sobre trajetórias + fronteira de
Pareto, superando aprendizado por reforço com até 35× menos execuções e o
MIPROv2 em mais de 10%. **DSPy 3.3.0** é a implementação de referência acessível.

**Onde ainda não chegou:** tarefas sem métrica automática, e domínios em que o
prompt precisa ser auditável por humano. Ver
[45](45-otimizacao-automatica.md).

### Gerador e avaliador separados

Linha de 2026, apoiada em pesquisa da própria Anthropic: **modelos não avaliam
com confiabilidade o próprio trabalho**. A resposta arquitetural é separar
gerador e avaliador — agentes distintos, prompts distintos, e de preferência
famílias de modelo distintas — em vez de pedir autocrítica ao mesmo modelo.

Consequência prática: "peça ao modelo para revisar a própria resposta" saiu da
lista de boas práticas e entrou na lista de coisas que dão falsa segurança.

### Engenharia de contexto como infraestrutura

A janela deixou de ser "o texto que eu mando" e virou **infraestrutura
programável**: o que entra é decidido dinamicamente por código, com orçamento,
prioridade, compactação e poda. Ver [15](15-contexto-e-rag.md).

### Avaliação de agentes de horizonte longo

Problema aberto e caro. Ninguém sabe pontuar bem uma trajetória de 200 passos
com resultado parcialmente certo. As abordagens correntes — marcos intermediários,
rubricas por etapa, verificação por estado final do ambiente — são todas
parciais.

### Segurança de agentes

A superfície cresceu com autonomia e ferramentas. A trinca letal
([35 §35.3](35-seguranca-e-injecao.md)) virou o vocabulário padrão de análise de
risco. **Não há defesa com garantia** contra injeção indireta; o que existe é
contenção arquitetural.

---

## 65.4 · Movimentos de mercado (2026)

| Data | Fato | Por que importa |
|---|---|---|
| 02/03/2026 | **Anthropic Academy** aberta: cursos e certificados gratuitos | material oficial gratuito supera a maioria dos cursos pagos |
| 09/03/2026 | **OpenAI anuncia aquisição do promptfoo** | a principal ferramenta aberta de avaliação passa a pertencer a um fornecedor de modelos; a empresa declarou que manterá a versão aberta |
| ao longo de 2026 | vagas de "prompt engineer" reintituladas para "AI engineer" | a habilidade se dissolveu na engenharia — ver [40](40-a-profissao.md) |
| 2026 | *agentic engineering* como enquadramento dominante | humanos escrevem especificação, critério de avaliação e limites; agentes executam |

**Risco a acompanhar (opinião):** ferramentas de avaliação pertencerem a
fornecedores de modelo cria conflito de interesse estrutural. Não é motivo para
abandonar a ferramenta hoje; é motivo para manter o seu próprio arnês mínimo
capaz de rodar sem ela.

---

## 65.5 · O que provavelmente vai envelhecer mal

Previsões, marcadas como **opinião**, para você reavaliar em 2027:

1. **Prompts longos escritos à mão.** Onde houver métrica, serão otimizados por
   máquina.
2. **Truques de formatação específicos de um modelo.** Cada geração absorve.
3. **RAG artesanal para casos simples.** Janela grande + cache já vence em
   corpora pequenos.
4. **Autocrítica pelo mesmo modelo.** Já está caindo (§65.3).
5. **Certificados genéricos de prompt.** Valor de mercado tendendo a zero.

E o que **não** deve envelhecer:

1. Definir o que é resposta certa, com quem entende do negócio.
2. Construir e manter conjunto de avaliação representativo.
3. Decidir o que entra no contexto.
4. Controlar custo, latência e risco.
5. Projetar o sistema em volta do modelo supondo que ele vai falhar.

---

## 65.6 · Como se manter atualizado sem se afogar

| Fonte | Cadência | Por quê |
|---|---|---|
| Notas de versão e documentação dos fornecedores | ao lançar modelo | é onde aparecem parâmetros novos e removidos |
| Seu próprio conjunto de avaliação, rodado no modelo novo | a cada modelo | é o único dado que fala do **seu** caso |
| arXiv cs.CL / cs.AI, filtrado | semanal, superficial | fronteira real |
| ICLR / NeurIPS / ACL, trilhas relevantes | anual | o que sobreviveu à revisão |
| Blogs de engenharia de quem opera em escala | mensal | prática que não vira paper |

**Método que eu recomendo:** quando sair um modelo novo, **não leia o anúncio —
rode o seu conjunto**. Trinta minutos de medição valem mais que uma semana de
leitura de opiniões alheias, e a resposta é sobre o seu problema.

---

## Autoteste

1. Quais são as três eras e qual é o artefato de trabalho de cada uma?
2. Cite três práticas consolidadas que já não são diferencial.
3. O que o GEPA mostrou e por que a fronteira de Pareto é central nele?
4. Por que "peça ao modelo para revisar a própria resposta" saiu da lista de
   boas práticas?
5. Qual é o conflito de interesse criado pela aquisição do promptfoo, e qual é
   a mitigação sensata?
6. Cite três coisas que devem envelhecer mal e três que não devem.
7. Qual é o método recomendado quando sai um modelo novo?

---

### Fontes consultadas (19/08/2026)

- GEPA, arXiv:2507.19457 — ICLR 2026 (oral) — <https://arxiv.org/abs/2507.19457>
- OpenAI, anúncio de aquisição do promptfoo (09/03/2026) — <https://openai.com/index/openai-to-acquire-promptfoo/>
- Promptfoo, *Promptfoo is joining OpenAI* — <https://www.promptfoo.dev/blog/promptfoo-joining-openai/>
- Anthropic Academy — <https://anthropic.skilljar.com>
- SDG Group, *The Evolution of Prompt Engineering to Context Design in 2026* — <https://www.sdggroup.com/en/insights/blog/the-evolution-of-prompt-engineering-to-context-design-in-2026>
- Epsilla, *Why Harness Engineering Replaced Prompting in 2026* — <https://www.epsilla.com/blogs/harness-engineering-evolution-prompt-context-autonomous-agents>
- PyPI, `dspy` 3.3.0 — <https://pypi.org/project/dspy/>
