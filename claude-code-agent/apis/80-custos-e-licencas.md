# 80 · Custos e licenças

`Nível: todos` · **`Preços consultados em 11/08/2026`**
`Câmbio usado: US$ 1 ≈ R$ 5,11 (11/08/2026)`

> ⚠️ **Preço sem data é desinformação.** Todos os valores têm a data de consulta e são de
> **tabela pública**. Contratos corporativos costumam ter desconto significativo. Confirme
> na fonte antes de usar em orçamento.

**Primeiro, a informação mais importante deste arquivo:** *aprender e construir APIs custa
**zero**.* Todo este curso, incluindo o projeto-modelo, roda com software livre e sem
nenhuma conta paga. O que custa é **operar em escala** — e é disso que trata o resto.

---

## 1. O que é gratuito (praticamente tudo que importa)

| Item | Licença | Custo |
|---|---|---|
| **HTTP, REST** | especificação aberta (IETF) | zero |
| **RFCs** | abertos, livres para leitura e implementação | zero |
| **OpenAPI** | Apache 2.0 | zero |
| **JSON Schema** | especificação aberta | zero |
| **GraphQL** | especificação sob a GraphQL Foundation (OWF) | zero |
| **gRPC / Protobuf** | Apache 2.0 / BSD-3 | zero |
| **AsyncAPI** | Apache 2.0 | zero |
| **MCP** | especificação aberta | zero |
| **curl** | licença tipo MIT | zero |
| **jq** | MIT | zero |
| **Node.js** | MIT | zero |
| **Fastify, Express, FastAPI, Spring** | MIT / Apache 2.0 | zero |
| **Bruno** | MIT (edição community) | zero |
| **Hoppscotch** | MIT | zero |
| **Insomnia** | Apache 2.0 (núcleo) | zero |
| **Spectral, Redocly CLI, Prism** | Apache 2.0 / MIT | zero |
| **Kong Gateway OSS, APISIX, Tyk OSS, Traefik** | Apache 2.0 / MIT | zero |
| **Prometheus, Grafana, Jaeger, OpenTelemetry** | Apache 2.0 | zero |

**Quem paga essa conta?** Combinação de: fundações (Linux Foundation, CNCF, OpenJS) mantidas
por empresas; empresas que abrem o núcleo e vendem a edição corporativa (*open core*); e
trabalho voluntário. **O modelo open core é o mais comum aqui** — e é o que explica por que
Kong, Tyk e Insomnia têm versão gratuita: ela é o funil da versão paga.

> **Consequência prática:** o gratuito é excelente, mas o que você mais vai querer em
> produção (SSO, RBAC, painel de desenvolvedor, suporte) costuma estar do lado pago.
> Isso é legítimo — só não seja pego de surpresa.

---

## 2. API Gateway gerenciado — preços de 11/08/2026

| Fornecedor | Preço por 1 milhão de chamadas | Observação |
|---|---|---|
| **AWS API Gateway — HTTP API** | **US$ 1,00** | cai para ~US$ 0,90 acima de 300 M/mês |
| **AWS API Gateway — REST API** | **US$ 3,50** | escalona para ~2,80 e ~2,38 em volume |
| **Cloudflare** | **~US$ 2,00** por 10 M (ordem de grandeza) | modelo diferente; muito competitivo |
| **Google Cloud API Gateway** | camada gratuita + por chamada | ver §2.2 |
| **Apigee (Google)** | **~US$ 20–30** por milhão | 8× a 30× o AWS HTTP API |
| **Kong Konnect** | ~US$ 105/mês por serviço, com 1 M incluído; **US$ 200** por milhão adicional | |
| **Kong Enterprise (autogerido)** | ~US$ 5.350/ano para ~5 M chamadas e 50 serviços | |
| **Azure API Management** | por tier (Consumption, Developer, Standard, Premium) | Premium custa milhares/mês |

**A diferença entre AWS HTTP API (US$ 1) e Apigee (US$ 20–30) é de uma a duas ordens de
grandeza.** Não é porque um é ruim: Apigee inclui gestão de API completa (portal do
desenvolvedor, monetização, políticas avançadas, analytics). Você está comparando um
roteador com uma plataforma.

