"""Testes do projeto `resumo`.

Estratégia: sempre que possível, conferir contra um valor **externo** —
tabela publicada, saída conhecida do NumPy/R, ou identidade matemática —
em vez de contra o que o próprio código produz. Teste que só confirma o
que o código faz não detecta erro nenhum.

    python3 -m unittest discover -s testes -v
"""

import contextlib
import io
import math
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from resumo import diagnostico as D          # noqa: E402
from resumo import incerteza as I            # noqa: E402
from resumo import medidas as M              # noqa: E402
from resumo import relatorio as R            # noqa: E402
from resumo.formato import num, pct          # noqa: E402
from resumo.leitura import (ErroDeLeitura, _para_float, detectar_decimal,  # noqa: E402
                            detectar_separador, ler_csv)
from resumo.__main__ import main             # noqa: E402

# conjunto de referência usado na literatura e nos exemplos do curso
D8 = [2, 4, 4, 4, 5, 5, 7, 9]


class TestPosicao(unittest.TestCase):

    def test_media(self):
        self.assertEqual(M.media(D8), 5.0)
        self.assertEqual(M.media([1, 2, 3, 4]), 2.5)

    def test_media_usa_soma_exata(self):
        # 10 milhões de 0,1: sum() acumula erro, fsum não
        v = [0.1] * 1_000_000
        self.assertAlmostEqual(M.media(v), 0.1, places=15)

    def test_mediana_impar_e_par(self):
        self.assertEqual(M.mediana([3, 1, 2]), 2)
        self.assertEqual(M.mediana([4, 1, 3, 2]), 2.5)

    def test_mediana_nao_depende_da_ordem(self):
        self.assertEqual(M.mediana([9, 1, 5]), M.mediana([1, 5, 9]))

    def test_moda_com_empate(self):
        self.assertEqual(M.moda([1, 1, 2, 2, 3]), ([1, 2], 2))

    def test_media_aparada_descarta_extremos(self):
        d = [1, 2, 3, 4, 5, 6, 7, 8, 9, 1000]
        self.assertLess(M.media_aparada(d, 0.10), M.media(d))

    def test_media_aparada_zero_e_a_media(self):
        self.assertEqual(M.media_aparada(D8, 0.0), M.media(D8))

    def test_harmonica_resolve_ida_e_volta(self):
        # 120 km a 100 km/h + 120 km a 60 km/h = 240 km em 3,2 h = 75 km/h
        self.assertAlmostEqual(M.media_harmonica([100, 60]), 75.0)

    def test_geometrica_bate_com_o_acumulado(self):
        fatores = [1.5, 0.5, 1.5, 0.5]
        g = M.media_geometrica(fatores)
        acumulado = 1.0
        for f in fatores:
            acumulado *= f
        self.assertAlmostEqual(g ** len(fatores), acumulado)

    def test_desigualdade_das_medias(self):
        d = [2.0, 5.0, 11.0, 3.5]
        self.assertLessEqual(M.media_harmonica(d), M.media_geometrica(d))
        self.assertLessEqual(M.media_geometrica(d), M.media(d))

    def test_geometrica_exige_positivos(self):
        with self.assertRaises(M.ErroDeMedida):
            M.media_geometrica([1, 0, 2])


class TestQuantis(unittest.TestCase):

    def test_quartis_tipo7_batem_com_numpy(self):
        # np.percentile([2,4,4,4,5,5,7,9], [25,50,75]) -> [4.0, 4.5, 5.5]
        self.assertEqual(M.quartis(D8), (4.0, 4.5, 5.5))

    def test_quantil_extremos(self):
        self.assertEqual(M.quantil(D8, 0.0), 2.0)
        self.assertEqual(M.quantil(D8, 1.0), 9.0)

    def test_quantil_meio_e_a_mediana(self):
        self.assertEqual(M.quantil(D8, 0.5), M.mediana(D8))

    def test_quantil_fora_do_dominio(self):
        with self.assertRaises(M.ErroDeMedida):
            M.quantil(D8, 1.5)

    def test_quantil_de_um_unico_valor(self):
        self.assertEqual(M.quantil([7], 0.9), 7.0)


