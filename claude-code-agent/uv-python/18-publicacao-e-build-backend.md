# 18 · Construir e publicar — `uv build`, `uv publish` e o `uv_build`

> **Nível:** avançado · **Atualizado em:** 31/08/2026 · **uv 0.12.7**

Como o seu código vira um `.whl` e como esse `.whl` chega ao PyPI.

---

## 1. O que é um build backend

**PEP 517/518** (2017) separaram duas coisas que antes eram uma:

- o **frontend** — quem pede o build (`uv build`, `pip install`, `python -m build`);
- o **backend** — quem sabe transformar o seu repositório em `sdist` e `wheel`.

Você declara o backend no `pyproject.toml`:

```toml
[build-system]
requires = ["uv_build>=0.12,<0.13"]
build-backend = "uv_build"
```

O frontend lê isso, cria um **ambiente de build isolado**, instala o que está em
`requires`, importa o módulo `build-backend` e chama funções padronizadas
(`build_wheel`, `build_sdist`, `prepare_metadata_for_build_wheel`).

**Por que isso importou:** antes da PEP 517, o `setuptools` era o único caminho, porque
`pip` executava literalmente `python setup.py bdist_wheel`. Depois dela, qualquer um pode
escrever um backend — e foi assim que apareceram `flit`, `hatchling`, `pdm-backend`,
`maturin` (para Rust) e o `uv_build`.

---

## 2. Escolhendo o backend

| Backend | Escrito em | Para quê | Escolha se |
|---|---|---|---|
| **`uv_build`** | Rust | Python puro, layout `src/` | é o padrão do `uv init`; rápido; você já usa uv |
| **`hatchling`** | Python | Python puro, muito configurável | precisa de hooks de build, versionamento dinâmico, inclusão de arquivos complexa |
| **`flit_core`** | Python | pacotes simples, sem configuração | quer o mínimo absoluto |
| **`setuptools`** | Python | qualquer coisa, inclusive extensões C | projeto legado, ou precisa de `Extension` em C |
| **`maturin`** | Rust | extensões Rust (PyO3) | seu pacote tem código Rust |
| **`scikit-build-core`** | Python | extensões C/C++ com CMake | seu pacote tem CMake |
| **`meson-python`** | Python | C/C++/Fortran com Meson | é o que numpy e scipy usam |

```bash
uv init --build-backend hatch minhalib   # escolher na criação
```
Valores aceitos: `uv`, `hatch`, `flit`, `pdm`, `setuptools`, `maturin`, `scikit`.

> **Recomendação:** comece com `uv_build`. Ele é rápido, tem zero configuração e cobre o
> caso Python puro, que é a maioria. Troque para `hatchling` no dia em que precisar de
> algo que ele não faz — a troca custa três linhas no `pyproject.toml`, porque tudo o
> mais é PEP 621 padrão.
>
> **Ressalva honesta:** ao usar `uv_build` você acopla o *build* do seu pacote ao
> ecossistema Astral. É um acoplamento pequeno (ele é publicado no PyPI como qualquer
> outro backend, e qualquer frontend PEP 517 o usa), mas existe. Se essa dependência te
> incomoda depois de ler o [11-historia](11-historia.md), `hatchling` é a alternativa
> neutra e excelente.

### Configuração do `uv_build`

```toml
[tool.uv.build-backend]
module-name = "meu_pacote"          # se difere do `name` normalizado
module-root = "src"                 # padrão: "src"; use "" para layout plano
source-include = ["tests/**"]        # arquivos extras no sdist
source-exclude = ["**/*.tmp"]
data = { scripts = "bin", headers = "include" }
```

---

## 3. `uv build`

```bash
uv build                       # sdist + wheel em dist/
uv build --sdist               # só o sdist
uv build --wheel               # só o wheel
uv build --out-dir ./saida
uv build --package comum       # um membro do workspace
uv build --all-packages
uv build /caminho/de/outro/projeto
```

Saída real do projeto-modelo deste curso:

```
Building source distribution...
Building wheel from source distribution...
Successfully built dist/lockspect-0.1.0.tar.gz
Successfully built dist/lockspect-0.1.0-py3-none-any.whl
```

> **Note a segunda linha:** o uv constrói o wheel **a partir do sdist**, não da pasta de
> trabalho. Isso é deliberado e é a coisa certa: garante que o sdist contém tudo que é
> preciso para construir. Se você esqueceu um arquivo no sdist, o build do wheel falha
> **agora**, e não na máquina do usuário. Muitos backends não fazem isso.

