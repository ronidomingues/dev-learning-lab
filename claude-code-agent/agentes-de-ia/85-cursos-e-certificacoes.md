# 85 · Cursos gratuitos e certificações

**Nível:** todos · **Pesquisado na web em 13/08/2026**

⚠️ Links e conteúdos de vídeo mudam. Cada item traz o ano de publicação quando
foi possível apurar. Confirme antes de investir tempo — e desconfie de "curso
2026" republicado.

Ordem de prioridade: **português → inglês → francês**.

---

## 1. Português

### 1.1 Vídeo, gratuito

O ecossistema em português sobre Claude Code é recente e dominado por
criadores independentes no YouTube. A qualidade varia bastante; o critério
abaixo é o que consegui apurar por busca, não por assistir integralmente.

| Curso | Onde | Duração | Nível | Vale? |
|---|---|---|---|---|
| **Claude Code: Curso Completo do Zero ao Avançado** | YouTube ([vídeo](https://www.youtube.com/watch?v=MzMM5iV3GcU)) | ~5 h | iniciante → intermediário | O mais completo que achei em PT-BR. Bom para instalação, primeiros passos e fluxo diário. Confira a data no vídeo: material de 2025 já tem comandos removidos |
| **Curso Completo de Claude Code (+4 horas)** | YouTube ([vídeo](https://www.youtube.com/watch?v=XXZ2wOom1l0)) | ~4 h | iniciante | Formato aula longa. Foco em uso prático |
| **Curso Claude Code Gratuito para Iniciantes** | YouTube ([vídeo](https://www.youtube.com/watch?v=p5CcZd0xGz4)) e [nocodestartup.io](https://nocodestartup.io/en/curso-claude-code-gratuito/) | variável | leigo | Voltado a quem **não** programa. Útil como porta de entrada; não substitui a revisão de código |
| **Curso Completo Claude Code — Crie e Venda com IA (2026)** | YouTube ([vídeo](https://www.youtube.com/watch?v=KoFOPpUWi98)) | variável | iniciante | Viés comercial forte ("crie e venda"). Trate a parte técnica e ignore a promessa de renda |

**Espanhol** (próximo o bastante para muito brasileiro): há material bom, como
[CLAUDE CODE 2026: Curso Completo en Español](https://www.youtube.com/watch?v=73eFWU-edO4)
e [Aprende a Programar con Agentes de IA desde CERO](https://www.youtube.com/watch?v=H3gH_Fe6xvs).

**Aviso honesto sobre a Udemy.** Há vários "cursos gratuitos" de Claude Code
lá. O padrão da plataforma é: preview gratuito, curso pago; ou gratuito por
tempo limitado. Confira o preço no dia. Além disso, curso gravado sobre uma
ferramenta que muda a cada semana envelhece rápido — em agosto de 2026, um
curso gravado em janeiro já ensina comandos que foram removidos.

> **Recomendação profissional:** *em português, use vídeo para vencer o
> primeiro dia (instalar, primeira sessão, tirar o medo) e migre para a
> documentação oficial em inglês para tudo depois disso. O material em vídeo
> quase nunca cobre hooks, MCP, subagentes e permissões — que é onde está o
> valor. Este curso que você está lendo foi escrito para preencher exatamente
> essa lacuna.*

### 1.2 Texto e documentação, em português

| Recurso | O que é |
|---|---|
| [Claude Docs](https://code.claude.com/docs/) | Oficial. Só em inglês, mas é **a** fonte. Leia com tradutor se precisar |
| [Anthropic Academy](https://anthropic.skilljar.com/) | Cursos oficiais gratuitos (interface em inglês; conteúdo acessível com legenda) |
| Este curso | do zero à pesquisa, em português, com projeto executável |

---

## 2. Inglês

### 2.1 Anthropic Academy — oficial e gratuito, com certificado

[anthropic.skilljar.com](https://anthropic.skilljar.com/)

| Curso | Duração aprox. | Nível | Comentário |
|---|---|---|---|
| **Claude Code in Action** | algumas horas | iniciante → intermediário | O curso oficial do Claude Code. Comece por ele |
| **Building with the Claude API** | 84 aulas, 8+ h | intermediário | O mais completo do catálogo. Base para construir o seu agente ([19](19-agent-sdk-e-agentes-proprios.md)) |
| **Model Context Protocol (MCP)** | 2–3 h | intermediário | Cobre o que o [15](15-mcp-model-context-protocol.md) resume |
| **AI Fluency** | 4–5 h | leigo | Não técnico; bom para levar ao seu time |

Gratuitos de verdade, com certificado de conclusão. Valor de mercado: modesto,
mas é o certificado oficial do fabricante — o que conta mais que a maioria.

### 2.2 Hugging Face — AI Agents Course

[huggingface.co/learn/agents-course](https://huggingface.co/learn/agents-course)

- **Gratuito**, aberto, com **certificado gratuito**. Mais de 200 mil
  certificações emitidas até meados de 2026.
- ~30 h, 5 unidades + projeto final.
- Cobre fundamentos de agente e os frameworks Python dominantes:
  `smolagents`, LangGraph, LlamaIndex.
- **Independente de fornecedor** — é o melhor complemento a este curso,
  porque mostra o assunto fora do ecossistema Claude.

**Se você só puder fazer um curso externo, faça este.**

### 2.3 DeepLearning.AI — cursos curtos

[deeplearning.ai/short-courses](https://www.deeplearning.ai/short-courses/)

Aulas de 1 a 2 h, muitas gratuitas para assistir. Os mais relevantes aqui:

| Curso | Parceria | Assunto |
|---|---|---|
| MCP: Build Rich-Context AI Apps with Anthropic | Anthropic | MCP na prática |
| Building Code Agents with Hugging Face smolagents | Hugging Face | laço agêntico com código |
| Multi AI Agent Systems with crewAI | CrewAI | orquestração |
| AI Agents in LangGraph | LangChain | grafos de estado |
| Building Towards Computer Use with Anthropic | Anthropic | uso de computador |

Bons para ver o mesmo conceito com outro vocabulário — o que ajuda a
distinguir o que é essencial do que é jargão de framework.

### 2.4 Leitura fundamental (grátis, e melhor que a maioria dos cursos)

| Texto | Por que |
|---|---|
| [Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents) (Anthropic, dez/2024) | **Leia primeiro.** 20 minutos que valem mais que 20 horas de vídeo |
| [Claude Code best practices](https://code.claude.com/docs/en/best-practices) | práticas do fabricante |
| [Especificação do MCP](https://modelcontextprotocol.io/) | a fonte |
| [ReAct (arXiv 2210.03629)](https://arxiv.org/abs/2210.03629) | o paper fundador |
| [SWE-bench (arXiv 2310.06770)](https://arxiv.org/abs/2310.06770) | como se mede |

### 2.5 Canais consistentes

| Canal | Foco |
|---|---|
| [Anthropic no YouTube](https://www.youtube.com/@anthropic-ai) | oficial: lançamentos, sessões técnicas |
| [Hugging Face](https://www.youtube.com/@HuggingFace) | agentes e modelos abertos |
| [DeepLearning.AI](https://www.youtube.com/@Deeplearningai) | fundamentos |

---

## 3. Francês

Oferta menor e mais comercial. O que existe de gratuito e sério:

| Recurso | Onde | Comentário |
|---|---|---|
| **AI Agents Course (Hugging Face)** | [huggingface.co](https://huggingface.co/learn/agents-course) | Interface e comunidade em francês na plataforma; conteúdo em inglês. Ainda é a melhor opção |
| **Cours sur les agents IA** (Salesforce) | [salesforce.com/fr/agentforce/ai-agent-course/](https://www.salesforce.com/fr/agentforce/ai-agent-course/) | Gratuito, em francês. Introdutório e **enviesado ao Agentforce** — bom para vocabulário, ruim para prática |
| **Cours sur les LLM** (Salesforce) | [salesforce.com/fr/agentforce/llm-course/](https://www.salesforce.com/fr/agentforce/llm-course/) | Gratuito, em francês. Base de LLM e RAG |
| **Canal Yassine Sdiri** | YouTube | Muitas horas gratuitas sobre n8n e agentes de IA, em francês. Foco em automação no-code |

**Pago, para contexto** (não recomendo, mas você vai encontrar):
formações presenciais/remotas de 2 dias na França custam a partir de ~2 000 €
(Sparks, IB Formation), e o ENSAE-ENSAI oferece *Construire des agents IA
autonomes avec des outils Open Source*. Se a empresa paga via OPCO, pode fazer
sentido; para autodidata, não.

---

## 4. Certificações

**A verdade primeiro:** em agosto de 2026, **não existe certificação de agentes
de IA com valor real de mercado.** A área tem menos de dois anos de maturidade
prática, e nenhum certificado ainda funciona como filtro de contratação. O que
funciona é portfólio: um servidor MCP publicado, um agente que roda, uma
suíte de avaliação com números.

Dito isso:

| Certificação | Emissor | Custo | Valor real |
|---|---|---|---|
| **Anthropic Academy** (por curso) | Anthropic | grátis | Modesto, mas é do fabricante. **A melhor da lista** |
| **AI Agents Course** | Hugging Face | grátis | Modesto; exige projeto final, o que é um sinal melhor que prova de múltipla escolha |
| DeepLearning.AI (conclusão) | DeepLearning.AI | grátis (audit) / pago | Simbólico |
| Certificações de nuvem com trilha de agentes (AWS, Google, Microsoft) | os provedores | US$ 100–300 | Reconhecidas **para a nuvem**, não para agentes especificamente |
| "Certified AI Agent Developer" de plataformas diversas | vários | US$ 50–500 | ⚠️ Sem valor de mercado apurável. Evite |

> **Opinião, sem meio-termo:** *pagar por certificação de agentes de IA em 2026
> é desperdício. Faça os gratuitos (Anthropic Academy e Hugging Face) porque o
> conteúdo é bom — o certificado é subproduto. Invista o dinheiro em créditos
> de API e construa algo.*

---

## 5. Trilha recomendada

**Semana 1 — funcionar**
1. Este curso: [01](01-introducao-leigo.md) → [05](05-manual-de-uso.md)
2. *Building Effective Agents* (20 min)
3. Um vídeo em PT para destravar a instalação, se precisar
4. Labs 1–3 do [70](70-pratica.md)

**Semanas 2–3 — entender**
5. Este curso: [10](10-fundamentos.md) → [14](14-contexto-memoria-compactacao.md)
6. Anthropic Academy: *Claude Code in Action*
7. Labs 4–8

**Semanas 4–6 — estender**
8. Este curso: [15](15-mcp-model-context-protocol.md) →
   [18](18-skills-plugins-extensibilidade.md)
9. Anthropic Academy: *MCP*
10. Labs 9 e 11; [projeto-modelo](07-projeto-modelo/README.md) inteiro

**Meses 2–3 — construir**
11. Hugging Face AI Agents Course (~30 h)
12. Este curso: [19](19-agent-sdk-e-agentes-proprios.md) e
    [20](20-avaliacao-e-benchmarks.md)
13. Labs 10, 12, 13, 14
14. Publique um servidor MCP

**Contínuo**
15. [65-estado-da-arte.md](65-estado-da-arte.md) a cada dois meses
16. Changelog do Claude Code (`/release-notes`)
17. Um paper por mês de [95-referencias.md](95-referencias.md)

---

## Autoteste

1. Qual é a melhor opção gratuita em inglês, e por que ela é a melhor
   **complementar** a este curso?
2. Por que curso gravado sobre Claude Code envelhece tão rápido?
3. Qual leitura de 20 minutos vale mais que 20 horas de vídeo, e por quê?
4. Existe certificação de agentes com valor de mercado em ago/2026? O que
   funciona no lugar?
5. Você tem 6 semanas e 10 h por semana. Descreva a sua trilha.
6. Por que os cursos franceses da Salesforce são "bons para vocabulário e
   ruins para prática"?

---

**Fontes consultadas em 13/08/2026:** buscas na web em português, inglês e
francês (YouTube, Udemy, Anthropic Academy, Hugging Face, DeepLearning.AI,
Salesforce FR, Jedha, ENSAE-ENSAI, Sparks, IB Formation); páginas oficiais dos
cursos citados.
