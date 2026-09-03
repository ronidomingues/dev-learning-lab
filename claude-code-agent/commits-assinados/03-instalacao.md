# 3 · Manual de instalação

> Nível: iniciante · **Versões conferidas na web em 13/08/2026** · Testado em Ubuntu 22.04.5
> LTS com Git 2.34.1, GnuPG 2.2.27 e OpenSSH 8.9p1

Este é o documento mais chato do curso e o que mais salva iniciante. Ele instala **todo o
conjunto**, não só a ferramenta principal: Git, GnuPG, o agente e o `pinentry`, o cliente
OpenSSH, e o `gh` (opcional, mas encurta muito o cadastro da chave).

Cada passo tem: o comando, o que ele faz, a verificação imediata com a saída esperada, e o
que fazer se a saída for diferente.

---

## 0. Antes de instalar qualquer coisa: você talvez não precise

Sempre que existir, o caminho sem instalação vem primeiro — é o que evita desistência no
primeiro dia. Três opções reais:

### a) Commits feitos pela interface web do GitHub já vêm assinados

Edite um arquivo pelo botão de lápis no site, ou aceite uma sugestão de revisão, ou use o
botão **Merge pull request**: o GitHub assina esses commits com a chave dele (a que aparece
como `GitHub <noreply@github.com>`, chave `web-flow`) e eles saem `Verified`.

Isso é 100 % do caminho para quem só edita documentação, e 0 % para quem programa. Detalhes
e o que isso realmente prova estão em
[15-verificacao-no-github.md](15-verificacao-no-github.md).

### b) GitHub Codespaces — ambiente pronto, no navegador

Codespaces vem com Git recente e, se você habilitar, **assina automaticamente** os commits
feitos lá dentro, usando uma chave gerenciada pelo GitHub.

1. Abra qualquer repositório seu → botão **Code** → aba **Codespaces** → **Create codespace**.
2. Em <https://github.com/settings/codespaces>, marque **GPG verification**.

Camada gratuita em 13/08/2026: 120 horas-núcleo e 15 GB-mês de armazenamento por mês para
contas pessoais Free (confira em [80-custos-e-licencas.md](80-custos-e-licencas.md), porque
esse número muda).

### c) Container descartável, se você tem Docker

```bash
docker run --rm -it -v "$PWD":/repo -w /repo alpine/git:latest sh
```

Serve para experimentar. Não serve para o dia a dia: a chave privada teria de entrar no
container, e aí você criou um problema maior do que resolveu.

**Se qualquer uma das três resolve o seu caso, pare aqui e vá para o
[04-como-comecar.md](04-como-comecar.md).** Se você programa de verdade, siga.

---

## 1. O conjunto completo — o que cada peça faz

| Peça | Para quê | Obrigatória? |
|---|---|---|
| **Git** ≥ 2.34 | faz o commit e chama o assinador | **sim** |
| **OpenSSH** (`ssh-keygen`) ≥ 8.1 | gera e verifica assinaturas no formato SSHSIG | só no método SSH |
| **GnuPG** (`gpg`) ≥ 2.2 | gera e verifica assinaturas OpenPGP | só no método GPG |
| **`gpg-agent`** | guarda a chave destravada, para não pedir senha a cada commit | vem junto do GnuPG |
| **`pinentry`** | a janelinha (ou o prompt) que pede a frase secreta | vem junto, **menos no macOS** |
| **`ssh-agent`** | idem, para chaves SSH com frase secreta | vem junto do OpenSSH |
| **`gh` (GitHub CLI)** ≥ 2.0 | cadastra a chave na sua conta por linha de comando | opcional |
| **Editor de texto** | editar `~/.gitconfig` e `allowed_signers` | qualquer um |

Versões atuais em 13/08/2026, para você saber o que é "novo":

| | Versão atual | Data | Fonte |
|---|---|---|---|
| Git | **2.55.0** | 11/08/2026 | anúncio do mantenedor |
| GnuPG | **2.5.21** | 02/07/2026 | gnupg.org — **a série 2.4 saiu de suporte em 30/06/2026** |
| OpenSSH | **10.5** | 11/08/2026 | openssh.com |
| Gpg4win (Windows) | **5.1.0** | 29/07/2026 | gpg4win.org — traz GnuPG 2.5.16; **só 64 bits** |
| GitHub CLI | **2.97.0** | 31/07/2026 | github.com/cli/cli |

