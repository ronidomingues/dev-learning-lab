# 03 · Manual de instalação

`Nível: iniciante` · `Atualizado em: 14/08/2026`
`Testado em: Ubuntu 22.04.5 LTS (x86_64), Node v24.18.0, Docker 29.1.3, curl 7.81.0, git 2.34.1`
`Versões correntes na data: Node 24.19.0 LTS (03/08/2026) · PostgreSQL 18.6 (13/08/2026) · nvm 0.40.6`

Optimistic locking é uma **técnica**, não um produto: não existe um `apt install
optimistic-locking`. O que este manual instala é o **ambiente para praticá-la**:

| Tecnologia | Obrigatória? | Para quê |
|---|---|---|
| **Node.js 24** | **sim** | projeto-modelo, exemplos, laboratórios |
| **git** | quase | clonar/versionar seus experimentos |
| **curl** | quase | exercitar `ETag`/`If-Match` na mão |
| **Docker** | não | subir PostgreSQL sem instalar nada no sistema |
| **PostgreSQL 18 + `psql`** | não | laboratórios de isolamento (`SERIALIZABLE`, `40001`) |
| **JDK 21 + Maven** | não | exemplo JPA/Hibernate do [`06`](06-exemplos.md) |
| **Python 3.12 + Django** | não | exemplo Django do [`06`](06-exemplos.md) |
| **.NET 10 SDK** | não | exemplo EF Core do [`06`](06-exemplos.md) |

> Se o seu objetivo é entender e usar, **só o Node basta**. Todo o resto é para aprofundar.

---

## 0. Alternativa sem instalar **nada** — comece hoje

Leia isto antes de baixar qualquer coisa. Você consegue fazer 80% deste curso no navegador.

### 0.1 SQL puro, no navegador

| Serviço | O que serve | Link | Precisa de conta? |
|---|---|---|---|
| **DB Fiddle** | rodar `CREATE TABLE`/`UPDATE ... WHERE version = ?` em PostgreSQL/MySQL/SQLite | <https://www.db-fiddle.com/> | não |
| **SQLime** | SQLite inteiro rodando em WebAssembly, offline depois de carregado | <https://sqlime.org/> | não |
| **PostgreSQL Playground (Neon)** | Postgres real, efêmero | <https://neon.com/> | sim (gratuito) |

Cole isto em qualquer um deles e você já executou optimistic locking:

```sql
CREATE TABLE conta (id INTEGER PRIMARY KEY, saldo INTEGER, version INTEGER);
INSERT INTO conta VALUES (1, 100, 1);

-- Ana leu a versão 1 e grava:
UPDATE conta SET saldo = 150, version = version + 1 WHERE id = 1 AND version = 1;
-- Bruno também leu a versão 1 e grava depois:
UPDATE conta SET saldo = 200, version = version + 1 WHERE id = 1 AND version = 1;

SELECT * FROM conta;
-- esperado: saldo = 150, version = 2  (a escrita de Bruno não teve efeito)
```

> **Limitação real desses playgrounds:** eles executam tudo numa sessão só. Você vê a **guarda**
> funcionando, mas não vê **duas sessões concorrentes de verdade**. Para isso, precisa do
> item 6 (dois `psql`) ou do projeto-modelo (item 1).

### 0.2 Ambiente completo, na nuvem

| Serviço | O que dá | Custo | Link |
|---|---|---|---|
| **GitHub Codespaces** | VS Code no navegador com Node e Docker prontos | 120 h·núcleo/mês grátis em conta pessoal | <https://github.com/features/codespaces> |
| **Gitpod** | idem | camada gratuita mensal | <https://www.gitpod.io/> |
| **Google Cloud Shell** | terminal Linux com Node, Docker e 5 GB persistentes | gratuito com conta Google | <https://shell.cloud.google.com/> |

Nos três, o projeto-modelo roda com os mesmos comandos do [`README`](07-projeto-modelo/README.md).
Confira preços e limites em [`80-custos-e-licencas.md`](80-custos-e-licencas.md) — mudam.

---

## 1. Node.js — obrigatório

**Versão mínima: 22.5** (quando o módulo `node:sqlite` apareceu).
**Recomendada: 24.x LTS.** **Evite:** 20 e anteriores (não têm `node:sqlite`), e ímpares
(21, 23, 25) — são séries "Current", sem suporte de longo prazo.

