# 23 — Dialetos: o mesmo SQL em bancos diferentes

Nível: intermediário · Data: 13/08/2026

Existe um padrão ISO e todo mundo o segue **quase**. O núcleo é idêntico; as
bordas divergem — e as bordas são justamente onde você vai passar o tempo.

**Estimativa honesta:** ~85% do que um analista escreve é portátil sem
alteração. Os 15% restantes são datas, funções de texto, paginação e
sintaxe de *upsert*.

---

## 1. Panorama

| Banco | Tipo | Licença | Melhor em | Pior em |
|---|---|---|---|---|
| **SQLite** | Embutido | Domínio público | Zero instalação; embarcado; teste | Concorrência de escrita; análise paralela |
| **PostgreSQL** | Servidor | PostgreSQL (tipo BSD) | Conformidade com o padrão; extensões; correção | Curva inicial de administração |
| **DuckDB** | Embutido, colunar | MIT | Análise sobre arquivo; CSV/Parquet | Escrita concorrente; OLTP |
| **MySQL / MariaDB** | Servidor | GPL / dupla | Web; onipresença em hospedagem | Conformidade; historicamente permissivo demais |
| **Oracle** | Servidor | Proprietária | Escala extrema; recursos; suporte | **Preço** e complexidade de licença |
| **SQL Server** | Servidor | Proprietária | Integração Microsoft; ferramental | Preço; Windows-cêntrico (menos hoje) |
| **SAP HANA** | Servidor, em memória | Proprietária | SAP | Preço; fora do SAP não faz sentido |

Preços em [80-custos-e-licencas.md](80-custos-e-licencas.md).

---

## 2. Tabela de tradução: as divergências que você vai encontrar

### Data e hora — a maior fonte de incompatibilidade

| Tarefa | SQLite | PostgreSQL | Oracle | SQL Server | MySQL | DuckDB |
|---|---|---|---|---|---|---|
| Agora | `datetime('now')` | `now()` | `SYSTIMESTAMP` | `SYSDATETIME()` | `NOW()` | `now()` |
| Hoje | `date('now')` | `current_date` | `TRUNC(SYSDATE)` | `CAST(GETDATE() AS DATE)` | `CURDATE()` | `today()` |
| Truncar na hora | `substr(ts,1,13)\|\|':00:00'` | `date_trunc('hour',ts)` | `TRUNC(ts,'HH')` | `DATETRUNC(hour,ts)` | `DATE_FORMAT(ts,'%Y-%m-%d %H:00')` | `date_trunc('hour',ts)` |
| Bucket de 15 min | aritmética manual | `date_bin('15 min',ts,'2000-01-01')` | `TRUNC` + aritmética | `DATE_BUCKET(minute,15,ts)` | aritmética | `time_bucket(INTERVAL '15 min',ts)` |
| Somar 1 dia | `date(ts,'+1 day')` | `ts + INTERVAL '1 day'` | `ts + 1` | `DATEADD(day,1,ts)` | `DATE_ADD(ts,INTERVAL 1 DAY)` | `ts + INTERVAL 1 DAY` |
| Diferença em min | `(julianday(a)-julianday(b))*1440` | `EXTRACT(EPOCH FROM a-b)/60` | `(a-b)*1440` | `DATEDIFF(minute,b,a)` | `TIMESTAMPDIFF(MINUTE,b,a)` | `date_diff('minute',b,a)` |
| Extrair ano | `strftime('%Y',ts)` | `EXTRACT(YEAR FROM ts)` | `EXTRACT(YEAR FROM ts)` | `YEAR(ts)` | `YEAR(ts)` | `year(ts)` |

### Texto

| Tarefa | Padrão / maioria | Exceções |
|---|---|---|
| Concatenar | `a \|\| b` | SQL Server: `a + b` ou `CONCAT`; MySQL: só `CONCAT` |
| Comprimento | `LENGTH(s)` | SQL Server: `LEN(s)` |
| Recorte | `SUBSTRING(s FROM 1 FOR 3)` | SQLite/Oracle/MySQL: `SUBSTR(s,1,3)` |
| Posição | `POSITION(sub IN s)` | SQLite: `INSTR`; SQL Server: `CHARINDEX` |
| Regex | PostgreSQL `~`; MySQL `REGEXP` | **SQLite não tem** por padrão |
| Sem acento | PostgreSQL `unaccent()` | SQLite exige ICU |

### Paginação

| Banco | Sintaxe |
|---|---|
| SQLite, PostgreSQL, MySQL, DuckDB | `LIMIT 10 OFFSET 20` |
| **Padrão ISO**, SQL Server 2012+, Oracle 12c+, PostgreSQL | `OFFSET 20 ROWS FETCH NEXT 10 ROWS ONLY` |
| SQL Server (antigo) | `SELECT TOP 10 ...` |
| Oracle (antigo) | `WHERE ROWNUM <= 10` — e cuidado, roda antes do `ORDER BY` |

