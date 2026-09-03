"""Interface de linha de comando."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from . import __version__, relatorio
from .config import Config
from .diff import ler
from .modelo import Resultado
from .regras import criterios, escopo, pacotes, segredos, tamanho

REGRAS = {
    "escopo": escopo,
    "tamanho": tamanho,
    "segredos": segredos,
    "pacotes": pacotes,
    "criterios": criterios,
}

CODIGO_OK = 0
CODIGO_REPROVADO = 1
CODIGO_ERRO = 2


def obter_diff(args) -> str:
    if args.diff:
        p = Path(args.diff)
        if not p.exists():
            raise SystemExit(f"arquivo de diff não encontrado: {p}")
        return p.read_text(encoding="utf-8")
    if not sys.stdin.isatty():
        dados = sys.stdin.read()
        if dados.strip():
            return dados
    comando = ["git", "diff", "--cached"] if args.staged else ["git", "diff", args.base]
    r = subprocess.run(comando, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(f"git falhou: {r.stderr.strip()}")
    return r.stdout


def montar_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="portao",
        description="Portão de verificação para código gerado por IA.",
    )
    p.add_argument("--version", action="version", version=f"portao {__version__}")
    p.add_argument(
        "regras", nargs="*", default=[],
        help="regras a rodar (padrão: todas). Opções: " + ", ".join(REGRAS),
    )
    p.add_argument("--diff", help="arquivo com o diff; padrão é ler do git ou do stdin")
    p.add_argument("--staged", action="store_true", help="usar `git diff --cached`")
    p.add_argument("--base", default="HEAD", help="base para `git diff` (padrão: HEAD)")
    p.add_argument("--config", default="portao.json", help="caminho da configuração")
    p.add_argument("--raiz", default=".", help="raiz do repositório")
    p.add_argument("--formato", choices=["texto", "json"], default="texto")
    p.add_argument("--sem-cor", action="store_true")
    p.add_argument(
        "--testes-editaveis", action="store_true",
        help="permitir alteração de arquivos de teste (use quando a tarefa É escrever teste)",
    )
    p.add_argument(
        "--online", action="store_true",
        help="consultar o registro de pacotes pela rede",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    args = montar_parser().parse_args(argv)

    desconhecidas = set(args.regras) - set(REGRAS)
    if desconhecidas:
        print(f"regra desconhecida: {', '.join(sorted(desconhecidas))}", file=sys.stderr)
        return CODIGO_ERRO

    try:
        cfg = Config.de_arquivo(Path(args.raiz) / args.config)
    except (ValueError, OSError) as e:
        print(f"configuração inválida: {e}", file=sys.stderr)
        return CODIGO_ERRO

    if args.testes_editaveis:
        cfg.testes_editaveis = True
    if args.online:
        cfg.checar_registro_online = True

    try:
        diff = ler(obter_diff(args))
    except SystemExit as e:
        print(e, file=sys.stderr)
        return CODIGO_ERRO

    escolhidas = args.regras or list(REGRAS)
    resultados: list[Resultado] = []
    raiz = Path(args.raiz)
    for nome in escolhidas:
        modulo = REGRAS[nome]
        if nome == "criterios":
            resultados.append(modulo.verificar(diff, cfg, raiz))
        else:
            resultados.append(modulo.verificar(diff, cfg))

    if args.formato == "json":
        print(relatorio.como_json(resultados))
    else:
        print(relatorio.texto(resultados, cor=not args.sem_cor))

    reprovado = any(r.bloqueios for r in resultados)
    return CODIGO_REPROVADO if reprovado else CODIGO_OK
