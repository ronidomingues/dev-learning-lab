# 06 · Exemplos — 14 receitas completas

> **Nível:** iniciante → avançado · **Atualizado em:** 31/08/2026 · **uv 0.12.7**
> Todo código aqui é **completo e executável**. Nada de `...` no meio.
>
> **O que foi executado nesta máquina em 31/08/2026:** os comandos dos exemplos 1, 2, 5,
> 6 e 7 (incluindo o workspace inteiro, montado do zero, com as saídas reais reproduzidas
> abaixo). Os exemplos 3, 4, 8, 9, 10, 13 e 14 usam comandos e sintaxe de configuração
> **conferidos individualmente** contra `uv --help` e a documentação oficial da 0.12.7,
> mas o cenário completo não foi rodado ponta a ponta. Os exemplos 11 e 12 (Docker e CI)
> **não puderam ser executados** — sem acesso ao daemon Docker nem a um runner nesta
> sessão. Onde há saída literal transcrita, ela é real.

---

## Exemplo 1 — Script de um arquivo só, com dependências (PEP 723)

**Problema:** você tem um script de 20 linhas que precisa de uma biblioteca. Não quer
criar projeto, `requirements.txt` nem ambiente virtual.

**Solução:**

```python
# clima.py
# /// script
# requires-python = ">=3.11"
# dependencies = ["httpx>=0.28"]
# ///
"""Mostra a previsão de temperatura para uma cidade, via API aberta."""

import sys

import httpx

CIDADES = {
    "sao-paulo": (-23.55, -46.63),
    "rio": (-22.91, -43.17),
    "belem": (-1.46, -48.50),
}


def main() -> None:
    cidade = sys.argv[1] if len(sys.argv) > 1 else "sao-paulo"
    if cidade not in CIDADES:
        print(f"Cidades disponíveis: {', '.join(CIDADES)}")
        raise SystemExit(1)

    lat, lon = CIDADES[cidade]
    resposta = httpx.get(
        "https://api.open-meteo.com/v1/forecast",
        params={"latitude": lat, "longitude": lon, "current": "temperature_2m"},
        timeout=10,
    )
    resposta.raise_for_status()
    temp = resposta.json()["current"]["temperature_2m"]
    print(f"{cidade}: {temp} °C")


if __name__ == "__main__":
    main()
```

```bash
uv run clima.py rio
```

**Explicação:** o bloco `# /// script ... # ///` é o padrão **PEP 723**, aceito
oficialmente desde 2024. O uv o lê, monta um ambiente efêmero (cacheado), baixa o Python
certo se necessário e executa. O arquivo é autocontido: você pode mandá-lo por e-mail e
quem tiver uv roda sem instrução nenhuma.

**Variação — deixar o uv escrever o cabeçalho:**

```bash
uv init --script clima.py --python 3.11
uv add --script clima.py httpx
```

---

## Exemplo 2 — Projeto de aplicação, do zero ao executável

**Problema:** criar uma aplicação de linha de comando instalável.

```bash
uv init --app conversor && cd conversor
uv add rich
```

```python
# src/conversor/__init__.py
"""Conversor de unidades com saída formatada."""

from rich.console import Console
from rich.table import Table

console = Console()

FATORES = {
    ("km", "milha"): 0.621371,
    ("milha", "km"): 1.609344,
    ("kg", "libra"): 2.204623,
    ("libra", "kg"): 0.453592,
    ("celsius", "fahrenheit"): None,  # tratado à parte: não é multiplicação
}


def converter(valor: float, de: str, para: str) -> float:
    if (de, para) == ("celsius", "fahrenheit"):
        return valor * 9 / 5 + 32
    fator = FATORES.get((de, para))
    if fator is None:
        raise ValueError(f"conversão não suportada: {de} → {para}")
    return valor * fator


def main() -> None:
    tabela = Table(title="Conversões de exemplo")
    tabela.add_column("Valor", justify="right")
    tabela.add_column("De")
    tabela.add_column("Para")
    tabela.add_column("Resultado", justify="right", style="green")

    casos = [(10.0, "km", "milha"), (5.0, "kg", "libra"), (30.0, "celsius", "fahrenheit")]
    for valor, de, para in casos:
        tabela.add_row(f"{valor:g}", de, para, f"{converter(valor, de, para):.4f}")

    console.print(tabela)


if __name__ == "__main__":
    main()
```

