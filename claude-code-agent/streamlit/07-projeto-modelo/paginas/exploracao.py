"""Exploração: a tela para a pergunta que o painel não previu.

Diferença de propósito, e é a que mais gente erra:
- **Painel** responde a perguntas conhecidas, rápido, sempre igual.
- **Exploração** permite perguntas novas, aceita ser mais lenta e mais feia.

Misturar as duas produz um painel com 40 filtros que ninguém entende.

Aqui também está o exemplo de `@st.fragment`: o gráfico de dispersão tem
controles próprios, e mexer neles reexecuta SÓ o fragmento — não a página toda,
não a consulta ao banco.
"""

from __future__ import annotations

import plotly.express as px
import streamlit as st

from nucleo import config, servicos
from paginas._comum import Filtros, barra_de_filtros, pedidos_em_cache, usuario_atual
from ui import componentes as c

CFG = st.session_state.get("_cfg") or config.carregar()
st.session_state["_cfg"] = CFG
usuario_atual()
f: Filtros = barra_de_filtros(CFG.caminho_banco)

c.cabecalho("Exploração", "Cruze as dimensões que quiser. Mais lento e mais livre que o painel.",
            icone=":material/search:")

df = pedidos_em_cache(CFG.caminho_banco, f.inicio, f.fim, f.status, f.canais, f.segmentos)
if df.empty:
    st.info("Sem dados com esses filtros.", icon=":material/filter_alt_off:")
    st.stop()

aba_pivot, aba_disp, aba_bruto = st.tabs(["Tabela dinâmica", "Dispersão", "Dados brutos"])

with aba_pivot:
    dims = ["cliente", "produto", "categoria", "segmento", "canal", "uf", "status"]
    l, col, m = st.columns(3)
    linha = l.selectbox("Linhas", dims, index=dims.index("segmento"), key="e_linha")
    coluna = col.selectbox("Colunas", ["(nenhuma)"] + dims, index=5, key="e_coluna")
    medida = m.selectbox("Medida", ["Receita (R$)", "Pedidos", "Quantidade"], key="e_medida")

    campo, agg = {
        "Receita (R$)": ("valor", "sum"),
        "Pedidos": ("id", "count"),
        "Quantidade": ("quantidade", "sum"),
    }[medida]

    if coluna == "(nenhuma)":
        tabela = df.groupby(linha, as_index=False).agg(**{medida: (campo, agg)})
        tabela = tabela.sort_values(medida, ascending=False)
    else:
        tabela = df.pivot_table(index=linha, columns=coluna, values=campo,
                                aggfunc=agg, fill_value=0)

    st.dataframe(tabela, width="stretch", height=430)

with aba_disp:
    # ------------------------------------------------------------------
    # @st.fragment: só este pedaço reexecuta quando os controles mudam.
    # Sem o decorador, mexer no eixo Y refaria a consulta e redesenharia
    # o painel inteiro. Com ele, o rerun para na fronteira da função.
    # ------------------------------------------------------------------
    @st.fragment
    def dispersao() -> None:
        e1, e2, e3 = st.columns(3)
        x = e1.selectbox("Eixo X", ["quantidade", "valor"], key="e_x")
        y = e2.selectbox("Eixo Y", ["valor", "quantidade"], key="e_y")
        cor = e3.selectbox("Cor", ["segmento", "canal", "categoria", "status"], key="e_cor")
        amostra = df.sample(min(len(df), 2000), random_state=1)  # 2k pontos é o teto útil
        # `symbol=cor` é CODIFICAÇÃO SECUNDÁRIA, e não enfeite: numa dispersão
        # todas as séries aparecem juntas (todos os pares, não só os vizinhos),
        # e nenhuma paleta de 5 cores separa todos os pares para quem tem
        # daltonismo. A forma do marcador resolve o que a cor não resolve.
        fig = px.scatter(amostra, x=x, y=y, color=cor, symbol=cor, opacity=0.65,
                         color_discrete_sequence=c.paleta())
        fig.update_layout(height=430, margin=dict(l=8, r=8, t=8, b=8),
                          separators=",.", legend_title_text="")
        fig.update_traces(marker=dict(size=8, line=dict(width=1, color="rgba(255,255,255,.6)")))
        st.plotly_chart(fig, width="stretch")
        st.caption(f"Amostra de {len(amostra)} de {len(df)} pedidos. "
                   "Dispersão com mais de ~2.000 pontos vira mancha e trava o navegador.")

    dispersao()

with aba_bruto:
    st.caption("Todas as colunas, sem formatação. Para conferência e exportação.")
    st.dataframe(df, width="stretch", height=430, hide_index=True, lazy=True)
