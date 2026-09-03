#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gerar_dados.py — gera a base do projeto-modelo "Tintas Aurora".

Distribuidora de tintas e resinas industriais. Gera CSVs em UTF-8 prontos para
serem consumidos pelo Power BI Desktop.

Só usa a biblioteca padrão do Python. Determinístico (semente fixa): rodar duas
vezes produz exatamente os mesmos arquivos.

    python3 gerar_dados.py [--saida dados] [--semente 20260814]

IMPORTANTE — os dados contêm OITO DEFEITOS PLANTADOS DE PROPÓSITO.
Eles estão documentados no README.md e são detectados por validar.py.
Dados limpos demais ensinam mal.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import math
import os
import random
import sys
from typing import Iterator

# ---------------------------------------------------------------------------
# Parâmetros do cenário
# ---------------------------------------------------------------------------

DATA_INICIO = dt.date(2024, 1, 1)
DATA_FIM = dt.date(2026, 7, 31)

# Sazonalidade mensal (índice 1..12). Construção civil e indústria caem em
# janeiro/fevereiro (férias coletivas) e aquecem no segundo semestre.
SAZONALIDADE = {
    1: 0.72, 2: 0.78, 3: 1.00, 4: 1.02, 5: 1.05, 6: 1.03,
    7: 1.08, 8: 1.12, 9: 1.15, 10: 1.18, 11: 1.10, 12: 0.85,
}

# Crescimento composto ao ano
CRESCIMENTO_ANUAL = 0.11

MEDIA_ITENS_POR_DIA_UTIL = 78

# ---------------------------------------------------------------------------
# Dimensões
# ---------------------------------------------------------------------------

# (Codigo, Produto, Categoria, Linha, CustoPadrao, MargemAlvo)
PRODUTOS = [
    ("TE-036", "Tinta Epóxi Bicomponente 3,6L", "Tintas", "Proteção Industrial", 128.40, 0.42),
    ("TE-180", "Tinta Epóxi Bicomponente 18L", "Tintas", "Proteção Industrial", 590.00, 0.40),
    ("TP-036", "Tinta Poliuretano Alifático 3,6L", "Tintas", "Proteção Industrial", 176.90, 0.44),
    ("TA-180", "Tinta Acrílica Industrial 18L", "Tintas", "Manutenção", 312.00, 0.33),
    ("TF-180", "Tinta de Demarcação Viária 18L", "Tintas", "Sinalização", 268.50, 0.30),
    ("PR-036", "Primer Epóxi Fosfato de Zinco 3,6L", "Tintas", "Proteção Industrial", 141.20, 0.38),
    ("PR-180", "Primer Anticorrosivo Óxido de Ferro 18L", "Tintas", "Manutenção", 402.00, 0.35),
    ("VP-050", "Verniz Poliuretano Bicomponente 5L", "Vernizes", "Acabamento", 231.00, 0.46),
    ("VA-050", "Verniz Acrílico Fosco 5L", "Vernizes", "Acabamento", 168.00, 0.41),
    ("RA-200", "Resina Alquídica Longa em Óleo 200L", "Resinas", "Matéria-prima", 3980.00, 0.18),
    ("RA-020", "Resina Alquídica Longa em Óleo 20L", "Resinas", "Matéria-prima", 452.00, 0.22),
    ("RE-200", "Resina Epóxi Base Bisfenol A 200L", "Resinas", "Matéria-prima", 6120.00, 0.16),
    ("RE-020", "Resina Epóxi Base Bisfenol A 20L", "Resinas", "Matéria-prima", 690.00, 0.20),
    ("SX-005", "Solvente Xilol 5L", "Solventes", "Auxiliares", 62.30, 0.28),
    ("SX-200", "Solvente Xilol 200L", "Solventes", "Auxiliares", 2180.00, 0.19),
    ("ST-005", "Thinner Acrílico 5L", "Solventes", "Auxiliares", 48.90, 0.31),
    ("SA-005", "Solvente Aguarrás Mineral 5L", "Solventes", "Auxiliares", 41.20, 0.29),
    ("AD-001", "Aditivo Antiespumante 1L", "Aditivos", "Auxiliares", 96.70, 0.48),
    ("AD-005", "Aditivo Secante de Cobalto 5L", "Aditivos", "Auxiliares", 284.00, 0.45),
    ("EP-025", "Endurecedor Poliamida 25L", "Aditivos", "Proteção Industrial", 1240.00, 0.24),
    ("PG-001", "Pigmento Dióxido de Titânio 1kg", "Pigmentos", "Matéria-prima", 58.40, 0.26),
    ("PG-025", "Pigmento Óxido de Ferro Vermelho 25kg", "Pigmentos", "Matéria-prima", 720.00, 0.23),
    ("EQ-001", "Kit Pistola HVLP Profissional", "Equipamentos", "Aplicação", 1180.00, 0.34),
    ("EQ-002", "Rolo de Lã Natural 23cm (cx 12)", "Equipamentos", "Aplicação", 214.00, 0.36),
    ("EQ-003", "EPI Respirador Semifacial + Filtros", "Equipamentos", "Segurança", 168.00, 0.39),
]

