# 13 — Junções (`JOIN`): onde todo mundo trava

Nível: iniciante → intermediário · Data: 13/08/2026 · Números **executados** contra o projeto-modelo

Se há um arquivo neste curso que vale ler duas vezes, é este. Junção errada
não dá erro — **dá número errado**, e o número errado vai para a reunião.

---

## 1. O que uma junção é

Combinar linhas de duas tabelas segundo uma condição.

```sql
SELECT l.ts, l.valor, t.descricao, t.unidade
  FROM leitura AS l
  JOIN tag     AS t ON t.tag_id = l.tag_id;
```

Mecanicamente, o modelo é: **para cada linha da esquerda, procure as linhas da
direita que satisfazem a condição; emita uma linha de saída para cada par que
casar.**

Guarde a última parte: **uma linha de saída para cada par**. É daí que vem tudo
que dá errado.

---

## 2. Cardinalidade: a única coisa que importa

### O experimento (números reais do projeto-modelo)

```sql
SELECT COUNT(*) FROM batelada;                                  -- 78
SELECT COUNT(*) FROM analise_lab;                               -- 308
SELECT COUNT(*) FROM batelada JOIN analise_lab USING (batelada_id);  -- 308
```

78 bateladas, 308 análises, resultado com **308 linhas**. Por quê? Porque cada
batelada tem 4 análises (viscosidade, acidez, umidade, pureza). A batelada foi
**multiplicada por quatro** no resultado.

Agora o desastre:

```sql
SELECT ROUND(SUM(carga_kg), 1) FROM batelada;
-- 389335.0  ← correto: 389 toneladas

SELECT ROUND(SUM(b.carga_kg), 1)
  FROM batelada b JOIN analise_lab a USING (batelada_id);
-- 1536422.4  ← 1.536 toneladas. QUATRO VEZES MAIS.
```

**A soma da carga ficou quase 4× maior porque cada batelada foi contada quatro
vezes.** Nenhum erro, nenhum aviso. Só um número errado, plausível o
suficiente para ninguém desconfiar até alguém comparar com a balança.

Isso se chama ***fan-out*** (leque), e é o bug mais comum e mais caro de SQL.

### Como se protege

**Regra:** conte antes e depois de todo `JOIN`.

```sql
SELECT COUNT(*) FROM a;                  -- antes
SELECT COUNT(*) FROM a JOIN b ON ...;    -- depois
```

| Depois | Significa | O que fazer |
|---|---|---|
| **Igual** | 1:1 — cada linha achou exatamente um par | Provavelmente certo |
| **Menor** | `INNER JOIN` descartou linhas sem par | Era intencional? Se não, `LEFT JOIN` |
| **Maior** | 1:N — o lado direito tem várias linhas por chave | **Toda soma está inflada** |

**As três saídas quando é 1:N e você não quer o leque:**

```sql
-- 1. agregue ANTES de juntar (a melhor)
SELECT b.batelada_id, b.carga_kg, l.n_ensaios
  FROM batelada b
  LEFT JOIN (SELECT batelada_id, COUNT(*) AS n_ensaios
               FROM analise_lab GROUP BY batelada_id) l USING (batelada_id);

-- 2. use EXISTS quando só quer saber se existe
SELECT * FROM batelada b
 WHERE EXISTS (SELECT 1 FROM analise_lab a WHERE a.batelada_id = b.batelada_id);

-- 3. agregue depois, com cuidado (frágil)
SELECT b.batelada_id, MAX(b.carga_kg) AS carga, COUNT(*) AS ensaios
  FROM batelada b JOIN analise_lab a USING (batelada_id)
 GROUP BY b.batelada_id;     -- MAX da carga, não SUM: a carga é a mesma nas 4 linhas
```

⚠️ **`SELECT DISTINCT` não conserta cardinalidade.** Ele remove linhas
totalmente idênticas; se as linhas diferem em qualquer coluna, continuam lá, e
a soma continua inflada. `DISTINCT` como remédio de junção é sintoma de bug,
não solução.

---

## 3. Os tipos de junção

