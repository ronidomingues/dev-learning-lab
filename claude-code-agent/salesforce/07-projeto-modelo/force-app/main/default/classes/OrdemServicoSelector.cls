/**
 * Camada de acesso a dados do domínio de manutenção.
 *
 * Por que existe: concentrar TODA a SOQL do domínio num lugar só.
 *  - auditar segurança fica trivial (um arquivo, não 40);
 *  - otimizar uma consulta lenta não exige caçá-la pelo projeto inteiro;
 *  - o Service fica testável com um stub deste Selector, sem tocar o banco.
 *
 * Convenção: nenhum método aqui contém regra de negócio. Só consulta.
 */
public with sharing class OrdemServicoSelector {

    /** Campos padrão da OS. Uma lista só evita divergência entre consultas. */
    private static final String CAMPOS_OS =
        'Id, Name, Status__c, Prioridade__c, Abertura__c, Conclusao__c, ' +
        'Horas_Gastas__c, Descricao__c, SLA_Horas__c, Dentro_SLA__c, ' +
        'Tecnico__c, Tecnico__r.Name, Equipamento__c, Equipamento__r.Name, ' +
        'Equipamento__r.Numero_Serie__c';

    /**
     * Ordens de um equipamento, mais recentes primeiro.
     * @param equipamentoId  Id do equipamento
     * @param apenasAbertas  se true, exclui Concluída e Cancelada
     */
    public static List<Ordem_Servico__c> porEquipamento(Id equipamentoId, Boolean apenasAbertas) {
        if (equipamentoId == null) {
            return new List<Ordem_Servico__c>();
        }
        String soql =
            'SELECT ' + CAMPOS_OS +
            ' FROM Ordem_Servico__c' +
            ' WHERE Equipamento__c = :equipamentoId';

        if (apenasAbertas == true) {
            soql += ' AND Status__c NOT IN (\'Concluida\', \'Cancelada\')';
        }
        soql += ' ORDER BY Abertura__c DESC NULLS LAST LIMIT 200';

        // queryWithBinds com USER_MODE: bind seguro (sem injection) e FLS aplicado.
        return (List<Ordem_Servico__c>) Database.queryWithBinds(
            soql,
            new Map<String, Object>{ 'equipamentoId' => equipamentoId },
            AccessLevel.USER_MODE
        );
    }

    /** Ordens por Id, para operações em lote. Sempre bulk — nunca uma por vez. */
    public static List<Ordem_Servico__c> porIds(Set<Id> ids) {
        if (ids == null || ids.isEmpty()) {
            return new List<Ordem_Servico__c>();
        }
        return [
            SELECT Id, Name, Status__c, Prioridade__c, Abertura__c, Conclusao__c,
                   Horas_Gastas__c, Equipamento__c
            FROM Ordem_Servico__c
            WHERE Id IN :ids
            WITH USER_MODE
        ];
    }

    /**
     * Conta ordens ainda abertas por equipamento.
     * Usado pelo handler para decidir o status do equipamento.
     *
     * @param equipamentoIds equipamentos a avaliar
     * @param ignorar        ordens a desconsiderar (as que estão sendo alteradas agora,
     *                       cujo novo valor ainda não está commitado)
     */
    public static Map<Id, Integer> contarAbertasPorEquipamento(Set<Id> equipamentoIds,
                                                               Set<Id> ignorar) {
        Map<Id, Integer> resultado = new Map<Id, Integer>();
        if (equipamentoIds == null || equipamentoIds.isEmpty()) {
            return resultado;
        }
        for (Id eqId : equipamentoIds) {
            resultado.put(eqId, 0);
        }

        Set<Id> excluir = ignorar == null ? new Set<Id>() : ignorar;

        // SYSTEM_MODE aqui é deliberado e documentado: o status do equipamento precisa
        // refletir TODAS as ordens, inclusive as que o usuário atual não pode ler.
        // Toda exceção a USER_MODE deve ter um comentário como este.
        for (AggregateResult ar : [
            SELECT Equipamento__c eq, COUNT(Id) total
            FROM Ordem_Servico__c
            WHERE Equipamento__c IN :equipamentoIds
              AND Id NOT IN :excluir
              AND Status__c NOT IN ('Concluida', 'Cancelada')
            WITH SYSTEM_MODE
            GROUP BY Equipamento__c
        ]) {
            resultado.put((Id) ar.get('eq'), (Integer) ar.get('total'));
        }
        return resultado;
    }

    /** Equipamentos por Id, com os campos que o handler precisa atualizar. */
    public static Map<Id, Equipamento__c> equipamentosPorIds(Set<Id> ids) {
        if (ids == null || ids.isEmpty()) {
            return new Map<Id, Equipamento__c>();
        }
        return new Map<Id, Equipamento__c>([
            SELECT Id, Name, Numero_Serie__c, Status__c, Criticidade__c,
                   Ultima_Manutencao__c, Conta__c
            FROM Equipamento__c
            WHERE Id IN :ids
            WITH SYSTEM_MODE
        ]);
    }

    /** Equipamento por número de série — a chave usada por integrações. */
    public static Equipamento__c porNumeroSerie(String numeroSerie) {
        if (String.isBlank(numeroSerie)) {
            return null;
        }
        List<Equipamento__c> achados = [
            SELECT Id, Name, Numero_Serie__c, Status__c, Criticidade__c
            FROM Equipamento__c
            WHERE Numero_Serie__c = :numeroSerie
            WITH USER_MODE
            LIMIT 1
        ];
        // Nunca atribua SOQL direto a um SObject: se vier vazio, lança QueryException.
        return achados.isEmpty() ? null : achados[0];
    }
}