# (Vendedor, Equipe, UF base)
VENDEDORES = [
    ("Ana Beatriz Ramalho", "Sudeste", "SP"),
    ("Bruno Sakamoto", "Sudeste", "SP"),
    ("Carla Duarte Pinho", "Sudeste", "MG"),
    ("Diego Fontenele", "Sudeste", "RJ"),
    ("Eduarda Vasques", "Sul", "PR"),
    ("Fábio Kunzler", "Sul", "RS"),
    ("Giovana Belmiro", "Sul", "SC"),
    ("Heitor Nascimento", "Nordeste", "PE"),
    ("Isadora Quintela", "Nordeste", "BA"),
    ("João Marcelo Prates", "Nordeste", "CE"),
    ("Kelly Amorim", "Centro-Oeste", "GO"),
    ("Lucas Bittencourt", "Centro-Oeste", "MT"),
]

SEGMENTOS = [
    ("Indústria Química", 0.24),
    ("Construção Civil", 0.28),
    ("Metalmecânica", 0.19),
    ("Naval e Offshore", 0.07),
    ("Revenda", 0.16),
    ("Governo", 0.06),
]

UF_REGIAO = {
    "SP": ("Sudeste", ["São Paulo", "Campinas", "Santo André", "Sorocaba", "São José dos Campos"]),
    "MG": ("Sudeste", ["Belo Horizonte", "Contagem", "Uberlândia", "Betim"]),
    "RJ": ("Sudeste", ["Rio de Janeiro", "Duque de Caxias", "Macaé", "Volta Redonda"]),
    "PR": ("Sul", ["Curitiba", "Londrina", "Araucária", "Maringá"]),
    "RS": ("Sul", ["Porto Alegre", "Caxias do Sul", "Canoas", "Triunfo"]),
    "SC": ("Sul", ["Joinville", "Blumenau", "Itajaí", "Criciúma"]),
    "PE": ("Nordeste", ["Recife", "Suape", "Caruaru", "Jaboatão"]),
    "BA": ("Nordeste", ["Salvador", "Camaçari", "Feira de Santana", "Candeias"]),
    "CE": ("Nordeste", ["Fortaleza", "Maracanaú", "Pecém"]),
    "GO": ("Centro-Oeste", ["Goiânia", "Anápolis", "Aparecida de Goiânia"]),
    "MT": ("Centro-Oeste", ["Cuiabá", "Rondonópolis", "Várzea Grande"]),
}

