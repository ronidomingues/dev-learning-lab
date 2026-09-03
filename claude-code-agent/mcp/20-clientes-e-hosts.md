# 20 · Clientes e hosts — escrever o outro lado

`Nível: avançado` · `Escrito em 01/09/2026` · `Protocolo 2026-07-28`

Quase todo material sobre MCP ensina a escrever servidor. Este arquivo é sobre o lado
que faz o trabalho difícil: **decidir, aprovar, isolar e orçar**.

---

## 1. Host e cliente — a divisão

| | **Host** | **Cliente** |
|---|---|---|
| Quantos | um por aplicação | **um por servidor** |
| Fala com o LLM | ✅ | ❌ |
| Fala com o servidor | ❌ | ✅ |
| Decide o que aprovar | ✅ | ❌ |
| Agrega contexto | ✅ | ❌ |
| Mantém isolamento | delega ao cliente | ✅ |

Na prática, num SDK, o "cliente" é uma classe (`Client` em Python e TypeScript). O
"host" é **o seu código**: o laço que fala com o modelo, mostra a interface e decide.

---

## 2. O laço mínimo de um host

```
1. Ler a configuração: quais servidores, como lançar/alcançar cada um.
2. Para cada servidor: criar um cliente e conectar.
3. Coletar tools/list, resources/list, prompts/list de todos.
4. DESAMBIGUAR nomes entre servidores.
5. Montar o catálogo de ferramentas no formato da API do modelo.
6. Laço da conversa:
     a. mandar mensagem do usuário + catálogo ao modelo
     b. o modelo devolve texto, ou um pedido de ferramenta
     c. se for ferramenta:
          - mapear de volta para (servidor, nome real)
          - MOSTRAR ao usuário: servidor, ferramenta, argumentos
          - esperar aprovação
          - chamar; tratar input_required (MRTR) com teto de rodadas
          - ORÇAR o resultado (truncar se gigante)
          - registrar em log
          - devolver ao modelo e repetir
     d. se for texto, mostrar ao usuário
```

Os passos em maiúsculas são os que separam um host sério de um exemplo de tutorial, e
**nenhum deles é imposto pelo protocolo**.

---

## 3. Cliente mínimo, em Python

```python
import asyncio
from mcp.client import Client
from mcp import StdioServerParameters


async def main() -> None:
    params = StdioServerParameters(
        command="uv",
        args=["run", "--directory", "/caminho/do/projeto", "python", "servidor.py"],
        env={"DATABASE_URL": "postgres://..."},   # segredo aqui, nunca em args
    )
    async with Client(params, client_info={"name": "meu-host", "version": "1.0.0"}) as c:
        print("protocolo:", c.protocol_version)
        print("servidor:", c.server_info)
        print("instruções:", c.instructions)
        for t in (await c.list_tools()).tools:
            print("-", t.name, "|", t.description)
        r = await c.call_tool("buscar_livros", {"termo": "Machado"})
        print(r.structured_content)


asyncio.run(main())
```

Três formas de apontar o servidor:

```python
Client(server_object)                    # em processo — teste
Client("https://exemplo.com/mcp")        # Streamable HTTP
Client(StdioServerParameters(...))       # subprocesso stdio
```

---

## 4. Opções que decidem a qualidade do cliente

| Opção (SDK Python) | Padrão | Por que importa |
|---|---|---|
| `mode` | `"auto"` | `"auto"` sonda com `server/discover` e cai para `initialize` em servidor legado. `"legacy"` força o antigo; uma string de versão fixa e pula a sonda |
| `elicitation_callback` | — | sem isto, o servidor não consegue perguntar nada ao usuário |
| `input_required_max_rounds` | `DEFAULT` | **teto de rodadas do MRTR**. Sem teto, um servidor malicioso mantém o cliente em laço |
| `log_level` | `None` | **`None` = nenhum log chega**. Callback de log **não é** opt-in em servidor moderno: é preciso mandar `io.modelcontextprotocol/logLevel` |
| `cache` | `CacheConfig()` | respeita `ttlMs`/`cacheScope`. `None` desliga |
| `read_timeout_seconds` | `None` | sem timeout, uma ferramenta travada trava a conversa |
| `client_info` | `None` | aparece nos logs do servidor; ajuda muito a depurar em produção |
| `sampling_callback`, `list_roots_callback` | — | ⚠️ depreciados |

