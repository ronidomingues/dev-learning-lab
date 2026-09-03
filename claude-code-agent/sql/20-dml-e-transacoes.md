# 20 — Inserir, atualizar, apagar, e transações

Nível: intermediário · Data: 13/08/2026 · Medições **executadas**

Consultar é seguro. Escrever, não. Este arquivo é sobre escrever sem destruir
nada e sem esperar meia hora.

---

## 1. `INSERT`

```sql
INSERT INTO leitura (tag_id, ts, valor) VALUES ('TI-101','2026-07-01 10:00:00', 179.8);

-- várias de uma vez: UMA instrução, muito mais rápido que N instruções
INSERT INTO leitura (tag_id, ts, valor) VALUES
    ('TI-101','2026-07-01 10:00:00', 179.8),
    ('TI-101','2026-07-01 10:01:00', 180.3),
    ('TI-101','2026-07-01 10:02:00', 181.2);

-- a partir de uma consulta
INSERT INTO leitura_hora (tag_id, hora, media)
SELECT tag_id, substr(ts,1,13)||':00:00', AVG(valor)
  FROM leitura GROUP BY 1, 2;
```

**Sempre liste as colunas.** `INSERT INTO t VALUES (...)` sem lista depende da
ordem física das colunas — e quebra silenciosamente no dia em que alguém
adicionar uma coluna no meio.

---

## 2. `UPDATE` e `DELETE`

```sql
UPDATE batelada SET status = 'CONCLUIDA', ts_fim = '2026-07-01 06:00:00'
 WHERE batelada_id = 'B-2026-0001';

DELETE FROM leitura WHERE ts < '2020-01-01';
```

### A regra que evita a demissão

```sql
-- 1. escreva como SELECT
SELECT COUNT(*) FROM leitura WHERE ts < '2020-01-01';
SELECT * FROM leitura WHERE ts < '2020-01-01' LIMIT 10;

-- 2. confira: o número faz sentido? as linhas são as certas?

-- 3. só então troque o SELECT por DELETE
DELETE FROM leitura WHERE ts < '2020-01-01';
```

`UPDATE`/`DELETE` **sem `WHERE` atinge a tabela inteira**, e não há desfazer
fora de uma transação aberta.

Proteções que valem adotar como hábito:

```sql
BEGIN;                                   -- 1. sempre dentro de transação
DELETE FROM leitura WHERE ts < '2020-01-01';
SELECT changes();                        -- 2. confira quantas foram (SQLite)
-- 3. COMMIT só se o número bater; senão ROLLBACK
ROLLBACK;
```

No cliente `sqlite3`, `.bail on` faz a sessão parar no primeiro erro em vez de
seguir executando o resto do script — o que já salvou muita gente.

### `RETURNING`: fique com o registro do que fez

```sql
DELETE FROM leitura WHERE ts < '2020-01-01' RETURNING tag_id, ts, valor;
```
Devolve as linhas afetadas. **Use sempre em expurgo**: você fica com o que
apagou, e pode gravar num arquivo antes de confirmar. SQLite ≥ 3.35,
PostgreSQL, Oracle, DuckDB.

### `UPDATE` com dado de outra tabela

```sql
-- SQLite ≥3.33, PostgreSQL
UPDATE batelada AS b
   SET produzido_kg = a.total
  FROM (SELECT batelada_id, SUM(massa_kg) AS total
          FROM saida_produto GROUP BY batelada_id) AS a
 WHERE a.batelada_id = b.batelada_id;
```

---

## 3. `UPSERT`: inserir ou atualizar

```sql
-- SQLite ≥3.24, PostgreSQL ≥9.5, DuckDB
INSERT INTO leitura (tag_id, ts, valor) VALUES ('TI-101','2026-07-01 10:00:00', 180.1)
ON CONFLICT (tag_id, ts) DO UPDATE SET valor = excluded.valor;

-- ignorar duplicata em vez de atualizar
INSERT INTO leitura (...) VALUES (...) ON CONFLICT DO NOTHING;
```

`excluded` é a linha que **teria** sido inserida.

```sql
-- MERGE: padrão ISO; Oracle, SQL Server, PostgreSQL ≥15
MERGE INTO leitura t
USING nova n ON (t.tag_id = n.tag_id AND t.ts = n.ts)
WHEN MATCHED THEN UPDATE SET valor = n.valor
WHEN NOT MATCHED THEN INSERT (tag_id, ts, valor) VALUES (n.tag_id, n.ts, n.valor);
```

⚠️ **`INSERT OR REPLACE` do SQLite não é *upsert*.** Ele **apaga** a linha
antiga e insere uma nova — o que dispara `ON DELETE CASCADE`, zera colunas que
você não mencionou e muda o `rowid`. Já apagou dado de gente que achava estar
atualizando. Use `ON CONFLICT DO UPDATE`.

