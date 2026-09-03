# 95 · Referências — docs, specs, código, pessoas

`Nível: todos` · `Última atualização: 11/08/2026`

Fontes primárias e verificáveis. Preferência por documentação oficial, código e artigos sobre
posts de blog. Onde cito fonte secundária, digo que é isso.

---

## 1. Documentação e site oficial

| Recurso | URL |
|---|---|
| **Documentação oficial** (a fonte de verdade) | [postgresql.org/docs](https://www.postgresql.org/docs/current/) |
| Tutorial oficial | [postgresql.org/docs/current/tutorial.html](https://www.postgresql.org/docs/current/tutorial.html) |
| Notas de versão | [postgresql.org/docs/release](https://www.postgresql.org/docs/release/) |
| PostgreSQL 18 release notes | [postgresql.org/docs/18/release-18.html](https://www.postgresql.org/docs/18/release-18.html) |
| Política de versões e suporte | [postgresql.org/support/versioning](https://www.postgresql.org/support/versioning/) |
| Licença | [postgresql.org/about/licence](https://www.postgresql.org/about/licence/) |
| Downloads | [postgresql.org/download](https://www.postgresql.org/download/) |
| Wiki | [wiki.postgresql.org](https://wiki.postgresql.org) |
| Listas de discussão (o coração do desenvolvimento) | [postgresql.org/list](https://www.postgresql.org/list/) |

A documentação do PostgreSQL é referência de qualidade na indústria. A `SELECT` reference, a
`CREATE INDEX`, os capítulos sobre MVCC, WAL e o planejador valem mais que a maioria dos tutoriais.

---

## 2. Código-fonte e desenvolvimento

| Recurso | URL |
|---|---|
| Código-fonte (git oficial) | [git.postgresql.org](https://git.postgresql.org/gitweb/?p=postgresql.git) |
| Espelho no GitHub | [github.com/postgres/postgres](https://github.com/postgres/postgres) |
| Commitfest (revisão de patches) | [commitfest.postgresql.org](https://commitfest.postgresql.org) |
| pgpedia (enciclopédia de versões/recursos) | [pgpedia.info](https://pgpedia.info) |

O PostgreSQL é desenvolvido por listas de e-mail e commitfests, não por pull requests — um processo
incomum e rigoroso que explica a qualidade e a estabilidade do projeto.

---

## 3. Extensões mencionadas

| Extensão | URL |
|---|---|
| **pgvector** | [github.com/pgvector/pgvector](https://github.com/pgvector/pgvector) |
| **pgvectorscale** | [github.com/timescale/pgvectorscale](https://github.com/timescale/pgvectorscale) |
| **PostGIS** | [postgis.net](https://postgis.net) |
| **TimescaleDB** | [github.com/timescale/timescaledb](https://github.com/timescale/timescaledb) |
| **Citus** | [github.com/citusdata/citus](https://github.com/citusdata/citus) |
| **pg_stat_statements**, **pg_trgm**, **pgcrypto** | contrib (na documentação oficial) |
| **PGXN** (rede de extensões) | [pgxn.org](https://pgxn.org) |

---

## 4. Ferramentas mencionadas

| Ferramenta | O que faz | URL |
|---|---|---|
| **psql** | Cliente de terminal | vem com o PostgreSQL |
| **pgAdmin** | GUI oficial | [pgadmin.org](https://www.pgadmin.org) |
| **DBeaver** | GUI universal | [dbeaver.io](https://dbeaver.io) |
| **pgBackRest** | Backup e PITR robusto | [pgbackrest.org](https://pgbackrest.org) |
| **Barman**, **WAL-G** | Backup / arquivamento de WAL | vários |
| **PgBouncer** | Pool de conexões | [pgbouncer.org](https://www.pgbouncer.org) |
| **Patroni** | Alta disponibilidade / failover | [github.com/patroni/patroni](https://github.com/patroni/patroni) |
| **pgtune** | Gerar configuração inicial | [pgtune.leopard.in.ua](https://pgtune.leopard.in.ua) |
| **postgres_exporter** | Métricas para Prometheus | [github.com/prometheus-community/postgres_exporter](https://github.com/prometheus-community/postgres_exporter) |
| **ora2pg** | Migrar de Oracle | [ora2pg.darold.net](https://ora2pg.darold.net) |

---

## 5. Artigos acadêmicos (fundamentos)

Referenciados em [60-teoria-avancada.md](60-teoria-avancada.md):

- **Codd, E. F.** (1970). *A Relational Model of Data for Large Shared Data Banks.* CACM 13(6). — o
  artigo fundador.
- **Codd, E. F.** (1972). *Relational Completeness of Data Base Sublanguages.* — o teorema álgebra ≡
  cálculo.
- **Chamberlin, D. & Boyce, R.** (1974). *SEQUEL: A Structured English Query Language.* — a origem
  do SQL.
- **Selinger, P. et al.** (1979). *Access Path Selection in a Relational Database Management
  System.* SIGMOD. — a otimização baseada em custo.
- **Stonebraker, M. & Rowe, L.** (1986). *The Design of POSTGRES.* — o projeto original; a tese da
  extensibilidade.
- **Gilbert, S. & Lynch, N.** (2002). *Brewer's Conjecture and the Feasibility of Consistent,
  Available, Partition-Tolerant Web Services.* — a prova do CAP.
- **Cahill, M., Röhm, U., Fekete, A.** (2008). *Serializable Isolation for Snapshot Databases.*
  SIGMOD. — a base do SSI do PostgreSQL.
- **Abadi, D.** (2012). *Consistency Tradeoffs in Modern Distributed Database System Design.* IEEE
  Computer. — PACELC.

Muitos estão em [dl.acm.org](https://dl.acm.org) e em cópias abertas dos autores.

---

## 6. Blogs e fontes secundárias (marcados como tais)

Úteis, mas **secundários** — verifique contra a documentação oficial:

| Fonte | Perfil |
|---|---|
| [Crunchy Data blog](https://www.crunchydata.com/blog) | Prático, atualizado, alta qualidade |
| [Cybertec blog](https://www.cybertec-postgresql.com/en/blog/) | Tuning, recursos avançados |
| [EDB blog](https://www.enterprisedb.com/blog) | Recursos, empresarial |
| [Neon blog](https://neon.com/blog) | Serverless, recursos novos |
| [Depesz (Hubert Lubaczewski)](https://www.depesz.com) | Análise técnica profunda; o `explain.depesz.com` |
| [pganalyze blog](https://pganalyze.com/blog) | Desempenho, planejador |
| [Planet PostgreSQL](https://planet.postgresql.org) | Agregador dos blogs da comunidade |
| [use-the-index-luke.com](https://use-the-index-luke.com) | Markus Winand, índices — quase primário |

---

## 7. Pessoas a seguir (fatos públicos, papel profissional conhecido)

| Pessoa | Por quê |
|---|---|
| **Bruce Momjian** | Cofundador; apresentações didáticas sobre internals |
| **Tom Lane** | Um dos maiores contribuidores; autoridade no planejador |
| **Michael Stonebraker** | Criador do POSTGRES (contexto histórico) |
| **Egor Rogov** | Autor de *PostgreSQL Internals* |
| **Markus Winand** | Autoridade em índices e desempenho de SQL |
| **Dimitri Fontaine** | *The Art of PostgreSQL*; contribuidor |
| **Regina Obe & Leo Hsu** | PostGIS e *Up and Running* |
| **Andres Freund** | Desempenho, I/O assíncrona do PG 18 (e famoso por achar o backdoor do xz em 2024) |
| **Melanie Plageman, Peter Geoghegan** | Contribuidores atuais (VACUUM, índices, AIO) |

---

## 8. Comunidades

| Comunidade | Onde |
|---|---|
| Listas de discussão oficiais | [postgresql.org/list](https://www.postgresql.org/list/) |
| Slack da comunidade | [pgtreats.info/slack](https://pgtreats.info) / postgres-slack |
| r/PostgreSQL | [reddit.com/r/PostgreSQL](https://www.reddit.com/r/PostgreSQL/) |
| Stack Overflow | tag `postgresql` |
| DBA Stack Exchange | [dba.stackexchange.com](https://dba.stackexchange.com) |
| Discord/fóruns em PT (grupos BR de PostgreSQL) | vários |

---

## 9. Como este material foi verificado

Transparência sobre a produção:

- **Versões e datas** (PostgreSQL 18 de 25/09/2025, 18.3 de 26/02/2026, recursos, preços,
  certificações): confirmadas por busca em **11/08/2026**, com as fontes citadas no rodapé de
  [03](03-instalacao.md), [11](11-historia.md), [65](65-estado-da-arte.md), [80](80-custos-e-licencas.md)
  e [85](85-cursos-e-certificacoes.md).
- **O código JavaScript do projeto-modelo** (`db.js`, `repositorio.js`, `server.js`, testes) teve a
  **sintaxe validada** (`node --check`), e a suíte **roda e pula corretamente** quando
  `DATABASE_URL` não está definida (5 testes, 0 falhas, 5 pulados) — comportamento intencional.
- ⚠️ **O SQL (`schema/*.sql`) e os testes de integração NÃO puderam ser executados contra um
  PostgreSQL real** no ambiente de escrita, porque não havia servidor Postgres instalado nem acesso
  ao Docker daemon. O SQL segue a documentação oficial do PostgreSQL 18 na data, mas **execute-o
  você mesmo** (`make subir` + `make testes` no projeto-modelo) e trate divergências como parte do
  aprendizado. O material não afirma o que não verificou.
- **Comandos de exemplo** seguem a documentação oficial vigente. Ainda assim: **rode na sua
  máquina.** Versões mudam, e um comando que "deveria funcionar" é hipótese até você executá-lo.
- **Onde uma afirmação vem de fonte secundária** (ex.: números de desempenho do pgvectorscale,
  detalhes de recursos do PG 18 vindos de blogs, preços de certificação), o texto marca isso
  explicitamente.

---

## Autoteste

1. Onde está a fonte de verdade sobre o comportamento do PostgreSQL?
2. Como o PostgreSQL é desenvolvido (pull requests? listas de e-mail?), e o que isso implica?
3. Onde você obtém, de graça, a referência sobre o interno do PostgreSQL?
4. Cite três extensões e onde encontrar seu código.
5. Qual artigo fundou o modelo relacional, e em que ano?
6. Por que os blogs listados são marcados como fonte secundária?
7. Cite três pessoas a seguir e o motivo de cada uma.
8. O que exatamente foi verificado no projeto-modelo, e o que não pôde ser?
9. Qual ferramenta gera um ponto de partida para a configuração?
10. Se um comando deste material falhar na sua máquina, o que a seção 9 sugere concluir?
