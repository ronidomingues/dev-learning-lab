"""Formatação da saída. Nenhuma lógica de negócio mora aqui.

Separar leitura (leitor), modelo (modelo) e apresentação (relatorio) é o que
permite testar a lógica sem capturar texto colorido de terminal.
"""

from __future__ import annotations

import json
from collections import Counter

from rich.console import Console
from rich.table import Table
from rich.tree import Tree

from lockspect.modelo import Lock, Pacote


def resumo(lock: Lock, console: Console) -> None:
    """Visão geral: quantos pacotes, de onde vêm, quais só têm sdist."""
    tabela = Table(title="Resumo do uv.lock", title_style="bold")
    tabela.add_column("Item")
    tabela.add_column("Valor", justify="right", style="cyan")

    tabela.add_row("Versão do formato", str(lock.versao_do_formato))
    tabela.add_row("Revisão", str(lock.revisao) if lock.revisao is not None else "—")
    tabela.add_row("requires-python", lock.requires_python or "—")
    tabela.add_row("Pacotes no total", str(len(lock.pacotes)))
    tabela.add_row("Locais (projeto/workspace)", str(len(lock.raizes)))
    tabela.add_row("De terceiros", str(len(lock.de_terceiros)))

    so_sdist = [p for p in lock.de_terceiros if p.so_sdist]
    tabela.add_row(
        "Sem wheel (compilam na instalação)",
        f"[red]{len(so_sdist)}[/red]" if so_sdist else "0",
    )
    total_wheels = sum(p.qtd_wheels for p in lock.pacotes)
    tabela.add_row("Wheels referenciados", str(total_wheels))

    console.print(tabela)

    if so_sdist:
        console.print(
            "\n[yellow]Atenção:[/yellow] estes pacotes não têm wheel e serão "
            "compilados em cada máquina — é onde a instalação fica lenta e "
            "onde falta de compilador quebra o build:"
        )
        for pacote in so_sdist:
            console.print(f"  • {pacote.nome} {pacote.versao}")

    fontes = Counter(p.tipo_de_fonte for p in lock.pacotes)
    console.print(
        "\n[bold]Origens:[/bold] " + ", ".join(f"{k}={v}" for k, v in sorted(fontes.items()))
    )


def arvore(lock: Lock, console: Console, profundidade: int | None = None) -> None:
    """Árvore de dependências a partir dos pacotes locais."""
    indice = lock.por_nome()
    raizes = lock.raizes or lock.pacotes[:1]

    for raiz in raizes:
        no = Tree(f"[bold]{raiz.nome}[/bold] {raiz.versao}")
        _expandir(raiz, indice, no, set(), 1, profundidade)
        console.print(no)


def _expandir(
    pacote: Pacote,
    indice: dict[str, Pacote],
    no: Tree,
    visitados: set[str],
    nivel: int,
    limite: int | None,
) -> None:
    if limite is not None and nivel > limite:
        return
    for nome in pacote.dependencias:
        filho = indice.get(nome)
        rotulo = f"{nome} {filho.versao}" if filho else f"{nome} [dim](fora do lock)[/dim]"
        if nome in visitados:
            no.add(f"{rotulo} [dim](já mostrado)[/dim]")
            continue
        sub = no.add(rotulo)
        if filho is not None:
            _expandir(filho, indice, sub, visitados | {nome}, nivel + 1, limite)


def dependentes(lock: Lock, alvo: str, console: Console) -> int:
    """Responde 'por que este pacote está aqui?'. Devolve o código de saída."""
    pacote = lock.por_nome().get(alvo)
    if pacote is None:
        console.print(f"[red]{alvo}[/red] não está neste lockfile.")
        return 1

    quem = lock.dependentes_de(alvo)
    console.print(f"[bold]{pacote.nome}[/bold] {pacote.versao} ({pacote.tipo_de_fonte})")
    if not quem:
        console.print("  ninguém depende dele — é uma dependência direta ou órfã.")
        return 0
    console.print("  requerido por:")
    for nome in quem:
        console.print(f"    ← {nome}")
    return 0


def como_json(lock: Lock) -> str:
    """Saída legível por máquina, para usar em pipelines."""
    return json.dumps(
        {
            "version": lock.versao_do_formato,
            "revision": lock.revisao,
            "requires_python": lock.requires_python,
            "packages": [
                {
                    "name": p.nome,
                    "version": p.versao,
                    "source_type": p.tipo_de_fonte,
                    "source": p.fonte,
                    "dependencies": list(p.dependencias),
                    "wheels": p.qtd_wheels,
                    "sdist_only": p.so_sdist,
                }
                for p in lock.pacotes
            ],
        },
        indent=2,
        ensure_ascii=False,
    )
