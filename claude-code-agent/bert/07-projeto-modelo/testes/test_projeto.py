"""Testes do projeto.

    pytest -q

Os testes de dados e de tokenização rodam sempre (segundos, sem GPU, sem modelo
treinado). Os de predição são pulados automaticamente se ainda não houver modelo
treinado — assim `pytest` nunca falha por um motivo que não é culpa do código.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config import config  # noqa: E402

MODELO_TREINADO = config.dir_saida.exists()
pular_sem_modelo = pytest.mark.skipif(
    not MODELO_TREINADO, reason="modelo ainda não treinado — rode `python treinar.py`"
)


# --------------------------------------------------------------------------
# Dados: o teste mais barato e o que mais evita desastre
# --------------------------------------------------------------------------
def test_csv_existe_e_tem_as_colunas():
    assert config.caminho_dados.exists(), f"faltando: {config.caminho_dados}"
    df = pd.read_csv(config.caminho_dados)
    assert {config.coluna_texto, config.coluna_rotulo} <= set(df.columns)


def test_rotulos_sao_apenas_os_esperados():
    df = pd.read_csv(config.caminho_dados)
    encontrados = set(df[config.coluna_rotulo].str.strip().str.upper())
    assert encontrados == set(config.categorias), f"rótulos inesperados: {encontrados}"


def test_sem_texto_duplicado():
    """Duplicata é vazamento: o mesmo texto em treino e teste infla a métrica."""
    df = pd.read_csv(config.caminho_dados)
    duplicados = df[df[config.coluna_texto].str.strip().duplicated()]
    assert duplicados.empty, f"textos duplicados: {duplicados[config.coluna_texto].tolist()}"


def test_todas_as_classes_tem_exemplos_suficientes():
    df = pd.read_csv(config.caminho_dados)
    contagem = df[config.coluna_rotulo].value_counts()
    assert contagem.min() >= 10, f"classe com poucos exemplos: {contagem.to_dict()}"


# --------------------------------------------------------------------------
# Tokenização: não depende de treino
# --------------------------------------------------------------------------
def test_tokenizacao_respeita_o_limite():
    from transformers import AutoTokenizer

    tok = AutoTokenizer.from_pretrained(config.modelo_base)
    texto_longo = "palavra " * 1000
    ids = tok(texto_longo, truncation=True, max_length=config.max_tokens)["input_ids"]
    assert len(ids) == config.max_tokens
    assert ids[0] == tok.cls_token_id and ids[-1] == tok.sep_token_id


# --------------------------------------------------------------------------
# Predição: só com modelo treinado
# --------------------------------------------------------------------------
@pular_sem_modelo
def test_predicao_devolve_categoria_valida():
    from prever import prever

    p = prever("minha fatura veio com valor errado")
    assert p.categoria in config.categorias
    assert 0.0 <= p.confianca <= 1.0
    assert abs(sum(p.probabilidades.values()) - 1.0) < 1e-3


@pular_sem_modelo
@pytest.mark.parametrize(
    "texto,esperado",
    [
        ("recebi cobrança em duplicidade no cartão", "FINANCEIRO"),
        ("o site fica fora do ar e dá erro 500", "TECNICO"),
        ("quero contratar mais licenças para a equipe", "COMERCIAL"),
        ("solicito o cancelamento imediato do contrato", "CANCELAMENTO"),
    ],
)
def test_acerta_casos_obvios(texto, esperado):
    """Teste de fumaça semântica: se o modelo erra ISTO, algo está muito errado."""
    from prever import prever

    assert prever(texto).categoria == esperado


@pular_sem_modelo
def test_texto_vazio_gera_erro_claro():
    from prever import prever

    with pytest.raises(ValueError):
        prever("   ")
