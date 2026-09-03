"""Testes da regra de escopo. Cobre CA-03 e CA-04."""

import unittest

from portao.config import Config
from portao.diff import ler
from portao.regras import escopo


def diff_de(caminho: str) -> str:
    return (
        f"diff --git a/{caminho} b/{caminho}\n"
        f"--- a/{caminho}\n"
        f"+++ b/{caminho}\n"
        "@@ -1,1 +1,2 @@\n"
        " existente\n"
        "+nova\n"
    )


class TesteEscopo(unittest.TestCase):
    def test_ca03_reprova_fora_do_escopo(self):
        """CA-03: arquivo fora de escopo_permitido reprova."""
        cfg = Config(escopo_permitido=["src/**"])
        r = escopo.verificar(ler(diff_de("infra/deploy.tf")), cfg)
        self.assertFalse(r.aprovado)
        self.assertIn("fora do escopo", r.bloqueios[0].mensagem)

    def test_ca03_aprova_dentro_do_escopo(self):
        """CA-03: arquivo dentro do escopo passa."""
        cfg = Config(escopo_permitido=["src/**"])
        r = escopo.verificar(ler(diff_de("src/pedido/calculo.py")), cfg)
        self.assertTrue(r.aprovado)

    def test_ca03_escopo_permitido_casa_raiz(self):
        """CA-03: 'src/**' também casa com arquivo direto em src/."""
        cfg = Config(escopo_permitido=["src/**"])
        r = escopo.verificar(ler(diff_de("src/app.py")), cfg)
        self.assertTrue(r.aprovado)

    def test_ca03_proibido_vence_permitido(self):
        """CA-03: caminho proibido reprova mesmo dentro do permitido."""
        cfg = Config(escopo_permitido=["**"], escopo_proibido=["**/*.pem"])
        r = escopo.verificar(ler(diff_de("certs/servidor.pem")), cfg)
        self.assertFalse(r.aprovado)

    def test_ca04_reprova_alteracao_de_teste(self):
        """CA-04: alterar teste reprova por padrão."""
        cfg = Config()
        r = escopo.verificar(ler(diff_de("tests/test_pedido.py")), cfg)
        self.assertFalse(r.aprovado)
        self.assertIn("teste", r.bloqueios[0].mensagem)

    def test_ca04_permite_quando_ligado(self):
        """CA-04: com testes_editaveis, alterar teste passa."""
        cfg = Config(testes_editaveis=True)
        r = escopo.verificar(ler(diff_de("tests/test_pedido.py")), cfg)
        self.assertTrue(r.aprovado)


if __name__ == "__main__":
    unittest.main()
