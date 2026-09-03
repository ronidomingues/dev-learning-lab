/**
 * Lógica do OrdemServicoTrigger.
 *
 * Responsabilidade: traduzir o contexto do trigger (Trigger.new, isBefore, isUpdate…)
 * em operações de domínio. Nada mais.
 *
 * Regra que este handler mantém:
 *   equipamento com pelo menos uma OS não terminal  → "Em manutencao"
 *   equipamento sem nenhuma OS aberta               → "Operacional" + Ultima_Manutencao__c
 */
public with sharing class OrdemServicoTriggerHandler {

    /**
     * Interruptor para migração de dados em massa.
     * Sempre religue dentro de um finally — ver 06-exemplos.md #14.
     */
    @TestVisible
    public static Boolean bypass = false;

    /** Guarda contra recursão: o mesmo lote não é reprocessado na mesma transação. */
    private static Set<Id> jaProcessados = new Set<Id>();

    private static final Set<String> STATUS_TERMINAIS =
        new Set<String>{ 'Concluida', 'Cancelada' };

    public static void run() {
        if (bypass) {
            return;
        }

        if (Trigger.isBefore && Trigger.isInsert) {
            preencherAbertura((List<Ordem_Servico__c>) Trigger.new);
        }

        if (Trigger.isBefore && Trigger.isUpdate) {
            marcarConclusao((List<Ordem_Servico__c>) Trigger.new,
                            (Map<Id, Ordem_Servico__c>) Trigger.oldMap);
        }

        if (Trigger.isAfter && (Trigger.isInsert || Trigger.isUpdate || Trigger.isDelete)) {
            List<Ordem_Servico__c> base = Trigger.isDelete
                ? (List<Ordem_Servico__c>) Trigger.old
                : (List<Ordem_Servico__c>) Trigger.new;
            sincronizarStatusDoEquipamento(base);
        }
    }

    // ------------------------------------------------------------- BEFORE

    /** Preenche a abertura quando o chamador não informou. Sem DML: estamos em before. */
    private static void preencherAbertura(List<Ordem_Servico__c> novas) {
        for (Ordem_Servico__c os : novas) {
            if (os.Abertura__c == null) {
                os.Abertura__c = System.now();
            }
        }
    }

    /** Carimba a conclusão quando o status vira terminal por qualquer caminho. */
    private static void marcarConclusao(List<Ordem_Servico__c> novas,
                                        Map<Id, Ordem_Servico__c> antigas) {
        for (Ordem_Servico__c os : novas) {
            Ordem_Servico__c antiga = antigas.get(os.Id);

            Boolean virouTerminal = STATUS_TERMINAIS.contains(os.Status__c)
                                 && !STATUS_TERMINAIS.contains(antiga.Status__c);

            if (virouTerminal && os.Conclusao__c == null) {
                os.Conclusao__c = System.now();
            }
            // Reabertura autorizada (custom permission): limpa a conclusão.
            if (!STATUS_TERMINAIS.contains(os.Status__c)
                && STATUS_TERMINAIS.contains(antiga.Status__c)) {
                os.Conclusao__c = null;
            }
        }
    }

    // -------------------------------------------------------------- AFTER

    /**
     * Ajusta o status do equipamento com base nas ordens ainda abertas.
     *
     * Bulk-safe: 2 consultas e 1 DML, independentemente do tamanho do lote.
     */
    private static void sincronizarStatusDoEquipamento(List<Ordem_Servico__c> ordens) {
        Set<Id> equipamentoIds = new Set<Id>();
        Set<Id> ordensDoLote   = new Set<Id>();

        for (Ordem_Servico__c os : ordens) {
            if (os.Equipamento__c != null) {
                equipamentoIds.add(os.Equipamento__c);
            }
            if (os.Id != null) {
                ordensDoLote.add(os.Id);
            }
        }

        // Também considera o equipamento ANTIGO, se a OS foi reparentada.
        if (Trigger.isUpdate && Trigger.oldMap != null) {
            for (SObject antigo : Trigger.old) {
                Id eqAntigo = (Id) antigo.get('Equipamento__c');
                if (eqAntigo != null) {
                    equipamentoIds.add(eqAntigo);
                }
            }
        }

        equipamentoIds.removeAll(jaProcessados);
        if (equipamentoIds.isEmpty()) {
            return;
        }
        jaProcessados.addAll(equipamentoIds);

        // Consulta 1: quantas OS abertas cada equipamento tem, ignorando as deste lote
        // (cujo novo valor ainda não está visível para a consulta neste ponto).
        Map<Id, Integer> abertasNoBanco =
            OrdemServicoSelector.contarAbertasPorEquipamento(equipamentoIds, ordensDoLote);

        // Soma as do lote atual que continuam abertas.
        if (!Trigger.isDelete) {
            for (Ordem_Servico__c os : ordens) {
                if (os.Equipamento__c != null && !STATUS_TERMINAIS.contains(os.Status__c)) {
                    Integer atual = abertasNoBanco.get(os.Equipamento__c);
                    abertasNoBanco.put(os.Equipamento__c, (atual == null ? 0 : atual) + 1);
                }
            }
        }

        // Consulta 2: estado atual dos equipamentos.
        Map<Id, Equipamento__c> equipamentos =
            OrdemServicoSelector.equipamentosPorIds(equipamentoIds);

        List<Equipamento__c> aAtualizar = new List<Equipamento__c>();
        for (Id eqId : equipamentoIds) {
            Equipamento__c eq = equipamentos.get(eqId);
            if (eq == null || eq.Status__c == 'Descartado') {
                continue;   // equipamento descartado não volta a operar sozinho
            }

            Integer abertas = abertasNoBanco.get(eqId) == null ? 0 : abertasNoBanco.get(eqId);
            String  novoStatus = abertas > 0 ? 'Em manutencao' : 'Operacional';

            Boolean mudouStatus = eq.Status__c != novoStatus;
            Boolean fechouTudo  = abertas == 0 && eq.Status__c == 'Em manutencao';

            if (!mudouStatus && !fechouTudo) {
                continue;   // nada a fazer: não gere DML inútil
            }

            Equipamento__c alterado = new Equipamento__c(Id = eqId, Status__c = novoStatus);
            if (fechouTudo) {
                alterado.Ultima_Manutencao__c = System.today();
            }
            aAtualizar.add(alterado);
        }

        if (aAtualizar.isEmpty()) {
            return;
        }

        // SYSTEM_MODE deliberado: o técnico pode concluir uma OS sem ter permissão de
        // edição no equipamento. A regra de negócio precisa valer mesmo assim.
        List<Database.SaveResult> srs =
            Database.update(aAtualizar, false, AccessLevel.SYSTEM_MODE);

        for (Integer i = 0; i < srs.size(); i++) {
            if (!srs[i].isSuccess()) {
                System.debug(LoggingLevel.ERROR,
                    'Falha ao sincronizar equipamento ' + aAtualizar[i].Id + ': ' +
                    srs[i].getErrors()[0].getMessage());
            }
        }
    }
}
