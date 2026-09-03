# 04 · Do ambiente pronto à primeira luz verde

`Nível: iniciante` · `Tempo: 20 a 40 minutos` · `Última atualização: 12/08/2026`

Este arquivo assume que você já seguiu o [03-instalacao.md](03-instalacao.md) e que o
checklist final passou. Nada de instalação aqui.

Todas as saídas abaixo foram **executadas** em 12/08/2026 (Ubuntu 22.04, Python 3.10.12 +
pytest 9.1.1, Node v24.18.0). É o que você vai ver na sua tela, não uma aproximação.

---

## 1. Escolha a trilha

Faça **uma**. As duas fazem exatamente a mesma coisa, e a seção 6 mostra a tradução.

- [Python, com pytest](#2-python--o-primeiro-teste)
- [JavaScript, com `node:test`](#3-javascript--o-primeiro-teste)

---

## 2. Python — o primeiro teste

### 2.1 Crie a pasta e o código

```bash
mkdir primeiro && cd primeiro
```

Crie um arquivo chamado **`gorjeta.py`**:

```python
def calcular_gorjeta(conta, percentual):
    """Devolve o valor da gorjeta para uma conta."""
    return conta * percentual / 100
```

### 2.2 Crie o teste

Crie **`test_gorjeta.py`** — o nome importa: o pytest procura arquivos que comecem com
`test_` (ou terminem com `_test.py`).

```python
from gorjeta import calcular_gorjeta


def test_gorjeta_de_dez_por_cento():
    assert calcular_gorjeta(100, 10) == 10
```

Três regras de nomenclatura que o pytest usa para **descobrir** os testes sozinho:

| Coisa | Padrão |
|---|---|
| arquivo | `test_*.py` ou `*_test.py` |
| função | `test_*` |
| classe | `Test*`, **sem** método `__init__` |

### 2.3 Rode

```bash
pytest
```

Saída real:

```
============================= test session starts ==============================
platform linux -- Python 3.10.12, pytest-9.1.1, pluggy-1.6.0
rootdir: /caminho/para/primeiro
plugins: cov-7.1.0, hypothesis-6.165.3
collected 1 item

test_gorjeta.py .                                                        [100%]

============================== 1 passed in 0.43s ===============================
```

**Você acabou de escrever e rodar um teste automatizado.** Leia a saída:

- `collected 1 item` — o pytest encontrou 1 teste sozinho. Você não registrou nada.
- `test_gorjeta.py .` — o ponto é o teste passando. Cada teste vira um caractere:
  `.` passou, `F` falhou, `E` erro, `s` pulado, `x` falha esperada.
- `1 passed in 0.43s` — o placar.

### 2.4 Agora faça falhar (a parte mais importante)

Um teste que você nunca viu falhar **não é um teste** — é uma linha de código que você
espera que funcione. Acrescente ao `test_gorjeta.py`:

```python
def test_gorjeta_nunca_e_negativa():
    assert calcular_gorjeta(100, -10) >= 0
```

```bash
pytest
```

Saída real:

```
collected 2 items

test_gorjeta.py .F                                                       [100%]

=================================== FAILURES ===================================
________________________ test_gorjeta_nunca_e_negativa _________________________

    def test_gorjeta_nunca_e_negativa():
>       assert calcular_gorjeta(100, -10) >= 0
E       assert -10.0 >= 0
E        +  where -10.0 = calcular_gorjeta(100, -10)

test_gorjeta.py:9: AssertionError
=========================== short test summary info ============================
FAILED test_gorjeta.py::test_gorjeta_nunca_e_negativa - assert -10.0 >= 0
========================= 1 failed, 1 passed in 0.15s ==========================
```

Pare e olhe com atenção para estas três linhas:

```
>       assert calcular_gorjeta(100, -10) >= 0
E       assert -10.0 >= 0
E        +  where -10.0 = calcular_gorjeta(100, -10)
```

O pytest **reescreve** suas asserções para mostrar o valor de cada parte da expressão. Você
não precisou escrever `assert x >= 0, f"deu {x}"`. Isso se chama *assertion rewriting*, é a
maior razão prática de o pytest ter vencido o `unittest`, e funciona por mágica de bytecode
— explicada em [16-python-pytest.md](16-python-pytest.md).

### 2.5 Conserte

O teste vermelho está dizendo algo verdadeiro: a função aceita percentual negativo e devolve
gorjeta negativa. Isso é um **bug de verdade** que você acabou de encontrar em três linhas.

```python
def calcular_gorjeta(conta, percentual):
    """Devolve o valor da gorjeta para uma conta.

    Percentual negativo não faz sentido: gorjeta não é desconto.
    """
    if percentual < 0:
        raise ValueError(f"percentual não pode ser negativo: {percentual}")
    return conta * percentual / 100
```

E o teste passa a dizer o que se espera de verdade:

```python
import pytest

from gorjeta import calcular_gorjeta


def test_gorjeta_de_dez_por_cento():
    assert calcular_gorjeta(100, 10) == 10


def test_percentual_negativo_e_recusado():
    with pytest.raises(ValueError, match="não pode ser negativo"):
        calcular_gorjeta(100, -10)
```

```bash
pytest -q
```
```
..                                                                       [100%]
2 passed in 0.02s
```

`pytest.raises` é o "afirmo que isto explode". Sem ele, um teste do caminho de erro teria de
ser escrito com `try/except` e um `pytest.fail()` no meio — feio e fácil de errar.

---

## 3. JavaScript — o primeiro teste

### 3.1 Crie a pasta e declare ESM

```bash
mkdir primeiro && cd primeiro
```

Crie **`package.json`** com uma linha só. Isso diz ao Node que os arquivos usam
`import`/`export` (módulos ES), e não `require` (CommonJS):

```json
{ "type": "module" }
```

### 3.2 Crie o código

**`gorjeta.js`**:

```javascript
export function calcularGorjeta(conta, percentual) {
  return (conta * percentual) / 100;
}
```

### 3.3 Crie o teste

**`gorjeta.test.js`** — o `node:test` procura, por padrão, arquivos `*.test.js`,
`*-test.js`, `test.js`, e tudo que estiver numa pasta `test/`.

```javascript
import assert from 'node:assert/strict';
import { test } from 'node:test';

import { calcularGorjeta } from './gorjeta.js';

test('gorjeta de dez por cento', () => {
  assert.equal(calcularGorjeta(100, 10), 10);
});
```

Duas coisas que confundem quem vem do Python:

1. **`node:assert/strict`, não `node:assert`.** A versão não-estrita usa `==` (comparação
   frouxa), e `assert.equal('10', 10)` **passa**. Use sempre `/strict`.
2. **A extensão `.js` no import é obrigatória** em ESM. `from './gorjeta'` dá
   `ERR_MODULE_NOT_FOUND`.

### 3.4 Rode

```bash
node --test
```

Saída real:

```
✔ gorjeta de dez por cento (0.849657ms)
ℹ tests 1
ℹ suites 0
ℹ pass 1
ℹ fail 0
ℹ cancelled 0
ℹ skipped 0
ℹ todo 0
ℹ duration_ms 95.699942
```

Sem instalar nada. Sem `node_modules`. Sem configuração.

### 3.5 Agora faça falhar

```javascript
test('gorjeta nunca é negativa', () => {
  assert.ok(calcularGorjeta(100, -10) >= 0);
});
```

```bash
node --test
```

Saída real (recortada):

```
✔ gorjeta de dez por cento (0.849657ms)
✖ gorjeta nunca é negativa (15.88277ms)
ℹ tests 2
ℹ pass 1
ℹ fail 1

✖ failing tests:

test at gorjeta.test.js:10:1
✖ gorjeta nunca é negativa (15.88277ms)
  AssertionError [ERR_ASSERTION]: The expression evaluated to a falsy value:

    assert.ok(calcularGorjeta(100, -10) >= 0)

    ...
    actual: false,
    expected: true,
```

Repare na diferença em relação ao pytest: o `node:test` mostra `actual: false` — ele não
sabe que `-10` era o valor intermediário, porque `assert.ok` só recebe um booleano já
avaliado. **Lição prática:** em JavaScript, prefira asserções que recebem os dois lados:

```javascript
// ruim: a mensagem de falha só diz "false"
assert.ok(calcularGorjeta(100, -10) >= 0);

// bom: a mensagem mostra os dois valores
assert.equal(calcularGorjeta(100, 10), 10);

// quando precisar de comparação, calcule antes e nomeie
const gorjeta = calcularGorjeta(100, -10);
assert.ok(gorjeta >= 0, `gorjeta ficou ${gorjeta}`);
```

Essa é a razão número 1 pela qual muita gente prefere Vitest/Jest em JavaScript: o
`expect(x).toBeGreaterThanOrEqual(0)` produz mensagem melhor de graça.

### 3.6 Conserte

```javascript
export function calcularGorjeta(conta, percentual) {
  if (percentual < 0) {
    throw new RangeError(`percentual não pode ser negativo: ${percentual}`);
  }
  return (conta * percentual) / 100;
}
```

```javascript
import assert from 'node:assert/strict';
import { test } from 'node:test';

import { calcularGorjeta } from './gorjeta.js';

test('gorjeta de dez por cento', () => {
  assert.equal(calcularGorjeta(100, 10), 10);
});

test('percentual negativo é recusado', () => {
  assert.throws(() => calcularGorjeta(100, -10), {
    name: 'RangeError',
    message: /não pode ser negativo/,
  });
});
```

```bash
node --test
```
```
ℹ tests 2
ℹ pass 2
ℹ fail 0
```

> **Cuidado com um erro clássico:** `assert.throws(calcularGorjeta(100, -10))` — sem a
> função-seta — chama a função **antes** e o erro escapa. `assert.throws` precisa receber
> **uma função para chamar**, não um resultado. O equivalente em Python é escrever
> `pytest.raises(ValueError, calcular_gorjeta(100, -10))` em vez de usar o `with`.

---

## 4. Verificação: você chegou lá?

Marque:

- [ ] Vi a saída verde de pelo menos um teste meu.
- [ ] Vi a saída **vermelha** e entendi qual linha falhou e por quê.
- [ ] Escrevi um teste que verifica que algo **explode** (`pytest.raises` / `assert.throws`).
- [ ] Sei o padrão de nome que faz o corredor encontrar meus testes.

Se todos estão marcados, você já é operacional. O resto é vocabulário e profundidade.

---

## 5. O ciclo de trabalho de verdade

Ninguém digita `pytest` a cada mudança. O ciclo real é:

### 5.1 Modo *watch*: roda sozinho ao salvar

```bash
# JavaScript — embutido
node --test --watch

# Python — precisa de um plugin
pip install pytest-watcher
ptw .
```

Salve o arquivo, olhe o canto da tela. Verde ou vermelho em menos de um segundo. É este
laço curto que muda a forma de programar — não a existência dos testes.

### 5.2 Rodar só o que interessa

Enquanto trabalha num pedaço, rode só aquele pedaço:

```bash
# Python
pytest test_gorjeta.py                      # um arquivo
pytest test_gorjeta.py::test_gorjeta_de_dez_por_cento   # um teste
pytest -k "negativo"                        # tudo que tem "negativo" no nome
pytest --lf                                 # só os que falharam da última vez
pytest -x                                   # para no primeiro erro
```

```bash
# JavaScript
node --test gorjeta.test.js                 # um arquivo
node --test --test-name-pattern="negativo"  # por nome
node --test --test-only                     # só os marcados com { only: true }
```

`pytest --lf` (*last failed*) é, na opinião de quem escreve isto, o atalho de maior retorno
do pytest inteiro: você conserta, roda `--lf`, e vê em meio segundo se resolveu, sem esperar
a suíte inteira.

### 5.3 O ciclo completo, no dia

```
   escreve/muda código
          │
          ├──► salva ──► watch roda ──► 🔴 ──► lê a mensagem ──► arruma ──┐
          │                              │                                │
          │                              └──► 🟢 ──► continua             │
          │                                                               │
          └───────────────────────────────────────────────────────────────┘
                                        │
          antes de enviar:  suíte inteira 🟢  →  commit  →  CI roda tudo de novo
```

---

## 6. A mesma coisa nas duas linguagens

Guarde esta tabela. Ela é o que permite ler qualquer exemplo deste curso independentemente
da trilha que você escolheu.

| Ideia | pytest (Python) | `node:test` (JavaScript) | Vitest / Jest |
|---|---|---|---|
| um teste | `def test_x():` | `test('x', () => {})` | `it('x', () => {})` |
| agrupar | `class TestX:` | `describe('X', () => {})` | `describe('X', () => {})` |
| igualdade | `assert a == b` | `assert.equal(a, b)` | `expect(a).toBe(b)` |
| igualdade profunda | `assert a == b` | `assert.deepStrictEqual(a, b)` | `expect(a).toEqual(b)` |
| verdadeiro | `assert x` | `assert.ok(x)` | `expect(x).toBeTruthy()` |
| explode | `with pytest.raises(E):` | `assert.throws(fn, E)` | `expect(fn).toThrow(E)` |
| explode (async) | `with pytest.raises(E):` + `await` | `await assert.rejects(fn, E)` | `await expect(p).rejects.toThrow()` |
| texto casa regex | `assert re.search(r, s)` | `assert.match(s, /r/)` | `expect(s).toMatch(/r/)` |
| antes de cada teste | fixture | `beforeEach()` | `beforeEach()` |
| vários casos | `@pytest.mark.parametrize` | laço gerando `test()` | `it.each([...])` |
| pular | `@pytest.mark.skip` | `test('x', { skip: true })` | `it.skip` |
| falha esperada | `@pytest.mark.xfail` | `test('x', { todo: true })` | `it.fails` |
| dublê | `unittest.mock.Mock()` | `t.mock.fn()` | `vi.fn()` / `jest.fn()` |
| cobertura | `pytest --cov` | `node --test --experimental-test-coverage` | `vitest run --coverage` |

---

## 7. Os cinco erros que todo iniciante comete (no uso, não na instalação)

### 7.1 Escrever o teste depois, "quando der tempo"

Não dá. A verdade prática: teste escrito depois é teste que confirma o que o código faz, e
não o que ele deveria fazer. Se você escreveu o bug, você vai escrever o teste que aprova o
bug. Escreva junto — não necessariamente antes (isso é TDD, cap. 15), mas **junto**.

### 7.2 Um teste que verifica cinco coisas

```python
# ruim
def test_gorjeta():
    assert calcular_gorjeta(100, 10) == 10
    assert calcular_gorjeta(200, 10) == 20
    assert calcular_gorjeta(0, 10) == 0
    with pytest.raises(ValueError):
        calcular_gorjeta(100, -1)
```

Quando isso falha, você sabe que "o teste da gorjeta falhou" e nada mais. Pior: a primeira
asserção que falha **interrompe** o teste, então as outras nem rodam — você conserta uma
coisa, roda de novo, descobre a segunda. Isso se chama *assertion roulette*.

O certo é um comportamento por teste, com nome que diz qual:

```python
def test_gorjeta_de_dez_por_cento_sobre_cem(): ...
def test_gorjeta_de_conta_zerada_e_zero(): ...
def test_percentual_negativo_e_recusado(): ...
```

### 7.3 Nome de teste que não diz nada

`test_1`, `test_funciona`, `test_calcular_gorjeta`. Quando esse teste falhar no CI às
23h de uma sexta-feira, o nome é a única coisa que você vê primeiro.

Regra prática: o nome deve completar a frase **"o sistema deve..."**.

- ✅ `test_percentual_negativo_e_recusado`
- ✅ `test_gorjeta_de_conta_zerada_e_zero`
- ❌ `test_gorjeta_2`

### 7.4 Repetir a lógica do código dentro do teste

```python
# ruim: se a fórmula estiver errada, o teste está errado do mesmo jeito
def test_gorjeta():
    assert calcular_gorjeta(100, 10) == 100 * 10 / 100
```

O teste tem de trazer o valor esperado **calculado por fora**, de preferência por uma pessoa
com uma calculadora. `== 10`. Um teste que reimplementa a função não testa nada.

### 7.5 Testar detalhe de implementação em vez de comportamento

```python
# ruim: quebra se você renomear uma variável interna
def test_usa_a_variavel_temporaria():
    assert hasattr(calcular_gorjeta, "_cache")
```

O teste deve verificar o que se pode observar de fora: o retorno, a exceção, o efeito. Se o
teste quebra quando você refatora **sem mudar o comportamento**, o teste está errado. Esse é
o critério mais útil que existe para julgar um teste, e volta em
[13-teste-unitario-a-fundo.md](13-teste-unitario-a-fundo.md).

---

## 8. Onde ir agora

| Se você quer... | Vá para |
|---|---|
| mais exemplos, do trivial ao real | [06-exemplos.md](06-exemplos.md) |
| a referência dos comandos e opções | [05-manual-de-uso.md](05-manual-de-uso.md) |
| ver uma aplicação inteira testada | [07-projeto-modelo/](07-projeto-modelo/README.md) |
| entender os conceitos por baixo | [10-fundamentos.md](10-fundamentos.md) |
| exercícios com correção | [70-pratica.md](70-pratica.md) |

---

## Autoteste

1. Que padrão de nome faz o pytest encontrar seu teste? E o `node:test`?
2. Por que ver o teste **falhar** pelo menos uma vez é obrigatório?
3. O que o pytest faz de diferente na mensagem de falha, e como isso se chama?
4. Por que `assert.ok(x >= 0)` dá uma mensagem pior que `assert.equal(a, b)` em JavaScript?
5. Qual o erro em `assert.throws(minhaFuncao(1, 2))`?
6. Por que `node:assert/strict` e não `node:assert`?
7. Explique, com suas palavras, por que um teste com cinco asserções é pior que cinco testes.
8. O que há de errado com `assert calcular_gorjeta(100, 10) == 100 * 10 / 100`?
9. Qual o critério para dizer que um teste está testando "detalhe de implementação"?
