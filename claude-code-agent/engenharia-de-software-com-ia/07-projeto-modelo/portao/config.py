"""Configuração do portão.

JSON, não TOML: `tomllib` só existe a partir do Python 3.11, e o portão
precisa rodar no 3.10 sem instalar nada.

Toda configuração tem padrão. Um repositório sem `portao.json` ainda é
verificado — com os padrões conservadores. Ferramenta que exige configuração
antes de dar qualquer valor não é adotada.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

PADROES_SEGREDO_IGNORADOS = ["*.lock", "*.snap", "package-lock.json"]


@dataclass
class Config:
    # escopo
    escopo_permitido: list[str] = field(default_factory=lambda: ["**"])
    escopo_proibido: list[str] = field(
        default_factory=lambda: [
            ".github/workflows/**",
            "**/*.pem",
            "**/*.key",
            ".env",
            ".env.*",
        ]
    )
    caminhos_de_teste: list[str] = field(
        default_factory=lambda: [
            "tests/**",
            "test/**",
            "**/test_*.py",
            "**/*_test.go",
            "**/*.test.ts",
            "**/*.test.js",
            "**/*.spec.ts",
        ]
    )
    testes_editaveis: bool = False

    # tamanho
    max_alteracoes_total: int = 400
    max_alteracoes_por_arquivo: int = 250
    max_arquivos: int = 15

    # segredos
    segredos_ignorar_caminhos: list[str] = field(
        default_factory=lambda: list(PADROES_SEGREDO_IGNORADOS)
    )
    entropia_minima: float = 4.2
    tamanho_minimo_entropia: int = 24

    # pacotes
    dependencias_permitidas: list[str] = field(default_factory=list)
    checar_registro_online: bool = False

    # critérios
    arquivo_de_especificacao: str = "ESPEC.md"

    @staticmethod
    def de_arquivo(caminho: str | Path) -> "Config":
        p = Path(caminho)
        if not p.exists():
            return Config()
        dados = json.loads(p.read_text(encoding="utf-8"))
        return Config.de_dict(dados)

    @staticmethod
    def de_dict(dados: dict) -> "Config":
        cfg = Config()
        conhecidos = {f for f in cfg.__dataclass_fields__}
        desconhecidos = set(dados) - conhecidos
        if desconhecidos:
            raise ValueError(
                "chaves desconhecidas em portao.json: "
                + ", ".join(sorted(desconhecidos))
            )
        for chave, valor in dados.items():
            setattr(cfg, chave, valor)
        cfg.validar()
        return cfg

    def validar(self) -> None:
        for campo in (
            "max_alteracoes_total",
            "max_alteracoes_por_arquivo",
            "max_arquivos",
            "tamanho_minimo_entropia",
        ):
            v = getattr(self, campo)
            if not isinstance(v, int) or v <= 0:
                raise ValueError(f"{campo} deve ser inteiro positivo, veio {v!r}")
        if not isinstance(self.entropia_minima, (int, float)):
            raise ValueError("entropia_minima deve ser número")
        if not self.escopo_permitido:
            raise ValueError("escopo_permitido não pode ser lista vazia")
