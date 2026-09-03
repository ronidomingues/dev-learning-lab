"""Leitura e validação do arquivo `uv.lock`.

O `uv.lock` é TOML. A partir do Python 3.11 a leitura de TOML está na biblioteca
padrão (`tomllib`, PEP 680); antes disso é preciso o pacote `tomli`. O import
condicional abaixo é o padrão da comunidade para esse caso — e é o motivo de o
`pyproject.toml` deste projeto declarar:

    "tomli>=2.0 ; python_version < '3.11'"

Esse marcador de ambiente é resolvido pelo uv: em 3.11+ o `tomli` nem é baixado.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from lockspect.modelo import Lock, Pacote

if sys.version_info >= (3, 11):
    import tomllib
else:  # pragma: no cover - depende da versão do interpretador
    import tomli as tomllib

FORMATOS_SUPORTADOS = frozenset({1})


class LockInvalido(Exception):
    """O arquivo existe mas não é um `uv.lock` que sabemos ler."""


def ler_lock(caminho: str | Path) -> Lock:
    """Lê um `uv.lock` e devolve o modelo.

    Levanta `FileNotFoundError` se o arquivo não existir e `LockInvalido` se o
    conteúdo não for um lockfile de uv reconhecível.
    """
    caminho = Path(caminho)
    if caminho.is_dir():
        caminho = caminho / "uv.lock"
    if not caminho.exists():
        raise FileNotFoundError(f"não encontrei o lockfile em {caminho}")

    try:
        dados: dict[str, Any] = tomllib.loads(caminho.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as erro:
        raise LockInvalido(f"{caminho} não é TOML válido: {erro}") from erro

    versao = dados.get("version")
    if not isinstance(versao, int):
        raise LockInvalido(f"{caminho} não tem a chave 'version' — é mesmo um uv.lock?")
    if versao not in FORMATOS_SUPORTADOS:
        raise LockInvalido(
            f"formato de lockfile versão {versao}; esta ferramenta lê "
            f"{sorted(FORMATOS_SUPORTADOS)}. Atualize o lockspect."
        )

    pacotes = tuple(_ler_pacote(bruto) for bruto in dados.get("package", []))
    return Lock(
        versao_do_formato=versao,
        revisao=dados.get("revision"),
        requires_python=dados.get("requires-python"),
        pacotes=pacotes,
    )


def _ler_pacote(bruto: dict[str, Any]) -> Pacote:
    tipo, fonte = _ler_fonte(bruto.get("source", {}))
    dev = bruto.get("dev-dependencies", {}) or {}
    return Pacote(
        nome=bruto.get("name", "<sem-nome>"),
        versao=bruto.get("version", "<sem-versão>"),
        tipo_de_fonte=tipo,
        fonte=fonte,
        dependencias=_nomes(bruto.get("dependencies", [])),
        dependencias_de_dev=tuple(sorted({n for grupo in dev.values() for n in _nomes(grupo)})),
        qtd_wheels=len(bruto.get("wheels", []) or []),
        tem_sdist="sdist" in bruto,
    )


def _ler_fonte(fonte: dict[str, Any]) -> tuple[str, str]:
    """Converte o dicionário `source` do TOML em (tipo, descrição)."""
    for chave in ("registry", "editable", "directory", "git", "url", "path", "virtual"):
        if chave in fonte:
            return chave, str(fonte[chave])
    return "desconhecida", ""


def _nomes(itens: Any) -> tuple[str, ...]:
    """Extrai nomes de uma lista de dependências do lockfile.

    O uv escreve `[{ name = "idna" }, { name = "urllib3", marker = "..." }]`.
    """
    if not isinstance(itens, list):
        return ()
    nomes = [item["name"] for item in itens if isinstance(item, dict) and "name" in item]
    return tuple(sorted(set(nomes)))
