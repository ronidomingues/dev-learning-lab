"""Interoperabilidade com o OpenSSL, via biblioteca `cryptography`.

Passar nos vetores do RFC prova que a implementação está certa nos casos
publicados. Este arquivo prova algo complementar e igualmente importante:
que ela produz bytes IDÊNTICOS aos de uma implementação de produção, para
entradas aleatórias — inclusive nos tamanhos que não são múltiplos de 64.

Se a biblioteca `cryptography` não estiver instalada, os testes são pulados;
o projeto continua funcionando sem nenhuma dependência externa.
"""

import os
import unittest

try:
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
    from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
    TEM_CRYPTOGRAPHY = True
except ImportError:                       # pragma: no cover
    TEM_CRYPTOGRAPHY = False

from cofrelib import aead, x25519


@unittest.skipUnless(TEM_CRYPTOGRAPHY, "biblioteca `cryptography` não instalada")
class TesteInteroperabilidade(unittest.TestCase):
    def test_aead_produz_os_mesmos_bytes(self):
        for tamanho in (0, 1, 63, 64, 65, 1000):
            with self.subTest(tamanho=tamanho):
                chave, nonce = os.urandom(32), os.urandom(12)
                claro, aad = os.urandom(tamanho), os.urandom(37)
                self.assertEqual(aead.cifrar(chave, nonce, claro, aad),
                                 ChaCha20Poly1305(chave).encrypt(nonce, claro, aad))

    def test_openssl_decifra_o_que_produzimos(self):
        chave, nonce = os.urandom(32), os.urandom(12)
        claro, aad = b"interoperar e o teste que importa", b"cabecalho"
        nosso = aead.cifrar(chave, nonce, claro, aad)
        self.assertEqual(ChaCha20Poly1305(chave).decrypt(nonce, nosso, aad), claro)

    def test_deciframos_o_que_o_openssl_produz(self):
        chave, nonce = os.urandom(32), os.urandom(12)
        claro, aad = b"e nos dois sentidos", b"cabecalho"
        deles = ChaCha20Poly1305(chave).encrypt(nonce, claro, aad)
        self.assertEqual(aead.decifrar(chave, nonce, deles, aad), claro)

    def test_x25519_bate_com_o_openssl(self):
        minha_privada = os.urandom(32)
        referencia = X25519PrivateKey.from_private_bytes(minha_privada)
        publica_referencia = referencia.public_key().public_bytes(
            serialization.Encoding.Raw, serialization.PublicFormat.Raw)
        self.assertEqual(x25519.chave_publica(minha_privada), publica_referencia)

        outra = X25519PrivateKey.generate()
        publica_outra = outra.public_key().public_bytes(
            serialization.Encoding.Raw, serialization.PublicFormat.Raw)
        self.assertEqual(x25519.segredo_compartilhado(minha_privada, publica_outra),
                         outra.exchange(referencia.public_key()))


if __name__ == "__main__":
    unittest.main()