RAZAO_SOCIAL_1 = [
    "Metalúrgica", "Indústria", "Tintas", "Construtora", "Estaleiro", "Química",
    "Engenharia", "Distribuidora", "Comercial", "Siderúrgica", "Manutenção",
    "Revestimentos", "Serviços", "Usina", "Refinaria",
]
RAZAO_SOCIAL_2 = [
    "Anhanguera", "Bandeirantes", "Cerrado", "Diamantina", "Estrela", "Farroupilha",
    "Guarani", "Horizonte", "Itamaraty", "Jaraguá", "Kalunga", "Litoral",
    "Mantiqueira", "Nordestina", "Oceânica", "Paranapanema", "Quaraí", "Rio Doce",
    "Serra Azul", "Tapajós", "Uruguaiana", "Vale Verde", "Xingu", "Yguaçu", "Zumbi",
    "Aurora", "Boreal", "Continental", "Delta", "Equatorial",
]
RAZAO_SOCIAL_3 = ["Ltda", "S.A.", "ME", "EIRELI", "Ltda", "S.A."]

MOTIVOS_TIPO = ["Venda"] * 97 + ["Devolucao"] * 3


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------

def dias(inicio: dt.date, fim: dt.date) -> Iterator[dt.date]:
    d = inicio
    um = dt.timedelta(days=1)
    while d <= fim:
        yield d
        d += um


def eh_dia_util(d: dt.date) -> bool:
    return d.weekday() < 5


def formata_cnpj(n: int) -> str:
    s = f"{n:014d}"
    return f"{s[0:2]}.{s[2:5]}.{s[5:8]}/{s[8:12]}-{s[12:14]}"


def escolhe_ponderado(rng: random.Random, pares) -> str:
    total = sum(p for _, p in pares)
    x = rng.random() * total
    acumulado = 0.0
    for valor, peso in pares:
        acumulado += peso
        if x <= acumulado:
            return valor
    return pares[-1][0]


def escreve_csv(caminho: str, cabecalho: list[str], linhas: list[list]) -> int:
    with open(caminho, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter=",", quoting=csv.QUOTE_MINIMAL)
        w.writerow(cabecalho)
        w.writerows(linhas)
    return len(linhas)


MESES_PT = ["jan", "fev", "mar", "abr", "mai", "jun",
            "jul", "ago", "set", "out", "nov", "dez"]
DIAS_PT = ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"]


# ---------------------------------------------------------------------------
# Geração das dimensões
# ---------------------------------------------------------------------------

def gerar_calendario() -> list[list]:
    linhas = []
    for d in dias(dt.date(DATA_INICIO.year, 1, 1), dt.date(DATA_FIM.year, 12, 31)):
        trimestre = (d.month - 1) // 3 + 1
        linhas.append([
            d.isoformat(),
            d.year,
            d.month,
            MESES_PT[d.month - 1],
            f"{d.year}-{d.month:02d}",
            f"T{trimestre}",
            f"{d.year}-T{trimestre}",
            d.day,
            DIAS_PT[d.weekday()],
            d.weekday() + 1,
            "Sim" if eh_dia_util(d) else "Não",
            d.timetuple().tm_yday,
            # índice contínuo de mês: permite deslocamento sem função de tempo
            (d.year - DATA_INICIO.year) * 12 + d.month - 1,
        ])
    return linhas


def gerar_produtos() -> list[list]:
    linhas = []
    for i, (cod, nome, cat, linha, custo, margem) in enumerate(PRODUTOS, start=1):
        preco_tabela = round(custo / (1 - margem), 2)
        linhas.append([i, cod, nome, cat, linha, f"{custo:.2f}", f"{preco_tabela:.2f}", "Sim"])
    return linhas


def gerar_vendedores() -> list[list]:
    linhas = []
    for i, (nome, equipe, uf) in enumerate(VENDEDORES, start=1):
        partes = nome.lower().split()
        email = f"{partes[0]}.{partes[-1]}@tintasaurora.com.br"
        email = (email.replace("á", "a").replace("ã", "a").replace("é", "e")
                      .replace("ê", "e").replace("í", "i").replace("ó", "o")
                      .replace("ô", "o").replace("ú", "u").replace("ç", "c"))
        linhas.append([i, nome, equipe, uf, email])
    return linhas


