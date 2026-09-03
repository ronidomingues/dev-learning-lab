# Glossário

`Atualizado: 11/08/2026`

Todo termo técnico usado neste material. Quando o termo é usado em inglês pelo mercado
brasileiro, ele aparece em inglês, com a tradução na definição.

---

## A

**AccessLevel** — Enum de Apex (`USER_MODE`, `SYSTEM_MODE`) que define se uma operação de
banco aplica as permissões do usuário. Ver [15-apex.md](15-apex.md) §9.

**Account** — Objeto padrão: a empresa (ou pessoa, com Person Accounts) com quem se faz
negócio. Prefixo de Id `001`.

**Account data skew** — Distorção causada por mais de ~10.000 registros filhos ligados à
mesma Account. Gera contenção de bloqueio. Ver [12](12-modelo-de-dados.md) §7.1.

**Agentforce** — Framework de agentes de IA autônomos da Salesforce, lançado em setembro de
2024. Executa ações no CRM usando Flow, Apex e dados da org.

**AppExchange** — Marketplace de aplicativos e componentes de terceiros, lançado em 2005.

**Apex** — Linguagem proprietária da Salesforce, com sintaxe de Java, executada nos
servidores da plataforma. Criada em 2006.

**Apex Managed Sharing** — Compartilhamento de registros criado por código, gravando na
tabela `X__Share`.

**Approval Process** — Processo formal de aprovação, com etapas, aprovadores e ações.
Trava o registro durante a aprovação.

**Assert** — Classe moderna de asserções em testes Apex (`Assert.areEqual`, `Assert.isTrue`).
Substitui `System.assertEquals`.

**AuraHandledException** — Exceção que envia mensagem legível ao LWC. Sem ela, o front-end
recebe `"Script-thrown exception"`.

**Aura Components** — Framework de componentes de 2014, antecessor do LWC. Legado.

**AutoNumber** — Tipo de campo com numeração sequencial automática. É texto, não reutiliza
números e pode ter buracos.

## B

**Batch Apex** — Processamento assíncrono em lotes, capaz de tratar até 50 milhões de
registros. Interface `Database.Batchable`.

**Big Object** — Objeto para bilhões de registros, com consulta restrita a um índice
composto imutável. Para histórico e auditoria.

**Bulk API 2.0** — API assíncrona para carga em massa via CSV, com limites separados dos
das chamadas de API comuns.

**Bulkification** — Escrever código que processa coleções em vez de registros isolados.
O conceito nº 1 de Apex. Ver [15](15-apex.md) §5.

**Bypass** — Interruptor estático em um handler de trigger para desligar a automação durante
migração de dados em massa.

## C

**Callout** — Chamada HTTP saindo do Salesforce para um sistema externo.

**Case** — Objeto padrão: chamado de suporte. Prefixo `500`.

**Change Data Capture (CDC)** — Publicação automática de eventos quando registros mudam.

**Change Set** — Mecanismo antigo de deploy entre orgs, manual e sem versionamento. Evitar.

**Circuit breaker** — Padrão que interrompe chamadas a um serviço que está falhando,
evitando desperdício e permitindo a recuperação do outro lado.

**cacheable=true** — Atributo de `@AuraEnabled` que permite `@wire` e cache no cliente.
Proíbe DML no método.

**Composite API** — API REST que agrupa até 25 sub-requisições numa chamada, com
encadeamento de referências.

**Connected App** — Registro que define como uma aplicação externa se autentica na org
(OAuth, escopos, políticas de IP).

**Contact** — Objeto padrão: pessoa dentro de uma conta. Prefixo `003`.

**Controlled by Parent** — OWD obrigatório em objetos com master-detail: a segurança é
herdada do pai.

**CRM** — *Customer Relationship Management*, gestão do relacionamento com o cliente.

**Custom Metadata Type** — Tipo de configuração deployável, versionável e visível em testes.
Preferível a Custom Settings.

**Custom Permission** — Permissão nomeada, atribuível por permission set, usável em fórmulas
(`$Permission.X`). Serve como válvula de escape em validation rules.

**Custom Setting** — Configuração armazenada como dado. Legado para novos casos; use Custom
Metadata Type.

## D

**Data 360 / Data Cloud** — Camada de unificação de dados: ingere de várias fontes, resolve
identidade e monta o perfil unificado do cliente.

**Database.Stateful** — Interface que preserva variáveis entre lotes de um Batch, ao custo
de serialização.

