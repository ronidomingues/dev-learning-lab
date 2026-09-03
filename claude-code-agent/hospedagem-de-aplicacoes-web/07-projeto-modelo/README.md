# 07 · Projeto-modelo — **EncurtaLink**

`Nível: intermediário` · `Atualizado em 18/08/2026`

Uma aplicação **pequena, porém inteira**, que exercita exatamente as quatro peças do curso:

```
┌───────────────┐    HTTP     ┌──────────────────┐
│   frontend    │ ──────────► │     backend      │
│ public/*.html │             │  Node 22+, HTTP  │
└───────────────┘             └────┬────────┬────┘
                                   │        │
                     ┌─────────────▼──┐  ┌──▼───────────────┐
                     │  PostgreSQL 18 │  │ Redis / Valkey 9 │
                     │  (durável)     │  │ (cache + limite) │
                     └────────────────┘  └──────────────────┘
```

**O que ela faz:** encurta URLs. Cria um apelido curto, redireciona, conta cliques e mostra um
ranking. Simples de entender, e mesmo assim obriga a resolver **todos** os problemas reais de
uma aplicação hospedada: cache, limite de taxa, migração de esquema, health check, encerramento
gracioso, validação de entrada, segredos, log estruturado e deploy.

---

## Começando em 30 segundos (sem instalar nada além do Node)

```bash
cd hospedagem-de-aplicacoes-web/07-projeto-modelo
node src/server.js
```

```
{"nivel":"aviso","msg":"sem DATABASE_URL: rodando em MODO MEMÓRIA. Os dados somem ao reiniciar."}
{"nivel":"info","msg":"ouvindo em 0.0.0.0:3000","modo":"memoria+memoria"}
```

Abra `http://localhost:3000`. **Funciona sem PostgreSQL, sem Redis, sem Docker e sem
`npm install`.**

> **Como isso é possível — e por que importa.** O sistema fala com dois *contratos*
> (`repositorio` e `cache`), não com bibliotecas. Existem dois adaptadores de cada:
> um em memória e um real. Trocar é uma variável de ambiente. É o padrão **porta e
> adaptador** (ou "arquitetura hexagonal"), e o benefício prático aparece já aqui: os
> **40 testes rodam em 0,3 segundo, sem infraestrutura nenhuma**.

---

## Rodando de verdade, com PostgreSQL e Redis

### Opção A — Docker Compose (recomendado)

```bash
docker compose up --build -d
docker compose exec api npm run migrate
curl -s localhost:3000/health
# esperado: {"ok":true,"banco":"up","cache":"up","modo":"postgres+redis"}
```

```bash
docker compose logs -f api      # acompanhar
docker compose down             # parar, mantendo os dados
docker compose down -v          # parar e APAGAR os dados
```

### Opção B — serviços na nuvem, aplicação local

```bash
npm install
export DATABASE_URL="postgresql://usuario:senha@ep-xxx.sa-east-1.aws.neon.tech/neondb?sslmode=require"
export REDIS_URL="rediss://default:TOKEN@xxx.upstash.io:6379"
export BASE_URL="http://localhost:3000"
npm run migrate
npm start
```

### Verificação funcional completa

```bash
# 1) saúde
curl -s localhost:3000/health | jq
# esperado: {"ok": true, "banco": "up", "cache": "up", "modo": "postgres+redis"}

# 2) criar um link
curl -s -X POST localhost:3000/api/links \
  -H 'content-type: application/json' \
  -d '{"destino":"https://www.postgresql.org/docs/"}' | jq
# esperado: {"slug":"aB3xY7q","destino":"...","url_curta":"http://localhost:3000/aB3xY7q",...}

# 3) redirecionar (-I mostra só os cabeçalhos)
curl -sI localhost:3000/aB3xY7q | head -3
# esperado: HTTP/1.1 302 Found
#           location: https://www.postgresql.org/docs/

# 4) ranking — repare no campo "fonte" mudando de "banco" para "cache"
curl -s localhost:3000/api/stats | jq .fonte    # "banco"
curl -s localhost:3000/api/stats | jq .fonte    # "cache"

# 5) apelido em uso
curl -s -X POST localhost:3000/api/links -H 'content-type: application/json' \
  -d '{"destino":"https://exemplo.com","slug":"minhaPagina"}' >/dev/null
curl -s -X POST localhost:3000/api/links -H 'content-type: application/json' \
  -d '{"destino":"https://outro.com","slug":"minhaPagina"}' | jq
# esperado: {"erro":"o apelido \"minhaPagina\" já existe","codigo":"slug_em_uso"}  (HTTP 409)

# 6) limite de taxa (o 21º POST em 60 s do mesmo IP)
for i in $(seq 1 21); do
  curl -s -o /dev/null -w "%{http_code} " -X POST localhost:3000/api/links \
    -H 'content-type: application/json' -d "{\"destino\":\"https://exemplo.com/$i\"}"
done; echo
# esperado: 201 repetido 20 vezes e depois 429
```

---

## Testes

```bash
npm test
```

