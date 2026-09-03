# 03 · Manual de instalação, passo a passo

`Nível: iniciante` · `Escrito e testado em 01/09/2026`

> **Ambiente de referência deste manual.** Tudo abaixo foi executado de verdade em
> **Ubuntu 22.04.5 LTS, x86-64, atrás de proxy corporativo**, em 01/09/2026, com:
> `uv` **0.12.7** · Python **3.12.14** (instalado pelo `uv`) · Node **v24.18.0** ·
> npm **12.0.1** · Docker **29.7.2** · SDK Python `mcp` **2.1.1** ·
> `@modelcontextprotocol/server` **2.0.0** · `@modelcontextprotocol/client` **2.0.0** ·
> `@modelcontextprotocol/inspector` **2.4.0**.
> As seções de macOS e Windows trazem os comandos oficiais equivalentes; o que **não**
> foi executado nesta máquina está marcado com ⚠️.

---

## Sumário

1. [O que precisa ser instalado](#1-o-que-precisa-ser-instalado)
2. [Escolha do caminho](#2-escolha-do-caminho)
3. [Python + uv](#3-python--uv)
4. [Node.js + npm](#4-nodejs--npm)
5. [SDK Python (`mcp`)](#5-sdk-python-mcp)
6. [SDK TypeScript](#6-sdk-typescript)
7. [MCP Inspector](#7-mcp-inspector)
8. [Docker (opcional, mas recomendado)](#8-docker-opcional-mas-recomendado)
9. [Um host para testar](#9-um-host-para-testar)
10. [PATH e variáveis de ambiente](#10-path-e-variáveis-de-ambiente)
11. [Permissões: o que nunca fazer com sudo](#11-permissões-o-que-nunca-fazer-com-sudo)
12. [Alternativa sem instalar nada](#12-alternativa-sem-instalar-nada)
13. [Rede corporativa: proxy, CA interna, registry espelhado](#13-rede-corporativa-proxy-ca-interna-registry-espelhado)
14. [Convivência de versões](#14-convivência-de-versões)
15. [Reprodutibilidade](#15-reprodutibilidade)
16. [Atualizar com segurança e voltar atrás](#16-atualizar-com-segurança-e-voltar-atrás)
17. [Desinstalar por completo](#17-desinstalar-por-completo)
18. [Solução de problemas — erros literais](#18-solução-de-problemas--erros-literais)
19. [Checklist "ambiente pronto"](#19-checklist-ambiente-pronto)

---

## 1. O que precisa ser instalado

MCP não é *um* programa. É um protocolo. Instalar "o MCP" não existe. O que você
instala é **o conjunto de tecnologias que permite escrever, rodar e depurar servidores
e clientes**. Um manual que instala só uma coisa não serve.

| # | Componente | Para quê | Obrigatório? |
|---|---|---|---|
| 1 | **Python 3.10+** e **`uv`** | escrever servidores/clientes em Python | Só se for usar Python |
| 2 | **Node.js 22.19+** e **npm** | escrever em TypeScript **e** rodar o Inspector | **Sim** (por causa do Inspector) |
| 3 | **SDK `mcp`** (PyPI) | biblioteca Python | Se for Python |
| 4 | **`@modelcontextprotocol/server` + `/client`** (npm) | biblioteca TypeScript | Se for TypeScript |
| 5 | **`@modelcontextprotocol/inspector`** | depurar servidores sem host nenhum | **Sim, na prática** |
| 6 | **Docker** | isolar servidores de terceiros; empacotar o seu | Recomendado |
| 7 | **Um host** (Claude Code / Desktop / VS Code / Cursor) | usar o servidor com um modelo de verdade | Opcional para aprender |
| 8 | **Um editor** com suporte a Python/TS | escrever o código | Sim |

> Se você só quer aprender e nunca escrever em TypeScript: **mesmo assim instale Node**,
> porque o Inspector é a melhor ferramenta de depuração do ecossistema e é Node.

---

## 2. Escolha do caminho

| Você quer… | Instale |
|---|---|
| Só entender e brincar hoje | pule para [§12 · sem instalar nada](#12-alternativa-sem-instalar-nada) |
| Escrever servidores em Python | §3 → §5 → §4 → §7 |
| Escrever servidores em TypeScript | §4 → §6 → §7 |
| Ambiente completo de estudo (recomendado) | §3 → §4 → §5 → §6 → §7 → §8 → §9 |

---

## 3. Python + uv

**Por que `uv` e não `pip`/`venv`/`conda`/`poetry`:** o `uv` instala o próprio
interpretador Python, cria o ambiente virtual, resolve dependências e gera lockfile —
tudo em um binário só, sem tocar no Python do sistema. É o que a documentação oficial
do MCP usa nos guias. Isso evita a classe inteira de problemas de "quebrei o Python
do sistema". Se você discorda e prefere `pip`, veja o método alternativo no fim da seção.

### 3.1 Linux — família Debian/Ubuntu

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```
Baixa e instala o `uv` em `~/.local/bin`. Não usa `sudo`, não toca no sistema.

> Se você desconfia de `curl | sh` — e é uma desconfiança saudável — baixe primeiro
> e leia: `curl -LsSf https://astral.sh/uv/install.sh -o uv-install.sh && less uv-install.sh && sh uv-install.sh`

**Abra um terminal novo** (ou `source ~/.bashrc`) e verifique:

```bash
uv --version
# esperado: uv 0.12.7 (ou superior)
```

**Se a saída for `command not found: uv`:** o `~/.local/bin` não está no PATH.
Vá para [§10](#10-path-e-variáveis-de-ambiente).

Agora instale um Python:

```bash
uv python install 3.12
```
Baixa um Python 3.12 gerenciado pelo `uv`, isolado do Python do sistema.

```bash
uv python list --only-installed
# esperado: uma linha contendo cpython-3.12.x-linux-x86_64-gnu
```

### 3.2 Linux — família Fedora/RHEL

Idêntico ao 3.1. O instalador do `uv` não depende de `apt` nem de `dnf`.
Se preferir o gerenciador do sistema:

```bash
sudo dnf install -y uv
```
Instala o `uv` empacotado pela distro — **pode estar atrasado**. Confira com `uv --version`
e, se estiver abaixo de 0.9, use o instalador da 3.1.

### 3.3 macOS (Intel e Apple Silicon)

```bash
brew install uv
```
Instala via Homebrew. Funciona igual nas duas arquiteturas; o Homebrew resolve
`/opt/homebrew` (Apple Silicon) vs `/usr/local` (Intel) sozinho.

Sem Homebrew:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

```bash
uv --version
# esperado: uv 0.12.7 (ou superior)
```

⚠️ Não executado nesta máquina.

### 3.4 Windows

**Caminho recomendado: WSL2.** Motivo concreto, não ideológico: praticamente todo
servidor MCP de terceiro assume caminhos POSIX, `stdout` sem CRLF e `stderr` como canal
de log. No Windows nativo você vai encontrar servidores que simplesmente não sobem, e
vai depurar diferença de fim de linha em vez de aprender MCP.

**WSL2** (PowerShell como Administrador):

```powershell
wsl --install -d Ubuntu-24.04
```
Instala o WSL2 com Ubuntu 24.04. Reinicie quando pedir; depois siga a seção 3.1
**dentro do Ubuntu**.

**Windows nativo** (PowerShell, se você realmente quiser):

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
Instala o `uv` em `%USERPROFILE%\.local\bin`.

```powershell
uv --version
# esperado: uv 0.12.7 (ou superior)
```

Se der `uv : O termo 'uv' não é reconhecido...`, **feche e reabra o PowerShell**.
Se persistir, veja [§10.3](#103-windows).

⚠️ Não executado nesta máquina.

### 3.5 Método alternativo: Python do sistema + `venv`

Legítimo, só mais trabalhoso e mais fácil de quebrar.

```bash
python3 --version
# esperado: Python 3.10.x ou superior — se for 3.9 ou menos, NÃO serve para mcp 2.x
```

```bash
python3 -m venv .venv && source .venv/bin/activate
```
Cria e ativa um ambiente virtual isolado no diretório atual.

```bash
which python
# esperado: um caminho terminado em /.venv/bin/python
```

> **Nunca** instale o SDK com `sudo pip install mcp`. Explicação em [§11](#11-permissões-o-que-nunca-fazer-com-sudo).

### 3.6 Comparação dos métodos

| Método | Prós | Contras | Use quando |
|---|---|---|---|
| **`uv`** ✅ recomendado | instala o Python, lockfile, rápido, sem `sudo` | mais uma ferramenta para aprender | sempre, salvo motivo forte |
| `venv` + `pip` | está em toda máquina, todo mundo conhece | não instala Python, sem lock por padrão | política da empresa proíbe binários externos |
| `pyenv` | várias versões de Python | compila do fonte, lento, exige libs de build | você já usa `pyenv` para outras coisas |
| `conda`/`mamba` | ecossistema científico | pesadíssimo para isto; conflita com `uv` | você já vive no conda |
| Docker | isolamento total | ciclo de desenvolvimento mais lento | rodar servidor de terceiro não confiável |

---

## 4. Node.js + npm

**Versão mínima real:** Node **20** para o SDK, mas **22.19.0** para o Inspector.
Instale **Node 22 LTS ou superior** e não pense mais no assunto.

### 4.1 Linux (Debian/Ubuntu e Fedora/RHEL) — via `fnm` (recomendado)

Não instale Node com `apt install nodejs`: a versão da distro fica anos atrás e
você não consegue trocar de versão por projeto.

```bash
curl -fsSL https://fnm.vercel.app/install | bash
```
Instala o `fnm` (Fast Node Manager) em `~/.local/share/fnm`, sem `sudo`.

Abra um terminal novo, então:

```bash
fnm install 22 && fnm default 22
```
Baixa o Node 22 LTS e o torna o padrão.

```bash
node --version
# esperado: v22.x.x (ou superior; esta máquina roda v24.18.0)
npm --version
# esperado: 10.x ou superior (esta máquina: 12.0.1)
```

**Se `node --version` disser `command not found`:** o `fnm` precisa de uma linha no
seu perfil. Veja [§10.1](#101-linux-e-macos).

Alternativa clássica com `nvm` (mais lento, mas todo mundo conhece):

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
```
Depois: `nvm install 22 && nvm use 22 && nvm alias default 22`.

### 4.2 macOS

```bash
brew install fnm
```
Depois `fnm install 22 && fnm default 22`.

Ou instalador oficial: baixe o `.pkg` em <https://nodejs.org/en/download>.
Funciona, mas prende você numa versão só.

⚠️ Não executado nesta máquina.

### 4.3 Windows

**WSL2:** siga a 4.1 dentro do Ubuntu. É o caminho recomendado.

**Windows nativo:**

```powershell
winget install OpenJS.NodeJS.LTS
```
Instala o Node LTS pelo gerenciador de pacotes da Microsoft.

```powershell
node --version
# esperado: v22.x.x ou superior
```

Para várias versões no Windows nativo, use `fnm` (`winget install Schniz.fnm`)
ou `nvm-windows` (projeto diferente do `nvm` do Linux — atenção).

⚠️ Não executado nesta máquina.

### 4.4 Comparação dos métodos

| Método | Prós | Contras |
|---|---|---|
| **`fnm`** ✅ | rápido (Rust), troca por `.node-version`, sem `sudo` | precisa de linha no perfil |
| `nvm` | onipresente, muita documentação | shell script lento; atrasa a abertura do terminal |
| `apt`/`dnf` | um comando | versão velha, difícil de trocar, tende a exigir `sudo npm -g` |
| instalador oficial | simples | uma versão só; atualizar é reinstalar |
| `volta` | lockfile de toolchain | menos difundido |

---

## 5. SDK Python (`mcp`)

### 5.1 Instalação num projeto novo (recomendado)

```bash
mkdir meu-servidor-mcp && cd meu-servidor-mcp
```

```bash
uv init --python 3.12 .
```
Cria `pyproject.toml`, `.python-version` e o esqueleto do projeto.

```bash
uv add "mcp[cli]"
```
Instala o SDK **e** a CLI `mcp` (que traz `mcp dev`, `mcp run`, `mcp install`).
O `uv` cria `.venv/` e grava `uv.lock`.

**Verificação:**

```bash
uv run mcp version
# esperado: MCP version 2.1.1 (ou superior)
```

```bash
uv run python -c "from mcp.server.mcpserver import MCPServer; print('ok')"
# esperado: ok
```

**Se a saída for `ModuleNotFoundError: No module named 'mcp.server.fastmcp'`** ao rodar
código antigo: você está no SDK 2.x, onde `FastMCP` virou `MCPServer`. Isso é
intencional e o próprio SDK te avisa. Ver [§18](#18-solução-de-problemas--erros-literais).

### 5.2 Fixando a versão maior

O salto de 1.x para 2.x **quebrou API**. Se você tem código v1:

```bash
uv add "mcp>=1.28,<2"
```
Trava no ramo 1.x, que está em modo de manutenção (só correção de segurança).

Para código novo, use 2.x — é o que fala a revisão `2026-07-28` do protocolo.

### 5.3 Método alternativo: `pip`

```bash
python3 -m venv .venv && source .venv/bin/activate && pip install "mcp[cli]"
```

```bash
mcp version
# esperado: MCP version 2.1.1
```

### 5.4 Sem projeto, para um teste rápido

```bash
uvx --from "mcp[cli]" mcp version
```
Roda a CLI num ambiente efêmero, sem instalar nada em lugar nenhum.

---

## 6. SDK TypeScript

> **Atenção à mudança de pacote.** No v1 havia um pacote monolítico
> `@modelcontextprotocol/sdk` (hoje na 1.30.0, ramo antigo). No **v2** ele foi
> dividido em `@modelcontextprotocol/server` e `@modelcontextprotocol/client`
> (ambos 2.0.0), que implementam a spec `2026-07-28`. Código novo usa os pacotes v2.

```bash
mkdir meu-servidor-ts && cd meu-servidor-ts && npm init -y
```

```bash
npm install @modelcontextprotocol/server @modelcontextprotocol/client zod
```
Instala servidor, cliente e o `zod` (usado para declarar os schemas das ferramentas).

**Verificação:**

```bash
npm ls --depth=0
# esperado, entre outras linhas:
# ├── @modelcontextprotocol/client@2.0.0
# ├── @modelcontextprotocol/server@2.0.0
# └── zod@4.5.4
```

```bash
node -e "const s=require('@modelcontextprotocol/server'); console.log(typeof s.McpServer)"
# esperado: function
```

Para TypeScript de verdade:

```bash
npm install -D typescript tsx @types/node && npx tsc --init
```
`tsx` roda `.ts` direto, sem passo de build — o ciclo de desenvolvimento fica curto.

Se estiver no ramo v1 por algum motivo (servidor legado):

```bash
npm install @modelcontextprotocol/sdk@1
```

---

## 7. MCP Inspector

A ferramenta oficial de depuração. **É o host mais importante do seu aprendizado**,
porque exercita o protocolo inteiro sem gastar um token de LLM.

Não instale globalmente. Rode sob demanda:

```bash
npx -y @modelcontextprotocol/inspector
```
Baixa (na primeira vez) e sobe a interface web do Inspector; ele imprime a URL
com um token de sessão. Abra no navegador.

**Modo CLI**, o que mais serve para script e CI:

```bash
npx -y @modelcontextprotocol/inspector --cli uv run python servidor.py --method tools/list
```
Sobe o seu servidor por stdio, pede a lista de ferramentas e imprime o JSON.
**Saída real desta máquina, 01/09/2026** (recortada):

```json
{
  "tools": [
    {
      "name": "somar",
      "description": "Soma dois números.",
      "inputSchema": {
        "type": "object",
        "properties": { "a": {"title":"A","type":"number"},
                        "b": {"title":"B","type":"number"} },
        "required": ["a","b"],
        "title": "somarArguments"
      },
      "outputSchema": { "type":"object",
        "properties": {"result":{"title":"Result","type":"number"}},
        "required":["result"], "title":"somarOutput" }
    }
  ]
}
```

**Se der `npm ERR! engine Unsupported engine`:** seu Node é anterior a 22.19.0.
Volte à [§4](#4-nodejs--npm).

O Inspector também tem modo **TUI** (terminal) — `--tui` — para quem não quer abrir
navegador.

---

## 8. Docker (opcional, mas recomendado)

Por que instalar: (a) muitos servidores de terceiros são distribuídos como imagem;
(b) é a única forma sã de rodar um servidor MCP de origem duvidosa sem lhe dar acesso
ao seu `~/.ssh`.

### 8.1 Linux (Debian/Ubuntu)

```bash
curl -fsSL https://get.docker.com | sudo sh
```
Instala o Docker Engine pelo script oficial.

```bash
sudo usermod -aG docker "$USER"
```
Permite usar o `docker` sem `sudo`. **Saia da sessão e entre de novo** — sem isso, o
grupo novo não vale.

```bash
docker --version
# esperado: Docker version 29.x (esta máquina: 29.7.2)
docker run --rm hello-world
# esperado: bloco de texto começando com "Hello from Docker!"
```

### 8.2 macOS / Windows

Instale **Docker Desktop** (<https://docs.docker.com/desktop/>) ou, no macOS,
`brew install --cask docker`. No Windows, o Docker Desktop usa o WSL2 por baixo.

⚠️ Não executado nesta máquina.

---

## 9. Um host para testar

Você não precisa de host nenhum para aprender (o Inspector basta). Mas em algum
momento vai querer ver o modelo usando a sua ferramenta.

### 9.1 Claude Code (CLI) — o mais prático para versionar configuração

```bash
claude --version
# esperado: 2.1.252 (Claude Code) ou superior
```

Registrar um servidor stdio local:

```bash
claude mcp add meu-servidor -- uv run --directory /caminho/do/projeto python servidor.py
```
Registra o servidor sob o nome `meu-servidor`, lançando o comando após o `--`.

Registrar um servidor HTTP remoto:

```bash
claude mcp add --transport http sentry https://mcp.sentry.dev/mcp
```

Com cabeçalho de autorização:

```bash
claude mcp add --transport http corridor https://app.corridor.dev/api/mcp --header "Authorization: Bearer SEU_TOKEN"
```

Conferir:

```bash
claude mcp list
```

### 9.2 Claude Desktop

Edite o arquivo de configuração:

| SO | Caminho |
|---|---|
| macOS | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Windows | `%APPDATA%\Claude\claude_desktop_config.json` |
| Linux | `~/.config/Claude/claude_desktop_config.json` |

```json
{
  "mcpServers": {
    "meu-servidor": {
      "command": "uv",
      "args": ["run", "--directory", "/caminho/absoluto/do/projeto", "python", "servidor.py"]
    }
  }
}
```

> **Três erros que todo mundo comete aqui:**
> 1. usar caminho relativo — o Claude Desktop não roda no diretório do seu projeto;
> 2. usar `uv` sem caminho absoluto quando o app não herda o seu PATH (no macOS, apps
>    do Finder não herdam o PATH do shell). Use `/Users/você/.local/bin/uv`;
> 3. esquecer de **reiniciar o aplicativo por completo** — fechar a janela não basta.

Atalho, se você usa a CLI `mcp` do SDK Python:

```bash
uv run mcp install servidor.py --name "Meu Servidor"
```
Escreve a entrada no `claude_desktop_config.json` para você.

### 9.3 VS Code / Cursor / outros

Todos leem um JSON com a mesma forma (`command` + `args`, ou `url` + `type: "http"`).
O nome e o local do arquivo mudam por aplicativo — consulte a documentação do seu.
A **forma** é sempre a mesma, e é essa a graça de haver um padrão.

---

## 10. PATH e variáveis de ambiente

### 10.1 Linux e macOS

O que é o PATH: a lista de pastas onde o shell procura um programa quando você digita
o nome dele. Se o binário não está numa dessas pastas, você recebe `command not found`
**mesmo com o programa instalado**.

Ver o PATH:

```bash
echo "$PATH" | tr ':' '\n'
```
Imprime uma pasta por linha.

Descobrir qual binário será usado:

```bash
which uv node npm
# esperado, por exemplo:
# /home/você/.local/bin/uv
# /home/você/.local/share/fnm/node-versions/v22.../installation/bin/node
```

Se faltar `~/.local/bin`, acrescente **no arquivo certo**:

| Shell | Arquivo | Como saber |
|---|---|---|
| bash | `~/.bashrc` | `echo $0` → `bash` |
| zsh (padrão do macOS) | `~/.zshrc` | `echo $0` → `zsh` |
| fish | `~/.config/fish/config.fish` | `echo $0` → `fish` |

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
```
Acrescenta a pasta ao PATH em toda sessão nova de bash.

```bash
source ~/.bashrc
```
Aplica agora, sem abrir outro terminal.

**Por que "não pegou" antes de reabrir o terminal:** um processo herda o ambiente do
pai **no momento em que nasce**. Editar `~/.bashrc` não altera o processo que já está
rodando; só afeta os próximos. Não é bug, é modelo de processos do Unix — e é a mesma
razão de o Claude Desktop precisar ser reiniciado por completo.

Para o `fnm`, a linha necessária é:

```bash
echo 'eval "$(fnm env --use-on-cd --shell bash)"' >> ~/.bashrc
```

### 10.2 Variáveis que o MCP usa

| Variável | Onde importa |
|---|---|
| `PATH` | o host precisa achar `uv`, `node`, `npx`, `python` |
| `HTTP_PROXY` / `HTTPS_PROXY` / `NO_PROXY` | instalação e servidores remotos ([§13](#13-rede-corporativa-proxy-ca-interna-registry-espelhado)) |
| `SSL_CERT_FILE`, `REQUESTS_CA_BUNDLE`, `NODE_EXTRA_CA_CERTS` | CA interna da empresa |
| segredos do seu servidor (`DATABASE_URL`, `GITHUB_TOKEN`…) | passados pelo host, na chave `env` da configuração |

> **Nunca coloque segredo em `args`.** `args` aparece em listagem de processos
> (`ps aux`) e frequentemente em logs do host. Use `env`.

Exemplo no Claude Desktop:

```json
{
  "mcpServers": {
    "meu-servidor": {
      "command": "uv",
      "args": ["run", "--directory", "/caminho", "python", "servidor.py"],
      "env": { "DATABASE_URL": "postgres://..." }
    }
  }
}
```

### 10.3 Windows

Ver o PATH:

```powershell
$env:PATH -split ';'
```

Acrescentar permanentemente para o usuário:

```powershell
[Environment]::SetEnvironmentVariable("PATH", "$env:USERPROFILE\.local\bin;" + [Environment]::GetEnvironmentVariable("PATH","User"), "User")
```
Grava no registro do usuário. **Feche e reabra o PowerShell** — o processo atual
não recebe a mudança.

Perfil do PowerShell (equivalente ao `.bashrc`): `$PROFILE` mostra o caminho;
`notepad $PROFILE` edita.

---

## 11. Permissões: o que nunca fazer com `sudo`

| Comando | Por que é problema | O que fazer |
|---|---|---|
| `sudo pip install mcp` | instala em `/usr/lib/python3/dist-packages`, o mesmo lugar em que o **gerenciador da distro** instala. Uma atualização do sistema sobrescreve ou conflita, e você quebra ferramentas do SO escritas em Python (`apt` inclusive, em algumas distros). | `uv add mcp` num projeto, ou `venv` |
| `sudo npm install -g` | cria arquivos de `root` em `/usr/lib/node_modules`; depois `npm` como usuário falha com `EACCES` e você fica preso ao `sudo` para sempre. Além disso, um pacote npm executa `postinstall` — com `sudo`, isso é código de terceiro rodando como root. | use `npx`, ou `fnm`, que instala tudo em `$HOME` |
| `sudo docker …` sem grupo | funciona, mas você acaba criando arquivos de `root` no seu projeto | `usermod -aG docker $USER` e reabra a sessão |
| rodar servidor MCP como root | o servidor executa código pedido pelo modelo. Como root, um erro de caminho vira dano irreversível | rode com o seu usuário, ou dentro de container sem privilégio |

Regra geral, e vale além do MCP: **se a instalação pede `sudo`, provavelmente você
escolheu o método errado.** Os três gerenciadores recomendados aqui (`uv`, `fnm`,
`npx`) instalam em `$HOME` e não pedem `sudo` nenhuma vez.

---

## 12. Alternativa sem instalar nada

Comece hoje; instale depois. Isto evita a desistência no primeiro dia.

| Opção | O que dá para fazer | Limite |
|---|---|---|
| **GitHub Codespaces** — abra qualquer repositório de exemplo do MCP e clique em *Code → Codespaces* | ambiente Linux completo no navegador, com Node e Python; roda Inspector e servidores | cota gratuita mensal por conta; expira |
| **Container pronto**: `docker run --rm -it python:3.12-slim bash`, e dentro dele `pip install "mcp[cli]"` | tudo de Python, isolado, some quando você sai | precisa de Docker instalado |
| **Servidores MCP remotos públicos** já hospedados (ex.: o servidor MCP do próprio site de documentação; conectores de serviços que você já usa) | ver MCP funcionando de verdade como **usuário**, sem escrever nada | você não aprende a escrever servidor |
| **Ler a fita** — o [arquivo 13](13-json-rpc-e-a-camada-base.md) traz requisições e respostas JSON reais, capturadas | entender o protocolo inteiro sem executar nada | nenhuma prática |
| **Repositório `modelcontextprotocol/servers`** no GitHub | ler implementações de referência | leitura só |

Recomendação honesta: se você tem uma máquina onde possa instalar, **instale**.
O ciclo de depuração local é muito melhor. As opções acima são para desbloquear
quem está preso, não para substituir o ambiente.

---

## 13. Rede corporativa: proxy, CA interna, registry espelhado

Esta máquina de referência **está atrás de um proxy corporativo**, então esta seção
foi exercitada de verdade.

### 13.1 Proxy

```bash
export HTTPS_PROXY="http://usuario:senha@proxy.empresa:6060"
export HTTP_PROXY="$HTTPS_PROXY"
export NO_PROXY="localhost,127.0.0.1,::1,.empresa.local"
```
Define o proxy para a sessão atual. Ponha no `~/.bashrc` para persistir.

> **Armadilha real e frequente:** `no_proxy` com **espaços depois das vírgulas**
> (`localhost, 127.0.0.0/8, ::1`) quebra clientes HTTP de Python — eles não fazem
> `strip()` e passam a mandar `localhost` pelo proxy. Sintoma: você sobe um servidor
> MCP em `127.0.0.1:8000` e o seu cliente Python recebe erro de proxy ao falar com o
> **próprio localhost**. **Escreva sem espaços.**

Para o npm, além das variáveis:

```bash
npm config set proxy "$HTTP_PROXY" && npm config set https-proxy "$HTTPS_PROXY"
```

### 13.2 CA interna (TLS com inspeção)

Se a empresa faz inspeção de TLS, os clientes veem um certificado emitido por uma CA
interna e recusam a conexão. Aponte cada runtime para o pacote de CAs da empresa:

```bash
export SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
export NODE_EXTRA_CA_CERTS=/etc/ssl/certs/ca-empresa.pem
export UV_NATIVE_TLS=1
```
`UV_NATIVE_TLS=1` faz o `uv` usar o armazenamento de certificados do sistema
operacional em vez do embutido — é o que resolve o caso corporativo.

Instalar a CA no sistema (Debian/Ubuntu):

```bash
sudo cp ca-empresa.crt /usr/local/share/ca-certificates/ && sudo update-ca-certificates
```

**Nunca** use `NODE_TLS_REJECT_UNAUTHORIZED=0` nem `pip --trusted-host` como solução
permanente: isso desliga a verificação para *todo mundo*, inclusive para um atacante.
Ver [tls](../tls/00-MAPA.md).

### 13.3 Registry espelhado

```bash
npm config set registry https://artifactory.empresa/api/npm/npm-remote/
export UV_DEFAULT_INDEX=https://artifactory.empresa/api/pypi/pypi-remote/simple
```

Verifique que o espelho tem os pacotes do MCP antes de gastar uma tarde:

```bash
npm view @modelcontextprotocol/server version
uv pip download mcp --no-deps -d /tmp/x && ls /tmp/x
```

### 13.4 Firewall

Servidores MCP **stdio não usam rede nenhuma** — são processos filhos. Se a política
da empresa bloqueia tudo, stdio ainda funciona. Só a *instalação* precisa de rede.
Isto é um argumento forte a favor de começar por stdio em ambiente restrito.

---

## 14. Convivência de versões

### 14.1 Python

```bash
uv python install 3.11 3.12 3.13
```
Instala três interpretadores lado a lado.

Por projeto, o arquivo `.python-version` decide:

```bash
echo "3.12" > .python-version
```

```bash
uv run python --version
# esperado: Python 3.12.x
```

### 14.2 Node

```bash
fnm install 20 22 24
```

```bash
echo "22" > .node-version
```
Com `--use-on-cd` no perfil, o `fnm` troca de versão sozinho ao entrar na pasta.

```bash
node --version
# esperado: v22.x.x
```

### 14.3 SDK v1 e v2 na mesma máquina

Não há conflito: cada projeto tem o seu `.venv` / `node_modules`.

- Python: um projeto com `mcp>=1.28,<2`, outro com `mcp>=2` — convivem.
- TypeScript: `@modelcontextprotocol/sdk@1` e `@modelcontextprotocol/server@2` são
  **pacotes com nomes diferentes**; podem até coexistir no mesmo `package.json`
  (útil durante migração).

### 14.4 Dois protocolos na mesma máquina

Um servidor SDK 2.x fala `2026-07-28`. Um host antigo fala `2025-06-18`. Isso **não é
problema de instalação, é de protocolo** — e o SDK trata: o cliente v2 tem
`mode="auto"`, que sonda com `server/discover` e cai para o `initialize` legado.
Detalhes em [17-versionamento](17-versionamento-e-compatibilidade.md).

---

## 15. Reprodutibilidade

Sem isto, "funciona na minha máquina" é garantido.

| Arquivo | Ferramenta | Para quê | Versionar no git? |
|---|---|---|---|
| `uv.lock` | `uv` | trava a árvore exata de dependências Python | **Sim** |
| `.python-version` | `uv` | trava a versão do interpretador | **Sim** |
| `pyproject.toml` | `uv`/pip | declara as dependências | **Sim** |
| `package-lock.json` | npm | trava a árvore npm | **Sim** |
| `.node-version` | `fnm` | trava a versão do Node | **Sim** |
| `.venv/`, `node_modules/` | — | artefatos | **Não** (`.gitignore`) |
| `Dockerfile` | Docker | ambiente inteiro | **Sim** |

Recriar o ambiente exato em outra máquina:

```bash
uv sync --frozen
```
Instala exatamente o que está no `uv.lock`; falha se o lock estiver desatualizado
(em vez de silenciosamente resolver de novo — que é o comportamento que você quer em CI).

```bash
npm ci
```
Equivalente para npm: instala a partir do `package-lock.json`, apaga `node_modules`
antes, e falha se `package.json` e o lock divergirem.

---

## 16. Atualizar com segurança e voltar atrás

```bash
uv self update
```
Atualiza o próprio `uv`.

```bash
uv lock --upgrade-package mcp && uv sync
```
Atualiza **só** o `mcp`, mantendo o resto travado. Depois **rode os seus testes**.

```bash
npm outdated
```
Mostra o que está atrasado, sem mudar nada.

```bash
npm update @modelcontextprotocol/server
```

**Voltar atrás:**

```bash
git checkout uv.lock && uv sync --frozen
```
O lockfile versionado *é* o seu mecanismo de rollback. Este é o motivo prático de
versioná-lo, mais forte do que qualquer argumento teórico.

```bash
npm ci
```
Idem para npm, a partir do `package-lock.json` do commit anterior.

Antes de subir de versão maior (1.x → 2.x), leia o guia de migração do SDK
(<https://py.sdk.modelcontextprotocol.io/v2/migration/>) e **não** faça isso na
sexta-feira.

---

## 17. Desinstalar por completo

Inclui os caches e configurações que ficam para trás e que quase todo tutorial ignora.

### 17.1 SDK Python de um projeto

```bash
uv remove mcp
```

Projeto inteiro:

```bash
rm -rf .venv uv.lock
```

### 17.2 `uv` e tudo que ele guarda

```bash
uv cache clean
```
Limpa o cache de pacotes (pode chegar a vários GB).

```bash
uv python uninstall --all
```
Remove os interpretadores gerenciados pelo `uv`.

```bash
rm -rf ~/.local/bin/uv ~/.local/bin/uvx ~/.local/share/uv ~/.cache/uv ~/.config/uv
```
Remove binários, dados, cache e configuração. Depois tire a linha do PATH do `~/.bashrc`.

### 17.3 Node, npm e caches

```bash
fnm uninstall 22
```

```bash
rm -rf ~/.local/share/fnm ~/.fnm
```

```bash
npm cache clean --force
rm -rf ~/.npm ~/.npmrc
```
`~/.npm/_cacache` costuma passar de 1 GB. `~/.npmrc` guarda proxy, registry **e
tokens de autenticação** — apague de propósito se for devolver a máquina.

O cache do `npx` (onde o Inspector fica):

```bash
rm -rf ~/.npm/_npx
```

### 17.4 Configuração dos hosts

```bash
claude mcp remove meu-servidor
```

Claude Desktop: edite o JSON e apague a entrada em `mcpServers`; depois
**reinicie o aplicativo por completo**.

### 17.5 Docker

```bash
docker image prune -a
docker system df
```
O segundo mostra quanto espaço o Docker ainda ocupa. Imagens de servidores MCP
que você testou ficam lá para sempre até você removê-las.

---

## 18. Solução de problemas — erros literais

| Mensagem literal | Causa provável | Correção |
|---|---|---|
| `command not found: uv` (ou `node`, `npx`) | binário instalado, mas fora do PATH; ou terminal aberto antes da instalação | `source ~/.bashrc` ou abra terminal novo; confira com `ls ~/.local/bin`; ver [§10](#10-path-e-variáveis-de-ambiente) |
| `EACCES: permission denied, mkdir '/usr/lib/node_modules/...'` | `npm install -g` sem permissão | **não** use `sudo`. Use `npx`, ou instale Node com `fnm` (tudo em `$HOME`) |
| `npm ERR! code ENOTFOUND` / `ETIMEDOUT` / `ECONNREFUSED` | proxy não configurado, ou registry inacessível | `npm config set proxy/https-proxy`; ver [§13](#13-rede-corporativa-proxy-ca-interna-registry-espelhado) |
| `npm ERR! engine Unsupported engine ... required: {"node":">=22.19.0"}` | Node velho para o Inspector 2.4.0 | `fnm install 22 && fnm use 22` |
| `SSL: CERTIFICATE_VERIFY_FAILED` / `unable to get local issuer certificate` | inspeção de TLS com CA interna | `UV_NATIVE_TLS=1`, `SSL_CERT_FILE`, `NODE_EXTRA_CA_CERTS`; **nunca** desligar a verificação |
| `ModuleNotFoundError: No module named 'mcp.server.fastmcp'` | código do SDK v1 rodando sob o SDK v2 | `from mcp.server.mcpserver import MCPServer`; ou fixe `mcp<2` |
| `AttributeError: 'CallToolResult' object has no attribute 'structuredContent'. Did you mean: 'structured_content'?` | no SDK Python v2 os campos são `snake_case` no objeto Python (o JSON continua `camelCase`) | use `resultado.structured_content` |
| `error: The requested Python version 3.9 is not available` / `Requires-Python: >=3.10` | Python velho demais para `mcp` 2.x | `uv python install 3.12` |
| **Servidor não aparece no host, sem erro visível** | caminho relativo na config; host não herda o PATH; app não reiniciado | use caminho **absoluto** para o comando e para `--directory`; reinicie o app **por completo** |
| Servidor "conecta e cai" logo depois | seu código escreveu em `stdout` (`print`, `console.log`) e corrompeu a fita JSON-RPC | **jamais escreva em `stdout` num servidor stdio**. Log vai para `stderr` |
| `HTTP 403` + corpo `Invalid Origin header` no servidor HTTP | validação de `Origin` contra DNS rebinding (comportamento correto do servidor) | mande `Origin` permitido, ou omita o cabeçalho em testes com `curl` |
| `{"code":-32020,"message":"mcp-name header does not match ..."}` | POST HTTP sem o cabeçalho `Mcp-Name`, ou com valor diferente do corpo | acrescente `Mcp-Name: <nome da ferramenta>` idêntico a `params.name` |
| `{"code":-32022,"message":"Unsupported protocol version","data":{"supported":[...]}}` | cliente pediu uma revisão que o servidor não fala | use uma das versões listadas em `data.supported` |
| `Method not found` (`-32601`) ao mandar `initialize` para servidor novo | servidor só fala `2026-07-28` (sem handshake); cliente é da era antiga | atualize o cliente, ou use um servidor *dual-era* |

---

## 19. Checklist "ambiente pronto"

Rode uma linha por vez. Se todas passarem, siga para [04 · Como começar](04-como-comecar.md).

```bash
uv --version
```
```bash
uv python list --only-installed
```
```bash
node --version
```
```bash
npm --version
```
```bash
uv run mcp version
```
```bash
uv run python -c "from mcp.server.mcpserver import MCPServer; print('SDK Python ok')"
```
```bash
node -e "const s=require('@modelcontextprotocol/server'); console.log('SDK TS ok', typeof s.McpServer)"
```
```bash
npx -y @modelcontextprotocol/inspector --version
```
```bash
docker run --rm hello-world
```
```bash
claude --version
```

Saídas esperadas nesta máquina, em 01/09/2026:

```
uv 0.12.7
cpython-3.12.14-linux-x86_64-gnu
v24.18.0
12.0.1
MCP version 2.1.1
SDK Python ok
SDK TS ok function
2.4.0
Hello from Docker!
2.1.252 (Claude Code)
```

---

## 20. Autoteste

1. Por que este manual recomenda `uv` em vez de `sudo pip install`? Dê o dano concreto.
2. Qual é a versão mínima de Node — e por que ela é ditada pelo Inspector, não pelo SDK?
3. O que muda entre `@modelcontextprotocol/sdk` e `@modelcontextprotocol/server`?
4. Você editou `~/.bashrc` e `uv` continua "não encontrado" no terminal aberto. Por quê?
5. Seu servidor conecta e cai logo depois. Qual é o suspeito número um?
6. Que arquivos você versiona no git para o ambiente ser reproduzível? Quais não?
7. Como voltar atrás de uma atualização que quebrou o servidor?
8. Por que servidores **stdio** funcionam mesmo com firewall bloqueando tudo?
9. Qual armadilha de `no_proxy` quebra clientes Python falando com o próprio `localhost`?
10. Cite três coisas que ficam para trás quando você "desinstala" o Node.

---

**Anterior:** [02 · Pré-requisitos](02-pre-requisitos.md) · **Próximo:** [04 · Como começar](04-como-comecar.md) · **Índice:** [00-MAPA](00-MAPA.md)

*Todos os comandos e saídas marcados sem ⚠️ foram executados em Ubuntu 22.04.5 LTS,
x86-64, atrás de proxy corporativo, em 01/09/2026. Versões de pacote conferidas em
PyPI e npm na mesma data. Documentação oficial consultada:
[modelcontextprotocol.io/docs/2026-07-28/sdk](https://modelcontextprotocol.io/docs/2026-07-28/sdk),
[modelcontextprotocol.io/docs/2026-07-28/tools/inspector](https://modelcontextprotocol.io/docs/2026-07-28/tools/inspector).*
