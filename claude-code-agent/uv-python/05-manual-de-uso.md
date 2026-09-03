# 05 · Manual de uso — referência de comandos

> **Nível:** iniciante → intermediário · **Atualizado em:** 31/08/2026 · **uv 0.12.7**
> Organizado **por tarefa**, não em ordem alfabética. Use `Ctrl+F`.
> Todas as flags foram conferidas contra `uv <comando> --help` da 0.12.7 nesta máquina.

---

## 0. Panorama: os 23 comandos de topo

```
uv auth       Gerenciar autenticação em índices
uv run        Executar um comando ou script
uv init       Criar um projeto novo
uv add        Adicionar dependências ao projeto
uv remove     Remover dependências do projeto
uv version    Ler ou alterar a versão do projeto
uv sync       Atualizar o ambiente do projeto
uv lock       Atualizar o lockfile
uv export     Exportar o lockfile para outro formato
uv tree       Mostrar a árvore de dependências
uv format     Formatar o código Python do projeto        (preview)
uv check      Rodar verificações no projeto              (preview)
uv audit      Auditar as dependências do projeto         (preview)
uv tool       Rodar e instalar programas de pacotes Python
uv python     Gerenciar versões e instalações de Python
uv pip        Interface compatível com pip
uv venv       Criar um ambiente virtual
uv build      Empacotar (sdist e wheel)
uv publish    Enviar para um índice
uv workspace  Inspecionar workspaces
uv cache      Gerenciar o cache
uv self       Gerenciar o próprio executável do uv
uv help       Documentação de um comando
```

Ajuda de qualquer um: `uv help <comando>` (longa) ou `uv <comando> --help` (curta).

---

## 1. Começar um projeto

| Comando | O que faz | Quando usar |
|---|---|---|
| `uv init NOME` | cria projeto com layout `src/`, `pyproject.toml`, `.python-version`, `.gitignore` e repositório Git | padrão |
| `uv init` | idem, no diretório atual | pasta já existe |
| `uv init --app NOME` | projeto de aplicação | um programa que você roda |
| `uv init --lib NOME` | biblioteca; acrescenta `py.typed` | algo que outros vão importar |
| `uv init --package NOME` | força projeto empacotável | precisa de `[project.scripts]` |
| `uv init --script arq.py` | cria script único com cabeçalho PEP 723 | automação de um arquivo só |
| `uv init --bare` | só o `pyproject.toml`, sem README/src/git | você quer controlar tudo |
| `uv init --python 3.13` | fixa a versão de Python já na criação | |
| `uv init --no-workspace` | não anexar ao workspace pai | criando projeto dentro de outro |
| `uv init --vcs none` | não inicializar Git | |
| `uv init --build-backend hatch` | usa outro backend (`hatch`, `flit`, `pdm`, `setuptools`, `maturin`, `scikit`) | precisa de extensão C/Rust |

**Diferença real entre `--app` e `--lib`** (verificado nesta máquina):

```
--app:  src/nome/__init__.py
--lib:  src/nome/__init__.py + src/nome/py.typed
```
Ambos usam layout `src/` e backend `uv_build`. A diferença é o marcador `py.typed`,
que sinaliza a verificadores de tipo que a sua biblioteca tem anotações confiáveis.

---

## 2. Dependências

### 2.1 Adicionar — `uv add`

```bash
uv add requests                    # última versão compatível, com limite inferior
uv add "django>=5,<6"              # faixa explícita (sintaxe PEP 508)
uv add "pandas==2.3.3"             # versão exata
uv add requests httpx rich         # várias de uma vez
```

