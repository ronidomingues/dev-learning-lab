"""Testes do `cosmos`.

FILOSOFIA DESTES TESTES — e ela difere da do projeto anterior:

No projeto de áudio, testávamos comportamento. Aqui testamos **física**. Cada
asserção compara com um número que se pode calcular à mão, com lápis, a partir
de uma fórmula publicada. Um teste que só compara com "o que o código deu ontem"
não protege contra um erro de constante ou de unidade — e erro de unidade já
derrubou sonda (Mars Climate Orbiter, 1999).

Rodar:  python -m unittest discover -s tests -v
"""

import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cosmos import (aquisicao, deteccao, dispersao, doppler,  # noqa: E402
                    pulsar, ruido)
from cosmos.__main__ import main  # noqa: E402
from cosmos.constantes import C_LUZ, K_BOLTZMANN, K_DISPERSAO  # noqa: E402


class TestConstantes(unittest.TestCase):
    """As constantes são exatas por definição do SI — devem bater ao último dígito."""

    def test_velocidade_da_luz_exata(self):
        self.assertEqual(C_LUZ, 299_792_458.0)

    def test_boltzmann_exata(self):
        self.assertEqual(K_BOLTZMANN, 1.380_649e-23)

    def test_constante_de_dispersao(self):
        # Convenção da comunidade de pulsares (Manchester & Taylor 1977).
        self.assertAlmostEqual(K_DISPERSAO, 4148.808, places=3)


class TestRuido(unittest.TestCase):

    def test_potencia_kTB(self):
        """P = k·T·B, conta direta: 1,380649e-23 × 25 × 1e8 = 3,4516e-14 W."""
        self.assertAlmostEqual(ruido.potencia_de_ruido(25, 1e8), 3.4516225e-14,
                               places=20)

    def test_radiometro_valor_de_mao(self):
        """ΔT = 25/√(1×1e8×60) = 25/77459,67 = 3,2275e-4 K."""
        self.assertAlmostEqual(ruido.radiometro(25, 1e8, 60, 1),
                               25/np.sqrt(6e9), places=12)

    def test_radiometro_escala_com_raiz_do_tempo(self):
        """Quadruplicar o tempo deve dividir ΔT por exatamente 2."""
        a = ruido.radiometro(30, 1e8, 10)
        b = ruido.radiometro(30, 1e8, 40)
        self.assertAlmostEqual(a/b, 2.0, places=10)

    def test_duas_polarizacoes_ganham_raiz_de_dois(self):
        a = ruido.radiometro(30, 1e8, 60, n_polarizacoes=1)
        b = ruido.radiometro(30, 1e8, 60, n_polarizacoes=2)
        self.assertAlmostEqual(a/b, np.sqrt(2), places=10)

    def test_tempo_necessario_inverte_o_radiometro(self):
        """tempo_necessario e radiometro têm de ser inversos exatos."""
        t = ruido.tempo_necessario(30, 1e8, 1e-3, n_sigma=5, n_polarizacoes=2)
        self.assertAlmostEqual(5*ruido.radiometro(30, 1e8, t, 2), 1e-3, places=12)

    def test_temperatura_de_sistema_soma(self):
        self.assertAlmostEqual(
            ruido.temperatura_de_sistema(20.0, 3.0, 2.0, 5.0), 30.0)

    def test_ruido_gerado_tem_a_potencia_certa(self):
        """A variância das amostras deve ser k·T·B, dentro do erro estatístico."""
        p_esperada = ruido.potencia_de_ruido(25, 1e8)
        x = ruido.gerar_ruido(200_000, 25, 1e8, semente=1)
        # Erro relativo da variância amostral ≈ √(2/N) = 0,45 % para N=200k.
        # Tolerância de 2 % dá ~4 sigma de folga.
        self.assertAlmostEqual(x.var()/p_esperada, 1.0, delta=0.02)

    def test_integracao_melhora_por_raiz_de_n(self):
        x = ruido.gerar_ruido(100_000, 25, 1e8, semente=2)
        y = ruido.integrar(x, 100)
        self.assertAlmostEqual(x.std()/y.std(), 10.0, delta=0.6)   # √100 = 10

    def test_integrar_recusa_sinal_curto(self):
        with self.assertRaises(ValueError):
            ruido.integrar(np.ones(5), 10)

    def test_valores_invalidos(self):
        with self.assertRaises(ValueError):
            ruido.potencia_de_ruido(-1, 1e8)
        with self.assertRaises(ValueError):
            ruido.radiometro(25, 1e8, 0)


