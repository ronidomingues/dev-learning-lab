"""Testes da interface de linha de comando. Cobre CA-11 e CA-12."""

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path

from portao.cli import main
from portao.config import Config

RAIZ = Path(__file__).resolve().parent.parent


class TesteCLI(unittest.TestCase):
    def roda(self, *args) -> tuple[int, str, str]:
        saida, erro = io.StringIO(), io.StringIO()
        with redirect_stdout(saida), redirect_stderr(erro):
            codigo = main(list(args))
        return codigo, saida.getvalue(), erro.getvalue()

    def test_ca11_aprovado_devolve_zero(self):
        """CA-11: diff limpo devolve código 0."""
        codigo, saida, _ = self.roda(
            "escopo", "tamanho", "segredos", "pacotes",
            "--diff", str(RAIZ / "exemplos" / "bom.diff"),
            "--raiz", str(RAIZ), "--sem-cor",
        )
        self.assertEqual(codigo, 0, saida)
        self.assertIn("APROVADO", saida)

    def test_ca11_reprovado_devolve_um(self):
        """CA-11: diff problemático devolve código 1."""
        codigo, saida, _ = self.roda(
            "--diff", str(RAIZ / "exemplos" / "ruim.diff"),
            "--raiz", str(RAIZ), "--sem-cor",
        )
        self.assertEqual(codigo, 1)
        self.assertIn("REPROVADO", saida)

    def test_ruim_dispara_as_tres_regras_esperadas(self):
        """O diff ruim viola escopo (teste), pacotes e segredos."""
        codigo, saida, _ = self.roda(
            "--diff", str(RAIZ / "exemplos" / "ruim.diff"),
            "--raiz", str(RAIZ), "--sem-cor", "--formato", "json",
        )
        dados = json.loads(saida)
        reprovadas = {r["regra"] for r in dados["regras"] if not r["aprovado"]}
        self.assertEqual(reprovadas, {"escopo", "pacotes", "segredos"})

    def test_formato_json_valido(self):
        _, saida, _ = self.roda(
            "escopo",
            "--diff", str(RAIZ / "exemplos" / "bom.diff"),
            "--raiz", str(RAIZ), "--formato", "json",
        )
        dados = json.loads(saida)
        self.assertIn("aprovado", dados)
        self.assertIn("regras", dados)

    def test_ca12_config_invalida_devolve_dois(self):
        """CA-12: configuração inválida devolve código 2 com mensagem clara."""
        tmp = Path(tempfile.mkdtemp())
        (tmp / "portao.json").write_text('{"max_arquivos": -3}', encoding="utf-8")
        codigo, _, erro = self.roda("--diff", str(RAIZ / "exemplos" / "bom.diff"), "--raiz", str(tmp))
        self.assertEqual(codigo, 2)
        self.assertIn("max_arquivos", erro)

    def test_ca12_chave_desconhecida_rejeitada(self):
        """CA-12: chave desconhecida na configuração é erro, não silêncio."""
        with self.assertRaises(ValueError) as ctx:
            Config.de_dict({"limite_maximo": 10})
        self.assertIn("limite_maximo", str(ctx.exception))

    def test_regra_desconhecida_devolve_dois(self):
        codigo, _, erro = self.roda("inexistente", "--diff", str(RAIZ / "exemplos" / "bom.diff"))
        self.assertEqual(codigo, 2)
        self.assertIn("inexistente", erro)

    def test_arquivo_de_diff_ausente_devolve_dois(self):
        codigo, _, erro = self.roda("--diff", "/nao/existe.diff")
        self.assertEqual(codigo, 2)

    def test_testes_editaveis_altera_o_veredito(self):
        """A mesma alteração reprova por padrão e passa com a bandeira."""
        tmp = Path(tempfile.mkdtemp())
        diff = tmp / "so-teste.diff"
        diff.write_text(
            "diff --git a/tests/test_x.py b/tests/test_x.py\n"
            "--- a/tests/test_x.py\n"
            "+++ b/tests/test_x.py\n"
            "@@ -1,1 +1,2 @@\n"
            " import unittest\n"
            "+# novo caso\n",
            encoding="utf-8",
        )
        args = ["escopo", "--diff", str(diff), "--raiz", str(RAIZ), "--sem-cor"]
        self.assertEqual(self.roda(*args)[0], 1)
        self.assertEqual(self.roda(*args, "--testes-editaveis")[0], 0)


if __name__ == "__main__":
    unittest.main()
