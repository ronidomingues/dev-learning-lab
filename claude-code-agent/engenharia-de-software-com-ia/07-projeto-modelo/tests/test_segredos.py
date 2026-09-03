"""Testes da regra de segredos. Cobre CA-07 e CA-08."""

import unittest

from portao.config import Config
from portao.diff import ler
from portao.regras import segredos
from portao.modelo import Severidade


def diff_com_linha(caminho: str, linha: str) -> str:
    return (
        f"diff --git a/{caminho} b/{caminho}\n"
        f"--- a/{caminho}\n"
        f"+++ b/{caminho}\n"
        "@@ -1,0 +1,1 @@\n"
        f"+{linha}\n"
    )


class TesteSegredos(unittest.TestCase):
    def test_ca07_chave_privada(self):
        """CA-07: bloco de chave privada é detectado."""
        d = ler(diff_com_linha("deploy.sh", "-----BEGIN RSA PRIVATE KEY-----"))
        r = segredos.verificar(d, Config())
        self.assertFalse(r.aprovado)
        self.assertIn("chave privada", r.bloqueios[0].mensagem)

    def test_ca07_chave_aws(self):
        """CA-07: chave de acesso da AWS é detectada."""
        d = ler(diff_com_linha("conf.py", 'AWS = "AKIAIOSFODNN7EXAMPLE"'))
        r = segredos.verificar(d, Config())
        self.assertFalse(r.aprovado)

    def test_ca07_chave_anthropic(self):
        """CA-07: chave da Anthropic é detectada."""
        chave = "sk-ant-api03-" + "Kd93jfLmQ8xZpR2vTnB7yWcH4sAeUgN1oVzXbMdF"
        d = ler(diff_com_linha("conf.py", f'API_KEY = "{chave}"'))
        r = segredos.verificar(d, Config())
        self.assertFalse(r.aprovado)

    def test_ca07_url_com_senha(self):
        """CA-07: URL com credencial embutida é detectada."""
        d = ler(diff_com_linha("conf.py", 'DB = "postgres://admin:Tr0ub4dor@db:5432/prod"'))
        r = segredos.verificar(d, Config())
        self.assertFalse(r.aprovado)

    def test_ca07_jwt(self):
        """CA-07: JWT em linha adicionada é detectado."""
        jwt = (
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
            "eyJzdWIiOiIxMjM0NTY3ODkwIn0."
            "dBjftJeZ4CVPmB92K27uhbUJU1p1r_wW1gFWFOEjXk"
        )
        d = ler(diff_com_linha("teste.js", f'const t = "{jwt}";'))
        r = segredos.verificar(d, Config())
        self.assertFalse(r.aprovado)

    def test_ca07_linha_removida_nao_conta(self):
        """CA-07: só linha ADICIONADA é examinada."""
        texto = (
            "diff --git a/conf.py b/conf.py\n"
            "--- a/conf.py\n"
            "+++ b/conf.py\n"
            "@@ -1,1 +1,1 @@\n"
            '-AWS = "AKIAIOSFODNN7EXAMPLE"\n'
            '+AWS = os.environ["AWS_KEY"]\n'
        )
        r = segredos.verificar(ler(texto), Config())
        self.assertTrue(r.aprovado)

    def test_ca08_placeholder_ignorado(self):
        """CA-08: valor de exemplo não vira alarme."""
        for valor in ("seu-token-aqui", "xxxxxxxxxxxxxxxxxxxxxxxxxx", "<YOUR_API_KEY>", "${API_KEY}"):
            with self.subTest(valor=valor):
                d = ler(diff_com_linha(".env.example", f'API_KEY={valor}'))
                r = segredos.verificar(d, Config())
                self.assertTrue(r.aprovado, f"falso positivo em {valor!r}")

    def test_ca08_escape_respeitado(self):
        """CA-08: o escape explícito desliga a regra naquela linha."""
        chave = "sk-ant-api03-" + "Kd93jfLmQ8xZpR2vTnB7yWcH4sAeUgN1oVzXbMdF"
        d = ler(diff_com_linha(
            "tests/fixtures.py",
            f'CHAVE_FALSA = "{chave}"  # portao: ignora-segredo',
        ))
        r = segredos.verificar(d, Config())
        self.assertTrue(r.aprovado)

    def test_ca08_entropia_apenas_avisa(self):
        """CA-08: alta entropia sem formato conhecido avisa, não bloqueia."""
        d = ler(diff_com_linha("conf.py", 'senha = "9fQzL2xVbN7mKpR4tYuH3wEa"'))
        r = segredos.verificar(d, Config())
        self.assertTrue(r.aprovado)
        self.assertEqual(len(r.avisos), 1)
        self.assertIs(r.avisos[0].severidade, Severidade.AVISA)

    def test_ca08_caminho_ignorado(self):
        """CA-08: lockfile não é varrido (ruído garantido, sinal nenhum)."""
        cfg = Config(segredos_ignorar_caminhos=["package-lock.json"])
        d = ler(diff_com_linha("package-lock.json", '"integrity": "sha512-AKIAIOSFODNN7EXAMPLE"'))
        r = segredos.verificar(d, cfg)
        self.assertTrue(r.aprovado)

    def test_entropia_calculada_corretamente(self):
        self.assertAlmostEqual(segredos.entropia("aaaa"), 0.0)
        self.assertAlmostEqual(segredos.entropia("abcd"), 2.0)
        self.assertAlmostEqual(segredos.entropia(""), 0.0)


if __name__ == "__main__":
    unittest.main()
