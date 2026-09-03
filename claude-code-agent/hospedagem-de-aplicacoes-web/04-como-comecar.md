# 04 · Do ambiente pronto a uma URL pública

`Nível: iniciante` · `Atualizado em 18/08/2026` · `Tempo: 40 a 90 minutos`

Este arquivo assume que você já passou pelo [`03-instalacao.md`](03-instalacao.md) — ou que
está num Codespace. **Não repetimos instalação aqui.**

Objetivo: em menos de uma hora, ter **quatro peças no ar, de graça, sem cartão de crédito**:

```
Cloudflare Pages (frontend)  →  Render (backend Node)  →  Neon (PostgreSQL, São Paulo)
                                        └──────────────►  Upstash (Redis)
```

---

## Parte 0 · O "hello world" mais curto que é significativo (5 minutos)

Antes das quatro peças, prove que o caminho funciona. Um único arquivo, uma URL pública.

```bash
mkdir -p ola-deploy && cd ola-deploy
```

```bash
cat > server.js <<'EOF'
// Servidor HTTP mínimo, sem nenhuma dependência.
// Duas coisas obrigatórias em qualquer deploy real, e é por isso que estão aqui:
//   1) ler a porta de process.env.PORT — a plataforma escolhe a porta, não você;
//   2) escutar em 0.0.0.0 — escutar em 127.0.0.1 funciona local e falha em container.
import { createServer } from "node:http";

const port = process.env.PORT || 3000;

createServer((req, res) => {
  if (req.url === "/health") {
    res.writeHead(200, { "content-type": "application/json" });
    return res.end(JSON.stringify({ ok: true }));
  }
  res.writeHead(200, { "content-type": "text/plain; charset=utf-8" });
  res.end(`Olá do deploy! Host=${process.env.RENDER_INSTANCE_ID ?? "local"}\n`);
}).listen(port, "0.0.0.0", () => console.log(`ouvindo em 0.0.0.0:${port}`));
EOF
```

```bash
cat > package.json <<'EOF'
{
  "name": "ola-deploy",
  "type": "module",
  "engines": { "node": ">=22" },
  "scripts": { "start": "node server.js" }
}
EOF
```

```bash
npm start
# esperado: ouvindo em 0.0.0.0:3000
```

Em outro terminal:

```bash
curl -s localhost:3000/health
# esperado: {"ok":true}
```

Pare com `Ctrl+C`, publique no GitHub:

```bash
git init && git add -A && git commit -m "hello deploy"
gh repo create ola-deploy --public --source=. --push
```

Agora vá em `dashboard.render.com` → **New → Web Service** → conecte o repositório →
Runtime **Node**, Build Command `npm install`, Start Command `npm start`, Instance Type
**Free** → **Deploy**.

**Verificação:** em 2 a 4 minutos você recebe uma URL do tipo
`https://ola-deploy-xxxx.onrender.com`.

```bash
curl -s https://ola-deploy-xxxx.onrender.com/health
# esperado: {"ok":true}
```

Se veio `{"ok":true}`, o caminho inteiro (Git → build → container → rede → TLS → DNS)
funciona. **A partir daqui é só acrescentar peças.**

> **O que você vai notar:** depois de 15 minutos sem acesso, a primeira requisição demora
> ~50 segundos. Isso é o *cold start* do plano gratuito do Render, e é intencional. Não é bug,
> não é sua internet, e não tem como desligar sem pagar US$ 7/mês. Veja
> [`60-teoria-avancada.md`](60-teoria-avancada.md), seção 1, para o porquê técnico.

---

## Parte 1 · O banco PostgreSQL na Neon (10 minutos)

1. Entre em `neon.com`, crie conta com o GitHub. Sem cartão.
2. **Create project.** No campo *Region*, escolha **AWS South America (São Paulo)
   `sa-east-1`** — é a única escolha que você **não pode mudar depois** sem migrar os dados.
3. Copie a *connection string*. Ela tem esta cara:

```
postgresql://usuario:senha@ep-nome-12345.sa-east-1.aws.neon.tech/neondb?sslmode=require
```

**Verificação imediata:**

```bash
psql "postgresql://...sslmode=require" -c "select version();"
# esperado: PostgreSQL 17.x/18.x on x86_64-pc-linux-gnu ... (a versão depende do que você escolheu ao criar o projeto)
```

**Se der `no pg_hba.conf entry ... no encryption`**, faltou `?sslmode=require` na URL.
**Se travar sem responder**, a porta 5432 está bloqueada na sua rede — veja
[`03`](03-instalacao.md), seção 10.3.

Crie a tabela:

```bash
psql "$DATABASE_URL" <<'EOF'
CREATE TABLE IF NOT EXISTS visita (
  id          bigserial PRIMARY KEY,
  caminho     text        NOT NULL,
  criado_em   timestamptz NOT NULL DEFAULT now()
);
EOF
```

```bash
psql "$DATABASE_URL" -c "\dt"
# esperado: uma tabela chamada visita
```

> **Limite a conhecer agora, não depois:** o plano gratuito da Neon dá **0,5 GB por projeto**
> e **100 CU-horas por mês**, e o *compute* **suspende após 5 minutos** de inatividade. A
> suspensão é boa (não consome sua cota) e custa ~500 ms na primeira consulta depois dela.

---

## Parte 2 · O Redis na Upstash (5 minutos)

1. Entre em `upstash.com`, crie conta com o GitHub. Sem cartão.
2. **Create Database** → tipo **Redis** → região mais próxima (há São Paulo como região
   primária ou como réplica de leitura no modo Global).
3. Copie a URL `rediss://...` (dois "s" — é TLS).

**Verificação:**

```bash
redis-cli --tls -u "rediss://default:TOKEN@xxx.upstash.io:6379" PING
# esperado: PONG
```

```bash
redis-cli --tls -u "$REDIS_URL" SET teste "funciona" EX 60
redis-cli --tls -u "$REDIS_URL" GET teste
# esperado: OK  e depois  "funciona"
```

> **Limite a conhecer agora:** 256 MB de dados, **500 mil comandos por mês** e 10 GB de
> tráfego. Um contador que dispara a cada requisição consome cota rápido: 500 mil comandos
> dão ~16 mil requisições por dia se você fizer 1 comando por requisição. Planeje isso.

---

## Parte 3 · Ligar o backend nas duas peças (15 minutos)

```bash
npm init -y && npm pkg set type=module
npm i pg ioredis
```
`pg` é o driver oficial do PostgreSQL para Node; `ioredis` é o cliente Redis mais usado.

```bash
cat > server.js <<'EOF'
import { createServer } from "node:http";
import pg from "pg";
import Redis from "ioredis";

// --- Conexões -------------------------------------------------------------
// Pool, e não Client: um pool reaproveita conexões TCP. Abrir conexão nova a
// cada requisição é o erro de performance nº 1 com PostgreSQL (ver 60-teoria).
const db = new pg.Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: { rejectUnauthorized: false }, // provedores gerenciados usam CA própria
  max: 5,                              // plano gratuito tem POUCAS conexões: seja modesto
  idleTimeoutMillis: 10_000,
});

const kv = new Redis(process.env.REDIS_URL, { maxRetriesPerRequest: 2 });

// --- Rotas ----------------------------------------------------------------
const server = createServer(async (req, res) => {
  const json = (code, obj) => {
    res.writeHead(code, { "content-type": "application/json; charset=utf-8" });
    res.end(JSON.stringify(obj));
  };

  try {
    if (req.url === "/health") {
      // Health check de verdade: prova que as dependências respondem.
      await db.query("SELECT 1");
      await kv.ping();
      return json(200, { ok: true, db: "up", cache: "up" });
    }

    if (req.url === "/visita") {
      // 1) grava no PostgreSQL (durável, não pode sumir)
      await db.query("INSERT INTO visita (caminho) VALUES ($1)", [req.url]);
      // 2) incrementa no Redis (rápido, pode sumir sem drama)
      const total = await kv.incr("visitas:total");
      // 3) o número "de verdade" vem do banco; o do cache é só o rápido
      return json(200, { visitas_no_cache: total });
    }

    if (req.url === "/relatorio") {
      // Cache-aside: tenta o cache; se não tiver, consulta o banco e guarda por 30 s.
      const cache = await kv.get("relatorio");
      if (cache) return json(200, { fonte: "cache", ...JSON.parse(cache) });

      const { rows } = await db.query("SELECT count(*)::int AS total FROM visita");
      const payload = { total: rows[0].total };
      await kv.set("relatorio", JSON.stringify(payload), "EX", 30);
      return json(200, { fonte: "banco", ...payload });
    }

    json(404, { erro: "rota não encontrada" });
  } catch (e) {
    console.error(e);           // log estruturado vai para o painel da plataforma
    json(500, { erro: e.message });
  }
});

const port = process.env.PORT || 3000;
server.listen(port, "0.0.0.0", () => console.log(`ouvindo em 0.0.0.0:${port}`));

// Encerramento gracioso: a plataforma manda SIGTERM antes de matar o container.
// Sem isto, requisições em andamento são cortadas a cada deploy.
process.on("SIGTERM", async () => {
  server.close();
  await Promise.allSettled([db.end(), kv.quit()]);
  process.exit(0);
});
EOF
```

