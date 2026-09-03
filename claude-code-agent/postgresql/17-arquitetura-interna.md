# 17 · Arquitetura interna — o que acontece por baixo

`Nível: avançado` · `Última atualização: 11/08/2026`

Sem caixas-pretas. Como o PostgreSQL organiza processos, memória e disco — e por que essas
escolhas o tornam tão robusto.

---

## 1. O modelo de processos: um por conexão

Diferente de muitos servidores modernos (que usam threads), o PostgreSQL usa **um processo do
sistema operacional por conexão**. Quando um cliente conecta, o processo mestre (*postmaster*) faz
um `fork` e cria um processo *backend* dedicado àquela conexão.

```
   postmaster (processo mestre — escuta a porta 5432, aceita conexões)
      │  fork() a cada conexão
      ├── backend (conexão do cliente A)
      ├── backend (conexão do cliente B)
      │
      ├── ── processos de segundo plano (sempre presentes): ──
      ├── background writer   (escreve páginas sujas no disco, aos poucos)
      ├── checkpointer        (garante que tudo até um ponto foi ao disco)
      ├── WAL writer          (grava o log de escrita)
      ├── autovacuum launcher (dispara os vacuums)
      ├── autovacuum workers  (limpam linhas mortas)
      ├── stats collector     (estatísticas de uso)
      └── (replicação) walsender / walreceiver
```

```bash
ps aux | grep postgres    # você vê o postmaster e um backend por conexão
```
```sql
SELECT pid, usename, application_name, state FROM pg_stat_activity;
```

### A consequência: conexões são caras

Cada conexão é um **processo** (com sua memória). Abrir uma conexão custa (fork), e milhares de
conexões consomem RAM e sobrecarregam o SO. Por isso:

- `max_connections` tem um limite prático (padrão 100; centenas, não milhares).
- Aplicações web devem usar um **pool de conexões** (reaproveitar conexões, ver o
  [projeto-modelo](07-projeto-modelo/app/src/db.js)).
- Para **muitas** conexões (serverless, microserviços), use um *pooler* externo como **PgBouncer**
  ou **pgcat**, que multiplexa milhares de clientes sobre poucas conexões reais.

> O PG 14+ reduziu bastante o custo por conexão ociosa, e há trabalho contínuo nessa direção, mas
> o modelo de processo por conexão continua sendo a razão pela qual "só abra mais conexões" não
> escala — e por que o pooler existe.

---

## 2. A memória: compartilhada e por processo

```
   ┌─────────────────────────────────────────────┐
   │           MEMÓRIA COMPARTILHADA              │  (todos os processos veem)
   │  shared_buffers   ← cache de páginas do banco│  ~25% da RAM
   │  WAL buffers      ← log de escrita pendente  │
   │  locks, etc.                                 │
   └─────────────────────────────────────────────┘
   ┌──────────────┐ ┌──────────────┐ ┌────────────┐
   │ backend A    │ │ backend B    │ │  ...       │  MEMÓRIA POR PROCESSO
   │ work_mem     │ │ work_mem     │ │            │  (privada de cada conexão)
   │ temp_buffers │ │ temp_buffers │ │            │
   └──────────────┘ └──────────────┘ └────────────┘
```

| Parâmetro | O que é | Ajuste típico |
|---|---|---|
| `shared_buffers` | Cache de páginas do banco, compartilhado | ~25% da RAM |
| `work_mem` | Memória por operação de sort/hash, **por conexão** | 16–64 MB (cuidado: multiplica) |
| `maintenance_work_mem` | Memória para VACUUM, CREATE INDEX | 256 MB–1 GB |
| `effective_cache_size` | Pista ao planejador de quanta RAM o SO tem para cache | ~50–75% da RAM |
| `wal_buffers` | Buffer do WAL | geralmente automático |

> **A armadilha do `work_mem`:** ele é **por operação, por conexão**. Uma consulta com 3
> ordenações, em 100 conexões, pode usar `3 × 100 × work_mem`. Definir `work_mem = 1GB` "para ir
> rápido" com 100 conexões pode pedir 300 GB e derrubar o servidor por falta de memória. Ajuste com
> a concorrência em mente.

---

## 3. O WAL — a alma da durabilidade

O **WAL** (*Write-Ahead Log*, log de escrita antecipada) é a ideia mais importante da arquitetura,
e a base do "A" e do "D" de ACID.

> **A regra do WAL:** antes de modificar uma página de dados no disco, o PostgreSQL primeiro
> escreve no WAL **o que vai fazer**. Só depois altera os dados. O WAL é sequencial (rápido de
> escrever) e é a fonte da verdade.

Por que isso dá durabilidade e atomicidade:

- **Crash no meio de uma transação?** Ao reiniciar, o PostgreSQL lê o WAL e **reaplica** (*redo*) o
  que foi confirmado mas não chegou aos arquivos de dados, e **ignora** o que não foi confirmado. O
  banco volta a um estado consistente. Isso é a *crash recovery*.
- **`COMMIT` só retorna** depois que o WAL correspondente está **fisicamente no disco** (`fsync`).
  Por isso um `COMMIT` sobrevive a queda de energia: o registro dele já está gravado.

```
   Transação                    Disco
   BEGIN
   UPDATE ...    ──escreve──▶  WAL (sequencial, rápido)   ← isto acontece primeiro
   COMMIT        ──fsync────▶  WAL forçado ao disco       ← só então o COMMIT retorna
                              ...
   checkpoint    ──────────▶  arquivos de dados atualizados (depois, em segundo plano)
```

**Checkpoints:** periodicamente, o *checkpointer* garante que todas as mudanças até um ponto foram
gravadas nos arquivos de dados, permitindo descartar o WAL antigo. Checkpoints muito frequentes
sobrecarregam o I/O; muito espaçados alongam a recuperação. É um parâmetro de tuning
(`checkpoint_timeout`, `max_wal_size`).

