"""Configuração da aplicação, lida do ambiente e validada na partida.

Por que não ler `os.environ` espalhado pelo código:
1. o erro aparece no primeiro acesso, em produção, dentro de um `try` qualquer;
2. não dá para saber, olhando o código, quais variáveis a app precisa;
3. não dá para testar com outra configuração sem mexer no ambiente global.

Aqui tudo é lido uma vez, validado, e vira um objeto imutável.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


class ErroDeConfiguracao(RuntimeError):
    """Configuração ausente ou inválida. Falha na partida, não no meio do uso."""


@dataclass(frozen=True)
class Config:
    caminho_banco: Path
    ambiente: str          # "dev" | "prod"
    iteracoes_hash: int    # custo do PBKDF2
    fuso: str

    @property
    def em_producao(self) -> bool:
        return self.ambiente == "prod"


def carregar(env: dict[str, str] | None = None) -> Config:
    """Lê a configuração do ambiente. `env` existe para os testes injetarem outra."""
    env = dict(os.environ if env is None else env)

    ambiente = env.get("PAINEL_AMBIENTE", "dev")
    if ambiente not in {"dev", "prod"}:
        raise ErroDeConfiguracao(
            f"PAINEL_AMBIENTE='{ambiente}' inválido; use 'dev' ou 'prod'."
        )

    caminho = Path(env.get("PAINEL_BANCO", RAIZ / "dados" / "painel.db"))
    caminho.parent.mkdir(parents=True, exist_ok=True)

    try:
        iteracoes = int(env.get("PAINEL_HASH_ITER", "240000"))
    except ValueError as e:
        raise ErroDeConfiguracao("PAINEL_HASH_ITER precisa ser um inteiro.") from e
    if iteracoes < 100_000:
        raise ErroDeConfiguracao(
            f"PAINEL_HASH_ITER={iteracoes} é baixo demais para PBKDF2-SHA256; use >= 100000."
        )

    return Config(
        caminho_banco=caminho,
        ambiente=ambiente,
        iteracoes_hash=iteracoes,
        fuso=env.get("PAINEL_FUSO", "America/Sao_Paulo"),
    )
