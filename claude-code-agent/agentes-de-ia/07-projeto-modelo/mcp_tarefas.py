#!/usr/bin/env python3
"""
Servidor MCP (Model Context Protocol) mínimo, sem nenhuma dependência externa.

Expõe quatro ferramentas sobre um banco SQLite de tarefas:
  - listar_tarefas(status?)
  - criar_tarefa(titulo, prioridade?)
  - concluir_tarefa(id)
  - estatisticas()

Por que escrever o protocolo na mão em vez de usar o SDK oficial?
Porque o objetivo aqui é didático: MCP é JSON-RPC 2.0 sobre stdin/stdout.
Ver o protocolo cru elimina a caixa-preta. Em produção, use o SDK
(`pip install mcp`) — ele cuida de reconexão, cancelamento e schemas.

Transporte: stdio. Uma mensagem JSON por linha (JSON-RPC 2.0).
Versão do protocolo implementada: 2025-06-18 (negociada no `initialize`).
"""

from __future__ import annotations

import json
import os
import sqlite3
import sys
from typing import Any

PROTOCOL_VERSION = "2025-06-18"
SERVER_NAME = "tarefas"
SERVER_VERSION = "1.0.0"

# O banco fica ao lado do script, salvo se TAREFAS_DB apontar para outro lugar.
# Isso permite que o teste automatizado use um banco descartável.
DB_PATH = os.environ.get(
    "TAREFAS_DB",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "tarefas.db"),
)


# --------------------------------------------------------------------------
# Camada de domínio: nada aqui sabe o que é MCP. É código comum, testável.
# --------------------------------------------------------------------------

