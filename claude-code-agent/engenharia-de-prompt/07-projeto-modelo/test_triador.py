#!/usr/bin/env python3
"""Testes do triador. Rode com: python3 -m unittest -v

Cobrem o que costuma quebrar em aplicação com LLM: extração de JSON sujo,
validação de contrato, o laço de correção, e a matemática do arnês de avaliação.
Nenhum deles precisa de rede ou de chave de API.
"""

import json
import unittest
from pathlib import Path

from avaliar import Placar, avaliar, carregar_casos, estimar_tokens
from provedor import SimulatedProvider, obter_provedor
from triador import CATEGORIAS_VALIDAS, extrair_json, triar, validar

RAIZ = Path(__file__).resolve().parent


class TestExtracaoJSON(unittest.TestCase):
    def test_json_puro(self):
        dados, limpo = extrair_json('{"categoria": "bug"}')
        self.assertEqual(dados, {"categoria": "bug"})
        self.assertTrue(limpo)

    def test_json_com_espaco_em_volta(self):
        dados, limpo = extrair_json('\n  {"a": 1}  \n')
        self.assertEqual(dados, {"a": 1})
        self.assertTrue(limpo, "espaço em branco não deve contar como sujeira")

    def test_cerca_markdown(self):
        dados, limpo = extrair_json('Claro!\n```json\n{"a": 1}\n```\nAlgo mais?')
        self.assertEqual(dados, {"a": 1})
        self.assertFalse(limpo)

    def test_cerca_sem_rotulo_de_linguagem(self):
        dados, _ = extrair_json('```\n{"a": 1}\n```')
        self.assertEqual(dados, {"a": 1})

    def test_json_solto_no_meio_do_texto(self):
        dados, limpo = extrair_json('Segue: {"a": {"b": 2}} — espero ter ajudado.')
        self.assertEqual(dados, {"a": {"b": 2}})
        self.assertFalse(limpo)

    def test_sem_json_nenhum(self):
        dados, limpo = extrair_json("Desculpe, não posso ajudar com isso.")
        self.assertIsNone(dados)
        self.assertFalse(limpo)

    def test_json_truncado_nao_e_aceito(self):
        # max_tokens curto demais corta a saída no meio: caso real e frequente.
        dados, _ = extrair_json('{"categoria": "bug", "resumo": "a tela')
        self.assertIsNone(dados)


class TestValidacao(unittest.TestCase):
    def test_objeto_correto(self):
        self.assertEqual(validar({"categoria": "bug", "urgencia": "alta", "resumo": "x"}), [])

    def test_categoria_inventada(self):
        erros = validar({"categoria": "financeiro", "urgencia": "alta", "resumo": "x"})
        self.assertEqual(len(erros), 1)
        self.assertIn("financeiro", erros[0])

    def test_campo_ausente(self):
        erros = validar({"categoria": "bug"})
        self.assertIn("campo ausente: urgencia", erros)
        self.assertIn("campo ausente: resumo", erros)

    def test_resumo_longo_demais(self):
        erros = validar({"categoria": "bug", "urgencia": "alta", "resumo": "x" * 200})
        self.assertTrue(any("limite" in e for e in erros))


class TestSimulador(unittest.TestCase):
    def test_prompt_sem_restricao_de_formato_tagarela(self):
        saida = SimulatedProvider().completar("Classifique.", "A tela trava.")
        self.assertIn("```", saida)

    def test_prompt_que_exige_json_puro_obedece(self):
        saida = SimulatedProvider().completar(
            "Responda com apenas o JSON. Categorias: cobranca, bug, acesso, duvida.",
            "A tela trava.")
        self.assertEqual(json.loads(saida)["categoria"], "bug")

    def test_determinismo(self):
        p = SimulatedProvider()
        self.assertEqual(p.completar("s", "u"), p.completar("s", "u"))


class TestTriagem(unittest.TestCase):
    def setUp(self):
        self.v3 = (RAIZ / "prompts" / "v3_fewshot.md").read_text(encoding="utf-8")

    def test_caso_de_fronteira_com_a_palavra_erro(self):
        r = triar("Deu erro no pagamento e fui cobrado duas vezes.",
                  self.v3, SimulatedProvider())
        self.assertTrue(r.valido, r.erros)
        self.assertEqual(r.dados["categoria"], "cobranca")

    def test_saida_invalida_dispara_nova_tentativa(self):
        v1 = (RAIZ / "prompts" / "v1_ingenuo.md").read_text(encoding="utf-8")
        r = triar("Fui cobrado duas vezes.", v1, SimulatedProvider(), tentativas=2)
        self.assertEqual(r.tentativas, 2)
        self.assertFalse(r.valido)

    def test_uma_tentativa_nao_reprocessa(self):
        v1 = (RAIZ / "prompts" / "v1_ingenuo.md").read_text(encoding="utf-8")
        r = triar("Fui cobrado duas vezes.", v1, SimulatedProvider(), tentativas=1)
        self.assertEqual(r.tentativas, 1)

    def test_categoria_sempre_dentro_do_conjunto_quando_valido(self):
        for caso in carregar_casos(RAIZ / "dados" / "casos.jsonl"):
            r = triar(caso["chamado"], self.v3, SimulatedProvider())
            if r.valido:
                self.assertIn(r.dados["categoria"], CATEGORIAS_VALIDAS)


class TestArnesDeAvaliacao(unittest.TestCase):
    def setUp(self):
        self.casos = carregar_casos(RAIZ / "dados" / "casos.jsonl")

    def test_conjunto_rotulado_esta_integro(self):
        ids = [c["id"] for c in self.casos]
        self.assertEqual(len(ids), len(set(ids)), "há id duplicado no conjunto")
        for c in self.casos:
            self.assertIn(c["categoria"], CATEGORIAS_VALIDAS)
            self.assertIn(c["urgencia"], {"alta", "normal"})

    def test_fewshot_supera_estruturado_que_supera_ingenuo(self):
        notas = {}
        for nome in ("v1_ingenuo", "v2_estruturado", "v3_fewshot"):
            p = avaliar(RAIZ / "prompts" / f"{nome}.md", self.casos, "simulado", 2)
            notas[nome] = p.taxa("ambos_ok")
        self.assertLess(notas["v1_ingenuo"], notas["v2_estruturado"])
        self.assertLess(notas["v2_estruturado"], notas["v3_fewshot"])

    def test_placar_vazio_nao_divide_por_zero(self):
        self.assertEqual(Placar(prompt="x").taxa("validos"), 0.0)

    def test_estimativa_de_tokens_e_monotonica(self):
        self.assertLess(estimar_tokens("oi"), estimar_tokens("oi " * 100))

    def test_provedor_desconhecido_falha_alto(self):
        with self.assertRaises(ValueError):
            obter_provedor("gpt-caseiro")


if __name__ == "__main__":
    unittest.main(verbosity=2)
