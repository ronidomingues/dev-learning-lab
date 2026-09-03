"""Leitura de CSV com contabilidade honesta do que foi descartado.

Regra de ouro deste módulo: **nada é jogado fora em silêncio**. Toda linha
não convertida é contada e classificada, e esse relato vai para a saída.
Uma análise vira mentira exatamente aqui — no ponto em que 12% das linhas
somem sem ninguém notar.

O problema difícil aqui não é ler CSV: é que "1.500" é ambíguo. Em pt-BR
significa mil e quinhentos; em en-US, um e meio. Nenhuma regra por valor
resolve isso, e nenhuma regra por coluna resolve *sempre*.

A política adotada, em três degraus:

1. se algum valor da coluna contém vírgula, há evidência real de convenção
   pt-BR ou en-US e a decisão é tomada contando as evidências;
2. se nenhum valor contém vírgula, o decimal é o **ponto** — o padrão de
   intercâmbio — porque supor milhar sem nenhuma corroboração já quebrou
   este próprio projeto durante o desenvolvimento (as alturas viraram
   milímetros);
3. quando o caso 2 acontece **e** a coluna tem muitos valores com exatamente
   três dígitos depois do ponto, a ambiguidade é sinalizada no relatório,
   com a saída manual `--decimal`.

A lição de ofício: quando a informação não está no dado, o certo não é
adivinhar melhor — é escolher o padrão menos destrutivo e **avisar**.
"""

from __future__ import annotations

import csv
import re
from dataclasses import dataclass, field

__all__ = ["Coluna", "ErroDeLeitura", "ler_csv", "detectar_separador",
           "detectar_decimal"]

# textos que, na prática, significam "sem valor"
AUSENTES = {
    "", "na", "n/a", "n.a.", "nan", "null", "none", "nd", "n.d.",
    "-", "--", "?", "sem dados", "sem informacao", "sem informação",
}

# sentinelas numéricas usadas por sistemas antigos para dizer "faltando"
SENTINELAS_SUSPEITAS = {-999.0, -9999.0, -99.0, 999.0, 9999.0}

_LIXO = re.compile(r"[R$US\s %]")


class ErroDeLeitura(Exception):
    """Falha ao ler ou interpretar o arquivo."""


@dataclass
class Coluna:
    """Uma coluna numérica lida, com o histórico do que aconteceu."""

    nome: str
    valores: list = field(default_factory=list)
    ausentes: int = 0
    invalidos: list = field(default_factory=list)
    total_linhas: int = 0
    decimal: str = "."
    sentinelas: int = 0
    decimal_ambiguo: bool = False

    @property
    def aproveitamento(self):
        if self.total_linhas == 0:
            return 0.0
        return len(self.valores) / self.total_linhas


def detectar_separador(caminho, encoding="utf-8"):
    """Descobre se o CSV usa ',' ou ';' — CSVs brasileiros usam ';'."""
    try:
        with open(caminho, newline="", encoding=encoding) as f:
            amostra = f.read(8192)
    except FileNotFoundError as e:
        raise ErroDeLeitura(f"arquivo não encontrado: {caminho}") from e
    except UnicodeDecodeError as e:
        raise ErroDeLeitura(
            f"não foi possível decodificar {caminho} como {encoding}. "
            f"Tente --encoding latin-1 (comum em exportações do Excel no Windows)."
        ) from e
    if not amostra.strip():
        raise ErroDeLeitura(f"arquivo vazio: {caminho}")
    primeira = amostra.splitlines()[0]
    return ";" if primeira.count(";") > primeira.count(",") else ","


def _limpar(bruto):
    return _LIXO.sub("", bruto.strip())


