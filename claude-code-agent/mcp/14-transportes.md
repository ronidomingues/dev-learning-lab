# 14 · Transportes — stdio e Streamable HTTP

`Nível: intermediário → avançado` · `Escrito em 01/09/2026` · `Protocolo 2026-07-28`

---

## 1. O que um transporte é, e o que não é

Um transporte (*binding*) define **quatro** coisas, e só essas quatro:

1. como as mensagens são **enquadradas** e entregues;
2. onde vive o **metadado da requisição**;
3. como se sinaliza **cancelamento**;
4. como se **encerra**.

O que ele **não** define: o que as mensagens significam. Os padrões de mensagem
(requisição/resposta, MRTR, assinar/notificar) são do núcleo e **idênticos em todo
transporte**.

Direções permitidas, em qualquer binding:

| | Cliente → Servidor | Servidor → Cliente |
|---|---|---|
| Requisição | ✅ | ❌ |
| Resposta | ❌ | ✅ |
| Notificação | ✅ | ✅ |

---

## 2. stdio

### 2.1 Mecânica

O cliente lança o servidor como **subprocesso**. Conversam pelos fluxos padrão.

| Regra | Detalhe |
|---|---|
| Leitura/escrita | servidor lê JSON-RPC de `stdin`, escreve em `stdout` |
| Enquadramento | **uma mensagem por linha**; a mensagem **não pode** conter nova linha embutida |
| `stderr` | o servidor **PODE** escrever UTF-8 para **qualquer** log: info, debug, erro |
| `stderr` no cliente | **PODE** capturar, encaminhar ou ignorar; **NÃO DEVERIA** supor que saída em `stderr` significa erro |
| `stdout` | o servidor **NÃO PODE** escrever nada que não seja mensagem MCP válida |
| `stdin` | o cliente **NÃO PODE** escrever nada que não seja mensagem MCP válida |
| Respostas | o cliente **NÃO PODE** escrever respostas JSON-RPC |
| Requisições | o servidor **NÃO PODE** escrever requisições JSON-RPC |

> A regra de `stdout` é a causa nº 1 de "meu servidor conecta e cai". Um `print()`,
> um aviso de biblioteca, uma barra de progresso — qualquer byte fora do formato
> corrompe a fita. Log **sempre** em `stderr`.

O `stderr` livre para qualquer nível de log foi esclarecido em `2025-11-25`; antes a
redação sugeria que ele era só para erro, e havia servidores calando o log de info.

### 2.2 Não é só "os fluxos padrão"

> Os fluxos padrão são o canal canônico, mas nada neste binding depende deles exceto o
> ciclo de vida do processo. O formato de fio — uma mensagem JSON-RPC por linha sobre um
> fluxo de bytes bidirecional confiável — funciona igual sobre **soquete Unix**, **TCP**
> ou canal semelhante.

Transportes personalizados sobre fluxo confiável **DEVERIAM reutilizar este
enquadramento** em vez de inventar outro. Só as partes de subprocesso (lançar, `stderr`,
encerrar fechando o fluxo, reiniciar) precisam de equivalentes.

**Consequência prática útil:** um servidor MCP local que precisa aceitar vários clientes
pode escutar num soquete Unix com o mesmo código de enquadramento — e soquete Unix tem
permissão de arquivo, que é um controle de acesso melhor do que "escuto em localhost".

### 2.3 Ciclo de vida

**Encerramento** — o cliente **DEVERIA**:

1. fechar o fluxo de entrada do filho;
2. esperar o servidor sair;
3. se não sair em tempo razoável, terminar à força:
   - POSIX: `SIGTERM`, escalando para `SIGKILL`;
   - Windows: `TerminateProcess` ou *Job Objects*.

Servidores **DEVERIAM** sair prontamente quando o `stdin` fechar ou a leitura devolver
EOF. **É o sinal de encerramento gracioso primário e o único portátil.**

**Morte inesperada:** o cliente **DEVERIA** reiniciar. Como o protocolo é sem estado,
requisições em voo simplesmente se perdem e podem ser reemitidas contra o processo novo.
Assinaturas `subscriptions/listen` precisam ser refeitas.

