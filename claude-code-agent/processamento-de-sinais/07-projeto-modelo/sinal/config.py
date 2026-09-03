"""Configuração central do projeto.

Uma coisa que tutoriais omitem e projetos reais têm: valores mágicos não ficam
espalhados pelo código. Tudo que é sintonizável mora aqui, com um valor padrão
justificado, e pode ser sobrescrito por variável de ambiente.
"""

from __future__ import annotations

import os
from dataclasses import dataclass


def _env_float(nome: str, padrao: float) -> float:
    """Lê um float de variável de ambiente, caindo no padrão se ausente/inválido."""
    bruto = os.environ.get(nome)
    if bruto is None:
        return padrao
    try:
        return float(bruto)
    except ValueError:
        # Falhar em silêncio aqui esconderia erro de digitação do usuário.
        raise ConfiguracaoInvalida(f"{nome}={bruto!r} não é um número.") from None


class ConfiguracaoInvalida(ValueError):
    """Configuração fornecida pelo ambiente não faz sentido."""


@dataclass(frozen=True)
class Config:
    """Parâmetros de análise.

    frequencia_rede: 60.0 no Brasil e na América do Norte, 50.0 na Europa.
        É a frequência do zumbido de alimentação que aparece em gravação
        mal aterrada. Sobrescreva com SINAL_FREQ_REDE=50.
    f0_min / f0_max: faixa de busca da fundamental, em Hz. O padrão cobre
        do Mi grave da guitarra de 5 cordas (~41 Hz) ao topo do violino (~2 kHz).
    n_fft: tamanho do bloco da FFT usado na análise espectral. Potência de 2
        porque o algoritmo radix-2 é o caminho mais rápido da FFT.
    limiar_clip: valor absoluto normalizado a partir do qual a amostra é
        considerada ceifada (clipping). 0.999 e não 1.0 porque quantizadores
        de 16 bits saturam em 32767/32768 = 0.99997.
    """

    frequencia_rede: float = 60.0
    f0_min: float = 40.0
    f0_max: float = 2000.0
    n_fft: int = 8192
    limiar_clip: float = 0.999

    @classmethod
    def do_ambiente(cls) -> "Config":
        """Constrói a configuração aplicando as variáveis SINAL_*."""
        cfg = cls(
            frequencia_rede=_env_float("SINAL_FREQ_REDE", 60.0),
            f0_min=_env_float("SINAL_F0_MIN", 40.0),
            f0_max=_env_float("SINAL_F0_MAX", 2000.0),
            n_fft=int(_env_float("SINAL_N_FFT", 8192)),
            limiar_clip=_env_float("SINAL_LIMIAR_CLIP", 0.999),
        )
        cfg.validar()
        return cfg

    def validar(self) -> None:
        if self.f0_min <= 0 or self.f0_max <= self.f0_min:
            raise ConfiguracaoInvalida(
                f"faixa de f0 inválida: [{self.f0_min}, {self.f0_max}] Hz"
            )
        if self.n_fft < 256 or (self.n_fft & (self.n_fft - 1)) != 0:
            raise ConfiguracaoInvalida(
                f"n_fft={self.n_fft} deve ser potência de 2 e >= 256"
            )