---

## 2. Linux

### 2.1 Debian, Ubuntu, Linux Mint, Pop!\_OS

**Passo 1 — instalar o básico.**

```bash
sudo apt update && sudo apt install -y git gnupg openssh-client
```

> Instala o Git, o GnuPG (com `gpg-agent` e `pinentry-curses` junto) e o cliente SSH.

**Verifique:**

```bash
git --version && gpg --version | head -1 && ssh -V
```

```
# esperado (exemplo real, Ubuntu 22.04.5):
git version 2.34.1
gpg (GnuPG) 2.2.27
OpenSSH_8.9p1 Ubuntu-3ubuntu0.16, OpenSSL 3.0.2 15 Mar 2022
```

**Se o Git for anterior a 2.34** (Ubuntu 20.04 entrega 2.25, Debian 11 entrega 2.30), a
assinatura por SSH não existe nessa versão. Corrija com o PPA oficial dos mantenedores do
Git no Ubuntu:

```bash
sudo add-apt-repository -y ppa:git-core/ppa
sudo apt update && sudo apt install -y git
```

> Adiciona o repositório que publica a versão estável mais recente do Git para Ubuntu, e
> atualiza. Funciona no Ubuntu e derivados; **não** no Debian puro.

```bash
git --version
# esperado: git version 2.55.0 (ou a estável do dia)
```

No **Debian**, o caminho é o `backports` da sua versão, ou compilar (§ 5.4):

```bash
# Debian 12 (bookworm)
echo "deb http://deb.debian.org/debian bookworm-backports main" \
  | sudo tee /etc/apt/sources.list.d/backports.list
sudo apt update && sudo apt install -y -t bookworm-backports git
```

**Passo 2 — `pinentry` gráfico (opcional, e só se você usa ambiente gráfico).**

```bash
sudo apt install -y pinentry-gnome3   # GNOME
# ou
sudo apt install -y pinentry-qt       # KDE
```

> Faz a frase secreta ser pedida numa janela em vez de dentro do terminal. Sem isso,
> funciona igual — só é menos bonito, e ocasionalmente atrapalha em editores gráficos.

**Passo 3 — `gh` (opcional).**

```bash
(type -p wget >/dev/null || (sudo apt update && sudo apt install wget -y)) \
  && sudo mkdir -p -m 755 /etc/apt/keyrings \
  && out=$(mktemp) && wget -nv -O$out https://cli.github.com/packages/githubcli-archive-keyring.gpg \
  && cat $out | sudo tee /etc/apt/keyrings/githubcli-archive-keyring.gpg > /dev/null \
  && sudo chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg \
  && sudo mkdir -p -m 755 /etc/apt/sources.list.d \
  && echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" \
     | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
  && sudo apt update && sudo apt install gh -y
```

> Comando oficial do projeto, verbatim. Ele baixa a chave do repositório, registra a fonte e
> instala. Note a ironia útil: você está **verificando uma assinatura** para instalar a
> ferramenta com que vai aprender a assinar.

```bash
gh --version
# esperado: gh version 2.97.0 (ou superior)
```

### 2.2 Fedora, RHEL, Rocky, Alma, CentOS Stream

```bash
sudo dnf install -y git-core gnupg2 openssh-clients pinentry
```

> `git-core` é o Git sem as extras (Perl, `gitk`); `gnupg2` é o GnuPG moderno.

```bash
git --version && gpg --version | head -1 && ssh -V
# esperado: git version 2.43.x ou superior (Fedora costuma trazer o mais novo)
```

`gh`, se quiser:

```bash
sudo dnf install -y dnf5-plugins
sudo dnf config-manager addrepo --from-repofile=https://cli.github.com/packages/rpm/gh-cli.repo
sudo dnf install -y gh
```

> Em RHEL 9 / Rocky 9, que ainda usam `dnf4`, troque as duas primeiras linhas por
> `sudo dnf config-manager --add-repo https://cli.github.com/packages/rpm/gh-cli.repo`.

### 2.3 Arch, Manjaro

