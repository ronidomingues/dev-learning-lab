# 04 · Como começar — do ambiente pronto a um painel na tela

> **Nível:** iniciante · **Escrito em:** 02/09/2026 · Streamlit 1.63.0
> Assume o ambiente do [03-instalacao.md](03-instalacao.md) já funcionando.
> Se `streamlit hello` não abriu, volte lá. Não improvise.

Em uma hora você sai do arquivo vazio para um painel com filtro, indicadores e
gráfico. E, mais importante, você vai entender **por que** cada coisa funciona
como funciona.

---

## 1. O menor programa que já é uma tela

```bash
mkdir -p ~/projetos/primeiro-painel && cd ~/projetos/primeiro-painel
```

Crie `app.py`:

```python
import streamlit as st

st.title("Meu primeiro painel")
st.write("Se você está lendo isto no navegador, funcionou.")
```

```bash
streamlit run app.py
```

**Verificação — é isto que tem de aparecer no terminal:**

```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.0.10:8501
```

E no navegador: um título grande "Meu primeiro painel" e uma linha de texto
abaixo. Se abriu, pare um segundo: você acabou de subir um servidor web,
com WebSocket, em duas linhas de Python.

> Se o navegador não abriu sozinho, abra `http://localhost:8501` à mão. Normal em
> WSL2, servidor sem interface gráfica e contêiner.

---

## 2. O ciclo de trabalho — e é aqui que o Streamlit ganha

Deixe o servidor rodando. **Não pare, não reinicie.** Acrescente uma linha ao
`app.py` e salve:

```python
import streamlit as st

st.title("Meu primeiro painel")
st.write("Se você está lendo isto no navegador, funcionou.")
st.write("E isto apareceu sem eu reiniciar nada.")   # <- nova
```

A página se atualiza **sozinha**, em menos de um segundo.

No canto superior direito há um menu (⋮) com **Settings → Run on save**. Deixe
ligado. É o ciclo mais curto que existe em programação de interface:

```
editar  →  salvar  →  olhar  →  editar  →  ...
```

Nada de compilar, nada de F5, nada de reiniciar servidor.

**Quando você PRECISA reiniciar** (`Ctrl+C` e `streamlit run` de novo):

| Situação | Por quê |
|---|---|
| mudou `.streamlit/config.toml` (seção `[server]`) | configuração de servidor é lida na partida |
| instalou uma biblioteca nova | o processo já tinha carregado o ambiente antigo |
| mudou a definição de uma classe que está no `session_state` | o objeto guardado é da classe velha; dá `isinstance` falso e erro estranho |
| o app travou de vez | acontece |

---

## 3. O primeiro controle — e o momento de entender o rerun

```python
import streamlit as st

st.title("Conversor")

celsius = st.slider("Temperatura em Celsius", -50, 50, 25)
st.write("Em Fahrenheit:", celsius * 9 / 5 + 32)
```

Arraste o controle. O número muda. Agora **prove para si mesmo** o que está
acontecendo:

```python
import streamlit as st
from datetime import datetime

st.title("Conversor")
st.caption(f"Este script rodou às {datetime.now():%H:%M:%S.%f}")   # <- prova

celsius = st.slider("Temperatura em Celsius", -50, 50, 25)
st.write("Em Fahrenheit:", celsius * 9 / 5 + 32)
```

Arraste o controle e olhe o horário: **ele muda a cada movimento**. O script
inteiro rodou de novo. Toda vez.

Isso é o modelo inteiro do Streamlit em uma linha de prova. Guarde:

> **A cada interação, o script roda do começo ao fim. O widget devolve o valor
> atual em vez do valor inicial.**

E daí saem, em cascata, todas as outras peças:

- se o script roda todo de novo, **variável comum não sobrevive** → `st.session_state`;
- se o script roda todo de novo, **conta cara é refeita** → `st.cache_data`;
- se o script roda todo de novo, **a tela pisca inteira** → `st.fragment`.

Nenhuma dessas três é enfeite. Cada uma existe para pagar o preço da escolha
original. É por isso que
[12-modelo-de-execucao-e-rerun.md](12-modelo-de-execucao-e-rerun.md) é o
arquivo mais importante do curso.

---

## 4. Dados na tela

