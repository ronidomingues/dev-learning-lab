"""Componentes visuais do painel.

Cada função escreve na tela e não devolve nada (ou devolve o valor do widget).
Ter isso num arquivo só é o que impede o "copiar e colar o bloco de KPI em cinco
páginas e esquecer de mudar em quatro".

Estas funções PODEM importar streamlit — é a camada de apresentação.
"""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from nucleo.modelos import KPIs
from ui.formatos import brl, brl_compacto, numero, percentual

# ---------------------------------------------------------------------------
# PALETA — validada, não escolhida por gosto.
#
# A primeira versão deste arquivo usava uma paleta "bonita" com vermelho
# (#be123c) e verde (#15803d) vizinhos. Rodando um validador de visão de cores,
# esse par tem ΔE 1,4 em deuteranopia: para ~8% dos homens, é a MESMA cor.
# O gráfico ficava ilegível e ninguém perceberia sem medir.
#
# Estes valores passam nos cinco testes (faixa de luminosidade, piso de croma,
# separação sob daltonismo, separação para visão normal, contraste com o fundo)
# na ordem em que estão. A ORDEM faz parte da validação: trocar de posição
# quebra a garantia. Ver 17-graficos-e-visualizacao.md.
# ---------------------------------------------------------------------------
PALETA_CLARA = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100",
                "#e87ba4", "#008300", "#4a3aa7", "#e34948"]
PALETA_ESCURA = ["#3987e5", "#d95926", "#199e70", "#c98500",
                 "#d55181", "#008300", "#9085e9", "#e66767"]

# Rampa sequencial de um hue só (azul, claro→escuro), para mapa de calor.
# Arco-íris NUNCA: a ordem das cores do arco-íris não corresponde à ordem
# dos números, e o olho inventa fronteiras onde não há.
RAMPA_SEQUENCIAL = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5",
                    "#256abf", "#184f95", "#0d366b"]


def paleta() -> list[str]:
    """Paleta do tema atual. `st.context.theme.type` diz se o usuário está no
    claro ou no escuro — melhor que chutar."""
    escuro = getattr(getattr(st.context, "theme", None), "type", "light") == "dark"
    return PALETA_ESCURA if escuro else PALETA_CLARA


# Nome curto para uso interno. Mantido por compatibilidade com as páginas.
PALETA = PALETA_CLARA


def cabecalho(titulo: str, subtitulo: str = "", *, icone: str = "") -> None:
    prefixo = f"{icone} " if icone else ""
    st.markdown(f"### {prefixo}{titulo}")
    if subtitulo:
        st.caption(subtitulo)


def linha_de_kpis(k: KPIs, historico: pd.DataFrame | None = None) -> None:
    """Os quatro números do topo, com variação e minigráfico.

    `st.metric(chart_data=...)` desenha a sparkline dentro do cartão — a partir
    do Streamlit 1.6x não é preciso gambiarra de CSS nem componente de terceiro.
    """
    cols = st.columns(4, gap="small")

    def serie(coluna: str) -> list[float] | None:
        if historico is None or historico.empty or coluna not in historico:
            return None
        return historico[coluna].tolist()

    with cols[0]:
        st.metric("Receita", brl_compacto(k.receita_centavos),
                  delta=percentual(k.var_receita), border=True, icon=":material/payments:",
                  chart_data=serie("valor"), chart_type="area",
                  help=f"Valor exato: {brl(k.receita_centavos)}. Exclui pedidos cancelados.")
    with cols[1]:
        st.metric("Pedidos", numero(k.pedidos), delta=percentual(k.var_pedidos),
                  border=True, icon=":material/receipt_long:",
                  chart_data=serie("pedidos"), chart_type="bar")
    with cols[2]:
        st.metric("Ticket médio", brl(k.ticket_medio_centavos),
                  delta=percentual(k.var_ticket), border=True, icon=":material/sell:")
    with cols[3]:
        st.metric("Clientes ativos", numero(k.clientes_ativos),
                  delta=percentual(k.var_clientes), border=True, icon=":material/group:")


