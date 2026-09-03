# 05 · Manual de uso — referência consultável

`Nível: intermediário` · `Organizado por tarefa, não por ordem alfabética` · `Última atualização: 11/08/2026`

Referência de bolso. Não se lê de ponta a ponta — se consulta. Cada seção responde a uma
pergunta do tipo "como eu faço X".

---

## Índice

1. [Rodar um container](#1-rodar-um-container)
2. [Inspecionar e diagnosticar](#2-inspecionar-e-diagnosticar)
3. [Entrar e depurar](#3-entrar-e-depurar)
4. [Imagens](#4-imagens)
5. [Construir imagens](#5-construir-imagens)
6. [Instruções do Dockerfile](#6-instruções-do-dockerfile)
7. [Volumes e dados](#7-volumes-e-dados)
8. [Redes](#8-redes)
9. [Registries](#9-registries)
10. [Compose](#10-compose)
11. [Limites de recurso](#11-limites-de-recurso)
12. [Limpeza e espaço em disco](#12-limpeza-e-espaço-em-disco)
13. [Contexts e daemon remoto](#13-contexts-e-daemon-remoto)
14. [Formatação de saída](#14-formatação-de-saída-go-templates)
15. [Obsoleto — o que não usar mais](#15-obsoleto--o-que-não-usar-mais)
16. [Atalhos que só quem usa há anos conhece](#16-atalhos-que-só-quem-usa-há-anos-conhece)

---

## 1. Rodar um container

```bash
docker run [OPÇÕES] IMAGEM [COMANDO] [ARG...]
```

### Flags essenciais

| Flag | O que faz | Quando usar |
|---|---|---|
| `-d`, `--detach` | Roda em segundo plano | Serviços de longa duração |
| `-it` | `-i` mantém stdin aberto, `-t` aloca TTY | Sempre que quiser um shell interativo |
| `--rm` | Remove o container ao terminar | **Sempre**, em containers efêmeros e de teste |
| `--name NOME` | Nome fixo | Sempre que precisar referenciá-lo depois |
| `-p HOST:CONTAINER` | Publica porta | Serviço acessível de fora |
| `-P` | Publica **todas** as portas de `EXPOSE` em portas altas aleatórias | Testes rápidos |
| `-e VAR=valor` | Variável de ambiente | Configuração |
| `--env-file arq` | Lê variáveis de um arquivo | Muitas variáveis; evita expor no histórico |
| `-v NOME:/cam` | Volume nomeado | Dados persistentes |
| `-v /host:/cam` | Bind mount (caminho absoluto) | Código em desenvolvimento |
| `--mount type=...` | Sintaxe explícita e verbosa | Scripts e produção; erra menos |
| `-w /cam` | Diretório de trabalho | Evita `cd` no comando |
| `-u UID:GID` | Usuário do processo | Corrigir dono de arquivos em bind mount |
| `--network NOME` | Conecta a uma rede | Comunicação entre containers |
| `--restart POLÍTICA` | `no` · `on-failure[:N]` · `always` · `unless-stopped` | Serviços que devem voltar sozinhos |
| `--init` | Injeta um init (`tini`) como PID 1 | App que não trata sinais nem colhe zumbis |
| `--platform linux/amd64` | Força a arquitetura | Imagem sem build para ARM |
| `--pull always` | Rebaixa a imagem local e busca do registry | CI, garantir versão fresca |
| `--entrypoint CMD` | Substitui o ENTRYPOINT da imagem | Depurar imagem que não abre shell |
| `--health-cmd`, `--health-interval` | Healthcheck sem alterar a imagem | Ajuste pontual |

### Diferença `run` × `create` × `start`

```bash
docker create --name x nginx    # cria, NÃO inicia
docker start x                  # inicia um container existente
docker run --name x nginx       # equivale a create + start
docker start -ai x              # inicia e anexa (interativo)
```

### Política de reinício — a tabela que resolve a dúvida

| Política | Reinicia se o processo falhar? | Reinicia no boot da máquina? | Reinicia após `docker stop` manual? |
|---|---|---|---|
| `no` (padrão) | não | não | não |
| `on-failure[:5]` | sim, se exit ≠ 0, até 5 vezes | sim | não |
| `always` | sim | sim | **sim** (surpresa comum) |
| `unless-stopped` | sim | sim, **exceto** se você parou antes | não |

**Recomendação:** `unless-stopped` para quase tudo. `always` só quando o container realmente
deve voltar mesmo após parada manual — o que raramente é o desejado.

---

## 2. Inspecionar e diagnosticar

| Comando | Para quê |
|---|---|
| `docker ps` | Containers rodando |
| `docker ps -a` | Todos, inclusive parados — **onde estão os que morreram** |
| `docker ps -q` | Só os IDs (para encadear em outros comandos) |
| `docker ps --filter "status=exited"` | Filtrar por estado |
| `docker logs NOME` | Saída padrão e de erro do PID 1 |
| `docker logs -f --tail 100 NOME` | Acompanhar, começando pelas últimas 100 linhas |
| `docker logs --since 10m NOME` | Só os últimos 10 minutos |
| `docker logs -t NOME` | Com timestamp |
| `docker inspect NOME` | **Tudo** sobre o container, em JSON |
| `docker stats` | CPU, memória, rede e I/O ao vivo |
| `docker stats --no-stream` | Uma foto, sem ficar atualizando |
| `docker top NOME` | Processos do container, vistos do host |
| `docker port NOME` | Mapeamento real de portas |
| `docker diff NOME` | Arquivos alterados na camada de escrita (A=add, C=change, D=delete) |
| `docker events` | Fluxo de eventos do daemon ao vivo |
| `docker system info` | Configuração do daemon: driver de storage, cgroup, runtime |

### Perguntas de diagnóstico e a resposta em uma linha

```bash
# Por que o container morreu?
docker inspect --format '{{.State.ExitCode}} {{.State.Error}} {{.State.OOMKilled}}' NOME
# OOMKilled=true → estourou o limite de memória

# Qual é o IP interno dele?
docker inspect --format '{{range .NetworkSettings.Networks}}{{.IPAddress}} {{end}}' NOME

# Que comando ele está rodando de fato?
docker inspect --format '{{.Config.Entrypoint}} {{.Config.Cmd}}' NOME

# Quais variáveis de ambiente ele recebeu?
docker inspect --format '{{range .Config.Env}}{{println .}}{{end}}' NOME

# O que está montado nele?
docker inspect --format '{{range .Mounts}}{{.Type}} {{.Source}} -> {{.Destination}}{{println}}{{end}}' NOME

# O healthcheck está falhando por quê?
docker inspect --format '{{json .State.Health}}' NOME | jq
```

### Códigos de saída que dizem alguma coisa

| Código | Significado |
|---|---|
| `0` | Terminou normalmente. Se era para ser um serviço, o processo estava errado |
| `1` | Erro genérico da aplicação — leia os logs |
| `125` | Erro **do próprio Docker** (flag inválida, por exemplo) |
| `126` | O comando existe mas não é executável (falta bit de execução) |
| `127` | Comando não encontrado (típico de erro de caminho ou binário ausente) |
| `137` | `SIGKILL` (128+9) — **quase sempre OOM**: confira `OOMKilled` |
| `143` | `SIGTERM` (128+15) — parada normal via `docker stop` |

---

## 3. Entrar e depurar

```bash
docker exec -it NOME sh              # shell num container rodando (funciona em Alpine)
docker exec -it NOME bash            # se a imagem tiver bash
docker exec -u root -it NOME sh      # entrar como root, mesmo que o container rode sem privilégio
docker exec -it NOME env             # ver as variáveis efetivas
docker attach NOME                   # anexa ao PID 1 (⚠️ Ctrl+C mata o container; saia com Ctrl-P Ctrl-Q)
```

### Quando a imagem não tem shell (distroless, scratch)

```bash
# Opção 1 — anexar um container de depuração ao namespace do alvo
docker run -it --rm --pid container:NOME --network container:NOME \
  --cap-add SYS_PTRACE nicolaka/netshoot

# Opção 2 — docker debug (Docker Desktop, assinatura paga)
docker debug NOME

# Opção 3 — copiar o sistema de arquivos para fora e olhar
docker export NOME | tar -tv | head -50
```

`nicolaka/netshoot` é a caixa de ferramentas de rede de fato: traz `dig`, `curl`, `tcpdump`,
`ss`, `iperf`, `nmap`. Vale memorizar o nome.

### Copiar arquivos

```bash
docker cp NOME:/app/log.txt ./           # de dentro para fora
docker cp ./config.json NOME:/app/       # de fora para dentro (não persiste após rm!)
```

---

## 4. Imagens

| Comando | Para quê |
|---|---|
| `docker images` / `docker image ls` | Listar |
| `docker images -a` | Incluir camadas intermediárias |
| `docker pull IMG:TAG` | Baixar |
| `docker push IMG:TAG` | Enviar ao registry |
| `docker tag ORIGEM DESTINO` | Criar outro nome para a mesma imagem (não copia nada) |
| `docker rmi IMG` | Remover |
| `docker image inspect IMG` | Metadados completos |
| `docker history IMG` | **Camadas, tamanho e comando de cada uma** — o mapa do que engordou |
| `docker save IMG -o img.tar` | Exportar para arquivo (máquina sem rede) |
| `docker load -i img.tar` | Importar |
| `docker image prune -a` | Remover imagens não usadas |

### Anatomia do nome de uma imagem

```
registry.exemplo.com:5000/organizacao/nome:tag@sha256:abc...
└──────── registry ─────┘ └─ namespace ─┘ └nome┘└tag┘└─── digest ────┘
      (padrão: docker.io)   (padrão: library)      (padrão: latest)
```

Portanto `nginx` é açúcar sintático para `docker.io/library/nginx:latest`. Saber disso resolve
metade das confusões com registry privado.

```bash
# Ver o digest imutável de uma imagem
docker image inspect --format '{{index .RepoDigests 0}}' nginx:alpine
```

---

## 5. Construir imagens

```bash
docker build -t nome:tag .
docker buildx build -t nome:tag .        # mesma coisa, com o motor moderno explícito
```

| Flag | O que faz |
|---|---|
| `-t nome:tag` | Nomeia. Pode repetir para múltiplas tags |
| `-f caminho/Dockerfile` | Dockerfile fora do padrão |
| `--build-arg CHAVE=valor` | Passa um `ARG` para o build (⚠️ **fica no histórico da imagem — nunca use para segredo**) |
| `--target ESTÁGIO` | Para num estágio do multi-stage (ex.: `--target dev`) |
| `--no-cache` | Ignora todo o cache |
| `--pull` | Rebusca a imagem base |
| `--platform linux/amd64,linux/arm64` | Build multi-arquitetura |
| `--progress=plain` | Log completo do build, sem a UI que colapsa linhas — **essencial para depurar** |
| `--secret id=x,src=arq` | Segredo montado só durante um `RUN`, sem ir para a imagem |
| `--ssh default` | Repassa o agente SSH para clonar repositório privado |
| `--cache-from` / `--cache-to` | Cache externo (registry), o que faz CI ficar rápido |
| `--output type=local,dest=./out` | Extrai artefatos do build sem gerar imagem |

### Multi-arquitetura, na prática

```bash
docker buildx create --name multi --driver docker-container --use   # uma vez só
docker buildx build --platform linux/amd64,linux/arm64 \
  -t usuario/app:1.0 --push .
```
> Multi-arch **exige** `--push`: o *manifest list* que agrupa as arquiteturas não cabe no
> armazenamento local antigo. Com o containerd image store (padrão desde a Engine 29), o
> `--load` de múltiplas plataformas passa a ser possível.

### Cache de build em CI

```bash
docker buildx build \
  --cache-from type=registry,ref=usuario/app:cache \
  --cache-to   type=registry,ref=usuario/app:cache,mode=max \
  -t usuario/app:1.0 --push .
```

---

## 6. Instruções do Dockerfile

| Instrução | O que faz | Cuidado |
|---|---|---|
| `FROM img:tag AS nome` | Imagem base; inicia um estágio | Sempre fixe a tag; `AS` habilita multi-stage |
| `WORKDIR /cam` | Define e **cria** o diretório de trabalho | Use em vez de `RUN cd`, que não persiste |
| `COPY origem destino` | Copia do contexto de build | Prefira a `ADD` |
| `COPY --from=estagio a b` | Copia de outro estágio | O coração do multi-stage |
| `COPY --chown=user:grp a b` | Copia já com o dono certo | Evita uma camada extra de `chown` |
| `ADD` | `COPY` + extrai tar + baixa URL | **Evite**: comportamento implícito surpreende |
| `RUN cmd` | Executa no build, cria camada | Encadeie com `&&` para reduzir camadas |
| `RUN --mount=type=cache,target=/cam` | Cache persistente entre builds | Ouro para `npm`, `pip`, `apt`, `go mod` |
| `RUN --mount=type=secret,id=x` | Segredo temporário | O jeito **certo** de usar credencial no build |
| `CMD ["a","b"]` | Comando padrão, sobrescrevível | Forma exec (lista JSON), sempre |
| `ENTRYPOINT ["a"]` | Executável fixo; o `CMD` vira argumento | Para imagens que se comportam como um comando |
| `ENV K=V` | Variável de ambiente na imagem e nos containers | Fica visível no `inspect` — não coloque segredo |
| `ARG K=V` | Variável **só durante o build** | Fica no histórico; não é segredo |
| `EXPOSE 3000` | Documenta a porta | **Não publica nada** |
| `USER node` | Troca o usuário | Sempre, antes do `CMD` |
| `VOLUME /dados` | Marca um caminho como volume anônimo | Use com parcimônia: cria volumes órfãos |
| `HEALTHCHECK CMD ...` | Como saber se está saudável | Habilita `condition: service_healthy` no Compose |
| `LABEL k=v` | Metadados | Use o padrão OCI (`org.opencontainers.image.*`) |
| `ONBUILD` | Dispara instruções na imagem filha | Confuso; evite |
| `STOPSIGNAL SIGQUIT` | Sinal de parada | nginx, por exemplo, quer `SIGQUIT` para sair rápido |
| `SHELL ["pwsh","-c"]` | Troca o shell da forma shell | Raro fora de Windows |

### `CMD` × `ENTRYPOINT` — a tabela que encerra a dúvida

| Dockerfile | `docker run img` executa | `docker run img echo oi` executa |
|---|---|---|
| `CMD ["node","app.js"]` | `node app.js` | `echo oi` (substitui) |
| `ENTRYPOINT ["node"]` | `node` | `node echo oi` (**acrescenta**) |
| `ENTRYPOINT ["node"]` + `CMD ["app.js"]` | `node app.js` | `node echo oi` |

Regra prática: **`ENTRYPOINT` = o que a imagem *é*; `CMD` = o argumento *padrão*.** Uma imagem
de `ffmpeg` deveria ter `ENTRYPOINT ["ffmpeg"]`; uma imagem de aplicação, só `CMD`.

---

## 7. Volumes e dados

```bash
docker volume create nome
docker volume ls
docker volume inspect nome            # mostra o Mountpoint no host
docker volume rm nome
docker volume prune                   # remove os órfãos ⚠️ apaga dados
docker volume ls -f dangling=true     # listar órfãos ANTES de apagar
```

### As três formas de montar

```bash
-v nome:/cam                                   # volume nomeado
-v /host/abs:/cam                              # bind mount (o caminho DEVE ser absoluto)
--mount type=volume,source=nome,target=/cam    # sintaxe explícita, equivalente à 1ª
--mount type=bind,source=/host/abs,target=/cam,readonly
--mount type=tmpfs,target=/tmp                 # em RAM, some ao parar; ideal para segredo
```

### Modificadores

| Sufixo | Efeito |
|---|---|
| `:ro` | Somente leitura — use sempre que o container não precise escrever |
| `:rw` | Leitura e escrita (padrão) |
| `:z` | Rótulo SELinux **compartilhado** entre containers (Fedora/RHEL) |
| `:Z` | Rótulo SELinux **exclusivo** deste container |
| `:delegated` / `:cached` | Dicas de consistência no macOS (obsoletas com VirtioFS) |

### Backup e restauração — a receita padrão

```bash
# Backup
docker run --rm -v MEU_VOLUME:/dados:ro -v "$PWD:/backup" alpine \
  tar czf /backup/volume-$(date +%F).tgz -C /dados .

# Restauração
docker run --rm -v MEU_VOLUME:/dados -v "$PWD:/backup" alpine \
  sh -c "rm -rf /dados/* && tar xzf /backup/volume-2026-08-11.tgz -C /dados"

# Backup lógico de banco (melhor que copiar arquivo do Postgres a quente)
docker compose exec -T db pg_dump -U usuario base | gzip > dump-$(date +%F).sql.gz
```

> **Nunca faça backup de um volume de Postgres/MySQL copiando os arquivos com o banco rodando.**
> Você captura um estado inconsistente. Use `pg_dump`/`mysqldump`, ou pare o container antes.

---

## 8. Redes

```bash
docker network ls
docker network create minha-rede
docker network create --driver bridge --subnet 172.28.0.0/16 rede-fixa
docker network inspect minha-rede          # quem está conectado, com quais IPs
docker network connect minha-rede NOME     # conecta um container já rodando
docker network disconnect minha-rede NOME
docker network prune
```

### Drivers

| Driver | O que faz | Quando usar |
|---|---|---|
| `bridge` | Rede virtual isolada, com NAT (padrão) | Praticamente sempre |
| `host` | Sem isolamento de rede: usa a pilha do host direto | Desempenho máximo, ou serviço que precisa de todas as portas. ⚠️ Só Linux, e `-p` deixa de funcionar |
| `none` | Sem rede | Processamento isolado, batch sem rede |
| `overlay` | Rede entre múltiplos hosts | Swarm, cluster |
| `macvlan` | O container recebe um MAC e um IP na sua LAN | Aparelhos que precisam ser vistos na rede física (Home Assistant, Pi-hole) |

### As regras de DNS que você precisa saber

1. Na **rede bridge padrão** (a que você usa sem `--network`), **não há resolução por nome**.
   Containers só se acham por IP. É legado, e é a causa de "por que `ping outro-container` não
   funciona".
2. Em **qualquer rede criada por você** — inclusive as que o Compose cria — o Docker embute um
   servidor DNS em `127.0.0.11` e **o nome do container/serviço resolve automaticamente**.
3. `host.docker.internal` resolve para o host, a partir do container. Funciona por padrão no
   Docker Desktop; no Linux, exige `--add-host=host.docker.internal:host-gateway`.

```bash
docker run -d --network minha-rede --name api nginx
docker run --rm --network minha-rede alpine ping -c1 api    # ✅ funciona
docker run --rm alpine ping -c1 api                          # ❌ rede padrão: não resolve
```

### Publicação de porta com cuidado

```bash
-p 8080:80                  # escuta em TODAS as interfaces — visível na sua LAN
-p 127.0.0.1:8080:80        # ✅ só na máquina local
-p 8080:80/udp              # UDP
-p 8080-8090:8080-8090      # faixa
```

> **Cicatriz de campo:** `-p 5432:5432` num Postgres de desenvolvimento expõe o banco para toda
> a rede local, e o Docker escreve regras de iptables que **passam por cima** do seu `ufw`. Um
> banco com senha fraca em rede de coworking é comprometido em horas. Use
> `-p 127.0.0.1:5432:5432`.

---

## 9. Registries

```bash
echo "$TOKEN" | docker login -u USUARIO --password-stdin
echo "$TOKEN" | docker login ghcr.io -u USUARIO --password-stdin
docker logout [registry]

docker tag app:1.0 ghcr.io/usuario/app:1.0
docker push ghcr.io/usuario/app:1.0
docker pull ghcr.io/usuario/app:1.0
```

| Registry | Endereço | Gratuito para |
|---|---|---|
| Docker Hub | `docker.io` | Público ilimitado; 1 repositório privado no plano gratuito |
| GitHub Container Registry | `ghcr.io` | Público ilimitado; privado dentro da cota do GitHub |
| Quay.io | `quay.io` | Público ilimitado |
| GitLab | `registry.gitlab.com` | Dentro da cota do projeto |
| AWS ECR / Google AR / Azure ACR | vários | Pago por armazenamento e tráfego |
| Registry local | `registry:2` | Você mesmo hospeda |

```bash
# Registry local em 30 segundos (laboratório)
docker run -d -p 5000:5000 --name registry --restart unless-stopped registry:2
docker tag app:1.0 localhost:5000/app:1.0
docker push localhost:5000/app:1.0
```

---

## 10. Compose

Arquivo padrão: **`compose.yaml`** (nomes aceitos, em ordem de precedência: `compose.yaml`,
`compose.yml`, `docker-compose.yaml`, `docker-compose.yml`).

| Comando | O que faz |
|---|---|
| `docker compose up -d` | Sobe tudo em segundo plano |
| `docker compose up -d --build` | Reconstrói as imagens antes |
| `docker compose up -d --force-recreate` | Recria containers mesmo sem mudança |
| `docker compose down` | Para e remove containers e redes (**mantém volumes**) |
| `docker compose down -v` | ⚠️ + remove volumes |
| `docker compose down --rmi all` | + remove imagens |
| `docker compose ps` | Estado dos serviços |
| `docker compose logs -f [serviço]` | Logs |
| `docker compose exec serviço sh` | Shell num serviço rodando |
| `docker compose run --rm serviço cmd` | Container **novo e efêmero** (migrações, testes) |
| `docker compose build [serviço]` | Só constrói |
| `docker compose pull` | Baixa as imagens declaradas |
| `docker compose restart [serviço]` | Reinicia |
| `docker compose stop` / `start` | Para/inicia sem remover |
| `docker compose config` | **Mostra o YAML final resolvido** — o melhor depurador de Compose |
| `docker compose top` | Processos de todos os serviços |
| `docker compose watch` | Sincroniza arquivos e reconstrói ao salvar (dev) |
| `docker compose -f a.yaml -f b.yaml up` | Sobrepõe arquivos (base + ambiente) |
| `docker compose --profile dev up` | Sobe só os serviços do perfil |

### `exec` × `run` — a confusão clássica

```bash
docker compose exec db psql -U app      # usa o container QUE JÁ ESTÁ RODANDO
docker compose run --rm db psql -U app  # cria um container NOVO (e sobe as dependências)
```
Use `exec` para inspecionar o que está no ar; `run --rm` para tarefas pontuais (migração,
seed, teste), porque não interfere no serviço em execução.

### Campos de `compose.yaml` que valem memorizar

```yaml
services:
  api:
    build:
      context: .
      dockerfile: Dockerfile
      target: production          # estágio do multi-stage
      args:                       # ARGs do build
        NODE_VERSION: "22"
    image: usuario/api:1.0        # nome da imagem construída
    command: ["node", "server.js"]
    entrypoint: ["/entrypoint.sh"]
    ports: ["127.0.0.1:3000:3000"]
    environment:
      NODE_ENV: production
    env_file: [.env]
    volumes:
      - ./src:/app/src:ro
      - dados:/app/uploads
    depends_on:
      db: { condition: service_healthy }
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/saude"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 40s           # carência inicial: falhas aqui não contam
    restart: unless-stopped
    deploy:
      resources:
        limits:   { cpus: "1.0", memory: 512M }
        reservations: { memory: 256M }
    networks: [interna]
    profiles: [prod]
    logging:
      driver: json-file
      options: { max-size: "10m", max-file: "3" }

volumes:
  dados:
networks:
  interna:
    internal: true                # sem saída para a internet
```

---

## 11. Limites de recurso

| Flag | Efeito | Observação |
|---|---|---|
| `-m 512m` / `--memory` | Teto de RAM | Ultrapassar = processo morto pelo OOM killer, exit 137 |
| `--memory-reservation 256m` | Limite flexível, sob pressão | |
| `--memory-swap 1g` | Memória + swap somados | `--memory-swap = --memory` desliga swap |
| `--oom-kill-disable` | Não mata no OOM | ⚠️ Congela o container. Quase nunca é o que se quer |
| `--cpus 1.5` | 1,5 núcleo | A forma moderna e legível |
| `--cpu-shares 512` | Peso relativo (padrão 1024) | Só vale sob disputa |
| `--cpuset-cpus 0,1` | Fixa em núcleos específicos | Latência previsível |
| `--pids-limit 200` | Máximo de processos | **Defesa barata contra fork bomb** |
| `--ulimit nofile=65535:65535` | Descritores de arquivo | Servidores com muitas conexões |
| `--device-read-bps /dev/sda:10mb` | Limita I/O de disco | Exige cgroup v2 |
| `--blkio-weight 500` | Peso relativo de I/O | |

```bash
docker run -d --name api -m 512m --cpus 1.0 --pids-limit 200 minha-api:1.0
docker stats --no-stream api
# esperado: MEM USAGE / LIMIT mostrando ".../ 512MiB"
```

> **Regra de produção:** todo container deve ter limite de memória. Sem limite, um vazamento
> numa aplicação derruba o host inteiro e leva junto todos os outros containers. O limite
> transforma "servidor caiu" em "um container reiniciou".

---

## 12. Limpeza e espaço em disco

```bash
docker system df                              # panorama; a coluna RECLAIMABLE é a que importa
docker system df -v                           # detalhado, por imagem e volume

docker container prune                        # containers parados
docker image prune                            # imagens dangling (<none>)
docker image prune -a                         # + todas as não usadas por container
docker volume prune                           # ⚠️ volumes órfãos = perda de dados
docker network prune
docker builder prune                          # cache de build (costuma ser o maior vilão)
docker builder prune --keep-storage 10GB

docker system prune                           # tudo acima, exceto volumes e imagens usadas
docker system prune -a --volumes              # ⚠️⚠️ arrasa quarteirão

# Filtrar por idade (mais seguro que sair podando tudo)
docker image prune -a --filter "until=168h"   # imagens com mais de 7 dias
```

### Limitar log — o vazamento silencioso

Por padrão, o driver `json-file` **não tem limite de tamanho**. Um container falante enche o
disco em semanas. Corrija globalmente:

```json
// /etc/docker/daemon.json
{
  "log-driver": "json-file",
  "log-opts": { "max-size": "10m", "max-file": "3" }
}
```
```bash
sudo systemctl restart docker    # vale para containers criados DEPOIS disso
```

---

## 13. Contexts e daemon remoto

```bash
docker context ls
docker context create prod --docker "host=ssh://usuario@servidor.exemplo.com"
docker context use prod
docker ps                                  # lista os containers do servidor remoto
docker context use default
docker --context prod ps                   # uso pontual, sem trocar o padrão
```

Melhor que `DOCKER_HOST` porque é nomeado, persistente e aparece no `ls`. Sobre SSH, não
precisa expor o socket do daemon na rede — o que seria entregar root remoto.

---

## 14. Formatação de saída (Go templates)

```bash
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
docker images --format "{{.Repository}}:{{.Tag}}\t{{.Size}}"
docker ps --format json | jq -r '.Names'
docker inspect --format '{{.NetworkSettings.IPAddress}}' NOME
docker ps -a --filter "status=exited" --format "{{.ID}}" | xargs -r docker rm
```

Alias que vale a pena guardar no `~/.bashrc`:

```bash
alias dps='docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"'
alias dclean='docker system prune -f && docker builder prune -f'
alias dsh='f(){ docker exec -it "$1" sh; }; f'
alias dlog='f(){ docker logs -f --tail 100 "$1"; }; f'
```

---

## 15. Obsoleto — o que não usar mais

| Obsoleto | Substituto | Desde |
|---|---|---|
| `docker-compose` (v1, Python, com hífen) | `docker compose` (v2, plugin Go) | v1 sem suporte desde jul/2023 |
| `version: "3.8"` no topo do Compose | Nada — o campo é ignorado e gera aviso | Compose Specification |
| `links:` entre serviços | Redes + DNS automático | Docker 1.9 |
| `docker run --link` | `docker network create` | Docker 1.9 |
| `MAINTAINER` no Dockerfile | `LABEL org.opencontainers.image.authors="..."` | Docker 1.13 |
| `ADD` para copiar arquivo local | `COPY` | Sempre foi a recomendação |
| `docker build` legado (sem BuildKit) | BuildKit/buildx (padrão desde a Engine 23) | 2023 |
| `docker rmi`/`docker rm` soltos | `docker image rm` / `docker container rm` | Docker 1.13 (os antigos continuam funcionando) |
| Docker Swarm clássico (standalone) | Swarm mode embutido, ou Kubernetes | 2016 |
| `latest` em produção | Tag semântica + digest | Sempre |
| Segredo via `--build-arg` | `--mount=type=secret` | BuildKit |

---

## 16. Atalhos que só quem usa há anos conhece

```bash
# Prefixo de ID basta, se for único
docker stop 3f2                    # em vez do ID completo de 64 caracteres

# O último container criado
docker logs $(docker ps -lq)
docker rm -f $(docker ps -lq)

# Rodar um comando pontual sem sujar a máquina
docker run --rm -it -v "$PWD:/w" -w /w python:3.13-alpine python script.py
docker run --rm -v "$PWD:/w" -w /w node:22-alpine npx prettier --write .

# Um Postgres descartável para 5 minutos de teste
docker run --rm -d --name pg -e POSTGRES_PASSWORD=x -p 5432:5432 postgres:16
docker exec -it pg psql -U postgres

# Ver o Dockerfile aproximado de uma imagem alheia
docker history --no-trunc --format "{{.CreatedBy}}" IMAGEM | tac

# Descobrir por que a imagem está gorda
docker history IMAGEM        # ou a ferramenta 'dive', que é muito melhor
docker run --rm -it -v /var/run/docker.sock:/var/run/docker.sock wagoodman/dive IMAGEM

# Entrar no namespace de rede de outro container (depurar rede sem sujar a imagem)
docker run --rm -it --network container:NOME nicolaka/netshoot

# Parar tudo, de uma vez
docker stop $(docker ps -q)

# Achar o container que está comendo a CPU
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}" | sort -k2 -hr

# Ver o processo do container no HOST (prova de que é só um processo)
docker inspect --format '{{.State.Pid}}' NOME
sudo ls -l /proc/$(docker inspect --format '{{.State.Pid}}' NOME)/ns/

# Copiar uma imagem entre máquinas sem registry
docker save img:tag | ssh usuario@destino 'docker load'

# Aquecer o cache de build em CI sem construir
docker buildx build --cache-to type=inline -t app:cache --push .
```

---

## Autoteste

1. Qual é a diferença entre `--restart always` e `--restart unless-stopped`? Em que cenário ela
   aparece?
2. Um container saiu com código 137. Qual é a causa mais provável e qual comando confirma?
3. Por que `docker run --link` está obsoleto e o que o substituiu?
4. `ENTRYPOINT ["python"]` + `CMD ["app.py"]`: o que executa `docker run img teste.py`?
5. Você precisa de um token do npm durante o build. Por que `--build-arg` é errado e o que usar?
6. Na rede bridge **padrão**, `ping outro-container` funciona? E numa rede criada por você?
7. Qual é a diferença entre `docker compose exec` e `docker compose run`, e quando cada um?
8. Qual comando mostra o YAML final do Compose com todas as sobreposições resolvidas?
9. Por que `-p 5432:5432` num Postgres de desenvolvimento é perigoso, e qual é a forma segura?
10. Cite três comandos que apagam dados sem pedir confirmação.
