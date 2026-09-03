# 18 · Compose e aplicações multi-container

`Nível: intermediário` · `Última atualização: 11/08/2026`

Compose é o que transforma "sei rodar um container" em "sei rodar uma aplicação". É também a
ferramenta mais usada e menos estudada do ecossistema.

---

## 1. O que o Compose faz por você

A partir de um `compose.yaml`, ele:

1. **Cria uma rede** dedicada ao projeto, com DNS por nome de serviço.
2. **Constrói ou baixa** as imagens declaradas.
3. **Cria volumes** nomeados, prefixados pelo nome do projeto.
4. **Inicia os serviços na ordem** definida por `depends_on`.
5. **Rotula tudo** (`com.docker.compose.project=...`), o que permite operar o conjunto como uma
   unidade.

```bash
docker compose up -d
docker network ls  | grep $(basename $PWD)   # rede criada automaticamente
docker volume ls   | grep $(basename $PWD)   # volumes prefixados
```

O **nome do projeto** vem, em ordem de precedência: da flag `-p`, da chave `name:` no arquivo,
da variável `COMPOSE_PROJECT_NAME`, ou do **nome da pasta**. Duas pastas com o mesmo nome em
máquinas diferentes geram recursos com o mesmo nome — fonte de confusão em CI. Declare `name:`
explicitamente.

---

## 2. Compose v1 × v2, e o `version:` que morreu

| | v1 (`docker-compose`) | v2 (`docker compose`) |
|---|---|---|
| Implementação | Python, binário separado | Go, plugin da CLI |
| Suporte | **encerrado em julho de 2023** | atual |
| Comando | `docker-compose` (hífen) | `docker compose` (espaço) |
| Especificação | `version: "3.8"` no topo | **Compose Specification** — sem `version:` |

```yaml
version: "3.8"     # ❌ obsoleto: ignorado, e gera aviso
services:          # ✅ comece direto aqui
```

Se você encontrar tutorial com `docker-compose` e `version:`, ele é de antes de 2023. O conteúdo
pode continuar válido, mas verifique tudo o que for sintaxe.

---

## 3. Anatomia de um `compose.yaml` completo

```yaml
name: minha-aplicacao          # nome do projeto, explícito

x-comum: &comum                # âncora YAML: bloco reutilizável
  restart: unless-stopped
  logging:
    driver: json-file
    options: { max-size: "10m", max-file: "3" }
  networks: [interna]

services:

  api:
    <<: *comum                 # herda o bloco acima
    build:
      context: .
      dockerfile: Dockerfile
      target: producao
      args:
        NODE_VERSION: "22"
      cache_from:
        - type=registry,ref=ghcr.io/org/api:cache
    image: ghcr.io/org/api:${TAG:-dev}
    environment:
      DATABASE_URL: postgres://app:${DB_SENHA:?defina DB_SENHA}@db:5432/app
      NODE_ENV: production
    env_file:
      - path: .env
        required: false
    depends_on:
      db: { condition: service_healthy }
      migracao: { condition: service_completed_successfully }
    healthcheck:
      test: ["CMD", "wget", "-qO-", "http://127.0.0.1:3000/saude"]
      interval: 15s
      timeout: 3s
      retries: 3
      start_period: 20s
    deploy:
      replicas: 2
      resources:
        limits:       { cpus: "1.0", memory: 512M }
        reservations: { memory: 128M }
    stop_grace_period: 30s
    security_opt: [no-new-privileges:true]
    cap_drop: [ALL]
    read_only: true
    tmpfs: [/tmp]
    networks: [interna, borda]

  migracao:
    <<: *comum
    image: ghcr.io/org/api:${TAG:-dev}
    command: ["npm", "run", "migrate:up"]
    depends_on:
      db: { condition: service_healthy }
    restart: "no"              # roda uma vez e termina

  db:
    <<: *comum
    image: postgres:16.3-alpine
    environment:
      POSTGRES_USER: app
      POSTGRES_PASSWORD: ${DB_SENHA:?}
      POSTGRES_DB: app
    volumes:
      - dados-db:/var/lib/postgresql/data
      - ./db/init.sql:/docker-entrypoint-initdb.d/10-init.sql:ro
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app -d app"]
      interval: 5s
      timeout: 3s
      retries: 10
      start_period: 10s
    shm_size: 256mb            # o Postgres usa memória compartilhada; o padrão de 64MB aperta

volumes:
  dados-db:

networks:
  borda:
  interna:
    internal: true
```