def detectar_decimal(brutos):
    """Decide se a coluna usa vírgula ou ponto como separador decimal.

    Devolve (decimal, ambiguo). Ver a política no topo do módulo.
    """
    limpos = [_limpar(b) for b in brutos]
    limpos = [t for t in limpos if t and t.lower() not in AUSENTES]
    if not limpos:
        return ".", False

    if not any("," in t for t in limpos):
        # sem nenhuma vírgula não há evidência de convenção pt-BR
        com_ponto = [t for t in limpos if "." in t]
        tres = sum(1 for t in com_ponto if re.search(r"\.\d{3}$", t))
        ambiguo = bool(com_ponto) and tres / len(com_ponto) >= 0.8 and len(com_ponto) >= 3
        return ".", ambiguo

    br = us = 0
    for t in limpos:
        if "," in t and "." in t:
            if t.rfind(",") > t.rfind("."):
                br += 1                   # 1.234,56
            else:
                us += 1                   # 1,234.56
            continue
        if re.search(r",\d{1,2}$", t):
            br += 1                       # 12,50
        elif re.search(r",\d{3}(?:\D|$)", t):
            us += 1                       # 1,500 -> milhar em en-US
        elif "," in t:
            br += 1                       # vírgula em outra posição: pt-BR
    return ("," if br > us else "."), False


def _para_float(bruto, decimal="."):
    """Converte texto em float segundo a convenção decimal da coluna.

    Devolve None se o texto significar ausência;
    levanta ValueError se for lixo de verdade.
    """
    t = bruto.strip()
    if t.lower() in AUSENTES:
        return None
    t = _limpar(t)
    if not t or t.lower() in AUSENTES:
        return None
    if decimal == ",":
        t = t.replace(".", "").replace(",", ".")
    else:
        t = t.replace(",", "")
    return float(t)


def ler_csv(caminho, coluna=None, encoding="utf-8", separador=None,
            decimal=None):
    """Lê uma coluna numérica de um CSV.

    Se `coluna` for None, usa a primeira coluna com ao menos 80% de valores
    numéricos. Se `decimal` for None, infere pela coluna inteira.
    """
    sep = separador or detectar_separador(caminho, encoding)
    try:
        with open(caminho, newline="", encoding=encoding) as f:
            leitor = csv.DictReader(f, delimiter=sep)
            if leitor.fieldnames is None:
                raise ErroDeLeitura("CSV sem cabeçalho")
            cabecalhos = [c.strip() for c in leitor.fieldnames]
            linhas = list(leitor)
    except UnicodeDecodeError as e:
        raise ErroDeLeitura(
            f"não foi possível decodificar {caminho} como {encoding}. "
            f"Tente --encoding latin-1."
        ) from e

    if not linhas:
        raise ErroDeLeitura("CSV sem linhas de dados")

    if coluna is None:
        coluna = _escolher_coluna(linhas, cabecalhos)
    elif coluna not in cabecalhos:
        raise ErroDeLeitura(
            f"coluna '{coluna}' não existe. Colunas disponíveis: "
            + ", ".join(cabecalhos)
        )

    brutos = [(linha.get(coluna) or "") for linha in linhas]
    detectado, ambiguo = detectar_decimal(brutos)
    dec = decimal or detectado

    col = Coluna(nome=coluna, total_linhas=len(linhas), decimal=dec,
                 decimal_ambiguo=ambiguo and decimal is None)
    for i, bruto in enumerate(brutos, start=2):     # linha 1 é o cabeçalho
        try:
            v = _para_float(bruto, dec)
        except ValueError:
            col.invalidos.append((i, bruto.strip()))
            continue
        if v is None:
            col.ausentes += 1
        else:
            col.valores.append(v)

    col.sentinelas = sum(1 for v in col.valores if v in SENTINELAS_SUSPEITAS)

    if not col.valores:
        raise ErroDeLeitura(
            f"nenhum valor numérico válido na coluna '{coluna}' "
            f"({col.ausentes} ausentes, {len(col.invalidos)} inválidos)"
        )
    return col


def _escolher_coluna(linhas, cabecalhos):
    melhor, melhor_taxa = None, 0.0
    for c in cabecalhos:
        brutos = [(linha.get(c) or "") for linha in linhas]
        dec, _ = detectar_decimal(brutos)
        ok = 0
        for bruto in brutos:
            try:
                if _para_float(bruto, dec) is not None:
                    ok += 1
            except ValueError:
                pass
        taxa = ok / len(linhas)
        if taxa > melhor_taxa:
            melhor, melhor_taxa = c, taxa
    if melhor is None or melhor_taxa < 0.8:
        raise ErroDeLeitura(
            "nenhuma coluna com pelo menos 80% de valores numéricos; "
            "informe a coluna com --coluna NOME"
        )
    return melhor