Escolha **um** método. Recomendação, por perfil:

| Perfil | Método recomendado | Por quê |
|---|---|---|
| Vai mexer em vários projetos JS | **gerenciador de versões** (`nvm`, `fnm` ou `mise`) | troca de versão por projeto, sem `sudo`, sem conflito |
| Só quer rodar este curso | **instalador oficial** ou pacote da distro | um comando, acabou |
| Máquina corporativa travada | **Docker** ou **binário portátil** | não exige administrador |
| Não quer nada na máquina | **item 0** | zero instalação |

### 1.1 Linux — família Debian/Ubuntu

**Não use `apt install nodejs` do repositório padrão do Ubuntu 22.04.** Ele entrega Node 12,
que não serve. Comprove antes de se frustrar:

```bash
apt-cache policy nodejs | head -3
# no Ubuntu 22.04 sem repositório extra: "Candidato: 12.22.9~dfsg-1ubuntu3.6" — velho demais
```

**Método A — nvm (recomendado).** Instala no seu diretório, sem `sudo`:

```bash
curl -fsSL https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.6/install.sh | bash
# baixa o nvm para ~/.nvm e adiciona as linhas de carga ao seu arquivo de perfil
```

```bash
exec "$SHELL" -l    # recarrega o shell para o nvm passar a existir
command -v nvm
# esperado: nvm
```

> Se a saída for vazia: o instalador escreveu num perfil que o seu shell não lê.
> Veja a seção 3 (PATH).

```bash
nvm install 24
# baixa e ativa o Node 24 LTS mais recente
```

```bash
node --version && npm --version
# esperado: v24.19.0 (ou superior) e 11.x
```

**Método B — repositório NodeSource** (instala no sistema, exige `sudo`):

```bash
curl -fsSL https://deb.nodesource.com/setup_24.x | sudo -E bash -
# adiciona o repositório e a chave GPG da NodeSource ao apt
```

```bash
sudo apt-get install -y nodejs
```

```bash
node --version
# esperado: v24.x
```

> **Por que ler o script antes de canalizar para o bash?** Porque `curl | bash` executa código
> remoto como você (ou como root, no caso B). É a prática dominante e é aceita na maioria dos
> ambientes, mas em máquina corporativa baixe primeiro (`curl -o setup.sh …`), leia, e só
> então execute. Isso não é paranoia: é a mesma razão pela qual você não instala `.exe`
> de origem desconhecida.

**Método C — mise** (gerencia Node, Python, Java e mais, com um arquivo por projeto):

```bash
curl -fsSL https://mise.run | sh
```

```bash
echo 'eval "$(~/.local/bin/mise activate bash)"' >> ~/.bashrc && exec "$SHELL" -l
```

```bash
mise use -g node@24 && node --version
# esperado: v24.x
```

### 1.2 Linux — família Fedora/RHEL/Rocky/Alma

```bash
dnf module list nodejs 2>/dev/null | head -20
# mostra os fluxos disponíveis; no Fedora recente o pacote já é recente o bastante
```

**Fedora 40+:**

```bash
sudo dnf install -y nodejs npm
```

```bash
node --version
# esperado: v22.x ou v24.x. Se vier < v22.5, use nvm (1.1 método A) — funciona igual aqui.
```

**RHEL/Rocky/Alma 9:**

```bash
curl -fsSL https://rpm.nodesource.com/setup_24.x | sudo -E bash -
sudo dnf install -y nodejs
```

### 1.3 Linux — Arch

```bash
sudo pacman -S nodejs-lts-jod npm
# 'jod' é o codinome da série 22. Para a 24, use `nodejs` ou nvm.
```

```bash
node --version
```

### 1.4 macOS

**Apple Silicon (M1–M4) e Intel usam os mesmos comandos**; o que muda é o prefixo do
Homebrew, e isso importa para o PATH:

| Chip | Prefixo do Homebrew |
|---|---|
| Apple Silicon | `/opt/homebrew` |
| Intel | `/usr/local` |

```bash
uname -m
# esperado: arm64 (Apple Silicon) ou x86_64 (Intel)
```

