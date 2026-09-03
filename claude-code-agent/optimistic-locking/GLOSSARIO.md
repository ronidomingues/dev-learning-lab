# Glossário

`Todos os termos técnicos usados neste material` · `Atualizado em: 14/08/2026`

Termos em inglês aparecem quando é assim que o campo os usa. A tradução vem primeiro quando
existe uma consagrada em português.

---

## A

**ABA (problema)** — Situação em que um valor muda de A para B e volta para A entre a leitura
e a escrita, fazendo uma guarda por igualdade aceitar uma escrita que deveria recusar. Ver
[`13 §4`](13-tokens-de-versao.md#4-o-problema-aba).

**Abort** — Encerramento de uma transação com desfazimento de todos os seus efeitos. Sinônimo
prático de *rollback* no contexto de conflito.

**ACID** — Atomicidade, Consistência, Isolamento e Durabilidade: as quatro propriedades
clássicas de uma transação.

**Agregado** — Conjunto de objetos tratado como uma unidade de consistência (termo do
Domain-Driven Design). A unidade de versionamento deveria coincidir com ele.

**Anomalia** — Comportamento observável numa execução concorrente que não ocorreria em nenhuma
execução sequencial. Ver leitura suja, leitura não repetível, fantasma, lost update, write skew.

**Atomicidade** — Propriedade de "tudo ou nada": ou todas as operações de uma unidade
acontecem, ou nenhuma.

**Auditoria (trilha de)** — Registro histórico das escritas, usado aqui para provar que
nenhuma se perdeu.

## B

**Backoff** — Atraso crescente entre tentativas. Ver **recuo exponencial**.

**Backward validation** — *Validação para trás*: comparar o próprio conjunto de leitura com as
escritas de transações que confirmaram depois do seu início. É o que a guarda
`WHERE version = ?` faz. Ver [`60 §2.1`](60-teoria-avancada.md#21-validação-para-trás-backward-validation).

**Bloat** — Espaço ocupado por versões mortas de linhas num banco MVCC, recolhido pelo `VACUUM`.

## C

**CALM** (*Consistency As Logical Monotonicity*) — Resultado teórico segundo o qual um programa
distribuído admite implementação sem coordenação se e somente se for monotônico. Explica por
que CRDTs funcionam e por que não garantem invariantes globais.

**CAP (teorema)** — Sob partição de rede, escolhe-se entre consistência e disponibilidade.

**CAS** (*compare-and-swap*) — Instrução atômica que compara um valor e o substitui se ele for
o esperado. É o mesmo mecanismo do `UPDATE ... WHERE version = ?`, na escala do processador.

**Check-and-set** — Nome do mecanismo de escrita condicional no Consul e em outros KV.

**Concorrência** — Sobreposição temporal na execução de duas ou mais operações. Não implica
paralelismo.

**Conflito** — Duas operações concorrentes sobre o mesmo dado, ao menos uma delas de escrita.

**Contenção** — Intensidade do conflito: quantas operações disputam o mesmo dado por unidade
de tempo. Distinta de **carga**.

**CRDT** (*Conflict-free Replicated Data Type*) — Estrutura de dados cujas operações são
comutativas, associativas e idempotentes, de modo que réplicas convergem sem detecção de
conflito. Garante convergência, não invariante global.

**Cópia privada** — Espaço onde a transação otimista acumula alterações antes de publicá-las.

## D

**Deadlock** (*abraço mortal*) — Duas ou mais transações esperando, cada uma, por um recurso
que a outra detém. Modo de falha típico do bloqueio pessimista.

**Delta atômico** — Atualização relativa (`SET x = x - 1`) executada num único comando, com a
regra de negócio na cláusula `WHERE`. Alternativa correta ao versionamento para operações
comutativas.

**Detecção** — Perceber que a guarda falhou. Na prática: o número de linhas afetadas ser zero.

**Dirty read** — Ver **leitura suja**.

**Dirty write** — Ver **escrita suja**.

**Distância de versão** — `versao_atual − versao_enviada` no momento do conflito. Indica
quantas escritas ocorreram na janela; métrica de diagnóstico de linha quente.

## E

**Efeito manada** (*thundering herd*) — Muitos agentes retentando no mesmo instante,
recriando o conflito. Evitado com *jitter*.

**Escalonamento** (*schedule*) — Ordenação total das operações de um conjunto de transações que
preserva a ordem interna de cada uma.

**Escrita cega** (*blind write*) — Escrever um item sem tê-lo lido antes.

**Escrita condicional** — Escrita executada apenas se uma condição sobre o estado atual for
verdadeira. Nome usado no DynamoDB, S3 e outros.

**Escrita suja** (*dirty write*) — Sobrescrever um valor ainda não confirmado por outra
transação.

**ETag** — Cabeçalho HTTP que carrega um identificador opaco da versão atual de um recurso.
Ver [`17`](17-http-e-apis.md).

**ETag forte / fraco** — Forte compara byte a byte (`"7"`); fraco compara equivalência
semântica (`W/"7"`). **`If-Match` exige comparação forte.**

## F

**Fantasma** (*phantom read*) — Consulta por faixa que retorna linhas diferentes ao ser
repetida na mesma transação.

**Fencing token** — Número estritamente crescente entregue a cada concessão de lock, verificado
**pelo recurso**, que recusa escritas com token menor que o último aceito. Sem ele, um lease
não garante exclusão mútua. Ver [`18 §4`](18-sistemas-distribuidos.md#4-fencing-tokens-por-que-o-lease-sozinho-não-basta).

**Forward validation** — *Validação para a frente*: comparar as próprias escritas com as
leituras de transações ainda em execução. Permite escolher a vítima.

## G

**Grafo de precedência** — Grafo com um nó por transação e uma aresta `Tᵢ → Tⱼ` quando uma
operação de `Tᵢ` conflita com e precede uma de `Tⱼ`. Aciclicidade equivale a
serializabilidade por conflito.

**Granularidade** — Nível em que a versão é mantida: campo, linha, agregado ou documento.

**Guarda** — A condição que compara o token esperado com o atual (`AND version = ?`).

## I

**Idempotência** — Propriedade de uma operação cujo efeito de executar duas vezes é igual ao de
executar uma. Pré-requisito da retentativa segura.

**Chave de idempotência** — Identificador gerado pelo cliente, único por **intenção**, que
permite ao servidor reconhecer e não reexecutar um pedido repetido.

**If-Match** — Cabeçalho HTTP de pré-condição: execute somente se o `ETag` do recurso for um
dos listados. É o optimistic locking do protocolo.

**If-None-Match** — Pré-condição inversa; usada para cache (`GET`) e para criação exclusiva
(`If-None-Match: *` em `PUT`).

**Isolamento** — Grau em que uma transação é protegida dos efeitos de outras em andamento.

**Instantâneo** (*snapshot*) — Visão consistente do banco num ponto do tempo, usada por MVCC.

## J

**Janela de vulnerabilidade** — Intervalo entre a leitura e a escrita de uma operação LMW.
Quanto maior, maior a chance de conflito.

**Jitter** — Componente aleatório no atraso de retentativa. *Full jitter*:
`aleatorio(0, min(teto, base·2^i))`.

## L

**Lease** — Lock com prazo de validade, liberado automaticamente na expiração. Requer relógio
único e, para exclusão mútua real, um fencing token.

**Leitura não repetível** (*non-repeatable read*) — Ler o mesmo item duas vezes na mesma
transação e obter valores diferentes.

**Leitura suja** (*dirty read*) — Ler um valor escrito por uma transação ainda não confirmada.

**Linha quente** (*hot row*) — Linha com contenção muito acima da média.

**LMW** (leitura-modificação-escrita; em inglês *read-modify-write*, RMW) — A tripla
`ler → computar → gravar`, unidade de análise deste assunto.

**Lock** — Mecanismo que impede o acesso concorrente a um recurso.

**Lock consultivo** (*advisory lock*) — Lock nomeado pela aplicação, sem relação com linhas
(`pg_advisory_lock`). Usado para exclusão mútua de processos.

**Lock otimista / pessimista** — Ver **optimistic locking** e **pessimistic locking**.

**Lost update** (*atualização perdida*) — Duas operações LMW se entrelaçam e uma sobrescreve o
efeito da outra **sem gerar erro**. O problema central deste material.

**LWT** (*lightweight transaction*) — Escrita condicional no Cassandra, implementada com Paxos.

**LWW** (*last-write-wins*) — Política de resolução em que vence o valor com o maior timestamp.
Converge sempre e descarta dados em silêncio.

## M

**Merge de três vias** — Reconciliação usando base (o que li), meu (o que quero) e deles (o que
está lá). Conflito real só quando o mesmo campo mudou dos dois lados para valores diferentes.

**Monotônico** — Propriedade de uma computação cujo resultado não é invalidado por dados que
cheguem depois. Ver **CALM**.

**MVCC** (*multiversion concurrency control*) — Manter múltiplas versões de cada linha para que
leitores não bloqueiem escritores.

## O

**OCC** (*optimistic concurrency control*) — O termo acadêmico para optimistic locking.

**Optimistic locking** — Estratégia que não impede o acesso concorrente e **detecta**, no
momento da escrita, se o estado lido ainda vale. O nome é impreciso: não há lock mantido entre
leitura e escrita.

**Outbox (padrão)** — Gravar a intenção de um efeito externo na mesma transação do dado, e
deixar um worker separado entregá-lo. Torna seguro retentar.

## P

**Pessimistic locking** — Estratégia que **impede** o acesso concorrente adquirindo um lock
antes da leitura e mantendo-o até o commit.

**Predicate lock** — Lock sobre um predicado (uma faixa de valores) em vez de uma linha. Base
do SSI; consome memória.

**PN-Counter / G-Counter** — CRDTs de contador (com e sem decremento).

## R

**Recuo exponencial** (*exponential backoff*) — Atraso que dobra a cada tentativa.

**Resolução** — O que se faz depois de detectar o conflito: retentar, mesclar, perguntar.

**Retentativa** (*retry*) — Reexecutar a operação após um conflito. **Exige reler o estado.**

**rowversion** — Tipo `binary(8)` do SQL Server, monotônico no banco inteiro, mantido
automaticamente. Token de versão ideal, mas específico do produto.

## S

**Saga** — Sequência de transações locais com compensações, usada quando não há transação
distribuída atômica.

**Serializabilidade** — Propriedade de uma execução concorrente equivaler a **alguma** execução
sequencial das mesmas transações.

**Serializabilidade por conflito** — Equivalência obtida trocando apenas operações não
conflitantes. Decidível em tempo polinomial; é o que os bancos implementam.

**Serializabilidade por visão** — Noção mais fraca e mais permissiva. Decidi-la é NP-completo;
nenhum banco a implementa.

**Snapshot isolation (SI)** — Nível em que cada transação vê um instantâneo consistente do
início. Permite write skew.

**SSI** (*Serializable Snapshot Isolation*) — Extensão do SI que rastreia dependências
leitura-escrita e aborta transações com estrutura perigosa. É o `SERIALIZABLE` do PostgreSQL
desde a 9.1.

**Starvation** (*inanição*) — Uma transação que nunca consegue confirmar por ser sempre a
vítima. Típica de transações longas sob validação para trás.

**SQLSTATE 40001** — Código padrão de *serialization failure*: refaça a transação inteira.

## T

**Thrashing** — Regime em que o aumento da concorrência **reduz** a vazão útil, porque quase
todo trabalho é descartado.

**Token de versão** — Valor que identifica uma versão específica de um dado e muda a cada
escrita.

**2PL** (*two-phase locking*) — Protocolo pessimista com fase de aquisição e fase de liberação
de locks. Garante serializabilidade.

**2PC** (*two-phase commit*) — Protocolo de commit distribuído em duas fases; bloqueante se o
coordenador falhar.

## V

**VACUUM** — Processo do PostgreSQL que recolhe versões mortas de linhas.

**Validação** — A fase do OCC em que se verifica se as leituras feitas continuam válidas.

**Vector clock** (*relógio vetorial*) — Mapa `{réplica → contador}` que permite distinguir
"atrasado" de "divergente". Necessário quando não há autoridade única.

**Versionless (optimistic locking)** — Detecção comparando os valores lidos, sem coluna de
versão. `OptimisticLockType.ALL` ou `DIRTY` no Hibernate.

## W

**WCU** (*write capacity unit*) — Unidade de capacidade de escrita do DynamoDB. Consumida
inclusive por escritas condicionais que falham.

**Write skew** (*distorção de escrita*) — Dois agentes leem o mesmo conjunto, cada um altera uma
linha **diferente**, e juntos violam uma invariante do conjunto. **Não é detectado por versão
de linha.** Ver [`10 §2.1`](10-fundamentos.md#21-write-skew-o-buraco-que-ninguém-vê).

## X

**xmin / xmax** — Campos de sistema do PostgreSQL: a transação que criou e a que removeu cada
versão de linha. `xmin` pode servir de token de versão, com ressalvas importantes.

---

## Códigos e mensagens de referência rápida

| Código | Significado |
|---|---|
| `40001` | serialization failure — refaça a transação |
| `40P01` | deadlock detectado (PostgreSQL) |
| `55P03` | lock não disponível (`NOWAIT`) |
| `ORA-08177` | falha de serialização (Oracle) |
| `ERROR 1213` | deadlock (MySQL) |
| `ERROR 1205` | timeout esperando lock (MySQL) |
| HTTP `409` | conflito de regra de negócio |
| HTTP `412` | pré-condição `If-Match` falhou |
| HTTP `428` | pré-condição obrigatória e ausente |
| `ConditionalCheckFailedException` | escrita condicional recusada (DynamoDB) |
| `OptimisticLockException` | versão não bateu (JPA) |
| `DbUpdateConcurrencyException` | versão não bateu (EF Core) |
| `StaleObjectError` | versão não bateu (ActiveRecord) |
| `SQLITE_BUSY` | contenção de arquivo — **não** é conflito de versão |