---

## 4. `depends_on` — as três condições

| Condição | Espera até | Uso |
|---|---|---|
| `service_started` (padrão) | O container **iniciar** | Quase nunca é suficiente |
| `service_healthy` | O **healthcheck** passar | **O que você quer** em bancos e APIs |
| `service_completed_successfully` | O container **sair com código 0** | Migrações, seeds, tarefas de preparo |

```yaml
depends_on:
  db:       { condition: service_healthy }
  migracao: { condition: service_completed_successfully }
```

`service_started` é insuficiente porque "o container iniciou" não significa "o serviço aceita
conexão". A imagem oficial do Postgres, por exemplo, **reinicia internamente** durante a
primeira inicialização — conectar cedo dá "connection refused" enganoso.

**Se o serviço não tem healthcheck**, ou você quer robustez independente da ordem, faça o
próprio app tentar de novo:

```javascript
async function conectarComEspera(tentativas = 10) {
  for (let i = 1; i <= tentativas; i++) {
    try { return await conectar(); }
    catch (e) {
      const espera = Math.min(1000 * 2 ** i, 30000);   // backoff exponencial com teto
      console.log(`tentativa ${i} falhou, aguardando ${espera}ms`);
      await new Promise(r => setTimeout(r, espera));
    }
  }
  throw new Error('banco indisponível após todas as tentativas');
}
```

*Opinião profissional:* `depends_on` resolve a ordem no **boot**; a lógica de reconexão no app
resolve o resto da vida do sistema (banco reiniciado, rede oscilando, failover). Em produção,
**os dois** são necessários — `depends_on` sozinho é insuficiente e reconexão sozinha atrasa o
boot.

---

## 5. Variáveis, `.env` e interpolação

Ordem de precedência (do mais forte para o mais fraco):

1. Variável do ambiente do shell
2. `--env-file` na linha de comando
3. `.env` no diretório do projeto
4. Valor padrão na interpolação (`${VAR:-padrao}`)

| Sintaxe | Comportamento |
|---|---|
| `${VAR}` | Vazio se indefinida |
| `${VAR:-padrao}` | `padrao` se indefinida **ou vazia** |
| `${VAR-padrao}` | `padrao` só se **indefinida** |
| `${VAR:?mensagem}` | **Aborta** com a mensagem se indefinida ou vazia |
| `${VAR:+valor}` | `valor` só se VAR estiver definida |

> **Distinção que confunde:** o arquivo `.env` alimenta a **interpolação do YAML**;
> `env_file:` injeta variáveis **dentro do container**. São coisas diferentes, e usar uma
> esperando a outra é erro comum.

```yaml
services:
  api:
    environment:
      URL: ${API_URL}          # ← vem do .env do projeto (interpolação)
    env_file:
      - .env.aplicacao         # ← vai para dentro do container
```

```bash
docker compose config     # ← O MELHOR DEPURADOR: mostra o YAML final resolvido
```

---

## 6. Sobreposição de arquivos: base + ambiente

`compose.yaml` (base):
```yaml
services:
  api:
    image: ghcr.io/org/api:${TAG:-latest}
    environment:
      NODE_ENV: production
```

`compose.override.yaml` (**carregado automaticamente**, se existir):
```yaml
services:
  api:
    build: .
    environment:
      NODE_ENV: development
    volumes:
      - ./src:/app/src
    ports:
      - "3000:3000"
```

`compose.prod.yaml` (explícito):
```yaml
services:
  api:
    deploy:
      replicas: 3
      resources:
        limits: { memory: 1G }
```

