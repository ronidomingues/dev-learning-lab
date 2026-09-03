# 95 · Referências — specs, código, pessoas

`Nível: todos` · **Verificado em 01/09/2026**

---

## 1. A especificação

| Recurso | Link |
|---|---|
| **Especificação vigente (`2026-07-28`)** | <https://modelcontextprotocol.io/specification/2026-07-28> |
| Changelog da revisão | <https://modelcontextprotocol.io/specification/2026-07-28/changelog> |
| **Registro de recursos depreciados** | <https://modelcontextprotocol.io/specification/2026-07-28/deprecated> |
| Arquitetura | <https://modelcontextprotocol.io/specification/2026-07-28/architecture> |
| Base do protocolo (JSON-RPC, `_meta`, erros) | <https://modelcontextprotocol.io/specification/2026-07-28/basic> |
| Versionamento e compatibilidade | <https://modelcontextprotocol.io/specification/2026-07-28/basic/versioning> |
| Padrões de mensagem | <https://modelcontextprotocol.io/specification/2026-07-28/basic/patterns> |
| MRTR | <https://modelcontextprotocol.io/specification/2026-07-28/basic/patterns/mrtr> |
| Assinaturas | <https://modelcontextprotocol.io/specification/2026-07-28/basic/patterns/subscriptions> |
| Transportes | <https://modelcontextprotocol.io/specification/2026-07-28/basic/transports> |
| — stdio | <https://modelcontextprotocol.io/specification/2026-07-28/basic/transports/stdio> |
| — Streamable HTTP | <https://modelcontextprotocol.io/specification/2026-07-28/basic/transports/streamable-http> |
| Autorização | <https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization> |
| Tools | <https://modelcontextprotocol.io/specification/2026-07-28/server/tools> |
| Resources | <https://modelcontextprotocol.io/specification/2026-07-28/server/resources> |
| Prompts | <https://modelcontextprotocol.io/specification/2026-07-28/server/prompts> |
| Elicitação | <https://modelcontextprotocol.io/specification/2026-07-28/client/elicitation> |
| **Referência do schema** | <https://modelcontextprotocol.io/specification/2026-07-28/schema> |

### Revisões anteriores

