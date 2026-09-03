# 19 · uv em Docker, CI e produção

> **Nível:** avançado · **Atualizado em:** 31/08/2026 · **uv 0.12.7**
> ⚠️ Os Dockerfiles e workflows deste arquivo seguem a documentação oficial consultada
> em 31/08/2026. **Não pude executar `docker build` nesta sessão** (sem acesso ao daemon
> Docker); os comandos de uv dentro deles foram verificados isoladamente. Verifique na
> sua máquina antes de levar para produção.

---

## 1. Os três padrões de Dockerfile

### Padrão A — imagem oficial do uv como base (mais simples)

```dockerfile
# syntax=docker/dockerfile:1
FROM ghcr.io/astral-sh/uv:0.12.7-python3.13-bookworm-slim

ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-install-project --no-dev

COPY . .
RUN uv sync --locked --no-dev

ENV PATH="/app/.venv/bin:$PATH"
CMD ["python", "-m", "app"]
```

Vantagem: uma linha para começar. Desvantagem: o binário do uv (≈35 MB) vai para a
imagem final sem necessidade.

### Padrão B — copiar só o binário (o que eu recomendo)

```dockerfile
# syntax=docker/dockerfile:1
FROM python:3.13-slim-bookworm

COPY --from=ghcr.io/astral-sh/uv:0.12.7 /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never
WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-install-project --no-dev

COPY . .
RUN uv sync --locked --no-dev

ENV PATH="/app/.venv/bin:$PATH"
CMD ["python", "-m", "app"]
```

`COPY --from=<imagem>` traz **apenas os dois arquivos**, com a versão fixada. É o padrão
oficial recomendado.

### Padrão C — multiestágio (imagem final sem o uv)

```dockerfile
# syntax=docker/dockerfile:1

FROM ghcr.io/astral-sh/uv:0.12.7-python3.13-bookworm-slim AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=never
WORKDIR /app
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-dev
COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev

FROM python:3.13-slim-bookworm
RUN groupadd -r app && useradd -r -g app app
COPY --from=builder --chown=app:app /app /app
ENV PATH="/app/.venv/bin:$PATH" PYTHONUNBUFFERED=1
USER app
WORKDIR /app
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Menor, sem uv, sem cache, rodando como usuário sem privilégio. É o que vai para produção.

---

## 2. As sete regras de ouro do uv em Docker

### Regra 1 — separe dependências de código, sempre

```dockerfile
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-install-project --no-dev     # camada A: muda raramente
COPY . .
RUN uv sync --locked --no-dev                          # camada B: muda a cada commit
```

Sem `--no-install-project`, o `COPY . .` invalidaria a camada de dependências a cada
alteração de código, e você reinstalaria 80 pacotes para trocar uma linha. **Esta é a
otimização isolada mais importante.**

### Regra 2 — `--locked`, nunca `uv sync` puro

`--locked` **falha** se o `uv.lock` estiver desatualizado em relação ao `pyproject.toml`.
Numa imagem de produção você quer o erro, não uma resolução silenciosa que produz um
ambiente diferente do que você testou.

### Regra 3 — `UV_LINK_MODE=copy`

O cache do BuildKit e a camada da imagem são sistemas de arquivos diferentes. Sem isso:
`failed to create hardlink ... Invalid cross-device link`.

### Regra 4 — `UV_COMPILE_BYTECODE=1`

Gera os `.pyc` no build. O container inicia mais rápido, e o sistema de arquivos de
produção pode ser somente-leitura (onde os `.pyc` nunca seriam gerados).

### Regra 5 — `UV_PYTHON_DOWNLOADS=never`

Falha alto se o Python esperado não estiver na imagem, em vez de baixar 35 MB
silenciosamente e produzir uma imagem inchada com dois interpretadores.

### Regra 6 — cache do BuildKit em vez de camada

```dockerfile
RUN --mount=type=cache,target=/root/.cache/uv uv sync --locked
```
O cache persiste entre builds **sem** entrar na imagem.

### Regra 7 — `PATH` do `.venv`, não `uv run` no `CMD`

```dockerfile
ENV PATH="/app/.venv/bin:$PATH"
CMD ["python", "-m", "app"]
```

**Por quê:** `CMD ["uv", "run", "python", "-m", "app"]` faz o uv verificar e sincronizar
o ambiente **a cada início de container**, o que custa tempo e, pior, pode tentar acessar
a rede num pod que não deveria ter saída. Colocar o `.venv` no `PATH` e chamar o
`python` direto é mais rápido e mais previsível.

Se insistir em `uv run`, use `--no-sync`.

---

## 3. GitHub Actions

```yaml
name: CI
on: [push, pull_request]

jobs:
  testes:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: astral-sh/setup-uv@v6
        with:
          version: "0.12.7"           # fixe SEMPRE
          enable-cache: true
          cache-dependency-glob: "uv.lock"

      - run: uv sync --locked --group test
      - run: uv run pytest -q
```

| Opção do `setup-uv` | Para quê |
|---|---|
| `version` | fixar a versão do uv. Sem isso, uma atualização do uv pode quebrar seu CI num dia aleatório |
| `enable-cache` | persiste `~/.cache/uv` entre execuções |
| `cache-dependency-glob` | invalida o cache só quando o `uv.lock` muda |
| `python-version` | instala e fixa a versão do Python |
| `prune-cache` | roda `uv cache prune --ci` antes de salvar, encolhendo o que é enviado |

### Portões que valem a pena

```yaml
      - name: o lock está atualizado?
        run: uv lock --check

      - name: os limites inferiores funcionam?
        run: uv sync --resolution lowest-direct && uv run pytest -q

      - name: vulnerabilidades conhecidas
        run: uv audit --preview-features audit-command

      - name: SBOM
        run: uv export --format cyclonedx1.5 -o sbom.json
