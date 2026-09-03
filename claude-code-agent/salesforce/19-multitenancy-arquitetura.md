# 19 · A arquitetura multi-inquilino por dentro

`Nível: avançado → pesquisa` · `Atualizado: 11/08/2026`

Este é o arquivo que explica **por que a plataforma é como é**. Tudo que irrita um
desenvolvedor no Salesforce — os limites, a falta de índices, a ausência de JOIN, a
proibição de callout após DML — decorre do que está aqui.

A fonte primária é o whitepaper *The Force.com Multitenant Architecture* (Salesforce, 2008),
ainda a descrição pública mais detalhada do mecanismo. Detalhes evoluíram desde então
(Hyperforce, Data 360, novos motores de busca), mas os princípios permanecem.

---

## 1. O problema fundamental

Como fazer **centenas de milhares de empresas** compartilharem a mesma infraestrutura, cada
uma com seu próprio esquema de dados, sem que:

- uma veja os dados da outra;
- uma degrade a performance da outra;
- cada mudança de esquema exija manutenção de banco;
- o custo por cliente cresça linearmente?

**A resposta convencional seria** um banco de dados por cliente. Ela resolve isolamento e
esquema, mas destrói a economia: 300 mil bancos significam 300 mil unidades de backup,
patch, monitoramento, tuning e capacidade ociosa. É exatamente o modelo que a Salesforce
existiu para eliminar.

**A resposta da Salesforce:** um conjunto pequeno de **tabelas físicas genéricas**
compartilhadas por todos, com a estrutura de cada cliente descrita em **metadados**.

---

## 2. As três camadas: dados, metadados, kernel

```text
┌─────────────────────────────────────────────────────────────┐
│  KERNEL — o motor compilado                                 │
│  compilador Apex · query optimizer · engine de sharing      │
│  UM SÓ, para todos os inquilinos                            │
└─────────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────────┐
│  METADADOS — a estrutura de CADA inquilino                  │
│  UDD (Universal Data Dictionary): objetos, campos, tipos,   │
│  relacionamentos, regras, layouts, código                   │
└─────────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────────┐
│  DADOS — as tabelas físicas compartilhadas                  │
│  MT_data · MT_indexes · MT_unique_indexes · MT_relationships│
└─────────────────────────────────────────────────────────────┘
```

**A ideia central em uma frase:** o kernel não sabe nada sobre o negócio do cliente; ele
lê o metadado em tempo de execução e monta a operação apropriada.

---

## 3. A tabela de dados universal

De forma simplificada, a tabela que guarda todos os registros de todos os objetos
customizados de todos os clientes tem, conceitualmente, esta forma:

| org_id | obj_id | guid | value0 | value1 | value2 | … | value500 |
|---|---|---|---|---|---|---|---|
| 00D...A | Equipamento__c | a01...1 | 'SN-000101' | 'Operacional' | '2026-07-01' | … | |
| 00D...A | Equipamento__c | a01...2 | 'SN-000102' | 'Em manutenção' | | … | |
| 00D...B | Pedido__c | a02...9 | '12345' | '1500.00' | 'Aprovado' | … | |

- **`org_id`** — a que inquilino a linha pertence. **Todo acesso é filtrado por ele**.
- **`obj_id`** — a que objeto lógico.
- **`guid`** — o Id do registro.
- **`value0…valueN`** — colunas genéricas, tipicamente de texto de tamanho variável.

**O metadado é que diz** que, para o objeto `Equipamento__c` da org A, `value0` é
`Numero_Serie__c` do tipo Text(50) e `value1` é `Status__c`, uma picklist restrita.

**Consequências diretas, e agora tudo faz sentido:**

| Fenômeno | Explicação |
|---|---|
| Criar um campo é instantâneo | é um `INSERT` no metadado, não um `ALTER TABLE` |
| Não há `ALTER TABLE`, logo não há downtime | a estrutura física nunca muda |
| Há limite de campos por objeto (800) | há um número finito de colunas `valueN` |
| Tipos de dado são convertidos | os valores são guardados como texto e convertidos na leitura |
| Sua query nunca roda "pura" | ela é reescrita para incluir `org_id` e mapear campos → colunas |
| Você não pode ver o plano de execução | o SQL executado não é o seu |

---

## 4. Índices: `MT_indexes` e as pivot tables

Um índice numa coluna `value0` compartilhada por milhares de objetos de milhares de
clientes seria inútil — os valores são heterogêneos.

A solução são as **pivot tables**: tabelas separadas que replicam, com **tipagem correta**,
os valores dos campos que precisam ser indexados.

