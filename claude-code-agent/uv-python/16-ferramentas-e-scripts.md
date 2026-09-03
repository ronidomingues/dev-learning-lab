# 16 · Ferramentas e scripts — `uvx`, `uv tool` e a PEP 723

> **Nível:** intermediário · **Atualizado em:** 31/08/2026 · **uv 0.12.7**

Dois modos de uso que não envolvem projeto nenhum — e que, na minha experiência, são os
que mais mudam o dia a dia de quem já usa Python há anos.

---

## Parte I — Ferramentas

## 1. O problema que `uv tool` resolve

Você quer usar `ruff`, `black`, `httpie`, `mkdocs`, `awscli`, `pre-commit`. Eles são
**programas**, não bibliotecas do seu projeto. Onde instalá-los?

| Caminho | O que dá errado |
|---|---|
| `pip install --user ruff` | vai para o Python do sistema; conflita com outras ferramentas; PEP 668 bloqueia |
| dentro do `.venv` do projeto | polui o `pyproject.toml` com algo que não é dependência do software; some quando você troca de projeto |
| um `.venv` manual por ferramenta | funciona, mas você gerencia 12 ambientes na mão |
| `pipx` | a solução correta desde 2019 — e é exatamente o que `uv tool` faz, mais rápido |

**A resposta certa:** cada ferramenta em seu próprio ambiente isolado, com apenas o
executável exposto no `PATH`.

---

## 2. `uvx` — rodar sem instalar

```bash
uvx ruff check .
```
Cria (ou reaproveita do cache) um ambiente efêmero, instala o `ruff`, executa, e o
ambiente permanece no cache para a próxima vez. Nada é adicionado ao seu `PATH`.

`uvx` é exatamente um atalho para `uv tool run`.

| Situação | Comando |
|---|---|
| pacote e comando têm o mesmo nome | `uvx ruff check .` |
| nomes diferentes | `uvx --from httpie http GET example.com` |
| versão específica | `uvx ruff@0.15.0 check .` |
| a mais recente, ignorando o cache | `uvx ruff@latest check .` |
| com dependência extra | `uvx --with pandas jupyter lab` |
| sob outra versão de Python | `uvx --python 3.12 mypy .` |
| de um repositório Git | `uvx --from git+https://github.com/org/ferramenta ferramenta` |

> **O caso `--from` é a pegadinha mais comum.** `uvx httpie` falha porque o pacote
> `httpie` fornece o comando `http`, não `httpie`. Quando `uvx X` reclamar que não achou
> o executável, é isso.

**Onde `uvx` brilha de verdade:** experimentar. "Será que essa ferramenta serve?" —
antes, isso custava criar um venv, instalar, testar, apagar. Agora custa uma linha, e
não deixa rastro.

---

## 3. `uv tool install` — instalar de vez

```bash
uv tool install ruff
```
```
Downloading ruff (9.8MiB)
 Downloaded ruff
Prepared 1 package in 899ms
Installed 1 package in 47ms
 + ruff==0.16.5
Installed 1 executable: ruff
```
(Saída real desta máquina, 31/08/2026.)

```bash
uv tool list
```
```
ruff v0.16.5
- ruff
```

Comandos completos:

```bash
uv tool install "mkdocs-material" --with mkdocs-mermaid2-plugin   # com plugins
uv tool install ruff --python 3.12                                 # sob um Python específico
uv tool install "ruff==0.15.0"                                     # versão travada
uv tool upgrade ruff
uv tool upgrade --all
uv tool uninstall ruff
uv tool uninstall --all
uv tool dir                     # ~/.local/share/uv/tools
uv tool update-shell            # garante o PATH
uv tool audit                   # vulnerabilidades nas ferramentas instaladas
```

**Estrutura em disco:**

```
~/.local/share/uv/tools/
├── ruff/
│   ├── bin/ruff            ← o executável real
│   ├── lib/python3.13/site-packages/
│   └── uv-receipt.toml     ← o que foi pedido, para o upgrade saber o que fazer
└── mkdocs-material/
    └── ...

~/.local/bin/ruff           ← link/atalho para o executável acima; ESTE é o que fica no PATH
```

---

## 4. `uvx` × `uv tool install` — quando usar cada um

