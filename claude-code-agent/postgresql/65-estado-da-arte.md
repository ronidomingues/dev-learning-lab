# 65 · Estado da arte — agosto de 2026

`Nível: pesquisa` · `Data de referência: 11/08/2026` · **Este é o arquivo que envelhece mais rápido.**

O que está estabelecido, o que está em disputa e o que é aposta. Onde uma afirmação vem de fonte
secundária ou é minha leitura, o texto diz isso.

---

## 1. O panorama em uma tabela

| Frente | Situação em ago/2026 |
|---|---|
| **Versão** | PostgreSQL 18 (25/09/2025) é a estável; série 19 em desenvolvimento |
| **Adoção** | O banco mais **desejado** e um dos mais **usados**; ~55% dos desenvolvedores o usam (Stack Overflow) |
| **IA / vetores** | pgvector + pgvectorscale tornaram o Postgres competitivo com bancos vetoriais dedicados |
| **Serverless** | Neon (adquirido pela Databricks) popularizou escala-a-zero e *branching* |
| **Distribuído** | Citus, e ofertas gerenciadas (Aurora, AlloyDB, Lakebase) |
| **Consolidação** | Tese "just use Postgres": um banco para OLTP, documentos, vetores, geo |
| **Fronteira** | I/O assíncrona, HTAP, Postgres como plataforma de IA |

---

## 2. O que o PostgreSQL 18 trouxe (2025)

Verificado nas notas de versão oficiais. As mudanças mais significativas:

- **I/O assíncrona (AIO)** — o maior avanço arquitetural. Um novo subsistema (`io_method`, com
  `io_uring` no Linux) permite ao banco disparar várias leituras sem bloquear, com melhorias
  reportadas de **2–3×** em varreduras sequenciais, *bitmap heap scans* e VACUUM. É a base de
  ganhos futuros de desempenho. Ver [17-arquitetura-interna.md](17-arquitetura-interna.md).
- **`uuidv7()` nativo** — UUIDs ordenados por tempo, resolvendo a fragmentação de índice do UUIDv4
  como chave primária. Ver [13-tipos-de-dados.md](13-tipos-de-dados.md).
- **Colunas geradas virtuais** — passam a ser o **padrão** para `GENERATED`; computadas na leitura,
  sem custo de escrita nem espaço.
- **Skip scan** em índices B-tree multicoluna — um índice `(a, b)` passa a servir consultas que
  filtram só por `b`, quando `a` tem poucos valores. Ver [14-indices.md](14-indices.md).
- **`RETURNING` com `OLD` e `NEW`** — acessar valores antigos e novos numa mesma instrução de
  escrita.
- **Autenticação OAuth** — integração com provedores de identidade modernos.
- **Upgrades de major menos disruptivos** — `pg_upgrade` mais rápido e melhor retenção de
  estatísticas após o upgrade, reduzindo o "banco lento logo após migrar".

---

## 3. A grande história: PostgreSQL virou infraestrutura de IA

O evento mais transformador da década para o PostgreSQL não veio do banco — veio dos modelos de
linguagem. E o gene da extensibilidade de 1986 (ver [11-historia.md](11-historia.md)) pagou seu
maior dividendo.

### pgvector cresceu, e o ecossistema em volta explodiu

- **pgvector** deixou de ser "a opção lenta" e virou concorrente legítimo de bancos vetoriais
  dedicados (Pinecone, Weaviate) para a maioria dos casos.
- **pgvectorscale** (da equipe da Timescale, escrito em Rust com pgrx) acrescentou o índice
  **StreamingDiskANN**, inspirado no algoritmo DiskANN da Microsoft. Fontes do setor reportam
  **latência p95 ~28× menor** e vazão **~16× maior** para busca aproximada de vizinhos, a custo
  muito menor que soluções dedicadas, quando bem configurado e auto-hospedado.

*Leitura da tendência, com fontes secundárias:* a mensagem de 2026 é que **um PostgreSQL bem
configurado iguala ou supera bancos vetoriais dedicados na maioria dos casos, reduzindo custo em
60–75%** — e, crucialmente, com os vetores **ao lado** dos dados de negócio, sob transações e SQL.
Isso não elimina os bancos vetoriais dedicados (que ainda ganham em escalas extremas e cargas
específicas), mas move o padrão: começa-se com pgvector, e só se sai dele por evidência. Trate os
números específicos como reportados, não como verificados por mim.

### Por que isso importa estrategicamente

Enquanto surgiam dezenas de bancos vetoriais novos entre 2022 e 2024, o PostgreSQL **absorveu** a
capacidade como extensão. É a validação máxima da aposta de Stonebraker: um banco *ensinável*
acompanha demandas que ninguém especificou de antemão. "Just use Postgres" deixou de ser slogan e
virou arquitetura de referência para aplicações de IA.

