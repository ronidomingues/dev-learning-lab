# Glossário

`Atualizado: 11/08/2026`

Todo termo técnico usado neste material. Termos usados em inglês pelo mercado brasileiro
aparecem em inglês, com a tradução na definição.

---

## A

**AsyncAPI** — Especificação para descrever APIs orientadas a evento (filas, tópicos,
webhooks). O análogo do OpenAPI para mensageria. Versão 3.0, dez/2023.

**At-least-once** — Garantia de entrega: nunca perde, pode duplicar. Combinada com
idempotência, produz o **efeito** exactly-once.

**At-most-once** — Garantia de entrega: nunca duplica, pode perder.

**Autenticação** (AuthN) — *Quem é você?* Ver [16](16-seguranca.md) §1.

**Autorização** (AuthZ) — *Você pode fazer isso?* Falha aqui é `403`, não `401`.

**API** — *Application Programming Interface*. Contrato pelo qual um software oferece
operações a outro software.

**API Gateway** — Intermediário à frente das APIs, que assume TLS, autenticação, rate limit,
roteamento e observabilidade.

## B

**Backoff exponencial** — Esperar cada vez mais entre retentativas (200 ms, 400, 800…).
Sem **jitter**, causa *thundering herd*.

**Bearer token** — Token portador: quem o tem, pode. Enviado em
`Authorization: Bearer <token>`.

**BFF** (*Backend for Frontend*) — API composta, feita sob medida para um cliente específico.

**BFLA** — *Broken Function Level Authorization*. Chamar operação administrativa sem
permissão. OWASP API5.

**BOLA** — *Broken Object Level Authorization*. Acessar objeto de outro usuário.
**A vulnerabilidade nº 1** do OWASP API Top 10.

**BOPLA** — *Broken Object Property Level Authorization*. Ler ou escrever campo indevido.
Inclui **mass assignment**. OWASP API3.

**Brotli** (`br`) — Algoritmo de compressão, ~5–15% melhor que gzip em texto.

**Brownout** — Indisponibilidade programada e curta de uma API obsoleta, para forçar os
consumidores a perceberem que precisam migrar.

**Bulkhead** — Isolar pools de recursos por dependência, para que uma falha não afogue tudo.

## C

**Cache-Control** — Cabeçalho que declara se e por quanto tempo a resposta pode ser guardada.

**CAP** — Teorema: consistência, disponibilidade e tolerância a partição — escolha dois.
Ver **PACELC**.

**Circuit breaker** — Padrão que interrompe chamadas a um serviço que está falhando,
falhando **rápido** em vez de esperar o timeout.

**Contrato** — A interface mais as promessas de comportamento. Ver **Lei de Hyrum**.

**CORS** — *Cross-Origin Resource Sharing*. Mecanismo **do navegador** que decide se o
JavaScript de uma origem pode ler a resposta de outra. Não é proteção da sua API.

**Cursor** — Identificador opaco que marca a posição na paginação. Estável sob inserção,
diferente de **offset**.

## D

**DataLoader** — Padrão que agrupa consultas de um mesmo ciclo em uma só. Obrigatório em
GraphQL para evitar **N+1**.

**Deprecation** — Cabeçalho (RFC 9745) que sinaliza que o recurso está obsoleto.
Acompanha **Sunset**.

**Design-first** — Escrever o contrato antes do código. Oposto de **code-first**.

## E

**Egress** — Tráfego de saída. **O custo mais subestimado** de operar uma API.
Ver [80](80-custos-e-licencas.md) §3.

**Error budget** — 100% menos o SLO. Quanto de falha você pode gastar no período.

**ETag** — Impressão digital de uma representação. Usado em `If-None-Match` (cache) e
`If-Match` (concorrência).

**Exactly-once** — Não existe na entrega; existe no **efeito**, via at-least-once +
idempotência.

**Expand/contract** — Migração em fases: adicione o novo, use os dois, migre, remova o antigo.

## F

**Falácias da computação distribuída** — Oito suposições falsas (a rede é confiável, a
latência é zero…). Ver [60](60-teoria-avancada.md) §1.

**Falha parcial** — Uma parte do sistema falha enquanto o resto continua. Define sistemas
distribuídos.

**FLP** — Teorema (1985): consenso é impossível em sistema assíncrono com uma falha.

## G

**gRPC** — RPC com Protobuf sobre HTTP/2. Contrato obrigatório, binário, quatro modos de
streaming.

**GraphQL** — Linguagem de consulta em que o **cliente** define os campos da resposta.

## H

**HATEOAS** — *Hypermedia As The Engine Of Application State*. A resposta contém os links
das transições possíveis. A restrição de REST que quase ninguém cumpre.

