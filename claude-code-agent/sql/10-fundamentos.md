# 10 — Fundamentos: o modelo relacional

Nível: iniciante → intermediário · Data: 13/08/2026

Aqui está o vocabulário e o modelo mental. Sem isto, SQL é decoreba de sintaxe
e você trava no primeiro problema que não é igual ao do tutorial.

---

## 1. A ideia central em uma frase

> **Um banco relacional guarda fatos em tabelas, e o SQL combina tabelas para
> produzir novas tabelas.**

Toda consulta SQL recebe tabelas e devolve uma tabela. Sempre. Esse fechamento
— entra tabela, sai tabela — é o que permite encaixar consulta dentro de
consulta indefinidamente, e é a razão de o modelo ser tão composicional.

---

## 2. Vocabulário: os dois nomes de cada coisa

Todo conceito tem um nome matemático (de Codd, 1970) e um nome prático (do
SQL). Você vai encontrar os dois.

| Matemático (modelo relacional) | SQL / prático | O que é |
|---|---|---|
| Relação | **Tabela** | Um conjunto de fatos do mesmo formato |
| Tupla | **Linha** (*row*, registro) | Um fato |
| Atributo | **Coluna** (*column*, campo) | Uma propriedade do fato |
| Domínio | **Tipo de dado** | O conjunto de valores possíveis daquele atributo |
| Cardinalidade | Número de linhas | |
| Grau | Número de colunas | |
| Chave candidata | — | Conjunto mínimo de colunas que identifica a linha |
| Chave primária | `PRIMARY KEY` | A chave candidata escolhida |
| Chave estrangeira | `FOREIGN KEY` | Coluna que referencia a chave de outra tabela |

Exemplo, com a tabela `leitura` do [projeto-modelo](07-projeto-modelo/):

```
                 ┌──────────── grau = 4 colunas ────────────┐
                 tag_id     ts                 valor  qualidade   ← atributos
               ┌ ─────────  ──────────────────  ─────  ─────────
cardinalidade  │ TI-101     2026-07-01 10:00:00 179.8  BOA        ← uma tupla
= 344.640      │ TI-101     2026-07-01 10:01:00 180.3  BOA
linhas         │ PI-101     2026-07-01 10:00:00   2.71 BOA
               └ ...
                 └──── chave primária ────┘
```

### A diferença que importa: relação é **conjunto**, tabela é **multiconjunto**

Na teoria de Codd, uma relação é um **conjunto** de tuplas: sem duplicatas e
sem ordem. Na prática do SQL, uma tabela é um ***bag*** (multiconjunto):
**pode ter linhas duplicadas**.

Essa divergência entre teoria e implementação é a fonte de vários
comportamentos que confundem:

- `SELECT tag_id FROM leitura` devolve 344.640 linhas com 8 valores distintos.
  Numa relação de verdade devolveria 8.
- Por isso existe `DISTINCT` — que não seria necessário no modelo puro.
- `UNION` remove duplicatas (fiel à teoria) e `UNION ALL` não (fiel à prática,
  e mais rápido).

Codd considerava isso um erro do SQL. Ele estava tecnicamente certo e
comercialmente derrotado: remover duplicata custa uma ordenação, e ninguém
quis pagar isso em toda consulta.

### A ordem das linhas não existe

Uma tabela **não tem ordem**. O banco pode devolver as linhas em qualquer
ordem, e a ordem pode mudar entre duas execuções da mesma consulta se o plano
mudar.

```sql
SELECT * FROM leitura LIMIT 5;                  -- ordem NÃO garantida
SELECT * FROM leitura ORDER BY ts LIMIT 5;      -- ordem garantida
```

Se a ordem importa, escreva `ORDER BY`. Depender da "ordem natural" é um bug
esperando a próxima versão do banco.

---

## 3. Chaves

### Chave primária

O conjunto **mínimo** de colunas que identifica cada linha de forma única.

