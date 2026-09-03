# Diretivas do Dockerfile — referência completa

> **Nível:** iniciante → intermediário
> **Última verificação:** 18/08/2026

Referência organizada **por tarefa**, não em ordem alfabética. Se você quer
saber "como defino a porta", procure em *Rede*, não em *E*.

## Mapa rápido

| Quero... | Diretiva |
|---|---|
| escolher a base | `FROM` |
| executar algo **durante o build** | `RUN` |
| definir o comando que roda **ao subir** | `CMD`, `ENTRYPOINT` |
| trazer arquivos para a imagem | `COPY`, `ADD` |
| definir o diretório de trabalho | `WORKDIR` |
| variável em tempo de **build** | `ARG` |
| variável em tempo de **execução** | `ENV` |
| trocar o usuário do processo | `USER` |
| declarar porta | `EXPOSE` |
| declarar ponto de montagem | `VOLUME` |
| verificar saúde | `HEALTHCHECK` |
| metadados | `LABEL` |
| sinal de parada | `STOPSIGNAL` |
| diretiva do parser | `# syntax=` |

---

## Base e estrutura

### `FROM`

```dockerfile
FROM python:3.12-slim-trixie
FROM python:3.12-slim-trixie AS builder          # estágio nomeado
FROM python:3.12-slim-trixie@sha256:2c941e86...  # travado por digest
FROM scratch                                     # imagem literalmente vazia
```

Primeira instrução (só `ARG` e `# syntax=` podem vir antes). Vários `FROM` no
mesmo arquivo = multi-stage ([módulo dedicado](multi-stage-build.md)).

`scratch` é a imagem vazia: nada, nem `/bin/sh`. Serve para binários estáticos
(Go, Rust). Sem shell, `RUN` não funciona e não há como fazer `docker exec`.

**Escolha da base — comparação honesta:**

| Base | Tamanho | Quando usar | Cuidado |
|---|---|---|---|
| `python:3.12` | ~1 GB | quase nunca | traz compilador e ferramentas que você não usa |
| `python:3.12-slim` | ~43 MB | **padrão sensato** | tag genérica; migra de suite Debian sem avisar |
| `python:3.12-alpine` | ~18 MB | quando cada MB conta | usa musl no lugar de glibc: wheels binárias não servem, tudo compila do zero — build lento e bugs sutis |
| `distroless` | ~25 MB | produção endurecida | sem shell: nada de `docker exec ... sh` |

**Opinião profissional, não consenso:** para Python, evite Alpine. A economia de
25 MB não paga o preço de builds 5× mais lentos e de bugs de compatibilidade com
musl (DNS e threads têm diferenças reais). Para Go, Alpine é ótimo. Muita gente
discorda; o argumento contrário é que a superfície de ataque menor compensa.

### `WORKDIR`

```dockerfile
WORKDIR /app        # cria se não existir, e faz cd
```

Use sempre em vez de `RUN cd /app` — o `cd` num `RUN` **não persiste** para a
instrução seguinte, porque cada `RUN` é um shell novo. Este é um erro clássico:

```dockerfile
RUN cd /app          # este cd morre aqui
RUN pip install -r requirements.txt   # roda em /, não em /app
```

Aceita caminho relativo, que se acumula (`WORKDIR /a` + `WORKDIR b` = `/a/b`).
Prefira absolutos.

---

## Executar

### `RUN`

```dockerfile
RUN pip install fastapi                        # forma shell (via /bin/sh -c)
RUN ["pip", "install", "fastapi"]              # forma exec (sem shell)
```

Roda **durante o build** e o resultado vira camada.

Encadeie o que é logicamente uma operação, porque cada `RUN` é uma camada:

```dockerfile
# RUIM: 3 camadas, e a lista do apt fica gravada para sempre na 1ª
RUN apt-get update
RUN apt-get install -y curl
RUN rm -rf /var/lib/apt/lists/*

# BOM: 1 camada, e a limpeza tem efeito real no tamanho
RUN apt-get update \
    && apt-get install --no-install-recommends -y curl \
    && rm -rf /var/lib/apt/lists/*
```

A diferença **não** é estética. Na versão ruim, o `rm` acontece numa camada
posterior; a lista de pacotes (~40 MB) continua gravada na primeira. Só encolhe
se a limpeza estiver **na mesma camada** que criou o lixo.

Com BuildKit, o cache de gerenciador de pacotes acelera muito:

```dockerfile
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt
```

O diretório montado **não** vira camada — fica num cache do BuildKit, reusado
entre builds e sem inchar a imagem.

### `CMD` e `ENTRYPOINT` — a distinção que mais confunde