```bash
sudo pacman -S --needed git gnupg openssh github-cli
```

### 2.4 openSUSE

```bash
sudo zypper install git gpg2 openssh github-cli
```

---

## 3. macOS

### 3.1 Qual caminho escolher

| Caminho | Quando usar | Ressalva |
|---|---|---|
| **Homebrew** | **recomendado** para quem já programa | precisa instalar o Homebrew antes |
| Xcode Command Line Tools | você só quer o Git e nada mais | traz Git **velho**, e não traz GnuPG |
| GPG Suite (`gpgtools.org`) | você quer interface gráfica e integração com Mail.app | pacote grande; parte é paga |
| MacPorts | você já usa MacPorts | menos gente usa, menos respostas na internet |

### 3.2 Homebrew

**Passo 1 — instalar o Homebrew, se ainda não tiver:**

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

**Passo 2 — pôr o Homebrew no `PATH`. Aqui Intel e Apple Silicon divergem**, e é a causa
número um de "instalei e o comando não existe":

```bash
# Apple Silicon (M1, M2, M3, M4...): o Homebrew instala em /opt/homebrew
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"

# Intel: instala em /usr/local
echo 'eval "$(/usr/local/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/usr/local/bin/brew shellenv)"
```

Descubra em qual você está:

```bash
uname -m
# arm64  = Apple Silicon → /opt/homebrew
# x86_64 = Intel         → /usr/local
```

**Passo 3 — instalar as ferramentas:**

```bash
brew install git gnupg pinentry-mac gh
```

> `gnupg` traz `gpg` e `gpg-agent`. **`pinentry-mac` é obrigatório na prática**: o `pinentry`
> padrão do GnuPG não consegue pedir senha na interface do macOS, e a assinatura falha com
> uma mensagem que não ajuda em nada.

**Passo 4 — dizer ao `gpg-agent` para usar o `pinentry-mac`:**

```bash
mkdir -p ~/.gnupg && chmod 700 ~/.gnupg
echo "pinentry-program $(brew --prefix)/bin/pinentry-mac" >> ~/.gnupg/gpg-agent.conf
gpgconf --kill gpg-agent
```

> A última linha derruba o agente para que ele releia a configuração. Sem isso, a mudança
> "não pega" até você reiniciar a máquina.

**Passo 5 — `GPG_TTY`.** O GnuPG precisa saber em qual terminal pedir a senha:

```bash
if [ -r ~/.zshrc ]; then echo -e '\nexport GPG_TTY=$(tty)' >> ~/.zshrc; \
else echo -e '\nexport GPG_TTY=$(tty)' >> ~/.zprofile; fi
```

Abra um terminal novo e verifique:

```bash
echo $GPG_TTY
# esperado: algo como /dev/ttys000  (se sair vazio, a linha não foi lida)
git --version && gpg --version | head -1 && ssh -V
```

> **Atenção ao Git do sistema.** Se `git --version` continuar mostrando uma versão antiga,
> o `PATH` está achando o Git da Apple primeiro. Confira com `which -a git`: o do Homebrew
> (`/opt/homebrew/bin/git` ou `/usr/local/bin/git`) precisa vir antes de `/usr/bin/git`.

---

## 4. Windows

### 4.1 Qual caminho escolher — leia isto antes

| Caminho | Recomendo? | Por quê |
|---|---|---|
| **WSL2 (Ubuntu dentro do Windows)** | **Sim, este** | você usa o mundo Linux inteiro, com toda a documentação da internet valendo; e é o que a maioria das equipes usa |
| Windows nativo (Git for Windows + Gpg4win) | só se você precisa mesmo | funciona, mas você passa a ter **dois** conjuntos de chaves e dois agentes que não se falam |
| Os dois ao mesmo tempo | evite | é a receita para "funciona no terminal e não funciona no VS Code" |

A dor real do caminho nativo: o Git for Windows traz um `gpg` próprio dentro dele, o Gpg4win
instala **outro** `gpg` no sistema, e eles usam pastas de chaves diferentes. Você gera a
chave num e o Git procura no outro. Isso é resolvível (§ 4.3), mas é meia hora da sua vida
que o WSL2 devolve.

