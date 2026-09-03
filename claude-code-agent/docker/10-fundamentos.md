# 10 · Fundamentos — vocabulário, modelos mentais e definições formais

`Nível: iniciante → intermediário` · `Última atualização: 11/08/2026`

Este é o arquivo que transforma "eu sei rodar `docker run`" em "eu sei o que está acontecendo".
Tudo aqui é definido antes de ser usado.

---

## 1. A definição formal de container

> **Container** é um ou mais processos executando em um sistema operacional hospedeiro, sob um
> conjunto de restrições impostas pelo kernel, das quais três eixos são essenciais:
> **isolamento de visão** (namespaces), **limitação de consumo** (cgroups) e **redução de
> privilégio** (capabilities, seccomp, LSM), executando a partir de um **sistema de arquivos
> raiz próprio**, montado a partir de uma imagem.

Cada elemento dessa definição responde a uma pergunta:

| Elemento | Pergunta que responde |
|---|---|
| "um ou mais processos" | O container **é** processo. Não é máquina, não é servidor |
| "sistema operacional hospedeiro" | O kernel é **compartilhado**. Daí toda a economia e todo o risco |
| "isolamento de visão" | O que o processo enxerga (PIDs, arquivos, rede, hostname) |
| "limitação de consumo" | Quanto ele pode usar (CPU, RAM, I/O, número de processos) |
| "redução de privilégio" | O que ele pode fazer (chamadas de sistema, operações privilegiadas) |
| "sistema de arquivos raiz próprio" | De onde vêm os arquivos que ele vê como `/` |

**O que a definição NÃO diz, e é o erro conceitual mais comum:** ela não diz "máquina virtual
leve". Não há virtualização. Não há kernel próprio. Não há hardware emulado.

---

## 2. O modelo mental correto

Guarde esta imagem:

```
    O QUE VOCÊ VÊ                     O QUE O KERNEL VÊ
  ┌──────────────────┐            ┌───────────────────────────────┐
  │   "um container" │            │ processo PID 4711             │
  │   com seu Linux  │    ≡       │  ├─ mnt ns: raiz em /var/...  │
  │   isolado        │            │  ├─ pid ns: acha que é PID 1  │
  │                  │            │  ├─ net ns: placa virtual     │
  └──────────────────┘            │  ├─ cgroup: máx 512MB         │
                                  │  └─ caps: sem CAP_SYS_ADMIN   │
                                  └───────────────────────────────┘
```

Prove você mesmo, em Linux:

```bash
docker run -d --name prova nginx:alpine
PID=$(docker inspect --format '{{.State.Pid}}' prova)

ps -p $PID -o pid,ppid,cmd          # o processo do container, visto do host
sudo ls -l /proc/$PID/ns/           # os namespaces dele
sudo cat /proc/$PID/cgroup          # o cgroup ao qual pertence
sudo ls /proc/$PID/root/            # o sistema de arquivos que ELE vê como /

docker rm -f prova
```

Você acabou de olhar "dentro" do container **sem usar o Docker**. Isso não é curiosidade: é a
prova de que não há mágica, e é como se depura quando o `docker exec` não funciona.

---

## 3. Os quatro substantivos e como eles se relacionam

```
  Dockerfile  ──docker build──▶  Imagem  ──docker push──▶  Registry
   (receita)                    (pacote)                   (estante)
                                   │                          │
                              docker run                 docker pull
                                   │                          │
                                   ▼                          ▼
                              Container                    Imagem
                            (processo vivo)              (em outra máquina)
```

| Substantivo | Natureza | Vive onde | Some quando |
|---|---|---|---|
| **Dockerfile** | Texto | No seu repositório Git | Você apaga o arquivo |
| **Imagem** | Dado imutável, endereçado por conteúdo | Disco local + registry | Você faz `docker rmi` |
| **Container** | Processo + camada de escrita | Memória + disco local | Você faz `docker rm` |
| **Volume** | Dado mutável | Disco, fora das camadas | Você faz `docker volume rm` |

**A regra que evita perda de dados:** só o **volume** é feito para durar. Todo o resto é
descartável por projeto.

---

## 4. Imagem: pilha de camadas endereçadas por conteúdo

Uma imagem não é um arquivo único. É uma **pilha ordenada de camadas** (*layers*), cada uma
sendo um conjunto de alterações no sistema de arquivos, mais um **manifesto** que descreve a
pilha e a configuração.

