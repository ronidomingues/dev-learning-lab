"""Testes da regra de critérios. Cobre CA-10."""

import tempfile
import unittest
from pathlib import Path

from portao.config import Config
from portao.diff import ler
from portao.regras import criterios

ESPEC = """# Espec

- **CA-01** primeira coisa
- **CA-02** segunda coisa
- **CA-03** terceira coisa
"""


class TesteCriterios(unittest.TestCase):
    def monta(self, espec: str, testes: dict[str, str]) -> Path:
        raiz = Path(tempfile.mkdtemp())
        (raiz / "ESPEC.md").write_text(espec, encoding="utf-8")
        (raiz / "tests").mkdir()
        for nome, conteudo in testes.items():
            (raiz / "tests" / nome).write_text(conteudo, encoding="utf-8")
        return raiz

    def test_ca10_reprova_criterio_sem_teste(self):
        """CA-10: critério sem teste que o cite reprova."""
        raiz = self.monta(ESPEC, {"test_a.py": "# cobre CA-01 e CA-02"})
        r = criterios.verificar(ler(""), Config(), raiz)
        self.assertFalse(r.aprovado)
        self.assertEqual(len(r.bloqueios), 1)
        self.assertIn("CA-03", r.bloqueios[0].mensagem)

    def test_ca10_aprova_quando_todos_citados(self):
        """CA-10: com todos os critérios citados, aprova."""
        raiz = self.monta(ESPEC, {"test_a.py": "# CA-01 CA-02 CA-03"})
        r = criterios.verificar(ler(""), Config(), raiz)
        self.assertTrue(r.aprovado)

    def test_ca10_criterio_orfao_apenas_avisa(self):
        """CA-10: identificador citado sem existir na espec só avisa."""
        raiz = self.monta(ESPEC, {"test_a.py": "# CA-01 CA-02 CA-03 CA-99"})
        r = criterios.verificar(ler(""), Config(), raiz)
        self.assertTrue(r.aprovado)
        self.assertEqual(len(r.avisos), 1)
        self.assertIn("CA-99", r.avisos[0].mensagem)

    def test_pula_sem_especificacao(self):
        raiz = Path(tempfile.mkdtemp())
        r = criterios.verificar(ler(""), Config(), raiz)
        self.assertTrue(r.pulada)
        self.assertTrue(r.aprovado)

    def test_pula_sem_criterios_no_formato(self):
        raiz = self.monta("# Espec sem identificadores\n", {})
        r = criterios.verificar(ler(""), Config(), raiz)
        self.assertTrue(r.pulada)

    def test_extrai_descricao_do_criterio(self):
        m = criterios.criterios_da_especificacao(ESPEC)
        self.assertEqual(m["CA-02"], "segunda coisa")


if __name__ == "__main__":
    unittest.main()