```
      A          B                    A ⋈ B
   ┌─────┐   ┌─────┐
   │  a1 │   │ b1  │   INNER JOIN   →  só o que casa dos dois lados
   │  a2 ├───┤ b2  │   LEFT  JOIN   →  tudo de A, NULL onde B falta
   │  a3 │   │ b3  │   RIGHT JOIN   →  tudo de B, NULL onde A falta
   └─────┘   └─────┘   FULL  JOIN   →  tudo dos dois
                       CROSS JOIN   →  todas as combinações (n × m)
```

### `INNER JOIN` — só o que casa

```sql
SELECT COUNT(DISTINCT b.batelada_id)
  FROM batelada b JOIN analise_lab a USING (batelada_id);
-- 77
```

### `LEFT JOIN` — tudo da esquerda

```sql
SELECT COUNT(DISTINCT b.batelada_id)
  FROM batelada b LEFT JOIN analise_lab a USING (batelada_id);
-- 78
```

**Uma batelada a mais.** Qual?

```sql
SELECT b.batelada_id, b.status
  FROM batelada b
  LEFT JOIN analise_lab a USING (batelada_id)
 WHERE a.batelada_id IS NULL;
-- B-2026-0040 | ABORTADA
```

A batelada abortada não foi ao laboratório. Com `INNER JOIN` ela **desaparece
do relatório** — silenciosamente. Se o relatório é de produção total, você
acaba de esconder uma batelada perdida, que é exatamente a que interessa.

**Este padrão — `LEFT JOIN` + `WHERE ... IS NULL` — é o "anti-join"**, e é
como se pergunta "o que está de um lado e não do outro":

- Bateladas sem laudo de laboratório.
- Tags cadastrados que nunca produziram leitura (instrumento morto).
- Ordens de manutenção sem apontamento de horas.

### `CROSS JOIN` — produto cartesiano

```sql
SELECT * FROM a CROSS JOIN b;     -- n × m linhas
```

Usos legítimos: gerar combinações (todos os tags × todas as horas, para achar
o que falta); **anexar um valor escalar a todas as linhas**, como no exemplo 8
de [06-exemplos.md](06-exemplos.md).

Uso acidental, e é o clássico: esquecer o `ON`.

```sql
SELECT * FROM leitura, tag;    -- 344.640 × 8 = 2.757.120 linhas
```

Por isso a junção implícita com vírgula é considerada obsoleta: com `JOIN ...
ON`, esquecer a condição é erro de sintaxe em muitos bancos; com vírgula, é
uma consulta perfeitamente válida que trava o servidor.

### `FULL OUTER JOIN` — tudo dos dois lados

Uso típico: conciliar duas fontes que deveriam ter o mesmo conteúdo (o
apontamento do operador × o registro do historiador). O que aparecer com
`NULL` de um lado é divergência.

⚠️ SQLite só tem `RIGHT` e `FULL JOIN` desde a **3.39** (2022). Em versões
anteriores, emule com `UNION` de dois `LEFT JOIN`.

---

## 4. A junção temporal: a mais importante para dado de processo

`ON` **não precisa ser igualdade**.

```sql
SELECT b.batelada_id, AVG(l.valor)
  FROM batelada b
  JOIN leitura  l ON l.ts >= b.ts_inicio        -- theta-join
                 AND l.ts <  b.ts_fim
 WHERE l.tag_id = 'TI-101'
 GROUP BY b.batelada_id;
```

Isto liga cada leitura à batelada que estava rodando naquele instante. Sem
isso, série temporal e produção são dois mundos separados — e ligá-los é
metade do trabalho de engenharia de dados de planta.

### As três armadilhas da junção temporal

**1. Fronteira duplicada.** Com `l.ts <= b.ts_fim`, a leitura do instante exato
da virada casa com **duas** bateladas. O total passa de 100%. Sempre
semiaberto: `>= início AND < fim`.

**2. Batelada em andamento (`ts_fim` nulo).** `l.ts < NULL` é desconhecido, e a
linha some. Trate:

```sql
AND l.ts < COALESCE(b.ts_fim, '9999-12-31')
```

