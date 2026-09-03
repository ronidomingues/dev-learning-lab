# Usuário não-root: por que o padrão do Docker é perigoso

> **Nível:** intermediário
> **Última verificação:** 18/08/2026

## 1. O padrão é root

```bash
docker run --rm python:3.12-slim id
# uid=0(root) gid=0(root) groups=0(root)
```

Sem `USER` no Dockerfile, seu processo é **root dentro do container**. E o root
do container é, por padrão, o **mesmo UID 0 do host** — os namespaces isolam a
visão, não a identidade numérica.

## 2. Por que isso importa (a cadeia completa)

A objeção comum é: "mas o container é isolado, root nele não é root no host".
Parcialmente verdade, e a parte falsa é a que machuca.

**Cenário 1 — escalada dentro do container.** Sua API tem uma falha de path
traversal. Como root, o atacante lê `/etc/shadow`, instala pacotes, escreve
binários. Como UID 10001, ele não consegue nem escrever fora de `/tmp`.

**Cenário 2 — volume montado.** Este é o mais concreto:

```yaml
volumes:
  - /srv/flixard/midia:/midia
```

O processo é root no container = **UID 0 no host**. Se ele escrever em `/midia`,
escreve como UID 0 no `/srv/flixard/midia` do host. Um `rm -rf` acidental
apaga sua coleção, e nenhuma permissão do host impede — porque UID 0 ignora
permissão.

**Cenário 3 — escape.** Falhas de escape de container são raras, mas existem
(CVE-2019-5736 no runc, CVE-2022-0492 em cgroups v1). Todas exigiam **root no
container** para serem exploradas. Rodar como não-root neutralizou cada uma
delas antes de existir patch.

A lógica é de defesa em profundidade: você não confia que nenhuma camada vai
falhar; você garante que uma falha isolada não seja suficiente.

## 3. Como fazer

### Debian/Ubuntu

```dockerfile
RUN groupadd --system --gid 10001 appgroup \
    && useradd --system --uid 10001 --gid appgroup --no-create-home appuser
```

### Alpine

```dockerfile
RUN addgroup -S -g 10001 appgroup \
    && adduser -S -u 10001 -G appgroup -H appuser
```

As flags:

| Flag | O que faz | Por quê |
|---|---|---|
| `--system` / `-S` | conta de serviço | sem senha, sem shell de login, fora da faixa de UID humana |
| `--uid 10001` | UID fixo | permissões de volume previsíveis entre máquinas |
| `--no-create-home` / `-H` | sem `/home` | a aplicação não precisa |

### Onde colocar o `USER`

**Depois** de tudo que precisa de root, **antes** do `CMD`:

```dockerfile
FROM python:3.12-slim-trixie

# 1) tudo que precisa de root
RUN apt-get update && apt-get install -y libpq5 && rm -rf /var/lib/apt/lists/*
RUN groupadd --system --gid 10001 appgroup \
    && useradd --system --uid 10001 --gid appgroup --no-create-home appuser

WORKDIR /app

# 2) copiar já com o dono certo
COPY --chown=appuser:appgroup app/ ./app/

# 3) diretórios que a app escreve
RUN mkdir -p /app/data && chown appuser:appgroup /app/data

# 4) descer de privilégio
USER 10001:10001

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0"]
```

### Por que numérico

```dockerfile
USER 10001:10001      # ✅
USER appuser          # ⚠️ funciona, mas...
```

O `hadolint` cobra isso na regra **DL3066** — e cobrou durante a escrita deste
curso:

```
Dockerfile:79 DL3066 info: Non-numeric user-id may not be resolvable by host system
```

O motivo: orquestradores como o Kubernetes precisam avaliar a política
`runAsNonRoot` **sem** abrir a imagem para ler o `/etc/passwd`. Com um nome, não
há como provar que o usuário não é UID 0, e o pod é recusado.

## 4. O problema das permissões

O sintoma mais comum depois de adicionar `USER`:

```
PermissionError: [Errno 13] Permission denied: '/app/data/app.db'
```

Causa: o `COPY` sem `--chown` cria arquivos pertencentes a root; o processo é
10001 e não pode escrever.

**A regra:** todo diretório onde a aplicação **escreve** precisa pertencer a ela,
e o `chown` tem que acontecer **antes** do `USER`.

```dockerfile
RUN mkdir -p /app/data /app/logs \
    && chown -R appuser:appgroup /app/data /app/logs
USER 10001:10001
```

Prefira `COPY --chown=` a um `RUN chown -R` posterior: o `RUN chown` cria uma
camada nova contendo **cópia de todos os arquivos alterados**, potencialmente
dobrando o tamanho da imagem.

### Volumes

Volume nomeado montado num diretório que **existe na imagem** herda o dono
daquele diretório:

```dockerfile
RUN mkdir -p /app/data && chown appuser:appgroup /app/data
```
```yaml
volumes:
  - dados:/app/data     # o volume nasce com dono appuser
```