```text
MT_indexes
┌────────┬────────────┬──────────┬─────────────┬──────────────┬──────────┐
│ org_id │ obj_id     │ guid     │ string_value│ number_value │ date_value│
├────────┼────────────┼──────────┼─────────────┼──────────────┼──────────┤
│ 00D..A │ Equipam..  │ a01...1  │ 'SN-000101' │              │           │
│ 00D..A │ Equipam..  │ a01...1  │             │              │ 2026-07-01│
└────────┴────────────┴──────────┴─────────────┴──────────────┴──────────┘
```

Existem também `MT_unique_indexes` (para campos `unique` e External Id) e
`MT_relationships` (para os relacionamentos declarados).

**Isso explica de uma vez três "limitações" da plataforma:**

1. **Por que apenas alguns campos são indexados por padrão** (Id, Name, OwnerId,
   CreatedDate, LastModifiedDate, RecordTypeId, campos de relacionamento, External Id,
   campos `unique`): manter a pivot table custa espaço e escrita. Indexar tudo seria
   inviável.
2. **Por que índice customizado passa pelo Suporte:** ele adiciona linhas a uma tabela
   física compartilhada. O custo é distribuído; a decisão não pode ser unilateral.
3. **Por que campos fórmula não são indexados:** o valor não está armazenado — é calculado
   na leitura. Não há o que indexar. (A Salesforce pode indexar fórmulas *determinísticas*
   mediante solicitação, justamente porque essas podem ser materializadas.)

---

## 5. O query optimizer multi-inquilino

Um otimizador de banco comum usa **estatísticas globais** da tabela. Aqui isso não funciona:
a tabela contém dados de milhares de inquilinos com distribuições completamente diferentes.

A Salesforce mantém **estatísticas por inquilino e por objeto**: quantas linhas a org A tem
em `Equipamento__c`, qual a cardinalidade de `Status__c` nessa org, e assim por diante.

**O algoritmo de decisão, em essência:**

```text
para cada filtro na consulta:
    se o campo é indexado:
        estime quantas linhas o filtro retorna, usando as estatísticas DA ORG
        se estimativa < limiar de seletividade:
            marque o índice como candidato
escolha o índice mais seletivo entre os candidatos
se nenhum índice é seletivo:
    → full table scan dentro da fatia do inquilino
    se a tabela do inquilino é grande (> ~200 mil linhas):
        → recuse a consulta com "Non-selective query against large object type"
```

**Os limiares publicados** (aproximados, e a Salesforce os ajusta):

| Tipo de índice | Seletivo se retornar |
|---|---|
| Índice padrão | < 30% das primeiras 1 M linhas, e < 15% do excedente; teto de 1 M linhas |
| Índice customizado | < 10% das linhas; teto de 333.333 linhas |

**Por que a plataforma *recusa* a consulta em vez de apenas demorar:** porque uma varredura
completa numa tabela compartilhada consome I/O do pool que atende outros inquilinos.
Recusar a consulta é uma forma de **isolamento de performance**: preferir falhar rápido para
um a degradar todos. Este é o princípio de projeto mais importante do sistema inteiro.

---

## 6. Os governor limits, explicados de verdade

Agora podemos responder à pergunta que todo desenvolvedor faz no primeiro mês.

**Um app tradicional roda em servidor dedicado:** se o seu código consome 100% da CPU por
30 segundos, quem sofre é você. **Aqui, um único servidor de aplicação atende dezenas ou
centenas de inquilinos simultaneamente.**

```text
Sem limites:
  Inquilino A roda um laço com 10 milhões de iterações
     → 100% da CPU do servidor por 2 minutos
     → Inquilinos B, C, D... param
     → chamados de suporte, SLA violado, reputação perdida

Com limites:
  Inquilino A atinge 10.000 ms de CPU
     → LimitException, transação abortada, recursos liberados
     → Inquilinos B, C, D... não percebem nada
```

**Os limites são um mecanismo de *fairness scheduling* implementado no nível da linguagem.**
Em vez de um escalonador preemptivo (que exigiria interromper e retomar execução, algo
inviável para uma transação de banco), a plataforma escolheu **contadores rígidos com
aborto**. É mais simples, mais previsível e mais barato de implementar — ao custo de o
desenvolvedor precisar programar dentro de um orçamento.

**Por que os limites assíncronos são mais generosos** (200 SOQL, 60 s de CPU, 12 MB de heap):
porque uma transação assíncrona não tem um usuário esperando na tela. Ela pode ser
enfileirada, adiada e executada quando houver capacidade. O sistema pode arbitrar quando
ela roda; numa transação síncrona, não pode.

