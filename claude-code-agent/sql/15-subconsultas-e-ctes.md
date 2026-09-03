# 15 — Subconsultas e CTEs

Nível: intermediário · Data: 13/08/2026

Consulta dentro de consulta. É o que permite compor perguntas complexas a
partir de perguntas simples — e é onde a legibilidade morre, se você não
souber organizar.

---

## 1. Os quatro tipos de subconsulta

### 1.1 Escalar — devolve **um** valor

Cabe em qualquer lugar onde caberia uma constante.

```sql
SELECT batelada_id, rendimento_pct,
       rendimento_pct - (SELECT AVG(rendimento_pct) FROM v_batelada) AS desvio
  FROM v_batelada;
```

⚠️ Se devolver mais de uma linha, é erro em quase todo banco (o SQLite pega
silenciosamente a primeira — mais uma permissividade perigosa).

### 1.2 De lista — devolve **uma coluna**, várias linhas

```sql
SELECT * FROM leitura
 WHERE tag_id IN (SELECT tag_id FROM tag WHERE grandeza = 'temperatura');
```

⚠️ **`NOT IN` com `NULL` na subconsulta devolve zero linhas.** Sempre. Se a
coluna da subconsulta é anulável, use `NOT EXISTS`.

### 1.3 Correlacionada — referencia a consulta externa

```sql
SELECT b.batelada_id
  FROM batelada b
 WHERE EXISTS (SELECT 1 FROM analise_lab a
                WHERE a.batelada_id = b.batelada_id     -- ← referência externa
                  AND a.valor > a.lim_sup);
```

Conceitualmente roda uma vez **por linha** da consulta externa. Na prática, um
otimizador decente reescreve como semi-junção e roda uma vez só. O SQLite às
vezes reescreve, às vezes não — verifique com `EXPLAIN QUERY PLAN` quando a
tabela externa for grande.

### 1.4 Derivada — no `FROM`

```sql
SELECT * FROM (
    SELECT tag_id, AVG(valor) AS m FROM leitura GROUP BY tag_id
) AS x
 WHERE x.m > 100;
```

Precisa de apelido em quase todo banco. É a forma antiga da CTE.

---

## 2. `EXISTS` × `IN` × `JOIN`

Três formas de perguntar "tem correspondência do outro lado?".

```sql
-- EXISTS: não multiplica linhas, para na primeira que achar
SELECT * FROM batelada b
 WHERE EXISTS (SELECT 1 FROM analise_lab a WHERE a.batelada_id = b.batelada_id);

-- IN: idem, mas materializa a lista
SELECT * FROM batelada
 WHERE batelada_id IN (SELECT batelada_id FROM analise_lab);

-- JOIN: MULTIPLICA — 4 análises por batelada = 4 linhas por batelada
SELECT DISTINCT b.* FROM batelada b JOIN analise_lab a USING (batelada_id);
```

| | `EXISTS` | `IN` | `JOIN` |
|---|---|---|---|
| Multiplica linhas? | Não | Não | **Sim** |
| Sofre com `NULL`? | Não | **Sim** no `NOT IN` | Não |
| Traz colunas do outro lado? | Não | Não | Sim |
| Recomendação | **Padrão para "existe?"** | Ok para lista pequena e sem nulo | Só quando precisa das colunas |

**Regra prática:** se você só quer *filtrar*, use `EXISTS`. Se precisa das
colunas do outro lado, use `JOIN` e cuide da cardinalidade. `DISTINCT` para
consertar `JOIN` é sintoma de escolha errada.

---

## 3. CTE (`WITH`): o organizador

```sql
WITH nome AS (
    SELECT ...
),
outro AS (
    SELECT ... FROM nome ...          -- pode usar a anterior
)
SELECT ... FROM outro;
```

Compare as duas formas da mesma pergunta:

```sql
-- aninhada: lê-se de dentro para fora, o que ninguém consegue
SELECT * FROM (
  SELECT tag_id, m FROM (
    SELECT tag_id, AVG(valor) AS m FROM (
      SELECT * FROM leitura WHERE qualidade='BOA'
    ) GROUP BY tag_id
  ) WHERE m > 100
) ORDER BY m DESC;
```

```sql
-- com CTE: lê-se de cima para baixo, como um procedimento
WITH bom AS (
    SELECT * FROM leitura WHERE qualidade = 'BOA'
),
medias AS (
    SELECT tag_id, AVG(valor) AS m FROM bom GROUP BY tag_id
)
SELECT * FROM medias WHERE m > 100 ORDER BY m DESC;
```

Mesmo plano de execução, mesma velocidade. **Diferença é humana** — e essa
diferença é a que determina se alguém encontra o bug antes da reunião.

### CTE é otimizada ou materializada?

Ponto importante e que confunde:

| Banco | Comportamento |
|---|---|
| SQLite | Achata (*inline*) por padrão; `AS MATERIALIZED` força materializar |
| PostgreSQL ≥ 12 | Achata quando usada uma vez; materializa quando usada várias. `AS [NOT] MATERIALIZED` controla |
| PostgreSQL ≤ 11 | **Sempre materializava** — CTE era barreira de otimização, e isso era usado como truque |
| Oracle, SQL Server | Decide pelo custo |
| DuckDB | Achata |

**Consequência:** em PostgreSQL antigo, jogar um filtro numa CTE podia deixar a
consulta *mais lenta*, porque impedia o *predicate pushdown*. Se você encontrar
código velho com CTEs "desnecessárias", pode ser isso — era intencional.