**Cancelamento:** `notifications/cancelled` com o `id` da requisição. Em stdio há um
canal único compartilhado — não existe fluxo por requisição para fechar.

### 2.4 Quando usar stdio

✅ Dados na máquina do usuário · ✅ um usuário por processo · ✅ sem rede (funciona com
firewall fechado) · ✅ credenciais do ambiente · ✅ desenvolvimento e aprendizado.

❌ Multiusuário · ❌ escala · ❌ servidor de terceiro em que você não confia (a menos
que dentro de container).

---

## 3. Streamable HTTP

### 3.1 A forma geral

- o servidor expõe **um** endpoint HTTP (o *MCP endpoint*), que aceita **POST**;
- cada requisição ou notificação JSON-RPC é **um POST separado**;
- a resposta é **um objeto JSON** ou **um fluxo SSE daquela requisição**;
- interações servidor→cliente vêm embutidas em resultados, via MRTR;
- notificações de mudança vêm no fluxo de resposta de um `subscriptions/listen`.

### 3.2 Segurança do endpoint — leia antes de escrever a primeira linha

1. Servidores **DEVEM** validar o cabeçalho `Origin` em toda conexão, para impedir
   **DNS rebinding**. `Origin` presente e inválido → **HTTP 403 Forbidden** (o corpo
   **PODE** ser um erro JSON-RPC sem `id`).
2. Rodando local, servidores **DEVERIAM** ligar **só** em `127.0.0.1`, nunca em `0.0.0.0`.
3. Servidores **DEVERIAM** implementar autenticação em todas as conexões.

**O ataque que isso evita, em uma frase:** você abre uma página web qualquer; ela faz
requisições para `http://127.0.0.1:8931/mcp`; se o servidor não checar `Origin`, a
página conversa com o servidor MCP que tem acesso aos seus arquivos.

Verificado nesta máquina, com `Origin: http://evil.example`:

```
Invalid Origin header
HTTP 403
```

### 3.3 Enviando mensagens

1. **POST**, sempre.
2. `Accept` **DEVE** listar `application/json` **e** `text/event-stream`.
3. Os cabeçalhos de metadado **DEVEM** estar presentes (§3.5).
4. O corpo é **uma** requisição ou notificação. **Nunca** uma resposta.
5. Notificação aceita → **`202 Accepted`, sem corpo**. Recusada → erro HTTP.
6. Requisição → o servidor devolve `application/json` **ou** `text/event-stream`.
   O cliente **DEVE** suportar os dois.

> Nesta revisão o núcleo **não define nenhuma notificação de cliente para servidor** em
> Streamable HTTP: a única do núcleo, `notifications/cancelled`, é só do stdio — em HTTP
> o cancelamento é fechar o fluxo.

### 3.4 Recebendo — SSE

Num fluxo `text/event-stream` de resposta:

- o servidor **PODE** mandar notificações (`notifications/progress`,
  `notifications/message`) antes da resposta final. Elas **DEVEM** dizer respeito à
  requisição de origem;
- o servidor **NÃO PODE** mandar requisições JSON-RPC independentes nesse fluxo;
- a resposta final **DEVERIA** encerrar o fluxo.

**`X-Accel-Buffering: no`**: o servidor **DEVERIA** enviar esse cabeçalho ao abrir um
SSE. Sem ele, o nginx acumula a resposta num buffer e os eventos chegam em lote —
matando o motivo de existir do fluxo. É a dica operacional mais útil desta página.

**Keep-alive:** em fluxos longos (o `subscriptions/listen`, sobretudo), recomenda-se
emitir periodicamente uma linha de comentário SSE (uma linha começando com `:`, por
exemplo `:\r\n`) para intermediários e timeouts ociosos não fecharem a conexão. Pela
spec de SSE, linha iniciada por dois-pontos é comentário sem dados: o cliente **deve**
ignorá-la e **não** tratá-la como entrada malformada.

**Retomada não existe.** `Last-Event-ID` foi removido. Fluxo quebrado = requisição
perdida; o cliente **DEVE** reemitir com **novo `id`**.

### 3.5 Metadado espelhado em cabeçalhos

