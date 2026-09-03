# 70 · Prática — laboratórios progressivos

`Nível: todos` · `Última atualização: 11/08/2026`

Aprender Docker é como aprender a nadar: não dá para ler o caminho todo. Cada laboratório tem
**objetivo**, **passos**, **critério de aprovação** e o **conceito que ele consolida**.

Ambiente: qualquer um do [03-instalacao.md](03-instalacao.md), inclusive
[Play with Docker](https://labs.play-with-docker.com). Onde um laboratório exige Linux, está
marcado.

---

## Lab 1 — Sobrevivência (30 min)

**Objetivo:** rodar, inspecionar, entrar e limpar. O ciclo básico.

```bash
docker run -d --name web -p 8080:80 nginx:alpine
curl -sI localhost:8080 | head -1
docker ps
docker logs web
docker exec -it web sh -c 'ls /usr/share/nginx/html && hostname'
docker stop web && docker rm web
docker ps -a | grep web || echo "removido"
```

**Critério de aprovação:**
- [ ] `curl` devolveu `HTTP/1.1 200 OK`.
- [ ] Você explicou, em `-p 8080:80`, qual porta é do host.
- [ ] O `hostname` de dentro do container era diferente do da sua máquina.
- [ ] Nenhum container `web` sobrou.

**Consolida:** container é processo; `-p` é `host:container`; `exec` entra no que já roda.

---

## Lab 2 — A primeira imagem sua (45 min)

**Objetivo:** escrever um Dockerfile e construir.

Crie `app.py`:
```python
import http.server, os, socketserver
PORTA = int(os.environ.get("PORT", "8000"))
class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200); self.end_headers()
        self.wfile.write(f"Ola de {socketserver.socket.gethostname()}\n".encode())
    def log_message(self, *a): pass
with socketserver.TCPServer(("0.0.0.0", PORTA), H) as s:
    print(f"ouvindo na {PORTA}", flush=True); s.serve_forever()
```

`Dockerfile`:
```dockerfile
# syntax=docker/dockerfile:1
FROM python:3.13-slim
WORKDIR /app
COPY app.py .
RUN useradd -m app
USER app
EXPOSE 8000
CMD ["python", "app.py"]
```

```bash
docker build -t meu-py:1.0 .
docker run --rm -d --name py -p 8000:8000 meu-py:1.0
curl localhost:8000
docker rm -f py
```

**Critério:**
- [ ] A imagem foi construída sem erro.
- [ ] `curl` devolveu "Ola de ...".
- [ ] `docker image inspect meu-py:1.0 --format '{{.Config.User}}'` mostra `app`, não vazio.
- [ ] Você entende por que `0.0.0.0` e não `127.0.0.1`.

**Consolida:** Dockerfile, contexto de build, usuário não-root, bind em `0.0.0.0`.

---

## Lab 3 — Persistência (45 min)

**Objetivo:** provar a diferença entre camada de escrita e volume.

```bash
# Sem volume: o dado morre
docker run --rm --name t alpine sh -c 'echo importante > /d.txt; cat /d.txt'
docker run --rm alpine cat /d.txt 2>&1 || echo "morreu, como esperado"

# Com volume: sobrevive
docker volume create meus
docker run --rm -v meus:/dados alpine sh -c 'echo importante > /dados/d.txt'
docker run --rm -v meus:/dados alpine cat /dados/d.txt

# Postgres com e sem volume
docker run -d --name pg -e POSTGRES_PASSWORD=x -v pgdata:/var/lib/postgresql/data postgres:16-alpine
sleep 8
docker exec pg psql -U postgres -c "CREATE TABLE t(id int); INSERT INTO t VALUES (42);"
docker rm -f pg
docker run -d --name pg -e POSTGRES_PASSWORD=x -v pgdata:/var/lib/postgresql/data postgres:16-alpine
sleep 8
docker exec pg psql -U postgres -c "SELECT * FROM t;"    # o 42 continua lá
docker rm -f pg && docker volume rm pgdata meus
```

**Critério:**
- [ ] O arquivo sem volume não sobreviveu à recriação.
- [ ] O `42` sobreviveu à destruição e recriação do container Postgres.
- [ ] Você sabe dizer onde o volume fica no host (`docker volume inspect`).

**Consolida:** efemeridade da camada de escrita; volume nomeado para estado.

---

## Lab 4 — Multi-stage e o tamanho da imagem (1 h)

**Objetivo:** reduzir uma imagem em 80% com multi-stage.

Construa **primeiro** a versão ingênua e meça; depois a multi-stage e compare.

Ingênua (`Dockerfile.ruim`):
```dockerfile
FROM node:22
WORKDIR /app
COPY . .
RUN npm ci && npm run build
CMD ["node", "dist/main.js"]
```

Multi-stage (`Dockerfile`): use o modelo do
[06-exemplos.md exemplo 4](06-exemplos.md#4-dockerfile-node-com-multi-stage-e-cache-eficiente).

```bash
docker build -f Dockerfile.ruim -t app:ruim .
docker build -t app:bom .
docker images | grep app
docker history app:bom
```

**Critério:**
- [ ] `app:bom` é pelo menos 60% menor que `app:ruim`.
- [ ] Você identifica, no `docker history`, a maior camada de cada uma.
- [ ] Alterar uma linha de código e reconstruir `app:bom` **não** reexecuta o `npm ci`.

**Consolida:** multi-stage, cache de camadas, ordem das instruções.

---

## Lab 5 — Compose com dependências (1 h)

**Objetivo:** subir app + banco + cache com ordem correta.

Use o `compose.yaml` do [04-como-comecar.md, Passo 5](04-como-comecar.md#passo-5--vários-containers-juntos-compose)
e evolua para incluir healthcheck com `condition: service_healthy`.

```bash
docker compose up -d
docker compose ps
docker compose exec app sh -c 'nslookup cache'
docker compose logs -f app
docker compose down
```

**Critério:**
- [ ] O `app` só subiu depois de o `cache` ficar `healthy`.
- [ ] O `app` alcança o `cache` pelo **nome**, não por IP.
- [ ] `docker compose config` mostra o YAML resolvido sem erro.

**Consolida:** Compose, DNS interno, `depends_on` com condição.

---

## Lab 6 — Depuração de rede (Linux, 1 h)

**Objetivo:** diagnosticar três falhas de conectividade plantadas.

```bash
# Falha A: app em 127.0.0.1
docker run -d --name fa -p 9001:9001 python:3.13-slim \
  python -c "import http.server,socketserver; socketserver.TCPServer(('127.0.0.1',9001),http.server.BaseHTTPRequestHandler).serve_forever()"
curl localhost:9001    # falha — descubra por quê e conserte usando 0.0.0.0

# Falha B: bridge padrão sem DNS
docker run -d --name fb1 nginx:alpine
docker run --rm alpine ping -c1 fb1    # falha — conserte criando uma rede

# Falha C: porta já em uso
docker run -d --name fc1 -p 9003:80 nginx:alpine
docker run -d --name fc2 -p 9003:80 nginx:alpine    # falha — leia o erro e resolva

docker rm -f fa fb1 fc1 fc2 2>/dev/null
```

**Critério:**
- [ ] Você explicou e corrigiu cada uma das três falhas.
- [ ] Usou `docker logs`, `docker port` e `ss -tlnp` no diagnóstico.
- [ ] Sabe entrar no namespace de rede com `--network container:NOME`.

**Consolida:** a árvore de diagnóstico de [16-redes.md](16-redes.md).

---

## Lab 7 — Segurança: endurecer um container (1 h)

**Objetivo:** transformar um container permissivo em um endurecido, sem quebrá-lo.

```bash
# Antes: permissivo
docker run -d --name antes nginx:alpine
docker exec antes id                      # root
docker exec antes sh -c 'echo x > /etc/y' # escreve na raiz

# Depois: endurecido
docker run -d --name depois \
  --user 101:101 \
  --cap-drop=ALL --cap-add=NET_BIND_SERVICE \
  --security-opt no-new-privileges:true \
  --read-only \
  --tmpfs /var/cache/nginx --tmpfs /var/run \
  --memory 128m --pids-limit 100 \
  nginx:alpine
sleep 2
docker exec depois sh -c 'echo x > /etc/y' 2>&1 || echo "escrita bloqueada — correto"
curl -sI localhost 2>/dev/null | head -1  # o nginx ainda funciona?
docker rm -f antes depois
```

**Critério:**
- [ ] O container endurecido **não** consegue escrever na raiz.
- [ ] Ele **não** roda como root.
- [ ] E ainda assim serve HTTP.
- [ ] Você aplicou o mesmo endurecimento no `compose.yaml` do projeto-modelo.

**Consolida:** o checklist de [20-seguranca.md](20-seguranca.md).

---

## Lab 8 — Segredo que não vaza (Linux, 45 min)

**Objetivo:** provar o vazamento por `ARG` e corrigir com `--mount=type=secret`.

```bash
# Vazamento
echo "token-secreto-123" > segredo.txt
cat > Dockerfile.vaza <<'EOF'
# syntax=docker/dockerfile:1
FROM alpine
ARG TOKEN
RUN echo "$TOKEN" > /tmp/t && cat /tmp/t && rm /tmp/t
EOF
docker build -f Dockerfile.vaza --build-arg TOKEN=$(cat segredo.txt) -t vaza .
docker history --no-trunc vaza | grep -c token    # > 0: vazou

# Correção
cat > Dockerfile.ok <<'EOF'
# syntax=docker/dockerfile:1
FROM alpine
RUN --mount=type=secret,id=tok cat /run/secrets/tok > /dev/null && echo "usei o segredo"
EOF
docker build -f Dockerfile.ok --secret id=tok,src=segredo.txt -t ok .
docker history --no-trunc ok | grep -c token      # 0: não vazou

rm segredo.txt Dockerfile.vaza Dockerfile.ok
```

**Critério:**
- [ ] Você viu o token no histórico da imagem `vaza`.
- [ ] Você confirmou que ele **não** aparece na imagem `ok`.

**Consolida:** [12-imagens-e-camadas.md, seção 6](12-imagens-e-camadas.md#6-segredos-vazam-em-camadas--a-demonstração).

---

## Lab 9 — Limites e OOM (Linux, 45 min)

**Objetivo:** ver o OOM killer agir e ler o exit code.

```bash
docker run --rm --memory 64m --memory-swap 64m python:3.13-slim \
  python -c "a=[]
while True: a.append(bytearray(5*1024*1024))" ; echo "exit: $?"
# esperado: Killed, exit 137

# Confirme que foi OOM
docker run -d --name oom --memory 64m --memory-swap 64m python:3.13-slim \
  python -c "a=[]
while True: a.append(bytearray(5*1024*1024))"
sleep 3
docker inspect oom --format '{{.State.OOMKilled}} {{.State.ExitCode}}'
docker rm -f oom

# Throttling de CPU
docker run -d --name cpu --cpus 0.2 alpine sh -c 'while :; do :; done'
sleep 5
CG=/sys/fs/cgroup/system.slice/docker-$(docker inspect -f '{{.Id}}' cpu).scope
cat $CG/cpu.stat | grep throttled
docker rm -f cpu
```

**Critério:**
- [ ] Exit code 137 e `OOMKilled=true`.
- [ ] `nr_throttled` maior que zero no container limitado a 0.2 CPU.

**Consolida:** [13-isolamento-namespaces-cgroups.md](13-isolamento-namespaces-cgroups.md).

---

## Lab 10 — Do zero à produção (projeto integrador, 3 h)

**Objetivo:** pegar uma aplicação sua (ou o [projeto-modelo](07-projeto-modelo/README.md)) e
levá-la a um estado publicável.

Etapas, cada uma com seu critério:

1. **Containerizar** com multi-stage, não-root, healthcheck, sinais tratados.
   - [ ] `docker build` produz imagem < 200 MB, roda como não-root, para em < 2 s.
2. **Compose** com banco, rede segmentada, limites e segredos.
   - [ ] Sobe com um comando; o banco não tem `ports:`; `internal: true` na rede interna.
3. **CI** que constrói, testa, escaneia e publica (use o
   [exemplo 12](06-exemplos.md#12-produção--pipeline-de-ci-completo-no-github-actions)).
   - [ ] O pipeline falha se um teste quebrar ou se houver CVE crítica corrigível.
4. **Publicar** no GHCR, com tag semântica e digest.
   - [ ] A imagem está no registry, referenciada por digest no deploy.
5. **Observar**: healthcheck, log estruturado, limite de log.
   - [ ] `docker inspect` mostra `healthy`; os logs são JSON de uma linha.
6. **Backup** de volume testado.
   - [ ] Você apagou o volume, restaurou do backup e os dados voltaram.

**Critério de aprovação final:**
- [ ] Outra pessoa consegue subir tudo seguindo só o seu `README.md`.
- [ ] Você consegue explicar cada decisão do Dockerfile e do Compose.
- [ ] Nenhum segredo no Git, na imagem ou em variável de ambiente inspecionável.

**Consolida:** tudo. Este laboratório é o exame prático do assunto.

---

## Autoavaliação final

Se você consegue fazer o Lab 10 sem consultar, você **sabe Docker** no nível de operar em
produção num servidor. O que falta a partir daí é escala (orquestração,
[25-orquestracao.md](25-orquestracao.md)) e profundidade interna
([13](13-isolamento-namespaces-cgroups.md), [14](14-runtime-e-arquitetura.md),
[60](60-teoria-avancada.md)).

Erros que você deveria conseguir diagnosticar em menos de um minuto, ao final:

1. Container sai imediatamente com `Exited (0)`.
2. `connection refused` num container aparentemente saudável.
3. Exit code 137.
4. "A imagem está com 1,5 GB."
5. `ping outro-container` não resolve o nome.
6. Build refaz o `npm ci` a cada mudança de código.
7. Arquivos criados pelo container pertencem ao root no host.
8. O disco encheu de `/var/lib/docker`.

Se algum desses ainda te trava, volte ao arquivo correspondente. As respostas estão todas em
[75-armadilhas.md](75-armadilhas.md).
