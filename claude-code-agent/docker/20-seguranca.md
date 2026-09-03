# 20 · Segurança de containers

`Nível: avançado` · `Última atualização: 11/08/2026`

Container **não** é uma fronteira de segurança forte. Este arquivo explica o que ele protege, o
que não protege, e o que fazer a respeito — em ordem de retorno sobre o esforço.

---

## 1. O modelo de ameaça, explicitado

Antes de qualquer controle, defina de quem você está se defendendo:

| Ameaça | Container protege? | O que realmente resolve |
|---|---|---|
| Bug da sua aplicação consumindo toda a RAM | ✅ com cgroup | Limites de recurso |
| Sua aplicação lendo arquivos do host | ✅ | Namespaces (salvo bind mount) |
| Dependência com CVE conhecida | ❌ | Escaneamento + atualização |
| Imagem base maliciosa | ❌ | Proveniência, assinatura, base confiável |
| Segredo vazado na imagem | ❌ | `--mount=type=secret`, escaneamento de segredo |
| Escape via bug do kernel | ❌ | Kernel atualizado, seccomp, gVisor/Kata |
| Escape via configuração errada (`--privileged`, socket) | ❌ | Higiene de configuração |
| Movimento lateral entre containers | ⚠️ parcial | Segmentação de rede |
| Exfiltração de dados | ❌ | Rede `internal`, egresso controlado |
| Tenant hostil no mesmo host | ❌ | **Micro-VM ou máquinas separadas** |

**A frase que resume:** container isola **acidente** muito bem e isola **ataque** razoavelmente,
desde que bem configurado. Se o adversário é hostil e desconhecido, o container **não é a última
barreira** — coloque uma VM.

---

## 2. As dez medidas, ordenadas por custo-benefício

Se você fizer só as cinco primeiras, já estará acima da média da indústria.

### 1. Não rode como root (custo: 3 linhas)

```dockerfile
RUN addgroup -S app && adduser -S -G app app
USER app
```
```yaml
user: "1000:1000"     # no compose, se a imagem não permitir alterar
```

```bash
# Auditoria: quais dos seus containers rodam como root?
docker ps -q | xargs -I{} sh -c 'echo -n "{} "; docker exec {} id -u 2>/dev/null || echo "?"'
```

### 2. `no-new-privileges` (custo: 1 linha)

```yaml
security_opt: [no-new-privileges:true]
```
Impede que qualquer binário `setuid` dentro do container eleve privilégio. Não quebra nada em
aplicações normais.

### 3. Descarte capabilities (custo: 2 linhas)

```yaml
cap_drop: [ALL]
cap_add: [NET_BIND_SERVICE]   # só se precisar de porta < 1024 — e você não deveria
```

### 4. Sistema de arquivos raiz somente leitura (custo: 2 linhas)

```yaml
read_only: true
tmpfs: [/tmp, /run]
```
Elimina a classe inteira de "atacante grava webshell/binário no container". A maioria das
aplicações web funciona sem alteração; as que não funcionam só precisam declarar onde escrevem.

### 5. Limites de recurso (custo: 4 linhas)

```yaml
deploy:
  resources:
    limits: { memory: 512M, cpus: "1.0" }
pids_limit: 200
```
`pids_limit` é a defesa mais barata contra *fork bomb*. Sem limite de memória, um vazamento
derruba o host inteiro.

### 6. Segmentação de rede

