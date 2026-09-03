# 03 · Manual de instalação — passo a passo, por sistema operacional

`Nível: iniciante` · `Versões verificadas nos índices oficiais (PyPI e download.pytorch.org) em 11/08/2026`

> **Testado de verdade:** o caminho Linux + `venv` + PyTorch CPU deste manual foi executado
> em **11/08/2026** em Ubuntu (kernel 6.8), Python 3.10.12, resultando em
> `torch 2.13.0+cpu`, `transformers 5.15.0`, `datasets 5.0.1`, `scikit-learn 1.7.2`,
> com o teste de `fill-mask` do Passo 4 devolvendo a saída mostrada. Os caminhos de macOS,
> Windows e CUDA foram conferidos contra os índices e a documentação oficiais, não executados
> nesta máquina — estão marcados onde há risco.

---

## Leia isto antes de instalar qualquer coisa

**Você pode começar hoje sem instalar nada.** Pule para
[§ Alternativa sem instalar nada](#alternativa-sem-instalar-nada) — Google Colab te dá
Python, PyTorch, GPU e tudo o mais funcionando em 30 segundos, de graça, no navegador.
Instale na sua máquina depois, quando souber que vai continuar.

Isso não é preguiça: a instalação local de um ambiente de deep learning é o ponto onde mais
gente desiste, e o motivo quase sempre é conflito de versões de CUDA — um problema que não
tem nada a ver com BERT nem com o que você quer aprender.

**Este manual instala o conjunto inteiro**, não só o `transformers`:

| # | Componente | Para quê | Obrigatório? |
|---|---|---|---|
| 1 | **Python 3.12** | linguagem em que tudo roda | sim |
| 2 | **Ambiente virtual** (`venv` ou `uv`) | isolar as dependências deste projeto | sim (na prática) |
| 3 | **PyTorch 2.13** | motor numérico; único backend do `transformers` 5 | sim |
| 4 | **transformers 5.15** | os modelos BERT e a API | sim |
| 5 | **datasets, scikit-learn** | carregar dados e medir resultado | sim, para treinar |
| 6 | **accelerate** | treino em GPU/multi-GPU (usado pelo `Trainer`) | sim, para treinar |
| 7 | **huggingface_hub** (CLI `hf`) | baixar e publicar modelos, login | vem junto; login é opcional |
| 8 | **sentence-transformers** | embeddings e busca semântica | só para o arquivo `16` |
| 9 | **VS Code + extensões** | editor e notebooks | recomendado |
| 10 | **Git** | versionar, clonar | recomendado |
| 11 | **Docker** | reprodutibilidade e deploy | só para o arquivo `19` |
| 12 | **Conta Hugging Face** | modelos privados/gated, publicar | opcional |

**Versões de referência deste curso** (fixadas em 11/08/2026):

```
Python        3.12.13   (mínimo 3.10 · 3.9 é rejeitado pelo transformers 5)
PyTorch       2.13.0    (mínimo 2.4)
transformers  5.15.0    (mínimo 5.0 para a API deste curso; ver § v4 vs v5)
datasets      5.0.1
tokenizers    0.23.1
accelerate    1.14.0
scikit-learn  1.7+
sentence-transformers 5.7.0
```

> **Evite:** `transformers` 4.x se você for seguir os exemplos deste curso ao pé da letra —
> a API mudou em pontos que quebram silenciosamente (`tokenizer=` → `processing_class=`,
> `torch_dtype=` → `dtype=`, pipelines removidos). Veja [§ v4 vs v5](#o-que-mudou-do-transformers-4-para-o-5).
> **Evite também** Python 3.10 para projeto novo: chega ao fim de vida em **31/10/2026**.

---

## Alternativa sem instalar nada

### Opção A — Google Colab (recomendada para começar)

1. Acesse **https://colab.research.google.com** e entre com uma conta Google.
2. `Arquivo → Novo notebook`.
3. Para ter GPU: `Ambiente de execução → Alterar o tipo de ambiente de execução → T4 GPU`.
4. Na primeira célula, cole e execute (Shift+Enter):

```python
# Colab já vem com torch; garante um transformers recente
!pip install -q -U transformers datasets
import torch, transformers
print("torch:", torch.__version__, "| GPU:", torch.cuda.is_available())
print("transformers:", transformers.__version__)
```

```
# saída esperada (algo como):
# torch: 2.13.0+cu130 | GPU: True
# transformers: 5.15.0
```

Se `GPU: False`, você esqueceu o passo 3.

**Limites do plano gratuito (agosto de 2026):** sessão cai após ~90 min de inatividade ou
~12 h de uso contínuo; a cota de GPU é diária e não publicada, e some se você usar muito.
Nada é salvo ao fechar — monte o Google Drive (`from google.colab import drive;
drive.mount('/content/drive')`) ou baixe os arquivos antes de sair.

### Opção B — Kaggle Notebooks

**https://www.kaggle.com/code** → `New Notebook` → painel direito → `Accelerator: GPU T4 x2`.
Exige verificar telefone. Cota bem mais generosa que a do Colab: cerca de 30 h de GPU por
semana, com o relógio visível na interface — o que evita a surpresa de ser cortado no meio.

### Opção C — Hugging Face Spaces

Para *demonstrar* um modelo (não para treinar). CPU grátis; GPU a partir de US$ 0,40/h.
Ver [80-custos-e-licencas.md](80-custos-e-licencas.md).

### Opção D — Docker, sem sujar sua máquina

Se você já tem Docker (veja o curso [`../docker/`](../docker/00-MAPA.md)):

```bash
# Ambiente CPU descartável com Python 3.12, entra num shell dentro do container
docker run --rm -it -v "$PWD:/work" -w /work python:3.12-slim bash
```

Dentro do container:

```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install transformers datasets scikit-learn
```

Para GPU NVIDIA, use a imagem oficial do PyTorch e o NVIDIA Container Toolkit:

```bash
docker run --rm -it --gpus all -v "$PWD:/work" -w /work pytorch/pytorch:2.13.0-cuda13.0-cudnn9-runtime bash
```

> Confira a tag exata em https://hub.docker.com/r/pytorch/pytorch/tags antes de rodar —
> as tags mudam a cada release e uma tag inexistente falha com `manifest unknown`.

---

# Instalação local

A partir daqui, o caminho longo. Faça **na ordem**.

---

## Passo 1 · Python

### 1.1 · Linux — Debian / Ubuntu

O Python do sistema serve para começar, mas o do sistema é *do sistema*: em Ubuntu 24.04 ele
é 3.12; em 22.04 é 3.10 (que morre em outubro de 2026). Verifique:

```bash
python3 --version
```

```
# esperado: Python 3.12.x (ou superior)
# se aparecer 3.10 ou 3.11, funciona, mas prefira instalar 3.12 — instruções abaixo
```

Instale o essencial (o `venv` **não** vem junto no Debian/Ubuntu, e essa é a pegadinha nº 1):

```bash
sudo apt update && sudo apt install -y python3 python3-pip python3-venv git curl
```

Para ter o 3.12 em uma distro que não o traz, o caminho oficial é o PPA deadsnakes:

```bash
sudo add-apt-repository -y ppa:deadsnakes/ppa && sudo apt update
sudo apt install -y python3.12 python3.12-venv
```

```bash
python3.12 --version
# esperado: Python 3.12.13
```

### 1.2 · Linux — Fedora / RHEL / Rocky

```bash
sudo dnf install -y python3.12 python3-pip git
```

```bash
python3.12 --version
# esperado: Python 3.12.x
```

No RHEL 9 e derivados, `python3.12` vem dos repositórios AppStream. Se não achar o pacote,
habilite: `sudo dnf module enable python312` (ou use `uv`, no passo 1.5, que ignora tudo isso).

### 1.3 · macOS

O Python que vem com o macOS é velho e é usado pelo sistema — **não mexa nele, não instale
pacotes nele**. Use Homebrew.

```bash
# instala o Homebrew, se ainda não tiver
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Ao final, o instalador imprime duas linhas mandando você rodar comandos de `shellenv`.
**Rode-as** — é isso que coloca o `brew` no PATH. Em Apple Silicon (M1/M2/M3/M4) o Homebrew
mora em `/opt/homebrew`; em Intel, em `/usr/local`. Confirme:

```bash
brew --version
# esperado: Homebrew 4.x.x
```

```bash
brew install python@3.12 git
```

```bash
python3.12 --version
# esperado: Python 3.12.x
```

### 1.4 · Windows

**Recomendação: use WSL2, não o Windows nativo.** Motivos concretos, não ideológicos:

- praticamente todo tutorial, script e Dockerfile do campo assume Linux;
- compilação de dependências nativas (`tokenizers`, `sentencepiece`, `flash-attn`) falha muito
  mais no Windows;
- ferramentas de treino distribuído e várias otimizações simplesmente não existem no Windows;
- a GPU NVIDIA **funciona dentro do WSL2** desde 2021 com o driver do Windows — você não perde
  a placa de vídeo.

Use Windows nativo apenas se: política da empresa proibir WSL, ou se você só vai fazer
inferência simples em CPU.

#### Caminho recomendado — WSL2

No PowerShell **como administrador**:

```powershell
wsl --install -d Ubuntu-24.04
```

Reinicie o computador, abra "Ubuntu" no menu Iniciar, crie usuário e senha, e a partir daí
**siga a seção 1.1 (Debian/Ubuntu)**. De dentro do WSL, seus arquivos do Windows estão em
`/mnt/c/...` — mas trabalhe dentro de `~` (o disco do Linux), porque `/mnt/c` é de 5 a 20 vezes
mais lento para operações com muitos arquivos pequenos, e datasets são exatamente isso.

```bash
# dentro do WSL, confirme a GPU (se você tiver uma NVIDIA)
nvidia-smi
# esperado: tabela com o nome da GPU e a versão do driver
```

Se `nvidia-smi` não existir no WSL, atualize o **driver da NVIDIA no Windows** (não instale
driver NVIDIA dentro do WSL — isso quebra a integração).

#### Caminho nativo (sem WSL)

```powershell
winget install -e --id Python.Python.3.12
winget install -e --id Git.Git
```

Feche e reabra o PowerShell (senão o PATH não pegou — ver [§ PATH](#path-e-variáveis-de-ambiente)).

```powershell
py -3.12 --version
# esperado: Python 3.12.x
```

No Windows nativo, use `py -3.12` em vez de `python` para não pegar o alias da Microsoft Store,
que abre a loja em vez de rodar Python.

### 1.5 · Alternativa moderna e multiplataforma: `uv`

`uv` é um gerenciador de pacotes e de versões de Python escrito em Rust, e é **muito** mais
rápido que `pip` (10–100× em instalações grandes; a diferença é sentida com PyTorch). Ele também
instala o próprio Python, o que resolve todas as seções acima de uma vez.

**Minha recomendação para projeto novo em 2026:** use `uv`. Mantive o `pip` como caminho
principal neste manual porque é o que 90% dos tutoriais assumem e você precisa saber ler.

```bash
# Linux e macOS
curl -LsSf https://astral.sh/uv/install.sh | sh
```

```powershell
# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

```bash
uv --version
# esperado: uv 0.9.x (ou superior)
```

Projeto inteiro com `uv`, do zero:

```bash
uv init meu-bert && cd meu-bert
uv python install 3.12          # baixa o próprio Python 3.12, sem tocar no do sistema
uv add torch transformers datasets scikit-learn accelerate
uv run python -c "import transformers; print(transformers.__version__)"
```

Isso cria `pyproject.toml` + `uv.lock` (reprodutibilidade real, ver
[§ Reprodutibilidade](#reprodutibilidade)) e dispensa ativar ambiente virtual à mão.

---

## Passo 2 · Ambiente virtual

**Nunca instale essas bibliotecas no Python do sistema.** Não é frescura — é a diferença
entre "quebrei meu projeto" e "quebrei meu sistema operacional". No Ubuntu e no Fedora,
ferramentas do próprio SO são escritas em Python; sobrescrever um pacote que elas usam
pode inutilizar o gerenciador de pacotes. Por isso as distros modernas passaram a **recusar**
`pip install` global com o erro `externally-managed-environment` (PEP 668).

```bash
# na pasta do seu projeto
cd ~/projetos/bert-curso        # crie a pasta antes: mkdir -p ~/projetos/bert-curso
python3.12 -m venv .venv
```

Ativar — **o comando muda por sistema e por shell**:

```bash
source .venv/bin/activate            # Linux, macOS, WSL (bash/zsh)
```

```powershell
.venv\Scripts\Activate.ps1           # Windows PowerShell
```

```cmd
.venv\Scripts\activate.bat           REM Windows CMD
```

Verificação — o prompt ganha o prefixo `(.venv)` e:

```bash
python -c "import sys; print(sys.prefix)"
# esperado: um caminho terminando em /.venv
```

Se o caminho **não** terminar em `.venv`, o ambiente não está ativo e tudo que você instalar
vai para o lugar errado.

> **Windows PowerShell:** se der `execução de scripts foi desabilitada neste sistema`, rode
> uma vez `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` e confirme com `S`.

Deixe o `pip` atualizado dentro do ambiente:

```bash
python -m pip install --upgrade pip
```

---

## Passo 3 · PyTorch

**Este é o passo que dá errado.** Leia antes de colar.

PyTorch tem builds diferentes conforme o acelerador. Instalar o errado é a causa nº 1 de
"instalei tudo e a GPU não aparece" e de downloads de 3 GB desnecessários.

### 3.1 · Descubra qual build você precisa

```bash
nvidia-smi
```

- **Tabela com a GPU e uma versão de CUDA no canto superior direito** → você tem NVIDIA.
  Anote a "CUDA Version" exibida — ela é a **máxima suportada pelo driver**, não a instalada.
- **`command not found` / erro** → sem GPU NVIDIA utilizável. Use o build de CPU
  (ou ROCm, se for AMD no Linux; ou MPS, se for Mac com Apple Silicon).

### 3.2 · Comandos por caso

**CPU (qualquer SO — Windows, Linux, macOS Intel):**

```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

Baixa ~200 MB em vez de ~3 GB. Use isto se você não tem GPU — evita puxar o CUDA inteiro à toa.

**macOS Apple Silicon (M1/M2/M3/M4):**

```bash
pip install torch
```

O wheel padrão do macOS já inclui o backend **MPS** (a GPU integrada da Apple). Não existe
CUDA em Mac; qualquer tutorial que mande instalar CUDA no Mac está errado.

**NVIDIA — CUDA 13.0 (padrão recomendado em ago/2026, driver ≥ 580):**

```bash
pip install torch --index-url https://download.pytorch.org/whl/cu130
```

**NVIDIA — driver mais antigo:** use um canal compatível, por exemplo
`https://download.pytorch.org/whl/cu128` (traz PyTorch 2.11, não 2.13 — o `transformers` 5
aceita, pois exige ≥ 2.4). Se a "CUDA Version" do `nvidia-smi` for menor que a do canal, o
`torch.cuda.is_available()` volta `False`. A regra é: **canal ≤ CUDA do driver**.

**AMD ROCm (só Linux):**

```bash
pip install torch --index-url https://download.pytorch.org/whl/rocm7.2
```

**Verificação (faça sempre, em qualquer caso):**

```bash
python -c "import torch; print(torch.__version__); print('CUDA:', torch.cuda.is_available()); print('MPS:', torch.backends.mps.is_available())"
```

```
# esperado num PC com NVIDIA:
# 2.13.0+cu130
# CUDA: True
# MPS: False

# esperado num Mac M-series:
# 2.13.0
# CUDA: False
# MPS: True

# esperado em CPU pura:
# 2.13.0+cpu
# CUDA: False
# MPS: False
```

**Se `CUDA: False` mas você tem GPU NVIDIA:**

1. Você instalou o build de CPU. Confirme: se `torch.__version__` termina em `+cpu`, é isso.
   Corrija com `pip uninstall -y torch` e reinstale pelo canal `cu130`.
2. Driver antigo demais para o canal escolhido → baixe um canal menor, ou atualize o driver.
3. No WSL: driver NVIDIA instalado *dentro* do Linux (errado) em vez de no Windows.
4. Placa muito antiga (Kepler/Maxwell, anteriores a ~2016) — sem suporte nos builds atuais.

---

## Passo 4 · transformers e o resto do conjunto

```bash
pip install transformers datasets scikit-learn accelerate
```

O que cada um faz, em uma linha:

- `transformers` — os modelos, tokenizadores e o `Trainer`. Puxa `tokenizers` (Rust) e
  `huggingface_hub` junto.
- `datasets` — carrega e transforma conjuntos de dados (CSV, JSON, Parquet, Hub) sem estourar RAM.
- `scikit-learn` — métricas (F1, matriz de confusão) e divisão treino/teste.
- `accelerate` — infraestrutura de treino (GPU, multi-GPU, precisão mista) usada pelo `Trainer`.

Opcionais, conforme o arquivo do curso que você for seguir:

```bash
pip install sentence-transformers          # arquivo 16 — embeddings e busca semântica
pip install "optimum[onnxruntime]"         # arquivo 19 — exportar para ONNX, acelerar em CPU
pip install evaluate seqeval               # arquivo 18 — métricas de NER
pip install jupyterlab ipywidgets          # notebooks locais
pip install fastapi "uvicorn[standard]"    # projeto-modelo — servir por HTTP
```

**Verificação:**

```bash
python -c "import transformers, datasets, sklearn; print(transformers.__version__, datasets.__version__, sklearn.__version__)"
```

```
# esperado: 5.15.0 5.0.1 1.7.x  (ou superiores)
```

**Teste de fogo — baixa um modelo real e usa:**

```bash
python -c "
from transformers import pipeline
p = pipeline('fill-mask', model='neuralmind/bert-base-portuguese-cased')
for r in p('O Brasil é o maior país da América do [MASK].')[:3]:
    print(round(r['score'], 3), r['token_str'])
"
```

```
# saída real, obtida em 11/08/2026 (transformers 5.15.0, torch 2.13.0+cpu):
# 0.955 Sul
# 0.042 Norte
# 0.002 sul
#
# Antes disso, o transformers imprime um "LOAD REPORT" listando
# bert.pooler.* e cls.seq_relationship.* como UNEXPECTED. Isso é NORMAL:
# são os pesos da tarefa NSP, que a cabeça de fill-mask não usa. Não é erro.
```

Se isso funcionou, **seu ambiente está pronto**. O primeiro uso baixa ~440 MB para o cache
(`~/.cache/huggingface`) e demora; as próximas vezes são instantâneas.

---

## Passo 5 · huggingface_hub e login (opcional)

Já foi instalado junto com o `transformers`. O CLI se chama `hf` (o antigo
`huggingface-cli` foi descontinuado na versão 1.0 do `huggingface_hub`).

```bash
hf --version
# esperado: hf, version 1.x.x
```

Você **não precisa** de login para baixar modelos públicos. Precisa para:
publicar modelos, acessar modelos *gated* (que exigem aceitar uma licença) e evitar o limite
de requisições anônimas.

1. Crie a conta em https://huggingface.co/join
2. Gere um token em https://huggingface.co/settings/tokens — escolha o tipo **Fine-grained**
   e marque só `Read` para uso normal. Token com escrita, só quando for publicar.
3. Faça login:

```bash
hf auth login
# cole o token quando pedir; ele fica em ~/.cache/huggingface/token
```

```bash
hf auth whoami
# esperado: seu nome de usuário
```

> **Segurança:** o token é uma senha. Nunca cole em notebook que você vá compartilhar, nem
> comite em repositório. Se vazar, revogue na mesma página em que foi criado. Em ambientes
> automatizados, use a variável `HF_TOKEN` em vez do arquivo.

---

## Passo 6 · Editor — VS Code

```bash
# Linux Debian/Ubuntu (snap)
sudo snap install --classic code
```

```bash
# macOS
brew install --cask visual-studio-code
```

```powershell
# Windows
winget install -e --id Microsoft.VisualStudioCode
```

Extensões (instale por dentro do VS Code, `Ctrl+Shift+X`):

| Extensão | ID | Para quê |
|---|---|---|
| Python | `ms-python.python` | interpretação, depuração, seleção de ambiente |
| Jupyter | `ms-toolsai.jupyter` | rodar notebooks `.ipynb` dentro do VS Code |
| Ruff | `charliermarsh.ruff` | lint e formatação rápidos |
| WSL | `ms-vscode-remote.remote-wsl` | **essencial** se você usa Windows + WSL2 |

Depois de abrir a pasta do projeto: `Ctrl+Shift+P` → `Python: Select Interpreter` → escolha o
que está dentro de `.venv`. Se você pular isso, o VS Code roda com o Python errado e você vai
ver `ModuleNotFoundError` para pacotes que você acabou de instalar — reclamação clássica.

---

## PATH e variáveis de ambiente

### Por que "não pegou" antes de reabrir o terminal

O PATH é lido **quando o shell inicia**. Um instalador que edita `.bashrc`/`.zshrc`/`Perfil`
não afeta janelas já abertas. Feche e reabra o terminal, ou recarregue:

```bash
source ~/.bashrc      # bash
source ~/.zshrc       # zsh (padrão do macOS desde o Catalina)
```

```powershell
. $PROFILE            # PowerShell
```

### Conferir o PATH

```bash
echo $PATH | tr ':' '\n'      # Linux/macOS — uma entrada por linha
```

```powershell
$env:PATH -split ';'          # Windows
```

```bash
which python pip              # Linux/macOS — mostra qual binário será usado
```

```powershell
where.exe python              # Windows
```

Com o ambiente virtual ativo, `which python` **tem** que apontar para dentro de `.venv`.
Se apontar para `/usr/bin/python`, o ambiente não está ativo.

### Variáveis que valem conhecer

| Variável | O que faz | Quando mexer |
|---|---|---|
| `HF_HOME` | onde ficam cache de modelos e token (padrão: `~/.cache/huggingface`) | disco cheio, ou disco de rede — aponte para um SSD com espaço |
| `HF_TOKEN` | token de autenticação | CI/CD, containers |
| `HF_HUB_OFFLINE=1` | proíbe qualquer acesso à rede; usa só o cache | produção, ar-gapped, evitar surpresa de download |
| `TRANSFORMERS_VERBOSITY=error` | reduz o barulho nos logs | scripts em produção |
| `TOKENIZERS_PARALLELISM=false` | silencia o aviso de fork do tokenizador | quando usa `DataLoader` com múltiplos *workers* |
| `CUDA_VISIBLE_DEVICES=0` | restringe quais GPUs o processo enxerga | máquina com várias GPUs compartilhadas |

> **Obsoleto:** `TRANSFORMERS_CACHE`, `PYTORCH_TRANSFORMERS_CACHE` e
> `PYTORCH_PRETRAINED_BERT_CACHE` foram **removidos** no `transformers` 5. Se seu script antigo
> usa isso, o cache vai para outro lugar sem avisar e você vai rebaixar tudo. Use `HF_HOME`.

Fixando permanentemente (exemplo em Linux/macOS):

```bash
echo 'export HF_HOME="$HOME/.cache/huggingface"' >> ~/.bashrc && source ~/.bashrc
```

```powershell
# Windows, permanente para o usuário
[Environment]::SetEnvironmentVariable("HF_HOME", "$HOME\.cache\huggingface", "User")
```

---

## Permissões — por que `sudo pip` é um erro

Três problemas concretos, em ordem de gravidade:

1. **Você pode quebrar o sistema.** `sudo pip install` grava em `/usr/lib/python3/dist-packages`,
   território do `apt`/`dnf`. Sobrescrever ali uma versão de que uma ferramenta do SO depende
   deixa o sistema em estado inconsistente — no Ubuntu, já quebrou `apt` de muita gente.
2. **Você executa código de terceiros como root.** `pip` roda scripts de build do pacote.
   Com `sudo`, esse código tem poder total sobre a máquina.
3. **Arquivos ficam com dono errado.** Metade do cache vira do root, e depois o `pip` normal
   falha com `Permission denied` em lugares aleatórios.

O certo é o ambiente virtual (Passo 2). Se precisar mesmo instalar fora dele, use
`pip install --user pacote`, que grava em `~/.local/`.

Distros modernas te protegem com este erro:

```
error: externally-managed-environment
× This environment is externally managed
```

Isso é o sistema fazendo a coisa certa. **Não** desative com `--break-system-packages`
(o nome do flag é literalmente o aviso). Crie um venv.

---

## Rede corporativa: proxy, certificado e registry espelhado

Se você está atrás do firewall de uma empresa e vê `SSLError`, `CERTIFICATE_VERIFY_FAILED`
ou downloads que travam em 0%:

```bash
# proxy
export HTTP_PROXY="http://usuario:senha@proxy.empresa.com:8080"
export HTTPS_PROXY="$HTTP_PROXY"
export NO_PROXY="localhost,127.0.0.1,.empresa.com"
```

```bash
# certificado interno (inspeção de TLS) — aponte para o bundle da empresa
export REQUESTS_CA_BUNDLE=/caminho/para/ca-empresa.pem
export SSL_CERT_FILE=/caminho/para/ca-empresa.pem
export CURL_CA_BUNDLE=/caminho/para/ca-empresa.pem
```

```ini
# índice PyPI espelhado — ~/.pip/pip.conf (Linux/macOS)
# ou %APPDATA%\pip\pip.ini (Windows)
[global]
index-url = https://nexus.empresa.com/repository/pypi/simple
trusted-host = nexus.empresa.com
```

Espelho do Hugging Face (existem espelhos regionais e internos):

```bash
export HF_ENDPOINT=https://hf-mirror.com
```

**Nunca** resolva com `pip install --trusted-host ... ` para tudo, nem desabilite verificação
de TLS globalmente: isso te expõe a *man-in-the-middle* real, o que é ironia amarga num
ambiente que instalou inspeção de TLS justamente para evitar isso.

**Ambiente sem internet:** baixe o modelo em uma máquina com acesso e leve a pasta:

```bash
hf download neuralmind/bert-base-portuguese-cased --local-dir ./bertimbau
# depois, na máquina isolada:
# AutoModel.from_pretrained("./bertimbau")
```

---

## Convivência de versões

Ter dois projetos com versões diferentes na mesma máquina, sem conflito:

| Ferramenta | O que isola | Comando essencial | Recomendação |
|---|---|---|---|
| `venv` | pacotes | `python3.12 -m venv .venv` | padrão, sempre |
| `uv` | pacotes **e** o próprio Python | `uv python install 3.12` | **melhor opção em 2026** |
| `pyenv` | versões de Python | `pyenv install 3.12.13` | clássico, ainda ótimo; não existe no Windows nativo |
| `conda`/`mamba` | Python, pacotes e libs C | `conda create -n bert python=3.12` | útil em HPC e quando há dependências C pesadas; pesado e lento |
| Docker | o SO inteiro | `docker run ... python:3.12-slim` | quando precisa ser idêntico em qualquer máquina |

**Não misture `conda` e `pip` no mesmo ambiente sem cuidado** — é a receita clássica para
dependências inconsistentes que só aparecem semanas depois, porque o `conda` não enxerga o
que o `pip` instalou.

Fixar a versão do Python por pasta:

```bash
pyenv local 3.12.13        # cria .python-version
```

```bash
uv python pin 3.12         # cria .python-version, respeitado pelo uv
```

---

## Reprodutibilidade

Sem isto, seu projeto funciona hoje e quebra em três meses — em geral, no dia da entrega.

```bash
# congela o que está instalado agora
pip freeze > requirements.txt
```

```bash
# reconstrói exatamente o mesmo ambiente em outra máquina
pip install -r requirements.txt
```

`pip freeze` tem um limite: ele grava versões, mas não *hashes*, e não distingue o que você
pediu do que veio por dependência. Alternativas melhores, em ordem de robustez:

```bash
uv lock                    # gera uv.lock com hashes e resolução determinística
uv sync                    # reconstrói exatamente
```

Arquivos que devem estar no Git:

```
pyproject.toml        # o que você pediu
uv.lock               # ou requirements.txt — o que foi resolvido
.python-version       # qual Python
Dockerfile            # se for para produção
```

Arquivos que **não** devem (adicione ao `.gitignore`):

```
.venv/
__pycache__/
*.pt
modelo-final/         # pesos: use o Hub ou um bucket, não o Git
data/                 # dados: idem
```

**Reprodutibilidade do resultado, não só do ambiente:** fixe também a semente aleatória, ou
dois treinos com o mesmo código dão números diferentes:

```python
from transformers import set_seed
set_seed(42)   # fixa random, numpy e torch de uma vez
```

Mesmo assim, **GPU não é 100% determinística por padrão** (a ordem de redução em ponto
flutuante varia). Para determinismo total, ao custo de velocidade:
`torch.use_deterministic_algorithms(True)` + `CUBLAS_WORKSPACE_CONFIG=:4096:8`.

---

## Atualizar com segurança e voltar atrás

```bash
# ver o que está instalado e o que está desatualizado
pip list --outdated
```

```bash
# atualizar um pacote específico (nunca "atualize tudo" num projeto que funciona)
pip install -U transformers
```

```bash
# voltar para uma versão específica
pip install "transformers==5.14.0"
```

Regra que evita muita dor: **antes de atualizar, congele**
(`pip freeze > requirements.backup.txt`). Se o novo ambiente quebrar,
`pip install -r requirements.backup.txt` te devolve o estado anterior.

Cuidado especial com o par `torch` × `transformers`: atualizar o `torch` sozinho, num
ambiente com CUDA, pode trocar o build para um canal incompatível com o driver e você perde
a GPU sem entender por quê. Ao atualizar o `torch`, use sempre o `--index-url` do canal certo.

---

## Desinstalar por completo

Desinstalar os pacotes é a parte fácil; o que fica para trás é o cache de modelos, que
tranquilamente passa de 20 GB depois de alguns meses de estudo.

```bash
# 1. pacotes: basta apagar o ambiente virtual
rm -rf .venv                      # Linux/macOS
```

```powershell
Remove-Item -Recurse -Force .venv  # Windows
```

```bash
# 2. cache de modelos e datasets do Hugging Face — o grande vilão de disco
hf cache scan                     # mostra o tamanho e o que está lá
hf cache delete                   # apaga interativamente, revisão por revisão
rm -rf ~/.cache/huggingface       # ou remova tudo de uma vez
```

```bash
# 3. cache do pip
pip cache purge
rm -rf ~/.cache/pip
```

```bash
# 4. cache do torch (modelos baixados por torch.hub, kernels compilados)
rm -rf ~/.cache/torch
```

Caminhos no Windows: `%USERPROFILE%\.cache\huggingface` e `%LOCALAPPDATA%\pip\Cache`.

Para remover o Python inteiro: `sudo apt remove python3.12` (Debian/Ubuntu),
`brew uninstall python@3.12` (macOS), `winget uninstall Python.Python.3.12` (Windows).
No Linux, **não remova** o `python3` do sistema — você quebra o SO.

---

## Requisitos reais de recurso

| Recurso | Mínimo | Confortável | Observação |
|---|---|---|---|
| Disco (ambiente) | 3 GB (CPU) | 10 GB (CUDA) | o build CUDA do PyTorch sozinho passa de 3 GB |
| Disco (cache de modelos) | 2 GB | 20 GB+ | BERT-base ≈ 440 MB, BERT-large ≈ 1,3 GB, cada variante baixada some do disco |
| RAM (inferência) | 4 GB | 8 GB | BERT-base em `float32` ocupa ~440 MB de RAM + ativações |
| RAM (treino, CPU) | 8 GB | 16 GB | treino guarda gradientes e estados do otimizador: ~4× o tamanho do modelo |
| VRAM (treino, GPU) | 6 GB | 12 GB+ | BERT-base, `batch=16`, `seq=128` cabe em ~6 GB; `seq=512` quadruplica |
| Arquitetura | x86-64 ou ARM64 | — | há wheels para ambos; ARM32 e 32 bits estão fora |
| Conta obrigatória | nenhuma | — | modelos públicos baixam sem login |
| Cartão de crédito | nunca | — | nada neste curso exige pagamento |

---

## Solução de problemas

Erros literais, causa e correção. Estes cobrem a esmagadora maioria dos travamentos reais.

| Mensagem | Causa provável | Correção |
|---|---|---|
| `command not found: python` (ou `pip`) | não instalado, ou fora do PATH | Linux: `sudo apt install python3`. Windows: use `py -3.12`. Sempre: **reabra o terminal** após instalar |
| `error: externally-managed-environment` | `pip` global numa distro protegida por PEP 668 | crie um venv (Passo 2). Não use `--break-system-packages` |
| `EACCES: permission denied` / `Permission denied: '/usr/lib/python3...'` | instalação global sem permissão | use venv, ou `pip install --user`. Nunca `sudo pip` |
| `ModuleNotFoundError: No module named 'transformers'` | ambiente virtual não ativado, ou VS Code apontando para outro interpretador | `source .venv/bin/activate`; no VS Code, `Python: Select Interpreter` |
| `ModuleNotFoundError: No module named 'torch'` ao importar `transformers` | `transformers` 5 exige PyTorch; não há mais fallback de TensorFlow | instale o `torch` (Passo 3) |
| `RuntimeError: Failed to import transformers.trainer because of the following error: ... torch` | versão de `torch` abaixo de 2.4 | `pip install -U torch --index-url <canal correto>` |
| `torch.cuda.is_available() == False` com GPU NVIDIA presente | build de CPU instalado, ou driver mais antigo que o canal CUDA | veja `torch.__version__`; se terminar em `+cpu`, reinstale pelo canal `cu130` |
| `CUDA error: no kernel image is available for execution on the device` | GPU antiga demais para o build | use um canal CUDA mais antigo, ou CPU |
| `torch.OutOfMemoryError: CUDA out of memory` | *batch* ou sequência grandes demais | reduza `per_device_train_batch_size`, use `max_length=128`, ligue `bf16=True` e `gradient_accumulation_steps` |
| `OSError: We couldn't connect to 'https://huggingface.co'` | sem rede, proxy, ou firewall | configure `HTTPS_PROXY`; ou baixe o modelo antes e use caminho local; ou `HF_HUB_OFFLINE=1` com o cache pronto |
| `OSError: ... is not a local folder and is not a valid model identifier` | nome do modelo digitado errado, ou modelo *gated* sem login | confira o nome exato na página do modelo; `hf auth login` se for gated |
| `SSLError: CERTIFICATE_VERIFY_FAILED` | certificado corporativo interceptando TLS | `export REQUESTS_CA_BUNDLE=/caminho/ca-empresa.pem` |
| `ValueError: Unrecognized configuration class ... for AutoModelForSequenceClassification` | `transformers` velho demais para o modelo (ex.: ModernBERT precisa ≥ 4.48) | `pip install -U transformers` |
| `TypeError: Trainer.__init__() got an unexpected keyword argument 'tokenizer'` | código escrito para `transformers` 4.x rodando no 5.x | troque `tokenizer=` por `processing_class=` |
| `TypeError: __init__() got an unexpected keyword argument 'evaluation_strategy'` | idem, nome antigo | use `eval_strategy=` |
| `No space left on device` durante download | cache de modelos encheu o disco | `hf cache scan` e `hf cache delete`; ou mova com `HF_HOME` |
| `huggingface_hub.errors.HfHubHTTPError: 429` | limite de requisições anônimas | `hf auth login` |
| `The current process just got forked... TOKENIZERS_PARALLELISM` (aviso) | tokenizador Rust + `DataLoader` com workers | inofensivo; silencie com `export TOKENIZERS_PARALLELISM=false` |
| `.venv\Scripts\Activate.ps1 ... execução de scripts foi desabilitada` | política do PowerShell | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |
| Treino em Mac muito lento | rodando em CPU, não em MPS | `model.to("mps")`, ou passe `use_mps_device` via `TrainingArguments`; confira `torch.backends.mps.is_available()` |

---

## O que mudou do transformers 4 para o 5

Você vai encontrar milhares de tutoriais escritos para a v4, e eles quebram. Tabela de
tradução dos pontos que mais aparecem (a lista oficial completa está no
[MIGRATION_GUIDE_V5.md](https://github.com/huggingface/transformers/blob/main/MIGRATION_GUIDE_V5.md)):

| v4 (tutoriais antigos) | v5 (correto hoje) |
|---|---|
| `Trainer(..., tokenizer=tok)` | `Trainer(..., processing_class=tok)` |
| `TrainingArguments(evaluation_strategy="epoch")` | `eval_strategy="epoch"` |
| `TrainingArguments(warmup_ratio=0.1)` | **removido** → `warmup_steps=0.1` (float < 1 = proporção) |
| `TrainingArguments(overwrite_output_dir=..., logging_dir=...)` | **removidos** |
| `from_pretrained(torch_dtype=torch.float16)` | `from_pretrained(dtype=torch.float16)` |
| `from_pretrained(use_auth_token=...)` | `from_pretrained(token=...)` |
| `from_pretrained(load_in_8bit=True)` | `quantization_config=BitsAndBytesConfig(load_in_8bit=True)` |
| `tokenizer.encode_plus(...)` | `tokenizer(...)` |
| `tokenizer.batch_decode(ids)` | `tokenizer.decode(ids)` (unificado) |
| `pipeline("question-answering")` | **removido** — faça manualmente ([06-exemplos.md](06-exemplos.md)) |
| `pipeline("summarization" / "translation")` | **removidos** — use modelo generativo |
| `TFBertModel`, `FlaxBertModel` | **removidos** — TensorFlow e JAX saíram da biblioteca |
| `AutoModelWithLMHead` | `AutoModelForMaskedLM` (para BERT) |
| `huggingface-cli` | `hf` |
| `TRANSFORMERS_CACHE=...` | `HF_HOME=...` |

Também mudou um padrão silencioso e perigoso: `from_pretrained` agora usa `dtype="auto"`,
carregando o modelo na precisão em que foi salvo. Antes era sempre `float32`. Se um cálculo
seu passou a divergir depois de atualizar, é provavelmente isto — force com
`dtype=torch.float32` se precisar do comportamento antigo.

---

## Checklist "ambiente pronto"

Rode um por linha. Todos precisam passar antes de você seguir para
[04-como-comecar.md](04-como-comecar.md).

```bash
python --version
```
```bash
python -c "import sys; print(sys.prefix)"          # tem que terminar em .venv
```
```bash
python -c "import torch; print(torch.__version__, torch.cuda.is_available())"
```
```bash
python -c "import transformers; print(transformers.__version__)"
```
```bash
python -c "import datasets, sklearn, accelerate; print('ok')"
```
```bash
python -c "from transformers import AutoTokenizer; t=AutoTokenizer.from_pretrained('neuralmind/bert-base-portuguese-cased'); print(t.tokenize('instalação concluída'))"
```
```bash
python -c "from transformers import pipeline; print(pipeline('fill-mask', model='neuralmind/bert-base-portuguese-cased')('A capital da França é [MASK].')[0]['token_str'])"
```
```bash
hf --version
```
```bash
git --version
```

Saída esperada do penúltimo comando: `Paris`.
Se todos passaram, o ambiente está pronto.

---

## Autoteste

1. Por que o Colab é recomendado *antes* da instalação local?
2. O que acontece se você rodar `sudo pip install torch` no Ubuntu, e por que isso é grave?
3. Você tem uma RTX 3060 e `torch.cuda.is_available()` devolve `False`. Cite três causas possíveis e como distinguir a primeira.
4. Qual variável de ambiente controla onde os modelos ficam em cache — e qual era o nome antigo, hoje removido?
5. Por que instalar `torch` pelo canal `cpu` quando você não tem GPU, em vez do `pip install torch` normal?
6. Um tutorial de 2023 usa `Trainer(tokenizer=tok)` e falha. O que trocar?
7. Como descobrir quanto espaço o cache do Hugging Face está ocupando, e como limpá-lo?
8. Você está numa rede com inspeção de TLS e recebe `CERTIFICATE_VERIFY_FAILED`. Qual é a correção certa, e qual é a errada (mas tentadora)?
9. Por que trabalhar em `/mnt/c/...` dentro do WSL2 é má ideia?

---

## Fontes consultadas

Consulta feita em **11/08/2026**:

- [PyPI — transformers](https://pypi.org/project/transformers/) — versão 5.15.0, Python ≥ 3.10, Apache-2.0
- [PyPI — torch](https://pypi.org/project/torch/) — versão 2.13.0
- [Índice de wheels do PyTorch](https://download.pytorch.org/whl/) — canais `cpu`, `cu130`, `cu132`, `rocm7.2` confirmados com `torch` 2.13.0 para CPython 3.10–3.15
- [PyPI — datasets 5.0.1, accelerate 1.14.0, tokenizers 0.23.1, sentence-transformers 5.7.0](https://pypi.org/)
- [MIGRATION_GUIDE_V5.md — huggingface/transformers](https://github.com/huggingface/transformers/blob/main/MIGRATION_GUIDE_V5.md)
- [Hugging Face — Installation](https://huggingface.co/docs/transformers/en/installation)
- [endoflife.date — Python](https://endoflife.date/python) — 3.10 EOL em 31/10/2026; 3.12.13 é o patch atual
- [neuralmind/bert-base-portuguese-cased](https://huggingface.co/neuralmind/bert-base-portuguese-cased)

---

*Anterior: [02-pre-requisitos.md](02-pre-requisitos.md) · Próximo: [04-como-comecar.md](04-como-comecar.md)*