| Flag | Efeito |
|---|---|
| `--dev` | vai para o grupo `dev` (não é instalado por quem usa sua biblioteca) |
| `--group NOME` | grupo de dependências nomeado (`docs`, `lint`, `test`) |
| `--optional EXTRA` | vira um *extra* opcional (`pip install meupkg[extra]`) |
| `--editable` | instala em modo editável (para dependências locais) |
| `--script ARQ.py` | adiciona ao cabeçalho PEP 723 de um script, não ao projeto |
| `--bounds lower\|major\|minor\|exact` | que tipo de limite escrever no `pyproject.toml` |
| `--raw` | escreve a especificação exatamente como você digitou, sem inferir limites |
| `--frozen` | adiciona sem re-resolver o lock |
| `--no-sync` | atualiza os arquivos mas não instala |
| `--marker "sys_platform=='linux'"` | aplica um marcador de ambiente às dependências |
| `--extra NOME` | ativa um extra da dependência (ex.: `uv add "fastapi" --extra standard`) |
| `--package NOME` | num workspace, adiciona ao membro indicado |

**Origens além do PyPI:**

```bash
uv add "ruff @ git+https://github.com/astral-sh/ruff"          # Git
uv add "meupkg @ git+https://github.com/org/repo" --tag v1.2.0 # Git, tag fixa
uv add "meupkg @ git+https://github.com/org/repo" --branch dev # Git, branch
uv add "meupkg @ git+https://github.com/org/repo" --rev abc123 # Git, commit
uv add ./pacotes/comum --editable                               # caminho local, editável
uv add "https://exemplo.com/pkg-1.0-py3-none-any.whl"          # URL direta
```

### 2.2 Remover — `uv remove`

```bash
uv remove requests
uv remove --dev pytest
uv remove --group docs mkdocs
uv remove --script analise.py pandas
```
Tira do `pyproject.toml`, re-resolve o lock e sincroniza o ambiente.

### 2.3 Ver — `uv tree`

```bash
uv tree                      # árvore completa
uv tree --depth 1            # só as diretas
uv tree --package requests   # a subárvore de um pacote
uv tree --invert             # "quem depende de quê" — o mais útil na depuração
uv tree --outdated           # mostra qual versão mais nova existe
uv tree --no-dedupe          # repete subárvores em vez de resumir
```

> **`--invert` é o comando que você vai amar** no dia em que precisar descobrir
> *por que diabos* `urllib3` foi parar no seu ambiente.

---

## 3. Grupos, extras e a diferença entre eles

Este é o ponto que mais confunde. Guarde a distinção:

| | **Extra** (`[project.optional-dependencies]`) | **Grupo** (`[dependency-groups]`, PEP 735) |
|---|---|---|
| Quem vê | **quem instala a sua biblioteca** | **só você e sua equipe** |
| Sintaxe do consumidor | `pip install meupkg[postgres]` | não existe — não é publicado |
| Para que serve | funcionalidade opcional do software | ferramentas de desenvolvimento |
| Exemplos | `[async]`, `[postgres]`, `[redis]` | `dev`, `test`, `docs`, `lint` |
| Vai no wheel publicado | ✅ sim | ❌ não |

```toml
[project.optional-dependencies]
postgres = ["psycopg[binary]>=3.2"]
redis = ["redis>=5.0"]

[dependency-groups]
dev = ["pytest>=8", "pytest-cov>=5"]
docs = ["mkdocs-material>=9"]
lint = ["ruff>=0.6"]
```

```bash
uv sync --extra postgres         # com um extra
uv sync --all-extras             # todos
uv sync --group docs             # com um grupo
uv sync --only-group lint        # somente esse grupo (útil no CI: instala pouco)
uv sync --no-dev                 # sem o grupo dev (produção)
uv sync --no-default-groups      # ignora os grupos marcados como padrão
uv sync --all-groups
```

> **Regra prática:** se um usuário da sua biblioteca pode querer aquilo → **extra**.
> Se só quem desenvolve precisa → **grupo**. Colocar `pytest` como extra é um erro
> clássico que polui a instalação de quem consome seu pacote.

---

## 4. Executar código

### 4.1 `uv run` — o cavalo de batalha

```bash
uv run python                       # REPL no ambiente do projeto
uv run python script.py
uv run -m pytest                    # rodar um módulo
uv run meucomando                   # entry point do [project.scripts]
uv run script.py                    # script com PEP 723
```

