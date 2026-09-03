"""Gera dados de demonstração determinísticos.

Determinístico de propósito (`random.Random(42)`): o painel do seu computador é
igual ao da apresentação, e o teste que confere um total não quebra amanhã.
"""

from __future__ import annotations

import random
from datetime import date, timedelta
from pathlib import Path

from nucleo import auth
from nucleo.db import conexao, migrar, transacao

SEGMENTOS = ["Varejo", "Indústria", "Serviços", "Governo", "Educação"]
UFS = ["SP", "RJ", "MG", "RS", "PR", "BA", "PE", "SC", "GO", "CE"]
CANAIS = ["site", "telefone", "parceiro", "representante"]
STATUS_PESOS = [("faturado", 55), ("confirmado", 25), ("rascunho", 12), ("cancelado", 8)]

PRODUTOS = [
    ("Licença Básica", "Software", 19_900),
    ("Licença Pro", "Software", 49_900),
    ("Licença Enterprise", "Software", 249_900),
    ("Suporte 8x5", "Serviço", 89_900),
    ("Suporte 24x7", "Serviço", 189_900),
    ("Treinamento Turma", "Serviço", 349_900),
    ("Consultoria (dia)", "Serviço", 280_000),
    ("Servidor Edge", "Hardware", 1_290_000),
    ("Sensor IoT", "Hardware", 34_900),
    ("Gateway IoT", "Hardware", 189_000),
]


def ja_populado(caminho: Path) -> bool:
    con = conexao(caminho)
    try:
        return con.execute("SELECT COUNT(*) FROM pedidos").fetchone()[0] > 0
    except Exception:
        return False


def popular(caminho: Path, *, dias: int = 400, pedidos: int = 4000,
            iteracoes_hash: int = 240_000, semente: int = 42) -> None:
    """Cria esquema, usuários, clientes, produtos e pedidos. Idempotente."""
    migrar(caminho)
    if ja_populado(caminho):
        return

    rnd = random.Random(semente)
    hoje = date.today()

    with transacao(caminho) as con:
        for i in range(1, 121):
            con.execute(
                "INSERT INTO clientes (nome, segmento, uf, observacao, criado_em) VALUES (?,?,?,?,?)",
                (f"Cliente {i:03d}", rnd.choice(SEGMENTOS), rnd.choice(UFS), "",
                 (hoje - timedelta(days=rnd.randint(400, 1200))).isoformat()),
            )
        for nome, cat, preco in PRODUTOS:
            con.execute(
                "INSERT INTO produtos (nome, categoria, preco_centavos) VALUES (?,?,?)",
                (nome, cat, preco),
            )

        status_pool = [s for s, peso in STATUS_PESOS for _ in range(peso)]
        for _ in range(pedidos):
            dia = hoje - timedelta(days=rnd.randint(0, dias))
            # Sazonalidade fabricada: fim de mês e fim de ano vendem mais.
            if dia.day > 25 and rnd.random() < 0.35:
                qtd = rnd.randint(2, 8)
            else:
                qtd = rnd.randint(1, 4)
            produto_id = rnd.randint(1, len(PRODUTOS))
            preco = PRODUTOS[produto_id - 1][2]
            desconto = rnd.choice([1.0, 1.0, 1.0, 0.95, 0.9, 0.85])
            con.execute(
                """INSERT INTO pedidos (cliente_id, produto_id, quantidade, valor_centavos, status, canal, data)
                   VALUES (?,?,?,?,?,?,?)""",
                (rnd.randint(1, 120), produto_id, qtd, int(preco * qtd * desconto),
                 rnd.choice(status_pool), rnd.choice(CANAIS), dia.isoformat()),
            )

    # Usuários de demonstração — senhas fracas de propósito, é uma demo local.
    for email, nome, senha, papel in [
        ("admin@exemplo.com", "Ana Admin", "admin123", "admin"),
        ("analista@exemplo.com", "Bruno Analista", "analista123", "analista"),
        ("leitor@exemplo.com", "Carla Leitora", "leitor123", "leitor"),
    ]:
        auth.criar_usuario(caminho, email=email, nome=nome, senha=senha,
                           papel=papel, iteracoes=iteracoes_hash)