### Inspecionar o que você produziu

```bash
unzip -l dist/lockspect-0.1.0-py3-none-any.whl
tar tzf dist/lockspect-0.1.0.tar.gz
```
Confira que **não** há segredos (`.env`, chaves), nem `.venv`, nem arquivos de teste que
você não queria distribuir. É o passo que quase todo mundo pula e que um dia dói.

```bash
uvx twine check dist/*
```
Valida os metadados (o PyPI recusa alguns formatos de README e classificadores inválidos).

---

## 4. Versionamento

```bash
uv version                 # ler:  "lockspect 0.1.0"
uv version 1.0.0           # definir
uv version --bump patch    # 0.1.0 → 0.1.1
uv version --bump minor    # 0.1.0 → 0.2.0
uv version --bump major    # 0.1.0 → 1.0.0
uv version --short         # imprime só "0.1.0" — útil em scripts
uv version --dry-run
```

**Versão derivada do Git** (sem duplicar o número em dois lugares) — precisa de outro
backend, porque o `uv_build` não faz versão dinâmica:

```toml
[build-system]
requires = ["hatchling", "hatch-vcs"]
build-backend = "hatchling.build"

[project]
name = "minhalib"
dynamic = ["version"]

[tool.hatch.version]
source = "vcs"
```
Agora `git tag v1.2.3` define a versão. É o padrão que eu recomendo para bibliotecas com
release frequente: uma fonte da verdade só.

---

## 5. `uv publish`

```bash
uv publish                                    # envia dist/* para o PyPI
uv publish --index testpypi                   # para um índice nomeado
uv publish --token "$PYPI_TOKEN"
uv publish --trusted-publishing automatic     # OIDC, sem token
uv publish dist/lockspect-0.1.0*              # arquivos específicos
uv publish --check-url https://pypi.org/simple  # pula o que já existe
```

Configurar um índice de teste:

```toml
[[tool.uv.index]]
name = "testpypi"
url = "https://test.pypi.org/simple/"
publish-url = "https://test.pypi.org/legacy/"
```

### Fluxo completo de um release, do começo ao fim

```bash
# 1. Verificar que está tudo limpo
uv lock --check
uv run pytest -q
uv run --only-group lint ruff check .

# 2. Subir a versão
uv version --bump minor
git add pyproject.toml uv.lock
git commit -m "release 0.2.0"
git tag v0.2.0

# 3. Construir e conferir
rm -rf dist/
uv build
uvx twine check dist/*
unzip -l dist/*.whl | head -30

# 4. Testar no TestPyPI primeiro (sempre)
uv publish --index testpypi
uvx --index https://test.pypi.org/simple/ --from lockspect==0.2.0 lockspect --version

# 5. Publicar de verdade
uv publish

# 6. Empurrar a tag (só depois que deu certo)
git push && git push --tags
```

---

## 6. Trusted Publishing — publique sem segredo nenhum

**O problema com tokens:** um token do PyPI é uma credencial de longa duração guardada
num "secret" do CI. Se alguém comprometer o repositório, um workflow malicioso pode
imprimir o token, e o atacante publica pacotes no seu nome. Isso já aconteceu com
projetos grandes.

**A solução (PyPI, desde 2023):** o GitHub Actions emite um **token OIDC de curta duração**
que prova "sou o workflow X do repositório Y". O PyPI confia nessa prova. Não existe
segredo armazenado.

Configuração, em duas partes:

**No PyPI:** projeto → *Publishing* → *Add a new publisher* → informe o dono, o
repositório, o nome do arquivo de workflow e o *environment*.

**No workflow:**

```yaml
publicar:
  if: github.event_name == 'release'
  runs-on: ubuntu-latest
  environment: pypi
  permissions:
    id-token: write        # ← isto é o que permite emitir o token OIDC
  steps:
    - uses: actions/checkout@v4
    - uses: astral-sh/setup-uv@v6
      with: { version: "0.12.7" }
    - run: uv build
    - run: uv publish --trusted-publishing automatic
```

> **Isto não é opcional na minha opinião — é o padrão mínimo de 2026.** Se você ainda tem
> `PYPI_API_TOKEN` num secret, troque hoje. Leva 10 minutos.

---

## 7. Publicar em índice privado

