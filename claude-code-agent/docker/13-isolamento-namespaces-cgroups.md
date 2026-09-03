# 13 · Isolamento — namespaces, cgroups e o que o kernel realmente faz

`Nível: avançado` · `Última atualização: 11/08/2026`

Aqui não há caixa-preta. Vamos construir um container à mão, sem Docker, e depois desmontar o
que o Docker faz por cima disso.

Os comandos deste arquivo exigem **Linux** e, em alguns casos, `sudo`. Em macOS/Windows, rode-os
dentro de uma VM Linux ou no WSL2.

---

## 1. Os sete namespaces, um a um

Um namespace faz um conjunto de processos ter uma **visão própria** de um recurso global do
kernel. Não há cópia do recurso: há uma indireção na estrutura de dados do kernel.

```bash
# Todo processo tem seus namespaces expostos como links simbólicos
ls -l /proc/self/ns/
# esperado: cgroup, ipc, mnt, net, pid, pid_for_children, time, user, uts
# cada um aponta para algo como 'net:[4026531840]' — o número é o ID do namespace
```

Dois processos com o **mesmo número** compartilham aquele namespace.

### `mnt` — pontos de montagem (Linux 2.4.19, 2002)

Dá ao processo sua própria tabela de montagens. É o que torna possível o container ter `/`
próprio.

```bash
sudo unshare --mount bash
mount -t tmpfs tmpfs /mnt      # só este shell enxerga essa montagem
findmnt /mnt
exit
findmnt /mnt                   # não existe fora
```

**A sutileza que causa bug real:** montagens têm **propagação** (`shared`, `private`, `slave`).
Se o Docker montar algo como `shared`, montagens feitas dentro do container vazam para o host.
É por isso que `--privileged` combinado com montagens é tão perigoso, e por que `/sys/fs/cgroup`
costuma ser montado como somente leitura.

### `uts` — hostname (2.6.19, 2006)

```bash
sudo unshare --uts bash
hostname meu-container
hostname          # meu-container
exit
hostname          # o do host, intacto
```

"UTS" vem de *Unix Time-Sharing System* — um nome herdado da estrutura `utsname`, que também
carrega o nome do sistema. É uma **convenção arbitrária** de nomenclatura, e vale dizer isso em
vez de inventar um significado.

### `ipc` — comunicação entre processos (2.6.19, 2006)

Isola memória compartilhada System V, filas de mensagens e semáforos. É o motivo pelo qual dois
containers não conseguem, por padrão, se comunicar por memória compartilhada — e por que
`--ipc=host` existe para os casos em que isso é necessário (PyTorch com múltiplos
`DataLoader` workers, por exemplo, que estoura o `/dev/shm` padrão de 64 MB).

### `pid` — tabela de processos (2.6.24, 2008)

O mais didático de todos.

```bash
sudo unshare --pid --fork --mount-proc bash
ps aux            # apenas bash e ps
echo $$           # 1  — este shell É o PID 1
exit
```

`--mount-proc` é necessário porque o `ps` lê `/proc`; sem remontar `/proc` no novo namespace,
você continuaria vendo os processos do host.

**Três propriedades do PID namespace que geram comportamento surpreendente:**

1. **É hierárquico.** O processo tem PID 1 dentro e um PID normal fora. O host vê tudo; o
   container não vê o host.
2. **PID 1 tem tratamento especial do kernel:** sinais sem tratador registrado são
   **descartados**. É por isso que `docker stop` demora 10 s em containers que não tratam
   `SIGTERM`.
3. **Se o PID 1 morre, o kernel mata todos os processos daquele namespace.** É o que faz o
   container terminar por inteiro quando o processo principal termina.

### `net` — pilha de rede (2.6.29, 2009)

Cada namespace de rede tem interfaces, endereços, tabelas de roteamento, regras de firewall e
portas próprios.

