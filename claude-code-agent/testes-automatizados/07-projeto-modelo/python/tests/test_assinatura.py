"""Máquina de estados: cobrir a tabela de transições inteira.

Padrão a copiar: em vez de escrever 16 testes quase iguais, escreve-se **uma**
tabela de transições e um teste parametrizado que a percorre. Quando um estado
novo aparecer, a tabela cresce e o teste continua o mesmo.
"""

from __future__ import annotations

from datetime import date, timedelta

import pytest

from assinaturas.assinatura import MAX_TENTATIVAS, Assinatura, Estado, TransicaoInvalida
from assinaturas.plano import CATALOGO

HOJE = date(2026, 8, 12)


def nova(estado: Estado = Estado.ATIVA, **kwargs) -> Assinatura:
    """Construtor de conveniência para os testes (*object mother*)."""
    a = Assinatura.criar("a1", "ana@exemplo.br", CATALOGO["pro"], HOJE)
    a.estado = estado
    for chave, valor in kwargs.items():
        setattr(a, chave, valor)
    return a


class TestCriacao:
    def test_comeca_ativa(self):
        assert nova().estado is Estado.ATIVA

    def test_primeira_cobranca_e_um_ciclo_a_frente(self):
        a = Assinatura.criar("a1", "ana@exemplo.br", CATALOGO["pro"], HOJE)
        assert a.proxima_cobranca == HOJE + timedelta(days=30)

    def test_plano_anual_cobra_em_365_dias(self):
        a = Assinatura.criar("a1", "ana@exemplo.br", CATALOGO["anual"], HOJE)
        assert a.proxima_cobranca == HOJE + timedelta(days=365)

    def test_nasce_sem_ciclos_pagos(self):
        assert nova().ciclos_pagos == 0


# ---------------------------------------------------------------------------
# Tabela de transições: (estado inicial, ação, estado final ou None se proibida)
# ---------------------------------------------------------------------------
ACOES = {
    "pausar": lambda a: a.pausar(),
    "retomar": lambda a: a.retomar(HOJE),
    "cancelar": lambda a: a.cancelar(),
    "pagar": lambda a: a.registrar_pagamento(HOJE),
    "falhar": lambda a: a.registrar_falha(),
}

TABELA = [
    (Estado.ATIVA, "pausar", Estado.PAUSADA),
    (Estado.ATIVA, "retomar", None),
    (Estado.ATIVA, "cancelar", Estado.CANCELADA),
    (Estado.ATIVA, "pagar", Estado.ATIVA),
    (Estado.ATIVA, "falhar", Estado.INADIMPLENTE),
    (Estado.PAUSADA, "pausar", None),
    (Estado.PAUSADA, "retomar", Estado.ATIVA),
    (Estado.PAUSADA, "cancelar", Estado.CANCELADA),
    (Estado.PAUSADA, "pagar", None),
    (Estado.PAUSADA, "falhar", None),
    (Estado.INADIMPLENTE, "pausar", None),
    (Estado.INADIMPLENTE, "retomar", None),
    (Estado.INADIMPLENTE, "cancelar", Estado.CANCELADA),
    (Estado.INADIMPLENTE, "pagar", Estado.ATIVA),
    (Estado.INADIMPLENTE, "falhar", Estado.INADIMPLENTE),
    (Estado.CANCELADA, "pausar", None),
    (Estado.CANCELADA, "retomar", None),
    (Estado.CANCELADA, "cancelar", None),
    (Estado.CANCELADA, "pagar", None),
    (Estado.CANCELADA, "falhar", None),
]


@pytest.mark.parametrize(
    ("inicial", "acao", "final"),
    TABELA,
    ids=[f"{i.value}-{a}" for i, a, _ in TABELA],
)
def test_tabela_de_transicoes(inicial: Estado, acao: str, final: Estado | None):
    assinatura = nova(inicial)
    if final is None:
        with pytest.raises(TransicaoInvalida):
            ACOES[acao](assinatura)
        assert assinatura.estado is inicial, "transição proibida não pode mudar o estado"
    else:
        ACOES[acao](assinatura)
        assert assinatura.estado is final


