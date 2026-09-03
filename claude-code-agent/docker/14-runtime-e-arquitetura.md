# 14 · Runtime e arquitetura — quem faz o quê, da CLI ao processo

`Nível: avançado` · `Última atualização: 11/08/2026`

Rastrear um `docker run` do teclado até a chamada `execve()` é o que dissolve as últimas
caixas-pretas.

---

## 1. As camadas, e por que existem tantas

```
  ┌──────────────────────────────────────────────────────────────────┐
  │  docker CLI            binário Go; fala a API HTTP do daemon      │
  └──────────────┬───────────────────────────────────────────────────┘
                 │ HTTP sobre /var/run/docker.sock (ou TCP, ou SSH)
  ┌──────────────▼───────────────────────────────────────────────────┐
  │  dockerd (daemon)      imagens, redes, volumes, builds, API       │
  │                        ── o "gerente"; NÃO executa containers ──  │
  └──────────────┬───────────────────────────────────────────────────┘
                 │ gRPC sobre /run/containerd/containerd.sock
  ┌──────────────▼───────────────────────────────────────────────────┐
  │  containerd            ciclo de vida, pull, snapshots, CRI        │
  │                        ── runtime de ALTO nível ──                │
  └──────────────┬───────────────────────────────────────────────────┘
                 │ exec de um shim por container
  ┌──────────────▼───────────────────────────────────────────────────┐
  │  containerd-shim-runc-v2   um POR container; mantém stdio e       │
  │                            reporta o exit; sobrevive ao daemon    │
  └──────────────┬───────────────────────────────────────────────────┘
                 │ exec
  ┌──────────────▼───────────────────────────────────────────────────┐
  │  runc                  runtime de BAIXO nível: cria namespaces,   │
  │                        cgroups, aplica seccomp, faz execve E SAI  │
  └──────────────┬───────────────────────────────────────────────────┘
                 │ execve()
  ┌──────────────▼───────────────────────────────────────────────────┐
  │  SEU PROCESSO          reparentado ao shim                        │
  └──────────────────────────────────────────────────────────────────┘
```

Veja a árvore real:

```bash
docker run -d --name arv nginx:alpine
PID=$(docker inspect -f '{{.State.Pid}}' arv)
ps -o pid,ppid,cmd --forest -p $PID $(ps -o ppid= -p $PID)
pstree -p $(pgrep -f containerd-shim | head -1)
docker rm -f arv
```

Note o que **não** aparece: o `runc`. Ele já terminou.

### Por que essa separação — as cinco razões

1. **`runc` executa e sai.** É um programa de vida curta que faz `clone()`, configura tudo e
   `execve()`. Depois, some. Só o shim permanece.
2. **O shim mantém o container vivo se o daemon reiniciar.** Com `live-restore` ativado,
   `systemctl restart docker` **não derruba os containers** — o shim segura o `stdio` e a
   contabilidade do exit code, e o daemon reconecta.
3. **Padronização.** `runc` implementa a OCI Runtime Spec; `containerd` implementa a CRI do
   Kubernetes. Ambos podem ser trocados por implementações alternativas.
4. **Responsabilidade única.** `containerd` não sabe construir imagem, não sabe Compose, não
   tem opinião sobre rede. Isso o tornou adotável por Kubernetes, nerdctl, Rancher e AWS.
5. **Modelo de segurança.** Menos código rodando como root permanentemente.

```bash
# Habilite live-restore e comprove
sudo tee /etc/docker/daemon.json >/dev/null <<'EOF'
{ "live-restore": true }
EOF
sudo systemctl restart docker

docker run -d --name sobrevivente nginx:alpine
sudo systemctl restart docker
docker ps      # o container continua "Up" — não reiniciou
docker rm -f sobrevivente
```

> **Limitação de `live-restore`:** não funciona em Swarm mode, e uma mudança de configuração de
> rede do daemon ainda exige derrubar os containers.

---

## 2. O que acontece, passo a passo, num `docker run -d -p 8080:80 nginx:alpine`

