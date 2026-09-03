# Glossário

Data: 13/08/2026 · Todo termo técnico usado no curso, definido

Termos em inglês aparecem com a tradução usual em português quando ela existe.
Quando o campo usa o termo em inglês, ele fica em inglês — porque é assim que
você vai encontrá-lo.

---

## A

**ACID** — Atomicidade, Consistência, Isolamento, Durabilidade. As quatro
garantias de uma transação. Ver [10](10-fundamentos.md) §7.

**agregação** — Função que colapsa muitas linhas em um valor: `SUM`, `AVG`,
`COUNT`, `MIN`, `MAX`. Ver [14](14-agregacao-e-grupos.md).

**AGM (cota)** — Cota superior justa para o tamanho da saída de uma junção,
dada pela cobertura fracionária de arestas do hipergrafo. Atserias, Grohe e
Marx, 2008. Ver [60](60-teoria-avancada.md) §2.

**álgebra relacional** — O conjunto de operações formais sobre relações
(seleção, projeção, produto, união, diferença, renomeação) do qual o SQL é uma
implementação. Ver [10](10-fundamentos.md) §4.

**alias** → **apelido**.

**anti-join** — Padrão `LEFT JOIN ... WHERE chave IS NULL`, que devolve o que
existe de um lado e não do outro. Ver [13](13-juncoes.md) §3.

**apelido** (*alias*) — Nome temporário dado a uma coluna ou tabela com `AS`.

**ANSI/SPARC** — Arquitetura de três níveis (externo, conceitual, interno)
formalizada em 1975. Base da independência de dados.

**as-of join** — Junção que traz, para cada linha, a última linha da outra
tabela anterior a ela no tempo. Nativa no DuckDB (`ASOF JOIN`). Ver
[13](13-juncoes.md) §4.

**atributo** — Nome formal de **coluna** no modelo relacional.

**autoincremento** — Coluna cujo valor é gerado sequencialmente pelo banco.

---

## B

**banda morta** (*deadband*) — Faixa de variação abaixo da qual uma mudança
não é registrada nem alarmada. Base do registro por exceção dos historiadores.
Ver [18](18-series-temporais.md) §6.

**batelada** (*batch*) — Modo de operação em que o produto é feito em lotes
discretos, não continuamente. Modelado pela norma ISA-88.

**BCNF** (Forma Normal de Boyce-Codd) — Toda dependência funcional tem uma
superchave como determinante. Ver [60](60-teoria-avancada.md) §3.

**BRIN** (*Block Range INdex*) — Índice do PostgreSQL que guarda mínimo e
máximo por bloco de páginas. Minúsculo e eficiente para tabelas naturalmente
ordenadas, como série temporal. Ver [21](21-indices-e-desempenho.md) §6.

**B-tree** (árvore B) — Estrutura de índice balanceada e larga, padrão em
praticamente todo banco relacional.

**bucket** — Intervalo em que o tempo é dividido para reamostragem (hora,
15 minutos). Ver [18](18-series-temporais.md) §3.

---

## C

**camada semântica** — Conjunto de views que expõem nomes de negócio e regras
únicas, isolando o usuário final das tabelas brutas. Ver
[22](22-views-e-analitico.md) §3.

**cancelamento catastrófico** — Perda de dígitos significativos ao subtrair
dois números de ponto flutuante quase iguais. Afeta a fórmula de um passo do
desvio padrão. Ver [14](14-agregacao-e-grupos.md) §4.

**CAP (teorema)** — Durante uma partição de rede, escolha entre consistência e
disponibilidade. **Não** diz "escolha duas de três". Ver
[60](60-teoria-avancada.md) §6.

**cardinalidade** — (1) Número de linhas de uma relação. (2) Em junções, a
relação de multiplicidade entre os lados (1:1, 1:N, N:M) — a causa nº 1 de
número errado. Ver [13](13-juncoes.md) §2.

**CEP** — Controle Estatístico de Processo. Cartas de controle, regras de
Nelson, Cp/Cpk. Ver [30](30-engenharia-quimica.md) §4.

