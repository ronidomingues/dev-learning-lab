# 21 — Índices e desempenho

Nível: intermediário → avançado · Data: 13/08/2026 · Medições **executadas** sobre 344.640 linhas

Um índice é a diferença entre 0,1 ms e 18 ms — ou entre 2 segundos e 40
minutos, na escala de produção. Este arquivo mostra como decidir, não como
adivinhar.

---

## 1. O que é um índice

Um índice é uma **estrutura ordenada auxiliar** que aponta para as linhas.
A analogia clássica é o índice remissivo de um livro: em vez de ler as 600
páginas procurando "azeotropia", você vai ao índice, acha "azeotropia — p. 214"
e pula direto.

Quase todo índice de banco relacional é uma **B-tree** (mais precisamente
B⁺-tree): uma árvore balanceada e larga, com centenas de chaves por nó,
projetada para minimizar leituras de disco. Buscar em 100 milhões de linhas
custa 4 ou 5 acessos, não 100 milhões.

```
                      [ 2026-07-10 | 2026-07-20 ]          ← raiz
                     /              |             \
      [07-03|07-07]       [07-13|07-17]      [07-24|07-28]  ← nós internos
       /    |    \          /   |   \           /   |   \
     ...  folhas com ponteiro para as linhas ...            ← folhas
```

---

## 2. As medições

Todas contra `leitura` (344.640 linhas), SQLite 3.37.2:

| Consulta | Tempo | Plano |
|---|---|---|
| `WHERE tag_id='TI-101' AND ts>=… AND ts<…` | **0,1 ms** | `SEARCH USING PRIMARY KEY (tag_id=? AND ts>? AND ts<?)` |
| `WHERE ts='2026-07-10 03:14:00'` | **<0,1 ms** | `SEARCH USING INDEX ix_leitura_ts (ts=?)` |
| `WHERE valor > 195` (sem índice) | **17,8 ms** | `SCAN leitura` |
| ... o mesmo, com índice em `valor` | **0,5 ms** | `SEARCH USING COVERING INDEX` |
| `WHERE substr(ts,1,10)='2026-07-10' AND tag_id='TI-101'` | **5,0 ms** | `SEARCH USING PRIMARY KEY (tag_id=?)` |
| ... reescrito como `ts>=… AND ts<…` | **0,1 ms** | `SEARCH USING PRIMARY KEY (tag_id=? AND ts>? AND ts<?)` |

Duas conclusões, e são as que pagam a conta:

- **Índice certo: 36× mais rápido** (17,8 → 0,5 ms).
- **Reescrever a consulta para não aplicar função na coluna: 50× mais rápido**
  (5,0 → 0,1 ms), **sem criar índice nenhum**.

A segunda é gratuita. É por onde começar.

---

## 3. *Sargable*: a palavra que vale saber

**SARG** = *Search ARGument*. Um predicado é ***sargable*** quando o banco
consegue usá-lo para navegar o índice. Deixa de ser quando a coluna está
"embrulhada" em alguma coisa.

| ❌ Não usa índice | ✅ Usa índice |
|---|---|
| `substr(ts,1,10) = '2026-07-10'` | `ts >= '2026-07-10' AND ts < '2026-07-11'` |
| `strftime('%Y',ts) = '2026'` | `ts >= '2026-01-01' AND ts < '2027-01-01'` |
| `UPPER(tag_id) = 'TI-101'` | `tag_id = 'TI-101'` (e normalize na **carga**) |
| `valor * 1.8 + 32 > 350` | `valor > (350-32)/1.8` |
| `CAST(valor AS TEXT) LIKE '19%'` | `valor >= 19 AND valor < 20` |
| `tag_id LIKE '%101'` | `tag_id LIKE 'TI-%'` |
| `ts + 1 > '2026-07-10'` | `ts > date('2026-07-10','-1 day')` |

**A regra única:** deixe a coluna sozinha de um lado do operador; toda a
matemática vai para o lado da constante.

**A exceção:** índices sobre expressão (*expression index*), onde você indexa
justamente a função:

```sql
CREATE INDEX ix_dia ON leitura(substr(ts,1,10));   -- SQLite ≥3.9, PostgreSQL
```
Agora `WHERE substr(ts,1,10)='2026-07-10'` usa índice. Vale quando você **não
pode** reescrever a consulta (ferramenta de BI que gera o SQL, por exemplo).

---

## 4. Índice composto: a ordem é tudo

```sql
PRIMARY KEY (tag_id, ts)
```

Este índice serve para:

| Consulta | Usa? |
|---|---|
| `WHERE tag_id='TI-101'` | ✅ prefixo |
| `WHERE tag_id='TI-101' AND ts BETWEEN … ` | ✅ ideal |
| `WHERE tag_id IN (…) AND ts >= …` | ✅ |
| `WHERE ts >= …` **sem** `tag_id` | ❌ — precisa de índice separado em `ts` |
| `ORDER BY tag_id, ts` | ✅ sem ordenar |
| `ORDER BY ts` | ❌ |

