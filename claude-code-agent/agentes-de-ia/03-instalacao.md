# 03 · Manual de instalação

**Nível:** iniciante · **Pesquisado na web e testado em 13/08/2026**

Este é um manual de campo. Siga na ordem, sem improvisar. Cada passo tem
comando exato, o que ele faz, como verificar e o que fazer se a saída for
diferente.

**Versões testadas:** Claude Code 2.1.231 · Node.js v24.18.0 · Python 3.10.12 ·
Ubuntu 22.04 (kernel 6.8) — verificado em 13/08/2026.
Versão mínima do Claude Code para tudo neste curso: **2.1.0**.
Evite: qualquer versão anterior a 2.0 (a interface e os comandos mudaram).

---

## 0. Antes de instalar qualquer coisa: comece sem instalar nada

Se você só quer ver o assunto funcionando hoje, existem dois caminhos sem
instalação local:

| Caminho | Como | Limite |
|---|---|---|
| **Claude Code na web** | [claude.ai/code](https://claude.ai/code) → conecte um repositório do GitHub → descreva a tarefa. Roda em VM da Anthropic; devolve um pull request. | Exige assinatura e um repo no GitHub. Não toca na sua máquina. |
| **App de desktop** | Baixe o app ([macOS](https://claude.ai/download), [Windows](https://claude.com/download), [Linux](https://code.claude.com/docs/en/desktop-linux)) e use com interface gráfica. | Ainda instala software, mas sem terminal. |

Faça isso primeiro. Depois volte e instale local — é o que evita a desistência
no primeiro dia por causa de um erro de PATH.

---

## 1. Claude Code

### 1.1 Escolha do método

| Método | Atualiza sozinho? | Quando usar |
|---|---|---|
| **Instalador nativo** | ✅ sim, em segundo plano | **recomendado.** Padrão para macOS, Linux, WSL e Windows. |
| Homebrew (macOS/Linux) | ❌ não | você já gerencia tudo por brew e quer consistência |
| WinGet (Windows) | ❌ não | política corporativa exige gerenciador do sistema |
| apt / dnf / apk (Linux) | ❌ não (usa o ciclo do sistema) | servidores, imagens, política de pacotes assinados |
| npm global | ⚠️ só se o diretório global for gravável | você já tem Node e prefere um só gerenciador |

> **Recomendação:** instalador nativo, salvo política corporativa em
> contrário. Ele é um binário — **não depende de Node em tempo de execução**,
> mesmo quando instalado via npm.

### 1.2 Linux (Debian/Ubuntu e Fedora/RHEL) — instalador nativo

```bash
curl -fsSL https://claude.ai/install.sh | bash
```
Baixa e instala o binário em `~/.local/share/claude/versions/` e cria o
lançador em `~/.local/bin/claude`.

Verifique:

```bash
claude --version
# esperado: 2.1.231 (Claude Code)  — ou superior
```

**Se der `command not found: claude`:** `~/.local/bin` não está no `PATH`.
Vá para a [seção 6](#6-path-e-variáveis-de-ambiente).

**Se der `syntax error near unexpected token '<'` ou um erro de HTTP:** o
`curl` recebeu uma página de erro em vez do script — quase sempre proxy
corporativo. Veja a [seção 8](#8-rede-corporativa).

### 1.3 Linux — repositórios assinados (apt / dnf / apk)

Use quando a política proíbe `curl | bash`. Os repositórios são assinados com
a chave de release do Claude Code; a impressão digital é
`31DDDE24DDFAB679F42D7BD2BAA929FF1A7ECACE`.

<details>
<summary><b>Debian / Ubuntu (apt)</b></summary>

```bash
sudo apt install curl gnupg
```
Garante as duas ferramentas usadas abaixo (instalações mínimas não as têm).

```bash
sudo install -d -m 0755 /etc/apt/keyrings
sudo curl -fsSL https://downloads.claude.ai/keys/claude-code.asc \
  -o /etc/apt/keyrings/claude-code.asc
```
Baixa a chave pública de assinatura.

```bash
gpg --show-keys /etc/apt/keyrings/claude-code.asc
# esperado, na linha da impressão digital:
# 31DD DE24 DDFA B679 F42D  7BD2 BAA9 29FF 1A7E CACE
```
**Confira essa impressão digital antes de continuar.** Se não bater, ou se o
gpg disser que não há dado OpenPGP válido, o download falhou ou foi
interceptado — não prossiga.

```bash
echo "deb [signed-by=/etc/apt/keyrings/claude-code.asc] https://downloads.claude.ai/claude-code/apt/stable stable main" \
  | sudo tee /etc/apt/sources.list.d/claude-code.list
sudo apt update
sudo apt install claude-code
```
Registra o repositório no canal `stable` (≈ uma semana de atraso, pulando
versões com regressão grave) e instala.

Para o canal `latest`, troque **as duas** ocorrências: a URL
(`.../apt/latest`) e o nome da suíte (`latest main`).

Atualizar depois: `sudo apt update && sudo apt upgrade claude-code`.
</details>

<details>
<summary><b>Fedora / RHEL (dnf)</b></summary>

```bash
sudo tee /etc/yum.repos.d/claude-code.repo <<'EOF'
[claude-code]
name=Claude Code
baseurl=https://downloads.claude.ai/claude-code/rpm/stable
enabled=1
gpgcheck=1
gpgkey=https://downloads.claude.ai/keys/claude-code.asc
EOF
sudo dnf install claude-code
```
O dnf pedirá confirmação da impressão digital na primeira instalação.
Confira contra `31DD DE24 DDFA B679 F42D 7BD2 BAA9 29FF 1A7E CACE`.

Canal `latest`: troque `rpm/stable` por `rpm/latest`.
Atualizar: `sudo dnf upgrade claude-code`.
</details>

<details>
<summary><b>Alpine (apk)</b></summary>

Alpine usa musl e não traz `bash` nem `curl`. Instale as dependências antes:

```sh
apk add bash curl libgcc libstdc++ ripgrep
```

`ripgrep` está no repositório `community`. Se faltar, adicione-o (ajuste a
versão do Alpine):

```sh
echo "https://dl-cdn.alpinelinux.org/alpine/v3.22/community" >> /etc/apk/repositories
apk update
```

Depois:

```sh
wget -O /etc/apk/keys/claude-code.rsa.pub https://downloads.claude.ai/keys/claude-code.rsa.pub
sha256sum /etc/apk/keys/claude-code.rsa.pub
# esperado: 395759c1f7449ef4cdef305a42e820f3c766d6090d142634ebdb049f113168b6
echo "https://downloads.claude.ai/claude-code/apk/stable" >> /etc/apk/repositories
apk add claude-code
```

E desative o ripgrep embutido, que é glibc:

```json
// ~/.claude/settings.json
{ "env": { "USE_BUILTIN_RIPGREP": "0" } }
```
</details>

### 1.4 macOS

```bash
curl -fsSL https://claude.ai/install.sh | bash
```
Mesmo instalador do Linux. Funciona igual em Intel e Apple Silicon — o script
detecta a arquitetura e baixa o binário correto.

Alternativa via Homebrew:

```bash
brew install --cask claude-code
```

> Há **dois** casks. `claude-code` segue o canal *stable*;
> `claude-code@latest` segue o *latest*. Homebrew **não atualiza sozinho**:
> rode `brew upgrade claude-code` (ou `claude-code@latest`) periodicamente, e
> `brew cleanup` de vez em quando para liberar as versões antigas.

Verifique:

```bash
claude --version
# esperado: 2.1.231 (Claude Code) ou superior
```

**Se o macOS bloquear o binário** ("não foi possível verificar o
desenvolvedor"), o binário é assinado pela "Anthropic PBC" e notarizado — o
bloqueio costuma vir de download por outro caminho. Confirme com:

```bash
codesign --verify --verbose $(which claude)
```

### 1.5 Windows

Decida primeiro **onde seu projeto mora**:

| Opção | Exige | Sandbox? | Quando usar |
|---|---|---|---|
| **Windows nativo** | nada (Git for Windows é opcional) | ❌ não | projetos e ferramentas Windows |
| **WSL 2** | WSL 2 habilitado | ✅ sim | toolchain Linux, ou você quer execução em sandbox |
| WSL 1 | WSL 1 | ❌ não | só se WSL 2 for indisponível |

> **Recomendação:** WSL 2, se seus projetos são Node/Python/Go. Windows
> nativo, se são .NET/MSVC. Não instale nos dois — duas instalações do Claude
> Code na mesma máquina causam confusão de PATH difícil de diagnosticar.

**Windows nativo, PowerShell:**

```powershell
irm https://claude.ai/install.ps1 | iex
```

**Windows nativo, CMD:**

```batch
curl -fsSL https://claude.ai/install.cmd -o install.cmd && install.cmd && del install.cmd
```

> Como saber em qual você está: o prompt mostra `PS C:\...` no PowerShell e
> `C:\...` (sem `PS`) no CMD. Erro `The token '&&' is not a valid statement
> separator` = você está no PowerShell e rodou o comando do CMD. Erro `'irm'
> is not recognized` = o contrário.

**Via WinGet:**

```powershell
winget install Anthropic.ClaudeCode
```
Não atualiza sozinho: `winget upgrade Anthropic.ClaudeCode` de tempos em
tempos. A atualização pode falhar com o Claude Code aberto (o Windows tranca
o executável) — feche antes.

**WSL 2:** abra o terminal da distribuição e siga a [seção 1.2](#12-linux-debianubuntu-e-fedorarhel--instalador-nativo).
Instale **dentro** do WSL, não pelo PowerShell.

**Git for Windows (nativo, opcional mas recomendado):** instale de
[git-scm.com/downloads/win](https://git-scm.com/downloads/win). Ele fornece o
Git Bash, que habilita a ferramenta `Bash` do agente. Sem ele, o Claude Code
usa PowerShell. Se ele não achar o Git Bash:

```json
// ~/.claude/settings.json
{ "env": { "CLAUDE_CODE_GIT_BASH_PATH": "C:\\Program Files\\Git\\bin\\bash.exe" } }
```

### 1.6 npm (qualquer SO, se você já tem Node)

```bash
npm install -g @anthropic-ai/claude-code
```
Requer **Node.js 22+** (a partir da versão 2.1.198 do pacote). Em Node mais
antigo, o npm emite um aviso `EBADENGINE` mas a instalação conclui — o pacote
baixa um binário nativo que não usa o seu Node em tempo de execução.

Atualizar: `npm install -g @anthropic-ai/claude-code@latest`.
**Não** use `npm update -g`: ele respeita o intervalo semver da instalação
original e pode não te levar à versão nova.

> ⚠️ **Nunca `sudo npm install -g`.** O motivo não é etiqueta: o `sudo` cria
> arquivos pertencentes ao root dentro do seu diretório npm global. A partir
> daí, toda instalação seguinte sem sudo falha com `EACCES`, e o
> auto-atualizador do Claude Code para de funcionar silenciosamente. Se o
> `npm install -g` sem sudo der `EACCES`, a correção certa é mudar o prefixo
> do npm — ver [seção 7](#7-permissões).

### 1.7 Verificação de integridade (opcional, mas faça em servidor)

Cada release publica um `manifest.json` com os SHA256 de todos os binários,
assinado com a chave GPG da Anthropic. Verificar a assinatura do manifesto
verifica, por transitividade, todos os binários.

```bash
curl -fsSL https://downloads.claude.ai/keys/claude-code.asc | gpg --import
gpg --fingerprint security@anthropic.com
# esperado: 31DD DE24 DDFA B679 F42D  7BD2 BAA9 29FF 1A7E CACE

REPO=https://downloads.claude.ai/claude-code-releases
VERSION=2.1.231
curl -fsSLO "$REPO/$VERSION/manifest.json"
curl -fsSLO "$REPO/$VERSION/manifest.json.sig"
gpg --verify manifest.json.sig manifest.json
# esperado: Good signature from "Anthropic Claude Code Release Signing <security@anthropic.com>"
```

O aviso `This key is not certified with a trusted signature!` é esperado para
chave recém-importada e não invalida nada — a linha `Good signature` é o que
importa, e a comparação de impressão digital acima é o que autentica a chave.

Assinaturas de manifesto existem a partir da versão `2.1.89`.

---

## 2. Autenticação

```bash
claude
```
Na primeira execução, abre o navegador para login. Escolha:

- **Assinatura Claude** (Pro/Max/Team/Enterprise) → `claude auth login`
- **Console Anthropic** (pagamento por uso via chave de API) →
  `claude auth login --console`
- **SSO corporativo** → `claude auth login --sso`

Verifique:

```bash
claude auth status --text
# esperado: informação de conta e "logged in"; sai com código 0
```

Se a variável `ANTHROPIC_API_KEY` estiver definida, o Claude Code pergunta uma
vez se você quer aprová-la, em vez de abrir o navegador.

**Sem navegador (servidor, SSH):** use `claude setup-token` numa máquina com
navegador para gerar um token de longa duração e leve-o para o servidor. Ele é
impresso na tela e não é salvo — copie na hora.

---

## 3. Ferramentas que o agente usa (instale, não assuma)

O Claude Code funciona sozinho, mas fica cego para o seu projeto sem as
ferramentas dele. Instale o que o seu stack exige.

### 3.1 Git (obrigatório na prática)

```bash
# Debian/Ubuntu
sudo apt install git
# Fedora/RHEL
sudo dnf install git
# macOS
brew install git       # ou: xcode-select --install
# Windows
# https://git-scm.com/downloads/win
```

```bash
git --version
# esperado: git version 2.34.1 ou superior
```

Sem Git, você perde `git diff` para revisar, checkpoints úteis, e os comandos
`/diff`, `/code-review`, `--worktree` e `/batch`.

### 3.2 ripgrep

Vem embutido no binário do Claude Code. Você só precisa instalá-lo à parte
em musl (Alpine) — ver [1.3](#13-linux--repositórios-assinados-apt--dnf--apk).
Se a busca falhar com erro estranho, teste:

```bash
rg --version   # se existir no sistema
```
e defina `USE_BUILTIN_RIPGREP=0` no `settings.json`.

### 3.3 Node.js (para servidores MCP em JS/TS e para o Agent SDK em TS)

Não instale Node pelo `apt`: a versão é antiga e a instalação global exige
sudo. Use um **gerenciador de versões**.

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
```
Instala o `nvm` em `~/.nvm` e acrescenta as linhas de inicialização ao seu
arquivo de perfil.

```bash
exec $SHELL -l          # recarrega o shell — sem isso, `nvm` não existe ainda
nvm install --lts
nvm alias default lts/*
```

```bash
node --version
# esperado: v22.x ou superior (testado com v24.18.0)
npm --version
# esperado: 10.x ou superior
```

**Se `nvm: command not found` depois do `exec $SHELL -l`:** o instalador
escreveu num arquivo de perfil que o seu shell não lê. Ver
[seção 6](#6-path-e-variáveis-de-ambiente).

Alternativas equivalentes: [`fnm`](https://github.com/Schniz/fnm) (mais
rápido), [`mise`](https://mise.jdx.dev/) (gerencia Node + Python + Go juntos).
No Windows nativo, use [`nvm-windows`](https://github.com/coreybutler/nvm-windows)
ou instale pelo site oficial.

### 3.4 Python + `uv` (para servidores MCP em Python, para o projeto-modelo e para o Agent SDK em Python)

O Python 3 do sistema serve para o projeto-modelo deste curso (que não tem
dependências). Para qualquer coisa com dependências, use o `uv` — ele
substitui `pip`, `venv` e `pyenv` de uma vez.

```bash
python3 --version
# esperado: Python 3.10 ou superior (testado com 3.10.12)
```

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```
Instala o `uv` em `~/.local/bin`.

```bash
exec $SHELL -l
uv --version
# esperado: uv 0.9.x ou superior
```

Windows PowerShell:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

> ⚠️ **Nunca `sudo pip install`.** Você mistura pacotes seus com pacotes do
> sistema operacional; no Ubuntu 23.04+ e Fedora recentes o próprio pip
> recusa, com `error: externally-managed-environment`. A correção é `uv` ou
> um ambiente virtual — nunca `--break-system-packages`.

Usar depois:

```bash
uv venv                 # cria .venv na pasta atual
uv pip install anthropic mcp
```

### 3.5 `gh` (GitHub CLI — opcional)

Necessário para `/install-github-app`, `/autofix-pr` e para o agente abrir
pull requests.

```bash
# Debian/Ubuntu
sudo apt install gh
# macOS
brew install gh
# Windows
winget install GitHub.cli
```

```bash
gh auth login
gh auth status
# esperado: "Logged in to github.com as <seu-usuario>"
```

### 3.6 Docker (opcional, para sandbox)

Recomendado se você pretende dar autonomia alta ao agente. Ver o assunto
[`docker`](../docker/00-MAPA.md) desta pasta para a instalação completa.

```bash
docker --version
# esperado: Docker version 27.x ou superior
```

### 3.7 Editor e integração de IDE (opcional)

- **VS Code / Cursor / Windsurf:** instale a extensão "Claude Code" pelo
  marketplace, ou rode `claude` no terminal integrado e digite `/ide`.
- **JetBrains (IntelliJ, PyCharm, WebStorm…):** plugin "Claude Code" no
  marketplace de plugins.

```
/ide
```
dentro de uma sessão mostra o estado da conexão.

---

## 4. Configuração inicial do projeto

Dentro da pasta do seu projeto:

```bash
cd ~/meu-projeto
claude
```

Na sessão:

```
/init
```
Gera um `CLAUDE.md` inicial lendo o repositório. **Revise e corte** — o
`/init` costuma escrever coisas que o agente descobriria sozinho, e tudo que
está no `CLAUDE.md` ocupa contexto em **toda** sessão.

```
/doctor
```
Roda um diagnóstico completo: instalação duplicada, PATH, arquivos de
configuração inválidos, hooks lentos, skills e servidores MCP não usados,
`CLAUDE.md` inchado. Ele **reporta antes de mudar** e pede confirmação.

```
/permissions
```
Ajusta o que ele pode fazer sem perguntar. Comece permitindo o que é
somente-leitura no seu projeto (`Bash(npm test)`, `Bash(git status)`).

---

## 5. Convivência de versões

**Duas versões do Claude Code na mesma máquina** é a causa mais comum de
"editei a configuração e nada mudou". Detecte:

```bash
which -a claude
# esperado: UM caminho. Se aparecerem dois, você tem instalação duplicada.
claude doctor
# lista instalações conflitantes e o que remover
```

Causas frequentes: instalou por npm e depois pelo instalador nativo; ou tem
uma no WSL e outra no Windows nativo (essas convivem bem, desde que você saiba
em qual está).

**Fixar uma versão específica:**

```bash
curl -fsSL https://claude.ai/install.sh | bash -s 2.1.231
```

**Fixar o canal e um piso de versão**, em `~/.claude/settings.json`:

```json
{
  "autoUpdatesChannel": "stable",
  "minimumVersion": "2.1.200"
}
```
`stable` fica ≈ uma semana atrás do `latest` e pula releases com regressão
grave. `minimumVersion` impede que a troca de canal te rebaixe.

**Reprodutibilidade em equipe:** versione `.claude/settings.json` e
`.mcp.json` no repositório; deixe `.claude/settings.local.json` no
`.gitignore` (é onde ficam as preferências pessoais). Para Node e Python, use
`.nvmrc` / `.tool-versions` e o lockfile do gerenciador.

---

## 6. PATH e variáveis de ambiente

O sintoma é sempre o mesmo: você instalou e `command not found`.

**Passo 1 — o binário existe?**

```bash
ls -l ~/.local/bin/claude
# esperado: um link simbólico para ~/.local/share/claude/versions/<versão>
```

Existe? Então é PATH. Não existe? A instalação falhou; volte ao passo 1.

**Passo 2 — o PATH inclui a pasta?**

```bash
echo "$PATH" | tr ':' '\n' | grep -n '\.local/bin'
# esperado: uma linha. Sem saída = a pasta não está no PATH.
```

**Passo 3 — corrija no arquivo certo.** Este é o detalhe que faz a maioria
perder uma hora:

| Shell | Qual arquivo editar | Como saber que é o seu shell |
|---|---|---|
| bash | `~/.bashrc` (Linux) · `~/.bash_profile` (macOS) | `echo $SHELL` → `/bin/bash` |
| zsh | `~/.zshrc` | `echo $SHELL` → `/bin/zsh` (padrão no macOS desde Catalina) |
| fish | `~/.config/fish/config.fish` | `echo $SHELL` → `/usr/bin/fish` |
| PowerShell | `$PROFILE` (rode `notepad $PROFILE`) | prompt `PS C:\>` |

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
```

**Passo 4 — recarregue.**

```bash
exec $SHELL -l
claude --version
```

> **"Editei o `.bashrc` e não pegou."** Três causas, nesta ordem de
> frequência: (a) você não reabriu o terminal — o arquivo de perfil é lido
> **uma vez**, na abertura; (b) você editou o `.bashrc` mas seu terminal abre
> como *login shell* e lê o `.bash_profile`; (c) você está no zsh e editou o
> `.bashrc`. Diagnostique com `echo $SHELL`.

**Variáveis de ambiente úteis:**

| Variável | Para quê |
|---|---|
| `ANTHROPIC_API_KEY` | autenticação por chave de API |
| `CLAUDE_CODE_GIT_BASH_PATH` | caminho do Git Bash no Windows nativo |
| `USE_BUILTIN_RIPGREP=0` | usar o ripgrep do sistema (musl/Alpine) |
| `DISABLE_AUTOUPDATER=1` | desligar a atualização automática em segundo plano |
| `HTTPS_PROXY`, `NO_PROXY` | rede corporativa ([seção 8](#8-rede-corporativa)) |

Prefira defini-las no bloco `env` do `settings.json` a exportá-las no shell:
ficam versionadas com o projeto e não vazam para outros processos.

```json
{ "env": { "USE_BUILTIN_RIPGREP": "0" } }
```

---

## 7. Permissões

**Regra geral: nada neste curso precisa de `sudo`, exceto instalar pacotes do
sistema (`apt`, `dnf`, `apk`, `docker`).**

### `EACCES: permission denied` no npm global

Sintoma:

```
npm ERR! code EACCES
npm ERR! syscall mkdir
npm ERR! path /usr/lib/node_modules/@anthropic-ai
```

Causa: o diretório global do npm pertence ao root. **Não resolva com sudo** —
isso cria arquivos root dentro do seu diretório de módulos e quebra as
instalações seguintes e o auto-atualizador.

Correção certa:

```bash
mkdir -p ~/.npm-global
npm config set prefix ~/.npm-global
echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.bashrc
exec $SHELL -l
npm install -g @anthropic-ai/claude-code
```

Melhor ainda: use o instalador nativo e não dependa do npm.

### `error: externally-managed-environment` no pip

Ubuntu 23.04+, Debian 12+, Fedora recentes. O Python do sistema é gerenciado
pelo `apt`/`dnf`, e o pip se recusa a mexer nele. **Não use
`--break-system-packages`** — o nome da flag é literal.

Correção: `uv` ([3.4](#34-python--uv-para-servidores-mcp-em-python-para-o-projeto-modelo-e-para-o-agent-sdk-em-python)),
ou `python3 -m venv .venv && source .venv/bin/activate`.

### Permissões *do agente* (assunto diferente)

Não confunda permissão de sistema de arquivos com o sistema de permissões do
Claude Code — o que ele pode fazer sem te perguntar. Isso está em
[17-hooks-permissoes-seguranca.md](17-hooks-permissoes-seguranca.md).

---

## 8. Rede corporativa

### Proxy

```bash
export HTTPS_PROXY=http://proxy.empresa.com:8080
export HTTP_PROXY=http://proxy.empresa.com:8080
export NO_PROXY=localhost,127.0.0.1,.empresa.com
```

Teste antes de instalar:

```bash
curl -sS -o /dev/null -w '%{http_code}\n' https://api.anthropic.com/
# esperado: 401 ou 404 (chegou lá). 000 ou timeout = o proxy está bloqueando.
```

### Certificado interno (TLS inspecionado)

Sintoma: `unable to get local issuer certificate` ou `SELF_SIGNED_CERT_IN_CHAIN`.

```bash
export NODE_EXTRA_CA_CERTS=/caminho/para/ca-empresa.pem
```

**Não** desligue a verificação de TLS (`NODE_TLS_REJECT_UNAUTHORIZED=0`) como
"solução": você passa a aceitar qualquer certificado, inclusive de um ataque
real.

### Domínios que precisam estar liberados

| Domínio | Para quê |
|---|---|
| `api.anthropic.com` | as chamadas do modelo — sem isso, nada funciona |
| `claude.ai` | login, instalador, atualizações |
| `downloads.claude.ai` | binários e repositórios de pacote |
| `statsig.anthropic.com` | feature flags (opcional; desligue com `DISABLE_TELEMETRY=1`) |

### Registry npm espelhado

```bash
npm config set registry https://nexus.empresa.com/repository/npm-group/
```

---

## 9. Atualizar e voltar atrás

```bash
claude update
# esperado: "Successfully updated from 2.1.230 to version 2.1.231"
#       ou: "Claude Code is up to date (2.1.231)"
```

Instalações via Homebrew, WinGet, apt, dnf e apk relatam
`Claude is up to date!` e exigem o comando do gerenciador correspondente.

**Voltar para uma versão anterior:**

```bash
claude install 2.1.220
claude --version   # confirma
```

**Desligar a atualização automática:**

```json
// ~/.claude/settings.json
{ "env": { "DISABLE_AUTOUPDATER": "1" } }
```
Isso só desliga a verificação em segundo plano; `claude update` continua
funcionando. Para bloquear todos os caminhos, use `DISABLE_UPDATES`.

---

## 10. Desinstalar por completo

### O binário

```bash
# instalação nativa — macOS, Linux, WSL
rm -f ~/.local/bin/claude
rm -rf ~/.local/share/claude
```

```powershell
# instalação nativa — Windows
Remove-Item -Path "$env:USERPROFILE\.local\bin\claude.exe" -Force
Remove-Item -Path "$env:USERPROFILE\.local\share\claude" -Recurse -Force
```

```bash
brew uninstall --cask claude-code          # ou claude-code@latest
winget uninstall Anthropic.ClaudeCode
sudo apt remove claude-code && sudo rm /etc/apt/sources.list.d/claude-code.list /etc/apt/keyrings/claude-code.asc
sudo dnf remove claude-code && sudo rm /etc/yum.repos.d/claude-code.repo
apk del claude-code
npm uninstall -g @anthropic-ai/claude-code
```

### O que fica para trás (quase todo tutorial esquece disto)

```bash
rm -rf ~/.claude        # configurações, sessões, histórico, caches, plugins
rm -f  ~/.claude.json   # estado por projeto
```

E dentro de **cada projeto** em que você usou:

```bash
rm -rf .claude
rm -f .mcp.json
```

> ⚠️ `~/.claude/projects/` contém o transcrito completo de todas as suas
> sessões, em texto claro. Se a máquina é compartilhada ou vai ser
> descartada, apagar isso é parte do procedimento, não opcional.
>
> Para limpar só um projeto, sem apagar o resto:
> `claude project purge ~/caminho/do/projeto --dry-run` (tire o `--dry-run`
> depois de conferir a lista).

> A extensão do VS Code, o plugin do JetBrains e o app de desktop também
> escrevem em `~/.claude/`. Se algum deles continuar instalado, a pasta é
> recriada. Desinstale-os antes.

---

## 11. Solução de problemas — mensagens literais

| Mensagem | Causa provável | Correção |
|---|---|---|
| `command not found: claude` | `~/.local/bin` fora do PATH, ou instalação falhou | [Seção 6](#6-path-e-variáveis-de-ambiente): confira `ls -l ~/.local/bin/claude`, depois o PATH, depois **reabra o terminal** |
| `EACCES: permission denied` (npm) | diretório npm global pertence ao root | Mude o prefixo do npm ([7](#7-permissões)). Nunca `sudo npm -g` |
| `error: externally-managed-environment` | pip no Python do sistema | Use `uv` ou um venv ([3.4](#34-python--uv-para-servidores-mcp-em-python-para-o-projeto-modelo-e-para-o-agent-sdk-em-python)) |
| `syntax error near unexpected token '<'` no instalador | o curl baixou uma página HTML de erro (proxy/firewall) | [Seção 8](#8-rede-corporativa); ou baixe o `install.sh` manualmente e inspecione |
| `unable to get local issuer certificate` | TLS inspecionado pela empresa | `NODE_EXTRA_CA_CERTS=/caminho/ca.pem` ([8](#8-rede-corporativa)) |
| `Invalid API key · Please run /login` | credencial ausente, expirada ou conflitante | `claude auth status`; se houver `ANTHROPIC_API_KEY` exportada **e** login por navegador, remova uma das duas — a chave tem precedência e ofusca o perfil |
| `NO_PUBKEY BAA929FF1A7ECACE` no `apt update` | a chave não foi baixada para `/etc/apt/keyrings/` | Refaça o download da chave em [1.3](#13-linux--repositórios-assinados-apt--dnf--apk) e confira a impressão digital |
| `The token '&&' is not a valid statement separator` | você rodou o comando do CMD no PowerShell | Use `irm ... \| iex` |
| `'irm' is not recognized...` | você rodou o comando do PowerShell no CMD | Use a linha com `curl ... install.cmd` |
| MCP aparece como `failed` no `/mcp` | comando do servidor não encontrado, ou erro na inicialização | `claude --debug=mcp` e leia o erro; quase sempre é caminho absoluto de `python3`/`node` |
| `Credit balance is too low` | conta de API sem créditos | Adicione créditos no Console, ou use uma assinatura Pro/Max |
| a busca de arquivos não retorna nada | ripgrep embutido incompatível (musl) | `USE_BUILTIN_RIPGREP=0` + `apk add ripgrep` |

Não achou aqui? `claude doctor` no terminal, `/doctor` dentro da sessão, e
`claude --debug` para o log completo.

---

## 12. Checklist "ambiente pronto"

Uma linha por vez. Todas precisam responder.

```bash
claude --version            # 2.1.231 ou superior
claude auth status --text   # logado
claude doctor               # sem erros críticos
git --version               # 2.34+
node --version              # v22+   (só se for usar MCP/SDK em JS)
python3 --version           # 3.10+  (só se for usar MCP/SDK em Python)
uv --version                # 0.9+   (idem)
gh auth status              # opcional
docker --version            # opcional
which -a claude             # UM caminho só
```

E dentro de um projeto de verdade:

```bash
cd ~/meu-projeto && claude
```
```
/doctor
/context
/exit
```

`/context` deve mostrar um contexto quase vazio. Se já estiver 30% cheio numa
sessão nova, seu `CLAUDE.md` está inchado — leia
[14-contexto-memoria-compactacao.md](14-contexto-memoria-compactacao.md).

Ambiente pronto? Siga para [04-como-comecar.md](04-como-comecar.md).

---

## Autoteste

1. Por que o instalador nativo é preferível ao npm, mesmo para quem já tem Node?
2. Você rodou `sudo npm install -g @anthropic-ai/claude-code` e funcionou.
   Que problema você acabou de criar, e como se corrige?
3. Editou o `~/.bashrc`, `claude` continua não encontrado. Liste três causas,
   da mais provável para a menos.
4. Qual a diferença entre os canais `stable` e `latest`, e para que serve o
   `minimumVersion`?
5. Que impressão digital GPG você deve conferir ao usar o repositório apt, e
   o que fazer se não bater?
6. `which -a claude` devolveu dois caminhos. Por que isso é um problema, e
   qual comando ajuda a diagnosticar?
7. Desinstalou o Claude Code e a pasta `~/.claude` voltou a aparecer. Por quê?
8. Que arquivo do seu diretório pessoal contém o transcrito das suas sessões,
   e por que isso importa numa máquina compartilhada?

---

**Fontes consultadas em 13/08/2026:** documentação oficial
[Advanced setup](https://code.claude.com/docs/en/setup),
[Troubleshoot installation](https://code.claude.com/docs/en/troubleshoot-install),
[Authentication](https://code.claude.com/docs/en/authentication),
[Network configuration](https://code.claude.com/docs/en/network-config);
`claude --help` e `claude doctor` da versão 2.1.231 instalada localmente;
[nvm](https://github.com/nvm-sh/nvm), [uv](https://docs.astral.sh/uv/).
