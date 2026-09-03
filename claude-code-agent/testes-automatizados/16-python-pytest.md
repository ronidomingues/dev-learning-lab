# 16 · Python a fundo — pytest por dentro

`Nível: intermediário → avançado` · `Base: pytest 9.1.1, Python 3.10–3.14` · `13/08/2026`

Este arquivo responde à pergunta *"como fazer testes em Python?"* com a profundidade de quem
vai manter uma suíte por anos. Para o primeiro teste, veja
[04-como-comecar.md](04-como-comecar.md); para a referência de comandos,
[05-manual-de-uso.md](05-manual-de-uso.md).

---

## 1. O ecossistema: o que existe e o que usar

| Ferramenta | O que é | Recomendação em 2026 |
|---|---|---|
| **`unittest`** | biblioteca padrão, porte do JUnit | só em código legado; não comece por ela |
| **`pytest`** | o padrão de fato | **use** |
| **`doctest`** | testes dentro do *docstring* | ótimo complemento para documentação executável |
| **`hypothesis`** | testes de propriedades | quando houver invariantes |
| **`coverage.py`** / `pytest-cov` | cobertura | sempre, com `--cov-branch` |
| **`tox`** / `nox` | rodar a suíte em várias versões | biblioteca publicada |
| **`mutmut`**, `cosmic-ray` | análise de mutação | ocasionalmente, no núcleo crítico |
| `nose`, `nose2` | mortos | não use |

---

## 2. Como o pytest descobre os testes

Passo a passo do que acontece quando você digita `pytest`:

```
1. determina o ROOTDIR   → procurando pyproject.toml / pytest.ini / setup.cfg / .git
2. lê a CONFIGURAÇÃO      → seção [tool.pytest.ini_options] etc.
3. carrega os CONFTEST    → conftest.py de cada nível, da raiz para baixo
4. COLETA                 → arquivos test_*.py ou *_test.py
                            classes Test* (sem __init__)
                            funções/métodos test_*
5. reescreve as ASSERÇÕES → manipula o bytecode dos módulos de teste
6. resolve as FIXTURES    → monta o grafo de dependências por nome de parâmetro
7. EXECUTA                → setup → teste → teardown, na ordem do arquivo
8. RELATA                 → placar, tracebacks, resumo
```

**Onde as pessoas se perdem:** o passo 1. Se o `rootdir` for detectado no lugar errado, os
imports quebram de forma misteriosa. `pytest` imprime o `rootdir` na primeira linha da saída —
**leia essa linha** quando algo estranho acontecer.

---

## 3. Reescrita de asserção: a mágica explicada

Este é o mecanismo que fez o pytest vencer, e vale entendê-lo.

Quando o pytest importa um módulo de teste, ele **não** o executa diretamente. Ele:

1. lê o código-fonte;
2. monta a árvore sintática (AST);
3. reescreve cada `assert expr` numa sequência que **guarda os valores intermediários**;
4. compila o resultado e armazena em `__pycache__` com uma marca própria.

Na prática, `assert calcular_gorjeta(100, -10) >= 0` vira, conceitualmente:

```python
_tmp1 = calcular_gorjeta(100, -10)
_tmp2 = _tmp1 >= 0
if not _tmp2:
    raise AssertionError(_explicar(f"assert {_tmp1} >= 0",
                                   f"where {_tmp1} = calcular_gorjeta(100, -10)"))
```

Daí a saída que você viu no [04](04-como-comecar.md):

```
>       assert calcular_gorjeta(100, -10) >= 0
E       assert -10.0 >= 0
E        +  where -10.0 = calcular_gorjeta(100, -10)
```

**Três consequências práticas:**

1. **A reescrita só acontece em arquivos de teste e em `conftest.py`.** Um `assert` dentro de
   uma função auxiliar em `utils.py` não ganha a explicação. Se você tem uma biblioteca de
   asserções própria, registre-a:

   ```python
   # conftest.py
   pytest.register_assert_rewrite("minha_lib.asserts")
   ```

2. **Rodar Python com `-O` (otimizado) remove todos os `assert`** — e a suíte inteira passa
   a "passar". Nunca rode testes com `python -O`.

