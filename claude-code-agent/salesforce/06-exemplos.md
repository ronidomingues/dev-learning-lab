# 06 · Exemplos

`Nível: intermediário` · `Atualizado: 11/08/2026` · `API 67.0`

14 exemplos completos e executáveis. Cada um traz **problema → solução → explicação**.
Todo código está inteiro — nada de `...` escondendo o que importa.
Os dois últimos são casos de produção reais, com as decisões que só aparecem em produção.

Assume ambiente de [03-instalacao.md](03-instalacao.md) e o ciclo de
[04-como-comecar.md](04-como-comecar.md).

| # | Exemplo | Nível |
|---|---|---|
| 1 | Objeto customizado completo em XML | trivial |
| 2 | Regra de validação | trivial |
| 3 | Campo fórmula e rollup | trivial |
| 4 | Trigger com handler (o padrão canônico) | básico |
| 5 | Bulkification: o certo e o errado, medidos | básico |
| 6 | Serviço com tratamento de erro e resultado parcial | intermediário |
| 7 | Queueable com encadeamento | intermediário |
| 8 | Batch Apex sobre milhões de registros | intermediário |
| 9 | Callout REST com Named Credential | intermediário |
| 10 | Expor uma API REST própria | intermediário |
| 11 | LWC com formulário, validação e toast | intermediário |
| 12 | LWC + Platform Event em tempo real | avançado |
| 13 | **Produção:** integração idempotente com retentativa e circuit breaker | avançado |
| 14 | **Produção:** processamento noturno de 8 milhões de registros | avançado |

---

## Exemplo 1 — Objeto customizado completo, em arquivo

**Problema.** Você quer versionar a definição de um objeto no Git, não criá-lo clicando.

**Solução.** Crie a estrutura de arquivos abaixo em `force-app/main/default/objects/`.

`objects/Equipamento__c/Equipamento__c.object-meta.xml`
```xml
<?xml version="1.0" encoding="UTF-8"?>
<CustomObject xmlns="http://soap.sforce.com/2006/04/metadata">
    <label>Equipamento</label>
    <pluralLabel>Equipamentos</pluralLabel>
    <nameField>
        <label>Código do Equipamento</label>
        <type>AutoNumber</type>
        <displayFormat>EQP-{0000}</displayFormat>
    </nameField>
    <deploymentStatus>Deployed</deploymentStatus>
    <sharingModel>ReadWrite</sharingModel>
    <enableActivities>true</enableActivities>
    <enableHistory>true</enableHistory>
    <enableReports>true</enableReports>
    <enableSearch>true</enableSearch>
</CustomObject>
```

`objects/Equipamento__c/fields/Numero_Serie__c.field-meta.xml`
```xml
<?xml version="1.0" encoding="UTF-8"?>
<CustomField xmlns="http://soap.sforce.com/2006/04/metadata">
    <fullName>Numero_Serie__c</fullName>
    <label>Número de Série</label>
    <type>Text</type>
    <length>50</length>
    <required>true</required>
    <unique>true</unique>
    <externalId>true</externalId>
    <caseSensitive>false</caseSensitive>
</CustomField>
```

`objects/Equipamento__c/fields/Status__c.field-meta.xml`
```xml
<?xml version="1.0" encoding="UTF-8"?>
<CustomField xmlns="http://soap.sforce.com/2006/04/metadata">
    <fullName>Status__c</fullName>
    <label>Status</label>
    <type>Picklist</type>
    <valueSet>
        <restricted>true</restricted>
        <valueSetDefinition>
            <sorted>false</sorted>
            <value><fullName>Operacional</fullName><default>true</default>
                   <label>Operacional</label></value>
            <value><fullName>Em manutenção</fullName><default>false</default>
                   <label>Em manutenção</label></value>
            <value><fullName>Fora de operação</fullName><default>false</default>
                   <label>Fora de operação</label></value>
        </valueSetDefinition>
    </valueSet>
</CustomField>
```

`objects/Equipamento__c/fields/Conta__c.field-meta.xml`
```xml
<?xml version="1.0" encoding="UTF-8"?>
<CustomField xmlns="http://soap.sforce.com/2006/04/metadata">
    <fullName>Conta__c</fullName>
    <label>Cliente</label>
    <type>Lookup</type>
    <referenceTo>Account</referenceTo>
    <relationshipName>Equipamentos</relationshipName>
    <relationshipLabel>Equipamentos</relationshipLabel>
    <deleteConstraint>SetNull</deleteConstraint>
    <required>false</required>
</CustomField>
```

```bash
sf project deploy start -d force-app/main/default/objects
```

**Explicação.**

- `externalId: true` no número de série é o que permite `upsert` por ele, sem conhecer o
  Id do Salesforce. É a chave de toda integração sã com sistema externo.
- `restricted: true` na picklist impede que a API grave um valor fora da lista. Sem isso,
  qualquer integração pode inserir lixo — e isso acontece sempre.
- `deleteConstraint: SetNull` diz o que fazer com o equipamento se a conta for apagada.
  As opções são `SetNull`, `Restrict` (impede a exclusão) e `Cascade` (só em master-detail).
- `sharingModel: ReadWrite` é o **OWD** do objeto — ver
  [13-seguranca-e-compartilhamento.md](13-seguranca-e-compartilhamento.md).
- `AutoNumber` no `nameField` gera `EQP-0001`, `EQP-0002`. **Cuidado:** a sequência não é
  reutilizada nem reiniciável, e não há garantia de ausência de buracos.

---

## Exemplo 2 — Regra de validação

**Problema.** Ninguém pode marcar um equipamento como "Operacional" se ele não tem data
de última manutenção nos últimos 365 dias.

**Solução.** `objects/Equipamento__c/validationRules/Manutencao_Vencida.validationRule-meta.xml`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<ValidationRule xmlns="http://soap.sforce.com/2006/04/metadata">
    <fullName>Manutencao_Vencida</fullName>
    <active>true</active>
    <description>Impede status Operacional com manutenção vencida há mais de 365 dias.</description>
    <errorConditionFormula>
AND(
  ISPICKVAL(Status__c, "Operacional"),
  OR(
    ISBLANK(Ultima_Manutencao__c),
    Ultima_Manutencao__c &lt; TODAY() - 365
  ),
  NOT($Permission.Ignorar_Validacao_Manutencao)
)
    </errorConditionFormula>
    <errorDisplayField>Status__c</errorDisplayField>
    <errorMessage>Equipamento sem manutenção há mais de 365 dias não pode ficar Operacional.</errorMessage>
</ValidationRule>
```

**Explicação.**

- A fórmula é a condição de **erro**: se ela der `true`, o registro é rejeitado. Isso é
  invertido em relação à intuição e derruba todo mundo na primeira vez.
- `&lt;` é `<` escapado — é XML.
- `NOT($Permission.Ignorar_Validacao_Manutencao)` cria uma **válvula de escape**: um
  *custom permission* que, atribuído por permission set, deixa um perfil específico passar.
  **Isso é essencial em produção** — sem ele, a migração de dados legados fica impossível e
  alguém vai simplesmente desativar a regra e esquecer de religar.
- Validation rules rodam **antes** dos triggers `after` e **depois** dos `before` — a ordem
  completa está em [14-automacao-declarativa.md](14-automacao-declarativa.md) §3.

---

## Exemplo 3 — Fórmula e rollup

**Problema.** (a) Mostrar quantos dias faltam para a próxima manutenção.
(b) Na conta, mostrar quantos equipamentos estão fora de operação.

**Solução (a) — campo fórmula em `Equipamento__c`:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<CustomField xmlns="http://soap.sforce.com/2006/04/metadata">
    <fullName>Dias_Ate_Manutencao__c</fullName>
    <label>Dias até a manutenção</label>
    <type>Number</type>
    <precision>18</precision>
    <scale>0</scale>
    <formula>IF(
  ISBLANK(Ultima_Manutencao__c),
  -999,
  (Ultima_Manutencao__c + 365) - TODAY()
)</formula>
    <formulaTreatBlanksAs>BlankAsZero</formulaTreatBlanksAs>
</CustomField>
```

