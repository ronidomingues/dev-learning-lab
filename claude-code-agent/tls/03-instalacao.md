# 03 · Manual de instalação

**Nível:** iniciante · **Data desta revisão:** 31/08/2026
**Verificado em:** Ubuntu 22.04.5 LTS, OpenSSL 3.0.2, curl 7.81.0, Python 3.10.12,
Node v24.18.0, Docker 29.7.2 — todos conferidos com o comando de versão nesta máquina.

Este é um manual de campo. Siga na ordem, um bloco por vez, e confira a saída de cada
verificação antes de seguir. Nada aqui pede que você improvise.

> ### Leia esta caixa antes de instalar qualquer coisa
> **Se você só quer ver TLS funcionando hoje, pule para a [§0 — sem instalar nada](#0-alternativa-sem-instalar-nada).**
> Dá para fazer os primeiros três laboratórios inteiros no navegador ou num container.
> Instalar tudo leva de 30 a 90 minutos; começar leva 2.

---

## Índice

- [§0 Alternativa sem instalar nada](#0-alternativa-sem-instalar-nada)
- [§1 O que vamos instalar e por quê](#1-o-que-vamos-instalar-e-por-quê)
- [§2 Linux — Debian/Ubuntu](#2-linux--debianubuntu)
- [§3 Linux — Fedora/RHEL/Rocky](#3-linux--fedorarhelrocky)
- [§4 macOS (Intel e Apple Silicon)](#4-macos-intel-e-apple-silicon)
- [§5 Windows — nativo e WSL2](#5-windows--nativo-e-wsl2)
- [§6 Docker — o caminho universal](#6-docker--o-caminho-universal)
- [§7 PATH e variáveis de ambiente](#7-path-e-variáveis-de-ambiente)
- [§8 Permissões — e onde `sudo` estraga tudo](#8-permissões--e-onde-sudo-estraga-tudo)
- [§9 Rede corporativa: proxy e certificado interno](#9-rede-corporativa-proxy-e-certificado-interno)
- [§10 Convivência de versões do OpenSSL](#10-convivência-de-versões-do-openssl)
- [§11 Reprodutibilidade](#11-reprodutibilidade)
- [§12 Atualizar e voltar atrás](#12-atualizar-e-voltar-atrás)
- [§13 Desinstalar por completo](#13-desinstalar-por-completo)
- [§14 Solução de problemas — erros literais](#14-solução-de-problemas--erros-literais)
- [§15 Checklist "ambiente pronto"](#15-checklist-ambiente-pronto)

---

## 0. Alternativa sem instalar nada

| Opção | O que dá para fazer | Link |
|---|---|---|
| **SSL Labs Server Test** | auditar qualquer site público: versões, cifras, cadeia, nota A–F | <https://www.ssllabs.com/ssltest/> |
| **Hardenize** | visão de TLS + DNS + e-mail de um domínio | <https://www.hardenize.com/> |
| **crt.sh** | ver todo certificado já emitido para um domínio (Certificate Transparency) | <https://crt.sh/> |
| **badssl.com** | dezenas de sites deliberadamente quebrados (expirado, autoassinado, nome errado, cifra fraca) para você ver cada erro | <https://badssl.com/> |
| **GitHub Codespaces / Gitpod** | terminal Linux completo no navegador, com OpenSSL e curl prontos | <https://github.com/codespaces> |
| **Docker sem instalar nada localmente** | ver §6 | — |

Um comando que já ensina muito, e que roda em qualquer terminal que tenha `curl`
(inclusive o PowerShell do Windows):

```bash
curl -sv https://badssl.com/ -o /dev/null 2>&1 | grep -E "TLS|subject|issuer"
```

---

## 1. O que vamos instalar e por quê

TLS não é *um* programa. É um protocolo implementado por várias bibliotecas e
manipulado por várias ferramentas. Instalar "TLS" não faz sentido; instalar o
**conjunto** faz.

| Grupo | Ferramenta | Papel | Obrigatório |
|---|---|---|---|
| **Biblioteca / canivete** | **OpenSSL** | gera chaves, cria certificados, abre conexões de teste, inspeciona tudo | **sim** |
| **Cliente** | **curl** | testar HTTPS como um cliente real faz | **sim** |
| **Linguagem** | **Python 3** | exemplos e projeto-modelo (`ssl` é biblioteca padrão) | **sim** |
| | Node.js | exemplos alternativos (`tls`, `https` são nativos) | não |
| **CA local** | **mkcert** | certificados para `localhost` já confiáveis pelo seu SO/navegador | recomendado |
| **CA pública** | **certbot** (ou `lego`, `acme.sh`) | obter certificado real do Let's Encrypt | só p/ ACME |
| **Servidor** | **nginx** | o servidor onde a configuração de TLS é ensinada | só p/ §17 |
| | **Caddy** | servidor que faz HTTPS automático sem você escrever nada | alternativa |
| **Auditoria** | **testssl.sh** | varre um endpoint e diz tudo que está fraco | recomendado |
| | **nmap** (`ssl-enum-ciphers`) | mesma coisa, por outro ângulo | opcional |
| **Ver no fio** | **Wireshark** / `tshark` | ver o handshake pacote a pacote | recomendado |
| **Isolamento** | **Docker** | rodar laboratórios sem sujar a máquina | opcional, facilita |

**Requisitos reais de espaço:** OpenSSL+curl+Python ≈ 150 MB (quase sempre já
instalados); +nginx ≈ 60 MB; +Wireshark ≈ 400 MB; +Docker ≈ 900 MB; +Node ≈ 120 MB.
Nenhuma dessas ferramentas exige conta, licença paga ou cartão de crédito.

---

## 2. Linux — Debian/Ubuntu

> Testado em **Ubuntu 22.04.5 LTS** em 31/08/2026. Vale igualmente para Debian 12+,
> Linux Mint 21+, Pop!_OS e derivados. Onde o nome do pacote muda, está anotado.

### 2.1 Atualizar a lista de pacotes

```bash
sudo apt update
```
Atualiza o catálogo local de pacotes disponíveis (não instala nada ainda).

```bash
# esperado: termina com "Reading package lists... Done" e sem linha "Err:"
```

Se aparecer `Err:` com `Could not connect`, você provavelmente está atrás de proxy — vá para a [§9](#9-rede-corporativa-proxy-e-certificado-interno).

### 2.2 OpenSSL

```bash
sudo apt install -y openssl ca-certificates
```
Instala o canivete suíço do TLS e o repositório de certificados raiz do sistema.

```bash
openssl version
# esperado nesta máquina: OpenSSL 3.0.2 15 Mar 2022
# aceitável: qualquer 3.0.x ou superior
# NÃO aceitável: 1.0.x ou 1.1.0 (sem suporte a TLS 1.3; fim de vida)
# 1.1.1 tem TLS 1.3, mas encerrou o suporte público em 11/09/2023 — atualize
```

**Se a saída for `OpenSSL 1.1.1...` ou anterior:** seu sistema é antigo. Não substitua
o OpenSSL do sistema à força (metade dos programas do Linux liga contra ele — você
quebra o `apt` e o `ssh`). Instale uma segunda versão em paralelo: [§10](#10-convivência-de-versões-do-openssl).

**Versão mínima recomendada e por quê:**

| Você precisa de… | Versão mínima |
|---|---|
| TLS 1.3 | 1.1.1 |
| Suporte mantido | 3.0 |
| `-groups` com ML-KEM (pós-quântico) | **3.5** |
| Provider padrão com Ed25519 em CMS, e melhorias de desempenho | 3.2+ |

O Ubuntu 22.04 traz 3.0.2; o Ubuntu 24.04 traz 3.0.13; o Ubuntu 26.04 traz uma 3.5.x.
Para experimentar pós-quântico sem trocar de distro, use o container da [§6](#6-docker--o-caminho-universal).

### 2.3 curl

```bash
sudo apt install -y curl
```
Cliente HTTP de linha de comando; é como testaremos quase tudo.

```bash
curl --version | head -2
# esperado: curl 7.81.0 (x86_64-pc-linux-gnu) libcurl/7.81.0 OpenSSL/3.0.2 ...
```

Repare no trecho `OpenSSL/3.0.2`: **o curl não usa o binário `openssl`, ele usa a
biblioteca**. Em algumas distros o curl é compilado contra GnuTLS ou NSS, e aí o
comportamento de TLS difere sutilmente (mensagens de erro, opções aceitas). Saber
com qual biblioteca o seu curl foi compilado já resolve um tipo inteiro de confusão.

### 2.4 Python 3 e o módulo `ssl`

```bash
sudo apt install -y python3 python3-venv python3-pip
```
Interpretador, criador de ambientes virtuais e instalador de pacotes.

```bash
python3 --version
# esperado: Python 3.10.12 (qualquer 3.9+ serve)

python3 -c "import ssl; print(ssl.OPENSSL_VERSION); print(ssl.HAS_TLSv1_3)"
# esperado:
# OpenSSL 3.0.2 15 Mar 2022
# True
```

Se a segunda linha imprimir `False`, seu Python foi compilado contra um OpenSSL
sem TLS 1.3 — refaça a instalação do Python pelo `pyenv` ([§10](#10-convivência-de-versões-do-openssl)).

### 2.5 mkcert — a CA local que salva sua sanidade

`mkcert` cria uma autoridade certificadora só sua, **instala a raiz dela no
repositório de confiança do seu sistema e dos navegadores**, e emite certificados
para `localhost` que não geram aviso. É a diferença entre praticar TLS em paz e
clicar em "aceitar risco" cem vezes por dia.

Caminho recomendado no Ubuntu 22.04+ (o pacote existe no repositório oficial):

```bash
sudo apt install -y mkcert libnss3-tools
```
`libnss3-tools` é o que permite ao mkcert instalar a raiz no Firefox e no Chrome, não só no sistema.

```bash
mkcert -version
# esperado: v1.4.4 (ou superior)
```

Se `mkcert` não existir no seu apt (Debian 11, Ubuntu 20.04), instale o binário:

```bash
curl -fsSLo /tmp/mkcert "https://dl.filippo.io/mkcert/latest?for=linux/amd64"
```
Baixa o binário oficial para a arquitetura x86-64.

```bash
chmod +x /tmp/mkcert && sudo mv /tmp/mkcert /usr/local/bin/mkcert
mkcert -version   # esperado: v1.4.4
```

Agora crie a CA local **uma única vez**:

```bash
mkcert -install
# esperado: "Created a new local CA 💥" e "The local CA is now installed in the system trust store! 👍"
```

```bash
mkcert -CAROOT
# esperado: /home/SEU_USUARIO/.local/share/mkcert
```

> ⚠️ **A chave privada dessa CA fica nesse diretório.** Quem tiver o arquivo
> `rootCA-key.pem` pode forjar certificado para *qualquer* domínio e o **seu**
> computador vai aceitar. Nunca copie esse arquivo para outra máquina, nunca
> versione, e rode `mkcert -uninstall` se a máquina for compartilhada.

### 2.6 nginx

```bash
sudo apt install -y nginx
```
Servidor web/proxy reverso; é onde vamos configurar TLS "de verdade".

```bash
nginx -v
# esperado: nginx version: nginx/1.18.0 (Ubuntu)   <- no 22.04
# a linha oficial estável em 2026 é a 1.30.x; a do sistema é mais antiga, e tudo bem para aprender
sudo systemctl status nginx --no-pager | head -3
# esperado: "Active: active (running)"
```

Verificação de verdade:

```bash
curl -sI http://localhost | head -1
# esperado: HTTP/1.1 200 OK
```

Para a versão nova (recursos como `ssl_conf_command`, HTTP/3), use o repositório
oficial do nginx em vez do da distro:

```bash
curl -fsSL https://nginx.org/keys/nginx_signing.key | sudo gpg --dearmor -o /usr/share/keyrings/nginx.gpg
```
Baixa e converte a chave PGP com que o projeto nginx assina os pacotes.

```bash
echo "deb [signed-by=/usr/share/keyrings/nginx.gpg] http://nginx.org/packages/ubuntu $(lsb_release -cs) nginx" | sudo tee /etc/apt/sources.list.d/nginx.list
sudo apt update && sudo apt install -y nginx
nginx -v   # esperado: nginx version: nginx/1.30.x
```

### 2.7 Caddy — HTTPS automático

Caddy obtém e renova certificado do Let's Encrypt sozinho, sem você configurar nada.
É a forma mais rápida de ter HTTPS real em produção.

```bash
sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo apt update && sudo apt install -y caddy
```

```bash
caddy version
# esperado: v2.11.x (a linha estável em 2026)
```

> **Conflito de porta:** nginx e Caddy querem a porta 80/443. Não deixe os dois
> ativos. `sudo systemctl stop nginx` antes de brincar com Caddy, e vice-versa.

### 2.8 certbot

```bash
sudo apt install -y certbot python3-certbot-nginx
```
Cliente ACME oficial do Let's Encrypt (EFF), com o plugin que edita a config do nginx sozinho.

```bash
certbot --version
# esperado: certbot 1.21.0 (versão do 22.04) — no repositório oficial a linha é 5.x
```

O `snap` traz a versão nova, e é o que a documentação oficial recomenda:

```bash
sudo snap install --classic certbot && sudo ln -sf /snap/bin/certbot /usr/bin/certbot
certbot --version   # esperado: certbot 5.x
```

### 2.9 testssl.sh — auditoria

```bash
git clone --depth 1 https://github.com/testssl/testssl.sh.git ~/testssl.sh
```
Clona o script (é Bash puro, não precisa compilar).

```bash
~/testssl.sh/testssl.sh --version
# esperado: testssl.sh 3.2 (ou 3.0.x na branch estável)
```

Teste real (leva ~2 min):

```bash
~/testssl.sh/testssl.sh --quiet --protocols https://example.com
# esperado: SSLv2/SSLv3/TLS1/TLS1.1 "not offered", TLS1.2 e TLS1.3 "offered"
```

### 2.10 Wireshark / tshark

```bash
sudo apt install -y wireshark tshark
```
Analisador de pacotes gráfico e sua versão de terminal.

Durante a instalação aparece a pergunta *"Should non-superusers be able to capture packets?"* — responda **Yes**. Depois:

```bash
sudo usermod -aG wireshark "$USER"
```
Coloca seu usuário no grupo que pode capturar sem `sudo`.

> **Faça logout e login** (ou reinicie) para o grupo valer. Se não fizer, você vai
> ver "no interfaces available" e achar que a instalação falhou. Confira com `id | grep wireshark`.

```bash
tshark --version | head -1
# esperado: TShark (Wireshark) 3.6.x ou superior
```

### 2.11 Node.js (opcional)

Não use o `nodejs` do apt do Ubuntu 22.04 (é antigo). Use um gerenciador de versões:

```bash
curl -fsSL https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
```
Instala o `nvm`, que permite ter várias versões de Node lado a lado, sem `sudo`.

```bash
source ~/.bashrc && nvm install --lts && node --version
# esperado nesta máquina: v24.18.0
```

### 2.12 Instalação em um comando (tudo do essencial)

```bash
sudo apt update && sudo apt install -y \
  openssl ca-certificates curl python3 python3-venv python3-pip \
  mkcert libnss3-tools nginx nmap
```

---

## 3. Linux — Fedora/RHEL/Rocky

> Testado conceitualmente em Fedora 42 e Rocky Linux 9. Substitua `dnf` por `yum` em RHEL 7 (mas RHEL 7 saiu de suporte em 30/06/2024 — migre).

```bash
sudo dnf install -y openssl ca-certificates curl python3 python3-pip nginx nmap
```
Mesmo conjunto essencial. Repare que aqui o pacote das raízes também se chama `ca-certificates`.

```bash
openssl version
# esperado no Fedora 42: OpenSSL 3.2.x ou 3.5.x
```

**mkcert no Fedora:**

```bash
sudo dnf install -y mkcert nss-tools
mkcert -install && mkcert -version   # esperado: v1.4.4
```

**certbot:**

```bash
sudo dnf install -y certbot python3-certbot-nginx
certbot --version
```

**Caddy:**

```bash
sudo dnf install -y 'dnf-command(copr)'
sudo dnf copr enable -y @caddy/caddy
sudo dnf install -y caddy
caddy version
```

**Wireshark:**

```bash
sudo dnf install -y wireshark wireshark-cli
sudo usermod -aG wireshark "$USER"   # relogue depois
```

**Diferença que morde:** RHEL e Fedora têm **política criptográfica de sistema**
(`update-crypto-policies`). Ela sobrepõe a configuração das aplicações. Se o seu
nginx "ignora" a cifra que você configurou, é isto:

```bash
update-crypto-policies --show
# esperado: DEFAULT  (outras: LEGACY, FUTURE, FIPS)
```

```bash
sudo update-crypto-policies --set DEFAULT:NO-SHA1
```
Endurece a política do sistema inteiro sem editar cada aplicação. Aplique com cuidado e reinicie os serviços.

---

## 4. macOS (Intel e Apple Silicon)

> Testado conceitualmente em macOS 15 (Sequoia) e macOS 26. A diferença entre
> Intel e Apple Silicon aparece no **prefixo do Homebrew** — e ela quebra o PATH
> de muita gente.

### 4.1 A pegadinha do OpenSSL do macOS

```bash
openssl version
# saída típica em macOS: LibreSSL 3.3.6
```

**Isso não é OpenSSL.** É o **LibreSSL**, um fork feito pelo projeto OpenBSD depois
do Heartbleed (2014). A Apple o envia por questões de licença. Ele é competente, mas
**não aceita várias opções que este curso usa** (`-groups` com nomes novos, `-provider`,
alguns formatos), e sua versão é atrasada. Instale o OpenSSL de verdade ao lado.

### 4.2 Homebrew

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```
Instala o Homebrew, o gerenciador de pacotes de facto do macOS.

```bash
brew --version
# esperado: Homebrew 4.x
which brew
# Apple Silicon (M1/M2/M3/M4): /opt/homebrew/bin/brew
# Intel:                       /usr/local/bin/brew
```

Se `brew` não for encontrado depois de instalar, é o PATH — veja [§7](#7-path-e-variáveis-de-ambiente).

### 4.3 OpenSSL de verdade

```bash
brew install openssl@3
```

```bash
$(brew --prefix openssl@3)/bin/openssl version
# esperado: OpenSSL 3.5.x  (a fórmula openssl@3 acompanha a linha LTS)
```

O Homebrew **de propósito** não põe esse `openssl` no PATH (para não quebrar
programas do sistema que esperam o LibreSSL). Para usar o novo por padrão:

```bash
echo 'export PATH="$(brew --prefix openssl@3)/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
openssl version   # esperado agora: OpenSSL 3.5.x
```

> Em macOS o shell padrão é o **zsh** desde o Catalina (2019); use `~/.zshrc`.
> Se seu shell for bash (`echo $SHELL`), use `~/.bash_profile`.

### 4.4 O resto

```bash
brew install curl mkcert nss nginx caddy certbot nmap wireshark
```
`nss` é o equivalente do `libnss3-tools`, necessário para o mkcert mexer no Firefox.

```bash
mkcert -install
# esperado: pede sua senha de administrador e diz "The local CA is now installed in the system trust store!"
```

```bash
mkcert -version && caddy version && nginx -v && certbot --version
```

**curl no macOS:** o `curl` do sistema usa o **Secure Transport/LibreSSL** da Apple
e lê as raízes do **Chaveiro (Keychain)**, não de um arquivo `.pem`. O `curl` do brew
usa OpenSSL e um arquivo. Isso explica por que "funciona no Safari e falha no curl":
são repositórios de confiança diferentes.

### 4.5 Onde ficam as raízes no macOS

Abra o app **Acesso às Chaves** (ou, no macOS 15+, **Ajustes do Sistema → Geral →
Perfis e Certificados**) e veja *Sistema → Certificados*. Para listar por terminal:

```bash
security find-certificate -a -p /System/Library/Keychains/SystemRootCertificates.keychain | grep -c "BEGIN CERTIFICATE"
# esperado: um número entre ~140 e ~180
```

---

## 5. Windows — nativo e WSL2

### 5.1 Qual caminho escolher

| Caminho | Quando usar | Recomendação |
|---|---|---|
| **WSL2** (Ubuntu dentro do Windows) | você quer aprender TLS, seguir este curso, usar as mesmas ferramentas de servidor | ✅ **recomendado** |
| **Windows nativo** | você administra IIS, Active Directory Certificate Services, ou precisa mexer no repositório de certificados do Windows | use junto, não em vez |

**Por que WSL2 é o recomendado:** 95% da documentação, dos scripts e dos servidores
de TLS do mundo são Unix. No WSL2 você segue a [§2](#2-linux--debianubuntu) literalmente,
sem tradução. Fazer TLS "à moda Windows" te obriga a traduzir tudo, e a maioria dos
erros que você vai encontrar na internet não terá resposta para o seu caso.

### 5.2 Instalar o WSL2

No **PowerShell como Administrador**:

```powershell
wsl --install -d Ubuntu-24.04
```
Instala o subsistema Linux e a distribuição Ubuntu 24.04 numa tacada.

Reinicie quando pedido. Na primeira abertura, crie usuário e senha do Linux.

```powershell
wsl --status
# esperado: "Default Version: 2"
wsl --list --verbose
# esperado: Ubuntu-24.04  Running  2
```

Se aparecer `Default Version: 1`, corrija — WSL1 não tem rede de verdade e vai te atrapalhar:

```powershell
wsl --set-default-version 2
wsl --set-version Ubuntu-24.04 2
```

Dentro do Ubuntu, siga a [§2](#2-linux--debianubuntu) inteira.

### 5.3 Windows nativo — as ferramentas

**Gerenciador de pacotes:** o `winget` já vem no Windows 11 e no 10 atualizado.

```powershell
winget --version
# esperado: v1.x
```

```powershell
winget install --id ShiningLight.OpenSSL.Light -e
```
Instala a distribuição Win32/Win64 OpenSSL do Shining Light Productions — o *build* oficioso de facto para Windows.

```powershell
winget install --id FiloSottile.mkcert -e
winget install --id WiresharkFoundation.Wireshark -e
winget install --id Python.Python.3.12 -e
```

O `curl` já vem no Windows 10 1803+ (é `curl.exe`, não o alias do PowerShell):

```powershell
curl.exe --version
# esperado: curl 8.x ... (Schannel)  <- no Windows ele usa Schannel, a pilha TLS da Microsoft
```

> Atenção: no PowerShell, `curl` **sem `.exe`** é um apelido para `Invoke-WebRequest`,
> que tem opções completamente diferentes. **Sempre digite `curl.exe`** ao seguir
> este curso no Windows nativo. É a causa nº 1 de "o comando do tutorial não funciona".

**Verificação do OpenSSL no Windows:**

```powershell
& "C:\Program Files\OpenSSL-Win64\bin\openssl.exe" version
# esperado: OpenSSL 3.5.x
```

Se `openssl` sozinho não funcionar, adicione ao PATH ([§7](#7-path-e-variáveis-de-ambiente)).

### 5.4 O repositório de certificados do Windows

O Windows não usa arquivo `.pem`; usa uma base própria. Para abri-la:

```powershell
certlm.msc     # certificados da MÁQUINA (afeta todos os usuários e serviços)
certmgr.msc    # certificados do USUÁRIO atual
```

Listar as raízes por linha de comando:

```powershell
Get-ChildItem Cert:\LocalMachine\Root | Measure-Object
# esperado: Count com algumas dezenas a ~100 (o Windows baixa raízes sob demanda)
```

> **Peculiaridade real do Windows:** ele não instala todas as raízes de antemão —
> baixa a raiz necessária na hora, pelo Windows Update. Numa máquina sem internet
> ou com Windows Update bloqueado, cadeias válidas falham. Esse é um bug clássico
> de servidor Windows isolado, e leva horas para ser diagnosticado.

**mkcert no Windows nativo** instala a raiz no repositório do Windows (serve para
Edge, Chrome e IE) mas o **Firefox tem repositório próprio** — o mkcert cuida disso
se encontrar o Firefox instalado.

### 5.5 Chocolatey (alternativa ao winget)

```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force; `
  [System.Net.ServicePointManager]::SecurityProtocol = 3072; `
  iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
choco install openssl mkcert wireshark -y
```

Use **um** dos dois gerenciadores, não os dois para o mesmo programa — duas cópias
no PATH é fonte garantida de confusão sobre "qual openssl eu estou rodando".

---

## 6. Docker — o caminho universal

Se você quer OpenSSL 3.5 com pós-quântico, ou nginx recém-saído do forno, sem tocar
na sua máquina, use container.

```bash
docker --version
# esperado nesta máquina: Docker version 29.7.2, build a7dcaa6
```

### 6.1 Um OpenSSL moderno descartável

```bash
docker run --rm -it alpine:3.22 sh -c "apk add --no-cache openssl && openssl version"
```
Sobe um Alpine temporário, instala o OpenSSL e mostra a versão. O `--rm` apaga tudo ao sair.

```
# esperado: OpenSSL 3.5.x  (o Alpine 3.22 acompanha a linha 3.5 LTS)
```

### 6.2 Testar pós-quântico (exige OpenSSL 3.5+)

```bash
docker run --rm -it alpine:3.22 sh -c \
  "apk add --no-cache openssl && openssl list -kem-algorithms | grep -i mlkem"
# esperado: linhas com ML-KEM-512 / ML-KEM-768 / ML-KEM-1024
```

### 6.3 Um nginx com TLS em 30 segundos

```bash
mkdir -p /tmp/tlslab && cd /tmp/tlslab
openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem -days 1 -nodes -subj "/CN=localhost"
```
Gera um par de chaves e um certificado autoassinado válido por 1 dia, sem senha (`-nodes`).

```bash
cat > nginx.conf <<'CONF'
events {}
http {
  server {
    listen 443 ssl;
    ssl_certificate     /etc/nginx/cert.pem;
    ssl_certificate_key /etc/nginx/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    location / { return 200 "TLS ok\n"; }
  }
}
CONF
docker run --rm -d --name tlslab -p 8443:443 \
  -v /tmp/tlslab/nginx.conf:/etc/nginx/nginx.conf:ro \
  -v /tmp/tlslab/cert.pem:/etc/nginx/cert.pem:ro \
  -v /tmp/tlslab/key.pem:/etc/nginx/key.pem:ro \
  nginx:alpine
```

```bash
curl -k https://localhost:8443/
# esperado: TLS ok
# (-k desliga a verificação, porque o certificado é autoassinado — nunca use -k em produção)
```

```bash
docker rm -f tlslab   # limpa
```

### 6.4 Docker em ambiente restrito

Se `docker` der `permission denied while trying to connect to the Docker daemon socket`,
seu usuário não está no grupo `docker`:

```bash
sudo usermod -aG docker "$USER"   # e faça logout/login
```

Se o daemon simplesmente não estiver acessível na sua máquina, use `podman` (compatível
em linha de comando, roda sem daemon e sem root):

```bash
sudo apt install -y podman
podman run --rm -it alpine:3.22 sh -c "apk add --no-cache openssl && openssl version"
```

---

## 7. PATH e variáveis de ambiente

### 7.1 O conceito, em uma frase

`PATH` é a lista ordenada de pastas onde o shell procura um programa quando você
digita o nome dele. **A primeira que casar vence.** Se você tem dois `openssl`
instalados, quem manda é a ordem do PATH — não o que você "quis instalar".

### 7.2 Descobrir qual binário está sendo usado

```bash
which -a openssl      # Linux/macOS: lista TODOS os openssl no PATH, em ordem
echo "$PATH" | tr ':' '\n'   # mostra o PATH, uma pasta por linha
```

```powershell
where.exe openssl     # Windows: mesma ideia
$env:Path -split ';'
```

Se `which -a openssl` listar dois caminhos, o de cima é o que roda. Esse comando
resolve sozinho um terço das perguntas "por que meu comando se comporta diferente do tutorial".

### 7.3 Onde colocar a alteração

| Shell / SO | Arquivo | Como recarregar |
|---|---|---|
| bash (Linux) | `~/.bashrc` | `source ~/.bashrc` ou reabrir o terminal |
| bash (macOS, sessão de login) | `~/.bash_profile` | `source ~/.bash_profile` |
| zsh (macOS padrão, Linux) | `~/.zshrc` | `source ~/.zshrc` |
| fish | `~/.config/fish/config.fish` | `source` no mesmo |
| PowerShell | `$PROFILE` (`notepad $PROFILE`) | reabrir o PowerShell |
| Windows GUI | Sistema → Variáveis de Ambiente | **reabrir todo terminal aberto** |

```bash
echo 'export PATH="/opt/openssl-3.5/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```
Põe uma pasta na frente da fila e recarrega o perfil na sessão atual.

> ### Por que "a mudança não pegou"
> Um processo recebe uma **cópia** das variáveis de ambiente quando é criado.
> Alterar `~/.bashrc` **não muda** o ambiente de terminais que já estavam abertos,
> nem de serviços já rodando, nem do VS Code que foi aberto antes. É preciso
> `source` (na sessão atual) ou reabrir o programa. No caso de serviço do systemd,
> é `sudo systemctl daemon-reload && sudo systemctl restart <serviço>`, porque o
> systemd nem lê seu `.bashrc`.

### 7.4 Variáveis de ambiente que o TLS realmente usa

| Variável | Quem lê | Para quê |
|---|---|---|
| `SSL_CERT_FILE` | OpenSSL, curl, Go, Ruby | arquivo único com as raízes confiáveis |
| `SSL_CERT_DIR` | OpenSSL, curl | diretório com raízes (uma por arquivo, com *hash link*) |
| `CURL_CA_BUNDLE` | curl | igual ao `SSL_CERT_FILE`, mas só para o curl |
| `REQUESTS_CA_BUNDLE` | Python `requests` | raízes para o `requests` |
| `NODE_EXTRA_CA_CERTS` | Node.js | **acrescenta** raízes às padrão (não substitui) |
| `SSLKEYLOGFILE` | navegadores, curl, Python | grava as chaves de sessão para o Wireshark decifrar — só em laboratório! |
| `OPENSSL_CONF` | OpenSSL | caminho do `openssl.cnf` a usar |

```bash
openssl version -d
# esperado: OPENSSLDIR: "/usr/lib/ssl"  <- onde o OpenSSL procura config e certs por padrão
```

```bash
python3 -c "import ssl; print(ssl.get_default_verify_paths())"
# mostra exatamente qual arquivo/diretório o Python está usando como âncora de confiança
```

---

## 8. Permissões — e onde `sudo` estraga tudo

### 8.1 A regra de ouro da chave privada

```bash
chmod 600 chave.pem            # só o dono lê e escreve
chown root:ssl-cert chave.pem  # padrão comum: grupo dedicado
chmod 640 chave.pem            # dono lê/escreve, grupo lê, mundo nada
```

**Por que isso importa de verdade, não por burocracia:** a chave privada é *a*
identidade do servidor. Quem a copia pode se passar pelo seu site para qualquer
pessoa cuja conexão ele consiga interceptar, e — se a cifra não tiver sigilo futuro —
pode decifrar tráfego gravado no passado. O certificado é público; a chave é
equivalente à sua identidade. Muitos programas (OpenSSH e alguns servidores)
**se recusam a iniciar** se a chave estiver com permissão frouxa, e essa recusa é uma
funcionalidade, não um bug.

Verificação:

```bash
ls -l /etc/ssl/private/ 2>/dev/null || ls -l /etc/letsencrypt/live/*/ 2>/dev/null
# esperado: chaves com -rw------- ou -rw-r----- e nunca -rw-rw-rw-
```

```bash
find /etc /home -name "*.key" -o -name "privkey*.pem" 2>/dev/null | xargs -r ls -l | awk '$1 ~ /r..r..r../ {print "PERIGOSO: " $0}'
# esperado: nenhuma saída
```

### 8.2 Onde `sudo` causa problema

| Prática comum | Por que dá errado |
|---|---|
| `sudo npm install -g` | scripts de instalação de pacotes rodam como root; um pacote malicioso ganha a máquina inteira. Além disso, os arquivos ficam de root e depois o `npm` do seu usuário não consegue atualizá-los. **Use `nvm`**, que instala tudo no seu `$HOME` sem root. |
| `sudo pip install` | mistura pacotes do Python do sistema (gerenciado pelo `apt`) com pacotes do `pip`. O `apt` e o `pip` sobrescrevem um ao outro e você quebra ferramentas do próprio sistema (no Ubuntu 24.04+ o Python bloqueia isso com `externally-managed-environment`). **Use `python3 -m venv`.** |
| `sudo mkcert -install` | a CA é criada em `/root/.local/share/mkcert` e o *seu* usuário não a tem; seus certificados de usuário não são reconhecidos, ou pior, uma CA de root fica esquecida na máquina. **Rode mkcert sem sudo** (ele pede a senha só na hora de mexer no repositório do sistema). |
| `sudo openssl genrsa -out key.pem` | a chave nasce pertencendo a root; depois o serviço que roda como `www-data` não lê. |
| `chmod 777` na pasta de certificados | resolve o sintoma de hoje e entrega a chave privada para qualquer processo da máquina. |

### 8.3 Portas abaixo de 1024

Em Unix, só o root pode escutar nas portas 1–1023 (443 inclusive). Três saídas, em ordem de preferência:

```bash
sudo setcap 'cap_net_bind_service=+ep' /usr/bin/caddy
```
Concede **só** a capacidade de abrir porta baixa, sem dar root ao processo inteiro. É o caminho certo.

```bash
sudo systemctl edit meuapp   # e adicione: AmbientCapabilities=CAP_NET_BIND_SERVICE
```
Mesma coisa, feita pelo systemd — o serviço abre a 443 e continua rodando como usuário comum.

```bash
# Alternativa: rode em 8443 e redirecione com o firewall
sudo iptables -t nat -A PREROUTING -p tcp --dport 443 -j REDIRECT --to-port 8443
```

Nos laboratórios deste curso usamos **8443** justamente para não precisar de nada disso.

---

## 9. Rede corporativa: proxy e certificado interno

Se você está numa empresa, provavelmente há um dispositivo que **intercepta e
reassina todo o seu TLS** (chamam de *TLS inspection*, *SSL bump* ou *break and
inspect*). Na prática, a empresa instalou uma CA própria na sua máquina e faz um
ataque de intermediário autorizado. Isso muda várias coisas neste curso.

### 9.1 Sintomas

```
curl: (60) SSL certificate problem: unable to get local issuer certificate
SSL: CERTIFICATE_VERIFY_FAILED certificate verify failed: unable to get local issuer certificate
Error: self-signed certificate in certificate chain
x509: certificate signed by unknown authority
```

E, revelador: o certificado de `google.com` aparece emitido por "Zscaler", "Netskope",
"Blue Coat", "Fortinet" ou pelo nome da sua empresa.

Confirme:

```bash
echo | openssl s_client -connect example.com:443 2>/dev/null | openssl x509 -noout -issuer
# em rede limpa:      issuer=C=US, O=DigiCert Inc, CN=DigiCert Global G3 TLS ECC SHA384 2020 CA1
# em rede com bump:   issuer=... CN=Zscaler Root CA  (ou o nome da sua empresa)
```

### 9.2 Instalar a CA da empresa (Linux/Debian)

```bash
sudo cp empresa-root.crt /usr/local/share/ca-certificates/empresa-root.crt
```
O arquivo precisa estar em PEM e ter extensão **`.crt`** — com `.pem` o `update-ca-certificates` ignora silenciosamente.

```bash
sudo update-ca-certificates
# esperado: "1 added, 0 removed; done."
```

```bash
curl -sI https://example.com | head -1
# esperado: HTTP/2 200   (sem erro de certificado)
```

**Fedora/RHEL:**

```bash
sudo cp empresa-root.crt /etc/pki/ca-trust/source/anchors/
sudo update-ca-trust extract
```

**macOS:**

```bash
sudo security add-trusted-cert -d -r trustRoot -k /Library/Keychains/System.keychain empresa-root.crt
```

**Windows:**

```powershell
Import-Certificate -FilePath .\empresa-root.crt -CertStoreLocation Cert:\LocalMachine\Root
```

### 9.3 Cada runtime tem seu próprio repositório

Instalar no sistema **não basta**. Estas ferramentas ignoram o repositório do sistema:

```bash
export NODE_EXTRA_CA_CERTS=/usr/local/share/ca-certificates/empresa-root.crt   # Node.js
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt                   # Python requests
export SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt                        # Go, Ruby, OpenSSL
pip config set global.cert /etc/ssl/certs/ca-certificates.crt                  # pip
npm config set cafile /usr/local/share/ca-certificates/empresa-root.crt        # npm
git config --global http.sslCAInfo /etc/ssl/certs/ca-certificates.crt          # git
```

Java tem repositório separado (`cacerts`), em formato próprio:

```bash
sudo keytool -importcert -alias empresa -file empresa-root.crt \
  -keystore "$JAVA_HOME/lib/security/cacerts" -storepass changeit -noprompt
```

### 9.4 Proxy

```bash
export http_proxy="http://proxy.empresa.com:8080"
export https_proxy="http://proxy.empresa.com:8080"
export no_proxy="localhost,127.0.0.1,::1,.empresa.com"
```

> ⚠️ **Armadilha frequente:** um `no_proxy` malformado (com espaços, com `http://`,
> ou com faixas CIDR — que a maioria dos clientes **não** entende) faz bibliotecas
> Python tentarem falar com `localhost` **através do proxy**, e seus laboratórios locais
> falham com erros incompreensíveis. Se seus testes em `127.0.0.1` derem timeout,
> desconfie do `no_proxy` antes de qualquer outra coisa. Teste com `env -u http_proxy -u https_proxy curl ...`.

### 9.5 O que **nunca** fazer

```bash
export PYTHONHTTPSVERIFY=0        # ❌
export NODE_TLS_REJECT_UNAUTHORIZED=0  # ❌
git config --global http.sslVerify false  # ❌
alias curl='curl -k'              # ❌❌
```

Isso não "resolve o proxy": desliga a verificação de identidade globalmente e para
sempre, na sua máquina, inclusive fora da rede da empresa. Você troca um erro visível
por uma vulnerabilidade invisível. Se precisar desligar, faça **por comando** e nunca
no perfil do shell.

---

## 10. Convivência de versões do OpenSSL

Você vai precisar disso quando quiser ML-KEM (3.5+) numa distro com 3.0, ou quando
tiver de reproduzir um bug de um sistema antigo.

### 10.1 A regra que evita o desastre

> **Nunca substitua o OpenSSL do sistema.** `apt`, `ssh`, `wget`, `python3`, `systemd`
> e mais uma centena de binários estão ligados dinamicamente à `libssl.so` do sistema.
> Trocá-la por outra versão de ABI diferente transforma sua máquina em um tijolo que
> não consegue nem baixar o pacote para se consertar.

Instale **ao lado**, em `/opt` ou `/usr/local`.

### 10.2 Compilar uma segunda versão (Linux)

```bash
sudo apt install -y build-essential perl wget
```
Compilador, `make` e o Perl que o sistema de build do OpenSSL exige.

```bash
cd /tmp && wget https://github.com/openssl/openssl/releases/download/openssl-3.5.7/openssl-3.5.7.tar.gz
tar xzf openssl-3.5.7.tar.gz && cd openssl-3.5.7
```
Baixa e extrai a linha **3.5 LTS** (suporte anunciado até 08/04/2030).

```bash
./Configure --prefix=/opt/openssl-3.5 --openssldir=/opt/openssl-3.5/ssl shared
```
`--prefix` é o que garante que nada toque no sistema.

```bash
make -j"$(nproc)" && sudo make install_sw install_ssldirs
```
`install_sw` instala binários e bibliotecas sem a documentação (economiza minutos).

```bash
/opt/openssl-3.5/bin/openssl version
# esperado: OpenSSL 3.5.7 ...
/opt/openssl-3.5/bin/openssl list -kem-algorithms | grep -i mlkem
# esperado: ML-KEM-512, ML-KEM-768, ML-KEM-1024
```

Use com um apelido, sem tocar no PATH global:

```bash
echo "alias openssl35='/opt/openssl-3.5/bin/openssl'" >> ~/.bashrc && source ~/.bashrc
openssl35 version
```

### 10.3 Python com um OpenSSL específico (pyenv)

```bash
curl -fsSL https://pyenv.run | bash
export CONFIGURE_OPTS="--with-openssl=/opt/openssl-3.5"
export LD_RUN_PATH="/opt/openssl-3.5/lib64"
pyenv install 3.13.5
pyenv local 3.13.5
python -c "import ssl; print(ssl.OPENSSL_VERSION)"
# esperado: OpenSSL 3.5.7
```

### 10.4 Descobrir contra qual biblioteca um binário está ligado

```bash
ldd "$(which curl)" | grep -E "ssl|crypto|gnutls|nss"
# esperado (Ubuntu): libssl.so.3 => /lib/x86_64-linux-gnu/libssl.so.3
```

```bash
otool -L "$(which curl)" | grep -iE "ssl|crypto"    # macOS
```

Este comando responde de vez a pergunta "por que o `openssl s_client` aceita e o
`curl` recusa": são pilhas de TLS diferentes.

---

## 11. Reprodutibilidade

Ambiente de TLS que "funciona na minha máquina" é epidemia. Fixe tudo:

| O que fixar | Como |
|---|---|
| versão do Python | `.python-version` (pyenv) ou `.tool-versions` (mise/asdf) |
| versão do Node | `.nvmrc` com `v24.18.0` |
| dependências Python | `requirements.txt` com `==`, ou `uv.lock`/`poetry.lock` |
| dependências Node | `package-lock.json` versionado; instale com `npm ci`, não `npm install` |
| toda a pilha | uma imagem de container com **digest fixado**, não só tag |

```bash
cat > .tool-versions <<'TOOLS'
python 3.13.5
nodejs 24.18.0
TOOLS
```
Um arquivo lido tanto pelo `asdf` quanto pelo `mise` — quem clonar o repositório pega as mesmas versões.

```dockerfile
# Fixar por digest é o que torna a build realmente reprodutível:
FROM nginx:1.30-alpine@sha256:<digest>
```

**E os certificados?** Nunca coloque certificado ou chave em imagem de container.
Monte por volume ou injete por segredo — veja
[variaveis-de-ambiente-e-segredos](../variaveis-de-ambiente-e-segredos/00-MAPA.md).

---

## 12. Atualizar e voltar atrás

```bash
sudo apt update && sudo apt install --only-upgrade openssl libssl3 ca-certificates
```
Atualiza só o que interessa, sem arrastar o sistema inteiro.

```bash
openssl version   # confirme que subiu
```

**Depois de atualizar `libssl`, reinicie o que usa TLS** — processos em execução
continuam com a biblioteca velha carregada na memória. É por isso que servidores
"corrigidos" continuam vulneráveis:

```bash
sudo apt install -y needrestart && sudo needrestart -r l
# lista os serviços que ainda usam bibliotecas antigas e pede para reiniciar
```

**Voltar a uma versão anterior (Debian/Ubuntu):**

```bash
apt list -a libssl3          # mostra as versões disponíveis
sudo apt install libssl3=3.0.2-0ubuntu1.15
sudo apt-mark hold libssl3   # impede que uma atualização automática desfaça
```

`apt-mark unhold libssl3` libera de volta. **Voltar versão de biblioteca de
criptografia quase sempre significa reintroduzir uma vulnerabilidade corrigida** —
faça só para diagnosticar, e reverta.

---

## 13. Desinstalar por completo

O que fica para trás depois de um `apt remove` é justamente o que causa confusão
seis meses depois.

```bash
sudo apt purge -y nginx certbot mkcert wireshark && sudo apt autoremove -y
```
`purge` (diferente de `remove`) apaga também os arquivos de configuração.

**Resíduos a limpar à mão:**

```bash
# mkcert: a CA local — IMPORTANTE, senão fica uma raiz confiável órfã na sua máquina
mkcert -uninstall          # remove a raiz do repositório do sistema e dos navegadores
rm -rf "$(mkcert -CAROOT)" # apaga a chave e o certificado da CA

# certbot / Let's Encrypt
sudo rm -rf /etc/letsencrypt /var/lib/letsencrypt /var/log/letsencrypt
sudo rm -f /etc/cron.d/certbot
sudo systemctl disable --now certbot.timer 2>/dev/null

# nginx
sudo rm -rf /etc/nginx /var/log/nginx /var/cache/nginx

# CA corporativa que você adicionou
sudo rm -f /usr/local/share/ca-certificates/empresa-root.crt && sudo update-ca-certificates --fresh

# caches e configs de usuário
rm -rf ~/.testssl ~/testssl.sh ~/.rnd
```

**Verificação de que não sobrou raiz estranha confiável na máquina** — vale rodar
mesmo sem desinstalar nada:

```bash
awk -v cmd='openssl x509 -noout -subject' '/BEGIN/{close(cmd)};{print | cmd}' /etc/ssl/certs/ca-certificates.crt | sort | grep -iE "mkcert|zscaler|empresa|burp|fiddler|mitmproxy"
# esperado após a limpeza: nenhuma saída
```

macOS:

```bash
brew uninstall openssl@3 mkcert nginx caddy certbot
sudo security delete-certificate -c "mkcert development CA" /Library/Keychains/System.keychain
```

Windows:

```powershell
winget uninstall ShiningLight.OpenSSL.Light
Get-ChildItem Cert:\LocalMachine\Root | Where-Object Subject -like "*mkcert*" | Remove-Item
```

---

## 14. Solução de problemas — erros literais

| Mensagem | Causa provável | Correção |
|---|---|---|
| `command not found: openssl` | binário não está no PATH, ou não foi instalado | `which -a openssl`; instale (§2–§5) ou ajuste o PATH (§7) |
| `curl: (60) SSL certificate problem: unable to get local issuer certificate` | falta a CA raiz — proxy corporativo, ou servidor não envia os intermediários | instale a CA da empresa (§9.2); ou conserte a cadeia do servidor (`openssl s_client -showcerts`) |
| `curl: (60) SSL: no alternative certificate subject name matches target host name` | o certificado é válido, mas para **outro** nome | confira o SAN: `openssl x509 -noout -text -in cert.pem \| grep -A1 "Subject Alternative Name"` |
| `curl: (35) error:0A000102:SSL routines::unsupported protocol` | o servidor só fala TLS 1.0/1.1 e seu OpenSSL 3.x os desabilitou por padrão | é o servidor que está errado; para diagnosticar: `curl --tlsv1.2 --ciphers DEFAULT@SECLEVEL=0 ...` |
| `SSL routines::sslv3 alert handshake failure` | nenhuma cifra/curva em comum, ou o servidor exige certificado de cliente | `openssl s_client -connect host:443 -tls1_2 -cipher ALL` para isolar; veja se é mTLS |
| `error:0308010C:digital envelope routines::unsupported` | Node 17+ com OpenSSL 3 recusando algoritmo legado (MD4 em webpack antigo) | atualize a dependência; paliativo: `export NODE_OPTIONS=--openssl-legacy-provider` |
| `ssl.SSLCertVerificationError: [SSL: CERTIFICATE_VERIFY_FAILED] unable to get local issuer certificate` (Python/macOS) | o Python do python.org não usa o Chaveiro | rode `/Applications/Python\ 3.x/Install\ Certificates.command` |
| `EACCES: permission denied, open '/etc/ssl/private/key.pem'` | processo não-root tentando ler chave de root | ajuste dono/grupo (§8.1), não use `chmod 777` |
| `bind() to 0.0.0.0:443 failed (13: Permission denied)` | porta < 1024 sem privilégio | `setcap` ou `AmbientCapabilities` (§8.3), ou use 8443 |
| `nginx: [emerg] cannot load certificate "/etc/nginx/cert.pem": PEM routines::no start line` | arquivo em DER, ou é a chave onde devia ser o certificado, ou está truncado | `openssl x509 -in cert.pem -noout -text`; converta com `openssl x509 -inform der -in c.der -out c.pem` |
| `nginx: [emerg] SSL_CTX_use_PrivateKey_file(...) key values mismatch` | a chave não é a do certificado | compare os módulos: `openssl x509 -noout -modulus -in cert.pem \| openssl md5` vs `openssl rsa -noout -modulus -in key.pem \| openssl md5` — têm de ser idênticos |
| `x509: certificate signed by unknown authority` (Go/Docker) | idem ao curl 60, em runtime Go | `SSL_CERT_FILE`, ou `/etc/docker/certs.d/<registry>/ca.crt` para o Docker |
| `certbot: Timeout during connect (likely firewall problem)` | o desafio HTTP-01 exige a porta **80** aberta para a internet | libere a 80, ou use o desafio **DNS-01** |
| `Error creating new order :: too many certificates already issued for` | limite de emissão do Let's Encrypt (50 certificados por domínio registrado por semana) | use `--staging` para testar; espere a janela |
| `wireshark: There are no interfaces on which a capture can be done` | usuário fora do grupo `wireshark`, ou grupo ainda não aplicado | `sudo usermod -aG wireshark $USER` **e faça logout/login** |
| `E: Unable to locate package mkcert` | distro antiga | instale o binário direto (§2.5) |
| `externally-managed-environment` (pip) | Python 3.12+/Ubuntu 24.04 protegendo os pacotes do sistema | `python3 -m venv .venv && source .venv/bin/activate` |

---

## 15. Checklist "ambiente pronto"

Rode tudo. Cada linha deve produzir a saída indicada antes de você ir para o
[04-como-comecar.md](04-como-comecar.md).

```bash
openssl version                                   # OpenSSL 3.x
curl --version | head -1                          # curl 7.7x+ ou 8.x
python3 -c "import ssl; print(ssl.HAS_TLSv1_3)"   # True
mkcert -version                                   # v1.4.4 (se instalou)
mkcert -CAROOT                                    # um caminho existente
openssl s_client -connect example.com:443 -brief </dev/null 2>&1 | grep Verification   # Verification: OK
curl -sI https://example.com | head -1            # HTTP/2 200
echo | openssl s_client -connect example.com:443 2>/dev/null | openssl x509 -noout -dates  # notBefore/notAfter
openssl ciphers -v 'TLS_AES_256_GCM_SHA384'       # TLSv1.3 Kx=any Au=any Enc=AESGCM(256) Mac=AEAD
```

Bônus — confirme que você consegue **falhar** corretamente (isto deve dar erro, e é o esperado):

```bash
curl https://expired.badssl.com/
# esperado: curl: (60) SSL certificate problem: certificate has expired
curl https://wrong.host.badssl.com/
# esperado: curl: (60) SSL: no alternative certificate subject name matches target host name
curl https://self-signed.badssl.com/
# esperado: curl: (60) SSL certificate problem: self-signed certificate
```

Se esses três **passaram** sem erro, sua verificação de certificado está desligada
em algum lugar (alias com `-k`, `CURL_CA_BUNDLE` apontando para lugar errado, ou
um MITM corporativo). Investigue antes de seguir — um ambiente que aceita tudo não
ensina nada.

---

## Fontes consultadas

- OpenSSL Library — política de releases e linha 3.5 LTS: <https://openssl-library.org/policies/releasestrat/> e <https://openssl-library.org/post/2025-02-20-openssl-3.5-lts/> (consulta: 31/08/2026)
- Releases do OpenSSL: <https://github.com/openssl/openssl/releases> (consulta: 31/08/2026)
- Let's Encrypt — certificados de 6 dias e de IP: <https://letsencrypt.org/2026/01/15/6day-and-ip-general-availability> (consulta: 31/08/2026)
- Documentação do mkcert: <https://github.com/FiloSottile/mkcert>
- Documentação do Caddy: <https://caddyserver.com/docs/install>
- Documentação do certbot: <https://certbot.eff.org/>
- testssl.sh: <https://github.com/testssl/testssl.sh>
- Versões locais conferidas por comando nesta máquina em 31/08/2026 (Ubuntu 22.04.5 LTS).

> Versões de terceiros citadas sem verificação local (nginx 1.30.x, Caddy 2.11.x,
> certbot 5.x, OpenSSL 3.5.7/4.0.x) vêm de fontes da web na data acima e podem ter
> avançado. **Sempre confira com o comando de versão** — o manual ensina o comando
> justamente para você não depender do número escrito aqui.

---

**Próximo:** [04-como-comecar.md](04-como-comecar.md) — do ambiente pronto ao primeiro HTTPS.
