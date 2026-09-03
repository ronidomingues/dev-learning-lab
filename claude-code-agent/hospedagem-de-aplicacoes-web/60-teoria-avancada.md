# 60 · Teoria avançada — a matemática por trás das decisões

`Nível: avançado / pesquisa` · `Atualizado em 18/08/2026`

Aqui os "por quês" acabam em teorema, em física ou em decisão histórica documentada. Este
capítulo dá os modelos que permitem **prever** comportamento em vez de descobrir em produção.

---

## 1. Cold start: por que existe e quanto custa

### 1.1 A anatomia

Um serviço adormecido precisa reconstruir uma pilha inteira antes da primeira resposta:

```
t0  requisição chega ao roteador
t1  roteador percebe que não há instância viva               (~1 ms)
t2  agendador escolhe uma máquina                            (1 a 50 ms)
t3  puxa a imagem (se não houver cache local)                (0 a 30 s)
t4  cria o sandbox (container, microVM ou isolate)           (0,005 a 500 ms)
t5  inicia o runtime (Node, JVM, Python)                     (30 a 3.000 ms)
t6  a aplicação carrega, abre pool, lê configuração          (10 a 5.000 ms)
t7  health check passa                                        (0 a 30 s)
t8  responde
```

Ordens de grandeza medidas publicamente:

| Ambiente | Cold start típico |
|---|---|
| Cloudflare Workers (isolate V8) | **< 5 ms** |
| AWS Lambda, Node, 512 MB | 100 a 400 ms |
| AWS Lambda, JVM sem SnapStart | 1 a 6 s |
| Cloud Run, container mínimo | 300 ms a 2 s |
| Fly.io Machines, `suspend` | ~200 a 500 ms |
| Fly.io Machines, `stop` | 1 a 3 s |
| Neon, retomada de compute | ~500 ms |
| **Render Free (serviço dormindo)** | **~50 s** |

O Render Free é a exceção brutal: não é cold start de container, é **provisionamento
completo** de um serviço desalocado.

### 1.2 A matemática da probabilidade de cold start

Se as requisições chegam segundo um processo de Poisson com taxa λ (por segundo) e a
plataforma mantém a instância viva por T segundos após a última requisição, a probabilidade de
uma requisição encontrar tudo frio é a probabilidade de o intervalo anterior ter passado de T:

```
P(cold) = e^(−λ·T)
```

Com T = 900 s (os 15 minutos do Render):

| Requisições por hora | λ (1/s) | P(cold) |
|---|---|---|
| 1 | 0,00028 | **78%** |
| 4 | 0,0011 | 37% |
| 10 | 0,0028 | 8% |
| 60 (uma por minuto) | 0,0167 | 0,00003% |

**Leitura:** com 4 acessos por hora, mais de um terço dos seus visitantes espera 50 segundos.
Com 60 por hora, o problema desaparece sozinho. **Cold start é um problema de projeto de
baixo tráfego** — o que é uma ironia cruel, porque baixo tráfego é exatamente quem usa plano
gratuito.

*Por que não manter tudo sempre quente?* Porque memória alocada é o recurso escasso e não
compartilhável de um provedor multi-inquilino. Manter 100 mil serviços gratuitos com 512 MB
cada exigiria 51 TB de RAM ociosa. **Parada legítima: um trade-off econômico explícito.**

---

## 2. Filas: por que 80% de utilização já é tarde demais

Modele o seu serviço como uma fila **M/M/1** (chegadas de Poisson, atendimento exponencial, um
servidor). Com utilização ρ = λ/μ (taxa de chegada sobre capacidade de atendimento), o tempo
médio no sistema é:

```
W = 1 / (μ − λ) = (1/μ) / (1 − ρ)
```

O fator `1/(1−ρ)` é o **multiplicador de espera**:

| Utilização ρ | Multiplicador | Se o serviço leva 100 ms sozinho |
|---|---|---|
| 50% | 2× | 200 ms |
| 70% | 3,3× | 330 ms |
| 80% | 5× | 500 ms |
| 90% | **10×** | **1.000 ms** |
| 95% | **20×** | **2.000 ms** |
| 99% | **100×** | **10.000 ms** |

**Este é o resultado mais útil de toda a teoria de filas para quem opera sistemas:** a
degradação não é linear, é hiperbólica. Entre 50% e 70% de CPU quase nada muda; entre 90% e
95%, o mundo desaba. É por isso que a prática de SRE manda dimensionar para **60 a 70% de
utilização em pico** — e por isso um gráfico de CPU "só" em 85% é um alarme, não um conforto.

