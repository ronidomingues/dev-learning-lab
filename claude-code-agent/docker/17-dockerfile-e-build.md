# 17 · Dockerfile e build — do texto à imagem

`Nível: intermediário → avançado` · `Última atualização: 11/08/2026`

O Dockerfile parece simples e é onde mais se erra. Este arquivo é o guia de escrita, com o
porquê de cada regra.

---

## 1. A anatomia de um Dockerfile de produção

```dockerfile
# syntax=docker/dockerfile:1
# ↑ Frontend do BuildKit. Baixa a versão mais recente do parser, dando acesso a recursos novos
#   sem atualizar o Docker. Coloque SEMPRE, e sempre na primeira linha.

ARG NODE_VERSION=22.4.0
# ↑ ARG antes do primeiro FROM é "global": só pode ser usado em linhas FROM.

FROM node:${NODE_VERSION}-alpine AS build
WORKDIR /app

# Menos volátil primeiro: manifesto de dependências
COPY package.json package-lock.json ./
RUN --mount=type=cache,target=/root/.npm npm ci

# Mais volátil depois: o código
COPY . .
RUN npm run build

FROM node:${NODE_VERSION}-alpine AS producao
# ↑ ARG global precisa ser redeclarado dentro do estágio para valer nas outras instruções

ENV NODE_ENV=production
WORKDIR /app

RUN apk add --no-cache tini

COPY --from=build --chown=node:node /app/dist ./dist
COPY --from=build --chown=node:node /app/node_modules ./node_modules
COPY --chown=node:node package.json ./

USER node
EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=3s --start-period=15s --retries=3 \
  CMD wget -qO- http://127.0.0.1:3000/saude || exit 1
STOPSIGNAL SIGTERM
ENTRYPOINT ["/sbin/tini", "--"]
CMD ["node", "dist/server.js"]
```

---

## 2. As armadilhas de escrita, uma a uma

### `ADD` vs `COPY`

`ADD` faz três coisas: copia, **extrai automaticamente arquivos tar** e **baixa URLs**. Essa
implicitude é o problema:

```dockerfile
ADD app.tar.gz /app/     # extrai — pode ser o que você quer, ou uma surpresa
COPY app.tar.gz /app/    # copia o arquivo, ponto
```

Um `ADD arquivo.tar /dest` que você achava que copiava passa a extrair quando alguém renomeia o
arquivo. **Use `COPY` sempre**, salvo o caso legítimo de extrair um tar local — e aí escreva um
comentário explicando.

Para baixar URL, `ADD` não valida checksum por padrão e cria uma camada difícil de auditar:

```dockerfile
# ✅ explícito, verificável, e limpa na mesma camada
RUN curl -fsSL -o /tmp/x.tgz https://exemplo.com/x.tgz \
 && echo "abc123...  /tmp/x.tgz" | sha256sum -c - \
 && tar xzf /tmp/x.tgz -C /opt \
 && rm /tmp/x.tgz
```

### `ARG` vs `ENV`

| | `ARG` | `ENV` |
|---|---|---|
| Existe durante | Só o build | Build **e** execução |
| Visível no container | não | sim |
| No `docker inspect` | não diretamente | **sim** |
| No histórico da imagem | **sim** | sim |
| Serve para segredo? | **NÃO** | **NÃO** |

```dockerfile
ARG VERSAO=1.0          # configuração de build
ENV APP_VERSAO=$VERSAO  # promovido para o runtime, se você quiser
```

Ambos ficam registrados. Segredo → `--mount=type=secret`.

### `CMD` vs `ENTRYPOINT`, e as formas exec/shell

```dockerfile
CMD ["node", "app.js"]     # ✅ forma EXEC: o node vira PID 1
CMD node app.js            # ❌ forma SHELL: vira ["/bin/sh","-c","node app.js"]
```

Na forma shell, o `/bin/sh` é o PID 1 e **não repassa sinais**. `docker stop` demora 10 s e mata
o processo à força. Em produção, isso é 502 no usuário a cada deploy.

| Dockerfile | `docker run img` | `docker run img echo oi` |
|---|---|---|
| `CMD ["node","app.js"]` | `node app.js` | `echo oi` (substitui) |
| `ENTRYPOINT ["node"]` | `node` | `node echo oi` (acrescenta) |
| `ENTRYPOINT ["node"]` + `CMD ["app.js"]` | `node app.js` | `node echo oi` |

