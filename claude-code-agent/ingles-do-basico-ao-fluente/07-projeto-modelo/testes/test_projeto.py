#!/usr/bin/env python3
"""Testes do Projeto Ponte. Só `unittest` da biblioteca padrão.

Rode da raiz do projeto:
    python3 -m unittest discover -s testes -v
"""

import contextlib
import io
import json
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))

import estudo  # noqa: E402
import gerar_deck  # noqa: E402


CABECALHO = "\t".join(gerar_deck.COLUNAS)


def tsv(*linhas: str) -> str:
    return "\n".join([CABECALHO, *linhas]) + "\n"


class CasoComTempDir(unittest.TestCase):
    """Diretório temporário que se limpa sozinho.

    Usamos addCleanup em vez de self.enterContext porque enterContext só
    existe a partir do Python 3.11, e o projeto tem de rodar em 3.9+.
    """

    def temp_dir(self) -> Path:
        d = tempfile.TemporaryDirectory()
        self.addCleanup(d.cleanup)
        return Path(d.name)


class TestValidacaoDoTSV(CasoComTempDir):
    def _escrever(self, conteudo: str) -> Path:
        d = self.temp_dir()
        p = d / "frases.tsv"
        p.write_text(conteudo, encoding="utf-8")
        return p

    def test_le_uma_linha_valida(self):
        p = self._escrever(tsv("001\tA1\trotina\tI live here.\tEu moro aqui.\t/laɪv/\tlive"))
        frases = gerar_deck.ler_frases(p)
        self.assertEqual(len(frases), 1)
        self.assertEqual(frases[0]["cloze"], "live")

    def test_recusa_cloze_que_nao_esta_na_frase(self):
        p = self._escrever(tsv("001\tA1\trotina\tI live here.\tEu moro aqui.\t/laɪv/\twork"))
        with self.assertRaises(gerar_deck.ErroDeDados) as ctx:
            gerar_deck.ler_frases(p)
        self.assertIn("não aparece", str(ctx.exception))

    def test_recusa_id_repetido(self):
        p = self._escrever(tsv(
            "001\tA1\trotina\tI live here.\tEu moro aqui.\t/laɪv/\tlive",
            "001\tA1\trotina\tI work here.\tEu trabalho aqui.\t/wɜːk/\twork",
        ))
        with self.assertRaisesRegex(gerar_deck.ErroDeDados, "repetido"):
            gerar_deck.ler_frases(p)

    def test_recusa_nivel_invalido(self):
        p = self._escrever(tsv("001\tZ9\trotina\tI live here.\tEu moro aqui.\t/laɪv/\tlive"))
        with self.assertRaisesRegex(gerar_deck.ErroDeDados, "inválido"):
            gerar_deck.ler_frases(p)

    def test_recusa_numero_de_colunas_errado(self):
        p = self._escrever(tsv("001\tA1\trotina\tI live here."))
        with self.assertRaisesRegex(gerar_deck.ErroDeDados, "colunas"):
            gerar_deck.ler_frases(p)

    def test_recusa_cabecalho_diferente(self):
        p = self._escrever("id\tfrase\n001\toi\n")
        with self.assertRaisesRegex(gerar_deck.ErroDeDados, "cabeçalho"):
            gerar_deck.ler_frases(p)

    def test_arquivo_inexistente_da_mensagem_util(self):
        with self.assertRaisesRegex(gerar_deck.ErroDeDados, "não encontrado"):
            gerar_deck.ler_frases(Path("/tmp/nao-existe-mesmo-12345.tsv"))


class TestGeracaoDeCartoes(unittest.TestCase):
    frase = {
        "id": "001", "cefr": "B1", "tag": "reuniao",
        "en": "Let me check and get back to you today.",
        "pt": "Deixa eu verificar e te retorno hoje.",
        "ipa": "/ɡet bæk/", "cloze": "get back to you",
    }

    def test_cartao_de_reconhecimento_tem_tres_campos(self):
        linha = gerar_deck.cartao_reconhecimento(self.frase)
        self.assertEqual(len(linha.split("\t")), 3)

    def test_reconhecimento_inclui_ipa_no_verso(self):
        _, verso, _ = gerar_deck.cartao_reconhecimento(self.frase).split("\t")
        self.assertIn("/ɡet bæk/", verso)

    def test_cloze_envolve_o_trecho_alvo(self):
        texto, _, tags = gerar_deck.cartao_producao(self.frase).split("\t")
        self.assertIn("{{c1::get back to you}}", texto)
        self.assertIn("producao", tags)

    def test_cloze_substitui_apenas_a_primeira_ocorrencia(self):
        f = dict(self.frase, en="go and go again", cloze="go")
        texto = gerar_deck.cartao_producao(f).split("\t")[0]
        self.assertEqual(texto.count("{{c1::"), 1)

    def test_campo_seguro_neutraliza_tab_e_quebra(self):
        self.assertEqual(gerar_deck.campo_seguro("a\tb\nc"), "a b<br>c")

    def test_tabs_no_texto_nao_quebram_o_numero_de_colunas(self):
        f = dict(self.frase, pt="tem\ttab aqui")
        self.assertEqual(len(gerar_deck.cartao_reconhecimento(f).split("\t")), 3)


