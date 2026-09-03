"""
nand.py — A ÚNICA porta primitiva deste projeto.

Todo o computador de 4 bits construído aqui sai desta função e de mais nada.
Nenhum outro arquivo usa `and`, `or`, `not`, `+`, `-` ou `if` para calcular
valores lógicos: tudo é construído chamando `nand()`.

Por que NAND e não AND/OR/NOT?
  1. NAND é funcionalmente completa: qualquer função booleana pode ser escrita
     só com ela (a demonstração está em ../10-fundamentos.md).
  2. Em silício CMOS, NAND custa 4 transistores e é a porta mais rápida da
     biblioteca. Fábricas reais preferem NAND pelo mesmo motivo que este
     projeto prefere (ver ../12-do-transistor-a-porta.md).

O CONTADOR
----------
Cada chamada a nand() é contabilizada. Isso responde, com número medido e não
estimado, à pergunta que originou este curso: quantas portas lógicas são
precisas para fazer X?

Cuidado com a diferença, que é o ponto didático central deste arquivo:

  * CIRCUITO COMBINACIONAL (somador, mux, ULA): cada porta é avaliada uma vez
    por chamada, então "avaliações contadas" == "portas físicas gastas".

  * CIRCUITO SEQUENCIAL (latch, flip-flop): há realimentação, e o simulador
    precisa reavaliar o mesmo par de portas até o circuito estabilizar. Aí
    "avaliações contadas" > "portas físicas gastas". Um latch SR tem 2 portas
    físicas, mas pode gastar 6 avaliações para assentar. Isso não é defeito do
    simulador — é a versão discreta do que o circuito real faz de forma
    contínua, em picossegundos.
"""

# Contador global de avaliações da porta NAND.
_CONTADOR = {"nand": 0}


class ErroDeSinal(ValueError):
    """Levantado quando um sinal não é 0 nem 1. Em hardware real, isso seria
    uma tensão intermediária — o estado proibido, que aquece e não decide."""


def _valida(sinal, nome):
    if sinal not in (0, 1):
        raise ErroDeSinal(
            f"sinal {nome!r} vale {sinal!r}; um fio digital só aceita 0 ou 1"
        )


def nand(a, b):
    """A porta NÃO-E. Responde 0 somente quando as duas entradas são 1.

    Tabela-verdade:
        a b | saída
        0 0 |   1
        0 1 |   1
        1 0 |   1
        1 1 |   0
    """
    _valida(a, "a")
    _valida(b, "b")
    _CONTADOR["nand"] += 1
    # A única linha do projeto que decide algo sem usar nand().
    # É o átomo: abaixo dela só há transistor.
    return 0 if (a == 1 and b == 1) else 1


# ---------------------------------------------------------------------------
# Instrumentação
# ---------------------------------------------------------------------------

def zerar_contador():
    """Zera a contagem. Use antes de medir um circuito."""
    _CONTADOR["nand"] = 0


def total_nands():
    """Quantas avaliações de NAND aconteceram desde o último zeramento."""
    return _CONTADOR["nand"]


class Medidor:
    """Mede quantos NANDs um trecho de código gasta.

    Uso:
        with Medidor() as m:
            somador_completo(1, 1, 0)
        print(m.total)   # 9
    """

    def __init__(self):
        self.total = 0
        self._inicio = 0

    def __enter__(self):
        self._inicio = _CONTADOR["nand"]
        return self

    def __exit__(self, *_):
        self.total = _CONTADOR["nand"] - self._inicio
        return False


def custo(funcao, *args, **kwargs):
    """Roda a função e devolve (resultado, nands_gastos)."""
    with Medidor() as m:
        resultado = funcao(*args, **kwargs)
    return resultado, m.total
