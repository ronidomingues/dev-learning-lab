"""Teste de fumaça (*smoke test*) da borda.

Objetivo modesto e explícito: garantir que a fiação da aplicação existe — que
`main()` monta os objetos, roda e sai com código 0. **Não** testa regra de
negócio: isso é trabalho dos outros arquivos.

Ferramenta: a fixture nativa `capsys`, que captura o que foi para stdout/stderr.
"""

from __future__ import annotations

import pytest

from assinaturas.cli import main


class TestComandoDemo:
    def test_sai_com_codigo_zero(self, capsys):
        assert main(["demo"]) == 0

    def test_imprime_o_relatorio(self, capsys):
        main(["demo"])
        saida = capsys.readouterr().out
        assert "relatório:" in saida

    def test_a_demo_cobra_uma_recusa_uma_e_ignora_a_futura(self, capsys):
        """A demo é determinística de propósito: relógio fixo e gateway falso.

        Uma demo que depende da data de hoje é uma demo que quebra sozinha —
        e este teste é o que garante que ela não passou a depender.
        """
        main(["demo"])
        saida = capsys.readouterr().out
        assert "1 cobradas (R$ 49,90), 1 recusadas, 0 canceladas, 0 com erro" in saida
        # Casamos por linha e por palavra, não por posição de coluna: um dia
        # alguém troca a largura do `:22` da formatação e o teste não deve cair
        # por isso. Testar alinhamento seria testar detalhe, não comportamento.
        linha_carla = next(l for l in saida.splitlines() if "carla@exemplo.br" in l)
        assert linha_carla.split()[2:3] == ["ativa"]  # não venceu, não foi cobrada
        assert "ciclos 0" in linha_carla


class TestArgumentos:
    def test_sem_comando_o_argparse_sai_com_erro_2(self):
        """`argparse` chama `sys.exit(2)`; capturamos via `SystemExit`."""
        with pytest.raises(SystemExit) as saida:
            main([])
        assert saida.value.code == 2

    def test_comando_desconhecido_tambem_sai_com_erro(self):
        with pytest.raises(SystemExit):
            main(["voar"])


class TestRenovarComBanco:
    @pytest.mark.integracao
    def test_renovar_cria_o_banco_e_nao_explode_vazio(self, tmp_path, capsys):
        banco = tmp_path / "vazio.db"
        assert main(["renovar", "--banco", str(banco), "--data", "2026-08-12"]) == 0
        assert banco.exists()
        assert "0 cobradas" in capsys.readouterr().out
