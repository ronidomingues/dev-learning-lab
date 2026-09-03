# 95 · Referências

`Nível: todos` · `Verificado em 11/08/2026`

Fontes primárias, ferramentas e pessoas. Tudo verificado na data acima.

---

## 1. Especificações — a fonte da verdade

### HTTP (RFCs de junho de 2022 — a reorganização)

| RFC | Título | Leia se |
|---|---|---|
| **9110** ⭐ | **HTTP Semantics** | **é o único que você vai ler**. Métodos (§9), status (§15), cabeçalhos |
| **9111** ⭐ | HTTP Caching | quer usar cache direito |
| 9112 | HTTP/1.1 | precisa do detalhe do formato |
| 9113 | HTTP/2 | idem |
| 9114 | HTTP/3 | idem |
| 9204 | QPACK | compressão de cabeçalho em HTTP/3 |
| 9000 | QUIC | o transporte por baixo do HTTP/3 |

https://www.rfc-editor.org/rfc/rfc9110.html

### Outros RFCs que aparecem no dia a dia

| RFC | Assunto |
|---|---|
| **9457** ⭐ | **Problem Details for HTTP APIs** (substitui o 7807) |
| **9562** | UUID, incluindo **UUIDv7** (substitui o 4122) |
| 8288 | *Web Linking* — o cabeçalho `Link`, usado em paginação |
| 8259 | JSON |
| 7386 | JSON Merge Patch |
| 6902 | JSON Patch |
| 6749 | OAuth 2.0 |
| 6750 | OAuth 2.0 Bearer Token |
| 7636 | **PKCE** |
| 7519 | JWT |
| 8725 | **JWT Best Current Practices** |
| 7807 | Problem Details (**obsoleto** — use o 9457) |
| 8594 | cabeçalho `Sunset` |
| 9745 | cabeçalho `Deprecation` |
| 6648 | desaconselha o prefixo `X-` |
| 5789 | método PATCH |
| 7234 | cache (**obsoleto** — use o 9111) |

**Rascunhos relevantes (IETF HTTP APIs WG):**
`Idempotency-Key` header · `RateLimit` headers · *Protocol Maintenance* (a crítica ao
Princípio da Robustez) — https://datatracker.ietf.org/wg/httpapi/documents/

### Outras especificações

| Spec | URL |
|---|---|
| **OpenAPI** | https://spec.openapis.org · https://www.openapis.org |
| **JSON Schema** | https://json-schema.org |
| **AsyncAPI** | https://www.asyncapi.com |
| **GraphQL** | https://spec.graphql.org |
| **gRPC / Protobuf** | https://grpc.io/docs/ · https://protobuf.dev |
| **Model Context Protocol** | https://modelcontextprotocol.io |
| **Fetch / CORS** (WHATWG) | https://fetch.spec.whatwg.org |
| **W3C Trace Context** | https://www.w3.org/TR/trace-context/ |
| **Server-Sent Events** (HTML Living Standard) | https://html.spec.whatwg.org/multipage/server-sent-events.html |
| **WebSocket** | RFC 6455 |
| **Standard Webhooks** | https://www.standardwebhooks.com |

---

## 2. Guias de design — leitura obrigatória

| Guia | URL | Por que |
|---|---|---|
| **Fielding, tese cap. 5** ⭐ | https://ics.uci.edu/~fielding/pubs/dissertation/rest_arch_style.htm | a definição de REST |
| Fielding — *REST APIs must be hypertext-driven* | https://roy.gbiv.com/untangled/2008/rest-apis-must-be-hypertext-driven | o protesto de 2008 |
| **Zalando RESTful API Guidelines** ⭐ | https://opensource.zalando.com/restful-api-guidelines/ | guia real de empresa grande, público e detalhado |
| **Google API Design Guide** ⭐ | https://cloud.google.com/apis/design | opinativo e fundamentado |
| **Microsoft REST API Guidelines** | https://github.com/microsoft/api-guidelines | outra referência corporativa |
| Fowler — *Richardson Maturity Model* | https://martinfowler.com/articles/richardsonMaturityModel.html | os quatro níveis |
| **OWASP API Security Top 10** ⭐ | https://owasp.org/API-Security/ | os riscos reais |
| OWASP Cheat Sheets (REST, JWT, Mass Assignment) | https://cheatsheetseries.owasp.org/ | defesas concretas |
| Diátaxis | https://diataxis.fr | como estruturar documentação |
| Hyrum's Law | https://www.hyrumslaw.com/ | por que o contrato efetivo não é o declarado |

