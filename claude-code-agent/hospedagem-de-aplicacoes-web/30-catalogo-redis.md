# 30 · Catálogo — onde hospedar o **Redis** (e o que aconteceu com o nome dele)

`Nível: intermediário` · `Preços e limites consultados na web em 18/08/2026`

---

## 0. Antes dos preços: a crise de licença de 2024–2025

Você vai encontrar três nomes — **Redis**, **Valkey** e **Dragonfly** — e precisa saber o que
cada um é, porque isso afeta o que você pode usar comercialmente.

```
1º trimestre de 2009 ── Salvatore Sanfilippo (antirez) cria o Redis. Licença BSD.
mar/2024 ────────────── Redis Inc. abandona a BSD e adota dupla licença
                        RSALv2 + SSPLv1 (fonte disponível, NÃO open source pela OSI).
                        Motivo declarado: provedores de nuvem lucravam com o produto
                        sem contribuir.
1 semana depois ─────── A Linux Foundation forka o Redis 7.2.4 e cria o VALKEY, sob BSD.
                        Apoiam AWS, Google Cloud, Oracle, Ericsson, Snap.
nov/2024 ────────────── antirez volta à Redis Inc.
mai/2025 ────────────── Redis 8 passa a ser TRI-licenciado: você escolhe AGPLv3
                        (aprovada pela OSI) OU RSALv2 OU SSPLv1.
2025–2026 ───────────── Valkey vira o padrão: Fedora, Ubuntu 26.04 LTS, Debian, Arch;
                        AWS torna Valkey o padrão em ElastiCache e MemoryDB, com preço
                        abaixo do Redis OSS. Linha atual: Valkey 9.x. Redis: linha 8.x.
```

**O que isso significa na prática, para você:**

| Se você… | Use |
|---|---|
| Consome um serviço gerenciado (Upstash, Redis Cloud, Render) | Tanto faz. A licença é problema do provedor |
| Roda no seu VPS e o sistema é interno | Redis 8 (AGPLv3) ou Valkey. Ambos servem |
| **Vende software que embute o servidor** | **Valkey (BSD)**. A AGPLv3 do Redis 8 obriga a disponibilizar o código de serviços derivados; a SSPL é ainda mais abrangente |
| Quer o caminho de menor atrito e maior futuro | **Valkey** — é o que as distribuições e as nuvens escolheram |

**Compatibilidade:** Valkey 9 é *drop-in* para Redis 7.2 — mesmo protocolo (RESP), mesmos
comandos, mesmos clientes. Trocar `redis:7` por `valkey/valkey:9` no seu compose costuma ser
uma linha. Divergências começam nos recursos exclusivos do Redis 8+ (alguns módulos, busca
vetorial) e nos recursos novos do Valkey (multi-thread de I/O mais agressivo, menor uso de
memória).

> **Recomendação, declarada como opinião:** use **Valkey** em qualquer coisa que você
> auto-hospede. Não por ideologia: porque é o que vem por padrão no seu Linux, o que a AWS
> cobra mais barato, e o que não vai criar uma conversa jurídica em uma auditoria.

---

## 1. Resumo executivo dos provedores

| Serviço | Gratuito | Limite do gratuito | Persistência | Região no Brasil | Cobrança |
|---|---|---|---|---|---|
| **Upstash** | ✅ permanente | **256 MB, 500 mil comandos/mês, 10 GB de banda, até 10 bancos** | sim | ✅ (primária ou réplica) | por comando |
| **Redis Cloud (Essentials)** | ✅ permanente | **30 MB, 30 conexões, 100 ops/s, 5 GB/mês** | não no gratuito | ✅ via AWS `sa-east-1` | por plano fixo |
| **Aiven for Valkey** | ✅ permanente | plano gratuito de nó único (recursos limitados) | conforme plano | ❌ | por plano |
| **Render Key Value** | ✅ permanente | **25 MB, sem persistência** (perde tudo ao reiniciar) | ❌ no gratuito | ❌ | por plano |
| **Railway** | ❌ | consome o crédito | sim | ❌ | por uso |
| **Fly.io** | ❌ | — (rode Valkey você mesmo numa máquina) | você decide | ✅ `gru` | por máquina |
| **AWS ElastiCache/MemoryDB** | ⚠️ | créditos do novo plano gratuito | sim (MemoryDB) | ✅ `sa-east-1` | por hora |
| **Auto-hospedado (VPS)** | ❌ (custo do VPS) | a RAM que você tiver | você decide | onde quiser | zero adicional |

---

## 2. Upstash — **a recomendação padrão**