**Cenários concretos, só do gateway:**

| Volume/mês | AWS HTTP API | AWS REST API | Apigee (~US$ 25) |
|---|---|---|---|
| 1 milhão | US$ 1 (~R$ 5) | US$ 3,50 (~R$ 18) | US$ 25 (~R$ 128) |
| 100 milhões | US$ 100 (~R$ 511) | US$ 350 (~R$ 1.789) | US$ 2.500 (~R$ 12.775) |
| 1 bilhão | ~US$ 930 (~R$ 4.752) | ~US$ 2.700 (~R$ 13.797) | ~US$ 25.000 (~R$ 127.750) |

> **Escolher AWS REST API quando o HTTP API bastaria custa 3,5× mais**, e a diferença
> funcional (WAF integrado, validação de requisição, chaves de API nativas, endpoint
> privado) só importa para alguns casos. **Verifique se você precisa antes de pagar.**

### 2.2 Camadas gratuitas

| Fornecedor | Gratuito |
|---|---|
| AWS API Gateway | 1 milhão de chamadas/mês nos primeiros 12 meses |
| Google Cloud API Gateway | cota mensal gratuita de chamadas |
| Cloudflare Workers | plano gratuito com cota diária de requisições |
| Kong / APISIX / Tyk / Traefik (autogerido) | **ilimitado** — você paga só a máquina |

**Para aprender e para projeto pequeno, a camada gratuita basta com folga.**

---

## 3. O custo escondido que domina a conta: **egress**

**Esta é a seção que mais economiza dinheiro deste arquivo.**

Provedores de nuvem cobram pouco (ou nada) pelos dados que **entram** e caro pelos que
**saem**. Numa API, a resposta é o que sai — então **a sua API é, por definição, uma máquina
de gerar egress**.

| Direção | Custo típico |
|---|---|
| Entrada (ingress) | geralmente **grátis** |
| Saída para a internet (egress) | ~US$ 0,05–0,12 por GB nos grandes provedores |
| Entre regiões | cobrado |
| Entre zonas de disponibilidade | frequentemente cobrado |
| Cloudflare, e alguns provedores menores | **egress zero ou muito baixo** |

**A conta que surpreende:**

```text
API que devolve 50 KB por resposta, 100 milhões de chamadas/mês
= 5 TB de egress
× US$ 0,09/GB
= US$ 450/mês  (~R$ 2.300)   ← só de tráfego de saída

Gateway (AWS HTTP API): US$ 100
Egress:                 US$ 450   ← 4,5× o gateway
```

**O egress frequentemente custa mais que o gateway e mais que a computação.** E quase
nunca aparece na estimativa inicial.

**Como reduzir, em ordem de impacto:**

| Ação | Redução típica |
|---|---|
| **Compressão** (gzip/brotli) em JSON | **70–85%** |
| **Campos esparsos** (`?campos=id,nome`) | 30–80%, conforme o caso |
| **Cache/CDN** (a resposta nem sai da origem) | até 90% em dado comum |
| `304 Not Modified` com ETag | ~100% naquela resposta |
| Paginação com limite razoável | evita respostas gigantes |
| Provedor com egress barato | 100% do custo unitário |

> **Ligar compressão é a otimização de melhor retorno da lista inteira.** É uma linha de
> configuração e corta ~75% da conta de egress. Se você fizer só uma coisa depois de ler
> este arquivo, faça essa.

---

## 4. O custo total de uma API em produção

| Componente | Ordem de grandeza (100 M chamadas/mês) |
|---|---|
| Gateway | US$ 100–2.500 |
| **Egress** | **US$ 200–800** |
| Computação (contêineres/serverless) | US$ 100–1.000 |
| Banco de dados | US$ 100–2.000 |
| Cache (Redis) | US$ 50–300 |
| Observabilidade (logs, métricas, traces) | **US$ 100–3.000** |
| WAF / proteção DDoS | US$ 20–500 |
| CDN | US$ 20–200 |

