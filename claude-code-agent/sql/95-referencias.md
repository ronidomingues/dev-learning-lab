# 95 — Referências

Data: 13/08/2026 · Specs, papers, documentação, código-fonte e pessoas

Tudo aqui é verificável. Onde não consegui confirmar um dado, digo.

---

## 1. O padrão

### ISO/IEC 9075 — Database languages — SQL

O padrão é dividido em partes. As que importam:

| Parte | Título | Nota |
|---|---|---|
| 9075-1 | Framework (SQL/Framework) | <https://www.iso.org/standard/76583.html> |
| 9075-2 | Foundation (SQL/Foundation) | O núcleo — a maior e a que importa |
| 9075-4 | Persistent Stored Modules (SQL/PSM) | Procedimentos |
| 9075-11 | Information and Definition Schemas | `information_schema` |
| 9075-13 | Java Routines (SQL/JRT) | |
| 9075-14 | XML-Related Specifications (SQL/XML) | |
| **9075-16** | **Property Graph Queries (SQL/PGQ)** | Novo no SQL:2023 — <https://www.iso.org/standard/79473.html> |

**Correção técnica de 2026:** ISO/IEC 9075-16:2023/Cor 1:2026, publicada em
agosto de 2026 — <https://www.iso.org/standard/93698.html>

⚠️ **O padrão é pago** (ordem de CHF 200 por parte). Alternativas legítimas e
gratuitas:

- **Rascunhos finais (working drafts)**, praticamente idênticos ao texto
  publicado, compilados em <https://modern-sql.com/standard> — mantido por
  Markus Winand. É a melhor porta de entrada.
- **GQL** (ISO/IEC 39075:2024), a linguagem irmã para grafos.

### Onde ver o que cada banco implementa

- PostgreSQL: <https://www.postgresql.org/docs/current/features.html> — lista
  explicitamente os recursos do padrão suportados e não suportados. Raro e
  louvável.
- <https://modern-sql.com> — matriz de compatibilidade por recurso, entre
  bancos. **A ferramenta mais útil desta seção.**

---

## 2. Papers seminais

### Fundação

**Codd, E. F.** *A Relational Model of Data for Large Shared Data Banks*.
Communications of the ACM, 13(6):377–387, junho de 1970.
<https://dl.acm.org/doi/10.1145/362384.362685>
> As onze páginas que fundaram o campo. Legível para quem tem matemática de
> engenharia. Leia pelo menos as três primeiras seções.

**Codd, E. F.** *Relational Completeness of Data Base Sublanguages*. IBM
Research Report RJ987, 1972.
> Define o critério de completude relacional.

**Codd, E. F.** *Extending the Database Relational Model to Capture More
Meaning*. ACM TODS, 4(4), 1979.
> Onde Codd trata de `NULL` e propõe **dois** marcadores distintos —
> "não se aplica" e "desconhecido". O comitê aprovou um só. Este paper é a
> origem histórica da crítica ao `NULL` do SQL.

### Linguagem

**Chamberlin, D. D.; Boyce, R. F.** *SEQUEL: A Structured English Query
Language*. SIGFIDET 1974.
> O nascimento da linguagem. O "English" no título explica a sintaxe que você
> escreve hoje.

**Chamberlin, D. D.** *Early History of SQL*. IEEE Annals of the History of
Computing, 34(4), 2012.
> Relato de primeira mão, quarenta anos depois. Excelente e acessível.

### Otimização

**Selinger, P. G.; Astrahan, M. M.; Chamberlin, D. D.; Lorie, R. A.; Price,
T. G.** *Access Path Selection in a Relational Database Management System*.
SIGMOD 1979.
> O artigo que definiu como todo otimizador funciona até hoje: programação
> dinâmica, modelo de custo, ordens interessantes. Ainda é leitura obrigatória.

**Leis, V. et al.** *How Good Are Query Optimizers, Really?* PVLDB 9(3), 2015.
<https://www.vldb.org/pvldb/vol9/p204-leis.pdf>
> O estudo experimental que mostrou que **estimativa de cardinalidade** é a
> fonte dominante de erro. Mudou a agenda de pesquisa da área.

