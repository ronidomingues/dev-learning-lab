# 85 · Cursos gratuitos e certificações

`Nível: todos` · `Pesquisado na web em: 14/08/2026`

Não existe curso — em nenhum idioma — dedicado exclusivamente a "optimistic locking". O
assunto aparece como **módulo** dentro de cursos de banco de dados, transações, concorrência
ou sistemas distribuídos. Este arquivo aponta, em cada curso, **qual parte assistir**, para
você não perder tempo.

Legenda: **🆓 gratuito de verdade** · **🎓 gratuito para assistir, pago para certificar** ·
**⏱ duração aproximada**

---

## 1. Português (Brasil e Portugal)

O material em português é o mais escasso e o mais desigual. Os vídeos abaixo foram
verificados na busca de 14/08/2026; canais do YouTube podem sair do ar.

### 1.1 Fundamentos acadêmicos

| Curso | Autor / instituição | Link | ⏱ | Nível | Ano | Vale? |
|---|---|---|---|---|---|---|
| **Controle de Concorrência (parte 1) — Aula 19, Bancos de Dados** 🆓 | curso universitário aberto no YouTube | [vídeo](https://www.youtube.com/watch?v=eUwpRteFZTE) | ~50 min | intermediário | 2015 | **Sim, para a base.** Trata isolamento, consistência e locks com rigor de sala de aula. Envelheceu pouco: a teoria não mudou. Não cobre a parte de aplicação (ORM, HTTP) |
| **Controle de Concorrência / Bloqueio — Aula 20/11, Bancos de Dados 2020.2** 🆓 | idem | [vídeo](https://www.youtube.com/watch?v=bBEWX9Gl358) | ~50 min | intermediário | 2020 | Sim, mais recente que o anterior e com a mesma abordagem |

### 1.2 Aplicado (a parte que os cursos acadêmicos não cobrem)

| Curso | Link | ⏱ | Nível | Ano | Vale? |
|---|---|---|---|---|---|
| **Lock Otimista vs Pessimista: trabalhando com alta concorrência** 🆓 | [vídeo](https://www.youtube.com/watch?v=ZcPilksFCQk) | ~15–25 min | iniciante/intermediário | 2022 | **Sim, como primeira exposição prática.** Foco na decisão entre as duas estratégias. É superficial em retentativa e não cobre a camada HTTP |
| **Lock otimista e pessimista — explicação de dev sênior** 🆓 | [vídeo](https://www.youtube.com/watch?v=vocYtV-9Bys) | ~15–25 min | intermediário | 2026 | Sim. Publicado em março de 2026, é o material em português mais recente que encontrei sobre o tema |
| **Table Lock, Row Lock e o segredo para fazer o PostgreSQL voar** 🆓 | [vídeo](https://www.youtube.com/watch?v=iqhRkJtUA6Q) | ~20–40 min | intermediário | 2025 | Sim, para a perspectiva de operação: deadlocks, lentidão, inconsistência no PostgreSQL |

### 1.3 Texto em português

| Recurso | Link | Vale? |
|---|---|---|
| **Optimistic Lock** — artigo de Guilherme Guini 🆓 | [Medium](https://medium.com/@guilhermeguini/optimistic-lock-965d78a56140) | Sim, leitura de 10 minutos, com código |
| **Concorrência otimista e pessimista** — Marco Baccaro 🆓 | [blog](https://marcobaccaro.wordpress.com/2011/07/21/concorrencia-otimista-e-pessimista/) | De 2011, mas a comparação conceitual continua válida |
| **Controle de concorrência entre transações** — DevMedia 🆓 (parcial) | [artigo](https://www.devmedia.com.br/controle-de-concorrencia-entre-transacoes-em-bancos-de-dados/27756) | Fundamentos em português; parte do conteúdo do site é para assinantes |
| **Documentação do PostgreSQL em português** 🆓 | [postgresql.org](https://www.postgresql.org/docs/) | A tradução para português é parcial e desatualizada em relação à original — prefira a versão em inglês para o capítulo de isolamento |

**Avaliação franca do material em português:** dá para construir a base (vídeos 1.1) e ter a
primeira exposição prática (1.2), mas **não existe, em português, material de profundidade
sobre OCC em API, retentativa e sistemas distribuídos**. A partir do nível intermediário,
o inglês deixa de ser opcional. Este curso que você está lendo foi escrito em parte para
preencher essa lacuna.

---

## 2. Inglês

Aqui está o material de referência mundial, e a maior parte é gratuita.

### 2.1 O melhor recurso, sem concorrente: CMU 15-445

| | |
|---|---|
| **Curso** | *Intro to Database Systems* (15-445/645) 🆓 |
| **Instituição** | Carnegie Mellon University — prof. Andy Pavlo |
| **Link** | [site oficial](https://15445.courses.cs.cmu.edu/) · [canal CMU Database Group no YouTube](https://www.youtube.com/@CMUDatabaseGroup) |
| **⏱** | 26 aulas de ~80 min; para este assunto, **4 aulas** (~5 h) |
| **Nível** | intermediário → avançado |
| **Ano** | oferecido anualmente; o site traz a edição corrente (Fall 2026) e as anteriores |

**Assista exatamente estas:** as aulas de **Concurrency Control** (teoria da serializabilidade,
2PL, ordenação por timestamp, **OCC**, MVCC) — na edição de 2022, a aula 15 é
*Concurrency Control Theory* ([vídeo](https://www.youtube.com/watch?v=W5FFiI5ALTc)) e a
sequência seguinte cobre 2PL, timestamp ordering e MVCC.

**Por que vale o tempo:** é o tratamento mais rigoroso e mais bem explicado que existe em
vídeo, gratuito, com slides e notas em PDF. Se você só puder assistir a uma coisa deste
arquivo, assista a esta.
**Por que pode não valer:** é acadêmico. Não ensina a usar `@Version` nem `If-Match`.

Há também o **15-721 (Advanced Database Systems)**, do mesmo grupo, que aprofunda OCC em
bancos em memória — para quem vai a [`60`](60-teoria-avancada.md).

### 2.2 Sistemas distribuídos

| | |
|---|---|
| **Curso** | *Distributed Systems* 🆓 |
| **Autor** | Martin Kleppmann — University of Cambridge |
| **Link** | [playlist no YouTube](https://www.youtube.com/playlist?list=PLeKd45zvjcDFUEv_ohr_HdUFe97RItdiB) · [notas em PDF](https://www.cl.cam.ac.uk/teaching/2021/ConcDisSys/dist-sys-notes.pdf) · [site do curso](https://www.distributedsystemscourse.com/) |
| **⏱** | 8 aulas, ~7 h de vídeo + 87 páginas de notas |
| **Licença** | CC BY-SA — pode usar e derivar, com crédito |
| **Nível** | intermediário → avançado |

**Assista para este assunto:** as aulas de **tempo lógico e broadcast** (relógios vetoriais),
**replicação e quóruns**, e o estudo de caso de **software colaborativo** (CRDTs). É o
complemento natural de [`18`](18-sistemas-distribuidos.md).

Do mesmo autor, o livro [`90-bibliografia.md`](90-bibliografia.md#1-o-livro-para-comprar-se-for-comprar-um-só).

### 2.3 Stanford, em plataforma

| Curso | Plataforma | Link | Custo |
|---|---|---|---|
| **Databases: Indexes and Transactions** 🎓 | edX (StanfordOnline) | [Class Central](https://www.classcentral.com/course/edx-databases-indexes-and-transactions-19470) | assistir grátis; certificado ~US$ 49 |
| **Databases: Advanced Topics in SQL** 🎓 | edX (StanfordOnline) | [edX](https://www.edx.org/learn/sql/stanford-university-databases-advanced-topics-in-sql) | assistir grátis; certificado ~US$ 49 |

São parte da série de cinco cursos autoinstrucionais da Stanford, originalmente um dos três
primeiros MOOCs da universidade (2011), hoje no edX. O módulo de **transações** cobre
concorrência e recuperação de falhas. Preços conferidos em 14/08/2026 — o edX altera valores
e promoções com frequência.

**Franqueza sobre o certificado:** o certificado verificado da edX/Stanford tem algum valor de
sinalização em currículo, mas **nenhum empregador sério contrata por causa dele**. O valor real
está no conteúdo, que é gratuito.

### 2.4 Documentação oficial como trilha de estudo

Frequentemente melhor que qualquer curso, e sempre atualizada:

| Documento | Link | Por quê |
|---|---|---|
| **PostgreSQL — Transaction Isolation** 🆓 | [doc](https://www.postgresql.org/docs/current/transaction-iso.html) | O texto mais claro que existe sobre níveis de isolamento, com as mensagens de erro literais |
| **RFC 9110 §13 — Conditional Requests** 🆓 | [IETF](https://datatracker.ietf.org/doc/html/rfc9110) | A fonte normativa de `ETag`/`If-Match` |
| **MDN — `If-Match`** 🆓 | [MDN](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/If-Match) | Versão legível da RFC, com exemplos |
| **EF Core — Handling Concurrency Conflicts** 🆓 | [Microsoft Learn](https://learn.microsoft.com/en-us/ef/core/saving/concurrency) | O melhor material de fornecedor sobre resolução de conflito |
| **Tutorial de concorrência com EF Core** 🆓 | [Microsoft Learn](https://learn.microsoft.com/en-us/aspnet/core/data/ef-mvc/concurrency?view=aspnetcore-10.0) | Passo a passo com interface, incluindo a tela de conflito |
| **AWS — erros de escrita condicional sob alta concorrência** 🆓 | [AWS Database Blog](https://aws.amazon.com/blogs/database/handle-conditional-write-errors-in-high-concurrency-scenarios-with-amazon-dynamodb/) | O melhor texto sobre OCC em NoSQL |

### 2.5 Blogs de referência

| Autor | Link | Por quê |
|---|---|---|
| **Vlad Mihalcea** 🆓 (parte do conteúdo é pago) | [optimistic locking com JPA](https://vladmihalcea.com/optimistic-locking-version-property-jpa-hibernate/) · [versionless](https://vladmihalcea.com/how-to-prevent-optimisticlockexception-using-hibernate-versionless-optimistic-locking/) | A referência mundial em concorrência com Hibernate. Os artigos gratuitos já valem |
| **Martin Kleppmann** 🆓 | [martin.kleppmann.com](https://martin.kleppmann.com/) | Especialmente os textos sobre locks distribuídos e fencing tokens |

---

## 3. Francês

O material francês é predominantemente **acadêmico e em texto**, com pouca produção em vídeo
sobre este tema específico. O que encontrei de melhor:

| Recurso | Instituição | Link | Nível | Vale? |
|---|---|---|---|---|
| **Contrôle de concurrence** — capítulo 10 do curso de bases de données 🆓 | *bdpedia* (Philippe Rigaux e col.) | [sys.bdpedia.fr](http://sys.bdpedia.fr/conc.html) | intermediário | **Sim.** Trata explicitamente a abordagem otimista — intervir só quando o conflito de fato ocorre. Texto claro e bem estruturado |
| **Bases de données avancées — concurrence d'accès et reprise** 🆓 | CY Cergy Paris Université (Dan Vodislav) | [PDF](https://depinfo.u-cergy.fr/~vodislav/Master/BDA/fichiers/concurrence.pdf) | avançado | Sim. Slides de mestrado; cobre estampilhagem (*estampillage*) como algoritmo otimista |
| **Contrôle des accès concurrents et reprise** 🆓 | Télécom SudParis / IMT | [curso](https://bdatsp.wp.imtbs-tsp.eu/supports-pedagogiques/cours-redige/concurrence-reprise/) · [versão anterior](http://www-inf.it-sudparis.eu/cours/bd/?idr=42) | intermediário | Sim. Apresenta as duas grandes técnicas de serializabilidade: pessimista (verrouillage/estampillage) e otimista |
| **Cours complet bases de données — gestion de transactions** 🆓 | Developpez.com | [tutorial](https://sgbd.developpez.com/tutoriels/cours-complet-bases-de-donnees/?page=gestion-de-transactions) | iniciante → intermediário | Sim, como introdução em francês |
| **Transactions de base de données et contrôle de la concurrence optimiste** 🆓 | Microsoft Learn (Azure Cosmos DB) | [doc](https://learn.microsoft.com/fr-fr/azure/cosmos-db/nosql/database-transactions-optimistic-concurrency) | intermediário | Sim, para o ângulo NoSQL/`_etag`. É documentação de fornecedor, traduzida |

**Avaliação franca:** para quem lê francês, o material da bdpedia é excelente e melhor
organizado que boa parte do conteúdo em inglês de nível equivalente. Mas **não encontrei
curso em vídeo em francês dedicado ao tema** — só slides e texto.

---

## 4. Certificações

### 4.1 A verdade sobre certificação neste assunto

**Não existe certificação em optimistic locking**, e não deveria existir — é um tópico dentro
de um assunto maior. O que existe são certificações de banco de dados que **incluem** o tema
no conteúdo programático. Nenhuma delas testa o assunto a fundo.

Minha opinião, e é firme: **para este tema, certificação não é o caminho.** O que sinaliza
competência é conseguir explicar um write skew, mostrar uma métrica de conflito de um sistema
seu, e apontar o caminho de escrita desprotegido no código de outra pessoa. Isso aparece numa
conversa técnica de 15 minutos; nenhum certificado aparece.

### 4.2 Certificações gratuitas ou de baixo custo

| Certificação | Emissor | Custo | Cobre o tema? | Vale? |
|---|---|---|---|---|
| **PostgreSQL Associate / Professional** | EDB | pago (US$ 200+) | isolamento e MVCC, sim | Só se você trabalha com PostgreSQL profissionalmente |
| **Oracle Database SQL Certified Associate (1Z0-071)** | Oracle | ~US$ 245 | transações, superficialmente | Valor de mercado real em empresas Oracle |
| **AWS Certified Developer – Associate** | AWS | US$ 150 | escritas condicionais no DynamoDB, sim | Valor de mercado real; o tema é uma fração pequena |
| **Microsoft DP-300 / AZ-204** | Microsoft | ~US$ 165 | concorrência com EF Core e SQL Server | Idem |
| **freeCodeCamp — Relational Database** | freeCodeCamp | **gratuito** | fundamentos de SQL; **não** cobre concorrência | Certificado simbólico, sem valor de mercado, mas o conteúdo é bom para a base |
| **edX/Stanford — verificado** | edX | ~US$ 49 | transações, sim | Valor simbólico. Conteúdo gratuito é o que importa |

**Certificadores realmente gratuitos** (emitem certificado sem cobrar):
freeCodeCamp, Fundação Bradesco (cursos de banco de dados em português), Cisco NetAcad
(introdutórios). Nenhum deles cobre optimistic locking com profundidade. São úteis para
preencher a base de SQL, não para este assunto.

### 4.3 O que fazer no lugar

Uma trilha alternativa que, na minha experiência contratando e sendo contratado, vale mais
que qualquer certificado:

1. Termine o [lab 12](70-pratica.md#lab-12--auditar-um-sistema-real) num sistema real e
   escreva o relatório de uma página.
2. Publique um repositório com uma demonstração de lost update e sua correção — como o
   [`07-projeto-modelo`](07-projeto-modelo/README.md).
3. Escreva um texto explicando write skew com um exemplo do seu domínio.
4. Contribua com a documentação de um projeto aberto na parte de concorrência. É o tipo de
   contribuição mais aceita, porque quase ninguém quer fazer.

---

## 5. Trilha recomendada

| Se você tem… | Faça |
|---|---|
| **2 horas** | Vídeos 1.2 (pt) + [`01`](01-introducao-leigo.md) e [`04`](04-como-comecar.md) deste curso |
| **1 fim de semana** | Bloco A deste curso + [CMU 15-445, aula de Concurrency Control Theory](https://www.youtube.com/watch?v=W5FFiI5ALTc) |
| **1 mês** | Este curso inteiro + as 4 aulas de concorrência da CMU + [`labs 1–10`](70-pratica.md) |
| **3 meses** | Acima + curso de sistemas distribuídos do Kleppmann + o livro dele + os papers de [`95`](95-referencias.md) |

---

## Autoteste

1. Existe curso dedicado a optimistic locking? Como o assunto é ensinado, então?
2. Qual é o melhor recurso gratuito em vídeo, e quais aulas específicas assistir?
3. Que lacuna existe no material em português, e a partir de que nível ela pesa?
4. Qual recurso em francês você recomendaria e por quê?
5. Por que uma certificação não é o caminho para este tema?
6. Cite duas alternativas que sinalizam competência melhor que um certificado.

---

## Fontes consultadas (14/08/2026)

Todos os links foram obtidos em busca na web em 14/08/2026. Vídeos do YouTube e páginas de
curso podem sair do ar; a data de publicação de cada um está indicada nas tabelas.

- [CMU 15-445/645 — site oficial](https://15445.courses.cs.cmu.edu/)
- [CMU 15-445 — Concurrency Control Theory (Fall 2022)](https://www.youtube.com/watch?v=W5FFiI5ALTc)
- [Kleppmann — Distributed Systems, playlist](https://www.youtube.com/playlist?list=PLeKd45zvjcDFUEv_ohr_HdUFe97RItdiB) · [notas](https://www.cl.cam.ac.uk/teaching/2021/ConcDisSys/dist-sys-notes.pdf) · [anúncio do curso](https://martin.kleppmann.com/2020/11/18/distributed-systems-and-elliptic-curves.html)
- [Class Central — Databases: Indexes and Transactions (Stanford/edX)](https://www.classcentral.com/course/edx-databases-indexes-and-transactions-19470)
- [edX — Databases: Advanced Topics in SQL](https://www.edx.org/learn/sql/stanford-university-databases-advanced-topics-in-sql)
- [bdpedia — Contrôle de concurrence](http://sys.bdpedia.fr/conc.html)
- [CY Cergy — Concurrence d'accès et reprise (PDF)](https://depinfo.u-cergy.fr/~vodislav/Master/BDA/fichiers/concurrence.pdf)
- [Télécom SudParis — Contrôle des accès concurrents](https://bdatsp.wp.imtbs-tsp.eu/supports-pedagogiques/cours-redige/concurrence-reprise/)
- [Microsoft Learn (fr) — Contrôle de la concurrence optimiste no Cosmos DB](https://learn.microsoft.com/fr-fr/azure/cosmos-db/nosql/database-transactions-optimistic-concurrency)
- [Vlad Mihalcea — Optimistic locking com JPA e Hibernate](https://vladmihalcea.com/optimistic-locking-version-property-jpa-hibernate/)
- Vídeos em português: [Aula 19 · 2015.2](https://www.youtube.com/watch?v=eUwpRteFZTE) · [Aula 20/11 · 2020.2](https://www.youtube.com/watch?v=bBEWX9Gl358) · [Lock Otimista vs Pessimista · 2022](https://www.youtube.com/watch?v=ZcPilksFCQk) · [Lock otimista e pessimista · 2026](https://www.youtube.com/watch?v=vocYtV-9Bys) · [PostgreSQL locks · 2025](https://www.youtube.com/watch?v=iqhRkJtUA6Q)
