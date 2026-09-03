# 15 · Armazenamento e volumes — onde os dados realmente vivem

`Nível: intermediário → avançado` · `Última atualização: 11/08/2026`

Perda de dados é o incidente mais caro do mundo dos containers, e quase sempre tem a mesma
causa: alguém achou que o container guardava o dado. Este arquivo elimina essa possibilidade.

---

## 1. As quatro formas de armazenamento, comparadas

| | Camada de escrita | Volume nomeado | Bind mount | tmpfs |
|---|---|---|---|---|
| Onde fica | `/var/lib/docker/overlay2/` | `/var/lib/docker/volumes/` | Onde você mandar | **RAM** |
| Sobrevive a `docker rm`? | ❌ | ✅ | ✅ | ❌ |
| Sobrevive a reboot? | ❌ | ✅ | ✅ | ❌ |
| Gerenciado pelo Docker? | sim | sim | não | sim |
| Desempenho em Linux | CoW, mais lento | nativo | nativo | RAM (o mais rápido) |
| Desempenho em macOS/Win | dentro da VM | dentro da VM (rápido) | **atravessa a fronteira (lento)** | RAM |
| Backup | difícil | fácil e padronizado | trivial (é uma pasta sua) | não se aplica |
| Uso correto | nada que importe | **estado de produção** | **código em desenvolvimento** | segredo, cache, `/tmp` |

```bash
-v nome:/caminho                              # volume nomeado
-v /caminho/absoluto/host:/caminho            # bind mount
--mount type=volume,source=nome,target=/cam   # o mesmo do primeiro, explícito
--mount type=bind,source=/abs,target=/cam,readonly
--mount type=tmpfs,target=/tmp,tmpfs-size=64m
```

> **`-v` vs `--mount`:** funcionalmente equivalentes para os casos comuns. O `-v` é conciso e
> **cria o diretório do host se não existir** (fonte de erros silenciosos: você digita o caminho
> errado e ganha uma pasta vazia em vez de um erro). O `--mount` é verboso, explícito e **falha**
> se a origem não existir. Use `-v` no terminal, `--mount` em script e produção.

---

## 2. Volumes nomeados

```bash
docker volume create dados-app
docker volume ls
docker volume inspect dados-app
# esperado: "Mountpoint": "/var/lib/docker/volumes/dados-app/_data"
docker volume rm dados-app
```

### A regra de inicialização que salva e que surpreende

**Quando um volume nomeado vazio é montado sobre um caminho que já existe na imagem, o Docker
copia o conteúdo E as permissões daquele caminho para dentro do volume.**

```bash
docker run --rm -v v-teste:/etc/nginx nginx:alpine ls /etc/nginx
docker run --rm -v v-teste:/x alpine ls /x
# esperado: nginx.conf, conf.d/, mime.types...  — vieram da imagem
docker volume rm v-teste
```

Isso tem três consequências:

1. **É como um container sem root consegue escrever num volume.** Se a imagem tem
   `RUN mkdir /dados && chown node:node /dados`, o volume nasce pertencendo ao `node`. Sem isso,
   nasceria do root e o app tomaria `EACCES`.
2. **Só acontece se o volume estiver vazio.** Na segunda execução, o conteúdo do volume vence.
   É por isso que "editei a config na imagem e nada mudou": o volume antigo tem a versão velha.
3. **Bind mount NÃO faz isso.** Um bind mount de uma pasta vazia **esconde** o conteúdo da
   imagem. Essa assimetria é a origem de metade da confusão sobre volumes.

### Volumes anônimos

```bash
docker run -v /dados alpine        # sem nome → o Docker sorteia um hash
docker volume ls -f dangling=true  # eles se acumulam aqui
```

Também são criados implicitamente pela instrução `VOLUME` no Dockerfile — o que é uma armadilha
das piores, porque acontece sem você pedir:

```dockerfile
VOLUME /var/lib/postgresql/data    # a imagem oficial do Postgres faz isso
```

Efeito: **todo** `docker run postgres` sem `-v` explícito cria um volume anônimo que nunca é
removido por `docker rm`. Depois de meses, `docker volume ls` mostra centenas deles ocupando
dezenas de GB.

