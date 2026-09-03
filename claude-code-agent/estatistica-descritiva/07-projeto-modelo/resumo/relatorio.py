"""Montagem do relatório: números, desenhos em ASCII e a frase final.

O relatório é organizado na ordem em que um profissional lê os dados:
procedência → posição → dispersão → forma → incerteza → desenho → avisos.
A última seção, "frase sugerida", é a mais importante: ela entrega pronta
uma descrição que não mente, para ser copiada no e-mail ou no artigo.
"""

from __future__ import annotations

import math

from . import diagnostico as D
from . import incerteza as I
from . import medidas as M
from .formato import num, pct

__all__ = ["calcular", "texto", "dicionario", "histograma", "boxplot"]

LARGURA = 74


def calcular(valores, confianca=0.95, repeticoes=2000, semente=42):
    """Calcula todas as medidas. Devolve um dicionário simples e serializável."""
    n = len(valores)
    r = {
        "n": n,
        "min": min(valores),
        "max": max(valores),
        "soma": math.fsum(valores),
        "media": M.media(valores),
        "mediana": M.mediana(valores),
        "amplitude": M.amplitude(valores),
        "distintos": len(set(valores)),
        "confianca": confianca,
    }
    modas, freq = M.moda(valores)
    r["moda"] = modas if len(modas) <= 3 else modas[:3]
    r["moda_freq"] = freq
    r["moda_unica"] = len(modas) == 1

    if n >= 2:
        r["dp"] = M.desvio_padrao(valores)
        r["dp_pop"] = M.desvio_padrao(valores, ddof=0)
        r["variancia"] = M.variancia(valores)
        r["ep"] = M.erro_padrao(valores)
        r["cobertura_1dp"] = M.cobertura_1dp(valores)
        r["media_aparada"] = M.media_aparada(valores, 0.10)
        try:
            r["cv"] = M.coef_variacao(valores)
        except M.ErroDeMedida:
            r["cv"] = None
        q1, q2, q3 = M.quartis(valores)
        r["q1"], r["q3"] = q1, q3
        r["iqr"] = q3 - q1
        r["mad"] = M.mad(valores)
        r["p05"] = M.quantil(valores, 0.05)
        r["p95"] = M.quantil(valores, 0.95)
        r["p99"] = M.quantil(valores, 0.99)
        r["ic_media"] = I.ic_media_t(valores, confianca)
        r["t_critico"] = I.t_critico(confianca, gl=n - 1)
        lo, hi, ep_md = I.ic_bootstrap(valores, M.mediana, confianca,
                                       repeticoes, semente)
        r["ic_mediana"] = (lo, hi)
        r["ep_mediana"] = ep_md
        r["bootstrap_repeticoes"] = repeticoes
        r["semente"] = semente
    if n >= 3:
        try:
            r["assimetria"] = M.assimetria(valores)
        except M.ErroDeMedida:
            r["assimetria"] = None
    if n >= 4:
        try:
            r["curtose"] = M.curtose_excesso(valores)
        except M.ErroDeMedida:
            r["curtose"] = None

    todos_pos = all(v > 0 for v in valores)
    r["todos_positivos"] = todos_pos
    if todos_pos:
        r["media_geometrica"] = M.media_geometrica(valores)
        r["media_harmonica"] = M.media_harmonica(valores)
    return r


# ------------------------------------------------------------------ desenhos

def histograma(valores, classes=None, largura=46):
    """Histograma em ASCII.

    O número de classes usa a regra de Freedman-Diaconis (largura = 2·IQR/n^(1/3)),
    que se adapta à dispersão real; se o IQR for zero, cai para a regra de
    Sturges. A escolha do número de classes MUDA a aparência do histograma —
    é a decisão mais subjetiva de toda a estatística descritiva.
    """
    n = len(valores)
    lo, hi = min(valores), max(valores)
    if hi == lo:
        return [f"  todos os valores iguais a {num(lo)}"]
    if classes is None:
        faixa = M.iqr(valores)
        if faixa > 0:
            h = 2 * faixa / (n ** (1 / 3))
            classes = max(4, min(24, int(math.ceil((hi - lo) / h))))
        else:
            classes = max(4, min(24, int(math.ceil(math.log2(n) + 1))))
    passo = (hi - lo) / classes
    cont = [0] * classes
    for v in valores:
        k = min(classes - 1, int((v - lo) / passo))
        cont[k] += 1
    pico = max(cont) or 1
    linhas = []
    for k, c in enumerate(cont):
        a, b = lo + k * passo, lo + (k + 1) * passo
        barra = "█" * int(round(largura * c / pico))
        linhas.append(f"  {num(a):>12} ┤{barra:<{largura}} {c}")
    linhas.append(f"  {num(hi):>12} ┘   ({classes} classes, "
                  f"largura {num(passo)}; regra de Freedman-Diaconis)")
    return linhas


