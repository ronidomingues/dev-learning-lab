# Glossário — PostgreSQL e bancos de dados relacionais

`Todo termo técnico do material, definido.` · `Última atualização: 11/08/2026`

Termos em inglês são mantidos quando é assim que o campo os usa, com a tradução na primeira menção.
Ordenado alfabeticamente.

---

**ACID** — as quatro garantias de uma transação: **A**tomicidade (tudo ou nada), **C**onsistência
(regras sempre válidas), **I**solamento (transações não se atrapalham), **D**urabilidade (o
confirmado sobrevive a falhas).

**Agregação** — operação que combina várias linhas num resultado (`SUM`, `COUNT`, `AVG`), com
`GROUP BY`.

**Álgebra relacional** — a matemática por trás do SQL: operadores (seleção, projeção, junção...)
sobre relações. Base da otimização de consultas.

**ANALYZE** — comando que atualiza as **estatísticas** que o planejador usa. Também o modo do
`EXPLAIN` que executa a consulta e mede.

**Atomicidade** — o "A" de ACID: uma transação acontece por inteiro ou não acontece.

**Autovacuum** — processo que roda o [VACUUM] automaticamente em segundo plano. Manter saudável é
essencial em produção.

**B-tree** — o tipo de [índice] padrão: árvore balanceada e ordenada, para igualdade, faixas e
ordenação.

**Bloat (inchaço)** — espaço ocupado por [linhas mortas] que o VACUUM ainda não recuperou; deixa
tabelas e índices maiores e mais lentos.

**BRIN** — *Block Range Index*: índice minúsculo para tabelas enormes e naturalmente ordenadas
(séries temporais).

**CAP (teorema)** — um sistema distribuído não pode garantir simultaneamente Consistência,
Disponibilidade e tolerância a Partição; durante uma partição, escolhe-se C ou A.

**Chave estrangeira** (*foreign key*) — coluna que referencia a [chave primária] de outra tabela; o
banco garante que o valor exista lá.

**Chave primária** (*primary key*) — coluna(s) que identifica(m) cada linha de forma única e
não-nula.

**cluster** — uma instância do servidor PostgreSQL (um diretório de dados, uma porta), contendo
vários bancos.

**Constraint (restrição)** — regra que o banco impõe: `PRIMARY KEY`, `FOREIGN KEY`, `UNIQUE`,
`NOT NULL`, `CHECK`, `EXCLUDE`.

**CRUD** — *Create, Read, Update, Delete*: as quatro operações básicas sobre dados.

**CTE** (*Common Table Expression*) — consulta nomeada com `WITH`, para legibilidade; pode ser
recursiva (`WITH RECURSIVE`) para hierarquias.

**Cursor** — mecanismo para percorrer um resultado aos poucos; também, "paginação por cursor"
(keyset).

**DDL** (*Data Definition Language*) — comandos que definem estrutura: `CREATE`, `ALTER`, `DROP`.

**Deadlock** — duas transações esperando uma pela outra indefinidamente; o PostgreSQL detecta e
aborta uma.

**Declarativo** — descrever o resultado desejado (SQL), não os passos para obtê-lo.

**Dependência funcional** — `X → Y`: o valor de X determina unicamente o de Y. Base da normalização.

**DML** (*Data Manipulation Language*) — comandos sobre dados: `INSERT`, `UPDATE`, `DELETE`,
`SELECT`.

**Durabilidade** — o "D" de ACID: o que foi confirmado (`COMMIT`) sobrevive a quedas. Garantida pelo
[WAL].

**Embedding** — vetor de números que representa o significado de um texto; buscado por similaridade
com [pgvector].

**ENUM** — tipo com um conjunto fixo e ordenado de valores.

**Esquema** (*schema*) — namespace de tabelas dentro de um banco (`public` é o padrão).

**EXPLAIN** — comando que mostra o [plano de execução] de uma consulta; `EXPLAIN ANALYZE` executa e
mede.

**Extensão** — pacote que adiciona tipos, funções e índices ao PostgreSQL (`CREATE EXTENSION`).

**Failover** — promover uma [réplica] a principal quando a principal falha.

**Fecho transitivo** — todos os nós alcançáveis num grafo; exige [CTE recursiva], além da álgebra
relacional pura.

**FDW** (*Foreign Data Wrapper*) — mecanismo para consultar dados externos (outro banco, arquivo)
como tabelas locais.

**Forma normal** — nível de organização que elimina redundância (1FN, 2FN, 3FN, BCNF).

**GIN** — *Generalized Inverted Index*: índice para JSONB, arrays e busca textual (`@>`, `@@`).

**GiST** — *Generalized Search Tree*: índice para geometria, ranges e "vizinhança".

**GRANT / REVOKE** — conceder / retirar privilégios de uma [role].

**HTAP** — *Hybrid Transactional/Analytical Processing*: cargas transacionais e analíticas no mesmo
banco.

**Índice** — estrutura auxiliar que acelera a busca de dados, ao custo de tornar a escrita mais
lenta.

**Índice parcial** — índice que cobre só um subconjunto das linhas (`WHERE condição`).

**Isolamento** — o "I" de ACID: transações concorrentes não interferem. Níveis: `READ COMMITTED`,
`REPEATABLE READ`, `SERIALIZABLE`.

**JOIN** — combina linhas de duas tabelas por uma condição (`INNER`, `LEFT`, `RIGHT`, `FULL`,
`CROSS`, `LATERAL`).