**Por que não há callout após DML:** um callout pode levar 120 s, e a transação de banco
estaria aberta segurando bloqueios em **tabelas compartilhadas**. Bloqueios longos em
tabela compartilhada degradam todos os inquilinos daquele pod. É o mesmo princípio de
isolamento, aplicado a bloqueios em vez de CPU.

---

## 7. Instâncias, pods e Hyperforce

**Pod / instância:** um conjunto completo e autônomo de infraestrutura (servidores de
aplicação, banco, busca, cache) que hospeda **muitos inquilinos**. Historicamente com nomes
como `NA45`, `EU17`, `AP4`.

```text
Pod NA45
├── Servidores de aplicação (Apex, UI, API)
├── Banco de dados
├── Índice de busca (SOSL)
├── Cache
└── ~ milhares de orgs
```

Cada pod tem sua **janela de manutenção** e sua **data de release** publicadas em
https://status.salesforce.com — é lá que se descobre por que "o Salesforce está lento hoje".

**Hyperforce** (2020→) é a rearquitetura da plataforma para rodar sobre nuvem pública
(AWS, e outras conforme a região), em vez de datacenters próprios. Motivações declaradas:

| Motivação | Efeito prático |
|---|---|
| **Residência de dados** | atender exigências legais (LGPD, GDPR, regulações locais) escolhendo a região |
| **Elasticidade** | escalar por demanda em vez de por compra de hardware |
| **Velocidade de expansão** | abrir uma região nova em meses, não anos |
| Padronização | uma arquitetura em vez de várias gerações de datacenter |

**O que Hyperforce *não* mudou:** o modelo multi-inquilino, os governor limits, o modelo de
metadados. Sua org continua compartilhando infraestrutura com outras; ela apenas roda em
outra infraestrutura física.

> **Fato vs. opinião:** que Hyperforce existe e que a motivação declarada é essa é fato
> público. Minha opinião é que a motivação econômica — trocar CapEx de datacenter por OpEx
> de nuvem, num negócio que precisa de margem crescente — pesou tanto quanto a técnica.

---

## 8. Isolamento — as camadas de garantia

| Dimensão | Mecanismo | Falha significaria |
|---|---|---|
| **Dados** | `org_id` em toda linha; toda query reescrita para filtrar | vazamento entre empresas |
| **Performance (CPU)** | governor limits com aborto | vizinho barulhento |
| **Performance (I/O)** | recusa de query não seletiva | idem |
| **Bloqueios** | proibição de callout com trabalho pendente; timeouts | contenção global |
| **Memória** | limite de heap | OOM derrubando o servidor |
| **Código** | Apex compilado e verificado; sem acesso a SO, rede ou disco | escape de sandbox |
| **Cliente (browser)** | Lightning Web Security, Shadow DOM | um pacote quebrando outro |
| **Armazenamento** | cotas por org | um inquilino consumindo o disco |

**O `org_id` merece destaque:** ele não é uma convenção que os desenvolvedores da Salesforce
lembram de aplicar. Ele é injetado pelo kernel em **toda** operação, e nenhum caminho de
código do cliente consegue emitir SQL diretamente. É por isso que Apex não tem acesso a SQL
bruto — não é para dificultar sua vida, é porque **SQL bruto quebraria o isolamento**.

---

## 9. O que a arquitetura *impede* — e o preço disso

| Você não pode | Consequência prática | Alternativa |
|---|---|---|
| Escrever SQL | sem JOIN livre, sem CTE, sem window function | SOQL + processamento em Apex, ou Data 360 |
| Criar índice | consultas lentas ficam lentas | pedir ao Suporte; modelar melhor; Skinny Table |
| Ver o plano de execução | otimização é por tentativa | *Query Plan* na Developer Console (aproximação) |
| Controlar transação com granularidade | sem transação distribuída, sem isolamento configurável | Savepoint; padrão outbox |
| Rodar código longo | sem processo de horas | Batch em lotes |
| Usar bibliotecas externas em Apex | sem `npm`/`maven` | copiar código; pacote gerenciado; Heroku |
| Escolher quando atualizar | 3 releases/ano impostos | testar no preview |
| Acessar disco, rede crua, threads | sem I/O de arquivo, sem socket | callout HTTP mediado; processar fora |