### 4.2 WSL2 — o caminho recomendado

**Passo 1 — instalar o WSL2 (PowerShell como administrador):**

```powershell
wsl --install -d Ubuntu
```

> Instala o subsistema Linux e a distribuição Ubuntu. Pode pedir reinício.

**Passo 2 — abrir o Ubuntu e seguir a seção 2.1 deste documento**, inteirinha. A partir daí,
o Windows deixa de importar.

**Verifique, dentro do WSL:**

```bash
git --version && gpg --version | head -1 && ssh -V
```

> **Onde guardar seus repositórios.** Deixe-os em `~/projetos` (dentro do sistema de arquivos
> do Linux), **não** em `/mnt/c/Users/...`. Trabalhar em `/mnt/c` é lento e as permissões de
> arquivo não funcionam como o SSH exige — o `ssh-keygen` reclama de "permissões abertas
> demais" numa chave que você não consegue corrigir com `chmod`.

### 4.3 Windows nativo

**Passo 1 — Git for Windows:**

```powershell
winget install --id Git.Git -e
```

**Passo 2 — Gpg4win (só se for usar GPG):**

```powershell
winget install --id GnuPG.Gpg4win -e
```

> Gpg4win 5.1.0 (29/07/2026) é **somente 64 bits** — o suporte a Windows 32 bits acabou.

**Passo 3 — GitHub CLI (opcional):**

```powershell
winget install --id GitHub.cli -e
```

**Passo 4 — feche e reabra o terminal** (o `PATH` só é relido em processo novo) e verifique:

```powershell
git --version
gpg --version | Select-Object -First 1
ssh -V
```

```
# esperado:
git version 2.55.0.windows.1
gpg (GnuPG) 2.5.16
OpenSSH_for_Windows_9.5p1, LibreSSL 3.8.2
```

**Passo 5 — resolver a briga dos dois `gpg`.** Descubra quantos você tem:

```powershell
where.exe gpg
```

Se aparecer mais de um, diga ao Git explicitamente qual usar:

```powershell
git config --global gpg.program "C:/Program Files (x86)/GnuPG/bin/gpg.exe"
```

> Ajuste o caminho ao que o `where.exe` mostrou. Sem isso, você gera a chave no Kleopatra
> (Gpg4win) e o Git, usando o `gpg` embutido dele, jura que a chave não existe.

**Passo 6 — o `ssh-agent` do Windows**, se for usar SSH com frase secreta:

```powershell
Get-Service ssh-agent | Set-Service -StartupType Automatic
Start-Service ssh-agent
```

---

## 5. Métodos alternativos

### 5.1 Gerenciador de versões (`mise`, `asdf`)

Útil quando você precisa de um Git novo sem poder tocar no do sistema:

```bash
mise use -g git@latest
```

> Instala e ativa o Git na sua pasta de usuário. Recomendo **só** se você já usa `mise` para
> outras coisas; para uma ferramenta só, é complexidade sem retorno.

### 5.2 Container

```bash
docker run --rm -it -v "$PWD":/repo -w /repo debian:12 bash
apt update && apt install -y git gnupg
```

> Bom para experimentar e para reproduzir um problema. Ruim para o dia a dia, pelo motivo já
> dito: a chave privada teria de entrar no container.

### 5.3 Versão portátil (Windows)

O Git for Windows publica um `PortableGit-*.7z.exe` que roda de um pendrive, sem instalar. É
a saída para máquina corporativa sem direito de administrador. Baixe em
<https://git-scm.com/download/win>.

### 5.4 Compilar do fonte (Linux/macOS)

Último recurso — quando você precisa de uma versão que ninguém empacotou:

```bash
sudo apt install -y build-essential libssl-dev libcurl4-gnutls-dev libexpat1-dev gettext
curl -LO https://www.kernel.org/pub/software/scm/git/git-2.55.0.tar.gz
tar -xzf git-2.55.0.tar.gz && cd git-2.55.0
make prefix=$HOME/.local all -j"$(nproc)"
make prefix=$HOME/.local install
```

> Instala em `~/.local`, **sem `sudo`** — de propósito. Compilar com `sudo make install`
> sobrescreve o Git do sistema e o gerenciador de pacotes passa a brigar com você para
> sempre. Depois, garanta que `~/.local/bin` vem antes de `/usr/bin` no `PATH` (§ 6).

