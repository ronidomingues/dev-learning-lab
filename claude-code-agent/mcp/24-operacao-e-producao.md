# 24 · Operação e produção — do laptop ao serviço

`Nível: avançado` · `Escrito em 01/09/2026` · `Protocolo 2026-07-28`

---

## 1. O que muda ao sair do laptop

| | Desenvolvimento | Produção |
|---|---|---|
| Transporte | stdio | Streamable HTTP |
| Usuários | um | muitos |
| Estado | variável do processo | armazenamento externo com handle explícito |
| Credencial | variável de ambiente | OAuth, com audiência validada |
| Falha | você vê no terminal | precisa ser detectada |
| Deploy | `Ctrl+C` e roda de novo | sem derrubar quem está usando |
| Custo | zero | tokens, infraestrutura, chamadas de API |

A boa notícia da revisão `2026-07-28`: como o protocolo é **sem estado**, um servidor MCP
remoto é **um serviço HTTP comum**. Sem afinidade de sessão, sem conexão longa
obrigatória, escala horizontal normal, deploy azul-verde normal. Foi exatamente esse o
objetivo da reescrita.

---

## 2. Empacotamento

### 2.1 Monte dentro da aplicação que você já tem

O caminho mais sensato para quem já tem uma API em produção: você herda autenticação,
log, métricas, deploy e alertas.

```python
from starlette.applications import Starlette
from starlette.routing import Mount

app_mcp = server.streamable_http_app()      # ASGI

app = Starlette(routes=[
    Mount("/mcp", app=app_mcp),
    # ... as suas rotas de sempre
])
```

Em TypeScript, o equivalente é `createMcpHandler` (ou
`WebStandardStreamableHTTPServerTransport` para Workers, Deno e Bun).

Rota de saúde no mesmo processo:

```python
@server.custom_route("/saude", methods=["GET"])
async def saude(request):
    from starlette.responses import JSONResponse
    return JSONResponse({"ok": True})
```

> **Melhor ainda:** use `server/discover` como sonda de saúde. Uma requisição diz versão,
> capacidades e identidade, e exercita o caminho real — não só "o processo está vivo".

### 2.2 Container

```dockerfile
FROM python:3.12-slim

# uv: instalação reprodutível a partir do lockfile
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev     # falha se o lock estiver desatualizado

COPY . .

# Usuário sem privilégio: o servidor executa o que o modelo pediu.
RUN useradd --create-home app && chown -R app:app /app
USER app

EXPOSE 8000
CMD ["uv", "run", "python", "servidor.py", "--http"]
```

Três decisões: `--frozen` para o build falhar em vez de resolver dependências de novo;
usuário sem privilégio, porque o servidor executa a pedido de um modelo; `--no-dev` para
não levar pytest para produção.

---

## 3. Configuração

Tudo por variável de ambiente — é o que o host passa em `env`, e é o que orquestradores
injetam.

| Variável | Para quê |
|---|---|
| `PORT`, `HOST` | onde escutar. Local: **`127.0.0.1`**. Em container: `0.0.0.0`, com a rede restrita por fora |
| `LOG_LEVEL` | verbosidade |
| credenciais | `DATABASE_URL`, `API_KEY` etc. |
| `MAX_LINHAS`, `TIMEOUT_S`, `RATE_LIMIT` | os tetos, ajustáveis sem redeploy |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | telemetria |

**Segredo nunca em `args`** (aparece em `ps aux` e nos logs do host) e nunca em imagem de
container.

---

## 4. Observabilidade

### 4.1 Log

Em stdio, `stderr`. Em HTTP, a saída padrão do seu serviço.

O que registrar em **toda** chamada de ferramenta:

