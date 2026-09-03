# Glossário — Docker e containers

`Todo termo técnico do material, definido.` · `Última atualização: 11/08/2026`

Termos em inglês são mantidos quando é assim que o campo os usa, com a tradução na primeira
menção. Ordenado alfabeticamente.

---

**AppArmor** — *Linux Security Module* usado em Debian/Ubuntu que aplica perfis de controle de
acesso obrigatório a processos, inclusive containers. Ver também [LSM], [seccomp].

**Attestation (atestado)** — declaração assinada sobre uma imagem: como foi construída
(proveniência SLSA), o que contém (SBOM) ou se uma CVE se aplica (VEX). Fica no registry, ligada
ao [digest].

**Base image (imagem base)** — a imagem declarada no primeiro `FROM`, sobre a qual as demais
camadas são empilhadas. Ex.: `alpine`, `node:22-alpine`, `scratch`.

**Bind mount** — montagem de um diretório do host dentro do container, por caminho absoluto.
Usado para código em desenvolvimento. Difere de [volume] por não ser gerenciado pelo Docker.

**Bridge** — driver de rede padrão: uma rede virtual isolada com [NAT]. A bridge padrão não tem
[DNS] interno; redes bridge criadas pelo usuário têm.

**BuildKit** — motor de build moderno do Docker (padrão desde a Engine 23): grafo de
dependências, build paralelo, cache remoto, `--mount=type=secret` e `type=cache`.

**Bundle (OCI)** — o par `config.json` + `rootfs/` que o [runtime] de baixo nível executa.

**Capability** — fração do poder do root concedida individualmente (ex.: `CAP_NET_BIND_SERVICE`
para porta < 1024). O Docker concede 14 das ~40 por padrão.

**cgroup** (*control group*) — recurso do kernel Linux que limita e contabiliza o consumo de
recursos (CPU, memória, I/O, número de processos) de um grupo de processos. A **v2** unifica os
controladores e é o padrão atual.

**CNI** (*Container Network Interface*) — especificação de plugins de rede, usada por
orquestradores.

**Compose** — ferramenta que define e opera aplicações multi-container a partir de um arquivo
YAML (`compose.yaml`). A **v2** (`docker compose`, com espaço) substituiu a v1
(`docker-compose`, com hífen).

**Confidential container** — container cuja memória é cifrada em uso por uma [TEE] (AMD SEV-SNP,
Intel TDX, ARM CCA), protegendo-o até do hipervisor e do operador da nuvem.

**containerd** — [runtime] de alto nível (projeto graduado da CNCF) que gerencia o ciclo de vida
dos containers, o pull de imagens e os snapshots. Usado pelo Docker e diretamente pelo
Kubernetes. Desde a Engine 29, seu *image store* é o padrão em instalações novas.

**Container** — um ou mais processos isolados por [namespaces], limitados por [cgroups] e
restringidos por políticas de segurança, executando a partir de uma [imagem].

**Copy-on-write (CoW)** — estratégia em que um arquivo de uma camada inferior só é copiado para a
camada de escrita quando modificado. No [OverlayFS] é por arquivo; em btrfs/zfs, por bloco.

**CRI** (*Container Runtime Interface*) — contrato entre o kubelet do Kubernetes e o runtime.
Implementado por containerd e CRI-O; **não** pelo Docker Engine (origem do episódio do
[dockershim]).

**crun** — [runtime] de baixo nível escrito em C, mais rápido e leve que o [runc]. Padrão do
Podman no Fedora.

**CVE** (*Common Vulnerabilities and Exposures*) — identificador padronizado de vulnerabilidade
conhecida. [Scanners] reportam CVEs por versão de pacote.

**Digest** — hash SHA-256 do manifesto de uma imagem (`sha256:...`). Imutável e verificável, ao
contrário da [tag]. Deploys de produção devem referenciar o digest.

**distroless** — imagens mínimas do Google, sem shell nem gerenciador de pacotes, contendo só o
runtime da linguagem. Menor superfície de ataque; a variante `:debug` traz shell.

**DNS interno** — o resolvedor em `127.0.0.11` que o Docker embute em redes definidas pelo
usuário, resolvendo nomes de container/serviço para IP. Ausente na bridge padrão.

**Dockerfile** — arquivo de texto com a receita de construção de uma [imagem].

**dockershim** — adaptador (removido do Kubernetes em 2022) que permitia ao kubelet falar com o
Docker Engine. Sua remoção foi o "Kubernetes está removendo o Docker" de 2020.