| # | Quem | O que faz |
|---|---|---|
| 1 | CLI | Traduz as flags e faz `POST /containers/create` no socket |
| 2 | dockerd | Resolve `nginx:alpine` → `docker.io/library/nginx:alpine` |
| 3 | dockerd | Não achou local: pede à containerd para baixar |
| 4 | containerd | Autentica no registry, baixa **manifesto**, depois cada **camada** ausente |
| 5 | containerd | Descompacta as camadas em *snapshots* (overlay2 ou o snapshotter do containerd) |
| 6 | dockerd | Cria o registro do container, aloca IP na bridge, prepara o volume/rootfs |
| 7 | dockerd | Escreve as regras de NAT (iptables ou nftables) para o `-p 8080:80` |
| 8 | dockerd | `POST /containers/{id}/start` → chama a containerd |
| 9 | containerd | Monta o rootfs (`merged` do OverlayFS) e gera o `config.json` da OCI |
| 10 | containerd | Faz `exec` de `containerd-shim-runc-v2` |
| 11 | shim | Faz `exec` de `runc create` e `runc start` |
| 12 | runc | `clone()` com as flags de namespace; entra no cgroup; aplica capabilities, seccomp, AppArmor; faz `pivot_root`; `execve("/docker-entrypoint.sh")` |
| 13 | runc | **Termina.** O processo do nginx é reparentado ao shim |
| 14 | shim | Captura stdout/stderr e os entrega ao driver de log do daemon |

Você pode observar boa parte disso ao vivo:

```bash
docker events &                    # eventos do daemon
sudo journalctl -u docker -f &     # log do daemon
docker run --rm alpine echo oi
kill %1 %2
```

---

## 3. O `config.json` da OCI — o contrato

Todo container é, para o `runc`, um **bundle**: um diretório com `config.json` + `rootfs/`.

```bash
# Veja o config.json real que o Docker gerou para um container em execução
docker run -d --name espiar --memory 256m --cap-drop=ALL nginx:alpine
ID=$(docker inspect -f '{{.Id}}' espiar)
sudo cat /run/containerd/io.containerd.runtime.v2.task/moby/$ID/config.json | jq '{process: .process.args, user: .process.user, caps: .process.capabilities.effective, ns: [.linux.namespaces[].type], mem: .linux.resources.memory}'
docker rm -f espiar
```

Estrutura essencial:

```json
{
  "ociVersion": "1.2.0",
  "process": {
    "terminal": false,
    "user": { "uid": 101, "gid": 101 },
    "args": ["nginx", "-g", "daemon off;"],
    "env": ["PATH=/usr/local/sbin:...", "NGINX_VERSION=1.27.0"],
    "cwd": "/",
    "capabilities": { "effective": ["CAP_CHOWN", "CAP_NET_BIND_SERVICE"] },
    "noNewPrivileges": true
  },
  "root": { "path": "rootfs", "readonly": false },
  "hostname": "a1b2c3d4",
  "mounts": [ { "destination": "/proc", "type": "proc", "source": "proc" } ],
  "linux": {
    "resources": {
      "memory": { "limit": 268435456 },
      "cpu": { "quota": 50000, "period": 100000 },
      "pids": { "limit": 200 }
    },
    "namespaces": [
      { "type": "pid" }, { "type": "network" }, { "type": "ipc" },
      { "type": "uts" }, { "type": "mount" }, { "type": "cgroup" }
    ],
    "seccomp": { "defaultAction": "SCMP_ACT_ERRNO", "syscalls": [ /* ... */ ] }
  }
}
```

**Este arquivo é o contrato da OCI Runtime Spec.** Qualquer runtime que o entenda pode executar
o container: `runc`, `crun`, `youki`, `runsc` (gVisor), `kata-runtime`. Trocar o runtime é
trocar um binário.

---

## 4. Os runtimes de baixo nível, comparados

| Runtime | Linguagem | Isolamento | Característica |
|---|---|---|---|
| **runc** | Go | namespaces + cgroups | Referência da OCI. O padrão em todo lugar |
| **crun** | C | namespaces + cgroups | ~2× mais rápido para iniciar, memória menor. Padrão no Podman em Fedora |
| **youki** | Rust | namespaces + cgroups | Segurança de memória por construção; em amadurecimento |
| **runsc** (gVisor) | Go | **kernel em espaço de usuário** | Intercepta syscalls; superfície de kernel drasticamente menor |
| **kata-runtime** | Go | **micro-VM com kernel próprio** | Isolamento de VM com interface de container |
| **runwasi / wasmedge** | Rust | sandbox Wasm | Executa módulos WebAssembly em vez de processos Linux |