| | `uvx` | `uv tool install` |
|---|---|---|
| Frequência de uso | eventual | diária |
| Fica no `PATH` | não | sim |
| Versão | escolhida a cada chamada | fixa até você atualizar |
| Uso típico | experimentar, executar em CI, rodar uma vez | `ruff`, `pre-commit`, `awscli` |
| Custo da 1ª vez | download | download |
| Custo das próximas | quase zero (cache) | zero |

**Minha regra:** se eu digitei a mesma `uvx` três vezes na semana, ela vira
`uv tool install`.

### `uv tool` como substituto do `pipx`

Migração completa:

```bash
pipx list                       # anote o que você tem
pipx uninstall-all
uv tool install ruff
uv tool install pre-commit
uv tool install httpie
```
Compatível em espírito e mais rápido. O `uv tool` não tem o `pipx inject` com o mesmo
nome — o equivalente é `--with` na instalação.

---

## Parte II — Scripts

## 5. A PEP 723: metadados dentro do arquivo

Aceita em 2024, a PEP 723 define um bloco de comentário que descreve as dependências do
próprio script:

```python
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "httpx>=0.28",
#     "rich>=13.0",
# ]
# ///
```

**Regras do formato**, para você não errar:

- começa com uma linha exatamente `# /// script`;
- toda linha do bloco começa com `# ` (cerquilha e um espaço) — ou é só `#` se vazia;
- termina com `# ///`;
- o conteúdo, sem os `# `, é **TOML**;
- deve aparecer antes de qualquer código (por convenção, logo após o shebang).

O uv lê o bloco e monta o ambiente. **Sem projeto, sem `.venv` visível, sem
`requirements.txt`.**

---

## 6. Usando na prática

```bash
uv run script.py                     # roda, montando o ambiente do cabeçalho
uv init --script novo.py --python 3.12   # cria o esqueleto com o bloco
uv add --script novo.py httpx pandas     # acrescenta dependências ao bloco
uv remove --script novo.py pandas
uv lock --script novo.py             # gera novo.py.lock — lock para um script!
uv sync --script novo.py             # materializa o ambiente sem executar
uv run --with rich script_sem_bloco.py   # dependência avulsa, sem editar o arquivo
```

Saída real da primeira execução de um script que pedia `httpx` e Python ≥ 3.11, nesta
máquina:

```
Downloading cpython-3.14.7-linux-x86_64-gnu (download) (34.3MiB)
 Downloaded cpython-3.14.7-linux-x86_64-gnu (download)
Installed 6 packages in 32ms
200
```

Repare: **baixou o interpretador** e montou o ambiente sozinho. Na segunda execução, tudo
vem do cache.

### Script executável direto

```python
#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["rich"]
# ///
```
```bash
chmod +x script.py && ./script.py
```

O `-S` do `env` permite mais de um argumento no shebang. Funciona no coreutils do GNU
(Linux) e no BSD moderno (macOS ≥ 12). **Não** funcione em Unix antigo — nesse caso,
chame `uv run --script arquivo.py`.

---

## 7. Para que isso serve de verdade

Cinco usos em que a PEP 723 + uv é estritamente melhor que a alternativa:

| Caso | Antes | Agora |
|---|---|---|
| **Compartilhar um utilitário com um colega** | mandar `.py` + `requirements.txt` + instruções | mandar **um arquivo** |
| **Script de manutenção em servidor** | manter um venv por script, que apodrece | o script se descreve; `cron` chama `uv run` |
| **Reproduzir um bug** | "instale a versão X de Y e Z" | um arquivo com as versões exatas |
| **Automação de CI** | passo de instalação separado | `uv run script.py` e pronto |
| **Ensinar / dar exemplo** | metade do tutorial é ambiente | o exemplo funciona copiando e colando |

> **Opinião:** este é o recurso do uv que mais me mudou o hábito, mais até que a
> velocidade. A categoria "script Python com dependências" era desconfortável havia 30
> anos; agora não é. É a coisa mais próxima de um shell script com bibliotecas que o
> Python já teve.

---

## 8. Lock de script

```bash
uv lock --script relatorio.py
ls relatorio.py.lock
```
Gera um lockfile ao lado do script, com versões e hashes. Nas execuções seguintes, o uv
usa esse lock em vez de re-resolver.

