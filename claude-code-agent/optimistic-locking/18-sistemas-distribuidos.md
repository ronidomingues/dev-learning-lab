# 18 · Sistemas distribuídos — CAS, leases e fencing

`Nível: avançado` · `Atualizado em: 14/08/2026`

Num único banco, optimistic locking é uma otimização. Em sistema distribuído, ele
frequentemente é **a única opção**: manter locks entre nós exige coordenação, e coordenação
em rede é lenta, cara e frágil a partições.

Este arquivo mostra a mesma ideia em cinco escalas — do registrador da CPU ao consenso entre
data centers — e o que muda em cada uma.

---

## 1. A mesma operação, cinco escalas

| Escala | Operação | Token | Falha |
|---|---|---|---|
| Registrador de CPU | `CMPXCHG` (x86), `LL/SC` (ARM) | o valor anterior | *flag* zero |
| Estrutura lock-free | `compareAndSet` | ponteiro + tag | `false` |
| Linha de banco | `UPDATE ... WHERE version = ?` | coluna de versão | 0 linhas |
| Chave em KV distribuído | `Txn().If(ModRevision == r)` | revisão do consenso | `Succeeded == false` |
| Recurso HTTP | `PUT + If-Match` | `ETag` | `412` |

**É a mesma operação em todas as linhas**: comparar um token e, atomicamente, escrever se ele
bater. O que muda entre elas não é a ideia; é **quem garante a atomicidade** e **quanto custa**.

- Na CPU, a atomicidade vem do protocolo de coerência de cache (MESI). Custa dezenas de ciclos.
- No banco, vem do lock interno de linha. Custa microssegundos.
- No etcd, vem do consenso Raft. Custa uma ida e volta pela rede, mais fsync no quórum.

Perceber que é a mesma coisa é o que permite transferir intuição: se você entende por que o
ABA quebra um CAS de ponteiro, entende por que um token que se repete quebra o seu `UPDATE`.

---

## 2. Escritas condicionais nos sistemas mais usados

### 2.1 DynamoDB

```python
tabela.update_item(
    Key={'id': 'conta-1'},
    UpdateExpression='SET saldo = :novo, version = :vnova',
    ConditionExpression='version = :vlida',      # a guarda
    ExpressionAttributeValues={':novo': 90, ':vnova': 8, ':vlida': 7},
    ReturnValuesOnConditionCheckFailure='ALL_OLD',
)
```

Três coisas específicas:

1. A escrita condicional é atômica **dentro de uma partição**. Entre partições, não — para
   isso existe `TransactWriteItems`, com custo dobrado.
2. **A escrita condicional que falha consome capacidade de escrita (WCU).** Numa chave quente
   você paga pelas tentativas recusadas. Em SQL, o custo de um `UPDATE 0` existe, mas não
   aparece diretamente na fatura.
3. `ReturnValuesOnConditionCheckFailure` (introduzido em 2023) devolve o item como estava na
   falha **sem cobrar uma leitura extra** — use sempre; economiza um `get_item` por conflito.

E uma armadilha: com leitura eventual (`ConsistentRead=False`, o padrão), você pode ler uma
versão antiga e gerar um conflito **garantido**. Leia com `ConsistentRead=True` antes de
escrever condicionalmente.

### 2.2 etcd

```go
resp, err := cli.Txn(ctx).
    If(clientv3.Compare(clientv3.ModRevision("/config/x"), "=", rev)).
    Then(clientv3.OpPut("/config/x", novoValor)).
    Else(clientv3.OpGet("/config/x")).       // devolve o estado atual no conflito
    Commit()
if !resp.Succeeded { /* conflito: resp.Responses[0] traz o valor atual */ }
```

O `ModRevision` é um contador **global e monotônico** mantido pelo Raft. Isso dá uma
propriedade que a coluna de versão de um banco não dá: **ordem total entre chaves diferentes**.
Você consegue dizer "esta escrita aconteceu antes daquela" para chaves que nada têm a ver
uma com a outra — base para *watch*, *snapshot* consistente e reconstrução de estado.

O Kubernetes usa exatamente isso: o campo `metadata.resourceVersion` de todo objeto é a
revisão do etcd, e `kubectl apply` com `--server-side` faz optimistic locking sobre ela.
Quando você vê `Operation cannot be fulfilled on deployments.apps "x": the object has been
modified; please apply your changes to the latest version and try again`, é um `412` com
outro nome.

### 2.3 Redis

```
WATCH conta:1
GET conta:1            → 100
MULTI
SET conta:1 90
EXEC                   → nil se conta:1 mudou desde o WATCH
```

