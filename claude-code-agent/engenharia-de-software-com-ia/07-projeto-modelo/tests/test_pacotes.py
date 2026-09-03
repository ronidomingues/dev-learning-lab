"""Testes da regra de pacotes. Cobre CA-09. Nenhum teste usa a rede."""

import unittest

from portao.config import Config
from portao.diff import ler
from portao.regras import pacotes

DIFF_REQUIREMENTS = """diff --git a/requirements.txt b/requirements.txt
--- a/requirements.txt
+++ b/requirements.txt
@@ -1,1 +1,3 @@
 requests==2.32.3
+starlette-reverse-proxy==0.4.1
+fastapi>=0.110
"""

DIFF_PACKAGE_JSON = """diff --git a/package.json b/package.json
--- a/package.json
+++ b/package.json
@@ -5,6 +5,8 @@
   "dependencies": {
     "express": "^4.19.2",
+    "left-pad-turbo": "^1.0.0",
+    "zod": "^3.23.8"
   }
"""


class TestePacotes(unittest.TestCase):
    def test_ca09_reprova_dependencia_nova_offline(self):
        """CA-09: dependência nova não aprovada reprova, sem rede."""
        cfg = Config(dependencias_permitidas=[], checar_registro_online=False)
        r = pacotes.verificar(ler(DIFF_REQUIREMENTS), cfg)
        self.assertFalse(r.aprovado)
        nomes = " ".join(a.mensagem for a in r.bloqueios)
        self.assertIn("starlette-reverse-proxy", nomes)
        self.assertIn("fastapi", nomes)

    def test_ca09_aprova_o_que_esta_na_lista(self):
        """CA-09: dependência já aprovada não reprova."""
        cfg = Config(dependencias_permitidas=["fastapi", "starlette-reverse-proxy"])
        r = pacotes.verificar(ler(DIFF_REQUIREMENTS), cfg)
        self.assertTrue(r.aprovado)

    def test_ca09_lista_e_insensivel_a_caixa(self):
        """CA-09: a comparação de nome ignora maiúsculas."""
        cfg = Config(dependencias_permitidas=["FastAPI", "Starlette-Reverse-Proxy"])
        r = pacotes.verificar(ler(DIFF_REQUIREMENTS), cfg)
        self.assertTrue(r.aprovado)

    def test_ca09_package_json(self):
        """CA-09: dependências de package.json também são pegas."""
        cfg = Config(dependencias_permitidas=["zod"])
        r = pacotes.verificar(ler(DIFF_PACKAGE_JSON), cfg)
        self.assertFalse(r.aprovado)
        self.assertEqual(len(r.bloqueios), 1)
        self.assertIn("left-pad-turbo", r.bloqueios[0].mensagem)

    def test_ca09_offline_nao_toca_a_rede(self):
        """CA-09: no modo padrão, existe_no_registro nunca é chamada."""
        chamou = []
        original = pacotes.existe_no_registro
        pacotes.existe_no_registro = lambda *a, **k: chamou.append(a)
        try:
            pacotes.verificar(ler(DIFF_REQUIREMENTS), Config())
        finally:
            pacotes.existe_no_registro = original
        self.assertEqual(chamou, [])

    def test_ca09_online_distingue_inexistente(self):
        """CA-09: com rede, pacote inexistente tem mensagem diferente."""
        original = pacotes.existe_no_registro
        pacotes.existe_no_registro = lambda eco, nome: nome != "starlette-reverse-proxy"
        try:
            cfg = Config(checar_registro_online=True)
            r = pacotes.verificar(ler(DIFF_REQUIREMENTS), cfg)
        finally:
            pacotes.existe_no_registro = original
        inexistentes = [a for a in r.bloqueios if "INEXISTENTE" in a.mensagem]
        self.assertEqual(len(inexistentes), 1)
        self.assertIn("starlette-reverse-proxy", inexistentes[0].mensagem)

    def test_ca09_falha_de_rede_apenas_avisa(self):
        """CA-09: rede indisponível não bloqueia o portão."""
        original = pacotes.existe_no_registro
        pacotes.existe_no_registro = lambda eco, nome: None
        try:
            cfg = Config(checar_registro_online=True)
            r = pacotes.verificar(ler(DIFF_REQUIREMENTS), cfg)
        finally:
            pacotes.existe_no_registro = original
        self.assertTrue(r.aprovado)
        self.assertEqual(len(r.avisos), 2)


if __name__ == "__main__":
    unittest.main()
