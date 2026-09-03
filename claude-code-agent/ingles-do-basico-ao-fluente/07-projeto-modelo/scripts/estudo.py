#!/usr/bin/env python3
"""Registro e relatório de estudo do Projeto Ponte.

Só biblioteca padrão. Guarda um JSON por linha (JSONL) — formato escolhido
porque é append-only: registrar nunca reescreve o arquivo inteiro, então uma
queda de energia no meio da gravação perde no máximo a última linha.

Uso:
    python3 scripts/estudo.py registrar --min 45 --hab escuta fala --nota "podcast BBC"
    python3 scripts/estudo.py relatorio
    python3 scripts/estudo.py relatorio --ultimos 30
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent

HABILIDADES = ["escuta", "fala", "leitura", "escrita", "vocabulario", "gramatica"]


class ErroDeDados(Exception):
    pass


def carregar_config(caminho: Path) -> dict:
    try:
        return json.loads(caminho.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise ErroDeDados(f"config não encontrado: {caminho}")
    except json.JSONDecodeError as e:
        raise ErroDeDados(f"config.json inválido ({e.msg}, linha {e.lineno})")


def ler_registro(caminho: Path) -> list[dict]:
    """Lê o JSONL. Linha corrompida é avisada e ignorada, não derruba o relatório."""
    if not caminho.exists():
        return []
    sessoes = []
    for n, linha in enumerate(caminho.read_text(encoding="utf-8").splitlines(), start=1):
        linha = linha.strip()
        if not linha:
            continue
        try:
            sessoes.append(json.loads(linha))
        except json.JSONDecodeError:
            print(f"aviso: linha {n} do registro está corrompida e foi ignorada", file=sys.stderr)
    return sessoes


def registrar(caminho: Path, dia: str, minutos: int, habilidades: list[str], nota: str) -> dict:
    if minutos <= 0:
        raise ErroDeDados("minutos precisa ser maior que zero")
    if minutos > 720:
        raise ErroDeDados("mais de 12 h em um dia: quase certamente erro de digitação")
    desconhecidas = [h for h in habilidades if h not in HABILIDADES]
    if desconhecidas:
        raise ErroDeDados(
            f"habilidade(s) desconhecida(s): {', '.join(desconhecidas)}. "
            f"Use: {', '.join(HABILIDADES)}"
        )
    try:
        datetime.strptime(dia, "%Y-%m-%d")
    except ValueError:
        raise ErroDeDados(f"data inválida: '{dia}' (use AAAA-MM-DD)")

    sessao = {"data": dia, "minutos": minutos, "habilidades": habilidades, "nota": nota}
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with caminho.open("a", encoding="utf-8") as f:
        f.write(json.dumps(sessao, ensure_ascii=False) + "\n")
    return sessao


def minutos_por_dia(sessoes: list[dict]) -> dict[str, int]:
    total: dict[str, int] = {}
    for s in sessoes:
        total[s["data"]] = total.get(s["data"], 0) + int(s["minutos"])
    return total


def sequencia_atual(dias: set[str], hoje: date) -> int:
    """Dias seguidos até hoje (ou até ontem, se hoje ainda não teve estudo).

    Contar a partir de ontem quando hoje está vazio evita zerar a sequência
    de quem abre o relatório de manhã antes de estudar — um detalhe pequeno
    que muda a chance de a pessoa continuar.
    """
    if not dias:
        return 0
    inicio = hoje if hoje.isoformat() in dias else hoje - timedelta(days=1)
    n = 0
    d = inicio
    while d.isoformat() in dias:
        n += 1
        d -= timedelta(days=1)
    return n


def maior_sequencia(dias: set[str]) -> int:
    if not dias:
        return 0
    ordenados = sorted(date.fromisoformat(d) for d in dias)
    melhor = atual = 1
    for anterior, seguinte in zip(ordenados, ordenados[1:]):
        atual = atual + 1 if (seguinte - anterior).days == 1 else 1
        melhor = max(melhor, atual)
    return melhor


def projecao(horas_feitas: float, horas_alvo: float, media_min_dia: float) -> str:
    faltam = horas_alvo - horas_feitas
    if faltam <= 0:
        return "meta de horas do nível-alvo já atingida — refaça o EF SET para confirmar."
    if media_min_dia <= 0:
        return "sem ritmo medido ainda: registre alguns dias para haver projeção."
    dias = faltam * 60 / media_min_dia
    alvo = date.today() + timedelta(days=int(dias))
    return (
        f"faltam {faltam:.0f} h; no ritmo atual de {media_min_dia:.0f} min/dia, "
        f"são ~{dias/30.4:.1f} meses (por volta de {alvo.isoformat()})"
    )


def relatorio(cfg: dict, sessoes: list[dict], ultimos: int, hoje: date) -> str:
    if not sessoes:
        return (
            "Nenhuma sessão registrada ainda.\n"
            "Comece com:  python3 scripts/estudo.py registrar --min 20 --hab escuta"
        )

    por_dia = minutos_por_dia(sessoes)
    dias = set(por_dia)
    total_min = sum(por_dia.values())
    total_h = total_min / 60

    recentes = {
        d: m for d, m in por_dia.items()
        if date.fromisoformat(d) > hoje - timedelta(days=ultimos)
    }
    media_recente = sum(recentes.values()) / ultimos if ultimos else 0

    por_hab: dict[str, int] = {}
    for s in sessoes:
        habs = s.get("habilidades") or ["(não informado)"]
        fatia = int(s["minutos"]) / len(habs)
        for h in habs:
            por_hab[h] = por_hab.get(h, 0) + fatia

    alvo = cfg.get("nivel_alvo", "B2")
    horas_alvo = float(cfg.get("horas_por_nivel", {}).get(alvo, 600))
    meta = int(cfg.get("meta_diaria_min", 40))

    linhas = ["=== Projeto Ponte · relatório de estudo ==="]
    linhas.append(f"sessões registradas : {len(sessoes)} em {len(dias)} dias distintos")
    linhas.append(f"tempo total         : {total_h:.1f} h ({total_min} min)")
    linhas.append(f"primeiro registro   : {min(dias)}")
    linhas.append(f"último registro     : {max(dias)}")
    linhas.append("")
    linhas.append(f"sequência atual     : {sequencia_atual(dias, hoje)} dia(s)")
    linhas.append(f"maior sequência     : {maior_sequencia(dias)} dia(s)")
    linhas.append(
        f"média dos últimos {ultimos} dias: {media_recente:.0f} min/dia "
        f"(meta: {meta} min/dia — {'ok' if media_recente >= meta else 'abaixo'})"
    )
    linhas.append("")
    linhas.append("distribuição por habilidade:")
    largura = 28
    maximo = max(por_hab.values()) if por_hab else 1
    for h in sorted(por_hab, key=lambda x: -por_hab[x]):
        barras = "#" * max(1, int(por_hab[h] / maximo * largura))
        pct = por_hab[h] / total_min * 100
        linhas.append(f"  {h:<12} {por_hab[h]/60:>5.1f} h {pct:>5.1f}%  {barras}")
    linhas.append("")
    linhas.append(f"alvo: {alvo} (~{horas_alvo:.0f} h guiadas)")
    linhas.append("  " + projecao(total_h, horas_alvo, media_recente))
    linhas.append("")
    linhas.append("Lembrete: a projeção é aritmética, não promessa. Horas mal gastas")
    linhas.append("(revisão passiva, tradução) rendem menos que a tabela supõe.")
    return "\n".join(linhas)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Registro e relatório de estudo.")
    p.add_argument("--config", default=str(RAIZ / "config.json"))
    sub = p.add_subparsers(dest="comando", required=True)

    r = sub.add_parser("registrar", help="registra uma sessão de estudo")
    r.add_argument("--min", type=int, required=True, dest="minutos")
    r.add_argument("--hab", nargs="+", default=[], choices=HABILIDADES, dest="habilidades")
    r.add_argument("--nota", default="")
    r.add_argument("--data", default=date.today().isoformat())

    v = sub.add_parser("relatorio", help="mostra o relatório")
    v.add_argument("--ultimos", type=int, default=14, help="janela da média, em dias")

    args = p.parse_args(argv)

    try:
        cfg = carregar_config(Path(args.config))
        registro = RAIZ / cfg["registro_de_estudo"]

        if args.comando == "registrar":
            s = registrar(registro, args.data, args.minutos, args.habilidades, args.nota)
            print(f"registrado: {s['data']} · {s['minutos']} min · {', '.join(s['habilidades']) or '—'}")
        else:
            print(relatorio(cfg, ler_registro(registro), args.ultimos, date.today()))
    except ErroDeDados as e:
        print(f"ERRO: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