```yaml
networks:
  interna:
    internal: true
```
Ver [16-redes.md](16-redes.md#6-segmentação-de-rede-como-camada-de-segurança). Uma linha que
corta o passo mais comum de uma cadeia de ataque: baixar ferramentas e exfiltrar dados.

### 7. Imagem base mínima e atualizada

Menos pacotes = menos CVEs. `distroless`/`scratch` não têm shell, o que sozinho inutiliza a
maior parte dos payloads prontos.

```bash
docker scout cves minha-app:1.0
docker scout recommendations minha-app:1.0
```

### 8. Segredos fora da imagem e fora do ambiente

- **Build:** `--mount=type=secret`, nunca `ARG`.
- **Runtime:** arquivo em tmpfs (`secrets:`) em vez de `environment:` — variáveis aparecem em
  `docker inspect`, em `/proc/PID/environ`, em despejos de erro e são herdadas por filhos.

```bash
# Escaneie o repositório e as imagens em busca de segredo vazado
docker run --rm -v "$PWD:/src" zricethezav/gitleaks:latest detect --source=/src
trivy image --scanners secret minha-app:1.0
```

### 9. Escaneamento contínuo no CI

Ver [19-registries-e-distribuicao.md](19-registries-e-distribuicao.md#5-cadeia-de-suprimentos-o-assunto-de-2026).
Escaneie **no push e periodicamente** — uma imagem que não mudou pode ter CVE nova amanhã.

### 10. Nunca monte o socket do Docker

```yaml
volumes:
  - /var/run/docker.sock:/var/run/docker.sock   # ❌ isso é dar root no host
```

Se for inevitável (Portainer, Watchtower, agente de CI), use um **proxy de socket** com
allow-list:

```yaml
  docker-proxy:
    image: tecnativa/docker-socket-proxy
    environment:
      CONTAINERS: 1        # permite só listar containers
      POST: 0              # nenhuma operação de escrita
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
    networks: [interna]
```

---

## 3. A demonstração que convence: escape com socket montado

Rode num laboratório descartável, nunca em máquina que importe.

```bash
# 1) Um container "inocente" com o socket montado
docker run -it --rm -v /var/run/docker.sock:/var/run/docker.sock alpine sh
apk add --no-cache curl >/dev/null

# 2) De dentro dele, crie um container privilegiado com a raiz do host montada
curl -s -X POST --unix-socket /var/run/docker.sock \
  -H "Content-Type: application/json" \
  -d '{"Image":"alpine","Cmd":["sh"],"OpenStdin":true,"Tty":true,
       "HostConfig":{"Binds":["/:/host"],"Privileged":true}}' \
  http://localhost/containers/create

# 3) Inicie e anexe — você tem a raiz do host em /host, como root.
```

**Isso não é um bug.** É o comportamento documentado da API. O socket **é** a interface
privilegiada do daemon. Quem o alcança, alcança a máquina.

O mesmo vale para:
- pertencer ao grupo `docker`;
- `--privileged`;
- `--pid=host` combinado com `nsenter`;
- montar `/` ou `/etc` como bind mount gravável.

---

## 4. As configurações que anulam o isolamento

| Configuração | O que quebra | Alternativa |
|---|---|---|
| `--privileged` | Tudo: capabilities, seccomp, LSM, dispositivos | `--cap-add` específico, `--device` específico |
| `-v /var/run/docker.sock:...` | Root no host | Proxy de socket com allow-list |
| `--pid=host` | Vê e sinaliza processos do host | `--pid container:outro` |
| `--net=host` | Sem isolamento de rede; alcança serviços em `localhost` do host | Rede bridge + `-p` |
| `--ipc=host` | Memória compartilhada do host | `--shm-size` |
| `--userns=host` (com userns-remap ativo) | Anula o remapeamento | — |
| `--security-opt seccomp=unconfined` | ~350 syscalls expostas | Perfil customizado |
| `--security-opt apparmor=unconfined` | Sem MAC | Perfil customizado |
| `-v /:/host` | Sistema de arquivos inteiro | Montar só o necessário, `:ro` |
| `--device=/dev/mem` | Memória física | Nunca |

```bash
# Auditoria rápida: quem está privilegiado?
docker ps -q | xargs docker inspect --format \
  '{{.Name}} privileged={{.HostConfig.Privileged}} pid={{.HostConfig.PidMode}} net={{.HostConfig.NetworkMode}}'
```

---

## 5. Ferramentas de auditoria

```bash
# Docker Bench for Security — CIS Docker Benchmark automatizado
docker run --rm --net host --pid host --userns host --cap-add audit_control \
  -v /var/lib:/var/lib:ro -v /var/run/docker.sock:/var/run/docker.sock:ro \
  -v /etc:/etc:ro --label docker_bench_security \
  docker/docker-bench-security

# Trivy: vulnerabilidades, segredos, má configuração — em imagem, Dockerfile e Compose
trivy image minha-app:1.0
trivy config .
trivy fs --scanners secret .

# Grype + Syft
syft minha-app:1.0 -o json | grype

# Dockle: boas práticas de imagem (usuário, healthcheck, segredos)
docker run --rm goodwithtech/dockle minha-app:1.0

# Hadolint: linter de Dockerfile
docker run --rm -i hadolint/hadolint < Dockerfile
```

**Detecção em tempo de execução:** **Falco** (CNCF) observa syscalls via eBPF e alerta sobre
comportamento anômalo — shell aberto dentro de container, escrita em `/etc`, conexão de saída
inesperada, montagem sensível. É a camada que responde "e se, apesar de tudo, entrarem?".

```bash
docker run -d --name falco --privileged \
  -v /var/run/docker.sock:/host/var/run/docker.sock \
  -v /proc:/host/proc:ro falcosecurity/falco:latest
```

---

## 6. Isolamento reforçado, quando o padrão não basta

| Tecnologia | Como isola | Sobrecarga | Quando usar |
|---|---|---|---|
| **runc** (padrão) | Namespaces + cgroups | ~0 | Código confiável, mesmo dono |
| **gVisor** (`runsc`) | Kernel em espaço de usuário intercepta syscalls | 10–30% em I/O | Código semiconfiável; reduz drasticamente a superfície de kernel |
| **Kata Containers** | Micro-VM com kernel próprio por container | +100–200 ms no start, +RAM | Multi-inquilino, conformidade |
| **Firecracker** | Micro-VM minimalista | ~125 ms de boot | Base do AWS Lambda e Fargate |
| **Máquinas separadas** | Físico | Custo de hardware | Quando o dado justifica |

```bash
docker run --runtime=runsc alpine echo "rodando sob gVisor"
```

**Critério de decisão:** se você executa código que **você não escreveu e não revisou** —
plugins de cliente, execução de código submetido por usuário, build de repositório de terceiro —
o container padrão não é suficiente. Use micro-VM.

---

## 7. Rootless como padrão de servidor

O daemon rodando como root é a maior concentração de privilégio de uma instalação típica.

```bash
sudo apt install -y docker-ce-rootless-extras uidmap
dockerd-rootless-setuptool.sh install
export DOCKER_HOST=unix:///run/user/$(id -u)/docker.sock
docker info | grep -i rootless
```

| Ganho | Perda |
|---|---|
| Escape não entrega root do host | Portas < 1024 exigem configuração extra |
| Cada usuário com seu daemon isolado | Rede em espaço de usuário: mais lenta |
| Instalação sem privilégio | Alguns drivers indisponíveis; cgroup exige delegação |

**Podman é rootless e sem daemon por padrão** — é o motivo principal de sua adoção em ambientes
regulados (bancos, saúde, governo).

---

## 8. Segredos em tempo de execução

Ordem de qualidade, do pior para o melhor:

| Método | Nota | Problema |
|---|---|---|
| Embutido na imagem | ❌ | Qualquer um que baixe a imagem tem o segredo |
| `--build-arg` | ❌ | Fica no histórico da imagem |
| `-e SENHA=...` | ⚠️ | Visível em `docker inspect`, `/proc/PID/environ`, logs de crash, herdado por filhos |
| `--env-file` | ⚠️ | Melhor que a linha de comando, mas continua sendo variável de ambiente |
| `secrets:` (arquivo em tmpfs) | ✅ | Bom; fora do Swarm, não há criptografia em repouso |
| Docker/Swarm secrets | ✅ | Criptografado em repouso e em trânsito |
| Vault, AWS/GCP/Azure Secrets Manager | ✅✅ | Rotação, auditoria, controle de acesso fino |
| SOPS + age/KMS no Git | ✅✅ | GitOps com segredo cifrado versionado |

```bash
# Prova de que variável de ambiente vaza
docker run -d --name x -e SENHA=supersecreta alpine sleep 300
docker inspect x --format '{{json .Config.Env}}'      # lá está
docker exec x cat /proc/1/environ | tr '\0' '\n'      # e aqui também
docker rm -f x
```

Aplicações modernas frequentemente aceitam o sufixo `_FILE`:

```yaml
environment:
  POSTGRES_PASSWORD_FILE: /run/secrets/db_senha
secrets: [db_senha]
```

---

## 9. Endurecimento do host

O container é tão seguro quanto o host embaixo dele.

```bash
# Kernel atualizado — a defesa mais importante contra escape
uname -r
sudo apt update && sudo apt upgrade

# Atualizações automáticas de segurança
sudo apt install -y unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades

# Auditoria de quem acessa o Docker
sudo auditctl -w /usr/bin/dockerd -k docker
sudo auditctl -w /var/run/docker.sock -k docker-socket

# Nunca exponha a API do daemon sem TLS mútuo
ss -tlnp | grep 2375     # se aparecer algo aqui, você tem um incidente
```

> **A porta 2375 (API sem TLS) exposta à internet é uma das formas mais comuns de servidores
> serem comprometidos para mineração de criptomoeda.** Varreduras automatizadas a encontram em
> minutos. Se precisa de acesso remoto, use `docker context` sobre **SSH** — que não expõe porta
> nenhuma.

```json
// /etc/docker/daemon.json — configuração endurecida
{
  "icc": false,                        // containers não conversam na bridge padrão
  "no-new-privileges": true,           // padrão para todos os containers
  "userns-remap": "default",           // root do container ≠ root do host
  "live-restore": true,
  "log-driver": "json-file",
  "log-opts": { "max-size": "10m", "max-file": "3" },
  "default-ulimits": { "nofile": { "Hard": 65535, "Soft": 65535 } }
}
```

---

## 10. Resposta a incidentes

Quando você suspeita de comprometimento:

```bash
# 1) NÃO mate o container ainda — preserve as evidências
docker pause CONTAINER

# 2) Capture o estado
docker inspect CONTAINER > incidente-inspect.json
docker logs CONTAINER > incidente-logs.txt 2>&1
docker diff CONTAINER > incidente-diff.txt     # o que foi alterado na camada de escrita
docker export CONTAINER > incidente-fs.tar     # o sistema de arquivos inteiro

# 3) Rede e processos
PID=$(docker inspect -f '{{.State.Pid}}' CONTAINER)
sudo ls -l /proc/$PID/exe /proc/$PID/cwd
sudo ss -tanp | grep $PID
docker top CONTAINER

# 4) Isole
docker network disconnect $(docker inspect -f '{{range $k,$v := .NetworkSettings.Networks}}{{$k}}{{end}}' CONTAINER) CONTAINER

# 5) Só então
docker stop CONTAINER
```

E as perguntas que orientam a investigação: a imagem veio de onde? Foi assinada? O socket estava
montado? Havia `--privileged`? Qual credencial esse container conhecia (e portanto precisa ser
rotacionada)? Que outros serviços ele alcançava pela rede?

---

## 11. Checklist de produção

**Imagem**
- [ ] Base mínima, fixada por digest
- [ ] Multi-stage: nenhum toolchain na imagem final
- [ ] `USER` não-root
- [ ] Nenhum segredo em `ARG`, `ENV` ou camada
- [ ] Escaneada no CI; falha em CRITICAL corrigível
- [ ] SBOM e proveniência gerados
- [ ] Assinada, e a assinatura **verificada** no deploy

**Runtime**
- [ ] `no-new-privileges:true`
- [ ] `cap_drop: [ALL]`, com `cap_add` mínimo
- [ ] `read_only: true` + `tmpfs` para os caminhos graváveis
- [ ] Limites de memória, CPU e `pids_limit`
- [ ] Sem `--privileged`, sem socket do Docker, sem `--pid=host`
- [ ] Rede segmentada; `internal: true` onde não precisa de saída
- [ ] Segredos por arquivo/gerenciador, não por variável de ambiente
- [ ] Limite de tamanho de log configurado

**Host**
- [ ] Kernel e Docker atualizados; atualizações automáticas de segurança
- [ ] Rootless, ou grupo `docker` restrito e auditado
- [ ] API do daemon **não** exposta em TCP sem TLS mútuo
- [ ] Auditoria (`auditd`) no binário e no socket
- [ ] Detecção em execução (Falco) em ambientes sensíveis
- [ ] Backup testado dos volumes

---

## Autoteste

1. Contra quais três ameaças o container protege bem, e contra quais três não protege?
2. Escreva as cinco linhas de YAML de maior retorno em segurança e explique cada uma.
3. Demonstre, em um comando, por que montar o socket do Docker é dar root no host.
4. Por que `read_only: true` raramente quebra uma aplicação web, e o que ela precisa declarar?
5. Cite quatro configurações que anulam o isolamento e a alternativa mais restrita de cada.
6. Por que variável de ambiente é um lugar ruim para senha? Cite três formas de vazamento.
7. Quando você escolheria Kata ou gVisor em vez de runc? Qual critério objetivo usa?
8. Por que a porta 2375 exposta é um incidente, e qual é a alternativa correta de acesso remoto?
9. Qual é o primeiro comando ao suspeitar de comprometimento, e por que **não** é `docker stop`?
10. Sua imagem passa no scanner sem nenhuma CVE. Cite três vetores de ataque que continuam
    abertos.
