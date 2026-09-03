"""Vetores de teste oficiais dos RFCs.

Este é o arquivo mais importante do projeto. Criptografia "que parece
funcionar" é o modo normal de falhar: um erro de rotação, um endianness
invertido ou um contador começando em 0 em vez de 1 produzem um sistema que
cifra e decifra perfeitamente consigo mesmo — e é incompatível com todo o
resto do mundo, além de possivelmente inseguro.

A única defesa barata é conferir cada primitiva contra os valores publicados
no RFC. Todos os hexadecimais abaixo foram copiados dos textos oficiais em
www.rfc-editor.org.
"""

import unittest

from cofrelib import aead, chacha20, kdf, poly1305, x25519


class TesteChaCha20(unittest.TestCase):
    def test_quarter_round_rfc8439_2_1_1(self):
        estado = [0x11111111, 0x01020304, 0x9B8D6F43, 0x01234567]
        chacha20.quarter_round(estado, 0, 1, 2, 3)
        self.assertEqual(estado, [0xEA2A92F4, 0xCB1CF8CE, 0x4581472E, 0x5881C4BB])

    def test_bloco_rfc8439_2_3_2(self):
        chave = bytes(range(32))
        nonce = bytes.fromhex("000000090000004a00000000")
        esperado = (
            "10f1e7e4d13b5915500fdd1fa32071c4"
            "c7d1f4c733c068030422aa9ac3d46c4e"
            "d2826446079faa0914c2d705d98b02a2"
            "b5129cd1de164eb9cbd083e8a2503c4e")
        self.assertEqual(chacha20.bloco(chave, 1, nonce).hex(), esperado)

    def test_cifragem_rfc8439_2_4_2(self):
        chave = bytes(range(32))
        nonce = bytes.fromhex("000000000000004a00000000")
        claro = (b"Ladies and Gentlemen of the class of '99: If I could offer "
                 b"you only one tip for the future, sunscreen would be it.")
        cifrado = chacha20.cifrar(chave, 1, nonce, claro)
        self.assertTrue(cifrado.hex().startswith("6e2e359a2568f98041ba0728dd0d6981"))
        self.assertEqual(chacha20.cifrar(chave, 1, nonce, cifrado), claro)

    def test_nonce_e_chave_de_tamanho_errado_sao_recusados(self):
        with self.assertRaises(ValueError):
            chacha20.bloco(b"curta", 1, bytes(12))
        with self.assertRaises(ValueError):
            chacha20.bloco(bytes(32), 1, b"nonce-curto")


class TestePoly1305(unittest.TestCase):
    def test_mac_rfc8439_2_5_2(self):
        chave = bytes.fromhex("85d6be7857556d337f4452fe42d506a8"
                              "0103808afb0db2fd4abff6af4149f51b")
        etiqueta = poly1305.mac(chave, b"Cryptographic Forum Research Group")
        self.assertEqual(etiqueta.hex(), "a8061dc1305136c6c22b8baf0c0127a9")

    def test_mensagem_vazia_rfc8439_a3_1(self):
        self.assertEqual(poly1305.mac(bytes(32), bytes(64)).hex(), "0" * 32)


class TesteAEAD(unittest.TestCase):
    CHAVE = bytes(range(0x80, 0xA0))
    NONCE = bytes.fromhex("070000004041424344454647")
    AAD = bytes.fromhex("50515253c0c1c2c3c4c5c6c7")
    CLARO = (b"Ladies and Gentlemen of the class of '99: If I could offer you "
             b"only one tip for the future, sunscreen would be it.")
    ETIQUETA = "1ae10b594f09e26a7e902ecbd0600691"
    CT_INICIO = "d31a8d34648e60db7b86afbc53ef7ec2"

    def test_cifragem_rfc8439_2_8_2(self):
        saida = aead.cifrar(self.CHAVE, self.NONCE, self.CLARO, self.AAD)
        self.assertTrue(saida.hex().startswith(self.CT_INICIO))
        self.assertEqual(saida[-16:].hex(), self.ETIQUETA)

    def test_decifragem_devolve_o_original(self):
        saida = aead.cifrar(self.CHAVE, self.NONCE, self.CLARO, self.AAD)
        self.assertEqual(aead.decifrar(self.CHAVE, self.NONCE, saida, self.AAD), self.CLARO)

    def test_bit_invertido_no_criptograma_e_detectado(self):
        saida = bytearray(aead.cifrar(self.CHAVE, self.NONCE, self.CLARO, self.AAD))
        saida[0] ^= 0x01
        with self.assertRaises(aead.ErroDeAutenticacao):
            aead.decifrar(self.CHAVE, self.NONCE, bytes(saida), self.AAD)

    def test_aad_alterado_e_detectado(self):
        saida = aead.cifrar(self.CHAVE, self.NONCE, self.CLARO, self.AAD)
        with self.assertRaises(aead.ErroDeAutenticacao):
            aead.decifrar(self.CHAVE, self.NONCE, saida, self.AAD + b"x")

    def test_reuso_de_nonce_vaza_o_xor_das_mensagens(self):
        """Demonstração do pior erro operacional possível com cifra de fluxo."""
        m1 = b"transferir 10 reais para a alice"
        m2 = b"transferir 99 reais para o mallo"
        c1 = aead.cifrar(self.CHAVE, self.NONCE, m1)[:-16]
        c2 = aead.cifrar(self.CHAVE, self.NONCE, m2)[:-16]
        xor_criptogramas = bytes(a ^ b for a, b in zip(c1, c2))
        xor_claros = bytes(a ^ b for a, b in zip(m1, m2))
        self.assertEqual(xor_criptogramas, xor_claros)  # a chave sumiu da equação