def test_a_tabela_cobre_todas_as_combinacoes():
    """Meta-teste: garante que a tabela não esqueceu nenhum par (estado, ação).

    Este é um teste sobre o **teste**. Sem ele, adicionar um estado novo à enum
    passa silenciosamente sem cobertura — o pior tipo de lacuna, porque a
    porcentagem de cobertura não cai.
    """
    esperado = {(e, a) for e in Estado for a in ACOES}
    coberto = {(i, a) for i, a, _ in TABELA}
    assert coberto == esperado


class TestVencimento:
    @pytest.mark.parametrize(
        ("dias", "vencida"),
        [(-1, False), (0, True), (1, True)],
        ids=["dia-antes", "no-dia-inclusive", "dia-depois"],
    )
    def test_fronteira_do_vencimento(self, dias: int, vencida: bool):
        a = nova(proxima_cobranca=HOJE)
        assert a.esta_vencida(HOJE + timedelta(days=dias)) is vencida

    @pytest.mark.parametrize("estado", [Estado.PAUSADA, Estado.CANCELADA])
    def test_pausada_e_cancelada_nunca_vencem(self, estado: Estado):
        a = nova(estado, proxima_cobranca=HOJE - timedelta(days=90))
        assert a.esta_vencida(HOJE) is False

    def test_inadimplente_continua_vencendo_para_ser_retentada(self):
        a = nova(Estado.INADIMPLENTE, proxima_cobranca=HOJE)
        assert a.esta_vencida(HOJE) is True


class TestPagamento:
    def test_pagamento_empurra_o_vencimento_um_ciclo(self):
        a = nova(proxima_cobranca=HOJE)
        a.registrar_pagamento(HOJE)
        assert a.proxima_cobranca == HOJE + timedelta(days=30)

    def test_pagamento_conta_o_ciclo(self):
        a = nova()
        a.registrar_pagamento(HOJE)
        a.registrar_pagamento(HOJE)
        assert a.ciclos_pagos == 2

    def test_pagamento_zera_as_tentativas_de_falha(self):
        a = nova(Estado.INADIMPLENTE, tentativas_falhas=2)
        a.registrar_pagamento(HOJE)
        assert a.tentativas_falhas == 0
        assert a.estado is Estado.ATIVA

    def test_o_novo_vencimento_conta_do_dia_do_pagamento_nao_do_vencimento_antigo(self):
        """Decisão de negócio: pagamento atrasado reinicia o ciclo do dia do pagamento.

        A alternativa (contar do vencimento antigo) puniria o cliente atrasado
        com um ciclo mais curto. Registrado em teste porque é a pergunta que o
        time de suporte faz uma vez por trimestre.
        """
        a = nova(proxima_cobranca=HOJE)
        pago_em = HOJE + timedelta(days=5)
        a.registrar_pagamento(pago_em)
        assert a.proxima_cobranca == pago_em + timedelta(days=30)


class TestInadimplencia:
    def test_primeira_falha_deixa_inadimplente(self):
        a = nova()
        a.registrar_falha()
        assert a.estado is Estado.INADIMPLENTE
        assert a.tentativas_falhas == 1

    def test_cancela_na_terceira_falha(self):
        a = nova()
        for _ in range(MAX_TENTATIVAS):
            a.registrar_falha()
        assert a.estado is Estado.CANCELADA

    def test_nao_cancela_na_segunda(self):
        a = nova()
        for _ in range(MAX_TENTATIVAS - 1):
            a.registrar_falha()
        assert a.estado is Estado.INADIMPLENTE

    def test_o_historico_registra_o_motivo_do_cancelamento(self):
        a = nova()
        for _ in range(MAX_TENTATIVAS):
            a.registrar_falha()
        assert a.historico[-1] == "cancelada por inadimplência"


class TestPausa:
    def test_retomar_reinicia_o_ciclo_do_dia_da_retomada(self):
        a = nova(proxima_cobranca=HOJE + timedelta(days=2))
        a.pausar()
        retomado_em = HOJE + timedelta(days=100)
        a.retomar(retomado_em)
        assert a.proxima_cobranca == retomado_em + timedelta(days=30)

    def test_cliente_nao_paga_pelo_tempo_pausado(self):
        """Consequência da regra acima, dita em linguagem de negócio."""
        a = nova(proxima_cobranca=HOJE)
        a.pausar()
        a.retomar(HOJE + timedelta(days=365))
        assert a.ciclos_pagos == 0
