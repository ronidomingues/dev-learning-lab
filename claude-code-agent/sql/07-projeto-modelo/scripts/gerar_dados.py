#!/usr/bin/env python3
"""Gera o banco `planta.db` do historiador de processo.

Só biblioteca padrão do Python — nada para instalar além do próprio Python.

O gerador é DETERMINÍSTICO: mesma semente, mesmo banco, byte a byte nos
valores. Isso é o que torna os testes em `testes/test_consultas.py` possíveis
e é a razão de o `.db` NÃO estar versionado no git — ele se reconstrói.

Anomalias plantadas de propósito (as consultas de `consultas/` existem para
achá-las; os testes verificam que acham):

  A1  Buraco de aquisição: nenhuma leitura entre 2026-07-14 03:00 e 05:00.
  A2  Sensor travado: TI-201 constante de 2026-07-08 10:00 a 11:30 (91 min).
  A3  Qualidade RUIM: AI-101 em 2026-07-21, das 06:00 às 12:00.
  A4  Leituras nulas: LI-101, 20 minutos espalhados, valor NULL + RUIM.
  A5  Excursão de temperatura: 2 bateladas passam de 195 °C (limite de alarme).
  A6  Batelada abortada: uma batelada termina em 3 h com rendimento baixo.
  A7  Erro de balanço de massa: ~8% das bateladas com soma de insumos ≠ carga.
  A8  Espículas de pressão: leituras isoladas de ~9,9 bar (falha de instrumento),
      com qualidade BOA — o flag de qualidade NÃO pega tudo.

Uso:
    python3 scripts/gerar_dados.py [caminho_do_banco] [--semente N] [--dias N]
"""

from __future__ import annotations

import argparse
import math
import os
import random
import sqlite3
import sys
from datetime import datetime, timedelta

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)

INICIO = datetime(2026, 7, 1, 0, 0, 0)
FMT = "%Y-%m-%d %H:%M:%S"

# Fases da batelada, em minutos a partir do início. (nome, minuto_final)
FASES = [("carga", 45), ("aquecimento", 120), ("reacao", 300),
         ("resfriamento", 345), ("descarga", 10 ** 9)]
DUR_BATELADA = 360          # 6 h — ciclo TEÓRICO da receita; o real varia
SETPOINT = 180.0            # °C no patamar de reação
AMBIENTE = 35.0             # °C

TAGS = ["TI-101", "PI-101", "LI-101", "SI-101", "AI-101",
        "FI-102", "TI-201", "FI-201"]


def ts(dt: datetime) -> str:
    return dt.strftime(FMT)


# ---------------------------------------------------------------------------
# 1. Linha do tempo: bateladas e paradas se alternando
# ---------------------------------------------------------------------------

def montar_linha_do_tempo(rng: random.Random, dias: int):
    """Devolve (bateladas, paradas). Cada batelada ocupa uma janela contínua."""
    fim_janela = INICIO + timedelta(days=dias)
    bateladas, paradas = [], []
    t = INICIO
    n = 0

    # Sorteio das paradas entre bateladas: a maioria é setup de rotina.
    catalogo_parada = (
        [("SETUP", 120, "Limpeza e carga de catalisador")] * 12
        + [("FALHA", 240, "Selo mecânico da bomba P-301")]
        + [("FALTA_INSUMO", 210, "Atraso na entrega de solvente")]
        + [("PROGRAMADA", 720, "Parada de manutenção preventiva")]
    )

    while t + timedelta(minutes=DUR_BATELADA) <= fim_janela:
        n += 1
        bid = f"B-2026-{n:04d}"
        carga = round(rng.uniform(4700, 5300), 1)
        abortada = (n == 40)
        excursao = n in (23, 57)
        # A batelada real quase nunca dura o ciclo teórico: a descarga demora,
        # o operador espera a análise de campo, a bomba não puxa. É essa
        # diferença que aparece como "índice de desempenho" no OEE.
        dur = 180 if abortada else DUR_BATELADA + rng.randrange(-5, 31)

        bateladas.append({
            "id": bid,
            "inicio": t,
            "fim": t + timedelta(minutes=dur),
            "dur": dur,
            "carga": carga,
            "abortada": abortada,
            "excursao": excursao,
            "operador": rng.choice(["A. Ferreira", "M. Nakagawa", "J. Duarte",
                                    "C. Rocha"]),
            "offset_sp": rng.gauss(0, 1.2),   # cada batelada acerta o SP um pouco diferente
        })

        t += timedelta(minutes=dur)

        if abortada:
            # Aborto vira parada por qualidade, ocupando o resto da janela.
            paradas.append(("R-101", t, t + timedelta(minutes=DUR_BATELADA - dur),
                            "QUALIDADE", "Batelada abortada: desvio de pH"))
            t += timedelta(minutes=DUR_BATELADA - dur)

        cat, dur_p, causa = catalogo_parada[rng.randrange(len(catalogo_parada))]
        fim_p = min(t + timedelta(minutes=dur_p), fim_janela)
        if fim_p > t:
            paradas.append(("R-101", t, fim_p, cat, causa))
        t = fim_p

    return bateladas, paradas