**Regra:** `ENTRYPOINT` = o que a imagem **é**; `CMD` = o argumento **padrão**.

Quando precisar de expansão de variável no comando, use um entrypoint script — não a forma
shell:

```bash
#!/bin/sh
set -e
# Aqui a expansão funciona, e o 'exec' faz o app HERDAR o PID 1.
exec node --max-old-space-size="${HEAP_MB:-512}" dist/server.js
```
O `exec` é essencial: sem ele, o shell continua como PID 1 e o problema dos sinais volta.

### `EXPOSE` não expõe nada

É documentação (e afeta `-P` e alguns orquestradores). Quem publica porta é `-p` no `run` ou
`ports:` no Compose. Nunca conte com `EXPOSE` para acessibilidade.

### `WORKDIR`, não `RUN cd`

```dockerfile
RUN cd /app && npm ci     # ❌ o cd não persiste para a próxima instrução
WORKDIR /app              # ✅ persiste, e cria o diretório se não existir
RUN npm ci
```

### `USER` — sempre, e antes do `CMD`

```dockerfile
# Alpine
RUN addgroup -S app && adduser -S -G app app
# Debian/Ubuntu
RUN groupadd -r app && useradd -r -g app app

USER app
```

Não rodar como root não impede toda exploração, mas elimina uma classe inteira: escrita em
caminhos do sistema, uso de capabilities herdadas, escrita no volume com dono errado.

### `HEALTHCHECK` que vale a pena

```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --start-period=15s --retries=3 \
  CMD wget -qO- http://127.0.0.1:3000/saude || exit 1
```

| Parâmetro | Significado |
|---|---|
| `interval` | De quanto em quanto tempo testar |
| `timeout` | Quanto esperar por resposta |
| `start-period` | **Carência inicial**: falhas aqui não contam |
| `retries` | Falhas consecutivas até marcar `unhealthy` |

Sem `start-period`, aplicação de boot lento entra em laço de reinício. E o teste deve **exercitar
a dependência real** (banco, disco), não devolver 200 fixo — healthcheck otimista é pior que
nenhum.

---

## 3. O cache, na prática

Ver [12-imagens-e-camadas.md](12-imagens-e-camadas.md) para o mecanismo. Aqui, os padrões.

### A ordem canônica

```dockerfile
FROM base                              # 1. muda raramente
RUN apk add --no-cache ferramentas     # 2. muda raramente
COPY package.json package-lock.json ./ # 3. muda quando dependências mudam
RUN npm ci                             # 4. idem
COPY . .                               # 5. muda a cada commit
RUN npm run build                      # 6. idem
```

### Cache montado por ecossistema

```dockerfile
# Node
RUN --mount=type=cache,target=/root/.npm npm ci

# Python (pip)
RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements.txt

# Python (uv)
RUN --mount=type=cache,target=/root/.cache/uv uv sync --frozen

# Go
RUN --mount=type=cache,target=/go/pkg/mod \
    --mount=type=cache,target=/root/.cache/go-build go build ./...

# Rust
RUN --mount=type=cache,target=/usr/local/cargo/registry \
    --mount=type=cache,target=/app/target cargo build --release

# Maven
RUN --mount=type=cache,target=/root/.m2 mvn -q package -DskipTests

# apt (exige desligar a limpeza automática do apt)
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    rm -f /etc/apt/apt.conf.d/docker-clean && apt-get update \
 && apt-get install -y --no-install-recommends curl
```

> **Atenção com Rust:** o cache de `/app/target` acelera muito, **mas o binário fica no cache,
> não na camada**. É preciso copiá-lo para fora dentro do mesmo `RUN`:
> `cargo build --release && cp target/release/app /app/bin`.

### Cache em CI

```bash
# GitHub Actions
--cache-from type=gha --cache-to type=gha,mode=max
# Registry (funciona em qualquer CI)
--cache-from type=registry,ref=usuario/app:cache \
--cache-to   type=registry,ref=usuario/app:cache,mode=max
```

---

## 4. `.dockerignore` — o arquivo que quase ninguém escreve direito

Ele determina **o que é enviado ao daemon** como contexto de build. Sem ele:

- o build fica lento (enviar `node_modules` e `.git` custa segundos ou minutos);
- o cache é invalidado por arquivo irrelevante;
- **segredos entram na imagem** via `COPY . .`.