3. **Mensagens customizadas continuam funcionando**: `assert x == y, "explicação"` mostra as
   duas coisas.

---

## 4. Fixtures a fundo

### 4.1 O modelo mental: injeção de dependência

Uma fixture não é um `setUp`. É um **provedor**, resolvido por nome:

```python
@pytest.fixture
def banco():
    con = sqlite3.connect(":memory:")
    yield con
    con.close()

@pytest.fixture
def repositorio(banco):        # ← fixture que pede outra fixture
    return Repositorio(banco)

def test_x(repositorio):       # ← o teste pede só o que usa
    ...
```

O pytest monta o **grafo** e resolve na ordem certa. Um teste que não pede `banco` não paga
por ele. É a diferença fundamental para o `beforeEach`.

### 4.2 Escopos e o custo de cada um

```python
@pytest.fixture(scope="session")   # function | class | module | package | session
def servidor():
    processo = subprocess.Popen([...])
    yield "http://localhost:8000"
    processo.terminate()
```

| Escopo | Criada uma vez por | Use para |
|---|---|---|
| `function` (padrão) | teste | tudo, por padrão |
| `class` | classe | raro |
| `module` | arquivo | conexão cara, se imutável |
| `package` | pacote | raro |
| `session` | execução | container, servidor, modelo carregado |

**A armadilha do escopo largo:** um objeto mutável de escopo `session` compartilhado faz o
teste A contaminar o teste B. Padrão seguro: **recurso caro com escopo largo + limpeza com
escopo de função**.

```python
@pytest.fixture(scope="session")
def conexao():                          # caro: cria uma vez
    return criar_conexao_postgres()

@pytest.fixture
def banco(conexao):                     # barato: transação por teste
    conexao.execute("BEGIN")
    yield conexao
    conexao.execute("ROLLBACK")         # desfaz TUDO o que o teste fez
```

Esse padrão — **transação com rollback por teste** — é o jeito mais rápido de ter isolamento
real em banco de dados. Custa milissegundos e é a técnica mais valiosa deste arquivo para
quem testa contra banco.

### 4.3 `yield` × `addfinalizer` × `request`

```python
@pytest.fixture
def recurso():
    r = abrir()
    yield r
    fechar(r)          # roda mesmo se o teste falhar

# equivalente, estilo antigo:
@pytest.fixture
def recurso(request):
    r = abrir()
    request.addfinalizer(lambda: fechar(r))
    return r
```

Use `yield`. `addfinalizer` só é necessário quando há vários finalizadores registrados
condicionalmente.

**Cuidado:** se a fixture **levantar exceção antes do `yield`**, o teardown não roda — e o
pytest reporta `E` (erro), não `F` (falha). Se você precisa de limpeza garantida mesmo com
setup parcial, use `try/finally` dentro da fixture.

### 4.4 Fixtures parametrizadas

```python
@pytest.fixture(params=["memoria", "sqlite"], ids=["fake", "real"])
def repositorio(request):
    if request.param == "memoria":
        yield RepositorioMemoria()
    else:
        r = RepositorioSQLite(":memory:")
        yield r
        r.fechar()
```

**Todo** teste que pedir `repositorio` roda duas vezes. É o mecanismo do **teste de
contrato** — e não tem equivalente direto em `node:test` ou Vitest.

### 4.5 `autouse`: poderoso e perigoso

```python
@pytest.fixture(autouse=True)
def limpar_registro():
    REGISTRO.clear()
    yield
```

Aplica-se a todos os testes do escopo, sem ser pedida. Legítimo para: limpar estado global,
configurar *logging*, garantir que nenhum teste faça rede de verdade.

```python
@pytest.fixture(autouse=True)
def proibir_rede(monkeypatch):
    """Qualquer teste que tentar abrir socket falha, com mensagem clara."""
    def bloquear(*args, **kwargs):
        raise RuntimeError("teste tentou acessar a rede — use um dublê")
    monkeypatch.setattr("socket.socket.connect", bloquear)
```

Essa fixture é um dos truques mais úteis que existem: ela **impede** que testes unitários
virem testes de integração por acidente.

