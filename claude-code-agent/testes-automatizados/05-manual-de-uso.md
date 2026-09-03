# 05 · Manual de uso — referência consultável

`Nível: iniciante → intermediário` · `Base: pytest 9.1.1 · Node 24.18 · Vitest 4.1 · Jest 30` · `12/08/2026`

Organizado **por tarefa**, não por ordem alfabética. Use o índice; não leia de ponta a ponta.

---

## Índice

1. [Rodar testes: selecionar o que roda](#1-rodar-testes-selecionar-o-que-roda)
2. [Ler a saída e controlar o barulho](#2-ler-a-saída-e-controlar-o-barulho)
3. [Asserções](#3-asserções)
4. [Preparar cenário: fixtures, hooks, setup](#4-preparar-cenário)
5. [Rodar o mesmo teste com vários dados](#5-vários-dados-parametrização)
6. [Pular, marcar, esperar falha](#6-pular-marcar-esperar-falha)
7. [Dublês: mocks, stubs, spies](#7-dublês)
8. [Tempo, aleatoriedade e variáveis de ambiente](#8-tempo-aleatoriedade-e-ambiente)
9. [Testes assíncronos](#9-testes-assíncronos)
10. [Cobertura](#10-cobertura)
11. [Velocidade: paralelismo e ordenação](#11-velocidade)
12. [Configuração](#12-configuração)
13. [Depurar um teste](#13-depurar-um-teste)
14. [O que está obsoleto](#14-o-que-está-obsoleto)
15. [Atalhos que só quem usa há anos conhece](#15-atalhos-que-só-quem-usa-há-anos-conhece)

---

## 1. Rodar testes: selecionar o que roda

### pytest

| Comando | O que faz |
|---|---|
| `pytest` | tudo, a partir do diretório atual |
| `pytest tests/` | só uma pasta |
| `pytest tests/test_a.py` | um arquivo |
| `pytest tests/test_a.py::TestX` | uma classe |
| `pytest tests/test_a.py::TestX::test_y` | um teste |
| `pytest -k "cupom and not expirado"` | por expressão sobre o **nome** |
| `pytest -m integracao` | por **marcador** |
| `pytest -m "not integracao"` | tudo, menos o marcador |
| `pytest --lf` | só os que falharam da última vez |
| `pytest --ff` | todos, mas começando pelos que falharam |
| `pytest --nf` | arquivos novos primeiro |
| `pytest -x` | para no primeiro erro |
| `pytest --maxfail=3` | para no terceiro |
| `pytest --collect-only` | lista o que rodaria, sem rodar |
| `pytest --co -q` | idem, saída curta — ótimo para conferir o filtro |

### node:test

| Comando | O que faz |
|---|---|
| `node --test` | tudo (procura `*.test.js`, `*-test.js`, `test.js`, pasta `test/`) |
| `node --test test/a.test.js` | um arquivo |
| `node --test "test/**/*.integracao.test.js"` | por glob |
| `node --test --test-name-pattern="cupom"` | por nome (regex) |
| `node --test --test-skip-pattern="lento"` | exclui por nome |
| `node --test --test-only` | só os marcados `{ only: true }` |
| `node --test --test-force-exit` | encerra mesmo com handle aberto |
| `node --test --watch` | re-roda ao salvar |
| `node --test --test-concurrency=4` | quantos arquivos em paralelo |

### Vitest

| Comando | O que faz |
|---|---|
| `vitest` | modo watch (o padrão!) |
| `vitest run` | roda uma vez e sai — **use este no CI** |
| `vitest run caminho/arquivo` | filtra por caminho |
| `vitest run -t "cupom"` | filtra por nome do teste |
| `vitest --ui` | interface web |
| `vitest run --bail=1` | para no primeiro erro |
| `vitest related src/x.js` | só os testes afetados por aquele arquivo |

> **Pegadinha do Vitest:** `vitest` sem `run` entra em modo watch e **nunca termina**. Num
> pipeline de CI isso trava o job até o timeout. Sempre `vitest run`.

### Jest

`jest`, `jest -t "nome"`, `jest caminho`, `jest --onlyChanged`, `jest --watch`.
Jest **não** entra em watch por padrão — o oposto do Vitest.

---

## 2. Ler a saída e controlar o barulho

### pytest

| Opção | Efeito |
|---|---|
| `-q` | uma linha por arquivo; placar no fim |
| (nada) | um caractere por teste |
| `-v` | um nome de teste por linha |
| `-vv` | idem, e **não trunca** os diffs longos |
| `-ra` | resumo no fim com o motivo de cada pulado/falho ← **use sempre** |
| `--tb=short` | traceback curto |
| `--tb=line` | uma linha por falha |
| `--tb=no` | sem traceback |
| `-s` | não captura `print()` — mostra na hora |
| `--capture=no` | idem |
| `-l` | mostra as variáveis locais no traceback |
| `--durations=10` | os 10 testes mais lentos ← ouro para caçar lentidão |
| `-p no:cacheprovider` | não escreve `.pytest_cache` |

Leitura dos caracteres: `.` passou · `F` falhou · `E` erro fora do teste (na fixture) ·
`s` pulado · `x` xfail (falhou como esperado) · `X` xpass (passou, mas era esperado falhar).

**`E` e `F` não são a mesma coisa.** `F` é asserção falsa: o código rodou e deu resultado
errado. `E` é exceção antes/fora: fixture quebrada, import errado, erro de setup. Erro de
setup costuma indicar problema de ambiente, não de código.

### node:test

Saída padrão é TAP-ish com símbolos. Repórteres alternativos:

```bash
node --test --test-reporter=spec     # legível (é o padrão em TTY)
node --test --test-reporter=tap      # TAP puro, para ferramentas
node --test --test-reporter=dot      # um ponto por teste
node --test --test-reporter=junit    # XML, para CI que lê JUnit
node --test --test-reporter=spec --test-reporter-destination=stdout \
            --test-reporter=junit --test-reporter-destination=resultado.xml
```

A última linha é o padrão útil em CI: humano no console **e** XML no arquivo.

---

## 3. Asserções

### Python: só `assert`

O pytest reescreve o `assert` nativo e mostra os valores intermediários. Não existe
`assertEqual`, `assertTrue` etc. — isso é `unittest`.

```python
assert resultado == 42
assert "erro" in mensagem
assert lista == [1, 2, 3]
assert 0.1 + 0.2 == pytest.approx(0.3)         # float
assert valor == pytest.approx(3.14, abs=0.01)  # tolerância absoluta
assert isinstance(x, Dinheiro)

with pytest.raises(ValueError):                 # explode
    f()

with pytest.raises(ValueError, match="negativo"):   # e a mensagem casa (regex!)
    f()

with pytest.raises(ValueError) as info:         # e eu quero inspecionar
    f()
assert info.value.codigo == 42

with pytest.warns(DeprecationWarning):          # emite aviso
    f()

with pytest.deprecated_call():
    f()
```

> `match=` recebe **regex**, não texto literal. `match="custa R$ 10 (barato)"` não casa,
> porque `(` e `)` são metacaracteres. Use `re.escape()` ou simplifique o padrão.

### JavaScript: `node:assert/strict`

```javascript
import assert from 'node:assert/strict';

assert.equal(a, b);                 // === (com /strict)
assert.notEqual(a, b);
assert.deepStrictEqual(obj, {a: 1}); // estrutura + protótipo
assert.notDeepStrictEqual(a, b);
assert.ok(x);                        // verdadeiro
assert.match('texto', /exto/);
assert.doesNotMatch('texto', /xyz/);
assert.throws(() => f(), TypeError);
assert.throws(() => f(), { name: 'RangeError', message: /negativo/ });
assert.doesNotThrow(() => f());
await assert.rejects(async () => f(), Error);       // promessa rejeitada
await assert.doesNotReject(async () => f());
assert.fail('chegou onde não devia');
```

Comparações que confundem:

| | compara | `{a:1}` vs `{a:1}` | `1` vs `'1'` |
|---|---|---|---|
| `assert.equal` (strict) | `===` | ❌ falha (referências) | ❌ falha |
| `assert.equal` (não-strict) | `==` | ❌ falha | ✅ **passa** (perigoso) |
| `assert.deepStrictEqual` | estrutura + tipo + protótipo | ✅ passa | ❌ falha |
| `assert.deepEqual` (não-strict) | estrutura, com `==` | ✅ passa | ✅ passa (perigoso) |

**Use sempre `node:assert/strict`.** Ele faz `equal` virar `strictEqual` e `deepEqual` virar
`deepStrictEqual` automaticamente.

### Vitest / Jest: `expect`

```javascript
expect(a).toBe(b);                       // Object.is — identidade
expect(obj).toEqual({a: 1});             // estrutura, ignora undefined
expect(obj).toStrictEqual({a: 1});       // estrutura + tipos + undefined
expect(obj).toMatchObject({a: 1});       // subconjunto
expect(x).toBeTruthy() / toBeFalsy() / toBeNull() / toBeUndefined();
expect(n).toBeGreaterThan(3) / toBeCloseTo(0.3, 5);
expect(s).toContain('sub') / toMatch(/re/);
expect(arr).toHaveLength(3) / toContainEqual({a: 1});
expect(fn).toThrow(/negativo/);
await expect(promessa).rejects.toThrow();
await expect(promessa).resolves.toBe(42);
expect(espiao).toHaveBeenCalledWith('ana', expect.any(Number));
expect(espiao).toHaveBeenCalledTimes(2);
expect(x).toMatchSnapshot() / toMatchInlineSnapshot();
```

Coringas úteis dentro de `toEqual`: `expect.any(String)`, `expect.anything()`,
`expect.stringContaining('x')`, `expect.arrayContaining([1])`, `expect.closeTo(0.3)`.

---

## 4. Preparar cenário

### pytest: fixtures

Uma fixture é uma função que **produz** o que o teste pede pelo nome do parâmetro. É
injeção de dependência aplicada a testes.

```python
import pytest

@pytest.fixture
def carrinho():
    return Carrinho()                     # sem limpeza

@pytest.fixture
def banco():
    con = conectar(":memory:")
    yield con                             # tudo antes do yield = setup
    con.close()                           # tudo depois = teardown, sempre roda

def test_x(carrinho, banco):              # pedidos pelo NOME do parâmetro
    ...
```

**Escopos** — quantas vezes a fixture é criada:

| Escopo | Criada uma vez por | Quando usar |
|---|---|---|
| `function` (padrão) | teste | quase sempre |
| `class` | classe | raro |
| `module` | arquivo | conexão cara reaproveitada |
| `package` | pacote | raro |
| `session` | execução inteira | container Docker, servidor de teste |

```python
@pytest.fixture(scope="session")
def servidor():
    p = subprocess.Popen([...])
    yield "http://localhost:8000"
    p.terminate()
```

> **Armadilha:** fixture de escopo largo com estado mutável faz um teste contaminar o
> seguinte, e o sintoma é falha que depende da ordem. Regra: escopo largo **só** para coisas
> imutáveis ou que você limpa explicitamente.

**`autouse`** — aplica-se sem ser pedida:

```python
@pytest.fixture(autouse=True)
def limpar_registro():
    REGISTRO.clear()
    yield
```

Use com muita parcimônia: fixture invisível é a principal causa de "por que esse teste
falhou?".

**Fixtures nativas mais úteis:**

| Fixture | O que dá |
|---|---|
| `tmp_path` | `pathlib.Path` para um diretório temporário exclusivo do teste |
| `tmp_path_factory` | idem, com escopo de sessão |
| `capsys` | captura `stdout`/`stderr` (`capsys.readouterr().out`) |
| `capfd` | idem, em nível de descritor de arquivo (pega subprocesso) |
| `monkeypatch` | altera atributo, `dict`, variável de ambiente ou `cwd`, e **desfaz** |
| `caplog` | captura o `logging` |
| `recwarn` | captura avisos |
| `request` | metadados do teste em execução |

```python
def test_env(monkeypatch):
    monkeypatch.setenv("MODO", "teste")
    monkeypatch.setattr(modulo, "CONSTANTE", 42)
    monkeypatch.delitem(config, "chave")
    monkeypatch.chdir(tmp_path)
    # tudo desfeito automaticamente no fim
```

Descobrir o que existe: `pytest --fixtures` (todas) · `pytest --fixtures-per-test` (quais
cada teste usa).

### node:test / Vitest / Jest: hooks

```javascript
import { after, afterEach, before, beforeEach, describe, it } from 'node:test';

before(() => {});      // uma vez, antes de tudo no escopo
beforeEach(() => {});  // antes de cada teste
afterEach(() => {});   // depois de cada teste
after(() => {});       // uma vez, no fim
```

Diferença conceitual importante em relação ao pytest: hooks rodam para **todos** os testes
do bloco, sejam necessários ou não. Fixture do pytest só roda para quem **pede**. Em suíte
grande, isso é diferença de segundos.

O equivalente à "fixture" em JavaScript é uma **função de fábrica**:

```javascript
function montarCarrinho({ vazio = true } = {}) {
  const c = new Carrinho();
  if (!vazio) c.adicionar(produto());
  return c;
}

it('soma', () => {
  const c = montarCarrinho({ vazio: false });   // explícito, sem mágica
});
```

**Opinião:** em JavaScript, prefira funções de fábrica a `beforeEach` com variáveis `let` no
escopo do `describe`. O teste fica autocontido e você lê o cenário na própria linha.

---

## 5. Vários dados (parametrização)

### pytest

```python
@pytest.mark.parametrize(
    ("entrada", "esperado"),
    [(100, 10), (200, 20), (0, 0)],
    ids=["cem", "duzentos", "zero"],       # nomes legíveis no relatório
)
def test_gorjeta(entrada, esperado):
    assert calcular_gorjeta(entrada, 10) == esperado
```

Empilhar decoradores faz o **produto cartesiano** (3 × 2 = 6 testes):

```python
@pytest.mark.parametrize("conta", [100, 200, 300])
@pytest.mark.parametrize("percentual", [10, 15])
def test_combinacoes(conta, percentual): ...
```

Marcar um caso individual:

```python
@pytest.mark.parametrize("x", [1, 2, pytest.param(3, marks=pytest.mark.xfail)])
```

Parametrizar a **fixture** (roda toda a suíte que a usa, uma vez por parâmetro):

```python
@pytest.fixture(params=["memoria", "sqlite"])
def repositorio(request): ...
```

Esse é o padrão de **teste de contrato** — ver o projeto-modelo.

### JavaScript

```javascript
// node:test — laço explícito
for (const [entrada, esperado] of [[100, 10], [200, 20]]) {
  it(`gorjeta de ${entrada} é ${esperado}`, () => {
    assert.equal(calcularGorjeta(entrada, 10), esperado);
  });
}

// Vitest / Jest — it.each
it.each([
  [100, 10],
  [200, 20],
])('gorjeta de %i é %i', (entrada, esperado) => {
  expect(calcularGorjeta(entrada, 10)).toBe(esperado);
});

// it.each com objetos e template — mais legível
it.each`
  conta  | percentual | esperado
  ${100} | ${10}      | ${10}
  ${200} | ${15}      | ${30}
`('$conta a $percentual% dá $esperado', ({ conta, percentual, esperado }) => {
  expect(calcularGorjeta(conta, percentual)).toBe(esperado);
});
```

---

## 6. Pular, marcar, esperar falha

### pytest

```python
@pytest.mark.skip(reason="API externa fora do ar até 20/08")
@pytest.mark.skipif(sys.platform == "win32", reason="caminho POSIX")
@pytest.mark.xfail(reason="bug #1234, corrigir na v2")
@pytest.mark.xfail(strict=True)   # se PASSAR, o teste FALHA — avisa que o bug sumiu
@pytest.mark.integracao           # marcador seu, declarado no pyproject.toml

pytest.skip("motivo")              # no meio do teste
pytest.importorskip("hypothesis")  # pula o arquivo inteiro se faltar a lib
pytestmark = pytest.mark.lento     # marca TODOS os testes do arquivo
```

Declare seus marcadores e ative `--strict-markers`:

```toml
[tool.pytest.ini_options]
addopts = ["--strict-markers"]
markers = ["integracao: toca I/O real", "lento: leva mais de 1s"]
```

Sem `--strict-markers`, escrever `@pytest.mark.integraçao` (com cedilha) faz o marcador
existir do nada, o filtro `-m integracao` não pega, e você acha que rodou o que não rodou.

### JavaScript

```javascript
// node:test
it('x', { skip: true }, () => {});
it('x', { skip: 'motivo' }, () => {});
it('x', { todo: 'ainda não implementado' }, () => {});
it('x', { only: true }, () => {});          // + rodar com --test-only
it('x', { concurrency: 4 }, () => {});
it('x', { timeout: 5000 }, () => {});

// Vitest / Jest
it.skip / it.only / it.todo / it.fails / it.concurrent
describe.skipIf(condicao) / describe.runIf(condicao)   // Vitest
```

---

## 7. Dublês

Taxonomia completa em [14-dubles-de-teste.md](14-dubles-de-teste.md). Aqui, a sintaxe.

### Python — `unittest.mock`

```python
from unittest.mock import MagicMock, Mock, call, create_autospec, patch

m = Mock()
m.metodo.return_value = 42
m.metodo.side_effect = ValueError("boom")          # explode
m.metodo.side_effect = [1, 2, 3]                   # devolve em sequência

m.metodo.assert_called()
m.metodo.assert_called_once()
m.metodo.assert_called_with("ana", 42)
m.metodo.assert_called_once_with("ana", 42)
m.metodo.assert_not_called()
m.metodo.assert_any_call("ana")
assert m.metodo.call_args_list == [call("a"), call("b")]
assert m.metodo.call_count == 2

# substituir temporariamente
with patch("meu.modulo.requests.get") as fake:
    fake.return_value.status_code = 200
    ...

@patch("meu.modulo.Servico")        # decorador — cuidado com a ORDEM dos parâmetros
def test_x(FakeServico): ...

# com verificação de assinatura — PREFIRA ESTA
gateway = create_autospec(GatewayHttp, instance=True)
gateway.metodo_inexistente()        # AttributeError, como deveria
```

> **Onde apontar o `patch`:** você aplica no lugar onde o nome é **usado**, não onde é
> definido. Se `meu_modulo.py` faz `from requests import get`, o alvo é
> `"meu_modulo.get"`, não `"requests.get"`. Este é o erro nº 1 do `mock` em Python.

### node:test

```javascript
it('x', (t) => {
  const fn = t.mock.fn();                        // função falsa
  const fn2 = t.mock.fn(() => 42);               // com implementação
  const espiao = t.mock.method(obj, 'metodo');   // espiona, mantendo o original
  const troca = t.mock.method(obj, 'm', () => 1);// espiona e substitui
  t.mock.getter(obj, 'prop', () => 1);
  t.mock.module('./x.js', { namedExports: {} }); // Stability 1.0 no Node 26

  fn.mock.callCount();
  fn.mock.calls[0].arguments;
  fn.mock.calls[0].result;
  fn.mock.restore();
  // tudo restaurado automaticamente no fim do teste
});
```

### Vitest / Jest

```javascript
import { vi } from 'vitest';   // em Jest: jest.*

const fn = vi.fn();
fn.mockReturnValue(42);
fn.mockResolvedValue(42);
fn.mockRejectedValueOnce(new Error('boom'));
fn.mockImplementation((a) => a * 2);

const espiao = vi.spyOn(obj, 'metodo');
espiao.mockRestore();

vi.mock('./modulo.js', () => ({ funcao: vi.fn() }));   // içado para o topo!
vi.mock('./modulo.js');                                 // automock
vi.unmock('./modulo.js');

vi.clearAllMocks();    // zera contadores
vi.resetAllMocks();    // zera contadores E implementações
vi.restoreAllMocks();  // devolve os originais dos spyOn
```

> `vi.mock`/`jest.mock` são **içados** (*hoisted*) para o topo do arquivo pelo
> transformador, antes dos `import`. Isso é a fonte de comportamento surpreendente: uma
> variável declarada acima do `vi.mock` ainda não existe quando a fábrica roda. A saída é
> `vi.hoisted()`.

---

## 8. Tempo, aleatoriedade e ambiente

```python
# Python — congelar o relógio (biblioteca externa)
# pip install freezegun
from freezegun import freeze_time

@freeze_time("2026-08-12")
def test_x(): ...

# semente fixa para aleatoriedade
random.seed(42)

# variável de ambiente
def test_y(monkeypatch):
    monkeypatch.setenv("API_KEY", "falsa")
```

```javascript
// node:test
t.mock.timers.enable({ apis: ['Date', 'setTimeout'], now: Date.UTC(2026, 7, 12) });
t.mock.timers.tick(1000);
t.mock.timers.runAll();
t.mock.timers.reset();

// Vitest / Jest
vi.useFakeTimers();
vi.setSystemTime(new Date('2026-08-12'));
vi.advanceTimersByTime(1000);
await vi.advanceTimersByTimeAsync(1000);
vi.runAllTimers();
vi.useRealTimers();          // SEMPRE no afterEach, senão vaza

// ambiente
vi.stubEnv('API_KEY', 'falsa');
vi.unstubAllEnvs();
```

**Recomendação forte:** antes de alcançar qualquer uma dessas ferramentas, considere
**injetar** o relógio/gerador como dependência. É mais simples, não vaza entre testes e
melhora o design. O projeto-modelo faz assim, e a discussão está em
[20-testabilidade-e-design.md](20-testabilidade-e-design.md).

---

## 9. Testes assíncronos

```python
# pytest, com pytest-asyncio (pip install pytest-asyncio)
@pytest.mark.asyncio
async def test_x():
    assert await buscar() == 42

# ou, no pyproject.toml, para não repetir o marcador:
# [tool.pytest.ini_options]
# asyncio_mode = "auto"
```

```javascript
// node:test, Vitest, Jest — basta a função ser async
it('busca', async () => {
  assert.equal(await buscar(), 42);
});

// ERRO CLÁSSICO: esquecer o await faz o teste passar sempre
it('errado', async () => {
  assert.rejects(async () => f());     // sem await → passa mesmo se não rejeitar
});
it('certo', async () => {
  await assert.rejects(async () => f());
});
```

> Esse esquecimento é a causa mais comum de teste verde que não testa nada em JavaScript.
> A regra de lint `require-await` e a `@typescript-eslint/no-floating-promises` pegam boa
> parte dos casos — vale ligar.

---

## 10. Cobertura

```bash
# Python
pytest --cov                       # usa a config do pyproject
pytest --cov=meupacote --cov-report=term-missing
pytest --cov --cov-report=html     # gera htmlcov/index.html
pytest --cov --cov-branch          # cobertura de RAMO, não só de linha
pytest --cov --cov-fail-under=80   # falha se cair abaixo
```

```bash
# node:test — usa a instrumentação do V8, sem transformar o código
node --test --experimental-test-coverage
node --test --experimental-test-coverage --test-coverage-lines=80
node --test --experimental-test-coverage --test-coverage-exclude="test/**"

# Vitest
vitest run --coverage
```

Ignorar trechos deliberadamente:

```python
if TYPE_CHECKING:          # pragma: no cover
def __repr__(self): ...    # pragma: no cover
```

```javascript
/* node:coverage disable */
/* node:coverage enable */
/* node:coverage ignore next */
/* c8 ignore next */          // Vitest, provider v8
```

**Cobertura de linha mente.** `if a and b:` conta como coberta se você só testou o caso
verdadeiro. Ligue **sempre** `--cov-branch` (Python); o `node:test` e o Vitest já reportam
ramo por padrão. Por que isso importa e o que fazer: [19-cobertura-e-metricas.md](19-cobertura-e-metricas.md).

---

## 11. Velocidade

| Objetivo | pytest | node:test | Vitest |
|---|---|---|---|
| paralelizar | `pytest -n auto` (plugin `pytest-xdist`) | `--test-concurrency=N` (por arquivo) | padrão: um worker por CPU |
| achar os lentos | `--durations=10` | tempo por teste na saída | `--reporter=verbose` |
| ordem aleatória | `pytest -p randomly` (`pytest-randomly`) | — | `--sequence.shuffle` |
| rodar só afetados | `pytest --testmon` (plugin) | — | `vitest related` |
| tempo limite | `--timeout=5` (`pytest-timeout`) | `{ timeout: 5000 }` | `testTimeout` na config |

**Ordem aleatória é subestimada.** Se a sua suíte só passa numa ordem, ela tem acoplamento
escondido entre testes — e isso vai explodir quando alguém paralelizar. Rodar embaralhado de
vez em quando é a forma barata de descobrir.

---

## 12. Configuração

### Python — `pyproject.toml` (preferido)

```toml
[tool.pytest.ini_options]
minversion = "8.0"
testpaths = ["tests"]
addopts = ["--import-mode=importlib", "--strict-markers", "--strict-config", "-ra"]
markers = ["integracao: toca I/O real", "lento: > 1s"]
filterwarnings = ["error"]
```

Alternativas históricas, em ordem de precedência: `pytest.ini` > `pyproject.toml` >
`tox.ini` > `setup.cfg`. **Escolha uma.** Ter duas é fonte garantida de confusão.

Desde o pytest 9 há suporte nativo a configuração em TOML sem depender do `[tool.pytest]`
legado; o formato acima continua funcionando e é o mais encontrado.

### JavaScript

`node:test` não tem arquivo de configuração — tudo é bandeira de linha de comando, e você
guarda no `package.json`:

```json
{
  "scripts": {
    "test": "node --test",
    "test:cov": "node --test --experimental-test-coverage"
  }
}
```

Vitest usa `vitest.config.js` (ou a seção `test` do `vite.config.js`); Jest usa
`jest.config.js` ou a chave `"jest"` do `package.json`.

---

## 13. Depurar um teste

```bash
# Python
pytest --pdb                # abre o depurador NA falha
pytest --trace              # abre no início de cada teste
pytest -s                   # deixa o print() aparecer
pytest -l                   # mostra variáveis locais no traceback
python -m pdb -m pytest ...
```

```python
breakpoint()   # no meio do teste, com -s
```

```bash
# JavaScript
node --inspect-brk --test test/x.test.js    # abre depurador; conecte pelo Chrome/VS Code
```

No VS Code, com a extensão de Python ou o Vitest Explorer, dá para pôr *breakpoint* na
margem e rodar o teste em modo depuração com um clique. É o caminho mais produtivo.

---

## 14. O que está obsoleto

| Obsoleto | Substituto | Desde |
|---|---|---|
| `unittest.TestCase` + `self.assertEqual` (em código novo Python) | `assert` puro com pytest | ~2015, na prática |
| `nose` / `nose2` | pytest | `nose` morto desde 2015 |
| setup/teardown ao estilo nose (`setup_method` herdado do nose) | fixtures | **removido no pytest 9** |
| `pytest.collect` (namespace legado) | API atual | **removido no pytest 9** |
| testes com `yield` (gerando casos) | `parametrize` | removido no pytest 9 |
| `mocha` + `chai` + `sinon` (três pacotes) | Vitest, ou `node:test` | ~2022 |
| `karma` | Vitest browser mode / Playwright | descontinuado em 2023 |
| `enzyme` (React) | Testing Library | ~2021 |
| `jest` com Babel para ESM | Vitest, ou Node com ESM nativo | ~2024 |
| `protractor` | Playwright / Cypress | descontinuado em 2023 |
| `--experimental-test-coverage` como flag | (ainda é flag no Node 24; acompanhar) | — |
| `assert.equal` sem `/strict` | `node:assert/strict` | sempre foi má ideia |

---

## 15. Atalhos que só quem usa há anos conhece

**pytest**

1. `pytest --lf -x` — o combo de conserto: só o que falhou, para no primeiro. Encurta o
   laço de segundos para décimos de segundo.
2. `pytest --sw` (*stepwise*) — para no primeiro erro e, na próxima execução, **continua
   daquele teste**. Perfeito para arrumar 30 testes quebrados por uma refatoração.
3. `pytest --collect-only -q | wc -l` — quantos testes eu tenho mesmo?
4. `pytest --durations=0 | head -20` — a lista completa de lentidão, ordenada.
5. `pytest -p no:randomly` — desliga a aleatorização quando você precisa reproduzir uma ordem.
6. `PYTEST_ADDOPTS="-x -q" pytest` — bandeiras via variável de ambiente, útil em CI.
7. `pytest --setup-show` — mostra a árvore de fixtures sendo criada e destruída. É a melhor
   ferramenta para entender por que uma fixture está rodando cedo demais.
8. `assert resultado == esperado` com **dicionários grandes**: use `-vv`, senão o pytest
   trunca o diff e você não vê a diferença.
9. `conftest.py` na raiz do repositório vale para tudo abaixo — e é o lugar certo para
   `collect_ignore` e ajustes de `sys.path`.
10. `pytest.ini` vazio na raiz basta para o pytest fixar o `rootdir` ali. Resolve metade dos
    problemas de import misteriosos.

**node:test / Vitest**

1. `node --test --watch --test-name-pattern="^Dinheiro"` — laço curtíssimo num só assunto.
2. `it('x', { only: true })` + `--test-only` — o equivalente do `.only` do Mocha.
3. `--test-reporter=dot` em CI: o log fica 20 vezes menor e você ainda vê as falhas.
4. `--experimental-test-isolation=none` (Node 22+) roda tudo num só processo: bem mais
   rápido, ao custo de perder isolamento. Bom para suíte pequena e pura.
5. `vitest --ui` abre um painel com o grafo de módulos — acha import circular na hora.
6. `vitest related --run src/x.js` no *hook* de pré-commit: roda só o que aquele arquivo
   afeta.
7. `expect(algo).toMatchInlineSnapshot()` **vazio**: rode uma vez e o Vitest escreve o
   valor esperado dentro do seu arquivo. Ótimo para capturar saída complexa — e perigoso,
   ver [75-armadilhas.md](75-armadilhas.md).
8. `t.diagnostic('mensagem')` no `node:test` emite uma linha `ℹ` no relatório, sem sujar a
   saída como `console.log`.

---

## Autoteste

1. Qual comando roda só os testes que falharam da última vez, em pytest?
2. Qual a diferença entre `F` e `E` na saída do pytest, e o que cada um costuma indicar?
3. Por que `vitest` sem `run` é um problema em CI?
4. Qual a diferença entre `toBe`, `toEqual` e `toStrictEqual`?
5. Por que `node:assert/strict` e não `node:assert`?
6. O que `--strict-markers` evita?
7. Você faz `from requests import get` no seu módulo. Qual é o alvo correto do `patch`?
8. Cite duas diferenças conceituais entre uma fixture do pytest e um `beforeEach`.
9. Por que rodar a suíte em ordem aleatória de vez em quando é uma boa ideia?
10. Qual o problema de `assert.rejects(...)` sem `await`?