**A observabilidade é o segundo custo mais subestimado.** Plataformas como Datadog e New
Relic cobram por volume de log e por host; uma API com log verboso pode gastar mais
observando-se do que executando. Alternativas: amostragem de traces (não guarde 100%),
retenção curta para log de debug, e pilha auto-hospedada (Prometheus + Loki + Grafana).

---

## 5. Consumir APIs de terceiros

| Categoria | Modelo | Faixa típica |
|---|---|---|
| Mapas / geocodificação | por requisição | US$ 2–10 por mil |
| Pagamento | percentual da transação | 2–5% + taxa fixa |
| E-mail transacional | por mensagem | US$ 0,10–1 por mil |
| SMS | por mensagem | R$ 0,05–0,20 (Brasil) |
| Modelos de linguagem | por token | varia muito; **modele por volume** |
| Consulta de CEP/CNPJ | grátis ou por requisição | ViaCEP e BrasilAPI são gratuitos |
| Dados públicos (IBGE, Banco Central) | **gratuitos** | — |

**As três armadilhas de custo em API de terceiro:**

1. **Cobrança por requisição sem cache.** Se o dado muda uma vez por dia e você consulta a
   cada requisição, está pagando por informação que já tem. **Cache é dinheiro literal.**
2. **Retry multiplicando a conta.** Retentativa sem limite pode triplicar o custo num
   incidente — e cada tentativa é cobrada.
3. **Ausência de teto.** Configure alerta de gasto **e** limite rígido. Um laço com bug pode
   gerar uma fatura de cinco dígitos em uma noite. Isso acontece com regularidade.

> **APIs públicas brasileiras gratuitas e úteis:** ViaCEP (CEP), BrasilAPI (agregadora),
> IBGE (localidades, dados), Banco Central (câmbio, SELIC), Portal da Transparência.
> Confira os termos de uso antes de depender delas em produção.

---

## 6. Ferramentas: gratuito × pago

| Ferramenta | Gratuito | Pago |
|---|---|---|
| **Postman** | uso individual limitado | por usuário/mês para recursos de time |
| **Bruno** | **completo, offline, MIT** | edição com recursos de time |
| **Insomnia** | núcleo aberto | plano de time |
| **Hoppscotch** | completo, auto-hospedável | nuvem |
| **Swagger/SmartBear** | Swagger UI e Editor | SwaggerHub para time |
| **Redocly** | CLI aberta | portal hospedado |
| **Stoplight** | Spectral e Prism abertos | plataforma |
| **Kong** | Gateway OSS | Konnect / Enterprise |
| **Tyk / APISIX / Traefik** | núcleo aberto | edição corporativa |
| **Datadog / New Relic** | camada gratuita mínima | por host e por volume |
| **Prometheus + Grafana + Loki** | **completo** | Grafana Cloud opcional |

> **Recomendação para começar:** **Bruno** (coleções em arquivo, versionadas no Git) ou a
> extensão **REST Client** do VS Code. Você evita o risco de sincronizar coleções — com
> tokens dentro — para a nuvem de um fornecedor. Ver [03-instalacao.md](03-instalacao.md) §6.

---

## 7. Licenças — o que você precisa saber

### 7.1 Das especificações

Todas as specs deste material são **abertas e implementáveis sem licença**: HTTP (IETF),
OpenAPI (Apache 2.0), GraphQL (OWF), gRPC/Protobuf (Apache 2.0/BSD), JSON Schema, AsyncAPI,
MCP. **Você pode implementar qualquer uma comercialmente, sem pagar nada.**

### 7.2 Das ferramentas — as três famílias

| Família | Exemplos | O que exige |
|---|---|---|
| **Permissiva** | MIT, Apache 2.0, BSD | atribuição; uso comercial livre |
| **Copyleft fraco** | LGPL, MPL 2.0 | alterações no componente voltam à comunidade |
| **Copyleft forte** | GPL, **AGPL** | derivados também sob a mesma licença |

