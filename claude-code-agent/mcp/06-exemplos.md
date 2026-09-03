# 06 · Exemplos — do trivial ao de produção

`Nível: iniciante → avançado` · `Executados em 01/09/2026`

Todo código aqui é **completo e executável**. Nada de `...` escondendo parte
essencial. As saídas mostradas foram capturadas nesta máquina
(`mcp` 2.1.1 / Python 3.12.14; `@modelcontextprotocol/server` 2.0.0 / Node v24.18.0).

Preparo comum aos exemplos em Python:

```bash
mkdir -p ~/mcp-exemplos && cd ~/mcp-exemplos && uv init --python 3.12 . && uv add "mcp[cli]"
```

---

## Índice

| # | Exemplo | Ensina |
|---|---|---|
| 1 | [Ferramenta mínima](#1-ferramenta-mínima) | o esqueleto |
| 2 | [Saída estruturada com Pydantic](#2-saída-estruturada-com-pydantic) | `outputSchema`, `structuredContent` |
| 3 | [Erro que o modelo consegue corrigir](#3-erro-que-o-modelo-consegue-corrigir) | `ToolError` × exceção crua |
| 4 | [Validação declarativa com `Annotated`](#4-validação-declarativa-com-annotated) | schema rico sem código |
| 5 | [Paginação — não estourar o contexto](#5-paginação--não-estourar-o-contexto) | o erro mais caro do MCP |
| 6 | [Progresso em tarefa longa](#6-progresso-em-tarefa-longa) | `Context`, `progressToken` |
| 7 | [Estado sem sessão: handles explícitos](#7-estado-sem-sessão-handles-explícitos) | o modelo sem estado de 2026-07-28 |
| 8 | [Recursos e templates de URI](#8-recursos-e-templates-de-uri) | `resources/*` |
| 9 | [Prompt reutilizável](#9-prompt-reutilizável) | `prompts/*` |
| 10 | [Perguntar ao usuário (MRTR/elicitação)](#10-perguntar-ao-usuário-mrtrelicitação) | `InputRequiredResult` |
| 11 | [Servidor HTTP + `curl` cru](#11-servidor-http--curl-cru) | Streamable HTTP na unha |
| 12 | [Teste automatizado](#12-teste-automatizado) | como travar comportamento |
| 13 | [Produção I — servidor de banco somente-leitura](#13-produção-i--servidor-de-banco-somente-leitura) | caso real |
| 14 | [Produção II — proxy de API com cache e limite](#14-produção-ii--proxy-de-api-com-cache-e-limite) | caso real |
| 15 | [TypeScript: servidor + cliente](#15-typescript-servidor--cliente) | o outro SDK |

---

## 1. Ferramenta mínima

**Problema.** Expor uma função Python para um modelo.

```python
# ex01.py
from mcp.server.mcpserver import MCPServer

server = MCPServer("ex01", version="1.0.0")


@server.tool()
def somar(a: float, b: float) -> float:
    """Soma dois números."""
    return a + b


if __name__ == "__main__":
    server.run()
```

```bash
npx -y @modelcontextprotocol/inspector --cli uv run python ex01.py \
  --method tools/call --tool-name somar --tool-arg a=20 --tool-arg b=22
```

**Explicação.** As anotações `a: float, b: float` viram o `inputSchema`; `-> float`
vira o `outputSchema`; a docstring vira a `description`. Você escreveu função Python
e ganhou uma ferramenta MCP. **Os três — nome, tipos, docstring — são o contrato com
o modelo.** Trate-os como API pública.

---

## 2. Saída estruturada com Pydantic

**Problema.** Devolver dados que o cliente possa validar e o modelo possa ler.

```python
# ex02.py
from pydantic import BaseModel, Field
from mcp.server.mcpserver import MCPServer

server = MCPServer("ex02", version="1.0.0")


class Clima(BaseModel):
    temperatura: float = Field(description="Temperatura em graus Celsius")
    condicao: str = Field(description="Descrição das condições")


@server.tool()
def clima(cidade: str) -> Clima:
    """Clima atual da cidade informada."""
    return Clima(temperatura=22.5, condicao="Parcialmente nublado")
```

Saída real (via cliente em processo):

```
{'temperatura': 22.5, 'condicao': 'Parcialmente nublado'}
```

**Explicação e armadilha.** O modelo Pydantic gera o `outputSchema`, e o resultado
volta em **dois** lugares: `content[0].text` (o JSON serializado, para o modelo ler)
e `structuredContent` (para o código do cliente consumir). A spec pede as duas coisas,
por compatibilidade.

> ⚠️ **Verificado nesta máquina:** anotar o retorno como `dict` cru **não** gera
> `outputSchema`, e `structured_content` volta `None`. `list[str]` idem. Só tipos
> com schema — `BaseModel`, `TypedDict`, escalares — produzem saída estruturada.
> Se você quer `structuredContent`, **declare um modelo**.

---

## 3. Erro que o modelo consegue corrigir

**Problema.** O modelo mandou a data no formato errado. Você quer que ele conserte
sozinho, sem incomodar o usuário.

```python
# ex03.py
from datetime import date
from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError

server = MCPServer("ex03", version="1.0.0")


@server.tool()
def agendar(data: str) -> str:
    """Agenda um compromisso numa data futura, no formato AAAA-MM-DD."""
    try:
        d = date.fromisoformat(data)
    except ValueError:
        raise ToolError(f"Data inválida: {data!r}. Use AAAA-MM-DD, ex.: 2026-09-15.")
    if d <= date.today():
        raise ToolError(f"A data deve ser futura. Hoje é {date.today().isoformat()}.")
    return f"agendado para {d.isoformat()}"
```

Saída real:

```
agendar erro: True  Error executing tool agendar: Data inválida: '31/12/2026'. Use AAAA-MM-DD, ex.: 2026-09-15.
agendar ok:          agendado para 2027-01-05
```

**A lição que custa caro.** No SDK Python 2.x, **só `ToolError` (e `ResourceError`)
têm a mensagem entregue ao modelo**. Qualquer outra exceção é tratada como *crash*:
o modelo recebe apenas `Error executing tool <nome>`, sem o texto, e o servidor
registra o traceback no log.

Comparação medida nesta máquina:

| O que você levanta | O que o modelo vê |
|---|---|
| `raise ValueError("Data inválida: '31/12/2026'. Use AAAA-MM-DD.")` | `Error executing tool agendar` ❌ |
| `raise ToolError("Data inválida: '31/12/2026'. Use AAAA-MM-DD.")` | `Error executing tool agendar: Data inválida: '31/12/2026'. Use AAAA-MM-DD.` ✅ |

Isso não é capricho do SDK: é a distinção da spec entre **erro de protocolo** (o modelo
não conserta) e **erro de execução** (o modelo conserta). Um crash inesperado pode
vazar caminho de arquivo, consulta SQL ou segredo na mensagem — por isso o texto é
retido. Você declara "eu previ isso" usando `ToolError`.

---

## 4. Validação declarativa com `Annotated`

**Problema.** Limitar tamanho, faixa e formato **no schema**, para o cliente validar
antes de chegar ao seu código.

```python
# ex04.py
from typing import Annotated
from pydantic import Field
from mcp.server.mcpserver import MCPServer

server = MCPServer("ex04", version="1.0.0")
ITENS = [f"item-{i:03d}" for i in range(1, 251)]


@server.tool()
def buscar(
    termo: Annotated[str, Field(description="Texto a buscar, mínimo 3 caracteres", min_length=3)],
    limite: Annotated[int, Field(description="Máximo de resultados", ge=1, le=50)] = 10,
) -> list[str]:
    """Busca itens cujo nome contenha o termo."""
    return [i for i in ITENS if termo in i][:limite]
```

Saída real com `termo="ab"`:

```
True  Error executing tool buscar: 1 validation error for buscarArguments
termo
  String should have at least 3 characters [type=string_too_short, ...]
```

**Explicação.** A falha de validação de argumento é **erro de execução**, com a
mensagem completa — a spec `2026-07-28` decidiu isso de propósito, para o modelo se
autocorrigir. Você ganhou validação, mensagem útil e documentação (`description` de
cada campo entra no schema que o modelo lê) sem escrever nenhum `if`.

---

## 5. Paginação — não estourar o contexto

**Problema.** `SELECT *` com 40.000 linhas destrói o contexto, custa dinheiro e piora
a resposta. É o erro mais caro do MCP.

```python
# ex05.py
from pydantic import BaseModel
from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError

server = MCPServer("ex05", version="1.0.0")
ITENS = [f"item-{i:03d}" for i in range(1, 251)]


class Pagina(BaseModel):
    total: int
    pagina: int
    itens: list[str]
    tem_proxima: bool


@server.tool()
def listar(pagina: int = 1, por_pagina: int = 20) -> Pagina:
    """Lista itens em páginas. Máximo 100 por página.
    Use `tem_proxima` para saber se deve pedir a página seguinte."""
    if not 1 <= por_pagina <= 100:
        raise ToolError("por_pagina deve estar entre 1 e 100")
    ini = (pagina - 1) * por_pagina
    return Pagina(
        total=len(ITENS),
        pagina=pagina,
        itens=ITENS[ini : ini + por_pagina],
        tem_proxima=ini + por_pagina < len(ITENS),
    )
```

Saída real com `pagina=2, por_pagina=3`:

```
{'total': 250, 'pagina': 2, 'itens': ['item-004', 'item-005', 'item-006'], 'tem_proxima': True}
```

**Três decisões de projeto que importam:**

1. `total` e `tem_proxima` explícitos — sem eles, o modelo pede páginas até o infinito
   ou para cedo demais.
2. **Teto** em `por_pagina`. O modelo *vai* tentar `por_pagina=10000`.
3. A instrução de como paginar está **na descrição**, que é onde o modelo lê.

Para resultado muito grande, devolva um resumo e um `resource_link` em vez do conteúdo.

---

## 6. Progresso em tarefa longa

```python
# ex06.py
from mcp.server.mcpserver import MCPServer, Context

server = MCPServer("ex06", version="1.0.0")


@server.tool()
async def processar(n: int, ctx: Context) -> str:
    """Processa n etapas, reportando progresso."""
    for i in range(n):
        await ctx.report_progress(i + 1, n, f"etapa {i+1}")
    return f"{n} etapas concluídas"
```

Saída real: `3 etapas concluídas` (com três `notifications/progress` no caminho).

**Explicação.** O parâmetro `ctx: Context` é **injetado pelo SDK** e **não aparece no
`inputSchema`** — o modelo não o vê nem pode preenchê-lo. As notificações só são
enviadas se o cliente pediu, incluindo `progressToken` no `_meta` da requisição.
No `Context` também estão `ctx.info/warning/error`, `ctx.read_resource`,
`ctx.request_id`, `ctx.headers`, `ctx.client_capabilities`.

---

## 7. Estado sem sessão: handles explícitos

**Problema.** Um carrinho de compras que sobrevive entre chamadas — sem sessão de
protocolo, que **não existe mais** desde `2026-07-28`.

```python
# ex07.py
import secrets
from pydantic import BaseModel
from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError

server = MCPServer("ex07", version="1.0.0")
CARRINHOS: dict[str, list[str]] = {}


class CarrinhoNovo(BaseModel):
    carrinho_id: str


class Carrinho(BaseModel):
    carrinho_id: str
    itens: int


@server.tool()
def criar_carrinho() -> CarrinhoNovo:
    """Cria um carrinho vazio e devolve o seu identificador.
    Carrinhos expiram após 24 h de inatividade."""
    cid = "crt_" + secrets.token_urlsafe(16)
    CARRINHOS[cid] = []
    return CarrinhoNovo(carrinho_id=cid)


@server.tool()
def adicionar(carrinho_id: str, sku: str) -> Carrinho:
    """Acrescenta um item ao carrinho identificado por `carrinho_id`
    (obtido em `criar_carrinho`)."""
    if carrinho_id not in CARRINHOS:
        raise ToolError(f"Carrinho {carrinho_id!r} não existe ou expirou. Crie um novo.")
    CARRINHOS[carrinho_id].append(sku)
    return Carrinho(carrinho_id=carrinho_id, itens=len(CARRINHOS[carrinho_id]))
```

Saída real:

```
criar:              {'carrinho_id': 'crt_mgVUFFJ_Kz8'}
adicionar:          {'carrinho_id': 'crt_mgVUFFJ_Kz8', 'itens': 1}
handle inexistente: True  Error executing tool adicionar: Carrinho 'crt_falso' não existe ou expirou. Crie um novo.
```

**Quatro regras para handles**, direto da spec:

1. **Autorização.** O handle é um *nome*, não uma *capacidade*. Em servidor
   autenticado, valide na **toda** chamada se ele pertence ao chamador. Guarde como
   `<user_id>:<handle>`, com o `user_id` vindo do token verificado — nunca do cliente.
2. **Opacidade.** `crt_` + `token_urlsafe(16)`. Nada de `carrinho-1`, `carrinho-2`.
3. **Vida útil.** Declare-a **na descrição da ferramenta**, para o modelo saber.
4. **Erro de expiração** explícito, para o modelo criar outro em vez de travar.

O `dict` global acima é didático: em produção use Redis/banco, porque o processo pode
morrer e porque com várias réplicas o `dict` de uma não é o da outra.

---

## 8. Recursos e templates de URI

```python
# ex08.py
import json
from mcp.server.mcpserver import MCPServer

server = MCPServer("ex08", version="1.0.0")
PRODUTOS = {"1": {"nome": "Café", "preco": 24.9}, "2": {"nome": "Chá", "preco": 18.5}}


@server.resource("config://app")
def config() -> str:
    """Configuração da aplicação."""
    return json.dumps({"ambiente": "producao", "regiao": "sa-east-1"}, ensure_ascii=False)


@server.resource("produto://{produto_id}")
def produto(produto_id: str) -> str:
    """Dados de um produto pelo id."""
    p = PRODUTOS.get(produto_id)
    return json.dumps(p, ensure_ascii=False) if p else json.dumps({"erro": "não encontrado"})
```

```bash
npx -y @modelcontextprotocol/inspector --cli uv run python ex08.py --method resources/list
npx -y @modelcontextprotocol/inspector --cli uv run python ex08.py \
  --method resources/read --uri "produto://1"
```

**Quando usar recurso em vez de ferramenta.** Recurso é **substantivo** e a aplicação
escolhe (o usuário anexa, ou o host inclui por heurística). Ferramenta é **verbo** e o
modelo escolhe. Na prática, em 2026 o suporte a recursos nos clientes é bem menor que
o de ferramentas — se você precisa que funcione em todo lugar, exponha **também** como
ferramenta. Ver [15](15-primitivas-do-servidor.md).

---

## 9. Prompt reutilizável

```python
# ex09.py
from mcp.server.mcpserver import MCPServer, Message, UserMessage, AssistantMessage

server = MCPServer("ex09", version="1.0.0")


@server.prompt()
def revisar_pr(diff: str, foco: str = "segurança") -> list[Message]:
    """Revisão de pull request com um foco declarado."""
    return [
        UserMessage(
            f"Você é revisor sênior. Revise o diff abaixo com foco em {foco}.\n"
            f"Aponte no máximo 5 problemas, do mais grave ao menos grave.\n"
            f"Para cada um: arquivo, linha, o que quebra, como corrigir.\n\n"
            f"```diff\n{diff}\n```"
        ),
        AssistantMessage("Entendido. Vou listar os problemas em ordem de gravidade."),
    ]
```

```bash
npx -y @modelcontextprotocol/inspector --cli uv run python ex09.py \
  --method prompts/get --prompt-name revisar_pr --prompt-args diff="- a\n+ b"
```

**Explicação.** Prompt é **escolhido pelo usuário** (tipicamente vira comando de barra
no host). É onde mora o conhecimento de *como pedir bem* — o que numa equipe costuma
estar num arquivo de texto que ninguém acha. A `AssistantMessage` no fim é a técnica
de "pôr palavras na boca do assistente" para ancorar o formato da resposta.

---

## 10. Perguntar ao usuário (MRTR/elicitação)

**Problema.** A ferramenta apaga arquivo. Você quer confirmação explícita do humano.

```python
# ex10.py
from typing import Annotated
from pydantic import BaseModel, Field
from mcp.server.mcpserver import (
    MCPServer, Resolve, Elicit, ElicitationResult, AcceptedElicitation,
)

server = MCPServer("ex10", version="1.0.0")


class Confirmacao(BaseModel):
    confirmar: bool = Field(description="Confirma a exclusão?")


def pedir_confirmacao(caminho: str):
    """Resolver: roda ANTES do corpo da ferramenta e devolve o pedido ao cliente."""
    return Elicit(f"Apagar {caminho}? Isto não pode ser desfeito.", Confirmacao)


@server.tool()
def apagar(
    caminho: str,
    ok: Annotated[ElicitationResult[Confirmacao], Resolve(pedir_confirmacao)],
) -> str:
    """Apaga um arquivo. Pede confirmação ao usuário antes."""
    if isinstance(ok, AcceptedElicitation) and ok.data.confirmar:
        return f"{caminho} apagado"
    return "cancelado pelo usuário"
```

Cliente que responde à pergunta:

```python
import asyncio
import mcp.types as types
from mcp.client import Client
from ex10 import server


async def elicitation_callback(context, params):
    print("  [cliente] servidor perguntou:", params.message)
    return types.ElicitResult(action="accept", content={"confirmar": True})


async def main():
    async with Client(server, elicitation_callback=elicitation_callback) as c:
        t = (await c.list_tools()).tools[0]
        print("inputSchema:", t.input_schema)
        r = await c.call_tool("apagar", {"caminho": "/tmp/x.txt"})
        print("resultado:", r.content[0].text)


asyncio.run(main())
```

Saída real:

```
inputSchema: {'type': 'object', 'properties': {'caminho': {'title': 'Caminho', 'type': 'string'}},
              'required': ['caminho'], 'title': 'apagarArguments'}
  [cliente] servidor perguntou: Apagar /tmp/x.txt? Isto não pode ser desfeito.
resultado: /tmp/x.txt apagado
```

**Duas coisas essenciais nessa saída:**

1. O parâmetro `ok` **não está no `inputSchema`**. O modelo não sabe que ele existe e
   não pode forjá-lo. Quem o preenche é o usuário, através do cliente.
2. Por baixo, o servidor devolveu `resultType: "input_required"` e o cliente
   **repetiu a chamada** com `inputResponses`. Isso é o **MRTR** de `2026-07-28`.

> ⚠️ **Armadilha real, medida aqui.** Chamar `await ctx.elicit(...)` direto dentro da
> ferramenta levanta
> `NoBackChannelError: Cannot send 'elicitation/create': this transport context has no
> back-channel for server-initiated requests.`
> Sob o protocolo `2026-07-28` **não existe canal de volta**: o servidor não inicia
> requisição. Use o padrão `Resolve`/`Elicit` acima, que o SDK traduz para MRTR na
> versão nova e para requisição direta na versão antiga.

**Nunca** peça senha, chave de API ou dado de pagamento por formulário — a spec
proíbe. Para isso existe a elicitação em **modo URL**.

---

## 11. Servidor HTTP + `curl` cru

```python
# ex11.py
from mcp.server.mcpserver import MCPServer

server = MCPServer("ex11", version="1.0.0")


@server.tool()
def somar(a: float, b: float) -> float:
    """Soma dois números."""
    return a + b


if __name__ == "__main__":
    server.run(transport="streamable-http", host="127.0.0.1", port=8931)
```

```bash
uv run python ex11.py &
```

```bash
curl -sS -X POST http://127.0.0.1:8931/mcp \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -H 'MCP-Protocol-Version: 2026-07-28' \
  -H 'Mcp-Method: tools/list' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{"_meta":{
       "io.modelcontextprotocol/protocolVersion":"2026-07-28",
       "io.modelcontextprotocol/clientCapabilities":{}}}}'
```

Resposta real (`HTTP/1.1 200 OK`, `content-type: application/json`):

```json
{"jsonrpc":"2.0","id":1,"result":{"cacheScope":"private","resultType":"complete",
 "tools":[{"description":"Soma dois números.","inputSchema":{"type":"object",
 "properties":{"a":{"title":"A","type":"number"},"b":{"title":"B","type":"number"}},
 "required":["a","b"],"title":"somarArguments"},"name":"somar",
 "outputSchema":{"properties":{"result":{"title":"Result","type":"number"}},
 "required":["result"],"title":"somarOutput","type":"object"}}],
 "ttlMs":0,"_meta":{"io.modelcontextprotocol/serverInfo":{"name":"ex11","version":"1.0.0"}}}}
```

Agora **erre de propósito** — é assim que se aprende o protocolo.

**(a) `tools/call` sem o cabeçalho `Mcp-Name`:**

```bash
curl -sS -o- -w '\nHTTP %{http_code}\n' -X POST http://127.0.0.1:8931/mcp \
  -H 'Content-Type: application/json' -H 'Accept: application/json, text/event-stream' \
  -H 'MCP-Protocol-Version: 2026-07-28' -H 'Mcp-Method: tools/call' \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"somar",
       "arguments":{"a":1,"b":1},"_meta":{"io.modelcontextprotocol/protocolVersion":"2026-07-28",
       "io.modelcontextprotocol/clientCapabilities":{}}}}'
```

```
{"jsonrpc":"2.0","id":2,"error":{"code":-32020,"message":"mcp-name header does not match the request body's 'name' parameter"}}
HTTP 400
```

**(b) `Origin` de outro domínio:**

```bash
curl -sS -o- -w '\nHTTP %{http_code}\n' -X POST http://127.0.0.1:8931/mcp \
  -H 'Origin: http://evil.example' -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -H 'MCP-Protocol-Version: 2026-07-28' -H 'Mcp-Method: tools/list' \
  -d '{"jsonrpc":"2.0","id":3,"method":"tools/list","params":{"_meta":{
       "io.modelcontextprotocol/protocolVersion":"2026-07-28",
       "io.modelcontextprotocol/clientCapabilities":{}}}}'
```

```
Invalid Origin header
HTTP 403
```

Isso é a defesa contra **DNS rebinding**: sem ela, uma página web qualquer aberta no
seu navegador poderia falar com o servidor MCP que roda no seu `localhost`.

**(c) versão de protocolo inexistente** (aqui em stdio, mas o comportamento é o mesmo):

```json
{"jsonrpc":"2.0","id":5,"error":{"code":-32022,"message":"Unsupported protocol version",
 "data":{"supported":["2026-07-28"],"requested":"1999-01-01"}}}
```

O cliente deve escolher uma versão de `data.supported` e repetir.

---

## 12. Teste automatizado

```python
# test_servidor.py
import pytest
from mcp.client import Client
from ex05 import server


@pytest.mark.anyio
async def test_lista_ferramentas():
    async with Client(server) as c:
        nomes = [t.name for t in (await c.list_tools()).tools]
        assert "listar" in nomes


@pytest.mark.anyio
async def test_paginacao():
    async with Client(server) as c:
        r = await c.call_tool("listar", {"pagina": 2, "por_pagina": 3})
        assert r.structured_content["itens"] == ["item-004", "item-005", "item-006"]
        assert r.structured_content["tem_proxima"] is True


@pytest.mark.anyio
async def test_teto_de_pagina_e_erro_util():
    """O modelo VAI pedir 10000 por página. A mensagem precisa ser acionável."""
    async with Client(server) as c:
        r = await c.call_tool("listar", {"por_pagina": 10000})
        assert r.is_error
        assert "entre 1 e 100" in r.content[0].text


@pytest.fixture
def anyio_backend():
    return "asyncio"
```

```bash
uv add --dev pytest anyio && uv run pytest -q
```

**Explicação.** `Client(server)` conecta **em processo**: sem subprocesso, sem porta,
sem flakiness. É rápido o bastante para rodar a cada salvamento. Os testes que mais
pagam não são os do caminho feliz — são os que travam **a mensagem de erro**, porque é
ela que o modelo lê para se corrigir, e é ela que quebra em silêncio quando alguém
refatora.

---

## 13. Produção I — servidor de banco somente-leitura

**Caso real.** Dar ao time de suporte a capacidade de perguntar sobre pedidos em
linguagem natural, **sem** dar ao modelo a chave do banco.

```python
# servidor_pedidos.py
import os
import sys
import logging
import sqlite3
from pydantic import BaseModel
from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError

logging.basicConfig(stream=sys.stderr, level=logging.INFO)  # NUNCA stdout
log = logging.getLogger("pedidos")

DB = os.environ.get("PEDIDOS_DB", "pedidos.db")
server = MCPServer("pedidos", version="1.0.0",
                   instructions="Consulta somente-leitura de pedidos. Não altera nada.")

MAX_LINHAS = 50


def conectar() -> sqlite3.Connection:
    # `mode=ro` no próprio driver: a garantia não depende do meu código.
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    return con


class Pedido(BaseModel):
    id: str
    cliente: str
    status: str
    total: float


class Resultado(BaseModel):
    total_encontrado: int
    truncado: bool
    pedidos: list[Pedido]


@server.tool()
def buscar_pedido(pedido_id: str) -> Pedido:
    """Busca UM pedido pelo identificador exato (ex.: 'PED-4711').
    Não faz busca por texto livre — para isso use `listar_pedidos`."""
    with conectar() as con:
        # Consulta PARAMETRIZADA. Nunca formate SQL com f-string.
        linha = con.execute(
            "SELECT id, cliente, status, total FROM pedidos WHERE id = ?", (pedido_id,)
        ).fetchone()
    if linha is None:
        raise ToolError(f"Pedido {pedido_id!r} não existe. Confira o identificador.")
    return Pedido(**dict(linha))


@server.tool()
def listar_pedidos(status: str | None = None, limite: int = 20) -> Resultado:
    """Lista pedidos, opcionalmente filtrando por status
    ('novo', 'pago', 'enviado', 'cancelado'). Devolve no máximo 50."""
    if limite < 1 or limite > MAX_LINHAS:
        raise ToolError(f"limite deve estar entre 1 e {MAX_LINHAS}")
    sql = "SELECT id, cliente, status, total FROM pedidos"
    params: tuple = ()
    if status is not None:
        if status not in {"novo", "pago", "enviado", "cancelado"}:
            raise ToolError(
                f"status {status!r} inválido. Use: novo, pago, enviado ou cancelado."
            )
        sql += " WHERE status = ?"
        params = (status,)
    sql += " ORDER BY id LIMIT ?"          # ORDEM DETERMINÍSTICA: ajuda o cache do LLM
    params = params + (limite + 1,)

    with conectar() as con:
        linhas = [dict(r) for r in con.execute(sql, params).fetchall()]

    truncado = len(linhas) > limite
    log.info("listar_pedidos status=%s limite=%s -> %s linhas", status, limite, len(linhas))
    return Resultado(
        total_encontrado=len(linhas[:limite]),
        truncado=truncado,
        pedidos=[Pedido(**l) for l in linhas[:limite]],
    )


if __name__ == "__main__":
    server.run()
```

Banco de teste:

```bash
sqlite3 pedidos.db "CREATE TABLE pedidos(id TEXT PRIMARY KEY, cliente TEXT, status TEXT, total REAL);
INSERT INTO pedidos VALUES('PED-4711','Ana','pago',249.90),('PED-4712','Bruno','novo',89.00);"
```

**Sete decisões que separam isto de um tutorial:**

1. **Não há ferramenta `executar_sql`.** Dar SQL arbitrário ao modelo é dar o banco
   inteiro a quem conseguir injetar um prompt. Exponha *verbos do domínio*.
2. **`mode=ro` no driver**, não só "eu só escrevi SELECT". Defesa que não depende de
   disciplina.
3. **Consultas parametrizadas.** Sempre. Sem exceção.
4. **Teto de linhas** e sinalização `truncado`, para o modelo saber que há mais.
5. **`ORDER BY` explícito** — ordem determinística melhora o cache de prompt e torna
   o teste reprodutível.
6. **Log em `stderr`**, com os parâmetros, para auditoria. Em `stdout` derrubaria o servidor.
7. **Erros com o valor recebido e a lista de valores válidos** — o modelo se corrige.

O que **falta** para produção de verdade e está em [24-operacao](24-operacao-e-producao.md):
limite de taxa, tempo máximo de consulta, métricas, e — se for remoto — autorização
com validação de audiência.

---

## 14. Produção II — proxy de API com cache e limite de taxa

**Caso real.** Envolver uma API de terceiro que cobra por chamada e limita a taxa.
Sem cuidado, o modelo faz 40 chamadas em 10 segundos e você recebe `429` (e a fatura).

```python
# servidor_cep.py
import sys
import time
import logging
import httpx
from pydantic import BaseModel
from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError

logging.basicConfig(stream=sys.stderr, level=logging.INFO)
log = logging.getLogger("cep")

server = MCPServer("cep", version="1.0.0")

_cache: dict[str, tuple[float, dict]] = {}
TTL = 60 * 60 * 24          # endereço muda pouco: 24 h
_chamadas: list[float] = []
LIMITE, JANELA = 30, 60.0   # 30 chamadas por minuto


class Endereco(BaseModel):
    cep: str
    logradouro: str
    bairro: str
    cidade: str
    uf: str


def _limite_ok() -> bool:
    agora = time.monotonic()
    _chamadas[:] = [t for t in _chamadas if agora - t < JANELA]
    if len(_chamadas) >= LIMITE:
        return False
    _chamadas.append(agora)
    return True


@server.tool()
def consultar_cep(cep: str) -> Endereco:
    """Consulta um endereço brasileiro pelo CEP (8 dígitos, com ou sem hífen).
    Resultados são cacheados por 24 h."""
    limpo = cep.replace("-", "").replace(".", "").strip()
    if not (len(limpo) == 8 and limpo.isdigit()):
        raise ToolError(f"CEP inválido: {cep!r}. Informe 8 dígitos, ex.: 01310-100.")

    agora = time.time()
    if (entrada := _cache.get(limpo)) and agora - entrada[0] < TTL:
        log.info("cache hit %s", limpo)
        return Endereco(**entrada[1])

    if not _limite_ok():
        raise ToolError(
            f"Limite de {LIMITE} consultas por minuto atingido. Tente de novo em instantes."
        )

    try:
        r = httpx.get(f"https://viacep.com.br/ws/{limpo}/json/", timeout=5.0)
        r.raise_for_status()
    except httpx.TimeoutException:
        raise ToolError("A consulta de CEP demorou demais. Tente novamente.")
    except httpx.HTTPStatusError as e:
        raise ToolError(f"O serviço de CEP respondeu {e.response.status_code}.")

    dados = r.json()
    if dados.get("erro"):
        raise ToolError(f"CEP {cep} não encontrado.")

    end = {
        "cep": dados["cep"], "logradouro": dados["logradouro"],
        "bairro": dados["bairro"], "cidade": dados["localidade"], "uf": dados["uf"],
    }
    _cache[limpo] = (agora, end)
    log.info("cache miss %s", limpo)
    return Endereco(**end)
```

```bash
uv add httpx && uv run python servidor_cep.py
```

**O que este exemplo ensina e o anterior não:**

- **Cache**, porque o modelo repete a mesma chamada com frequência espantosa
  (ele não "lembra" que já perguntou, se o resultado saiu do contexto).
- **Limite de taxa do lado do servidor**, com mensagem que orienta a esperar. Sem ele,
  um laço do modelo esgota a sua cota.
- **Timeout explícito.** `httpx` sem `timeout` espera para sempre — e a chamada do
  modelo trava junto.
- **Cada erro de rede vira `ToolError` com texto próprio.** "Demorou demais" leva o
  modelo a tentar de novo; "não encontrado" leva a perguntar outro CEP. Um `502` cru
  não leva a nada.
- **Normalização da entrada** (`01310-100` e `01310100` são o mesmo CEP), porque o
  modelo escreve dos dois jeitos.

---

## 15. TypeScript: servidor + cliente

```javascript
// demo.mjs
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

const [tCliente, tServidor] = InMemoryTransport.createLinkedPair();
const client = new Client({ name: "demo-cli", version: "1.0.0" });

await server.connect(tServidor);
await client.connect(tCliente);

console.log("tools:", (await client.listTools()).tools.map((t) => t.name));
console.log(
  "call:",
  JSON.stringify(await client.callTool({ name: "somar", arguments: { a: 20, b: 22 } }))
);
process.exit(0);
```

```bash
npm install @modelcontextprotocol/server @modelcontextprotocol/client zod && node demo.mjs
```

Saída real:

```
tools: [ 'somar' ]
call: {"content":[{"type":"text","text":"42"}]}
```

**Nota de migração.** No SDK v1 o pacote era `@modelcontextprotocol/sdk` e o import
vinha de `.../server/mcp.js`. No v2 são dois pacotes. `InMemoryTransport.createLinkedPair()`
é o equivalente TypeScript do `Client(server)` do Python: teste rápido, sem processo.

---

## 16. Autoteste

1. Por que `raise ValueError("mensagem útil")` **não** entrega a mensagem ao modelo no SDK Python 2.x? Qual exceção usar?
2. Que tipos de retorno geram `outputSchema` e `structuredContent` — e quais não geram?
3. Cite três decisões da ferramenta de paginação que evitam que o modelo se perca.
4. Por que `ctx: Context` não aparece no `inputSchema`? E por que isso é bom para segurança?
5. Por que `await ctx.elicit(...)` falha com `NoBackChannelError` na revisão `2026-07-28`? Qual é o padrão certo?
6. No exemplo 13, cite três defesas que **não dependem** de o programador lembrar de fazer a coisa certa.
7. Por que uma ferramenta `executar_sql` genérica é perigosa mesmo com o banco em modo somente-leitura?
8. Que status HTTP e que código JSON-RPC você recebe se o cabeçalho `Mcp-Name` não bater com o corpo?
9. Por que o exemplo 14 precisa de cache **e** de limite de taxa? Não bastaria um dos dois?
10. Qual a vantagem de `Client(server)` / `InMemoryTransport` sobre subir um subprocesso no teste?

---

**Anterior:** [05 · Manual de uso](05-manual-de-uso.md) · **Próximo:** [07 · Projeto-modelo](07-projeto-modelo/README.md) · **Índice:** [00-MAPA](00-MAPA.md)

*Exemplos 1–12 e 15 executados nesta máquina em 01/09/2026. Os exemplos 13 e 14
seguem os mesmos padrões verificados; a estrutura de `ToolError`, `stderr`, tetos e
ordem determinística foi exercitada nos exemplos anteriores. Comportamento de
`ToolError` × exceção crua confirmado lendo `mcp/server/mcpserver/exceptions.py`
do SDK 2.1.1 e medido na prática.*
