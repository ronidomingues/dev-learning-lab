# 04 · Do ambiente pronto ao primeiro servidor funcionando

`Nível: iniciante` · `Escrito e executado em 01/09/2026`

> Este arquivo assume o ambiente do [03 · Instalação](03-instalacao.md). Não repetimos
> a instalação aqui. Se `uv run mcp version` ainda não responde, volte ao 03.

---

## 1. O menor servidor MCP que faz algo

### 1.1 Crie o projeto

```bash
mkdir -p ~/mcp-primeiro && cd ~/mcp-primeiro
```

```bash
uv init --python 3.12 .
```

```bash
uv add "mcp[cli]"
```

### 1.2 Escreva o servidor

Arquivo `servidor.py`:

```python
"""Servidor MCP mínimo — SDK Python 2.x, protocolo 2026-07-28."""
from mcp.server.mcpserver import MCPServer

# O nome e a versão aparecem no `serverInfo` de toda resposta.
server = MCPServer("demo", version="1.0.0")


@server.tool()
def somar(a: float, b: float) -> float:
    """Soma dois números."""
    return a + b


@server.resource("config://saudacao")
def saudacao() -> str:
    """Uma saudação fixa."""
    return "Olá do MCP!"


@server.prompt()
def revisar(codigo: str) -> str:
    """Pede revisão de um trecho de código."""
    return f"Revise este código e aponte bugs:\n\n{codigo}"


if __name__ == "__main__":
    server.run()          # transporte padrão: stdio
```

**Repare no que você não escreveu:**

- não escreveu o JSON Schema da ferramenta — ele é **derivado das anotações de tipo**;
- não escreveu o texto que descreve a ferramenta para o modelo — é a **docstring**;
- não escreveu nada de JSON-RPC, `id`, `_meta`, versão de protocolo.

Isso é o SDK trabalhando. Os três detalhes acima, porém, **são o contrato com o
modelo**: nome, tipos e docstring são literalmente o que o LLM lê para decidir se e
como chamar a sua ferramenta. Escreva-os como se fossem documentação pública, porque são.

### 1.3 Verificação imediata — sem host, sem LLM

```bash
npx -y @modelcontextprotocol/inspector --cli uv run python servidor.py --method tools/list
```

Saída real desta máquina (recortada):

```json
{
  "tools": [
    {
      "name": "somar",
      "description": "Soma dois números.",
      "inputSchema": {
        "type": "object",
        "properties": {
          "a": { "title": "A", "type": "number" },
          "b": { "title": "B", "type": "number" }
        },
        "required": ["a", "b"],
        "title": "somarArguments"
      },
      "outputSchema": {
        "type": "object",
        "properties": { "result": { "title": "Result", "type": "number" } },
        "required": ["result"],
        "title": "somarOutput"
      }
    }
  ]
}
```

**Deu isso? Você tem um servidor MCP funcionando.** O resto do curso é sobre fazer
isso bem.

Chamando a ferramenta:

```bash
npx -y @modelcontextprotocol/inspector --cli uv run python servidor.py \
  --method tools/call --tool-name somar --tool-arg a=20 --tool-arg b=22
```

---

## 2. Um cliente, para ver os dois lados

Arquivo `cliente.py`:

```python
import asyncio
from mcp.client import Client
from servidor import server        # conexão em processo, ideal para teste


async def main() -> None:
    async with Client(server) as c:
        tools = await c.list_tools()
        print("TOOLS:", [t.name for t in tools.tools])

        r = await c.call_tool("somar", {"a": 2, "b": 3})
        print("CALL:", r.content[0].text, "| structured:", r.structured_content)

        res = await c.list_resources()
        print("RESOURCES:", [str(x.uri) for x in res.resources])

        rr = await c.read_resource("config://saudacao")
        print("READ:", rr.contents[0].text)

        ps = await c.list_prompts()
        print("PROMPTS:", [p.name for p in ps.prompts])

        gp = await c.get_prompt("revisar", {"codigo": "x = 1/0"})
        print("PROMPT:", gp.messages[0].content.text)

        print("PROTOCOL:", c.protocol_version)
        print("SERVER INFO:", c.server_info)


asyncio.run(main())
```

