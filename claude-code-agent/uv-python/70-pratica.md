# 70 · Prática — 14 laboratórios progressivos

> **Nível:** iniciante → avançado · **Atualizado em:** 31/08/2026 · **uv 0.12.7**
> Faça na ordem. Cada laboratório tem **objetivo**, **passos**, **critério de sucesso** e
> **o que você deveria ter entendido**. Não pule o critério de sucesso: é ali que se
> descobre que você achou que entendeu.

Tempo total estimado: **10 a 14 horas**, distribuídas.

---

## Lab 1 — Instalação limpa e verificação · 20 min

**Objetivo:** ter um ambiente funcional e saber provar que está.

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env
uv --version
uvx cowsay -t "lab 1"
uv python install 3.13
uv python list --only-installed
uv cache dir && uv python dir && uv tool dir
```

**Sucesso:** a vaca apareceu, e você sabe dizer os três diretórios de cor.

**Entendeu se souber responder:** por que o instalador não pediu `sudo`? Onde os
binários foram parar?

---

## Lab 2 — Primeiro projeto, do zero · 30 min

**Objetivo:** o ciclo completo declaração → resolução → materialização.

```bash
uv init lab2 && cd lab2
ls -a
cat pyproject.toml
uv add requests
git status                       # o que mudou?
uv run python -c "import requests; print(requests.__version__)"
uv tree
```

**Sucesso:** você consegue apontar, dos arquivos criados, **qual é a declaração, qual é
a resolução e qual é a materialização** — e dizer quais vão para o Git.

**Desafio:** apague o `.venv` inteiro. Recupere sem reinstalar nada à mão.

---

## Lab 3 — Script PEP 723 · 20 min

**Objetivo:** o modo script.

```bash
uv init --script lab3.py --python 3.12
uv add --script lab3.py httpx rich
cat lab3.py
```

Escreva algo que use as duas bibliotecas, e:

```bash
uv run lab3.py
time uv run lab3.py     # segunda vez
```

**Sucesso:** a segunda execução é ordens de grandeza mais rápida. Você sabe explicar por quê.

**Desafio:** faça o arquivo executável direto (`./lab3.py`) e diga por que o `-S` no
shebang é necessário.

---

## Lab 4 — Grupos, extras e a diferença · 40 min

**Objetivo:** parar de confundir os dois. **Este é o lab que mais gente erra.**

```bash
uv init --lib lab4 && cd lab4
uv add pydantic
uv add --group dev pytest
uv add --group docs mkdocs
uv add --optional postgres "psycopg[binary]"
cat pyproject.toml
```

Agora compare o que cada comando instala:

```bash
uv sync --no-dev            && uv pip list | wc -l
uv sync                     && uv pip list | wc -l
uv sync --all-extras        && uv pip list | wc -l
uv sync --only-group docs   && uv pip list | wc -l
```

```bash
uv build && unzip -p dist/*.whl '*/METADATA' | grep -i "^Requires-Dist"
```

**Sucesso:** você explica por que `pytest` e `mkdocs` **não** aparecem no `METADATA` do
wheel, mas `psycopg` aparece (marcado com `extra == "postgres"`).

---

## Lab 5 — Reproduzir o ambiente de outra pessoa · 30 min

**Objetivo:** entender o que o lock realmente garante.

```bash
# simule um colega
git init && git add -A && git commit -m "inicial"
cd .. && git clone lab4 lab4-colega && cd lab4-colega
ls -a                        # não há .venv
uv sync
uv pip list
```

Compare com o original:

```bash
cd ../lab4 && uv pip freeze | sort > /tmp/a.txt
cd ../lab4-colega && uv pip freeze | sort > /tmp/b.txt
diff /tmp/a.txt /tmp/b.txt   # esperado: sem diferença
```

**Sucesso:** `diff` vazio.

**Desafio:** apague o `uv.lock` do clone, rode `uv sync` e compare de novo. Explique
qualquer diferença que aparecer — e por que ela poderia ser bem maior daqui a seis meses.

---

## Lab 6 — Provocar e ler um erro de resolução · 40 min

**Objetivo:** ler mensagens de conflito sem medo.

```bash
uv init lab6 && cd lab6
uv add "requests==2.20.0" "urllib3>=2.0"     # deve falhar
```

Leia a mensagem inteira. Depois:

```bash
uv add "requests>=2.31" "urllib3>=2.0"       # deve funcionar
uv tree --invert --package urllib3
```

Agora provoque outro tipo de conflito:

```bash
uv add "pacote-que-nao-existe-xyz123"
uv add "httpx>=99.0"
```

**Sucesso:** você distingue, pela mensagem, três causas: conflito genuíno entre pacotes,
nome inexistente, e versão inexistente.

---

## Lab 7 — Testar limites inferiores · 30 min

**Objetivo:** descobrir que seus `>=` mentem.

```bash
uv init --lib lab7 && cd lab7
uv add "pandas>=2.0" "requests>=2.25"
uv add --group test pytest
```

Escreva um teste que use um recurso do pandas 2.2. Então:

```bash
uv lock --resolution lowest-direct
uv sync --group test
uv run pytest -q                 # provavelmente falha
uv pip list | grep pandas        # qual versão?
```

Corrija subindo o limite no `pyproject.toml` e repita.

**Sucesso:** você entendeu por que essa checagem precisa estar no CI, e escreveu o
`>=` honesto.

---

## Lab 8 — Múltiplas versões de Python · 30 min

```bash
uv python install 3.10 3.11 3.12 3.13
cd lab7
for v in 3.10 3.11 3.12 3.13; do
  echo "=== $v ==="
  uv run --python "$v" --isolated pytest -q 2>&1 | tail -2