**Decimal** — Tipo numérico de precisão arbitrária. **Use para dinheiro**, nunca `Double`.

**Developer Edition (DE)** — Org gratuita e permanente para desenvolvimento e estudo.
~5 MB de dados, 15.000 chamadas de API por dia.

**Dev Hub** — Recurso ativado numa org que permite criar scratch orgs. Ativação irreversível.

**DevOps Center** — Ferramenta oficial e gratuita de pipeline de deploy, orientada a admins.

**DML** — *Data Manipulation Language*: `insert`, `update`, `upsert`, `delete`, `undelete`,
`merge`. Limite de 150 instruções por transação.

## E

**Einstein** — Marca das funcionalidades de IA da Salesforce, desde 2016.

**Einstein Trust Layer** — Camada de segurança da IA: mascaramento de dados sensíveis,
retenção zero pelos provedores de modelo, auditoria.

**empApi** — Módulo LWC para assinar Platform Events e CDC no cliente
(`lightning/empApi`).

**Enterprise Edition** — Edição mais comum em empresas médias e grandes. É o piso para
projetos com desenvolvimento. US$ 175/usuário/mês em 11/08/2026.

**Enterprise Patterns** — Conjunto de padrões (Domain, Selector, Service, Unit of Work)
popularizado por Andrew Fawcett para organizar código Apex.

**Experience Cloud** — Produto para portais de clientes, parceiros e comunidades.

**External Credential** — Onde o segredo de uma Named Credential é armazenado. Nunca entra
no Git.

**External Id** — Flag em um campo que habilita `upsert` por ele e cria um índice.
Peça central de integrações idempotentes.

**External Object** — Objeto cujos dados vivem fora do Salesforce, acessados em tempo real
via Salesforce Connect.

## F

**Field Audit Trail** — Componente do Shield: histórico de campo com retenção de até 10 anos.

**Field History Tracking** — Recurso nativo e gratuito: histórico de até 20 campos por
objeto, com retenção de 18 a 24 meses.

**Finalizer** — Interface de Queueable que executa mesmo se o job falhar. Análogo a `finally`.

**Flex Credits** — Unidade de consumo do Agentforce. US$ 500 por 100.000 créditos;
ação padrão = 20 créditos.

**Flow** — Ferramenta de automação declarativa atual. Substitui Workflow Rules e Process
Builder.

**FLS** — *Field-Level Security*: controle de leitura e edição por campo.

**Force.com** — Nome antigo da plataforma de desenvolvimento. Hoje: Salesforce Platform.

**Formula field** — Campo calculado na leitura, não armazenado. Não é indexado (salvo
exceções mediante solicitação).

## G

**Governor limits** — Limites de consumo por transação (SOQL, DML, CPU, heap). Mecanismo de
isolamento de performance no ambiente multi-inquilino. Ver [19](19-multitenancy-arquitetura.md).

**GraphQL API** — API de consulta declarativa. Em Summer '26, ganhou encadeamento de
referências em mutations.

## H

**Handler** — Classe que contém a lógica de um trigger. O trigger apenas a chama.

**Heroku** — PaaS adquirida em 2010. Válvula de escape para computação que não cabe em Apex.

**Hyperforce** — Rearquitetura da plataforma para rodar sobre nuvem pública, permitindo
escolher a região de residência dos dados.

## I

**Id** — Identificador de registro, de 15 (sensível a maiúsculas) ou 18 caracteres
(insensível). Os 3 primeiros indicam o tipo de objeto.

**Idempotência** — Propriedade de uma operação que, repetida, produz o mesmo resultado.
Requisito de toda integração correta.

**Implicit Sharing** — Regras de compartilhamento embutidas e não configuráveis, entre
Account e seus Contacts, Opportunities e Cases.

**inherited sharing** — Declaração que faz a classe herdar o modo de sharing do chamador.

**InvocableMethod** — Anotação que expõe um método Apex a Flow. Recebe e devolve listas.

## J

**Jest** — Framework de teste unitário de LWC, executado localmente, sem org.

**JWT Bearer Flow** — Fluxo OAuth com certificado, sem senha. O correto para CI/CD e
integração servidor a servidor.

**Junction object** — Objeto de junção com dois master-details, usado para modelar relações
muitos-para-muitos.

## L

**Lead** — Objeto padrão de topo de funil. Converte em Account + Contact + Opportunity.