**Método A — Homebrew (recomendado):**

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
# pule se já tiver: `brew --version` responde
```

```bash
brew install node@24
```

```bash
brew link --overwrite node@24   # só se `node --version` não achar a 24
node --version
# esperado: v24.x
```

**Método B — nvm:** idêntico ao 1.1-A, mas o perfil normalmente é `~/.zshrc` (zsh é o padrão
desde o macOS Catalina).

**Método C — instalador `.pkg` oficial:** baixe em <https://nodejs.org/en/download> e execute.
Instala em `/usr/local/bin`. Simples, mas prende você a uma versão só.

### 1.5 Windows

**Caminho recomendado: WSL2.** Motivos concretos, não de gosto:

1. Todo o material, exemplos e scripts assumem caminhos e comandos POSIX.
2. Ferramentas de banco (`psql`, Docker) têm ecossistema muito melhor no Linux.
3. O sistema de arquivos do WSL2 (`/home/você`, não `/mnt/c`) é várias vezes mais rápido para
   `node_modules` e SQLite.
4. Você vai depurar problemas do seu código, não do Windows.

**WSL2 — instalação:**

```powershell
wsl --install -d Ubuntu-24.04
# instala o WSL2 e o Ubuntu 24.04; pode pedir reinicialização
```

```powershell
wsl --status
# esperado: "Versão padrão: 2"
```

Depois, **dentro do Ubuntu**, siga a seção 1.1 como se fosse Linux nativo. É Linux nativo.

> **Armadilha de desempenho:** guarde os projetos em `~/projetos`, **não** em `/mnt/c/Users/...`.
> A ponte entre os dois sistemas de arquivos é lenta e já custou horas a muita gente.

**Windows nativo (sem WSL) — método A, `winget`:**

```powershell
winget install OpenJS.NodeJS.LTS
```

```powershell
node --version
# esperado: v24.x. Se der "não reconhecido", ABRA UM TERMINAL NOVO (veja seção 3).
```

**Windows nativo — método B, `fnm`** (gerenciador de versões que funciona bem no PowerShell):

```powershell
winget install Schniz.fnm
```

```powershell
fnm env --use-on-cd | Out-String | Invoke-Expression
fnm install 24
fnm use 24
node --version
```

Para tornar permanente, adicione a linha `fnm env --use-on-cd | Out-String |
Invoke-Expression` ao seu perfil do PowerShell (`notepad $PROFILE`).

**Windows nativo — método C, instalador `.msi`:** <https://nodejs.org/en/download>.
Marque a opção de adicionar ao PATH.

### 1.6 Docker — sem instalar Node no sistema

```bash
docker run --rm -it -v "$PWD":/app -w /app node:24-bookworm-slim node --version
# esperado: v24.x  (baixa ~80 MB na primeira vez)
```

Para rodar o projeto-modelo assim:

```bash
docker run --rm -it -p 3000:3000 -v "$PWD":/app -w /app node:24-bookworm-slim npm test
```

> Em Linux, arquivos criados dentro do contêiner podem ficar com dono `root`.
> Acrescente `--user "$(id -u):$(id -g)"` para evitar.

### 1.7 Versão portátil (sem administrador, sem gerenciador)

```bash
curl -fsSLO https://nodejs.org/dist/v24.19.0/node-v24.19.0-linux-x64.tar.xz
tar -xJf node-v24.19.0-linux-x64.tar.xz -C ~/.local --strip-components=1
export PATH="$HOME/.local/bin:$PATH"
node --version
```

Confira a integridade antes de usar (a NodeSource publica `SHASUMS256.txt` assinado):

```bash
curl -fsSLO https://nodejs.org/dist/v24.19.0/SHASUMS256.txt
sha256sum -c SHASUMS256.txt --ignore-missing
# esperado: node-v24.19.0-linux-x64.tar.xz: SUCESSO
```

### 1.8 Verificação final do Node

```bash
node -e "const {DatabaseSync}=require('node:sqlite'); const d=new DatabaseSync(':memory:'); d.exec('CREATE TABLE t(v INTEGER)'); console.log('node:sqlite OK');"
# esperado: node:sqlite OK
```

Se der `Cannot find module 'node:sqlite'`, sua versão é anterior à 22.5. Volte à 1.1.
Se der aviso `ExperimentalWarning: SQLite is an experimental feature`, está tudo certo —
é só um aviso, e ele some nas versões mais novas da série 24.

---

## 2. git e curl

Estão presentes em quase toda instalação Linux e macOS. Confira:

```bash
git --version && curl --version | head -1
# esperado: git version 2.3x+ e curl 7.8x+ (ou 8.x)
```

Se faltar:

```bash
sudo apt install -y git curl        # Debian/Ubuntu
sudo dnf install -y git curl        # Fedora/RHEL
brew install git curl               # macOS
winget install Git.Git cURL.cURL    # Windows
```

> **Windows:** o `curl` do PowerShell é um **alias para `Invoke-WebRequest`**, com sintaxe
> diferente. Os comandos `curl -i -X PUT -H '...'` deste curso **não funcionam** nele.
> Use `curl.exe` explicitamente, ou o WSL, ou o Git Bash.

---

## 3. PATH e variáveis de ambiente

A causa nº 1 de "instalei e não funciona".

### Como conferir onde o sistema procura

```bash
echo "$PATH" | tr ':' '\n'
# lista, um por linha, os diretórios onde o shell procura executáveis
```

```bash
command -v node
# esperado: um caminho, ex.: /home/voce/.nvm/versions/node/v24.19.0/bin/node
# se vier vazio: o diretório do node não está no PATH
```

```powershell
# Windows PowerShell
$env:Path -split ';'
Get-Command node
```

### Em qual arquivo mexer

| Shell / SO | Arquivo de perfil | Observação |
|---|---|---|
| bash (Linux) | `~/.bashrc` | lido em shell interativo; `~/.profile` em shell de login |
| zsh (macOS, Linux) | `~/.zshrc` | padrão do macOS desde o Catalina |
| fish | `~/.config/fish/config.fish` | sintaxe diferente: `set -gx PATH ...` |
| PowerShell | `$PROFILE` | `notepad $PROFILE`; crie o arquivo se não existir |

Exemplo de correção (bash/zsh):

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
```