Com *c* servidores (M/M/c), a fórmula de Erlang C suaviza a curva: mais instâncias
paralelas absorvem melhor a variância. Daí a regra empírica de **três réplicas pequenas em vez
de uma grande** para carga irregular.

---

## 3. Pool de conexões: o gargalo escondido

### 3.1 Por que o PostgreSQL sofre

Um processo por conexão (decisão do POSTGRES de Berkeley, anos 1980). Cada processo custa
memória e o escalonador do kernel precisa alterná-los. A partir de algumas centenas de
conexões ativas, o throughput **cai** conforme você adiciona conexões — o clássico
*colapso por thrashing*.

### 3.2 Quantas conexões você precisa

Pela **Lei de Little**: `L = λ × W`, onde L é o número médio de requisições no sistema, λ é a
taxa de chegada e W é o tempo médio de cada uma.

```
Exemplo: 200 req/s, cada uma segurando a conexão por 5 ms
L = 200 × 0,005 = 1 conexão em uso, em média.

Com pico de 3× e alguma variância: 3 a 6 conexões bastam.
```

**Quase todo mundo configura pool grande demais.** Um `max: 50` num serviço que precisa de 4
não acelera nada — só aumenta a chance de estourar o limite do servidor quando você escalar
para cinco instâncias (5 × 50 = 250 conexões).

**Regra prática do PostgreSQL:** `max_connections` útil ≈ `(núcleos × 2) + discos_efetivos`
para trabalho **ativo**. Conexões acima disso só fazem sentido se estiverem ociosas — e para
ociosas existe pooler.

### 3.3 Modos de pooler

| Modo | Reutiliza a conexão quando | Suporta |
|---|---|---|
| **Session** | o cliente desconecta | tudo |
| **Transaction** | a transação termina | **não**: prepared statements nomeados, `LISTEN/NOTIFY`, temp table entre comandos, advisory lock de sessão |
| **Statement** | cada comando termina | só autocommit |

**Transaction** é o modo usado por PgBouncer, Supavisor e pela Neon, e é o que permite
milhares de clientes com dezenas de conexões reais. O preço é a lista de incompatibilidades
acima — e ela é a origem do bug de produção mais comum de quem adota pooler sem ler a
documentação (o Prisma usa prepared statements por padrão; é preciso desligar).

---

## 4. Cache: taxa de acerto, e por que 90% pode não bastar

Tempo médio efetivo com cache:

```
T_médio = h × T_cache + (1 − h) × T_banco
```

Com `T_cache = 0,3 ms` e `T_banco = 20 ms`:

| Acerto h | T_médio | Redução |
|---|---|---|
| 0% | 20 ms | — |
| 50% | 10,2 ms | 49% |
| 90% | 2,3 ms | 89% |
| 95% | 1,3 ms | 94% |
| 99% | 0,5 ms | 98% |

**Mas a carga no banco é o que interessa para a sobrevivência.** Com 1.000 req/s:

| Acerto | Requisições que chegam ao banco |
|---|---|
| 90% | **100/s** |
| 99% | **10/s** |
| 99,9% | **1/s** |

Ou seja: **subir de 90% para 99% divide a carga do banco por dez.** É por isso que vale muito
mais melhorar o TTL e a granularidade da chave do que trocar de servidor.

### 4.1 Estampida — a matemática do desastre

Quando uma chave popular expira, todas as requisições no intervalo entre a expiração e a
regravação vão ao banco:

```
requisições perdidas = λ × T_reconstrução
```

Com λ = 500 req/s e reconstrução de 800 ms: **400 consultas idênticas simultâneas**. Se o pool
tem 5 conexões, 395 requisições ficam esperando, o tempo de resposta explode, o health check
falha e a plataforma reinicia tudo — piorando o problema.

Mitigações, na ordem de simplicidade (implementação no [`06-exemplos.md`](06-exemplos.md),
exemplos 2 e 3):

1. **TTL com jitter** — aleatorize ±10%; evita expiração sincronizada em massa.
2. **Single-flight com trava** — só um reconstrói; os demais esperam.
3. **Recomputação antecipada probabilística** (*XFetch*): recalcule antes de expirar, com
   probabilidade crescente conforme o TTL se aproxima do fim. O artigo de referência é
   *Optimal Probabilistic Cache Stampede Prevention* (Vattani, Chierichetti, Lowenstein,
   VLDB 2015).