**O perigo:** fixture `autouse` num `conftest.py` que ninguém lê é a causa nº 1 de "por que
esse teste está falhando?". Regra: `autouse` só para coisas que **todo** teste precisa, e
com nome autoexplicativo.

### 4.6 Descobrir o que está acontecendo

```bash
pytest --fixtures              # todas as fixtures visíveis, com docstring
pytest --fixtures-per-test     # quais fixtures cada teste usa
pytest --setup-show            # árvore de setup/teardown durante a execução
```

`--setup-show` é a ferramenta de diagnóstico mais subutilizada do pytest.

---

## 5. `conftest.py`: como funciona de verdade

- É descoberto **automaticamente**, sem import.
- Vale para o diretório dele e **todos os subdiretórios**.
- Vários níveis se acumulam: o mais próximo pode sobrescrever o mais distante.
- É o único lugar onde ganchos (*hooks*) do pytest podem ser definidos localmente.

```
projeto/
├── conftest.py              ← vale para tudo
└── tests/
    ├── conftest.py          ← vale para tests/ e abaixo
    ├── unitarios/
    │   └── conftest.py      ← só aqui
    └── integracao/
        └── conftest.py
```

**Regra deste curso:** uma fixture só sobe para o `conftest.py` quando é usada por **dois ou
mais arquivos**. Fixture usada por um arquivo mora naquele arquivo.

Ganchos úteis:

```python
# conftest.py

def pytest_collection_modifyitems(config, items):
    """Marca automaticamente como lento tudo que estiver em tests/integracao/."""
    for item in items:
        if "integracao" in str(item.fspath):
            item.add_marker(pytest.mark.integracao)


def pytest_addoption(parser):
    """Cria uma opção de linha de comando própria."""
    parser.addoption("--rodar-lentos", action="store_true", default=False)


def pytest_runtest_setup(item):
    if "lento" in item.keywords and not item.config.getoption("--rodar-lentos"):
        pytest.skip("precisa de --rodar-lentos")
```

---

## 6. Parametrização avançada

```python
# produto cartesiano: 3 × 2 = 6 testes
@pytest.mark.parametrize("conta", [100, 200, 300])
@pytest.mark.parametrize("percentual", [10, 15])
def test_combinacoes(conta, percentual): ...


# marcar um caso individual
@pytest.mark.parametrize(
    "x",
    [1, 2, pytest.param(3, marks=pytest.mark.xfail(reason="bug #123"))],
)
def test_com_caso_conhecido_quebrado(x): ...


# gerar casos programaticamente, com ids legíveis
CASOS = [(cpf, True) for cpf in CPFS_VALIDOS] + [(cpf, False) for cpf in CPFS_INVALIDOS]

@pytest.mark.parametrize(
    ("cpf", "valido"), CASOS, ids=[f"{c}-{'ok' if v else 'ruim'}" for c, v in CASOS]
)
def test_cpf(cpf, valido): ...


# geração dinâmica com o gancho, quando parametrize não basta
def pytest_generate_tests(metafunc):
    if "arquivo_de_exemplo" in metafunc.fixturenames:
        arquivos = sorted(Path("exemplos").glob("*.json"))
        metafunc.parametrize("arquivo_de_exemplo", arquivos, ids=lambda p: p.stem)
```

O último padrão é o de **testes dirigidos por dados de arquivo**: você põe casos em JSON/YAML
e cada arquivo vira um teste. Excelente para regras de negócio com muitos casos vindos da
área de negócio.

---

## 7. `unittest.mock` a fundo

### 7.1 A hierarquia

| Classe | Diferença |
|---|---|
| `Mock` | responde a qualquer atributo |
| `MagicMock` | idem + protocolos mágicos (`__len__`, `__iter__`, `__enter__`…) |
| `AsyncMock` | métodos são corrotinas |
| `create_autospec(X)` | copia a assinatura de `X` — **prefira esta** |
| `NonCallableMock` | quando o objeto não é chamável |

### 7.2 `patch` — as três formas