Teste local, com as variáveis apontando para a nuvem:

```bash
DATABASE_URL="postgresql://..." REDIS_URL="rediss://..." node server.js
```

```bash
curl -s localhost:3000/health
# esperado: {"ok":true,"db":"up","cache":"up"}
curl -s localhost:3000/visita
# esperado: {"visitas_no_cache":1}
curl -s localhost:3000/relatorio
# esperado: {"fonte":"banco","total":1}
curl -s localhost:3000/relatorio
# esperado: {"fonte":"cache","total":1}   ← a segunda vez veio do Redis
```

**Essa última diferença — `banco` virando `cache` — é o momento em que o Redis deixa de ser
teoria.**

Agora, no painel do Render, em *Environment*, crie `DATABASE_URL` e `REDIS_URL` com os mesmos
valores, e faça o commit:

```bash
git add -A && git commit -m "backend com postgres e redis" && git push
```

O Render faz deploy sozinho a cada `push` na branch padrão.

**Verificação final do backend:**

```bash
curl -s https://SEU-APP.onrender.com/health
# esperado: {"ok":true,"db":"up","cache":"up"}
```

---

## Parte 4 · O frontend na Cloudflare Pages (10 minutos)

```bash
mkdir -p ../frontend && cd ../frontend
```

```bash
cat > index.html <<'EOF'
<!doctype html>
<html lang="pt-BR">
<meta charset="utf-8">
<title>Painel</title>
<style>body{font:16px system-ui;margin:3rem auto;max-width:38rem}button{padding:.6rem 1rem}</style>
<h1>Painel de visitas</h1>
<button id="b">Registrar visita</button>
<pre id="saida">—</pre>
<script>
// Troque pela URL do seu backend no Render.
const API = "https://SEU-APP.onrender.com";
const saida = document.getElementById("saida");
document.getElementById("b").onclick = async () => {
  saida.textContent = "carregando… (se o backend estiver dormindo, leva ~50 s)";
  const r = await fetch(`${API}/visita`);
  const v = await r.json();
  const rel = await (await fetch(`${API}/relatorio`)).json();
  saida.textContent = JSON.stringify({ ...v, ...rel }, null, 2);
};
</script>
EOF
```

```bash
git init && git add -A && git commit -m "frontend" && gh repo create painel-frontend --public --source=. --push
```

Em `dash.cloudflare.com` → **Workers & Pages → Create → Pages → Connect to Git** → escolha o
repositório → build command vazio, output directory `/` → **Save and Deploy**.

**Verificação:** abre `https://painel-frontend.pages.dev` e o botão funciona.

