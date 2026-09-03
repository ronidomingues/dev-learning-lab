"""Interface de linha de comando.

Usa `argparse` da biblioteca padrão de propósito: um projeto-modelo não deve
ensinar uma dependência a mais do que o necessário. Para CLIs grandes, `typer`
ou `click` valem a pena.
"""

from __future__ import annotations

import argparse
import os
import sys
from collections.abc import Sequence

from rich.console import Console

from lockspect import __version__, relatorio
from lockspect.leitor import LockInvalido, ler_lock

# Configuração por variável de ambiente, com padrão sensato.
# LOCKSPECT_LOCK permite apontar para outro arquivo sem repetir --arquivo.
PADRAO = os.environ.get("LOCKSPECT_LOCK", "uv.lock")


def construir_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="lockspect",
        description="Inspeciona um arquivo uv.lock e explica o que há dentro dele.",
    )
    parser.add_argument("--version", action="version", version=f"lockspect {__version__}")
    parser.add_argument(
        "-a",
        "--arquivo",
        default=PADRAO,
        help="caminho do uv.lock ou do diretório que o contém (padrão: %(default)s)",
    )
    parser.add_argument("--json", action="store_true", help="saída em JSON, para pipelines")
    parser.add_argument("--sem-cor", action="store_true", help="desliga cores (logs de CI)")

    sub = parser.add_subparsers(dest="comando")
    sub.add_parser("resumo", help="visão geral do lockfile (padrão)")

    p_arvore = sub.add_parser("arvore", help="árvore de dependências")
    p_arvore.add_argument(
        "-d", "--profundidade", type=int, default=None, help="limita a profundidade da árvore"
    )

    p_quem = sub.add_parser("quem", help="quem depende de um pacote")
    p_quem.add_argument("pacote", help="nome do pacote a investigar")

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Ponto de entrada. Devolve o código de saída em vez de chamar sys.exit,
    o que torna a função testável."""
    args = construir_parser().parse_args(argv)
    console = Console(no_color=args.sem_cor, stderr=False)

    try:
        lock = ler_lock(args.arquivo)
    except FileNotFoundError as erro:
        print(f"erro: {erro}", file=sys.stderr)
        print("dica: rode dentro de um projeto uv, ou use --arquivo CAMINHO", file=sys.stderr)
        return 2
    except LockInvalido as erro:
        print(f"erro: {erro}", file=sys.stderr)
        return 3

    if args.json:
        print(relatorio.como_json(lock))
        return 0

    comando = args.comando or "resumo"
    if comando == "resumo":
        relatorio.resumo(lock, console)
        return 0
    if comando == "arvore":
        relatorio.arvore(lock, console, args.profundidade)
        return 0
    if comando == "quem":
        return relatorio.dependentes(lock, args.pacote, console)

    return 1  # pragma: no cover - argparse já barra comandos desconhecidos


if __name__ == "__main__":
    raise SystemExit(main())
