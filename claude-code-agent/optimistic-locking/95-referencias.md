# 95 · Referências — specs, papers, docs e pessoas

`Nível: todos` · `Verificado em: 14/08/2026`

Fontes primárias, na ordem em que você provavelmente vai precisar delas.

---

## 1. Papers fundamentais

| Ano | Trabalho | Por que ler | Acesso |
|---|---|---|---|
| 1979 | Papadimitriou — *The serializability of concurrent database updates*, JACM 26(4) | O teorema do grafo de precedência e a NP-completude da serializabilidade por visão | ACM DL (pago); cópias circulam em páginas de curso |
| **1981** | **Kung & Robinson — *On optimistic methods for concurrency control*, ACM TODS 6(2)** | **O paper fundador.** Três fases, validação para trás e para a frente | [ACM DL](https://dl.acm.org/doi/10.1145/319566.319567) (pago) · **[cópia aberta na CMU](https://www.cs.cmu.edu/~dga/15-712/F07/lectures/12-optimism.pdf)** · [resumo comentado](https://mwhittaker.github.io/papers/html/kung1981optimistic.html) |
| 1981 | Reed — *Implementing atomic actions on decentralized data* | Semente do MVCC | ACM DL |
| 1995 | Berenson, Bernstein, Gray, Melton, O'Neil, O'Neil — *A Critique of ANSI SQL Isolation Levels*, SIGMOD | Por que os níveis do SQL-92 são ambíguos e por que *lost update* ficou de fora | Microsoft Research / SIGMOD |
| 2005 | Fekete, Liarokapis, O'Neil, O'Neil, Shasha — *Making Snapshot Isolation Serializable*, ACM TODS 30(2) | A caracterização exata das anomalias sob SI (estrutura perigosa) | ACM DL |
| 2008 | Cahill, Röhm, Fekete — *Serializable Isolation for Snapshot Databases*, SIGMOD | O algoritmo SSI que o PostgreSQL implementa desde a 9.1 | ACM DL / páginas dos autores |
| 2011 | Shapiro, Preguiça, Baquero, Zawirski — *Conflict-free Replicated Data Types* | A formalização dos CRDTs | INRIA (aberto) |
| 2011 | Larson, Blanas, Diaconu, Freedman, Patel, Zwilling — *High-Performance Concurrency Control Mechanisms for Main-Memory Databases*, VLDB | Comparação empírica entre OCC e pessimista em banco em memória | **[arXiv, aberto](https://arxiv.org/pdf/1201.0228)** |
| 2012 | Thomson et al. — *Calvin: Fast Distributed Transactions for Partitioned Database Systems*, SIGMOD | Execução determinística: ordenar antes de executar | Yale (aberto) |
| 2013 | Tu, Zheng, Kohler, Liskov, Madden — *Speedy Transactions in Multicore In-Memory Databases* (Silo), SOSP | OCC por épocas em muitos núcleos | MIT (aberto) |
| 2016 | Yu, Xia, Pavlo, Sanchez, Rudolph, Devadas — *TicToc: Time Traveling Optimistic Concurrency Control*, SIGMOD | Timestamps derivados dos dados, sem contador global | CMU (aberto) |
| 2016 | Kim et al. — *Mostly-optimistic concurrency control for highly contended dynamic workloads on a thousand cores*, PVLDB 10(2) | OCC adaptativo sob contenção extrema | [ACM DL](https://dl.acm.org/doi/10.14778/3015274.3015276) |
| 2019 | Ding, Kot, Gehrke — *Improving Optimistic Concurrency Control Through Transaction Batching and Operation Reordering*, PVLDB 12(2) | Reduzir abortos por reordenação | **[PDF aberto](http://www.vldb.org/pvldb/vol12/p169-ding.pdf)** |
| 2019 | Guo, Wang et al. — *Adaptive optimistic concurrency control for heterogeneous workloads*, PVLDB 12(5) | Escolher a política por transação | [ACM DL](https://dl.acm.org/doi/10.14778/3303753.3303763) |
| 2020 | Hellerstein & Alvaro — *Keeping CALM: When Distributed Consistency is Easy*, CACM | Monotonicidade e a fronteira do que dispensa coordenação | CACM / arXiv (aberto) |
| 2025 | Lu et al. — *A Hybrid Approach to Integrating Deterministic and Non-Deterministic Concurrency Control (HDCC)*, PVLDB 18 | Calvin e OCC no mesmo banco | **[PDF aberto](https://www.vldb.org/pvldb/vol18/p1376-lu.pdf)** · [ACM](https://dl.acm.org/doi/10.14778/3718057.3718066) |
| 2026 | *Epoch-based Optimistic Concurrency Control in Geo-replicated Databases* | OCC entre regiões, validado em lote | **[arXiv](https://arxiv.org/pdf/2602.21566)** |
| 2026 | *TxnSails: Serializable Transaction Scheduling with Self-Adaptive Isolation Level Selection* | Escolher o nível de isolamento por transação | **[arXiv](https://arxiv.org/pdf/2502.00991)** |

**Se você for ler só um:** Kung & Robinson (1981), na cópia aberta da CMU. São 20 páginas e
elas contêm tudo o que os arquivos `10` e `60` deste curso formalizam.

---

## 2. Especificações e normas

| Spec | Seções relevantes | Link |
|---|---|---|
| **RFC 9110 — HTTP Semantics** (junho de 2022) | §8.8 (validadores: `ETag`, `Last-Modified`), §13 (requisições condicionais), §15.5.13 (`412`) | [datatracker](https://datatracker.ietf.org/doc/html/rfc9110) · [versão navegável](https://rfc.blacklabs.team/rfc9110.html) |
| RFC 7232 — Conditional Requests | obsoleta pela 9110; útil só como histórico | [httpwg](https://httpwg.org/specs/rfc7232.html) |
| RFC 6585 — Additional HTTP Status Codes | `428 Precondition Required` | IETF |
| ISO/IEC 9075 (SQL) | níveis de isolamento; `SQLSTATE 40001` | norma paga; a documentação do PostgreSQL cobre melhor e de graça |
| Jakarta Persistence | `@Version`, `LockModeType`, `OptimisticLockException` | [jakarta.ee/specifications/persistence](https://jakarta.ee/specifications/persistence/) |

---

## 3. Documentação oficial

### Bancos de dados

| Doc | Link |
|---|---|
| **PostgreSQL — Transaction Isolation** (a melhor de todas) | <https://www.postgresql.org/docs/current/transaction-iso.html> |
| PostgreSQL — Explicit Locking (`FOR UPDATE`, advisory locks) | <https://www.postgresql.org/docs/current/explicit-locking.html> |
| PostgreSQL — Error Codes (`40001`, `40P01`, `55P03`) | <https://www.postgresql.org/docs/current/errcodes-appendix.html> |
| MySQL — InnoDB Transaction Model | <https://dev.mysql.com/doc/refman/8.4/en/innodb-transaction-model.html> |
| SQLite — Isolation e WAL | <https://www.sqlite.org/isolation.html> |

### ORMs e frameworks

| Doc | Link |
|---|---|
| **EF Core — Handling Concurrency Conflicts** | <https://learn.microsoft.com/en-us/ef/core/saving/concurrency> |
| EF Core — tutorial de concorrência com interface | <https://learn.microsoft.com/en-us/aspnet/core/data/ef-mvc/concurrency?view=aspnetcore-10.0> |
| Hibernate — anotação `@OptimisticLocking` (javadoc) | <https://docs.hibernate.org/orm/6.4/javadocs/org/hibernate/annotations/OptimisticLocking.html> |
| Hibernate — página do projeto e licenças | <https://hibernate.org/orm/> · <https://hibernate.org/community/license/> |
| **Rails — `ActiveRecord::Locking::Optimistic`** | <https://api.rubyonrails.org/classes/ActiveRecord/Locking/Optimistic.html> |
| Django — expressões `F()` | <https://docs.djangoproject.com/en/stable/ref/models/expressions/> |
| Django — `select_for_update` | <https://docs.djangoproject.com/en/stable/ref/models/querysets/> |

### Nuvem e NoSQL

| Doc | Link |
|---|---|
| DynamoDB — escritas condicionais sob alta concorrência | <https://aws.amazon.com/blogs/database/handle-conditional-write-errors-in-high-concurrency-scenarios-with-amazon-dynamodb/> |
| DynamoDB — redução de custo em escritas condicionais falhas (2023) | <https://aws.amazon.com/about-aws/whats-new/2023/06/amazon-dynamodb-cost-failed-conditional-writes/> |
| Cosmos DB — concorrência otimista (`_etag`) | <https://learn.microsoft.com/en-us/azure/cosmos-db/nosql/database-transactions-optimistic-concurrency> |
| MongoDB — `findOneAndUpdate` | <https://www.mongodb.com/docs/manual/reference/method/db.collection.findOneAndUpdate/> |
| Redis — transações (`WATCH`/`MULTI`/`EXEC`) | <https://redis.io/docs/latest/develop/interact/transactions/> |
| etcd — API e transações | <https://etcd.io/docs/v3.5/learning/api/> |
| Kubernetes — `resourceVersion` e concorrência | <https://kubernetes.io/docs/reference/using-api/api-concepts/> |

---

## 4. Código-fonte para ler

Ler implementação real é o melhor antídoto contra entendimento superficial.

| O quê | Onde | Por quê |
|---|---|---|
| **SSI do PostgreSQL** | `src/backend/storage/lmgr/predicate.c` — o comentário de cabeçalho tem ~700 linhas | Um dos melhores textos explicativos sobre SSI que existe, e está num arquivo `.c` |
| MVCC do PostgreSQL | `src/backend/access/heap/heapam_visibility.c` | Como a visibilidade por instantâneo é decidida na prática |
| `@Version` no Hibernate | `org.hibernate.persister.entity.AbstractEntityPersister` (geração do `UPDATE`) | O SQL que a anotação produz |
| EF Core | `Microsoft.EntityFrameworkCore.Update` | Como os três conjuntos de valores são mantidos |
| ActiveRecord | `activerecord/lib/active_record/locking/optimistic.rb` | ~150 linhas; o mecanismo inteiro cabe numa leitura |
| **Este curso** | [`07-projeto-modelo/src/repo.js`](07-projeto-modelo/src/repo.js) | 130 linhas, tudo comentado |

O arquivo do ActiveRecord é o melhor ponto de partida: é curto o suficiente para ler inteiro
e faz exatamente o que os arquivos `10` a `13` descrevem.

---

## 5. Pessoas para acompanhar

| Pessoa | Área | Onde |
|---|---|---|
| **Martin Kleppmann** | transações, sistemas distribuídos, CRDTs, local-first | [martin.kleppmann.com](https://martin.kleppmann.com/) |
| **Andy Pavlo** | bancos de dados, controle de concorrência | [CMU Database Group](https://15445.courses.cs.cmu.edu/) e o canal do grupo no YouTube |
| **Vlad Mihalcea** | JPA/Hibernate, concorrência em Java | [vladmihalcea.com](https://vladmihalcea.com/) |
| **Peter Bailis** | isolamento, consistência (trabalhos seminais sobre coordenação) | páginas acadêmicas |
| **Philip Bernstein** | teoria de controle de concorrência | Microsoft Research |
| **Joseph Hellerstein** | CALM, coordenação | Berkeley |
| **Martin Fowler** | padrões de aplicação (*Optimistic Offline Lock*) | [martinfowler.com](https://martinfowler.com/eaaCatalog/) |

---

## 6. Ferramentas de diagnóstico

| Ferramenta | Para quê |
|---|---|
| `pg_stat_activity`, `pg_locks` | ver quem está esperando o quê no PostgreSQL |
| `pg_stat_database.xact_rollback` | contar transações abortadas |
| `log_lock_waits = on` | registrar esperas longas por lock |
| `SHOW ENGINE INNODB STATUS` | último deadlock no MySQL |
| `EXPLAIN (ANALYZE, BUFFERS)` | entender o custo do `UPDATE` que afeta zero linhas |
| `pgbench` com script próprio | reproduzir contenção de forma controlada |
| `jmeter` / `k6` / `wrk` | gerar concorrência de verdade contra a API |
| **`node test/demo-corrida.js`** | a versão mínima e legível de tudo isso: [aqui](07-projeto-modelo/test/demo-corrida.js) |

---

## 7. Outros assuntos desta pasta

| Assunto | Relação |
|---|---|
| [`../sql/`](../sql/00-MAPA.md) | a linguagem em que a guarda é escrita |
| [`../postgresql/`](../postgresql/00-MAPA.md) | MVCC, transações e isolamento em profundidade |
| [`../apis/`](../apis/00-MAPA.md) | HTTP, `ETag`, códigos de status |
| [`../docker/`](../docker/00-MAPA.md) | subir bancos para os laboratórios 8–10 |
| [`../testes-automatizados/`](../testes-automatizados/00-MAPA.md) | como testar concorrência sem enganar a si mesmo |

---

## Autoteste

1. Qual é o paper fundador, e onde obtê-lo legalmente de graça?
2. Que publicação apontou que o SQL-92 esquece o *lost update*?
3. Qual RFC é normativa hoje para `ETag`/`If-Match`, e que seção você consulta?
4. Onde está, no código do PostgreSQL, a melhor explicação sobre SSI?
5. Qual arquivo de código-fonte é o melhor ponto de partida para ler uma implementação inteira?
6. Que comando mostra o último deadlock no MySQL?
7. Cite dois papers de 2025–2026 e o que cada um propõe.
