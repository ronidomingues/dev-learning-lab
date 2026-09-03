# Glossário — MCP

`Atualizado em 01/09/2026` · `Protocolo 2026-07-28`

Termos em ordem alfabética. Quando o campo usa o termo em inglês, ele vem primeiro,
com a tradução ao lado. ⚠️ marca o que está **depreciado ou removido**.

---

## A

**AAIF · Agentic AI Foundation** — Fundação da Linux Foundation que é dona do MCP desde
09/12/2025. Cofundada por Anthropic, Block e OpenAI. Abriga também goose e AGENTS.md.

**AEAD** — *Authenticated Encryption with Associated Data*. Cifra que garante
confidencialidade **e** integridade. A spec recomenda AEAD (ou HMAC) para proteger o
`requestState`. Ver [16 §1.4](16-primitivas-do-cliente.md).

**Annotations** (anotações) — Dicas opcionais em ferramentas (`readOnlyHint`,
`destructiveHint`) e em conteúdo (`audience`, `priority`, `lastModified`). ⚠️ **Clientes
DEVEM tratá-las como não confiáveis**, salvo vindas de servidor confiável.

**AS · Authorization Server** — Servidor de autorização OAuth. Emite os tokens. Pode ser
o mesmo serviço do servidor MCP ou uma entidade separada.

**`aud` (audience)** — Claim do token que diz para quem ele foi emitido. **Validar a
audiência é a regra mais dura da spec de autorização.**

---

## B

**Batching** ⚠️ — Envio de várias mensagens JSON-RPC num array. Acrescentado em
`2025-03-26`, **removido** em `2025-06-18`.

**Binding** — Ver *Transporte*.

---

## C

**`cacheScope`** — Campo obrigatório nos resultados de listagem e leitura. `"public"` ou
`"private"`: se um intermediário compartilhado pode cachear. **Use `"private"` sempre que
o conteúdo variar com a autorização.**

**Capability** (capacidade) — Declaração do que uma parte sabe fazer. O servidor declara
em `server/discover`; o cliente declara em `_meta` de **cada** requisição. Nada pode ser
usado sem declaração prévia.

**CIMD · Client ID Metadata Documents** — Mecanismo recomendado de registro de cliente
OAuth desde `2025-11-25`: o `client_id` é uma **URL HTTPS** que serve um documento JSON
com os metadados. Substitui o DCR.

**Cliente (Client)** — Componente criado pelo host, **um por servidor**, relação 1:1.
Mantém a fronteira de isolamento entre servidores.

**Confused deputy** (delegado confuso) — Ataque em que um programa com autoridade ampla é
induzido a usá-la a serviço da designação de outro. Descrito por Norm Hardy em 1988.
No MCP, ataca proxies com `client_id` estático. Ver [19 §2](19-seguranca.md).

**`content`** — Campo do resultado de ferramenta com conteúdo **não estruturado**: `text`,
`image`, `audio`, `resource_link`, `resource`.

---

## D

**DCR · Dynamic Client Registration** ⚠️ — RFC 7591. Registro dinâmico de cliente OAuth.
**Depreciado** em `2026-07-28` em favor de CIMD; mantido por compatibilidade. É peça
central do ataque de confused deputy.

**Deprecated** (depreciado) — Estado do ciclo de vida: continua funcionando, **novas
implementações não devem adotar**, elegível para remoção após no mínimo **doze meses**.

**Descoberta em tempo de execução** — Propriedade central do MCP: o catálogo de
capacidades é lido a cada sessão, não compilado.

**`DiscoverResult`** — Resultado de `server/discover`: `supportedVersions`, `capabilities`,
`instructions` e `serverInfo`.

**DPoP** — *Demonstrating Proof of Possession*. Prova criptográfica de posse da chave
ligada ao token. Prioridade do roadmap de 22/08/2026.

**Dual-era** — Implementação que suporta tanto o protocolo **moderno** (`2026-07-28`+)
quanto o **legado** (`initialize`).

---

## E

**Elicitação (Elicitation)** — Primitiva de cliente pela qual o servidor pede informação
ao usuário. Dois modos: **formulário** (dado estruturado, passa pelo cliente) e **URL**
(interação fora de banda, para dado sensível). A única primitiva de cliente **ativa**.

**Era** — Ver *Legado* e *Moderno*.