def conectar() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS tarefas (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo     TEXT    NOT NULL,
            prioridade TEXT    NOT NULL DEFAULT 'media',
            status     TEXT    NOT NULL DEFAULT 'aberta'
        )
        """
    )
    return conn


def listar_tarefas(status: str | None = None) -> str:
    with conectar() as conn:
        if status:
            linhas = conn.execute(
                "SELECT * FROM tarefas WHERE status = ? ORDER BY id", (status,)
            ).fetchall()
        else:
            linhas = conn.execute("SELECT * FROM tarefas ORDER BY id").fetchall()
    if not linhas:
        return "Nenhuma tarefa encontrada."
    return "\n".join(
        f"#{r['id']} [{r['status']}] ({r['prioridade']}) {r['titulo']}" for r in linhas
    )


def criar_tarefa(titulo: str, prioridade: str = "media") -> str:
    titulo = (titulo or "").strip()
    if not titulo:
        raise ValueError("titulo não pode ser vazio")
    if prioridade not in ("baixa", "media", "alta"):
        raise ValueError("prioridade deve ser baixa, media ou alta")
    with conectar() as conn:
        cur = conn.execute(
            "INSERT INTO tarefas (titulo, prioridade) VALUES (?, ?)",
            (titulo, prioridade),
        )
    return f"Tarefa #{cur.lastrowid} criada: {titulo} (prioridade {prioridade})"


def concluir_tarefa(id: int) -> str:
    with conectar() as conn:
        cur = conn.execute(
            "UPDATE tarefas SET status = 'concluida' WHERE id = ? AND status = 'aberta'",
            (id,),
        )
        if cur.rowcount == 0:
            raise ValueError(f"tarefa #{id} não existe ou já está concluída")
    return f"Tarefa #{id} concluída."


def estatisticas() -> str:
    with conectar() as conn:
        linhas = conn.execute(
            "SELECT status, COUNT(*) AS n FROM tarefas GROUP BY status"
        ).fetchall()
    if not linhas:
        return "Banco vazio."
    return "\n".join(f"{r['status']}: {r['n']}" for r in linhas)


# --------------------------------------------------------------------------
# Declaração das ferramentas.
#
# A `description` é o texto que o modelo lê para decidir SE e QUANDO chamar
# a ferramenta. É a parte mais importante e a mais negligenciada: descrição
# vaga = ferramenta ignorada ou usada errado. Diga quando usar, não só o que faz.
# --------------------------------------------------------------------------

FERRAMENTAS: list[dict[str, Any]] = [
    {
        "name": "listar_tarefas",
        "description": (
            "Lista as tarefas registradas. Use sempre antes de responder qualquer "
            "pergunta sobre o que está pendente, o que já foi feito ou quantas "
            "tarefas existem — nunca responda de memória. Opcionalmente filtra "
            "por status."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "enum": ["aberta", "concluida"],
                    "description": "Filtra por status. Omita para listar todas.",
                }
            },
            "required": [],
        },
        "_fn": listar_tarefas,
    },
    {
        "name": "criar_tarefa",
        "description": (
            "Cria uma nova tarefa. Use quando o usuário pedir para anotar, "
            "registrar ou lembrar de algo a fazer. Retorna o id atribuído."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "titulo": {
                    "type": "string",
                    "description": "Descrição curta da tarefa, em uma linha.",
                },
                "prioridade": {
                    "type": "string",
                    "enum": ["baixa", "media", "alta"],
                    "description": "Prioridade. Padrão: media.",
                },
            },
            "required": ["titulo"],
        },
        "_fn": criar_tarefa,
    },
    {
        "name": "concluir_tarefa",
        "description": (
            "Marca uma tarefa como concluída pelo seu id. Se você não souber o "
            "id, chame listar_tarefas antes. Falha se a tarefa não existir ou já "
            "estiver concluída."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "id": {"type": "integer", "description": "Id da tarefa."}
            },
            "required": ["id"],
        },
        "_fn": concluir_tarefa,
    },
    {
        "name": "estatisticas",
        "description": (
            "Retorna a contagem de tarefas por status. Use para responder "
            "perguntas de resumo sem precisar listar tudo."
        ),
        "inputSchema": {"type": "object", "properties": {}, "required": []},
        "_fn": estatisticas,
    },
]

POR_NOME = {f["name"]: f for f in FERRAMENTAS}


def catalogo_publico() -> list[dict[str, Any]]:
    """O `_fn` é detalhe interno: não vai no protocolo."""
    return [{k: v for k, v in f.items() if not k.startswith("_")} for f in FERRAMENTAS]


# --------------------------------------------------------------------------
# Camada MCP: despacho JSON-RPC 2.0.
# --------------------------------------------------------------------------

def tratar(msg: dict[str, Any]) -> dict[str, Any] | None:
    """Recebe uma mensagem JSON-RPC, devolve a resposta (ou None se for notificação)."""
    metodo = msg.get("method")
    id_ = msg.get("id")
    params = msg.get("params") or {}

    # Notificações não têm "id" e não recebem resposta.
    if id_ is None:
        return None

    def ok(resultado: Any) -> dict[str, Any]:
        return {"jsonrpc": "2.0", "id": id_, "result": resultado}

    def erro(codigo: int, mensagem: str) -> dict[str, Any]:
        return {"jsonrpc": "2.0", "id": id_, "error": {"code": codigo, "message": mensagem}}

    if metodo == "initialize":
        # Negociação: se o cliente pedir outra versão, ecoamos a dele quando
        # soubermos falar; aqui só falamos uma, então informamos a nossa.
        return ok(
            {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {"tools": {}},
                "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
            }
        )

    if metodo == "ping":
        return ok({})

    if metodo == "tools/list":
        return ok({"tools": catalogo_publico()})

    if metodo == "tools/call":
        nome = params.get("name")
        args = params.get("arguments") or {}
        ferramenta = POR_NOME.get(nome)
        if ferramenta is None:
            return erro(-32602, f"ferramenta desconhecida: {nome}")
        try:
            texto = ferramenta["_fn"](**args)
            return ok({"content": [{"type": "text", "text": texto}], "isError": False})
        except TypeError as e:
            # Argumentos errados: erro do protocolo, não do domínio.
            return erro(-32602, f"argumentos inválidos para {nome}: {e}")
        except Exception as e:
            # Erro de domínio: devolvido como RESULTADO com isError=True, e não
            # como erro JSON-RPC. Isso é deliberado — o modelo precisa LER a
            # mensagem para se corrigir. Um erro de protocolo aborta a chamada;
            # um isError=True vira contexto e o agente tenta outra coisa.
            return ok({"content": [{"type": "text", "text": f"Erro: {e}"}], "isError": True})

    return erro(-32601, f"método não implementado: {metodo}")


def main() -> None:
    for linha in sys.stdin:
        linha = linha.strip()
        if not linha:
            continue
        try:
            msg = json.loads(linha)
        except json.JSONDecodeError:
            continue
        resposta = tratar(msg)
        if resposta is not None:
            sys.stdout.write(json.dumps(resposta, ensure_ascii=False) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
