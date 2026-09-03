# 20 · MCP — conectar o agente às suas ferramentas

> **Nível:** avançado · **Atualizado em:** 13/08/2026 · Claude Code 2.1.231

MCP (*Model Context Protocol*, protocolo de contexto de modelo) é um padrão aberto,
anunciado pela Anthropic em novembro de 2024, para ligar agentes a sistemas externos:
Jira, GitHub, Sentry, banco de dados, Figma, o que você escrever.

Vou adiantar a conclusão, porque ela é impopular e vai poupar seu tempo: **MCP é excelente
para o que não tem CLI, e frequentemente a escolha errada para o que tem.**

---

## 1. O que MCP resolve

Sem MCP, para o agente saber o que diz o ticket ENG-4521, você copia e cola. Com MCP, ele
consulta direto. O ganho é real:

- *"Implemente o que está descrito no ENG-4521 e abra o PR."*
- *"Confira no Sentry se aquele erro parou depois do deploy."*
- *"Ache no banco 10 usuários que usaram o recurso X."*

Um servidor MCP expõe três coisas: **ferramentas** (ações), **recursos** (dados que você
referencia com `@`) e **prompts** (que viram comandos de barra).

---

## 2. Instalar um servidor

### HTTP (o mais comum hoje)

```bash
claude mcp add --transport http notion https://mcp.notion.com/mcp
```

Com cabeçalho de autenticação:

```bash
claude mcp add --transport http api-interna https://api.empresa.com/mcp \
  --header "Authorization: Bearer ${MEU_TOKEN}"
```

### SSE (legado, ainda usado)

```bash
claude mcp add --transport sse asana https://mcp.asana.com/sse
```

### stdio (processo local)

```bash
claude mcp add --env AIRTABLE_API_KEY=SUA_CHAVE --transport stdio airtable \
  -- npx -y airtable-mcp-server
```

> **A pegadinha do `--`:** ele separa as opções do `claude` do comando que será executado.
> Sem ele, `npx` e seus argumentos são interpretados como opções do `claude mcp add`.

### Escopos

```bash
claude mcp add --transport http stripe --scope local   https://mcp.stripe.com  # só você, só aqui (padrão)
claude mcp add --transport http stripe --scope project https://mcp.stripe.com  # vai para .mcp.json, versionado
claude mcp add --transport http stripe --scope user    https://mcp.stripe.com  # você, em todos os projetos
```

`.mcp.json` versionado é o caminho para times. Ele exige aprovação de quem clona — o que é
proteção, não burocracia: um servidor MCP injeta ferramentas no seu agente.

### Gerenciar

```bash
claude mcp list                 # servidores e estado de saúde
claude mcp login <nome>         # fluxo OAuth
claude mcp logout <nome>
```
```
/mcp                            # dentro da sessão: status, habilitar, desabilitar, reconectar
```

Nomes reservados que você não pode usar: `workspace`, `claude-in-chrome`, `computer-use`,
`Claude Preview`, `Claude Browser`.

---

## 3. O custo de contexto — leia antes de instalar cinco servidores

Cada ferramenta MCP entra no contexto como nome + descrição + esquema. Um servidor com 40
ferramentas pode custar **dezenas de milhares de tokens em toda mensagem**. É o único custo
de contexto **recorrente** do sistema; todos os outros são pontuais.

Mitigação embutida: **as definições são adiadas por padrão.** Só os nomes entram; o esquema
completo é carregado sob demanda pela ferramenta `ToolSearch`. Isso reduz muito o custo,
mas acrescenta uma chamada antes do primeiro uso.

Diagnóstico:

```
/context all      # mostra quanto cada servidor está custando
/usage            # atribuição: quanto do seu uso recente veio de cada servidor MCP
```

### A recomendação impopular: prefira a CLI

| Necessidade | MCP | CLI equivalente |
|---|---|---|
| GitHub | servidor `github` | **`gh`** |
| AWS | servidor `aws` | **`aws`** |
| Google Cloud | servidor | **`gcloud`** |
| Sentry | servidor `sentry` | **`sentry-cli`** |
| Banco Postgres | servidor | **`psql`** |
| Kubernetes | servidor | **`kubectl`** |

**Por que a CLI costuma vencer:** ela custa **zero** de contexto até ser usada — não existe
listagem de ferramentas para carregar. O agente já sabe usar `gh` e `kubectl` (estão no
treino), e você controla o acesso com regras de permissão comuns:
`Bash(gh pr view *)`, `Bash(gh pr create *)`.

**Quando MCP ganha, sem discussão:**

- não existe CLI (Figma, Notion, ferramenta interna da empresa);
- a autenticação é OAuth interativa e a CLI não a suporta;
- você quer **recursos** (`@servidor:recurso`) além de ações;
- o servidor **empurra** eventos para a sessão (canais: Telegram, Discord, webhook);
- a organização quer um ponto único de controle e auditoria de acesso.

*(Isto é opinião profissional fundamentada, não consenso. A documentação oficial faz a mesma
recomendação na seção de custos: "prefira CLI quando existir".)*

---

## 4. Usar dentro da sessão

**Ferramentas** aparecem como `mcp__<servidor>__<ferramenta>` — é esse o nome em regras de
permissão e matchers de hook:

```json
{
  "permissions": {
    "allow": ["mcp__jira__get_issue"],
    "deny": ["mcp__jira__delete_issue", "mcp__postgres__execute"]
  }
}
```

