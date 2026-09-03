# 19 · Multipágina e navegação

> **Nível:** intermediário · **Escrito em:** 02/09/2026 · Streamlit 1.63.0

---

## 1. As duas formas, e qual usar

### A antiga: a pasta mágica `pages/`

```
app.py
pages/
├── 1_Painel.py
├── 2_Pedidos.py
└── 3_Admin.py
```

O Streamlit varre a pasta, ordena pelo número, tira o prefixo e monta o menu.
Zero código. Ainda funciona.

**O limite:** o menu é a listagem da pasta. Você não decide **em Python** quem vê
o quê. Esconder o item com CSS não é controle de acesso — o arquivo continua
acessível pela URL.

### A atual: `st.navigation` + `st.Page` (desde 1.36)

```python
paginas = {
    "Análise": [
        st.Page("paginas/painel.py", title="Painel",
                icon=":material/monitoring:", default=True),
        st.Page("paginas/exploracao.py", title="Exploração"),
    ],
    "Operação": [
        st.Page("paginas/pedidos.py", title="Pedidos"),
    ],
}
if usuario.papel == "admin":
    paginas["Administração"] = [st.Page("paginas/admin.py", title="Administração")]

st.navigation(paginas, position="sidebar").run()
```

**Use esta.** Ela é declarativa e, principalmente, é **código**: a lista de páginas
pode depender do usuário, de uma configuração, de um teste A/B.

Assinaturas (1.63.0):

```python
st.navigation(pages, *, position="sidebar"|"top"|"hidden", expanded=False) -> Page
st.Page(page, *, title=None, icon=None, url_path=None, default=False,
        visibility="visible"|"hidden") -> None
```

`page` aceita **caminho de arquivo** ou **função Python**. Arquivo para projeto de
verdade; função para exemplos autocontidos e telas curtas (como o login).

---

## 2. O portão de autenticação

O padrão canônico, que está em [`app.py`](07-projeto-modelo/app.py):

```python
usuario = st.session_state.get("usuario")

if usuario is None:
    # navegação escondida, uma página só: não há para onde ir sem logar
    st.navigation([st.Page(tela_de_login, title="Entrar")], position="hidden").run()
else:
    st.navigation(montar_paginas(usuario)).run()
```

**Duas camadas, sempre.** A primeira é não registrar a página. A segunda é a
guarda dentro da própria página:

```python
# no topo de paginas/admin.py
u = exigir(("admin",))     # mostra erro e chama st.stop() se não for admin
```

Por que as duas: hoje a página não está registrada para o leitor; amanhã alguém
mexe no `montar_paginas` e registra. A guarda interna é o cinto de segurança.

> **Comportamento verificado (Streamlit 1.63.0, 02/09/2026):** quando um usuário
> tenta a URL de uma página que **não** está registrada na navegação daquela
> sessão, o Streamlit não executa a página — ele cai na página padrão. Ou seja, a
> primeira camada funciona de fato. Ainda assim, mantenha a segunda.

---

## 3. Navegar por código

```python
st.switch_page("paginas/pedidos.py")                       # vai para lá agora
st.switch_page("paginas/pedidos.py", query_params={"id": 42})
st.page_link("paginas/painel.py", label="Voltar", icon=":material/arrow_back:")
```

`st.page_link` desenha um link; `st.switch_page` levanta uma exceção de controle e
troca de página imediatamente (nada abaixo executa, como no `st.stop()`).

---

## 4. Estado entre páginas

`st.session_state` é **da sessão**, não da página: sobrevive à navegação. É por
isso que o usuário logado continua logado ao trocar de página.

**O que NÃO sobrevive:** o valor de um widget cujo `key` só existe em uma página.
Ao sair da página, o widget deixa de ser renderizado e o Streamlit limpa a chave.

```python
st.multiselect("UF", ufs, key="f_uf", persist_state="session")   # sobrevive
```

**Padrão para filtros globais:** monte a barra lateral numa função compartilhada
(`paginas/_comum.py`), com as mesmas chaves em todas as páginas. Assim o usuário
troca de página e o recorte continua o mesmo — que é o que ele espera.

---

## 5. URL e estado compartilhável

```python
st.Page("paginas/painel.py", url_path="painel")     # define /painel
```

Com `bind="query-params"` nos filtros, a URL fica assim:

```
https://painel.empresa.com/painel?f_atalho=90+dias&f_segmento=Varejo&f_segmento=Governo
```

O usuário copia, manda no chat, e o colega abre **a mesma coisa**. Esse é o
recurso que mais aproxima um painel de Streamlit de uma ferramenta de BI.

Cuidados já mencionados em [13](13-session-state-e-widgets.md): nada sensível na
URL, e atenção ao tamanho da query string.

---

## 6. Organização de arquivos que aguenta crescer

```
app.py                      # só: config, login, navegação
paginas/
├── _comum.py               # cache, filtros, guardas — compartilhado
├── painel.py
├── pedidos.py
└── admin.py
nucleo/                     # backend: sem importar streamlit
ui/                         # componentes visuais
```

**Regras:**

1. `app.py` **não** cresce. Se ele passou de 150 linhas, algo que é de página está
   nele.
2. Módulos internos com prefixo `_` (`_comum.py`) não viram página.
3. Cada arquivo de página é um **script**, não um módulo com funções — o Streamlit
   o executa de cima a baixo. Ponha as funções em `ui/` ou `nucleo/`.
4. Import compartilhado vai para `_comum.py`, não copiado em cinco arquivos.

**Sobre imports em arquivos de página:** o diretório do script principal entra no
`sys.path`, então `from nucleo import servicos` funciona a partir de qualquer
página, sem instalar o pacote.

---

## 7. Menu no topo e marca

```python
st.navigation(paginas, position="top").run()      # menu horizontal
st.logo("logo.png", size="medium", icon_image="marca-pequena.png",
        link="https://empresa.com")
```

`position="top"` funciona bem em app com 3 a 5 páginas e libera a lateral inteira
para os filtros. Com muitas páginas, volte para a lateral.

`icon_image` é a versão reduzida, usada quando a barra lateral está fechada.

---

## 8. Armadilhas

| Armadilha | Correção |
|---|---|
| `st.set_page_config` numa página filha | deve ficar **só** no `app.py`, e ser o primeiro comando |
| filtro reseta ao trocar de página | `persist_state="session"`, ou barra de filtros compartilhada |
| duas páginas com o mesmo `url_path` | dê `url_path` explícito e único |
| esconder o item do menu como "segurança" | não é segurança; use `st.navigation` condicional **e** guarda na página |
| `pages/` e `st.navigation` juntos | escolha um; misturar dá comportamento confuso |
| `app.py` com 800 linhas | mova para `paginas/` |

---

## Autoteste

1. Quais são as duas formas de multipágina, e por que `st.navigation` é a certa
   para app com papéis?
2. Descreva o portão de autenticação com `position="hidden"`.
3. Por que duas camadas de controle de acesso, se a primeira já funciona?
4. O que acontece com o valor de um widget ao trocar de página? Como evitar?
5. Como fazer um painel compartilhável por link?
6. Quatro regras de organização de arquivos numa app multipágina.
7. Onde o `st.set_page_config` deve ficar numa app multipágina, e por quê?