| Flag | Efeito |
|---|---|
| `-w`, `--with PKG` | roda com um pacote extra, **sem** adicioná-lo ao projeto |
| `--with-requirements arq.txt` | idem, a partir de um arquivo |
| `--with-editable ./caminho` | idem, em modo editável |
| `--isolated` | ambiente virgem, ignora o `.venv` do projeto |
| `--no-sync` | não sincroniza antes (mais rápido; assume ambiente correto) |
| `--frozen` | não re-resolve o lock |
| `--locked` | falha se o lock estiver desatualizado |
| `--env-file .env` | carrega variáveis de um arquivo `.env` |
| `--no-project` | ignora qualquer projeto ao redor |
| `--python 3.12` | força a versão do interpretador |
| `--exact` | sincronização exata: remove pacotes sobrando |
| `--all-packages` | (workspace) instala todos os membros |
| `-s`, `--script` | trata o argumento como script mesmo sem extensão `.py` |
| `--gui-script` | (Windows) roda com `pythonw`, sem janela de console |

**Truque muito útil:**
```bash
uv run --with ipython ipython
```
Um IPython com todas as dependências do seu projeto disponíveis, sem sujar o
`pyproject.toml` com uma dependência que só você usa.

### 4.2 `uvx` / `uv tool run` — programas isolados

```bash
uvx ruff check .                       # roda e descarta
uvx ruff@0.15.0 check .                # versão fixa
uvx --from httpie http GET example.com # pacote ≠ nome do comando
uvx --with pandas jupyter lab          # ferramenta + dependência extra
uvx --python 3.12 mypy .               # sob outra versão de Python
```

### 4.3 `uv tool` — instalar de vez

```bash
uv tool install ruff                       # instala e expõe o executável
uv tool install "mkdocs-material" --with mkdocs-git-revision-date-localized-plugin
uv tool list                               # o que está instalado
uv tool upgrade ruff                       # atualizar uma
uv tool upgrade --all                      # todas
uv tool uninstall ruff
uv tool uninstall --all
uv tool dir                                # onde ficam os ambientes
uv tool update-shell                       # garantir o PATH
uv tool audit                              # vulnerabilidades nas ferramentas
```

Substituição direta do `pipx`. Cada ferramenta tem seu ambiente virtual próprio;
apenas os executáveis são expostos em `~/.local/bin`.

---

## 5. Ambiente e lockfile

### 5.1 `uv sync` — pôr o ambiente no estado do lock

```bash
uv sync                     # o normal
uv sync --locked            # falha se o lock estiver desatualizado  ← use no CI
uv sync --frozen            # usa o lock como está, sem re-resolver
uv sync --no-dev            # sem dependências de desenvolvimento     ← produção
uv sync --inexact           # não remove pacotes extras do ambiente
uv sync --reinstall         # reinstala tudo do zero
uv sync --reinstall-package requests
uv sync --dry-run           # mostra o que faria
uv sync --no-install-project  # só as dependências, sem o projeto     ← camada Docker
uv sync --python-platform linux --python-version 3.12   # para outra plataforma
uv sync --output-format json  # saída legível por máquina
```

**O trio que você precisa distinguir:**

| Flag | Re-resolve? | Escreve `uv.lock`? | Falha se lock velho? |
|---|---|---|---|
| (nenhuma) | se preciso | sim | não |
| `--frozen` | não | não | não |
| `--locked` | não | não | **sim** |

Use `--locked` em CI e em builds de imagem. Use `--frozen` em runtime de container,
onde você quer velocidade e sabe que o lock está certo.

### 5.2 `uv lock` — só resolver, sem instalar

```bash
uv lock                          # gerar/atualizar
uv lock --upgrade                # atualizar tudo que puder
uv lock --upgrade-package requests   # atualizar só um pacote
uv lock --check                  # verificar se está atualizado (não escreve)
uv lock --resolution lowest      # menor versão possível de tudo
uv lock --resolution lowest-direct # menor das diretas, maior das transitivas
uv lock --prerelease allow       # aceitar pré-lançamentos
uv lock --exclude-newer 2026-01-01  # ignorar tudo publicado depois dessa data
```