```
   ┌──────────────────────────────────┐  ← camada de escrita (do CONTAINER, efêmera)
   ├──────────────────────────────────┤
   │ COPY src/ /app/src               │  camada 4  (2 MB)
   ├──────────────────────────────────┤
   │ RUN npm ci                       │  camada 3  (180 MB)
   ├──────────────────────────────────┤
   │ COPY package.json .              │  camada 2  (4 KB)
   ├──────────────────────────────────┤
   │ FROM node:22-alpine              │  camada 1  (50 MB)   ← compartilhada
   └──────────────────────────────────┘
              ↓ união (OverlayFS)
        o processo vê UM sistema de arquivos
```

Três propriedades decorrem disso, e todas têm consequência prática:

**(a) Camadas são identificadas pelo hash do próprio conteúdo.** Duas imagens que usam
`node:22-alpine` **compartilham fisicamente** aquela camada no disco. Baixar a segunda imagem
custa quase nada. É por isso que padronizar a imagem base numa equipe economiza gigabytes.

**(b) Camadas são somente leitura; só a do container é escrevível.** Quando o processo escreve
em um arquivo que veio de uma camada inferior, o sistema faz **copy-on-write**: copia o arquivo
para a camada superior e escreve na cópia. Arquivo grande = primeira escrita cara.

**(c) Apagar não diminui.** `RUN rm -rf /cache` cria uma camada que **marca** o arquivo como
apagado (um *whiteout*), mas a camada anterior, com o arquivo, continua na imagem. Por isso:

```dockerfile
# ❌ a imagem continua carregando o cache do apt
RUN apt-get update && apt-get install -y curl
RUN rm -rf /var/lib/apt/lists/*

# ✅ tudo numa camada só: o apagado nunca chega a existir numa camada final
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*
```