### Complexidade e junções

**Chandra, A. K.; Merlin, P. M.** *Optimal Implementation of Conjunctive
Queries in Relational Data Bases*. STOC 1977.
> Contenção de consultas conjuntivas é NP-completa.

**Atserias, A.; Grohe, M.; Marx, D.** *Size Bounds and Query Plans for
Relational Joins*. FOCS 2008.
> A cota AGM. Base teórica dos algoritmos ótimos de junção.

**Ngo, H. Q.; Porat, E.; Ré, C.; Rudra, A.** *Worst-case Optimal Join
Algorithms*. PODS 2012.
> O primeiro algoritmo a atingir a cota AGM.

**Veldhuizen, T. L.** *Leapfrog Triejoin: A Simple, Worst-Case Optimal Join
Algorithm*. ICDT 2014.
> A versão prática, implementada em produtos.

### Transações e concorrência

**Gray, J.; Lorie, R.; Putzolu, G.; Traiger, I.** *Granularity of Locks and
Degrees of Consistency in a Shared Data Base*. IBM, 1976.
> Origem dos níveis de isolamento. Jim Gray ganhou o Turing Award em 1998.

**Berenson, H.; Bernstein, P.; Gray, J.; Melton, J.; O'Neil, E.; O'Neil, P.**
*A Critique of ANSI SQL Isolation Levels*. SIGMOD 1995.
<https://arxiv.org/abs/cs/0701157>
> Mostra que as definições do padrão são ambíguas e que *snapshot isolation*
> não corresponde a nenhum nível do ANSI. **Leitura essencial** para quem
> trabalha com concorrência.

**Cahill, M. J.; Röhm, U.; Fekete, A. D.** *Serializable Isolation for
Snapshot Databases*. SIGMOD 2008.
> SSI — o que o PostgreSQL implementa desde a 9.1 no nível `SERIALIZABLE`.

**Fischer, M. J.; Lynch, N. A.; Paterson, M. S.** *Impossibility of
Distributed Consensus with One Faulty Process*. JACM 32(2), 1985.
> O resultado FLP.

**Gilbert, S.; Lynch, N.** *Brewer's Conjecture and the Feasibility of
Consistent, Available, Partition-Tolerant Web Services*. ACM SIGACT News,
33(2), 2002.
> A prova formal do teorema CAP.

**Abadi, D.** *Consistency Tradeoffs in Modern Distributed Database System
Design* (PACELC). IEEE Computer, 45(2), 2012.
> Refinamento do CAP que descreve melhor os sistemas reais.

### Arquitetura

**Hellerstein, J. M.; Stonebraker, M.; Hamilton, J.** *Architecture of a
Database System*. Foundations and Trends in Databases, 1(2), 2007.
<https://dsf.berkeley.edu/papers/fntdb07-architecture.pdf> 📖
> ~120 páginas, gratuito. A melhor visão geral concisa que existe.

**Stonebraker, M.; Çetintemel, U.** *"One Size Fits All": An Idea Whose Time
Has Come and Gone*. ICDE 2005.
> O argumento de que bancos especializados vencem os generalistas. **Vale ler
> em 2026 contra a tendência de "PostgreSQL maximalismo"** — a história deu
> razão parcial aos dois lados.

### Colunar e analítico

**Boncz, P.; Zukowski, M.; Nes, N.** *MonetDB/X100: Hyper-Pipelining Query
Execution*. CIDR 2005.
> A execução vetorizada. Base intelectual do DuckDB, cujos autores vêm do mesmo
> grupo (CWI, Amsterdã).

**Raasveldt, M.; Mühleisen, H.** *DuckDB: an Embeddable Analytical Database*.
SIGMOD 2019 (demo).
> O artigo do DuckDB.

### Texto natural → SQL

