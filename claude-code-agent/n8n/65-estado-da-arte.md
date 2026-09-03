# 65 · Estado da arte — onde o campo está em setembro de 2026

`Nível: pesquisa` · `Pesquisado na web em 01/09/2026` · **Reavalie a cada 3 meses**

> Tudo neste arquivo tem prazo de validade. Números e afirmações valem para
> **01/09/2026** e estão datados individualmente.

---

## 1. O n8n hoje, em números verificados

| Medida | Valor | Fonte, em 01/09/2026 |
|---|---|---|
| Última versão publicada | **2.38.1** (01/09/2026) | GitHub Releases |
| Canal `stable` / `beta` | **2.36.9** / **2.37.6** | documentação oficial |
| Cadência | uma versão menor **quase toda semana** | documentação oficial |
| Estrelas no GitHub | **203.017** | API do GitHub |
| Forks | **60.488** | API do GitHub |
| Tipos de nó na instalação padrão | **910** | `n8n export:nodes` executado localmente |
| Licença | Sustainable Use License (fair-code) — o GitHub classifica como *"Other"* | `LICENSE.md` do repositório |
| Última captação | **US$ 180 mi**, Série C liderada pela Accel, avaliação de **US$ 2,5 bi** (out/2025) | PitchBook |
| Próxima grande versão | **3.0**, prevista para **outubro de 2026** | changelog oficial |

> **Nota de honestidade sobre números de mercado:** blogs de terceiros citam
> avaliações e contagens de estrelas divergentes (vi "US$ 1 bi" e "180 mil estrelas"
> em textos de 2026). Os números acima vêm da API do GitHub e da cobertura da
> rodada; se você precisar citar em algum lugar sério, **confira na fonte primária**.

---

## 2. O que muda no n8n 3.0 (outubro de 2026)

A mudança mais consequente da história do produto para quem autogere:

| Mudança | Impacto |
|---|---|
| **Instalação só por Docker** — `npm install n8n` e `npx n8n` deixam de funcionar | Todo mundo que instalou por npm precisa migrar |
| Remoção dos nós **Function**, **Function Item**, **Item Lists** | Fluxos antigos quebram |
| Remoção do **AI Agent v1** (SQL, Conversational, OpenAI Functions, Plan-and-Execute, ReAct) | **Todo tutorial de agente de 2024 fica obsoleto** |
| Remoção de `$getPairedItem` | Trocar por `$('nó').item` / `itemMatching()` |
| Remoção do **Chat Hub** e do import de workflow por URL | — |
| **Rotação de chave ligada por padrão** | Segurança melhora; atenção na operação |
| Limites de compressão reduzidos (2 GiB → **256 MiB**; 5.000 → **1.000** entradas em zip) | Fluxos que descompactam arquivos grandes quebram |
| Tratamento mais rígido de nomes de recurso e de credenciais | — |

**Leitura estratégica (opinião):** a remoção do npm não é sobre empacotamento. É a
n8n encerrando a categoria "n8n como programa que você instala" e assumindo "n8n
como serviço que você opera". Reduz drasticamente a matriz de suporte e alinha
autogestão com Cloud. É a decisão certa para a empresa e um custo real para quem
tem instalação npm em produção — e é o motivo pelo qual o
[03-instalacao.md](03-instalacao.md) deste curso trata npm como legado.

---

## 3. As quatro tendências do campo

### 3.1 A convergência automação × agentes já aconteceu

Não é mais previsão. As ferramentas de automação viraram plataformas de agentes
sem mudar de motor, porque o problema técnico é o mesmo: encadear passos, tratar
erro, manter estado, chamar ferramentas.

O que ainda **não** está resolvido, e é a fronteira real:

- **Depurar um agente.** Quando o grafo é decidido em tempo de execução por um
  modelo, o histórico de execução do n8n mostra *o que* aconteceu, mas não
  *por que* o modelo escolheu aquilo. LangSmith ajuda; não resolve.
- **Testar um agente.** Não-determinismo torna teste de regressão difícil. Os
  recursos de *evaluations* do n8n são um primeiro passo honesto.
- **Custo previsível.** Um agente com laço de raciocínio tem custo variável por
  execução. Orçar isso ainda é adivinhação.

### 3.2 A commoditização das capacidades de IA

Em 2024, "seu fluxo pode buscar na web e ler documentos" era diferencial.
Em 2026, isso é nativo dos próprios serviços de LLM (projetos, conectores, busca).
A própria n8n reconhece isso publicamente: essas capacidades viraram *table stakes*.

**O que restou como diferencial**, segundo esse mesmo argumento — e eu concordo:

1. **A parte determinística.** A capacidade de dizer "aqui **não** se raciocina,
   aqui se executa este passo exato". Ironicamente, o valor de uma plataforma de
   agentes está no que ela **impede** o modelo de decidir.
2. **Codabilidade e padrões de orquestração:** roteamento, paralelização,
   orquestrador-trabalhador, multiagente.
3. **Prontidão corporativa:** observabilidade, DLP, autenticação, RBAC, sandbox de
   agentes.

Isso valida a tese central deste curso: o valor não está em chamar um LLM — está
em **confiabilidade, tratamento de erro e idempotência** ([18](18-erros-e-confiabilidade.md)).

### 3.3 MCP: adoção real, entusiasmo em ajuste

O Model Context Protocol foi adotado rapidamente e virou padrão de fato para expor
ferramentas a modelos. O n8n suporta os dois lados (Client e Server Trigger).

