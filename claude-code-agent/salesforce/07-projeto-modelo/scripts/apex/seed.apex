/**
 * Dados de exemplo do projeto-modelo.
 *
 * IDEMPOTENTE: pode ser executado quantas vezes quiser. Usa upsert pela chave externa
 * Numero_Serie__c, então rodar de novo atualiza em vez de duplicar.
 *
 * Rode com:  sf apex run --file scripts/apex/seed.apex
 */

// A automação é desligada durante a carga: o handler recalcularia status a cada DML,
// e aqui nós queremos controlar o estado final explicitamente.
OrdemServicoTriggerHandler.bypass = true;

try {
    // ---------------------------------------------------------------- CONTAS
    List<Account> contas = new List<Account>{
        new Account(Name = 'Padaria Pão de Ouro',      Industry = 'Retail'),
        new Account(Name = 'Hospital Santa Clara',      Industry = 'Healthcare'),
        new Account(Name = 'Metalúrgica Ribeirão S.A.', Industry = 'Manufacturing')
    };
    // Sem chave externa em Account, evitamos duplicar apagando os do seed anterior.
    delete [SELECT Id FROM Account WHERE Name IN ('Padaria Pão de Ouro',
                                                  'Hospital Santa Clara',
                                                  'Metalúrgica Ribeirão S.A.')];
    insert contas;

    Map<String, Id> contaPorNome = new Map<String, Id>();
    for (Account a : contas) {
        contaPorNome.put(a.Name, a.Id);
    }

    // ---------------------------------------------------------- EQUIPAMENTOS
    List<Equipamento__c> equipamentos = new List<Equipamento__c>{
        new Equipamento__c(Numero_Serie__c = 'SN-000101', Criticidade__c = 'Baixa',
            Status__c = 'Operacional', Conta__c = contaPorNome.get('Padaria Pão de Ouro'),
            Ultima_Manutencao__c = Date.today().addDays(-40)),
        new Equipamento__c(Numero_Serie__c = 'SN-000102', Criticidade__c = 'Media',
            Status__c = 'Operacional', Conta__c = contaPorNome.get('Padaria Pão de Ouro'),
            Ultima_Manutencao__c = Date.today().addDays(-120)),
        new Equipamento__c(Numero_Serie__c = 'SN-000103', Criticidade__c = 'Baixa',
            Status__c = 'Operacional', Conta__c = contaPorNome.get('Padaria Pão de Ouro')),

        new Equipamento__c(Numero_Serie__c = 'SN-000201', Criticidade__c = 'Alta',
            Status__c = 'Operacional', Conta__c = contaPorNome.get('Hospital Santa Clara'),
            Ultima_Manutencao__c = Date.today().addDays(-15)),
        new Equipamento__c(Numero_Serie__c = 'SN-000202', Criticidade__c = 'Alta',
            Status__c = 'Operacional', Conta__c = contaPorNome.get('Hospital Santa Clara')),
        new Equipamento__c(Numero_Serie__c = 'SN-000203', Criticidade__c = 'Media',
            Status__c = 'Fora de operacao', Conta__c = contaPorNome.get('Hospital Santa Clara'),
            Ultima_Manutencao__c = Date.today().addDays(-400)),

        new Equipamento__c(Numero_Serie__c = 'SN-000301', Criticidade__c = 'Alta',
            Status__c = 'Operacional', Conta__c = contaPorNome.get('Metalúrgica Ribeirão S.A.')),
        new Equipamento__c(Numero_Serie__c = 'SN-000302', Criticidade__c = 'Media',
            Status__c = 'Operacional', Conta__c = contaPorNome.get('Metalúrgica Ribeirão S.A.'),
            Ultima_Manutencao__c = Date.today().addDays(-200)),
        new Equipamento__c(Numero_Serie__c = 'SN-000303', Criticidade__c = 'Baixa',
            Status__c = 'Descartado', Conta__c = contaPorNome.get('Metalúrgica Ribeirão S.A.'))
    };

    // upsert pela chave externa: é isto que torna o script idempotente.
    Database.upsert(equipamentos, Equipamento__c.Numero_Serie__c, true);

    Map<String, Id> eqPorSerie = new Map<String, Id>();
    for (Equipamento__c e : [SELECT Id, Numero_Serie__c FROM Equipamento__c
                             WHERE Numero_Serie__c LIKE 'SN-000%']) {
        eqPorSerie.put(e.Numero_Serie__c, e.Id);
    }

    // ------------------------------------------------------ ORDENS DE SERVIÇO
    // Apaga as ordens do seed anterior para não acumular a cada execução.
    delete [SELECT Id FROM Ordem_Servico__c WHERE Equipamento__c IN :eqPorSerie.values()];

    List<Ordem_Servico__c> ordens = new List<Ordem_Servico__c>{
        new Ordem_Servico__c(Equipamento__c = eqPorSerie.get('SN-000102'),
            Status__c = 'Aberta', Prioridade__c = 'Alta',
            Descricao__c = 'Forno não atinge a temperatura programada.',
            Abertura__c = System.now().addHours(-3)),

        new Ordem_Servico__c(Equipamento__c = eqPorSerie.get('SN-000202'),
            Status__c = 'Em andamento', Prioridade__c = 'Critica',
            Descricao__c = 'Alarme intermitente na UTI. Técnico em campo.',
            Abertura__c = System.now().addHours(-6)),

        new Ordem_Servico__c(Equipamento__c = eqPorSerie.get('SN-000203'),
            Status__c = 'Aberta', Prioridade__c = 'Alta',
            Descricao__c = 'Equipamento parado desde a última inspeção.',
            Abertura__c = System.now().addDays(-2)),

        new Ordem_Servico__c(Equipamento__c = eqPorSerie.get('SN-000301'),
            Status__c = 'Concluida', Prioridade__c = 'Normal',
            Descricao__c = 'Troca de rolamento.',
            Abertura__c = System.now().addDays(-10),
            Conclusao__c = System.now().addDays(-10).addHours(5),
            Horas_Gastas__c = 5),

        new Ordem_Servico__c(Equipamento__c = eqPorSerie.get('SN-000302'),
            Status__c = 'Concluida', Prioridade__c = 'Baixa',
            Descricao__c = 'Lubrificação preventiva.',
            Abertura__c = System.now().addDays(-30),
            Conclusao__c = System.now().addDays(-29),
            Horas_Gastas__c = 1.5),

        new Ordem_Servico__c(Equipamento__c = eqPorSerie.get('SN-000101'),
            Status__c = 'Cancelada', Prioridade__c = 'Normal',
            Descricao__c = 'Chamado aberto por engano.',
            Abertura__c = System.now().addDays(-5),
            Conclusao__c = System.now().addDays(-5))
    };
    insert ordens;

} finally {
    // finally: se qualquer DML acima falhar, o bypass NÃO fica ligado para o resto
    // da org. Estáticos sobrevivem por toda a transação.
    OrdemServicoTriggerHandler.bypass = false;
}

// ------------------------------------------------------------- SINCRONIZAÇÃO
// Com o bypass religado, um toque em cada ordem faz o handler recalcular o status
// dos equipamentos a partir do estado real — em vez de nós carimbarmos na mão.
List<Ordem_Servico__c> paraTocar = [
    SELECT Id, Status__c FROM Ordem_Servico__c
    WHERE Equipamento__r.Numero_Serie__c LIKE 'SN-000%'
];
update paraTocar;

Integer qtdContas = [
    SELECT COUNT() FROM Account
    WHERE Name IN ('Padaria Pão de Ouro', 'Hospital Santa Clara', 'Metalúrgica Ribeirão S.A.')
];
Integer qtdEquipamentos = [SELECT COUNT() FROM Equipamento__c WHERE Numero_Serie__c LIKE 'SN-000%'];
Integer qtdOrdens       = [SELECT COUNT() FROM Ordem_Servico__c];

System.debug('Seed concluído: ' + qtdContas + ' contas, ' +
             qtdEquipamentos + ' equipamentos, ' +
             qtdOrdens + ' ordens de serviço.');
