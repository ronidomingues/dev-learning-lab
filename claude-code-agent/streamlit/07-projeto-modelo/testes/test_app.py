"""Testes da INTERFACE com `st.testing.v1.AppTest` — sem navegador.

AppTest executa o script do jeito que o servidor executaria, e devolve a árvore
de elementos para você inspecionar. É rápido (roda em CI, sem Chrome) e pega a
classe de erro mais comum em Streamlit: "o script quebra em algum caminho de
estado que ninguém testou à mão".

O que ele NÃO pega: CSS, layout, componente customizado em JavaScript. Para
isso é Playwright — e, na minha experiência, quase nunca vale o custo num app
de dados interno.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from nucleo import seed
from nucleo.modelos import Usuario

RAIZ = Path(__file__).resolve().parent.parent
TEMPO_LIMITE = 60          # o primeiro run popula o banco; 3s (padrão) não basta


@pytest.fixture()
def app(tmp_path: Path, monkeypatch) -> AppTest:
    """App apontando para um banco temporário, já populado.

    Se outra fixture do teste já apontou PAINEL_BANCO para um banco preparado
    (ver `banco_vazio_em_governo`), respeita a escolha dela.
    """
    if not os.environ.get("PAINEL_BANCO", "").startswith(str(tmp_path)):
        caminho = tmp_path / "app.db"
        seed.popular(caminho, dias=120, pedidos=300, iteracoes_hash=100_000, semente=7)
        monkeypatch.setenv("PAINEL_BANCO", str(caminho))
        monkeypatch.setenv("PAINEL_HASH_ITER", "100000")
    return AppTest.from_file(str(RAIZ / "app.py"), default_timeout=TEMPO_LIMITE)


def _logado(app: AppTest, papel: str = "admin") -> AppTest:
    app.session_state["usuario"] = Usuario(1, f"{papel}@exemplo.com", "Teste", papel)
    return app


# --- portão de autenticação ------------------------------------------------
def test_sem_login_mostra_tela_de_entrada(app: AppTest):
    app.run()
    assert not app.exception
    textos = " ".join(m.value for m in app.markdown)
    assert "Painel Comercial" in textos
    # A tela de login tem exatamente dois campos e nenhum dado de negócio.
    assert len(app.text_input) == 2


def test_login_com_senha_errada_mostra_erro(app: AppTest):
    app.run()
    app.text_input[0].set_value("admin@exemplo.com")
    app.text_input[1].set_value("senha-errada")
    app.button[0].click().run()
    assert app.error
    assert "incorretos" in app.error[0].value
    assert "usuario" not in app.session_state


def test_login_correto_entra_no_painel(app: AppTest):
    app.run()
    app.text_input[0].set_value("admin@exemplo.com")
    app.text_input[1].set_value("admin123")
    app.button[0].click().run()
    assert not app.exception
    assert app.session_state["usuario"].papel == "admin"
    assert len(app.metric) >= 4          # a linha de KPIs apareceu


# --- painel ----------------------------------------------------------------
def test_painel_desenha_os_quatro_kpis(app: AppTest):
    _logado(app).run()
    assert not app.exception
    rotulos = [m.label for m in app.metric]
    for esperado in ("Receita", "Pedidos", "Ticket médio", "Clientes ativos"):
        assert esperado in rotulos


def test_periodo_sem_dados_avisa_e_nao_quebra(app: AppTest, banco_vazio_em_governo):
    """O caminho que mais derruba painel: filtro que não devolve nada.

    NOTA: o caminho natural deste teste seria mexer no `st.date_input` para um
    período sem pedidos. Não dá: em Streamlit 1.63.0,
    `AppTest.date_input(...).set_value()` NÃO tem efeito — o estado é gerado
    corretamente mas o script continua lendo o valor antigo. `text_input`,
    `number_input`, `slider`, `time_input` e `multiselect` funcionam.
    Ver 75-armadilhas.md, armadilha 24. Por isso o teste usa o multiselect de
    segmento contra um segmento que a fixture esvaziou.
    """
    _logado(app).run()
    app.multiselect(key="f_segmento").set_value(["Governo"]).run()
    assert not app.exception
    assert app.info                                        # avisou em vez de estourar
    assert "Nenhum pedido" in app.info[0].value


def test_filtro_vazio_significa_sem_filtro(app: AppTest):
    """Decisão de projeto explícita: multiselect vazio NÃO é 'nada selecionado',
    é 'sem restrição'. Documentada aqui para ninguém 'consertar' isso depois."""
    _logado(app).run()
    com_filtro = app.metric[1].value
    app.multiselect(key="f_status").set_value([]).run()
    assert not app.exception
    assert app.metric[1].value != com_filtro   # sem restrição traz mais pedidos


def test_trocar_granularidade_nao_quebra(app: AppTest):
    _logado(app).run()
    app.segmented_control(key="p_gran").set_value("Mês").run()
    assert not app.exception


# --- permissões ------------------------------------------------------------
def test_leitor_que_forca_a_url_de_admin_cai_no_painel(app: AppTest):
    """Esconder o item do menu não bastaria; quem barra é o `st.navigation`.

    Como a página de admin nem entra na lista de páginas de um leitor, forçar a
    URL não a executa: o Streamlit cai na página padrão. Comportamento correto,
    e a razão pela qual `st.navigation` (e não a pasta mágica `pages/`) é o
    caminho certo para app com papéis.

    A guarda `exigir(("admin",))` dentro da própria página é a SEGUNDA camada,
    e é ela que protege se um dia alguém registrar a página para todo mundo.
    """
    _logado(app, "leitor").switch_page("paginas/admin.py").run()
    assert not app.exception
    assert any("Painel comercial" in m.value for m in app.markdown)   # caiu no padrão
    assert not any("Importar pedidos" in str(t) for t in app.tabs)


def test_guarda_da_pagina_barra_papel_insuficiente(app: AppTest):
    """A segunda camada, testada isoladamente: `exigir(("admin",))` para a página."""
    def pagina_protegida() -> None:
        # `AppTest.from_function` reexecuta o CÓDIGO-FONTE da função num script
        # novo: nomes do módulo de teste NÃO estão visíveis lá dentro.
        # Todo import precisa estar dentro da própria função.
        import sys
        from pathlib import Path as P

        import streamlit as st

        sys.path.insert(0, str(P(__file__).resolve().parent.parent)
                        if "__file__" in dir() else ".")
        from nucleo.modelos import Usuario as U
        from paginas import _comum

        st.session_state["usuario"] = U(1, "leitor@e.com", "L", "leitor")
        _comum.exigir(("admin",))
        st.write("não deveria chegar aqui")

    at = AppTest.from_function(pagina_protegida, default_timeout=TEMPO_LIMITE)
    at.run()
    assert at.error and "Acesso negado" in at.error[0].value
    assert not at.markdown


def test_leitor_nao_pode_criar_pedido(app: AppTest):
    _logado(app, "leitor").switch_page("paginas/pedidos.py").run()
    assert not app.exception
    novo = [b for b in app.button if b.label == "Novo pedido"]
    assert novo and novo[0].disabled          # botão existe, mas desabilitado


def test_analista_pode_criar_pedido(app: AppTest):
    _logado(app, "analista").switch_page("paginas/pedidos.py").run()
    assert not app.exception
    novo = [b for b in app.button if b.label == "Novo pedido"]
    assert novo and not novo[0].disabled


def test_admin_abre_a_pagina_de_administracao(app: AppTest):
    _logado(app, "admin").switch_page("paginas/admin.py").run()
    assert not app.exception
    assert any("Administração" in m.value for m in app.markdown)


# --- páginas carregam ------------------------------------------------------
@pytest.mark.parametrize("pagina", [
    "paginas/painel.py", "paginas/exploracao.py",
    "paginas/pedidos.py", "paginas/clientes.py",
])
def test_todas_as_paginas_carregam_sem_excecao(app: AppTest, pagina: str):
    _logado(app).switch_page(pagina).run()
    assert not app.exception, f"{pagina} levantou: {app.exception}"
