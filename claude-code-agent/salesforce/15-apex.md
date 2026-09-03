# 15 · Apex

`Nível: intermediário → avançado` · `Atualizado: 11/08/2026` · `API 67.0`

Apex é uma linguagem orientada a objetos, fortemente tipada, com sintaxe de Java, que roda
**exclusivamente** nos servidores da Salesforce, dentro de um contexto multi-inquilino
medido e limitado. Entender esse contexto é mais importante que a sintaxe.

---

## 1. O que Apex é e o que ele não é

| Apex **é** | Apex **não é** |
|---|---|
| Compilada para bytecode e executada pelo runtime da Salesforce | executada na sua máquina |
| Fortemente tipada, com SOQL/SOSL embutidos e validados em compilação | dinâmica ou interpretada |
| Transacional por natureza — commit ou rollback | um ambiente com controle fino de transação |
| Multithreaded do ponto de vista da plataforma | capaz de criar threads |
| Com acesso a rede **mediado** (callouts) | capaz de abrir sockets, ler arquivos, usar o SO |
| Versionada por API — código antigo mantém comportamento antigo | uma linguagem que evolui rápido |

**O que não existe em Apex** e frequentemente se procura: threads, reflexão completa
(há `Type.forName`, limitada), lambdas de verdade (há apenas construções restritas),
generics definíveis pelo usuário, `var` com inferência plena, operadores sobrecarregáveis,
anotações customizadas, e um ecossistema de bibliotecas externas — não existe `npm`/`maven`
para Apex; dependência se resolve copiando código ou instalando um pacote gerenciado.

---

## 2. Sintaxe essencial

```apex
public with sharing class Exemplo {

    // Constante: static final em MAIÚSCULAS por convenção
    private static final Integer LIMITE_PADRAO = 50;

    // Enum
    public enum Situacao { NOVO, ATIVO, ENCERRADO }

    // Propriedades com getter/setter
    public String nome { get; set; }
    public Integer contador { get; private set; }

    // Construtor
    public Exemplo(String nome) {
        this.nome = nome;
        this.contador = 0;
    }

    // Coleções — os três tipos que você usa 95% do tempo
    public void colecoes() {
        List<String> lista = new List<String>{ 'a', 'b', 'c' };   // ordenada, permite duplicata
        Set<Id>      ids   = new Set<Id>();                        // sem duplicata, sem ordem
        Map<Id, Account> mapa = new Map<Id, Account>();            // chave → valor

        // Idioma que você vai usar sempre: List<SObject> → Map<Id, SObject>
        Map<Id, Account> porId = new Map<Id, Account>([SELECT Id, Name FROM Account LIMIT 10]);
        Set<Id> chaves = porId.keySet();

        // Iteração
        for (String s : lista) { System.debug(s); }
        for (Integer i = 0; i < lista.size(); i++) { System.debug(lista[i]); }

        // SOQL for-loop: processa em lotes de 200 e NÃO carrega tudo em heap.
        // É como se processa 50.000 registros sem estourar memória.
        for (Account a : [SELECT Id, Name FROM Account]) {
            System.debug(a.Name);
        }
    }

    // switch on — a única construção "moderna" que a linguagem ganhou
    public String descrever(Situacao s) {
        switch on s {
            when NOVO     { return 'recém-criado'; }
            when ATIVO    { return 'em operação';  }
            when else     { return 'encerrado';    }
        }
    }

    // Exceções
    public class ExemploException extends Exception {}   // o nome DEVE terminar em Exception

    public void tratar() {
        try {
            throw new ExemploException('algo deu errado');
        } catch (ExemploException e) {
            System.debug(e.getMessage() + ' em ' + e.getStackTraceString());
        } catch (Exception e) {
            System.debug('genérico');
        } finally {
            System.debug('sempre executa');
        }
    }
}
```

**Tipos numéricos — a regra que evita bug de dinheiro:**

| Tipo | Guarda | Use para |
|---|---|---|
| `Integer` | 32 bits | contadores, índices |
| `Long` | 64 bits | timestamps em milissegundos |
| `Double` | ponto flutuante binário | cálculo científico |
| `Decimal` | **precisão arbitrária** | **dinheiro, sempre** |

```apex
Double  d = 0.1 + 0.2;              // 0.30000000000000004  ← IEEE 754
Decimal m = 0.1 + 0.2;              // 0.3
Decimal valor = 10.005.setScale(2, System.RoundingMode.HALF_UP);   // 10.01
```

