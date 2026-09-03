# 03 · Manual de instalação — todas as tecnologias, por sistema operacional

`Nível: iniciante` · `Atualizado em: 14/08/2026`

> **Boa notícia antes de tudo:** variável de ambiente **não se instala**. É um recurso
> do sistema operacional que já existe na sua máquina desde que ela foi ligada pela
> primeira vez. Você pode fazer o [04-como-comecar.md](04-como-comecar.md) **agora**,
> sem instalar nada além do runtime da sua linguagem.
>
> Este arquivo instala o **ferramental ao redor**: os runtimes, as bibliotecas `.env`,
> as ferramentas de criptografia de arquivo (SOPS/age), o detector de vazamento
> (gitleaks), o cofre local (OpenBao) e o Docker. Instale **só a seção da trilha que
> você vai seguir** — não é preciso instalar tudo.

**Ambiente onde este manual foi escrito e testado:**
Ubuntu 22.04.5 LTS · Node v24.18.0 · npm 12.0.1 · Python 3.10.12 · PHP 8.1.2 ·
Docker 29.1.3 · git 2.34.1 — verificado em **14/08/2026**.
Os comandos de macOS e Windows **não foram executados nesta máquina** e estão
marcados como tal ao final.

---

## Índice

| § | Tecnologia | Precisa se você… |
|---|---|---|
| [1](#1-tabela-de-decisão) | tabela de decisão | — |
| [2](#2-git--o-primeiro-e-mais-importante) | Git | sempre |
| [3](#3-nodejs) | Node.js + `dotenv` | trilha Node |
| [4](#4-php--composer) | PHP + Composer + `phpdotenv` | trilha PHP |
| [5](#5-python) | Python + `python-dotenv` / `pydantic-settings` | trilha Python |
| [6](#6-docker) | Docker / Podman | contêineres |
| [7](#7-direnv-opcional-mas-transforma-o-dia-a-dia) | direnv | qualquer trilha (recomendado) |
| [8](#8-sops--age--criptografar-o-env-e-versioná-lo) | SOPS + age | versionar segredo criptografado |
| [9](#9-gitleaks--impedir-que-segredo-entre-no-repositório) | gitleaks | sempre (fortemente recomendado) |
| [10](#10-openbao--vault--cofre-local) | OpenBao / Vault | cofre |
| [11](#11-alternativa-sem-instalar-nada) | **sem instalar nada** | está com pressa ou sem permissão |
| [12](#12-path-e-variáveis-de-ambiente-do-seu-shell) | PATH e perfis do shell | quando o comando "não é encontrado" |
| [13](#13-permissões-e-por-que-sudo-é-armadilha) | permissões | sempre |
| [14](#14-rede-corporativa-proxy-e-certificado-interno) | proxy corporativo | rede de empresa |
| [15](#15-convivência-de-versões) | múltiplas versões | mais de um projeto |
| [16](#16-reprodutibilidade) | lockfiles | equipe |
| [17](#17-atualizar-e-voltar-atrás) | upgrade/rollback | manutenção |
| [18](#18-desinstalar-por-completo) | desinstalação | limpeza |
| [19](#19-solução-de-problemas--mensagens-literais) | tabela de erros | quando quebrar |
| [20](#20-checklist-ambiente-pronto) | checklist final | antes de seguir |

---

## 1. Tabela de decisão

| Seu objetivo hoje | Instale só isto |
|---|---|
| Entender e testar variáveis de ambiente | nada — vá para o [04](04-como-comecar.md) |
| Rodar o projeto-modelo | §2 Git, §3 Node |
| Trabalhar com `.env` em PHP | §2, §4 |
| Trabalhar com `.env` em Python | §2, §5 |
| Nunca mais vazar segredo no Git | §2, §9 gitleaks |
| Versionar segredos criptografados | §8 SOPS + age |
| Entregar em contêiner | §6 Docker |
| Montar um cofre e brincar com ele | §6 Docker + §10 OpenBao |

---

## 2. Git — o primeiro e mais importante

Sem Git configurado, o principal risco deste assunto (commitar segredo) não pode
nem ser demonstrado nem prevenido.

### Linux — Debian/Ubuntu

```bash
sudo apt update && sudo apt install -y git
```
Instala o Git a partir do repositório da distribuição.

```bash
git --version
# esperado: git version 2.34.1 (ou superior)
```

Se a saída for `command not found`, o pacote não instalou — releia a saída do `apt`
procurando por erro de rede (veja §14 se estiver atrás de proxy).

### Linux — Fedora/RHEL/Rocky

```bash
sudo dnf install -y git
```

```bash
git --version
# esperado: git version 2.4x.x
```

### macOS

```bash
xcode-select --install
```
Instala as ferramentas de linha de comando da Apple, que incluem o Git.

Ou, com Homebrew (versão mais nova):

```bash
brew install git
```

```bash
git --version
# esperado: git version 2.39.x (Apple) ou 2.5x.x (Homebrew)
```

### Windows

**Caminho recomendado: WSL2.** Instale o Ubuntu dentro do Windows e siga as
instruções de Linux. Justificativa em §5 de [30-entrega-em-producao.md](30-entrega-em-producao.md):
o modelo de permissão de arquivo do Windows nativo não protege um `.env` do mesmo
jeito, e todo material de produção do mundo pressupõe Unix.

```powershell
wsl --install -d Ubuntu
```
Instala o WSL2 com Ubuntu. Requer reinício.

Windows nativo, se você realmente precisa:

```powershell
winget install --id Git.Git -e --source winget
```

```powershell
git --version
# esperado: git version 2.4x.x.windows.1
```

### Configuração global obrigatória para este curso

Crie um `.gitignore` **global**, que protege todos os seus repositórios de uma vez:

```bash
git config --global core.excludesfile ~/.gitignore_global
```
Diz ao Git para ler também esse arquivo ao decidir o que ignorar.

```bash
printf '.env\n.env.*\n!.env.example\n!.env.*.example\n*.pem\n*.key\nid_rsa\nid_ed25519\n' >> ~/.gitignore_global
```
Ignora `.env` e variantes em qualquer repositório seu, **exceto** os exemplos
(o `!` reverte a exclusão), e também chaves privadas soltas.

```bash
cat ~/.gitignore_global
# esperado: as 8 linhas acima
```

> ⚠️ **Isto protege você, não a equipe.** O `.gitignore` global não é versionado,
> então o colega novo não o tem. **Todo projeto ainda precisa do seu próprio
> `.gitignore` versionado com `.env` dentro.** O global é a rede de segurança
> pessoal por cima disso.

---

## 3. Node.js

### Método recomendado: gerenciador de versões (`nvm` ou `fnm`)

Por que não usar o pacote da distribuição: a versão do `apt` costuma ser antiga e
atualizar exige `sudo`, o que leva a `EACCES` em instalações globais de npm (§13).

#### Linux e macOS — `nvm`

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
```
Baixa e executa o instalador do nvm, que grava em `~/.nvm` e acrescenta linhas ao
seu `~/.bashrc` ou `~/.zshrc`.

> Antes de canalizar um script para o `bash`, o certo é olhar o que ele faz:
> `curl -o- <url> | less`. Faça isso pelo menos uma vez na vida.

```bash
exec $SHELL -l   # reabre o shell para carregar o nvm
command -v nvm
# esperado: nvm
```

Se sair vazio: o instalador não conseguiu editar o seu arquivo de perfil.
Veja §12 e acrescente as linhas à mão.

```bash
nvm install --lts
```
Instala a versão LTS (suporte de longo prazo) mais recente do Node.

```bash
node --version
# esperado: v22.x.x ou v24.x.x  (testado aqui: v24.18.0)
npm --version
# esperado: 10.x ou superior     (testado aqui: 12.0.1)
```

**Versão mínima para este curso: Node 20.6.0** — é a partir dela que existe a flag
nativa `--env-file`. **Recomendada: 22 LTS ou 24 LTS.** Evite Node 18 e anteriores:
fora de suporte de segurança e sem `--env-file`.

#### Windows

```powershell
winget install --id CoreyButler.NVMforWindows -e
```
`nvm-windows` é um projeto diferente do `nvm` de Unix, com sintaxe parecida.

```powershell
nvm install lts
nvm use lts
node --version
# esperado: v22.x.x ou superior
```

### A biblioteca `dotenv` (opcional em Node moderno)

```bash
npm install dotenv
```
Instala a biblioteca no projeto (`package.json` + `node_modules`).

```bash
node -e "console.log(require('dotenv/package.json').version)"
# esperado: 17.x.x (linha 17 é a atual em ago/2026)
```

> **Opinião profissional, e não consenso:** em projeto novo com Node ≥ 22, **não
> instale `dotenv`**. Use `node --env-file=.env app.js`, que é nativo, e no código
> leia `process.env` direto. Menos uma dependência na cadeia de suprimentos, e o
> código fica idêntico em desenvolvimento e produção.
> A contrapartida real: o carregador nativo **não faz expansão de variáveis**
> (`URL=${HOST}/api` não funciona) e não tem os utilitários de `dotenv`.
> Detalhes e comparação completa em [15-node.md](15-node.md).

---

## 4. PHP + Composer

### Linux — Debian/Ubuntu

```bash
sudo apt update && sudo apt install -y php-cli php-mbstring unzip
```
Instala o PHP de linha de comando e a extensão `mbstring`, exigida pelo Composer.

```bash
php --version
# esperado: PHP 8.1.x ou superior (testado aqui: PHP 8.1.2)
```

**Versão mínima do `vlucas/phpdotenv` 5.6: PHP 7.2.5.** Recomendado: **PHP 8.2+**
(8.1 saiu do suporte de segurança em 31/12/2025). Para PHP 8.3/8.4 no Ubuntu, use
o PPA do Ondřej Surý:

```bash
sudo add-apt-repository -y ppa:ondrej/php && sudo apt update && sudo apt install -y php8.3-cli php8.3-mbstring
```

### Linux — Fedora/RHEL

```bash
sudo dnf install -y php-cli php-mbstring unzip
```

### macOS

```bash
brew install php composer
```

```bash
php --version
# esperado: PHP 8.3.x ou superior
```

### Windows

Caminho recomendado: WSL2 (§2). Nativo:

```powershell
winget install --id PHP.PHP.8.3 -e
```

Depois é **obrigatório** conferir o PATH (§12) e habilitar extensões editando o
`php.ini` — no Windows o PHP vem com quase tudo comentado:

```powershell
php --version
# esperado: PHP 8.3.x (cli)
```

### Composer (gerenciador de pacotes do PHP)

```bash
php -r "copy('https://getcomposer.org/installer', 'composer-setup.php');"
```
Baixa o instalador oficial.

```bash
php -r "if (hash_file('sha384', 'composer-setup.php') === trim(file_get_contents('https://composer.github.io/installer.sig'))) { echo 'OK'.PHP_EOL; } else { echo 'CORROMPIDO'.PHP_EOL; unlink('composer-setup.php'); }"
```
**Verifica a assinatura do instalador antes de executá-lo.** Não pule este passo:
é literalmente um ataque de cadeia de suprimentos que você está evitando.

```
# esperado: OK
```

```bash
php composer-setup.php --install-dir=/usr/local/bin --filename=composer && rm composer-setup.php
```
Instala o Composer como comando global e apaga o instalador.

```bash
composer --version
# esperado: Composer version 2.x.x
```

### A biblioteca `phpdotenv`

```bash
composer require vlucas/phpdotenv
```

```bash
composer show vlucas/phpdotenv | head -3
# esperado: versions : * v5.6.x
```

Versão atual da linha 5.6 em ago/2026: **v5.6.3** (27/12/2025), com suporte oficial
a PHP 8.5. Se você usa **Laravel** ou **Symfony**, `phpdotenv` já vem junto — não
instale de novo. Ver [16-php.md](16-php.md).

---

## 5. Python

### Linux — Debian/Ubuntu

```bash
sudo apt update && sudo apt install -y python3 python3-venv python3-pip
```
Instala o Python, o módulo de ambientes virtuais e o `pip`.

```bash
python3 --version
# esperado: Python 3.10.x ou superior (testado aqui: 3.10.12)
```

**Mínimo recomendado para projetos novos: Python 3.11.** 3.9 e anteriores estão
no fim da vida. Para versões mais novas que a da distro, use `pyenv` ou `uv`.

### Linux — Fedora/RHEL

```bash
sudo dnf install -y python3 python3-pip
```

### macOS

```bash
brew install python@3.12
```

> **Nunca use o Python que vem de fábrica no macOS** (`/usr/bin/python3`) para
> instalar pacotes: ele é do sistema, e mexer nele quebra ferramentas do próprio macOS.

### Windows

```powershell
winget install --id Python.Python.3.12 -e
```

Marque **"Add Python to PATH"** se usar o instalador gráfico. Se esqueceu, veja §12.

```powershell
python --version
# esperado: Python 3.12.x
```

### Ambiente virtual — obrigatório, não opcional

```bash
python3 -m venv .venv
```
Cria uma cópia isolada do Python dentro da pasta do projeto.

```bash
source .venv/bin/activate          # Linux/macOS
# .venv\Scripts\Activate.ps1       # Windows PowerShell
```

```bash
which python
# esperado: /caminho/do/projeto/.venv/bin/python
```

Se apontar para `/usr/bin/python`, o `activate` não funcionou — confira se você usou
`source` (e não executou o script direto).

### As bibliotecas

```bash
pip install python-dotenv
```

```bash
python -c "import dotenv, importlib.metadata as m; print(m.version('python-dotenv'))"
# esperado: 1.2.2 (versão de 01/03/2026) ou superior
```

> 🔒 **Atualize para ≥ 1.2.2.** Versões anteriores tinham uma falha em `set_key()` e
> `unset_key()`: elas **seguiam links simbólicos** ao reescrever o `.env`, o que
> permitia sobrescrever arquivos fora do lugar previsto.

Para configuração validada e tipada (o que eu recomendo em projeto sério):

```bash
pip install pydantic-settings
```

```bash
python -c "import importlib.metadata as m; print(m.version('pydantic-settings'))"
# esperado: 2.14.x ou superior
```

---

## 6. Docker

### Linux — Debian/Ubuntu (repositório oficial, não o do Ubuntu)

```bash
sudo apt update && sudo apt install -y ca-certificates curl gnupg
```

```bash
sudo install -m 0755 -d /etc/apt/keyrings && curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg && sudo chmod a+r /etc/apt/keyrings/docker.gpg
```
Adiciona a chave GPG oficial da Docker, para o `apt` verificar a autenticidade dos pacotes.

```bash
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo $VERSION_CODENAME) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

```bash
sudo apt update && sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

```bash
docker --version
# esperado: Docker version 27.x ou superior (testado aqui: 29.1.3)
docker compose version
# esperado: Docker Compose version v2.x.x
```

```bash
sudo usermod -aG docker $USER && newgrp docker
```
Permite rodar `docker` sem `sudo`. **Entenda o que isso significa:** o grupo `docker`
dá acesso equivalente a root na máquina (é possível montar `/` dentro de um contêiner).
Em servidor multiusuário, prefira **rootless mode** ou **Podman**.

```bash
docker run --rm hello-world
# esperado: "Hello from Docker!"
```

### macOS e Windows

Instale **Docker Desktop** pelo site oficial. Atenção à licença: **Docker Desktop é
pago para empresas com mais de 250 funcionários ou receita acima de US$ 10 milhões
por ano** — a versão gratuita cobre uso pessoal, educação e pequenas empresas.
Alternativas gratuitas: **Podman Desktop**, **Rancher Desktop**, **colima** (macOS).
Ver [80-custos-e-licencas.md](80-custos-e-licencas.md).

---

## 7. `direnv` — opcional, mas transforma o dia a dia

`direnv` carrega e **descarrega** variáveis automaticamente quando você entra e sai
da pasta do projeto no terminal. Elimina a classe inteira de erro
"rodei o script de produção com o `.env` de desenvolvimento carregado".

```bash
sudo apt install -y direnv        # Debian/Ubuntu
sudo dnf install -y direnv        # Fedora
brew install direnv               # macOS
```

Ative no seu shell (esta linha vai no arquivo de perfil — ver §12):

```bash
echo 'eval "$(direnv hook bash)"' >> ~/.bashrc && exec $SHELL -l
```
Para zsh, troque `bash` por `zsh`; para fish, `fish`.

```bash
direnv version
# esperado: 2.32.x ou superior
```

Uso:

```bash
mkdir -p /tmp/teste-direnv && cd /tmp/teste-direnv
echo 'export MINHA_VAR=oi' > .envrc
direnv allow            # obrigatório: aprova o arquivo (segurança)
echo $MINHA_VAR
# esperado: oi
cd .. && echo "[$MINHA_VAR]"
# esperado: []   ← descarregou sozinha ao sair da pasta
```

O `direnv allow` existe porque `.envrc` é **script executável**, não um arquivo de
dados. Nunca dê `allow` num `.envrc` que veio de repositório de terceiro sem ler.

---

## 8. SOPS + age — criptografar o `.env` e versioná-lo

SOPS (**S**ecrets **OP**eration**S**) criptografa **só os valores** de um arquivo
YAML/JSON/ENV, deixando as chaves legíveis — então o `git diff` continua útil.
Nasceu na Mozilla em 2015 e é hoje projeto **sandbox da CNCF**, mantido pela
organização `getsops`. Versão atual da linha 3: **v3.13.x** (ago/2026).

`age` é a ferramenta de criptografia moderna que substitui o GPG para este uso —
chaves curtas, sem cadeia de confiança, sem 400 opções.

### Linux

```bash
sudo apt install -y age            # Debian 12+/Ubuntu 22.04+
sudo dnf install -y age            # Fedora
```

```bash
age --version
# esperado: v1.1.x ou superior
```

SOPS não está nos repositórios da maioria das distros — baixe o binário da release:

```bash
SOPS_VER=v3.13.0
curl -LO "https://github.com/getsops/sops/releases/download/${SOPS_VER}/sops-${SOPS_VER}.linux.amd64"
```
Baixa o binário. **Confira em github.com/getsops/sops/releases qual é a última
versão antes de rodar** — a que está aqui é a de ago/2026.

```bash
sudo install -m 0755 "sops-${SOPS_VER}.linux.amd64" /usr/local/bin/sops && rm "sops-${SOPS_VER}.linux.amd64"
```

```bash
sops --version
# esperado: sops 3.13.x
```

### macOS

```bash
brew install sops age
```

### Windows

```powershell
winget install --id Mozilla.SOPS -e
winget install --id FiloSottile.age -e
```

### Gerar sua chave e testar

```bash
mkdir -p ~/.config/sops/age && age-keygen -o ~/.config/sops/age/keys.txt
```
Gera o par de chaves. A saída no terminal mostra a **chave pública** (`age1...`);
o arquivo contém a **privada**.

```bash
chmod 600 ~/.config/sops/age/keys.txt
```
**Este arquivo é o segredo que protege todos os outros segredos.** Se ele vazar,
tudo que foi criptografado com ele vazou junto.

```bash
age-keygen -y ~/.config/sops/age/keys.txt
# esperado: age1xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

Teste completo:

```bash
cd /tmp && printf 'DB_PASSWORD: senha-secreta\nAPP_NAME: loja\n' > cofre.yaml
export SOPS_AGE_RECIPIENTS=$(age-keygen -y ~/.config/sops/age/keys.txt)
sops --encrypt --in-place cofre.yaml
grep DB_PASSWORD cofre.yaml
# esperado: DB_PASSWORD: ENC[AES256_GCM,data:...,type:str]
sops --decrypt cofre.yaml
# esperado: DB_PASSWORD: senha-secreta
```

Se `sops --decrypt` reclamar de chave, exporte o caminho:
`export SOPS_AGE_KEY_FILE=~/.config/sops/age/keys.txt`.

Uso completo em [40-cofres-de-segredos.md §5](40-cofres-de-segredos.md).

---

## 9. gitleaks — impedir que segredo entre no repositório

Escaneia código e histórico do Git procurando padrões de segredo. Licença MIT, escrito
em Go, rápido o bastante para rodar como gancho de pre-commit (menos de um segundo
num diff típico).

```bash
GITLEAKS_VER=8.28.0
curl -LO "https://github.com/gitleaks/gitleaks/releases/download/v${GITLEAKS_VER}/gitleaks_${GITLEAKS_VER}_linux_x64.tar.gz"
```
Confira a última versão em github.com/gitleaks/gitleaks/releases antes de rodar.

```bash
tar -xzf "gitleaks_${GITLEAKS_VER}_linux_x64.tar.gz" gitleaks && sudo install -m 0755 gitleaks /usr/local/bin/ && rm gitleaks "gitleaks_${GITLEAKS_VER}_linux_x64.tar.gz"
```

```bash
gitleaks version
# esperado: 8.x.x
```

macOS: `brew install gitleaks`. Windows: `winget install --id Gitleaks.Gitleaks -e`.

Teste imediato num repositório qualquer:

```bash
cd seu-projeto && gitleaks git --no-banner
# esperado: "no leaks found"  — se aparecer achado, leia 50-vazamentos-e-resposta.md
```

Sem instalar nada, via Docker:

```bash
docker run --rm -v "$PWD:/repo" zricethezav/gitleaks:latest git /repo --no-banner
```

O gancho de pre-commit que bloqueia o commit está em
[50-vazamentos-e-resposta.md §2](50-vazamentos-e-resposta.md).

---

## 10. OpenBao / Vault — cofre local

**Contexto de licença, que você precisa saber antes de escolher:**
em agosto de 2023 a HashiCorp trocou a licença do Vault de MPL 2.0 para **BUSL 1.1**
(uso permitido, exceto oferecer o produto como serviço concorrente; cada versão
volta a ser MPL 2.0 quatro anos depois). A comunidade — com engenheiros da IBM à
frente — forkou a última versão MPL (1.14.0) e criou o **OpenBao**, hoje sob a
**Linux Foundation**, licença MPL 2.0. A IBM concluiu a compra da HashiCorp no
início de 2025; a versão paga chama-se **IBM Vault Enterprise**. O OpenBao chegou
ao 2.0 em setembro de 2024 e tem adotantes de peso (a Nvidia consta na lista oficial).

**Minha recomendação:** para aprender, **OpenBao** — mesma API, mesma CLI, licença
sem pegadinha. Para empresa que já paga Vault Enterprise, siga com o Vault.

### O jeito mais rápido: contêiner em modo de desenvolvimento

```bash
docker run --rm -d --name bao -p 8200:8200 -e BAO_DEV_ROOT_TOKEN_ID=raiz openbao/openbao:latest server -dev -dev-listen-address=0.0.0.0:8200
```
Sobe um cofre **em memória, sem persistência e destravado** — bom para aprender,
**criminoso em produção**.

```bash
curl -s http://127.0.0.1:8200/v1/sys/health | head -c 200
# esperado: JSON com "initialized":true,"sealed":false
```

Abra `http://127.0.0.1:8200` no navegador e entre com o token `raiz`.

Para parar: `docker stop bao`.

### CLI nativa (opcional)

Binário em github.com/openbao/openbao/releases; instale igual ao SOPS (§8).

```bash
bao version
# esperado: OpenBao v2.x.x
```

---

## 11. Alternativa sem instalar nada

Se você quer começar **hoje**, ou não tem permissão de instalar na máquina do trabalho:

| Opção | O que dá para fazer | Link |
|---|---|---|
| **O terminal que você já tem** | tudo do [04-como-comecar.md](04-como-comecar.md): `export`, `printenv`, passar variável na linha de comando. Isso sozinho já ensina 70% do conceito | — |
| **GitHub Codespaces** | ambiente completo Linux no navegador, com Node/Python/PHP/Docker prontos; camada gratuita mensal para contas pessoais | github.com/codespaces |
| **Gitpod** | idem, com camada gratuita | gitpod.io |
| **Replit** | Node/Python no navegador; tem painel de "Secrets" que é, ele mesmo, um bom exemplo didático do conceito | replit.com |
| **Play with Docker** | sessões Docker de 4 horas no navegador, grátis | labs.play-with-docker.com |
| **`php -a` / `node` / `python3` já instalados** | a maioria das distros Linux já traz Python 3 | — |

Recomendação honesta: comece **no seu próprio terminal**, sem instalar nada, e só
instale a partir do §3 quando precisar do projeto-modelo.

---

## 12. PATH e variáveis de ambiente do seu shell

Metade dos "não funciona" desta área é PATH.

### Como conferir

```bash
echo $PATH
# esperado: uma lista separada por ':' — /usr/local/bin:/usr/bin:/bin...
```

```bash
which sops age gitleaks node php python3 2>&1
```
Mostra o caminho de cada binário, ou nada se não estiver no PATH.

### Qual arquivo editar

| Shell / SO | Arquivo | Quando é lido |
|---|---|---|
| bash (Linux, login) | `~/.bash_profile` ou `~/.profile` | ao fazer login |
| bash (Linux, interativo) | `~/.bashrc` | a cada terminal novo |
| zsh (macOS padrão desde Catalina) | `~/.zshrc` | a cada terminal novo |
| fish | `~/.config/fish/config.fish` | a cada terminal novo |
| PowerShell | caminho em `$PROFILE` | a cada terminal novo |
| **contexto não-interativo (cron, systemd, CI)** | **nenhum destes** | ⚠️ ver aviso abaixo |

Adicionar um diretório ao PATH:

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc && exec $SHELL -l
```
Acrescenta a linha ao perfil e reabre o shell.

### **Por que "não pegou" antes de reabrir o terminal**

Esta é a dúvida número um, e a resposta explica o assunto inteiro do curso:

> O ambiente é **copiado** do processo pai para o filho **no instante da criação do
> processo** (a chamada `execve` do Unix — ver [10-fundamentos.md](10-fundamentos.md)).
> Editar o `~/.bashrc` muda um **arquivo**; o processo do seu terminal, que já está
> rodando, tem uma cópia do ambiente feita **antes** dessa edição, e ela não muda
> retroativamente. Só um shell **novo** lerá o arquivo novo.

Por isso `exec $SHELL -l` ou `source ~/.bashrc` resolvem: o primeiro substitui o
processo; o segundo relê o arquivo dentro do processo atual.

### ⚠️ O erro clássico de produção

Você põe `export DATABASE_URL=...` no `~/.bashrc`, testa por SSH, funciona.
Aí o serviço sobe pelo **systemd** ou pelo **cron** — e não enxerga nada.
Motivo: nenhum dos dois inicia um shell de login, então `~/.bashrc` **nunca é lido**.
A correção está em [30-entrega-em-producao.md §2](30-entrega-em-producao.md).

**Nunca coloque segredo de produção no `~/.bashrc`.** Ele é lido por todo processo
interativo, aparece em `history`, e vaza em qualquer `ps e` de outro usuário privilegiado.

---

## 13. Permissões, e por que `sudo` é armadilha

### O caso `sudo npm install -g`

```bash
sudo npm install -g alguma-coisa     # ❌ NÃO FAÇA
```

Por que é problema, de verdade (não é superstição):

1. O `npm` executa **scripts de instalação** (`postinstall`) dos pacotes.
   Com `sudo`, esse script arbitrário de um terceiro roda **como root**.
   Um pacote comprometido na cadeia de dependências ganha a máquina inteira.
2. Arquivos passam a pertencer ao root em `~/.npm`, e o próximo comando sem `sudo`
   falha com `EACCES` — o que leva a pessoa a usar `sudo` para tudo, piorando.

**Caminho certo:** use `nvm`/`fnm` (§3) — o Node fica em `~/.nvm`, seu usuário é
dono de tudo, `sudo` nunca é necessário.

Se você já se meteu nisso:

```bash
sudo chown -R $(whoami) ~/.npm ~/.config
```
Devolve a posse dos diretórios ao seu usuário.

### O mesmo vale para `pip`

```bash
sudo pip install pacote            # ❌ pode quebrar ferramentas do sistema
python3 -m venv .venv              # ✅
```

Em Debian/Ubuntu modernos o `pip` global recusa instalar
(`error: externally-managed-environment`) exatamente para impedir isso — ver §19.

### Permissões de um `.env` em servidor

```bash
chmod 600 .env && chown appuser:appuser .env
```
Só o usuário que roda a aplicação lê e escreve. Ninguém mais, nem o grupo.

```bash
ls -l .env
# esperado: -rw------- 1 appuser appuser ... .env
```

Se aparecer `-rw-r--r--` (644), **qualquer usuário do servidor lê suas senhas**.
Em hospedagem compartilhada de PHP isso significa: os outros clientes do servidor.

O `umask` decide a permissão padrão de arquivos novos:

```bash
umask
# esperado: 0022 (arquivo nasce 644) — para segredo, prefira 0077 no processo que cria
```

---

## 14. Rede corporativa: proxy e certificado interno

```bash
export HTTP_PROXY=http://proxy.empresa.com:8080
export HTTPS_PROXY=http://proxy.empresa.com:8080
export NO_PROXY=localhost,127.0.0.1,.empresa.com
```

Configuração por ferramenta:

```bash
npm config set proxy http://proxy.empresa.com:8080
npm config set https-proxy http://proxy.empresa.com:8080
git config --global http.proxy http://proxy.empresa.com:8080
pip config set global.proxy http://proxy.empresa.com:8080
composer config --global http-basic.repo.packagist.org usuario senha   # se houver espelho autenticado
```

> ⚠️ **Ironia perigosa:** ao configurar o proxy com usuário e senha, você acabou de
> escrever uma credencial em `~/.npmrc`, `~/.gitconfig` e `~/.config/pip/pip.conf`
> em texto puro. Esses arquivos são candidatos frequentes a vazar em imagem Docker
> (`COPY . .` copia tudo). Trate-os como segredo: `chmod 600` e no `.dockerignore`.

**Certificado interno** (a empresa faz inspeção TLS):

```bash
export NODE_EXTRA_CA_CERTS=/caminho/ca-empresa.pem
export REQUESTS_CA_BUNDLE=/caminho/ca-empresa.pem     # Python (requests)
export SSL_CERT_FILE=/caminho/ca-empresa.pem
git config --global http.sslCAInfo /caminho/ca-empresa.pem
```

**Nunca** use `npm config set strict-ssl false` nem `NODE_TLS_REJECT_UNAUTHORIZED=0`
como solução permanente: isso desliga a verificação de certificado para **todo**
tráfego do processo, o que é bem pior que o problema original.

---

## 15. Convivência de versões

| Runtime | Ferramenta | Arquivo do projeto |
|---|---|---|
| Node | `nvm`, `fnm` | `.nvmrc` |
| Python | `pyenv`, `uv` | `.python-version` |
| PHP | `phpenv`, ou pacotes `php8.2-*`/`php8.3-*` lado a lado + `update-alternatives` | — |
| Vários de uma vez | **`mise`** (antigo rtx) ou `asdf` | `.tool-versions` |

Minha recomendação para quem mexe em três linguagens (é o caso deste curso): **`mise`**.
Um só arquivo `.tool-versions` fixa Node, Python e PHP do projeto, e a troca é automática
ao entrar na pasta.

```bash
curl https://mise.run | sh
echo 'eval "$(~/.local/bin/mise activate bash)"' >> ~/.bashrc && exec $SHELL -l
mise --version
# esperado: 2026.x.x
```

```bash
mise use node@22 python@3.12
cat .tool-versions
# esperado: node 22.x.x / python 3.12.x
```

---

## 16. Reprodutibilidade

| Item | Arquivo | Vai para o Git? |
|---|---|---|
| Versão do runtime | `.nvmrc`, `.python-version`, `.tool-versions` | **sim** |
| Dependências travadas | `package-lock.json`, `composer.lock`, `requirements.txt`/`uv.lock` | **sim** |
| **Nomes** das variáveis exigidas | `.env.example` | **sim** |
| **Valores** das variáveis | `.env` | **NÃO** |
| Segredos criptografados | `secrets.enc.yaml` (SOPS) | sim, se criptografado |
| Imagem do ambiente | `Dockerfile`, `compose.yaml` | **sim** |

O `.env.example` é peça central e quase sempre esquecida: é o **contrato** de quais
variáveis o sistema exige. Sem ele, quem instalar o sistema no cliente descobre o que
falta por tentativa e erro.

```bash
# gera um .env.example a partir do .env, mantendo nomes e apagando valores
sed -E 's/=.*/=/' .env > .env.example
```

Confira o resultado à mão antes de commitar — se algum valor de exemplo tiver ficado
(por exemplo em linhas comentadas), você acabou de vazar.

---

## 17. Atualizar e voltar atrás

```bash
nvm install 24 --reinstall-packages-from=22   # Node: instala 24 trazendo os pacotes globais
nvm use 22                                    # volta atrás na hora
```

```bash
pip install --upgrade python-dotenv
pip install python-dotenv==1.0.1              # volta a uma versão específica
```

```bash
composer update vlucas/phpdotenv
git checkout composer.lock && composer install # volta ao estado travado
```

Para SOPS/age/gitleaks (binários soltos), guarde a versão anterior antes de trocar:

```bash
sudo cp /usr/local/bin/sops /usr/local/bin/sops.bak
```

**Regra de ouro na atualização de biblioteca de configuração:** leia o `UPGRADING.md`.
A passagem do `phpdotenv` 4 para 5 mudou o comportamento de `$_ENV` e `getenv()`, e a
do `dotenv` (Node) 16 para 17 mexeu na saída de log. Ambas quebram silenciosamente.

---

## 18. Desinstalar por completo

### Node via nvm

```bash
nvm deactivate && rm -rf ~/.nvm
```
Remova também as linhas do `nvm` do `~/.bashrc`/`~/.zshrc`.

Sobras frequentemente esquecidas:

```bash
rm -rf ~/.npm ~/.node-gyp ~/.npmrc
```
⚠️ `~/.npmrc` costuma conter **tokens de registry privado**. Apagar é o certo; se for
só desinstalar temporariamente, ao menos confira o conteúdo.

### Python

```bash
rm -rf .venv ~/.cache/pip
```

### PHP/Composer

```bash
sudo rm /usr/local/bin/composer && rm -rf ~/.composer ~/.config/composer ~/.cache/composer
```
⚠️ `~/.composer/auth.json` guarda **credenciais de repositórios privados**.

### Docker

```bash
sudo apt purge -y docker-ce docker-ce-cli containerd.io && sudo rm -rf /var/lib/docker /var/lib/containerd
```
⚠️ Isto apaga **todas as imagens, contêineres e volumes**. Volumes podem conter dados.

### SOPS / age / gitleaks

```bash
sudo rm -f /usr/local/bin/sops /usr/local/bin/gitleaks
```

```bash
rm -rf ~/.config/sops
```
🚨 **Pare antes de rodar isto.** `~/.config/sops/age/keys.txt` é a chave privada que
decifra todos os seus arquivos SOPS. Apagá-la **torna todo arquivo criptografado com
ela permanentemente ilegível**. Faça backup fora da máquina antes.

### direnv

```bash
sudo apt purge -y direnv && rm -rf ~/.local/share/direnv
```

---

## 19. Solução de problemas — mensagens literais

| Mensagem | Causa provável | Correção |
|---|---|---|
| `command not found: sops` (ou `node`, `php`, `gitleaks`) | binário fora do PATH, ou shell não recarregado | `which sops`; se vazio, veja §12 e rode `exec $SHELL -l` |
| `EACCES: permission denied, mkdir '/usr/lib/node_modules/...'` | `npm -g` sem permissão | **não** use `sudo`; instale via `nvm` (§3) e reinstale o pacote |
| `error: externally-managed-environment` (pip, Debian/Ubuntu 23+) | proteção contra quebrar o Python do sistema | crie um venv: `python3 -m venv .venv && source .venv/bin/activate`. `--break-system-packages` existe, e o nome é um aviso |
| `ModuleNotFoundError: No module named 'dotenv'` | instalou fora do venv, ou esqueceu de ativá-lo | `which python` deve apontar para `.venv/bin/python`; reative e reinstale |
| `Warning: require(vendor/autoload.php): Failed to open stream` | não rodou `composer install` | `composer install` na raiz do projeto |
| `PHP Warning: Module "mbstring" is already loaded` / Composer reclama de mbstring | extensão faltando ou duplicada | `sudo apt install php-mbstring`; confira `php -m \| grep mbstring` |
| `Cannot connect to the Docker daemon at unix:///var/run/docker.sock` | serviço parado ou usuário fora do grupo `docker` | `sudo systemctl start docker`; `sudo usermod -aG docker $USER && newgrp docker` |
| `Failed to get the data key required to decrypt the SOPS file` | a chave `age` não está onde o SOPS procura | `export SOPS_AGE_KEY_FILE=~/.config/sops/age/keys.txt` |
| `.env` existe mas as variáveis chegam `undefined` | caminho relativo: a biblioteca procura o `.env` no **diretório de trabalho atual**, não ao lado do arquivo `.js`/`.py` | rode a partir da raiz do projeto, ou passe o caminho absoluto — ver [75-armadilhas.md #3](75-armadilhas.md) |
| `EnvironmentFile: No such file or directory` (systemd) | caminho errado ou SELinux bloqueando | caminho absoluto na unit; `sudo systemctl daemon-reload`; conferir contexto SELinux em RHEL |
| `self-signed certificate in certificate chain` | proxy corporativo com inspeção TLS | `NODE_EXTRA_CA_CERTS` / `REQUESTS_CA_BUNDLE` (§14). Não desligue a verificação |
| `direnv: error .envrc is blocked` | proteção do direnv contra script não aprovado | leia o arquivo, depois `direnv allow` |
| `gitleaks: leaks found: 3` no CI | há segredo no diff ou no histórico | **não é falso alarme até prova em contrário** — [50-vazamentos-e-resposta.md](50-vazamentos-e-resposta.md) |

---

## 20. Checklist "ambiente pronto"

Rode tudo; cada linha deve responder algo, não erro.

```bash
git --version
```
```bash
cat ~/.gitignore_global | grep -c '.env'
```
```bash
node --version
```
```bash
npm --version
```
```bash
python3 --version
```
```bash
php --version | head -1
```
```bash
composer --version
```
```bash
docker --version
```
```bash
docker compose version
```
```bash
sops --version
```
```bash
age --version
```
```bash
gitleaks version
```
```bash
direnv version
```
```bash
printenv | wc -l
```
```bash
echo "$PATH" | tr ':' '\n' | head
```

Faltando algum? Só instale se for da trilha que você vai seguir (§1).
**O mínimo absoluto para seguir para o próximo arquivo é: um terminal.**

---

## Autoteste

1. Por que uma alteração no `~/.bashrc` não afeta o terminal que já está aberto?
2. Cite dois motivos técnicos para não usar `sudo npm install -g`.
3. Qual permissão um `.env` deve ter num servidor, e o que significa cada dígito?
4. Por que o `systemd` não lê o seu `~/.bashrc`?
5. Qual arquivo do SOPS/age você **jamais** pode perder, e o que acontece se perder?
6. O que o `.env.example` faz que o `.env` não faz?
7. Por que configurar proxy corporativo pode, ele mesmo, criar um vazamento?
8. Qual a versão mínima de Node para usar `--env-file` sem biblioteca?

---

**Fontes consultadas em 14/08/2026:** pypi.org/project/python-dotenv ·
github.com/vlucas/phpdotenv/releases · github.com/getsops/sops/releases ·
nodejs.org (release schedule) · docs.docker.com/engine/install ·
github.com/openbao/openbao · getcomposer.org/download.
**Versões testadas nesta máquina (Ubuntu 22.04.5, 14/08/2026):** Node v24.18.0,
npm 12.0.1, Python 3.10.12, PHP 8.1.2, Docker 29.1.3, git 2.34.1.
**Não executado aqui:** instalação em macOS e Windows, `winget`, Homebrew, `nvm-windows`.

**Próximo:** [04-como-comecar.md](04-como-comecar.md) · Voltar ao [mapa](00-MAPA.md)
