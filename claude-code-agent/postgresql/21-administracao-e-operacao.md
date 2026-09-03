# 21 · Administração e operação

`Nível: avançado` · `Última atualização: 11/08/2026`

Rodar um `SELECT` é fácil. Manter um banco de produção saudável, rápido e recuperável é uma
especialidade. Este arquivo é o que separa "uso PostgreSQL" de "cuido de PostgreSQL".

---

## 1. Backup — a coisa mais importante

> **Um banco sem backup testado é um incidente esperando data.** E um backup nunca restaurado não
> é um backup — é uma esperança.

### Backup lógico (`pg_dump`)

Exporta os dados como comandos SQL ou um formato próprio. Portátil, seletivo, funciona entre
versões.

```bash
pg_dump -U app -d loja -Fc -f loja.dump          # -Fc = custom (comprimido, restauração flexível)
pg_dump -U app -d loja -Fc -j 4 -f loja.dump     # paralelo (mais rápido)
pg_dump -U app -d loja -t clientes -Fc -f c.dump # só uma tabela
pg_dumpall -U postgres --globals-only > roles.sql # roles e configs globais (pg_dump NÃO os inclui)

# Restaurar
pg_restore -U app -d loja_nova loja.dump
pg_restore -U app -d loja_nova -j 4 loja.dump    # paralelo
```

Vantagens: portátil, seletivo. Desvantagens: **lento em bancos grandes** (dumpar 1 TB leva horas), e
captura o estado do início do dump (consistente, mas não incremental).

### Backup físico + PITR (`pg_basebackup` + WAL)

