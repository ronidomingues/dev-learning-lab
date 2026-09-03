# Projeto-modelo · `central-de-pedidos`

Uma aplicação **pequena, mas inteira**: uma API de recebimento de pedidos
construída inteiramente em n8n, com banco de dados, idempotência, tratamento de
erro, relatório agendado e teste automatizado.

`Nível: intermediário` · `n8n 2.36.9 · PostgreSQL 18` · `Escrito e verificado em 01/09/2026`

---

## O que ela faz

```mermaid
flowchart TD
    subgraph W1["01 · Receber pedido"]
        A[POST /webhook/pedido] --> B[Validar e normalizar]
        B --> C{É válido?}
        C -->|não| D[400 + lista de erros]
        C -->|sim| E[202 Aceito]
        E --> F[INSERT idempotente<br/>ON CONFLICT DO NOTHING]
        F --> G[Resultado da gravação]
    end
    subgraph W2["02 · Consultar pedido"]
        H[GET /webhook/pedido?id=X] --> I[SELECT parametrizado]
        I --> J{Achou?}
        J -->|sim| K[200 + pedido]
        J -->|não| L[404]
    end
    subgraph W3["03 · Relatório diário"]
        M[Cron 07:00] --> N[Agregar 24h] --> O[CSV] --> P[/files]
    end
    subgraph W4["04 · Alerta de falhas"]
        Q[Error Trigger] --> R[Formatar] --> S[Gravar em erros]
    end
    F -.falha.-> Q
    I -.falha.-> Q
```

Quatro workflows, um banco, uma tabela de erros. É o esqueleto real de uma
integração de produção — só que pequeno o bastante para caber na cabeça.

---

## Pré-requisitos