```bash
uv run conversor
```

**Explicação:** `uv init --app` já criou `[project.scripts] conversor = "conversor:main"`,
por isso `uv run conversor` funciona. O `uv add rich` travou a versão no `uv.lock`.
Nenhum ambiente virtual foi ativado manualmente.

---

## Exemplo 3 — Biblioteca com testes e grupos de dependências

**Problema:** escrever algo que outras pessoas vão importar, com testes que **não**
sejam instalados junto.

```bash
uv init --lib estatistica && cd estatistica
uv add --group test pytest pytest-cov
uv add --group lint ruff
```

```python
# src/estatistica/__init__.py
"""Estatísticas descritivas mínimas, sem dependências externas."""

from __future__ import annotations

from collections.abc import Sequence


def media(valores: Sequence[float]) -> float:
    """Média aritmética. Levanta ValueError para sequência vazia."""
    if not valores:
        raise ValueError("sequência vazia não tem média")
    return sum(valores) / len(valores)


def mediana(valores: Sequence[float]) -> float:
    """Mediana. Para tamanho par, a média dos dois centrais."""
    if not valores:
        raise ValueError("sequência vazia não tem mediana")
    ordenados = sorted(valores)
    meio = len(ordenados) // 2
    if len(ordenados) % 2 == 1:
        return float(ordenados[meio])
    return (ordenados[meio - 1] + ordenados[meio]) / 2


def variancia(valores: Sequence[float], *, amostral: bool = True) -> float:
    """Variância. amostral=True usa n-1 (Bessel); False usa n."""
    n = len(valores)
    if n < 2 and amostral:
        raise ValueError("variância amostral exige ao menos 2 valores")
    m = media(valores)
    soma = sum((x - m) ** 2 for x in valores)
    return soma / (n - 1 if amostral else n)
```

```python
# tests/test_estatistica.py
import pytest

from estatistica import media, mediana, variancia


def test_media():
    assert media([1, 2, 3, 4]) == 2.5


def test_mediana_impar():
    assert mediana([3, 1, 2]) == 2


def test_mediana_par():
    assert mediana([4, 1, 3, 2]) == 2.5


def test_variancia_amostral():
    assert variancia([2, 4, 4, 4, 5, 5, 7, 9]) == pytest.approx(4.571428, rel=1e-5)


def test_variancia_populacional():
    assert variancia([2, 4, 4, 4, 5, 5, 7, 9], amostral=False) == pytest.approx(4.0)


@pytest.mark.parametrize("func", [media, mediana])
def test_vazio_levanta(func):
    with pytest.raises(ValueError):
        func([])
```

```bash
uv run pytest -q
uv run --only-group lint ruff check .
```

**Explicação:** `pytest` está no grupo `test`, não em `dependencies`. Quem instalar
`estatistica` do PyPI **não** recebe o pytest. O `--only-group lint` cria um ambiente
com quase nada — no CI, isso significa segundos em vez de minutos.

---

## Exemplo 4 — Extras opcionais (funcionalidade que o usuário escolhe)

**Problema:** sua biblioteca pode falar com PostgreSQL ou com Redis, mas ninguém precisa
dos dois.

```toml
# pyproject.toml
[project]
name = "cache-lib"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = ["pydantic>=2.0"]

[project.optional-dependencies]
postgres = ["psycopg[binary]>=3.2"]
redis = ["redis>=5.0"]
tudo = ["cache-lib[postgres,redis]"]

[dependency-groups]
dev = ["pytest>=8", "ruff>=0.6"]

[build-system]
requires = ["uv_build>=0.12,<0.13"]
build-backend = "uv_build"
```

