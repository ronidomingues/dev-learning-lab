# 15 · Estilos e protocolos — o catálogo completo

`Nível: intermediário` · `Atualizado: 11/08/2026`

Cada estilo, o problema que resolve, como se parece, e o que ele custa.
A **comparação lado a lado** e o fluxograma de decisão estão em
[19-como-escolher.md](19-como-escolher.md); aqui está o detalhe de cada um.

---

## 1. RPC — Remote Procedure Call

**A ideia:** chamar uma função que roda em outra máquina.

```http
POST /rpc
{"jsonrpc": "2.0", "method": "calcularFrete",
 "params": {"cep": "01310-100", "peso_g": 1200}, "id": 1}
→
{"jsonrpc": "2.0", "result": {"valor_centavos": 2490, "prazo_dias": 3}, "id": 1}
```

**Variantes:** JSON-RPC 2.0, XML-RPC, gRPC (§3), tRPC, Twirp, Connect.

| A favor | Contra |
|---|---|
| natural para **ações**, não "coisas" | perde a semântica do HTTP: cache, status, idempotência |
| contrato explícito de entrada e saída | nível 0 de Richardson |
| geração de código simples | intermediários não entendem nada do tráfego |
| não precisa torturar substantivos | difícil de explorar sem documentação |

> **Quando RPC é mais honesto que REST:** quando o seu domínio é feito de **verbos**, não de
> substantivos. `traduzir`, `calcular`, `validar`, `simular`, `renderizar`. Forçar isso em
> `POST /traducoes` funciona, mas é uma ficção — e ficções custam clareza.

---

## 2. SOAP

**A ideia:** envelope XML com um sistema formal de padrões em volta.

```xml
POST /servico HTTP/1.1
Content-Type: text/xml; charset=utf-8
SOAPAction: "http://exemplo.com/ObterSaldo"

<?xml version="1.0"?>
<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope">
  <soap:Header>
    <wsse:Security>...</wsse:Security>
  </soap:Header>
  <soap:Body>
    <ObterSaldo xmlns="http://exemplo.com/">
      <conta>12345-6</conta>
    </ObterSaldo>
  </soap:Body>
</soap:Envelope>
```

**O contrato é o WSDL** — um XML que descreve operações, tipos e endereços. Ferramentas
geram cliente e servidor a partir dele.

| A favor | Contra |
|---|---|
| contrato formal, verificável por máquina | **verbosidade extrema** |
| **WS-Security**: assinatura e criptografia **por mensagem** | complexidade do universo WS-* |
| transações distribuídas (WS-AtomicTransaction) | curva de aprendizado de semanas |
| independente de transporte (HTTP, SMTP, JMS) | difícil de depurar à mão |
| maturidade de 25 anos em ferramentas corporativas | ninguém novo quer aprender |

**Onde SOAP ainda vive, e por quê:** bancos, seguradoras, governo, telecomunicações,
integrações B2B antigas. Não é inércia burra — **WS-Security resolve coisas que REST não
resolve**: assinatura no nível da mensagem (que sobrevive a intermediários que reprocessam)
e não-repúdio. Quando a mensagem precisa ser provadamente autêntica anos depois, TLS não
basta, porque TLS protege o transporte, não o documento.

> **Não crie APIs SOAP novas.** Mas se você trabalha com integração corporativa no Brasil,
> vai encontrá-las — nota fiscal eletrônica, sistemas bancários, órgãos públicos. Saber ler
> um WSDL é uma habilidade empregável.

---

## 3. gRPC

**A ideia:** RPC com contrato binário (Protocol Buffers) sobre HTTP/2.

```protobuf
syntax = "proto3";
service Catalogo {
  rpc ObterLivro    (ObterPedido) returns (Livro);
  rpc ListarLivros  (ListaPedido) returns (stream Livro);          // servidor transmite
  rpc EnviarLote    (stream Livro) returns (Resumo);               // cliente transmite
  rpc Conversar     (stream Msg)   returns (stream Msg);           // os dois
}
message Livro {
  int32  id = 1;        // o NÚMERO é o contrato, não o nome
  string titulo = 2;
  repeated string generos = 5;
}
```