**Solução (b) — rollup summary.** Requer que `Equipamento__c` seja filho **master-detail**
de `Account`. Com lookup (Exemplo 1) **não é possível** usar rollup nativo.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<CustomField xmlns="http://soap.sforce.com/2006/04/metadata">
    <fullName>Equipamentos_Parados__c</fullName>
    <label>Equipamentos parados</label>
    <type>Summary</type>
    <summaryForeignKey>Equipamento__c.Conta__c</summaryForeignKey>
    <summaryOperation>count</summaryOperation>
    <summaryFilterItems>
        <field>Equipamento__c.Status__c</field>
        <operation>equals</operation>
        <value>Fora de operação</value>
    </summaryFilterItems>
</CustomField>
```

**Explicação — e a decisão de arquitetura escondida aqui.**

| | Lookup | Master-detail |
|---|---|---|
| Filho pode existir sem pai | Sim | Não |
| Apagar o pai | Filho fica órfão ou bloqueia | **Apaga os filhos em cascata** |
| Segurança do filho | Própria | **Herdada do pai** |
| Rollup summary | ❌ | ✅ |
| Reparentear | Livre | Só se marcado como reparentável |
| Limite por objeto | 40 lookups | 2 master-details |

**A pegadinha de produção:** master-detail causa **contenção de bloqueio**. Toda atualização
de filho bloqueia o pai por um instante. Se 500 equipamentos da mesma conta forem atualizados
em paralelo, você terá `UNABLE_TO_LOCK_ROW`. Isso é o famoso *account data skew* —
ver [12-modelo-de-dados.md](12-modelo-de-dados.md) §7.

**Fórmulas têm limite invisível:** 3.900 caracteres de fórmula compilada e 5.000 bytes.
Fórmulas grandes que referenciam outras fórmulas estouram e o erro só aparece no deploy.

---

## Exemplo 4 — Trigger com handler (o padrão canônico)

**Problema.** Quando um equipamento vai para "Fora de operação", registrar a data e abrir
um Case para o cliente.

**Solução.**

`triggers/EquipamentoTrigger.trigger`
```apex
trigger EquipamentoTrigger on Equipamento__c (
    before insert, before update, before delete,
    after  insert, after  update, after  delete, after undelete
) {
    // O trigger não contém lógica. Um por objeto. Sempre.
    EquipamentoTriggerHandler.run();
}
```

`classes/EquipamentoTriggerHandler.cls`
```apex
public with sharing class EquipamentoTriggerHandler {

    // Interruptor para desligar a automação em migração de dados em massa.
    public static Boolean bypass = false;

    public static void run() {
        if (bypass) { return; }

        if (Trigger.isBefore && Trigger.isUpdate) {
            marcarDataDeParada((List<Equipamento__c>) Trigger.new,
                               (Map<Id, Equipamento__c>) Trigger.oldMap);
        }
        if (Trigger.isAfter && Trigger.isUpdate) {
            abrirCasosDeParada((List<Equipamento__c>) Trigger.new,
                               (Map<Id, Equipamento__c>) Trigger.oldMap);
        }
    }

    /**
     * BEFORE: alteramos o próprio registro. Sem DML — a plataforma grava por nós.
     */
    private static void marcarDataDeParada(List<Equipamento__c> novos,
                                           Map<Id, Equipamento__c> antigos) {
        for (Equipamento__c e : novos) {
            Equipamento__c antigo = antigos.get(e.Id);
            Boolean acabouDeParar = e.Status__c == 'Fora de operação'
                                 && antigo.Status__c != 'Fora de operação';
            if (acabouDeParar) {
                e.Data_Parada__c = System.now();
            }
            if (e.Status__c == 'Operacional' && antigo.Status__c == 'Fora de operação') {
                e.Data_Parada__c = null;
            }
        }
    }

    /**
     * AFTER: criamos OUTROS registros. Um único DML no final, fora do laço.
     */
    private static void abrirCasosDeParada(List<Equipamento__c> novos,
                                           Map<Id, Equipamento__c> antigos) {
        List<Case> casos = new List<Case>();

        for (Equipamento__c e : novos) {
            Equipamento__c antigo = antigos.get(e.Id);
            if (e.Status__c == 'Fora de operação'
                && antigo.Status__c != 'Fora de operação'
                && e.Conta__c != null) {

                casos.add(new Case(
                    AccountId   = e.Conta__c,
                    Subject     = 'Equipamento parado: ' + e.Name,
                    Description = 'Detectado automaticamente em ' + System.now().format(),
                    Origin      = 'Automático',
                    Priority    = 'High',
                    Status      = 'New'
                ));
            }
        }

        if (casos.isEmpty()) { return; }

        // allOrNone = false: um caso que falhe não derruba os outros.
        List<Database.SaveResult> resultados = Database.insert(casos, false);
        for (Integer i = 0; i < resultados.size(); i++) {
            if (!resultados[i].isSuccess()) {
                for (Database.Error err : resultados[i].getErrors()) {
                    System.debug(LoggingLevel.ERROR,
                        'Falha ao abrir caso: ' + err.getStatusCode() + ' — ' + err.getMessage());
                }
            }
        }
    }
}
```

**Explicação — cinco decisões, cinco motivos.**

1. **Um trigger por objeto.** Se houver dois, a ordem entre eles é **indeterminada** pela
   plataforma. Não é "má prática", é comportamento não especificado.
2. **Sem lógica no trigger.** Triggers não são classes: não têm construtor, não são
   instanciáveis, e não dá para testar unitariamente. O handler dá.
3. **`before` para o próprio registro, `after` para outros.** Escrever no próprio registro
   em `after` exige `update` explícito, o que dispara o trigger de novo → recursão.
4. **`bypass` estático.** Numa migração de 2 milhões de registros, você precisa desligar a
   automação. Sem esse interruptor, a alternativa é desativar o trigger em produção —
   o que exige deploy e deixa a org descoberta.
5. **`Database.insert(lista, false)`** em vez de `insert lista`. Falha parcial é preferível
   a falha total num processo automático.

**O que este exemplo NÃO faz de propósito, e você deve fazer em produção:** não há
tratamento de recursão. Se o Case criar algo que atualize o equipamento, o ciclo recomeça.
Padrão comum: `private static Set<Id> jaProcessados`.

---

## Exemplo 5 — Bulkification: o errado e o certo, medidos

**Problema.** Copiar o setor da conta para cada equipamento novo.

### ❌ Errado — morre com volume

```apex
public class ErradoBulk {
    public static void preencher(List<Equipamento__c> equipamentos) {
        for (Equipamento__c e : equipamentos) {
            // 1 SOQL POR REGISTRO → 101 registros já estoura o limite de 100
            Account a = [SELECT Industry FROM Account WHERE Id = :e.Conta__c];
            e.Setor__c = a.Industry;
            update e;   // 1 DML POR REGISTRO → 151 registros estoura o limite de 150
        }
    }
}
```

Erro real que aparece: `System.LimitException: Too many SOQL queries: 101`.

### ✅ Certo — 2 SOQL e 1 DML, para 1 ou 10.000 registros

```apex
public with sharing class CertoBulk {
    public static void preencher(List<Equipamento__c> equipamentos) {
        // 1. Colete as chaves. Set elimina duplicatas de graça.
        Set<Id> contaIds = new Set<Id>();
        for (Equipamento__c e : equipamentos) {
            if (e.Conta__c != null) { contaIds.add(e.Conta__c); }
        }
        if (contaIds.isEmpty()) { return; }

        // 2. UMA consulta para todas as chaves.
        Map<Id, Account> contas = new Map<Id, Account>([
            SELECT Id, Industry FROM Account WHERE Id IN :contaIds
        ]);

        // 3. Atribua em memória.
        for (Equipamento__c e : equipamentos) {
            Account a = contas.get(e.Conta__c);
            if (a != null) { e.Setor__c = a.Industry; }
        }
        // 4. Nenhum DML: se isto rodar num trigger `before`, a plataforma grava.
        //    Se for chamada avulsa, faça UM update fora do laço.
    }
}
```

**Medindo a diferença — cole no Execute Anonymous:**

```apex
List<Equipamento__c> amostra = [SELECT Id, Conta__c, Setor__c FROM Equipamento__c LIMIT 200];

Integer soql0 = Limits.getQueries();
Integer cpu0  = Limits.getCpuTime();

CertoBulk.preencher(amostra);

