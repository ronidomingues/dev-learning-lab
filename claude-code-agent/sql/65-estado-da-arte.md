# 65 — Estado da arte

Nível: avançado → pesquisa · **Data: 13/08/2026** · Este arquivo envelhece rápido

Tudo aqui tem data. Reavalie em fevereiro de 2027.

---

## 1. O padrão

**SQL:2023** (ISO/IEC 9075) é a edição vigente. O que trouxe:

- **SQL/PGQ** (Parte 16) — consultas em grafo de propriedades dentro do SQL:
  `CREATE PROPERTY GRAPH`, e a função de tabela `GRAPH_TABLE` com casamento de
  padrão de caminho.
- Tipo **`JSON`** nativo (antes era texto com funções).
- `UNIQUE NULLS [NOT] DISTINCT` — resolve a velha ambiguidade de vários `NULL`
  numa coluna `UNIQUE`.
- Melhorias em `MATCH_RECOGNIZE` (reconhecimento de padrão em linhas).

**Novidade de 2026:** a **ISO/IEC 9075-16:2023/Cor 1:2026**, correção técnica
ao SQL/PGQ, foi publicada em **agosto de 2026** — sinal de que a
implementação real está começando a expor os problemas do texto.

**Implementação:** o PostgreSQL está trabalhando em SQL/PGQ para a **versão
19** — a `commitfest` de julho de 2026 tem o patch com `CREATE/ALTER/DROP
PROPERTY GRAPH`, `GRAPH_TABLE` e os catálogos de sistema. Não está em nenhuma
versão estável no momento em que escrevo. Bancos de grafo (Neo4j, TigerGraph)
convergiram para o **GQL** (ISO/IEC 39075:2024), que é a linguagem irmã e
independente.

---

## 2. Versões atuais (13/08/2026)

| Produto | Versão | Notas |
|---|---|---|
| **PostgreSQL** | **18.6** (série 18 desde 25/09/2025) | Novo subsistema de E/S assíncrona, com ganhos medidos de até 3× em leitura de disco |
| **SQLite** | **3.53.4** (24/07/2026) | Patch com correções de defeitos majoritariamente **descobertos por IA** — sinal dos tempos |
| **DuckDB** | **1.5.5** | Série 1.5 desde 09/03/2026; escrita completa em Iceberg desde a 1.4 |
| **MySQL** | 8.4 LTS / 9.x | |
| **Oracle** | 23ai / 26ai | Vetor nativo; `BOOLEAN` finalmente |
| **SQL Server** | 2025 | Preço de lista inalterado desde 2022 |

---

## 3. As cinco tendências que importam

### 3.1 "PostgreSQL maximalismo"

A tendência mais forte de 2024–2026: em vez de adotar um banco especializado
por problema, **estender o PostgreSQL**.

| Necessidade | Extensão |
|---|---|
| Série temporal | TimescaleDB |
| Busca vetorial | pgvector, pgvectorscale |
| Colunar/analítico | pg_duckdb, pg_mooncake, pg_analytics |
| Geoespacial | PostGIS |
| Fila de mensagens | pgmq |
| Busca textual | pg_search / ParadeDB |

**Por que está vencendo:** um banco para operar, uma linguagem, transações
consistentes entre os domínios, e nenhuma sincronização entre sistemas.

**A crítica honesta:** extensão não é núcleo. Você depende de o mantenedor
acompanhar cada versão maior do PostgreSQL, o suporte gerenciado na nuvem pode
não oferecer a extensão que você quer, e "um banco para tudo" tem limite real
— ninguém roda 500 TB de série temporal em Postgres puro.

### 3.2 Formatos abertos: o Iceberg venceu

**Apache Iceberg** consolidou-se como o formato de tabela do *lakehouse*.
Microsoft Fabric, Oracle 26ai, Snowflake e Databricks oferecem leitura e
escrita nativas; o DuckDB ganhou escrita completa (`INSERT`/`UPDATE`/`DELETE`)
na 1.4.

**O significado estratégico:** o dado deixa de morar dentro do produto. Você
guarda em Parquet + Iceberg no seu próprio armazenamento de objetos e aponta
**vários** motores para ele — DuckDB, Spark, Trino, Snowflake. Isso reduz o
aprisionamento de fornecedor de forma real, e é a mudança arquitetural mais
importante da década para quem tem dado grande.