def gerar_clientes(rng: random.Random, n: int) -> list[list]:
    linhas = []
    vistos = set()
    for i in range(1, n + 1):
        while True:
            nome = (f"{rng.choice(RAZAO_SOCIAL_1)} {rng.choice(RAZAO_SOCIAL_2)} "
                    f"{rng.choice(RAZAO_SOCIAL_3)}")
            if nome not in vistos:
                vistos.add(nome)
                break
        uf = rng.choice(list(UF_REGIAO.keys()))
        regiao, cidades = UF_REGIAO[uf]
        segmento = escolhe_ponderado(rng, SEGMENTOS)
        cnpj = formata_cnpj(rng.randrange(10_000_000_000_000, 99_999_999_999_999))
        porte = escolhe_ponderado(rng, [("Pequeno", 0.55), ("Médio", 0.33), ("Grande", 0.12)])
        linhas.append([i, cnpj, nome, segmento, porte, uf, regiao, rng.choice(cidades)])
    return linhas


# ---------------------------------------------------------------------------
# Geração dos fatos
# ---------------------------------------------------------------------------

def gerar_vendas(rng: random.Random, produtos: list[list], clientes: list[list],
                 vendedores: list[list]) -> tuple[list[list], dict]:
    """Gera as linhas de fVendas. Devolve (linhas, estatísticas dos defeitos)."""
    linhas: list[list] = []
    defeitos = {
        "orfaos_produto": 0,
        "devolucao_positiva": 0,
        "desconto_fora_de_escala": 0,
        "preco_zero": 0,
        "data_absurda": 0,
    }

    # Peso de cada produto (curva ABC realista: poucos produtos dominam)
    pesos_produto = []
    for idx, p in enumerate(produtos):
        cat = p[3]
        base = {"Tintas": 1.00, "Vernizes": 0.45, "Resinas": 0.30,
                "Solventes": 0.75, "Aditivos": 0.40, "Pigmentos": 0.35,
                "Equipamentos": 0.55}.get(cat, 0.5)
        # decaimento exponencial por posição, para gerar Pareto
        linhas_peso = base * math.exp(-idx / 9.0)
        pesos_produto.append((p[0], linhas_peso))

    # Peso de cliente: distribuição de cauda longa
    pesos_cliente = [(c[0], 1.0 / (1.0 + (i / 40.0) ** 1.6)) for i, c in enumerate(clientes)]

    # Mapa UF -> vendedores daquela região
    por_equipe: dict[str, list[int]] = {}
    for v in vendedores:
        por_equipe.setdefault(v[2], []).append(v[0])

    prod_por_sk = {p[0]: p for p in produtos}
    cli_por_sk = {c[0]: c for c in clientes}

    nf = 100000
    for d in dias(DATA_INICIO, DATA_FIM):
        if not eh_dia_util(d):
            # sábado tem movimento residual
            if d.weekday() == 5 and rng.random() < 0.25:
                fator_dia = 0.15
            else:
                continue
        else:
            fator_dia = 1.0

        anos_decorridos = (d - DATA_INICIO).days / 365.25
        fator_cresc = (1 + CRESCIMENTO_ANUAL) ** anos_decorridos
        fator_mes = SAZONALIDADE[d.month]
        # ruído diário
        fator_ruido = rng.gauss(1.0, 0.18)
        fator_ruido = max(0.35, fator_ruido)

        qtd_itens = int(round(MEDIA_ITENS_POR_DIA_UTIL * fator_dia * fator_cresc
                              * fator_mes * fator_ruido))
        qtd_itens = max(0, qtd_itens)

        i = 0
        while i < qtd_itens:
            nf += 1
            sk_cliente = escolhe_ponderado(rng, pesos_cliente)
            cliente = cli_por_sk[sk_cliente]
            uf_cliente = cliente[5]
            regiao_cliente = cliente[6]
            candidatos = por_equipe.get(regiao_cliente) or [v[0] for v in vendedores]
            sk_vendedor = rng.choice(candidatos)

            itens_na_nf = min(rng.choice([1, 1, 1, 2, 2, 3, 4, 6]), qtd_itens - i)
            prazo = rng.choice([2, 3, 3, 4, 5, 5, 7, 10, 15])
            data_entrega = d + dt.timedelta(days=prazo)

            usados = set()
            for item in range(1, itens_na_nf + 1):
                sk_produto = escolhe_ponderado(rng, pesos_produto)
                tentativas = 0
                while sk_produto in usados and tentativas < 5:
                    sk_produto = escolhe_ponderado(rng, pesos_produto)
                    tentativas += 1
                usados.add(sk_produto)

                produto = prod_por_sk[sk_produto]
                custo_padrao = float(produto[5])
                preco_tabela = float(produto[6])

                # quantidade depende do porte da embalagem (heurística pelo custo)
                if custo_padrao > 2000:
                    quantidade = rng.choice([1, 1, 1, 2, 2, 3])
                elif custo_padrao > 400:
                    quantidade = rng.choice([1, 2, 2, 3, 4, 5, 8])
                elif custo_padrao > 100:
                    quantidade = rng.choice([2, 4, 5, 6, 10, 12, 20])
                else:
                    quantidade = rng.choice([6, 10, 12, 20, 24, 40, 60, 100])

                # desconto por porte do cliente e por volume
                base_desc = {"Pequeno": 0.02, "Médio": 0.05, "Grande": 0.09}[cliente[4]]
                desconto = base_desc + min(0.10, quantidade / 600.0) + rng.gauss(0, 0.015)
                desconto = round(min(0.35, max(0.0, desconto)), 4)

                # preço praticado oscila em torno da tabela
                preco = round(preco_tabela * rng.gauss(1.0, 0.03), 2)
                preco = max(round(custo_padrao * 1.02, 2), preco)

                # custo real oscila (compra, câmbio)
                custo = round(custo_padrao * rng.gauss(1.0, 0.045), 2)

                tipo = rng.choice(MOTIVOS_TIPO)
                if tipo == "Devolucao":
                    quantidade = -quantidade

                data_venda = d
                data_ent = data_entrega

                # ---------------- DEFEITOS PLANTADOS ----------------

                # (1) produto órfão: SK que não existe na dimensão
                if rng.random() < 0.0007:
                    sk_produto = 999
                    defeitos["orfaos_produto"] += 1

                # (3) devolução lançada com quantidade positiva (erro de digitação)
                if tipo == "Devolucao" and rng.random() < 0.22:
                    quantidade = abs(quantidade)
                    defeitos["devolucao_positiva"] += 1

                # (5) desconto digitado em pontos percentuais (15 em vez de 0,15)
                if rng.random() < 0.0006:
                    desconto = round(desconto * 100, 2)
                    if desconto > 1:      # só conta o que é observável na auditoria
                        defeitos["desconto_fora_de_escala"] += 1

                # (6) bonificação lançada com preço zero
                if rng.random() < 0.0015:
                    preco = 0.0
                    defeitos["preco_zero"] += 1

                # (4) data digitada com o século errado
                if rng.random() < 0.00025:
                    data_venda = d.replace(year=d.year + 100)
                    data_ent = data_venda + dt.timedelta(days=prazo)
                    defeitos["data_absurda"] += 1

                linhas.append([
                    nf, item,
                    data_venda.isoformat(),
                    data_ent.isoformat(),
                    sk_produto, sk_cliente, sk_vendedor,
                    quantidade,
                    f"{preco:.2f}",
                    f"{desconto:.4f}",
                    f"{custo:.2f}",
                    tipo,
                ])
            i += itens_na_nf

    return linhas, defeitos