class TestDispersao(unittest.TestCase):

    def test_atraso_conta_de_mao(self):
        """DM=50, 400 vs 800 MHz:
        4148,808 × 50 × (1/400² − 1/800²) = 4148,808 × 50 × 4,6875e−6 = 0,972377 s
        """
        self.assertAlmostEqual(dispersao.atraso_dispersao(50, 400, 800),
                               0.9723768750, places=9)

    def test_lei_inversa_do_quadrado(self):
        """Dobrar a frequência divide o atraso absoluto por exatamente 4."""
        a = dispersao.atraso_dispersao(30, 400)
        b = dispersao.atraso_dispersao(30, 800)
        self.assertAlmostEqual(a/b, 4.0, places=10)

    def test_atraso_proporcional_ao_dm(self):
        self.assertAlmostEqual(dispersao.atraso_dispersao(100, 400, 800),
                               2*dispersao.atraso_dispersao(50, 400, 800),
                               places=12)

    def test_ida_e_volta_dm(self):
        for dm in (0.5, 50.0, 1200.0):
            t = dispersao.atraso_dispersao(dm, 400, 800)
            self.assertAlmostEqual(
                dispersao.dm_a_partir_do_atraso(t, 400, 800), dm, places=9)

    def test_dm_negativo_recusado(self):
        with self.assertRaises(ValueError):
            dispersao.atraso_dispersao(-1, 400)

    def test_dedispersar_desfaz_dispersar(self):
        """Aplicar e desfazer com o mesmo DM tem de realinhar os canais."""
        n_canais, n = 32, 4000
        freqs = np.linspace(400, 800, n_canais)
        limpo = np.zeros((n_canais, n))
        limpo[:, 2000] = 1.0                      # um pulso, alinhado em todos
        disperso = dispersao.aplicar_dispersao(limpo, freqs, 20.0, 1e-3)
        serie = dispersao.dedispersar(disperso, freqs, 20.0, 1e-3)
        # Todo o sinal (32 canais × 1,0) tem de reaparecer numa amostra só.
        self.assertEqual(int(np.argmax(serie)), 2000)
        self.assertAlmostEqual(serie.max(), float(n_canais), delta=1.0)

    def test_dm_errado_borra_o_pulso(self):
        """Dedispersar com DM errado tem de ESPALHAR o pulso e baixar o pico."""
        n_canais, n = 32, 4000
        freqs = np.linspace(400, 800, n_canais)
        limpo = np.zeros((n_canais, n)); limpo[:, 2000] = 1.0
        disperso = dispersao.aplicar_dispersao(limpo, freqs, 20.0, 1e-3)
        certo = dispersao.dedispersar(disperso, freqs, 20.0, 1e-3).max()
        errado = dispersao.dedispersar(disperso, freqs, 60.0, 1e-3).max()
        self.assertGreater(certo, 5*errado)

    def test_forma_incompativel_e_recusada(self):
        with self.assertRaises(ValueError):
            dispersao.dedispersar(np.zeros((4, 100)), np.array([400., 800.]),
                                  10.0, 1e-3)


