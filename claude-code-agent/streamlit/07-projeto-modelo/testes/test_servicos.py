"""Testes do NÚCLEO — sem Streamlit, sem navegador. Rodam em milissegundos.

É este arquivo que justifica a separação `nucleo/` × `paginas/`: 90% das regras
que podem estar erradas moram aqui, e aqui elas são baratas de testar.
"""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

import pandas as pd
import pytest

from nucleo import auth, config, repositorio, servicos
from nucleo.db import migrar, versao_atual, conexao


# --- esquema ---------------------------------------------------------------
def test_migracao_e_idempotente(tmp_path: Path):
    caminho = tmp_path / "m.db"
    assert migrar(caminho) == migrar(caminho)          # rodar duas vezes não muda nada
    assert versao_atual(conexao(caminho)) == migrar(caminho)


def test_chave_estrangeira_esta_ligada(banco: Path):
    """SQLite ignora FOREIGN KEY por padrão. Se este teste passar, o PRAGMA pegou."""
    import sqlite3
    with pytest.raises(sqlite3.IntegrityError):
        repositorio.inserir_pedido(banco, dict(
            cliente_id=999999, produto_id=1, quantidade=1, valor_centavos=100,
            status="confirmado", canal="site", data=date.today().isoformat()))


# --- autenticação ----------------------------------------------------------
def test_senha_correta_autentica(banco: Path):
    u = auth.autenticar(banco, "admin@exemplo.com", "admin123")
    assert u.papel == "admin" and u.pode_administrar()


def test_senha_errada_recusa(banco: Path):
    with pytest.raises(auth.ErroDeLogin):
        auth.autenticar(banco, "admin@exemplo.com", "errada")


def test_email_inexistente_da_a_mesma_mensagem(banco: Path):
    """Não contar ao atacante quais e-mails existem."""
    with pytest.raises(auth.ErroDeLogin) as a:
        auth.autenticar(banco, "ninguem@exemplo.com", "x")
    with pytest.raises(auth.ErroDeLogin) as b:
        auth.autenticar(banco, "admin@exemplo.com", "x")
    assert str(a.value) == str(b.value)


def test_hash_muda_com_salt(banco: Path):
    h1, s1 = auth.gerar_hash("mesma-senha", 100_000)
    h2, s2 = auth.gerar_hash("mesma-senha", 100_000)
    assert s1 != s2 and h1 != h2       # dois usuários com a mesma senha têm hashes diferentes


def test_papel_leitor_nao_edita(banco: Path):
    assert not auth.autenticar(banco, "leitor@exemplo.com", "leitor123").pode_editar()
    assert auth.autenticar(banco, "analista@exemplo.com", "analista123").pode_editar()


# --- injeção de SQL --------------------------------------------------------
def test_filtro_com_aspas_nao_quebra_nem_injeta(banco: Path):
    """A entrada clássica de injeção entra como VALOR e não acontece nada."""
    hoje = date.today()
    linhas = repositorio.buscar_pedidos(
        banco, inicio=hoje - timedelta(days=365), fim=hoje,
        canais=("site'; DROP TABLE pedidos; --",))
    assert linhas == []
    assert conexao(banco).execute("SELECT COUNT(*) FROM pedidos").fetchone()[0] > 0


def test_coluna_fora_da_lista_branca_e_recusada(banco: Path):
    with pytest.raises(ValueError):
        repositorio.valores_distintos(banco, "usuarios; --")


def test_atualizacao_recusa_coluna_desconhecida(banco: Path):
    with pytest.raises(ValueError):
        repositorio.atualizar_pedido(banco, 1, {"senha_hash": b"x"})


# --- regras de negócio -----------------------------------------------------
def test_cancelado_nao_entra_na_receita(cfg: config.Config):
    hoje = date.today()
    df = servicos.carregar_pedidos(cfg.caminho_banco, hoje - timedelta(days=365), hoje)
    k = servicos.calcular_kpis(df, df.iloc[0:0])
    esperado = int(df[df["status"] != "cancelado"]["valor_centavos"].sum())
    assert k.receita_centavos == esperado
    assert k.receita_centavos < int(df["valor_centavos"].sum())   # havia cancelados


