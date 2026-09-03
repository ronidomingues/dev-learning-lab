# 12 · Imagens e camadas — o formato por dentro

`Nível: intermediário → avançado` · `Última atualização: 11/08/2026`

Se você entender este arquivo, para de errar em cache de build, tamanho de imagem e vazamento
de segredo. É onde a maior parte do dinheiro e do tempo é perdida por desconhecimento.

---

## 1. O que uma imagem é, literalmente

Uma imagem OCI é composta de três tipos de objeto, todos identificados por hash SHA-256 do
próprio conteúdo:

```
  ÍNDICE (manifest list)          ← opcional, para multi-arquitetura
        │
        ├──▶ MANIFESTO (linux/amd64)
        │        ├──▶ CONFIG (JSON): env, cmd, entrypoint, user, histórico
        │        └──▶ CAMADAS: [blob1.tar.gz, blob2.tar.gz, ...]
        │
        └──▶ MANIFESTO (linux/arm64)
                 ├──▶ CONFIG
                 └──▶ CAMADAS
```

Veja de verdade:

```bash
docker manifest inspect nginx:alpine
# ou, sem depender de login:
docker buildx imagetools inspect nginx:alpine
```

O manifesto é um JSON pequeno assim:

```json
{
  "schemaVersion": 2,
  "mediaType": "application/vnd.oci.image.manifest.v1+json",
  "config": {
    "mediaType": "application/vnd.oci.image.config.v1+json",
    "digest": "sha256:9b1e2f...",
    "size": 7023
  },
  "layers": [
    { "mediaType": "application/vnd.oci.image.layer.v1.tar+gzip",
      "digest": "sha256:a1b2c3...", "size": 3401819 },
    { "mediaType": "application/vnd.oci.image.layer.v1.tar+gzip",
      "digest": "sha256:d4e5f6...", "size": 1204 }
  ]
}
```

**Cada camada é literalmente um arquivo `.tar.gz`** com as alterações do sistema de arquivos
daquele passo. Nada mais exótico que isso.

```bash
# Extraia uma imagem e olhe por dentro
docker save alpine:3.20 -o alpine.tar
mkdir -p /tmp/alpine && tar -xf alpine.tar -C /tmp/alpine
ls /tmp/alpine
# esperado: blobs/, index.json, oci-layout   (formato OCI moderno)
cat /tmp/alpine/index.json | jq
```

---

## 2. Endereçamento por conteúdo: por que o digest é imutável e a tag não

O identificador real de uma imagem é o **digest**: o SHA-256 do manifesto.

```
nginx:alpine                                      ← tag: MUTÁVEL
nginx@sha256:1a2b3c...64 caracteres hexadecimais  ← digest: IMUTÁVEL
```

- **Tag** é um ponteiro nomeado. Quem tem permissão de push pode reapontá-la a qualquer momento.
  `nginx:alpine` hoje e amanhã podem ser imagens completamente diferentes.
- **Digest** é derivado do conteúdo. Se o conteúdo mudar, o digest muda. Não há como reapontar
  um digest para outro conteúdo sem quebrar o SHA-256 — o que é a garantia de integridade.

```bash
docker pull nginx:alpine
docker image inspect --format '{{index .RepoDigests 0}}' nginx:alpine
# nginx@sha256:...

# Em produção, referencie assim:
docker run nginx@sha256:1a2b3c...
```

```dockerfile
# E no Dockerfile, para builds realmente reproduzíveis:
FROM node:22.4.0-alpine@sha256:1a2b3c...
```

> **Isto é a base de tudo em cadeia de suprimentos.** Assinatura, atestado de proveniência e
> SBOM referenciam o **digest**, nunca a tag. Uma política que diz "só rode imagens assinadas"
> é inútil se o deploy for por tag.

---

## 3. Como as camadas viram um sistema de arquivos: OverlayFS

O driver de armazenamento padrão hoje é o **overlay2**, que usa o OverlayFS do kernel.

```
   Camada superior (upperdir)  ← escrita do container, efêmera
   ────────────────────────────
   lowerdir 3                  ┐
   lowerdir 2                  ├─ somente leitura, compartilhadas entre containers
   lowerdir 1                  ┘
   ────────────────────────────
   merged                      ← o que o processo enxerga como /
```

Três regras governam a união:

1. **Arquivo presente em várias camadas:** vence o da camada **mais alta**.
2. **Escrita em arquivo de camada inferior:** *copy-on-write* — o arquivo inteiro é copiado
   para a camada superior e a escrita ocorre na cópia.
3. **Remoção:** cria-se um **whiteout** (um arquivo de dispositivo de caractere 0:0 com o mesmo
   nome) na camada superior, que esconde o original. **O original continua ocupando espaço.**