class TestPulsar(unittest.TestCase):

    def test_perfil_tem_pico_na_fase_pedida(self):
        p = pulsar.perfil_gaussiano(1000, largura_fracao=0.02, fase_pico=0.35)
        self.assertAlmostEqual(np.argmax(p)/1000, 0.35, delta=0.01)

    def test_perfil_e_circular(self):
        """Um pulso na fase 0,0 não pode ser cortado pela borda do período."""
        p = pulsar.perfil_gaussiano(1000, largura_fracao=0.02, fase_pico=0.0)
        self.assertAlmostEqual(p[0], 1.0, places=6)
        self.assertAlmostEqual(p[1], p[-1], places=6)   # simétrico em torno de 0

    def test_folding_recupera_pulso_invisivel(self):
        """O caso central do projeto: pulso 26 dB abaixo do ruído, recuperado."""
        espectro, freqs = pulsar.sintetizar_observacao(
            periodo_s=0.5, dm=30.0, duracao_s=40.0, amplitude_pulso=0.05,
            semente=3)
        serie = dispersao.dedispersar(espectro, freqs, 30.0, 1e-3)
        perfil = pulsar.dobrar(serie, 0.5, 1e-3, 64)
        self.assertGreater(pulsar.snr_perfil(perfil), 8.0)

    def test_periodo_errado_nao_detecta(self):
        """Dobrar num período errado por 10 % tem de destruir a detecção."""
        espectro, freqs = pulsar.sintetizar_observacao(
            periodo_s=0.5, dm=30.0, duracao_s=40.0, semente=3)
        serie = dispersao.dedispersar(espectro, freqs, 30.0, 1e-3)
        certo = pulsar.snr_perfil(pulsar.dobrar(serie, 0.5, 1e-3, 64))
        errado = pulsar.snr_perfil(pulsar.dobrar(serie, 0.55, 1e-3, 64))
        self.assertGreater(certo, 2.5*errado)

    def test_snr_cresce_com_raiz_da_duracao(self):
        """Quadruplicar a observação deve aproximadamente dobrar a SNR."""
        snrs = []
        for dur in (20.0, 80.0):
            espectro, freqs = pulsar.sintetizar_observacao(
                periodo_s=0.5, dm=30.0, duracao_s=dur, amplitude_pulso=0.04,
                semente=11)
            serie = dispersao.dedispersar(espectro, freqs, 30.0, 1e-3)
            snrs.append(pulsar.snr_perfil(pulsar.dobrar(serie, 0.5, 1e-3, 64)))
        # Tolerância larga: a SNR estimada de uma única realização flutua.
        self.assertAlmostEqual(snrs[1]/snrs[0], 2.0, delta=0.7)

    def test_dedispersar_ganha_sobre_somar_cru(self):
        espectro, freqs = pulsar.sintetizar_observacao(semente=5)
        com = pulsar.snr_perfil(pulsar.dobrar(
            dispersao.dedispersar(espectro, freqs, 50.0, 1e-3), 0.714, 1e-3, 64))
        sem = pulsar.snr_perfil(pulsar.dobrar(
            espectro.sum(axis=0), 0.714, 1e-3, 64))
        self.assertGreater(com, 3*sem)

    def test_busca_de_dm_encontra_o_verdadeiro(self):
        espectro, freqs = pulsar.sintetizar_observacao(dm=50.0, semente=5)
        r = pulsar.buscar_dm(espectro, freqs, np.arange(0, 101, 5.0),
                             0.714, 1e-3)
        # Passo da grade é 5; exigir o valor exato seria testar sorte, não código.
        self.assertLessEqual(abs(r.dm - 50.0), 5.0)

    def test_folding_recusa_n_fase_grande_demais(self):
        with self.assertRaises(ValueError):
            pulsar.dobrar(np.zeros(50), 1.0, 1e-3, n_fase=4096)


