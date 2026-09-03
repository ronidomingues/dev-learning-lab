# APIs — Mapa do Assunto

`Nível: do zero absoluto ao de pesquisa` · `Última atualização: 11/08/2026`
`Base técnica: HTTP RFC 9110–9114 · OpenAPI 3.2.0 · Node.js 24 LTS`

---

## Sua pergunta, respondida em 30 segundos

Você perguntou quatro coisas. Aqui está a resposta curta; o material inteiro é o desdobramento dela.

**1. O que é uma API?**
É um **contrato**: um conjunto de operações que um software oferece para que **outro
software** o utilize, sem precisar saber como ele funciona por dentro.
*(Detalhe em [01-introducao-leigo.md](01-introducao-leigo.md) e [10-fundamentos.md](10-fundamentos.md).)*

**2. O que é uma API RESTful?**
REST é um **estilo arquitetural** definido por Roy Fielding em 2000, com **seis restrições**.
Uma API é "RESTful" quando as respeita — o que inclui uma restrição, a de **hipermídia
(HATEOAS)**, que **quase nenhuma API do mercado cumpre**. Na prática, "REST" virou sinônimo
de "JSON sobre HTTP com URLs de recursos", que é outra coisa.
*(Detalhe em [13-rest-e-restful.md](13-rest-e-restful.md).)*

**3. Qual a diferença entre API e API RESTful?**
"API" é o gênero; "RESTful" é uma espécie. Toda API RESTful é uma API. A recíproca é falsa:
a biblioteca `Math` do JavaScript é uma API e não tem nada de REST. Uma API pode ser SOAP,
gRPC, GraphQL, uma biblioteca local, uma chamada de sistema operacional.
*(Detalhe em [10-fundamentos.md](10-fundamentos.md) §2.)*

**4. Quais tipos existem e quais as diferenças?**
Duas classificações independentes, que costumam ser confundidas:

| Por **escopo** (quem usa) | Por **estilo** (como se conversa) |
|---|---|
| API de biblioteca (local, no mesmo processo) | REST |
| API de sistema operacional (syscall) | RPC / gRPC |
| API remota — **web API** | SOAP |
| API interna / privada | GraphQL |
| API de parceiro | WebSocket · SSE · Webhook |
| API pública / aberta | Event-driven (fila, tópico) |
| | MCP (para agentes de IA) |

A comparação completa, com quando usar cada um, está em
[19-como-escolher.md](19-como-escolher.md) — é o arquivo que responde diretamente à sua
quarta pergunta, com tabelas lado a lado e um fluxograma de decisão.

---

## O que você saberá ao final

- Explicar o que é uma API para alguém de fora da tecnologia, sem jargão.
- Distinguir com precisão **API**, **web API**, **REST**, **RESTful** e "REST-ish".
- Entender HTTP de verdade: métodos, status, cabeçalhos, cache, negociação de conteúdo,
  e por que HTTP/1.1, /2 e /3 existem.
- Recitar e aplicar as **seis restrições de REST**, e julgar honestamente o nível de
  maturidade de qualquer API (modelo de Richardson).
- Projetar uma API que não envergonhe: recursos, URIs, versionamento, paginação, filtros,
  erros padronizados (RFC 9457), idempotência, concorrência otimista.
- Escolher entre REST, GraphQL, gRPC, SOAP, WebSocket, SSE, webhook e mensageria — com
  critério, não por moda.
- Proteger uma API: OAuth 2.1, OIDC, JWT, mTLS, HMAC, e o OWASP API Security Top 10.
- Escrever e usar um contrato **OpenAPI 3.2**, e gerar código, testes e documentação dele.
- Operar uma API em produção: gateway, rate limiting, observabilidade, SLO, depreciação.
- Estimar **custo** de expor uma API (gateway, egress, suporte) e conhecer as licenças.
- Discutir os limites teóricos: idempotência, exactly-once, CAP, complexidade de consultas
  GraphQL, e por que "compatibilidade retroativa" é um problema de subtipagem.

---

## Roteiro de leitura

### Caminho rápido — "só quero entender" (2 horas)
`01` → `10` → `13` → `19`

### Caminho de quem vai **consumir** uma API
`01` → `02` → `03` → `04` → `12` → `16` → `06` → `75`

### Caminho de quem vai **construir** uma API
`01` → `03` → `04` → `10` → `12` → `13` → `14` → `16` → `17` → `07-projeto-modelo/` → `70`

### Caminho de arquitetura / decisão técnica
`10` → `11` → `13` → `15` → `19` → `18` → `60` → `65`

### Caminho de quem decide compra
`01` → `19` → `18` → `80` → `65`

---

## Arquivos

### BLOCO A · Porta de entrada (01–09)

| Arquivo | Nível | Conteúdo |
|---|---|---|
| [01-introducao-leigo.md](01-introducao-leigo.md) | iniciante | O que é uma API, sem jargão. As quatro perguntas respondidas devagar. |
| [02-pre-requisitos.md](02-pre-requisitos.md) | iniciante | O que saber antes. Tempo realista. Rota de resgate. |
| [03-instalacao.md](03-instalacao.md) | iniciante | curl, HTTPie, Bruno/Postman, Node, Docker — por SO, com verificação. |
| [04-como-comecar.md](04-como-comecar.md) | iniciante | Primeira chamada a uma API real e primeira API própria, em 40 min. |
| [05-manual-de-uso.md](05-manual-de-uso.md) | intermediário | Referência: métodos, status, cabeçalhos, curl, HTTPie, jq. |
| [06-exemplos.md](06-exemplos.md) | intermediário | 15 exemplos executáveis, do `GET` trivial ao webhook assinado. |
| [07-projeto-modelo/](07-projeto-modelo/README.md) | intermediário | API REST completa em Node.js: OpenAPI, auth, paginação, testes. Roda. |