| | `ENTRYPOINT` | `CMD` |
|---|---|---|
| Papel | o executável | os argumentos padrão |
| `docker run img arg` | argumento é **anexado** | é **substituído** por completo |
| Sobrescrever | precisa de `--entrypoint` | basta passar depois da imagem |

Os três padrões que cobrem tudo:

```dockerfile
# 1) Só CMD — flexível. Melhor para aplicações.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0"]
# docker run img                    -> uvicorn ...
# docker run img python -c "1+1"    -> python -c "1+1"  (CMD ignorado)

# 2) Só ENTRYPOINT — a imagem VIRA um comando. Melhor para ferramentas CLI.
ENTRYPOINT ["curl"]
# docker run img https://exemplo.com  -> curl https://exemplo.com

# 3) Os dois — comando fixo com argumento padrão sobrescrevível.
ENTRYPOINT ["uvicorn", "app.main:app"]
CMD ["--host", "0.0.0.0", "--port", "8000"]
# docker run img                  -> uvicorn app.main:app --host 0.0.0.0 --port 8000
# docker run img --port 9000      -> uvicorn app.main:app --port 9000
```

**Forma exec (array JSON) sempre.** Na forma shell o processo vira filho de
`/bin/sh`, que não repassa `SIGTERM`: o `docker stop` é ignorado, o Docker
espera 10 s e mata com `SIGKILL`. Conexões caem no meio e transações não fazem
rollback limpo.

Se você **precisa** de recurso de shell (expandir variável, pipe), chame o shell
explicitamente com `exec`, que substitui o processo em vez de criar filho:

```dockerfile
CMD ["sh", "-c", "exec uvicorn app.main:app --port ${PORT:-8000}"]
```

O padrão mais robusto para inicialização complexa é um `entrypoint.sh` que
termina com `exec "$@"`:

```bash
#!/bin/sh
set -e
python manage.py migrate      # preparação
exec "$@"                     # exec: o CMD VIRA o PID 1, herda os sinais
```

---

## Arquivos

### `COPY` e `ADD`

```dockerfile
COPY requirements.txt .
COPY --chown=10001:10001 app/ ./app/
COPY --from=builder /opt/venv /opt/venv
```

`ADD` faz tudo que o `COPY` faz **e mais**: baixa URL e descompacta tarball
automaticamente. Essa "gentileza" é justamente o problema — comportamento
implícito que surpreende.

**Regra:** use `COPY`. Use `ADD` só para extrair um tarball local, que é o único
caso em que ele ganha de verdade.

```dockerfile
# ADD baixando URL: ruim (sem verificação de integridade, vira camada, não cacheia bem)
ADD https://exemplo.com/app.tar.gz /tmp/

# melhor: explícito, com verificação, e tudo numa camada só
RUN curl -fsSL https://exemplo.com/app.tar.gz -o /tmp/app.tar.gz \
    && echo "abc123...  /tmp/app.tar.gz" | sha256sum -c - \
    && tar -xzf /tmp/app.tar.gz -C /opt \
    && rm /tmp/app.tar.gz
```

`--chown` no `COPY` evita um `RUN chown -R` posterior — que criaria uma camada
nova com **cópia de todos os arquivos**, dobrando o tamanho da imagem.

### `.dockerignore`

Não é diretiva, mas pertence a esta discussão. Fica na raiz do build context e
define o que **não** é enviado ao daemon. Sem ele: build lento, cache
invalidado a cada commit (porque `.git/` muda), e risco de `.env` entrar na
imagem.

---

## Variáveis: `ARG` vs `ENV`

A confusão nº 1 do Dockerfile.

| | `ARG` | `ENV` |
|---|---|---|
| Existe durante | **só o build** | build **e** execução |
| Definido por | `--build-arg` | `-e` / `environment:` |
| Vai para a imagem final? | não | **sim** |
| Aparece em `docker inspect`? | não (mas veja abaixo) | **sim** |
| Serve para segredo? | **não** | **não** |

```dockerfile
ARG PYTHON_VERSION=3.12                  # ARG antes do FROM: só o FROM enxerga
FROM python:${PYTHON_VERSION}-slim-trixie

ARG APP_VERSION=dev                      # precisa ser redeclarado após o FROM
ENV APP_VERSION=${APP_VERSION}           # promove para runtime
```

**Nenhum dos dois serve para segredo.** `ENV` fica gravado na imagem e sai em
`docker inspect`. `ARG` não vai para a imagem final, mas **aparece no
`docker history`** — ou seja, um `--build-arg SENHA=x` é recuperável por quem
tiver a imagem. Para segredo em build, use `RUN --mount=type=secret`.

Duas armadilhas de escopo:

```dockerfile
ARG VERSAO=1.0
FROM alpine
RUN echo $VERSAO      # VAZIO! ARG antes do FROM não atravessa

# correto:
ARG VERSAO=1.0
FROM alpine
ARG VERSAO            # redeclara, herdando o valor
RUN echo $VERSAO      # 1.0
```