```python
# 1. gerenciador de contexto (o mais claro)
with patch("modulo.funcao") as fake:
    fake.return_value = 42
    ...

# 2. decorador — ATENÇÃO à ordem: de baixo para cima
@patch("modulo.b")      # ← este vem SEGUNDO no parâmetro
@patch("modulo.a")      # ← este vem PRIMEIRO
def test_x(fake_a, fake_b): ...

# 3. início/fim manual (para usar em fixture)
@pytest.fixture
def fake_relogio():
    p = patch("modulo.datetime")
    m = p.start()
    yield m
    p.stop()
```

Variantes: `patch.object(Classe, "metodo")`, `patch.dict(os.environ, {...})`,
`patch.multiple(...)`.

### 7.3 Efeitos colaterais

```python
m.metodo.return_value = 42                      # sempre 42
m.metodo.side_effect = [1, 2, 3]                # 1, depois 2, depois 3, depois StopIteration
m.metodo.side_effect = ValueError("boom")       # explode
m.metodo.side_effect = lambda x: x * 2          # calcula
```

### 7.4 Verificações

```python
m.assert_called()
m.assert_called_once()
m.assert_called_with(1, b=2)
m.assert_called_once_with(1, b=2)
m.assert_any_call(1)
m.assert_has_calls([call(1), call(2)], any_order=False)
m.assert_not_called()

m.call_count
m.call_args            # a última chamada
m.call_args.args       # posicionais
m.call_args.kwargs     # nomeados
m.call_args_list       # todas
m.mock_calls           # todas, incluindo chamadas a filhos e métodos mágicos
```

> **Armadilha silenciosa — e o que já foi corrigido.** O Python moderno protege contra os
> erros de digitação mais comuns: qualquer atributo começando por `assert` ou `assret` que
> não seja uma asserção válida levanta `AttributeError`. Verificado em Python 3.10.12:
>
> ```python
> m.assert_called_once_wiht(1)
> # AttributeError: 'assert_called_once_wiht' is not a valid assertion.
> ```
>
> **O buraco que resta** é o nome que não começa com `assert`:
>
> ```python
> m.called_once_with(1)     # não levanta nada. Cria um Mock e devolve outro. PASSA.
> m.verify_called()         # idem
> ```
>
> `m.called_once_with(...)` é um erro real e frequente, porque `m.called` **existe** e as
> pessoas completam de memória. Proteção: `create_autospec`/`spec=` (que restringe os
> atributos ao objeto real) e regras de lint que sinalizam chamadas a métodos inexistentes
> em mocks.

---

## 8. `monkeypatch`: o dublê nativo do pytest

Mais simples que `unittest.mock` para os casos comuns, e desfaz sozinho.

```python
def test_x(monkeypatch):
    monkeypatch.setattr("modulo.CONSTANTE", 42)
    monkeypatch.setattr(objeto, "metodo", lambda: "falso")
    monkeypatch.delattr("modulo.funcao_perigosa")
    monkeypatch.setitem(config, "chave", "valor")
    monkeypatch.delitem(config, "outra", raising=False)
    monkeypatch.setenv("API_KEY", "falsa")
    monkeypatch.delenv("PROXY", raising=False)
    monkeypatch.syspath_prepend("/caminho/extra")
    monkeypatch.chdir(tmp_path)
```

**Quando usar `monkeypatch` e quando usar `mock`:**

| Situação | Ferramenta |
|---|---|
| trocar um valor ou função por outro | `monkeypatch` |
| variável de ambiente, `dict`, diretório | `monkeypatch` |
| precisa **verificar** como foi chamado | `mock` |
| precisa de assinatura verificada | `create_autospec` |

---

## 9. Testes assíncronos

O pytest não roda corrotinas nativamente. Duas opções:

```bash
pip install pytest-asyncio      # o mais usado
pip install anyio               # se você usa trio, ou quer os dois back-ends
```

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"     # dispensa o marcador em cada teste
```

```python
async def test_busca():
    assert await buscar(1) == {"id": 1}


@pytest.fixture
async def cliente():
    async with httpx.AsyncClient() as c:
        yield c