class TestDispersao(unittest.TestCase):

    def test_desvio_padrao_amostral_e_populacional(self):
        # valores conhecidos: np.std(D8, ddof=1)=2.138089935299395; ddof=0 -> 2.0
        self.assertAlmostEqual(M.desvio_padrao(D8), 2.138089935299395)
        self.assertAlmostEqual(M.desvio_padrao(D8, ddof=0), 2.0)

    def test_variancia_de_constante_e_zero(self):
        self.assertEqual(M.variancia([5, 5, 5, 5]), 0.0)

    def test_welford_evita_cancelamento_catastrofico(self):
        # a forma ingênua sum(x^2)/n - m^2 devolve valor errado (às vezes negativo)
        base = 1e9
        d = [base + 4, base + 7, base + 13, base + 16]
        self.assertAlmostEqual(M.variancia(d), M.variancia([4, 7, 13, 16]), places=6)

    def test_variancia_invariante_a_deslocamento(self):
        d = [3, 7, 7, 19]
        self.assertAlmostEqual(M.variancia(d), M.variancia([x + 1000 for x in d]))

    def test_desvio_padrao_escala_linear(self):
        d = [3, 7, 7, 19]
        self.assertAlmostEqual(M.desvio_padrao([3 * x for x in d]),
                               3 * M.desvio_padrao(d))

    def test_erro_padrao_cai_com_raiz_de_n(self):
        # quadruplicar n com a mesma dispersão reduz o EP pela metade
        d = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        razao = M.erro_padrao(d * 4) / M.erro_padrao(d)
        self.assertLess(abs(razao - 0.5), 0.05)

    def test_mad_igual_ao_dp_em_dados_normais(self):
        import random
        rng = random.Random(1)
        d = [rng.gauss(0, 1) for _ in range(20000)]
        self.assertAlmostEqual(M.mad(d), M.desvio_padrao(d), places=1)

    def test_mad_ignora_outlier_e_dp_nao(self):
        d = [10, 11, 12, 11, 10, 12, 11]
        dp0, mad0 = M.desvio_padrao(d), M.mad(d)
        d2 = d + [10000]
        self.assertGreater(M.desvio_padrao(d2), 10 * dp0)
        self.assertLess(M.mad(d2), 2 * mad0)

    def test_cv_indefinido_com_media_zero(self):
        with self.assertRaises(M.ErroDeMedida):
            M.coef_variacao([-1, 1, -2, 2])

    def test_stdev_exige_dois_pontos(self):
        with self.assertRaises(M.ErroDeMedida):
            M.desvio_padrao([5])


class TestForma(unittest.TestCase):

    def test_assimetria_de_simetrico_e_zero(self):
        self.assertAlmostEqual(M.assimetria([1, 2, 3, 4, 5]), 0.0, places=12)

    def test_assimetria_positiva_com_cauda_direita(self):
        self.assertGreater(M.assimetria([1, 1, 2, 2, 3, 100]), 1.0)

    def test_curtose_de_uniforme_e_negativa(self):
        d = list(range(1, 201))
        self.assertLess(M.curtose_excesso(d), -1.0)

    def test_cobertura_1dp_em_normal(self):
        import random
        rng = random.Random(7)
        d = [rng.gauss(0, 1) for _ in range(50000)]
        self.assertAlmostEqual(M.cobertura_1dp(d), 0.6827, places=2)

    def test_cobertura_1dp_em_cauda_pesada(self):
        d = [1] * 98 + [1000, 2000]
        self.assertGreater(M.cobertura_1dp(d), 0.90)