```
.git
.github
node_modules
dist
build
coverage
*.log
.env
.env.*
!.env.example
*.pem
*.key
.npmrc
.netrc
.DS_Store
.vscode
.idea
Dockerfile*
compose*.yaml
README.md
docs/
```

Verifique o tamanho real do que está sendo enviado:

```bash
docker build --progress=plain -t x . 2>&1 | grep -i "transferring context"
# esperado: alguns MB. Se aparecer "500MB", falta .dockerignore
```

---

## 5. Multi-stage: cinco padrões úteis

### (a) Compilar e descartar o toolchain
```dockerfile
FROM golang:1.23-alpine AS build
WORKDIR /src
COPY . .
RUN CGO_ENABLED=0 go build -ldflags="-s -w" -o /app ./cmd/api

FROM gcr.io/distroless/static-debian12
COPY --from=build /app /app
USER nonroot:nonroot
ENTRYPOINT ["/app"]
```

### (b) Separar dependências de produção e de desenvolvimento
```dockerfile
FROM node:22-alpine AS deps-prod
COPY package*.json ./
RUN npm ci --omit=dev

FROM node:22-alpine AS build
COPY package*.json ./
RUN npm ci                 # com devDependencies
COPY . .
RUN npm run build

FROM node:22-alpine
COPY --from=deps-prod /node_modules ./node_modules
COPY --from=build /dist ./dist
```

### (c) Testes como portão de qualidade
```dockerfile
FROM build AS testes
RUN npm run lint && npm test
# `docker build --target testes .` falha se algo quebrar
```

### (d) Estágios paralelos
O BuildKit executa estágios independentes **ao mesmo tempo**:
```dockerfile
FROM node:22 AS frontend
RUN npm run build:web

FROM golang:1.23 AS backend
RUN go build -o /api

FROM alpine
COPY --from=frontend /app/dist /www
COPY --from=backend /api /api
```
Os dois primeiros estágios rodam em paralelo, sem que você faça nada.

### (e) Base comum
```dockerfile
FROM python:3.13-slim AS base
ENV PYTHONUNBUFFERED=1
RUN useradd -m app

FROM base AS dev
RUN pip install -r requirements-dev.txt
FROM base AS producao
RUN pip install -r requirements.txt
```

---

## 6. Escolha da imagem base — o quadro de decisão

```
Seu app compila para binário estático (Go, Rust, Zig, C estático)?
├── SIM → distroless/static ou scratch          (2-10 MB)
└── NÃO
     ├── Precisa de glibc? (Python com wheels, extensões nativas, Oracle client)
     │    ├── SIM → debian:12-slim ou distroless com runtime  (~80 MB)
     │    └── NÃO → alpine                                     (~8 MB)
     └── É uma linguagem com runtime oficial? (Node, Python, Java, Ruby)
          └── Use a imagem oficial na variante -alpine ou -slim
```

Ressalvas por linguagem:

| Linguagem | Recomendação | Motivo |
|---|---|---|
| **Go / Rust** | `scratch` ou `distroless/static` | Binário estático; nada mais é necessário |
| **Node** | `node:22-alpine` | O runtime vem junto; musl não é problema |
| **Python** | `python:3.13-slim` (**não** alpine) | Wheels `manylinux` exigem glibc; alpine força compilar do fonte |
| **Java** | `eclipse-temurin:21-jre-alpine` ou imagem com `jlink` | Use o **JRE**, não o JDK; `jlink` gera runtime sob medida |
| **Ruby / PHP** | `-slim` | Extensões nativas, mesma razão do Python |
| **.NET** | `mcr.microsoft.com/dotnet/aspnet:8.0-alpine` | Runtime, não SDK |

---

## 7. Reprodutibilidade

Um build reproduzível produz o **mesmo digest** a partir da mesma entrada. Na prática, isso é
difícil — mas dá para chegar perto:

| Fonte de variação | Como controlar |
|---|---|
| Tag da imagem base | Fixe com digest: `FROM node:22.4.0-alpine@sha256:...` |
| Versões de pacote | `apt-get install curl=8.5.0-2` · lockfiles |
| Timestamps nas camadas | `SOURCE_DATE_EPOCH` (suportado pelo BuildKit) |
| Ordem de arquivos | Naturalmente estável no `COPY` |
| Downloads da internet | Verifique checksum; prefira espelho interno |
| `latest` em qualquer lugar | Nunca use |

