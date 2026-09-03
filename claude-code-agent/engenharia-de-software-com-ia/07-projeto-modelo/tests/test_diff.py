"""Testes do leitor de diff. Cobre CA-01 e CA-02."""

import unittest

from portao.diff import ler

DIFF_SIMPLES = """diff --git a/src/a.py b/src/a.py
index 111..222 100644
--- a/src/a.py
+++ b/src/a.py
@@ -10,3 +10,5 @@ def f():
     x = 1
+    y = 2
+    z = 3
     return x
"""

DIFF_NOVO = """diff --git a/src/novo.py b/src/novo.py
new file mode 100644
index 0000000..333
--- /dev/null
+++ b/src/novo.py
@@ -0,0 +1,2 @@
+print("oi")
+print("tchau")
"""

DIFF_REMOVIDO = """diff --git a/src/velho.py b/src/velho.py
deleted file mode 100644
index 444..0000000
--- a/src/velho.py
+++ /dev/null
@@ -1,2 +0,0 @@
-print("oi")
-print("tchau")
"""


class TesteLeitorDeDiff(unittest.TestCase):
    def test_ca01_identifica_arquivo_e_linhas_adicionadas(self):
        """CA-01: arquivos e linhas adicionadas com número correto."""
        d = ler(DIFF_SIMPLES)
        self.assertEqual(d.caminhos, ["src/a.py"])
        arq = d.arquivos[0]
        self.assertEqual([l.texto for l in arq.adicionadas], ["    y = 2", "    z = 3"])
        # a linha de contexto "x = 1" está na 10; as adicionadas vêm em 11 e 12
        self.assertEqual([l.numero for l in arq.adicionadas], [11, 12])

    def test_ca01_conta_removidas(self):
        """CA-01: linhas removidas entram na contagem de alterações."""
        d = ler(DIFF_REMOVIDO)
        self.assertEqual(d.arquivos[0].removidas, 2)
        self.assertEqual(d.total_alteracoes, 2)

    def test_ca02_arquivo_novo(self):
        """CA-02: arquivo novo é reconhecido como novo."""
        d = ler(DIFF_NOVO)
        self.assertTrue(d.arquivos[0].novo)
        self.assertFalse(d.arquivos[0].removido)

    def test_ca02_arquivo_removido(self):
        """CA-02: arquivo removido é reconhecido como removido."""
        d = ler(DIFF_REMOVIDO)
        self.assertTrue(d.arquivos[0].removido)
        self.assertFalse(d.arquivos[0].novo)

    def test_diff_vazio_nao_quebra(self):
        d = ler("")
        self.assertEqual(d.arquivos, [])
        self.assertEqual(d.total_alteracoes, 0)

    def test_varios_arquivos(self):
        d = ler(DIFF_SIMPLES + DIFF_NOVO)
        self.assertEqual(d.caminhos, ["src/a.py", "src/novo.py"])


if __name__ == "__main__":
    unittest.main()
