from . import criterios, escopo, pacotes, segredos, tamanho

REGRAS = [escopo, tamanho, segredos, pacotes, criterios]

__all__ = ["REGRAS", "escopo", "tamanho", "segredos", "pacotes", "criterios"]