`WATCH` implementa OCC de verdade: se qualquer chave observada mudar entre o `WATCH` e o
`EXEC`, a transação inteira é descartada.

Ressalvas práticas: o `WATCH` é por **conexão**, então um *pool* que devolve a conexão no meio
quebra tudo; e em Redis Cluster todas as chaves precisam estar no mesmo slot. Para lógica
mais complexa, um script Lua roda **atomicamente** no servidor e dispensa o `WATCH` — é a
solução preferida hoje.

### 2.4 S3 e armazenamento de objetos

O S3 passou a suportar escritas condicionais (`If-Match`, `If-None-Match` em `PutObject`),
o que habilita um padrão importante: **usar o próprio armazenamento como fonte de verdade
transacional**, sem um banco no meio. É a base de formatos de tabela como Delta Lake e
Iceberg, que fazem *commit* trocando um ponteiro de metadados por escrita condicional.

---

## 3. Leases: o lock que não trava para sempre

Num sistema distribuído, o problema com locks não é adquirir — é **liberar quando o dono
morre**. A resposta é o **lease**: um lock com prazo de validade.

```
adquirir(recurso, dono, prazo):
    UPDATE recurso SET dono = ?, expira_em = now() + prazo, version = version + 1
     WHERE id = ? AND (dono IS NULL OR expira_em < now() OR dono = ?)
```

| Propriedade | Lock clássico | Lease |
|---|---|---|
| Liberação se o dono morrer | precisa de detecção externa | automática, no prazo |
| Requer relógio? | não | **sim** |
| Garante exclusão mútua? | sim | **não sozinho** (seção 4) |

**A parte que quase todo mundo erra:** o prazo tem de ser avaliado com o relógio **de um único
lugar** — o do banco ou o do serviço de coordenação. Comparar `expira_em` com o relógio da
aplicação significa comparar relógios de máquinas diferentes, e a diferença entre eles é
exatamente a janela pela qual dois donos coexistem.