def indexar_estado(bateladas, total_min):
    """Vetor minuto→estado. Custa memória, mas deixa o cálculo do sinal trivial."""
    estado = [None] * total_min
    for b in bateladas:
        i0 = int((b["inicio"] - INICIO).total_seconds() // 60)
        for m in range(b["dur"]):
            i = i0 + m
            if 0 <= i < total_min:
                fase = next(f for f, lim in FASES if m < lim)
                estado[i] = (b, fase, m)
    return estado


# ---------------------------------------------------------------------------
# 2. Modelo do sinal de cada tag
# ---------------------------------------------------------------------------

def temperatura_reator(b, fase, m, min_ocioso):
    if b is None:
        # Resfriamento natural durante a parada: exponencial rumo ao ambiente.
        return AMBIENTE + 25.0 * math.exp(-min_ocioso / 45.0)
    sp = SETPOINT + b["offset_sp"]
    if fase == "carga":
        return AMBIENTE + 5.0 * (m / 45.0)
    if fase == "aquecimento":
        return 40.0 + (sp - 40.0) * ((m - 45) / 75.0)
    if fase == "reacao":
        base = sp
        if b["excursao"]:
            # Sobressinal do controle: um pico largo no meio do patamar.
            base += 18.0 * math.exp(-((m - 210) ** 2) / (2 * 35.0 ** 2))
        return base
    if fase == "resfriamento":
        return 60.0 + (sp - 60.0) * math.exp(-(m - 300) / 12.0)
    # Descarga: a fase que "sobra" quando a batelada estende. min(...,1) evita
    # extrapolar a rampa para fora do intervalo previsto.
    return 60.0 - 15.0 * min((m - 345) / 15.0, 1.0)


def valor_tag(tag, b, fase, m, min_ocioso, temp, rng):
    """Devolve o valor do tag naquele minuto, já com ruído."""
    if tag == "TI-101":
        return temp + rng.gauss(0, 0.35)

    if tag == "PI-101":
        p = 0.35 + max(0.0, temp - AMBIENTE) * 0.0165
        return p + rng.gauss(0, 0.02)

    if tag == "LI-101":
        if b is None:
            return 0.0 + abs(rng.gauss(0, 0.05))
        if fase == "carga":
            return 85.0 * (m / 45.0) + rng.gauss(0, 0.3)
        if fase == "descarga":
            return 84.0 * max(1 - (m - 345) / 15.0, 0.0) + rng.gauss(0, 0.4)
        return 84.5 + rng.gauss(0, 0.15)

    if tag == "SI-101":
        if b is None or fase == "descarga" or (fase == "carga" and m < 20):
            return 0.0
        return 90.0 + rng.gauss(0, 1.5)

    if tag == "AI-101":
        if b is None:
            return 7.0 + rng.gauss(0, 0.05)
        if fase in ("carga", "aquecimento"):
            return 7.2 + rng.gauss(0, 0.05)
        if fase == "reacao":
            # Esterificação consome ácido → pH cai e estabiliza perto de 4,6.
            return 4.6 + 2.6 * math.exp(-(m - 120) / 55.0) + rng.gauss(0, 0.06)
        return 4.65 + rng.gauss(0, 0.05)

    if tag == "FI-102":
        if b is not None and fase == "carga":
            return b["carga"] / 0.75 + rng.gauss(0, 40)   # kg em 45 min → kg/h
        return 0.0

    if tag == "TI-201":
        # Água de resfriamento: sai mais quente quanto maior a carga térmica.
        return 22.0 + 0.075 * max(0.0, temp - AMBIENTE) + rng.gauss(0, 0.25)

    if tag == "FI-201":
        if b is None:
            return 3000.0 + rng.gauss(0, 60)
        if fase in ("reacao", "resfriamento"):
            return 15000.0 + rng.gauss(0, 250)
        return 6000.0 + rng.gauss(0, 150)

    raise ValueError(tag)


# ---------------------------------------------------------------------------
# 3. Geração das leituras, com as anomalias plantadas
# ---------------------------------------------------------------------------

GAP_INI = datetime(2026, 7, 14, 3, 0, 0)
GAP_FIM = datetime(2026, 7, 14, 5, 0, 0)
TRAVADO_INI = datetime(2026, 7, 8, 10, 0, 0)
TRAVADO_FIM = datetime(2026, 7, 8, 11, 30, 0)
RUIM_INI = datetime(2026, 7, 21, 6, 0, 0)
RUIM_FIM = datetime(2026, 7, 21, 12, 0, 0)


def gerar_leituras(bateladas, total_min, rng):
    estado = indexar_estado(bateladas, total_min)
    min_ocioso = 0
    valor_travado = None
    nulos_restantes = 20
    minutos_nulos = sorted(rng.sample(range(total_min), 60))
    minutos_nulos = [x for x in minutos_nulos if 100 < x < total_min - 100][:20]
    conjunto_nulos = set(minutos_nulos)

    for i in range(total_min):
        agora = INICIO + timedelta(minutes=i)

        if GAP_INI <= agora < GAP_FIM:          # A1 — buraco de aquisição
            min_ocioso = min_ocioso + 1 if estado[i] is None else 0
            continue

        b, fase, m = estado[i] if estado[i] else (None, None, None)
        min_ocioso = 0 if b else min_ocioso + 1
        temp = temperatura_reator(b, fase, m, min_ocioso)

        for tag in TAGS:
            v = valor_tag(tag, b, fase, m, min_ocioso, temp, rng)
            q = "BOA"

            if tag == "TI-201" and TRAVADO_INI <= agora <= TRAVADO_FIM:  # A2
                if valor_travado is None:
                    valor_travado = round(v, 3)
                v = valor_travado
            elif tag == "TI-201":
                valor_travado = None

            if tag == "AI-101" and RUIM_INI <= agora < RUIM_FIM:          # A3
                q = "RUIM"
                v += 1.8            # sensor sujo: lê alto e ninguém percebe

            if tag == "LI-101" and i in conjunto_nulos and nulos_restantes > 0:  # A4
                nulos_restantes -= 1
                yield (tag, ts(agora), None, "RUIM")
                continue

            if tag == "PI-101" and rng.random() < 0.00012:                 # A8
                v = 9.9

            # Ruído de qualidade do coletor. Só rebaixa quem estava BOA —
            # senão o defeito plantado em A3 seria sobrescrito.
            if q == "BOA" and rng.random() < 0.002:
                q = "DUVIDOSA"

            yield (tag, ts(agora), round(v, 3), q)


# ---------------------------------------------------------------------------
# 4. Produção, laboratório, alarmes
# ---------------------------------------------------------------------------

INSUMOS = [("resina base", 0.60), ("solvente", 0.25),
           ("anidrido ftálico", 0.12), ("catalisador", 0.03)]


def gerar_producao(bateladas, rng):
    linhas_b, linhas_i = [], []
    for b in bateladas:
        if b["abortada"]:
            rend, status = 0.11, "ABORTADA"
        else:
            rend = 0.930 - (0.062 if b["excursao"] else 0.0) - rng.uniform(0, 0.022)
            status = "CONCLUIDA"
        b["produzido"] = round(b["carga"] * rend, 1)
        linhas_b.append((b["id"], "Resina alquídica AR-40", "R-101",
                         ts(b["inicio"]), ts(b["fim"]), b["carga"],
                         b["produzido"], status, b["operador"]))

        erro = rng.random() < 0.08                      # A7
        for nome, frac in INSUMOS:
            massa = b["carga"] * frac
            if erro and nome == "solvente":
                massa *= 1.12                           # erro de apontamento
            linhas_i.append((b["id"], nome, round(massa, 1)))
    return linhas_b, linhas_i


ESPECS = {
    "viscosidade":    ("cP",       400.0, 600.0, "ASTM D2196"),
    "indice_acidez":  ("mgKOH/g",  None,    2.5, "ASTM D1980"),
    "umidade":        ("%",        None,    0.5, "ASTM D1364"),
    "pureza":         ("%",       98.0,   None,  "cromatografia"),
}


def gerar_lab(bateladas, rng):
    linhas = []
    for b in bateladas:
        if b["abortada"]:
            continue                       # batelada abortada não vai ao lab
        coleta = b["fim"] - timedelta(minutes=15)
        resultado = coleta + timedelta(minutes=rng.randrange(120, 360))
        fora = rng.random() < 0.06         # alguma reprovação sem excursão
        for par, (un, li, ls, met) in ESPECS.items():
            if par == "viscosidade":
                v = 505 + (115 if b["excursao"] else 0) + rng.gauss(0, 22)
                if fora:
                    v += 130
            elif par == "indice_acidez":
                v = 1.35 + (0.9 if b["excursao"] else 0) + rng.gauss(0, 0.25)
            elif par == "umidade":
                v = 0.28 + rng.gauss(0, 0.06)
            else:
                v = 99.2 - (0.9 if b["excursao"] else 0) + rng.gauss(0, 0.25)
            linhas.append((b["id"], ts(coleta), ts(resultado), par,
                           round(v, 3), un, li, ls, met))
    return linhas


def gerar_alarmes(con, rng):
    """Deriva os alarmes das leituras já gravadas — assim os dois nunca divergem.

    Um SDCD real alarma no sinal bruto, então NÃO filtramos por qualidade aqui.
    Consequência didática: as espículas de pressão (A8) viram alarmes fantasma,
    exatamente como na vida real.
    """
    limites = con.execute("""
        SELECT tag_id, lim_inf_alarme, lim_sup_alarme FROM tag
         WHERE lim_inf_alarme IS NOT NULL OR lim_sup_alarme IS NOT NULL
    """).fetchall()

    eventos = []
    for tag_id, li, ls in limites:
        for lim, tipo, sinal in ((ls, "ALTO", 1), (li, "BAIXO", -1)):
            if lim is None:
                continue
            cond = "valor > ?" if sinal > 0 else "valor < ?"
            linhas = con.execute(
                f"SELECT ts FROM leitura WHERE tag_id=? AND valor IS NOT NULL "
                f"AND {cond} ORDER BY ts", (tag_id, lim)).fetchall()
            if not linhas:
                continue
            # Agrupa minutos consecutivos em um único evento.
            inicio = anterior = datetime.strptime(linhas[0][0], FMT)
            for (s,) in linhas[1:] + [("9999-12-31 00:00:00",)]:
                atual = datetime.strptime(s, FMT)
                if (atual - anterior) > timedelta(minutes=5):
                    dur = (anterior - inicio).total_seconds() / 60
                    prio = 1 if tag_id == "TI-101" else 2
                    ack = (ts(inicio + timedelta(minutes=rng.randrange(1, 9)))
                           if dur >= 2 else None)
                    eventos.append((tag_id, ts(inicio),
                                    "ALTO" if sinal > 0 else "BAIXO", prio, ack,
                                    ts(anterior + timedelta(minutes=1))))
                    inicio = atual
                anterior = atual
    return eventos


# ---------------------------------------------------------------------------
# 5. Montagem do banco
# ---------------------------------------------------------------------------

def executar_arquivo(con, nome):
    with open(os.path.join(RAIZ, "sql", nome), encoding="utf-8") as f:
        con.executescript(f.read())


def main() -> int:
    p = argparse.ArgumentParser(description="Gera o banco do historiador.")
    p.add_argument("banco", nargs="?", default=os.path.join(RAIZ, "planta.db"))
    p.add_argument("--semente", type=int, default=42)
    p.add_argument("--dias", type=int, default=30)
    a = p.parse_args()

    if os.path.exists(a.banco):
        os.remove(a.banco)
    for sufixo in ("-wal", "-shm"):
        if os.path.exists(a.banco + sufixo):
            os.remove(a.banco + sufixo)

    rng = random.Random(a.semente)
    con = sqlite3.connect(a.banco)
    con.execute("PRAGMA foreign_keys = ON")

    executar_arquivo(con, "001-esquema.sql")
    executar_arquivo(con, "002-views.sql")
    executar_arquivo(con, "003-seed-cadastro.sql")

    bateladas, paradas = montar_linha_do_tempo(rng, a.dias)
    linhas_b, linhas_i = gerar_producao(bateladas, rng)

    con.executemany("""INSERT INTO batelada (batelada_id, produto, equipamento_id,
                       ts_inicio, ts_fim, carga_kg, produzido_kg, status, operador)
                       VALUES (?,?,?,?,?,?,?,?,?)""", linhas_b)
    con.executemany("INSERT INTO consumo_insumo VALUES (?,?,?)", linhas_i)
    con.executemany("""INSERT INTO parada (equipamento_id, ts_inicio, ts_fim,
                       categoria, causa) VALUES (?,?,?,?,?)""",
                    [(e, ts(i), ts(f), c, ca) for e, i, f, c, ca in paradas])
    con.executemany("""INSERT INTO analise_lab (batelada_id, ts_coleta,
                       ts_resultado, parametro, valor, unidade, lim_inf, lim_sup,
                       metodo) VALUES (?,?,?,?,?,?,?,?,?)""",
                    gerar_lab(bateladas, rng))

    total_min = a.dias * 24 * 60
    # Uma transação só para 345 mil linhas. Uma transação POR LINHA levaria
    # minutos: cada COMMIT é um fsync. Ver 20-dml-e-transacoes.md.
    con.executemany("INSERT INTO leitura (tag_id, ts, valor, qualidade) "
                    "VALUES (?,?,?,?)",
                    gerar_leituras(bateladas, total_min, rng))
    con.commit()

    con.executemany("""INSERT INTO evento_alarme (tag_id, ts, tipo, prioridade,
                       ts_reconhecimento, ts_normalizacao) VALUES (?,?,?,?,?,?)""",
                    gerar_alarmes(con, rng))

    n_leituras = con.execute("SELECT COUNT(*) FROM leitura").fetchone()[0]
    con.execute("INSERT INTO carga_log (ts, descricao, linhas, semente) "
                "VALUES (datetime('now'), ?, ?, ?)",
                (f"carga sintética de {a.dias} dias", n_leituras, a.semente))
    con.commit()

    # ANALYZE alimenta as estatísticas que o planejador usa para escolher índice.
    con.execute("ANALYZE")
    con.commit()

    print(f"Banco criado em {a.banco}")
    for tabela in ("equipamento", "tag", "leitura", "batelada", "consumo_insumo",
                   "analise_lab", "evento_alarme", "parada"):
        n = con.execute(f"SELECT COUNT(*) FROM {tabela}").fetchone()[0]
        print(f"  {tabela:<16} {n:>8} linhas")
    con.close()
    tam = os.path.getsize(a.banco) / 1e6
    print(f"  {'tamanho':<16} {tam:>8.1f} MB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