```

**Armadilha nº 1:** esquecer `asyncio_mode = "auto"` ou o marcador `@pytest.mark.asyncio`. O
teste é coletado, a corrotina nunca é aguardada, e o pytest **avisa** mas o teste conta como
"passou" em versões antigas. Com `filterwarnings = ["error"]` isso vira erro — mais um
motivo para ligá-lo.

---

## 10. Configuração recomendada, comentada

```toml
[tool.pytest.ini_options]
minversion = "8.0"
testpaths = ["tests"]

addopts = [
  # modo de import recomendado desde o pytest 8: evita a bagunça de sys.path
  # do modo "prepend" e dispensa __init__.py na pasta de testes
  "--import-mode=importlib",
  # marcador não declarado vira ERRO, não aviso.
  # Sem isso, um typo em @pytest.mark.integraçao faz o teste sumir do filtro
  # em silêncio — e você acha que tem cobertura que não tem.
  "--strict-markers",
  # chave de configuração desconhecida também vira erro
  "--strict-config",
  # resumo no fim com o motivo de cada teste pulado/falho
  "-ra",
]

markers = [
  "integracao: toca I/O real. Excluir com -m 'not integracao'",
  "lento: leva mais de 1 segundo",
  "propriedade: teste baseado em propriedades (Hypothesis)",
]

# DeprecationWarning da sua própria stack é um bug com data marcada.
filterwarnings = ["error"]

[tool.coverage.run]
branch = true                # cobertura de RAMO, não só de linha
source = ["meupacote"]

[tool.coverage.report]
show_missing = true
exclude_lines = [
  "pragma: no cover",
  "if TYPE_CHECKING:",
  "raise NotImplementedError",
  "\\.\\.\\.$",              # corpo de Protocol
]
fail_under = 80
```

**Sobre `filterwarnings = ["error"]`:** é a configuração mais controversa da lista e a que
mais paga. Ela transforma todo aviso em falha. No começo dói (uma dependência antiga enche a
tela), mas cada exceção que você adiciona é uma dívida **explícita e datada**:

```toml
filterwarnings = [
  "error",
  # remover quando a lib X publicar a 3.0 (prevista para out/2026) — issue #412
  "ignore:datetime.utcnow.*:DeprecationWarning:libx",
]
```

Sem isso, você descobre que estava usando API removida no dia em que atualiza a versão maior.

---

## 11. Organização de arquivos

```
projeto/
├── pyproject.toml
├── src/
│   └── meupacote/
│       ├── __init__.py
│       └── dominio.py
└── tests/
    ├── conftest.py
    ├── unitarios/
    │   └── test_dominio.py
    └── integracao/
        ├── conftest.py
        └── test_banco.py
```

**`src/` layout ou plano?** Recomendação: **`src/`**. Motivo concreto: com o pacote em
`src/`, é **impossível** importá-lo por acidente a partir do diretório de trabalho — você é
obrigado a instalá-lo (`pip install -e .`), e portanto seus testes exercitam o pacote
*instalado*, do mesmo jeito que o usuário vai usá-lo. Com layout plano, um `import meupacote`
pega a pasta local, e erros de empacotamento (arquivo de dados esquecido no `MANIFEST`) só
aparecem para o usuário final.

**`__init__.py` em `tests/`?** Com `--import-mode=importlib`, **não é necessário** — e é
melhor não ter. Sem ele, você pode ter `tests/unitarios/test_x.py` e
`tests/integracao/test_x.py` com o mesmo nome sem conflito.

---

## 12. `doctest`: a documentação que é testada

Subutilizado e excelente para bibliotecas.

```python
def aplicar_desconto(centavos: int, percentual: int) -> int:
    """Desconta um percentual, arredondando meio para cima.

    >>> aplicar_desconto(10000, 10)
    9000
    >>> aplicar_desconto(1999, 10)
    1799
    >>> aplicar_desconto(100, 150)
    Traceback (most recent call last):
        ...
    ValueError: percentual fora de 0..100: 150
    """
