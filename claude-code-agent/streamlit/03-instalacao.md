# 03 · Manual de instalação — Streamlit e todo o conjunto ao redor

> **Nível:** iniciante · **Escrito e verificado em:** 02/09/2026
> **Versões testadas:** Streamlit **1.63.0** (publicada em 01/09/2026) ·
> Python **3.10.12** · pandas **2.3.3** · plotly **7.0.0** · uv **0.12.7**
> **Máquina de referência:** Ubuntu 22.04.5 LTS, x86-64.
> Trechos de macOS e Windows conferidos contra a documentação oficial na mesma data.

Um manual de campo. A ideia é que dê para seguir sem saber nada, sem improvisar
e sem consultar outra fonte. Todo passo tem: o comando, o que ele faz, como
verificar, e o que fazer se der diferente.

---

## Índice

- [0. Antes de instalar qualquer coisa](#0-antes-de-instalar-qualquer-coisa)
- [1. Sem instalar nada — comece hoje](#1-sem-instalar-nada--comece-hoje)
- [2. O que precisa ser instalado (mapa)](#2-o-que-precisa-ser-instalado-mapa)
- [3. Python](#3-python)
- [4. Gerenciador de pacotes e ambiente](#4-gerenciador-de-pacotes-e-ambiente)
- [5. Streamlit](#5-streamlit)
- [6. Extras do Streamlit (auth, sql, charts, pdf, performance)](#6-extras-do-streamlit)
- [7. Bibliotecas de dados e gráficos](#7-bibliotecas-de-dados-e-graficos)
- [8. Editor e extensões](#8-editor-e-extensões)
- [9. Git](#9-git)
- [10. Docker (opcional, mas recomendado)](#10-docker)
- [11. Banco de dados (opcional)](#11-banco-de-dados-opcional)
- [12. PATH e variáveis de ambiente](#12-path-e-variáveis-de-ambiente)
- [13. Permissões — e por que `sudo pip` é armadilha](#13-permissões)
- [14. Rede corporativa: proxy, certificado, registry](#14-rede-corporativa)
- [15. Conviver com várias versões](#15-conviver-com-várias-versões)
- [16. Reprodutibilidade](#16-reprodutibilidade)
- [17. Atualizar com segurança e voltar atrás](#17-atualizar-e-voltar-atrás)
- [18. Desinstalar por completo](#18-desinstalar-por-completo)
- [19. Solução de problemas — erros literais](#19-solução-de-problemas)
- [20. Checklist "ambiente pronto"](#20-checklist-ambiente-pronto)

---

## 0. Antes de instalar qualquer coisa

Requisitos reais, medidos:

| Item | Valor |
|---|---|
| Espaço em disco | ~**480 MB** para `streamlit + pandas + plotly` num venv limpo (medido em 02/09/2026) |
| Memória para rodar | ~**120 MB** de base por processo; o resto é o seu DataFrame |
| Arquitetura | x86-64 e ARM64 (Apple Silicon, Raspberry Pi 4/5, servidores Graviton) |
| Licença | **Apache 2.0** — uso comercial livre, sem royalties. Ver [80](80-custos-e-licencas.md) |
| Conta obrigatória | **nenhuma** para instalar e rodar localmente |
| Cartão de crédito | **nunca**, para nada do que está neste arquivo |

> Na primeira execução o Streamlit pede um e-mail no terminal. **É opcional.**
> Aperte Enter em branco. Para nunca mais ver a pergunta, ver a seção
> [12](#12-path-e-variáveis-de-ambiente) (`server.showEmailPrompt = false`).

---

## 1. Sem instalar nada — comece hoje

Se a sua meta é *hoje*, use um destes e volte para a instalação amanhã. Isso é
sério: a maior parte das desistências acontece no primeiro dia, na instalação.

### 1.1 GitHub Codespaces (o melhor dos três)

Uma máquina Linux completa no navegador. 60 horas/mês grátis na conta pessoal
gratuita (verificado em 02/09/2026 — confira em
<https://github.com/features/codespaces>, o limite muda).

1. Crie um repositório novo no GitHub, com um arquivo `streamlit_app.py`.
2. Botão verde **Code** → aba **Codespaces** → **Create codespace on main**.
3. No terminal que abre:

```bash
pip install streamlit
streamlit run streamlit_app.py
```

O Codespaces detecta a porta 8501 e oferece o link. Funciona.

### 1.2 Google Colab

Colab não expõe porta HTTP diretamente; precisa de um túnel. Funciona, mas é
gambiarra — use só para experimentar:

```python
!pip install streamlit -q
!npx --yes localtunnel --port 8501 &
!streamlit run app.py --server.headless true
```

Não recomendo para aprender: o túnel cai, e você vai debugar o túnel em vez do
Streamlit.

### 1.3 Streamlit Community Cloud direto do GitHub

Se você já tem um repositório com um app, publique sem instalar nada:
<https://share.streamlit.io> → conecte o GitHub → escolha o repositório e o
arquivo. Detalhes em [28-deploy-e-operacao.md](28-deploy-e-operacao.md).

---

## 2. O que precisa ser instalado (mapa)

Um manual que instala só o Streamlit e assume o resto não serve. Isto é o
conjunto inteiro:

```mermaid
flowchart TD
    P["Python ≥ 3.10<br/>OBRIGATÓRIO"] --> G["Gerenciador de ambiente<br/>uv · venv · conda<br/>OBRIGATÓRIO na prática"]
    G --> S["streamlit 1.63.0<br/>OBRIGATÓRIO"]
    S --> D["pandas · numpy · pyarrow<br/>(pandas já vem como dependência)"]
    S --> C["Gráficos: plotly ou altair<br/>altair já vem junto"]
    S --> X["Extras: auth · sql · pdf<br/>OPCIONAIS"]
    E["Editor: VS Code ou PyCharm<br/>+ extensão Python"] -.-> S
    GT["Git"] -.->|"deploy grátis"| S
    DK["Docker"] -.->|"produção"| S
    BD["PostgreSQL / SQLite"] -.->|"backend"| S
```

| Componente | Obrigatório? | Seção |
|---|---|---|
| Python ≥ 3.10 | **sim** | [3](#3-python) |
| uv (ou venv+pip) | na prática, sim | [4](#4-gerenciador-de-pacotes-e-ambiente) |
| streamlit | **sim** | [5](#5-streamlit) |
| pandas, numpy, pyarrow, altair | vêm juntos com o streamlit | [7](#7-bibliotecas-de-dados-e-graficos) |
| plotly | recomendado para painel bom | [7](#7-bibliotecas-de-dados-e-graficos) |
| Authlib (`streamlit[auth]`) | só se usar `st.login()` | [6](#6-extras-do-streamlit) |
| SQLAlchemy (`streamlit[sql]`) | só se usar `st.connection("sql")` | [6](#6-extras-do-streamlit) |
| VS Code + extensão Python | recomendado | [8](#8-editor-e-extensões) |
| Git | só para deploy no Community Cloud | [9](#9-git) |
| Docker | só para produção | [10](#10-docker) |
| PostgreSQL | só se o backend for Postgres | [11](#11-banco-de-dados-opcional) |

---

## 3. Python

**Versão mínima: 3.10.** Não é opinião — está nos metadados do pacote:

```bash
python3 -c "import importlib.metadata as m; print(m.metadata('streamlit')['Requires-Python'])"
# esperado: >=3.10
```

**Versão recomendada: 3.12.** Estável, rápida, e todo o ecossistema de dados já
publicou *wheels* (pacotes binários prontos) para ela.
**Evite** a versão mais nova recém-lançada nos primeiros meses: pandas, numpy e
pyarrow demoram a publicar binários, e sem binário o `pip` tenta **compilar**, o
que exige compilador e leva 20 minutos — quando funciona.

### 3.1 Linux — Debian / Ubuntu

```bash
python3 --version
```
*O que faz:* diz qual Python já existe. Ubuntu 22.04 traz 3.10.12; 24.04 traz 3.12.

```
# esperado: Python 3.10.12 (ou superior)
```

Se for menor que 3.10, ou não existir:

```bash
sudo apt update && sudo apt install -y python3 python3-venv python3-pip
```
*O que faz:* instala Python, o módulo de ambiente virtual e o pip.
**`python3-venv` é um pacote separado no Debian/Ubuntu** — sem ele, `python3 -m venv`
falha com uma mensagem confusa. Instale sempre.

Verificação:

```bash
python3 --version && python3 -m venv --help > /dev/null && echo "venv ok"
# esperado: Python 3.1x.y
#           venv ok
```

Para uma versão mais nova que a da distro, sem quebrar o sistema:

```bash
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt update && sudo apt install -y python3.12 python3.12-venv
python3.12 --version
# esperado: Python 3.12.x
```
*Aviso:* o PPA `deadsnakes` é mantido pela comunidade, não pela Canonical. Se
isso for problema de conformidade na sua empresa, use `uv python install`
(seção [4.1](#41-uv-recomendado)) ou um contêiner.

### 3.2 Linux — Fedora / RHEL / Rocky / Alma

```bash
sudo dnf install -y python3 python3-pip
python3 --version
# esperado: Python 3.12.x no Fedora 40+; 3.9 no RHEL 9 (INSUFICIENTE)
```

**RHEL 9 vem com Python 3.9 como padrão — não serve.** Instale outro:

```bash
sudo dnf install -y python3.12 python3.12-pip
python3.12 --version
# esperado: Python 3.12.x
```

### 3.3 macOS

O Python que vem no macOS é da Apple, fica em `/usr/bin/python3` e **não deve ser
usado para instalar pacotes** — ele é do sistema, sofre com atualizações do SO,
e em versões recentes o `pip` recusa instalar nele.

**Caminho recomendado: Homebrew.**

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```
*O que faz:* instala o Homebrew, gerenciador de pacotes do macOS.

Depois da instalação ele imprime dois comandos para adicionar o `brew` ao PATH.
**Execute-os** — é o passo que todo mundo pula:

```bash
# Apple Silicon (M1/M2/M3/M4) — o Homebrew fica em /opt/homebrew
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"

# Intel — fica em /usr/local
echo 'eval "$(/usr/local/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/usr/local/bin/brew shellenv)"
```

```bash
brew install python@3.12
python3.12 --version
# esperado: Python 3.12.x
```

**Intel × Apple Silicon:** desde 2020 os Macs têm ARM64. Todas as dependências do
Streamlit publicam wheels para `macosx_arm64` há anos, então não há mais o
sofrimento antigo com pyarrow. Se você usa Rosetta por algum motivo, saiba que um
venv criado sob Rosetta é x86-64 e não mistura com um nativo — e a mensagem de
erro não vai dizer isso.

### 3.4 Windows

Há dois caminhos, e **a recomendação depende do seu objetivo**:

| | **WSL2** (recomendado) | **Windows nativo** |
|---|---|---|
| Igual ao servidor de produção | sim (é Linux) | não |
| Docker | funciona nativamente | precisa do WSL2 por baixo mesmo assim |
| Caminho de arquivo | `/home/voce/...` | `C:\Users\...` — barra invertida quebra script |
| Desempenho de disco | ótimo dentro do WSL, **péssimo** cruzando para `/mnt/c` | ótimo |
| Curva inicial | 20 minutos a mais | zero |

**Recomendação:** se você vai colocar em produção algum dia, use WSL2. Se você
quer só um painel local no seu computador, o Windows nativo serve bem.

#### 3.4.1 Windows nativo

Baixe em <https://www.python.org/downloads/windows/> a versão **3.12.x**,
instalador de 64 bits.

**Na primeira tela do instalador, marque "Add python.exe to PATH".** É uma
caixinha pequena embaixo. Não marcar é a causa nº 1 de
`'python' não é reconhecido como um comando`.

Verificação, no PowerShell:

```powershell
python --version
# esperado: Python 3.12.x
py -0
# esperado: lista das versões instaladas, com * na padrão
```

> Se `python` abrir a Microsoft Store, você caiu no *app execution alias* do
> Windows. Correção: Configurações → Aplicativos → Aliases de execução de
> aplicativo → desligue **python.exe** e **python3.exe**.

#### 3.4.2 WSL2

No PowerShell **como administrador**:

```powershell
wsl --install -d Ubuntu-24.04
```
*O que faz:* instala o subsistema Linux e a distribuição Ubuntu 24.04.
Reinicie quando pedir; na primeira abertura ele pede usuário e senha do Linux.

```bash
# já dentro do Ubuntu
sudo apt update && sudo apt install -y python3 python3-venv python3-pip
python3 --version
# esperado: Python 3.12.3 (Ubuntu 24.04)
```

**Regra de ouro do WSL2:** guarde o projeto em `~/projetos/...` (disco do Linux),
**nunca** em `/mnt/c/Users/...`. Atravessar o sistema de arquivos deixa o
observador de mudanças do Streamlit lento e às vezes cego — o *hot reload* para
de funcionar e você não entende por quê.

---

## 4. Gerenciador de pacotes e ambiente

**Nunca instale o Streamlit no Python do sistema.** Motivo concreto, não
ideológico: seu sistema operacional (e o `apt`) também usa Python. Instalar
pacotes globalmente já quebrou instalação de Ubuntu de gente que eu conheço. E,
com dois projetos, você vai precisar de duas versões da mesma biblioteca — não
tem como, num Python só.

Três opções, com recomendação explícita:

| Método | Quando usar | Velocidade | Recomendação |
|---|---|---|---|
| **uv** | quase sempre | ~10× mais rápido que pip | **use este** |
| **venv + pip** | quando não pode instalar ferramenta nova | referência | ótimo, universal |
| **conda / mamba** | quando o time já usa, ou há dependência científica pesada (GDAL, CUDA) | lento | só se já estiver no seu contexto |

### 4.1 uv (recomendado)

O uv é o gerenciador de pacotes e ambientes da Astral, escrito em Rust. Ele
resolve, baixa e instala tudo em segundos, e ainda instala o próprio Python.
Curso completo: [`uv-python`](../uv-python/00-MAPA.md).

**Linux e macOS:**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```
*O que faz:* baixa um binário para `~/.local/bin/uv`. Não pede `sudo`, não toca
no Python do sistema.

```bash
uv --version
# esperado: uv 0.12.7 (ou superior)
```

Se der `command not found: uv`, reabra o terminal (o instalador acrescentou o
`~/.local/bin` ao seu perfil, e o terminal aberto ainda não sabe disso). Se
persistir, ver seção [12](#12-path-e-variáveis-de-ambiente).

**Windows (PowerShell):**

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
uv --version
# esperado: uv 0.12.7
```

Instalar um Python específico com o próprio uv (útil quando você não tem
permissão de administrador):

```bash
uv python install 3.12
uv python list
# esperado: uma linha com cpython-3.12.x marcada como instalada
```

### 4.2 venv + pip (universal)

Funciona em qualquer lugar, sem instalar nada além do Python.

```bash
mkdir -p ~/projetos/meu-painel && cd ~/projetos/meu-painel
python3 -m venv .venv
```
*O que faz:* cria a pasta `.venv` com um Python isolado.

```bash
# Linux / macOS
source .venv/bin/activate

# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# Windows CMD
.venv\Scripts\activate.bat
```

Verificação — a mais importante deste arquivo inteiro:

```bash
which python      # Linux/macOS   (Windows: where python)
# esperado: /home/voce/projetos/meu-painel/.venv/bin/python
#           SE aparecer /usr/bin/python, o ambiente NÃO está ativo.
```

> **Erro clássico do Windows PowerShell:**
> `não pode ser carregado porque a execução de scripts foi desabilitada`.
> Correção (uma vez, só para o seu usuário):
> ```powershell
> Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
> ```

Atualize o pip antes de instalar qualquer coisa — pip velho baixa código-fonte em
vez de wheel e você espera vinte minutos por nada:

```bash
python -m pip install --upgrade pip
pip --version
# esperado: pip 25.x ou superior
```

### 4.3 conda / mamba

```bash
conda create -n painel python=3.12 -y
conda activate painel
conda install -c conda-forge streamlit -y
```

**Regra que evita o pior problema do conda:** escolha **um** canal e **um**
instalador por ambiente. Misturar `conda install` e `pip install` no mesmo
ambiente funciona *até* o dia em que não funciona, e aí o erro é ilegível. Se for
usar conda, use conda para tudo — ou use conda só para o Python e pip para tudo o
mais, nunca em zigue-zague.

---

## 5. Streamlit

### 5.1 Com uv (projeto novo, do zero)

```bash
mkdir -p ~/projetos/meu-painel && cd ~/projetos/meu-painel
uv init --python 3.12
```
*O que faz:* cria `pyproject.toml`, `.python-version` e um esqueleto de projeto.

```bash
uv add streamlit
```
*O que faz:* resolve, baixa, instala **e grava a dependência** no `pyproject.toml`
com um `uv.lock` (arquivo de trava). É o passo que torna o projeto reprodutível.

```bash
uv run streamlit version
# esperado: Streamlit, version 1.63.0
```

### 5.2 Com venv + pip

```bash
# com o ambiente ATIVO (veja 4.2)
pip install streamlit
streamlit version
# esperado: Streamlit, version 1.63.0
```

Para fixar a versão (recomendado em qualquer coisa que outra pessoa vá rodar):

```bash
pip install "streamlit==1.63.0"
```

### 5.3 Verificação real — rode a demonstração

Instalar não é verificar. Isto é verificar:

```bash
streamlit hello
```
*O que faz:* sobe o servidor com a app de demonstração.

Esperado no terminal:

```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

E o navegador abre sozinho com a tela "Welcome to Streamlit". Se abriu, **está
instalado e funcionando**. `Ctrl+C` encerra.

Se o navegador não abriu sozinho, abra `http://localhost:8501` à mão — isso é
normal em WSL2, em servidor sem interface gráfica e em contêiner.

### 5.4 Esqueleto de projeto pronto

Desde a versão 1.5x existe um comando para criar o esqueleto:

```bash
streamlit init
```
*O que faz:* cria `streamlit_app.py` e `requirements.txt` na pasta atual e
pergunta se você quer rodar agora. Verificado em 02/09/2026 com 1.63.0.

Saída esperada:

```
✨ Created new Streamlit app in .
🚀 Run it with: streamlit run ./streamlit_app.py
❓ Run the app now? [Y/n]:
```

### 5.5 Bônus: instruções para agentes de IA

O Streamlit passou a distribuir "skills" para agentes de código (Claude Code e
compatíveis), a partir da 1.58:

```bash
streamlit skills          # instala no projeto (.claude/skills, .agents/skills)
streamlit skills --global # instala uma vez, vale para todos os projetos
```
*O que faz:* cria links para as instruções que o Streamlit publica junto com o
pacote, para o agente escrever código idiomático da versão que você tem
instalada. Verificado em 02/09/2026.

---

## 6. Extras do Streamlit

O pacote declara *extras* — grupos opcionais de dependências. Instale só o que
for usar; cada extra é peso a mais na imagem e uma dependência a mais para
auditar.

| Extra | Instala | Precisa se você for usar |
|---|---|---|
| `auth` | `Authlib>=1.3.2`, `httpx` | `st.login()` / OIDC |
| `sql` | `SQLAlchemy>=2.0` | `st.connection("sql")` |
| `charts` | `matplotlib`, `plotly`, `graphviz`, `orjson` | esses gráficos |
| `pdf` | `streamlit-pdf` | `st.pdf()` |
| `performance` | `orjson`, `uvloop` (não-Windows) | serialização e laço de eventos mais rápidos |
| `snowflake` | conector e Snowpark | Snowflake |
| `all` | tudo acima + `rich` | preguiça (não recomendo em produção) |

```bash
uv add "streamlit[auth,sql]"
# ou
pip install "streamlit[auth,sql]"
```

Verificação:

```bash
python -c "import authlib, sqlalchemy; print(authlib.__version__, sqlalchemy.__version__)"
# esperado: duas versões, sem ModuleNotFoundError
```

> **O que mudou por dentro, e importa:** até a versão 1.56 o Streamlit rodava
> sobre **Tornado**. A partir da 1.57 (29/04/2026) o servidor padrão é
> **Starlette + Uvicorn** (ASGI). Consequência prática: o pacote instalado hoje
> traz `starlette`, `uvicorn`, `httptools`, `anyio` e `websockets`, e **não traz
> mais Tornado**. Se você tem código antigo que importava `tornado` para
> estender o servidor, ele quebrou. Ver [65-estado-da-arte.md](65-estado-da-arte.md).

---

## 7. Bibliotecas de dados e gráficos

Boa notícia: **quase tudo já vem junto**. Instalar `streamlit` traz, como
dependências obrigatórias:

```
altair · numpy · pandas · pillow · pyarrow · protobuf · requests
click · packaging · toml · typing-extensions
starlette · uvicorn · httptools · anyio · websockets · itsdangerous
python-multipart · watchdog (fora do macOS)
```

Ou seja: `import pandas`, `import numpy` e gráficos Altair funcionam sem
instalar mais nada.

O que vale instalar além disso:

```bash
uv add plotly           # gráficos interativos com controle fino  (recomendado)
uv add matplotlib       # gráficos estáticos, publicação acadêmica
uv add openpyxl         # ler e escrever .xlsx
uv add sqlalchemy psycopg[binary]   # PostgreSQL
```

Verificação de tudo de uma vez:

```bash
python - <<'EOF'
import streamlit, pandas, numpy, altair, pyarrow
print("streamlit", streamlit.__version__)
print("pandas   ", pandas.__version__)
print("numpy    ", numpy.__version__)
print("altair   ", altair.__version__)
print("pyarrow  ", pyarrow.__version__)
EOF
```

Saída esperada (valores de 02/09/2026; os seus podem ser maiores):

```
streamlit 1.63.0
pandas    2.3.3
numpy     2.x.y
altair    5.x.y
pyarrow   2x.y.z
```

---

## 8. Editor e extensões

### VS Code (recomendado)

**Linux (Debian/Ubuntu):**
```bash
sudo snap install --classic code
# ou baixe o .deb em https://code.visualstudio.com/
```

**macOS:**
```bash
brew install --cask visual-studio-code
```

**Windows:** instalador em <https://code.visualstudio.com/>. Marque *"Adicionar
ao PATH"* durante a instalação.

**Extensões, em ordem de utilidade:**

```bash
code --install-extension ms-python.python
code --install-extension ms-python.vscode-pylance
code --install-extension charliermarsh.ruff
code --install-extension ms-vscode-remote.remote-wsl        # só Windows/WSL2
code --install-extension ms-azuretools.vscode-docker        # se for usar Docker
```

Verificação:

```bash
code --list-extensions | grep -E "ms-python.python|ruff"
# esperado: as duas linhas
```

**Passo que quase todo mundo pula e depois reclama:** apontar o VS Code para o
interpretador do venv. `Ctrl+Shift+P` → *Python: Select Interpreter* → escolha o
que termina em `.venv/bin/python`. Sem isso, o autocompletar não conhece o
`streamlit`, e o editor sublinha de vermelho código que funciona.

Arquivo `.vscode/settings.json` sugerido para o projeto:

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
  "python.terminal.activateEnvironment": true,
  "[python]": { "editor.defaultFormatter": "charliermarsh.ruff" },
  "files.exclude": { "**/__pycache__": true }
}
```

### PyCharm

Community Edition é gratuita e suficiente. Configure em
*Settings → Project → Python Interpreter → Add → Existing environment* apontando
para `.venv/bin/python`. Para rodar com F5, crie uma configuração do tipo
*Python* com módulo `streamlit` e parâmetros `run app.py`.

---

## 9. Git

Necessário **só** se você for publicar no Streamlit Community Cloud — que exige
que o código esteja num repositório do GitHub.

```bash
# Debian/Ubuntu
sudo apt install -y git
# Fedora
sudo dnf install -y git
# macOS
brew install git
# Windows: https://git-scm.com/download/win
```

```bash
git --version
# esperado: git version 2.3x.y
git config --global user.name "Seu Nome"
git config --global user.email "voce@exemplo.com"
```

Curso completo, incluindo assinatura de commit:
[`commits-assinados`](../commits-assinados/00-MAPA.md).

---

## 10. Docker

Opcional para aprender, praticamente obrigatório para produção. Curso completo:
[`curso-docker`](../curso-docker/00-indice.md).

**Linux (Debian/Ubuntu), script oficial:**

```bash
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER
```
*O que faz:* instala o Docker Engine e coloca o seu usuário no grupo `docker`,
para não precisar de `sudo` a cada comando.

**Você precisa sair e entrar da sessão** (ou reiniciar) para o grupo valer.
Verificação:

```bash
docker run --rm hello-world
# esperado: "Hello from Docker!"
# se der "permission denied ... /var/run/docker.sock": o grupo ainda não pegou.
```

**macOS e Windows:** Docker Desktop, em <https://www.docker.com/products/docker-desktop/>.
No Windows ele usa o WSL2 por baixo — instale o WSL2 antes (seção
[3.4.2](#342-wsl2)).

> **Licença do Docker Desktop:** gratuito para uso pessoal, educação e empresas
> pequenas; **pago** para empresas com mais de 250 funcionários **ou** mais de
> US$ 10 milhões de receita anual (política verificada em 02/09/2026 em
> <https://www.docker.com/pricing/>). Alternativas gratuitas: Podman Desktop,
> Rancher Desktop, ou Docker Engine puro dentro do WSL2.

---

## 11. Banco de dados (opcional)

Só se o seu app for escrever dados. Para aprender, **SQLite basta e já vem com o
Python** — é o que o [projeto-modelo](07-projeto-modelo/) usa.

```bash
python -c "import sqlite3; print('sqlite', sqlite3.sqlite_version)"
# esperado: sqlite 3.3x.y  (nada a instalar)
```

**PostgreSQL, quando for para valer.** O jeito mais simples é contêiner:

```bash
docker run -d --name pg-painel \
  -e POSTGRES_PASSWORD=segredo \
  -e POSTGRES_DB=painel \
  -p 5432:5432 \
  -v pg-painel-dados:/var/lib/postgresql/data \
  postgres:17
```
*O que faz:* sobe um PostgreSQL 17 na porta 5432, com os dados num volume que
sobrevive ao contêiner.

```bash
docker exec -it pg-painel psql -U postgres -d painel -c "SELECT version();"
# esperado: PostgreSQL 17.x on x86_64-pc-linux-gnu ...
```

Cliente Python:

```bash
uv add "psycopg[binary]" sqlalchemy
python -c "import psycopg, sqlalchemy; print('ok', sqlalchemy.__version__)"
```

Curso completo: [`postgresql`](../postgresql/00-MAPA.md).

---

## 12. PATH e variáveis de ambiente

### Por que a mudança "não pegou"

O PATH é lido **quando o terminal inicia**. Alterar o arquivo de perfil não
altera o terminal que já está aberto. Reabra o terminal — ou recarregue o perfil:

```bash
source ~/.bashrc     # bash
source ~/.zshrc      # zsh (padrão do macOS desde o Catalina)
```

No Windows, o PowerShell também só relê o PATH ao abrir. Feche e abra.

### Conferir onde as coisas estão

```bash
# Linux / macOS
echo "$PATH" | tr ':' '\n'
which python streamlit uv

# Windows PowerShell
$env:PATH -split ';'
where.exe python; where.exe streamlit
```

### Corrigir, no arquivo certo

| Shell | Arquivo | Linha a acrescentar |
|---|---|---|
| bash | `~/.bashrc` | `export PATH="$HOME/.local/bin:$PATH"` |
| zsh (macOS) | `~/.zshrc` | `export PATH="$HOME/.local/bin:$PATH"` |
| fish | `~/.config/fish/config.fish` | `fish_add_path ~/.local/bin` |
| PowerShell | `$PROFILE` (`notepad $PROFILE`) | `$env:PATH = "$HOME\.local\bin;$env:PATH"` |

> `~/.bash_profile` × `~/.bashrc`: no Linux, terminal gráfico lê `.bashrc`; login
> por SSH lê `.bash_profile`. Se funciona no terminal e falha no SSH, é isso.

### Variáveis de ambiente do Streamlit

Toda opção de configuração tem uma variável equivalente, no padrão
`STREAMLIT_<SEÇÃO>_<OPÇÃO>` em maiúsculas:

```bash
export STREAMLIT_SERVER_PORT=8502
export STREAMLIT_SERVER_HEADLESS=true          # não tenta abrir navegador
export STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
export STREAMLIT_SERVER_SHOW_EMAIL_PROMPT=false  # nunca mais pede e-mail
export STREAMLIT_CLIENT_SHOW_ERROR_DETAILS=none  # produção: não vaza traceback
```

A ordem de precedência, do mais forte para o mais fraco:

```
argumento de linha de comando  >  variável de ambiente
   >  ./.streamlit/config.toml (do projeto)
   >  ~/.streamlit/config.toml (do usuário)
   >  padrão
```

Ver o que está valendo agora:

```bash
streamlit config show | head -40
```

---

## 13. Permissões

### Por que `sudo pip install` é armadilha

Não é regra de etiqueta. São três problemas concretos:

1. **Você mistura seus pacotes com os do sistema.** No Ubuntu, o `apt` instala
   pacotes Python em `/usr/lib/python3/dist-packages`. Um `sudo pip install`
   pode substituir uma versão de que o `apt` depende. Já vi isso derrubar o
   `apt` inteiro — e aí você não consegue nem consertar com `apt`.
2. **Você executa código de terceiros como root.** Um pacote no PyPI pode rodar
   código arbitrário na instalação (`setup.py`). Como root, isso é o fim.
3. **Não resolve nada que um venv não resolva melhor.**

Por isso o Python moderno **recusa**, e a mensagem é esta:

```
error: externally-managed-environment
× This environment is externally managed
```

Isso é o [PEP 668](https://peps.python.org/pep-0668/) funcionando. A resposta
certa **não** é `--break-system-packages` (o nome já avisa). É criar um venv.

### Os três caminhos legítimos sem `sudo`

```bash
# 1. venv no projeto — o certo
python3 -m venv .venv && source .venv/bin/activate && pip install streamlit

# 2. uv — nem toca no Python do sistema
uv add streamlit

# 3. instalação só para o seu usuário (quando você não pode nem criar venv)
pip install --user streamlit
# o binário vai para ~/.local/bin — que precisa estar no PATH (seção 12)
```

### Máquina sem permissão de administrador

Tudo neste manual, exceto Docker e o `apt`/`dnf`/`brew`, funciona **sem** ser
administrador:

- `uv` instala em `~/.local/bin` — não precisa de root;
- `uv python install 3.12` instala um Python no seu diretório — não precisa de root;
- `pip install --user` — não precisa de root.

Se nem isso for possível, use Codespaces (seção [1.1](#11-github-codespaces-o-melhor-dos-três)).

---

## 14. Rede corporativa

Sintoma típico: a instalação fica parada e termina com
`Connection timed out` ou `CERTIFICATE_VERIFY_FAILED`.

### Proxy

```bash
export HTTP_PROXY="http://usuario:senha@proxy.empresa.com:8080"
export HTTPS_PROXY="$HTTP_PROXY"
export NO_PROXY="localhost,127.0.0.1,::1,.empresa.local"
```

> **Cuidado, e isto derruba app de Streamlit especificamente:** o `NO_PROXY`
> precisa conter `localhost` **e** `127.0.0.1`. Se faltar, o navegador (ou um
> cliente Python dentro do app) tenta falar com o seu próprio servidor
> *através do proxy* — e o proxy não conhece a sua máquina. Sintoma: a página
> carrega o esqueleto e fica eternamente em "Connecting...".
> `NO_PROXY` malformado (com espaços, ou com `*` no meio) é pior que ausente:
> algumas bibliotecas ignoram a variável inteira em silêncio.

No PowerShell:

```powershell
$env:HTTP_PROXY  = "http://usuario:senha@proxy.empresa.com:8080"
$env:HTTPS_PROXY = $env:HTTP_PROXY
$env:NO_PROXY    = "localhost,127.0.0.1,::1"
```

### Certificado interno (TLS inspecionado)

Empresas que inspecionam TLS reassinam os certificados com uma autoridade
própria. O Python não a conhece.

**Correto:**

```bash
export SSL_CERT_FILE=/caminho/para/ca-empresa.pem
export REQUESTS_CA_BUNDLE=/caminho/para/ca-empresa.pem
pip config set global.cert /caminho/para/ca-empresa.pem
```

**Errado, e por quê:** `pip install --trusted-host pypi.org` desliga a
verificação. Você passa a aceitar qualquer coisa que o proxy entregar, inclusive
um pacote adulterado. Use só como diagnóstico de dez segundos, nunca como
configuração permanente.

### Registry espelhado (Nexus, Artifactory)

```bash
pip config set global.index-url https://nexus.empresa.com/repository/pypi/simple
pip config set global.trusted-host nexus.empresa.com
```

Para o uv, no `pyproject.toml` ou em variável:

```bash
export UV_INDEX_URL="https://nexus.empresa.com/repository/pypi/simple"
```

### Firewall e a porta 8501

Streamlit escuta na 8501 por padrão. Se o colega não abre o seu "Network URL":

```bash
# Ubuntu com ufw
sudo ufw allow 8501/tcp
# Fedora/RHEL
sudo firewall-cmd --add-port=8501/tcp --permanent && sudo firewall-cmd --reload
```

Ver [`portas-de-rede`](../portas-de-rede/00-MAPA.md).

---

## 15. Conviver com várias versões

### Duas versões de Streamlit na mesma máquina

Trivial: **um venv por projeto**. É a razão de o venv existir.

```bash
cd ~/projetos/painel-antigo && uv venv && uv pip install "streamlit==1.44.0"
cd ~/projetos/painel-novo   && uv venv && uv pip install "streamlit==1.63.0"
```

Cada projeto tem seu `.venv`. Não há conflito porque não há nada compartilhado.

### Duas versões de Python

```bash
uv python install 3.10 3.12 3.13
uv python list

# fixar a versão de um projeto:
cd ~/projetos/meu-painel
uv venv --python 3.12
echo "3.12" > .python-version
```

Alternativas: `pyenv` (Linux/macOS), `mise`/`asdf` (multi-linguagem), ou o
lançador `py` no Windows (`py -3.12 -m venv .venv`).

### Duas apps rodando ao mesmo tempo

```bash
streamlit run app_a.py --server.port 8501
streamlit run app_b.py --server.port 8502
```

Sem a troca de porta, a segunda falha com `Port 8501 is already in use`.

---

## 16. Reprodutibilidade

"Funciona na minha máquina" é quase sempre dependência que subiu sozinha.

### Com uv (melhor)

```bash
uv add streamlit pandas plotly
uv lock          # gera uv.lock com o hash de cada pacote
uv sync          # instala EXATAMENTE o que está no lock
```

Versione: `pyproject.toml`, `uv.lock`, `.python-version`.

### Com pip

```bash
pip freeze > requirements.txt
```

`pip freeze` congela tudo, inclusive dependências transitivas — é o que você
quer para deploy. Para a lista curta do que **você** pediu, mantenha à mão um
`requirements.in` e use `uv pip compile` ou `pip-tools`.

Verificação de que a trava funciona (num diretório limpo):

```bash
python -m venv /tmp/teste && /tmp/teste/bin/pip install -r requirements.txt
/tmp/teste/bin/streamlit version
# esperado: exatamente a versão que você fixou
```

### Com contêiner (o mais forte)

Fixe a imagem base por *digest*, não por tag — tag se move:

```dockerfile
FROM python:3.12-slim
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
```

Ver o [Dockerfile do projeto-modelo](07-projeto-modelo/Dockerfile), que já traz
usuário sem privilégio e `HEALTHCHECK`.

---

## 17. Atualizar e voltar atrás

### Ver o que mudaria antes de mudar

```bash
pip list --outdated
# ou
uv lock --upgrade --dry-run
```

### Atualizar

```bash
uv add "streamlit@latest"      # atualiza e regrava o lock
# ou
pip install --upgrade streamlit
streamlit version
```

### Voltar atrás

```bash
pip install "streamlit==1.62.0"
# com uv:
uv add "streamlit==1.62.0" && uv sync
```

**Procedimento que eu recomendo, e que evita o susto:**

1. leia as notas de versão em <https://docs.streamlit.io/develop/quick-reference/release-notes>;
2. atualize num *branch*;
3. rode a suíte de testes com `AppTest` (ver [30-testes.md](30-testes.md));
4. só então mude o `requirements.txt` da produção.

Streamlit é uma biblioteca que **remove** coisas: `st.experimental_rerun`,
`st.cache`, `use_container_width` — todas já deram trabalho para alguém. As
depreciações vêm com prazo escrito no aviso. Leia o aviso no terminal; ele diz o
substituto e a data.

---

## 18. Desinstalar por completo

### O pacote

```bash
pip uninstall -y streamlit
# uv:
uv remove streamlit
```

### O que fica para trás (e ninguém apaga)

```bash
# configuração e credencial do usuário
rm -rf ~/.streamlit

# cache de dados persistido em disco (st.cache_data(persist="disk"))
rm -rf ~/.streamlit/cache

# cache do pip / uv
pip cache purge
uv cache clean

# o ambiente virtual inteiro (o jeito mais limpo de todos)
rm -rf .venv
```

**Windows:**

```powershell
Remove-Item -Recurse -Force "$env:USERPROFILE\.streamlit"
Remove-Item -Recurse -Force .\.venv
```

**macOS** — se instalou por Homebrew e quer tirar o Python também:

```bash
brew uninstall python@3.12
brew cleanup
```

Verificação de que sumiu:

```bash
which streamlit || echo "removido"
ls ~/.streamlit 2>/dev/null || echo "config removida"
```

---

## 19. Solução de problemas

Mensagem literal, causa e correção. Cobre os erros que mais aparecem.

| Mensagem | Causa provável | Correção |
|---|---|---|
| `command not found: streamlit` (Linux/macOS)<br>`'streamlit' não é reconhecido` (Windows) | o venv não está ativo, ou `~/.local/bin` fora do PATH | ative o venv (`source .venv/bin/activate`); ou rode `python -m streamlit run app.py`; ou conserte o PATH (seção [12](#12-path-e-variáveis-de-ambiente)) |
| `error: externally-managed-environment` | `pip` no Python do sistema, protegido pelo PEP 668 | crie um venv. **Não** use `--break-system-packages` |
| `ModuleNotFoundError: No module named 'streamlit'` | instalou num ambiente e está rodando em outro | `which python` e `which streamlit` têm de apontar para o mesmo `.venv` |
| `Port 8501 is already in use` | outra instância ainda rodando | `streamlit run app.py --server.port 8502`; ou `lsof -ti:8501 \| xargs kill` (Linux/macOS), `netstat -ano \| findstr :8501` + `taskkill /PID <pid> /F` (Windows) |
| `EACCES: permission denied` / `Permission denied: '/usr/lib/python3...'` | tentou instalar global sem permissão | venv, ou `pip install --user` |
| `SSLError: CERTIFICATE_VERIFY_FAILED` | proxy corporativo com TLS inspecionado | aponte `SSL_CERT_FILE` para a CA da empresa (seção [14](#14-rede-corporativa)) |
| `ReadTimeoutError: HTTPSConnectionPool(host='pypi.org'...)` | proxy ou firewall | configure `HTTPS_PROXY`; ou use o registry interno |
| Página fica em **"Connecting..."** para sempre | proxy sem `localhost` no `NO_PROXY`; ou proxy reverso sem repasse de WebSocket | acerte o `NO_PROXY`; no nginx, `proxy_set_header Upgrade`/`Connection` e `proxy_read_timeout 3600` (ver [28](28-deploy-e-operacao.md)) |
| `Please replace use_container_width with width.` | API depreciada (some depois de 31/12/2025) | troque por `width="stretch"` ou `width="content"` |
| `StreamlitSetPageConfigMustBeFirstCommandError` | algum `st.*` antes do `st.set_page_config` | mova o `set_page_config` para a primeira linha depois dos imports |
| `StreamlitDuplicateElementKey` / `DuplicateWidgetID` | dois widgets iguais sem `key` distinta | dê `key=` explícita a cada um |
| `AxiosError: Request failed with status code 403` no upload | proteção XSRF + proxy que não repassa cookie | acerte o proxy. **Não** desligue `server.enableXsrfProtection` |
| `RuntimeError: main thread is not in main loop` (matplotlib) | backend gráfico interativo numa thread do servidor | `import matplotlib; matplotlib.use("Agg")` antes de `pyplot` |
| `killed` / a aba morre no Community Cloud | estourou o limite de ~1 GB de memória | reduza os dados, use `ttl` no cache, filtre no banco (ver [80](80-custos-e-licencas.md)) |
| `no such table: pedidos` (SQLite) | esqueceu de rodar a migração, ou o caminho do banco mudou | rode a migração na partida; use caminho absoluto |
| `sqlite3.OperationalError: database is locked` | duas escritas concorrentes | `PRAGMA journal_mode=WAL` e `busy_timeout`; ou troque para PostgreSQL |
| No WSL2: salvar o arquivo **não** recarrega a página | projeto em `/mnt/c/...` — o observador não recebe eventos | mova o projeto para `~/` dentro do WSL |
| `python` abre a Microsoft Store | *app execution alias* do Windows | Configurações → Aliases de execução de aplicativo → desligue `python.exe` |
| `.venv\Scripts\Activate.ps1 não pode ser carregado` | política de execução do PowerShell | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |

---

## 20. Checklist "ambiente pronto"

Rode um por linha. Todos precisam responder.

```bash
python3 --version                              # >= 3.10
which python                                   # tem de apontar para o .venv
pip --version                                  # >= 25
streamlit version                              # Streamlit, version 1.63.0
python -c "import pandas, numpy, altair; print('dados ok')"
python -c "import plotly; print('plotly', plotly.__version__)"   # se instalou
git --version                                  # se for publicar
docker run --rm hello-world                    # se for usar contêiner
streamlit hello                                # abre a demo no navegador
```

Marque:

- [ ] `streamlit hello` abriu a demonstração no navegador.
- [ ] `which python` aponta para o `.venv` do projeto, não para `/usr/bin`.
- [ ] Consigo editar um arquivo, salvar, e a página recarrega sozinha.
- [ ] O editor autocompleta `st.` sem sublinhar de vermelho.
- [ ] Tenho `requirements.txt` (ou `uv.lock`) com a versão fixada.
- [ ] Sei em que porta estou e como trocar.

Tudo marcado → [04-como-comecar.md](04-como-comecar.md).

---

## Autoteste

1. Qual é a versão mínima de Python, e com que comando você **prova** isso na sua
   máquina?
2. Por que `sudo pip install streamlit` é má ideia? Dê os três motivos concretos.
3. Você está numa rede corporativa e a página fica em "Connecting..." para
   sempre. Qual é a primeira variável de ambiente que você confere, e por quê?
4. Como ter Streamlit 1.44 e 1.63 na mesma máquina, sem conflito?
5. O que muda, na prática, por o Streamlit ter trocado Tornado por Starlette na
   versão 1.57?
6. Você desinstalou o `streamlit` com `pip uninstall`. O que ficou no disco?
7. `streamlit run app.py` diz `Port 8501 is already in use`. Duas soluções.
8. Por que guardar o projeto em `/mnt/c/...` no WSL2 quebra o recarregamento
   automático?
9. Qual é a ordem de precedência entre argumento de linha de comando, variável de
   ambiente e `config.toml`?

---

## Fontes consultadas

Consultadas e verificadas em **02/09/2026**:

- Documentação oficial do Streamlit — <https://docs.streamlit.io>
- Notas de versão de 2026 — <https://docs.streamlit.io/develop/quick-reference/release-notes/2026>
- Metadados do pacote instalado (`importlib.metadata`), streamlit 1.63.0 — verificação local
- `streamlit --help` e `streamlit skills --help` da 1.63.0 — verificação local
- Instalação do uv — <https://docs.astral.sh/uv/getting-started/installation/>
- PEP 668 (ambiente gerenciado externamente) — <https://peps.python.org/pep-0668/>
- Preços do Docker Desktop — <https://www.docker.com/pricing/>
- GitHub Codespaces — <https://github.com/features/codespaces>
