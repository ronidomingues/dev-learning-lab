# 05 · Manual de uso — referência consultável

`Nível: intermediário` · `Atualizado: 11/08/2026` · `CLI 2.146.x · API 67.0`

Organizado **por tarefa**, não por ordem alfabética. Use `Ctrl+F`.
Convenção: `-o` é sempre `--target-org`; omita se você já rodou `sf config set target-org=<alias>`.

---

## Índice

1. [Salesforce CLI — mapa dos comandos](#1-salesforce-cli--mapa-dos-comandos)
2. [Autenticação e orgs](#2-autenticação-e-orgs)
3. [Projeto: deploy, retrieve, manifest](#3-projeto-deploy-retrieve-manifest)
4. [Dados: consultar, criar, importar, exportar](#4-dados-consultar-criar-importar-exportar)
5. [Apex: executar, testar, logar](#5-apex-executar-testar-logar)
6. [Geração de código (scaffolding)](#6-geração-de-código-scaffolding)
7. [Packaging](#7-packaging)
8. [SOQL — referência de sintaxe](#8-soql--referência-de-sintaxe)
9. [SOSL — busca textual](#9-sosl--busca-textual)
10. [Apex — referência rápida da linguagem](#10-apex--referência-rápida-da-linguagem)
11. [Governor limits — a tabela que você vai consultar sempre](#11-governor-limits--a-tabela-que-você-vai-consultar-sempre)
12. [Tipos de metadado mais usados](#12-tipos-de-metadado-mais-usados)
13. [Navegação no Setup — caminhos diretos por URL](#13-navegação-no-setup--caminhos-diretos-por-url)
14. [Atalhos e padrões que só quem usa há anos conhece](#14-atalhos-e-padrões-que-só-quem-usa-há-anos-conhece)
15. [O que está obsoleto](#15-o-que-está-obsoleto)

---

## 1. Salesforce CLI — mapa dos comandos

A CLI segue o padrão `sf <tópico> <subtópico> <ação> [flags]`.

| Tópico | Para quê |
|---|---|
| `sf org` | Criar, autorizar, abrir, listar, deletar orgs |
| `sf project` | Deploy, retrieve, gerar projeto, converter formato |
| `sf data` | CRUD de registros, query, import/export em massa |
| `sf apex` | Executar, testar, logs |
| `sf lightning` | Gerar componentes |
| `sf package` | Pacotes de segunda geração (2GP) |
| `sf sobject` | Descrever objetos e listar |
| `sf schema` | Metadados de esquema |
| `sf force` | Comandos legados (evite; migrando para os acima) |
| `sf plugins` | Gerenciar plugins |
| `sf doctor` | Diagnóstico do ambiente |

**Flags globais úteis:**

| Flag | Efeito |
|---|---|
| `--json` | Saída em JSON — essencial para script e CI |
| `-o, --target-org` | Escolhe a org |
| `-w, --wait <min>` | Espera a operação assíncrona terminar |
| `--flags-dir <dir>` | Lê flags de arquivos, para comandos longos |
| `--help` | Ajuda daquele comando (sempre atual, use-a) |

```bash
sf commands            # lista TODOS os comandos disponíveis
sf <comando> --help    # a fonte da verdade; a doc online pode estar atrás
```

---

## 2. Autenticação e orgs

| Tarefa | Comando |
|---|---|
| Login por navegador | `sf org login web -a meualias -s` |
| Login sem navegador (servidor/container) | `sf org login device -a meualias` |
| Login em sandbox | `sf org login web -a uat -r https://test.salesforce.com` |
| Login para CI (JWT, sem senha) | `sf org login jwt -f server.key -i <consumerKey> -u <user> -a ci` |
| Listar orgs autorizadas | `sf org list` |
| Detalhes e token de acesso | `sf org display -o meualias` |
| Abrir no navegador | `sf org open -o meualias` |
| Abrir numa página específica | `sf org open -p lightning/setup/ApexClasses/home` |
| Definir org padrão do projeto | `sf config set target-org=meualias` |
| Definir Dev Hub padrão | `sf config set target-dev-hub=devhub` |
| Sair / revogar token | `sf org logout -o meualias` |
| Criar scratch org | `sf org create scratch -f config/project-scratch-def.json -a s1 -d 7 -y 7` |
| Deletar scratch org | `sf org delete scratch -o s1 -p` |
| Criar sandbox | `sf org create sandbox -l Developer -n uat1 -o prod -w 60` |
| Atualizar sandbox | `sf org refresh sandbox -n uat1 -o prod` |
| Gerar usuário na scratch org | `sf org create user -f config/user-def.json` |
| Gerar senha para o usuário | `sf org generate password -o s1` |

> **`-r/--instance-url` importa.** Sandboxes ficam em `test.salesforce.com`; orgs de
> produção e DE em `login.salesforce.com`. Errar isso dá "invalid credentials" com a
> senha certa — é o erro de login mais comum de todos.

---

## 3. Projeto: deploy, retrieve, manifest

### 3.1 Deploy (disco → org)

| Tarefa | Comando |
|---|---|
| Enviar uma pasta | `sf project deploy start -d force-app` |
| Enviar um arquivo | `sf project deploy start -d force-app/main/default/classes/X.cls` |
| Enviar por tipo de metadado | `sf project deploy start -m "ApexClass:X,CustomObject:Conta__c"` |
| Enviar por manifesto | `sf project deploy start -x manifest/package.xml` |
| Simular sem gravar (**validação**) | `sf project deploy start -d force-app --dry-run` |
| Ver o que mudaria | `sf project deploy preview -d force-app` |
| Deploy com testes específicos | `sf project deploy start -d force-app -l RunSpecifiedTests -t MinhaTest` |
| Deploy para produção (exige testes) | `sf project deploy start -d force-app -l RunLocalTests -w 60` |
| Validar para *quick deploy* | `sf project deploy validate -d force-app -l RunLocalTests -w 60` |
| Executar o quick deploy validado | `sf project deploy quick -i <jobId>` |
| Ver status de um deploy | `sf project deploy report -i <jobId>` |
| Cancelar | `sf project deploy cancel -i <jobId>` |

**Níveis de teste (`-l`):**

| Valor | Roda | Quando usar |
|---|---|---|
| `NoTestRun` | nada | sandbox, iteração rápida (padrão em não-produção) |
| `RunSpecifiedTests` | só os que você listar | validação pontual |
| `RunLocalTests` | todos os seus, exceto de pacotes gerenciados | **produção — o padrão correto** |
| `RunAllTestsInOrg` | tudo, inclusive de pacotes | auditoria, raramente |

> **Padrão de produção maduro:** `deploy validate` durante o dia (leva 40–90 min numa org
> grande), guardando o `jobId`, e `deploy quick` na janela de release (leva segundos).
> A validação vale por **10 dias**. Isso transforma uma janela de 2 horas numa de 5 minutos.

### 3.2 Retrieve (org → disco)

| Tarefa | Comando |
|---|---|
| Trazer por tipo | `sf project retrieve start -m "ApexClass:X"` |
| Trazer tudo de um tipo | `sf project retrieve start -m "ApexClass"` |
| Trazer por manifesto | `sf project retrieve start -x manifest/package.xml` |
| Trazer o que mudou (source tracking) | `sf project retrieve start` |
| Ver diferenças sem baixar | `sf project retrieve preview` |

### 3.3 Manifesto (`package.xml`)

```bash
sf project generate manifest --source-dir force-app --name package
```
*Gera um `package.xml` cobrindo tudo que está em `force-app`.*

```bash
sf project generate manifest --from-org devorg --metadata "ApexClass,CustomObject"
```
*Gera um manifesto a partir do que existe na org.*

Estrutura do arquivo:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<Package xmlns="http://soap.sforce.com/2006/04/metadata">
    <types>
        <members>ContaService</members>
        <members>ContaServiceTest</members>
        <types-placeholder/>
        <name>ApexClass</name>
    </types>
    <types>
        <members>*</members>              <!-- * = todos daquele tipo -->
        <name>CustomObject</name>
    </types>
    <version>67.0</version>
</Package>
```

**Manifesto de destruição** (`destructiveChanges.xml`) — para apagar metadados:
```bash
sf project deploy start --manifest manifest/package.xml \
  --pre-destructive-changes manifest/destructiveChanges.xml
```
*Apaga o que está no destrutivo **antes** de aplicar o pacote. Use `--post-destructive-changes`
para apagar depois (necessário quando o novo código substitui o antigo).*

### 3.4 `.forceignore`

Mesma sintaxe do `.gitignore`. Impede que arquivos sejam enviados ou recebidos.

```gitignore
# Perfis são um pesadelo de merge — gerencie por permission set
**/profiles/**

# Metadados que a org gera sozinha
**/jsconfig.json
**/.eslintrc.json

# Nunca versione isto
.sf/
.sfdx/
```

---

## 4. Dados: consultar, criar, importar, exportar

| Tarefa | Comando |
|---|---|
| Consultar (SOQL) | `sf data query -q "SELECT Id, Name FROM Account LIMIT 10"` |
| Consultar em CSV | `sf data query -q "..." -r csv > contas.csv` |
| Consultar objetos de ferramenta (Tooling API) | `sf data query -q "SELECT Name FROM ApexClass" -t` |
| Consultar volume grande (Bulk API 2.0) | `sf data query -q "..." --bulk -w 10` |
| Criar um registro | `sf data create record -s Account -v "Name='Acme' Industry='Technology'"` |
| Ler um registro | `sf data get record -s Account -i 001xx...` |
| Atualizar | `sf data update record -s Account -i 001xx... -v "Industry='Banking'"` |
| Deletar | `sf data delete record -s Account -i 001xx...` |
| Importar CSV em massa | `sf data import bulk -s Account -f contas.csv -w 10` |
| Atualizar em massa | `sf data update bulk -s Account -f contas.csv -w 10` |
| Upsert em massa | `sf data upsert bulk -s Account -f contas.csv -i ExternalId__c -w 10` |
| Deletar em massa | `sf data delete bulk -s Account -f ids.csv -w 10` |
| Exportar árvore de registros | `sf data export tree -q "SELECT Id, Name, (SELECT LastName FROM Contacts) FROM Account" -d dados/ -p` |
| Importar árvore | `sf data import tree -p dados/plan.json` |

> **`export tree` + `import tree` é a forma correta de semear uma scratch org.**
> Ele preserva relacionamentos usando referências simbólicas em vez de IDs — que mudam
> entre orgs. Alternativa mais poderosa para volume: o plugin comunitário `sfdmu`.

**Diferença crucial entre as APIs de dados:**

| API | Volume | Modo | Custa do limite de |
|---|---|---|---|
| REST/SOAP (`data query`) | até ~2.000 por chamada | síncrono | chamadas de API |
| **Bulk API 2.0** (`--bulk`) | milhões | assíncrono, em lotes | limites de Bulk (separados) |
| Tooling API (`-t`) | metadados e código | síncrono | chamadas de API |

---

## 5. Apex: executar, testar, logar

| Tarefa | Comando |
|---|---|
| Executar Apex anônimo | `sf apex run -f script.apex` |
| Rodar todos os testes locais | `sf apex run test -l RunLocalTests -w 20 -r human -c` |
| Rodar uma classe de teste | `sf apex run test -n MinhaTest -w 10 -r human` |
| Rodar um método específico | `sf apex run test --tests MinhaTest.metodo -w 10` |
| Resultado de execução anterior | `sf apex get test -i <testRunId>` |
| Ver logs disponíveis | `sf apex list log` |
| Baixar um log | `sf apex get log -i 07Lxx...` |
| Log ao vivo (tail) | `sf apex tail log -c` |
| Ligar debug log de um usuário | Setup → Debug Logs → *New* (ou `sf apex tail log`, que ativa um trace temporário) |

**Flags de teste que importam:**

| Flag | Efeito |
|---|---|
| `-c, --code-coverage` | inclui cobertura no resultado |
| `-r human\|tap\|junit\|json` | formato; use `junit` em CI |
| `--output-dir <dir>` | salva os resultados em arquivos |
| `--synchronous` | roda em série (útil para depurar; mais lento) |
| `--detailed-coverage` | cobertura linha a linha |

**Níveis de log** (`Setup → Debug Levels`): `NONE`, `ERROR`, `WARN`, `INFO`, `DEBUG`, `FINE`, `FINER`, `FINEST`.

> **Armadilha:** logs têm teto de **20 MB** por transação. Ao estourar, o log é **truncado
> no meio** e você perde justamente o fim, onde está o erro. Se seu log some, baixe o
> nível de `ApexCode` de `FINEST` para `DEBUG` e desligue as categorias que não interessam.

---

## 6. Geração de código (scaffolding)

| Tarefa | Comando |
|---|---|
| Projeto | `sf project generate -n meuprojeto -t standard` |
| Classe Apex | `sf apex generate class -n MinhaClasse -d force-app/main/default/classes` |
| Trigger Apex | `sf apex generate trigger -n ContaTrigger -s Account -e before insert,after update -d force-app/main/default/triggers` |
| LWC | `sf lightning generate component -n meuComp --type lwc -d force-app/main/default/lwc` |
| Aura (legado) | `sf lightning generate component -n meuComp --type aura -d force-app/main/default/aura` |
| Página Visualforce (legado) | `sf visualforce generate page -n MinhaPagina -d force-app/main/default/pages` |
| Manifesto | `sf project generate manifest -d force-app` |

---

## 7. Packaging

Pacotes de segunda geração (**2GP**) são a forma moderna de empacotar e versionar.

| Tarefa | Comando |
|---|---|
| Criar o pacote (uma vez) | `sf package create -n MeuPacote -t Unlocked -r force-app` |
| Criar uma versão | `sf package version create -p MeuPacote -x manifest/package.xml -w 60 -k <senha>` |
| Listar versões | `sf package version list -p MeuPacote` |
| Promover para *released* | `sf package version promote -p MeuPacote@1.0.0-1` |
| Instalar numa org | `sf package install -p 04txx... -w 20 -o alvo` |
| Desinstalar | `sf package uninstall -p 04txx... -o alvo` |

| Tipo de pacote | Quem edita depois | Uso típico |
|---|---|---|
| **Unlocked** | o cliente pode editar na org | organizar a própria org por módulos |
| **Managed** | ninguém — código oculto | vender no AppExchange |
| Unmanaged (legado) | vira código solto na org | evitar; sem upgrade |

---

## 8. SOQL — referência de sintaxe

*Salesforce Object Query Language.* Parece SQL, **não é SQL**. Diferenças que doem estão marcadas.

### 8.1 Estrutura

```sql
SELECT campos
FROM objeto
[WHERE condição]
[WITH SECURITY_ENFORCED | WITH USER_MODE | WITH SYSTEM_MODE]
[GROUP BY campo [HAVING condição]]
[ORDER BY campo [ASC|DESC] [NULLS FIRST|LAST]]
[LIMIT n] [OFFSET n]
[FOR VIEW | FOR REFERENCE | FOR UPDATE]
```

### 8.2 O que **não existe** em SOQL (e existe em SQL)

| Não existe | Faça em vez disso |
|---|---|
| `SELECT *` | Liste os campos. Sempre. (Ou use `FIELDS(STANDARD)` / `FIELDS(ALL)` com `LIMIT 200`) |
| `JOIN` arbitrário | Só relacionamentos declarados, via notação de ponto ou subquery |
| `UNION` | Duas queries e junte em Apex |
| Subquery no `SELECT` (escalar) | Não há; use consulta separada |
| `LIKE` com função | Só `LIKE 'texto%'`, `'%texto%'`, `'%texto'` |
| `DISTINCT` | Use `GROUP BY` |
| Índice sob seu controle | Peça ao Suporte um índice customizado; ou use *External ID* / campo *Unique* |

### 8.3 Relacionamentos

```sql
-- Filho → pai: notação de ponto (até 5 níveis)
SELECT Id, Name, Account.Name, Account.Owner.Email
FROM Contact

-- Pai → filhos: subquery com o NOME DO RELACIONAMENTO (plural), não o do objeto
SELECT Id, Name, (SELECT LastName, Email FROM Contacts)
FROM Account

-- Em objeto customizado, o relacionamento ganha __r (e o campo, __c)
SELECT Id, Conta__r.Name, (SELECT Id FROM Itens__r)
FROM Pedido__c

-- Relacionamento polimórfico
SELECT Id, TYPEOF What WHEN Account THEN Industry WHEN Opportunity THEN Amount END
FROM Event
```

**A regra de nomenclatura que confunde todo mundo:**

| Coisa | Sufixo | Exemplo |
|---|---|---|
| Objeto customizado | `__c` | `Pedido__c` |
| Campo customizado | `__c` | `Valor_Total__c` |
| Relacionamento **para o pai** | `__r` | `Conta__r.Name` |
| Relacionamento **para filhos** | `__r` (plural, definido no campo pai) | `(SELECT ... FROM Itens__r)` |
| Campo/objeto de pacote gerenciado | `ns__Nome__c` | `fin__Fatura__c` |

### 8.4 Filtros de data — literais que economizam código

```sql
WHERE CreatedDate = TODAY
WHERE CloseDate   = THIS_MONTH
WHERE CreatedDate = LAST_N_DAYS:30
WHERE CloseDate   = NEXT_FISCAL_QUARTER
WHERE LastModifiedDate > 2026-08-01T00:00:00Z    -- datetime é sempre UTC, sem aspas
WHERE CloseDate       > 2026-08-01                -- date é sem aspas, formato ISO
```

Literais disponíveis: `YESTERDAY`, `TODAY`, `TOMORROW`, `LAST_WEEK`, `THIS_WEEK`,
`NEXT_WEEK`, `LAST_MONTH`, `THIS_MONTH`, `NEXT_MONTH`, `LAST_90_DAYS`, `NEXT_90_DAYS`,
`LAST_N_DAYS:n`, `NEXT_N_DAYS:n`, `THIS_QUARTER`, `THIS_FISCAL_YEAR`, `LAST_N_FISCAL_QUARTERS:n`.

### 8.5 Agregação

```sql
SELECT Industry, COUNT(Id) total, SUM(AnnualRevenue) receita, AVG(NumberOfEmployees) media
FROM Account
WHERE AnnualRevenue != NULL
GROUP BY Industry
HAVING COUNT(Id) > 5
ORDER BY SUM(AnnualRevenue) DESC
```

Funções: `COUNT()`, `COUNT(campo)`, `COUNT_DISTINCT()`, `SUM()`, `AVG()`, `MIN()`, `MAX()`.
Também `GROUP BY ROLLUP(...)` e `GROUP BY CUBE(...)` para subtotais.

Em Apex, o retorno é `List<AggregateResult>`:
```apex
for (AggregateResult ar : [SELECT Industry ind, COUNT(Id) c FROM Account GROUP BY Industry]) {
    String setor = (String)  ar.get('ind');
    Integer qtd  = (Integer) ar.get('c');
}
```

### 8.6 Semi-join e anti-join

```sql
-- Contas que têm ao menos uma oportunidade fechada
SELECT Id FROM Account WHERE Id IN (SELECT AccountId FROM Opportunity WHERE IsWon = true)

-- Contas SEM nenhum contato
SELECT Id FROM Account WHERE Id NOT IN (SELECT AccountId FROM Contact WHERE AccountId != NULL)
```
**Limite:** no máximo 2 semi/anti-joins por query, e a subquery não pode ter `LIMIT`.

### 8.7 Modo de execução (mudou na API 67.0 — leia)

```sql
SELECT Id FROM Account WITH USER_MODE      -- respeita FLS, permissões e sharing do usuário
SELECT Id FROM Account WITH SYSTEM_MODE    -- ignora (use com consciência)
```

> **Mudança de contrato em Summer '26 / API 67.0:** consultas e DML em Apex passam a rodar
> em **user mode por padrão** (antes era system mode). E a cláusula
> `WITH SECURITY_ENFORCED` foi **removida** — classes em v67.0+ que a usem **não compilam**.
> Substitua por `WITH USER_MODE`. Detalhes e estratégia de migração em
> [15-apex.md](15-apex.md) §9.

### 8.8 Vinculação de variáveis (bind)

```apex
String nome = 'Acme%';
Set<Id> ids = new Set<Id>{'001xx...'};
List<Account> r = [SELECT Id FROM Account WHERE Name LIKE :nome AND Id IN :ids];
```
O `:` faz *bind* com escape automático — **é a defesa contra SOQL injection**.
Em SOQL dinâmica, use a forma segura:
```apex
Map<String,Object> binds = new Map<String,Object>{ 'n' => nome };
Database.queryWithBinds('SELECT Id FROM Account WHERE Name LIKE :n', binds, AccessLevel.USER_MODE);
```
**Nunca** concatene entrada de usuário em SOQL dinâmica. Se não houver jeito, use
`String.escapeSingleQuotes()`.

---

## 9. SOSL — busca textual

*Salesforce Object Search Language.* Enquanto SOQL busca em **um** objeto por campos
estruturados, SOSL busca **texto** em vários objetos ao mesmo tempo, usando índice de busca.

```apex
List<List<SObject>> resultados = [
    FIND 'acme OR "sabor da esquina"'
    IN NAME FIELDS
    RETURNING Account(Id, Name WHERE Industry = 'Technology' ORDER BY Name LIMIT 10),
              Contact(Id, LastName),
              Lead(Id, Company)
    LIMIT 200
];
List<Account> contas = (List<Account>) resultados[0];
```

| Escopo (`IN ... FIELDS`) | Busca em |
|---|---|
| `ALL FIELDS` | todos os campos indexados |
| `NAME FIELDS` | campos de nome |
| `EMAIL FIELDS` | campos de e-mail |
| `PHONE FIELDS` | telefones |
| `SIDEBAR FIELDS` | o que a busca global usa |

**Quando usar SOSL em vez de SOQL:** busca "tipo Google" pelo usuário; procurar um termo
sem saber em qual objeto está; `LIKE '%texto%'` em tabela grande (que não usa índice e
é lentíssimo, enquanto o SOSL usa o índice invertido).

---

## 10. Apex — referência rápida da linguagem

### 10.1 Tipos

| Categoria | Tipos |
|---|---|
| Primitivos | `Integer`, `Long`, `Decimal`, `Double`, `Boolean`, `String`, `Date`, `Datetime`, `Time`, `Id`, `Blob`, `Object` |
| Coleções | `List<T>`, `Set<T>`, `Map<K,V>` |
| sObject | `Account`, `Contact`, `Meu_Objeto__c`, ou o genérico `SObject` |
| Enum | `enum Status { NOVO, ATIVO }` |
| Especiais | `Schema.*`, `Database.*`, `System.*` |

> **Use `Decimal` para dinheiro, nunca `Double`.** `Double` é ponto flutuante binário e
> erra centavos. `Decimal` é de precisão arbitrária com escala controlada. Isso não é
> peculiaridade do Apex — é IEEE 754 — mas é um bug clássico em código de faturamento.

### 10.2 DML

```apex
insert conta;                    // lança exceção se qualquer registro falhar
update contas;                   // aceita lista (até 10.000)
upsert contas Chave_Externa__c;  // insere ou atualiza pela chave externa
delete contas;
undelete contasDaLixeira;        // registros ficam 15 dias na Recycle Bin
merge contaMestre contasDuplicadas;

// Versão que NÃO lança exceção — retorna resultado por registro (parcial sucesso)
Database.SaveResult[] rs = Database.insert(contas, false);
for (Database.SaveResult r : rs) {
    if (!r.isSuccess()) {
        for (Database.Error e : r.getErrors()) System.debug(e.getMessage());
    }
}

// Com controle explícito de modo (API 67+)
Database.insert(contas, AccessLevel.USER_MODE);
```

### 10.3 Triggers

```apex
trigger ContaTrigger on Account (before insert, before update, after insert, after update) {
    // Padrão obrigatório: UM trigger por objeto, sem lógica dentro dele.
    ContaTriggerHandler.run();
}
```

Contexto disponível dentro de um trigger:

| Variável | Antes de insert | Depois de insert | Antes de update | Depois de update | Delete |
|---|---|---|---|---|---|
| `Trigger.new` | ✅ (editável) | ✅ (só leitura) | ✅ (editável) | ✅ (só leitura) | ❌ |
| `Trigger.old` | ❌ | ❌ | ✅ | ✅ | ✅ |
| `Trigger.newMap` | ❌ (sem Id ainda) | ✅ | ✅ | ✅ | ❌ |
| `Trigger.oldMap` | ❌ | ❌ | ✅ | ✅ | ✅ |
| `Trigger.isBefore/isAfter/isInsert/...` | ✅ | ✅ | ✅ | ✅ | ✅ |
| `Trigger.size` | ✅ | ✅ | ✅ | ✅ | ✅ |

**Regra de ouro:** altere campos do próprio registro em `before`; crie/atualize **outros**
registros em `after`. Fazer DML no próprio registro em `after` causa recursão.

### 10.4 Assíncrono — as quatro formas

| Forma | Como | Use quando |
|---|---|---|
| `@future` | `@future(callout=true) public static void m(Set<Id> ids)` | callout a partir de trigger; simples; **só parâmetros primitivos** |
| **Queueable** | `implements Queueable, Database.AllowsCallouts` | quase sempre a melhor escolha: aceita objetos, encadeia, tem Job ID |
| **Batch** | `implements Database.Batchable<SObject>` | processar milhões de registros em lotes |
| **Schedulable** | `implements Schedulable` | rodar em horário; use `System.schedule('nome','0 0 2 * * ?', new X())` |

```apex
// Queueable — o padrão moderno
public class EnviarNotificacao implements Queueable, Database.AllowsCallouts {
    private final List<Id> ids;
    public EnviarNotificacao(List<Id> ids) { this.ids = ids; }
    public void execute(QueueableContext ctx) {
        // ... trabalho ...
        // Encadeamento: até 1 filho por job (5 em Developer Edition)
        // System.enqueueJob(new OutroJob());
    }
}
System.enqueueJob(new EnviarNotificacao(idsList));
```

```apex
// Batch — o esqueleto que você vai copiar
global class RecalcularContas implements Database.Batchable<SObject>, Database.Stateful {
    global Integer processados = 0;                      // Stateful preserva entre lotes
    global Database.QueryLocator start(Database.BatchableContext bc) {
        return Database.getQueryLocator('SELECT Id, AnnualRevenue FROM Account');
    }
    global void execute(Database.BatchableContext bc, List<Account> escopo) {
        for (Account a : escopo) { a.AnnualRevenue = 0; }
        update escopo;
        processados += escopo.size();
    }
    global void finish(Database.BatchableContext bc) {
        System.debug('Total: ' + processados);
    }
}
Database.executeBatch(new RecalcularContas(), 200);   // 200 = tamanho do lote
```

### 10.5 Testes

```apex
@isTest
private class MinhaTest {
    @TestSetup static void setup() { /* dados criados uma vez, restaurados por método */ }

    @isTest static void cenario() {
        Test.startTest();                 // reinicia os governor limits aqui
        // ... código sob teste ...
        Test.stopTest();                  // força a execução de tudo que era assíncrono
        Assert.areEqual(esperado, obtido, 'mensagem que explica a falha');
    }

    @isTest static void comMock() {
        Test.setMock(HttpCalloutMock.class, new MeuMock());   // callouts em teste
    }

    @isTest static void comUsuario() {
        User u = [SELECT Id FROM User WHERE Profile.Name = 'Standard User' LIMIT 1];
        System.runAs(u) { /* testa segurança e sharing sob outro usuário */ }
    }
}
```

Classe `Assert` (moderna, desde Winter '23) — prefira-a a `System.assertEquals`:
`Assert.areEqual`, `Assert.areNotEqual`, `Assert.isTrue`, `Assert.isFalse`,
`Assert.isNull`, `Assert.isNotNull`, `Assert.isInstanceOfType`, `Assert.fail`.

---

## 11. Governor limits — a tabela que você vai consultar sempre

Limites **por transação**, salvo indicação. Válidos em API 67.0.

| Recurso | Síncrono | Assíncrono |
|---|---|---|
| Consultas SOQL | 100 | 200 |
| Registros retornados por SOQL (total) | 50.000 | 50.000 |
| Registros por `QueryLocator` (batch `start`) | 10.000 | 50.000.000 |
| Consultas SOSL | 20 | 20 |
| Registros por SOSL | 2.000 | 2.000 |
| Instruções DML | 150 | 150 |
| Registros processados por DML | 10.000 | 10.000 |
| **Tempo de CPU** | **10.000 ms** | **60.000 ms** |
| Memória heap | 6 MB | 12 MB |
| Callouts HTTP | 100 | 100 |
| Tempo total de callout | 120 s | 120 s |
| `@future` invocados | 50 | 0 (não pode chamar de future) |
| Jobs Queueable enfileirados | 50 | 1 (encadeamento) |
| E-mails via `Messaging.sendEmail` | 10 | 10 |
| `describe` de sObject | ilimitado (era 100) | — |

**Limites por org / por 24 h:**

| Recurso | Limite |
|---|---|
| Chamadas de API | 15.000 (DE) · 100.000+ (EE, escala com licenças) |
| Jobs assíncronos (future+queueable+batch) | 250.000 ou 200 × nº de licenças, o que for maior |
| Batches na fila | 100 (5 ativos ao mesmo tempo) |
| E-mails para endereços externos | 5.000/dia |
| Tamanho do debug log | 20 MB por transação, 1 GB por org |

**Como ver o consumo em tempo de execução:**
```apex
System.debug('SOQL: ' + Limits.getQueries() + '/' + Limits.getLimitQueries());
System.debug('CPU: ' + Limits.getCpuTime() + '/' + Limits.getLimitCpuTime());
System.debug('Heap: ' + Limits.getHeapSize() + '/' + Limits.getLimitHeapSize());
System.debug('DML: ' + Limits.getDmlStatements() + '/' + Limits.getLimitDmlStatements());
```

> **O limite que mais mata em produção é o de CPU (10 s).** SOQL e DML são fáceis de
> contar e otimizar; tempo de CPU acumula silenciosamente por Flows, triggers de pacotes
> gerenciados, regras de validação e fórmulas — e você nem escreveu o código que consumiu.
> A explicação de *por que* esses limites existem está em
> [19-multitenancy-arquitetura.md](19-multitenancy-arquitetura.md) §5.

---

## 12. Tipos de metadado mais usados

| Tipo (API name) | O que é | Onde fica no projeto |
|---|---|---|
| `ApexClass` | classe Apex | `classes/X.cls` + `.cls-meta.xml` |
| `ApexTrigger` | trigger | `triggers/X.trigger` |
| `LightningComponentBundle` | LWC | `lwc/nome/` |
| `AuraDefinitionBundle` | componente Aura (legado) | `aura/nome/` |
| `CustomObject` | objeto + seus campos | `objects/Nome__c/` |
| `CustomField` | campo | `objects/X/fields/Y__c.field-meta.xml` |
| `ValidationRule` | regra de validação | `objects/X/validationRules/` |
| `Flow` | fluxo declarativo | `flows/Nome.flow-meta.xml` |
| `PermissionSet` | conjunto de permissões | `permissionsets/` |
| `Profile` | perfil (evite versionar — ver §14) | `profiles/` |
| `Layout` | layout de página | `layouts/` |
| `FlexiPage` | página Lightning | `flexipages/` |
| `CustomLabel` | texto traduzível | `labels/CustomLabels.labels-meta.xml` |
| `CustomMetadata` | registro de metadado customizado | `customMetadata/` |
| `NamedCredential` | credencial de integração | `namedCredentials/` |
| `RemoteSiteSetting` | domínio liberado para callout | `remoteSiteSettings/` |
| `StaticResource` | arquivo estático (JS, CSS, ZIP) | `staticresources/` |

Lista completa: `sf org list metadata-types -o devorg`.

---

## 13. Navegação no Setup — caminhos diretos por URL

Cole depois do domínio da sua org (`https://sua-org.lightning.force.com/`).
**Isto economiza minutos por dia.**

| Destino | Caminho |
|---|---|
| Home do Setup | `lightning/setup/SetupOneHome/home` |
| Object Manager | `lightning/setup/ObjectManager/home` |
| Classes Apex | `lightning/setup/ApexClasses/home` |
| Triggers Apex | `lightning/setup/ApexTriggers/home` |
| Jobs Apex (assíncrono) | `lightning/setup/AsyncApexJobs/home` |
| Debug Logs | `lightning/setup/ApexDebugLogs/home` |
| Flows | `lightning/setup/Flows/home` |
| Users | `lightning/setup/ManageUsers/home` |
| Profiles | `lightning/setup/EnhancedProfiles/home` |
| Permission Sets | `lightning/setup/PermSets/home` |
| Sharing Settings | `lightning/setup/SecuritySharing/home` |
| Deployment Status | `lightning/setup/DeployStatus/home` |
| Company Information (limites, licenças) | `lightning/setup/CompanyProfileInfo/home` |
| System Overview (uso vs. limites) | `lightning/setup/SystemOverview/home` |
| Um registro qualquer, por Id | `lightning/r/Account/001xx.../view` |

---

## 14. Atalhos e padrões que só quem usa há anos conhece

**Interface**

1. **Setup em nova aba:** clique com o botão do meio na engrenagem. Você raramente quer
   perder a tela em que estava.
2. **`Ctrl+Alt+F` (ou `Cmd+Opt+F`)** foca a caixa de busca do Setup de qualquer lugar.
3. Na Quick Find do Setup, digite **partes** do nome: `flo` acha *Flows*, *Flow Trigger
   Explorer*, *Process Automation*.
4. **Login as** (Setup → Users → *Login*) é a única forma honesta de testar permissão.
   Não confie em "no meu usuário funciona".
5. `?` em muitas telas Lightning abre a lista de atalhos de teclado.

**Desenvolvimento**

6. **Um trigger por objeto, sem lógica dentro.** Múltiplos triggers no mesmo objeto têm
   ordem de execução **indefinida** — não é "não recomendado", é indeterminismo real.
7. **Custom Metadata Types em vez de Custom Settings** para configuração. Metadados são
   deployáveis, versionáveis e visíveis em teste sem `SeeAllData`.
8. **Não versione `Profile`.** Perfis são arquivos gigantes que a org reescreve, geram
   conflito de merge insolúvel e sobrescrevem permissões alheias. Use `PermissionSet` e
   `PermissionSetGroup`. Ponha `**/profiles/**` no `.forceignore`.
9. **`Test.startTest()`/`stopTest()` reinicia os limites** — coloque só o código sob teste
   entre eles, e o setup fora. Também é o que força jobs assíncronos a rodarem.
10. **Cobertura ≠ qualidade.** Um teste sem `Assert` cobre 100% e não testa nada. A
    plataforma só exige a cobertura; a responsabilidade da asserção é sua.
11. **`sf project deploy validate` + `quick deploy`** transforma janela de release de horas
    em segundos (§3.1).
12. **Queueable > `@future`** em praticamente todo caso novo: aceita tipos complexos,
    devolve Job ID rastreável e encadeia.
13. **`Database.insert(lista, false)`** para importações onde falha parcial é aceitável —
    evita perder 9.999 registros bons por causa de 1 ruim.
14. **`Schema.getGlobalDescribe()` é caro.** Prefira `Type.forName()` ou
    `Schema.describeSObjects(new List<String>{'Account'})`.
15. **Nomeie campos pensando em 5 anos.** O *rótulo* pode mudar depois; o **nome de API
    não pode**, e ele aparece em todo código, relatório e integração.

**Dados e depuração**

16. `sf apex tail log -c` num terminal enquanto você clica na interface: você vê tudo
    acontecendo ao vivo. Melhor ferramenta de depuração da plataforma.
17. Na *Developer Console*, aba **Query Editor**, marque **Use Tooling API** para consultar
    `ApexClass`, `Flow`, `ApexCodeCoverage` — os metadados que a SOQL comum não vê.
18. Para achar quem está consumindo CPU: `Setup → Debug Logs`, nível `FINEST` em `ApexCode`,
    abra o log e use a aba **Timeline** / **Execution Overview** na Developer Console.

---

## 15. O que está obsoleto

| Obsoleto | Substituto | Desde | Ainda funciona? |
|---|---|---|---|
| `sfdx-cli` (pacote npm) | `@salesforce/cli`, comando `sf` | 2023 | Sem atualizações |
| Comandos `sfdx force:source:push/pull` | `sf project deploy start` / `retrieve start` | 2023 | Alias mantido |
| **Workflow Rules** | **Flow** | Migração forçada anunciada | Não se cria mais novos |
| **Process Builder** | **Flow** | idem | idem |
| `WITH SECURITY_ENFORCED` | `WITH USER_MODE` | **API 67.0 — não compila mais** | ❌ em v67+ |
| Aura Components | **LWC** | 2019 | Sim, mas não comece novo |
| Visualforce | LWC (ou VF só como container) | 2019 | Sim; ainda necessário para PDF e alguns overrides |
| Salesforce Classic (UI) | Lightning Experience | 2019 | Em retirada |
| `@future` para a maioria dos casos | `Queueable` | 2015 | Sim |
| API versions 31.0–40.0 | 45.0+ | Deprecação em Summer '27, **retirada em Summer '28** | Sim, até lá |
| `System.assertEquals` | `Assert.areEqual` | Winter '23 | Sim |
| Locker Service | **Lightning Web Security** | 2023 | Migrando |
| Custom Settings (para config) | Custom Metadata Types | ~2015 | Sim, mas evite para novo |
| Change Sets (para deploy) | Packages 2GP + CI, ou DevOps Center | — | Sim; opinião: use só como último recurso |

---

## Autoteste

1. Qual comando valida um deploy sem gravar nada, e qual comando executa a validação já feita?
2. Escreva a SOQL que retorna nome da conta e sobrenome de todos os contatos dela, em uma consulta.
3. Quais são os limites de SOQL, DML e tempo de CPU numa transação **síncrona**?
4. Quando você usaria SOSL em vez de SOQL? Dê dois casos.
5. Por que `WITH SECURITY_ENFORCED` não deve mais ser usado, e desde qual versão?
6. Qual a diferença entre `@future` e `Queueable`? Por que preferir o segundo?
7. Por que não se deve versionar `Profile` no Git, e o que usar no lugar?
8. O que `Test.startTest()` faz, além de delimitar o trecho testado?
9. Qual é a diferença entre `insert lista;` e `Database.insert(lista, false);`?
10. Onde você olharia primeiro para descobrir qual código está estourando o limite de CPU?