4. **Servir obsoleto enquanto revalida** (`stale-while-revalidate`) — devolve o valor velho e
   atualiza em segundo plano. É a melhor experiência quando dado ligeiramente velho é aceitável.

---

## 5. Latência de cauda: por que o p99 é o número que importa

Se uma página faz N chamadas **sequenciais** e cada uma tem probabilidade `p` de ser lenta, a
probabilidade de a página ser lenta é:

```
P(página lenta) = 1 − (1 − p)^N
```

Com p = 1% (o seu p99) e N = 10 chamadas: **9,6%**. **O p99 de um serviço vira o p90 de uma
página que o chama dez vezes.** É o fenômeno que Jeff Dean batizou de *tail at scale* (ACM,
2013): quanto mais componentes, mais a cauda domina a experiência.

Consequências práticas:

- **Média de latência é inútil** para decisão. Sempre p95 e p99.
- Reduzir o número de chamadas (agrupar, usar `JOIN`, carregar em lote) melhora mais que
  otimizar cada uma.
- **Requisições de resguardo** (*hedged requests*): dispare uma segunda cópia se a primeira
  passar do p95, e use a que responder antes. Custa ~5% de tráfego a mais e derruba o p99
  drasticamente. Só funciona em operações idempotentes.
- **Timeout agressivo com retentativa** costuma ser melhor que timeout longo — desde que haja
  *backoff* exponencial com jitter, senão você constrói uma tempestade de retentativas.

---

## 6. CAP, PACELC e o que isso significa na sua escolha

**Teorema CAP** (conjectura de Eric Brewer em 2000, provado por Gilbert e Lynch em 2002):
um sistema distribuído não pode oferecer simultaneamente **consistência**, **disponibilidade**
e **tolerância a partição de rede**. Como partição de rede não é opcional (ela acontece), a
escolha real é **C ou A durante uma partição**.

**PACELC** (Daniel Abadi, 2010) completa o quadro, e é mais útil na prática:

```
if (Partition)  then choose Availability or Consistency
else (Else)     then choose Latency or Consistency
```

A segunda metade é a que importa no dia a dia: **mesmo sem falha nenhuma, você troca latência
por consistência.** Onde isso aparece na sua pilha:

| Decisão | Você escolheu |
|---|---|
| Ler de réplica de leitura | **latência** (aceita ver dado atrasado) |
| Cache com TTL de 30 s | **latência** (aceita 30 s de dado velho) |
| Workers KV (consistência eventual, ~60 s) | **latência** |
| Ler sempre do primário | **consistência** |
| Transação `SERIALIZABLE` | **consistência** (paga em contenção) |

> **Isso não é teoria distante.** Toda vez que você põe um `SET chave valor EX 30`, está
> assinando um contrato PACELC: "aceito servir dado com até 30 segundos de atraso em troca de
> ser 60 vezes mais rápido". Escrever isso explicitamente no código, em comentário, evita
> discussões futuras sobre "bug" que na verdade é decisão.

---

## 7. Escrita: o gargalo final

Leitura escala com cache e réplica. **Escrita, não.** Um PostgreSQL com replicação em cascata
ainda tem **um único primário** aceitando escritas, limitado por:

1. **`fsync` do WAL** — durabilidade exige gravação confirmada em disco. Com SSD NVMe, algo
   entre 10 e 100 µs por sincronização; com `commit_delay`/`synchronous_commit = off`, mais
   rápido e menos durável.
2. **Contenção de bloqueios** — linhas quentes (um contador global, um saldo) serializam.
3. **Amplificação de escrita** — cada `UPDATE` no MVCC cria uma **nova versão** da linha e
   deixa a antiga para o `VACUUM` limpar. Atualizar a mesma linha mil vezes por segundo é o
   caminho mais rápido para inchar uma tabela.

**Padrões para contornar, em ordem de complexidade:**

| Padrão | Como | Custo |
|---|---|---|
| **Agregar antes de gravar** | contar no Redis (`INCR`) e descarregar no banco a cada 30 s | perde precisão instantânea |
| **Escrita em lote** | acumular e usar `COPY` ou `INSERT` múltiplo | latência de escrita maior |
| **Fila** | responder ao usuário e processar depois | consistência eventual |
| **Particionar** | dividir a tabela por tempo ou por chave | complexidade de consulta |
| **Fragmentar (*sharding*)** | dividir por cliente/região | **muito** complexo; evite enquanto der |
| **CRDT / multi-primário** | tipos de dado que convergem sem coordenação | modelo de dado restrito |

