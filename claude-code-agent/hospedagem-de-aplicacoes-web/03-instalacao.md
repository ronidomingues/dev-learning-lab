# 03 · Manual de instalação — todo o ferramental de deploy

`Nível: iniciante` · `Escrito e verificado em 18/08/2026`
`Máquina de referência: Ubuntu 22.04.5 LTS, kernel 6.8, x86_64`

Este é o arquivo mais chato deste curso e o que mais salva o iniciante. Ele instala **todo o
conjunto** de ferramentas — não só uma. Siga na ordem; cada passo tem verificação.

> **Se você tem pressa ou a máquina é fraca, pule para a
> [seção 12 — Alternativa sem instalar nada](#12-alternativa-sem-instalar-nada).**
> Dá para fazer o curso inteiro no navegador e instalar depois.

---

## Índice

1. [O que vamos instalar e por quê](#1-o-que-vamos-instalar-e-por-quê)
2. [Requisitos reais](#2-requisitos-reais)
3. [Git](#3-git)
4. [Node.js (com gerenciador de versões)](#4-nodejs-com-gerenciador-de-versões)
5. [Docker e Docker Compose](#5-docker-e-docker-compose)
6. [Cliente PostgreSQL (`psql`)](#6-cliente-postgresql-psql)
7. [Cliente Redis/Valkey (`redis-cli`)](#7-cliente-redisvalkey-redis-cli)
8. [Ferramentas de apoio (`curl`, `jq`, `gh`)](#8-ferramentas-de-apoio-curl-jq-gh)
9. [As CLIs das plataformas](#9-as-clis-das-plataformas)
10. [PATH, permissões e rede corporativa](#10-path-permissões-e-rede-corporativa)
11. [Reprodutibilidade, convivência de versões, atualizar e desinstalar](#11-reprodutibilidade-convivência-de-versões-atualizar-e-desinstalar)
12. [Alternativa sem instalar nada](#12-alternativa-sem-instalar-nada)
13. [Solução de problemas — erros literais](#13-solução-de-problemas--erros-literais)
14. [Checklist "ambiente pronto"](#14-checklist-ambiente-pronto)

---

## 1. O que vamos instalar e por quê

| Ferramenta | Para quê | Obrigatório? |
|---|---|---|
| **Git** | Todo deploy moderno parte de um repositório | ✅ sim |
| **Node.js + npm** | Roda o projeto-modelo e instala metade das CLIs | ✅ sim |
| **Docker + Compose** | Subir Postgres e Redis localmente; e é o formato universal de deploy | ✅ sim (ou use os serviços na nuvem direto) |
| **`psql`** | Falar com o PostgreSQL de qualquer provedor, sem painel web | ✅ sim |
| **`redis-cli`** | Falar com Redis/Valkey/Upstash | ✅ sim |
| **`curl`, `jq`** | Testar API, ler JSON | ✅ sim |
| **`gh`** (GitHub CLI) | Criar repositório e segredos de CI sem sair do terminal | recomendado |
| **CLIs de plataforma** (`render`, `railway`, `flyctl`, `vercel`, `wrangler`, `supabase`, `neonctl`) | Deploy, logs, variáveis, túnel de banco | instale **só as das plataformas que você for usar** |

> **Regra que economiza horas:** não instale as sete CLIs. Escolha a pilha em
> [`40-arquiteturas-de-referencia.md`](40-arquiteturas-de-referencia.md) e instale três.

**Versões testadas nesta máquina, em 18/08/2026:**

```
git 2.34.1 · Node v24.18.0 · npm 12.0.1 · Docker 29.1.3 · Docker Compose v5.5.0
curl 7.81.0 · jq 1.6 · Python 3.10.12 · gh 2.4.0
```

**Versões mínimas suportadas:** Git 2.28+ (por causa de `init.defaultBranch`), Node 20+
(a CLI do Supabase exige 20+; o projeto-modelo exige 22+), Docker Engine 24+,
Docker Compose v2+ (o `docker-compose` com hífen, v1, está morto desde julho de 2023).
**Evite:** Node 18 ou anterior (fora de suporte), `docker-compose` v1, PostgreSQL cliente 12
ou anterior (não fala `scram-sha-256` corretamente com servidores novos).

---

## 2. Requisitos reais

| Item | Valor |
|---|---|
| Espaço em disco | ~4 GB para as ferramentas + 6 a 15 GB para imagens Docker |
| RAM | 8 GB mínimo (Docker Compose do projeto-modelo usa ~700 MB) |
| Arquitetura | x86-64 e ARM64 suportados por tudo aqui |
| Conta obrigatória | GitHub (grátis, sem cartão) |
| Cartão de crédito | **não** para o caminho principal deste curso |
| Privilégio de administrador | necessário para Docker; **evitável** para Node e as CLIs (veja a seção 10) |

---

## 3. Git

### 3.1 Linux — família Debian/Ubuntu

```bash
sudo apt update && sudo apt install -y git
```
Instala o Git a partir do repositório da distribuição.

```bash
git --version
# esperado: git version 2.34.1 (ou superior)
```

**Se a saída for diferente** (`command not found`): o pacote não instalou; rode
`sudo apt install -y git` de novo e leia a mensagem de erro — quase sempre é falta de rede ou
`apt` travado por outro processo (`E: Could not get lock`).

**Se a versão for anterior à 2.28**, o Ubuntu é antigo. Use o PPA oficial:

```bash
sudo add-apt-repository -y ppa:git-core/ppa && sudo apt update && sudo apt install -y git
```

### 3.2 Linux — família Fedora/RHEL

```bash
sudo dnf install -y git
```

```bash
git --version
# esperado: git version 2.4x.x
```

### 3.3 macOS (Intel e Apple Silicon)

O macOS já traz um Git antigo embutido nas Command Line Tools. Prefira o do Homebrew.

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```
Instala o Homebrew, o gerenciador de pacotes de fato do macOS.

```bash
brew install git
```

```bash
git --version
# esperado: git version 2.5x.x (do Homebrew), não a versão da Apple
which git
# esperado (Apple Silicon): /opt/homebrew/bin/git
# esperado (Intel):        /usr/local/bin/git
```

**Se `which git` responder `/usr/bin/git`**, o PATH do Homebrew não está ativo. Veja a
[seção 10](#10-path-permissões-e-rede-corporativa) — no Apple Silicon o prefixo é
`/opt/homebrew`, no Intel é `/usr/local`, e essa é a diferença nº 1 entre os dois.

### 3.4 Windows

**Caminho recomendado: WSL2.** Instale o Ubuntu no WSL2 e siga a seção 3.1 lá dentro.
Motivo: praticamente toda a documentação, todo script de instalação e todo `Makefile` do
ecossistema assumem um shell POSIX. Rodar Windows nativo funciona, mas você paga um imposto
diário em incompatibilidades de caminho, de fim de linha (`CRLF`) e de permissão.

```powershell
wsl --install -d Ubuntu-24.04
```
Instala o WSL2 com Ubuntu 24.04. Reinicie quando pedir.

```powershell
wsl --status
# esperado: Versão padrão: 2
```

**Windows nativo**, se você realmente quiser:

```powershell
winget install --id Git.Git -e --source winget
```

```powershell
git --version
# esperado: git version 2.5x.x.windows.1
```

**Configuração obrigatória de fim de linha no Windows nativo** (evita que todo arquivo apareça
como modificado e que scripts `.sh` quebrem em container Linux):

```bash
git config --global core.autocrlf input
```

### 3.5 Configuração mínima (todos os SOs)

```bash
git config --global user.name "Seu Nome"
git config --global user.email "seu@email.com"
git config --global init.defaultBranch main
```

```bash
git config --global --list
# esperado: as três linhas acima
```

---

## 4. Node.js (com gerenciador de versões)

**Não instale Node pelo `apt`/`dnf`.** A versão da distribuição fica velha e você vai precisar
de duas versões diferentes no mesmo mês. Use um gerenciador de versões — é a diferença entre
quem sofre e quem não sofre.

| Método | Quando usar | Veredito |
|---|---|---|
| `nvm` | Padrão histórico, funciona em qualquer lugar | **recomendado para começar** |
| `fnm` | Igual ao `nvm`, escrito em Rust, muito mais rápido | recomendado se você troca de versão o tempo todo |
| `mise` (ex-`rtx`) / `asdf` | Gerencia Node, Python, Go, Terraform… num arquivo só | recomendado se você usa várias linguagens |
| Instalador oficial do nodejs.org | Máquina de uso único | aceitável |
| `apt`/`dnf`/`brew` | — | **evite**: versão velha e conflito com pacotes globais |
| Docker | CI, ou máquina que você não quer sujar | ótimo para CI |

### 4.1 Linux e macOS — via `nvm`

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
```
Baixa e instala o `nvm` no seu diretório pessoal (`~/.nvm`). **Não usa `sudo` — de propósito.**

```bash
exec $SHELL -l
```
Recarrega o shell para que a função `nvm` exista. **Este é o passo que 80% das pessoas pulam**
e depois recebem `nvm: command not found`.

```bash
nvm --version
# esperado: 0.40.3
```

```bash
nvm install 24 && nvm alias default 24
```
Instala o Node 24 (Active LTS em agosto de 2026) e o define como padrão.

```bash
node --version
# esperado: v24.18.0 (ou superior da linha 24)
npm --version
# esperado: 12.x
```

**Se a saída for diferente**: se `nvm: command not found`, o `nvm` não foi carregado — confira
se `~/.bashrc` (ou `~/.zshrc`) contém o bloco `export NVM_DIR=...`; se contém, você não
reabriu o terminal. Se `node` responde uma versão diferente da que você instalou, há **outro**
Node no PATH antes do `nvm`; rode `which -a node` e remova o intruso (`sudo apt remove nodejs`).

> **Sobre versões do Node em agosto de 2026:** as linhas mantidas são 22 (manutenção),
> **24 (Active LTS)** e 26 (Current). A partir da versão 27, em outubro de 2026, o Node passa a
> ter **um major por ano, todos LTS** — a distinção par/ímpar acaba. Use 24 hoje; ele tem
> suporte até 2027.

### 4.2 Windows nativo

```powershell
winget install --id CoreyButler.NVMforWindows -e
```
Instala o `nvm-windows` (projeto diferente do `nvm` do Linux, mesma ideia).

```powershell
nvm install 24.18.0
nvm use 24.18.0
node --version
# esperado: v24.18.0
```

### 4.3 Fixando a versão no projeto (reprodutibilidade)

```bash
echo "24" > .nvmrc
```
Cria o arquivo que diz a versão de Node do projeto. Quem clonar roda `nvm use` e acerta.

Se você usa `mise`/`asdf`, o equivalente é `.tool-versions`:

```bash
printf 'nodejs 24.18.0\n' > .tool-versions
```

---

## 5. Docker e Docker Compose

Docker é o que permite subir PostgreSQL e Redis na sua máquina em 30 segundos, sem instalar
nenhum dos dois — e é o formato que quase toda plataforma de deploy aceita.

### 5.1 Linux — família Debian/Ubuntu (repositório oficial)

**Não use o pacote `docker.io` do Ubuntu** se você quiser a versão atual; use o repositório
oficial da Docker.

```bash
sudo apt-get update && sudo apt-get install -y ca-certificates curl gnupg
```
Instala o necessário para adicionar um repositório assinado.

```bash
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
```
Baixa e instala a chave pública com que a Docker assina os pacotes.

```bash
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
```
Adiciona o repositório oficial e atualiza o índice.

```bash
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```
Instala o motor, a CLI, o runtime de container, o `buildx` e o **plugin do Compose v2**.

```bash
docker --version
# esperado: Docker version 29.x.x (ou 24+)
docker compose version
# esperado: Docker Compose version v5.5.0 (qualquer v2+ serve)
```

**Se `docker compose version` falhar mas `docker-compose --version` funcionar**, você está
com o Compose v1 (Python, descontinuado em julho de 2023). Instale o plugin
(`docker-compose-plugin`) e troque `docker-compose` por `docker compose` em todo lugar.

**Rodar Docker sem `sudo`** — importante e mal explicado:

```bash
sudo usermod -aG docker $USER
```
Adiciona seu usuário ao grupo `docker`.

```bash
newgrp docker   # ou faça logout/login
docker run --rm hello-world
# esperado: "Hello from Docker!" seguido de explicação
```

> **Por que isso importa e qual é o risco:** o socket `/var/run/docker.sock` dá controle total
> ao daemon, que roda como root. **Quem está no grupo `docker` é, na prática, root na máquina**
> (`docker run -v /:/host ...` monta o sistema de arquivos inteiro). Isso é aceitável na sua
> máquina de desenvolvimento e **inaceitável num servidor compartilhado** — lá, use
> [Rootless Docker](https://docs.docker.com/engine/security/rootless/) ou Podman.

### 5.2 Linux — família Fedora/RHEL

```bash
sudo dnf -y install dnf-plugins-core
sudo dnf config-manager --add-repo https://download.docker.com/linux/fedora/docker-ce.repo
sudo dnf install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo systemctl enable --now docker
```

```bash
docker run --rm hello-world
# esperado: "Hello from Docker!"
```

### 5.3 macOS

```bash
brew install --cask docker-desktop
```
Instala o Docker Desktop (aplicativo com interface + motor rodando numa VM Linux).

Abra o aplicativo uma vez para ele pedir permissão de sistema. Depois:

```bash
docker --version && docker compose version
# esperado: ambas as versões impressas
```

**Alternativas no macOS**, se você não quer o Docker Desktop (licença comercial exige
assinatura em empresas com mais de 250 funcionários ou US$ 10 milhões de faturamento):

| Alternativa | Comando | Observação |
|---|---|---|
| **Colima** | `brew install colima docker docker-compose && colima start` | leve, sem interface, Apple Silicon nativo |
| **OrbStack** | `brew install --cask orbstack` | muito rápido; gratuito só para uso pessoal |
| **Podman Desktop** | `brew install podman-desktop` | sem daemon, sem licença comercial |

### 5.4 Windows

**Com WSL2 (recomendado):** instale o Docker Desktop no Windows e ative a integração com a
sua distro WSL em *Settings → Resources → WSL Integration*. Você roda `docker` de dentro do
Ubuntu do WSL e ele conversa com o motor do Windows.

```powershell
winget install --id Docker.DockerDesktop -e
```

```bash
# de dentro do WSL:
docker run --rm hello-world
# esperado: "Hello from Docker!"
```

### 5.5 Verificação real: subir Postgres e Redis em 30 segundos

```bash
docker run -d --name pg-teste -e POSTGRES_PASSWORD=segredo -p 5432:5432 postgres:18
```
Sobe um PostgreSQL 18 em background, com senha `segredo`, ouvindo na porta 5432.

```bash
docker run -d --name redis-teste -p 6379:6379 valkey/valkey:9
```
Sobe um Valkey 9 (o fork BSD do Redis — veja [`30`](30-catalogo-redis.md)) na porta 6379.

```bash
docker ps --format '{{.Names}}\t{{.Status}}'
# esperado:
# pg-teste     Up X seconds
# redis-teste  Up X seconds
```

Limpe depois: `docker rm -f pg-teste redis-teste`.

---

## 6. Cliente PostgreSQL (`psql`)

Você precisa do **cliente**, não do servidor. O servidor virá do Docker ou da nuvem.

### 6.1 Debian/Ubuntu

```bash
sudo apt install -y postgresql-client-18
```
Instala apenas o cliente da linha 18.

```bash
psql --version
# esperado: psql (PostgreSQL) 18.x
```

**Se a saída for** `Error: You must install at least one postgresql-client-<version> package`
(erro real observado nesta máquina em 18/08/2026): você instalou só o
`postgresql-client-common`, que é um seletor de versões, sem nenhuma versão instalada.
Instale `postgresql-client-18`. Se o repositório do Ubuntu não tiver a 18, adicione o
repositório oficial do PostgreSQL (PGDG):

```bash
sudo sh -c 'echo "deb https://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
curl -fsSL https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo gpg --dearmor -o /etc/apt/trusted.gpg.d/pgdg.gpg
sudo apt update && sudo apt install -y postgresql-client-18
```

### 6.2 Fedora/RHEL

```bash
sudo dnf install -y postgresql
psql --version
```

### 6.3 macOS

```bash
brew install libpq && brew link --force libpq
```
Instala só as ferramentas de cliente (`psql`, `pg_dump`, `pg_restore`) sem o servidor.

```bash
psql --version
# esperado: psql (PostgreSQL) 18.x
```

### 6.4 Windows

Use o WSL (seção 6.1). Nativo: baixe o instalador da EDB em
`https://www.enterprisedb.com/downloads/postgres-postgresql-downloads` e **desmarque** o
componente *PostgreSQL Server*, deixando só *Command Line Tools*.

### 6.5 Alternativa: usar `psql` de dentro do Docker (zero instalação)

```bash
docker run --rm -it postgres:18 psql "postgresql://usuario:senha@host:5432/banco"
```
Roda o `psql` dentro de um container descartável. Perfeito quando você não quer instalar nada.

### 6.6 Teste real de conexão

```bash
psql "postgresql://postgres:segredo@localhost:5432/postgres" -c "SELECT version();"
# esperado: uma linha começando com "PostgreSQL 18.x on x86_64-pc-linux-gnu..."
```

---

## 7. Cliente Redis/Valkey (`redis-cli`)

`redis-cli` e `valkey-cli` são intercambiáveis para uso normal.

### 7.1 Debian/Ubuntu

```bash
sudo apt install -y redis-tools
```
Instala **apenas o cliente** (`redis-cli`), sem subir servidor nenhum.

```bash
redis-cli --version
# esperado: redis-cli 6.x ou superior
```

**Se a saída for** `redis-cli: comando não encontrado` (erro real desta máquina antes da
instalação): o pacote não está instalado. No Ubuntu 22.04 o pacote se chama `redis-tools`;
`redis-server` sobe um servidor local que você **não quer** — ele ocupa a porta 6379 e vai
conflitar com o container.

### 7.2 Fedora/RHEL

```bash
sudo dnf install -y valkey    # Fedora 42+ substituiu redis por valkey
valkey-cli --version
```

### 7.3 macOS

```bash
brew install valkey    # traz valkey-cli; ou: brew install redis
valkey-cli --version
```

### 7.4 Alternativa via Docker

```bash
docker run --rm -it valkey/valkey:9 valkey-cli -u "rediss://default:TOKEN@host:6379"
```

### 7.5 Teste real

```bash
redis-cli -h localhost -p 6379 PING
# esperado: PONG
```

**Conectar no Upstash (TLS obrigatório):**

```bash
redis-cli --tls -u "rediss://default:SEU_TOKEN@sua-instancia.upstash.io:6379" PING
# esperado: PONG
```
Se você esquecer `--tls`/`rediss://`, o erro é
`Error: Protocol error, got "\x15" as reply type byte` — é TLS batendo em cliente sem TLS.

---

## 8. Ferramentas de apoio (`curl`, `jq`, `gh`)

```bash
# Debian/Ubuntu
sudo apt install -y curl jq
# Fedora
sudo dnf install -y curl jq
# macOS
brew install curl jq
```

```bash
curl --version | head -1
# esperado: curl 7.81.0 (ou superior)
jq --version
# esperado: jq-1.6 (ou superior)
```

**GitHub CLI** (`gh`) — cria repositório, abre PR e grava segredos de CI sem sair do terminal:

```bash
# Debian/Ubuntu (repositório oficial, porque o do Ubuntu é muito velho)
sudo mkdir -p -m 755 /etc/apt/keyrings
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo tee /etc/apt/keyrings/githubcli-archive-keyring.gpg > /dev/null
sudo chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update && sudo apt install -y gh
```

```bash
# macOS
brew install gh
# Windows
winget install --id GitHub.cli -e
```

```bash
gh --version
# esperado: gh version 2.6x.x (a versão 2.4.0 do repositório do Ubuntu 22.04 é de 2022 — velha demais)
gh auth login
# siga o assistente; escolha HTTPS e autenticação pelo navegador
gh auth status
# esperado: "Logged in to github.com as SEU_USUARIO"
```

---

## 9. As CLIs das plataformas

> **Instale só as que você vai usar.** Todas são opcionais para o primeiro deploy — as
> plataformas fazem tudo pelo painel web. As CLIs valem para logs, variáveis e automação.

### 9.1 Render

```bash
# macOS e Linux (Homebrew)
brew install render-oss/render/render
```
Alternativa sem Homebrew: baixe o binário de `https://github.com/render-oss/cli/releases`.

```bash
render --version
# esperado: 2.23.x (versão atual em 18/08/2026)
render login       # abre o navegador para autorizar
```

Comandos que importam: `render services`, `render deploys create <ID>`,
`render psql <DATABASE_ID>`, `render ssh <SERVICE_ID>`, `render blueprints validate`.

### 9.2 Railway

```bash
# qualquer SO com Node
npm i -g @railway/cli
# macOS
brew install railway
# Linux/macOS/WSL, sem Node
bash <(curl -fsSL railway.com/install.sh)
# Windows
scoop install railway
```

```bash
railway --version
railway login
railway status
```

### 9.3 Fly.io

```bash
# Linux e macOS
curl -L https://fly.io/install.sh | sh
# macOS (Homebrew)
brew install flyctl
# Windows (PowerShell)
pwsh -Command "iwr https://fly.io/install.ps1 -useb | iex"
```

```bash
flyctl version
flyctl auth login
```

> O instalador põe o binário em `~/.fly/bin`. Se `flyctl: command not found` depois de
> instalar, falta `export PATH="$HOME/.fly/bin:$PATH"` no seu `~/.bashrc`/`~/.zshrc`.

### 9.4 Vercel

```bash
npm i -g vercel
vercel --version
vercel login
```

### 9.5 Cloudflare (`wrangler`)

**Não instale global.** A Cloudflare recomenda por projeto, porque a CLI e o runtime andam
juntos:

```bash
npm i -D wrangler@latest
npx wrangler --version
npx wrangler login
```

### 9.6 Supabase

**Instalação global via npm não é suportada** — é dependência de projeto:

```bash
npm install supabase --save-dev
npx supabase --version
```

```bash
# macOS e Linux
brew install supabase/tap/supabase
# Windows
scoop bucket add supabase https://github.com/supabase/scoop-bucket.git
scoop install supabase
```

### 9.7 Neon

```bash
npm i -g neonctl
neonctl --version
neonctl auth
```

---

## 10. PATH, permissões e rede corporativa

### 10.1 PATH — por que "não pegou"

O PATH é a lista de pastas onde o shell procura um comando. Três fatos que resolvem 90% dos
problemas:

1. **Mudança em arquivo de perfil só vale em shell novo.** Editar `~/.bashrc` não afeta o
   terminal já aberto. Rode `exec $SHELL -l` ou abra outro terminal.
2. **Qual arquivo editar depende do shell**, não do SO:

   | Shell | Arquivo | Como descobrir |
   |---|---|---|
   | bash | `~/.bashrc` (Linux), `~/.bash_profile` (macOS) | `echo $SHELL` |
   | zsh (padrão do macOS desde 2019) | `~/.zshrc` | `echo $SHELL` |
   | fish | `~/.config/fish/config.fish` | — |
   | PowerShell | `$PROFILE` | `echo $PROFILE` |

3. **A ordem importa.** Se dois `node` existem, ganha o que aparece primeiro.

```bash
echo "$PATH" | tr ':' '\n'
# lista as pastas, na ordem de busca
which -a node
# mostra TODOS os node encontrados; o primeiro é o que roda
```

Adicionar uma pasta ao PATH, de forma permanente:

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc && exec $SHELL -l
```

### 10.2 Permissões — o caminho certo sem `sudo`

**Nunca use `sudo npm install -g`.** Motivo concreto, não superstição:

- Os pacotes vão para `/usr/lib/node_modules`, pertencentes ao root. Os `postinstall` scripts
  desses pacotes rodam **como root**, com acesso total à sua máquina — um pacote comprometido
  vira comprometimento total. Isso já aconteceu várias vezes na história do npm
  (`event-stream` em 2018, `ua-parser-js` em 2021, os ataques em cadeia de 2025).
- Depois, comandos sem `sudo` falham com `EACCES` e você entra num ciclo de usar `sudo` sempre.

**Solução correta — prefixo no diretório do usuário:**

```bash
mkdir -p ~/.npm-global && npm config set prefix "$HOME/.npm-global"
echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.bashrc && exec $SHELL -l
```

```bash
npm config get prefix
# esperado: /home/SEU_USUARIO/.npm-global
```

Se você usa `nvm`, isso já vem resolvido: tudo mora em `~/.nvm` e nada precisa de `sudo`.

O mesmo vale para Python: **não use `sudo pip install`**. Use `python3 -m venv .venv` ou
`pipx`.

### 10.3 Rede corporativa: proxy, certificado e firewall

**Proxy HTTP:**

```bash
export HTTP_PROXY="http://usuario:senha@proxy.empresa.com:8080"
export HTTPS_PROXY="$HTTP_PROXY"
export NO_PROXY="localhost,127.0.0.1,.empresa.com"
```
Ponha no `~/.bashrc` para valer sempre. **Cuidado:** senha em variável de ambiente vaza em
`ps` e em log de CI — prefira proxy sem autenticação ou `~/.netrc` com permissão `600`.

Cada ferramenta tem sua própria configuração, e elas **não** leem o proxy do sistema:

```bash
npm config set proxy "$HTTP_PROXY" && npm config set https-proxy "$HTTPS_PROXY"
git config --global http.proxy "$HTTP_PROXY"
```

Docker precisa de configuração no daemon:

```bash
sudo mkdir -p /etc/systemd/system/docker.service.d
printf '[Service]\nEnvironment="HTTP_PROXY=%s"\nEnvironment="HTTPS_PROXY=%s"\nEnvironment="NO_PROXY=localhost,127.0.0.1"\n' "$HTTP_PROXY" "$HTTPS_PROXY" | sudo tee /etc/systemd/system/docker.service.d/proxy.conf
sudo systemctl daemon-reload && sudo systemctl restart docker
```

**Certificado interno (TLS interceptado).** Sintoma:
`unable to get local issuer certificate` ou `SELF_SIGNED_CERT_IN_CHAIN`.

```bash
sudo cp certificado-da-empresa.crt /usr/local/share/ca-certificates/
sudo update-ca-certificates
export NODE_EXTRA_CA_CERTS=/usr/local/share/ca-certificates/certificado-da-empresa.crt
```

> **Nunca** resolva isso com `npm config set strict-ssl false` ou
> `NODE_TLS_REJECT_UNAUTHORIZED=0`. Isso desliga a verificação de TLS **globalmente** e
> transforma sua máquina em alvo fácil. É a "solução" mais copiada do Stack Overflow e a
> mais perigosa.

**Firewall corporativo.** Deploy precisa de saída em 443 (HTTPS) para os domínios das
plataformas, e o `psql` precisa de **5432 de saída**, o `redis-cli` de **6379 ou 6380**.
Redes corporativas frequentemente bloqueiam 5432 e 6379 — é a causa nº 1 de "funciona em casa
e não no escritório". Teste antes de culpar o código:

```bash
nc -zv ep-xxx.sa-east-1.aws.neon.tech 5432
# esperado: Connection to ... 5432 port [tcp/postgresql] succeeded!
```

Se estiver bloqueado, use um provedor que ofereça conexão por HTTP na porta 443 (Neon tem
*driver serverless* sobre HTTP; Upstash tem API REST) — veja
[`25`](25-catalogo-postgresql.md) e [`30`](30-catalogo-redis.md).

---

## 11. Reprodutibilidade, convivência de versões, atualizar e desinstalar

### 11.1 Reprodutibilidade

| Ferramenta | Arquivo que fixa a versão | Comando |
|---|---|---|
| Node | `.nvmrc` / `.tool-versions` | `nvm use` / `mise install` |
| npm | `package-lock.json` | `npm ci` (não `npm install`) em CI |
| Docker | tag **e** digest da imagem | `FROM node:24.18.0-slim@sha256:...` |
| PostgreSQL | tag da imagem e versão do servidor | `postgres:18.6` |
| CI | versão fixa na action | `actions/setup-node@v4` com `node-version-file: .nvmrc` |

> **A regra:** `npm install` em CI é um bug esperando para acontecer — ele pode atualizar
> dependências e fazer o build de hoje diferir do de ontem. Use **`npm ci`**, que respeita o
> lockfile ao pé da letra e falha se ele estiver desatualizado.

### 11.2 Convivência de duas versões na mesma máquina

```bash
nvm install 22 && nvm install 24
nvm use 22 && node --version   # v22.x
nvm use 24 && node --version   # v24.x
```

Para PostgreSQL cliente no Debian/Ubuntu, várias versões convivem e o `pg_wrapper` escolhe:

```bash
ls /usr/lib/postgresql/          # versões instaladas
psql --version                    # a escolhida
PGCLUSTER=18/main psql --version  # forçar uma
```

Para bancos locais, o caminho mais simples é **um container por versão, em portas diferentes**:

```bash
docker run -d --name pg16 -p 5416:5432 -e POSTGRES_PASSWORD=x postgres:16
docker run -d --name pg18 -p 5418:5432 -e POSTGRES_PASSWORD=x postgres:18
```

### 11.3 Atualizar com segurança (e voltar atrás)

```bash
# Node: instale a nova, teste, e só então troque o padrão
nvm install 26 && nvm use 26 && npm test
nvm alias default 26      # se passou
nvm alias default 24      # rollback, se não passou
```

```bash
# Docker (Debian/Ubuntu)
sudo apt update && sudo apt install --only-upgrade docker-ce docker-ce-cli
# voltar a uma versão específica:
apt-cache madison docker-ce                       # lista versões disponíveis
sudo apt install docker-ce=5:28.0.1-1~ubuntu.22.04~jammy
```

```bash
# CLIs via npm
npm update -g vercel neonctl @railway/cli
npm i -g vercel@41.0.0     # fixar uma versão anterior
```

### 11.4 Desinstalar por completo (inclusive o que fica para trás)

```bash
# nvm + todos os Nodes + caches
rm -rf ~/.nvm ~/.npm ~/.npm-global ~/.node-gyp
sed -i '/NVM_DIR/d' ~/.bashrc
```

```bash
# Docker (Debian/Ubuntu) — ATENÇÃO: apaga TODAS as imagens, containers e volumes
sudo apt purge -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo rm -rf /var/lib/docker /var/lib/containerd /etc/docker
sudo rm -f /etc/apt/sources.list.d/docker.list /etc/apt/keyrings/docker.gpg
sudo groupdel docker
rm -rf ~/.docker
```

```bash
# Limpeza sem desinstalar (o comando que recupera dezenas de GB)
docker system df                 # mostra quanto está ocupado
docker system prune -a --volumes # remove tudo que não está em uso — INCLUI VOLUMES COM DADOS
```

> **Cuidado real:** `--volumes` apaga bancos de dados locais. Se você tem um Postgres de
> desenvolvimento com dados que importam, faça `pg_dump` antes. Já vi gente perder três
> semanas de dados de teste com esse comando.

```bash
# CLIs de plataforma
npm uninstall -g vercel neonctl @railway/cli
brew uninstall render railway flyctl supabase
rm -rf ~/.fly ~/.config/render ~/.railway ~/.vercel ~/.wrangler ~/.config/supabase
```

---

## 12. Alternativa sem instalar nada

Ofereço isto **antes** do caminho longo porque é o que evita desistência no primeiro dia.

| Opção | O que dá para fazer | Limite gratuito (18/08/2026) |
|---|---|---|
| **GitHub Codespaces** | Tudo deste curso: VS Code no navegador, com Docker, Node e Git prontos | **120 horas-núcleo/mês** e 15 GB-mês (conta GitHub Free); 180 h e 20 GB (Pro) |
| **Gitpod** | Idem | plano gratuito com horas mensais |
| **StackBlitz / CodeSandbox** | Frontend e Node no navegador (WebContainers), sem Docker | generoso para projetos públicos |
| **Painel web das plataformas** | Deploy, logs, variáveis e console SQL — **sem CLI nenhuma** | ilimitado |
| **Console SQL do provedor** | Neon, Supabase e Render têm editor SQL no navegador — dispensa `psql` | ilimitado |
| **Docker Playground** (`labs.play-with-docker.com`) | Experimentar Docker sem instalar | sessões de 4 h |

**Para abrir este próprio material num Codespace:**

```bash
gh codespace create -R SEU_USUARIO/SEU_REPO
gh codespace ssh
```

Tudo neste curso (inclusive o [`07-projeto-modelo/`](07-projeto-modelo/README.md)) roda num
Codespace de 2 núcleos.

---

## 13. Solução de problemas — erros literais

| Mensagem literal | Causa provável | Correção |
|---|---|---|
| `command not found: nvm` | `nvm` é uma função de shell, não um binário; o perfil não foi recarregado | `exec $SHELL -l`; confira o bloco `NVM_DIR` no `~/.bashrc` |
| `EACCES: permission denied, mkdir '/usr/lib/node_modules/...'` | `npm -g` sem permissão | **não** use `sudo`: `npm config set prefix "$HOME/.npm-global"` (seção 10.2) |
| `Cannot connect to the Docker daemon at unix:///var/run/docker.sock` | Daemon parado, ou seu usuário fora do grupo `docker` | `sudo systemctl start docker`; `sudo usermod -aG docker $USER` e reabra a sessão |
| `Error: You must install at least one postgresql-client-<version> package` | Só o `postgresql-client-common` está instalado | `sudo apt install postgresql-client-18` (seção 6.1) |
| `redis-cli: comando não encontrado` | Pacote `redis-tools` ausente | `sudo apt install redis-tools` |
| `Error: Protocol error, got "\x15" as reply type byte` | Servidor exige TLS, cliente conectou sem TLS | use `--tls` e `rediss://` |
| `psql: error: connection to server ... failed: FATAL: no pg_hba.conf entry ... no encryption` | Servidor exige SSL e a URL não pede | acrescente `?sslmode=require` à URL |
| `Error: P1001: Can't reach database server at ...:5432` | Firewall bloqueando 5432, ou banco pausado por inatividade | teste com `nc -zv host 5432`; acorde o projeto no painel (Supabase pausa após 7 dias) |
| `unable to get local issuer certificate` / `SELF_SIGNED_CERT_IN_CHAIN` | TLS interceptado por proxy corporativo | instale o certificado interno + `NODE_EXTRA_CA_CERTS` (seção 10.3). **Não** desligue `strict-ssl` |
| `exec /usr/local/bin/docker-entrypoint.sh: exec format error` | Imagem de arquitetura errada (imagem `amd64` rodando em ARM, ou vice-versa) | `docker build --platform linux/amd64 ...` ou use imagem multiarquitetura |
| `docker: Error response from daemon: driver failed programming external connectivity ... address already in use` | Porta 5432/6379 já ocupada por um Postgres/Redis instalado localmente | `sudo ss -tlnp | grep 5432`; pare o serviço ou publique em outra porta (`-p 5433:5432`) |
| `E: Could not get lock /var/lib/dpkg/lock-frontend` | Outro `apt` rodando (atualização automática) | espere 1–2 min e repita; `ps aux | grep -i apt` para confirmar |
| `fatal: could not read Username for 'https://github.com': No such device or address` | Git sem credencial em ambiente não interativo | `gh auth login`, ou use chave SSH |
| `npm ERR! code ERESOLVE` | Conflito de dependências entre pacotes | leia a árvore impressa; **evite** `--force`; prefira ajustar a versão do pacote conflitante |
| `wrangler: command not found` | Wrangler é dependência de projeto, não global | use `npx wrangler ...` |

---

## 14. Checklist "ambiente pronto"

Cole isto no terminal. **Todas as linhas devem imprimir uma versão, sem erro.**

```bash
git --version
node --version
npm --version
docker --version
docker compose version
psql --version
redis-cli --version
curl --version | head -1
jq --version
gh auth status
```

Teste funcional (o que realmente prova que está pronto):

```bash
docker run -d --name chk-pg -e POSTGRES_PASSWORD=x -p 5432:5432 postgres:18 >/dev/null
docker run -d --name chk-kv -p 6379:6379 valkey/valkey:9 >/dev/null
sleep 5
psql "postgresql://postgres:x@localhost:5432/postgres" -tAc "select 'PG OK'"
redis-cli -h localhost -p 6379 PING
docker rm -f chk-pg chk-kv >/dev/null
```

Saída esperada:

```
PG OK
PONG
```

Se as duas linhas apareceram, siga para [`04-como-comecar.md`](04-como-comecar.md).

---

## Autoteste

1. Por que este manual desaconselha instalar Node pelo `apt` e recomenda `nvm`/`fnm`/`mise`?
2. O que exatamente `sudo usermod -aG docker $USER` concede — e por que isso é inaceitável num servidor compartilhado?
3. Você rodou `nvm install 24` e o terminal responde `nvm: command not found`. O que aconteceu e como se resolve?
4. Qual é o problema de segurança concreto de `sudo npm install -g`, e qual é a alternativa correta?
5. Sua empresa intercepta TLS. Qual é a correção certa e qual é a "correção" perigosa que a internet recomenda?
6. Você recebe `Error: Protocol error, got "\x15" as reply type byte` ao conectar num Redis. O que é isso?
7. Que comando recupera dezenas de GB de disco — e que dado ele pode destruir se você não tomar cuidado?
8. Como você roda `psql` sem instalar `psql`?
9. Qual é a diferença entre `npm install` e `npm ci`, e por que a segunda é obrigatória em CI?

---

### Fontes consultadas (18/08/2026)

- Docker Docs — *Install Docker Engine on Ubuntu / Fedora*, *Rootless mode* — docs.docker.com
- Node.js — *Evolving the Node.js Release Schedule* (mudança para um major por ano a partir da v27, out/2026) — nodejs.org
- nvm — repositório `nvm-sh/nvm`, instalador v0.40.3
- PostgreSQL — *Versioning Policy* e anúncio de 13/08/2026 (18.6, 17.11, 16.15, 15.19, 14.24 e 19 Beta 3) — postgresql.org
- Render — *Render CLI* (v2.23.0) — render.com/docs/cli
- Railway — *CLI* — docs.railway.com/guides/cli
- Supabase — *Local development & CLI: Getting started* (npm global não suportado; exige Node 20+) — supabase.com/docs
- GitHub Docs — *About billing for GitHub Codespaces* (120 h-núcleo/15 GB no Free; 180 h/20 GB no Pro)
- Valkey — notas de versão da linha 9.x
- Saídas de versão reais desta máquina (Ubuntu 22.04.5, x86_64), coletadas em 18/08/2026