Quando forçar materialização é útil de verdade: quando a CTE é cara e usada
várias vezes, ou quando ela contém uma função com efeito colateral.

---

## 4. CTE recursiva

Para hierarquia, série gerada, ou qualquer coisa que se define em termos de si
mesma.

```sql
WITH RECURSIVE nome(colunas) AS (
    <caso base>                       -- roda uma vez
    UNION ALL
    <passo> FROM nome WHERE <parada>  -- roda até não produzir linha nova
)
SELECT * FROM nome;
```

### Gerar uma série de tempo

```sql
WITH RECURSIVE minuto(ts) AS (
    SELECT '2026-07-14 02:00:00'
    UNION ALL
    SELECT datetime(ts, '+1 minute') FROM minuto
     WHERE ts < '2026-07-14 06:00:00'
)
SELECT COUNT(*) FROM minuto;      -- 241
```

**Uso real:** achar os instantes que faltam no historiador, comparando o
calendário gerado com o que existe. Ver o exemplo 11 de
[06-exemplos.md](06-exemplos.md), que devolve **120 instantes faltando** no
banco do projeto-modelo.

### Percorrer hierarquia

Para uma estrutura de produto (BOM), um fluxograma de processo, ou uma
hierarquia de equipamentos:

```sql
WITH RECURSIVE arvore(equipamento_id, nivel, caminho) AS (
    SELECT equipamento_id, 0, equipamento_id
      FROM equipamento WHERE pai_id IS NULL
    UNION ALL
    SELECT e.equipamento_id, a.nivel + 1, a.caminho || ' > ' || e.equipamento_id
      FROM equipamento e
      JOIN arvore a ON e.pai_id = a.equipamento_id
     WHERE a.nivel < 10                  -- proteção contra ciclo
)
SELECT * FROM arvore ORDER BY caminho;
```

⚠️ **Duas armadilhas obrigatórias:**

1. **Condição de parada.** Sem ela, roda até estourar a memória. Escreva a
   parada **antes** de rodar pela primeira vez.
2. **Ciclos.** Se `A` é pai de `B` e alguém marcar `B` como pai de `A`, a
   recursão não termina nunca. O `nivel < 10` acima é a proteção pobre; a
   correta é acumular o caminho e testar
   `WHERE instr(a.caminho, e.equipamento_id) = 0`.
   PostgreSQL ≥ 14 tem `CYCLE ... SET ... USING ...` que faz isso nativamente.

`UNION` (sem `ALL`) também evita ciclo, removendo linhas repetidas — ao custo
de deduplicar a cada iteração.

### Onde CTE recursiva **não** é a ferramenta

Um SQL recursivo é Turing-completo, então dá para fazer qualquer coisa nele.
Isso não quer dizer que se deva: gerar fractal, resolver sudoku e simular
autômatos celulares em SQL recursivo são exercícios divertidos e código
horrível. Se o problema é iterativo por natureza (integração numérica,
otimização, simulação), leve-o para Python.

---

## 5. Onde cada ferramenta ganha

| Problema | Melhor ferramenta |
|---|---|
| Comparar com uma constante calculada | Subconsulta **escalar** |
| Filtrar por existência | `EXISTS` |
| Filtrar por lista pequena e fixa | `IN` |
| Reaproveitar um resultado intermediário 3 vezes | **CTE** (materializada) |
| Passo a passo legível | **CTE** encadeada |
| Hierarquia, série gerada | **CTE recursiva** |
| Precisa de colunas dos dois lados | `JOIN` |
| Comparar linha com vizinhas | **Função de janela** ([16](16-funcoes-de-janela.md)) |
| Reusar em vários relatórios | **View** ([22](22-views-e-analitico.md)) |

**A troca mais comum e mais lucrativa:** subconsulta correlacionada → função
de janela. Onde antes se escrevia

```sql
SELECT ts, valor,
       (SELECT valor FROM leitura l2
         WHERE l2.tag_id = l.tag_id AND l2.ts < l.ts
         ORDER BY l2.ts DESC LIMIT 1) AS anterior
  FROM leitura l;
```

hoje se escreve

```sql
SELECT ts, valor, LAG(valor) OVER (PARTITION BY tag_id ORDER BY ts) AS anterior
  FROM leitura;
```

Uma passada em vez de N, e legível. Se você encontrar o primeiro padrão em
código, ele provavelmente é anterior a 2012 — ou foi escrito por alguém que
aprendeu antes disso e nunca atualizou.

---

## Autoteste

1. Cite os quatro tipos de subconsulta e um caso de uso de cada.
2. Por que `NOT IN (SELECT ...)` é perigoso, e o que usar no lugar?
3. Qual a diferença entre `EXISTS` e `JOIN` quanto ao número de linhas?
4. CTE deixa a consulta mais rápida? Explique o que ela muda e o que não muda.
5. Por que uma CTE em PostgreSQL 11 podia deixar a consulta mais lenta?
6. Escreva uma CTE recursiva que gere as horas de um dia.
7. Cite as duas armadilhas obrigatórias de CTE recursiva e como se protege de
   cada uma.
8. Reescreva uma subconsulta correlacionada de "valor anterior" usando função
   de janela.

---

*Próximo: [16-funcoes-de-janela.md](16-funcoes-de-janela.md).*