**Recursos** com `@`:

```
@jira:ENG-4521 implemente o que está descrito aqui
```

**Prompts** do servidor viram comandos de barra: `/servidor:nome-do-prompt`.

---

## 5. Escrever o seu

Vale a pena quando existe um sistema interno sem CLI. Esboço mínimo em Node:

```js
// servidor-mcp.mjs — servidor stdio mínimo, sem dependências além do SDK oficial
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";

const server = new Server(
  { name: "sistema-interno", version: "1.0.0" },
  { capabilities: { tools: {} } },
);

server.setRequestHandler("tools/list", async () => ({
  tools: [{
    name: "buscar_pedido",
    // A descrição é o que o modelo lê para decidir usar. Escreva-a como documentação pública.
    description: "Busca um pedido pelo número no sistema interno. Use quando pedirem status ou detalhe de um pedido.",
    inputSchema: {
      type: "object",
      properties: { numero: { type: "string", description: "Número do pedido, ex.: PED-1234" } },
      required: ["numero"],
    },
  }],
}));

server.setRequestHandler("tools/call", async (req) => {
  if (req.params.name !== "buscar_pedido") throw new Error("ferramenta desconhecida");
  const r = await fetch(`https://interno.empresa.com/pedidos/${req.params.arguments.numero}`, {
    headers: { authorization: `Bearer ${process.env.TOKEN_INTERNO}` },
  });
  if (!r.ok) return { content: [{ type: "text", text: `erro ${r.status}` }], isError: true };
  return { content: [{ type: "text", text: JSON.stringify(await r.json(), null, 2) }] };
});

await server.connect(new StdioServerTransport());
```

```bash
claude mcp add --env TOKEN_INTERNO=xxx --transport stdio interno -- node ./servidor-mcp.mjs
```

> **Não executado neste ambiente** (exige o SDK `@modelcontextprotocol/sdk`, e este projeto é
> zero-dependência). Trate como esqueleto de referência; a API canônica está em
> [modelcontextprotocol.io](https://modelcontextprotocol.io).

Duas regras ao escrever servidor, que valem mais que o código:

1. **Poucas ferramentas, bem descritas.** Vinte ferramentas mal descritas custam contexto e
   confundem a escolha. Cinco boas resolvem mais.
2. **Devolva pouco.** Se a ferramenta retorna 5 mil linhas de JSON, tudo isso entra no
   contexto. Resuma, pagine, filtre — do lado do servidor.

---

## 6. Segurança

Um servidor MCP **injeta ferramentas no seu agente**. Instalar um é comparável a instalar uma
extensão de navegador com permissão total.

| Risco | Defesa |
|---|---|
| Servidor malicioso | Só use os que você escreveu ou de fornecedores confiáveis. A Anthropic revisa conectores do Diretório contra critérios de listagem, mas **não audita segurança** |
| Injeção de prompt via dados do servidor | O conteúdo devolvido é texto que entra no contexto. Um ticket do Jira pode conter "ignore instruções anteriores…" ([`24`](24-seguranca.md)) |
| Vazamento de credencial | Nunca ponha segredo direto no `.mcp.json` versionado — use variável de ambiente |
| Excesso de permissão | `deny` explícito nas ferramentas destrutivas |

Controles de organização:

```json
{
  "allowedMcpServers": [{ "serverName": "github" }],
  "deniedMcpServers": [{ "serverName": "filesystem" }],
  "allowManagedMcpServersOnly": true,
  "enabledMcpjsonServers": ["memory", "github"]
}
```

---

## 7. Os cinco porquês: por que meu servidor MCP deixou tudo lento?

1. **Por que ficou lento e caro?**
   As definições das ferramentas dele entram no contexto de **toda** mensagem.
2. **Por que não carregar só quando usar?**
   É o que a busca de ferramentas faz por padrão — mas o modelo precisa saber que a
   ferramenta **existe** para querer usá-la. Os nomes ficam sempre visíveis.
3. **Por que precisa saber que existe?**
   Porque a decisão de usar uma ferramenta é uma escolha do modelo dentro do contexto. O que
   não está no contexto, para ele, não existe.
4. **Não dá para o Claude Code adivinhar quais servidores são relevantes?**
   Adivinhar exigiria julgamento — ou seja, outra chamada ao modelo, com custo e latência
   próprios. Foi a troca escolhida: nomes sempre, esquemas sob demanda.
5. **Então o que eu faço?**
   Instale poucos servidores; desabilite os inativos com `/mcp`; e, quando existir CLI, use a
   CLI. *(Parada legítima: trade-off explícito entre custo de contexto e descobribilidade.)*

---

## Autoteste

1. O que MCP resolve, e quais são as três coisas que um servidor pode expor?
2. Por que a CLI (`gh`, `kubectl`) costuma vencer o servidor MCP equivalente?
3. Cite quatro situações em que MCP ganha sem discussão.
4. Qual a pegadinha do `--` no `claude mcp add` com transporte stdio?
5. Como se chamam as ferramentas MCP em regras de permissão? Escreva uma regra de negação.
6. Quais são as duas regras de ouro ao escrever um servidor MCP?
7. Por que instalar um servidor MCP é comparável a instalar uma extensão de navegador?
8. Por que os nomes das ferramentas ficam no contexto mesmo com carregamento adiado?