**HMAC** — Assinatura com chave compartilhada. Base da verificação de webhooks.

**HTTP/1.1, /2, /3** — Versões do protocolo. RFCs 9112, 9113, 9114.

**Head-of-line blocking** — Uma requisição travada bloqueia as seguintes. Na aplicação em
HTTP/1.1, no TCP em HTTP/2, eliminado em HTTP/3.

## I

**Idempotência** — $f(f(S)) = f(S)$. Repetir tem o mesmo efeito de fazer uma vez.

**Idempotency-Key** — Cabeçalho com identificador único da operação, que torna um `POST`
idempotente.

**Interface uniforme** — A quinta restrição de REST. Inclui identificação de recursos,
manipulação por representações, mensagens autodescritivas e **HATEOAS**.

## J

**Jitter** — Aleatoriedade no tempo de espera entre retentativas. Evita *thundering herd*.

**JSON** — *JavaScript Object Notation*. RFC 8259. Formato dominante em APIs web.

**JSON Patch** (RFC 6902) — Formato de PATCH com operações explícitas
(`add`, `remove`, `replace`).

**JSON Merge Patch** (RFC 7386) — Formato de PATCH em que `null` **apaga** o campo.

**JSON Schema** — Vocabulário de validação de JSON. Draft 2020-12. Base do OpenAPI 3.1+.

**JWT** — *JSON Web Token*. Token autocontido e assinado. O payload é **codificado**, não
cifrado.

## L

**Lei de Hyrum** — Com usuários suficientes, **todo** comportamento observável do sistema
será dependido por alguém, esteja no contrato ou não.

**Long polling** — O servidor segura a resposta até haver novidade. Substituído por SSE.

**Lost update** — Duas escritas concorrentes; a segunda apaga a primeira silenciosamente.
Evitado com `ETag` + `If-Match`.

## M

**Mass assignment** — Aceitar cegamente todos os campos do corpo, permitindo ao cliente
alterar campos indevidos.

**MCP** — *Model Context Protocol*. Padrão para agentes de IA descobrirem e usarem
ferramentas. Anthropic, nov/2024.

**mTLS** — TLS mútuo: os dois lados apresentam certificado.

## N

**N+1** — Uma consulta para a lista e mais uma por item. Praga do GraphQL e dos ORMs.

**no-cache** — Pode guardar, **deve revalidar**. Não é o mesmo que **no-store**.

**no-store** — Não guarde em lugar nenhum. Para dado sensível.

## O

**OAuth 2.x** — Framework de autorização delegada. Fluxos: Authorization Code + PKCE,
Client Credentials, Device.

**Offset** — Paginação por "pule N". Frágil sob inserção; custa O(offset) no banco.

**OIDC** — *OpenID Connect*. Camada de identidade sobre OAuth 2.0.

**OpenAPI** — Especificação de contrato para APIs HTTP. Versão corrente: **3.2.0** (set/2025).

**OpenTelemetry** — Padrão de instrumentação para métricas, logs e traces. CNCF.

**Outbox** (*transactional outbox*) — Gravar dado e intenção de publicar na mesma transação;
um processo separado publica depois.

**Over-fetching** — Receber mais dados do que precisa.

**OWASP API Security Top 10** — Lista dos dez riscos mais comuns em APIs.

## P

**PACELC** — Extensão do CAP: se há Partição, escolha A ou C; **senão** (Else), escolha
Latência ou Consistência.

**PKCE** — RFC 7636. Impede a interceptação do código de autorização no OAuth.

**Preflight** — Requisição `OPTIONS` que o navegador faz antes da requisição real, no CORS.

**Problem Details** — RFC 9457. Formato padrão de erro, com `type`, `title`, `status`,
`detail`, `instance`. Media type `application/problem+json`.

**Protobuf** — *Protocol Buffers*. Formato binário do gRPC. O **número** do campo é o
contrato, não o nome.

## Q

**QUIC** — Protocolo de transporte sobre UDP, base do HTTP/3. RFC 9000.

## R

**Rate limiting** — Limitar requisições por período. Resposta correta: `429` + `Retry-After`.

**Recurso** — A coisa de que se fala. Tem identidade (URI) e pode ter várias
**representações**.

**Representação** — Forma concreta de um recurso: o JSON, o XML, o PDF.

**REST** — *REpresentational State Transfer*. Estilo arquitetural com seis restrições,
descrito por Roy Fielding em 2000.

**"RESTful"** — No uso corrente: JSON sobre HTTP com URLs de recursos. No sentido estrito:
respeita as seis restrições, **incluindo HATEOAS**.

**Retry-After** — Cabeçalho que diz quantos segundos esperar. Obrigatório em `429` e `503`.

