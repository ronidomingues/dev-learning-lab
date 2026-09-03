"""Regra: o diff só pode tocar no que foi combinado.

Esta é a regra mais importante do portão e a mais barata de rodar.
A falha que ela pega — "o agente aproveitou para mexer em outra coisa" —
é a que mais passa despercebida em revisão humana, porque o revisor lê o
arquivo que esperava e para por aí.
"""

from __future__ import annotations

from fnmatch import fnmatch

from ..config import Config
from ..diff import Diff
from ..modelo import Achado, Resultado, Severidade

NOME = "escopo"


def casa(caminho: str, padroes: list[str]) -> bool:
    for p in padroes:
        if fnmatch(caminho, p):
            return True
        # "src/**" deve casar com "src/a/b.py" e também com "src/b.py"
        if p.endswith("/**") and (
            caminho == p[:-3] or caminho.startswith(p[:-2])
        ):
            return True
        if p == "**":
            return True
    return False


def verificar(diff: Diff, cfg: Config) -> Resultado:
    r = Resultado(regra=NOME)
    for arq in diff.arquivos:
        if not casa(arq.caminho, cfg.escopo_permitido):
            r.achados.append(
                Achado(
                    arquivo=arq.caminho,
                    linha=None,
                    mensagem="fora do escopo permitido",
                    detalhe=f"permitido: {', '.join(cfg.escopo_permitido)}",
                )
            )
            continue
        if casa(arq.caminho, cfg.escopo_proibido):
            r.achados.append(
                Achado(
                    arquivo=arq.caminho,
                    linha=None,
                    mensagem="caminho explicitamente proibido",
                    detalhe="alteração aqui exige mudança manual e revisão dedicada",
                )
            )
            continue
        if not cfg.testes_editaveis and casa(arq.caminho, cfg.caminhos_de_teste):
            r.achados.append(
                Achado(
                    arquivo=arq.caminho,
                    linha=None,
                    mensagem="arquivo de teste alterado",
                    detalhe=(
                        "o teste é o critério; alterá-lo para fazer o código "
                        "passar destrói a evidência. Use --testes-editaveis "
                        "quando a tarefa FOR escrever teste."
                    ),
                )
            )
    return r
