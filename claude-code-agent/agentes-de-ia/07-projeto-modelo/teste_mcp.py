#!/usr/bin/env python3
"""
Teste de contrato do servidor MCP.

Sobe `mcp_tarefas.py` como subprocesso, fala JSON-RPC 2.0 pela stdin/stdout
e verifica o handshake, o catálogo de ferramentas, uma chamada feliz e uma
chamada que falha.

Não precisa de chave de API nem de rede: exercita o servidor, não o modelo.
Rode assim:

    python3 teste_mcp.py
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile

AQUI = os.path.dirname(os.path.abspath(__file__))
SERVIDOR = os.path.join(AQUI, "mcp_tarefas.py")

falhas = 0


def verificar(condicao: bool, descricao: str) -> None:
    global falhas
    if condicao:
        print(f"  ok   {descricao}")
    else:
        falhas += 1
        print(f"  FALHA {descricao}")


class Cliente:
    """Cliente MCP mínimo sobre stdio."""

    def __init__(self, db_path: str) -> None:
        env = dict(os.environ, TAREFAS_DB=db_path)
        self.proc = subprocess.Popen(
            [sys.executable, SERVIDOR],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True,
            env=env,
            bufsize=1,
        )
        self._id = 0

    def chamar(self, metodo: str, params: dict | None = None) -> dict:
        self._id += 1
        msg = {"jsonrpc": "2.0", "id": self._id, "method": metodo}
        if params is not None:
            msg["params"] = params
        assert self.proc.stdin and self.proc.stdout
        self.proc.stdin.write(json.dumps(msg) + "\n")
        self.proc.stdin.flush()
        return json.loads(self.proc.stdout.readline())

    def notificar(self, metodo: str) -> None:
        assert self.proc.stdin
        self.proc.stdin.write(json.dumps({"jsonrpc": "2.0", "method": metodo}) + "\n")
        self.proc.stdin.flush()

    def fechar(self) -> None:
        assert self.proc.stdin
        self.proc.stdin.close()
        self.proc.wait(timeout=5)


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        cli = Cliente(os.path.join(tmp, "teste.db"))

        print("handshake")
        r = cli.chamar("initialize", {"protocolVersion": "2025-06-18",
                                      "capabilities": {},
                                      "clientInfo": {"name": "teste", "version": "0"}})
        verificar(r["result"]["serverInfo"]["name"] == "tarefas", "serverInfo.name = tarefas")
        verificar("tools" in r["result"]["capabilities"], "declara capability tools")
        cli.notificar("notifications/initialized")

        print("catálogo")
        r = cli.chamar("tools/list")
        nomes = {t["name"] for t in r["result"]["tools"]}
        verificar(
            nomes == {"listar_tarefas", "criar_tarefa", "concluir_tarefa", "estatisticas"},
            "quatro ferramentas publicadas",
        )
        verificar(
            all("_fn" not in t for t in r["result"]["tools"]),
            "detalhe interno _fn não vaza no protocolo",
        )
        verificar(
            all(t["description"].strip() for t in r["result"]["tools"]),
            "toda ferramenta tem descrição",
        )

        print("banco vazio")
        r = cli.chamar("tools/call", {"name": "listar_tarefas", "arguments": {}})
        verificar("Nenhuma tarefa" in r["result"]["content"][0]["text"], "lista vazia")

        print("caminho feliz")
        r = cli.chamar("tools/call", {"name": "criar_tarefa",
                                      "arguments": {"titulo": "escrever o curso",
                                                    "prioridade": "alta"}})
        verificar(r["result"]["isError"] is False, "criar_tarefa não é erro")
        verificar("#1" in r["result"]["content"][0]["text"], "id 1 atribuído")

        cli.chamar("tools/call", {"name": "criar_tarefa", "arguments": {"titulo": "revisar"}})
        r = cli.chamar("tools/call", {"name": "listar_tarefas", "arguments": {}})
        verificar(r["result"]["content"][0]["text"].count("\n") == 1, "duas tarefas listadas")

        r = cli.chamar("tools/call", {"name": "concluir_tarefa", "arguments": {"id": 1}})
        verificar(r["result"]["isError"] is False, "concluir_tarefa #1")

        r = cli.chamar("tools/call", {"name": "listar_tarefas",
                                      "arguments": {"status": "aberta"}})
        verificar("#2" in r["result"]["content"][0]["text"]
                  and "#1" not in r["result"]["content"][0]["text"],
                  "filtro por status funciona")

        r = cli.chamar("tools/call", {"name": "estatisticas", "arguments": {}})
        texto = r["result"]["content"][0]["text"]
        verificar("aberta: 1" in texto and "concluida: 1" in texto, "estatísticas corretas")

        print("erros de domínio viram isError=True, não erro de protocolo")
        r = cli.chamar("tools/call", {"name": "concluir_tarefa", "arguments": {"id": 1}})
        verificar("error" not in r, "concluir duas vezes não é erro JSON-RPC")
        verificar(r["result"]["isError"] is True, "isError=True")
        verificar("já está concluída" in r["result"]["content"][0]["text"],
                  "mensagem explica o motivo (o modelo precisa ler isso)")

        r = cli.chamar("tools/call", {"name": "criar_tarefa",
                                      "arguments": {"titulo": "x", "prioridade": "urgentíssima"}})
        verificar(r["result"]["isError"] is True, "prioridade inválida rejeitada")

        print("erros de protocolo viram erro JSON-RPC")
        r = cli.chamar("tools/call", {"name": "nao_existe", "arguments": {}})
        verificar(r.get("error", {}).get("code") == -32602, "ferramenta inexistente = -32602")

        r = cli.chamar("tools/call", {"name": "criar_tarefa", "arguments": {"cor": "azul"}})
        verificar(r.get("error", {}).get("code") == -32602, "argumento desconhecido = -32602")

        r = cli.chamar("metodo/inventado")
        verificar(r.get("error", {}).get("code") == -32601, "método desconhecido = -32601")

        cli.fechar()

    print()
    if falhas:
        print(f"{falhas} falha(s).")
        return 1
    print("Todos os testes passaram.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
