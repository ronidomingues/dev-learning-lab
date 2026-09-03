# 19 · Replicação e alta disponibilidade

`Nível: avançado` · `Última atualização: 11/08/2026`

Como fazer o PostgreSQL sobreviver à morte de uma máquina, distribuir a carga de leitura e não
perder dados. Onde "um banco só" deixa de bastar.

---

## 1. Por que replicar

Um único servidor tem dois problemas inevitáveis:

1. **Ele pode morrer.** Disco falha, máquina desliga, data center cai. Sem cópia, os dados somem e
   o serviço para.
2. **Ele tem um limite.** Uma máquina só aguenta tanta carga de leitura.

Replicação cria **cópias** do banco em outras máquinas. Isso dá:
- **Alta disponibilidade** — se a principal cair, uma réplica assume.
- **Escala de leitura** — distribuir consultas de leitura entre réplicas.
- **Backup vivo** — uma réplica é uma cópia atualizada, próxima de um backup.
- **Geografia** — réplicas perto dos usuários reduzem latência.

---

## 2. Replicação física (streaming) — a base

O mecanismo nativo mais usado. Lembra do **WAL** (ver [17-arquitetura-interna.md](17-arquitetura-interna.md))?
A replicação física simplesmente **envia o WAL** da principal para as réplicas, que o **reaplicam**,
ficando cópias byte a byte.

```
   PRIMARY (leitura + escrita)
      │  envia o fluxo de WAL
      ▼
   STANDBY / RÉPLICA (só leitura — "hot standby")
```

- A principal (*primary*) aceita escritas.
- As réplicas (*standby*) são **somente leitura** e aplicam o WAL continuamente.
- "Hot standby" significa que a réplica **aceita consultas** enquanto replica — você lê dela.

```sql
-- Na réplica, verificar o atraso em relação à principal
SELECT now() - pg_last_xact_replay_timestamp() AS atraso_replicacao;
-- Na principal, ver as réplicas conectadas
SELECT client_addr, state, sync_state, replay_lag FROM pg_stat_replication;
```

Configuração (esboço): a principal permite conexões de replicação (`pg_hba.conf`, um role
`REPLICATION`), e a réplica é criada com `pg_basebackup` + configuração de `primary_conninfo`.
Ferramentas como **repmgr**, **Patroni** e **pg_auto_failover** automatizam a montagem e o
*failover*.

### Síncrona vs. assíncrona — o trade-off central

| Modo | O `COMMIT` espera... | Perda em falha | Custo |
|---|---|---|---|
| **Assíncrona** (padrão) | só o WAL local ao disco | pode perder as últimas transações não replicadas | latência baixa |
| **Síncrona** | a réplica confirmar que recebeu | **zero** perda (RPO=0) | latência maior (espera a rede) |

> **A escolha honesta:** replicação **assíncrona** dá desempenho e é suficiente para a maioria — o
> risco é perder alguns segundos de transações se a principal morrer subitamente. Replicação
> **síncrona** garante zero perda, mas cada `COMMIT` espera a confirmação da réplica pela rede, o
> que aumenta a latência de escrita. Sistemas financeiros costumam exigir síncrona; a maioria vive
> bem com assíncrona. Você pode ter um meio-termo: síncrona para uma réplica próxima, assíncrona
> para as distantes.

---

## 3. Replicação lógica — seletiva e entre versões

Enquanto a física copia **tudo**, byte a byte, a **replicação lógica** decodifica o WAL em
**mudanças de linha** (`INSERT`/`UPDATE`/`DELETE`) e as envia seletivamente:

```sql
-- Na origem: publicar tabelas específicas
CREATE PUBLICATION minha_pub FOR TABLE clientes, pedidos;

-- No destino: assinar
CREATE SUBSCRIPTION minha_sub
    CONNECTION 'host=origem dbname=loja user=repl password=...'
    PUBLICATION minha_pub;
```

Vantagens sobre a física:
- **Seletiva** — replica só algumas tabelas, não o banco inteiro.
- **Entre versões diferentes** — permite **upgrade de major sem downtime** (replica da 17 para a 18,
  depois vira a chave).
- **Destino gravável** — a réplica lógica pode ter suas próprias tabelas e escritas.
- **Consolidação** — juntar dados de vários bancos num só (data warehouse).

Limitações: não replica DDL (mudanças de esquema) automaticamente, precisa de chave primária nas
tabelas, e tem mais sobrecarga que a física. Cada uma serve a um propósito.

---

## 4. Failover — quando a principal morre

Se a principal cai, uma réplica precisa **assumir** (*promote*) como nova principal:

```
   1. Detectar que a principal morreu (health check)
   2. Escolher a réplica mais atualizada
   3. Promovê-la a principal (pg_promote / pg_ctl promote)
   4. Redirecionar as aplicações para a nova principal
   5. Reconstruir as outras réplicas para seguir a nova principal
```