```bash
docker rm -v CONTAINER              # o -v remove os volumes ANÔNIMOS junto
docker volume prune                 # remove todos os órfãos ⚠️ verifique antes
docker volume ls -f dangling=true   # ← rode ISTO antes daquilo
```

*Recomendação:* evite `VOLUME` no seu Dockerfile. Declare o volume no `compose.yaml`, onde ele é
visível e nomeado.

---

## 3. Bind mounts e o problema de permissão

O bind mount é simples até o momento em que os UIDs não batem — e aí consome uma tarde.

### Por que acontece

O kernel não conhece nomes de usuário. Ele conhece **números**. Se dentro do container o app
roda como UID 1000 chamado `node`, e no host o UID 1000 é você, funciona por coincidência. Se
o container roda como UID 999 (`postgres`, por exemplo) e o host não tem esse UID, os arquivos
aparecem com dono numérico e ninguém consegue editá-los.

```bash
# Demonstre o problema
mkdir -p /tmp/perm && cd /tmp/perm
docker run --rm -v "$PWD:/w" -w /w alpine touch arquivo-root
ls -l arquivo-root
# esperado: -rw-r--r-- 1 root root ... — você não consegue apagar sem sudo
```

### As quatro soluções, em ordem de qualidade

**1. Rode o container com o seu UID (melhor para desenvolvimento):**
```bash
docker run --rm --user "$(id -u):$(id -g)" -v "$PWD:/w" -w /w alpine touch arquivo-meu
ls -l arquivo-meu    # dono: você
```
Ressalva: o UID pode não existir no `/etc/passwd` do container, e alguns programas reclamam
("whoami: unknown uid"). Contorne com `--user "$(id -u):$(id -g)" -e HOME=/tmp`.

**2. Crie na imagem um usuário com o UID certo (melhor para equipe):**
```dockerfile
ARG UID=1000
ARG GID=1000
RUN addgroup -g $GID app && adduser -D -u $UID -G app app
USER app
```
```bash
docker build --build-arg UID=$(id -u) --build-arg GID=$(id -g) -t app .
```

**3. `chown` no entrypoint (o que as imagens oficiais fazem):**
Um entrypoint que roda como root, ajusta o dono e então faz `su-exec`/`gosu` para o usuário
final. Funciona, mas exige começar como root.

**4. User namespace remap (mais robusto, mais complexo):**
```json
// /etc/docker/daemon.json
{ "userns-remap": "default" }
```
O root do container passa a mapear para um UID sem privilégio no host. Muda o modelo de
permissão de todos os volumes existentes — planeje a migração.

### SELinux (Fedora, RHEL, Rocky)

```bash
docker run -v "$PWD:/app" alpine ls /app     # Permission denied, mesmo com dono correto
docker run -v "$PWD:/app:Z" alpine ls /app   # ✅
```

| Sufixo | Efeito |
|---|---|
| `:z` (minúsculo) | Rótulo **compartilhado**: vários containers podem acessar |
| `:Z` (maiúsculo) | Rótulo **exclusivo** deste container |

> ⚠️ **Cuidado sério:** `:Z` em um diretório do sistema (como `/home` ou `/var`) **relabela
> recursivamente** aquele diretório e pode quebrar o host. Use apenas em pastas de projeto.

---

## 4. Desempenho: onde o I/O dói

### Linux

Volumes e bind mounts vão direto ao sistema de arquivos do host — desempenho nativo. A camada
de escrita (OverlayFS) é mais lenta por causa do copy-on-write, sobretudo na primeira escrita de
arquivos grandes.

Regra: **carga de escrita intensa nunca fica na camada de escrita.** Banco de dados, índices,
uploads e caches vão para volume.

### macOS e Windows — a fronteira que custa caro

Todo container Linux roda numa VM. Bind mounts precisam atravessar host ↔ VM:

| Mecanismo | Plataforma | Desempenho relativo |
|---|---|---|
| **VirtioFS** | macOS (Docker Desktop recente) | Bom; use este |
| **gRPC-FUSE** | macOS (legado) | Ruim |
| **osxfs** | macOS (histórico) | Muito ruim |
| **9p** | WSL2 acessando `/mnt/c` | **Péssimo** |
| **ext4 nativo** | WSL2 dentro de `~` | Nativo |

Números que aparecem na prática: `npm install` numa pasta bind-montada do `/mnt/c` no WSL2
podia levar **10 a 50×** o tempo do mesmo comando dentro do sistema de arquivos do Linux.

**As correções, em ordem:**

1. **No Windows, mantenha o projeto em `~` dentro do WSL**, nunca em `/mnt/c`.
2. **No macOS, habilite VirtioFS** nas configurações do Docker Desktop.
3. **Coloque as pastas pesadas em volume nomeado**, não em bind mount:
   ```yaml
   volumes:
     - ./src:/app/src          # código: bind mount (pequeno, precisa ser editável)
     - node_modules:/app/node_modules   # dependências: volume (grande, não precisa ser editável)
   ```
4. **Use `docker compose watch`** com `action: sync`, que copia arquivos em vez de montar.

---

## 5. Backup, restauração e migração

### O padrão que funciona para qualquer volume

```bash
# Backup
docker run --rm \
  -v MEU_VOLUME:/dados:ro \
  -v "$PWD:/backup" \
  alpine tar czf /backup/backup-$(date +%F).tgz -C /dados .

# Restauração
docker run --rm \
  -v MEU_VOLUME:/dados \
  -v "$PWD:/backup" \
  alpine sh -c "rm -rf /dados/* /dados/..?* 2>/dev/null; tar xzf /backup/backup-2026-08-11.tgz -C /dados"

# Migrar entre máquinas
docker run --rm -v MEU_VOLUME:/d alpine tar cz -C /d . | ssh destino \
  'docker run --rm -i -v MEU_VOLUME:/d alpine tar xz -C /d'
```

### Banco de dados: **não** copie os arquivos a quente

Copiar `/var/lib/postgresql/data` com o Postgres em execução captura páginas em estados
inconsistentes — o dump pode restaurar, pode não restaurar, ou pode restaurar corrompido. Use a
ferramenta lógica do próprio banco:

```bash
# Postgres
docker compose exec -T db pg_dump -U app --no-owner app | gzip > dump-$(date +%F).sql.gz
gunzip -c dump-2026-08-11.sql.gz | docker compose exec -T db psql -U app app

# MySQL / MariaDB
docker compose exec -T db mysqldump -u root -p"$SENHA" --single-transaction app | gzip > dump.sql.gz

# MongoDB
docker compose exec -T db mongodump --archive --gzip > dump.gz

# Redis (o próprio Redis já grava snapshot; force um antes de copiar)
docker compose exec redis redis-cli BGSAVE
```

### A regra 3-2-1, aplicada a containers

**3** cópias, em **2** mídias diferentes, **1** fora do local.

```yaml
  backup:
    image: restic/restic:latest
    environment:
      RESTIC_REPOSITORY: s3:s3.amazonaws.com/meu-bucket/backups
      RESTIC_PASSWORD: ${RESTIC_SENHA:?}
      AWS_ACCESS_KEY_ID: ${AWS_KEY:?}
      AWS_SECRET_ACCESS_KEY: ${AWS_SECRET:?}
    volumes:
      - dados-db:/dados:ro
    command: ["backup", "/dados", "--tag", "diario"]
```

**E teste a restauração.** Um backup nunca restaurado não é um backup — é uma esperança. Coloque
o teste de restauração no calendário, trimestral no mínimo.

---

## 6. Volume drivers e armazenamento em rede

Volumes locais servem a uma máquina. Em cluster, o volume precisa seguir o container.

```bash
# NFS, sem plugin externo — o driver 'local' sabe fazer isso
docker volume create --driver local \
  --opt type=nfs \
  --opt o=addr=192.168.1.10,rw,nfsvers=4 \
  --opt device=:/export/dados \
  dados-nfs

# CIFS/SMB
docker volume create --driver local \
  --opt type=cifs \
  --opt o=username=usuario,password=senha,uid=1000 \
  --opt device=//servidor/compartilhamento \
  dados-smb
```

