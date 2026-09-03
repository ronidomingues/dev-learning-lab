# 06 · Exemplos — 14 receitas completas e executáveis

`Nível: intermediário` · `Todo código é completo — nada de "..."` · `Última atualização: 11/08/2026`

Cada exemplo tem: **problema → solução → explicação**. Os quatro últimos são casos reais de
produção, não didáticos.

| # | Exemplo | Nível |
|---|---|---|
| [1](#1-banco-de-dados-descartável-para-testar-uma-consulta) | Banco descartável em 30 segundos | trivial |
| [2](#2-rodar-uma-ferramenta-sem-instalá-la) | Rodar ferramenta sem instalar | trivial |
| [3](#3-servir-um-site-estático) | Site estático com nginx | trivial |
| [4](#4-dockerfile-node-com-multi-stage-e-cache-eficiente) | Node multi-stage com cache | básico |
| [5](#5-python-com-uv-e-imagem-enxuta) | Python enxuto | básico |
| [6](#6-go-imagem-de-8-mb-com-scratch) | Go em imagem de 8 MB | intermediário |
| [7](#7-ambiente-de-desenvolvimento-com-recarga-automática) | Dev com recarga automática | intermediário |
| [8](#8-stack-completa-api--postgres--redis--nginx) | Stack completa com Compose | intermediário |
| [9](#9-migração-de-banco-antes-de-subir-a-api) | Migração antes do boot | intermediário |
| [10](#10-segredo-no-build-sem-vazar-na-imagem) | Segredo no build | avançado |
| [11](#11-build-multi-arquitetura-amd64--arm64) | Multi-arch amd64 + arm64 | avançado |
| [12](#12-produção--pipeline-de-ci-completo-no-github-actions) | **Produção:** CI/CD completo | avançado |
| [13](#13-produção--backup-automatizado-de-postgres-com-retenção) | **Produção:** backup com retenção | avançado |
| [14](#14-produção--proxy-reverso-com-tls-automático-para-vários-serviços) | **Produção:** proxy reverso com TLS | avançado |

---

## 1. Banco de dados descartável para testar uma consulta

**Problema:** você quer testar uma query em Postgres 16, mas não quer instalar Postgres na sua
máquina nem sujar o banco de desenvolvimento.

```bash
docker run --rm -d --name pg-teste \
  -e POSTGRES_PASSWORD=segredo \
  -e POSTGRES_DB=laboratorio \
  -p 127.0.0.1:5432:5432 \
  postgres:16-alpine

# Espere ficar pronto (o Postgres reinicia uma vez durante a inicialização)
until docker exec pg-teste pg_isready -U postgres > /dev/null 2>&1; do sleep 1; done
echo "pronto"

docker exec -it pg-teste psql -U postgres -d laboratorio -c "
  CREATE TABLE pedidos (id serial PRIMARY KEY, cliente text, valor numeric);
  INSERT INTO pedidos (cliente, valor) VALUES ('ana', 100), ('bruno', 250), ('ana', 75);
  SELECT cliente, sum(valor) AS total FROM pedidos GROUP BY cliente ORDER BY total DESC;
"

docker stop pg-teste     # --rm remove sozinho; não sobra nada
```

**Saída esperada:**
```
 cliente | total
---------+-------
 bruno   |   250
 ana     |   175
```

**Explicação.** `--rm` faz o container se autodestruir ao parar. Como **não** há volume,
os dados morrem junto — que é exatamente o desejado num laboratório. `127.0.0.1:5432:5432`
publica a porta apenas no loopback: sem isso, o banco ficaria visível para toda a rede local.
O laço com `pg_isready` existe porque a imagem do Postgres reinicia internamente durante a
primeira inicialização; conectar cedo demais dá "connection refused" enganoso.

---

## 2. Rodar uma ferramenta sem instalá-la

**Problema:** você precisa de `jq`, `imagemagick`, uma versão específica do Node, ou o
`awscli` — e não quer poluir a máquina.

```bash
# jq, sem instalar jq
echo '{"nome":"docker","ano":2013}' | docker run --rm -i ghcr.io/jqlang/jq '.nome'
# esperado: "docker"

# Redimensionar imagens com ImageMagick, sem instalar ImageMagick
docker run --rm -v "$PWD:/img" -w /img dpokidov/imagemagick \
  -resize 800x600 foto.jpg foto-menor.jpg

# Node 18 numa máquina onde só existe o Node 22
docker run --rm -it -v "$PWD:/app" -w /app node:18-alpine npm test

# Python 3.11 com as dependências do projeto, sem virtualenv
docker run --rm -it -v "$PWD:/app" -w /app python:3.11-slim \
  sh -c "pip install -q -r requirements.txt && python main.py"

# Escanear vulnerabilidades sem instalar o Trivy
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image minha-app:1.0
```

**Explicação.** Este é o uso do Docker que muda o dia a dia mais rápido do que qualquer outro:
a máquina fica limpa e cada ferramenta vem na versão exata. O padrão é sempre o mesmo:
`--rm` + `-v "$PWD:/app"` + `-w /app`.

**Armadilha:** arquivos criados por esses containers pertencem ao **root** do host, porque o
processo lá dentro roda como root. Corrija com `--user "$(id -u):$(id -g)"`:

```bash
docker run --rm --user "$(id -u):$(id -g)" -v "$PWD:/app" -w /app node:22-alpine npm init -y
ls -l package.json     # dono: você, não root
```

---

## 3. Servir um site estático

**Problema:** publicar uma pasta com HTML/CSS/JS.

`site/index.html`:
```html
<!doctype html>
<html lang="pt-BR">
  <head><meta charset="utf-8"><title>Meu site</title></head>
  <body><h1>Funcionando em container</h1></body>
</html>
```

**Modo rápido** (desenvolvimento, sem construir imagem):
```bash
docker run --rm -d --name site -p 8080:80 -v "$PWD/site:/usr/share/nginx/html:ro" nginx:alpine
curl -s localhost:8080 | grep h1
# esperado: <h1>Funcionando em container</h1>
docker stop site
```

**Modo imagem** (o que vai para produção):

`Dockerfile`:
```dockerfile
# syntax=docker/dockerfile:1
FROM nginx:1.27-alpine
COPY site/ /usr/share/nginx/html/
COPY nginx.conf /etc/nginx/conf.d/default.conf
HEALTHCHECK --interval=30s --timeout=3s CMD wget -qO- http://localhost/ || exit 1
```

`nginx.conf`:
```nginx
server {
    listen 80;
    root /usr/share/nginx/html;
    index index.html;

    gzip on;
    gzip_types text/css application/javascript application/json image/svg+xml;

    # SPA: qualquer rota desconhecida devolve o index.html
    location / { try_files $uri $uri/ /index.html; }

    # Assets com hash no nome podem ser cacheados para sempre
    location ~* \.(js|css|png|jpg|svg|woff2)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

```bash
docker build -t meu-site:1.0 .
docker run --rm -d --name site -p 8080:80 meu-site:1.0
curl -sI localhost:8080 | head -1     # esperado: HTTP/1.1 200 OK
docker stop site
```

**Explicação.** O bind mount com `:ro` serve para desenvolvimento — o conteúdo vem do host e
você vê a mudança na hora. A imagem serve para produção: o conteúdo está **dentro** dela, e por
isso é reproduzível e distribuível. Nunca dependa de bind mount em produção.

---

## 4. Dockerfile Node com multi-stage e cache eficiente

**Problema:** o build demora 4 minutos porque reinstala todas as dependências a cada mudança de
uma linha de código. E a imagem final tem 1,2 GB.

```dockerfile
# syntax=docker/dockerfile:1

# ---------- Estágio 1: dependências de produção ----------
FROM node:22-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN --mount=type=cache,target=/root/.npm \
    npm ci --omit=dev

# ---------- Estágio 2: build (precisa das devDependencies) ----------
FROM node:22-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN --mount=type=cache,target=/root/.npm \
    npm ci
COPY . .
RUN npm run build

# ---------- Estágio 3: imagem final ----------
FROM node:22-alpine AS production
ENV NODE_ENV=production
WORKDIR /app

RUN apk add --no-cache tini            # init de verdade: repassa sinais e colhe zumbis

COPY --from=deps  --chown=node:node /app/node_modules ./node_modules
COPY --from=build --chown=node:node /app/dist          ./dist
COPY --chown=node:node package.json ./

USER node
EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s \
  CMD wget -qO- http://localhost:3000/saude || exit 1

ENTRYPOINT ["/sbin/tini", "--"]
CMD ["node", "dist/server.js"]
```

`.dockerignore` — **tão importante quanto o Dockerfile**:
```
node_modules
dist
.git
.env
*.log
coverage
.vscode
Dockerfile
.dockerignore
README.md
```

```bash
docker build -t api:1.0 .
docker images api:1.0
# esperado: SIZE em torno de 150-200MB, contra ~1.2GB sem multi-stage
```

**Explicação — as quatro decisões que importam:**

1. **`COPY package*.json` antes de `COPY . .`.** O cache do Docker invalida uma camada e
   **todas as seguintes**. Copiando só o manifesto primeiro, o `npm ci` só refaz quando as
   dependências mudam de verdade. Sem isso, cada `git commit` custa 4 minutos.
2. **`--mount=type=cache`** mantém o cache do npm **entre builds diferentes**, sem que ele entre
   na imagem. É a diferença entre baixar da rede e ler do disco.
3. **Multi-stage.** As `devDependencies`, o compilador TypeScript e o código-fonte ficam no
   estágio de build e **não vão** para a imagem final — nem em camada escondida. Menos tamanho e
   menos superfície de ataque.
4. **`USER node` + `tini`.** Não rodar como root é higiene básica; o `tini` garante que
   `SIGTERM` chegue ao processo e que processos zumbis sejam colhidos.

---

## 5. Python com `uv` e imagem enxuta

**Problema:** imagem Python de 1 GB e `pip install` lento a cada build.

```dockerfile
# syntax=docker/dockerfile:1

FROM python:3.13-slim AS base
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# ---------- build ----------
FROM base AS build
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# ---------- runtime ----------
FROM base AS runtime
RUN useradd --create-home --uid 1000 app
WORKDIR /app
COPY --from=build --chown=app:app /app/.venv /app/.venv
COPY --chown=app:app src/ ./src/
ENV PATH="/app/.venv/bin:$PATH"
USER app
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s CMD python -c \
  "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://localhost:8000/saude').status==200 else 1)"
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Explicação.**
- `PYTHONUNBUFFERED=1` é **obrigatório** em container: sem ele, o Python bufferiza a saída e
  seus `print`/logs só aparecem quando o buffer enche — ou nunca, se o processo morre. Causa
  clássica de "meu container não tem logs".
- `python:3.13-slim` (~120 MB) contra `python:3.13` (~1 GB). Só use a variante completa se
  precisar compilar extensões C **em tempo de execução** — o que quase nunca é o caso.
- `uv` (escrito em Rust) resolve e instala dependências uma ordem de grandeza mais rápido que o
  `pip`. Copiado direto de uma imagem oficial, sem instalação.
- `--host 0.0.0.0` no uvicorn: com o padrão `127.0.0.1`, nada de fora do container o alcança.

---

## 6. Go: imagem de 8 MB com `scratch`

**Problema:** você quer a menor imagem possível e a menor superfície de ataque possível.

```dockerfile
# syntax=docker/dockerfile:1

FROM golang:1.23-alpine AS build
WORKDIR /src
COPY go.mod go.sum ./
RUN --mount=type=cache,target=/go/pkg/mod go mod download
COPY . .
RUN --mount=type=cache,target=/root/.cache/go-build \
    CGO_ENABLED=0 GOOS=linux go build -ldflags="-s -w" -o /app ./cmd/servidor

FROM scratch
# scratch é literalmente vazio: sem shell, sem libc, sem /etc/passwd
COPY --from=build /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/
COPY --from=build /app /app
USER 65534:65534         # nobody — precisa ser numérico: não há /etc/passwd para resolver nome
EXPOSE 8080
ENTRYPOINT ["/app"]
```

```bash
docker build -t servidor-go:1.0 .
docker images servidor-go:1.0
# esperado: SIZE entre 8MB e 15MB
```

**Explicação.**
- `CGO_ENABLED=0` produz um binário **estático**, sem depender da libc — pré-requisito para
  rodar em `scratch`.
- `-ldflags="-s -w"` remove tabela de símbolos e informação de debug: 20–30% menor.
- A cópia dos **certificados raiz** é obrigatória se o programa fizer HTTPS. Esquecer isso
  gera `x509: certificate signed by unknown authority` para qualquer site — erro que confunde
  porque parece problema de rede.
- `USER 65534:65534` precisa ser numérico, porque não existe `/etc/passwd` para traduzir
  `nobody`.

**Trade-off honesto:** em `scratch` você não tem shell, então `docker exec -it x sh` não
funciona e depurar em produção fica difícil. Alternativa equilibrada:
`gcr.io/distroless/static-debian12` — quase tão pequena, com certificados e usuário `nonroot`
já prontos, e uma variante `:debug` com shell para emergências.

---

## 7. Ambiente de desenvolvimento com recarga automática

**Problema:** você quer editar o código no seu editor e ver a mudança no container
imediatamente, sem reconstruir a imagem.

`compose.yaml`:
```yaml
services:
  api:
    build:
      context: .
      target: dev              # estágio dedicado, com as devDependencies
    ports:
      - "127.0.0.1:3000:3000"
      - "127.0.0.1:9229:9229"  # porta do depurador do Node
    environment:
      NODE_ENV: development
    volumes:
      - ./src:/app/src         # código do host, ao vivo
      - ./package.json:/app/package.json:ro
      - /app/node_modules      # ⚠️ volume anônimo: PROTEGE os node_modules da imagem
    command: ["node", "--watch", "--inspect=0.0.0.0:9229", "src/server.js"]
```

Estágio `dev` no `Dockerfile`:
```dockerfile
FROM node:22-alpine AS dev
WORKDIR /app
COPY package*.json ./
RUN npm ci                     # inclui devDependencies
COPY . .
CMD ["node", "--watch", "src/server.js"]
```

```bash
docker compose up
# edite src/server.js e salve → o Node reinicia sozinho, sem rebuild
```

**Explicação — a linha `- /app/node_modules` é a mais importante e a menos óbvia.**

Sem ela, se você tiver uma pasta `node_modules` no host (ou nenhuma), o bind mount de `./` a
cobriria e apagaria a que foi instalada na imagem — quebrando o container com
`Cannot find module`. Declarar `/app/node_modules` como **volume anônimo** faz o Docker montar
algo por cima daquele caminho, protegendo o conteúdo vindo da imagem.

Isso importa especialmente quando o host e o container têm arquiteturas ou sistemas
operacionais diferentes: pacotes com binários nativos (`bcrypt`, `sharp`, `sqlite3`) compilados
no macOS **não funcionam** dentro do container Linux.

**Alternativa moderna:** `docker compose watch` faz sincronização seletiva e declarativa, sem
bind mount de tudo:
```yaml
    develop:
      watch:
        - action: sync           # copia o arquivo para dentro
          path: ./src
          target: /app/src
        - action: rebuild        # mudou dependência → reconstrói a imagem
          path: package.json
```

---

## 8. Stack completa: API + Postgres + Redis + nginx

**Problema:** subir uma aplicação inteira com um comando, com ordem de inicialização correta,
rede isolada e o banco inacessível de fora.

`compose.yaml`:
```yaml
services:

  proxy:
    image: nginx:1.27-alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf:ro
    depends_on:
      api: { condition: service_healthy }
    networks: [publica, interna]
    restart: unless-stopped

  api:
    build: .
    environment:
      DATABASE_URL: postgres://app:${DB_SENHA:?defina DB_SENHA no .env}@db:5432/app
      REDIS_URL: redis://cache:6379
      NODE_ENV: production
    depends_on:
      db:    { condition: service_healthy }
      cache: { condition: service_healthy }
    healthcheck:
      test: ["CMD", "wget", "-qO-", "http://localhost:3000/saude"]
      interval: 10s
      timeout: 3s
      retries: 5
      start_period: 20s
    networks: [interna]          # NÃO está na rede pública: só o proxy a alcança
    restart: unless-stopped
    deploy:
      resources:
        limits: { memory: 512M, cpus: "1.0" }

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: app
      POSTGRES_PASSWORD: ${DB_SENHA:?defina DB_SENHA no .env}
      POSTGRES_DB: app
    volumes:
      - dados-db:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql:ro
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app -d app"]
      interval: 5s
      timeout: 3s
      retries: 10
    networks: [interna]
    restart: unless-stopped
    # SEM 'ports:' — o banco NÃO é acessível de fora da rede do Compose

  cache:
    image: redis:7-alpine
    command: ["redis-server", "--maxmemory", "256mb", "--maxmemory-policy", "allkeys-lru"]
    volumes:
      - dados-redis:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5
    networks: [interna]
    restart: unless-stopped

volumes:
  dados-db:
  dados-redis:

networks:
  publica:
  interna:
    internal: true               # esta rede não tem rota para a internet
```

`nginx.conf`:
```nginx
upstream api { server api:3000; }

server {
    listen 80;

    location / {
        proxy_pass http://api;
        proxy_set_header Host              $host;
        proxy_set_header X-Real-IP         $remote_addr;
        proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /saude { access_log off; proxy_pass http://api/saude; }
}
```

`.env` (e **`.env` no `.gitignore`**):
```bash
DB_SENHA=troque-esta-senha
```

```bash
docker compose up -d
docker compose ps        # todos "running", db e cache "(healthy)"
curl -s localhost/saude  # esperado: {"status":"ok"}
docker compose down      # volumes preservados
```

**Explicação — as cinco decisões de arquitetura:**

1. **Duas redes.** `publica` só tem o proxy; `interna` (com `internal: true`) não tem rota para
   a internet. Se a API for comprometida, o atacante não consegue nem exfiltrar dados por HTTP.
2. **O banco não tem `ports:`.** Só quem está na rede `interna` o alcança. Precisa acessar de
   fora para depurar? Use `docker compose exec db psql -U app`.
3. **`condition: service_healthy`** em vez de `depends_on` simples. Sem isso, a API tenta
   conectar num Postgres que ainda está inicializando e morre no primeiro segundo.
4. **`${DB_SENHA:?mensagem}`** faz o Compose **falhar imediatamente** se a variável não estiver
   definida, em vez de subir com senha vazia. Muito melhor que descobrir isso em produção.
5. **`start_period`** no healthcheck da API: durante a carência, falhas não contam como
   `unhealthy`. Sem isso, aplicações com boot lento entram em laço de reinício.

---

## 9. Migração de banco antes de subir a API

**Problema:** o esquema do banco precisa estar atualizado **antes** de a API começar a
responder, e a migração não pode rodar duas vezes em paralelo.

```yaml
services:
  migracao:
    build: .
    command: ["npm", "run", "migrate:up"]
    environment:
      DATABASE_URL: postgres://app:${DB_SENHA}@db:5432/app
    depends_on:
      db: { condition: service_healthy }
    restart: "no"                # roda uma vez e termina; NÃO reinicie
    networks: [interna]

  api:
    build: .
    depends_on:
      migracao: { condition: service_completed_successfully }
      db:       { condition: service_healthy }
    networks: [interna]
```

```bash
docker compose up -d
# ordem garantida: db saudável → migração termina com exit 0 → api sobe
docker compose logs migracao
```

**Explicação.** `service_completed_successfully` é a condição menos conhecida e mais útil do
`depends_on`: o serviço dependente só sobe se o container de migração terminar com **código de
saída 0**. Se a migração falhar, a API não sobe — que é o comportamento correto, porque uma API
contra esquema errado corrompe dados em silêncio.

**Anti-padrão comum a evitar:** rodar a migração no `ENTRYPOINT` da própria API. Com duas
réplicas, duas migrações concorrentes brigam pelo mesmo lock. Migração é um passo separado, e
idealmente um passo do *deploy*, não do boot.

---

## 10. Segredo no build sem vazar na imagem

**Problema:** o build precisa de um token (npm privado, repositório Git privado) e esse token
**não pode** ficar na imagem.

**❌ O jeito errado, que quase todo mundo faz primeiro:**
```dockerfile
ARG NPM_TOKEN
RUN echo "//registry.npmjs.org/:_authToken=${NPM_TOKEN}" > .npmrc && npm ci && rm .npmrc
```
Apagar o arquivo **não adianta**: a camada anterior, que o continha, permanece na imagem. Prove:
```bash
docker history --no-trunc IMAGEM | grep -i token     # o token está lá
docker save IMAGEM | tar -x -O | grep -a _authToken  # e no conteúdo das camadas, também
```

**✅ O jeito certo — `--mount=type=secret`:**
```dockerfile
# syntax=docker/dockerfile:1
FROM node:22-alpine AS build
WORKDIR /app
COPY package*.json ./

RUN --mount=type=secret,id=npmrc,target=/root/.npmrc,mode=0400 \
    --mount=type=cache,target=/root/.npm \
    npm ci --omit=dev

COPY . .
RUN npm run build
```

```bash
docker buildx build --secret id=npmrc,src=$HOME/.npmrc -t app:1.0 .

# Prova de que não vazou:
docker history --no-trunc app:1.0 | grep -ci token   # esperado: 0
```

**Para clonar um repositório Git privado:**
```dockerfile
RUN --mount=type=ssh \
    git clone git@github.com:org/repo-privado.git /app/vendor
```
```bash
docker buildx build --ssh default -t app:1.0 .
```

**Explicação.** O `--mount=type=secret` monta o arquivo num tmpfs que existe **só durante aquele
`RUN`**, e nunca vira camada. Já `ARG`/`--build-arg` fica gravado no histórico da imagem e é
recuperável por qualquer um que baixe a imagem — inclusive de um registry público. Isto é uma
das causas mais frequentes de vazamento de credencial em imagens públicas.

**Regra:** `ARG` para configuração (versão, arquitetura); `--mount=type=secret` para segredo.
**Nunca** o contrário.

---

## 11. Build multi-arquitetura (amd64 + arm64)

**Problema:** a equipe usa MacBook com Apple Silicon (ARM64) e o servidor é x86-64. Uma imagem
só precisa servir aos dois.

```bash
# Uma vez: cria um builder capaz de emular outras arquiteturas
docker buildx create --name multi --driver docker-container --bootstrap --use
docker buildx inspect --bootstrap | grep Platforms
# esperado: linux/amd64, linux/arm64, ... (a emulação vem via QEMU/binfmt)

docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t usuario/app:1.0 \
  --push .

# Verifique o manifest list gerado
docker buildx imagetools inspect usuario/app:1.0
# esperado: duas entradas, uma por plataforma
```

Para builds nativos rápidos, use `TARGETARCH` e evite a emulação na etapa cara:

```dockerfile
# syntax=docker/dockerfile:1
FROM --platform=$BUILDPLATFORM golang:1.23-alpine AS build
ARG TARGETOS TARGETARCH
WORKDIR /src
COPY . .
# compila NATIVAMENTE para o alvo — cross-compilação, sem QEMU
RUN CGO_ENABLED=0 GOOS=$TARGETOS GOARCH=$TARGETARCH go build -o /app ./cmd/servidor

FROM alpine:3.20
COPY --from=build /app /app
ENTRYPOINT ["/app"]
```

**Explicação.** `--platform=$BUILDPLATFORM` no estágio de build significa "compile na
arquitetura **da máquina que está construindo**", e `GOARCH=$TARGETARCH` gera o binário para a
arquitetura **de destino**. Isso troca emulação QEMU (lenta, às vezes 10× mais) por
cross-compilação nativa. Linguagens que cross-compilam bem (Go, Rust, Zig) ganham muito com
esse padrão; linguagens interpretadas, nem tanto.

**Armadilha:** builds ARM64 emulados de projetos Node/Python com dependências nativas podem
levar **20+ minutos** ou simplesmente falhar. Se puder, use runners nativos de cada arquitetura
no CI e junte os manifests no fim (`docker buildx imagetools create`).

---

## 12. PRODUÇÃO — pipeline de CI completo no GitHub Actions

**Problema real:** a cada push na `main`, construir a imagem multi-arch, escanear
vulnerabilidades, gerar SBOM, assinar, publicar no GHCR e fazer o deploy — falhando o pipeline
se houver vulnerabilidade crítica.

`.github/workflows/build.yml`:
```yaml
name: build-e-publica

on:
  push:
    branches: [main]
    tags: ['v*']
  pull_request:

env:
  REGISTRY: ghcr.io
  IMAGEM: ${{ github.repository }}

jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
      id-token: write          # necessário para assinatura keyless com cosign
      security-events: write   # para enviar o relatório ao GitHub Security

    steps:
      - uses: actions/checkout@v4

      - name: Configura QEMU (emulação para arm64)
        uses: docker/setup-qemu-action@v3

      - name: Configura Buildx
        uses: docker/setup-buildx-action@v3

      - name: Login no GHCR
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Calcula tags e labels
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGEM }}
          tags: |
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}
            type=sha,format=long
            type=ref,event=branch

      - name: Constrói e publica
        id: build
        uses: docker/build-push-action@v6
        with:
          context: .
          platforms: linux/amd64,linux/arm64
          push: ${{ github.event_name != 'pull_request' }}
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
          provenance: true      # atestado SLSA de proveniência
          sbom: true            # lista de materiais de software

      - name: Escaneia vulnerabilidades
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: ${{ env.REGISTRY }}/${{ env.IMAGEM }}:sha-${{ github.sha }}
          format: sarif
          output: trivy.sarif
          severity: CRITICAL,HIGH
          exit-code: '1'        # falha o pipeline se houver CRITICAL ou HIGH
          ignore-unfixed: true  # não falhe por CVE sem correção disponível

      - name: Envia o relatório para o GitHub Security
        if: always()
        uses: github/codeql-action/upload-sarif@v3
        with: { sarif_file: trivy.sarif }

      - name: Instala cosign
        if: github.event_name != 'pull_request'
        uses: sigstore/cosign-installer@v3

      - name: Assina a imagem (keyless, via OIDC)
        if: github.event_name != 'pull_request'
        run: |
          cosign sign --yes \
            ${{ env.REGISTRY }}/${{ env.IMAGEM }}@${{ steps.build.outputs.digest }}
```

Deploy no servidor, verificando a assinatura antes de subir:

```bash
#!/usr/bin/env bash
# deploy.sh — executado no servidor
set -euo pipefail

IMAGEM="ghcr.io/org/app"
DIGEST="$1"                      # passado pelo pipeline

cosign verify "${IMAGEM}@${DIGEST}" \
  --certificate-identity-regexp "https://github.com/org/app/.github/workflows/.*" \
  --certificate-oidc-issuer "https://token.actions.githubusercontent.com" > /dev/null

echo "IMAGEM=${IMAGEM}@${DIGEST}" > /opt/app/.env
docker compose -f /opt/app/compose.yaml pull
docker compose -f /opt/app/compose.yaml up -d --wait   # --wait espera ficar healthy
docker image prune -af --filter "until=168h"
```

**Explicação — por que cada peça está aí:**

- **`cache-from/to: type=gha`** usa o cache do GitHub Actions entre execuções. Build de 6
  minutos cai para menos de 1 em mudanças pequenas.
- **`ignore-unfixed: true`** no Trivy é pragmatismo: falhar o pipeline por uma CVE sem correção
  publicada apenas ensina a equipe a ignorar o scanner.
- **`provenance` e `sbom`** geram atestados anexados à imagem no registry — cada vez mais
  exigidos por política de conformidade (e pelo *EU Cyber Resilience Act*).
- **Assinatura keyless com cosign** usa OIDC do próprio GitHub: **não há chave privada para
  vazar**. A verificação no deploy garante que a imagem foi construída por aquele workflow
  daquele repositório, e não empurrada à mão por alguém.
- **Deploy por digest, não por tag.** Tag é mutável; digest é o hash do conteúdo. Deploy por tag
  é como fazer deploy de "a versão que estiver lá quando o servidor puxar".
- **`--wait`** no `compose up` faz o comando retornar somente quando os healthchecks passarem —
  transformando um deploy silenciosamente quebrado em um deploy que falha alto.

---

## 13. PRODUÇÃO — backup automatizado de Postgres com retenção

**Problema real:** backup diário do banco, com retenção de 7 diários + 4 semanais, enviado para
armazenamento externo, com verificação de que o dump não está corrompido.

`compose.yaml` (trecho):
```yaml
  backup:
    image: postgres:16-alpine
    depends_on:
      db: { condition: service_healthy }
    environment:
      PGPASSWORD: ${DB_SENHA:?}
    volumes:
      - ./backups:/backups
      - ./backup.sh:/backup.sh:ro
    entrypoint: ["/bin/sh", "/backup.sh"]
    networks: [interna]
    restart: unless-stopped
```

`backup.sh`:
```sh
#!/bin/sh
# Backup do Postgres com retenção. Roda em laço; sem cron, sem daemon extra.
set -eu

DESTINO=/backups
RETENCAO_DIARIA=7
RETENCAO_SEMANAL=4
INTERVALO=86400        # 24h

mkdir -p "$DESTINO/diario" "$DESTINO/semanal"

fazer_backup() {
    carimbo=$(date +%Y-%m-%d_%H%M%S)
    arquivo="$DESTINO/diario/app_${carimbo}.sql.gz"

    echo "[$(date -Iseconds)] iniciando backup -> $arquivo"

    # -Fc seria o formato custom; usamos SQL puro comprimido por ser mais portátil
    if ! pg_dump -h db -U app -d app --no-owner --no-acl | gzip -9 > "$arquivo.parcial"; then
        echo "[$(date -Iseconds)] ERRO: pg_dump falhou" >&2
        rm -f "$arquivo.parcial"
        return 1
    fi

    # Verificação: o gzip está íntegro e o dump não está vazio?
    if ! gzip -t "$arquivo.parcial"; then
        echo "[$(date -Iseconds)] ERRO: arquivo corrompido" >&2
        rm -f "$arquivo.parcial"
        return 1
    fi
    tamanho=$(wc -c < "$arquivo.parcial")
    if [ "$tamanho" -lt 1024 ]; then
        echo "[$(date -Iseconds)] ERRO: dump suspeito de vazio (${tamanho} bytes)" >&2
        rm -f "$arquivo.parcial"
        return 1
    fi

    # Só agora vira definitivo — evita backup pela metade sendo tomado por válido
    mv "$arquivo.parcial" "$arquivo"
    echo "[$(date -Iseconds)] ok: $(du -h "$arquivo" | cut -f1)"

    # Domingo vira backup semanal
    if [ "$(date +%u)" = "7" ]; then
        cp "$arquivo" "$DESTINO/semanal/"
    fi

    # Retenção
    ls -1t "$DESTINO/diario"/*.sql.gz  2>/dev/null | tail -n +$((RETENCAO_DIARIA + 1))  | xargs -r rm -f
    ls -1t "$DESTINO/semanal"/*.sql.gz 2>/dev/null | tail -n +$((RETENCAO_SEMANAL + 1)) | xargs -r rm -f
}

# Encerramento limpo quando o container for parado
trap 'echo "encerrando"; exit 0' TERM INT

while true; do
    fazer_backup || echo "[$(date -Iseconds)] backup falhou; tentarei de novo no próximo ciclo" >&2
    sleep "$INTERVALO" &
    wait $!            # 'wait' permite que o trap interrompa o sleep imediatamente
done
```

Teste de restauração — **um backup nunca testado não é um backup**:
```bash
# Sobe um Postgres limpo e restaura o dump mais recente
docker run --rm -d --name pg-restauracao -e POSTGRES_PASSWORD=x -e POSTGRES_DB=app postgres:16-alpine
until docker exec pg-restauracao pg_isready -U postgres >/dev/null 2>&1; do sleep 1; done

gunzip -c ./backups/diario/$(ls -1t ./backups/diario | head -1) \
  | docker exec -i pg-restauracao psql -U postgres -d app

docker exec pg-restauracao psql -U postgres -d app -c "\dt"       # as tabelas voltaram?
docker exec pg-restauracao psql -U postgres -d app -c "SELECT count(*) FROM pedidos;"
docker stop pg-restauracao
```

**Explicação — as decisões que separam backup de teatro de backup:**

1. **Escreve em `.parcial` e só depois renomeia.** Se o processo morrer no meio, não fica um
   arquivo truncado parecendo válido. `mv` no mesmo sistema de arquivos é atômico.
2. **Verifica integridade e tamanho mínimo.** Um `pg_dump` que falha por autenticação pode
   produzir um `.gz` válido de 20 bytes. Sem a checagem de tamanho, o alarme só toca no dia do
   desastre.
3. **`pg_dump`, não cópia de arquivo.** Copiar `/var/lib/postgresql/data` com o banco rodando
   captura um estado inconsistente que pode não restaurar.
4. **`trap` + `wait $!`** fazem o `docker stop` funcionar em menos de um segundo, em vez de
   esperar o `sleep` de 24h ser morto à força.
5. **O teste de restauração é parte do procedimento**, não uma boa intenção. A regra 3-2-1
   (3 cópias, 2 mídias, 1 fora do local) exige ainda enviar esses arquivos para fora do
   servidor — `rclone`, `restic` ou `aws s3 sync` num segundo container.

---

## 14. PRODUÇÃO — proxy reverso com TLS automático para vários serviços

**Problema real:** vários serviços em um servidor, cada um num subdomínio, todos com HTTPS
válido e renovação automática, sem editar configuração de nginx a cada serviço novo.

`compose.yaml`:
```yaml
services:

  caddy:
    image: caddy:2-alpine
    ports:
      - "80:80"
      - "443:443"
      - "443:443/udp"          # HTTP/3
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile:ro
      - caddy-dados:/data      # ⚠️ os certificados vivem AQUI. Perder = re-emitir tudo
      - caddy-config:/config
    networks: [borda]
    restart: unless-stopped

  app:
    image: ghcr.io/org/app:1.4.2
    environment:
      DATABASE_URL: postgres://app:${DB_SENHA:?}@db:5432/app
    depends_on:
      db: { condition: service_healthy }
    networks: [borda, interna]
    restart: unless-stopped
    deploy:
      replicas: 2              # o Caddy balanceia entre as réplicas via DNS
      resources:
        limits: { memory: 512M }

  painel:
    image: grafana/grafana:11.1.0
    environment:
      GF_SERVER_ROOT_URL: https://painel.exemplo.com
      GF_AUTH_ANONYMOUS_ENABLED: "false"
    volumes:
      - grafana-dados:/var/lib/grafana
    networks: [borda]
    restart: unless-stopped

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: app
      POSTGRES_PASSWORD: ${DB_SENHA:?}
      POSTGRES_DB: app
    volumes:
      - dados-db:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app"]
      interval: 5s
      retries: 10
    networks: [interna]
    restart: unless-stopped

volumes:
  caddy-dados:
  caddy-config:
  grafana-dados:
  dados-db:

networks:
  borda:
  interna:
    internal: true
```

`Caddyfile`:
```caddyfile
{
    email admin@exemplo.com     # usado pelo Let's Encrypt para avisos de expiração
}

app.exemplo.com {
    reverse_proxy app:3000 {
        health_uri      /saude
        health_interval 10s
        lb_policy       round_robin
    }
    encode gzip zstd
    header {
        Strict-Transport-Security "max-age=31536000; includeSubDomains"
        X-Content-Type-Options    "nosniff"
        X-Frame-Options           "DENY"
        Referrer-Policy           "strict-origin-when-cross-origin"
        -Server
    }
    log {
        output file /data/access.log {
            roll_size 10mb
            roll_keep 5
        }
    }
}

painel.exemplo.com {
    # Restringe o painel à VPN/rede interna, mesmo com certificado público
    @externo not remote_ip 10.0.0.0/8 192.168.0.0/16
    respond @externo "acesso restrito" 403
    reverse_proxy painel:3000
}
```

```bash
docker compose up -d
docker compose logs caddy | grep -i certificate
# esperado: linhas indicando a obtenção do certificado junto ao Let's Encrypt
curl -sI https://app.exemplo.com | head -1     # HTTP/2 200
```

**Explicação.**

- **Caddy em vez de nginx + certbot** elimina a peça mais frágil da operação: o certificado é
  obtido e renovado automaticamente via ACME, sem cron, sem hook, sem "esqueci de renovar".
  *Opinião profissional:* para 90% dos casos de proxy reverso caseiro ou de pequena empresa,
  Caddy custa menos operação que nginx. nginx ainda ganha em ajuste fino e em carga muito alta.
- **`caddy-dados` é o volume mais crítico da stack.** É onde ficam as chaves e certificados.
  Recriar o container sem esse volume força re-emissão, e o Let's Encrypt tem limite de 5
  certificados idênticos por semana — dá para se auto-bloquear.
- **`replicas: 2` + DNS.** O Docker resolve `app` para os IPs das duas réplicas; o Caddy
  balanceia com verificação de saúde e tira do rodízio a réplica que falhar.
- **`443:443/udp`** habilita HTTP/3 (QUIC), que roda sobre UDP. Esquecer essa linha faz o HTTP/3
  simplesmente não funcionar, sem erro visível.
- **Rede `interna: true`** para o banco: nem o Caddy o alcança. Só a `app` está nas duas redes.

---

## Autoteste

1. Por que copiar `package.json` antes de `COPY . .` reduz o tempo de build em 90%?
2. O que a linha `- /app/node_modules` num Compose faz, e o que quebra sem ela?
3. Você usou `--build-arg TOKEN=xyz`. Como provar em dois comandos que o token vazou na imagem?
4. Qual é a diferença entre `depends_on: condition: service_started`, `service_healthy` e
   `service_completed_successfully`?
5. Uma imagem `scratch` com um binário Go falha ao chamar uma API HTTPS. O que faltou copiar?
6. Por que `PYTHONUNBUFFERED=1` é praticamente obrigatório em container Python?
7. No exemplo 13, por que o dump é escrito em `.parcial` e só depois renomeado?
8. Por que fazer deploy por digest é diferente de fazer deploy por tag, e por que isso importa?
9. No exemplo 14, qual volume é o mais crítico e o que acontece se você o perder?
10. `--platform=$BUILDPLATFORM` no estágio de build: o que ele evita, e para quais linguagens
    esse ganho é maior?
