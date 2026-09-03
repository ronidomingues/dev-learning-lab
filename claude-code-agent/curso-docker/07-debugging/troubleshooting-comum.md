# Troubleshooting: catálogo de erros reais

> **Nível:** todos
> **Última verificação:** 18/08/2026

Catálogo consultável, organizado pela **mensagem literal** que aparece no
terminal. Use `Ctrl+F`.

---

## Instalação e daemon

### `Cannot connect to the Docker daemon at unix:///var/run/docker.sock`

Ou: `permission denied while trying to connect to the Docker API`.

**Causa.** O daemon não está rodando, **ou** seu usuário não tem permissão no
socket. Note que o CLI estar instalado não significa nada — ele é só um cliente.

**Diagnóstico:**

```bash
systemctl is-active docker            # o daemon está no ar?
ls -la /var/run/docker.sock           # srw-rw---- root docker
id                                    # você está no grupo docker?
getent group docker                   # quem está no grupo
```

Este erro apareceu na máquina onde este curso foi escrito. O diagnóstico real:

```
srw-rw---- 1 root docker 0 /var/run/docker.sock
docker:x:141:                          ← grupo vazio
uid=1002(ronivaldo) grupos=...,27(sudo)  ← usuário fora do grupo
```

**Correção:**

```bash
sudo systemctl start docker            # se estiver parado
sudo usermod -aG docker $USER          # adicionar ao grupo
newgrp docker                          # aplicar na sessão atual
# ou faça logout/login
```

**Atenção:** estar no grupo `docker` **equivale a ser root** na máquina — você
pode montar `/` num container. É uma decisão de segurança, não uma formalidade.
A alternativa é rootless mode ou Podman.

### `docker: unknown command: docker compose`

**Causa.** O plugin do Compose v2 não está instalado. O binário v1
(`docker-compose`, com hífen) chegou ao fim de vida em julho/2023.

**Correção sem sudo** (foi o caminho usado neste curso):

```bash
mkdir -p ~/.docker/cli-plugins
curl -fsSL -o ~/.docker/cli-plugins/docker-compose \
  https://github.com/docker/compose/releases/latest/download/docker-compose-linux-x86_64
chmod +x ~/.docker/cli-plugins/docker-compose
docker compose version
# Docker Compose version v5.5.0
```

Com sudo: `sudo apt install docker-compose-plugin`.

---

## Build

### `failed to solve: failed to compute cache key: "/requirements.txt" not found`

**Causa.** O arquivo está fora do **build context**, ou barrado pelo
`.dockerignore`.

```bash
docker build .        # o "." é o context — o COPY só enxerga daqui para baixo
```

`COPY ../arquivo` **nunca** funciona: não se pode sair do context.

**Correção.** Ajuste o context, ou mova o arquivo:

```yaml
build:
  context: ..              # sobe um nível
  dockerfile: docker/Dockerfile
```

### `Version '12.9' for 'build-essential' was not found`

**Causa.** Pino de versão de pacote apt que não existe na suite da imagem base.

Caso real deste curso: `python:3.12-slim` migrou de Debian bookworm
(`build-essential` 12.9) para trixie (12.12) sem mudar de nome de tag. Confirmado
por digest:

```
python:3.12-slim        -> sha256:2c941e86...
python:3.12-slim-trixie -> sha256:2c941e86...   ← idêntico
```

**Correção.** Fixe a suite (`python:3.12-slim-trixie`) e evite pinar versão de
pacote apt em estágio de build — o Debian remove o `.deb` antigo do mirror ao
publicar correção de segurança, e o pino passa a falhar com 404.

### `E: Unable to locate package X` / `404 Not Found` no apt

**Causa.** `apt-get update` numa camada separada, cacheada há semanas.

```dockerfile
# ❌ o texto do update nunca muda -> camada cacheada indefinidamente
RUN apt-get update
RUN apt-get install -y curl
```

**Correção:**

```dockerfile
RUN apt-get update \
    && apt-get install --no-install-recommends -y curl \
    && rm -rf /var/lib/apt/lists/*
```

### `error: command 'gcc' failed: No such file or directory`

**Causa.** Pacote Python com extensão em C (`asyncpg`, `psycopg2`, `numpy`) sem
wheel pré-compilada para a plataforma, e sem compilador na imagem.

**Correção.** Instale `build-essential` **no estágio builder** de um multi-stage,
ou use a variante binária (`psycopg2-binary`). Note que Alpine agrava isso: quase
nada tem wheel para musl, então tudo compila do zero.