```bash
exec "$SHELL" -l && command -v node
# esperado: o caminho do node
```

### Por que "não pegou" antes de reabrir o terminal

Variáveis de ambiente são **copiadas** para o processo no instante em que ele nasce. Alterar
o `~/.bashrc` muda o que os processos **futuros** vão receber; o terminal já aberto continua
com a cópia velha. Não há mágica: ou você reabre, ou recarrega com `source ~/.bashrc`
(ou `exec "$SHELL" -l`).

No Windows, `winget`/instaladores alteram o PATH no registro e disparam uma notificação de
ambiente; terminais já abertos raramente a respeitam. **Abra um terminal novo.**

---

## 4. Permissões — e por que `sudo npm -g` estraga a máquina

Este curso **não precisa de nenhum pacote npm global**. Mas você vai encontrar tutoriais
mandando fazer `sudo npm install -g <algo>`, e vale saber o estrago:

1. Os arquivos passam a pertencer ao `root` dentro do seu diretório de cache (`~/.npm`).
   Depois disso, um `npm install` **normal** falha com `EACCES` — e a "solução" que a internet
   dá é usar `sudo` de novo, agravando o problema.
2. Scripts de `postinstall` de pacotes de terceiros passam a rodar **como root**. Um pacote
   comprometido deixa de ser um problema do seu usuário e passa a ser da máquina inteira.
3. A instalação escapa do gerenciador de versões: você troca de Node e as ferramentas somem
   (ou pior, ficam apontando para o binário antigo).

**O jeito certo**, se um dia precisar de global:

```bash
npm config set prefix "$HOME/.npm-global"
echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.bashrc
exec "$SHELL" -l
npm install -g <pacote>     # agora sem sudo, tudo dentro do seu HOME
```

Se você já usou `sudo npm`, conserte as posses:

```bash
sudo chown -R "$(id -u):$(id -g)" ~/.npm ~/.config 2>/dev/null
```

Com `nvm`/`fnm`/`mise` o problema não existe: tudo já vive no seu diretório.

---

## 5. Conviver com várias versões na mesma máquina

Você vai precisar disto no dia em que um projeto antigo exigir Node 20.