⭐ = as cinco que eu manteria abertas.

---

## 3. Documentação de referência

| Recurso | URL |
|---|---|
| **MDN — HTTP (pt-BR)** ⭐ | https://developer.mozilla.org/pt-BR/docs/Web/HTTP |
| MDN — Status codes | https://developer.mozilla.org/pt-BR/docs/Web/HTTP/Status |
| MDN — Headers | https://developer.mozilla.org/pt-BR/docs/Web/HTTP/Headers |
| MDN — CORS | https://developer.mozilla.org/pt-BR/docs/Web/HTTP/CORS |
| **curl — manual** | https://curl.se/docs/manpage.html |
| **curl — *Everything curl*** (livro gratuito) | https://everything.curl.dev |
| **jq — manual** | https://jqlang.github.io/jq/manual/ |
| **JSON, em português** | https://www.json.org/json-pt.html |
| **HTTP Archive Web Almanac** | https://almanac.httparchive.org |
| **Cloudflare Radar** | https://radar.cloudflare.com |

---

## 4. Ferramentas

### Cliente e exploração
| Ferramenta | URL | Nota |
|---|---|---|
| **curl** | https://curl.se | a língua franca |
| **HTTPie** | https://httpie.io | sintaxe amigável |
| **Bruno** | https://www.usebruno.com | **coleções em arquivo, versionáveis** |
| **Hoppscotch** | https://hoppscotch.io | no navegador, open source |
| **Postman** | https://www.postman.com | o mais popular |
| **Insomnia** | https://insomnia.rest | alternativa aberta |
| **REST Client (VS Code)** | https://marketplace.visualstudio.com/items?itemName=humao.rest-client | arquivos `.http` |
| **grpcurl** | https://github.com/fullstorydev/grpcurl | o curl do gRPC |
| **websocat** | https://github.com/vi/websocat | o curl do WebSocket |
| **jq** | https://jqlang.github.io/jq/ | processar JSON |

### Contrato
| Ferramenta | URL | Faz |
|---|---|---|
| **Spectral** | https://docs.stoplight.io/docs/spectral | lint de OpenAPI com regras próprias |
| **Redocly CLI** | https://redocly.com/docs/cli/ | valida, junta, gera docs |
| **oasdiff** ⭐ | https://github.com/Tufin/oasdiff | **detecta mudança quebradora** |
| **Prism** | https://github.com/stoplightio/prism | mock a partir do contrato |
| **openapi-generator** | https://openapi-generator.tech | clientes e servidores |
| **openapi-typescript** | https://github.com/openapi-ts/openapi-typescript | tipos TS |
| **Schemathesis** | https://schemathesis.readthedocs.io | testes gerados do contrato |
| **Swagger Editor** | https://editor.swagger.io | edição no navegador |
| **Scalar** | https://scalar.com | documentação moderna |
| **Ajv** | https://ajv.js.org | validação JSON Schema (JS) |

### Gateway e infraestrutura
| Ferramenta | URL | Licença |
|---|---|---|
| **Kong** | https://konghq.com | Apache 2.0 (OSS) |
| **Apache APISIX** | https://apisix.apache.org | Apache 2.0 |
| **Tyk** | https://tyk.io | MPL (OSS) |
| **Traefik** | https://traefik.io | MIT |
| **Envoy** | https://www.envoyproxy.io | Apache 2.0 |
| **Caddy** | https://caddyserver.com | Apache 2.0 |
| **nginx** | https://nginx.org | BSD |