```json
{
  "ts": "2026-09-01T16:16:21Z",
  "evento": "tools/call",
  "ferramenta": "emprestar_livro",
  "cliente": {"nome": "claude-code", "versao": "2.1.252"},
  "protocolo": "2026-07-28",
  "principal": "sub-do-token-verificado",
  "request_id": "abc123",
  "traceparent": "00-0af7651916cd43dd8448eb211c80319c-00f067aa0ba902b7-01",
  "argumentos": {"isbn": "9788535902778", "leitor": "Ana"},
  "duracao_ms": 42,
  "is_error": false
}
```

Regras:

- **argumentos sim, resultado não** (ou só o tamanho). Resultado pode ter dado pessoal e
  é enorme;
- **o principal vem do token verificado**, nunca do `clientInfo`, que é autodeclarado;
- **redija segredo** antes de registrar;
- **um `request_id`** para correlacionar com o cliente.

No SDK Python: `ctx.request_id`, `ctx.headers`, `ctx.protocol_version`,
`ctx.client_capabilities`.

### 4.2 Trace com OpenTelemetry

A revisão `2026-07-28` documenta a propagação de contexto de trace em `_meta`, com as
chaves `traceparent`, `tracestate` e `baggage` seguindo W3C Trace Context/Baggage — a
**exceção explícita** à regra de prefixo de `_meta`, para casar com as convenções
semânticas de OpenTelemetry para MCP.

Isso permite um trace único atravessando: host → cliente → servidor MCP → banco/API.
É a diferença entre "está lento" e "está lento **naquela** consulta".

### 4.3 Métricas que valem

| Métrica | Por quê |
|---|---|
| chamadas por ferramenta | quais existem de verdade; quais podem ser removidas |
| latência p50/p95/p99 por ferramenta | p99 alto trava a conversa do usuário |
| taxa de `isError` por ferramenta | erro alto = **descrição ou schema ruins**, não bug |
| **tamanho do resultado** (p95) | o custo de contexto que você está impondo |
| chamadas por principal | abuso, laço do modelo, cota |
| rodadas de MRTR por chamada | número alto = elicitação mal projetada |
| falhas de validação de audiência | **sinal precoce de reuso de token** |
| `tools/list` por hora | cliente repolando? configure `ttlMs` |

> A métrica mais subestimada é o **tamanho do resultado**. Ela é a que se traduz
> diretamente em conta de tokens do usuário.

---

## 5. Limites

### 5.1 Limite de taxa

Necessário porque **o modelo entra em laço**. Não é hipótese: é o comportamento normal
quando a mensagem de erro não instrui.

Dimensões, na ordem de utilidade: por principal; por ferramenta (a cara custa menos
chamadas); e global, como rede de proteção.

E a mensagem precisa orientar:

```python
raise ToolError(
    f"Limite de {LIMITE} consultas por minuto atingido. "
    f"Aguarde alguns segundos antes de tentar de novo."
)
```

### 5.2 Timeout

Duas pontas, e as duas são obrigatórias:

- **do lado do servidor**, para a operação (consulta, chamada externa). Sem isso a
  requisição fica pendurada;
- **do lado do cliente**, por chamada (`read_timeout_seconds`).

```python
r = httpx.get(url, timeout=5.0)   # httpx sem timeout espera para SEMPRE
```

Operação que passa de poucos segundos deveria ser **Tasks** ([22](22-extensoes.md)), não
uma requisição bloqueante — clientes e intermediários impõem timeouts próprios.

### 5.3 Tamanho

Teto de linhas, teto de bytes, e **truncamento avisado no texto**.

---

## 6. Cache

`ttlMs` e `cacheScope` são **obrigatórios** nos resultados de `tools/list`,
`prompts/list`, `resources/list`, `resources/read` e `resources/templates/list`.

| Campo | Valores | Significado |
|---|---|---|
| `ttlMs` | milissegundos | por quanto tempo o cliente pode cachear. `0` = não cacheie |
| `cacheScope` | `"public"` / `"private"` | se intermediário compartilhado pode cachear |

Escolhendo:

| Situação | `ttlMs` | `cacheScope` |
|---|---|---|
| lista de ferramentas fixa, igual para todos | 300000 (5 min) ou mais | `"public"` |
| lista que varia por autorização | curto | **`"private"`** |
| conteúdo de recurso que muda | curto, ou 0 | `"private"` |

⚠️ **A armadilha:** se a lista varia com o token do chamador, `cacheScope` **tem** de ser
`"private"`. Caso contrário, um intermediário compartilhado pode servir a lista de um
usuário a outro.

O SDK Python 2.1.1 devolve `ttlMs: 0` e `cacheScope: "private"` por padrão — conservador
e correto, mas você paga em viagens. Configure `cache_hints` no `MCPServer`.

Cache **complementa** `listChanged`, não substitui: o TTL reduz polling, a notificação
avisa de mudança.

---

## 7. Deploy e versionamento

### 7.1 O que quebra o cliente

| Mudança | Quebra? |
|---|---|
| acrescentar ferramenta | não |
| acrescentar parâmetro **opcional** | não |
| melhorar descrição | não (pode mudar o comportamento do modelo — teste) |
| **renomear ferramenta** | **sim** |
| **acrescentar parâmetro obrigatório** | **sim** |
| **remover ferramenta** | **sim** |
| **estreitar tipo** (`str` → `enum`) | **sim**, se o modelo já mandava outro valor |
| mudar o formato do retorno | **sim**, se o cliente valida contra `outputSchema` |

### 7.2 Como mudar sem quebrar

```python
@server.tool(name="buscar_pedido")            # nome antigo, mantido
def buscar_pedido_legado(id: str) -> Pedido:
    """OBSOLETA: use `buscar_pedido_por_id`. Será removida em 01/03/2027."""
    return buscar_pedido_por_id(pedido_id=id)
```

Deprecie na **descrição** (é o que o modelo lê), mantenha por uma janela declarada, e
meça o uso antes de remover. É a mesma política de doze meses que o próprio MCP adotou.

### 7.3 Sem estado = deploy comum

Sem sessão, uma réplica pode sair do ar no meio do uso: as requisições em voo se perdem e
o cliente reemite. Rolling update, azul-verde e canário funcionam como em qualquer serviço
HTTP. **Este é o retorno prático da reescrita de 2026.**

Uma ressalva: se você guarda estado sob handle, ele precisa estar em armazenamento
**compartilhado** entre réplicas (Redis, banco). Um `dict` na memória de uma réplica não
é o `dict` da outra — e é o bug número um de quem migra do laptop.

---

## 8. Custo

O que gera conta, em ordem:

1. **Tokens do catálogo**, em **toda** requisição ao modelo. Trinta ferramentas com
   descrições longas custam em cada mensagem da conversa. É o custo mais invisível.
2. **Tokens dos resultados.** Um `SELECT *` custa mais que a infraestrutura do mês.
3. **Chamadas de API a jusante**, se você envolve serviço pago.
4. **Infraestrutura** do servidor remoto — quase sempre a menor parcela.

Como reduzir, na ordem de retorno:

- **menos ferramentas**, com descrições enxutas;
- **paginação agressiva** e resumos;
- **`resource_link`** em vez de embutir conteúdo;
- **cache com `ttlMs`** para o cliente não repolar;
- **ordem determinística**, que melhora o acerto do cache de prompt do LLM.

Ver [80 · Custos e licenças](80-custos-e-licencas.md).

---

## 9. Falhas comuns em produção

