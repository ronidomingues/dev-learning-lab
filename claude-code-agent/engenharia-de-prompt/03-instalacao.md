# 3 · Manual de instalação — o ambiente completo, passo a passo

**Nível:** iniciante · **Escrito em:** 19/08/2026
**Versões conferidas na web em 19/08/2026** (fontes no rodapé).

> **Leia primeiro:** você **não precisa instalar nada** para começar hoje.
> Pule para a [§0](#0--comece-hoje-sem-instalar-nada) e volte aqui quando quiser
> automatizar. Este manual instala o ambiente **profissional** — o que você
> precisa para medir, versionar e integrar.

| Ferramenta | Versão testada | Mínima | Para quê |
|---|---|---|---|
| Python | 3.10.12 (Ubuntu 22.04) · 3.14.7 é a mais nova | 3.10 | tudo |
| `uv` | 0.12.5 | 0.5 | ambientes e pacotes, rápido |
| `anthropic` (SDK) | 0.123.0 (publicada em 19/08/2026) | 0.40 | chamar a API |
| Node.js | v24.18.0 · LTS 24.19.0 "Krypton" | 22.22 | só para o promptfoo |
| `promptfoo` | 0.122.0 | 0.90 | avaliação declarativa de prompt |
| `dspy` | 3.3.0 | 2.5 | otimização automática de prompt |
| `git` | 2.34+ | 2.20 | versionar prompt |
| `jq` | 1.6+ | 1.5 | ler JSON no terminal |

---

## 0 · Comece hoje, sem instalar nada

Ordem de preferência para quem quer o primeiro resultado em 5 minutos:

| Opção | Custo | O que dá para fazer | Limite |
|---|---|---|---|
| [claude.ai](https://claude.ai) | camada gratuita | conversar, testar prompt, anexar arquivo | cota diária; sem automação |
| [Anthropic Console → Workbench](https://console.anthropic.com/workbench) | precisa de crédito na conta | **o melhor ambiente de prompt que existe**: prompt de sistema separado, variáveis, comparação lado a lado, exportação para código | consome crédito por chamada |
| [Google AI Studio](https://aistudio.google.com/) | gratuito com limites | testar prompt e obter chave de API sem cartão | limite de requisições/dia |
| [Google Colab](https://colab.research.google.com/) | gratuito | rodar Python no navegador, incluindo o SDK | sessão expira; disco temporário |
| [GitHub Codespaces](https://github.com/codespaces) | gratuito até 60 h/mês | ambiente Linux completo no navegador, com VS Code | cota mensal |
| [Tutorial interativo oficial da Anthropic](https://github.com/anthropics/prompt-eng-interactive-tutorial) | gratuito | 9 capítulos com exercícios; há versão em Google Sheets que roda sem instalar nada | — |

**Recomendação:** faça o [04-como-comecar](04-como-comecar.md) inteiro no
Workbench ou no AI Studio. Só instale quando o gargalo passar a ser "preciso
rodar 300 casos e contar os acertos".

---

## 1 · Conta e chave de API

Sem chave, nada abaixo tem serventia.

### Anthropic (usada nos exemplos deste curso)

1. Crie a conta em <https://console.anthropic.com>.
2. **Adicione crédito** em *Settings → Billing*. Requer cartão. Não há camada
   gratuita de API — o mínimo costuma ser US$ 5. (A camada gratuita existe no
   claude.ai, não na API.)
3. Gere a chave em *Settings → API Keys → Create Key*. Ela aparece **uma única
   vez**; copie na hora.
4. Guarde-a como variável de ambiente, nunca no código. Ver [§10](#10--path-e-variáveis-de-ambiente).

Alternativa moderna, que evita chave no disco: o CLI oficial `ant`, com
`ant auth login`, grava um perfil em `~/.config/anthropic/` que os SDKs leem
sozinhos. Se `ant auth status` mostra perfil ativo, o cliente `Anthropic()` sem
argumento nenhum já funciona.

### Alternativas sem cartão

- **Google AI Studio** → *Get API key*: gratuito com limite de requisições.
  Bom para aprender; a biblioteca é outra (`google-genai`).
- **Groq**, **Together**, **OpenRouter**: têm camadas gratuitas ou créditos
  iniciais. Verifique as condições no dia — mudam com frequência.
- **Modelo local com ollama** ([§9](#9--opcional-modelo-local-com-ollama)):
  gratuito para sempre, custa hardware e qualidade.

> **Regra de ouro:** chave de API é senha. Vazou uma vez, revogue e gere outra.
> Nunca cole em prompt, em issue, em captura de tela, em repositório público.
> Ver [variaveis-de-ambiente-e-segredos](../variaveis-de-ambiente-e-segredos/00-MAPA.md).

---

## 2 · Python

### 2.1 · Linux — família Debian/Ubuntu

```bash
sudo apt update && sudo apt install -y python3 python3-venv python3-pip git jq curl
```
Instala o Python do sistema, o módulo de ambientes virtuais, o pip, o git e o `jq`.

```bash
python3 --version
# esperado: Python 3.10.12 (ou superior)
```

Se sair `Python 2.x` ou "command not found", seu sistema é antigo: instale pelo
`uv` ([§2.5](#25--todos-os-sistemas--versão-específica-com-uv)) em vez de brigar
com o gerenciador de pacotes.

### 2.2 · Linux — família Fedora/RHEL

```bash
sudo dnf install -y python3 python3-pip git jq curl
```

```bash
python3 --version
# esperado: Python 3.12.x ou superior no Fedora recente
```

### 2.3 · macOS (Intel e Apple Silicon)

O Python que vem com o macOS é antigo e é usado pelo sistema — **não mexa
nele**. Instale um seu:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```
Instala o Homebrew, o gerenciador de pacotes de facto do macOS.

```bash
brew install python@3.13 git jq
```

```bash
python3 --version
# esperado: Python 3.13.x
```

**Apple Silicon (M1/M2/M3/M4):** o Homebrew instala em `/opt/homebrew`; em
Intel, em `/usr/local`. Se `python3` continuar apontando para o do sistema,
o PATH não pegou o diretório do Homebrew — ver [§10](#10--path-e-variáveis-de-ambiente).

### 2.4 · Windows

**Recomendado: WSL2.** Motivo honesto: praticamente toda a documentação,
todo script de exemplo e toda ferramenta da área supõem Linux. No WSL2 você
segue as instruções de Ubuntu deste manual sem tradução, e não perde tempo
depurando diferenças de caminho e de terminal.

No PowerShell **como administrador**:

```powershell
wsl --install -d Ubuntu-24.04
```
Instala o WSL2 com Ubuntu 24.04. Reinicie quando pedido, crie usuário e senha
do Linux e siga a [§2.1](#21--linux--família-debianubuntu) **dentro** do Ubuntu.

```powershell
wsl --status
# esperado: "Versão padrão: 2"
```

**Windows nativo** (quando WSL2 não é opção — política da empresa, por exemplo):

```powershell
winget install --id Python.Python.3.13 -e
```

```powershell
python --version
# esperado: Python 3.13.x
```

Se `python` abrir a Microsoft Store, o *alias de execução* do Windows está
interceptando: *Configurações → Aplicativos → Aliases de execução de
aplicativo* → desligue `python.exe` e `python3.exe`.

No Windows nativo, use `py -3.13` em vez de `python3`, e barra invertida nos
caminhos. Os comandos deste curso usam a forma Unix.

### 2.5 · Todos os sistemas — versão específica com `uv`

`uv` (Astral, escrito em Rust) instala Python, cria ambientes e instala pacotes
— 10 a 100× mais rápido que o pip. **É o caminho que eu recomendo hoje**, e o
que mais evita os problemas de permissão da [§11](#11--permissões--por-que-sudo-pip-é-uma-armadilha).

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```
Baixa e instala o `uv` em `~/.local/bin` — **sem sudo**.

No Windows nativo (PowerShell):

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

```bash
uv --version
# esperado: uv 0.12.5 (ou superior)
```

Se der `command not found`, `~/.local/bin` não está no PATH — [§10](#10--path-e-variáveis-de-ambiente).

```bash
uv python install 3.13
uv python list
# esperado: uma linha com cpython-3.13.x marcada como instalada
```

### 2.6 · Qual método usar?

| Método | Quando usar | Quando evitar |
|---|---|---|
| Gerenciador do sistema (`apt`/`dnf`) | máquina pessoal, um projeto só | quando precisar de versão específica ou de duas versões |
| **`uv`** ✅ recomendado | qualquer caso profissional | nunca, na prática |
| `pyenv` | você já usa e gosta | é mais lento e exige compilar |
| Instalador oficial (python.org) | Windows nativo sem winget | Linux |
| Docker | equipe grande, CI, reprodutibilidade máxima | primeiro dia de estudo — atrapalha |
| Anaconda | você vem de ciência de dados | projeto novo: traz 3 GB que você não vai usar |

---

## 3 · Ambiente virtual e dependências

**Nunca instale pacote Python no interpretador do sistema.** Um ambiente
virtual é uma pasta com uma cópia isolada do Python e dos pacotes.

Com `uv` (recomendado):

```bash
mkdir -p ~/lab-prompt && cd ~/lab-prompt
uv venv --python 3.13
```
Cria `.venv/` com o Python 3.13.

```bash
source .venv/bin/activate           # Linux, macOS, WSL
# .venv\Scripts\Activate.ps1        # Windows nativo (PowerShell)
```

```bash
which python
# esperado: /home/SEU_USUARIO/lab-prompt/.venv/bin/python
```

Se aparecer `/usr/bin/python`, o ambiente **não** foi ativado — o `source` não
funciona se você rodar o script em vez de o carregar.

Sem `uv`, o equivalente com a biblioteca padrão:

```bash
python3 -m venv .venv && source .venv/bin/activate
```

---

## 4 · SDK da Anthropic

```bash
uv pip install anthropic
# ou, sem uv:  pip install anthropic
```

```bash
python -c "import anthropic; print(anthropic.__version__)"
# esperado: 0.123.0 (ou superior)
```

Se der `ModuleNotFoundError`, você instalou fora do ambiente ativo. Confira com
`which python` e `which pip` — os dois têm de apontar para dentro de `.venv/`.

Teste de ponta a ponta (**consome crédito**, alguns centavos de milésimo):

```bash
export ANTHROPIC_API_KEY=sk-ant-...
python - <<'PY'
import anthropic
r = anthropic.Anthropic().messages.create(
    model="claude-opus-5",
    max_tokens=64,
    messages=[{"role": "user", "content": "Responda apenas: ambiente ok"}],
)
print(r.content[0].text)
PY
# esperado: ambiente ok
```

Erros possíveis e o que significam:

- `AuthenticationError: invalid x-api-key` → chave errada, com espaço, ou de
  outra organização.
- `PermissionError` / crédito insuficiente → falta saldo em *Billing*.
- `APIConnectionError` → rede, proxy ou firewall — vá para a [§12](#12--rede-corporativa--proxy-certificado-firewall).

---

## 5 · Node.js (só para as ferramentas de avaliação)

Você **não** precisa de Node para escrever prompt. Precisa para o `promptfoo`.

### Linux/macOS/WSL — via `nvm` (recomendado, sem sudo)

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
```
Instala o `nvm`, gerenciador de versões do Node, em `~/.nvm`.

Feche e reabra o terminal (o instalador só edita o arquivo de perfil; a sessão
atual não vê a mudança). Então:

```bash
nvm install --lts
nvm alias default lts/*
```

```bash
node --version
# esperado: v24.19.0 (Krypton) ou superior — v24.18.0 também serve
npm --version
# esperado: 11.x
```

### Windows nativo

```powershell
winget install --id OpenJS.NodeJS.LTS -e
```

### Por que não `apt install nodejs`?

Porque a versão dos repositórios de distribuições LTS costuma estar duas linhas
atrás — e o `promptfoo` 0.122.0 exige Node **≥ 22.22.0**. Com `nvm` você
atualiza sem sudo e mantém versões conviventes.

---

## 6 · promptfoo — avaliação declarativa

```bash
npx promptfoo@latest --version
# esperado: 0.122.0 (ou superior)
```
`npx` baixa e executa sem instalar globalmente. **É a forma recomendada** —
evita o problema de permissão da [§11](#11--permissões--por-que-sudo-pip-é-uma-armadilha).

Se você usa todo dia e quer o comando fixo:

```bash
npm install -g promptfoo
```

Se isso der `EACCES`, **não** repita com `sudo`. Configure um prefixo do usuário:

```bash
mkdir -p ~/.npm-global && npm config set prefix ~/.npm-global
echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.bashrc && source ~/.bashrc
npm install -g promptfoo
```

```bash
promptfoo --version
# esperado: 0.122.0
```

> **Nota de contexto (verificada em 19/08/2026):** o promptfoo foi adquirido
> pela OpenAI em 09/03/2026; a empresa declarou que continuará mantendo a
> versão de código aberto. Isso não muda nada hoje na sua instalação, mas é
> fator de risco a acompanhar se você for depender dele em produção.
> Ver [80-custos-e-licencas](80-custos-e-licencas.md).

---

## 7 · DSPy — otimização automática de prompt

Só faz sentido no nível 4 ([45-otimizacao-automatica](45-otimizacao-automatica.md)),
mas instale agora se quiser folhear.

```bash
uv pip install dspy
```

```bash
python -c "import dspy; print(dspy.__version__)"
# esperado: 3.3.0 (ou superior)
```

Exige Python **≥ 3.10 e < 3.15**. Em Python 3.9 a instalação falha na resolução
de dependências — é o sintoma mais comum.

---

## 8 · Editor, git e utilitários

**VS Code** é o padrão de fato. Alternativas legítimas: Neovim, Zed, PyCharm.

```bash
# Ubuntu/Debian
sudo snap install --classic code
# macOS
brew install --cask visual-studio-code
# Windows
winget install --id Microsoft.VisualStudioCode -e
```

Extensões que valem a pena para este trabalho:

| Extensão | Para quê |
|---|---|
| `ms-python.python` | Python, depurador, seleção de ambiente virtual |
| `ms-vscode-remote.remote-wsl` | editar dentro do WSL2 a partir do Windows |
| `redhat.vscode-yaml` | os arquivos do promptfoo são YAML |
| `yzhang.markdown-all-in-one` | prompts versionados em `.md` |
| `anthropic.claude-code` | usar o Claude Code dentro do editor — ver [claude-code](../claude-code/00-MAPA.md) |

```bash
git --version   # esperado: git version 2.34.1 ou superior
jq --version    # esperado: jq-1.6 ou superior
```

`jq` parece detalhe e não é: metade do trabalho é olhar JSON de saída no
terminal. `python3 -m json.tool` serve como substituto pobre.

---

## 9 · Opcional: modelo local com `ollama`

Serve para iterar sem gastar e para trabalhar com dado que não pode sair da
empresa. Não substitui o modelo grande em qualidade.

```bash
curl -fsSL https://ollama.com/install.sh | sh          # Linux
brew install ollama                                    # macOS
# Windows: instalador em https://ollama.com/download
```

```bash
ollama --version
# esperado: uma linha "ollama version is 0.x.y"
```

```bash
ollama run llama3.1:8b "Responda apenas: modelo local ok"
```
Baixa ~5 GB na primeira vez. Exige ~6 GB de RAM livre. Em CPU pura, espere
alguns segundos por resposta.

---

## 10 · PATH e variáveis de ambiente

**PATH** é a lista de pastas onde o terminal procura programas. Metade dos
`command not found` do mundo é PATH.

```bash
echo $PATH | tr ':' '\n'
# esperado: uma pasta por linha; ~/.local/bin deve estar entre elas
```

Se `~/.local/bin` não estiver lá:

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

Qual arquivo editar:

| Terminal | Arquivo | Como recarregar |
|---|---|---|
| bash (padrão do Ubuntu) | `~/.bashrc` | `source ~/.bashrc` |
| zsh (padrão do macOS) | `~/.zshrc` | `source ~/.zshrc` |
| fish | `~/.config/fish/config.fish` | `source` no mesmo caminho |
| PowerShell | `$PROFILE` (`notepad $PROFILE`) | reabrir o terminal |

> **Por que "não pegou" antes de reabrir o terminal?** Porque o arquivo de
> perfil é lido **uma vez**, quando a sessão começa. Alterar o arquivo não
> altera as sessões já abertas. Não é bug; é como processos herdam ambiente.

### A chave de API

```bash
echo 'export ANTHROPIC_API_KEY=sk-ant-...' >> ~/.bashrc && source ~/.bashrc
```

```bash
echo ${ANTHROPIC_API_KEY:0:10}
# esperado: sk-ant-api  (os 10 primeiros caracteres, para não vazar o resto)
```

Melhor prática para projeto: use um arquivo `.env` **fora do git** com
`python-dotenv`, ou o perfil do `ant auth login`. Ver
[variaveis-de-ambiente-e-segredos](../variaveis-de-ambiente-e-segredos/00-MAPA.md).

**Nunca** faça `export ANTHROPIC_API_KEY=...` direto no terminal e esqueça: a
chave fica no `~/.bash_history` em texto puro.

---

## 11 · Permissões — por que `sudo pip` é uma armadilha

Você vai ver conselhos de `sudo pip install` e `sudo npm install -g` na
internet. **Não faça.** As razões, na ordem de importância:

1. **Corrompe o sistema.** Em Ubuntu e Fedora, ferramentas do próprio sistema
   operacional são escritas em Python e dependem de versões específicas de
   pacotes. `sudo pip install` sobrescreve essas versões e quebra o `apt` — um
   estrago chato de desfazer.
2. **Executa código de terceiro como root.** `pip install` roda scripts de
   instalação do pacote. Com `sudo`, esse código tem poder total sobre a
   máquina. Um pacote com nome parecido com o que você quis digitar
   (*typosquatting*) vira comprometimento completo.
3. **Cria arquivos que seu usuário não consegue apagar depois**, o que produz o
   próximo erro de permissão, que produz o próximo `sudo`, e assim por diante.

O Python moderno inclusive se defende disso: em distribuições recentes,
`pip install` fora de ambiente virtual falha com
`error: externally-managed-environment`. **Isso é proteção, não obstáculo** —
crie um venv ([§3](#3--ambiente-virtual-e-dependências)).

| Em vez de | Faça |
|---|---|
| `sudo pip install X` | `uv pip install X` dentro de um `.venv` |
| `sudo npm install -g X` | `npx X@latest` ou prefixo do usuário ([§6](#6--promptfoo--avaliação-declarativa)) |
| `sudo` para consertar permissão | descobrir por que o arquivo é de outro dono |

---

## 12 · Rede corporativa — proxy, certificado, firewall

### Proxy

```bash
export HTTP_PROXY=http://usuario:senha@proxy.empresa.com:8080
export HTTPS_PROXY=$HTTP_PROXY
export NO_PROXY=localhost,127.0.0.1,::1
```

> ⚠️ **Armadilha verificada nesta máquina, em 19/08/2026.** Se o `no_proxy`
> tiver **espaço depois da vírgula** — `no_proxy=localhost, 127.0.0.0/8, ::1` —
> o `curl` tolera, mas o `urllib` do Python **não faz o match**: ele manda a
> requisição para `127.0.0.1` ao proxy e recebe **502**. O sintoma clássico é
> um teste local que falha enquanto o `curl` no mesmo endereço responde 200.
>
> Regra de diagnóstico: **502 vindo de serviço local é impossível — é proxy.**
> Correção: escreva `NO_PROXY` sem espaços; em código Python que chama
> localhost, force o desvio com
> `urllib.request.build_opener(urllib.request.ProxyHandler({}))`.

### Certificado interno (inspeção de TLS)

Sintoma: `SSL: CERTIFICATE_VERIFY_FAILED`.

```bash
export REQUESTS_CA_BUNDLE=/caminho/para/ca-corporativa.pem
export SSL_CERT_FILE=$REQUESTS_CA_BUNDLE
export NODE_EXTRA_CA_CERTS=$REQUESTS_CA_BUNDLE
```
Aponta Python (`requests`/`httpx`), OpenSSL e Node para a autoridade da empresa.

**Nunca** resolva com `verify=False` ou `NODE_TLS_REJECT_UNAUTHORIZED=0`: isso
desliga a verificação para *todo* o tráfego, inclusive sua chave de API.

### Registry espelhado

```bash
pip config set global.index-url https://nexus.empresa.com/repository/pypi/simple
npm config set registry https://nexus.empresa.com/repository/npm/
```

### Firewall

A API da Anthropic sai por HTTPS (443) para `api.anthropic.com`. Se o firewall
bloquear por domínio, peça a liberação desse host — não há faixa de IP estável.

---

## 13 · Convivência de versões

```bash
uv python install 3.11 3.12 3.13     # três versões lado a lado
uv venv --python 3.11 .venv-legado   # um ambiente por projeto
```

Node:

```bash
nvm install 22 && nvm install 24
nvm use 24
node --version   # esperado: v24.x
```

Regra prática: **uma versão por projeto, declarada em arquivo**, nunca "a
versão que está na máquina".

---

## 14 · Reprodutibilidade

Sem isto, seu experimento de prompt não é reproduzível — nem por você, em três
meses.

```bash
uv pip freeze > requirements.txt     # trava as versões exatas de Python
echo "3.13" > .python-version        # versão do Python, lida por uv e pyenv
node --version | sed 's/v//' > .nvmrc  # versão do Node, lida por nvm
```

E, específico da área — **o que mais gente esquece**:

| Anote junto com o resultado | Por quê |
|---|---|
| **ID exato do modelo** (`claude-opus-5`, não "Claude") | modelos mudam de comportamento entre versões |
| **Data da execução** | fornecedores atualizam modelos servidos sob o mesmo nome |
| Parâmetros de amostragem, quando existirem | mudam a variabilidade da saída |
| **Hash do arquivo de prompt** | `git rev-parse HEAD` já resolve, se o prompt estiver versionado |

---

## 15 · Atualizar e voltar atrás

```bash
uv self update                       # o próprio uv
uv pip install --upgrade anthropic   # o SDK
npm update -g promptfoo              # o promptfoo
nvm install --lts --reinstall-packages-from=current
```

Voltar atrás:

```bash
uv pip install anthropic==0.122.0    # versão específica
nvm use 22                           # Node anterior
```

> **Conselho de quem já se queimou:** não atualize SDK na véspera de entrega.
> Atualize, rode a suíte de avaliação, compare os números, **depois** siga.
> Mudança de SDK e mudança de modelo alteram resultado de prompt.

---

## 16 · Desinstalar por completo

```bash
# Ambiente virtual e o projeto inteiro
rm -rf ~/lab-prompt/.venv

# uv (binário, Pythons baixados e cache)
rm -rf ~/.local/bin/uv ~/.local/bin/uvx ~/.local/share/uv ~/.cache/uv

# nvm e todas as versões de Node
rm -rf ~/.nvm
# depois remova as linhas do nvm de ~/.bashrc ou ~/.zshrc

# pacotes globais do npm instalados com prefixo do usuário
rm -rf ~/.npm-global ~/.npm

# ollama (Linux)
sudo systemctl stop ollama && sudo rm /usr/local/bin/ollama
rm -rf ~/.ollama            # ATENÇÃO: isto apaga os modelos baixados (GBs)

# caches que quase todo mundo esquece
rm -rf ~/.cache/pip ~/.cache/huggingface
```

E o que **não** some sozinho: a chave de API no `~/.bashrc`, as linhas de PATH
que os instaladores acrescentaram, o perfil em `~/.config/anthropic/` e o
crédito na conta do fornecedor (cancele o pagamento recorrente, se houver).

---

## 17 · Requisitos reais

| Recurso | Quanto |
|---|---|
| Disco | ~300 MB (Python + SDK) · ~500 MB (Node + promptfoo) · **5–40 GB** se usar ollama |
| Memória | 2 GB para tudo acima · **6 GB+** para modelo local de 8 B |
| Arquitetura | x86-64 e arm64 (Apple Silicon) suportados |
| Conta obrigatória | sim, no provedor de modelo |
| **Cartão de crédito** | **obrigatório na API da Anthropic**; não obrigatório no Google AI Studio nem no ollama |
| Licenças | SDK `anthropic` (MIT), `promptfoo` (MIT), `dspy` (MIT), `uv` (MIT/Apache-2.0). O **modelo** é serviço pago sob termos de uso, não software licenciado a você — ver [80](80-custos-e-licencas.md) |

---

## 18 · Solução de problemas

| Mensagem literal | Causa provável | Correção |
|---|---|---|
| `command not found: uv` (ou `python3`, `node`, `promptfoo`) | binário não está no PATH, ou o terminal não foi reaberto | `echo $PATH \| tr ':' '\n'`; acrescente a pasta no arquivo de perfil e rode `source` — [§10](#10--path-e-variáveis-de-ambiente) |
| `error: externally-managed-environment` | pip fora de ambiente virtual, num sistema que protege o Python dele | crie e ative um venv — [§3](#3--ambiente-virtual-e-dependências). **Não** use `--break-system-packages` |
| `EACCES: permission denied, mkdir '/usr/lib/node_modules'` | `npm install -g` sem permissão | `npx promptfoo@latest`, ou prefixo do usuário — [§6](#6--promptfoo--avaliação-declarativa). Nunca `sudo npm` |
| `ModuleNotFoundError: No module named 'anthropic'` | instalou fora do venv ativo, ou usa dois Pythons | `which python && which pip` — os dois têm de estar em `.venv/` |
| `anthropic.AuthenticationError: invalid x-api-key` | chave errada, com espaço/quebra de linha, revogada, ou de outra organização | `echo ${#ANTHROPIC_API_KEY}` para conferir o tamanho; gere outra no Console |
| `anthropic.APIConnectionError: Connection error` | proxy, firewall ou DNS | teste `curl -I https://api.anthropic.com`; configure proxy — [§12](#12--rede-corporativa--proxy-certificado-firewall) |
| `SSL: CERTIFICATE_VERIFY_FAILED` | inspeção de TLS corporativa | aponte `SSL_CERT_FILE`/`NODE_EXTRA_CA_CERTS` para a CA da empresa — [§12](#12--rede-corporativa--proxy-certificado-firewall) |
| `502 Bad Gateway` chamando `127.0.0.1` | `no_proxy` malformado (espaço após a vírgula) | reescreva `NO_PROXY` sem espaços — [§12](#12--rede-corporativa--proxy-certificado-firewall) |
| `Error: promptfoo requires Node >= 22.22.0` | Node do repositório da distro está velho | instale via `nvm` — [§5](#5--nodejs-só-para-as-ferramentas-de-avaliação) |
| `Credit balance is too low` | conta sem saldo | *Console → Settings → Billing* |
| `RateLimitError: 429` | excedeu requisições por minuto | espere o `retry-after`; reduza a concorrência da avaliação |

---

## 19 · Checklist de "ambiente pronto"

Rode uma linha por vez. Todas têm de responder sem erro:

```bash
python3 --version                                  # ≥ 3.10
uv --version                                       # ≥ 0.12
source ~/lab-prompt/.venv/bin/activate && which python   # dentro de .venv/
python -c "import anthropic; print(anthropic.__version__)"  # ≥ 0.123.0
echo ${ANTHROPIC_API_KEY:0:7}                      # sk-ant-
node --version                                     # ≥ v22.22
npx promptfoo@latest --version                     # ≥ 0.122.0
git --version                                      # ≥ 2.20
jq --version                                       # ≥ 1.6
curl -I https://api.anthropic.com                  # responde (401 é ok: sem chave)
```

Passou tudo? Vá para [04-como-comecar](04-como-comecar.md).

Falhou alguma? Volte à seção correspondente. **Não siga com ambiente meio
pronto** — o erro vai reaparecer disfarçado de "o prompt não funciona".

---

## Autoteste

1. Por que este manual recomenda começar **sem instalar nada**?
2. Explique, em duas frases, por que `sudo pip install` pode quebrar o `apt`.
3. Você editou o `~/.bashrc` e o comando continua "não encontrado". O que
   aconteceu e como resolver?
4. Qual é o sintoma exato de `no_proxy` malformado, e por que ele engana?
5. Três coisas que você deve anotar junto com o resultado de um experimento de
   prompt, além das versões dos pacotes.
6. Qual é o problema de resolver `CERTIFICATE_VERIFY_FAILED` com `verify=False`?
7. `promptfoo` exige Node ≥ 22.22. Por que instalar pelo `apt` costuma não
   servir, e qual é a alternativa sem `sudo`?

---

### Fontes consultadas (19/08/2026)

- PyPI, metadados de `anthropic` 0.123.0 — <https://pypi.org/pypi/anthropic/json>
- PyPI, metadados de `dspy` 3.3.0 — <https://pypi.org/pypi/dspy/json>
- PyPI, metadados de `uv` 0.12.5 — <https://pypi.org/pypi/uv/json>
- npm registry, `promptfoo` 0.122.0 (engines: node ≥ 22.22.0) — <https://registry.npmjs.org/promptfoo/latest>
- Node.js, índice oficial de versões (LTS 24.19.0 "Krypton", 03/08/2026) — <https://nodejs.org/dist/index.json>
- python.org, downloads (3.14.7, 05/08/2026) — <https://www.python.org/downloads/>
- Anúncio de aquisição do promptfoo pela OpenAI (09/03/2026) — <https://openai.com/index/openai-to-acquire-promptfoo/>
- Tutorial interativo oficial — <https://github.com/anthropics/prompt-eng-interactive-tutorial>
- Versões locais verificadas na máquina de escrita: Python 3.10.12, Node v24.18.0.
