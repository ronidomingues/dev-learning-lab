"""Testes do formato de arquivo e da linha de comando.

Aqui não há vetor oficial para comparar: o formato é nosso. O que se testa é
o comportamento que um usuário real depende — inclusive, e principalmente, o
comportamento quando algo dá errado.
"""

import os
import subprocess
import sys
import tempfile
import unittest

from cofrelib import aead, chaves, cli, formato, x25519

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_N_RAPIDO = 12  # 2^12 em vez de 2^15: testes não precisam da lentidão real


class TesteFormatoSenha(unittest.TestCase):
    def test_ida_e_volta(self):
        dados = b"o codigo do cofre e 4 8 15 16 23 42"
        arquivo = formato.cifrar_com_senha(dados, "senha correta", log_n=LOG_N_RAPIDO)
        self.assertEqual(formato.decifrar_com_senha(arquivo, "senha correta"), dados)

    def test_cabecalho_tem_assinatura_versao_e_modo(self):
        arquivo = formato.cifrar_com_senha(b"x", "s", log_n=LOG_N_RAPIDO)
        self.assertEqual(arquivo[:6], b"COFRE1")
        self.assertEqual(arquivo[6], formato.VERSAO)
        self.assertEqual(arquivo[7], formato.MODO_SENHA)

    def test_senha_errada_nao_decifra(self):
        arquivo = formato.cifrar_com_senha(b"x", "certa", log_n=LOG_N_RAPIDO)
        with self.assertRaises(aead.ErroDeAutenticacao):
            formato.decifrar_com_senha(arquivo, "errada")

    def test_dois_arquivos_da_mesma_senha_sao_diferentes(self):
        """Sal e nonce aleatórios: nada de criptograma determinístico."""
        a = formato.cifrar_com_senha(b"mesmo texto", "mesma senha", log_n=LOG_N_RAPIDO)
        b = formato.cifrar_com_senha(b"mesmo texto", "mesma senha", log_n=LOG_N_RAPIDO)
        self.assertNotEqual(a, b)

    def test_rebaixar_o_custo_do_scrypt_no_cabecalho_e_detectado(self):
        """O ataque que o AAD existe para impedir."""
        arquivo = bytearray(formato.cifrar_com_senha(b"x", "s", log_n=14))
        arquivo[8] = 12                       # de 2^14 para 2^12
        with self.assertRaises(aead.ErroDeAutenticacao):
            formato.decifrar_com_senha(bytes(arquivo), "s")

    def test_log_n_absurdo_e_recusado_antes_de_alocar_memoria(self):
        arquivo = bytearray(formato.cifrar_com_senha(b"x", "s", log_n=LOG_N_RAPIDO))
        arquivo[8] = 40                       # 2^40 blocos = pedido de DoS
        with self.assertRaises(formato.ArquivoInvalido):
            formato.decifrar_com_senha(bytes(arquivo), "s")

    def test_arquivo_alheio_e_recusado_com_mensagem_clara(self):
        with self.assertRaises(formato.ArquivoInvalido):
            formato.decifrar_com_senha(b"%PDF-1.7 blah blah", "s")

    def test_versao_futura_e_recusada(self):
        arquivo = bytearray(formato.cifrar_com_senha(b"x", "s", log_n=LOG_N_RAPIDO))
        arquivo[6] = 99
        with self.assertRaises(formato.ArquivoInvalido):
            formato.decifrar_com_senha(bytes(arquivo), "s")

    def test_arquivo_truncado_e_recusado(self):
        arquivo = formato.cifrar_com_senha(b"x" * 100, "s", log_n=LOG_N_RAPIDO)
        with self.assertRaises((formato.ArquivoInvalido, aead.ErroDeAutenticacao)):
            formato.decifrar_com_senha(arquivo[:-10], "s")


class TesteFormatoChavePublica(unittest.TestCase):
    def setUp(self):
        self.privada = chaves.gerar_privada()
        self.publica = x25519.chave_publica(self.privada)

    def test_ida_e_volta(self):
        dados = b"mensagem para o dono da chave"
        arquivo = formato.cifrar_para_chave(dados, self.publica)
        self.assertEqual(formato.decifrar_com_chave(arquivo, self.privada), dados)

    def test_outra_chave_privada_nao_abre(self):
        arquivo = formato.cifrar_para_chave(b"x", self.publica)
        with self.assertRaises(aead.ErroDeAutenticacao):
            formato.decifrar_com_chave(arquivo, chaves.gerar_privada())

    def test_a_chave_efemera_muda_a_cada_arquivo(self):
        a = formato.cifrar_para_chave(b"x", self.publica)
        b = formato.cifrar_para_chave(b"x", self.publica)
        self.assertNotEqual(a[8:40], b[8:40])   # nonce zero só é seguro por isso

    def test_modo_trocado_da_erro_util(self):
        arquivo = formato.cifrar_para_chave(b"x", self.publica)
        with self.assertRaises(formato.ArquivoInvalido):
            formato.decifrar_com_senha(arquivo, "s")