---

## 6. `PATH` e variáveis de ambiente

### Onde cada shell lê a configuração

| Shell | Arquivo | Quando é lido |
|---|---|---|
| bash (Linux) | `~/.bashrc` | a cada terminal interativo |
| bash (login, macOS) | `~/.bash_profile` | ao abrir sessão |
| zsh (padrão do macOS) | `~/.zshrc` | a cada terminal interativo |
| zsh (login) | `~/.zprofile` | ao abrir sessão |
| fish | `~/.config/fish/config.fish` | a cada terminal |
| PowerShell | `$PROFILE` (veja com `echo $PROFILE`) | a cada terminal |

**Por que "não pegou".** Editar o arquivo de perfil não muda o terminal já aberto: aquele
processo leu o arquivo quando nasceu. Ou você abre um terminal novo, ou recarrega à mão:

```bash
source ~/.bashrc      # ou ~/.zshrc
```

### As variáveis que importam neste assunto

| Variável | Para quê | Como conferir |
|---|---|---|
| `GPG_TTY` | diz ao GnuPG em qual terminal pedir a senha | `echo $GPG_TTY` |
| `GNUPGHOME` | onde fica o chaveiro (padrão `~/.gnupg`) | `echo ${GNUPGHOME:-~/.gnupg}` |
| `SSH_AUTH_SOCK` | caminho do `ssh-agent` ativo | `echo $SSH_AUTH_SOCK` |
| `PATH` | qual `git`/`gpg` será usado | `which -a git gpg` |

`GPG_TTY` é a causa da mensagem `Inappropriate ioctl for device`. A correção definitiva, em
Linux e macOS:

```bash
echo 'export GPG_TTY=$(tty)' >> ~/.bashrc   # ou ~/.zshrc
source ~/.bashrc
```

### Conferindo qual binário está sendo usado

```bash
which -a git
# /home/voce/.local/bin/git     ← este vence
# /usr/bin/git
```