```bash
sudo ip netns add teste
sudo ip netns exec teste ip addr      # só 'lo', e DOWN
sudo ip netns exec teste ip link set lo up
sudo ip netns del teste
```

**Consequência que confunde todo iniciante:** `127.0.0.1` dentro do container **não é** o
`127.0.0.1` do host. São loopbacks diferentes. E dois containers podem ambos escutar na porta
80 sem conflito, porque cada um tem sua própria tabela de portas.

### `user` — mapeamento de UID/GID (3.8, 2013)

O mais poderoso e o mais tardio. Permite que o UID 0 (root) **dentro** do namespace corresponda
a um UID sem privilégio **fora**.

```bash
unshare --user --map-root-user bash    # NÃO precisa de sudo!
id                                     # uid=0(root)
cat /proc/self/uid_map                 # 0  1000  1  → root dentro = uid 1000 fora
touch /etc/teste                       # Permission denied: você não é root de verdade
exit
```

É a base do **rootless containers** (Podman por padrão, Docker rootless mode). Também é a base do
`--userns-remap` do Docker.

**Por que só chegou em 2013, cinco anos depois dos outros?** Porque tocar no modelo de
credenciais do kernel é a mudança mais arriscada possível — e, de fato, o user namespace foi
fonte de uma sequência de CVEs de escalada de privilégio nos anos seguintes. Algumas distros
chegaram a desabilitá-lo para usuários comuns por precaução.

### `cgroup` (4.6, 2016) e `time` (5.6, 2020)

O namespace de cgroup esconde a hierarquia real, para o container não descobrir o caminho do
seu cgroup no host. O de tempo permite deslocar `CLOCK_MONOTONIC` e `CLOCK_BOOTTIME` — usado
sobretudo em *checkpoint/restore* (CRIU), quando um processo migra de máquina.

---

## 2. Construindo um container à mão, sem Docker

Este exercício vale mais que dez artigos. Em uma máquina Linux:

```bash
# 1) Um sistema de arquivos raiz. Pegamos o do Alpine, via Docker, só para não baixar à mão.
mkdir -p /tmp/meurootfs
docker export $(docker create alpine:3.20) | tar -x -C /tmp/meurootfs
ls /tmp/meurootfs        # bin dev etc home lib ... — um Linux completo, ~8 MB

# 2) Crie os namespaces e troque a raiz
sudo unshare --mount --uts --ipc --pid --fork --net --mount-proc=/tmp/meurootfs/proc \
  chroot /tmp/meurootfs /bin/sh

# --- você está "dentro" ---
hostname container-artesanal
ps aux                   # só sh e ps
ls /                     # o rootfs do Alpine
cat /etc/os-release      # Alpine Linux
ip addr                  # só lo — sem rede, porque não configuramos o par veth
exit
```

Você acabou de criar um container com **um comando do coreutils**. O que o Docker acrescenta:

| O Docker faz | O que fizemos acima |
|---|---|
| Baixa e monta camadas via OverlayFS | Extraímos um tar |
| Cria par `veth`, bridge, NAT, DNS | Nada (`--net` isolou, mas não conectou) |
| Aplica cgroups | Nada |
| Aplica seccomp, capabilities, AppArmor | Nada (herdamos root pleno — **perigoso**) |
| Gerencia ciclo de vida, logs, restart | Nada |
| Distribui a imagem por registry | Nada |

**A conclusão importante:** o isolamento é do **kernel**. O Docker é a ergonomia, a
distribuição e as políticas de segurança padrão. Isso explica por que Podman, containerd e CRI-O
produzem containers equivalentes: todos chamam o mesmo kernel.

---

## 3. cgroups v2 na prática

```bash
stat -fc %T /sys/fs/cgroup/        # cgroup2fs = v2
```

Crie e use um cgroup manualmente:

```bash
sudo mkdir /sys/fs/cgroup/meu-teste

# Habilite os controladores no pai (na v2, é preciso delegar explicitamente)
cat /sys/fs/cgroup/cgroup.controllers      # o que está disponível
echo "+memory +cpu +pids" | sudo tee /sys/fs/cgroup/cgroup.subtree_control

# Limite: 100 MB de memória, 50% de um núcleo, 20 processos
echo 100000000            | sudo tee /sys/fs/cgroup/meu-teste/memory.max
echo "50000 100000"       | sudo tee /sys/fs/cgroup/meu-teste/cpu.max   # 50ms a cada 100ms
echo 20                   | sudo tee /sys/fs/cgroup/meu-teste/pids.max

# Coloque um shell dentro e observe
echo $$ | sudo tee /sys/fs/cgroup/meu-teste/cgroup.procs
cat /sys/fs/cgroup/meu-teste/memory.current      # uso atual, em bytes

# Estoure o limite (o kernel mata o processo)
python3 -c "a=[]
while True: a.append(' '*10_000_000)"
# esperado: Killed
dmesg | tail -5      # a mensagem do OOM killer, com o cgroup nomeado

sudo rmdir /sys/fs/cgroup/meu-teste
```

### Os arquivos que valem conhecer (cgroup v2)

| Arquivo | O que faz |
|---|---|
| `memory.max` | Teto rígido. Ultrapassar = OOM kill |
| `memory.high` | Teto **flexível**: acima dele o kernel aplica pressão e throttling, sem matar |
| `memory.current` | Uso atual |
| `memory.events` | Contadores: `high`, `max`, `oom`, `oom_kill` |
| `cpu.max` | `"QUOTA PERÍODO"` em microssegundos. `"max 100000"` = sem limite |
| `cpu.stat` | `nr_throttled`, `throttled_usec` — **a métrica que revela throttling de CPU** |
| `pids.max` | Máximo de processos/threads |
| `io.max` | Limites de IOPS e vazão por dispositivo |
| `cgroup.procs` | Os PIDs no grupo |

### `memory.high` vs `memory.max` — a diferença que o Docker esconde

`-m 512m` no Docker define `memory.max`: ao ultrapassar, o processo **morre**.
`--memory-reservation` mapeia para algo próximo de `memory.high`: o kernel aplica pressão de
recuperação de memória, degradando desempenho em vez de matar.

*Opinião profissional:* usar `memory.high` um pouco abaixo de `memory.max` produz um
comportamento muito mais operável — o serviço fica lento e emite sinal antes de morrer, dando
tempo de alertar. Poucos usam porque a exposição pelo Docker é indireta.

### O throttling de CPU que ninguém vê

```bash
docker run -d --name t --cpus 0.5 alpine sh -c 'while :; do :; done'
sleep 5
cat /sys/fs/cgroup/system.slice/docker-$(docker inspect -f '{{.Id}}' t).scope/cpu.stat
# nr_throttled > 0 e throttled_usec crescendo → o processo está sendo estrangulado
docker rm -f t
```

**Este é um dos diagnósticos mais valiosos de produção.** Latência alta com CPU aparentemente
ociosa costuma ser throttling: o container consome sua cota em 20 ms do período de 100 ms e fica
80 ms parado. Aplicações com muitas threads (JVM, Go com `GOMAXPROCS` alto) atingem a cota mais
rápido do que o esperado. A correção pode ser aumentar a cota **ou** reduzir o paralelismo
interno.

---

## 4. Capabilities: o que o container pode fazer

```bash
# O que o Docker concede por padrão
docker run --rm alpine sh -c 'apk add -q libcap 2>/dev/null; capsh --print' 2>/dev/null | head -3
# ou, de forma mais direta:
docker run --rm alpine grep CapEff /proc/1/status
# CapEff: 00000000a80425fb  → uma máscara de bits das capabilities efetivas
```

As 14 concedidas por padrão pelo Docker:

`CHOWN`, `DAC_OVERRIDE`, `FSETID`, `FOWNER`, `MKNOD`, `NET_RAW`, `SETGID`, `SETUID`,
`SETFCAP`, `SETPCAP`, `NET_BIND_SERVICE`, `SYS_CHROOT`, `KILL`, `AUDIT_WRITE`.

**Duas dessas são discutíveis:**

- **`NET_RAW`** permite construir pacotes crus: ARP spoofing e varredura de rede a partir do
  container. Muitos guias de segurança recomendam removê-la. O motivo de ela estar no padrão é
  histórico: fazer `ping` funcionar sem configuração extra. É um **trade-off explícito de
  conveniência sobre segurança**.
- **`DAC_OVERRIDE`** permite ignorar permissões de arquivo — o que reduz o benefício de rodar
  como não-root em vários cenários.

O caminho recomendado:

```bash
docker run --cap-drop=ALL --cap-add=NET_BIND_SERVICE minha-app
```

E se o app escuta em porta > 1024 (o que deveria), nem essa é necessária: `--cap-drop=ALL` puro.

### `--privileged`: o que ele realmente faz

```bash
docker run --privileged ...
```

Concede **todas** as capabilities, desabilita seccomp e AppArmor, e dá acesso a todos os
dispositivos do host. **É equivalente a rodar como root no host, sem barreira.** Prova:

```bash
docker run --rm --privileged alpine sh -c 'mkdir -p /h && mount /dev/sda1 /h && ls /h'
# o disco do host, montado dentro do container
```

Casos em que às vezes se justifica: Docker-in-Docker, ferramentas que manipulam o kernel,
alguns testes de sistema. Em **todos** eles existe uma alternativa mais restrita:
`--cap-add` específico, `--device` específico, ou `sysbox`/`kaniko` no lugar de DinD.

*Regra:* `--privileged` num `docker run` de produção é um incidente de segurança esperando data.

---

## 5. seccomp

O perfil padrão do Docker bloqueia cerca de 40 das ~350 chamadas de sistema do Linux, entre elas
`kexec_load` (trocar o kernel), `open_by_handle_at` (base do exploit "Shocker", de 2014),
`init_module`, `bpf` e `clock_settime`.

```bash
# Sem seccomp, a syscall passa; com o perfil padrão, é bloqueada
docker run --rm --security-opt seccomp=unconfined alpine sh -c 'echo teste'

# Perfil customizado (allow-list)
docker run --security-opt seccomp=/caminho/perfil.json minha-app
```

Ferramentas como `oci-seccomp-bpf-hook` e `strace` permitem **gerar** um perfil observando o que
o app realmente chama. Isso é trabalho de segurança madura, não de primeiro dia — mas é o que
reduz a superfície de kernel de 350 syscalls para as 40 que seu app usa.

---

## 6. Rootless: o modelo mais seguro

