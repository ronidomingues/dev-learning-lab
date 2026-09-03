# 05 · Manual de uso — referência consultável

`Nível: intermediário` · `Atualizado em 01/09/2026` · `Protocolo 2026-07-28`

Organizado **por tarefa**, não por ordem alfabética. Use o sumário.

---

## Sumário

1. [Métodos do protocolo](#1-métodos-do-protocolo)
2. [Campos `_meta` reservados](#2-campos-_meta-reservados)
3. [Códigos de erro](#3-códigos-de-erro)
4. [Cabeçalhos HTTP](#4-cabeçalhos-http)
5. [SDK Python — receituário](#5-sdk-python--receituário)
6. [SDK TypeScript — receituário](#6-sdk-typescript--receituário)
7. [CLI `mcp` (SDK Python)](#7-cli-mcp-sdk-python)
8. [MCP Inspector](#8-mcp-inspector)
9. [`claude mcp` e configuração de hosts](#9-claude-mcp-e-configuração-de-hosts)
10. [Depuração: o que olhar, em que ordem](#10-depuração-o-que-olhar-em-que-ordem)
11. [Atalhos que só quem usa há tempo conhece](#11-atalhos-que-só-quem-usa-há-tempo-conhece)
12. [O que está obsoleto](#12-o-que-está-obsoleto)

---

## 1. Métodos do protocolo

Revisão `2026-07-28`. Todos são JSON-RPC 2.0.

### 1.1 Cliente → Servidor

| Método | O que faz | Resposta | Aceita `input_required`? |
|---|---|---|---|
| `server/discover` | pede versões suportadas, capacidades e identidade. **Todo servidor MUST implementar.** | `DiscoverResult` | não |
| `tools/list` | lista ferramentas. Pagina; devolve `ttlMs`/`cacheScope`. | `ListToolsResult` | não |
| `tools/call` | executa uma ferramenta | `CallToolResult` | **sim** |
| `resources/list` | lista recursos | `ListResourcesResult` | não |
| `resources/templates/list` | lista modelos de URI (RFC 6570) | `ListResourceTemplatesResult` | não |
| `resources/read` | lê o conteúdo de um recurso | `ReadResourceResult` | **sim** |
| `prompts/list` | lista prompts | `ListPromptsResult` | não |
| `prompts/get` | resolve um prompt com argumentos | `GetPromptResult` | **sim** |
| `completion/complete` | autocompleta argumento de prompt ou de template de recurso | `CompleteResult` | não |
| `subscriptions/listen` | abre **um** fluxo longo de notificações, com filtro | fluxo SSE | não |

### 1.2 Notificações

| Notificação | Direção | Quando |
|---|---|---|
| `notifications/cancelled` | C→S | cancelar requisição. **Só em stdio** — em HTTP, fechar o fluxo é o cancelamento |
| `notifications/progress` | S→C | progresso; só no fluxo da requisição que a originou |
| `notifications/message` | S→C | log; só se a requisição pediu via `io.modelcontextprotocol/logLevel` |
| `notifications/subscriptions/acknowledged` | S→C | confirma a assinatura aberta |
| `notifications/tools/list_changed` | S→C | lista de ferramentas mudou |
| `notifications/prompts/list_changed` | S→C | lista de prompts mudou |
| `notifications/resources/list_changed` | S→C | lista de recursos mudou |
| `notifications/resources/updated` | S→C | recurso assinado mudou |

### 1.3 Requisições que o servidor faz ao cliente

**Nenhuma, diretamente.** Desde `2026-07-28` o servidor **não inicia requisição
JSON-RPC**. Ele devolve um resultado com `resultType: "input_required"` contendo
`inputRequests`, e o cliente **repete a requisição original** com `inputResponses`.
Isso se chama **MRTR** (*Multi Round-Trip Requests*). Ver [16](16-primitivas-do-cliente.md).

Os três pedidos que cabem em `inputRequests`:

| Chave | Pede ao cliente |
|---|---|
| `elicitation/create` | perguntar algo ao usuário (formulário ou URL) |
| `sampling/createMessage` | uma inferência do LLM do host ⚠️ *depreciado* |
| `roots/list` | os diretórios/URIs em que o cliente autoriza trabalhar ⚠️ *depreciado* |

---

## 2. Campos `_meta` reservados

`_meta` é o "porta-malas" das mensagens. Prefixos cujo segundo rótulo seja
`modelcontextprotocol` ou `mcp` são **reservados**. Use `com.suaempresa/` para o seu.

### 2.1 Em toda requisição do cliente

| Chave | Tipo | Obrigatório | O que é |
|---|---|---|---|
| `io.modelcontextprotocol/protocolVersion` | `string` | **sim** | ex.: `"2026-07-28"` |
| `io.modelcontextprotocol/clientCapabilities` | objeto | **sim** | o que o cliente sabe fazer |
| `io.modelcontextprotocol/clientInfo` | objeto | não (SHOULD) | nome e versão do cliente |
| `io.modelcontextprotocol/logLevel` | string | não | nível mínimo de log **para esta requisição** |
| `progressToken` | string/número | não | opta por receber `notifications/progress` |
| `traceparent`, `tracestate`, `baggage` | string | não | contexto de trace do OpenTelemetry (W3C) |

Requisição sem campo obrigatório → erro `-32602` e, em HTTP, `400 Bad Request`.

### 2.2 Em todo resultado do servidor

| Chave | O que é |
|---|---|
| `io.modelcontextprotocol/serverInfo` | nome e versão do servidor (SHOULD) |
| `io.modelcontextprotocol/subscriptionId` | correlaciona notificação com a assinatura (**MUST**, no fluxo de `subscriptions/listen`) |

> `clientInfo` e `serverInfo` são **autodeclarados e não verificados**. Servem para
> exibir e depurar. Não tome decisão de segurança com base neles.

---

## 3. Códigos de erro

| Código | Nome | Significado |
|---|---|---|
| `-32700` | Parse error | JSON inválido |
| `-32600` | Invalid Request | não é JSON-RPC válido |
| `-32601` | Method not found | método desconhecido. Em HTTP, vem com `404` |
| `-32602` | Invalid params | parâmetros inválidos, `_meta` faltando, **recurso não encontrado** |
| `-32603` | Internal error | erro interno do servidor |
| `-32020` | `HeaderMismatch` | cabeçalho HTTP não bate com o corpo, ou falta |
| `-32021` | `MissingRequiredClientCapability` | servidor precisa de capacidade que o cliente não declarou |
| `-32022` | `UnsupportedProtocolVersion` | versão não suportada; `data.supported` lista as que são |

**Política de faixas** (nova em `2026-07-28`): `-32000` a `-32019` é legado, não aloque
nada novo ali; `-32020` a `-32099` é **reservado à especificação**. Códigos seus vão
fora de `-32768..-32000`.

Aposentados, não reutilizar: `-32002` (recurso não encontrado, até `2025-11-25` — clientes
**devem continuar aceitando** de servidores antigos) e `-32042` (elicitação por URL, só em `2025-11-25`).

---

## 4. Cabeçalhos HTTP

Só no transporte **Streamable HTTP**.

| Cabeçalho | Origem no corpo | Obrigatório em |
|---|---|---|
| `MCP-Protocol-Version` | `_meta.io.modelcontextprotocol/protocolVersion` | **toda** requisição POST |
| `Mcp-Method` | `method` | **toda** requisição |
| `Mcp-Name` | `params.name` ou `params.uri` | `tools/call`, `resources/read`, `prompts/get` |
| `Mcp-Param-{Nome}` | parâmetro anotado com `x-mcp-header` no `inputSchema` | quando o valor está presente |
| `Accept` | — | deve listar `application/json` **e** `text/event-stream` |
| `Content-Type` | — | `application/json` na requisição |
| `X-Accel-Buffering: no` | — | **resposta** SSE (SHOULD), para nginx não bufferizar |

**Regra de ouro:** o **corpo é a fonte da verdade**; o cabeçalho é espelho para
balanceador e WAF poderem rotear sem abrir o JSON. Divergência → `400` + `-32020`.

Valor que não cabe em ASCII de cabeçalho usa a sentinela:

```
Mcp-Param-Greeting: =?base64?SGVsbG8sIOS4lueVjA==?=
```

Códigos de status esperados:

| Situação | Status |
|---|---|
| requisição ok | `200` (JSON ou SSE) |
| notificação aceita | `202 Accepted`, sem corpo |
| `Origin` inválido | **`403 Forbidden`** |
| cabeçalho x corpo divergem, versão não suportada, capacidade faltando | `400 Bad Request` |
| método RPC inexistente | `404 Not Found` + `-32601` |
| `GET`/`DELETE` no endpoint (clientes antigos) | `405 Method Not Allowed` (SHOULD) |

> **Observação de campo:** o SDK Python 2.1.1 responde **`400`**, não `405`, a um `GET`
> no endpoint MCP. É uma divergência do "SHOULD" da spec, sem consequência prática
> (o cliente novo não faz GET). Verificado nesta máquina em 01/09/2026.

---

## 5. SDK Python — receituário

`from mcp.server.mcpserver import MCPServer` · `from mcp.client import Client`

### 5.1 Criar o servidor

```python
server = MCPServer(
    "meu-servidor",
    version="1.2.0",
    title="Meu Servidor",           # nome de exibição
    description="O que ele faz",    # aparece no `Implementation`
    instructions="Como me usar",    # dica geral entregue ao host
    website_url="https://exemplo.com",
    log_level="INFO",
    dependencies=["httpx"],         # usado por `mcp install`
)
```

### 5.2 Ferramentas

```python
@server.tool()
def nome_da_ferramenta(arg: str, opcional: int = 10) -> dict:
    """Descrição que o MODELO vai ler para decidir usar isto."""
    return {"ok": True}
```

| Quero… | Faça |
|---|---|
| nome diferente do da função | `@server.tool(name="outro_nome")` |
| descrição diferente da docstring | `@server.tool(description="...")` |
| saída estruturada validada | anote o retorno com `dict`, `TypedDict`, `pydantic.BaseModel` ou `list[...]` — o `outputSchema` sai daí |
| registrar/remover em runtime | `server.add_tool(...)` / `server.remove_tool("nome")` |
| erro que o modelo consiga corrigir | levante `ValueError("mensagem acionável")` → vira `isError: true` |
| acessar contexto da requisição | receba um parâmetro anotado com `ServerRequestContext` |

### 5.3 Recursos

```python
@server.resource("config://app")            # URI fixa
def config() -> str: ...

@server.resource("clima://{cidade}")        # template RFC 6570
def clima(cidade: str) -> str: ...
```

`server.add_resource(Resource(...))` para registrar em runtime.

### 5.4 Prompts

```python
@server.prompt()
def revisar(codigo: str) -> str:
    """Roteiro de revisão de código."""
    return f"Revise:\n{codigo}"
```
Retorno pode ser `str` (vira uma mensagem `user`) ou `list[Message]` para conversa
com vários turnos.

### 5.5 Rodar

```python
server.run()                                          # stdio
server.run(transport="streamable-http",
           host="127.0.0.1", port=8000)               # HTTP
```

Montar dentro de um app ASGI existente:

```python
app = server.streamable_http_app()      # Starlette/ASGI
```

Rota HTTP extra no mesmo processo (health check, por exemplo):

```python
@server.custom_route("/saude", methods=["GET"])
async def saude(request): ...
```

### 5.6 Cliente

```python
from mcp.client import Client
from mcp import StdioServerParameters

Client(server)                                      # em processo — para teste
Client("https://exemplo.com/mcp")                   # Streamable HTTP
Client(StdioServerParameters(command="uv",
       args=["run", "python", "servidor.py"]))      # subprocesso stdio
```

Opções que importam:

| Opção | Para quê |
|---|---|
| `mode="auto"` (padrão) | sonda com `server/discover`, cai para `initialize` em servidor antigo |
| `mode="legacy"` | força o handshake antigo |
| `mode="2026-07-28"` | fixa a versão, sem sondar |
| `elicitation_callback=` | responder a `elicitation/create` |
| `sampling_callback=` | responder a `sampling/createMessage` |
| `list_roots_callback=` | responder a `roots/list` |
| `log_level="info"` | **necessário** para receber `notifications/message` em servidor moderno |
| `input_required_max_rounds=` | teto de idas e vindas do MRTR |
| `cache=CacheConfig()` | respeita `ttlMs`/`cacheScope`; `None` desliga |
| `read_timeout_seconds=` | tempo limite de leitura |

Chamadas:

```python
await c.list_tools() / c.call_tool(nome, args)
await c.list_resources() / c.read_resource(uri)
await c.list_prompts() / c.get_prompt(nome, args)
await c.complete(...)
c.protocol_version, c.server_info, c.server_capabilities, c.instructions
```

> **Nomes de campo:** no JSON é `camelCase` (`structuredContent`, `isError`);
> no objeto Python é `snake_case` (`structured_content`, `is_error`).

---

## 6. SDK TypeScript — receituário

Pacotes v2: `@modelcontextprotocol/server` e `@modelcontextprotocol/client`.

```javascript
import { McpServer, InMemoryTransport } from "@modelcontextprotocol/server";
import { Client } from "@modelcontextprotocol/client";
import { z } from "zod";

const server = new McpServer({ name: "demo", version: "1.0.0" });

server.registerTool(
  "somar",
  { description: "Soma dois números", inputSchema: { a: z.number(), b: z.number() } },
  async ({ a, b }) => ({ content: [{ type: "text", text: String(a + b) }] })
);
```

Exports úteis do pacote `server`:

| Símbolo | Para quê |
|---|---|
| `McpServer` | API de alto nível (o que você quer) |
| `Server` | API de baixo nível, mensagem a mensagem |
| `InMemoryTransport.createLinkedPair()` | par cliente/servidor no mesmo processo — **teste** |
| `WebStandardStreamableHTTPServerTransport` | HTTP com `Request`/`Response` padrão (Workers, Deno, Bun) |
| `PerRequestHTTPServerTransport` | um transporte por requisição, sem estado |
| `createMcpHandler` | monta o handler HTTP pronto |
| `requireBearerAuth`, `verifyBearerToken` | middleware de autorização |
| `validateOriginHeader`, `validateHostHeader` | defesa contra DNS rebinding |
| `ResourceTemplate`, `UriTemplate`, `completable` | recursos com template e autocompletar |
| `isInputRequiredResult`, `inputRequired`, `inputResponse` | MRTR |

Exports úteis do pacote `client`:

| Símbolo | Para quê |
|---|---|
| `Client` | cliente de alto nível |
| `StreamableHTTPClientTransport` | transporte HTTP |
| `SSEClientTransport` | transporte HTTP+SSE antigo (compatibilidade) |
| `withOAuth`, `auth`, `discoverOAuthProtectedResourceMetadata` | fluxo OAuth completo |
| `ClientCredentialsProvider`, `PrivateKeyJwtProvider`, `CrossAppAccessProvider` | autenticação máquina-a-máquina |
| `withInputRequired` | dirige o laço do MRTR |
| `InMemoryResponseCacheStore` | cache de `ttlMs`/`cacheScope` |
| `computeScopeUnion`, `isStrictScopeSuperset` | acúmulo de escopos em *step-up* |

---

## 7. CLI `mcp` (SDK Python)

Disponível com `uv add "mcp[cli]"`.

| Comando | O que faz |
|---|---|
| `mcp version` | mostra a versão do SDK |
| `mcp dev <arquivo.py>` | sobe o servidor **já ligado ao Inspector** |
| `mcp run <arquivo.py>` | roda o servidor direto |
| `mcp install <arquivo.py>` | escreve a entrada no `claude_desktop_config.json` |

Opções (saída real de `--help`, `mcp` 2.1.1):

| Opção | Vale em | O que faz |
|---|---|---|
| `-t, --transport {stdio\|sse\|streamable-http}` | `run` | escolhe o transporte |
| `-e, --with-editable <dir>` | `dev`, `install` | instala o projeto em modo editável |
| `--with <pacote>` | `dev`, `install` | acrescenta dependências ao ambiente |
| `-n, --name <str>` | `install` | nome do servidor no host |
| `-v, --env-var KEY=VALUE` | `install` | variável de ambiente (repetível) |
| `-f, --env-file <.env>` | `install` | carrega variáveis de um arquivo |

Sintaxe `arquivo.py:objeto` seleciona qual objeto servidor usar quando há mais de um.

---

## 8. MCP Inspector

`npx -y @modelcontextprotocol/inspector [--cli|--tui] <servidor> [flags]`

### 8.1 Como apontar o servidor

```bash
# stdio: tudo que é posicional é o comando a lançar
mcp-inspector --cli node build/index.js --method tools/list

# HTTP
mcp-inspector --cli https://api.exemplo.com/mcp --transport http --method tools/list

# a partir de um arquivo de configuração
mcp-inspector --cli --config ./mcp.json --server meuservidor --method tools/list
```

### 8.2 Métodos e acompanhantes obrigatórios

| `--method` | Exige | Nota |
|---|---|---|
| `initialize` | — | sonda de conexão: `serverInfo`, versão, capacidades |
| `tools/list` | — | |
| `tools/call` | `--tool-name` + `--tool-arg` ou `--tool-args-json` | |
| `resources/list` | — | |
| `resources/read` | `--uri` | |
| `resources/templates/list` | — | |
| `prompts/list` | — | |
| `prompts/get` | `--prompt-name`, `--prompt-args` | |
| `logging/setLevel` | `--log-level` | **só era legada** |
| `servers/list`, `servers/show` | — | leem o catálogo **sem conectar** |

### 8.3 Argumentos

```bash
# --tool-arg faz coerção por JSON: count=1 vira número; "012" vira 12
--tool-arg chave=valor --tool-arg count=1 --tool-arg 'options={"format":"json"}'

# --tool-args-json passa VERBATIM: "012" continua a string "012"
--tool-args-json '{"zip":"10001"}'
```
Os dois são mutuamente exclusivos. **Use `--tool-args-json` quando o tipo importa.**

### 8.4 Códigos de saída — o que torna o Inspector útil em CI

| Código | Significado |
|---|---|
| `0` | sucesso |
| `1` | erro de uso ou inesperado |
| `2` | a ferramenta não tem MCP App (sonda `--app-info`) |
| `3` | servidor exige autenticação (401/403, OAuth) |
| `4` | servidor inalcançável (DNS, recusa, timeout) |
| `5` | erro de ferramenta: `isError: true` ou ferramenta inexistente |

Em qualquer saída diferente de zero, uma **única linha JSON no `stderr`**:

```json
{"error":{"code":"auth_required","message":"Unauthorized","status":401,"url":"https://api.exemplo/mcp"}}
```

Receita de CI:

```bash
set -euo pipefail
mcp-inspector --cli --config ./ci-servers.json --server meu-servidor \
  --stored-auth-only --method tools/list --format json \
  | jq -e '.result.tools | map(.name) | index("get_weather")' > /dev/null
```

### 8.5 Autorização em script

| Flag | Efeito |
|---|---|
| `--stored-auth-only` | **a flag que CI quer**: nunca abre navegador; usa token guardado ou falha com `auth_required` |
| `--use-stored-auth` | reaproveita token obtido pelo Inspector web nesta máquina, renovando se preciso |

Sem nenhuma das duas e sem TTY, o CLI falha rápido em vez de travar quinze minutos
esperando um callback que ninguém vai completar.

### 8.6 Outros

- `--format json` → um objeto JSON no `stdout`, sem banner, encanável com `jq`.
- `--app-info` → diz se a ferramenta traz UI de MCP App **sem chamá-la**.
- Proxy: honra `HTTPS_PROXY`/`HTTP_PROXY`/`NO_PROXY`, sem flag própria.

---

## 9. `claude mcp` e configuração de hosts

```bash
claude mcp add <nome> -- <comando> [args...]              # stdio
claude mcp add --transport http <nome> <url>              # HTTP
claude mcp add --transport http <nome> <url> --header "Authorization: Bearer ..."
claude mcp add <nome> -e API_KEY=xxx -- npx meu-servidor  # com variável de ambiente
claude mcp add-json <nome> '<json>'                       # forma completa
claude mcp add-from-claude-desktop                        # importar (macOS e WSL)
claude mcp list
claude mcp remove <nome>
```

Forma canônica do JSON (a mesma em quase todo host):

```json
{
  "mcpServers": {
    "local": {
      "command": "/caminho/absoluto/uv",
      "args": ["run", "--directory", "/caminho/absoluto/projeto", "python", "servidor.py"],
      "env": { "DATABASE_URL": "postgres://..." }
    },
    "remoto": {
      "type": "http",
      "url": "https://exemplo.com/mcp",
      "headers": { "Authorization": "Bearer ..." }
    }
  }
}
```

**Segredo vai em `env`/`headers`, nunca em `args`** — `args` aparece em `ps aux`.

---

## 10. Depuração: o que olhar, em que ordem

| Sintoma | Olhe primeiro | Depois |
|---|---|---|
| servidor não aparece no host | caminho absoluto? o host herda o PATH? app reiniciado? | log do host |
| conecta e cai | escreveu em `stdout`? | rode o servidor no terminal e observe `stderr` |
| ferramenta não aparece | `tools/list` no Inspector | capacidade `tools` declarada? |
| modelo não chama a ferramenta | nome e descrição | schema: campo obrigatório demais? |
| modelo chama com argumento errado | `description` de cada propriedade | exemplos na descrição |
| resposta enorme / contexto estourado | tamanho do retorno | pagine, resuma, use `resource_link` |
| `-32020` em HTTP | cabeçalho `Mcp-Name`/`Mcp-Method` | conferir contra o corpo |
| `-32022` | versão pedida | usar uma de `data.supported` |
| `403 Invalid Origin header` | cabeçalho `Origin` | é o servidor se defendendo, e está certo |
| lentidão em produção | `ttlMs`/`cacheScope` do `tools/list` | o cliente está repolando? |

Ver a fita crua, sem SDK — a técnica mais subestimada:

```bash
printf '%s\n' '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{"_meta":{"io.modelcontextprotocol/protocolVersion":"2026-07-28","io.modelcontextprotocol/clientCapabilities":{}}}}' \
 | uv run python servidor.py 2>/dev/null | jq .
```

---

## 11. Atalhos que só quem usa há tempo conhece

1. **`Client(server)` em processo** dispensa subir subprocesso em teste. Rápido e determinístico.
2. **`--tool-args-json`** em vez de `--tool-arg` quando o valor é string que parece número (CEP, código com zero à esquerda).
3. **`--format json | jq`** transforma o Inspector em ferramenta de CI de verdade.
4. **Ordem determinística em `tools/list`** melhora o *cache* de prompt do LLM. A spec pede
   ("SHOULD") e isso vira dinheiro em servidor de alto volume.
5. **`ttlMs: 0`** (o que o SDK Python devolve por padrão) significa "não cacheie".
   Se a sua lista é estável, ponha `ttlMs` de verdade e economize viagens.
6. **Um `logging.basicConfig(stream=sys.stderr)` na primeira linha** economiza a
   depuração mais frustrante do ecossistema.
7. **`server/discover` é `curl`-ável.** Uma linha diz versão, capacidades e identidade
   de qualquer servidor remoto — a melhor sonda de saúde que existe.
8. **`x-mcp-header`** deixa balanceador rotear por `region` sem abrir o corpo. E **nunca**
   marque parâmetro sensível assim: cabeçalho é visível a todo intermediário.
9. **`Mcp-Name` com valor não-ASCII** exige a sentinela `=?base64?...?=`. Se o seu
   servidor recusa acentos, é isto.
10. **Ferramenta com zero parâmetros:** use `{"type":"object","additionalProperties":false}`,
    não `{}` — o segundo aceita qualquer objeto.

---

## 12. O que está obsoleto

Marcado formalmente sob a **política de ciclo de vida** adotada em `2026-07-28`
(janela mínima de doze meses antes da remoção).

| Recurso | Situação | Substituto |
|---|---|---|
| **Transporte HTTP+SSE** (`2024-11-05`) | depreciado desde `2025-03-26`; reclassificado como *Deprecated* | Streamable HTTP |
| **Roots** | **depreciado** em `2026-07-28` | passe diretórios como parâmetro de ferramenta, URI de recurso ou configuração |
| **Sampling** | **depreciado** | integre direto com a API do provedor de LLM |
| **Logging** (`logging/setLevel`, `notifications/message`) | **depreciado** | `stderr` no stdio, ou OpenTelemetry |
| **DCR (RFC 7591)** como registro de cliente | depreciado | *Client ID Metadata Documents* |
| `includeContext: "thisServer"` / `"allServers"` | depreciado | omitir, ou `"none"` |
| **Sessões de protocolo** (`Mcp-Session-Id`) | **removido** em `2026-07-28` | handles explícitos como argumento de ferramenta |
| **Handshake `initialize`** | **removido** | `_meta` por requisição + `server/discover` |
| **`ping`** | **removido** | — |
| **Retomada de SSE** (`Last-Event-ID`) | **removido** | reemitir a requisição com novo `id` |
| **GET no endpoint MCP** | **removido** | `subscriptions/listen` |
| `resources/subscribe` / `unsubscribe` | **removido** | `subscriptions/listen` com filtro |
| `notifications/roots/list_changed` | **removido** | — |
| `FastMCP` (SDK Python) | renomeado na v2 | `MCPServer` |
| `@modelcontextprotocol/sdk` (npm) | ramo v1, manutenção | `@modelcontextprotocol/server` + `/client` |
| `mcp` 1.x (PyPI) | manutenção, só correção de segurança | `mcp` 2.x |
| erro `-32002` (recurso não encontrado) | aposentado | `-32602` (mas **aceite** `-32002` de servidor antigo) |

---

## 13. Autoteste

1. Quais três métodos aceitam resposta `input_required`?
2. Que campos `_meta` são obrigatórios em toda requisição do cliente?
3. Qual status HTTP para `Origin` inválido? E para método RPC inexistente?
4. Qual a fonte da verdade quando cabeçalho e corpo divergem, e qual erro é devolvido?
5. Como um cliente recebe `notifications/message` de um servidor moderno?
6. Que flag do Inspector CLI é a certa para CI, e por quê?
7. Qual código de saída do Inspector indica `isError: true`?
8. Cite três coisas removidas — não só depreciadas — em `2026-07-28`.
9. Por que segredo não pode ir em `args` da configuração do host?
10. Qual a diferença entre `--tool-arg` e `--tool-args-json`, com um exemplo em que importa?

---

**Anterior:** [04 · Como começar](04-como-comecar.md) · **Próximo:** [06 · Exemplos](06-exemplos.md) · **Índice:** [00-MAPA](00-MAPA.md)

*Fontes: [Spec 2026-07-28 — base](https://modelcontextprotocol.io/specification/2026-07-28/basic),
[transportes](https://modelcontextprotocol.io/specification/2026-07-28/basic/transports),
[changelog](https://modelcontextprotocol.io/specification/2026-07-28/changelog),
[Inspector CLI](https://modelcontextprotocol.io/docs/2026-07-28/tools/inspector/cli).
Saídas de `mcp --help`, `claude mcp --help` e do SDK obtidas nesta máquina em 01/09/2026
(`mcp` 2.1.1, Claude Code 2.1.252).*
