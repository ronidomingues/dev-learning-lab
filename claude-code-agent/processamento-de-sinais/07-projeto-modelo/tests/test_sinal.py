"""Testes do `sinal` — só `unittest` da biblioteca padrão, sem pytest.

Filosofia dos testes de DSP: você quase nunca testa igualdade exata (ponto
flutuante + janelamento + interpolação), você testa **tolerância com número
justificado**. Cada tolerância abaixo tem um comentário dizendo de onde veio.

Rodar:  python -m unittest discover -s tests -v
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sinal import filtros, frequencia, geracao, io_wav, medidas  # noqa: E402
from sinal.__main__ import main  # noqa: E402
from sinal.config import Config, ConfiguracaoInvalida  # noqa: E402

TAXA = 44100


class TestIO(unittest.TestCase):
    def test_ida_e_volta_preserva_o_sinal(self):
        """WAV 16 bits deve devolver o sinal com erro < 1 LSB (2^-15)."""
        x = geracao.tom(440, 0.1, TAXA)
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "t.wav"
            io_wav.escrever_wav(p, x, TAXA)
            y, taxa = io_wav.ler_wav(p)
        self.assertEqual(taxa, TAXA)
        self.assertEqual(len(y), len(x))
        # 2^-15 = 3,05e-5 é o passo de quantização; o erro de arredondamento
        # é no máximo meio passo, mais folga numérica.
        self.assertLess(np.max(np.abs(x - y)), 2 ** -14)

    def test_arquivo_inexistente_da_erro_claro(self):
        with self.assertRaises(io_wav.ErroDeAudio):
            io_wav.ler_wav("/nao/existe/arquivo.wav")

    def test_escrita_satura_em_vez_de_dar_a_volta(self):
        """Um float 2.0 deve virar o máximo positivo, nunca um negativo."""
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "t.wav"
            io_wav.escrever_wav(p, np.array([2.0, -2.0, 0.0]), TAXA)
            y, _ = io_wav.ler_wav(p)
        self.assertGreater(y[0], 0.99)
        self.assertLess(y[1], -0.99)


class TestGeracao(unittest.TestCase):
    def test_tom_respeita_nyquist(self):
        with self.assertRaises(ValueError):
            geracao.tom(5000, 0.1, 8000, harmonicos=3)  # 15 kHz > 4 kHz

    def test_ruido_tem_o_rms_pedido(self):
        r = geracao.ruido_branco(100000, rms=0.1, semente=7)
        self.assertAlmostEqual(medidas.rms(r), 0.1, places=6)

    def test_sinal_de_teste_nao_ceifa(self):
        x = geracao.sinal_de_teste(220, 0.5, TAXA)
        self.assertLess(np.max(np.abs(x)), 1.0)


class TestFrequencia(unittest.TestCase):
    def test_tres_metodos_acertam_senoide_pura(self):
        x = geracao.tom(440, 0.5, TAXA)
        est = frequencia.estimar_f0(x, TAXA)
        for nome, valor in [("fft", est.fft), ("hps", est.hps),
                            ("acf", est.autocorrelacao)]:
            # 0,5 % ≈ 8 cents: abaixo do que um ouvido treinado distingue.
            self.assertAlmostEqual(valor, 440.0, delta=440 * 0.005,
                                   msg=f"método {nome} errou")
        self.assertTrue(est.concordam)

    def test_acerta_sinal_sujo_com_harmonicos_e_zumbido(self):
        x = geracao.sinal_de_teste(196.0, 1.0, TAXA, harmonicos=6,
                                   rms_ruido=0.03, amp_rede=0.08)
        est = frequencia.estimar_f0(x, TAXA)
        self.assertAlmostEqual(est.consenso, 196.0, delta=2.0)

    def test_hps_nao_cai_no_harmonico(self):
        """Sinal cujo 2º harmônico é MAIS forte que a fundamental —
        o caso em que a FFT ingênua erra a oitava e o HPS não deve errar."""
        t = np.arange(int(0.5 * TAXA)) / TAXA
        x = 0.3 * np.sin(2 * np.pi * 150 * t) + 1.0 * np.sin(2 * np.pi * 300 * t)
        self.assertAlmostEqual(frequencia.f0_por_fft(x, TAXA), 300.0, delta=3)
        self.assertAlmostEqual(frequencia.f0_por_hps(x, TAXA), 150.0, delta=3)

    def test_nota_e_cents(self):
        self.assertEqual(frequencia.nota_mais_proxima(440.0).nome, "A4")
        self.assertEqual(frequencia.nota_mais_proxima(261.626).nome, "C4")
        self.assertEqual(frequencia.nota_mais_proxima(82.41).nome, "E2")
        # Um semitom acima de A4 são 100 cents; meio caminho são ~50.
        n = frequencia.nota_mais_proxima(440 * 2 ** (0.25 / 12))
        self.assertAlmostEqual(n.desvio_cents, 25.0, delta=0.5)

    def test_afinacao_barroca_muda_o_nome(self):
        """415 Hz é A4 na afinação barroca e G#4 quase exato em 440."""
        self.assertEqual(frequencia.nota_mais_proxima(415.0, a4=415.0).nome, "A4")
        self.assertEqual(frequencia.nota_mais_proxima(415.0, a4=440.0).nome, "G#4")