```bash
nvm install 20 && nvm install 24
nvm ls
# lista as versões instaladas e marca a ativa com ->
```

```bash
nvm use 20 && node --version   # v20.x
nvm use 24 && node --version   # v24.x
```

**Fixe a versão por projeto** — assim ninguém (nem você daqui a seis meses) roda no runtime
errado:

```bash
echo "24" > .nvmrc      # nvm e fnm leem este arquivo
```

```bash
nvm use
# esperado: "Now using node v24.x (npm v11.x)"
```

Com `mise`, o equivalente é `.tool-versions` ou `mise.toml`:

```bash
mise use node@24        # grava mise.toml no diretório do projeto
```

---

## 6. PostgreSQL 18 — opcional, para os laboratórios de isolamento

Necessário só para os labs 8–12 de [`70-pratica.md`](70-pratica.md), onde você precisa de
**duas sessões concorrentes de verdade** e de erros `40001`.

### 6.1 Via Docker (recomendado — nada fica no sistema)

```bash
docker run -d --name pg-ocl \
  -e POSTGRES_PASSWORD=segredo \
  -e POSTGRES_DB=lab \
  -p 5432:5432 \
  postgres:18
# sobe o PostgreSQL 18 escutando em localhost:5432
```

```bash
docker exec -it pg-ocl psql -U postgres -d lab -c 'SELECT version();'
# esperado: PostgreSQL 18.x on x86_64-pc-linux-gnu ...
```

Duas sessões concorrentes (abra dois terminais):

```bash
docker exec -it pg-ocl psql -U postgres -d lab
```

Para remover tudo depois:

```bash
docker rm -f pg-ocl
```

> **Permissão negada no Docker (Linux):** se aparecer
> `permission denied while trying to connect to the Docker daemon socket`, seu usuário não
> está no grupo `docker`:
> ```bash
> sudo usermod -aG docker "$USER" && newgrp docker
> ```
> Isso concede, na prática, privilégios equivalentes a root na máquina. Em ambiente
> compartilhado, prefira `sudo docker` ou o modo *rootless*.

### 6.2 Nativo — Debian/Ubuntu

```bash
sudo apt install -y postgresql-common
sudo /usr/share/postgresql-common/pgdg/apt.postgresql.org.sh
# adiciona o repositório oficial PGDG, que tem a 18; o do Ubuntu costuma estar atrasado
```

```bash
sudo apt install -y postgresql-18
```

```bash
psql --version
# esperado: psql (PostgreSQL) 18.x
```

```bash
sudo -u postgres psql -c 'SELECT version();'
```

### 6.3 Nativo — Fedora/RHEL

```bash
sudo dnf install -y postgresql-server postgresql
sudo postgresql-setup --initdb
sudo systemctl enable --now postgresql
psql --version
```

### 6.4 Nativo — macOS

```bash
brew install postgresql@18
brew services start postgresql@18
psql --version
```

### 6.5 Windows

Use **WSL2** (siga 6.2) ou o instalador da EDB: <https://www.postgresql.org/download/windows/>.
Só o cliente:

```powershell
winget install PostgreSQL.psql
```

> Detalhes de instalação, tuning e operação do PostgreSQL estão em
> [`../postgresql/03-instalacao.md`](../postgresql/03-instalacao.md). Aqui só o mínimo.

---

## 7. Runtimes opcionais para os exemplos do [`06`](06-exemplos.md)

Instale **apenas** o da linguagem que você usa. Nenhum é necessário para o projeto-modelo.

### Java 21 + Maven (exemplo JPA/Hibernate)

```bash
sudo apt install -y openjdk-21-jdk maven        # Debian/Ubuntu
brew install openjdk@21 maven                   # macOS
winget install EclipseAdoptium.Temurin.21.JDK Apache.Maven   # Windows
```

```bash
java -version && mvn -version
# esperado: openjdk version "21.x" e Apache Maven 3.9.x
```

> Se o `java -version` mostrar 17 (comum em Ubuntu 22.04, que tem o 17 por padrão), o exemplo
> ainda compila — Hibernate 6.x roda em Java 17. Para Hibernate 7, o mínimo é Java 17 também,
> mas prefira 21 por ser a LTS atual.
> Alternar entre JDKs: `sudo update-alternatives --config java`.