**chattering** — Alarme que oscila rapidamente em torno do limite, gerando
dezenas de eventos para um único distúrbio. Corrige-se com banda morta e
atraso de acionamento.

**chave candidata** — Conjunto mínimo de colunas que identifica unicamente uma
linha.

**chave estrangeira** (*foreign key*) — Coluna que referencia a chave de outra
tabela; garante integridade referencial. **No SQLite, exige
`PRAGMA foreign_keys = ON`.**

**chave natural** — Chave primária com significado no domínio (`tag_id`, CPF).

**chave primária** (*primary key*) — A chave candidata escolhida. Única e não
nula.

**chave artificial** (*surrogate key*) — Chave sem significado, gerada pelo
banco (`id INTEGER PRIMARY KEY`).

**CMMS** — *Computerized Maintenance Management System*. Sistema de gestão de
manutenção.

**colunar** — Armazenamento por coluna em vez de por linha. Ótimo para
agregação; ruim para atualizar uma linha. DuckDB, ClickHouse, BigQuery.

**collation** — Regra de comparação e ordenação de texto. Define se `'Á'` vem
antes ou depois de `'Z'`.

**COMMIT** — Confirma uma transação, tornando as mudanças permanentes. Cada
`COMMIT` custa um `fsync`.

**consulta conjuntiva** (CQ) — `SELECT-FROM-WHERE` só com igualdades e `AND`.
Ver [60](60-teoria-avancada.md) §2.

**Cp / Cpk** — Índices de capacidade de processo. `Cp = (LSE−LIE)/6σ`;
`Cpk = min(LSE−μ, μ−LIE)/3σ`. Cpk considera a descentragem.

**CROSS JOIN** — Produto cartesiano: toda linha de A com toda de B.

**CTE** (*Common Table Expression*) — Consulta nomeada declarada com `WITH`,
usável na consulta principal. Ver [15](15-subconsultas-e-ctes.md).

**CTE recursiva** — CTE que se referencia; gera séries e percorre hierarquias.
**Exige condição de parada.**

**cursor** — Objeto que percorre o resultado de uma consulta linha a linha.
Em SQL procedural, um laço de cursor é geralmente um antipadrão.

---

## D

**DCL** — *Data Control Language*: `GRANT`, `REVOKE`.

**DDL** — *Data Definition Language*: `CREATE`, `ALTER`, `DROP`.

**deadlock** — Duas transações esperando uma pela outra. O banco detecta e
mata uma. Previne-se travando sempre na mesma ordem.

**dependência funcional** — X → Y: se duas tuplas concordam em X, concordam em
Y. Base da normalização.

**desnormalização** — Duplicar dado deliberadamente para ganhar desempenho.
Otimização consciente, com custo declarado.

**dimensão** — Tabela que descreve (equipamento, produto, tempo), em modelagem
dimensional. Contrasta com **fato**.

**DML** — *Data Manipulation Language*: `INSERT`, `UPDATE`, `DELETE`, `MERGE`.

**DQL** — *Data Query Language*: `SELECT`.

**downsampling** → **reamostragem**.

---

## E

**EEMUA 191** — Guia de gestão de alarmes. Meta prática de ~6 alarmes/hora por
operador.

**egresso** (*egress*) — Cobrança por transferir dados **para fora** da nuvem.
Entrar é grátis; sair, não.

**escalar (subconsulta)** — Subconsulta que devolve um único valor.

**esquema** (*schema*) — (1) A estrutura das tabelas. (2) Em alguns bancos, um
espaço de nomes dentro do banco.

**EXISTS** — Predicado que testa se uma subconsulta devolve ao menos uma
linha. Não multiplica linhas.

**EXPLAIN** — Mostra o plano de execução de uma consulta. No SQLite,
`EXPLAIN QUERY PLAN`.

---

## F

**fan-out** (leque) — Multiplicação de linhas causada por um `JOIN` 1:N,
inflando somas. Ver [13](13-juncoes.md) §2.

**fato** — Tabela de medidas numéricas em modelagem dimensional.