O corpo é a fonte da verdade. Os cabeçalhos existem para **intermediários** — balanceador,
gateway, WAF, observabilidade — rotearem e inspecionarem sem abrir o JSON.

| Cabeçalho | Origem no corpo | Obrigatório para |
|---|---|---|
| `MCP-Protocol-Version` | `_meta.…/protocolVersion` | **toda** requisição POST |
| `Mcp-Method` | `method` | **todas** as requisições |
| `Mcp-Name` | `params.name` ou `params.uri` | `tools/call`, `resources/read`, `prompts/get` |
| `Mcp-Param-{Nome}` | propriedade anotada com `x-mcp-header` | quando o valor está presente |

Exemplo real da spec:

```http
POST /mcp HTTP/1.1
Content-Type: application/json
MCP-Protocol-Version: 2026-07-28
Mcp-Method: tools/call
Mcp-Name: get_weather

{"jsonrpc":"2.0","id":1,"method":"tools/call",
 "params":{"name":"get_weather","arguments":{"location":"Seattle, WA"},
 "_meta":{"io.modelcontextprotocol/protocolVersion":"2026-07-28",
          "io.modelcontextprotocol/clientInfo":{"name":"ExampleClient","version":"1.0.0"},
          "io.modelcontextprotocol/clientCapabilities":{}}}}
```

#### Validação obrigatória — e o porquê

Servidores que processam o corpo **DEVEM** rejeitar quando os cabeçalhos não batem com
ele: **400** + `-32020` (`HeaderMismatch`).

> "Isto previne vulnerabilidades quando componentes diferentes da rede confiam em fontes
> de verdade diferentes (por exemplo, um balanceador roteando pelo cabeçalho enquanto o
> servidor MCP executa pelo corpo)."

Esse é um padrão de segurança que vale muito além do MCP: **sempre que um valor é
duplicado em duas camadas, alguém vai divergi-los de propósito.** A defesa é comparar
e recusar.

Medido nesta máquina, `tools/call` sem `Mcp-Name`:

```json
{"jsonrpc":"2.0","id":2,"error":{"code":-32020,
 "message":"mcp-name header does not match the request body's 'name' parameter"}}
```
com `HTTP 400`.

Condições que disparam a falha: cabeçalho obrigatório ausente; valor divergente do corpo
(decodificando antes a sentinela Base64, quando aplicável); caracteres inválidos.

Nota da spec para intermediários: quem aplica política com base nos cabeçalhos espelhados
**deveria** verificar que `MCP-Protocol-Version` indica uma versão que **exige** a
validação cabeçalho-corpo. Se for anterior ou ausente, **deveria rejeitar** em vez de
confiar em cabeçalho não validado.

#### `x-mcp-header` — parâmetro virando cabeçalho

Servidores **PODEM** marcar propriedades do `inputSchema` para serem espelhadas:

```json
{
  "name": "execute_sql",
  "inputSchema": {
    "type": "object",
    "properties": {
      "region": { "type": "string", "x-mcp-header": "Region" },
      "query":  { "type": "string" }
    },
    "required": ["region", "query"]
  }
}
```
→ o cliente acrescenta `Mcp-Param-Region: us-west1`.

O uso é opcional para o servidor, mas **clientes DEVEM suportar**.

Restrições ao valor de `x-mcp-header`:

- não vazio; sintaxe de *token* de nome de campo HTTP (RFC 9110 §5.1);
- sem caracteres de controle, CR ou LF;
- **único** (sem distinção de maiúsculas) dentro do `inputSchema`;
- só tipos primitivos: `integer`, `string`, `boolean`. **`number` não é permitido**;
  inteiro dentro da faixa segura de IEEE754 (−2⁵³+1 a 2⁵³−1);
- só propriedades **estaticamente alcançáveis** da raiz: a cadeia tem de ser composta
  **apenas** de chaves `properties`. Não pode passar por `items`, `oneOf`, `anyOf`,
  `allOf`, `not`, `if`/`then`/`else` ou `$ref`.

Cliente que vê `x-mcp-header` inválido **DEVE excluir aquela ferramenta** do resultado
de `tools/list` (e **deveria** registrar um aviso, com nome e motivo) — para que uma
definição malformada não inutilize as outras.