> `--exclude-newer` é uma arma poderosa e pouco conhecida: permite reproduzir a
> resolução como ela teria sido em uma data passada, e serve tanto para depuração
> histórica quanto para "cooldown" de segurança (não adotar pacote publicado ontem).

### 5.3 `uv export` — gerar outros formatos

```bash
uv export --format requirements.txt -o requirements.txt
uv export --format requirements.txt --no-hashes --no-dev -o requirements.txt
uv export --format pylock.toml -o pylock.toml       # PEP 751, padrão oficial
uv export --format cyclonedx1.5 -o sbom.json        # SBOM para conformidade
uv export --all-packages                            # workspace inteiro
uv export --only-group dev
```

Saída real deste curso (`--no-hashes`):

```
# This file was autogenerated by uv via the following command:
#    uv export --no-hashes --format requirements.txt
-e .
certifi==2026.7.22
    # via requests
...
```

> **Quando exportar:** quando algo fora do uv precisa consumir a lista — um scanner de
> segurança corporativo, uma imagem base que só tem `pip`, uma plataforma de deploy que
> exige `requirements.txt`. **A fonte da verdade continua sendo o `uv.lock`.** Nunca
> edite o arquivo exportado.

### 5.4 `uv venv` — quando você quer o ambiente na mão

```bash
uv venv                          # cria .venv com o Python padrão
uv venv --python 3.13            # com versão específica
uv venv meuambiente              # com outro nome
uv venv --seed                   # já com pip e setuptools dentro (compatibilidade)
uv venv --system-site-packages   # enxerga os pacotes do sistema
uv venv --clear                  # apaga e recria
```

Verificação real desta máquina:
```
Using CPython 3.14.7
Creating virtual environment at: v1
Activate with: source v1/bin/activate
```

> **Atenção:** `uv venv` sozinho escolhe o Python *preferido do uv*, que pode ser um
> gerenciado recém-baixado — e não o do `.python-version` se você estiver fora do
> projeto. Dentro de um projeto, prefira deixar o `uv sync` criar o `.venv`.

---

## 6. Interface pip — `uv pip`

Existe para **migração e compatibilidade**. Não gerencia `pyproject.toml` nem `uv.lock`.

```bash
uv pip install requests                 # instala no ambiente ativo/descoberto
uv pip install -r requirements.txt
uv pip install -e .                     # o projeto atual, editável
uv pip uninstall requests
uv pip list                             # o que está instalado
uv pip freeze                           # formato requirements.txt
uv pip show requests                    # detalhes de um pacote
uv pip tree                             # árvore do ambiente
uv pip check                            # conferir compatibilidade das versões instaladas
uv pip compile requirements.in -o requirements.txt   # substituto do pip-compile
uv pip sync requirements.txt            # ambiente = exatamente esse arquivo
```

| Diferença em relação ao pip | Detalhe |
|---|---|
| **Não** instala no Python do sistema por padrão | precisa de `--system` (e você não deve querer) |
| Muito mais rápido | resolução paralela + cache global |
| Mensagens de conflito muito melhores | diz qual par de restrições é incompatível |
| Não tem `pip install --user` | por desenho: use `uv tool install` |
| `uv pip compile` é multiplataforma opcional | `--universal` gera resolução para todas as plataformas |

> **Opinião:** use `uv pip` só durante a migração ou em scripts legados. O modo projeto
> (`uv add`/`uv sync`) é estritamente melhor porque produz um lock universal. Ver
> [20-migracao](20-migracao-de-pip-poetry-conda.md).

---

## 7. Gerenciar Python — `uv python`

```bash
uv python list                       # instalados + disponíveis
uv python list --only-installed
uv python list --all-versions
uv python install 3.13               # instalar
uv python install 3.11 3.12 3.13     # várias
uv python install --reinstall 3.13
uv python upgrade 3.13               # atualizar o patch (3.13.4 → 3.13.15)
uv python pin 3.13                   # escreve .python-version no projeto
uv python pin --resolved 3.13        # grava a versão exata resolvida
uv python find 3.12                  # caminho do interpretador
uv python dir                        # onde ficam
uv python uninstall 3.11
uv python uninstall --all
uv python update-shell               # expor pythonX.Y no PATH
```