```bash
# Instalar e usar um runtime alternativo
sudo tee -a /etc/docker/daemon.json >/dev/null <<'EOF'
{ "runtimes": { "crun": { "path": "/usr/bin/crun" } } }
EOF
sudo systemctl restart docker
docker run --rm --runtime=crun alpine echo "rodou com crun"
```

*Opinião profissional:* `crun` é uma troca de baixo risco e ganho mensurável quando você inicia
muitos containers curtos (CI, funções, testes). Para carga estável de longa duração, a diferença
some.

---

## 5. BuildKit: por que o build ficou outro

Até a Engine 23, `docker build` usava o construtor legado: sequencial, cache frágil, sem
segredos. O **BuildKit** é padrão desde então.

| | Construtor legado | BuildKit |
|---|---|---|
| Execução | Sequencial, instrução a instrução | **Grafo de dependências**; estágios independentes em paralelo |
| Cache | Por camada, local | Por conteúdo, exportável para registry |
| Segredos | Não há | `--mount=type=secret`, `--mount=type=ssh` |
| Cache de gerenciador de pacotes | Não | `--mount=type=cache` |
| Multi-plataforma | Precária | Nativa |
| Saída | Só imagem | Imagem, tar, arquivos locais, cache |
| Frontend | Fixo | Plugável (`# syntax=`) |

A linha `# syntax=docker/dockerfile:1` no topo do Dockerfile **baixa o frontend mais recente**,
o que dá acesso a recursos novos sem atualizar o Docker. É por isso que ela aparece em todos os
exemplos deste material.

```bash
docker buildx build --progress=plain -t app .    # log completo, essencial para depurar
docker buildx du                                  # quanto o cache ocupa
docker buildx prune --filter until=72h            # limpeza seletiva
```

### Drivers do buildx

| Driver | Onde constrói | Quando usar |
|---|---|---|
| `docker` | Dentro do daemon local | Padrão; limitado em multi-plataforma |
| `docker-container` | Container BuildKit dedicado | Multi-arch, cache exportável |
| `kubernetes` | Pods num cluster | Builds distribuídos em equipe |
| `remote` | BuildKit já em execução | Builder compartilhado |

---

## 6. Drivers plugáveis: log, storage, rede

O daemon delega três subsistemas a drivers.

### Log

```bash
docker system info | grep "Logging Driver"
```

| Driver | Uso | Ressalva |
|---|---|---|
| `json-file` | Padrão | **Sem limite de tamanho por padrão** — enche disco |
| `local` | Formato binário, mais eficiente, com rotação por padrão | `docker logs` funciona; ferramentas externas, não |
| `journald` | systemd | Integra com `journalctl` |
| `syslog`, `fluentd`, `gelf`, `awslogs` | Agregação central | **`docker logs` deixa de funcionar** |
| `none` | Descarta | Quando o app já envia para outro lugar |

```json
// /etc/docker/daemon.json — o ajuste que todo servidor deveria ter
{ "log-driver": "json-file", "log-opts": { "max-size": "10m", "max-file": "3" } }
```

### Storage

| Driver | Situação |
|---|---|
| `overlay2` | Padrão há anos; maduro e rápido |
| `containerd snapshotter` | **Padrão em instalações novas desde a Engine 29** |
| `btrfs`, `zfs` | Quando o sistema de arquivos do host é esse; snapshot nativo |
| `devicemapper` | **Obsoleto**; removido |
| `vfs` | Sem CoW: cópia integral. Só para testes; enorme e lento |

### Rede

`bridge`, `host`, `none`, `overlay`, `macvlan`, `ipvlan`, mais plugins (Weave, Calico). Detalhes
em [16-redes.md](16-redes.md).

---

## 7. A API do daemon

Tudo que a CLI faz é HTTP. Você pode falar direto:

```bash
curl -s --unix-socket /var/run/docker.sock http://localhost/version | jq
curl -s --unix-socket /var/run/docker.sock http://localhost/containers/json | jq '.[].Names'
curl -s --unix-socket /var/run/docker.sock http://localhost/info | jq '.ServerVersion, .Driver'

# Criar e iniciar um container só com curl
curl -s -X POST --unix-socket /var/run/docker.sock \
  -H "Content-Type: application/json" \
  -d '{"Image":"alpine","Cmd":["echo","via API"]}' \
  http://localhost/containers/create
```