**Lightning Data Service (LDS)** — Camada de acesso a registros no cliente, com cache
compartilhado, FLS e sharing aplicados sem Apex.

**Lightning Experience** — Interface atual, lançada em 2015. Substitui o Salesforce Classic.

**Lightning Web Components (LWC)** — Framework de componentes baseado em Web Components
padrão, lançado em 2019. Código aberto sob **licença MIT**.

**Lightning Web Security (LWS)** — Substituto do Locker Service; isola componentes por
virtualização de namespace.

**LimitException** — Exceção lançada ao estourar um governor limit. Não deve ser capturada
para "continuar mesmo assim".

**Locker Service** — Mecanismo antigo de isolamento no cliente. Substituído por LWS.

**Lookup** — Relacionamento fraco: o filho existe sem o pai, tem segurança própria, não
permite rollup.

## M

**Master-Detail** — Relacionamento forte: o filho não existe sem o pai, herda segurança,
é apagado em cascata e permite rollup. Causa contenção de bloqueio.

**Metadata API** — API de deploy e recuperação de configuração.

**Metadata-driven** — Arquitetura em que a estrutura de cada inquilino é descrita em
metadados interpretados em runtime. A ideia central da plataforma.

**MuleSoft** — Plataforma de integração (ESB/API) adquirida em 2018.

**Multi-inquilino (multitenant)** — Arquitetura em que muitos clientes compartilham a mesma
infraestrutura, isolados logicamente.

## N

**Named Credential** — Metadado que guarda endpoint e autenticação de um sistema externo.
Substitui credencial em código.

**Named Query API** — API que expõe consultas SOQL nomeadas como ações escaláveis.
Chegou a GA em Summer '26.

## O

**Opportunity** — Objeto padrão: negócio em andamento, com valor e data de fechamento.
Prefixo `006`.

**Org** — Instância de Salesforce: dados, metadados, usuários. Unidade de licenciamento,
segurança e limites.

**Ownership skew** — Distorção causada por mais de ~10.000 registros do mesmo objeto
pertencendo ao mesmo usuário. Ver [12](12-modelo-de-dados.md) §7.2.

**OWD** — *Organization-Wide Defaults*: o nível mínimo de acesso a registros que um usuário
tem sobre o que não é dele.

## P

**Permission Set** — Conjunto de permissões adicionais atribuível a vários usuários.
Só soma, nunca subtrai.

**Permission Set Group** — Agrupamento de permission sets, com possibilidade de *muting*.

**Person Account** — Recurso que funde Account e Contact num registro, para B2C.
Ativação irreversível.

**Pivot table** — Tabela auxiliar da arquitetura interna que replica valores com tipagem
correta para permitir indexação. Ver [19](19-multitenancy-arquitetura.md) §4.

**Platform Event** — Evento publicado no barramento da plataforma, com esquema definido por
você. Retenção de 72 horas para replay.

**Pod / instância** — Conjunto autônomo de infraestrutura que hospeda muitas orgs.

**Process Builder** — Ferramenta de automação de 2015. Descontinuada; migre para Flow.

**Profile** — Perfil: exatamente um por usuário; define permissões base e padrões. Evite
versionar em Git.

## Q

**Query optimizer** — Componente que decide o plano de execução de uma consulta, usando
estatísticas **por inquilino**.

**Queueable** — Interface de processamento assíncrono moderna: aceita objetos, encadeia,
devolve Job Id. Preferível a `@future`.

**QueryLocator** — Cursor usado no `start` de um Batch, capaz de percorrer até 50 milhões
de registros.

## R

**Record Type** — Mecanismo para ter layouts, picklists e processos diferentes no mesmo
objeto.

**refreshApex** — Função de LWC que invalida o cache de um `@wire` e recarrega os dados.

**Release Update** — Mudança de comportamento anunciada com prazo, que a plataforma
eventualmente impõe.

**Roll-Up Summary** — Campo que agrega valores dos filhos. Só com master-detail.

**RowCause** — Motivo de um compartilhamento na tabela `__Share`. Um RowCause customizado
(*Apex Sharing Reason*) preserva shares criados por código.

## S

**Sandbox** — Cópia da org de produção para desenvolvimento e teste. Tipos: Developer,
Developer Pro, Partial Copy, Full Copy.

**Scratch org** — Org efêmera (1 a 30 dias) criada a partir de um arquivo de definição.
Base do modelo de desenvolvimento moderno.