**A regra do prefixo à esquerda:** um índice `(a, b, c)` serve para consultas
sobre `(a)`, `(a,b)` e `(a,b,c)` — **nunca** para `(b)` ou `(c)` sozinhos.

Pense como uma lista telefônica ordenada por sobrenome e depois nome: achar
"Silva, João" é imediato; achar "todos os João" exige ler tudo.

**Como escolher a ordem das colunas:**

1. Colunas de **igualdade** primeiro, colunas de **faixa** por último.
2. Entre as de igualdade, a mais seletiva primeiro (empate técnico, na prática).
3. Colunas do `ORDER BY` depois, na mesma ordem e direção — assim o banco pula
   a ordenação.

Por isso `(tag_id, ts)`: `tag_id` é igualdade, `ts` é faixa.

---

## 5. Índice de cobertura

Se **todas** as colunas de que a consulta precisa estão no índice, o banco
responde sem tocar na tabela. Isso é um *covering index*, e o ganho é grande.

```sql
CREATE INDEX ix_cobre ON leitura(tag_id, ts, valor);

SELECT ts, valor FROM leitura WHERE tag_id='TI-101' AND ts >= '…';
-- plano: SEARCH ... USING COVERING INDEX ix_cobre
```

Foi assim que a consulta `WHERE valor > 195` caiu de 17,8 para **0,5 ms**: o
índice em `valor` cobria `COUNT(*)`, que não precisa de mais nada.

⚠️ Este é o argumento definitivo contra `SELECT *`: com `*`, **nenhum** índice
cobre, e o banco sempre vai à tabela.

---

## 6. Índices especiais

| Tipo | Sintaxe | Para quê |
|---|---|---|
| **Único** | `CREATE UNIQUE INDEX ...` | Garante unicidade e acelera |
| **Parcial** | `CREATE INDEX ... WHERE qualidade='RUIM'` | Índice pequeno para consulta que só olha um subconjunto |
| **Sobre expressão** | `CREATE INDEX ... (substr(ts,1,10))` | Quando a consulta não pode ser reescrita |
| **Descendente** | `CREATE INDEX ... (ts DESC)` | Para `ORDER BY ts DESC LIMIT n` |
| GIN / GiST | PostgreSQL | Busca textual, JSON, geometria, faixas |
| BRIN | PostgreSQL | **Tabelas enormes, naturalmente ordenadas** — perfeito para série temporal: índice minúsculo |

**BRIN merece um parágrafo para quem trabalha com dado de planta.** Em vez de
apontar para cada linha, ele guarda o valor mínimo e máximo de cada bloco de
páginas. Para uma tabela de 100 milhões de leituras inseridas em ordem
cronológica, um índice BRIN em `ts` ocupa alguns **kilobytes** onde uma B-tree
ocuparia gigabytes, e responde consultas por faixa quase tão bem. Só existe no
PostgreSQL, e é a razão técnica mais forte para preferi-lo ao SQLite em
histórico grande.

---

## 7. O custo do índice

| Operação | Efeito de ter N índices |
|---|---|
| `SELECT` com filtro coberto | Muito mais rápido |
| `INSERT` | Mais lento: atualiza N estruturas |
| `UPDATE` de coluna indexada | Mais lento |
| `DELETE` | Mais lento |
| Espaço | Cada índice ocupa; um índice de 3 colunas pode ter metade do tamanho da tabela |

**Índice não é grátis.** Numa tabela de série temporal com escrita contínua, um
índice a mais é escrita a mais em cada leitura gravada, para sempre.

**Como decidir:**

```sql
-- ache os índices que ninguém usa (PostgreSQL)
SELECT relname, indexrelname, idx_scan
  FROM pg_stat_user_indexes WHERE idx_scan = 0;
```
No SQLite não há essa estatística; a análise é manual, olhando os planos das
consultas que importam.

---

## 8. Ler o plano de execução

### SQLite

```sql
EXPLAIN QUERY PLAN
SELECT ... ;
```

| Aparece | Significa | Bom? |
|---|---|---|
| `SCAN tabela` | Varre tudo | Ruim, se a tabela é grande |
| `SCAN tabela USING INDEX ix` | Varre o índice inteiro | Melhor que varrer a tabela |
| `SEARCH tabela USING INDEX ix (col=?)` | Busca direcionada | Bom |
| `SEARCH ... USING PRIMARY KEY` | Idem, pela chave | Ótimo |
| `USING COVERING INDEX` | Respondeu só com o índice | Ótimo |
| `USE TEMP B-TREE FOR ORDER BY` | Ordenou em memória/disco | Um índice na ordem certa elimina |
| `USE TEMP B-TREE FOR GROUP BY` | Idem, para agrupar | Idem |
| `CORRELATED SCALAR SUBQUERY` | Subconsulta rodando por linha | Suspeito — considere junção ou janela |

No projeto-modelo: `python3 scripts/consultar.py --plano 05`

### PostgreSQL

