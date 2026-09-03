# 3. Manual de instalação — passo a passo, por sistema operacional

`Nível: iniciante` · `Última atualização: 20/08/2026`
`Testado em: Ubuntu 22.04.5 LTS, Python 3.10.12, pip 22.0.2 — em 20/08/2026`
`Versões atuais consultadas na web em 20/08/2026 (fontes no rodapé)`

> **Leia esta caixa antes de instalar qualquer coisa.**
> Para acompanhar **todo** este curso você não precisa de nenhuma biblioteca externa.
> Todos os exemplos dos arquivos 04, 06 e 07 rodam com **Python puro, biblioteca padrão,
> zero `pip install`** — inclusive o projeto-modelo. Isso é uma decisão de projeto, não uma
> limitação: em estatística descritiva, ver a conta acontecer ensina mais do que chamar
> `np.std()`. NumPy, pandas, R, JASP e planilha estão aqui porque você vai encontrá-los no
> mundo real, não porque o curso dependa deles.

---

## 3.0 Comece hoje, sem instalar nada

Se você quer o primeiro resultado na tela nos próximos 5 minutos, use uma destas opções e
volte a este arquivo outro dia. É o caminho recomendado para o primeiro contato — a maior
causa de desistência em qualquer assunto técnico é gastar o primeiro dia brigando com
instalação em vez de ver a coisa funcionar.

| Opção | Link | O que serve | Precisa de conta? | Limite |
|---|---|---|---|---|
| **Google Colab** | <https://colab.research.google.com> | Python completo, NumPy/pandas/SciPy/matplotlib já instalados | sim (conta Google) | sessão cai após ~90 min ociosa; some tudo |
| **JupyterLite** | <https://jupyter.org/try-jupyter/lab/> | Python no próprio navegador (WebAssembly) | **não** | sem internet dentro do notebook; pacotes limitados |
| **Python oficial no navegador** | <https://www.python.org/shell/> | console Python simples | não | só console, sem gráficos |
| **jamovi Cloud (plano Guest)** | <https://www.jamovi.org/cloud.html> | estatística clicando, sem programar | não (plano Guest) | sessão curta, sem salvar |
| **Planilha online** | Google Sheets / Excel Online / LibreOffice | `MÉDIA`, `MED`, `DESVPAD` | conta, exceto LibreOffice local | — |

**Teste de 60 segundos no Colab ou JupyterLite** — cole e execute:

```python
import statistics as st
dados = [12, 15, 11, 14, 98, 13, 12]
print("média   :", round(st.mean(dados), 2))
print("mediana :", st.median(dados))
print("desvpad :", round(st.stdev(dados), 2))
```

```
# esperado:
# média   : 25.0
# mediana : 13
# desvpad : 32.1
```

Se você viu isso, seu ambiente está pronto para o arquivo
[04-como-comecar.md](04-como-comecar.md). O resto deste manual é para quando você quiser
trabalhar na sua própria máquina, com dados que não podem sair dela.

> **Já repare no resultado:** média 25, mediana 13. Um único valor (98) puxou a média para
> quase o dobro do valor típico. Você acabou de reproduzir o "bar com Bill Gates" do
> [arquivo 01](01-introducao-leigo.md).

---

## 3.1 O que este manual instala

Não é só "a ferramenta principal". Cobrimos toda a pilha que uma pessoa fazendo estatística
usa de verdade:

| # | Componente | Para quê | Obrigatório? |
|---|---|---|---|
| 1 | **Python 3.10+** | rodar todos os exemplos do curso | **sim** (ou use a nuvem) |
| 2 | **venv** (já vem com Python) | isolar projetos | recomendado |
| 3 | **pip** | instalar bibliotecas | vem com Python |
| 4 | **NumPy, SciPy, pandas, matplotlib, statsmodels** | trabalho profissional | opcional |
| 5 | **JupyterLab** | caderno interativo | opcional, muito útil |
| 6 | **R + RStudio (ou Positron)** | o outro ecossistema padrão da estatística | opcional |
| 7 | **JASP ou jamovi** | estatística sem programar | opcional |
| 8 | **LibreOffice Calc** | planilha, onde o mundo real faz contas | opcional |
| 9 | **Git** | versionar sua análise (sim, análise é código) | recomendado |
| 10 | **VS Code** (ou outro editor) | escrever os scripts | recomendado |

Instale na ordem 1 → 2 → 4 → 5. Os demais, quando precisar.

**Versões atuais em 20/08/2026** (consultadas na web nesta data):

| Software | Versão atual | Versão mínima para este curso | Evitar |
|---|---|---|---|
| Python | 3.14.7 / 3.13.15 (05/08/2026) | **3.10** | ≤ 3.8 (fora de suporte) |
| NumPy | 2.5.2 (09/08/2026) | 1.21 | 1.x em código novo (API mudou na 2.0) |
| SciPy | 1.18 (jun/2026) | 1.7 | — |
| pandas | 2.3.3 | 2.0 | 1.x (mudança de tipos de dado na 2.0) |
| R | **4.6.1** (24/06/2026, "Happy Hop") | 4.1 (precisa do `\|>`) | ≤ 3.6 |
| JASP | 0.98.1 (07/07/2026) | qualquer 0.16+ | — |
| jamovi | 28.2 (13/08/2026) | qualquer 2.x+ | — |
| uv (instalador rápido) | 0.12.5 | — | — |

---

## 3.2 Python — Linux

