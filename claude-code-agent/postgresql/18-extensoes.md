# 18 · Extensões — o superpoder do PostgreSQL

`Nível: intermediário → avançado` · `Última atualização: 11/08/2026`

A extensibilidade é o gene fundador do PostgreSQL (desde 1986, ver [11-historia.md](11-historia.md)),
e a razão pela qual ele absorve capacidades novas — geografia, IA, séries temporais — sem
reinventar o núcleo. Este arquivo mostra como e quais.

---

## 1. O que é uma extensão

Uma extensão é um pacote que adiciona **tipos, funções, operadores, índices ou comportamentos**
ao PostgreSQL, instalável com um comando. Diferente de um plugin frágil, extensões são cidadãos de
primeira classe: participam de transações, backups e do catálogo.

```sql
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;   -- ativa numa base
SELECT * FROM pg_available_extensions ORDER BY name; -- o que está disponível para instalar
SELECT * FROM pg_extension;                          -- o que já está ativo
ALTER EXTENSION pgvector UPDATE;                      -- atualiza
DROP EXTENSION pg_stat_statements;
```

Algumas extensões (as que carregam código na inicialização, como `pg_stat_statements`) exigem
constar em `shared_preload_libraries` no `postgresql.conf` e um restart. As demais são só
`CREATE EXTENSION`.

> **De onde vêm:** algumas acompanham o PostgreSQL (os *contrib modules*, sempre disponíveis).
> Outras se instalam pelo sistema de pacotes (`postgresql-18-postgis`, `postgresql-18-pgvector`) e
> depois se ativam com `CREATE EXTENSION`. Em serviços gerenciados (RDS, Cloud SQL), a lista de
> extensões permitidas é definida pelo provedor — nem toda extensão está disponível na nuvem.

---

## 2. As extensões que acompanham o PostgreSQL (contrib)

| Extensão | O que faz |
|---|---|
| **pg_stat_statements** | Estatísticas por consulta — **essencial** para tuning ([16](16-consultas-e-planejador.md)) |
| **pgcrypto** | Funções de criptografia e hash (`crypt`, `digest`, `gen_random_uuid`) |
| **uuid-ossp** | Geração de UUIDs (menos necessária no PG 18, que tem `uuidv7()` nativo) |
| **citext** | Tipo de texto insensível a maiúsculas (para e-mails, logins) |
| **hstore** | Pares chave-valor (anterior ao JSONB; hoje prefira JSONB) |
| **pg_trgm** | Similaridade e busca por trigramas — busca "fuzzy", `LIKE '%x%'` indexável |
| **btree_gin / btree_gist** | Misturar tipos comuns com GIN/GiST (habilita `EXCLUDE` com `=`) |
| **tablefunc** | Tabelas dinâmicas (*crosstab*/pivot) |
| **postgres_fdw** | Consultar tabelas de **outro** servidor PostgreSQL como se fossem locais |
| **file_fdw** | Ler arquivos (CSV) como tabelas |
| **pg_prewarm** | Aquecer o cache após reinício |
| **amcheck** | Verificar corrupção de índices |

`pg_trgm` merece destaque — resolve a busca "contém" com tolerância a erro:
```sql
CREATE EXTENSION pg_trgm;
CREATE INDEX ON produtos USING GIN (nome gin_trgm_ops);
SELECT * FROM produtos WHERE nome ILIKE '%camseta%';      -- indexável agora
SELECT nome, similarity(nome, 'camseta') FROM produtos ORDER BY similarity DESC;  -- fuzzy
```

---

## 3. As extensões que fizeram história

### PostGIS — o melhor SIG livre do mundo

