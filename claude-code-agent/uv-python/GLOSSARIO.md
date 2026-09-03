# Glossário

> Todos os termos técnicos usados neste curso. Ordem alfabética.
> Atualizado em 31/08/2026.

---

**Air-gapped** — ambiente sem qualquer acesso à internet, por política de segurança. Com
uv, exige wheels pré-baixados ou um índice interno. Ver [19](19-uv-em-docker-e-ci.md).

**Ambiente virtual** (*virtual environment*) — diretório contendo um interpretador Python
e um `site-packages` próprios, isolando as dependências de um projeto. Definido pela
PEP 405. No uv, é o `.venv`, criado e mantido automaticamente.

**`archive-v0`** — o bucket do cache do uv onde ficam os **wheels já descompactados**.
É a origem dos hard links e ~90% do tamanho do cache. Ver [14](14-cache-e-instalacao.md).

**`argparse`** — módulo da biblioteca padrão para interpretar argumentos de linha de
comando. Usado no projeto-modelo.

**Astral** — empresa fundada por Charlie Marsh, criadora do Ruff, do uv e do `ty`.
Adquirida pela OpenAI em 19/03/2026.

**Backtracking** — estratégia de busca em que, ao encontrar um beco sem saída, o algoritmo
volta à última decisão e tenta outra. O resolvedor do `pip` usa; o PubGrub faz melhor,
com aprendizado de conflitos.

**Build backend** — o programa que transforma o seu repositório em sdist e wheel. Ex.:
`uv_build`, `hatchling`, `setuptools`, `maturin`. Declarado em `[build-system]`.
Ver [18](18-publicacao-e-build-backend.md).

**Build frontend** — quem **pede** o build ao backend: `uv build`, `pip install`,
`python -m build`.

**Bytecode** — a forma compilada intermediária do Python, guardada em `.pyc`. Gerado no
primeiro import, ou na instalação com `UV_COMPILE_BYTECODE=1`.

**Cache** — armazenamento local do uv em `~/.cache/uv`, com metadados de índice, wheels
baixados e wheels extraídos. Ver `uv cache dir`, `uv cache size`, `uv cache prune`.

**CDCL** (*Conflict-Driven Clause Learning*) — família de algoritmos de satisfatibilidade
que aprendem cláusulas a partir de conflitos. O PubGrub é um CDCL sobre intervalos de
versão. Ver [60](60-teoria-avancada.md).

**Clone** (*reflink*) — modo de ligação em que o sistema de arquivos faz cópia
*copy-on-write*: compartilha o espaço até alguém escrever. Disponível em APFS, Btrfs, XFS.
`--link-mode clone`.

**conda-forge** — canal comunitário e gratuito de pacotes conda. **Distinto** dos canais
`defaults` da Anaconda, que exigem licença paga para organizações grandes.

**Confusão de dependência** (*dependency confusion*) — ataque em que se publica, num
índice público, um pacote com o nome de um pacote interno da vítima. Prevenido com
`default = true` ou `explicit = true`. Ver [21](21-seguranca-e-cadeia-de-suprimentos.md).

**Constraint** (`constraint-dependencies`) — restrição de versão aplicada a um pacote
**se** ele entrar no grafo; não o adiciona. A ferramenta de escape mais segura.

**Cooldown** — política de não adotar pacotes publicados nos últimos N dias, como defesa
contra pacotes maliciosos recém-publicados. Implementada com `exclude-newer = "14 days"`.

**CycloneDX** — um dos dois formatos padrão de SBOM (o outro é SPDX).
`uv export --format cyclonedx1.5`.

**Declaração / Resolução / Materialização** — as três camadas do modelo do uv:
`pyproject.toml` (o que quero) → `uv.lock` (o que foi decidido) → `.venv` (o que existe
aqui). **O conceito central do curso.** Ver [10](10-fundamentos.md).

**Dependência direta** — a que você declarou. **Transitiva** — a que veio junto, exigida
por outra.

