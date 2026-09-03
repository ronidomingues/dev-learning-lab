# 03 · Manual de instalação — passo a passo, por sistema operacional

`Nível: iniciante` · `Manual de campo` · `Última atualização: 11/08/2026`

> **Versões de referência deste manual** (consultadas em **11/08/2026**):
> - **Docker Engine: 29.7.1**, publicada em 04/08/2026. Série **29** é a atual.
> - **Docker Compose:** plugin v2 (`docker compose`, com espaço). O binário legado
>   `docker-compose` (com hífen, v1, Python) está **descontinuado** — não instale.
> - **containerd:** série 2.x. Desde a Engine 29, o *containerd image store* é o **padrão em
>   instalações novas**.
> - **Versão mínima que ainda vale a pena usar:** Engine 24.x. Abaixo disso faltam BuildKit por
>   padrão e correções de segurança relevantes.
> - **Versão a evitar:** qualquer pacote `docker.io` de repositório antigo de distro que
>   entregue Engine < 20.10, e o `docker-compose` v1.
>
> Onde eu **não** consegui confirmar um número exato na data acima, o texto diz isso
> explicitamente em vez de inventar. Sempre confie na saída de `--version` da sua máquina.

---

## Leia isto antes de qualquer coisa

Este manual instala **o conjunto inteiro**, não só o Docker:

1. **Docker Engine** (o daemon que roda containers) ou **Docker Desktop**
2. **Docker CLI** (o comando `docker`)
3. **Buildx** (motor de build moderno — plugin `docker-buildx-plugin`)
4. **Compose v2** (plugin `docker-compose-plugin`)
5. **Git** (você vai versionar Dockerfile e Compose)
6. **Editor + extensão** (VS Code + extensão Docker/Container Tools)
7. **WSL2** (só Windows)
8. **Conta no Docker Hub** (para não bater no limite de 10 *pulls*/hora)

Pule qualquer um desses e você trava mais adiante, em geral no pior momento.

### Índice