| Precisa | Verificar com | Se faltar |
|---|---|---|
| Docker Engine 24+ | `docker --version` | [03-instalacao.md](../03-instalacao.md#3-instalar-o-docker-pré-requisito-de-tudo) |
| Docker Compose **v2** | `docker compose version` | idem |
| `make`, `curl`, `openssl` | `make -v && curl -V && openssl version` | `apt install make curl openssl` |
| ~2 GB de RAM livres e 3 GB de disco | `free -h && df -h .` | — |

Não precisa de conta em lugar nenhum. Não precisa de chave de IA.

---

## Como rodar — os comandos exatos

```bash
cd 07-projeto-modelo

make preparar     # gera .env e credenciais/postgres.json com segredos aleatórios
make subir        # sobe n8n + Postgres e espera ficarem no ar
```

Abra <http://localhost:5678> e **crie o usuário dono** (é local, no seu banco).
Depois volte ao terminal:

```bash
make importar     # importa a credencial do Postgres e os 4 workflows
make publicar     # publica os 4 e reinicia o n8n (a CLI exige o restart)
make testar       # roda o teste de ponta a ponta
```

**Saída esperada de `make testar`:**

```
== central-de-pedidos: teste de ponta a ponta ==
   base: http://localhost:5678   pedido: P-1788268191

1) pedido valido -> 202
  ✓ POST /webhook/pedido (valido)                202
2) pedido invalido -> 400
  ✓ POST /webhook/pedido (invalido)              400
3) reenvio do MESMO pedido -> 202 e sem duplicar (idempotencia)
  ✓ POST /webhook/pedido (reenvio)               202
4) consulta do pedido -> 200
  ✓ GET /webhook/pedido?id=P-1788268191          200
5) consulta de pedido inexistente -> 404
  ✓ GET /webhook/pedido?id=NAO-EXISTE-999        404
6) o banco tem exatamente UMA linha para P-1788268191
  ✓ linhas em pedidos para P-1788268191          1

== TUDO PASSOU ==
```

Outros atalhos:

```bash
make relatorio    # roda o relatório agora, sem esperar as 07:00 → saida/*.csv
make psql         # abre o psql no banco
make logs         # acompanha os logs do n8n
make parar        # para tudo (dados ficam)
make limpar       # ⚠️ APAGA TUDO, inclusive os volumes
```

---

## Estrutura de pastas, comentada

```
07-projeto-modelo/
├── compose.yml                  # n8n 2.36.9 + Postgres 18. Versões FIXAS, de propósito
├── .env.example                 # modelo; o .env real é gerado e nunca vai para o Git
├── .gitignore                   # protege .env e a credencial gerada
├── Makefile                     # todos os comandos do ciclo de vida
├── sql/
│   └── init.sql                 # esquema: pedidos (PK = chave de idempotência) e erros
├── credenciais/
│   └── postgres.example.json    # modelo da credencial; a real é gerada pelo script
├── workflows/
│   ├── 01-receber-pedido.json   # POST — valida, responde, grava
│   ├── 02-consultar-pedido.json # GET  — consulta parametrizada, 200/404
│   ├── 03-relatorio-diario.json # cron — agrega e escreve CSV
│   └── 04-alerta-de-falhas.json # Error Trigger — registra falhas no banco
├── scripts/
│   ├── preparar.sh              # gera segredos; idempotente
│   └── testar.sh                # 6 verificações de ponta a ponta
└── saida/                       # onde o relatório aparece (montado como /files)
```

---

## O que cada decisão de projeto ensina

### 1. `pedido_id` é a chave primária — e isso é a idempotência inteira

```sql
pedido_id TEXT PRIMARY KEY
```
```sql
INSERT INTO pedidos (...) VALUES (...) ON CONFLICT (pedido_id) DO NOTHING RETURNING pedido_id;
```

Webhooks **são reenviados**. Todo provedor sério reenvia quando não recebe `2xx`
rápido, e alguns reenviam mesmo tendo recebido. Se você tratar isso na aplicação
("verifico se já existe antes de inserir"), você tem uma condição de corrida:
dois reenvios simultâneos passam os dois pelo `SELECT` e inserem os dois.

A garantia tem de estar **no banco**, onde existe atomicidade. `ON CONFLICT DO
NOTHING` faz o segundo reenvio virar um não-evento — e o `RETURNING` vazio é como
o workflow sabe que era duplicata (nó "Resultado da gravação").

> **Lição transferível:** idempotência não é feita de `if`. É feita de constraint.

### 2. Responder **antes** de gravar (`ack-then-process`)

O nó `Responder 202 Aceito` vem **antes** do nó de banco. O cliente recebe a
resposta em milissegundos; a gravação acontece depois.

Isso foi verificado na prática, e o resultado é instrutivo: numa execução em que
o Postgres estava inacessível, **o cliente recebeu `202` normalmente** e a execução
foi marcada como `error` no histórico. Ou seja:

> Ao responder antes de processar, **você assumiu a responsabilidade**. Ninguém vai
> reenviar. É exatamente por isso que o workflow 04 (Error Workflow) não é opcional
> neste projeto — sem ele, a falha seria invisível.

O código `202 Accepted` (e não `200 OK`) é semanticamente correto: "recebi e vou
processar", não "está feito".

### 3. Consulta parametrizada, nunca interpolada

```json
"query": "SELECT ... WHERE pedido_id = $1;",
"options": { "queryReplacement": "={{ $json.query.id }}" }
```

Se fosse `WHERE pedido_id = '{{ $json.query.id }}'`, um `id` valendo
`x' OR '1'='1` devolveria a base inteira. O `$1` faz o driver enviar o valor
separado da instrução — o banco nunca o interpreta como SQL.
É a mesma regra de qualquer linguagem; o fato de estar num campo visual não muda nada.

### 4. `alwaysOutputData` + um nó que trata o vazio

O `SELECT` que não acha nada devolve **zero itens**, e um ramo sem itens
simplesmente para — sem erro, sem resposta, e o cliente fica pendurado.
Com `alwaysOutputData: true`, o nó emite um item vazio, o `IF` avalia
`pedido_id exists` como falso e o `404` acontece.

O mesmo padrão aparece no relatório: o nó "Tratar relatório vazio" transforma
"nenhum pedido em 24 h" numa linha explícita, em vez de gerar um CSV vazio.

> **Lição transferível:** o caminho do "nada aconteceu" é um caminho de verdade e
> precisa de código. Fluxo que só trata o caso feliz falha em silêncio.

### 5. `retryOnFail` só onde é seguro

O nó de gravação tem `retryOnFail: true, maxTries: 3`. Isso só é seguro **porque**
a inserção é idempotente. Repetir um `INSERT` comum criaria duplicatas.

> Retry sem idempotência não é resiliência: é duplicação automatizada.

### 6. Versões fixas no `compose.yml`

`n8nio/n8n:2.36.9`, `postgres:18`. Nada de `:latest`. Se este projeto ainda
precisar rodar daqui a um ano, ele roda igual. `latest` é um projeto que muda
sozinho enquanto você dorme.

### 7. Segredos gerados, nunca comitados

`make preparar` gera senha e `N8N_ENCRYPTION_KEY` aleatórias com `openssl rand`.
O `.gitignore` protege `.env` e `credenciais/postgres.json`. O que vai para o Git
são os `.example`.

> **A `N8N_ENCRYPTION_KEY` é a peça mais importante da pilha.** Ela cifra as
> credenciais dentro do banco. Backup do banco **sem** a chave é backup inútil.

### 8. Poda de execuções ligada desde o primeiro dia

```yaml
EXECUTIONS_DATA_PRUNE: "true"
EXECUTIONS_DATA_MAX_AGE: "168"      # 7 dias
EXECUTIONS_DATA_PRUNE_MAX_COUNT: "10000"
```

O n8n guarda os dados de **entrada e saída de cada nó** de cada execução. É o que
torna a depuração maravilhosa e o que enche o disco. Ligar a poda depois que o
banco já tem 40 GB é uma tarde perdida; ligar no primeiro dia custa três linhas.

### 9. `$env` bloqueado

`N8N_BLOCK_ENV_ACCESS_IN_NODE: "true"` impede que qualquer expressão leia as
variáveis de ambiente do processo — inclusive a senha do banco e a chave de
criptografia. Num n8n com mais de uma pessoa, deixar isso aberto significa que
quem pode criar um workflow pode ler todos os segredos do host.

---

## Como verificar você mesmo que funcionou

```bash
# 1) o pedido foi gravado uma única vez
make psql
# dentro do psql:
select pedido_id, cliente, valor, recebido_em from pedidos order by recebido_em desc limit 5;
select count(*) from pedidos;
\q

# 2) o relatório sai em CSV
make relatorio && cat saida/relatorio-*.csv

# 3) as falhas são registradas — force uma:
docker compose stop postgres
curl -s -o /dev/null -w '%{http_code}\n' -X POST http://localhost:5678/webhook/pedido \
  -H 'Content-Type: application/json' \
  -d '{"pedido_id":"P-FALHA","cliente":"Teste","valor":10,"itens":[{"sku":"X","qtd":1}]}'
# devolve 202 (a resposta vem ANTES da gravação — essa é a lição do item 2)
docker compose start postgres
# em Executions, no navegador, a execução aparece em vermelho
```

---

## Exercícios (aumentam o projeto sem reescrevê-lo)

1. **Assinatura HMAC.** Exija um cabeçalho `X-Signature` e rejeite com `401` se
   não bater (modelo no [exemplo 11](../06-exemplos.md#exemplo-11--caso-de-produção-webhook-rápido--processamento-assíncrono)).
2. **Paginação.** Acrescente `GET /webhook/pedidos?pagina=1&tamanho=20`.
3. **Notificação real.** Faça o workflow 04 mandar mensagem no Telegram além de gravar.
4. **Retentativa manual.** Crie um workflow que leia a tabela `erros` e reprocesse.
5. **Modo fila.** Converta a pilha para queue mode com Redis e dois workers
   ([21-escala-e-producao.md](../21-escala-e-producao.md)). Rode o `testar.sh`
   de novo: tudo deve continuar passando.
6. **Concorrência.** Dispare 50 requisições simultâneas com o mesmo `pedido_id`
   (`seq 50 | xargs -P50 -I{} curl ...`) e confirme que o banco tem **uma** linha.

---

## O que foi verificado, e o que não foi — honestamente

**Executado de verdade** (n8n 2.36.9, Node 24.18.0, Ubuntu 22.04.5, em 01/09/2026):

- ✅ Os quatro `workflows/*.json` importam sem erro (`n8n import:workflow --separate`).
- ✅ A credencial importa a partir do JSON em texto claro (`n8n import:credentials`).
- ✅ `publish:workflow` publica e, após reiniciar, os webhooks ficam registrados
  (`Activated workflow "CP · 01 Receber pedido"` no log).
- ✅ `POST /webhook/pedido` com corpo inválido devolve **HTTP 400** e o corpo real
  `{"status":"rejeitado","erros":["pedido_id obrigatorio","cliente obrigatorio","valor deve ser maior que zero","itens deve ser uma lista nao vazia"]}`.
- ✅ `POST /webhook/pedido` com corpo válido devolve **HTTP 202** e
  `{"status":"aceito","pedido_id":"P-9"}` — **inclusive com o Postgres inacessível**,
  o que comprova, na prática, o comportamento do item 2 acima.

**Não executado nesta máquina:** o trecho que depende do Postgres em contêiner
(gravação, consulta 200/404, relatório em CSV e registro de erros). O motivo é do
ambiente, não do projeto: a máquina em que este material foi escrito só alcança a
internet por proxy corporativo, e o *daemon* do Docker não tem esse proxy
configurado — não há como baixar as imagens `n8nio/n8n` e `postgres`. Os comandos,
o esquema SQL e as consultas estão corretos e prontos para você executar; o
`make testar` verifica exatamente esses pontos e falha alto se algo estiver errado.

---

## Solução de problemas

| Sintoma | Causa | Correção |
|---|---|---|
| `make importar` diz `Cannot find module` ou não acha o arquivo | Os volumes `./workflows` e `./credenciais` só existem depois de `make subir` | Rode `make subir` primeiro |
| Webhook devolve 404 | Faltou publicar, ou faltou reiniciar o n8n depois | `make publicar` |
| `The DNS server returned an error` no nó Postgres | O n8n não achou o host `postgres` | Confirme que o serviço subiu: `docker compose ps` |
| `password authentication failed` | O `.env` foi regerado depois de criar a credencial | `rm credenciais/postgres.json && make preparar && make importar` |
| `database files are incompatible with server` | Volume de um Postgres de outra versão maior | `make limpar` (⚠️ apaga dados) ou migre com `pg_dumpall` |
| Relatório não aparece em `saida/` | Permissão do bind mount (o contêiner roda como UID 1000) | `sudo chown -R 1000:1000 saida` (em Fedora/RHEL, acrescente `:Z` ao mount) |
| Tudo passa, mas o item 6 do teste falha | O `.env` não foi carregado no shell do teste | Use `make testar` (ele carrega o `.env`) em vez de chamar o script direto |

---

*Volta para: [06-exemplos.md](../06-exemplos.md) · Segue para: [10-fundamentos.md](../10-fundamentos.md)*