```python
# src/cache_lib/__init__.py
"""Cache com backend escolhido em tempo de execução."""

from __future__ import annotations

from typing import Protocol


class Backend(Protocol):
    def get(self, chave: str) -> str | None: ...
    def set(self, chave: str, valor: str) -> None: ...


class MemoriaBackend:
    """Sempre disponível — não exige extra nenhum."""

    def __init__(self) -> None:
        self._dados: dict[str, str] = {}

    def get(self, chave: str) -> str | None:
        return self._dados.get(chave)

    def set(self, chave: str, valor: str) -> None:
        self._dados[chave] = valor


def criar_backend(tipo: str = "memoria", **kwargs: object) -> Backend:
    if tipo == "memoria":
        return MemoriaBackend()
    if tipo == "redis":
        try:
            import redis  # noqa: PLC0415
        except ImportError as erro:  # mensagem que ensina o usuário
            raise ImportError(
                "backend redis exige o extra: pip install 'cache-lib[redis]' "
                "(ou uv add 'cache-lib[redis]')"
            ) from erro
        return _RedisBackend(redis.Redis(**kwargs))
    raise ValueError(f"backend desconhecido: {tipo}")


class _RedisBackend:
    def __init__(self, cliente: object) -> None:
        self._c = cliente

    def get(self, chave: str) -> str | None:
        valor = self._c.get(chave)  # type: ignore[attr-defined]
        return valor.decode() if valor else None

    def set(self, chave: str, valor: str) -> None:
        self._c.set(chave, valor)  # type: ignore[attr-defined]
```

```bash
uv sync                    # só o núcleo
uv sync --extra redis      # com Redis
uv sync --all-extras       # tudo
```

**Explicação:** o `try/except ImportError` com mensagem instrutiva é o padrão de
biblioteca profissional. O usuário que erra recebe **o comando exato** para consertar,
não um `ModuleNotFoundError` cru.

---

## Exemplo 5 — Instalar e usar ferramentas sem sujar nada

**Problema:** você quer usar `ruff`, `httpie` e `jupyter` sem instalá-los no projeto.

```bash
# rodar e descartar
uvx ruff check .
uvx ruff format --diff .
uvx --from httpie http GET https://httpbin.org/json
uvx --with pandas --with matplotlib jupyter lab

# fixar versão da ferramenta
uvx ruff@0.15.0 check .

# instalar de vez as que você usa todo dia
uv tool install ruff
uv tool install "mkdocs-material" --with mkdocs-mermaid2-plugin
uv tool list
uv tool upgrade --all
```

Saída real de `uv tool list` nesta máquina:

```
ruff v0.16.5
- ruff
```

**Explicação:** `uvx` = `uv tool run`. Cada ferramenta ganha ambiente virtual próprio em
`~/.local/share/uv/tools`, e só o executável é exposto. Isso é exatamente o que o `pipx`
faz — mais rápido e sem precisar de Python instalado antes.

---

## Exemplo 6 — Migrar um projeto que usa `requirements.txt`

**Problema:** projeto antigo com `requirements.txt` e `requirements-dev.txt`.

```bash
cd projeto-antigo

# 1. Criar o pyproject.toml sem tocar em mais nada
uv init --bare

# 2. Importar as dependências
uv add -r requirements.txt
uv add --group dev -r requirements-dev.txt

# 3. Conferir que o ambiente ficou equivalente
uv run python -c "import django, celery; print('ok')"
uv run pytest

# 4. Só depois de os testes passarem, remover os arquivos antigos
git rm requirements.txt requirements-dev.txt
git add pyproject.toml uv.lock
git commit -m "migra dependências para uv"
```

