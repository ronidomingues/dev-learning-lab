# 05 · Manual de uso — referência consultável

> **Nível:** iniciante a intermediário · **Escrito em:** 02/09/2026
> **Todas as assinaturas foram extraídas do Streamlit 1.63.0 instalado**, com
> `inspect.signature`, não da documentação. Se divergir do que você tem, rode:
> ```python
> import inspect, streamlit as st; print(inspect.signature(st.metric))
> ```

Organizado **por tarefa**, não por ordem alfabética — porque a pergunta real
nunca é "o que faz `st.pills`", é "como eu ponho um seletor de opções aí".

---

## Índice por tarefa

| Quero... | Seção |
|---|---|
| escrever texto, título, aviso | [1](#1-texto-e-mensagem) |
| mostrar tabela e DataFrame | [2](#2-tabelas-e-dados) |
| desenhar gráfico | [3](#3-gráficos) |
| pedir entrada do usuário | [4](#4-controles-widgets) |
| organizar a tela | [5](#5-layout-e-contêineres) |
| navegar entre páginas | [6](#6-navegação-multipágina) |
| controlar o fluxo do script | [7](#7-fluxo-de-execução) |
| guardar estado | [8](#8-estado-e-url) |
| acelerar (cache) | [9](#9-cache) |
| falar com banco e API | [10](#10-conexões-e-segredos) |
| autenticar usuário | [11](#11-usuário-e-autenticação) |
| mídia, arquivo, download | [12](#12-mídia-arquivos-e-download) |
| chat e IA | [13](#13-chat-e-streaming) |
| configurar tema e servidor | [14](#14-configuração) |
| usar a linha de comando | [15](#15-linha-de-comando) |
| **saber o que está obsoleto** | [16](#16-obsoleto--o-que-mudou) |
| **truques de quem usa há anos** | [17](#17-o-que-só-quem-usa-há-anos-sabe) |

Convenção: `▸` marca parâmetro que quase ninguém usa e deveria.

---

## 1. Texto e mensagem

| Comando | Para quê |
|---|---|
| `st.write(*args)` | canivete suíço: aceita texto, número, DataFrame, figura, dicionário, exceção, função |
| `st.markdown(body, ...)` | Markdown completo, com extensões do Streamlit |
| `st.title` / `st.header` / `st.subheader` | hierarquia de títulos |
| `st.caption(body)` | texto pequeno e cinza: unidade, fonte, data de atualização |
| `st.code(body, language="python")` | bloco de código com destaque |
| `st.text(body)` | monoespaçado, sem interpretar nada |
| `st.latex(body)` | fórmula matemática (aceita `sympy.Expr`) |
| `st.divider()` | linha horizontal |
| `st.badge(label, color=...)` | etiqueta colorida |
| `st.json(body, expanded=...)` | JSON navegável |
| `st.html(body)` | HTML cru — ver o aviso em [29-seguranca.md](29-seguranca.md) |

### Markdown com as extensões do Streamlit

```python
st.markdown("""
**negrito**, *itálico*, `código`, ~~riscado~~

:red[texto vermelho] · :blue-background[fundo azul] · :gray[cinza]

:material/rocket_launch: ícone do Material Symbols · :rocket: emoji

:shimmer[carregando...]        ← efeito de brilho, desde a 1.57
""")
```

As cores disponíveis: `red`, `orange`, `yellow`, `green`, `blue`, `violet`,
`gray`/`grey`, `primary`, e as variantes `-background`.

### Mensagens de estado

```python
st.info("Neutro.",     icon=":material/info:")
st.success("Deu certo.", icon=":material/check_circle:")
st.warning("Cuidado.",   icon=":material/warning:")
st.error("Falhou.",      icon=":material/error:", title="Não foi possível gravar")  # ▸ title
st.exception(ValueError("mostra o traceback formatado"))
st.toast("Salvo.", icon=":material/check:", duration="short")   # notificação flutuante
```

▸ `title=` em `st.error`/`warning`/`info`/`success` (1.6x) separa o resumo do
detalhe. Use: título curto na primeira linha, o que fazer no corpo.

---

## 2. Tabelas e dados

```python
st.dataframe(df, ...)     # interativa: ordena, busca, redimensiona, exporta
st.data_editor(df, ...)   # editável: é a "planilha" do Streamlit
st.table(df)              # estática, simples, sem interação
st.metric(...)            # o cartão de indicador
```

### `st.dataframe` — os parâmetros que importam

```python
evento = st.dataframe(
    df,
    width="stretch",              # "stretch" | "content" | pixels (int)
    height=420,                   # "auto" | pixels
    hide_index=True,
    column_order=["id", "nome"],  # ▸ ordem e SELEÇÃO de colunas de uma vez
    column_config={...},          # ver abaixo — é o que separa relatório de dump
    on_select="rerun",            # torna a tabela um widget
    selection_mode="single-row",  # "single-row" | "multi-row" | "single-column" | ...
    row_height=32,                # ▸
    lazy=True,                    # ▸ 1.61+: carrega as linhas sob demanda
    key="tabela",
)
linhas = evento.selection.rows    # índices posicionais das linhas marcadas
```

### `column_config` — a diferença entre um dump e um relatório

Tipos disponíveis na 1.63.0 (verificado por `dir(st.column_config)`):

```
Column · TextColumn · NumberColumn · CheckboxColumn · SelectboxColumn ·
MultiselectColumn · DateColumn · DatetimeColumn · TimeColumn · ListColumn ·
LinkColumn · ImageColumn · AudioColumn · VideoColumn · JsonColumn ·
MarkdownColumn · ProgressColumn · BarChartColumn · LineChartColumn ·
AreaChartColumn · ButtonColumn
```

```python
st.dataframe(df, column_config={
    "id":     st.column_config.NumberColumn("Nº", format="%d", pinned=True, width="small"),
    "data":   st.column_config.DateColumn("Data", format="DD/MM/YYYY"),
    "valor":  st.column_config.NumberColumn("Valor", format="R$ %.2f"),
    "meta":   st.column_config.ProgressColumn("Meta", min_value=0, max_value=1, format="%.0f%%"),
    "hist":   st.column_config.LineChartColumn("12 meses", y_min=0),
    "site":   st.column_config.LinkColumn("Site", display_text="abrir"),
    "status": st.column_config.SelectboxColumn("Status", options=["novo", "pago"]),
    "abrir":  st.column_config.ButtonColumn("Ação", on_click=minha_funcao),  # 1.59+
})
```

▸ `pinned=True` congela a coluna à esquerda ao rolar horizontalmente. Em tabela
larga, é o parâmetro que salva a leitura.

### `st.data_editor` — edição

```python
editado = st.data_editor(
    df,
    num_rows="dynamic",           # "fixed" | "dynamic" | "add" | "delete"
    disabled=["id", "criado_em"], # colunas somente leitura
    key="editor",
)

# O QUE MUDOU está em st.session_state["editor"], não na diferença de DataFrames:
#   {"edited_rows": {2: {"uf": "RJ"}}, "added_rows": [...], "deleted_rows": [3]}
mudancas = st.session_state["editor"]["edited_rows"]
```

Comparar DataFrames inteiros para descobrir a diferença é desperdício, e erra
quando o índice muda. Use o dicionário de estado.

### `st.metric` — o cartão de indicador

```python
st.metric(
    "Receita", "R$ 1,2 mi",
    delta="+12,3%",                # variação
    delta_color="normal",          # "normal" | "inverse" | "off"
    delta_arrow="auto",            # ▸
    delta_description="vs. mês anterior",   # ▸ 1.6x: explica contra o quê
    border=True,                   # cartão com borda — sempre use em painel
    icon=":material/payments:",    # ▸ 1.61+
    chart_data=[10, 12, 9, 15],    # ▸ sparkline DENTRO do cartão
    chart_type="area",             # "line" | "bar" | "area"
    help="Exclui cancelados.",     # ▸ a definição do indicador. NUNCA omita.
)
```

`delta_color="inverse"` é para indicadores em que **subir é ruim** (custo,
churn, tempo de resposta). Esquecer disso é o erro de KPI mais comum.

---

## 3. Gráficos

### Nativos (rápidos, pouco configuráveis)

```python
st.line_chart(df, x="data", y="valor", color="regiao")
st.area_chart(df, x="data", y="valor", stack="normalize")
st.bar_chart(df, x="cat", y="valor", horizontal=True)
st.scatter_chart(df, x="a", y="b", size="c", color="d")
st.map(df, latitude="lat", longitude="lon", size="peso", color="#2563eb")
```

Servem para rascunho e para exploração. Para painel entregue a alguém, use
Plotly ou Altair — o controle de rótulo, formato e *hover* é o que faz o gráfico
parecer profissional.

### Bibliotecas

```python
st.plotly_chart(fig, theme="streamlit", on_select="rerun", config={...}, key="g")
st.altair_chart(chart, theme="streamlit", on_select="rerun")
st.vega_lite_chart(df, spec)
st.pyplot(fig)                      # matplotlib (estático)
st.graphviz_chart(dot)
st.pydeck_chart(deck, on_select="rerun")
st.mermaid_chart(codigo)            # 1.59+ — diagrama sem instalar nada
```

`theme="streamlit"` faz o gráfico herdar a paleta do seu tema; `theme=None`
mantém a paleta da biblioteca. Escolha um e seja consistente.

`on_select="rerun"` transforma o gráfico em widget: clicar num ponto reexecuta o
script com a seleção disponível. É como se faz *drill-down*.

---

## 4. Controles (widgets)

### Tabela de decisão

| Preciso de... | Use | Observação |
|---|---|---|
| ação | `st.button` | `type="primary"` para a ação principal; ▸ `shortcut="ctrl+s"` |
| ação que baixa arquivo | `st.download_button` | não dispara rerun se `on_click="ignore"` |
| link externo | `st.link_button` | não é botão de ação; não reexecuta |
| sim/não | `st.checkbox` ou `st.toggle` | `toggle` para ligar/desligar algo; `checkbox` para marcar item |
| 1 de poucos (2–5) | `st.radio` ou `st.segmented_control` ou `st.pills` | `segmented_control` é o mais moderno e ocupa menos |
| 1 de muitos | `st.selectbox` | ▸ `accept_new_options=True`; ▸ `filter_mode="fuzzy"` |
| vários de muitos | `st.multiselect` | lista vazia = decida se é "tudo" ou "nada" e documente |
| número | `st.number_input` ou `st.slider` | `slider` quando a ordem de grandeza importa |
| faixa | `st.slider(value=(a, b))` | devolve tupla |
| texto curto | `st.text_input` | ▸ `type="email"/"url"/"phone"/"search"`; ▸ `validate=` |
| texto longo | `st.text_area` | |
| data | `st.date_input` | `value=(a, b)` vira intervalo |
| data e hora | `st.datetime_input` | 1.6x |
| hora | `st.time_input` | |
| cor | `st.color_picker` | |
| arquivo | `st.file_uploader` | devolve objeto em memória, não caminho |
| foto / áudio | `st.camera_input` / `st.audio_input` | |
| avaliação | `st.feedback("stars")` | `"thumbs"`, `"faces"`, `"stars"` |
| menu de ações | `st.menu_button` | 1.56+ |
| paginação | `st.pagination(num_pages)` | 1.58+ |

### Parâmetros comuns a quase todos

```python
st.selectbox(
    "Rótulo", opcoes,
    key="chave",                  # identidade estável; use SEMPRE em app real
    help="explicação",
    on_change=funcao, args=(), kwargs={},
    disabled=False,
    label_visibility="visible",   # "visible" | "hidden" | "collapsed"
    width="stretch",
    format_func=lambda x: ...,    # ▸ mostra bonito, devolve o objeto real
    bind="query-params",          # ▸ 1.55+: estado na URL
    persist_state="session",      # ▸ "page" | "session"
)
```

▸ **`format_func`** é subutilizado e resolve um problema real: você quer que o
usuário veja `"Cliente 042 — São Paulo"` mas que o código receba `42`.

```python
cid = st.selectbox("Cliente", [c.id for c in clientes],
                   format_func=lambda i: nomes[i])   # devolve o ID, mostra o nome
```

▸ **`bind="query-params"`** grava o valor na URL. Consequência: o usuário copia o
endereço e o colega abre a página **no mesmo estado**. Para painel compartilhado,
isso é transformador.

### Validação no cliente (1.62+)

```python
email = st.text_input("E-mail", type="email")                 # validação automática
cpf   = st.text_input("CPF", validate=(r"^\d{11}$", "Digite 11 dígitos."))
```

`validate` aceita uma expressão regular ou `(regex, mensagem)`. **É validação de
conveniência, no navegador.** Nunca confie nela: revalide no servidor.

### `st.form` — agrupar e disparar um rerun só

```python
with st.form("cadastro", clear_on_submit=True, enter_to_submit=True, border=True):
    nome = st.text_input("Nome")
    idade = st.number_input("Idade", 0, 120)
    ok = st.form_submit_button("Salvar", type="primary")

if ok:
    gravar(nome, idade)
```

Regras do formulário:

- widgets dentro do form **não** disparam rerun ao mudar; só o `form_submit_button` dispara;
- `st.button` comum **não pode** ficar dentro de um form (só `form_submit_button`);
- não dá para atualizar a tela *durante* o preenchimento — é o preço.

---

## 5. Layout e contêineres

```python
c1, c2, c3 = st.columns([2, 1, 1], gap="medium", vertical_alignment="center",
                        border=False, wrap=True)   # ▸ wrap=False: fila rolável

with st.container(border=True, height=300, horizontal=False, gap="small",
                  horizontal_alignment="left", key="bloco"):
    ...

with st.expander("Detalhes", expanded=False, icon=":material/info:"):
    ...

abas = st.tabs(["Resumo", "Detalhe"])        # ▸ default=, on_change=
with abas[0]:
    ...

with st.sidebar:
    ...

with st.popover("Filtros", icon=":material/tune:"):
    ...

with st.bottom():          # 1.57+ — fixo no rodapé (barra de chat, ações)
    ...

espaco = st.empty()        # espaço reservado; escrever nele SUBSTITUI o conteúdo
espaco.info("carregando")
espaco.success("pronto")   # troca a mensagem, não empilha

st.space("large")          # espaçamento vertical explícito
st.skeleton(height=200)    # 1.59+ — esqueleto de carregamento
```

▸ `st.container(horizontal=True)` faz uma **linha** de elementos — é a alternativa
mais limpa a `st.columns` quando você só quer botões lado a lado.

▸ `st.empty()` é a peça mais subestimada do Streamlit. É o único jeito de
**substituir** conteúdo em vez de acrescentar.

### Diálogo modal

```python
@st.dialog("Confirmar exclusão", width="small", dismissible=True)
def confirmar(item_id: int):
    st.warning(f"Excluir o item {item_id}?")
    if st.button("Excluir", type="primary"):
        excluir(item_id)
        st.rerun()

if st.button("Excluir"):
    confirmar(42)
```

Só **um** diálogo por vez. Chamar a função abre; `st.rerun()` fecha.

---

## 6. Navegação multipágina

**A forma atual** (desde 1.36) — declarativa, e a única que serve para app com
papéis:

```python
paginas = {
    "Análise": [
        st.Page("paginas/painel.py", title="Painel", icon=":material/monitoring:", default=True),
        st.Page(funcao_python, title="Ao vivo", url_path="ao-vivo"),
    ],
    "Admin": [st.Page("paginas/admin.py", title="Administração")],
}
st.navigation(paginas, position="sidebar", expanded=False).run()
```

`position`: `"sidebar"` (padrão), `"top"` (menu horizontal) ou `"hidden"`
(você desenha a navegação).

**A forma antiga**, ainda funcional: uma pasta `pages/` ao lado do script
principal, com arquivos numerados (`1_Painel.py`). Simples, mas você não decide
em Python quem vê o quê. Para app real, use `st.navigation`.

```python
st.switch_page("paginas/pedidos.py")           # navegar por código
st.page_link("paginas/painel.py", label="Voltar ao painel", icon="🏠")
st.logo("logo.png", size="medium", icon_image="marca.png")
```

---

## 7. Fluxo de execução

```python
st.stop()                    # encerra ESTE rerun aqui; nada abaixo executa
st.rerun()                   # reexecuta a app inteira agora
st.rerun(scope="fragment")   # reexecuta só o fragmento atual

@st.fragment(run_every="10s", parallel=True, key="ticker")
def bloco():
    ...                      # reexecuta sozinho, sem reexecutar a página
```

`st.stop()` é a ferramenta de **guarda**: sem permissão, sem dados, sem login →
mostre a mensagem e pare. Tentar fazer isso com `if/else` aninhado produz
pirâmide ilegível.

### `st.status` e progresso

```python
with st.status("Processando...", expanded=True) as s:
    st.write("etapa 1")
    ...
    s.update(label="Concluído", state="complete")   # "running" | "complete" | "error"

barra = st.progress(0.0, text="0%")
for i in range(100):
    barra.progress((i + 1) / 100, text=f"{i + 1}%")

with st.spinner("Consultando...", show_time=True):
    dados = consulta()
```

---

## 8. Estado e URL

```python
st.session_state["chave"] = valor      # dicionário por ABA do navegador
st.session_state.chave                  # mesma coisa, notação de atributo
"chave" in st.session_state
st.session_state.pop("chave", None)
del st.session_state["chave"]
```

**Três regras que evitam 90% dos erros:**

1. Inicialize com `if "x" not in st.session_state:` — não com `= valor` direto.
2. A chave de um widget pertence ao widget. Escrever nela **depois** de o widget
   existir levanta `StreamlitAPIException`. Escreva antes, ou num `on_change`.
3. Widget que sai da tela **perde** o valor do estado, por padrão. Use
   `persist_state="session"` (1.6x) ou copie para outra chave.

### Parâmetros de URL

```python
st.query_params["periodo"] = "90d"
periodo = st.query_params.get("periodo", "30d")
st.query_params.from_dict({"uf": "SP", "seg": "Varejo"})
todos = st.query_params.get_all("uf")      # ?uf=SP&uf=RJ
st.query_params.clear()
```

Ou, mais simples, deixe o widget cuidar disso: `bind="query-params"`.

---

## 9. Cache

```python
@st.cache_data(
    ttl="10m",                  # segundos, timedelta ou "1h30m"
    max_entries=100,
    show_spinner="Carregando...",
    show_time=True,             # ▸ mostra quanto demorou — ótimo para diagnosticar
    persist="disk",             # sobrevive ao reinício do processo
    hash_funcs={MinhaClasse: id},
    scope="global",             # ▸ "global" | "session"
    refresh_mode="background",  # ▸ 1.61+: serve o valor velho e atualiza atrás
)
def consultar(inicio, fim): ...

@st.cache_resource(ttl=None, validate=conexao_viva, on_release=fechar)
def conexao(): ...
```

| | `cache_data` | `cache_resource` |
|---|---|---|
| Guarda | uma **cópia** serializada | **o próprio objeto** |
| Compartilhado | entre sessões, por chave de argumentos | entre sessões, o mesmo objeto |
| Para | DataFrame, lista, dicionário, resultado de consulta | conexão, cliente de API, modelo de ML |
| Mutação afeta outros? | não (cada um recebe cópia) | **sim** — cuidado |

Invalidar:

```python
consultar.clear()              # só esta função
consultar.clear(inicio, fim)   # só esta entrada
st.cache_data.clear()          # tudo
```

▸ `refresh_mode="background"` (1.61+): quando o TTL expira, o valor antigo
continua sendo servido enquanto o novo é calculado numa thread. Painel não pisca.
Cuidado: o usuário pode ver dado velho por mais tempo do que o TTL sugere.

---

## 10. Conexões e segredos

```python
conn = st.connection("meu_banco", type="sql")     # SQLAlchemy por baixo
df = conn.query("SELECT * FROM pedidos WHERE data >= :d", params={"d": inicio}, ttl="5m")

with conn.session as s:                            # escrita
    s.execute(text("UPDATE ..."), {...})
    s.commit()
```

`secrets.toml` (em `.streamlit/`, **fora do Git**):

```toml
[connections.meu_banco]
url = "postgresql+psycopg://usuario:senha@host:5432/base"

[api]
chave = "..."
```

```python
st.secrets["api"]["chave"]
st.secrets.api.chave
```

Em produção, prefira **variável de ambiente** a arquivo de segredo:
`STREAMLIT_...` ou o mecanismo de segredo do seu orquestrador. Ver
[`variaveis-de-ambiente-e-segredos`](../variaveis-de-ambiente-e-segredos/00-MAPA.md).

---

## 11. Usuário e autenticação

```python
st.login()                  # inicia o fluxo OIDC (precisa de streamlit[auth])
st.login("google")          # provedor nomeado no secrets.toml
st.logout()

if st.user.is_logged_in:
    st.write(st.user.email, st.user.name)
    token = st.user.tokens   # 1.53+
```

Contexto da requisição:

```python
st.context.url · st.context.ip_address · st.context.headers · st.context.cookies
st.context.locale · st.context.timezone · st.context.timezone_offset
st.context.theme.type · st.context.is_embedded
```

Detalhe e armadilhas em [22-autenticacao-e-autorizacao.md](22-autenticacao-e-autorizacao.md).

---

## 12. Mídia, arquivos e download

```python
st.image(img, caption="...", width=400, link="https://...")
st.video(v, autoplay=True, muted=True, loop=True, subtitles="legendas.vtt")
st.audio(a, sample_rate=44100)
st.pdf(dados, height=600)          # precisa de streamlit[pdf]

arq = st.file_uploader("CSV", type=["csv"], accept_multiple_files=False,
                       max_upload_size=50)   # em MB
if arq is not None:
    df = pd.read_csv(arq)          # objeto em memória; NÃO é caminho de arquivo
    bytes_ = arq.getvalue()        # se precisar dos bytes crus
```

```python
st.download_button("Baixar", data=csv_bytes, file_name="dados.csv",
                   mime="text/csv", on_click="ignore")   # ▸ ignore = não reexecuta
```

Servir arquivos estáticos (imagens, fontes):

```toml
[server]
enableStaticServing = true     # serve a pasta ./static em /app/static/...
```

---

## 13. Chat e streaming

```python
for m in st.session_state.get("mensagens", []):
    with st.chat_message(m["papel"]):
        st.markdown(m["texto"])

if pergunta := st.chat_input("Pergunte algo", accept_file=True, file_type=["pdf"]):
    with st.chat_message("user"):
        st.markdown(pergunta)
    with st.chat_message("assistant"):
        resposta = st.write_stream(gerador_de_tokens(pergunta))
```

`st.write_stream` aceita gerador, gerador assíncrono ou iterável, escreve token a
token e **devolve o texto completo** ao final — que é o que você guarda no
histórico.

---

## 14. Configuração

`.streamlit/config.toml`, no projeto (versionado):

```toml
[theme]
base = "light"
primaryColor = "#2563eb"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f6f7f9"
textColor = "#111827"
font = "Inter, sans-serif"          # ▸ ou fontFaces para fonte própria
baseRadius = "0.5rem"
chartCategoricalColors = ["#2563eb", "#0891b2", "#7c3aed"]   # ▸ paleta dos gráficos

[theme.sidebar]                      # ▸ a barra lateral tem tema PRÓPRIO
backgroundColor = "#0f172a"
textColor = "#e2e8f0"

[theme.dark]                         # ▸ e há variante escura de tudo
backgroundColor = "#0b1120"

[server]
port = 8501
address = "0.0.0.0"
headless = true
enableXsrfProtection = true
enableCORS = true
maxUploadSize = 200
maxMessageSize = 200
enableStaticServing = false
allowedHosts = []                    # ▸ contra rebinding de DNS
websocketPingInterval = 20
disconnectedSessionTTL = 120         # ▸ quanto tempo guardar a sessão após queda

[client]
showErrorDetails = "none"            # produção
toolbarMode = "minimal"              # "auto" | "developer" | "viewer" | "minimal"
disableDataExport = false            # ▸ 1.60+: some com o botão de baixar dados
showSidebarNavigation = true

[browser]
gatherUsageStats = false

[runner]
magicEnabled = true
fastReruns = true
parallelMaxWorkers = 8               # ▸ fragmentos paralelos (1.58+)
```

Ver o que está valendo: `streamlit config show`.

---

## 15. Linha de comando

| Comando | O que faz |
|---|---|
| `streamlit run app.py` | roda |
| `streamlit run app.py -- --arg 1` | passa argumentos **ao script** |
| `streamlit run https://.../app.py` | baixa e roda um script remoto |
| `streamlit hello` | demonstração |
| `streamlit init` | cria esqueleto do projeto |
| `streamlit config show` | imprime a configuração vigente |
| `streamlit cache clear` | limpa o cache em disco |
| `streamlit docs` | abre a documentação |
| `streamlit skills` | instala instruções para agentes de IA |
| `streamlit version` | versão |
| `streamlit activate` | registra o e-mail (opcional) |

Qualquer opção de configuração vira flag: `--server.port`, `--theme.base`,
`--client.showErrorDetails`, etc.

---

## 16. Obsoleto — o que mudou

| Não use | Use | Desde |
|---|---|---|
| `st.cache` | `st.cache_data` / `st.cache_resource` | 1.18 (removido) |
| `st.experimental_memo` | `st.cache_data` | 1.18 |
| `st.experimental_singleton` | `st.cache_resource` | 1.18 |
| `st.experimental_rerun` | `st.rerun` | 1.27 |
| `st.experimental_get_query_params` | `st.query_params` | 1.30 |
| `st.experimental_dialog` | `st.dialog` | 1.35 |
| `st.experimental_fragment` | `st.fragment` | 1.37 |
| `st.experimental_user` | `st.user` | 1.42 |
| pasta mágica `pages/` | `st.navigation` + `st.Page` | 1.36 (a antiga ainda funciona) |
| `use_container_width=True` | `width="stretch"` | anunciado para remoção após 31/12/2025 |
| `use_container_width=False` | `width="content"` | idem |
| servidor Tornado | Starlette/Uvicorn (interno) | 1.57 |

O padrão do projeto: o que era `experimental_*` vira estável com o mesmo nome sem
o prefixo, e o antigo some depois de alguns meses. Se você vê `experimental_` em
um tutorial, o tutorial é velho.

---

## 17. O que só quem usa há anos sabe

1. **`st.empty()` é o único jeito de substituir conteúdo.** Tudo o mais
   acrescenta. Guarde o espaço antes e escreva nele depois.

2. **Toda função de escrita devolve um `DeltaGenerator`** — dá para guardar e
   escrever nele depois, fora de ordem:
   ```python
   cabecalho = st.container()
   dados = carregar()                  # demora
   cabecalho.metric("Total", len(dados))   # escreve LÁ EM CIMA, depois
   ```

3. **"Magic":** uma expressão sozinha numa linha é escrita na tela, sem `st.write`.
   Ótimo em notebook, ruim em código de produção — desligue com
   `[runner] magicEnabled = false` se a equipe for grande.

4. **`st.echo()`** mostra o código *e* executa. Insubstituível em material didático:
   ```python
   with st.echo():
       total = df["valor"].sum()
   ```

5. **`st.help(objeto)`** imprime a documentação de qualquer coisa dentro da app.

6. **`key=` em contêiner** (`st.container(key="x")`) vira uma classe CSS
   (`st-key-x`) no HTML. É o gancho oficial para estilizar um bloco específico
   sem sair caçando seletor gerado.

7. **`st.button(shortcut="ctrl+s")`** dá atalho de teclado. Painel operacional
   com atalho parece software de verdade.

8. **`st.rerun(scope=...)` aceita a `key` de um fragmento**, para reexecutar um
   fragmento específico de fora dele.

9. **`st.context.theme.type`** diz se o usuário está no claro ou no escuro — use
   para escolher a paleta do gráfico em vez de chutar.

10. **`st.set_page_config(menu_items={"Report a bug": None})`** remove itens do
    menu ⋮. `toolbarMode = "viewer"` esconde o menu de desenvolvedor de quem só
    vê o painel.

11. **`persist="disk"` no cache** sobrevive ao reinício do processo — o que
    transforma "o primeiro usuário do dia espera 40 s" em "ninguém espera".

12. **Um `.streamlit/config.toml` no projeto vence o global do usuário.** É o
    jeito de garantir que o tema é o mesmo na sua máquina e em produção.

---

## Autoteste

1. Quando usar `st.dataframe` e quando usar `st.data_editor`? Onde ficam as
   alterações feitas no editor?
2. Como fazer um `selectbox` mostrar o nome do cliente e devolver o ID?
3. Qual é a diferença prática entre `st.cache_data` e `st.cache_resource`?
4. O que `bind="query-params"` muda para quem usa o painel?
5. Como você substitui uma mensagem na tela em vez de empilhar outra?
6. Cite três comandos obsoletos e o que os substituiu.
7. Para que serve `st.stop()`, e por que ele é melhor que `if/else` aninhado numa
   guarda de permissão?
8. O que `refresh_mode="background"` faz, e qual é o risco?
9. Como dar um atalho de teclado a um botão?
10. Você quer estilizar um bloco específico com CSS. Qual é o gancho oficial?
