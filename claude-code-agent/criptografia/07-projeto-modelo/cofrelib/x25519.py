"""X25519 (RFC 7748), em Python puro.

X25519 é a troca de chaves Diffie-Hellman sobre a curva de Montgomery
Curve25519. Ela responde à pergunta que a criptografia simétrica não responde
sozinha: como duas pessoas que nunca se falaram combinam uma chave secreta
conversando por um canal que o adversário lê inteiro?

Ideia em uma linha: a função X25519(k, u) é fácil de calcular e difícil de
inverter, e comuta —
    X25519(a, X25519(b, G)) == X25519(b, X25519(a, G))
Cada lado publica sua parte pública; o segredo compartilhado nunca trafega.

AVISO HONESTO SOBRE ESTA IMPLEMENTAÇÃO
--------------------------------------
Este código é correto (bate com os vetores do RFC 7748) e é didático, mas NÃO
é de tempo constante. Os inteiros grandes do Python têm tamanho variável, o
laço de exponenciação modular de `pow` não protege contra medição de tempo, e
o coletor de lixo deixa cópias do segredo espalhadas pela memória. Em produção,
use libsodium / a biblioteca `cryptography` / o X25519 do seu sistema.
Ver 25-canais-laterais-e-implementacao.md.
"""

P = 2 ** 255 - 19       # o primo do corpo
A24 = 121665            # (A - 2) / 4, com A = 486662
TAMANHO = 32
BASE = b"\x09" + b"\x00" * 31   # ponto base: u = 9


class ChaveInvalida(Exception):
    """Chave pública de ordem pequena: o segredo resultante seria zero."""


def _clamp(escalar: bytes) -> int:
    """Ajusta os bits do escalar (RFC 7748 §5).

    Três decisões, cada uma com um motivo concreto:
      * zera os 3 bits baixos  -> o escalar vira múltiplo de 8, o que neutraliza
        ataques de subgrupo pequeno (o cofator da curva é 8);
      * zera o bit 255         -> mantém o escalar dentro da faixa;
      * liga o bit 254         -> fixa o comprimento do escalar, para que a
        escada de Montgomery execute sempre o mesmo número de passos.
    """
    bits = bytearray(escalar)
    bits[0] &= 248
    bits[31] &= 127
    bits[31] |= 64
    return int.from_bytes(bits, "little")


def _decodificar_u(u: bytes) -> int:
    """Lê a coordenada u, ignorando o bit mais significativo (RFC 7748 §5)."""
    bits = bytearray(u)
    bits[31] &= 127
    return int.from_bytes(bits, "little") % P


def _cswap(troca: int, x2: int, x3: int):
    """Troca condicional. Em C isso vira aritmética de máscara sem desvio."""
    return (x3, x2) if troca else (x2, x3)


def x25519(escalar: bytes, coordenada_u: bytes) -> bytes:
    """Multiplicação escalar na Curve25519 (escada de Montgomery)."""
    if len(escalar) != TAMANHO or len(coordenada_u) != TAMANHO:
        raise ValueError("X25519 opera sobre valores de exatamente 32 bytes")

    k = _clamp(escalar)
    u = _decodificar_u(coordenada_u)

    x1, x2, z2, x3, z3, trocado = u, 1, 0, u, 1, 0

    for t in range(254, -1, -1):
        bit = (k >> t) & 1
        trocado ^= bit
        x2, x3 = _cswap(trocado, x2, x3)
        z2, z3 = _cswap(trocado, z2, z3)
        trocado = bit

        a = (x2 + z2) % P
        aa = (a * a) % P
        b = (x2 - z2) % P
        bb = (b * b) % P
        e = (aa - bb) % P
        c = (x3 + z3) % P
        d = (x3 - z3) % P
        da = (d * a) % P
        cb = (c * b) % P
        x3 = pow((da + cb) % P, 2, P)
        z3 = (x1 * pow((da - cb) % P, 2, P)) % P
        x2 = (aa * bb) % P
        z2 = (e * ((aa + A24 * e) % P)) % P

    x2, x3 = _cswap(trocado, x2, x3)
    z2, z3 = _cswap(trocado, z2, z3)

    # Divisão no corpo = multiplicar pelo inverso. Pelo pequeno teorema de
    # Fermat, z^(P-2) == z^-1 (mod P) quando P é primo.
    resultado = (x2 * pow(z2, P - 2, P)) % P
    return resultado.to_bytes(TAMANHO, "little")


def chave_publica(chave_privada: bytes) -> bytes:
    """Deriva a chave pública correspondente a uma chave privada."""
    return x25519(chave_privada, BASE)


def segredo_compartilhado(chave_privada: bytes, publica_do_outro: bytes) -> bytes:
    """Diffie-Hellman propriamente dito, com a verificação obrigatória.

    O RFC 7748 §6.1 manda checar se o resultado é todo zero: isso acontece
    quando a chave pública recebida é um ponto de ordem pequena, um jeito
    barato de o outro lado forçar um "segredo" que ele já conhece.
    """
    segredo = x25519(chave_privada, publica_do_outro)
    if segredo == bytes(TAMANHO):
        raise ChaveInvalida("chave pública de ordem pequena; troca abortada")
    return segredo