```sql
PRIMARY KEY (tag_id, ts)     -- chave COMPOSTA: instrumento + instante
```

Duas propriedades garantidas: **única** e **não nula**.

**Chave natural × chave artificial (*surrogate*)** — o debate mais antigo da
modelagem:

| | Natural | Artificial |
|---|---|---|
| Exemplo | `(tag_id, ts)`, CPF, código do produto | `id INTEGER PRIMARY KEY AUTOINCREMENT`, UUID |
| A favor | Tem significado; evita junção para saber o que é; impede duplicata de verdade | Nunca muda; é pequena; junções são baratas |
| Contra | Se o significado mudar, você reescreve o mundo (a empresa mudou o padrão de tag…) | Não impede duplicata lógica; exige junção para entender |

**Minha recomendação profissional**, e é opinião fundamentada, não consenso:
use a chave natural quando ela é genuinamente imutável e curta — e
`(tag_id, ts)` de série temporal é o caso mais claro que existe, porque ela é
o dado. Use artificial quando a chave natural é longa, composta de quatro
colunas, ou pode mudar. **Nunca** use artificial *e* deixe de criar a `UNIQUE`
sobre a chave natural: aí você não tem chave nenhuma, só um contador, e as
duplicatas entram.

### Chave estrangeira

Diz que o valor desta coluna **tem de existir** naquela outra tabela.

```sql
tag_id TEXT NOT NULL REFERENCES tag(tag_id)
```

É o que impede uma leitura de um instrumento que não existe no cadastro. Chama-se
**integridade referencial**.

⚠️ **No SQLite ela é desligada por padrão.** `PRAGMA foreign_keys = ON`, e o
PRAGMA vale por conexão — cada vez que seu programa conecta, precisa repetir.
Sem isso, todo `REFERENCES` do seu esquema é comentário.

### Ações em cascata

```sql
tag_id TEXT REFERENCES tag(tag_id) ON DELETE CASCADE     -- apaga junto
tag_id TEXT REFERENCES tag(tag_id) ON DELETE RESTRICT    -- proíbe apagar o pai
tag_id TEXT REFERENCES tag(tag_id) ON DELETE SET NULL    -- órfão vira NULL
```

`CASCADE` em tabela de série temporal é uma arma carregada: apagar um tag
apaga silenciosamente 43 mil leituras. Em banco de processo, prefira
`RESTRICT` — que obriga alguém a pensar antes.

---

## 4. As oito operações que o SQL faz (álgebra relacional)

Todo `SELECT`, por mais complicado, é uma composição destas operações. Saber
disso é o que permite raciocinar sobre uma consulta em vez de decorá-la.

| Operação | Símbolo | SQL | O que faz |
|---|---|---|---|
| Seleção | σ (sigma) | `WHERE` | Escolhe **linhas** |
| Projeção | π (pi) | `SELECT col1, col2` | Escolhe **colunas** |
| Produto cartesiano | × | `CROSS JOIN` | Toda linha de A com toda de B |
| Junção | ⋈ | `JOIN ... ON` | Produto + seleção |
| União | ∪ | `UNION` | Empilha duas tabelas compatíveis |
| Diferença | − | `EXCEPT` | O que está em A e não em B |
| Interseção | ∩ | `INTERSECT` | O que está nas duas |
| Renomeação | ρ (rho) | `AS` | Troca o nome |

Só isso. Agregação (`GROUP BY`) e funções de janela (`OVER`) são **extensões**
posteriores — não fazem parte da álgebra original, e é por isso que se comportam
de forma um pouco estranha em relação ao resto.

Detalhe formal, com as provas, em [60-teoria-avancada.md](60-teoria-avancada.md).

---

## 5. As três sublinguagens do SQL

Todo comando SQL cai numa destas famílias. Os nomes aparecem em toda
documentação e em toda entrevista de emprego.