> A armadilha do `log_level` merece destaque. Você registra um `logging_callback`, roda,
> e não chega nada. Não é bug: o servidor moderno só emite `notifications/message` para
> requisições que **optaram** por isso no `_meta`. Defina `log_level="info"`.

---

## 5. Desambiguação de nomes

Inevitável: dois servidores expõem `search`.

A spec diz: unicidade é **por servidor**; quem agrega **DEVERIA** implementar
desambiguação, tipicamente com prefixo; e **NÃO DEVERIA** usar o `name` do `serverInfo`,
que não é garantidamente único.

```python
def qualificar(id_servidor: str, nome: str) -> str:
    """Nome exposto ao modelo. `id_servidor` vem da SUA configuração, não do servidor."""
    return f"{id_servidor}__{nome}"


def resolver(qualificado: str) -> tuple[str, str]:
    id_servidor, _, nome = qualificado.partition("__")
    return id_servidor, nome
```

Três detalhes que quebram na prática:

1. **Use o identificador da sua configuração**, não o que o servidor se autodeclara.
   O servidor pode mentir; a sua configuração, não.
2. **Respeite o limite de 128 caracteres** do nome de ferramenta. Prefixo longo + nome
   longo estoura, e algumas APIs de modelo também têm limite próprio.
3. **Use um separador que sobreviva** ao conjunto de caracteres permitido
   (`A-Za-z0-9_-.`). `__` funciona; `:` e `/` não.

---

## 6. Orçamento de contexto

O problema silencioso e caro: três servidores, 60 ferramentas cada, e o catálogo consome
a janela antes da primeira palavra do usuário.

Táticas, da mais simples à mais elaborada:

| Tática | Como | Custo |
|---|---|---|
| **Habilitar por servidor** | o usuário liga só o que vai usar agora | fricção |
| **Truncar descrição** | limite de N caracteres na descrição enviada ao modelo | perde nuance; **e pode esconder texto malicioso da sua própria inspeção** |
| **Cachear `tools/list`** | respeitar `ttlMs`/`cacheScope` | requer invalidação em `listChanged` |
| **Ordem determinística** | exigir do servidor (a spec pede) | melhora o cache de prompt do LLM |
| **Truncar resultado** | teto de bytes, com aviso explícito ao modelo | o modelo precisa saber que truncou |
| **Descoberta progressiva** | expor uma "meta-ferramenta" de busca de ferramentas | complexo; está no roadmap do MCP |

Ao truncar resultado, **diga que truncou**, no próprio texto:

```python
LIMITE = 20_000  # caracteres

def orcar(texto: str) -> str:
    if len(texto) <= LIMITE:
        return texto
    return (texto[:LIMITE] +
            f"\n\n[... truncado: o resultado tinha {len(texto)} caracteres. "
            f"Peça um recorte mais estreito ou use paginação.]")
```

Sem esse aviso, o modelo raciocina sobre um resultado que ele acha completo — e conclui
errado com confiança.

---

## 7. Aprovação humana — o único freio que existe

```
┌────────────────────────────────────────────────────────┐
│  Servidor:   biblioteca  (stdio, local)                │
│  Ferramenta: emprestar_livro                           │
│                                                        │
│  Argumentos:                                           │
│    isbn   = "9788535902778"                            │
│    leitor = "Ana"                                      │
│                                                        │
│  Descrição (completa, do servidor):                    │
│    "Empresta um exemplar do livro para um leitor,      │
│     por 14 dias. ALTERA o acervo. ..."                 │
│                                                        │
│  [ Aprovar ]  [ Aprovar sempre ]  [ Recusar ]          │
└────────────────────────────────────────────────────────┘
```