Sem CSV à mão, gere um:

```python
import numpy as np
import pandas as pd
import streamlit as st

st.title("Vendas")

# Dados fictícios, mas com semente fixa: o resultado é sempre o mesmo.
rng = np.random.default_rng(42)
dados = pd.DataFrame({
    "data": pd.date_range("2026-01-01", periods=180, freq="D"),
    "regiao": rng.choice(["Norte", "Sul", "Leste", "Oeste"], 180),
    "valor": rng.integers(500, 5000, 180),
})

st.dataframe(dados, hide_index=True)
st.line_chart(dados, x="data", y="valor")
```

**Verificação:** uma tabela rolável com 180 linhas e, abaixo, um gráfico de linha.
A tabela já vem com ordenação por clique no cabeçalho, busca e botão de download
— de graça, sem configurar nada.

---

## 5. Filtro: o primeiro app de verdade

```python
import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Vendas", page_icon="📊", layout="wide")
st.title("Vendas por região")

rng = np.random.default_rng(42)
dados = pd.DataFrame({
    "data": pd.date_range("2026-01-01", periods=180, freq="D"),
    "regiao": rng.choice(["Norte", "Sul", "Leste", "Oeste"], 180),
    "valor": rng.integers(500, 5000, 180),
})

# --- filtros, na barra lateral ---
with st.sidebar:
    st.header("Filtros")
    regioes = st.multiselect("Região", sorted(dados["regiao"].unique()))
    minimo = st.slider("Valor mínimo", 0, 5000, 0, step=100)

# --- aplicação do filtro ---
filtrado = dados[dados["valor"] >= minimo]
if regioes:                      # lista vazia = sem restrição
    filtrado = filtrado[filtrado["regiao"].isin(regioes)]

# --- indicadores ---
c1, c2, c3 = st.columns(3)
c1.metric("Total", f"R$ {filtrado['valor'].sum():,.0f}".replace(",", "."), border=True)
c2.metric("Vendas", len(filtrado), border=True)
c3.metric("Média", f"R$ {filtrado['valor'].mean():,.0f}".replace(",", ".")
          if len(filtrado) else "—", border=True)

# --- gráfico e tabela ---
if filtrado.empty:
    st.info("Nenhuma venda com esses filtros.")
else:
    st.bar_chart(filtrado.groupby("regiao")["valor"].sum())
    st.dataframe(filtrado, hide_index=True, height=300)
```

**Verificação:** barra lateral com dois filtros; três cartões no topo; um gráfico
de barras; uma tabela. Mexa nos filtros — tudo acompanha.

Repare em quatro decisões que já são "de gente grande":

1. `layout="wide"` — painel quer largura.
2. Filtro na **barra lateral**, resultado no corpo. Nunca misture.
3. **Estado vazio tratado** (`if filtrado.empty`). Sem isso, `mean()` de uma série
   vazia devolve `NaN` e o cartão mostra `nan`.
4. Lista de filtro vazia significa "sem restrição", **não** "nada selecionado".
   É uma decisão; o importante é ser consistente e escrever isso em algum lugar.

---

## 6. `set_page_config` — a linha que precisa vir primeiro

```python
st.set_page_config(
    page_title="Vendas",          # título da aba do navegador
    page_icon="📊",               # emoji, URL de imagem ou ":material/nome:"
    layout="wide",                # "centered" (padrão) ou "wide"
    initial_sidebar_state="expanded",
)
```

**Tem de ser o primeiro comando `st.*` do script.** Se houver qualquer outro
antes — até um `st.write` de depuração — você recebe:

```
StreamlitSetPageConfigMustBeFirstCommandError
```

Regra prática: `import`s, depois `set_page_config`, depois o resto. Se você
precisa importar módulos que chamam `st.*` na importação, importe-os **depois**
do `set_page_config` (o [projeto-modelo](07-projeto-modelo/app.py) faz exatamente
isso, com um comentário explicando).

---

## 7. Cache: a primeira otimização, e a que mais rende

Troque a geração de dados por uma leitura "cara" e veja o problema:

```python
import time
import pandas as pd
import streamlit as st

def carregar():
    time.sleep(3)                      # finge um banco lento
    return pd.read_csv("vendas.csv")

dados = carregar()                     # 3 segundos A CADA INTERAÇÃO
st.slider("mexa aqui", 0, 100)
st.dataframe(dados)
```

