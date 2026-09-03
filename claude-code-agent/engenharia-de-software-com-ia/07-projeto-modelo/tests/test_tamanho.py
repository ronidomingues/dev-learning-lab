"""Testes da regra de tamanho. Cobre CA-05 e CA-06."""

import unittest

from portao.config import Config
from portao.diff import ler
from portao.regras import tamanho
from portao.modelo import Severidade


def diff_com(caminho: str, adicionadas: int) -> str:
    corpo = "".join(f"+linha {i}\n" for i in range(adicionadas))
    return (
        f"diff --git a/{caminho} b/{caminho}\n"
        f"--- a/{caminho}\n"
        f"+++ b/{caminho}\n"
        f"@@ -1,0 +1,{adicionadas} @@\n"
        f"{corpo}"
    )


class TesteTamanho(unittest.TestCase):
    def test_ca05_reprova_acima_do_limite_total(self):
        """CA-05: diff acima do limite total reprova."""
        cfg = Config(max_alteracoes_total=10, max_alteracoes_por_arquivo=1000)
        r = tamanho.verificar(ler(diff_com("src/a.py", 50)), cfg)
        self.assertFalse(r.aprovado)
        self.assertTrue(any("50 linhas alteradas" in a.mensagem for a in r.bloqueios))

    def test_ca05_aprova_dentro_do_limite(self):
        """CA-05: diff dentro do limite passa."""
        cfg = Config(max_alteracoes_total=100)
        r = tamanho.verificar(ler(diff_com("src/a.py", 50)), cfg)
        self.assertTrue(r.aprovado)

    def test_ca05_reprova_muitos_arquivos(self):
        """CA-05: número de arquivos também é limitado."""
        cfg = Config(max_arquivos=2, max_alteracoes_total=10000)
        texto = "".join(diff_com(f"src/a{i}.py", 1) for i in range(5))
        r = tamanho.verificar(ler(texto), cfg)
        self.assertFalse(r.aprovado)

    def test_ca06_apenas_avisa_por_arquivo(self):
        """CA-06: estouro por arquivo avisa, não bloqueia."""
        cfg = Config(max_alteracoes_total=10000, max_alteracoes_por_arquivo=10)
        r = tamanho.verificar(ler(diff_com("src/grande.py", 100)), cfg)
        self.assertTrue(r.aprovado)
        self.assertEqual(len(r.avisos), 1)
        self.assertIs(r.avisos[0].severidade, Severidade.AVISA)


if __name__ == "__main__":
    unittest.main()