**Erro de execução (Tool Execution Error)** — Falha reportada no `result`, com
`isError: true`. O modelo **consegue** se corrigir a partir dela. Inclui validação de
entrada, desde `2025-11-25`.

**Erro de protocolo (Protocol Error)** — Falha reportada no `error` do JSON-RPC. O modelo
dificilmente se corrige a partir dela.

**Extensão** — Adição opcional ao núcleo, identificada por `{prefixo}/{nome}`, negociada
pelo campo `extensions` das capacidades. **Sempre desativada por padrão.** Oficiais:
MCP Apps, Tasks, e as de autorização.

---

## F

**FastMCP** ⚠️ — Nome da classe de alto nível do SDK Python **v1**. Renomeada para
`MCPServer` no v2. Importar `mcp.server.fastmcp` no v2 levanta `ModuleNotFoundError` com
a mensagem de migração.

---

## H

**Handle** (identificador de estado) — String opaca que o servidor cunha e devolve, e que
o cliente passa de volta como argumento comum, para relacionar chamadas. **Não é
capacidade nem autenticação**: valide a autorização a cada uso e ligue ao usuário
autenticado.

**`HeaderMismatch` (`-32020`)** — Erro quando um cabeçalho HTTP `Mcp-*` não bate com o
corpo, ou falta. Resposta HTTP: `400`.

**Host (anfitrião)** — O aplicativo com que o usuário conversa. Fala com o LLM, cria os
clientes, **aplica as políticas de segurança e o consentimento**.

**HTTP+SSE** ⚠️ — Transporte de `2024-11-05`, com dois endpoints. Depreciado desde
`2025-03-26`, reclassificado como *Deprecated* em `2026-07-28`.

---

## I

**Idempotência** — Propriedade de a operação repetida ter o mesmo efeito da primeira.
**Obrigatória em escrita**, porque o modelo repete chamadas.

**`initialize`** ⚠️ — Handshake das revisões até `2025-11-25`. **Removido** em
`2026-07-28`. Hoje o metadado vai em `_meta` de cada requisição.

**`inputRequests` / `inputResponses`** — Mapas do MRTR. O servidor pede (`inputRequests`);
o cliente responde nas mesmas chaves (`inputResponses`) ao **repetir** a requisição.

**`InputRequiredResult`** — Resultado com `resultType: "input_required"`, contendo
`inputRequests` e/ou `requestState`.

**`inputSchema`** — JSON Schema dos parâmetros da ferramenta. **DEVE** ser objeto válido,
nunca `null`.

**`instructions`** — Texto do servidor, na `DiscoverResult`, que ensina ao modelo a
**ordem** e a política de uso do conjunto de ferramentas. Subutilizado e muito útil.

**`isError`** — Booleano no resultado de ferramenta. `true` = erro de execução.

---

## J

**JSON-RPC 2.0** — A moldura de toda mensagem MCP. Três formas: requisição, resposta,
notificação. Herdada do LSP.

---

## L

**Legado (Legacy)** — Versões do protocolo que estabelecem sessão com `initialize`:
`2025-11-25` e anteriores.

**Line jumping** — Ataque em que a descrição maliciosa de uma ferramenta influencia o
modelo **antes** de qualquer ferramenta ser chamada — basta o servidor estar conectado.

**`listChanged`** — Subcapacidade que indica se o servidor emitirá notificação quando a
lista de ferramentas, recursos ou prompts mudar.

**LSP · Language Server Protocol** — Protocolo da Microsoft (2016) que resolveu o mesmo
problema M×N para editores. Antepassado direto do MCP: JSON-RPC, capacidades, servidor
como processo separado.

---

## M

**M×N (problema)** — Com M clientes e N serviços, sem padrão você escreve M×N
integrações; com padrão, M+N.

**`Mcp-Method` / `Mcp-Name`** — Cabeçalhos HTTP obrigatórios que espelham `method` e
`params.name`/`params.uri`. Existem para intermediários rotearem sem abrir o corpo.
Divergência do corpo → `400` + `-32020`.

**`MCP-Protocol-Version`** — Cabeçalho HTTP obrigatório, igual ao
`_meta.io.modelcontextprotocol/protocolVersion`.

**`Mcp-Param-{Nome}`** — Cabeçalho gerado a partir de propriedade anotada com
`x-mcp-header`.

