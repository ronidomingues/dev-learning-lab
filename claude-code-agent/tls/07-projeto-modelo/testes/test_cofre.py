#!/usr/bin/env python3
"""
Testes do cofre-tls.

Metade deles são ATAQUES: certificado de outra CA, certificado revogado,
certificado vencido, cliente sem certificado, servidor com nome errado,
cliente tentando ação fora da sua permissão. Um teste de TLS que só verifica
o caminho feliz não testou nada — o valor do TLS está exatamente nos casos
em que ele deve DIZER NÃO.

Rode com:  ./executar-testes.sh     (ou: python3 -m unittest discover -s testes -v)
"""
from __future__ import annotations

import json
import os
import ssl
import subprocess
import sys
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
PKI = BASE / "pki"
sys.path.insert(0, str(BASE))

import servidor as app  # noqa: E402


PORTA = int(os.environ.get("COFRE_PORTA_TESTE", "18443"))
URL = f"https://localhost:{PORTA}"


def openssl(*args: str) -> str:
    return subprocess.run(["openssl", *args], capture_output=True, text=True).stdout


def ctx_cliente(identidade: str | None, ca: str = "ca.crt") -> ssl.SSLContext:
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ctx.minimum_version = ssl.TLSVersion.TLSv1_2
    ctx.load_verify_locations(str(PKI / ca))
    if identidade:
        ctx.load_cert_chain(str(PKI / f"{identidade}.crt"), str(PKI / f"{identidade}.key"))
    return ctx


def chamar(ctx, caminho, metodo="GET", corpo=None, url=URL, bruto=None):
    dados = bruto if bruto is not None else (json.dumps(corpo).encode() if corpo is not None else None)
    req = urllib.request.Request(url + caminho, data=dados, method=metodo)
    if dados:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=10) as r:
            texto = r.read().decode()
            return r.status, json.loads(texto) if texto.strip() else {}
    except urllib.error.HTTPError as e:
        texto = e.read().decode()
        return e.code, json.loads(texto) if texto.strip() else {}


# ─────────────────────────────────────────────────────────────────────────────
class ServidorDeTeste:
    """Sobe o servidor real, em thread, ligado em 0.0.0.0 (para o teste de nome)."""

    def __enter__(self):
        from http.server import ThreadingHTTPServer
        self.srv = ThreadingHTTPServer(("0.0.0.0", PORTA), app.Cofre)
        self.srv.socket = app.montar_contexto().wrap_socket(self.srv.socket, server_side=True)
        self.t = threading.Thread(target=self.srv.serve_forever, daemon=True)
        self.t.start()
        return self

    def __exit__(self, *a):
        self.srv.shutdown()
        self.srv.server_close()


_servidor: ServidorDeTeste | None = None


def setUpModule():
    global _servidor
    if not (PKI / "ca.crt").exists():
        raise unittest.SkipTest("PKI ausente — rode ./criar-pki.sh")
    _servidor = ServidorDeTeste().__enter__()


def tearDownModule():
    if _servidor:
        _servidor.__exit__()


