# Anatomia do Compose: services, volumes, networks, depends_on

> **Nível:** iniciante → intermediário
> **Última verificação:** 18/08/2026 (Docker Compose v5.5.0)

## 1. O problema

Sua aplicação precisa de API, banco e cache. Sem Compose:

```bash
docker network create minha-rede
docker volume create pgdata
docker run -d --name db --network minha-rede -v pgdata:/var/lib/postgresql/data \
  -e POSTGRES_PASSWORD=x postgres:17-alpine
docker run -d --name redis --network minha-rede redis:7-alpine
docker run -d --name api --network minha-rede -p 8000:8000 \
  -e DATABASE_URL=... minha-api:1.0
```

Seis comandos, na ordem certa, digitados de novo a cada máquina. Ninguém
lembra. Alguém esquece o `--network` e passa a tarde depurando DNS.

O Compose transforma isso num arquivo versionado no git:

```bash
docker compose up -d
```

**Compose é para uma máquina.** Para várias, é Swarm ou Kubernetes
([módulo 09](../09-proximos-passos.md)).

## 2. Notas de versão que evitam confusão

| Assunto | Situação em 18/08/2026 |
|---|---|
| `docker-compose` (v1, Python) | fim de vida em julho/2023. Não use |
| `docker compose` (v2, plugin Go) | é o atual |
| `version: "3.8"` no topo | **descontinuado**; remova a chave |
| `compose.yaml` | nome oficial preferido |
| `docker-compose.yml` | ainda funciona, nome legado |

Se um tutorial começa com `version: '3'`, ele é anterior a 2023. Desconfie do
resto.

## 3. Estrutura

```yaml
services:      # os containers
volumes:       # armazenamento nomeado
networks:      # redes
secrets:       # segredos em arquivo
configs:       # configuração não-sensível
```

Só `services` é obrigatório.

## 4. `services` — o essencial

```yaml
services:
  api:
    # --- de onde vem a imagem: build OU image ---
    build:
      context: .              # diretório do build
      dockerfile: Dockerfile
      target: runtime         # estágio do multi-stage
      args:
        APP_VERSION: "1.0.0"  # vira --build-arg
    image: minha-api:1.0.0    # com build: nome dado à imagem construída
                              # sem build: imagem baixada do registry

    # --- rede ---
    ports:
      - "8000:8000"           # host:container — acessível de toda a LAN
      - "127.0.0.1:9000:9000" # só do próprio host
    expose:
      - "8001"                # só para outros containers, sem publicar

    # --- configuração ---
    environment:
      APP_ENV: production     # valor literal
      DATABASE_URL: ${DB_URL} # do .env ou do ambiente do shell
    env_file:
      - .env                  # carrega arquivo inteiro

    # --- armazenamento ---
    volumes:
      - dados:/app/dados      # volume nomeado
      - ./config:/app/config:ro  # bind mount somente-leitura

    # --- ordem e saúde ---
    depends_on:
      db:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "python", "/app/healthcheck.py"]
      interval: 30s
      timeout: 5s
      start_period: 10s
      retries: 3

    # --- ciclo de vida ---
    restart: unless-stopped
    stop_grace_period: 30s    # tempo entre SIGTERM e SIGKILL

    # --- sobrescritas ---
    command: ["uvicorn", "app.main:app"]   # substitui o CMD
    entrypoint: ["/entrada.sh"]            # substitui o ENTRYPOINT
    user: "10001:10001"
    working_dir: /app
```

### `restart`: as quatro políticas

| Valor | Comportamento |
|---|---|
| `no` (padrão) | nunca reinicia |
| `on-failure` | reinicia se sair com código ≠ 0 |
| `always` | sempre reinicia, **inclusive** após reboot do host |
| `unless-stopped` | igual a `always`, mas respeita uma parada manual sua |

**Use `unless-stopped`.** A diferença para `always` aparece no pior momento:
você para um serviço para manutenção, a máquina reinicia, e com `always` ele
volta sozinho.

## 5. `depends_on` — a armadilha nº 1 do Compose

```yaml
# ❌ Espera o container INICIAR, não ficar PRONTO
depends_on:
  - db

# ✅ Espera o healthcheck passar
depends_on:
  db:
    condition: service_healthy
```

Com a forma curta, o Compose sobe o `db` e imediatamente sobe a `api`. O
Postgres leva ~3 s para aceitar conexão. A API tenta conectar em ~0,5 s, falha
com `connection refused` e morre.

Pior: **funciona na sua máquina** (imagens em cache, tudo rápido) e falha no
servidor. Bug clássico de "só quebra em produção".

As três condições:

| Condição | Significa |
|---|---|
| `service_started` | o container iniciou (padrão da forma curta) |
| `service_healthy` | o healthcheck passou |
| `service_completed_successfully` | terminou com código 0 — para jobs de migration |

E a verdade incômoda: **mesmo com `service_healthy`, sua aplicação deve
reconectar sozinha.** O banco pode reiniciar depois que a API já subiu. O
`depends_on` resolve a partida, não a vida inteira. Por isso o projeto modelo
usa `pool_pre_ping=True`.

## 6. `networks`