```toml
[[tool.uv.index]]
name = "empresa"
url = "https://artifactory.empresa.com/api/pypi/pypi-local/simple"
publish-url = "https://artifactory.empresa.com/api/pypi/pypi-local"
```

```bash
uv auth login empresa          # guarda credencial no cofre do sistema
uv publish --index empresa
```

Ou por variáveis, o normal em CI:

```bash
export UV_PUBLISH_USERNAME="ci-bot"
export UV_PUBLISH_PASSWORD="$ARTIFACTORY_TOKEN"
uv publish --index empresa
```

---

## 8. Armadilhas de publicação

| Armadilha | Consequência | Prevenção |
|---|---|---|
| Publicar uma versão errada | **PyPI não permite reenviar a mesma versão, nunca** — nem depois de apagar | teste sempre no TestPyPI antes |
| Segredo dentro do sdist | vazamento público e permanente | `source-exclude`; inspecionar o `.tar.gz` antes |
| README que o PyPI recusa | upload falha com erro obscuro | `uvx twine check dist/*` |
| Nome já em uso | erro no primeiro upload | conferir em `pypi.org/project/NOME` antes de escolher |
| Esquecer de limpar `dist/` | envia wheels antigos junto | `rm -rf dist/` antes de `uv build` |
| Wheel sem os arquivos de dados | funciona local, quebra instalado | inspecionar com `unzip -l` |
| Publicar `api` antes de `comum` (workspace) | dependência não resolve para o usuário | publicar as folhas primeiro |
| Deixar `[tool.uv.sources]` achando que vai junto | não vai — e é correto que não vá | declarar limites de versão reais nas dependências |

---

## 9. Os cinco porquês: por que empacotar Python era um pesadelo?

**1. Por que existiam tantos jeitos de construir um pacote?**
Porque, antes da PEP 517, todos eram variações de `setup.py` com truques diferentes.

**2. Por que `setup.py` gerou tanta variação?**
Porque era **código executável**, então cada autor podia fazer qualquer coisa: ler
arquivos, chamar `git`, gerar código, compilar. Não havia contrato — só convenção.

**3. Por que foi projetado como código executável?**
**Decisão histórica:** o `distutils` (2000) foi pensado como uma **biblioteca** que o
autor usava num script, no espírito "Python é a linguagem de configuração". Era o padrão
da época — o `Makefile` também é executável. Ninguém previu que ferramentas automáticas
precisariam ler metadados de 600 mil pacotes sem executar nada.

**4. Por que demorou 17 anos para separar frontend e backend?**
**Trade-off econômico:** a PEP 517 exigia coordenar `pip`, `setuptools`, `wheel` e o
ecossistema de build inteiro, com garantia de não quebrar nada. É um trabalho de anos, de
voluntários, sem financiamento — a mesma história do [11-historia](11-historia.md).

**5. Por que o `uv build` constrói o wheel a partir do sdist?**
Porque é a única forma de **verificar** que o sdist está completo. Construir o wheel da
pasta de trabalho esconde arquivos esquecidos, que só somem quando o usuário instala do
sdist. É uma escolha de projeto que troca alguns segundos de build por uma classe inteira
de bug eliminada. **Parada legítima: é um trade-off explícito de projeto, e o correto.**

---

## Autoteste

1. O que a PEP 517 separou, e por que isso importou?
2. Quando usar `hatchling` em vez de `uv_build`?
3. Por que o `uv build` constrói o wheel a partir do sdist?
4. Escreva os comandos para conferir o conteúdo de um wheel antes de publicar.
5. Por que "publicou versão errada" é um erro irreversível no PyPI?
6. Explique Trusted Publishing e por que ele é mais seguro que um token.
7. Qual permissão o workflow precisa para usar OIDC?
8. Como fazer a versão do pacote vir de uma tag do Git?
9. Num workspace, qual pacote publicar primeiro e por quê?
10. Por que `[tool.uv.sources]` não vai para o pacote publicado — e por que isso é certo?

---

**Fontes:** builds e saídas executados localmente em 31/08/2026 (uv 0.12.7) ·
[PEP 517](https://peps.python.org/pep-0517/) · [PEP 518](https://peps.python.org/pep-0518/) ·
[docs.astral.sh/uv/guides/package](https://docs.astral.sh/uv/guides/package/) ·
[docs.pypi.org/trusted-publishers](https://docs.pypi.org/trusted-publishers/).

**Próximo:** [19-uv-em-docker-e-ci.md](19-uv-em-docker-e-ci.md)