**Fazer isso à mão sob pressão é arriscado.** Por isso existem orquestradores:

| Ferramenta | O que faz |
|---|---|
| **Patroni** | O padrão de fato; usa um armazenamento de consenso (etcd/Consul) para eleger a principal automaticamente |
| **repmgr** | Gerência de replicação e failover, mais simples |
| **pg_auto_failover** | Failover automático da própria comunidade |
| **PgBouncer/pgcat + HAProxy** | Roteamento das conexões para a principal atual |

> **O perigo do *split-brain*:** se a rede se parte e **duas** máquinas acham que são a principal,
> ambas aceitam escritas e os dados divergem irreconciliavelmente. Prevenir isso é o trabalho mais
> difícil da alta disponibilidade, e a razão de os orquestradores usarem um sistema de consenso
> (que exige maioria para eleger). Nunca improvise failover manual sem um mecanismo contra
> split-brain.

**RTO e RPO** — o vocabulário de continuidade:
- **RPO** (*Recovery Point Objective*): quanto dado você tolera perder (assíncrona: segundos;
  síncrona: zero).
- **RTO** (*Recovery Time Objective*): quanto tempo até voltar (failover automático: segundos a
  minutos; manual: horas).

---

## 5. Point-In-Time Recovery (PITR)

Diferente de replicação, PITR é sobre **voltar no tempo**. Combinando um backup base
(`pg_basebackup`) com o **arquivamento contínuo do WAL**, você pode restaurar o banco a **qualquer
instante** — inclusive "cinco minutos antes de alguém rodar aquele `DELETE` sem `WHERE`".

```
   Backup base (segunda-feira)  +  WAL arquivado (contínuo)
                                    │
                                    ▼
   restaurar até '2026-08-11 14:32:00'  ← o instante exato antes do erro
```

Configuração (esboço): `archive_mode = on` e `archive_command` (ou `archive_library`) enviam cada
WAL cheio para um armazenamento seguro; na restauração, você aponta `recovery_target_time`.
Ferramentas que empacotam isso: **pgBackRest** (o padrão robusto), **Barman**, **WAL-G** (para
armazenamento de objetos como S3).

> **PITR é a rede de segurança contra erro humano**, que a replicação **não** dá: uma réplica copia
> fielmente o `DROP TABLE` errado. Só o PITR (ou um backup lógico antigo) te leva a antes do erro.
> Ver [21-administracao-e-operacao.md](21-administracao-e-operacao.md).

---

## 6. Distribuir a leitura na aplicação

Com réplicas de leitura, a aplicação roteia:
- **Escritas e leituras que precisam ser imediatamente consistentes** → principal.
- **Leituras que toleram um pequeno atraso** (relatórios, listagens) → réplicas.

Cuidado com a **consistência eventual**: numa réplica assíncrona, um dado recém-escrito na
principal pode ainda não ter chegado. "Escrevi e não vejo na hora" é o sintoma. Para o fluxo
"escreveu → leu logo em seguida", leia da principal, ou use *read-your-writes* explícito.

---

## 7. Escala horizontal (sharding) — o limite

Replicação escala **leitura**, mas toda escrita ainda vai para **uma** principal. Quando a escrita
excede uma máquina, entra o **sharding**: particionar os dados por chave entre vários nós, cada um
com sua fatia.

| Abordagem | Como |
|---|---|
| **Citus** (extensão) | Distribui tabelas por uma chave de shard; SQL distribuído transparente |
| **Sharding na aplicação** | A app decide em qual nó cada dado mora (complexo, mas total controle) |
| **Postgres distribuído gerenciado** | Cloud SQL, Aurora, AlloyDB, CockroachDB (compatível), Yugabyte |

*Opinião profissional:* **a maioria dos projetos nunca precisa de sharding.** Uma única principal
moderna, bem ajustada, com réplicas de leitura, aguenta uma quantidade enorme de carga — dezenas de
milhares de transações por segundo. Sharding adiciona complexidade grande (transações distribuídas,
JOINs entre shards, rebalanceamento) e deve ser a última opção, não a primeira. Escale verticalmente
(máquina maior) e com réplicas de leitura antes de shardar.

---

## Autoteste

1. Quais são os quatro benefícios de replicar um banco?
2. Como a replicação física funciona, em termos de WAL?
3. Qual é o trade-off entre replicação síncrona e assíncrona, em RPO e latência?
4. Cite três vantagens da replicação lógica sobre a física.
5. Como a replicação lógica permite upgrade de major sem downtime?
6. O que é *split-brain*, e por que os orquestradores usam um sistema de consenso?
7. Diferencie RTO de RPO.
8. Por que uma réplica **não** protege contra um `DROP TABLE` errado, e o que protege?
9. Qual é o sintoma de ler de uma réplica assíncrona logo após escrever na principal?
10. Por que sharding deve ser a última opção, e o que tentar antes?
