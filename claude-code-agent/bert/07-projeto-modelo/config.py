"""Configuração central do projeto.

Tudo que muda entre máquinas (caminhos, hiperparâmetros, modelo base) vive aqui e
pode ser sobrescrito por variável de ambiente. Nenhum outro arquivo do projeto lê
`os.environ` diretamente — essa disciplina é o que permite rodar o mesmo código em
notebook, em CI e em produção sem editar fonte.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

RAIZ = Path(__file__).resolve().parent


def _env(nome: str, padrao: str) -> str:
    return os.environ.get(nome, padrao)


@dataclass(frozen=True)
class Config:
    # --- Modelo ---------------------------------------------------------
    # BERTimbau: BERT-base pré-treinado em português do Brasil (BrWaC), licença MIT.
    # Troque por "answerdotai/ModernBERT-base" (inglês) ou "jhu-clsp/mmBERT-base"
    # (multilíngue) para comparar — o restante do código não muda.
    modelo_base: str = _env("MODELO_BASE", "neuralmind/bert-base-portuguese-cased")

    # --- Dados ----------------------------------------------------------
    caminho_dados: Path = Path(_env("CAMINHO_DADOS", str(RAIZ / "dados" / "chamados.csv")))
    coluna_texto: str = "texto"
    coluna_rotulo: str = "categoria"

    # --- Saída ----------------------------------------------------------
    dir_saida: Path = Path(_env("DIR_SAIDA", str(RAIZ / "modelo-treinado")))
    dir_checkpoints: Path = Path(_env("DIR_CHECKPOINTS", str(RAIZ / "checkpoints")))

    # --- Hiperparâmetros ------------------------------------------------
    # Estes quatro números são 90% do que se ajusta na prática.
    # A receita do paper original (Devlin et al., 2019, Apêndice A.3) é
    # lr ∈ {5e-5, 4e-5, 3e-5, 2e-5}, lote ∈ {16, 32}, 2 a 4 épocas — e continua
    # sendo o melhor ponto de partida em 2026. Aqui o lote é 8 (cabe em CPU) e
    # são 6 épocas porque o conjunto é pequeno: com 122 exemplos de treino, 4
    # épocas dão só ~92 passos de gradiente, e o modelo fica subtreinado (mesma
    # acurácia, porém com confiança bem mais baixa). Ver a tabela de experimentos
    # no README.
    epocas: float = float(_env("EPOCAS", "6"))
    lote: int = int(_env("LOTE", "8"))
    taxa_aprendizado: float = float(_env("TAXA_APRENDIZADO", "5e-5"))
    max_tokens: int = int(_env("MAX_TOKENS", "128"))

    # --- Reprodutibilidade e divisão dos dados --------------------------
    semente: int = int(_env("SEMENTE", "42"))
    fracao_teste: float = float(_env("FRACAO_TESTE", "0.2"))
    fracao_validacao: float = float(_env("FRACAO_VALIDACAO", "0.15"))

    # --- Inferência -----------------------------------------------------
    # Abaixo deste limiar a predição é tratada como "não sei" e vai para triagem
    # humana. Um classificador em produção sem limiar de confiança é uma armadilha:
    # ele sempre responde alguma coisa, inclusive para texto fora do domínio.
    limiar_confianca: float = float(_env("LIMIAR_CONFIANCA", "0.60"))

    rotulo_indefinido: str = "INDEFINIDO"
    categorias: tuple[str, ...] = field(
        default=("CANCELAMENTO", "COMERCIAL", "FINANCEIRO", "TECNICO")
    )


config = Config()