def test_periodo_anterior_tem_o_mesmo_tamanho():
    ini, fim = date(2026, 3, 1), date(2026, 3, 31)
    a, b = servicos.periodo_anterior(ini, fim)
    assert (b - a).days == (fim - ini).days
    assert b == ini - timedelta(days=1)          # encosta, não sobrepõe


def test_variacao_sem_base_e_none(cfg: config.Config):
    vazio = servicos.carregar_pedidos(cfg.caminho_banco, date(1990, 1, 1), date(1990, 1, 2))
    k = servicos.calcular_kpis(vazio, vazio)
    assert k.var_receita is None                 # não inventar "+100%" contra zero


def test_periodo_sem_dados_nao_quebra(cfg: config.Config):
    df = servicos.carregar_pedidos(cfg.caminho_banco, date(1990, 1, 1), date(1990, 1, 2))
    assert df.empty and list(df.columns)[:3] == ["id", "data", "status"]
    assert servicos.serie_temporal(df).empty
    assert servicos.ranking(df, "cliente").empty
    assert servicos.matriz_canal_segmento(df).empty


def test_ticket_medio_e_receita_sobre_pedidos(cfg: config.Config):
    hoje = date.today()
    df = servicos.carregar_pedidos(cfg.caminho_banco, hoje - timedelta(days=90), hoje)
    k = servicos.calcular_kpis(df, df.iloc[0:0])
    assert k.ticket_medio_centavos == k.receita_centavos // k.pedidos


def test_dinheiro_e_inteiro_do_comeco_ao_fim(cfg: config.Config):
    """Regressão do erro clássico: somar float e perder centavos."""
    hoje = date.today()
    df = servicos.carregar_pedidos(cfg.caminho_banco, hoje - timedelta(days=365), hoje)
    assert df["valor_centavos"].dtype.kind == "i"
    k = servicos.calcular_kpis(df, df.iloc[0:0])
    assert isinstance(k.receita_centavos, int)


def test_validacao_pega_os_erros(cfg: config.Config):
    erros = servicos.validar_pedido({"cliente_id": 0, "produto_id": None, "quantidade": 0,
                                     "valor_centavos": -5, "status": "xx", "canal": "yy"})
    assert len(erros) == 6


def test_serie_temporal_agrega_por_mes(cfg: config.Config):
    hoje = date.today()
    df = servicos.carregar_pedidos(cfg.caminho_banco, hoje - timedelta(days=120), hoje)
    mensal = servicos.serie_temporal(df, "ME")
    diaria = servicos.serie_temporal(df, "D")
    assert len(mensal) < len(diaria)
    assert round(mensal["valor"].sum(), 2) == round(diaria["valor"].sum(), 2)


# --- transação -------------------------------------------------------------
def test_transacao_desfaz_tudo_em_caso_de_erro(banco: Path):
    from nucleo.db import transacao
    antes = conexao(banco).execute("SELECT COUNT(*) FROM pedidos").fetchone()[0]
    with pytest.raises(RuntimeError):
        with transacao(banco) as con:
            con.execute("""INSERT INTO pedidos (cliente_id,produto_id,quantidade,
                           valor_centavos,status,canal,data) VALUES (1,1,1,100,'confirmado','site',?)""",
                        (date.today().isoformat(),))
            raise RuntimeError("falha no meio da operação")
    assert conexao(banco).execute("SELECT COUNT(*) FROM pedidos").fetchone()[0] == antes


# --- configuração ----------------------------------------------------------
def test_config_recusa_ambiente_invalido():
    with pytest.raises(config.ErroDeConfiguracao):
        config.carregar({"PAINEL_AMBIENTE": "producao"})


def test_config_recusa_hash_fraco():
    with pytest.raises(config.ErroDeConfiguracao):
        config.carregar({"PAINEL_HASH_ITER": "1000"})


# --- formatação ------------------------------------------------------------
@pytest.mark.parametrize("centavos,esperado", [
    (0, "R$ 0,00"), (5, "R$ 0,05"), (100, "R$ 1,00"),
    (123456789, "R$ 1.234.567,89"), (-2550, "R$ -25,50"),
])
def test_formato_brl(centavos, esperado):
    from ui.formatos import brl
    assert brl(centavos) == esperado


def test_percentual_none_continua_none():
    from ui.formatos import percentual
    assert percentual(None) is None
    assert percentual(0.1234) == "+12,3%"
    assert percentual(-0.05) == "-5,0%"
