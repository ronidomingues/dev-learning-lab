# 16 · Consultas e o planejador — por que o banco escolhe o que escolhe

`Nível: avançado` · `Última atualização: 11/08/2026`

Você diz **o quê**; o planejador decide **o como**. Este arquivo abre essa caixa-preta — a
diferença entre "meu SQL está lento" e "eu sei por que e como consertar".

---

## 1. O caminho de uma consulta, do texto ao resultado

```
   SQL (texto)
      │  Parser        → transforma em árvore de sintaxe
      ▼
   Árvore de análise
      │  Rewriter      → aplica views, regras
      ▼
   Consulta reescrita
      │  PLANNER/OPTIMIZER  ← o cérebro: gera vários planos e escolhe o mais BARATO
      ▼
   Plano de execução
      │  Executor      → roda o plano, produz linhas
      ▼
   Resultado
```

O **planejador** é o componente que, para `SELECT nome FROM clientes WHERE cidade='Recife'`,
decide: varrer a tabela inteira? usar um índice? Se houver JOIN, em que ordem juntar? Qual
algoritmo de JOIN? Ele gera múltiplos planos possíveis, **estima o custo** de cada um, e escolhe o
mais barato. É um **otimizador baseado em custo**.

---

## 2. EXPLAIN — ver o plano

```sql
EXPLAIN SELECT * FROM pedidos WHERE cliente_id = 42;
```
```
Index Scan using ix_pedidos_cliente on pedidos  (cost=0.43..8.45 rows=10 width=64)
  Index Cond: (cliente_id = 42)
```

Lendo isso:
- **`Index Scan`** — o método de acesso escolhido (usou o índice).
- **`cost=0.43..8.45`** — custo estimado: `0.43` para começar a devolver a primeira linha, `8.45`
  para terminar. Unidade arbitrária (baseada em custo de I/O e CPU), útil para **comparar** planos.
- **`rows=10`** — quantas linhas o planejador **estima**.
- **`width=64`** — largura média da linha em bytes.

### EXPLAIN ANALYZE — executar e medir de verdade

```sql
EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM pedidos WHERE cliente_id = 42;
```
```
Index Scan using ix_pedidos_cliente on pedidos
  (cost=0.43..8.45 rows=10 width=64) (actual time=0.02..0.05 rows=8 loops=1)
  Index Cond: (cliente_id = 42)
  Buffers: shared hit=4
Planning Time: 0.1 ms
Execution Time: 0.08 ms
```

Agora você tem **estimado** (`cost`, `rows`) **e real** (`actual time`, `rows`). A comparação é o
ouro:

> **A regra de ouro do diagnóstico:** compare `rows` **estimado** com `rows` **real**. Se o
> planejador estimou 10 e vieram 2 milhões (ou vice-versa), suas **estatísticas estão erradas**, e
> ele tomou decisões ruins baseadas nelas. `ANALYZE tabela` corrige.

`BUFFERS` mostra I/O: `shared hit` = lido do cache (rápido); `read` = lido do disco (lento). Muito
`read` sugere cache pequeno ou dados frios.

---

## 3. Os métodos de acesso — como ler uma tabela

| Nó do plano | O que faz | Bom quando |
|---|---|---|
| **Seq Scan** | Lê a tabela inteira, linha a linha | Você quer a maioria das linhas, ou não há índice útil |
| **Index Scan** | Desce o índice e busca cada linha na tabela | Filtro seletivo (poucas linhas) |
| **Index Only Scan** | Responde só com o índice, sem tocar a tabela | O índice cobre todas as colunas pedidas |
| **Bitmap Heap Scan** | Junta vários acertos de índice, lê a tabela em ordem de disco | Filtro de seletividade média; combina índices |

> **Seq Scan não é sempre ruim!** Iniciantes veem "Seq Scan" e entram em pânico. Mas se a consulta
> traz 60% da tabela, ler tudo em sequência é **mais rápido** que pular do índice para a tabela
> milhões de vezes. Seq Scan é ruim quando você filtra **poucas** linhas de uma tabela **grande** —
> aí sim falta índice.

---

## 4. Os algoritmos de JOIN

Quando há JOIN, o planejador escolhe entre três algoritmos:

| Algoritmo | Como | Bom quando |
|---|---|---|
| **Nested Loop** | Para cada linha de A, busca as correspondentes em B | Uma das tabelas é pequena, ou há índice no lado interno |
| **Hash Join** | Constrói uma tabela hash de B na memória, sonda com A | Tabelas médias/grandes, sem ordem útil, JOIN por igualdade |
| **Merge Join** | Ordena os dois lados e "casa" em paralelo, como fechar um zíper | Ambos já ordenados (por índice) ou grandes |