class TestIncerteza(unittest.TestCase):

    def test_z_critico_bate_com_a_tabela(self):
        self.assertAlmostEqual(I.z_critico(0.95), 1.959963984540054, places=9)
        self.assertAlmostEqual(I.z_critico(0.99), 2.5758293035489004, places=9)

    def test_t_critico_bate_com_a_tabela_impressa(self):
        tabela = {1: 12.7062, 2: 4.3027, 5: 2.5706, 9: 2.2622,
                  10: 2.2281, 30: 2.0423, 100: 1.9840}
        for gl, esperado in tabela.items():
            self.assertAlmostEqual(I.t_critico(0.95, gl), esperado, places=4)

    def test_t_converge_para_z(self):
        self.assertAlmostEqual(I.t_critico(0.95, 100000), I.z_critico(0.95), places=3)

    def test_t_e_sempre_mais_largo_que_z(self):
        for gl in (2, 5, 10, 50):
            self.assertGreater(I.t_critico(0.95, gl), I.z_critico(0.95))

    def test_t_cdf_simetrica(self):
        self.assertAlmostEqual(I.t_cdf(0.0, 7), 0.5)
        self.assertAlmostEqual(I.t_cdf(1.3, 7) + I.t_cdf(-1.3, 7), 1.0, places=12)

    def test_ic_media_contem_a_media(self):
        d = [12, 15, 11, 14, 13, 12, 16, 14, 13, 15]
        lo, hi = I.ic_media_t(d)
        self.assertLess(lo, M.media(d))
        self.assertGreater(hi, M.media(d))

    def test_ic_mais_confiante_e_mais_largo(self):
        d = [12, 15, 11, 14, 13, 12, 16, 14, 13, 15]
        lo95, hi95 = I.ic_media_t(d, 0.95)
        lo99, hi99 = I.ic_media_t(d, 0.99)
        self.assertGreater(hi99 - lo99, hi95 - lo95)

    def test_bootstrap_e_reprodutivel_com_semente(self):
        d = [1, 5, 3, 8, 2, 9, 4]
        a = I.ic_bootstrap(d, M.mediana, repeticoes=500, semente=7)
        b = I.ic_bootstrap(d, M.mediana, repeticoes=500, semente=7)
        self.assertEqual(a, b)

    def test_bootstrap_muda_com_outra_semente(self):
        d = [1, 5, 3, 8, 2, 9, 4, 11, 6]
        a = I.ic_bootstrap(d, M.media, repeticoes=500, semente=1)
        b = I.ic_bootstrap(d, M.media, repeticoes=500, semente=2)
        self.assertNotEqual(a, b)

    def test_bootstrap_da_media_bate_com_o_erro_padrao_teorico(self):
        import random
        rng = random.Random(3)
        d = [rng.gauss(50, 10) for _ in range(200)]
        _, _, ep_boot = I.ic_bootstrap(d, M.media, repeticoes=4000, semente=9)
        self.assertAlmostEqual(ep_boot, M.erro_padrao(d), delta=0.10)

    def test_n_para_margem_reproduz_o_padrao_das_pesquisas(self):
        self.assertEqual(I.n_para_margem(0.02), 2401)
        self.assertEqual(I.n_para_margem(0.01), 9604)

    def test_quadruplicar_n_reduz_margem_pela_metade(self):
        n1 = I.n_para_margem(0.04)
        n2 = I.n_para_margem(0.02)
        self.assertAlmostEqual(n2 / n1, 4.0, delta=0.02)


class TestDiagnostico(unittest.TestCase):

    def test_detecta_assimetria(self):
        d = [1, 1, 2, 2, 3, 3, 4, 100]
        titulos = [a.titulo for a in D.diagnosticar(d)]
        self.assertTrue(any("assimétrica" in t for t in titulos))

    def test_detecta_outlier(self):
        d = [10, 11, 12, 11, 10, 12, 11, 500]
        titulos = [a.titulo for a in D.diagnosticar(d)]
        self.assertTrue(any("1,5×IQR" in t for t in titulos))

    def test_detecta_valores_todos_iguais(self):
        avisos = D.diagnosticar([7] * 40)
        self.assertEqual(avisos[0].gravidade, D.GRAVE)
        self.assertIn("iguais", avisos[0].titulo)

    def test_detecta_escala_ordinal_disfarcada(self):
        d = [3, 4, 5, 4, 3, 2, 5, 4, 3, 4] * 8
        titulos = [a.titulo for a in D.diagnosticar(d)]
        self.assertTrue(any("distintos" in t for t in titulos))

    def test_dados_bem_comportados_nao_geram_aviso_grave(self):
        import random
        rng = random.Random(4)
        d = [rng.gauss(100, 10) for _ in range(500)]
        graves = [a for a in D.diagnosticar(d) if a.gravidade == D.GRAVE]
        self.assertEqual(graves, [])

    def test_todo_aviso_tem_acao(self):
        d = [1, 1, 2, 2, 3, 3, 4, 100]
        for a in D.diagnosticar(d):
            self.assertTrue(a.acao.strip(), f"aviso sem ação: {a.titulo}")

    def test_detecta_arredondamento(self):
        d = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100] * 3
        titulos = [a.titulo for a in D.diagnosticar(d)]
        self.assertTrue(any("múltiplos" in t for t in titulos))


