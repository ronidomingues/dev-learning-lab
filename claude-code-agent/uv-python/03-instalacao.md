# 03 · Manual de instalação — passo a passo, por sistema operacional

> **Nível:** iniciante · **Atualizado em:** 31/08/2026
> **Testado em:** uv **0.12.7** (`x86_64-unknown-linux-gnu`), Ubuntu 22.04.5 LTS,
> em **31/08/2026**. Os comandos para macOS e Windows vêm da documentação oficial
> consultada na mesma data; onde não pude executar, isso está dito explicitamente.
> **Versão mínima recomendada:** 0.9.0 (antes disso faltam `uv version`, `uv format`,
> `uv check` e o backend `uv_build` estável). **Evite:** qualquer coisa abaixo de 0.5,
> onde o formato do `uv.lock` ainda mudava com frequência.

---

## Índice deste manual

1. [Antes de tudo: a alternativa sem instalar nada](#alternativa-sem-instalar-nada)
2. [Decisão: qual método usar](#1-decisão-qual-método-de-instalação-usar)
3. [Linux](#2-linux)
4. [macOS](#3-macos)
5. [Windows nativo](#4-windows-nativo)
6. [Windows com WSL2](#5-windows-com-wsl2)
7. [Docker / container](#6-docker--container)
8. [PATH e variáveis de ambiente](#7-path-e-variáveis-de-ambiente)
9. [Permissões: por que `sudo` é armadilha](#8-permissões-por-que-sudo-costuma-ser-armadilha)
10. [Autocompletar no shell](#9-autocompletar-no-shell)
11. [Instalando o Python **com** o uv](#10-instalando-o-python-com-o-uv)
12. [As outras tecnologias do conjunto](#11-as-outras-tecnologias-do-conjunto)
13. [Rede corporativa](#12-rede-corporativa-proxy-certificado-e-índice-espelhado)
14. [Convivência de versões](#13-convivência-de-versões)
15. [Reprodutibilidade](#14-reprodutibilidade-travar-a-versão-do-próprio-uv)
16. [Atualizar e voltar atrás](#15-atualizar-e-voltar-atrás)
17. [Desinstalar por completo](#16-desinstalar-por-completo)
18. [Solução de problemas](#17-solução-de-problemas--tabela-de-erros-literais)
19. [Checklist "ambiente pronto"](#18-checklist-ambiente-pronto)

---

<a id="alternativa-sem-instalar-nada"></a>
## 0. Antes de tudo: a alternativa sem instalar nada

**Leia esta seção primeiro.** Se o seu objetivo hoje é *entender* o uv, você não
precisa instalar nada. Instale depois, com calma. Três caminhos, do mais rápido ao
mais completo:

### 0.1 GitHub Codespaces (navegador, gratuito com limites)

1. Acesse qualquer repositório seu no GitHub (ou crie um vazio).
2. Botão verde **Code** → aba **Codespaces** → **Create codespace on main**.
3. Espere o VS Code abrir no navegador. No terminal integrado:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```
Instala o uv dentro do container efêmero do Codespace.

```bash
source $HOME/.local/bin/env && uv --version
# esperado: uv 0.12.7 (ou superior)
```

> **Camada gratuita (consultada em 31/08/2026):** contas pessoais do GitHub têm
> 120 core-hours e 15 GB-mês de armazenamento gratuitos por mês. Uma máquina de 2 núcleos
> consome 2 core-hours por hora de uso — ou seja, ~60 h/mês. Exige cartão cadastrado
> apenas se você quiser passar do limite. Confira os valores atuais antes de confiar.

### 0.2 Docker, se você já tem Docker (2 comandos)

```bash
docker run --rm -it ghcr.io/astral-sh/uv:0.12.7-python3.13-bookworm bash
```
Sobe um container Debian com uv 0.12.7 e Python 3.13 já dentro, e te dá um shell.

```bash
uv --version && python --version
# esperado: uv 0.12.7 ... / Python 3.13.x
```
Ao sair (`exit`), o container é destruído (`--rm`) e nada fica na sua máquina.

### 0.3 Playground online de Python (sem uv)

Não existe um "playground do uv" oficial no navegador — o uv é uma ferramenta de
sistema de arquivos, não faz sentido em sandbox web. Se você só quer testar *Python*,
use [python.org/shell](https://www.python.org/shell/) ou
[Google Colab](https://colab.research.google.com). Mas para aprender uv de verdade,
use 0.1 ou 0.2.

**Quando o caminho longo compensa:** a partir do momento em que você vai trabalhar no
seu próprio projeto, todos os dias. Aí instale local — o cache e os hard links, que são
metade da vantagem do uv, só existem em disco de verdade.

---

## 1. Decisão: qual método de instalação usar

| Método | Recomendo? | Quando usar | Riscos |
|---|---|---|---|
| **Instalador oficial** (`curl \| sh`, `irm \| iex`) | ✅ **padrão para todo mundo** | máquina pessoal ou de trabalho, qualquer SO | executa script da internet; leia antes se sua política exigir |
| **Homebrew** (macOS/Linux) | ✅ se você já vive no Homebrew | quer o uv junto do resto das suas ferramentas | atualiza junto com tudo; `uv self update` fica bloqueado |
| **WinGet / Scoop** (Windows) | ✅ | ambiente Windows gerenciado | idem: atualização pelo gerenciador |
| **pipx** | 🟡 aceitável | você já usa pipx e quer padronizar | ironia: usa Python para instalar a ferramenta que gerencia Python |
| **pip** | ❌ evite | último recurso | instala o uv *dentro* de um ambiente Python; some quando o ambiente some |
| **Cargo** (`cargo install --locked uv`) | 🟡 só para quem desenvolve o uv | quer compilar do fonte | compila por ~10–20 min e exige toolchain Rust |
| **Docker** | ✅ para CI e para experimentar | pipelines, ambientes efêmeros | não é sua máquina; cache não persiste sem volume |
| **Pacote da distro** (`apt`, `dnf`) | ❌ evite | — | quase sempre desatualizado; o uv lança versão a cada ~1–2 semanas |

> **Recomendação explícita:** use o **instalador oficial**. Ele não precisa de `sudo`,
> instala em `~/.local/bin`, funciona igual nos três sistemas, e é o único caminho em
> que `uv self update` funciona.

---

## 2. Linux

### 2.1 Família Debian / Ubuntu

**Passo 1 — garanta que existe `curl`.**

```bash
sudo apt update && sudo apt install -y curl ca-certificates
```
Instala o `curl` (para baixar o instalador) e os certificados raiz (para o HTTPS funcionar).

```bash
curl --version | head -1
# esperado: curl 7.81.0 (x86_64-pc-linux-gnu) ... (ou superior)
```
Se der `command not found`, o `apt install` falhou — repita olhando a mensagem de erro.

**Passo 2 — instale o uv.**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```
Baixa o script oficial (`-L` segue redirecionamento, `-s` silencioso, `-S` mostra erro,
`-f` falha em erro HTTP) e executa. Ele detecta sua arquitetura, baixa o binário certo,
coloca em `~/.local/bin` e escreve um arquivo `~/.local/bin/env`.

> **Quer inspecionar antes de executar** (recomendado em máquina corporativa)?
> ```bash
> curl -LsSf https://astral.sh/uv/install.sh -o /tmp/uv-install.sh && less /tmp/uv-install.sh && sh /tmp/uv-install.sh
> ```

**Passo 3 — carregue o `PATH` na sessão atual.**

```bash
source $HOME/.local/bin/env
```
O instalador já acrescentou essa linha ao seu `~/.bashrc`, mas o terminal **já aberto**
não sabe disso. Este comando resolve para a sessão atual.

**Passo 4 — verifique.**

```bash
uv --version
# esperado: uv 0.12.7 (x86_64-unknown-linux-gnu)
```
Se aparecer `uv: command not found`, veja a [seção de PATH](#7-path-e-variáveis-de-ambiente).

```bash
which uv uvx
# esperado:
# /home/SEU_USUARIO/.local/bin/uv
# /home/SEU_USUARIO/.local/bin/uvx
```

**Passo 5 — teste de fogo (opcional, 20 s).**

```bash
uvx cowsay -t "uv funciona"
```
Baixa o pacote `cowsay` num ambiente temporário, roda e descarta. Se você viu uma vaca
em ASCII, **está tudo funcionando**: rede, TLS, cache, execução.

<details>
<summary>Saída real desta máquina (31/08/2026)</summary>

```
  ===========
           \
            \
              ^__^
              (oo)\_______
              (__)\       )\/\
                  ||----w |
                  ||     ||
```
</details>

### 2.2 Família Fedora / RHEL / Rocky / Alma

```bash
sudo dnf install -y curl ca-certificates
```
Mesmo papel do `apt` acima.

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh && source $HOME/.local/bin/env
```
Instala e carrega o PATH em um comando.

```bash
uv --version
# esperado: uv 0.12.7 (x86_64-unknown-linux-gnu)
```

**Alternativa nativa (Fedora 40+):** existe pacote `uv` no repositório oficial.

```bash
sudo dnf install -y uv && uv --version
```
Funciona, mas **fica para trás**: a versão do repositório costuma estar semanas atrás da
oficial, e `uv self update` é bloqueado. Use só se sua política proibir instaladores externos.

### 2.3 Arch / Manjaro

```bash
sudo pacman -S uv && uv --version
```
O Arch acompanha upstream de perto; aqui o pacote da distro é uma escolha razoável.

### 2.4 Alpine (musl)

```bash
apk add --no-cache curl bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```
O instalador detecta musl e baixa o binário `x86_64-unknown-linux-musl`.

```bash
uv --version
# esperado: uv 0.12.7 (x86_64-unknown-linux-musl)
```
Confira o sufixo `musl` — se vier `gnu`, algo está errado e o binário vai falhar com
`not found` mesmo existindo (erro clássico de musl: falta do `ld-linux`).

### 2.5 Linux ARM64 (Raspberry Pi, Graviton, Ampere)

Idêntico ao 2.1. O instalador detecta `aarch64` sozinho.

```bash
uname -m
# esperado: aarch64
uv --version
# esperado: uv 0.12.7 (aarch64-unknown-linux-gnu)
```

### 2.6 Sem `curl`? Use `wget`

```bash
wget -qO- https://astral.sh/uv/install.sh | sh
```
`-q` silencia, `-O-` manda a saída para o `stdout` (que é canalizado para o `sh`).

---

## 3. macOS

### 3.1 Instalador oficial (recomendado)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```
Mesmo script do Linux; detecta `arm64` (Apple Silicon: M1/M2/M3/M4) ou `x86_64` (Intel).

```bash
source $HOME/.local/bin/env
uv --version
# esperado (Apple Silicon): uv 0.12.7 (aarch64-apple-darwin)
# esperado (Intel):         uv 0.12.7 (x86_64-apple-darwin)
```

> **Intel × Apple Silicon — quando importa:** importa muito para os **pacotes**, não para
> o uv. Em Apple Silicon, se você rodar um terminal sob Rosetta, o uv detecta `x86_64` e
> vai instalar wheels Intel — que funcionam, mas lentos. Confira com:
> ```bash
> arch
> # esperado num Mac ARM nativo: arm64
> ```
> Se aparecer `i386` num Mac M-series, seu Terminal está em Rosetta: Finder → Aplicativos
> → Utilitários → clique-direito no Terminal → Obter Informações → desmarque
> "Abrir com Rosetta".

### 3.2 Homebrew

```bash
brew install uv
```
Instala pelo Homebrew (em `/opt/homebrew/bin` no ARM, `/usr/local/bin` no Intel).

```bash
uv --version
# esperado: uv 0.12.7 (...-apple-darwin)
```

Atualizar: `brew upgrade uv`. **`uv self update` não funciona** nesta instalação — e isso
é proposital: o uv se recusa a substituir um binário gerenciado por outro gerenciador,
para não deixar o Homebrew com um registro mentiroso.

### 3.3 MacPorts

```bash
sudo port install uv && uv --version
```

### 3.4 Ferramentas de linha de comando da Apple

Você **não** precisa do Xcode inteiro. Precisa das *Command Line Tools* se algum pacote
Python tiver de ser compilado do código-fonte (acontece com pacotes científicos antigos
sem wheel para ARM):

```bash
xcode-select --install
```
Abre um diálogo gráfico; aceite. Ocupa ~2 GB.

```bash
xcode-select -p
# esperado: /Library/Developer/CommandLineTools
```

---

## 4. Windows nativo

> **Caminho recomendado:** para **desenvolver Python puro em Windows**, o uv nativo é
> excelente e é o que recomendo — mais rápido que WSL para I/O de arquivos e integra
> direto com VS Code e PowerShell. Use **WSL2** apenas se o seu projeto depende de
> bibliotecas ou comportamentos Unix (por exemplo `uvloop`, `fcntl`, caminhos POSIX,
> ou uma imagem Docker Linux que você quer espelhar exatamente). Explico a escolha na
> [seção 5](#5-windows-com-wsl2).

### 4.1 Instalador oficial (PowerShell)

Abra o **Terminal do Windows** (não o `cmd.exe`) e:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
`irm` (`Invoke-RestMethod`) baixa o script; `iex` (`Invoke-Expression`) executa.
`-ExecutionPolicy ByPass` evita o bloqueio padrão do Windows a scripts — vale só para
este processo, não muda a política da máquina.

**Feche e reabra o terminal.** No Windows a variável `PATH` só é relida em processo novo.

```powershell
uv --version
# esperado: uv 0.12.7 (x86_64-pc-windows-msvc)
```

```powershell
Get-Command uv | Select-Object Source
# esperado: C:\Users\SEU_USUARIO\.local\bin\uv.exe
```

### 4.2 WinGet

```powershell
winget install --id=astral-sh.uv -e
```
`-e` exige correspondência exata do ID, evitando instalar um pacote de nome parecido.

```powershell
uv --version
```

### 4.3 Scoop

```powershell
scoop install main/uv
uv --version
```

### 4.4 `uv.exe`, `uvx.exe` e `uvw.exe` — a diferença

| Binário | Para quê |
|---|---|
| `uv.exe` | o comando principal |
| `uvx.exe` | atalho para `uv tool run` |
| `uvw.exe` | igual ao `uv`, mas **sem abrir janela de console** — use ao chamar o uv de dentro de um app gráfico ou de uma tarefa agendada |

### 4.5 Compilador no Windows (só se precisar)

Se um pacote não tiver wheel para Windows, o uv tentará compilar e falhará com
`Microsoft Visual C++ 14.0 or greater is required`. Instale as ferramentas de build:

```powershell
winget install --id=Microsoft.VisualStudio.2022.BuildTools -e
```
Depois, no instalador do Visual Studio, marque a carga de trabalho
**"Desenvolvimento para desktop com C++"**. Ocupa ~7 GB.

> **Antes de gastar 7 GB:** verifique se o pacote realmente não tem wheel. Procure em
> `https://pypi.org/project/NOME/#files` por um arquivo `...-win_amd64.whl`. Na maioria
> esmagadora dos casos existe, e o erro real é outro (Python de 32 bits, versão de Python
> nova demais).

---

## 5. Windows com WSL2

WSL2 (*Windows Subsystem for Linux*, versão 2) roda um Linux real dentro do Windows.

**Passo 1 — instale o WSL2** (PowerShell como administrador):

```powershell
wsl --install -d Ubuntu-24.04
```
Instala o subsistema e a distro Ubuntu 24.04. Reinicie quando pedir.

```powershell
wsl --status
# esperado: Versão padrão: 2
```

**Passo 2 — dentro do Ubuntu do WSL**, siga exatamente a [seção 2.1](#21-família-debian--ubuntu).

**Passo 3 — a regra de ouro do desempenho:**

> **Mantenha o projeto dentro do sistema de arquivos do Linux** (`/home/voce/projetos`),
> **nunca** em `/mnt/c/Users/...`. O acesso a `/mnt/c` atravessa uma ponte de rede
> (9P/virtiofs) e é ordens de grandeza mais lento. Um `uv sync` que leva 2 segundos em
> `/home` pode levar minutos em `/mnt/c`. Este é, de longe, o erro nº 1 de quem usa uv
> no WSL.

**Quando escolher WSL2 em vez de Windows nativo:**

| Situação | Escolha |
|---|---|
| Aprendendo Python, apps de terminal, web, dados | **Windows nativo** |
| Precisa reproduzir exatamente uma imagem Docker Linux | **WSL2** |
| Dependências que só existem em Linux (`uvloop`, `python-prctl`) | **WSL2** |
| Equipe toda em Linux/macOS e você quer o mesmo `uv.lock` resolvido | **WSL2** (o lock do uv é universal, mas o comportamento de build não) |
| Quer o máximo de velocidade de I/O | **Windows nativo** |

---

## 6. Docker / container

### 6.1 Imagens oficiais

```bash
docker pull ghcr.io/astral-sh/uv:0.12.7
```
Imagem só com o binário do uv (baseada em Debian), sem Python.

```bash
docker pull ghcr.io/astral-sh/uv:0.12.7-python3.13-bookworm-slim
```
Imagem com uv **e** Python 3.13 sobre Debian 12 slim — a que eu uso na maioria dos casos.

Variantes disponíveis: `-alpine`, `-bookworm`, `-bookworm-slim`, `-trixie`,
e por versão de Python (`-python3.10` a `-python3.14`).

### 6.2 Copiar o binário para a sua imagem (padrão recomendado)

```dockerfile
# syntax=docker/dockerfile:1
FROM python:3.13-slim-bookworm

# Copia apenas o binário do uv de uma imagem oficial fixada por versão.
COPY --from=ghcr.io/astral-sh/uv:0.12.7 /uv /uvx /bin/

WORKDIR /app

# Copia primeiro só os manifestos, para aproveitar o cache de camada do Docker.
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-install-project --no-dev

# Agora o código; mudanças aqui não invalidam a camada de dependências.
COPY . .
RUN uv sync --locked --no-dev

ENV PATH="/app/.venv/bin:$PATH"
CMD ["python", "-m", "meuapp"]
```

Verificação:

```bash
docker build -t meuapp . && docker run --rm meuapp
```

> **Por que `--locked`?** Ele **falha** se o `uv.lock` estiver desatualizado em relação
> ao `pyproject.toml`, em vez de silenciosamente relockar. Numa imagem de produção você
> quer o erro, não a surpresa. Ver [19-uv-em-docker-e-ci.md](19-uv-em-docker-e-ci.md).

### 6.3 Verificação da imagem

```bash
docker run --rm ghcr.io/astral-sh/uv:0.12.7 uv --version
# esperado: uv 0.12.7 (x86_64-unknown-linux-gnu)
```

---

## 7. PATH e variáveis de ambiente

### 7.1 O que o instalador faz

O instalador coloca os binários em:

| SO | Diretório |
|---|---|
| Linux / macOS | `$HOME/.local/bin` |
| Windows | `%USERPROFILE%\.local\bin` |

e acrescenta esse diretório ao seu `PATH` editando o arquivo de perfil do shell.

### 7.2 Qual arquivo de perfil, exatamente

| Shell / SO | Arquivo editado | Como recarregar sem fechar o terminal |
|---|---|---|
| bash (Linux) | `~/.bashrc` | `source ~/.bashrc` |
| bash (macOS) | `~/.bash_profile` | `source ~/.bash_profile` |
| zsh (padrão do macOS) | `~/.zshrc` | `source ~/.zshrc` |
| fish | `~/.config/fish/conf.d/` | `exec fish` |
| PowerShell | `$PROFILE` (veja com `echo $PROFILE`) | `. $PROFILE` |
| qualquer um (uv ≥ 0.5) | `~/.local/bin/env` | `source $HOME/.local/bin/env` |

> **Por que "a mudança não pegou"?** Porque variáveis de ambiente são **herdadas na
> criação do processo**. Seu terminal já estava aberto quando o arquivo mudou; ele não
> relê nada sozinho. Ou você recarrega (`source`), ou abre um terminal novo. No Windows,
> `source` não existe — **é obrigatório abrir um terminal novo**.

### 7.3 Conferir o PATH

```bash
echo "$PATH" | tr ':' '\n' | grep -n "local/bin"
# esperado: uma linha contendo /home/SEU_USUARIO/.local/bin
```
Quebra o PATH em uma entrada por linha e procura pelo diretório do uv.

No PowerShell:

```powershell
$env:PATH -split ';' | Select-String "\.local\\bin"
```

### 7.4 Corrigir o PATH à mão

Linux/macOS com bash:

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc && source ~/.bashrc
```
Acrescenta o diretório **no início** do PATH (prioridade) e recarrega.

Windows (permanente, para o usuário):

```powershell
[Environment]::SetEnvironmentVariable("PATH", "$env:USERPROFILE\.local\bin;" + [Environment]::GetEnvironmentVariable("PATH","User"), "User")
```
Depois **feche e reabra o terminal**.

### 7.5 Instalar em outro diretório

```bash
curl -LsSf https://astral.sh/uv/install.sh | env UV_INSTALL_DIR="/opt/uv" sh
```
`UV_INSTALL_DIR` define onde o binário vai. Útil para instalação compartilhada em servidor.

```bash
curl -LsSf https://astral.sh/uv/install.sh | env UV_NO_MODIFY_PATH=1 sh
```
`UV_NO_MODIFY_PATH=1` impede o instalador de tocar nos seus arquivos de perfil — use em
CI ou quando você gerencia o PATH por outro meio (Ansible, dotfiles versionados).

```bash
curl -LsSf https://astral.sh/uv/install.sh | env UV_UNMANAGED_INSTALL="/tmp/uv-ci" sh
```
`UV_UNMANAGED_INSTALL` instala sem registrar receptor de auto-update nem mexer em perfil —
o modo correto para runners efêmeros de CI.

### 7.6 As variáveis de ambiente que valem a pena conhecer agora

| Variável | Para quê |
|---|---|
| `UV_CACHE_DIR` | mover o cache (disco cheio, disco de rede, CI) |
| `UV_PYTHON_INSTALL_DIR` | onde ficam os Pythons gerenciados |
| `UV_PYTHON_DOWNLOADS=never` | proibir o uv de baixar Python (ambientes controlados) |
| `UV_TOOL_DIR` / `UV_TOOL_BIN_DIR` | onde ficam as ferramentas do `uv tool install` |
| `UV_PROJECT_ENVIRONMENT` | usar outro caminho no lugar de `.venv` |
| `UV_LINK_MODE` | `hardlink` (padrão), `copy`, `symlink`, `clone` — ver [14-cache](14-cache-e-instalacao.md) |
| `UV_OFFLINE=1` | trabalhar sem rede, só com cache |
| `UV_COMPILE_BYTECODE=1` | pré-compilar `.pyc` na instalação (imagens Docker: startup mais rápido) |
| `UV_HTTP_TIMEOUT` | aumentar o tempo limite (padrão 30 s) em rede ruim |
| `UV_CONCURRENT_DOWNLOADS` | reduzir paralelismo em rede frágil ou proxy que rejeita rajadas |
| `UV_SYSTEM_CERTS=1` | usar o repositório de certificados do sistema (rede corporativa) |
| `UV_INDEX` | índices adicionais (repositório privado da empresa) |
| `UV_PUBLISH_TOKEN` | token para `uv publish` |

Lista completa: `uv help` e a [referência oficial de variáveis](https://docs.astral.sh/uv/reference/environment/).

---

## 8. Permissões: por que `sudo` costuma ser armadilha

**Regra:** você **nunca** precisa de `sudo` para instalar ou usar o uv, exceto se
escolher deliberadamente instalar em diretório do sistema.

### Por que `sudo pip install` é problema (e por que o uv evita)

1. **Ele corrompe o Python do sistema.** Em Ubuntu, Fedora e derivados, ferramentas do
   próprio SO (`apt`, `dnf`, `firewalld`, `netplan`) são escritas em Python e importam
   pacotes de `/usr/lib/python3/dist-packages`. Instalar globalmente pode substituir uma
   versão que o SO esperava e **quebrar o gerenciador de pacotes da máquina** — um estrago
   que costuma exigir reinstalar o sistema.
2. **Ele é irreversível na prática.** Arquivos ficam espalhados por `/usr/lib`,
   `/usr/local/lib`, `/usr/bin`; `pip uninstall` não remove tudo.
3. **Ele mistura raiz e usuário.** Arquivos criados por root dentro de `~/.cache` fazem
   comandos futuros do seu usuário falharem com `Permission denied`.

Por isso, desde 2023, distros marcam o Python do sistema como *externally managed*
(PEP 668) e o `pip` global recusa a instalação com a mensagem
`error: externally-managed-environment`.

**A resposta do uv:** ele nunca instala no Python do sistema por padrão. Ele cria um
`.venv` no projeto, ou usa `~/.local/share/uv/tools` para ferramentas, ou
`~/.local/share/uv/python` para interpretadores. Tudo dentro do seu diretório pessoal.

### Se você *já* estragou o Python do sistema

```bash
# Ubuntu/Debian: veja o que foi instalado fora do controle do apt
ls /usr/local/lib/python3.*/dist-packages
```
Nada aí deveria existir numa máquina saudável. Remova com cuidado, um a um, e
**reinstale os pacotes do SO afetados** com `sudo apt install --reinstall python3-<nome>`.

### Instalação para todos os usuários (servidor)

```bash
sudo env UV_INSTALL_DIR=/usr/local/bin UV_NO_MODIFY_PATH=1 sh -c 'curl -LsSf https://astral.sh/uv/install.sh | sh'
```
Coloca o binário num diretório já no PATH de todos. Aqui o `sudo` é legítimo: você está
instalando **um binário estático**, não pacotes Python. `uv self update` passará a exigir
`sudo` também — o que é correto.

---

## 9. Autocompletar no shell

Vale os 10 segundos: o uv tem muitos subcomandos e flags.

```bash
echo 'eval "$(uv generate-shell-completion bash)"' >> ~/.bashrc && source ~/.bashrc
```
Bash.

```bash
echo 'eval "$(uv generate-shell-completion zsh)"' >> ~/.zshrc && source ~/.zshrc
```
Zsh (padrão do macOS).

```bash
echo 'uv generate-shell-completion fish | source' > ~/.config/fish/completions/uv.fish
```
Fish.

```powershell
Add-Content -Path $PROFILE -Value '(& uv generate-shell-completion powershell) | Out-String | Invoke-Expression'
```
PowerShell. Se der erro dizendo que `$PROFILE` não existe:
`New-Item -Path $PROFILE -Type File -Force` antes.

Verificação: digite `uv py` e aperte `TAB`. Deve completar para `uv python`.

Para o `uvx`, repita trocando `uv` por `uvx` no comando (`uvx generate-shell-completion ...`).

---

## 10. Instalando o Python **com** o uv

Este é o ponto onde o uv substitui o `pyenv` e o instalador do python.org.

### 10.1 Ver o que está disponível

```bash
uv python list
```
Lista versões instaladas e disponíveis para download.

<details>
<summary>Saída real desta máquina (31/08/2026, recortada)</summary>

```
cpython-3.15.0rc1-linux-x86_64-gnu                 <download available>
cpython-3.14.7-linux-x86_64-gnu                    <download available>
cpython-3.14.7+freethreaded-linux-x86_64-gnu       <download available>
cpython-3.13.15-linux-x86_64-gnu                   <download available>
cpython-3.12.14-linux-x86_64-gnu                   <download available>
cpython-3.11.16-linux-x86_64-gnu                   <download available>
cpython-3.10.12-linux-x86_64-gnu                   /usr/bin/python3.10
pypy-3.11.15-linux-x86_64-gnu                      <download available>
graalpy-3.12.0-linux-x86_64-gnu                    <download available>
```
</details>

Repare: o uv **enxerga o Python do sistema** (`/usr/bin/python3.10`) e o reaproveita,
em vez de duplicar. E oferece **PyPy**, **GraalPy** e builds **free-threaded**
(sem GIL, PEP 703).

### 10.2 Instalar uma versão

```bash
uv python install 3.13
```
Baixa e instala o CPython 3.13 mais recente em `~/.local/share/uv/python`. Não toca no
Python do sistema, não exige `sudo`, não altera nada fora do seu `$HOME`.

```bash
uv python list --only-installed
# esperado: uma linha com cpython-3.13.x-... e o caminho da instalação
```

Várias de uma vez:

```bash
uv python install 3.11 3.12 3.13 3.14
```

### 10.3 Fixar a versão de um projeto

```bash
cd meuprojeto && uv python pin 3.13
```
Escreve `3.13` no arquivo `.python-version`. Todo comando do uv naquele diretório passa
a usar essa versão — e **baixa automaticamente** se faltar. Versione esse arquivo no Git.

```bash
cat .python-version
# esperado: 3.13
```

### 10.4 Onde as coisas ficam

```bash
uv python dir   # /home/SEU_USUARIO/.local/share/uv/python
uv tool dir     # /home/SEU_USUARIO/.local/share/uv/tools
uv cache dir    # /home/SEU_USUARIO/.cache/uv
```
(Saídas reais desta máquina.)

### 10.5 O Python do uv é "de verdade"?

Sim, com uma ressalva honesta. São builds do projeto
[`astral-sh/python-build-standalone`](https://github.com/astral-sh/python-build-standalone):
CPython oficial, compilado de forma **relocável** (funciona em qualquer caminho) e com as
bibliotecas ligadas estaticamente sempre que possível.

**A ressalva:** por serem estáticos e relocáveis, há diferenças observáveis em casos raros —
extensões C que dependem de detalhes de `libpython` compartilhada, alguns
comportamentos de `dlopen`, e o `tkinter` que nem sempre vem completo. Para 99% dos
usos você não vai notar. Se for um desses 1%, use um Python do sistema com
`uv python pin /usr/bin/python3.12` ou `UV_PYTHON_DOWNLOADS=never`.

### 10.6 Colocar o Python do uv no PATH (opcional)

```bash
uv python update-shell
```
Adiciona o diretório dos executáveis Python gerenciados ao seu PATH, para que
`python3.13` funcione fora de projetos uv. **Meu conselho: não faça isso** a menos que
precise. Deixe o `uv run` resolver o Python — é justamente o que evita confusão.

---

## 11. As outras tecnologias do conjunto

O uv sozinho não é um ambiente de desenvolvimento. Aqui está o resto, cada um com sua
instalação e verificação.

### 11.1 Git — obrigatório para trabalho em equipe

| SO | Comando |
|---|---|
| Debian/Ubuntu | `sudo apt install -y git` |
| Fedora/RHEL | `sudo dnf install -y git` |
| Arch | `sudo pacman -S git` |
| macOS | `xcode-select --install` (já traz git) ou `brew install git` |
| Windows | `winget install --id Git.Git -e` |

```bash
git --version
# esperado: git version 2.34.1 (ou superior)
```

Configuração mínima (uma vez por máquina):

```bash
git config --global user.name "Seu Nome"
git config --global user.email "seu@email.com"
```
Sem isso, o `uv init` cria o repositório mas você não consegue commitar.

### 11.2 VS Code + extensões — recomendado, não obrigatório

| SO | Comando |
|---|---|
| Debian/Ubuntu | `sudo snap install code --classic` |
| Fedora | baixe o `.rpm` em [code.visualstudio.com](https://code.visualstudio.com/) |
| macOS | `brew install --cask visual-studio-code` |
| Windows | `winget install --id Microsoft.VisualStudioCode -e` |

Extensões (pela linha de comando, depois de instalar o VS Code):

```bash
code --install-extension ms-python.python
code --install-extension charliermarsh.ruff
code --install-extension tamasfe.even-better-toml
```
1. Suporte a Python (IntelliSense, depurador). 2. Ruff, o linter/formatador da Astral —
é o que o `uv format` usa por baixo. 3. Realce e validação de `pyproject.toml`.

```bash
code --list-extensions | grep -E "ms-python|ruff|toml"
# esperado: as três linhas acima
```

**Fazer o VS Code enxergar o `.venv` do uv:** crie `.vscode/settings.json` no projeto:

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
  "python.terminal.activateEnvironment": true
}
```
No Windows, troque por `${workspaceFolder}\\.venv\\Scripts\\python.exe`.

### 11.3 Compilador C — só se um pacote não tiver wheel

| SO | Comando |
|---|---|
| Debian/Ubuntu | `sudo apt install -y build-essential python3-dev` |
| Fedora/RHEL | `sudo dnf install -y gcc gcc-c++ make python3-devel` |
| macOS | `xcode-select --install` |
| Windows | Visual Studio Build Tools ([seção 4.5](#45-compilador-no-windows-só-se-precisar)) |

```bash
cc --version
# esperado: gcc (Ubuntu 11.4.0-...) 11.4.0  (ou clang no macOS)
```

> **Quando isto é necessário na prática, em 2026:** quase nunca. O ecossistema Python
> tem wheels binários para Linux/macOS/Windows × x86-64/ARM64 para praticamente todo
> pacote relevante. Você vai precisar de compilador ao (a) usar pacotes antigos e
> abandonados, (b) rodar em arquitetura exótica (s390x, RISC-V), (c) usar Alpine/musl
> com pacotes que só publicam `manylinux`.

### 11.4 Docker — para o capítulo de CI e produção

| SO | Comando |
|---|---|
| Debian/Ubuntu | `curl -fsSL https://get.docker.com \| sudo sh` |
| Fedora | `sudo dnf install -y docker-ce docker-ce-cli containerd.io` |
| macOS | `brew install --cask docker` (Docker Desktop) ou `brew install colima docker` |
| Windows | `winget install --id Docker.DockerDesktop -e` |

Linux, para não precisar de `sudo` a cada comando:

```bash
sudo usermod -aG docker "$USER" && newgrp docker
```
Adiciona seu usuário ao grupo `docker`. **Atenção de segurança:** pertencer a esse grupo
equivale a ter root na máquina, porque você pode montar `/` dentro de um container.
Em máquina pessoal é aceitável; em servidor compartilhado, não.

```bash
docker run --rm hello-world
# esperado: "Hello from Docker!"
```

Curso completo de Docker nesta pasta: [../docker/00-MAPA.md](../docker/00-MAPA.md).

### 11.5 Ruff e ty — instalados pelo próprio uv

A partir da 0.12, `uv format` e `uv check` baixam sozinhos o Ruff e o `ty` na primeira
execução (comportamento observado nesta máquina em 31/08/2026):

```
warning: `uv format` is experimental and may change without warning.
Downloading ruff v0.15.22 (10.5MiB)
1 file left unchanged
```

Se você quiser as ferramentas disponíveis fora de projetos:

```bash
uv tool install ruff
```
Instala o `ruff` num ambiente isolado e coloca o executável em `~/.local/bin`.

```bash
uv tool list
# esperado:
# ruff v0.16.5
# - ruff
```
(Saída real desta máquina. Repare que a versão do `uv tool install` — 0.16.5 — é mais
nova que a que o `uv format` baixou internamente — 0.15.22: são canais diferentes.)

```bash
uv tool update-shell
```
Garante que `~/.local/bin` (ou `UV_TOOL_BIN_DIR`) esteja no PATH. Se você instalou o uv
pelo instalador oficial, já está.

### 11.6 Um índice de pacotes acessível

Verificação de que o PyPI está alcançável a partir da sua máquina:

```bash
uv pip download --no-deps --dest /tmp/testepypi requests 2>&1 | tail -2
```
Se falhar com erro de TLS ou timeout, vá para a [seção 12](#12-rede-corporativa-proxy-certificado-e-índice-espelhado).

---

## 12. Rede corporativa: proxy, certificado e índice espelhado

### 12.1 Proxy HTTP

```bash
export HTTPS_PROXY="http://proxy.empresa.com:8080"
export HTTP_PROXY="http://proxy.empresa.com:8080"
export NO_PROXY="localhost,127.0.0.1,.empresa.com"
```
O uv usa a convenção padrão do sistema. Coloque no `~/.bashrc` para persistir.

Com usuário e senha:

```bash
export HTTPS_PROXY="http://usuario:senha@proxy.empresa.com:8080"
```
> ⚠️ Isso deixa a senha no histórico do shell e no ambiente de todo processo filho.
> Prefira um proxy que aceite autenticação integrada, ou use um arquivo com permissão
> `600` carregado por `source`. Ver
> [variaveis-de-ambiente-e-segredos](../variaveis-de-ambiente-e-segredos/00-MAPA.md).

> **Armadilha real e comum:** um `NO_PROXY` malformado (com espaços, com `http://`, ou
> com CIDR que a biblioteca não entende) faz chamadas a `localhost` irem para o proxy e
> falharem de um jeito confuso. Se algo local quebrou depois de configurar proxy,
> desconfie do `NO_PROXY` antes de qualquer outra coisa.

### 12.2 Certificado interno (TLS interceptado)

Sintoma: `error sending request ... invalid peer certificate: UnknownIssuer`.

Causa: a empresa intercepta HTTPS com um certificado próprio, que o uv (que traz sua
própria lista de certificados raiz, via `webpki-roots`) não conhece.

**Solução A — usar o repositório de certificados do sistema:**

```bash
export UV_SYSTEM_CERTS=1
```
Faz o uv ler os certificados já instalados no SO (onde o time de TI provavelmente já
colocou o certificado da empresa). É a solução certa. (`UV_NATIVE_TLS` é o nome antigo,
depreciado.)

**Solução B — apontar um pacote de certificados explícito:**

```bash
export SSL_CERT_FILE=/caminho/para/ca-empresa.pem
```

Para instalar o certificado no SO:

```bash
# Debian/Ubuntu
sudo cp ca-empresa.crt /usr/local/share/ca-certificates/ && sudo update-ca-certificates
# Fedora/RHEL
sudo cp ca-empresa.crt /etc/pki/ca-trust/source/anchors/ && sudo update-ca-trust
```

**Solução C — último recurso, inseguro:**

```bash
export UV_INSECURE_HOST="pypi.org files.pythonhosted.org"
```
Desativa a verificação de certificado para esses hosts. **Isto abre você a ataque
man-in-the-middle.** Use só para diagnosticar, nunca como configuração permanente.

### 12.3 Índice interno (Artifactory, Nexus, devpi)

`~/.config/uv/uv.toml` (Linux/macOS) ou `%APPDATA%\uv\uv.toml` (Windows):

```toml
[[index]]
name = "empresa"
url = "https://artifactory.empresa.com/api/pypi/pypi-virtual/simple"
default = true
```
Torna o índice interno o padrão, substituindo o PyPI.

Se o índice exigir autenticação:

```bash
uv auth login empresa
```
Guarda a credencial no cofre do sistema (`uv auth dir` mostra onde). Alternativa por
variável: `UV_INDEX_EMPRESA_USERNAME` e `UV_INDEX_EMPRESA_PASSWORD`.

> **Segurança — o ataque de "confusão de dependência":** se você configurar o índice
> interno como *extra* em vez de *default*, o uv pode encontrar em ambos os índices um
> pacote de mesmo nome, e um invasor pode publicar no PyPI público um pacote com o nome
> do seu pacote interno. Use `default = true` (substituindo o PyPI) ou fixe a origem de
> cada pacote interno com `[tool.uv.sources]` e `explicit = true`.
> Mais em [21-seguranca.md](21-seguranca-e-cadeia-de-suprimentos.md).

### 12.4 Firewall — o que precisa ser liberado

| Host | Para quê |
|---|---|
| `astral.sh` | baixar o instalador |
| `github.com`, `objects.githubusercontent.com` | binários do uv e Pythons gerenciados |
| `pypi.org` | metadados de pacotes |
| `files.pythonhosted.org` | os arquivos dos pacotes |
| `ghcr.io` | imagens Docker oficiais (se usar) |

### 12.5 Rede instável

```bash
export UV_HTTP_TIMEOUT=120
export UV_CONCURRENT_DOWNLOADS=4
```
Aumenta o tempo limite (padrão 30 s) e reduz o paralelismo (padrão é alto), que às vezes
faz proxies corporativos derrubarem conexões.

---

## 13. Convivência de versões

### 13.1 Várias versões de Python na mesma máquina

É o caso normal com uv, e não dá conflito:

```bash
uv python install 3.11 3.12 3.13
```
As três coexistem em `~/.local/share/uv/python`, em diretórios separados, junto com o
Python do sistema, que fica intocado.

Cada projeto escolhe a sua:

```bash
cd projeto-legado && uv python pin 3.11
cd ../projeto-novo && uv python pin 3.13
```

Ou por comando:

```bash
uv run --python 3.12 python --version
# esperado: Python 3.12.x
```

### 13.2 Convivência com `pyenv`, `conda` e `asdf`

| Coexiste com | Como | Cuidado |
|---|---|---|
| **pyenv** | sim; o uv detecta interpretadores do pyenv no PATH | os *shims* do pyenv podem fazer `python` apontar para lugar inesperado; prefira `uv run` |
| **conda** | sim; com um ambiente conda ativo, `uv pip install` instala **nele** | não misture `conda install` e `uv pip install` no mesmo ambiente para o mesmo pacote: o conda não conhece o que o uv fez |
| **asdf / mise** | sim | evite gerenciar Python em dois lugares; escolha um |
| **Python do sistema** | sim, e o uv o reaproveita | nunca instale pacotes nele (PEP 668 já impede) |

### 13.3 Duas versões do próprio uv

Raro, mas acontece em CI que precisa reproduzir um lock antigo:

```bash
uvx uv@0.9.5 --version
```
Executa a versão 0.9.5 do uv sem instalá-la. `uvx` sabe rodar o próprio uv.

Ou instale isoladamente:

```bash
uv tool install uv@0.9.5 --with-executables-from uv
```

### 13.4 Descobrir de onde veio o uv que você está usando

```bash
which -a uv
```
Lista **todas** as ocorrências no PATH. Se aparecer mais de uma (por exemplo
`/opt/homebrew/bin/uv` e `~/.local/bin/uv`), a primeira ganha — e é essa a origem do
seu "atualizei mas a versão não mudou".

---

## 14. Reprodutibilidade: travar a versão do próprio uv

### 14.1 No projeto

```toml
# pyproject.toml
[tool.uv]
required-version = ">=0.12,<0.13"
```
Faz o uv recusar-se a operar no projeto se a versão instalada estiver fora da faixa —
protege contra um colega com uv antigo gerar um lock incompatível.

### 14.2 Arquivos que devem ir para o Git

| Arquivo | Versionar? | Por quê |
|---|---|---|
| `pyproject.toml` | ✅ **sempre** | é a declaração das suas dependências |
| `uv.lock` | ✅ **sempre** (aplicações **e** bibliotecas) | é o que garante o ambiente idêntico |
| `.python-version` | ✅ sim | garante a mesma versão de Python para todos |
| `.venv/` | ❌ **nunca** | é gerado, é grande, é específico da máquina |
| `uv.toml` | ✅ se existir | configuração do uv fora do `pyproject.toml` |
| `requirements.txt` gerado por `uv export` | 🟡 só se algo externo precisar | é derivado; o original é o `uv.lock` |

> **Debate real:** a orientação clássica do Python era "biblioteca não versiona lockfile".
> A prática moderna, que eu recomendo, é **versionar sempre**: o lock não afeta quem
> instala a sua biblioteca (só o `pyproject.toml` importa para isso), mas garante que
> os **seus testes** rodem sempre no mesmo ambiente. Você ganha reprodutibilidade sem
> custo. Use `--resolution lowest-direct` no CI para também testar os limites inferiores.

### 14.3 `.gitignore` mínimo

O `uv init` já cria um. Confira que contém:

```gitignore
.venv/
__pycache__/
*.py[cod]
dist/
build/
*.egg-info/
```

### 14.4 Fixar a versão do uv no CI

```yaml
# GitHub Actions
- uses: astral-sh/setup-uv@v6
  with:
    version: "0.12.7"
    enable-cache: true
```
Instala exatamente a 0.12.7 e ativa o cache entre execuções.

---

## 15. Atualizar e voltar atrás

### 15.1 Atualizar

```bash
uv self update
```
Só funciona na instalação pelo **instalador oficial**. Baixa a versão mais nova e
substitui o binário no lugar.

```bash
uv --version
# esperado: uma versão >= a que você tinha
```

| Instalado via | Como atualizar |
|---|---|
| instalador oficial | `uv self update` |
| Homebrew | `brew upgrade uv` |
| WinGet | `winget upgrade astral-sh.uv` |
| Scoop | `scoop update uv` |
| pipx | `pipx upgrade uv` |
| apt/dnf/pacman | `sudo apt upgrade uv` etc. |
| Docker | mude a tag da imagem |

### 15.2 Voltar a uma versão anterior

```bash
uv self update 0.12.5
```
`uv self update` aceita a versão de destino, inclusive para baixo.

Ou reinstale pela URL com versão:

```bash
curl -LsSf https://astral.sh/uv/0.12.5/install.sh | sh
```

### 15.3 Política de versões do uv, e o que isso significa para você

O uv está em `0.x`. Pela política declarada do projeto, mudanças que quebram
compatibilidade podem acontecer em **releases de minor** (`0.12` → `0.13`), nunca em
patch (`0.12.6` → `0.12.7`). O esquema do `uv.lock` também só muda em minor.

**Consequência prática:** fixe `>=0.12,<0.13` em `required-version` e atualize o minor
de forma deliberada, lendo o changelog. Patches podem ser automáticos sem medo.

---

## 16. Desinstalar por completo

Na ordem. Pular passos deixa gigabytes para trás.

**Passo 1 — apague o cache.**

```bash
uv cache clean
```
Remove `~/.cache/uv` inteiro. (Nesta máquina, após um dia de uso, ele tinha **217 MB** —
confirmado com `uv cache size`.)

**Passo 2 — remova os Pythons gerenciados.**

```bash
uv python uninstall --all
```
Ou, à força: `rm -rf "$(uv python dir)"`. Cada versão ocupa 100–150 MB.

**Passo 3 — remova as ferramentas instaladas.**

```bash
uv tool uninstall --all
```
Ou: `rm -rf "$(uv tool dir)"`.

**Passo 4 — remova os binários.**

```bash
rm -f ~/.local/bin/uv ~/.local/bin/uvx ~/.local/bin/env
```

Windows:

```powershell
Remove-Item "$HOME\.local\bin\uv.exe","$HOME\.local\bin\uvx.exe","$HOME\.local\bin\uvw.exe" -Force
```

**Passo 5 — limpe o que ficou para trás.**

```bash
rm -rf ~/.config/uv          # configuração global (uv.toml)
rm -rf ~/.local/share/uv     # python, tools, receipts
```

E edite `~/.bashrc` / `~/.zshrc` / `$PROFILE` removendo as linhas que o instalador
acrescentou (`. "$HOME/.local/bin/env"` e as de autocompletar).

**Passo 6 — os `.venv` dos projetos.**

Eles não estão nos diretórios acima. Encontre-os:

```bash
find ~ -maxdepth 4 -type d -name ".venv" -prune 2>/dev/null
```
Apague os que quiser. Nenhum deles é necessário: `uv sync` recria todos a partir do
`uv.lock`.

**Verificação final:**

```bash
command -v uv || echo "uv removido"
# esperado: uv removido
```

---

## 17. Solução de problemas — tabela de erros literais

| Mensagem | Causa provável | Correção |
|---|---|---|
| `uv: command not found` / `bash: uv: command not found` | `~/.local/bin` não está no PATH, ou o terminal não foi reaberto | `source $HOME/.local/bin/env` — se resolver, o problema é que o terminal era antigo. Se não, [seção 7.4](#74-corrigir-o-path-à-mão) |
| `'uv' is not recognized as an internal or external command` (Windows) | PATH não atualizado no processo atual | **Feche e reabra o Terminal.** No Windows não existe `source`. Se persistir, [seção 7.4](#74-corrigir-o-path-à-mão) |
| `error: externally-managed-environment` | você usou `pip install` no Python do sistema (PEP 668) | não use `pip` global. Use `uv add` num projeto, ou `uv tool install` para ferramentas |
| `error sending request for url (https://pypi.org/simple/...): invalid peer certificate: UnknownIssuer` | TLS interceptado por proxy corporativo | `export UV_SYSTEM_CERTS=1` ([seção 12.2](#122-certificado-interno-tls-interceptado)) |
| `error: Failed to download ... operation timed out` | proxy não configurado, firewall, ou rede lenta | configure `HTTPS_PROXY`; aumente `UV_HTTP_TIMEOUT=120`; reduza `UV_CONCURRENT_DOWNLOADS=4` |
| `error: No solution found when resolving dependencies` | versões pedidas são incompatíveis entre si | leia a explicação — o uv diz **qual par** conflita. Ver [13-resolucao](13-resolucao-de-dependencias.md) e [75-armadilhas](75-armadilhas.md) |
| `error: Distribution not found at: file:///...` | cache corrompido ou pacote removido do índice | `uv cache clean` e repita |
| `error: Failed to build \`pacote==1.2.3\`` seguido de `error: command 'gcc' failed` | não há wheel para sua plataforma e falta compilador | instale build tools ([seção 11.3](#113-compilador-c--só-se-um-pacote-não-tiver-wheel)); ou fixe uma versão que tenha wheel |
| `Microsoft Visual C++ 14.0 or greater is required` (Windows) | idem, no Windows | Visual Studio Build Tools ([seção 4.5](#45-compilador-no-windows-só-se-precisar)) |
| `error: The lockfile at \`uv.lock\` needs to be updated, but \`--locked\` was provided` | `pyproject.toml` mudou e o lock não foi regerado | rode `uv lock` e **comite o `uv.lock`** |
| `error: Python interpreter not found for: 3.13` com `UV_PYTHON_DOWNLOADS=never` | download proibido e a versão não está instalada | `uv python install 3.13`, ou remova a restrição |
| `EACCES: permission denied` ao instalar | você rodou algo com `sudo` antes e deixou arquivos de root no cache | `sudo chown -R "$USER:$USER" ~/.cache/uv ~/.local/share/uv` |
| `warning: \`uv audit\` is experimental and may change without warning` | comando em *preview* | é aviso, não erro. Silencie com `--preview-features audit-command` |
| `error: failed to create hardlink ... Invalid cross-device link` | cache e `.venv` estão em sistemas de arquivos diferentes (comum em Docker e WSL com `/mnt/c`) | `export UV_LINK_MODE=copy` ou coloque `UV_CACHE_DIR` no mesmo volume |
| `uv self update` diz `self-update is only available for uv binaries installed via the standalone installer` | instalado por Homebrew/apt/pipx | use o gerenciador correspondente ([seção 15.1](#151-atualizar)) |
| No WSL: tudo funciona mas está lento demais | o projeto está em `/mnt/c/...` | mova para `/home/voce/...` ([seção 5](#5-windows-com-wsl2)) |

### Diagnóstico geral

```bash
uv --version && uv python dir && uv cache dir && uv tool dir
```
Quatro fatos essenciais numa linha.

```bash
uv -v add requests
```
`-v` (ou `-vv`) mostra a resolução passo a passo: quais índices consultou, o que veio do
cache, por que escolheu cada versão. É a primeira coisa a fazer antes de pedir ajuda.

```bash
uv cache clean && uv sync --reinstall
```
A "reinstalação do zero": limpa cache e reconstrói o ambiente. Resolve uma classe grande
de problemas misteriosos.

---

## 18. Checklist "ambiente pronto"

Rode um por linha. Todos devem passar antes de você ir para o
[04-como-comecar.md](04-como-comecar.md).

```bash
uv --version
```
```bash
uvx cowsay -t "ok"
```
```bash
uv python list --only-installed
```
```bash
uv python install 3.13
```
```bash
uv cache dir
```
```bash
git --version
```
```bash
cd /tmp && uv init verificacao && cd verificacao && uv add requests && uv run python -c "import requests; print('AMBIENTE OK')"
```
```bash
cd /tmp && rm -rf verificacao
```

Se o penúltimo imprimiu `AMBIENTE OK`, você tem: uv funcionando, rede, TLS, cache,
criação de ambiente virtual, resolução, instalação e execução. **Está pronto.**

---

## Autoteste

1. Você está numa máquina sem permissão de administrador e sem Python. Qual é a
   sequência exata de comandos para chegar a um projeto rodando?
2. Por que `uv self update` falha numa instalação feita por Homebrew — e isso é um bug?
3. Qual variável de ambiente você usaria em um runner de CI efêmero, e por quê?
4. Explique, para um colega, por que `sudo pip install` pode quebrar o `apt` do Ubuntu.
5. Você recebe `invalid peer certificate: UnknownIssuer` no trabalho. Quais são as três
   soluções, em ordem de preferência, e por que a terceira é a pior?
6. O que significa `Invalid cross-device link` e qual a correção de uma linha?
7. Por que colocar um projeto em `/mnt/c` no WSL2 é um erro de desempenho grave?
8. Liste os seis passos para desinstalar o uv completamente, e diga o que cada um libera.
9. Qual a diferença entre `uv python pin` e `uv python install`?
10. Por que a orientação deste curso é versionar o `uv.lock` também em bibliotecas?

---

**Fontes consultadas (31/08/2026):**
[docs.astral.sh/uv/getting-started/installation](https://docs.astral.sh/uv/getting-started/installation/) ·
[docs.astral.sh/uv/reference/environment](https://docs.astral.sh/uv/reference/environment/) ·
[github.com/astral-sh/uv/releases/tag/0.12.7](https://github.com/astral-sh/uv/releases/tag/0.12.7) ·
[github.com/astral-sh/python-build-standalone](https://github.com/astral-sh/python-build-standalone) ·
saídas de comando executadas localmente em Ubuntu 22.04.5 com uv 0.12.7.

**Próximo:** [04-como-comecar.md](04-como-comecar.md)