### Inserir-ou-atualizar

```sql
-- SQLite ≥3.24, PostgreSQL ≥9.5, DuckDB
INSERT ... ON CONFLICT (chave) DO UPDATE SET col = excluded.col;
-- MySQL
INSERT ... ON DUPLICATE KEY UPDATE col = VALUES(col);
-- Oracle, SQL Server, PostgreSQL ≥15  (padrão ISO)
MERGE INTO ... USING ... ON ... WHEN MATCHED THEN ... WHEN NOT MATCHED THEN ...;
```

### Estatística e análise

| Função | SQLite | PostgreSQL | DuckDB | Oracle | SQL Server | MySQL |
|---|---|---|---|---|---|---|
| `stddev_samp` | ❌ | ✅ | ✅ | ✅ | `STDEV` | ✅ |
| `percentile_cont` | ❌ | ✅ | `quantile_cont` | ✅ | ✅ | ❌ |
| `corr` | ❌ | ✅ | ✅ | ✅ | ❌ | ❌ |
| `regr_slope` | ❌ | ✅ | ✅ | ✅ | ❌ | ❌ |
| `FILTER (WHERE …)` | ✅ ≥3.30 | ✅ | ✅ | ❌ | ❌ | ❌ |
| `ROLLUP`/`CUBE` | ❌ | ✅ | ✅ | ✅ | ✅ | `WITH ROLLUP` |
| `PIVOT` | ❌ | ❌ | ✅ | ✅ | ✅ | ❌ |
| `ASOF JOIN` | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ |
| Funções de janela | ✅ ≥3.25 | ✅ | ✅ | ✅ | ✅ | ✅ 8.0+ |
| `RANGE` com `INTERVAL` | ❌ | ✅ ≥11 | ✅ | ✅ | ❌ | ❌ |

### Outros

| Item | Divergência |
|---|---|
| Booleano | PostgreSQL tem; SQLite usa 0/1; MySQL é `TINYINT`; Oracle só desde 23c |
| `NULL` na ordenação | SQLite/PostgreSQL: primeiro em `ASC`. Oracle/SQL Server: último |
| Sensível a maiúsculas | PostgreSQL: sim. MySQL: depende do *collation*. SQL Server: depende |
| Aspas duplas | Identificador (padrão). MySQL usa crase e aceita `"texto"` |
| Limite de identificador | PostgreSQL: 63 caracteres, **truncado em silêncio** |
| Concorrência | SQLite: 1 escritor. Postgres: MVCC. Oracle: MVCC |

---

## 3. Como escrever SQL portátil (quando vale a pena)

**Quando vale:** produto que roda em vários bancos; código que vai migrar.
**Quando não vale:** análise interna que sempre vai rodar no banco da empresa —
aí usar `time_bucket` e `PIVOT` economiza horas.

Se for portar:

- Use `CASE WHEN` em vez de `FILTER`, `IIF`, `NVL`, `DECODE`.
- Use `COALESCE`, não `IFNULL`/`NVL`/`ISNULL`.
- Use `JOIN ... ON` explícito.
- Evite função de data específica: passe as fronteiras já calculadas como
  parâmetro, do lado da aplicação.
- Use `CAST(x AS tipo)`, não sintaxe `::` do PostgreSQL.
- Não confie na ordem sem `ORDER BY`.
- Não confie em limite de identificador maior que 30 caracteres.

**Opinião profissional:** SQL "portátil de verdade" costuma ser SQL ruim —
você abre mão dos recursos que resolvem o problema em troca de uma portabilidade
que 90% dos projetos nunca exercem. **Recomendação:** escreva idiomático para o
seu banco, isole os poucos trechos específicos, e resolva a portabilidade
quando ela for real.

---

## 4. SQLite × DuckDB: os dois embutidos

Confunde-se muito. São opostos no eixo que importa.

| | SQLite | DuckDB |
|---|---|---|
| Orientação | **Linha** | **Coluna** |
| Uso | Transacional (OLTP) | Analítico (OLAP) |
| Ganha em | Ler/gravar linha por chave | Varrer e agregar milhões |
| Paralelismo | Não | Sim, todos os núcleos |
| Lê CSV/Parquet direto | Não | **Sim** |
| Escrita concorrente | 1 escritor | Não é o caso de uso |
| Estatística embutida | Mínima | Completa |
| Estabilidade de formato | Compatível desde 2004 | Estável só a partir da 1.0 |

**Medido neste curso** (agregação por tag sobre 344.640 linhas):

| | Tempo |
|---|---|
| SQLite, banco já carregado | 41 ms |
| DuckDB, lendo CSV de 13,3 MB direto | 153 ms |
| DuckDB, sobre Parquet (3,3 MB) | **21 ms** |