Você não escolhe o algoritmo — o planejador escolhe. Mas entender ajuda a ler o plano: um **Nested
Loop** sobre duas tabelas grandes sem índice é o sinal clássico de consulta que "explodiu"
(milhões × milhões).

Além disso, o planejador decide a **ordem** dos JOINs (juntar A com B primeiro, ou B com C?) — e a
ordem certa pode mudar o tempo em ordens de magnitude. Ele usa as estatísticas para estimar qual
ordem produz menos linhas intermediárias.

---

## 5. Estatísticas — como o planejador "sabe" das coisas

O planejador decide com base em **estatísticas** coletadas sobre os dados: quantas linhas há,
quantos valores distintos por coluna, os valores mais comuns, o histograma de distribuição. Elas
vivem em `pg_statistic` (visível via `pg_stats`).

```sql
SELECT attname, n_distinct, most_common_vals
FROM pg_stats WHERE tablename = 'pedidos';
```

Essas estatísticas são atualizadas por **`ANALYZE`** (e pelo autovacuum, que roda `ANALYZE`
periodicamente):

```sql
ANALYZE pedidos;             -- recalcula as estatísticas desta tabela
```

> **A causa nº 1 de "a consulta ficou lenta do nada":** estatísticas desatualizadas. Você carregou
> um milhão de linhas, mas o planejador ainda acha que a tabela tem mil (o autovacuum não rodou
> ainda), então escolhe um plano bom para mil linhas e péssimo para um milhão. `ANALYZE` resolve.
> Depois de cargas grandes, rode `ANALYZE` explicitamente.

**Estatísticas estendidas** — para colunas correlacionadas:
```sql
-- Se cidade e estado são correlacionados, o planejador pode estimar mal.
CREATE STATISTICS s_cidade_estado (dependencies) ON cidade, estado FROM enderecos;
ANALYZE enderecos;
```

---

## 6. Diagnóstico sistemático de consulta lenta

O procedimento, em ordem:

```sql
-- 1) Ver o plano REAL
EXPLAIN (ANALYZE, BUFFERS, VERBOSE) <sua consulta>;

-- 2) Procurar os sinais:
--    - "Seq Scan" numa tabela grande com filtro seletivo → falta índice
--    - rows estimado MUITO diferente de rows real → ANALYZE
--    - "Nested Loop" sobre tabelas grandes → índice no lado interno, ou reescrever
--    - "Rows Removed by Filter: <número enorme>" → índice resolveria
--    - Buffers com muito "read" → dados frios / cache pequeno / falta índice

-- 3) Achar as consultas mais caras do SISTEMA (não só a que você olha)
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;   -- precisa estar em shared_preload_libraries
SELECT round(total_exec_time::numeric,1) AS ms_total, calls,
       round(mean_exec_time::numeric,2) AS ms_media, query
FROM pg_stat_statements ORDER BY total_exec_time DESC LIMIT 20;

-- 4) Agir: criar índice (CONCURRENTLY), rodar ANALYZE, reescrever, ajustar memória
CREATE INDEX CONCURRENTLY ix ON pedidos (cliente_id);
ANALYZE pedidos;

-- 5) Reexecutar o EXPLAIN ANALYZE e COMPARAR o Execution Time
```

`pg_stat_statements` é a ferramenta mais valiosa de tuning: ela agrega o tempo por **forma** de
consulta em todo o sistema, revelando que muitas vezes o gargalo não é a query lenta que alguém
reclamou, mas uma query rápida executada um milhão de vezes.

---

## 7. Parâmetros de memória que afetam planos

```sql
SHOW work_mem;              -- memória por operação de ordenação/hash (padrão modesto)
SHOW shared_buffers;       -- cache de páginas do banco (idealmente ~25% da RAM)
SHOW effective_cache_size; -- pista para o planejador de quanta RAM o SO tem para cache
SHOW random_page_cost;     -- custo estimado de ler página aleatória (baixe para SSD)
```

- **`work_mem`** baixo demais faz ordenações e hashes irem para o disco (`external merge Disk` no
  plano) — lento. Aumentar acelera, mas cuidado: é **por operação, por conexão**, então multiplica.