---

## 3. Triggers

```apex
trigger ContaTrigger on Account (before insert, before update, after insert, after update) {
    ContaTriggerHandler.run();
}
```

**Os sete contextos** e o que está disponível em cada um:

| Contexto | `Trigger.new` | `Trigger.old` | `newMap` | `oldMap` | Id preenchido |
|---|---|---|---|---|---|
| `before insert` | ✅ editável | ❌ | ❌ | ❌ | ❌ |
| `after insert` | ✅ leitura | ❌ | ✅ | ❌ | ✅ |
| `before update` | ✅ editável | ✅ | ✅ | ✅ | ✅ |
| `after update` | ✅ leitura | ✅ | ✅ | ✅ | ✅ |
| `before delete` | ❌ | ✅ | ❌ | ✅ | ✅ |
| `after delete` | ❌ | ✅ | ❌ | ✅ | ✅ |
| `after undelete` | ✅ leitura | ❌ | ✅ | ❌ | ✅ |

### 3.1 Padrão de trigger — o consenso do mercado

```apex
// 1. UM trigger por objeto. Sem lógica.
trigger ContaTrigger on Account (before insert, before update, after insert, after update) {
    ContaTriggerHandler.run();
}
```

```apex
// 2. Handler: traduz contexto → chamadas de domínio
public with sharing class ContaTriggerHandler {

    @TestVisible public static Boolean bypass = false;
    private static Set<Id> jaProcessados = new Set<Id>();

    public static void run() {
        if (bypass) { return; }

        if (Trigger.isBefore && Trigger.isInsert) {
            ContaService.normalizarDados((List<Account>) Trigger.new);
        }
        if (Trigger.isAfter && Trigger.isUpdate) {
            Set<Id> novos = idsAindaNaoProcessados(Trigger.newMap.keySet());
            if (!novos.isEmpty()) {
                ContaService.sincronizarFiliais(novos);
            }
        }
    }

    private static Set<Id> idsAindaNaoProcessados(Set<Id> candidatos) {
        Set<Id> novos = new Set<Id>(candidatos);
        novos.removeAll(jaProcessados);
        jaProcessados.addAll(novos);
        return novos;
    }
}
```

**Por que um trigger por objeto?** Porque a ordem de execução entre múltiplos triggers no
mesmo objeto é **indefinida pela plataforma**. Não é "má prática" — é comportamento não
especificado, que pode mudar entre releases.

**Por que a lógica não fica no trigger?** Porque triggers não são classes: não têm
construtor, não são instanciáveis, não implementam interfaces e não podem ser testados
isoladamente. Um handler pode.

**Por que a guarda contra recursão?** Porque a ordem de execução reinicia o ciclo em várias
situações (rollup atualizando o pai, workflow field update, DML em `after`). Sem guarda,
você entra em laço e vê `Maximum trigger depth exceeded` (limite: 16 níveis).

---

## 4. Assíncrono — as quatro formas

| | `@future` | **Queueable** | **Batch** | **Schedulable** |
|---|---|---|---|---|
| Parâmetros | só primitivos e coleções deles | **objetos completos** | construtor livre | construtor livre |
| Retorna Job Id | ❌ | ✅ | ✅ | ✅ |
| Encadeia | ❌ | ✅ (1 filho; 5 em DE) | ✅ | ✅ |
| Volume | pequeno | médio | **milhões** | — |
| Callout | com `(callout=true)` | com `Database.AllowsCallouts` | com `Database.AllowsCallouts` | via os outros |
| Monitorável | pobre | `AsyncApexJob` | `AsyncApexJob` | `CronTrigger` |
| Quando usar | legado; casos triviais | **padrão para tudo novo** | processar tabela inteira | horário fixo |

### 4.1 Queueable — o padrão moderno

```apex
public class SincronizarComERP implements Queueable, Database.AllowsCallouts {

    private final List<Id> pendentes;
    private final Integer  tentativa;

    public SincronizarComERP(List<Id> ids) { this(ids, 1); }
    public SincronizarComERP(List<Id> ids, Integer tentativa) {
        this.pendentes = ids;
        this.tentativa = tentativa;
    }

    public void execute(QueueableContext ctx) {
        // ... processa até 50 itens ...
        // Encadeamento com backoff: reagenda os que faltaram
        List<Id> restantes = new List<Id>();  // preenchido acima
        if (!restantes.isEmpty() && !Test.isRunningTest()) {
            System.enqueueJob(new SincronizarComERP(restantes, tentativa + 1));
        }
    }
}

Id jobId = System.enqueueJob(new SincronizarComERP(ids));
// jobId permite monitorar:
AsyncApexJob job = [SELECT Status, NumberOfErrors FROM AsyncApexJob WHERE Id = :jobId];
```