Novidade adjacente: **DuckLake 1.0**, formato que guarda os metadados do
lakehouse **num banco SQL** em vez de arquivos, já em versão de produção.

**Para engenheiro químico:** se sua planta exporta anos de histórico,
**Parquet é a resposta**, não CSV. Medido neste curso: 13,3 MB → **3,3 MB**,
com tipos preservados e consultas ~7× mais rápidas.

### 3.3 Busca vetorial deixou de ser um mercado

A história de 2026: **bancos de propósito geral com suporte a vetor comeram a
carga de trabalho dos bancos vetoriais dedicados**, exceto na escala de
bilhões. PostgreSQL + pgvector, Oracle 26ai, MongoDB, SQL Server — todos com
vetor nativo.

Os bancos vetoriais dedicados (Pinecone, Qdrant, Weaviate) estreitaram para
nichos de altíssima escala e latência.

**Onde isso toca a indústria de processo:** busca semântica em procedimentos
operacionais, relatórios de incidente e ordens de manutenção — encontrar "casos
parecidos com este" em texto livre. É uma aplicação real e pouco explorada.

### 3.4 Texto natural → SQL

O tema mais superestimado e mais interessante ao mesmo tempo. Os números de
2026:

| Bancada | Melhor resultado | Humano |
|---|---|---|
| **BIRD** (bancos reais, valores reais) | **~81,9%** de execução correta | ~93% |
| **Spider** (esquemas limpos, acadêmicos) | mais alto | — |
| **BIRD-Ent / Spider-Ent** (esquemas *empresariais* reais) | **39,1%** e **60,5%** | — |

**A leitura correta desses números:** em esquema limpo e pergunta bem-posta, os
modelos vão muito bem. Em **esquema corporativo real** — 800 tabelas, nomes
como `MSEG` e `AUFK`, regras de negócio que não estão em lugar nenhum, colunas
com significado histórico — a acurácia **cai para 39%**.

E 39% é um número perigoso, não um número ruim: **a consulta roda e devolve um
número plausível.** Não dá erro. Não avisa. Vai para o slide.

**Consequência para você:** a habilidade que ganha valor não é escrever SQL —
é **ler, auditar e validar** SQL que alguém (ou algo) escreveu, e saber se o
número faz sentido físico. Isso é exatamente o que um engenheiro de processo
tem e a ferramenta não tem.

**Minha opinião profissional, declarada como opinião:** em 2030, a maioria do
SQL de análise será gerada, e a maioria dos erros de análise também. Quem
souber conferir vai valer mais, não menos.

### 3.5 Otimização aprendida e adaptativa

Estimativa de cardinalidade por aprendizado de máquina (Neo, Bao, Balsa) e
otimização adaptativa (corrigir o plano durante a execução). **Estado de
adoção em 2026:** pesquisa ativa, produção limitada. Funciona bem em carga
repetitiva; é arriscado em consulta nova, e a regressão de desempenho é pior
que a estimativa ruim que ela substitui.

Ver [60-teoria-avancada.md](60-teoria-avancada.md) §5.

---

## 4. O que estagnou, e por quê

| Coisa | Estado |
|---|---|
| **NoSQL como substituto do SQL** | Acabou. Sobreviveu como nicho legítimo (cache, documento, grafo) e os sobreviventes adotaram SQL |
| **Bancos NewSQL distribuídos** | CockroachDB, TiDB, YugabyteDB são bons e caros; a maioria dos projetos descobriu que não precisava |
| **Consulta sobre dado criptografado** | Criptografia homomórfica continua impraticável para consulta geral; enclaves são o compromisso |
| **Índices aprendidos** (Kraska 2018) | Não substituíram B-trees em produção |
| ***Worst-case optimal joins*** | Adoção lenta; presente em DuckDB e sistemas de grafo, ausente em Postgres/Oracle. Um resultado de 2012 ainda não absorvido |
| **XML em bancos** | Morto. Substituído por JSON |
| **Tabelas temporais do SQL:2011** | Adoção parcial (SQL Server, Oracle, DB2, MariaDB); PostgreSQL e SQLite não têm |

