/**
 * Testes do Selector.
 *
 * Um Selector merece teste próprio: ele é o único lugar com SOQL, e uma consulta
 * errada aqui contamina todas as camadas acima em silêncio.
 */
@isTest
private class OrdemServicoSelectorTest {

    @isTest
    static void porEquipamento_ordenaPorAberturaDesc() {
        TestDataFactory.Cenario c = TestDataFactory.cenarioBasico(3);

        List<Ordem_Servico__c> r =
            OrdemServicoSelector.porEquipamento(c.equipamento.Id, false);

        Assert.areEqual(3, r.size());
        Assert.isTrue(r[0].Abertura__c >= r[1].Abertura__c,
            'Deveria vir da mais recente para a mais antiga');
    }

    @isTest
    static void porEquipamento_idNulo_retornaListaVazia() {
        // Guarda de entrada: não pode lançar exceção nem consultar a org inteira.
        Assert.areEqual(0, OrdemServicoSelector.porEquipamento(null, true).size());
    }

    @isTest
    static void porNumeroSerie_inexistente_retornaNull() {
        // A armadilha clássica: SOQL atribuída direto a um SObject lança QueryException
        // quando não há linhas. O Selector devolve null de propósito.
        Assert.isNull(OrdemServicoSelector.porNumeroSerie('SN-QUE-NAO-EXISTE'));
        Assert.isNull(OrdemServicoSelector.porNumeroSerie('   '));
    }

    @isTest
    static void porNumeroSerie_existente_retornaRegistro() {
        List<Equipamento__c> eqs = TestDataFactory.equipamentos(1, null, 'Alta');
        insert eqs;

        Equipamento__c achado = OrdemServicoSelector.porNumeroSerie(eqs[0].Numero_Serie__c);

        Assert.isNotNull(achado);
        Assert.areEqual(eqs[0].Id, achado.Id);
        Assert.areEqual('Alta', achado.Criticidade__c);
    }

    @isTest
    static void contarAbertas_ignoraOrdensInformadas() {
        TestDataFactory.Cenario c = TestDataFactory.cenarioBasico(3);
        Set<Id> eqIds = new Set<Id>{ c.equipamento.Id };

        Map<Id, Integer> semIgnorar =
            OrdemServicoSelector.contarAbertasPorEquipamento(eqIds, null);
        Map<Id, Integer> ignorandoUma =
            OrdemServicoSelector.contarAbertasPorEquipamento(
                eqIds, new Set<Id>{ c.ordens[0].Id });

        Assert.areEqual(3, semIgnorar.get(c.equipamento.Id));
        Assert.areEqual(2, ignorandoUma.get(c.equipamento.Id),
            'A ordem informada em "ignorar" não deve ser contada');
    }

    @isTest
    static void colecoesVazias_naoConsultamNada() {
        Integer antes = Limits.getQueries();

        OrdemServicoSelector.porIds(new Set<Id>());
        OrdemServicoSelector.equipamentosPorIds(null);
        OrdemServicoSelector.contarAbertasPorEquipamento(new Set<Id>(), null);

        Assert.areEqual(antes, Limits.getQueries(),
            'Guardas de entrada devem evitar consultas desnecessárias');
    }
}
