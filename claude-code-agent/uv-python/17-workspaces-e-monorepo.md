# 17 · Workspaces — vários pacotes, um lockfile

> **Nível:** avançado · **Atualizado em:** 31/08/2026 · **uv 0.12.7**

O conceito vem do Cargo (Rust), e o uv o adotou quase sem mudanças. É a resposta para
"tenho quatro pacotes Python no mesmo repositório".

---

## 1. O que é, exatamente

Um **workspace** é um conjunto de pacotes que:

- vivem no mesmo repositório;
- compartilham **um único `uv.lock`** e **um único `.venv`**, na raiz;
- podem depender uns dos outros por nome, resolvidos localmente;
- são versionados e publicados **separadamente**, se você quiser.

```
monorepo/
├── pyproject.toml         ← define o workspace (a "raiz")
├── uv.lock                ← UM lock para todos
├── .venv/                 ← UM ambiente para todos
└── pacotes/
    ├── comum/pyproject.toml
    ├── api/pyproject.toml
    └── worker/pyproject.toml
```

---

## 2. Montando um, do zero (verificado)

```bash
mkdir monorepo && cd monorepo
cat > pyproject.toml <<'EOF'
[project]
name = "monorepo"
version = "0"
requires-python = ">=3.10"

[tool.uv.workspace]
members = ["pacotes/*"]
exclude = ["pacotes/experimental"]
EOF

mkdir pacotes && cd pacotes
uv init --lib comum
uv init --app api
cd ..

cd pacotes/api && uv add comum && cd ../..
```

O `uv add comum` **detecta** que `comum` é membro do workspace e escreve sozinho:

```toml
# pacotes/api/pyproject.toml
dependencies = ["comum"]

[tool.uv.sources]
comum = { workspace = true }
```

Verificação real desta máquina (31/08/2026):

```bash
uv workspace list
```
```
api
comum
monorepo
```
```bash
uv sync --all-packages
```
```
Resolved 3 packages in 0.98ms
Checked 2 packages in 7ms
```

---

## 3. Os comandos

```bash
uv workspace list                # membros
uv workspace metadata            # metadados, em JSON
uv workspace dir comum           # caminho de um membro

uv sync                          # instala a raiz + suas dependências
uv sync --all-packages           # instala TODOS os membros
uv sync --package api            # só um membro (e suas dependências)

uv run --package api python -m api
uv run --package comum pytest
uv add --package api fastapi     # dependência de um membro específico
uv remove --package api fastapi

uv lock                          # UM lock para o workspace inteiro
uv build --all-packages          # empacota todos
uv build --package comum         # empacota um
uv version --package comum --bump minor
```

Repare que **quase todo comando aceita `--package`**. Sem ele, o comando age sobre a raiz.

---

## 4. Dependências compartilhadas

Para não repetir a mesma faixa de versão em cinco `pyproject.toml`, use a raiz como
fonte de restrição:

```toml
# pyproject.toml da raiz
[tool.uv]
constraint-dependencies = [
  "pydantic>=2.9,<3",
  "httpx>=0.28",
]

[tool.uv.workspace]
members = ["pacotes/*"]
```

Cada membro continua declarando o que **usa**:

```toml
# pacotes/api/pyproject.toml
dependencies = ["pydantic", "httpx"]
```

E a raiz garante a faixa comum. É o padrão que evita o pior problema de monorepo: dois
serviços com versões diferentes da mesma biblioteca central.

### Grupos compartilhados de desenvolvimento

```toml
# raiz
[dependency-groups]
dev = ["pytest>=8", "pytest-cov>=5"]
lint = ["ruff>=0.6"]
```
Um `uv sync` na raiz instala o ferramental para o repositório inteiro. Não repita isso
em cada membro.

---

## 5. Quando usar workspace — e quando **não**

### Use quando

- Os pacotes são **lançados juntos** ou quase.
- Um depende do outro e você quer editar os dois na mesma sessão, sem `pip install -e`.
- Você quer uma única resolução, garantindo que ninguém divirja.
- É um serviço quebrado em módulos (`api` + `worker` + `comum`).

### **Não** use quando

| Situação | Por quê | O que fazer |
|---|---|---|
| Os pacotes precisam de **versões diferentes** da mesma dependência | um workspace tem **uma** resolução; é a limitação fundamental | projetos separados, ou `[tool.uv.sources]` com caminho relativo |
| Ciclos de release muito distintos | atualizar um força relockar todos | repositórios separados |
| Um membro precisa de outro `requires-python` incompatível | a resolução é conjunta | separar |
| São só pastas de código, sem serem pacotes | workspace é para **pacotes** | um pacote único com submódulos |
| O repositório tem 200 pacotes | a resolução conjunta fica lenta e frágil | ferramentas de monorepo de verdade (Pants, Bazel) |

> **A limitação a memorizar:** *um workspace = uma resolução*. Se `api` exige
> `pydantic<2` e `worker` exige `pydantic>=2`, o workspace **não resolve** — e essa é uma
> propriedade desejada, não um defeito. Se você precisa mesmo dos dois, eles não deveriam
> compartilhar um ambiente.

