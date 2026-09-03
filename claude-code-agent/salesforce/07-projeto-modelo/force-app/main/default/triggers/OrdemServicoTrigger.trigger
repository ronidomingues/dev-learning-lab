/**
 * UM trigger por objeto. Sem lógica aqui.
 *
 * Por quê: quando existem dois triggers no mesmo objeto, a ordem de execução entre eles
 * é INDEFINIDA pela plataforma — não é "má prática", é comportamento não especificado.
 * E triggers não são instanciáveis nem testáveis isoladamente; handlers são.
 */
trigger OrdemServicoTrigger on Ordem_Servico__c (
    before insert, before update, before delete,
    after  insert, after  update, after  delete, after undelete
) {
    OrdemServicoTriggerHandler.run();
}
