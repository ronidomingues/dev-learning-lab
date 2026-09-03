# 03 · Manual de instalação, passo a passo

`Nível: iniciante` · `Pesquisado na web e testado em 12/08/2026`

> **Leia isto primeiro:** você pode começar **sem instalar nada**. Pule para a
> [seção 10](#10-alternativa-sem-instalar-nada) se quiser sua primeira luz verde em cinco
> minutos, no navegador. Instalar dá para fazer depois — e é o que evita desistência no
> primeiro dia.

**Ambiente onde este manual foi testado:** Ubuntu 22.04.5 LTS, x86-64, com
Python 3.10.12, Node.js v24.18.0, npm 12.0.1, pytest 9.1.1, coverage 7.15.4,
Hypothesis 6.165.3, Vitest 4.1.10. Os comandos de macOS e Windows vêm da documentação
oficial de cada projeto, consultada em 12/08/2026, e **não** foram executados nesta
máquina — isso está declarado onde importa.

---

## Índice

1. [O que precisa ser instalado, e por quê](#1-o-que-precisa-ser-instalado-e-por-quê)
2. [Trilha Python — Linux](#2-trilha-python--linux)
3. [Trilha Python — macOS](#3-trilha-python--macos)
4. [Trilha Python — Windows](#4-trilha-python--windows)
5. [Trilha JavaScript — Linux, macOS e Windows](#5-trilha-javascript)
6. [Editor e extensões](#6-editor-e-extensões)
7. [PATH, permissões e os erros que vêm daí](#7-path-permissões-e-os-erros-que-vêm-daí)
8. [Rede corporativa: proxy, certificado e registry](#8-rede-corporativa)
9. [Conviver com várias versões · reprodutibilidade · atualizar · desinstalar](#9-versões-reprodutibilidade-atualizar-desinstalar)
10. [Alternativa sem instalar nada](#10-alternativa-sem-instalar-nada)
11. [Solução de problemas — tabela de erros literais](#11-solução-de-problemas)
12. [Checklist "ambiente pronto"](#12-checklist-ambiente-pronto)

---

## 1. O que precisa ser instalado, e por quê

Um manual que instala só a ferramenta principal não serve. Segue **tudo** o que entra em
jogo, com o motivo.

### Trilha Python

| Componente | Para quê | Obrigatório? |
|---|---|---|
| **Python 3.10+** | rodar o código e os testes | sim |
| **`venv`** (módulo padrão) | ambiente isolado por projeto | sim, na prática |
| **`pip`** ou **`uv`** | instalar pacotes | sim (um dos dois) |
| **`pytest`** | o corredor de testes | sim |
| **`pytest-cov`** | medir cobertura | quase sempre |
| **`hypothesis`** | testes de propriedades | só no cap. 60 e no projeto-modelo |
| **Editor + extensão Python** | rodar teste com um clique, ver o verde/vermelho | não, mas muda a vida |
| **Git** | versionar e usar CI | não para este material |

### Trilha JavaScript

| Componente | Para quê | Obrigatório? |
|---|---|---|
| **Node.js 20+** (24 LTS recomendado) | rodar o código e os testes | sim |
| **`node:test`** | o corredor de testes | **já vem no Node** — nada a instalar |
| **`npm`** | instalar pacotes | vem junto com o Node |
| **Vitest** ou **Jest** | corredor alternativo, com `expect` e mocks mais ricos | opcional |
| **Editor + extensão** | idem | não, mas muda a vida |

> Em 12/08/2026, **Node.js 24 é a linha LTS ativa** (suporte até 30/04/2028) e **Node.js 26
> é a Current**, com previsão de virar LTS em outubro de 2026. Para este material, use o 24.
> A partir de outubro de 2026 o Node passa a fazer **um** *major* por ano, com o número
> alinhado ao calendário e **toda** versão virando LTS.
> *(Fontes ao final.)*

---

## 2. Trilha Python — Linux

### 2.1 Verifique o que já existe

```bash
python3 --version
```

```
# esperado: Python 3.10.12 (ou superior)
```

Se a saída for **3.10 ou maior**, pule para o [passo 2.4](#24-crie-o-ambiente-virtual).
Se der `command not found: python3` ou uma versão 3.9 ou menor, siga adiante.

### 2.2 Instalar o Python — família Debian/Ubuntu

```bash
sudo apt update
```
Atualiza a lista de pacotes disponíveis. Sem isso, o `apt` pode não achar a versão nova.

```bash
sudo apt install -y python3 python3-venv python3-pip
```
Instala o interpretador, o módulo de ambiente virtual e o instalador de pacotes.
**Os três**: no Debian/Ubuntu, `python3-venv` vem em pacote separado, e essa é a causa
número 1 de erro no primeiro dia.

Verifique:

```bash
python3 --version && python3 -m venv --help > /dev/null && echo "venv ok"
```
```
# esperado:
# Python 3.10.12
# venv ok
```

Se `venv` reclamar, instale o pacote com a versão no nome:
`sudo apt install python3.10-venv` (troque pelo seu número).

### 2.3 Instalar o Python — família Fedora/RHEL

```bash
sudo dnf install -y python3 python3-pip
```
No Fedora/RHEL o `venv` já vem dentro do pacote `python3`.

```bash
python3 --version
```
```
# esperado: Python 3.13.x no Fedora 42+, 3.9 no RHEL 9 (ver aviso abaixo)
```

> **Aviso RHEL/CentOS/Rocky 9:** o Python do sistema é o 3.9, **abaixo do mínimo** deste
> material. Instale um mais novo em paralelo, sem substituir o do sistema:
> ```bash
> sudo dnf install -y python3.12
> python3.12 --version
> ```
> E use `python3.12` no lugar de `python3` daqui para frente. **Nunca** troque o
> `/usr/bin/python3` do RHEL: metade das ferramentas do sistema (`dnf` incluso) depende dele.

### 2.4 Crie o ambiente virtual

Vá para a pasta do projeto (aqui, o projeto-modelo):

```bash
cd testes-automatizados/07-projeto-modelo/python
```

```bash
python3 -m venv .venv
```
Cria uma pasta `.venv/` com uma cópia isolada do Python e do pip. Tudo o que você instalar
daqui em diante fica **dentro dela**, não no sistema.

```bash
source .venv/bin/activate
```
Ativa o ambiente. Seu prompt passa a mostrar `(.venv)` na frente.

Verifique que está mesmo no ambiente virtual:

```bash
which python
```
```
# esperado: .../07-projeto-modelo/python/.venv/bin/python
# se aparecer /usr/bin/python, a ativação NÃO funcionou — veja a seção 11
```

### 2.5 Instale o pytest

```bash
pip install pytest pytest-cov hypothesis
```
`pytest` é o corredor; `pytest-cov` mede cobertura; `hypothesis` faz testes de propriedades.

```bash
pytest --version
```
```
# esperado: pytest 9.1.1   (qualquer 8.x ou 9.x serve)
```

Se der `command not found: pytest` com o ambiente ativado, use `python -m pytest` — funciona
sempre, e é o comando mais à prova de PATH quebrado que existe.

### 2.6 Alternativa moderna: `uv` no lugar de `venv` + `pip`

`uv` é um gerenciador escrito em Rust, da Astral (mesmos autores do Ruff). Ele cria o
ambiente, instala pacotes e até **baixa versões do Python** — de 8 a 100 vezes mais rápido
que o `pip`, dependendo do caso.

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```
Baixa e instala o `uv` no seu diretório de usuário (`~/.local/bin`), sem `sudo`.

> Ler um script da internet antes de executá-lo é bom hábito:
> `curl -LsSf https://astral.sh/uv/install.sh | less`

```bash
exec $SHELL -l && uv --version
```
Reabre o shell para o PATH pegar, e confere.

Com `uv`, o ciclo inteiro vira:

```bash
uv venv                       # cria .venv
uv pip install pytest pytest-cov hypothesis
uv run pytest                 # roda sem precisar ativar nada
```

**Recomendação, declarada como opinião:** para **aprender**, use `venv` + `pip` — são o
padrão que você vai encontrar em toda documentação e em todo projeto antigo. Para
**trabalhar** num projeto novo em 2026, `uv` é a escolha melhor: mais rápido, com lockfile
universal e gerenciamento de versão do Python embutido. Os dois convivem sem conflito.

### 2.7 Rode a suíte do projeto-modelo

```bash
pytest -q
```
```
# esperado:
# ........................................................................ [ 75%]
# ..............................................                           [100%]
# 190 passed in 3.05s
```

Se você viu isso, seu ambiente Python está **pronto**. Vá para
[04-como-comecar.md](04-como-comecar.md).

---

## 3. Trilha Python — macOS

### 3.1 O Python que já vem no macOS não serve

O macOS traz um Python de sistema em `/usr/bin/python3`. A Apple **desaconselha** usá-lo
para desenvolvimento: a versão é antiga, muda sem aviso em atualizações do sistema, e
instalar pacotes nele pode quebrar ferramentas do próprio macOS.

Instale um Python próprio. Duas formas, ambas boas:

### 3.2 Opção A — Homebrew (recomendada)

Se você ainda não tem o Homebrew:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

**Apple Silicon (M1/M2/M3/M4)**: o Homebrew instala em `/opt/homebrew`, e o instalador
imprime duas linhas para você colar no fim — elas ajustam o PATH. **Não pule essas linhas**,
senão o `brew` "não existe" na próxima vez que abrir o terminal.

**Intel**: instala em `/usr/local`, que já costuma estar no PATH.

```bash
brew install python@3.13
```

```bash
python3 --version
```
```
# esperado: Python 3.13.x
```

### 3.3 Opção B — instalador oficial

Baixe o `.pkg` de [python.org/downloads](https://www.python.org/downloads/) e execute.
Em 12/08/2026, a versão estável mais recente é a **3.14.7** (lançada em 05/08/2026).

O instalador oficial cria um atalho `Install Certificates.command` dentro de
`/Applications/Python 3.x/`. **Execute-o.** Sem isso, o Python do macOS não valida
certificados HTTPS e todo `pip install` falha com `SSL: CERTIFICATE_VERIFY_FAILED`.

### 3.4 O resto é igual ao Linux

```bash
cd testes-automatizados/07-projeto-modelo/python
python3 -m venv .venv
source .venv/bin/activate
pip install pytest pytest-cov hypothesis
pytest --version
```
```
# esperado: pytest 9.1.1
```

> **Não testado nesta máquina.** Os comandos vêm da documentação do Homebrew e do
> python.org, consultadas em 12/08/2026.

---

## 4. Trilha Python — Windows

### 4.1 Escolha o caminho: WSL2 ou nativo

| | WSL2 (recomendado) | Windows nativo |
|---|---|---|
| O que é | um Linux completo rodando dentro do Windows | Python compilado para Windows |
| Comandos deste material | funcionam **exatamente** como escritos | precisam de tradução (`source` → `Activate.ps1`) |
| Compatibilidade com CI | idêntica ao servidor (que roda Linux) | pode divergir: fim de linha, separador de caminho, sensibilidade a maiúsculas |
| Velocidade de I/O | ruim se o projeto estiver em `/mnt/c/...` | boa |
| Integração com editor | VS Code tem suporte de primeira | nativa |

**Recomendação:** use **WSL2**, e mantenha os projetos dentro do sistema de arquivos do
Linux (`~/projetos`), **não** em `/mnt/c/`. O motivo do desempenho é concreto: acessar
`/mnt/c` atravessa uma camada de tradução (9P/virtio-9p) e fica 5 a 10 vezes mais lento —
uma suíte de testes que lê muitos arquivos sente isso na hora.

### 4.2 Instalar o WSL2

No PowerShell **como administrador**:

```powershell
wsl --install -d Ubuntu
```
Instala o WSL2 com Ubuntu. Reinicie quando pedir; na primeira abertura, ele pede um usuário
e senha do Linux (que não têm relação com sua conta Windows).

```powershell
wsl --status
```
```
# esperado: Versão padrão: 2
```

Depois disso, abra o Ubuntu e **siga a seção 2 deste manual, sem nenhuma alteração**.

### 4.3 Windows nativo — instalar o Python

Opção A, recomendada, pelo gerenciador de pacotes da Microsoft:

```powershell
winget install --id Python.Python.3.13 -e
```

Opção B, instalador oficial de [python.org](https://www.python.org/downloads/windows/):
**marque a caixa "Add python.exe to PATH"** na primeira tela. Se você esquecer, o Windows
vai responder `Python não foi encontrado` para sempre — e a correção está na seção 11.

Feche e **reabra** o PowerShell (o PATH só é lido na abertura) e verifique:

```powershell
python --version
```
```
# esperado: Python 3.13.x
```

> No Windows o comando é `python`, não `python3`. Existe um alias `python3` desde o
> Windows 10, mas ele às vezes abre a Microsoft Store em vez do Python — é a "app execution
> alias" da Store. Se isso acontecer: Configurações → Aplicativos → Aliases de execução de
> aplicativo → desligue `python.exe` e `python3.exe`.

### 4.4 Windows nativo — ambiente virtual e pytest

```powershell
cd testes-automatizados\07-projeto-modelo\python
python -m venv .venv
```

```powershell
.venv\Scripts\Activate.ps1
```
Ativa o ambiente. **Se der erro de política de execução**, rode uma vez:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```
Isso libera scripts locais só para o seu usuário. É a configuração recomendada pela
Microsoft para desenvolvimento; não mexe na máquina inteira.

No **CMD** clássico, o comando é outro: `.venv\Scripts\activate.bat`.

```powershell
pip install pytest pytest-cov hypothesis
pytest --version
```
```
# esperado: pytest 9.1.1
```

> **Não testado nesta máquina.** Comandos verificados contra a documentação da Microsoft e
> do Python, em 12/08/2026.

---

## 5. Trilha JavaScript

Boa notícia: **o corredor de testes já vem no Node**. Desde o Node 20 o módulo `node:test`
é estável, e desde o Node 22 ele traz mocks, cobertura e modo *watch*. Instalar o Node é
tudo o que você precisa fazer.

### 5.1 Verifique o que já existe

```bash
node --version
```
```
# esperado: v24.18.0 (qualquer v20+ serve; v24 é a LTS em 12/08/2026)
```

### 5.2 Método recomendado: gerenciador de versões

**Por que não instalar pelo `apt`/`brew`/instalador?** Porque mais cedo do que você imagina
vai aparecer um projeto que precisa de outra versão do Node. Um gerenciador de versões
resolve isso em dois segundos; a instalação global exige desinstalar e reinstalar.

**Linux e macOS — `nvm`:**

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
```
Instala o `nvm` em `~/.nvm` e acrescenta três linhas ao seu `~/.bashrc` ou `~/.zshrc`.

```bash
exec $SHELL -l
```
Reabre o shell para o `nvm` existir. **Este passo é o que quase todo mundo esquece**, e o
sintoma é `nvm: command not found` logo após uma instalação bem-sucedida.

```bash
nvm install 24
```
Baixa e ativa o Node 24 LTS.

```bash
node --version && npm --version
```
```
# esperado:
# v24.18.0
# 12.0.1
```

**Alternativa mais rápida, `fnm`** (escrito em Rust, compatível com `.nvmrc`):

```bash
curl -fsSL https://fnm.vercel.app/install | bash
exec $SHELL -l
fnm install 24 && fnm use 24
```

**Windows** — `nvm` não funciona nativamente (é um script de shell). Três saídas:

```powershell
# A) dentro do WSL2 — use os comandos de Linux acima (recomendado)

# B) fnm, que tem binário nativo para Windows
winget install Schniz.fnm

# C) instalador oficial, sem gerenciamento de versões
winget install OpenJS.NodeJS.LTS
```

### 5.3 Método alternativo: pacote do sistema

Funciona, mas prende você a uma versão.

```bash
# Debian/Ubuntu — o node do apt costuma estar MUITO atrasado.
# Use o repositório oficial da NodeSource:
curl -fsSL https://deb.nodesource.com/setup_24.x | sudo -E bash -
sudo apt install -y nodejs
```

```bash
# Fedora
sudo dnf install -y nodejs

# macOS
brew install node@24
```

### 5.4 Rode a suíte do projeto-modelo — sem instalar nada mais

```bash
cd testes-automatizados/07-projeto-modelo/javascript
node --test
```
```
# esperado (final da saída):
# ℹ tests 245
# ℹ pass 245
# ℹ fail 0
```

Pronto. Sem `npm install`, sem `node_modules`, sem esperar download. Este é o argumento mais
forte do `node:test`.

### 5.5 Opcional: Vitest

Só se você quiser a experiência `expect(...)`, mocks mais ricos e interface web.

```bash
npm install -D vitest
```
```
# esperado: added 44 packages, and audited 45 packages in 28s
```

```bash
npx vitest run
```
```
# esperado:
#  RUN  v4.1.10
#  Test Files  2 passed (2)
#       Tests  52 passed (52)
```

**Vitest ou Jest, em 12/08/2026?** Para projeto novo: **Vitest**. Ele é mais rápido (as
comparações públicas de 2026 falam em ~2× no arranque a frio e bem mais no modo *watch*),
tem ESM e TypeScript nativos sem Babel, e é o padrão recomendado por Nuxt, SvelteKit, Astro
e pelas ferramentas atuais do Angular. **Jest 30** continua defensável em base CommonJS
legada, em monorepo corporativo grande com ecossistema fechado, e em **React Native** — onde
o Vitest não tem suporte. Comparação completa em
[17-javascript-vitest-jest.md](17-javascript-vitest-jest.md).

### 5.6 Opcional: Playwright (testes de navegador)

Só necessário a partir de [18-integracao-e-e2e.md](18-integracao-e-e2e.md).

```bash
npm init playwright@latest
```
Cria a configuração e baixa os navegadores.

```bash
npx playwright --version
```
```
# esperado: Version 1.62.1
```

> **Atenção ao espaço em disco:** o Playwright baixa Chromium, Firefox e WebKit completos —
> algo entre 500 MB e 1 GB. No Linux ele também instala dependências de sistema; se falhar,
> rode `npx playwright install-deps` (pede `sudo`).

---

## 6. Editor e extensões

Nada aqui é obrigatório, mas a diferença prática é grande: rodar o teste sob o cursor com um
atalho, e ver verde/vermelho na margem do arquivo, muda o ritmo de trabalho.

### VS Code

```bash
# Linux
sudo snap install code --classic
# ou baixe o .deb/.rpm de https://code.visualstudio.com/

# macOS
brew install --cask visual-studio-code

# Windows
winget install Microsoft.VisualStudioCode
```

Extensões a instalar (`Ctrl+Shift+X`, buscar pelo identificador):

| Identificador | Para quê | Trilha |
|---|---|---|
| `ms-python.python` | rodar/depurar testes pytest pela interface | Python |
| `charliermarsh.ruff` | formatação e lint rápidos | Python |
| `vitest.explorer` | painel de testes do Vitest | JavaScript |
| `ms-vscode.vscode-typescript-next` | tipos melhores para JS/TS | JavaScript |
| `ms-vscode-remote.remote-wsl` | trabalhar dentro do WSL2 | Windows |

Configuração mínima do pytest no VS Code: abra a paleta (`Ctrl+Shift+P`) →
`Python: Configure Tests` → `pytest` → pasta `tests`. O painel de testes (`Ctrl+Shift+T`)
passa a listar tudo.

### Alternativas

- **PyCharm Community** (grátis, Python): integração com pytest de primeira linha.
- **WebStorm** (pago; grátis para uso não comercial desde 2024): idem para JavaScript.
- **Neovim + `neotest`**: para quem já vive no terminal.

---

## 7. PATH, permissões e os erros que vêm daí

### 7.1 O que é o PATH, e por que "não pegou"

`PATH` é uma lista de pastas que o sistema percorre quando você digita um comando. Se o
`pytest` está em `~/.local/bin` e essa pasta não está no PATH, o terminal responde
`command not found` — mesmo com o programa instalado e funcionando.

**Ver o PATH:**

```bash
echo $PATH | tr ':' '\n'          # Linux/macOS
```
```powershell
$env:PATH -split ';'              # Windows PowerShell
```

**Por que a mudança "não pegou":** o PATH é lido **quando o terminal abre**. Editar o
`~/.bashrc` não afeta o terminal já aberto. Sempre faça uma destas coisas:

```bash
source ~/.bashrc     # recarrega no terminal atual
exec $SHELL -l       # ou reabra o shell
```

**Qual arquivo editar:**

| Shell / SO | Arquivo |
|---|---|
| bash (Linux) | `~/.bashrc` |
| bash (macOS, login shell) | `~/.bash_profile` |
| zsh (padrão no macOS desde 2019) | `~/.zshrc` |
| fish | `~/.config/fish/config.fish` |
| PowerShell | `$PROFILE` (rode `notepad $PROFILE`) |

Descubra qual shell você usa: `echo $SHELL`.

Acrescentar uma pasta ao PATH (exemplo com `~/.local/bin`):

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc && source ~/.bashrc
```

### 7.2 Permissões: por que `sudo pip install` estraga a máquina

Você vai encontrar na internet a sugestão de resolver erro de permissão com `sudo`.
**Não faça.** Os motivos, em ordem de gravidade:

1. **Você mistura pacotes seus com pacotes do sistema.** No Debian/Ubuntu/Fedora, o gerenciador
   de pacotes do SO instala bibliotecas Python em `/usr/lib/python3/dist-packages`. Um
   `sudo pip install` grava em cima. Quando o `apt` atualizar aquele pacote, os dois brigam —
   e o sintoma é uma ferramenta do sistema (às vezes o próprio `apt`) parando de funcionar.
2. **Um `setup.py` roda código arbitrário na instalação.** Com `sudo`, esse código roda como
   root.
3. **Fica impossível ter dois projetos com versões diferentes da mesma biblioteca.**

O Python moderno **impede** isso por padrão: desde a PEP 668 (adotada no Debian 12, Ubuntu
23.04, Fedora 38 em diante), `pip install` fora de um ambiente virtual devolve
`error: externally-managed-environment`. Isso é uma proteção, não um obstáculo.

**O caminho certo, em ordem de preferência:**

```bash
python3 -m venv .venv && source .venv/bin/activate && pip install pytest   # projeto
pipx install pytest       # ferramenta de linha de comando, isolada e global
pip install --user pytest # só se as duas acima não servirem
```

Nunca: `sudo pip install`.

### 7.3 O mesmo vale para o npm

`sudo npm install -g` tem os mesmos problemas, mais um: pacotes npm executam scripts
`postinstall` na instalação, também como root.

**O caminho certo:** use `nvm`/`fnm`. Eles instalam o Node dentro da sua pasta de usuário,
então `npm install -g` nunca precisa de `sudo`. Se você já instalou o Node com `sudo` e está
preso nisso:

```bash
mkdir -p ~/.npm-global
npm config set prefix ~/.npm-global
echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.bashrc && source ~/.bashrc
```

Melhor ainda: para rodar uma ferramenta uma vez, `npx <ferramenta>` não instala nada
globalmente.

---

## 8. Rede corporativa

Se você está numa máquina de empresa, provavelmente há um proxy e um certificado interno
entre você e a internet. Sintomas típicos: `SSLError`, `CERTIFICATE_VERIFY_FAILED`,
`ETIMEDOUT`, ou download que fica parado em 0 %.

### 8.1 Proxy

```bash
export HTTP_PROXY="http://usuario:senha@proxy.empresa.com:8080"
export HTTPS_PROXY="$HTTP_PROXY"
export NO_PROXY="localhost,127.0.0.1,.empresa.com"
```
Para valer em todo terminal, ponha essas linhas no `~/.bashrc`.

> **Cuidado:** senha em `~/.bashrc` fica em texto puro e vai parar no histórico do shell.
> Se o proxy exigir autenticação, prefira a configuração por ferramenta (abaixo) ou um
> gerenciador de credenciais.

```powershell
# Windows PowerShell
$env:HTTP_PROXY  = "http://proxy.empresa.com:8080"
$env:HTTPS_PROXY = $env:HTTP_PROXY
```

Por ferramenta:

```bash
pip config set global.proxy http://proxy.empresa.com:8080
npm config set proxy http://proxy.empresa.com:8080
npm config set https-proxy http://proxy.empresa.com:8080
```

### 8.2 Certificado interno (TLS inspection)

Empresas que inspecionam HTTPS substituem o certificado dos sites por um próprio. Suas
ferramentas não confiam nele até você dizer que pode.

Peça ao time de infraestrutura o arquivo `.pem`/`.crt` da autoridade interna e:

```bash
export REQUESTS_CA_BUNDLE=/caminho/empresa-ca.pem   # requests, e boa parte do ecossistema
export SSL_CERT_FILE=/caminho/empresa-ca.pem        # OpenSSL/urllib
pip config set global.cert /caminho/empresa-ca.pem
npm config set cafile /caminho/empresa-ca.pem
```

> **Nunca** use `npm config set strict-ssl false` nem `pip --trusted-host` como solução
> permanente. Isso desliga a verificação e transforma qualquer rede hostil num vetor de
> ataque de cadeia de suprimentos. Use só para diagnosticar, e desfaça em seguida.

### 8.3 Registry espelhado

Muitas empresas mantêm um espelho interno (Artifactory, Nexus, Verdaccio):

```bash
pip config set global.index-url https://nexus.empresa.com/repository/pypi/simple
npm config set registry https://nexus.empresa.com/repository/npm-group/
```

Voltar ao padrão:

```bash
pip config unset global.index-url
npm config delete registry
```

---

## 9. Versões, reprodutibilidade, atualizar, desinstalar

### 9.1 Conviver com várias versões

**Python:**

```bash
# com uv (mais simples): baixa e usa a versão pedida
uv python install 3.12 3.13
uv venv --python 3.12

# com pyenv (clássico)
curl -fsSL https://pyenv.run | bash
pyenv install 3.13.5
pyenv local 3.13.5        # cria .python-version nesta pasta
```

**Node:**

```bash
nvm install 20 && nvm install 24
nvm use 20                 # nesta sessão
nvm alias default 24       # padrão nas próximas
echo "24" > .nvmrc         # e então basta `nvm use` na pasta
```

Com `fnm` e a opção `--use-on-cd`, entrar na pasta já troca a versão automaticamente.

### 9.2 Reprodutibilidade — "na minha máquina funciona"

Fixar versões é o que faz o teste que passou hoje passar no ano que vem e no servidor de CI.

| Arquivo | Trilha | O que fixa | Commitar? |
|---|---|---|---|
| `.python-version` | Python | versão do interpretador (pyenv/uv) | sim |
| `pyproject.toml` | Python | faixas de dependência (`pytest>=8`) | sim |
| `uv.lock` / `requirements.txt` | Python | versões **exatas** | sim |
| `.nvmrc` | JavaScript | versão do Node | sim |
| `package.json` | JavaScript | faixas (`^4.1.10`) | sim |
| `package-lock.json` | JavaScript | versões exatas de tudo | **sim** |
| `.tool-versions` | ambos | versões para `asdf`/`mise` | sim |
| `node_modules/`, `.venv/` | ambos | — | **não** (`.gitignore`) |

Gerar o congelamento exato:

```bash
pip freeze > requirements.txt      # pip
uv lock                            # uv
npm ci                             # instala EXATAMENTE o lock, e falha se divergir
```

`npm ci` (e não `npm install`) é o comando certo em CI: ele apaga `node_modules`, instala o
que está no lock, e **falha** se o `package.json` e o lock discordarem — o que impede a
famosa quebra silenciosa em produção.

### 9.3 Atualizar com segurança

```bash
pip install --upgrade pytest            # Python
npm update vitest                       # JavaScript, dentro da faixa do package.json
npm install -D vitest@latest            # muda a faixa, para major novo
nvm install 26 --reinstall-packages-from=24   # Node, trazendo os globais
```

Ordem recomendada: **atualize uma coisa por vez, rode a suíte, commite.** Atualizar cinco
coisas juntas e ver 12 testes vermelhos não diz nada sobre a causa.

### 9.4 Voltar atrás

```bash
pip install "pytest==8.4.2"
npm install -D vitest@3.2.4
nvm use 22
```

Se você tem lockfile commitado, voltar atrás é `git checkout` do lock + `npm ci` (ou
`uv sync`). É esse o motivo de commitar lock.

### 9.5 Desinstalar por completo

Inclui os caches e configurações que ficam para trás — a parte que quase todo tutorial omite.

**Python:**

```bash
deactivate 2>/dev/null            # sair do venv, se estiver dentro
rm -rf .venv                      # o ambiente do projeto
pip uninstall -y pytest pytest-cov hypothesis
rm -rf ~/.cache/pip               # cache de downloads (pode ter centenas de MB)
rm -rf ~/.cache/uv                # se usou uv
rm -rf ~/.pyenv                   # se usou pyenv (e tire as linhas do ~/.bashrc)
```

Restos que o projeto deixa e ninguém lembra:

```bash
rm -rf .pytest_cache .hypothesis htmlcov .coverage *.egg-info
find . -name __pycache__ -type d -exec rm -rf {} +
```

**JavaScript:**

```bash
rm -rf node_modules package-lock.json
npm cache clean --force
rm -rf ~/.npm                     # cache global do npm
rm -rf ~/.nvm                     # se usou nvm (e tire as 3 linhas do ~/.bashrc)
npx playwright uninstall --all    # os navegadores, se instalou Playwright
rm -rf ~/.cache/ms-playwright
```

**Windows:** desinstale pelo Painel de Controle ou `winget uninstall`, e apague à mão
`%LOCALAPPDATA%\pip\Cache`, `%APPDATA%\npm-cache` e `%LOCALAPPDATA%\ms-playwright`.

---

## 10. Alternativa sem instalar nada

Todas testadas quanto a existirem e funcionarem em 12/08/2026. Use **antes** de instalar
qualquer coisa se você quiser começar hoje.

| Onde | Trilha | Precisa de conta? | Bom para |
|---|---|---|---|
| [pythontutor.com](https://pythontutor.com/) | Python | não | ver o código executar passo a passo (sem pytest) |
| [Google Colab](https://colab.research.google.com/) | Python | conta Google | notebook com `!pip install pytest` e `!pytest` funcionando |
| [replit.com](https://replit.com/) | ambas | sim | ambiente completo no navegador; camada gratuita limitada |
| [StackBlitz](https://stackblitz.com/) | JavaScript | não para começar | roda **Node de verdade** no navegador (WebContainers); `node --test` funciona |
| [CodeSandbox](https://codesandbox.io/) | JavaScript | sim | idem, com mais recursos de time |
| [GitHub Codespaces](https://github.com/features/codespaces) | ambas | conta GitHub | VS Code completo na nuvem; **60 h/mês grátis** no plano Free (verifique o limite atual) |
| [Gitpod](https://gitpod.io/) | ambas | sim | alternativa ao Codespaces |

**O caminho mais curto até a primeira luz verde, sem instalar nada:**

1. Abra [stackblitz.com/fork/node](https://stackblitz.com/fork/node).
2. Crie um arquivo `soma.test.js` com:

```javascript
import assert from 'node:assert/strict';
import { test } from 'node:test';

test('dois mais dois são quatro', () => {
  assert.equal(2 + 2, 4);
});
```

3. No terminal embutido: `node --test`.

Verde em menos de dois minutos, sem instalar nada. Depois volte e instale com calma.

**Container pronto, se você já tem Docker:**

```bash
docker run --rm -it -v "$PWD":/app -w /app python:3.13-slim \
  sh -c "pip install -q pytest && pytest"
```
```bash
docker run --rm -it -v "$PWD":/app -w /app node:24-alpine node --test
```

---

## 11. Solução de problemas

Erros literais, em ordem de frequência.

### 11.1 Python

| Mensagem | Causa provável | Correção |
|---|---|---|
| `command not found: python3` (Linux/macOS) | Python não instalado, ou não está no PATH | `sudo apt install python3` · ver seção 7.1 |
| `Python não foi encontrado; execute sem argumentos para instalar da Microsoft Store` | alias da Store ativo, Python não instalado ou sem PATH | desligue os aliases (seção 4.3) e reinstale marcando "Add to PATH" |
| `error: externally-managed-environment` | `pip install` fora de venv, em SO com PEP 668 | crie o venv: `python3 -m venv .venv && source .venv/bin/activate` |
| `The virtual environment was not created successfully because ensurepip is not available` | falta o pacote `python3-venv` (Debian/Ubuntu) | `sudo apt install python3-venv` (ou `python3.X-venv`) |
| `command not found: pytest` (com venv ativo) | o `bin/` do venv não entrou no PATH, ou a ativação falhou | use `python -m pytest`; confira `which python` |
| `ModuleNotFoundError: No module named 'assinaturas'` | o pacote não foi instalado nem está no `sys.path` | `pip install -e .` na raiz do projeto, ou `PYTHONPATH=. pytest` |
| `ImportError: attempted relative import with no known parent package` | rodou `python arquivo.py` num módulo com import relativo | rode como módulo: `python -m pacote.arquivo` |
| `E   fixture 'xyz' not found` | fixture com nome errado, ou fora do `conftest.py` visível | confira o nome; `pytest --fixtures` lista todas |
| `PytestUnknownMarkWarning: Unknown pytest.mark.xyz` | marcador não declarado no `pyproject.toml` | declare em `markers = [...]` e ative `--strict-markers` |
| `SSL: CERTIFICATE_VERIFY_FAILED` | certificados não instalados (macOS) ou proxy corporativo | rode `Install Certificates.command`; ver seção 8.2 |
| `.venv\Scripts\Activate.ps1 não pode ser carregado porque a execução de scripts foi desabilitada` | política de execução do PowerShell | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |
| `Permission denied: '/usr/lib/python3/...'` | tentou instalar no Python do sistema | use venv; **não** use `sudo` (seção 7.2) |
| `collected 0 items` | o pytest não achou nada com o padrão de nome | arquivos `test_*.py`, funções `test_*`, classes `Test*` sem `__init__` |

### 11.2 JavaScript / Node

| Mensagem | Causa provável | Correção |
|---|---|---|
| `nvm: command not found` (logo após instalar) | o shell não foi reaberto | `exec $SHELL -l` ou `source ~/.bashrc` |
| `SyntaxError: Cannot use import statement outside a module` | arquivo ESM sem `"type": "module"` | acrescente `"type": "module"` ao `package.json`, ou use extensão `.mjs` |
| `Error [ERR_REQUIRE_ESM]: require() of ES Module ...` | mistura de CommonJS com ESM | padronize no ESM; se não der, use `await import()` |
| `Cannot find module 'node:sqlite'` | Node abaixo de 22.5 | `nvm install 24` |
| `Cannot find module './x'` (com ESM) | ESM exige a **extensão** no import | `import x from './x.js'`, não `'./x'` |
| `node: bad option: --test` | Node abaixo de 18 | atualize o Node |
| `EACCES: permission denied, access '/usr/lib/node_modules'` | `npm install -g` sem permissão | use `nvm`/`fnm`, ou mude o prefix (seção 7.3) |
| `npm ERR! code ERESOLVE` | conflito de dependências entre pacotes | `npm install --legacy-peer-deps` como paliativo; a correção é alinhar as versões |
| `npm ERR! Cannot read properties of null (reading 'matches')` | `node_modules` ou lock corrompidos | `rm -rf node_modules package-lock.json && npm install` |
| `unable to get local issuer certificate` | certificado corporativo | `npm config set cafile /caminho/ca.pem` (seção 8.2) |
| `browserType.launch: Executable doesn't exist` | Playwright sem os navegadores baixados | `npx playwright install` |
| `Host system is missing dependencies to run browsers` | falta biblioteca de sistema (Linux) | `npx playwright install-deps` |
| `ℹ tests 0` | nenhum arquivo casou com o padrão | por padrão o `node:test` procura `*.test.js`, `*-test.js`, `test.js` e o que estiver em `test/` |

---

## 12. Checklist "ambiente pronto"

Rode um comando por linha. Todos devem responder sem erro **antes** de você seguir para
[04-como-comecar.md](04-como-comecar.md).

### Python

```bash
python3 --version                       # ≥ 3.10
which python                            # deve apontar para dentro de .venv
pip --version                           # idem
pytest --version                        # ≥ 8.0
python -c "import hypothesis; print(hypothesis.__version__)"
cd testes-automatizados/07-projeto-modelo/python && pytest -q
```
```
# esperado na última linha: 190 passed
```

### JavaScript

```bash
node --version                          # ≥ v20, idealmente v24
npm --version
node --test --help > /dev/null && echo "node:test ok"
cd testes-automatizados/07-projeto-modelo/javascript && node --test
```
```
# esperado: ℹ pass 245 / ℹ fail 0
```

### Opcionais

```bash
npx vitest --version                    # 4.x, se instalou
npx playwright --version                # 1.62.x, se instalou
git --version
code --version
```

---

## Autoteste

1. Por que `sudo pip install` é uma má ideia? Dê dois motivos distintos.
2. O que é `error: externally-managed-environment` e qual a correção correta?
3. Você editou o `~/.bashrc` e o comando continua "não encontrado". O que falta?
4. Por que a trilha JavaScript não precisa instalar corredor de testes?
5. No Windows, quando escolher WSL2 e quando escolher o Python nativo?
6. Qual a diferença entre `npm install` e `npm ci`, e onde cada um deve ser usado?
7. Cite três arquivos que se deve commitar para garantir reprodutibilidade, e dois que não.
8. Você precisa começar hoje e não pode instalar nada. Qual é o caminho mais curto até um teste verde?
9. Por que `.venv/` e `node_modules/` nunca vão para o Git?
10. O que `--strict-markers` evita, e por que isso é mais grave do que parece?

---

## Fontes consultadas (12/08/2026)

- [Python 3.14.7 e 3.13.15 — Python Insider, 05/08/2026](https://blog.python.org/2026/08/python-3147-31315/)
- [Download Python — python.org](https://www.python.org/downloads/)
- [pytest — changelog e releases](https://docs.pytest.org/en/stable/changelog.html) · [releases no GitHub](https://github.com/pytest-dev/pytest/releases)
- [Node.js — releases anteriores e cronograma](https://nodejs.org/en/about/previous-releases)
- [Node.js — Evolving the Node.js Release Schedule](https://nodejs.org/en/blog/announcements/evolving-the-nodejs-release-schedule)
- [Node.js — Test runner (documentação da API)](https://nodejs.org/api/test.html)
- [Node.js — Collecting code coverage](https://nodejs.org/learn/test-runner/collecting-code-coverage)
- [uv vs pip — Real Python](https://realpython.com/uv-vs-pip/)
- [Vitest vs Jest 2026 — SitePoint](https://www.sitepoint.com/vitest-vs-jest-2026-migration-benchmark/)
- Versões conferidas por execução local: `pytest 9.1.1`, `coverage 7.15.4`,
  `hypothesis 6.165.3`, `node v24.18.0`, `npm 12.0.1`, `vitest 4.1.10`,
  `@playwright/test 1.62.1` (via `npm view`).