def gerar_metas(rng: random.Random, vendas: list[list],
                vendedores: list[list]) -> tuple[list[list], int]:
    """Metas mensais por vendedor, calibradas ~8% acima do realizado do ano anterior."""
    realizado: dict[tuple[str, int], float] = {}
    for r in vendas:
        data = r[2]
        if data[:4] > "2100":            # ignora o defeito de data absurda
            continue
        anomes = data[:7]
        sk_vend = r[6]
        qtd = int(r[7])
        preco = float(r[8])
        desc = float(r[9])
        if desc > 1:                      # ignora o defeito de escala de desconto
            desc = desc / 100
        realizado[(anomes, sk_vend)] = realizado.get((anomes, sk_vend), 0.0) + \
            qtd * preco * (1 - desc)

    linhas = []
    faltantes = 0
    anomeses = sorted({k[0] for k in realizado})
    for anomes in anomeses:
        for v in vendedores:
            sk = v[0]
            base = realizado.get((anomes, sk), 0.0)
            if base <= 0:
                base = 120_000.0
            meta = base * rng.uniform(1.02, 1.16)

            # (7) DEFEITO PLANTADO: metas faltando para alguns pares mês/vendedor
            if rng.random() < 0.02:
                faltantes += 1
                continue

            linhas.append([anomes, sk, f"{round(meta, -2):.2f}"])
    return linhas, faltantes