def boxplot(valores, largura=60):
    """Diagrama de caixa em ASCII, com as cercas de 1,5×IQR."""
    lo, hi = min(valores), max(valores)
    q1, q2, q3 = M.quartis(valores)
    faixa = q3 - q1
    cerca_lo, cerca_hi = q1 - 1.5 * faixa, q3 + 1.5 * faixa
    dentro = [v for v in valores if cerca_lo <= v <= cerca_hi]
    bigode_lo = min(dentro) if dentro else lo
    bigode_hi = max(dentro) if dentro else hi
    fora = [v for v in valores if v < cerca_lo or v > cerca_hi]

    if hi == lo:
        return ["  todos os valores iguais"]

    def pos(v):
        return max(0, min(largura - 1, int(round((v - lo) / (hi - lo) * (largura - 1)))))

    linha = [" "] * largura
    for i in range(pos(bigode_lo), pos(q1)):
        linha[i] = "-"
    for i in range(pos(q3) + 1, pos(bigode_hi) + 1):
        linha[i] = "-"
    for i in range(pos(q1), pos(q3) + 1):
        linha[i] = "="
    linha[pos(bigode_lo)] = "|"
    linha[pos(bigode_hi)] = "|"
    linha[pos(q1)] = "["
    linha[pos(q3)] = "]"
    linha[pos(q2)] = "#"
    for v in fora:
        linha[pos(v)] = "o"
    eixo = f"  {''.join(linha)}"
    legenda = (f"  {num(lo):<{max(1, largura//2)}}{num(hi):>{max(1, largura - largura//2)}}")
    return [
        eixo,
        legenda,
        f"  | bigode  [ Q1  # mediana  ] Q3  - dados  o fora da cerca 1,5×IQR",
        f"  Q1 = {num(q1)}   mediana = {num(q2)}   Q3 = {num(q3)}   IQR = {num(faixa)}",
    ]


# ------------------------------------------------------------------ saídas

def _linha(titulo=""):
    if not titulo:
        return "─" * LARGURA
    return f"── {titulo} " + "─" * max(0, LARGURA - len(titulo) - 4)