**dockerd** — o daemon do Docker: gerencia imagens, containers, redes, volumes e builds; expõe a
API.

**eBPF** — mecanismo do kernel Linux para executar programas verificados sem módulos. Base de
Cilium (rede), Tetragon e Falco (segurança), e de observabilidade sem instrumentação.

**Egress** — tráfego de saída. O principal custo variável de registries e nuvens; imagens
menores reduzem-no.

**ENTRYPOINT** — instrução do Dockerfile que define o executável fixo do container; o [CMD] vira
seu argumento padrão.

**EXPOSE** — instrução que **documenta** a porta do container. Não publica nada — quem publica é
`-p` ou `ports:`.

**Firecracker** — [micro-VM] minimalista da AWS, base do Lambda e do Fargate; boot em ~125 ms.

**gVisor** — [runtime] que implementa um kernel em espaço de usuário (`runsc`), interceptando
syscalls e reduzindo a superfície de kernel. Base do Google Cloud Run.

**HEALTHCHECK** — instrução/definição que informa como verificar se o container está saudável.
Habilita `condition: service_healthy` no Compose.

**Image store** — o subsistema que armazena camadas e conteúdo de imagens. O *containerd image
store* é o padrão em instalações novas desde a Engine 29, substituindo o backend histórico.

**Imagem** — pacote imutável, em [camadas], com o sistema de arquivos e a configuração de uma
aplicação. Identificada por [digest].

**Init (PID 1)** — o primeiro processo de um [namespace] de PID. Recebe tratamento especial do
kernel: sinais sem tratador são ignorados, e sua morte encerra o namespace. [tini] é um init
mínimo para containers.

**Kata Containers** — [runtime] que executa cada container numa [micro-VM] com kernel próprio,
oferecendo isolamento de VM com interface de container.

**Layer (camada)** — conjunto de alterações no sistema de arquivos, endereçado por hash de
conteúdo. Imagens são pilhas de camadas reaproveitáveis.

**Lazy pulling** — iniciar um container antes de a [imagem] estar inteiramente baixada, buscando
blocos sob demanda (eStargz, SOCI, Nydus). Relevante para imagens grandes, como as de IA.

**Liveness** — sonda que responde "o processo está de pé?". Falha → **reiniciar**. Distinta de
[readiness].

**LSM** (*Linux Security Module*) — arcabouço do kernel para controle de acesso obrigatório.
Implementações: [AppArmor], [SELinux].

**Manifest (manifesto)** — documento JSON que lista as camadas e a configuração de uma imagem
para uma arquitetura.

**Manifest list / índice** — manifesto que aponta para vários manifestos, um por arquitetura
(base do multi-arch).

**Micro-VM** — máquina virtual minimalista, de boot rápido e footprint reduzido, usada para dar
isolamento de VM a containers ([Firecracker], [Kata]).

**Moby** — o projeto upstream de código aberto do qual o Docker Engine é montado.

**Multi-stage build** — Dockerfile com vários `FROM`, em que artefatos de um estágio são copiados
para outro, mantendo o toolchain fora da imagem final.

**Namespace** — recurso do kernel Linux que dá a um conjunto de processos uma visão própria de um
recurso global (PIDs, montagens, rede, hostname, IPC, usuários, cgroups, tempo).

**NAT** (*Network Address Translation*) — tradução de endereços que permite aos containers na
[bridge] alcançarem a rede externa e receberem portas publicadas.

**nftables** — sucessor do iptables para firewall no Linux. Backend **experimental** no Docker
desde a Engine 29.

**OCI** (*Open Container Initiative*) — organização sob a Linux Foundation que mantém as
especificações de [imagem], [runtime] e distribuição. A razão pela qual imagens são portáteis
entre runtimes.

**OOM killer** (*Out Of Memory*) — mecanismo do kernel que mata um processo que excede o limite
de memória do [cgroup]. Resulta em exit code 137.

**Orquestrador** — sistema que agenda e gerencia containers em várias máquinas (Kubernetes,
Swarm, Nomad).

**OverlayFS** — sistema de arquivos de união do kernel usado pelo driver `overlay2` para
apresentar as camadas empilhadas como um único sistema de arquivos.

**PID namespace** — [namespace] que isola a tabela de processos; dentro dele, o processo
principal é [PID 1].

**Podman** — engine de containers sem daemon e rootless por padrão, com CLI compatível com a do
Docker.

**Privileged (`--privileged`)** — modo que concede todas as [capabilities], desliga [seccomp] e
[LSM] e dá acesso a todos os dispositivos. Equivale a root no host.