class TestDoppler(unittest.TestCase):

    def test_sinal_do_desvio(self):
        """Afastar-se BAIXA a frequência (redshift). Sinal negativo."""
        self.assertLess(doppler.desvio_doppler(8.42e9, +1000), 0)
        self.assertGreater(doppler.desvio_doppler(8.42e9, -1000), 0)

    def test_valor_de_mao_banda_x(self):
        """8,42e9 × 1000 / 299792458 = 28086,1 Hz por km/s."""
        self.assertAlmostEqual(abs(doppler.desvio_doppler(8.42e9, 1000)),
                               8.42e9*1000/C_LUZ, places=6)

    def test_ida_e_volta_velocidade(self):
        for v in (-30000.0, 1.0, 20000.0):
            d = doppler.desvio_doppler(8.42e9, v)
            self.assertAlmostEqual(
                doppler.velocidade_a_partir_do_desvio(8.42e9, d), v, places=6)

    def test_duas_vias_dobra(self):
        self.assertAlmostEqual(doppler.doppler_duas_vias(8.42e9, 1000),
                               2*doppler.desvio_doppler(8.42e9, 1000), places=9)

    def test_estimador_de_frequencia(self):
        fs = 1e4
        s = doppler.gerar_portadora_com_doppler(8192, fs, 1234.5)
        self.assertAlmostEqual(doppler.estimar_frequencia(s, fs), 1234.5, delta=1.0)

    def test_estimador_aceita_frequencia_negativa(self):
        """Sinal complexo distingue aproximação de afastamento — o teste prova."""
        fs = 1e4
        s = doppler.gerar_portadora_com_doppler(8192, fs, -800.0)
        self.assertAlmostEqual(doppler.estimar_frequencia(s, fs), -800.0, delta=1.0)

    def test_estimador_de_deriva(self):
        fs = 1e4
        s = doppler.gerar_portadora_com_doppler(20000, fs, 1234.5,
                                                deriva_hz_por_s=25.0)
        _, deriva = doppler.estimar_deriva(s, fs, n_blocos=8)
        self.assertAlmostEqual(deriva, 25.0, delta=1.0)

    def test_correcao_traz_para_banda_base(self):
        fs = 1e4
        s = doppler.gerar_portadora_com_doppler(8192, fs, 2000.0,
                                                deriva_hz_por_s=10.0)
        corrigido = doppler.corrigir_doppler(s, fs, 2000.0, 10.0)
        # Depois de corrigir, sobra uma constante: frequência ~0 e fase fixa.
        self.assertAlmostEqual(abs(doppler.estimar_frequencia(corrigido, fs)),
                               0.0, delta=1.0)


class TestAquisicao(unittest.TestCase):

    def test_comprimento_de_sequencia_m(self):
        for grau in (3, 5, 10):
            self.assertEqual(len(aquisicao.lfsr_sequencia_m(grau)), 2**grau - 1)

    def test_balanceamento_de_golomb(self):
        """Propriedade 1: exatamente 2^(n−1) uns e 2^(n−1)−1 zeros."""
        for grau in (5, 10):
            b = aquisicao.lfsr_sequencia_m(grau)
            self.assertEqual(int(b.sum()), 2**(grau-1))

    def test_autocorrelacao_de_dois_niveis(self):
        """Propriedade 2 (a que importa): pico N, e EXATAMENTE −1 no resto.

        É esta propriedade que torna a sequência-m melhor que ruído verdadeiro
        para sincronização: ruído real teria laterais flutuando em ±√N.
        """
        for grau in (5, 10):
            c = aquisicao.codigo_pn(grau)
            ac = aquisicao.autocorrelacao_circular(c)
            n = len(c)
            self.assertAlmostEqual(ac[0], float(n), places=6)
            self.assertTrue(np.allclose(ac[1:], -1.0, atol=1e-6),
                            f"grau {grau}: laterais não são todas −1")

    def test_estado_todo_zero_recusado(self):
        with self.assertRaises(ValueError):
            aquisicao.lfsr_sequencia_m(5, estado_inicial=0)

    def test_ganho_de_processamento(self):
        self.assertAlmostEqual(aquisicao.ganho_de_processamento_db(1023),
                               30.0988, places=3)

    def test_aquisicao_acha_atraso_e_doppler(self):
        c = aquisicao.codigo_pn(10); n = len(c); fs = 1.023e6
        atraso, fd = 317, 1500.0
        t = np.arange(n)/fs
        rng = np.random.default_rng(7)
        sinal = np.roll(c, atraso)*np.exp(2j*np.pi*fd*t)
        rx = 0.316*sinal + (rng.standard_normal(n) +
                            1j*rng.standard_normal(n))/np.sqrt(2)   # −10 dB
        d, f_est, razao, _ = aquisicao.adquirir(rx, c, fs, 3000, 250)
        self.assertEqual(d, atraso)
        self.assertLessEqual(abs(f_est - fd), 250)
        self.assertGreater(razao, 5.0)

    def test_acumulacao_resgata_caso_que_falha_com_um_periodo(self):
        """A −20 dB, 1 período falha e 4 acertam. É o teste que documenta o
        motivo de a função `adquirir_acumulado` existir."""
        c = aquisicao.codigo_pn(10); n = len(c); fs = 1.023e6
        atraso, fd = 317, 1500.0
        rng = np.random.default_rng(7)
        n_tot = n*4
        t = np.arange(n_tot)/fs
        sinal = np.tile(np.roll(c, atraso), 4)*np.exp(2j*np.pi*fd*t)
        rx = 0.1*sinal + (rng.standard_normal(n_tot) +
                          1j*rng.standard_normal(n_tot))/np.sqrt(2)   # −20 dB
        d, f_est, _, _ = aquisicao.adquirir_acumulado(rx, c, fs, 3000, 250, 4)
        self.assertEqual(d, atraso)
        self.assertLessEqual(abs(f_est - fd), 250)

    def test_sinal_curto_recusado(self):
        c = aquisicao.codigo_pn(5)
        with self.assertRaises(ValueError):
            aquisicao.adquirir(np.zeros(10, dtype=complex), c, 1e6, 1000, 100)