---

## 4. Serverless e o modelo Neon

A **Neon** reimaginou o PostgreSQL para a nuvem separando **computação de armazenamento**, o que
permite:
- **Escala a zero** — o banco "adormece" quando ocioso e você não paga computação parada. Ideal
  para desenvolvimento, ambientes de preview e cargas intermitentes.
- **Branching** — criar uma cópia instantânea do banco (como um branch de Git) para testar uma
  migração ou uma feature, e descartá-la. Muda o fluxo de trabalho de desenvolvimento.
- **Provisionamento instantâneo** — sem planejamento de capacidade.

A **Databricks adquiriu a Neon** (reportado como ~US$ 1 bilhão, em 2025) e, em 2026, lançou o
**Lakebase** — um PostgreSQL gerenciado voltado a aplicações de IA e cargas "agênticas", com a tese
de convergir dados operacionais e analíticos. *Interpretação:* as grandes plataformas de dados
passaram a ver o PostgreSQL não como um banco entre outros, mas como **a interface padrão** sobre a
qual construir — inclusive para IA. (Nota factual, verificada na busca: até meados de 2026,
**Databricks e Snowflake permanecem concorrentes independentes**; não houve aquisição de uma pela
outra, apesar de boatos recorrentes.)

*Avaliação profissional:* serverless Postgres é excelente para desenvolvimento, cargas variáveis e
projetos que valorizam branching. Para cargas constantes de alto volume 24/7, o modelo baseado em
uso pode sair mais caro que uma instância reservada — faça a conta. Ver
[80-custos-e-licencas.md](80-custos-e-licencas.md).

---

## 5. Distribuído e HTAP — os limites sendo empurrados

- **Citus** (extensão, hoje da Microsoft) distribui tabelas por uma chave de shard, dando escala
  horizontal de escrita mantendo a interface SQL. É a base do Azure Cosmos DB for PostgreSQL.
- **Aurora PostgreSQL** (AWS) e **AlloyDB** (Google) reescreveram a camada de armazenamento para
  desempenho e escala, mantendo compatibilidade.
- **CockroachDB** e **YugabyteDB** são bancos distribuídos **compatíveis** com o protocolo do
  PostgreSQL — não são o Postgres, mas falam a mesma língua, mostrando o protocolo virando padrão.
- **HTAP** (transacional + analítico no mesmo banco) é uma fronteira ativa: extensões de
  armazenamento colunar e a I/O assíncrona do PG 18 caminham para tornar o Postgres viável também
  para análise sobre os dados operacionais, sem um data warehouse separado.

*Opinião profissional:* a maioria dos projetos **nunca** precisa de Postgres distribuído. Uma
instância vertical moderna com réplicas de leitura aguenta uma carga enorme. Distribuído resolve um
problema real de escala que poucos têm, ao custo de complexidade grande. Ver
[19-replicacao-e-alta-disponibilidade.md](19-replicacao-e-alta-disponibilidade.md).

---

## 6. A tese da consolidação: "just use Postgres"

O movimento cultural mais forte de 2024–2026 é a **consolidação de stack no PostgreSQL**. Em vez de
um zoológico de bancos especializados (um relacional, um de documentos, um de vetores, um de filas,
um de busca, um de séries temporais), a proposta é: **use PostgreSQL para tudo até provar que não
dá.**

| Precisa de… | Em vez de… | Use no Postgres |
|---|---|---|
| Documentos flexíveis | MongoDB | JSONB |
| Busca textual | Elasticsearch | tsvector / pg_trgm |
| Vetores / IA | Pinecone | pgvector |
| Geolocalização | banco geo dedicado | PostGIS |
| Fila de trabalho | RabbitMQ/SQS (às vezes) | `SKIP LOCKED` |
| Séries temporais | InfluxDB | TimescaleDB / particionamento |
| Cache (às vezes) | Redis | `UNLOGGED` tables |

**O argumento a favor:** menos sistemas para operar, transações atravessando tudo, uma linguagem,
uma cópia dos dados, um backup. Para a maioria das equipes, a simplicidade operacional vale mais
que o desempenho de pico de uma ferramenta especializada.

**O argumento contra (honesto):** em escalas extremas ou cargas muito específicas, a ferramenta
dedicada ganha — Elasticsearch faz busca melhor que tsvector em corpora enormes; Redis é mais rápido
que qualquer tabela; um banco vetorial dedicado escala além do pgvector. A consolidação é um
**ponto de partida excelente**, não um dogma. *Minha posição:* comece consolidado; especialize por
evidência medida, não por antecipação. O custo de operar cinco bancos é real e imediato; o custo de
migrar de um Postgres bem feito para uma ferramenta dedicada, quando comprovadamente necessário, é
gerenciável.

---

## 7. Debates abertos, com os dois lados