| Sigla | Nome | Comandos | Para quê |
|---|---|---|---|
| **DQL** | *Data Query Language* | `SELECT` | Perguntar. É 90% do que você vai fazer |
| **DML** | *Data Manipulation Language* | `INSERT`, `UPDATE`, `DELETE`, `MERGE` | Mudar dados |
| **DDL** | *Data Definition Language* | `CREATE`, `ALTER`, `DROP`, `TRUNCATE` | Mudar a **estrutura** |
| **DCL** | *Data Control Language* | `GRANT`, `REVOKE` | Permissões |
| **TCL** | *Transaction Control* | `BEGIN`, `COMMIT`, `ROLLBACK` | Transações |

(Muita gente junta DQL dentro de DML. Não muda nada na prática.)

**Uma diferença que morde:** na maioria dos bancos, DDL é **auto-commit** —
um `CREATE TABLE` no meio de uma transação confirma tudo que veio antes e não
pode ser desfeito. PostgreSQL e SQLite são exceções felizes: lá o DDL é
transacional e um `ROLLBACK` desfaz até o `CREATE TABLE`. No Oracle e no
MySQL, não é. Descobrir isso durante uma migração de produção é uma noite ruim.

---

## 6. Independência de dados: a razão de tudo isto existir

Este é o conceito que Codd inventou e que justifica o modelo inteiro.

**Antes de 1970**, o programa precisava saber a estrutura física: em que
arquivo, em que ordem, seguindo qual ponteiro. Mudar a organização física
quebrava todos os programas.

Codd separou em três níveis (formalizados depois na **arquitetura ANSI/SPARC**,
1975):

```
┌─────────────────────────────────────────────┐
│  NÍVEL EXTERNO  — o que cada usuário vê     │  views, permissões
│  "v_batelada tem rendimento_pct"            │
├─────────────────────────────────────────────┤
│  NÍVEL CONCEITUAL — o esquema lógico        │  tabelas, colunas, restrições
│  "batelada(id, carga_kg, produzido_kg)"     │
├─────────────────────────────────────────────┤
│  NÍVEL INTERNO   — como está gravado        │  páginas, B-tree, compressão
│  "página 4021, offset 88, B-tree em ts"     │
└─────────────────────────────────────────────┘
```

- **Independência física**: criar um índice, mudar a compressão, trocar o disco
  — nada disso muda uma consulta.
- **Independência lógica**: uma view isola o usuário de mudanças no esquema.
  Você reorganiza a tabela por baixo e o relatório do gerente continua rodando.

**Isto é o que faz uma consulta de 1995 rodar hoje.** É a maior conquista de
engenharia do modelo relacional, e explica por que ele sobreviveu a todas as
ondas que prometeram substituí-lo: orientado a objetos (anos 90), XML (2000s),
NoSQL (2010s).

### Regra dos cinco porquês, aplicada

> **Por que** o SQL é declarativo?
> Porque assim o programa não precisa saber como o dado está guardado.
>
> **Por que** isso importa?
> Porque, antes, mudar o arquivo quebrava todos os programas.
>
> **Por que** quebrava?
> Porque o código tinha o caminho de acesso embutido — o programa navegava a
> estrutura, seguindo ponteiros (modelos hierárquico e de rede, CODASYL, 1969).
>
> **Por que** era assim?
> Porque em 1965 a memória custava cerca de US$ 1 por byte e o disco era
> caríssimo: era inviável gastar ciclo de CPU procurando o dado; o programador
> tinha de dizer exatamente onde ele estava.
>
> **Por que** deixou de ser assim?
> Porque hardware ficou barato e programador ficou caro. Essa inversão de
> custo — e não uma descoberta teórica — é a razão econômica de o modelo
> relacional ter vencido. Codd publicou em 1970; o primeiro produto comercial
> saiu em 1979; a adoção em massa veio nos anos 80, quando o custo do hardware
> tinha caído o suficiente para pagar a conta do otimizador.
>
> **Parada legítima:** trade-off econômico explícito. O modelo relacional é
> tecnicamente *mais lento* que navegar ponteiros à mão. Ele venceu porque o
> tempo de programador passou a valer mais que o tempo de CPU.