```bash
docker compose up -d                                       # base + override (dev)
docker compose -f compose.yaml -f compose.prod.yaml up -d   # base + prod
```

**As regras de mesclagem, que causam surpresa:**

| Tipo | Comportamento |
|---|---|
| Escalares (`image`, `command`) | O último **substitui** |
| Mapas (`environment`, `labels`) | **Mesclados** chave a chave |
| Listas (`ports`, `volumes`) | **Concatenadas** — e é aqui que dá problema |

Concatenação de listas significa que você **não consegue remover** uma porta ou um volume por
sobreposição, só acrescentar. Para casos assim, use `!reset` (Compose recente) ou arquivos
separados sem base comum:

```yaml
services:
  api:
    ports: !reset []
```

---

## 7. Perfis

```yaml
services:
  api:
    # sem profiles → sempre sobe

  depurador:
    profiles: [debug]
    image: nicolaka/netshoot
    command: sleep infinity

  ferramentas:
    profiles: [tools, debug]     # participa de dois perfis
    image: minha-app:1.0
```

```bash
docker compose up -d                       # só a api
docker compose --profile debug up -d       # api + depurador + ferramentas
COMPOSE_PROFILES=debug,tools docker compose up -d
```

Uso típico: um único arquivo servindo a dev, testes, ferramentas de administração e produção,
sem multiplicar arquivos.

---

## 8. `docker compose watch` — desenvolvimento sem bind mount de tudo

```yaml
services:
  api:
    build: .
    develop:
      watch:
        - action: sync           # copia o arquivo para dentro do container
          path: ./src
          target: /app/src
          ignore: ["**/*.test.js"]
        - action: rebuild        # mudou dependência → reconstrói a imagem
          path: package.json
        - action: sync+restart   # copia e reinicia o processo
          path: ./config
          target: /app/config
```

```bash
docker compose watch
```

Vantagem sobre bind mount: **muito mais rápido em macOS e Windows** (copia arquivos em vez de
montar um sistema de arquivos através da fronteira da VM) e permite reagir de formas diferentes
conforme o arquivo alterado.

---

## 9. Escala e as suas limitações

```bash
docker compose up -d --scale api=3
docker compose ps
# minha-aplicacao-api-1, -api-2, -api-3
```

O DNS interno devolve os três IPs para o nome `api`, e um proxy à frente pode balancear.

**O que quebra ao escalar, e por quê:**

| Problema | Causa | Solução |
|---|---|---|
| `ports: "3000:3000"` falha na 2ª réplica | Porta do host já ocupada | Remova `ports:`; use proxy. Ou faixa: `"3000-3002:3000"` |
| Estado divergente entre réplicas | Cada uma tem sua camada de escrita | Estado em banco ou volume compartilhado |
| Migração roda 3 vezes | Cada réplica executa o entrypoint | Serviço de migração separado |
| Sessão perdida a cada requisição | Sessão em memória do processo | Sessão em Redis |
| Cron duplicado | Todas as réplicas têm o mesmo agendador | Serviço dedicado, ou lock distribuído |

> **O limite honesto do Compose:** ele opera **um host**. Sem reagendamento em falha de máquina,
> sem *rolling update* de verdade, sem balanceamento nativo entre nós. Para isso existem Swarm e
> Kubernetes — [25-orquestracao.md](25-orquestracao.md).

---

## 10. Compose em produção — quando faz sentido

*Opinião profissional, e há discordância legítima:* **Compose em produção é uma escolha
respeitável para um servidor só.** Homelab, aplicação interna, produto pequeno, SaaS em estágio
inicial — Kubernetes ali é complexidade sem retorno.

O que fazer para tornar isso sério:

```yaml
services:
  api:
    image: ghcr.io/org/api@sha256:abc...   # por DIGEST, nunca por tag
    restart: unless-stopped
    healthcheck: { test: [...], start_period: 20s }
    deploy:
      resources:
        limits: { memory: 512M, cpus: "1.0" }
    logging:
      driver: json-file
      options: { max-size: "10m", max-file: "3" }
    security_opt: [no-new-privileges:true]
    cap_drop: [ALL]
    read_only: true
    tmpfs: [/tmp]
```