```bash
uv run python cliente.py
```

Saída real desta máquina:

```
TOOLS: ['somar']
CALL: 5.0 | structured: {'result': 5.0}
RESOURCES: ['config://saudacao']
READ: Olá do MCP!
PROMPTS: ['revisar']
PROMPT: Revise este código e aponte bugs:

x = 1/0
PROTOCOL: 2026-07-28
SERVER INFO: name='demo' title=None version='1.0.0' description=None website_url=None icons=None
```

> **Atenção ao `structured_content`.** No JSON o campo se chama `structuredContent`;
> no objeto Python do SDK 2.x ele é `structured_content`. Escrever `r.structuredContent`
> levanta `AttributeError` — foi o primeiro erro que este material cometeu ao ser
> escrito, e o SDK ainda sugere a correção na mensagem.

---

## 3. O mesmo em TypeScript

```bash
mkdir -p ~/mcp-primeiro-ts && cd ~/mcp-primeiro-ts && npm init -y
npm install @modelcontextprotocol/server @modelcontextprotocol/client zod
```

Arquivo `demo.mjs`:

```javascript
import { McpServer, InMemoryTransport } from "@modelcontextprotocol/server";
import { Client } from "@modelcontextprotocol/client";
import { z } from "zod";

const server = new McpServer({ name: "demo-ts", version: "1.0.0" });

server.registerTool(
  "somar",
  {
    description: "Soma dois números",
    inputSchema: { a: z.number(), b: z.number() },
  },
  async ({ a, b }) => ({ content: [{ type: "text", text: String(a + b) }] })
);

// Par de transportes em memória: cliente e servidor no mesmo processo.
const [transporteCliente, transporteServidor] = InMemoryTransport.createLinkedPair();
const client = new Client({ name: "demo-cli", version: "1.0.0" });

await server.connect(transporteServidor);
await client.connect(transporteCliente);

console.log("tools:", (await client.listTools()).tools.map((t) => t.name));
console.log(
  "call:",
  JSON.stringify(await client.callTool({ name: "somar", arguments: { a: 20, b: 22 } }))
);
process.exit(0);
```

```bash
node demo.mjs
```

Saída real desta máquina:

```
tools: [ 'somar' ]
call: {"content":[{"type":"text","text":"42"}]}
```

Diferença conceitual entre os dois SDKs: nenhuma. Diferença de estilo: em Python o
schema vem das anotações de tipo; em TypeScript vem do `zod`. Escolha pela linguagem
em que você já é produtivo.

---

## 4. Ligando ao seu host

### Claude Code

```bash
claude mcp add demo -- uv run --directory ~/mcp-primeiro python servidor.py
```

```bash
claude mcp list
```

Depois, na conversa, peça: *"Some 137 e 4 usando a ferramenta do servidor demo."*
Você deve ver o pedido de aprovação da chamada, e o resultado `141`.

### Claude Desktop

```bash
uv run mcp install servidor.py --name "Demo"
```
Escreve a entrada no `claude_desktop_config.json`.