**FILTER** — Cláusula que restringe uma agregação:
`COUNT(*) FILTER (WHERE ...)`. SQLite ≥3.30, PostgreSQL, DuckDB.

**FLP** — Resultado de impossibilidade: consenso é impossível em sistema
assíncrono com uma falha. Fischer, Lynch, Paterson, 1985.

**forma normal** — Critérios de projeto que eliminam redundância: 1FN, 2FN,
3FN, BCNF, 4FN, 5FN.

**fsync** — Chamada que força a gravação física no disco. É o custo de cada
`COMMIT` e a razão da letra **D** de ACID.

---

## G

**gaps and islands** — Padrão de SQL analítico que identifica blocos contíguos
usando a diferença entre duas numerações. Ver [16](16-funcoes-de-janela.md) §5.

**gatilho** (*trigger*) — Código que roda automaticamente em resposta a
`INSERT`/`UPDATE`/`DELETE`. Poderoso e invisível — use pouco.

**GQL** — ISO/IEC 39075:2024, linguagem padrão de consulta a grafos, irmã do
SQL/PGQ.

**GROUP BY** — Agrupa linhas para agregação.

---

## H

**hash join** — Algoritmo de junção que constrói uma tabela hash da relação
menor. Só funciona com igualdade. **Não existe no SQLite.**

**HAVING** — Filtra **grupos** depois da agregação. Contrasta com `WHERE`,
que filtra linhas antes.

**historiador** (*process historian*) — Banco especializado em série temporal
de processo: PI System, IP.21, PHD. Guarda sinal muito bem e relaciona muito
mal.

---

## I

**idempotente** — Rodar duas vezes tem o mesmo efeito de rodar uma. Propriedade
essencial de qualquer processo de carga. Ver [06](06-exemplos.md) exemplo 14.

**independência de dados** — Separação entre o significado lógico dos dados e
sua organização física. A contribuição central de Codd.

**índice** — Estrutura ordenada auxiliar que acelera busca. Custa espaço e
escrita.

**índice de cobertura** (*covering index*) — Índice que contém todas as
colunas de que a consulta precisa, dispensando ir à tabela.

**índice parcial** — Índice com `WHERE`, cobrindo só um subconjunto das linhas.

**INNER JOIN** — Junção que devolve só o que casa dos dois lados.

**integridade referencial** — Garantia de que toda chave estrangeira aponta
para uma linha existente.

**isolamento** — Grau em que transações concorrentes se afetam.
`READ UNCOMMITTED` < `READ COMMITTED` < `REPEATABLE READ` < `SERIALIZABLE`.

**ISA-5.1 / 88 / 95 / 18.2** — Normas: identificação de instrumentos; controle
de batelada; integração empresa-controle; gestão de alarmes.

---

## J

**janela (função de)** (*window function*) — Função calculada sobre linhas
vizinhas **sem colapsá-las**: `OVER (PARTITION BY ... ORDER BY ...)`. Ver
[16](16-funcoes-de-janela.md).

**JOIN** → **junção**.

**julianday** — Função do SQLite que devolve o dia juliano fracionário. A
diferença entre dois `julianday` × 1440 dá minutos.

**junção** (*join*) — Combinação de linhas de duas tabelas segundo uma
condição.

**junção temporal** — Junção cuja condição é um intervalo de tempo
(`ts >= inicio AND ts < fim`). A mais importante para dado de processo.

---

## L

**LAG / LEAD** — Funções de janela que acessam o valor de uma linha anterior /
posterior.

**lakehouse** — Arquitetura que combina o armazenamento barato do *data lake*
com a semântica de tabela do *data warehouse*. Formato dominante em 2026:
Apache Iceberg.

**LEFT JOIN** — Junção que preserva todas as linhas da esquerda, preenchendo
com `NULL` onde não há par.

**LIMS** — *Laboratory Information Management System*. Sistema do laboratório:
amostras, ensaios, laudos, especificações.

**LOCF** (*Last Observation Carried Forward*) — Preencher lacuna repetindo o
último valor conhecido. Adequado para sinais de estado.