**Desde Winter '23**, Queueable suporta `Finalizer` — um bloco que roda mesmo se o job
falhar, análogo a um `finally`:

```apex
public class MeuJob implements Queueable, Finalizer {
    public void execute(QueueableContext ctx) {
        System.attachFinalizer(this);
        // ... trabalho que pode lançar ...
    }
    public void execute(FinalizerContext ctx) {
        if (ctx.getResult() == ParentJobResult.UNHANDLED_EXCEPTION) {
            // registre o erro, notifique, reagende — isto executa mesmo com falha
            System.debug(LoggingLevel.ERROR, ctx.getException().getMessage());
        }
    }
}
```

Isso resolve o problema histórico de "o job morreu e ninguém ficou sabendo".

### 4.2 Batch — o esqueleto e as decisões

```apex
public class ProcessarContas implements Database.Batchable<SObject>, Database.Stateful {
    public Integer processados = 0;

    public Database.QueryLocator start(Database.BatchableContext bc) {
        // QueryLocator: até 50 MILHÕES de registros. Um List<> comum: 50 mil.
        return Database.getQueryLocator([
            SELECT Id, Name FROM Account WHERE LastModifiedDate >= LAST_N_DAYS:7
        ]);
    }
    public void execute(Database.BatchableContext bc, List<Account> escopo) {
        // Limites RESETAM a cada lote. É por isso que Batch processa milhões.
        processados += escopo.size();
    }
    public void finish(Database.BatchableContext bc) {
        System.debug('Total: ' + processados);
    }
}
Database.executeBatch(new ProcessarContas(), 200);   // 200 = tamanho do lote
```

| Decisão | Efeito |
|---|---|
| **Tamanho do lote** | maior = menos jobs, mais risco de estourar CPU/heap por lote |
| `Database.Stateful` | preserva variáveis entre lotes, ao custo de serialização |
| `Database.AllowsCallouts` | permite HTTP; limite de callouts é **por lote** |
| `Iterable` em vez de `QueryLocator` | permite fonte customizada, mas cai para 50 mil registros |

**Limites de Batch:** 5 jobs ativos por org simultaneamente, 100 na fila.
Estourar dá `Attempted to schedule too many concurrent batch jobs`.

---

## 5. Bulkification — o conceito nº 1

```apex
// ❌ Morre com 101 registros
for (Opportunity o : Trigger.new) {
    Account a = [SELECT Industry FROM Account WHERE Id = :o.AccountId];   // 1 SOQL por item
    o.Setor__c = a.Industry;
}
```

```apex
// ✅ 1 SOQL, funciona com 1 ou 10.000
Set<Id> contaIds = new Set<Id>();
for (Opportunity o : Trigger.new) {
    if (o.AccountId != null) { contaIds.add(o.AccountId); }
}
Map<Id, Account> contas = new Map<Id, Account>([
    SELECT Id, Industry FROM Account WHERE Id IN :contaIds
]);
for (Opportunity o : Trigger.new) {
    Account a = contas.get(o.AccountId);
    if (a != null) { o.Setor__c = a.Industry; }
}
```

**O padrão em três passos, que resolve praticamente todos os casos:**
1. **Colete** as chaves num `Set`.
2. **Consulte uma vez** e monte um `Map`.
3. **Itere de novo**, resolvendo em memória.

**A regra absoluta:** nunca coloque dentro de um laço: SOQL, SOSL, DML, `sendEmail`,
callout, `System.enqueueJob`, `Database.executeBatch`, `Approval.process`,
`Schema.getGlobalDescribe()`.

---

## 6. Testes