```bash
SOURCE_DATE_EPOCH=$(git log -1 --pretty=%ct) \
  docker buildx build --output type=image,rewrite-timestamp=true -t app:1.0 .
```

---

## 8. Linting e verificação

```bash
# hadolint — o linter de Dockerfile
docker run --rm -i hadolint/hadolint < Dockerfile

# BuildKit tem verificações embutidas
docker buildx build --check .

# Escanear a imagem resultante
docker scout cves minha-app:1.0
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy image minha-app:1.0
```

As advertências do `hadolint` que mais valem a pena:

| Código | O que diz |
|---|---|
| DL3006 | Fixe a tag da imagem base |
| DL3008 | Fixe a versão dos pacotes do apt |
| DL3009 | Limpe o cache do apt na mesma camada |
| DL3015 | Use `--no-install-recommends` |
| DL3025 | Use a forma exec em `CMD`/`ENTRYPOINT` |
| DL3002 | Não termine com `USER root` |

---

## 9. Erros de build e o que significam

| Mensagem | Causa | Correção |
|---|---|---|
| `COPY failed: file not found in build context` | O arquivo está fora do contexto ou no `.dockerignore` | Confira o `.` do `docker build` e o ignore |
| `failed to solve: process "/bin/sh -c apt-get update" did not complete` | Sem rede/DNS/proxy no build | Configure `proxies` em `~/.docker/config.json` |
| `404 Not Found` em `apt-get install` | Índice do `apt-get update` veio do cache | `update && install` na mesma camada |
| `exec format error` ao rodar | Arquitetura errada | `--platform`, ou build multi-arch |
| `no such file or directory` para um arquivo que existe | CRLF no script, ou binário dinâmico em `scratch` | `dos2unix`; `CGO_ENABLED=0` |
| `unable to prepare context: path not found` | Caminho do contexto errado | Verifique o último argumento do `build` |
| `Error: EACCES: permission denied` no `npm ci` | `USER` trocado antes do `COPY` | Troque de usuário **depois** das cópias |
| Build "trava" no `transferring context` | Contexto enorme | `.dockerignore` |

Depure com log completo:
```bash
docker buildx build --progress=plain --no-cache -t x . 2>&1 | tee build.log
```

E entre no estágio que falhou:
```bash
docker build --target build -t depurar .
docker run --rm -it depurar sh
```

---

## 10. Checklist de Dockerfile de produção

- [ ] `# syntax=docker/dockerfile:1` na primeira linha
- [ ] Imagem base fixada por tag específica (idealmente com digest)
- [ ] Multi-stage: nenhum toolchain na imagem final
- [ ] `.dockerignore` presente e cobrindo `.git`, `node_modules`, `.env`, chaves
- [ ] `COPY` do manifesto de dependências antes do `COPY` do código
- [ ] `--mount=type=cache` nos gerenciadores de pacote
- [ ] `--mount=type=secret` para qualquer credencial; nenhum `ARG` com segredo
- [ ] `USER` não-root antes do `CMD`
- [ ] Forma **exec** em `CMD` e `ENTRYPOINT`
- [ ] `tini` ou `--init` se o app não trata sinais
- [ ] `HEALTHCHECK` que exercita a dependência real, com `start-period`
- [ ] Cache de gerenciador de pacotes limpo **na mesma camada**
- [ ] `LABEL org.opencontainers.image.*` preenchidos
- [ ] Imagem escaneada (`trivy`/`scout`) no CI
- [ ] SBOM e proveniência gerados no build de produção

---

## Autoteste

1. Por que a linha `# syntax=docker/dockerfile:1` importa mesmo com o Docker atualizado?
2. Quais três comportamentos o `ADD` tem que o `COPY` não tem, e por que isso é um problema?
3. Escreva a tabela `CMD`/`ENTRYPOINT` de memória, com os três casos.
4. Por que `exec` é obrigatório na última linha de um entrypoint script?
5. `ARG` e `ENV`: qual existe em tempo de execução, e qual dos dois serve para segredo?
6. Onde entra `--mount=type=cache` e onde entra `--mount=type=secret`? Dê um exemplo de cada.
7. Por que Alpine é má escolha para Python e boa para Go?
8. O build "trava" em `transferring context`. Qual é o diagnóstico e a correção?
9. Como fazer o build falhar se um teste quebrar, sem duplicar configuração de CI?
10. Liste cinco itens do checklist que você aplicaria hoje a um Dockerfile que já tem em uso.