# ═══════════════════════════════ 1. A PKI ════════════════════════════════════
class TestePKI(unittest.TestCase):

    def test_01_arquivos_existem(self):
        for nome in ("ca.crt", "ca.key", "ca.crl", "ca-com-crl.pem",
                     "servidor.crt", "admin.crt", "leitor.crt",
                     "escritor.crt", "banido.crt", "vencido.crt", "intruso.crt"):
            self.assertTrue((PKI / nome).exists(), f"faltando {nome}")

    def test_02_ca_e_uma_ca_de_verdade(self):
        t = openssl("x509", "-in", str(PKI / "ca.crt"), "-noout", "-text")
        self.assertIn("CA:TRUE", t)
        self.assertIn("pathlen:0", t)
        self.assertIn("Certificate Sign", t)

    def test_03_servidor_tem_san(self):
        t = openssl("x509", "-in", str(PKI / "servidor.crt"), "-noout", "-ext", "subjectAltName")
        self.assertIn("DNS:localhost", t)
        self.assertIn("IP Address:127.0.0.1", t)

    def test_04_servidor_so_serve_para_servidor(self):
        t = openssl("x509", "-in", str(PKI / "servidor.crt"), "-noout", "-ext", "extendedKeyUsage")
        self.assertIn("TLS Web Server Authentication", t)
        self.assertNotIn("TLS Web Client Authentication", t)

    def test_05_cliente_so_serve_para_cliente(self):
        t = openssl("x509", "-in", str(PKI / "admin.crt"), "-noout", "-ext", "extendedKeyUsage")
        self.assertIn("TLS Web Client Authentication", t)
        self.assertNotIn("TLS Web Server Authentication", t)

    def test_06_chave_bate_com_o_certificado(self):
        pub_cert = openssl("x509", "-in", str(PKI / "servidor.crt"), "-noout", "-pubkey")
        pub_chave = openssl("pkey", "-in", str(PKI / "servidor.key"), "-pubout")
        self.assertEqual(pub_cert.strip(), pub_chave.strip())

    def test_07_chaves_privadas_com_permissao_restrita(self):
        for nome in ("ca.key", "servidor.key", "admin.key"):
            modo = (PKI / nome).stat().st_mode & 0o077
            self.assertEqual(modo, 0, f"{nome} está legível por outros")

    def test_08_crl_contem_o_banido(self):
        serie = openssl("x509", "-in", str(PKI / "banido.crt"), "-noout", "-serial").split("=")[1].strip()
        crl = openssl("crl", "-in", str(PKI / "ca.crl"), "-noout", "-text")
        self.assertIn(serie, crl)

    def test_09_base_marca_revogado_e_expirado(self):
        linhas = (PKI / "index.txt").read_text().splitlines()
        estados = {l.split("\t")[5].split("CN=")[-1]: l.split("\t")[0] for l in linhas}
        self.assertEqual(estados["banido"], "R")
        self.assertEqual(estados["vencido"], "E")

    def test_10_vencido_realmente_venceu(self):
        r = subprocess.run(["openssl", "x509", "-in", str(PKI / "vencido.crt"),
                            "-noout", "-checkend", "0"], capture_output=True)
        self.assertNotEqual(r.returncode, 0, "o certificado 'vencido' ainda é válido")


# ═══════════════════════ 2. Caminho feliz e autorização ══════════════════════
class TesteAutorizacao(unittest.TestCase):

    def test_20_admin_ve_saude_e_a_propria_identidade(self):
        cod, res = chamar(ctx_cliente("admin"), "/saude")
        self.assertEqual(cod, 200)
        self.assertEqual(res["voce"], "admin")

    def test_21_leitor_pode_listar(self):
        cod, res = chamar(ctx_cliente("leitor"), "/notas")
        self.assertEqual(cod, 200)
        self.assertIn("notas", res)

    def test_22_escritor_pode_criar(self):
        cod, res = chamar(ctx_cliente("escritor"), "/notas", "POST", {"texto": "oi"})
        self.assertEqual(cod, 201)
        self.assertEqual(res["autor"], "escritor")

    def test_23_leitor_NAO_pode_criar(self):
        cod, res = chamar(ctx_cliente("leitor"), "/notas", "POST", {"texto": "x"})
        self.assertEqual(cod, 403)
        self.assertIn("leitor", res["erro"])

    def test_24_escritor_NAO_pode_apagar(self):
        cod, _ = chamar(ctx_cliente("escritor"), "/notas/1", "DELETE")
        self.assertEqual(cod, 403)

    def test_25_admin_pode_apagar(self):
        _, nota = chamar(ctx_cliente("escritor"), "/notas", "POST", {"texto": "some"})
        cod, _ = chamar(ctx_cliente("admin"), f"/notas/{nota['id']}", "DELETE")
        self.assertEqual(cod, 204)

    def test_26_apagar_nota_inexistente_da_404(self):
        cod, _ = chamar(ctx_cliente("admin"), "/notas/99999", "DELETE")
        self.assertEqual(cod, 404)

    def test_27_rota_inexistente_da_404(self):
        cod, _ = chamar(ctx_cliente("admin"), "/nao-existe")
        self.assertEqual(cod, 404)

    def test_28_json_invalido_da_400(self):
        cod, _ = chamar(ctx_cliente("escritor"), "/notas", "POST", bruto=b"{isso nao e json")
        self.assertEqual(cod, 400)

    def test_29_texto_vazio_da_400(self):
        cod, _ = chamar(ctx_cliente("escritor"), "/notas", "POST", {"texto": "   "})
        self.assertEqual(cod, 400)

    def test_30_corpo_gigante_e_recusado(self):
        cod, _ = chamar(ctx_cliente("escritor"), "/notas", "POST", bruto=b"x" * (70 * 1024))
        self.assertEqual(cod, 400)