System.debug('SOQL usadas: ' + (Limits.getQueries() - soql0));   // esperado: 1
System.debug('CPU (ms):    ' + (Limits.getCpuTime() - cpu0));
System.debug('Restam SOQL: ' + (Limits.getLimitQueries() - Limits.getQueries()));
```

**Explicação.** Bulkification não é otimização — é **requisito de corretude**. Um trigger
processa lotes de até 200 registros por padrão, e a Bulk API pode mandar 10.000 de uma vez.
Código que assume um registro por vez **funciona no teste manual e quebra no primeiro
import**. É o erro nº 1 de Apex, sem concorrência.

**A regra em uma frase:** *nunca* SOQL, DML, `sendEmail` ou callout dentro de um laço.

---

## Exemplo 6 — Serviço com erro tratado e resultado parcial

**Problema.** Uma rotina que dá baixa em equipamentos. Se um falhar, os outros devem seguir,
e quem chamou precisa saber exatamente o que aconteceu.

```apex
public with sharing class BaixaEquipamentoService {

    /** Resultado tipado: melhor que Map<String,Object> ou exceção genérica. */
    public class Resultado {
        @AuraEnabled public Integer sucessos = 0;
        @AuraEnabled public List<Falha> falhas = new List<Falha>();
        @AuraEnabled public Boolean get_temFalha() { return !falhas.isEmpty(); }
    }
    public class Falha {
        @AuraEnabled public Id      registroId;
        @AuraEnabled public String  motivo;
        public Falha(Id i, String m) { registroId = i; motivo = m; }
    }

    /** Exceção específica do domínio — permite catch seletivo pelo chamador. */
    public class BaixaException extends Exception {}

    public static Resultado darBaixa(Set<Id> ids, String motivo) {
        Resultado r = new Resultado();

        if (ids == null || ids.isEmpty()) {
            throw new BaixaException('Nenhum equipamento informado.');
        }
        if (String.isBlank(motivo)) {
            throw new BaixaException('O motivo da baixa é obrigatório.');
        }

        // USER_MODE: respeita FLS e sharing do usuário. Padrão a partir da API 67.0,
        // mas explicitar deixa a intenção clara para quem lê.
        List<Equipamento__c> equipamentos = [
            SELECT Id, Name, Status__c
            FROM Equipamento__c
            WHERE Id IN :ids
            WITH USER_MODE
        ];

        Set<Id> encontrados = new Map<Id, Equipamento__c>(equipamentos).keySet();
        for (Id faltante : ids) {
            if (!encontrados.contains(faltante)) {
                r.falhas.add(new Falha(faltante, 'Não encontrado ou sem permissão de leitura.'));
            }
        }

        List<Equipamento__c> aAtualizar = new List<Equipamento__c>();
        for (Equipamento__c e : equipamentos) {
            if (e.Status__c == 'Fora de operação') {
                r.falhas.add(new Falha(e.Id, 'Já estava fora de operação.'));
                continue;
            }
            aAtualizar.add(new Equipamento__c(
                Id             = e.Id,
                Status__c      = 'Fora de operação',
                Motivo_Baixa__c = motivo,
                Data_Parada__c = System.now()
            ));
        }

        if (aAtualizar.isEmpty()) { return r; }

        // Savepoint: se algo catastrófico ocorrer depois, desfaz tudo.
        Savepoint sp = Database.setSavepoint();
        try {
            List<Database.SaveResult> srs =
                Database.update(aAtualizar, false, AccessLevel.USER_MODE);

            for (Integer i = 0; i < srs.size(); i++) {
                if (srs[i].isSuccess()) {
                    r.sucessos++;
                } else {
                    String msg = '';
                    for (Database.Error e : srs[i].getErrors()) {
                        msg += e.getStatusCode() + ': ' + e.getMessage() + ' ';
                    }
                    r.falhas.add(new Falha(aAtualizar[i].Id, msg.trim()));
                }
            }
        } catch (DmlException ex) {
            Database.rollback(sp);
            throw new BaixaException('Falha inesperada na baixa: ' + ex.getMessage(), ex);
        }
        return r;
    }
}
```

**Explicação.**

- **Exceção customizada** (`extends Exception`) permite ao chamador tratar seletivamente.
  Em Apex, o nome da classe **precisa** terminar em `Exception` — é regra do compilador.
- **`AccessLevel.USER_MODE` no DML** é o complemento do `WITH USER_MODE` da SOQL.
- **`Savepoint`** cria um ponto de rollback. Custa um dos ~5 savepoints por transação;
  não abuse.
- **Retornar um objeto tipado** em vez de lançar exceção para erro de negócio esperado é a
  diferença entre uma API usável e uma que obriga o chamador a fazer parse de string.
- **Falha parcial explícita.** O chamador sabe quantos passaram, quais falharam e por quê.

---

## Exemplo 7 — Queueable com encadeamento

**Problema.** Após a baixa, notificar um sistema externo. Callout não pode acontecer no
mesmo contexto do trigger.

```apex
public class NotificarBaixaQueueable implements Queueable, Database.AllowsCallouts {

    private final List<Id> pendentes;
    private final Integer  tamanhoLote = 50;

    public NotificarBaixaQueueable(List<Id> ids) {
        this.pendentes = ids;
    }

    public void execute(QueueableContext ctx) {
        List<Id> lote      = new List<Id>();
        List<Id> restantes = new List<Id>();

        for (Integer i = 0; i < pendentes.size(); i++) {
            if (i < tamanhoLote) { lote.add(pendentes[i]); }
            else                 { restantes.add(pendentes[i]); }
        }

        List<Equipamento__c> eqs = [
            SELECT Id, Name, Numero_Serie__c, Status__c
            FROM Equipamento__c WHERE Id IN :lote
        ];

        HttpRequest req = new HttpRequest();
        req.setEndpoint('callout:ERP_Manutencao/api/v1/baixas');  // Named Credential
        req.setMethod('POST');
        req.setHeader('Content-Type', 'application/json');
        req.setTimeout(30000);   // padrão é 10 s; 120 s é o teto
        req.setBody(JSON.serialize(new Map<String, Object>{
            'origem' => 'salesforce',
            'itens'  => eqs
        }));

        try {
            HttpResponse res = new Http().send(req);
            if (res.getStatusCode() >= 200 && res.getStatusCode() < 300) {
                System.debug('Notificados: ' + eqs.size());
            } else {
                System.debug(LoggingLevel.ERROR,
                    'ERP retornou ' + res.getStatusCode() + ': ' + res.getBody());
            }
        } catch (CalloutException ce) {
            System.debug(LoggingLevel.ERROR, 'Callout falhou: ' + ce.getMessage());
        }

        // Encadeia o próximo lote. Não encadeie dentro de teste — a plataforma proíbe.
        if (!restantes.isEmpty() && !Test.isRunningTest()) {
            System.enqueueJob(new NotificarBaixaQueueable(restantes));
        }
    }
}
```

Disparo a partir do handler:
```apex
if (!idsParaNotificar.isEmpty()) {
    System.enqueueJob(new NotificarBaixaQueueable(new List<Id>(idsParaNotificar)));
}
```

**Explicação.**

- **Por que não fazer o callout direto no trigger?** A plataforma proíbe callouts após
  qualquer DML na mesma transação — `You have uncommitted work pending`. O motivo real:
  um callout pode demorar; segurar um bloqueio de banco esperando um servidor de terceiros
  é receita para travar a instância inteira. É uma decisão de arquitetura multi-inquilino,
  não uma limitação arbitrária. Ver [19-multitenancy-arquitetura.md](19-multitenancy-arquitetura.md).
- **`Database.AllowsCallouts`** é obrigatório; sem essa interface, o callout falha.
- **Encadeamento** permite processar mais que os limites de uma transação. Limite: 1 job
  filho por job (5 na Developer Edition), profundidade ilimitada em produção.
- **`!Test.isRunningTest()`**: em teste, encadear lança
  `System.LimitException: Maximum stack depth has been reached`. Feio, mas necessário.

---

## Exemplo 8 — Batch Apex

**Problema.** Recalcular a criticidade de 8 milhões de equipamentos, toda madrugada.

```apex
public class RecalcularCriticidadeBatch implements
        Database.Batchable<SObject>, Database.Stateful, Schedulable {

    // Stateful: estas variáveis sobrevivem entre lotes.
    public Integer processados = 0;
    public Integer comErro     = 0;
    public List<String> amostraDeErros = new List<String>();

    /** start: define o universo. QueryLocator suporta até 50 milhões de registros. */
    public Database.QueryLocator start(Database.BatchableContext bc) {
        return Database.getQueryLocator([
            SELECT Id, Status__c, Ultima_Manutencao__c, Horas_Uso__c, Criticidade__c
            FROM Equipamento__c
            WHERE Status__c != 'Descartado'
        ]);
    }

    /** execute: roda uma vez por lote, com limites zerados a cada lote. */
    public void execute(Database.BatchableContext bc, List<Equipamento__c> escopo) {
        List<Equipamento__c> alterados = new List<Equipamento__c>();

        for (Equipamento__c e : escopo) {
            String nova = calcular(e);
            if (nova != e.Criticidade__c) {          // só grava o que mudou
                alterados.add(new Equipamento__c(Id = e.Id, Criticidade__c = nova));
            }
        }

        if (alterados.isEmpty()) { return; }

        for (Database.SaveResult sr : Database.update(alterados, false)) {
            if (sr.isSuccess()) {
                processados++;
            } else {
                comErro++;
                if (amostraDeErros.size() < 20) {     // guarda amostra, não tudo (heap!)
                    amostraDeErros.add(sr.getId() + ': ' + sr.getErrors()[0].getMessage());
                }
            }
        }
    }

    /** finish: roda uma vez, depois de todos os lotes. */
    public void finish(Database.BatchableContext bc) {
        AsyncApexJob job = [
            SELECT Id, Status, NumberOfErrors, JobItemsProcessed, TotalJobItems,
                   CreatedBy.Email
            FROM AsyncApexJob WHERE Id = :bc.getJobId()
        ];

        Messaging.SingleEmailMessage m = new Messaging.SingleEmailMessage();
        m.setToAddresses(new String[]{ job.CreatedBy.Email });
        m.setSubject('Recálculo de criticidade — ' + job.Status);
        m.setPlainTextBody(
            'Lotes: '      + job.JobItemsProcessed + '/' + job.TotalJobItems + '\n' +
            'Atualizados: '+ processados + '\n' +
            'Erros: '      + comErro     + '\n\n' +
            String.join(amostraDeErros, '\n')
        );
        Messaging.sendEmail(new Messaging.SingleEmailMessage[]{ m });
    }

    /** Schedulable na mesma classe: agenda e execução juntas. */
    public void execute(SchedulableContext sc) {
        Database.executeBatch(new RecalcularCriticidadeBatch(), 200);
    }

    private String calcular(Equipamento__c e) {
        Integer dias = e.Ultima_Manutencao__c == null
            ? 9999
            : e.Ultima_Manutencao__c.daysBetween(Date.today());
        Decimal horas = e.Horas_Uso__c == null ? 0 : e.Horas_Uso__c;

        if (dias > 365 || horas > 10000) { return 'Alta';  }
        if (dias > 180 || horas > 5000)  { return 'Média'; }
        return 'Baixa';
    }
}
```

Agendamento (Execute Anonymous, uma vez):
```apex
// Sintaxe cron: seg min hora dia mês dia-da-semana [ano]
System.schedule('Criticidade diária 02:00',
                '0 0 2 * * ?',
                new RecalcularCriticidadeBatch());