- **`random_page_cost`**: o padrão (4.0) pressupõe disco giratório, onde acesso aleatório é caro. Em
  **SSD**, baixe para ~1.1 — isso faz o planejador favorecer índices corretamente. É um dos ajustes
  de maior impacto e mais esquecidos.
- **`effective_cache_size`**: não aloca nada; só informa ao planejador quanta RAM o SO tem para
  cache de arquivos, influenciando a escolha por índices.

Ver tuning completo em [21-administracao-e-operacao.md](21-administracao-e-operacao.md).

---

## 8. Reescritas que ajudam o planejador

Às vezes o problema é a consulta, não o índice:

```sql
-- OFFSET alto → keyset (ver 06-exemplos)
-- NOT IN com NULL → NOT EXISTS
-- Função na coluna impede índice:
WHERE date_trunc('day', criado_em) = '2026-08-11'   -- ❌ não usa índice em criado_em
WHERE criado_em >= '2026-08-11' AND criado_em < '2026-08-12'   -- ✅ usa

-- OR entre colunas diferentes pode virar UNION:
WHERE a = 1 OR b = 2               -- ❌ às vezes força seq scan
SELECT ... WHERE a=1 UNION SELECT ... WHERE b=2   -- ✅ dois index scans

-- Trazer só as colunas necessárias (habilita Index Only Scan)
SELECT * FROM grande            -- ❌ lê tudo
SELECT id, status FROM grande   -- ✅ pode ser só índice
```

> **Regra:** aplicar função **na coluna** (`lower(email)`, `date_trunc(data)`) impede o uso do
> índice, a menos que exista um índice **naquela expressão**. Reescreva o filtro para tocar a
> coluna crua (faixas em vez de `date_trunc`), ou crie o índice por expressão.

---

## 9. Os cinco porquês: por que o banco escolhe o plano, e não você?

**1. Por que o banco decide o plano de execução, em vez de o programador especificá-lo?**
Porque o melhor plano depende de fatos que o programador não conhece quando escreve a consulta.

**2. Por que o programador não conhece esses fatos?**
Porque o melhor plano depende do **tamanho atual** das tabelas, da **distribuição** dos dados, de
**quais índices** existem e de **quanta memória** há — tudo isso muda com o tempo e só é conhecido
em tempo de execução.

**3. Por que deixar a decisão em tempo de execução é melhor que fixá-la no código?**
Porque a mesma consulta `WHERE cliente_id = ?` precisa de planos diferentes conforme o cliente
tenha 3 pedidos (use índice) ou 3 milhões (talvez seq scan). Um plano fixo seria ótimo num caso e
péssimo no outro.

**4. Por que o banco consegue estimar isso bem?**
Porque mantém estatísticas amostradas dos dados (`ANALYZE`) e um modelo de custo calibrado. Quando
as estatísticas estão corretas, as estimativas são boas; quando estão velhas, as decisões pioram —
o que confirma que a decisão é genuinamente informada por dados de runtime.

**5. Por que essa abordagem (otimização baseada em custo) venceu a alternativa (o programador
escrever o plano)?**
Aqui chega-se ao mesmo **trade-off econômico** do modelo relacional: escrever planos à mão dá, no
melhor caso, planos ótimos para um instante — mas exige reotimizar a cada mudança de dados, de
volume ou de esquema, o que é caríssimo em tempo humano. O otimizador troca alguns planos
subótimos por **zero manutenção de planos** e adaptação automática. Quando o tempo de gente é o
recurso caro, essa troca vence — e é por isso que todo banco relacional sério usa otimização por
custo.

---

## Autoteste

1. Descreva o caminho de uma consulta, do texto SQL ao resultado, nomeando o planejador.
2. Na saída de `EXPLAIN`, o que são `cost`, `rows` e `width`?
3. Qual é a "regra de ouro" ao comparar `EXPLAIN ANALYZE` — o que comparar?
4. Por que "Seq Scan" nem sempre é ruim? Quando ele **é** ruim?
5. Cite os três algoritmos de JOIN e quando cada um é bom.
6. O que são estatísticas, o que as atualiza, e por que "a consulta ficou lenta do nada" costuma
   ser culpa delas?
7. O que `pg_stat_statements` revela que o `EXPLAIN` de uma consulta isolada não revela?
8. Por que baixar `random_page_cost` em SSD melhora as escolhas do planejador?
9. Por que `WHERE date_trunc('day', criado_em) = ...` não usa o índice, e como reescrever?
10. Percorra os cinco porquês de "por que o banco escolhe o plano?" até a parada econômica.
