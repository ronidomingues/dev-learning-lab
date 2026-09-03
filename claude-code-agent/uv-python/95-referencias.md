# 95 · Referências — specs, código-fonte, pessoas e onde perguntar

> **Nível:** todos · **Verificado em:** 31/08/2026

---

## 1. Fontes primárias do uv

| Recurso | Link | O que é |
|---|---|---|
| Repositório | [github.com/astral-sh/uv](https://github.com/astral-sh/uv) | código-fonte, issues, discussões |
| Documentação | [docs.astral.sh/uv](https://docs.astral.sh/uv/) | a referência viva |
| CHANGELOG | [CHANGELOG.md](https://github.com/astral-sh/uv/blob/main/CHANGELOG.md) | **a fonte mais confiável do que mudou** |
| Releases | [releases](https://github.com/astral-sh/uv/releases) | binários, notas, checksums |
| Referência de CLI | [reference/cli](https://docs.astral.sh/uv/reference/cli/) | todos os comandos e flags |
| Referência de configuração | [reference/settings](https://docs.astral.sh/uv/reference/settings/) | todas as chaves de `[tool.uv]` |
| Variáveis de ambiente | [reference/environment](https://docs.astral.sh/uv/reference/environment/) | todas as `UV_*` |
| Internals — Resolver | [reference/internals/resolver](https://docs.astral.sh/uv/reference/internals/resolver/) | como o PubGrub é usado ali dentro |
| Política de versões | [reference/policies/versioning](https://docs.astral.sh/uv/reference/policies/versioning/) | o que pode quebrar e quando |
| Blog da Astral | [astral.sh/blog](https://astral.sh/blog) | anúncios e decisões de projeto |

### Projetos irmãos e de apoio

| Projeto | Link | Papel |
|---|---|---|
| `python-build-standalone` | [github.com/astral-sh/python-build-standalone](https://github.com/astral-sh/python-build-standalone) | os interpretadores que `uv python install` baixa |
| `setup-uv` | [github.com/astral-sh/setup-uv](https://github.com/astral-sh/setup-uv) | ação do GitHub Actions |
| `uv-pre-commit` | [github.com/astral-sh/uv-pre-commit](https://github.com/astral-sh/uv-pre-commit) | hooks `uv-lock` e `uv-export` |
| Imagens Docker | [github.com/astral-sh/uv/pkgs/container/uv](https://github.com/astral-sh/uv/pkgs/container/uv) | `ghcr.io/astral-sh/uv` |
| Ruff | [github.com/astral-sh/ruff](https://github.com/astral-sh/ruff) | linter/formatador usado por `uv format` |
| ty | [github.com/astral-sh/ty](https://github.com/astral-sh/ty) | verificador de tipos usado por `uv check` |
| `pubgrub-rs` | [github.com/pubgrub-rs/pubgrub](https://github.com/pubgrub-rs/pubgrub) | a biblioteca de resolução |

---

## 2. Padrões — as PEPs, na ordem em que importam

| PEP | Título | Link |
|---|---|---|
| **621** | Storing project metadata in pyproject.toml | [peps.python.org/pep-0621](https://peps.python.org/pep-0621/) |
| **508** | Dependency specification for Python Software Packages | [pep-0508](https://peps.python.org/pep-0508/) |
| **440** | Version Identification and Dependency Specification | [pep-0440](https://peps.python.org/pep-0440/) |
| **517** | A build-system independent format for source trees | [pep-0517](https://peps.python.org/pep-0517/) |
| **518** | Specifying Minimum Build System Requirements | [pep-0518](https://peps.python.org/pep-0518/) |
| **723** | Inline script metadata | [pep-0723](https://peps.python.org/pep-0723/) |
| **735** | Dependency Groups in pyproject.toml | [pep-0735](https://peps.python.org/pep-0735/) |
| **751** | A file format to record Python dependencies (`pylock.toml`) | [pep-0751](https://peps.python.org/pep-0751/) |
| **427** | The Wheel Binary Package Format 1.0 | [pep-0427](https://peps.python.org/pep-0427/) |
| **503** | Simple Repository API | [pep-0503](https://peps.python.org/pep-0503/) |
| **600** | Future `manylinux` Platform Tags | [pep-0600](https://peps.python.org/pep-0600/) |
| **658** | Serve Distribution Metadata in the Simple Repository API | [pep-0658](https://peps.python.org/pep-0658/) |
| **668** | Marking Python base environments as "externally managed" | [pep-0668](https://peps.python.org/pep-0668/) |
| **405** | Python Virtual Environments | [pep-0405](https://peps.python.org/pep-0405/) |
| **680** | `tomllib`: Support for Parsing TOML in the Standard Library | [pep-0680](https://peps.python.org/pep-0680/) |
| **703** | Making the Global Interpreter Lock Optional in CPython | [pep-0703](https://peps.python.org/pep-0703/) |
| **722** | Dependency specification for single-file scripts (**rejeitada**) | [pep-0722](https://peps.python.org/pep-0722/) |
| **458** | Secure PyPI downloads with signed repository metadata (TUF) | [pep-0458](https://peps.python.org/pep-0458/) |
| **582** | Python local packages directory (**rejeitada**) | [pep-0582](https://peps.python.org/pep-0582/) |

**Especificações vivas** (que substituíram o texto das PEPs como fonte normativa):
[packaging.python.org/en/latest/specifications](https://packaging.python.org/en/latest/specifications/)

---

## 3. Documentação do ecossistema

| Recurso | Link |
|---|---|
| Python Packaging User Guide (PyPA) | [packaging.python.org](https://packaging.python.org/) |
| PyPI | [pypi.org](https://pypi.org/) · [blog.pypi.org](https://blog.pypi.org/) · [docs.pypi.org](https://docs.pypi.org/) |
| Trusted Publishers | [docs.pypi.org/trusted-publishers](https://docs.pypi.org/trusted-publishers/) |
| TestPyPI | [test.pypi.org](https://test.pypi.org/) |
| TOML | [toml.io/pt/v1.0.0](https://toml.io/pt/v1.0.0) (tem versão em português) |
| Documentação do CPython | [docs.python.org/3](https://docs.python.org/3/) |
| `venv` | [docs.python.org/3/library/venv.html](https://docs.python.org/3/library/venv.html) |

---

## 4. Onde perguntar (na ordem certa)

1. **Documentação oficial e CHANGELOG.** Resolve a maioria.
2. **[github.com/astral-sh/uv/issues](https://github.com/astral-sh/uv/issues)** — pesquise
   antes de abrir. A chance de já existir é alta.
3. **[github.com/astral-sh/uv/discussions](https://github.com/astral-sh/uv/discussions)** —
   para dúvidas de uso, não para bugs.
4. **[discuss.python.org — Packaging](https://discuss.python.org/c/packaging/14)** — para
   questões de padrão e de ecossistema, não específicas do uv. É onde as PEPs de
   empacotamento são debatidas por quem as escreve.
5. **Discord da Astral** — o convite está no README do repositório. Rápido para dúvidas
   curtas.
6. **Stack Overflow**, tags `uv` e `python-packaging`.

**Como fazer uma boa pergunta sobre uv** — inclua sempre:

```bash
uv --version
uv python list --only-installed
cat pyproject.toml
uv -vv <o comando que falhou> 2>&1 | tail -50
```
E diga o sistema operacional e a arquitetura. Sem isso, ninguém consegue ajudar.

---

## 5. Pessoas e contas que vale acompanhar

| Pessoa | Papel | Onde |
|---|---|---|
| **Charlie Marsh** | criador do Ruff e do uv; fundador da Astral, hoje na OpenAI | [github.com/charliermarsh](https://github.com/charliermarsh) |
| **Zanie Blue** | engenheira da equipe do uv; escreve sobre decisões de projeto | GitHub `zanieb` |
| **Simon Willison** | comentarista independente e criterioso sobre o ecossistema | [simonwillison.net](https://simonwillison.net/) |
| **Brett Cannon** | membro do Steering Council; autor de PEPs de empacotamento (incl. 751) | [snarky.ca](https://snarky.ca/) |
| **Paul Moore / Pradyun Gedam** | mantenedores do `pip` e da PyPA | discuss.python.org |
| **Henry Schreiner** | scikit-hep, `scikit-build-core`; o artigo sobre limites superiores | [iscinumpy.dev](https://iscinumpy.dev/) |
| **Claudio Jolowicz** | autor de *Hypermodern Python Tooling*, comantenedor do Nox | [cjolowicz.github.io](https://cjolowicz.github.io/) |
| **Eduardo Mendes (dunossauro)** 🇧🇷 | *Live de Python*, *FastAPI do Zero* | [youtube.com/@Dunossauro](https://www.youtube.com/@Dunossauro) |
| **Luciano Ramalho** 🇧🇷 | autor de *Python Fluente* | [github.com/ramalho](https://github.com/ramalho) |
| **Michael Kennedy** | *Talk Python To Me* | [talkpython.fm](https://talkpython.fm/) |

---

## 6. Ferramentas relacionadas

| Ferramenta | Link | Papel |
|---|---|---|
| `migrate-to-uv` | [github.com/mkniewallner/migrate-to-uv](https://github.com/mkniewallner/migrate-to-uv) | migra de Poetry, Pipenv e pip-tools (comunidade) |
| `tox-uv` | [github.com/tox-dev/tox-uv](https://github.com/tox-dev/tox-uv) | usa uv como backend do tox |
| `nox` | [github.com/wntrblm/nox](https://github.com/wntrblm/nox) | automação de sessões; suporta uv |
| `pip-audit` | [github.com/pypa/pip-audit](https://github.com/pypa/pip-audit) | auditoria de vulnerabilidades (PyPA) |
| `twine` | [github.com/pypa/twine](https://github.com/pypa/twine) | publicação e `twine check` |
| `hatchling` | [github.com/pypa/hatch](https://github.com/pypa/hatch) | build backend alternativo |
| `maturin` | [github.com/PyO3/maturin](https://github.com/PyO3/maturin) | build backend para extensões Rust |
| `pixi` | [github.com/prefix-dev/pixi](https://github.com/prefix-dev/pixi) | "o uv do conda-forge" |
| `devpi` | [github.com/devpi/devpi](https://github.com/devpi/devpi) | índice PyPI privado, open source |
| `pre-commit` | [pre-commit.com](https://pre-commit.com/) | hooks de commit |

---

## 7. Artigos e fontes citados neste curso

**Sobre o uv e a Astral:**
- [uv: Python packaging in Rust](https://astral.sh/blog/uv) — Astral, 15/02/2024
- [uv: Unified Python packaging](https://astral.sh/blog/uv-unified-python-packaging) — Astral, 20/08/2024
- [pyx: a Python-native package registry](https://astral.sh/blog/introducing-pyx) — Astral, ago/2025
- [OpenAI to acquire Astral](https://openai.com/index/openai-to-acquire-astral/) — OpenAI, 19/03/2026
- [Thoughts on OpenAI acquiring Astral](https://simonwillison.net/2026/mar/19/openai-acquiring-astral/) — Simon Willison, 19/03/2026
- [Astral Shuts Down pyx, Open-Sources the Part That Mattered](https://pydevtools.com/blog/astral-winds-down-pyx-open-sources-gpu-packaging/) — pydevtools, 2026
- [Talk Python #476 — Unified Python packaging with uv](https://talkpython.fm/episodes/show/476/unified-python-packaging-with-uv) — 2024
- [Talk Python #552 — Astral joins OpenAI](https://talkpython.fm/episodes/show/552/astral-joins-openai) — 2026
- [Why aren't we uv yet?](https://aleyan.com/blog/2026-why-arent-we-uv-yet/) — 2026

**Sobre resolução e teoria:**
- [PubGrub solver documentation](https://github.com/dart-lang/pub/blob/master/doc/solver.md) — Natalie Weizenbaum
- Mancinelli et al., *Managing the Complexity of Large Free and Open Source Package-Based
  Software Distributions*, ASE 2006
- [Minimal Version Selection](https://research.swtch.com/vgo-mvs) — Russ Cox, 2018
- [Should You Use Upper Bound Version Constraints?](https://iscinumpy.dev/post/bound-version-constraints/) — Henry Schreiner, 2021
- [The Purely Functional Software Deployment Model](https://edolstra.github.io/pubs/phd-thesis.pdf) — Eelco Dolstra, 2006

**Sobre segurança:**
- [Dependency Confusion](https://medium.com/@alex.birsan/dependency-confusion-4a5d60fec610) — Alex Birsan, 2021
- [Removing PGP from PyPI](https://blog.pypi.org/posts/2023-05-23-removing-pgp/) — PyPI, 2023
- [Trusted Publishers](https://docs.pypi.org/trusted-publishers/) — PyPI

---

## 8. Outros assuntos desta pasta relacionados

| Assunto | Relação |
|---|---|
| [docker](../docker/00-MAPA.md) | containers, imagens e camadas — base do arquivo 19 |
| [testes-automatizados](../testes-automatizados/00-MAPA.md) | pytest e CI — usados no projeto-modelo |
| [variaveis-de-ambiente-e-segredos](../variaveis-de-ambiente-e-segredos/00-MAPA.md) | `PATH`, `UV_*`, tokens e proxies |
| [commits-assinados](../commits-assinados/00-MAPA.md) | integridade de código e cadeia de suprimentos |
| [criptografia](../criptografia/00-MAPA.md) | SHA-256 nos lockfiles, TLS nos índices |
| [apis](../apis/00-MAPA.md) | o que os exemplos deste curso consomem |
| [engenharia-de-software-com-ia](../engenharia-de-software-com-ia/00-MAPA.md) | contexto do Codex e da aquisição da Astral |

---

## 9. Como verificar que este material continua válido

```bash
uv --version
```
Se for **0.13 ou superior**, houve uma quebra de compatibilidade de minor desde
31/08/2026: leia o [CHANGELOG](https://github.com/astral-sh/uv/blob/main/CHANGELOG.md)
antes de seguir os exemplos de configuração deste curso.

Os arquivos que envelhecem mais rápido, em ordem:
[65-estado-da-arte](65-estado-da-arte.md) → [80-custos](80-custos-e-licencas.md) →
[85-cursos](85-cursos-e-certificacoes.md) → [03-instalacao](03-instalacao.md) →
[05-manual-de-uso](05-manual-de-uso.md).

Os que praticamente não envelhecem:
[10-fundamentos](10-fundamentos.md), [11-historia](11-historia.md),
[60-teoria-avancada](60-teoria-avancada.md).

---

**Próximo:** [GLOSSARIO.md](GLOSSARIO.md)