**A AGPL merece atenção**, porque afeta APIs especificamente: ela estende o copyleft ao uso
**pela rede**. Se você modifica um software AGPL e o disponibiliza como serviço, precisa
disponibilizar o código modificado — mesmo sem distribuir binário. Vários bancos de dados e
ferramentas de infraestrutura usam AGPL exatamente por isso.

**Licenças "source-available" (BSL/BUSL, SSPL, Elastic License)** não são open source pela
definição da OSI: restringem uso concorrente ou como serviço gerenciado. Várias empresas
migraram para elas nos últimos anos. **Se você pretende oferecer um serviço baseado numa
ferramenta, leia a licença antes** — o modelo mudou em produtos populares e o histórico não
é garantia.

### 7.3 Do que você consome

Uma API de terceiro tem **termos de uso**, não licença de software. Verifique:

- **rate limit** e o que acontece ao excedê-lo;
- se pode **cachear** e por quanto tempo (alguns proíbem!);
- se pode **redistribuir** os dados;
- **atribuição** obrigatória;
- **SLA** e o que ele garante de verdade;
- política de **mudança e depreciação**;
- para dados pessoais: **LGPD** — base legal, finalidade, transferência internacional.

> **Dois erros comuns e caros:** (1) cachear dados de uma API que proíbe cache em contrato;
> (2) redistribuir dados de terceiro num produto seu sem direito. Ambos são problemas
> jurídicos, não técnicos, e aparecem tarde.

---

## 8. Como reduzir custo — checklist ordenado por impacto

1. **Ligue compressão.** Uma linha, corta ~75% do egress.
2. **Use cache HTTP e CDN** no que for comum. É o que separa 1 servidor de 100.
3. **Use `ETag` e responda `304`.** Barato de implementar, elimina o corpo.
4. **Paginação com limite máximo.** Impede a resposta de 500 MB.
5. **Campos esparsos** para clientes que não precisam de tudo.
6. **Escolha o gateway certo.** AWS HTTP API em vez de REST API, se der: 3,5× mais barato.
7. **Amostre traces.** Guardar 100% em produção é caro e desnecessário.
8. **Retenção curta para log de debug.** Longa só para o de auditoria.
9. **Cache das APIs de terceiro** que você consome. É dinheiro literal.
10. **Teto de gasto e alerta** em toda API paga. Sem exceção.
11. **Avalie egress do provedor.** Cloudflare e alguns provedores menores cobram muito
    menos — em volume alto, isso sozinho justifica a escolha.
12. **Auto-hospede a observabilidade** se o volume for grande. Prometheus + Loki + Grafana.

---

## 9. Autoteste

1. Quanto custa aprender e construir APIs com este material? Por quê?
2. O que é "open core" e por que ele explica a versão gratuita de Kong e Insomnia?
3. Qual a diferença de preço entre AWS HTTP API e REST API? Quando a mais cara se justifica?
4. Por que o egress é o custo mais subestimado? Faça a conta de 100 M chamadas de 50 KB.
5. Qual é a única otimização que corta ~75% do egress?
6. Cite as três armadilhas de custo ao consumir API de terceiro.
7. O que a AGPL exige que a GPL não exige? Por que isso afeta APIs especificamente?
8. O que verificar nos termos de uso de uma API de terceiro? Cite quatro itens.
9. Cite os cinco itens de maior impacto do checklist de redução de custo.

---

### Fontes consultadas (11/08/2026)

- Zuplo — *API Gateway Pricing Compared (2026)* — https://zuplo.com/learning-center/api-gateway-pricing-comparison-2026
- CloudZero — *AWS API Gateway Pricing Simplified: A 2026 Guide* — https://www.cloudzero.com/blog/aws-api-gateway-pricing/
- APIGatewayCost — comparativos 2026 — https://apigatewaycost.com/
- DigitalAPI — *API Management Cost: AWS, Kong, Apigee & Azure Pricing Guide (2026)* — https://www.digitalapi.ai/blogs/api-management-cost
- Open Source Initiative — definição e lista de licenças — https://opensource.org/licenses
- Investing.com — cotação USD/BRL em 11/08/2026 — https://br.investing.com/currencies/usd-brl
