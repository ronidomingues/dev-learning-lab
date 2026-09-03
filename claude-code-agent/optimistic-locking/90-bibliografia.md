# 90 · Bibliografia comentada

`Nível: todos` · `Verificado na web em: 14/08/2026`

Nenhum livro é dedicado a optimistic locking. O assunto ocupa um capítulo — às vezes uma
seção — em livros de transações, bancos de dados ou sistemas distribuídos. Abaixo, o que
realmente vale, com o **capítulo específico** a ler.

Onde eu não tive certeza da edição ou do ISBN, **omiti** em vez de arriscar. Confira sempre
na página do editor antes de comprar.

---

## 1. O livro para comprar, se for comprar um só

### Kleppmann, Martin; Riccomini, Chris. *Designing Data-Intensive Applications*. 2ª edição. O'Reilly Media, 2026.

| | |
|---|---|
| **Nível** | intermediário → avançado |
| **Leia** | o capítulo de **transações** (capítulo 7 na 2ª edição) e o de consistência e consenso |
| **Gratuito?** | não; capítulos de amostra circulam, e a ScyllaDB já patrocinou uma oferta ([link](https://lp.scylladb.com/designing-data-intensive-apps-book-offer)) — verifique se ainda vale |
| **Edição em português?** | a 1ª edição saiu no Brasil como *Projetando Aplicações com Uso Intensivo de Dados* (Novatec). A tradução é competente; a 2ª edição, até 14/08/2026, eu não confirmei em português |

**O que ele faz melhor que os outros:** explica *lost update*, write skew e as anomalias de
isolamento em linguagem de engenharia, com exemplos reais, sem exigir formalismo. É o único
livro que trata **por que o seu banco não protege o que você acha que protege** de um jeito
que um desenvolvedor entende na primeira leitura.

**Envelheceu?** A 1ª edição (2017) continuava valendo em 2026 na parte de transações — a teoria
não mudou. A 2ª edição (janeiro de 2026), escrita com Chris Riccomini, reestruturou capítulos
e reescreveu quase por completo o de consistência e consenso. Se você vai comprar agora,
compre a segunda.

**Minha recomendação:** se você lê um livro sobre este assunto na vida, é este.

---

## 2. Os clássicos que continuam valendo

### Bernstein, Philip A.; Hadzilacos, Vassos; Goodman, Nathan. *Concurrency Control and Recovery in Database Systems*. Addison-Wesley, 1987.

| | |
|---|---|
| **Nível** | avançado → pesquisa |
| **Leia** | capítulo 4 (*Concurrency Control*), com a seção sobre métodos por certificação/otimistas |
| **Gratuito?** | **sim, legalmente.** Esgotado em papel, os autores liberaram o PDF: <http://research.microsoft.com/pubs/ccontrol/> · também no [Internet Archive](https://archive.org/details/concurrencycontr0000bern) |

**O que faz melhor:** é o tratamento formal mais completo e mais bem escrito de controle de
concorrência que existe. A teoria de serializabilidade de [`60`](60-teoria-avancada.md) está
aqui, com as provas.

**Envelheceu?** A teoria, não — é matemática. O que envelheceu foram as premissas de hardware
(discos lentos, pouca memória) e a ausência de MVCC moderno, SSI e sistemas distribuídos
contemporâneos. Leia pela teoria, não pelas recomendações práticas.

### Gray, Jim; Reuter, Andreas. *Transaction Processing: Concepts and Techniques*. Morgan Kaufmann, 1992.

| | |
|---|---|
| **Nível** | avançado |
| **Leia** | os capítulos 7 e 8 (isolamento e mecanismos de lock) |
| **Gratuito?** | não; esgotado, circula usado |

**O que faz melhor:** é o livro de quem **construiu** os sistemas. Jim Gray ganhou o prêmio
Turing por este trabalho. A profundidade sobre o que dá errado em produção não tem paralelo.

**Envelheceu?** Parcialmente. Os capítulos sobre transações e isolamento continuam
insubstituíveis. Os de hardware, armazenamento e disponibilidade são de outra era. É um livro
denso, grande e desconfortável de ler — e ainda assim vale.

### Weikum, Gerhard; Vossen, Gottfried. *Transactional Information Systems*. Morgan Kaufmann, 2001.

| | |
|---|---|
| **Nível** | pesquisa |
| **Leia** | a parte II, sobre controle de concorrência |
| **Gratuito?** | não |

**O que faz melhor:** é o tratamento formal mais moderno que o Bernstein, com notação
consistente e cobertura de protocolos multiníveis. É o livro para quem vai fazer pesquisa,
não para quem vai programar.

---

## 3. Livros-texto de banco de dados (para a base)

### Silberschatz, Abraham; Korth, Henry F.; Sudarshan, S. *Database System Concepts*. 7ª edição. McGraw-Hill, 2019/2020.

| | |
|---|---|
| **Nível** | iniciante → intermediário |
| **Leia** | os capítulos de transações e de controle de concorrência |
| **Gratuito?** | o livro, não. **Slides, exercícios resolvidos e seis capítulos online são gratuitos** no site oficial: <https://www.db-book.com/> |
| **Português?** | edições anteriores saíram como *Sistema de Banco de Dados* (Elsevier/Campus). Tradução aceitável; confira qual edição está disponível |

**O que faz melhor:** é o livro-texto padrão de graduação no mundo todo. Se você precisa da
base de transações antes de encarar este curso, é aqui.

### Garcia-Molina, Héctor; Ullman, Jeffrey D.; Widom, Jennifer. *Database Systems: The Complete Book*. 2ª edição. Pearson, 2008.

| | |
|---|---|
| **Nível** | intermediário |
| **Leia** | a parte sobre controle de concorrência (validação otimista tem seção própria) |
| **Gratuito?** | não |

**O que faz melhor:** a exposição da **validação otimista** é mais clara e mais didática que a
do Silberschatz, com o algoritmo apresentado passo a passo. É o mesmo grupo que produziu os
cursos de Stanford citados em [`85`](85-cursos-e-certificacoes.md).

**Envelheceu?** A 2ª edição é de 2008 e não cobre MVCC moderno, SSI nem NoSQL. Para a teoria
de OCC, continua ótima.

### Elmasri, Ramez; Navathe, Shamkant B. *Fundamentals of Database Systems*. Pearson.

| | |
|---|---|
| **Nível** | iniciante → intermediário |
| **Português?** | **sim** — *Sistemas de Banco de Dados*, Pearson Brasil, com várias edições traduzidas |

**O que faz melhor:** é o livro de banco de dados mais adotado em cursos brasileiros e a
melhor opção **em português** para os fundamentos de transações e concorrência. A tradução é
adequada, ainda que a terminologia às vezes destoe do jargão usado no mercado.
Confira a edição corrente no site da Pearson antes de comprar.

---

## 4. Livros de aplicação

### Mihalcea, Vlad. *High-Performance Java Persistence*. Autopublicado, 2016 (com atualizações posteriores).

| | |
|---|---|
| **Nível** | intermediário → avançado |
| **Leia** | a parte sobre concorrência: `@Version`, versionless, modos de lock |
| **Gratuito?** | não; **o blog do autor é gratuito e já cobre boa parte do conteúdo** ([vladmihalcea.com](https://vladmihalcea.com/optimistic-locking-version-property-jpa-hibernate/)) |

**O que faz melhor:** é o tratamento mais completo de optimistic locking **em JPA/Hibernate**
que existe, com o SQL gerado mostrado a cada caso. Se você trabalha com Java, é o livro mais
diretamente aplicável desta lista.

**Ressalva honesta:** é específico de Java. Se você não usa JPA, o blog basta.

### Fowler, Martin. *Patterns of Enterprise Application Architecture*. Addison-Wesley, 2002.

| | |
|---|---|
| **Nível** | intermediário |
| **Leia** | os padrões *Optimistic Offline Lock* e *Pessimistic Offline Lock* |
| **Gratuito?** | não; os **catálogos resumidos dos padrões estão no site do autor**, gratuitamente ([martinfowler.com](https://martinfowler.com/eaaCatalog/)) |
| **Português?** | *Padrões de Arquitetura de Aplicações Corporativas*, Bookman |

**O que faz melhor:** é a origem do nome "offline lock" e a melhor formulação do problema
**do ponto de vista de arquitetura de aplicação**, não de banco de dados. A distinção entre
lock *offline* (entre requisições) e lock de banco (dentro da transação) é exatamente o
recorte deste curso, e Fowler a nomeou primeiro.

**Envelheceu?** O livro como um todo, bastante — os exemplos são de 2002. **Estes dois padrões,
não.** Continuam a descrição mais precisa do problema.

---

## 5. Sistemas distribuídos

### Kleppmann, Martin. *Distributed Systems* (notas de aula). University of Cambridge.

| | |
|---|---|
| **Nível** | intermediário → avançado |
| **Gratuito?** | **sim, e sob licença CC BY-SA** — [PDF, 87 páginas](https://www.cl.cam.ac.uk/teaching/2021/ConcDisSys/dist-sys-notes.pdf) |
| **Leia** | tempo lógico, replicação e o estudo de caso de software colaborativo |

Não é um livro, mas cobre o material de [`18`](18-sistemas-distribuidos.md) melhor que a
maioria dos livros, é gratuito, e vem com [8 aulas em vídeo](https://www.youtube.com/playlist?list=PLeKd45zvjcDFUEv_ohr_HdUFe97RItdiB).

### Tanenbaum, Andrew S.; van Steen, Maarten. *Distributed Systems*. 4ª edição, 2023.

| | |
|---|---|
| **Nível** | intermediário |
| **Gratuito?** | **sim** — os autores disponibilizam o PDF em <https://www.distributed-systems.net/> |
| **Leia** | os capítulos de consistência e replicação |

**O que faz melhor:** cobertura ampla e didática. Menos profundo que o Kleppmann na parte de
transações, mais completo em tópicos gerais de sistemas distribuídos.

---

## 6. O que **não** ler

Sendo direto para poupar seu tempo:

- **Livros de "receitas" de ORM** que dedicam meia página a `@Version` e não explicam nada.
  O blog do Mihalcea e a documentação da Microsoft são melhores e gratuitos.
- **Date, C. J. — *An Introduction to Database Systems*.** Excelente para modelo relacional e
  teoria; fraco e datado na parte de concorrência prática.
- **Livros de "microsserviços" que tratam consistência em duas páginas.** O assunto merece mais
  do que a menção a *saga* que costumam fazer.
- **Qualquer livro anterior a 2010 como fonte sobre a camada HTTP.** A RFC 9110 é gratuita,
  normativa e mais clara.

---

## 7. Trilha de leitura

| Objetivo | Leia, nesta ordem |
|---|---|
| **Base de transações** | Elmasri & Navathe (pt) **ou** Silberschatz, capítulos de transações |
| **Aplicar bem** | Kleppmann DDIA cap. 7 → Fowler (os dois padrões) → Mihalcea (se Java) |
| **Entender a fundo** | DDIA completo → Bernstein (gratuito) cap. 4 → Kleppmann notas de sistemas distribuídos |
| **Pesquisar** | Bernstein → Weikum & Vossen → os papers de [`95`](95-referencias.md) |

**Custo total da trilha "entender a fundo": o preço de um livro (DDIA).** Todo o resto é
legalmente gratuito.

---

## Autoteste

1. Qual livro comprar, se for comprar apenas um? Qual capítulo ler primeiro?
2. Que clássico está legalmente disponível de graça, e por quê?
3. Onde a validação otimista é explicada de forma mais didática, e onde de forma mais formal?
4. Qual é a melhor opção **em português** para os fundamentos?
5. O que Fowler nomeou, e por que esse recorte importa para este curso?
6. Por que não usar livro anterior a 2010 como fonte sobre a camada HTTP?

---

## Fontes consultadas (14/08/2026)

- [Martin Kleppmann — anúncio da 2ª edição de DDIA (24/03/2026)](https://martin.kleppmann.com/2026/03/24/designing-data-intensive-applications-2e.html)
- [O'Reilly — *Designing Data-Intensive Applications*, 2ª edição](https://www.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/)
- [ScyllaDB — oferta patrocinada do livro](https://lp.scylladb.com/designing-data-intensive-apps-book-offer)
- [Bernstein, Hadzilacos & Goodman — PDF liberado pelos autores](http://research.microsoft.com/pubs/ccontrol/) · [Internet Archive](https://archive.org/details/concurrencycontr0000bern) · [registro dblp/SIGMOD](https://www.sigmod.org/publications/dblp/db/books/dbtext/bernstein87.html)
- [db-book.com — site oficial de *Database System Concepts*, 7ª ed.](https://www.db-book.com/)
- [Yale/Silberschatz — página do livro](https://codex.cs.yale.edu/avi/db-book/index.html)
- [McGraw-Hill — página do produto](https://www.mheducation.com/highered/product/database-system-concepts-silberschatz.html)
- [Kleppmann — notas de Distributed Systems (CC BY-SA)](https://www.cl.cam.ac.uk/teaching/2021/ConcDisSys/dist-sys-notes.pdf)
- [Tanenbaum & van Steen — distributed-systems.net](https://www.distributed-systems.net/)
- [Martin Fowler — catálogo de padrões do PoEAA](https://martinfowler.com/eaaCatalog/)
- [Vlad Mihalcea — blog](https://vladmihalcea.com/optimistic-locking-version-property-jpa-hibernate/)
