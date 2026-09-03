# 30 · Testes

> **Nível:** avançado · **Escrito em:** 02/09/2026 · Streamlit 1.63.0
> Os comportamentos descritos aqui foram **exercitados** contra a 1.63.0 em
> 02/09/2026 — inclusive um defeito encontrado no caminho (seção 7).

"Não dá para testar Streamlit" era verdade até outubro de 2023. Desde a versão
1.28 existe `st.testing.v1.AppTest`, que roda a app **sem navegador**.

---

## 1. A pirâmide de testes de uma app Streamlit

```
        ╱╲        Playwright — poucos, lentos, frágeis
       ╱  ╲       (só o caminho crítico, se houver componente customizado)
      ╱────╲
     ╱      ╲     AppTest — dezenas, rápidos
    ╱        ╲    (a interface: caminhos, permissões, estados)
   ╱──────────╲
  ╱            ╲  pytest puro — centenas, instantâneos
 ╱______________╲ (as REGRAS, em nucleo/, sem streamlit)
```

**A base é a maior de propósito.** O `nucleo/` do
[projeto-modelo](07-projeto-modelo/) tem 27 testes que rodam em menos de um
segundo; a interface tem 16 com `AppTest`; e não há nenhum Playwright — porque
não há componente customizado.

**É a separação de camadas ([23](23-arquitetura-de-app-real.md)) que torna a base
possível.** Se a regra de negócio está dentro de um `with st.form`, ela só é
testável pela camada do meio, que é 100× mais lenta.

---

## 2. A base: testar o núcleo, sem Streamlit

```python
# testes/test_servicos.py
from datetime import date, timedelta
import pytest
from nucleo import servicos

def test_cancelado_nao_entra_na_receita(cfg):
    hoje = date.today()
    df = servicos.carregar_pedidos(cfg.caminho_banco, hoje - timedelta(days=365), hoje)
    k = servicos.calcular_kpis(df, df.iloc[0:0])
    assert k.receita_centavos == int(df[df.status != "cancelado"].valor_centavos.sum())

def test_variacao_sem_base_e_none(cfg):
    vazio = servicos.carregar_pedidos(cfg.caminho_banco, date(1990,1,1), date(1990,1,2))
    assert servicos.calcular_kpis(vazio, vazio).var_receita is None
```

**O que testar aqui** — e é onde mora quase todo bug que importa:

- as **regras de negócio** ("cancelado não conta como receita");
- os **casos de borda**: período vazio, divisão por zero, valor negativo;
- a **validação**;
- as **defesas**: injeção de SQL, coluna fora da lista branca, papel insuficiente;
- as **conversões**: centavos, fuso horário, formatação de moeda;
- as **transações**: falha no meio desfaz tudo.

Fixtures com banco temporário por teste:

```python
@pytest.fixture()
def banco(tmp_path):
    caminho = tmp_path / "teste.db"
    seed.popular(caminho, dias=120, pedidos=300, iteracoes_hash=100_000, semente=7)
    return caminho
```

Três detalhes: `tmp_path` (banco novo por teste — testes que compartilham banco
falham em ordem aleatória), `semente=7` (dados determinísticos) e
`iteracoes_hash=100_000` (custo de hash baixo: teste não é produção).

---

## 3. O meio: `AppTest`

```python
from streamlit.testing.v1 import AppTest

at = AppTest.from_file("app.py", default_timeout=30)
at.run()

assert not at.exception
assert at.title[0].value == "Painel"
```

Três formas de criar:

```python
AppTest.from_file("app.py")          # a app real — o que você quer em CI
AppTest.from_string("import streamlit as st\nst.write('oi')")
AppTest.from_function(minha_funcao)  # uma página definida como função
```

> **Pegadinha do `from_function`:** ele reexecuta o **código-fonte** da função num
> script novo. Nomes do módulo de teste **não** estão visíveis lá dentro; todo
> import precisa estar dentro da própria função. Verificado na 1.63.0.

### Interagir

```python
at.text_input[0].set_value("admin@exemplo.com")
at.text_input(key="senha").set_value("segredo")
at.button[0].click().run()
at.selectbox(key="uf").set_value("RJ").run()
at.multiselect(key="status").set_value(["faturado"]).run()
at.slider(key="n").set_value(50).run()
at.checkbox(key="c").check().run()
at.number_input(key="q").set_value(3).run()
at.chat_input[0].set_value("olá").run()
at.switch_page("paginas/pedidos.py").run()
```

Cada `.run()` é um rerun. `at.session_state` pode ser lido e escrito antes do
`run()` — é como você "loga" alguém sem passar pela tela de login:

```python
at.session_state["usuario"] = Usuario(1, "a@e.com", "Ana", "admin")
at.run()
```

### Inspecionar

```python
at.exception            # lista — se não estiver vazia, o script quebrou
at.error, at.warning, at.info, at.success
at.markdown, at.title, at.header, at.caption
at.metric, at.dataframe, at.table
at.button, at.selectbox, at.text_input, at.multiselect
at.tabs, at.expander, at.columns, at.sidebar
at.get("download_button")     # por nome, para tipos sem atalho
```

`at.sidebar` filtra pela barra lateral: `at.sidebar.button[0]`.

---

## 4. O que testar com `AppTest`

Os testes que efetivamente pegam bug, por ordem de retorno:

```python
def test_todas_as_paginas_carregam(app):
    """O teste mais barato e o que mais pega. Rode para TODAS as páginas."""
    for pagina in ["paginas/painel.py", "paginas/pedidos.py", "paginas/admin.py"]:
        app.switch_page(pagina).run()
        assert not app.exception, f"{pagina}: {app.exception}"

def test_periodo_sem_dados_nao_quebra(app):
    """O caminho que mais derruba painel: o filtro que não devolve nada."""
    app.multiselect(key="f_segmento").set_value(["Governo"]).run()
    assert not app.exception
    assert app.info                                # avisou, não estourou

def test_leitor_nao_pode_criar(app):
    app.session_state["usuario"] = Usuario(1, "l@e.com", "L", "leitor")
    app.switch_page("paginas/pedidos.py").run()
    botao = [b for b in app.button if b.label == "Novo pedido"][0]
    assert botao.disabled

def test_login_errado_mostra_erro(app):
    app.run()
    app.text_input[0].set_value("admin@exemplo.com")
    app.text_input[1].set_value("errada")
    app.button[0].click().run()
    assert "incorretos" in app.error[0].value
    assert "usuario" not in app.session_state
```

**Os quatro tipos que valem sempre:**

1. **"todas as páginas carregam"** — barato, e pega import quebrado, erro de
   digitação, mudança de API;
2. **estados vazios** — o caminho mais esquecido e o que mais quebra;
3. **permissões** — cada papel, cada página restrita;
4. **fluxos de escrita** — criar, editar, excluir, com verificação no banco.

---

## 5. Configurar o ambiente do teste

```python
@pytest.fixture()
def app(tmp_path, monkeypatch):
    caminho = tmp_path / "app.db"
    seed.popular(caminho, dias=120, pedidos=300, iteracoes_hash=100_000, semente=7)
    monkeypatch.setenv("PAINEL_BANCO", str(caminho))
    return AppTest.from_file("app.py", default_timeout=60)
```

Segredos, quando a app usa `st.secrets`:

```python
at.secrets["banco"] = {"url": "sqlite:///:memory:"}
at.query_params["uf"] = "SP"
```

**`default_timeout`:** o padrão é 3 segundos. Uma app que popula banco ou carrega
modelo na primeira execução estoura isso e o erro (`timeout`) não sugere a causa.
Aumente.

---

## 6. O que `AppTest` **não** faz

Seja realista sobre o que este teste cobre:

- **não renderiza CSS nem layout** — um painel visualmente quebrado passa;
- **não executa JavaScript** — componente customizado não é exercitado;
- **não testa o servidor de verdade** — WebSocket, upload, proxy ficam de fora;
- **não simula o navegador** — nada de responsividade, foco, teclado.

Para isso, Playwright. **Minha recomendação:** só se você tem componente
customizado ou um fluxo visual crítico. Para painel interno, o custo de manter
teste de navegador raramente se paga.

---

## 7. Limitações reais encontradas (1.63.0, 02/09/2026)

Escrevendo os testes do projeto-modelo, encontrei e isolei um defeito:

> **`AppTest.date_input(...).set_value()` não tem efeito.** O estado do widget é
> gerado corretamente (as datas certas chegam a `_widget_state`), mas o script
> continua lendo o valor anterior. Reproduzido com e sem `key`, com e sem
> `value=`, em intervalo e em data única.
>
> **`text_input`, `number_input`, `slider`, `time_input`, `multiselect`,
> `selectbox` e `segmented_control` funcionam normalmente** — testados no mesmo
> script.

**Contorno:** conduza o teste por outro widget. No projeto-modelo, o teste de
estado vazio filtra por um segmento que a fixture esvaziou, em vez de mexer no
período.

**Lição geral:** ao escrever um teste que "não deveria falhar", verifique se o
harness está mesmo aplicando o que você pediu:

```python
at.multiselect(key="f").set_value(["x"]).run()
assert at.session_state["f"] == ["x"]      # confirme que pegou
```

---

## 8. Testar desempenho

```python
import time

def test_painel_carrega_em_menos_de_5s(app):
    inicio = time.perf_counter()
    app.run()
    assert time.perf_counter() - inicio < 5.0
    assert not app.exception
```

Grosseiro, e ainda assim útil: pega a regressão do dia em que alguém tira um
`@st.cache_data` "para simplificar".

---

## 9. CI

```yaml
name: ci
on: [push, pull_request]
jobs:
  testar:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v5
      - run: uv sync --frozen
      - run: uv run ruff check .
      - run: uv run pytest -q --maxfail=3
```

Sem navegador, sem serviço externo, sem Docker. É o que torna testar Streamlit
barato — e é o motivo de não haver desculpa para não testar.

---

## 10. Checklist

- [ ] Regras de negócio testadas **sem** Streamlit.
- [ ] Um teste "carrega sem exceção" para cada página.
- [ ] Estado vazio testado em cada tela com filtro.
- [ ] Cada papel testado contra cada página restrita.
- [ ] Fluxos de escrita testados, com verificação no banco.
- [ ] Fixture com banco temporário por teste.
- [ ] Dados de teste determinísticos (semente fixa).
- [ ] `default_timeout` suficiente.
- [ ] CI rodando em todo push.

---

## Autoteste

1. Desenhe a pirâmide de testes e diga o que vai em cada nível.
2. Por que a separação de camadas é pré-requisito para a base da pirâmide?
3. Quais são as três formas de criar um `AppTest`? Qual é a pegadinha do
   `from_function`?
4. Cite os quatro tipos de teste de `AppTest` que valem sempre.
5. O que `AppTest` **não** cobre? Quando vale Playwright?
6. Por que `default_timeout` costuma precisar de ajuste?
7. Que defeito da 1.63.0 este curso encontrou, e como ele foi contornado?
8. Por que dados de teste devem ser determinísticos?