**Distribuição** (*distribution*) — o pacote publicável. Não confundir com o nome do
módulo importado: instala-se `pillow`, importa-se `PIL`.

**`dist-info`** — diretório de metadados criado ao instalar um wheel, com `METADATA`,
`RECORD` e `WHEEL`.

**Editable install** — instalação que aponta para o código-fonte em vez de copiá-lo, de
modo que editar o fonte afeta imediatamente o ambiente. O uv instala o seu projeto assim
por padrão.

**Egg** — formato de pacote antigo, do setuptools. **Obsoleto**; substituído pelo wheel.

**`exclude-newer`** — opção que ignora tudo publicado depois de uma data ou janela.
Serve para reprodução histórica e para cooldown de segurança.

**Extra** — conjunto opcional de dependências que **o usuário da sua biblioteca** pode
ativar: `pip install pacote[postgres]`. Declarado em `[project.optional-dependencies]`.
Distinto de **grupo**.

**Fork / forking** (na resolução) — divisão do espaço de ambientes em regiões disjuntas,
cada uma com sua própria solução, gravadas no mesmo lock com marcadores. É o que torna a
resolução universal possível. Ver [13](13-resolucao-de-dependencias.md).

**Free-threaded** — build do CPython sem GIL (PEP 703). Instalável com
`uv python install 3.14t`.

**GIL** (*Global Interpreter Lock*) — cadeado que impede dois threads Python de executarem
bytecode simultaneamente. Opcional a partir do 3.13.

**Grupo de dependências** (*dependency group*) — conjunto de dependências **só de
desenvolvimento**, declarado em `[dependency-groups]` (PEP 735). **Não é publicado.**
Distinto de **extra**.

**Hard link** — entrada de diretório adicional apontando para o mesmo inode. Como o uv
instala pacotes sem copiar bytes. ⚠️ Editar o arquivo afeta todas as referências.

**Índice** (*index*) — servidor que lista e serve pacotes. O PyPI é o público. Configurado
com `[[tool.uv.index]]`.

**Inode** — a estrutura do sistema de arquivos que guarda os dados e metadados de um
arquivo. Vários nomes podem apontar para o mesmo inode (hard links).

**`link-mode`** — como o uv materializa arquivos no `.venv`: `hardlink` (padrão), `clone`,
`copy`, `symlink`.

**Lockfile** — arquivo com as versões e hashes exatos de todas as dependências resolvidas.
No uv: `uv.lock`. **Deve ser versionado no Git.**

**`manylinux`** — perfil de compatibilidade que define quais bibliotecas de sistema um
wheel Linux pode usar (PEP 600). Ex.: `manylinux_2_28_x86_64`.

**Marcador de ambiente** (*environment marker*) — condição da PEP 508 que restringe uma
dependência a certos ambientes: `; sys_platform == 'linux'`.

**MVS** (*Minimal Version Selection*) — modelo do Go: escolhe a **menor** versão que
satisfaz, dispensando resolvedor. Discutido em [60](60-teoria-avancada.md).

**NP-difícil / NP-completo** — classes de complexidade. Resolver dependências é
NP-completo, por redução a partir do 3-SAT.

**Override** (`override-dependencies`) — substituição da declaração de dependência de um
terceiro. ⚠️ É você afirmando que o autor errou; use após verificar.