### Observabilidade e teste de carga
| Ferramenta | URL |
|---|---|
| **OpenTelemetry** | https://opentelemetry.io |
| **Prometheus** | https://prometheus.io |
| **Grafana** | https://grafana.com |
| **Jaeger** | https://www.jaegertracing.io |
| **k6** | https://k6.io |
| **oha** | https://github.com/hatoo/oha |
| **autocannon** | https://github.com/mcollina/autocannon |

### Segurança
| Ferramenta | URL |
|---|---|
| **OWASP ZAP** | https://www.zaproxy.org |
| **Burp Suite** (Community é gratuita) | https://portswigger.net/burp |
| **gitleaks** | https://github.com/gitleaks/gitleaks |
| **trufflehog** | https://github.com/trufflesecurity/trufflehog |
| **42Crunch** | https://42crunch.com |

---

## 5. APIs públicas para praticar

| API | URL | Nota |
|---|---|---|
| **httpbin** | https://httpbin.org | ecoa o que você mandar; ideal para aprender |
| **GitHub API** | https://docs.github.com/rest | bem projetada; ótimo objeto de estudo |
| **ViaCEP** | https://viacep.com.br | CEP brasileiro, gratuito, sem cadastro |
| **BrasilAPI** | https://brasilapi.com.br | CEP, CNPJ, bancos, feriados, DDD |
| **IBGE** | https://servicodados.ibge.gov.br/api/docs | localidades, dados |
| **Banco Central** | https://dadosabertos.bcb.gov.br | câmbio, SELIC |
| **Portal da Transparência** | https://api.portaldatransparencia.gov.br | dados públicos |
| **JSONPlaceholder** | https://jsonplaceholder.typicode.com | API falsa para teste |
| **Public APIs (lista)** | https://github.com/public-apis/public-apis | catálogo enorme |
| **PokéAPI** | https://pokeapi.co | bem documentada, sem cadastro |

> **Comece pelo `httpbin`** para aprender mecânica, e pela **API do GitHub** para estudar
> design real: ela tem paginação por `Link`, `ETag`, rate limit com cabeçalhos, versionamento
> por cabeçalho e erros bem estruturados. É um ótimo objeto de engenharia reversa (Lab 1).

---

## 6. Pessoas e comunidades

Não é lista de influenciadores — são pessoas cujo trabalho técnico é verificável.

| Pessoa | Contribuição |
|---|---|
| **Roy Fielding** | REST; coautor do HTTP |
| **Mark Nottingham** | RFC 9110/9111, RFC 9457; IETF HTTP WG |
| **Martin Kleppmann** | *Designing Data-Intensive Applications*; pesquisa em sistemas distribuídos |
| **Martin Fowler** | Richardson Maturity Model, refatoração, arquitetura |
| **Phil Sturgeon** | *Build APIs You Won't Hate*; APIs You Won't Hate |
| **Mike Amundsen** | hipermídia; *RESTful Web APIs* |
| **Leonard Richardson** | modelo de maturidade; *RESTful Web APIs* |
| **JJ Geewax** | *API Design Patterns* |
| **Erik Wilde** | RFC 9457; padrões de web API |
| **Chris Richardson** | padrões de microsserviços (saga, outbox) |
| **Michael Nygard** | *Release It!*; padrões de estabilidade |
| **Neil Madden** | *API Security in Action* |

**Comunidades:**
- **APIs You Won't Hate** — https://apisyouwonthate.com
- **IETF HTTP Working Group** — https://httpwg.org (leitura pública)
- **OpenAPI Initiative** — https://www.openapis.org (Slack e GitHub abertos)
- **OWASP** — https://owasp.org (capítulos locais, inclusive no Brasil)
- **Stack Overflow** — perguntas pontuais

---

## 7. Fontes usadas na produção deste material

Todas consultadas em **11/08/2026**.

**Especificações e padrões**
- IETF — RFC 9110, 9111, 9112, 9113, 9114, 9457, 9562, 8288, 6749, 6750, 7636, 7519 — https://www.rfc-editor.org/
- OpenAPI Initiative — https://www.openapis.org · SIG Moonwalk — https://github.com/OAI/sig-moonwalk
- Fielding, R. T. — tese (2000) e o post de 2008 (links na §2)
- OWASP — API Security Top 10 (2023) — https://owasp.org/API-Security/

