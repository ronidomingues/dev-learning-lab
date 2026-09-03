# Glossário

> Todos os termos técnicos usados no curso. Termos em inglês mantidos como o
> campo os usa, com tradução na primeira ocorrência.

**ABI** (*Application Binary Interface*) — contrato binário entre um programa
compilado e a biblioteca/interpretador. Extensões C do Python são compiladas para
uma ABI específica (`cpython-312`), por isso builder e runtime precisam da mesma
versão de Python.

**Alpine** — distribuição Linux minimalista usada como imagem base (~5 MB). Usa
`musl` no lugar da `glibc`, o que quebra wheels binárias de Python.

**Bind mount** — montagem de um diretório ou arquivo **do host** dentro do
container. Você escolhe o caminho e enxerga os arquivos normalmente.
Ver [módulo 04](04-armazenamento/bind-mount-vs-volume.md).

**Bridge** — modo de rede padrão. O Docker cria uma ponte virtual e dá IP privado
a cada container, com NAT para a internet.

**Build context** (*contexto de build*) — o diretório enviado ao daemon no
`docker build .`. Um `COPY` só enxerga o que está dentro dele.

**BuildKit** — o construtor moderno de imagens do Docker, padrão desde a versão
23. Habilita `--mount=type=cache`, `--mount=type=secret` e execução paralela de
estágios.

**Camada** (*layer*) — resultado imutável de uma instrução do Dockerfile que
altera o filesystem. Camadas são compartilhadas entre imagens, cacheadas e
**aditivas** (apagar em camada posterior não reduz o tamanho).

**Capability** — permissão granular do kernel Linux (ex.: `CAP_NET_RAW`,
`CAP_CHOWN`). O Docker concede ~14 por padrão; `cap_drop: ALL` remove todas.

**cgroups** (*control groups*) — recurso do kernel Linux que limita CPU, memória
e I/O de um grupo de processos. Contribuído pelo Google em 2007. É o que
implementa os limites de recurso do Docker.

**Compose** — ferramenta para definir e rodar múltiplos containers em **uma
máquina**, a partir de um arquivo YAML. A v2 (plugin `docker compose`) substituiu
a v1 (`docker-compose`), cujo fim de vida foi em julho/2023.

**Container** — um processo em execução a partir de uma imagem, com namespaces e
cgroups próprios. Está para a imagem como o objeto está para a classe.

**containerd** — runtime de container de baixo nível usado pelo Docker e,
diretamente, pelo Kubernetes.

**Daemon** (`dockerd`) — o serviço que realmente constrói e roda containers. O
comando `docker` é só um cliente que fala com ele por socket.

**Digest** — hash SHA-256 do conteúdo de uma imagem
(`@sha256:2c941e86...`). É a única referência **imutável**; tags podem mudar de
destino.

**Distroless** — imagem que contém só a aplicação e suas dependências de runtime,
sem shell nem gerenciador de pacotes.

**Dockerfile** — arquivo de texto com as instruções para construir uma imagem.

**`.dockerignore`** — arquivo que define o que **não** entra no build context.
Essencial para build rápido e para não vazar segredo na imagem.

**Entrypoint** — o executável do container. Diferente de `CMD`, argumentos
passados no `docker run` são **anexados** a ele, não o substituem.

**Exit code** — código de saída do processo principal. `137` = SIGKILL (quase
sempre OOM), `143` = SIGTERM, `127` = comando não encontrado.

**Forma exec / forma shell** — `CMD ["a","b"]` (exec) executa direto; `CMD a b`
(shell) executa via `/bin/sh -c`, que **não repassa SIGTERM** — por isso o
`docker stop` demora 10 s e mata com força.

**Healthcheck** — comando que o Docker executa periodicamente para decidir se o
container está `healthy`. Sai com 0 (saudável) ou 1 (não).

**Host (modo de rede)** — o container usa a pilha de rede do host diretamente,
sem isolamento nem NAT. Necessário para descoberta por broadcast (DLNA, mDNS).

**Imagem** — sistema de arquivos empacotado e imutável, em camadas, do qual se
criam containers.

**Interpolação** — substituição de `${VAR}` no arquivo compose, feita **ao ler o
YAML**, com valores do shell ou do `.env`. Não confundir com `environment:`, que
define variáveis **dentro** do container.

**Multi-stage build** — Dockerfile com vários `FROM`, em que estágios de
construção são descartados e só os artefatos escolhidos passam para a imagem
final via `COPY --from=`.

**musl / glibc** — implementações da biblioteca C. Alpine usa `musl`; Debian usa
`glibc`. Wheels binárias de Python geralmente só existem para `glibc`.

**Namespace** — recurso do kernel Linux que dá a um processo uma visão isolada de
PIDs, rede, pontos de montagem, usuários. É o que faz o container "achar" que
está sozinho na máquina.

**NAT** (*Network Address Translation*) — tradução de endereços que permite ao
container sair para a internet com o IP do host. Broadcast **não** atravessa NAT
— daí a necessidade de `--network host` para DLNA.

**OCI** (*Open Container Initiative*) — padrão aberto de formato de imagem e
runtime, o que torna Docker, Podman e containerd intercambiáveis.

**OOM killer** (*Out Of Memory killer*) — mecanismo do kernel que mata processos
quando a memória acaba. Escolhe pelo score, não pelo culpado — por isso o banco
costuma ser a vítima.

**PID 1** — o processo principal do container. O container vive enquanto ele
viver, e é ele quem recebe os sinais do `docker stop`.

**Podman** — alternativa ao Docker, sem daemon e rootless por desenho.

**Registry** — servidor onde imagens são publicadas e baixadas (Docker Hub,
GitHub Container Registry, Harbor).

**Rootless mode** — modo em que o **daemon** do Docker roda como usuário comum,
não como root. Diferente de rodar o **container** como não-root, que é o `USER`.

**runc** — runtime de baixo nível que efetivamente cria o container, usando
namespaces e cgroups.

**Secret** — no Compose, arquivo montado em `/run/secrets/<nome>` num tmpfs. Não
vaza em `docker inspect` nem para subprocessos, mas **não** é criptografado em
repouso fora do Swarm.

**Suite (Debian)** — nome da versão da distribuição (`bullseye`, `bookworm`,
`trixie`). Tags como `python:3.12-slim` mudam de suite sem avisar — por isso o
curso recomenda `python:3.12-slim-trixie`.

**Tag** — rótulo móvel que aponta para uma imagem (`:1.0.0`, `:latest`).
`:latest` **não** significa "mais recente" — é só a tag padrão quando nenhuma é
especificada.

**tmpfs** — sistema de arquivos em RAM. Some no restart. Usado para `/tmp` de
containers com `read_only: true` e para montar secrets.

**Volume anônimo** — volume criado sem nome, geralmente por um `VOLUME` no
Dockerfile sem montagem correspondente. Acumula silenciosamente e enche o disco.

**Volume nomeado** — armazenamento gerenciado pelo Docker em
`/var/lib/docker/volumes/`. Sobrevive à remoção do container e é a escolha certa
para dados que nenhum humano abre na mão.

---
[índice](00-indice.md)
