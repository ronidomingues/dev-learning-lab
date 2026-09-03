# 20 · Tema e identidade visual

> **Nível:** intermediário · **Escrito em:** 02/09/2026 · Streamlit 1.63.0
> A lista de opções deste arquivo foi extraída do **pacote instalado**
> (`streamlit.config._config_options`), não da documentação.

Em 2025–2026 o tema do Streamlit deixou de ser "quatro cores" e virou um sistema
completo: fontes, raios de borda, cores de gráfico, tema separado para a barra
lateral, e variantes claro/escuro de tudo. Isso mudou o que dá para fazer sem
CSS — e o CSS é justamente o que você quer evitar.

---

## 1. Onde o tema mora

```
.streamlit/config.toml        ← do projeto (VERSIONE ESTE)
~/.streamlit/config.toml      ← do usuário
variáveis STREAMLIT_THEME_*   ← ambiente
--theme.base=dark             ← linha de comando
```

Precedência, do mais forte para o mais fraco: linha de comando → ambiente →
config do projeto → config do usuário → padrão.

**Versione o `config.toml` do projeto.** É a única forma de garantir que o painel
tem a mesma cara na sua máquina e em produção.

---

## 2. A estrutura do tema

Quatro escopos, e cada um aceita quase todas as opções:

```toml
[theme]                # base: vale para tudo
[theme.sidebar]        # sobrescreve na barra lateral
[theme.dark]           # sobrescreve no modo escuro
[theme.dark.sidebar]   # barra lateral no modo escuro
```

Também existem `[theme.light]` e `[theme.light.sidebar]`, para o caso de você
definir a base com valores neutros.

---

## 3. Um tema profissional completo, comentado

```toml
[theme]
base = "light"

# --- Cores estruturais ---
primaryColor            = "#2a78d6"   # botões primários, foco, seleção
backgroundColor         = "#ffffff"   # fundo do conteúdo
secondaryBackgroundColor= "#f6f7f9"   # fundo de blocos, cabeçalho de tabela
textColor               = "#111827"
linkColor               = "#1d4ed8"
linkUnderline           = true

# --- Tipografia ---
font        = "Inter, system-ui, sans-serif"   # corpo
headingFont = "Inter, system-ui, sans-serif"   # títulos
codeFont    = "JetBrains Mono, monospace"
baseFontSize   = 15
baseFontWeight = 400
metricValueFontSize   = 34        # o número do KPI
metricValueFontWeight = 600

# --- Forma ---
baseRadius   = "0.5rem"
buttonRadius = "0.5rem"
borderColor  = "#e5e7eb"
showWidgetBorder = true
showSidebarBorder = false
dataframeBorderColor = "#e5e7eb"
dataframeHeaderBackgroundColor = "#f6f7f9"

# --- Cores dos gráficos (ver 17) ---
chartCategoricalColors = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100",
                          "#e87ba4", "#008300", "#4a3aa7", "#e34948"]
chartSequentialColors  = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5",
                          "#256abf", "#184f95", "#0d366b"]

# --- Barra lateral escura: separa "controles" de "conteúdo" ---
[theme.sidebar]
backgroundColor          = "#0f172a"
secondaryBackgroundColor = "#1e293b"
textColor                = "#e2e8f0"
primaryColor             = "#60a5fa"
linkColor                = "#93c5fd"

# --- Modo escuro: NÃO é o claro invertido ---
[theme.dark]
backgroundColor          = "#0b1120"
secondaryBackgroundColor = "#111a2e"
textColor                = "#e5e7eb"
primaryColor             = "#60a5fa"
borderColor              = "#1f2a44"
chartCategoricalColors   = ["#3987e5", "#d95926", "#199e70", "#c98500",
                            "#d55181", "#008300", "#9085e9", "#e66767"]
```

**A barra lateral escura é o truque de melhor retorno do arquivo.** Cinco linhas,
e o painel deixa de parecer um formulário e passa a parecer um produto — porque a
separação visual entre "onde eu mexo" e "o que eu leio" fica óbvia.

---

## 4. Fonte própria

Sem instalar nada no sistema, apontando para arquivos servidos pela própria app:

```toml
[[theme.fontFaces]]
family = "Inter"
url = "app/static/Inter-Regular.woff2"
weight = 400
style = "normal"

[[theme.fontFaces]]
family = "Inter"
url = "app/static/Inter-SemiBold.woff2"
weight = 600
style = "normal"

[theme]
font = "Inter, system-ui, sans-serif"
```

E ligue a pasta estática:

```toml
[server]
enableStaticServing = true      # serve ./static em /app/static/...
```

**Cuidados:**

- mudança em `fontFaces` **exige reiniciar** o servidor (as demais opções de tema
  atualizam ao vivo);
- **sempre** dê uma pilha de reserva (`Inter, system-ui, sans-serif`) — se o
  arquivo não carregar, a app não pode ficar em Times New Roman;
- fonte hospedada por você evita depender do Google Fonts, o que costuma ser
  requisito em ambiente corporativo e em conformidade com a LGPD/GDPR.

---

## 5. Cores em Markdown

Sem CSS, direto no texto:

```python
st.markdown(":red[atrasado] · :green[em dia] · :blue-background[destaque]")
st.badge("Crítico", color="red", icon=":material/priority_high:")
st.markdown(":shimmer[calculando...]")     # 1.57+
```