**LSM-tree** — Estrutura de armazenamento otimizada para escrita. Base de
vários bancos NoSQL e de série temporal.

---

## M

**materialização** — Gravar o resultado de uma consulta em vez de recalculá-lo.

**MERGE** — Comando padrão ISO para inserir-ou-atualizar. Oracle, SQL Server,
PostgreSQL ≥15.

**MES / MOM** — *Manufacturing Execution System* / *Manufacturing Operations
Management*. Nível 3 da ISA-95.

**multiconjunto** (*bag*) — Coleção que aceita duplicatas. Uma tabela SQL é um
multiconjunto; uma relação de Codd é um conjunto.

**MVCC** (*Multi-Version Concurrency Control*) — Cada transação vê um
instantâneo consistente. Leitores não bloqueiam escritores. PostgreSQL, Oracle.

---

## N

**nested loop join** — Algoritmo de junção que, para cada linha de A, procura
em B. **O único que o SQLite tem.**

**normalização** — Processo de organizar tabelas para eliminar redundância.

**NULL** — Marcador de valor **desconhecido**. Não é zero, não é vazio, não é
falso. `NULL = NULL` é `NULL`. Ver [17](17-tipos-e-nulos.md).

---

## O

**OEE** (*Overall Equipment Effectiveness*) — Disponibilidade × Desempenho ×
Qualidade. A métrica de manufatura mais usada e mais mal calculada.

**OLAP** — Processamento analítico: varrer e agregar muitas linhas.

**OLTP** — Processamento transacional: ler e gravar poucas linhas por chave.

**ORM** (*Object-Relational Mapping*) — Camada que gera SQL a partir de
classes. Útil em aplicação; atrapalha em análise.

**otimizador** (*query optimizer*) — Componente que escolhe o plano de
execução. Sua maior fraqueza é estimar cardinalidade.

---

## P

**PACELC** — Refinamento do CAP: na partição (P), escolha entre A e C;
senão (E), entre latência (L) e consistência (C).

**Parquet** — Formato de arquivo colunar comprimido. Medido neste curso:
13,3 MB de CSV → 3,3 MB de Parquet.

**particionamento** — Dividir fisicamente uma tabela por faixa de valor
(geralmente tempo).

**PI System** — Historiador da AVEVA (ex-OSIsoft), o mais implantado do mundo
em indústria de processo. Expõe SQL por ODBC/OLE DB.

**pivô** (*pivot*) — Girar dado do formato longo (uma linha por medição) para o
largo (uma coluna por tag).

**plano de execução** — A sequência de operações físicas que o banco escolheu.

**PRAGMA** — Comando de configuração do SQLite. Vários valem **por conexão**.

**predicate pushdown** — Transformação do otimizador que empurra o filtro para
o mais fundo possível na consulta.

**projeção** — Escolher colunas (π na álgebra relacional; `SELECT` no SQL).

---

## Q

**qualidade (flag de)** — Marcação de confiabilidade da leitura, vinda do
coletor. **Não pega tudo**: espículas de instrumento chegam marcadas como boas.

---

## R

**reamostragem** (*downsampling*) — Reduzir a frequência dos dados agregando em
buckets. Guarde min, máx e n junto com a média.

**reconciliação de dados** — Ajuste de medidas redundantes para satisfazer os
balanços de massa e energia, ponderando pela incerteza de cada instrumento.

**registro por exceção** (*exception reporting*) — Gravar só quando o valor
muda mais que a banda morta. Padrão dos historiadores; torna o intervalo entre
amostras irregular **por projeto**.

**relação** — Nome formal de tabela no modelo relacional. É um **conjunto**.

**RETURNING** — Cláusula que devolve as linhas afetadas por
`INSERT`/`UPDATE`/`DELETE`.

**ROLLUP / CUBE** — Extensões do `GROUP BY` que produzem subtotais. **Não
existem no SQLite.**

**ROW_NUMBER / RANK / DENSE_RANK** — Funções de janela de numeração. Diferem no
tratamento de empates.

---

## S

