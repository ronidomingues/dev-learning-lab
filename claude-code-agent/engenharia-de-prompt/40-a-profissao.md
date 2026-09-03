# 40 · A profissão — o cargo real, o mercado real, e como entrar

**Nível:** todos · **Escrito em:** 19/08/2026
**Dados de mercado consultados na web em 19/08/2026.** Fontes no rodapé.

Este arquivo é deliberadamente desconfortável. Se depois de lê-lo você ainda
quiser a carreira, é boa notícia: quer dizer que quer a carreira que existe, e
não a que foi vendida.

---

## 40.1 · O que a vaga pede de verdade

Descrição composta a partir de vagas reais de 2026 (título varia: *AI Engineer*,
*Applied AI Engineer*, *LLM Engineer*, *Prompt Engineer*, *AI Solutions
Engineer*):

```
- Projetar, testar e manter prompts e pipelines de LLM em produção
- Construir e manter suítes de avaliação; instrumentar métricas e traços
- Integrar via API: Python, tratamento de erro, retentativa, streaming
- Otimizar custo e latência (cache, escolha de modelo, batch)
- Trabalhar com RAG: indexação, recuperação, avaliação de recuperação
- Segurança: injeção de prompt, dados sensíveis, red teaming
- Conversar com o time de produto para definir o que é "resposta certa"
```

Note o que **não** está na lista: escrever prompts inspirados. Está lá o
suficiente de engenharia de software para que a pergunta certa seja:

> **É uma vaga de engenharia com especialização em LLM.** Se você não programa,
> a porta de entrada realista é outra (§40.5).

---

## 40.2 · O mercado, com números e com ressalvas

**Ressalva primeiro, porque ela vale mais que os números:** dados de salário de
agregadores (Glassdoor, sites de carreira, blogs) têm amostra pequena, viés de
autorrelato e misturam níveis. Trate tudo abaixo como **ordem de grandeza**.

**Estados Unidos (agosto/2026):** faixas divulgadas de US$ 95 mil a 206 mil de
base, média nacional citada perto de US$ 129,5 mil; laboratórios de fronteira
citam pacotes bem maiores, mas para papéis de engenharia aplicada seniores, não
para escrita de prompt.

**Brasil (agosto/2026), em CLT:**

| Nível | Faixa citada |
|---|---|
| Júnior | R$ 6 mil – 12 mil |
| Pleno | R$ 12 mil – 18 mil |
| Sênior | R$ 20 mil+ |
| Engenheiro de IA (guia Robert Half 2026) | R$ 19,5 mil – 27,1 mil |
| Freelancer internacional com portfólio | US$ 50 – 150/hora |

**A tendência mais importante não é o valor, é o título.** Vagas abertas como
"prompt engineer" frequentemente são **reintituladas** para "AI engineer" antes
de fechar. Ao mesmo tempo, a **habilidade** aparece em muito mais vagas do que
antes — relatórios de 2026 falam em triplicar desde 2024.

**Tradução prática, e é a tese deste arquivo:**

> A profissão não morreu e não é o que prometeram. Ela **se dissolveu dentro da
> engenharia**. O cargo puro é raro; a habilidade é quase obrigatória. Procure
> vagas de engenharia de IA e leve a habilidade de prompt como diferencial —
> não o contrário.

---

## 40.3 · Os três perfis que o mercado contrata

| Perfil | O que faz | Onde está | Faixa |
|---|---|---|---|
| **Engenheiro de IA aplicada** | constrói o produto com LLM: código, prompt, avaliação, custo | produto, startup, consultoria | a maior parte das vagas |
| **Especialista de domínio + IA** | jurídico, saúde, contábil que domina a IA da sua área | escritórios, hospitais, indústria | crescente, e pouco disputada |
| **Pesquisador de avaliação / alinhamento** | mede capacidade e risco de modelos | laboratórios, academia | poucas vagas, alta barreira |

**Opinião profissional:** o segundo perfil é a melhor relação
esforço/oportunidade em 2026 para quem **já tem uma profissão**. Um advogado
que sabe montar e avaliar um sistema de análise de contrato é raríssimo — e
compete com muito menos gente do que um desenvolvedor a mais.

---

## 40.4 · Como se tornar um, do zero — plano de 6 meses

Supõe ~10 h/semana. Cada mês termina com **artefato público**, não com
certificado.

| Mês | O que fazer | Artefato |
|---|---|---|
| **1** | [01](01-introducao-leigo.md)–[06](06-exemplos.md) deste curso; Python básico se faltar; tutorial oficial da Anthropic | repositório com 10 prompts e o que cada um resolve |
| **2** | [07-projeto-modelo](07-projeto-modelo/README.md) inteiro; refazer com **dados seus** | classificador seu, com conjunto rotulado e avaliação |
| **3** | [20-avaliacao](20-avaliacao-e-evals.md) a fundo; promptfoo; portão de CI | repositório com CI verde e relatório de avaliação |
| **4** | [15-contexto-e-rag](15-contexto-e-rag.md); construir um RAG sobre um corpus real | RAG com Recall@k medido e citação verificada |
| **5** | [25-ferramentas](25-ferramentas-e-agentes.md) + [30-custo](30-custo-latencia-caching.md); agente com ferramentas e limite de custo | agente com política de parada e custo p95 medido |
| **6** | [35-seguranca](35-seguranca-e-injecao.md); red team do próprio projeto; escrever o relatório | relatório de red team com achados e correções |

**Regra do artefato:** cada projeto tem README com o problema, a métrica, o
número **antes e depois**, e o custo por mil execuções. Isso é o que faz um
recrutador técnico parar no seu perfil.

---

## 40.5 · Se você não programa

