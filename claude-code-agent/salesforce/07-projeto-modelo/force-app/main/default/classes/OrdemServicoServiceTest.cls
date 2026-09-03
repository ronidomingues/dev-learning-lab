/**
 * Testes da camada de serviço.
 *
 * O que estes testes garantem (o contrato do serviço):
 *  - abrir valida entrada e deriva prioridade da criticidade;
 *  - concluir aplica regras e devolve falha parcial detalhada;
 *  - a segurança é respeitada sob um usuário não-administrador.
 */
@isTest
private class OrdemServicoServiceTest {

    // ------------------------------------------------------------- ABRIR

    @isTest
    static void abrir_criaOrdemComPrioridadeDerivada() {
        TestDataFactory.Cenario c = TestDataFactory.cenarioBasico(0);

        Test.startTest();
        List<Ordem_Servico__c> criadas = OrdemServicoService.abrir(
            new List<OrdemServicoService.PedidoAbertura>{
                new OrdemServicoService.PedidoAbertura(c.equipamento.Id, 'Vazamento')
            }
        );
        Test.stopTest();

        Assert.areEqual(1, criadas.size(), 'Deveria criar uma ordem');
        Ordem_Servico__c os = [
            SELECT Status__c, Prioridade__c, Abertura__c, Descricao__c
            FROM Ordem_Servico__c WHERE Id = :criadas[0].Id
        ];
        Assert.areEqual('Aberta', os.Status__c);
        // equipamento com criticidade Media → prioridade Alta
        Assert.areEqual('Alta', os.Prioridade__c, 'Prioridade deve vir da criticidade');
        Assert.isNotNull(os.Abertura__c, 'Abertura deve ser preenchida pelo trigger');
        Assert.areEqual('Vazamento', os.Descricao__c);
    }

    @isTest
    static void abrir_respeitaPrioridadeExplicita() {
        TestDataFactory.Cenario c = TestDataFactory.cenarioBasico(0);

        List<Ordem_Servico__c> criadas = OrdemServicoService.abrir(
            new List<OrdemServicoService.PedidoAbertura>{
                new OrdemServicoService.PedidoAbertura(c.equipamento.Id, 'Ruído')
                    .comPrioridade('Baixa')
            }
        );

        Ordem_Servico__c os = [
            SELECT Prioridade__c, SLA_Horas__c FROM Ordem_Servico__c WHERE Id = :criadas[0].Id
        ];
        Assert.areEqual('Baixa', os.Prioridade__c);
        Assert.areEqual(72, os.SLA_Horas__c, 'SLA de prioridade Baixa é 72 h');
    }

    @isTest
    static void abrir_listaVazia_lancaExcecao() {
        try {
            OrdemServicoService.abrir(new List<OrdemServicoService.PedidoAbertura>());
            Assert.fail('Deveria ter lançado OrdemServicoException');
        } catch (OrdemServicoService.OrdemServicoException e) {
            Assert.isTrue(e.getMessage().contains('Nenhum pedido'),
                          'Mensagem inesperada: ' + e.getMessage());
        }
    }

    @isTest
    static void abrir_equipamentoDescartado_lancaExcecao() {
        TestDataFactory.Cenario c = TestDataFactory.cenarioBasico(0);
        update new Equipamento__c(Id = c.equipamento.Id, Status__c = 'Descartado');

        try {
            OrdemServicoService.abrir(
                new List<OrdemServicoService.PedidoAbertura>{
                    new OrdemServicoService.PedidoAbertura(c.equipamento.Id, 'x')
                }
            );
            Assert.fail('Deveria ter recusado equipamento descartado');
        } catch (OrdemServicoService.OrdemServicoException e) {
            Assert.isTrue(e.getMessage().contains('descartado'));
        }
    }

    // ---------------------------------------------------------- CONCLUIR

    @isTest
    static void concluir_marcaStatusEHoras() {
        TestDataFactory.Cenario c = TestDataFactory.cenarioBasico(1);

        Test.startTest();
        OrdemServicoService.Resultado r =
            OrdemServicoService.concluirUma(c.ordens[0].Id, 3.5);
        Test.stopTest();

        Assert.areEqual(1, r.concluidas);
        Assert.isFalse(r.temFalha(), 'Não deveria haver falhas');

        Ordem_Servico__c os = [
            SELECT Status__c, Conclusao__c, Horas_Gastas__c
            FROM Ordem_Servico__c WHERE Id = :c.ordens[0].Id
        ];
        Assert.areEqual('Concluida', os.Status__c);
        Assert.areEqual(3.5, os.Horas_Gastas__c);
        Assert.isNotNull(os.Conclusao__c);
    }