def gerar_seguranca(vendedores: list[list]) -> list[list]:
    linhas = []
    for v in vendedores:
        linhas.append([v[4], v[0], "Vendedor", ""])
    linhas.append(["gerente.sudeste@tintasaurora.com.br", 0, "Equipe", "Sudeste"])
    linhas.append(["gerente.sul@tintasaurora.com.br", 0, "Equipe", "Sul"])
    linhas.append(["gerente.nordeste@tintasaurora.com.br", 0, "Equipe", "Nordeste"])
    linhas.append(["gerente.co@tintasaurora.com.br", 0, "Equipe", "Centro-Oeste"])
    linhas.append(["diretoria@tintasaurora.com.br", 0, "Tudo", ""])
    return linhas


# ---------------------------------------------------------------------------
# Defeito 2 (cliente duplicado) e defeito 8 (UF suja)
# ---------------------------------------------------------------------------

def plantar_cliente_duplicado(rng: random.Random, clientes: list[list],
                              vendas: list[list]) -> int:
    """(2) Cria uma segunda SK para clientes já existentes, com o MESMO CNPJ.

    Simula o recadastro após mudança de razão social — causa clássica de
    contagem distinta inflada.
    """
    alvos = rng.sample(range(min(60, len(clientes))), 6)
    proximo_sk = max(c[0] for c in clientes) + 1
    mapa_dup = {}
    for idx in alvos:
        original = clientes[idx]
        novo = list(original)
        novo[0] = proximo_sk
        novo[2] = original[2] + " (NOVA RAZAO SOCIAL)"
        clientes.append(novo)
        mapa_dup[original[0]] = proximo_sk
        proximo_sk += 1

    # Metade das vendas recentes desses clientes passa a apontar para a SK nova
    movidas = 0
    for r in vendas:
        if r[5] in mapa_dup and r[2] >= "2026-01-01" and rng.random() < 0.5:
            r[5] = mapa_dup[r[5]]
            movidas += 1
    return len(mapa_dup)


def sujar_uf(rng: random.Random, clientes: list[list]) -> int:
    """(8) Sujeira de cadastro em UF: caixa e espaços inconsistentes."""
    sujos = 0
    for c in clientes:
        x = rng.random()
        if x < 0.012:
            c[5] = c[5].lower()
            sujos += 1
        elif x < 0.020:
            c[5] = " " + c[5]
            sujos += 1
        elif x < 0.026:
            c[5] = c[5] + " "
            sujos += 1
    return sujos


