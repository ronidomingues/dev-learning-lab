#!/usr/bin/env python3
"""
carteira.py — compara, em reais liquidos, onde colocar o seu dinheiro.

Uso:
    python3 carteira.py                              # padrao: R$ 6.000
    python3 carteira.py --valor 20000 --prazos 90,365,1825
    python3 carteira.py plano --valor 6000 --despesa-mensal 2500
    python3 carteira.py --config meu_cenario.json    # cenario proprio
    python3 carteira.py --formato csv > saida.csv

Sem dependencias externas: so a biblioteca padrao do Python 3.10+.
"""

import argparse
import json
import sys

import indicadores as ind
import produtos as prod
import tributos as trib


# --- configuracao ----------------------------------------------------------

CAMPOS_CONFIGURAVEIS = {
    "SELIC_META", "SELIC_OVER", "CDI", "IPCA_12M", "IPCA_ESPERADO",
    "TR_MENSAL", "TAXA_CUSTODIA_B3",
}


def aplicar_config(caminho: str) -> list:
    """Sobrescreve indicadores a partir de um JSON. Devolve o que mudou."""
    try:
        with open(caminho, encoding="utf-8") as fh:
            dados = json.load(fh)
    except FileNotFoundError:
        raise SystemExit(f"erro: arquivo de configuracao nao encontrado: {caminho}")
    except json.JSONDecodeError as e:
        raise SystemExit(f"erro: JSON invalido em {caminho}: {e}")

    if not isinstance(dados, dict):
        raise SystemExit("erro: a configuracao deve ser um objeto JSON")

    mudancas = []
    for chave, valor in dados.items():
        if chave not in CAMPOS_CONFIGURAVEIS:
            raise SystemExit(
                f"erro: campo '{chave}' nao e configuravel. "
                f"Validos: {', '.join(sorted(CAMPOS_CONFIGURAVEIS))}"
            )
        if not isinstance(valor, (int, float)):
            raise SystemExit(f"erro: '{chave}' deve ser numero, veio {type(valor).__name__}")
        if not -1 < valor < 5:
            raise SystemExit(f"erro: '{chave}'={valor} fora de faixa plausivel (use 0.14 para 14%)")
        mudancas.append(f"{chave}: {getattr(ind, chave):.4f} -> {valor:.4f}")
        setattr(ind, chave, float(valor))
    return mudancas


# --- formatacao ------------------------------------------------------------

def brl(v: float) -> str:
    s = f"{v:,.2f}"
    return "R$ " + s.replace(",", "X").replace(".", ",").replace("X", ".")


def pct(v: float) -> str:
    return f"{v * 100:.2f}%".replace(".", ",")


def rotulo_prazo(dias: int) -> str:
    if dias < 60:
        return f"{dias} dias"
    if dias < 730:
        return f"{dias} dias (~{dias / 30:.0f} meses)"
    return f"{dias} dias (~{dias / 365:.1f} anos)"


def tabela(resultados: list, dias: int) -> str:
    linhas = []
    larg = max(len(r.produto) for r in resultados)
    cab = (f"{'produto':<{larg}}  {'liquido':>12}  {'% a.a.':>8}  "
           f"{'real a.a.':>10}  {'IR+IOF':>10}  {'taxas':>8}  observacao")
    linhas.append(cab)
    linhas.append("-" * len(cab))
    for r in sorted(resultados, key=lambda x: -x.liquido):
        linhas.append(
            f"{r.produto:<{larg}}  {brl(r.liquido):>12}  {pct(r.taxa_liquida_aa):>8}  "
            f"{pct(r.taxa_real_aa):>10}  {brl(r.ir + r.iof):>10}  {brl(r.taxas):>8}  "
            f"{r.observacao}"
        )
    return "\n".join(linhas)


