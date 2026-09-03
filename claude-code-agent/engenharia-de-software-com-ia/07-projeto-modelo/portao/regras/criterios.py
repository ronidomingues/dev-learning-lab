"""Regra: todo critério de aceitação precisa estar coberto por um teste.

Esta é a regra que fecha o laço entre *especificação* e *verificação* — a
tese central do curso. Sem ela, o portão confere forma; com ela, confere
intenção.

Mecânica, deliberadamente simples: cada critério na especificação tem um
identificador (`CA-01`); um teste que cobre o critério cita o identificador
em qualquer lugar do arquivo (nome do teste, comentário, docstring).
Rastreabilidade por convenção de texto — a mesma técnica usada em software
aeroespacial há décadas, e que não exige ferramenta nenhuma.
"""

from __future__ import annotations

import re
from fnmatch import fnmatch
from pathlib import Path

from ..config import Config
from ..diff import Diff
from ..modelo import Achado, Resultado, Severidade

NOME = "criterios"

RE_CRITERIO = re.compile(r"\b(CA-\d{1,3})\b")


def criterios_da_especificacao(texto: str) -> dict[str, str]:
    """Mapeia identificador -> texto do critério."""
    encontrados: dict[str, str] = {}
    for linha in texto.splitlines():
        m = RE_CRITERIO.search(linha)
        if not m:
            continue
        ident = m.group(1)
        if ident in encontrados:
            continue
        descricao = linha.split(ident, 1)[1].lstrip(" *:-—.").strip()
        encontrados[ident] = descricao or "(sem descrição)"
    return encontrados


def criterios_citados(raiz: Path, padroes: list[str]) -> set[str]:
    citados: set[str] = set()
    for caminho in raiz.rglob("*"):
        if not caminho.is_file():
            continue
        rel = caminho.relative_to(raiz).as_posix()
        if not any(fnmatch(rel, p) for p in padroes):
            continue
        try:
            conteudo = caminho.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        citados.update(RE_CRITERIO.findall(conteudo))
    return citados


def verificar(diff: Diff, cfg: Config, raiz: Path | None = None) -> Resultado:
    r = Resultado(regra=NOME)
    raiz = raiz or Path(".")
    espec = raiz / cfg.arquivo_de_especificacao

    if not espec.exists():
        r.pulada = True
        r.motivo_pulada = f"{cfg.arquivo_de_especificacao} não encontrado"
        return r

    esperados = criterios_da_especificacao(espec.read_text(encoding="utf-8"))
    if not esperados:
        r.pulada = True
        r.motivo_pulada = "nenhum critério no formato CA-NN na especificação"
        return r

    citados = criterios_citados(raiz, cfg.caminhos_de_teste)

    for ident, descricao in sorted(esperados.items()):
        if ident not in citados:
            r.achados.append(
                Achado(
                    arquivo=cfg.arquivo_de_especificacao,
                    linha=None,
                    mensagem=f"{ident} sem teste que o cite",
                    detalhe=descricao[:120],
                )
            )

    orfaos = citados - set(esperados)
    for ident in sorted(orfaos):
        r.achados.append(
            Achado(
                arquivo="(testes)",
                linha=None,
                mensagem=f"{ident} citado em teste mas ausente da especificação",
                severidade=Severidade.AVISA,
                detalhe="critério removido da espec ou identificador digitado errado",
            )
        )
    return r
