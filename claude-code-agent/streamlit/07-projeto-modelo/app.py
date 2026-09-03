"""Painel Comercial — ponto de entrada.

Rode com:  streamlit run app.py

Este arquivo faz quatro coisas e nada mais:
  1. configura a página (tem de ser o PRIMEIRO comando de Streamlit do script);
  2. prepara o "backend" uma única vez por processo (`st.cache_resource`);
  3. decide se mostra a tela de login ou a aplicação (portão de autenticação);
  4. declara a navegação.

Tudo o mais mora em `paginas/`, `ui/` e `nucleo/`. Um `app.py` que cresce é o
primeiro sintoma de um app de Streamlit que vai virar um arquivo de 2.000 linhas.
"""

from __future__ import annotations

import streamlit as st

# ---------------------------------------------------------------------------
# 1. Configuração da página.
# st.set_page_config precisa vir antes de qualquer outro comando st.*, senão o
# Streamlit levanta StreamlitSetPageConfigMustBeFirstCommandError.
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Painel Comercial",
    page_icon=":material/monitoring:",
    layout="wide",                      # ocupa a largura toda: painel quer espaço
    initial_sidebar_state="expanded",
    menu_items={
        "Get help": "https://docs.streamlit.io",
        "Report a bug": None,
        "About": "Projeto-modelo do curso de Streamlit. Dados fictícios.",
    },
)

from nucleo import config, seed          # noqa: E402  (import depois do set_page_config
from nucleo.auth import ErroDeLogin, autenticar   # noqa: E402   é proposital: ver acima)
from nucleo.modelos import Usuario       # noqa: E402


# ---------------------------------------------------------------------------
# 2. Preparação única do backend.
#
# `st.cache_resource` guarda o objeto no processo, compartilhado por TODAS as
# sessões. É o lugar certo para: conexão de banco, cliente de API, modelo de ML
# carregado. Não use `st.cache_data` para isso — ela serializa o valor.
# ---------------------------------------------------------------------------
@st.cache_resource(show_spinner="Preparando o banco de dados...")
def preparar() -> config.Config:
    cfg = config.carregar()
    seed.popular(cfg.caminho_banco, iteracoes_hash=cfg.iteracoes_hash)
    return cfg


try:
    CFG = preparar()
except config.ErroDeConfiguracao as e:
    st.error(f"Erro de configuração: {e}", icon=":material/error:")
    st.stop()          # st.stop() encerra este rerun aqui. Nada abaixo executa.


# ---------------------------------------------------------------------------
# 3. Portão de autenticação.
#
# LIMITE HONESTO: `st.session_state` vive na memória do servidor e some quando a
# aba fecha ou o servidor reinicia. Isso é uma sessão de verdade (não dá para
# forjar do navegador), mas não é "lembrar de mim". Para produção, veja o
# arquivo 22-autenticacao-e-autorizacao.md: `st.login()` com OIDC.
# ---------------------------------------------------------------------------
def usuario_logado() -> Usuario | None:
    return st.session_state.get("usuario")


def tela_de_login() -> None:
    _, meio, _ = st.columns([1, 1.1, 1])
    with meio:
        st.space("large")
        st.markdown("## :material/monitoring: Painel Comercial")
        st.caption("Entre para continuar.")

        # st.form agrupa widgets e só dispara UM rerun, no submit. Sem form,
        # cada tecla no campo de senha reexecutaria o script inteiro.
        with st.form("login", border=True):
            email = st.text_input("E-mail", type="email", icon=":material/mail:",
                                  placeholder="voce@exemplo.com")
            senha = st.text_input("Senha", type="password", icon=":material/key:")
            enviar = st.form_submit_button("Entrar", type="primary", width="stretch")

        if enviar:
            try:
                st.session_state["usuario"] = autenticar(CFG.caminho_banco, email, senha)
                st.rerun()          # recarrega já autenticado
            except ErroDeLogin as e:
                st.error(str(e), icon=":material/block:")

        with st.expander("Contas de demonstração"):
            st.markdown(
                "| E-mail | Senha | Papel |\n|---|---|---|\n"
                "| `admin@exemplo.com` | `admin123` | administrador |\n"
                "| `analista@exemplo.com` | `analista123` | analista |\n"
                "| `leitor@exemplo.com` | `leitor123` | leitor |"
            )
            st.caption("Senhas fracas de propósito: é uma demonstração local com dados fictícios.")


def sair() -> None:
    st.session_state.pop("usuario", None)
    st.cache_data.clear()      # não deixar dados de um usuário no cache do próximo
    st.rerun()


# ---------------------------------------------------------------------------
# 4. Navegação.
#
# st.navigation + st.Page é a forma atual de app multipágina (desde 1.36). Ela
# substitui a pasta mágica `pages/`, porque permite decidir em Python QUAIS
# páginas existem — que é exatamente o que um sistema com papéis precisa.
# ---------------------------------------------------------------------------
u = usuario_logado()

if u is None:
    st.navigation([st.Page(tela_de_login, title="Entrar")], position="hidden").run()
else:
    st.logo("https://streamlit.io/images/brand/streamlit-mark-color.png", size="medium")

    paginas = {
        "Análise": [
            st.Page("paginas/painel.py", title="Painel", icon=":material/monitoring:", default=True),
            st.Page("paginas/exploracao.py", title="Exploração", icon=":material/search:"),
        ],
        "Operação": [
            st.Page("paginas/pedidos.py", title="Pedidos", icon=":material/receipt_long:"),
            st.Page("paginas/clientes.py", title="Clientes", icon=":material/group:"),
        ],
    }
    if u.pode_administrar():
        paginas["Administração"] = [
            st.Page("paginas/admin.py", title="Administração", icon=":material/settings:")
        ]

    with st.sidebar:
        st.markdown(f"**{u.nome}**")
        st.caption(f"{u.email} · {u.papel}")
        if st.button("Sair", icon=":material/logout:", width="stretch"):
            sair()
        st.divider()

    st.navigation(paginas).run()