Em 2026, a leitura do campo é mais sóbria: houve uma alta meteórica seguida de
correção, e o roteiro do protocolo passou a focar em **escala e governança** —
transporte HTTP sem estado, descoberta de servidores, tarefas assíncronas e
padrões multiagente, trilhas de auditoria, OAuth 2.1, comportamento de gateway.

**Tradução:** o MCP saiu da fase "que legal, funciona" e entrou na fase
"como isso é seguro e operável numa empresa". Que é exatamente onde o n8n joga.

### 3.4 A concorrência ficou séria

| Categoria | Nomes |
|---|---|
| Automação clássica | Zapier, Make, Power Automate, Workato |
| Agentes/LLM, abertos | **Dify**, **Langflow** (ambos acima de 100 mil estrelas), Flowise (adquirida pela Workday) |
| Autogeridos "code-first" | Windmill, Activepieces, Pipedream |
| Big tech | **Google Opal**, **OpenAI Agent Builder**, Microsoft Copilot Studio |

A entrada das grandes plataformas de modelos no espaço de construção de agentes é
o fato competitivo mais relevante de 2026. **Opinião profissional:** elas vão
dominar o caso "agente simples usando os dados que já estão na plataforma delas",
e vão ter dificuldade com "orquestrar 40 sistemas internos legados, com dados que
não podem sair da empresa". O segundo caso é onde o n8n é forte, e é um mercado
grande e chato — o tipo que dura.

---

## 4. O que mudou na própria ferramenta em 2026

| Mudança | Por que importa |
|---|---|
| **`Publish` separado de `Save`** (2.0) | Corrigiu uma confusão perigosa de intenção |
| **Python nativo substitui Pyodide** (2.0) | Mais rápido, mais restrito, quebra código antigo |
| **Binário fora da memória** (2.0) | Estabilidade sob carga |
| **`sqlite-pooled` padrão** (2.0) | Alivia o gargalo de escrita do SQLite |
| **Agendador durável** (2.36.0, opcional) | Agendamento sobrevive a reinício; base para multi-main sem líder |
| **Data tables** | Armazenamento estruturado nativo, sem banco externo (teto de 200 MiB) |
| **Pacotes `.n8np`** | Exportar/importar conjuntos com dependências resolvidas |
| **`n8nio/runners` obrigatório para modo externo** (2.0) | Isolamento vira decisão explícita de operação |
| **Evaluations** | Primeiro caminho oficial para testar fluxos de IA |

**Leitura de conjunto:** 2026 foi o ano em que o n8n parou de crescer em superfície
e começou a endurecer o núcleo. Todas as mudanças acima são de **operabilidade**, não
de funcionalidade nova. É o comportamento de um produto que entrou em ambientes
corporativos e passou a sentir dor de produção.

---

## 5. O que eu observaria nos próximos 12 meses

1. **Como o 3.0 é recebido em outubro de 2026.** A remoção do npm vai gerar atrito.
   Vale acompanhar o fórum e o volume de issues.
2. **Se o agendador durável vira o padrão.** Se virar, é sinal de que o n8n está se
   posicionando para implantações grandes e distribuídas.
3. **Se o RBAC desce para a edição Community.** Hoje é o maior incentivo de compra
   e a maior fonte de frustração de quem autogere.
4. **Se aparece uma resposta boa para "testar agente".** Quem resolver isso primeiro
   ganha o segmento corporativo.
5. **Se a licença muda.** Empresas com capital de risco alto e concorrência de big
   tech às vezes apertam licenças. Não há sinal disso — mas é a variável de maior
   impacto para quem constrói em cima.

---

## Autoteste

1. Qual a versão publicada, os canais `stable`/`beta` e a cadência de lançamentos?
2. Quantos tipos de nó tem a instalação padrão? Como esse número foi obtido aqui?
3. Cite cinco remoções do n8n 3.0 e o impacto de cada uma.
4. Qual a leitura estratégica da remoção do npm?
5. Quais três problemas de agentes ainda não estão resolvidos?
6. O que se comoditizou na parte de IA, e o que restou como diferencial?
7. Por que é irônico que o diferencial esteja no componente determinístico?
8. Em que fase o MCP entrou em 2026? Cite três prioridades do roteiro.
9. Onde as plataformas de big tech tendem a ganhar e onde tendem a perder?
10. Que padrão une todas as mudanças do n8n em 2026?

---

*Fontes consultadas em 01/09/2026: [GitHub API — n8n-io/n8n](https://api.github.com/repos/n8n-io/n8n),
[GitHub Releases](https://github.com/n8n-io/n8n/releases),
[docs.n8n.io — v3.0 breaking changes](https://docs.n8n.io/changelog/v30-breaking-changes),
[PitchBook — Série C](https://pitchbook.com/news/articles/ai-agent-startup-n8n-lands-2-5b-valuation-with-180m-series-c),
[n8n Blog — "We need to re-learn what AI agent development tools are in 2026"](https://blog.n8n.io/we-need-re-learn-what-ai-agent-development-tools-are-in-2026/),
[Toloka — The future of MCP: 2026 roadmap](https://toloka.ai/blog/the-future-of-mcp-enterprise-adoption/).*

*Anterior: [60-teoria-avancada.md](60-teoria-avancada.md) · Próximo: [70-pratica.md](70-pratica.md)*