class TestLeitura(unittest.TestCase):

    def _arquivo(self, conteudo, sufixo=".csv", encoding="utf-8"):
        f = tempfile.NamedTemporaryFile("w", suffix=sufixo, delete=False,
                                        encoding=encoding, newline="")
        f.write(conteudo)
        f.close()
        self.addCleanup(os.unlink, f.name)
        return f.name

    def test_detecta_separador_ponto_e_virgula(self):
        p = self._arquivo("a;b;c\n1;2;3\n")
        self.assertEqual(detectar_separador(p), ";")

    def test_detecta_decimal_brasileiro(self):
        self.assertEqual(detectar_decimal(["R$ 1.500,00", "2.300,00", "1.234,56"]),
                         (",", False))

    def test_detecta_decimal_americano(self):
        self.assertEqual(detectar_decimal(["1,500.00", "2300.5", "1.5"]), (".", False))

    def test_sem_virgula_o_decimal_e_ponto(self):
        # regressão: "1.734" como altura já foi lido como 1734 milímetros
        self.assertEqual(detectar_decimal(["1.734", "1.702", "1.688", "1.75"]),
                         (".", False))

    def test_ambiguidade_e_sinalizada(self):
        dec, ambiguo = detectar_decimal(["1.500", "2.300", "12.000"])
        self.assertEqual(dec, ".")
        self.assertTrue(ambiguo)

    def test_altura_nao_vira_milimetro(self):
        p = self._arquivo("id,altura\n1,1.734\n2,1.702\n3,1.688\n4,1.75\n")
        col = ler_csv(p, "altura")
        self.assertTrue(all(1.0 < v < 2.5 for v in col.valores), col.valores)
        self.assertTrue(col.decimal_ambiguo is False)

    def test_para_float_formatos(self):
        self.assertEqual(_para_float("1.234,56", ","), 1234.56)
        self.assertEqual(_para_float("1,234.56", "."), 1234.56)
        self.assertEqual(_para_float("12%", "."), 12.0)
        self.assertIsNone(_para_float("N/A", "."))
        with self.assertRaises(ValueError):
            _para_float("abc", ".")

    def test_conta_ausentes_e_invalidos(self):
        # campo vazio precisa de outra coluna: linha totalmente em branco é
        # descartada pelo csv.DictReader antes de chegar aqui
        p = self._arquivo("id,v\n1,1\n2,2\n3,\n4,abc\n5,5\n")
        col = ler_csv(p, "v")
        self.assertEqual(col.valores, [1.0, 2.0, 5.0])
        self.assertEqual(col.ausentes, 1)
        self.assertEqual(len(col.invalidos), 1)
        self.assertEqual(col.invalidos[0][1], "abc")

    def test_marca_sentinela(self):
        p = self._arquivo("v\n10\n12\n-999\n11\n")
        col = ler_csv(p, "v")
        self.assertEqual(col.sentinelas, 1)

    def test_coluna_inexistente(self):
        p = self._arquivo("a\n1\n2\n")
        with self.assertRaises(ErroDeLeitura) as ctx:
            ler_csv(p, "inexistente")
        self.assertIn("não existe", str(ctx.exception))

    def test_arquivo_inexistente(self):
        with self.assertRaises(ErroDeLeitura):
            ler_csv("/caminho/que/nao/existe.csv")

    def test_arquivo_vazio(self):
        p = self._arquivo("")
        with self.assertRaises(ErroDeLeitura):
            ler_csv(p)

    def test_coluna_sem_nenhum_numero(self):
        p = self._arquivo("v\nabc\ndef\n")
        with self.assertRaises(ErroDeLeitura):
            ler_csv(p, "v")

    def test_escolhe_coluna_numerica_sozinho(self):
        p = self._arquivo("nome,valor\nana,10\nbia,20\ncau,30\n")
        col = ler_csv(p)
        self.assertEqual(col.nome, "valor")

    def test_aproveitamento(self):
        p = self._arquivo("id,v\n1,1\n2,2\n3,\n4,4\n")
        col = ler_csv(p, "v")
        self.assertAlmostEqual(col.aproveitamento, 0.75)

    def test_linha_em_branco_e_descartada_pelo_csv(self):
        # comportamento do módulo csv da biblioteca padrão, não deste projeto
        p = self._arquivo("v\n1\n2\n\n4\n")
        col = ler_csv(p, "v")
        self.assertEqual(col.total_linhas, 3)
        self.assertEqual(col.ausentes, 0)


