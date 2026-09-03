#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
validar.py — auditoria da base do projeto-modelo "Tintas Aurora".

Faz três coisas:

  1. AUDITA a integridade dos dados (o que um projeto de BI sério faz ANTES
     de qualquer gráfico) e encontra os oito defeitos plantados.
  2. Calcula os NÚMEROS DE REFERÊNCIA (gabarito) que o modelo do Power BI
     precisa reproduzir. Se o seu DAX não bater com isto, o DAX está errado.
  3. Verifica a CONSISTÊNCIA entre os CSVs e a definição do modelo em TMDL
     (colunas declaradas × colunas existentes).

Só usa a biblioteca padrão do Python.

    python3 validar.py [--dados dados] [--modelo modelo]

Código de saída: 0 se todas as verificações estruturais passarem, 1 se alguma
falhar. Os defeitos plantados NÃO fazem falhar — eles são esperados, e o
relatório mostra a contagem de cada um.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import os
import re
import sys
from collections import Counter, defaultdict

VERDE = "\033[92m"
VERMELHO = "\033[91m"
AMARELO = "\033[93m"
CINZA = "\033[90m"
FIM = "\033[0m"


class Relatorio:
    def __init__(self) -> None:
        self.ok = 0
        self.falhas = 0
        self.avisos = 0

    def secao(self, titulo: str) -> None:
        print()
        print("=" * 70)
        print(titulo)
        print("=" * 70)

    def verifica(self, descricao: str, condicao: bool, detalhe: str = "") -> bool:
        if condicao:
            self.ok += 1
            print(f"  {VERDE}ok{FIM}    {descricao}")
        else:
            self.falhas += 1
            print(f"  {VERMELHO}FALHA{FIM} {descricao}")
            if detalhe:
                print(f"        {CINZA}{detalhe}{FIM}")
        return condicao

    def achado(self, descricao: str, quantidade: int, esperado_min: int = 1) -> None:
        """Um defeito plantado: esperado, mas precisa aparecer."""
        if quantidade >= esperado_min:
            self.avisos += 1
            print(f"  {AMARELO}achado{FIM}  {descricao}: {quantidade}")
        else:
            self.falhas += 1
            print(f"  {VERMELHO}FALHA{FIM}   {descricao}: esperava >= {esperado_min}, "
                  f"achou {quantidade}")

    def info(self, rotulo: str, valor) -> None:
        print(f"  {CINZA}·{FIM}     {rotulo:<44} {valor}")