---

## 7. O que o banco garante: ACID

| Letra | Nome | Garante | Se faltar |
|---|---|---|---|
| **A** | Atomicidade | Tudo ou nada | Meia transferência: saiu de uma conta e não entrou na outra |
| **C** | Consistência | As restrições valem antes e depois | Leitura de um instrumento inexistente |
| **I** | Isolamento | Transações simultâneas não veem o meio uma da outra | Relatório somando um estado que nunca existiu |
| **D** | Durabilidade | Depois do `COMMIT`, sobrevive a queda de energia | Perda de dado confirmado |

**Por que isso importa em planta:** o coletor grava leituras enquanto o
relatório mensal roda. Sem isolamento, o relatório poderia somar metade de uma
carga. Sem durabilidade, um pico de energia apagaria as últimas duas horas de
processo — justamente as que interessam, porque foi o pico que derrubou a
planta.

Detalhe em [20-dml-e-transacoes.md](20-dml-e-transacoes.md).

---

## 8. Modelos alternativos, e quando fazem sentido

Honestidade profissional: o relacional não é sempre a resposta.

| Modelo | Exemplo | Bom para | Ruim para |
|---|---|---|---|
| **Relacional** | PostgreSQL, Oracle, SQLite | Dado estruturado, relações, integridade, consulta ad hoc | Documento sem esquema fixo; escala horizontal extrema |
| **Documento** | MongoDB | Estrutura variável por registro | Junção; consistência entre documentos |
| **Chave-valor** | Redis | Cache, sessão, contador | Qualquer consulta que não seja por chave |
| **Colunar** | ClickHouse, DuckDB, BigQuery | Varrer bilhões de linhas agregando | Atualizar uma linha |
| **Série temporal** | InfluxDB, TimescaleDB | Dado de sensor em altíssima frequência | Relações complexas |
| **Grafo** | Neo4j | Caminhos, redes, "quem conecta com quem" | Agregação em massa |

**Para dado de processo químico**, a resposta prática em 2026:

- **até ~100 milhões de linhas** → PostgreSQL puro resolve, e resolve bem;
- **mais que isso, com muita escrita** → TimescaleDB (extensão do PostgreSQL)
  ou o historiador proprietário que a planta já tem;
- **análise sobre exportação em arquivo** → DuckDB;
- **aprendizado e protótipo** → SQLite.

Repare que **todos falam SQL**. O modelo relacional venceu tão completamente
que até os concorrentes adotaram a linguagem: InfluxDB migrou para SQL na
versão 3, o MongoDB tem um dialeto de agregação inspirado nele, e todo produto
"NoSQL" sério de 2026 tem uma camada SQL. Ver
[65-estado-da-arte.md](65-estado-da-arte.md).

---

## Autoteste

1. Qual a diferença entre uma *relação* (Codd) e uma *tabela* (SQL)? Cite uma
   consequência prática.
2. Por que a ordem das linhas não é garantida sem `ORDER BY`?
3. Chave natural ou artificial para uma tabela de leituras de sensor? Defenda.
4. O que a chave estrangeira garante, e o que é preciso fazer no SQLite para
   que ela funcione de verdade?
5. Liste as oito operações da álgebra relacional e a cláusula SQL de cada uma.
6. O que é independência física de dados? Dê um exemplo do seu trabalho.
7. Explique as quatro letras de ACID com um exemplo de planta para cada.
8. Aplique os cinco porquês: por que o SQL é declarativo? Onde a cadeia para?
9. Cite dois casos em que **não** usar banco relacional é a decisão certa.

---

*Próximo: [11-historia.md](11-historia.md).*