**Yu, T. et al.** *Spider: A Large-Scale Human-Labeled Dataset for Complex and
Cross-Domain Semantic Parsing and Text-to-SQL Task*. EMNLP 2018.

**Li, J. et al.** *Can LLM Already Serve as A Database Interface? A BIg Bench
for Large-Scale Database Grounded Text-to-SQLs* (BIRD). NeurIPS 2023.
> As duas bancadas de referência. Os números de 2026 estão em
> [65-estado-da-arte.md](65-estado-da-arte.md).

---

## 3. Documentação oficial

| Produto | Endereço |
|---|---|
| PostgreSQL | <https://www.postgresql.org/docs/current/> |
| SQLite | <https://sqlite.org/docs.html> |
| — *Quirks, Caveats and Gotchas* | <https://sqlite.org/quirks.html> |
| — *Query Optimizer Overview* | <https://sqlite.org/optoverview.html> |
| — *STRICT tables* | <https://sqlite.org/stricttables.html> |
| — *Write-Ahead Logging* | <https://sqlite.org/wal.html> |
| — *Appropriate Uses For SQLite* | <https://sqlite.org/whentouse.html> |
| DuckDB | <https://duckdb.org/docs/> |
| MySQL | <https://dev.mysql.com/doc/> |
| Oracle | <https://docs.oracle.com/en/database/> |
| SQL Server (T-SQL) | <https://learn.microsoft.com/sql/t-sql/> |
| TimescaleDB | <https://docs.timescale.com/> |
| **AVEVA PI SQL Client (OLE DB)** | <https://docs.aveva.com/bundle/pi-sql-client-oledb/page/1014303.html> |
| **AVEVA PI SQL Client (ODBC)** | <https://docs.aveva.com/bundle/pi-sql-client-odbc/page/1014381.html> |
| **PI OLEDB Enterprise** | <https://docs.aveva.com/bundle/pi-oledb-enterprise/page/1015809.html> |

---

## 4. Código-fonte

Ler o código de um banco é a forma definitiva de tirar dúvida sobre
comportamento.

| Projeto | Onde | Nota |
|---|---|---|
| **SQLite** | <https://sqlite.org/src/> (Fossil) e espelho em <https://github.com/sqlite/sqlite> | Domínio público. **Cobertura de teste de 100% de ramificações** — a suíte tem mais de 600× o tamanho do código |
| **PostgreSQL** | <https://git.postgresql.org/> · <https://github.com/postgres/postgres> | Código C exemplarmente comentado. `src/backend/optimizer/README` é material didático |
| **DuckDB** | <https://github.com/duckdb/duckdb> | C++ moderno, legível |

---

## 5. Normas técnicas de processo citadas neste curso

| Norma | O que define | Onde aparece |
|---|---|---|
| **ISA-5.1** | Símbolos e identificação de instrumentação (a nomenclatura `TI-101`) | [projeto-modelo](07-projeto-modelo/), [30](30-engenharia-quimica.md) |
| **ISA-88** (IEC 61512) | Controle de batelada: modelo físico, receita, fase | [18](18-series-temporais.md), [30](30-engenharia-quimica.md) |
| **ISA-95** (IEC 62264) | Integração entre empresa e controle; a hierarquia de níveis | [30](30-engenharia-quimica.md) §1 |
| **ISA-18.2** (IEC 62682) | Gestão do ciclo de vida de sistemas de alarme | [30](30-engenharia-quimica.md) §6 |
| **EEMUA 191** | Sistemas de alarme: projeto, gestão e aquisição (a meta de ~6 alarmes/h) | idem |
| **21 CFR Part 11** (FDA) | Registros e assinaturas eletrônicas | [06](06-exemplos.md) exemplo 13 |

⚠️ Todas são **pagas**, adquiridas pela ISA, IEC, EEMUA ou ABNT. Resumos
públicos e artigos técnicos costumam ser suficientes para entender os
conceitos; para conformidade, é preciso o texto.

---

## 6. Pessoas para acompanhar

