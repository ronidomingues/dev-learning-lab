# 06 · Exemplos — 14 receitas completas

`Nível: iniciante a avançado` · `Atualizado em 18/08/2026`

Todo código aqui é **completo e executável**. Nada de `...` escondendo o essencial.
Cada exemplo segue: **problema → solução → explicação**.

| # | Exemplo | Nível |
|---|---|---|
| 1 | [Health check que verifica de verdade](#1-health-check-que-verifica-de-verdade) | iniciante |
| 2 | [Cache-aside com TTL](#2-cache-aside-com-ttl) | iniciante |
| 3 | [Proteção contra estampida de cache](#3-proteção-contra-estampida-de-cache) | intermediário |
| 4 | [Limitação de taxa (rate limit) com Redis](#4-limitação-de-taxa-rate-limit-com-redis) | intermediário |
| 5 | [Sessão em Redis, não na memória do processo](#5-sessão-em-redis-não-na-memória-do-processo) | intermediário |
| 6 | [Fila de trabalho com Redis Streams](#6-fila-de-trabalho-com-redis-streams) | avançado |
| 7 | [Migração de banco versionada](#7-migração-de-banco-versionada) | intermediário |
| 8 | [Dockerfile de produção para Node](#8-dockerfile-de-produção-para-node) | intermediário |
| 9 | [`compose.yaml` local com Postgres e Valkey](#9-composeyaml-local-com-postgres-e-valkey) | iniciante |
| 10 | [`render.yaml` — pilha inteira em um arquivo](#10-renderyaml--pilha-inteira-em-um-arquivo) | intermediário |
| 11 | [`fly.toml` com região São Paulo](#11-flytoml-com-região-são-paulo) | intermediário |
| 12 | [Backup automático e gratuito no GitHub Actions](#12-backup-automático-e-gratuito-no-github-actions) | intermediário |
| 13 | [Backend no Cloudflare Workers falando com PostgreSQL](#13-backend-no-cloudflare-workers-falando-com-postgresql) | avançado |
| 14 | [Teste de carga e leitura do resultado](#14-teste-de-carga-e-leitura-do-resultado) | avançado |

Os exemplos **2, 3, 4, 6, 12 e 14** são casos reais de produção, não didáticos.

---

## 1. Health check que verifica de verdade

**Problema.** Toda plataforma usa um endpoint de saúde para decidir se manda tráfego para a
sua instância. Um health check que só devolve `200 OK` mente: o processo está vivo, mas o
banco pode estar fora, e a plataforma vai continuar mandando usuários para um serviço quebrado.

**Solução.**

```js
// health.js — Node 22+, sem framework
import pg from "pg";
import Redis from "ioredis";

const db = new pg.Pool({ connectionString: process.env.DATABASE_URL, max: 3 });
const kv = new Redis(process.env.REDIS_URL, { maxRetriesPerRequest: 1 });

// Timeout é obrigatório: um health check que trava é pior que um que falha,
// porque a plataforma fica esperando e nenhuma decisão é tomada.
const comPrazo = (promessa, ms, nome) =>
  Promise.race([
    promessa,
    new Promise((_, rej) => setTimeout(() => rej(new Error(`${nome}: timeout ${ms}ms`)), ms)),
  ]);

export async function health() {
  const checagens = {
    db:    comPrazo(db.query("SELECT 1"), 1500, "postgres"),
    cache: comPrazo(kv.ping(),            800,  "redis"),
  };

  const resultados = await Promise.allSettled(Object.values(checagens));
  const nomes = Object.keys(checagens);

  const detalhe = {};
  let saudavel = true;
  resultados.forEach((r, i) => {
    detalhe[nomes[i]] = r.status === "fulfilled" ? "up" : `down: ${r.reason.message}`;
    // Regra de negócio: banco fora = não saudável. Cache fora = degradado, mas serve.
    if (r.status === "rejected" && nomes[i] === "db") saudavel = false;
  });

  return { status: saudavel ? 200 : 503, corpo: { ok: saudavel, ...detalhe } };
}
```

**Explicação.**

- **`Promise.allSettled`, não `all`**: você quer o estado de *todas* as dependências, não
  parar na primeira que falhar.
- **Timeout por dependência**: sem ele, um banco lento faz o health check estourar o limite
  da plataforma, que declara a instância morta e a reinicia — e a reinicialização não conserta
  o banco. É um laço de reinício em massa; já derrubou serviços inteiros.
- **Nem toda dependência é crítica.** Aqui, Redis fora significa "degradado, mas responde".
  Se você marcar tudo como crítico, uma falha no cache derruba o site inteiro.
- **Dois endpoints são melhores que um:** `/health/live` (o processo respira? só devolve 200)
  e `/health/ready` (posso receber tráfego? checa dependências). É o vocabulário do
  Kubernetes — *liveness* e *readiness* — e faz sentido em qualquer plataforma.

---

## 2. Cache-aside com TTL

**Problema.** Uma consulta pesada (`GROUP BY` sobre milhões de linhas) leva 800 ms e é
chamada 50 vezes por minuto com o mesmo resultado.

**Solução.**

```js
// cache.js
import crypto from "node:crypto";

const chaveDe = (nome, params) =>
  `c:${nome}:${crypto.createHash("sha1").update(JSON.stringify(params)).digest("hex").slice(0, 16)}`;

/**
 * Executa `consulta` com cache no Redis.
 * @param {object} kv      cliente ioredis
 * @param {string} nome    espaço de nomes lógico (ajuda a invalidar em bloco)
 * @param {object} params  entra na chave; parâmetros diferentes = cache diferente
 * @param {number} ttl     segundos de validade
 * @param {Function} consulta função async que vai ao banco
 */
export async function comCache(kv, nome, params, ttl, consulta) {
  const chave = chaveDe(nome, params);

  const emCache = await kv.get(chave);
  if (emCache !== null) return { fonte: "cache", dados: JSON.parse(emCache) };

  const dados = await consulta();

  // TTL com jitter (±10%): se mil chaves forem criadas no mesmo segundo,
  // elas NÃO devem expirar no mesmo segundo. Isso evita a estampida do exemplo 3.
  const jitter = Math.floor(ttl * (0.9 + Math.random() * 0.2));
  await kv.set(chave, JSON.stringify(dados), "EX", jitter);

  return { fonte: "banco", dados };
}
```

Uso:

```js
const r = await comCache(kv, "relatorio_vendas", { mes: "2026-08" }, 300, async () => {
  const { rows } = await db.query(
    "SELECT vendedor, sum(valor) AS total FROM venda WHERE date_trunc('month', criado_em) = $1 GROUP BY 1",
    ["2026-08-01"]
  );
  return rows;
});
console.log(r.fonte, r.dados.length);
```

**Explicação.**

- **A chave inclui os parâmetros.** Esquecer isso é o bug clássico: o usuário A vê os dados do
  usuário B. Se a consulta depende do usuário, `params` **precisa** conter o `user_id`.
- **`kv.get` retorna `null`, não `undefined`.** Testar com `if (!emCache)` trata um `0` ou `""`
  legítimo como ausência de cache.
- **TTL curto e burro vence invalidação sofisticada.** Invalidação correta é um dos dois
  problemas difíceis da computação. 30 a 300 segundos resolve 95% dos casos reais, com risco
  controlado de dado velho.
- **Nunca guarde no cache algo que você não possa recalcular.** Redis pode perder tudo a
  qualquer momento (é o contrato dele nos planos gratuitos).

---

## 3. Proteção contra estampida de cache

**Problema (real, de produção).** A chave `home:destaques` expira. No mesmo instante, 400
requisições concorrentes acham o cache vazio e disparam **400 consultas idênticas** ao banco.
O banco satura, a latência explode, o health check falha, a plataforma reinicia o serviço — e
o problema recomeça. Isso se chama *cache stampede* ou *thundering herd*.

**Solução (single-flight com trava distribuída).**

```js
// single-flight.js
const dormir = (ms) => new Promise((r) => setTimeout(r, ms));

export async function comCacheProtegido(kv, chave, ttl, consulta, opcoes = {}) {
  const { travaTtl = 10, esperaMax = 3000, passo = 50 } = opcoes;

  const cache = await kv.get(chave);
  if (cache !== null) return JSON.parse(cache);

  const chaveTrava = `lock:${chave}`;
  const token = crypto.randomUUID();

  // SET NX = "só define se não existir". É a primitiva de trava do Redis.
  // EX garante que a trava morre sozinha se o processo que a pegou cair.
  const peguei = await kv.set(chaveTrava, token, "NX", "EX", travaTtl);

  if (peguei) {
    try {
      const dados = await consulta();
      await kv.set(chave, JSON.stringify(dados), "EX", ttl);
      return dados;
    } finally {
      // Libera a trava SOMENTE se ainda for a nossa. Sem esta checagem atômica,
      // um processo lento libera a trava de outro — bug clássico de trava distribuída.
      await kv.eval(
        `if redis.call("get", KEYS[1]) == ARGV[1] then return redis.call("del", KEYS[1]) else return 0 end`,
        1, chaveTrava, token
      );
    }
  }

  // Não peguei a trava: outro está calculando. Espero o resultado dele.
  const limite = Date.now() + esperaMax;
  while (Date.now() < limite) {
    await dormir(passo);
    const pronto = await kv.get(chave);
    if (pronto !== null) return JSON.parse(pronto);
  }

  // Deu tempo demais: melhor ir ao banco do que devolver erro ao usuário.
  // Isso é uma decisão de projeto: prefere-se carga extra a indisponibilidade.
  return consulta();
}
```

**Explicação.**

- **`SET chave valor NX EX n`** é uma operação **atômica**: ou define e trava, ou não faz nada.
  Fazer `EXISTS` e depois `SET` **não** é atômico e falha sob concorrência.
- **A liberação precisa ser condicional e atômica**, daí o script Lua: no Redis, um script Lua
  roda inteiro, sem intercalação.
- **Isto não é um Redlock.** Para trava distribuída com garantias fortes entre múltiplos nós
  Redis, há um debate famoso — Martin Kleppmann contra Salvatore Sanfilippo, 2016 — sobre o
  algoritmo Redlock ser ou não seguro. Resumo honesto: para **eficiência** (evitar trabalho
  duplicado), esta trava basta. Para **correção** (nunca, jamais, dois processos ao mesmo
  tempo), Redis não é a ferramenta; use uma transação no PostgreSQL com
  `SELECT ... FOR UPDATE` ou `pg_advisory_lock`.

---

## 4. Limitação de taxa (rate limit) com Redis

**Problema.** Alguém descobre `/api/login` e tenta 5.000 senhas por minuto. Ou um cliente mal
configurado chama sua API em laço e consome a cota gratuita do Upstash em duas horas.

**Solução (janela deslizante, atômica, um round-trip).**

```lua
-- rate_limit.lua — janela deslizante com precisão de milissegundo
-- KEYS[1] = chave do balde  |  ARGV[1] = limite  ARGV[2] = janela(ms)  ARGV[3] = agora(ms)  ARGV[4] = id único
local chave, limite, janela, agora, id = KEYS[1], tonumber(ARGV[1]), tonumber(ARGV[2]), tonumber(ARGV[3]), ARGV[4]

redis.call('ZREMRANGEBYSCORE', chave, 0, agora - janela)  -- descarta o que saiu da janela
local usados = redis.call('ZCARD', chave)

if usados >= limite then
  local mais_antigo = redis.call('ZRANGE', chave, 0, 0, 'WITHSCORES')
  local espera = math.ceil((tonumber(mais_antigo[2]) + janela - agora) / 1000)
  return {0, usados, espera}
end

redis.call('ZADD', chave, agora, id)
redis.call('PEXPIRE', chave, janela)      -- a chave se apaga sozinha; nada de lixo eterno
return {1, usados + 1, 0}
```

```js
// rate-limit.js
import { readFileSync } from "node:fs";
const SCRIPT = readFileSync(new URL("./rate_limit.lua", import.meta.url), "utf8");

export function criarLimitador(kv, { limite = 60, janelaMs = 60_000 } = {}) {
  return async function permitir(identificador) {
    const [ok, usados, esperaS] = await kv.eval(
      SCRIPT, 1, `rl:${identificador}`, limite, janelaMs, Date.now(), crypto.randomUUID()
    );
    return { permitido: ok === 1, usados, retryAfter: esperaS };
  };
}
```

Uso, com os cabeçalhos HTTP corretos:

```js
const limitar = criarLimitador(kv, { limite: 10, janelaMs: 60_000 });

// dentro do handler:
const ip = req.headers["cf-connecting-ip"]         // Cloudflare
        ?? req.headers["x-forwarded-for"]?.split(",")[0].trim()
        ?? req.socket.remoteAddress;

const r = await limitar(`login:${ip}`);
res.setHeader("ratelimit-limit", 10);
res.setHeader("ratelimit-remaining", Math.max(0, 10 - r.usados));
if (!r.permitido) {
  res.setHeader("retry-after", r.retryAfter);      // RFC 9110 — o cliente deve respeitar
  res.writeHead(429, { "content-type": "application/json" });
  return res.end(JSON.stringify({ erro: "muitas requisições" }));
}
```

**Explicação.**

- **Tudo num script Lua = uma ida e volta e atomicidade.** Fazer `ZCARD` e depois `ZADD` em
  chamadas separadas permite que N requisições concorrentes passem juntas.
- **`PEXPIRE` em toda chamada** impede que chaves de IPs que nunca mais voltam fiquem para
  sempre ocupando memória — no plano gratuito de 256 MB isso importa muito.
- **Cuidado com `X-Forwarded-For`**: qualquer cliente pode forjá-lo. Confie **apenas** no
  cabeçalho que o seu proxy da frente escreve (`CF-Connecting-IP` na Cloudflare,
  `X-Forwarded-For` do balanceador da própria plataforma) e **nunca** no primeiro valor de uma
  lista vinda da internet aberta.
- **Custo na cota:** cada chamada é 1 comando (o `eval`). Com o limite gratuito da Upstash
  (500 mil comandos/mês), isso são ~16 mil requisições/dia — planeje limitar só as rotas caras.

---

## 5. Sessão em Redis, não na memória do processo

**Problema.** Você guardou a sessão num `Map` em memória. Funciona perfeitamente — até você
subir a segunda instância, ou até a plataforma reiniciar o container (o que ela faz a cada
deploy, e o plano gratuito faz a cada 15 minutos de ociosidade). Aí todo mundo é deslogado.

**Solução.**

```js
// sessao.js
import crypto from "node:crypto";

const TTL = 60 * 60 * 24 * 7;   // 7 dias

export async function criarSessao(kv, dados) {
  // 32 bytes de aleatoriedade criptográfica. NUNCA use Math.random() para isto.
  const id = crypto.randomBytes(32).toString("base64url");
  await kv.set(`sess:${id}`, JSON.stringify(dados), "EX", TTL);
  return id;
}

export async function lerSessao(kv, id) {
  if (!id) return null;
  const bruto = await kv.get(`sess:${id}`);
  if (!bruto) return null;
  await kv.expire(`sess:${id}`, TTL);   // sessão deslizante: renova a cada uso
  return JSON.parse(bruto);
}

export const destruirSessao = (kv, id) => kv.del(`sess:${id}`);

export function cookieDeSessao(id) {
  // Os quatro atributos que importam, e por quê:
  //   HttpOnly  → JavaScript da página não lê (mitiga XSS roubando sessão)
  //   Secure    → só trafega em HTTPS
  //   SameSite  → mitiga CSRF; Lax é o padrão sensato
  //   Max-Age   → o navegador esquece junto com o servidor
  return `sid=${id}; HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=${TTL}`;
}
```

**Explicação.**

- **Sessão em Redis é o que torna o serviço *stateless***, e serviço stateless é o que permite
  escalar horizontalmente, reiniciar sem dor e usar plano gratuito que dorme.
- **Sessão no Redis vs. JWT no cookie**: o JWT não precisa de servidor de estado, mas **não é
  revogável** antes de expirar. Sessão em Redis é revogável (`DEL`) e custa uma ida ao Redis
  por requisição. Recomendação profissional: **sessão em Redis para aplicação web com login**,
  JWT para comunicação entre serviços. Veja [`jwt`](../jwt/00-MAPA.md).
- **`base64url`, não `hex`**: mesma entropia, cookie 25% menor.

---

## 6. Fila de trabalho com Redis Streams

**Problema.** Enviar e-mail, gerar PDF ou chamar uma API lenta dentro da requisição HTTP faz o
usuário esperar e estoura o timeout da plataforma (Vercel Hobby: 300 s; Cloudflare Workers:
CPU limitada por invocação). Precisa ir para segundo plano.

**Solução — produtor:**

```js
// produtor.js
export async function enfileirar(kv, tarefa) {
  // XADD acrescenta ao stream. MAXLEN ~ 10000 mantém o stream limitado
  // (o "~" é aproximado e MUITO mais barato que o corte exato).
  return kv.xadd("fila:emails", "MAXLEN", "~", 10_000, "*",
    "tipo", tarefa.tipo,
    "payload", JSON.stringify(tarefa.payload),
    "tentativas", "0");
}
```

**Consumidor (worker), com grupo e reprocessamento:**

```js
// worker.js — roda como processo separado (outro serviço na plataforma)
import Redis from "ioredis";
const kv = new Redis(process.env.REDIS_URL);

const STREAM = "fila:emails";
const GRUPO  = "workers";
const EU     = `worker-${process.pid}`;

async function garantirGrupo() {
  try {
    // MKSTREAM cria o stream se não existir. "$" = só mensagens novas.
    await kv.xgroup("CREATE", STREAM, GRUPO, "$", "MKSTREAM");
  } catch (e) {
    if (!String(e.message).includes("BUSYGROUP")) throw e;  // já existe: tudo bem
  }
}

async function processar(id, campos) {
  const tarefa = Object.fromEntries(
    campos.reduce((acc, v, i) => (i % 2 ? acc : [...acc, [v, campos[i + 1]]]), [])
  );
  console.log("processando", id, tarefa.tipo);
  // ... o trabalho de verdade ...
  await kv.xack(STREAM, GRUPO, id);   // ACK: só depois de concluído com sucesso
}

async function recuperarPendentes() {
  // Mensagens entregues a um worker que morreu antes do ACK ficam "pendentes".
  // XAUTOCLAIM as transfere para mim depois de 60 s sem ACK.
  const [, mensagens] = await kv.xautoclaim(STREAM, GRUPO, EU, 60_000, "0", "COUNT", 10);
  for (const [id, campos] of mensagens) await processar(id, campos);
}

async function laco() {
  await garantirGrupo();
  for (;;) {
    await recuperarPendentes();
    // BLOCK 5000: espera até 5 s por mensagem nova, sem consumir CPU nem cota.
    const r = await kv.xreadgroup("GROUP", GRUPO, EU, "COUNT", 10, "BLOCK", 5000,
                                  "STREAMS", STREAM, ">");
    if (!r) continue;
    for (const [, mensagens] of r) {
      for (const [id, campos] of mensagens) {
        try { await processar(id, campos); }
        catch (e) { console.error("falhou", id, e.message); /* fica pendente e será reclamada */ }
      }
    }
  }
}

process.on("SIGTERM", async () => { await kv.quit(); process.exit(0); });
laco();
```

**Explicação.**

- **Por que Streams e não `LPUSH`/`BRPOP`?** Lista não tem confirmação: se o worker morre
  depois de tirar o item e antes de terminar, **o item some**. Stream com *consumer group*
  guarda a mensagem como pendente até o `XACK`. É a diferença entre "no máximo uma vez" e
  "pelo menos uma vez".
- **"Pelo menos uma vez" implica que seu processamento precisa ser idempotente.** Se o worker
  morre após enviar o e-mail e antes do `XACK`, o e-mail será enviado de novo. Guarde uma
  chave de idempotência (`SET enviado:<id> 1 NX EX 86400`).
- **`MAXLEN ~`**: sem isso, o stream cresce para sempre e estoura a memória do plano gratuito.
- **`BLOCK` em vez de laço de *polling*:** polling a cada 100 ms gasta 864 mil comandos por
  dia — mais que a cota mensal inteira do Upstash gratuito. `BLOCK` gasta ~1 comando a cada
  5 segundos ociosos.
- **Alternativa pronta:** BullMQ (Node) implementa tudo isso e mais retentativa exponencial.
  Use quando o problema crescer; entenda o mecanismo antes.

---

## 7. Migração de banco versionada

**Problema.** Você adicionou uma coluna direto no `psql` de produção. Três meses depois,
ninguém sabe por que o banco de homologação é diferente, e recriar o ambiente é impossível.

**Solução — `node-pg-migrate`:**

```bash
npm i -D node-pg-migrate
npx node-pg-migrate create adiciona-tabela-link
```

```js
// migrations/1755500000000_adiciona-tabela-link.cjs
exports.up = (pgm) => {
  pgm.createTable("link", {
    id:        { type: "bigserial", primaryKey: true },
    slug:      { type: "text", notNull: true, unique: true },
    destino:   { type: "text", notNull: true },
    criado_em: { type: "timestamptz", notNull: true, default: pgm.func("now()") },
  });

  // CONCURRENTLY não trava a tabela para escrita — obrigatório em produção com tráfego.
  // Exige rodar fora de transação, daí o `disableTransaction` abaixo.
  pgm.createIndex("link", "criado_em", { name: "idx_link_criado_em", concurrently: true });
};

exports.down = (pgm) => pgm.dropTable("link");

// Sem isto, CREATE INDEX CONCURRENTLY falha com:
//   "CREATE INDEX CONCURRENTLY cannot run inside a transaction block"
exports.shorthands = undefined;
module.exports.disableTransaction = true;
```

```bash
DATABASE_URL="postgresql://..." npx node-pg-migrate up
# esperado:
# > Migrating files:
# > - 1755500000000_adiciona-tabela-link
# > ### MIGRATION 1755500000000_adiciona-tabela-link (UP) ###
```

**Explicação.**

- **A ferramenta cria uma tabela `pgmigrations`** com o que já rodou. É isso que torna a
  operação idempotente e auditável.
- **`down` existe, mas não confie nele em produção.** Reverter uma migração que apagou dados
  não traz os dados de volta. O `down` serve para desenvolvimento; em produção, a rota segura
  é **rolar para frente** com uma nova migração corretiva.
- **`CONCURRENTLY`**: um `CREATE INDEX` comum trava escritas na tabela pelo tempo da criação.
  Em tabela grande, isso é uma indisponibilidade. Veja
  [`postgresql/14-indices.md`](../postgresql/14-indices.md).
- **Ordem correta no deploy:** migração **antes** do código novo, e a migração precisa ser
  compatível com o código **velho** (que ainda está rodando durante o rollout).

---

## 8. Dockerfile de produção para Node

**Problema.** A imagem tem 1,4 GB, demora 6 minutos para construir, roda como root e inclui
o código-fonte, os testes e as credenciais do `.env`.

**Solução.**

```dockerfile
# syntax=docker/dockerfile:1.7

# ---------- estágio 1: dependências de produção ----------
FROM node:24.18.0-slim AS deps
WORKDIR /app
COPY package.json package-lock.json ./
# npm ci respeita o lockfile e falha se ele estiver dessincronizado.
# --omit=dev deixa devDependencies de fora da imagem final.
RUN --mount=type=cache,target=/root/.npm npm ci --omit=dev

# ---------- estágio 2: build (se houver transpilação) ----------
FROM node:24.18.0-slim AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN --mount=type=cache,target=/root/.npm npm ci
COPY . .
RUN npm run build --if-present

# ---------- estágio 3: imagem final, mínima ----------
FROM node:24.18.0-slim AS runtime
ENV NODE_ENV=production
# dumb-init resolve o problema do PID 1: sem ele, o Node não recebe SIGTERM
# corretamente e o encerramento gracioso não acontece.
RUN apt-get update && apt-get install -y --no-install-recommends dumb-init \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY --from=deps  /app/node_modules ./node_modules
COPY --from=build /app/dist ./dist
COPY package.json ./

# Usuário sem privilégio. A imagem oficial do Node já traz o usuário "node".
USER node
EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD node -e "fetch('http://127.0.0.1:3000/health').then(r=>process.exit(r.ok?0:1)).catch(()=>process.exit(1))"
ENTRYPOINT ["dumb-init", "--"]
CMD ["node", "dist/server.js"]
```

`.dockerignore` — tão importante quanto o Dockerfile:

```
node_modules
npm-debug.log
.git
.github
.env
.env.*
*.md
coverage
dist
.vscode
```

**Explicação.**

- **Multi-stage**: a imagem final não contém compilador, `devDependencies` nem código-fonte.
  Menos MB, menos superfície de ataque, deploy mais rápido.
- **Ordem das camadas**: copiar `package*.json` **antes** do resto faz o Docker reaproveitar o
  cache de `npm ci` enquanto as dependências não mudam. Inverta a ordem e todo build baixa
  tudo de novo.
- **`USER node`**: container rodando como root é o achado nº 1 de qualquer auditoria de
  segurança. Custa uma linha.
- **`dumb-init`**: sem um init adequado, o Node vira PID 1 e ignora sinais por padrão; o
  `SIGTERM` do deploy não chega e o container é morto à força após o *grace period*,
  cortando requisições em andamento.
- **`.dockerignore` com `.env`**: sem isso, seus segredos vão para dentro da imagem — e
  imagens são compartilhadas, publicadas e cacheadas.

---

## 9. `compose.yaml` local com Postgres e Valkey

**Problema.** Cada pessoa da equipe tem uma versão diferente de Postgres instalada na máquina,
e "na minha máquina funciona".

**Solução.**

```yaml
# compose.yaml — Docker Compose v2 (o campo "version:" é obsoleto desde 2023)
name: minha-app

services:
  db:
    image: postgres:18.6
    environment:
      POSTGRES_USER: app
      POSTGRES_PASSWORD: dev_senha_local
      POSTGRES_DB: app
    ports: ["5432:5432"]
    volumes:
      - pgdata:/var/lib/postgresql/data
      - ./sql/init.sql:/docker-entrypoint-initdb.d/01-init.sql:ro
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app -d app"]
      interval: 5s
      timeout: 3s
      retries: 10

  cache:
    image: valkey/valkey:9
    command: ["valkey-server", "--save", "", "--appendonly", "no", "--maxmemory", "128mb", "--maxmemory-policy", "allkeys-lru"]
    ports: ["6379:6379"]
    healthcheck:
      test: ["CMD", "valkey-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 10

  api:
    build: .
    environment:
      DATABASE_URL: postgresql://app:dev_senha_local@db:5432/app
      REDIS_URL: redis://cache:6379
      PORT: "3000"
    ports: ["3000:3000"]
    depends_on:
      db:    { condition: service_healthy }   # espera o healthcheck, não só o container subir
      cache: { condition: service_healthy }
    develop:
      watch:                                   # recarrega ao salvar (Compose 2.22+)
        - action: sync
          path: ./src
          target: /app/src
        - action: rebuild
          path: package.json

volumes:
  pgdata:
```

```bash
docker compose up --watch
# esperado: db e cache "healthy", api ouvindo em 0.0.0.0:3000
docker compose ps
docker compose down          # para tudo, MANTÉM o volume
docker compose down -v       # para tudo e APAGA os dados
```

**Explicação.**

- **`condition: service_healthy`**: sem isso, a API sobe antes do banco aceitar conexões e
  morre com `ECONNREFUSED`. `depends_on` puro só espera o container *iniciar*, não *ficar
  pronto*.
- **`--save "" --appendonly no`** desliga a persistência do Valkey em desenvolvimento: é um
  cache, não precisa sobreviver, e evita I/O inútil.
- **`maxmemory-policy allkeys-lru`** faz o Valkey descartar as chaves menos usadas quando
  encher, em vez de responder `OOM command not allowed`. É a política certa para cache puro —
  e a **errada** se você usa o Redis como fila (aí o certo é `noeviction`).
- **Nome do host é o nome do serviço** (`db`, `cache`), resolvido pelo DNS interno do Compose.
  `localhost` dentro de um container é o próprio container.

---

## 10. `render.yaml` — pilha inteira em um arquivo

**Problema.** A configuração de produção só existe nos cliques que alguém deu no painel.

**Solução.**

```yaml
# render.yaml — Blueprint: API + worker + PostgreSQL + Key Value, tudo versionado
services:
  - type: web
    name: api
    runtime: node
    plan: free                 # troque para "starter" (US$ 7/mês) para não dormir
    region: oregon             # Render não tem região no Brasil (ago/2026)
    branch: main
    buildCommand: npm ci && npm run build --if-present
    startCommand: npm start
    healthCheckPath: /health
    autoDeploy: true
    envVars:
      - key: NODE_ENV
        value: production
      - key: DATABASE_URL
        fromDatabase:
          name: app-db
          property: connectionString
      - key: REDIS_URL
        fromService:
          type: keyvalue
          name: app-cache
          property: connectionString
      - key: SESSION_SECRET
        generateValue: true    # o Render gera um valor aleatório e nunca o mostra no repositório

  - type: worker               # processo de segundo plano (exemplo 6)
    name: worker
    runtime: node
    plan: starter              # worker NÃO existe no plano free
    startCommand: node worker.js
    envVars:
      - key: REDIS_URL
        fromService: { type: keyvalue, name: app-cache, property: connectionString }

  - type: keyvalue
    name: app-cache
    plan: free                 # 25 MB, sem persistência
    region: oregon
    maxmemoryPolicy: allkeys-lru
    ipAllowList: []            # lista vazia = só a rede interna do Render alcança

databases:
  - name: app-db
    plan: free                 # 1 GB, EXPIRA 30 DIAS APÓS A CRIAÇÃO
    region: oregon
    postgresMajorVersion: "18"
```

```bash
render blueprints validate       # valida antes de subir
git add render.yaml && git commit -m "infra como código" && git push
# no painel: New → Blueprint → aponte para o repositório
```

**Explicação.**

- **`fromDatabase`/`fromService`** injetam a URL de conexão sem você copiar e colar segredo
  nenhum. É o padrão certo.
- **`generateValue: true`** cria um segredo forte que nunca passa pelo seu repositório.
- **O comentário sobre os 30 dias não é decorativo:** o PostgreSQL gratuito do Render
  **expira 30 dias após a criação**, com 14 dias de carência para migrar antes de ser apagado.
  Se você usar o plano gratuito do Render como banco, **coloque um lembrete no calendário**.
- **Worker não existe no plano gratuito.** É a limitação que mais surpreende quem monta fila.

---

## 11. `fly.toml` com região São Paulo

**Problema.** Seus usuários estão no Brasil e o backend está em Oregon: ~170 ms só de ida e
volta de rede, antes de qualquer processamento.

**Solução.**

```toml
# fly.toml
app = "minha-api"
primary_region = "gru"          # gru = Guarulhos/São Paulo

[build]
  dockerfile = "Dockerfile"

[env]
  NODE_ENV = "production"
  PORT = "8080"

[http_service]
  internal_port = 8080
  force_https = true
  auto_stop_machines = "suspend"   # suspende sem tráfego (economiza dinheiro)
  auto_start_machines = true       # acorda na primeira requisição
  min_machines_running = 0         # 0 = escala a zero; 1 = sempre uma acordada

  [http_service.concurrency]
    type = "requests"
    soft_limit = 200
    hard_limit = 250

  [[http_service.checks]]
    interval = "15s"
    timeout = "2s"
    grace_period = "10s"
    method = "GET"
    path = "/health"

[[vm]]
  size = "shared-cpu-1x"
  memory = "512mb"                 # ~US$ 3,32/mês se ficar sempre ligada
```

```bash
flyctl secrets set DATABASE_URL="postgresql://..." REDIS_URL="rediss://..."
flyctl deploy
flyctl status
# esperado: uma máquina em "gru", estado "started"
flyctl regions list
```

**Explicação.**

- **`auto_stop_machines = "suspend"`** é diferente de `"stop"`: *suspend* congela a memória e
  o retorno é de centenas de milissegundos; *stop* desliga e o retorno leva segundos.
- **`min_machines_running = 0`** significa custo próximo de zero em serviço sem tráfego — mas
  cold start para o primeiro usuário. Com `1`, você paga a máquina 24×7 (~US$ 3,32/mês para
  512 MB) e nunca tem cold start.
- **Fly.io não tem mais camada gratuita** desde 2024 (contas antigas mantiveram o legado).
  O trial novo é de 2 horas de VM ou 7 dias. Mas é **a plataforma mais barata com região no
  Brasil** — veja [`45`](45-brasil-latencia-e-lgpd.md).

---

## 12. Backup automático e gratuito no GitHub Actions

**Problema (real).** No plano gratuito de Neon, Supabase e Render, **não há backup que você
possa restaurar sozinho** com o histórico de que precisa. Se alguém rodar um `DELETE` sem
`WHERE`, acabou.

**Solução.**

```yaml
# .github/workflows/backup.yml
name: backup-postgres
on:
  schedule:
    - cron: "0 6 * * *"        # todo dia às 06:00 UTC (03:00 em Brasília)
  workflow_dispatch:            # permite rodar manualmente pelo botão

jobs:
  dump:
    runs-on: ubuntu-latest
    steps:
      - name: Instalar cliente do PostgreSQL 18
        run: |
          sudo sh -c 'echo "deb https://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
          curl -fsSL https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo gpg --dearmor -o /etc/apt/trusted.gpg.d/pgdg.gpg
          sudo apt-get update && sudo apt-get install -y postgresql-client-18

      - name: Gerar dump comprimido e cifrado
        env:
          DATABASE_URL:   ${{ secrets.DATABASE_URL }}
          BACKUP_PASSPHRASE: ${{ secrets.BACKUP_PASSPHRASE }}
        run: |
          set -euo pipefail
          ARQ="backup-$(date -u +%Y-%m-%dT%H%M).dump"
          # -Fc = formato custom (comprimido, restauração seletiva)
          pg_dump -Fc --no-owner --no-privileges "$DATABASE_URL" > "$ARQ"
          # Cifra em repouso: o artefato do GitHub não é lugar para dado cru de cliente.
          gpg --batch --yes --symmetric --cipher-algo AES256 \
              --passphrase "$BACKUP_PASSPHRASE" -o "$ARQ.gpg" "$ARQ"
          rm -f "$ARQ"
          ls -lh "$ARQ.gpg"
          echo "ARQ=$ARQ.gpg" >> "$GITHUB_ENV"

      - name: Guardar como artefato (90 dias)
        uses: actions/upload-artifact@v4
        with:
          name: ${{ env.ARQ }}
          path: ${{ env.ARQ }}
          retention-days: 90

      # Opcional: mandar para armazenamento externo (R2 da Cloudflare tem 10 GB grátis)
      # - name: Enviar para o R2
      #   run: |
      #     aws s3 cp "$ARQ" "s3://meus-backups/$ARQ" \
      #       --endpoint-url "https://<conta>.r2.cloudflarestorage.com"
      #   env:
      #     AWS_ACCESS_KEY_ID:     ${{ secrets.R2_KEY_ID }}
      #     AWS_SECRET_ACCESS_KEY: ${{ secrets.R2_SECRET }}
```

Restaurar (**pratique isto antes de precisar**):

```bash
gh run download --name backup-2026-08-18T0600.dump.gpg
gpg --batch --passphrase "$BACKUP_PASSPHRASE" -o restaurado.dump -d backup-*.gpg
createdb -h localhost -U postgres teste_restauracao
pg_restore --no-owner --clean --if-exists -d "postgresql://postgres@localhost/teste_restauracao" restaurado.dump
psql "postgresql://postgres@localhost/teste_restauracao" -c "\dt"
# esperado: as tabelas do seu sistema
```

**Explicação.**

- **GitHub Actions dá 2.000 minutos/mês grátis** em repositório privado e é **ilimitado em
  repositório público** (verificado em 18/08/2026). Um dump diário de um banco de 500 MB leva
  segundos. Ou seja: **backup de graça, sem infraestrutura própria**.
- **Cifrar é obrigatório** se há dado pessoal: artefato do GitHub é acessível a qualquer pessoa
  com acesso ao repositório, e a LGPD não perdoa isso.
- **Retenção de 90 dias** é o máximo padrão de artefatos. Para retenção maior, mande para R2,
  S3 ou Backblaze B2.
- **`set -euo pipefail`** faz o script falhar de verdade quando algo dá errado. Sem isso, um
  `pg_dump` que falha gera um arquivo vazio e o workflow reporta sucesso — o pior tipo de
  backup, o que você acha que tem.

---

## 13. Backend no Cloudflare Workers falando com PostgreSQL

**Problema.** Workers rodam em isolates V8 na borda, não em Node. Eles não têm sockets TCP
tradicionais, e abrir uma conexão nova de PostgreSQL a cada invocação — em centenas de
localidades — esgota o limite de conexões do banco em minutos.

**Solução — Hyperdrive (pool e cache de consultas gerenciados pela Cloudflare):**

```jsonc
// wrangler.jsonc
{
  "name": "api-edge",
  "main": "src/index.js",
  "compatibility_date": "2026-08-01",
  "compatibility_flags": ["nodejs_compat"],
  "hyperdrive": [
    { "binding": "HYPERDRIVE", "id": "<ID_GERADO_PELO_WRANGLER>" }
  ],
  "kv_namespaces": [
    { "binding": "CACHE", "id": "<ID_DO_NAMESPACE>" }
  ]
}
```

```bash
npx wrangler hyperdrive create meu-pg \
  --connection-string="postgresql://usuario:senha@ep-xxx.sa-east-1.aws.neon.tech/neondb?sslmode=require"
# copie o id retornado para o wrangler.jsonc
```

```js
// src/index.js
import postgres from "postgres";   // npm i postgres — cliente compatível com Workers

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);

    if (url.pathname === "/health") {
      return Response.json({ ok: true });
    }

    if (url.pathname === "/links") {
      // A connectionString do Hyperdrive aponta para o pool da Cloudflare,
      // não direto para o banco. O pool é reaproveitado entre invocações.
      const sql = postgres(env.HYPERDRIVE.connectionString, {
        max: 5,
        fetch_types: false,   // economiza um round-trip de introspecção de tipos
      });

      try {
        const linhas = await sql`SELECT slug, destino FROM link ORDER BY id DESC LIMIT 20`;
        // waitUntil: fecha a conexão DEPOIS de responder ao usuário.
        ctx.waitUntil(sql.end());
        return Response.json(linhas);
      } catch (e) {
        ctx.waitUntil(sql.end());
        return Response.json({ erro: e.message }, { status: 500 });
      }
    }

    // Workers KV como cache global (leitura barata, escrita cara e eventualmente consistente)
    if (url.pathname.startsWith("/r/")) {
      const slug = url.pathname.slice(3);
      const destino = await env.CACHE.get(`link:${slug}`);
      if (destino) return Response.redirect(destino, 302);
      return new Response("não encontrado", { status: 404 });
    }

    return new Response("não encontrado", { status: 404 });
  },
};
```

```bash
npx wrangler deploy
npx wrangler tail --format pretty
```

**Explicação.**

- **Hyperdrive existe porque o modelo da borda é incompatível com o modelo de conexão do
  PostgreSQL.** O Postgres usa **um processo do sistema operacional por conexão** — herança de
  1986 — e por isso 500 conexões já pesam num servidor pequeno. Na borda, cada uma das
  centenas de localidades abriria as suas. Hyperdrive multiplexa tudo.
- **Está incluído nos planos Free e Paid** do Workers; o Free permite **100.000 consultas por
  dia** (18/08/2026).
- **Workers KV é eventualmente consistente** (leituras podem ver valor antigo por até ~60 s
  após escrita). Serve para configuração e para cache de leitura pesada; **não serve** para
  contador exato nem para trava. Para isso, use Durable Objects.
- **Limite do plano gratuito do Workers: 10 ms de CPU por invocação.** Tempo esperando I/O
  (banco, fetch) **não conta**; só CPU. É mais generoso do que parece — e é fatal para
  processamento pesado.

---

## 14. Teste de carga e leitura do resultado

**Problema.** "Aguenta quantos usuários?" Ninguém sabe, e a resposta chega na primeira
campanha de marketing.

**Solução.**

```bash
npm i -g autocannon          # simples; ou use k6, mais completo
```

```bash
autocannon -c 50 -d 30 -l https://minha-api.onrender.com/relatorio
#  -c 50 = 50 conexões concorrentes
#  -d 30 = 30 segundos
#  -l    = imprime a distribuição de latência (é o que importa, não a média)
```

Saída típica e como lê-la:

```
Latency (ms)
┌───────┬──────┬──────┬───────┬───────┬─────────┬─────────┬──────────┐
│ Stat  │ 2.5% │ 50%  │ 97.5% │ 99%   │ Avg     │ Stdev   │ Max      │
├───────┼──────┼──────┼───────┼───────┼─────────┼─────────┼──────────┤
│       │ 41   │ 63   │ 892   │ 2310  │ 118.4   │ 271.9   │ 4102     │
└───────┴──────┴──────┴───────┴───────┴─────────┴─────────┴──────────┘
Req/Sec: 412 (avg)     2xx: 12360     non-2xx: 0     errors: 0
```

Como um profissional lê isso:

| O que olhar | O que significa |
|---|---|
| **p50 = 63 ms** | metade dos usuários teve boa experiência. Sozinho, não diz nada |
| **p99 = 2310 ms** | **1 em cada 100 requisições levou 2,3 segundos.** É este número que gera reclamação |
| **Avg 118 ms** | a média esconde a cauda. **Nunca decida por média de latência** |
| **Max 4102 ms** | provavelmente um cold start, um GC, ou a espera por conexão do pool |
| **errors: 0** | se aparecer erro aqui, o teste já achou seu limite |

Versão em k6, com critérios de aprovação (o que se coloca no CI):

```js
// carga.js
import http from "k6/http";
import { check, sleep } from "k6";

export const options = {
  stages: [
    { duration: "30s", target: 20 },   // sobe devagar
    { duration: "1m",  target: 100 },  // patamar
    { duration: "30s", target: 0 },    // desce
  ],
  thresholds: {
    http_req_duration: ["p(95)<500", "p(99)<1500"],  // o teste FALHA se estourar
    http_req_failed:   ["rate<0.01"],                // menos de 1% de erro
  },
};

export default function () {
  const r = http.get(`${__ENV.BASE_URL}/relatorio`);
  check(r, { "status 200": (res) => res.status === 200 });
  sleep(1);
}
```

```bash
k6 run -e BASE_URL=https://minha-api.onrender.com carga.js
```

**Explicação.**

- **Meça percentis, não médias.** A média é dominada pelo caso comum; a experiência ruim mora
  em p95/p99. Numa página que faz 10 chamadas de API, o p99 de cada chamada vira o **caso
  típico** da página (probabilidade de pelo menos uma chamada lenta ≈ 1 − 0,99¹⁰ ≈ 10%).
- **Teste a partir de onde os usuários estão.** Rodar `autocannon` do seu notebook em
  Porto Alegre contra um servidor em Oregon mede principalmente a distância.
- **Não teste carga contra plano gratuito de terceiros sem ler os termos.** Muitos proíbem
  teste de carga; você pode ser suspenso. Teste contra o seu próprio ambiente.
- **O gargalo quase nunca é a CPU do app.** Nesta ordem: pool de conexões do banco → consulta
  sem índice → latência de rede entre app e banco → CPU. Meça antes de otimizar.

---

## Autoteste

1. Por que um health check que só devolve `200` é pior que não ter health check?
2. O que é estampida de cache e quais duas técnicas deste capítulo a combatem?
3. Por que a trava do exemplo 3 precisa de Lua para ser liberada?
4. Por que Redis Streams e não `LPUSH`/`BRPOP` para uma fila que não pode perder mensagens?
5. O que "pelo menos uma vez" obriga o seu processamento a ser?
6. Cite três coisas que o Dockerfile do exemplo 8 faz e que um Dockerfile ingênuo não faz.
7. Por que `depends_on` puro não basta no Compose?
8. O que expira 30 dias depois de criado no plano gratuito do Render?
9. Por que Workers precisam do Hyperdrive para falar com PostgreSQL?
10. Você tem p50 de 60 ms e p99 de 2,3 s. Qual é o problema e por que a média não o revela?
