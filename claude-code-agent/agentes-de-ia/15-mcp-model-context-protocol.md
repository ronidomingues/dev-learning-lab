# 15 · MCP — Model Context Protocol

**Nível:** intermediário · Atualizado em 13/08/2026

---

## 1. O problema que ele resolve

Antes do MCP, cada cliente de IA precisava de uma integração própria com cada
ferramenta. Com **M** clientes e **N** ferramentas, você escrevia **M × N**
integrações — e cada nova ferramenta exigia N novos conectores.

```
    SEM MCP                         COM MCP

  cliente₁ ─┬─ Jira            cliente₁ ─┐        ┌─ Jira
            ├─ Slack                     │        │
            └─ banco          cliente₂ ──┼─ MCP ──┼─ Slack
  cliente₂ ─┬─ Jira                      │        │
            ├─ Slack           cliente₃ ─┘        └─ banco
            └─ banco
      M × N integrações             M + N integrações
```

O MCP foi publicado pela Anthropic em **novembro de 2024**, como
especificação aberta. Ao longo de 2025 foi adotado por OpenAI, Google DeepMind
e Microsoft — um padrão publicado por um fornecedor e adotado pelos
concorrentes, o que é raro o bastante para significar alguma coisa.

A analogia oficial é "USB-C para IA". A analogia mais precisa, para quem
programa, é **LSP**: o Language Server Protocol resolveu exatamente o mesmo
M×N entre editores e linguagens, em 2016, e pelo mesmo caminho.

---

## 2. O protocolo, sem mistério

MCP é **JSON-RPC 2.0** sobre um transporte. Uma linha de JSON entra, uma sai.

**Transportes:**

| Transporte | Uso |
|---|---|
| `stdio` | servidor local, subprocesso. O caso mais comum |
| Streamable HTTP | servidor remoto |
| SSE | remoto, formato mais antigo |

**Os métodos que importam:**

| Método | O que faz |
|---|---|
| `initialize` | handshake: versão do protocolo, capacidades, identificação |
| `notifications/initialized` | o cliente avisa que terminou o handshake |
| `tools/list` | catálogo de ferramentas |
| `tools/call` | executa uma |
| `resources/list`, `resources/read` | dados que o cliente pode incluir no contexto |
| `prompts/list`, `prompts/get` | modelos de prompt (viram comandos `/mcp__servidor__prompt`) |
| `ping` | verificação de vida |

Um diálogo inteiro, copiável:

```bash
printf '%s\n' \
  '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"eu","version":"0"}}}' \
  '{"jsonrpc":"2.0","id":2,"method":"tools/list"}' \
  | python3 07-projeto-modelo/mcp_tarefas.py
```

Faça isso uma vez. Depois de ver as duas linhas de JSON, "meu MCP não conecta"
deixa de ser um mistério e vira depuração comum.

---

## 3. As três primitivas

| Primitiva | Quem controla | Analogia |
|---|---|---|
| **Tools** | o **modelo** decide chamar | função |
| **Resources** | a **aplicação** decide incluir | arquivo aberto no editor |
| **Prompts** | o **usuário** invoca | template / snippet |

Na prática, 90% dos servidores MCP expõem só *tools*. Resources são úteis
quando o cliente deve poder anexar um documento sem que o modelo peça;
prompts são atalhos que aparecem como comandos de barra.

---

## 4. Escrever um servidor

### Com o SDK (produção)

```bash
pip install mcp        # Python
npm install @modelcontextprotocol/sdk   # TypeScript
```

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("meu-servidor")

@mcp.tool()
def buscar_pedido(numero: str) -> str:
    """Busca um pedido pelo número.

    Use sempre que a pergunta envolver um pedido específico — o status muda
    ao longo do dia, então nunca responda de memória.

    Args:
        numero: número do pedido, ex.: 'PED-2026-0042'.
    """
    ...