**sargable** (*Search ARGument ABLE*) — Predicado que o banco consegue usar
para navegar o índice. Deixa de ser quando há função aplicada na coluna.
Medido: 5,0 ms → 0,1 ms ao tornar *sargable*.

**SCD** (*Slowly Changing Dimension*) — Estratégias para historiar cadastro que
muda. Tipo 1 sobrescreve; **tipo 2** cria nova linha com validade; tipo 3 guarda
o anterior.

**seleção** — Escolher linhas (σ na álgebra; `WHERE` no SQL).

**semiaberto (intervalo)** — `[início, fim)`: inclui o início, exclui o fim. O
padrão correto para tempo.

**serializabilidade** — Uma execução concorrente é serializável se equivale a
alguma execução sequencial.

**soft sensor** (sensor virtual) — Modelo que estima uma propriedade de difícil
medição (viscosidade, composição) a partir de variáveis de processo medidas.

**SQL/PGQ** — Parte 16 do padrão (SQL:2023): consultas em grafo de propriedades.

**STRICT** — Modo de tabela do SQLite ≥3.37 que impõe tipagem de verdade.
**Use sempre.**

**subconsulta** — Consulta dentro de outra.

---

## T

**tabela temporal** — Tabela com versionamento por período (SQL:2011).
SQL Server, Oracle, DB2, MariaDB. **Não** no PostgreSQL nem no SQLite.

**tag** — Ponto de medição da planta, identificado pela ISA-5.1 (`TI-101`).

**theta-join** — Junção cuja condição não é igualdade (por exemplo, um
intervalo).

**TimescaleDB** — Extensão do PostgreSQL para série temporal: partição
automática, compressão, agregados contínuos.

**transação** — Unidade atômica de trabalho. `BEGIN` … `COMMIT` / `ROLLBACK`.

**tupla** — Nome formal de linha no modelo relacional.

---

## U

**UNION / UNION ALL** — Empilha duas consultas. `UNION` remove duplicatas
(custa uma ordenação); `UNION ALL` não.

**UNS** (*Unified Namespace*) — Arquitetura em que todos os sistemas de uma
planta publicam e assinam num espaço de nomes comum, tipicamente sobre MQTT
Sparkplug.

**UPSERT** — Inserir ou atualizar. `ON CONFLICT DO UPDATE` no SQLite,
PostgreSQL e DuckDB.

**UTC** — Tempo universal coordenado. **Guarde sempre em UTC**; converta só na
exibição.

---

## V

**vetorizada (execução)** — Processar lotes de valores por vez em vez de linha
a linha. Base do desempenho de bancos colunares.

**view** — Consulta com nome. Não guarda dado.

**view materializada** — View que guarda o resultado. PostgreSQL, Oracle,
SQL Server, DuckDB. **Não no SQLite.**

---

## W

**WAL** (*Write-Ahead Logging*) — Grava as mudanças num log antes de aplicá-las.
No SQLite, `PRAGMA journal_mode=WAL` permite que leitores não bloqueiem o
escritor.

**WHERE** — Filtra **linhas**, antes do agrupamento.

**WITHOUT ROWID** — Tabela do SQLite em que a chave primária é o índice
agrupado. Bom quando o acesso pela chave domina.

**worst-case optimal join** — Algoritmo de junção que atinge a cota AGM
processando todos os atributos ao mesmo tempo. Leapfrog Triejoin, NPRR.

**write skew** — Anomalia em que duas transações leem um estado consistente,
cada uma escreve algo válido isoladamente, e o resultado conjunto viola a
restrição. `REPEATABLE READ` **não** impede.

---

## Z

**ZOH** (*Zero-Order Hold*) — Interpolação em degrau: o valor se mantém
constante até a próxima amostra. Suposição padrão de historiador. Contrasta com
interpolação linear.

**z-score** — `(x − μ)/σ`. Quantos desvios padrão um valor está da média. Base
de detecção simples de anomalia — e enviesada quando os próprios outliers
entram no cálculo de μ e σ.

---

*Voltar ao [00-MAPA.md](00-MAPA.md).*