- [Alternativa sem instalar nada](#alternativa-sem-instalar-nada) ← **comece por aqui se tiver pressa**
- [Linux — Debian/Ubuntu](#linux--família-debianubuntu)
- [Linux — Fedora/RHEL](#linux--família-fedorarhelrocky)
- [Linux — pós-instalação obrigatória](#linux--pós-instalação-obrigatória)
- [macOS](#macos--intel-e-apple-silicon)
- [Windows](#windows--wsl2-recomendado-e-nativo)
- [Git](#git-em-todos-os-sistemas)
- [Editor e extensões](#editor-e-extensões)
- [Conta no Docker Hub](#conta-no-docker-hub-e-login)
- [PATH e variáveis de ambiente](#path-e-variáveis-de-ambiente)
- [Permissões e o problema do sudo](#permissões-e-o-problema-do-sudo)
- [Rede corporativa: proxy e certificado](#rede-corporativa-proxy-certificado-e-registry-espelhado)
- [Convivência de versões](#convivência-de-versões-na-mesma-máquina)
- [Reprodutibilidade](#reprodutibilidade)
- [Atualizar e voltar atrás](#atualizar-e-voltar-atrás)
- [Desinstalar por completo](#desinstalar-por-completo)
- [Solução de problemas](#solução-de-problemas--erros-literais)
- [Checklist "ambiente pronto"](#checklist-ambiente-pronto)

---

## Alternativa sem instalar nada

**Faça isto primeiro se você só quer começar hoje.** Instalar leva 30–60 minutos e pode dar
errado; estas opções levam 2 minutos e permitem seguir todo o [04-como-comecar.md](04-como-comecar.md)
e boa parte do [06-exemplos.md](06-exemplos.md).

| Opção | Link | O que dá | Limite |
|---|---|---|---|
| **Play with Docker** | [labs.play-with-docker.com](https://labs.play-with-docker.com) | Terminal com Docker real, no navegador. Cria até 5 nós — dá para praticar Swarm | Sessão de **4 horas**, tudo é apagado depois. Exige conta Docker Hub |
| **Killercoda** | [killercoda.com/docker](https://killercoda.com) | Cenários guiados com terminal real | Sessões curtas, ambiente efêmero |
| **GitHub Codespaces** | [github.com/codespaces](https://github.com/codespaces) | VM Linux completa com Docker, VS Code no navegador | Cota gratuita mensal na conta pessoal (verifique a sua; a cota já mudou várias vezes) |
| **Google Cloud Shell** | [shell.cloud.google.com](https://shell.cloud.google.com) | Shell Linux com Docker, 5 GB persistentes | Requer conta Google; horas mensais limitadas |
| **VM na nuvem** | qualquer VPS | Ambiente definitivo, seu | Custa dinheiro (US$ 4–6/mês numa VPS mínima) |

**Recomendação:** comece no *Play with Docker* hoje, e instale localmente no fim de semana. É
o que evita a desistência no primeiro dia.

---

## Linux — família Debian/Ubuntu

Testado em Ubuntu 24.04 LTS e Debian 12, em 11/08/2026. Vale também para Linux Mint, Pop!_OS,
Raspberry Pi OS (trocando `ubuntu` por `debian` na URL do repositório).

### Métodos disponíveis e qual escolher

| Método | Quando usar | Recomendado? |
|---|---|---|
| **Repositório APT oficial da Docker** | Praticamente sempre | ✅ **Sim** — é este manual |
| `apt install docker.io` (repo da distro) | Nunca, se puder evitar | ❌ Versão atrasada, Compose v2 ausente ou defasado |
| Script `get.docker.com` | Máquina descartável, laboratório, CI | ⚠️ Funciona, mas roda um script remoto como root e não é ideal em produção |
| Pacote `.deb` avulso | Máquina sem internet (*air-gapped*) | ⚠️ Só nesse caso; você atualiza tudo à mão |
| Docker Desktop for Linux | Se quiser a GUI | ⚠️ Adiciona uma VM desnecessária no Linux |
| Compilar do fonte (Moby) | Desenvolver o próprio Docker | ❌ Não para uso |

### Passo 1 — remover pacotes conflitantes

```bash
sudo apt remove docker.io docker-compose docker-compose-v2 docker-doc docker-buildx podman-docker containerd runc
```
*O que faz:* remove versões antigas ou concorrentes que sequestram o nome `docker`. É normal o
apt dizer que alguns pacotes nem estavam instalados.

```bash
dpkg -l | grep -E '^ii\s+(docker|containerd|runc)' || echo "limpo"
# esperado: limpo
```
*Se a saída listar pacotes:* remova-os explicitamente pelo nome antes de continuar. Manter dois
Dockers na máquina é fonte garantida de confusão.

> **Atenção:** este passo **não** apaga imagens, containers e volumes — eles ficam em
> `/var/lib/docker`. Para apagar de verdade, veja [Desinstalar por completo](#desinstalar-por-completo).

### Passo 2 — chave GPG do repositório oficial

```bash
sudo apt update
sudo apt install -y ca-certificates curl
```
*O que faz:* garante que o sistema saiba validar certificados TLS e tenha o `curl`.

```bash
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
```
*O que faz:* baixa a chave pública com que a Docker assina os pacotes, e a torna legível pelo
apt. Sem isso, o apt recusa o repositório — corretamente.

> **Debian:** troque `ubuntu` por `debian` na URL acima e no passo 3.

```bash
ls -l /etc/apt/keyrings/docker.asc
# esperado: -rw-r--r-- 1 root root <alguns milhares de bytes> ... /etc/apt/keyrings/docker.asc
```
*Se o arquivo tiver 0 byte:* o download falhou (proxy, DNS, firewall). Veja
[Rede corporativa](#rede-corporativa-proxy-certificado-e-registry-espelhado).

### Passo 3 — adicionar o repositório

```bash
sudo tee /etc/apt/sources.list.d/docker.sources > /dev/null <<EOF
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}")
Components: stable
Architectures: $(dpkg --print-architecture)
Signed-By: /etc/apt/keyrings/docker.asc
EOF
sudo apt update
```
*O que faz:* declara o repositório da Docker no formato **deb822** (`.sources`), que substituiu
o antigo `.list` de uma linha. As substituições `$(...)` preenchem automaticamente o codinome da
sua distro e a arquitetura.

```bash
apt-cache policy docker-ce | head -5
# esperado: linhas com "Candidato:" apontando para uma versão 5:29.x e o repositório download.docker.com
```
*Se `Candidato:` vier `(nenhum)`:* o codinome da sua distro não existe no repositório
(distro muito nova ou derivada não reconhecida). Solução: fixe manualmente um codinome
suportado, ex. `Suites: noble` no Ubuntu 24.04.

### Passo 4 — instalar

```bash
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```
*O que faz:* instala, respectivamente: o daemon, a CLI, o runtime containerd, o motor de build
Buildx e o Compose v2. **Os cinco são necessários** — instalar só `docker-ce` deixa você sem
`docker compose` e sem `docker buildx`.

```bash
sudo docker version
# esperado: seções "Client:" e "Server: Docker Engine - Community", ambas com Version: 29.x.x
```
*Se aparecer só "Client" e um erro de conexão:* o daemon não está rodando — vá para o passo 5.

### Passo 5 — daemon ativo

```bash
sudo systemctl enable --now docker
sudo systemctl status docker --no-pager
```
*O que faz:* habilita o serviço no boot e o inicia agora.

```
# esperado: "Active: active (running)" em verde
```
*Se vier `Failed to start`:* rode `sudo journalctl -u docker -n 50 --no-pager` e procure a
mensagem real. As causas comuns estão na [tabela de erros](#solução-de-problemas--erros-literais).

---

## Linux — família Fedora/RHEL/Rocky

Testado em Fedora 42 e Rocky Linux 9, em 11/08/2026.

### Passo 1 — remover conflitantes

```bash
sudo dnf remove -y docker docker-client docker-client-latest docker-common \
  docker-latest docker-latest-logrotate docker-logrotate docker-selinux \
  docker-engine-selinux docker-engine podman runc
```
*O que faz:* limpa pacotes antigos. **Cuidado:** isso remove o `podman`, que vem instalado por
padrão no Fedora. Se você usa Podman, pule-o da lista e veja
[Convivência de versões](#convivência-de-versões-na-mesma-máquina).

### Passo 2 — adicionar o repositório

```bash
sudo dnf -y install dnf-plugins-core
sudo dnf config-manager addrepo --from-repofile=https://download.docker.com/linux/fedora/docker-ce.repo
```
*O que faz:* registra o repositório oficial. **Em RHEL/Rocky/AlmaLinux**, troque `fedora` por
`rhel` na URL. Em versões mais antigas do dnf, o subcomando é
`sudo dnf config-manager --add-repo <url>` — se a primeira forma falhar, use a segunda.

```bash
dnf repolist | grep docker
# esperado: uma linha com "docker-ce-stable"
```

### Passo 3 — instalar e ativar

```bash
sudo dnf install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo systemctl enable --now docker
```

```bash
sudo docker run --rm hello-world
# esperado: "Hello from Docker!" seguido de uma explicação de 4 parágrafos
```
*Se falhar com erro de SELinux:* veja a [tabela de erros](#solução-de-problemas--erros-literais).
No Fedora/RHEL, SELinux está ativo e **vai** interferir em bind mounts — a solução é a flag
`:z`/`:Z`, explicada em [15-armazenamento-e-volumes.md](15-armazenamento-e-volumes.md).

---

## Linux — pós-instalação obrigatória

### Rodar `docker` sem `sudo`

Por padrão, o socket do daemon (`/var/run/docker.sock`) pertence ao root. Digitar `sudo` a cada
comando é insuportável, e — pior — arquivos criados por containers ficam com dono errado.

```bash
sudo groupadd -f docker
sudo usermod -aG docker $USER
```
*O que faz:* cria o grupo `docker` (se não existir) e adiciona você a ele. Quem está nesse grupo
pode falar com o socket.

```bash
newgrp docker      # aplica o grupo na sessão atual, sem relogar
docker run --rm hello-world
# esperado: "Hello from Docker!" — SEM sudo
```
*Se ainda pedir permissão:* **faça logout e login de novo** (ou reinicie). Mudança de grupo só
vale para sessões criadas depois dela; `newgrp` resolve apenas o terminal atual.

> ### ⚠️ O que ninguém te conta sobre o grupo `docker`
>
> **Estar no grupo `docker` é equivalente a ser root na máquina.** Não é exagero retórico —
> é uma escalada de privilégio de uma linha:
>
> ```bash
> docker run -v /:/host -it alpine chroot /host sh   # você é root no host
> ```
>
> O daemon roda como root e faz o que você mandar. Por isso:
> - Numa máquina pessoal, o grupo `docker` é aceitável e conveniente.
> - Num **servidor compartilhado**, colocar alguém no grupo `docker` é dar root a essa pessoa.
>   Use **rootless mode** (abaixo) ou `sudo` explícito e auditado.

### Rootless mode (opcional, recomendado em servidor multiusuário)

Roda o daemon como seu usuário comum, sem privilégio de root.

```bash
sudo apt install -y docker-ce-rootless-extras uidmap   # Debian/Ubuntu
dockerd-rootless-setuptool.sh install
```
*O que faz:* instala o suporte a mapeamento de UID e configura um daemon pessoal na sua sessão.

```bash
export DOCKER_HOST=unix:///run/user/$(id -u)/docker.sock
docker info | grep -i rootless
# esperado: uma linha contendo "rootless"
```

Adicione a linha `export DOCKER_HOST=...` ao seu `~/.bashrc` para ela persistir.

**O que se perde no rootless:** portas < 1024 exigem configuração extra, alguns drivers de rede
e de storage não funcionam, e o desempenho de rede é levemente pior. **O que se ganha:** uma
falha de escape de container não entrega a máquina.

### Iniciar no boot

```bash
sudo systemctl enable docker.service containerd.service
systemctl is-enabled docker
# esperado: enabled
```

---

## macOS — Intel e Apple Silicon

> **Fato estrutural:** o macOS não tem kernel Linux. **Todo** container Linux no macOS roda
> dentro de uma VM Linux. As opções abaixo diferem em quem gerencia essa VM, não em *se* ela
> existe.

### Requisitos

- macOS 13 (Ventura) ou superior — as versões suportadas mudam a cada release do Docker Desktop
- 8 GB de RAM no mínimo (16 GB é o confortável)
- Apple Silicon (M1–M4+) ou Intel — o instalador é **diferente** para cada um

```bash
uname -m
# esperado: arm64 (Apple Silicon) ou x86_64 (Intel)
```

### Métodos, e qual escolher

| Método | Licença | Recomendado para |
|---|---|---|
| **Docker Desktop** | Grátis com limites; paga em empresa grande | ✅ Padrão, se a licença permitir |
| **colima** (Homebrew, livre) | Apache 2.0 | ✅ Quem quer só a CLI, sem GUI, sem licença |
| **Podman Desktop** | Apache 2.0 | ✅ Alternativa livre com GUI |
| **Rancher Desktop** | Apache 2.0 | ✅ Alternativa livre, traz Kubernetes junto |
| **OrbStack** | Proprietário, pago para uso comercial | ⚠️ O mais rápido do mercado; avalie se a velocidade justifica |

### Opção A — Docker Desktop

```bash
# 1) Instale o Homebrew, se ainda não tiver
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 2) Instale o Docker Desktop
brew install --cask docker
```
*O que faz:* baixa e instala o app. Alternativamente, baixe o `.dmg` de
[docs.docker.com/desktop/install/mac-install](https://docs.docker.com/desktop/install/mac-install/)
— **atenção ao escolher o arquivo certo para Apple Silicon ou Intel**.

Abra o app **Docker** uma vez (ele precisa de autorização do sistema e instala um helper
privilegiado). Espere o ícone da baleia na barra de menu ficar estável.

```bash
docker version
# esperado: Client e Server, ambos com versão 2x.x
docker run --rm hello-world
# esperado: "Hello from Docker!"
```
*Se der `Cannot connect to the Docker daemon`:* o app não está rodando. Abra-o pelo Launchpad e
aguarde.

**Ajuste de recursos** (Settings → Resources): o padrão costuma ser conservador. Em máquina de
16 GB, dar 6–8 GB e 4 CPUs à VM é razoável. Reduzir o *Virtual disk limit* não recupera espaço
já usado — veja [Desinstalar por completo](#desinstalar-por-completo).

**Habilite o VirtioFS** (Settings → General → *file sharing implementation*) se estiver
disponível. É o que torna bind mounts toleráveis no macOS.

### Opção B — colima (sem GUI, sem licença)

```bash
brew install docker docker-compose docker-buildx colima
colima start --cpu 4 --memory 8 --disk 60 --vm-type vz --mount-type virtiofs
```
*O que faz:* instala a CLI (sem o Desktop) e sobe uma VM Linux enxuta com o daemon. `--vm-type vz`
usa o framework de virtualização nativo da Apple; `virtiofs` é o modo de compartilhamento de
arquivos mais rápido.

```bash
docker context ls
# esperado: uma linha "colima" marcada com * (contexto ativo)
docker run --rm hello-world
# esperado: "Hello from Docker!"
```

Os plugins instalados pelo Homebrew precisam ser registrados para o `docker` enxergá-los:

```bash
mkdir -p ~/.docker/cli-plugins
ln -sfn $(brew --prefix)/opt/docker-compose/bin/docker-compose ~/.docker/cli-plugins/docker-compose
ln -sfn $(brew --prefix)/opt/docker-buildx/bin/docker-buildx  ~/.docker/cli-plugins/docker-buildx
docker compose version
# esperado: "Docker Compose version v2.x.x"
```

---

## Windows — WSL2 (recomendado) e nativo

> **Recomendação e o porquê:** use **WSL2**. Containers Linux no Windows sempre rodam numa VM;
> a diferença é que com WSL2 essa VM é integrada, compartilha memória dinamicamente com o
> Windows e dá I/O de disco muito melhor **desde que seus arquivos estejam dentro do sistema de
> arquivos do Linux**. Trabalhar em `/mnt/c/...` a partir do WSL é a causa nº 1 de "Docker no
> Windows é lento".

### Passo 1 — habilitar o WSL2

Abra o **PowerShell como Administrador**:

```powershell
wsl --install -d Ubuntu
```
*O que faz:* habilita os recursos de virtualização necessários, instala o WSL2 e a distro
Ubuntu numa tacada. **Reinicie a máquina** quando pedir.

```powershell
wsl --status
# esperado: "Versão padrão: 2"
wsl --list --verbose
# esperado: uma linha "Ubuntu   Running   2"  — a coluna final PRECISA ser 2, não 1
```
*Se a versão for 1:* `wsl --set-version Ubuntu 2` e depois `wsl --set-default-version 2`.
*Se der erro de virtualização:* entre na BIOS/UEFI e habilite **Intel VT-x** ou **AMD-V**. Em
notebooks é comum vir desabilitado de fábrica.

```powershell
wsl --update
```
*O que faz:* atualiza o kernel do WSL2. Kernel velho causa falhas obscuras no Docker.

### Passo 2 — instalar o Docker Desktop

Baixe de [docs.docker.com/desktop/install/windows-install](https://docs.docker.com/desktop/install/windows-install/)
e execute. Na tela de opções, marque **"Use WSL 2 instead of Hyper-V"**.

Depois de instalado: **Settings → Resources → WSL Integration** → habilite a integração com a
distro `Ubuntu`. Sem isso, o comando `docker` não existe dentro do WSL.

### Passo 3 — verificar de dentro do WSL

Abra o terminal **Ubuntu** (não o PowerShell):

```bash
docker version
# esperado: Client e Server presentes, versão 2x.x
docker run --rm hello-world
# esperado: "Hello from Docker!"
```
*Se `docker: command not found` dentro do WSL:* a integração WSL não foi habilitada no
Docker Desktop. Volte às Settings.

### Passo 4 — trabalhar no lugar certo (isto é performance, não estética)

```bash
# ✅ CERTO — sistema de arquivos do Linux, rápido
cd ~
mkdir -p ~/projetos && cd ~/projetos

# ❌ ERRADO — disco do Windows via tradução de protocolo, 10x a 50x mais lento
cd /mnt/c/Users/SeuNome/projetos
```

No VS Code, instale a extensão **WSL** e abra a pasta com `code .` **de dentro do WSL**. A
janela mostrará `[WSL: Ubuntu]` no canto inferior esquerdo — é assim que você confirma.

### Alternativa: Docker Engine dentro do WSL, sem Docker Desktop

Se a licença do Docker Desktop for problema na sua empresa, você pode instalar o **Docker Engine
nativamente dentro da distro WSL** seguindo a seção [Debian/Ubuntu](#linux--família-debianubuntu)
deste manual, de ponta a ponta. Funciona. Duas ressalvas:

- O daemon não inicia sozinho no boot do Windows. Adicione ao `~/.bashrc`:
  ```bash
  # inicia o daemon se não estiver rodando (WSL não usa systemd por padrão em versões antigas)
  if ! service docker status > /dev/null 2>&1; then sudo service docker start > /dev/null 2>&1; fi
  ```
  Em WSL com `systemd=true` habilitado no `/etc/wsl.conf`, use `systemctl enable docker` normalmente.
- Não há integração com o Docker do lado Windows — o que é irrelevante se você trabalha só no WSL.

### Windows containers (nicho)

Containers que rodam **Windows de verdade** exigem host Windows e imagens base da Microsoft
(`mcr.microsoft.com/windows/servercore`). São gigantes (GB), lentos para iniciar e o
isolamento de versão de kernel é rígido. Só fazem sentido para .NET Framework legado que não
migra para .NET moderno. Este material **não** cobre esse caminho.

---

## Git em todos os sistemas

```bash
# Debian/Ubuntu
sudo apt install -y git
# Fedora/RHEL
sudo dnf install -y git
# macOS
brew install git
# Windows: já vem no WSL Ubuntu; para o lado Windows, use https://git-scm.com/download/win
```

```bash
git --version
# esperado: git version 2.4x.x ou superior
git config --global user.name "Seu Nome"
git config --global user.email "seu@email"
git config --global init.defaultBranch main
```

---

## Editor e extensões

**VS Code** é o padrão de fato, e as extensões abaixo poupam tempo real:

| Extensão | ID | O que faz |
|---|---|---|
| Container Tools / Docker | `ms-azuretools.vscode-docker` | Realce e autocompletar em Dockerfile e Compose, painel de containers, anexar terminal |
| Dev Containers | `ms-vscode-remote.remote-containers` | Abrir o projeto **dentro** de um container, com o editor junto |
| WSL | `ms-vscode-remote.remote-wsl` | Obrigatória no Windows |
| YAML | `redhat.vscode-yaml` | Valida `compose.yaml` antes de você descobrir o erro no terminal |
| Hadolint | `exiasr.hadolint` | *Linter* de Dockerfile — pega má prática enquanto você digita (exige o binário `hadolint`) |

```bash
code --version
# esperado: número de versão em três linhas
```

---

## Conta no Docker Hub e login

Sem login você tem **10 *pulls* por hora, contados por IP** — e IP compartilhado (empresa,
universidade, CGNAT de provedor) estoura esse número em minutos. Com conta gratuita, são **100
por hora**. Isso, sozinho, justifica criar a conta.

1. Crie a conta em [hub.docker.com/signup](https://hub.docker.com/signup) (gratuita, sem cartão).
2. Gere um **Personal Access Token** em *Account Settings → Personal access tokens*. **Nunca use
   a senha da conta na CLI** — o token pode ser revogado sozinho e tem escopo limitado.

```bash
echo "SEU_TOKEN_AQUI" | docker login -u SEU_USUARIO --password-stdin
# esperado: Login Succeeded
```
*Por que `--password-stdin`:* passar o segredo como argumento (`-p senha`) o grava no histórico
do shell e o expõe na lista de processos.

```bash
docker system info | grep -i username
# esperado: Username: SEU_USUARIO
```

> **Onde a credencial fica:** por padrão, em `~/.docker/config.json`, **codificada em base64,
> não criptografada**. Em máquina compartilhada, instale um *credential helper*
> (`docker-credential-pass` no Linux, Keychain no macOS, `wincred` no Windows).

---

## PATH e variáveis de ambiente

### Conferir se o `docker` está no PATH

```bash
which docker          # Linux/macOS
# esperado: /usr/bin/docker  ou  /usr/local/bin/docker
```
```powershell
where.exe docker      # Windows
```
*Se não retornar nada:* o binário existe mas o shell não o encontra.

### Corrigir, e em qual arquivo

| Shell | Arquivo de perfil | Como saber qual é o seu |
|---|---|---|
| bash | `~/.bashrc` (interativo) e `~/.bash_profile` (login) | `echo $SHELL` → `/bin/bash` |
| zsh (padrão no macOS) | `~/.zshrc` | `echo $SHELL` → `/bin/zsh` |
| fish | `~/.config/fish/config.fish` | `echo $SHELL` → `/usr/bin/fish` |
| PowerShell | `$PROFILE` (`notepad $PROFILE`) | — |

```bash
echo 'export PATH="/usr/local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc        # <- ESTE passo é o que as pessoas esquecem
```

> **Por que "não pegou" antes de reabrir o terminal:** o arquivo de perfil é lido **uma vez**,
> quando o shell inicia. Editá-lo não afeta shells já abertos. `source` relê o arquivo na
> sessão atual; abrir um terminal novo tem o mesmo efeito.

### Variáveis que importam

| Variável | Para que serve | Exemplo |
|---|---|---|
| `DOCKER_HOST` | Aponta para outro daemon (remoto, rootless, colima) | `unix:///run/user/1000/docker.sock` |
| `DOCKER_CONTEXT` | Seleciona um *context* nomeado (melhor que `DOCKER_HOST`) | `docker context use remoto` |
| `DOCKER_BUILDKIT` | Liga/desliga o BuildKit (já é padrão desde a Engine 23) | `1` |
| `COMPOSE_PROJECT_NAME` | Prefixo dos recursos criados pelo Compose | `meuapp` |
| `COMPOSE_FILE` | Arquivo Compose padrão | `compose.yaml:compose.dev.yaml` |
| `DOCKER_DEFAULT_PLATFORM` | Força a arquitetura das imagens | `linux/amd64` (útil no Apple Silicon) |

```bash
docker context ls
# esperado: lista de contextos, com * no ativo
```

---

## Permissões e o problema do `sudo`

### Regra geral

| Situação | Faça | Não faça |
|---|---|---|
| Rodar `docker` no seu desktop | Entre no grupo `docker` | `sudo docker ...` toda vez |
| Servidor com vários usuários | **rootless mode** ou `sudo` auditado | Colocar todo mundo no grupo `docker` |
| Container que escreve em bind mount | Rode com `--user "$(id -u):$(id -g)"` | Rodar como root e depois `sudo chown` |
| Instalar ferramentas | Pacote da distro ou gerenciador de versão | `sudo npm install -g`, `sudo pip install` |

### Por que `sudo docker` estraga arquivos

O daemon roda como root. Se o processo dentro do container roda como root e escreve num
diretório do host montado por bind mount, os arquivos nascem **pertencendo ao root no host**.
Aí você não consegue mais editá-los no seu editor e precisa de `sudo chown -R $USER:` para
consertar. É desagradável e evitável:

```bash
docker run --rm -v "$PWD:/app" -w /app --user "$(id -u):$(id -g)" node:22-alpine npm init -y
ls -l package.json
# esperado: o dono é você, não root
```

### Por que `sudo npm install -g` e `sudo pip install` são problema

Não é etiqueta — é dano concreto:

1. **Corrompe a árvore de permissões**: parte dos arquivos passa a ser do root e o gerenciador
   de pacotes não consegue mais atualizá-los sem `sudo`, criando dependência permanente.
2. **Executa código arbitrário como root**: scripts de `postinstall` de um pacote qualquer
   rodam com privilégio total.
3. **Mistura com o gerenciador de pacotes do sistema**, que também escreve nos mesmos diretórios,
   e o próximo `apt upgrade` sobrescreve ou quebra sua instalação.

O caminho certo é usar um gerenciador de versão por usuário: `nvm`, `pyenv`, `mise`, `asdf`. Ou
— apropriadamente — rodar a ferramenta **dentro de um container**.

---

## Rede corporativa: proxy, certificado e registry espelhado

### Proxy para o daemon

O daemon é um serviço do sistema; ele **não** lê as variáveis de proxy do seu shell.

```bash
sudo mkdir -p /etc/systemd/system/docker.service.d
sudo tee /etc/systemd/system/docker.service.d/http-proxy.conf > /dev/null <<'EOF'
[Service]
Environment="HTTP_PROXY=http://proxy.empresa.com:3128"
Environment="HTTPS_PROXY=http://proxy.empresa.com:3128"
Environment="NO_PROXY=localhost,127.0.0.1,.empresa.com,registry.interno"
EOF
sudo systemctl daemon-reload
sudo systemctl restart docker
```

```bash
sudo systemctl show --property=Environment docker
# esperado: a linha com HTTP_PROXY e HTTPS_PROXY que você definiu
```

### Proxy para a CLI e para os builds

```bash
mkdir -p ~/.docker
cat > ~/.docker/config.json <<'EOF'
{
  "proxies": {
    "default": {
      "httpProxy":  "http://proxy.empresa.com:3128",
      "httpsProxy": "http://proxy.empresa.com:3128",
      "noProxy":    "localhost,127.0.0.1,.empresa.com"
    }
  }
}
EOF
```
*O que faz:* injeta as variáveis de proxy dentro dos containers e dos builds automaticamente —
sem isso, `apt-get` **dentro** do Dockerfile falha mesmo com o daemon configurado.

### Certificado TLS interno (inspeção de tráfego / *TLS interception*)

Sintoma: `x509: certificate signed by unknown authority`.

```bash
# Registry interno com certificado próprio
sudo mkdir -p /etc/docker/certs.d/registry.empresa.com:5000
sudo cp ca-empresa.crt /etc/docker/certs.d/registry.empresa.com:5000/ca.crt
sudo systemctl restart docker
```

E, para que os builds também confiem, copie a CA para dentro da imagem:

```dockerfile
COPY ca-empresa.crt /usr/local/share/ca-certificates/
RUN update-ca-certificates
```

### Registry espelhado (e como escapar do limite do Docker Hub)

```bash
sudo tee /etc/docker/daemon.json > /dev/null <<'EOF'
{
  "registry-mirrors": ["https://mirror.empresa.com"],
  "insecure-registries": []
}
EOF
sudo systemctl restart docker
docker system info | grep -A2 "Registry Mirrors"
# esperado: a URL do espelho listada
```

> **`insecure-registries` desliga a verificação TLS.** Só use em rede isolada de laboratório, e
> saiba que está trocando segurança por conveniência.

---

## Convivência de versões na mesma máquina

**Não instale dois Docker Engines na mesma máquina.** Ao contrário de Node ou Python, o Docker
tem um daemon único, um socket único e um diretório de dados único; duas instalações brigam.

Como resolver os casos reais:

| Necessidade | Solução |
|---|---|
| Testar uma versão diferente do Engine | Uma VM ou um servidor separado, acessado por `docker context` |
| Vários daemons na mesma máquina | `docker context` + rootless (um daemon por usuário) |
| Podman e Docker convivendo | Convivem sem conflito. `podman` usa socket próprio. Evite o pacote `podman-docker`, que cria um `docker` falso |
| Versões diferentes do Compose | Instale binários avulsos em `~/.docker/cli-plugins/` e alterne por symlink |
| Versões diferentes de linguagem/runtime | **Não é problema de Docker**: cada imagem traz a sua. É exatamente a vantagem — `node:20` e `node:22` coexistem sem conflito |

```bash
docker context create servidor --docker "host=ssh://usuario@servidor"
docker context use servidor
docker ps            # agora lista os containers do servidor remoto
docker context use default
```

---

## Reprodutibilidade

Instalação reprodutível é o que separa "funcionou uma vez" de "funciona para a equipe inteira".

| Mecanismo | Arquivo | O que garante |
|---|---|---|
| **Tag imutável por digest** | `FROM node:22.4.0-alpine@sha256:abc123...` | O *mesmo byte* de imagem base, sempre. Tag pode ser reescrita; digest, não |
| **Lockfile da linguagem** | `package-lock.json`, `poetry.lock`, `go.sum`, `Cargo.lock` | Mesmas dependências |
| **`.dockerignore`** | `.dockerignore` | Contexto de build idêntico entre máquinas (e build mais rápido) |
| **Versão da ferramenta** | `.tool-versions` (mise/asdf) | Mesma versão de CLI auxiliar na equipe |
| **Dev Container** | `.devcontainer/devcontainer.json` | Ambiente de desenvolvimento inteiro versionado |
| **Compose fixado** | `image: postgres:16.3` (nunca `postgres:latest`) | Serviços de apoio iguais para todos |

```bash
# Descubra o digest de uma imagem que você já usa
docker image inspect --format '{{index .RepoDigests 0}}' node:22-alpine
# esperado: node@sha256:<64 caracteres hexadecimais>
```

> **`latest` é uma mentira útil.** Não significa "a mais recente": é apenas a tag padrão quando
> nenhuma é dada, e ela é reescrita a cada publicação. Em produção, `latest` é a causa de
> "ontem funcionava".

---

## Atualizar e voltar atrás

### Atualizar

```bash
# Debian/Ubuntu
sudo apt update && sudo apt upgrade docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
# Fedora/RHEL
sudo dnf upgrade docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
# macOS / Windows: o Docker Desktop avisa e atualiza sozinho
```

```bash
docker version --format '{{.Server.Version}}'
# esperado: a nova versão
```

> **Antes de atualizar em servidor:** containers em execução são **reiniciados** quando o daemon
> reinicia (a menos que `live-restore` esteja habilitado). Planeje janela. E leia as notas da
> versão: a Engine 29 mudou o *image store* padrão para containerd em instalações novas — o que
> **não** migra imagens existentes automaticamente numa atualização, mas muda o comportamento de
> quem reinstala do zero.

### Voltar atrás

```bash
apt-cache madison docker-ce
# esperado: lista de versões disponíveis, ex.: 5:29.7.1-1~ubuntu.24.04~noble

sudo apt install -y --allow-downgrades docker-ce=<VERSAO> docker-ce-cli=<VERSAO>
sudo apt-mark hold docker-ce docker-ce-cli    # impede que o upgrade automático suba de novo
```
*Para liberar depois:* `sudo apt-mark unhold docker-ce docker-ce-cli`.

---

## Desinstalar por completo

**A remoção do pacote não apaga os dados.** Imagens, containers, volumes e redes ficam em
`/var/lib/docker` e podem ocupar dezenas de GB indefinidamente.

### Linux

```bash
# 1) Ver o que está ocupando espaço ANTES de decidir
docker system df
# esperado: tabela com Images / Containers / Local Volumes / Build Cache e o "RECLAIMABLE"

# 2) Remover os pacotes
sudo apt purge -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin \
     docker-compose-plugin docker-ce-rootless-extras
# (Fedora/RHEL: sudo dnf remove -y ...)

# 3) Apagar TODOS os dados — imagens, containers e VOLUMES. Irreversível.
sudo rm -rf /var/lib/docker /var/lib/containerd

# 4) Configuração e credenciais
sudo rm -rf /etc/docker /etc/apt/sources.list.d/docker.sources /etc/apt/keyrings/docker.asc
rm -rf ~/.docker

# 5) Grupo
sudo groupdel docker
```

> ⚠️ O passo 3 **apaga volumes**. Se houver banco de dados ali, o dado morre. Faça backup antes:
> `docker run --rm -v meu_volume:/d -v "$PWD:/b" alpine tar czf /b/backup.tgz -C /d .`

### macOS

```bash
# Docker Desktop: use "Troubleshoot → Uninstall" no próprio app, depois:
rm -rf ~/Library/Group\ Containers/group.com.docker
rm -rf ~/Library/Containers/com.docker.docker
rm -rf ~/.docker ~/Library/Application\ Support/Docker\ Desktop
rm -f  ~/Library/Preferences/com.docker.docker.plist

# colima
colima delete
brew uninstall colima docker docker-compose docker-buildx
```

### Windows

Painel de Controle → Programas → desinstalar **Docker Desktop**. Depois, no PowerShell como
Administrador:

```powershell
wsl --unregister docker-desktop
Remove-Item -Recurse -Force "$env:APPDATA\Docker", "$env:LOCALAPPDATA\Docker", "$env:USERPROFILE\.docker"
```

### Limpeza sem desinstalar (o caso comum: disco cheio)

```bash
docker system df                 # o que ocupa espaço
docker system prune              # remove containers parados, redes órfãs e cache pendente
docker system prune -a           # + TODAS as imagens não usadas por nenhum container
docker system prune -a --volumes # + VOLUMES órfãos ⚠️ APAGA DADOS
docker builder prune --keep-storage 10GB   # limita o cache de build
```

---

## Solução de problemas — erros literais

| Mensagem (literal) | Causa provável | Correção |
|---|---|---|
| `Cannot connect to the Docker daemon at unix:///var/run/docker.sock. Is the docker daemon running?` | O daemon não está no ar, ou `DOCKER_HOST` aponta para o lugar errado | `sudo systemctl start docker` (Linux) · abrir o Docker Desktop (mac/Win) · `colima start` · conferir `echo $DOCKER_HOST` |
| `permission denied while trying to connect to the Docker daemon socket` | Seu usuário não está no grupo `docker`, ou o grupo ainda não valeu nesta sessão | `sudo usermod -aG docker $USER` e então **logout/login** (ou `newgrp docker`) |
| `docker: command not found` | Binário ausente ou fora do PATH; no Windows, integração WSL desligada | `which docker` · reinstalar · Docker Desktop → Settings → Resources → WSL Integration |
| `toomanyrequests: You have reached your pull rate limit` | Limite do Docker Hub: 10 *pulls*/h sem login, 100/h com conta grátis | `docker login` · usar espelho (`registry-mirrors`) · usar GHCR/Quay · plano pago |
| `x509: certificate signed by unknown authority` | Proxy corporativo com inspeção TLS, ou registry com certificado próprio | Instalar a CA em `/etc/docker/certs.d/<host>/ca.crt` e no sistema; reiniciar o daemon |
| `no space left on device` | `/var/lib/docker` cheio de imagens, volumes e cache de build | `docker system df` → `docker system prune -a` · `docker builder prune` · aumentar o disco |
| `Error response from daemon: driver failed programming external connectivity ... address already in use` | Outro processo já ocupa a porta do host | `ss -tlnp \| grep :8080` para achar o culpado · trocar a porta do lado esquerdo do `-p` |
| `WSL 2 installation is incomplete` / `Hardware assisted virtualization ... must be enabled` | VT-x/AMD-V desabilitado na BIOS, ou kernel do WSL velho | Habilitar virtualização na BIOS/UEFI · `wsl --update` · reiniciar |
| `exec /app/entrypoint.sh: no such file or directory` (e o arquivo existe!) | Fim de linha CRLF do Windows, ou binário de arquitetura errada | `dos2unix entrypoint.sh` · `.gitattributes` com `* text eol=lf` · conferir `--platform` |
| `exec format error` | Imagem de outra arquitetura (amd64 num ARM, ou vice-versa) | `docker run --platform linux/amd64 ...` · construir multi-arch com `buildx` |
| `Permission denied` num arquivo dentro de bind mount, só em Fedora/RHEL | SELinux bloqueando o acesso do container | Use `-v "$PWD:/app:Z"` (rótulo exclusivo) ou `:z` (compartilhado) |
| `failed to solve: process "/bin/sh -c apt-get update" did not complete successfully` | Sem rede/DNS dentro do build, quase sempre proxy não configurado para builds | Configurar `proxies` em `~/.docker/config.json` · conferir DNS do daemon |
| `manifest unknown` / `pull access denied` | Nome ou tag errados, ou imagem privada sem login | Conferir o nome exato no registry · `docker login` |
| `The container name "/x" is already in use by container ...` | Já existe um container com esse nome, mesmo parado | `docker rm x` · ou use `--rm` para containers efêmeros |

---

## Checklist "ambiente pronto"

Rode tudo. Se um item falhar, resolva antes de ir para o [04-como-comecar.md](04-como-comecar.md).

```bash
docker version                                  # Client E Server, ambos 29.x (ou >= 24)
docker compose version                          # Docker Compose version v2.x.x
docker buildx version                           # github.com/docker/buildx v0.x.x
docker run --rm hello-world                     # "Hello from Docker!"
docker run --rm alpine ping -c1 1.1.1.1         # rede saindo do container: "1 packets received"
docker run --rm alpine nslookup docker.com      # DNS dentro do container resolve
docker run -d --rm --name t -p 8080:80 nginx:alpine && sleep 2 && curl -sI localhost:8080 | head -1 && docker stop t
                                                # "HTTP/1.1 200 OK"  → publicação de porta funciona
docker volume create teste && docker run --rm -v teste:/d alpine sh -c 'echo ok > /d/f' \
  && docker run --rm -v teste:/d alpine cat /d/f && docker volume rm teste
                                                # "ok"  → volumes funcionam
docker run --rm -v "$PWD:/w" -w /w alpine ls    # bind mount enxerga seus arquivos
git --version                                   # 2.4x ou superior
docker system info | grep -i username           # você está logado no Hub
docker system df                                # sem erro, e você sabe quanto está ocupando
```

Dez linhas verdes = ambiente pronto. Siga para [04-como-comecar.md](04-como-comecar.md).

---

## Autoteste

1. Por que instalar apenas `docker-ce` (sem os plugins) deixa o ambiente incompleto?
2. Você adicionou seu usuário ao grupo `docker` e continua tomando `permission denied`. Por quê?
3. Explique, em uma frase e com um comando, por que estar no grupo `docker` equivale a ter root.
4. Qual é a diferença prática entre `docker-compose` e `docker compose`, e qual usar?
5. No Windows, por que trabalhar em `/mnt/c/...` a partir do WSL degrada tanto o desempenho?
6. Seu build falha com `x509: certificate signed by unknown authority` só na rede da empresa.
   Quais dois lugares precisam receber a CA?
7. `sudo apt purge docker-ce` libera espaço em disco? Justifique.
8. Por que fixar `FROM node:22-alpine` ainda não é reprodutível, e o que torna?
9. Você recebe `exec format error` ao rodar uma imagem num Mac M3. O que aconteceu e como
   resolver de dois jeitos?

---

### Fontes consultadas (11/08/2026)

- [Docker Docs — Install Docker Engine on Ubuntu](https://docs.docker.com/engine/install/ubuntu/) — comandos exatos do repositório APT em formato deb822
- [Docker Engine v29 Release — Docker Blog](https://www.docker.com/blog/docker-engine-version-29/) e [Docker Engine 29 release notes](https://docs.docker.com/engine/release-notes/29/) — containerd image store como padrão em instalações novas, backend nftables experimental
- [Linuxiac — Docker Engine 29: Containerd Becomes Default, Experimental nftables Support](https://linuxiac.com/docker-engine-29-containerd-becomes-default-experimental-nftables-support/)
- [endoflife.date — Docker Engine](https://endoflife.date/docker-engine) — versão 29.7.1 publicada em 04/08/2026
- [Docker Docs — Usage and rate limits](https://docs.docker.com/docker-hub/usage/) e [GitLab Support — Docker Hub rate limiting](https://support.gitlab.com/hc/en-us/articles/20028360858140-Docker-Hub-rate-limiting-impacts-GitLab-pipelines) — 10 *pulls*/hora sem autenticação, 100/hora com conta gratuita, desde 01/04/2025