### Python 3.12 + Django (exemplo Django)

```bash
python3 --version
# esperado: 3.10+ ; o exemplo pede 3.10+, e o Django 5.x exige 3.10+
```

```bash
python3 -m venv .venv && source .venv/bin/activate && pip install "django>=5.0"
# ambiente virtual: NUNCA instale pacotes Python com sudo pip no sistema —
# você quebra ferramentas do próprio SO que dependem do Python do sistema
```

```bash
python -c "import django; print(django.get_version())"
# esperado: 5.x
```

### .NET 10 (exemplo EF Core)

```bash
# Debian/Ubuntu (Microsoft publica pacotes próprios):
sudo apt install -y dotnet-sdk-10.0
# macOS:  brew install --cask dotnet-sdk
# Windows: winget install Microsoft.DotNet.SDK.10
```

```bash
dotnet --version
# esperado: 10.x
```

---

## 8. Rede corporativa: proxy, certificado, registry espelhado

Se você está atrás de um proxy da empresa, quase todos os comandos acima falham em silêncio
ou com erro de TLS. Configure antes:

```bash
export HTTP_PROXY=http://proxy.empresa.com:8080
export HTTPS_PROXY=http://proxy.empresa.com:8080
export NO_PROXY=localhost,127.0.0.1,.empresa.com
# adicione ao ~/.bashrc para não repetir a cada terminal
```

```bash
npm config set proxy "$HTTP_PROXY"
npm config set https-proxy "$HTTPS_PROXY"
```

**Certificado interno (TLS interceptado):**

```bash
# Linux: instale o certificado da empresa na âncora de confiança do sistema
sudo cp empresa-ca.crt /usr/local/share/ca-certificates/ && sudo update-ca-certificates
```

```bash
export NODE_EXTRA_CA_CERTS=/usr/local/share/ca-certificates/empresa-ca.crt
# faz o Node confiar no certificado sem desativar a verificação
```

> **Nunca** use `NODE_TLS_REJECT_UNAUTHORIZED=0` nem `npm config set strict-ssl false` como
> solução definitiva. Isso desliga a verificação de TLS **para tudo**, inclusive para o
> download dos pacotes que você vai executar. É trocar um erro visível por uma vulnerabilidade
> invisível.

**Registry espelhado (Nexus, Artifactory):**

```bash
npm config set registry https://nexus.empresa.com/repository/npm-group/
npm config get registry
```

**Docker atrás de proxy:** configure em `~/.docker/config.json` (cliente) e no serviço
(`/etc/systemd/system/docker.service.d/http-proxy.conf`), depois
`sudo systemctl daemon-reload && sudo systemctl restart docker`.

---

## 9. Reprodutibilidade

Para que a mesma coisa rode na sua máquina, na do colega e na CI:

| Arquivo | Fixa | Lido por |
|---|---|---|
| `.nvmrc` (`24`) | versão do Node | `nvm`, `fnm`, ação `setup-node` do GitHub |
| `.tool-versions` / `mise.toml` | Node, Python, Java, tudo | `mise`, `asdf` |
| `package.json` → `"engines"` | versão mínima aceita | `npm` (avisa; com `engine-strict=true`, falha) |
| `package-lock.json` | versões exatas das dependências | `npm ci` |
| `Dockerfile` / `compose.yaml` | o ambiente inteiro | Docker |

O projeto-modelo deste curso declara:

```json
{ "engines": { "node": ">=24.0.0" } }
```

e **não tem `package-lock.json` porque não tem dependência nenhuma** — o que, aliás, é a
forma mais forte de reprodutibilidade que existe.

---

## 10. Atualizar com segurança — e voltar atrás

```bash
nvm install 24 --reinstall-packages-from=current
# instala a 24 mais recente trazendo os pacotes globais da versão atual
```

```bash
nvm ls                       # veja o que existe
nvm alias default 24         # define o padrão de novos terminais
```

**Voltar atrás** (a razão de existir do gerenciador de versões):

```bash
nvm use 22 && node --version
```

Com pacotes do sistema:

```bash
sudo apt list --installed | grep nodejs        # descubra a versão instalada
sudo apt install nodejs=<versão-anterior>      # rebaixa (pode exigir o repositório certo)
```