class TestMedidas(unittest.TestCase):
    def test_fator_de_crista_de_senoide(self):
        x = np.sin(2 * np.pi * 100 * np.arange(TAXA) / TAXA)
        n = medidas.medir_niveis(x)
        # pico/RMS = √2 → 20·log10(√2) = 3,0103 dB. Constante de livro.
        self.assertAlmostEqual(n.fator_de_crista_db, 3.0103, places=3)

    def test_deteccao_de_clipping(self):
        x = np.clip(2.0 * np.sin(2 * np.pi * 100 * np.arange(1000) / TAXA), -1, 1)
        self.assertGreater(medidas.medir_niveis(x).amostras_ceifadas, 0)

    def test_snr(self):
        s = geracao.tom(440, 0.2, TAXA)
        r = geracao.ruido_branco(len(s), rms=medidas.rms(s) / 10)
        self.assertAlmostEqual(medidas.snr_db(s, r), 20.0, delta=0.5)

    def test_energia_em_faixa_encontra_o_zumbido(self):
        n = TAXA
        x = geracao.ruido_branco(n, 0.01) + geracao.zumbido(n, TAXA, 60.0, 0.5)
        frac = medidas.energia_em_faixa(x, TAXA, 55, 65)
        self.assertGreater(frac, 0.5)


class TestFiltros(unittest.TestCase):
    def test_corte_fora_de_nyquist_e_recusado(self):
        with self.assertRaises(filtros.ErroDeFiltro):
            filtros.fir_passa_baixa(30000, TAXA)   # > 22050
        with self.assertRaises(filtros.ErroDeFiltro):
            filtros.fir_passa_baixa(1000, TAXA, n_taps=200)  # par

    def test_passa_baixa_atenua_o_tom_alto(self):
        t = np.arange(TAXA) / TAXA
        baixo = np.sin(2 * np.pi * 200 * t)
        alto = np.sin(2 * np.pi * 8000 * t)
        h = filtros.fir_passa_baixa(1000, TAXA, n_taps=401)
        y = filtros.aplicar_fir(baixo + alto, h)
        # A banda de rejeição de uma janela Hamming fica ~53 dB abaixo;
        # exigimos 30 dB para dar folga às bordas da convolução.
        atenuacao = medidas.db(medidas.rms(filtros.aplicar_fir(alto, h)))
        self.assertLess(atenuacao, medidas.db(medidas.rms(alto)) - 30)
        self.assertAlmostEqual(medidas.rms(y), medidas.rms(baixo), delta=0.05)

    def test_notch_mata_o_zumbido_e_poupa_o_sinal(self):
        n = 2 * TAXA
        musica = geracao.tom(440, 2.0, TAXA, harmonicos=3)
        zum = geracao.zumbido(n, TAXA, 60.0, 0.4)
        y = filtros.remover_zumbido(musica + zum, TAXA, 60.0)
        antes = medidas.energia_em_faixa(musica + zum, TAXA, 55, 65)
        depois = medidas.energia_em_faixa(y, TAXA, 55, 65)
        self.assertLess(depois, antes / 100)
        # O sinal útil em 440 Hz deve sobreviver praticamente intacto.
        self.assertAlmostEqual(medidas.rms(y), medidas.rms(musica), delta=0.05)

    def test_filtfilt_tem_fase_zero(self):
        """Um impulso filtrado com fase zero continua simétrico em torno de si."""
        x = np.zeros(2001)
        x[1000] = 1.0
        sos = filtros.sos_passa_baixa(2000, TAXA, ordem=4)
        y = filtros.aplicar_sos(x, sos, fase_zero=True)
        self.assertEqual(int(np.argmax(np.abs(y))), 1000)

    def test_sosfilt_causal_atrasa(self):
        x = np.zeros(2001)
        x[1000] = 1.0
        sos = filtros.sos_passa_baixa(2000, TAXA, ordem=4)
        y = filtros.aplicar_sos(x, sos, fase_zero=False)
        self.assertGreater(int(np.argmax(np.abs(y))), 1000)


class TestConfig(unittest.TestCase):
    def test_n_fft_precisa_ser_potencia_de_dois(self):
        with self.assertRaises(ConfiguracaoInvalida):
            Config(n_fft=5000).validar()

    def test_variavel_de_ambiente(self):
        os.environ["SINAL_FREQ_REDE"] = "50"
        try:
            self.assertEqual(Config.do_ambiente().frequencia_rede, 50.0)
        finally:
            del os.environ["SINAL_FREQ_REDE"]

    def test_variavel_invalida_falha_alto(self):
        os.environ["SINAL_FREQ_REDE"] = "cinquenta"
        try:
            with self.assertRaises(ConfiguracaoInvalida):
                Config.do_ambiente()
        finally:
            del os.environ["SINAL_FREQ_REDE"]


class TestCLI(unittest.TestCase):
    def test_fluxo_completo_gerar_filtrar_analisar(self):
        with tempfile.TemporaryDirectory() as d:
            bruto = str(Path(d) / "bruto.wav")
            limpo = str(Path(d) / "limpo.wav")
            self.assertEqual(main(["gerar", bruto, "--f0", "329.63",
                                   "--dur", "1.0"]), 0)
            self.assertEqual(main(["filtrar", bruto, limpo,
                                   "--remover-zumbido", "--passa-alta", "80"]), 0)
            self.assertEqual(main(["analisar", limpo]), 0)

    def test_erro_de_arquivo_devolve_codigo_1(self):
        self.assertEqual(main(["analisar", "/nao/existe.wav"]), 1)


if __name__ == "__main__":
    unittest.main()