Saída real, medida em 18/08/2026 (Node v24.18.0, Ubuntu 22.04.5):

```
ℹ tests 40
ℹ suites 1
ℹ pass 40
ℹ fail 0
ℹ duration_ms 269.6
```

Os testes de integração (PostgreSQL e Redis reais) ficam **pulados** por padrão. Para rodá-los:

```bash
docker compose up -d db cache
DATABASE_URL=postgresql://app:dev_senha_local@localhost:5432/app \
REDIS_URL=redis://localhost:6379 \
npm run migrate && npm run test:integracao
```

---

## Estrutura de pastas, comentada

```
07-projeto-modelo/
├── src/
│   ├── config.js               lê e VALIDA o ambiente. Falha na partida, não na 1ª requisição
│   ├── erros.js                erros de domínio com código estável (o HTTP traduz o código)
│   ├── ids.js                  geração de slug com CSPRNG e alfabeto sem 0/O/1/l/I
│   ├── validate.js             validação de URL e de apelido, com bloqueio de SSRF
│   ├── servico.js              TODA a regra de negócio. Não conhece HTTP, SQL nem Redis
│   ├── app.js                  roteamento HTTP, tradução de erro, log, CORS, limite de corpo
│   ├── server.js               composição: escolhe adaptadores, sobe, encerra com elegância
│   ├── migrate.js              migrador mínimo: tabela de controle + arquivos + transação
│   ├── repositorio-pg.js       adaptador PostgreSQL (pool, consulta parametrizada, erro 23505)
│   ├── repositorio-memoria.js  adaptador em memória — mesmo contrato
│   ├── cache-redis.js          adaptador Redis/Valkey/Upstash
│   └── cache-memoria.js        adaptador em memória com relógio injetável (testa TTL sem sleep)
├── sql/001_init.sql            esquema, com o porquê de cada tipo e cada índice
├── public/index.html           frontend inteiro: um arquivo, zero dependências, zero build
├── tests/                      40 testes (ids, validate, cache, serviço, API) + integração
├── Dockerfile                  multi-stage, usuário sem privilégio, dumb-init, healthcheck
├── compose.yaml                API + Postgres 18 + Valkey 9, com healthcheck e depends_on
├── render.yaml                 Blueprint do Render: web + keyvalue + database
├── fly.toml                    Fly.io na região gru (São Paulo), escala a zero
├── .github/workflows/ci.yml    CI: testes unitários + migração + integração com serviços
├── .env.example                todas as variáveis, documentadas, sem nenhum valor real
└── .dockerignore               impede .env, testes e .git de entrarem na imagem
```

---

## O que cada decisão de projeto ensina

| Decisão | O que ela ensina |
|---|---|
| **Dois adaptadores por dependência** | Testar sem infraestrutura, e trocar de fornecedor sem reescrever a aplicação. É a defesa concreta contra aprisionamento |
| **Serviço sem HTTP, SQL ou Redis** | Onde a regra de negócio deve morar. Trocar Express por Fastify não deveria tocar em uma linha de regra |
| **`302`, não `301`, no redirecionamento** | `301` é cacheado pelo navegador quase para sempre: você perde a métrica e a capacidade de mudar o destino |
| **Contagem de clique fora do caminho da resposta** | Latência do usuário > precisão da métrica. Um trade-off consciente e declarado |
| **Cache-aside com TTL curto** | Invalidação correta é difícil; TTL curto é simples e resolve 95% dos casos |
| **`UNIQUE` no banco decide a colisão** | Verificar-e-depois-inserir é uma condição de corrida. A fonte da verdade é a restrição |
| **Limite de taxa antes da validação** | Proteger a cota gratuita e o banco antes de gastar CPU com entrada hostil |
| **Bloqueio de SSRF na validação** | Um encurtador ingênuo vira um proxy para atacar `169.254.169.254` (metadados da nuvem) |
| **Limite de 16 KB no corpo** | Sem limite, um POST grande derruba o processo — DoS trivial |
| **Health check que consulta as dependências** | Um `200 OK` que mente faz a plataforma mandar tráfego para um serviço quebrado |
| **Cache fora = degradado; banco fora = indisponível** | Nem toda dependência é crítica. Marcar tudo como crítico derruba o site por causa do cache |
| **`SIGTERM` com prazo** | Todo deploy manda `SIGTERM`. Sem tratar, requisições em andamento morrem no meio |
| **Log em JSON, uma linha por requisição** | Qualquer coletor entende, sem parser próprio; e você consegue filtrar por status e latência |
| **Erro interno não vaza `stack`** | Stack trace na resposta é o mapa da casa entregue ao atacante |
| **`USER node` no Dockerfile** | Container como root é o achado nº 1 de auditoria. Custa uma linha |
| **Migração em transação, com tabela de controle** | O mecanismo que toda ferramenta séria usa, sem mágica |
| **`.env` no `.dockerignore` e no `.gitignore`** | O vazamento de segredo nº 1 é o segredo que entrou na imagem ou no repositório |

---

## Endpoints