Docker é o caso mais simples: troque a tag (`node:24` → `node:22`) e recrie o contêiner.

---

## 11. Desinstalar por completo

O que normalmente **fica para trás** e ninguém remove: caches, configurações e diretórios
globais. A lista completa:

**nvm:**

```bash
rm -rf "$NVM_DIR" ~/.nvm
# e apague as linhas do nvm do seu ~/.bashrc / ~/.zshrc
```

**Node via apt (Debian/Ubuntu):**

```bash
sudo apt purge -y nodejs
sudo rm -f /etc/apt/sources.list.d/nodesource.list
sudo rm -f /etc/apt/keyrings/nodesource.gpg
sudo apt autoremove -y
```

**Node via Homebrew:**

```bash
brew uninstall node@24 && brew cleanup
```

**Node no Windows:**

```powershell
winget uninstall OpenJS.NodeJS.LTS
Remove-Item -Recurse -Force "$env:APPDATA\npm", "$env:APPDATA\npm-cache"
```

**Resíduos comuns em todos os sistemas:**

```bash
rm -rf ~/.npm ~/.npmrc ~/.node-gyp ~/.cache/node
# ~/.npm  = cache de pacotes (chega facilmente a 1–2 GB)
# ~/.npmrc = configuração (proxy, registry, prefix)
```

**PostgreSQL via Docker:**

```bash
docker rm -f pg-ocl
docker volume prune     # cuidado: remove volumes órfãos de OUTROS contêineres também
```

**PostgreSQL nativo (Debian/Ubuntu) — apaga os dados:**

```bash
sudo apt purge -y 'postgresql-*'
sudo rm -rf /var/lib/postgresql /etc/postgresql
```

---

## 12. Requisitos reais

| Recurso | Node 24 | + Docker | + PostgreSQL nativo |
|---|---|---|---|
| Disco | ~120 MB | +600 MB (Docker) +80 MB (imagem node) +450 MB (imagem postgres) | ~250 MB + dados |
| Memória em uso | ~60 MB (o projeto-modelo) | +400 MB (daemon) | ~150 MB de base |
| Arquitetura | x86_64, arm64 | x86_64, arm64 | x86_64, arm64 |
| Privilégio de administrador | **não** (com nvm) | **sim** (grupo docker ou root) | **sim** |
| Conta em algum serviço | **não** | não (Docker Hub anônimo tem limite de *pull*) | não |
| Cartão de crédito | **não** | não | não |
| Licença | MIT (Node) | Apache 2.0 (Engine) | PostgreSQL License |

Detalhes de licença e do que muda em uso comercial: [`80-custos-e-licencas.md`](80-custos-e-licencas.md).

---

## 13. Solução de problemas — mensagens literais

| Mensagem | Causa provável | Correção |
|---|---|---|
| `bash: node: command not found` <br> `'node' não é reconhecido como um comando interno` | binário fora do PATH, ou terminal aberto antes da instalação | **abra um terminal novo**; depois `command -v node`; se vazio, seção 3 |
| `nvm: command not found` (logo após instalar) | `nvm` é uma **função de shell**, não um binário; o perfil não foi recarregado | `exec "$SHELL" -l` ou `source ~/.nvm/nvm.sh` |
| `Error: Cannot find module 'node:sqlite'` | Node anterior à 22.5 | `nvm install 24 && nvm use 24`; confira com `node --version` |
| `ExperimentalWarning: SQLite is an experimental feature` | aviso normal da série 22/24 | ignore; para silenciar: `node --no-warnings ...` |
| `EACCES: permission denied, access '/usr/lib/node_modules'` | `npm -g` sem permissão, ou resíduo de `sudo npm` | seção 4: `npm config set prefix "$HOME/.npm-global"`; **não** repita com `sudo` |
| `npm ERR! code SELF_SIGNED_CERT_IN_CHAIN` <br> `unable to get local issuer certificate` | TLS interceptado por proxy corporativo | seção 8: instale a CA e use `NODE_EXTRA_CA_CERTS`; não desligue o `strict-ssl` |
| `npm ERR! network ETIMEDOUT` / `ECONNREFUSED` | proxy não configurado, ou firewall bloqueando o registry | seção 8 |
| `Error: listen EADDRINUSE: address already in use :::3000` | já existe algo na porta 3000 | `PORTA=3001 npm start`, ou descubra o culpado: `ss -ltnp \| grep 3000` |
| `permission denied while trying to connect to the Docker daemon socket` | usuário fora do grupo `docker` | `sudo usermod -aG docker "$USER" && newgrp docker` (leia o aviso da seção 6.1) |
| `psql: error: connection to server ... Connection refused` | serviço parado, ou porta errada | Docker: `docker ps`; nativo: `sudo systemctl status postgresql` |
| `psql: FATAL: role "seu-usuario" does not exist` | o Postgres nativo cria só o papel `postgres` | `sudo -u postgres createuser -s "$USER"` |
| `SQLITE_BUSY: database is locked` | duas conexões escrevendo no mesmo arquivo SQLite | use `:memory:`, ou `PRAGMA journal_mode=WAL`, ou `timeout` no `DatabaseSync` |
| `The system cannot find the path specified` (Windows, WSL) | projeto em `/mnt/c/...` com permissões estranhas | mova para `~/projetos` dentro do WSL |
| `curl: (60) SSL certificate problem` | mesma causa do `SELF_SIGNED_CERT_IN_CHAIN` | seção 8 |