| Solução | Modelo | Observação |
|---|---|---|
| `local` + NFS | Rede | Simples; latência e travamento de bloqueio (`lock`) são os riscos |
| **CSI** (Container Storage Interface) | Padrão do Kubernetes | O caminho moderno; EBS, GCE PD, Ceph, Longhorn |
| Ceph / Longhorn / OpenEBS | Replicado | Para cluster próprio |
| EBS / Persistent Disk / Azure Disk | Nuvem | Preso a uma zona de disponibilidade |

> **Advertência que vale a tarde perdida:** bancos de dados relacionais sobre NFS são uma fonte
> clássica de corrupção e de travamento por problemas de `lock` e semântica de `fsync`. Se
> precisar de banco replicado, use replicação **do banco** (streaming replication, réplicas), não
> armazenamento compartilhado.

---

## 7. Diagnóstico — quando o disco enche

```bash
docker system df                 # panorama
docker system df -v              # detalhado, por imagem, container e volume

# Os maiores volumes
sudo du -sh /var/lib/docker/volumes/* | sort -hr | head -10

# Os maiores logs de container
sudo find /var/lib/docker/containers -name "*-json.log" -exec du -h {} + | sort -hr | head

# Cache de build
docker builder du
docker buildx du --verbose

# Órfãos (verifique ANTES de podar)
docker volume ls -f dangling=true
docker ps -a --filter status=exited --format "{{.Names}}\t{{.Status}}"
```

**A ordem segura de limpeza:**

```bash
docker container prune                       # 1. containers parados
docker builder prune --keep-storage 10GB     # 2. cache de build (costuma ser o maior)
docker image prune -a --filter "until=168h"  # 3. imagens sem uso há mais de 7 dias
docker volume ls -f dangling=true            # 4. LISTE os volumes órfãos...
docker volume rm <um por um>                 #    ...e remova o que reconhecer
```

**Nunca comece por `docker system prune -a --volumes`.** Ele é a última linha, não a primeira,
e apaga dados sem perguntar.

---

## 8. Recuperação de desastre — os três casos que acontecem

### "Apaguei o container e perdi o banco"

Se havia volume, o dado está lá:
```bash
docker volume ls
docker run --rm -v NOME_DO_VOLUME:/d alpine ls -la /d
# recrie o container apontando para o mesmo volume
```
Se **não** havia volume, o dado estava na camada de escrita e foi removido com o `docker rm`.
Não há recuperação prática.

### "Rodei `docker compose down -v`"

Os volumes do projeto foram removidos. Recuperação só a partir de backup. É por isso que a
seção 5 existe.

### "O volume existe mas o container não sobe por permissão"

```bash
docker run --rm -v NOME:/d alpine ls -ln /d       # veja os UIDs numéricos
docker run --rm -v NOME:/d alpine chown -R 1000:1000 /d   # ajuste para o UID do app
```

---

## Autoteste

1. Quais das quatro formas de armazenamento sobrevivem a `docker rm`? E a um reboot?
2. Descreva a regra de inicialização de volume nomeado e diga por que ela **não** vale para bind
   mount.
3. Você alterou um arquivo de configuração na imagem e nada mudou no container. Qual é a
   hipótese nº 1?
4. Por que `VOLUME` no Dockerfile é considerado uma armadilha? O que ele provoca ao longo dos
   meses?
5. Um arquivo criado por um container aparece com dono `root` no host. Explique a causa em
   termos de UID e dê duas soluções.
6. Qual é a diferença entre `:z` e `:Z` no SELinux, e qual perigo o `:Z` traz?
7. Por que `npm install` é dramaticamente mais lento em `/mnt/c` no WSL2, e qual é a correção?
8. Por que copiar `/var/lib/postgresql/data` a quente é perigoso, e o que fazer em vez disso?
9. Escreva o comando de backup genérico de um volume, explicando cada `-v`.
10. Liste, em ordem, os quatro passos seguros de limpeza quando o disco enche.