| Método | Rota | O que faz | Códigos |
|---|---|---|---|
| `GET` | `/` | serve o frontend | 200 |
| `GET` | `/health` | saúde com estado das dependências | 200, 503 |
| `POST` | `/api/links` | cria link `{destino, slug?}` | 201, 400, 409, 413, 429 |
| `GET` | `/api/links/:slug` | detalhe com contagem de cliques | 200, 404 |
| `GET` | `/api/stats` | 10 mais clicados (cache de 10 s) | 200 |
| `GET` | `/:slug` | redireciona | 302, 404 |

---

## Variáveis de ambiente

| Variável | Obrigatória | Padrão | Efeito |
|---|---|---|---|
| `DATABASE_URL` | não | — | ausente ⇒ **modo memória** (dados somem ao reiniciar) |
| `REDIS_URL` | não | — | ausente ⇒ cache local ao processo |
| `PORT` | não | `3000` | a plataforma sobrescreve |
| `BASE_URL` | não | `http://localhost:$PORT` | monta a `url_curta` devolvida |
| `RATE_LIMITE` | não | `20` | criações por janela, por IP |
| `RATE_JANELA_MS` | não | `60000` | tamanho da janela |
| `CORS_ORIGEM` | não | — | origem permitida quando o frontend está noutro domínio |
| `NODE_ENV` | não | `development` | — |

---

## Publicando

| Plataforma | Comando |
|---|---|
| **Render** | commit do `render.yaml` → painel → *New → Blueprint* |
| **Fly.io** | `flyctl launch --copy-config` → `flyctl secrets set DATABASE_URL=... REDIS_URL=...` → `flyctl deploy` |
| **Railway** | `railway init` → `railway add` (Postgres e Redis) → `railway up` |
| **Koyeb / Northflank** | apontar para o `Dockerfile` no painel |
| **VPS com Coolify** | conectar o repositório; o Coolify detecta o `compose.yaml` |

Depois de publicar, **defina `BASE_URL` com a URL pública** — sem isso a `url_curta`
devolvida aponta para `localhost`.

---

## O que foi executado e o que não foi — declaração honesta

**Executado nesta máquina (Ubuntu 22.04.5, Node v24.18.0), em 18/08/2026:**

- `npm test` → **40 testes, 40 aprovados**, 0,27 s, sem nenhuma dependência instalada.
- `node src/server.js` em modo memória → servidor no ar, `/health`, `POST /api/links` e
  `/api/stats` conferidos por `curl`, `SIGTERM` encerrando com elegância.
- Sintaxe de todos os módulos verificada com `node --check`.

**Não executado (declarado, não fingido):**

- `docker compose up` e o `Dockerfile`: **o daemon do Docker não estava acessível** no
  ambiente de escrita (`permission denied ... /var/run/docker.sock`). A configuração segue as
  práticas documentadas em [`06-exemplos.md`](../06-exemplos.md), exemplos 8 e 9, mas **não
  foi construída aqui**.
- Os testes de integração contra PostgreSQL e Redis reais (dependem do Docker acima).
- Deploy real em Render, Fly.io, Railway, Koyeb ou Northflank. Os manifestos
  (`render.yaml`, `fly.toml`) seguem o esquema documentado de cada plataforma em 18/08/2026,
  **e devem ser validados** com `render blueprints validate` e `flyctl config validate` antes
  do primeiro uso.

**Ao rodar num ambiente com Docker, comece por:**

```bash
docker compose config       # valida o compose.yaml sem subir nada
docker build -t encurtalink .
docker compose up -d && docker compose exec api npm run migrate && npm run test:integracao
```

---

## Exercícios (aumentam de dificuldade)

1. Acrescente `GET /api/links/:slug/qr` devolvendo um QR code SVG do link curto.
2. Faça o `slug` aceitar expiração (`expira_em`) e o redirecionamento devolver `410 Gone`
   depois do prazo. Lembre-se de migrar o esquema com um arquivo novo em `sql/`.
3. Troque o limitador de janela fixa por janela deslizante ([`06-exemplos.md`](../06-exemplos.md),
   exemplo 4) e explique, por escrito, qual problema da janela fixa isso resolve.
4. Acrescente um `repositorio-sqlite.js` e faça os testes passarem com ele — sem tocar em
   `servico.js`. Se você precisou tocar, o acoplamento estava errado.
5. Descarregue a contagem de cliques para o Redis (`INCR`) e grave no PostgreSQL em lote a
   cada 30 segundos. Meça a diferença em requisições por segundo com `autocannon`
   ([`06-exemplos.md`](../06-exemplos.md), exemplo 14).

---

## Autoteste

1. Por que o projeto tem dois adaptadores para cada dependência, e o que isso viabiliza?
2. Por que o redirecionamento usa `302` e não `301`?
3. Por que a colisão de slug é detectada pelo banco e não por uma consulta prévia?
4. O que acontece se você publicar sem definir `BASE_URL`?
5. Por que o health check considera "cache fora" diferente de "banco fora"?
6. Qual parte deste projeto **não** foi executada durante a escrita, e por quê?