### 3.2.1 Debian / Ubuntu / Mint / Pop!_OS

O Python já vem instalado. **Confira antes de instalar qualquer coisa:**

```bash
python3 --version
```
```
# esperado: Python 3.10.12  (qualquer 3.10 ou superior serve)
```

*Se aparecer `Python 3.8.x` ou menos* → siga para "instalar versão mais nova" (§3.2.3).
*Se aparecer `command not found`* → o Python não está instalado (raro; acontece em contêineres
enxutos):

```bash
sudo apt update && sudo apt install -y python3
```

Agora instale as duas peças que o Debian/Ubuntu **separam do Python** e que quase todo
tutorial esquece:

```bash
sudo apt install -y python3-venv python3-pip
```
> `python3-venv` permite criar ambientes isolados; `python3-pip` instala bibliotecas.
> No Debian/Ubuntu eles vêm em pacotes à parte por decisão da distribuição — é a causa nº 1
> do erro `No module named venv` logo no primeiro dia.

Verifique:

```bash
python3 -m venv --help | head -1
```
```
# esperado: usage: venv [-h] [--system-site-packages] [--symlinks | --copies] ...
```

```bash
python3 -m pip --version
```
```
# esperado: pip 22.0.2 from /usr/lib/python3/dist-packages/pip (python 3.10)
```

### 3.2.2 Fedora / RHEL / Rocky / AlmaLinux

```bash
python3 --version
```
```
# esperado: Python 3.12.x (Fedora 40+) ou Python 3.9.x (RHEL 9)
```

No RHEL 9 o padrão é 3.9 — abaixo do mínimo deste curso. Instale uma versão paralela
(o RHEL suporta isso oficialmente, e **não** substitui o Python do sistema):

```bash
sudo dnf install -y python3.12 python3.12-pip
```
```bash
python3.12 --version
# esperado: Python 3.12.x
```

No Fedora, o venv já vem embutido. No RHEL, garanta:

```bash
sudo dnf install -y python3-pip
```

> ⚠️ **Nunca** faça `sudo dnf remove python3` nem substitua o binário `/usr/bin/python3`
> em RHEL/CentOS. O gerenciador de pacotes `dnf` **é escrito em Python** e usa esse
> interpretador. Trocá-lo transforma a máquina em tijolo — é um clássico, e o conserto
> envolve live-USB.

### 3.2.3 Instalar uma versão mais nova sem quebrar o sistema (qualquer Linux)

Três caminhos. **Recomendação: `uv`**, se você não tiver preferência.

| Método | Quando usar | Prós | Contras |
|---|---|---|---|
| **`uv`** (Astral) | padrão hoje para projetos novos | rapidíssimo; instala Python *e* pacotes; um binário só | ferramenta jovem (2024→) |
| **`pyenv`** | quando você precisa de muitas versões e controle fino | maduro, funciona há uma década | compila do fonte: lento, precisa de dependências de build |
| **deadsnakes PPA** (Ubuntu) | quando você quer pacote `.deb` do sistema | integra com apt | repositório de terceiro |

**Com `uv`:**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```
> Baixa e instala o binário `uv` em `~/.local/bin`. Leia o script antes se estiver em
> máquina corporativa — canalizar `curl` para `sh` executa código remoto sem revisão, e isso
> merece uma olhada consciente, não um hábito.

```bash
uv --version
# esperado: uv 0.12.5 (ou superior)
```
*Se der `command not found`* → o `~/.local/bin` não está no PATH. Ver §3.9.

```bash
uv python install 3.13
uv python list
# esperado: linha contendo cpython-3.13.x com o caminho da instalação
```

**Com `pyenv`:**

```bash
sudo apt install -y make build-essential libssl-dev zlib1g-dev libbz2-dev \
  libreadline-dev libsqlite3-dev curl libncursesw5-dev xz-utils tk-dev \
  libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev
```
> Dependências para **compilar** o Python. Faltando qualquer uma, a compilação termina
> "com sucesso" mas sem alguns módulos (`sqlite3`, `lzma`, `ssl`) — e o erro só aparece
> semanas depois. É a armadilha clássica do pyenv.

```bash
curl -fsSL https://pyenv.run | bash
```

Adicione ao `~/.bashrc` (ou `~/.zshrc`):

```bash
export PYENV_ROOT="$HOME/.pyenv"
[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init - bash)"
```

```bash
exec "$SHELL"          # recarrega o shell — sem isso, "não pega"
pyenv install 3.13.15
pyenv global 3.13.15
python --version
# esperado: Python 3.13.15
```

---

## 3.3 Python — macOS

### 3.3.1 O aviso que economiza um dia

O macOS traz um `python3` do sistema (parte das Command Line Tools). Ele funciona, mas é
antigo e a Apple pode trocá-lo numa atualização do sistema, quebrando seus ambientes.
**Não construa nada em cima dele.** Instale o seu próprio.

```bash
python3 --version
# se responder algo como Python 3.9.6, é o do sistema — instale outro
```

### 3.3.2 Com Homebrew (recomendado)

Instale o Homebrew, se ainda não tiver:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

**Apple Silicon (M1/M2/M3/M4)** — o Homebrew instala em `/opt/homebrew`, que **não** está no
PATH por padrão. Este passo é obrigatório e é onde a maioria trava:

```bash
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"
```

**Intel** — instala em `/usr/local`, que já está no PATH. Nada a fazer.

```bash
brew --version
# esperado: Homebrew 4.x.x
```

```bash
brew install python@3.13
python3.13 --version
# esperado: Python 3.13.x
```

> **Diferença Intel × Apple Silicon que importa:** em Apple Silicon, NumPy e SciPy usam o
> **Accelerate** framework da Apple para álgebra linear; em Intel, usam OpenBLAS. Os
> resultados podem diferir na **15ª casa decimal**. Isso não é bug: é aritmética de ponto
> flutuante com ordens de soma diferentes. Se você comparar resultados entre um Mac M2 e um
> servidor Linux e vir diferença em `1e-15`, é isso. Ver
> [75-armadilhas.md](75-armadilhas.md), seção sobre soma numérica.

### 3.3.3 Com o instalador oficial

Baixe de <https://www.python.org/downloads/macos/>, abra o `.pkg`, siga o assistente.
Depois, **rode o script que a instalação deixa** (senão `pip` falha com erro de certificado):

```bash
/Applications/Python\ 3.13/Install\ Certificates.command
```
> Instala os certificados raiz para o Python — o macOS não os compartilha com ele.
> Sem isso: `SSL: CERTIFICATE_VERIFY_FAILED` em qualquer `pip install`.

---

## 3.4 Python — Windows

### 3.4.1 Qual caminho escolher

| Caminho | Recomendado para | Por quê |
|---|---|---|
| **WSL2 + Ubuntu** | ✅ **quem pretende trabalhar com dados a sério** | tudo que você lerá na internet assume Linux; caminhos, permissões e comandos batem |
| **Python nativo** | quem quer só rodar os exemplos, ou precisa integrar com Excel/Power BI | mais simples, integra com o resto do Windows |

**Recomendação:** se você tem 30 minutos e não depende de software Windows-only,
**instale o WSL2**. Se tem 5 minutos ou vai integrar com Excel, use nativo. Os dois funcionam
para este curso.

### 3.4.2 Nativo — via winget (mais simples)

No PowerShell:

```powershell
winget install --id Python.Python.3.13 -e
```

Feche e reabra o PowerShell (o PATH só é lido na abertura):

```powershell
python --version
```
```
# esperado: Python 3.13.x
```

*Se abrir a Microsoft Store em vez de mostrar a versão* → é o "alias de execução de
aplicativo" do Windows. Desligue-o:
**Configurações → Aplicativos → Configurações avançadas de aplicativo →
Aliases de execução de aplicativo** → desative `python.exe` e `python3.exe`.

### 3.4.3 Nativo — via instalador oficial

Baixe de <https://www.python.org/downloads/windows/>. No assistente:

- ☑️ **"Add python.exe to PATH"** — marque. Não marcar é o erro nº 1 no Windows.
- Escolha "Customize installation" → marque `pip`, `py launcher`, `tcl/tk`.

```powershell
py -0
```
```
# esperado: lista de versões instaladas, ex.:
#  -V:3.13 *        Python 3.13 (64-bit)
```
> O `py` é o *Python Launcher* — exclusivo do Windows e a melhor coisa do ecossistema lá.
> Ele resolve qual Python usar: `py -3.13 script.py`.

### 3.4.4 WSL2 (recomendado)

No PowerShell **como administrador**:

```powershell
wsl --install -d Ubuntu-24.04
```
> Instala o subsistema Linux e a distribuição Ubuntu 24.04. Requer Windows 10 versão 2004+
> ou Windows 11, e reinicialização.

Depois de reiniciar e criar usuário/senha no Ubuntu:

```bash
python3 --version
# esperado: Python 3.12.x (Ubuntu 24.04)
sudo apt update && sudo apt install -y python3-venv python3-pip
```

**Regra de ouro do WSL2:** mantenha seus arquivos **dentro** do Linux (`/home/você/`), não em
`/mnt/c/`. Acesso a `/mnt/c` atravessa uma ponte de sistema de arquivos e é **de 5 a 20 vezes
mais lento**. Ler um CSV de 1 GB em `/mnt/c` pode levar minutos; em `/home`, segundos.

---

## 3.5 Ambiente isolado (venv) — o passo que evita 80% dos problemas futuros

**Não instale bibliotecas no Python do sistema.** Um ambiente virtual é uma pasta com uma
cópia do Python e das bibliotecas *daquele projeto*. Projetos diferentes, versões diferentes,
sem conflito.

```bash
mkdir -p ~/estatistica && cd ~/estatistica
python3 -m venv .venv
```
> Cria a pasta `.venv` com um Python isolado.

**Ativar** (é preciso a cada terminal novo):

| Sistema / shell | Comando |
|---|---|
| Linux, macOS, WSL (bash/zsh) | `source .venv/bin/activate` |
| Windows PowerShell | `.venv\Scripts\Activate.ps1` |
| Windows cmd.exe | `.venv\Scripts\activate.bat` |
| fish | `source .venv/bin/activate.fish` |

```bash
which python        # Linux/macOS
```
```
# esperado: /home/você/estatistica/.venv/bin/python   (dentro do .venv!)
```

*No PowerShell, se der `execução de scripts foi desabilitada neste sistema`:*

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```
> Permite rodar scripts locais assinados ou próprios, só para o seu usuário.
> É a configuração recomendada pela Microsoft para desenvolvimento.

**Desativar:** `deactivate`.

---

## 3.6 Bibliotecas científicas

Com o venv **ativado**:

```bash
python -m pip install --upgrade pip
```
```
# esperado: Successfully installed pip-25.x  (ou superior)
```

```bash
python -m pip install numpy scipy pandas matplotlib statsmodels
```

Verifique (comando testado em 20/08/2026):

```bash
python -c "import numpy,scipy,pandas,matplotlib,statsmodels as sm; print('numpy',numpy.__version__); print('scipy',scipy.__version__); print('pandas',pandas.__version__); print('matplotlib',matplotlib.__version__); print('statsmodels',sm.__version__)"
```
```
# saída real obtida em Python 3.10.12, Ubuntu 22.04.5, 20/08/2026:
# numpy 2.2.6
# scipy 1.15.3
# pandas 2.3.3
# matplotlib 3.10.9
# statsmodels 0.14.6
```

> **Leia com atenção o que acabou de acontecer.** A versão atual do NumPy em 20/08/2026 é a
> **2.5.2**, mas o `pip` instalou a **2.2.6**. Não é bug nem cache: o NumPy 2.5 exige
> **Python ≥ 3.12**, e a máquina tem 3.10. O `pip` resolveu, silenciosamente e corretamente,
> a versão mais nova compatível.
> **Lição:** "instalei a última versão" quase nunca é verdade — você instalou a última versão
> *compatível com o seu Python*. Quando um exemplo da internet não funciona com o seu pacote
> "atualizado", esta costuma ser a explicação. Confira sempre com `--version`, nunca por fé.

**Teste funcional** (não basta importar; tem que calcular):

```bash
python -c "import numpy as np; x=np.array([2.,4.,4.,4.,5.,5.,7.,9.]); print(x.mean(), x.std(), x.std(ddof=1))"
```
```
# esperado: 5.0 2.0 2.13808993529939
```
> Guarde este exemplo: `std()` do NumPy usa `ddof=0` (divide por *n*) e o `stdev` do Python
> e o `sd` do R usam *n−1*. **São dois números diferentes para os mesmos dados**, e a
> diferença é real, não arredondamento. O porquê está em
> [13-medidas-de-dispersao.md](13-medidas-de-dispersao.md). É a incompatibilidade silenciosa
> mais comum entre ferramentas.

### Com `uv` (alternativa moderna e muito mais rápida)

```bash
uv venv
source .venv/bin/activate
uv pip install numpy scipy pandas matplotlib statsmodels
```
> Mesmo resultado, tipicamente 10 a 100× mais rápido que o `pip`. A sintaxe é
> deliberadamente idêntica.

---

## 3.7 JupyterLab (caderno interativo)

```bash
python -m pip install jupyterlab
jupyter lab
```
> Abre o navegador em `http://localhost:8888/lab`.

```bash
jupyter --version
```
```
# esperado: várias linhas, incluindo  jupyterlab : 4.x.x
```

*Se o navegador não abrir:* copie a URL com `token=` que aparece no terminal e cole no
navegador. Em WSL2 isso é o normal — o Linux não sabe abrir o navegador do Windows.

**Parar:** `Ctrl+C` duas vezes no terminal.

⚠️ **Alerta de reprodutibilidade, não de instalação:** notebooks guardam a *saída* das
células, não a *ordem* em que você as executou. Um notebook pode mostrar resultados que
nenhuma execução limpa reproduz. Antes de mandar para alguém, sempre:
**Kernel → Restart Kernel and Run All Cells**. Se quebrar, era mentira.

---

## 3.8 R, RStudio, JASP, jamovi e planilha

### 3.8.1 R (versão 4.6.1, "Happy Hop", 24/06/2026)

**Ubuntu/Debian** — o R do `apt` costuma estar anos atrasado; use o repositório oficial do CRAN:

```bash
sudo apt install -y --no-install-recommends software-properties-common dirmngr
wget -qO- https://cloud.r-project.org/bin/linux/ubuntu/marutter_pubkey.asc \
  | sudo tee -a /etc/apt/trusted.gpg.d/cran_ubuntu_key.asc
sudo add-apt-repository "deb https://cloud.r-project.org/bin/linux/ubuntu $(lsb_release -cs)-cran40/"
sudo apt update && sudo apt install -y r-base r-base-dev
```

```bash
R --version | head -1
# esperado: R version 4.6.1 (2026-06-24) -- "Happy Hop"
```

