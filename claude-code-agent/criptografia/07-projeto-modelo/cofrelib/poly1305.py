"""Poly1305 (RFC 8439, seção 2.5), em Python puro.

Poly1305 é um MAC de uso único (one-time authenticator): dada uma chave de
32 bytes que só pode ser usada para UMA mensagem, produz uma etiqueta (tag) de
16 bytes que prova que a mensagem não foi alterada.

Por que "de uso único" e não "de várias mensagens" como o HMAC?
Porque a segurança do Poly1305 vem de avaliar um polinômio cujos coeficientes
saem da mensagem, no ponto secreto `r`, módulo o primo 2^130 - 5, somando `s`
no fim. Com duas etiquetas produzidas pela mesma chave, o atacante monta um
sistema de equações e recupera `r` — e, com `r`, forja qualquer mensagem.
No AEAD do RFC 8439 isso se resolve derivando uma chave Poly1305 nova a cada
nonce (ver aead.py).
"""

P = (1 << 130) - 5  # primo: 2^130 - 5


def _clamp(r: int) -> int:
    """Zera 22 bits específicos de r (RFC 8439 §2.5).

    Não é superstição: os bits removidos são exatamente os que permitiriam que
    as somas parciais estourassem certos limites, o que quebraria as otimizações
    em aritmética de 26/32 bits que Bernstein projetou para a implementação
    rápida. É uma decisão de engenharia documentada, não uma escolha estética.
    """
    return r & 0x0FFFFFFC0FFFFFFC0FFFFFFC0FFFFFFF


def mac(chave: bytes, mensagem: bytes) -> bytes:
    """Calcula a etiqueta Poly1305 de 16 bytes."""
    if len(chave) != 32:
        raise ValueError("Poly1305 exige chave de 32 bytes")

    r = _clamp(int.from_bytes(chave[:16], "little"))
    s = int.from_bytes(chave[16:], "little")

    acumulador = 0
    for indice in range(0, len(mensagem), 16):
        bloco = mensagem[indice:indice + 16]
        # O byte 0x01 anexado ao fim do bloco marca onde o bloco termina.
        # Sem ele, "AB" e "AB\x00" produziriam o mesmo coeficiente.
        n = int.from_bytes(bloco + b"\x01", "little")
        acumulador = ((acumulador + n) * r) % P

    etiqueta = (acumulador + s) % (1 << 128)
    return etiqueta.to_bytes(16, "little")