**Os quatro modos** são a característica que REST não tem:

| Modo | Uso |
|---|---|
| Unário | requisição–resposta comum |
| Streaming do servidor | resultados grandes, atualizações contínuas |
| Streaming do cliente | upload em pedaços, telemetria |
| Bidirecional | conversa contínua nos dois sentidos |

| A favor | Contra |
|---|---|
| **30–50% menos bytes** que JSON | ilegível sem ferramenta |
| contrato obrigatório e verificado | não funciona direto do navegador (precisa de **gRPC-Web** + proxy) |
| geração de código excelente em ~12 linguagens | curva de aprendizado do Protobuf |
| streaming nativo | depuração exige `grpcurl` |
| *deadlines* e cancelamento propagados | cache HTTP não se aplica |
| códigos de erro tipados | infraestrutura precisa suportar HTTP/2 fim a fim |

**A regra de compatibilidade do Protobuf**, que é a melhor parte:
- o **número** do campo é o contrato; renomear é seguro;
- adicionar campo novo é seguro (clientes antigos ignoram);
- **nunca reutilize um número** — use `reserved`;
- nunca mude o tipo de um campo existente.

**O arranjo dominante em 2026:** REST/GraphQL na borda (navegador, parceiros, público),
**gRPC entre serviços internos**. Não é indecisão — é usar cada um onde ele ganha.

---

## 4. GraphQL

**A ideia:** o **cliente** descreve exatamente os dados que quer.

```graphql
query {
  pedido(id: "42") {
    total
    cliente { nome email }
    itens(primeiros: 3) { quantidade produto { nome preco } }
  }
}
```
```json
{ "data": { "pedido": { "total": 4790,
  "cliente": { "nome": "Ana", "email": "ana@x.com" },
  "itens": [ ... ] } } }
```

**Resolve dois problemas reais de REST:**
- **over-fetching**: `/usuarios/1` traz 40 campos, você usa 3;
- **under-fetching**: montar uma tela exige 5 chamadas encadeadas (o "waterfall" móvel).

**Cria seis problemas novos:**

| Problema | Detalhe |
|---|---|
| **Cache HTTP some** | tudo é `POST /graphql`. CDN não ajuda. Exige *persisted queries* |
| **N+1** | cada resolver consulta o banco. Exige **DataLoader** em todo lugar |
| **Consultas maliciosas** | aninhamento profundo é exponencial. Exige *depth limit* e *cost analysis* |
| **Status HTTP** | erros vêm em `200` com array `errors`. Monitoramento por status não funciona |
| **Upload de arquivo** | fora da spec; exige extensão |
| **Rate limit por complexidade** | contar requisições não faz sentido; é preciso pontuar a consulta |

**Federation** permite compor um único grafo a partir de vários serviços — poderoso e caro
em complexidade operacional.

> **Recomendação:** GraphQL compensa com **muitos clientes de necessidades diferentes** sobre
> um **grafo de dados rico** e um time com maturidade para operar cache, DataLoader e limite
> de complexidade. Não compensa em API pública simples nem em CRUD com um consumidor.
> Demonstração do N+1 em [06-exemplos.md](06-exemplos.md) §13.

---

## 5. WebSocket

**A ideia:** um canal TCP bidirecional persistente, negociado a partir do HTTP.

```http
GET /chat HTTP/1.1
Upgrade: websocket
Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==
→
HTTP/1.1 101 Switching Protocols
Sec-WebSocket-Accept: s3pPLMBiTxaQ9kYGzzhZRbK+xOo=
```

**Depois do `101`, não é mais HTTP.** É um fluxo binário de quadros. Você perde: cache,
códigos de status, cabeçalhos por mensagem, e a maior parte das ferramentas de depuração.