Ou edite à mão (caminhos e armadilhas em [03 §9.2](03-instalacao.md#92-claude-desktop)).
**Reinicie o aplicativo por completo.**

---

## 5. O ciclo de trabalho do dia a dia

```
   editar servidor.py
        │
        ▼
   Inspector --cli  ──► viu o JSON? o schema está como você quer?
        │                    │ não
        │ sim                └──► volte a editar
        ▼
   Inspector (web/TUI) ──► chamar a ferramenta à mão, ver erro real
        │
        ▼
   host de verdade  ──► o MODELO escolhe a ferramenta certa? entende o resultado?
        │                    │ não
        │ sim                └──► ajuste NOME, DESCRIÇÃO e SCHEMA (não a lógica)
        ▼
   teste automatizado (Client em processo) ──► trava o comportamento
```

Quatro observações que valem anos de prática:

1. **O Inspector é o seu loop rápido.** Não depure no host: é lento, custa tokens, e
   o modelo mascara os seus erros ("ele chamou errado, mas deu certo mesmo assim").
2. **Quando o modelo erra a ferramenta, o bug quase nunca está na lógica.** Está no
   nome, na descrição ou no schema. Ver [23-projeto-de-ferramentas](23-projeto-de-ferramentas.md).
3. **Teste com `Client(server)` em processo.** É rápido, determinístico e não precisa
   subir processo nenhum — o SDK Python aceita passar o objeto servidor direto.
4. **Reinicie o host a cada mudança de configuração.** Mudança no *código* do servidor
   stdio também exige, porque o processo é lançado uma vez.

---

## 6. Os cinco primeiros erros de uso (não de instalação)

### 6.1 `print()` no servidor stdio

```python
@server.tool()
def somar(a: float, b: float) -> float:
    print("chamou somar")     # ❌ ESCREVE NO STDOUT
    return a + b
```

`stdout` **é a fita do protocolo**. Qualquer byte que não seja uma mensagem JSON-RPC
válida corrompe a conversa e o cliente derruba a conexão. O sintoma é cruel: o servidor
"conecta e cai" sem erro claro.

**Correção** — log vai para `stderr`, que a spec reserva explicitamente para isso:

```python
import sys, logging
logging.basicConfig(stream=sys.stderr, level=logging.INFO)
log = logging.getLogger(__name__)

@server.tool()
def somar(a: float, b: float) -> float:
    log.info("chamou somar a=%s b=%s", a, b)   # ✅
    return a + b
```

Em TypeScript o equivalente é usar `console.error`, nunca `console.log`.

### 6.2 Descrição vaga, ou nenhuma

```python
@server.tool()
def buscar(q: str) -> str:          # ❌ o modelo não sabe o que isso busca
    ...
```

O modelo escolhe a ferramenta lendo **nome + descrição + schema**. Sem descrição, ele
chuta. Com o nome `buscar` e mais três ferramentas de busca no mesmo host, ele chuta pior.

```python
@server.tool()
def buscar_pedido_por_id(pedido_id: str) -> dict:
    """Busca UM pedido pelo identificador exato (ex.: 'PED-4711').
    Não faz busca por texto livre nem por cliente — para isso use `listar_pedidos`.
    Devolve erro se o pedido não existir."""
```

Diga o que a ferramenta faz, o que ela **não** faz, e o que acontece no caso ruim.

### 6.3 Devolver um `SELECT *` inteiro

```python
@server.tool()
def listar_clientes() -> list[dict]:
    return db.query("SELECT * FROM clientes")     # ❌ 40.000 linhas
```

Tudo que a ferramenta devolve vai para **o contexto do modelo**. Você acabou de
gastar dinheiro, estourar a janela e piorar a resposta. Pagine e resuma:

```python
@server.tool()
def listar_clientes(pagina: int = 1, por_pagina: int = 20) -> dict:
    """Lista clientes, 20 por página. Devolve `total` e `itens`."""
    if not 1 <= por_pagina <= 100:
        raise ValueError("por_pagina deve estar entre 1 e 100")
    ...
```

### 6.4 Levantar exceção crua em vez de erro utilizável

Há **dois** tipos de erro em MCP, e confundi-los custa caro:

| Tipo | Quando | Como o modelo reage |
|---|---|---|
| **Erro de protocolo** (JSON-RPC `error`) | ferramenta inexistente, requisição malformada | não consegue se corrigir |
| **Erro de execução** (`isError: true` no resultado) | data inválida, valor fora da faixa, API caiu | **lê o texto e tenta de novo, corrigido** |

Um erro de validação deve ser **erro de execução**, com texto acionável:

```python
@server.tool()
def agendar(data: str) -> str:
    """Agenda para uma data futura no formato AAAA-MM-DD."""
    try:
        d = date.fromisoformat(data)
    except ValueError:
        # Vira isError=true com este texto — o modelo consegue corrigir sozinho.
        raise ValueError(f"Data inválida: {data!r}. Use o formato AAAA-MM-DD, ex.: 2026-09-15.")
    if d <= date.today():
        raise ValueError(f"A data deve ser futura. Hoje é {date.today().isoformat()}.")
    ...
```

Isso não é preciosismo: a spec `2026-07-28` mudou de propósito para dizer que erro de
validação de entrada **deve** ser erro de execução, justamente para o modelo se
autocorrigir.

### 6.5 Assumir que o servidor lembra do que aconteceu antes

```python
carrinho = []                       # ❌ estado global escondido

@server.tool()
def adicionar_item(sku: str) -> str:
    carrinho.append(sku)
    return f"{len(carrinho)} itens"
```

Desde a revisão `2026-07-28` **o MCP é sem estado**: não há sessão de protocolo, e o
servidor não pode supor que duas chamadas venham do mesmo usuário, da mesma conversa
ou da mesma conexão. Estado que atravessa chamadas precisa de um **identificador
explícito**, criado pelo servidor e devolvido pelo modelo como argumento:

```python
@server.tool()
def criar_carrinho() -> dict:
    """Cria um carrinho e devolve o seu identificador. Expira em 24 h."""
    cid = secrets.token_urlsafe(16)
    ...
    return {"carrinho_id": cid}

@server.tool()
def adicionar_item(carrinho_id: str, sku: str) -> dict:
    """Acrescenta um item ao carrinho identificado por `carrinho_id`."""
    ...
```

E o identificador **não é autenticação**: valide sempre se ele pertence a quem está
chamando. Ver [19-seguranca §Sequestro de handle](19-seguranca.md).

---

## 7. Onde ir agora

| Você quer… | Vá para |
|---|---|
| Ver muitos exemplos completos | [06 · Exemplos](06-exemplos.md) |
| Um projeto inteiro que roda | [07 · Projeto-modelo](07-projeto-modelo/README.md) |
| Referência de comandos e API | [05 · Manual de uso](05-manual-de-uso.md) |
| Entender o protocolo por dentro | [13 · JSON-RPC e a camada base](13-json-rpc-e-a-camada-base.md) |
| Fazer o modelo usar bem a ferramenta | [23 · Projeto de ferramentas](23-projeto-de-ferramentas.md) |
| Não se machucar | [19 · Segurança](19-seguranca.md) |

---

## 8. Autoteste

1. De onde o SDK Python tira o `inputSchema` e a `description` da ferramenta?
2. Por que um `print()` derruba um servidor stdio? Para onde vai o log, então?
3. Qual a diferença entre erro de protocolo e erro de execução, e qual deles o modelo consegue corrigir sozinho?
4. Por que testar no Inspector antes de testar no host?
5. O modelo escolheu a ferramenta errada. Onde está o bug, quase sempre?
6. Por que uma variável global no servidor é uma armadilha na revisão `2026-07-28`?
7. No SDK Python 2.x, como se lê o conteúdo estruturado do resultado — e por que não `structuredContent`?
8. Como conectar um cliente ao servidor **no mesmo processo**, e por que isso é bom para teste?

---

**Anterior:** [03 · Instalação](03-instalacao.md) · **Próximo:** [05 · Manual de uso](05-manual-de-uso.md) · **Índice:** [00-MAPA](00-MAPA.md)

*Todo o código e todas as saídas deste arquivo foram executados em 01/09/2026:
`mcp` 2.1.1 / Python 3.12.14 / `uv` 0.12.7; `@modelcontextprotocol/server` 2.0.0 e
`/client` 2.0.0 / Node v24.18.0; Inspector 2.4.0; Ubuntu 22.04.5 LTS.*