```bash
# Veja a estrutura real
docker run -d --name teste alpine sleep 3600
docker inspect --format '{{json .GraphDriver.Data}}' teste | jq
# esperado: LowerDir, UpperDir, MergedDir, WorkDir com caminhos em /var/lib/docker/overlay2/

# Prove o copy-on-write
docker exec teste sh -c 'echo alterado >> /etc/hostname'
docker diff teste
# esperado: C /etc  e  C /etc/hostname   (C = changed)
docker rm -f teste
```

### As consequências de desempenho que você vai encontrar

| Situação | Efeito | Mitigação |
|---|---|---|
| Primeira escrita em arquivo grande | Copia o arquivo **inteiro** para a camada superior | Coloque dados mutáveis em **volume**, não na camada de escrita |
| Muitas camadas (>50) | Cada `open()` percorre a pilha; latência cresce | Consolide `RUN`s; use multi-stage |
| Banco de dados na camada de escrita | Escrita aleatória sofre com CoW | **Sempre** use volume para banco |
| Muitos arquivos pequenos | `page cache` compartilhado ajuda, mas metadados pesam | Menos camadas; base menor |

---

## 4. O cache de build: a regra e as cinco consequências

**A regra, em uma frase:** o Docker calcula uma chave de cache por instrução; se a chave bate e
**todas as instruções anteriores também bateram**, a camada é reaproveitada. Uma invalidação
invalida tudo dali para baixo.

Como a chave é calculada:

| Instrução | Chave de cache baseada em |
|---|---|
| `FROM` | Digest da imagem base |
| `RUN` | **O texto literal do comando** — não o resultado dele |
| `COPY` / `ADD` | Checksum do **conteúdo** dos arquivos copiados + destino |
| `ENV`, `ARG`, `LABEL`, `WORKDIR` | O texto da instrução |

### Consequência 1 — ordene do menos volátil ao mais volátil

```dockerfile
# ❌ 4 minutos a cada mudança de uma linha de código
COPY . .
RUN npm ci

# ✅ o npm ci só refaz quando as dependências mudam
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
```

### Consequência 2 — `RUN apt-get update` sozinho é uma armadilha

```dockerfile
# ❌ o 'update' fica em cache por semanas; o 'install' pega índice velho
RUN apt-get update
RUN apt-get install -y curl

# ✅ mesma camada: se um roda, o outro roda
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*
```

Isso tem nome: **cache busting**. O `apt-get update` cacheado aponta para espelhos cujos pacotes
já mudaram, e o `install` falha com `404 Not Found` — erro que confunde porque "funcionava
ontem".

### Consequência 3 — `.dockerignore` faz parte da chave de cache

Se `node_modules` não estiver no `.dockerignore`, qualquer alteração ali invalida o `COPY . .` —
e você não vai entender por quê.

### Consequência 4 — o cache é local por padrão

Em CI, cada execução começa em uma máquina limpa e o cache não existe. Solução: cache externo.

```bash
docker buildx build \
  --cache-from type=registry,ref=usuario/app:cache \
  --cache-to   type=registry,ref=usuario/app:cache,mode=max \
  -t usuario/app:1.0 --push .
```

`mode=max` exporta o cache de **todos os estágios** (inclusive os intermediários do
multi-stage); `mode=min`, só o do estágio final. Em multi-stage, `mode=max` é quase sempre o
que você quer.

### Consequência 5 — cache montado é diferente de camada cacheada

```dockerfile
RUN --mount=type=cache,target=/root/.npm npm ci
```

Esse cache **persiste entre builds diferentes** e **não entra na imagem**. É o mecanismo certo
para caches de gerenciador de pacotes (`~/.npm`, `~/.cache/pip`, `/go/pkg/mod`,
`~/.cargo/registry`, `/var/cache/apt`). A camada continua sendo recalculada, mas o download não.

```bash
docker builder prune                  # limpa esses caches quando o disco apertar
docker builder du                     # veja quanto ocupam
```

---

## 5. Por que sua imagem está gorda — e como emagrecer

### Diagnóstico primeiro

```bash
docker images --format "table {{.Repository}}:{{.Tag}}\t{{.Size}}"
docker history minha-app:1.0                 # camada a camada
docker run --rm -it -v /var/run/docker.sock:/var/run/docker.sock \
  wagoodman/dive minha-app:1.0               # a melhor ferramenta: mostra o desperdício por camada
```

O `dive` calcula um "score de eficiência" e lista arquivos que são adicionados e depois
removidos ou sobrescritos — exatamente o desperdício que o `docker history` não mostra.

### As técnicas, em ordem de retorno sobre o esforço

