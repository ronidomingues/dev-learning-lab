"""Teste de **integração**: exercita o SQLite de verdade.

Diferenças em relação aos testes unitários deste projeto:
- toca I/O (um arquivo, ou `:memory:`);
- é mais lento (milissegundos em vez de microssegundos);
- está marcado com `@pytest.mark.integracao`, para poder ser excluído
  no laço rápido de desenvolvimento: `pytest -m "not integracao"`.

Aqui testamos o que o fake em memória **não** pode garantir: SQL correto,
serialização de datas, `ON CONFLICT DO UPDATE`, índice usado pela consulta.
"""

from __future__ import annotations

from datetime import date, timedelta

import pytest

from assinaturas.assinatura import Assinatura, Estado
from assinaturas.plano import CATALOGO
from assinaturas.repositorio import RepositorioSQLite

pytestmark = pytest.mark.integracao  # aplica o marcador a TODOS os testes do arquivo

HOJE = date(2026, 8, 12)


@pytest.fixture
def repo():
    """Banco novo por teste. `yield` + fechamento = teardown garantido."""
    r = RepositorioSQLite(":memory:")
    yield r
    r.fechar()


@pytest.fixture
def repo_em_arquivo(tmp_path):
    """Versão em arquivo, para provar que os dados sobrevivem à reconexão.

    `tmp_path` é uma fixture nativa do pytest: entrega um diretório temporário
    exclusivo daquele teste e o limpa depois. Nunca escreva em caminho fixo.
    """
    caminho = tmp_path / "teste.db"
    r = RepositorioSQLite(str(caminho))
    yield r, str(caminho)
    r.fechar()


def nova(id: str, dias_para_vencer: int = 30, estado: Estado = Estado.ATIVA) -> Assinatura:
    a = Assinatura.criar(id, f"{id}@ex.br", CATALOGO["pro"], HOJE)
    a.proxima_cobranca = HOJE + timedelta(days=dias_para_vencer)
    a.estado = estado
    return a


class TestPersistencia:
    def test_salva_e_recupera(self, repo: RepositorioSQLite):
        repo.salvar(nova("a1"))
        recuperada = repo.buscar("a1")
        assert recuperada is not None
        assert recuperada.cliente == "a1@ex.br"

    def test_id_inexistente_devolve_none(self, repo: RepositorioSQLite):
        assert repo.buscar("nao-existe") is None

    def test_salvar_duas_vezes_atualiza_em_vez_de_duplicar(self, repo: RepositorioSQLite):
        a = nova("a1")
        repo.salvar(a)
        a.registrar_pagamento(HOJE)
        repo.salvar(a)  # exercita o ON CONFLICT DO UPDATE
        recuperada = repo.buscar("a1")
        assert recuperada is not None and recuperada.ciclos_pagos == 1

    def test_a_data_faz_ida_e_volta_sem_perder_o_dia(self, repo: RepositorioSQLite):
        """SQLite não tem tipo DATE. Guardamos ISO-8601 e este teste prova que volta igual."""
        a = nova("a1")
        a.proxima_cobranca = date(2026, 2, 28)
        repo.salvar(a)
        recuperada = repo.buscar("a1")
        assert recuperada is not None and recuperada.proxima_cobranca == date(2026, 2, 28)

    def test_dados_sobrevivem_a_reconexao(self, repo_em_arquivo):
        repo, caminho = repo_em_arquivo
        repo.salvar(nova("a1"))
        repo.fechar()

        with RepositorioSQLite(caminho) as outro:
            assert outro.buscar("a1") is not None

    def test_esquema_e_idempotente(self, repo_em_arquivo):
        """Abrir o mesmo banco duas vezes não pode explodir no CREATE TABLE."""
        _repo, caminho = repo_em_arquivo
        with RepositorioSQLite(caminho):
            pass
        with RepositorioSQLite(caminho):
            pass  # se o CREATE não tivesse IF NOT EXISTS, aqui quebraria


class TestConsultaDeVencidas:
    def test_traz_a_que_vence_hoje_e_ignora_a_de_amanha(self, repo: RepositorioSQLite):
        repo.salvar(nova("hoje", dias_para_vencer=0))
        repo.salvar(nova("amanha", dias_para_vencer=1))
        assert [a.id for a in repo.listar_vencidas(HOJE)] == ["hoje"]

    def test_traz_as_atrasadas(self, repo: RepositorioSQLite):
        repo.salvar(nova("atrasada", dias_para_vencer=-30))
        assert len(repo.listar_vencidas(HOJE)) == 1

    @pytest.mark.parametrize("estado", [Estado.PAUSADA, Estado.CANCELADA])
    def test_ignora_pausadas_e_canceladas(self, repo: RepositorioSQLite, estado: Estado):
        repo.salvar(nova("a1", dias_para_vencer=-1, estado=estado))
        assert repo.listar_vencidas(HOJE) == []

    def test_inclui_inadimplentes_para_retentativa(self, repo: RepositorioSQLite):
        repo.salvar(nova("a1", dias_para_vencer=-1, estado=Estado.INADIMPLENTE))
        assert len(repo.listar_vencidas(HOJE)) == 1

    def test_ordena_por_id_para_ser_deterministico(self, repo: RepositorioSQLite):
        for id_ in ("c", "a", "b"):
            repo.salvar(nova(id_, dias_para_vencer=0))
        assert [a.id for a in repo.listar_vencidas(HOJE)] == ["a", "b", "c"]

    def test_comparacao_de_data_como_texto_funciona_por_ser_iso8601(self, repo: RepositorioSQLite):
        """Cinco porquês, último nível: por que `proxima_cobranca <= ?` funciona em TEXT?

        Porque ISO-8601 (`AAAA-MM-DD`) tem a propriedade de que a ordem
        lexicográfica coincide com a ordem cronológica — campos de largura fixa,
        do mais significativo para o menos. Com `DD/MM/AAAA` isso seria falso e
        a consulta traria lixo. Este teste trava a escolha do formato.
        """
        repo.salvar(nova("dezembro_ano_passado"))
        a = repo.buscar("dezembro_ano_passado")
        assert a is not None
        a.proxima_cobranca = date(2025, 12, 31)
        repo.salvar(a)
        assert [x.id for x in repo.listar_vencidas(date(2026, 1, 1))] == ["dezembro_ano_passado"]


class TestIntegracaoDoServicoComBancoReal:
    def test_ciclo_completo_com_sqlite(self, repo: RepositorioSQLite):
        """Um teste de integração de ponta a ponta do lote de cobrança.

        É o único teste que junta serviço + banco. Um só, de propósito: a lógica
        já está coberta pelos unitários; aqui só se verifica que a fiação existe.
        """
        from assinaturas.gateway import GatewayFalso
        from assinaturas.relogio import RelogioFixo
        from assinaturas.servico import NotificadorEspiao, ServicoRenovacao

        repo.salvar(nova("a1", dias_para_vencer=0))
        repo.salvar(nova("a2", dias_para_vencer=5))

        servico = ServicoRenovacao(repo, GatewayFalso(), RelogioFixo(HOJE), NotificadorEspiao())
        relatorio = servico.renovar_vencidas()

        assert relatorio.cobradas == 1
        a1 = repo.buscar("a1")
        assert a1 is not None and a1.proxima_cobranca == HOJE + timedelta(days=30)