Cores disponíveis: `red`, `orange`, `yellow`, `green`, `blue`, `violet`, `gray`,
`primary` — e as variantes `-background`. Todas seguem o tema, inclusive no modo
escuro. É melhor que HTML embutido justamente por isso.

Os tons de cada cor também são configuráveis (`redColor`, `redBackgroundColor`,
`redTextColor`, e as variantes por escopo), mas mexer neles raramente vale a pena.

---

## 6. Ícones

```python
st.button("Salvar", icon=":material/save:")
st.metric("Receita", "R$ 1,2 mi", icon=":material/payments:")
st.Page("...", icon=":material/monitoring:")
st.markdown(":material/warning: atenção")
```

Use **Material Symbols** (`:material/nome:`), não emoji. Emoji é renderizado pelo
sistema operacional: o mesmo 📊 é diferente no Windows, no macOS e no Android. O
ícone Material é o mesmo em todo lugar e herda a cor do tema.

Catálogo: <https://fonts.google.com/icons>. Os nomes válidos estão no próprio
pacote, em `streamlit/material_icon_names.py`.

---

## 7. Ler o tema em Python

```python
tema = st.context.theme.type        # "light" | "dark"
paleta = PALETA_ESCURA if tema == "dark" else PALETA_CLARA
```

Serve para escolher a paleta do Plotly, a cor de fundo de uma figura matplotlib,
ou a variante de um logotipo. É melhor que chutar — e melhor que forçar um tema
só, porque quem usa modo escuro tem motivo.

---

## 8. CSS: quando, como, e por que evitar

**A regra:** tudo que dá para fazer com tema, faça com tema. CSS é o último
recurso.

**Por que evitar:** as classes internas do Streamlit (`.st-emotion-cache-1v0mbdj`
e afins) são geradas e **mudam entre versões, sem aviso**. Um painel que depende
delas quebra numa atualização de rotina, e o erro é visual — ninguém percebe até
o usuário reclamar.

**O gancho oficial e estável**, quando você precisa mesmo:

```python
with st.container(key="cartao_destaque"):
    st.metric("Receita", "R$ 1,2 mi")
```

`key="cartao_destaque"` gera a classe `st-key-cartao_destaque` no HTML. **Essa**
classe é sua, e é estável.

```python
st.html("""
<style>
  .st-key-cartao_destaque {
      background: linear-gradient(135deg, #2a78d6 0%, #1baf7a 100%);
      border-radius: 12px;
      padding: 8px;
  }
</style>
""")
```

Use `st.html` e não `st.markdown(..., unsafe_allow_html=True)`: é o comando
específico para isso, e deixa a intenção explícita na leitura do código.

**Nunca** injete CSS com conteúdo vindo do usuário. Ver
[29-seguranca.md](29-seguranca.md).

---

## 9. Esconder elementos da interface

```toml
[client]
toolbarMode = "minimal"        # "auto" | "developer" | "viewer" | "minimal"
showSidebarNavigation = true
showErrorDetails = "none"      # produção

[ui]
hideTopBar = false
```

```python
st.set_page_config(menu_items={
    "Get help": "https://wiki.empresa.com/painel",
    "Report a bug": "https://jira.empresa.com/novo",
    "About": "Painel Comercial · dados do ERP, atualizados às 06h.",
})
```

Preencher o "About" com a fonte e o horário de atualização do dado é um daqueles
detalhes que fazem o painel parecer mantido por gente.

---

## 10. Embutir a app em outra página

```python
st.context.is_embedded          # True quando aberta com ?embed=true
```

Acrescente `?embed=true` à URL para esconder cabeçalho, rodapé e menu — é como se
põe um painel dentro de um `iframe` de uma intranet ou de um Confluence.

Opções extras via `?embed_options=...`: `show_toolbar`, `show_padding`,
`disable_scrolling`, `light_theme`, `dark_theme`.

---

## 11. Checklist visual

- [ ] `config.toml` do projeto versionado.
- [ ] `primaryColor` é a cor da marca.
- [ ] Barra lateral com fundo próprio.
- [ ] `[theme.dark]` definido — e **selecionado**, não invertido automaticamente.
- [ ] `chartCategoricalColors` validado (ver [17](17-graficos-e-visualizacao.md)).
- [ ] Fonte com pilha de reserva.
- [ ] Ícones Material, não emoji.
- [ ] `toolbarMode = "minimal"` e `showErrorDetails = "none"` em produção.
- [ ] Nenhum CSS mirando classe interna do Streamlit.
- [ ] "About" preenchido com fonte do dado e horário de atualização.

---

## Autoteste

1. Quais são os quatro escopos de tema e a ordem de precedência das fontes de
   configuração?
2. Por que a barra lateral com fundo próprio muda tanto a percepção?
3. Que cuidado toda declaração de fonte própria exige, e o que precisa de
   reinício?
4. Por que ícone Material é melhor que emoji num painel?
5. Como o Python descobre se o usuário está no tema claro ou escuro, e para que
   isso serve?
6. Por que mirar classes internas do Streamlit com CSS é má ideia? Qual é o gancho
   estável?
7. Como embutir o painel num iframe sem o cabeçalho do Streamlit?
