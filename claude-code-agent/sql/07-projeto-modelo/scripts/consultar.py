#!/usr/bin/env python3
"""Executa as consultas de `consultas/` e imprime o resultado em tabela.

Só biblioteca padrão. Serve de exemplo mínimo de "aplicação que fala SQL":
abre conexão, executa, formata, fecha.

Uso:
    python3 scripts/consultar.py            # roda todas
    python3 scripts/consultar.py 03 06      # roda só as que começam por 03 e 06
    python3 scripts/consultar.py --plano 03 # mostra também o plano de execução
"""

from __future__ import annotations

import argparse
import glob
import os
import sqlite3
import sys
import time

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
BANCO = os.path.join(RAIZ, "planta.db")


def formatar(colunas, linhas, limite=25):
    """Tabela de largura fixa. Feio e suficiente — o assunto aqui é SQL."""
    if not linhas:
        return "  (nenhuma linha)"
    dados = [[("" if v is None else str(v)) for v in ln] for ln in linhas[:limite]]
    larg = [max(len(c), *(len(d[i]) for d in dados)) for i, c in enumerate(colunas)]
    sep = "  " + "-+-".join("-" * w for w in larg)
    out = ["  " + " | ".join(c.ljust(larg[i]) for i, c in enumerate(colunas)), sep]
    out += ["  " + " | ".join(d[i].rjust(larg[i]) for i in range(len(colunas)))
            for d in dados]
    if len(linhas) > limite:
        out.append(f"  ... e mais {len(linhas) - limite} linha(s)")
    return "\n".join(out)


def cabecalho_do_arquivo(texto):
    """Primeira linha de comentário do .sql — serve de título."""
    for linha in texto.splitlines():
        if linha.startswith("--"):
            return linha.lstrip("- ").strip()
    return ""


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("filtros", nargs="*", help="prefixos dos arquivos a rodar")
    p.add_argument("--banco", default=BANCO)
    p.add_argument("--plano", action="store_true",
                   help="mostra EXPLAIN QUERY PLAN antes de cada consulta")
    p.add_argument("--limite", type=int, default=25)
    a = p.parse_args()

    if not os.path.exists(a.banco):
        print(f"Banco não encontrado: {a.banco}\n"
              f"Rode primeiro: python3 scripts/gerar_dados.py", file=sys.stderr)
        return 1

    con = sqlite3.connect(a.banco)
    arquivos = sorted(glob.glob(os.path.join(RAIZ, "consultas", "*.sql")))
    if a.filtros:
        arquivos = [f for f in arquivos
                    if any(os.path.basename(f).startswith(x) for x in a.filtros)]

    for arq in arquivos:
        with open(arq, encoding="utf-8") as f:
            sql = f.read()
        nome = os.path.basename(arq)
        print(f"\n{'=' * 78}\n{nome} — {cabecalho_do_arquivo(sql)}\n{'=' * 78}")

        if a.plano:
            print("  PLANO:")
            for linha in con.execute("EXPLAIN QUERY PLAN " + sql):
                print("   ", linha[-1])
            print()

        t0 = time.perf_counter()
        cur = con.execute(sql)
        linhas = cur.fetchall()
        dt = (time.perf_counter() - t0) * 1000
        colunas = [d[0] for d in cur.description]
        print(formatar(colunas, linhas, a.limite))
        print(f"  [{len(linhas)} linha(s) em {dt:.1f} ms]")

    con.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