Use quando o script for parte de infraestrutura de verdade (deploy, migração,
processamento agendado): você quer que ele rode igual daqui a seis meses, e não com as
versões que o PyPI tiver naquele dia.

---

## 9. Limites e armadilhas

| Limite | Detalhe |
|---|---|
| **Um arquivo só** | se o script cresce e precisa de módulos próprios, virou projeto: `uv init` |
| **Sem `[project.scripts]`** | não há entry point; a chamada é sempre `uv run arquivo.py` |
| **Ambiente efêmero** | fica em `~/.cache/uv/environments-v2`; `uv cache clean` o remove e a próxima execução reinstala |
| **`uv add --script` reescreve o arquivo** | ele edita o seu `.py`. Tenha-o versionado antes |
| **Não roda sem uv** | quem receber o arquivo precisa ter uv. Sem uv, o bloco é só um comentário — o script funciona se as dependências já estiverem instaladas |
| **`env -S` não é universal** | em Unix antigo, o shebang de múltiplos argumentos falha |
| **Cron não tem seu PATH** | use caminho absoluto do `uv` no `crontab`. Erro nº 1 |

---

## 10. Os cinco porquês: por que "script com dependências" era difícil?

**1. Por que eu não podia simplesmente rodar um `.py` que usa `requests`?**
Porque o `requests` precisa estar instalado em algum lugar que o `sys.path` alcance.

**2. Por que não instalar globalmente e pronto?**
Porque scripts diferentes querem versões diferentes, e globais colidem — o mesmo problema
de sempre, agora com scripts.

**3. Por que não existia um jeito de declarar dependências dentro do arquivo?**
**Decisão histórica:** o modelo de empacotamento do Python sempre foi **por diretório de
projeto** (`setup.py`, depois `pyproject.toml`), herdado do `distutils` de 2000, que
pensava em *distribuições*, não em arquivos avulsos. Ninguém tinha padronizado o caso do
arquivo único.

**4. Por que demorou até 2023 para alguém propor a PEP 723?**
Houve tentativas antes — `pipx run` já suportava um formato informal desde 2021, e a
PEP 722 (uma proposta concorrente, com sintaxe própria em vez de TOML) foi debatida e
rejeitada em favor da 723. **Parada legítima: foi uma escolha deliberada de reusar TOML
para não inventar um formato novo**, registrada na decisão do Steering Council.

**5. Por que só ficou realmente útil com o uv?**
Porque a PEP define **o formato**, não a ferramenta. Sem um executor que resolva rápido,
faça cache e ainda baixe o interpretador certo, ler o bloco não resolve nada. `pipx run`
implementa parcialmente; o uv fecha o ciclo — e faz isso em milissegundos, o que muda a
ergonomia de "aceitável" para "melhor que a alternativa".

---

## Autoteste

1. Onde ficam os pacotes de uma ferramenta instalada com `uv tool install`?
2. Por que `uvx httpie` falha, e qual é a correção?
3. Escreva o comando para rodar o `jupyter lab` com `pandas` disponível, sem instalar nada.
4. Qual é a regra que você usa para decidir entre `uvx` e `uv tool install`?
5. Escreva um bloco PEP 723 completo e correto para Python ≥ 3.12 com `polars`.
6. Cite as cinco regras de formato do bloco PEP 723.
7. Quando gerar um `.py.lock` para um script? Qual comando?
8. Qual é o erro nº 1 ao colocar um script uv no `cron`?
9. O que acontece se alguém sem uv receber seu script PEP 723?
10. Por que a PEP 722 foi preterida em favor da 723?

---

**Fontes:** [PEP 723](https://peps.python.org/pep-0723/) ·
[PEP 722 (rejeitada)](https://peps.python.org/pep-0722/) ·
[docs.astral.sh/uv/guides/scripts](https://docs.astral.sh/uv/guides/scripts/) ·
[docs.astral.sh/uv/guides/tools](https://docs.astral.sh/uv/guides/tools/) ·
comandos e saídas executados localmente em 31/08/2026 (uv 0.12.7).

**Próximo:** [17-workspaces-e-monorepo.md](17-workspaces-e-monorepo.md)
