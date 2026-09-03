# Exercício — Dockerfile

> **Tente antes de olhar.** Solução comentada após o separador.

## Enunciado

Você recebeu este Dockerfile de um colega. Ele funciona, mas a imagem tem
**1,1 GB**, o build leva **3 minutos toda vez** que ele muda uma linha de
Python, e a equipe de segurança recusou o deploy.

```dockerfile
FROM python:3.12
MAINTAINER colega@empresa.com

ADD . /app
WORKDIR /app

RUN apt-get update
RUN apt-get install -y build-essential libpq-dev curl vim
RUN pip install -r requirements.txt
RUN rm -rf /var/lib/apt/lists/*

ENV DB_PASSWORD=SenhaSuperSecreta123

EXPOSE 8000
CMD uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Tarefas:**

1. Liste **todos** os problemas que você encontrar. São pelo menos 10.
2. Para cada um, explique a consequência concreta.
3. Reescreva o Dockerfile corrigido, com multi-stage, não-root e healthcheck.
4. Valide sua versão com `hadolint`.

---
---
---

# SOLUÇÃO COMENTADA

## 1 e 2. Os problemas

### Problema 1 — `FROM python:3.12` (imagem completa)

~1 GB, contra ~43 MB da `-slim`. Traz compilador, headers e ferramentas de
desenvolvimento que ninguém usa em produção.

**Consequência:** deploy lento, disco caro, superfície de ataque enorme.

**Agravante:** a tag não fixa a suite do Debian. Como vimos na
[investigação real do módulo 08](../08-projeto-aplicado/dockerfile-fastapi-sqlalchemy.md),
`python:3.12-slim` migrou de bookworm para trixie sem aviso — o mesmo vale aqui.

### Problema 2 — `MAINTAINER` descontinuado

Substituído por `LABEL org.opencontainers.image.authors=`.

**Consequência:** aviso no build; ferramentas OCI não leem o campo.

### Problema 3 — `ADD` onde cabia `COPY`

`ADD` descompacta tarball e baixa URL automaticamente. Comportamento implícito
que surpreende quando alguém põe um `.tar.gz` no repositório.

### Problema 4 — `ADD . /app` **antes** de instalar as dependências

**O problema mais caro do arquivo.** Qualquer edição de qualquer arquivo
invalida esta camada e todas as seguintes — inclusive o `pip install`.

**Consequência:** os 3 minutos a cada mudança de uma linha.

### Problema 5 — `apt-get update` em `RUN` separado

O texto do comando nunca muda, então a camada é cacheada indefinidamente,
servindo uma lista de pacotes velha.

**Consequência:** semanas depois, `apt-get install` falha com `404 Not Found`
em pacote que "existia ontem".

### Problema 6 — `rm -rf /var/lib/apt/lists/*` em camada separada

Camadas são aditivas. A lista (~40 MB) já foi gravada na camada do `install`; o
`rm` posterior só marca como apagado.

**Consequência:** +40 MB permanentes. A "limpeza" não limpa nada.

### Problema 7 — `vim` e `curl` na imagem de produção

Ferramentas interativas não têm função em produção — servem ao invasor.

**Consequência:** superfície de ataque. Se precisar depurar, use
`docker debug` ou um container efêmero com `--pid=container:<alvo>`.

### Problema 8 — `build-essential` na imagem final

Necessário para compilar `psycopg`/`asyncpg`, inútil depois. ~300 MB.

**Consequência:** é exatamente o que multi-stage resolve.

### Problema 9 — `ENV DB_PASSWORD=...` — o mais grave

Senha **hardcoded** e gravada na imagem para sempre.

**Consequência:** qualquer pessoa com a imagem lê a senha:

```bash
docker inspect imagem | grep DB_PASSWORD
docker history --no-trunc imagem | grep DB_PASSWORD
```

Se a imagem foi publicada, a senha está comprometida — **rotacione**. Apagar a
imagem não desfaz o download de quem já baixou.

### Problema 10 — roda como root

Sem `USER`, o processo é root. Uma falha de path traversal vira root no
container, e a distância até o host é menor do que se imagina.

### Problema 11 — `CMD` em forma shell

`CMD uvicorn ...` roda `/bin/sh -c`, que não repassa `SIGTERM`.

**Consequência:** `docker stop` é ignorado, 10 s de espera e `SIGKILL`.
Conexões caem no meio.

### Problema 12 — sem `HEALTHCHECK`

O orquestrador não tem como distinguir "processo de pé" de "aplicação
funcionando".

### Problema 13 — sem `.dockerignore`

`.git`, `.venv` e caches vão para o build context. Build lento, cache
invalidado a cada commit, e risco de `.env` entrar na imagem.

## 3. Dockerfile corrigido

```dockerfile
# syntax=docker/dockerfile:1

# ---------------- builder ----------------
FROM python:3.12-slim-trixie AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /build

# update e install NO MESMO RUN, com limpeza na mesma camada.
# hadolint ignore=DL3008
RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Manifesto SOZINHO e ANTES do código: preserva o cache do install.
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

# ---------------- runtime ----------------
FROM python:3.12-slim-trixie AS runtime

LABEL org.opencontainers.image.authors="colega@empresa.com" \
      org.opencontainers.image.source="https://github.com/empresa/projeto"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

# libpq5 é a biblioteca de RUNTIME do Postgres (o -dev era só para compilar).
# hadolint ignore=DL3008
RUN apt-get update \
    && apt-get install --no-install-recommends -y libpq5 \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --system --gid 10001 appgroup \
    && useradd --system --uid 10001 --gid appgroup --no-create-home appuser

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv
COPY --chown=appuser:appgroup app/ ./app/
COPY --chown=appuser:appgroup healthcheck.py ./

USER 10001:10001

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD ["python", "/app/healthcheck.py"]

# Forma exec: o uvicorn vira PID 1 e recebe SIGTERM diretamente.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

E o `.dockerignore`:

```
.git
.venv
__pycache__
.pytest_cache
.env
.env.*
!.env.example
*.db
README.md
Dockerfile
```

**A senha sai do Dockerfile** e vira secret em runtime:

```yaml
services:
  api:
    environment:
      DATABASE_URL_FILE: /run/secrets/database_url
    secrets: [database_url]
```

Ver [secrets](../06-seguranca/secrets-e-variaveis-sensiveis.md).

## 4. Validação com hadolint

```bash
hadolint Dockerfile
# esperado: nenhuma saída
```

Sobre os dois `# hadolint ignore=DL3008`: a regra pede pinar versão de pacote
apt. Ignoramos deliberadamente porque o Debian remove o `.deb` antigo do mirror
ao publicar correção de segurança, e o build passa a falhar com 404. A
reprodutibilidade vem da **tag de suite fixa** (`slim-trixie`) e do
`requirements.txt` pinado.

Lembre que a diretiva `# hadolint ignore=` precisa ser a **última linha antes do
`RUN`** — um comentário entre ela e a instrução a anula silenciosamente (erro
cometido durante a escrita deste curso).

## Resultado

| Métrica | Antes | Depois |
|---|---|---|
| Tamanho | ~1,1 GB | ~150 MB |
| Rebuild após editar `.py` | ~3 min | ~5 s |
| Usuário | root | uid 10001 |
| Senha na imagem | sim | não |
| Healthcheck | não | sim |
| `docker stop` limpo | não | sim |

> Os números de tamanho e tempo são **estimativas fundamentadas**, não medições:
> o daemon não estava disponível na máquina onde este curso foi escrito. O
> Dockerfile acima, esse sim, passou pelo `hadolint` sem avisos. Meça os seus
> com `docker images` e `time docker build`.

---
[← multi-stage](multi-stage-build.md) · [módulo 03: Compose →](../03-compose/anatomia-docker-compose.md) · [índice](../00-indice.md)