**Selector** — Camada de padrão em que se concentra toda a SOQL de um domínio.

**Service (camada)** — Camada onde vive a regra de negócio, reutilizável por trigger, LWC,
API e batch.

**sf** — Executável atual da Salesforce CLI (pacote npm `@salesforce/cli`). Substitui `sfdx`.

**sfdx** — Executável antigo (pacote `sfdx-cli`), descontinuado.

**Shadow DOM** — Mecanismo padrão da web que isola estrutura e estilo de um componente.
Usado por LWC.

**Sharing rule** — Regra que abre acesso a registros por dono ou por critério de campo.

**Shield** — Add-on pago: Platform Encryption, Event Monitoring e Field Audit Trail.

**Skinny Table** — Tabela desnormalizada criada pelo Suporte para acelerar relatórios.

**SLDS** — *Salesforce Lightning Design System*: sistema de design, código aberto.

**SOQL** — *Salesforce Object Query Language*. Parece SQL, mas sem JOIN livre, sem UNION,
sem `SELECT *`.

**SOSL** — *Salesforce Object Search Language*: busca textual em vários objetos, usando
índice de busca.

**Superbadge** — Projeto prático longo do Trailhead, avaliado automaticamente numa org.
O que realmente conta no currículo.

## T

**Tooling API** — API para metadados de desenvolvimento: classes, cobertura, logs, Flows.

**Trailhead** — Plataforma oficial de ensino, gratuita, lançada em 2014.

**Transactional outbox** — Padrão em que a intenção de notificar é gravada na mesma
transação do dado, e um processo separado notifica com retentativa.

**Trigger** — Código Apex executado em resposta a eventos de banco. Um por objeto, sem
lógica dentro.

**Trigger Order** — Prioridade de execução (1 a 2.000) de Flows record-triggered. Sem ela,
a ordem é indefinida.

## U

**UDD** — *Universal Data Dictionary*: o dicionário de metadados que descreve a estrutura de
cada inquilino.

**UNABLE_TO_LOCK_ROW** — Erro de contenção de bloqueio, tipicamente causado por data skew.

**Unlocked Package** — Pacote 2GP editável pelo cliente. Forma moderna de modularizar a
própria org.

**Upsert** — Operação que insere ou atualiza conforme uma chave externa. Base da
idempotência.

**User mode** — Modo de execução que aplica FLS, permissões de objeto e sharing.
**Padrão em Apex a partir da API 67.0.**

## V

**Validation Rule** — Regra que rejeita a gravação quando uma fórmula avalia como
verdadeira. Roda depois dos triggers `before`.

**Visualforce** — Framework de páginas de 2007. Legado, mas ainda insubstituível para
geração de PDF.

## W

**WITH SECURITY_ENFORCED** — Cláusula SOQL que aplicava FLS. **Removida na API 67.0** —
classes em v67+ que a usem não compilam. Substituto: `WITH USER_MODE`.

**WITH SYSTEM_MODE** — Cláusula que executa a consulta ignorando FLS e permissões.
Toda exceção deve ser comentada.

**WITH USER_MODE** — Cláusula que executa a consulta aplicando FLS e permissões.
Padrão implícito na API 67.0+.

**with sharing / without sharing** — Declarações de classe que controlam se as regras de
compartilhamento **de registro** são respeitadas. Não controlam FLS.

**Workflow Rule** — Ferramenta de automação de 2004. Descontinuada; migre para Flow.

## Z

**Zero-copy** — Capacidade da Data 360 de consultar dados onde eles estão (Snowflake,
BigQuery, Databricks) sem copiá-los.

---

## Símbolos e convenções de nomenclatura

| Símbolo | Significado |
|---|---|
| `__c` | objeto ou campo **customizado** |
| `__r` | **relacionamento** (para o pai ou para os filhos) |
| `__e` | **Platform Event** |
| `__mdt` | **Custom Metadata Type** |
| `__b` | **Big Object** |
| `__x` | **External Object** |
| `__Share` | tabela de compartilhamento de um objeto |
| `__History` | tabela de histórico de campos |
| `__Feed` | feed do Chatter de um objeto |
| `ns__` | prefixo de **namespace** de pacote gerenciado |
| `001`, `003`, `006`, `500`, `00Q`, `005`, `00D` | prefixos de Id: Account, Contact, Opportunity, Case, Lead, User, Organization |