**O que é.** Redis serverless: você não aluga um servidor, paga por **comando executado**.
Fala tanto o protocolo Redis (RESP, com TLS) quanto uma **API REST sobre HTTPS** — e essa
segunda porta é o que faz o Upstash funcionar em Cloudflare Workers, Vercel Edge e redes
corporativas que bloqueiam a porta 6379.

**Gratuito (18/08/2026):**
- **500.000 comandos por mês**
- **256 MB** de dados
- **10 GB** de banda mensal
- **até 10 bancos de dados gratuitos** (além disso, US$ 0,50 por banco)

**Pago:** *Pay as you go* a **US$ 0,20 por 100 mil comandos**, armazenamento US$ 0,25/GB
(1 GB grátis), banda US$ 0,03/GB acima de 200 GB/mês. Planos fixos: 250 MB por US$ 10/mês,
1 GB por US$ 20/mês, 5 GB por US$ 100/mês.

**Global:** um banco pode ter uma região primária de escrita e réplicas de leitura em outras
regiões — **São Paulo está entre elas**.

**Veredito.** É o padrão do mercado para projeto pequeno e para arquitetura serverless.
**Cuidado com a matemática da cota:** 500 mil comandos por mês ≈ **16 mil comandos por dia**.
Se cada requisição do seu app faz 3 comandos (ler cache, contar, limitar taxa), a cota acaba
em **~5.500 requisições diárias**. Não é pouco para um projeto pessoal, e é muito pouco para
um sistema com tráfego. Meça antes de assumir.

**Erros literais frequentes:**

```
Error: Protocol error, got "\x15" as reply type byte
  → você conectou sem TLS. Use rediss:// e --tls.

ERR max daily request limit exceeded
  → cota estourada. Espere o ciclo ou mude de plano.

ERR max request size exceeded
  → valor grande demais. O Upstash limita o tamanho de requisição no plano gratuito.
```

---

## 3. Redis Cloud (Redis Inc.) — plano Essentials gratuito

**Gratuito:** **30 MB**, **30 conexões simultâneas**, **100 operações por segundo**,
**5 GB de banda mensal**, infraestrutura compartilhada, **1 banco**, sem alta
disponibilidade, sem SLA, suporte comunitário.

**Veredito.** 30 MB e 100 ops/s são pouco — é uma vitrine, não uma camada de produção. A
vantagem é que você usa o **Redis oficial**, com os módulos da casa (busca, JSON, séries
temporais, vetores) que não existem no Valkey. Se o seu caso precisa de `RediSearch` ou de
busca vetorial, é aqui ou é auto-hospedado.

---

## 4. Render Key Value

**Gratuito:** um por workspace, **25 MB, sem persistência** — reiniciou, perdeu tudo. Ao
migrar do plano gratuito para um pago, **os dados também são perdidos**.

**Veredito.** Serve exatamente para o que um cache deve ser: descartável. **Não use para
sessão** se deslogar todo mundo for um problema, e **jamais para fila** — perder mensagens
silenciosamente é pior que não ter fila.

---

## 5. Auto-hospedar Valkey/Redis

A opção mais barata e, para cache, a mais sensata quando você já tem um VPS.

```bash
docker run -d --name cache --restart unless-stopped \
  -p 127.0.0.1:6379:6379 \
  valkey/valkey:9 \
  valkey-server --maxmemory 256mb --maxmemory-policy allkeys-lru \
                --save "" --appendonly no --requirepass "$SENHA_FORTE"
```

Cada opção, e por quê:

| Opção | O que faz | Por que |
|---|---|---|
| `-p 127.0.0.1:6379:6379` | publica **só no localhost** | **Redis exposto na internet é sequestrado em minutos.** Sem isso, você vira minerador de cripto |
| `--maxmemory 256mb` | teto de memória | sem teto, o Redis cresce até o kernel matar o processo (OOM) |
| `--maxmemory-policy allkeys-lru` | descarta o menos usado ao encher | a política certa **para cache**. Para fila, use `noeviction` |
| `--save "" --appendonly no` | desliga persistência | cache não precisa sobreviver; economiza I/O |
| `--requirepass` | exige senha | defesa em profundidade, mesmo no localhost |
| `--restart unless-stopped` | volta após reboot | óbvio, e sempre esquecido |

> **Aviso sério.** Redis sem autenticação exposto à internet é uma das portas mais exploradas
> que existem. O ataque clássico grava uma chave SSH no `authorized_keys` via `CONFIG SET dir`
> e o servidor é seu — de outra pessoa. Desde a versão 3.2 existe o *protected mode*, que
> mitiga o caso padrão, mas **não confie nele**: use bind em localhost, senha e firewall.
> Veja [`portas-de-rede`](../portas-de-rede/00-MAPA.md).

---

## 6. Dragonfly — a alternativa de desempenho

