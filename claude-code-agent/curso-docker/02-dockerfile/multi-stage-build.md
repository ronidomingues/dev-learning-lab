# Multi-stage build: separar o que constrói do que roda

> **Nível:** intermediário → avançado
> **Última verificação:** 18/08/2026

## 1. O problema

Para **instalar** `asyncpg` você precisa de `gcc`, headers do Python e
`build-essential` — cerca de 300 MB. Para **rodar** `asyncpg`, você precisa de
zero disso: a extensão já está compilada.

Numa imagem de estágio único, tudo que entrou fica:

```dockerfile
FROM python:3.12-slim-trixie
RUN apt-get update && apt-get install -y build-essential   # +300 MB, para sempre
RUN pip install asyncpg
COPY app/ ./app/
# resultado: ~400 MB, dos quais ~300 MB são compilador que nunca será usado
```

Não é só disco. É superfície de ataque: um compilador dentro do container em
produção é a primeira ferramenta que um invasor procura.

E não adianta `apt-get remove` depois — [camadas são
aditivas](../01-fundamentos/conceito.md): remover numa camada posterior não
apaga da anterior.

## 2. A solução

```dockerfile
# syntax=docker/dockerfile:1

# ---------- estágio 1: constrói ----------
FROM python:3.12-slim-trixie AS builder
RUN apt-get update \
    && apt-get install --no-install-recommends -y build-essential \
    && rm -rf /var/lib/apt/lists/*
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

# ---------- estágio 2: roda ----------
FROM python:3.12-slim-trixie AS runtime
ENV PATH="/opt/venv/bin:$PATH"
COPY --from=builder /opt/venv /opt/venv     # ← só o resultado atravessa
COPY app/ ./app/
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0"]
```

O segundo `FROM` **começa do zero**. Nada do estágio anterior existe, exceto o
que você trouxe explicitamente com `COPY --from=`.

Resultado: ~130 MB em vez de ~400 MB, e nenhum compilador no runtime.

### Por que copiar um venv funciona?

Porque um virtualenv é apenas um diretório: `bin/`, `lib/python3.12/site-packages/`
e um `pyvenv.cfg`. Não há registro global no sistema, nem banco de pacotes fora
dele. Copiar a pasta e colocar `/opt/venv/bin` no `PATH` **é** uma instalação
completa.

O detalhe que torna isso confiável: os dois estágios usam **a mesma imagem
base**. Versão de Python diferente entre builder e runtime quebra — os
`.so` compilados são específicos da ABI (`cpython-312-x86_64-linux-gnu.so`). Se
o builder for 3.12 e o runtime 3.13, o import falha com `ModuleNotFoundError`
numa extensão que visivelmente está lá.

## 3. Padrões por linguagem

### Go — o caso mais dramático

```dockerfile
FROM golang:1.23 AS builder
WORKDIR /src
COPY go.mod go.sum ./
RUN --mount=type=cache,target=/go/pkg/mod go mod download
COPY . .
# CGO_ENABLED=0 gera binário estático, sem dependência de libc
RUN CGO_ENABLED=0 go build -ldflags="-s -w" -o /app/servidor ./cmd/servidor

FROM scratch
COPY --from=builder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/
COPY --from=builder /app/servidor /servidor
ENTRYPOINT ["/servidor"]
```

De ~900 MB para ~10 MB. `scratch` é a imagem vazia — literalmente nada.
O `COPY` dos certificados é obrigatório se o programa fizer HTTPS; sem ele o
erro é `x509: certificate signed by unknown authority`, que confunde porque não
parece um problema de imagem.

### Node — front-end estático

```dockerfile
FROM node:22-slim AS builder
WORKDIR /app
COPY package*.json ./
RUN --mount=type=cache,target=/root/.npm npm ci
COPY . .
RUN npm run build

FROM nginx:1.29-alpine
COPY --from=builder /app/dist /usr/share/nginx/html
```

O Node inteiro (~200 MB) e o `node_modules` (frequentemente 500 MB+) ficam para
trás. Vai só o HTML/CSS/JS compilado.