### Build lentíssimo, reinstala tudo a cada mudança

**Causa.** `COPY . .` antes do `pip install`.

**Correção.** Manifesto sozinho e antes do código. Ver
[cache de camadas](../02-dockerfile/cache-de-camadas.md).

---

## Execução

### Container sobe e morre imediatamente, sem erro

**Causa.** O container vive enquanto o **PID 1** viver. Se o processo principal
termina — ou roda em background — o container termina junto.

```dockerfile
CMD ["nginx"]                      # ❌ nginx daemoniza e o PID 1 sai
CMD ["nginx", "-g", "daemon off;"] # ✅ fica em foreground
```

**Diagnóstico:** `docker compose logs <svc>` e `docker ps -a` (exit code).

### `exec /app/entrada.sh: no such file or directory` (mas o arquivo existe!)

Duas causas, ambas enganosas:

**1. Terminação de linha CRLF.** Arquivo salvo no Windows. O shebang vira
`#!/bin/sh\r`, e o `\r` faz parte do nome do interpretador procurado.

```bash
file entrada.sh          # "with CRLF line terminators"
dos2unix entrada.sh
# ou no git: adicione .gitattributes com  *.sh text eol=lf
```

**2. Binário dinâmico em imagem sem libc** (`scratch`, distroless). O "arquivo não
encontrado" é o **linker dinâmico**, não o binário.

```bash
CGO_ENABLED=0 go build ...   # binário estático
```

### `exec format error`

**Causa.** Arquitetura errada — imagem `amd64` num ARM (Raspberry Pi), ou o
contrário.

```bash
docker inspect <imagem> --format '{{.Architecture}}'
uname -m
```

**Correção:**

```bash
docker buildx build --platform linux/amd64,linux/arm64 -t app:1.0 --push .
```

### `Exit code 137`

**Causa.** SIGKILL — quase sempre o OOM killer.

```bash
docker inspect <container> --format '{{.State.OOMKilled}}'   # true
docker stats --no-stream
```

**Correção.** Aumentar o limite, ou corrigir o vazamento de memória. E **sempre**
definir limites: sem eles, o kernel escolhe a vítima pelo score e frequentemente
mata o banco, não o culpado.

### `Permission denied` ao escrever em volume

**Causa.** UID do processo no container ≠ dono do diretório no host.

```bash
docker compose exec api id            # uid=10001
ls -ln ./dados                        # dono 1000
```

**Correção:** `sudo chown -R 10001:10001 ./dados`, ou `user:` no compose em dev.
Ver [usuário não-root](../06-seguranca/usuario-nao-root.md).

### `docker stop` demora 10 segundos

**Causa.** `CMD` em forma shell. O PID 1 vira `/bin/sh`, que não repassa
`SIGTERM`. O Docker espera o timeout e manda `SIGKILL`.

**Correção.** Forma exec (array JSON), ou `exec "$@"` no entrypoint.

---

## Rede

### `could not translate host name "db" to address` / `bad address 'db'`

**Causa.** Serviços em redes diferentes, ou uso da bridge padrão (que **não** tem
DNS por nome).

```bash
docker network inspect <projeto>_default    # quem está conectado?
docker compose exec api getent hosts db
```

**Correção.** Mesma rede; usar o **nome do serviço**. Ver
[DNS interno](../05-redes/dns-interno-entre-servicos.md).

### `connection refused` — o nome resolve, a porta não responde

Três causas, em ordem de frequência:

**1. Aplicação escutando em `127.0.0.1` dentro do container.**

```bash
uvicorn app.main:app --host 0.0.0.0    # não 127.0.0.1
```

**2. Porta errada** — usou a porta do **host** em vez da interna.

```yaml
ports: ["5433:5432"]
# entre containers, use 5432
```

**3. O serviço ainda não subiu.** `depends_on` sem `condition: service_healthy`.

### `port is already allocated`

```bash
docker ps --format 'table {{.Names}}\t{{.Ports}}'
sudo ss -tlnp | grep 8000
```

Pode ser também soma de listas no merge de `compose.override.yaml` —
`docker compose config` mostra o resultado final.

### Porta acessível da LAN mesmo com `ufw deny`

**Causa.** As regras de iptables do Docker são avaliadas **antes** das do UFW.

**Correção.** `ports: ["127.0.0.1:8000:8000"]`, ou não publicar.

---

## Compose

### `services.api additional properties 'imagem' not allowed`