class TestFiltros(unittest.TestCase):
    frases = [
        {"id": "1", "cefr": "A1", "tag": "rotina", "en": "a", "pt": "a", "ipa": "", "cloze": "a"},
        {"id": "2", "cefr": "B2", "tag": "reuniao", "en": "b", "pt": "b", "ipa": "", "cloze": "b"},
        {"id": "3", "cefr": "B1", "tag": "reuniao", "en": "c", "pt": "c", "ipa": "", "cloze": "c"},
    ]

    def test_filtro_por_nivel_maximo_e_inclusivo(self):
        r = gerar_deck.filtrar(self.frases, "B1", None)
        self.assertEqual([f["id"] for f in r], ["1", "3"])

    def test_filtro_por_tag_ignora_maiusculas(self):
        r = gerar_deck.filtrar(self.frases, None, ["REUNIAO"])
        self.assertEqual([f["id"] for f in r], ["2", "3"])

    def test_filtros_combinados_podem_resultar_em_vazio(self):
        self.assertEqual(gerar_deck.filtrar(self.frases, "A1", ["reuniao"]), [])


class TestRegistroDeEstudo(CasoComTempDir):
    def setUp(self):
        self.dir = self.temp_dir()
        self.reg = self.dir / "registro.jsonl"

    def test_registrar_grava_uma_linha_json(self):
        estudo.registrar(self.reg, "2026-08-31", 40, ["escuta"], "podcast")
        linhas = self.reg.read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(linhas), 1)
        self.assertEqual(json.loads(linhas[0])["minutos"], 40)

    def test_registrar_e_append_e_nao_sobrescreve(self):
        estudo.registrar(self.reg, "2026-08-30", 30, ["fala"], "")
        estudo.registrar(self.reg, "2026-08-31", 40, ["escuta"], "")
        self.assertEqual(len(estudo.ler_registro(self.reg)), 2)

    def test_recusa_minutos_zero_ou_negativos(self):
        with self.assertRaisesRegex(estudo.ErroDeDados, "maior que zero"):
            estudo.registrar(self.reg, "2026-08-31", 0, ["escuta"], "")

    def test_recusa_valor_absurdo_de_minutos(self):
        with self.assertRaisesRegex(estudo.ErroDeDados, "12 h"):
            estudo.registrar(self.reg, "2026-08-31", 1000, ["escuta"], "")

    def test_recusa_habilidade_desconhecida(self):
        with self.assertRaisesRegex(estudo.ErroDeDados, "desconhecida"):
            estudo.registrar(self.reg, "2026-08-31", 30, ["telepatia"], "")

    def test_recusa_data_malformada(self):
        with self.assertRaisesRegex(estudo.ErroDeDados, "data inválida"):
            estudo.registrar(self.reg, "31/08/2026", 30, ["escuta"], "")

    def test_registro_inexistente_devolve_lista_vazia(self):
        self.assertEqual(estudo.ler_registro(self.dir / "nao-existe.jsonl"), [])

    def test_linha_corrompida_e_ignorada_sem_derrubar(self):
        self.reg.write_text(
            '{"data":"2026-08-30","minutos":30,"habilidades":["fala"],"nota":""}\n'
            "{lixo que não é json\n"
            '{"data":"2026-08-31","minutos":40,"habilidades":["escuta"],"nota":""}\n',
            encoding="utf-8",
        )
        self.assertEqual(len(estudo.ler_registro(self.reg)), 2)