Se o errado vier primeiro, ponha o caminho certo na frente:

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
```

---

## 7. Permissões

### As três permissões que o OpenSSH exige, e recusa trabalhar sem

```bash
chmod 700 ~/.ssh
chmod 600 ~/.ssh/id_ed25519        # chave PRIVADA: só você lê
chmod 644 ~/.ssh/id_ed25519.pub    # chave pública: pode ser lida por todos
chmod 700 ~/.gnupg
```

**Por que o SSH é rígido a esse ponto?** Porque uma chave privada legível por outros usuários
da máquina é uma chave comprometida, e o modo de falha silencioso (funciona, mas está
vazando) é pior que o barulhento. Então ele se recusa a usar a chave e diz por quê:

```
Permissions 0644 for '/home/voce/.ssh/id_ed25519' are too open.
```

### `sudo` — onde ele estraga tudo

**Nunca** rode `gpg`, `ssh-keygen` ou `git config --global` com `sudo`.

O motivo é concreto, não supersticioso: com `sudo`, `$HOME` vira `/root`. Você gera a chave
em `/root/.gnupg`, e o seu usuário normal — que é quem vai commitar — não tem como lê-la.
Aí o Git diz `secret key not available` para uma chave que você "acabou de criar" e que
existe mesmo, só que na casa de outro usuário.

Se você já fez isso, o conserto é apagar e refazer sem `sudo`:

```bash
sudo rm -rf /root/.gnupg     # confira antes que é isso mesmo
gpg --full-generate-key      # agora como você mesmo
```

O mesmo vale para arquivos que ficaram do usuário errado:

```bash
sudo chown -R "$USER":"$USER" ~/.gnupg ~/.ssh
chmod 700 ~/.gnupg ~/.ssh
```

---

## 8. Rede corporativa

### Proxy

```bash
git config --global http.proxy http://proxy.empresa.com:8080
export https_proxy=http://proxy.empresa.com:8080   # para curl/wget/gh
```

Para o GnuPG falar com servidor de chaves através do proxy:

```bash
echo "keyserver-options http-proxy=http://proxy.empresa.com:8080" >> ~/.gnupg/dirmngr.conf
gpgconf --kill dirmngr
```

### Certificado interno (interceptação de TLS)

Se a empresa inspeciona TLS, o Git vai reclamar de certificado desconhecido. O caminho certo
é confiar no certificado da empresa, **não** desligar a verificação:

```bash
git config --global http.sslCAInfo /caminho/para/certificado-da-empresa.crt
```

> **Não** use `git config --global http.sslVerify false`. Isso desliga a verificação para
> *tudo*, inclusive para o clone que traz código para dentro da empresa. É trocar um aviso
> chato por um buraco permanente.

### Servidor de chaves bloqueado

Muita empresa bloqueia as portas de servidores de chaves OpenPGP (11371, e às vezes o
`keys.openpgp.org` inteiro). Duas notas:

- **No método SSH isso não importa**: ele não usa servidor de chaves para nada.
- No método GPG, também não é obrigatório: publicar a chave em servidor é opcional. O que o
  GitHub precisa é que você **cole a chave pública** na conta, e isso é feito pelo navegador.

---

## 9. Convivência de versões

Ter dois Gits na máquina é normal (o do sistema e um mais novo). A regra é: **não substitua
o do sistema, ponha o novo antes no `PATH`**.

```bash
# instale em ~/.local (§ 5.4) e:
export PATH="$HOME/.local/bin:$PATH"
which -a git    # confira a ordem
```

Com GnuPG, dois chaveiros convivem por `GNUPGHOME`:

```bash
GNUPGHOME=~/.gnupg-trabalho gpg --list-keys    # chaveiro do trabalho
gpg --list-keys                                # o seu, pessoal
```

É exatamente o que o [07-projeto-modelo](07-projeto-modelo/) faz para não encostar no seu.

---

## 10. Reprodutibilidade

Não há "lockfile" para assinatura, mas há três coisas que valem versionar no repositório:

| Arquivo | Para quê |
|---|---|
| `.gitattributes` | nada a ver com assinatura, mas evita que fim de linha mude o conteúdo entre máquinas — e conteúdo diferente é assinatura diferente |
| `allowed_signers` **no repositório** | permite que qualquer pessoa clone e verifique o histórico sem montar nada; o Git aceita `gpg.ssh.allowedSignersFile` apontando para um arquivo versionado |
| `.github/workflows/verificar-assinaturas.yml` | garante que a regra é a mesma para todo mundo |

Versionar o `allowed_signers` é uma decisão com trade-off real, e a discussão está em
[18-politica-de-equipe.md](18-politica-de-equipe.md): ganha-se verificação por qualquer um,
perde-se a possibilidade de o próprio arquivo ser alterado por quem tem escrita no repo.

---

## 11. Atualizar, e voltar atrás

```bash
# Debian/Ubuntu
sudo apt update && sudo apt install --only-upgrade git gnupg openssh-client

# Fedora
sudo dnf upgrade git-core gnupg2 openssh-clients

# macOS
brew upgrade git gnupg gh

# Windows
winget upgrade --id Git.Git -e
```

**Voltar atrás**, se a atualização quebrar algo:

```bash
# Debian/Ubuntu — instalar uma versão específica
apt-cache madison git                 # lista as disponíveis
sudo apt install git=1:2.34.1-1ubuntu1.15

# macOS
brew uninstall git && brew install git@2.49   # se a fórmula versionada existir
```

> Antes de atualizar o **GnuPG** entre séries (2.2 → 2.5), faça backup do chaveiro:
> `tar czf ~/gnupg-backup-$(date +%F).tgz -C ~ .gnupg`. Atualização de GnuPG raramente
> quebra, mas quando quebra, quebra com a sua única chave dentro.

---

## 12. Desinstalar por completo

Desinstalar o programa é a parte fácil. O que fica para trás é o que importa.

```bash
# 1. os programas
sudo apt remove --purge git gnupg openssh-client gh      # Debian/Ubuntu
brew uninstall git gnupg pinentry-mac gh                 # macOS
winget uninstall --id Git.Git -e                         # Windows

# 2. o agente ainda rodando (sempre esquecido)
gpgconf --kill all
pkill ssh-agent