| # | Técnica | Redução típica |
|---|---|---|
| 1 | **Multi-stage**: compilar em um estágio, copiar só o artefato | 60–90% |
| 2 | **Base menor**: `alpine`, `slim`, `distroless` | 50–80% |
| 3 | **`.dockerignore` correto** | variável, às vezes enorme |
| 4 | Consolidar `RUN` e limpar cache **na mesma camada** | 5–30% |
| 5 | `--no-install-recommends` (apt) / `--no-cache` (apk) | 10–40% |
| 6 | Remover ferramentas de build da imagem final | incluído no (1) |
| 7 | `strip`/`-ldflags="-s -w"` em binários compilados | 20–30% do binário |

### Comparação de bases (ordens de grandeza; confira na sua máquina)

| Base | Tamanho aprox. | Tem shell? | Gerenciador de pacotes | Quando usar |
|---|---|---|---|---|
| `scratch` | 0 | não | não | Binário estático (Go, Rust) |
| `gcr.io/distroless/static` | ~2 MB | não (há variante `:debug`) | não | Binário estático, com certificados e usuário nonroot |
| `alpine:3.20` | ~8 MB | sim (`ash`) | `apk` | Padrão para a maioria |
| `debian:12-slim` | ~75 MB | sim | `apt` | Quando precisa de glibc |
| `ubuntu:24.04` | ~78 MB | sim | `apt` | Familiaridade |
| `node:22-alpine` | ~50 MB | sim | `apk` + npm | Node enxuto |
| `node:22` | ~400 MB | sim | `apt` + npm | Só se precisar de toolchain |

> ### ⚠️ A ressalva importante sobre Alpine
>
> Alpine usa **musl libc** em vez de **glibc**. Isso causa três problemas reais:
>
> 1. **Pacotes Python com rodas binárias (`manylinux`) não funcionam.** O `pip` cai para
>    compilar do fonte, o que exige toolchain e faz o build durar 10 minutos em vez de 20
>    segundos. Para Python, `python:3.13-slim` costuma ser a escolha melhor.
> 2. **Diferenças de desempenho no alocador de memória** já foram medidas como significativas
>    em cargas com muita alocação. Menos crítico nas versões recentes do musl, mas ainda real.
> 3. **Resolução de DNS** tem diferenças históricas de comportamento (uso de `search`, TCP como
>    fallback) que causam falhas intermitentes difíceis de diagnosticar.
>
> *Recomendação:* Alpine para Go, Rust, C compilado estaticamente e Node (que traz seu próprio
> runtime). `slim` (Debian) para Python, Ruby e qualquer coisa com extensões nativas.

### O padrão multi-stage, resumido

```dockerfile
FROM node:22 AS build          # 400 MB de toolchain, tudo bem
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:22-alpine AS producao  # 50 MB
WORKDIR /app
COPY --from=build /app/dist ./dist
COPY --from=build /app/node_modules ./node_modules
USER node
CMD ["node", "dist/main.js"]
```

O estágio de build **não vai** para o registry. Ele existe só durante o `docker build`.

---

## 6. Segredos vazam em camadas — a demonstração

Esta seção existe porque é o erro com maior consequência e menor visibilidade.

```dockerfile
# ❌ ERRADO
ARG NPM_TOKEN
RUN echo "//registry.npmjs.org/:_authToken=${NPM_TOKEN}" > ~/.npmrc \
 && npm ci \
 && rm ~/.npmrc          # o rm NÃO adianta
```

Prove o vazamento por três caminhos independentes:

```bash
# 1) O ARG fica no histórico e na config da imagem
docker history --no-trunc IMAGEM | grep -i token
docker image inspect IMAGEM --format '{{json .Config.Env}}'

# 2) O arquivo está no tar de alguma camada
docker save IMAGEM -o img.tar && tar -xf img.tar -C /tmp/img
grep -ra "_authToken" /tmp/img/blobs | head

# 3) Um container montado numa camada intermediária o encontra
docker run --rm IMAGEM cat /root/.npmrc 2>/dev/null   # pode não estar na final...
# ...mas a camada anterior, sim — e ela está no registry.
```

Isso vale para **qualquer** segredo: chave SSH, token de nuvem, senha de banco, certificado.
Uma imagem publicada num registry público com uma dessas camadas é uma credencial vazada.

**O jeito certo:**

```dockerfile
# syntax=docker/dockerfile:1
RUN --mount=type=secret,id=npmrc,target=/root/.npmrc,mode=0400 npm ci
```
```bash
docker buildx build --secret id=npmrc,src=$HOME/.npmrc -t app:1.0 .
```

O arquivo é montado num tmpfs que existe apenas durante aquele `RUN` e **nunca vira camada**.

**Regra final:** `ARG` para configuração não sensível (versão, arquitetura, flags);
`--mount=type=secret` para segredo. Sem exceção.

---

## 7. Imagens multi-arquitetura

Um **índice** (antes chamado *manifest list*) aponta para vários manifestos, um por
`os/arquitetura`. Quando você faz `docker pull`, o cliente informa sua plataforma e o registry
devolve o manifesto certo.