done
```

```bash
uv python pin 3.11 && uv run python --version
uv python pin 3.13 && uv run python --version
cat .python-version
```

**Sucesso:** os quatro rodaram, e você sabe onde os interpretadores foram parar.

**Desafio:** faça o mesmo com `uvx --with tox-uv tox`.

---

## Lab 9 — Workspace · 50 min

```bash
mkdir lab9 && cd lab9
cat > pyproject.toml <<'EOF'
[project]
name = "lab9"
version = "0"
requires-python = ">=3.11"

[tool.uv.workspace]
members = ["pacotes/*"]
EOF
mkdir pacotes && cd pacotes
uv init --lib nucleo
uv init --app servico
cd ..
cd pacotes/servico && uv add nucleo && cd ../..

uv workspace list
uv sync --all-packages
uv run --package servico python -c "import nucleo; print('ok')"
```

Agora edite `pacotes/nucleo/src/nucleo/__init__.py` acrescentando uma função e chame-a
do `servico` **sem** rodar nenhum comando de instalação.

**Sucesso:** funcionou de imediato. Você sabe explicar por quê (instalação editável).

**Desafio:** faça `nucleo` exigir `pydantic<2` e `servico` exigir `pydantic>=2`. Observe
o erro e explique por que é uma propriedade desejada do workspace.

---

## Lab 10 — Ferramentas · 25 min

```bash
uvx ruff check .
uvx --from httpie http GET https://httpbin.org/json
uvx ruff@0.15.0 --version
uv tool install ruff
uv tool list
uv tool dir && ls "$(uv tool dir)"
which ruff
uv tool upgrade --all
```

**Sucesso:** você explica a diferença entre o que está em `~/.local/share/uv/tools` e o
que está em `~/.local/bin`.

---

## Lab 11 — Empacotar e publicar (no TestPyPI) · 60 min

```bash
cd lab7
uv version --bump minor
uv build
tar tzf dist/*.tar.gz | head -20
unzip -l dist/*.whl
uvx twine check dist/*
```

Crie conta no [test.pypi.org](https://test.pypi.org), gere um token, e:

```bash
cat >> pyproject.toml <<'EOF'

[[tool.uv.index]]
name = "testpypi"
url = "https://test.pypi.org/simple/"
publish-url = "https://test.pypi.org/legacy/"
EOF
uv publish --index testpypi --token "pypi-SEU_TOKEN"
uvx --index https://test.pypi.org/simple/ --from lab7 python -c "import lab7"
```

**Sucesso:** você instalou, de um índice remoto, o pacote que acabou de construir.

⚠️ Use um nome único (`lab7-seunome`) — nomes no TestPyPI também são exclusivos.

---

## Lab 12 — Docker · 50 min

**Requer Docker.** Usando o projeto do Lab 7, escreva o Dockerfile do padrão B do
[19-uv-em-docker-e-ci](19-uv-em-docker-e-ci.md).

```bash
docker build -t lab12 .
docker run --rm lab12
```

Agora **meça a otimização de camada**:

```bash
touch src/lab7/__init__.py && time docker build -t lab12 .   # rápido?
# altere o pyproject.toml (acrescente uma dependência)
time docker build -t lab12 .                                  # lento?
```

Depois **remova** o `--no-install-project` da primeira camada e repita as duas medições.

**Sucesso:** você mediu a diferença e sabe explicar de onde ela vem.

---

## Lab 13 — CI completo · 60 min

Suba o Lab 7 para o GitHub e escreva `.github/workflows/ci.yml` com:

- `astral-sh/setup-uv@v6` com versão fixa e cache;
- portão `uv lock --check`;
- matriz de 3 versões de Python × 2 estratégias de resolução;
- job de lint com `--only-group lint`;
- `uv audit`;
- artefato de SBOM.

Depois, **quebre o CI de propósito**: altere o `pyproject.toml` sem commitar o `uv.lock`.

**Sucesso:** o job falha em `uv lock --check` com mensagem clara, e não silenciosamente
mais adiante.

---

## Lab 14 — Migrar um projeto real · 90 min

Pegue um projeto **seu** (ou clone um do GitHub que use Poetry ou `requirements.txt`).

```bash
# registre o estado ANTES
pip list --format=freeze | sort > /tmp/antes.txt   # ou poetry show

uvx migrate-to-uv            # se for Poetry/Pipenv/pip-tools
# ou
uv init --bare && uv add -r requirements.txt

uv lock && uv sync --all-groups
uv pip freeze | sort > /tmp/depois.txt
diff /tmp/antes.txt /tmp/depois.txt
uv run pytest
```

**Sucesso:** os testes passam e você **explica cada linha do `diff`**. Se houver
diferença que você não sabe justificar, você ainda não terminou.

---

## Projeto final — escolha um

### Opção A · Ferramenta de linha de comando
Um programa útil de verdade, empacotado com `[project.scripts]`, publicado no TestPyPI,
com testes, CI e Dockerfile. Requisito: usa pelo menos um extra e um grupo de dev.

### Opção B · Estenda o projeto-modelo
Implemente os exercícios 3, 4 e 6 do [07-projeto-modelo](07-projeto-modelo/README.md):
`lockspect diff`, o grafo com `graphviz` sob um extra, e a comparação entre pedido
(`requires-dist`) e travado.

### Opção C · Monorepo de serviço
Workspace com três membros (`api`, `worker`, `comum`), um único lock, CI com matriz por
membro, e duas imagens Docker (uma por serviço) que compartilham a camada de dependências.

### Opção D · Auditoria da sua organização
Levante todos os projetos Python do seu time. Para cada um: gerenciador atual, se tem
lockfile, se o CI usa `--locked`, se há pacotes só com sdist, se há índice extra sem
`explicit`. Produza um relatório com prioridades de migração. **É o mais valioso dos
quatro se você trabalha em equipe.**

---

## Autoavaliação final

Marque o que você consegue fazer **sem consultar**:

- [ ] Criar um projeto e adicionar uma dependência.
- [ ] Explicar declaração × resolução × materialização, e quais arquivos vão ao Git.
- [ ] Escrever um script PEP 723 correto de cabeça.
- [ ] Distinguir extra de grupo e escolher certo.
- [ ] Ler um erro de resolução e identificar a causa.
- [ ] Testar limites inferiores com `--resolution lowest-direct`.
- [ ] Montar um workspace e explicar sua limitação fundamental.
- [ ] Escrever um Dockerfile com as camadas separadas corretamente.
- [ ] Configurar um índice privado sem abrir a porta da confusão de dependência.
- [ ] Publicar um pacote com Trusted Publishing.
- [ ] Migrar um projeto de Poetry e justificar cada diferença no `diff`.
- [ ] Explicar por que `uv sync --locked` deve estar no CI.

Menos de 8 marcados? Volte aos labs correspondentes. Este material não é para ler.

---

**Próximo:** [75-armadilhas.md](75-armadilhas.md)