**JSONB** — tipo binário para documentos JSON, indexável e rápido de consultar (preferível ao
`JSON` textual).

**Keyset pagination** — paginação por [cursor], usando a chave do último item; rápida em páginas
altas (vs. `OFFSET`).

**Linha morta** (*dead tuple*) — versão antiga de uma linha, deixada pelo [MVCC], que o [VACUUM]
recupera.

**MVCC** — *Multi-Version Concurrency Control*: cada transação vê uma foto consistente; leitores não
bloqueiam escritores.

**Normalização** — organizar tabelas para eliminar redundância e anomalias.

**NULL** — ausência de valor (desconhecido/não aplicável); qualquer comparação com `NULL` dá `NULL`.
Use `IS NULL`.

**NUMERIC** — tipo decimal **exato**; obrigatório para dinheiro (nunca `float`).

**OLTP / OLAP** — processamento transacional (muitas escritas pequenas) / analítico (consultas
grandes de leitura).

**Otimizador / planejador** — o componente que escolhe o [plano de execução] mais barato para uma
consulta.

**PACELC** — refinamento do [CAP]: se há Partição, escolha A ou C; senão (Else), escolha Latência ou
Consistência.

**Particionamento** — dividir uma tabela lógica em várias físicas por um critério (ex.: faixa de
data).

**pgvector** — extensão que adiciona busca por similaridade de vetores (IA/RAG).

**PITR** — *Point-In-Time Recovery*: restaurar o banco a um instante exato, via backup base + [WAL].

**Plano de execução** — a sequência de operações que o executor usa para responder uma consulta.

**Pool de conexões** — reaproveitar conexões em vez de abrir uma por requisição (as conexões são
caras).

**Pooler** — serviço externo (PgBouncer) que multiplexa muitos clientes sobre poucas conexões
reais.

**PostGIS** — extensão que faz do PostgreSQL um banco geoespacial de referência.

**psql** — o cliente de terminal interativo do PostgreSQL.

**Réplica** (*standby*) — cópia somente-leitura do banco, alimentada por [replicação].

**Replicação** — manter cópias do banco em outras máquinas (física/streaming ou lógica).

**RLS** (*Row-Level Security*) — política que filtra quais **linhas** cada usuário pode ver.

**Role** — usuário ou grupo no PostgreSQL; vive no [cluster], com ou sem login.

**scram-sha-256** — método moderno e recomendado de autenticação por senha (substitui o `md5`).

**Serialização (anomalia)** — resultado de transações concorrentes que difere de qualquer execução
serial; prevenida por `SERIALIZABLE`.

**SGBD** — Sistema de Gerenciamento de Banco de Dados (o programa, ex.: PostgreSQL).

**Sharding** — particionar dados por chave entre vários servidores, para escala horizontal de
escrita.

**SSI** (*Serializable Snapshot Isolation*) — a técnica do PostgreSQL que dá serializabilidade com o
desempenho do [MVCC].

**SQL** (*Structured Query Language*) — a linguagem declarativa para definir e consultar dados
relacionais.

**Subconsulta** — uma consulta dentro de outra.

**TIMESTAMPTZ** — data/hora com fuso (guarda o instante em UTC); use sempre para instantes reais.

**TOAST** — técnica que armazena valores grandes (textos, JSONB) fora da linha principal,
comprimidos.

**Transação** — conjunto de operações atômicas (`BEGIN` ... `COMMIT`/`ROLLBACK`).

**Tupla** — uma linha de uma [relação]/tabela.

**UPSERT** — inserir ou, se já existir, atualizar (`INSERT ... ON CONFLICT`).

**uuidv7** — UUID ordenado por tempo (PG 18); evita a fragmentação de índice do UUIDv4.

**VACUUM** — recupera o espaço das [linhas mortas] deixadas pelo [MVCC]; previne [bloat] e
wraparound.

**View** — consulta salva usada como tabela; *materialized view* armazena o resultado.

**WAL** (*Write-Ahead Log*) — o log escrito **antes** de modificar os dados; base da durabilidade,
da recuperação de crash e da replicação.

**Função de janela** (*window function*) — agrega sobre um conjunto de linhas **sem** colapsá-las
(`OVER`, `PARTITION BY`).

**Wraparound (de XID)** — a volta que os ids de transação de 32 bits dão; se o [VACUUM] não congela
linhas antigas a tempo, o banco para de aceitar escritas.

---

### Termos de comando/psql frequentes

| Termo | Significado |
|---|---|
| **`\d tabela`** | Descreve uma tabela no psql |
| **`\dt`, `\l`, `\du`** | Lista tabelas / bancos / roles |
| **`\copy`** | Importa/exporta CSV pelo cliente (não precisa de superusuário) |
| **`RETURNING`** | Devolve as linhas afetadas por `INSERT`/`UPDATE`/`DELETE` |
| **`ON CONFLICT`** | A cláusula de UPSERT |
| **`FOR UPDATE`** | Trava linhas selecionadas para escrita |
| **`SKIP LOCKED`** | Pula linhas já travadas (filas de trabalho) |
| **`GENERATED ALWAYS AS IDENTITY`** | Chave autoincrementada moderna (melhor que `SERIAL`) |
| **`CONCURRENTLY`** | Criar/recriar índice sem travar a tabela |