---

## 8. O custo marginal de um provedor multi-inquilino

Por que uma PaaS consegue cobrar US$ 7 pelo que lhe custaria US$ 40 fazer sozinho?

```
Custo total do provedor = F + v·N
   F = custo fixo (equipe, plataforma, ferramenta, rede)  ← altíssimo
   v = custo variável por cliente                         ← baixo
   N = número de clientes

Custo por cliente = F/N + v
```

Com F grande e N grande, `F/N → v`. **A economia de escala não é mágica: é diluição de custo
fixo.** É por isso que o mercado tende a poucos vencedores grandes, e por isso plataformas
novas precisam de capital de risco para sobreviver ao período em que N ainda é pequeno.

E é por isso que **auto-hospedar tem N = 1**: você paga o custo fixo inteiro sozinho — só que
o seu custo fixo é o seu tempo, que você talvez não contabilize.

---

## 9. Problemas em aberto (fronteira de pesquisa)

1. **Estado na borda.** Como oferecer leitura e escrita com latência baixa em 300 localidades,
   com garantias fortes? Tentativas em produção: Durable Objects (Cloudflare), Turso embarcado,
   D1 com réplicas de leitura, Cloud Spanner (com relógio atômico, TrueTime). Nenhuma resolve o
   caso geral.
2. **Cold start zero para código arbitrário.** Isolates resolvem para JS/WASM. Snapshot e
   restauração de microVM (Firecracker snapshot, AWS SnapStart) reduzem, mas não eliminam.
3. **Postgres com threads.** Discussão ativa na comunidade desde 2023; ainda não entregue até a
   versão 18. Mudaria a economia de conexões de forma profunda.
4. **Colocação automática de dados.** Decidir onde cada partição deve viver conforme o padrão
   de acesso real, movendo-a sem indisponibilidade.
5. **Serverless para trabalho com estado.** Funções são ótimas para requisição curta; treino de
   modelo, ETL e processamento longo continuam mal atendidos.
6. **Custo como restrição de primeira classe.** Escalonadores que otimizam explicitamente
   dinheiro (e carbono), não só latência e throughput. É o que a área chama de FinOps
   automatizado, e ainda é imaturo.

---

## Autoteste

1. Deduza a probabilidade de cold start com 4 requisições por hora e T = 900 s.
2. Por que o multiplicador de espera hiperbólico faz de 85% de CPU um alarme?
3. Use a Lei de Little para dimensionar o pool de um serviço com 300 req/s e 8 ms por consulta.
4. Que recursos o modo *transaction* de pooler quebra, e por que isso derruba o Prisma?
5. Por que subir a taxa de acerto de cache de 90% para 99% importa mais do que parece?
6. Calcule as requisições perdidas numa estampida com λ = 800 req/s e reconstrução de 500 ms.
7. Enuncie PACELC e mostre onde você já o aplicou sem perceber.
8. Por que `UPDATE` repetido na mesma linha incha a tabela no PostgreSQL?
9. Explique, com a fórmula `F/N + v`, por que auto-hospedar raramente é mais barato para um só sistema.

---

### Fontes consultadas (18/08/2026)

- Gilbert, S.; Lynch, N. — *Brewer's Conjecture and the Feasibility of Consistent, Available, Partition-Tolerant Web Services* (ACM SIGACT News, 2002)
- Abadi, D. — *Consistency Tradeoffs in Modern Distributed Database System Design* (IEEE Computer, 2012) — PACELC
- Dean, J.; Barroso, L. A. — *The Tail at Scale* (Communications of the ACM, 2013)
- Vattani, A.; Chierichetti, F.; Lowenstein, K. — *Optimal Probabilistic Cache Stampede Prevention* (VLDB 2015)
- Agache, A. et al. — *Firecracker: Lightweight Virtualization for Serverless Applications* (NSDI 2020)
- Kleppmann, M. — *How to do distributed locking* (2016) e a resposta de Sanfilippo sobre o Redlock
- PostgreSQL 18 — documentação de MVCC, WAL, `max_connections` e VACUUM
- Google — *Site Reliability Engineering* (capítulos sobre carga e latência)