---

## 4. Transações

```sql
BEGIN;
UPDATE conta SET saldo = saldo - 100 WHERE id = 1;
UPDATE conta SET saldo = saldo + 100 WHERE id = 2;
COMMIT;      -- ou ROLLBACK
```

### ACID, com o que quebra sem cada letra

| Letra | Garante | Sem ela, em planta |
|---|---|---|
| **A**tomicidade | Tudo ou nada | Carga interrompida deixa metade do CSV dentro, e ninguém sabe onde parou |
| **C**onsistência | As restrições valem ao fim | Leitura de instrumento inexistente; batelada que termina antes de começar |
| **I**solamento | Concorrentes não veem o meio uma da outra | O relatório mensal soma metade de uma carga |
| **D**urabilidade | Depois do `COMMIT`, sobrevive à queda | Pico de energia apaga as duas últimas horas — justamente as do incidente |

### Níveis de isolamento

| Nível | Impede | Padrão em |
|---|---|---|
| `READ UNCOMMITTED` | nada (lê dado não confirmado) | — |
| `READ COMMITTED` | leitura suja | PostgreSQL, Oracle, SQL Server |
| `REPEATABLE READ` | + leitura não repetível | MySQL/InnoDB |
| `SERIALIZABLE` | + leitura fantasma | **SQLite** (sempre) |

Os três fenômenos, com exemplo:

- **Leitura suja**: você lê um valor que a outra transação ainda vai desfazer.
- **Leitura não repetível**: você lê a mesma linha duas vezes e ela mudou no
  meio.
- **Leitura fantasma**: você conta as linhas duas vezes e apareceram linhas
  novas que satisfazem o mesmo filtro.

⚠️ Para relatório longo sobre dado que está sendo escrito, `READ COMMITTED`
pode dar um resultado que **nunca existiu** em nenhum instante: a primeira
metade do relatório vê um estado, a segunda vê outro. Se o número precisa
"fechar" (balanço, fechamento contábil, inventário), use `REPEATABLE READ` ou
`SERIALIZABLE`, ou trabalhe sobre um instantâneo.

---

## 5. Desempenho: a medição que muda tudo

Inserindo **20.000 linhas** em SQLite (Python 3.10.12, disco local, medido):

| Estratégia | Tempo | Taxa | Relativo |
|---|---|---|---|
| **Um `COMMIT` por linha** | **131,50 s** | 152 linhas/s | 1× |
| **Um `COMMIT` no total** (`executemany`) | **0,03 s** | 655.600 linhas/s | **4.311×** |
| WAL + um `COMMIT` | 0,03 s | 701.027 linhas/s | 4.612× |

**Quatro mil vezes.** Não é 20% nem 3×.

**Por quê:** cada `COMMIT` exige um `fsync()` — forçar o sistema operacional a
gravar fisicamente no disco e esperar a confirmação. É o preço da letra **D**
de ACID, e não tem como ser barato: é física do dispositivo. Um SSD faz da
ordem de centenas de `fsync` por segundo; 20.000 deles levam minutos.

**Consequência prática:** se a sua carga de dados está lenta, quase certamente
você está confirmando por linha. Em Python:

```python
# ❌ 131 segundos
for linha in linhas:
    con.execute("INSERT ...", linha)
    con.commit()

# ✅ 0,03 segundo
con.executemany("INSERT ...", linhas)
con.commit()

# ✅ idem, com transação explícita e rollback automático em caso de erro
with con:
    con.executemany("INSERT ...", linhas)
```

### Outras alavancas de escrita

| Ação | Ganho | Risco |
|---|---|---|
| `executemany` / transação única | **Enorme** | Nenhum |
| `PRAGMA journal_mode = WAL` | Leitores não bloqueiam o escritor | Três arquivos em vez de um; não funciona em disco de rede |
| `PRAGMA synchronous = NORMAL` | ~2× em escrita | Perde as últimas transações se a **máquina** cair (não se o processo cair) |
| `PRAGMA synchronous = OFF` | Mais rápido ainda | **Pode corromper o banco.** Só para dado descartável |
| Criar índices **depois** da carga | Muito, em carga inicial | Nenhum, se a carga é offline |
| `COPY` (PostgreSQL) / `.import` (SQLite) | 5–10× sobre `INSERT` | Nenhum |
| Carga em lotes de 10–50 mil | Controla memória e permite retomar | Nenhum |

**Recomendação para carga de historiador:** `WAL` + `synchronous = NORMAL` +
lotes de 50 mil dentro de uma transação por lote + índices criados ao final.
`synchronous = OFF` só se você puder recarregar tudo do zero.

---

## 6. Concorrência

### SQLite

**Um escritor por vez, sempre.** Com WAL, os leitores continuam lendo enquanto
alguém escreve — mas dois escritores não coexistem.