def ler(caminho: str) -> list[dict]:
    with open(caminho, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def brl(v: float) -> str:
    s = f"{v:,.2f}"
    return "R$ " + s.replace(",", "@").replace(".", ",").replace("@", ".")


def num(v: float) -> str:
    return f"{v:,.0f}".replace(",", ".")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dados", default="dados")
    ap.add_argument("--modelo", default="modelo")
    args = ap.parse_args()

    r = Relatorio()

    # ------------------------------------------------------------------
    # Carga
    # ------------------------------------------------------------------
    r.secao("1 · CARGA DOS ARQUIVOS")

    arquivos = ["dCalendario", "dProduto", "dCliente", "dVendedor",
                "fVendas", "fMetas", "dSeguranca"]
    tabelas: dict[str, list[dict]] = {}
    for nome in arquivos:
        caminho = os.path.join(args.dados, nome + ".csv")
        existe = os.path.exists(caminho)
        r.verifica(f"{nome}.csv existe", existe,
                   f"esperado em {os.path.abspath(caminho)} — rode gerar_dados.py")
        if not existe:
            return 1
        tabelas[nome] = ler(caminho)
        r.info(f"{nome} carregada", f"{num(len(tabelas[nome]))} linhas")

    cal = tabelas["dCalendario"]
    prod = tabelas["dProduto"]
    cli = tabelas["dCliente"]
    vend = tabelas["dVendedor"]
    vendas = tabelas["fVendas"]
    metas = tabelas["fMetas"]
    seg = tabelas["dSeguranca"]

    # ------------------------------------------------------------------
    # Chaves e unicidade
    # ------------------------------------------------------------------
    r.secao("2 · CHAVES PRIMÁRIAS (o lado '1' de cada relacionamento)")

    def unica(linhas: list[dict], coluna: str) -> tuple[bool, list]:
        vals = [l[coluna] for l in linhas]
        c = Counter(vals)
        dups = [k for k, v in c.items() if v > 1]
        return (len(dups) == 0, dups)

    for tabela, chave in [("dCalendario", "Data"), ("dProduto", "SK_Produto"),
                          ("dCliente", "SK_Cliente"), ("dVendedor", "SK_Vendedor")]:
        ok, dups = unica(tabelas[tabela], chave)
        r.verifica(f"{tabela}[{chave}] é única",
                   ok, f"duplicadas: {dups[:5]}")

    # Chave composta de fVendas
    chaves_venda = [(l["NF"], l["ItemNF"]) for l in vendas]
    r.verifica("fVendas[NF]+[ItemNF] é única",
               len(set(chaves_venda)) == len(chaves_venda),
               f"{len(chaves_venda) - len(set(chaves_venda))} duplicadas")

    chaves_meta = [(l["AnoMes"], l["SK_Vendedor"]) for l in metas]
    r.verifica("fMetas[AnoMes]+[SK_Vendedor] é única",
               len(set(chaves_meta)) == len(chaves_meta))

    # ------------------------------------------------------------------
    # Integridade referencial
    # ------------------------------------------------------------------
    r.secao("3 · INTEGRIDADE REFERENCIAL (o filtro vai chegar ao fato?)")

    sk_prod = {l["SK_Produto"] for l in prod}
    sk_cli = {l["SK_Cliente"] for l in cli}
    sk_vend = {l["SK_Vendedor"] for l in vend}
    datas_cal = {l["Data"] for l in cal}

    orfaos_prod = [l for l in vendas if l["SK_Produto"] not in sk_prod]
    orfaos_cli = [l for l in vendas if l["SK_Cliente"] not in sk_cli]
    orfaos_vend = [l for l in vendas if l["SK_Vendedor"] not in sk_vend]
    orfaos_data = [l for l in vendas if l["Data"] not in datas_cal]
    orfaos_entrega = [l for l in vendas if l["DataEntrega"] not in datas_cal]

    r.verifica("fVendas[SK_Cliente] → dCliente sem órfãos", len(orfaos_cli) == 0,
               f"{len(orfaos_cli)} órfãos")
    r.verifica("fVendas[SK_Vendedor] → dVendedor sem órfãos", len(orfaos_vend) == 0,
               f"{len(orfaos_vend)} órfãos")

    metas_orfas = [l for l in metas if l["SK_Vendedor"] not in sk_vend]
    r.verifica("fMetas[SK_Vendedor] → dVendedor sem órfãos", len(metas_orfas) == 0)

    meses_cal = {l["AnoMes"] for l in cal}
    metas_mes_orfa = [l for l in metas if l["AnoMes"] not in meses_cal]
    r.verifica("fMetas[AnoMes] → dCalendario sem órfãos", len(metas_mes_orfa) == 0)

    # ------------------------------------------------------------------
    # Os oito defeitos plantados
    # ------------------------------------------------------------------
    r.secao("4 · DEFEITOS PLANTADOS (esperados — cada um ensina uma coisa)")

    # (1) produto órfão
    r.achado("(1) vendas com SK_Produto inexistente (vira 'Em branco' no visual)",
             len(orfaos_prod))
    if orfaos_prod:
        r.info("    SKs órfãos encontradas",
               sorted({l["SK_Produto"] for l in orfaos_prod}))
        valor_orfao = sum(int(l["Quantidade"]) * float(l["PrecoUnitario"])
                          for l in orfaos_prod)
        r.info("    faturamento bruto preso no órfão", brl(valor_orfao))

    # (2) cliente duplicado por CNPJ
    por_cnpj = defaultdict(list)
    for l in cli:
        por_cnpj[l["CNPJ"]].append(l["SK_Cliente"])
    dup_cnpj = {k: v for k, v in por_cnpj.items() if len(v) > 1}
    r.achado("(2) CNPJs com mais de uma SK_Cliente (contagem distinta infla)",
             len(dup_cnpj))
    if dup_cnpj:
        exemplo = next(iter(dup_cnpj.items()))
        r.info("    exemplo", f"CNPJ {exemplo[0]} → SKs {exemplo[1]}")
        r.info("    clientes distintos por SK", num(len(sk_cli)))
        r.info("    clientes distintos por CNPJ (o número certo)",
               num(len(por_cnpj)))

    # (3) devolução com quantidade positiva
    dev_positiva = [l for l in vendas
                    if l["Tipo"] == "Devolucao" and int(l["Quantidade"]) > 0]
    dev_total = [l for l in vendas if l["Tipo"] == "Devolucao"]
    r.achado("(3) devoluções com quantidade POSITIVA (somam em vez de subtrair)",
             len(dev_positiva))
    r.info("    devoluções no total", num(len(dev_total)))

    # (4) datas absurdas
    r.achado("(4) vendas com data fora do calendário (século errado)",
             len(orfaos_data))
    if orfaos_data:
        r.info("    exemplos", sorted({l["Data"] for l in orfaos_data})[:3])
    if orfaos_entrega:
        r.info("    idem em DataEntrega", len(orfaos_entrega))

    # (5) desconto fora de escala
    desc_ruim = [l for l in vendas if float(l["Desconto"]) > 1]
    r.achado("(5) desconto > 1 (digitado em pontos percentuais)", len(desc_ruim))
    if desc_ruim:
        pior = max(desc_ruim, key=lambda l: float(l["Desconto"]))
        impacto = (int(pior["Quantidade"]) * float(pior["PrecoUnitario"])
                   * (1 - float(pior["Desconto"])))
        r.info("    pior caso (desconto)", pior["Desconto"])
        r.info("    faturamento líquido dessa linha", brl(impacto))

    # (6) preço zero
    preco_zero = [l for l in vendas if float(l["PrecoUnitario"]) == 0]
    r.achado("(6) linhas com preço unitário zero (bonificação sem marcação)",
             len(preco_zero))

    # (7) metas faltantes
    meses_com_venda = sorted({l["Data"][:7] for l in vendas if l["Data"][:4] < "2100"})
    esperadas = set()
    for m in meses_com_venda:
        for v in vend:
            esperadas.add((m, v["SK_Vendedor"]))
    presentes = {(l["AnoMes"], l["SK_Vendedor"]) for l in metas}
    faltantes = esperadas - presentes
    r.achado("(7) pares mês/vendedor sem meta (atingimento vira infinito)",
             len(faltantes))
    if faltantes:
        r.info("    exemplos", sorted(faltantes)[:3])

    # (8) UF suja
    ufs = Counter(l["UF"] for l in cli)
    ufs_sujas = {k: v for k, v in ufs.items() if k != k.strip().upper()}
    r.achado("(8) valores de UF com caixa/espaço inconsistente", len(ufs_sujas))
    if ufs_sujas:
        r.info("    valores distintos de UF (com sujeira)", len(ufs))
        r.info("    valores distintos de UF (normalizados)",
               len({u.strip().upper() for u in ufs}))
        r.info("    exemplos sujos", {repr(k): v for k, v in list(ufs_sujas.items())[:4]})

    # ------------------------------------------------------------------
    # Gabarito de KPIs
    # ------------------------------------------------------------------
    r.secao("5 · GABARITO — os números que o seu modelo DAX deve reproduzir")

    def limpa_desconto(d: float) -> float:
        return d / 100 if d > 1 else d

    fat_bruto_cru = 0.0
    fat_liq_cru = 0.0
    custo_cru = 0.0
    fat_liq_limpo = 0.0
    custo_limpo = 0.0
    qtd_limpa = 0
    linhas_limpas = 0

    for l in vendas:
        q = int(l["Quantidade"])
        p = float(l["PrecoUnitario"])
        d = float(l["Desconto"])
        c = float(l["CustoUnitario"])
        data_ok = l["Data"] in datas_cal

        fat_bruto_cru += q * p
        fat_liq_cru += q * p * (1 - d)
        custo_cru += q * c

        if data_ok:
            q_ok = -abs(q) if l["Tipo"] == "Devolucao" else q
            d_ok = limpa_desconto(d)
            fat_liq_limpo += q_ok * p * (1 - d_ok)
            custo_limpo += q_ok * c
            qtd_limpa += q_ok
            linhas_limpas += 1

    print(f"  {CINZA}-- SEM tratar os defeitos (o que um modelo ingênuo mostra) --{FIM}")
    r.info("Faturamento bruto (cru)", brl(fat_bruto_cru))
    r.info("Faturamento líquido (cru)", brl(fat_liq_cru))
    r.info("Custo total (cru)", brl(custo_cru))
    r.info("Margem % (cru)",
           f"{(fat_liq_cru - custo_cru) / fat_liq_cru * 100:.2f}%")

    print()
    print(f"  {CINZA}-- DEPOIS de tratar os oito defeitos (o número correto) --{FIM}")
    r.info("Linhas consideradas", num(linhas_limpas))
    r.info("Faturamento líquido (tratado)", brl(fat_liq_limpo))
    r.info("Custo total (tratado)", brl(custo_limpo))
    r.info("Margem bruta (tratada)", brl(fat_liq_limpo - custo_limpo))
    r.info("Margem % (tratada)",
           f"{(fat_liq_limpo - custo_limpo) / fat_liq_limpo * 100:.2f}%")
    r.info("Quantidade líquida vendida", num(qtd_limpa))
    r.info("NFs distintas", num(len({l["NF"] for l in vendas})))
    r.info("Ticket médio por NF",
           brl(fat_liq_limpo / len({l["NF"] for l in vendas})))

    diferenca = fat_liq_cru - fat_liq_limpo
    print()
    r.info("DIFERENÇA causada pelos defeitos", brl(diferenca))
    r.info("  em % do faturamento tratado",
           f"{diferenca / fat_liq_limpo * 100:+.2f}%")

    # Por ano
    print()
    print(f"  {CINZA}-- Faturamento líquido tratado, por ano --{FIM}")
    por_ano: dict[str, float] = defaultdict(float)
    for l in vendas:
        if l["Data"] not in datas_cal:
            continue
        q = int(l["Quantidade"])
        if l["Tipo"] == "Devolucao":
            q = -abs(q)
        d = limpa_desconto(float(l["Desconto"]))
        por_ano[l["Data"][:4]] += q * float(l["PrecoUnitario"]) * (1 - d)
    anos = sorted(por_ano)
    for i, a in enumerate(anos):
        if i == 0:
            r.info(f"  {a}", brl(por_ano[a]))
        else:
            var = (por_ano[a] / por_ano[anos[i - 1]] - 1) * 100
            sufixo = "  (ano parcial)" if a == anos[-1] else ""
            r.info(f"  {a}", f"{brl(por_ano[a])}   {var:+.1f}% vs ano anterior{sufixo}")

    # Top 5 categorias
    print()
    print(f"  {CINZA}-- Top 5 categorias (faturamento líquido tratado) --{FIM}")
    cat_por_sk = {l["SK_Produto"]: l["Categoria"] for l in prod}
    por_cat: dict[str, float] = defaultdict(float)
    for l in vendas:
        if l["Data"] not in datas_cal:
            continue
        cat = cat_por_sk.get(l["SK_Produto"], "(produto órfão)")
        q = int(l["Quantidade"])
        if l["Tipo"] == "Devolucao":
            q = -abs(q)
        d = limpa_desconto(float(l["Desconto"]))
        por_cat[cat] += q * float(l["PrecoUnitario"]) * (1 - d)
    for cat, v in sorted(por_cat.items(), key=lambda x: -x[1])[:6]:
        pct = v / fat_liq_limpo * 100
        r.info(f"  {cat}", f"{brl(v)}   ({pct:.1f}%)")

    # ------------------------------------------------------------------
    # Consistência com o TMDL
    # ------------------------------------------------------------------
    r.secao("6 · CONSISTÊNCIA ENTRE OS CSVs E O MODELO EM TMDL")

    pasta_modelo = os.path.join(args.modelo, "definition", "tables")
    if not os.path.isdir(pasta_modelo):
        print(f"  {CINZA}(pasta {pasta_modelo} não encontrada — verificação pulada){FIM}")
    else:
        mapa_csv = {
            "dCalendario": cal, "dProduto": prod, "dCliente": cli,
            "dVendedor": vend, "fVendas": vendas, "fMetas": metas,
            "dSeguranca": seg,
        }
        for arquivo in sorted(os.listdir(pasta_modelo)):
            if not arquivo.endswith(".tmdl"):
                continue
            nome_tabela = arquivo[:-5]
            texto = open(os.path.join(pasta_modelo, arquivo), encoding="utf-8").read()

            if nome_tabela not in mapa_csv:
                print(f"  {CINZA}·     {nome_tabela}: tabela calculada (sem CSV) "
                      f"— verificação de colunas não se aplica{FIM}")
                continue

            # Colunas importadas: as que declaram "sourceColumn:".
            # Colunas calculadas (com "column Nome = ...") não têm sourceColumn
            # e, portanto, ficam de fora automaticamente — é assim que deve ser.
            fontes = set(re.findall(r"^\s*sourceColumn:\s*(\S.*?)\s*$",
                                    texto, re.MULTILINE))

            # Trecho M da partição: colunas criadas ali (ex.: UF_Normalizada)
            m_part = re.search(r"source\s*=\s*(.*)$", texto, re.DOTALL)
            codigo_m = m_part.group(1) if m_part else ""

            do_csv = (set(mapa_csv[nome_tabela][0].keys())
                      if nome_tabela in mapa_csv else set())

            faltando = sorted(
                c for c in fontes
                if c not in do_csv and f'"{c}"' not in codigo_m
            )
            criadas_no_m = sorted(
                c for c in fontes if c not in do_csv and f'"{c}"' in codigo_m
            )
            sobrando = sorted(do_csv - fontes)

            r.verifica(
                f"{nome_tabela}: toda sourceColumn existe no CSV ou é criada no M",
                len(faltando) == 0,
                f"não encontradas: {faltando}")
            if criadas_no_m:
                print(f"  {CINZA}·     {nome_tabela}: criadas no Power Query: "
                      f"{criadas_no_m}{FIM}")
            if sobrando:
                print(f"  {CINZA}·     {nome_tabela}: no CSV mas não usadas no modelo "
                      f"(ok se proposital): {sobrando}{FIM}")

        # relacionamentos
        rel_path = os.path.join(args.modelo, "definition", "relationships.tmdl")
        if os.path.exists(rel_path):
            texto = open(rel_path, encoding="utf-8").read()
            pares = re.findall(r"(fromColumn|toColumn):\s*([^\s]+)\.([^\s]+)", texto)
            problemas = []
            for _, tabela, coluna in pares:
                tabela = tabela.strip("'")
                coluna = coluna.strip("'")
                if tabela in mapa_csv and coluna not in mapa_csv[tabela][0]:
                    problemas.append(f"{tabela}[{coluna}]")
            r.verifica("relationships.tmdl referencia colunas existentes",
                       len(problemas) == 0, f"inexistentes: {problemas}")
            r.info("relacionamentos declarados", len(pares) // 2)

    # ------------------------------------------------------------------
    # Resumo
    # ------------------------------------------------------------------
    r.secao("RESUMO")
    print(f"  verificações estruturais ok ....... {r.ok}")
    print(f"  defeitos plantados encontrados .... {r.avisos}")
    print(f"  falhas ........................... {r.falhas}")
    print()
    if r.falhas == 0:
        print(f"  {VERDE}Base íntegra e defeitos localizados. "
              f"Siga para o README.md, seção 'Roteiro'.{FIM}")
        return 0
    print(f"  {VERMELHO}Há falhas estruturais. Rode gerar_dados.py de novo.{FIM}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
