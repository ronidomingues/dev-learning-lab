# 11 · História — como o MCP surgiu e por que virou o que é

`Nível: intermediário` · `Escrito em 01/09/2026`

História técnica não é enfeite. Quase toda decisão estranha do MCP tem uma data e um
problema por trás. Quem sabe a história prevê a próxima mudança.

---

## 1. O que existia antes, e por que não bastava

### 1.1 Plugins de ChatGPT (março de 2023)

O primeiro esforço sério de dar ferramentas a um LLM. O desenvolvedor publicava um
`ai-plugin.json` e uma spec OpenAPI; o modelo lia e chamava.

Por que morreu:

- **preso a um fornecedor.** O plugin só funcionava no ChatGPT.
- **só HTTP público.** Não havia como expor a sua pasta local nem o banco na sua rede.
- **descoberta estática.** A lista era carregada uma vez, não em tempo de execução.
- **OpenAPI é grande demais.** Specs reais tinham centenas de endpoints e enchiam o
  contexto antes de qualquer conversa.

Lição herdada pelo MCP: **descoberta em tempo de execução, com lista pequena e
transporte local de primeira classe.**

### 1.2 *Function calling* (junho de 2023)

A OpenAI publicou o mecanismo de o modelo pedir uma função com argumentos em JSON.
Anthropic, Google e os demais seguiram. Funciona bem — e continua sendo a base.

O que ele **não** resolve: de onde vêm as funções. Cada aplicação escrevia o seu
catálogo à mão, no seu formato, com o seu carregamento. Voltamos ao problema M×N.

MCP é, literalmente, **a camada de descoberta e transporte que falta ao function
calling**. Não é substituto: é complemento.

### 1.3 LSP — Language Server Protocol (2016, Microsoft)

O antepassado direto, e o MCP não esconde isso. O LSP resolveu exatamente o mesmo
formato de problema no mundo dos editores: M editores × N linguagens = M×N plugins de
autocompletar. Depois do LSP, M+N.

O que o MCP copiou do LSP, quase literalmente:

- **JSON-RPC 2.0** como base;
- **negociação de capacidades** na abertura;
- servidor como **processo separado** falando por stdio;
- a ideia de que o cliente (editor/host) manda no ciclo de vida.

O que o MCP mudou, e por quê: no LSP o cliente é determinístico (o editor sabe quando
pedir autocompletar). No MCP o cliente é um **modelo estatístico**, que decide sozinho.
Isso obrigou a acrescentar aprovação humana, descrições em linguagem natural e schemas
para o modelo ler.

---

## 2. A linha do tempo

| Data | Evento |
|---|---|
| **05/11/2024** | data da primeira revisão da especificação: `2024-11-05` |
| **25/11/2024** | Anthropic anuncia e abre o código do MCP. Autores: **David Soria Parra** e **Justin Spahr-Summers** |
| **26/03/2025** | revisão `2025-03-26` |
| **Março/2025** | **OpenAI adota o MCP** no ChatGPT Desktop e na API. Ponto de virada |
| **Abril/2025** | Google DeepMind confirma suporte no Gemini |
| **18/06/2025** | revisão `2025-06-18` |
| **2025** | Microsoft, AWS, Cloudflare e Bloomberg entram como apoiadores |
| **25/11/2025** | revisão `2025-11-25` — um ano de MCP |
| **09/12/2025** | **Anthropic doa o MCP à Agentic AI Foundation** (Linux Foundation), cofundada com Block e OpenAI. Mais de 10.000 servidores ativos |
| **28/07/2026** | revisão `2026-07-28` — a maior reescrita: protocolo **sem estado** |
| **22/08/2026** | novo roadmap publicado pelos mantenedores |

---

## 3. Revisão por revisão — o que mudou e **por quê**

### 3.1 `2024-11-05` — o começo

Traz o essencial: JSON-RPC, handshake `initialize`, capacidades, tools, resources,
prompts, sampling, roots, transporte **stdio** e transporte **HTTP+SSE**.

O HTTP+SSE usava **dois endpoints**: um `GET` que abria um fluxo SSE e devolvia, no
primeiro evento, o endereço de um `POST` para o cliente mandar mensagens. Funcionava,
mas exigia conexão longa desde o primeiro instante — inviável em *serverless*, ruim
atrás de balanceador, impossível em CDN.

### 3.2 `2025-03-26` — profissionalização

Mudanças maiores:

1. **Framework de autorização** completo, baseado em **OAuth 2.1**.
2. **Streamable HTTP** substitui o HTTP+SSE: **um** endpoint, cada mensagem é um POST, e
   a resposta pode ser JSON simples ou um fluxo SSE.
3. **Batching de JSON-RPC** (que duraria 3 meses).
4. **Anotações de ferramenta** — dizer se é somente-leitura, se é destrutiva.

Outras: campo `message` em `ProgressNotification`; conteúdo de **áudio**; capacidade
`completions` explícita.

**Por que Streamable HTTP:** para um servidor MCP remoto poder ser um *serviço HTTP
comum*. Sem conexão longa obrigatória, ele roda em Lambda, em Cloud Run, atrás de
qualquer balanceador. Foi a mudança que tornou MCP remoto viável comercialmente.

### 3.3 `2025-06-18` — segurança e estrutura

1. **Remoção do batching** — 3 meses depois de acrescentado.
2. **Saída estruturada de ferramenta** (`structuredContent`, `outputSchema`).
3. Servidores MCP classificados como **OAuth Resource Servers**, com *Protected Resource
   Metadata* (RFC 9728) para descobrir o servidor de autorização.
4. **Resource Indicators (RFC 8707) obrigatórios** no cliente, para impedir que um
   servidor malicioso obtenha token destinado a outro.
5. Página nova de **boas práticas de segurança**.
6. **Elicitação**: o servidor pode perguntar algo ao usuário no meio da operação.
7. **Resource links** em resultado de ferramenta.
8. Cabeçalho **`MCP-Protocol-Version`** obrigatório em HTTP.
9. `SHOULD` → `MUST` na operação do ciclo de vida.
10. Campo `title` separado de `name` — nome para humano × identificador programático.

**Por que o batching durou três meses.** Ele complicava o transporte (uma resposta HTTP
podia carregar N respostas, algumas em erro), complicava o cancelamento e a correlação,
e o ganho era desprezível: o gargalo de um agente é a latência do **modelo**, não o
número de viagens HTTP. Este é um exemplo raro e saudável de padrão **removendo** algo
cedo, em vez de carregá-lo por uma década.

### 3.4 `2025-11-25` — o primeiro aniversário

1. Descoberta do servidor de autorização com **OpenID Connect Discovery 1.0**.
2. **Ícones** para tools, resources, templates e prompts.
3. **Consentimento incremental de escopo** via `WWW-Authenticate` (*step-up*).
4. Orientação sobre **nomes de ferramenta**.
5. `ElicitResult`/`EnumSchema` refeitos: enums com e sem título, seleção única e múltipla.
6. **Elicitação em modo URL** — para senha, chave de API, pagamento, que **não podem**
   passar pelo cliente.
7. **Tool calling dentro de sampling** (`tools`, `toolChoice`).
8. **OAuth Client ID Metadata Documents** como registro recomendado de cliente.
9. **Tasks experimentais** — requisições duráveis com polling.

Menores relevantes: `stderr` liberado para log de qualquer nível no stdio; **HTTP 403**
obrigatório para `Origin` inválido; erro de validação de entrada deve ser **erro de
execução**, não de protocolo, para o modelo se autocorrigir; JSON Schema **2020-12**
como dialeto padrão.

Governança: estrutura formalizada, Working Groups e Interest Groups criados, e um
**sistema de tiers para SDKs**.

### 3.5 `2026-07-28` — a reescrita

A maior mudança desde a criação. Em uma frase: **o MCP deixou de ter sessão.**

Removido:

- **sessões de protocolo** e o cabeçalho `Mcp-Session-Id`;
- o **handshake `initialize`** e `notifications/initialized`;
- o **endpoint GET** e `resources/subscribe`/`unsubscribe`;
- **`ping`**, `logging/setLevel`, `notifications/roots/list_changed`;
- **retomada de SSE** (`Last-Event-ID`) e reentrega de mensagem;
- **requisições iniciadas pelo servidor**.

Acrescentado:

- **`server/discover`**, que todo servidor **deve** implementar;
- **`_meta` por requisição** com versão, capacidades e identidade do cliente;
- **`subscriptions/listen`** — um fluxo longo só, com filtro e confirmação;
- **MRTR** — `InputRequiredResult`, `inputRequests`, `inputResponses`, `requestState`;
- **`resultType`** obrigatório em todo resultado;
- cabeçalhos `Mcp-Method` e `Mcp-Name` obrigatórios, e `x-mcp-header` para parâmetro;
- **`ttlMs` e `cacheScope`** obrigatórios nos resultados de listagem e leitura;
- propagação de contexto **OpenTelemetry** em `_meta`;
- campo `extensions` nas capacidades;
- **política de ciclo de vida** com janela mínima de 12 meses para depreciação.