```
Error: database is locked
```

Causas e correções:

| Causa | Correção |
|---|---|
| Outro processo com transação aberta | Feche-a. Transação aberta e esquecida é o caso mais comum |
| Sem WAL, um leitor bloqueia o escritor | `PRAGMA journal_mode=WAL` |
| Timeout curto demais | `PRAGMA busy_timeout = 5000` (espera 5 s em vez de falhar) |
| Banco em disco de rede (NFS, SMB, `/mnt/c` no WSL) | **Não use.** O bloqueio de arquivo não é confiável e o banco corrompe |

A última é séria: **SQLite em compartilhamento de rede corrompe**. A
documentação oficial diz isso, e a experiência de campo confirma.

### PostgreSQL: MVCC

Cada transação vê um instantâneo consistente. Leitores nunca bloqueiam
escritores nem vice-versa. O custo é que versões antigas de linha ficam no
disco até o `VACUUM` limpar — e um `VACUUM` mal configurado é a causa nº 1 de
banco Postgres inchado.

### Bloqueio explícito

```sql
-- PostgreSQL: reserva a linha para esta transação
SELECT * FROM batelada WHERE batelada_id='B-001' FOR UPDATE;
```

Use com muita parcimônia. **Ordem de bloqueio inconsistente entre duas
transações = *deadlock***: A trava a linha 1 e quer a 2; B trava a 2 e quer a
1. O banco detecta e mata uma das duas. A prevenção é sempre travar na mesma
ordem.

---

## 7. `TRUNCATE` × `DELETE`

```sql
DELETE FROM leitura;        -- linha a linha, transacional, aciona gatilhos, lento
TRUNCATE TABLE leitura;     -- descarta tudo de uma vez, muito rápido
```

| | `DELETE` | `TRUNCATE` |
|---|---|---|
| Transacional | Sim | PostgreSQL sim; Oracle/MySQL **não** (é DDL, auto-commit) |
| Aciona gatilho | Sim | Não |
| Reseta contador | Não | Geralmente sim |
| Velocidade | O(n) | O(1) |
| Existe no SQLite | — | **Não**; `DELETE FROM t` sem `WHERE` é otimizado internamente |

⚠️ Em Oracle e MySQL, `TRUNCATE` **não pode ser desfeito**, nem dentro de
transação. Não é `DELETE` rápido; é outra coisa.

---

## 8. Gatilhos (*triggers*)

```sql
CREATE TRIGGER trg_auditoria_batelada
AFTER UPDATE ON batelada
BEGIN
    INSERT INTO batelada_auditoria (batelada_id, campo, de, para, quando)
    VALUES (NEW.batelada_id, 'status', OLD.status, NEW.status, datetime('now'));
END;
```

**Bons usos:** trilha de auditoria; manter coluna derivada; validar regra que
`CHECK` não alcança.

**Maus usos:** regra de negócio complexa; qualquer coisa que outro
desenvolvedor precise saber que existe.

**A objeção séria:** gatilho é **lógica invisível**. O `INSERT` do seu script
faz mais do que diz, e nada no código indica isso. Depurar um sistema com 30
gatilhos encadeados é uma das piores experiências da profissão. Use pouco, e
documente no esquema.

---

## 9. Backup

```bash
# SQLite: backup a QUENTE, transacionalmente consistente
sqlite3 planta.db ".backup planta-2026-08-13.db"

# exportar como SQL (portátil, maior)
sqlite3 planta.db .dump > planta.sql

# PostgreSQL
pg_dump -Fc planta > planta.dump
```

⚠️ **`cp planta.db backup.db` com o banco em uso pode gerar arquivo
corrompido** — você copia páginas de dois estados diferentes. Use `.backup`,
que coordena com o banco.

**Backup não testado não é backup.** Restaure num arquivo novo e rode
`PRAGMA integrity_check` (SQLite) ou uma consulta de contagem. Uma vez por
trimestre, no mínimo.

---

## Autoteste

1. Por que sempre listar as colunas no `INSERT`?
2. Descreva o procedimento de três passos antes de um `DELETE`.
3. Por que `INSERT OR REPLACE` não é um *upsert*, e o que ele pode destruir?
4. Um `COMMIT` por linha custou 131 s; um só, 0,03 s. Explique a causa física.
5. Cite as quatro letras de ACID com um exemplo de planta para cada.
6. Que fenômeno o `READ COMMITTED` **não** impede, e por que isso importa num
   relatório de fechamento?
7. `database is locked`: cite três causas e a correção de cada.
8. Por que SQLite em compartilhamento de rede é proibido?
9. `TRUNCATE` × `DELETE`: qual a diferença perigosa em Oracle?
10. Por que `cp` não serve como backup de um banco em uso?

---

*Próximo: [21-indices-e-desempenho.md](21-indices-e-desempenho.md).*