Erro de digitação na chave. O `docker compose config` aponta a linha:

```bash
docker compose config --quiet     # valida SEM precisar de daemon
```

### API morre no `up` com `connection refused` no banco

**Causa.** `depends_on` sem `condition`. Espera o container **iniciar**, não
ficar **pronto**.

```yaml
depends_on:
  db:
    condition: service_healthy    # e o db precisa ter healthcheck
```

Funciona na sua máquina (tudo em cache, rápido) e falha no servidor.

### Mudei o `.env` e nada mudou

Variáveis são lidas na **criação** do container.

```bash
docker compose up -d --force-recreate
```

### Valor errado sem explicação

Variável exportada no shell **sobrepõe** o `.env` (verificado empiricamente —
ver [variáveis de ambiente](../03-compose/variaveis-de-ambiente.md)).

```bash
env | grep NOME_DA_VARIAVEL
```

### Dados sumiram

`docker compose down -v` apaga volumes. Ou o **nome do projeto** mudou (por
renomear a pasta), e o compose criou volumes novos:

```bash
docker volume ls          # os dados antigos podem estar em projeto-antigo_pgdata
```

Prevenção: `name: meu-projeto` no topo do compose.

---

## Healthcheck

### Container `unhealthy` mas a aplicação responde

**Primeiro passo — leia a saída do check, não adivinhe:**

```bash
docker inspect <container> --format '{{json .State.Health}}' | python3 -m json.tool
```

Causas comuns:

| Causa | Correção |
|---|---|
| `curl` não existe na imagem `slim`/`alpine` | usar Python/wget, ou instalar curl |
| Sem `--start-period`, app demora a subir | `--start-period=15s` |
| Healthcheck usa `localhost` e o app escuta em `0.0.0.0` | usar `127.0.0.1` (funciona nos dois casos) |
| **`HTTP_PROXY` no ambiente** | cliente que ignora proxy explicitamente |

O último é o caso real deste curso: `curl` respondia 200 e o healthcheck em
Python falhava com **502**, porque o `no_proxy` tinha espaço depois da vírgula
(`localhost, 127.0.0.0/8`) e o `urllib` não faz o match. Correção:

```python
opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
```

**Regra geral:** 502 vindo de um serviço local é impossível — 502 é resposta de
proxy. Se você vê isso, há um intermediário no caminho.

---

## Disco

### `no space left on device`

```bash
docker system df                  # onde está o espaço
docker system df -v               # detalhe por item
```

Em ordem de segurança para limpar:

```bash
docker builder prune              # cache de build — seguro, costuma ser o maior
docker image prune                # imagens sem tag
docker container prune            # containers parados
docker volume ls -f dangling=true # LISTE antes
docker volume prune               # ⚠️ pode apagar dados seus
```

**Nunca** rode `docker system prune -a --volumes` sem olhar a lista antes.

Prevenção: limite de log em todos os serviços.

```yaml
logging:
  driver: json-file
  options: {max-size: "10m", max-file: "3"}
```

---

## Método geral

Quando nada acima se aplica:

1. **Leia a mensagem inteira**, não a primeira linha. A causa costuma estar no
   fim do traceback.
2. **Isole a camada**: o problema é do build, do runtime, da rede ou da
   aplicação? Um `curl` de dentro do container separa rede de aplicação em um
   comando.
3. **Compare com o que funciona.** Duas ferramentas discordando sobre o mesmo
   endereço apontam para o **cliente**, não o servidor.
4. **Reduza ao mínimo.** `docker run --rm -it <base> sh` e refaça os passos na
   mão até quebrar.
5. **Verifique o óbvio por último, mas verifique**: nome do serviço, porta
   interna, arquivo no context, variável exportada no shell.

## Autoteste

1. `Cannot connect to the Docker daemon`: duas causas possíveis?
2. Container sobe e morre sem erro. Qual é a explicação estrutural?
3. `exec ...: no such file or directory` num arquivo que existe: duas causas.
4. Exit 137: o que é e como confirmar?
5. Nome resolve mas dá `connection refused`: três causas, em ordem.
6. Por que `ufw deny` pode não proteger?
7. Qual comando mostra **por que** um healthcheck falha?
8. Qual é a limpeza de disco mais segura, e qual exige cuidado?

---
[← logs e exec](logs-e-exec.md) · [módulo 08: projeto aplicado →](../08-projeto-aplicado/dockerfile-fastapi-sqlalchemy.md) · [índice](../00-indice.md)
