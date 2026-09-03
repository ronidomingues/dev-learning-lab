"""Testes do caso de uso, com dublês.

Aqui aparecem os quatro tipos de dublê que valem a pena:

- **stub** (`RelogioFixo`): responde o que o teste precisa, nada mais;
- **fake** (`GatewayFalso`, `RepositorioMemoria`): implementação funcional simplificada;
- **spy** (`NotificadorEspiao`): registra as chamadas para o teste inspecionar;
- **mock** (`unittest.mock.Mock`): verifica a interação exata — usado com parcimônia.

Regra deste projeto: verificar **estado** sempre que possível, **interação**
só quando o efeito colateral é o comportamento (enviar e-mail, cobrar).
"""

from __future__ import annotations

from datetime import date, timedelta
from unittest.mock import Mock, call

import pytest

from assinaturas.assinatura import Assinatura, Estado
from assinaturas.dinheiro import Dinheiro
from assinaturas.gateway import Cobranca, GatewayFalso, GatewayQueExplode
from assinaturas.plano import CATALOGO, CupomInvalido
from assinaturas.relogio import RelogioFixo
from assinaturas.repositorio import RepositorioMemoria
from assinaturas.servico import NotificadorEspiao, ServicoRenovacao

HOJE = date(2026, 8, 12)


def vencida(id: str, cliente: str, plano: str = "pro", dias_atraso: int = 0) -> Assinatura:
    a = Assinatura.criar(id, cliente, CATALOGO[plano], HOJE)
    a.proxima_cobranca = HOJE - timedelta(days=dias_atraso)
    return a


def montar(*assinaturas: Assinatura, gateway=None, cupons=None):
    """Fábrica de cenário: devolve (servico, repo, gateway, notificador)."""
    repo = RepositorioMemoria(assinaturas)
    gw = gateway or GatewayFalso()
    espiao = NotificadorEspiao()
    servico = ServicoRenovacao(repo, gw, RelogioFixo(HOJE), espiao, cupons)
    return servico, repo, gw, espiao


class TestCaminhoFeliz:
    def test_cobra_apenas_as_vencidas(self):
        a_vencida = vencida("a1", "ana@ex.br")
        a_futura = Assinatura.criar("a2", "bruno@ex.br", CATALOGO["pro"], HOJE)
        servico, _repo, gateway, _e = montar(a_vencida, a_futura)

        relatorio = servico.renovar_vencidas()

        assert relatorio.cobradas == 1
        assert [c for c, _v in gateway.cobrancas] == ["ana@ex.br"]

    def test_soma_o_arrecadado(self):
        servico, *_ = montar(vencida("a1", "ana@ex.br", "pro"), vencida("a2", "b@ex.br", "basico"))
        relatorio = servico.renovar_vencidas()
        assert relatorio.total_arrecadado == Dinheiro.de_reais("69,80")  # 49,90 + 19,90

    def test_persiste_o_novo_vencimento(self):
        servico, repo, *_ = montar(vencida("a1", "ana@ex.br"))
        servico.renovar_vencidas()
        salva = repo.buscar("a1")
        assert salva is not None
        assert salva.proxima_cobranca == HOJE + timedelta(days=30)

    def test_notifica_o_cliente_com_o_id_da_transacao(self):
        servico, _r, _g, espiao = montar(vencida("a1", "ana@ex.br"))
        servico.renovar_vencidas()
        assert espiao.assuntos_de("ana@ex.br") == ["Pagamento confirmado"]
        assert "tx-1" in espiao.mensagens[0][2]

    def test_lista_vazia_nao_chama_o_gateway(self):
        servico, _r, gateway, espiao = montar()
        relatorio = servico.renovar_vencidas()
        assert (relatorio.cobradas, gateway.cobrancas, espiao.mensagens) == (0, [], [])


class TestRecusa:
    def test_recusa_deixa_inadimplente_e_nao_arrecada(self):
        servico, repo, *_ = montar(vencida("a1", "ana@ex.br"), gateway=GatewayFalso(aprovar=False))
        relatorio = servico.renovar_vencidas()
        salva = repo.buscar("a1")
        assert relatorio.recusadas == 1
        assert relatorio.total_arrecadado.centavos == 0
        assert salva is not None and salva.estado is Estado.INADIMPLENTE

    def test_terceira_recusa_cancela_e_avisa(self):
        a = vencida("a1", "ana@ex.br")
        a.tentativas_falhas = 2
        a.estado = Estado.INADIMPLENTE
        servico, repo, _g, espiao = montar(a, gateway=GatewayFalso(aprovar=False))

        relatorio = servico.renovar_vencidas()

        salva = repo.buscar("a1")
        assert relatorio.canceladas == 1
        assert salva is not None and salva.estado is Estado.CANCELADA
        assert espiao.assuntos_de("ana@ex.br") == ["Assinatura cancelada"]

    def test_a_recusa_de_um_cliente_nao_impede_a_cobranca_do_outro(self):
        """Isolamento de falha: o laço não pode abortar no primeiro problema."""
        servico, repo, *_ = montar(
            vencida("a1", "ruim@ex.br"),
            vencida("a2", "boa@ex.br"),
            gateway=GatewayFalso(falhar_para={"ruim@ex.br"}),
        )
        relatorio = servico.renovar_vencidas()
        assert (relatorio.cobradas, relatorio.recusadas) == (1, 1)
        boa = repo.buscar("a2")
        assert boa is not None and boa.ciclos_pagos == 1