# 3. os dados — LEIA ANTES DE RODAR
#    isto apaga suas CHAVES PRIVADAS. Sem backup, é irreversível:
#    você perde a capacidade de assinar como você mesmo, para sempre.
rm -rf ~/.gnupg          # chaveiro OpenPGP inteiro
rm -rf ~/.ssh            # TODAS as chaves SSH, inclusive as de acesso
rm -f  ~/.gitconfig      # configuração global do Git
rm -rf ~/.config/git     # allowed_signers, ignore global, atributos

# 4. no macOS, o que o Homebrew deixa
rm -rf "$(brew --prefix)/etc/gnupg"

# 5. no Windows
#    %APPDATA%\gnupg          → chaveiro
#    %USERPROFILE%\.ssh       → chaves SSH
#    %USERPROFILE%\.gitconfig → configuração
```

**Faça backup antes**, sempre:

```bash
tar czf ~/backup-chaves-$(date +%F).tgz -C ~ .gnupg .ssh .gitconfig
```

E lembre-se de **revogar** no GitHub o que você apagou aqui:
<https://github.com/settings/keys>. Chave apagada da máquina e ainda listada na conta é uma
chave que você não controla mais e que continua autorizada.

---

## 13. Requisitos reais

| Item | Quanto |
|---|---|
| Espaço em disco | Git ~50 MB · GnuPG ~30 MB · Gpg4win ~350 MB · `gh` ~40 MB |
| Memória | irrelevante (`gpg-agent` fica em ~10 MB) |
| Arquitetura | x86-64, ARM64 — todas suportadas; Windows 32 bits **não** (Gpg4win 5.x) |
| Conta obrigatória | GitHub, gratuita |
| Cartão de crédito | **não**, em nenhum ponto |
| Licença | tudo software livre (§ [80-custos-e-licencas.md](80-custos-e-licencas.md)) |
| Rede | só para instalar e para cadastrar a chave; assinar e verificar são **offline** |

---

## 14. Solução de problemas — a mensagem literal, a causa e a correção

| Mensagem de erro | Causa provável | Correção |
|---|---|---|
| `error: gpg failed to sign the data` / `error: o gpg não pôde assinar os dados` | genérica — é preciso ver o erro real do gpg | rode `echo teste \| gpg --clearsign` para ver a mensagem verdadeira, e volte a esta tabela |
| `gpg: signing failed: Inappropriate ioctl for device` | o GnuPG não sabe onde pedir a senha | `export GPG_TTY=$(tty)` e ponha no `~/.bashrc`/`~/.zshrc` |
| `gpg: signing failed: No secret key` / `secret key not available` | `user.signingkey` aponta para uma chave que não está neste chaveiro — quase sempre porque foi gerada com `sudo` ou em outro `GNUPGHOME` | `gpg --list-secret-keys --keyid-format=long` e reconfigure com o ID que aparecer; se ela estiver em `/root`, refaça sem `sudo` (§ 7) |
| `gpg: signing failed: Unusable secret key` | a chave **expirou**, ou não tem capacidade de assinatura `[S]` | renove: `gpg --quick-set-expire <FPR> 2y`. Confirmado no teste: com a chave expirada, o `git commit -S` falha e **não** cria o commit |
| `error: unsupported value for gpg.format: ssh` | Git anterior a 2.34 | atualize (§ 2.1) ou use o método GPG |
| `error: Couldn't load public key key::ssh-ed25519 ...: No such file or directory?` | a sintaxe `key::` exige Git ≥ **2.35** | aponte `user.signingkey` para o **arquivo** `.pub`, ou atualize o Git |
| `Permissions 0644 for '.../id_ed25519' are too open.` | chave privada legível por outros | `chmod 600 ~/.ssh/id_ed25519` |
| `error: Load key "/tmp/.git_signing_key_tmpXXXX": error in libcrypto` | chave literal em `user.signingkey` numa versão do Git que não a suporta, ou chave colada com quebra de linha | use o caminho do arquivo `.pub` |
| `gpg: can't connect to the agent: IPC connect call failed` | `gpg-agent` morto, ou pasta do agente removida com ele rodando | `gpgconf --kill all` e tente de novo; confira `ls -ld ~/.gnupg` (precisa ser `700` e sua) |
| `No principal matched.` (ao verificar) | o `allowed_signers` não tem aquela chave, ou tem com `valid-before`/`valid-after` que não cobre a data | veja o arquivo; confirmado no teste: `key has expired: verify time 2026-08-13 > valid-before 2025-01-01` |
| `error: gpg.ssh.allowedSignersFile needs to be configured` | está tentando verificar assinatura SSH sem a lista | `git config --global gpg.ssh.allowedSignersFile ~/.config/git/allowed_signers` |
| `fatal: Commit XXXX does not have a GPG signature.` | `merge.verifySignatures=true` e a ponta do ramo não está assinada | assine a ponta, ou mescle sem a verificação (conscientemente) |

