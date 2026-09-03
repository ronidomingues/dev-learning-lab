"""
relatorio.py — transforma dados em decisão.

Uma lista de portas não é um relatório. Relatório é a lista mais o julgamento:
o que disso aqui é normal, o que é dívida, e o que precisa ser fechado hoje.
Este módulo é onde o catálogo encontra o inventário.
"""

from __future__ import annotations

import json
from dataclasses import asdict

from catalogo import ALTO, BAIXO, MEDIO, consultar, descrever_faixa, nome_do_sistema
from inventario import Socket, faixa_efemera

VERDE = "\033[32m"
AMARELO = "\033[33m"
VERMELHO = "\033[31m"
CINZA = "\033[90m"
NEGRITO = "\033[1m"
FIM = "\033[0m"

COR_RISCO = {ALTO: VERMELHO, MEDIO: AMARELO, BAIXO: VERDE}


def classificar(s: Socket) -> tuple[str, str]:
    """
    Devolve (severidade, motivo).

    A regra de ouro, e o motivo de este projeto existir: o risco não está no
    número da porta. Está no par (número, quem alcança). Postgres em 127.0.0.1
    é higiene; o mesmo Postgres em 0.0.0.0 é um incidente esperando data.
    """
    servico = consultar(s.porta_local, s.protocolo)
    ini_ef, fim_ef = faixa_efemera()

    if not s.exposto:
        return "ok", "só a própria máquina alcança (loopback)"

    if servico is None:
        if ini_ef <= s.porta_local <= fim_ef:
            return "atencao", ("porta na faixa efêmera escutando para fora — "
                               "quase sempre um servidor de desenvolvimento esquecido")
        return "atencao", "serviço não catalogado exposto — identifique antes de liberar"

    if servico.risco_exposto == ALTO:
        return "critico", f"{servico.nome}: {servico.descricao}"
    if servico.risco_exposto == MEDIO:
        return "atencao", f"{servico.nome}: {servico.descricao}"
    return "ok", f"{servico.nome}: exposição usual para este serviço"


ORDEM = {"critico": 0, "atencao": 1, "ok": 2}
ROTULO = {"critico": f"{VERMELHO}CRÍTICO{FIM}", "atencao": f"{AMARELO}ATENÇÃO{FIM}", "ok": f"{VERDE}OK{FIM}"}


def texto(sockets: list[Socket], cor: bool = True) -> str:
    def pinta(s: str) -> str:
        return s if cor else _sem_cor(s)

    linhas: list[str] = []
    linhas.append(pinta(f"{NEGRITO}INVENTÁRIO DE PORTAS LOCAIS{FIM}"))
    ini, fim = faixa_efemera()
    linhas.append(pinta(f"{CINZA}faixa efêmera deste host: {ini}-{fim}  "
                        f"({fim - ini + 1} portas de origem disponíveis){FIM}"))
    linhas.append("")

    itens = [(classificar(s), s) for s in sockets]
    itens.sort(key=lambda par: (ORDEM[par[0][0]], par[1].porta_local))

    cab = f"{'':<9} {'PROTO':<6} {'ENDEREÇO LOCAL':<26} {'ESCOPO':<20} {'PROCESSO':<24} MOTIVO"
    linhas.append(pinta(NEGRITO + cab + FIM))
    linhas.append("-" * 140)

    for (sev, motivo), s in itens:
        endereco = f"{s.ip_local}:{s.porta_local}"
        proc = f"{s.processo}[{s.pid}]" if s.processo else "(sem permissão)"
        linhas.append(pinta(
            f"{ROTULO[sev]:<9} {s.protocolo:<6} {endereco:<26} {s.escopo:<20} {proc:<24} {motivo}"
            if cor else
            f"{sev.upper():<9} {s.protocolo:<6} {endereco:<26} {s.escopo:<20} {proc:<24} {motivo}"
        ))

    n_crit = sum(1 for (sev, _), _ in itens if sev == "critico")
    n_at = sum(1 for (sev, _), _ in itens if sev == "atencao")
    linhas.append("")
    linhas.append(pinta(f"{NEGRITO}RESUMO{FIM}: {len(itens)} sockets em escuta · "
                        f"{VERMELHO}{n_crit} crítico(s){FIM} · {AMARELO}{n_at} atenção{FIM} · "
                        f"{VERDE}{len(itens) - n_crit - n_at} ok{FIM}"))
    if n_crit:
        linhas.append(pinta(f"{CINZA}Próximo passo: para cada crítico, decida — "
                            f"(a) o serviço precisa mesmo ser alcançável de fora? "
                            f"(b) se sim, quem pode alcançar? Feche no bind antes de "
                            f"tentar consertar no firewall.{FIM}"))
    return "\n".join(linhas)


def _sem_cor(s: str) -> str:
    import re
    return re.sub(r"\033\[[0-9;]*m", "", s)


def para_json(sockets: list[Socket]) -> str:
    saida = []
    for s in sockets:
        sev, motivo = classificar(s)
        servico = consultar(s.porta_local, s.protocolo)
        d = asdict(s)
        d.update({
            "escopo": s.escopo,
            "exposto": s.exposto,
            "severidade": sev,
            "motivo": motivo,
            "servico_catalogo": servico.nome if servico else None,
            "protocolo_aplicacao": servico.proto_app if servico else None,
            "servico_etc_services": nome_do_sistema(s.porta_local, s.protocolo),
            "faixa_iana": descrever_faixa(s.porta_local),
        })
        saida.append(d)
    return json.dumps(saida, indent=2, ensure_ascii=False)


def texto_varredura(resultados, host: str, cor: bool = True) -> str:
    from varredura import ABERTA, FECHADA, FILTRADA
    abertas = [r for r in resultados if r.estado == ABERTA]
    fechadas = sum(1 for r in resultados if r.estado == FECHADA)
    filtradas = sum(1 for r in resultados if r.estado == FILTRADA)

    linhas = [f"VARREDURA DE {host} — {len(resultados)} portas testadas", ""]
    if not abertas:
        linhas.append("nenhuma porta aberta encontrada no conjunto testado")
    else:
        linhas.append(f"{'PORTA':<8} {'SERVIÇO ESPERADO':<22} {'ms':<8} BANNER / EVIDÊNCIA")
        linhas.append("-" * 100)
        for r in abertas:
            serv = consultar(r.porta, "tcp")
            nome = serv.nome if serv else (nome_do_sistema(r.porta, "tcp") or "?")
            ms = f"{r.latencia_ms:.1f}" if r.latencia_ms is not None else "-"
            linhas.append(f"{r.porta:<8} {nome:<22} {ms:<8} {r.banner or '(sem banner)'}")
    linhas.append("")
    linhas.append(f"abertas: {len(abertas)} · fechadas (RST): {fechadas} · filtradas (silêncio): {filtradas}")
    if filtradas:
        linhas.append("filtrada = nada voltou. Pode ser firewall descartando, pode ser "
                      "perda de pacote. Repita com timeout maior antes de concluir.")
    texto_final = "\n".join(linhas)
    return texto_final if cor else _sem_cor(texto_final)
