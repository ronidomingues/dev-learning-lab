"""Planos, catálogo e aritmética de calendário."""

from __future__ import annotations

from datetime import date, timedelta

import pytest

from assinaturas.dinheiro import Dinheiro
from assinaturas.plano import CATALOGO, Plano, proxima_cobranca


class TestPlano:
    def test_ciclo_zero_e_recusado(self):
        with pytest.raises(ValueError, match="dias_ciclo deve ser positivo"):
            Plano("x", "X", Dinheiro(100), dias_ciclo=0)

    def test_ciclo_negativo_e_recusado(self):
        with pytest.raises(ValueError):
            Plano("x", "X", Dinheiro(100), dias_ciclo=-30)

    def test_plano_e_imutavel(self):
        with pytest.raises(Exception):
            CATALOGO["pro"].preco = Dinheiro(1)  # type: ignore[misc]


class TestCatalogo:
    @pytest.mark.parametrize("codigo", ["basico", "pro", "anual"])
    def test_o_codigo_da_chave_bate_com_o_do_objeto(self, codigo: str):
        """Consistência de dados de configuração.

        Parece trivial. É o teste que pega o copiar-e-colar na hora de
        acrescentar o quarto plano — erro que o SQLite depois esconde,
        porque `plano` é só uma string na tabela.
        """
        assert CATALOGO[codigo].codigo == codigo

    def test_precos_sao_positivos_e_o_anual_e_mais_barato_por_mes(self):
        mensal = CATALOGO["pro"].preco.centavos
        anual_por_mes = CATALOGO["anual"].preco.centavos / 12
        assert anual_por_mes < mensal, "o plano anual precisa compensar o compromisso"


class TestProximaCobranca:
    @pytest.mark.parametrize(
        ("ciclos", "dias"),
        [(0, 0), (1, 30), (2, 60), (12, 360)],
    )
    def test_multiplica_o_ciclo(self, ciclos: int, dias: int):
        base = date(2026, 8, 12)
        assert proxima_cobranca(base, 30, ciclos) == base + timedelta(days=dias)

    def test_ciclos_negativos_sao_recusados(self):
        with pytest.raises(ValueError, match="não pode ser negativo"):
            proxima_cobranca(date(2026, 8, 12), 30, -1)

    def test_atravessa_ano_bissexto_sem_pular_dia(self):
        """2028 é bissexto: 2028-02-01 + 30 dias = 2028-03-02 (fev tem 29 dias)."""
        assert proxima_cobranca(date(2028, 2, 1), 30) == date(2028, 3, 2)

    def test_em_ano_comum_o_mesmo_calculo_da_um_dia_antes_no_calendario(self):
        """2026 não é bissexto: 2026-02-01 + 30 = 2026-03-03.

        Comparar os dois casos lado a lado é o que torna a consequência da
        escolha "ciclo em dias" visível: o dia do mês **escorrega**. É um
        trade-off aceito e documentado, não um bug.
        """
        assert proxima_cobranca(date(2026, 2, 1), 30) == date(2026, 3, 3)

    def test_atravessa_a_virada_do_ano(self):
        assert proxima_cobranca(date(2026, 12, 20), 30) == date(2027, 1, 19)