class TesteX25519(unittest.TestCase):
    def test_vetor_rfc7748_5_2_primeiro(self):
        escalar = bytes.fromhex("a546e36bf0527c9d3b16154b82465edd"
                                "62144c0ac1fc5a18506a2244ba449ac4")
        u = bytes.fromhex("e6db6867583030db3594c1a424b15f7c"
                          "726624ec26b3353b10a903a6d0ab1c4c")
        self.assertEqual(
            x25519.x25519(escalar, u).hex(),
            "c3da55379de9c6908e94ea4df28d084f32eccf03491c71f754b4075577a28552")

    def test_vetor_rfc7748_5_2_segundo(self):
        escalar = bytes.fromhex("4b66e9d4d1b4673c5ad22691957d6af5"
                                "c11b6421e0ea01d42ca4169e7918ba0d")
        u = bytes.fromhex("e5210f12786811d3f4b7959d0538ae2c"
                          "31dbe7106fc03c3efc4cd549c715a493")
        self.assertEqual(
            x25519.x25519(escalar, u).hex(),
            "95cbde9476e8907d7aade45cb4b873f88b595a68799fa152e6f8f7647aac7957")

    def test_troca_de_chaves_rfc7748_6_1(self):
        a = bytes.fromhex("77076d0a7318a57d3c16c17251b26645"
                          "df4c2f87ebc0992ab177fba51db92c2a")
        b = bytes.fromhex("5dab087e624a8a4b79e17f8b83800ee6"
                          "6f3bb1292618b6fd1c2f8b27ff88e0eb")
        pub_a = x25519.chave_publica(a)
        pub_b = x25519.chave_publica(b)
        self.assertEqual(pub_a.hex(),
                         "8520f0098930a754748b7ddcb43ef75a0dbf3a0d26381af4eba4a98eaa9b4e6a")
        self.assertEqual(pub_b.hex(),
                         "de9edb7d7b7dc1b4d35b61c2ece435373f8343c85b78674dadfc7e146f882b4f")
        segredo = "4a5d9d5ba4ce2de1728e3bf480350f25e07e21c947d19e3376f09b3c1e161742"
        self.assertEqual(x25519.segredo_compartilhado(a, pub_b).hex(), segredo)
        self.assertEqual(x25519.segredo_compartilhado(b, pub_a).hex(), segredo)

    def test_ponto_de_ordem_pequena_e_recusado(self):
        with self.assertRaises(x25519.ChaveInvalida):
            x25519.segredo_compartilhado(bytes(range(32)), bytes(32))


class TesteKDF(unittest.TestCase):
    def test_hkdf_rfc5869_caso1(self):
        ikm = bytes.fromhex("0b" * 22)
        sal = bytes.fromhex("000102030405060708090a0b0c")
        info = bytes.fromhex("f0f1f2f3f4f5f6f7f8f9")
        self.assertEqual(
            kdf.hkdf_extract(sal, ikm).hex(),
            "077709362c2e32df0ddc3f0dc47bba6390b6c73bb50f9c3122ec844ad7c2b3e5")
        self.assertEqual(
            kdf.hkdf(ikm, sal, info, 42).hex(),
            "3cb25f25faacd57a90434f64d0362f2a2d2d0a90cf1a5a4c5db02d56"
            "ecc4c5bf34007208d5b887185865")

    def test_info_diferente_gera_chave_diferente(self):
        segredo = b"segredo de alta entropia" * 2
        ida = kdf.hkdf(segredo, b"sal", b"ida")
        volta = kdf.hkdf(segredo, b"sal", b"volta")
        self.assertNotEqual(ida, volta)

    def test_scrypt_rfc7914_vetor2(self):
        import hashlib
        derivada = hashlib.scrypt(b"password", salt=b"NaCl", n=1024, r=8, p=16,
                                  maxmem=kdf.SCRYPT_MAXMEM, dklen=64)
        self.assertTrue(derivada.hex().startswith("fdbabe1c9d3472007856e7190d01e9fe"))

    def test_sal_curto_e_recusado(self):
        with self.assertRaises(ValueError):
            kdf.derivar_de_senha("abc", b"sal-curto")


if __name__ == "__main__":
    unittest.main()
