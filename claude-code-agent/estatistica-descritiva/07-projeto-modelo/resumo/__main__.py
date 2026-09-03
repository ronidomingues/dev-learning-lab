"""Interface de linha de comando.

    python3 -m resumo dados/alugueis.csv --coluna aluguel
    python3 -m resumo dados/alugueis.csv --formato json
    python3 -m resumo --demo
"""

from __future__ import annotations

import argparse
import json
import sys

from . import __version__
from .leitura import ErroDeLeitura, ler_csv
from .medidas import ErroDeMedida
from .relatorio import dicionario, texto

DEMO = [1200, 1350, 1400, 1450, 1500, 1500, 1600, 1650, 1700, 1800,
        1850, 1900, 2000, 2100, 2200, 2400, 2800, 3200, 4500, 9000]


def montar_parser():
    p = argparse.ArgumentParser(
        prog="resumo",
        description="Relatório estatístico honesto de uma coluna numérica.",
        epilog="Sem argumentos de arquivo, use --demo para ver um exemplo.",
    )
    p.add_argument("arquivo", nargs="?", help="caminho do CSV")
    p.add_argument("--coluna", "-c", help="nome da coluna (padrão: a primeira numérica)")
    p.add_argument("--formato", "-f", choices=["texto", "json"], default="texto")
    p.add_argument("--confianca", type=float, default=0.95,
                   help="nível de confiança dos intervalos (padrão: 0,95)")
    p.add_argument("--bootstrap", type=int, default=2000,
                   help="reamostragens do bootstrap (padrão: 2000)")
    p.add_argument("--semente", type=int, default=42,
                   help="semente do sorteio, para reprodutibilidade (padrão: 42)")
    p.add_argument("--encoding", default="utf-8",
                   help="codificação do arquivo (padrão: utf-8; tente latin-1)")
    p.add_argument("--separador", help="separador de campos (padrão: detectado)")
    p.add_argument("--decimal", choices=[".", ","],
                   help="separador decimal (padrão: detectado pela coluna)")
    p.add_argument("--demo", action="store_true",
                   help="roda com um conjunto de exemplo embutido")
    p.add_argument("--version", action="version", version=f"resumo {__version__}")
    return p


def main(argv=None):
    args = montar_parser().parse_args(argv)

    if not 0.5 <= args.confianca < 1.0:
        print("erro: --confianca deve estar entre 0,5 e 1,0 (ex.: 0.95)", file=sys.stderr)
        return 2
    if args.bootstrap < 100:
        print("erro: --bootstrap deve ser pelo menos 100", file=sys.stderr)
        return 2

    if args.demo:
        valores, coluna, procedencia = DEMO, "aluguel (demo)", None
    elif args.arquivo:
        try:
            col = ler_csv(args.arquivo, args.coluna, args.encoding,
                          args.separador, args.decimal)
        except ErroDeLeitura as e:
            print(f"erro de leitura: {e}", file=sys.stderr)
            return 1
        valores, coluna = col.valores, col.nome
        procedencia = col
    else:
        montar_parser().print_help()
        return 2

    kw = dict(confianca=args.confianca, repeticoes=args.bootstrap,
              semente=args.semente)
    try:
        if args.formato == "json":
            d = dicionario(valores, coluna, **kw)
            if procedencia is not None:
                d["procedencia"] = _procedencia(procedencia)
            print(json.dumps(d, ensure_ascii=False, indent=2, default=str))
        else:
            if procedencia is not None:
                print(_bloco_procedencia(procedencia))
            print(texto(valores, coluna, **kw))
    except ErroDeMedida as e:
        print(f"erro de cálculo: {e}", file=sys.stderr)
        return 1
    return 0


def _procedencia(col):
    return {
        "linhas_no_arquivo": col.total_linhas,
        "valores_usados": len(col.valores),
        "ausentes": col.ausentes,
        "invalidos": len(col.invalidos),
        "exemplos_invalidos": col.invalidos[:5],
        "sentinelas_suspeitas": col.sentinelas,
        "separador_decimal": col.decimal,
        "decimal_ambiguo": col.decimal_ambiguo,
        "aproveitamento": round(col.aproveitamento, 4),
    }


def _bloco_procedencia(col):
    L = ["── PROCEDÊNCIA DOS DADOS " + "─" * 49,
         f"  linhas no arquivo .... {col.total_linhas}",
         f"  valores usados ....... {len(col.valores)} "
         f"({100*col.aproveitamento:.1f}% do arquivo)",
         f"  ausentes ............. {col.ausentes}",
         f"  inválidos ............ {len(col.invalidos)}"]
    if col.invalidos:
        amostra = ", ".join(f"linha {i}: {repr(t)}" for i, t in col.invalidos[:3])
        L.append(f"     exemplos: {amostra}")
        L.append("     ⚠ linhas descartadas podem enviesar o resultado.")
    if col.sentinelas:
        L.append(f"  ⚠ {col.sentinelas} valor(es) iguais a sentinelas típicas de "
                 "ausência (-999, 9999...)")
        L.append("     Verifique se significam 'faltando' — se sim, estão "
                 "contaminando as medidas.")
    L.append(f"  separador decimal .... '{col.decimal}' (detectado pela coluna)")
    if col.decimal_ambiguo:
        L.append("  ⚠ AMBÍGUO: quase todos os valores têm 3 dígitos após o ponto.")
        L.append("     '1.500' pode ser mil e quinhentos (pt-BR) ou um e meio (en-US).")
        L.append("     Foi adotado o ponto como decimal. Para forçar o outro: --decimal ','")
    return "\n".join(L)


if __name__ == "__main__":
    sys.exit(main())