class TestFalhaDeInfraestrutura:
    def test_gateway_fora_do_ar_nao_pune_o_cliente(self):
        """A distinção mais importante deste serviço.

        "Cartão recusado" é culpa do cliente e conta tentativa.
        "Gateway caiu" é culpa nossa e **não** conta. Sem este teste, um
        incidente de 20 minutos no provedor cancelaria assinaturas em massa —
        é um bug que já aconteceu em empresas reais.
        """
        servico, repo, _g, espiao = montar(vencida("a1", "ana@ex.br"), gateway=GatewayQueExplode())

        relatorio = servico.renovar_vencidas()

        salva = repo.buscar("a1")
        assert relatorio.com_erro == 1
        assert relatorio.recusadas == 0
        assert salva is not None
        assert salva.tentativas_falhas == 0
        assert salva.estado is Estado.ATIVA
        assert espiao.assuntos_de("ana@ex.br") == ["Não conseguimos processar sua cobrança hoje"]

    def test_erro_em_um_cliente_nao_interrompe_o_lote(self):
        class GatewayInstavel:
            def __init__(self):
                self.chamadas = 0

            def cobrar(self, cliente, valor):
                self.chamadas += 1
                if self.chamadas == 1:
                    raise ConnectionResetError("conexão caiu")
                return Cobranca(True, f"tx-{self.chamadas}")

        servico, *_ = montar(
            vencida("a1", "ana@ex.br"), vencida("a2", "bruno@ex.br"), gateway=GatewayInstavel()
        )
        relatorio = servico.renovar_vencidas()
        assert (relatorio.com_erro, relatorio.cobradas) == (1, 1)


class TestComMockDeVerdade:
    """Quando o mock do `unittest.mock` é a ferramenta certa.

    Aqui o que interessa é a **interação**: o gateway recebeu o cliente e o
    valor corretos? Isso não deixa rastro no estado do serviço, então verificar
    a chamada é legítimo.
    """

    def test_gateway_recebe_cliente_e_valor_do_plano(self):
        gateway = Mock()
        gateway.cobrar.return_value = Cobranca(True, "tx-abc")
        repo = RepositorioMemoria([vencida("a1", "ana@ex.br", "basico")])
        servico = ServicoRenovacao(repo, gateway, RelogioFixo(HOJE), NotificadorEspiao())

        servico.renovar_vencidas()

        gateway.cobrar.assert_called_once_with("ana@ex.br", Dinheiro(1990))

    def test_ordem_das_cobrancas_segue_a_ordem_do_repositorio(self):
        gateway = Mock()
        gateway.cobrar.return_value = Cobranca(True, "tx")
        repo = RepositorioMemoria([vencida("a2", "b@ex.br"), vencida("a1", "a@ex.br")])
        servico = ServicoRenovacao(repo, gateway, RelogioFixo(HOJE), NotificadorEspiao())

        servico.renovar_vencidas()

        assert gateway.cobrar.call_args_list == [
            call("a@ex.br", Dinheiro(4990)),
            call("b@ex.br", Dinheiro(4990)),
        ]

    def test_mock_sem_spec_aceita_metodo_que_nao_existe(self):
        """Demonstração de uma armadilha, não de uma boa prática.

        `Mock()` responde a qualquer atributo. Se o contrato mudar de `cobrar`
        para `criar_cobranca`, o mock continua "funcionando" e o teste passa
        enquanto a produção quebra. A correção é `spec=`/`autospec`.
        """
        frouxo = Mock()
        frouxo.metodo_que_nunca_existiu()  # não levanta nada

        from unittest.mock import create_autospec

        from assinaturas.gateway import GatewayHttp

        rigoroso = create_autospec(GatewayHttp, instance=True)
        with pytest.raises(AttributeError):
            rigoroso.metodo_que_nunca_existiu()


class TestCupons:
    def test_aplica_desconto_do_cupom(self, cupons):
        servico, *_ = montar(vencida("a1", "ana@ex.br"), cupons=cupons)
        assinatura = vencida("a1", "ana@ex.br")
        assert servico.preco_a_cobrar(assinatura, "BEMVINDO10") == Dinheiro.de_reais("44,91")

    def test_sem_cupom_cobra_o_preco_cheio(self, cupons):
        servico, *_ = montar(cupons=cupons)
        assert servico.preco_a_cobrar(vencida("a1", "a@ex.br")) == Dinheiro.de_reais("49,90")

    def test_cupom_inexistente_explode(self, cupons):
        servico, *_ = montar(cupons=cupons)
        with pytest.raises(CupomInvalido, match="não existe"):
            servico.preco_a_cobrar(vencida("a1", "a@ex.br"), "INVENTADO")

    def test_cupom_expirado_explode_usando_o_relogio_injetado(self, cupons):
        servico, *_ = montar(cupons=cupons)
        with pytest.raises(CupomInvalido, match="expirou"):
            servico.preco_a_cobrar(vencida("a1", "a@ex.br"), "EXPIRADO")

    def test_cupom_de_uso_unico_nao_vale_no_segundo_ciclo(self, cupons):
        servico, *_ = montar(cupons=cupons)
        a = vencida("a1", "a@ex.br")
        a.ciclos_pagos = 1
        with pytest.raises(CupomInvalido, match="esgotado"):
            servico.preco_a_cobrar(a, "BEMVINDO10")


class TestRelatorio:
    def test_formata_em_uma_linha_legivel(self):
        servico, *_ = montar(vencida("a1", "a@ex.br", "basico"))
        assert str(servico.renovar_vencidas()) == (
            "1 cobradas (R$ 19,90), 0 recusadas, 0 canceladas, 0 com erro"
        )