```apex
@isTest
private class ContaServiceTest {

    /** Roda uma vez por classe; o estado é restaurado antes de cada método. */
    @TestSetup
    static void setup() {
        insert new Account(Name = 'Base');
    }

    @isTest
    static void cenarioFeliz() {
        Test.startTest();       // ← os governor limits ZERAM aqui
        ContaService.processar();
        Test.stopTest();        // ← jobs assíncronos enfileirados EXECUTAM aqui, síncronos

        Assert.areEqual(1, [SELECT COUNT() FROM Account WHERE Setor__c != NULL]);
    }

    @isTest
    static void sobOutroUsuario() {
        User u = [SELECT Id FROM User WHERE Profile.Name = 'Standard User' AND IsActive = true LIMIT 1];
        System.runAs(u) {
            // testa sharing, FLS e CRUD de verdade — não como System Administrator
        }
    }

    @isTest
    static void comCallout() {
        Test.setMock(HttpCalloutMock.class, new MeuMock());
        // callouts reais são PROIBIDOS em teste; sem mock, exceção
    }

    @isTest
    static void comBulk() {
        List<Account> muitas = new List<Account>();
        for (Integer i = 0; i < 200; i++) { muitas.add(new Account(Name = 'A' + i)); }
        Test.startTest();
        insert muitas;          // é ESTE teste que pega o bug de bulkification
        Test.stopTest();
    }
}
```

**Regras da plataforma:**

| Regra | Detalhe |
|---|---|
| Cobertura mínima para deploy em produção | **75% da org**, e cada trigger com **> 0%** |
| Todos os testes devem passar | inclusive os que você não escreveu |
| Testes não veem dados da org | exceto objetos de configuração (User, Profile, RecordType…) |
| `@isTest(SeeAllData=true)` | evite. Torna o teste dependente do ambiente |
| Callouts reais | proibidos; use `HttpCalloutMock` ou `WebServiceMock` |
| `Test.startTest/stopTest` | reseta limites e força execução do assíncrono |
| Classes `@isTest` | não contam para o limite de código da org |

> **Cobertura ≠ qualidade.** Um teste sem nenhum `Assert` cobre 100% das linhas e não
> testa nada. A plataforma só sabe medir cobertura; a responsabilidade pela asserção é sua.
> Se eu pudesse mudar uma coisa na plataforma, seria exigir asserções, não linhas.