| Revisão | Link | Changelog |
|---|---|---|
| `2025-11-25` | [spec](https://modelcontextprotocol.io/specification/2025-11-25) | [mudanças](https://modelcontextprotocol.io/specification/2025-11-25/changelog) |
| `2025-06-18` | [spec](https://modelcontextprotocol.io/specification/2025-06-18) | [mudanças](https://modelcontextprotocol.io/specification/2025-06-18/changelog) |
| `2025-03-26` | [spec](https://modelcontextprotocol.io/specification/2025-03-26) | [mudanças](https://modelcontextprotocol.io/specification/2025-03-26/changelog) |
| `2024-11-05` | [spec](https://modelcontextprotocol.io/specification/2024-11-05) | — |

### O schema, como fonte da verdade

| Formato | Link |
|---|---|
| **TypeScript** (fonte da verdade) | <https://github.com/modelcontextprotocol/modelcontextprotocol/blob/main/schema/2026-07-28/schema.ts> |
| JSON Schema (gerado) | <https://github.com/modelcontextprotocol/modelcontextprotocol/blob/main/schema/2026-07-28/schema.json> |

> Quando a prosa da spec e o schema divergirem, **o schema TypeScript é a fonte da
> verdade** — a spec diz isso explicitamente. O JSON Schema é gerado a partir dele.

---

## 2. Documentação e guias

| Recurso | Link |
|---|---|
| O que é MCP | <https://modelcontextprotocol.io/docs/2026-07-28/getting-started/intro> |
| Arquitetura (guia) | <https://modelcontextprotocol.io/docs/2026-07-28/learn/architecture> |
| Conceitos de servidor | <https://modelcontextprotocol.io/docs/2026-07-28/learn/server-concepts> |
| Conceitos de cliente | <https://modelcontextprotocol.io/docs/2026-07-28/learn/client-concepts> |
| Versionamento (guia) | <https://modelcontextprotocol.io/docs/2026-07-28/learn/versioning> |
| **Construir um servidor** | <https://modelcontextprotocol.io/docs/2026-07-28/develop/build-server> |
| **Construir um cliente** | <https://modelcontextprotocol.io/docs/2026-07-28/develop/build-client> |
| Boas práticas de cliente | <https://modelcontextprotocol.io/docs/2026-07-28/develop/clients/client-best-practices> |
| Conectar servidores locais | <https://modelcontextprotocol.io/docs/2026-07-28/develop/connect-local-servers> |
| Conectar servidores remotos | <https://modelcontextprotocol.io/docs/2026-07-28/develop/connect-remote-servers> |
| **Boas práticas de segurança** | <https://modelcontextprotocol.io/docs/2026-07-28/tutorials/security/security_best_practices> |
| Autorização (tutorial) | <https://modelcontextprotocol.io/docs/2026-07-28/tutorials/security/authorization> |
| Depuração | <https://modelcontextprotocol.io/docs/2026-07-28/tools/debugging> |
| **Índice para máquinas** (`llms.txt`) | <https://modelcontextprotocol.io/llms.txt> |

---

## 3. Ferramentas

### MCP Inspector

| Recurso | Link |
|---|---|
| Visão geral | <https://modelcontextprotocol.io/docs/2026-07-28/tools/inspector> |
| Cliente web | <https://modelcontextprotocol.io/docs/2026-07-28/tools/inspector/web> |
| **Cliente CLI** | <https://modelcontextprotocol.io/docs/2026-07-28/tools/inspector/cli> |
| Cliente TUI | <https://modelcontextprotocol.io/docs/2026-07-28/tools/inspector/tui> |
| Configuração e flags | <https://modelcontextprotocol.io/docs/2026-07-28/tools/inspector/configuration> |
| Autorização | <https://modelcontextprotocol.io/docs/2026-07-28/tools/inspector/authorization> |
| Eras de protocolo | <https://modelcontextprotocol.io/docs/2026-07-28/tools/inspector/protocol-eras> |
| Receitas | <https://modelcontextprotocol.io/docs/2026-07-28/tools/inspector/recipes> |

```bash
npx -y @modelcontextprotocol/inspector            # web
npx -y @modelcontextprotocol/inspector --tui      # terminal
npx -y @modelcontextprotocol/inspector --cli ...  # script e CI
```

---

## 4. SDKs

| Linguagem | Tier | Documentação | Repositório |
|---|---|---|---|
| **TypeScript** | 1 | [ts.sdk](https://ts.sdk.modelcontextprotocol.io) | [typescript-sdk](https://github.com/modelcontextprotocol/typescript-sdk) |
| **Python** | 1 | [py.sdk](https://py.sdk.modelcontextprotocol.io) | [python-sdk](https://github.com/modelcontextprotocol/python-sdk) |
| **C#** | 1 | [csharp.sdk](https://csharp.sdk.modelcontextprotocol.io) | [csharp-sdk](https://github.com/modelcontextprotocol/csharp-sdk) |
| **Go** | 1 | [go.sdk](https://go.sdk.modelcontextprotocol.io) | [go-sdk](https://github.com/modelcontextprotocol/go-sdk) |
| **Rust** | 1 | [rust.sdk](https://rust.sdk.modelcontextprotocol.io) | [rust-sdk](https://github.com/modelcontextprotocol/rust-sdk) |
| **Java** | 2 | [java.sdk](https://java.sdk.modelcontextprotocol.io) | [java-sdk](https://github.com/modelcontextprotocol/java-sdk) |
| **Ruby** | 2 | [ruby.sdk](https://ruby.sdk.modelcontextprotocol.io) | [ruby-sdk](https://github.com/modelcontextprotocol/ruby-sdk) |
| **Swift** | 3 | — | [swift-sdk](https://github.com/modelcontextprotocol/swift-sdk) |
| **PHP** | 3 | [php.sdk](https://php.sdk.modelcontextprotocol.io) | [php-sdk](https://github.com/modelcontextprotocol/php-sdk) |
| **Kotlin** | 3 | [kotlin.sdk](https://kotlin.sdk.modelcontextprotocol.io) | [kotlin-sdk](https://github.com/modelcontextprotocol/kotlin-sdk) |

O que cada tier significa: <https://modelcontextprotocol.io/community/sdk-tiers>

### Pacotes e versões observadas em 01/09/2026

| Pacote | Versão | Licença |
|---|---|---|
| `mcp` (PyPI) | **2.1.1** (`Requires-Python: >=3.10`) | MIT |
| `@modelcontextprotocol/server` (npm) | **2.0.0** (`node >=20`) | MIT |
| `@modelcontextprotocol/client` (npm) | **2.0.0** | MIT |
| `@modelcontextprotocol/sdk` (npm, ramo v1) | **1.30.0** | MIT |
| `@modelcontextprotocol/inspector` (npm) | **2.4.0** (`node >=22.19.0`) | MIT |

Guia de migração do SDK Python v1 → v2:
<https://py.sdk.modelcontextprotocol.io/v2/migration/>

---

## 5. Extensões

| Extensão | Documentação | Repositório |
|---|---|---|
| Visão geral | [extensions/overview](https://modelcontextprotocol.io/extensions/overview) | — |
| **Matriz de suporte por cliente** | [client-matrix](https://modelcontextprotocol.io/extensions/client-matrix) | — |
| **MCP Apps** | [apps/overview](https://modelcontextprotocol.io/extensions/apps/overview) · [API](https://apps.extensions.modelcontextprotocol.io) | [ext-apps](https://github.com/modelcontextprotocol/ext-apps) |
| **Tasks** | [tasks/overview](https://modelcontextprotocol.io/extensions/tasks/overview) | [ext-tasks](https://github.com/modelcontextprotocol/ext-tasks) |
| Autorização | [auth/overview](https://modelcontextprotocol.io/extensions/auth/overview) | [ext-auth](https://github.com/modelcontextprotocol/ext-auth) |
| — OAuth Client Credentials | [oauth-client-credentials](https://modelcontextprotocol.io/extensions/auth/oauth-client-credentials) | — |
| — Enterprise-Managed Authorization | [enterprise-managed-authorization](https://modelcontextprotocol.io/extensions/auth/enterprise-managed-authorization) | — |

---

## 6. Registry

| Recurso | Link |
|---|---|
| Sobre | <https://modelcontextprotocol.io/registry/about> |
| **Quickstart de publicação** | <https://modelcontextprotocol.io/registry/quickstart> |
| Autenticação (GitHub, DNS, HTTP) | <https://modelcontextprotocol.io/registry/authentication> |
| Tipos de pacote suportados | <https://modelcontextprotocol.io/registry/package-types> |
| Servidores remotos | <https://modelcontextprotocol.io/registry/remote-servers> |
| Versionamento | <https://modelcontextprotocol.io/registry/versioning> |
| Automação com GitHub Actions | <https://modelcontextprotocol.io/registry/github-actions> |
| Política de moderação | <https://modelcontextprotocol.io/registry/moderation-policy> |
| Agregadores | <https://modelcontextprotocol.io/registry/registry-aggregators> |
| Código e OpenAPI | <https://github.com/modelcontextprotocol/registry> |
| API pública | `https://registry.modelcontextprotocol.io/v0.1/servers?search=...` |

---

## 7. Governança e comunidade

| Recurso | Link |
|---|---|
| Governança e curadoria | <https://modelcontextprotocol.io/community/governance> |
| **Princípios de projeto** | <https://modelcontextprotocol.io/community/design-principles> |
| **Ciclo de vida e depreciação** | <https://modelcontextprotocol.io/community/feature-lifecycle> |
| Tiers de SDK | <https://modelcontextprotocol.io/community/sdk-tiers> |
| Diretrizes de SEP | <https://modelcontextprotocol.io/community/sep-guidelines> |
| **Índice de SEPs** | <https://modelcontextprotocol.io/seps/index> |
| Grupos de trabalho e de interesse | <https://modelcontextprotocol.io/community/working-interest-groups> |
| Como contribuir | <https://modelcontextprotocol.io/community/contributing> |
| Escada de contribuidor | <https://modelcontextprotocol.io/community/contributor-ladder> |
| Política de segurança | <https://modelcontextprotocol.io/community/security> |
| Comunicação (Discord) | <https://modelcontextprotocol.io/community/communication> |
| **Roadmap** | <https://modelcontextprotocol.io/development/roadmap> |
| **Blog oficial** | <https://blog.modelcontextprotocol.io/> |

### SEPs citados neste curso

| SEP | Assunto |
|---|---|
| [2575](https://modelcontextprotocol.io/seps/2575-stateless-mcp) | **MCP sem estado** — remove sessões e `initialize` |
| [2322](https://modelcontextprotocol.io/seps/2322-MRTR) | **MRTR** — requisições de múltiplas idas e vindas |
| [2663](https://modelcontextprotocol.io/seps/2663-tasks-extension) | Tasks como extensão |
| [2549](https://modelcontextprotocol.io/seps/2549-TTL-for-list-results) | `ttlMs` e `cacheScope` |
| [2133](https://modelcontextprotocol.io/seps/2133-extensions) | Framework de extensões |
| [2596](https://github.com/modelcontextprotocol/modelcontextprotocol/pull/2596) | Política de ciclo de vida e depreciação |
| [2577](https://github.com/modelcontextprotocol/modelcontextprotocol/pull/2577) | Depreciação de Roots, Sampling e Logging |
| [986](https://github.com/modelcontextprotocol/modelcontextprotocol/pull/1603) | Orientação sobre nomes de ferramenta |
| [1303](https://github.com/modelcontextprotocol/modelcontextprotocol/issues/1303) | Erro de validação como erro de execução |
| [2243](https://github.com/modelcontextprotocol/modelcontextprotocol/pull/2243) | Cabeçalhos padrão e `x-mcp-header` |
| [2468](https://github.com/modelcontextprotocol/modelcontextprotocol/pull/2468) | Validação de `iss` (RFC 9207) |
| [991](https://github.com/modelcontextprotocol/modelcontextprotocol/issues/991) | Client ID Metadata Documents |

---

## 7.1 Pessoas

| Quem | Papel |
|---|---|
| **David Soria Parra** | coautor do MCP; Core Maintainer (SDK) |
| **Justin Spahr-Summers** | coautor do MCP |
| **Caitie McCaffrey**, **Clare Liguori**, **Peter Alexander** | Core Maintainers — primitivas de mensagem para agentes |
| **Kurtis Van Gent**, **Nick Cooper** | Core Maintainers — transporte HTTP |
| **Paul Carleton**, **Den Delimarsky** | Core Maintainers — identidade de agente e segurança |

**Working Groups:** Agents · File Uploads · Inspector V2 · Interceptors · Registry · SDK ·
Server Card · Skills Over MCP · Transports · Triggers and Events

**Interest Groups:** Authorization · Enterprise · Enterprise-Managed Authorization ·
Financial Services · Primitive Grouping · Security · Tool Annotations

---

## 8. Código de referência

| Recurso | Link |
|---|---|
| **Servidores de referência** | <https://github.com/modelcontextprotocol/servers> |
| Exemplos | <https://modelcontextprotocol.io/examples> |
| Recursos de quickstart | <https://github.com/modelcontextprotocol/quickstart-resources> |
| Exemplos de MCP Apps | <https://github.com/modelcontextprotocol/ext-apps/tree/main/examples> |
| Organização no GitHub | <https://github.com/modelcontextprotocol> |

---

## 9. Padrões externos de que o MCP depende

| Padrão | Link | Onde entra |
|---|---|---|
| **JSON-RPC 2.0** | <https://www.jsonrpc.org/specification> | toda mensagem |
| **JSON Schema 2020-12** | <https://json-schema.org/draft/2020-12/schema> | dialeto padrão dos schemas |
| **RFC 3986** — URI | <https://datatracker.ietf.org/doc/html/rfc3986> | URIs de recurso; comparação de `iss` |
| **RFC 6570** — URI Template | <https://datatracker.ietf.org/doc/html/rfc6570> | templates de recurso |
| **RFC 6750** — Bearer Token | <https://datatracker.ietf.org/doc/html/rfc6750> | `Authorization`, `WWW-Authenticate` |
| **RFC 7591** — DCR ⚠️ depreciado | <https://datatracker.ietf.org/doc/html/rfc7591> | registro dinâmico de cliente |
| **RFC 8414** — AS Metadata | <https://datatracker.ietf.org/doc/html/rfc8414> | descoberta do servidor de autorização |
| **RFC 8707** — Resource Indicators | <https://www.rfc-editor.org/rfc/rfc8707.html> | parâmetro `resource`; audiência |
| **RFC 9110** — HTTP Semantics | <https://datatracker.ietf.org/doc/html/rfc9110> | cabeçalhos `Mcp-*`, codificação de valores |
| **RFC 9207** — AS Issuer Identification | <https://datatracker.ietf.org/doc/html/rfc9207> | validação de `iss`; mix-up |
| **RFC 9700** — OAuth Security BCP | <https://datatracker.ietf.org/doc/html/rfc9700> | boas práticas |
| **RFC 9728** — Protected Resource Metadata | <https://datatracker.ietf.org/doc/html/rfc9728> | descoberta do AS pelo servidor MCP |
| **OAuth 2.1** (draft-13) | <https://datatracker.ietf.org/doc/html/draft-ietf-oauth-v2-1-13> | a base da autorização |
| **Client ID Metadata Documents** (draft-00) | <https://datatracker.ietf.org/doc/html/draft-ietf-oauth-client-id-metadata-document-00> | registro recomendado |
| **OpenID Connect Discovery 1.0** | <https://openid.net/specs/openid-connect-discovery-1_0.html> | descoberta alternativa |
| **W3C Trace Context** | <https://www.w3.org/TR/trace-context/> | `traceparent`, `tracestate` |
| **W3C Baggage** | <https://www.w3.org/TR/baggage/> | `baggage` |
| **OTel · convenções para MCP** | <https://opentelemetry.io/docs/specs/semconv/gen-ai/mcp/> | telemetria |
| **Server-Sent Events** | <https://html.spec.whatwg.org/multipage/server-sent-events.html> | fluxos de resposta |

---

## 10. Segurança — leituras externas

| Recurso | Link |
|---|---|
| **NSA/AISC · CSI sobre segurança do MCP** (20/05/2026) | [nsa.gov](https://www.nsa.gov/Press-Room/Press-Releases-Statements/Press-Release-View/Article/4496698/nsa-releases-security-design-considerations-for-ai-driven-automation-leveraging/) |
| OWASP · SSRF Prevention Cheat Sheet | [cheatsheetseries.owasp.org](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html) |
| OWASP Top 10 · A10:2021 SSRF | [owasp.org](https://owasp.org/Top10/2021/A10_2021-Server-Side_Request_Forgery_%28SSRF%29/) |
| Smokescreen (proxy de saída anti-SSRF) | [github.com/stripe/smokescreen](https://github.com/stripe/smokescreen) |
| Simon Willison sobre injeção de prompt | [simonwillison.net](https://simonwillison.net/tags/prompt-injection/) |

---

## 11. Fundação e histórico

| Recurso | Link |
|---|---|
| **Anthropic · doação do MCP à AAIF** (09/12/2025) | [anthropic.com](https://www.anthropic.com/news/donating-the-model-context-protocol-and-establishing-of-the-agentic-ai-foundation) |
| **Linux Foundation · formação da AAIF** | [linuxfoundation.org](https://www.linuxfoundation.org/press/linux-foundation-announces-the-formation-of-the-agentic-ai-foundation) |
| Blog · a especificação `2026-07-28` (28/07/2026) | [blog.mcp](https://blog.modelcontextprotocol.io/posts/2026-07-28/) |
| Blog · um ano de MCP (25/11/2025) | [blog.mcp](https://blog.modelcontextprotocol.io/posts/2025-11-25-first-mcp-anniversary/) |
| Wikipédia · Model Context Protocol | [en.wikipedia.org](https://en.wikipedia.org/wiki/Model_Context_Protocol) |

---

## 12. Neste repositório

| Assunto relacionado | Onde |
|---|---|
| Agentes de IA | [agentes-de-ia](../agentes-de-ia/00-MAPA.md) |
| Engenharia de prompt | [engenharia-de-prompt](../engenharia-de-prompt/00-MAPA.md) |
| APIs | [apis](../apis/00-MAPA.md) |
| JWT | [jwt](../jwt/00-MAPA.md) |
| TLS | [tls](../tls/00-MAPA.md) |
| Docker | [curso-docker](../curso-docker/) |
| uv e Python | [uv-python](../uv-python/00-MAPA.md) |
| n8n (MCP em low-code) | [n8n](../n8n/00-MAPA.md) |
| Variáveis de ambiente e segredos | [variaveis-de-ambiente-e-segredos](../variaveis-de-ambiente-e-segredos/00-MAPA.md) |
| Portas de rede | [portas-de-rede](../portas-de-rede/00-MAPA.md) |
| PostgreSQL | [postgresql](../postgresql/00-MAPA.md) |
| Testes automatizados | [testes-automatizados](../testes-automatizados/00-MAPA.md) |

---

**Anterior:** [90 · Bibliografia](90-bibliografia.md) · **Próximo:** [GLOSSARIO](GLOSSARIO.md) · **Índice:** [00-MAPA](00-MAPA.md)

*Todos os links verificados em 01/09/2026. Versões de pacote lidas de PyPI e npm nesta
máquina na mesma data.*
