#!/usr/bin/env python3
"""Arnês de avaliação — a peça que separa engenharia de adivinhação.

Roda o mesmo conjunto rotulado contra uma ou mais versões de prompt e imprime
uma tabela comparativa. Termina com código 1 se a versão vencedora ficar abaixo
do limite exigido — é assim que isto vira um portão de CI.

Uso:
    python3 avaliar.py                                   # compara as 3 versões
    python3 avaliar.py --prompt prompts/v3_fewshot.md    # avalia uma só
    python3 avaliar.py --limite 0.9                      # exige 90% de acerto
    python3 avaliar.py --erros                           # lista cada caso errado
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

from provedor import ProviderError, obter_provedor
from triador import triar

RAIZ = Path(__file__).resolve().parent
CASOS_PADRAO = RAIZ / "dados" / "casos.jsonl"
PROMPTS_PADRAO = ["prompts/v1_ingenuo.md", "prompts/v2_estruturado.md", "prompts/v3_fewshot.md"]

# Preço de referência (Claude Opus 5, consultado em 19/08/2026):
# US$ 5,00 por milhão de tokens de entrada, US$ 25,00 por milhão de saída.
PRECO_ENTRADA = 5.00 / 1_000_000
PRECO_SAIDA = 25.00 / 1_000_000


def estimar_tokens(texto: str) -> int:
    """Estimativa grosseira: ~4 caracteres por token em português.

    Isto é uma APROXIMAÇÃO para dar ordem de grandeza. Para número exato use o
    endpoint de contagem de tokens do provedor (`client.messages.count_tokens`).
    Nunca reporte custo estimado como se fosse fatura.
    """
    return max(1, len(texto) // 4)


@dataclass
class Placar:
    prompt: str
    total: int = 0
    validos: int = 0
    formato_limpo: int = 0
    categoria_ok: int = 0
    urgencia_ok: int = 0
    ambos_ok: int = 0
    tentativas: int = 0
    tokens_entrada: int = 0
    tokens_saida: int = 0
    falhas: list[tuple[str, str]] = field(default_factory=list)

    def taxa(self, atributo: str) -> float:
        return getattr(self, atributo) / self.total if self.total else 0.0

    @property
    def custo_estimado(self) -> float:
        return self.tokens_entrada * PRECO_ENTRADA + self.tokens_saida * PRECO_SAIDA


def carregar_casos(caminho: Path) -> list[dict]:
    casos = []
    for numero, linha in enumerate(caminho.read_text(encoding="utf-8").splitlines(), 1):
        linha = linha.strip()
        if not linha:
            continue
        try:
            casos.append(json.loads(linha))
        except json.JSONDecodeError as exc:
            raise SystemExit(f"caso inválido em {caminho}:{numero}: {exc}")
    return casos


def avaliar(prompt: Path, casos: list[dict], nome_provedor: str, tentativas: int) -> Placar:
    sistema = prompt.read_text(encoding="utf-8")
    provedor = obter_provedor(nome_provedor)
    placar = Placar(prompt=prompt.name)

    for caso in casos:
        resultado = triar(caso["chamado"], sistema, provedor, tentativas=tentativas)
        placar.total += 1
        placar.tentativas += resultado.tentativas
        placar.tokens_entrada += estimar_tokens(sistema + caso["chamado"]) * resultado.tentativas
        placar.tokens_saida += estimar_tokens(resultado.bruto)

        if resultado.formato_limpo_inicial:
            placar.formato_limpo += 1

        if not resultado.valido:
            placar.falhas.append((caso["id"], "; ".join(resultado.erros)))
            continue

        placar.validos += 1
        cat_ok = resultado.dados.get("categoria") == caso["categoria"]
        urg_ok = resultado.dados.get("urgencia") == caso["urgencia"]
        placar.categoria_ok += cat_ok
        placar.urgencia_ok += urg_ok
        placar.ambos_ok += cat_ok and urg_ok

        if not cat_ok:
            placar.falhas.append(
                (caso["id"], f"categoria: esperado {caso['categoria']}, "
                             f"veio {resultado.dados.get('categoria')}"))
        elif not urg_ok:
            placar.falhas.append(
                (caso["id"], f"urgencia: esperado {caso['urgencia']}, "
                             f"veio {resultado.dados.get('urgencia')}"))

    return placar


def imprimir_tabela(placares: list[Placar]) -> None:
    cab = f"{'prompt':<24} {'válido':>7} {'fmt.limpo':>10} {'categoria':>10} {'urgência':>9} {'ambos':>7} {'US$/1k':>9}"
    print(cab)
    print("-" * len(cab))
    for p in placares:
        print(f"{p.prompt:<24} "
              f"{p.taxa('validos'):>6.0%} "
              f"{p.taxa('formato_limpo'):>10.0%} "
              f"{p.taxa('categoria_ok'):>10.0%} "
              f"{p.taxa('urgencia_ok'):>9.0%} "
              f"{p.taxa('ambos_ok'):>7.0%} "
              f"{p.custo_estimado / p.total * 1000:>9.3f}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Avalia versões de prompt contra um conjunto rotulado.")
    ap.add_argument("--prompt", action="append", help="pode repetir; padrão: as três versões")
    ap.add_argument("--casos", default=str(CASOS_PADRAO))
    ap.add_argument("--provedor", default="simulado", choices=["simulado", "anthropic"])
    ap.add_argument("--tentativas", type=int, default=2)
    ap.add_argument("--limite", type=float, default=0.0,
                    help="acerto mínimo em 'ambos' para sair com código 0")
    ap.add_argument("--erros", action="store_true", help="lista os casos que falharam")
    args = ap.parse_args(argv)

    casos = carregar_casos(Path(args.casos))
    prompts = [Path(p) for p in (args.prompt or PROMPTS_PADRAO)]

    print(f"conjunto: {args.casos} ({len(casos)} casos) · provedor: {args.provedor}\n")

    placares = []
    for prompt in prompts:
        if not prompt.exists():
            print(f"erro: prompt não encontrado: {prompt}", file=sys.stderr)
            return 2
        try:
            placares.append(avaliar(prompt, casos, args.provedor, args.tentativas))
        except ProviderError as exc:
            print(f"erro de provedor: {exc}", file=sys.stderr)
            return 1

    imprimir_tabela(placares)

    if args.erros:
        for p in placares:
            print(f"\nfalhas de {p.prompt}:")
            for caso_id, motivo in p.falhas:
                print(f"  {caso_id}: {motivo}")

    melhor = max(placares, key=lambda p: p.taxa("ambos_ok"))
    print(f"\nmelhor: {melhor.prompt} — {melhor.taxa('ambos_ok'):.0%} de acerto completo")

    if args.limite and melhor.taxa("ambos_ok") < args.limite:
        print(f"REPROVADO: abaixo do limite de {args.limite:.0%}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