```sql
CREATE EXTENSION postgis;
CREATE TABLE lojas (id BIGINT, nome TEXT, geo GEOGRAPHY(POINT));
INSERT INTO lojas VALUES (1, 'Centro', 'POINT(-34.87 -8.05)');
-- Lojas num raio de 5 km de um ponto
SELECT nome FROM lojas
WHERE ST_DWithin(geo, 'POINT(-34.88 -8.06)'::geography, 5000);
```
PostGIS transforma o PostgreSQL no banco geoespacial de referência — cálculo de distâncias no globo,
polígonos, projeções, roteamento. É usado por governos, mapas e logística no mundo todo. Sozinho,
justifica escolher PostgreSQL para qualquer aplicação com mapas.

### pgvector — a extensão que trouxe a IA para o Postgres

```sql
CREATE EXTENSION vector;
CREATE TABLE docs (id BIGINT, conteudo TEXT, embedding VECTOR(1536));
CREATE INDEX ON docs USING hnsw (embedding vector_cosine_ops);
SELECT conteudo FROM docs ORDER BY embedding <=> '[...]' LIMIT 5;   -- os mais similares
```
Guarda *embeddings* (representações de significado) e faz busca por similaridade — a base de RAG e
de busca semântica. Coberta em [06-exemplos.md, exemplo 13](06-exemplos.md#13-produção--busca-por-similaridade-com-pgvector).
Foi o maior motor de adoção recente do PostgreSQL: em vez de um banco vetorial separado, você tem
vetores **ao lado** dos dados de negócio, com transações e JOINs. Ver [65](65-estado-da-arte.md).

### As de séries temporais e escala

| Extensão | O que faz |
|---|---|
| **TimescaleDB** | Transforma o PostgreSQL num banco de séries temporais de alto desempenho (hipertabelas, compressão, agregação contínua). Popular em IoT e métricas |
| **Citus** | Distribui o PostgreSQL por vários nós (*sharding*), para escala horizontal |
| **pg_partman** | Automatiza criação e descarte de partições ([06, exemplo 12](06-exemplos.md#12-produção--particionamento-por-data)) |
| **pg_cron** | Agenda tarefas SQL (como cron) dentro do banco |

> **Nota sobre licenças e nuvem:** TimescaleDB e Citus têm componentes com licenças específicas
> (não são a PostgreSQL License pura), e a disponibilidade em serviços gerenciados varia. TimescaleDB
> tem sua própria nuvem; Citus foi adquirido pela Microsoft e é a base do Azure Cosmos DB for
> PostgreSQL. Verifique a licença antes de depender delas comercialmente. Ver
> [80-custos-e-licencas.md](80-custos-e-licencas.md).

---

## 4. Foreign Data Wrappers — consultar outros sistemas

FDWs permitem consultar dados **de fora** do PostgreSQL como se fossem tabelas locais:

```sql
CREATE EXTENSION postgres_fdw;
CREATE SERVER outro FOREIGN DATA WRAPPER postgres_fdw
    OPTIONS (host 'servidor2', dbname 'vendas');
CREATE USER MAPPING FOR current_user SERVER outro OPTIONS (user 'app', password '...');
IMPORT FOREIGN SCHEMA public FROM SERVER outro INTO externo;
SELECT * FROM externo.pedidos;    -- consulta o outro servidor de forma transparente
```

Há FDWs para MySQL, Oracle, SQLite, MongoDB, arquivos, APIs REST e mais. O PostgreSQL vira um **hub
de integração** — você consulta múltiplas fontes com um SQL só, e até faz JOIN entre elas.

---

## 5. Linguagens procedurais

Além do SQL, você escreve funções em várias linguagens:

| Linguagem | Extensão | Para |
|---|---|---|
| **PL/pgSQL** | nativa | O padrão: lógica, loops, tratamento de erro (ver [projeto-modelo](07-projeto-modelo/schema/002_functions.sql)) |
| **PL/Python** | `plpython3u` | Usar bibliotecas Python dentro do banco |
| **PL/Perl**, **PL/Tcl** | várias | Legado, integração |
| **PL/v8** | `plv8` | JavaScript no banco |
| **PL/Rust** (pgrx) | ecossistema | Extensões e funções em Rust, com desempenho nativo |

> **Ponderação:** rodar Python/JS **dentro** do banco é poderoso e perigoso — acopla a lógica ao
> banco, consome recursos do servidor de dados, e as linguagens "untrusted" (sufixo `u`) podem
> fazer qualquer coisa no SO. Use PL/pgSQL para lógica de dados; reserve as outras para casos com
> justificativa clara.

---

## 6. Como escolher e avaliar uma extensão

Nem toda extensão da internet é confiável. Critérios:

1. **Manutenção ativa** — commits recentes, compatível com a sua major.
2. **Licença** — a PostgreSQL License / BSD / MIT são seguras; verifique as demais.
3. **Disponibilidade na nuvem** — se você usa RDS/Cloud SQL, confira a lista permitida do provedor.
4. **Código carregado na inicialização** (`shared_preload_libraries`) precisa de restart e é mais
   invasivo — pese o benefício.
5. **Reputação** — PostGIS, pgvector, pg_stat_statements, TimescaleDB, Citus são consolidadas;
   extensões obscuras exigem mais cautela.

---

## 7. Os cinco porquês: por que o PostgreSQL é extensível e os concorrentes nem tanto?

**1. Por que o PostgreSQL consegue ganhar tipos novos (geo, vetor) como extensão, e outros bancos
precisam de novas versões do produto?**
Porque seu núcleo foi projetado, desde 1986, com um sistema de tipos, operadores e métodos de
índice **abstratos e plugáveis** — o usuário pode registrar os seus.

**2. Por que ele foi projetado assim?**
Porque essa era a **tese central** do projeto POSTGRES de Stonebraker: o problema dos bancos da
época não era a falta de funcionalidade, era a **rigidez**. Ele quis um banco que se pudesse
*ensinar*.

**3. Por que os concorrentes não fizeram o mesmo?**
Porque a maioria (comerciais como Oracle, SQL Server) otimizou para um conjunto **fixo** de tipos e
casos, priorizando desempenho e simplicidade sobre extensibilidade — e porque a extensibilidade tem
custo de complexidade que só compensa a longo prazo.

**4. Por que esse custo de complexidade compensou para o PostgreSQL?**
Porque, sendo um projeto **acadêmico e depois comunitário sem dono**, ele podia priorizar
arquitetura de longo prazo sobre lucro de curto prazo. Um produto comercial precisa vender agora;
um projeto de pesquisa/comunidade pode apostar em flexibilidade que só paga em 20 anos.

**5. Por que essa aposta de longo prazo acabou vencendo?**
Aqui a cadeia chega a uma **contingência histórica** que virou vantagem estrutural: ninguém em 1986
previu JSON, mapas globais ou IA. A aposta na extensibilidade foi uma aposta **contra a
imprevisibilidade do futuro** — e o futuro trouxe justamente demandas novas (documentos, geografia,
vetores) que um núcleo rígido não absorveria. A flexibilidade venceu porque o mundo mudou de formas
que ninguém podia especificar de antemão, e só um sistema *ensinável* acompanha o inespecificável.

---

## Autoteste

1. O que é uma extensão, e como ela difere de um plugin frágil?
2. Como você ativa uma extensão, e o que muda quando ela precisa de `shared_preload_libraries`?
3. Para que serve o `pg_trgm`, e que tipo de consulta ele torna indexável?
4. O que o PostGIS acrescenta, e por que ele sozinho justifica escolher PostgreSQL às vezes?
5. O que o pgvector faz, e por que foi um motor de adoção recente tão grande?
6. O que é um Foreign Data Wrapper, e como ele transforma o PostgreSQL num hub de integração?
7. Quais são os riscos de rodar PL/Python "untrusted" dentro do banco?
8. Cite três critérios para avaliar se deve confiar numa extensão.
9. Por que a disponibilidade de extensões pode ser um fator ao escolher um serviço gerenciado?
10. Percorra os cinco porquês da extensibilidade até a parada. Que tipo de parada é?