Por padrão o Compose cria uma rede e coloca todos os serviços nela. Todos
enxergam todos — o que nem sempre você quer.

```yaml
services:
  proxy:
    networks: [borda, interna]
  api:
    networks: [interna]
  db:
    networks: [interna]      # inalcançável a partir da borda

networks:
  borda:
  interna:
    internal: true           # sem rota para a internet
```

Dentro de uma rede, serviços se acham pelo **nome do serviço**:
`postgresql://user:pass@db:5432/app`. Detalhes em
[DNS interno](../05-redes/dns-interno-entre-servicos.md).

## 7. `volumes`

```yaml
services:
  db:
    volumes:
      - pgdata:/var/lib/postgresql/data   # nomeado: gerenciado pelo Docker
      - ./backup:/backup                  # bind mount: caminho do host
      - ./config.yaml:/app/config.yaml:ro # arquivo único, read-only

volumes:
  pgdata:                                 # precisa ser declarado aqui
```

`docker compose down` preserva volumes nomeados. `docker compose down -v`
**apaga**. Comparação completa no
[módulo 04](../04-armazenamento/bind-mount-vs-volume.md).

## 8. Múltiplos arquivos: dev e produção sem duplicar

O Compose lê `compose.yaml` + `compose.override.yaml` **automaticamente** e
mescla os dois.

```yaml
# compose.yaml — comum a todos os ambientes
services:
  api:
    build: .
    environment:
      APP_ENV: production
```

```yaml
# compose.override.yaml — só desenvolvimento (lido automaticamente)
services:
  api:
    volumes:
      - ./app:/app/app:ro
    command: ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--reload"]
    environment:
      APP_ENV: development
```

```bash
docker compose up                      # base + override (dev)
docker compose -f compose.yaml up      # só a base (produção)
```

**Verificação executada** (este mecanismo foi testado de verdade):

```bash
docker compose config --quiet                  # base + override -> válido
docker compose -f compose.yaml config --quiet  # só base          -> válido
docker compose config                          # mostra o merge resolvido
```

O `config` resolvido confirmou que o `command` veio do override e o
`healthcheck` veio da base — exatamente o comportamento esperado do merge.

### Regras do merge

| Tipo | Comportamento |
|---|---|
| escalar (`image`, `command`) | o override **substitui** |
| lista (`ports`, `volumes`) | os itens são **somados** |
| mapa (`environment`, `labels`) | mesclado chave a chave |

Listas somarem é a fonte de surpresa: definir `ports` nos dois arquivos não
substitui — resulta em duas publicações e, às vezes, `port is already allocated`.

## 9. Comandos do dia a dia

```bash
docker compose up -d              # subir em background
docker compose up --build         # rebuildar antes
docker compose down               # derrubar (mantém volumes)
docker compose down -v            # derrubar E APAGAR volumes

docker compose ps                 # status, inclusive (healthy)
docker compose logs -f api        # acompanhar um serviço
docker compose logs --tail=100    # últimas linhas de todos

docker compose exec api sh        # shell num container RODANDO
docker compose run --rm api pytest # container NOVO e efêmero

docker compose config             # ver o YAML final resolvido
docker compose config --quiet     # só validar (não precisa de daemon!)

docker compose restart api
docker compose pull               # atualizar imagens
docker compose up -d --force-recreate api
```

Dois merecem destaque:

**`docker compose config --quiet`** valida sintaxe **sem daemon nenhum**. Foi
como todos os composes deste curso foram verificados. Ponha no seu CI.

**`exec` vs `run`:** `exec` entra num container já em execução; `run` cria um
container novo e descartável. Para rodar testes, `run --rm` é o certo.

## 10. Erros que você provavelmente vai cometer

| Mensagem | Causa raiz | Correção |
|---|---|---|
| `services.api additional properties 'imagem' not allowed` | erro de digitação na chave | `docker compose config` aponta a linha |
| API morre com `connection refused` ao subir | `depends_on` sem `condition` | `condition: service_healthy` |
| `port is already allocated` | porta ocupada, ou somada pelo merge do override | `docker compose ps`; conferir `docker compose config` |
| Mudei o `.env` e nada aconteceu | variáveis são lidas na criação do container | `docker compose up -d --force-recreate` |
| `network not found` após editar redes | rede antiga órfã | `docker compose down && docker compose up -d` |
| Dados sumiram | rodou `down -v` | não há volta sem backup — atenção ao `-v` |
| `service "db" is not running` no `exec` | container parado ou em restart loop | `docker compose ps` e `logs db` |

## 11. Autoteste

1. Por que `version:` não deve mais aparecer no compose?
2. Diferença entre `depends_on: [db]` e `condition: service_healthy`.
3. Por que `service_healthy` ainda não dispensa reconexão na aplicação?
4. `unless-stopped` vs `always`: quando a diferença aparece?
5. O que acontece com `ports` definido na base **e** no override?
6. Diferença entre `exec` e `run --rm`.
7. Como validar um compose sem ter daemon rodando?
8. O que `down -v` faz de diferente do `down`?

---
[variáveis de ambiente →](variaveis-de-ambiente.md) · [índice](../00-indice.md)
