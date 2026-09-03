# 15 · Primitivas do servidor — tools, resources, prompts

`Nível: intermediário → avançado` · `Escrito em 01/09/2026` · `Protocolo 2026-07-28`

---

## 1. A regra que separa as três

| Primitiva | Quem decide usar | Como aparece na interface |
|---|---|---|
| **Tool** | o **modelo** | chamada com aprovação do usuário |
| **Resource** | a **aplicação** / o usuário | seletor, anexo, inclusão automática por heurística |
| **Prompt** | o **usuário** | comando de barra, item de menu |

A spec é explícita: para prompts, *"isto se refere a quem decide quando o prompt é
usado, não a quem escreve o conteúdo. O conteúdo é definido pelo servidor."*

---

## 2. Tools

### 2.1 Capacidade

```json
{ "capabilities": { "tools": { "listChanged": true } } }
```

Servidores que declaram `tools` **DEVEM** responder a `tools/list` com o conjunto de
ferramentas disponíveis **para o requisitante**. Esse conjunto:

- **PODE** ser vazio e **PODE** mudar com o tempo;
- **NÃO PODE** variar por conexão nem como efeito colateral de outra requisição;
- **PODE** variar conforme a **autorização apresentada na requisição** — devolvendo só
  as ferramentas que os escopos do chamador permitem — porque credencial é entrada
  **por requisição**, não estado de conexão.

Essa última linha é a reconciliação entre "sem estado" e "cada usuário vê o seu conjunto".
Vale ler duas vezes: **a lista pode depender do token, nunca da conexão.**

Servidores **DEVERIAM** devolver as ferramentas em **ordem determinística** — a mesma
ordem entre requisições quando o conjunto não mudou. Motivo declarado: permite cache
confiável no cliente **e melhora o acerto de cache de prompt do LLM** quando as
ferramentas entram no contexto do modelo. É desempenho e dinheiro, não estética.

### 2.2 Anatomia de uma `Tool`

| Campo | Obrigatório | O que é |
|---|---|---|
| `name` | sim | identificador programático |
| `title` | não | nome para humano |
| `description` | não (na prática, **sim**) | o que o modelo lê para decidir |
| `icons` | não | ícones para a interface |
| `inputSchema` | sim | JSON Schema dos parâmetros. **DEVE** ser objeto válido, nunca `null` |
| `outputSchema` | não | JSON Schema da saída estruturada |
| `annotations` | não | dicas de comportamento (somente-leitura, destrutiva…) |

**Ferramenta sem parâmetros** — duas formas válidas:

```json
{ "type": "object", "additionalProperties": false }   // recomendado: só objeto vazio
{ "type": "object" }                                  // aceita qualquer objeto
```

⚠️ **Anotações são não confiáveis.** A spec: *"para confiança, segurança e proteção,
clientes **DEVEM** considerar as anotações de ferramenta como não confiáveis, a menos que
venham de servidores confiáveis."* Ou seja: `readOnlyHint: true` **não é** garantia de
que a ferramenta não escreve. É uma afirmação do servidor sobre si mesmo.

### 2.3 Nomes de ferramenta

Orientação nova em `2025-11-25`:

- entre **1 e 128** caracteres;
- **sensível a maiúsculas**;
- só letras ASCII, dígitos, `_`, `-` e `.`;
- **sem** espaço, vírgula ou caractere especial;
- únicos **dentro de um servidor**.

Válidos: `getUser`, `DATA_EXPORT_v2`, `admin.tools.list`.

**Colisão entre servidores** é problema do cliente: quem agrega vários servidores
**DEVERIA** implementar desambiguação, tipicamente prefixando com um identificador de
servidor. E **NÃO DEVERIA** usar o `name` do `serverInfo` para isso, porque ele não é
garantidamente único.

### 2.4 `tools/call` e o resultado

Requisição:

```json
{ "jsonrpc":"2.0","id":2,"method":"tools/call",
  "params": { "name":"get_weather","arguments":{"location":"New York"} } }
```

Resultado:

```json
{ "jsonrpc":"2.0","id":2,
  "result": { "resultType":"complete",
              "content":[{"type":"text","text":"Temperatura: 22°C"}],
              "isError": false } }
```

Tipos de conteúdo em `content`:

| `type` | Campos | Uso |
|---|---|---|
| `text` | `text` | o caso comum |
| `image` | `data` (base64), `mimeType` | imagem |
| `audio` | `data` (base64), `mimeType` | áudio |
| `resource_link` | `uri`, `name`, `description`, `mimeType` | **aponta** para um recurso, sem embutir |
| `resource` | `resource` (com `uri`, `mimeType`, `text` ou `blob`) | embute o conteúdo |

Todos aceitam `annotations` opcionais com `audience` (`"user"`, `"assistant"`),
`priority` (0.0–1.0) e `lastModified` (ISO 8601).

> `resource_link` é a ferramenta subutilizada mais útil do MCP. Em vez de devolver
> 40 mil linhas, devolva um resumo e um link. O cliente busca o conteúdo **se** e
> **quando** precisar — e o contexto do modelo é poupado.
> Nota da spec: links devolvidos por ferramenta **não têm garantia** de aparecer em
> `resources/list`.

### 2.5 Conteúdo estruturado

`structuredContent` é **qualquer valor JSON** (objeto, array, string, número, booleano,
nulo) conforme o `outputSchema`, se houver.

- servidor com `outputSchema` **DEVE** produzir resultado conforme o schema;
- cliente **DEVERIA** validar;
- por compatibilidade, quem devolve `structuredContent` **DEVERIA também** devolver o
  JSON serializado num bloco de texto.

> `structuredContent` é dado produzido pelo servidor, e **não tem relação** com
> "structured outputs" de LLM (geração restrita por schema). Nomes parecidos, conceitos
> diferentes.

⚠️ **Medido nesta máquina** (SDK Python 2.1.1): anotar o retorno como `dict` cru ou
`list[str]` **não** gera `outputSchema` e deixa `structured_content` nulo. Só tipos com
schema — `BaseModel`, `TypedDict`, escalares — produzem saída estruturada.

### 2.6 Os dois tipos de erro

| | Erro de protocolo | Erro de execução |
|---|---|---|
| Forma | `error` JSON-RPC | `result` com `isError: true` |
| Casos | ferramenta desconhecida, requisição malformada, erro do servidor | falha de API, validação de entrada, regra de negócio |
| O modelo consegue corrigir? | **improvável** | **sim, e é o objetivo** |
| Cliente | **PODE** passar ao modelo | **DEVERIA** passar ao modelo |

