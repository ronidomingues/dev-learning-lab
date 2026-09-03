# Exercício — Compose

> **Tente antes de olhar.** Solução após o separador.

## Enunciado

### Parte A — encontrar os defeitos

Este `compose.yaml` tem **pelo menos 8 problemas**. Encontre-os, explique a
consequência de cada um e escreva a versão corrigida.

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
      - "5432:5432"
    environment:
      - DATABASE_URL=postgresql+asyncpg://admin:admin123@db:5432/app
      - SECRET_KEY=chave-super-secreta-de-producao
    depends_on:
      - db
    restart: always

  db:
    image: postgres
    environment:
      - POSTGRES_PASSWORD=admin123
    ports:
      - "5432:5432"
```

### Parte B — construir

Escreva do zero um `compose.yaml` para um blog com:

- API em FastAPI (build local, porta 8000, só no loopback do host)
- Postgres com dados persistentes e healthcheck
- Redis para cache, **sem** persistência
- A API só deve subir depois que Postgres **e** Redis estiverem prontos
- Senha do banco por secret, não por variável de ambiente
- Banco e cache inalcançáveis a partir do host
- Valide com `docker compose config --quiet`

---
---
---

# SOLUÇÃO COMENTADA

## Parte A — os problemas

### 1. `version: '3.8'` — descontinuado

Emite aviso no Compose v2+. Remova a chave.

### 2. `ports: "5432:5432"` na **api**

A API não escuta em 5432 — isso é porta de banco. Provavelmente copiado sem
pensar. Publica uma porta onde ninguém atende, e se houver conflito o `up` falha
com `port is already allocated`.

### 3. Postgres publicando `5432` no host — **grave**

`"5432:5432"` faz o Docker escutar em `0.0.0.0`: **toda a sua LAN** alcança o
banco. Com a senha `admin123`, é questão de tempo.

E o detalhe que quase ninguém sabe: **as regras de iptables do Docker passam por
cima do UFW**. `ufw deny 5432` ativo e a porta continua aberta.

O banco não precisa de porta publicada — a API o alcança pela rede interna.
Se você precisa acessar de fora para depurar, use `127.0.0.1:5432:5432` ou um
túnel SSH.

### 4. Senha em `environment:`

`admin123` e `SECRET_KEY` vazam em `docker inspect`, em `/proc/1/environ` e para
todo subprocesso. Além de serem senhas fracas e duplicadas em dois lugares (se
mudar uma e esquecer a outra, quebra).

### 5. `image: postgres` sem tag

Equivale a `postgres:latest`. Hoje traz a 18, amanhã a 19 — e uma atualização de
major do Postgres **não** lê o diretório de dados da anterior. O container entra
em restart loop com `database files are incompatible with server`.

### 6. **Sem volume no banco** — o mais grave de todos

Sem `volumes:`, os dados moram na camada de escrita do container. `docker
compose down` remove o container e **todos os dados somem**.

### 7. `depends_on` sem `condition`

Espera o container iniciar, não o Postgres aceitar conexão. A API tenta conectar
antes e morre com `connection refused`. Funciona na sua máquina e falha no
servidor.

### 8. `restart: always` em vez de `unless-stopped`

Com `always`, um serviço que você parou manualmente volta sozinho após reboot.

### 9. Sem healthcheck em nenhum serviço

Sem isso, `condition: service_healthy` nem é possível.

### 10. Uma rede só

Banco e cache na mesma rede de quem fala com o mundo.

## Parte A — versão corrigida

```yaml
services:
  api:
    build:
      context: .
      target: runtime
    image: blog-api:1.0.0
    ports:
      - "127.0.0.1:8000:8000"
    environment:
      DATABASE_URL_FILE: /run/secrets/database_url
      SECRET_KEY_FILE: /run/secrets/secret_key
    secrets:
      - database_url
      - secret_key
    depends_on:
      db:
        condition: service_healthy
    networks: [interna]
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "python", "/app/healthcheck.py"]
      interval: 30s
      timeout: 5s
      start_period: 10s
      retries: 3

  db:
    image: postgres:17-alpine
    environment:
      POSTGRES_USER: bloguser
      POSTGRES_DB: blog
      POSTGRES_PASSWORD_FILE: /run/secrets/db_password
    secrets:
      - db_password
    volumes:
      - pgdata:/var/lib/postgresql/data
    networks: [interna]
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U bloguser -d blog"]
      interval: 10s
      timeout: 3s
      retries: 5
      start_period: 10s

