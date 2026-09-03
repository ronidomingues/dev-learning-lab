"""Regra: o diff precisa caber numa revisão humana.

O limite não é estético. Um diff que ninguém consegue revisar em 10 minutos
não é revisado — é aprovado. E aprovação sem revisão é pior que nenhuma
revisão, porque produz a ilusão de controle.
"""

from __future__ import annotations

from ..config import Config
from ..diff import Diff
from ..modelo import Achado, Resultado, Severidade

NOME = "tamanho"


def verificar(diff: Diff, cfg: Config) -> Resultado:
    r = Resultado(regra=NOME)

    if len(diff.arquivos) > cfg.max_arquivos:
        r.achados.append(
            Achado(
                arquivo="(diff)",
                linha=None,
                mensagem=(
                    f"{len(diff.arquivos)} arquivos alterados; "
                    f"o limite é {cfg.max_arquivos}"
                ),
                detalhe="fatie a tarefa",
            )
        )

    if diff.total_alteracoes > cfg.max_alteracoes_total:
        r.achados.append(
            Achado(
                arquivo="(diff)",
                linha=None,
                mensagem=(
                    f"{diff.total_alteracoes} linhas alteradas; "
                    f"o limite é {cfg.max_alteracoes_total}"
                ),
                detalhe="fatie a tarefa",
            )
        )

    for arq in diff.arquivos:
        if arq.total_alteracoes > cfg.max_alteracoes_por_arquivo:
            r.achados.append(
                Achado(
                    arquivo=arq.caminho,
                    linha=None,
                    mensagem=(
                        f"{arq.total_alteracoes} linhas alteradas neste arquivo; "
                        f"o limite é {cfg.max_alteracoes_por_arquivo}"
                    ),
                    severidade=Severidade.AVISA,
                    detalhe=(
                        "arquivo novo e grande costuma ser legítimo; "
                        "reescrita disfarçada de ajuste, não"
                    ),
                )
            )
    return r