**`Mcp-Session-Id`** ⚠️ — Cabeçalho de sessão das revisões `2025-03-26` a `2025-11-25`.
**Removido**. Servidores novos devem **ignorá-lo**.

**MCP Apps** — Extensão `io.modelcontextprotocol/ui`. UI HTML interativa renderizada
dentro da conversa, em iframe isolado, comunicando por `postMessage`.

**`MCPServer`** — Classe de alto nível do SDK Python **v2** (`mcp.server.mcpserver`).
Antes chamada `FastMCP`.

**`_meta`** — Campo que carrega o metadado de protocolo. Prefixos cujo segundo rótulo seja
`modelcontextprotocol` ou `mcp` são **reservados**.

**`MissingRequiredClientCapability` (`-32021`)** — Erro quando o servidor precisa de uma
capacidade que o cliente não declarou. `data.requiredCapabilities` lista o que falta.

**Mix-up (ataque de)** — Um AS malicioso induz o cliente a lhe enviar um código emitido
por um AS honesto. Mitigado pela validação de `iss` (RFC 9207). **PKCE não previne.**

**Moderno (Modern)** — Versões que levam versão, identidade e capacidades como metadado
**por requisição**: `2026-07-28` e posteriores.

**MRTR · Multi Round-Trip Requests** — Padrão que substitui as requisições iniciadas pelo
servidor. O servidor devolve `input_required`; o cliente **repete** a requisição com as
respostas e o `requestState` ecoado, com **`id` novo**.

---

## N

**`NoBackChannelError`** — Erro do SDK Python quando alguém tenta enviar requisição do
servidor ao cliente sob `2026-07-28`. Não é bug: **não existe canal de volta**.

**Notificação** — Mensagem JSON-RPC sem `id`, sem resposta. Cliente→servidor: só
`notifications/cancelled`, e só em stdio.

---

## O

**OAuth 2.1** — Base da autorização MCP em HTTP. PKCE obrigatório, sem *implicit*, sem
*password grant*.

**`outputSchema`** — JSON Schema opcional do resultado estruturado. ⚠️ No SDK Python 2.x,
retorno anotado como `dict` cru **não** o gera.

---

## P

**PKCE** — *Proof Key for Code Exchange*. Obrigatório no OAuth 2.1. Previne interceptação
do código de autorização; **não** previne mix-up.

**PRM · Protected Resource Metadata** — RFC 9728. Documento pelo qual o servidor MCP
aponta o seu servidor de autorização. **Servidores MCP DEVEM implementar.**

**Prompt** — Primitiva **controlada pelo usuário**: um roteiro que o servidor oferece e o
usuário escolhe (tipicamente comando de barra).

---

## R

**`requestState`** — String **opaca** que o servidor devolve num `InputRequiredResult` e
que o cliente **DEVE** ecoar idêntica, sem inspecionar. O servidor **DEVE** tratá-la como
entrada de atacante: HMAC ou AEAD, com principal, TTL e vínculo à requisição.

**Resource (recurso)** — Primitiva **controlada pela aplicação**: dado identificado por
URI que o host ou o usuário escolhe incluir.

**`resource` (parâmetro OAuth)** — RFC 8707. Identifica o servidor MCP alvo do token.
**DEVE** ir na autorização **e** no token, mesmo que o AS não suporte.

**`resource_link`** — Tipo de conteúdo que **aponta** para um recurso em vez de embuti-lo.
A ferramenta subutilizada mais útil do MCP para economizar contexto.

**`resultType`** — Campo obrigatório de todo resultado: `"complete"` ou
`"input_required"` (ou definido por extensão). **Ausente = tratar como `"complete"`.**

**Roots** ⚠️ — Primitiva de cliente que informava diretórios em que o servidor pode
operar. **Depreciada** em `2026-07-28`. Nunca foi controle de acesso: era uma dica.

**Rug pull** — Ataque em que o servidor apresenta uma ferramenta benigna, ganha aprovação,
e muda a definição depois. Relacionado à **CVE-2025-54136** ("MCPoison").

---

## S

**Sampling** ⚠️ — Primitiva pela qual o servidor pedia uma inferência do LLM do host.
**Depreciada** em `2026-07-28`. Migração: chamar a API do provedor diretamente.

**SEP · Specification Enhancement Proposal** — Proposta de mudança na spec. Fluxo baseado
em PR, com patrocinador, status por rótulo e revisão dos Core Maintainers.

