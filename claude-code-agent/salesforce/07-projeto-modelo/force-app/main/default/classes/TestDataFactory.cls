/**
 * Fábrica de dados de teste.
 *
 * Por que existe: testes Apex NÃO enxergam os dados da org (isolamento por padrão).
 * Cada teste precisa criar o que usa. Sem uma fábrica, essa criação é copiada em cada
 * classe de teste e, quando um campo obrigatório é adicionado, 40 testes quebram de uma vez.
 *
 * @isTest na classe: ela não conta para o limite de código da org nem para a cobertura.
 */
@isTest
public class TestDataFactory {

    /** Contas de teste, prontas para insert. */
    public static List<Account> contas(Integer quantidade) {
        List<Account> lista = new List<Account>();
        for (Integer i = 0; i < quantidade; i++) {
            lista.add(new Account(
                Name     = 'Cliente Teste ' + i,
                Industry = Math.mod(i, 2) == 0 ? 'Manufacturing' : 'Technology'
            ));
        }
        return lista;
    }

    /** Equipamentos ligados a uma conta (ou sem conta, se contaId for null). */
    public static List<Equipamento__c> equipamentos(Integer quantidade,
                                                    Id contaId,
                                                    String criticidade) {
        List<Equipamento__c> lista = new List<Equipamento__c>();
        for (Integer i = 0; i < quantidade; i++) {
            lista.add(new Equipamento__c(
                // Número de série único E no formato exigido pela validation rule
                // Serie_Formato_Valido (SN- + 6 dígitos). Timestamp + índice evita
                // colisão com a constraint UNIQUE dentro do mesmo método de teste.
                Numero_Serie__c = 'SN-' + String.valueOf(
                    Math.mod(System.currentTimeMillis() + i, 1000000)
                ).leftPad(6, '0'),
                Status__c       = 'Operacional',
                Criticidade__c  = criticidade == null ? 'Baixa' : criticidade,
                Conta__c        = contaId
            ));
        }
        return lista;
    }

    /** Ordens de serviço abertas para um equipamento. */
    public static List<Ordem_Servico__c> ordens(Integer quantidade,
                                                Id equipamentoId,
                                                String prioridade) {
        List<Ordem_Servico__c> lista = new List<Ordem_Servico__c>();
        for (Integer i = 0; i < quantidade; i++) {
            lista.add(new Ordem_Servico__c(
                Equipamento__c = equipamentoId,
                Status__c      = 'Aberta',
                Prioridade__c  = prioridade == null ? 'Normal' : prioridade,
                Descricao__c   = 'Falha simulada ' + i,
                Abertura__c    = System.now().addHours(-i)
            ));
        }
        return lista;
    }

    /**
     * Usuário de teste com o permission set do projeto.
     *
     * Usado com System.runAs para testar segurança de verdade — não confie em
     * "funciona no meu usuário", que é System Administrator e enxerga tudo.
     */
    public static User usuarioPadrao() {
        Profile p = [SELECT Id FROM Profile WHERE Name = 'Standard User' LIMIT 1];
        String sufixo = String.valueOf(System.currentTimeMillis());

        User u = new User(
            FirstName         = 'Tecnico',
            LastName          = 'Teste' + sufixo,
            Email             = 'tecnico' + sufixo + '@exemplo.invalid',
            // Username é global e único em TODA a Salesforce. Um domínio inventado
            // e um timestamp garantem que o teste não colida com nada.
            Username          = 'tecnico' + sufixo + '@curso.teste.invalid',
            Alias             = 'tec' + sufixo.right(4),
            ProfileId         = p.Id,
            TimeZoneSidKey    = 'America/Sao_Paulo',
            LocaleSidKey      = 'pt_BR',
            EmailEncodingKey  = 'UTF-8',
            LanguageLocaleKey = 'pt_BR'
        );
        insert u;

        atribuirPermissionSet(u.Id, 'Gestao_Manutencao');
        return u;
    }

    /** Atribui um permission set pelo nome de API. Silencioso se já estiver atribuído. */
    public static void atribuirPermissionSet(Id userId, String nomeApi) {
        List<PermissionSet> ps = [
            SELECT Id FROM PermissionSet WHERE Name = :nomeApi LIMIT 1
        ];
        if (ps.isEmpty()) {
            return;
        }
        List<PermissionSetAssignment> existente = [
            SELECT Id FROM PermissionSetAssignment
            WHERE AssigneeId = :userId AND PermissionSetId = :ps[0].Id
        ];
        if (existente.isEmpty()) {
            insert new PermissionSetAssignment(
                AssigneeId = userId, PermissionSetId = ps[0].Id);
        }
    }

    /** Cenário completo: 1 conta, 1 equipamento, N ordens abertas. */
    public static Cenario cenarioBasico(Integer qtdOrdens) {
        Cenario c = new Cenario();

        List<Account> cs = contas(1);
        insert cs;
        c.conta = cs[0];

        List<Equipamento__c> eqs = equipamentos(1, c.conta.Id, 'Media');
        insert eqs;
        c.equipamento = eqs[0];

        if (qtdOrdens > 0) {
            c.ordens = ordens(qtdOrdens, c.equipamento.Id, 'Normal');
            insert c.ordens;
        }
        return c;
    }

    public class Cenario {
        public Account                conta;
        public Equipamento__c         equipamento;
        public List<Ordem_Servico__c> ordens = new List<Ordem_Servico__c>();
    }
}
