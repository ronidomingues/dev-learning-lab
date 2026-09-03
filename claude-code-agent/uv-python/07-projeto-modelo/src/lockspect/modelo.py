"""Estruturas de dados do lockfile.

Só `dataclass` e tipos da biblioteca padrão: o modelo não deve depender de como
o arquivo foi lido nem de como o relatório será impresso.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Pacote:
    """Um pacote travado no lockfile."""

    nome: str
    versao: str
    tipo_de_fonte: str
    """`registry`, `editable`, `directory`, `git`, `url` ou `desconhecida`."""
    fonte: str
    """A URL do índice, o caminho local ou a URL do repositório Git."""
    dependencias: tuple[str, ...] = ()
    dependencias_de_dev: tuple[str, ...] = ()
    qtd_wheels: int = 0
    tem_sdist: bool = False

    @property
    def e_local(self) -> bool:
        """Verdadeiro para o próprio projeto e para membros do workspace."""
        return self.tipo_de_fonte in {"editable", "directory", "virtual"}

    @property
    def so_sdist(self) -> bool:
        """Sem wheel: será compilado na instalação. Costuma ser o gargalo."""
        return self.tem_sdist and self.qtd_wheels == 0


@dataclass(frozen=True)
class Lock:
    """O lockfile inteiro."""

    versao_do_formato: int
    revisao: int | None
    requires_python: str | None
    pacotes: tuple[Pacote, ...] = field(default=())

    def por_nome(self) -> dict[str, Pacote]:
        return {p.nome: p for p in self.pacotes}

    @property
    def raizes(self) -> tuple[Pacote, ...]:
        """Pacotes locais — o projeto e os membros do workspace."""
        return tuple(p for p in self.pacotes if p.e_local)

    @property
    def de_terceiros(self) -> tuple[Pacote, ...]:
        return tuple(p for p in self.pacotes if not p.e_local)

    def dependentes_de(self, nome: str) -> tuple[str, ...]:
        """Quem depende de `nome`. Responde 'por que isso está aqui?'."""
        alvo = _normalizar(nome)
        achados = [
            p.nome
            for p in self.pacotes
            if alvo in {_normalizar(d) for d in (*p.dependencias, *p.dependencias_de_dev)}
        ]
        return tuple(sorted(achados))


def _normalizar(nome: str) -> str:
    """Normalização de nome de projeto conforme a PEP 503.

    `Foo.Bar_baz` e `foo-bar-baz` são o mesmo pacote para o índice.
    """
    resultado = []
    anterior_foi_separador = False
    for caractere in nome.lower():
        if caractere in "-_.":
            if not anterior_foi_separador:
                resultado.append("-")
            anterior_foi_separador = True
        else:
            resultado.append(caractere)
            anterior_foi_separador = False
    return "".join(resultado).strip("-")
