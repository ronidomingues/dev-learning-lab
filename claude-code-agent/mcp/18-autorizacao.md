# 18 · Autorização — OAuth 2.1 para servidores MCP remotos

`Nível: avançado` · `Escrito em 01/09/2026` · `Protocolo 2026-07-28`

> **A parte mais difícil do MCP.** Se você é iniciante, adie: escreva três servidores
> **stdio** antes de encostar aqui. Em stdio, autorização é uma variável de ambiente.
>
> Pré-requisito real: entender OAuth 2.1 e JWT. Se você não sabe o que é `aud`, `iss`,
> PKCE ou *bearer token*, leia [jwt](../jwt/00-MAPA.md) antes.

---

## 1. Quando isto se aplica

| Transporte | Regra da spec |
|---|---|
| **stdio** | **NÃO DEVERIA** seguir esta especificação. Pegue credenciais **do ambiente** |
| **HTTP** | **DEVERIA** conformar-se a esta especificação |
| outro | **DEVE** seguir as boas práticas de segurança do próprio protocolo |

Autorização é **OPCIONAL** no MCP. Mas se o seu servidor é remoto e toca dado de alguém,
não é opcional na prática.

---

## 2. Os papéis, em vocabulário OAuth

| Papel MCP | Papel OAuth 2.1 |
|---|---|
| **Servidor MCP protegido** | *Resource Server* — aceita e responde a requisições com token |
| **Cliente MCP** | *Client* — faz requisições em nome do dono do recurso |
| **Servidor de autorização (AS)** | interage com o usuário e emite os tokens |

O AS **pode** ser o mesmo serviço do servidor MCP ou uma entidade separada (Auth0, Okta,
Entra ID, Keycloak, o IdP da empresa). A spec não define como o AS funciona por dentro —
define como o servidor MCP **aponta** para ele.

> A decisão de projeto que resolve o problema: o servidor MCP **não é** um servidor de
> autorização. Ele é um *resource server*. Isso permite plugá-lo no IdP que a empresa já
> tem, em vez de reimplementar OAuth.

---

## 3. Os padrões usados

Um subconjunto deliberado, "para garantir segurança e interoperabilidade mantendo a
simplicidade":

| Padrão | Papel |
|---|---|
| **OAuth 2.1** (draft-ietf-oauth-v2-1-13) | a base: PKCE obrigatório, sem *implicit*, sem *password grant* |
| **RFC 6750** | uso do *bearer token*, cabeçalho `Authorization`, `WWW-Authenticate` |
| **RFC 8414** | metadados do servidor de autorização |
| **RFC 9728** | **Protected Resource Metadata** — como o servidor MCP aponta para o AS |
| **RFC 8707** | *Resource Indicators* — o parâmetro `resource` |
| **RFC 9207** | identificação do emissor: o parâmetro `iss` na resposta de autorização |
| **RFC 7591** | *Dynamic Client Registration* — ⚠️ **depreciado**, mantido por compatibilidade |
| **CIMD** (draft-ietf-oauth-client-id-metadata-document-00) | **Client ID Metadata Documents**, o registro recomendado |
| **OpenID Connect Discovery 1.0** | descoberta alternativa do AS |

Requisitos duros:

1. o AS **DEVE** implementar OAuth 2.1, para cliente confidencial e público;
2. AS e clientes **DEVERIAM** suportar **CIMD**;
3. AS e clientes **PODEM** suportar DCR (RFC 7591) — depreciado;
4. servidores MCP **DEVEM** implementar **RFC 9728**; clientes **DEVEM** usá-la para
   descobrir o AS;
5. o AS **DEVE** oferecer ao menos um mecanismo de descoberta: **RFC 8414** ou
   **OIDC Discovery**. Clientes **DEVEM** suportar **os dois**.

---

## 4. O fluxo completo