```

O esquema JSON é gerado da assinatura; a descrição vem do docstring. **É por
isso que o docstring de uma ferramenta MCP é código de produção**, e não
comentário: ele é literalmente o prompt que decide se a ferramenta será usada.

### Sem SDK (didático)

O [projeto-modelo](07-projeto-modelo/mcp_tarefas.py) implementa o protocolo em
~60 linhas, sem nenhuma dependência, com testes de contrato que rodam sem rede
nem chave de API. Vale ler uma vez.

---

## 5. Registrar no Claude Code

**Escopo de projeto** — `.mcp.json` na raiz, versionado no git, compartilhado
com o time:

```json
{
  "mcpServers": {
    "tarefas": {
      "command": "python3",
      "args": ["mcp_tarefas.py"]
    },
    "sentry": {
      "type": "http",
      "url": "https://mcp.sentry.dev/mcp"
    }
  }
}
```

**Escopo de usuário** — pelo comando, para servidores que valem em todos os
projetos:

```bash
claude mcp add meu-servidor -- python3 /caminho/absoluto/servidor.py
claude mcp list
claude mcp login sentry        # fluxo OAuth
```

Dentro da sessão:

```
/mcp                      # lista, estado, autenticação
/mcp reconnect tarefas
/mcp disable pesado       # desliga sem remover
```

---

## 6. Custo e segurança — as duas coisas que ninguém avisa

### Custo em contexto

Cada ferramenta MCP conectada tem sua definição carregada no contexto. Vinte
servidores ricos podem consumir dezenas de milhares de tokens **antes da sua
primeira mensagem**.

O Claude Code mitiga isso por padrão com **tool search**: os esquemas ficam
adiados, só os nomes ocupam espaço, e o esquema completo é carregado quando o
modelo decide usar aquela ferramenta. Confira o custo por servidor com:

```
/context
/mcp
```

Regra: conecte o que você usa. Desconecte o resto. Um servidor que você usa
uma vez por mês não deveria estar no `.mcp.json` do projeto.

### Segurança — leia antes de instalar servidor de terceiro

Um servidor MCP é **código que roda na sua máquina, com as suas permissões**, e
cujas descrições de ferramenta **entram no prompt do modelo**. Isso abre três
superfícies distintas:

| Risco | O que acontece |
|---|---|
| **Execução de código** | o servidor roda localmente; pode ler tudo que você lê |
| **Injeção via descrição** | a `description` de uma ferramenta é texto que o modelo obedece. Um servidor malicioso pode instruir o agente a exfiltrar arquivos |
| **Envenenamento de resultado** | o retorno de uma ferramenta também entra no contexto — e também pode conter instruções |

O agravante: as descrições podem mudar depois da instalação (*rug pull*) — o
servidor que você auditou na segunda pode servir outra coisa na quinta.

Práticas mínimas:

1. **Leia o código de servidores de terceiro**, ou use apenas servidores
   oficiais dos fornecedores.
2. **Fixe a versão** (`npx pacote@1.2.3`, não `@latest`).
3. **Escopo mínimo de credencial**: token só-leitura sempre que der.
4. **Trate resultado de ferramenta como entrada não confiável** — se ele vem
   da internet ou de um sistema com conteúdo de terceiros, o texto ali pode
   ser hostil.
5. **Combine com permissões**: `/permissions` aceita regras por ferramenta
   MCP (`mcp__servidor__.*`), e hooks casam com `mcp__servidor__ferramenta`.

Ver [17](17-hooks-permissoes-seguranca.md) para o modelo completo.

---

## 7. Quando MCP, quando não

| Situação | Use |
|---|---|
| Ferramenta que serve a vários clientes / ao time | **MCP** |
| Sistema interno que o agente precisa consultar | **MCP** |
| Procedimento em texto, sem código | **skill** ([18](18-skills-plugins-extensibilidade.md)) |
| Regra que precisa valer sempre | **hook** ([17](17-hooks-permissoes-seguranca.md)) |
| Uma chamada `curl` que você faz uma vez | **`!curl ...`**, e pronto |
| Ferramenta só sua, dentro do seu próprio agente | função no código; MCP é overhead |

> **Opinião:** *MCP é excelente para integração e péssimo como martelo
> universal. O erro comum de 2025–2026 é embrulhar em MCP coisas que
> caberiam numa skill de dez linhas — pagando processo, protocolo e contexto
> por algo que era texto.*

---

## Autoteste

1. Explique M×N → M+N com um exemplo concreto.
2. Quais são os quatro métodos MCP que você precisa implementar para um
   servidor de ferramentas funcionar?
3. Diferença entre tools, resources e prompts — e quem controla cada um.
4. Por que o docstring de uma ferramenta MCP é código de produção?
5. Como você inspeciona um servidor MCP sem nenhum cliente de IA?
6. Um servidor MCP tem 30 ferramentas e o seu contexto começa cheio. O que o
   Claude Code faz por padrão, e o que você pode fazer a mais?
7. Descreva o ataque de injeção via descrição de ferramenta. Por que fixar a
   versão ajuda?
8. Você tem um procedimento de 40 linhas para gerar um relatório, sem código.
   MCP ou skill? Por quê?