**PEP** (*Python Enhancement Proposal*) — documento de proposta e especificação do Python.
As relevantes estão listadas em [95-referencias](95-referencias.md#2-padrões--as-peps-na-ordem-em-que-importam).

**PEP 723** — metadados embutidos em script, no bloco `# /// script`. A base do modo
script do uv.

**`pylock.toml`** — formato **padronizado** de lockfile, definido pela PEP 751 (2025).
O uv exporta e consome; ainda não é seu formato nativo.

**PubGrub** — o algoritmo de resolução usado pelo uv (via `pubgrub-rs`), criado por
Natalie Weizenbaum para o `pub` do Dart. Produz explicações legíveis de conflito.

**PyPA** (*Python Packaging Authority*) — o grupo de mantenedores de `pip`, `setuptools`,
`twine`, `hatch` e da documentação de empacotamento.

**PyPI** (*Python Package Index*) — o índice público oficial, em `pypi.org`.

**`pyproject.toml`** — o arquivo central de um projeto Python moderno. Contém metadados
(PEP 621), sistema de build (PEP 517/518) e configuração de ferramentas (`[tool.*]`).

**`pyvenv.cfg`** — arquivo de três a seis linhas dentro do `.venv` que diz onde está o
Python real. É o mecanismo do isolamento.

**Registry** — ver **índice**.

**Resolução** — o processo de escolher uma versão de cada pacote que satisfaça todas as
restrições.

**Resolução universal** — resolução que vale para **todas** as plataformas e versões de
Python da faixa declarada, com marcadores. É o que o `uv.lock` contém.

**Ruff** — linter e formatador Python em Rust, da Astral. Usado por baixo do `uv format`.

**SAT** (satisfatibilidade booleana) — problema de decidir se uma fórmula proposicional
tem atribuição verdadeira. Resolução de dependências reduz a ele.

**SBOM** (*Software Bill of Materials*) — lista formal de tudo que compõe um software.
Exigida por regulação crescente. `uv export --format cyclonedx1.5`.

**sdist** (*source distribution*) — `.tar.gz` com o código-fonte. Precisa ser
**construído** na máquina do usuário: lento e sujeito a falha.

**`site-packages`** — diretório onde os pacotes instalados ficam, dentro do ambiente.

**Sources** (`[tool.uv.sources]`) — mapeamento de um nome de pacote para uma origem
específica (workspace, Git, caminho, índice). **Não é publicado no wheel.**

**`sys.path`** — a lista de diretórios em que o Python procura módulos ao importar.

**Trusted Publishing** — publicação no PyPI usando token OIDC de curta duração emitido
pelo CI, sem segredo armazenado. O padrão recomendado desde 2023.

**Typosquatting** — publicar pacote com nome parecido com um popular, esperando erro de
digitação.

**`ty`** — verificador de tipos em Rust da Astral, usado por baixo do `uv check`. Em beta
em 31/08/2026, com alvo de release estável em 2026.

**`uv.lock`** — o lockfile do uv. Formato próprio, universal, com hashes.
Ver [12](12-o-modelo-de-projeto.md).

**`uv_build`** — o build backend próprio do uv, escrito em Rust. Padrão do `uv init`.

**`uvx`** — atalho para `uv tool run`: executa uma ferramenta em ambiente efêmero.

**`.venv`** — o diretório do ambiente virtual do projeto, criado pelo uv. **Nunca deve
ir para o Git.**

**Wheel** (`.whl`) — pacote binário pré-construído (PEP 427). Instalar é apenas
descompactar. Rápido e seguro (não executa código na instalação).

**Workspace** — conjunto de pacotes no mesmo repositório, com **um** `uv.lock` e **um**
`.venv`. Conceito importado do Cargo. Ver [17](17-workspaces-e-monorepo.md).

---

## Siglas rápidas

| Sigla | Significado |
|---|---|
| CDCL | Conflict-Driven Clause Learning |
| CI/CD | Integração Contínua / Entrega Contínua |
| CVE | Common Vulnerabilities and Exposures |
| GIL | Global Interpreter Lock |
| MIT / Apache-2.0 | licenças permissivas de software livre |
| MVS | Minimal Version Selection |
| OIDC | OpenID Connect |
| PEP | Python Enhancement Proposal |
| PSF | Python Software Foundation |
| PyPA | Python Packaging Authority |
| PyPI | Python Package Index |
| SAT | Boolean Satisfiability |
| SBOM | Software Bill of Materials |
| TLS | Transport Layer Security |
| TOML | Tom's Obvious Minimal Language |
| TUF | The Update Framework |
| WSL | Windows Subsystem for Linux |

---

**Volte para:** [00-MAPA.md](00-MAPA.md)