| Sintoma | Causa provável | Correção |
|---|---|---|
| funciona local, falha em container | estado em memória, com várias réplicas | mover para armazenamento compartilhado |
| SSE chega em lote | proxy bufferizando | `X-Accel-Buffering: no` |
| `403` inesperado | validação de `Origin` | ajustar a allowlist de origens |
| `-32020` | balanceador reescrevendo cabeçalho `Mcp-*` | não reescrever; ou revalidar |
| `401` intermitente | token expirando sem *refresh* | implementar refresh, ou vida útil maior |
| custo explodindo | resultado grande, ou catálogo grande | métrica de tamanho de resultado |
| modelo em laço na mesma ferramenta | mensagem de erro sem instrução | reescrever a mensagem |
| latência p99 péssima | sem timeout na chamada externa | timeout, e Tasks para operação longa |
| servidor cai sem log | escreveu em `stdout` (stdio) | log em `stderr` |
| `tools/list` a cada segundo | `ttlMs: 0` | configurar dicas de cache |

---

## 10. Antes de ir para produção

**Funcional**
- [ ] roda em container, com usuário sem privilégio
- [ ] configuração por ambiente; **nada** de segredo em `args` ou na imagem
- [ ] estado sob handle, em armazenamento **compartilhado**
- [ ] rota de saúde **e** `server/discover` respondendo

**Segurança**
- [ ] `Origin` validado (403); TLS obrigatório
- [ ] **audiência do token validada**; **nenhum** repasse de token
- [ ] `requestState` com HMAC/AEAD, com principal, TTL e id da requisição
- [ ] escopos mínimos; elevação por desafio
- [ ] SQL parametrizado; caminho de arquivo sanitizado
- [ ] handles opacos, com expiração, ligados ao usuário autenticado

**Limites**
- [ ] limite de taxa por principal e por ferramenta
- [ ] timeout de servidor em toda operação externa
- [ ] teto de linhas/bytes, com truncamento avisado
- [ ] Tasks para o que passa de poucos segundos

**Observabilidade**
- [ ] log estruturado de toda chamada, com principal e argumentos redigidos
- [ ] trace com `traceparent` propagado
- [ ] métricas: latência, `isError`, **tamanho de resultado**, chamadas por principal
- [ ] alerta em falha de validação de audiência

**Operação**
- [ ] `ttlMs`/`cacheScope` conscientes (e `private` quando varia por token)
- [ ] ordem determinística em todo resultado
- [ ] política de depreciação declarada nas descrições
- [ ] runbook: **como você desconecta este servidor às pressas?**

---

## 11. Autoteste

1. Por que a revisão `2026-07-28` tornou o deploy de servidor MCP um deploy comum?
2. Qual é a maneira mais sensata de expor MCP em quem já tem uma API? O que se herda?
3. Por que rodar o servidor com usuário sem privilégio, mesmo em container?
4. O que registrar em cada chamada — e o que **não** registrar, e por quê?
5. De onde vem o "principal" no log? Por que não do `clientInfo`?
6. Qual é a métrica mais subestimada, e em que ela se traduz?
7. Quando `cacheScope` **tem** de ser `"private"`? O que acontece se você errar?
8. Cite três mudanças que quebram o cliente e três que não quebram.
9. Qual é o bug número um de quem migra do laptop para várias réplicas?
10. Liste os quatro custos de um servidor MCP em produção, em ordem de peso.

---

**Anterior:** [23 · Projeto de ferramentas](23-projeto-de-ferramentas.md) · **Próximo:** [60 · Teoria avançada](60-teoria-avancada.md) · **Índice:** [00-MAPA](00-MAPA.md)

*Fontes: [Changelog 2026-07-28](https://modelcontextprotocol.io/specification/2026-07-28/changelog)
(cache, OpenTelemetry, statelessness), [Streamable HTTP](https://modelcontextprotocol.io/specification/2026-07-28/basic/transports/streamable-http),
[Tasks](https://modelcontextprotocol.io/extensions/tasks/overview),
[Convenções semânticas de OpenTelemetry para MCP](https://opentelemetry.io/docs/specs/semconv/gen-ai/mcp/).
Padrões de `ttlMs`/`cacheScope` do SDK medidos nesta máquina (`mcp` 2.1.1) em 01/09/2026.
As recomendações operacionais são opinião profissional, declarada como tal.*
