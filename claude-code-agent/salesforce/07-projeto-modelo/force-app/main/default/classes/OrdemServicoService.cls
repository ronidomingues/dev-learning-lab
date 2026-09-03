/**
 * Regra de negócio de ordens de serviço.
 *
 * Este é o único lugar que decide O QUE pode acontecer com uma OS.
 * Pode ser chamado por: LWC (@AuraEnabled), trigger handler, API REST, Flow (@InvocableMethod),
 * Batch. Se a regra estivesse no trigger, só existiria via DML.
 *
 * Todos os métodos públicos são BULK: recebem coleções, não registros isolados.
 */
public with sharing class OrdemServicoService {

    /** Exceção de domínio. Em Apex, o nome DEVE terminar em "Exception". */
    public class OrdemServicoException extends Exception {}

    private static final Set<String> STATUS_TERMINAIS =
        new Set<String>{ 'Concluida', 'Cancelada' };

    // ---------------------------------------------------------------- ABRIR

    /**
     * Abre ordens de serviço em lote.
     *
     * @param pedidos lista de pedidos de abertura
     * @return as ordens criadas, com Id preenchido
     * @throws OrdemServicoException se algum pedido for inválido
     */
    public static List<Ordem_Servico__c> abrir(List<PedidoAbertura> pedidos) {
        if (pedidos == null || pedidos.isEmpty()) {
            throw new OrdemServicoException('Nenhum pedido de abertura informado.');
        }

        Set<Id> equipamentoIds = new Set<Id>();
        for (PedidoAbertura p : pedidos) {
            if (p.equipamentoId == null) {
                throw new OrdemServicoException('Equipamento é obrigatório na abertura.');
            }
            equipamentoIds.add(p.equipamentoId);
        }

        // Uma consulta para todos os equipamentos — nunca uma por iteração.
        Map<Id, Equipamento__c> equipamentos =
            OrdemServicoSelector.equipamentosPorIds(equipamentoIds);

        List<Ordem_Servico__c> novas = new List<Ordem_Servico__c>();
        for (PedidoAbertura p : pedidos) {
            Equipamento__c eq = equipamentos.get(p.equipamentoId);
            if (eq == null) {
                throw new OrdemServicoException(
                    'Equipamento não encontrado ou sem acesso: ' + p.equipamentoId);
            }
            if (eq.Status__c == 'Descartado') {
                throw new OrdemServicoException(
                    'Equipamento ' + eq.Name + ' está descartado; não aceita nova OS.');
            }

            novas.add(new Ordem_Servico__c(
                Equipamento__c = p.equipamentoId,
                Status__c      = 'Aberta',
                Prioridade__c  = String.isBlank(p.prioridade)
                                    ? prioridadePorCriticidade(eq.Criticidade__c)
                                    : p.prioridade,
                Descricao__c   = p.descricao,
                Tecnico__c     = p.tecnicoId,
                Abertura__c    = System.now()
            ));
        }

        Database.insert(novas, true, AccessLevel.USER_MODE);
        return novas;
    }

    // -------------------------------------------------------------- CONCLUIR

    /**
     * Conclui ordens de serviço em lote, com falha parcial.
     *
     * @param horasPorOrdem  Id da OS → horas gastas
     * @return resultado detalhado por ordem
     */
    public static Resultado concluir(Map<Id, Decimal> horasPorOrdem) {
        Resultado r = new Resultado();

        if (horasPorOrdem == null || horasPorOrdem.isEmpty()) {
            throw new OrdemServicoException('Nenhuma ordem de serviço informada.');
        }

        List<Ordem_Servico__c> ordens =
            OrdemServicoSelector.porIds(horasPorOrdem.keySet());

        Set<Id> encontradas = new Map<Id, Ordem_Servico__c>(ordens).keySet();
        for (Id id : horasPorOrdem.keySet()) {
            if (!encontradas.contains(id)) {
                r.falhas.add(new Falha(id, 'Não encontrada ou sem permissão de leitura.'));
            }
        }

        List<Ordem_Servico__c> aAtualizar = new List<Ordem_Servico__c>();
        for (Ordem_Servico__c os : ordens) {
            Decimal horas = horasPorOrdem.get(os.Id);

            if (STATUS_TERMINAIS.contains(os.Status__c)) {
                r.falhas.add(new Falha(os.Id, 'Já está ' + os.Status__c + '.'));
                continue;
            }
            if (horas == null || horas <= 0) {
                r.falhas.add(new Falha(os.Id, 'Horas gastas devem ser maiores que zero.'));
                continue;
            }
            if (horas > 24) {
                r.falhas.add(new Falha(os.Id, 'Horas gastas acima do limite de 24 por OS.'));
                continue;
            }

            aAtualizar.add(new Ordem_Servico__c(
                Id             = os.Id,
                Status__c      = 'Concluida',
                Conclusao__c   = System.now(),
                Horas_Gastas__c = horas
            ));
        }

        if (aAtualizar.isEmpty()) {
            return r;
        }

        // allOrNone = false: uma OS que a validation rule rejeite não derruba as outras.
        List<Database.SaveResult> srs =
            Database.update(aAtualizar, false, AccessLevel.USER_MODE);

        for (Integer i = 0; i < srs.size(); i++) {
            if (srs[i].isSuccess()) {
                r.concluidas++;
            } else {
                String msg = '';
                for (Database.Error e : srs[i].getErrors()) {
                    msg += e.getMessage() + ' ';
                }
                r.falhas.add(new Falha(aAtualizar[i].Id, msg.trim()));
            }
        }
        return r;
    }

    /** Conveniência para uma única ordem — delega ao método bulk. */
    public static Resultado concluirUma(Id ordemId, Decimal horas) {
        return concluir(new Map<Id, Decimal>{ ordemId => horas });
    }

    // ------------------------------------------------------- PONTE PARA O LWC

    /** Ordens de um equipamento, para o painel. cacheable: sem DML, cache no cliente. */
    @AuraEnabled(cacheable=true)
    public static List<Ordem_Servico__c> listarPorEquipamento(Id equipamentoId,
                                                              Boolean apenasAbertas) {
        try {
            return OrdemServicoSelector.porEquipamento(equipamentoId, apenasAbertas);
        } catch (Exception e) {
            System.debug(LoggingLevel.ERROR, e.getStackTraceString());
            throw new AuraHandledException('Não foi possível carregar as ordens de serviço.');
        }
    }

    /** Concluir a partir do painel. Sem cacheable: faz DML. */
    @AuraEnabled
    public static String concluirDoPainel(Id ordemId, Decimal horas) {
        try {
            Resultado r = concluirUma(ordemId, horas);
            if (r.concluidas == 1) {
                return 'Ordem de serviço concluída.';
            }
            // AuraHandledException: a mensagem chega legível ao LWC.
            // Sem ela, o front recebe "Script-thrown exception".
            throw new AuraHandledException(
                r.falhas.isEmpty() ? 'Falha desconhecida.' : r.falhas[0].motivo);

        } catch (AuraHandledException ahe) {
            throw ahe;                       // repassa sem embrulhar
        } catch (OrdemServicoException ose) {
            throw new AuraHandledException(ose.getMessage());
        } catch (Exception e) {
            System.debug(LoggingLevel.ERROR, e.getStackTraceString());
            throw new AuraHandledException('Erro inesperado ao concluir a ordem.');
        }
    }

    // ---------------------------------------------------------------- APOIO

    /** Prioridade padrão derivada da criticidade do equipamento. */
    @TestVisible
    private static String prioridadePorCriticidade(String criticidade) {
        if (criticidade == 'Alta')  { return 'Critica'; }
        if (criticidade == 'Media') { return 'Alta';    }
        return 'Normal';
    }

    // ------------------------------------------------------- TIPOS DE APOIO

    /** Pedido de abertura. Classe em vez de 5 parâmetros soltos: legível e extensível. */
    public class PedidoAbertura {
        public Id     equipamentoId;
        public String prioridade;
        public String descricao;
        public Id     tecnicoId;

        public PedidoAbertura(Id equipamentoId, String descricao) {
            this.equipamentoId = equipamentoId;
            this.descricao     = descricao;
        }
        public PedidoAbertura comPrioridade(String p) { this.prioridade = p;  return this; }
        public PedidoAbertura comTecnico(Id t)        { this.tecnicoId  = t;  return this; }
    }

    /** Resultado tipado: o chamador não precisa fazer parse de string. */
    public class Resultado {
        @AuraEnabled public Integer     concluidas = 0;
        @AuraEnabled public List<Falha> falhas     = new List<Falha>();
        public Boolean temFalha() { return !falhas.isEmpty(); }
    }

    public class Falha {
        @AuraEnabled public Id     ordemId;
        @AuraEnabled public String motivo;
        public Falha(Id ordemId, String motivo) {
            this.ordemId = ordemId;
            this.motivo  = motivo;
        }
    }
}