---

## Identidade e rede

### `USER`

```dockerfile
RUN groupadd --system --gid 10001 appgroup \
    && useradd --system --uid 10001 --gid appgroup --no-create-home appuser
USER 10001:10001
```

Tudo depois do `USER` roda com aquele usuário — inclusive os `RUN` seguintes.
Se precisar instalar algo depois, volte para `USER root` e desça de novo (mas
prefira reordenar). Detalhes no [módulo 06](../06-seguranca/usuario-nao-root.md).

### `EXPOSE`

```dockerfile
EXPOSE 8000
```

**Não publica porta nenhuma.** É documentação, mais um hook para `docker run -P`
(maiúsculo), que publica todas as portas expostas em portas aleatórias do host.
Quem publica de verdade é `-p` ou `ports:`.

### `VOLUME`

```dockerfile
VOLUME ["/app/dados"]
```

Declara que o caminho deve ser um ponto de montagem. Se o usuário não montar
nada ali, o Docker cria um **volume anônimo** automaticamente.

**Opinião profissional:** evite `VOLUME` no Dockerfile. Volumes anônimos se
acumulam invisíveis (e é uma das causas de disco cheio), e a diretiva impede que
alguém use aquele caminho como camada normal. Declare volumes no `compose.yaml`,
onde quem opera enxerga.

---

## Saúde e metadados

### `HEALTHCHECK`

```dockerfile
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD ["python", "/app/healthcheck.py"]
```

| Opção | Padrão | O que faz |
|---|---|---|
| `--interval` | 30s | espaço entre checagens |
| `--timeout` | 30s | tempo máximo de cada checagem |
| `--start-period` | 0s | período inicial em que a falha **não conta** |
| `--retries` | 3 | falhas seguidas até marcar `unhealthy` |

`--start-period` é o mais importante e o mais esquecido: sem ele, uma aplicação
que leva 8 s para subir é marcada `unhealthy` e reiniciada em loop infinito.

O comando precisa sair com **0 = healthy, 1 = unhealthy**. É só o exit code que
conta; a saída de texto é apenas guardada para `docker inspect`.

`HEALTHCHECK NONE` desliga um healthcheck herdado da imagem base.

### `LABEL` e `STOPSIGNAL`

```dockerfile
LABEL org.opencontainers.image.source="https://github.com/voce/projeto" \
      org.opencontainers.image.version="1.0.0"

STOPSIGNAL SIGTERM
```

Os labels `org.opencontainers.image.*` são padrão OCI — ferramentas de scan e
registries os reconhecem. `org.opencontainers.image.source` é o que faz o
GitHub associar a imagem ao repositório automaticamente.

---

## Obsoleto — não use

| Diretiva | Situação | Substituto |
|---|---|---|
| `MAINTAINER` | descontinuada | `LABEL org.opencontainers.image.authors=` |
| `ADD` para URL | desaconselhada | `RUN curl` com checksum |
| `version:` no compose | descontinuada | remover a chave |
| `docker-compose` (binário v1) | fim de vida em julho/2023 | `docker compose` (plugin v2) |
| `links:` no compose | legado | redes + DNS interno |

---

## Erros que você provavelmente vai cometer

| Mensagem | Causa raiz | Correção |
|---|---|---|
| `RUN cd /app` não teve efeito | cada `RUN` é um shell novo | usar `WORKDIR` |
| variável de `ARG` vazia no `RUN` | `ARG` antes do `FROM` não atravessa | redeclarar depois do `FROM` |
| `docker stop` demora 10 s | `CMD` em forma shell; `sh` não repassa SIGTERM | forma exec, ou `exec "$@"` |
| imagem enorme apesar do `rm` | limpeza em `RUN` separado | encadear na mesma camada |
| `permission denied` após `USER` | arquivos copiados pertencem a root | `COPY --chown=` |
| porta não responde | `EXPOSE` sem `-p` | publicar com `-p` ou `ports:` |

## Autoteste

1. Diferença entre `CMD` e `ENTRYPOINT` quando você roda `docker run img bash`.
2. Por que `RUN cd /app` não funciona como se espera?
3. `ARG` serve para passar senha no build? Justifique.
4. Por que `EXPOSE 8000` sozinho não torna a aplicação acessível?
5. Por que `RUN apt-get update` e `RUN rm -rf /var/lib/apt/lists/*` em
   instruções separadas não reduz a imagem?
6. Quando `ADD` é preferível a `COPY`?
7. O que `--start-period` evita?
8. Por que `COPY --chown=` é melhor que `RUN chown -R`?

---
[cache de camadas →](cache-de-camadas.md) · [índice](../00-indice.md)