**3. Desempenho.** Junção por intervalo não usa índice tão bem quanto
igualdade: o banco tende a, para cada batelada, varrer um trecho da série. Com
78 bateladas e 344 mil leituras, funciona. Com 10 mil intervalos e 1 bilhão de
leituras, não funciona — a saída é gravar o `batelada_id` na própria linha de
leitura (desnormalizar), pagando espaço para comprar tempo. Ver
[19-ddl-e-modelagem.md](19-ddl-e-modelagem.md).

### *As-of join*: o valor vigente naquele instante

"Qual era o setpoint quando esta leitura foi tomada?" — o setpoint muda em
instantes esparsos; a leitura é a cada minuto. Você quer, para cada leitura,
**a última** mudança de setpoint anterior a ela.

```sql
SELECT l.ts, l.valor,
       (SELECT s.setpoint FROM setpoint s
         WHERE s.tag_id = l.tag_id AND s.ts <= l.ts
         ORDER BY s.ts DESC LIMIT 1) AS setpoint_vigente
  FROM leitura l
 WHERE l.tag_id = 'TI-101';
```

DuckDB tem `ASOF JOIN` nativo, que faz isso de forma muito mais eficiente:

```sql
SELECT l.ts, l.valor, s.setpoint
  FROM leitura l ASOF JOIN setpoint s
    ON l.tag_id = s.tag_id AND l.ts >= s.ts;
```

Este é um dos casos em que o dialeto muda o que é praticável. Ver
[23-dialetos.md](23-dialetos.md).

---

## 5. `ON` × `WHERE` em `LEFT JOIN`: a diferença que muda tudo

Numa junção **interna** os dois são equivalentes. Num `LEFT JOIN`, **não são**,
e essa é uma das confusões mais persistentes do SQL.

```sql
-- A) condição no ON: filtra o lado DIREITO antes de juntar
SELECT b.batelada_id, a.parametro
  FROM batelada b
  LEFT JOIN analise_lab a
         ON a.batelada_id = b.batelada_id
        AND a.parametro = 'viscosidade';
-- → TODAS as 78 bateladas; as sem viscosidade vêm com NULL

-- B) condição no WHERE: filtra DEPOIS de juntar
SELECT b.batelada_id, a.parametro
  FROM batelada b
  LEFT JOIN analise_lab a ON a.batelada_id = b.batelada_id
 WHERE a.parametro = 'viscosidade';
-- → só as que TÊM viscosidade. O LEFT virou INNER.
```

**Regra:** condição sobre a tabela da direita num `LEFT JOIN` vai no `ON`.
Se for para o `WHERE`, o `LEFT JOIN` deixa de existir — porque as linhas
"sem par" têm `NULL` naquela coluna, e `NULL = 'viscosidade'` é falso.

A única exceção é o anti-join proposital: `WHERE a.batelada_id IS NULL`.

---

## 6. Junções de várias tabelas

```sql
SELECT l.ts, l.valor, t.descricao, e.nome AS equipamento, e.area
  FROM leitura     l
  JOIN tag         t ON t.tag_id = l.tag_id
  JOIN equipamento e ON e.equipamento_id = t.equipamento_id
 WHERE l.ts >= '2026-07-01' AND l.ts < '2026-07-02';
```

O banco junta duas por vez, na ordem que o otimizador escolher. **A ordem que
você escreve não é a ordem de execução** — exceto em bancos com dica explícita
(`STRAIGHT_JOIN` no MySQL, `/*+ LEADING */` no Oracle) ou quando o número de
tabelas passa do limite de busca do otimizador (8 no SQLite, configurável em
outros).

⚠️ **Um `LEFT JOIN` seguido de `INNER JOIN` na mesma cadeia anula o `LEFT`**:

```sql
FROM a
LEFT JOIN b ON ...
JOIN c ON c.id = b.id      -- ← este INNER exige b, e mata o LEFT anterior
```

Se `b` for nulo, `c.id = NULL` é falso e a linha some. Use `LEFT JOIN c`
também, ou reorganize.

---

## 7. Como o banco executa uma junção

Três algoritmos. Saber qual está sendo usado explica o desempenho.