**Interpretação honesta:** DuckDB não é magicamente mais rápido. Lendo CSV cru
ele perde, porque analisar texto custa. Sobre Parquet ganha, porque lê só as
colunas necessárias, já comprimidas.

**O ganho real do DuckDB para engenheiro químico não é velocidade — é atrito
zero.** `SELECT ... FROM 'export.csv'` sem criar tabela, sem importar, sem
declarar esquema. Do arquivo à resposta em trinta segundos.

**Use os dois:** DuckDB para explorar e analisar arquivo; SQLite ou PostgreSQL
para guardar dado que cresce ao longo do tempo.

---

## 5. Os bancos que você vai encontrar na indústria

### Oracle
Está no ERP, no MES, no LIMS. Você provavelmente terá acesso **somente
leitura** a uma réplica. Peculiaridades que vão te pegar:

- `DUAL`: `SELECT SYSDATE FROM DUAL` — precisa de um `FROM`.
- `NVL` no lugar de `COALESCE`; `DECODE` no lugar de `CASE`.
- **String vazia `''` é `NULL`** no Oracle. Só nele. Isso quebra lógica portada.
- `ROWNUM` é aplicado **antes** do `ORDER BY` — a causa clássica de "meu
  top 10 veio errado".
- `MINUS` no lugar de `EXCEPT`.

### SQL Server
Comum em MES e em planta com forte presença Microsoft.
- `TOP n`, `ISNULL`, `GETDATE()`, `+` para concatenar.
- `[colchetes]` para identificador.
- Bom ferramental gratuito (Azure Data Studio, SSMS).

### SAP HANA
Se a planta tem SAP, o dado de produção está lá. SQL razoavelmente padrão, mas
o modelo de dados do SAP é a dificuldade real: tabelas com nomes como `MSEG`,
`AUFK`, `AFPO`, milhares de colunas, documentação em alemão. **O SQL é o menor
dos seus problemas.**

### PI System (AVEVA, ex-OSIsoft)
O historiador mais comum em indústria de processo. Não é um banco SQL, mas
**expõe SQL**: `PI SQL Client` (ODBC e OLE DB) e `PI OLEDB Enterprise` para o
PI AF, através do `PI SQL Data Access Server (RTQP)`.

```sql
-- forma típica de consulta ao PI AF via PI SQL Client
SELECT a.Name, ad.Value, ad.Time
  FROM [MinhaBase].[Asset].[ElementAttribute] a
  JOIN [MinhaBase].[Data].[Archive] ad ON ad.ElementAttributeID = a.ID
 WHERE a.Element_Name = 'R-101'
   AND ad.Time BETWEEN '2026-07-01' AND '2026-07-02';
```

⚠️ Não é SQL padrão, é somente leitura, e o desempenho depende inteiramente de
como o AF foi modelado. **Na prática, a maioria das equipes extrai do PI para
um banco relacional** e faz a análise lá — porque o PI é ótimo em guardar sinal
e ruim em relacionar com LIMS, ERP e apontamento. Ver
[30-engenharia-quimica.md](30-engenharia-quimica.md).

---

## 6. Migração entre bancos

Ordem de dificuldade crescente:

| O que | Dificuldade |
|---|---|
| Dado | Fácil — CSV, ou ferramenta de ETL |
| Esquema | Médio — tipos e restrições traduzem quase sempre |
| Consultas | Médio — datas e funções de texto |
| Procedimentos armazenados | **Difícil** — PL/SQL, T-SQL e PL/pgSQL são linguagens diferentes |
| Comportamento de concorrência | **Difícil e invisível** — código que funcionava passa a dar *deadlock* |
| Desempenho | **Difícil** — os índices e planos são outros; tudo precisa ser re-medido |

**Ferramentas:** `pgloader` (para PostgreSQL, gratuita), AWS DMS, Ora2Pg.

**Aviso de campo:** migrações de banco de dados estouram prazo. O motivo quase
nunca é o dado — é o comportamento sutil (fuso, `NULL`, ordenação, isolamento)
que só aparece em produção. Orce o dobro do que parece.

---

## Autoteste

1. Qual porcentagem do SQL do dia a dia é portátil, e onde ficam as exceções?
2. Traduza `date_trunc('hour', ts)` para SQLite, Oracle e SQL Server.
3. Quais funções estatísticas faltam no SQLite, e o que fazer sem elas?
4. `FILTER (WHERE …)` funciona em quais bancos? E qual o substituto universal?
5. SQLite × DuckDB: qual a diferença fundamental e quando usar cada um?
6. Por que o DuckDB perdeu para o SQLite lendo CSV?
7. Cite três peculiaridades do Oracle que quebram código portado.
8. O que é o PI SQL Client, e por que times acabam extraindo o dado do PI?
9. Numa migração, o que é mais difícil que o dado? Cite três coisas.

---

*Próximo: [24-sql-com-python.md](24-sql-com-python.md).*