```

**Explicação.**

- **Tamanho do lote** (`200`) é o parâmetro mais importante. Cada lote tem limites próprios.
  Lote muito grande estoura CPU/heap; muito pequeno consome jobs à toa. Comece em 200,
  meça (`Setup → Apex Jobs`), e reduza se der `Apex CPU time limit exceeded`.
- **`Database.Stateful`** preserva estado entre lotes. **Custa serialização** — não guarde
  listas grandes ali, ou você estoura o heap.
- **Só gravar o que mudou** evita disparar triggers, workflows e sincronizações
  desnecessárias em milhões de registros. É a otimização de maior impacto neste código.
- **`finish` e-mail** — em produção, prefira gravar num objeto de log customizado. E-mail
  tem limite diário de 5.000 e ninguém lê.
- **Limite:** 5 batches ativos por org ao mesmo tempo, 100 na fila.

---

## Exemplo 9 — Callout REST com Named Credential

**Problema.** Consultar a garantia de um equipamento numa API externa, sem colocar
credencial no código.

### 9.1 Configurar (metadado, não código)

`externalCredentials/ERP_Manutencao_Cred.externalCredential-meta.xml`
```xml
<?xml version="1.0" encoding="UTF-8"?>
<ExternalCredential xmlns="http://soap.sforce.com/2006/04/metadata">
    <label>ERP Manutenção — Credencial</label>
    <authenticationProtocol>Custom</authenticationProtocol>
    <principals>
        <principalName>ERP_Service_Account</principalName>
        <principalType>NamedPrincipal</principalType>
        <sequenceNumber>1</sequenceNumber>
    </principals>
</ExternalCredential>
```

`namedCredentials/ERP_Manutencao.namedCredential-meta.xml`
```xml
<?xml version="1.0" encoding="UTF-8"?>
<NamedCredential xmlns="http://soap.sforce.com/2006/04/metadata">
    <label>ERP Manutenção</label>
    <namedCredentialType>SecuredEndpoint</namedCredentialType>
    <endpoint>https://erp.exemplo.com.br</endpoint>
    <generateAuthorizationHeader>true</generateAuthorizationHeader>
    <parameters>
        <parameterName>ExternalCredential</parameterName>
        <parameterType>Authentication</parameterType>
        <parameterValue>ERP_Manutencao_Cred</parameterValue>
    </parameters>
</NamedCredential>
```

> O segredo em si (token, senha) é preenchido **na interface**, em
> *Setup → Named Credentials → External Credentials → Principals → Authentication Parameters*.
> Ele **nunca** vai para o Git. É exatamente esse o ponto.

### 9.2 Código

```apex
public with sharing class GarantiaClient {

    public class GarantiaException extends Exception {}

    /** Resposta desserializada — classe interna evita Map<String,Object> por todo lado. */
    public class Garantia {
        public String  numeroSerie;
        public Boolean ativa;
        public Date    validaAte;
        public String  nivelCobertura;
    }

    public static Garantia consultar(String numeroSerie) {
        if (String.isBlank(numeroSerie)) {
            throw new GarantiaException('Número de série é obrigatório.');
        }

        HttpRequest req = new HttpRequest();
        // "callout:" resolve endpoint + autenticação a partir da Named Credential.
        req.setEndpoint('callout:ERP_Manutencao/api/v1/garantias/'
                        + EncodingUtil.urlEncode(numeroSerie, 'UTF-8'));
        req.setMethod('GET');
        req.setHeader('Accept', 'application/json');
        req.setTimeout(20000);

        HttpResponse res;
        try {
            res = new Http().send(req);
        } catch (CalloutException ce) {
            throw new GarantiaException('ERP indisponível: ' + ce.getMessage(), ce);
        }

        switch on res.getStatusCode() {
            when 200 {
                return (Garantia) JSON.deserialize(res.getBody(), Garantia.class);
            }
            when 404 {
                return null;                       // não encontrado não é erro
            }
            when 401, 403 {
                throw new GarantiaException('Credencial do ERP inválida ou expirada.');
            }
            when else {
                throw new GarantiaException(
                    'ERP retornou ' + res.getStatusCode() + ': ' + res.getBody());
            }
        }
    }
}
```

### 9.3 O teste (obrigatório: callouts reais são proibidos em teste)

```apex
@isTest
private class GarantiaClientTest {

    private class MockOk implements HttpCalloutMock {
        public HttpResponse respond(HttpRequest req) {
            Assert.isTrue(req.getEndpoint().contains('/garantias/SN-123'),
                          'Endpoint deveria conter o número de série');
            HttpResponse r = new HttpResponse();
            r.setStatusCode(200);
            r.setHeader('Content-Type', 'application/json');
            r.setBody('{"numeroSerie":"SN-123","ativa":true,' +
                      '"validaAte":"2027-12-31","nivelCobertura":"total"}');
            return r;
        }
    }

    private class MockStatus implements HttpCalloutMock {
        private Integer codigo;
        MockStatus(Integer c) { codigo = c; }
        public HttpResponse respond(HttpRequest req) {
            HttpResponse r = new HttpResponse();
            r.setStatusCode(codigo);
            r.setBody('{"erro":"..."}');
            return r;
        }
    }

    @isTest static void consulta_bemSucedida() {
        Test.setMock(HttpCalloutMock.class, new MockOk());
        Test.startTest();
        GarantiaClient.Garantia g = GarantiaClient.consultar('SN-123');
        Test.stopTest();

        Assert.isNotNull(g);
        Assert.isTrue(g.ativa);
        Assert.areEqual(Date.newInstance(2027, 12, 31), g.validaAte);
    }