# ═══════════════════════════════ 3. ATAQUES ══════════════════════════════════
class TesteAtaques(unittest.TestCase):
    """Cada teste aqui é uma tentativa de entrar. Todas devem falhar."""

    def test_40_sem_certificado_de_cliente(self):
        with self.assertRaises((ssl.SSLError, urllib.error.URLError)) as e:
            chamar(ctx_cliente(None), "/saude")
        self.assertIn("CERTIFICATE_REQUIRED", str(e.exception).upper().replace(" ", "_"))

    def test_41_certificado_de_outra_ca(self):
        """O intruso tem CN='admin' — mas foi assinado pela CA errada."""
        with self.assertRaises((ssl.SSLError, urllib.error.URLError)) as e:
            chamar(ctx_cliente("intruso"), "/saude")
        self.assertIn("UNKNOWN_CA", str(e.exception).upper())

    def test_42_certificado_revogado(self):
        with self.assertRaises((ssl.SSLError, urllib.error.URLError)) as e:
            chamar(ctx_cliente("banido"), "/saude")
        self.assertIn("REVOKED", str(e.exception).upper())

    def test_43_certificado_vencido(self):
        with self.assertRaises((ssl.SSLError, urllib.error.URLError)) as e:
            chamar(ctx_cliente("vencido"), "/saude")
        self.assertIn("EXPIRED", str(e.exception).upper())

    def test_44_cliente_recusa_servidor_com_nome_errado(self):
        """127.0.0.2 não está no SAN do servidor: a verificação de nome tem de barrar.

        Usamos socket cru de propósito. `urllib` respeita as variáveis de
        proxy do ambiente, e um `no_proxy` com faixa CIDR (`127.0.0.0/8`) —
        que a maioria dos clientes NÃO interpreta — faria a conexão sair pelo
        proxy corporativo e o erro observado seria outro. Teste de TLS não
        pode depender do ambiente de rede de quem roda.
        """
        import socket
        ctx = ctx_cliente("admin")
        with self.assertRaises(ssl.SSLCertVerificationError) as e:
            with socket.create_connection(("127.0.0.2", PORTA), 10) as s:
                ctx.wrap_socket(s, server_hostname="127.0.0.2")
        self.assertIn("MISMATCH", str(e.exception).upper().replace(" ", ""))

    def test_45_cliente_recusa_servidor_de_ca_desconhecida(self):
        """Confiando só na CA do intruso, o servidor legítimo tem de ser recusado."""
        import socket
        ctx = ctx_cliente("admin", ca="intruso-ca.crt")
        with self.assertRaises(ssl.SSLCertVerificationError) as e:
            with socket.create_connection(("127.0.0.1", PORTA), 10) as s:
                ctx.wrap_socket(s, server_hostname="localhost")
        self.assertIn("VERIFY", str(e.exception).upper())

    def test_46_tls_antigo_e_recusado(self):
        """Cliente preso em TLS 1.1 não deve conseguir falar com o servidor."""
        ctx = ctx_cliente("admin")
        ctx.minimum_version = ssl.TLSVersion.TLSv1
        ctx.maximum_version = ssl.TLSVersion.TLSv1_1
        with self.assertRaises((ssl.SSLError, urllib.error.URLError, OSError)):
            chamar(ctx, "/saude")

    def test_47_check_hostname_esta_realmente_ligado(self):
        ctx = ctx_cliente("admin")
        self.assertTrue(ctx.check_hostname)
        self.assertEqual(ctx.verify_mode, ssl.CERT_REQUIRED)


# ═══════════════════════ 4. Propriedades da conexão ══════════════════════════
class TesteConexao(unittest.TestCase):

    def _sessao(self):
        import socket
        ctx = ctx_cliente("admin")
        with socket.create_connection(("127.0.0.1", PORTA), 10) as s:
            with ctx.wrap_socket(s, server_hostname="localhost") as ts:
                return ts.version(), ts.cipher()

    def test_50_negocia_tls13(self):
        versao, _ = self._sessao()
        self.assertEqual(versao, "TLSv1.3")

    def test_51_cifra_e_aead(self):
        _, cifra = self._sessao()
        nome = cifra[0]
        self.assertTrue(nome.startswith("TLS_AES") or nome.startswith("TLS_CHACHA20"),
                        f"cifra inesperada: {nome}")

    def test_52_servidor_exige_verificacao_de_cliente(self):
        ctx = app.montar_contexto()
        self.assertEqual(ctx.verify_mode, ssl.CERT_REQUIRED)
        self.assertTrue(ctx.verify_flags & ssl.VERIFY_CRL_CHECK_LEAF)
        self.assertEqual(ctx.minimum_version, ssl.TLSVersion.TLSv1_2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
