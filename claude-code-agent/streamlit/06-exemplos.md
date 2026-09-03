# 06 · Exemplos — receitas completas e executáveis

> **Nível:** iniciante a avançado · **Escrito em:** 02/09/2026 · Streamlit 1.63.0
> **Todos os 12 exemplos foram executados** com `st.testing.v1.AppTest` na
> máquina de referência (Ubuntu 22.04.5, Python 3.10.12) em 02/09/2026, e as
> interações principais de cada um foram exercitadas. Nenhum tem `...` no meio:
> copie o bloco inteiro para um arquivo e rode.

```bash
streamlit run exemplo.py
```

Dependências além do Streamlit, por exemplo: pandas (1, 2, 3, 5, 10, 12),
numpy (1, 5, 10), plotly (5), openpyxl (10, opcional).

| # | O que resolve | Nível |
|---|---|---|
| [1](#1--indicadores-de-um-csv-qualquer) | painel de KPI a partir de um CSV enviado | trivial |
| [2](#2--filtros-em-cascata) | filtro que não deixa o usuário chegar ao vazio | fácil |
| [3](#3--crud-mínimo-em-sqlite) | o menor "site com backend" possível | fácil |
| [4](#4--formulário-com-validação-de-verdade) | validação no servidor, mensagem por campo | fácil |
| [5](#5--gráfico-com-drill-down) | clicar no gráfico e filtrar a tabela | médio |
| [6](#6--cache-com-ttl-e-botão-de-atualizar) | controlar frescor do dado | médio |
| [7](#7--monitor-ao-vivo-com-fragment) | bloco que se atualiza sozinho | médio |
| [8](#8--tarefa-longa-com-progresso-e-parada) | processo demorado sem travar a tela | médio |
| [9](#9--chat-com-resposta-em-streaming) | interface de conversa | médio |
| [10](#10--exportar-para-excel-e-csv--caso-de-produção) | **caso de produção**: relatório que o Excel BR abre certo | médio |
| [11](#11--multipágina-com-papéis) | navegação por perfil de usuário | médio |
| [12](#12--importação-tudo-ou-nada--caso-de-produção) | **caso de produção**: carga de planilha sem meio-termo | avançado |

---
## 1 · Indicadores de um CSV qualquer

**Problema.** Alguém manda um CSV por semana e quer ver os números. Você não sabe
de antemão quais são as colunas.

**Solução.** Descobrir o esquema em tempo de execução e deixar o usuário apontar
qual coluna é o valor e qual é a categoria.

```python
"""Exemplo 1 — Painel de indicadores a partir de um CSV enviado pelo usuário."""
import io

import pandas as pd
import streamlit as st

st.set_page_config(page_title="KPI de CSV", layout="wide")
st.title("Indicadores de qualquer CSV")

MODELO = "data,categoria,valor\n2026-01-05,A,120.50\n2026-01-06,B,80.00\n"

arquivo = st.file_uploader("Envie um CSV", type=["csv"])
if arquivo is None:
    st.info("Sem arquivo. Usando dados de exemplo.", icon=":material/science:")
    df = pd.read_csv(io.StringIO(MODELO))
    st.download_button("Baixar o CSV de exemplo", MODELO, "exemplo.csv", "text/csv")
else:
    df = pd.read_csv(arquivo)

# Descoberta de colunas: o app não sabe o esquema de antemão.
numericas = df.select_dtypes("number").columns.tolist()
if not numericas:
    st.error("O arquivo não tem nenhuma coluna numérica.", icon=":material/error:")
    st.stop()

col_valor = st.selectbox("Coluna de valor", numericas)
categorias = [c for c in df.columns if c not in numericas]
col_cat = st.selectbox("Coluna de categoria", categorias or df.columns.tolist())

a, b, c, d = st.columns(4)
a.metric("Linhas", f"{len(df):,}".replace(",", "."), border=True)
b.metric("Soma", f"{df[col_valor].sum():,.2f}", border=True)
c.metric("Média", f"{df[col_valor].mean():,.2f}", border=True)
d.metric("Categorias", df[col_cat].nunique(), border=True)

st.bar_chart(df.groupby(col_cat)[col_valor].sum())
st.dataframe(df, hide_index=True, height=300)
```

**Por que funciona.** `select_dtypes("number")` descobre as colunas numéricas; os
`selectbox` transformam essa descoberta em escolha do usuário. O `st.stop()`
quando não há coluna numérica evita um `KeyError` feio três linhas abaixo — é o
padrão "falhe cedo, com mensagem em português".

**Detalhe que importa.** `st.file_uploader` devolve um objeto **em memória**, não
um caminho de arquivo. `pd.read_csv(arquivo)` funciona porque o pandas aceita
objetos tipo-arquivo. Se você precisar dos bytes crus, use `arquivo.getvalue()`.

---

## 2 · Filtros em cascata

**Problema.** O usuário escolhe "Brasil" e depois "Lisboa", o painel fica vazio, e
ele acha que o sistema está quebrado.

**Solução.** As opções de cada filtro saem do recorte já filtrado pelo anterior.

```python
"""Exemplo 2 — Filtros em cascata (o segundo filtro depende do primeiro)."""
import pandas as pd
import streamlit as st

st.title("Filtros em cascata")

DADOS = pd.DataFrame({
    "pais":   ["Brasil", "Brasil", "Brasil", "Portugal", "Portugal", "Angola"],
    "estado": ["SP", "SP", "RJ", "Lisboa", "Porto", "Luanda"],
    "cidade": ["Campinas", "Santos", "Niterói", "Sintra", "Gaia", "Talatona"],
    "vendas": [120, 80, 95, 60, 45, 30],
})

pais = st.selectbox("País", sorted(DADOS["pais"].unique()))

# A chave da cascata: as opções do próximo filtro saem do recorte anterior.
# Sem isso o usuário escolhe "Brasil" + "Lisboa" e o painel fica vazio, sem
# explicação — o erro de usabilidade mais comum em painel com muitos filtros.
so_pais = DADOS[DADOS["pais"] == pais]
estado = st.selectbox("Estado / região", sorted(so_pais["estado"].unique()))

so_estado = so_pais[so_pais["estado"] == estado]
cidades = st.multiselect("Cidades", sorted(so_estado["cidade"].unique()),
                         default=sorted(so_estado["cidade"].unique()))

recorte = so_estado[so_estado["cidade"].isin(cidades)]

st.metric("Vendas no recorte", int(recorte["vendas"].sum()), border=True)
st.dataframe(recorte, hide_index=True)

if recorte.empty:
    st.warning("Nenhuma cidade selecionada.", icon=":material/filter_alt_off:")
```

**Por que funciona.** Como o script roda inteiro a cada interação, o recorte
`so_pais` já está calculado quando o segundo `selectbox` é criado. Em um
framework de eventos, isso exigiria um callback que repopula o segundo campo.
Aqui, é a ordem das linhas.

**Custo.** Cada filtro dispara um rerun completo. Com dados grandes, ponha
`@st.cache_data` na função que traz os dados e filtre no banco.

---

## 3 · CRUD mínimo em SQLite

**Problema.** "Como faço um site com backend?" — este é o núcleo da resposta:
criar, ler, atualizar e excluir, com dados que sobrevivem ao fechar o navegador.

```python
"""Exemplo 3 — CRUD mínimo em SQLite, tudo em um arquivo.

É o menor "site com backend" possível: cria a tabela, insere, lista, exclui.
"""
import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st

BANCO = Path(st.session_state.get("_banco", "tarefas.db"))


@st.cache_resource
def conexao() -> sqlite3.Connection:
    """cache_resource, não cache_data: conexão é RECURSO, não é dado."""
    con = sqlite3.connect(BANCO, check_same_thread=False)
    con.row_factory = sqlite3.Row
    con.execute("""CREATE TABLE IF NOT EXISTS tarefas (
        id INTEGER PRIMARY KEY,
        titulo TEXT NOT NULL,
        feita INTEGER NOT NULL DEFAULT 0)""")
    con.commit()
    return con


con = conexao()

st.title("Tarefas")

with st.form("nova", clear_on_submit=True):
    titulo = st.text_input("Nova tarefa", placeholder="o que precisa ser feito?")
    if st.form_submit_button("Adicionar", type="primary") :
        if not titulo.strip():
            st.error("O título é obrigatório.")
        else:
            # Parâmetro ligado (?), nunca f-string: isto é defesa contra injeção.
            con.execute("INSERT INTO tarefas (titulo) VALUES (?)", (titulo.strip(),))
            con.commit()
            st.rerun()

linhas = con.execute("SELECT id, titulo, feita FROM tarefas ORDER BY id DESC").fetchall()
if not linhas:
    st.info("Nenhuma tarefa ainda.")
    st.stop()

df = pd.DataFrame([dict(l) for l in linhas])
df["feita"] = df["feita"].astype(bool)

editado = st.data_editor(
    df, hide_index=True, disabled=["id", "titulo"], key="ed",
    column_config={
        "id": st.column_config.NumberColumn("Nº", width="small"),
        "titulo": st.column_config.TextColumn("Tarefa", width="large"),
        "feita": st.column_config.CheckboxColumn("Feita?"),
    },
)

mudou = st.session_state.get("ed", {}).get("edited_rows", {})
if mudou and st.button("Gravar", type="primary"):
    for pos, campos in mudou.items():
        if "feita" in campos:
            con.execute("UPDATE tarefas SET feita = ? WHERE id = ?",
                        (int(campos["feita"]), int(df.iloc[int(pos)]["id"])))
    con.commit()
    st.rerun()

if st.button("Excluir as feitas", icon=":material/delete:"):
    n = con.execute("DELETE FROM tarefas WHERE feita = 1").rowcount
    con.commit()
    st.toast(f"{n} tarefa(s) excluída(s).")
    st.rerun()
```

**Três decisões, e todas se repetem em qualquer app de verdade:**

1. **`@st.cache_resource` na conexão**, não `cache_data`. Conexão é recurso: não
   se serializa, e queremos uma só, compartilhada.
2. **Parâmetro ligado (`?`)**, nunca f-string. Concatenar entrada do usuário em
   SQL é injeção de SQL.
3. **`st.session_state["ed"]["edited_rows"]`** diz exatamente o que mudou. Não
   compare DataFrames.

**Limite honesto.** `check_same_thread=False` é necessário porque o Streamlit
atende sessões em threads diferentes, mas **não** torna o SQLite seguro para
escrita concorrente pesada. Para isso: `PRAGMA journal_mode=WAL` e `busy_timeout`
(ver o [projeto-modelo](07-projeto-modelo/nucleo/db.py)), ou PostgreSQL.

---

## 4 · Formulário com validação de verdade

**Problema.** "Dados inválidos" não ajuda ninguém. O usuário precisa saber
**qual** campo e **o que** fazer.

```python
"""Exemplo 4 — Formulário com validação no servidor e mensagens úteis."""
import re
from datetime import date

import streamlit as st

st.title("Cadastro")

REGEX_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[a-zA-Z]{2,}$")


def validar(dados: dict) -> dict[str, str]:
    """Devolve {campo: mensagem}. Vazio = tudo certo.

    Validação no SERVIDOR. `validate=` no widget é conveniência do navegador e
    pode ser burlada por qualquer um com o console aberto.
    """
    erros: dict[str, str] = {}
    if len(dados["nome"].strip()) < 3:
        erros["nome"] = "O nome precisa ter ao menos 3 letras."
    if not REGEX_EMAIL.match(dados["email"]):
        erros["email"] = "E-mail inválido."
    if dados["nascimento"] >= date.today():
        erros["nascimento"] = "A data de nascimento tem de ser no passado."
    idade = (date.today() - dados["nascimento"]).days // 365
    if idade < 18:
        erros["nascimento"] = f"É preciso ter 18 anos ou mais (você tem {idade})."
    if not dados["aceite"]:
        erros["aceite"] = "É preciso aceitar os termos."
    return erros


with st.form("cadastro"):
    nome = st.text_input("Nome completo")
    email = st.text_input("E-mail", type="email")
    nascimento = st.date_input("Nascimento", value=date(1990, 1, 1),
                               min_value=date(1900, 1, 1), format="DD/MM/YYYY")
    aceite = st.checkbox("Aceito os termos de uso")
    enviado = st.form_submit_button("Cadastrar", type="primary")

if enviado:
    erros = validar({"nome": nome, "email": email,
                     "nascimento": nascimento, "aceite": aceite})
    if erros:
        # Uma mensagem POR CAMPO, dizendo o que fazer. Não "dados inválidos".
        for campo, msg in erros.items():
            st.error(f"**{campo}** — {msg}", icon=":material/error:")
    else:
        st.success(f"Cadastro de {nome} concluído.", icon=":material/check_circle:")
        st.balloons()
```

**Por que funciona.** A validação é uma **função pura** que recebe um dicionário e
devolve `{campo: mensagem}`. Ela não sabe o que é Streamlit — o que significa que
você pode testá-la com `pytest` em milissegundos, e reusá-la na importação de
CSV e na API.

**Sobre `validate=` no widget.** O Streamlit 1.62 ganhou validação no navegador
(`st.text_input(validate=...)`). Use — melhora a experiência. Mas **revalide
sempre no servidor**: qualquer pessoa com o console do navegador aberto contorna
a validação do cliente.

---

## 5 · Gráfico com drill-down

**Problema.** O gráfico mostra a forma; o usuário quer o detalhe de um ponto.

```python
"""Exemplo 5 — Gráfico interativo com drill-down: clicar no ponto filtra a tabela."""
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(layout="wide")
st.title("Clique num ponto para ver o detalhe")

rng = np.random.default_rng(7)
n = 200
df = pd.DataFrame({
    "cliente": [f"C{i:03d}" for i in range(n)],
    "receita": rng.integers(1_000, 90_000, n),
    "pedidos": rng.integers(1, 60, n),
    "segmento": rng.choice(["Varejo", "Indústria", "Serviços"], n),
})

fig = px.scatter(df, x="pedidos", y="receita", color="segmento",
                 hover_data=["cliente"], opacity=0.75)
fig.update_layout(height=420, margin=dict(l=8, r=8, t=8, b=8), separators=",.")

# on_select="rerun" transforma o gráfico num WIDGET: a seleção volta em Python.
evento = st.plotly_chart(fig, key="disp", on_select="rerun",
                         selection_mode=("points", "box", "lasso"))

pontos = evento.selection["points"] if evento and "selection" in evento else []
if not pontos:
    st.info("Selecione pontos no gráfico (clique, caixa ou laço).",
            icon=":material/ads_click:")
    st.stop()

# O Plotly devolve o índice da linha DENTRO DO TRAÇO (a série de cor), não do
# DataFrame. Por isso reconstruímos a partir de x/y — é a pegadinha deste recurso.
selecionados = pd.DataFrame([{"pedidos": p["x"], "receita": p["y"]} for p in pontos])
detalhe = df.merge(selecionados, on=["pedidos", "receita"], how="inner")

st.metric("Clientes selecionados", len(detalhe), border=True)
st.dataframe(detalhe, hide_index=True)
```

**Por que funciona.** `on_select="rerun"` transforma o gráfico num widget: cada
seleção dispara um rerun e a seleção volta em Python.

**A pegadinha, e ela custa uma tarde.** O Plotly numera os pontos **dentro do
traço** (cada cor é um traço), não dentro do DataFrame. `pointIndex` 3 do traço
"Varejo" não é a linha 3 do seu DataFrame. Por isso o exemplo reconstrói a
seleção a partir de `x`/`y` e faz um `merge`. Alternativa mais robusta em dados
com duplicatas: use `customdata` na figura para carregar o ID real.

---

## 6 · Cache com TTL e botão de atualizar

**Problema.** O painel precisa ser rápido **e** confiável. Cache demais mostra
número velho; cache de menos derruba o banco.

```python
"""Exemplo 6 — Cache com TTL, botão de atualizar e diagnóstico do cache."""
import time
from datetime import datetime

import pandas as pd
import streamlit as st

st.title("Cache com controle")


@st.cache_data(ttl=60, show_spinner="Consultando a fonte...", show_time=True)
def consultar(regiao: str) -> pd.DataFrame:
    """Finge uma consulta lenta. O `time.sleep` é o seu banco de dados."""
    time.sleep(1.5)
    return pd.DataFrame({
        "regiao": [regiao] * 3,
        "mes": ["jan", "fev", "mar"],
        "valor": [100, 140, 130],
        "consultado_em": [datetime.now().strftime("%H:%M:%S")] * 3,
    })


regiao = st.selectbox("Região", ["Norte", "Sul", "Leste"])

col_a, col_b = st.columns([1, 3])
with col_a:
    if st.button("Atualizar agora", icon=":material/refresh:", width="stretch"):
        # Limpa SÓ esta entrada do cache, não o cache inteiro.
        consultar.clear(regiao)
        st.rerun()

df = consultar(regiao)
st.dataframe(df, hide_index=True)

st.caption(
    "Troque de região: a primeira vez demora 1,5 s (chave nova no cache); "
    "voltar a uma região já vista é instantâneo. Depois de 60 s o TTL expira "
    "e ela demora de novo. O horário na coluna mostra quando o dado foi obtido."
)
```

**A regra que eu uso, e sugiro:**

| Natureza do dado | TTL |
|---|---|
| fechamento do mês anterior | `ttl=None` + botão de limpar |
| painel operacional (vendas do dia) | 60 a 300 s |
| monitoramento (fila, latência) | 5 a 30 s, ou `@st.fragment(run_every=...)` |
| tabela de referência (UFs, categorias) | `ttl="1h"` ou mais |

`consultar.clear(regiao)` limpa **uma entrada**. `st.cache_data.clear()` limpa
tudo, de todo mundo — use com parcimônia.

`show_time=True` mostra na tela quanto tempo a função levou. É a forma mais
barata de descobrir onde o painel está lento.

---

## 7 · Monitor ao vivo com fragment

**Problema.** Um número precisa se atualizar sozinho, sem a página inteira piscar.

```python
"""Exemplo 7 — Monitor ao vivo com @st.fragment(run_every=...).

O bloco se atualiza sozinho a cada 2 segundos SEM reexecutar o resto da página.
Sem fragment, você precisaria de um `while True` com `time.sleep`, que bloqueia
a sessão inteira e é o anti-padrão clássico de Streamlit.
"""
import random
from datetime import datetime

import pandas as pd
import streamlit as st

st.title("Monitor ao vivo")

st.write("Este texto **não** pisca: ele está fora do fragmento.")

if "historico" not in st.session_state:
    st.session_state.historico = []


@st.fragment(run_every="2s")
def monitor() -> None:
    agora = datetime.now()
    cpu = random.uniform(5, 95)
    st.session_state.historico.append({"t": agora, "cpu": cpu})
    st.session_state.historico = st.session_state.historico[-60:]   # janela deslizante

    a, b = st.columns(2)
    a.metric("CPU agora", f"{cpu:.1f}%".replace(".", ","), border=True,
             delta_color="inverse")     # subir é RUIM: cor invertida
    b.metric("Amostras", len(st.session_state.historico), border=True)

    st.line_chart(pd.DataFrame(st.session_state.historico).set_index("t"))
    st.caption(f"Atualizado às {agora:%H:%M:%S}")


monitor()

st.divider()
st.write("E este também não. Só o bloco acima reexecuta.")
```

**Por que funciona.** `@st.fragment(run_every="2s")` agenda a reexecução **só
daquela função**. O resto do script não roda.

**O anti-padrão que isto substitui:**

```python
# NÃO FAÇA ISSO
while True:
    espaco.metric("CPU", medir())
    time.sleep(2)          # trava a sessão; nenhum outro widget responde
```

**Cuidado com memória.** O exemplo guarda só as últimas 60 amostras
(`historico[-60:]`). Uma lista que só cresce dentro de `session_state` é
vazamento de memória garantido — e a causa nº 1 de app derrubado no Community
Cloud por estourar o limite de ~1 GB.

**Cuidado com custo.** `run_every="2s"` com uma consulta ao banco dentro são
1.800 consultas por hora **por usuário conectado**. Multiplique antes de escolher
o intervalo.

---

## 8 · Tarefa longa com progresso e parada

**Problema.** Um processo de 30 segundos deixa a tela morta e o usuário clica de
novo, achando que não funcionou.

```python
"""Exemplo 8 — Tarefa longa com progresso, etapas e possibilidade de parar."""
import time

import streamlit as st

st.title("Processamento em lote")

total = st.number_input("Quantos itens processar", 1, 200, 20)

if st.button("Começar", type="primary"):
    st.session_state.rodando = True
    st.session_state.processados = 0

if st.session_state.get("rodando"):
    if st.button("Parar", icon=":material/stop:"):
        st.session_state.rodando = False
        st.warning("Interrompido pelo usuário.")
        st.stop()

    with st.status("Processando...", expanded=True) as status:
        barra = st.progress(0.0)
        erros = 0
        for i in range(int(total)):
            time.sleep(0.02)                       # o seu trabalho de verdade
            if i % 7 == 6:
                erros += 1
                st.write(f":red[item {i + 1}: falhou]")
            barra.progress((i + 1) / total, text=f"{i + 1} de {total}")
        st.session_state.processados = int(total)

        if erros:
            status.update(label=f"Concluído com {erros} falha(s)", state="error")
        else:
            status.update(label="Concluído", state="complete")

    st.session_state.rodando = False

if st.session_state.get("processados"):
    st.metric("Itens processados", st.session_state.processados, border=True)
```

**Por que funciona.** `st.status` dá o contêiner que muda de estado
(`running` → `complete`/`error`); `st.progress` dá a barra; e o estado em
`session_state.rodando` sobrevive aos reruns.

**Limite honesto que precisa ser dito.** O botão "Parar" só é lido **no próximo
rerun** — ou seja, o laço não é interrompido no meio de verdade. Para
cancelamento real, o trabalho precisa sair para outro processo (fila de tarefas,
`concurrent.futures`, Celery, RQ) e o app apenas consultar o andamento. Ver
[24-tarefas-longas-e-concorrencia.md](24-tarefas-longas-e-concorrencia.md).

---

## 9 · Chat com resposta em streaming

**Problema.** Interface de conversa com resposta que aparece palavra por palavra.

```python
"""Exemplo 9 — Chat com resposta em streaming, sem depender de API externa.

Troque `responder()` por uma chamada real ao seu modelo. Todo o resto —
histórico, `st.chat_message`, `st.write_stream` — fica igual.
"""
import time
from collections.abc import Iterator

import streamlit as st

st.title("Assistente")

if "mensagens" not in st.session_state:
    st.session_state.mensagens = [
        {"papel": "assistant", "texto": "Olá! Pergunte alguma coisa."}
    ]


def responder(pergunta: str) -> Iterator[str]:
    """Gerador que devolve a resposta em pedaços. É o formato que o
    `st.write_stream` espera — e é o formato que as APIs de LLM entregam."""
    resposta = (
        f"Você perguntou: *{pergunta}*. "
        "Esta resposta chega palavra por palavra, como a de um modelo de verdade."
    )
    for palavra in resposta.split(" "):
        yield palavra + " "
        time.sleep(0.02)


# 1. Redesenha o histórico. O script roda todo de novo, então a tela é
#    reconstruída a cada rerun — o histórico é a fonte da verdade.
for m in st.session_state.mensagens:
    with st.chat_message(m["papel"]):
        st.markdown(m["texto"])

# 2. Entrada. `:=` guarda e testa na mesma linha.
if pergunta := st.chat_input("Escreva aqui"):
    st.session_state.mensagens.append({"papel": "user", "texto": pergunta})
    with st.chat_message("user"):
        st.markdown(pergunta)

    with st.chat_message("assistant"):
        # write_stream escreve token a token E DEVOLVE o texto completo.
        texto = st.write_stream(responder(pergunta))

    st.session_state.mensagens.append({"papel": "assistant", "texto": texto})

with st.sidebar:
    if st.button("Limpar conversa", icon=":material/delete_sweep:"):
        del st.session_state.mensagens
        st.rerun()
```

**Por que funciona.** O histórico em `session_state` é a **fonte da verdade**: a
cada rerun, a conversa inteira é redesenhada a partir dele. Isso parece
desperdício e é exatamente o que torna o código simples — não existe estado
escondido na tela.

**Para ligar num modelo de verdade**, troque só o `responder()`. As APIs de LLM
já devolvem um iterável de pedaços; `st.write_stream` consome direto. Ver
[27-tempo-real-e-streaming.md](27-tempo-real-e-streaming.md) e o assunto
[`agentes-de-ia`](../agentes-de-ia/00-MAPA.md).

---

## 10 · Exportar para Excel e CSV — caso de produção

**Problema.** "Dá para eu levar isso para o Excel?" é o pedido nº 1 em painel
corporativo — e o CSV padrão do pandas abre errado no Excel em português.

```python
"""Exemplo 10 — Relatório em Excel e CSV gerados sob demanda.

Caso de produção: o usuário filtra na tela e leva o recorte para o Excel.
Detalhe que ninguém lembra: o BOM (`utf-8-sig`) e o separador `;` — sem eles o
Excel em português abre tudo numa coluna só e estraga os acentos.
"""
import io
from datetime import date

import numpy as np
import pandas as pd
import streamlit as st

st.title("Exportação de relatório")

rng = np.random.default_rng(3)
df = pd.DataFrame({
    "data": pd.date_range("2026-01-01", periods=120, freq="D"),
    "produto": rng.choice(["Ação", "Suporte", "Licença"], 120),
    "valor": rng.integers(100, 9000, 120) / 100,
    "descrição": ["Ação com acentuação: ç, ã, é"] * 120,
})

produtos = st.multiselect("Produtos", sorted(df["produto"].unique()))
recorte = df[df["produto"].isin(produtos)] if produtos else df
st.dataframe(recorte, hide_index=True, height=260)


def para_csv_excel(d: pd.DataFrame) -> bytes:
    """CSV que o Excel brasileiro abre certo: ; como separador, vírgula decimal,
    UTF-8 com BOM."""
    return d.to_csv(index=False, sep=";", decimal=",",
                    date_format="%d/%m/%Y").encode("utf-8-sig")


def para_xlsx(d: pd.DataFrame) -> bytes:
    """XLSX de verdade, com largura de coluna ajustada. Requer openpyxl."""
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as escritor:
        d.to_excel(escritor, index=False, sheet_name="Relatório")
        planilha = escritor.sheets["Relatório"]
        for i, coluna in enumerate(d.columns, start=1):
            largura = max(len(str(coluna)), int(d[coluna].astype(str).str.len().max())) + 2
            planilha.column_dimensions[planilha.cell(1, i).column_letter].width = min(largura, 50)
    return buffer.getvalue()


hoje = date.today().isoformat()
a, b = st.columns(2)
a.download_button("Baixar CSV (Excel BR)", para_csv_excel(recorte),
                  f"relatorio_{hoje}.csv", "text/csv",
                  icon=":material/download:", width="stretch", on_click="ignore")

try:
    import openpyxl  # noqa: F401
    b.download_button(
        "Baixar XLSX", para_xlsx(recorte), f"relatorio_{hoje}.xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        icon=":material/table:", width="stretch", on_click="ignore")
except ImportError:
    b.button("Baixar XLSX", disabled=True, width="stretch",
             help="Instale openpyxl: pip install openpyxl")

st.caption("`on_click=\"ignore\"` evita que o download dispare um rerun inútil.")
```

**Os três detalhes que fazem a diferença** (e que sempre faltam):

1. **`sep=";"`** — o Excel em português espera ponto e vírgula. Com vírgula, ele
   joga a linha inteira numa coluna só.
2. **`decimal=","`** — senão `1234.56` vira texto, e a soma no Excel não funciona.
3. **`encoding="utf-8-sig"`** — o BOM. Sem ele, "Ação" vira "AÃ§Ã£o".

**`on_click="ignore"`** no `download_button` evita um rerun inútil a cada
download. Sem isso, baixar um arquivo grande reexecuta o script inteiro.

**Sobre gerar o arquivo.** O exemplo gera o XLSX a cada rerun. Em produção com
dados grandes, embrulhe em `@st.cache_data` com os filtros como argumentos — a
geração vira instantânea para o mesmo recorte.

---

## 11 · Multipágina com papéis

**Problema.** Nem todo usuário pode ver tudo.

```python
"""Exemplo 11 — Multipágina com papéis, em um arquivo só.

Mostra o padrão de `st.navigation` com páginas definidas como FUNÇÕES, o que
deixa o exemplo autocontido. Em projeto real, use arquivos (ver 07-projeto-modelo).
"""
import streamlit as st

st.set_page_config(page_title="Multipágina", layout="wide")

PAPEIS = {"ana@exemplo.com": "admin", "bruno@exemplo.com": "leitor"}


def pagina_login() -> None:
    st.title("Entrar")
    email = st.selectbox("Quem é você?", list(PAPEIS))
    if st.button("Entrar", type="primary"):
        st.session_state.usuario = {"email": email, "papel": PAPEIS[email]}
        st.rerun()


def pagina_painel() -> None:
    st.title("Painel")
    st.metric("Receita", "R$ 1,2 mi", "+8,4%", border=True)


def pagina_relatorios() -> None:
    st.title("Relatórios")
    st.write("Disponível para qualquer usuário autenticado.")


def pagina_admin() -> None:
    st.title("Administração")
    # SEGUNDA camada de defesa: mesmo que a página seja registrada por engano,
    # ela para aqui. A primeira camada é não registrá-la no st.navigation.
    if st.session_state.get("usuario", {}).get("papel") != "admin":
        st.error("Acesso negado.", icon=":material/block:")
        st.stop()
    st.write("Só administradores chegam aqui.")


usuario = st.session_state.get("usuario")

if usuario is None:
    st.navigation([st.Page(pagina_login, title="Entrar")], position="hidden").run()
else:
    paginas = [
        st.Page(pagina_painel, title="Painel", icon=":material/monitoring:", default=True),
        st.Page(pagina_relatorios, title="Relatórios", icon=":material/description:"),
    ]
    if usuario["papel"] == "admin":
        paginas.append(st.Page(pagina_admin, title="Admin", icon=":material/settings:"))

    with st.sidebar:
        st.caption(f"{usuario['email']} · {usuario['papel']}")
        if st.button("Sair"):
            del st.session_state.usuario
            st.rerun()

    st.navigation(paginas).run()
```

**Por que `st.navigation` e não a pasta `pages/`.** A pasta mágica lista todos os
arquivos, para todo mundo. Com `st.navigation`, **você** decide em Python quais
páginas existem naquela sessão. É a diferença entre "esconder o link" e "a página
não existe para esse usuário".

**Duas camadas, sempre.** A primeira é não registrar a página. A segunda é a
guarda dentro dela (`if papel != "admin": st.error(...); st.stop()`). A segunda
existe porque um dia alguém vai registrar a página para todo mundo por engano.

---

## 12 · Importação tudo-ou-nada — caso de produção

**Problema.** Carga de planilha que falha na linha 700 de 1.000 deixa o banco num
estado que ninguém sabe descrever.

```python
"""Exemplo 12 — Importação de planilha com validação tudo-ou-nada.

Caso de produção. A regra: se UMA linha for inválida, NADA é gravado. Importação
parcial é pior que importação falha, porque você não sabe onde parou.
"""
import io
import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st

st.title("Importar lançamentos")

OBRIGATORIAS = ["data", "descricao", "valor"]


@st.cache_resource
def conexao() -> sqlite3.Connection:
    con = sqlite3.connect(Path("lancamentos.db"), check_same_thread=False)
    con.row_factory = sqlite3.Row
    con.execute("""CREATE TABLE IF NOT EXISTS lancamentos (
        id INTEGER PRIMARY KEY, data TEXT NOT NULL,
        descricao TEXT NOT NULL, valor_centavos INTEGER NOT NULL)""")
    con.commit()
    return con


def validar(df: pd.DataFrame) -> list[str]:
    problemas: list[str] = []
    faltando = [c for c in OBRIGATORIAS if c not in df.columns]
    if faltando:
        return [f"Faltam as colunas: {', '.join(faltando)}."]
    for i, linha in df.iterrows():
        n = i + 2                      # +2: linha 1 é o cabeçalho, e o índice é 0
        if pd.isna(linha["data"]) or not str(linha["data"]).strip():
            problemas.append(f"linha {n}: data vazia")
        if not str(linha["descricao"]).strip():
            problemas.append(f"linha {n}: descrição vazia")
        try:
            if float(linha["valor"]) <= 0:
                problemas.append(f"linha {n}: valor precisa ser positivo")
        except (TypeError, ValueError):
            problemas.append(f"linha {n}: valor '{linha['valor']}' não é número")
    return problemas


MODELO = "data,descricao,valor\n2026-03-01,Aluguel,2500.00\n2026-03-02,Energia,318.45\n"
st.download_button("Baixar modelo", MODELO, "modelo.csv", "text/csv")

arquivo = st.file_uploader("CSV de lançamentos", type=["csv"])
if arquivo is None:
    st.stop()

df = pd.read_csv(io.BytesIO(arquivo.getvalue()))
st.caption(f"{len(df)} linha(s) no arquivo. Prévia:")
st.dataframe(df.head(10), hide_index=True)

problemas = validar(df)
if problemas:
    st.error(f"{len(problemas)} problema(s). **Nada foi gravado.**",
             icon=":material/error:")
    st.code("\n".join(problemas[:30]))
    st.stop()

st.success("Arquivo válido.", icon=":material/check_circle:")

if st.button("Importar", type="primary", icon=":material/upload:"):
    con = conexao()
    registros = [
        (str(l["data"]), str(l["descricao"]).strip(), int(round(float(l["valor"]) * 100)))
        for _, l in df.iterrows()
    ]
    try:
        # UMA transação para o lote inteiro: tudo entra ou nada entra.
        with con:
            con.executemany(
                "INSERT INTO lancamentos (data, descricao, valor_centavos) VALUES (?,?,?)",
                registros)
    except sqlite3.Error as e:
        st.error(f"Falha ao gravar: {e}. Nenhuma linha foi inserida.")
        st.stop()

    total = con.execute("SELECT COUNT(*) FROM lancamentos").fetchone()[0]
    st.success(f"{len(registros)} lançamento(s) importado(s). "
               f"Total na base: {total}.", icon=":material/check_circle:")
```

**A regra, e ela não é negociável:** valide **tudo** antes de gravar **qualquer
coisa**; grave em **uma** transação. Importação parcial é pior que importação
falha, porque a falha você repete — a parcial você tem de investigar.

**Detalhes que vêm da prática:**

- `linha {i + 2}` — o usuário conta a partir de 1 e o cabeçalho é a linha 1. Errar
  isso faz o usuário procurar o problema na linha errada.
- Dinheiro convertido para **centavos inteiros** na entrada. Guardar `float`
  é como se perde R$ 0,01 por linha em 100.000 linhas.
- `with con:` no sqlite3 já é bloco transacional: commit no sucesso, rollback na
  exceção.
- A prévia mostra 10 linhas antes de qualquer botão. Ninguém importa às cegas.

---
## Exercícios

1. No exemplo 1, acrescente detecção automática de coluna de data e um gráfico
   de série temporal quando ela existir.
2. No exemplo 3, acrescente edição do título da tarefa (não só do "feita"), com
   `st.dialog` de confirmação.
3. No exemplo 5, use `customdata` do Plotly para carregar o ID do cliente e
   elimine o `merge` por x/y. Compare a robustez com dados duplicados.
4. No exemplo 7, troque o dado aleatório por uma leitura real (`psutil.cpu_percent()`)
   e meça quanto o `run_every` custa de CPU.
5. No exemplo 8, tire o trabalho do laço e ponha num `ThreadPoolExecutor`, com o
   app só consultando o andamento. O botão "Parar" passa a funcionar de verdade?
6. No exemplo 12, acrescente detecção de duplicata contra o que já está no banco,
   com a opção "ignorar duplicatas" ou "abortar".

---

## Autoteste

1. Por que o exemplo 2 evita que o usuário chegue a um recorte vazio? Que
   propriedade do modelo de execução torna isso trivial?
2. No exemplo 3, por que a conexão usa `cache_resource` e não `cache_data`?
3. Qual é a pegadinha do índice de seleção no Plotly, e como se contorna?
4. Que TTL você usaria para: fechamento contábil, vendas do dia, tamanho de fila?
5. Por que o botão "Parar" do exemplo 8 não interrompe o laço de verdade?
6. Cite os três ajustes que fazem um CSV abrir corretamente no Excel em português.
7. Por que `st.navigation` é melhor que a pasta `pages/` para app com papéis?
8. Por que importação parcial é pior que importação falha?