Depreciado: **Roots, Sampling e Logging**; HTTP+SSE reclassificado; DCR (RFC 7591) em
favor de CIMD.

---

## 4. Os cinco porquês da grande virada de 2026

Pergunta: **por que remover a sessão?**

1. **Por que remover a sessão?** Porque um servidor com sessão precisa de *afinidade de
   sessão* no balanceador — a segunda requisição tem de cair na mesma réplica que atendeu
   a primeira.
2. **Por que isso é um problema?** Porque quebra escala horizontal comum. Não se pode
   pôr o servidor atrás de um ALB comum, nem rodá-lo em *serverless*, nem reiniciar uma
   réplica sem derrubar conversas.
3. **Por que isso importou agora e não em 2024?** Porque em 2024 o servidor típico era
   local, stdio, um processo por usuário. Em 2026 o servidor típico é **remoto,
   multiusuário e comercial**. O que era irrelevante virou o custo dominante.
4. **Por que não bastava tornar a sessão opcional?** Porque o cliente teria de suportar
   os dois modos e o servidor não poderia contar com nenhum — a complexidade fica nos dois
   lados, e o pior de dois mundos vira o padrão. Um protocolo escolhe.
5. **Por que remover *também* as requisições iniciadas pelo servidor?** Porque elas
   **exigem** um canal de volta, e canal de volta é estado de conexão. Sem sessão, não há
   onde ancorá-lo. Daí o MRTR: o servidor "pergunta" devolvendo um resultado, e o cliente
   pergunta de novo — cada requisição continua autossuficiente.