```mermaid
sequenceDiagram
    participant B as Navegador
    participant C as Cliente MCP
    participant M as Servidor MCP (Resource Server)
    participant A as Servidor de Autorização

    C->>M: requisição MCP sem token
    M->>C: 401 + WWW-Authenticate
    Note over C: extrai resource_metadata do WWW-Authenticate
    C->>M: GET Protected Resource Metadata
    M->>C: metadados
    Note over C: escolhe o AS a usar
    C->>A: GET metadados do AS (RFC 8414 e/ou OIDC, em ordem de prioridade)
    A-->>C: metadados do AS
    alt Client ID Metadata Documents
        Note over C: usa uma URL HTTPS como client_id
        A->>C: busca o metadado na URL do client_id
        C-->>A: documento JSON
    else Dynamic Client Registration (depreciado)
        C->>A: POST /register
        A->>C: credenciais do cliente
    else cliente pré-registrado
        Note over C: usa o client_id existente
    end
    Note over C: gera PKCE, inclui `resource`,<br/>aplica a estratégia de escopo,<br/>REGISTRA o issuer esperado
    C->>B: abre o navegador na URL de autorização
    B->>A: requisição de autorização (com `resource`)
    Note over A: usuário autoriza
    A->>B: redireciona ao callback com code + iss
    B->>C: código de autorização
    Note over C: VALIDA `iss` contra o issuer registrado (RFC 9207)
    C->>A: troca code + code_verifier + resource
    A->>C: access token (+ refresh token)
    C->>M: requisição MCP com o token
    M-->>C: resposta MCP
```

---

## 5. Descoberta — RFC 9728

O servidor MCP responde `401` com um `WWW-Authenticate` que aponta para o seu documento
de metadados:

```http
HTTP/1.1 401 Unauthorized
WWW-Authenticate: Bearer resource_metadata="https://mcp.exemplo.com/.well-known/oauth-protected-resource",
                         scope="files:read"
```

O cliente busca esse documento, descobre `authorization_servers` e `scopes_supported`,
escolhe um AS, e daí busca os metadados do AS (RFC 8414 e/ou OIDC).

> Desde `2025-11-25`, alinhado à RFC 9728: o cabeçalho `WWW-Authenticate` é **opcional**,
> com recuo para o endpoint `.well-known`.

