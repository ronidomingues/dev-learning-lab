"""Testes de fronteira (boundary testing) e de exceção.

Cupom é o lugar clássico do erro *off-by-one* em data: "vale até dia 31" —
vale **no** dia 31 ou até o dia 30? A resposta é uma decisão de negócio, e o
teste é onde ela fica registrada de forma executável.
"""

from __future__ import annotations

from datetime import date, timedelta

import pytest

from assinaturas.dinheiro import Dinheiro
from assinaturas.plano import Cupom, CupomInvalido

PRECO = Dinheiro.de_reais("100,00")
VALIDADE = date(2026, 8, 31)


@pytest.fixture
def cupom() -> Cupom:
    return Cupom("PROMO20", percentual=20, validade=VALIDADE, usos_maximos=2)


class TestValidade:
    @pytest.mark.parametrize(
        ("hoje", "vale"),
        [
            (VALIDADE - timedelta(days=1), True),
            (VALIDADE, True),  # ← a fronteira. Vale NO dia da validade.
            (VALIDADE + timedelta(days=1), False),
        ],
        ids=["dia-anterior", "ultimo-dia-inclusive", "dia-seguinte"],
    )
    def test_fronteira_da_validade(self, cupom: Cupom, hoje: date, vale: bool):
        if vale:
            assert cupom.preco_com_desconto(PRECO, hoje, 0) == Dinheiro.de_reais("80,00")
        else:
            with pytest.raises(CupomInvalido, match="expirou"):
                cupom.preco_com_desconto(PRECO, hoje, 0)

    def test_mensagem_de_expiracao_traz_a_data_formatada(self, cupom: Cupom):
        # Testar a mensagem de erro é polêmico: engessa refatoração. Aqui vale,
        # porque a mensagem vai para o cliente final — é comportamento, não detalhe.
        with pytest.raises(CupomInvalido) as excecao:
            cupom.preco_com_desconto(PRECO, date(2026, 9, 1), 0)
        assert "31/08/2026" in str(excecao.value)


class TestLimiteDeUsos:
    @pytest.mark.parametrize(
        ("usos_atuais", "vale"),
        [(0, True), (1, True), (2, False), (3, False)],
        ids=["primeiro-uso", "segundo-uso", "estourou", "muito-alem"],
    )
    def test_fronteira_de_usos(self, cupom: Cupom, usos_atuais: int, vale: bool):
        if vale:
            assert cupom.preco_com_desconto(PRECO, VALIDADE, usos_atuais).centavos == 8000
        else:
            with pytest.raises(CupomInvalido, match="esgotado"):
                cupom.preco_com_desconto(PRECO, VALIDADE, usos_atuais)


class TestPercentuais:
    def test_cortesia_de_cem_por_cento_zera_a_conta(self):
        cortesia = Cupom("CORTESIA", 100, VALIDADE)
        assert cortesia.preco_com_desconto(PRECO, VALIDADE, 0).centavos == 0

    def test_cupom_de_zero_por_cento_e_valido_e_inocuo(self):
        # Parece bobo, mas cupom de 0% é criado por engano em campanha real
        # e o sistema não deve quebrar por causa disso.
        inocuo = Cupom("NADA", 0, VALIDADE)
        assert inocuo.preco_com_desconto(PRECO, VALIDADE, 0) == PRECO


class TestOrdemDasValidacoes:
    def test_expirado_e_esgotado_reporta_expiracao_primeiro(self, cupom: Cupom):
        """Quando dois motivos coexistem, a mensagem é determinística.

        Sem este teste, alguém reordena as validações "para ficar mais legível"
        e uma suíte de contrato de mensagem em outro serviço quebra.
        """
        with pytest.raises(CupomInvalido, match="expirou"):
            cupom.preco_com_desconto(PRECO, date(2026, 12, 1), usos_atuais=99)