class TestSequenciaEProjecao(unittest.TestCase):
    def test_sequencia_conta_dias_seguidos_ate_hoje(self):
        hoje = date(2026, 8, 31)
        dias = {"2026-08-29", "2026-08-30", "2026-08-31"}
        self.assertEqual(estudo.sequencia_atual(dias, hoje), 3)

    def test_sequencia_nao_zera_se_hoje_ainda_nao_estudou(self):
        hoje = date(2026, 8, 31)
        dias = {"2026-08-29", "2026-08-30"}
        self.assertEqual(estudo.sequencia_atual(dias, hoje), 2)

    def test_sequencia_quebra_com_buraco(self):
        hoje = date(2026, 8, 31)
        dias = {"2026-08-25", "2026-08-30", "2026-08-31"}
        self.assertEqual(estudo.sequencia_atual(dias, hoje), 2)

    def test_sequencia_vazia_e_zero(self):
        self.assertEqual(estudo.sequencia_atual(set(), date(2026, 8, 31)), 0)

    def test_maior_sequencia_encontra_o_melhor_trecho(self):
        dias = {"2026-08-01", "2026-08-02", "2026-08-03", "2026-08-10", "2026-08-11"}
        self.assertEqual(estudo.maior_sequencia(dias), 3)

    def test_minutos_por_dia_soma_sessoes_do_mesmo_dia(self):
        sessoes = [
            {"data": "2026-08-31", "minutos": 20, "habilidades": ["escuta"]},
            {"data": "2026-08-31", "minutos": 25, "habilidades": ["fala"]},
        ]
        self.assertEqual(estudo.minutos_por_dia(sessoes), {"2026-08-31": 45})

    def test_projecao_sem_ritmo_nao_divide_por_zero(self):
        self.assertIn("sem ritmo", estudo.projecao(10, 600, 0))

    def test_projecao_reconhece_meta_atingida(self):
        self.assertIn("já atingida", estudo.projecao(700, 600, 40))

    def test_projecao_dobrar_o_ritmo_corta_o_prazo_pela_metade(self):
        import re
        def meses(texto):
            return float(re.search(r"~([\d.]+) meses", texto).group(1))
        lento = meses(estudo.projecao(0, 600, 30))
        rapido = meses(estudo.projecao(0, 600, 60))
        self.assertAlmostEqual(lento / rapido, 2.0, places=1)


class TestRelatorio(unittest.TestCase):
    cfg = {"nivel_alvo": "B2", "horas_por_nivel": {"B2": 600}, "meta_diaria_min": 40}

    def test_relatorio_vazio_orienta_o_primeiro_passo(self):
        texto = estudo.relatorio(self.cfg, [], 14, date(2026, 8, 31))
        self.assertIn("registrar", texto)

    def test_relatorio_soma_horas_e_mostra_habilidades(self):
        sessoes = [
            {"data": "2026-08-30", "minutos": 60, "habilidades": ["escuta"], "nota": ""},
            {"data": "2026-08-31", "minutos": 60, "habilidades": ["fala", "escuta"], "nota": ""},
        ]
        texto = estudo.relatorio(self.cfg, sessoes, 14, date(2026, 8, 31))
        self.assertIn("2.0 h", texto)
        self.assertIn("escuta", texto)
        self.assertIn("fala", texto)

    def test_sessao_com_duas_habilidades_divide_o_tempo(self):
        sessoes = [{"data": "2026-08-31", "minutos": 60, "habilidades": ["fala", "escuta"], "nota": ""}]
        texto = estudo.relatorio(self.cfg, sessoes, 14, date(2026, 8, 31))
        self.assertEqual(texto.count("0.5 h"), 2)

    def test_sessao_sem_habilidade_nao_quebra_o_relatorio(self):
        sessoes = [{"data": "2026-08-31", "minutos": 30, "habilidades": [], "nota": ""}]
        texto = estudo.relatorio(self.cfg, sessoes, 14, date(2026, 8, 31))
        self.assertIn("não informado", texto)


class TestIntegracao(CasoComTempDir):
    """Roda o gerador de ponta a ponta sobre os dados reais do projeto."""

    def test_dados_reais_do_projeto_sao_validos(self):
        cfg = gerar_deck.carregar_config(RAIZ / "config.json")
        frases = gerar_deck.ler_frases(RAIZ / cfg["arquivo_de_frases"])
        self.assertGreaterEqual(len(frases), 50)

    def test_gera_dois_arquivos_com_uma_linha_por_frase(self):
        destino = self.temp_dir()
        cfg = gerar_deck.carregar_config(RAIZ / "config.json")
        frases = gerar_deck.ler_frases(RAIZ / cfg["arquivo_de_frases"])
        gerar_deck.gerar(frases, destino, escrever=True)
        for nome in ("anki-reconhecimento.tsv", "anki-producao.tsv"):
            linhas = (destino / nome).read_text(encoding="utf-8").strip().splitlines()
            self.assertEqual(len(linhas), len(frases), nome)
            for linha in linhas:
                self.assertEqual(len(linha.split("\t")), 3, f"{nome}: {linha[:40]}")

    def test_dry_run_nao_escreve_nada(self):
        destino = self.temp_dir()
        frases = gerar_deck.ler_frases(RAIZ / "deck/frases-nucleo.tsv")
        gerar_deck.gerar(frases, destino, escrever=False)
        self.assertEqual(list(destino.iterdir()), [])

    def test_main_devolve_zero_no_caminho_feliz(self):
        destino = self.temp_dir()
        with contextlib.redirect_stdout(io.StringIO()):
            codigo = gerar_deck.main(["--out", str(destino)])
        self.assertEqual(codigo, 0)

    def test_main_devolve_um_quando_o_filtro_zera(self):
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            codigo = gerar_deck.main(["--max-cefr", "A1", "--tag", "entrevista", "--dry-run"])
        self.assertEqual(codigo, 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
