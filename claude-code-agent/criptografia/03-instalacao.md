# 03 · Manual de instalação, passo a passo

**Nível:** iniciante · **Última atualização e verificação de versões:** 19/08/2026

Este é um manual de campo. Siga na ordem, confira cada passo, e não improvise.
Se a saída de um comando for diferente da mostrada, **pare e resolva antes de
seguir** — em criptografia, seguir com o ambiente meio quebrado produz erros
que parecem matemáticos e são de instalação.

> **Você não precisa instalar nada para começar hoje.** Pule para a
> [seção 10 — Alternativas sem instalar](#10-alternativas-sem-instalar-nada) se
> quiser o primeiro resultado em cinco minutos. Volte aqui depois.

## Índice

1. [O que vamos instalar, e por quê](#1-o-que-vamos-instalar-e-por-quê)
2. [Requisitos reais](#2-requisitos-reais)
3. [Linux — Debian/Ubuntu](#3-linux--debianubuntu)
4. [Linux — Fedora/RHEL](#4-linux--fedorarhel)
5. [macOS](#5-macos)
6. [Windows](#6-windows-nativo-e-wsl2)
7. [Bibliotecas Python](#7-bibliotecas-python)
8. [PATH, permissões e proxy corporativo](#8-path-permissões-e-proxy-corporativo)
9. [Convivência de versões e reprodutibilidade](#9-convivência-de-versões-e-reprodutibilidade)
10. [Alternativas sem instalar nada](#10-alternativas-sem-instalar-nada)
11. [Atualizar, voltar atrás e desinstalar](#11-atualizar-voltar-atrás-e-desinstalar)
12. [Solução de problemas](#12-solução-de-problemas)
13. [Checklist de ambiente pronto](#13-checklist-de-ambiente-pronto)

---

## 1. O que vamos instalar, e por quê

Um curso de criptografia não usa uma ferramenta só. Cada peça abaixo aparece
em pelo menos um arquivo deste material.

| Ferramenta | Para quê | Obrigatória? |
|---|---|---|
| **Python 3.10+** | projeto-modelo, todos os exemplos, laboratórios | ✅ sim |
| **OpenSSL 3.x** | a navalha suíça: chaves, certificados, cifras, TLS, teste de servidor | ✅ sim |
| **GnuPG 2.4+** | assinatura e cifragem de arquivos e e-mail, rede de confiança | ✅ sim |
| **age 1.2+** | cifragem moderna de arquivos, o contraponto simples ao GPG | ✅ sim |
| **`cryptography` (Python)** | biblioteca de produção; tem ML-KEM e ML-DSA desde a v46 | ✅ sim |
| **PyNaCl (Python)** | ligação com a libsodium; API "difícil de errar" | 🟡 recomendada |
| **Wireshark** | ver um handshake TLS pacote a pacote (arquivo 20) | 🟡 recomendada |
| **curl** | inspecionar TLS de servidores reais | 🟡 quase sempre já vem |
| **mkcert** | autoridade certificadora local, para o laboratório de PKI | ⬜ opcional |
| **hashcat ou John the Ripper** | laboratório de quebra de senha (arquivo 22) | ⬜ opcional |
| **Docker** | rodar tudo isolado, sem sujar a máquina | ⬜ opcional |

**Versões de referência, confirmadas em 19/08/2026:**

| Ferramenta | Versão atual | Mínima aceitável | Evite |
|---|---|---|---|
| Python | 3.14.7 (05/08/2026) | 3.8 | 2.x, e 3.7 ou anterior (sem suporte) |
| OpenSSL | 4.0.1 (09/06/2026); **LTS: 3.5.7**, suporte até 08/04/2030 | 1.1.1 | 1.0.x e 1.1.0 (sem suporte, sem TLS 1.3) |
| GnuPG | 2.5.21 (02/07/2026) | 2.2 | 1.4 (só para ler arquivos antigos) |
| age | 1.3.1 | 1.0 | — |
| `cryptography` (PyPI) | 50.0.0 | 42 | qualquer versão < 42 (CVEs conhecidas) |
| PyNaCl (PyPI) | 1.6.2 | 1.5 | — |

O **OpenSSL 3.5 LTS** é o marco importante deste curso: foi a primeira versão
a trazer **ML-KEM, ML-DSA e SLH-DSA nativos** e a preferir, por padrão, o
grupo híbrido `X25519MLKEM768` no TLS. Se você quer praticar criptografia
pós-quântica, precisa de 3.5 ou superior.

---

## 2. Requisitos reais

| Recurso | Necessário | Observação |
|---|---|---|
| Disco | 400 MB (só o essencial) · 2,5 GB (com Wireshark e Docker) | compilar OpenSSL do fonte pede mais 1,5 GB temporários |
| RAM | 2 GB · 8 GB confortável | o scrypt com N=2¹⁵ pede 32 MiB **por tentativa em paralelo** |
| Arquitetura | x86-64 ou ARM64 | tudo aqui roda nas duas; Apple Silicon incluído |
| Conta em serviço | **nenhuma** | nada neste curso exige cadastro ou cartão |
| Privilégio de administrador | sim, para instalar pacotes do sistema | há caminho sem `sudo` na seção 8 |
| Internet | para instalar e baixar RFCs | depois disso, os laboratórios rodam offline |

---

## 3. Linux — Debian/Ubuntu

*Testado em Ubuntu 22.04.5 LTS, em 19/08/2026.*
Também vale para Debian 12, Linux Mint 21+, Pop!_OS e derivados.

### 3.1 Atualize o índice de pacotes

```bash
sudo apt update
```
> Baixa a lista de pacotes disponíveis. Não instala nada ainda.

### 3.2 Python, pip e venv

```bash
sudo apt install -y python3 python3-pip python3-venv
```
> Instala o interpretador, o gerenciador de pacotes e o módulo de ambientes
> virtuais. No Debian/Ubuntu o `venv` vem separado — e é a causa nº 1 do erro
> `ensurepip is not available`.

Verifique:

```bash
python3 --version
# esperado: Python 3.10.12 (ou superior)
python3 -m venv --help > /dev/null && echo "venv ok"
# esperado: venv ok
python3 -c "import hashlib; print(hashlib.scrypt(b'a', salt=b'b'*16, n=2, r=8, p=1).hex()[:8])"
# esperado: 8 caracteres hexadecimais, por exemplo 88bd5edb
```

**Se a última linha der `ValueError` ou `AttributeError`:** seu Python foi
compilado sem OpenSSL. Em distribuição oficial isso não acontece; se
acontecer, você provavelmente está num Python compilado à mão — use o
`pyenv` da seção 9.

### 3.3 OpenSSL

O Ubuntu 22.04 traz o **3.0.2**, que é suficiente para 90% deste curso, mas
**não tem pós-quântico**. Três caminhos, em ordem de recomendação:

**Caminho A — usar o do sistema (recomendado para começar):**

```bash
sudo apt install -y openssl
openssl version
# esperado no Ubuntu 22.04: OpenSSL 3.0.2 15 Mar 2022
```

**Caminho B — Ubuntu 24.04+ ou Debian 13, que já trazem 3.5:**

```bash
openssl version
# esperado: OpenSSL 3.5.x
```

**Caminho C — compilar o 3.5 LTS ao lado, sem substituir o do sistema
(necessário para os laboratórios pós-quânticos):**

```bash
sudo apt install -y build-essential perl wget
cd /tmp
wget https://github.com/openssl/openssl/releases/download/openssl-3.5.7/openssl-3.5.7.tar.gz
tar xf openssl-3.5.7.tar.gz && cd openssl-3.5.7
./Configure --prefix=$HOME/.local/openssl-3.5 --openssldir=$HOME/.local/openssl-3.5/ssl
make -j"$(nproc)"
make install_sw
```
> `--prefix` é o que impede o desastre: instala em `~/.local`, sem tocar no
> `/usr/bin/openssl` de que o sistema inteiro (apt, ssh, curl) depende.
> **Nunca** rode `make install` de OpenSSL sobre o prefixo padrão numa máquina
> que você usa para trabalhar.

Verifique o novo, sem mexer no antigo:

```bash
$HOME/.local/openssl-3.5/bin/openssl version
# esperado: OpenSSL 3.5.7 (ou a versão que você baixou)
$HOME/.local/openssl-3.5/bin/openssl list -kem-algorithms | grep -i ml-kem
# esperado: linhas mencionando ML-KEM-512 / 768 / 1024
```

Confira a versão exata mais recente da série 3.5 em
<https://openssl-library.org/source/> antes de baixar; o número acima pode ter
avançado.

### 3.4 GnuPG

```bash
sudo apt install -y gnupg
gpg --version | head -2
# esperado no Ubuntu 22.04: gpg (GnuPG) 2.2.27 / libgcrypt 1.9.4
```

A série 2.2 é antiga mas funcional para tudo neste curso. **A série 2.4
chegou ao fim da vida em 30/06/2026**; a linha ativa é a 2.5 (que virará 2.6).
Se quiser a atual, o projeto mantém repositórios próprios para Debian/Ubuntu
desde 27/08/2025 — instruções em <https://gnupg.org/download/>.

### 3.5 age

```bash
sudo apt install -y age
age --version
# Ubuntu 22.04 entrega: v1.0.0
```

O pacote do Ubuntu 22.04 está em **1.0.0**, três anos atrás da versão atual
(1.3.1). Para a versão corrente, baixe o binário oficial:

```bash
cd /tmp
wget https://github.com/FiloSottile/age/releases/download/v1.3.1/age-v1.3.1-linux-amd64.tar.gz
tar xf age-v1.3.1-linux-amd64.tar.gz
mkdir -p ~/.local/bin && mv age/age age/age-keygen ~/.local/bin/
age --version
# esperado: v1.3.1
```
> Se der `command not found`, `~/.local/bin` não está no PATH. Veja a seção 8.

### 3.6 Ferramentas complementares

```bash
sudo apt install -y curl xxd wireshark
```
> `xxd` mostra arquivos em hexadecimal — indispensável para ver o formato de
> um arquivo cifrado. O instalador do Wireshark pergunta se usuários não-root
> podem capturar pacotes; responda **Sim** e depois:

```bash
sudo usermod -aG wireshark "$USER"
# faça logout e login para o grupo valer
```

---

## 4. Linux — Fedora/RHEL

*Comandos conforme a documentação oficial das distribuições; não executados na
máquina de referência deste curso.* Vale para Fedora 40+, RHEL 9/10, Rocky,
AlmaLinux e CentOS Stream.

```bash
sudo dnf install -y python3 python3-pip openssl gnupg2 age curl vim-common wireshark
```
> `vim-common` é o pacote que contém o `xxd` no mundo RPM — detalhe que trava
> muita gente.

Verifique:

```bash
python3 --version   # esperado: 3.12.x no Fedora 40+, 3.9+ no RHEL 9
openssl version     # Fedora 42: 3.5.x · RHEL 9.6: 3.2.x · RHEL 10: 3.5.x
gpg --version | head -1
age --version
```

O **RHEL 10** e o **Fedora 42** já trazem OpenSSL 3.5 com ML-KEM habilitado —
neles não é preciso compilar nada para praticar pós-quântico.

Se o `age` não estiver nos repositórios da sua versão:

```bash
sudo dnf copr enable filippo/age && sudo dnf install age
# ou use o binário oficial, como na seção 3.5
```

---

## 5. macOS

*Comandos conforme a documentação oficial do Homebrew; não executados na
máquina de referência.* Vale para macOS 12 (Monterey) ou superior, Intel e
Apple Silicon.

### 5.1 Homebrew

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```
> Instala o gerenciador de pacotes. Em **Apple Silicon** ele vai para
> `/opt/homebrew`; em **Intel**, para `/usr/local`. Essa diferença é a origem
> de metade dos problemas de PATH em Mac.

Ao terminar, o instalador imprime duas linhas para adicionar ao seu perfil.
Execute-as. Em Apple Silicon costumam ser:

```bash
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"
```

### 5.2 As ferramentas

```bash
brew install python@3.13 openssl@3.5 gnupg age wireshark
```

Verifique:

```bash
python3 --version
brew --prefix openssl@3.5
# esperado: /opt/homebrew/opt/openssl@3.5 (Apple Silicon)
$(brew --prefix openssl@3.5)/bin/openssl version
# esperado: OpenSSL 3.5.x
gpg --version | head -1
age --version
```

### 5.3 A armadilha do OpenSSL no macOS

O macOS traz um `/usr/bin/openssl` que **não é o OpenSSL**: é o **LibreSSL**,
um fork da OpenBSD, com comandos e opções diferentes.

```bash
/usr/bin/openssl version
# esperado: LibreSSL 3.3.x  <- NÃO é o que este curso usa
```

O Homebrew **não** substitui o binário do sistema, de propósito. Para usar o
verdadeiro OpenSSL, ou chame pelo caminho completo, ou coloque-o antes no PATH:

```bash
echo 'export PATH="$(brew --prefix openssl@3.5)/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
openssl version   # agora deve dizer OpenSSL 3.5.x
```

---

## 6. Windows (nativo e WSL2)

**Recomendação explícita: use o WSL2.** Motivo concreto, não ideológico: todo
material de criptografia do mundo — RFC, tutorial, script de curso, resposta
de fórum — pressupõe um shell Unix. No WSL2 você segue qualquer instrução
sem tradução, e ainda edita os arquivos pelo VS Code do Windows normalmente.
O caminho nativo existe abaixo para quem não pode habilitar virtualização.

### 6.1 Caminho recomendado — WSL2

No **PowerShell como administrador**:

```powershell
wsl --install -d Ubuntu-24.04
```
> Habilita a virtualização, instala o kernel do WSL2 e a distribuição.
> Reinicie quando pedir. Na primeira abertura, o Ubuntu pede um nome de
> usuário e uma senha (que não é a do Windows).

Verifique, já dentro do Ubuntu:

```bash
wsl.exe --status     # do PowerShell: deve dizer "Versão padrão: 2"
uname -a             # do Ubuntu: deve conter "microsoft-standard-WSL2"
```

A partir daqui, **siga a seção 3 inteira**. O Ubuntu 24.04 traz OpenSSL 3.4+
e Python 3.12.

Três avisos que economizam horas:

- Trabalhe em `~/` (dentro do Linux), **não** em `/mnt/c/...`. O acesso ao
  disco do Windows pelo WSL2 é dezenas de vezes mais lento e não respeita
  permissões Unix — o que quebra o `chmod 600` que suas chaves privadas
  exigem, inclusive no `ssh` e no `gpg`.
- Para abrir a pasta no VS Code: `code .` dentro do WSL, com a extensão
  *WSL* instalada.
- O `gpg` no WSL não acessa a Windows Hello nem o TPM do Windows. Para chave
  em hardware, use o caminho nativo.

### 6.2 Caminho nativo — winget

No **PowerShell como administrador**:

```powershell
winget install --id Python.Python.3.13 -e
winget install --id GnuPG.Gpg4win -e
winget install --id FiloSottile.age -e
winget install --id WiresharkFoundation.Wireshark -e
```
> `-e` exige correspondência exata do identificador, evitando instalar um
> pacote homônimo de terceiro.

Para o OpenSSL no Windows não existe binário oficial do projeto. As opções
razoáveis, nesta ordem:

1. O OpenSSL que vem com o **Git for Windows** (`winget install Git.Git`),
   disponível dentro do *Git Bash* — suficiente para quase tudo deste curso.
2. As compilações da [Shining Light Productions](https://slproweb.com/products/Win32OpenSSL.html),
   as mais usadas há duas décadas, mas de terceiro: confira o SHA-256
   publicado antes de instalar.
3. WSL2 (volte para 6.1).

Verifique, num **novo** PowerShell (o PATH só é relido em janelas novas):

```powershell
python --version
gpg --version
age --version
```

**Duas armadilhas específicas do Windows:**

- O `python` da Microsoft Store é uma *stub* que abre a loja. Se
  `python --version` abrir a Store, desative os "App execution aliases" em
  *Configurações → Aplicativos → Aliases de execução de aplicativo*.
- O PowerShell mais antigo grava arquivos em **UTF-16 com BOM** ao usar `>`.
  Uma chave pública salva assim não é lida por nenhuma ferramenta. Use
  `Set-Content -Encoding utf8` ou trabalhe no WSL.

---

## 7. Bibliotecas Python

**Nunca instale pacotes Python com `sudo pip install`.** Três motivos
concretos: (1) o `pip` sobrescreve arquivos que o `apt`/`dnf` gerencia,
quebrando ferramentas do sistema escritas em Python — no Ubuntu, isso já
derrubou o próprio `apt`; (2) um pacote malicioso do PyPI executa código de
instalação **como root**; (3) desinstalar depois é adivinhação. Desde o
Python 3.11, com a PEP 668, as distribuições até bloqueiam isso com a
mensagem `error: externally-managed-environment` — e essa mensagem é uma
proteção, não um obstáculo a contornar com `--break-system-packages`.

O caminho certo é um **ambiente virtual**:

```bash
cd ~/estudos/criptografia          # ou onde você guarda este curso
python3 -m venv .venv
source .venv/bin/activate          # Windows PowerShell: .venv\Scripts\Activate.ps1
```
> O prompt passa a mostrar `(.venv)`. A partir daí, `pip` instala **dentro da
> pasta**, sem tocar no sistema. Para sair: `deactivate`.

```bash
pip install --upgrade pip
pip install cryptography pynacl
```

Verifique — *saída real desta máquina, em 19/08/2026*:

```bash
python -c "import cryptography, nacl; print(cryptography.__version__, nacl.__version__)"
# esperado: 50.0.0 1.6.2 (ou superior)
python -c "from cryptography.hazmat.backends.openssl.backend import backend; print(backend.openssl_version_text())"
# esperado: OpenSSL 4.0.1 9 Jun 2026
```

Repare no segundo comando: a roda (*wheel*) do `cryptography` **embute a
própria cópia do OpenSSL**. Ou seja, a versão do OpenSSL do seu sistema não
limita a biblioteca Python — o que explica como se tem ML-KEM em Python numa
máquina cujo `openssl version` diz 3.0.2:

```bash
python -c "from cryptography.hazmat.primitives.asymmetric import mlkem, mldsa; print('PQC disponível')"
# esperado: PQC disponível  (a partir do cryptography 46)
```

### Se você prefere `uv` (mais rápido, moderno)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh   # Linux/macOS
uv venv && source .venv/bin/activate
uv pip install cryptography pynacl
```

### Escolhendo a biblioteca certa

| Biblioteca | Quando usar | Cuidado |
|---|---|---|
| **`cryptography`** | padrão para quase tudo em Python; tem PQC | a API "hazmat" é de baixo nível de propósito: se você está lá, saiba por quê |
| **PyNaCl** | quando quer uma API que é difícil de usar errado | menos algoritmos, e é essa a intenção |
| **`pycryptodome`** | ler código legado, CTFs, CryptoHack | permite construções inseguras sem avisar |
| `pycrypto` | **nunca** | abandonada desde 2014, com CVEs sem correção |

---

## 8. PATH, permissões e proxy corporativo

### 8.1 PATH — por que "não pegou"

O PATH é a lista de pastas onde o shell procura um comando. Quando você
instala um binário em `~/.local/bin` e o shell responde `command not found`,
é quase sempre porque essa pasta não está na lista.

```bash
echo "$PATH" | tr ':' '\n'
# procure ~/.local/bin ou /home/seu-usuario/.local/bin na saída
```

Corrigindo, no arquivo certo para o seu shell:

| Shell | Arquivo | Como saber que é o seu |
|---|---|---|
| bash | `~/.bashrc` | `echo $SHELL` termina em `/bash` |
| zsh (padrão no macOS) | `~/.zshrc` | `echo $SHELL` termina em `/zsh` |
| fish | `~/.config/fish/config.fish` | — |
| PowerShell | saída de `$PROFILE` | — |

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc      # <- este é o passo que todo mundo esquece
```

**Por que a mudança "não pegou" antes de reabrir o terminal:** o shell lê o
arquivo de perfil **uma vez**, ao iniciar. Editar o arquivo não afeta sessões
já abertas. `source` relê agora; abrir um terminal novo tem o mesmo efeito.

Ordem importa: `$HOME/.local/bin:$PATH` coloca sua pasta **antes**, então sua
versão vence a do sistema. Trocar para `$PATH:$HOME/.local/bin` faz o
contrário — e é a causa de "instalei o age 1.3.1 mas `age --version` insiste
em dizer 1.0.0".

### 8.2 Permissões — o `sudo` que atrapalha

| Situação | Errado | Certo | Por quê |
|---|---|---|---|
| Instalar pacote Python | `sudo pip install X` | `python3 -m venv .venv` + `pip install X` | quebra o gerenciador de pacotes do sistema e roda código de terceiro como root |
| Instalar binário pessoal | `sudo cp age /usr/local/bin` | `cp age ~/.local/bin` | não exige privilégio, não conflita com o gerenciador de pacotes |
| Gerar chave | `sudo ssh-keygen` | `ssh-keygen` | a chave nasce de root e seu usuário não consegue mais usá-la |
| Ler `~/.gnupg` | `sudo gpg --list-keys` | `gpg --list-keys` | o `sudo` cria arquivos de root dentro do seu `~/.gnupg` e o GPG passa a falhar de forma inexplicável |

Permissões exigidas por arquivos de chave:

```bash
chmod 700 ~/.gnupg && chmod 600 ~/.gnupg/*
chmod 700 ~/.ssh   && chmod 600 ~/.ssh/id_*
```
> Ferramentas sérias **recusam** chaves privadas legíveis por outros usuários.
> Não é frescura: num servidor compartilhado, `chmod 644` numa chave privada é
> equivalente a publicá-la.

### 8.3 Rede corporativa

```bash
export HTTP_PROXY="http://usuario:senha@proxy.empresa.com:8080"
export HTTPS_PROXY="$HTTP_PROXY"
export NO_PROXY="localhost,127.0.0.1,::1,.empresa.com"
```
> **Atenção ao `NO_PROXY`**: separado por vírgula, **sem espaços**. Um espaço
> a mais quebra bibliotecas Python de um jeito difícil de diagnosticar — o
> cliente tenta falar com `localhost` através do proxy e trava.

Certificado interno (a empresa faz inspeção de TLS):

```bash
# Debian/Ubuntu
sudo cp empresa-raiz.crt /usr/local/share/ca-certificates/
sudo update-ca-certificates
# Fedora/RHEL
sudo cp empresa-raiz.crt /etc/pki/ca-trust/source/anchors/
sudo update-ca-trust
# Python (pip e requests)
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
export PIP_CERT=/etc/ssl/certs/ca-certificates.crt
```

**Nunca** resolva isso com `pip install --trusted-host` nem
`curl -k`/`--insecure`. Você estaria desligando exatamente a verificação que
este curso ensina a fazer. Vale o desconforto de configurar direito — e a
ironia de aprender criptografia com verificação desativada não passa
despercebida em entrevista.

Registry espelhado (Artifactory, Nexus):

```bash
pip config set global.index-url https://nexus.empresa.com/repository/pypi/simple
```

---

## 9. Convivência de versões e reprodutibilidade

### Duas versões de Python na mesma máquina

`pyenv` é a ferramenta padrão:

```bash
curl -fsSL https://pyenv.run | bash
# siga as três linhas que ele manda acrescentar ao ~/.bashrc, e recarregue
pyenv install 3.13.5
pyenv local 3.13.5        # cria .python-version nesta pasta
python --version          # esperado: Python 3.13.5
```
> `pyenv local` grava um arquivo `.python-version` na pasta. Quem clonar o
> repositório pega a mesma versão automaticamente. Isso é reprodutibilidade
> barata.

### Duas versões de OpenSSL

Já resolvido na seção 3.3 com `--prefix`. Para alternar sem confusão:

```bash
alias openssl35="$HOME/.local/openssl-3.5/bin/openssl"
openssl version      # o do sistema
openssl35 version    # o novo
```
> Nunca troque `/usr/bin/openssl` por um binário compilado à mão. `apt`,
> `curl`, `ssh` e `git` dependem da biblioteca correspondente, e a
> incompatibilidade aparece como erro de rede aleatório dias depois.

### Fixando tudo

```bash
pip freeze > requirements.txt      # versões exatas das bibliotecas
python --version > .python-version # versão do interpretador
```

Para reprodutibilidade completa, um container:

```dockerfile
# Dockerfile — ambiente do curso, idêntico em qualquer máquina
FROM python:3.13-slim-bookworm
RUN apt-get update && apt-get install -y --no-install-recommends \
        openssl gnupg age curl xxd ca-certificates \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir cryptography==50.0.0 pynacl==1.6.2
WORKDIR /curso
CMD ["bash"]
```

```bash
docker build -t curso-cripto .
docker run --rm -it -v "$PWD":/curso curso-cripto
```

---

## 10. Alternativas sem instalar nada

Comece hoje, instale depois. Todas gratuitas, todas verificadas em 19/08/2026.

| Recurso | O que dá para fazer | Link |
|---|---|---|
| **CryptoHack** | plataforma de desafios de criptografia, do zero ao avançado, tudo no navegador; conta gratuita | <https://cryptohack.org/> |
| **CyberChef** (GCHQ) | cifrar, decifrar, hash, base64, XOR, análise de frequência — arrastando blocos | <https://gchq.github.io/CyberChef/> |
| **Google Colab** | Python completo no navegador; `!pip install cryptography` funciona | <https://colab.research.google.com/> |
| **Cryptii** | conversões e cifras clássicas, visual, ótimo para o arquivo 11 | <https://cryptii.com/> |
| **SSL Labs Server Test** | analisa o TLS de qualquer site público, com nota | <https://www.ssllabs.com/ssltest/> |
| **badssl.com** | servidores propositalmente quebrados, para ver o navegador recusar | <https://badssl.com/> |
| **GitHub Codespaces** | máquina Linux completa no navegador; camada gratuita mensal | <https://github.com/codespaces> |

Com Colab + CryptoHack você faz talvez 60% dos laboratórios deste curso sem
instalar coisa alguma. O que não dá para fazer no navegador: Wireshark com
captura real, GPG com chave em hardware, e medir tempo de execução com
seriedade.

---

## 11. Atualizar, voltar atrás e desinstalar

### Atualizar

```bash
sudo apt update && sudo apt upgrade -y          # Debian/Ubuntu
sudo dnf upgrade --refresh                      # Fedora/RHEL
brew update && brew upgrade                     # macOS
winget upgrade --all                            # Windows
pip install --upgrade cryptography pynacl       # dentro do venv
```

### Voltar atrás

```bash
# Ubuntu: instalar uma versão específica anterior
apt-cache policy openssl          # lista as versões disponíveis
sudo apt install openssl=3.0.2-0ubuntu1.26

# Python (dentro do venv)
pip install cryptography==49.0.0

# Homebrew
brew uninstall openssl@3.5 && brew install openssl@3.0
```

**Antes de atualizar o GnuPG entre séries maiores** (2.2 → 2.5), copie o
diretório de chaves:

```bash
tar czf ~/gnupg-backup-$(date +%F).tar.gz -C ~ .gnupg
```
> O formato interno do chaveiro mudou entre séries. Sem cópia, uma atualização
> malsucedida custa suas chaves — e chave privada perdida não se recupera de
> nenhum jeito. Guarde essa cópia cifrada, em outro lugar.

### Desinstalar por completo

```bash
# pacotes do sistema
sudo apt remove --purge age gnupg wireshark && sudo apt autoremove
sudo dnf remove age gnupg2 wireshark
brew uninstall age gnupg openssl@3.5

# binários instalados à mão
rm -f ~/.local/bin/age ~/.local/bin/age-keygen
rm -rf ~/.local/openssl-3.5

# ambiente Python
deactivate 2>/dev/null; rm -rf .venv

# restos que quase todo tutorial esquece  ⚠️ CONTÊM SUAS CHAVES PRIVADAS
ls -la ~/.gnupg          # chaveiro GPG
ls -la ~/.config/age     # se você criou
ls -la ~/.cache/pip      # cache de pacotes, pode ter centenas de MB
ls -la ~/.pyenv          # interpretadores do pyenv
```
> Olhe antes de apagar. `~/.gnupg` contém chaves privadas que podem ser as
> únicas cópias existentes. Apagar é irreversível — não há "recuperar senha"
> em criptografia.

Para apagar de verdade material sensível em disco:

```bash
shred -u arquivo-com-chave.txt        # sobrescreve antes de remover
```
> Ressalva honesta: em **SSD** e em sistemas de arquivos com *copy-on-write*
> (Btrfs, ZFS, APFS), o `shred` **não garante** nada — o controlador do disco
> pode ter escrito em outra célula física. A proteção real é ter o disco
> cifrado desde o início (LUKS, FileVault, BitLocker).

---

## 12. Solução de problemas

| Mensagem literal | Causa provável | Correção |
|---|---|---|
| `command not found: age` | binário fora do PATH, ou instalado em `~/.local/bin` sem o PATH ajustado | `echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc && source ~/.bashrc` |
| `error: externally-managed-environment` | PEP 668: o sistema proíbe `pip install` global (Debian 12+, Ubuntu 23.04+, Fedora 38+) | crie um venv: `python3 -m venv .venv && source .venv/bin/activate`. Não use `--break-system-packages` |
| `ensurepip is not available` | falta o pacote `python3-venv` no Debian/Ubuntu | `sudo apt install python3-venv` |
| `ValueError: [digital envelope routines] memory limit exceeded` | `hashlib.scrypt` com N grande e `maxmem` no padrão do OpenSSL (32 MiB) | passe `maxmem=128*1024*1024` na chamada; ver `cofrelib/kdf.py` |
| `EACCES: permission denied` ao instalar | tentativa de escrever em pasta do sistema sem privilégio | instale no venv ou em `~/.local`; **não** resolva com `sudo` |
| `gpg: agent_genkey failed: No such file or directory` | `~/.gnupg` com dono ou permissão errados, quase sempre por um `sudo gpg` anterior | `sudo chown -R "$USER:$USER" ~/.gnupg && chmod 700 ~/.gnupg && chmod 600 ~/.gnupg/*` |
| `gpg: signing failed: Inappropriate ioctl for device` | o `pinentry` não achou um terminal para pedir a senha (comum em SSH e em scripts) | `export GPG_TTY=$(tty)` no `~/.bashrc`; se persistir, `echo "pinentry-mode loopback" >> ~/.gnupg/gpg.conf` |
| `SSL: CERTIFICATE_VERIFY_FAILED` no `pip` | proxy corporativo com inspeção de TLS, ou CA do sistema desatualizada | instale a CA da empresa (seção 8.3) e aponte `PIP_CERT`. **Nunca** `--trusted-host` |
| `openssl: error while loading shared libraries: libssl.so.3` | binário compilado à mão sem `LD_LIBRARY_PATH`, ou instalação parcial | `export LD_LIBRARY_PATH=$HOME/.local/openssl-3.5/lib64:$LD_LIBRARY_PATH`, ou recompile com `-Wl,-rpath` |
| `unknown option -provider` no `openssl` | você está usando o **LibreSSL** do macOS, não o OpenSSL | use `$(brew --prefix openssl@3.5)/bin/openssl` |
| `age: error: no identity matched any of the recipients` | chave privada errada, ou arquivo destinado a outra chave pública | confira com `age-keygen -y sua.chave` qual pública corresponde à sua privada |
| No Windows: `python` abre a Microsoft Store | alias de execução da Store ativo | *Configurações → Aplicativos → Aliases de execução*, desative `python.exe` e `python3.exe` |
| `bash: /mnt/c/...: Permission denied` no WSL | permissões Unix não funcionam no disco do Windows | mova o trabalho para `~/` dentro do WSL |

---

## 13. Checklist de ambiente pronto

Rode tudo. Cada linha deve responder sem erro.

```bash
python3 --version                                    # >= 3.8
python3 -m venv --help > /dev/null && echo venv-ok   # venv-ok
openssl version                                      # OpenSSL 3.x
gpg --version | head -1                              # gpg (GnuPG) 2.x
age --version                                        # v1.x
curl --version | head -1                             # curl 7.x ou 8.x
echo -n abc | sha256sum                              # ba7816bf8f01cfea...
python3 -c "import hashlib;print(hashlib.scrypt(b'a',salt=b'b'*16,n=2,r=8,p=1).hex()[:8])"
python3 -c "import secrets; print(secrets.token_hex(16))"   # 32 hex, diferentes a cada execução
openssl rand -hex 16                                 # 32 hex, diferentes a cada execução
```

E o teste final, que exercita o curso inteiro de uma vez:

```bash
cd criptografia/07-projeto-modelo && python3 cofre.py autoteste
```

Saída esperada:

```
[ok ] RFC 8439 2.8.2 AEAD (etiqueta)
[ok ] RFC 8439 2.5.2 Poly1305
[ok ] RFC 7748 6.1 X25519 (segredo compartilhado)
[ok ] RFC 5869 A.1 HKDF-SHA256
autoteste: tudo certo
```

Se você chegou aqui com tudo verde, o ambiente está pronto.
Vá para [04-como-comecar.md](04-como-comecar.md).

---

## Autoteste

1. Por que não se deve rodar `sudo pip install`? Dê dois motivos diferentes.
2. Qual versão mínima do OpenSSL traz ML-KEM nativo, e até quando ela tem
   suporte?
3. O `openssl` de `/usr/bin` no macOS é o OpenSSL? O que é, e como usar o certo?
4. Você instalou o `age` 1.3.1 em `~/.local/bin`, mas `age --version` diz
   1.0.0. O que aconteceu e como se corrige?
5. Por que a alteração no `~/.bashrc` "não pegou" no terminal já aberto?
6. Que arquivo você tem de copiar antes de atualizar o GnuPG entre séries, e
   por que a pressa aqui é perigosa?
7. Cite dois recursos que permitem estudar criptografia hoje sem instalar nada.
8. Qual mensagem de erro indica o limite de memória do scrypt, e qual é a
   correção exata?

---

**Fontes consultadas em 19/08/2026:**
[Roadmap e ciclo de vida do OpenSSL](https://openssl-library.org/roadmap/index.html) ·
[Notas da série OpenSSL 3.5](https://openssl-library.org/news/openssl-3.5-notes/) ·
[Releases do age](https://github.com/FiloSottile/age/releases) ·
[Notícias do GnuPG](https://www.gnupg.org/news.html) ·
[Downloads do Python](https://www.python.org/downloads/) ·
PyPI (`cryptography` 50.0.0, PyNaCl 1.6.2, instalados e verificados nesta máquina) ·
versões de Ubuntu conferidas por `apt-cache policy` em Ubuntu 22.04.5.

**Anterior:** [02-pre-requisitos.md](02-pre-requisitos.md) ·
**Próximo:** [04-como-comecar.md](04-como-comecar.md)