---

## 14. Checklist de "ambiente pronto"

Rode uma linha por vez. Todas precisam responder.

```bash
node --version
```
```bash
npm --version
```
```bash
node -e "require('node:sqlite'); console.log('sqlite ok')"
```
```bash
node -e "console.log(typeof fetch === 'function' ? 'fetch ok' : 'fetch AUSENTE')"
```
```bash
git --version
```
```bash
curl --version | head -1
```
```bash
cd 07-projeto-modelo && npm test
```

Saída esperada da última linha: `ℹ pass 21` e `ℹ fail 0`.

Opcionais, só se você for fazer os labs 8–12:

```bash
docker --version
```
```bash
docker run --rm postgres:18 psql --version
```

Com tudo isso respondendo, siga para [`04-como-comecar.md`](04-como-comecar.md).

---

## Autoteste

1. Por que `apt install nodejs` no Ubuntu 22.04 não serve para este curso?
2. Você instalou o Node e `node --version` diz "command not found". Quais são as duas
   primeiras coisas a verificar, nessa ordem?
3. Explique, sem usar a palavra "segurança", por que `sudo npm install -g` cria problemas
   depois.
4. Qual arquivo você cria para garantir que o colega rode o projeto na mesma versão do Node?
5. O que `NODE_EXTRA_CA_CERTS` resolve, e por que ele é preferível a
   `NODE_TLS_REJECT_UNAUTHORIZED=0`?
6. Cite dois resíduos que ficam na máquina depois de "desinstalar" o Node.
7. Você quer ver duas sessões concorrentes de verdade. Por que o DB Fiddle não basta?

---

## Fontes consultadas

Consultadas em **14/08/2026**:

- [Node.js — Release v24.19.0 (LTS), 03/08/2026](https://nodejs.org/en/blog/release/v24.19.0)
- [Node.js — v24.19.0 no GitHub](https://github.com/nodejs/node/releases/tag/v24.19.0)
- [Node.js — Node.js 24.0.0 (Current), notas de lançamento](https://nodejs.org/en/blog/release/v24.0.0)
- [Node.js — Download](https://nodejs.org/en/download)
- [nvm-sh/nvm — Release v0.40.6](https://github.com/nvm-sh/nvm/releases/tag/v0.40.6)
- [nvm-sh/nvm — Release v0.40.5 (corrige CVE-2026-10796)](https://github.com/nvm-sh/nvm/releases/tag/v0.40.5)
- [PostgreSQL — 18.6, 17.11, 16.15, 15.19, 14.24 e 19 Beta 3 lançados, 13/08/2026](https://www.postgresql.org/about/news/postgresql-186-1711-1615-1519-1424-and-19-beta-3-released-3365/)
- [PostgreSQL — Download para Windows](https://www.postgresql.org/download/windows/)
- Verificações locais: `node v24.18.0`, `docker 29.1.3`, `git 2.34.1`, `curl 7.81.0`,
  `openjdk 17.0.19`, `Python 3.10.12` em Ubuntu 22.04.5 LTS x86_64.