---

## 15. Checklist de "ambiente pronto"

Um comando por linha. Todos precisam responder antes de você abrir o
[04-como-comecar.md](04-como-comecar.md):

```bash
git --version                                   # ≥ 2.34 (ideal: 2.55)
ssh -V                                          # ≥ 8.1 (ideal 8.5+)
gpg --version | head -1                         # ≥ 2.2 (só se for usar GPG)
echo $GPG_TTY                                   # não pode estar vazio (só se for usar GPG)
ls -ld ~/.ssh ~/.gnupg 2>/dev/null              # precisam ser drwx------ (700)
git config --get user.email                     # o e-mail que está verificado no GitHub
gh auth status 2>/dev/null || echo "gh opcional"
```

E o teste que prova que a máquina consegue assinar, sem tocar em nada seu — rode o
laboratório do projeto-modelo:

```bash
cd 07-projeto-modelo && ./bin/sandbox.sh
```

Se ele chegar ao "RESUMO" com dois `[G]`, o seu ambiente está pronto.

---

## Autoteste

1. Por que o Ubuntu 22.04 é um caso de borda para este assunto?
2. Você está no macOS e o `git commit -S` falha sem mensagem clara. Quais são as duas
   primeiras coisas a conferir?
3. Por que gerar chave com `sudo` estraga tudo, concretamente?
4. Qual a diferença entre `~/.zshrc` e `~/.zprofile`, e por que ela importa aqui?
5. No Windows, por que ter Git for Windows e Gpg4win juntos causa confusão?
6. Sua empresa bloqueia servidores de chaves OpenPGP. Isso impede você de assinar? Nos dois
   métodos?
7. Você vai desinstalar tudo. Qual é o passo que quase todo mundo esquece, e que deixa um
   risco de segurança para trás?

*(Respostas: 1 — entrega Git 2.34.1, exatamente o mínimo para SSH signing, sem a sintaxe
`key::`. 2 — `pinentry-mac` instalado e configurado em `gpg-agent.conf`; `GPG_TTY` definido.
3 — `$HOME` vira `/root`, a chave nasce em `/root/.gnupg` e o seu usuário não a enxerga.
4 — `.zshrc` roda em todo terminal interativo, `.zprofile` só na sessão de login; pôr no lugar
errado faz a variável "não pegar". 5 — cada um traz o seu `gpg`, com chaveiros diferentes;
resolve-se com `git config --global gpg.program`. 6 — não impede: no SSH não se usa servidor
de chaves, e no GPG publicar é opcional — o GitHub quer a chave colada na conta.
7 — revogar/remover a chave também **no GitHub**; apagada da máquina e ainda listada na conta,
ela continua autorizada.)*

---

**Fontes consultadas em 13/08/2026:** git-scm.com (versão 2.55.0) · gnupg.org/download
(2.5.21; fim de suporte da série 2.4 em 30/06/2026) · gpg4win.org (5.1.0, 29/07/2026) ·
openssh.com/releasenotes.html (10.5) · github.com/cli/cli (2.97.0) e
`docs/install_linux.md` do projeto · launchpad.net/~git-core/+archive/ubuntu/ppa ·
docs.github.com — *Telling Git about your signing key*.
As saídas de verificação mostradas foram **executadas** em Ubuntu 22.04.5 LTS; as seções de
macOS e Windows **não** foram executadas nesta redação e seguem a documentação oficial.

**Próximo:** [04-como-comecar.md](04-como-comecar.md) — do ambiente pronto ao selo `Verified`.