### Estágio de teste que não vai para produção

```dockerfile
FROM python:3.12-slim-trixie AS base
# ... dependências de runtime ...

FROM base AS test
COPY requirements-dev.txt .
RUN pip install -r requirements-dev.txt
COPY . .
RUN pytest -q                    # falha aqui = build falha

FROM base AS runtime
COPY app/ ./app/
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0"]
```

```bash
docker build --target test .      # roda os testes
docker build --target runtime .   # imagem de produção, sem pytest
```

Com `--target`, você **escolhe onde parar**. Um mesmo Dockerfile serve para CI e
para produção.

## 4. Detalhes que valem tempo

### Estágios rodam em paralelo

O BuildKit constrói o grafo de dependências e executa estágios independentes
**ao mesmo tempo**:

```dockerfile
FROM node:22-slim AS frontend
RUN npm run build

FROM python:3.12-slim-trixie AS backend
RUN pip install -r requirements.txt

FROM nginx:1.29-alpine
COPY --from=frontend /app/dist /usr/share/nginx/html
COPY --from=backend  /opt/venv /opt/venv
```

`frontend` e `backend` não dependem um do outro — rodam simultaneamente.
Estruturar o Dockerfile para maximizar isso é uma otimização real e barata.

### Copiar de uma imagem externa

```dockerfile
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
```

`--from` aceita nome de imagem, não só de estágio. É a forma limpa de trazer um
binário de ferramenta sem instalar nada.

### Estágio-base compartilhado evita repetição

```dockerfile
FROM python:3.12-slim-trixie AS base
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app

FROM base AS builder
# ...

FROM base AS runtime
# herda ENV e WORKDIR, sem repetir
```

## 5. Quando NÃO usar multi-stage

Honestidade: multi-stage não é sempre.

- **Linguagem interpretada sem dependência compilada.** Se o `pip install` é só
  Python puro, não há compilador para descartar. O ganho é marginal e o
  Dockerfile fica mais complexo à toa.
- **Imagem já mínima.** Se você parte de `alpine` e instala dois pacotes, não há
  o que separar.
- **Durante depuração.** Um estágio único é mais fácil de inspecionar. Otimize
  depois que funcionar.

Complexidade tem custo. Adote quando houver ganho mensurável.

## 6. Erros que você provavelmente vai cometer

| Mensagem | Causa raiz | Correção |
|---|---|---|
| `COPY --from=builder: no such file or directory` | caminho não existe **no estágio de origem** | `docker build --target builder -t x . && docker run --rm x ls /caminho` |
| `ModuleNotFoundError` em pacote que está no venv | `PATH` não inclui `/opt/venv/bin` no runtime | `ENV PATH="/opt/venv/bin:$PATH"` **depois** do último `FROM` |
| `ModuleNotFoundError` só em extensão C | versão de Python diferente entre estágios | mesma imagem base nos dois |
| `x509: certificate signed by unknown authority` | `scratch` sem certificados de CA | copiar `ca-certificates.crt` do builder |
| `exec /servidor: no such file or directory` (existe!) | binário dinâmico em `scratch`, sem libc | `CGO_ENABLED=0` para binário estático |
| imagem final ainda enorme | copiou o estágio inteiro, não só o artefato | `COPY --from` apontando para o caminho específico |
| CI não cacheia estágios intermediários | `mode=min` | `--cache-to=...,mode=max` |

## 7. Autoteste

1. Por que o segundo `FROM` descarta tudo do primeiro?
2. Por que copiar um virtualenv entre estágios funciona?
3. O que quebra se builder for Python 3.12 e runtime 3.13?
4. Para que serve `--target`, e como isso ajuda no CI?
5. Por que `scratch` precisa de `COPY` dos certificados de CA?
6. `exec ... no such file or directory` num binário que existe: o que é?
7. Cite um caso em que multi-stage **não** compensa.

---
[← cache](cache-de-camadas.md) · [exercício →](exercicio.md) · [índice](../00-indice.md)