---

## 6. A alternativa: `path sources` sem workspace

Quando você quer o link local **sem** a resolução compartilhada:

```toml
# pacotes/api/pyproject.toml
dependencies = ["comum"]

[tool.uv.sources]
comum = { path = "../comum", editable = true }

[tool.uv]
package = true
```

E na raiz, **não** declare `[tool.uv.workspace]`. Cada projeto passa a ter seu próprio
`uv.lock` e seu próprio `.venv`.

| | Workspace | Path source |
|---|---|---|
| Lockfiles | 1 | um por projeto |
| `.venv` | 1 | um por projeto |
| Versões podem divergir | ❌ | ✅ |
| Resolução | conjunta, consistente | independente |
| Espaço em disco | menor | maior (mitigado por hard links) |
| Complexidade | menor | maior |

---

## 7. Publicar membros de um workspace

Cada membro é publicado como um pacote independente:

```bash
uv build --package comum
uv publish dist/comum-*
```

**A armadilha crítica:** quando você publica `api`, que depende de `comum` via
`{ workspace = true }`, o wheel publicado contém apenas `comum` como nome — **sem** a
fonte local, porque `[tool.uv.sources]` **não vai para o pacote publicado**. Isso é
correto: quem instalar `api` do PyPI deve buscar `comum` no PyPI.

Mas então: **você precisa publicar `comum` primeiro, e precisa de um limite de versão
declarado.** Escreva:

```toml
# pacotes/api/pyproject.toml
dependencies = ["comum>=0.3,<0.4"]

[tool.uv.sources]
comum = { workspace = true }   # vale só no desenvolvimento
```

Sem o `>=0.3`, o wheel publicado pede "qualquer `comum`", e o usuário pode receber uma
versão incompatível.

---

## 8. CI para workspace

```yaml
jobs:
  testes:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        pacote: [comum, api, worker]
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v6
        with: { version: "0.12.7", enable-cache: true }
      - run: uv sync --locked --all-packages
      - run: uv run --package ${{ matrix.pacote }} pytest -q
```

Um `uv sync` monta o ambiente inteiro; a matriz só varia o alvo dos testes. Como o lock é
único, não há como um job testar uma combinação de versões que outro não testou.

---

## 9. Os cinco porquês: por que monorepo Python era difícil?

**1. Por que não posso simplesmente ter três pastas com `pyproject.toml`?**
Pode — mas `api` não enxerga `comum`, porque `comum` não está instalado no ambiente.

**2. Por que a solução tradicional (`pip install -e ../comum`) é ruim?**
Porque é um comando manual, fora do lock, que cada pessoa e cada máquina de CI precisa
lembrar de rodar. É reprodutibilidade por convenção — ou seja, nenhuma.

**3. Por que não existia um conceito de workspace no Python?**
**Decisão histórica:** o modelo de empacotamento nasceu para **uma distribuição por
repositório**. `distutils` (2000) e `setuptools` assumiam `setup.py` na raiz. Ninguém
padronizou "vários pacotes, uma resolução".

**4. Por que ninguém padronizou depois?**
Porque padronizar workspace exige padronizar também **resolução**, e a comunidade nunca
padronizou lockfile até a PEP 751 (2025) — que, aliás, cobre instalação, não workspace.
**Trade-off econômico:** cada ferramenta preferiu resolver para si (o Poetry tem
`path` dependencies; o PDM tem algo parecido; o Pants e o Bazel resolvem por fora) a
gastar anos num consenso.

**5. Por que o uv copiou do Cargo em vez de inventar?**
Porque o modelo do Cargo já é conhecido, testado em milhões de projetos Rust, e resolve
o problema com o mínimo de conceitos: raiz, membros, um lock. É a decisão de projeto
correta — não inventar onde já existe uma boa resposta. **Parada legítima: escolha de
projeto documentada no anúncio da 0.3.0**, que cita o Cargo por nome.

---

## Autoteste

1. O que exatamente é compartilhado entre membros de um workspace?
2. Quem escreveu `[tool.uv.sources] comum = { workspace = true }` no exemplo — e quando?
3. Cite três situações em que workspace é a escolha **errada**.
4. Qual é a limitação fundamental de um workspace, em cinco palavras?
5. Qual a diferença entre workspace e `path source`? Quando escolher a segunda?
6. Você publica `api` que depende de `comum`. Qual é a armadilha, e como evitá-la?
7. Escreva o comando que roda os testes de um único membro.
8. Como compartilhar limites de versão entre todos os membros?
9. Por que `pip install -e ../comum` é "reprodutibilidade por convenção"?
10. De onde veio o conceito de workspace, e por que copiá-lo foi a decisão certa?

---

**Fontes:** workspace montado e verificado localmente em 31/08/2026 (uv 0.12.7) ·
[docs.astral.sh/uv/concepts/projects/workspaces](https://docs.astral.sh/uv/concepts/projects/workspaces/) ·
[astral.sh/blog/uv-unified-python-packaging](https://astral.sh/blog/uv-unified-python-packaging).

**Próximo:** [18-publicacao-e-build-backend.md](18-publicacao-e-build-backend.md)
