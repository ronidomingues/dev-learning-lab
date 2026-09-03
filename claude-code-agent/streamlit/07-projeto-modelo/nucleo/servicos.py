"""Regras de negócio e agregações.

A camada que a interface chama. Recebe tipos simples (datas, tuplas de string),
devolve DataFrames e dataclasses. Nenhuma linha de `streamlit` aqui — é isso que
faz `testes/test_servicos.py` rodar em milissegundos, sem navegador nem servidor.

Nota de arquitetura: as agregações são feitas em **SQL/pandas sobre o conjunto
já filtrado**, e o filtro é aplicado no banco, não em Python. Trazer 2 milhões
de linhas para filtrar no pandas é o erro de desempenho nº 1 de painel em
Streamlit — e o motivo mais comum do "app has gone over its resource limits".
"""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

import pandas as pd

from nucleo import repositorio
from nucleo.modelos import KPIs

COLUNAS_PEDIDO = [
    "id", "data", "status", "canal", "quantidade", "valor_centavos",
    "cliente_id", "cliente", "segmento", "uf", "produto_id", "produto", "categoria",
]


def _vazio() -> pd.DataFrame:
    """DataFrame vazio com as colunas e os tipos certos.

    Sem isto, um período sem pedidos derruba o painel com KeyError na primeira
    coluna acessada. 'Sem dados' é um estado normal, não uma exceção.
    """
    df = pd.DataFrame({c: pd.Series(dtype="object") for c in COLUNAS_PEDIDO})
    df["data"] = pd.to_datetime(df["data"])
    for c in ("quantidade", "valor_centavos", "id", "cliente_id", "produto_id"):
        df[c] = df[c].astype("int64")
    df["valor"] = pd.Series(dtype="float64")
    return df


def carregar_pedidos(
    caminho: Path,
    inicio: date,
    fim: date,
    status: tuple[str, ...] = (),
    canais: tuple[str, ...] = (),
    segmentos: tuple[str, ...] = (),
) -> pd.DataFrame:
    """Pedidos do período como DataFrame, já com `valor` em reais (float, só para exibir)."""
    linhas = repositorio.buscar_pedidos(
        caminho, inicio=inicio, fim=fim, status=status, canais=canais, segmentos=segmentos
    )
    if not linhas:
        return _vazio()
    df = pd.DataFrame(linhas)
    df["data"] = pd.to_datetime(df["data"])
    # `valor` é derivado e serve só para gráfico e exibição.
    # A conta continua sendo feita em `valor_centavos` (inteiro).
    df["valor"] = df["valor_centavos"] / 100.0
    return df


def periodo_anterior(inicio: date, fim: date) -> tuple[date, date]:
    """Janela imediatamente anterior, do mesmo tamanho. É o que dá sentido ao 'delta'."""
    dias = (fim - inicio).days + 1
    return inicio - timedelta(days=dias), inicio - timedelta(days=1)


def _variacao(atual: float, anterior: float) -> float | None:
    """Variação relativa. None quando não há base — mostrar '+100%' contra zero é mentira."""
    if anterior == 0:
        return None
    return (atual - anterior) / anterior


def calcular_kpis(atual: pd.DataFrame, anterior: pd.DataFrame) -> KPIs:
    """Os quatro números do topo, comparados com o período anterior.

    Regra de negócio explícita: pedido 'cancelado' não conta como receita.
    Deixar isso claro num único lugar evita o clássico 'o painel bate com o
    financeiro em janeiro e não bate em fevereiro'.
    """
    def agrega(df: pd.DataFrame) -> tuple[int, int, int, int]:
        val = df[df["status"] != "cancelado"] if len(df) else df
        receita = int(val["valor_centavos"].sum()) if len(val) else 0
        pedidos = int(len(val))
        ticket = receita // pedidos if pedidos else 0
        clientes = int(val["cliente_id"].nunique()) if len(val) else 0
        return receita, pedidos, ticket, clientes

    r1, p1, t1, c1 = agrega(atual)
    r0, p0, t0, c0 = agrega(anterior)
    return KPIs(
        receita_centavos=r1, pedidos=p1, ticket_medio_centavos=t1, clientes_ativos=c1,
        var_receita=_variacao(r1, r0), var_pedidos=_variacao(p1, p0),
        var_ticket=_variacao(t1, t0), var_clientes=_variacao(c1, c0),
    )


def serie_temporal(df: pd.DataFrame, granularidade: str = "D") -> pd.DataFrame:
    """Receita por dia/semana/mês. `granularidade`: 'D', 'W' ou 'ME'."""
    if df.empty:
        return pd.DataFrame({"data": pd.Series(dtype="datetime64[ns]"),
                             "valor": pd.Series(dtype="float64")})
    val = df[df["status"] != "cancelado"]
    if val.empty:
        return pd.DataFrame({"data": pd.Series(dtype="datetime64[ns]"),
                             "valor": pd.Series(dtype="float64")})
    s = (val.set_index("data")["valor"].resample(granularidade).sum())
    return s.reset_index().rename(columns={0: "valor"})


def ranking(df: pd.DataFrame, coluna: str, n: int = 10) -> pd.DataFrame:
    """Top N por receita numa dimensão qualquer (cliente, produto, categoria...)."""
    if df.empty or coluna not in df.columns:
        return pd.DataFrame({coluna: [], "valor": []})
    val = df[df["status"] != "cancelado"]
    if val.empty:
        return pd.DataFrame({coluna: [], "valor": []})
    return (val.groupby(coluna, as_index=False)["valor"].sum()
               .sort_values("valor", ascending=False).head(n))


def composicao_por_status(df: pd.DataFrame) -> pd.DataFrame:
    """Contagem e valor por status — inclusive cancelado, que aqui interessa ver."""
    if df.empty:
        return pd.DataFrame({"status": [], "pedidos": [], "valor": []})
    g = df.groupby("status", as_index=False).agg(pedidos=("id", "count"), valor=("valor", "sum"))
    return g.sort_values("valor", ascending=False)


def matriz_canal_segmento(df: pd.DataFrame) -> pd.DataFrame:
    """Tabela cruzada canal × segmento (receita). Entra num heatmap."""
    if df.empty:
        return pd.DataFrame()
    val = df[df["status"] != "cancelado"]
    if val.empty:
        return pd.DataFrame()
    return val.pivot_table(index="canal", columns="segmento", values="valor",
                           aggfunc="sum", fill_value=0.0)


def validar_pedido(dados: dict) -> list[str]:
    """Valida antes de gravar. Devolve a lista de problemas (vazia = tudo certo).

    Validar no serviço, e não no formulário, é o que garante que a regra vale
    também para a importação de CSV, para a API e para o script de carga.
    """
    from nucleo.modelos import CANAIS, STATUS

    erros: list[str] = []
    if not dados.get("cliente_id"):
        erros.append("Selecione um cliente.")
    if not dados.get("produto_id"):
        erros.append("Selecione um produto.")
    if int(dados.get("quantidade", 0)) <= 0:
        erros.append("A quantidade precisa ser maior que zero.")
    if int(dados.get("valor_centavos", -1)) < 0:
        erros.append("O valor não pode ser negativo.")
    if dados.get("status") not in STATUS:
        erros.append(f"Status inválido. Use um de: {', '.join(STATUS)}.")
    if dados.get("canal") not in CANAIS:
        erros.append(f"Canal inválido. Use um de: {', '.join(CANAIS)}.")
    if isinstance(dados.get("data"), str) and not dados["data"]:
        erros.append("Informe a data.")
    return erros
