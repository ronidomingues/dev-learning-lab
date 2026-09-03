"""Peças compartilhadas entre as páginas: cache, filtros, guarda de permissão.

Módulo interno (prefixo `_`): não é uma página, é apoio.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
import streamlit as st

from nucleo import repositorio, servicos
from nucleo.modelos import STATUS, Usuario


# ---------------------------------------------------------------------------
# Cache
#
# `st.cache_data` guarda o VALOR de retorno, indexado pelo hash dos argumentos.
# Como a assinatura inclui o período e os filtros, trocar um filtro é uma chave
# nova (busca no banco); voltar ao filtro anterior é acerto de cache (instantâneo).
#
# ttl=300: dado de vendas pode ficar 5 minutos velho sem prejuízo. Cache sem TTL
# em painel operacional é o motivo nº 1 de "o número está errado" — está velho.
# ---------------------------------------------------------------------------
@st.cache_data(ttl=300, show_spinner="Consultando pedidos...", show_time=True)
def pedidos_em_cache(
    caminho: Path, inicio: date, fim: date,
    status: tuple[str, ...], canais: tuple[str, ...], segmentos: tuple[str, ...],
) -> pd.DataFrame:
    return servicos.carregar_pedidos(caminho, inicio, fim, status, canais, segmentos)


@st.cache_data(ttl=600)
def opcoes_em_cache(caminho: Path, coluna: str) -> list[str]:
    return repositorio.valores_distintos(caminho, coluna)


@st.cache_data(ttl=600)
def clientes_em_cache(caminho: Path) -> list[tuple[int, str]]:
    return [(c.id, c.nome) for c in repositorio.listar_clientes(caminho)]


@st.cache_data(ttl=600)
def produtos_em_cache(caminho: Path) -> list[tuple[int, str, int]]:
    return [(p.id, p.nome, p.preco_centavos) for p in repositorio.listar_produtos(caminho)]


def invalidar_cache_de_pedidos() -> None:
    """Depois de gravar, o cache mente. Limpe só o que ficou velho."""
    pedidos_em_cache.clear()


# ---------------------------------------------------------------------------
# Filtros
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Filtros:
    inicio: date
    fim: date
    status: tuple[str, ...]
    canais: tuple[str, ...]
    segmentos: tuple[str, ...]

    @property
    def dias(self) -> int:
        return (self.fim - self.inicio).days + 1


ATALHOS = {"7 dias": 7, "30 dias": 30, "90 dias": 90, "12 meses": 365}


def barra_de_filtros(caminho: Path) -> Filtros:
    """Filtros na barra lateral, com estado ligado à URL.

    `bind="query-params"` (Streamlit ≥ 1.55) grava o valor do widget na query
    string. Consequência prática: o usuário copia a URL, manda no chat, e o
    colega abre o painel JÁ FILTRADO. Sem isso, todo painel compartilhado vira
    "filtra ali em cima, últimos 90 dias, canal parceiro".
    """
    with st.sidebar:
        st.markdown("#### Filtros")

        hoje = date.today()

        def _aplicar_atalho() -> None:
            """Callback do atalho: escreve a data no estado do OUTRO widget.

            Callback (`on_change`) roda ANTES do rerun, então o `st.date_input`
            abaixo já lê o valor novo. Tentar fazer isso depois — atribuir a
            `st.session_state["f_intervalo"]` no corpo do script, após o widget
            existir — levanta StreamlitAPIException. Essa é a regra que mais
            confunde: só callback e código antes do widget podem escrever a
            chave dele.
            """
            dias = ATALHOS.get(st.session_state.get("f_atalho") or "90 dias", 90)
            st.session_state["f_intervalo"] = (hoje - timedelta(days=dias - 1), hoje)

        st.segmented_control(
            "Período", list(ATALHOS), default="90 dias", key="f_atalho",
            on_change=_aplicar_atalho, bind="query-params",
            label_visibility="collapsed", width="stretch",
        )
        padrao_inicio = hoje - timedelta(days=ATALHOS.get(st.session_state.get("f_atalho") or "90 dias", 90) - 1)

        intervalo = st.date_input(
            "Intervalo", value=(padrao_inicio, hoje), max_value=hoje,
            format="DD/MM/YYYY", key="f_intervalo",
        )
        # date_input com `value=(a, b)` devolve tupla de 1 elemento enquanto o
        # usuário escolheu só a primeira data. Ignorar isso quebra a página.
        if isinstance(intervalo, (tuple, list)) and len(intervalo) == 2:
            inicio, fim = intervalo
        else:
            inicio, fim = padrao_inicio, hoje

        status = st.multiselect("Status", STATUS, default=["confirmado", "faturado"],
                                key="f_status", bind="query-params")
        canais = st.multiselect("Canal", opcoes_em_cache(caminho, "canal"),
                                key="f_canal", bind="query-params")
        segmentos = st.multiselect("Segmento", opcoes_em_cache(caminho, "segmento"),
                                   key="f_segmento", bind="query-params")

        st.divider()
        st.caption(f"Período: {inicio.strftime('%d/%m/%Y')} a {fim.strftime('%d/%m/%Y')}")

    return Filtros(inicio=inicio, fim=fim, status=tuple(status),
                   canais=tuple(canais), segmentos=tuple(segmentos))


# ---------------------------------------------------------------------------
# Guarda de permissão
# ---------------------------------------------------------------------------
def exigir(papeis: tuple[str, ...]) -> Usuario:
    """Interrompe a página se o usuário não tiver papel suficiente.

    Chame no TOPO da página. `st.stop()` encerra o rerun; nada abaixo executa.
    Esconder o botão não é controle de acesso — a página inteira precisa parar.
    """
    u: Usuario | None = st.session_state.get("usuario")
    if u is None:
        st.error("Sessão expirada. Recarregue a página.", icon=":material/lock:")
        st.stop()
    if u.papel not in papeis:
        st.error(
            f"Acesso negado. Esta página exige um destes papéis: {', '.join(papeis)}. "
            f"O seu é '{u.papel}'.",
            icon=":material/block:",
        )
        st.stop()
    return u


def usuario_atual() -> Usuario:
    u = st.session_state.get("usuario")
    if u is None:
        st.error("Sessão expirada. Recarregue a página.", icon=":material/lock:")
        st.stop()
    return u