**Estado da arte (ago/2026)**
- APIScout — *OpenAPI 3.2: What's New & Migration Guide 2026* — https://apiscout.dev/guides/openapi-4-whats-new-migration-guide-2026
- OpenAPI Initiative — *Moonwalk 2025 update* — https://www.openapis.org/blog/2025/02/05/moonwalk-2025-update
- Cloudflare — *Radar Year in Review* — https://blog.cloudflare.com/radar-2025-year-in-review/
- Medições independentes de adoção de HTTP/3 (W3Techs, TechnologyChecker, Cloudflare Radar)
- Model Context Protocol — *The 2026-07-28 Specification* — https://blog.modelcontextprotocol.io/posts/2026-07-28/
- Model Context Protocol — *The 2026 MCP Roadmap* — https://blog.modelcontextprotocol.io/posts/2026-mcp-roadmap/

**Ferramentas e versões**
- Node.js Release Working Group — https://github.com/nodejs/Release
- NodeSource — *Node.js 24 Becomes LTS* — https://nodesource.com/blog/nodejs-24-becomes-lts
- npm — `fastify` (5.11.3 verificado em execução local)
- curl — https://curl.se/docs/ · jq — https://jqlang.github.io/jq/manual/

**Custos**
- Zuplo — *API Gateway Pricing Compared (2026)* — https://zuplo.com/learning-center/api-gateway-pricing-comparison-2026
- CloudZero — *AWS API Gateway Pricing (2026)* — https://www.cloudzero.com/blog/aws-api-gateway-pricing/
- DigitalAPI — *API Management Cost (2026)* — https://www.digitalapi.ai/blogs/api-management-cost
- Investing.com — USD/BRL — https://br.investing.com/currencies/usd-brl

**Cursos**
- OpenClassrooms — https://openclassrooms.com/fr/courses/6573181-adoptez-les-api-rest-pour-vos-projets-web
- MOOC Francophone — https://mooc-francophone.com
- Jornada do Dev — https://jornadadodev.com.br/cursos/back-end/rest-api
- Class Central — https://www.classcentral.com/subject/rest-apis

**Papers**
- Parnas (1972) · Waldo et al. (1994) · FLP (1985) · Gilbert & Lynch (2002) · Abadi (2012)
  · Liskov & Wing (1994) — referências completas em [60-teoria-avancada.md](60-teoria-avancada.md)

---

## 8. Como verificar uma informação sobre APIs

Hierarquia de confiança, do mais para o menos confiável:

1. **O RFC / a especificação.** É normativa. Se o RFC diz, é isso.
2. **MDN.** Precisa, atualizada, com exemplos, e em português.
3. **A resposta real da API**, observada com `curl -v`. O comportamento vence a documentação.
4. **A documentação oficial da ferramenta.**
5. **Guias corporativos** (Zalando, Google, Microsoft) — opinativos, mas fundamentados.
6. **Stack Overflow** com resposta aceita e votada — **verifique a data**.
7. **Blogs e conteúdo gerado por IA** — trate como hipótese a verificar.

> **A regra que eu aplico:** se a informação envolve **número** (limite, preço, versão) ou
> **comportamento normativo** ("o servidor deve..."), vá às fontes 1, 2 ou 3. Não confie em
> memória — nem na minha, nem na sua.

---

## Autoteste

1. Qual RFC você leria se pudesse ler só um, e quais seções?
2. Qual RFC substituiu o 7807? E o 4122?
3. Cite três guias corporativos de design de API abertos ao público.
4. Qual ferramenta detecta mudança quebradora entre versões de contrato?
5. Qual API pública você usaria para aprender mecânica de HTTP, e qual para estudar bom design?
6. Qual é a hierarquia de confiança para verificar uma informação técnica?
7. Por que o comportamento observado vence a documentação?