E o deploy:
```bash
docker compose pull
docker compose up -d --wait      # --wait retorna só quando os healthchecks passarem
docker image prune -af --filter "until=168h"
```

**Deixe o systemd cuidar do boot:**

```ini
# /etc/systemd/system/minha-app.service
[Unit]
Description=Minha aplicação
Requires=docker.service
After=docker.service network-online.target

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/minha-app
ExecStart=/usr/bin/docker compose up -d --wait
ExecStop=/usr/bin/docker compose down
TimeoutStartSec=300

[Install]
WantedBy=multi-user.target
```
```bash
sudo systemctl enable --now minha-app
```

**Quando sair do Compose:** mais de um servidor; necessidade de deploy sem interrupção com
rollback automático; escala automática; equipes múltiplas dividindo infraestrutura. Antes disso,
Kubernetes costuma custar mais do que entrega.

---

## 11. Segredos no Compose

```yaml
services:
  db:
    image: postgres:16
    environment:
      POSTGRES_PASSWORD_FILE: /run/secrets/db_senha   # ← as imagens oficiais aceitam _FILE
    secrets: [db_senha]

secrets:
  db_senha:
    file: ./segredos/db_senha.txt      # em Swarm: external: true
```

O segredo é montado em `/run/secrets/db_senha` num **tmpfs** (RAM). Vantagem sobre
`environment:`: variáveis de ambiente aparecem em `docker inspect`, em `/proc/PID/environ`, em
logs de crash e são herdadas por processos filhos. Arquivo em tmpfs, não.

> Fora do Swarm, `secrets` do Compose é essencialmente um bind mount conveniente — não há
> criptografia em repouso nem distribuição segura. Para isso, use o gerenciador de segredos da
> plataforma (Vault, AWS Secrets Manager, SOPS + age).

---

## 12. Comandos e diagnóstico

```bash
docker compose config                  # YAML final resolvido — comece SEMPRE por aqui
docker compose config --services       # lista os serviços
docker compose ps -a                   # inclui os que saíram
docker compose logs -f --tail 100 api
docker compose exec api sh             # no container em execução
docker compose run --rm api npm test   # container novo e efêmero
docker compose top
docker compose events
docker compose down --remove-orphans   # remove containers de serviços que você apagou do YAML
docker compose kill -s SIGHUP api      # envia um sinal específico
```

| Sintoma | Diagnóstico |
|---|---|
| "Minha variável não chegou" | `docker compose config` mostra o valor resolvido |
| "O serviço sobe e morre" | `docker compose logs SERVIÇO` (funciona com o container parado) |
| "Um serviço não enxerga o outro" | `docker compose exec a ping b`; confira se estão na mesma rede |
| "Sobrou container de um serviço que apaguei" | `docker compose down --remove-orphans` |
| "Alterei o YAML e nada mudou" | `docker compose up -d --force-recreate` |
| "A imagem não foi reconstruída" | `docker compose up -d --build` |

---

## Autoteste

1. Cite três coisas que o Compose faz automaticamente e que você teria de fazer à mão com
   `docker run`.
2. Por que `version: "3.8"` não deve mais aparecer, e o que o substituiu?
3. Explique as três condições de `depends_on`, com um exemplo de uso para cada.
4. Qual é a diferença entre o arquivo `.env` e a chave `env_file:`?
5. `${DB_SENHA:?erro}` e `${DB_SENHA:-padrao}`: o que cada um faz quando a variável falta?
6. Como listas e mapas se comportam na sobreposição de arquivos, e qual das duas causa problema?
7. Você roda `--scale api=3` e a segunda réplica falha. Qual é a causa mais provável?
8. Quando `docker compose watch` é preferível a bind mount, e por quê?
9. Por que `secrets` é melhor que `environment` para uma senha? Cite dois vazamentos que ele
   evita.
10. Em que ponto Compose em produção deixa de ser adequado? Dê três critérios objetivos.