    @isTest static void naoEncontrado_retornaNull() {
        Test.setMock(HttpCalloutMock.class, new MockStatus(404));
        Assert.isNull(GarantiaClient.consultar('SN-999'));
    }

    @isTest static void credencialInvalida_lancaExcecao() {
        Test.setMock(HttpCalloutMock.class, new MockStatus(401));
        try {
            GarantiaClient.consultar('SN-1');
            Assert.fail('Deveria ter lançado GarantiaException');
        } catch (GarantiaClient.GarantiaException e) {
            Assert.isTrue(e.getMessage().contains('inválida'));
        }
    }

    @isTest static void serieVazia_lancaExcecao() {
        try {
            GarantiaClient.consultar('   ');
            Assert.fail('Deveria ter lançado');
        } catch (GarantiaClient.GarantiaException e) {
            Assert.isTrue(e.getMessage().contains('obrigatório'));
        }
    }
}
```

**Explicação.** Named Credentials resolvem três problemas de uma vez: (1) segredo fora do
código e fora do Git; (2) a plataforma injeta o header de autorização, incluindo renovação
de token OAuth; (3) o domínio fica automaticamente liberado, sem precisar de
*Remote Site Setting*. **Não existe motivo legítimo, em 2026, para colocar URL e token em
Custom Setting.**

---

## Exemplo 10 — Expor uma API REST própria

**Problema.** O app móvel da equipe de campo precisa registrar manutenções.

```apex
@RestResource(urlMapping='/manutencao/*')
global with sharing class ManutencaoAPI {

    global class Requisicao {
        public String  numeroSerie;
        public String  tecnico;
        public String  observacoes;
        public Decimal horasGastas;
    }
    global class Resposta {
        public Boolean sucesso;
        public String  mensagem;
        public Id      manutencaoId;
    }

    @HttpPost
    global static Resposta registrar() {
        RestRequest  req = RestContext.request;
        RestResponse res = RestContext.response;
        Resposta out = new Resposta();

        try {
            Requisicao dados =
                (Requisicao) JSON.deserialize(req.requestBody.toString(), Requisicao.class);

            if (String.isBlank(dados.numeroSerie)) {
                res.statusCode = 400;
                out.sucesso = false;
                out.mensagem = 'numeroSerie é obrigatório.';
                return out;
            }

            List<Equipamento__c> eq = [
                SELECT Id FROM Equipamento__c
                WHERE Numero_Serie__c = :dados.numeroSerie
                WITH USER_MODE LIMIT 1
            ];
            if (eq.isEmpty()) {
                res.statusCode = 404;
                out.sucesso = false;
                out.mensagem = 'Equipamento não encontrado: ' + dados.numeroSerie;
                return out;
            }

            Manutencao__c m = new Manutencao__c(
                Equipamento__c = eq[0].Id,
                Tecnico__c     = dados.tecnico,
                Observacoes__c = dados.observacoes,
                Horas__c       = dados.horasGastas,
                Data__c        = System.today()
            );
            Database.insert(m, AccessLevel.USER_MODE);

            res.statusCode  = 201;
            out.sucesso     = true;
            out.mensagem    = 'Manutenção registrada.';
            out.manutencaoId = m.Id;

        } catch (JSONException je) {
            res.statusCode = 400;
            out.sucesso = false;
            out.mensagem = 'JSON inválido: ' + je.getMessage();
        } catch (Exception e) {
            res.statusCode = 500;
            out.sucesso = false;
            out.mensagem = 'Erro interno.';   // nunca vaze stack trace para o cliente
            System.debug(LoggingLevel.ERROR, e.getStackTraceString());
        }
        return out;
    }

    @HttpGet
    global static List<Manutencao__c> listar() {
        // /services/apexrest/manutencao/SN-123
        String serie = RestContext.request.requestURI.substringAfterLast('/');
        return [
            SELECT Id, Data__c, Tecnico__c, Horas__c, Observacoes__c
            FROM Manutencao__c
            WHERE Equipamento__r.Numero_Serie__c = :serie
            WITH USER_MODE
            ORDER BY Data__c DESC
            LIMIT 100
        ];
    }
}
```

Consumo:
```bash
# 1. Obter o token
sf org display -o devorg --json | python3 -c "import json,sys; d=json.load(sys.stdin)['result']; print(d['accessToken']); print(d['instanceUrl'])"

# 2. POST
curl -X POST "$INSTANCE/services/apexrest/manutencao/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"numeroSerie":"SN-123","tecnico":"Ana","observacoes":"Troca de filtro","horasGastas":2.5}'

# esperado: HTTP 201 e {"sucesso":true,"mensagem":"Manutenção registrada.","manutencaoId":"a01..."}
```

**Explicação.**

- `global` é obrigatório em `@RestResource` e nos métodos — é o modificador que expõe fora
  do namespace.
- **`with sharing`** faz a API respeitar o compartilhamento do usuário do token. Uma API
  `without sharing` vaza dados de toda a org para quem tiver qualquer token. Isso é um
  incidente de segurança esperando acontecer.
- **Nunca devolva `e.getMessage()` de exceção genérica ao cliente** — vaza nomes de campo,
  estrutura interna e às vezes dados.
- **Limitação real:** Apex REST consome do limite de chamadas de API da org e roda com
  os limites síncronos (10 s de CPU). Para volume alto, use Bulk API ou Platform Events.

---

## Exemplo 11 — LWC com formulário, validação e toast

**Problema.** Tela para o técnico registrar manutenção, com validação e feedback.

`lwc/registroManutencao/registroManutencao.html`
```html
<template>
    <lightning-card title="Registrar manutenção" icon-name="utility:wrench">
        <div class="slds-var-m-around_medium">

            <lightning-input
                label="Número de série"
                value={numeroSerie}
                onchange={handleSerie}
                required
                message-when-value-missing="Informe o número de série">
            </lightning-input>

            <lightning-input
                type="number"
                label="Horas gastas"
                value={horas}
                onchange={handleHoras}
                step="0.5" min="0.5" max="24"
                message-when-range-overflow="Máximo 24 horas"
                message-when-range-underflow="Mínimo 0,5 hora">
            </lightning-input>

            <lightning-textarea
                label="Observações"
                value={observacoes}
                onchange={handleObs}
                max-length="500">
            </lightning-textarea>

            <div class="slds-var-m-top_medium">
                <lightning-button
                    variant="brand"
                    label="Salvar"
                    onclick={handleSalvar}
                    disabled={salvando}>
                </lightning-button>
            </div>

            <template lwc:if={salvando}>
                <lightning-spinner alternative-text="Salvando"></lightning-spinner>
            </template>
        </div>
    </lightning-card>
</template>
```

`lwc/registroManutencao/registroManutencao.js`
```javascript
import { LightningElement, api } from 'lwc';
import { ShowToastEvent } from 'lightning/platformShowToastEvent';
import { CloseActionScreenEvent } from 'lightning/actions';
import registrar from '@salesforce/apex/ManutencaoService.registrar';

export default class RegistroManutencao extends LightningElement {
    @api recordId;          // preenchido automaticamente em página de registro

    numeroSerie = '';
    horas = 1;
    observacoes = '';
    salvando = false;

    handleSerie(e)  { this.numeroSerie = e.target.value; }
    handleHoras(e)  { this.horas       = e.target.value; }
    handleObs(e)    { this.observacoes = e.target.value; }

    /** Valida todos os lightning-input do template de uma vez. */
    validarCampos() {
        return [...this.template.querySelectorAll('lightning-input, lightning-textarea')]
            .reduce((valido, campo) => {
                campo.reportValidity();
                return valido && campo.checkValidity();
            }, true);
    }

    async handleSalvar() {
        if (!this.validarCampos()) {
            this.toast('Corrija os campos', 'Há campos inválidos no formulário.', 'warning');
            return;
        }

        this.salvando = true;
        try {
            const id = await registrar({
                numeroSerie: this.numeroSerie,
                horas: parseFloat(this.horas),
                observacoes: this.observacoes
            });
            this.toast('Pronto', `Manutenção ${id} registrada.`, 'success');
            this.limpar();
            this.dispatchEvent(new CloseActionScreenEvent());
        } catch (erro) {
            // Erro de Apex vem em erro.body.message; AuraHandledException dá mensagem limpa.
            const msg = erro?.body?.message ?? erro?.message ?? 'Erro desconhecido';
            this.toast('Falha ao salvar', msg, 'error', 'sticky');
        } finally {
            this.salvando = false;
        }
    }