> ⚠️ Servidores **NÃO DEVERIAM** marcar parâmetro sensível (senha, chave, token, dado
> pessoal) com `x-mcp-header`: valor de cabeçalho é visível a todo intermediário.

#### Codificação de valores

Valor de cabeçalho HTTP só admite ASCII visível, espaço e tabulação. Quando não couber
— acento, controle, espaço nas pontas — o cliente **DEVE** usar a sentinela:

```
Mcp-Param-{Nome}: =?base64?{valorEmBase64}?=
```

O prefixo `=?base64?` e o sufixo `?=` são **sensíveis a maiúsculas** e devem aparecer
exatamente assim. Vale também para `Mcp-Name` — nome de ferramenta e URI de recurso só
têm restrição "SHOULD" de serem seguros para cabeçalho.

| Valor original | Motivo | Cabeçalho |
|---|---|---|
| `us-west1` | ASCII puro | `Mcp-Param-Region: us-west1` |
| `Hello, 世界` | não-ASCII | `=?base64?SGVsbG8sIOS4lueVjA==?=` |
| `" padded "` | espaços nas pontas | `=?base64?IHBhZGRlZCA=?=` |
| `line1\nline2` | nova linha | `=?base64?bGluZTEKbGluZTI=?=` |
| `=?base64?literal?=` | **colide com a sentinela** | `=?base64?PT9iYXNlNjQ/bGl0ZXJhbD89?=` |

A última linha é fina e importante: valor ASCII que **pareça** a sentinela **também**
precisa ser codificado, para não haver ambiguidade.

### 3.6 Códigos de status

| Situação | Status |
|---|---|
| requisição ok | `200` (JSON ou SSE) |
| notificação aceita | `202`, sem corpo |
| `Origin` inválido | **`403`** |
| cabeçalho ≠ corpo, versão não suportada, capacidade faltando, `_meta` incompleto | `400` |
| método RPC inexistente | `404` + `-32601` |
| `GET`/`DELETE` no endpoint (cliente antigo) | `405` (SHOULD) |
| `Mcp-Session-Id` de cliente antigo | **ignorar**, não cunhar nem ecoar |
| `Last-Event-ID` | **ignorar**; fluxos não são retomáveis |

O `404` com corpo JSON-RPC é deliberado: distingue "método não implementado" de um `404`
de servidor HTTP+SSE legado que nem hospeda o endpoint moderno.

> **Divergência medida.** O SDK Python 2.1.1 responde **400**, não 405, a um `GET` no
> endpoint. É um "SHOULD", não um "MUST", e não tem consequência prática (cliente moderno
> não faz GET). Registrado aqui como observação de campo, 01/09/2026.

### 3.7 Cancelamento

Fechar o fluxo SSE da resposta **DEVE** ser tratado pelo servidor como cancelamento
daquela requisição. Como cada requisição tem o seu próprio fluxo, a desconexão é
inequívoca. O servidor **DEVERIA** parar o trabalho assim que possível e **NÃO PODE**
mandar mais nada para aquela requisição.

**Comparação que vale guardar:**

| | stdio | Streamable HTTP |
|---|---|---|
| Cancelar | `notifications/cancelled` | fechar o fluxo |
| Por quê | canal único compartilhado; precisa dizer *qual* | um fluxo por requisição; a desconexão já identifica |

### 3.8 Compatibilidade com o passado

**Detecção de era.** Um cliente que fala moderno e legado **PODE** tentar primeiro uma
requisição moderna. Ao receber `400`, **DEVERIA inspecionar o corpo antes de recuar** —
servidores modernos também usam `400` para `UnsupportedProtocolVersionError`,
`MissingRequiredClientCapabilityError` e falha de validação de cabeçalho.

- corpo com erro JSON-RPC moderno reconhecido → **é servidor moderno**: repita com uma
  versão da lista `supported`, ou corrija a requisição. **Não** recue.
- corpo vazio ou não reconhecido → recue para `initialize` e siga na versão legada.