**Se algo fora do uv ainda precisar do `requirements.txt`** (uma plataforma de deploy,
um scanner corporativo), gere-o a partir do lock em vez de mantê-lo à mão:

```bash
uv export --format requirements.txt --no-dev --no-hashes -o requirements.txt
```

E automatize para nunca ficar desatualizado (`.git/hooks/pre-commit` ou pre-commit):

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/uv-pre-commit
    rev: 0.12.7
    hooks:
      - id: uv-lock
      - id: uv-export
        args: ["--no-dev", "--no-hashes", "-o", "requirements.txt"]
```

---

## Exemplo 7 — Monorepo com workspace

**Problema:** uma API e uma biblioteca compartilhada no mesmo repositório, com uma única
resolução de dependências.

Estrutura:

```
monorepo/
├── pyproject.toml         # raiz: define o workspace
├── uv.lock                # UM lock para tudo
└── pacotes/
    ├── comum/             # biblioteca compartilhada
    └── api/               # aplicação que usa a biblioteca
```

```bash
mkdir monorepo && cd monorepo
cat > pyproject.toml <<'EOF'
[project]
name = "monorepo"
version = "0"
requires-python = ">=3.10"

[tool.uv.workspace]
members = ["pacotes/*"]
EOF

mkdir pacotes && cd pacotes
uv init --lib comum
uv init --app api
cd ..

cd pacotes/api && uv add comum && cd ../..
```

O `uv add comum` detecta que `comum` é membro do workspace e escreve sozinho:

```toml
# pacotes/api/pyproject.toml
dependencies = ["comum"]

[tool.uv.sources]
comum = { workspace = true }
```

Verificação real desta máquina:

```bash
uv workspace list
# api
# comum
# monorepo

uv sync --all-packages
# Resolved 3 packages in 0.98ms
# Checked 2 packages in 7ms
```

Uso diário:

```bash
uv run --package api python -m api      # rodar a API
uv run --package comum pytest           # testar só a biblioteca
uv add --package api fastapi            # dependência só para a API
uv build --all-packages                 # empacotar todos
```

**Explicação:** um único `uv.lock` na raiz governa todos os membros. É impossível o
`comum` usado pela API divergir do `comum` testado — o problema clássico de monorepo
Python resolvido por construção. Mais em [17-workspaces](17-workspaces-e-monorepo.md).

---

## Exemplo 8 — Múltiplas versões de Python e matriz de testes

**Problema:** garantir que sua biblioteca funciona de 3.10 a 3.14.

```bash
uv python install 3.10 3.11 3.12 3.13 3.14

for v in 3.10 3.11 3.12 3.13 3.14; do
  echo "=== Python $v ==="
  uv run --python "$v" --isolated pytest -q || echo "FALHOU em $v"
done
```

Com `tox`, sem instalar o tox no projeto:

```ini
# tox.ini
[tox]
env_list = py310, py311, py312, py313, py314
requires = tox>=4

[testenv]
runner = uv-venv-lock-runner
extras = test
commands = pytest {posargs}
```

```bash
uvx --with tox-uv tox
```

**Explicação:** `tox-uv` faz o tox usar o uv como backend, o que reduz o tempo de uma
matriz de 5 versões de minutos para segundos. A flag `--isolated` no loop garante que
cada rodada não reaproveita o `.venv` da anterior.

---

## Exemplo 9 — Testar os limites inferiores das dependências

**Problema:** seu `pyproject.toml` diz `pandas>=2.0`, mas você nunca testou com 2.0 —
só com a versão mais nova. Um usuário com 2.0 vai quebrar.

```bash
# Resolve para as MENORES versões compatíveis das dependências diretas
uv lock --resolution lowest-direct
uv sync
uv run pytest

# Voltar ao normal
uv lock
uv sync
```

No CI (GitHub Actions):

```yaml
name: testes
on: [push, pull_request]