# ---------------------------------------------------------------------------
# Principal
# ---------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description="Gera a base do projeto-modelo Tintas Aurora.")
    ap.add_argument("--saida", default="dados", help="pasta de saída (padrão: dados)")
    ap.add_argument("--semente", type=int, default=20260814, help="semente aleatória")
    ap.add_argument("--clientes", type=int, default=420, help="quantidade de clientes")
    args = ap.parse_args()

    rng = random.Random(args.semente)
    os.makedirs(args.saida, exist_ok=True)

    print("Gerando dimensões...")
    calendario = gerar_calendario()
    produtos = gerar_produtos()
    vendedores = gerar_vendedores()
    clientes = gerar_clientes(rng, args.clientes)

    print("Gerando fVendas (pode levar alguns segundos)...")
    vendas, defeitos = gerar_vendas(rng, produtos, clientes, vendedores)

    print("Plantando defeitos de cadastro...")
    n_dup = plantar_cliente_duplicado(rng, clientes, vendas)
    n_uf = sujar_uf(rng, clientes)

    print("Gerando fMetas...")
    metas, metas_faltantes = gerar_metas(rng, vendas, vendedores)
    seguranca = gerar_seguranca(vendedores)

    p = lambda nome: os.path.join(args.saida, nome)

    n = {}
    n["dCalendario"] = escreve_csv(
        p("dCalendario.csv"),
        ["Data", "Ano", "NumMes", "Mes", "AnoMes", "Trimestre", "AnoTrimestre",
         "Dia", "DiaSemana", "NumDiaSemana", "DiaUtil", "DiaDoAno", "IndiceMes"],
        calendario)
    n["dProduto"] = escreve_csv(
        p("dProduto.csv"),
        ["SK_Produto", "Codigo", "Produto", "Categoria", "Linha",
         "CustoPadrao", "PrecoTabela", "Ativo"],
        produtos)
    n["dCliente"] = escreve_csv(
        p("dCliente.csv"),
        ["SK_Cliente", "CNPJ", "Cliente", "Segmento", "Porte", "UF", "Regiao", "Cidade"],
        clientes)
    n["dVendedor"] = escreve_csv(
        p("dVendedor.csv"),
        ["SK_Vendedor", "Vendedor", "Equipe", "UFBase", "Email"],
        vendedores)
    n["fVendas"] = escreve_csv(
        p("fVendas.csv"),
        ["NF", "ItemNF", "Data", "DataEntrega", "SK_Produto", "SK_Cliente",
         "SK_Vendedor", "Quantidade", "PrecoUnitario", "Desconto",
         "CustoUnitario", "Tipo"],
        vendas)
    n["fMetas"] = escreve_csv(
        p("fMetas.csv"),
        ["AnoMes", "SK_Vendedor", "MetaValor"],
        metas)
    n["dSeguranca"] = escreve_csv(
        p("dSeguranca.csv"),
        ["Email", "SK_Vendedor", "Escopo", "Equipe"],
        seguranca)

    print()
    print("=" * 66)
    print("ARQUIVOS GERADOS em", os.path.abspath(args.saida))
    print("=" * 66)
    total_bytes = 0
    for nome, qtd in n.items():
        caminho = p(nome + ".csv")
        tam = os.path.getsize(caminho)
        total_bytes += tam
        print(f"  {nome:<14} {qtd:>9,} linhas   {tam/1024/1024:>7.2f} MB"
              .replace(",", "."))
    print(f"  {'TOTAL':<14} {'':>9}          {total_bytes/1024/1024:>7.2f} MB")

    print()
    print("=" * 66)
    print("DEFEITOS PLANTADOS (de propósito — veja README.md)")
    print("=" * 66)
    print(f"  1. Vendas com produto órfão (SK 999) ........ {defeitos['orfaos_produto']:>6}")
    print(f"  2. Clientes duplicados (mesmo CNPJ) ......... {n_dup:>6}")
    print(f"  3. Devoluções com quantidade positiva ....... {defeitos['devolucao_positiva']:>6}")
    print(f"  4. Datas com século errado (ano +100) ....... {defeitos['data_absurda']:>6}")
    print(f"  5. Desconto em escala errada (>1) ........... {defeitos['desconto_fora_de_escala']:>6}")
    print(f"  6. Linhas com preço unitário zero ........... {defeitos['preco_zero']:>6}")
    print(f"  7. Metas faltando (mês/vendedor) ............ {metas_faltantes:>6}")
    print(f"  8. UF com caixa/espaço inconsistente ........ {n_uf:>6}")
    print()
    print("Próximo passo:  python3 validar.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
