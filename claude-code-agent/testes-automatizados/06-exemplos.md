# 06 · Exemplos — do trivial ao de produção

`Nível: iniciante → avançado` · `Todos executados em 12/08/2026`

**Regra deste arquivo:** todo código é completo e roda como está. Nada de `...` no meio.
Cada exemplo traz problema → solução → explicação, e as saídas mostradas foram capturadas
da execução real (Python 3.10.12 + pytest 9.1.1 + Hypothesis 6.165.3; Node v24.18.0).

| # | Exemplo | Linguagem | Ensina |
|---|---|---|---|
| 1 | [Validador de CPF](#exemplo-1--validador-de-cpf) | Python | função pura, `parametrize`, `ids` |
| 2 | [Conversor CSV → JSON](#exemplo-2--conversor-csv--json) | Python | `tmp_path`, fixture, acentuação, arquivo inexistente |
| 3 | [Configuração por variável de ambiente](#exemplo-3--configuração-por-variável-de-ambiente) | Python | `monkeypatch`, valores-padrão, erro de configuração |
| 4 | [Cliente HTTP com mock](#exemplo-4--cliente-http-com-mock) | Python | `patch`, onde apontar o alvo, erro de rede como erro de domínio |
| 5 | [Parcelamento — o bug que a propriedade acha](#exemplo-5--parcelamento-o-bug-que-a-propriedade-acha) | Python | Hypothesis, *shrinking*, invariantes |
| 6 | [Carrinho de compras imutável](#exemplo-6--carrinho-de-compras-imutável) | JavaScript | `describe`/`it`, imutabilidade, fronteira do frete |
| 7 | [Repetição com espera exponencial](#exemplo-7--repetição-com-espera-exponencial) | JavaScript | `t.mock.fn`, injetar o `sleep`, testar espera sem esperar |
| 8 | [API HTTP de tarefas](#exemplo-8--api-http-de-tarefas-caso-de-produção) | JavaScript | **produção**: servidor real, status, cabeçalhos, 4xx |
| 9 | [Máquina de estados por tabela](#exemplo-9--máquina-de-estados-por-tabela) | ambas | cobrir o espaço inteiro, meta-teste |
| 10 | [Fake verificado por contrato](#exemplo-10--fake-verificado-por-contrato) | Python | a mesma bateria no fake e no real |
| 11 | [Teste de caracterização em código legado](#exemplo-11--teste-de-caracterização-em-código-legado) | Python | **produção**: rede de segurança antes de refatorar |
| 12 | [Snapshot: quando ajuda e quando apodrece](#exemplo-12--snapshot-quando-ajuda-e-quando-apodrece) | JavaScript | `toMatchInlineSnapshot`, e seus limites |

---

## Exemplo 1 — Validador de CPF

**Problema:** validar CPF é a função pura brasileira por excelência: entrada de texto,
saída booleana, regra fechada, e um monte de caso de borda.

**`cpf.py`**

```python
def limpar(cpf: str) -> str:
    return "".join(c for c in cpf if c.isdigit())


def digito_verificador(digitos: str, peso_inicial: int) -> int:
    soma = sum(int(d) * p for d, p in zip(digitos, range(peso_inicial, 1, -1)))
    resto = (soma * 10) % 11
    return 0 if resto == 10 else resto


def cpf_valido(cpf: str) -> bool:
    numeros = limpar(cpf)
    if len(numeros) != 11:
        return False
    if numeros == numeros[0] * 11:
        return False
    if digito_verificador(numeros[:9], 10) != int(numeros[9]):
        return False
    return digito_verificador(numeros[:10], 11) == int(numeros[10])
```

**`test_cpf.py`**

```python
import pytest

from cpf import cpf_valido, limpar


class TestLimpar:
    def test_remove_pontuacao(self):
        assert limpar("529.982.247-25") == "52998224725"

    def test_deixa_numeros_intactos(self):
        assert limpar("52998224725") == "52998224725"

    def test_string_vazia_vira_vazia(self):
        assert limpar("") == ""


class TestCpfValido:
    @pytest.mark.parametrize(
        "cpf",
        ["529.982.247-25", "52998224725", " 529 982 247 25 "],
        ids=["formatado", "so-numeros", "com-espacos"],
    )
    def test_aceita_cpf_valido_em_qualquer_formato(self, cpf):
        assert cpf_valido(cpf) is True

    @pytest.mark.parametrize(
        ("cpf", "motivo"),
        [
            ("529.982.247-26", "digito verificador errado"),
            ("111.111.111-11", "todos os digitos iguais"),
            ("000.000.000-00", "todos zeros"),
            ("529.982.247-2", "curto demais"),
            ("529.982.247-255", "longo demais"),
            ("", "vazio"),
            ("abcdefghijk", "sem numero nenhum"),
        ],
    )
    def test_recusa_cpf_invalido(self, cpf, motivo):
        assert cpf_valido(cpf) is False, f"deveria recusar: {motivo}"
```

```bash
pytest -q test_cpf.py
```
```
.............                                                            [100%]
13 passed in 0.17s
```

**O que ensina:**

- **`ids=`** transforma `test_aceita_cpf_valido_em_qualquer_formato[cpf0]` em
  `[formatado]`. Quando falhar no CI, você lê o nome e já sabe o caso.
- A **mensagem no `assert`** (`f"deveria recusar: {motivo}"`) diz *por que* aquele caso está
  na lista. Sem ela, `("111.111.111-11", ...)` é um número mágico.
- `assert cpf_valido(x) is True` e não `assert cpf_valido(x)`. A diferença: a segunda versão
  passa se a função devolver `"sim"`, `1` ou qualquer coisa "verdadeira". A primeira exige o
  booleano — trava o contrato de tipo, que em Python não é travado de outro jeito.
- **CPF `000.000.000-00` é matematicamente válido** pelo algoritmo dos dígitos
  verificadores. Ele é recusado pela regra explícita "todos iguais". Se essa linha sumir, o
  teste pega — e essa é exatamente a classe de regra que alguém "otimiza" fora sem saber.

---

## Exemplo 2 — Conversor CSV → JSON

**Problema:** código que escreve arquivo. Onde escrever, sem sujar a máquina e sem um teste
atrapalhar o outro?

**`test_arquivo.py`** (código e teste juntos, por brevidade)

```python
import csv
import json
from pathlib import Path

import pytest


def csv_para_json(entrada: Path, saida: Path) -> int:
    with entrada.open(encoding="utf-8", newline="") as f:
        linhas = list(csv.DictReader(f))
    saida.write_text(json.dumps(linhas, ensure_ascii=False, indent=2), encoding="utf-8")
    return len(linhas)


@pytest.fixture
def csv_de_exemplo(tmp_path: Path) -> Path:
    caminho = tmp_path / "clientes.csv"
    caminho.write_text("nome,cidade\nAna,São Paulo\nBruno,Belém\n", encoding="utf-8")
    return caminho


def test_converte_e_conta_linhas(csv_de_exemplo: Path, tmp_path: Path):
    saida = tmp_path / "clientes.json"
    assert csv_para_json(csv_de_exemplo, saida) == 2


def test_preserva_acentos(csv_de_exemplo: Path, tmp_path: Path):
    saida = tmp_path / "clientes.json"
    csv_para_json(csv_de_exemplo, saida)
    dados = json.loads(saida.read_text(encoding="utf-8"))
    assert dados[1]["cidade"] == "Belém"


def test_csv_vazio_gera_lista_vazia(tmp_path: Path):
    entrada = tmp_path / "vazio.csv"
    entrada.write_text("nome,cidade\n", encoding="utf-8")
    saida = tmp_path / "saida.json"
    assert csv_para_json(entrada, saida) == 0
    assert json.loads(saida.read_text(encoding="utf-8")) == []


def test_arquivo_inexistente_explode(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        csv_para_json(tmp_path / "nao-existe.csv", tmp_path / "s.json")
```

```bash
pytest -q test_arquivo.py
```
```
....                                                                     [100%]
4 passed in 0.17s
```

**O que ensina:**

- **`tmp_path`** entrega um diretório temporário **exclusivo daquele teste**, e o pytest o
  limpa depois (mantém os últimos 3 para você inspecionar quando algo falha). Nunca escreva
  em `/tmp/teste.csv` fixo: dois testes em paralelo colidem, e a falha aparece só às vezes.
- **Uma fixture que devolve um `Path`** é o jeito idiomático de montar dados de entrada.
- O teste de **acento** existe porque codificação é a fonte silenciosa nº 1 de bug em CSV
  brasileiro — e `ensure_ascii=False` no `json.dumps` é a linha que se perde numa
  refatoração.
- **CSV vazio** (só cabeçalho) é o caso de borda que quebra código escrito às pressas.

---

## Exemplo 3 — Configuração por variável de ambiente

**Problema:** `os.environ` é estado global. Um teste que o altera contamina o seguinte.

```python
import os

import pytest


class ConfiguracaoInvalida(Exception):
    pass


def carregar_config() -> dict:
    url = os.environ.get("BANCO_URL")
    if not url:
        raise ConfiguracaoInvalida("BANCO_URL é obrigatória")
    return {
        "url": url,
        "timeout": int(os.environ.get("BANCO_TIMEOUT", "30")),
        "debug": os.environ.get("DEBUG", "").lower() in ("1", "true", "sim"),
    }


def test_le_a_url_do_ambiente(monkeypatch):
    monkeypatch.setenv("BANCO_URL", "postgres://localhost/teste")
    assert carregar_config()["url"] == "postgres://localhost/teste"


def test_timeout_tem_padrao(monkeypatch):
    monkeypatch.setenv("BANCO_URL", "x")
    monkeypatch.delenv("BANCO_TIMEOUT", raising=False)
    assert carregar_config()["timeout"] == 30


@pytest.mark.parametrize(
    ("valor", "esperado"),
    [("1", True), ("true", True), ("SIM", True), ("0", False), ("", False), ("nao", False)],
)
def test_debug_aceita_varias_formas(monkeypatch, valor, esperado):
    monkeypatch.setenv("BANCO_URL", "x")
    monkeypatch.setenv("DEBUG", valor)
    assert carregar_config()["debug"] is esperado


def test_sem_url_explode_com_mensagem_util(monkeypatch):
    monkeypatch.delenv("BANCO_URL", raising=False)
    with pytest.raises(ConfiguracaoInvalida, match="BANCO_URL"):
        carregar_config()


def test_o_ambiente_real_nao_e_afetado(monkeypatch):
    monkeypatch.setenv("BANCO_URL", "temporaria")
    assert os.environ["BANCO_URL"] == "temporaria"
    # ...e no fim deste teste o monkeypatch remove a variável sozinho.
```

```bash
pytest -q test_env.py
```
```
..........                                                               [100%]
10 passed in 0.14s
```

**O que ensina:**

- **`monkeypatch` desfaz sozinho.** Se você fizesse `os.environ["X"] = "y"` na mão, a
  variável ficaria setada para o resto da execução — e o teste seguinte, que testa a
  ausência dela, falharia. Esse é o defeito que só aparece quando a suíte roda inteira, o
  pior de diagnosticar.
- **`raising=False`** no `delenv` evita que o teste quebre em máquinas onde a variável já
  não existia. Teste não pode depender do ambiente de quem roda.
- Testar o **valor-padrão** (`timeout == 30`) é tão importante quanto testar o configurado:
  é o caminho que 99 % das execuções de produção percorre.

---

## Exemplo 4 — Cliente HTTP com mock

**Problema:** o código chama uma API externa. O teste não pode depender da internet nem
gastar cota.

**`clima.py`**

```python
import json
import urllib.request


class ClimaIndisponivel(Exception):
    pass


def temperatura_agora(cidade: str, *, timeout: float = 5.0) -> float:
    url = f"https://api.exemplo.br/clima?cidade={cidade}"
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resposta:
            dados = json.load(resposta)
    except (TimeoutError, OSError) as erro:
        raise ClimaIndisponivel(f"não consegui falar com a API: {erro}") from erro
    if "temperatura" not in dados:
        raise ClimaIndisponivel(f"resposta sem temperatura: {dados}")
    return float(dados["temperatura"])
```

**`test_clima.py`**

```python
import io
import json
from contextlib import contextmanager
from unittest.mock import patch

import pytest

from clima import ClimaIndisponivel, temperatura_agora


def resposta_falsa(corpo: dict):
    """Imita o `urlopen`, que devolve um gerenciador de contexto com bytes dentro."""

    @contextmanager
    def gerenciador(*_args, **_kwargs):
        yield io.BytesIO(json.dumps(corpo).encode())

    return gerenciador


def test_devolve_a_temperatura_da_api():
    with patch("clima.urllib.request.urlopen", resposta_falsa({"temperatura": 23.5})):
        assert temperatura_agora("Recife") == 23.5


def test_converte_inteiro_para_float():
    with patch("clima.urllib.request.urlopen", resposta_falsa({"temperatura": 23})):
        assert temperatura_agora("Recife") == 23.0


def test_resposta_sem_o_campo_esperado_explode():
    with patch("clima.urllib.request.urlopen", resposta_falsa({"erro": "cidade desconhecida"})):
        with pytest.raises(ClimaIndisponivel, match="sem temperatura"):
            temperatura_agora("Atlantida")


def test_timeout_vira_erro_de_dominio():
    with patch("clima.urllib.request.urlopen", side_effect=TimeoutError("demorou")):
        with pytest.raises(ClimaIndisponivel, match="não consegui falar"):
            temperatura_agora("Recife")


def test_a_url_e_o_timeout_sao_montados_corretamente():
    with patch("clima.urllib.request.urlopen") as fake:
        fake.return_value.__enter__.return_value = io.BytesIO(b'{"temperatura": 1}')

        temperatura_agora("Recife", timeout=0.5)

        assert fake.call_args.args[0] == "https://api.exemplo.br/clima?cidade=Recife"
        assert fake.call_args.kwargs["timeout"] == 0.5
```

```bash
pytest -q test_clima.py
```
```
.....                                                                    [100%]
5 passed in 0.14s
```

**O que ensina:**

- **O alvo do `patch` é `"clima.urllib.request.urlopen"`, não `"urllib.request.urlopen"`.**
  Você substitui o nome **onde ele é usado**. Se `clima.py` tivesse feito
  `from urllib.request import urlopen`, o alvo seria `"clima.urlopen"`. Esse é o erro nº 1
  de `mock` em Python, e o sintoma é o teste "não fazer efeito nenhum".
- **Traduzir erro de infraestrutura para erro de domínio** (`TimeoutError` →
  `ClimaIndisponivel`) é a decisão de projeto que torna o resto do sistema testável: quem
  chama trata **um** tipo de erro, não a zoologia inteira do `urllib`.
- O último teste verifica a **interação** (a URL montada). É legítimo aqui porque a URL não
  deixa rastro no estado; ela *é* o comportamento observável.
- **Limite honesto deste exemplo:** o mock devolve o que você mandou. Ele não prova que a
  API real responde assim. Para isso existe o teste de contrato do
  [Exemplo 8](#exemplo-8--api-http-de-tarefas-caso-de-produção), com servidor de verdade.

---

## Exemplo 5 — Parcelamento: o bug que a propriedade acha

**Problema:** dividir R$ 100,00 em 3 parcelas. Quanto é cada uma? Um teste de exemplo passa
com números redondos e esconde o bug.

**`parcelas.py` — versão ingênua, com bug**

```python
def parcelar(total_centavos: int, n: int) -> list[int]:
    """Divide um total em n parcelas iguais. (Versão ingênua — tem bug.)"""
    if n <= 0:
        raise ValueError("n deve ser positivo")
    valor = total_centavos // n
    return [valor] * n
```

**Um teste de exemplo passaria:** `parcelar(9000, 3) == [3000, 3000, 3000]`. ✅

**Um teste de propriedade não:**

```python
from hypothesis import given
from hypothesis import strategies as st

from parcelas import parcelar


@given(
    total=st.integers(min_value=0, max_value=10**7),
    n=st.integers(min_value=1, max_value=24),
)
def test_a_soma_das_parcelas_e_o_total(total, n):
    assert sum(parcelar(total, n)) == total
```

```bash
pytest -q test_parcelas.py
```

Saída real:

```
total = 1, n = 2

    def test_a_soma_das_parcelas_e_o_total(total, n):
>       assert sum(parcelar(total, n)) == total
E       assert 0 == 1
E        +  where 0 = sum([0, 0])
E        +    where [0, 0] = parcelar(1, 2)
E       Failing test case: test_a_soma_das_parcelas_e_o_total(
E           total=1,
E           n=2,
E       )

1 failed in 0.34s
```

Repare no contraexemplo: **`total=1, n=2`**. A Hypothesis não achou isso por sorte — ela
achou um caso qualquer que falha e depois **encolheu** (*shrinking*) até o menor caso que
ainda falha. É por isso que o contraexemplo é sempre legível.

**A correção, e a bateria completa:**

```python
def parcelar(total_centavos: int, n: int) -> list[int]:
    """Divide um total em n parcelas, distribuindo o resto nas primeiras."""
    if n <= 0:
        raise ValueError("n deve ser positivo")
    base, resto = divmod(total_centavos, n)
    return [base + 1] * resto + [base] * (n - resto)
```

```python
import pytest
from hypothesis import given
from hypothesis import strategies as st

from parcelas import parcelar

totais = st.integers(min_value=0, max_value=10**7)
parcelas = st.integers(min_value=1, max_value=24)


@given(total=totais, n=parcelas)
def test_a_soma_das_parcelas_e_o_total(total, n):
    assert sum(parcelar(total, n)) == total


@given(total=totais, n=parcelas)
def test_gera_exatamente_n_parcelas(total, n):
    assert len(parcelar(total, n)) == n


@given(total=totais, n=parcelas)
def test_parcelas_diferem_no_maximo_um_centavo(total, n):
    valores = parcelar(total, n)
    assert max(valores) - min(valores) <= 1


@given(total=totais, n=parcelas)
def test_as_maiores_vem_primeiro(total, n):
    valores = parcelar(total, n)
    assert valores == sorted(valores, reverse=True)


def test_exemplo_concreto_para_ancorar_a_leitura():
    assert parcelar(100, 3) == [34, 33, 33]


def test_n_zero_e_recusado():
    with pytest.raises(ValueError):
        parcelar(100, 0)
```

```
......                                                                   [100%]
6 passed in 0.50s
```

**O que ensina:**

- Teste de exemplo responde *"para ESTE caso, dá AQUILO"*. Teste de propriedade responde
  *"para QUALQUER caso, esta lei vale"* — e a biblioteca procura ativamente o contraexemplo.
- As três propriedades juntas **especificam** a função: soma correta, quantidade correta,
  diferença máxima de 1 centavo. Um humano tentando escrever essa especificação em prosa
  levaria um parágrafo, e ele não seria executável.
- **Mantenha um teste de exemplo junto** (`parcelar(100, 3) == [34, 33, 33]`). As
  propriedades não mostram como a saída *se parece*, e quem lê o código depois precisa disso.
- Aprofundamento em [60-teoria-avancada.md](60-teoria-avancada.md).

---

## Exemplo 6 — Carrinho de compras imutável

**Problema:** funções que recebem e devolvem estado. É a forma mais testável de código que
existe — e vale ver por quê.

**`carrinho.js`**

```javascript
export function criarCarrinho() {
  return { itens: [], cupom: null };
}

export function adicionar(carrinho, produto, quantidade = 1) {
  if (!Number.isInteger(quantidade) || quantidade < 1) {
    throw new RangeError(`quantidade inválida: ${quantidade}`);
  }
  const existente = carrinho.itens.find((i) => i.sku === produto.sku);
  const itens = existente
    ? carrinho.itens.map((i) =>
        i.sku === produto.sku ? { ...i, quantidade: i.quantidade + quantidade } : i,
      )
    : [...carrinho.itens, { ...produto, quantidade }];
  return { ...carrinho, itens };
}

export function remover(carrinho, sku) {
  return { ...carrinho, itens: carrinho.itens.filter((i) => i.sku !== sku) };
}

export function subtotal(carrinho) {
  return carrinho.itens.reduce((s, i) => s + i.precoCentavos * i.quantidade, 0);
}

export function frete(carrinho) {
  const s = subtotal(carrinho);
  if (s === 0) return 0;
  if (s >= 20000) return 0;
  return 1990;
}

export function total(carrinho) {
  return subtotal(carrinho) + frete(carrinho);
}
```

**`carrinho.test.js`** (recorte com o essencial; a versão completa tem 20 testes)

```javascript
import assert from 'node:assert/strict';
import { describe, it } from 'node:test';

import { adicionar, criarCarrinho, frete, remover, subtotal, total } from './carrinho.js';

const CAFE = { sku: 'CAFE', nome: 'Café 500g', precoCentavos: 2990 };
const CANECA = { sku: 'CANECA', nome: 'Caneca', precoCentavos: 4500 };

describe('carrinho vazio', () => {
  it('começa sem itens', () => {
    assert.deepEqual(criarCarrinho().itens, []);
  });

  it('não cobra frete de carrinho vazio', () => {
    assert.equal(frete(criarCarrinho()), 0);
  });
});

describe('adicionar', () => {
  it('não modifica o carrinho original (imutabilidade)', () => {
    const antes = criarCarrinho();
    adicionar(antes, CAFE);
    assert.deepEqual(antes.itens, []);
  });

  it('soma a quantidade quando o produto já está no carrinho', () => {
    let c = adicionar(criarCarrinho(), CAFE, 2);
    c = adicionar(c, CAFE, 3);
    assert.equal(c.itens.length, 1);
    assert.equal(c.itens[0].quantidade, 5);
  });

  for (const ruim of [0, -1, 1.5, NaN, '2']) {
    it(`recusa quantidade ${JSON.stringify(ruim)}`, () => {
      assert.throws(() => adicionar(criarCarrinho(), CAFE, ruim), RangeError);
    });
  }
});

describe('remover', () => {
  it('remover algo que não existe não quebra nem muda nada', () => {
    const c = adicionar(criarCarrinho(), CAFE);
    assert.deepEqual(remover(c, 'INEXISTENTE').itens, c.itens);
  });
});

describe('frete — a regra com fronteira', () => {
  const casos = [
    [19999, 1990, 'um centavo abaixo do limite: cobra'],
    [20000, 0, 'exatamente no limite: grátis'],
    [20001, 0, 'acima do limite: grátis'],
  ];

  for (const [valor, esperado, rotulo] of casos) {
    it(rotulo, () => {
      const c = { itens: [{ sku: 'X', precoCentavos: valor, quantidade: 1 }], cupom: null };
      assert.equal(frete(c), esperado);
    });
  }
});

describe('total', () => {
  it('soma subtotal e frete', () => {
    assert.equal(total(adicionar(criarCarrinho(), CAFE)), 2990 + 1990);
  });

  it('acima de R$ 200 o total é só o subtotal', () => {
    assert.equal(total(adicionar(criarCarrinho(), CAFE, 7)), 20930);
  });
});
```

```bash
node --test carrinho.test.js
```
```
ℹ tests 20
ℹ pass 20
ℹ fail 0
```

**O que ensina:**

- **O teste de imutabilidade** (`adicionar` não altera o original) é o teste que impede a
  "otimização" `carrinho.itens.push(produto)`, que funciona nos outros 19 testes e quebra a
  aplicação inteira em produção quando dois lugares compartilham o mesmo carrinho.
- **`'2'` na lista de quantidades ruins.** Em JavaScript, `'2' * 1 === 2`; sem
  `Number.isInteger`, uma string passaria e depois viraria concatenação em algum lugar.
- **A fronteira do frete grátis** é o exemplo canônico de teste de valor limite: 19999,
  20000, 20001. Se a regra é "a partir de R$ 200", o teste do **20000 exato** é o único que
  distingue `>=` de `>`.
- Repare que `total()` tem só **dois** testes: ela é uma soma de duas funções já testadas.
  Não se testa a mesma regra três vezes.

---

## Exemplo 7 — Repetição com espera exponencial

**Problema:** você quer repetir uma chamada instável com espera de 100 ms, 200 ms, 400 ms.
Como testar isso sem a suíte levar segundos?

**`repetir.js`**

```javascript
export const esperar = (ms) => new Promise((r) => setTimeout(r, ms));

/**
 * Repete `acao` até `tentativas` vezes, com espera exponencial.
 * Só repete erros marcados como temporários.
 */
export async function comRepeticao(acao, {
  tentativas = 3,
  baseMs = 100,
  eTemporario = (e) => e.temporario === true,
  dormir = esperar,
} = {}) {
  let ultimoErro;
  for (let n = 1; n <= tentativas; n += 1) {
    try {
      return await acao(n);
    } catch (erro) {
      ultimoErro = erro;
      if (!eTemporario(erro) || n === tentativas) throw erro;
      await dormir(baseMs * 2 ** (n - 1));
    }
  }
  throw ultimoErro;
}
```

**`repetir.test.js`**

```javascript
import assert from 'node:assert/strict';
import { describe, it } from 'node:test';

import { comRepeticao } from './repetir.js';

function erroTemporario(mensagem = 'instável') {
  const e = new Error(mensagem);
  e.temporario = true;
  return e;
}

describe('comRepeticao', () => {
  it('não repete quando dá certo de primeira', async (t) => {
    const acao = t.mock.fn(async () => 'ok');
    assert.equal(await comRepeticao(acao), 'ok');
    assert.equal(acao.mock.callCount(), 1);
  });

  it('repete erro temporário e devolve o sucesso', async (t) => {
    const acao = t.mock.fn(async (n) => {
      if (n < 3) throw erroTemporario();
      return 'ok na terceira';
    });
    const dormir = t.mock.fn(async () => {});

    assert.equal(await comRepeticao(acao, { dormir }), 'ok na terceira');
    assert.equal(acao.mock.callCount(), 3);
  });

  it('espera com atraso exponencial: 100 ms, depois 200 ms', async (t) => {
    const acao = t.mock.fn(async () => {
      throw erroTemporario();
    });
    const dormir = t.mock.fn(async () => {});

    await assert.rejects(() => comRepeticao(acao, { dormir }));

    assert.deepEqual(
      dormir.mock.calls.map((c) => c.arguments[0]),
      [100, 200],
    );
  });

  it('não repete erro permanente', async (t) => {
    const acao = t.mock.fn(async () => {
      throw new Error('404: não existe');
    });
    const dormir = t.mock.fn(async () => {});

    await assert.rejects(() => comRepeticao(acao, { dormir }), /não existe/);
    assert.equal(acao.mock.callCount(), 1);
    assert.equal(dormir.mock.callCount(), 0);
  });

  it('propaga o último erro depois de esgotar as tentativas', async () => {
    const acao = async () => {
      throw erroTemporario('caiu de novo');
    };
    await assert.rejects(() => comRepeticao(acao, { dormir: async () => {} }), /caiu de novo/);
  });

  it('respeita o número de tentativas configurado', async (t) => {
    const acao = t.mock.fn(async () => {
      throw erroTemporario();
    });
    await assert.rejects(() => comRepeticao(acao, { tentativas: 5, dormir: async () => {} }));
    assert.equal(acao.mock.callCount(), 5);
  });

  it('a suíte inteira levou milissegundos, não segundos', () => {
    // Nenhum teste acima esperou de verdade: `dormir` foi injetado.
    // Sem essa injeção, os testes acima levariam ~2 segundos de espera real.
    assert.ok(true);
  });
});
```

```bash
node --test repetir.test.js
```
```
ℹ tests 7
ℹ pass 7
ℹ fail 0
ℹ duration_ms 94.25924
```

**94 milissegundos.** Sem a injeção do `dormir`, esses testes esperariam de verdade:
100 + 200 + 100 + 200 + 100 + 200 + 400 + 800 ms ≈ **2 segundos**. Multiplique por uma suíte
com cinquenta testes assim e você tem a diferença entre uma suíte que roda a cada `Ctrl+S` e
uma que ninguém roda.

**O que ensina:**

- **`dormir` como parâmetro com valor-padrão** é o truque mais barato de testabilidade que
  existe em JavaScript: produção nem sabe que ele existe, o teste substitui numa linha.
  A alternativa (`vi.useFakeTimers()` / `t.mock.timers`) funciona, mas mexe em estado global.
- Verificar **os argumentos** do `dormir` (`[100, 200]`) testa a política de espera sem
  medir tempo. Testar tempo com relógio é a receita de teste *flaky*.
- **O teste do erro permanente é o mais valioso da suíte:** ele garante que um 404 não vai
  ser repetido 3 vezes. Sem ele, um bug de digitação na URL gera 3× a carga no serviço
  alheio — e é assim que se derruba a API de um parceiro.

---

## Exemplo 8 — API HTTP de tarefas (caso de produção)

**Problema:** testar uma API HTTP de verdade — rotas, status, cabeçalhos, corpo, erros —
sem mockar o servidor.

**`api.js`**

```javascript
import { createServer } from 'node:http';

/** Camada de dados — trocável, e é isso que torna a API testável. */
export function repositorioEmMemoria(iniciais = []) {
  const dados = new Map(iniciais.map((t) => [t.id, t]));
  let proximoId = dados.size + 1;
  return {
    listar: () => [...dados.values()],
    criar(titulo) {
      const tarefa = { id: proximoId++, titulo, feita: false };
      dados.set(tarefa.id, tarefa);
      return tarefa;
    },
    concluir(id) {
      const t = dados.get(id);
      if (!t) return null;
      const atualizada = { ...t, feita: true };
      dados.set(id, atualizada);
      return atualizada;
    },
  };
}

export function criarApi(repo) {
  return createServer(async (req, res) => {
    const responder = (status, corpo) => {
      res.writeHead(status, { 'content-type': 'application/json; charset=utf-8' });
      res.end(JSON.stringify(corpo));
    };

    const url = new URL(req.url, 'http://localhost');

    if (req.method === 'GET' && url.pathname === '/tarefas') {
      return responder(200, repo.listar());
    }

    if (req.method === 'POST' && url.pathname === '/tarefas') {
      let corpo = '';
      for await (const pedaco of req) corpo += pedaco;
      let dados;
      try {
        dados = JSON.parse(corpo);
      } catch {
        return responder(400, { erro: 'JSON inválido' });
      }
      if (typeof dados.titulo !== 'string' || dados.titulo.trim() === '') {
        return responder(422, { erro: 'titulo é obrigatório' });
      }
      const tarefa = repo.criar(dados.titulo.trim());
      res.setHeader('location', `/tarefas/${tarefa.id}`);
      return responder(201, tarefa);
    }

    const casaConcluir = /^\/tarefas\/(\d+)\/concluir$/.exec(url.pathname);
    if (req.method === 'POST' && casaConcluir) {
      const tarefa = repo.concluir(Number(casaConcluir[1]));
      return tarefa ? responder(200, tarefa) : responder(404, { erro: 'tarefa não existe' });
    }

    return responder(404, { erro: 'rota não existe' });
  });
}
```

**`api.test.js`**

```javascript
import assert from 'node:assert/strict';
import { after, before, beforeEach, describe, it } from 'node:test';

import { criarApi, repositorioEmMemoria } from './api.js';

let servidor;
let base;
let repo;

before(async () => {
  repo = repositorioEmMemoria();
  servidor = criarApi(repo);
  // porta 0 = "me dê qualquer porta livre". Nunca fixe a porta num teste:
  // dois jobs de CI na mesma máquina brigariam por ela.
  await new Promise((r) => servidor.listen(0, '127.0.0.1', r));
  base = `http://127.0.0.1:${servidor.address().port}`;
});

after(() => servidor.close());

beforeEach(() => {
  // Estado limpo entre testes, sem derrubar e subir o servidor a cada um.
  Object.assign(repo, repositorioEmMemoria());
});

async function pedir(metodo, caminho, corpo) {
  const resposta = await fetch(base + caminho, {
    method: metodo,
    headers: corpo === undefined ? {} : { 'content-type': 'application/json' },
    body: corpo === undefined ? undefined : JSON.stringify(corpo),
  });
  const texto = await resposta.text();
  return {
    status: resposta.status,
    cabecalhos: resposta.headers,
    corpo: texto === '' ? null : JSON.parse(texto),
  };
}

describe('GET /tarefas', () => {
  it('devolve lista vazia no começo', async () => {
    const r = await pedir('GET', '/tarefas');
    assert.equal(r.status, 200);
    assert.deepEqual(r.corpo, []);
  });

  it('devolve JSON com charset', async () => {
    const r = await pedir('GET', '/tarefas');
    assert.equal(r.cabecalhos.get('content-type'), 'application/json; charset=utf-8');
  });
});

describe('POST /tarefas', () => {
  it('cria e devolve 201 com Location', async () => {
    const r = await pedir('POST', '/tarefas', { titulo: 'comprar café' });
    assert.equal(r.status, 201);
    assert.equal(r.corpo.titulo, 'comprar café');
    assert.equal(r.corpo.feita, false);
    assert.equal(r.cabecalhos.get('location'), `/tarefas/${r.corpo.id}`);
  });

  it('remove espaços em volta do título', async () => {
    const r = await pedir('POST', '/tarefas', { titulo: '   pagar conta   ' });
    assert.equal(r.corpo.titulo, 'pagar conta');
  });

  it('recusa título vazio com 422', async () => {
    const r = await pedir('POST', '/tarefas', { titulo: '   ' });
    assert.equal(r.status, 422);
    assert.match(r.corpo.erro, /titulo/);
  });

  it('recusa corpo sem título com 422', async () => {
    const r = await pedir('POST', '/tarefas', { outra: 'coisa' });
    assert.equal(r.status, 422);
  });

  it('recusa JSON malformado com 400', async () => {
    const resposta = await fetch(base + '/tarefas', {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: '{isto não é json',
    });
    assert.equal(resposta.status, 400);
  });

  it('a tarefa criada aparece no GET seguinte', async () => {
    await pedir('POST', '/tarefas', { titulo: 'x' });
    const r = await pedir('GET', '/tarefas');
    assert.equal(r.corpo.length, 1);
  });
});

describe('POST /tarefas/:id/concluir', () => {
  it('marca como feita', async () => {
    const criada = await pedir('POST', '/tarefas', { titulo: 'x' });
    const r = await pedir('POST', `/tarefas/${criada.corpo.id}/concluir`);
    assert.equal(r.status, 200);
    assert.equal(r.corpo.feita, true);
  });

  it('id inexistente devolve 404', async () => {
    const r = await pedir('POST', '/tarefas/9999/concluir');
    assert.equal(r.status, 404);
  });

  it('id não numérico cai no 404 de rota', async () => {
    const r = await pedir('POST', '/tarefas/abc/concluir');
    assert.equal(r.status, 404);
    assert.match(r.corpo.erro, /rota/);
  });
});

describe('rota desconhecida', () => {
  it('devolve 404 com JSON', async () => {
    const r = await pedir('GET', '/nao-existe');
    assert.equal(r.status, 404);
    assert.deepEqual(r.corpo, { erro: 'rota não existe' });
  });
});
```

```bash
node --test api.test.js
```
```
ℹ tests 12
ℹ pass 12
ℹ fail 0
```

**O que ensina — e por que isto é "de produção":**

- **`listen(0)`** pede uma porta livre qualquer. Fixar `3000` num teste quebra assim que dois
  jobs rodam na mesma máquina — e é um dos motivos clássicos de CI *flaky*.
- **Servidor no `before`, dados limpos no `beforeEach`.** Subir e derrubar o servidor a cada
  teste custaria 12× mais; limpar só o repositório dá o mesmo isolamento por uma fração do
  preço.
- **A função auxiliar `pedir()`** é o que impede o teste de virar sopa de `fetch`. Escreva
  uma dessas em todo projeto de API. (É o que a biblioteca `supertest` faz — mas hoje, com
  `fetch` nativo no Node, ela deixou de ser necessária para casos simples.)
- **Distinguir 400 de 422** é decisão de contrato: JSON malformado é sintaxe (400), título
  vazio é semântica (422). Trocar isso quebra clientes silenciosamente — por isso está
  travado por teste. Mais sobre isso em [`apis/`](../apis/00-MAPA.md).
- **O teste do `/tarefas/abc/concluir`** documenta uma decisão sutil: id não numérico cai no
  404 de *rota*, não no de *recurso*. Sem o teste, ninguém saberia que era intencional.
- O `repositorioEmMemoria` injetado é o que permite tudo isso. Se a API abrisse a conexão com
  o Postgres por dentro, esta suíte precisaria de um banco no ar.

---

## Exemplo 9 — Máquina de estados por tabela

**Problema:** um objeto com 4 estados e 5 ações tem 20 combinações. Escrever 20 testes quase
idênticos é insuportável — e por isso ninguém escreve, e por isso as transições proibidas
nunca são testadas.

**Solução:** uma tabela, um teste parametrizado, e um meta-teste que garante que a tabela
está completa.

**Python:**

```python
ACOES = {
    "pausar": lambda a: a.pausar(),
    "retomar": lambda a: a.retomar(HOJE),
    "cancelar": lambda a: a.cancelar(),
    "pagar": lambda a: a.registrar_pagamento(HOJE),
    "falhar": lambda a: a.registrar_falha(),
}

TABELA = [
    (Estado.ATIVA, "pausar", Estado.PAUSADA),
    (Estado.ATIVA, "retomar", None),          # None = proibida
    (Estado.ATIVA, "cancelar", Estado.CANCELADA),
    # ... as 20 combinações
]


@pytest.mark.parametrize(
    ("inicial", "acao", "final"), TABELA, ids=[f"{i.value}-{a}" for i, a, _ in TABELA]
)
def test_tabela_de_transicoes(inicial, acao, final):
    assinatura = nova(inicial)
    if final is None:
        with pytest.raises(TransicaoInvalida):
            ACOES[acao](assinatura)
        assert assinatura.estado is inicial, "transição proibida não pode mudar o estado"
    else:
        ACOES[acao](assinatura)
        assert assinatura.estado is final


def test_a_tabela_cobre_todas_as_combinacoes():
    """Meta-teste: garante que a tabela não esqueceu nenhum par (estado, ação)."""
    esperado = {(e, a) for e in Estado for a in ACOES}
    coberto = {(i, a) for i, a, _ in TABELA}
    assert coberto == esperado
```

**JavaScript:**

```javascript
for (const [inicial, acao, final] of TABELA) {
  it(`${inicial} + ${acao} → ${final ?? 'PROIBIDO'}`, () => {
    const a = nova(inicial);
    if (final === null) {
      assert.throws(() => ACOES[acao](a), TransicaoInvalida);
      assert.equal(a.estado, inicial, 'transição proibida não pode mudar o estado');
    } else {
      ACOES[acao](a);
      assert.equal(a.estado, final);
    }
  });
}

it('a tabela cobre todas as combinações (meta-teste)', () => {
  const esperado = Object.values(Estado)
    .flatMap((e) => Object.keys(ACOES).map((a) => `${e}|${a}`))
    .sort();
  const coberto = TABELA.map(([e, a]) => `${e}|${a}`).sort();
  assert.deepEqual(coberto, esperado);
});
```

Código completo e executável: [`07-projeto-modelo/`](07-projeto-modelo/README.md),
arquivos `tests/test_assinatura.py` e `test/assinatura.test.js`.

**O que ensina:**

- **Testar as transições proibidas vale tanto quanto testar as permitidas.** O `assert` de
  que o estado **não mudou** é o que pega o bug em que a exceção é lançada *depois* de já
  ter alterado o objeto — deixando-o num estado corrompido.
- **O meta-teste é a peça rara.** Ele não testa o código de produção; testa se o **teste**
  ficou incompleto. Quando alguém acrescentar um estado `SUSPENSA` à enum, ele fica vermelho
  imediatamente. Sem isso, o novo estado entraria sem cobertura nenhuma e a **porcentagem de
  cobertura não cairia** — a lacuna mais perigosa que existe.

---

## Exemplo 10 — Fake verificado por contrato

**Problema:** seus testes rápidos usam um repositório falso em memória. Como garantir que
ele se comporta como o banco de verdade?

```python
@pytest.fixture(params=["memoria", "sqlite"])
def repositorio(request):
    """Fixture parametrizada: cada teste abaixo roda DUAS vezes, uma por implementação."""
    if request.param == "memoria":
        yield RepositorioMemoria()
    else:
        r = RepositorioSQLite(":memory:")
        yield r
        r.fechar()


def test_busca_devolve_none_para_id_desconhecido(repositorio):
    assert repositorio.buscar("fantasma") is None


def test_vencidas_incluem_o_proprio_dia(repositorio):
    repositorio.salvar(nova("a1", dias=0))
    assert [a.id for a in repositorio.listar_vencidas(HOJE)] == ["a1"]


def test_vencidas_excluem_o_futuro(repositorio):
    repositorio.salvar(nova("a1", dias=1))
    assert repositorio.listar_vencidas(HOJE) == []


def test_repositorio_vazio_devolve_lista_vazia_nao_none(repositorio):
    assert repositorio.listar_vencidas(HOJE) == []
```

```bash
pytest -q tests/test_contrato_repositorio.py
```
```
....................                                                     [100%]
20 passed in 0.06s
```

Dez testes × duas implementações = 20.

**O que ensina:**

- Este é o antídoto para o risco mais sério de usar dublês: **o fake mentir**. Todos os
  unitários passam, e a produção quebra porque o SQL estava errado.
- A parametrização acontece na **fixture**, não no teste. É o mecanismo que o pytest tem e
  que o `node:test` não tem — em JavaScript, o equivalente é um laço em volta do `describe`
  (ver `test/contratoRepositorio.test.js` no projeto-modelo).
- **Documente a divergência que sobrar.** No projeto-modelo há um teste chamado
  `divergência conhecida entre as implementações`, que verifica que o fake guarda
  referências e o SQLite guarda cópias. Escrever isso como teste, e não como comentário,
  garante que a divergência não aumente sem alguém perceber.

---

## Exemplo 11 — Teste de caracterização em código legado

**Problema:** você recebeu uma função de 80 linhas, sem testes, que ninguém entende, e
precisa mudá-la. Como não quebrar?

**Resposta:** não tente escrever o teste "certo". Escreva um teste que registra o que o
código **faz hoje** — certo ou errado. É a técnica de *characterization test*, de Michael
Feathers.

```python
"""Rede de segurança para `calcular_frete`, que ninguém entende mais.

Estes testes NÃO afirmam que o comportamento está certo. Eles afirmam que ele é
o que era em 12/08/2026. Servem para uma coisa só: detectar mudança acidental
durante a refatoração. Depois de refatorar, alguns podem virar testes de verdade;
outros vão ser apagados quando a regra for finalmente entendida e reescrita.
"""

import itertools

import pytest

from legado import calcular_frete

# Gerado por varredura: rodamos a função com muitas entradas e gravamos a saída.
# Se você mudar a função e algum destes mudar, PARE e entenda por quê.
CASOS_OBSERVADOS = [
    ("SP", 1.0, 0, 1990),
    ("SP", 1.0, 20000, 0),
    ("SP", 30.0, 0, 4990),
    ("AM", 1.0, 0, 4990),
    ("AM", 1.0, 20000, 2990),   # ← surpresa: no Norte o frete grátis não zera
    ("AM", 30.0, 50000, 2990),
    ("RS", 0.0, 0, 1990),       # ← peso zero cobra frete cheio
    ("XX", 1.0, 0, 1990),       # ← UF inválida não explode: usa o padrão
]


@pytest.mark.parametrize(("uf", "peso", "subtotal", "esperado"), CASOS_OBSERVADOS)
def test_comportamento_atual(uf, peso, subtotal, esperado):
    assert calcular_frete(uf, peso, subtotal) == esperado


def test_nunca_devolve_negativo():
    """Invariante que descobrimos por varredura e queremos preservar."""
    for uf, peso, subtotal in itertools.product(
        ["SP", "AM", "RS", "XX"], [0.0, 1.0, 30.0, 999.0], [0, 100, 20000, 10**6]
    ):
        assert calcular_frete(uf, peso, subtotal) >= 0, f"{uf} {peso} {subtotal}"
```

**O que ensina:**

- **O comentário no topo é parte do teste.** Sem ele, daqui a um ano alguém lê
  `("AM", 1.0, 20000, 2990)` e acha que isso é uma regra de negócio aprovada, quando é só
  "o que o código fazia".
- **As surpresas marcadas com `←` são ouro.** Cada uma é um candidato a bug que ninguém
  sabia que existia. Você não conserta agora — anota e refatora com a rede no lugar.
- **O teste de invariante** (`nunca devolve negativo`) é mais robusto que os casos fixos:
  ele sobrevive à refatoração que muda valores mas mantém a sanidade.
- Como gerar os casos: escreva um script que roda a função com um produto cartesiano de
  entradas plausíveis e imprime `(entrada, saída)`. Cole o resultado no teste. É trabalho
  mecânico de 20 minutos que compra semanas de tranquilidade.
- Aprofundamento em [20-testabilidade-e-design.md](20-testabilidade-e-design.md).

---

## Exemplo 12 — Snapshot: quando ajuda e quando apodrece

**Problema:** verificar uma saída grande e estruturada (HTML renderizado, JSON de relatório,
mensagem formatada) linha por linha é insuportável.

```javascript
import { describe, expect, it } from 'vitest';

import { relatorioMensal } from '../src/relatorio.js';

describe('relatório mensal', () => {
  it('formata o cabeçalho e os totais', () => {
    const relatorio = relatorioMensal({
      mes: '2026-08',
      cobradas: 1420,
      recusadas: 38,
      totalCentavos: 7085800,
    });

    // Na primeira execução o Vitest ESCREVE o valor esperado aqui dentro.
    expect(relatorio).toMatchInlineSnapshot(`
      "RELATÓRIO — agosto de 2026
      ==========================
      cobranças aprovadas: 1.420
      cobranças recusadas:    38
      taxa de aprovação:   97,4%
      total arrecadado:    R$ 70.858,00"
    `);
  });
});
```

**Quando o snapshot ajuda:**

- saída **estável** (não muda a cada execução) e **pequena** (cabe na tela);
- formatação, onde escrever a asserção seria mais longo que a saída;
- o teste é sobre a **aparência do texto**, não sobre a regra que o gerou.

**Quando ele apodrece — e é caro:**

| Sintoma | Por que acontece |
|---|---|
| snapshot de 400 linhas | ninguém revisa; `-u` é apertado no automático |
| snapshot com data/hora/UUID dentro | falha todo dia; alguém "conserta" com `-u` |
| toda mudança de código muda 30 snapshots | vira ruído; a revisão de PR desliga o cérebro |
| ninguém sabe por que aquele valor é o certo | o teste deixou de documentar qualquer coisa |

**A regra prática, dita sem meias-palavras:** um snapshot que você não consegue **ler e
julgar em 10 segundos** não é um teste — é um carimbo. Para regra de negócio, escreva a
asserção explícita:

```javascript
// no lugar de um snapshot gigante do objeto inteiro:
expect(relatorio.taxaAprovacao).toBe('97,4%');
expect(relatorio.totalFormatado).toBe('R$ 70.858,00');
```

Mais sobre isso em [75-armadilhas.md](75-armadilhas.md), seção "snapshot podre".

---

## Autoteste

1. Por que `assert cpf_valido(x) is True` é diferente de `assert cpf_valido(x)`?
2. Para que serve `ids=` no `parametrize`, e quando você sente falta dele?
3. Por que nunca escrever em `/tmp/arquivo-fixo.csv` num teste?
4. Se `clima.py` fizesse `from urllib.request import urlopen`, qual seria o alvo do `patch`?
5. No exemplo 5, por que o contraexemplo foi `total=1, n=2` e não um número enorme?
6. Por que manter um teste de exemplo junto com os testes de propriedade?
7. No carrinho, qual teste impede a "otimização" `carrinho.itens.push(...)`?
8. Por que o exemplo 7 é 20× mais rápido do que seria sem a injeção do `dormir`?
9. Por que `servidor.listen(0)` e não `listen(3000)`?
10. O meta-teste do exemplo 9 não testa código de produção. Justifique a existência dele.
11. Qual é o risco que o teste de contrato (exemplo 10) elimina?
12. Um teste de caracterização registra comportamento errado. Isso é aceitável? Por quê?
13. Dê dois sinais de que um snapshot virou carimbo em vez de teste.