**O WAL habilita muito mais que recuperação:**
- **Replicação** (streaming) — enviar o WAL para outro servidor que o reaplica (ver
  [19-replicacao-e-alta-disponibilidade.md](19-replicacao-e-alta-disponibilidade.md)).
- **PITR** (*Point-In-Time Recovery*) — restaurar a um instante exato, arquivando o WAL.
- **Replicação lógica** — decodificar o WAL em mudanças de linha para enviar seletivamente.

---

## 4. O I/O assíncrono do PostgreSQL 18

Historicamente, quando um backend precisava ler uma página do disco, ele **bloqueava** esperando o
disco responder. O **PG 18** introduziu um subsistema de **I/O assíncrono (AIO)**: o backend pode
disparar várias leituras e continuar trabalhando enquanto o disco as atende.

- Controlado por `io_method`: `io_uring` no Linux (usa a interface moderna do kernel) ou um método
  baseado em *workers* como alternativa multiplataforma.
- Benefício reportado: melhorias de 2–3× em operações que leem muito do disco — varreduras
  sequenciais, *bitmap heap scans*, VACUUM.

É a mudança arquitetural mais significativa da versão 18, e a base de ganhos futuros. Ver
[65-estado-da-arte.md](65-estado-da-arte.md).

---

## 5. Como uma linha vive no disco

```
   Arquivo de dados de uma tabela (heap)
   ┌──────────── página de 8 KB ────────────┐
   │ cabeçalho │ ponteiros → │ ... espaço ...│
   │           │             │  tupla │ tupla│
   └─────────────────────────────────────────┘
```

- A unidade de I/O é a **página** de **8 KB**. O banco lê e escreve páginas inteiras, não linhas
  soltas.
- Cada tabela é um ou mais arquivos de 1 GB em `base/<oid_do_banco>/<oid_da_tabela>`.
- Valores grandes (textos longos, JSONB grande) são movidos para uma área separada chamada
  **TOAST** (*The Oversized-Attribute Storage Technique*), automaticamente comprimidos e/ou
  fatiados, para a linha principal caber na página.
- Cada linha carrega os carimbos `xmin`/`xmax` do MVCC (ver [15](15-transacoes-e-mvcc.md)).

```sql
SELECT pg_relation_filepath('pedidos');       -- o caminho do arquivo da tabela
SELECT pg_size_pretty(pg_total_relation_size('pedidos'));  -- tabela + índices + TOAST
```

---

## 6. Onde tudo fica (o diretório de dados)

```bash
sudo -u postgres psql -c "SHOW data_directory;"    # ex.: /var/lib/postgresql/18/main
```

| Caminho | Conteúdo |
|---|---|
| `base/` | Os dados: um subdiretório por banco, arquivos por tabela/índice |
| `global/` | Objetos do cluster (roles, tablespaces) |
| `pg_wal/` | Os arquivos de WAL — **crítico**; não apague à mão |
| `pg_stat/`, `pg_stat_tmp/` | Estatísticas |
| `postgresql.conf` | Configuração principal (no Debian/Ubuntu fica em `/etc/postgresql/...`) |
| `pg_hba.conf` | Autenticação: quem conecta de onde e como |
| `postmaster.pid` | PID do processo mestre |

> **Nunca mexa nos arquivos do diretório de dados à mão.** Não copie tabelas, não apague WAL, não
> edite arquivos de dados. O único jeito seguro de manipular dados é via SQL, e de fazer backup é
> via `pg_dump`/`pg_basebackup`. Copiar `base/` com o banco rodando captura um estado inconsistente.

---

## 7. O ciclo de vida de um `UPDATE`, ponta a ponta

Juntando tudo, o que acontece em `UPDATE pedidos SET status='pago' WHERE id=1; COMMIT;`:

1. O **backend** recebe o SQL, o parser/planner produzem um plano.
2. O executor encontra a linha (via índice em `id`).
3. **MVCC:** em vez de sobrescrever, cria uma **nova versão** da linha com `status='pago'` e marca a
   antiga com `xmax` (a versão antiga ainda é visível a quem começou antes).
4. A mudança é registrada no **WAL** (na memória, `wal_buffers`).
5. A página de dados alterada fica **suja** em `shared_buffers` (ainda não no disco de dados).
6. No `COMMIT`, o WAL é forçado ao disco (`fsync`) — **agora** a transação é durável, e o COMMIT
   retorna.
7. Depois, em segundo plano, o **background writer**/**checkpointer** gravam a página suja nos
   arquivos de dados.
8. Mais tarde, o **autovacuum** limpa a versão antiga da linha quando ninguém mais precisa dela.

Cada passo mapeia para um componente da arquitetura — e nenhum é mágica.

---

## Autoteste

1. Como o PostgreSQL trata cada conexão (processo ou thread)? Qual é a consequência prática?
2. Por que conexões são "caras", e o que se usa para ter muitas delas (pool, pooler)?
3. Qual é a diferença entre `shared_buffers` e `work_mem`, e qual é a armadilha do `work_mem`?
4. Enuncie a regra do WAL e explique como ela dá durabilidade após uma queda de energia.
5. Por que um `COMMIT` só retorna depois do `fsync` do WAL?
6. O que a I/O assíncrona do PG 18 mudou, e em quais operações?
7. Qual é a unidade de I/O do PostgreSQL, e o que é o TOAST?
8. Por que você nunca deve copiar os arquivos de `base/` com o banco rodando?
9. O que os processos background writer, checkpointer e autovacuum fazem?
10. Descreva o ciclo de vida de um `UPDATE ... COMMIT`, do backend ao autovacuum.