⚠️ **Este passo é um vetor de SSRF.** O cliente busca URLs que um servidor potencialmente
malicioso escolheu. Ver [19 · SSRF](19-seguranca.md#4-ssrf-na-descoberta-de-oauth).

---

## 6. Registro de cliente

Três mecanismos, em ordem de prioridade:

### 6.1 Client ID Metadata Documents (CIMD) — recomendado

O `client_id` **é uma URL HTTPS** que serve um documento JSON com os metadados do
cliente. O AS detecta que o `client_id` tem forma de URL, busca o documento, valida os
metadados e os `redirect_uris`.

**Por que é melhor que DCR:** não há registro a criar, não há segredo a guardar, e a
posse do domínio prova quem você é. Resolve o problema de um cliente distribuído em
milhares de máquinas precisar de um `client_id` cada.

**O que ele não prova:** qual processo local está escutando num `redirect_uri` de
`localhost`. Ver [19 · Impersonação de redirect de localhost](19-seguranca.md).

⚠️ Também é vetor de SSRF, agora **contra o AS**: um cliente malicioso faz o AS buscar
uma URL arbitrária. Os mesmos controles de rede se aplicam.

### 6.2 Pré-registro

O clássico: você registra o cliente à mão no IdP e guarda o `client_id`. Serve bem para
cliente corporativo interno.

### 6.3 DCR (RFC 7591) ⚠️ depreciado

Depreciado em `2026-07-28` em favor de CIMD. Mantido só para compatibilidade com AS que
não suportam CIMD. **Não adote em implementação nova.**

Além de depreciado, é a peça central do ataque de **confused deputy** contra proxies MCP.
Ver [19](19-seguranca.md).

---

## 7. O parâmetro `resource` (RFC 8707)

Clientes MCP **DEVEM** implementar *Resource Indicators*. O parâmetro `resource`:

1. **DEVE** estar **nas duas** requisições: autorização **e** token;
2. **DEVE** identificar o servidor MCP com que o token será usado;
3. **DEVE** usar a **URI canônica** do servidor MCP;
4. **DEVE** ser enviado **mesmo que o AS não o suporte**.

**Por que existe:** sem ele, um servidor MCP malicioso pode induzir o cliente a obter um
token que serve em **outro** servidor. Com ele, o token nasce amarrado à audiência certa.

### URI canônica

| Válidas | Inválidas |
|---|---|
| `https://mcp.exemplo.com/mcp` | `mcp.exemplo.com` (sem esquema) |
| `https://mcp.exemplo.com` | `https://mcp.exemplo.com#frag` (com fragmento) |
| `https://mcp.exemplo.com:8443` | |
| `https://mcp.exemplo.com/server/mcp` | |

Use a URI **mais específica** que você puder. A forma canônica usa esquema e host em
minúsculas, mas implementações **DEVERIAM** aceitar maiúsculas por robustez. Prefira
**sem** barra final, salvo quando ela for semanticamente significativa.

Na requisição: `&resource=https%3A%2F%2Fmcp.exemplo.com`

---

## 8. Validação da resposta de autorização (RFC 9207)

Novidade de `2026-07-28`, e a defesa contra **ataques de mix-up**.

**Antes** de redirecionar o navegador, o cliente **DEVE registrar** o valor `issuer` dos
metadados validados do AS escolhido, associado ao mesmo registro por requisição que
guarda o `code_verifier` do PKCE (e o `state`, se houver).

Ao receber a resposta, **antes** de mandar o código a qualquer endpoint de token:

| `authorization_response_iss_parameter_supported` | `iss` presente? | Ação do cliente |
|---|---|---|
| `true` | sim | comparar com o issuer registrado, por **comparação simples de string** (RFC 3986 §6.2.1) |
| `true` | não | **rejeitar** |
| `false`/ausente | sim | comparar mesmo assim |
| `false`/ausente | não | prosseguir |

Depois de decodificar o `iss` do corpo `application/x-www-form-urlencoded`, o cliente
**NÃO PODE** aplicar normalização antes de comparar: nada de dobrar maiúsculas de esquema
ou host, elidir porta padrão, acrescentar barra final ou normalizar *percent-encoding*.

A validação vale **também para respostas de erro**: se não bater, o cliente **NÃO PODE**
agir nem exibir `error`, `error_description` ou `error_uri`.

> **Nota da spec:** uma revisão futura deve elevar a inclusão de `iss` de **SHOULD** para
> **MUST**. Emita e valide desde já.
>
> **PKCE sozinho não previne mix-up**, porque o cliente transmite o `code_verifier` ao
> endpoint de token do atacante. E *resource indicators* não ajudam quando o AS do
> atacante intercepta antes do AS honesto.

---

## 9. Uso do token

```http
GET /mcp HTTP/1.1
Host: mcp.exemplo.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

- **DEVE** ir no cabeçalho `Authorization`, em **toda** requisição HTTP;
- **NÃO PODE** ir na *query string* da URI (vaza em log de proxy, em `Referer`, em histórico).

### 9.1 Validação pelo servidor — a regra que não se negocia

O servidor MCP, como *resource server*, **DEVE**:

- validar o token conforme OAuth 2.1 §5.2;
- **validar que o token foi emitido especificamente para ele como audiência pretendida**
  (RFC 8707 §2);
- responder **401** a token inválido ou expirado;
- **aceitar apenas tokens válidos para os seus próprios recursos**;
- **NÃO PODE aceitar nem repassar nenhum outro token.**

E o cliente **NÃO PODE** mandar ao servidor MCP tokens que não tenham sido emitidos pelo
AS daquele servidor.

> **Token passthrough é explicitamente proibido.** Aceitar um token emitido para outro
> serviço, ou repassar o token do cliente adiante sem trocar, é o anti-padrão nomeado na
> spec. Ver [19 · Token passthrough](19-seguranca.md#3-token-passthrough).

Se você implementar **uma única coisa** deste arquivo, que seja **validar a audiência**.

---

## 10. Escopos

### 10.1 Estratégia de seleção

Servidores **DEVERIAM** incluir `scope` no `WWW-Authenticate` (RFC 6750 §3), indicando os
escopos necessários para aquele acesso.

Os escopos do desafio **PODEM** coincidir com `scopes_supported`, ser subconjunto,
superconjunto, ou um conjunto alternativo que não é nem um nem outro. Clientes
**NÃO PODEM** supor relação de conjunto nenhuma, e **DEVEM** tratar os escopos do desafio
como **autoritativos para a operação atual**.

Ordem de prioridade do cliente na autorização inicial:

1. usar o `scope` do `WWW-Authenticate` do `401`, se houver;
2. senão, usar **todos** os escopos de `scopes_supported` da PRM, omitindo o parâmetro se
   `scopes_supported` for indefinido.

> O passo 2 parece contradizer o menor privilégio, e a spec explica por quê: clientes MCP
> são de propósito geral e não têm conhecimento de domínio para escolher escopo. Pedir
> tudo que está listado deixa a decisão com o AS e com o usuário na tela de consentimento.
> **Por isso `scopes_supported` deve conter só o conjunto mínimo para a funcionalidade
> básica** — o resto vem por *step-up*.

### 10.2 Escopo insuficiente em tempo de execução

```http
HTTP/1.1 403 Forbidden
WWW-Authenticate: Bearer error="insufficient_scope",
                         scope="files:write",
                         resource_metadata="https://mcp.exemplo.com/.well-known/oauth-protected-resource",
                         error_description="File write permission required for this operation"
```

O servidor **DEVERIA** incluir **todos** os escopos necessários para a operação atual
**num único desafio**. Desafiar incrementalmente — devolver um escopo faltante, depois
outro na retentativa — força várias idas ao AS para uma operação só e degrada a
experiência. Os escopos podem ser determinados dinamicamente pelos argumentos, mas, uma
vez determinados, saem juntos.

### 10.3 Fluxo de step-up

1. **analisar** o erro (do AS ou do `WWW-Authenticate`);
2. **determinar os escopos** calculando a **união** do conjunto pedido antes com os do
   desafio atual — isso preserva permissões já concedidas para outras operações;
3. **(re)autorizar** com o conjunto resultante;
4. **repetir a requisição original** — **poucas vezes**; depois, tratar como falha
   permanente de autorização.

Clientes **DEVERIAM** limitar tentativas e rastrear tentativas de elevação, para não
repetir a mesma falha. Clientes agindo em nome de usuário **DEVERIAM** tentar o step-up;
clientes `client_credentials` **PODEM** tentar ou abortar imediatamente.

Servidores **DEVEM** considerar **hierarquia de escopos** — um escopo mais amplo que
implica um mais estreito — ao decidir se um token basta. A acumulação de escopos é
responsabilidade **do cliente**; a hierarquia, **do servidor**.

---

## 11. Refresh tokens

**Clientes que querem refresh token:**

- **DEVEM** mantê-lo confidencial em trânsito e em repouso;
- **DEVERIAM** incluir `refresh_token` em `grant_types` nos metadados do cliente;
- **PODEM** acrescentar `offline_access` ao `scope` quando o AS o listar em
  `scopes_supported`;
- **NÃO PODEM** supor que ele será emitido — a decisão é do AS.

**Servidores MCP** (resource servers) **NÃO DEVERIAM** incluir `offline_access` no escopo
do `WWW-Authenticate` nem em `scopes_supported`: refresh token não é requisito de recurso.
Sutil, e muita gente erra.

---

## 12. Códigos de erro

| Status | Quando |
|---|---|
| **401 Unauthorized** | falta autorização, ou token inválido/expirado |
| **403 Forbidden** | escopo insuficiente ou permissão insuficiente |
| **400 Bad Request** | requisição de autorização malformada |

---

## 13. Extensões de autorização

No repositório [`modelcontextprotocol/ext-auth`](https://github.com/modelcontextprotocol/ext-auth).
São **opcionais**, **aditivas**, **componíveis** e **versionadas independentemente**.

| Extensão | Para quê |
|---|---|
| **OAuth Client Credentials** | máquina-a-máquina, sem usuário presente |
| **Enterprise-Managed Authorization** | controle centralizado; usa ID-JAG (*Identity Assertion JWT Authorization Grant*) |

O roadmap de 22/08/2026 coloca **identidade de agente** como uma das cinco prioridades:
DPoP (prova de posse), *Workload Identity Federation* (SEP-1933), ID-JAG e troca de token
(RFC 8693), coordenados com os grupos OAuth e WIMSE do IETF. É o campo de batalha atual.

---

## 14. Um caminho pragmático

Opinião profissional, na ordem em que eu faria:

1. **Comece em stdio.** Credencial do ambiente. Zero OAuth. Resolve a maioria dos casos
   internos.
2. **Se precisar de remoto interno**, monte o servidor MCP **dentro da aplicação HTTP que
   você já tem**, com a autenticação que você já tem. Você continua devendo a validação de
   audiência — mas herda tudo o resto.
3. **Só se precisar de terceiros**, implemente a spec inteira, com um IdP de mercado como
   AS. **Não escreva um servidor de autorização.**
4. **Nunca** repasse o token do cliente para a API a jusante. Troque por um token da
   audiência correta.
5. **Registre e monitore** as falhas de validação de audiência: elas são o sinal precoce
   de que alguém está tentando reusar token.

---

## 15. Autoteste

1. Por que servidores stdio **não deveriam** seguir esta especificação?
2. Qual papel OAuth o servidor MCP exerce, e por que essa escolha simplifica a adoção?
3. Que RFC o servidor MCP **deve** implementar para apontar o seu AS? Como o cliente descobre a URL?
4. O que o parâmetro `resource` impede? Escreva uma URI canônica válida e uma inválida.
5. Descreva a validação de `iss` da RFC 9207. Por que a comparação não pode normalizar a URI?
6. Por que PKCE sozinho não previne mix-up?
7. Qual é a **única** coisa que um servidor MCP protegido não pode deixar de fazer com o token?
8. Por que o cliente deve pedir **todos** os `scopes_supported` quando não há `scope` no desafio?
9. O que é o fluxo de step-up, e por que o cliente calcula a **união** dos escopos?
10. Por que um servidor MCP não deveria listar `offline_access` em `scopes_supported`?

---

**Anterior:** [17 · Versionamento](17-versionamento-e-compatibilidade.md) · **Próximo:** [19 · Segurança](19-seguranca.md) · **Índice:** [00-MAPA](00-MAPA.md)

*Fontes: [Autorização](https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization),
[Descoberta do AS](https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization/authorization-server-discovery),
[Registro de cliente](https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization/client-registration),
[Boas práticas de segurança](https://modelcontextprotocol.io/docs/2026-07-28/tutorials/security/security_best_practices),
[Roadmap 22/08/2026](https://modelcontextprotocol.io/development/roadmap),
RFCs [6750](https://datatracker.ietf.org/doc/html/rfc6750),
[8414](https://datatracker.ietf.org/doc/html/rfc8414),
[8707](https://www.rfc-editor.org/rfc/rfc8707.html),
[9207](https://datatracker.ietf.org/doc/html/rfc9207),
[9728](https://datatracker.ietf.org/doc/html/rfc9728). Consultas em 01/09/2026.*
