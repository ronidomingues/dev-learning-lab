"""Acesso a dados. Só aqui existe SQL.

Por que isolar: o dia em que o SQLite virar PostgreSQL, você edita este arquivo
e mais nada. E os testes podem trocar o repositório por um falso sem tocar na UI.

Todo SQL usa **parâmetros ligados** (`?`), nunca f-string. Concatenar entrada do
usuário em SQL é injeção de SQL — o buraco de segurança nº 1 de app de dados.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

from nucleo.db import conexao, transacao
from nucleo.modelos import Cliente, Pedido, Produto

# --------------------------------------------------------------------------
# Leitura
# --------------------------------------------------------------------------

def listar_clientes(caminho: Path) -> list[Cliente]:
    linhas = conexao(caminho).execute(
        "SELECT id, nome, segmento, uf, observacao FROM clientes ORDER BY nome"
    ).fetchall()
    return [Cliente(**dict(l)) for l in linhas]


def listar_produtos(caminho: Path) -> list[Produto]:
    linhas = conexao(caminho).execute(
        "SELECT id, nome, categoria, preco_centavos FROM produtos ORDER BY nome"
    ).fetchall()
    return [Produto(**dict(l)) for l in linhas]


def buscar_pedidos(
    caminho: Path,
    *,
    inicio: date,
    fim: date,
    status: tuple[str, ...] = (),
    canais: tuple[str, ...] = (),
    segmentos: tuple[str, ...] = (),
    limite: int | None = None,
) -> list[dict[str, Any]]:
    """Pedidos do período, já com nome do cliente e do produto (JOIN).

    Filtros opcionais viram cláusulas só quando preenchidos. Repare que o número
    de `?` é gerado a partir do tamanho da tupla — o valor nunca entra no texto.
    """
    sql = [
        """SELECT p.id, p.data, p.status, p.canal, p.quantidade, p.valor_centavos,
                  c.id AS cliente_id, c.nome AS cliente, c.segmento, c.uf,
                  pr.id AS produto_id, pr.nome AS produto, pr.categoria
           FROM pedidos p
           JOIN clientes c  ON c.id  = p.cliente_id
           JOIN produtos pr ON pr.id = p.produto_id
           WHERE p.data BETWEEN ? AND ?"""
    ]
    args: list[Any] = [inicio.isoformat(), fim.isoformat()]

    if status:
        sql.append(f"AND p.status IN ({','.join('?' * len(status))})")
        args += list(status)
    if canais:
        sql.append(f"AND p.canal IN ({','.join('?' * len(canais))})")
        args += list(canais)
    if segmentos:
        sql.append(f"AND c.segmento IN ({','.join('?' * len(segmentos))})")
        args += list(segmentos)

    sql.append("ORDER BY p.data DESC, p.id DESC")
    if limite is not None:
        sql.append("LIMIT ?")
        args.append(limite)

    linhas = conexao(caminho).execute(" ".join(sql), args).fetchall()
    return [dict(l) for l in linhas]


def valores_distintos(caminho: Path, coluna: str) -> list[str]:
    """Valores para preencher filtros. `coluna` é validada contra uma lista fixa —
    nome de coluna NÃO pode ser parâmetro ligado, então tem que ser lista branca."""
    permitidas = {
        "canal": "SELECT DISTINCT canal FROM pedidos ORDER BY canal",
        "segmento": "SELECT DISTINCT segmento FROM clientes ORDER BY segmento",
        "categoria": "SELECT DISTINCT categoria FROM produtos ORDER BY categoria",
        "uf": "SELECT DISTINCT uf FROM clientes ORDER BY uf",
    }
    if coluna not in permitidas:
        raise ValueError(f"coluna '{coluna}' não permitida")
    return [l[0] for l in conexao(caminho).execute(permitidas[coluna]).fetchall()]


# --------------------------------------------------------------------------
# Escrita
# --------------------------------------------------------------------------

def inserir_pedido(caminho: Path, pedido: dict[str, Any]) -> int:
    with transacao(caminho) as con:
        cur = con.execute(
            """INSERT INTO pedidos (cliente_id, produto_id, quantidade, valor_centavos, status, canal, data)
               VALUES (:cliente_id, :produto_id, :quantidade, :valor_centavos, :status, :canal, :data)""",
            pedido,
        )
        return int(cur.lastrowid)


def atualizar_pedido(caminho: Path, pedido_id: int, campos: dict[str, Any]) -> int:
    """Atualização parcial. Só as colunas da lista branca podem ser escritas."""
    permitidas = {"quantidade", "valor_centavos", "status", "canal", "data", "cliente_id", "produto_id"}
    desconhecidas = set(campos) - permitidas
    if desconhecidas:
        raise ValueError(f"campos não permitidos: {sorted(desconhecidas)}")
    if not campos:
        return 0
    atrib = ", ".join(f"{c} = :{c}" for c in campos)
    with transacao(caminho) as con:
        cur = con.execute(
            f"UPDATE pedidos SET {atrib} WHERE id = :id", {**campos, "id": pedido_id}
        )
        return cur.rowcount


def excluir_pedido(caminho: Path, pedido_id: int) -> int:
    with transacao(caminho) as con:
        return con.execute("DELETE FROM pedidos WHERE id = ?", (pedido_id,)).rowcount


def inserir_cliente(caminho: Path, cliente: dict[str, Any]) -> int:
    with transacao(caminho) as con:
        cur = con.execute(
            """INSERT INTO clientes (nome, segmento, uf, observacao, criado_em)
               VALUES (:nome, :segmento, :uf, :observacao, :criado_em)""",
            cliente,
        )
        return int(cur.lastrowid)


def registrar_auditoria(caminho: Path, *, ator: str, acao: str, detalhe: str) -> None:
    from datetime import datetime, timezone

    with transacao(caminho) as con:
        con.execute(
            "INSERT INTO auditoria (quando, ator, acao, detalhe) VALUES (?,?,?,?)",
            (datetime.now(timezone.utc).isoformat(timespec="seconds"), ator, acao, detalhe),
        )


def listar_auditoria(caminho: Path, limite: int = 200) -> list[dict[str, Any]]:
    linhas = conexao(caminho).execute(
        "SELECT quando, ator, acao, detalhe FROM auditoria ORDER BY id DESC LIMIT ?",
        (limite,),
    ).fetchall()
    return [dict(l) for l in linhas]