```sql
EXPLAIN (ANALYZE, BUFFERS) SELECT ...;
```

`EXPLAIN` sozinho estima; **`ANALYZE` executa de verdade e mede**. Compare
`rows=` estimado com `actual rows=`: divergência de ordem de grandeza indica
estatística desatualizada — rode `ANALYZE` na tabela.

Ferramenta que ajuda muito a ler planos grandes: <https://explain.dalibo.com>
(gratuita, e processa localmente no navegador).

---

## 9. Estatísticas e o otimizador

O otimizador escolhe o plano com base em **estatísticas**: quantas linhas,
quantos valores distintos, como estão distribuídos. Se as estatísticas estão
velhas, ele escolhe mal.

```sql
ANALYZE;                        -- SQLite: grava em sqlite_stat1
ANALYZE leitura;                -- PostgreSQL: uma tabela
```

O PostgreSQL faz isso sozinho (autovacuum). **O SQLite não** — rode `ANALYZE`
depois de uma carga grande. O gerador do projeto-modelo faz isso ao final.

**O caso em que o otimizador erra e você precisa ajudar:** correlação entre
colunas. Se `equipamento_id='R-101'` e `area='100'` são praticamente a mesma
coisa, o otimizador multiplica as seletividades e estima 100× menos linhas do
que existem, escolhendo nested loop onde deveria escolher hash. PostgreSQL ≥ 10
tem `CREATE STATISTICS` para declarar essa dependência. É raro precisar, mas
quando precisa não há outro jeito.

---

## 10. Receita para consulta lenta

Em ordem. Não pule etapas — a maioria dos problemas morre no passo 3.

1. **Meça.** Sem número, você está adivinhando.
   ```bash
   sqlite3 planta.db ".timer on" "SELECT ..."
   ```
2. **Leia o plano.** `EXPLAIN QUERY PLAN`. Achou `SCAN` numa tabela grande?
3. **Verifique se o predicado é *sargable*.** Tem função na coluna? Corrija —
   é de graça e costuma ser o problema.
4. **Confira as estatísticas.** `ANALYZE`.
5. **Reduza o conjunto cedo.** Filtre antes de juntar e antes de agregar.
6. **Verifique a cardinalidade das junções.** Um leque acidental multiplica
   trabalho e ainda dá número errado.
7. **Considere um índice.** Composto, na ordem das perguntas, preferindo
   cobertura.
8. **Considere pré-agregar.** Tabela de resumo horário resolve o que índice
   nenhum resolve.
9. **Só então**, considere trocar de ferramenta (DuckDB, TimescaleDB,
   particionamento).

**O erro mais comum:** pular direto ao passo 7 e sair criando índices. Índice
demais deixa a escrita lenta e não conserta consulta não-*sargable*.

---

## 11. Escala: quando o SQLite deixa de servir

| Volume | SQLite | PostgreSQL | Colunar (DuckDB/ClickHouse) |
|---|---|---|---|
| < 1 M linhas | Ótimo | Ótimo | Exagero |
| 1 M – 50 M | Bom | Ótimo | Bom |
| 50 M – 500 M | Sofre (só nested loop; sem paralelismo) | Bom, com índice e partição | Ótimo |
| > 500 M | Não | TimescaleDB / partição | Ótimo |
| Muitos escritores simultâneos | **Um escritor por vez** | Ótimo | Não é o caso de uso |
| Agregação sobre tudo | Lento (linha a linha) | Médio | **Ótimo** (colunar + vetorizado) |

Os três limites reais do SQLite, e vale saber quais são:

1. **Um escritor por vez.** Com WAL, leitores não bloqueiam, mas só um processo
   escreve. Para um coletor único gravando, é suficiente; para dez, não.
2. **Só nested loop join.** Juntar duas tabelas grandes sem índice adequado é
   inviável.
3. **Sem paralelismo.** Uma consulta usa um núcleo. O DuckDB usa todos.

E não é limite: o SQLite aguenta bancos de terabytes e é usado assim em
produção. O que ele não faz é concorrência de escrita e análise paralela.

---

## Autoteste

1. O que é um índice, e por que buscar em 100 milhões de linhas custa ~5
   acessos?
2. Defina *sargable* e dê três exemplos de predicado que não é.
3. `substr(ts,1,10)='2026-07-10'` custou 5,0 ms; a versão com faixa, 0,1 ms.
   Explique.
4. O índice `(tag_id, ts)` serve para `WHERE ts >= …` sem `tag_id`? Por quê?
5. O que é índice de cobertura, e qual a relação disso com `SELECT *`?
6. Cite o custo de manter um índice.
7. O que significa `USE TEMP B-TREE FOR ORDER BY`, e como eliminá-lo?
8. Por que rodar `ANALYZE` no SQLite depois de uma carga grande?
9. Quando um índice BRIN vence uma B-tree, e por que isso interessa a dado de
   planta?
10. Cite os três limites reais do SQLite e diga qual deles te afeta.

---

*Próximo: [22-views-e-analitico.md](22-views-e-analitico.md).*
