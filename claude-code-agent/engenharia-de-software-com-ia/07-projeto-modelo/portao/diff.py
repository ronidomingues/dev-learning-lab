"""Leitor de *unified diff*.

Por que escrever um leitor em vez de usar biblioteca: o portão precisa rodar
em qualquer máquina, dentro de qualquer container mínimo, sem instalar nada.
Uma dependência a mais no portão é uma dependência a mais na superfície de
ataque que o portão existe para vigiar.

Suporta o formato produzido por `git diff` e `git diff --cached`.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

CABECALHO = re.compile(r"^diff --git a/(?P<a>.+?) b/(?P<b>.+)$")
ORIGEM = re.compile(r"^--- (?:a/(?P<caminho>.*)|/dev/null)$")
DESTINO = re.compile(r"^\+\+\+ (?:b/(?P<caminho>.*)|/dev/null)$")
HUNK = re.compile(r"^@@ -\d+(?:,\d+)? \+(?P<inicio>\d+)(?:,(?P<qtd>\d+))? @@")


@dataclass
class LinhaAdicionada:
    numero: int
    texto: str


@dataclass
class ArquivoDiff:
    caminho: str
    novo: bool = False
    removido: bool = False
    renomeado_de: str | None = None
    adicionadas: list[LinhaAdicionada] = field(default_factory=list)
    removidas: int = 0

    @property
    def total_alteracoes(self) -> int:
        return len(self.adicionadas) + self.removidas


@dataclass
class Diff:
    arquivos: list[ArquivoDiff] = field(default_factory=list)

    @property
    def caminhos(self) -> list[str]:
        return [a.caminho for a in self.arquivos]

    @property
    def total_alteracoes(self) -> int:
        return sum(a.total_alteracoes for a in self.arquivos)

    def por_caminho(self, caminho: str) -> ArquivoDiff | None:
        for a in self.arquivos:
            if a.caminho == caminho:
                return a
        return None


def ler(texto: str) -> Diff:
    """Converte o texto de um unified diff em uma estrutura navegável."""
    diff = Diff()
    atual: ArquivoDiff | None = None
    proxima_linha = 0
    dentro_de_hunk = False

    for bruta in texto.splitlines():
        cab = CABECALHO.match(bruta)
        if cab:
            atual = ArquivoDiff(caminho=cab.group("b"))
            if cab.group("a") != cab.group("b"):
                atual.renomeado_de = cab.group("a")
            diff.arquivos.append(atual)
            dentro_de_hunk = False
            continue

        if atual is None:
            continue

        if bruta.startswith("--- "):
            m = ORIGEM.match(bruta)
            if m and m.group("caminho") is None:
                atual.novo = True
            dentro_de_hunk = False
            continue

        if bruta.startswith("+++ "):
            m = DESTINO.match(bruta)
            if m and m.group("caminho") is None:
                atual.removido = True
            dentro_de_hunk = False
            continue

        h = HUNK.match(bruta)
        if h:
            proxima_linha = int(h.group("inicio"))
            dentro_de_hunk = True
            continue

        if not dentro_de_hunk:
            continue

        if bruta.startswith("+"):
            atual.adicionadas.append(LinhaAdicionada(proxima_linha, bruta[1:]))
            proxima_linha += 1
        elif bruta.startswith("-"):
            atual.removidas += 1
        elif bruta.startswith("\\"):
            # "\ No newline at end of file" — não é conteúdo
            continue
        else:
            proxima_linha += 1

    return diff
