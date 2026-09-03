"""Borda do sistema: monta os objetos reais e imprime.

Repare que aqui **não há regra de negócio nenhuma** — só montagem
(*composition root*). É de propósito: a borda é a parte mais difícil de testar,
então ela é a mais fina possível.

Uso:
    python -m assinaturas.cli demo
    python -m assinaturas.cli renovar --banco assinaturas.db --data 2026-09-11
"""

from __future__ import annotations

import argparse
from datetime import date

from .assinatura import Assinatura
from .gateway import GatewayFalso
from .plano import CATALOGO
from .relogio import RelogioDoSistema, RelogioFixo
from .repositorio import RepositorioMemoria, RepositorioSQLite
from .servico import NotificadorEspiao, ServicoRenovacao


def demo() -> int:
    """Roda um ciclo completo em memória, sem banco e sem rede."""
    hoje = date(2026, 8, 12)
    relogio = RelogioFixo(hoje)
    repo = RepositorioMemoria(
        [
            Assinatura.criar("a1", "ana@exemplo.br", CATALOGO["pro"], date(2026, 7, 13)),
            Assinatura.criar("a2", "bruno@exemplo.br", CATALOGO["basico"], date(2026, 7, 13)),
            Assinatura.criar("a3", "carla@exemplo.br", CATALOGO["anual"], hoje),
        ]
    )
    gateway = GatewayFalso(falhar_para={"bruno@exemplo.br"})
    notificador = NotificadorEspiao()

    servico = ServicoRenovacao(repo, gateway, relogio, notificador)
    relatorio = servico.renovar_vencidas()

    print(f"data simulada: {hoje:%d/%m/%Y}")
    print(f"relatório: {relatorio}")
    print("\nnotificações enviadas:")
    for cliente, assunto, corpo in notificador.mensagens:
        print(f"  → {cliente}: {assunto} | {corpo}")
    print("\nestado final:")
    for id_ in ("a1", "a2", "a3"):
        a = repo.buscar(id_)
        assert a is not None
        print(
            f"  {a.id} {a.cliente:22} {a.estado.value:12} "
            f"próx. {a.proxima_cobranca} ciclos {a.ciclos_pagos}"
        )
    return 0


def renovar(banco: str, data: str | None) -> int:
    relogio = RelogioFixo(date.fromisoformat(data)) if data else RelogioDoSistema()
    with RepositorioSQLite(banco) as repo:
        servico = ServicoRenovacao(repo, GatewayFalso(), relogio, NotificadorEspiao())
        print(servico.renovar_vencidas())
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="assinaturas")
    sub = parser.add_subparsers(dest="comando", required=True)
    sub.add_parser("demo", help="ciclo completo em memória")
    p_ren = sub.add_parser("renovar", help="renova vencidas de um banco SQLite")
    p_ren.add_argument("--banco", default="assinaturas.db")
    p_ren.add_argument("--data", help="data simulada, formato AAAA-MM-DD")

    args = parser.parse_args(argv)
    if args.comando == "demo":
        return demo()
    return renovar(args.banco, args.data)


if __name__ == "__main__":
    raise SystemExit(main())
