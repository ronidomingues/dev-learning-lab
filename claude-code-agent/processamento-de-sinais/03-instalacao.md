# 03 · Manual de instalação — do zero, por sistema operacional

`Nível: iniciante` · `Escrito e testado em: 14/08/2026`
`Ambiente de referência do autor: Ubuntu 22.04.5 · Python 3.10.12 · NumPy 2.2.6 · SciPy 1.15.3 · Matplotlib 3.10.9`

Este é um manual de campo. Siga na ordem, execute a verificação de cada passo, e
não improvise. Se a saída não bater com a esperada, a correção está logo abaixo do
comando ou na [tabela de erros](#solução-de-problemas--erros-literais).

**Versões de referência em agosto de 2026:**

| Software | Última estável | Mínima recomendada | Evitar |
|---|---|---|---|
| Python | 3.14.7 (05/08/2026) | 3.10 | 3.8 e anteriores (sem suporte) |
| NumPy | 2.5.2 (09/08/2026) | 1.24 | 1.x se for usar SciPy ≥ 1.18 |
| SciPy | 1.18.0 (19/06/2026) | 1.10 | — |
| Matplotlib | 3.10.x | 3.6 | — |
| GNU Octave | 11.3.0 (01/06/2026) | 8.0 | — |
| Audacity | 3.7.8 (29/06/2026) | 3.4 | 3.0.x (bugs de exportação) |
| GNU Radio | 3.10.12 estável; 4.0 em RC1 desde 03/2026 | 3.10 | 3.7 (Python 2, morto) |

> ⚠️ **SciPy 1.18 exige Python 3.12–3.14 e NumPy ≥ 2.0.** Se você está no Python
> 3.10 ou 3.11 (caso do Ubuntu 22.04 padrão), o `pip` instalará automaticamente a
> última versão compatível — 1.15.x — e isso está perfeitamente bem para este
> curso. Foi o que aconteceu na máquina de referência.

---

## 0 · Comece sem instalar nada (leia isto primeiro)

Você pode fazer os capítulos 01 a 20 inteiros sem instalar uma linha. Se hoje é o
seu primeiro dia, **use esta seção e instale depois**. Desistência no primeiro dia
costuma ser desistência de instalação, não de conteúdo.

### Opção A — Google Colab (recomendada para começar)

1. Abra <https://colab.research.google.com> (precisa de conta Google, gratuita).
2. `Arquivo → Novo notebook`.
3. Cole e execute:

```python
import numpy, scipy, matplotlib
print(numpy.__version__, scipy.__version__, matplotlib.__version__)
```

NumPy, SciPy e Matplotlib já vêm instalados. Não precisa de cartão de crédito.
Limitação: sessão morre após inatividade e você perde arquivos não salvos no Drive.

### Opção B — JupyterLite / Pyodide (sem conta nenhuma)

<https://jupyter.org/try-jupyter/lab/> roda Python **dentro do seu navegador**
via WebAssembly. Zero instalação, zero conta, zero servidor. NumPy e Matplotlib
funcionam; SciPy funciona parcialmente (`scipy.signal` sim). Ideal para os
primeiros exemplos.

### Opção C — Octave Online

<https://octave-online.net> roda Octave no navegador. Serve para executar código
MATLAB de livros e artigos sem comprar MATLAB.

### Opção D — Contêiner pronto (se você já tem Docker)

```bash
docker run -it --rm -p 8888:8888 quay.io/jupyter/scipy-notebook:latest
```

Sobe um JupyterLab com toda a pilha científica. Abra a URL com token que aparece
no terminal. **Verificação:** a URL abre e o `import scipy` funciona numa célula.

---

## 1 · Instalar Python

### 1.1 Linux — família Debian/Ubuntu

O Ubuntu 22.04 traz Python 3.10; o 24.04 traz 3.12; o 26.04 traz 3.13.
Qualquer um serve.

```bash
sudo apt update
```
Atualiza a lista de pacotes. Sem isso, o `apt install` pode instalar versão velha.

```bash
sudo apt install -y python3 python3-pip python3-venv
```
Instala o interpretador, o instalador de pacotes e o módulo de ambientes virtuais.
**O `python3-venv` é separado no Debian/Ubuntu** e sua ausência é a causa do erro
mais comum da seção 2.

**Verificação:**

```bash
python3 --version
# esperado: Python 3.10.12 (ou superior — qualquer 3.10+)
```

```bash
python3 -m venv --help > /dev/null && echo "venv OK"
# esperado: venv OK
```

**Se a saída for diferente:** se `python3` não existir, seu sistema é muito antigo
ou minimalista — instale pelo `apt` acima. Se aparecer `The virtual environment was
not created`, falta o `python3-venv` (veja a tabela de erros).

**Se você precisa de uma versão mais nova que a da distro** (ex.: Python 3.13 no
Ubuntu 22.04), use o repositório *deadsnakes*:

```bash
sudo add-apt-repository -y ppa:deadsnakes/ppa && sudo apt update
sudo apt install -y python3.13 python3.13-venv
python3.13 --version
# esperado: Python 3.13.x
```

PPA é mantido pela comunidade, não pela Canonical. É confiável e amplamente usado,
mas é uma dependência externa — em ambiente corporativo, verifique a política.

### 1.2 Linux — família Fedora/RHEL/Rocky

```bash
sudo dnf install -y python3 python3-pip
```

No Fedora, `venv` já vem no pacote base. Verificação idêntica à do Ubuntu.
Fedora 42+ traz Python 3.13.

```bash
python3 --version
# esperado: Python 3.13.x no Fedora 42; 3.9.x no RHEL 9 (ver aviso)
```

**RHEL/Rocky 9 traz Python 3.9, que é velho demais.** Instale um mais novo em
paralelo, sem tocar no do sistema:

```bash
sudo dnf install -y python3.12
python3.12 --version
```

⚠️ **Nunca** remova ou substitua o `python3` do sistema no Fedora/RHEL: o `dnf`
é escrito em Python e você inutiliza o gerenciador de pacotes da máquina. Este é
um dos jeitos mais rápidos de precisar reinstalar o sistema.

### 1.3 Linux — Arch

```bash
sudo pacman -S python python-pip python-numpy python-scipy python-matplotlib
python --version
```

No Arch, `python` **é** o Python 3. E o Arch usa "externally managed environment"
(PEP 668): o `pip install` global falha de propósito. Use `venv` (seção 2) ou os
pacotes `python-*` do repositório.

### 1.4 macOS

O macOS traz um Python de sistema antigo e reservado à Apple. **Não use.**
Instale o seu.

**Caminho recomendado: Homebrew.**

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```
Instala o Homebrew, o gerenciador de pacotes de fato do macOS.

Ao final, o instalador imprime duas linhas para adicionar ao seu perfil. **Elas
importam** — em Apple Silicon o Homebrew instala em `/opt/homebrew`, que não está
no PATH por padrão (em Intel é `/usr/local`, que está):

```bash
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
source ~/.zprofile
```
Apple Silicon (M1/M2/M3/M4). Em Mac Intel, troque `/opt/homebrew` por `/usr/local`.

```bash
brew install python@3.13
```

**Verificação:**

```bash
which python3
# esperado (Apple Silicon): /opt/homebrew/bin/python3
# esperado (Intel):        /usr/local/bin/python3
# ERRADO: /usr/bin/python3  ← esse é o da Apple; seu PATH não pegou
```

```bash
python3 --version
# esperado: Python 3.13.x
```

**Se aparecer `/usr/bin/python3`:** o `eval "$(brew shellenv)"` não foi para o
perfil, ou você não reabriu o terminal. Veja a seção [PATH](#5--path-e-variáveis-de-ambiente).

**Alternativa: instalador oficial** de <https://www.python.org/downloads/macos/>.
Funciona, mas dá mais trabalho para conviver com várias versões, e o instalador
mexe no `/Applications` e no PATH de um jeito que confunde depois. Prefira o Homebrew.

### 1.5 Windows

Aqui existe uma escolha real, e ela muda sua vida.

| Caminho | Quando escolher | Custo |
|---|---|---|
| **WSL2 (Ubuntu no Windows)** — recomendado | Você quer seguir tutoriais, papers e código do mundo real sem tradução | 1 h de instalação, ~3 GB de disco |
| **Python nativo do Windows** | Você só quer NumPy/SciPy/Matplotlib e integração com Excel/Windows | 10 min |

**Minha recomendação profissional:** WSL2. Praticamente toda ferramenta séria de
DSP (GNU Radio, SoX, ffmpeg, compiladores para DSP embarcado) tem instalação de
uma linha no Linux e um fim de semana no Windows nativo. Se você só vai usar
Python puro, o nativo basta.

#### 1.5.a WSL2

Abra o **PowerShell como Administrador**:

```powershell
wsl --install -d Ubuntu-24.04
```
Instala o subsistema Linux e o Ubuntu 24.04. Reinicie quando ele pedir.

Depois de reiniciar, abra "Ubuntu" no menu Iniciar, crie usuário e senha, e siga
**a seção 1.1 deste manual** dentro dele. Daqui em diante você está no Linux.

**Verificação:**

```powershell
wsl -l -v
# esperado:
#   NAME            STATE           VERSION
# * Ubuntu-24.04    Running         2      ← a VERSION tem de ser 2
```

**Se a VERSION for 1:** `wsl --set-version Ubuntu-24.04 2`. WSL1 não roda o
`sounddevice`/PortAudio nem tem desempenho de I/O decente.

#### 1.5.b Python nativo

```powershell
winget install --id Python.Python.3.13 -e
```
Instala pelo gerenciador de pacotes embutido no Windows 11 (e no 10 atualizado).

**Alternativa:** instalador de <https://www.python.org/downloads/windows/>.
⚠️ Na primeira tela, marque **"Add python.exe to PATH"**. Se esquecer, você cai
direto no erro `'python' não é reconhecido` da tabela de erros.

**Verificação** (feche e reabra o terminal antes):

```powershell
python --version
# esperado: Python 3.13.x
```

```powershell
py -0
# lista todas as versões instaladas; o `py` é o launcher oficial do Windows
```

**Se aparecer a Microsoft Store:** o Windows tem um "atalho de execução de app"
para `python` que abre a loja. Desligue em
`Configurações → Aplicativos → Configurações de aplicativo avançadas → Aliases de
execução de aplicativo` → desmarque `python.exe` e `python3.exe`.

---

## 2 · Ambiente virtual — obrigatório, não opcional

**Por quê:** dois projetos vão querer versões diferentes da mesma biblioteca. Sem
isolamento, um quebra o outro. E, em Linux, instalar pacote Python globalmente com
`sudo pip` pode sobrescrever o que o gerenciador de pacotes do sistema instalou e
quebrar ferramentas do sistema operacional — em Fedora/RHEL isso quebra o `dnf`.

Desde o PEP 668 (2023), Debian, Ubuntu, Fedora e Arch **bloqueiam** o `pip install`
global e mandam a mensagem `error: externally-managed-environment`. O bloqueio está
certo. Não use `--break-system-packages` para contorná-lo; o nome do parâmetro é
uma descrição honesta do que ele faz.

```bash
mkdir -p ~/dsp && cd ~/dsp
python3 -m venv .venv
```
Cria um Python isolado dentro da pasta `.venv`.

```bash
source .venv/bin/activate          # Linux, macOS, WSL
# .venv\Scripts\activate           # Windows PowerShell/CMD
```

**Verificação:**

```bash
which python
# esperado: /home/você/dsp/.venv/bin/python   ← dentro do .venv
```

```bash
python -c "import sys; print(sys.prefix)"
# esperado: /home/você/dsp/.venv
```

**Se apontar para `/usr/bin/python`:** o `activate` não rodou. No PowerShell, pode
ser bloqueio de script: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.

Para sair: `deactivate`.

### Alternativas ao venv, e quando usar cada uma

| Ferramenta | Use quando | Não use quando |
|---|---|---|
| `venv` + `pip` (padrão) | sempre que puder; é o que este curso usa | — |
| `uv` (Astral, Rust) | quer velocidade — 10 a 100× mais rápido que o pip | precisa de estabilidade de ferramenta antiga |
| `conda`/`mamba`/Miniforge | precisa de MKL, CUDA, GNU Radio, ou pacotes não-Python | quer instalação leve (Miniforge ≈ 500 MB) |
| `pyenv` / `mise` / `asdf` | precisa de **várias versões do Python** na mesma máquina | uma versão basta |
| Docker | precisa de reprodutibilidade total ou vai para produção | está aprendendo e quer atrito zero |

Instalação do `uv` (opcional, mas vale muito a pena):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv --version
```

Com `uv`, o equivalente ao passo acima é `uv venv && uv pip install numpy scipy matplotlib`,
e leva segundos em vez de minutos.

---

## 3 · Instalar a pilha de DSP em Python

Com o `.venv` **ativo**:

```bash
python -m pip install --upgrade pip
```
Atualiza o pip. Um pip velho baixa código-fonte e tenta compilar SciPy — o que
falha de dez formas diferentes. Um pip novo baixa um *wheel* pré-compilado.

```bash
pip install numpy scipy matplotlib
```
As três bibliotecas obrigatórias do curso. Baixa ~120 MB, ocupa ~400 MB instaladas.

**Verificação:**

```bash
python -c "import numpy, scipy, matplotlib; print('numpy', numpy.__version__); print('scipy', scipy.__version__); print('matplotlib', matplotlib.__version__)"
# esperado (exemplo real desta máquina, 14/08/2026):
# numpy 2.2.6
# scipy 1.15.3
# matplotlib 3.10.9
```

**Teste funcional de verdade** — não basta importar, tem que calcular:

```bash
python -c "
import numpy as np
from scipy import signal
t = np.arange(1000)/1000
x = np.sin(2*np.pi*50*t)
X = np.abs(np.fft.rfft(x))
print('pico em', np.argmax(X), 'Hz  (esperado: 50)')
b = signal.firwin(21, 0.2)
print('soma dos taps =', round(float(b.sum()), 6), ' (esperado: 1.0)')
"
```

Saída esperada, verificada em 14/08/2026:

```
pico em 50 Hz  (esperado: 50)
soma dos taps = 1.0  (esperado: 1.0)
```

**Se o pico não for 50:** algo muito errado no NumPy — reinstale o venv do zero.
**Se `soma dos taps` não for 1.0:** versão de SciPy exótica; reporte.

### Opcionais úteis

```bash
pip install jupyterlab
```
Ambiente de notebook — o ciclo de exploração natural em DSP. Verificação:
`jupyter lab --version` deve imprimir 4.x.

```bash
pip install soundfile librosa
```
`soundfile` lê e escreve WAV/FLAC/OGG (usa libsndfile, que vem no wheel).
`librosa` é a caixa de ferramentas de áudio musical (MFCC, CQT, beat tracking).
⚠️ `librosa` puxa `numba`, `scikit-learn` e mais ~800 MB. Instale **só quando
precisar**; este curso e o projeto-modelo não precisam.

```bash
pip install sounddevice
```
Tocar e gravar áudio ao vivo. **Depende do PortAudio, que é uma biblioteca C:**

- Linux: `sudo apt install -y libportaudio2` (Debian/Ubuntu) ou
  `sudo dnf install -y portaudio` (Fedora)
- macOS: `brew install portaudio`
- Windows: já vem no wheel
- WSL2: áudio funciona no WSLg (Windows 11), mas com latência ruim; para tempo
  real, use o Windows nativo

Verificação: `python -c "import sounddevice; print(sounddevice.query_devices())"`
deve listar seus dispositivos. Se der `PortAudioError`, falta a biblioteca C.

---

## 4 · Outras tecnologias do ecossistema

Não são obrigatórias para o curso, mas cada uma tem sua hora. Instale sob demanda.

### 4.1 Audacity — ver e ouvir áudio sem programar

Insubstituível para intuição: você **vê** o espectrograma e **ouve** o resultado
do filtro no mesmo lugar. Use no começo, sempre.

```bash
sudo apt install -y audacity          # Debian/Ubuntu
sudo dnf install -y audacity          # Fedora
brew install --cask audacity          # macOS
winget install --id Audacity.Audacity -e   # Windows
```

Verificação: abra, `Gerar → Tom` (440 Hz, 3 s), depois `Analisar → Plotar espectro`.
Deve aparecer um pico único em 440 Hz.

⚠️ A partir da versão 3.x o Audacity é da Muse Group e pergunta sobre telemetria na
primeira execução. É opcional; pode recusar. Se isso incomodar, use o *fork*
**Tenacity**, sem telemetria.

### 4.2 GNU Octave — rodar código MATLAB de graça

Praticamente todo livro clássico e boa parte dos papers trazem código MATLAB.
O Octave executa a maioria sem alteração.

```bash
sudo apt install -y octave octave-signal   # o pacote `octave-signal` é o equivalente ao Signal Processing Toolbox
sudo dnf install -y octave octave-signal
brew install octave
winget install --id GNU.Octave -e
```

Verificação:

```bash
octave --eval "pkg load signal; disp(fir1(4, 0.3))"
# esperado: quatro/cinco números somando ~1, sem erro de pacote
```

**Se der `package signal is not installed`:** no Ubuntu, `sudo apt install
octave-signal`; via Octave, `pkg install -forge signal` (precisa de compilador).

### 4.3 ffmpeg / SoX — converter formatos

Você vai receber MP3, M4A e OPUS, e as bibliotecas de análise querem WAV PCM.

```bash
sudo apt install -y ffmpeg sox
brew install ffmpeg sox
winget install --id Gyan.FFmpeg -e
```

Conversão canônica para análise (mono, 44,1 kHz, 16 bits):

```bash
ffmpeg -i entrada.mp3 -ac 1 -ar 44100 -acodec pcm_s16le saida.wav
```

### 4.4 GNU Radio + SDR — quando chegar em rádio (cap. 26)

Pesado. Só instale quando for fazer o capítulo 26 com hardware na mão.

```bash
sudo apt install -y gnuradio          # Ubuntu 24.04 traz 3.10.x
sudo dnf install -y gnuradio
brew install gnuradio                  # macOS: funciona, mas é o caminho mais frágil
```
No Windows, o caminho suportado é o instalador **Radioconda**
(<https://github.com/ryanvolz/radioconda>), não o `pip`.

Verificação: `gnuradio-companion` abre a interface gráfica; `python -c "import gnuradio; print(gnuradio.__file__)"`.

Hardware, com preço de agosto de 2026 (detalhes em [`80`](80-custos-e-licencas.md)):
RTL-SDR Blog V4 ≈ US$ 30–40 (**produção encerrada** — o chip R828D acabou; procure
o sucessor ou estoque remanescente), ADALM-PLUTO ≈ US$ 100–250, HackRF One ≈ US$ 340.

### 4.5 Editor

Qualquer um serve. VS Code com as extensões *Python* e *Jupyter* é o padrão de
mercado:

```bash
sudo snap install code --classic      # Ubuntu
brew install --cask visual-studio-code
winget install --id Microsoft.VisualStudioCode -e
```

⚠️ No VS Code, escolha o interpretador do `.venv`:
`Ctrl+Shift+P` → `Python: Select Interpreter` → aponte para `.venv/bin/python`.
Não fazer isso é a causa nº 1 de "instalei mas o import falha" dentro do editor.

---

## 5 · PATH e variáveis de ambiente

**O que é PATH:** a lista de pastas onde o sistema procura um programa quando você
digita o nome dele. Se o programa existe mas não está numa dessas pastas, você
recebe `command not found` — o arquivo está lá, o sistema é que não olha.

**Conferir:**

```bash
echo $PATH            # Linux, macOS, WSL
```
```powershell
$env:PATH -split ';'  # Windows PowerShell
```

**Qual arquivo editar:**

| Shell | Arquivo | Como descobrir o seu shell |
|---|---|---|
| bash (Linux padrão) | `~/.bashrc` | `echo $SHELL` |
| zsh (macOS padrão desde 2019) | `~/.zshrc` | `echo $SHELL` |
| fish | `~/.config/fish/config.fish` | — |
| PowerShell | caminho em `$PROFILE` | `notepad $PROFILE` |

**Adicionar uma pasta ao PATH (exemplo: binários locais do pip):**

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```
A segunda linha é a que quase todo mundo esquece.

> **"Editei o arquivo e não pegou."** O arquivo de perfil é lido **quando o shell
> começa**. Editá-lo não afeta um terminal já aberto. Ou rode `source ~/.bashrc`,
> ou feche e abra o terminal. No macOS, há uma pegadinha extra: terminais de login
> leem `~/.zprofile`, e não-login leem `~/.zshrc` — em caso de dúvida, ponha nos dois.

**Variáveis de ambiente que importam em DSP:**

| Variável | Para que serve |
|---|---|
| `MPLBACKEND=Agg` | força o Matplotlib a não tentar abrir janela (servidor, CI, WSL sem X) |
| `OMP_NUM_THREADS=4` | limita as threads da BLAS/FFT; útil para medir desempenho de forma reprodutível |
| `PYTHONPATH` | acrescenta pastas ao caminho de import. **Evite** — quase sempre é um venv mal feito disfarçado |
| `SINAL_FREQ_REDE` | do projeto-modelo: 50 na Europa, 60 no Brasil |

---

## 6 · Permissões — por que `sudo pip` é armadilha

Instalar com `sudo pip install` grava em `/usr/lib/python3/dist-packages`, o mesmo
lugar onde o `apt`/`dnf` grava. Quando as duas ferramentas escrevem lá:

1. O gerenciador do sistema perde o controle de quem é dono de cada arquivo.
2. Uma atualização do sistema pode sobrescrever sua versão, ou vice-versa.
3. Ferramentas do sistema escritas em Python (no Fedora/RHEL, o **`dnf`**; no
   Ubuntu, `apt`, `netplan`, `ubuntu-advantage`) podem quebrar.
4. Os arquivos ficam com dono `root` e você não consegue mais atualizá-los sem `sudo`,
   o que perpetua o problema.

**Caminho certo, em ordem de preferência:**

1. `venv` (isolado, descartável) ← use este
2. `pip install --user` (grava em `~/.local`, não precisa de `sudo`)
3. `pipx` para *aplicativos* de linha de comando (não para bibliotecas)
4. pacote da distro (`python3-numpy` etc.) quando quiser integração com o sistema

Se você já fez `sudo pip install` e a coisa está confusa: crie um venv limpo e
esqueça o global. Tentar "limpar" o global costuma custar mais que ignorá-lo.

---

## 7 · Rede corporativa

**Proxy:**

```bash
export HTTPS_PROXY=http://usuario:senha@proxy.empresa.com:8080
export HTTP_PROXY=$HTTPS_PROXY
pip install numpy
```
Ou permanentemente em `~/.config/pip/pip.conf` (Linux/macOS) /
`%APPDATA%\pip\pip.ini` (Windows):

```ini
[global]
proxy = http://proxy.empresa.com:8080
index-url = https://nexus.empresa.com/repository/pypi/simple
trusted-host = nexus.empresa.com
```

**Certificado interno (inspeção TLS):** o erro é
`SSLError: certificate verify failed`. A correção **certa** é apontar para o
certificado da empresa, não desligar a verificação:

```bash
export PIP_CERT=/caminho/para/ca-empresa.pem
export REQUESTS_CA_BUNDLE=/caminho/para/ca-empresa.pem
export SSL_CERT_FILE=/caminho/para/ca-empresa.pem
```

⚠️ `pip install --trusted-host pypi.org` funciona e desliga a verificação de
autenticidade do pacote. É aceitável como diagnóstico pontual, não como configuração
permanente — você passa a aceitar qualquer coisa que o proxy devolver.

**Firewall:** o `pip` precisa de HTTPS para `pypi.org` e `files.pythonhosted.org`.
Liberar só o primeiro é um erro comum e dá timeout no download.

---

## 8 · Conviver com várias versões

**Várias versões do Python na mesma máquina:**

```bash
curl https://pyenv.run | bash          # pyenv (Linux/macOS)
pyenv install 3.13.5
pyenv local 3.13.5                     # cria .python-version nesta pasta
python --version
```

Alternativa moderna e mais simples, que também gerencia Node, Rust etc.:

```bash
curl https://mise.run | sh
mise use python@3.13
```

No Windows nativo, o launcher `py` já resolve: `py -3.12 -m venv .venv`.

**Várias versões de biblioteca:** um venv por projeto. Sempre. Sem exceção.

---

## 9 · Reprodutibilidade

Sem isso, seu código funciona hoje e falha em seis meses — e você não vai saber por quê.

```bash
pip freeze > requirements.txt
```
Congela **todas** as versões, inclusive as transitivas.

```bash
pip install -r requirements.txt
```
Reconstrói o ambiente idêntico.

Arquivos que vale versionar no git junto do código:

| Arquivo | O que fixa |
|---|---|
| `requirements.txt` | versões de pacotes Python |
| `.python-version` | versão do interpretador (pyenv/mise) |
| `.tool-versions` | idem (asdf/mise) |
| `Dockerfile` | o sistema operacional inteiro |

Para reprodutibilidade forte, o `uv` gera `uv.lock` com hashes; `pip-tools`
(`pip-compile`) faz o equivalente para quem prefere pip.

**Reprodutibilidade específica de DSP** — e isso quase ninguém documenta:

- **Fixe a semente** de qualquer gerador aleatório: `rng = np.random.default_rng(42)`.
  Sem isso, seu teste de ruído passa hoje e falha amanhã.
- **Registre a taxa de amostragem** em todo arquivo e toda função. Metade dos bugs
  de DSP é taxa errada silenciosamente propagada.
- **Registre a versão da SciPy**: `scipy.signal` mudou padrões entre versões
  (ex.: `spectrogram` e `stft` foram substituídos por `ShortTimeFFT` na 1.12+, e
  os antigos estão legados). Código de 2019 pode produzir número diferente hoje.

---

## 10 · Atualizar e voltar atrás

```bash
pip list --outdated
```
Mostra o que está velho. Não atualize tudo de uma vez sem motivo.

```bash
pip install --upgrade scipy
```

**Voltar para uma versão específica:**

```bash
pip install "scipy==1.15.3"
```

**A forma mais segura de atualizar** — e a que eu uso: não atualize o venv, crie
outro. Testa lá, e se estiver bom, aponta o projeto para ele. `venv` é descartável
por natureza; tratá-lo como precioso é o erro conceitual.

```bash
python3 -m venv .venv-novo && source .venv-novo/bin/activate
pip install -r requirements.txt && python -m unittest discover -s tests
```

---

## 11 · Desinstalar por completo

**Pacotes Python:** apague a pasta do venv. É só isso.

```bash
deactivate 2>/dev/null; rm -rf ~/dsp/.venv
```

**Caches e restos que ficam para trás** (podem somar vários GB):

```bash
pip cache purge                     # cache de wheels do pip
rm -rf ~/.cache/pip                 # Linux
rm -rf ~/Library/Caches/pip         # macOS
rm -rf ~/.cache/matplotlib          # cache de fontes do Matplotlib
rm -rf ~/.local/share/jupyter ~/.jupyter   # kernels e config do Jupyter
rm -rf ~/.ipython
```
Windows: `%LOCALAPPDATA%\pip\Cache`, `%APPDATA%\jupyter`.

**Python do sistema:**

```bash
sudo apt remove --purge python3.13 python3.13-venv && sudo apt autoremove
brew uninstall python@3.13
winget uninstall Python.Python.3.13
```
⚠️ No Linux, **nunca** desinstale o `python3` padrão da distro (seção 1.2).

**pyenv:** `rm -rf ~/.pyenv` e remova as linhas correspondentes do `~/.bashrc`.

**Verificar que não sobrou nada:**

```bash
which -a python3 pip
# esperado: só os caminhos do sistema, nenhum do venv apagado
```

---

## Requisitos reais

| Item | Necessidade |
|---|---|
| Disco | Python + NumPy + SciPy + Matplotlib ≈ **1,2 GB**. Com JupyterLab, ~1,6 GB. Com librosa, +800 MB. Com GNU Radio, +2 GB |
| RAM | 4 GB bastam. FFT de 1 min de áudio em float64: ~50 MB |
| Arquitetura | x86-64 e ARM64 (Apple Silicon, Raspberry Pi 4/5) têm wheels prontos. ARM32 compila do fonte e demora horas |
| Conta obrigatória | **nenhuma** |
| Cartão de crédito | **nenhum**, nem no Colab gratuito |
| Licença | tudo aqui é livre: Python (PSF), NumPy/SciPy/Matplotlib (BSD), Octave/Audacity/GNU Radio (GPL). Detalhes em [`80`](80-custos-e-licencas.md) |
| Internet | só na instalação. Depois, o curso roda offline |

---

## Solução de problemas — erros literais

| Mensagem | Causa provável | Correção |
|---|---|---|
| `error: externally-managed-environment` | PEP 668: a distro bloqueia `pip` global (Debian 12+, Ubuntu 23.04+, Fedora 38+, Arch) | Crie e ative um venv (seção 2). Não use `--break-system-packages` |
| `The virtual environment was not created successfully because ensurepip is not available` | falta o pacote `python3-venv` (Debian/Ubuntu separam) | `sudo apt install python3.XX-venv` com o número da sua versão |
| `ModuleNotFoundError: No module named 'scipy'` | venv não ativado, ou o editor está usando outro interpretador | `source .venv/bin/activate`; no VS Code, `Python: Select Interpreter` |
| `'python' não é reconhecido como um comando interno ou externo` (Windows) | não marcou "Add python.exe to PATH" | Reinstale marcando a opção, ou use `py` em vez de `python` |
| `command not found: python` (macOS) | no macOS moderno só existe `python3`; o `python` sem sufixo foi removido em 2019 (era Python 2) | Use `python3`, ou crie um alias no `~/.zshrc` |
| `ERROR: Could not build wheels for scipy` | pip antigo tentando compilar do fonte; falta compilador/BLAS | `pip install --upgrade pip setuptools wheel` e tente de novo. Se persistir, é arquitetura sem wheel: instale via `conda`/`apt` |
| `ImportError: numpy.core.multiarray failed to import` | NumPy 1.x com pacote compilado contra NumPy 2.x (ou o inverso) | `pip install --force-reinstall numpy` e reinstale o pacote dependente. É o erro mais comum da transição NumPy 2 |
| `SSLError: [SSL: CERTIFICATE_VERIFY_FAILED]` | proxy corporativo com inspeção TLS | `export PIP_CERT=/caminho/ca-empresa.pem` (seção 7) |
| `PortAudioError: Error querying device -1` | falta a libportaudio, ou não há dispositivo de áudio (servidor, contêiner, WSL) | Instale `libportaudio2`; em servidor, simplesmente não use `sounddevice` |
| `UserWarning: Matplotlib is currently using agg, which is a non-GUI backend` | sem servidor gráfico (SSH, WSL sem WSLg, contêiner) | Salve em arquivo com `plt.savefig("f.png")` em vez de `plt.show()` |
| `RuntimeWarning: divide by zero encountered in log10` | `20*np.log10(0)` num espectro com bin exatamente nulo | Ponha um piso: `20*np.log10(np.maximum(np.abs(X), 1e-12))` |
| `error: Microsoft Visual C++ 14.0 or greater is required` (Windows) | pacote sem wheel tentando compilar | Instale o *Build Tools for Visual Studio*, ou (melhor) use WSL2 |

---

## Checklist de "ambiente pronto"

Rode tudo, de cima para baixo. Se todas as linhas responderem, siga para o
[`04-como-comecar.md`](04-como-comecar.md).

```bash
python3 --version                       # 3.10 ou superior
source ~/dsp/.venv/bin/activate         # sem erro
which python                            # caminho dentro do .venv
python -c "import numpy; print(numpy.__version__)"
python -c "import scipy; print(scipy.__version__)"
python -c "import matplotlib; print(matplotlib.__version__)"
python -c "from scipy import signal; print(signal.firwin(21, 0.2).sum())"   # 1.0
python -c "import numpy as np; print(np.argmax(np.abs(np.fft.rfft(np.sin(2*np.pi*50*np.arange(1000)/1000)))))"   # 50
python -c "import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt; plt.plot([1,2]); plt.savefig('/tmp/ok.png'); print('figura OK')"
```

---

## Autoteste

1. Por que `sudo pip install` é problema em Fedora/RHEL especificamente?
2. O que o PEP 668 faz e por que ele está certo?
3. Você editou o `~/.bashrc` e o comando continua não achado. O que fazer?
4. Qual é a diferença prática entre WSL2 e Python nativo no Windows para este curso?
5. Um colega recebeu `ImportError: numpy.core.multiarray failed to import`. Diagnóstico?
6. Como começar hoje sem instalar nada, e qual a limitação disso?
7. Cite três coisas específicas de DSP que precisam ser fixadas para o resultado
   ser reprodutível daqui a um ano.

---

## Fontes consultadas

- Python 3.14.7 — python.org, release de 05/08/2026 (consultado em 14/08/2026)
- NumPy 2.5.2 — numpy.org/news, 09/08/2026
- SciPy 1.18.0 — docs.scipy.org/doc/scipy/release/1.18.0-notes.html, 19/06/2026
  (requer Python 3.12–3.14 e NumPy ≥ 2.0)
- GNU Octave 11.3.0 — octave.org/news, 01/06/2026
- Audacity 3.7.8 — audacityteam.org, 29/06/2026
- GNU Radio 3.10.12 estável / 4.0-RC1 — gnuradio.org/news, 22/03/2026
- Preços de SDR — rtl-sdr.com (V4 descontinuado), consultado em 14/08/2026
- Comandos verificados na máquina de referência (Ubuntu 22.04.5) em 14/08/2026;
  os comandos de macOS e Windows seguem a documentação oficial de cada projeto
  e **não** foram executados nesta máquina.