| A favor | Contra |
|---|---|
| latência mínima nos dois sentidos | conexão com estado — atrapalha escala horizontal |
| overhead por mensagem muito baixo | reconexão é **problema seu** |
| texto e binário | autenticação é atípica (não há cabeçalho por mensagem) |
| ideal para chat, jogo, colaboração | proxies e balanceadores exigem configuração |

**Use quando:** o **cliente** precisa enviar com frequência. Se o fluxo é só
servidor → cliente, **SSE é melhor** (§6).

---

## 6. Server-Sent Events (SSE)

**A ideia:** o servidor empurra eventos por uma resposta HTTP que não termina.

```http
GET /eventos
Accept: text/event-stream
→
HTTP/1.1 200 OK
Content-Type: text/event-stream
Cache-Control: no-cache

id: 1
event: pedido.pago
data: {"id":"ped_42"}

: comentário serve de keep-alive

id: 2
event: entrega.a_caminho
data: {"minutos":35}
```

```javascript
const es = new EventSource('/eventos');
es.addEventListener('pedido.pago', e => console.log(JSON.parse(e.data)));
// Reconexão automática e retomada por Last-Event-ID vêm DE GRAÇA.
```

| A favor | Contra |
|---|---|
| **é HTTP comum** — atravessa proxy, CDN, autenticação | **só servidor → cliente** |
| **reconexão automática** no navegador | só texto UTF-8 |
| **retomada** via `Last-Event-ID` | limite de conexões por origem em HTTP/1.1 (some com HTTP/2) |
| trivial de implementar | menos conhecido que WebSocket |

> **SSE é o mais subestimado desta lista.** Para o caso mais comum — "o servidor precisa
> avisar o cliente" — ele é mais simples que WebSocket, reaproveita toda a infraestrutura
> HTTP e traz reconexão de graça. **É o mecanismo por trás do streaming de respostas de
> modelos de linguagem**, o que o tornou subitamente onipresente.

---

## 7. Webhooks

**A ideia:** inversão de controle — **o servidor chama você** quando algo acontece.

```http
POST https://seu-sistema.com/webhooks/pagamentos
Webhook-Id: 9f2a4b1c-...
Webhook-Timestamp: 1786553400
Webhook-Signature: v1,3a7f9c...
Content-Type: application/json

{"tipo": "pagamento.aprovado", "dados": {"id": "pag_42"}}
```

**O checklist de quem recebe** (implementação em [06-exemplos.md](06-exemplos.md) §10):

| Item | Por quê |
|---|---|
| Verificar **assinatura HMAC** | sua URL é pública; qualquer um pode postar nela |
| Assinar o **corpo bruto** | re-serializar muda a string e quebra a assinatura |
| **Timestamp na assinatura** + janela | senão uma requisição capturada é reutilizável para sempre |
| Comparação em **tempo constante** | `===` vaza a assinatura por *timing* |
| **Deduplicar** por id | entrega é *at-least-once*; duplicata é normal, não exceção |
| Responder **`2xx` rápido**, processar depois | se demorar, o emissor considera falha e reenvia |
| Tratar **fora de ordem** | não há garantia de ordem; use o `criado_em` do evento |

**O checklist de quem emite:**
- retentativa com backoff exponencial (ex.: 1 min, 5 min, 30 min, 2 h, 12 h);
- assinatura e timestamp;
- **id único por entrega**, estável entre retentativas;
- painel para o cliente ver as entregas e **reenviar manualmente**;
- desativar o endpoint após N falhas consecutivas, com aviso.

> **Padronização:** o esforço **Standard Webhooks** convergiu os nomes de cabeçalho
> (`webhook-id`, `webhook-timestamp`, `webhook-signature`). Antes, cada fornecedor inventava
> o seu. Se você emite webhooks, siga a convenção padrão.

---

## 8. Mensageria e arquitetura orientada a eventos

**A ideia:** produtores publicam em um **broker**; consumidores assinam. Ninguém conhece
ninguém.

