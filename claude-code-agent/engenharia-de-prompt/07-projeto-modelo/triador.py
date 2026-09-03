#!/usr/bin/env python3
"""Triador de chamados — a peça que roda em produção.

Uso:
    python3 triador.py --chamado "Fui cobrado duas vezes na fatura"
    python3 triador.py --prompt prompts/v2_estruturado.md --chamado "..."
    python3 triador.py --provedor anthropic --chamado "..."      # precisa de chave

Saída: uma linha de JSON válido no stdout, ou uma mensagem de erro no stderr
com código de saída 1. Foi feito para ser encadeado em pipe.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

from provedor import ProviderError, obter_provedor

CATEGORIAS_VALIDAS = {"cobranca", "bug", "acesso", "duvida"}
URGENCIAS_VALIDAS = {"alta", "normal"}
LIMITE_RESUMO = 80

RAIZ = Path(__file__).resolve().parent
PROMPT_PADRAO = RAIZ / "prompts" / "v3_fewshot.md"


# --------------------------------------------------------------------------
# Extração e validação — onde 90% dos bugs de aplicação com LLM moram
# --------------------------------------------------------------------------

_CERCA = re.compile(r"```(?:json)?\s*(.*?)```", re.DOTALL)


@dataclass
class Resultado:
    """O que sai de uma triagem, incluindo os metadados que a avaliação usa."""

    bruto: str
    dados: dict | None = None
    formato_limpo: bool = False       # o modelo devolveu só o JSON?
    formato_limpo_inicial: bool = False  # ...já na PRIMEIRA tentativa (a métrica honesta)
    erros: list[str] = field(default_factory=list)
    tentativas: int = 1

    @property
    def valido(self) -> bool:
        return self.dados is not None and not self.erros


def extrair_json(texto: str) -> tuple[dict | None, bool]:
    """Tenta obter um objeto JSON de uma resposta de modelo.

    Devolve (objeto, formato_limpo). `formato_limpo` é True apenas quando a
    resposta inteira já era JSON — é a métrica que diz se o seu prompt está
    conseguindo calar a tagarelice do modelo.

    Ordem de tentativa, da mais estrita para a mais tolerante:
      1. a resposta inteira;
      2. o conteúdo de uma cerca ```json ... ```;
      3. o primeiro par de chaves balanceadas no meio do texto.
    """
    limpo = texto.strip()
    try:
        return json.loads(limpo), True
    except json.JSONDecodeError:
        pass

    cerca = _CERCA.search(texto)
    if cerca:
        try:
            return json.loads(cerca.group(1).strip()), False
        except json.JSONDecodeError:
            pass

    inicio = texto.find("{")
    if inicio != -1:
        profundidade = 0
        for i in range(inicio, len(texto)):
            if texto[i] == "{":
                profundidade += 1
            elif texto[i] == "}":
                profundidade -= 1
                if profundidade == 0:
                    try:
                        return json.loads(texto[inicio : i + 1]), False
                    except json.JSONDecodeError:
                        break
    return None, False


def validar(dados: dict) -> list[str]:
    """Valida o objeto contra o contrato. Devolve a lista de problemas."""
    erros: list[str] = []

    for campo in ("categoria", "urgencia", "resumo"):
        if campo not in dados:
            erros.append(f"campo ausente: {campo}")

    categoria = dados.get("categoria")
    if categoria is not None and categoria not in CATEGORIAS_VALIDAS:
        erros.append(f"categoria fora do conjunto: {categoria!r}")

    urgencia = dados.get("urgencia")
    if urgencia is not None and urgencia not in URGENCIAS_VALIDAS:
        erros.append(f"urgencia fora do conjunto: {urgencia!r}")

    resumo = dados.get("resumo")
    if isinstance(resumo, str) and len(resumo) > LIMITE_RESUMO:
        erros.append(f"resumo com {len(resumo)} caracteres (limite {LIMITE_RESUMO})")

    return erros


# --------------------------------------------------------------------------
# Triagem
# --------------------------------------------------------------------------


def triar(chamado: str, sistema: str, provedor, tentativas: int = 2) -> Resultado:
    """Classifica um chamado, com uma rodada de correção se a saída não validar.

    A rodada de correção devolve ao modelo o erro literal do validador. É a
    técnica mais barata de recuperação que existe e resolve a maioria das saídas
    malformadas de modelos grandes. Com o provedor simulado ela não muda nada —
    a caricatura é determinística — e isso está certo: o teste existe para
    provar que o caminho de código funciona, não para inflar a métrica.
    """
    mensagem = chamado
    ultimo = Resultado(bruto="")
    limpo_inicial = False

    for tentativa in range(1, tentativas + 1):
        bruto = provedor.completar(sistema, mensagem)
        dados, limpo = extrair_json(bruto)
        if tentativa == 1:
            limpo_inicial = limpo
        erros = ["resposta não contém JSON"] if dados is None else validar(dados)
        ultimo = Resultado(bruto=bruto, dados=dados, formato_limpo=limpo,
                           formato_limpo_inicial=limpo_inicial,
                           erros=erros, tentativas=tentativa)
        if ultimo.valido:
            return ultimo

        mensagem = (
            f"{chamado}\n\n"
            f"Sua resposta anterior foi rejeitada pelo validador com estes erros:\n"
            f"{chr(10).join('- ' + e for e in erros)}\n"
            f"Responda novamente, apenas o JSON válido."
        )

    return ultimo


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Triagem de chamados de suporte.")
    ap.add_argument("--chamado", help="texto do chamado; se ausente, lê do stdin")
    ap.add_argument("--prompt", default=str(PROMPT_PADRAO), help="arquivo de prompt de sistema")
    ap.add_argument("--provedor", default="simulado", choices=["simulado", "anthropic"])
    ap.add_argument("--tentativas", type=int, default=2)
    ap.add_argument("--bruto", action="store_true", help="imprime a resposta crua do modelo")
    args = ap.parse_args(argv)

    chamado = args.chamado if args.chamado is not None else sys.stdin.read()
    if not chamado.strip():
        print("erro: chamado vazio", file=sys.stderr)
        return 2

    try:
        sistema = Path(args.prompt).read_text(encoding="utf-8")
    except OSError as exc:
        print(f"erro: não consegui ler o prompt {args.prompt}: {exc}", file=sys.stderr)
        return 2

    try:
        provedor = obter_provedor(args.provedor)
        resultado = triar(chamado, sistema, provedor, tentativas=args.tentativas)
    except ProviderError as exc:
        print(f"erro de provedor: {exc}", file=sys.stderr)
        return 1

    if args.bruto:
        print(resultado.bruto)

    if not resultado.valido:
        print(f"saída inválida após {resultado.tentativas} tentativa(s): "
              f"{'; '.join(resultado.erros)}", file=sys.stderr)
        return 1

    print(json.dumps(resultado.dados, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
