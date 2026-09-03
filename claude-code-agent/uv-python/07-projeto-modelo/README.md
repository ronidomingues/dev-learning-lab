# `lockspect` — projeto-modelo do curso de uv

> **Nível:** iniciante → intermediário · **Atualizado em:** 31/08/2026
> **Testado com:** uv 0.12.7, CPython 3.10.12 (via `.python-version`), Ubuntu 22.04.5, em 31/08/2026.
> Resultado: **25 testes passando** (15 de leitura, 10 de CLI), cobertura de **96%**.

Uma ferramenta de linha de comando pequena **porém inteira** que lê um arquivo
`uv.lock` e explica o que há dentro dele.

O assunto foi escolhido de propósito: para escrever esta ferramenta você é obrigado a
entender o que o uv grava no lockfile — que é o coração da reprodutibilidade e o
conceito central do curso. A ferramenta se inspeciona a si mesma.

---

## 1. Pré-requisitos

- `uv` ≥ 0.9 instalado ([03-instalacao.md](../03-instalacao.md))
- Nada mais. O uv baixa o Python se preciso.

```bash
uv --version
# esperado: uv 0.12.7 (ou superior)
```

---

## 2. Como rodar — comandos exatos

```bash
cd 07-projeto-modelo
```
```bash
uv sync
```
Cria o `.venv`, resolve o `uv.lock` e instala tudo, inclusive o grupo `dev`
(porque o `pyproject.toml` declara `default-groups = ["dev"]`).

```bash
uv run lockspect --arquivo tests/dados/exemplo.uv.lock
```
Roda o comando `resumo` (o padrão) sobre o lockfile de exemplo.

Saída real desta máquina:

```
               Resumo do uv.lock
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┓
┃ Item                               ┃  Valor ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━┩
│ Versão do formato                  │      1 │
│ Revisão                            │      3 │
│ requires-python                    │ >=3.10 │
│ Pacotes no total                   │      8 │
│ Locais (projeto/workspace)         │      1 │
│ De terceiros                       │      7 │
│ Sem wheel (compilam na instalação) │      1 │
│ Wheels referenciados               │      7 │
└────────────────────────────────────┴────────┘

Atenção: estes pacotes não têm wheel e serão compilados em cada máquina — é onde
a instalação fica lenta e onde falta de compilador quebra o build:
  • legado-sem-wheel 0.9.0

Origens: editable=1, registry=7
```

### Os outros subcomandos

```bash
uv run lockspect -a tests/dados/exemplo.uv.lock arvore
```
Árvore de dependências a partir dos pacotes locais.

```bash
uv run lockspect -a tests/dados/exemplo.uv.lock arvore --profundidade 1
```
Só o primeiro nível.

```bash
uv run lockspect -a tests/dados/exemplo.uv.lock quem urllib3
```
Responde **"por que este pacote está aqui?"** — a pergunta que você mais vai fazer
na vida real.

```bash
uv run lockspect -a tests/dados/exemplo.uv.lock --json | head -20
```
Saída legível por máquina, para pipelines.

### Inspecionar o próprio projeto

```bash
uv run lockspect
```
Sem `--arquivo`, ele lê o `uv.lock` do diretório atual — o deste projeto.

### Configuração por variável de ambiente

```bash
LOCKSPECT_LOCK=tests/dados/exemplo.uv.lock uv run lockspect
```

---

## 3. Rodar os testes

```bash
uv run pytest
```
```bash
uv run pytest --cov=lockspect --cov-report=term-missing
```

Resultado real desta máquina em 31/08/2026 (Python 3.10.12):

```
25 passed in 0.29s
```

Lint e formatação (grupo separado, instalado sob demanda):

```bash
uv run --only-group lint ruff check .
```
```bash
uv run --only-group lint ruff format --check .
```

Empacotar:

```bash
uv build
```
Gera `dist/lockspect-0.1.0.tar.gz` e `dist/lockspect-0.1.0-py3-none-any.whl`.

---

## 4. Estrutura de pastas — comentada

```
07-projeto-modelo/
├── pyproject.toml            # ÚNICO arquivo de configuração: projeto, deps, ruff, pytest
├── uv.lock                   # versões exatas + hashes — versionado no Git
├── .python-version           # versão de Python do projeto — versionado
├── .gitignore                # ignora .venv/, dist/, __pycache__/
├── README.md                 # este arquivo
│
├── src/                      # LAYOUT src/: o pacote não é importável por acidente
│   └── lockspect/
│       ├── __init__.py       # API pública e __version__
│       ├── modelo.py         # dataclasses puras — nenhuma dependência externa
│       ├── leitor.py         # lê e valida o TOML → modelo
│       ├── relatorio.py      # modelo → texto (única parte que conhece o `rich`)
│       └── cli.py            # argparse, códigos de saída, variáveis de ambiente
│
├── scripts/
│   └── comparar_locks.py     # script PEP 723 independente do projeto
│
└── tests/
    ├── conftest.py           # fixture compartilhada
    ├── dados/
    │   └── exemplo.uv.lock   # lockfile sintético, sem rede nos testes
    ├── test_leitor.py        # 15 testes da leitura
    └── test_cli.py           # 10 testes da CLI, incluindo códigos de saída
```

