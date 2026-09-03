# 05 · Manual de uso — referência por tarefa

`Nível: iniciante a intermediário` · `Atualizado em 18/08/2026`

Referência **consultável**, organizada por *tarefa que você quer realizar*, não por ordem
alfabética de comando. Use `Ctrl+F`.

Convenção: `<ID>` e `<NOME>` são placeholders. Onde há mais de um jeito, o **primeiro é o
recomendado**.

---

## Índice de tarefas

| Quero… | Vá para |
|---|---|
| Fazer o primeiro deploy | [§1](#1-deploy-inicial) |
| Ver logs | [§2](#2-logs) |
| Definir variáveis de ambiente e segredos | [§3](#3-variáveis-de-ambiente-e-segredos) |
| Conectar no banco de produção | [§4](#4-banco-de-dados-postgresql) |
| Fazer backup e restaurar | [§5](#5-backup-e-restauração) |
| Mexer no Redis | [§6](#6-redisvalkey) |
| Apontar um domínio | [§7](#7-domínio-e-tls) |
| Fazer rollback | [§8](#8-rollback-e-histórico-de-deploy) |
| Escalar / mudar tamanho | [§9](#9-escala-e-tamanho-de-instância) |
| Definir tudo em arquivo (IaC) | [§10](#10-infraestrutura-como-código) |
| Entrar no container | [§11](#11-shell-no-container-e-execução-pontual) |
| Automatizar com CI | [§12](#12-ci-cd-com-github-actions) |
| Saber o que está obsoleto | [§13](#13-obsoleto-e-o-que-substituiu) |

---

## 1. Deploy inicial

| Plataforma | Comando | Observação |
|---|---|---|
| **Render** | painel web (recomendado) ou `render.yaml` + *Blueprint* | a CLI **não** cria serviço interativamente; use `render services create` só em modo não interativo |
| **Railway** | `railway init` → `railway up` | `railway up` envia o diretório atual e constrói na nuvem |
| **Fly.io** | `flyctl launch` → `flyctl deploy` | `launch` gera o `fly.toml` e faz perguntas; `deploy` usa o arquivo |
| **Vercel** | `vercel` (preview) → `vercel --prod` | sem argumento ele cria um deploy de *preview* |
| **Cloudflare** | `npx wrangler deploy` | precisa de `wrangler.toml`/`wrangler.jsonc` |
| **Koyeb** | painel web ou `koyeb service create` | |
| **Northflank** | painel web ou `northflank create service` | |
| **VPS + Coolify** | `git push` para o repositório conectado | o Coolify escuta o webhook |

```bash
# Fly.io — o fluxo completo, do zero
flyctl launch --no-deploy        # gera fly.toml sem subir nada ainda
flyctl secrets set DATABASE_URL="postgresql://..."   # segredos ANTES do primeiro deploy
flyctl deploy                     # constrói e publica
flyctl status                     # esperado: instâncias com estado "started"
flyctl open                       # abre a URL no navegador
```

```bash
# Vercel
vercel link                       # associa a pasta a um projeto existente
vercel --prod                     # deploy de produção
vercel inspect <URL>              # detalhes de um deploy específico
```

---

## 2. Logs

| Plataforma | Ao vivo | Histórico | Retenção no plano gratuito |
|---|---|---|---|
| Render | painel → *Logs* | painel, filtro por texto | 7 dias (planos pagos guardam mais) |
| Railway | `railway logs` | `railway logs --deployment <ID>` | limitada |
| Fly.io | `flyctl logs` | `flyctl logs -i <INSTANCE>` | curta; use *log shipper* para guardar |
| Vercel | `vercel logs <URL>` | painel → *Runtime Logs* | **1 hora** no Hobby, 1 dia no Pro |
| Cloudflare | `npx wrangler tail` | Logpush (pago) | *tail* é ao vivo, não é histórico |
| Supabase | painel → *Logs* | | 1 dia no Free |

```bash
railway logs --follow                       # segue o fluxo
flyctl logs --app <NOME> --region gru       # só de uma região
npx wrangler tail --format pretty           # log ao vivo do Worker
```

> **Regra de ouro:** log de plataforma é volátil e some. Se o log importa (auditoria,
> depuração de incidente antigo), **mande para fora** — Better Stack, Axiom, Grafana Loki,
> ou um bucket S3. Veja [`50-operacao-e-ciclo-de-vida.md`](50-operacao-e-ciclo-de-vida.md).

---

## 3. Variáveis de ambiente e segredos

| Plataforma | Definir | Listar | Efeito |
|---|---|---|---|
| Render | painel → *Environment*, ou `render.yaml` | painel | **exige novo deploy** |
| Railway | `railway variables --set "CHAVE=valor"` | `railway variables` | redeploy automático |
| Fly.io | `flyctl secrets set CHAVE=valor` | `flyctl secrets list` (mostra só o *digest*) | **reinicia as máquinas** |
| Vercel | `vercel env add CHAVE production` | `vercel env ls` | vale no próximo build |
| Cloudflare | `npx wrangler secret put CHAVE` | `npx wrangler secret list` | imediato |
| Supabase | painel → *Settings → API* | | |

```bash
# puxar as variáveis de produção para um .env local (útil, perigoso)
vercel env pull .env.local
railway variables --json > vars.json
```

Regras que evitam vazamento — todas já custaram caro a alguém:

1. `.env` **sempre** no `.gitignore`; versione um `.env.example` **sem valores**.
2. Segredo que foi para o Git está **queimado**, mesmo depois de removido no commit seguinte:
   ele fica no histórico e nos *forks*. **Rotacione**, não apague.
3. Em CI, use os *secrets* do provedor (`gh secret set NOME`), nunca texto no YAML.
4. Nunca imprima o valor em log. Imprima só a chave, ou o *hash*.
5. Prefira segredos de vida curta (tokens com expiração) a senhas eternas.

Detalhamento completo: [`variaveis-de-ambiente-e-segredos`](../variaveis-de-ambiente-e-segredos/01-introducao-leigo.md).

---

## 4. Banco de dados (PostgreSQL)

### 4.1 Conectar

```bash
psql "$DATABASE_URL"                       # o jeito universal
render psql <DATABASE_ID>                  # Render: abre psql já autenticado
flyctl postgres connect -a <NOME>          # Fly (Postgres não gerenciado, legado)
railway connect Postgres                   # Railway: abre psql no serviço
npx supabase db remote commit              # Supabase: fluxo de migração
neonctl connection-string <projeto>        # Neon: imprime a URL
```

### 4.2 Comandos de `psql` que você vai usar toda semana

| Comando | O que faz |
|---|---|
| `\l` | lista bancos |
| `\dt` | lista tabelas |
| `\d nome_tabela` | descreve a tabela (colunas, índices, constraints) |
| `\di` | lista índices |
| `\du` | lista roles/usuários |
| `\x` | alterna saída "expandida" (essencial para linhas largas) |
| `\timing` | mostra o tempo de cada consulta |
| `\e` | abre a última consulta no editor |
| `\copy tabela FROM 'arq.csv' CSV HEADER` | importa CSV **pelo cliente** (funciona sem acesso ao disco do servidor) |
| `\q` | sai |

### 4.3 Diagnóstico rápido em produção

```sql
-- Quantas conexões, por estado? (o gargalo nº 1 dos planos pequenos)
SELECT state, count(*) FROM pg_stat_activity GROUP BY state;

-- Quem está travando quem?
SELECT pid, wait_event_type, wait_event, left(query, 60)
FROM pg_stat_activity WHERE state <> 'idle';

-- Tamanho do banco (o que consome sua cota gratuita)
SELECT pg_size_pretty(pg_database_size(current_database()));

-- As 5 maiores tabelas
SELECT relname, pg_size_pretty(pg_total_relation_size(relid)) AS tamanho
FROM pg_catalog.pg_statio_user_tables ORDER BY pg_total_relation_size(relid) DESC LIMIT 5;

-- Consultas mais custosas (exige a extensão pg_stat_statements)
SELECT left(query,60), calls, round(mean_exec_time::numeric,2) AS ms_medio
FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 10;
```

### 4.4 Migrações

Nunca altere esquema por `psql` manual em produção. Use uma ferramenta com histórico:

| Ferramenta | Ecossistema | Comando típico |
|---|---|---|
| **node-pg-migrate** | Node puro | `npx node-pg-migrate up` |
| **Prisma Migrate** | Node/TS com ORM | `npx prisma migrate deploy` |
| **Drizzle Kit** | Node/TS, SQL-first | `npx drizzle-kit migrate` |
| **Flyway** | Java e agnóstico | `flyway migrate` |
| **Alembic** | Python/SQLAlchemy | `alembic upgrade head` |
| **golang-migrate** | Go e agnóstico | `migrate -path ./migrations -database "$DATABASE_URL" up` |
| **Supabase CLI** | Supabase | `npx supabase db push` |

Regra de ouro das migrações em produção: **sempre compatível para trás**. Adicione coluna
nova como nula, faça o código escrever nos dois lugares, migre os dados, e só então remova a
velha. Isso é o padrão *expand/contract*. Detalhe em
[`50-operacao-e-ciclo-de-vida.md`](50-operacao-e-ciclo-de-vida.md).

---

## 5. Backup e restauração

```bash
# Dump lógico completo, formato custom (o mais flexível)
pg_dump -Fc --no-owner --no-privileges "$DATABASE_URL" > backup_$(date +%F).dump

# Restaurar em outro banco
pg_restore --no-owner --clean --if-exists -d "$DATABASE_URL_DESTINO" backup_2026-08-18.dump

# Só o esquema, ou só os dados
pg_dump --schema-only "$DATABASE_URL" > esquema.sql
pg_dump --data-only   "$DATABASE_URL" > dados.sql

# Uma tabela só
pg_dump -t public.pedidos "$DATABASE_URL" > pedidos.sql
```

| Provedor | Backup automático no plano gratuito? |
|---|---|
| Neon | *point-in-time* limitado por retenção do plano; o **Free tem histórico curto** |
| Supabase | **não** no Free (o Pro tem diário, 7 dias) |
| Render | **não** no banco gratuito |
| Aiven | conforme o plano |
| Railway | conforme o plano |

> **Consequência prática:** no plano gratuito, **o backup é responsabilidade sua**. Um
> `pg_dump` semanal num cron do GitHub Actions custa zero e já salvou muita gente. Receita
> pronta em [`06-exemplos.md`](06-exemplos.md), exemplo 11.

**Um backup que nunca foi restaurado não é um backup.** Teste a restauração ao menos uma vez
por trimestre.

---

## 6. Redis/Valkey

### 6.1 Conectar

```bash
redis-cli -u "$REDIS_URL"                    # sem TLS
redis-cli --tls -u "rediss://...:6379"       # com TLS (Upstash, Redis Cloud)
```

### 6.2 Comandos por tarefa

| Tarefa | Comando |
|---|---|
| Guardar com expiração | `SET chave valor EX 300` |
| Ler | `GET chave` |
| Contador | `INCR chave` / `INCRBY chave 5` |
| Expiração posterior | `EXPIRE chave 60` / ver com `TTL chave` |
| Apagar | `DEL chave` / `UNLINK chave` (assíncrono, melhor para chaves grandes) |
| Hash (objeto) | `HSET user:1 nome Ana idade 30` / `HGETALL user:1` |
| Lista/fila | `LPUSH fila item` / `BRPOP fila 0` |
| Conjunto | `SADD tags a b c` / `SMEMBERS tags` |
| Ordenado (ranking) | `ZADD placar 100 ana` / `ZREVRANGE placar 0 9 WITHSCORES` |
| Pub/sub | `SUBSCRIBE canal` / `PUBLISH canal msg` |
| Fila durável (moderno) | `XADD fluxo * campo valor` / `XREADGROUP ...` (Streams) |
| Trava distribuída | `SET trava token NX EX 30` (e libere só se o token bater — use Lua) |
| Uso de memória | `INFO memory` / `MEMORY USAGE chave` |
| Achar chaves | `SCAN 0 MATCH "user:*" COUNT 100` |

> ⚠️ **`KEYS *` é proibido em produção.** Ele varre todo o espaço de chaves e **bloqueia o
> servidor inteiro** (Redis é single-threaded para comandos). Use `SCAN`, que é incremental.
> Idem para `FLUSHALL` — apaga tudo, sem confirmação, sem volta.

### 6.3 Idioma de cache que você vai usar 90% das vezes

```
cache-aside (lazy loading):
  valor = GET chave
  se vazio:
      valor = consulta_no_banco()
      SET chave valor EX ttl
  retorna valor
```

Cuidados: **estampida** (mil requisições perdendo o cache ao mesmo tempo e batendo no banco
juntas — resolve-se com trava ou TTL aleatório) e **invalidação** (o dado mudou no banco e o
cache não sabe). Ambos em [`60-teoria-avancada.md`](60-teoria-avancada.md).

---

## 7. Domínio e TLS

```bash
# Render
# painel → Settings → Custom Domain → adicione → crie o CNAME que ele indicar

# Fly.io
flyctl certs add app.seudominio.com.br
flyctl certs show app.seudominio.com.br     # mostra o que falta no DNS

# Vercel
vercel domains add app.seudominio.com.br
vercel domains inspect app.seudominio.com.br

# Cloudflare Pages
npx wrangler pages deployment list
# domínio: painel → Custom domains (se o DNS já está na Cloudflare, é um clique)
```

Registros de DNS que você vai criar:

| Situação | Tipo | Valor |
|---|---|---|
| Subdomínio (`app.seudominio.com`) | `CNAME` | `seu-app.onrender.com` |
| Domínio raiz (`seudominio.com`) | `A` / `AAAA`, ou `ALIAS`/`ANAME` | IP da plataforma, ou o alias que ela indicar |
| Verificação de propriedade | `TXT` | valor fornecido pela plataforma |

Verificar antes de culpar a plataforma:

```bash
dig +short app.seudominio.com.br
# esperado: o CNAME/IP que você configurou
curl -sI https://app.seudominio.com.br | head -3
# esperado: HTTP/2 200
openssl s_client -connect app.seudominio.com.br:443 -servername app.seudominio.com.br </dev/null 2>/dev/null | openssl x509 -noout -dates
# esperado: notBefore/notAfter com validade futura
```

> **CNAME no domínio raiz é proibido pela RFC 1034** (o apex precisa conviver com registros
> `SOA` e `NS`). Por isso provedores inventaram `ALIAS`/`ANAME`/*CNAME flattening* — a
> Cloudflare faz isso automaticamente. É a razão de "no `www` funciona e no domínio puro não".

---

## 8. Rollback e histórico de deploy

| Plataforma | Como voltar |
|---|---|
| Render | painel → *Deploys* → deploy anterior → **Rollback** |
| Railway | painel → *Deployments* → *Redeploy* de uma versão anterior, ou `railway redeploy` |
| Fly.io | `flyctl releases` → `flyctl deploy --image <IMAGEM_ANTERIOR>` |
| Vercel | `vercel rollback <URL_DO_DEPLOY_ANTERIOR>` (ou *Promote to Production* no painel) |
| Cloudflare | `npx wrangler rollback [VERSION_ID]` |
| Git (universal) | `git revert <sha> && git push` — funciona em qualquer plataforma |

> **Opinião:** o rollback por `git revert` é o único que também conserta o repositório. O
> rollback do painel deixa o código quebrado no `main` — e alguém vai reimplantar por engano.
> Use o botão para parar a hemorragia **e** o revert para fechar a ferida.

**Migração de banco não faz rollback junto com o código.** Se o deploy que você reverteu
rodou uma migração destrutiva, voltar o código não traz a coluna de volta. É por isso que
migração compatível para trás não é preciosismo.

---

## 9. Escala e tamanho de instância

```bash
# Fly.io
flyctl scale count 2                    # duas instâncias
flyctl scale vm shared-cpu-2x --memory 1024
flyctl scale show

# Railway
railway scale --replicas 3

# Render / Koyeb / Northflank / Vercel: pelo painel ou pelo manifesto (§10)
```

Conceitos:

- **Escala vertical** (máquina maior): simples, com teto físico, e exige reinício.
- **Escala horizontal** (mais instâncias): sem teto prático, **exige que a aplicação seja
  stateless** — nada de guardar sessão em memória do processo. É aqui que o Redis deixa de
  ser opcional.
- **Escala a zero**: dorme sem tráfego. Ótimo para custo, ruim para latência (cold start).
- O **banco quase nunca escala horizontalmente para escrita**. Escrita é o gargalo final de
  toda arquitetura. Veja [`60`](60-teoria-avancada.md).

---

## 10. Infraestrutura como código

| Plataforma | Arquivo | Comando de validação |
|---|---|---|
| Render | `render.yaml` (*Blueprint*) | `render blueprints validate` |
| Fly.io | `fly.toml` | `flyctl config validate` |
| Railway | `railway.json` / `railway.toml` | — |
| Vercel | `vercel.json` | — |
| Cloudflare | `wrangler.toml` / `wrangler.jsonc` | `npx wrangler deploy --dry-run` |
| Docker (universal) | `Dockerfile` + `compose.yaml` | `docker compose config` |
| Multiplataforma | Terraform / OpenTofu / Pulumi | `terraform plan` |

Exemplo mínimo de `render.yaml` com as três peças (o do projeto-modelo é completo):

```yaml
# render.yaml — um único bloco `services` para TODOS os serviços (web e keyvalue),
# e um bloco `databases` separado para o PostgreSQL. Repetir a chave `services`
# é erro de YAML: a segunda ocorrência sobrescreve a primeira, silenciosamente.
services:
  - type: web
    name: api
    runtime: node
    plan: free
    buildCommand: npm ci
    startCommand: npm start
    healthCheckPath: /health
    envVars:
      - key: DATABASE_URL
        fromDatabase: { name: meu-banco, property: connectionString }
      - key: REDIS_URL
        fromService: { type: keyvalue, name: meu-cache, property: connectionString }

  - type: keyvalue
    name: meu-cache
    plan: free
    maxmemoryPolicy: allkeys-lru
    ipAllowList: []          # [] = acessível só pela rede interna do Render

databases:
  - name: meu-banco
    plan: free
```

> **Por que isso importa mais do que parece:** o painel web é ótimo para o primeiro dia e
> péssimo para o centésimo. Sem manifesto, a configuração de produção existe apenas na cabeça
> de quem clicou. É o principal motivo de "não conseguimos recriar o ambiente".

---

## 11. Shell no container e execução pontual

```bash
render ssh <SERVICE_ID>                 # não disponível no plano Free
railway ssh                              # shell no container
flyctl ssh console -a <NOME>            # shell na máquina
flyctl ssh console -C "node -e 'console.log(1+1)'"
docker exec -it <container> sh          # local
```

Rodar uma tarefa pontual (migração, seed, script de correção):

```bash
railway run npm run migrate             # roda LOCAL com as variáveis da nuvem
flyctl ssh console -C "npm run migrate" # roda DENTRO da máquina remota
```

> A diferença importa: `railway run` roda no **seu** computador com as credenciais de
> produção — ótimo para depurar, arriscado porque sua máquina passa a ter acesso ao banco de
> produção. `flyctl ssh console -C` roda **lá dentro**, na rede da plataforma.

---

## 12. CI/CD com GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: deploy
on:
  push: { branches: [main] }

jobs:
  test-and-deploy:
    runs-on: ubuntu-latest
    services:                              # Postgres e Redis efêmeros para o teste
      postgres:
        image: postgres:18
        env: { POSTGRES_PASSWORD: teste }
        options: >-
          --health-cmd pg_isready --health-interval 5s --health-timeout 5s --health-retries 10
        ports: ['5432:5432']
      redis:
        image: valkey/valkey:9
        ports: ['6379:6379']
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version-file: '.nvmrc', cache: 'npm' }
      - run: npm ci                        # NUNCA npm install em CI
      - run: npm test
        env:
          DATABASE_URL: postgresql://postgres:teste@localhost:5432/postgres
          REDIS_URL: redis://localhost:6379
      - name: deploy
        run: curl -fsS -X POST "$RENDER_DEPLOY_HOOK"
        env: { RENDER_DEPLOY_HOOK: '${{ secrets.RENDER_DEPLOY_HOOK }}' }
```

```bash
gh secret set RENDER_DEPLOY_HOOK --body "https://api.render.com/deploy/srv-xxx?key=yyy"
gh run list --limit 5
gh run watch
```

---

## 13. Obsoleto, e o que substituiu

| Obsoleto | Desde | Substituto |
|---|---|---|
| `docker-compose` (v1, Python) | jul/2023 (fim de suporte) | `docker compose` (plugin v2) |
| `heroku ps:scale web=0` como "free tier" | nov/2022 | Eco dynos (US$ 5) ou outra plataforma |
| Heroku free dynos / Postgres / Redis | 28/11/2022 | Render Free, Fly, Railway, Koyeb |
| ElephantSQL (Postgres gratuito clássico) | encerrado em jan/2025 | Neon, Supabase, Aiven |
| Xata "Lite" (free tier) | retirado em 28/02/2026 | Neon, Supabase, Prisma Postgres |
| Fly.io free allowances (3 VMs) | 2024 | pay-as-you-go; legado mantido para contas antigas |
| `vercel.json` com `builds` | ~2021 | detecção automática de framework |
| Cloudflare Workers "Bundled/Unbound" | 2023 | modelo *Standard* (requisições + CPU-ms) |
| Vercel `KV`/`Postgres` próprios | 2024–2025 | Marketplace: Upstash e Neon como parceiros |
| Redis sob SSPL/RSAL como "open source" | mar/2024 | Redis 8+ é tri-licenciado com **AGPLv3**; ou use **Valkey** (BSD) |
| `npm install` em pipeline de CI | — | `npm ci` |
| Sessão em memória do processo | — | Redis, ou cookie assinado/JWT |

---

## Autoteste

1. Qual comando você usa para ver quantas conexões abertas o seu PostgreSQL tem — e por que isso importa no plano gratuito?
2. Por que `KEYS *` é proibido em produção e o que se usa no lugar?
3. Qual a diferença prática entre `railway run` e `flyctl ssh console -C`?
4. O que é o padrão *expand/contract* em migrações e que desastre ele evita?
5. Por que não se pode criar um `CNAME` no domínio raiz, e como as plataformas contornam isso?
6. Você fez rollback pelo painel. Por que isso ainda não é suficiente?
7. Cite três coisas desta lista que ficaram obsoletas entre 2022 e 2026.
8. Onde os logs do seu plano gratuito ficam guardados, por quanto tempo, e o que fazer se você precisa deles depois?

---

### Fontes consultadas (18/08/2026)

- Documentação oficial de CLI: Render (v2.23.0), Railway, Fly.io, Vercel, Wrangler, Supabase, Neon
- PostgreSQL 18 — documentação de `psql`, `pg_dump`/`pg_restore`, catálogos `pg_stat_*`
- Redis/Valkey — referência de comandos
- RFC 1034 (por que CNAME não pode existir no apex)