**Provenance (proveniência)** — atestado de como, onde e a partir de quê uma imagem foi
construída. Formalizado pelo [SLSA].

**Readiness** — sonda que responde "consigo atender agora?". Falha → **tirar do balanceamento**,
sem reiniciar. Distinta de [liveness].

**Registry** — servidor que armazena e distribui imagens (Docker Hub, GHCR, Quay, ECR). Hoje,
também depósito de artefatos ([SBOM], assinaturas).

**Rootless** — modo em que o daemon e os containers rodam como usuário sem privilégio, via [user
namespace]. Reduz o dano de um escape.

**runc** — [runtime] de baixo nível de referência da [OCI]: cria namespaces e cgroups, aplica
segurança, faz `execve` e sai.

**Runtime** — programa que executa containers. De **baixo nível**: runc, crun, youki, runsc,
kata. De **alto nível**: containerd, CRI-O.

**SBOM** (*Software Bill of Materials*) — inventário de todos os componentes e versões de uma
imagem. Formatos: [SPDX], [CycloneDX]. Exigido pelo [CRA] da UE.

**Scanner** — ferramenta que analisa uma imagem em busca de [CVEs], segredos ou má configuração
(Trivy, Grype, Docker Scout).

**scratch** — imagem base vazia (0 byte). Usada para binários estáticos; sem shell, sem libc.

**seccomp** (*secure computing mode*) — filtro de chamadas de sistema. O perfil padrão do Docker
bloqueia ~40 das ~350 syscalls.

**SELinux** — [LSM] usado em Fedora/RHEL. Exige os sufixos `:z`/`:Z` em [bind mounts].

**Shim** — processo intermediário (`containerd-shim-runc-v2`), um por container, que mantém o
container vivo e reporta seu término, permitindo reiniciar o daemon sem derrubá-lo.

**SLSA** (*Supply-chain Levels for Software Artifacts*) — arcabouço de níveis de garantia de
integridade da cadeia de suprimentos.

**Swarm** — modo de orquestração embutido no Docker Engine. Funcional e simples, mas com
desenvolvimento estagnado; perdeu mercado para o Kubernetes.

**tag** — rótulo humano e **mutável** que aponta para um [digest] (ex.: `nginx:alpine`).
`latest` é apenas a tag padrão, não "a mais recente".

**TEE** (*Trusted Execution Environment*) — ambiente de hardware que cifra memória em uso, base
dos [confidential containers].

**tini** — init mínimo (~10 KB) que, como [PID 1], repassa sinais ao processo real e colhe
zumbis. Disponível também via `docker run --init`.

**tmpfs** — sistema de arquivos em RAM. Usado para dados efêmeros e segredos, que somem ao parar
o container.

**Twelve-Factor App** — conjunto de práticas para aplicações em nuvem (config por ambiente, log
em stdout, processos sem estado) fortemente alinhado ao modelo de containers.

**User namespace** — [namespace] que mapeia UIDs/GIDs, permitindo que o root dentro do container
seja um usuário sem privilégio fora. Base do [rootless].

**VEX** (*Vulnerability Exploitability eXchange*) — atestado que declara se uma [CVE] é
explorável em um contexto, reduzindo o ruído dos [scanners].

**veth pair** — par de interfaces virtuais ligadas como um cabo; uma ponta no container (`eth0`),
a outra na [bridge] do host.

**Volume** — armazenamento gerenciado pelo Docker, fora das [camadas], que sobrevive ao
container. Forma correta de guardar estado.

**WASI / WebAssembly (Wasm)** — formato de bytecode portátil e isolado por design, executável em
containers via shim [runwasi]. Ocupa o nicho de funções muito curtas e código não confiável.

**Whiteout** — marcador criado na camada de escrita do [OverlayFS] para "apagar" um arquivo de
camada inferior. O arquivo original continua ocupando espaço na imagem.

**youki** — [runtime] de baixo nível escrito em Rust, com segurança de memória por construção.

---

### Termos de comando frequentes

| Termo | Significado |
|---|---|
| **`-d` / detached** | Rodar em segundo plano |
| **`-it`** | Interativo com terminal (`-i` + `-t`) |
| **`--rm`** | Remover o container ao terminar |
| **Build context** | A pasta enviada ao daemon no `docker build` (o `.` final) |
| **`.dockerignore`** | Arquivo que exclui itens do build context |
| **Exit code 137** | SIGKILL — quase sempre [OOM] |
| **Exit code 143** | SIGTERM — parada normal |
| **`docker compose config`** | Mostra o YAML final resolvido — o melhor depurador de Compose |
