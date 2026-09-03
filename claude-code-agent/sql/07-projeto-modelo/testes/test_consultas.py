#!/usr/bin/env python3
"""Testes do historiador: esquema, restrições, anomalias plantadas e consultas.

Só `unittest` da biblioteca padrão. Rodar da raiz do projeto:

    python3 -m unittest discover -s testes -v

Um projeto de dados sem teste é uma planilha com pretensões. O que se testa
aqui não é "o SQL roda" — é que ele responde a coisa CERTA sobre um dado cuja
resposta certa nós conhecemos, porque nós plantamos o defeito.
"""

from __future__ import annotations

import glob
import os
import sqlite3
import subprocess
import sys
import tempfile
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BANCO = os.path.join(RAIZ, "planta.db")
GERADOR = os.path.join(RAIZ, "scripts", "gerar_dados.py")


def setUpModule():
    """Constrói o banco se ele não existir. Idempotente e barato o suficiente."""
    if not os.path.exists(BANCO):
        subprocess.run([sys.executable, GERADOR], check=True,
                       stdout=subprocess.DEVNULL)


class Base(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.con = sqlite3.connect(f"file:{BANCO}?mode=ro", uri=True)
        cls.con.execute("PRAGMA foreign_keys = ON")

    @classmethod
    def tearDownClass(cls):
        cls.con.close()

    def um(self, sql, *args):
        return self.con.execute(sql, args).fetchone()

    def todos(self, sql, *args):
        return self.con.execute(sql, args).fetchall()

    def sql_do_arquivo(self, prefixo):
        (arq,) = glob.glob(os.path.join(RAIZ, "consultas", prefixo + "*.sql"))
        with open(arq, encoding="utf-8") as f:
            return f.read()


# ---------------------------------------------------------------------------
class TestEsquema(Base):

    def test_integridade_fisica(self):
        self.assertEqual(self.um("PRAGMA integrity_check")[0], "ok")

    def test_sem_chave_estrangeira_orfa(self):
        self.assertEqual(self.todos("PRAGMA foreign_key_check"), [])

    def test_cadastro_completo(self):
        self.assertEqual(self.um("SELECT COUNT(*) FROM equipamento")[0], 5)
        self.assertEqual(self.um("SELECT COUNT(*) FROM tag")[0], 8)

    def test_volume_de_leituras(self):
        # 30 dias × 1440 min × 8 tags − 120 min de buraco × 8 tags
        esperado = 30 * 1440 * 8 - 120 * 8
        self.assertEqual(self.um("SELECT COUNT(*) FROM leitura")[0], esperado)

    def test_toda_leitura_tem_tag_cadastrado(self):
        self.assertEqual(
            self.um("SELECT COUNT(*) FROM leitura l "
                    "WHERE NOT EXISTS (SELECT 1 FROM tag t "
                    "                   WHERE t.tag_id = l.tag_id)")[0], 0)


# ---------------------------------------------------------------------------
class TestRestricoes(unittest.TestCase):
    """Cada teste abre um banco novo em memória: restrição se testa violando-a."""

    def setUp(self):
        self.con = sqlite3.connect(":memory:")
        self.con.execute("PRAGMA foreign_keys = ON")
        for nome in ("001-esquema.sql", "002-views.sql", "003-seed-cadastro.sql"):
            with open(os.path.join(RAIZ, "sql", nome), encoding="utf-8") as f:
                self.con.executescript(f.read())
        # executescript faz COMMIT implícito e o PRAGMA acima sobrevive,
        # mas o script tem seu próprio PRAGMA foreign_keys = ON. Reafirma:
        self.con.execute("PRAGMA foreign_keys = ON")

    def tearDown(self):
        self.con.close()

    def _batelada(self, **kw):
        d = dict(batelada_id="B-X", produto="P", equipamento_id="R-101",
                 ts_inicio="2026-07-01 00:00:00", ts_fim="2026-07-01 06:00:00",
                 carga_kg=1000.0, produzido_kg=900.0, status="CONCLUIDA",
                 operador="teste")
        d.update(kw)
        self.con.execute(
            "INSERT INTO batelada (batelada_id, produto, equipamento_id, "
            "ts_inicio, ts_fim, carga_kg, produzido_kg, status, operador) "
            "VALUES (:batelada_id,:produto,:equipamento_id,:ts_inicio,:ts_fim,"
            ":carga_kg,:produzido_kg,:status,:operador)", d)

    def test_batelada_valida_entra(self):
        self._batelada()

    def test_fim_antes_do_inicio_e_rejeitado(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self._batelada(ts_fim="2026-06-30 23:00:00")

    def test_em_andamento_precisa_de_fim_nulo(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self._batelada(status="EM_ANDAMENTO")

    def test_carga_negativa_e_rejeitada(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self._batelada(carga_kg=-1.0)

    def test_equipamento_inexistente_e_rejeitado(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self._batelada(equipamento_id="R-999")

    def test_qualidade_fora_do_dominio_e_rejeitada(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.con.execute("INSERT INTO leitura VALUES "
                             "('TI-101','2026-07-01 00:00:00',1.0,'MAIS_OU_MENOS')")

    def test_strict_rejeita_texto_em_coluna_real(self):
        # Sem STRICT, o SQLite guardaria a string alegremente. Este teste é a
        # prova de que a tabela é STRICT.
        with self.assertRaises(sqlite3.IntegrityError):
            self.con.execute("INSERT INTO leitura VALUES "
                             "('TI-101','2026-07-01 00:00:00','quente','BOA')")

    def test_leitura_duplicada_e_rejeitada(self):
        self.con.execute("INSERT INTO leitura VALUES "
                         "('TI-101','2026-07-01 00:00:00',150.0,'BOA')")
        with self.assertRaises(sqlite3.IntegrityError):
            self.con.execute("INSERT INTO leitura VALUES "
                             "('TI-101','2026-07-01 00:00:00',151.0,'BOA')")


# ---------------------------------------------------------------------------
class TestAnomaliasPlantadas(Base):
    """Cada anomalia do gerador tem de ser achada pela consulta correspondente."""

    def test_a1_buraco_de_aquisicao(self):
        n = self.um("SELECT COUNT(*) FROM leitura "
                    "WHERE ts >= '2026-07-14 03:00:00' "
                    "  AND ts <  '2026-07-14 05:00:00'")[0]
        self.assertEqual(n, 0)
        achados = self.todos(self.sql_do_arquivo("09"))
        self.assertEqual(len(achados), 8)                 # todos os 8 tags
        for tag, n_buracos, horas, *_ in achados:
            self.assertEqual(n_buracos, 1, tag)
            self.assertAlmostEqual(horas, 2.02, places=2)

    def test_a2_sensor_travado(self):
        achados = self.todos(self.sql_do_arquivo("08"))
        self.assertEqual(len(achados), 1, "só TI-201 deveria estar travado")
        tag, valor, inicio, fim, amostras, minutos = achados[0]
        self.assertEqual(tag, "TI-201")
        self.assertEqual(inicio, "2026-07-08 10:00:00")
        self.assertEqual(fim, "2026-07-08 11:30:00")
        self.assertEqual(minutos, 90.0)

    def test_a3_qualidade_ruim_do_ph(self):
        n = self.um("SELECT COUNT(*) FROM leitura WHERE tag_id='AI-101' "
                    "AND qualidade='RUIM'")[0]
        self.assertEqual(n, 360)                          # 6 h de minuto a minuto
        # E a view de dado bom tem de excluí-los.
        n_boa = self.um("SELECT COUNT(*) FROM v_leitura_boa WHERE tag_id='AI-101' "
                        "AND ts >= '2026-07-21 06:00:00' "
                        "AND ts <  '2026-07-21 12:00:00'")[0]
        self.assertEqual(n_boa, 0)

    def test_a4_leituras_nulas(self):
        linhas = self.todos("SELECT tag_id, qualidade, COUNT(*) FROM leitura "
                            "WHERE valor IS NULL GROUP BY 1,2")
        self.assertEqual(linhas, [("LI-101", "RUIM", 20)])
        # AVG ignora NULL; COUNT(*) não. É o teste da armadilha do NULL.
        total, com_valor = self.um(
            "SELECT COUNT(*), COUNT(valor) FROM leitura WHERE tag_id='LI-101'")
        self.assertEqual(total - com_valor, 20)

    def test_a5_excursao_de_temperatura(self):
        achados = self.todos(self.sql_do_arquivo("05"))
        ids = sorted(l[0] for l in achados)
        self.assertEqual(ids, ["B-2026-0023", "B-2026-0057"])
        for _, pico, *_ in achados:
            self.assertGreater(pico, 195.0)

    def test_a6_batelada_abortada(self):
        linhas = self.todos("SELECT batelada_id, rendimento_pct FROM v_batelada "
                            "WHERE status='ABORTADA'")
        self.assertEqual(len(linhas), 1)
        self.assertLess(linhas[0][1], 20.0)

    def test_a7_erro_de_balanco_de_massa(self):
        achados = self.todos(self.sql_do_arquivo("04"))
        self.assertGreaterEqual(len(achados), 3)
        for linha in achados:
            erro_pct = linha[5]
            self.assertGreater(abs(erro_pct), 0.5)
            # O erro plantado é sempre no solvente, +12% sobre 25% da receita.
            self.assertAlmostEqual(erro_pct, 3.0, delta=0.05)

    def test_a8_espiculas_de_pressao_passam_pelo_filtro_de_qualidade(self):
        n = self.um("SELECT COUNT(*) FROM v_leitura_boa "
                    "WHERE tag_id='PI-101' AND valor > 9")[0]
        self.assertGreater(n, 0, "as espículas têm de sobreviver ao filtro "
                                 "de qualidade — é esse o ponto do exercício")


# ---------------------------------------------------------------------------
class TestSemanticaDasViews(Base):

    def test_v_leitura_boa_exclui_ruim_e_nulo(self):
        self.assertEqual(
            self.um("SELECT COUNT(*) FROM v_leitura_boa "
                    "WHERE valor IS NULL")[0], 0)
        total_bom = self.um("SELECT COUNT(*) FROM leitura "
                            "WHERE qualidade='BOA' AND valor IS NOT NULL")[0]
        self.assertEqual(self.um("SELECT COUNT(*) FROM v_leitura_boa")[0],
                         total_bom)

    def test_intervalo_semiaberto_nao_duplica_leitura(self):
        """Nenhuma leitura pode pertencer a duas bateladas ao mesmo tempo."""
        dup = self.um("SELECT COUNT(*) FROM ("
                      "  SELECT tag_id, ts FROM v_leitura_batelada "
                      "  GROUP BY tag_id, ts HAVING COUNT(*) > 1)")[0]
        self.assertEqual(dup, 0)

    def test_utilidades_nao_entram_na_batelada(self):
        """TI-201 e FI-201 são do trocador, não do reator: não têm batelada."""
        n = self.um("SELECT COUNT(*) FROM v_leitura_batelada "
                    "WHERE tag_id IN ('TI-201','FI-201')")[0]
        self.assertEqual(n, 0)

    def test_fases_cobrem_a_batelada_inteira(self):
        fases = {f for (f,) in self.todos(
            "SELECT DISTINCT fase FROM v_leitura_fase")}
        self.assertEqual(fases, {"carga", "aquecimento", "reacao",
                                 "resfriamento", "descarga"})

    def test_rendimento_e_coerente(self):
        linhas = self.todos("SELECT batelada_id, carga_kg, produzido_kg, "
                            "rendimento_pct FROM v_batelada")
        for bid, carga, produzido, rend in linhas:
            self.assertAlmostEqual(rend, 100.0 * produzido / carga, places=2,
                                   msg=bid)


# ---------------------------------------------------------------------------
class TestConsultasExecutam(Base):
    """Toda consulta do diretório roda e devolve pelo menos uma linha."""

    def test_todas_as_consultas(self):
        arquivos = sorted(glob.glob(os.path.join(RAIZ, "consultas", "*.sql")))
        self.assertGreaterEqual(len(arquivos), 14)
        for arq in arquivos:
            with self.subTest(consulta=os.path.basename(arq)):
                with open(arq, encoding="utf-8") as f:
                    linhas = self.con.execute(f.read()).fetchall()
                self.assertGreater(len(linhas), 0)

    def test_oee_dentro_de_faixa_plausivel(self):
        linha = self.todos(self.sql_do_arquivo("11"))[0]
        (_, _, _, _, disp, desemp, qual, oee) = linha
        for nome, v in (("disponibilidade", disp), ("desempenho", desemp),
                        ("qualidade", qual), ("oee", oee)):
            self.assertGreater(v, 0, nome)
            self.assertLessEqual(v, 100.0, nome)
        self.assertAlmostEqual(oee, disp * desemp * qual / 10000.0, delta=0.15)

    def test_correlacao_pico_rendimento_e_negativa(self):
        """Mais pico de temperatura, menos rendimento — é o que o dado tem."""
        (_, _, _, r_visc, r_rend) = self.todos(self.sql_do_arquivo("12"))[0]
        self.assertGreater(r_visc, 0.3)
        self.assertLess(r_rend, -0.3)


# ---------------------------------------------------------------------------
class TestDeterminismo(unittest.TestCase):

    def test_mesma_semente_mesmo_banco(self):
        with tempfile.TemporaryDirectory() as d:
            alvo = os.path.join(d, "a.db")
            subprocess.run([sys.executable, GERADOR, alvo, "--dias", "2"],
                           check=True, stdout=subprocess.DEVNULL)
            c1 = sqlite3.connect(alvo)
            soma1 = c1.execute("SELECT ROUND(SUM(valor), 6), COUNT(*) "
                               "FROM leitura").fetchone()
            c1.close()

            alvo2 = os.path.join(d, "b.db")
            subprocess.run([sys.executable, GERADOR, alvo2, "--dias", "2"],
                           check=True, stdout=subprocess.DEVNULL)
            c2 = sqlite3.connect(alvo2)
            soma2 = c2.execute("SELECT ROUND(SUM(valor), 6), COUNT(*) "
                               "FROM leitura").fetchone()
            c2.close()
        self.assertEqual(soma1, soma2)

    def test_semente_diferente_muda_o_dado(self):
        with tempfile.TemporaryDirectory() as d:
            somas = []
            for semente in (1, 2):
                alvo = os.path.join(d, f"s{semente}.db")
                subprocess.run([sys.executable, GERADOR, alvo, "--dias", "2",
                                "--semente", str(semente)],
                               check=True, stdout=subprocess.DEVNULL)
                c = sqlite3.connect(alvo)
                somas.append(c.execute("SELECT SUM(valor) FROM leitura").fetchone())
                c.close()
        self.assertNotEqual(somas[0], somas[1])


if __name__ == "__main__":
    unittest.main(verbosity=2)