---

## 5. Especificamente para dado de processo industrial

| Tendência | Onde está em 2026 |
|---|---|
| Historiadores abrindo para SQL/API | Todos os grandes têm camada SQL ou REST; a qualidade varia muito |
| Analítica de série temporal self-service | Seeq e TrendMiner consolidados; caros; não resolvem a junção com LIMS/ERP |
| **Unified Namespace (UNS) / MQTT Sparkplug** | Ganhando espaço como alternativa ao historiador monolítico |
| TimescaleDB para historiador aberto | Viável e usado; ainda minoria em planta grande |
| Parquet + Iceberg para histórico frio | Tendência clara; barato e sem aprisionamento |
| *Soft sensors* e modelos de qualidade | Cresce; depende inteiramente de contexto de batelada bem modelado — **e é aí que o SQL entra** |
| IA generativa em operação | Muito piloto, pouca produção. Onde funciona: sumarizar incidente, buscar procedimento, gerar rascunho de relatório |

**Onde está o valor não capturado, na minha avaliação:** não é em modelo. É em
**contexto**. A maioria das plantas tem dez anos de série temporal e nenhuma
forma confiável de dizer, para uma leitura de 2019, qual batelada, qual lote de
matéria-prima, qual receita e qual operador estavam ativos. Sem isso, nenhum
modelo funciona — e resolver isso é modelagem de dados e SQL, não ciência de
dados.

---

## 6. O que provavelmente **não** vai mudar

Previsão com prazo, para poder ser cobrada:

1. **O SQL continuará sendo a interface até pelo menos 2035.** Inércia de
   ecossistema, não superioridade técnica.
2. **`NULL` e a lógica de três valores não serão consertados.** Quebraria
   compatibilidade com tudo.
3. **O modelo relacional continuará sendo o padrão para dado estruturado.**
   Cinquenta e seis anos e quatro ondas de substituição depois.
4. **Estimativa de cardinalidade continuará sendo o ponto fraco** dos
   otimizadores.
5. **O padrão continuará sendo pago**, e continuará sendo estranho que a
   especificação de uma linguagem usada por milhões custe centenas de francos.

---

## Autoteste

1. O que o SQL:2023 trouxe de novo, e qual parte ainda não está implementada em
   PostgreSQL estável?
2. O que é "PostgreSQL maximalismo"? Qual a crítica honesta?
3. Por que o Iceberg vencer importa estrategicamente?
4. O que aconteceu com o mercado de bancos vetoriais em 2026?
5. Texto→SQL: por que 81,9% em BIRD e 39,1% em BIRD-Ent, e por que 39% é
   perigoso e não apenas ruim?
6. Qual habilidade ganha valor com a geração automática de SQL?
7. Cite três coisas que estagnaram e a razão de cada uma.
8. Onde está o valor não capturado em dado de processo industrial?

---

## Fontes consultadas (13/08/2026)

- ISO/IEC 9075-16:2023/Cor 1:2026 — <https://www.iso.org/standard/93698.html>
- SQL/PGQ no PostgreSQL 19 — <https://www.depesz.com/2026/07/31/waiting-for-postgresql-19-sql-property-graph-queries-sql-pgq/>
- PostgreSQL 18.6 e notas de versão — <https://www.postgresql.org/docs/release/>
- SQLite 3.53.4 (24/07/2026) — <https://sqlite.org/changes.html>
- DuckDB 1.5 e ecossistema — <https://duckdb.org/2026/03/09/announcing-duckdb-150>, <https://motherduck.com/blog/duckdb-ecosystem-newsletter-april-2026/>
- BIRD e a lacuna empresarial — <https://beancount.io/bean-labs/research-logs/2026/06/06/bird-benchmark-text-to-sql-real-database-gap> e <https://openreview.net/forum?id=gXkIkSN2Ha>
- Panorama de bancos vetoriais 2026 — <https://suparbase.com/blog/vector-databases-ranked-2026>
- Historiadores e analítica industrial — pesquisa web em 13/08/2026

---

*Próximo: [70-pratica.md](70-pratica.md).*
