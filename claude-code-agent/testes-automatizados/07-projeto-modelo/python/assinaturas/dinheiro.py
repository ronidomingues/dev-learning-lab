"""Dinheiro representado em centavos inteiros.

Regra do projeto: **dinheiro nunca é float**. `0.1 + 0.2 != 0.3` em ponto
flutuante binário (IEEE 754), e um erro de um centavo em cobrança recorrente
vira reclamação no Procon. Usamos `int` de centavos e arredondamos de forma
explícita e documentada.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal


class ValorInvalido(ValueError):
    """Erro de domínio: valor monetário impossível."""


@dataclass(frozen=True, slots=True, order=True)
class Dinheiro:
    """Quantia em centavos de real. Imutável — operações retornam novo objeto."""

    centavos: int

    def __post_init__(self) -> None:
        if isinstance(self.centavos, bool) or not isinstance(self.centavos, int):
            raise ValorInvalido(f"centavos deve ser int, veio {type(self.centavos).__name__}")
        if self.centavos < 0:
            raise ValorInvalido(f"dinheiro não pode ser negativo: {self.centavos}")

    # ---- construtores alternativos -------------------------------------

    @classmethod
    def de_reais(cls, texto: str | int | float | Decimal) -> Dinheiro:
        """Constrói a partir de reais. Aceita "19,90", "19.90", 19 ou Decimal.

        Não aceita float silenciosamente por acidente: se vier float, o valor é
        convertido via `str` antes de virar Decimal, o que evita o clássico
        `Decimal(0.1) == 0.1000000000000000055511151231257827021181583404541015625`.
        """
        if isinstance(texto, str):
            limpo = texto.strip().replace("R$", "").replace(" ", "")
            # aceita tanto 1.234,56 (pt-BR) quanto 1234.56 (en-US)
            if "," in limpo:
                limpo = limpo.replace(".", "").replace(",", ".")
            bruto = Decimal(limpo)
        else:
            bruto = Decimal(str(texto))
        centavos = (bruto * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
        return cls(int(centavos))

    # ---- aritmética -----------------------------------------------------

    def __add__(self, outro: Dinheiro) -> Dinheiro:
        return Dinheiro(self.centavos + outro.centavos)

    def __sub__(self, outro: Dinheiro) -> Dinheiro:
        return Dinheiro(self.centavos - outro.centavos)  # ValorInvalido se ficar negativo

    def __mul__(self, fator: int) -> Dinheiro:
        if not isinstance(fator, int) or isinstance(fator, bool):
            raise ValorInvalido("multiplique dinheiro só por int (quantidade)")
        return Dinheiro(self.centavos * fator)

    def aplicar_desconto(self, percentual: int) -> Dinheiro:
        """Desconta `percentual`% arredondando **meio para cima** (ROUND_HALF_UP).

        A escolha do arredondamento é decisão de negócio, não de programação:
        R$ 19,99 com 10% de desconto dá 1,999 centavos de desconto. Arredondar
        para cima favorece o cliente em 1 centavo; para baixo favorece a empresa.
        Escolhemos favorecer o cliente e **testamos exatamente esse caso**.
        """
        if not isinstance(percentual, int) or isinstance(percentual, bool):
            raise ValorInvalido("percentual deve ser int")
        if not 0 <= percentual <= 100:
            raise ValorInvalido(f"percentual fora de 0..100: {percentual}")
        desconto = (Decimal(self.centavos) * percentual / 100).quantize(
            Decimal("1"), rounding=ROUND_HALF_UP
        )
        return Dinheiro(self.centavos - int(desconto))

    # ---- apresentação ---------------------------------------------------

    def __str__(self) -> str:
        inteiros, resto = divmod(self.centavos, 100)
        return f"R$ {inteiros:,}".replace(",", ".") + f",{resto:02d}"


ZERO = Dinheiro(0)