jobs:
  testes:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python: ["3.11", "3.13"]
        resolution: ["highest", "lowest-direct"]
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v6
        with:
          version: "0.12.7"
          enable-cache: true
      - run: uv sync --group test --resolution ${{ matrix.resolution }} --python ${{ matrix.python }}
      - run: uv run pytest -q
```

**Explicação:** `lowest-direct` usa a menor versão das suas dependências **diretas** e a
mais nova das transitivas. É o ajuste certo: testa que os seus limites inferiores são
honestos, sem o inferno de resolver o ecossistema inteiro para 2019.

---

## Exemplo 10 — Ambiente reprodutível congelado numa data

**Problema:** um bug apareceu em produção depois de um deploy. Você quer reproduzir
exatamente a resolução de duas semanas atrás.

```bash
uv lock --exclude-newer 2026-08-17T00:00:00Z
uv sync
uv run pytest
```

Ou como política permanente de "cooldown" (não adotar pacote publicado ontem — defesa
contra pacote comprometido recém-publicado):

```toml
[tool.uv]
exclude-newer = "14 days"

# exceção para um pacote em que você quer atualizações rápidas de segurança
exclude-newer-package = { certifi = "0 days" }
```

**Explicação:** `--exclude-newer` filtra o índice por data de publicação. É a coisa mais
próxima de uma máquina do tempo que existe em empacotamento Python. Também é uma defesa
real de cadeia de suprimentos: a maioria dos ataques de pacote malicioso é descoberta em
poucos dias, e um cooldown de 14 dias te tira da linha de tiro.
Ver [21-seguranca](21-seguranca-e-cadeia-de-suprimentos.md).

---

## Exemplo 11 — Caso de produção: imagem Docker enxuta e rápida

**Problema:** imagem Docker de uma API FastAPI, com build rápido e camadas bem cacheadas.

```dockerfile
# syntax=docker/dockerfile:1

# ---------- estágio 1: construir o ambiente ----------
FROM ghcr.io/astral-sh/uv:0.12.7-python3.13-bookworm-slim AS builder

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

WORKDIR /app

# Camada 1: só as dependências. Muda raramente → cache aproveitado quase sempre.
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-dev

# Camada 2: o código. Muda a cada commit.
COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev

# ---------- estágio 2: imagem final, sem o uv ----------
FROM python:3.13-slim-bookworm

# Usuário sem privilégio
RUN groupadd -r app && useradd -r -g app app

COPY --from=builder --chown=app:app /app /app

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

USER app
WORKDIR /app
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health').read()" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
docker build -t minha-api . && docker run --rm -p 8000:8000 minha-api
```

**As sete decisões e o que cada uma ensina:**

| Decisão | Por quê |
|---|---|
| `--mount=type=bind` para `uv.lock` e `pyproject.toml` | os arquivos entram só nesse `RUN`; não viram camada permanente |
| `--mount=type=cache` no `~/.cache/uv` | o cache do uv persiste entre builds sem inchar a imagem |
| `--no-install-project` na primeira camada | separa "dependências" (lento, muda pouco) de "seu código" (rápido, muda sempre) |
| `UV_COMPILE_BYTECODE=1` | gera `.pyc` no build; o container inicia mais rápido |
| `UV_LINK_MODE=copy` | evita `Invalid cross-device link` entre o volume de cache e a camada |
| `UV_PYTHON_DOWNLOADS=never` | falha alto se o Python esperado não estiver na imagem, em vez de baixar 35 MB em silêncio |
| estágio final sem o uv | o binário do uv não vai para produção: imagem menor e superfície de ataque menor |

---

## Exemplo 12 — Caso de produção: pipeline completo de CI/CD

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push: { branches: [main] }
  pull_request:
  release: { types: [published] }

env:
  UV_VERSION: "0.12.7"

jobs:
  qualidade:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v6
        with:
          version: ${{ env.UV_VERSION }}
          enable-cache: true
          cache-dependency-glob: "uv.lock"

      # Falha se alguém alterou pyproject.toml e esqueceu de regerar o lock
      - name: lock está atualizado?
        run: uv lock --check

      - name: instalar só o necessário para lint
        run: uv sync --only-group lint

      - run: uv run ruff check --output-format=github .
      - run: uv run ruff format --check .

  testes:
    runs-on: ${{ matrix.os }}
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        python: ["3.11", "3.12", "3.13"]
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v6
        with:
          version: ${{ env.UV_VERSION }}
          enable-cache: true
      - run: uv sync --locked --group test --python ${{ matrix.python }}
      - run: uv run pytest -q --cov --cov-report=xml
      - uses: codecov/codecov-action@v4
        if: matrix.os == 'ubuntu-latest' && matrix.python == '3.13'

  seguranca:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v6
        with: { version: "0.12.7" }
      - run: uv audit --preview-features audit-command
      - name: gerar SBOM
        run: uv export --format cyclonedx1.5 -o sbom.json
      - uses: actions/upload-artifact@v4
        with: { name: sbom, path: sbom.json }

  publicar:
    if: github.event_name == 'release'
    needs: [qualidade, testes, seguranca]
    runs-on: ubuntu-latest
    environment: pypi
    permissions:
      id-token: write        # necessário para Trusted Publishing (OIDC)
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v6
        with: { version: "0.12.7" }
      - run: uv build
      - run: uv publish --trusted-publishing automatic
```

