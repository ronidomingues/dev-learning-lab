"""Testes baseados em propriedades (*property-based testing*) com Hypothesis.

Um teste de exemplo diz: "para ESTE valor, o resultado é AQUELE".
Um teste de propriedade diz: "para QUALQUER valor válido, esta lei se mantém" —
e a biblioteca procura ativamente um contraexemplo, encolhendo-o até o menor
caso que ainda falha (*shrinking*).

Rode com `pytest tests/test_propriedades.py -m propriedade`.
Se Hypothesis não estiver instalado, o arquivo é pulado inteiro.
"""

from __future__ import annotations

from datetime import date, timedelta

import pytest

hypothesis = pytest.importorskip("hypothesis", reason="pip install hypothesis")

from hypothesis import assume, given, settings  # noqa: E402
from hypothesis import strategies as st  # noqa: E402

from assinaturas.assinatura import Assinatura, Estado  # noqa: E402
from assinaturas.dinheiro import Dinheiro, ValorInvalido  # noqa: E402
from assinaturas.plano import CATALOGO, Cupom, CupomInvalido, proxima_cobranca  # noqa: E402

pytestmark = pytest.mark.propriedade

centavos = st.integers(min_value=0, max_value=10**9)
percentuais = st.integers(min_value=0, max_value=100)
datas = st.dates(min_value=date(2020, 1, 1), max_value=date(2040, 12, 31))


class TestPropriedadesDeDinheiro:
    @given(centavos)
    def test_desconto_nunca_aumenta_o_valor(self, c: int):
        d = Dinheiro(c)
        for p in (0, 1, 50, 99, 100):
            assert d.aplicar_desconto(p).centavos <= c

    @given(centavos)
    def test_desconto_de_zero_e_identidade(self, c: int):
        assert Dinheiro(c).aplicar_desconto(0) == Dinheiro(c)

    @given(centavos)
    def test_desconto_de_cem_zera(self, c: int):
        assert Dinheiro(c).aplicar_desconto(100).centavos == 0

    @given(centavos, percentuais)
    def test_desconto_erra_no_maximo_meio_centavo(self, c: int, p: int):
        """A lei que amarra o arredondamento: |resultado - exato| <= 0,5 centavo."""
        from decimal import Decimal

        exato = Decimal(c) * (100 - p) / 100
        obtido = Decimal(Dinheiro(c).aplicar_desconto(p).centavos)
        assert abs(obtido - exato) <= Decimal("0.5")

    @given(centavos, centavos)
    def test_soma_e_comutativa(self, a: int, b: int):
        assert Dinheiro(a) + Dinheiro(b) == Dinheiro(b) + Dinheiro(a)

    @given(centavos, centavos)
    def test_somar_e_subtrair_volta_ao_original(self, a: int, b: int):
        assert (Dinheiro(a) + Dinheiro(b)) - Dinheiro(b) == Dinheiro(a)

    @given(centavos)
    def test_formatar_e_reler_preserva_o_valor(self, c: int):
        """Propriedade de ida-e-volta (*round-trip*) — a mais produtiva de todas.

        Foi este tipo de propriedade que encontrou o bug do separador de milhar
        durante a escrita deste projeto.
        """
        d = Dinheiro(c)
        assert Dinheiro.de_reais(str(d)) == d

    @given(st.integers(max_value=-1))
    def test_qualquer_negativo_e_recusado(self, c: int):
        with pytest.raises(ValorInvalido):
            Dinheiro(c)


class TestPropriedadesDeCalendario:
    @given(datas, st.integers(min_value=1, max_value=400), st.integers(min_value=0, max_value=50))
    def test_proxima_cobranca_e_monotonica(self, base: date, ciclo: int, ciclos: int):
        assume(base.year + (ciclo * (ciclos + 1)) // 365 < 4000)  # não estourar date.max
        assert proxima_cobranca(base, ciclo, ciclos) <= proxima_cobranca(base, ciclo, ciclos + 1)

    @given(datas, st.integers(min_value=1, max_value=400))
    def test_zero_ciclos_e_a_propria_data(self, base: date, ciclo: int):
        assert proxima_cobranca(base, ciclo, 0) == base


class TestPropriedadesDaMaquinaDeEstados:
    @given(st.lists(st.sampled_from(["pausar", "retomar", "cancelar", "pagar", "falhar"]),
                    min_size=0, max_size=25))
    @settings(max_examples=200)
    def test_nenhuma_sequencia_de_acoes_produz_estado_invalido(self, acoes: list[str]):
        """Invariante global: aconteça o que acontecer, o objeto continua coerente.

        Este é o teste de propriedade mais útil para máquinas de estado: aplica
        uma sequência aleatória de ações, ignora as que são proibidas, e verifica
        os **invariantes** no final — em vez de prever o resultado exato.
        """
        from assinaturas.assinatura import TransicaoInvalida

        hoje = date(2026, 8, 12)
        a = Assinatura.criar("a1", "ana@ex.br", CATALOGO["pro"], hoje)

        for i, acao in enumerate(acoes):
            dia = hoje + timedelta(days=i)
            try:
                match acao:
                    case "pausar":
                        a.pausar()
                    case "retomar":
                        a.retomar(dia)
                    case "cancelar":
                        a.cancelar()
                    case "pagar":
                        a.registrar_pagamento(dia)
                    case "falhar":
                        a.registrar_falha()
            except TransicaoInvalida:
                pass  # ação proibida naquele estado: esperado, segue o baile

        assert isinstance(a.estado, Estado)
        assert 0 <= a.tentativas_falhas <= 3
        assert a.ciclos_pagos >= 0
        assert a.proxima_cobranca >= a.inicio
        if a.estado is Estado.ATIVA:
            assert a.tentativas_falhas == 0

    @given(st.integers(min_value=1, max_value=10))
    def test_cancelamento_e_absorvente(self, quantas_falhas: int):
        """Estado absorvente: uma vez cancelada, nenhuma ação a tira de lá."""
        from assinaturas.assinatura import TransicaoInvalida

        hoje = date(2026, 8, 12)
        a = Assinatura.criar("a1", "ana@ex.br", CATALOGO["pro"], hoje)
        a.cancelar()
        for _ in range(quantas_falhas):
            for metodo in (a.pausar, a.cancelar, a.registrar_falha):
                with pytest.raises(TransicaoInvalida):
                    metodo()
        assert a.estado is Estado.CANCELADA


class TestPropriedadesDeCupom:
    @given(centavos, percentuais, datas, datas, st.integers(min_value=0, max_value=5))
    def test_ou_devolve_valor_menor_ou_igual_ou_levanta_cupominvalido(
        self, c: int, p: int, validade: date, hoje: date, usos: int
    ):
        """Propriedade de totalidade: a função nunca falha de forma inesperada.

        Ela ou devolve um `Dinheiro` que respeita a lei do desconto, ou levanta
        `CupomInvalido`. Nada de `TypeError`, `AttributeError` ou `None`.
        """
        cupom = Cupom("X", p, validade, usos_maximos=3)
        try:
            resultado = cupom.preco_com_desconto(Dinheiro(c), hoje, usos)
        except CupomInvalido:
            return
        assert isinstance(resultado, Dinheiro)
        assert resultado.centavos <= c