def texto(valores, coluna=None, avisos=None, **kw):
    """Relatório completo em texto."""
    r = calcular(valores, **kw)
    avisos = D.diagnosticar(valores) if avisos is None else avisos
    n = r["n"]
    L = []
    ap = L.append

    ap(_linha())
    ap(f"RESUMO ESTATÍSTICO — coluna: {coluna or '(sem nome)'}")
    ap(_linha())
    ap("")

    ap(_linha("POSIÇÃO — onde os dados se concentram"))
    ap(f"  n .................... {num(n)} observações ({num(r['distintos'])} valores distintos)")
    ap(f"  média ................ {num(r['media'])}")
    ap(f"  mediana .............. {num(r['mediana'])}")
    if r.get("media_aparada") is not None:
        ap(f"  média aparada (10%) .. {num(r['media_aparada'])}")
    if r["moda_unica"]:
        ap(f"  moda ................. {num(r['moda'][0])} (aparece {num(r['moda_freq'])}×)")
    else:
        ap(f"  moda ................. {', '.join(num(m) for m in r['moda'])}"
           f" (empate, {num(r['moda_freq'])}× cada)")
    if r["todos_positivos"]:
        ap(f"  média geométrica ..... {num(r['media_geometrica'])}")
        ap(f"  média harmônica ...... {num(r['media_harmonica'])}")
    ap(f"  soma ................. {num(r['soma'])}")
    ap("")

    if n >= 2:
        ap(_linha("DISPERSÃO — o quanto os dados discordam entre si"))
        ap(f"  desvio padrão (n−1) .. {num(r['dp'])}")
        ap(f"  desvio padrão (n) .... {num(r['dp_pop'])}   [populacional]")
        ap(f"  variância ............ {num(r['variancia'])}   [unidade ao quadrado]")
        ap(f"  amplitude ............ {num(r['amplitude'])}  ({num(r['min'])} a {num(r['max'])})")
        ap(f"  IQR (Q3−Q1) .......... {num(r['iqr'])}   [robusto]")
        ap(f"  MAD escalado ......... {num(r['mad'])}   [robusto, comparável ao DP]")
        if r["cv"] is not None:
            ap(f"  coef. de variação .... {pct(r['cv'])}")
        ap(f"  dentro de 1 DP ....... {pct(r['cobertura_1dp'], 0)}   [normal: ~68%]")
        ap("")

        ap(_linha("QUANTIS"))
        ap(f"  mín  p05   Q1    mediana   Q3    p95   p99   máx")
        ap(f"  {num(r['min'])}  {num(r['p05'])}  {num(r['q1'])}  "
           f"{num(r['mediana'])}  {num(r['q3'])}  {num(r['p95'])}  "
           f"{num(r['p99'])}  {num(r['max'])}")
        ap("")

    if r.get("assimetria") is not None:
        ap(_linha("FORMA"))
        a = r["assimetria"]
        lado = "simétrica" if abs(a) < 0.5 else ("cauda à direita" if a > 0 else "cauda à esquerda")
        ap(f"  assimetria (G1) ...... {num(a)}   [{lado}]")
        if r.get("curtose") is not None:
            k = r["curtose"]
            cauda = ("caudas leves" if k < -0.5 else
                     "caudas parecidas com a normal" if k <= 1 else "caudas pesadas")
            ap(f"  curtose em excesso ... {num(k)}   [{cauda}]")
        ap("")

    if n >= 2:
        ap(_linha(f"INCERTEZA — o quanto estas estimativas balançam ({pct(r['confianca'],0)})"))
        lo, hi = r["ic_media"]
        ap(f"  erro padrão da média . {num(r['ep'])}   [= DP/√n]")
        ap(f"  IC da média (t) ...... [{num(lo)} ; {num(hi)}]   "
           f"t({n-1}) = {num(r['t_critico'])}")
        lo2, hi2 = r["ic_mediana"]
        ap(f"  IC da mediana (boot) . [{num(lo2)} ; {num(hi2)}]   "
           f"EP ≈ {num(r['ep_mediana'])}")
        ap(f"  bootstrap ............ {num(r['bootstrap_repeticoes'])} reamostragens, "
           f"semente {r['semente']}")
        ap("")

    ap(_linha("DISTRIBUIÇÃO"))
    L.extend(histograma(valores))
    ap("")
    L.extend(boxplot(valores))
    ap("")

    ap(_linha("DIAGNÓSTICO"))
    if not avisos:
        ap("  Nenhum aviso. As medidas usuais descrevem bem estes dados.")
    else:
        for a in avisos:
            ap(f"  {a}".replace("\n", "\n  "))
            ap("")
    ap("")

    ap(_linha("FRASE SUGERIDA PARA O RELATÓRIO"))
    for linha in frase_final(r, avisos):
        ap(f"  {linha}")
    ap("")
    ap(_linha())
    return "\n".join(L)


def frase_final(r, avisos):
    """Gera a descrição honesta, escolhendo as medidas conforme o diagnóstico."""
    graves = [a.titulo for a in avisos if a.gravidade == D.GRAVE]
    assimetrico = any("assim" in t for t in graves) or any("desvio padrão maior" in t for t in graves)
    n = r["n"]
    if n < 2:
        return [f"n = 1; valor observado: {num(r['media'])}. "
                "Não há dispersão nem incerteza a estimar."]
    if assimetrico:
        lo, hi = r["ic_mediana"]
        return [
            f"Mediana de {num(r['mediana'])} "
            f"(IC{pct(r['confianca'],0)} por bootstrap: {num(lo)} a {num(hi)}); "
            f"IQR de {num(r['q1'])} a {num(r['q3'])}; n = {num(n)}.",
            f"p95 = {num(r['p95'])} e máximo = {num(r['max'])}.",
            "A distribuição é assimétrica; a média "
            f"({num(r['media'])}) não representa o caso típico e não deve ser "
            "usada como meta ou expectativa.",
        ]
    lo, hi = r["ic_media"]
    return [
        f"Média de {num(r['media'])} "
        f"(DP {num(r['dp'])}; IC{pct(r['confianca'],0)} da média: "
        f"{num(lo)} a {num(hi)}); n = {num(n)}.",
        f"Mediana {num(r['mediana'])}, faixa observada de {num(r['min'])} "
        f"a {num(r['max'])}.",
    ]


def dicionario(valores, coluna=None, **kw):
    """Mesmo conteúdo, em estrutura serializável para JSON."""
    r = calcular(valores, **kw)
    avisos = D.diagnosticar(valores)
    r["coluna"] = coluna
    r["avisos"] = [
        {"gravidade": a.gravidade, "titulo": a.titulo,
         "detalhe": a.detalhe, "acao": a.acao} for a in avisos
    ]
    r["frase_sugerida"] = frase_final(r, avisos)
    return r
