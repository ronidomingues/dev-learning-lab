# 65 · Estado da arte — agosto de 2026

`Nível: pesquisa` · `Panorama fechado em: 14/08/2026`
`Reavaliar em: fevereiro de 2027 (ou quando o PostgreSQL 19 sair da fase beta)`

Este arquivo envelhece. As afirmações abaixo valem para a data no cabeçalho e trazem a fonte.
Onde eu dou opinião em vez de fato, está dito.

---

## 1. O estado consolidado (não muda desde ~2015)

Coisas que já estão resolvidas e não são fronteira de nada:

- **OCC por coluna de versão é o padrão de fato** em aplicações com formulário. Todo ORM
  relevante implementa; a discussão sobre "usar ou não" acabou.
- **`ETag`/`If-Match`** é o mecanismo padrão no HTTP desde 1997, consolidado na
  [RFC 9110](https://datatracker.ietf.org/doc/html/rfc9110) (2022). Não há proposta séria de
  substituição.
- **MVCC venceu** como base de implementação: PostgreSQL, Oracle, MySQL/InnoDB, SQL Server
  (com `SNAPSHOT`), SQLite (WAL), CockroachDB, TiDB — todos multiversão.
- **SSI** (`SERIALIZABLE` sem locks de leitura) está disponível desde o PostgreSQL 9.1 (2011).
  Continua subutilizado em produção, por desconhecimento mais do que por custo.
- **CRDTs saíram do laboratório.** Yjs e Automerge são infraestrutura de produto, não pesquisa.

Se o seu problema é um CRUD com formulário, o estado da arte para você é o que está nos
arquivos `10` a `20`. O que segue é fronteira, e a maior parte não vai afetar o seu trabalho.

---

## 2. Bancos de dados: para onde a pesquisa foi

### 2.1 Híbridos determinístico + otimista

A linha mais ativa. A ideia: bancos determinísticos (Calvin) ordenam as transações **antes**
de executá-las, o que elimina a validação — mas exigem conhecer os conjuntos de leitura e
escrita de antemão, o que nem toda transação permite. OCC não exige, mas aborta.

O trabalho **HDCC** (*A Hybrid Approach to Integrating Deterministic and Non-Deterministic
Concurrency Control in Database Systems*, PVLDB vol. 18) roda **os dois no mesmo banco**,
com regras que escolhem o caminho por transação, e mecanismos de *lock-sharing*, validação
global e intercalação de dois logs para manter serializabilidade e recuperação corretas.
Relata até **3,1×** sobre híbridos anteriores em TPC-C e YCSB.
[PDF](https://www.vldb.org/pvldb/vol18/p1376-lu.pdf) ·
[ACM DL](https://dl.acm.org/doi/10.14778/3718057.3718066)

**Em aberto:** classificar automaticamente qual transação vai para qual caminho, sem
anotação manual.

### 2.2 OCC geo-replicado por épocas

Validar cada transação exige uma ida e volta entre regiões — 100 a 300 ms entre continentes.
A resposta recente é agrupar transações em **épocas** e validar em lote, amortizando a latência
por muitas transações. Ver
[*Epoch-based Optimistic Concurrency Control in Geo-replicated Databases*](https://arxiv.org/pdf/2602.21566).

Trade-off explícito: a latência de **uma** transação piora (ela espera o fim da época); a
**vazão** melhora muito. É a escolha certa para carga de lote e a errada para interativo.

### 2.3 Seleção adaptativa de nível de isolamento

Em vez de o desenvolvedor escolher `READ COMMITTED` ou `SERIALIZABLE` de uma vez, o sistema
escolhe por transação, garantindo serializabilidade com o nível mais barato que a carga
permitir. Ver [TxnSails](https://arxiv.org/pdf/2502.00991).

**Minha opinião:** esta é a linha com maior chance de chegar a produtos comerciais nos
próximos anos, porque resolve um problema real e visível (todo mundo roda em `READ COMMITTED`
por medo do custo do `SERIALIZABLE`) sem exigir que o desenvolvedor entenda o assunto.

### 2.4 Controle de concorrência aprendido

Modelar a escolha de política como função aprendida da carga observada. Publicações recentes
(2026) tratam disso. Estado: **promissor e imaturo**.

Os dois problemas conhecidos: comportamento sob carga fora da distribuição de treino, e a
dificuldade de dar garantias quando a política é um modelo estatístico. Minha posição: a
correção precisa vir do mecanismo, com o modelo escolhendo apenas entre políticas **todas
corretas** — um modelo capaz de violar serializabilidade é inutilizável em banco de dados.

### 2.5 Muitos núcleos

Em máquinas com centenas de núcleos, o contador global de transações vira ponto de
serialização e a própria validação é o gargalo. As respostas — Silo (*epoch-based*), TicToc
(timestamps derivados dos dados) e derivados — continuam sendo a base do que se faz em bancos
em memória. Ver também
[*Mostly-optimistic concurrency control for highly contended dynamic workloads on a thousand
cores*](https://dl.acm.org/doi/10.14778/3015274.3015276) e
[*Improving OCC Through Transaction Batching and Operation Reordering*](http://www.vldb.org/pvldb/vol12/p169-ding.pdf).

---

## 3. Local-first: o conflito deixando de existir

A mudança mais visível para quem constrói produto, e onde há mais movimento em 2026.

### 3.1 O que mudou

| Antes (~2020) | Agosto de 2026 |
|---|---|
| CRDT era pesquisa, com fama de lento e pesado | Yjs e Automerge são infraestrutura de produto |
| Cada equipe escrevia o próprio servidor de sincronização | plataformas gerenciadas (Liveblocks, Hocuspocus) |
| Estado no servidor, cliente burro | SQLite no cliente + motor de sincronização |
| Conflito resolvido por versão | conflito **eliminado** por construção |

Números publicados: o Automerge 3.0 (final de 2025) introduziu formato colunar com redução de
40–60% no tamanho dos documentos e tempos de merge abaixo do milissegundo; o Yjs continua a
biblioteca mais implantada, com ordem de ~920 mil downloads semanais e o maior ecossistema de
integrações. Fonte:
[Yjs vs Automerge vs Loro — PkgPulse, 2026](https://www.pkgpulse.com/guides/yjs-vs-automerge-vs-loro-crdt-libraries-2026).
Trate os números como ordem de grandeza — são de levantamento secundário, não de medição
própria.

O FOSDEM 2026 teve trilha dedicada a Local-First, sync engines e CRDTs
([programa](https://fosdem.org/2026/schedule/track/local-first/)), o que é um indicador
razoável de que o assunto saiu do nicho.

### 3.2 O que **não** mudou

E é o que mais importa para não se iludir:

- **CRDT garante convergência, não invariante global.** "Estoque não fica negativo" continua
  exigindo coordenação. Isso é o teorema CALM ([`60 §4.3`](60-teoria-avancada.md#43-o-teorema-cap-e-a-coordenação)),
  não uma limitação de implementação.
- **Convergir não é acertar.** Duas réplicas podem convergir para um estado que ninguém
  queria. O merge automático de texto produz frases que nenhum dos autores escreveu.
- **O custo de metadados é real.** Um CRDT de texto guarda informação por caractere; documentos
  longos com histórico longo crescem. A compressão do Automerge 3.0 atacou exatamente isso.
- **Não substitui o OCC no back-end.** Sincronizar o cliente com CRDT e gravar no banco
  continua exigindo guarda na escrita.

### 3.3 Convergência para SQLite

Um padrão que se firmou: **SQLite como banco da aplicação no cliente**, com semântica de
sincronização por cima — `cr-sqlite` adiciona semântica CRDT a tabelas SQLite como extensão
carregável. O efeito prático é que o modelo de dados do cliente e o do servidor passam a ser
o mesmo, e a sincronização vira um detalhe de infraestrutura em vez de um projeto.

---

## 4. O que continua sem solução

Uma lista honesta dos problemas em aberto que afetam trabalho real:

1. **Escolher a granularidade de versionamento automaticamente.** Ninguém sabe decidir, sem
   conhecer o domínio, se a versão vai na linha ou no agregado. Continua sendo julgamento humano.
2. **Resolução semântica de conflito.** Merge de três vias resolve conflito **sintático**.
   "Ana mudou o preço para R$ 100 e Bruno mudou a moeda para dólar" é sintaticamente
   mesclável e semanticamente desastroso. Não há solução geral.
3. **Prever a taxa de conflito antes de construir.** Só se descobre medindo em produção.
4. **UX de conflito.** Não há padrão consolidado. Cada produto reinventa, e a maioria
   reinventa mal. É, na minha opinião, a maior lacuna prática do assunto — e não é um problema
   de banco de dados.
5. **Invariantes distribuídas sem coordenação.** O CALM diz que é impossível para operações não
   monotônicas. Continuará impossível.

---

## 5. Se eu fosse escolher hoje

Recomendações para agosto de 2026, deixando claro o que é consenso e o que é minha leitura.

| Situação | Recomendação | Natureza |
|---|---|---|
| CRUD com formulário | coluna `version` + `If-Match` no HTTP | consenso |
| API pública | `ETag` forte, `412`, `428`, estado atual no corpo do 412 | consenso (e mal praticado) |
| Invariante sobre conjunto de linhas | `SERIALIZABLE` + retentativa em `40001` | consenso técnico, adoção baixa |
| Contador, saldo, estoque | delta atômico com guarda no `WHERE` | consenso |
| Colaboração em tempo real | Yjs (ecossistema) ou Automerge (histórico e DX) | consenso |
| Aplicativo offline-first | SQLite local + motor de sincronização | **minha leitura** — o campo ainda se move |
| Linha quente (> 30% de conflito) | fila por chave ou reprojetar o dado | **minha leitura**, mas confortável |
| Multi-região com escrita em todo lado | evite; particione por região se possível | **minha opinião**, e forte |

---

## 6. O que observar até fevereiro de 2027

- **PostgreSQL 19** (beta 3 em agosto de 2026): acompanhar o que muda em `SERIALIZABLE`,
  em desempenho de MVCC e no `VACUUM`.
  [Notas de lançamento](https://www.postgresql.org/about/news/postgresql-186-1711-1615-1519-1424-and-19-beta-3-released-3365/)
- **Seleção adaptativa de isolamento** chegando (ou não) a algum produto comercial.
- **Consolidação dos motores de sincronização**: hoje há muitos concorrentes; espero que
  alguns desapareçam.
- **Escritas condicionais em armazenamento de objetos** (S3 e equivalentes) sendo usadas como
  base transacional por formatos de tabela — se isso se firmar, muda como se constrói
  *data lake* transacional.

---

## Autoteste

1. O que já é consenso e não é mais fronteira de pesquisa neste assunto?
2. O que o HDCC combina, e por que a combinação faz sentido?
3. Qual é o trade-off do OCC por épocas em geo-replicação?
4. Por que o controle de concorrência aprendido não pode ter a correção delegada ao modelo?
5. O que CRDT resolve e o que ele comprovadamente não resolve? Cite o resultado teórico.
6. Cite três problemas em aberto que afetam trabalho prático.
7. Nas recomendações da seção 5, quais itens são consenso e quais são opinião do autor?

---

## Fontes consultadas (14/08/2026)

- [*A Hybrid Approach to Integrating Deterministic and Non-Deterministic Concurrency Control (HDCC)*, PVLDB 18](https://www.vldb.org/pvldb/vol18/p1376-lu.pdf) · [ACM](https://dl.acm.org/doi/10.14778/3718057.3718066)
- [*Epoch-based Optimistic Concurrency Control in Geo-replicated Databases*, arXiv](https://arxiv.org/pdf/2602.21566)
- [*TxnSails: Serializable Transaction Scheduling with Self-Adaptive Isolation Level Selection*, arXiv](https://arxiv.org/pdf/2502.00991)
- [*Mostly-optimistic concurrency control…*, PVLDB 10(2)](https://dl.acm.org/doi/10.14778/3015274.3015276)
- [*Adaptive optimistic concurrency control for heterogeneous workloads*, PVLDB 12(5)](https://dl.acm.org/doi/10.14778/3303753.3303763)
- [*Improving OCC Through Transaction Batching and Operation Reordering*, PVLDB 12(2)](http://www.vldb.org/pvldb/vol12/p169-ding.pdf)
- [*A survey on hybrid transactional and analytical processing*, VLDB Journal](https://link.springer.com/article/10.1007/s00778-024-00858-9)
- [FOSDEM 2026 — trilha Local-First, sync engines, CRDTs](https://fosdem.org/2026/schedule/track/local-first/)
- [Yjs vs Automerge vs Loro — comparativo 2026](https://www.pkgpulse.com/guides/yjs-vs-automerge-vs-loro-crdt-libraries-2026)
- [PostgreSQL 18.6 e 19 Beta 3, 13/08/2026](https://www.postgresql.org/about/news/postgresql-186-1711-1615-1519-1424-and-19-beta-3-released-3365/)
- [RFC 9110 — HTTP Semantics](https://datatracker.ietf.org/doc/html/rfc9110)