| Pessoa | Por quê | Onde |
|---|---|---|
| **Markus Winand** | Índices e SQL moderno. Escreve melhor que qualquer livro sobre o assunto | <https://use-the-index-luke.com>, <https://modern-sql.com> |
| **Hubert "depesz" Lubaczewski** | Série "Waiting for PostgreSQL" — o que vem na próxima versão, explicado | <https://www.depesz.com> |
| **Bruce Momjian** | Veterano do PostgreSQL; palestras excelentes sobre MVCC e internos | <https://momjian.us/main/presentations/> |
| **D. Richard Hipp** | Autor do SQLite; entrevistas e palestras sobre por que o SQLite é como é | busque "Richard Hipp SQLite" |
| **Martin Kleppmann** | Sistemas distribuídos, transações, CRDTs | <https://martin.kleppmann.com> |
| **Andy Pavlo** (CMU) | 📖 **Curso completo de bancos de dados no YouTube, gratuito** — CMU 15-445 e 15-721. Nível de pós-graduação | <https://15445.courses.cs.cmu.edu> |
| **Hannes Mühleisen / Mark Raasveldt** | Autores do DuckDB | <https://duckdb.org/news/> |

**A recomendação da seção:** o curso **CMU 15-445 (Database Systems)** do Andy
Pavlo está inteiro no YouTube, com slides e trabalhos, gratuitamente. É
equivalente a uma disciplina de pós-graduação e é a melhor coisa gratuita que
existe sobre internos de bancos de dados.

---

## 7. Ferramentas

| Ferramenta | Para quê | Licença |
|---|---|---|
| **DB Browser for SQLite** | Interface gráfica para SQLite | GPLv3/MPL2 |
| **DBeaver Community** | Cliente multi-banco | Apache 2.0 |
| **pgAdmin 4** | PostgreSQL | PostgreSQL |
| **explain.dalibo.com** | Visualizar plano do PostgreSQL (processa no navegador) | Gratuito |
| **SQLFluff** | *Linter* e formatador de SQL | MIT |
| **dbt Core** | Transformação em SQL, com testes e documentação | Apache 2.0 |
| **pgTAP** | Testes unitários dentro do PostgreSQL | — |
| **Flyway / Liquibase / Alembic** | Migrações versionadas de esquema | Versão básica gratuita |
| **Metabase / Apache Superset** | BI open-source | AGPL / Apache 2.0 |
| **sqlime.org** · **sqliteonline.com** · **shell.duckdb.org** | SQL no navegador | Gratuitos |

---

## 8. Verificação deste curso

O que foi **executado** na produção deste material, em 13/08/2026, em
Ubuntu 22.04.5 LTS / Python 3.10.12 / SQLite 3.37.2 / DuckDB 1.5.5:

- O [projeto-modelo](07-projeto-modelo/) inteiro: geração de 344.640 leituras,
  as 14 consultas de análise e os **31 testes** (todos passando).
- Todos os exemplos de [04-como-comecar.md](04-como-comecar.md), incluindo as
  cinco mensagens de erro literais.
- Os 15 exemplos de [06-exemplos.md](06-exemplos.md).
- As medições de índice e de plano de [21](21-indices-e-desempenho.md).
- A medição de transação de [20](20-dml-e-transacoes.md): 131,50 s × 0,03 s.
- As semânticas de tipo e `NULL` de [17](17-tipos-e-nulos.md).
- O comportamento de moldura de janela de [16](16-funcoes-de-janela.md).
- As soluções dos laboratórios 4, 7 e 8 de [70](70-pratica.md).
- O erro de glibc do binário oficial do SQLite, em
  [03-instalacao.md](03-instalacao.md).

O que **não** foi executado, e está declarado no ponto:
instalação em Windows e macOS; PostgreSQL (nenhum servidor disponível no
ambiente de escrita); Docker; os 12 laboratórios de
[70-pratica.md](70-pratica.md) como enunciados; consultas ao PI System.

---

*Fim do bloco de fontes. Volte ao [00-MAPA.md](00-MAPA.md).*
