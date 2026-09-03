"""Como testar (um pouquinho) a única coisa que fala com o mundo real.

`RelogioDoSistema.hoje()` é a fronteira: não há como verificar o valor sem
reintroduzir a dependência que estamos tentando eliminar. O que se pode fazer é
um teste de **sanidade** — o tipo certo e uma faixa absurdamente larga —
e aceitar que o resto é coberto pela ausência de lógica.

Esta é a resposta honesta a "como testo `date.today()`?": você não testa. Você
o empurra para uma linha só, sem lógica, e testa tudo o que consome o resultado.
"""

from __future__ import annotations

from datetime import date, timedelta

from assinaturas.relogio import Relogio, RelogioDoSistema, RelogioFixo


class TestRelogioDoSistema:
    def test_devolve_um_date(self):
        assert isinstance(RelogioDoSistema().hoje(), date)

    def test_esta_dentro_de_uma_faixa_plausivel(self):
        """Faixa larga de propósito: o teste não pode falhar à meia-noite.

        Um teste que compara com `date.today()` exato é *flaky* — se rodar às
        23:59:59.999 e a comparação cair no dia seguinte, quebra sem motivo.
        """
        hoje = RelogioDoSistema().hoje()
        assert date(2024, 1, 1) < hoje < date(2100, 1, 1)

    def test_duas_chamadas_no_mesmo_teste_dao_o_mesmo_dia_quase_sempre(self):
        """Documenta uma condição de corrida real em vez de fingir que não existe."""
        a, b = RelogioDoSistema().hoje(), RelogioDoSistema().hoje()
        assert (b - a).days in (0, 1)  # 1 apenas se o teste cruzou a meia-noite


class TestRelogioFixo:
    def test_devolve_sempre_a_mesma_data(self):
        relogio = RelogioFixo(date(2026, 8, 12))
        assert relogio.hoje() == relogio.hoje() == date(2026, 8, 12)

    def test_avancar_simula_a_passagem_do_tempo(self):
        relogio = RelogioFixo(date(2026, 8, 12))
        relogio.avancar(30)
        assert relogio.hoje() == date(2026, 9, 11)

    def test_avancar_aceita_valor_negativo_e_volta_no_tempo(self):
        relogio = RelogioFixo(date(2026, 8, 12))
        relogio.avancar(-1)
        assert relogio.hoje() == date(2026, 8, 11)

    def test_avancos_sucessivos_acumulam(self):
        relogio = RelogioFixo(date(2026, 1, 1))
        for _ in range(12):
            relogio.avancar(30)
        assert relogio.hoje() == date(2026, 1, 1) + timedelta(days=360)


class TestContrato:
    def test_as_duas_implementacoes_satisfazem_o_protocolo(self):
        """`Protocol` com `runtime_checkable` seria necessário para `isinstance`.

        Sem ele, a verificação é estática (mypy/pyright). Aqui fazemos a versão
        estrutural, que é o que o Python realmente exige em tempo de execução:
        o método existe e é chamável.
        """
        for implementacao in (RelogioDoSistema(), RelogioFixo(date(2026, 8, 12))):
            assert callable(getattr(implementacao, "hoje"))
            assert isinstance(implementacao.hoje(), date)

    def test_o_protocolo_e_usado_apenas_para_tipagem(self):
        # `Relogio` é um Protocol: não se instancia, serve para o verificador de tipos.
        assert Relogio.__module__ == "assinaturas.relogio"