networks:
  interna:
    internal: true

volumes:
  pgdata:

secrets:
  database_url:
    file: ./secrets/database_url.txt
  secret_key:
    file: ./secrets/secret_key.txt
  db_password:
    file: ./secrets/db_password.txt
```

> Atenção a um detalhe: com `internal: true`, a `api` não consegue acessar a
> internet. Se ela precisar (webhook, API externa), adicione uma segunda rede
> não-interna a ela — como no [compose do FlixARD](../08-projeto-aplicado/compose-flixard.md).

## Parte B — solução

```yaml
services:

  api:
    build:
      context: .
      target: runtime
    image: blog-api:1.0.0
    ports:
      - "127.0.0.1:8000:8000"
    environment:
      APP_ENV: production
      DATABASE_URL_FILE: /run/secrets/database_url
      REDIS_URL: redis://cache:6379/0
    secrets:
      - database_url
    depends_on:
      db:
        condition: service_healthy
      cache:
        condition: service_healthy
    networks: [interna]
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "python", "/app/healthcheck.py"]
      interval: 30s
      timeout: 5s
      start_period: 15s
      retries: 3

  db:
    image: postgres:17-alpine
    environment:
      POSTGRES_USER: bloguser
      POSTGRES_DB: blog
      POSTGRES_PASSWORD_FILE: /run/secrets/db_password
    secrets:
      - db_password
    volumes:
      - pgdata:/var/lib/postgresql/data
    networks: [interna]
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U bloguser -d blog"]
      interval: 10s
      timeout: 3s
      retries: 5
      start_period: 10s

  cache:
    image: redis:7-alpine
    # Sem persistência: é cache, pode perder. Sem --save "", o Redis
    # grava dump.rdb e passa a exigir disco e cuidado que não queremos.
    command: ["redis-server", "--save", "", "--appendonly", "no", "--maxmemory", "256mb", "--maxmemory-policy", "allkeys-lru"]
    networks: [interna]
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5

networks:
  interna:
    internal: true

volumes:
  pgdata:

secrets:
  database_url:
    file: ./secrets/database_url.txt
  db_password:
    file: ./secrets/db_password.txt
```

### Decisões que valem comentário

**`maxmemory` + `allkeys-lru` no Redis.** Sem limite, o cache cresce até
consumir a RAM da máquina e o OOM killer entra em ação — matando, com boa
probabilidade, o Postgres. Com `allkeys-lru`, ao atingir 256 MB o Redis descarta
as chaves menos usadas. É o comportamento que se espera de um cache, mas **não** é
o padrão.

**Dois `depends_on` com `condition`.** Ambos precisam estar prontos. O Compose
espera os dois em paralelo, não em série.

**`127.0.0.1:8000:8000`.** Só o host alcança. O acesso externo passa por proxy
reverso com TLS.

### Validação

```bash
mkdir -p secrets
printf 'senha-forte-aqui' > secrets/db_password.txt
printf 'postgresql+asyncpg://bloguser:senha-forte-aqui@db:5432/blog' > secrets/database_url.txt
chmod 600 secrets/*.txt

docker compose config --quiet && echo "válido"
```

Use `printf`, não `echo`: o `echo` acrescenta `\n` ao arquivo, e a senha com
quebra de linha falha a autenticação com uma mensagem que não ajuda.

Confira o resultado resolvido antes de subir:

```bash
docker compose config | head -40
```

---
[← variáveis](variaveis-de-ambiente.md) · [módulo 04: armazenamento →](../04-armazenamento/bind-mount-vs-volume.md) · [índice](../00-indice.md)