class TestFormato(unittest.TestCase):

    def test_padrao_brasileiro(self):
        self.assertEqual(num(1234567.891), "1.234.567,89")
        self.assertEqual(num(3500.0), "3.500")
        self.assertEqual(num(-1775.0), "-1.775")

    def test_pct(self):
        self.assertEqual(pct(0.0667), "6,7%")

    def test_none_e_nan(self):
        self.assertEqual(num(None), "—")
        self.assertEqual(num(float("nan")), "—")


class TestRelatorio(unittest.TestCase):

    def test_calcular_tem_as_chaves_esperadas(self):
        r = R.calcular(D8 * 5, repeticoes=200)
        for chave in ("n", "media", "mediana", "dp", "ep", "ic_media",
                      "ic_mediana", "q1", "q3", "iqr", "mad"):
            self.assertIn(chave, r)

    def test_texto_contem_secoes(self):
        t = R.texto([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], "x", repeticoes=200)
        for secao in ("POSIÇÃO", "DISPERSÃO", "QUANTIS", "INCERTEZA",
                      "DIAGNÓSTICO", "FRASE SUGERIDA"):
            self.assertIn(secao, t)

    def test_frase_usa_mediana_quando_assimetrico(self):
        d = [1, 1, 2, 2, 3, 3, 4, 4, 5, 500]
        r = R.dicionario(d, "x", repeticoes=200)
        frase = " ".join(r["frase_sugerida"])
        self.assertIn("Mediana", frase)
        self.assertIn("não representa o caso típico", frase)

    def test_frase_usa_media_quando_bem_comportado(self):
        import random
        rng = random.Random(2)
        d = [rng.gauss(100, 10) for _ in range(300)]
        r = R.dicionario(d, "x", repeticoes=200)
        self.assertIn("Média", r["frase_sugerida"][0])

    def test_dicionario_e_serializavel(self):
        import json
        r = R.dicionario([1, 2, 3, 4, 5, 6, 7, 8], "x", repeticoes=200)
        json.dumps(r, ensure_ascii=False, default=str)   # não pode levantar

    def test_histograma_tem_uma_linha_por_classe(self):
        linhas = R.histograma(list(range(100)), classes=5)
        self.assertEqual(len(linhas), 6)          # 5 classes + rodapé

    def test_boxplot_marca_outlier(self):
        linhas = R.boxplot([10, 11, 12, 11, 10, 12, 11, 500])
        self.assertIn("o", linhas[0])


class TestCLI(unittest.TestCase):
    """A CLI escreve no terminal; aqui a saída é engolida para o log ficar limpo."""

    def _rodar(self, argv):
        buf_out, buf_err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(buf_out), contextlib.redirect_stderr(buf_err):
            return main(argv)

    def test_demo_roda(self):
        self.assertEqual(self._rodar(["--demo"]), 0)

    def test_json_roda(self):
        self.assertEqual(self._rodar(["--demo", "--formato", "json"]), 0)

    def test_arquivo_inexistente_retorna_1(self):
        self.assertEqual(self._rodar(["/nao/existe.csv"]), 1)

    def test_confianca_invalida_retorna_2(self):
        self.assertEqual(self._rodar(["--demo", "--confianca", "1.5"]), 2)

    def test_bootstrap_pequeno_demais_retorna_2(self):
        self.assertEqual(self._rodar(["--demo", "--bootstrap", "10"]), 2)

    def test_sem_argumentos_retorna_2(self):
        self.assertEqual(self._rodar([]), 2)

    def test_le_o_csv_de_exemplo(self):
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        caminho = os.path.join(base, "dados", "alugueis.csv")
        if os.path.exists(caminho):
            self.assertEqual(self._rodar([caminho, "--coluna", "aluguel"]), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