def _layout_padrao(fig: go.Figure, altura: int = 320) -> go.Figure:
    """Um único lugar decide como TODO gráfico do painel se parece.

    O que faz um gráfico parecer profissional, em ordem de impacto:
    1. tirar o lixo (grade vertical, moldura, fundo, legenda redundante);
    2. margens pequenas e consistentes;
    3. rótulo em português e no formato do país;
    4. hover que diz o valor exato — o gráfico dá a forma, o hover dá o número.
    """
    fig.update_layout(
        height=altura,
        margin=dict(l=8, r=8, t=28, b=8),
        showlegend=False,
        hovermode="x unified",
        xaxis_title=None,
        yaxis_title=None,
        colorway=paleta(),
        separators=",.",           # decimal vírgula, milhar ponto
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(size=13),
    )
    fig.update_xaxes(showgrid=False, showline=True, linewidth=1, linecolor="rgba(128,128,128,.25)")
    fig.update_yaxes(showgrid=True, gridcolor="rgba(128,128,128,.15)", zeroline=False)
    return fig


def grafico_serie(df: pd.DataFrame, titulo: str) -> None:
    if df.empty:
        st.info("Sem dados no período selecionado.")
        return
    fig = px.area(df, x="data", y="valor", title=titulo)
    fig.update_traces(
        line=dict(width=2), fillcolor="rgba(42,120,214,.12)",
        hovertemplate="%{x|%d/%m/%Y}<br><b>R$ %{y:,.2f}</b><extra></extra>",
    )
    st.plotly_chart(_layout_padrao(fig), width="stretch")


def grafico_ranking(df: pd.DataFrame, coluna: str, titulo: str) -> None:
    if df.empty:
        st.info("Sem dados no período selecionado.")
        return
    df = df.sort_values("valor")  # barra horizontal lê melhor de baixo para cima
    fig = px.bar(df, x="valor", y=coluna, orientation="h", title=titulo)
    fig.update_traces(
        marker_color=paleta()[0],
        hovertemplate="%{y}<br><b>R$ %{x:,.2f}</b><extra></extra>",
    )
    st.plotly_chart(_layout_padrao(fig, altura=max(260, 34 * len(df))), width="stretch")


def grafico_composicao(df: pd.DataFrame, titulo: str) -> None:
    if df.empty:
        st.info("Sem dados no período selecionado.")
        return
    fig = px.bar(df, x="status", y="valor", title=titulo, color="status",
                 color_discrete_sequence=PALETA)
    fig.update_traces(hovertemplate="%{x}<br><b>R$ %{y:,.2f}</b><extra></extra>")
    st.plotly_chart(_layout_padrao(fig), width="stretch")


def mapa_de_calor(matriz: pd.DataFrame, titulo: str) -> None:
    if matriz.empty:
        st.info("Sem dados no período selecionado.")
        return
    fig = px.imshow(matriz, text_auto=".2s", aspect="auto", title=titulo,
                    color_continuous_scale=RAMPA_SEQUENCIAL)
    fig.update_traces(hovertemplate="canal %{y} · %{x}<br><b>R$ %{z:,.2f}</b><extra></extra>")
    fig = _layout_padrao(fig, altura=300)
    fig.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig, width="stretch")


def tabela_pedidos(df: pd.DataFrame, *, altura: int = 420) -> None:
    """Tabela de leitura, com `column_config` — a diferença entre 'dump de
    DataFrame' e 'relatório'. Note `pinned` na coluna-chave e o formato de moeda."""
    if df.empty:
        st.info("Sem pedidos no período selecionado.")
        return
    visao = df[["id", "data", "cliente", "produto", "quantidade", "valor", "status", "canal"]]
    st.dataframe(
        visao,
        height=altura,
        hide_index=True,
        column_config={
            "id": st.column_config.NumberColumn("Nº", format="%d", pinned=True, width="small"),
            "data": st.column_config.DateColumn("Data", format="DD/MM/YYYY", width="small"),
            "cliente": st.column_config.TextColumn("Cliente", width="medium"),
            "produto": st.column_config.TextColumn("Produto", width="medium"),
            "quantidade": st.column_config.NumberColumn("Qtd.", format="%d", width="small"),
            "valor": st.column_config.NumberColumn("Valor", format="R$ %.2f"),
            "status": st.column_config.TextColumn("Status", width="small"),
            "canal": st.column_config.TextColumn("Canal", width="small"),
        },
    )


def aviso_sem_permissao(acao: str) -> None:
    st.warning(
        f"Seu perfil não permite {acao}. "
        "Peça a um administrador para alterar seu papel.",
        icon=":material/lock:",
    )
