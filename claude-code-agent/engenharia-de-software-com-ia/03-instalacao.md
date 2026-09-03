# 3 · Manual de instalação — o ambiente completo

**Nível:** iniciante · **Escrito em:** 20/08/2026
**Ambiente de verificação:** Ubuntu 22.04.5 LTS · Node v24.18.0 · npm 12.0.1 ·
Python 3.10.12 · Git 2.34.1 · Docker 29.7.2 · ripgrep 14.1.1 ·
Claude Code 2.1.237

> **Leia isto antes de instalar qualquer coisa.** Este arquivo é um manual de
> campo. Ele parte do princípio de que você não sabe nada, não quer improvisar e
> não quer consultar outra fonte. Cada passo tem: o comando, o que ele faz, como
> verificar, e o que fazer se a verificação falhar.
>
> **Ele também parte do princípio de que você não vai instalar tudo.** Instale o
> Bloco 1 (obrigatório) + **uma** ferramenta do Bloco 4. O resto é conforme a
> necessidade.

---

## 0 · Comece hoje, sem instalar nada

Se você quer só começar, pule tudo abaixo e use uma destas três opções. Todas
funcionam no navegador e não pedem cartão de crédito.

| Opção | O que dá | Limite gratuito | Link |
|---|---|---|---|
| **GitHub Codespaces** | Máquina Linux completa + VS Code no navegador, com Copilot já ligado | 60 h/mês e 15 GB de armazenamento na conta pessoal gratuita | [github.com/codespaces](https://github.com/codespaces) |
| **Google Cloud Shell** | Máquina Linux com editor, 5 GB persistentes | 50 h/semana | [shell.cloud.google.com](https://shell.cloud.google.com) |
| **Claude na web** | Conversa e código, sem agente no seu repositório | Limite diário baixo | [claude.ai](https://claude.ai) |

**Recomendação:** Codespaces. Você abre qualquer repositório do GitHub, aperta
`.` no teclado ou clica em *Code → Codespaces → Create*, e em ~90 segundos tem
um ambiente Linux real com Node, Python, Git e Docker já instalados.

Dentro do Codespaces, para ter um agente de terminal, rode:

```bash
npm install -g @github/copilot
```

E siga direto para o [04-como-comecar](04-como-comecar.md). Volte para este
arquivo quando quiser o ambiente local.

> **Por que essa seção vem primeiro:** a maior causa de desistência em qualquer
> tecnologia é passar o primeiro dia inteiro instalando coisas e não ver
> resultado nenhum. Ver o resultado primeiro e instalar depois inverte isso.

---

## O que compõe o ambiente

Não existe "instalar a IA". Existe um conjunto de peças, e cada uma tem seção
própria aqui:

```
┌─────────────────────────────────────────────────────────────┐
│ BLOCO 1 — BASE (obrigatório)                                │
│   terminal · Git · editor (VS Code) · ripgrep               │
├─────────────────────────────────────────────────────────────┤
│ BLOCO 2 — RUNTIME (pelo menos um)                           │
│   Node.js (via gerenciador de versão)                       │
│   Python (via gerenciador de versão)                        │
├─────────────────────────────────────────────────────────────┤
│ BLOCO 3 — ISOLAMENTO (recomendado)                          │
│   Docker / Podman · git worktree                            │
├─────────────────────────────────────────────────────────────┤
│ BLOCO 4 — AGENTE (escolha UM para começar)                  │
│   Claude Code · Codex CLI · GitHub Copilot CLI ·            │
│   Gemini CLI · Aider · Cursor · Windsurf                    │
├─────────────────────────────────────────────────────────────┤
│ BLOCO 5 — PORTÃO DE VERIFICAÇÃO (o que ninguém instala,     │
│           e é o que separa L2 de L3)                        │
│   gitleaks · pre-commit · linter · formatador · testes      │
├─────────────────────────────────────────────────────────────┤
│ BLOCO 6 — OPCIONAL                                          │
│   uv · mise · GitHub CLI · servidores MCP · Spec Kit        │
└─────────────────────────────────────────────────────────────┘
```

**O Bloco 5 é o que este curso considera não-negociável.** Instalar um agente
sem instalar o portão é comprar a serra sem comprar o gabarito.

---

## BLOCO 1 · Base

### 1.1 Terminal

#### Linux (Debian/Ubuntu, Fedora/RHEL)

Já tem. Abra com `Ctrl+Alt+T`.

#### macOS

Já tem: **Terminal.app** (`Cmd+Espaço` → "Terminal"). Se quiser algo melhor,
**iTerm2** ou **Ghostty** — opcional, não muda nada funcional.

#### Windows

Use o **Windows Terminal** (não o `cmd.exe` antigo). No Windows 11 já vem; no
Windows 10 instale:

```powershell
winget install Microsoft.WindowsTerminal
```

*O que faz:* instala o terminal moderno da Microsoft, que suporta abas, cores e
UTF-8 corretamente.

**Verificação:**

```powershell
wt --version
# esperado: uma versão como 1.22.x
```

**Se falhar com `winget não é reconhecido`:** o WinGet vem no Windows 10 1809+
via "Instalador de Aplicativo" da Microsoft Store. Instale por lá e reabra o
terminal.

#### Windows: nativo ou WSL2?

**Recomendação: WSL2.** Motivos concretos, não ideológicos:

- Todo agente executa comandos de shell. Fora do WSL, ele propõe comandos POSIX
  que falham no PowerShell, percebe o erro, tenta de novo — você paga tokens e
  tempo por isso, a cada tarefa.
- Recursos de *sandbox* (isolamento do agente) de várias ferramentas **só
  existem no Linux/WSL2**. No Windows nativo, não há isolamento.
- Praticamente toda documentação e todo `Makefile` do mundo assumem POSIX.

Instalar WSL2:

```powershell
wsl --install -d Ubuntu-24.04
```

*O que faz:* habilita o subsistema Linux, instala o kernel e a distribuição
Ubuntu 24.04. Exige reiniciar.

**Verificação (após reiniciar):**

```powershell
wsl -l -v
# esperado:
#   NAME            STATE           VERSION
# * Ubuntu-24.04    Running         2
```

**Se a coluna VERSION mostrar `1`:** converta com
`wsl --set-version Ubuntu-24.04 2`.

**Se falhar com `Erro 0x80370102`:** a virtualização está desligada na BIOS.
Reinicie, entre na BIOS/UEFI e habilite *Intel VT-x* ou *AMD-V*.

> **Armadilha clássica do WSL:** guarde seus projetos **dentro** do sistema de
> arquivos do Linux (`/home/seu-usuario/`), nunca em `/mnt/c/`. Ler arquivos em
> `/mnt/c/` a partir do WSL é 10 a 20 vezes mais lento, e um agente lê centenas
> de arquivos por tarefa. Já vi gente concluir que "o agente é lento" quando o
> problema era esse.

---

### 1.2 Git

#### Linux — Debian/Ubuntu

```bash
sudo apt update && sudo apt install -y git
```

*O que faz:* atualiza a lista de pacotes e instala o Git.

#### Linux — Fedora/RHEL

```bash
sudo dnf install -y git
```

#### macOS

```bash
xcode-select --install
```

*O que faz:* instala as ferramentas de linha de comando da Apple, que incluem
o Git. Alternativa mais atual: `brew install git` (ver 1.4).

#### Windows nativo

```powershell
winget install Git.Git
```

Mesmo usando WSL, **instale também o Git for Windows** se for rodar algum
agente no Windows nativo: ele fornece o Git Bash, que é o que dá ao agente um
shell POSIX.

**Verificação (todos os sistemas):**

```bash
git --version
# esperado: git version 2.34.1 (ou superior)
```

Versão mínima recomendada: **2.30**. Abaixo disso, `git worktree` e
`git rebase --update-refs` têm limitações que atrapalham fluxo com agentes.

**Configuração obrigatória (senão o primeiro commit falha):**

```bash
git config --global user.name "Seu Nome"
git config --global user.email "seu@email.com"
git config --global init.defaultBranch main
```

**Verificação:**

```bash
git config --global --list | head -5
# esperado: as três linhas acima
```

> Se você quer que os commits feitos com ajuda de agente sejam assinados e
> verificáveis, o assunto está inteiro em
> [commits-assinados](../commits-assinados/00-MAPA.md).

---

### 1.3 ripgrep (`rg`)

Parece detalhe e não é. **Todo agente moderno usa `ripgrep` para procurar no seu
código.** Se ele não achar `rg`, cai para uma busca muito mais lenta e às vezes
falha em repositórios grandes.

| Sistema | Comando |
|---|---|
| Debian/Ubuntu | `sudo apt install -y ripgrep` |
| Fedora/RHEL | `sudo dnf install -y ripgrep` |
| macOS | `brew install ripgrep` |
| Windows | `winget install BurntSushi.ripgrep.MSVC` |
| Alpine | `apk add ripgrep` (repositório *community*) |

**Verificação:**

```bash
rg --version
# esperado: ripgrep 14.1.1 (ou superior)
```

**Se `command not found` no Debian/Ubuntu antigo:** o pacote se chama
`ripgrep` a partir do Debian 11 / Ubuntu 20.04. Em versões anteriores, baixe o
`.deb` das [releases do projeto](https://github.com/BurntSushi/ripgrep/releases).

---

### 1.4 Homebrew (só macOS e Linux)

Gerenciador de pacotes que a maioria das ferramentas de IA usa como caminho
oficial no macOS.

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

*O que faz:* instala o Homebrew em `/opt/homebrew` (Apple Silicon) ou
`/usr/local` (Intel).

**Passo crítico que quase todo mundo esquece — o PATH.** No Apple Silicon, o
instalador **não** configura o PATH sozinho. Ao final ele imprime duas linhas;
execute-as. Se você fechou o terminal antes de ler:

```bash
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"
```

*O que faz:* a primeira linha grava a configuração no arquivo que o zsh lê ao
abrir; a segunda aplica agora, sem precisar reabrir.

**Verificação:**

```bash
brew --version
# esperado: Homebrew 4.x.x
which brew
# esperado (Apple Silicon): /opt/homebrew/bin/brew
# esperado (Intel):         /usr/local/bin/brew
```

**Se `command not found: brew` depois de instalar:** é PATH. Veja a seção
[PATH](#path-e-variáveis-de-ambiente) mais abaixo.

---

### 1.5 Editor — VS Code

Você pode usar qualquer editor. Uso o VS Code aqui porque é o denominador comum
e porque todas as ferramentas do Bloco 4 têm extensão para ele.

| Sistema | Comando |
|---|---|
| Debian/Ubuntu | `sudo snap install code --classic` |
| Fedora/RHEL | `sudo dnf install -y code` (após adicionar o repo da Microsoft) |
| macOS | `brew install --cask visual-studio-code` |
| Windows | `winget install Microsoft.VisualStudioCode` |

**Verificação:**

```bash
code --version
# esperado: três linhas — versão, hash do commit, arquitetura
```

**Se `code` não existir no PATH no macOS:** abra o VS Code, aperte
`Cmd+Shift+P`, digite `shell command` e escolha
*"Shell Command: Install 'code' command in PATH"*.

**Extensões que valem a pena, e por quê:**

```bash
code --install-extension ms-vscode-remote.remote-wsl
code --install-extension eamodio.gitlens
code --install-extension usernamehw.errorlens
```

| Extensão | Por que importa **no contexto de IA** |
|---|---|
| Remote WSL | Edita arquivos do Linux com desempenho nativo |
| GitLens | Mostra "quem escreveu esta linha e quando" — indispensável para revisar código de agente e distinguir o que é seu do que é gerado |
| Error Lens | Põe o erro do linter na própria linha; você enxerga problema em código gerado sem abrir o painel |

---

## BLOCO 2 · Runtime

Você precisa de **Node.js** (a maioria dos agentes de CLI é distribuída via npm)
e, muito provavelmente, de **Python**.

### A regra que evita 80% dos problemas

> **Nunca instale linguagem pelo gerenciador de pacotes do sistema quando
> existir um gerenciador de versões.**

Por quê, até o fim (regra dos cinco porquês):

1. Por que não usar `apt install nodejs`? Porque a versão é antiga e você não
   controla quando muda.
2. Por que isso importa? Porque projetos diferentes exigem versões diferentes, e
   uma versão global só serve a um deles.
3. Por que não instalar duas versões manualmente? Porque as duas disputam o mesmo
   PATH, e qual ganha depende da ordem — um bug que não se reproduz na máquina do
   colega.
4. Por que isso é pior com IA? Porque o agente executa comandos com o PATH que
   você tem. Se o `node` errado responder, ele vai depurar um erro que não existe,
   gastando tokens e chegando a conclusões erradas sobre o **seu** código.
5. Por que não há solução perfeita? Porque o PATH do Unix é uma lista ordenada
   herdada dos anos 1970 (V7 Unix, 1979) e resolve nome por precedência, não por
   requisito declarado. É uma decisão histórica que nunca dá para desfazer sem
   quebrar tudo. Os gerenciadores de versão são a camada que contorna isso.

---

### 2.1 Node.js

Três métodos. Recomendação explícita: **`fnm`** se você só usa Node;
**`mise`** se você usa Node e Python e mais coisas.

#### Método A — `fnm` (recomendado, rápido, multiplataforma)

**Linux e macOS:**

```bash
curl -fsSL https://fnm.vercel.app/install | bash
```

*O que faz:* baixa o binário do `fnm` e adiciona a inicialização ao seu perfil
de shell.

Feche e reabra o terminal. Depois:

```bash
fnm install 22
fnm default 22
```

*O que faz:* instala o Node.js 22 (LTS) e o define como padrão.

**Windows (PowerShell):**

```powershell
winget install Schniz.fnm
```

Depois adicione ao perfil do PowerShell:

```powershell
Add-Content $PROFILE 'fnm env --use-on-cd | Out-String | Invoke-Expression'
```

*O que faz:* faz o `fnm` trocar de versão automaticamente ao entrar numa pasta
que tenha `.node-version` ou `.nvmrc`.

#### Método B — `nvm` (o mais conhecido; só Linux/macOS)

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
```

Feche e reabra o terminal, então:

```bash
nvm install --lts
nvm alias default lts/*
```

`nvm` é um script shell, não um binário. É mais lento ao abrir o terminal
(300–800 ms) e **não funciona no PowerShell**. Prefira `fnm`.

#### Método C — instalador oficial (aceitável se você só tem um projeto)

Baixe em [nodejs.org](https://nodejs.org/en/download). Escolha **LTS**.

#### Método D — gerenciador do sistema (**desaconselhado**)

`apt install nodejs` no Ubuntu 22.04 entrega Node 12. Isso é velho demais para
qualquer agente moderno. Só use se você tiver certeza do que está fazendo.

**Verificação (qualquer método):**

```bash
node --version
# esperado: v22.x.x ou superior (verificado aqui com v24.18.0)

npm --version
# esperado: 10.x ou superior (verificado aqui com 12.0.1)
```

> **Versão mínima em agosto de 2026:** Node **22**. O pacote npm do Claude Code
> exige Node 22+ desde a v2.1.198; o GitHub Copilot CLI exige Node 22+. Node 18
> está fora de suporte. **Evite** Node 23 e 25 (versões ímpares são de
> desenvolvimento, sem LTS).

---

### 2.2 Python

Recomendação: **`uv`**. É o gerenciador que ganhou o mercado entre 2024 e 2026
por ser 10 a 100× mais rápido que `pip` e por resolver instalação de versão de
Python **e** de pacotes com uma ferramenta só.

**Linux e macOS:**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

*O que faz:* instala o binário `uv` em `~/.local/bin` (Linux/macOS) ou
`%USERPROFILE%\.local\bin` (Windows).

Feche e reabra o terminal.

**Verificação:**

```bash
uv --version
# esperado: uv 0.9.x ou superior
```

Instalar uma versão de Python com ele:

```bash
uv python install 3.12
```

**Verificação:**

```bash
uv run python --version
# esperado: Python 3.12.x
```

**Alternativas:** `pyenv` (Linux/macOS, tradicional), `mise`, ou o instalador
oficial do [python.org](https://www.python.org/downloads/). No Windows, o
instalador oficial funciona bem — **marque a caixa "Add python.exe to PATH"**,
que vem desmarcada e é a causa nº 1 de `python não é reconhecido`.

**Versão mínima:** Python **3.10**. Muitas bibliotecas do ecossistema já
exigem 3.10+; várias já exigem 3.11.

---

## BLOCO 3 · Isolamento

Um agente executa comandos na sua máquina, com as suas permissões e as suas
credenciais. Isolamento não é paranoia: é a diferença entre "o agente apagou uma
pasta de teste" e "o agente apagou uma pasta de teste que era o seu `~/Documentos`".

### 3.1 Docker

| Sistema | Comando |
|---|---|
| Debian/Ubuntu | Siga o [roteiro oficial](https://docs.docker.com/engine/install/ubuntu/) — o pacote `docker.io` do apt costuma ser desatualizado |
| Fedora/RHEL | `sudo dnf install -y docker-ce docker-ce-cli containerd.io` após adicionar o repo |
| macOS | `brew install --cask docker` (Docker Desktop) ou `brew install colima docker` (mais leve) |
| Windows | `winget install Docker.DockerDesktop` — habilite a integração com WSL2 nas configurações |

**Verificação:**

```bash
docker --version
# esperado: Docker version 29.x (verificado aqui com 29.7.2)

docker run --rm hello-world
# esperado: "Hello from Docker!" e um parágrafo explicativo
```

**Se `permission denied while trying to connect to the Docker daemon socket`
no Linux:**

```bash
sudo usermod -aG docker $USER
```

*O que faz:* põe seu usuário no grupo `docker`, que tem permissão no socket.
**Você precisa sair da sessão e entrar de novo** (ou `newgrp docker`) para a
mudança valer — o grupo é lido no login.

> **Consciência de segurança:** estar no grupo `docker` é equivalente a ter root,
> porque quem pode montar volumes pode montar `/`. Em máquina compartilhada,
> prefira **Podman** *rootless*: `sudo apt install podman` e depois
> `alias docker=podman`.

O assunto inteiro está em [docker](../docker/00-MAPA.md) desta pasta.

### 3.2 `git worktree` — isolamento sem container

Não precisa instalar nada; vem com o Git. É a técnica mais subestimada para
trabalhar com agentes:

```bash
git worktree add ../meuprojeto-agente -b tarefa/importar-csv
```

*O que faz:* cria uma **segunda cópia de trabalho** do mesmo repositório, em
outra pasta, em outro branch, compartilhando o mesmo `.git`.

Por que importa: você solta o agente em `../meuprojeto-agente` e continua
trabalhando normalmente em `meuprojeto/`. Sem conflito, sem `stash`, sem
esperar. E se der errado:

```bash
git worktree remove ../meuprojeto-agente --force
```

**Verificação:**

```bash
git worktree list
# esperado: duas linhas, uma por worktree, com o branch de cada
```

---

## BLOCO 4 · O agente

**Escolha um.** Instalar cinco no primeiro dia é a forma mais eficiente de não
aprender nenhum. A comparação honesta está no
[80-custos-e-licencas](80-custos-e-licencas.md); aqui é só instalação.

Guia rápido de escolha:

| Se você… | Comece por |
|---|---|
| Não quer gastar nada e já tem GitHub | **GitHub Copilot CLI** (ou Copilot no VS Code) |
| Quer o agente de terminal mais capaz e vai pagar por isso | **Claude Code** |
| Já paga ChatGPT Plus/Pro | **Codex CLI** |
| Quer camada gratuita generosa e código aberto | **Gemini CLI** |
| Quer um IDE em vez de terminal | **Cursor** |
| Quer código aberto, controle total, e escolher o modelo | **Aider** |

---

### 4.1 Claude Code

**Testado em:** 2.1.237, em 20/08/2026, Ubuntu 22.04.5.

**Requisitos:** macOS 13+, Windows 10 1809+, Ubuntu 20.04+, Debian 10+ ou
Alpine 3.19+; 4 GB+ de RAM; conexão com a internet. **Exige plano pago**
(Pro, Max, Team, Enterprise ou conta de Console com API) — o plano gratuito do
Claude.ai **não** inclui o Claude Code.

#### Instalador nativo (recomendado — não precisa de Node)

**macOS, Linux, WSL:**

```bash
curl -fsSL https://claude.ai/install.sh | bash
```

**Windows PowerShell:**

```powershell
irm https://claude.ai/install.ps1 | iex
```

**Windows CMD:**

```batch
curl -fsSL https://claude.ai/install.cmd -o install.cmd && install.cmd && del install.cmd
```

#### Homebrew (macOS/Linux)

```bash
brew install --cask claude-code
```

Há duas *casks*: `claude-code` segue o canal estável (cerca de uma semana de
atraso, pulando releases com regressão grave) e `claude-code@latest` segue o
canal mais novo. Instalações via Homebrew **não** se atualizam sozinhas:
`brew upgrade claude-code`.

#### WinGet (Windows)

```powershell
winget install Anthropic.ClaudeCode
```

#### apt / dnf / apk (Linux, repositórios assinados)

Debian/Ubuntu:

```bash
sudo apt install curl gnupg
sudo install -d -m 0755 /etc/apt/keyrings
sudo curl -fsSL https://downloads.claude.ai/keys/claude-code.asc \
  -o /etc/apt/keyrings/claude-code.asc
gpg --show-keys /etc/apt/keyrings/claude-code.asc
```

*O que faz:* instala as ferramentas de download e assinatura, cria o diretório de
chaves, baixa a chave pública e mostra a impressão digital.

**Verificação obrigatória:** a impressão digital precisa ser exatamente

```
31DDDE24DDFAB679F42D7BD2BAA929FF1A7ECACE
```

Se não for, **pare**: você baixou outra coisa. Confirme que a rede alcança
`downloads.claude.ai` e refaça.

```bash
echo "deb [signed-by=/etc/apt/keyrings/claude-code.asc] https://downloads.claude.ai/claude-code/apt/stable stable main" \
  | sudo tee /etc/apt/sources.list.d/claude-code.list
sudo apt update
sudo apt install claude-code
```

#### npm

```bash
npm install -g @anthropic-ai/claude-code
```

Exige **Node 22+** desde a v2.1.198. O pacote npm baixa o mesmo binário nativo;
o `claude` instalado não usa Node em tempo de execução.

> **Nunca use `sudo npm install -g`.** Explicação na seção
> [Permissões](#permissões-e-por-que-sudo-npm--g-é-um-problema).

**Verificação:**

```bash
claude --version
# esperado: 2.1.237 (Claude Code) — ou superior
```

```bash
claude doctor
# esperado: diagnóstico read-only da instalação e das configurações,
#           sem iniciar sessão
```

**Autenticação:** rode `claude` e siga o navegador. Se a variável
`ANTHROPIC_API_KEY` estiver definida, ele pergunta uma vez se você quer usá-la
em vez de abrir o navegador.

**Desinstalar por completo:**

```bash
rm -f ~/.local/bin/claude
rm -rf ~/.local/share/claude
rm -rf ~/.claude
rm -f ~/.claude.json
# no projeto:
rm -rf .claude .mcp.json
```

> O curso dedicado está em [claude-code](../claude-code/00-MAPA.md) desta pasta.

---

### 4.2 OpenAI Codex CLI

**macOS/Linux:**

```bash
curl -fsSL https://chatgpt.com/codex/install.sh | sh
```

**Windows PowerShell:**

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://chatgpt.com/codex/install.ps1 | iex"
```

**Via gerenciador de pacotes:**

```bash
npm install -g @openai/codex
```

```bash
brew install --cask codex
```

**Verificação e autenticação:**

```bash
codex
# esperado: a interface abre e oferece "Sign in with ChatGPT"
```

Funciona com ChatGPT Plus, Pro, Business, Edu ou Enterprise. Também aceita
chave de API.

**Desinstalar:** `npm uninstall -g @openai/codex` ou
`brew uninstall --cask codex`, e remova `~/.codex`.

---

### 4.3 GitHub Copilot CLI

**Requisitos:** assinatura ativa do Copilot (a camada **Free** serve para
começar); Node 22+ se instalar por npm; PowerShell 6+ no Windows.

```bash
npm install -g @github/copilot
```

```powershell
winget install GitHub.Copilot
```

```bash
brew install --cask copilot-cli
```

```bash
curl -fsSL https://gh.io/copilot-install | bash
```

**Autenticação:** rode `copilot` e use `/login`. Alternativa para automação:
crie um *fine-grained personal access token* com a permissão *Copilot Requests*
e exporte-o:

```bash
export COPILOT_GITHUB_TOKEN="ghp_..."
```

> **Cuidado:** essa variável é uma credencial. Não a escreva em `.bashrc`
> versionado nem em `Dockerfile`. Veja
> [variaveis-de-ambiente-e-segredos](../variaveis-de-ambiente-e-segredos/00-MAPA.md).

**Verificação:**

```bash
copilot --version
# esperado: número de versão
```

---

### 4.4 Gemini CLI

Código aberto, licença Apache 2.0, camada gratuita generosa.

```bash
npm install -g @google/gemini-cli
```

```bash
brew install gemini-cli
```

Para experimentar sem instalar:

```bash
npx @google/gemini-cli
```

**Verificação:**

```bash
gemini --version
```

Autenticação: rode `gemini` e faça login com a conta Google.

---

### 4.5 Aider (código aberto, escolha o modelo que quiser)

```bash
uv tool install --force --python python3.12 --with pip aider-chat@latest
```

*O que faz:* instala o Aider num ambiente isolado gerenciado pelo `uv`, sem
poluir o Python do sistema.

Alternativa, se você não usa `uv`:

```bash
python3 -m pip install --user aider-install && aider-install
```

**Verificação:**

```bash
aider --version
```

Configuração da chave (exemplo com Anthropic):

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
aider --model sonnet
```

> Aider é a melhor porta de entrada para entender **o que um agente realmente
> faz**, porque ele é pequeno, o código é legível, e ele mostra o *diff* antes de
> aplicar. Vale instalar mesmo que não vire sua ferramenta principal.

---

### 4.6 Cursor (IDE)

Baixe em [cursor.com](https://cursor.com/download). É um *fork* do VS Code: as
suas extensões, temas e atalhos são importados na primeira execução.

```bash
brew install --cask cursor
```

```powershell
winget install Anysphere.Cursor
```

**Verificação:** abra, faça login, aperte `Ctrl+I` (ou `Cmd+I`) e peça algo.

### 4.7 Windsurf (IDE)

Baixe em [windsurf.com](https://windsurf.com/download). Mesma ideia do Cursor.

---

## BLOCO 5 · O portão de verificação

Este bloco é o que separa quem usa IA de quem **sabe** usar IA. Nenhum tutorial
o inclui e é o único que ainda vai importar daqui a cinco anos.

### 5.1 gitleaks — impede que segredo vaze no commit

Agentes leem `.env`, leem logs, e ocasionalmente colam uma chave num arquivo de
teste. Isso não é hipótese; é rotina.

| Sistema | Comando |
|---|---|
| macOS/Linux | `brew install gitleaks` |
| Debian/Ubuntu | baixe o binário das [releases](https://github.com/gitleaks/gitleaks/releases) e ponha em `~/.local/bin` |
| Windows | `winget install Gitleaks.Gitleaks` |
| Qualquer um | `docker run --rm -v "$PWD:/path" zricethezav/gitleaks:latest detect --source="/path"` |

**Verificação:**

```bash
gitleaks version
# esperado: 8.x.x
```

Rodar no repositório:

```bash
gitleaks detect --source . --no-banner
# esperado quando está limpo: "no leaks found"
```

### 5.2 pre-commit — o portão que roda sozinho

```bash
uv tool install pre-commit
```

ou

```bash
python3 -m pip install --user pre-commit
```

Crie `.pre-commit-config.yaml` na raiz do projeto:

```yaml
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.30.0
    hooks:
      - id: gitleaks
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v6.0.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-merge-conflict
      - id: check-added-large-files
        args: ['--maxkb=500']
```

Instale o gancho no repositório:

```bash
pre-commit install
```

*O que faz:* escreve um script em `.git/hooks/pre-commit` que roda essas
verificações a cada `git commit`, bloqueando o commit se alguma falhar.

**Verificação:**

```bash
pre-commit run --all-files
# esperado: uma linha por hook, com "Passed" ou "Failed"
```

> **Por que `check-added-large-files` está aqui:** agentes ocasionalmente commitam
> arquivos que não deveriam — `node_modules`, dumps, artefatos de build, um
> `.log` de 40 MB. Um limite de 500 KB pega isso antes de virar história do Git,
> que é praticamente impossível de limpar depois.

### 5.3 Linter e formatador

O que instalar depende da linguagem. O ponto é: **instale**. O linter é o
revisor mais barato que existe e ele revisa código de agente exatamente como
revisa o seu.

| Linguagem | Ferramenta | Instalação |
|---|---|---|
| Python | `ruff` (linter + formatador, muito rápido) | `uv tool install ruff` |
| JavaScript/TypeScript | `biome` ou `eslint` + `prettier` | `npm i -D @biomejs/biome` |
| Go | `golangci-lint` | `brew install golangci-lint` |
| Rust | `clippy` | vem com `rustup` |

**Verificação (exemplo com ruff):**

```bash
ruff --version
# esperado: ruff 0.14.x ou superior
ruff check .
# esperado: "All checks passed!" ou a lista de problemas
```

---

## BLOCO 6 · Opcional, mas útil

### 6.1 GitHub CLI (`gh`)

Deixa você — e o agente — abrir PR, ler *issue* e ver o status do CI sem sair do
terminal.

| Sistema | Comando |
|---|---|
| Debian/Ubuntu | `sudo apt install gh` (versão pode ser antiga; prefira o [repo oficial](https://github.com/cli/cli/blob/trunk/docs/install_linux.md)) |
| Fedora/RHEL | `sudo dnf install gh` |
| macOS | `brew install gh` |
| Windows | `winget install GitHub.cli` |

```bash
gh auth login
```

**Verificação:**

```bash
gh --version
gh auth status
# esperado: "Logged in to github.com as seu-usuario"
```

### 6.2 mise — um gerenciador para todas as linguagens

Se você trabalha com Node **e** Python **e** Go, `mise` substitui `fnm`, `pyenv`,
`nvm` e `asdf` de uma vez.

```bash
curl https://mise.run | sh
```

Adicione ao perfil:

```bash
echo 'eval "$(~/.local/bin/mise activate bash)"' >> ~/.bashrc
```

(troque `bash` por `zsh` e `~/.bashrc` por `~/.zshrc` se você usa zsh)

Num projeto, crie `.mise.toml`:

```toml
[tools]
node = "22"
python = "3.12"
```

Entrar na pasta passa a trocar as versões automaticamente.

**Verificação:**

```bash
mise doctor
# esperado: "No problems found"
```

### 6.3 GitHub Spec Kit — desenvolvimento guiado por especificação

Toolkit de código aberto do GitHub que formaliza o fluxo
*especificar → planejar → tarefas → implementar* para agentes. Suporta
mais de duas dezenas de ferramentas (Claude Code, Copilot, Codex, Cursor,
Gemini CLI, Windsurf, entre outras).

```bash
uvx --from git+https://github.com/github/spec-kit.git specify init meu-projeto
```

*O que faz:* baixa e roda o `specify` sem instalar nada permanentemente, e cria
a estrutura de especificação dentro de `meu-projeto`.

**Verificação:** o comando cria uma pasta com os templates e comandos de
especificação. O conceito é tratado no [16](16-especificacao-e-plano.md).

### 6.4 Servidores MCP

**MCP** (*Model Context Protocol*) é o padrão aberto que permite ao agente falar
com sistemas externos — banco de dados, Jira, navegador, sistema de arquivos
remoto. Não instale nenhum no primeiro dia: você não vai saber avaliar o risco.

Quando chegar a hora, o assunto está em
[agentes-de-ia](../agentes-de-ia/00-MAPA.md), arquivo `15-mcp-model-context-protocol.md`,
e a superfície de ataque está no [22-seguranca](22-seguranca.md) daqui.

---

## PATH e variáveis de ambiente

Metade dos problemas de instalação é PATH. Vale entender de verdade, uma vez.

### O que é o PATH

É uma variável de ambiente com uma **lista ordenada de diretórios**. Quando você
digita `claude`, o shell procura um arquivo executável chamado `claude` em cada
diretório da lista, **em ordem**, e roda o primeiro que encontrar.

```bash
echo $PATH
# exemplo:
# /home/voce/.local/bin:/usr/local/bin:/usr/bin:/bin
```

No Windows PowerShell:

```powershell
$env:PATH -split ';'
```

### Descobrir qual binário está sendo usado

```bash
which claude          # o primeiro que o shell acharia
type -a claude        # TODOS os que existem, em ordem  ← mais útil
```

`type -a` é o comando que resolve o mistério "instalei a versão nova e continua
rodando a velha": ele mostra que existem duas, e qual ganha.

No Windows:

```powershell
Get-Command claude -All
```

### Em qual arquivo mexer

| Shell | Arquivo de perfil | Como saber qual shell você usa |
|---|---|---|
| bash | `~/.bashrc` (interativo) e `~/.bash_profile` (login) | `echo $SHELL` |
| zsh (padrão no macOS) | `~/.zshrc` | `echo $SHELL` |
| fish | `~/.config/fish/config.fish` | `echo $SHELL` |
| PowerShell | `$PROFILE` (rode `echo $PROFILE` para o caminho) | — |

Adicionar um diretório ao PATH:

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

*O que faz:* a primeira linha grava no perfil; a segunda **recarrega agora**.

### "Instalei e continua dando `command not found`"

Quase sempre é uma destas três:

1. **Você não reabriu o terminal.** O perfil só é lido quando o shell inicia. A
   mudança existe no arquivo mas não na sessão atual. Solução: `source ~/.bashrc`
   ou abrir uma aba nova.
2. **Você editou o arquivo errado.** Escreveu em `~/.bash_profile` mas usa zsh.
   Confira com `echo $SHELL`.
3. **O diretório está no PATH mas o binário não está lá.** Confirme com
   `ls ~/.local/bin/`.

### Variáveis de ambiente que este curso usa

| Variável | Para que serve | Onde definir |
|---|---|---|
| `ANTHROPIC_API_KEY` | Chave da API da Anthropic | Gerenciador de segredos, **nunca** no perfil versionado |
| `OPENAI_API_KEY` | Chave da OpenAI | idem |
| `COPILOT_GITHUB_TOKEN` | Token do Copilot CLI | idem |
| `HTTP_PROXY` / `HTTPS_PROXY` / `NO_PROXY` | Proxy corporativo | Perfil do shell |
| `DISABLE_AUTOUPDATER` | Trava a atualização automática do Claude Code | `settings.json` do Claude Code |

> **Regra que salva carreira:** chave de API não mora em arquivo de perfil, não
> mora em `Dockerfile`, não mora em `docker-compose.yml`, e principalmente não
> mora num arquivo que o agente pode ler e colar em outro lugar. Use
> `direnv`, `1Password CLI`, `pass`, ou o gerenciador de credenciais do sistema.
> O tratado completo está em
> [variaveis-de-ambiente-e-segredos](../variaveis-de-ambiente-e-segredos/00-MAPA.md).

---

## Permissões — e por que `sudo npm -g` é um problema

Você vai ver, em fórum e resposta de IA, a sugestão de resolver erro de permissão
com `sudo npm install -g`. **Não faça.** Motivos concretos:

1. **Os arquivos ficam pertencendo ao root.** Da próxima vez que você (sem sudo)
   tentar atualizar, dá `EACCES` de novo — e agora você está preso a usar `sudo`
   para sempre.
2. **Scripts de `postinstall` rodam como root.** Um pacote npm arbitrário
   executa código na sua máquina com privilégio total, na hora da instalação.
   Isso é a superfície de ataque mais explorada da cadeia de suprimentos de
   software. Com pacote alucinado por IA no meio (ver
   [22-seguranca](22-seguranca.md)), o risco deixa de ser teórico.
3. **A atualização automática quebra.** Ferramentas como o Claude Code detectam
   que o diretório global do npm não é gravável e param de se atualizar
   sozinhas — você fica numa versão velha sem perceber.

### O jeito certo: prefixo global no seu diretório pessoal

```bash
mkdir -p ~/.npm-global
npm config set prefix ~/.npm-global
echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

*O que faz:* diz ao npm para instalar pacotes globais dentro da sua pasta, e põe
essa pasta no PATH. A partir daí `npm install -g` funciona sem `sudo`.

**Verificação:**

```bash
npm config get prefix
# esperado: /home/seu-usuario/.npm-global
npm install -g cowsay && cowsay funcionou
# esperado: um desenho de vaca dizendo "funcionou", sem erro de permissão
```

Se você usa `fnm`, `nvm` ou `mise`, isso já está resolvido: o Node fica na sua
pasta pessoal e o diretório global também.

---

## Rede corporativa

Se você está atrás de proxy, firewall ou inspeção TLS, nada disso funciona sem
configuração. Sintoma típico: o download trava, ou dá
`unable to get local issuer certificate`.

### Proxy

```bash
export HTTP_PROXY="http://proxy.empresa.com:8080"
export HTTPS_PROXY="http://proxy.empresa.com:8080"
export NO_PROXY="localhost,127.0.0.1,::1,.empresa.com"
```

Ponha no perfil do shell para persistir.

> **Armadilha real e chata de diagnosticar:** um `NO_PROXY` malformado (com
> espaço depois da vírgula, ou com `http://` no valor) faz bibliotecas Python e
> Node tentarem passar pelo proxy até para `localhost`. O sintoma é o teste
> local falhando com erro de proxy. Escreva sem espaços.

### npm e proxy

```bash
npm config set proxy http://proxy.empresa.com:8080
npm config set https-proxy http://proxy.empresa.com:8080
```

### Certificado interno (inspeção TLS)

Sua empresa provavelmente intercepta HTTPS com um certificado próprio. Para as
ferramentas confiarem nele:

```bash
export NODE_EXTRA_CA_CERTS=/caminho/para/ca-empresa.pem
export REQUESTS_CA_BUNDLE=/caminho/para/ca-empresa.pem
export SSL_CERT_FILE=/caminho/para/ca-empresa.pem
```

```bash
git config --global http.sslCAInfo /caminho/para/ca-empresa.pem
```

> **Nunca** resolva isso com `npm config set strict-ssl false` ou
> `git config --global http.sslVerify false`. Isso desliga a verificação
> globalmente e transforma qualquer rede em que você entrar num alvo fácil. É a
> "solução" mais recomendada da internet e é errada.

### Domínios que precisam ser liberados

Peça ao time de rede a liberação de (conforme as ferramentas que você usar):

```
api.anthropic.com          claude.ai            downloads.claude.ai
api.openai.com             chatgpt.com
api.githubcopilot.com      github.com           api.github.com
generativelanguage.googleapis.com
registry.npmjs.org         pypi.org             files.pythonhosted.org
```

---

## Convivência de versões

Cenário real: um projeto exige Node 20, outro Node 22, e o agente precisa acertar
em ambos.

**Solução:** arquivo de versão na raiz de cada projeto.

```bash
echo "22.14.0" > .node-version    # lido por fnm, mise, asdf
echo "3.12"    > .python-version  # lido por pyenv, uv, mise
```

Ou, com `mise`, um só arquivo:

```toml
# .mise.toml
[tools]
node = "22.14.0"
python = "3.12"
```

**Verificação:**

```bash
cd meu-projeto && node --version
# esperado: exatamente a versão do .node-version
```

> **Por que isso importa especificamente com IA:** o arquivo de versão é uma
> **instrução legível por máquina**. O agente lê `.node-version`, entende o alvo,
> e para de sugerir sintaxe que não existe na sua versão. Sem ele, o agente
> assume a versão mais comum na internet — que muda a cada seis meses.

---

## Reprodutibilidade

Se o ambiente não é reproduzível, "funciona na minha máquina" vira "funciona na
sessão do agente" — o que é pior, porque a sessão morre.

Checklist mínimo por projeto:

| Artefato | Para quê | Comando |
|---|---|---|
| `package-lock.json` | Trava as versões exatas de dependências Node | gerado por `npm install` — **commite** |
| `uv.lock` ou `requirements.txt` com hash | Idem para Python | `uv lock` |
| `.node-version` / `.python-version` | Trava a versão da linguagem | `echo` acima |
| `.devcontainer/devcontainer.json` | Ambiente inteiro em container, idêntico para todos | ver [docker](../docker/00-MAPA.md) |
| `AGENTS.md` | Instruções para o agente: como buildar, testar, estilo | ver [14](14-contexto-e-o-repositorio.md) |

> **Instalação via lockfile, não via `install`:** use `npm ci` em vez de
> `npm install` no CI e ao clonar. `npm ci` instala **exatamente** o que está no
> lockfile e falha se houver divergência; `npm install` pode atualizar
> silenciosamente. Isso é a sua primeira defesa contra pacote alucinado entrando
> na árvore de dependências — assunto do [22-seguranca](22-seguranca.md).

---

## Atualizar com segurança, e voltar atrás

| Ferramenta | Atualizar | Voltar atrás |
|---|---|---|
| Claude Code (nativo) | automático; forçar com `claude update` | `curl -fsSL https://claude.ai/install.sh \| bash -s 2.1.89` |
| Claude Code (brew) | `brew upgrade claude-code` | `brew install claude-code@<versão>` |
| Copilot CLI (npm) | `npm install -g @github/copilot@latest` | `npm install -g @github/copilot@<versão>` |
| Codex CLI (npm) | `npm install -g @openai/codex@latest` | idem |
| Node (fnm) | `fnm install 22 && fnm default 22` | `fnm use 20` |
| Python (uv) | `uv python install 3.13` | `uv python pin 3.12` |

**Regra de ofício:** antes de atualizar a ferramenta que você usa todo dia,
anote a versão que está funcionando. Ferramentas de agente mudam rápido e
regressões acontecem.

```bash
claude --version >> ~/versoes-que-funcionaram.txt
```

Para travar o Claude Code no canal estável (cerca de uma semana de atraso,
pulando releases com regressão grave), em `~/.claude/settings.json`:

```json
{
  "autoUpdatesChannel": "stable"
}
```

---

## Desinstalar por completo

Instalação parcial esquecida é a causa nº 1 de "atualizei e continua na versão
velha".

### Encontrar todas as cópias

```bash
type -a claude
type -a node
```

### Claude Code

Veja a seção 4.1. Não esqueça de `~/.claude` e `~/.claude.json`.

### Node instalado por gerenciador de versão

```bash
fnm uninstall 22
rm -rf ~/.fnm         # remove o fnm inteiro
```

### npm — pacotes globais e cache

```bash
npm ls -g --depth=0     # lista o que está instalado globalmente
npm cache clean --force
rm -rf ~/.npm           # cache; pode chegar a alguns GB
```

### Python — ambientes e cache

```bash
uv cache clean
rm -rf ~/.cache/uv ~/.cache/pip
```

### O que sempre fica para trás

| Caminho | Do quê |
|---|---|
| `~/.cache/` | caches de npm, pip, uv, ferramentas |
| `~/.config/` | configurações de várias CLIs |
| `~/.local/share/` | binários e dados de instaladores nativos |
| `~/Library/Caches/` (macOS) | idem |
| `%LOCALAPPDATA%` (Windows) | idem |

---

## Solução de problemas — erros literais

| Mensagem | Causa provável | Correção |
|---|---|---|
| `command not found: claude` | Binário fora do PATH, ou terminal não reaberto | `type -a claude`; se não achar, confira `ls ~/.local/bin/`; `source ~/.bashrc` ou abra outra aba |
| `EACCES: permission denied, mkdir '/usr/lib/node_modules/...'` | `npm -g` sem permissão no diretório global | Configure prefixo pessoal (seção Permissões). **Não** use `sudo` |
| `npm ERR! code EBADENGINE` / `Unsupported engine` | Node abaixo da versão mínima do pacote | `fnm install 22 && fnm use 22` |
| `unable to get local issuer certificate` | Inspeção TLS corporativa sem CA configurada | `export NODE_EXTRA_CA_CERTS=/caminho/ca.pem`. **Não** desligue `strict-ssl` |
| `permission denied while trying to connect to the Docker daemon socket at unix:///var/run/docker.sock` | Usuário fora do grupo `docker` | `sudo usermod -aG docker $USER` e **relogar** |
| `python não é reconhecido como um comando interno ou externo` (Windows) | Instalador rodado sem "Add python.exe to PATH" | Reinstale marcando a caixa, ou adicione manualmente ao PATH |
| `syntax error near unexpected token '<'` ao rodar `curl ... \| bash` | O curl recebeu HTML (página de erro, portal de proxy) em vez do script | Rode o `curl` sozinho e leia a saída. Provável bloqueio de rede |
| `The token '&&' is not a valid statement separator` | Você está no PowerShell rodando comando de CMD | Use a variante PowerShell do comando |
| `fatal: not a git repository` | Você não está dentro de um repositório | `git init` ou `cd` para o projeto certo |
| `Error: Cannot find module '@anthropic-ai/claude-code-linux-x64'` | npm instalou sem dependências opcionais | `npm install -g @anthropic-ai/claude-code --include=optional` ou use o instalador nativo |
| `gpg: no valid OpenPGP data found` ao adicionar o repo apt | O download da chave falhou (rede/proxy) | Confirme acesso a `downloads.claude.ai` e refaça o `curl` |
| `NO_PUBKEY BAA929FF1A7ECACE` no `apt update` | A chave não foi baixada corretamente | Refaça o passo do `curl` da chave |
| Agente muito lento no Windows | Projeto em `/mnt/c/` acessado do WSL | Mova o projeto para `~/` dentro do WSL |
| `EAI_AGAIN` / `getaddrinfo ENOTFOUND` | DNS ou proxy | Confira `HTTPS_PROXY` e a liberação dos domínios |

---

## Checklist de "ambiente pronto"

Rode tudo. Se qualquer linha falhar, volte para a seção correspondente antes de
seguir para o [04-como-comecar](04-como-comecar.md).

```bash
git --version
```
```bash
rg --version
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
docker run --rm hello-world
```
```bash
claude --version
```
```bash
gitleaks version
```
```bash
pre-commit --version
```
```bash
git config --global user.email
```
```bash
echo $PATH
```

E, por fim, o teste que prova que o conjunto funciona:

```bash
mkdir -p /tmp/teste-ambiente && cd /tmp/teste-ambiente
git init
echo "print('ok')" > main.py
python3 main.py
# esperado: ok
git add -A && git commit -m "teste"
# esperado: commit criado, sem erro de identidade
```

---

## Fontes consultadas

Consultadas em **20/08/2026**:

- Claude Code — instalação e requisitos: https://code.claude.com/docs/en/setup
- OpenAI Codex CLI: https://github.com/openai/codex
- GitHub Copilot CLI — instalação: https://docs.github.com/en/copilot/how-tos/copilot-cli/set-up-copilot-cli/install-copilot-cli
- Gemini CLI (repositório oficial, ativo, Apache 2.0): https://github.com/google-gemini/gemini-cli
- GitHub Spec Kit: https://github.com/github/spec-kit
- AGENTS.md: https://agents.md/
- uv (Astral): https://docs.astral.sh/uv/
- fnm: https://github.com/Schniz/fnm
- mise: https://mise.jdx.dev/
- gitleaks: https://github.com/gitleaks/gitleaks

> **Nota de método:** durante a pesquisa para este arquivo, vários sites
> agregadores afirmavam que o Gemini CLI havia sido descontinuado em 2026. A
> verificação no repositório oficial mostrou o projeto **ativo**, com releases
> semanais. Isso é uma lição do próprio curso: **conteúdo de agregador sobre
> ferramentas de IA é frequentemente gerado por IA e frequentemente falso.**
> Verifique na fonte primária.

---

## Autoteste

1. Por que a seção "comece sem instalar nada" vem antes de tudo?
2. Explique, com os cinco porquês, por que não se deve instalar Node pelo `apt`.
3. Você digitou `claude` e deu `command not found`, mas o arquivo existe em
   `~/.local/bin/claude`. Quais são as três causas possíveis?
4. Por que `sudo npm install -g` é ruim? Dê três razões, sendo uma de segurança.
5. Qual é o comando que mostra **todas** as cópias de um binário, e por que ele é
   mais útil que `which`?
6. No Windows, por que WSL2 é recomendado em vez do PowerShell nativo para
   trabalho com agentes? Dê duas razões técnicas.
7. O que é o Bloco 5 e por que este curso o considera não-negociável?
8. Você está atrás de proxy corporativo com inspeção TLS. Qual é a correção
   certa e qual é a "correção" que a internet sugere e que você não deve fazer?
9. Por que `.node-version` na raiz do projeto ajuda especificamente um agente?
10. Um projeto no WSL está lentíssimo com o agente. Qual é a primeira hipótese?

---

**Anterior:** [02-pre-requisitos](02-pre-requisitos.md) ·
**Próximo:** [04-como-comecar](04-como-comecar.md) — do ambiente pronto ao
primeiro resultado.