---

## 5. O que cada decisão de projeto ensina

| Decisão | O que ela ensina |
|---|---|
| **Layout `src/`** | o teste importa o pacote **instalado**, não a pasta ao lado. Sem isso, um `__init__.py` faltando passa despercebido até o dia do release. É o motivo de o `uv init` usar `src/` por padrão desde a 0.7 |
| **`tomli>=2.0 ; python_version < '3.11'`** | *marcador de ambiente* (PEP 508): em 3.11+ o `tomli` nem é baixado, porque `tomllib` entrou na biblioteca padrão. É o mecanismo que faz o lock universal funcionar |
| **Grupos `dev` e `lint` separados** | `uv run --only-group lint ruff check .` instala 2 pacotes em vez de 17. No CI, isso é a diferença entre 4 s e 40 s |
| **Extra `grafo` opcional** | mostra a diferença entre *extra* (para quem instala) e *grupo* (para quem desenvolve) |
| **`default-groups = ["dev"]`** | `uv sync` já traz o pytest, sem flag; o `--no-dev` continua disponível para produção |
| **`required-version = ">=0.9"`** | protege contra um colega com uv antigo gerar um lock incompatível |
| **`main()` devolve `int` em vez de chamar `sys.exit`** | a CLI vira testável sem subprocesso — os 10 testes de `test_cli.py` dependem disso |
| **Códigos de saída distintos (0/1/2/3)** | um script que consome a ferramenta consegue distinguir "não achei o arquivo" (2) de "arquivo inválido" (3). Tutoriais quase sempre omitem isso |
| **Erro com dica acionável** (`dica: rode dentro de um projeto uv...`) | mensagem de erro é interface de usuário |
| **Configuração por `LOCKSPECT_LOCK`** | a ordem padrão *flag > variável de ambiente > padrão* é a convenção de toda ferramenta séria |
| **`modelo.py` sem dependências externas** | a lógica é testável sem `rich`, sem terminal e sem I/O. Separar modelo de apresentação é o que torna os testes rápidos e estáveis |
| **`_normalizar()` implementando a PEP 503** | `charset_normalizer` e `charset-normalizer` são o mesmo pacote. Quem não normaliza, erra |
| **Fixture `.uv.lock` sintética** | os testes **não acessam a rede** e não dependem do que o PyPI publicou hoje |
| **Teste do "formato versão 99"** | comportamento à prova de futuro: recusar com mensagem útil é melhor que interpretar errado em silêncio |
| **`scripts/comparar_locks.py` com PEP 723** | um script pode ter dependências próprias, diferentes das do projeto que o hospeda |

---

## 6. Exercícios propostos

1. **Fácil.** Acrescente uma coluna "Origem" à tabela do `resumo` com o host do índice.
2. **Fácil.** Faça `quem` aceitar vários pacotes de uma vez.
3. **Médio.** Implemente `lockspect diff a.lock b.lock` mostrando pacotes adicionados,
   removidos e com versão alterada. (O `scripts/comparar_locks.py` tem um esboço.)
4. **Médio.** Use o extra `grafo` para gerar um `.svg` do grafo de dependências com
   `graphviz`, e faça o comando falhar com mensagem instrutiva se o extra não estiver
   instalado — como no exemplo 4 do [06-exemplos.md](../06-exemplos.md).
5. **Difícil.** Detecte **ciclos** no grafo de dependências (existem, e o uv lida com eles).
6. **Difícil.** Leia também `[package.metadata] requires-dist` e mostre a diferença
   entre o que foi **pedido** (`>=2.31`) e o que foi **travado** (`2.34.2`).
7. **Integração.** Escreva um job de CI que falhe se algum pacote novo entrar no lock
   sem wheel para `linux_x86_64`.

---

## 7. Limitações conscientes

- Lê apenas lockfiles com `version = 1` — o formato atual do uv 0.12.x. Um formato
  futuro é **recusado com mensagem clara**, não interpretado às cegas.
- Não avalia marcadores de ambiente: a árvore mostra todas as dependências, inclusive as
  que não seriam instaladas na sua plataforma. Avaliar marcadores exigiria implementar a
  PEP 508 inteira — é o exercício natural seguinte.
- Não valida hashes. Isso é trabalho do uv, não desta ferramenta.

---

**Volte para:** [00-MAPA.md](../00-MAPA.md) · **Conceitos usados aqui:**
[12-o-modelo-de-projeto.md](../12-o-modelo-de-projeto.md) ·
[13-resolucao-de-dependencias.md](../13-resolucao-de-dependencias.md)