| Algoritmo | Como funciona | Custo | Quando o banco escolhe |
|---|---|---|---|
| **Nested loop** | Para cada linha de A, procura em B | O(n·m), ou O(n·log m) com índice | Uma das tabelas é pequena, ou há índice na chave do lado interno |
| **Hash join** | Constrói tabela hash da menor, varre a maior | O(n+m), mas usa memória | Tabelas grandes, junção por **igualdade** |
| **Merge join** | Ordena os dois e percorre em paralelo | O(n log n + m log m) | Já vêm ordenados, ou há índice na ordem certa |

⚠️ **O SQLite só tem nested loop.** Por isso ele depende inteiramente de
índices para junções grandes serem viáveis, e por isso ele não é a ferramenta
certa para juntar duas tabelas de 100 milhões de linhas. PostgreSQL e DuckDB
têm os três e escolhem sozinhos.

**Hash join não funciona com desigualdade** — precisa de `=`. É por isso que a
junção temporal (`>=`, `<`) cai em nested loop mesmo no PostgreSQL, e por isso
ela é a junção lenta por natureza.

Veja qual foi escolhido:

```bash
python3 scripts/consultar.py --plano 03
```

---

## 8. Tabela de decisão

| Você quer | Use |
|---|---|
| Só o que existe nos dois | `INNER JOIN` |
| Tudo da tabela principal, com o extra quando houver | `LEFT JOIN` |
| Saber se existe, sem trazer colunas | `EXISTS` (não multiplica linhas) |
| Saber o que **não** existe do outro lado | `LEFT JOIN ... WHERE b.chave IS NULL` |
| Contar quantos do outro lado | Subconsulta agregada, **não** `JOIN` + `COUNT` |
| Ligar a um intervalo de tempo | `JOIN ... ON ts >= inicio AND ts < fim` |
| O valor vigente naquele instante | Subconsulta correlacionada com `ORDER BY ... LIMIT 1`, ou `ASOF JOIN` |
| Empilhar duas tabelas parecidas | `UNION ALL` — **não** é junção |
| Todas as combinações | `CROSS JOIN` |

---

## 9. Depuração de junção: o roteiro

Quando o número não bate, siga nesta ordem:

1. **Conte.** `COUNT(*)` antes e depois. Mudou como você esperava?
2. **Ache a duplicata.**
   ```sql
   SELECT chave, COUNT(*) FROM tabela_da_direita
    GROUP BY chave HAVING COUNT(*) > 1 LIMIT 10;
   ```
3. **Verifique o tipo da chave.** `'101'` (texto) nunca casa com `101`
   (número). Em SQLite, isso não dá erro — dá zero linhas.
4. **Verifique espaços e caixa.** `'TI-101 '` ≠ `'TI-101'`. Use
   `TRIM()`/`UPPER()` para diagnosticar, e **corrija o dado**, não a consulta.
5. **Verifique `NULL` na chave.** `NULL = NULL` é falso: linhas com chave nula
   nunca casam, com nenhum tipo de junção.
6. **Leia o plano.** `EXPLAIN QUERY PLAN`. Apareceu `SCAN` nas duas tabelas?
   Falta índice.

---

## Autoteste

1. 78 bateladas juntadas com 308 análises deram 308 linhas. Explique.
2. Por que `SUM(carga_kg)` passou de 389 t para 1.536 t?
3. Cite as três formas de evitar o *fan-out*, e diga qual é a melhor.
4. Por que `SELECT DISTINCT` não conserta cardinalidade?
5. Qual batelada some com `INNER JOIN` e aparece com `LEFT JOIN`, e por que
   isso importa?
6. Escreva um anti-join que ache tags cadastrados sem nenhuma leitura.
7. Qual a diferença entre pôr `a.parametro='viscosidade'` no `ON` e no `WHERE`
   de um `LEFT JOIN`?
8. Por que a junção temporal precisa ser semiaberta?
9. Por que hash join não serve para junção por intervalo?
10. Sua junção devolveu zero linhas e você tem certeza de que deveria casar.
    Cite três causas possíveis.

---

*Próximo: [14-agregacao-e-grupos.md](14-agregacao-e-grupos.md).*