    @isTest
    static void concluir_horasInvalidas_registraFalha() {
        TestDataFactory.Cenario c = TestDataFactory.cenarioBasico(1);

        OrdemServicoService.Resultado zero =
            OrdemServicoService.concluirUma(c.ordens[0].Id, 0);
        Assert.areEqual(0, zero.concluidas);
        Assert.areEqual(1, zero.falhas.size());
        Assert.isTrue(zero.falhas[0].motivo.contains('maiores que zero'));

        OrdemServicoService.Resultado demais =
            OrdemServicoService.concluirUma(c.ordens[0].Id, 99);
        Assert.areEqual(0, demais.concluidas);
        Assert.isTrue(demais.falhas[0].motivo.contains('limite'));
    }

    @isTest
    static void concluir_jaConcluida_registraFalha() {
        TestDataFactory.Cenario c = TestDataFactory.cenarioBasico(1);
        OrdemServicoService.concluirUma(c.ordens[0].Id, 1);

        OrdemServicoService.Resultado r =
            OrdemServicoService.concluirUma(c.ordens[0].Id, 2);

        Assert.areEqual(0, r.concluidas);
        Assert.isTrue(r.falhas[0].motivo.contains('Já está'));
    }

    @isTest
    static void concluir_falhaParcial_naoDerrubaOsBons() {
        TestDataFactory.Cenario c = TestDataFactory.cenarioBasico(3);

        Map<Id, Decimal> pedido = new Map<Id, Decimal>{
            c.ordens[0].Id => 2,      // válido
            c.ordens[1].Id => 0,      // inválido: horas zero
            c.ordens[2].Id => 4       // válido
        };

        Test.startTest();
        OrdemServicoService.Resultado r = OrdemServicoService.concluir(pedido);
        Test.stopTest();

        Assert.areEqual(2, r.concluidas, 'Os dois válidos deveriam passar');
        Assert.areEqual(1, r.falhas.size(), 'Só o inválido deveria falhar');
    }

    @isTest
    static void concluir_mapaVazio_lancaExcecao() {
        try {
            OrdemServicoService.concluir(new Map<Id, Decimal>());
            Assert.fail('Deveria ter lançado');
        } catch (OrdemServicoService.OrdemServicoException e) {
            Assert.isTrue(e.getMessage().contains('Nenhuma ordem'));
        }
    }

    // ------------------------------------------------------ PONTE COM LWC

    @isTest
    static void listarPorEquipamento_filtraAbertas() {
        TestDataFactory.Cenario c = TestDataFactory.cenarioBasico(3);
        OrdemServicoService.concluirUma(c.ordens[0].Id, 1);

        List<Ordem_Servico__c> todas =
            OrdemServicoService.listarPorEquipamento(c.equipamento.Id, false);
        List<Ordem_Servico__c> abertas =
            OrdemServicoService.listarPorEquipamento(c.equipamento.Id, true);

        Assert.areEqual(3, todas.size(),   'Sem filtro, devolve todas');
        Assert.areEqual(2, abertas.size(), 'Com filtro, exclui a concluída');
    }

    @isTest
    static void concluirDoPainel_erro_viraAuraHandledException() {
        TestDataFactory.Cenario c = TestDataFactory.cenarioBasico(1);
        try {
            OrdemServicoService.concluirDoPainel(c.ordens[0].Id, -1);
            Assert.fail('Deveria ter lançado AuraHandledException');
        } catch (AuraHandledException e) {
            // A mensagem legível é o ponto: sem AuraHandledException o LWC receberia
            // "Script-thrown exception" e o usuário não saberia o que houve.
            Assert.isNotNull(e.getMessage());
        }
    }

    // --------------------------------------------------------- SEGURANÇA

    @isTest
    static void usuarioPadrao_comPermissionSet_consegueAbrirEConcluir() {
        TestDataFactory.Cenario c = TestDataFactory.cenarioBasico(0);
        User tecnico = TestDataFactory.usuarioPadrao();

        Test.startTest();
        System.runAs(tecnico) {
            List<Ordem_Servico__c> criadas = OrdemServicoService.abrir(
                new List<OrdemServicoService.PedidoAbertura>{
                    new OrdemServicoService.PedidoAbertura(c.equipamento.Id, 'Sob usuário padrão')
                }
            );
            Assert.areEqual(1, criadas.size(),
                'Usuário com o permission set deveria conseguir abrir OS');

            OrdemServicoService.Resultado r =
                OrdemServicoService.concluirUma(criadas[0].Id, 1.5);
            Assert.areEqual(1, r.concluidas);
        }
        Test.stopTest();
    }
}