**O trade-off, declarado sem eufemismo:** você troca **controle** por **não ter que operar
nada**. Não há DBA, não há patch de segurança, não há upgrade de servidor, não há
dimensionamento de capacidade, não há plano de disaster recovery para escrever. Para a
maioria das empresas, essa troca é excelente. Para sistemas de altíssimo volume, baixa
latência ou computação pesada, é péssima. Saber de qual lado o seu problema está é a
decisão de arquitetura mais importante ao adotar Salesforce.

---

## 10. Os cinco porquês, aplicados ao fundo do poço

**Pergunta:** por que meu código Apex não pode rodar por mais de 10 segundos de CPU?

**1.** Porque o servidor de aplicação é compartilhado por muitos inquilinos.

**2.** Por que é compartilhado? Porque um servidor por inquilino tornaria o custo por cliente
alto demais para o modelo de assinatura funcionar — e o modelo de assinatura acessível é a
razão de a empresa existir.

**3.** Por que não usar um escalonador preemptivo, que dividiria a CPU de forma justa sem
abortar ninguém? Porque preempção de uma transação de banco em andamento é extremamente
difícil: seria preciso salvar e restaurar estado de execução, bloqueios e cursores. Contadores
com aborto são ordens de magnitude mais simples e previsíveis.

**4.** Por que 10 segundos, especificamente? Aqui a resposta honesta é: **não sei**, e não
conheço fonte pública que explique o número. É quase certamente um valor empírico, calibrado
para acomodar a grande maioria das transações legítimas sem permitir abuso. É uma
**convenção operacional**, não uma constante física — e ela já mudou ao longo dos anos.

**5.** Por que a plataforma não simplesmente cobra mais de quem consome mais, em vez de
proibir? Porque cobrança não resolve o problema em tempo real: no instante em que o
inquilino A consome a CPU, o inquilino B já está esperando. Preço é um mecanismo de
alocação lento demais para um problema de milissegundos.

*(Paradas legítimas alcançadas: trade-off econômico explícito, limite prático de engenharia,
e uma convenção arbitrária admitida como tal.)*

---

## 11. Comparação com outras arquiteturas multi-inquilino

| Modelo | Isolamento | Custo/cliente | Flexibilidade de esquema | Exemplo |
|---|---|---|---|---|
| **Banco por inquilino** | máximo | alto | total | muitos SaaS B2B corporativos |
| **Schema por inquilino** | alto | médio | total | SaaS de porte médio |
| **Linha por inquilino** (`tenant_id` em tabelas normais) | médio | baixo | **nenhuma** — esquema comum | a maioria dos SaaS modernos |
| **Metadata-driven** (Salesforce) | médio-alto | **muito baixo** | **por inquilino, em runtime** | Salesforce, ServiceNow |

A quarta linha é rara porque é **difícil de construir**. Ela exige um kernel próprio, um
otimizador próprio, um dicionário de dados próprio e uma linguagem própria. A Salesforce e
a ServiceNow investiram uma década nisso. É a maior barreira de entrada do setor — e explica
por que concorrentes com mais dinheiro não replicaram o modelo, apenas o produto.

---

## Autoteste

1. Descreva a tabela de dados universal. Por que criar um campo é instantâneo?
2. O que são as pivot tables (`MT_indexes`) e que três limitações da plataforma elas explicam?
3. Como o query optimizer decide usar um índice? Por que ele usa estatísticas por inquilino?
4. Por que a plataforma **recusa** uma consulta não seletiva em vez de apenas demorar?
5. Explique os governor limits como mecanismo de escalonamento justo. Por que aborto e não preempção?
6. Por que os limites assíncronos são mais generosos que os síncronos?
7. Por que não se pode fazer callout com trabalho não commitado? Ligue à ideia de isolamento.
8. O que Hyperforce mudou e o que ele **não** mudou?
9. Compare os quatro modelos de multi-inquilino. Por que o modelo da Salesforce é raro?
10. Qual é o trade-off central da plataforma, dito sem eufemismo?

---

### Fontes consultadas (11/08/2026)

- Salesforce — *WHITEPAPER: The Force.com Multitenant Architecture* — https://www.developerforce.com/media/ForcedotcomBookLibrary/Force.com_Multitenancy_WP_101508.pdf
- Salesforce Developers — *Multi Tenant Architecture* (wiki) — https://developer.salesforce.com/ja/wiki/multi_tenant_architecture
- O'Reilly — *The Force.com Multitenant Architecture* (livro, 2008) — https://www.oreilly.com/library/view/the-force-com-multitenant/30000LTI00089/
- Salesforce Trust — status de instâncias e janelas de manutenção — https://status.salesforce.com