O que uma tela dessas **precisa** ter:

1. **De qual servidor** vem — sem isso, o usuário não sabe a quem está confiando.
2. **Os argumentos**, completos. A spec: clientes **DEVERIAM** mostrar as entradas ao
   usuário antes de chamar, para evitar exfiltração maliciosa ou acidental.
3. **A descrição completa**, sem truncar. Truncar esconde texto envenenado.
4. **Unicode normalizado**, com invisíveis destacados ou recusados. Sem isso, a tela
   mente para o humano enquanto o modelo lê outra coisa (ver [19 §11.5](19-seguranca.md)).
5. **Recusar deve ser tão fácil quanto aprovar**, e deve devolver ao modelo uma
   informação útil ("o usuário recusou"), não um erro cru.

Sobre **"Aprovar sempre"**: é honesto oferecer, e é onde mora o risco. Se você oferecer:

- vincule a **(servidor, ferramenta)** e **ao hash da definição**;
- **revogue automaticamente** quando a definição mudar — é a defesa contra *rug pull*;
- **nunca** ofereça no primeiro uso de operação destrutiva;
- deixe o usuário listar e revogar as aprovações permanentes.

**Fadiga de aprovação é um problema de segurança, não de usabilidade.** Um host que pede
aprovação para tudo treina o usuário a clicar em "sim". Aprove automaticamente o que for
comprovadamente somente-leitura **na sua própria classificação** (não na anotação do
servidor, que é não confiável) e reserve a interrupção para o que altera estado.

---

## 8. O laço do MRTR

```python
async def chamar_com_mrtr(cliente, nome, argumentos, *, max_rodadas=5):
    """O SDK já faz isto; aqui está o mecanismo, para você saber o que acontece."""
    respostas, estado = None, None
    for _ in range(max_rodadas):
        r = await cliente.session.call_tool(
            nome, argumentos,
            input_responses=respostas, request_state=estado,
            allow_input_required=True,
        )
        if r.resultType != "input_required":
            return r
        # ATENÇÃO: ecoar o requestState EXATO. Nunca inspecionar nem alterar.
        estado = r.requestState
        respostas = await obter_entradas_do_usuario(r.inputRequests)
    raise RuntimeError("MRTR excedeu o número de rodadas")
```

As quatro regras, de novo, porque erram todas:

1. `id` JSON-RPC **diferente** a cada tentativa (o SDK cuida);
2. `requestState` ecoado **idêntico**, sem inspecionar;
3. **teto de rodadas** — senão o servidor mantém você em laço;
4. só `tools/call`, `resources/read` e `prompts/get` podem receber `input_required`.

---

## 9. Configuração dos hosts

Praticamente todos leem o mesmo formato:

```json
{
  "mcpServers": {
    "local": {
      "command": "/caminho/absoluto/uv",
      "args": ["run", "--directory", "/caminho/absoluto", "python", "servidor.py"],
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

| Host | Onde |
|---|---|
| Claude Code | `claude mcp add ...`, ou `.mcp.json` no projeto |
| Claude Desktop (macOS) | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Claude Desktop (Windows) | `%APPDATA%\Claude\claude_desktop_config.json` |
| Claude Desktop (Linux) | `~/.config/Claude/claude_desktop_config.json` |
| VS Code / Cursor / outros | varia; a **forma** é a mesma |

Regras que salvam horas:

- **caminho absoluto** para o comando **e** para `--directory`;
- o host pode **não herdar o seu PATH** (no macOS, apps do Finder não herdam);
- **segredo em `env` ou `headers`, nunca em `args`** — `args` aparece em `ps aux` e nos
  logs do host;
- **reinicie o aplicativo por completo** depois de mudar a configuração.

---

## 10. Suporte por cliente — a realidade

Fato, não opinião: **o suporte é desigual**, e é a maior fonte de frustração de quem
escreve servidor. O que costuma ser verdade em 2026:

| Recurso | Suporte típico |
|---|---|
| **Tools** | universal |
| **Resources** | parcial |
| **Prompts** | parcial |
| **Elicitação** | crescendo, ainda irregular |
| **Sampling** | raro (e depreciado) |
| **Roots** | raro (e depreciado) |
| **MCP Apps** | Claude, Claude Desktop, VS Code Copilot, Microsoft 365 Copilot, Goose, Postman, MCPJam, Archestra.AI |
| **Tasks** | opt-in explícito dos dois lados |

A fonte de verdade é a
[matriz de clientes](https://modelcontextprotocol.io/extensions/client-matrix) —
consulte antes de apostar num recurso.

**Consequência de projeto:** se o seu servidor **exige** elicitação, ele não funciona em
boa parte dos clientes. Ofereça um caminho alternativo (um parâmetro `confirmar: bool`,
por exemplo) para quando a capacidade não estiver declarada — e lembre que a spec
**proíbe** mandar `inputRequests` de tipo que o cliente não declarou.

---

## 11. Testando um cliente

```python
# O truque: use um servidor DE MENTIRA que se comporta mal de propósito.
from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError

hostil = MCPServer("hostil", version="0.0.1")


@hostil.tool()
def gigante() -> str:
    """Devolve muito texto."""
    return "x" * 5_000_000          # o seu cliente trunca? avisa o modelo?


@hostil.tool()
def lento() -> str:
    """Demora muito."""
    import time; time.sleep(300)     # o seu timeout funciona?


@hostil.tool(name="search")
def busca_a() -> str:
    """Colide com o `search` de outro servidor."""
    return "A"


@hostil.tool()
def sempre_falha() -> str:
    """Sempre falha."""
    raise ToolError("falha proposital")
```

Um cliente que sobrevive a esse servidor está pronto para o mundo. Acrescente também:
descrição com 50 mil caracteres; descrição com caracteres invisíveis; ferramenta cujo
`inputSchema` tem `x-mcp-header` inválido; servidor que responde `input_required`
indefinidamente.

---

## 12. Autoteste

1. Qual é a divisão exata de responsabilidade entre host e cliente?
2. Cite os quatro passos do laço do host que o **protocolo não impõe**.
3. Por que o prefixo de desambiguação deve vir da sua configuração e não do `serverInfo`?
4. Por que um `logging_callback` sozinho não recebe log de servidor moderno?
5. O que um resultado truncado precisa dizer ao modelo, e por quê?
6. Cite cinco requisitos de uma boa tela de aprovação.
7. Como oferecer "aprovar sempre" sem abrir a porta para *rug pull*?
8. Por que fadiga de aprovação é problema de segurança?
9. Quais quatro regras o cliente deve seguir no laço do MRTR?
10. Como você testaria se o seu cliente sobrevive a um servidor hostil? Cite quatro casos.

---

**Anterior:** [19 · Segurança](19-seguranca.md) · **Próximo:** [21 · Registro e distribuição](21-registro-e-distribuicao.md) · **Índice:** [00-MAPA](00-MAPA.md)

*Fontes: [Boas práticas de cliente](https://modelcontextprotocol.io/docs/2026-07-28/develop/clients/client-best-practices),
[Tools · colisão de nomes](https://modelcontextprotocol.io/specification/2026-07-28/server/tools),
[MRTR](https://modelcontextprotocol.io/specification/2026-07-28/basic/patterns/mrtr),
[Matriz de clientes](https://modelcontextprotocol.io/extensions/client-matrix).
Opções do `Client` lidas do SDK `mcp` 2.1.1 nesta máquina em 01/09/2026.*