**Como escrever a versão desejada** — todas estas formas funcionam:

```
3.13                         # o patch mais novo do 3.13
3.13.2                       # exato
>=3.11,<3.14                 # faixa
cpython@3.13                 # implementação específica
pypy@3.11                    # PyPy
3.14t  ou  3.14+freethreaded # build sem GIL (PEP 703)
/usr/bin/python3.12          # caminho absoluto
```

Ordem em que o uv procura um interpretador:
1. `--python` na linha de comando
2. `UV_PYTHON`
3. `.python-version` do projeto (ou de um diretório acima)
4. `requires-python` do `pyproject.toml`
5. um Python já gerenciado pelo uv
6. um Python do `PATH` do sistema
7. baixa um novo (a menos que `UV_PYTHON_DOWNLOADS=never`)

---

## 8. Empacotar e publicar

```bash
uv build                       # gera sdist e wheel em dist/
uv build --sdist               # só o sdist
uv build --wheel               # só o wheel
uv build --all-packages        # todos os membros do workspace
uv build --out-dir ./saida
```

Saída real (projeto de teste desta máquina):
```
Building source distribution...
Building wheel from source distribution...
Successfully built dist/demo-0.1.0.tar.gz
Successfully built dist/demo-0.1.0-py3-none-any.whl
```

```bash
uv publish                                     # envia dist/* para o PyPI
uv publish --index testpypi                    # para um índice nomeado
uv publish --token "$PYPI_TOKEN"
uv publish --trusted-publishing automatic      # OIDC no GitHub Actions, sem token
```

> **Recomendação forte:** em CI, use **Trusted Publishing** (OIDC). Ele elimina o segredo
> de longa duração — não existe token para vazar. É o padrão da PyPI desde 2023.

Gerenciar versão do projeto:

```bash
uv version                   # ler (saída real: "demo 0.1.0")
uv version 1.0.0             # definir
uv version --bump patch      # 0.1.0 → 0.1.1
uv version --bump minor      # 0.1.0 → 0.2.0
uv version --bump major      # 0.1.0 → 1.0.0
uv version --short           # só o número
uv version --dry-run
```

---

## 9. Workspaces (monorepo)

```toml
# pyproject.toml na raiz
[tool.uv.workspace]
members = ["pacotes/*"]
exclude = ["pacotes/experimental"]
```

```bash
uv workspace list             # membros
uv workspace metadata         # metadados em JSON
uv workspace dir NOME         # caminho de um membro
uv sync --all-packages        # instalar todos
uv run --package api pytest   # rodar dentro de um membro
uv add --package api fastapi  # adicionar dependência a um membro
uv build --all-packages
```

Um único `uv.lock` na raiz governa o workspace inteiro — é o que garante que os membros
nunca divirjam de versão. Detalhes em [17-workspaces](17-workspaces-e-monorepo.md).

---

## 10. Cache

```bash
uv cache dir       # onde fica
uv cache size      # quanto ocupa   (preview)
uv cache prune     # remove o que não é mais alcançável — seguro, use no CI
uv cache prune --ci  # otimizado para CI: remove wheels construídos, mantém baixados
uv cache clean     # apaga tudo
uv cache clean requests   # apaga as entradas de um pacote
```

Saída real desta máquina em 31/08/2026: `217247744` bytes ≈ **207 MiB**.

| Situação | Use |
|---|---|
| disco cheio | `uv cache prune` primeiro; `clean` só se não bastar |
| CI com cache persistido | `uv cache prune --ci` ao final do job |
| erro estranho de instalação | `uv cache clean` + `uv sync --reinstall` |

---

## 11. Autenticação em índices — `uv auth`

```bash
uv auth login empresa       # guarda credencial no cofre do sistema
uv auth token empresa       # exibe o token guardado
uv auth logout empresa
uv auth dir                 # onde as credenciais ficam
```