def csv(resultados_por_prazo: dict) -> str:
    linhas = ["dias;produto;principal;bruto;iof;ir;taxas;liquido;taxa_liquida_aa;taxa_real_aa"]
    for dias, resultados in resultados_por_prazo.items():
        for r in resultados:
            linhas.append(
                f"{dias};{r.produto};{r.principal:.2f};{r.bruto:.2f};{r.iof:.2f};"
                f"{r.ir:.2f};{r.taxas:.2f};{r.liquido:.2f};"
                f"{r.taxa_liquida_aa:.6f};{r.taxa_real_aa:.6f}"
            )
    return "\n".join(linhas)


# --- comandos --------------------------------------------------------------

def cmd_comparar(args) -> int:
    resultados_por_prazo = {}
    for dias in args.prazos:
        resultados_por_prazo[dias] = [p.simular(args.valor, dias) for p in prod.catalogo()]

    if args.formato == "csv":
        print(csv(resultados_por_prazo))
        return 0

    print(cabecalho(args.valor))
    for dias, resultados in resultados_por_prazo.items():
        print(f"\n### Prazo: {rotulo_prazo(dias)}\n")
        print(tabela(resultados, dias))
        liquidos = [r for r in resultados if not r.observacao.startswith("RESGATE")]
        melhor = max(liquidos, key=lambda r: r.liquido)
        pior = min(resultados, key=lambda r: r.liquido)
        print(f"\n  Melhor com resgate disponivel: {melhor.produto} "
              f"({brl(melhor.liquido)} liquidos, {pct(melhor.taxa_liquida_aa)} a.a.)")
        print(f"  Diferenca para o pior da lista ({pior.produto}): "
              f"{brl(melhor.liquido - pior.liquido)}")
    print(rodape())
    return 0


def cmd_plano(args) -> int:
    if args.despesa_mensal <= 0:
        raise SystemExit("erro: --despesa-mensal deve ser positiva")
    alvo_reserva = args.despesa_mensal * args.meses_reserva
    reserva = min(args.valor, alvo_reserva)
    excedente = max(0.0, args.valor - alvo_reserva)

    print(cabecalho(args.valor))
    print(f"\n### Plano para {brl(args.valor)}\n")
    print(f"Despesa mensal informada ..... {brl(args.despesa_mensal)}")
    print(f"Reserva alvo ({args.meses_reserva} meses) ..... {brl(alvo_reserva)}")
    print()
    print(f"1) Reserva de emergencia ..... {brl(reserva)}")
    print("   Veiculo: Tesouro Reserva / Tesouro Selic / CDB 100% CDI com liquidez diaria.")
    print("   Criterio: liquidez em D+0 e risco de credito minimo. Rendimento e o terceiro criterio.")
    if excedente <= 0:
        falta = alvo_reserva - args.valor
        print(f"\n   Ainda faltam {brl(falta)} para completar a reserva.")
        print("   Enquanto faltar, NAO ha decisao de alocacao a tomar: tudo vai para a reserva.")
    else:
        print(f"\n2) Excedente ..... {brl(excedente)}")
        print("   So aqui comeca a conversa sobre prazo, risco e imposto:")
        print("   - objetivo em ate 2 anos  -> pos-fixado (CDB/LCI) ou Tesouro Selic")
        print("   - objetivo de 2 a 5 anos  -> LCI/LCA isenta + Tesouro IPCA+ curto")
        print("   - objetivo acima de 5 anos-> Tesouro IPCA+ longo, e so entao renda variavel")
    print(rodape())
    return 0