**Richardson Maturity Model** — Régua de 0 a 3 para medir o uso do HTTP por uma API.
Nível 2 = verbos e status corretos. Nível 3 = hipermídia.

**RPC** — *Remote Procedure Call*. Chamar uma função remota.

## S

**Saga** — Sequência de passos, cada um com uma compensação. Substitui a transação
distribuída, sem isolamento.

**SLI / SLO / SLA** — O que se mede / a meta interna / o compromisso contratual.

**SOAP** — Protocolo de envelope XML com o universo WS-*. Contrato em WSDL.

**SSE** — *Server-Sent Events*. O servidor empurra eventos por uma resposta HTTP que não
termina. Reconexão e retomada automáticas no navegador.

**SSRF** — *Server-Side Request Forgery*. O atacante faz o **seu** servidor chamar uma URL
escolhida por ele. OWASP API7.

**Stateless** (sem estado) — Cada requisição carrega tudo que o servidor precisa. A
restrição de REST com maior impacto em escala.

**Sunset** — Cabeçalho (RFC 8594) com a data em que o recurso deixará de existir.

## T

**Thundering herd** — Muitos clientes retentando no mesmo instante, derrubando o servidor
que tentava se recuperar. Evitado com **jitter**.

**Timeout** — Tempo máximo de espera. **Pré-requisito de toda resiliência**; o padrão de
quase toda biblioteca HTTP é infinito, e é o padrão errado.

**Traceparent** — Cabeçalho W3C que propaga o contexto de tracing entre serviços.

## U

**Under-fetching** — Precisar de várias chamadas para montar uma tela.

**URI / URL** — Identificador / localizador de recurso.

**UUIDv4** — Identificador aleatório. Fragmenta índice em tabela grande.

**UUIDv7** — RFC 9562 (mai/2024). Embute timestamp: é **ordenável no tempo** e agrupa bem em
índice. **Prefira-o ao v4** para chave de banco.

## V

**Vary** — Cabeçalho que diz quais cabeçalhos da requisição afetam a resposta.
**`Vary: Authorization` é obrigatório** em resposta cacheável e autenticada.

## W

**Webhook** — O servidor chama a **sua** URL quando algo acontece. Exige assinatura HMAC,
timestamp e deduplicação.

**WebSocket** — Canal TCP bidirecional persistente, negociado a partir do HTTP (`101`).
Depois do handshake, **não é mais HTTP**.

**WSDL** — Descrição de contrato de serviço SOAP, em XML.

---

## Símbolos e convenções

| Símbolo | Significado |
|---|---|
| `2xx` | sucesso |
| `3xx` | redirecionamento / cache |
| `4xx` | **o cliente errou** — repetir vai falhar de novo |
| `5xx` | **o servidor errou** — repetir pode funcionar |
| `q=0.8` | qualidade relativa na negociação de conteúdo |
| `W/"abc"` | ETag **fraco** (semanticamente equivalente) |
| `"abc"` | ETag **forte** (byte a byte) |
| `application/json` | media type de JSON |
| `application/problem+json` | media type de erro (RFC 9457) |
| `text/event-stream` | media type de SSE |
| `+json` (sufixo) | o formato base é JSON |
| `__` em Protobuf | — (não se aplica; ver o número do campo) |

## Códigos de status mais usados

| Código | Nome | Uso |
|---|---|---|
| 200 | OK | leitura ou atualização com corpo |
| 201 | Created | criou. **Envie `Location`** |
| 202 | Accepted | aceitei, processo depois |
| 204 | No Content | deu certo, sem corpo |
| 301/308 | Moved Permanently | mudou para sempre |
| 304 | Not Modified | use seu cache |
| 400 | Bad Request | malformada |
| 401 | Unauthorized | **não autenticado** |
| 403 | Forbidden | autenticado, **sem permissão** |
| 404 | Not Found | não existe |
| 405 | Method Not Allowed | **envie `Allow`** |
| 406 | Not Acceptable | não produzo esse formato |
| 409 | Conflict | conflito de estado |
| 410 | Gone | existiu, foi removido de propósito |
| 412 | Precondition Failed | o `If-Match` não bateu |
| 413 | Content Too Large | corpo grande demais |
| 415 | Unsupported Media Type | Content-Type não aceito |
| 422 | Unprocessable Content | sintaxe ok, **semântica inválida** |
| 428 | Precondition Required | exijo `If-Match` |
| 429 | Too Many Requests | **envie `Retry-After`** |
| 500 | Internal Server Error | eu quebrei |
| 502 | Bad Gateway | quem está atrás de mim falhou |
| 503 | Service Unavailable | indisponível. **`Retry-After`** |
| 504 | Gateway Timeout | quem está atrás demorou |