**Revisões anteriores de Streamable HTTP** (`2025-03-26` a `2025-11-25`) usavam:
sessão via `Mcp-Session-Id` (terminada com `DELETE`), fluxo SSE autônomo aberto com
`GET`, requisições iniciadas pelo servidor no SSE, e retomada por `Last-Event-ID`.
**Nada disso existe nesta revisão.**

**HTTP+SSE de `2024-11-05`** está depreciado desde `2025-03-26` e reclassificado como
*Deprecated* sob a política de ciclo de vida. Servidores que queiram atender clientes
antigos mantêm os dois endpoints antigos ao lado do endpoint MCP novo. Clientes antigos
detectam: tentam POST; se der `400`/`404`/`405` **e** o corpo não for um erro JSON-RPC
moderno reconhecido, fazem `GET` esperando um evento `endpoint` como primeiro do fluxo.

---

## 4. Escolhendo o transporte

| Pergunta | stdio | Streamable HTTP |
|---|---|---|
| Os dados estão na máquina do usuário? | ✅ | ❌ |
| Vários usuários? | ❌ | ✅ |
| Precisa escalar horizontalmente? | ❌ | ✅ |
| Precisa de OAuth? | não (ambiente) | sim |
| Funciona com firewall fechado? | ✅ | ❌ |
| Tem infraestrutura HTTP pronta? | irrelevante | ✅ grande vantagem |
| Custo operacional | ~nenhum | o de um serviço web |
| Superfície de ataque | processo local com os seus privilégios | endpoint na internet |

**Recomendação:** comece em stdio, sempre. Migre para HTTP quando precisar de
multiusuário ou de acesso remoto — e, quando migrar, **monte o servidor MCP dentro da
sua aplicação HTTP existente**, reaproveitando autenticação, log e deploy. Nos dois SDKs
isso é uma linha.

---

## 5. Transportes personalizados

Permitidos. Requisitos: preservar o **formato JSON-RPC**, os **padrões de mensagem** e o
**modelo de metadado por requisição**. **Deveriam** documentar estabelecimento de conexão,
enquadramento e cancelamento.

Sobre fluxo de bytes bidirecional confiável (soquete Unix, TCP), **reutilize o
enquadramento do stdio** em vez de inventar outro.

Existem no ecossistema pontes e proxies (WebSocket, `mcp-remote` e afins). **Opinião
profissional:** use com parcimônia. Cada ponte é mais uma peça que pode mentir sobre a
origem da mensagem e mais um lugar para o token vazar; a spec dedica uma seção inteira
ao risco de **escalonamento de privilégio via proxy stdio**. Ver [19](19-seguranca.md).

---

## 6. Autoteste

1. Quais quatro coisas um transporte define? O que ele **não** define?
2. Por que `print()` derruba um servidor stdio? Onde vai o log, e desde quando isso ficou claro na spec?
3. Como o cliente encerra um servidor stdio, e por que fechar o `stdin` é o sinal primário?
4. Que status HTTP para `Origin` inválido, e qual ataque isso impede?
5. Por que o corpo é a fonte da verdade e os cabeçalhos são espelho? Que erro sai da divergência?
6. Quais tipos podem ser marcados com `x-mcp-header`? Por que `number` não pode?
7. Quando o valor de `Mcp-Name` precisa da sentinela Base64? Dê o caso "fino".
8. Como se cancela em stdio e em HTTP, e por que a diferença não é arbitrária?
9. Um cliente dual-era recebe `400`. O que ele deve fazer **antes** de recuar para `initialize`?
10. Para que serve `X-Accel-Buffering: no`, e o que quebra sem ele?

---

**Anterior:** [13 · JSON-RPC](13-json-rpc-e-a-camada-base.md) · **Próximo:** [15 · Primitivas do servidor](15-primitivas-do-servidor.md) · **Índice:** [00-MAPA](00-MAPA.md)

*Fontes: [Transportes](https://modelcontextprotocol.io/specification/2026-07-28/basic/transports),
[stdio](https://modelcontextprotocol.io/specification/2026-07-28/basic/transports/stdio),
[Streamable HTTP](https://modelcontextprotocol.io/specification/2026-07-28/basic/transports/streamable-http).
Comportamentos de 403, 400/-32020 e GET medidos nesta máquina (`mcp` 2.1.1) em 01/09/2026.*
