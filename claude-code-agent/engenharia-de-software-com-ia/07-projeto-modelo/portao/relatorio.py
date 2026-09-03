"""Apresentação do resultado.

Separado das regras de propósito: mudar como o relatório aparece nunca
deve exigir tocar na lógica que decide se algo passa.
"""

from __future__ import annotations

import json

from .modelo import Resultado, Severidade

LARGURA = 72


def texto(resultados: list[Resultado], cor: bool = True) -> str:
    def pinta(s: str, codigo: str) -> str:
        return f"\033[{codigo}m{s}\033[0m" if cor else s

    linhas: list[str] = []
    linhas.append("═" * LARGURA)
    linhas.append("PORTÃO DE VERIFICAÇÃO")
    linhas.append("═" * LARGURA)

    for r in resultados:
        if r.pulada:
            linhas.append(f"{pinta('PULADA  ', '90')} {r.regra} — {r.motivo_pulada}")
            continue
        marca = pinta("APROVADO", "32") if r.aprovado else pinta("REPROVADO", "31")
        linhas.append(f"{marca} {r.regra}")
        for a in r.achados:
            simbolo = "✗" if a.severidade is Severidade.BLOQUEIA else "!"
            cor_a = "31" if a.severidade is Severidade.BLOQUEIA else "33"
            local = f"{a.arquivo}:{a.linha}" if a.linha else a.arquivo
            linhas.append(f"  {pinta(simbolo, cor_a)} {local} — {a.mensagem}")
            if a.detalhe:
                linhas.append(f"      {a.detalhe}")

    bloqueios = sum(len(r.bloqueios) for r in resultados)
    avisos = sum(len(r.avisos) for r in resultados)
    linhas.append("─" * LARGURA)
    if bloqueios:
        linhas.append(
            pinta(f"REPROVADO — {bloqueios} bloqueio(s), {avisos} aviso(s)", "31;1")
        )
    else:
        linhas.append(pinta(f"APROVADO — 0 bloqueios, {avisos} aviso(s)", "32;1"))
    linhas.append("═" * LARGURA)
    return "\n".join(linhas)


def como_json(resultados: list[Resultado]) -> str:
    bloqueios = sum(len(r.bloqueios) for r in resultados)
    return json.dumps(
        {
            "aprovado": bloqueios == 0,
            "bloqueios": bloqueios,
            "avisos": sum(len(r.avisos) for r in resultados),
            "regras": [r.como_dict() for r in resultados],
        },
        ensure_ascii=False,
        indent=2,
    )
