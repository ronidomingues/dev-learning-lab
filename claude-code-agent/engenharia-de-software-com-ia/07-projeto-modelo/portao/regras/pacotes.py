"""Regra: nenhuma dependência nova entra sem decisão humana.

Motivo, em uma frase: modelos alucinam nomes de pacote, atacantes registram
esses nomes, e `install` executa código. O ataque tem nome — *slopsquatting* —
e a defesa barata é: dependência nova nunca é automática.

Modo offline (padrão) é determinístico: qualquer dependência adicionada que
não esteja na lista aprovada reprova. Modo online (`--online`) consulta o
registro e distingue "não aprovada" de "não existe" — que é bem pior.
"""

from __future__ import annotations

import json
import re
import urllib.error
import urllib.parse
import urllib.request

from ..config import Config
from ..diff import Diff
from ..modelo import Achado, Resultado, Severidade

NOME = "pacotes"
TIMEOUT = 10

ARQ_PYTHON = ("requirements.txt", "requirements-dev.txt", "pyproject.toml")
ARQ_NODE = ("package.json",)

RE_REQ = re.compile(r"^\s*([A-Za-z0-9][A-Za-z0-9._\-]*)\s*(?:\[[^\]]*\])?\s*(?:[<>=!~;].*)?$")
RE_PKG_JSON = re.compile(r'^\s*"([^"]+)"\s*:\s*"([^"]*)"\s*,?\s*$')
RE_PYPROJECT = re.compile(r'^\s*"?([A-Za-z0-9][A-Za-z0-9._\-]*)[^"]*"?\s*,?\s*$')


def _dependencias_adicionadas(diff: Diff) -> list[tuple[str, str, int]]:
    """Devolve (ecossistema, nome, linha) para cada dependência adicionada."""
    achados: list[tuple[str, str, int]] = []
    for arq in diff.arquivos:
        base = arq.caminho.rsplit("/", 1)[-1]
        for linha in arq.adicionadas:
            texto = linha.texto.strip()
            if not texto or texto.startswith("#"):
                continue
            if base in ARQ_NODE:
                m = RE_PKG_JSON.match(linha.texto)
                if m and not m.group(1).startswith(("//", "$")):
                    nome, versao = m.group(1), m.group(2)
                    # heurística: dependência tem versão semver-ish
                    if re.match(r"^[\^~>=<]*\d|^\*$|^latest$", versao or ""):
                        achados.append(("npm", nome, linha.numero))
            elif base in ("requirements.txt", "requirements-dev.txt"):
                m = RE_REQ.match(texto.split("#")[0])
                if m:
                    achados.append(("pypi", m.group(1), linha.numero))
            elif base == "pyproject.toml":
                m = RE_PYPROJECT.match(texto)
                if m and texto.startswith('"'):
                    achados.append(("pypi", m.group(1), linha.numero))
    return achados


def existe_no_registro(ecossistema: str, nome: str) -> bool | None:
    """True/False se souber; None se a rede falhar (não bloqueia por rede)."""
    if ecossistema == "pypi":
        url = f"https://pypi.org/pypi/{nome}/json"
    else:
        url = f"https://registry.npmjs.org/{urllib.parse.quote(nome, safe='@')}"
    try:
        with urllib.request.urlopen(url, timeout=TIMEOUT) as resp:
            json.load(resp)
            return True
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return False
        return None
    except Exception:
        return None


def verificar(diff: Diff, cfg: Config) -> Resultado:
    r = Resultado(regra=NOME)
    permitidas = {p.lower() for p in cfg.dependencias_permitidas}

    for ecossistema, nome, linha in _dependencias_adicionadas(diff):
        if nome.lower() in permitidas:
            continue

        if not cfg.checar_registro_online:
            r.achados.append(
                Achado(
                    arquivo=_arquivo_de(diff, nome) or "(dependências)",
                    linha=linha,
                    mensagem=f"dependência nova não aprovada: {nome} ({ecossistema})",
                    detalhe=(
                        "confirme que o pacote existe e é o que você espera, "
                        "e então acrescente a dependencias_permitidas"
                    ),
                )
            )
            continue

        existe = existe_no_registro(ecossistema, nome)
        if existe is False:
            r.achados.append(
                Achado(
                    arquivo=_arquivo_de(diff, nome) or "(dependências)",
                    linha=linha,
                    mensagem=f"PACOTE INEXISTENTE no {ecossistema}: {nome}",
                    detalhe="forte indício de alucinação. NÃO instale.",
                )
            )
        elif existe is None:
            r.achados.append(
                Achado(
                    arquivo="(rede)",
                    linha=None,
                    mensagem=f"não foi possível verificar {nome} no {ecossistema}",
                    severidade=Severidade.AVISA,
                    detalhe="falha de rede; verifique manualmente",
                )
            )
        else:
            r.achados.append(
                Achado(
                    arquivo=_arquivo_de(diff, nome) or "(dependências)",
                    linha=linha,
                    mensagem=f"dependência nova não aprovada: {nome} ({ecossistema})",
                    detalhe="o pacote existe, mas existir não é o mesmo que ser seguro",
                )
            )
    return r


def _arquivo_de(diff: Diff, nome: str) -> str | None:
    for arq in diff.arquivos:
        for linha in arq.adicionadas:
            if nome in linha.texto:
                return arq.caminho
    return None