**Fedora:** `sudo dnf install -y R`
**macOS:** `brew install --cask r` — ou o `.pkg` de <https://cloud.r-project.org/bin/macosx/>
(atenção: há pacotes distintos para Apple Silicon e Intel).
**Windows:** `winget install --id RProject.R -e` — ou o instalador de
<https://cloud.r-project.org/bin/windows/base/>.
No Windows, instale também o **Rtools** (<https://cran.r-project.org/bin/windows/Rtools/>) se
for compilar pacotes; sem ele, `install.packages()` falha em pacotes com código C/Fortran.

Teste dentro do R:

```r
sd(c(2,4,4,4,5,5,7,9))
# esperado: [1] 2.13809
q()
```

### 3.8.2 RStudio ou Positron

**RStudio Desktop** (grátis, versão Open Source): <https://posit.co/download/rstudio-desktop/>
Instale o R **antes** — o RStudio é só a interface e não traz o R junto.

```bash
# Ubuntu, depois de baixar o .deb:
sudo apt install -y ./rstudio-*.deb
```

**Positron** (o sucessor da Posit, baseado no VS Code, suporta R **e** Python no mesmo
ambiente): <https://positron.posit.co/>. É onde a Posit está investindo. Se você usa os dois
idiomas, vale começar por ele. Se usa só R, o RStudio continua mais completo e mais
documentado — *opinião profissional, não consenso*.

### 3.8.3 JASP e jamovi (estatística clicando, sem programar)

Ambos são **gratuitos, de código aberto**, e produzem resultados de qualidade publicável.
São a melhor resposta para "preciso fazer isso e não vou aprender a programar".

| | JASP 0.98.1 (07/07/2026) | jamovi 28.2 (13/08/2026) |
|---|---|---|
| Base | C++ e R | R |
| Diferencial | **estatística bayesiana** lado a lado com a clássica | módulos da comunidade; planilha embutida |
| Parecido com | SPSS | SPSS / planilha |
| Licença | AGPL v3 | AGPL v3 |
| Download | <https://jasp-stats.org/download/> | <https://www.jamovi.org/download.html> |

Linux: ambos oferecem **Flatpak**, que é o caminho de menor atrito:

```bash
flatpak install flathub org.jaspstats.JASP
flatpak run org.jaspstats.JASP
```

### 3.8.4 LibreOffice Calc (planilha grátis)

```bash
sudo apt install -y libreoffice-calc     # Debian/Ubuntu
sudo dnf install -y libreoffice-calc     # Fedora
brew install --cask libreoffice          # macOS
winget install --id TheDocumentFoundation.LibreOffice -e   # Windows
```

Funções equivalentes às deste curso (nomes em português na interface em pt-BR):

| Medida | LibreOffice / Excel pt-BR | Excel en-US |
|---|---|---|
| média | `=MÉDIA(A1:A100)` | `=AVERAGE(...)` |
| mediana | `=MED(A1:A100)` | `=MEDIAN(...)` |
| desvio padrão amostral (n−1) | `=DESVPAD.A(A1:A100)` | `=STDEV.S(...)` |
| desvio padrão populacional (n) | `=DESVPAD.P(A1:A100)` | `=STDEV.P(...)` |
| quartil | `=QUARTIL(A1:A100; 1)` | `=QUARTILE(...)` |
| percentil | `=PERCENTIL(A1:A100; 0,95)` | `=PERCENTILE(...)` |

⚠️ Duas armadilhas de planilha que atrapalham gente experiente:
1. **`DESVPAD` (sem sufixo) é obsoleto** e equivale a `DESVPAD.A`. Se o arquivo veio de outra
   pessoa, confira qual foi usada — a diferença entre `.A` e `.P` é real.
2. Na configuração em português, o **separador de argumentos é `;`**, não `,`. Colar fórmula
   de um site em inglês quase sempre falha por isso.

### 3.8.5 Git e editor

```bash
sudo apt install -y git                      # Debian/Ubuntu
brew install git                             # macOS
winget install --id Git.Git -e               # Windows
git --version
# esperado: git version 2.34.1 (ou superior)
```

```bash
# VS Code
sudo snap install --classic code             # Ubuntu
brew install --cask visual-studio-code       # macOS
winget install --id Microsoft.VisualStudioCode -e   # Windows
```
Extensões úteis: **Python** (Microsoft), **Jupyter** (Microsoft), **Data Wrangler**
(Microsoft, visualiza DataFrames), **R** (REditorSupport) se usar R.

---

## 3.9 PATH e variáveis de ambiente

**O sintoma:** você instalou, mas o terminal responde `command not found`.
**A causa quase sempre:** o binário existe, mas a pasta dele não está no PATH — a lista de
diretórios onde o shell procura programas.

Ver o PATH:

```bash
echo $PATH            # Linux, macOS, WSL
```
```powershell
$env:PATH -split ';'  # Windows PowerShell
```

Descobrir onde o programa foi parar:

```bash
ls -l ~/.local/bin/    # destino típico de instalações "--user" e do uv
which -a python3       # mostra TODOS os python3 no PATH, na ordem de prioridade
```

Corrigir — **em qual arquivo mexer**:

| Shell / sistema | Arquivo | Observação |
|---|---|---|
| bash (Linux) | `~/.bashrc` | lido em terminal interativo |
| bash (macOS) | `~/.bash_profile` | o macOS trata terminais como *login shell* |
| zsh (macOS padrão desde Catalina) | `~/.zshrc`; variáveis de ambiente em `~/.zprofile` | — |
| fish | `~/.config/fish/config.fish` | ou `fish_add_path ~/.local/bin` |
| Windows | Configurações → "Editar variáveis de ambiente do sistema" | ou `[Environment]::SetEnvironmentVariable(...)` |

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### Por que "não pegou" antes de reabrir o terminal

Um processo recebe uma **cópia** das variáveis de ambiente **no instante em que nasce**.
Alterar o `~/.bashrc` muda o que os *próximos* shells vão ler; não toca no que já está
rodando. Não é lentidão nem cache: é como o modelo de processos do Unix funciona desde 1970,
e o Windows faz o equivalente. Daí `source ~/.bashrc` (relê o arquivo no shell atual) ou
abrir um terminal novo.

E daí também um erro caro: **no VS Code, o terminal integrado herda o ambiente de quando o
VS Code foi aberto**. Mudou o PATH e o VS Code não vê? Feche o VS Code inteiro, não só a aba.

---

## 3.10 Permissões — e por que `sudo pip` é uma péssima ideia

**Nunca faça:**

```bash
sudo pip install pandas          # ❌ NÃO
sudo pip install --upgrade pip   # ❌ PIOR AINDA
```

Três motivos concretos, do mais imediato ao mais grave:

1. **Você quebra o gerenciador de pacotes da distribuição.** Em Ubuntu e Fedora, ferramentas
   do sistema (`apt`, `dnf`, `firewalld`, `netplan`) são escritas em Python e dependem de
   versões específicas de bibliotecas. O `pip` como root sobrescreve essas versões sem avisar
   ao `apt`, que continua achando que a antiga está lá. O resultado aparece dias depois,
   como um `apt upgrade` que falha e não conserta.
2. **Você executa código de terceiros como root.** Instalar um pacote roda o script de
   build do autor. Como root, um pacote comprometido — ou apenas com nome parecido com o que
   você queria digitar — tem acesso à máquina inteira.
3. **Você não consegue desfazer com precisão.** Não há registro confiável do que foi
   sobrescrito.

**O jeito certo**, em ordem de preferência:

```bash
# 1. venv (recomendado, sempre)
python3 -m venv .venv && source .venv/bin/activate && pip install pandas

# 2. instalação por usuário, sem root
python3 -m pip install --user pandas

# 3. ferramenta de linha de comando isolada
pipx install jupyterlab
```

No Python 3.11+ em Debian/Ubuntu/Fedora, o próprio sistema passou a **bloquear** a instalação
global com a mensagem `error: externally-managed-environment` (definida na
[PEP 668](https://peps.python.org/pep-0668/)). Isso é proteção, não obstáculo.
A tentação é usar `--break-system-packages`. O nome da opção foi escolhido para desencorajar,
e o conselho é: não use, crie um venv.

---

## 3.11 Rede corporativa: proxy, certificado e registry interno

Se você está atrás de proxy, o `pip` falha com `Connection timed out` ou
`SSLError: CERTIFICATE_VERIFY_FAILED`.

```bash
export HTTP_PROXY="http://usuario:senha@proxy.empresa.com:8080"
export HTTPS_PROXY="$HTTP_PROXY"
export NO_PROXY="localhost,127.0.0.1,.empresa.com"
```

⚠️ **Erro que custa uma tarde:** `NO_PROXY` precisa ser uma lista **separada por vírgulas,
sem espaços**. Um espaço depois da vírgula faz bibliotecas Python (`requests`, `urllib3`)
ignorarem a entrada seguinte — e aí conexões a `localhost` vão para o proxy e morrem com
timeout. Se o Jupyter local parou de abrir depois que você configurou proxy, é isto.

Certificado interno (a empresa inspeciona TLS):

```bash
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
export SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt
pip config set global.cert /caminho/para/certificado-da-empresa.pem
```

Espelho interno de PyPI (Nexus, Artifactory):

```bash
pip config set global.index-url https://nexus.empresa.com/repository/pypi/simple
pip config set global.trusted-host nexus.empresa.com
```

Para R:

```r
options(repos = c(CRAN = "https://cran.empresa.com"))
# permanente: coloque a linha no arquivo ~/.Rprofile
```

> ❌ Nunca use `pip install --trusted-host pypi.org` "para funcionar logo". Isso desativa a
> verificação de certificado e abre a porta para injeção de pacote no meio do caminho.
> Peça o certificado ao time de infraestrutura — é pedido de 5 minutos.

---

## 3.12 Conviver com várias versões

| Situação | Solução |
|---|---|
| Dois projetos, bibliotecas incompatíveis | um **venv por projeto**. Sempre. |
| Dois projetos, versões de Python diferentes | `uv python install 3.11 3.13` ou `pyenv local 3.11.9` |
| Python do sistema + o seu | nunca sobreponha; use `python3.13` explícito ou `venv` |
| Windows, várias versões | `py -3.11 script.py`, `py -3.13 script.py` |
| R, várias versões | `rig` (<https://github.com/r-lib/rig>) — o `pyenv` do R |
| Bibliotecas R por projeto | `renv::init()` dentro do projeto |

---

## 3.13 Reprodutibilidade — congelar o ambiente

Se a sua análise não roda igual daqui a seis meses, ela não é verificável, e uma análise
não verificável não é análise.

```bash
pip freeze > requirements.txt      # grava as versões exatas em uso
cat requirements.txt
```
```
# exemplo real (Python 3.10.12, 20/08/2026):
# numpy==2.2.6
# pandas==2.3.3
# scipy==1.15.3
```

Reconstruir depois, em qualquer máquina:

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

Fixe também a versão do Python:

```bash
echo "3.13.15" > .python-version    # lido por pyenv e por uv
```

Com `uv`, use `uv.lock` (trava a árvore inteira de dependências, incluindo as indiretas):

```bash
uv init && uv add numpy pandas && uv sync
```

Em R: `renv::init()` e depois `renv::snapshot()`.

**Camada máxima — container.** Se o resultado precisa ser idêntico daqui a 5 anos:

```dockerfile
FROM python:3.13.15-slim
WORKDIR /analise
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "analise.py"]
```
```bash
docker build -t minha-analise . && docker run --rm minha-analise
```
> Repare no `3.13.15-slim`, não `3.13-slim` nem `latest`. Tag flutuante é irreprodutibilidade
> com passo agendado.

---

## 3.14 Atualizar — e voltar atrás

```bash
pip list --outdated                       # o que está velho
pip install --upgrade pandas              # atualiza um pacote
pip install "pandas==2.2.3"               # volta a uma versão específica
```

**Antes de atualizar qualquer coisa em análise que está em uso:**

```bash
cp requirements.txt requirements.backup.txt
```

> ⚠️ **Atualização nunca é neutra em estatística.** Exemplos reais de mudanças que alteram
> resultados: o pandas 2.0 mudou o tratamento de valores ausentes em `groupby`; o NumPy 2.0
> mudou regras de promoção de tipo (um `float32` que virava `float64` agora pode não virar).
> Números *mudam*, silenciosamente, e continuam parecendo corretos.
> **Regra:** ao atualizar, rode a análise antiga e **compare os números**. Se você não tem
> como comparar, você não tem como atualizar com segurança — e isso é um problema do seu
> processo, não da biblioteca.

---

## 3.15 Desinstalar por completo

```bash
# bibliotecas de um projeto: apague o venv inteiro
rm -rf ~/estatistica/.venv

# cache do pip (costuma ter 1–5 GB)
pip cache purge
rm -rf ~/.cache/pip                       # Linux
rm -rf ~/Library/Caches/pip               # macOS
# Windows: %LocalAppData%\pip\Cache

# Python instalado via apt/brew/winget
sudo apt remove --purge python3.13 && sudo apt autoremove   # Ubuntu
brew uninstall python@3.13                                   # macOS
winget uninstall --id Python.Python.3.13                     # Windows

# pyenv
rm -rf ~/.pyenv          # + remova as 3 linhas do ~/.bashrc

# uv
rm -rf ~/.local/bin/uv ~/.local/share/uv ~/.cache/uv

# Jupyter (deixa rastros em 3 lugares)
pip uninstall jupyterlab
rm -rf ~/.jupyter ~/.local/share/jupyter ~/.ipython
```

**O que fica para trás mesmo assim** (e ninguém avisa):

- `~/.config/matplotlib/` — configuração e cache de fontes
- `~/.local/share/jupyter/kernels/` — *kernels* apontando para venvs que não existem mais;
  causa clássica do Jupyter que abre e trava em "Connecting to kernel"
- `~/.Rprofile`, `~/R/` — bibliotecas de R por usuário
- `~/.config/JASP/`, `~/.jamovi/`

Listar kernels órfãos: `jupyter kernelspec list` → remover: `jupyter kernelspec remove NOME`.

---

## 3.16 Requisitos reais

| Recurso | Mínimo | Confortável | Observação |
|---|---|---|---|
| Disco | 300 MB (Python só) | 5 GB | NumPy+SciPy+pandas+matplotlib ≈ 800 MB; R + tidyverse ≈ 2 GB |
| RAM | 2 GB | 8 GB | pandas carrega o CSV **inteiro** na memória, tipicamente ocupando de 2× a 10× o tamanho do arquivo |
| CPU | qualquer x86-64 ou ARM64 | — | GPU **não** é usada em estatística descritiva |
| Internet | só para baixar | — | tudo roda offline depois |
| Conta obrigatória | **nenhuma** | — | Colab pede conta Google; JupyterLite não pede nada |
| Cartão de crédito | **nunca** | — | tudo neste manual é gratuito e sem cadastro pago |

---

## 3.17 Solução de problemas — mensagens literais

| Mensagem de erro | Causa provável | Correção |
|---|---|---|
| `command not found: python` (Linux/macOS) | no Linux/macOS o binário chama-se `python3` | use `python3`, ou ative um venv (dentro dele, `python` funciona) |
| `bash: pip: command not found` | pip não instalado ou fora do PATH | `python3 -m pip --version`; se falhar, `sudo apt install python3-pip` |
| `No module named venv` | Debian/Ubuntu separam o venv em outro pacote | `sudo apt install python3-venv` |
| `error: externally-managed-environment` | PEP 668: proibido instalar no Python do sistema | crie um venv. **Não** use `--break-system-packages` |
| `EACCES: permission denied` / `Permission denied: '/usr/lib/python3'` | tentando instalar como usuário comum em diretório do sistema | venv, ou `pip install --user` |
| `SSL: CERTIFICATE_VERIFY_FAILED` | certificados ausentes (macOS) ou proxy com TLS inspecionado | macOS: rodar `Install Certificates.command`; corporativo: `REQUESTS_CA_BUNDLE` (§3.11) |
| `Could not find a version that satisfies the requirement numpy==2.5.2` | essa versão não suporta o seu Python | `python3 --version` e consulte a exigência do pacote; instale o que for compatível ou atualize o Python |
| `ModuleNotFoundError: No module named 'numpy'` **depois** de instalar | instalou num Python e está rodando com outro | `which python` e `python -m pip list`; ative o venv certo |
| `ImportError: numpy.core.multiarray failed to import` | mistura de NumPy 1.x e 2.x, ou pacote compilado contra outra versão | `pip install --force-reinstall numpy` ou recriar o venv do zero |
| Windows: abre a Microsoft Store ao digitar `python` | alias de execução de aplicativo | desative em Configurações → Aliases de execução de aplicativo |
| PowerShell: `execução de scripts foi desabilitada` | política de execução restritiva | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |
| `UserWarning: Matplotlib is building the font cache` (demora) | primeiro uso, montando cache de fontes | espere; só acontece uma vez |
| `Qt platform plugin "xcb" could not be loaded` (Linux) | falta biblioteca gráfica do sistema | `sudo apt install libxcb-cursor0 libgl1`; ou use o backend `Agg` para salvar em arquivo |
| Jupyter trava em "Connecting to kernel" | kernel apontando para um venv apagado | `jupyter kernelspec list` e remova os órfãos |
| R: `installation of package had non-zero exit status` | falta compilador ou biblioteca de sistema | Linux: `sudo apt install r-base-dev build-essential`; Windows: instale o **Rtools** |

---

## 3.18 Checklist de "ambiente pronto"

Rode uma linha por vez. Todas devem responder sem erro **antes** de você ir para o
[04-como-comecar.md](04-como-comecar.md).

```bash
python3 --version
```
```bash
python3 -m pip --version
```
```bash
python3 -m venv --help > /dev/null && echo "venv OK"
```
```bash
python3 -c "import statistics, math, random, csv; print('biblioteca padrao OK')"
```
```bash
python3 -c "import statistics as s; print(s.mean([1,2,3,4]), s.median([1,2,3,4]), round(s.stdev([1,2,3,4]),4))"
```
```
# esperado: 2.5 2.5 1.291
```

**Opcional** — só se você instalou as bibliotecas científicas:

```bash
python3 -c "import numpy, pandas; print('cientificas OK')"
```
```bash
R -e 'cat(sd(c(2,4,4,4,5,5,7,9)), "\n")' --no-save --quiet
```
```
# esperado: 2.13809
```

Marcou tudo? O ambiente está pronto. **Nada além do quarto comando é obrigatório para este
curso.**

---

## Autoteste

1. Por que este curso insiste que você **não** precisa instalar NumPy?
2. O que significa `error: externally-managed-environment` e qual é a resposta certa?
3. Você instalou o pandas e mesmo assim `import pandas` falha. Quais dois comandos você roda
   primeiro para diagnosticar?
4. Por que `sudo pip install` pode quebrar o `apt`?
5. `np.std(x)` e `statistics.stdev(x)` deram números diferentes para os mesmos dados. Qual dos
   dois está errado?
6. Você pediu NumPy 2.5.2 e o pip instalou 2.2.6 sem reclamar. O que aconteceu?
7. Por que alterar o PATH no `.bashrc` "não pega" no terminal já aberto?
8. Em WSL2, por que guardar os dados em `/mnt/c/Users/...` é má ideia?

<details><summary>Respostas</summary>

1. Porque escrever a conta à mão é o que ensina a medida; e porque zero dependência significa
   zero motivo para o exemplo parar de funcionar daqui a dois anos.
2. É a [PEP 668](https://peps.python.org/pep-0668/): a distribuição marcou o Python do sistema
   como gerenciado por ela, e o pip se recusa a mexer nele. Resposta certa: **criar um venv**.
   `--break-system-packages` faz exatamente o que o nome diz.
3. `which python` (qual interpretador está ativo) e `python -m pip list` (o que ele enxerga).
   Quase sempre são dois Pythons diferentes.
4. Porque `apt` e `dnf` são escritos em Python e dependem de versões específicas de
   bibliotecas. O pip como root as sobrescreve sem informar o gerenciador de pacotes, que
   segue acreditando na versão antiga.
5. **Nenhum dos dois.** `np.std` usa `ddof=0` (divide por *n*, desvio populacional);
   `statistics.stdev` usa *n−1* (amostral). Respondem a perguntas diferentes — ver
   [13](13-medidas-de-dispersao.md).
6. NumPy 2.5 exige Python ≥ 3.12 e a máquina tem 3.10; o pip escolheu a versão mais nova
   compatível. "Última versão" sempre quer dizer "última compatível com o seu Python".
7. Porque cada processo recebe uma **cópia** do ambiente ao nascer. Mudar o arquivo afeta os
   próximos shells; use `source ~/.bashrc` ou abra outro terminal.
8. Porque o acesso atravessa a ponte entre os sistemas de arquivos do Windows e do Linux,
   sendo de 5 a 20 vezes mais lento. Guarde em `/home/você/`.

</details>

---

## Fontes consultadas (20/08/2026)

- Python.org — releases 3.14.7 e 3.13.15 (05/08/2026): <https://www.python.org/downloads/>
- NumPy — 2.5.2 (09/08/2026), exigência de Python ≥ 3.12: <https://numpy.org/news/>
- SciPy 1.18 (jun/2026): <https://scipy.org/>
- CRAN — R 4.6.1 "Happy Hop" (24/06/2026): <https://cran.r-project.org/>
- Posit — RStudio Desktop e Positron: <https://posit.co/download/rstudio-desktop/> · <https://positron.posit.co/>
- JASP 0.98.1 (07/07/2026): <https://jasp-stats.org/download/>
- jamovi 28.2 (13/08/2026): <https://www.jamovi.org/releases.html>
- PEP 668 (ambientes gerenciados externamente): <https://peps.python.org/pep-0668/>
- Astral `uv` 0.12.5: <https://docs.astral.sh/uv/>
- **Verificado nesta máquina em 20/08/2026** (Ubuntu 22.04.5, Python 3.10.12): pip instalou
  numpy 2.2.6, scipy 1.15.3, pandas 2.3.3, matplotlib 3.10.9, statsmodels 0.14.6.

---

**Próximo:** [04-como-comecar.md](04-como-comecar.md) — do ambiente pronto ao primeiro
resumo estatístico honesto na tela.