def cmd_impostos(args) -> int:
    print(cabecalho(args.valor))
    print("\n### Tabela regressiva do IR (Lei 11.033/2004)\n")
    for linha in trib.resumo_tabela_ir():
        print("  " + linha)
    print("\n### Equivalencia isento x tributado\n")
    print("  Um produto ISENTO a X% do CDI equivale a quantos % do CDI tributado?\n")
    print(f"  {'% do CDI isento':>16} | " + " | ".join(f"{d:>6}d" for d in (180, 360, 720, 1080)))
    for p in (0.80, 0.85, 0.88, 0.90, 0.95):
        celulas = " | ".join(
            f"{trib.percentual_cdi_equivalente(p, d) * 100:>6.1f}%" for d in (180, 360, 720, 1080)
        )
        print(f"  {p * 100:>15.0f}% | {celulas}")
    print("\n  Leitura: uma LCI a 90% do CDI resgatada no dia 360 rende o mesmo que")
    print("  um CDB a 112,5% do CDI. Esperando ate o dia 361, bastam 109,1%.")
    print("  Compare sempre o LIQUIDO no SEU prazo, nunca o percentual anunciado.")
    print(rodape())
    return 0


def cabecalho(valor: float) -> str:
    return (f"Simulador de renda fixa — cenario de {ind.DATA_REFERENCIA}\n"
            f"Selic {pct(ind.SELIC_META)} a.a. | CDI {pct(ind.CDI)} a.a. | "
            f"IPCA 12m {pct(ind.IPCA_12M)} | valor simulado {brl(valor)}")


def rodape() -> str:
    linhas = ["\n--- fontes dos indicadores ---"]
    for f in ind.FONTES:
        linhas.append(f"  {f.indicador:<28} {f.valor:<44} {f.origem} ({f.data})")
    linhas.append("\nMaterial educacional. Nao e recomendacao de investimento.")
    return "\n".join(linhas)


# --- entrada ---------------------------------------------------------------

def lista_de_prazos(texto: str) -> list:
    try:
        prazos = [int(x) for x in texto.split(",") if x.strip()]
    except ValueError:
        raise argparse.ArgumentTypeError("prazos devem ser inteiros separados por virgula")
    if not prazos:
        raise argparse.ArgumentTypeError("informe ao menos um prazo")
    if any(d <= 0 or d > 36500 for d in prazos):
        raise argparse.ArgumentTypeError("cada prazo deve estar entre 1 e 36500 dias")
    return prazos


def construir_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Compara produtos de renda fixa pelo que sobra no bolso.",
        epilog="Material educacional. Nao e recomendacao de investimento.",
    )
    p.add_argument("--valor", type=float, default=6000.0, help="valor a investir (padrao: 6000)")
    p.add_argument("--prazos", type=lista_de_prazos, default=[30, 180, 365, 730, 1825],
                   help="prazos em dias, separados por virgula")
    p.add_argument("--formato", choices=("tabela", "csv"), default="tabela")
    p.add_argument("--config", help="arquivo JSON com indicadores proprios")

    sub = p.add_subparsers(dest="comando")
    pl = sub.add_parser("plano", help="divide o valor entre reserva e excedente")
    pl.add_argument("--valor", type=float, default=6000.0)
    pl.add_argument("--despesa-mensal", type=float, required=True)
    pl.add_argument("--meses-reserva", type=int, default=6)
    pl.add_argument("--config")
    pl.add_argument("--formato", choices=("tabela",), default="tabela")
    pl.set_defaults(func=cmd_plano)

    im = sub.add_parser("impostos", help="tabelas de IR e equivalencia isento/tributado")
    im.add_argument("--valor", type=float, default=6000.0)
    im.add_argument("--config")
    im.add_argument("--formato", choices=("tabela",), default="tabela")
    im.set_defaults(func=cmd_impostos)

    p.set_defaults(func=cmd_comparar)
    return p


def main(argv=None) -> int:
    args = construir_parser().parse_args(argv)
    if args.valor <= 0:
        raise SystemExit("erro: --valor deve ser positivo")
    if args.valor > 1e9:
        raise SystemExit("erro: --valor implausivel; este simulador e para varejo")
    if getattr(args, "config", None):
        for m in aplicar_config(args.config):
            print(f"# config: {m}", file=sys.stderr)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
