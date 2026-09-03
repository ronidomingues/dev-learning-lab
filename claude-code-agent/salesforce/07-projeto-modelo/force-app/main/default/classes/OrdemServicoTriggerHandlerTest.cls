/**
 * Testes do trigger handler.
 *
 * Destaque: o método bulk_200Ordens_respeitaLimites é o teste que pega o bug real.
 * Um handler escrito com SOQL dentro de laço passa em todos os outros testes e falha
 * só neste — que é exatamente o que acontece no primeiro import de produção.
 */
@isTest
private class OrdemServicoTriggerHandlerTest {

    @isTest
    static void abrirOS_colocaEquipamentoEmManutencao() {
        TestDataFactory.Cenario c = TestDataFactory.cenarioBasico(0);

        Test.startTest();
        insert TestDataFactory.ordens(1, c.equipamento.Id, 'Normal');
        Test.stopTest();

        Equipamento__c eq = [
            SELECT Status__c, OS_Abertas__c FROM Equipamento__c WHERE Id = :c.equipamento.Id
        ];
        Assert.areEqual('Em manutencao', eq.Status__c);
        Assert.areEqual(1, eq.OS_Abertas__c, 'O rollup nativo deveria contar 1');
    }

    @isTest
    static void concluirUltimaOS_voltaParaOperacional() {
        TestDataFactory.Cenario c = TestDataFactory.cenarioBasico(1);

        Equipamento__c antes = [
            SELECT Status__c FROM Equipamento__c WHERE Id = :c.equipamento.Id
        ];
        Assert.areEqual('Em manutencao', antes.Status__c, 'Pré-condição do teste');

        Test.startTest();
        update new Ordem_Servico__c(
            Id = c.ordens[0].Id, Status__c = 'Concluida', Horas_Gastas__c = 2);
        Test.stopTest();

        Equipamento__c depois = [
            SELECT Status__c, Ultima_Manutencao__c, OS_Abertas__c
            FROM Equipamento__c WHERE Id = :c.equipamento.Id
        ];
        Assert.areEqual('Operacional', depois.Status__c);
        Assert.areEqual(Date.today(), depois.Ultima_Manutencao__c,
            'Data da última manutenção deve ser carimbada ao fechar a última OS');
        Assert.areEqual(0, depois.OS_Abertas__c);
    }

    @isTest
    static void concluirUmaDeDuas_mantemEmManutencao() {
        TestDataFactory.Cenario c = TestDataFactory.cenarioBasico(2);

        Test.startTest();
        update new Ordem_Servico__c(
            Id = c.ordens[0].Id, Status__c = 'Concluida', Horas_Gastas__c = 1);
        Test.stopTest();

        Equipamento__c eq = [
            SELECT Status__c, Ultima_Manutencao__c
            FROM Equipamento__c WHERE Id = :c.equipamento.Id
        ];
        Assert.areEqual('Em manutencao', eq.Status__c,
            'Ainda há uma OS aberta — o equipamento não pode voltar a operar');
        Assert.isNull(eq.Ultima_Manutencao__c,
            'Data só é carimbada quando a ÚLTIMA OS fecha');
    }

    @isTest
    static void cancelarOS_contaComoFechada() {
        TestDataFactory.Cenario c = TestDataFactory.cenarioBasico(1);

        Test.startTest();
        update new Ordem_Servico__c(Id = c.ordens[0].Id, Status__c = 'Cancelada');
        Test.stopTest();

        Equipamento__c eq = [
            SELECT Status__c FROM Equipamento__c WHERE Id = :c.equipamento.Id
        ];
        Assert.areEqual('Operacional', eq.Status__c,
            'Cancelada é status terminal — conta como fechada');
    }