**Ferramentas de teste que valem conhecer:** `ApexMocks` (mocking com stubs, usa a
`StubProvider` nativa), `Test.createStub()` (nativo, desde 2017), `Assert` (classe moderna,
desde Winter '23).

---

## 7. Tratamento de erro

```apex
// DML que lança em qualquer falha
insert contas;                                 // DmlException, tudo desfeito

// DML com falha parcial — o padrão para processos automáticos
List<Database.SaveResult> rs = Database.insert(contas, false);
for (Integer i = 0; i < rs.size(); i++) {
    if (!rs[i].isSuccess()) {
        for (Database.Error e : rs[i].getErrors()) {
            // getStatusCode() é enumerado e estável — melhor que fazer parse da mensagem
            System.debug(e.getStatusCode() + ': ' + e.getMessage() + ' campos: ' + e.getFields());
        }
    }
}

// Savepoint e rollback manual (máx. ~5 savepoints por transação)
Savepoint sp = Database.setSavepoint();
try {
    // ... várias operações ...
} catch (Exception e) {
    Database.rollback(sp);
    throw new MeuException('Operação desfeita: ' + e.getMessage(), e);
}

// addError: rejeita um registro específico dentro de um trigger, com mensagem no campo
for (Account a : Trigger.new) {
    if (a.AnnualRevenue != null && a.AnnualRevenue < 0) {
        a.AnnualRevenue.addError('Receita não pode ser negativa.');
    }
}
```

**Exceções que você precisa reconhecer:**

| Exceção | Causa |
|---|---|
| `DmlException` | falha de gravação (validação, permissão, obrigatório) |
| `QueryException` | SOQL atribuída a SObject retornando 0 ou >1 linha; query não seletiva |
| `NullPointerException` | o clássico |
| `ListException` | índice fora do intervalo |
| `LimitException` | governor limit estourado — **não pode ser capturada de forma útil**: uma vez estourado, a transação morre |
| `CalloutException` | timeout, DNS, TLS, endpoint não liberado |
| `AuraHandledException` | você lança para mandar mensagem legível ao LWC |
| `UNABLE_TO_LOCK_ROW` | contenção de bloqueio; ver [12-modelo-de-dados.md](12-modelo-de-dados.md) §7 |

> `LimitException` merece um aviso: você **não deve** tentar capturá-la para "continuar
> mesmo assim". Depois de estourar um limite, o estado da transação é indefinido. O certo é
> **não chegar lá** — medir com `Limits.getQueries()` e mudar de estratégia antes.

---

## 8. Performance em Apex

| Prática | Ganho |
|---|---|
| SOQL for-loop (`for (X x : [SELECT ...])`) | processa em lotes de 200; evita estourar heap |
| Consultar **só os campos que usa** | menos heap, menos CPU de serialização |
| `Map` em vez de laço aninhado | O(n) em vez de O(n²) — o maior ganho isolado |
| `Set.contains()` em vez de `List.contains()` | O(1) vs. O(n) |
| Só gravar o que mudou | menos DML, menos triggers em cascata |
| Evitar `Schema.getGlobalDescribe()` | é caríssimo; use `Type.forName` ou describe pontual |
| Concatenar String em laço | use `List<String>` + `String.join()` |
| `@AuraEnabled(cacheable=true)` | cache no cliente, não bate no servidor |
| Platform Cache | evita reconsultar dados estáveis (custa licença acima da cota gratuita) |

```apex
// ❌ O(n²) — 200 × 200 = 40.000 comparações
for (Account a : contas) {
    for (Contact c : contatos) {
        if (c.AccountId == a.Id) { /* ... */ }
    }
}

// ✅ O(n) — um passe para indexar, um para usar
Map<Id, List<Contact>> porConta = new Map<Id, List<Contact>>();
for (Contact c : contatos) {
    if (!porConta.containsKey(c.AccountId)) {
        porConta.put(c.AccountId, new List<Contact>());
    }
    porConta.get(c.AccountId).add(c);
}
for (Account a : contas) {
    List<Contact> desta = porConta.get(a.Id);
    // ...
}
```

---

## 9. A mudança da API 67.0 — user mode por padrão

**A mudança mais significativa no modelo de segurança do Apex em quase duas décadas.**
Vale para classes e triggers cuja **versão de API** seja **67.0 ou superior**.

| Comportamento | Até API 66.0 | A partir da API 67.0 |
|---|---|---|
| SOQL, SOSL, DML e métodos `Database.*` | **system mode** (ignora FLS e CRUD) | **user mode** (aplica FLS e CRUD) |
| Classe sem declaração de sharing | `without sharing` na maioria dos contextos | **`with sharing`** |
| `WITH SECURITY_ENFORCED` | válida | **removida — não compila** |

### 9.1 O que fazer com o código existente

```apex
// Antes (v66 e anteriores)
List<Account> a = [SELECT Id, Salario__c FROM Account WITH SECURITY_ENFORCED];

// Depois (v67+)
List<Account> a = [SELECT Id, Salario__c FROM Account WITH USER_MODE];
// ou, como user mode já é o padrão, simplesmente:
List<Account> a = [SELECT Id, Salario__c FROM Account];
```

```apex
// Quando você PRECISA ignorar (job de sistema, sincronização, cálculo de rollup):
List<Account> todos = [SELECT Id FROM Account WITH SYSTEM_MODE];
Database.update(registros, false, AccessLevel.SYSTEM_MODE);
// Comente SEMPRE o porquê. Toda exceção sem justificativa é um achado de auditoria.
```

### 9.2 Estratégia de migração que eu recomendo

1. **Não suba a versão de API de tudo de uma vez.** Faça classe a classe, ou módulo a módulo.
2. **Antes de subir, escreva testes com `System.runAs`** sob um usuário que *não* seja
   administrador. É o único jeito de descobrir o que vai quebrar.
3. **Procure `WITH SECURITY_ENFORCED` no projeto inteiro** e troque por `WITH USER_MODE` —
   isso é obrigatório antes de subir para 67.
4. **Identifique os métodos que legitimamente precisam de system mode** (jobs, integrações,
   cálculos administrativos) e marque-os explicitamente com `SYSTEM_MODE`.
5. **Rode o Salesforce Code Analyzer** — ele tem regras específicas para isso.
6. **Espere que quebre.** Uma org com 10 anos de Apex tem código que só funciona porque
   ignorava a segurança. Descobrir isso é o objetivo, não um efeito colateral.

> **Opinião profissional:** essa mudança vai custar caro a muita gente e é inequivocamente
> a decisão certa. O padrão inseguro produziu, ao longo de 18 anos, uma quantidade enorme
> de código que expõe dados que o usuário não deveria ver — e quase sempre sem que ninguém
> tenha decidido isso conscientemente.

---

## 10. Os cinco porquês: por que 75% de cobertura de teste?

**1. Por que a Salesforce obriga cobertura de teste para deploy em produção?**
Porque código quebrado em produção numa plataforma multi-inquilino gera chamados de suporte
que a Salesforce paga, e reputação que a Salesforce perde.

**2. Por que 75% e não 80% ou 100%?**
75% é um número de compromisso: alto o bastante para forçar o hábito, baixo o bastante para
não inviabilizar entregas. Não há justificativa técnica publicada para o valor exato — é uma
convenção administrativa. Não sei de fonte oficial que explique a escolha do número.

**3. Por que medir *cobertura* e não *qualidade* do teste?**
Porque cobertura é a única métrica que a plataforma consegue medir automaticamente e de
forma objetiva. "O teste é bom?" não é computável.

**4. Isso não incentiva testes inúteis?**
Sim, e incentiva mesmo. Existe uma quantidade enorme de Apex no mundo cujos testes só criam
dados e chamam métodos, sem uma única asserção. A métrica é gamificável e é gamificada.

**5. Então valeu a pena?**
Na minha opinião, sim — e com folga. O ecossistema Salesforce tem, em média, mais testes
automatizados que ecossistemas comparáveis, precisamente porque a plataforma tornou o teste
**inegociável** e não uma questão de disciplina do time. Uma métrica imperfeita e obrigatória
produziu mais resultado que uma métrica perfeita e opcional.

*(Parada legítima: convenção administrativa explícita, com trade-off declarado.)*

---

## 11. Referência rápida de anotações

| Anotação | Efeito |
|---|---|
| `@isTest` | classe ou método de teste |
| `@TestSetup` | dados criados uma vez, restaurados entre métodos |
| `@TestVisible` | membro privado acessível pelos testes |
| `@future` | assíncrono simples |
| `@future(callout=true)` | assíncrono com permissão de callout |
| `@AuraEnabled` | expõe ao LWC/Aura |
| `@AuraEnabled(cacheable=true)` | permite `@wire` e cache no cliente; **proíbe DML** |
| `@InvocableMethod` | expõe a Flow (recebe e devolve listas) |
| `@InvocableVariable` | campo de entrada/saída de ação invocável |
| `@RestResource(urlMapping='/x/*')` | expõe endpoint REST |
| `@HttpGet/@HttpPost/@HttpPut/@HttpPatch/@HttpDelete` | verbo do endpoint |
| `@ReadOnly` | eleva o limite de registros consultados para 1 milhão; proíbe DML |
| `@SuppressWarnings` | silencia avisos do analisador |
| `@Deprecated` | marca API de pacote gerenciado como obsoleta |
| `@JsonAccess` | controla serialização de classes de pacote |
| `@NamespaceAccessible` | expõe entre namespaces de pacotes |

---

## Autoteste

1. Por que Apex não permite criar threads nem abrir sockets?
2. Escreva o padrão de bulkification em três passos. Por que ele resolve o problema?
3. Qual a diferença entre `insert lista;` e `Database.insert(lista, false);`?
4. Quando usar Queueable em vez de `@future`? Cite três vantagens.
5. O que `Test.startTest()` faz, além de delimitar o trecho testado?
6. Por que não se deve tentar capturar `LimitException`?
7. O que mudou na API 67.0 quanto a user mode e sharing? Qual cláusula deixou de compilar?
8. Escreva a estratégia de migração de uma classe de v58 para v67, em cinco passos.
9. Por que a plataforma mede cobertura em vez de qualidade de teste? Isso valeu a pena?
10. Transforme um laço aninhado O(n²) em O(n) usando `Map`. Explique o ganho.

---

### Fontes consultadas (11/08/2026)

- Salesforce Developers Blog — *The Salesforce Developer's Guide to the Summer '26 Release* — https://developer.salesforce.com/blogs/2026/06/the-salesforce-developers-guide-to-the-summer-26-release
- Salesforce Blog — *Summer '26 Release Architect Highlights: Sharing, Security, and Agentic Integration* — https://www.salesforce.com/blog/summer-26-release-architect-highlights/
- conemis — *Salesforce Summer '26 Release API Updates: API Version 67.0* — https://www.conemis.com/news/salesforce-summer-26-release-api-updates-version-67-0