Alternativa por variáveis (o padrão em CI):
```bash
export UV_INDEX_EMPRESA_USERNAME="usuario"
export UV_INDEX_EMPRESA_PASSWORD="senha"
```
O trecho `EMPRESA` corresponde ao `name` do índice em `[[tool.uv.index]]`, em maiúsculas.

---

## 12. Qualidade de código (preview na 0.12.7)

```bash
uv format                # formata com Ruff
uv format --check        # só verifica, não altera — use no CI
uv format --diff         # mostra o que mudaria
uv check                 # verificação de tipos com ty
uv audit                 # vulnerabilidades conhecidas
uv audit --output-format json
```

Silenciar os avisos de preview:
```bash
uv format --preview-features format-command
uv check  --preview-features check-command
uv audit  --preview-features audit-command
```

Ou de uma vez, no `pyproject.toml`:
```toml
[tool.uv]
preview-features = ["format-command", "check-command", "audit-command"]
```

> **Opinião profissional:** eu ainda mantenho `ruff` e `mypy`/`ty` como dependências
> explícitas do grupo `lint` nos projetos sérios, porque quero **a versão travada no
> lock**, não a que o uv decidir baixar. `uv format` e `uv check` são ótimos para
> scripts, protótipos e para quem está começando.

---

## 13. Flags globais (valem para quase todo comando)

| Flag | Efeito |
|---|---|
| `-q` / `-v` / `-vv` | menos / mais / muito mais saída |
| `--offline` | proibir rede; só cache |
| `-n`, `--no-cache` | ignorar o cache |
| `--directory DIR` | mudar de diretório antes de executar |
| `--project DIR` | usar o projeto deste diretório |
| `--config-file arq.toml` | usar outro arquivo de configuração |
| `--no-config` | ignorar `pyproject.toml`/`uv.toml` de configuração |
| `--color auto\|always\|never` | cor na saída |
| `--native-tls` / `--system-certs` | usar certificados do sistema |
| `--allow-insecure-host HOST` | pular verificação TLS (perigoso) |
| `--no-progress` | sem barras de progresso (logs de CI) |
| `--managed-python` / `--no-managed-python` | exigir / proibir Python gerenciado pelo uv |
| `--no-python-downloads` | não baixar Python |

---

## 14. Configuração: `[tool.uv]` no `pyproject.toml`

As chaves que valem a pena conhecer:

```toml
[tool.uv]
required-version = ">=0.12,<0.13"     # recusa uv fora dessa faixa
package = false                        # projeto não empacotável (só ambiente)
default-groups = ["dev"]               # grupos instalados por padrão no sync
environments = ["sys_platform == 'linux'", "sys_platform == 'darwin'"]
required-environments = ["sys_platform == 'darwin' and platform_machine == 'arm64'"]
constraint-dependencies = ["urllib3>=2"]      # limita sem adicionar
override-dependencies = ["numpy>=1.26"]       # sobrepõe o que outro pacote pediu
exclude-dependencies = ["pacote-ruim"]        # remove do grafo
conflicts = [[{ extra = "cpu" }, { extra = "gpu" }]]   # extras mutuamente exclusivos
exclude-newer = "2026-01-01T00:00:00Z"        # congela o índice numa data
link-mode = "hardlink"                        # hardlink | copy | symlink | clone
compile-bytecode = true                       # gera .pyc na instalação
no-build-isolation-package = ["flash-attn"]   # pacotes que exigem build sem isolamento

[[tool.uv.index]]
name = "empresa"
url = "https://artifactory.empresa.com/api/pypi/simple"
default = true

[tool.uv.sources]
comum = { workspace = true }                          # membro do workspace
minha-lib = { git = "https://github.com/org/lib", tag = "v1.2" }
torch = [                                              # fonte condicional
  { index = "torch-cpu", marker = "sys_platform != 'linux'" },
  { index = "torch-cu124", marker = "sys_platform == 'linux'" },
]

[tool.uv.workspace]
members = ["pacotes/*"]
```

**Onde a configuração pode morar**, em ordem de prioridade (a primeira ganha):