    @isTest
    static void equipamentoDescartado_naoVoltaSozinho() {
        TestDataFactory.Cenario c = TestDataFactory.cenarioBasico(1);
        // Descarta o equipamento com a OS ainda aberta.
        OrdemServicoTriggerHandler.bypass = true;
        update new Equipamento__c(Id = c.equipamento.Id, Status__c = 'Descartado');
        OrdemServicoTriggerHandler.bypass = false;

        Test.startTest();
        update new Ordem_Servico__c(
            Id = c.ordens[0].Id, Status__c = 'Concluida', Horas_Gastas__c = 1);
        Test.stopTest();

        Equipamento__c eq = [
            SELECT Status__c FROM Equipamento__c WHERE Id = :c.equipamento.Id
        ];
        Assert.areEqual('Descartado', eq.Status__c,
            'Equipamento descartado não pode voltar a Operacional automaticamente');
    }

    @isTest
    static void bypass_desligaToda_automacao() {
        TestDataFactory.Cenario c = TestDataFactory.cenarioBasico(0);

        Test.startTest();
        OrdemServicoTriggerHandler.bypass = true;
        try {
            List<Ordem_Servico__c> os = TestDataFactory.ordens(1, c.equipamento.Id, 'Normal');
            os[0].Abertura__c = null;      // o handler preencheria; com bypass, não
            insert os;

            Ordem_Servico__c criada = [
                SELECT Abertura__c FROM Ordem_Servico__c WHERE Id = :os[0].Id
            ];
            Assert.isNull(criada.Abertura__c, 'Com bypass, o before insert não roda');

            Equipamento__c eq = [
                SELECT Status__c FROM Equipamento__c WHERE Id = :c.equipamento.Id
            ];
            Assert.areEqual('Operacional', eq.Status__c,
                'Com bypass, o equipamento não é sincronizado');
        } finally {
            // finally: se o teste falhar no meio, o bypass NÃO fica ligado para os
            // testes seguintes. Estáticos sobrevivem dentro da mesma execução.
            OrdemServicoTriggerHandler.bypass = false;
        }
        Test.stopTest();
    }

    /**
     * O TESTE QUE IMPORTA.
     *
     * 200 ordens em 20 equipamentos, num único DML. Se o handler tiver SOQL ou DML
     * dentro de laço, este teste estoura os governor limits e falha. Nenhum outro pega.
     */
    @isTest
    static void bulk_200Ordens_respeitaLimites() {
        List<Account> contas = TestDataFactory.contas(1);
        insert contas;

        List<Equipamento__c> equipamentos =
            TestDataFactory.equipamentos(20, contas[0].Id, 'Baixa');
        insert equipamentos;

        List<Ordem_Servico__c> ordens = new List<Ordem_Servico__c>();
        for (Equipamento__c eq : equipamentos) {
            ordens.addAll(TestDataFactory.ordens(10, eq.Id, 'Normal'));   // 20 × 10 = 200
        }

        Test.startTest();
        Integer soqlAntes = Limits.getQueries();
        Integer dmlAntes  = Limits.getDmlStatements();

        insert ordens;

        Integer soqlUsadas = Limits.getQueries()       - soqlAntes;
        Integer dmlUsados  = Limits.getDmlStatements() - dmlAntes;
        Test.stopTest();

        Assert.areEqual(200, ordens.size());
        // Números folgados de propósito: o teste protege contra a ordem de grandeza
        // errada (uma consulta por registro), não contra uma consulta a mais.
        Assert.isTrue(soqlUsadas <= 10,
            'Handler não está bulkificado: ' + soqlUsadas + ' consultas para 200 registros');
        Assert.isTrue(dmlUsados <= 5,
            'Handler não está bulkificado: ' + dmlUsados + ' DMLs para 200 registros');

        Integer emManutencao = [
            SELECT COUNT() FROM Equipamento__c
            WHERE Id IN :equipamentos AND Status__c = 'Em manutencao'
        ];
        Assert.areEqual(20, emManutencao, 'Todos os 20 equipamentos deveriam estar em manutenção');
    }
}