class TestDeteccao(unittest.TestCase):

    def test_valores_classicos_de_sigma(self):
        """1 sigma ≈ 15,87 %; 3 sigma ≈ 1/741; 5 sigma ≈ 1/3,49 milhões."""
        self.assertAlmostEqual(deteccao.probabilidade_falso_alarme(1.0),
                               0.158655, places=5)
        self.assertAlmostEqual(deteccao.probabilidade_falso_alarme(3.0),
                               1.3499e-3, places=6)
        self.assertAlmostEqual(deteccao.probabilidade_falso_alarme(5.0),
                               2.8665e-7, places=10)

    def test_efeito_das_multiplas_tentativas(self):
        """5 sigma em 1 milhão de tentativas deixa de ser convincente."""
        p = deteccao.probabilidade_falso_alarme(5.0, 1_000_000)
        self.assertGreater(p, 0.2)
        self.assertLess(p, 0.3)

    def test_limiar_inverte_a_probabilidade(self):
        for n in (1, 1000, 10**6):
            limiar = deteccao.limiar_para_falso_alarme(0.01, n)
            self.assertAlmostEqual(
                deteccao.probabilidade_falso_alarme(limiar, n), 0.01, places=6)

    def test_mais_tentativas_exigem_limiar_maior(self):
        self.assertLess(deteccao.limiar_para_falso_alarme(0.01, 1),
                        deteccao.limiar_para_falso_alarme(0.01, 10**6))

    def test_veredito_muda_com_as_tentativas(self):
        """A MESMA SNR de 5 sigma: detecção com 1 tentativa, ruído com 1e6."""
        self.assertEqual(deteccao.resumo_deteccao(5.0, 1)["veredito"], "detecção")
        self.assertIn("ruído", deteccao.resumo_deteccao(5.0, 10**6)["veredito"])

    def test_ganho_de_integracao(self):
        self.assertAlmostEqual(deteccao.snr_necessaria(0.1, 10_000), 10.0,
                               places=9)


class TestCLI(unittest.TestCase):

    def test_radiometro(self):
        self.assertEqual(main(["radiometro", "--tau", "10"]), 0)

    def test_dispersao(self):
        self.assertEqual(main(["dispersao", "--dm", "25"]), 0)

    def test_pulsar_curto(self):
        self.assertEqual(main(["pulsar", "--duracao", "20", "--canais", "16",
                               "--dm-passo", "10"]), 0)

    def test_enlace(self):
        self.assertEqual(main(["enlace", "--snr", "-10", "--periodos", "2"]), 0)

    def test_erro_devolve_codigo_1(self):
        self.assertEqual(main(["radiometro", "--tau", "-5"]), 1)


if __name__ == "__main__":
    unittest.main()
