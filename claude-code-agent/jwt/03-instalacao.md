# 3 · Manual de instalação

> Nível: iniciante · **Versões e comandos pesquisados na web em 14/08/2026** ·
> Testado em Ubuntu 22.04.5, Node v24.18.0, Python 3.10.12, OpenSSL 3.0.2, OpenJDK 17.0.19

Este é o arquivo mais chato do material e o que mais salva iniciante. Ele é escrito
como manual de campo: siga sem improvisar, sem consultar outra fonte.

**Comece pela seção 0.** Talvez você não precise instalar nada hoje.

---

## Índice

- [0 · Sem instalar nada](#0--sem-instalar-nada)
- [1 · O que exatamente precisa ser instalado](#1--o-que-exatamente-precisa-ser-instalado)
- [2 · OpenSSL](#2--openssl-todos-os-sistemas)
- [3 · Node.js](#3--nodejs)
- [4 · Bibliotecas JavaScript](#4--bibliotecas-javascript-jose-e-companhia)
- [5 · Python e PyJWT](#5--python-e-pyjwt)
- [6 · Java e JJWT](#6--java-e-jjwt)
- [7 · Go](#7--go)
- [8 · jwt-cli](#8--jwt-cli-inspecionar-tokens-no-terminal)
- [9 · Editor](#9--editor-e-extensões)
- [10 · Docker](#10--docker-o-caminho-que-não-suja-a-máquina)
- [11 · PATH e variáveis de ambiente](#11--path-e-variáveis-de-ambiente)
- [12 · Permissões: o `sudo` que quebra tudo](#12--permissões-o-sudo-que-quebra-tudo)
- [13 · Rede corporativa](#13--rede-corporativa-proxy-e-certificado-interno)
- [14 · Conviver com várias versões](#14--conviver-com-várias-versões)
- [15 · Reprodutibilidade](#15--reprodutibilidade)
- [16 · Atualizar e voltar atrás](#16--atualizar-e-voltar-atrás)
- [17 · Desinstalar por completo](#17--desinstalar-por-completo)
- [18 · Solução de problemas](#18--solução-de-problemas)
- [19 · Checklist "ambiente pronto"](#19--checklist-ambiente-pronto)

---

## 0 · Sem instalar nada

Três caminhos que funcionam **hoje**, no navegador. Comece por eles; instale depois,
quando souber que vai continuar.

### 0.1 · jwt.io — o inspetor de tokens

<https://jwt.io> · gratuito, sem cadastro.

Cole um token e ele mostra cabeçalho, payload e o estado da assinatura, colorindo os
três segmentos. É a ferramenta mais usada do ecossistema, mantida pela Auth0/Okta.

> **Cuidado real, não paranoia:** o site processa tudo no navegador (não envia o
> token para o servidor), mas **nunca cole um token de produção em site nenhum**. Um
> token é uma credencial viva. Colar um token de produção num site é o equivalente a
> colar sua senha. Use tokens de teste. Se precisar inspecionar um token real, use o
> `jwt-cli` da [seção 8](#8--jwt-cli-inspecionar-tokens-no-terminal), que roda offline.

### 0.2 · Um verificador em duas linhas, no console do navegador

Abra o console de qualquer aba (F12) e cole:

```js
const token = "eyJhbGciOiJFUzI1NiIsInR5cCI6ImF0K2p3dCJ9.eyJzdWIiOiI0MiIsImV4cCI6MTc4NjcyNjk3Nn0.QaTj";
JSON.parse(atob(token.split('.')[1].replace(/-/g,'+').replace(/_/g,'/')));
```

```
// esperado: { sub: "42", exp: 1786726976 }
```

Isso já demonstra o ponto central do assunto: **você acabou de ler o conteúdo de um
token sem nenhuma chave**.

### 0.3 · Playgrounds que rodam código

| Plataforma | O que dá para fazer | Link |
|---|---|---|
| **StackBlitz** | Node completo no navegador; `npm i jose` funciona | <https://stackblitz.com> |
| **GitHub Codespaces** | Ubuntu real com Node/Python já instalados. Gratuito até 60 h/mês em conta pessoal (consultado em 14/08/2026) | <https://github.com/codespaces> |
| **Google Colab** | Python; `!pip install pyjwt` funciona | <https://colab.research.google.com> |

---

## 1 · O que exatamente precisa ser instalado

Um manual que instala só a biblioteca principal e assume o resto não serve. A lista
completa, com o porquê de cada item:

| Tecnologia | Para quê | Obrigatório? |
|---|---|---|
| **OpenSSL** | gerar pares de chaves, inspecionar, converter formatos. Toda a criptografia do assunto passa por aqui. | **sim** |
| **Node.js ≥ 20** | rodar o [projeto-modelo](07-projeto-modelo/) e os exemplos | **sim** (para a trilha principal) |
| **`jose`** (npm) | a biblioteca JOSE recomendada em JavaScript | recomendado |
| **Python 3.9+ e PyJWT** | trilha alternativa dos exemplos | opcional |
| **JDK 17+ e JJWT** | trilha alternativa (Spring Boot) | opcional |
| **Go 1.21+** | trilha alternativa | opcional |
| **`jwt-cli`** | inspecionar tokens no terminal, offline | recomendado |
| **`curl`** | exercitar a API | **sim** |
| **`jq`** | ler as respostas JSON sem chorar | recomendado |
| **Editor + extensão REST** | rodar o `requisicoes.http` | opcional |
| **Docker** | alternativa a instalar qualquer coisa acima | opcional |

Conta em serviço externo: **nenhuma**. Cartão de crédito: **nenhum**.

---

## 2 · OpenSSL (todos os sistemas)

Provavelmente já está instalado. Confira primeiro.

```bash
openssl version
# esperado: OpenSSL 3.x.x  (qualquer 3.x serve; 1.1.1 ainda funciona para o material)
```

**Se a saída for diferente** — `command not found` ou versão 1.0.x — instale:

### Linux · Debian / Ubuntu

```bash
sudo apt update && sudo apt install -y openssl
```

### Linux · Fedora / RHEL / Rocky

```bash
sudo dnf install -y openssl
```

### macOS

O macOS traz LibreSSL sob o nome `openssl`, que **não** é a mesma coisa e não suporta
alguns comandos usados aqui. Instale o OpenSSL de verdade:

```bash
brew install openssl@3
```

```bash
# adicione ao PATH (Apple Silicon):
echo 'export PATH="/opt/homebrew/opt/openssl@3/bin:$PATH"' >> ~/.zshrc
# Intel:
echo 'export PATH="/usr/local/opt/openssl@3/bin:$PATH"' >> ~/.zshrc

exec zsh          # recarrega o shell — sem isso a mudança "não pega"
openssl version   # esperado: OpenSSL 3.x.x   (e NÃO "LibreSSL")
```

### Windows

**Caminho recomendado: WSL2.** Instale o Ubuntu e siga a seção Debian/Ubuntu.

```powershell
wsl --install -d Ubuntu-24.04
# reinicie quando pedido; depois abra "Ubuntu" no menu Iniciar
```

Por que WSL2 e não o Windows nativo: praticamente todo material de criptografia,
todo script de exemplo e toda documentação do ecossistema assume um shell POSIX. No
Windows nativo você passará mais tempo traduzindo comandos do que aprendendo JWT.

Se ainda assim precisar do Windows nativo:

```powershell
winget install --id FireDaemon.OpenSSL
# ou, se já tiver Git para Windows, o openssl dele serve:
# C:\Program Files\Git\usr\bin\openssl.exe
```

### Verificação que vale para todos

```bash
openssl ecparam -name prime256v1 -genkey -noout -out /tmp/teste-ec.pem && \
openssl ec -in /tmp/teste-ec.pem -pubout -out /tmp/teste-ec.pub && \
echo "OK: gerou par de chaves P-256" && rm /tmp/teste-ec.pem /tmp/teste-ec.pub
# esperado: (algumas linhas de log do openssl) e depois "OK: gerou par de chaves P-256"
```

---

## 3 · Node.js

**Versão mínima:** 18 (por causa do `fetch` nativo).
**Recomendada:** 24.x LTS. **Testado em: Node v24.18.0, em 14/08/2026.**
**Evite:** qualquer versão ímpar (19, 21, 23) — são linhas de vida curta, sem LTS.

### 3.1 · Escolha do método

| Método | Quando usar | Ressalva |
|---|---|---|
| **`nvm` / `fnm` / `mise`** | **recomendado** para desenvolvimento | precisa carregar no shell |
| Repositório NodeSource | servidor Linux, uma versão só | exige `sudo` |
| Instalador oficial (.pkg/.msi) | quem não quer linha de comando | trocar de versão é manual |
| `apt install nodejs` (Ubuntu padrão) | **evite** | o Ubuntu 22.04 entrega Node 12 — velho demais |
| Docker | não quer instalar nada | ver [seção 10](#10--docker-o-caminho-que-não-suja-a-máquina) |

### 3.2 · Linux e macOS — via `nvm` (recomendado)

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
```
> Baixa e executa o instalador do nvm, que se instala em `~/.nvm` e acrescenta três
> linhas ao seu arquivo de perfil. Nada disso pede `sudo` — e é justamente esse o
> ponto (ver [seção 12](#12--permissões-o-sudo-que-quebra-tudo)).

```bash
exec $SHELL          # recarrega o shell para o nvm existir
command -v nvm
# esperado: nvm
```

**Se a saída for vazia:** o instalador escreveu no arquivo de perfil errado. Descubra
qual o seu shell usa (`echo $SHELL`) e adicione à mão:

```bash
# em ~/.bashrc (bash) ou ~/.zshrc (zsh):
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
```

```bash
nvm install 24
nvm alias default 24
```
> Baixa o Node 24 LTS e o torna o padrão de novos terminais.

```bash
node --version
# esperado: v24.x.x (testado com v24.18.0)
npm --version
# esperado: 11.x.x ou superior
```

### 3.3 · Linux — via NodeSource (servidor)

```bash
curl -fsSL https://deb.nodesource.com/setup_24.x | sudo -E bash -
sudo apt install -y nodejs
```
> Adiciona o repositório oficial da NodeSource e instala o Node 24 em todo o sistema.

Fedora/RHEL:

```bash
curl -fsSL https://rpm.nodesource.com/setup_24.x | sudo bash -
sudo dnf install -y nodejs
```

```bash
node --version    # esperado: v24.x.x
```

### 3.4 · macOS — via Homebrew

```bash
brew install node@24
brew link --overwrite node@24
node --version    # esperado: v24.x.x
```

Apple Silicon vs. Intel: o Homebrew instala em `/opt/homebrew` no Apple Silicon e em
`/usr/local` no Intel. Se `node --version` não achar nada depois do `brew install`,
é isso — veja a [seção 11](#11--path-e-variáveis-de-ambiente).

### 3.5 · Windows

**Recomendado — WSL2:** abra o Ubuntu e siga a [seção 3.2](#32--linux-e-macos--via-nvm-recomendado).

**Windows nativo, com gerenciador de versões:**

```powershell
winget install Schniz.fnm
```
```powershell
# adicione ao seu Perfil do PowerShell:
notepad $PROFILE
# cole a linha:  fnm env --use-on-cd | Out-String | Invoke-Expression
```
```powershell
fnm install 24
fnm use 24
node --version
# esperado: v24.x.x
```

**Windows nativo, instalador oficial:** baixe o `.msi` em <https://nodejs.org>.
Marque "Automatically install the necessary tools" só se for compilar módulos
nativos — para este material, não precisa.

---

## 4 · Bibliotecas JavaScript: `jose` e companhia

> **O projeto-modelo deste curso não precisa de nenhuma delas** — ele implementa JWS
> do zero, de propósito. Instale-as para os exemplos do
> [arquivo 06](06-exemplos.md) e para escrever código de produção.

### 4.1 · Qual escolher

Pesquisado na web em 14/08/2026:

| Biblioteca | Versão atual | Downloads/semana | Veredito |
|---|---|---|---|
| **`jose`** | **6.2.8** | ~76,5 M | **Use esta.** Zero dependências, Web Crypto, roda em Node/Deno/Bun/browser/Cloudflare Workers, suporta JWS, JWE, JWK, JWKS remoto. Mantida por Filip Skokan, que também mantém as bibliotecas OAuth de referência. |
| `jsonwebtoken` | 9.0.3 | ~42,6 M | Legado. Só mantenha o que já existe; não comece projeto novo com ela. Cripto síncrona (bloqueia o *event loop*), sem ESM nativo, sem JWE, sem JWKS. |
| `fast-jwt` | — | — | Foco em desempenho. **Recebeu a CVE-2026-34950 (CVSS 9,1) em 06/04/2026**, uma reabertura da confusão de algoritmo por espaço em branco na chave. Atualize se usar. |

Opinião profissional, declarada como opinião: para código novo em JavaScript, `jose`
é a escolha certa e a discussão acaba aí. O `jsonwebtoken` sobrevive por inércia de
tutoriais antigos.

### 4.2 · Instalar

```bash
mkdir -p ~/laboratorio-jwt && cd ~/laboratorio-jwt
npm init -y
npm install jose
```
> Cria um projeto vazio e instala a `jose`. Repare que **não** há `sudo` — ver
> [seção 12](#12--permissões-o-sudo-que-quebra-tudo).

```bash
npm ls jose
# esperado:
# laboratorio-jwt@1.0.0 /home/voce/laboratorio-jwt
# └── jose@6.2.8
```

**Verificação real** (não só "instalou", mas "funciona"):

```bash
node --input-type=module -e "
import { SignJWT, jwtVerify, generateKeyPair } from 'jose';
const { privateKey, publicKey } = await generateKeyPair('ES256');
const t = await new SignJWT({ papel: 'admin' })
  .setProtectedHeader({ alg: 'ES256' })
  .setIssuer('https://teste').setAudience('api').setExpirationTime('5m')
  .sign(privateKey);
const { payload } = await jwtVerify(t, publicKey, { issuer: 'https://teste', audience: 'api' });
console.log('OK', payload.papel);
"
# esperado: OK admin
```

**Se der `ERR_MODULE_NOT_FOUND`:** você está fora da pasta `~/laboratorio-jwt`.
**Se der `SyntaxError: Cannot use import statement`:** faltou `--input-type=module`.

---

## 5 · Python e PyJWT

**Versão mínima do Python:** 3.9. **Testado em: Python 3.10.12, em 14/08/2026.**
**PyJWT atual: 2.13.0** (pesquisado na web em 14/08/2026).

> ⚠️ **Não use PyJWT abaixo de 2.13.0.** A **CVE-2026-48526** é uma falha crítica de
> confusão de algoritmo que atinge as versões anteriores, quando a aplicação valida
> tokens usando JWK cru e suporta famílias mistas de algoritmo. Corrigida em 2.13.0.

### 5.1 · Linux

```bash
sudo apt install -y python3 python3-pip python3-venv    # Debian/Ubuntu
sudo dnf install -y python3 python3-pip                 # Fedora/RHEL
python3 --version
# esperado: Python 3.10.x ou superior
```

### 5.2 · macOS

```bash
brew install python@3.12
python3 --version    # esperado: Python 3.12.x
```

### 5.3 · Windows

```powershell
winget install Python.Python.3.12
python --version     # esperado: Python 3.12.x
```

### 5.4 · Instalar PyJWT — sempre em ambiente virtual

```bash
cd ~/laboratorio-jwt
python3 -m venv .venv
```
> Cria um ambiente isolado em `.venv`. **Este passo não é opcional.** Instalar
> pacote Python com `sudo pip` no sistema quebra ferramentas do próprio SO que
> dependem do Python — em distribuições recentes o `pip` inclusive se recusa a fazer
> isso (`externally-managed-environment`), e está certo.

```bash
source .venv/bin/activate           # Linux/macOS
# .venv\Scripts\Activate.ps1        # Windows PowerShell
```

```bash
pip install "PyJWT[crypto]>=2.13.0"
```
> O extra `[crypto]` puxa a biblioteca `cryptography`, **sem a qual RS256, ES256 e
> EdDSA simplesmente não funcionam** — só HMAC. Esse é o erro nº 1 de quem usa PyJWT:
> instala `pip install pyjwt`, tenta RS256 e recebe
> `NotImplementedError: Algorithm not supported`.

```bash
python -c "import jwt; print(jwt.__version__)"
# esperado: 2.13.0 (ou superior)
```

**Verificação real:**

```bash
python - <<'PY'
import jwt, time
from cryptography.hazmat.primitives.asymmetric import ec
sk = ec.generate_private_key(ec.SECP256R1())
t = jwt.encode({"sub":"42","iss":"https://teste","aud":"api","exp":int(time.time())+300}, sk, algorithm="ES256")
print("OK", jwt.decode(t, sk.public_key(), algorithms=["ES256"], issuer="https://teste", audience="api")["sub"])
PY
# esperado: OK 42
```

---

## 6 · Java e JJWT

**JDK mínimo:** 8 para JJWT, 17 para Spring Boot 3.
**Testado em: OpenJDK 17.0.19, em 14/08/2026.**
**JJWT atual: 0.13.0** (último lançamento em 20/08/2025; pesquisado em 14/08/2026).

```bash
# Debian/Ubuntu
sudo apt install -y openjdk-17-jdk
# Fedora/RHEL
sudo dnf install -y java-17-openjdk-devel
# macOS
brew install openjdk@17
# Windows
winget install EclipseAdoptium.Temurin.17.JDK
```

```bash
java -version
# esperado: openjdk version "17.x.x"
```

Dependência Maven — **três artefatos, não um**:

```xml
<dependency>
  <groupId>io.jsonwebtoken</groupId><artifactId>jjwt-api</artifactId>
  <version>0.13.0</version>
</dependency>
<dependency>
  <groupId>io.jsonwebtoken</groupId><artifactId>jjwt-impl</artifactId>
  <version>0.13.0</version><scope>runtime</scope>
</dependency>
<dependency>
  <groupId>io.jsonwebtoken</groupId><artifactId>jjwt-jackson</artifactId>
  <version>0.13.0</version><scope>runtime</scope>
</dependency>
```

> O artefato monolítico `io.jsonwebtoken:jjwt` está **obsoleto**. A separação
> api/impl é deliberada: seu código compila só contra a interface, e a implementação
> entra em tempo de execução. Se você importar só `jjwt-api`, tudo compila e explode
> na primeira chamada com `Unable to discover any JWT implementations`.

Alternativa em Java: **Nimbus JOSE+JWT** (`com.nimbusds:nimbus-jose-jwt`), mais
completa em JOSE (JWE, JWK, ECDH) e a base do Spring Security OAuth2.

---

## 7 · Go

**Go mínimo:** 1.21. **`golang-jwt/jwt/v5`** — última publicação em 28/01/2026
(pesquisado em 14/08/2026).

```bash
# Linux
sudo apt install -y golang-go        # ou baixe de go.dev/dl para versão recente
# macOS
brew install go
# Windows
winget install GoLang.Go
```

```bash
go version
# esperado: go version go1.2x.x
```

```bash
mkdir -p ~/laboratorio-jwt-go && cd ~/laboratorio-jwt-go
go mod init laboratorio
go get github.com/golang-jwt/jwt/v5
```

> **Não use `github.com/dgrijalva/jwt-go`.** É o projeto original, abandonado desde
> 2021 e com CVE conhecida. O `golang-jwt/jwt` é o sucessor oficial mantido pela
> comunidade. Muito tutorial na internet ainda aponta para o abandonado.

---

## 8 · `jwt-cli`: inspecionar tokens no terminal

Decodifica e verifica tokens **offline**, sem colar nada em site nenhum. É a
ferramenta certa para inspecionar um token de produção.

```bash
# macOS / Linux com Homebrew
brew install mike-engel/jwt-cli/jwt-cli

# Linux — binário direto do GitHub (sem Homebrew)
curl -sL https://github.com/mike-engel/jwt-cli/releases/latest/download/jwt-linux.tar.gz \
  | tar xz -C ~/.local/bin
```
> Descompacta o binário em `~/.local/bin`, que fica no seu PATH sem precisar de
> `sudo`. Se essa pasta não existir: `mkdir -p ~/.local/bin`.

```bash
jwt --version
# esperado: jwt-cli 6.x.x (ou superior)
```

```bash
jwt decode eyJhbGciOiJFUzI1NiJ9.eyJzdWIiOiI0MiJ9.QaTj
# esperado: as seções Token header e Token claims formatadas
```

**Alternativa sem instalar nada**, com o que você já tem:

```bash
# decodifica o payload de um token que está na variável $AT
echo "$AT" | cut -d. -f2 | tr '_-' '/+' | base64 -d 2>/dev/null | jq .
```

---

## 9 · Editor e extensões

Qualquer editor serve. Com VS Code, três extensões valem o tempo:

```bash
code --install-extension humao.rest-client        # roda o requisicoes.http do projeto
code --install-extension vscjava.vscode-java-pack # só se for a trilha Java
code --install-extension ms-python.python         # só se for a trilha Python
```

> **Não instale extensões de "JWT debugger"** que pedem para colar o token num painel
> que envia dados para algum servidor. Confira sempre o que a extensão faz com o
> token. A extensão `rest-client` é local.

---

## 10 · Docker: o caminho que não suja a máquina

Se você não quer instalar Node, Python ou Java, e já tem Docker
(ver [docker/03-instalacao.md](../docker/03-instalacao.md)):

```bash
# Node 24, na pasta do projeto-modelo
cd 07-projeto-modelo
docker run --rm -it -v "$PWD":/app -w /app -p 3000:3000 node:24-alpine node --test
# esperado: pass 54  fail 0
```

```bash
# subir o servidor
docker run --rm -it -v "$PWD":/app -w /app -p 3000:3000 node:24-alpine node src/servidor.js
```

```bash
# Python com PyJWT, descartável
docker run --rm -it python:3.12-slim bash -c "pip install -q 'PyJWT[crypto]' && python"
```

```bash
# OpenSSL sem instalar
docker run --rm -it alpine/openssl version
```

**Testado em: Docker 29.1.3, em 14/08/2026.**

---

## 11 · PATH e variáveis de ambiente

Quase toda instalação que "não pegou" é problema de PATH. O padrão é sempre o mesmo:
o binário existe, mas o shell não sabe onde procurar.

### Diagnóstico

```bash
which node        # onde o shell acha o node? (vazio = não acha)
echo $PATH        # a lista de pastas onde ele procura, separadas por :
ls -la ~/.nvm/versions/node/     # o binário está aí, mesmo que o which não ache
```

No PowerShell:

```powershell
Get-Command node
$env:Path -split ';'
```

### Onde escrever a correção

| Shell | Arquivo | Como descobrir o seu |
|---|---|---|
| bash | `~/.bashrc` (interativo) e `~/.profile` (login) | `echo $SHELL` → `/bin/bash` |
| zsh (padrão do macOS) | `~/.zshrc` | `echo $SHELL` → `/bin/zsh` |
| fish | `~/.config/fish/config.fish` | `echo $SHELL` → `/usr/bin/fish` |
| PowerShell | `$PROFILE` (`notepad $PROFILE`) | — |

```bash
# exemplo: acrescentar ~/.local/bin ao PATH
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
```

### Por que "não pegou" antes de reabrir o terminal

Um shell lê o arquivo de perfil **uma vez, ao nascer**. Editar o arquivo não muda o
shell que já está aberto — ele não relê nada. Ou você abre um terminal novo, ou
força a releitura:

```bash
source ~/.bashrc     # relê no shell atual
# ou
exec $SHELL          # substitui o processo do shell por um novo
```

Esse é, disparado, o motivo nº 1 de "instalei e não funcionou".

### Variáveis que o material usa

O projeto-modelo lê estas (todas com valor padrão, nenhuma obrigatória):

```bash
export JWT_ISS="https://auth.suaempresa.com"   # emissor
export JWT_AUD="sua-api"                       # audiência
export JWT_ACCESS_TTL=900                      # vida do access token, em segundos
export JWT_REFRESH_TTL=1209600                 # vida do refresh, em segundos
export JWT_LEEWAY=60                           # tolerância de relógio
export PORT=3000
export COOKIE_SECURE=true                      # exigir HTTPS no cookie (produção)
```

> **Nunca ponha o segredo de assinatura numa variável de ambiente em produção** sem
> pensar duas vezes: variáveis de ambiente vazam em *crash dump*, em página de erro
> de framework, em `docker inspect` e em `/proc/<pid>/environ`. Ver
> [22-operacao-em-producao.md](22-operacao-em-producao.md).

---

## 12 · Permissões: o `sudo` que quebra tudo

**Nunca rode `sudo npm install -g`.** Não é superstição.

**Por que é problema, concretamente:**

1. Os arquivos instalados ficam com dono `root`. O próximo `npm install` normal, sem
   `sudo`, não consegue escrever neles — e você fica preso a usar `sudo` para sempre.
2. Um pacote npm pode executar scripts de instalação (`postinstall`). Com `sudo`,
   esse script arbitrário roda **como root**, com acesso total à sua máquina. Você
   entregou a máquina a quem quer que mantenha qualquer um dos milhares de pacotes da
   árvore de dependências.
3. O cache do npm em `~/.npm` fica com dono misturado, e passa a dar `EACCES` em
   operações que não têm nada a ver com o pacote instalado.

**O caminho certo:** use `nvm`/`fnm`/`mise`, que instalam tudo dentro do seu `$HOME`.
Aí `npm install -g` funciona sem `sudo`, porque a pasta é sua.

Se você já se meteu no problema:

```bash
# ver o estrago
ls -la ~/.npm | head
# consertar o dono do cache
sudo chown -R "$(id -u):$(id -g)" ~/.npm
```

Mesma regra em Python: **`sudo pip install` é pior ainda**, porque pode sobrescrever
bibliotecas de que o próprio sistema operacional depende. Use `venv`, sempre.

**Permissão de arquivo de chave privada:**

```bash
chmod 600 chave-privada.pem
ls -l chave-privada.pem
# esperado: -rw------- (só o dono lê e escreve)
```

Muitas ferramentas se recusam a usar uma chave privada legível por outros usuários —
e fazem certo.

---

## 13 · Rede corporativa: proxy e certificado interno

Se você está atrás de um proxy que inspeciona TLS, o `npm install` falha com
`self signed certificate in certificate chain` ou `UNABLE_TO_VERIFY_LEAF_SIGNATURE`.

```bash
# proxy
npm config set proxy       http://usuario:senha@proxy.empresa:8080
npm config set https-proxy http://usuario:senha@proxy.empresa:8080
export HTTP_PROXY=http://proxy.empresa:8080
export HTTPS_PROXY=http://proxy.empresa:8080
export NO_PROXY=localhost,127.0.0.1,.empresa.local
```

```bash
# certificado interno — o jeito CERTO
npm config set cafile /caminho/para/ca-da-empresa.pem
export NODE_EXTRA_CA_CERTS=/caminho/para/ca-da-empresa.pem
```

> ❌ **Não faça `npm config set strict-ssl false` nem
> `export NODE_TLS_REJECT_UNAUTHORIZED=0`.** Isso desliga a verificação de
> certificado *inteira*, para todo destino, permanentemente. Você troca um problema
> de configuração por uma porta aberta a interceptação. Peça o `.pem` da CA interna
> ao time de infraestrutura — eles têm.

Python:

```bash
pip install --proxy http://proxy.empresa:8080 "PyJWT[crypto]"
export REQUESTS_CA_BUNDLE=/caminho/para/ca-da-empresa.pem
```

Se a empresa usa registry espelhado (Nexus, Artifactory):

```bash
npm config set registry https://nexus.empresa/repository/npm-group/
pip config set global.index-url https://nexus.empresa/repository/pypi/simple
```

---

## 14 · Conviver com várias versões

Duas versões de Node na mesma máquina, sem conflito:

```bash
nvm install 20
nvm install 24
nvm use 20            # neste terminal
node --version        # esperado: v20.x.x
nvm use 24
node --version        # esperado: v24.x.x
nvm alias default 24  # o padrão de terminais novos
```

Por projeto, automático:

```bash
cd meu-projeto
echo "24" > .nvmrc
nvm use               # lê o .nvmrc
```

Python, por projeto: um `.venv` por pasta, e pronto. Nunca compartilhe ambientes
virtuais entre projetos.

---

## 15 · Reprodutibilidade

Sua máquina hoje e a máquina do CI daqui a seis meses precisam se comportar igual.

| Ferramenta | Arquivo | Efeito |
|---|---|---|
| Node | `.nvmrc` com `24` | `nvm use` acerta a versão |
| `mise`/`asdf` | `.tool-versions` | fixa Node, Python, Java de uma vez |
| npm | **`package-lock.json`** — **comite-o** | fixa a árvore inteira, com hash de cada pacote |
| npm no CI | `npm ci` (não `npm install`) | instala exatamente o lockfile e falha se divergir |
| Python | `requirements.txt` com `==`, ou `uv.lock` | fixa versão exata |
| Docker | tag com digest: `node:24-alpine@sha256:...` | a mesma imagem, byte a byte |

```bash
# .tool-versions, se você usa mise ou asdf
cat > .tool-versions <<'EOF'
nodejs 24.18.0
python 3.12.7
java temurin-17.0.19
EOF
```

**Por que isso importa neste assunto em particular:** uma CVE de biblioteca JWT (e há
várias, todo ano) só se corrige se você souber qual versão está rodando em cada
lugar. Sem lockfile, você não sabe.

---

## 16 · Atualizar e voltar atrás

```bash
# ver o que está desatualizado
npm outdated
# esperado: uma tabela com Current / Wanted / Latest

# ver vulnerabilidades conhecidas — faça isto hoje
npm audit
```

```bash
# atualizar a jose
npm install jose@latest
npm ls jose      # confira a versão nova

# voltar atrás, se algo quebrou
npm install jose@6.2.7
```

```bash
# Node: voltar para a versão anterior é trocar de linha, não desinstalar
nvm use 20
```

```bash
# Python
pip install --upgrade "PyJWT[crypto]"
pip install "PyJWT==2.13.0"    # fixar
```

**Regra prática:** atualização de biblioteca de segurança é a única que vale fazer
sem esperar. Se `npm audit` apontar algo em biblioteca JWT, é para hoje, não para a
próxima sprint. As três CVEs de 2026 citadas neste material são todas de *bypass de
autenticação* — quem não atualizou ficou com a porta aberta.

---

## 17 · Desinstalar por completo

Inclusive caches e configurações, que quase todo guia esquece.

### Node via nvm

```bash
nvm deactivate
nvm uninstall 24
rm -rf ~/.nvm
# remova as 3 linhas do nvm do seu ~/.bashrc ou ~/.zshrc
rm -rf ~/.npm ~/.npmrc          # cache e configuração global do npm
rm -rf ~/.node-gyp ~/.cache/node
```

### Node via apt / dnf / Homebrew / winget

```bash
sudo apt purge -y nodejs && sudo apt autoremove -y
sudo rm -f /etc/apt/sources.list.d/nodesource.list
sudo dnf remove -y nodejs
brew uninstall node@24 && brew cleanup
winget uninstall OpenJS.NodeJS
```

### Python / PyJWT

```bash
deactivate 2>/dev/null
rm -rf .venv                    # o ambiente virtual inteiro
rm -rf ~/.cache/pip
```

### jwt-cli

```bash
brew uninstall jwt-cli
rm -f ~/.local/bin/jwt
```

### O que fica para trás se você esquecer

| Sobra | Onde | Por que incomoda |
|---|---|---|
| cache do npm | `~/.npm` (pode passar de 1 GB) | espaço, e `EACCES` fantasma se tiver dono `root` |
| `~/.npmrc` | `$HOME` | guarda **tokens de registry** — apague de verdade |
| linhas do nvm | `~/.bashrc` | erro no shell a cada abertura |
| `.venv` órfãos | espalhados | centenas de MB somados |
| **chaves privadas de teste** | onde você as gerou | **apague**: `shred -u chave.pem` |

---

## 18 · Solução de problemas

Mensagem literal → causa → correção.

| Mensagem | Causa provável | Correção |
|---|---|---|
| `command not found: node` | binário fora do PATH, ou shell não releu o perfil | `exec $SHELL`; confira `echo $PATH`; ver [seção 11](#11--path-e-variáveis-de-ambiente) |
| `EACCES: permission denied, mkdir '/usr/lib/node_modules/...'` | tentou `npm i -g` num Node instalado com `sudo` | migre para `nvm`; **não** resolva com `sudo` — ver [seção 12](#12--permissões-o-sudo-que-quebra-tudo) |
| `nvm: command not found` | o instalador escreveu no arquivo de perfil errado | adicione o bloco `NVM_DIR` à mão em `~/.bashrc` ou `~/.zshrc` |
| `Error: Cannot find module 'jose'` | rodou fora da pasta do projeto, ou faltou `npm install` | `cd` para a pasta certa; `npm ls jose` |
| `SyntaxError: Cannot use import statement outside a module` | arquivo `.js` em CommonJS usando `import` | ponha `"type": "module"` no `package.json`, ou renomeie para `.mjs` |
| `self signed certificate in certificate chain` | proxy corporativo inspecionando TLS | `npm config set cafile ...`; **não** desligue `strict-ssl` — ver [seção 13](#13--rede-corporativa-proxy-e-certificado-interno) |
| `NotImplementedError: Algorithm 'RS256' could not be found` (PyJWT) | instalou `pyjwt` sem o extra `[crypto]` | `pip install "PyJWT[crypto]"` |
| `externally-managed-environment` (pip) | pip tentando instalar no Python do sistema | crie um `venv`; **não** use `--break-system-packages` |
| `Unable to discover any JWT implementations` (Java) | só `jjwt-api` no classpath | acrescente `jjwt-impl` e `jjwt-jackson` com `<scope>runtime</scope>` |
| `error:0308010C:digital envelope routines::unsupported` | OpenSSL 3 recusando algoritmo legado (chave RSA antiga, PKCS#1 velho) | regenere a chave em formato moderno; não use `--openssl-legacy-provider` como hábito |
| `LibreSSL` na saída de `openssl version` (macOS) | é o binário da Apple, não o OpenSSL | `brew install openssl@3` e ajuste o PATH — ver [seção 2](#2--openssl-todos-os-sistemas) |
| `EADDRINUSE: address already in use :::3000` | já há um servidor na porta 3000 | `PORT=3001 node src/servidor.js`, ou `lsof -i :3000` para achar o processo |
| `secretOrPrivateKey must have a value` | variável de ambiente do segredo vazia | confira `echo $JWT_SECRET`; lembre que `export` não atravessa terminais |

---

## 19 · Checklist "ambiente pronto"

Rode cada linha. Todas precisam responder o esperado antes de você abrir o
[04-como-comecar.md](04-como-comecar.md).

```bash
node --version
# esperado: v20.x.x ou superior (testado: v24.18.0)
```
```bash
npm --version
# esperado: 10.x ou superior
```
```bash
openssl version
# esperado: OpenSSL 3.x.x  (no macOS: NÃO pode dizer LibreSSL)
```
```bash
curl --version | head -1
# esperado: curl 7.x ou 8.x
```
```bash
jq --version
# esperado: jq-1.6 ou superior   (opcional, mas facilita muito)
```
```bash
openssl ecparam -name prime256v1 -genkey -noout -out /tmp/ok.pem && echo "cripto OK" && rm /tmp/ok.pem
# esperado: cripto OK
```
```bash
cd 07-projeto-modelo && node --test
# esperado: ... pass 54   fail 0
```

Se as sete linhas passaram, seu ambiente está pronto — **e você acabou de rodar uma
implementação completa de JWT sem instalar uma única dependência.**

---

## Autoteste

1. Você precisa instalar alguma coisa para começar a estudar JWT hoje? Cite dois
   caminhos que não exigem instalação.
2. Por que colar um token de produção no jwt.io é uma má ideia, mesmo o site
   processando tudo no navegador?
3. Explique, com um argumento concreto, por que `sudo npm install -g` é problema — e
   qual é o caminho certo.
4. Você instalou o Node, editou o `~/.bashrc`, e `node --version` continua dizendo
   `command not found` no terminal aberto. O que aconteceu e como resolver?
5. O que o extra `[crypto]` do PyJWT muda, e qual erro literal aparece sem ele?
6. Qual versão mínima de PyJWT você deve exigir em 2026, e por quê?
7. Sua empresa usa proxy com inspeção TLS e o `npm install` falha com
   `self signed certificate`. Qual a correção certa, e qual é o atalho perigoso que
   você deve recusar?
8. Você desinstalou o Node. Cite três coisas que ficaram para trás no seu `$HOME`.

---

### Fontes consultadas

Pesquisado na web em **14/08/2026**:

- [`jose` no npm](https://www.npmjs.com/package/jose) — versão 6.2.8
- [`jsonwebtoken` no npm](https://www.npmjs.com/package/jsonwebtoken) — versão 9.0.3
- [PyJWT no PyPI](https://pypi.org/project/PyJWT/) e [changelog](https://pyjwt.readthedocs.io/en/stable/changelog.html) — versão 2.13.0
- [CVE-2026-48526 (PyJWT)](https://cvereports.com/reports/CVE-2026-48526)
- [CVE-2026-34950 (fast-jwt)](https://securityonline.info/fast-jwt-authentication-bypass-cve-2026-34950-whitespace/)
- [jjwt no GitHub](https://github.com/jwtk/jjwt) e [Maven Central](https://central.sonatype.com/artifact/io.jsonwebtoken/jjwt) — 0.13.0
- [golang-jwt/jwt v5](https://pkg.go.dev/github.com/golang-jwt/jwt/v5)
- [comparativo jose × jsonwebtoken × fast-jwt](https://www.pkgpulse.com/guides/jose-vs-jsonwebtoken-vs-fast-jwt-jwt-libraries-nodejs-2026)

Verificado localmente em 14/08/2026: Node v24.18.0 · Python 3.10.12 · OpenSSL 3.0.2 ·
OpenJDK 17.0.19 · Docker 29.1.3 · Ubuntu 22.04.5 LTS.