Bind mount **não** herda nada: o dono é o do host. Aí é preciso alinhar:

```bash
sudo chown -R 10001:10001 ./dados
```

Ou, em desenvolvimento, rodar o container com o seu próprio UID:

```yaml
services:
  api:
    user: "${UID:-1000}:${GID:-1000}"
```
```bash
UID=$(id -u) GID=$(id -g) docker compose up
```

Assim os arquivos que o container criar pertencem a você — o que evita o
irritante "não consigo apagar o que o Docker criou".

## 5. Portas abaixo de 1024

Processo não-root não consegue abrir porta < 1024. Se sua aplicação escuta na 80:

```
PermissionError: [Errno 13] Permission denied: bind 0.0.0.0:80
```

Três soluções, em ordem de preferência:

```yaml
# 1) MELHOR: aplicação em porta alta, mapeamento resolve o resto
ports:
  - "80:8000"          # host 80 -> container 8000
```

```dockerfile
# 2) Conceder só a capability necessária
# compose: cap_add: [NET_BIND_SERVICE]
```

```yaml
# 3) Reduzir o limite do kernel (evite)
sysctls:
  net.ipv4.ip_unprivileged_port_start: 0
```

Use a 1. A restrição de porta baixa existe desde os anos 80 para impedir que
usuário comum suba um serviço se passando por daemon do sistema; num container,
o mapeamento de porta torna a restrição irrelevante — não há motivo para
contorná-la.

## 6. Imagens oficiais que já são não-root

| Imagem | Usuário padrão | Observação |
|---|---|---|
| `postgres` | `postgres` (999) | o entrypoint começa como root e desce sozinho |
| `redis` | `redis` (999) | idem |
| `nginx` | **root** | o master é root, os workers descem para `nginx` |
| `node` | `node` (1000) disponível, mas **não ativo** | precisa de `USER node` explícito |
| `python` | **root** | precisa criar o usuário |

Sempre confira:

```bash
docker run --rm <imagem> id
```

O caso do nginx merece nota: o processo master **precisa** de root para abrir a
porta 80 e ler certificados; ele desce os workers para `nginx` sozinho. Para um
nginx totalmente não-root, existe a variante `nginxinc/nginx-unprivileged`.

## 7. Rootless Docker — o degrau seguinte

Tudo acima trata do usuário **dentro** do container. Mas o **daemon** ainda roda
como root no host, e estar no grupo `docker` equivale a ser root (você pode
montar `/` num container).

O **rootless mode** roda o daemon inteiro como usuário comum:

```bash
dockerd-rootless-setuptool.sh install
export DOCKER_HOST=unix:///run/user/$(id -u)/docker.sock
```

| | Docker normal | Rootless |
|---|---|---|
| Daemon | root | seu usuário |
| Grupo `docker` = root | sim | não se aplica |
| Portas < 1024 | sim | não (sem configuração extra) |
| Desempenho de rede | nativo | um pouco menor (slirp4netns) |
| `--network host` | funciona | limitado |

**Recomendação:** para homelab pessoal, o Docker normal com containers não-root
é um bom equilíbrio. Rootless faz sentido em máquina compartilhada ou se o
requisito de segurança for alto. Podman é rootless por desenho e vale
considerar, se você estiver começando do zero.

## 8. Erros que você provavelmente vai cometer

| Mensagem | Causa raiz | Correção |
|---|---|---|
| `Permission denied` ao escrever | diretório pertence a root | `chown` **antes** do `USER` |
| `Permission denied` bind 0.0.0.0:80 | porta < 1024 sem privilégio | app em porta alta, mapear com `ports:` |
| Funcionou local, quebrou com volume | bind mount não herda dono | `chown` no host, ou `user:` no compose |
| `useradd: command not found` | Alpine usa `adduser` | sintaxe do BusyBox |
| Kubernetes recusa o pod (`runAsNonRoot`) | `USER` com nome, não número | `USER 10001:10001` |
| `apt-get` falha depois do `USER` | apt precisa de root | mover instalações para antes do `USER` |
| Arquivos criados pelo container que você não consegue apagar | container rodou como root em bind mount | `user:` com seu UID em dev |

## 9. Autoteste

1. Por que root no container é perigoso mesmo com namespaces?
2. Descreva o cenário do volume montado, concretamente.
3. Por que `USER 10001:10001` e não `USER appuser`?
4. Onde exatamente colocar o `USER` no Dockerfile, e por quê?
5. A app não consegue abrir a porta 80. Três soluções, em ordem.
6. Por que `COPY --chown=` é melhor que `RUN chown -R`?
7. Volume nomeado herda dono? E bind mount?
8. O que o rootless mode resolve que o `USER` não resolve?

---
[secrets →](secrets-e-variaveis-sensiveis.md) · [índice](../00-indice.md)