Cada movimento do controle custa 3 segundos. Agora acrescente **uma linha**:

```python
@st.cache_data(ttl=300)                # <- só isto
def carregar():
    time.sleep(3)
    return pd.read_csv("vendas.csv")
```

Primeira execução: 3 segundos. Todas as seguintes: instantâneas, por 5 minutos.

**A regra de bolso, e ela resolve quase tudo:**

| Você quer guardar... | Use | Por quê |
|---|---|---|
| **dados** (DataFrame, lista, dicionário, número) | `@st.cache_data` | guarda uma **cópia** por combinação de argumentos; é seguro entre sessões |
| **conexão, cliente de API, modelo carregado** | `@st.cache_resource` | guarda **o próprio objeto**, compartilhado por todo mundo; não serializa |

Trocar os dois é o erro de cache mais comum. `cache_data` numa conexão de banco
tenta serializar a conexão e falha (ou pior: entrega uma conexão morta).
`cache_resource` num DataFrame entrega **o mesmo objeto** para todas as sessões —
e se alguém modificar, modificou para todo mundo.

Detalhe completo, incluindo `hash_funcs`, `refresh_mode="background"` e como
invalidar: [14-cache-e-dados.md](14-cache-e-dados.md).

---

## 8. Estado: quando a variável comum não basta

Este código **não funciona**, e vale a pena ver por quê:

```python
import streamlit as st

contador = 0                          # ← recriada a cada rerun
if st.button("Somar 1"):
    contador += 1
st.write(contador)                    # sempre 0 ou 1. Nunca 2.
```

O script roda inteiro de novo, então `contador = 0` executa de novo. Sempre.

A solução é a caixinha que sobrevive ao rerun:

```python
import streamlit as st

if "contador" not in st.session_state:     # inicializa UMA vez
    st.session_state.contador = 0

if st.button("Somar 1"):
    st.session_state.contador += 1

st.write(st.session_state.contador)        # 0, 1, 2, 3...
```

`st.session_state` é um dicionário por **aba do navegador**. Duas abas = dois
estados independentes. Fechou a aba, perdeu. Reiniciou o servidor, todo mundo
perdeu.

Detalhe completo — inclusive as regras de quem pode escrever na chave de um
widget, e por que atribuir a ela no corpo do script levanta exceção:
[13-session-state-e-widgets.md](13-session-state-e-widgets.md).

---

## 9. Os cinco primeiros erros de **uso** (não de instalação)

Instalação está no [03](03-instalacao.md). Estes são os do dia 1 de código.

### 9.1 "O botão não faz nada na segunda vez"

```python
if st.button("Mostrar"):
    st.write("apareceu")          # some no próximo clique em qualquer outra coisa
```

**Causa:** `st.button` devolve `True` **só no rerun causado pelo próprio clique**.
No rerun seguinte, volta a `False`, e o `if` não entra.

**Correção:** guarde a decisão no estado.

```python
if st.button("Mostrar"):
    st.session_state.mostrar = True
if st.session_state.get("mostrar"):
    st.write("apareceu")
```

### 9.2 "Meu app está lento e pisca inteiro"

**Causa:** conta cara sem cache, ou dado grande sendo relido a cada rerun.

**Correção:** `@st.cache_data` na função de carga; filtre **no banco**, não em
Python; use `@st.fragment` no bloco que tem controles próprios.

### 9.3 `DuplicateWidgetID` / `StreamlitDuplicateElementKey`

```python
st.text_input("Nome")
st.text_input("Nome")      # explode
```

**Causa:** o Streamlit identifica o widget por tipo + parâmetros. Dois idênticos
colidem.

**Correção:** `key=` distinta em cada um.

```python
st.text_input("Nome", key="nome_pf")
st.text_input("Nome", key="nome_pj")
```

### 9.4 "Cada tecla que eu digito recarrega tudo"

**Causa:** é o modelo. Cada widget dispara um rerun.

**Correção:** `st.form`. Os widgets dentro dele só disparam **um** rerun, no
envio.