Copia os arquivos do banco e arquiva o WAL contínuo, permitindo restaurar a **qualquer instante**
(ver [19-replicacao-e-alta-disponibilidade.md](19-replicacao-e-alta-disponibilidade.md#5-point-in-time-recovery-pitr)).

```bash
# Ferramentas que empacotam isso corretamente (não faça à mão em produção):
# pgBackRest (o padrão robusto), Barman, WAL-G (para S3/object storage)
```

Vantagens: recuperação a um ponto no tempo, rápido de restaurar bancos grandes, incremental.
Desvantagens: da mesma major, mais complexo.

### A estratégia certa

| Cenário | Estratégia |
|---|---|
| Banco de estudo / pequeno | `pg_dump` diário, verificado |
| Produção pequena/média | `pg_dump` diário + réplica |
| Produção séria | pgBackRest com PITR + réplica + backup fora do local (regra 3-2-1) |

**E teste a restauração** — periodicamente, restaure num ambiente descartável e verifique.

```bash
# Verificar que um dump não está corrompido
pg_restore --list loja.dump > /dev/null && echo "dump íntegro"
```

---

## 2. VACUUM e autovacuum — o metabolismo do PostgreSQL

Por causa do MVCC (ver [15](15-transacoes-e-mvcc.md)), toda atualização e remoção deixa **linhas
mortas**. O VACUUM as recupera. Se ele não acompanha, a tabela **incha** (*bloat*) e tudo fica
lento. É a manutenção mais importante e mais negligenciada.

```sql
-- Ver saúde das tabelas: linhas vivas vs. mortas, último vacuum/analyze
SELECT relname,
       n_live_tup, n_dead_tup,
       round(n_dead_tup * 100.0 / nullif(n_live_tup + n_dead_tup, 0), 1) AS pct_morto,
       last_autovacuum, last_autoanalyze
FROM pg_stat_user_tables
ORDER BY n_dead_tup DESC;
```

O **autovacuum** roda sozinho, disparado quando a proporção de linhas mortas passa um limite. Ajuste
para tabelas muito escritas:

```sql
-- Tornar o autovacuum mais agressivo numa tabela quente
ALTER TABLE pedidos SET (autovacuum_vacuum_scale_factor = 0.05);   -- padrão 0.2
```

> **Os dois perigos que o VACUUM previne:**
> 1. **Bloat** — espaço morto acumulado deixa consultas lentas e desperdiça disco.
> 2. **Wraparound de XID** — os ids de transação são de 32 bits; se o VACUUM não "congela" linhas
>    antigas a tempo, o banco **para de aceitar escritas** para se proteger (ver [15](15-transacoes-e-mvcc.md)).
>    Monitore `age(datfrozenxid)`:
> ```sql
> SELECT datname, age(datfrozenxid) FROM pg_database ORDER BY 2 DESC;
> -- se algum se aproxima de ~2 bilhões, o autovacuum está atrasado — investigue JÁ
> ```

**A transação zumbi:** um `BEGIN` sem `COMMIT` (conexão de app travada, `idle in transaction`)
impede o VACUUM de limpar qualquer linha morta desde que ela começou. Uma transação esquecida por
horas incha o banco inteiro. Monitore e mate:
```sql
SELECT pid, state, now()-xact_start AS duracao, query
FROM pg_stat_activity WHERE state = 'idle in transaction' AND now()-xact_start > interval '5 min';
SELECT pg_terminate_backend(PID);
```

---

## 3. Tuning de configuração — os parâmetros que importam

O `postgresql.conf` padrão é conservador (feito para rodar em qualquer máquina). Os ajustes de
maior impacto:

| Parâmetro | Padrão | Recomendação inicial | Efeito |
|---|---|---|---|
| `shared_buffers` | 128 MB | ~25% da RAM | Cache de páginas do banco |
| `effective_cache_size` | 4 GB | ~50–75% da RAM | Pista ao planejador (não aloca) |
| `work_mem` | 4 MB | 16–64 MB (com cuidado) | Sort/hash por operação — **multiplica** |
| `maintenance_work_mem` | 64 MB | 256 MB–1 GB | VACUUM, CREATE INDEX |
| `random_page_cost` | 4.0 | **1.1 em SSD** | Faz o planejador favorecer índices |
| `max_connections` | 100 | manter baixo + pooler | Cada conexão é um processo |
| `wal_compression` | off | on | Reduz o volume de WAL |
| `checkpoint_timeout` / `max_wal_size` | — | aumentar em cargas de escrita | Menos checkpoints, menos I/O em picos |

> **Não copie um `postgresql.conf` da internet cegamente.** Use um ponto de partida calculado a
> partir da sua RAM/CPU/disco (o site [pgtune.leopard.in.ua](https://pgtune.leopard.in.ua) e a
> ferramenta `pgtune` geram um bom ponto de partida), depois ajuste medindo. Os dois ajustes de
> maior retorno e mais esquecidos: **`shared_buffers` proporcional à RAM** e **`random_page_cost=1.1`
> em SSD**.

```sql
SHOW shared_buffers;                    -- ver um parâmetro
ALTER SYSTEM SET random_page_cost = 1.1;  -- muda no postgresql.auto.conf
SELECT pg_reload_conf();                  -- aplica (parâmetros que não exigem restart)
```

---

## 4. Monitoramento — o que observar

```sql
-- Conexões e atividade
SELECT state, count(*) FROM pg_stat_activity GROUP BY state;
SELECT pid, now()-query_start AS duracao, state, query
FROM pg_stat_activity WHERE state='active' ORDER BY duracao DESC;

-- Cache hit ratio (deve ser > 99% num banco bem dimensionado)
SELECT round(sum(heap_blks_hit)*100.0/nullif(sum(heap_blks_hit+heap_blks_read),0),2) AS hit_pct
FROM pg_statio_user_tables;

-- Consultas mais custosas do sistema (a ferramenta nº 1 de tuning)
SELECT calls, round(mean_exec_time::numeric,2) AS ms_media,
       round(total_exec_time::numeric,1) AS ms_total, query
FROM pg_stat_statements ORDER BY total_exec_time DESC LIMIT 20;

-- Tamanhos
SELECT pg_size_pretty(pg_database_size(current_database()));
SELECT relname, pg_size_pretty(pg_total_relation_size(oid))
FROM pg_class WHERE relkind='r' ORDER BY pg_total_relation_size(oid) DESC LIMIT 10;

-- Bloqueios pendentes
SELECT * FROM pg_locks WHERE NOT granted;

-- Replicação (na principal)
SELECT client_addr, state, replay_lag FROM pg_stat_replication;
```

| Métrica | Alerta quando |
|---|---|
| Cache hit ratio | < 99% (falta RAM ou índices) |
| Conexões ativas / max_connections | perto do limite (falta pooler) |
| `n_dead_tup` / linhas | alto (autovacuum atrasado) |
| `age(datfrozenxid)` | perto de 2 bilhões (wraparound iminente) |
| Atraso de replicação | crescendo (réplica não acompanha) |
| Consultas > N segundos | latência acima do SLO |
| Espaço em disco | < 20% livre (WAL pode encher rápido) |

Ferramentas: **Prometheus + postgres_exporter + Grafana** (o padrão open source), **pgwatch**,
**pgAdmin**, e os monitores dos provedores de nuvem.

---

## 5. Migrações de esquema — evoluir sem quebrar

Mudar o esquema em produção, com dados e tráfego, é uma arte. Ferramentas de migração versionam as
mudanças: **Flyway**, **Liquibase**, **dbmate**, **sqitch**, ou as embutidas em frameworks
(Alembic, Rails, Prisma, Ecto).

As armadilhas que causam downtime:

```sql
-- ❌ Adicionar coluna NOT NULL com default em tabela grande, em versões antigas,
--    reescrevia a tabela inteira e travava. No PG moderno, default constante é instantâneo.
ALTER TABLE grande ADD COLUMN x INT NOT NULL DEFAULT 0;   -- ok no PG atual

-- ❌ Criar índice sem CONCURRENTLY trava escritas
CREATE INDEX ...;                          -- trava
CREATE INDEX CONCURRENTLY ...;             -- ✅ não trava

-- ❌ Adicionar FK valida a tabela inteira na hora (trava)
ALTER TABLE p ADD CONSTRAINT fk ... ;                          -- valida tudo, trava
ALTER TABLE p ADD CONSTRAINT fk ... NOT VALID;                 -- ✅ adiciona sem validar
ALTER TABLE p VALIDATE CONSTRAINT fk;                          -- valida depois, sem travar tanto

-- ❌ Renomear/dropar coluna que a app ainda usa → erro para clientes na versão antiga
```

> **Regra de migração sem downtime:** faça mudanças **compatíveis para trás**, em etapas.
> Adicionar antes de usar; parar de usar antes de remover. Nunca renomeie uma coluna num deploy —
> adicione a nova, migre os dados, atualize a app, remova a antiga depois. Isso é o *expand/contract*.

---

## 6. Diagnóstico de problemas comuns

| Sintoma | Investigação |
|---|---|
| "Ficou lento do nada" | `ANALYZE` (estatísticas velhas); `pg_stat_statements`; `EXPLAIN ANALYZE` |
| "Disco enchendo" | Bloat (`n_dead_tup`), `pg_wal/` crescendo (replicação parada? archive falhando?), tabela crescendo |
| "too many clients already" | `max_connections` atingido; falta pooler; conexões vazando |
| "Consulta travada" | `pg_locks` / `pg_stat_activity` — quem segura o lock? Transação zumbi? |
| "Banco não aceita escritas" | Wraparound de XID (autovacuum atrasado), ou disco cheio |
| "Réplica atrasando" | Rede, carga de escrita alta, réplica subdimensionada |
| "Corrupção" (raro) | `amcheck`; restaurar do backup; verificar hardware/disco |

Sempre olhe o **log** primeiro:
```bash
sudo tail -100 /var/log/postgresql/postgresql-18-main.log   # Debian/Ubuntu
# procure ERROR, FATAL, WARNING, deadlock, checkpoint, autovacuum
```

---

## 7. Rotina operacional

**Diária (automatizada):** backup verificado · alertas ativos (disco, replicação, conexões) ·
checar erros no log.

**Semanal:** revisar `pg_stat_statements` (consultas caras) · `n_dead_tup` (autovacuum) · espaço
em disco · índices não usados.

**Mensal:** aplicar minor updates de segurança · testar restauração de backup · revisar `work_mem`
e limites vs. uso real · revisar `age(datfrozenxid)`.

**Trimestral/anual:** planejar major upgrade · exercício de disaster recovery · revisão de
capacidade e crescimento.

---

## Autoteste

1. Por que "um backup nunca restaurado não é um backup"? Como se verifica um dump?
2. Diferencie backup lógico (`pg_dump`) de físico + PITR. Quando usar cada um?
3. Por que `pg_dump` não inclui as roles, e o que as inclui?
4. O que o VACUUM faz, e quais dois perigos ele previne?
5. Como uma transação zumbi (`idle in transaction`) incha o banco inteiro?
6. Quais são os dois ajustes de configuração de maior retorno e mais esquecidos?
7. Por que `work_mem` alto pode derrubar o servidor?
8. Qual comando mostra as consultas mais custosas do sistema, e por que ele é a ferramenta nº 1?
9. Descreva a regra *expand/contract* para migração sem downtime, com o exemplo de renomear uma
   coluna.
10. Você recebe "too many clients already". Cite três causas e a solução de cada.