**Parada legítima:** um trade-off econômico e operacional explícito. Trocou-se
simplicidade de escrita do servidor (agora ele precisa gerir `requestState` cifrado)
por operabilidade em infraestrutura HTTP padrão. Não é uma verdade técnica eterna; é
uma escolha, e ela está documentada em [SEP-2575](https://modelcontextprotocol.io/seps/2575-stateless-mcp)
e [SEP-2322](https://modelcontextprotocol.io/seps/2322-MRTR).

---

## 5. Por que o MCP venceu, e o que quase o matou

### 5.1 Por que venceu

Em ordem de peso, opinião fundamentada:

1. **O problema doía e era universal.** M×N não é abstração: era o quinto conector de
   GitHub que a mesma pessoa escrevia no mesmo semestre.
2. **A barreira de entrada é ridícula.** 20 linhas para um servidor útil.
3. **Um concorrente adotou cedo.** Quando a OpenAI adotou, em março de 2025, MCP deixou
   de ser aposta e virou caminho seguro. Padrões vencem por **efeito de rede**, não por
   mérito técnico — e quem esquece isso escreve o padrão tecnicamente melhor que ninguém usa.
4. **A doação à Linux Foundation** (09/12/2025) tirou o último argumento de quem dizia
   "é da Anthropic". Isso importou para adoção corporativa mais do que qualquer recurso.
5. **SDKs oficiais em muitas linguagens**, com sistema de tiers e compromisso de manutenção.

### 5.2 O que quase o matou

- **Autorização.** Foi a parte mais dolorosa e a que mais mudou (2025-03-26 → 2025-06-18
  → 2025-11-25 → 2026-07-28, quatro revisões consecutivas). Muita gente desistiu do
  servidor remoto e ficou no stdio.
- **Segurança.** *Tool poisoning*, *line jumping*, *rug pull*: abril de 2025 trouxe as
  primeiras provas de conceito públicas, e a imprensa técnica pegou pesado. O ecossistema
  respondeu com página de boas práticas, política de moderação no registry e verificação
  de namespace — mas o problema de fundo (o modelo confia no texto que lê) **não tem
  solução dentro do protocolo**.
- **Instabilidade.** Cinco revisões em vinte meses, com remoções. Quem escreveu servidor
  em 2024 reescreveu em 2026. A **política de ciclo de vida** de `2026-07-28`, com janela
  de doze meses, é a resposta institucional a essa reclamação.
- **Contexto.** Servidores com 60 ferramentas cada, três instalados, e a janela do modelo
  acabava antes da conversa. Isso motivou o trabalho de *progressive discovery* no roadmap
  atual.

---

## 6. As pessoas e as instituições

| Quem | Papel |
|---|---|
| **David Soria Parra** | coautor do MCP (Anthropic); hoje Core Maintainer, área de SDK |
| **Justin Spahr-Summers** | coautor do MCP (Anthropic) |
| **Agentic AI Foundation (AAIF)** | dona do projeto desde 09/12/2025; parte da Linux Foundation |
| **Anthropic, Block, OpenAI** | cofundadores da AAIF |
| **Google, Microsoft, AWS, Cloudflare, Bloomberg** | apoiadores |
| **Core Maintainers** | Caitie McCaffrey, Clare Liguori, Peter Alexander, Kurtis Van Gent, Nick Cooper, Paul Carleton, Den Delimarsky, David Soria Parra |
| **Working Groups** | Agents, File Uploads, Inspector V2, Interceptors, Registry, SDK, Server Card, Skills Over MCP, Transports, Triggers & Events |
| **Interest Groups** | Authorization, Enterprise, Enterprise-Managed Authorization, Financial Services, Primitive Grouping, Security, Tool Annotations |

Projetos irmãos na AAIF: **goose** (Block) e **AGENTS.md** (OpenAI).

---

## 7. O que a história ensina sobre o futuro

Três padrões observáveis, com previsão explicitamente marcada como opinião:

1. **O protocolo remove tanto quanto acrescenta.** Batching durou 3 meses; sessões
   duraram 20. **Opinião:** Sampling, Roots e Logging — hoje depreciados — saem por
   volta de 2027-2028, respeitada a janela de 12 meses.
2. **A pressão vem do uso corporativo remoto.** Toda mudança grande desde 2025-03-26
   veio de "isto não funciona atrás de um balanceador / com um IdP / numa auditoria".
   **Opinião:** identidade de agente e DPoP são o próximo campo de batalha, e o roadmap
   de agosto de 2026 diz exatamente isso.
3. **O que não muda é o núcleo.** JSON-RPC, três primitivas, negociação de capacidades e
   os quatro princípios de projeto sobreviveram a todas as revisões. **Opinião:** quem
   investe tempo entendendo *isso* não perde o investimento; quem decora o formato do
   handshake, sim.

---

## 8. Autoteste

1. Que problema o LSP resolveu, e o que o MCP copiou dele? O que precisou mudar, e por quê?
2. Por que os plugins de ChatGPT não viraram padrão? Cite dois motivos estruturais.
3. Qual a relação entre *function calling* e MCP — concorrentes ou complementares?
4. Por que o batching de JSON-RPC foi acrescentado e removido em três meses?
5. Aplique os cinco porquês à remoção das sessões em `2026-07-28`. Onde está a parada legítima?
6. Por que remover as sessões obrigou a remover também as requisições iniciadas pelo servidor?
7. Qual evento de março de 2025 foi o ponto de virada, e por quê?
8. O que mudou com a doação à Agentic AI Foundation — tecnicamente e politicamente?
9. Cite três coisas que quase mataram a adoção do MCP.
10. Qual parte do MCP sobreviveu intacta a todas as revisões?

---

**Anterior:** [10 · Fundamentos](10-fundamentos.md) · **Próximo:** [12 · Arquitetura](12-arquitetura.md) · **Índice:** [00-MAPA](00-MAPA.md)

*Fontes: changelogs oficiais de [2025-03-26](https://modelcontextprotocol.io/specification/2025-03-26/changelog),
[2025-06-18](https://modelcontextprotocol.io/specification/2025-06-18/changelog),
[2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25/changelog) e
[2026-07-28](https://modelcontextprotocol.io/specification/2026-07-28/changelog);
[Anthropic — doação do MCP (09/12/2025)](https://www.anthropic.com/news/donating-the-model-context-protocol-and-establishing-of-the-agentic-ai-foundation);
[Linux Foundation — AAIF](https://www.linuxfoundation.org/press/linux-foundation-announces-the-formation-of-the-agentic-ai-foundation);
[Roadmap de 22/08/2026](https://modelcontextprotocol.io/development/roadmap);
[Wikipédia — Model Context Protocol](https://en.wikipedia.org/wiki/Model_Context_Protocol).
Consultas em 01/09/2026.*