```python
with st.form("cadastro"):
    nome = st.text_input("Nome")
    idade = st.number_input("Idade", 0, 120)
    enviado = st.form_submit_button("Salvar")

if enviado:
    st.success(f"{nome}, {idade} anos.")
```

### 9.5 "Mudei o valor de um widget no código e deu exceção"

```python
st.slider("x", 0, 10, key="x")
st.session_state.x = 5       # StreamlitAPIException
```

**Causa:** depois que o widget existe no script, a chave dele pertence ao widget.

**Correção:** escreva **antes** do widget ser criado, ou dentro de um `on_change`.

```python
if "x" not in st.session_state:
    st.session_state.x = 5       # antes: ok
st.slider("x", 0, 10, key="x")
```

---

## 10. Comandos de terminal que você vai usar toda semana

```bash
streamlit run app.py                          # o básico
streamlit run app.py --server.port 8502       # outra porta
streamlit run app.py --server.headless true   # sem tentar abrir navegador
streamlit run app.py --server.runOnSave true  # recarrega ao salvar
streamlit run app.py -- --meu-argumento 42    # passar argumentos PARA O SCRIPT
streamlit config show                         # ver toda a configuração vigente
streamlit cache clear                          # limpar o cache em disco
streamlit docs                                 # abrir a documentação
streamlit hello                                # a demonstração
streamlit init                                 # criar esqueleto de projeto
```

O `--` do quinto comando é importante: sem ele, o Streamlit tenta interpretar
`--meu-argumento` como opção dele e reclama.

---

## 11. Depurar

**`st.write` é o seu `print`.** Ele aceita quase tudo: dicionário, DataFrame,
figura, exceção, função.

```python
st.write(type(dados), dados.shape, dados.dtypes)
```

**Inspecione o estado inteiro:**

```python
with st.expander("estado (depuração)"):
    st.json({k: str(v)[:200] for k, v in st.session_state.items()})
```

**Meça o tempo:**

```python
import time
t = time.perf_counter()
resultado = conta_cara()
st.caption(f"{time.perf_counter() - t:.2f}s")
```

Ou, sem escrever nada, ligue `show_time=True` no cache:

```python
@st.cache_data(ttl=300, show_time=True)
def carregar(): ...
```

**Onde ver os erros:** o traceback aparece **na página**, não só no terminal.
Em produção, esconda-o:

```toml
# .streamlit/config.toml
[client]
showErrorDetails = "none"
```

Rastreamento de pilha na tela do usuário conta a estrutura do seu código para
quem não deveria ver.

---

## 12. Onde ir agora

| Você quer... | Vá para |
|---|---|
| receitas curtas que resolvem tarefas | [06-exemplos.md](06-exemplos.md) |
| referência dos comandos | [05-manual-de-uso.md](05-manual-de-uso.md) |
| um app inteiro, com backend, que roda | [07-projeto-modelo/](07-projeto-modelo/README.md) |
| entender **por que** funciona assim | [10-fundamentos.md](10-fundamentos.md) e [12](12-modelo-de-execucao-e-rerun.md) |
| **fazer um painel profissional** | [16-layout-e-design.md](16-layout-e-design.md) e [17-graficos-e-visualizacao.md](17-graficos-e-visualizacao.md) |
| **fazer um site com backend** | [21](21-backend-dados-e-conexoes.md), [22](22-autenticacao-e-autorizacao.md), [23](23-arquitetura-de-app-real.md) |

---

## Autoteste

1. Como você **prova**, na tela, que o script inteiro roda de novo a cada
   interação? Escreva as duas linhas.
2. Em que situações é preciso reiniciar o servidor, mesmo com *run on save* ligado?
3. Qual é a diferença entre `st.cache_data` e `st.cache_resource`, e o que dá
   errado ao trocar os dois?
4. Por que `contador = 0; if st.button(...): contador += 1` nunca chega a 2?
5. Um usuário reclama que "cada letra digitada trava a tela". Qual é a correção?
6. O que `st.set_page_config` faz e por que a posição dele importa?
7. Você tem dois `st.text_input("Nome")` na mesma página. O que acontece e como
   se resolve?
8. Por que `st.session_state.x = 5` depois de `st.slider(..., key="x")` levanta
   exceção? Onde a atribuição funcionaria?