Rotas reais, em ordem de viabilidade:

1. **Especialista de domínio (a melhor).** Você já é advogado, médico,
   contador, professor, analista. Aprenda o suficiente para montar avaliação e
   trabalhar com quem programa. Seu diferencial é saber **o que é resposta
   certa** — que é justamente o que falta nas equipes de engenharia.
2. **Operações de IA / design de conversa.** Manter prompts, curar conjuntos de
   avaliação, rotular, monitorar qualidade. Existe, paga menos, é porta de
   entrada legítima.
3. **Aprender a programar.** Seis meses de Python mudam a faixa inteira. É o
   melhor retorno sobre esforço se você tem tempo.

O que **não** funciona: acumular certificados de prompt sem nunca ter medido
nada. O mercado de 2026 já passou dessa fase.

---

## 40.6 · Portfólio: o que mostrar

Um projeto bem feito vale mais que dez rasos. O que um avaliador técnico
procura, na ordem:

- [ ] **Conjunto rotulado por você**, com o critério de rotulagem escrito.
- [ ] **Métrica antes/depois** de cada mudança de prompt, com o número de casos.
- [ ] **Intervalo de confiança** ou, no mínimo, a consciência de que 20 casos
      não separam 75% de 85% ([20 §20.4](20-avaliacao-e-evals.md)).
- [ ] **Custo por mil execuções**, com o preço datado.
- [ ] **Casos de fronteira** e o que você fez com eles.
- [ ] **Um caso de red team** e a defesa correspondente.
- [ ] **Uma decisão de trade-off explicada** ("usei o modelo menor: −2 pp de
      acerto, −78% de custo; para este caso, compensa").

O último item é o mais raro e o que mais impressiona: ele mostra que você
entende que engenharia é escolha sob restrição.

---

## 40.7 · Entrevista: o que costuma cair

| Pergunta | O que estão avaliando | Resposta ruim | Resposta boa |
|---|---|---|---|
| "Como você melhoraria este prompt?" | se você mede | lista de técnicas | "primeiro montaria 30 casos e mediria onde erra" |
| "O modelo está alucinando. O que fazer?" | diagnóstico | "melhoro o prompt" | fonte no contexto, citação verificada, permitir "não sei", verificar fora do modelo |
| "Como saber se a mudança melhorou?" | estatística | "testei e ficou melhor" | conjunto pareado, tamanho de amostra, intervalo |
| "Custo dobrou. O que investigar?" | economia | — | cache invalidado, saída longa, retentativas, histórico crescendo |
| "Como você impede injeção de prompt?" | maturidade | "instruo o modelo a ignorar" | trinca letal, validação de saída, menor privilégio |
| "Escreva um prompt para X" | ofício | prompt bonito | prompt + como você o avaliaria |

**O padrão:** eles querem saber se você pensa em **medição, custo e falha** —
não se você conhece truques.

---

## 40.8 · Riscos da carreira (a parte honesta)

| Risco | Avaliação |
|---|---|
| **Modelos melhores tornam técnicas desnecessárias** | 🔴 real e contínuo. Metade do que se ensinava em 2023 é inútil. Mitigação: aposte em avaliação, contexto e sistemas — isso não é absorvido |
| **Otimização automática substitui a escrita manual** | 🟡 já acontece onde há métrica ([45](45-otimizacao-automatica.md)). Quem define a métrica continua sendo necessário |
| **O título some** | 🟡 provável, e já em curso. A habilidade permanece |
| **Comoditização** | 🟡 saber usar chatbot vira alfabetização básica; saber medir, não |
| **Mercado saturado de iniciantes** | 🔴 milhares de certificados por mês. Diferencie-se com artefato medido |

**Onde eu apostaria** (opinião, não consenso): avaliação, engenharia de
contexto, segurança e especialização de domínio. **Onde eu não apostaria:**
coleção de técnicas de redação e certificados genéricos.

---

## Autoteste

1. Por que a maioria das vagas dessa área hoje é, na prática, de engenharia?
2. Qual é a diferença entre "o cargo morreu" e "o cargo se dissolveu"?
3. Qual dos três perfis tem a melhor relação esforço/oportunidade para quem já
   tem outra profissão, e por quê?
4. Quais são os sete itens do portfólio, e qual é o mais raro?
5. Como se responde bem a "o modelo está alucinando, o que fazer?"
6. Cite dois riscos reais da carreira e a mitigação de cada um.

---

### Fontes consultadas (19/08/2026)

- Coursera, *Prompt Engineering Salary: A 2026 Guide* — <https://www.coursera.org/articles/prompt-engineering-salary>
- PE Collective, *Is Prompt Engineering a Real Career in 2026?* — <https://pecollective.com/blog/is-prompt-engineering-a-real-career/>
- KORE1, *Prompt Engineer Salary Guide 2026* — <https://www.kore1.com/prompt-engineer-salary-guide/>
- Robert Half Brasil, guia salarial 2026 — <https://www.roberthalf.com/br/pt/vagas-detalhes/engenheiroa-de-prompt>
- Forbes Brasil, *Engenheiro de IA: o que faz e quanto ganha* (fev/2026) — <https://forbes.com.br/carreira/2026/02/engenheiro-de-ia-o-que-faz-quanto-ganha-profissao-mais-cresce-brasil/>
- Beer and Code, faixas de engenheiro de IA no Brasil (2026) — <https://blog.beerandcode.com.br/noticias/quanto-ganha-engenheiro-de-ia-brasil-2026>

**Aviso:** todas as faixas acima vêm de agregadores e reportagens, não de
pesquisa amostral auditada. Use-as para ordem de grandeza e confirme com fontes
primárias antes de negociar.