E é por isso que **segredo apagado num `RUN` posterior continua recuperável** — o assunto do
[exemplo 10](06-exemplos.md#10-segredo-no-build-sem-vazar-na-imagem).

Detalhes completos em [12-imagens-e-camadas.md](12-imagens-e-camadas.md).

---

## 5. Namespaces: o isolamento de visão

Um **namespace** é um recurso do kernel Linux que faz um conjunto de processos ter uma visão
própria de um recurso global do sistema.

| Namespace | Isola | Efeito visível | Ano no kernel |
|---|---|---|---|
| `mnt` | Pontos de montagem | O container tem seu próprio `/` | 2002 (2.4.19) |
| `uts` | Hostname e domínio | `hostname` devolve o ID do container | 2006 (2.6.19) |
| `ipc` | Memória compartilhada, filas | Processos não veem IPC de fora | 2006 (2.6.19) |
| `pid` | Tabela de processos | O app é PID 1; não enxerga o host | 2008 (2.6.24) |
| `net` | Pilha de rede inteira | IP, rotas, iptables e portas próprios | 2009 (2.6.29) |
| `user` | Mapeamento de UID/GID | Root dentro ≠ root fora — base do rootless | 2013 (3.8) |
| `cgroup` | Visão da hierarquia de cgroups | Não vê os limites dos outros | 2016 (4.6) |
| `time` | Relógios monotônico e de boot | Raro; usado em migração de processos | 2020 (5.6) |

A chamada de sistema que os cria é `clone()` com as flags `CLONE_NEW*`, ou `unshare()`.

Você pode criar um container "à mão", sem Docker, para ver que não há truque:

```bash
sudo unshare --pid --fork --mount-proc --uts --net --ipc bash
# você está num "container" agora:
hostname container-manual
ps aux          # só o bash e o ps
ip addr         # só o loopback, sem rede
exit
```

Isso é 80% do que o `docker run` faz. Os outros 20% são a imagem, os cgroups e a rede.

Aprofundamento: [13-isolamento-namespaces-cgroups.md](13-isolamento-namespaces-cgroups.md).

---

## 6. cgroups: a limitação de consumo

**cgroup** = *control group*. Agrupa processos e aplica limites e contabilidade sobre recursos.

| Controlador | Limita | Flag do Docker |
|---|---|---|
| `memory` | RAM e swap | `-m 512m`, `--memory-swap` |
| `cpu` | Tempo de CPU | `--cpus`, `--cpu-shares` |
| `cpuset` | Quais núcleos | `--cpuset-cpus` |
| `io` | Vazão de disco | `--device-read-bps` |
| `pids` | Número de processos | `--pids-limit` |

**cgroup v1 vs v2:** a v2 unifica todos os controladores numa hierarquia única, com semântica
consistente. É o padrão em distros modernas desde ~2021 e é o que você deve usar. Alguns
recursos (limites de I/O confiáveis, contabilidade de memória precisa) **só funcionam bem na
v2**.

```bash
stat -fc %T /sys/fs/cgroup/
# cgroup2fs → v2 (bom)  ·  tmpfs → v1 (legado)
```

### A consequência que morde: o OOM killer

Quando um container excede o limite de memória, o kernel **mata** o processo — não devolve erro
de alocação, não avisa o app. Você vê apenas exit code 137.

```bash
docker inspect --format '{{.State.OOMKilled}} {{.State.ExitCode}}' NOME
# true 137  → confirmado
```

E um detalhe que causa horas de confusão: **muitas runtimes de linguagem não enxergam o limite
do cgroup**, e sim a RAM total do host. Uma JVM antiga num container de 512 MB podia
dimensionar seu heap para 8 GB e ser morta imediatamente. Java 10+ e .NET Core 3+ passaram a
respeitar cgroups; Node e Python ainda exigem configuração explícita
(`--max-old-space-size`, por exemplo).

---

## 7. Capabilities, seccomp e LSM: a redução de privilégio

Historicamente, o Linux tinha dois estados: root (pode tudo) e não-root (não pode quase nada).
As **capabilities** quebraram o poder do root em ~40 permissões independentes.

| Capability | Permite | O Docker dá por padrão? |
|---|---|---|
| `CAP_NET_BIND_SERVICE` | Escutar em porta < 1024 | Sim |
| `CAP_CHOWN` | Mudar dono de arquivo | Sim |
| `CAP_SETUID` / `CAP_SETGID` | Trocar de usuário | Sim |
| `CAP_NET_RAW` | Pacotes crus (`ping`, ARP spoofing) | Sim (discutível) |
| `CAP_SYS_ADMIN` | "O novo root": montar, namespaces, quase tudo | **Não** |
| `CAP_SYS_PTRACE` | Depurar outros processos | Não |
| `CAP_SYS_MODULE` | Carregar módulos do kernel | Não |

O Docker mantém 14 capabilities por padrão, de ~40. A boa prática é ir mais longe:

```bash
docker run --cap-drop=ALL --cap-add=NET_BIND_SERVICE minha-app
```

**seccomp** (*secure computing mode*) filtra **chamadas de sistema**. O perfil padrão do Docker
bloqueia cerca de 40 das ~350 syscalls — as historicamente exploráveis (`kexec_load`,
`mount`, `ptrace` em certos contextos). Rodar com `--security-opt seccomp=unconfined` remove
esse filtro e é um retrocesso relevante de segurança.

**LSM** (*Linux Security Modules*): AppArmor (Debian/Ubuntu) e SELinux (Fedora/RHEL) aplicam
uma camada adicional, de controle de acesso obrigatório. É o SELinux que exige `:z`/`:Z` em
bind mounts no Fedora.

Aprofundamento: [20-seguranca.md](20-seguranca.md).

---

## 8. A arquitetura do Docker: quem faz o quê

Muita gente acha que "Docker" é um programa. São pelo menos quatro, em camadas:

```
   docker (CLI)                      ← o que você digita
        │  API HTTP sobre socket Unix
        ▼
   dockerd (daemon)                  ← gerencia imagens, redes, volumes, builds
        │  gRPC
        ▼
   containerd                        ← ciclo de vida do container, pull de imagem
        │
        ├── containerd-shim-runc-v2  ← um shim POR container; sobrevive ao restart do daemon
        │        │
        │        ▼
        │   runc                     ← executa: cria namespaces/cgroups, faz exec e SAI
        │        │
        │        ▼
        └──▶  seu processo           ← reparentado ao shim
```

**Por que essa separação importa, em três consequências:**

1. **`runc` executa e sai.** Ele não fica rodando. Depois do `exec`, o processo do container é
   filho do *shim*, não do daemon.
2. **Por isso você pode reiniciar o `dockerd` sem matar os containers** (com `live-restore`
   habilitado). O shim mantém tudo de pé.
3. **`containerd` e `runc` são padrões da indústria**, doados à CNCF. O Kubernetes fala
   diretamente com o `containerd`, **sem Docker no meio** — foi isso, e não mais que isso, o
   "Kubernetes está removendo o Docker" de 2020, que gerou pânico desproporcional.

Aprofundamento: [14-runtime-e-arquitetura.md](14-runtime-e-arquitetura.md).

---

## 9. OCI: o padrão que impede o aprisionamento

A **Open Container Initiative**, criada em 2015 sob a Linux Foundation, mantém três
especificações:

| Especificação | Define |
|---|---|
| **Image Spec** | O formato da imagem: manifesto, camadas, configuração, digests |
| **Runtime Spec** | O formato do *bundle* e como executá-lo (`config.json` + rootfs) |
| **Distribution Spec** | A API HTTP de um registry (push, pull, autenticação) |

A consequência prática é a mais importante do ecossistema: **imagem construída com Docker roda
em Podman, containerd, CRI-O, Kubernetes ou AWS Fargate**. Você não está preso a um fornecedor.
Foi isso que transformou "container" de produto em infraestrutura comum.

---

## 10. As seis coisas que um container **não** é

Corrigir esses mal-entendidos economiza semanas:

| Mito | Realidade |
|---|---|
| "É uma VM leve" | Não há virtualização nem kernel próprio. É um processo restrito |
| "É seguro por padrão" | O padrão é razoável, não é isolamento forte. Kernel compartilhado = superfície compartilhada |
| "É imutável" | A **imagem** é imutável. O **container** tem uma camada de escrita mutável |
| "Container é para microserviço" | Container é embalagem. Microserviço é decisão organizacional. São independentes |
| "Docker é o container" | Docker é uma implementação. O padrão é OCI; há várias implementações |
| "Container não tem estado" | Ele **pode** ter estado — em volume. O que ele não deve ter é estado na camada de escrita |

---

## 11. O ciclo de vida completo de um container

```
       docker create              docker start
  [imagem] ──────────▶ [created] ──────────▶ [running] ──┐
                            ▲                    │       │ docker pause
                            │                    │       ▼
                    docker start                 │   [paused]
                            │                    │       │ docker unpause
                        [exited] ◀───────────────┘◀──────┘
                            │      docker stop / processo terminou
                            │      docker kill
                            │
                        docker rm
                            │
                            ▼
                        [removido]   ← camada de escrita apagada
```

**`docker run` = `create` + `start`.**
**Um container parado ainda ocupa disco** (a camada de escrita e os logs). É por isso que
`docker ps -a` costuma revelar dezenas de containers esquecidos consumindo espaço.

**Estado `restarting`**: se a política de reinício estiver ativa e o processo falhar
repetidamente, o container fica em laço. O Docker aplica *backoff* exponencial (100 ms, 200 ms,
400 ms…) para não derrubar a máquina. `docker ps` mostrando `Restarting (1) 3 seconds ago` é o
sintoma clássico de app que morre no boot — e `docker logs` mostra o porquê.

---

## 12. Os cinco modelos mentais que valem mais que qualquer comando

**1. "Container é processo."** Toda dúvida sobre ciclo de vida se resolve perguntando: *o que o
PID 1 está fazendo?* Container "não sobe" = processo saiu. Container "não morre" = processo
ignora sinal.

**2. "A imagem é o artefato; o container é a execução."** Deploy é trocar qual imagem executa.
Rollback é apontar para a imagem anterior. Se você está fazendo `ssh` no servidor e editando
arquivo dentro de um container, o modelo está errado.

**3. "Camada é cache."** A ordem das instruções no Dockerfile determina o tempo de build. O que
muda pouco vai em cima; o que muda a cada commit vai embaixo.

**4. "Tudo é efêmero, exceto o que você declarou que não é."** Se um dado importa, ele está em
volume — ou está por um fio.

**5. "O kernel é compartilhado."** Toda decisão de segurança em container decorre desta frase.
Se o isolamento precisa ser forte, é preciso outra barreira (VM, micro-VM, gVisor, Kata).

---

## 13. Os cinco porquês aplicados: por que containers iniciam tão rápido?

Seguindo a regra dos cinco porquês do preset, até uma parada legítima:

**1. Por que um container inicia em milissegundos e uma VM em segundos?**
Porque o container não faz boot. É um `fork` + `exec` de um processo, com algumas chamadas de
configuração antes.

**2. Por que a VM precisa dar boot?**
Porque ela tem um kernel próprio, que precisa inicializar hardware (virtual), montar sistemas
de arquivos, iniciar o `init` e uma árvore de serviços.

**3. Por que o container não precisa de kernel próprio?**
Porque namespaces e cgroups permitem que **o mesmo** kernel apresente visões e limites
diferentes para conjuntos de processos distintos. O isolamento é feito na estrutura de dados do
kernel, não em hardware.

**4. Por que o kernel foi construído com essa capacidade?**
Por uma linhagem de necessidades reais: `chroot` (1979, isolar visão do sistema de arquivos em
testes de compilação), FreeBSD Jails (2000, hospedagem compartilhada), Solaris Zones (2004), e
sobretudo o **Process Containers do Google** (2006, Paul Menage e Rohit Seth), renomeado para
cgroups e mesclado no kernel 2.6.24 em 2008. O Google precisava rodar milhares de trabalhos por
máquina com isolamento de desempenho — e VMs eram caras demais para essa densidade.

**5. Por que VMs eram caras demais para essa densidade?**
Porque cada VM duplica o kernel, o `init`, os daemons e o cache de página em memória. Com
milhares de trabalhos por máquina, essa duplicação consome uma fração dominante da RAM e do
CPU. **Aqui a cadeia chega a um trade-off econômico explícito:** a densidade que o Google
precisava só era alcançável abrindo mão do isolamento por hardware — decisão consciente, tomada
num ambiente onde todo o código executado era da própria empresa, e portanto o modelo de ameaça
era diferente do de um provedor de nuvem pública.

E é exatamente por isso que provedores que rodam **código de terceiros desconhecidos** (AWS
Lambda, Cloudflare Workers, Fly.io) reintroduziram uma barreira: micro-VMs (Firecracker),
sandbox de syscalls (gVisor) ou isolados de V8. A escolha do Google não era universal — era
apropriada ao contexto dele.

---

## 14. Vocabulário consolidado

| Termo | Definição |
|---|---|
| **Imagem** | Pilha imutável de camadas + configuração, identificada por digest |
| **Camada** (*layer*) | Conjunto de alterações no sistema de arquivos, endereçado por hash de conteúdo |
| **Manifesto** | Documento JSON que lista as camadas e a configuração de uma imagem |
| **Manifest list / índice** | Manifesto que aponta para vários manifestos, um por arquitetura (multi-arch) |
| **Digest** | `sha256:...` do conteúdo. Imutável, ao contrário da tag |
| **Tag** | Rótulo humano e **mutável** apontando para um digest |
| **Container** | Processo(s) isolado(s) executando a partir de uma imagem |
| **Camada de escrita** | Camada mutável e efêmera, exclusiva de cada container |
| **Copy-on-write** | Estratégia de copiar o arquivo para a camada superior na primeira escrita |
| **Volume** | Armazenamento gerenciado, fora das camadas, que sobrevive ao container |
| **Bind mount** | Diretório do host montado dentro do container |
| **Registry** | Servidor que armazena e distribui imagens |
| **Repositório** | Conjunto de tags de uma mesma imagem num registry |
| **Namespace** | Recurso do kernel que isola a visão de um recurso global |
| **cgroup** | Recurso do kernel que limita e contabiliza consumo |
| **Capability** | Fração do poder do root, concedida individualmente |
| **seccomp** | Filtro de chamadas de sistema |
| **runtime** | Programa que executa o container (`runc`, `crun`, `youki`, `gVisor`, `kata`) |
| **shim** | Processo intermediário que mantém o container vivo entre o daemon e o runtime |
| **OCI** | Padrão aberto de imagem, runtime e distribuição |
| **Orquestrador** | Sistema que agenda containers num conjunto de máquinas |

Lista completa em [GLOSSARIO.md](GLOSSARIO.md).

---

## Autoteste

1. Escreva a definição formal de container sem consultar, e explique cada uma das cinco partes.
2. Por que `RUN rm -rf /cache` numa linha separada não reduz o tamanho da imagem?
3. Qual comando prova, sem usar o Docker, que um container é apenas um processo do host?
4. Diferencie namespace de cgroup em uma frase cada, com um exemplo de problema que cada um
   resolve.
5. Seu container Java num limite de 512 MB é morto com exit 137. Cite duas causas possíveis.
6. Por que `runc` não aparece no `ps` de um container em execução?
7. O que exatamente aconteceu em 2020 quando "o Kubernetes removeu o Docker"?
8. Cite as três especificações da OCI e o que cada uma torna possível.
9. Percorra os cinco porquês de "por que containers iniciam rápido" até a parada legítima. Que
   tipo de parada é (lei física, decisão histórica, trade-off econômico ou convenção)?
10. Um container está `Restarting (1) 3 seconds ago`. Qual é o diagnóstico e qual comando você
    roda primeiro?