**Se o botão falhar com erro de CORS** no console do navegador
(`Access to fetch at ... has been blocked by CORS policy`), acrescente no backend, antes de
qualquer resposta:

```js
res.setHeader("access-control-allow-origin", "https://painel-frontend.pages.dev");
res.setHeader("access-control-allow-methods", "GET,POST,OPTIONS");
if (req.method === "OPTIONS") { res.writeHead(204); return res.end(); }
```

> **Não use `*` em produção** se a API usar cookies ou credenciais — `*` e
> `credentials: include` são incompatíveis por especificação, e mesmo quando funciona é uma
> porta aberta.

---

## O ciclo de trabalho do dia a dia

```
   editar  ──►  rodar local  ──►  ver  ──►  commit  ──►  push  ──►  deploy automático
      ▲                                                                    │
      └────────────────────  ler log / rollback  ◄────────────────────────┘
```

Comandos do ciclo (na sua pilha):

```bash
docker compose up -d          # sobe Postgres e Redis locais (ver 07-projeto-modelo)
npm run dev                    # roda a aplicação com recarga automática
npm test                       # roda os testes antes de subir
git push                       # dispara o deploy
render services                # (opcional) acompanha pela CLI
```

Ver log de produção:

```bash
render ssh SEU_SERVICE_ID          # shell no container (não disponível no plano Free)
# no plano Free, use o painel: Dashboard → Logs
```

Rollback (o comando mais importante que ninguém pratica antes de precisar):
no painel do Render, *Deploys* → escolha o deploy anterior → **Rollback**. Pratique isso
**hoje**, não durante um incidente. Há um laboratório inteiro sobre isso em
[`70-pratica.md`](70-pratica.md), lab 9.

---

## Os cinco primeiros erros de uso (não de instalação)

| Sintoma | Causa | Correção |
|---|---|---|
| Deploy "sucesso", mas a URL dá `502 Bad Gateway` ou fica em *Deploy failed: no open ports* | O app escutou em `127.0.0.1` ou numa porta fixa | escute em `0.0.0.0` e use `process.env.PORT` |
| Primeira requisição do dia leva 50 segundos | Cold start do plano gratuito | esperado; pague US$ 7 ou aceite. **Não** "resolva" com um cron que pinga o serviço — veja [`75`](75-armadilhas.md), armadilha 6 |
| `Error: connect ETIMEDOUT` ao chamar o banco em produção | Banco em outra região, ou pausado, ou firewall da plataforma | confira região e status; teste com `psql` da mesma rede |
| `remaining connection slots are reserved` / `too many connections` | Um `pg.Client` novo por requisição, ou `max` alto demais para o plano | use **um** pool com `max` pequeno (2–5 no gratuito) |
| Variável de ambiente "não pega" | Foi criada no painel mas o serviço não foi reimplantado | plataformas exigem novo deploy após mudar variável; confira com um endpoint que imprima `Object.keys(process.env)` — **nunca os valores** |

---

## Onde ir depois

- Mais receitas prontas: [`06-exemplos.md`](06-exemplos.md)
- A aplicação completa, com testes e migrações: [`07-projeto-modelo/`](07-projeto-modelo/README.md)
- Comandos de todas as CLIs, por tarefa: [`05-manual-de-uso.md`](05-manual-de-uso.md)
- Escolher a pilha definitiva: [`40-arquiteturas-de-referencia.md`](40-arquiteturas-de-referencia.md)

---

## Autoteste

1. Por que o servidor deve escutar em `0.0.0.0` e ler `process.env.PORT`? O que acontece se não fizer?
2. Qual foi a prova visível, na Parte 3, de que o cache estava funcionando?
3. Por que a região da Neon é a decisão mais irreversível desta parte do curso?
4. O que é `?sslmode=require` e o que acontece sem ele?
5. Por que usar um *pool* com `max` baixo em vez de abrir uma conexão por requisição?
6. O que o `SIGTERM` faz no código, e o que quebra sem ele?
7. Você mudou uma variável de ambiente no painel e nada mudou. Por quê?