Reimplementação compatível com o protocolo Redis, multi-thread, com foco em usar melhor
máquinas grandes. Licença **BSL** (Business Source License — *não* é open source pela OSI;
converte-se em Apache 2.0 após alguns anos). Há um Dragonfly Cloud gerenciado.

**Veredito.** Interessante quando você tem **uma máquina grande e um único Redis
sobrecarregado**, porque escala em núcleos (o Redis executa comandos em uma thread só). Para
99% dos leitores deste curso, é otimização prematura — e a licença BSL merece leitura antes de
uso comercial.

---

## 7. Quanto Redis você realmente precisa?

Faça a conta antes de escolher o plano. Estimativas úteis:

| Uso | Tamanho por item | 100 mil itens |
|---|---|---|
| Sessão (JSON pequeno, ~500 B) | ~600 B com sobrecarga | ~60 MB |
| Cache de consulta (1 KB) | ~1,1 KB | ~110 MB |
| Contador (`INCR`) | ~80 B | ~8 MB |
| Chave de rate limit (janela fixa) | ~90 B | ~9 MB |
| Item em Redis Stream | ~200 B + payload | depende do `MAXLEN` |

**Comandos por mês** = requisições/dia × comandos por requisição × 30.
Exemplo: 2.000 requisições/dia × 3 comandos × 30 = **180 mil comandos/mês** — cabe no gratuito
do Upstash com folga. A 10.000 requisições/dia, são 900 mil: **não cabe**.

**Truques que reduzem consumo drasticamente:**
- **Pipeline**: agrupe N comandos numa ida e volta. (Atenção: no Upstash, **cada comando ainda
  conta**; o pipeline economiza latência, não cota.)
- Prefira **um `HGETALL`** a cinco `GET`.
- Use `BLOCK` em vez de *polling* em filas — polling a cada 100 ms gasta 864 mil comandos/dia.
- **Cache local em memória do processo, com TTL de segundos, na frente do Redis.** Corta a
  maioria das leituras repetidas. (Aceite a divergência entre instâncias; para cache de
  configuração, é irrelevante.)

---

## 8. Quando você **não** precisa de Redis

Vale dizer, porque metade dos projetos pequenos adiciona Redis por hábito:

- **Cache de poucos itens que mudam pouco** → um `Map` com TTL no processo resolve, com zero
  infraestrutura. Só perde em consistência entre instâncias.
- **Fila de baixo volume** → uma tabela no PostgreSQL com `SELECT ... FOR UPDATE SKIP LOCKED`
  é uma fila transacional, durável e boa até dezenas de milhares de mensagens por hora — e
  você já tem o Postgres.
- **Trava** → `pg_advisory_lock` no PostgreSQL é mais seguro que trava em Redis
  (veja [`06-exemplos.md`](06-exemplos.md), exemplo 3).
- **Contador exato** → o PostgreSQL conta certo; o Redis conta rápido. Escolha conforme o que
  dói mais.
- **Pub/sub simples** → `LISTEN/NOTIFY` do PostgreSQL resolve (com a ressalva de não funcionar
  através de pooler em modo transaction).

> **Opinião:** acrescente o Redis quando **medir** um problema — latência de consulta,
> contenção no banco, necessidade de rate limit distribuído. Adicioná-lo "porque toda
> arquitetura tem" é uma peça a mais para operar, monitorar e pagar.

---

## Autoteste

1. Conte a história da licença do Redis entre março de 2024 e maio de 2025, e diga o que é o Valkey.
2. Você vende um produto que embute o servidor de cache. Qual você escolhe e por quê?
3. Quantas requisições diárias cabem no plano gratuito do Upstash se cada uma faz 3 comandos?
4. Por que o Render Key Value gratuito não serve para fila?
5. Cite as cinco opções do comando de auto-hospedagem e o motivo de cada uma.
6. Qual é o ataque clássico contra um Redis exposto sem senha?
7. Dê três casos em que o PostgreSQL substitui o Redis, e o que se perde em cada um.
8. Por que pipeline não economiza cota no Upstash, mas ainda vale a pena?

---

### Fontes consultadas (18/08/2026)

- Upstash — página de preços do Redis e documentação de *Global Database* — upstash.com
- Redis — *Redis Cloud Essentials plan details* (plano gratuito de 30 MB) — redis.io/docs
- Redis — anúncio de licença de março de 2024 e retorno ao open source com AGPLv3 (maio de 2025)
- Linux Foundation / Valkey — anúncio do fork e notas da linha 9.x
- Render — *Free instance types* (Key Value de 25 MB sem persistência)
- Aiven — *Free tier* e *Free Valkey database*
- AWS — documentação do ElastiCache/MemoryDB (Valkey como padrão e preço reduzido)
- Dragonfly — licença BSL e documentação do projeto
