"""
Testes do simulador. Rode com:   python3 -m unittest -v

Filosofia dos testes: eles NAO travam o valor dos indicadores (que mudam
toda semana), travam as REGRAS — tabela de IR, tabela de IOF, ordem de
incidencia, aniversario da poupanca, isencao de custodia, come-cotas.
Regra muda por lei; indicador muda por decisao do Copom.
"""

import unittest

import indicadores as ind
import produtos as prod
import tributos as trib
import carteira


class TestIR(unittest.TestCase):
    def test_faixas_da_tabela_regressiva(self):
        self.assertEqual(trib.aliquota_ir(1), 0.225)
        self.assertEqual(trib.aliquota_ir(180), 0.225)
        self.assertEqual(trib.aliquota_ir(181), 0.200)
        self.assertEqual(trib.aliquota_ir(360), 0.200)
        self.assertEqual(trib.aliquota_ir(361), 0.175)
        self.assertEqual(trib.aliquota_ir(720), 0.175)
        self.assertEqual(trib.aliquota_ir(721), 0.150)
        self.assertEqual(trib.aliquota_ir(10_000), 0.150)

    def test_um_dia_a_mais_muda_a_aliquota(self):
        """O caso que custa dinheiro de verdade: resgatar no dia 180."""
        r = 1000.0
        no_dia_180 = trib.liquido(r, 180)
        no_dia_181 = trib.liquido(r, 181)
        self.assertAlmostEqual(no_dia_181 - no_dia_180, 25.0, places=6)

    def test_prazo_negativo_e_erro(self):
        with self.assertRaises(ValueError):
            trib.aliquota_ir(-1)

    def test_isento_nao_paga(self):
        self.assertEqual(trib.imposto_renda(1000, 30, isento=True), 0.0)

    def test_prejuizo_nao_gera_imposto(self):
        self.assertEqual(trib.imposto_renda(-500, 400), 0.0)
        self.assertEqual(trib.iof(-500, 5), 0.0)


class TestIOF(unittest.TestCase):
    def test_tabela_e_decrescente(self):
        valores = [trib.fator_iof(d) for d in range(1, 31)]
        self.assertTrue(all(a >= b for a, b in zip(valores, valores[1:])))

    def test_zera_no_trigesimo_dia(self):
        self.assertGreater(trib.fator_iof(29), 0)
        self.assertEqual(trib.fator_iof(30), 0.0)
        self.assertEqual(trib.fator_iof(45), 0.0)

    def test_iof_reduz_a_base_do_ir(self):
        """Ordem legal: IOF primeiro, IR sobre o que sobrou."""
        rendimento = 100.0
        esperado_iof = 100 * 0.50            # 15 dias -> 50%
        esperado_ir = (100 - esperado_iof) * 0.225
        self.assertAlmostEqual(trib.iof(rendimento, 15), esperado_iof)
        self.assertAlmostEqual(trib.imposto_renda(rendimento, 15), esperado_ir)
        self.assertAlmostEqual(trib.liquido(rendimento, 15),
                               100 - esperado_iof - esperado_ir)

    def test_resgate_em_um_dia_quase_zera_o_ganho(self):
        self.assertAlmostEqual(trib.liquido(100, 1), 100 * 0.04 * (1 - 0.225))


class TestEquivalencia(unittest.TestCase):
    def test_lci_90_pct_em_um_ano(self):
        """90% do CDI isento equivale a ~109,1% do CDI tributado (17,5%)."""
        self.assertAlmostEqual(trib.percentual_cdi_equivalente(0.90, 365), 0.90 / 0.825)

    def test_prazo_menor_exige_mais_do_tributado(self):
        curto = trib.percentual_cdi_equivalente(0.90, 100)
        longo = trib.percentual_cdi_equivalente(0.90, 1000)
        self.assertGreater(curto, longo)


class TestConversaoDeTaxas(unittest.TestCase):
    def test_anualizar_e_inverso_de_fator_periodo(self):
        f = prod.fator_periodo(0.139, 365)
        self.assertAlmostEqual(prod.anualizar(f, 365), 0.139, places=10)

    def test_juro_real_nao_e_subtracao(self):
        real = ind.juro_real(0.1390, 0.0444)
        self.assertNotAlmostEqual(real, 0.1390 - 0.0444, places=4)
        self.assertAlmostEqual(real, 1.1390 / 1.0444 - 1)

    def test_dias_invalidos(self):
        with self.assertRaises(ValueError):
            prod.fator_periodo(0.10, -5)
        with self.assertRaises(ValueError):
            prod.anualizar(1.1, 0)