> ### ⚠️ Por que montar `/var/run/docker.sock` num container é perigoso
>
> Ferramentas como Portainer, Watchtower e agentes de CI pedem esse socket. Quem o tem, tem
> **root no host**:
>
> ```bash
> # De DENTRO de um container com o socket montado:
> curl -s -X POST --unix-socket /var/run/docker.sock \
>   -H "Content-Type: application/json" \
>   -d '{"Image":"alpine","Cmd":["chroot","/host","sh"],"HostConfig":{"Binds":["/:/host"],"Privileged":true}}' \
>   http://localhost/containers/create
> ```
>
> Mitigações reais: um **proxy de socket** com allow-list de endpoints
> (`tecnativa/docker-socket-proxy`), a **API por TLS** com certificado de cliente, ou
> **rootless mode** — que reduz o dano a "root do seu usuário".

---

## 8. Docker vs. containerd vs. Podman vs. CRI-O

| | Docker | containerd | Podman | CRI-O |
|---|---|---|---|---|
| Daemon | sim (`dockerd`) | sim | **não** | sim (mínimo) |
| Root necessário | por padrão, sim | sim | **não** | sim |
| Constrói imagem | sim (BuildKit) | não | sim (Buildah embutido) | não |
| Compose | sim | não | sim (`podman compose`, pods) | não |
| CRI para Kubernetes | não | **sim** | não | **sim** |
| CLI | `docker` | `ctr` (baixo nível), `nerdctl` | `podman` (compatível com docker) | `crictl` |
| Uso típico | Desktop, dev | Nós de cluster | Dev e produção em ambiente regulado | Nós de cluster (OpenShift) |

```bash
# Podman é praticamente drop-in
alias docker=podman
podman run -d -p 8080:80 nginx:alpine
podman generate systemd --name web > web.service   # gera unidade systemd: ótimo em servidor
```

**Diferença conceitual que importa:** o Podman tem **pods** (grupo de containers compartilhando
namespace de rede), tomando emprestado o conceito do Kubernetes. Isso facilita levar uma stack
local para um cluster.

*Recomendação prática:* em desktop Linux e em servidores de organizações com restrição de
licença, Podman é a escolha racional. Em desktop macOS/Windows, o Docker Desktop ainda tem a
melhor integração. Em nós de Kubernetes, a pergunta nem se coloca: é containerd ou CRI-O.

---

## 9. Onde as coisas ficam no disco

```bash
docker system info | grep "Docker Root Dir"      # normalmente /var/lib/docker
sudo du -sh /var/lib/docker/*
```

| Caminho | Conteúdo |
|---|---|
| `/var/lib/docker/overlay2/` | Camadas de imagem e de container — **quase sempre o maior** |
| `/var/lib/docker/volumes/` | Volumes nomeados |
| `/var/lib/docker/containers/<id>/` | Metadados e **logs** (`<id>-json.log`) |
| `/var/lib/docker/image/` | Índice de imagens do store legado |
| `/var/lib/docker/buildkit/` | Cache de build |
| `/run/containerd/` | Sockets e bundles em execução (efêmero) |
| `/etc/docker/daemon.json` | Configuração do daemon |

```bash
# Achar o log gigante que encheu o disco
sudo find /var/lib/docker/containers -name "*-json.log" -size +100M -exec ls -lh {} \;
```

**Mover o diretório de dados** (por exemplo, para um disco maior):

```bash
sudo systemctl stop docker
sudo rsync -aP /var/lib/docker/ /mnt/dados/docker/
echo '{ "data-root": "/mnt/dados/docker" }' | sudo tee /etc/docker/daemon.json
sudo systemctl start docker
docker system info | grep "Docker Root Dir"
```

---

## Autoteste

1. Desenhe de memória a cadeia CLI → processo, nomeando os cinco componentes.
2. Por que `runc` não aparece no `ps` de um container em execução?
3. O que `live-restore` permite, e em que situação ele não funciona?
4. O que é um *bundle* OCI e quais são suas duas partes?
5. Cite três runtimes de baixo nível alternativos ao `runc` e o que cada um oferece de diferente.
6. Liste quatro capacidades do BuildKit que o construtor legado não tinha.
7. Por que o driver de log `json-file` sem `max-size` é um risco operacional?
8. Escreva o comando `curl` que lista os containers pelo socket do daemon.
9. Explique, com um exemplo concreto, por que montar `/var/run/docker.sock` equivale a dar root.
10. Você precisa liberar espaço urgente. Quais três diretórios sob `/var/lib/docker` você
    inspeciona primeiro, e em que ordem?