| Tecnologia | Modelo | Forte em |
|---|---|---|
| **RabbitMQ** | filas, roteamento rico | roteamento complexo, prioridades |
| **Apache Kafka** | log particionado e persistente | alto volume, releitura do histórico |
| **NATS** | pub/sub leve | latência mínima, simplicidade |
| **Redis Streams** | log leve | quando você já tem Redis |
| **SQS / Pub-Sub / Event Grid** | gerenciado na nuvem | não operar infraestrutura |

**Fila vs. log — a distinção que decide a escolha:**

| | Fila (RabbitMQ, SQS) | Log (Kafka) |
|---|---|---|
| Consumiu, some? | **sim** | **não** — fica pelo período de retenção |
| Vários consumidores | competem pela mesma mensagem | **cada um lê tudo, no seu ritmo** |
| Reprocessar o passado | ❌ | ✅ **volta o offset e relê** |
| Ordem | por fila | **por partição** |

> A capacidade de **reler o histórico** é o que faz Kafka valer a complexidade. Se um
> consumidor tinha um bug, você corrige e reprocessa três meses de eventos. Com fila, os
> dados já foram.

**Comando vs. evento** — uma distinção de modelagem que muda o acoplamento:

```json
// COMANDO: um destinatário, imperativo, o emissor espera que aconteça
{"tipo": "EnviarEmailDeBoasVindas", "usuario_id": 42}

// EVENTO: fato consumado, no passado, o emissor não sabe quem escuta
{"tipo": "UsuarioCadastrado", "usuario_id": 42, "em": "2026-08-11T14:00:00Z"}
```

**Prefira eventos.** Um comando acopla o emissor ao que deve acontecer; um evento apenas
narra um fato. Quando um sexto consumidor precisar reagir a `UsuarioCadastrado`, ninguém
mexe no emissor.

---

## 9. Long polling — o que veio antes, e ainda aparece

O cliente faz `GET` e o **servidor segura a resposta** até haver novidade (ou até um timeout).

```text
Polling comum:  GET a cada 5s → 95% das respostas são "nada novo"
Long polling:   GET → servidor segura 30s → responde quando houver algo
```

**Ainda faz sentido quando:** você não pode usar SSE nem WebSocket (proxy hostil, cliente
muito antigo), ou os eventos são raríssimos. Fora isso, **SSE substitui com vantagem**.

---

## 10. MCP — Model Context Protocol

**A ideia:** padronizar como um agente de IA descobre e usa ferramentas e dados.

**O problema:** M modelos × N ferramentas = M×N integrações artesanais. É o mesmo problema
que ODBC resolveu para bancos e USB para periféricos.

**Como funciona, no essencial:** um **servidor MCP** expõe, sobre JSON-RPC:

| Primitiva | O que é |
|---|---|
| **Tools** | ações que o agente pode executar (com schema de entrada) |
| **Resources** | dados que o agente pode ler |
| **Prompts** | modelos de instrução reutilizáveis |

Cada uma vem com **descrição em linguagem natural** — porque quem lê é um modelo, não um
programador.

**O que MCP não é:**
- não substitui a sua API REST (na prática, **envolve** ela);
- não é um padrão de API de propósito geral;
- não é uma camada de orquestração.

**Estado em agosto de 2026:** adotado por Anthropic, OpenAI, Google e Microsoft; ecossistema
com dezenas de milhares de servidores publicados; a revisão de julho/2026 moveu a
arquitetura para **stateless**, aproximando-a do modelo da web — cacheável, roteável e
escalável horizontalmente.

> **O que isso significa para quem projeta APIs:** você passa a ter **dois públicos**.
> Programadores leem a documentação; agentes leem a **descrição da ferramenta**. Uma
> descrição vaga (`"processa dados"`) faz o agente usar a ferramenta errada. **Descrever bem
> virou requisito funcional**, não cortesia. Ver [65-estado-da-arte.md](65-estado-da-arte.md) §5.

