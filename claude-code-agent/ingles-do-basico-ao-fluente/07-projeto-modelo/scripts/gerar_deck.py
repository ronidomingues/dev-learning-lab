#!/usr/bin/env python3
"""Gera baralhos importáveis no Anki a partir de um arquivo de frases em TSV.

Só biblioteca padrão. Nada para instalar.

Uso:
    python3 scripts/gerar_deck.py                      # gera tudo
    python3 scripts/gerar_deck.py --max-cefr B1        # só até B1
    python3 scripts/gerar_deck.py --tag reuniao email  # só esses assuntos
    python3 scripts/gerar_deck.py --dry-run            # valida e não escreve nada

Saída (dentro de `saida/`):
    anki-reconhecimento.tsv  -> Front / Back / Tags        (tipo "Básico")
    anki-producao.tsv        -> Text  / Extra / Tags       (tipo "Cloze")
    relatorio.txt            -> o que foi gerado e o que foi recusado

Código de saída: 0 se tudo válido; 1 se houver erro de validação.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

NIVEIS = ["A1", "A2", "B1", "B2", "C1", "C2"]
COLUNAS = ["id", "cefr", "tag", "en", "pt", "ipa", "cloze"]

RAIZ = Path(__file__).resolve().parent.parent


class ErroDeDados(Exception):
    """Erro no arquivo de frases. Sempre traz o número da linha."""


def carregar_config(caminho: Path) -> dict:
    """Lê config.json. Falha com mensagem útil em vez de traceback cru."""
    try:
        with caminho.open(encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        raise ErroDeDados(f"config não encontrado: {caminho}")
    except json.JSONDecodeError as e:
        raise ErroDeDados(f"config.json inválido ({e.msg}, linha {e.lineno})")


def ler_frases(caminho: Path) -> list[dict]:
    """Lê o TSV e devolve uma lista de dicionários, já validada.

    Validamos aqui, e não na geração, porque um deck com erro só aparece
    semanas depois — quando você já decorou a frase errada.
    """
    if not caminho.exists():
        raise ErroDeDados(f"arquivo de frases não encontrado: {caminho}")

    linhas = caminho.read_text(encoding="utf-8").splitlines()
    if not linhas:
        raise ErroDeDados(f"arquivo de frases vazio: {caminho}")

    cabecalho = linhas[0].split("\t")
    if cabecalho != COLUNAS:
        raise ErroDeDados(
            f"cabeçalho inesperado.\n  esperado: {COLUNAS}\n  encontrado: {cabecalho}"
        )

    frases: list[dict] = []
    vistos: dict[str, int] = {}
    erros: list[str] = []

    for n, linha in enumerate(linhas[1:], start=2):
        if not linha.strip():
            continue
        campos = linha.split("\t")
        if len(campos) != len(COLUNAS):
            erros.append(f"linha {n}: {len(campos)} colunas, esperava {len(COLUNAS)}")
            continue

        item = dict(zip(COLUNAS, (c.strip() for c in campos)))

        if item["id"] in vistos:
            erros.append(f"linha {n}: id '{item['id']}' repetido (já na linha {vistos[item['id']]})")
        vistos[item["id"]] = n

        if item["cefr"] not in NIVEIS:
            erros.append(f"linha {n}: nível '{item['cefr']}' inválido (use {'/'.join(NIVEIS)})")

        for obrigatorio in ("en", "pt", "cloze"):
            if not item[obrigatorio]:
                erros.append(f"linha {n}: campo '{obrigatorio}' vazio")

        # A regra que mais pega erro na prática: o trecho a ocultar precisa
        # existir literalmente na frase, ou o cartão Cloze sai quebrado.
        if item["cloze"] and item["cloze"] not in item["en"]:
            erros.append(
                f"linha {n}: cloze '{item['cloze']}' não aparece em \"{item['en']}\""
            )

        frases.append(item)

    if erros:
        raise ErroDeDados("erros no arquivo de frases:\n  - " + "\n  - ".join(erros))

    return frases


def filtrar(frases: list[dict], max_cefr: str | None, tags: list[str] | None) -> list[dict]:
    saida = frases
    if max_cefr:
        limite = NIVEIS.index(max_cefr)
        saida = [f for f in saida if NIVEIS.index(f["cefr"]) <= limite]
    if tags:
        alvo = {t.lower() for t in tags}
        saida = [f for f in saida if f["tag"].lower() in alvo]
    return saida


def campo_seguro(texto: str) -> str:
    """O Anki importa TSV: tab e quebra de linha dentro do campo quebram a importação."""
    return texto.replace("\t", " ").replace("\n", "<br>")


def cartao_reconhecimento(f: dict) -> str:
    """Frente = inglês. Verso = português + IPA. Treina compreensão."""
    frente = campo_seguro(f["en"])
    verso = campo_seguro(f["pt"])
    if f["ipa"]:
        verso += f"<br><i>{campo_seguro(f['ipa'])}</i>"
    tags = f"ponte {f['cefr'].lower()} {f['tag']}"
    return f"{frente}\t{verso}\t{tags}"


def cartao_producao(f: dict) -> str:
    """Cloze: apaga o trecho-chave dentro da frase. Treina produção."""
    texto = campo_seguro(f["en"]).replace(f["cloze"], "{{c1::" + f["cloze"] + "}}", 1)
    extra = campo_seguro(f["pt"])
    tags = f"ponte {f['cefr'].lower()} {f['tag']} producao"
    return f"{texto}\t{extra}\t{tags}"


def gerar(frases: list[dict], destino: Path, escrever: bool) -> dict:
    reconhecimento = [cartao_reconhecimento(f) for f in frases]
    producao = [cartao_producao(f) for f in frases]

    if escrever:
        destino.mkdir(parents=True, exist_ok=True)
        (destino / "anki-reconhecimento.tsv").write_text(
            "\n".join(reconhecimento) + "\n", encoding="utf-8"
        )
        (destino / "anki-producao.tsv").write_text(
            "\n".join(producao) + "\n", encoding="utf-8"
        )

    return {"reconhecimento": len(reconhecimento), "producao": len(producao)}


def montar_relatorio(frases: list[dict], contagem: dict, escrito: bool) -> str:
    por_nivel: dict[str, int] = {}
    por_tag: dict[str, int] = {}
    for f in frases:
        por_nivel[f["cefr"]] = por_nivel.get(f["cefr"], 0) + 1
        por_tag[f["tag"]] = por_tag.get(f["tag"], 0) + 1

    linhas = ["=== Projeto Ponte · geração de baralho ==="]
    linhas.append(f"frases selecionadas : {len(frases)}")
    linhas.append(f"cartões de reconhecimento: {contagem['reconhecimento']}")
    linhas.append(f"cartões de produção (cloze): {contagem['producao']}")
    linhas.append(f"total de cartões    : {contagem['reconhecimento'] + contagem['producao']}")
    linhas.append("")
    linhas.append("por nível:")
    for nivel in NIVEIS:
        if nivel in por_nivel:
            linhas.append(f"  {nivel}: {por_nivel[nivel]:>3}")
    linhas.append("")
    linhas.append("por assunto:")
    for tag in sorted(por_tag):
        linhas.append(f"  {tag:<14} {por_tag[tag]:>3}")
    linhas.append("")
    linhas.append("arquivos escritos" if escrito else "MODO --dry-run: nada foi escrito")
    return "\n".join(linhas)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Gera baralhos do Anki a partir do TSV de frases.")
    p.add_argument("--config", default=str(RAIZ / "config.json"))
    p.add_argument("--max-cefr", choices=NIVEIS, help="inclui apenas até este nível")
    p.add_argument("--tag", nargs="+", help="inclui apenas estes assuntos")
    p.add_argument("--out", help="diretório de saída (sobrescreve o config)")
    p.add_argument("--dry-run", action="store_true", help="valida sem escrever")
    args = p.parse_args(argv)

    try:
        cfg = carregar_config(Path(args.config))
        frases = ler_frases(RAIZ / cfg["arquivo_de_frases"])
    except ErroDeDados as e:
        print(f"ERRO: {e}", file=sys.stderr)
        return 1

    selecionadas = filtrar(frases, args.max_cefr, args.tag)
    if not selecionadas:
        print("ERRO: nenhum item passou pelos filtros.", file=sys.stderr)
        return 1

    destino = Path(args.out) if args.out else RAIZ / cfg["diretorio_de_saida"]
    contagem = gerar(selecionadas, destino, escrever=not args.dry_run)
    relatorio = montar_relatorio(selecionadas, contagem, escrito=not args.dry_run)
    print(relatorio)

    if not args.dry_run:
        (destino / "relatorio.txt").write_text(relatorio + "\n", encoding="utf-8")
        print(f"\nsaída em: {destino}")
        print("Importe no Anki: Arquivo → Importar → escolha o .tsv → separador Tab.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