```bash
docker buildx imagetools inspect alpine:3.20
# esperado: entradas para linux/amd64, linux/arm64, linux/arm/v7, linux/386, ...
```

```bash
docker buildx create --name multi --driver docker-container --bootstrap --use
docker buildx build --platform linux/amd64,linux/arm64 -t usuario/app:1.0 --push .
```

**Erros clássicos aqui:**

- `exec format error` = você está rodando uma imagem de outra arquitetura. Confirme com
  `docker image inspect --format '{{.Architecture}}'`.
- Build ARM64 emulado por QEMU pode levar **10× mais tempo** ou falhar em dependências nativas.
  Use `--platform=$BUILDPLATFORM` + cross-compilação quando a linguagem permitir, ou runners
  nativos por arquitetura no CI.
- Multi-arch tradicionalmente exigia `--push` (o armazenamento local legado não guardava índices
  com múltiplas plataformas). Com o **containerd image store** — padrão em instalações novas
  desde a Engine 29 — isso deixa de ser limitação.

---

## 8. O armazenamento de imagens: overlay2 e o containerd image store

Historicamente, o Docker mantinha seu próprio banco de imagens em `/var/lib/docker`, com o
driver `overlay2`. A partir da **Engine 29**, instalações novas passam a usar o
**containerd image store** por padrão.

| | Store legado do Docker | containerd image store |
|---|---|---|
| Quem gerencia | `dockerd` | `containerd` |
| Multi-plataforma local | limitado | nativo |
| Compartilhamento com Kubernetes/nerdctl | não | sim |
| Snapshotters plugáveis (`stargz`, `overlaybd`) | não | sim |
| Migração ao atualizar | — | **não é automática**: vale para instalações novas |

```bash
docker system info | grep -i -A2 "storage driver"
# esperado no padrão novo: menção a containerd snapshotter
```

**Por que isso importa:** o `containerd` é o mesmo runtime que o Kubernetes usa. Unificar o
armazenamento aproxima o que você constrói na máquina do que roda no cluster, e destrava
recursos como *lazy pulling* (iniciar o container antes de baixar a imagem inteira, via
`stargz`/`eStargz`) — relevante quando a imagem tem gigabytes, como as de IA.

---

## 9. Metadados e proveniência

```dockerfile
LABEL org.opencontainers.image.title="minha-api" \
      org.opencontainers.image.description="API de pedidos" \
      org.opencontainers.image.version="1.4.2" \
      org.opencontainers.image.revision="$GIT_SHA" \
      org.opencontainers.image.source="https://github.com/org/repo" \
      org.opencontainers.image.licenses="MIT"
```

E os artefatos modernos que acompanham a imagem no registry:

| Artefato | O que é | Ferramenta |
|---|---|---|
| **SBOM** | Lista de todos os componentes e versões | `docker buildx build --sbom=true`, `syft` |
| **Proveniência (SLSA)** | Como, onde e a partir de quê a imagem foi construída | `--provenance=true` |
| **Assinatura** | Prova criptográfica de quem publicou | `cosign sign` |
| **Atestado de vulnerabilidade** | Resultado de escaneamento anexado | `trivy`, `grype`, Docker Scout |

```bash
docker buildx imagetools inspect usuario/app:1.0 --format '{{json .SBOM}}'
cosign verify usuario/app:1.0 --certificate-identity-regexp '.*' \
  --certificate-oidc-issuer https://token.actions.githubusercontent.com
```

Esses artefatos ficam **no registry, ao lado da imagem**, referenciados pelo digest. É o
registry deixando de ser depósito de imagem e virando depósito de artefatos OCI.

---

## Autoteste

1. Qual é a diferença entre tag e digest, e por que política de segurança referencia digest?
2. Explique copy-on-write e diga por que colocar um banco de dados na camada de escrita é ruim.
3. Por que `RUN apt-get update` numa camada e `RUN apt-get install` em outra causa erro 404
   semanas depois?
4. O que a chave de cache de um `RUN` leva em conta — o comando ou o resultado dele? Qual é a
   consequência?
5. Cite três problemas concretos de usar Alpine, e para quais linguagens você o evitaria.
6. Você usou `--build-arg TOKEN=xyz` e depois `rm`. Descreva três formas independentes de
   recuperar o token da imagem.
7. Qual é a diferença entre `mode=min` e `mode=max` no cache de registry, e qual usar em
   multi-stage?
8. O que é um whiteout no OverlayFS e por que ele explica "apaguei e a imagem não diminuiu"?
9. O que muda com o containerd image store, e por que uma atualização de versão não migra
   automaticamente?
10. Como você provaria, em um comando, que duas imagens diferentes compartilham a mesma camada
    base no disco?