**Erro de validação de entrada é erro de execução.** Isso mudou de propósito em
`2025-11-25` ([SEP-1303](https://github.com/modelcontextprotocol/modelcontextprotocol/issues/1303)),
para o modelo se autocorrigir em vez de desistir.

```json
{ "jsonrpc":"2.0","id":4,
  "result": { "resultType":"complete",
    "content":[{"type":"text",
      "text":"Data de partida inválida: deve ser futura. Hoje é 08/08/2025."}],
    "isError": true } }
```

**No SDK Python 2.x:** só `ToolError` e `ResourceError` têm a mensagem entregue ao modelo.
Qualquer outra exceção vira `Error executing tool <nome>`, sem texto — para não vazar
caminho, SQL ou segredo num crash. Ver [06 · exemplo 3](06-exemplos.md#3-erro-que-o-modelo-consegue-corrigir).

### 2.7 Ferramentas com estado

A spec traz uma seção inteira, **não normativa**, sobre isto — sinal de quanto o assunto
doeu depois da remoção das sessões.

O protocolo **não tem** conceito de handle: do ponto de vista do fio, um handle é uma
string comum num resultado e um argumento comum na chamada seguinte.

```jsonc
// → tools/call
{ "name": "create_basket", "arguments": {} }
// ← result
{ "content":[{"type":"text","text":"Created basket bsk_a1b2c3"}],
  "structuredContent": { "basket_id": "bsk_a1b2c3" } }
// → tools/call
{ "name": "add_item", "arguments": { "basket_id": "bsk_a1b2c3", "sku": "..." } }
```

**O modelo é responsável por carregar o handle adiante.** Isso tem uma consequência
que a spec não diz e a prática mostra: se o handle sair da janela de contexto, ele se
perde. Handles devem ser curtos, aparecer no texto e ser fáceis de reencontrar.

Os quatro cuidados que a spec lista:

1. **Autorização.** Em servidor autenticado, o handle é um **nome**, não uma
   **capacidade**: valide a autorização do chamador contra o handle a **cada** chamada.
   Em servidor não autenticado o handle é necessariamente um *bearer token* — gere com
   entropia suficiente (UUIDv4, por exemplo) e dê vida útil limitada.
2. **Opacidade.** Handle com estrutura visível convida a adivinhar. Use identificador opaco.
3. **Vida útil.** Como o handle sobrevive a qualquer conexão, **declare a política de
   retenção na descrição da ferramenta de criação** ("cestas expiram após 24 h de
   inatividade"), para o modelo ver isso quando decidir criar estado.
4. **Erro de expiração.** Chamada com handle expirado ou desconhecido deve devolver um
   **erro de execução dizendo isso**, para o modelo criar outro.

### 2.8 Segurança de ferramentas

Servidores **DEVEM**: validar toda entrada; implementar controle de acesso; **limitar a
taxa** de invocação; sanitizar saída.

Clientes **DEVERIAM**: pedir confirmação em operação sensível; **mostrar os argumentos ao
usuário antes de chamar**, para evitar exfiltração maliciosa ou acidental; validar o
resultado antes de passar ao LLM; respeitar as regras de `$ref` ao validar; aplicar
timeout; registrar o uso para auditoria.

---

## 3. Resources

### 3.1 Capacidade

```json
{ "capabilities": { "resources": { "listChanged": true, "subscribe": true } } }
```

`listChanged` e `subscribe` são independentes: um, outro, os dois, ou nenhum
(`"resources": {}`).

Valem as mesmas regras de `tools/list`: o conjunto **não pode** variar por conexão,
**pode** variar pela autorização apresentada.

### 3.2 Métodos

| Método | O que faz | Suporta |
|---|---|---|
| `resources/list` | lista recursos | paginação, cache |
| `resources/read` | lê o conteúdo | cache, **`input_required`** |
| `resources/templates/list` | lista templates de URI (RFC 6570) | paginação, cache, autocompletar |

`resources/read` **PODE** devolver **vários** conteúdos numa resposta — por exemplo, o
conteúdo de vários arquivos ao ler um "diretório".

### 3.3 Conteúdo

```json
{ "uri": "file:///exemplo.txt", "mimeType": "text/plain", "text": "conteúdo" }
{ "uri": "file:///exemplo.png", "mimeType": "image/png", "blob": "base64..." }
```

Campos de um `Resource`: `uri`, `name`, `title`, `description`, `icons`, `mimeType`, `size`.

### 3.4 Esquemas de URI

| Esquema | Uso |
|---|---|
| `https://` | recurso na web que **o cliente consegue buscar sozinho**. Se ele precisa passar pelo servidor, use outro esquema |
| `file://` | comporta-se como sistema de arquivos (não precisa ser um de verdade). Tipo MIME XDG como `inode/directory` marca não-arquivos |
| `git://` | integração com controle de versão |
| personalizado | conforme a RFC 3986 |

### 3.5 Assinaturas

Nada de `resources/subscribe`. O cliente abre **um** `subscriptions/listen` com as URIs
em `notifications.resourceSubscriptions`. O servidor confirma e depois entrega:

```json
{ "jsonrpc":"2.0","method":"notifications/resources/updated",
  "params": { "_meta": { "io.modelcontextprotocol/subscriptionId": 4 },
              "uri": "file:///project/src/main.rs" } }
```

O `subscriptionId` é **obrigatório** e é como o cliente correlaciona — necessário
porque, no stdio, todas as notificações compartilham o mesmo `stdout`.

### 3.6 Erros e segurança

- recurso inexistente → **`-32602`** (Invalid Params). Erro interno → `-32603`.
- por compatibilidade, clientes **DEVERIAM** aceitar também `-32002`, usado até `2025-11-25`.
- servidores **NÃO PODEM** devolver `contents` vazio para recurso inexistente: é
  ambíguo — pode significar "existe e está vazio" ou "não existe".

Segurança: validar toda URI; controlar acesso a recurso sensível; codificar binário
corretamente; checar permissão antes da operação; **sanitizar caminho contra travessia
de diretório** em `file://`.

### 3.7 Por que recursos são subutilizados — e o que fazer

Fato: em 2026 o suporte a recursos nos clientes é bem menor que o de ferramentas.

Motivos, em ordem de peso:

1. **Exige UI que muitos hosts não construíram** — seletor, árvore, busca.
2. **Exige ação do usuário**, e o usuário não sabe que existem.
3. **Ferramenta funciona em todo lugar**, então o autor do servidor escolhe ferramenta.

**Recomendação prática:** exponha o dado como **ferramenta** (para funcionar em todo
lugar) **e** como **recurso** (para o host que souber usar), e use `resource_link` nos
resultados de ferramenta. É pouco código extra e o retorno de contexto poupado é grande.

---

## 4. Prompts

### 4.1 Capacidade e métodos

```json
{ "capabilities": { "prompts": { "listChanged": true } } }
```

| Método | O que faz |
|---|---|
| `prompts/list` | lista prompts (paginação, cache) |
| `prompts/get` | resolve com argumentos (aceita `input_required`) |

Argumentos podem ser autocompletados via `completion/complete`.

### 4.2 Forma

```json
{ "name": "code_review", "title": "Request Code Review",
  "description": "Pede ao LLM que analise a qualidade do código",
  "arguments": [ { "name": "code", "description": "O código a revisar", "required": true } ] }
```

`prompts/get` devolve `messages`, cada uma com `role` (`user`/`assistant`) e `content`
de um dos tipos: `text`, `image`, `audio`, `resource_link`, `resource`.

### 4.3 Erros

- nome inválido → `-32602`;
- argumento obrigatório faltando → `-32602`;
- erro interno → `-32603`.

### 4.4 Para que prompts servem de verdade

Opinião profissional, marcada como tal: **prompts são a primitiva mais mal aproveitada
do MCP**, e por um motivo cultural, não técnico. Eles são o lugar certo para guardar o
conhecimento de *como pedir bem* — aquele arquivo `prompts.md` que toda equipe tem e
ninguém acha.

Bons usos:

- fluxos de várias etapas com formato de saída fixo (revisão, triagem, relatório);
- padronizar uma tarefa entre pessoas do time;
- pôr palavras na boca do assistente (`AssistantMessage`) para ancorar o formato;
- embutir um recurso do servidor no meio do roteiro.

Maus usos: coisa que o modelo já faz bem sem roteiro; e qualquer coisa que dependa de o
usuário adivinhar que o prompt existe.

---

## 5. Cache — `ttlMs` e `cacheScope`

Novo em `2026-07-28`. **Obrigatórios** nos resultados de `tools/list`, `prompts/list`,
`resources/list`, `resources/read` e `resources/templates/list`.

| Campo | O que é |
|---|---|
| `ttlMs` | dica de frescor em milissegundos — por quanto tempo o cliente pode cachear |
| `cacheScope` | `"public"` ou `"private"` — se intermediários compartilhados podem cachear |

Complementam as notificações `listChanged`, não as substituem: cache reduz *polling*;
notificação avisa de mudança.

Observado nesta máquina: o SDK Python 2.1.1 devolve `ttlMs: 0` e `cacheScope: "private"`
por padrão — ou seja, **não cacheie**. Se a sua lista de ferramentas é estável, configure
`cache_hints` no `MCPServer` e economize viagens.

---

## 6. Autoteste

1. O que decide se algo deve ser tool, resource ou prompt?
2. Como o conjunto de `tools/list` pode variar por usuário sem violar o modelo sem estado?
3. Por que a spec pede ordem determinística em `tools/list`? Cite os dois ganhos.
4. Por que anotações de ferramenta são "não confiáveis"? O que `readOnlyHint: true` garante?
5. Quando usar `resource_link` em vez de `resource` embutido?
6. Diferencie erro de protocolo e erro de execução, com um exemplo de cada.
7. Cite os quatro cuidados da spec ao projetar handles de estado.
8. Por que um handle não é autenticação, mesmo sendo imprevisível?
9. Por que o servidor não pode devolver `contents: []` para recurso inexistente?
10. Que par de campos novos de `2026-07-28` controla cache, e o que cada um significa?

---

**Anterior:** [14 · Transportes](14-transportes.md) · **Próximo:** [16 · Primitivas do cliente](16-primitivas-do-cliente.md) · **Índice:** [00-MAPA](00-MAPA.md)

*Fontes: [Tools](https://modelcontextprotocol.io/specification/2026-07-28/server/tools),
[Resources](https://modelcontextprotocol.io/specification/2026-07-28/server/resources),
[Prompts](https://modelcontextprotocol.io/specification/2026-07-28/server/prompts),
[Changelog 2026-07-28](https://modelcontextprotocol.io/specification/2026-07-28/changelog).
Comportamentos do SDK medidos nesta máquina (`mcp` 2.1.1) em 01/09/2026.*