1. flags da linha de comando
2. variáveis de ambiente `UV_*`
3. `uv.toml` no diretório do projeto
4. `[tool.uv]` no `pyproject.toml`
5. `uv.toml` de usuário: `~/.config/uv/uv.toml` (Linux/macOS) ou `%APPDATA%\uv\uv.toml`
6. `uv.toml` de sistema: `/etc/uv/uv.toml`

> `uv.toml` tem prioridade sobre `[tool.uv]` **no mesmo diretório**, e quando existe,
> o `[tool.uv]` do `pyproject.toml` é ignorado por completo naquele nível — não é uma
> fusão. Isso pega muita gente.

---

## 15. Obsoleto ou depreciado — não use

| Antigo | Situação | Use |
|---|---|---|
| `UV_INDEX_URL` | depreciado | `UV_DEFAULT_INDEX` ou `[[tool.uv.index]]` |
| `UV_EXTRA_INDEX_URL` | depreciado | `UV_INDEX` ou `[[tool.uv.index]]` |
| `--native-tls` / `UV_NATIVE_TLS` | renomeado | `--system-certs` / `UV_SYSTEM_CERTS` |
| `INSTALLER_NO_MODIFY_PATH` | nome antigo | `UV_NO_MODIFY_PATH` |
| `uv pip install --system` | funciona, mas é armadilha | ambiente de projeto ou `uv tool` |
| `[tool.uv] dev-dependencies` | substituído | `[dependency-groups] dev` (PEP 735) |
| `main.py` na raiz do `uv init` | mudou na 0.7+ | layout `src/` |
| `pip-tools` (`pip-compile`) | superado | `uv pip compile` ou `uv lock` |

---

## 16. Atalhos que só quem usa há tempo conhece

```bash
uv run --with rich --with httpx python      # ambiente descartável com o que quiser
uv run --isolated --no-project python       # Python limpo, ignorando tudo ao redor
uvx uv@0.9.5 --version                      # rodar outra versão do próprio uv
uv tree --invert --package urllib3          # quem trouxe esse pacote para cá?
uv lock --exclude-newer "$(date -d '30 days ago' -Iseconds)"   # cooldown de 30 dias
uv sync --only-group lint                   # CI de lint que instala quase nada
uv run --env-file .env python -m app        # variáveis do .env sem biblioteca extra
uv pip compile --universal requirements.in  # lock multiplataforma no modo pip
uv python install --reinstall 3.13          # consertar Python gerenciado corrompido
uv cache prune --ci                         # cache de CI enxuto
uv add --bounds exact requests              # travar `==` no pyproject, não só no lock
uv build && uv publish --trusted-publishing automatic   # release sem segredo
UV_LINK_MODE=copy uv sync                   # quando cache e projeto estão em discos diferentes
```

---

## Autoteste

1. Qual a diferença entre `--extra` e `--group`, e qual dos dois aparece para quem
   instala a sua biblioteca?
2. Explique a diferença de comportamento entre `uv sync`, `uv sync --frozen` e
   `uv sync --locked`. Qual usar em CI?
3. Você quer rodar um Jupyter com as dependências do projeto, mas sem adicioná-lo ao
   `pyproject.toml`. Qual comando?
4. Qual comando descobre **quem** trouxe uma dependência transitiva indesejada?
5. Escreva o comando que gera um SBOM CycloneDX a partir do lock.
6. Qual é a ordem de precedência entre `uv.toml`, `[tool.uv]` e variáveis `UV_*`?
7. Cite três configurações depreciadas e seus substitutos.
8. O que faz `--exclude-newer` e cite dois usos legítimos.
9. Por que `uv pip install` existe se o modo projeto é melhor?
10. Qual comando publica no PyPI sem nenhum token guardado, e por que isso é mais seguro?

---

**Fontes:** `uv <comando> --help` da versão 0.12.7 executado localmente em 31/08/2026;
[docs.astral.sh/uv/reference/cli](https://docs.astral.sh/uv/reference/cli/);
[docs.astral.sh/uv/reference/settings](https://docs.astral.sh/uv/reference/settings/).

**Próximo:** [06-exemplos.md](06-exemplos.md)
