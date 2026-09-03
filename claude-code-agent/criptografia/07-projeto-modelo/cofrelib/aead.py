"""AEAD_CHACHA20_POLY1305 (RFC 8439, seção 2.8), em Python puro.

AEAD = Authenticated Encryption with Associated Data
     = cifragem autenticada com dados associados.

Três garantias em uma primitiva só:

1. Sigilo do texto claro            -> vem do ChaCha20.
2. Integridade do texto claro       -> vem do Poly1305 sobre o criptograma.
3. Integridade dos dados associados -> o AAD é autenticado mas NÃO é cifrado.

O AAD serve para cabeçalhos que precisam ficar legíveis (número de versão,
identificador de algoritmo, endereço de destino) mas não podem ser adulterados.
No formato deste projeto, o cabeçalho inteiro do arquivo entra como AAD — é o
que impede um atacante de trocar "modo senha" por "modo chave pública" ou de
reduzir o custo do scrypt de N=2^15 para N=2^1 num arquivo já cifrado.

Ordem correta: Encrypt-then-MAC. Cifra-se primeiro, autentica-se o criptograma.
A ordem inversa (MAC-then-Encrypt, usada no TLS até a versão 1.2) obriga o
receptor a decifrar dados não autenticados, e foi a raiz de toda a família de
ataques Lucky13/POODLE/padding oracle.
"""

import hmac

from . import chacha20, poly1305


class ErroDeAutenticacao(Exception):
    """Etiqueta inválida: chave errada, nonce errado ou dado adulterado.

    A mensagem é deliberadamente genérica. Dizer ao atacante QUAL das três
    causas ocorreu é entregar um oráculo de graça.
    """


def _chave_poly1305(chave: bytes, nonce: bytes) -> bytes:
    """Deriva a chave Poly1305 de uso único (RFC 8439 §2.6).

    Usa o bloco 0 do ChaCha20 com a mesma chave e o mesmo nonce; os dados
    começam no bloco 1. Como o nonce muda a cada mensagem, a chave do MAC muda
    junto — que é exatamente o que o Poly1305 exige.
    """
    return chacha20.bloco(chave, 0, nonce)[:32]


def _preenchimento16(dados: bytes) -> bytes:
    """Zeros até completar múltiplo de 16 bytes."""
    resto = len(dados) % 16
    return b"\x00" * (16 - resto) if resto else b""


def _entrada_do_mac(aad: bytes, criptograma: bytes) -> bytes:
    """Monta o buffer autenticado (RFC 8439 §2.8.1).

    aad || pad16(aad) || ct || pad16(ct) || len(aad) || len(ct)

    Os dois comprimentos de 8 bytes no fim não são enfeite: sem eles, mover
    bytes da fronteira entre AAD e criptograma produziria a mesma etiqueta —
    uma ambiguidade de canonicalização, o mesmo tipo de bug que já quebrou
    protocolos reais.
    """
    return (
        aad + _preenchimento16(aad)
        + criptograma + _preenchimento16(criptograma)
        + len(aad).to_bytes(8, "little")
        + len(criptograma).to_bytes(8, "little")
    )


def cifrar(chave: bytes, nonce: bytes, texto_claro: bytes, aad: bytes = b"") -> bytes:
    """Devolve criptograma || etiqueta (16 bytes no fim)."""
    if len(chave) != 32:
        raise ValueError("a chave do AEAD precisa ter 32 bytes")
    if len(nonce) != 12:
        raise ValueError("o nonce do AEAD precisa ter 12 bytes")

    chave_mac = _chave_poly1305(chave, nonce)
    criptograma = chacha20.cifrar(chave, 1, nonce, texto_claro)
    etiqueta = poly1305.mac(chave_mac, _entrada_do_mac(aad, criptograma))
    return criptograma + etiqueta


def decifrar(chave: bytes, nonce: bytes, criptograma_com_etiqueta: bytes,
             aad: bytes = b"") -> bytes:
    """Verifica a etiqueta e só então decifra. Levanta ErroDeAutenticacao."""
    if len(criptograma_com_etiqueta) < 16:
        raise ErroDeAutenticacao("dados curtos demais para conter uma etiqueta")

    criptograma = criptograma_com_etiqueta[:-16]
    etiqueta_recebida = criptograma_com_etiqueta[-16:]

    chave_mac = _chave_poly1305(chave, nonce)
    etiqueta_esperada = poly1305.mac(chave_mac, _entrada_do_mac(aad, criptograma))

    # hmac.compare_digest compara em tempo constante. Um `==` comum sai no
    # primeiro byte diferente, e essa diferença de microssegundos é medível
    # pela rede: com ela um atacante forja a etiqueta byte a byte, em ~16*256
    # tentativas em vez de 2^128.
    if not hmac.compare_digest(etiqueta_esperada, etiqueta_recebida):
        raise ErroDeAutenticacao("etiqueta de autenticação inválida")

    return chacha20.cifrar(chave, 1, nonce, criptograma)