class TestPoupanca(unittest.TestCase):
    def test_aniversario_mensal_penaliza_resgate_antecipado(self):
        p = prod.Poupanca()
        self.assertEqual(p.simular(6000, 29).liquido, 0.0)
        self.assertGreater(p.simular(6000, 30).liquido, 0.0)

    def test_regra_muda_abaixo_de_85_pct(self):
        original = ind.SELIC_META
        try:
            ind.SELIC_META = 0.08
            self.assertLess(ind.poupanca_mensal(), 0.005 + ind.TR_MENSAL)
        finally:
            ind.SELIC_META = original

    def test_poupanca_e_isenta(self):
        r = prod.Poupanca().simular(6000, 365)
        self.assertEqual(r.ir, 0.0)
        self.assertEqual(r.iof, 0.0)


class TestTesouro(unittest.TestCase):
    def test_isencao_de_custodia_ate_10_mil(self):
        t = prod.TesouroSelic()
        self.assertEqual(t.custos(9_999, 365), 0.0)
        self.assertAlmostEqual(t.custos(20_000, 365), 10_000 * 0.002, places=6)

    def test_ipca_mais_usa_produto_e_nao_soma(self):
        t = prod.IPCAMais(taxa_real_aa=0.0665, inflacao_esperada=0.05)
        self.assertAlmostEqual(t.taxa_bruta_aa(), 1.0665 * 1.05 - 1)
        self.assertGreater(t.taxa_bruta_aa(), 0.0665 + 0.05)

    def test_prefixado_paga_custodia_sem_isencao(self):
        p = prod.Prefixado(taxa_aa=0.14)
        self.assertGreater(p.custos(6_000, 365), 0.0)


class TestFundoDI(unittest.TestCase):
    def test_come_cotas_e_taxa_derrubam_o_liquido(self):
        cdb = prod.PosFixadoCDI(percentual_cdi=1.0).simular(6000, 730)
        fundo = prod.FundoDI(taxa_admin_aa=0.005).simular(6000, 730)
        self.assertLess(fundo.liquido, cdb.liquido)

    def test_taxa_maior_rende_menos(self):
        barato = prod.FundoDI(taxa_admin_aa=0.005).simular(6000, 1825)
        caro = prod.FundoDI(taxa_admin_aa=0.020).simular(6000, 1825)
        self.assertLess(caro.liquido, barato.liquido)

    def test_conta_eventos_de_come_cotas(self):
        self.assertEqual(trib.datas_come_cotas(181), 0)
        self.assertEqual(trib.datas_come_cotas(365), 2)
        self.assertEqual(trib.datas_come_cotas(730), 4)


class TestCarencia(unittest.TestCase):
    def test_marca_resgate_bloqueado(self):
        lci = prod.PosFixadoCDI(percentual_cdi=0.88, isento_ir=True, carencia_dias=180)
        self.assertIn("RESGATE BLOQUEADO", lci.simular(6000, 100).observacao)
        self.assertEqual(lci.simular(6000, 200).observacao, "")


class TestRegressaoDeCenario(unittest.TestCase):
    """Valores publicados no material. Se a regra mudar, estes quebram."""

    def test_cdb_100_cdi_um_ano_seis_mil(self):
        r = prod.PosFixadoCDI(percentual_cdi=1.0).simular(6000, 365)
        self.assertAlmostEqual(r.liquido, 688.05, places=2)
        self.assertAlmostEqual(r.taxa_liquida_aa, 0.1147, places=4)

    def test_poupanca_um_ano_seis_mil(self):
        r = prod.Poupanca().simular(6000, 365)
        self.assertAlmostEqual(r.liquido, 500.58, places=2)

    def test_ordem_do_ranking_em_um_ano(self):
        res = {p.nome: p.simular(6000, 365).liquido for p in prod.catalogo()}
        self.assertGreater(res["CDB 110% CDI (banco medio)"],
                           res["LCI/LCA 88% CDI (isenta de IR)"])
        self.assertGreater(res["LCI/LCA 88% CDI (isenta de IR)"],
                           res["CDB 100% CDI (banco grande)"])
        self.assertGreater(res["CDB 100% CDI (banco grande)"], res["Poupanca"])


class TestEntradas(unittest.TestCase):
    def test_valor_negativo_e_rejeitado(self):
        with self.assertRaises(SystemExit):
            carteira.main(["--valor", "-100"])

    def test_prazo_invalido_e_rejeitado(self):
        with self.assertRaises(SystemExit):
            carteira.main(["--prazos", "abc"])

    def test_config_inexistente(self):
        with self.assertRaises(SystemExit):
            carteira.aplicar_config("/caminho/que/nao/existe.json")

    def test_principal_zero(self):
        with self.assertRaises(ValueError):
            prod.TesouroSelic().simular(0, 365)


if __name__ == "__main__":
    unittest.main()