No modo tradicional, o `dockerd` roda como root. Quem tem acesso ao socket tem root no host
(demonstrado em [03-instalacao.md](03-instalacao.md#permissões-e-o-problema-do-sudo)).

No **rootless**, o daemon e os containers rodam como seu usuário, usando `user namespace` +
`slirp4netns`/`pasta` para rede.

```bash
dockerd-rootless-setuptool.sh install
export DOCKER_HOST=unix:///run/user/$(id -u)/docker.sock
docker info | grep -i rootless
```

| Ganho | Perda |
|---|---|
| Escape de container não entrega root do host | Portas < 1024 exigem configuração extra |
| Vários usuários, daemons isolados | Rede mais lenta (userspace networking) |
| Não requer privilégio para instalar | Alguns drivers de storage e rede indisponíveis |
| — | `--net=host`, cgroup limitado sem delegação |

O **Podman é rootless por padrão** e sem daemon — cada `podman run` é um `fork`/`exec` direto,
com um `conmon` por container. É a razão principal de sua adoção em ambientes regulados.

---

## 7. O que o isolamento NÃO protege

Honestidade sobre o modelo de ameaça:

| Vetor | Container protege? | Observação |
|---|---|---|
| App consome toda a RAM | ✅ (com cgroup) | Só se você definiu o limite |
| App vê processos do host | ✅ | PID namespace |
| App lê arquivos do host | ✅ | Salvo bind mount, `--privileged`, socket montado |
| Vulnerabilidade **no kernel** | ❌ | Kernel é compartilhado. Um bug em syscall afeta o host |
| Canal lateral de CPU (Spectre, L1TF) | ❌ | Mitigado por microcódigo e flags do kernel, não pelo container |
| Exaustão de recurso não limitada por cgroup | ⚠️ | Descritores de arquivo, portas, inodes, entropia |
| `--privileged` ou socket do Docker montado | ❌ | Você entregou a máquina voluntariamente |
| Imagem base maliciosa | ❌ | É um problema de cadeia de suprimentos, não de isolamento |

**Quando é preciso mais que container:**

| Tecnologia | Como funciona | Custo |
|---|---|---|
| **gVisor** (Google) | Um kernel em espaço de usuário, em Go, intercepta as syscalls. O kernel real vê pouquíssimas chamadas | 10–30% de sobrecarga em I/O; algumas syscalls não suportadas |
| **Kata Containers** | Cada container numa micro-VM leve, com kernel próprio | ~100–200 ms extras no start, mais RAM |
| **Firecracker** (AWS) | Micro-VM minimalista; base do Lambda e do Fargate | ~125 ms de boot, footprint mínimo |
| **Sandbox de V8** (Cloudflare Workers) | Isolados de JavaScript, sem processo por tenant | Só serve para JS/Wasm |

Todos são **drop-in** via `--runtime` ou RuntimeClass no Kubernetes:

```bash
docker run --runtime=runsc alpine   # gVisor
```

---

## 8. Depuração de isolamento — a caixa de ferramentas

```bash
# Em quais namespaces o container está?
PID=$(docker inspect -f '{{.State.Pid}}' NOME)
sudo ls -l /proc/$PID/ns/

# Entrar nos namespaces de um container sem usar 'docker exec'
sudo nsenter -t $PID -n -p -m -u ip addr

# Qual é o cgroup dele, e quanto está consumindo?
sudo cat /proc/$PID/cgroup
CG=/sys/fs/cgroup/$(sudo cat /proc/$PID/cgroup | cut -d: -f3)
cat $CG/memory.current $CG/memory.max
cat $CG/cpu.stat | grep throttled

# Quais capabilities ele tem?
sudo grep Cap /proc/$PID/status
sudo capsh --decode=$(sudo grep CapEff /proc/$PID/status | awk '{print $2}')

# seccomp está ativo?
sudo grep Seccomp /proc/$PID/status
# 0 = desligado · 2 = filtro ativo

# O que o container enxerga como raiz?
sudo ls /proc/$PID/root/
```

`nsenter` é a ferramenta que salva quando a imagem não tem shell: você entra nos namespaces do
alvo usando o binário **do host**.

---

## Autoteste

1. Liste os sete namespaces e diga, para cada um, um sintoma observável de que ele está ativo.
2. Por que `unshare --pid --fork` precisa também de `--mount-proc` para o `ps` fazer sentido?
3. Escreva a sequência de comandos que cria um container à mão, sem Docker.
4. Por que o user namespace só chegou ao kernel em 2013, cinco anos depois do PID namespace?
5. Qual é a diferença entre `memory.max` e `memory.high`, e por que a segunda é mais operável?
6. Você tem latência alta e a CPU parece ociosa. Qual arquivo de cgroup você lê, e o que procura?
7. Cite duas capabilities concedidas por padrão pelo Docker que são discutíveis, e por quê.
8. O que `--privileged` faz exatamente? Demonstre o risco em um comando.
9. Cite três coisas contra as quais o isolamento por namespace **não** protege.
10. Quando você escolheria gVisor em vez de runc, e o que pagaria por isso?