### "pgvector substitui bancos vetoriais dedicados?"

**A favor:** para a maioria dos casos, sim — desempenho competitivo com pgvectorscale, custo menor,
e vetores junto dos dados. **Contra:** em bilhões de vetores com requisitos extremos de latência e
recall, os dedicados ainda ganham. *Posição:* comece com pgvector; migre só se medir que precisa.

### "Serverless ou instância dedicada?"

**Serverless:** ótimo para dev, cargas variáveis, branching. **Dedicada:** previsível e mais barata
para carga constante alta. *Posição:* depende do perfil de carga — faça a conta com dados reais, não
com o preço de tabela.

### "Consolidar tudo no Postgres, ou usar ferramentas especializadas?"

Tratado na seção 6. Resumo: consolide primeiro, especialize por evidência.

---

## 8. Previsões para 2027–2028 — e o que as invalidaria

Explicitamente **especulação**, com critério de falsificação:

| Previsão | Confiança | O que a invalidaria |
|---|---|---|
| I/O assíncrona destrava ganhos de desempenho em cascata nas próximas versões | alta | Limitações do `io_uring` ou regressões |
| PostgreSQL continua como padrão de facto para IA (RAG, agentes) | alta | Um banco vetorial dedicado dominar por vantagem decisiva |
| Serverless Postgres vira o padrão para novos projetos | média | Custo em carga constante afastar quem cresce |
| HTAP no Postgres reduz a necessidade de data warehouse separado para médios | média | Cargas analíticas grandes continuarem exigindo colunar dedicado |
| A consolidação "just use Postgres" segue como conselho padrão | alta | Uma classe de carga nova que o Postgres não absorva bem |
| Postgres distribuído continua nicho | média-alta | Escala global barata virar requisito comum |

---

## 9. O que **não** mudou, e provavelmente não vai mudar

- **O modelo relacional e o SQL.** 55 anos, e é a base de tudo aqui.
- **ACID e a obsessão por não perder dados.** É a identidade do projeto.
- **MVCC e o WAL.** A arquitetura que sustenta a confiabilidade.
- **A extensibilidade.** O gene que faz o Postgres absorver o futuro.
- **A governança sem dono, sob a PostgreSQL License.** O que protege o investimento de quem o usa.
- **"Normalize primeiro; otimize por evidência."** Bons fundamentos de modelagem.

Ferramenta e moda mudam; fundamento não. Por isso os arquivos 10 a 21 envelhecem em década, e este
aqui, em meses.

---

## Autoteste

1. Qual foi o maior avanço arquitetural do PostgreSQL 18, e que ganhos ele traz?
2. Como o pgvector + pgvectorscale mudaram a posição do Postgres frente a bancos vetoriais
   dedicados? (Cite que os números são reportados.)
3. O que a Neon reimaginou, e o que é "escala a zero" e "branching"?
4. Qual é o fato verificado sobre Databricks e Snowflake em meados de 2026?
5. Explique a tese "just use Postgres" e dê o argumento a favor e o contra.
6. Quando um banco vetorial dedicado ainda ganha do pgvector?
7. Serverless ou instância dedicada — de que depende a escolha?
8. Por que a maioria dos projetos nunca precisa de Postgres distribuído?
9. Escolha uma previsão da seção 8 e descreva um evento que a invalidaria.
10. Cite três fundamentos que não mudaram e por que são estáveis.

---

### Fontes consultadas (11/08/2026)

- [PostgreSQL 18 release notes](https://www.postgresql.org/docs/18/release-18.html) e [postgresql.org — PostgreSQL 18 released](https://www.postgresql.org/about/news/postgresql-18-released-3142/) — AIO, uuidv7, skip scan, colunas geradas virtuais, OAuth
- [Neon — PostgreSQL 18 New Features](https://neon.com/postgresql/18-new-features) e [Crunchy Data — Get Excited About Postgres 18](https://www.crunchydata.com/blog/get-excited-about-postgres-18) — **fontes secundárias** para detalhes das features
- [pgvector vs pgvectorscale — production RAG guide 2026](https://devstarsj.github.io/2026/04/04/postgresql-pgvector-pgvectorscale-rag-production-guide-2026/) e [PostgreSQL for AI Applications (2026)](https://www.adwaitx.com/postgresql-ai-applications-vector-database/) — **secundárias**; números de latência/custo reportados, não verificados por mim
- [Neon Serverless Postgres Pricing 2026 — Simplyblock](https://vela.simplyblock.io/articles/neon-serverless-postgres-pricing-2026/) — aquisição pela Databricks, Lakebase, mudanças de preço
- [Microsoft — What's new with Postgres, 2026 edition](https://techcommunity.microsoft.com/blog/adforpostgresql/whats-new-with-postgres-at-microsoft-2026-edition/4526963) e Citus — distribuído