### BLOCO B · Núcleo (10–69)

| Arquivo | Nível | Conteúdo |
|---|---|---|
| [10-fundamentos.md](10-fundamentos.md) | iniciante | Contrato, interface, acoplamento, cliente/servidor. O vocabulário. |
| [11-historia.md](11-historia.md) | iniciante | De chamadas de biblioteca a MCP: 1960 → 2026, e o porquê de cada virada. |
| [12-http-por-dentro.md](12-http-por-dentro.md) | intermediário | O protocolo: métodos, status, headers, cache, HTTP/1.1 vs /2 vs /3. |
| [13-rest-e-restful.md](13-rest-e-restful.md) | intermediário | As 6 restrições de Fielding, HATEOAS, Richardson, e a verdade incômoda. |
| [14-design-de-api-rest.md](14-design-de-api-rest.md) | intermediário | Recursos, URIs, versionamento, paginação, erros, idempotência, ETag. |
| [15-estilos-e-protocolos.md](15-estilos-e-protocolos.md) | intermediário | SOAP, RPC, gRPC, GraphQL, WebSocket, SSE, webhooks, mensageria, MCP. |
| [16-seguranca.md](16-seguranca.md) | avançado | Autenticação, autorização, OAuth 2.1, OIDC, JWT, mTLS, OWASP API Top 10. |
| [17-contratos-e-documentacao.md](17-contratos-e-documentacao.md) | avançado | OpenAPI 3.2, JSON Schema, AsyncAPI, Protobuf, testes de contrato. |
| [18-operacao-e-ciclo-de-vida.md](18-operacao-e-ciclo-de-vida.md) | avançado | Gateway, rate limit, observabilidade, SLO, versionamento, depreciação. |
| [19-como-escolher.md](19-como-escolher.md) | todos | **Comparação lado a lado de todos os estilos.** Fluxograma de decisão. |
| [60-teoria-avancada.md](60-teoria-avancada.md) | pesquisa | Idempotência, exactly-once, CAP, subtipagem e compatibilidade, complexidade. |
| [65-estado-da-arte.md](65-estado-da-arte.md) | pesquisa | Agosto/2026: OpenAPI 3.2, HTTP/3 estagnado, MCP, APIs para agentes. |

### BLOCO C · Prática e erros (70–79)

| Arquivo | Nível | Conteúdo |
|---|---|---|
| [70-pratica.md](70-pratica.md) | todos | 10 laboratórios com critério de aprovação verificável. |
| [75-armadilhas.md](75-armadilhas.md) | todos | Erros clássicos, mitos, más práticas e por que sobrevivem. |

### BLOCO D · Economia e ecossistema (80–89)

| Arquivo | Nível | Conteúdo |
|---|---|---|
| [80-custos-e-licencas.md](80-custos-e-licencas.md) | todos | Gateways, egress, licenças, custo oculto. Preços de 11/08/2026. |
| [85-cursos-e-certificacoes.md](85-cursos-e-certificacoes.md) | todos | Cursos grátis PT/EN/FR e o que existe de certificação (pouco). |

### BLOCO E · Fontes (90–99)

| Arquivo | Nível | Conteúdo |
|---|---|---|
| [90-bibliografia.md](90-bibliografia.md) | todos | Livros com edição, nível e o que envelheceu. |
| [95-referencias.md](95-referencias.md) | todos | RFCs, specs, ferramentas, pessoas. |
| [GLOSSARIO.md](GLOSSARIO.md) | todos | Todo o jargão definido. |

---

## Status por bloco

| Bloco | Status | Observação |
|---|---|---|
| A · Porta de entrada | ✅ | 7 documentos + projeto-modelo executável |
| B · Núcleo | ✅ | 12 documentos, contrato → protocolos → teoria |
| C · Prática e erros | ✅ | 10 laboratórios + catálogo de armadilhas |
| D · Economia | ✅ | Preços consultados em 11/08/2026 |
| E · Fontes | ✅ | RFCs e specs verificadas |
| Glossário | ✅ | ~130 termos |

Legenda: ✅ completo · 🟡 parcial · ⬜ pendente

---

## Relação com os outros assuntos desta pasta

| Assunto | Onde se cruza |
|---|---|
| [spa-single-page-application](../spa-single-page-application/00-MAPA.md) | uma SPA é, por definição, um cliente de API. Ver `08-dados-e-rede.md` lá |
| [salesforce](../salesforce/00-MAPA.md) | `17-integracao-e-apis.md` aplica tudo daqui a uma plataforma real, com limites concretos |

---

## Aviso de validade

O que envelhece: `65-estado-da-arte.md` (meses), `80-custos-e-licencas.md` (meses),
`03-instalacao.md` (versões de ferramenta), `85-cursos-e-certificacoes.md` (um ano).

O que **não** envelhece: `10`, `12`, `13`, `60`. HTTP tem 35 anos e os RFCs de 2022
consolidaram semântica que já era estável. A dissertação de Fielding é de 2000 e continua
sendo a definição normativa de REST. Invista seu tempo de estudo aí.

---

## Autoteste do mapa

1. Em uma frase, qual a diferença entre "API" e "API RESTful"?
2. Cite as duas classificações independentes de tipos de API. Por que confundi-las gera erro?
3. Qual restrição de REST quase nenhuma API do mercado cumpre?
4. Qual arquivo você leria primeiro para decidir entre REST e gRPC?
5. Qual parte deste material continuará válida em 2036, e por quê?
