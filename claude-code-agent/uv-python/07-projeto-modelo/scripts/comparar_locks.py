#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["rich>=13.0"]
# ///
"""Compara dois arquivos `uv.lock` e mostra o que mudou.

Este script é **independente do projeto** que o hospeda: ele declara as próprias
dependências no cabeçalho PEP 723 e exige Python >= 3.11 (para usar `tomllib` da
biblioteca padrão), enquanto o projeto `lockspect` suporta 3.10.

Rode com:
    uv run scripts/comparar_locks.py antigo.lock novo.lock
ou, se o seu `env` aceitar `-S` no shebang:
    ./scripts/comparar_locks.py antigo.lock novo.lock
"""

from __future__ import annotations

import sys
from pathlib import Path

import tomllib
from rich.console import Console
from rich.table import Table


def versoes(caminho: Path) -> dict[str, str]:
    dados = tomllib.loads(caminho.read_text(encoding="utf-8"))
    return {p["name"]: p.get("version", "?") for p in dados.get("package", [])}


def main() -> int:
    if len(sys.argv) != 3:
        print(f"uso: {sys.argv[0]} ANTIGO.lock NOVO.lock", file=sys.stderr)
        return 2

    antigo_caminho, novo_caminho = Path(sys.argv[1]), Path(sys.argv[2])
    for caminho in (antigo_caminho, novo_caminho):
        if not caminho.exists():
            print(f"erro: não encontrei {caminho}", file=sys.stderr)
            return 2

    antigo, novo = versoes(antigo_caminho), versoes(novo_caminho)
    console = Console()

    tabela = Table(title=f"{antigo_caminho.name} → {novo_caminho.name}")
    tabela.add_column("Mudança")
    tabela.add_column("Pacote")
    tabela.add_column("De", justify="right")
    tabela.add_column("Para", justify="right")

    for nome in sorted(set(antigo) | set(novo)):
        antes, depois = antigo.get(nome), novo.get(nome)
        if antes == depois:
            continue
        if antes is None:
            tabela.add_row("[green]+ adicionado[/green]", nome, "—", depois or "—")
        elif depois is None:
            tabela.add_row("[red]- removido[/red]", nome, antes, "—")
        else:
            tabela.add_row("[yellow]~ alterado[/yellow]", nome, antes, depois)

    if tabela.row_count == 0:
        console.print("[green]Nenhuma diferença de versão entre os dois lockfiles.[/green]")
        return 0

    console.print(tabela)
    return 1  # código 1: houve mudança — útil como portão de CI


if __name__ == "__main__":
    raise SystemExit(main())