    limpar() {
        this.numeroSerie = '';
        this.horas = 1;
        this.observacoes = '';
    }

    toast(title, message, variant, mode = 'dismissable') {
        this.dispatchEvent(new ShowToastEvent({ title, message, variant, mode }));
    }
}
```

`classes/ManutencaoService.cls` (o lado Apex)
```apex
public with sharing class ManutencaoService {

    @AuraEnabled
    public static Id registrar(String numeroSerie, Decimal horas, String observacoes) {
        try {
            List<Equipamento__c> eq = [
                SELECT Id FROM Equipamento__c
                WHERE Numero_Serie__c = :numeroSerie WITH USER_MODE LIMIT 1
            ];
            if (eq.isEmpty()) {
                // AuraHandledException: mensagem controlada chega limpa ao LWC.
                throw new AuraHandledException('Equipamento ' + numeroSerie + ' não encontrado.');
            }
            Manutencao__c m = new Manutencao__c(
                Equipamento__c = eq[0].Id,
                Horas__c       = horas,
                Observacoes__c = observacoes,
                Data__c        = System.today()
            );
            Database.insert(m, AccessLevel.USER_MODE);
            return m.Id;

        } catch (AuraHandledException ahe) {
            throw ahe;                                  // repassa sem embrulhar
        } catch (Exception e) {
            System.debug(LoggingLevel.ERROR, e.getStackTraceString());
            throw new AuraHandledException('Não foi possível registrar a manutenção.');
        }
    }
}
```

`lwc/registroManutencao/registroManutencao.js-meta.xml`
```xml
<?xml version="1.0" encoding="UTF-8"?>
<LightningComponentBundle xmlns="http://soap.sforce.com/2006/04/metadata">
    <apiVersion>67.0</apiVersion>
    <isExposed>true</isExposed>
    <targets>
        <target>lightning__RecordPage</target>
        <target>lightning__AppPage</target>
        <target>lightning__RecordAction</target>
    </targets>
    <targetConfigs>
        <targetConfig targets="lightning__RecordAction">
            <actionType>ScreenAction</actionType>
        </targetConfig>
    </targetConfigs>
</LightningComponentBundle>
```

**Explicação.**

- **`AuraHandledException` é o único jeito de mandar mensagem legível ao LWC.** Qualquer
  outra exceção chega como `"Script-thrown exception"` — inútil e um clássico de suporte.
- O `catch (AuraHandledException ahe) { throw ahe; }` existe porque, sem ele, o `catch`
  genérico embaixo captura a sua própria exceção e troca a mensagem.
- `reportValidity()` + `checkValidity()` é o padrão de validação nativo do SLDS; não
  reimplemente validação com regex e mensagens próprias.
- `disabled={salvando}` + `finally` previne o duplo clique — a causa de registros duplicados
  número um em formulários Lightning.

---

## Exemplo 12 — LWC + Platform Event em tempo real

**Problema.** Um painel na parede da oficina deve mostrar, ao vivo, cada equipamento que sai
de operação — sem recarregar e sem *polling*.

### 12.1 O evento (metadado)

`objects/Equipamento_Parado__e/Equipamento_Parado__e.object-meta.xml`
```xml
<?xml version="1.0" encoding="UTF-8"?>
<CustomObject xmlns="http://soap.sforce.com/2006/04/metadata">
    <label>Equipamento Parado</label>
    <pluralLabel>Equipamentos Parados</pluralLabel>
    <eventType>HighVolume</eventType>
    <publishBehavior>PublishAfterCommit</publishBehavior>
    <deploymentStatus>Deployed</deploymentStatus>
</CustomObject>
```
*(mais os campos `Equipamento_Nome__c`, `Conta_Nome__c`, `Momento__c` — mesmo formato do Exemplo 1)*

### 12.2 Publicar (no handler do trigger)

```apex
List<Equipamento_Parado__e> eventos = new List<Equipamento_Parado__e>();
for (Equipamento__c e : paradosAgora) {
    eventos.add(new Equipamento_Parado__e(
        Equipamento_Nome__c = e.Name,
        Conta_Nome__c       = nomesDeConta.get(e.Conta__c),
        Momento__c          = System.now()
    ));
}
for (Database.SaveResult sr : EventBus.publish(eventos)) {
    if (!sr.isSuccess()) {
        System.debug(LoggingLevel.ERROR, sr.getErrors()[0].getMessage());
    }
}
```

### 12.3 Consumir no LWC

`lwc/painelParadas/painelParadas.js`
```javascript
import { LightningElement } from 'lwc';
import { subscribe, unsubscribe, onError } from 'lightning/empApi';

const CANAL = '/event/Equipamento_Parado__e';
const MAX_LINHAS = 20;

export default class PainelParadas extends LightningElement {
    eventos = [];
    inscricao = null;

    connectedCallback() {
        onError((erro) => {
            // eslint-disable-next-line no-console
            console.error('Erro no barramento de eventos', JSON.stringify(erro));
        });

        // -1 = só eventos novos. -2 = todos os retidos (janela de 72 h).
        subscribe(CANAL, -1, (mensagem) => {
            const p = mensagem.data.payload;
            this.eventos = [
                {
                    id: mensagem.data.event.replayId,
                    equipamento: p.Equipamento_Nome__c,
                    conta: p.Conta_Nome__c,
                    momento: new Date(p.Momento__c).toLocaleString('pt-BR')
                },
                ...this.eventos
            ].slice(0, MAX_LINHAS);
        }).then((resposta) => {
            this.inscricao = resposta;
        });
    }

    disconnectedCallback() {
        // Sem isto, a inscrição vaza a cada navegação e você estoura o limite de clientes.
        if (this.inscricao) {
            unsubscribe(this.inscricao);
            this.inscricao = null;
        }
    }

    get vazio() {
        return this.eventos.length === 0;
    }
}
```

`lwc/painelParadas/painelParadas.html`
```html
<template>
    <lightning-card title="Paradas em tempo real" icon-name="utility:warning">
        <template lwc:if={vazio}>
            <p class="slds-var-m-around_medium slds-text-color_weak">
                Aguardando eventos…
            </p>
        </template>
        <ul class="slds-has-dividers_bottom-space">
            <template for:each={eventos} for:item="ev">
                <li key={ev.id} class="slds-item slds-var-p-around_small">
                    <strong>{ev.equipamento}</strong> — {ev.conta}
                    <span class="slds-text-body_small slds-text-color_weak">
                        &nbsp;{ev.momento}
                    </span>
                </li>
            </template>
        </ul>
    </lightning-card>