```

```bash
pytest --doctest-modules src/
```

**Onde ganha:** o exemplo na documentação **nunca** fica desatualizado, porque quebra o CI.
**Onde perde:** ruim para casos complexos (saída longa, ordem de dicionário, floats). Use
para o exemplo canônico de cada função pública, e testes de verdade para o resto.

---

## 13. Plugins que valem a pena

| Plugin | Para quê |
|---|---|
| `pytest-cov` | cobertura |
| `pytest-xdist` | `-n auto` paraleliza por processos |
| `pytest-randomly` | embaralha a ordem — detecta acoplamento entre testes |
| `pytest-timeout` | mata teste travado (essencial em CI) |
| `pytest-mock` | fixture `mocker`, com limpeza automática |
| `pytest-asyncio` | testes `async` |
| `pytest-benchmark` | medições, quando você precisa de número |
| `pytest-sugar` | saída mais legível |
| `pytest-watcher` | modo *watch* |
| `syrupy` | snapshots |
| `pytest-postgresql`, `testcontainers` | banco descartável |

**Cuidado com o excesso.** Cada plugin é uma dependência que pode quebrar na atualização do
pytest. A lista mínima para um projeto sério: `pytest-cov`, `pytest-xdist`,
`pytest-timeout`, `pytest-randomly`.

---

## 14. `unittest` para quem tem legado

O pytest **roda testes `unittest` sem modificação**. Migração incremental:

```python
# antes
class TestDinheiro(unittest.TestCase):
    def setUp(self):
        self.d = Dinheiro(100)

    def test_soma(self):
        self.assertEqual(self.d + Dinheiro(50), Dinheiro(150))

# depois
class TestDinheiro:
    @pytest.fixture
    def d(self):
        return Dinheiro(100)

    def test_soma(self, d):
        assert d + Dinheiro(50) == Dinheiro(150)
```

Tradução das asserções:

| unittest | pytest |
|---|---|
| `assertEqual(a, b)` | `assert a == b` |
| `assertTrue(x)` | `assert x` |
| `assertIn(a, b)` | `assert a in b` |
| `assertIsNone(x)` | `assert x is None` |
| `assertRaises(E)` | `with pytest.raises(E):` |
| `assertAlmostEqual(a, b)` | `assert a == pytest.approx(b)` |
| `assertCountEqual(a, b)` | `assert sorted(a) == sorted(b)` |
| `setUp` / `tearDown` | fixture com `yield` |

**Estratégia:** não migre tudo de uma vez. Escreva o **novo** em pytest, converta o antigo
quando tocar nele.

---

## 15. Erros específicos de Python que os testes precisam pegar

Armadilhas da linguagem que valem um teste dedicado:

```python
def test_bool_e_int_em_python():
    """isinstance(True, int) é True. Sem validação, Dinheiro(True) vale 1 centavo."""
    with pytest.raises(ValorInvalido):
        Dinheiro(True)


def test_argumento_padrao_mutavel_nao_e_compartilhado():
    """def f(x=[]) cria a lista UMA vez, na definição — e ela é compartilhada."""
    a, b = Carrinho(), Carrinho()
    a.adicionar("x")
    assert b.itens == []


def test_igualdade_de_float_nunca_e_exata():
    assert 0.1 + 0.2 != 0.3
    assert 0.1 + 0.2 == pytest.approx(0.3)


def test_dict_preserva_ordem_de_insercao():
    """Garantido pela linguagem desde o Python 3.7 — mas alguém vai duvidar."""
    assert list({"b": 1, "a": 2}) == ["b", "a"]
```

---

## Autoteste

1. Descreva os oito passos que o pytest executa ao ser invocado.
2. O que é a reescrita de asserção, e em quais arquivos ela acontece?
3. Por que nunca rodar testes com `python -O`?
4. Qual a diferença fundamental entre uma fixture e um `beforeEach`?
5. Descreva o padrão "conexão de sessão + transação com rollback por teste" e por que ele é rápido.
6. Escreva uma fixture `autouse` que impeça testes unitários de acessar a rede.
7. Qual a regra deste curso para promover uma fixture ao `conftest.py`?
8. `m.assert_called_once_wiht(1)` levanta erro; `m.called_once_with(1)` não. Explique a diferença e como se proteger.
9. Quando usar `monkeypatch` e quando usar `unittest.mock`?
10. Justifique o layout `src/` com um argumento concreto sobre empacotamento.
11. O que `filterwarnings = ["error"]` compra, e qual é o custo?
12. Onde `doctest` ganha e onde perde?