class TesteChaves(unittest.TestCase):
    def test_codificar_e_decodificar(self):
        privada = chaves.gerar_privada()
        publica = x25519.chave_publica(privada)
        self.assertEqual(chaves.decodificar_privada(chaves.codificar_privada(privada)),
                         privada)
        self.assertEqual(chaves.decodificar_publica(chaves.codificar_publica(publica)),
                         publica)

    def test_arquivo_de_chave_nasce_com_permissao_600(self):
        with tempfile.TemporaryDirectory() as pasta:
            caminho = os.path.join(pasta, "k")
            privada = chaves.gerar_privada()
            chaves.gravar_privada(caminho, privada, x25519.chave_publica(privada))
            self.assertEqual(os.stat(caminho).st_mode & 0o777, 0o600)
            self.assertEqual(chaves.ler_privada(caminho), privada)

    def test_permissao_frouxa_e_recusada(self):
        with tempfile.TemporaryDirectory() as pasta:
            caminho = os.path.join(pasta, "k")
            privada = chaves.gerar_privada()
            chaves.gravar_privada(caminho, privada, x25519.chave_publica(privada))
            os.chmod(caminho, 0o644)
            with self.assertRaises(chaves.ChaveMalFormada):
                chaves.ler_privada(caminho)

    def test_prefixo_errado_e_recusado(self):
        with self.assertRaises(chaves.ChaveMalFormada):
            chaves.decodificar_publica("ssh-ed25519 AAAA...")


class TesteCLI(unittest.TestCase):
    """Roda a CLI como um processo de verdade, igual ao usuário faria."""

    def executar(self, *args, senha=None, esperar=0):
        ambiente = dict(os.environ)
        if senha is not None:
            ambiente["COFRE_SENHA"] = senha
        processo = subprocess.run(
            [sys.executable, "cofre.py", *args],
            cwd=RAIZ, env=ambiente, capture_output=True, text=True)
        self.assertEqual(processo.returncode, esperar,
                         f"saída: {processo.stdout}{processo.stderr}")
        return processo

    def test_autoteste_passa(self):
        saida = self.executar("autoteste").stdout
        self.assertIn("autoteste: tudo certo", saida)

    def test_ciclo_completo_com_senha(self):
        with tempfile.TemporaryDirectory() as pasta:
            claro = os.path.join(pasta, "diario.txt")
            cifrado = os.path.join(pasta, "diario.cofre")
            recuperado = os.path.join(pasta, "volta.txt")
            with open(claro, "wb") as arquivo:
                arquivo.write(b"terca-feira: aprendi o que e um nonce\n")

            self.executar("cifrar", "--entrada", claro, "--saida", cifrado,
                          "--log-n", str(LOG_N_RAPIDO), senha="abacaxi-com-hortela")
            with open(cifrado, "rb") as arquivo:
                self.assertEqual(arquivo.read(6), b"COFRE1")

            self.executar("decifrar", "--entrada", cifrado, "--saida", recuperado,
                          senha="abacaxi-com-hortela")
            with open(recuperado, "rb") as arquivo:
                self.assertEqual(arquivo.read(), b"terca-feira: aprendi o que e um nonce\n")

    def test_senha_errada_sai_com_codigo_2(self):
        with tempfile.TemporaryDirectory() as pasta:
            claro = os.path.join(pasta, "a.txt")
            cifrado = os.path.join(pasta, "a.cofre")
            with open(claro, "wb") as arquivo:
                arquivo.write(b"conteudo")
            self.executar("cifrar", "--entrada", claro, "--saida", cifrado,
                          "--log-n", str(LOG_N_RAPIDO), senha="certa")
            self.executar("decifrar", "--entrada", cifrado, "--saida",
                          os.path.join(pasta, "x"), senha="errada", esperar=2)

    def test_ciclo_completo_com_chave_publica(self):
        with tempfile.TemporaryDirectory() as pasta:
            chave = os.path.join(pasta, "minha.chave")
            saida = self.executar("chave-nova", "--saida", chave).stdout
            publica = [l.split(": ", 1)[1] for l in saida.splitlines()
                       if l.startswith("chave pública")][0]

            claro = os.path.join(pasta, "carta.txt")
            selado = os.path.join(pasta, "carta.cofre")
            aberto = os.path.join(pasta, "carta-aberta.txt")
            with open(claro, "wb") as arquivo:
                arquivo.write(b"nem quem selou consegue reabrir\n")

            self.executar("selar", "--para", publica, "--entrada", claro,
                          "--saida", selado)
            self.executar("abrir", "--chave", chave, "--entrada", selado,
                          "--saida", aberto)
            with open(aberto, "rb") as arquivo:
                self.assertEqual(arquivo.read(), b"nem quem selou consegue reabrir\n")

    def test_nao_sobrescreve_sem_forcar(self):
        with tempfile.TemporaryDirectory() as pasta:
            claro = os.path.join(pasta, "a.txt")
            existente = os.path.join(pasta, "ocupado.cofre")
            for caminho, conteudo in ((claro, b"x"), (existente, b"nao me apague")):
                with open(caminho, "wb") as arquivo:
                    arquivo.write(conteudo)
            processo = subprocess.run(
                [sys.executable, "cofre.py", "cifrar", "--entrada", claro,
                 "--saida", existente, "--log-n", str(LOG_N_RAPIDO)],
                cwd=RAIZ, env={**os.environ, "COFRE_SENHA": "s"},
                capture_output=True, text=True)
            self.assertNotEqual(processo.returncode, 0)
            with open(existente, "rb") as arquivo:
                self.assertEqual(arquivo.read(), b"nao me apague")

    def test_arquivo_inexistente_sai_com_codigo_4(self):
        self.executar("decifrar", "--entrada", "/nao/existe.cofre",
                      "--saida", "-", senha="s", esperar=4)


if __name__ == "__main__":
    unittest.main()