Ver a implementação completa em
[`06-exemplos.md` § 13](06-exemplos.md#13--produção-reserva-de-assentos-com-lease--occ).

---

## 4. Fencing tokens: por que o lease sozinho não basta

O argumento é de Martin Kleppmann e é o mais importante desta página.

```
Cliente A adquire o lease (prazo: 30 s)
Cliente A sofre uma pausa de GC de 40 s   ← ou: swap, VM migrada, rede lenta
                        lease de A expira
                        Cliente B adquire o lease
                        Cliente B escreve
Cliente A acorda, acha que ainda tem o lease, e escreve por cima
```

Nenhum ajuste de prazo resolve: a pausa pode ser maior que qualquer prazo. O lease sozinho
**não garante exclusão mútua**.

A correção é o **fencing token**: o serviço de lock devolve um número **estritamente
crescente** a cada concessão, e o **recurso** (não o cliente) recusa qualquer escrita com
token menor que o último que aceitou.

```
A recebe lease com token 33
                        B recebe lease com token 34
                        B escreve com token 34  → aceito, recurso guarda 34
A acorda e escreve com token 33 → RECUSADO (33 < 34)
```

```sql
-- O recurso guardando o maior token já visto. Isto é optimistic locking puro.
UPDATE recurso
   SET conteudo = ?, ultimo_token = ?
 WHERE id = ? AND ultimo_token < ?;
-- 0 linhas = você é um dono zumbi; pare e não tente de novo
```

Note a estrutura: **o fencing token é uma guarda otimista com comparação de ordem em vez de
igualdade.** Em vez de "só grave se a versão for exatamente 7", é "só grave se o meu token for
maior que o último aceito". Mesma família, propriedade diferente.

Onde isso aparece em produtos reais:

- **Kafka**: `producer epoch` — um produtor "zumbi" que volta recebe `ProducerFencedException`.
- **HDFS / ZooKeeper**: `zxid` e o padrão de *fencing* de NameNode.
- **etcd**: a `revision` serve de token natural, por ser globalmente monotônica.
- **Kubernetes**: `resourceVersion` cumpre o mesmo papel para os controladores.

**Se você implementar um lock distribuído sem fencing token, você não implementou exclusão
mútua — implementou uma redução de probabilidade.** Isso pode ser suficiente (é, para muitos
casos), mas precisa ser uma decisão consciente e documentada, não um mal-entendido.

---

## 5. Multi-mestre: quando não há uma autoridade

Tudo acima pressupõe **um lugar** que sabe a versão atual. Quando há vários escritores
independentes que se sincronizam depois — replicação multi-mestre, aplicativo offline,
dispositivos —, a premissa cai e o contador único deixa de funcionar.

### 5.1 Relógios vetoriais

```
A = {r1: 3, r2: 1}   B = {r1: 3, r2: 2}   →  B descende de A     (aplicar B)
A = {r1: 4, r2: 1}   B = {r1: 3, r2: 2}   →  CONCORRENTES        (conflito real)
```

O ganho é o terceiro estado: um contador único não distingue "você está atrasado" de "nós
divergimos". O custo é o tamanho (cresce com o número de réplicas) e a poda de réplicas mortas.

### 5.2 Last-write-wins e o que ele custa

A alternativa barata é `LWW`: fica o valor com o maior timestamp. É o que o Cassandra faz por
padrão.

É simples, converge sempre e **descarta dados em silêncio**. Duas escritas concorrentes: uma
some, e ninguém é avisado. Como os relógios das máquinas divergem, "a mais recente" pode ser
literalmente a mais antiga. LWW é uma decisão de projeto legítima para dados descartáveis
(cache, telemetria, presença) e uma escolha ruim para qualquer coisa que alguém precise
auditar depois.

### 5.3 CRDTs

Estruturas cujas operações são comutativas, associativas e idempotentes por construção: a
ordem de aplicação não importa, e réplicas que receberam o mesmo conjunto de operações
convergem para o mesmo estado. **Não há conflito a detectar.**

| Tipo | O que resolve |
|---|---|
| G-Counter / PN-Counter | contadores que só sobem / sobem e descem |
| G-Set / OR-Set | conjuntos com adição / adição e remoção |
| LWW-Register | registrador com desempate por timestamp |
| RGA / Yjs / Automerge | texto colaborativo em tempo real |

O limite é conceitual e importante: **CRDT garante convergência, não invariantes globais**.
"O saldo nunca fica negativo" não é expressável — duas réplicas podem debitar
simultaneamente e convergir para um saldo negativo. Para invariantes globais é preciso
coordenação, e aí você voltou ao OCC ou ao consenso.

---

## 6. Transações distribuídas e OCC

Quando a transação atravessa vários nós, as opções principais:

| Técnica | Como funciona | Custo |
|---|---|---|
| **2PC** (commit em duas fases) | prepara todos, depois confirma todos | bloqueante: se o coordenador cai entre as fases, os participantes ficam presos |
| **OCC distribuído** | cada nó valida localmente; o coordenador aborta se algum recusar | sem bloqueio, mas a taxa de aborto cresce com o número de nós |
| **Determinístico** (Calvin) | ordena as transações **antes** de executar | ordem conhecida = nada a validar; exige conhecer o conjunto de leituras/escritas de antemão |
| **Saga** | sequência de transações locais com compensação | sem atomicidade global; exige compensação para cada passo |

A observação que importa: com OCC distribuído, se cada nó tem probabilidade `p` de conflito e
os eventos são aproximadamente independentes, a chance de a transação inteira passar é
`(1−p)ⁿ`. Com `p = 5%` e 10 nós, a taxa de sucesso cai para ~60% — e cada aborto desperdiça o
trabalho de todos os nós. **O OCC escala mal com o número de participantes.** É a razão de os
sistemas realmente grandes irem para determinismo (Calvin, FaunaDB) ou para particionamento
que evita transações multi-nó.

---

## 7. O que levar deste arquivo

1. **É tudo a mesma operação**, do `CMPXCHG` ao `If-Match`. Muda quem garante a atomicidade e
   quanto ela custa.
2. **Lease sem fencing token não é exclusão mútua** — é redução de probabilidade.
3. **Fencing token é OCC com ordem em vez de igualdade.**
4. **Sem uma autoridade única, contador vira vetor** — ou você aceita LWW e a perda silenciosa.
5. **CRDT elimina o conflito, mas não garante invariante global.**
6. **OCC degrada com o número de participantes**: `(1−p)ⁿ`.

---

## Autoteste

1. Liste as cinco escalas da seção 1 e diga quem garante a atomicidade em cada uma.
2. Por que uma escrita condicional que falha no DynamoDB ainda custa dinheiro?
3. Explique, com uma linha do tempo, por que um lease sozinho não garante exclusão mútua.
4. Em que sentido um fencing token é um caso particular de optimistic locking?
5. Que estado um relógio vetorial distingue que um contador único não distingue?
6. Por que LWW é uma escolha ruim para dados auditáveis?
7. Que invariante um CRDT de contador **não** consegue garantir, e por quê?
8. Com `p = 5%` por nó, qual a taxa de sucesso de uma transação OCC em 10 nós? O que isso
   implica para a arquitetura?