**O que este pipeline ensina:**

1. `uv lock --check` como **portão**: impede o clássico "esqueci de commitar o lock".
2. `--only-group lint` no job de qualidade: instala 3 pacotes em vez de 80.
3. `--locked` nos testes: garante que o CI testa exatamente o que está no repositório.
4. `enable-cache` + `cache-dependency-glob: uv.lock`: o cache só é invalidado quando o
   lock muda de verdade.
5. **Trusted Publishing** com `id-token: write`: publica no PyPI **sem nenhum segredo**
   armazenado. Se o repositório for comprometido, não há token para roubar.
6. SBOM como artefato: exigência crescente de conformidade (executiva 14028 nos EUA,
   CRA na União Europeia).

---

## Exemplo 13 — Dependência condicional por plataforma (o caso PyTorch)

**Problema:** você quer PyTorch com CUDA no Linux e a versão de CPU no macOS. Este é
*o* caso difícil clássico do empacotamento Python.

```toml
[project]
name = "treinamento"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = ["torch>=2.5"]

[[tool.uv.index]]
name = "pytorch-cpu"
url = "https://download.pytorch.org/whl/cpu"
explicit = true          # só usado por quem for explicitamente apontado a ele

[[tool.uv.index]]
name = "pytorch-cu124"
url = "https://download.pytorch.org/whl/cu124"
explicit = true

[tool.uv.sources]
torch = [
  { index = "pytorch-cu124", marker = "sys_platform == 'linux'" },
  { index = "pytorch-cpu", marker = "sys_platform != 'linux'" },
]
```

```bash
uv sync
uv run python -c "import torch; print(torch.__version__, torch.cuda.is_available())"
```

**Explicação e a armadilha:** `explicit = true` é **obrigatório** aqui. Sem isso, o uv
consideraria os índices do PyTorch para *qualquer* pacote, e um invasor poderia publicar
num deles um pacote com o nome de uma dependência sua — o ataque de **confusão de
dependência**. Com `explicit`, o índice só serve aos pacotes que o apontam por nome.

O `uv.lock` resultante contém **as duas** variantes, com marcadores. É a resolução
universal em ação: o mesmo lock serve para o dev no MacBook e para o servidor com GPU.

---

## Exemplo 14 — Script de manutenção que roda por `cron`, sem ambiente