```

---

## 4. GitLab CI

```yaml
default:
  image: ghcr.io/astral-sh/uv:0.12.7-python3.13-bookworm-slim

variables:
  UV_CACHE_DIR: .uv-cache
  UV_LINK_MODE: copy

cache:
  key:
    files: [uv.lock]
  paths: [.uv-cache]

testes:
  script:
    - uv sync --locked --group test
    - uv run pytest -q --junitxml=report.xml
  after_script:
    - uv cache prune --ci
  artifacts:
    reports:
      junit: report.xml
```

`UV_CACHE_DIR` dentro do diretório do projeto é obrigatório: o GitLab só consegue
cachear caminhos relativos ao workspace.

---

## 5. pre-commit

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/uv-pre-commit
    rev: 0.12.7
    hooks:
      - id: uv-lock            # regenera o lock se o pyproject mudou
      - id: uv-export          # mantém requirements.txt sincronizado
        args: ["--no-dev", "--no-hashes", "-o", "requirements.txt"]

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.16.5
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
```

```bash
uv tool install pre-commit
pre-commit install
```

O hook `uv-lock` é o que impede, de forma automática, o erro nº 1 de equipes: alterar o
`pyproject.toml` e esquecer de commitar o `uv.lock`.

---

## 6. Produção sem container

**Serviço systemd:**

```ini
# /etc/systemd/system/minhaapi.service
[Unit]
Description=Minha API
After=network.target

[Service]
Type=exec
User=app
WorkingDirectory=/opt/minhaapi
Environment="PATH=/opt/minhaapi/.venv/bin:/usr/bin:/bin"
ExecStart=/opt/minhaapi/.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Deploy:

```bash
cd /opt/minhaapi
git pull
uv sync --locked --no-dev
sudo systemctl restart minhaapi
```

> **Chame o binário do `.venv` diretamente no `ExecStart`**, não `uv run`. O `systemd`
> tem um ambiente mínimo, e `uv run` tentaria sincronizar (e talvez acessar a rede) na
> hora de subir o serviço — exatamente o momento em que você não quer surpresa.

**AWS Lambda / funções serverless:**

```bash
uv export --format requirements.txt --no-dev --no-hashes -o requirements.txt
uv pip install --target ./pacote -r requirements.txt --python-platform x86_64-manylinux2014 --python-version 3.13
cd pacote && zip -r ../deploy.zip . && cd .. && zip -g deploy.zip app.py
```

As flags `--python-platform` e `--python-version` fazem o uv baixar os wheels da
**plataforma de destino**, não da sua. Sem elas, você empacota wheels do macOS ARM e a
função quebra no Linux x86-64 — um erro clássico e caro de diagnosticar.

---

## 7. Ambientes sem rede (air-gapped)

```bash
# Na máquina COM rede
uv export --format requirements.txt --no-dev -o requirements.txt
uv pip download -r requirements.txt -d ./rodas --python-platform x86_64-manylinux2014 --python-version 3.13

# Copiar ./rodas para a máquina isolada, então:
uv pip install --no-index --find-links ./rodas -r requirements.txt
```

Alternativa: montar um índice interno (devpi, Artifactory) e apontar `UV_DEFAULT_INDEX`.

---

## 8. Diagnóstico em CI

| Sintoma | Causa | Correção |
|---|---|---|
| build lento mesmo com cache | `COPY . .` antes do `uv sync` | separe as camadas (Regra 1) |
| `Invalid cross-device link` | cache e destino em volumes distintos | `UV_LINK_MODE=copy` |
| `lockfile needs to be updated` | alguém não commitou o lock | `uv lock` e commit; hook `uv-lock` |
| imagem enorme | uv, cache e Python duplicado dentro | multiestágio; `UV_PYTHON_DOWNLOADS=never` |
| container demora a iniciar | `.pyc` gerado a cada start, ou `uv run` no `CMD` | `UV_COMPILE_BYTECODE=1`; `PATH` do `.venv` |
| funciona local, quebra no Lambda | wheels da plataforma errada | `--python-platform` / `--python-version` |
| CI quebrou "sozinho" | versão do uv não fixada | `version: "0.12.7"` no `setup-uv` |

---

## Autoteste

1. Por que `--no-install-project` na primeira camada muda tanto o tempo de build?
2. Por que `--locked` em vez de `uv sync` numa imagem de produção?
3. O que causa `Invalid cross-device link` em Docker, e qual a correção?
4. Por que não usar `uv run` no `CMD`? Qual a alternativa?
5. O que `UV_PYTHON_DOWNLOADS=never` protege numa imagem?
6. Por que fixar a versão do uv no `setup-uv`?
7. Qual hook do pre-commit previne o esquecimento do `uv.lock`?
8. Como empacotar para Lambda a partir de um MacBook ARM, sem quebrar?
9. Como instalar dependências numa máquina sem internet?
10. Por que `cache-dependency-glob: uv.lock` e não o padrão?

---

**Fontes (consultadas em 31/08/2026):**
[docs.astral.sh/uv/guides/integration/docker](https://docs.astral.sh/uv/guides/integration/docker/) ·
[docs.astral.sh/uv/guides/integration/github](https://docs.astral.sh/uv/guides/integration/github/) ·
[github.com/astral-sh/setup-uv](https://github.com/astral-sh/setup-uv) ·
[github.com/astral-sh/uv-pre-commit](https://github.com/astral-sh/uv-pre-commit).

**Próximo:** [20-migracao-de-pip-poetry-conda.md](20-migracao-de-pip-poetry-conda.md)
