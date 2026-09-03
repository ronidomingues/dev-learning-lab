"""Painel executivo: a tela que alguém abre às 8h e fecha em 30 segundos.

Regras de projeto que estão aplicadas aqui, e o porquê de cada uma:

1. **Números antes de gráficos.** Quem manda quer o número; o gráfico explica o
   número. KPI no topo, sempre com comparação — número sem base não informa nada.
2. **Uma pergunta por bloco.** Cada gráfico responde a UMA pergunta explícita,
   escrita no título. "Receita por dia" é um título; "Análise temporal" não é.
3. **O filtro é global e mora na barra lateral.** Filtro espalhado pela página
   faz o usuário perder de vista o que está vendo.
4. **Nada abaixo da dobra sem motivo.** Detalhe fica em aba ou expander.
5. **Estado de vazio tratado.** Todo bloco sabe o que dizer quando não há dado.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from nucleo import servicos
from paginas._comum import Filtros, barra_de_filtros, pedidos_em_cache, usuario_atual
from ui import componentes as c
from ui.formatos import brl, data_br

CFG = st.session_state.get("_cfg") or __import__("nucleo.config", fromlist=["carregar"]).carregar()
st.session_state["_cfg"] = CFG

usuario_atual()
f: Filtros = barra_de_filtros(CFG.caminho_banco)

c.cabecalho(
    "Painel comercial",
    f"{data_br(f.inicio)} a {data_br(f.fim)} · {f.dias} dias · "
    f"comparado com os {f.dias} dias anteriores",
    icone=":material/monitoring:",
)

# --- dados ------------------------------------------------------------------
atual = pedidos_em_cache(CFG.caminho_banco, f.inicio, f.fim, f.status, f.canais, f.segmentos)
ini_ant, fim_ant = servicos.periodo_anterior(f.inicio, f.fim)
anterior = pedidos_em_cache(CFG.caminho_banco, ini_ant, fim_ant, f.status, f.canais, f.segmentos)

kpis = servicos.calcular_kpis(atual, anterior)

# Série curta para as sparklines dos cartões (últimos 30 pontos do período).
serie_dia = servicos.serie_temporal(atual, "D")
if not serie_dia.empty:
    contagem = (atual[atual["status"] != "cancelado"]
                .set_index("data")["id"].resample("D").count()
                .reset_index(name="pedidos"))
    hist = serie_dia.merge(contagem, on="data", how="left").tail(30)
else:
    hist = None

c.linha_de_kpis(kpis, hist)

if atual.empty:
    st.info(
        "Nenhum pedido bate com esses filtros. "
        "Tente ampliar o período ou limpar o filtro de canal/segmento.",
        icon=":material/filter_alt_off:",
    )
    st.stop()

st.space("small")

# --- linha 1: evolução + composição ----------------------------------------
esq, dir_ = st.columns([2, 1], gap="medium")

with esq:
    with st.container(border=True):
        gran = st.segmented_control(
            "Granularidade", ["Dia", "Semana", "Mês"], default="Dia",
            key="p_gran", label_visibility="collapsed",
        ) or "Dia"
        mapa = {"Dia": "D", "Semana": "W", "Mês": "ME"}
        c.grafico_serie(servicos.serie_temporal(atual, mapa[gran]),
                        f"Quanto entrou por {gran.lower()}")

with dir_:
    with st.container(border=True):
        c.grafico_composicao(servicos.composicao_por_status(atual),
                             "Em que estágio está o dinheiro")

# --- linha 2: rankings ------------------------------------------------------
a, b = st.columns(2, gap="medium")
with a:
    with st.container(border=True):
        c.grafico_ranking(servicos.ranking(atual, "cliente", 10), "cliente",
                          "Quem mais comprou")
with b:
    with st.container(border=True):
        c.grafico_ranking(servicos.ranking(atual, "produto", 10), "produto",
                          "O que mais vendeu")

# --- linha 3: cruzamento ----------------------------------------------------
with st.container(border=True):
    c.mapa_de_calor(servicos.matriz_canal_segmento(atual),
                    "Onde o canal encontra o segmento (receita)")

# --- detalhe sob demanda ----------------------------------------------------
with st.expander(f"Ver os {len(atual)} pedidos do período", icon=":material/table:"):
    c.tabela_pedidos(atual, altura=380)

    # Download é o recurso mais pedido em painel corporativo e o mais esquecido.
    # `to_csv` com `;` e vírgula decimal abre certo no Excel em português.
    csv = (atual[["id", "data", "cliente", "produto", "quantidade", "valor", "status", "canal"]]
           .to_csv(index=False, sep=";", decimal=",", date_format="%d/%m/%Y")
           .encode("utf-8-sig"))   # BOM: sem ele o Excel estraga acentos
    st.download_button(
        "Baixar CSV", data=csv,
        file_name=f"pedidos_{f.inicio:%Y%m%d}_{f.fim:%Y%m%d}.csv",
        mime="text/csv", icon=":material/download:",
    )

st.caption(
    f"Receita exata no período: **{brl(kpis.receita_centavos)}** · "
    "pedidos cancelados não entram na receita."
)