**`server/discover`** — RPC que **todo servidor DEVE implementar**. Devolve versões
suportadas, capacidades e identidade. A melhor sonda de saúde para servidor MCP.

**Servidor (Server)** — Programa que expõe ferramentas, recursos e prompts. Local
(subprocesso) ou remoto (serviço HTTP). Nunca vê a conversa.

**Sem estado (Stateless)** — Propriedade central desde `2026-07-28`: toda informação
necessária está na própria requisição. *Uma conexão aberta não é uma conversa.*

**SSE · Server-Sent Events** — Formato de fluxo unidirecional sobre HTTP, usado nas
respostas em fluxo e no `subscriptions/listen`. ⚠️ Não é retomável desde `2026-07-28`.

**SSRF · Server-Side Request Forgery** — Ataque em que se induz um servidor (ou cliente)
a buscar uma URL escolhida pelo atacante. Vetor clássico na descoberta OAuth do MCP; alvo
canônico: `http://169.254.169.254/`.

**stdio** — Transporte em que o cliente lança o servidor como subprocesso e conversa por
`stdin`/`stdout`, uma mensagem JSON por linha. `stderr` é livre para log de qualquer nível.

**`structuredContent`** — Campo do resultado de ferramenta com **qualquer valor JSON**
conforme o `outputSchema`. No objeto Python do SDK v2 chama-se `structured_content`.
**Nada a ver** com "structured outputs" de LLM.

**`subscriptions/listen`** — Requisição cuja resposta é um fluxo longo de notificações,
com filtro por tipo. Substituiu o endpoint GET e `resources/subscribe`.

---

## T

**Tasks** — Extensão `io.modelcontextprotocol/tasks` para operações longas: o servidor
devolve um `taskId` durável; o cliente faz polling com `tasks/get`, responde entrada com
`tasks/update` e cancela com `tasks/cancel`. Estados: `working`, `input_required`,
`completed`, `failed`, `cancelled`.

**Token passthrough** — Anti-padrão **proibido**: aceitar token não emitido para o
servidor MCP, ou repassá-lo intacto a jusante.

**Tool (ferramenta)** — Primitiva **controlada pelo modelo**, com aprovação humana. Um
verbo. É, de longe, a primitiva mais suportada.

**Tool poisoning** — Injeção de instruções maliciosas na descrição da ferramenta. Primeira
prova de conceito pública: Invariant Labs, abril de 2025.

**Tool shadowing** — Um servidor descreve as suas ferramentas de modo a alterar como o
modelo usa as de **outro** servidor.

**Transporte (binding)** — Define enquadramento, entrega, onde vive o metadado e como se
cancela. **Não** define o significado das mensagens. Padrões: stdio e Streamable HTTP.

**`ttlMs`** — Dica de frescor, em milissegundos, obrigatória nos resultados de listagem e
leitura. `0` = não cacheie.

---

## U

**`UnsupportedProtocolVersion` (`-32022`)** — Erro quando o servidor não fala a versão
pedida. `data.supported` lista as que ele fala.

---

## X

**`x-mcp-header`** — Anotação numa propriedade do `inputSchema` que faz o cliente espelhar
o valor num cabeçalho `Mcp-Param-{Nome}`. Só tipos primitivos (não `number`), só
propriedades estaticamente alcançáveis. ⚠️ **Nunca** em parâmetro sensível.

---

## Códigos de erro, em resumo

| Código | Nome |
|---|---|
| `-32700` | Parse error |
| `-32600` | Invalid Request |
| `-32601` | Method not found |
| `-32602` | Invalid params · **recurso não encontrado** |
| `-32603` | Internal error |
| `-32020` | `HeaderMismatch` |
| `-32021` | `MissingRequiredClientCapability` |
| `-32022` | `UnsupportedProtocolVersion` |
| `-32002` ⚠️ | recurso não encontrado (até `2025-11-25`; **aceitar**, não emitir) |
| `-32042` ⚠️ | elicitação por URL (só `2025-11-25`) |

**Faixas:** `-32000`–`-32019` legado (não alocar) · `-32020`–`-32099` reservado à spec ·
códigos seus fora de `-32768`–`-32000`.

---

**Índice:** [00-MAPA](00-MAPA.md) · **Referências:** [95](95-referencias.md)
