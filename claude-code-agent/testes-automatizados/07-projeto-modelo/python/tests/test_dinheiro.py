"""Testes unitários puros: nenhuma dependência, nenhum dublê, nenhum setup.

Este arquivo é o exemplo canônico de teste unitário. Cada teste:
1. tem um nome que descreve o comportamento, não o método;
2. segue Arrange–Act–Assert (aqui muitas vezes em uma linha só);
3. verifica **uma** afirmação de comportamento.
"""

from __future__ import annotations

import pytest

from assinaturas.dinheiro import Dinheiro, ValorInvalido


class TestConstrucao:
    def test_centavos_inteiros_sao_aceitos(self):
        assert Dinheiro(1990).centavos == 1990

    def test_zero_e_valido(self):
        assert Dinheiro(0).centavos == 0

    def test_negativo_e_recusado(self):
        with pytest.raises(ValorInvalido, match="não pode ser negativo"):
            Dinheiro(-1)

    def test_float_e_recusado_para_nao_perder_centavo(self):
        with pytest.raises(ValorInvalido, match="deve ser int"):
            Dinheiro(19.90)  # type: ignore[arg-type]

    def test_bool_e_recusado_mesmo_sendo_int_em_python(self):
        # `isinstance(True, int)` é True em Python. Sem o teste, `Dinheiro(True)`
        # passaria valendo 1 centavo. Este teste existe por causa de um bug real.
        with pytest.raises(ValorInvalido):
            Dinheiro(True)  # type: ignore[arg-type]


class TestDeReais:
    @pytest.mark.parametrize(
        ("entrada", "centavos"),
        [
            ("19,90", 1990),
            ("19.90", 1990),
            ("R$ 19,90", 1990),
            (" 19,90 ", 1990),
            ("1.234,56", 123456),
            ("0,01", 1),
            ("0", 0),
            (49, 4900),
            ("100", 10000),
        ],
        ids=[
            "virgula-ptbr",
            "ponto-enus",
            "com-simbolo",
            "com-espacos",
            "milhar-ptbr",
            "um-centavo",
            "zero",
            "int-puro",
            "string-inteira",
        ],
    )
    def test_converte_formatos_de_entrada(self, entrada, centavos):
        assert Dinheiro.de_reais(entrada).centavos == centavos

    @pytest.mark.parametrize(
        ("entrada", "esperado"),
        [("0,005", 1), ("0,004", 0), ("0,015", 2)],
        ids=["meio-arredonda-pra-cima", "abaixo-de-meio-desce", "um-e-meio-sobe"],
    )
    def test_arredonda_meio_para_cima(self, entrada, esperado):
        # ROUND_HALF_UP e não o padrão do Python (ROUND_HALF_EVEN, "do banqueiro"):
        # `round(0.5) == 0` em Python surpreende contador e cliente.
        assert Dinheiro.de_reais(entrada).centavos == esperado

    def test_float_nao_contamina_a_conversao(self):
        # Decimal(0.1) seria 0.1000000000000000055511151231257827…
        # Convertemos via str() antes, então o resultado é exato.
        assert Dinheiro.de_reais(0.1).centavos == 10


class TestAritmetica:
    def test_soma(self):
        assert Dinheiro(1990) + Dinheiro(10) == Dinheiro(2000)

    def test_subtracao(self):
        assert Dinheiro(2000) - Dinheiro(10) == Dinheiro(1990)

    def test_subtracao_que_ficaria_negativa_explode(self):
        with pytest.raises(ValorInvalido):
            Dinheiro(100) - Dinheiro(101)

    def test_multiplicacao_por_quantidade(self):
        assert Dinheiro(1990) * 3 == Dinheiro(5970)

    def test_multiplicacao_por_float_e_recusada(self):
        # Multiplicar dinheiro por fração é "aplicar percentual" — outra operação,
        # com outra regra de arredondamento. A API impede a confusão.
        with pytest.raises(ValorInvalido, match="só por int"):
            Dinheiro(1990) * 0.9  # type: ignore[operator]

    def test_e_imutavel(self):
        d = Dinheiro(100)
        with pytest.raises(Exception):  # FrozenInstanceError herda de AttributeError
            d.centavos = 200  # type: ignore[misc]

    def test_valores_iguais_sao_iguais(self):
        assert Dinheiro(100) == Dinheiro(100)

    def test_ordena(self):
        assert sorted([Dinheiro(300), Dinheiro(100), Dinheiro(200)]) == [
            Dinheiro(100),
            Dinheiro(200),
            Dinheiro(300),
        ]


class TestDesconto:
    @pytest.mark.parametrize(
        ("centavos", "percentual", "esperado"),
        [
            (1000, 10, 900),
            (1000, 0, 1000),
            (1000, 100, 0),
            (1999, 10, 1799),  # 199,9 → 200 de desconto (meio para cima)
            (1, 50, 0),  # 0,5 centavo de desconto → 1, sobra 0 (favorece o cliente)
            (3, 50, 1),  # 1,5 → 2 de desconto, sobra 1
        ],
        ids=["dez-por-cento", "zero", "cortesia", "fronteira-1999", "um-centavo", "tres-centavos"],
    )
    def test_calcula_desconto(self, centavos, percentual, esperado):
        assert Dinheiro(centavos).aplicar_desconto(percentual).centavos == esperado

    @pytest.mark.parametrize("percentual", [-1, 101, 1000])
    def test_percentual_fora_da_faixa_explode(self, percentual):
        with pytest.raises(ValorInvalido, match="fora de 0..100"):
            Dinheiro(1000).aplicar_desconto(percentual)

    def test_percentual_float_e_recusado(self):
        with pytest.raises(ValorInvalido, match="deve ser int"):
            Dinheiro(1000).aplicar_desconto(10.5)  # type: ignore[arg-type]


class TestFormatacao:
    @pytest.mark.parametrize(
        ("centavos", "texto"),
        [
            (0, "R$ 0,00"),
            (1, "R$ 0,01"),
            (1990, "R$ 19,90"),
            (123456, "R$ 1.234,56"),
            (100000000, "R$ 1.000.000,00"),
        ],
    )
    def test_formata_em_padrao_brasileiro(self, centavos, texto):
        assert str(Dinheiro(centavos)) == texto

    def test_ida_e_volta_preserva_o_valor(self):
        original = Dinheiro(123456)
        assert Dinheiro.de_reais(str(original)) == original