</template>
```

**Explicação.**

- **Platform Events** implementam pub/sub sobre o barramento da Salesforce, com entrega
  ao menos uma vez e **retenção de 72 horas** para *replay*.
- `PublishAfterCommit` só publica se a transação der commit — evita notificar sobre algo
  que foi desfeito por rollback. `PublishImmediately` publica mesmo em caso de rollback:
  útil para log de auditoria, perigoso para notificação de negócio.
- **`disconnectedCallback` com `unsubscribe` não é opcional.** Sem ele, cada navegação
  deixa uma inscrição órfã e você bate no limite de clientes CometD concorrentes
  (que varia por edição). O sintoma é o painel parar de receber eventos "sem motivo".
- **Limites:** eventos publicados por hora e clientes concorrentes são cotas por org.
  `Setup → Platform Events` mostra o consumo.

---

## Exemplo 13 — PRODUÇÃO: integração idempotente, com retentativa e circuit breaker

**Contexto real.** Toda oportunidade fechada precisa virar um pedido no ERP. O ERP cai
algumas vezes por mês, por 5 a 40 minutos. O negócio não tolera pedido duplicado nem
pedido perdido.

Esse é o problema mais comum de integração corporativa e onde a maioria das implementações
falha. As três exigências são: **idempotência**, **retentativa com backoff** e
**parada rápida quando o outro lado está fora**.

### 13.1 Objeto de fila (metadado — resumo dos campos)

`Integracao_Pedido__c`:

| Campo | Tipo | Papel |
|---|---|---|
| `Oportunidade__c` | Lookup(Opportunity) | origem |
| `Chave_Idempotencia__c` | Text(64), **Unique**, External Id | impede duplicata **no banco** |
| `Status__c` | Picklist: Pendente/Enviando/Sucesso/Falha/Descartado | máquina de estados |
| `Tentativas__c` | Number(2,0), default 0 | controle de backoff |
| `Proxima_Tentativa__c` | DateTime | quando reprocessar |
| `Ultimo_Erro__c` | LongTextArea(4000) | diagnóstico |
| `Id_Externo_ERP__c` | Text(64) | o que o ERP devolveu |

`Circuit_Breaker__c` (Custom Setting hierárquico, ou uma linha em objeto de config):
`Aberto_Ate__c` (DateTime), `Falhas_Consecutivas__c` (Number).

### 13.2 Enfileirar (trigger → fila, nunca callout direto)

```apex
public with sharing class PedidoIntegracaoEnqueuer {

    public static void enfileirar(List<Opportunity> ganhas) {
        List<Integracao_Pedido__c> fila = new List<Integracao_Pedido__c>();
        for (Opportunity o : ganhas) {
            fila.add(new Integracao_Pedido__c(
                Oportunidade__c        = o.Id,
                // Chave determinística: mesmo registro → mesma chave, sempre.
                Chave_Idempotencia__c  = gerarChave(o.Id),
                Status__c              = 'Pendente',
                Tentativas__c          = 0,
                Proxima_Tentativa__c   = System.now()
            ));
        }
        // upsert pela chave única: se já existe, não duplica. A garantia é do BANCO,
        // não do código — nenhuma condição de corrida a quebra.
        Database.upsert(fila, Integracao_Pedido__c.Chave_Idempotencia__c, false);
    }

    private static String gerarChave(Id oppId) {
        Blob h = Crypto.generateDigest('SHA-256', Blob.valueOf('OPP-' + oppId));
        return EncodingUtil.convertToHex(h).substring(0, 64);
    }
}
```

### 13.3 Processar

```apex
public with sharing class PedidoIntegracaoProcessor implements Schedulable {

    private static final Integer MAX_TENTATIVAS   = 5;
    private static final Integer LIMIAR_BREAKER   = 5;    // falhas seguidas para abrir
    private static final Integer MINUTOS_BREAKER  = 10;   // tempo de circuito aberto
    private static final Integer LOTE             = 50;

    public void execute(SchedulableContext sc) {
        processarPendentes();
    }

    public static void processarPendentes() {
        if (circuitoAberto()) {
            System.debug(LoggingLevel.WARN, 'Circuit breaker aberto; nada a fazer.');
            return;
        }

        List<Integracao_Pedido__c> pendentes = [
            SELECT Id, Oportunidade__c, Chave_Idempotencia__c, Tentativas__c
            FROM Integracao_Pedido__c
            WHERE Status__c IN ('Pendente', 'Falha')
              AND Tentativas__c < :MAX_TENTATIVAS
              AND Proxima_Tentativa__c <= :System.now()
            ORDER BY Proxima_Tentativa__c ASC
            LIMIT :LOTE
            FOR UPDATE                       // trava as linhas: dois jobs não pegam o mesmo
        ];
        if (pendentes.isEmpty()) { return; }

        System.enqueueJob(new EnviarLote(pendentes));
    }

    /** Queueable: contexto onde o callout é permitido. */
    public class EnviarLote implements Queueable, Database.AllowsCallouts {
        private final List<Integracao_Pedido__c> itens;
        public EnviarLote(List<Integracao_Pedido__c> i) { itens = i; }

        public void execute(QueueableContext ctx) {
            List<Integracao_Pedido__c> paraAtualizar = new List<Integracao_Pedido__c>();
            Integer falhasSeguidas = 0;

            for (Integracao_Pedido__c item : itens) {
                if (falhasSeguidas >= LIMIAR_BREAKER) {
                    abrirCircuito();
                    break;                     // para de queimar callouts contra um ERP morto
                }

                item.Tentativas__c = (item.Tentativas__c == null ? 0 : item.Tentativas__c) + 1;

                try {
                    HttpRequest req = new HttpRequest();
                    req.setEndpoint('callout:ERP_Manutencao/api/v1/pedidos');
                    req.setMethod('POST');
                    req.setHeader('Content-Type', 'application/json');
                    // Cabeçalho de idempotência: o ERP também deduplica do lado dele.
                    req.setHeader('Idempotency-Key', item.Chave_Idempotencia__c);
                    req.setTimeout(30000);
                    req.setBody(montarCorpo(item));

                    HttpResponse res = new Http().send(req);
                    Integer sc = res.getStatusCode();

                    if (sc == 200 || sc == 201 || sc == 409) {
                        // 409 Conflict = o ERP já tinha esse pedido. Para nós, é sucesso.
                        item.Status__c        = 'Sucesso';
                        item.Id_Externo_ERP__c = extrairId(res.getBody());
                        item.Ultimo_Erro__c   = null;
                        falhasSeguidas = 0;
                        fecharCircuito();

                    } else if (sc >= 400 && sc < 500) {
                        // Erro do cliente: retentar não vai adiantar. Desista e avise gente.
                        item.Status__c      = 'Descartado';
                        item.Ultimo_Erro__c = 'HTTP ' + sc + ': ' + res.getBody();
                        falhasSeguidas = 0;

                    } else {
                        // 5xx: o outro lado quebrou. Vale retentar.
                        throw new CalloutException('HTTP ' + sc + ': ' + res.getBody());
                    }

                } catch (Exception e) {
                    falhasSeguidas++;
                    item.Ultimo_Erro__c = e.getMessage().abbreviate(4000);
                    if (item.Tentativas__c >= MAX_TENTATIVAS) {
                        item.Status__c = 'Descartado';
                    } else {
                        item.Status__c = 'Falha';
                        // Backoff exponencial: 2, 4, 8, 16, 32 minutos.
                        Integer minutos = (Integer) Math.pow(2, item.Tentativas__c.intValue());
                        item.Proxima_Tentativa__c = System.now().addMinutes(minutos);
                    }
                }
                paraAtualizar.add(item);
            }

            if (!paraAtualizar.isEmpty()) {
                Database.update(paraAtualizar, false);
            }
        }

        private String montarCorpo(Integracao_Pedido__c item) {
            Opportunity o = [
                SELECT Id, Name, Amount, CloseDate, Account.Name, Account.Numero_ERP__c
                FROM Opportunity WHERE Id = :item.Oportunidade__c
            ];
            return JSON.serialize(new Map<String, Object>{
                'referencia'  => o.Id,
                'cliente'     => o.Account.Numero_ERP__c,
                'descricao'   => o.Name,
                'valor'       => o.Amount,
                'dataEntrega' => String.valueOf(o.CloseDate)
            });
        }

        private String extrairId(String corpo) {
            try {
                Map<String, Object> m = (Map<String, Object>) JSON.deserializeUntyped(corpo);
                return String.valueOf(m.get('id'));
            } catch (Exception e) { return null; }
        }
    }

    // ---- Circuit breaker ----
    private static Boolean circuitoAberto() {
        Circuit_Breaker__c cb = Circuit_Breaker__c.getOrgDefaults();
        return cb.Aberto_Ate__c != null && cb.Aberto_Ate__c > System.now();
    }
    private static void abrirCircuito() {
        Circuit_Breaker__c cb = Circuit_Breaker__c.getOrgDefaults();
        cb.Aberto_Ate__c = System.now().addMinutes(MINUTOS_BREAKER);
        upsert cb;
        System.debug(LoggingLevel.ERROR, 'Circuit breaker ABERTO até ' + cb.Aberto_Ate__c);
    }
    private static void fecharCircuito() {
        Circuit_Breaker__c cb = Circuit_Breaker__c.getOrgDefaults();
        if (cb.Aberto_Ate__c != null) { cb.Aberto_Ate__c = null; upsert cb; }
    }
}
```

Agendamento a cada 5 minutos (Salesforce agenda no mínimo de hora em hora pela interface;
o truque é agendar 12 jobs deslocados, ou usar `System.schedule` com expressões distintas):
```apex
for (Integer m = 0; m < 60; m += 5) {
    System.schedule('Integracao Pedidos ' + m, '0 ' + m + ' * * * ?',
                    new PedidoIntegracaoProcessor());
}
```

**Explicação — por que cada peça existe.**

| Peça | Sem ela, o que acontece na vida real |
|---|---|
| Fila em objeto | O trigger tenta o callout, o ERP está fora, o pedido some. Ninguém percebe até o cliente ligar. |
| `Chave_Idempotencia__c` **Unique** | Duas execuções concorrentes criam dois pedidos. O cliente recebe duas cobranças. |
| Tratar **409 como sucesso** | O ERP já tinha o pedido; você retenta para sempre e nunca marca sucesso. |
| Distinguir **4xx de 5xx** | Você retenta 5 vezes um payload inválido, gastando callouts e mascarando o bug. |
| Backoff exponencial | Você martela o ERP que está caindo, e o impede de se recuperar. |
| Circuit breaker | Com 5.000 itens na fila e o ERP fora, você queima o limite diário de callouts em minutos. |
| `FOR UPDATE` na query | Dois jobs agendados pegam o mesmo item e enviam duas vezes. |
| `Tentativas__c < MAX` | Item envenenado (*poison message*) reprocessa eternamente. |

> **Opinião profissional, ganha em campo:** se sua integração não tem chave de idempotência
> **garantida por constraint no banco**, ela vai duplicar. Não é questão de "se", é de
> quando — basta um timeout de rede em que a requisição chegou e a resposta não voltou.
> Idempotência garantida em código, com um `SELECT` antes do `INSERT`, não resolve: entre
> o select e o insert existe uma janela, e concorrência encontra janelas.

---

## Exemplo 14 — PRODUÇÃO: processar 8 milhões de registros à noite

**Contexto real.** Recalcular o *health score* de 8 milhões de contratos toda madrugada,
dentro de uma janela de 4 horas, sem derrubar a org nem estourar limites diários.

```apex
public class HealthScoreBatch implements
        Database.Batchable<SObject>, Database.Stateful, Database.RaisesPlatformEvents {

    private final Date   corte;
    private final Id     execucaoId;
    public  Integer      atualizados = 0;
    public  Integer      erros       = 0;
    private Datetime     inicio;

    public HealthScoreBatch(Date corte) {
        this.corte      = corte;
        this.execucaoId = null;
    }

    public Database.QueryLocator start(Database.BatchableContext bc) {
        inicio = System.now();
        // Filtro por campo INDEXADO. Sem índice, o QueryLocator sofre timeout
        // e o batch nem começa — erro clássico em tabelas de milhões de linhas.
        return Database.getQueryLocator([
            SELECT Id, Health_Score__c, Ultimo_Uso__c, Chamados_Abertos__c,
                   Valor_Contrato__c, Dias_Atraso__c
            FROM Contrato__c
            WHERE Ativo__c = true
              AND LastModifiedDate >= :corte
            ORDER BY Id                      // ordem estável para retomada
        ]);
    }

    public void execute(Database.BatchableContext bc, List<Contrato__c> escopo) {
        List<Contrato__c> alterados = new List<Contrato__c>();

        for (Contrato__c c : escopo) {
            Decimal novo = calcular(c);
            // Só grava se mudou mais que o ruído. Reduz DML, triggers e sincronização
            // downstream em ordens de grandeza.
            if (c.Health_Score__c == null || Math.abs(novo - c.Health_Score__c) >= 0.01) {
                alterados.add(new Contrato__c(Id = c.Id, Health_Score__c = novo));
            }
        }

        if (alterados.isEmpty()) { return; }

        // Desliga automação pesada durante o recálculo em massa.
        ContratoTriggerHandler.bypass = true;
        try {
            for (Database.SaveResult sr : Database.update(alterados, false)) {
                if (sr.isSuccess()) { atualizados++; }
                else {
                    erros++;
                    logar(sr.getId(), sr.getErrors()[0].getMessage());
                }
            }
        } finally {
            ContratoTriggerHandler.bypass = false;   // finally: sempre religa
        }
    }

    public void finish(Database.BatchableContext bc) {
        Long duracaoMin = (System.now().getTime() - inicio.getTime()) / 60000;

        insert new Job_Log__c(
            Nome__c        = 'HealthScoreBatch',
            Job_Id__c      = bc.getJobId(),
            Atualizados__c = atualizados,
            Erros__c       = erros,
            Duracao_Min__c = duracaoMin,
            Status__c      = erros == 0 ? 'OK' : 'Com erros'
        );

        // Só encadeia a etapa seguinte se esta foi bem.
        if (erros == 0) {
            Database.executeBatch(new NotificarContratosCriticosBatch(), 200);
        }
    }

    private Decimal calcular(Contrato__c c) {
        Decimal score = 100;
        Integer diasSemUso = c.Ultimo_Uso__c == null
            ? 999 : c.Ultimo_Uso__c.daysBetween(Date.today());
        score -= Math.min(diasSemUso * 0.5, 40);
        score -= Math.min((c.Chamados_Abertos__c == null ? 0 : c.Chamados_Abertos__c) * 3, 30);
        score -= Math.min((c.Dias_Atraso__c == null ? 0 : c.Dias_Atraso__c) * 1.5, 30);
        return Math.max(score, 0).setScale(2);
    }

    private void logar(Id registro, String msg) {
        System.debug(LoggingLevel.ERROR, 'HealthScore ' + registro + ': ' + msg);
    }
}
```

Disparo:
```apex
// Lote de 500: menos jobs consumidos, ainda longe do teto de CPU deste cálculo (leve).
Database.executeBatch(new HealthScoreBatch(Date.today().addDays(-30)), 500);
```

**As sete decisões que separam isso de um exemplo de tutorial:**

1. **Filtro por campo indexado no `start`.** `LastModifiedDate` é indexado. Um `WHERE`
   sobre campo de fórmula ou texto longo não usa índice e o `QueryLocator` sofre timeout
   antes do primeiro lote — o batch falha sem processar nada.
2. **`ORDER BY Id`.** Ordem estável permite retomar de onde parou, se você implementar
   checkpoint. Sem ordem, "reprocessar o que faltou" é impossível.
3. **Processamento incremental** (`LastModifiedDate >= corte`) em vez da tabela inteira.
   Recalcular 8 milhões todo dia quando 200 mil mudaram é desperdício de janela.
4. **Só gravar o que mudou de verdade** (limiar de 0,01). É a otimização de maior impacto:
   corta DML, triggers, regras de sharing e sincronização com Data Cloud.
5. **`bypass` da automação com `try/finally`.** Sem o `finally`, uma exceção deixa a
   automação desligada **para a org inteira** até o próximo deploy. Já vi isso derrubar
   uma operação por um dia inteiro.
6. **Tamanho de lote de 500**, não 200. Cálculo leve permite lotes maiores; menos lotes =
   menos jobs assíncronos consumidos da cota diária (250.000 por org). Se o cálculo fosse
   pesado, o certo seria reduzir para 50 ou 100 e medir o CPU por lote.
7. **`Job_Log__c` em vez de e-mail.** É consultável, gera relatório de tendência e não
   depende de alguém ler a caixa de entrada às 4h.

**O que ainda falta para isso ser realmente robusto** — e vale saber que falta:
retomada automática após falha parcial, alerta ativo (não só log), e um teste de carga em
sandbox *full* com volume comparável. Sandbox de desenvolvedor tem 200 MB de dados; testar
batch de milhões só numa Full Copy, que custa caro e demora dias para atualizar. Ver
[18-devops-e-alm.md](18-devops-e-alm.md) §3.

---

## Autoteste

1. Por que `externalId: true` num campo é decisivo para integração?
2. Qual é a diferença de comportamento entre lookup e master-detail ao apagar o pai? E qual gera contenção de bloqueio?
3. Escreva um trigger que respeite o padrão canônico. Por que a lógica não fica dentro dele?
4. Reescreva o Exemplo 5 (versão errada) e explique, com números, por que ele falha em 200 registros.
5. Por que não se pode fazer callout diretamente de um trigger? Qual é a razão arquitetural?
6. O que `AuraHandledException` resolve, e o que aparece no LWC se você não usá-la?
7. No Exemplo 13, por que HTTP 409 é tratado como sucesso?
8. Por que a idempotência precisa ser garantida por *constraint* de banco e não por `SELECT` antes de `INSERT`?
9. No Exemplo 14, o que aconteceria se o `bypass = false` não estivesse dentro de um `finally`?
10. Por que "só gravar o que mudou" é a otimização de maior impacto num batch de milhões?