---

## 11. Comparação resumida

| | REST | RPC | gRPC | GraphQL | SOAP | WebSocket | SSE | Webhook | Fila | MCP |
|---|---|---|---|---|---|---|---|---|---|---|
| Transporte | HTTP | HTTP | HTTP/2 | HTTP | HTTP+ | TCP | HTTP | HTTP | broker | JSON-RPC |
| Formato | JSON | JSON | binário | JSON | XML | livre | texto | JSON | livre | JSON |
| Direção | C→S | C→S | ambos | C→S | C→S | ambos | S→C | S→C | assín. | ambos |
| Cache HTTP | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | — | — | ❌ |
| Contrato obrigatório | ❌ | ❌ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ✅ |
| Streaming | limitado | ❌ | ✅ | parcial | ❌ | ✅ | ✅ | — | ✅ | ✅ |
| Navegador | ✅ | ✅ | ⚠️ | ✅ | ⚠️ | ✅ | ✅ | — | ❌ | — |
| Legível | ✅ | ✅ | ❌ | ✅ | ⚠️ | varia | ✅ | ✅ | varia | ✅ |
| Curva | baixa | baixa | média | média | alta | média | **baixa** | baixa | alta | média |

O fluxograma de decisão está em [19-como-escolher.md](19-como-escolher.md).

---

## 12. Os cinco porquês: por que tantos estilos coexistem?

**1. Por que não há um estilo vencedor?**
Porque os requisitos são genuinamente conflitantes: eficiência **contra** legibilidade;
flexibilidade do cliente **contra** cacheabilidade; contrato rígido **contra** facilidade de
começar.

**2. Por que esses conflitos não se resolvem com engenharia?**
Porque são **trade-offs**, não problemas. Um formato binário é sempre menos legível que um
textual — isso não é limitação de implementação, é a definição de binário.

**3. Então por que se fala em "REST vs. GraphQL" como se um fosse vencer?**
Porque discurso de tecnologia é vendido em modas, e moda precisa de vencedor. Também porque
a maioria dos artigos compara os dois **fora de contexto** — e fora de contexto qualquer
comparação é vazia.

**4. Como escolher, então?**
Pelo **contexto**, em quatro perguntas: quem consome (navegador? serviço interno? parceiro
externo? agente?), qual o volume, o que precisa acontecer em tempo real, e qual a
maturidade operacional do time. As mesmas quatro perguntas de
[19-como-escolher.md](19-como-escolher.md).

**5. E se eu escolher errado?**
Aqui está a boa notícia, e o conselho mais útil deste arquivo: **você pode ter mais de um**.
gRPC por dentro e REST na borda. REST para CRUD e SSE para tempo real. Webhook **e** polling
como alternativa. Adaptadores são baratos comparados a reescrever o domínio. **O erro caro
não é escolher o protocolo errado — é acoplar a sua regra de negócio a ele.** Mantenha o
domínio independente do transporte, e a escolha vira reversível.

*(Parada legítima: trade-offs irredutíveis, declarados como tais.)*

---

## Autoteste

1. Quando RPC é mais honesto que REST? Dê três exemplos de domínio.
2. Que problema o WS-Security resolve que o TLS não resolve?
3. Quais são os quatro modos de streaming do gRPC? Por que o número do campo é o contrato?
4. Cite os seis problemas que GraphQL cria. Qual deles exige DataLoader?
5. Compare SSE e WebSocket em cinco dimensões. Quando escolher cada um?
6. Liste sete itens do checklist de quem recebe webhook, com o motivo de cada um.
7. Qual a diferença entre fila e log? Que capacidade justifica a complexidade do Kafka?
8. Qual a diferença entre comando e evento? Por que preferir eventos?
9. O que é MCP, que problema resolve, e por que ele não substitui a sua API REST?
10. Por que tantos estilos coexistem? Qual é o erro caro — escolher errado ou outra coisa?