**Problema:** um script que roda de madrugada no servidor, precisa de bibliotecas, e você
não quer manter um ambiente virtual para ele.

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["psycopg[binary]>=3.2", "httpx>=0.28"]
# ///
"""Verifica o tamanho do banco e alerta se passar do limite."""

import os
import sys

import httpx
import psycopg

LIMITE_GB = 50.0


def tamanho_do_banco_gb(dsn: str) -> float:
    with psycopg.connect(dsn) as conexao, conexao.cursor() as cursor:
        cursor.execute("SELECT pg_database_size(current_database())")
        (bytes_,) = cursor.fetchone()
    return bytes_ / 1024**3


def alertar(mensagem: str) -> None:
    webhook = os.environ.get("WEBHOOK_URL")
    if not webhook:
        print(mensagem, file=sys.stderr)
        return
    httpx.post(webhook, json={"text": mensagem}, timeout=10).raise_for_status()


def main() -> None:
    dsn = os.environ.get("DATABASE_URL")
    if not dsn:
        print("DATABASE_URL não definida", file=sys.stderr)
        raise SystemExit(2)

    gb = tamanho_do_banco_gb(dsn)
    print(f"banco: {gb:.2f} GB (limite {LIMITE_GB} GB)")
    if gb > LIMITE_GB:
        alertar(f"⚠️ banco em {gb:.2f} GB, acima do limite de {LIMITE_GB} GB")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
```

```bash
chmod +x verificar_banco.py
./verificar_banco.py
```

No `crontab`:

```cron
# m h  dom mon dow  comando
  0 3   *   *   *   cd /opt/scripts && /home/svc/.local/bin/uv run --script verificar_banco.py >> /var/log/verificar_banco.log 2>&1
```

**Explicação:** o shebang `#!/usr/bin/env -S uv run --script` faz o arquivo ser
executável direto. O `-S` do `env` permite passar vários argumentos no shebang (é uma
extensão do coreutils do GNU e do BSD moderno; **não funciona** em Unix muito antigo —
nesse caso, chame `uv run --script arquivo.py` explicitamente, como no `crontab` acima).

No cron, use **caminho absoluto** para o `uv`: o `PATH` do cron é mínimo e quase nunca
inclui `~/.local/bin`. Esse é o erro nº 1 de scripts uv em cron.

---

## Autoteste

1. Escreva o cabeçalho PEP 723 completo para um script que precisa de Python ≥ 3.12 e
   das bibliotecas `polars` e `httpx`.
2. Qual a diferença prática entre `--group test` e `--optional test` no exemplo 3?
3. No exemplo 7, quem escreveu `[tool.uv.sources] comum = { workspace = true }` — você
   ou o uv? Como isso aconteceu?
4. Por que `--resolution lowest-direct` é melhor que `lowest` para testar limites?
5. No Dockerfile do exemplo 11, por que `--no-install-project` aparece na primeira camada?
6. Por que `explicit = true` é obrigatório nos índices do exemplo 13? O que acontece sem?
7. Cite dois motivos para usar `exclude-newer` que não sejam depuração.
8. No exemplo 12, por que `id-token: write` é necessário — e o que ele substitui?
9. Qual é o erro nº 1 ao rodar scripts uv no cron?
10. Você precisa entregar um `requirements.txt` para uma plataforma legada. Qual é o
    comando, e por que você **não** deve editá-lo depois?

---

**Fontes:** comandos e saídas dos exemplos 1, 2, 5, 6 e 7 executados localmente em
31/08/2026 com uv 0.12.7 (Ubuntu 22.04.5); demais exemplos conferidos contra
`uv <comando> --help` da 0.12.7 e a documentação oficial —
[guias de integração](https://docs.astral.sh/uv/guides/integration/docker/),
[ação setup-uv](https://github.com/astral-sh/setup-uv) e
[índices e fontes](https://docs.astral.sh/uv/concepts/indexes/) — consultadas na mesma data.

**Próximo:** [07-projeto-modelo/README.md](07-projeto-modelo/README.md)
