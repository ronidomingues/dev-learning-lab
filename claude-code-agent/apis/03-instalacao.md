# 03 · Manual de instalação

`Nível: iniciante` · `Atualizado: 11/08/2026`
`Testado contra: curl 8.x · jq 1.7.x · Node.js 24.x LTS · Docker 27.x`

Manual de campo. Siga na ordem. **Cada passo tem o comando, o que ele faz, uma verificação
com a saída esperada, e o que fazer se a saída for diferente.**

Boa notícia: **APIs é o assunto que menos exige instalação de todo este repositório.**
A ferramenta principal, o `curl`, já está no seu computador.

---

## Índice

1. [Sem instalar nada — comece agora](#1-sem-instalar-nada--comece-agora)
2. [curl](#2-curl)
3. [Windows: a pegadinha do curl no PowerShell](#3-windows-a-pegadinha-do-curl-no-powershell)
4. [jq — ler JSON sem enlouquecer](#4-jq--ler-json-sem-enlouquecer)
5. [HTTPie (opcional, mas agradável)](#5-httpie-opcional-mas-agradável)
6. [Cliente gráfico: Bruno, Postman ou Hoppscotch](#6-cliente-gráfico-bruno-postman-ou-hoppscotch)
7. [Node.js](#7-nodejs)
8. [Docker (opcional)](#8-docker-opcional)
9. [Editor: VS Code + extensões](#9-editor-vs-code--extensões)
10. [Ferramentas de contrato: Redocly, Spectral, oapi-tools](#10-ferramentas-de-contrato)
11. [PATH e variáveis de ambiente](#11-path-e-variáveis-de-ambiente)
12. [Permissões — por que não usar sudo](#12-permissões--por-que-não-usar-sudo)
13. [Rede corporativa: proxy, certificado, firewall](#13-rede-corporativa-proxy-certificado-firewall)
14. [Convivência de versões](#14-convivência-de-versões)
15. [Reprodutibilidade](#15-reprodutibilidade)
16. [Atualizar e voltar atrás](#16-atualizar-e-voltar-atrás)
17. [Desinstalar por completo](#17-desinstalar-por-completo)
18. [Solução de problemas](#18-solução-de-problemas)
19. [Checklist: ambiente pronto](#19-checklist-ambiente-pronto)

---

## 1. Sem instalar nada — comece agora

Leia esta seção antes de qualquer outra.

### 1.1 O navegador já é um cliente de API

Cole isto na barra de endereços do seu navegador:

```
https://api.github.com/repos/nodejs/node
```

**Verificação:** aparece um bloco de JSON com dados do repositório do Node.js.
Chrome e Firefox formatam JSON automaticamente hoje.

**Você acabou de consumir uma API pública, sem cadastro, sem instalar nada.**

### 1.2 O DevTools mostra todas as APIs de qualquer site

1. Abra qualquer site moderno.
2. `F12` (ou `Ctrl+Shift+I` / `Cmd+Opt+I`) → aba **Network** / **Rede**.
3. Filtre por **Fetch/XHR**.
4. Navegue pelo site.

Cada linha ali é uma chamada de API. Clique numa: você vê a URL, o método, os cabeçalhos,
o corpo enviado e a resposta.

> **Este é o melhor exercício de aprendizado de API que existe, e é grátis.** Abra o site
> de um banco, de um e-commerce, de uma rede social, e veja como profissionais desenham
> APIs de verdade. Clique com o botão direito numa linha → *Copy → Copy as cURL* e você tem
> o comando pronto para reproduzir a chamada no terminal.

### 1.3 Clientes de API no navegador, sem instalação

| Ferramenta | URL | Nota |
|---|---|---|
| **Hoppscotch** | https://hoppscotch.io | leve, open source, roda tudo no navegador |
| **Postman Web** | https://web.postman.co | exige conta |
| **ReqBin** | https://reqbin.com | simples, sem conta |

> Atenção: um cliente que roda **no navegador** esbarra em **CORS** ao chamar APIs que não
> o permitem. Hoppscotch oferece um *proxy* para contornar — o que significa que sua
> requisição, **incluindo credenciais**, passa pelo servidor deles. **Não use proxy de
> terceiros com token de produção.** O que é CORS: [12-http-por-dentro.md](12-http-por-dentro.md) §9.

### 1.4 Ambientes online completos

| Opção | Para quê |
|---|---|
| **GitHub Codespaces** | container Linux completo no navegador; cota gratuita mensal |
| **StackBlitz / CodeSandbox** | rodar o projeto-modelo em Node sem instalar |
| **Replit** | idem |

**Recomendação:** faça §1.1 e §1.2 hoje, siga para [04-como-comecar.md](04-como-comecar.md),
e volte para instalar o resto quando for construir sua própria API.

---

## 2. curl

O canivete suíço de HTTP. Presente em praticamente toda instalação de Linux, macOS e
Windows 10+.

**Primeiro, verifique se você já tem:**

```bash
curl --version
```
```text
# esperado (número exato varia):
# curl 8.9.1 (x86_64-pc-linux-gnu) libcurl/8.9.1 OpenSSL/3.2.2 ...
# Release-Date: 2026-xx-xx
# Protocols: dict file ftp ftps gopher gophers http https imap ...
# Features: alt-svc AsynchDNS brotli HSTS HTTP2 HTTPS-proxy IPv6 ... 
```

**Duas coisas para olhar na saída:**
- a versão deve ser **8.x** (versões 7.x antigas não têm `--json` nem HTTP/2 confiável);
- em `Features`, procure por **`HTTP2`**. Se aparecer `HTTP3`, melhor ainda (raro em pacotes
  padrão, porque exige uma biblioteca TLS específica).

Se já apareceu, **pule para a §4**.

### 2.1 Linux — Debian/Ubuntu

```bash
sudo apt-get update && sudo apt-get install -y curl
```
*Instala o curl a partir dos repositórios da distribuição.*

### 2.2 Linux — Fedora/RHEL/Rocky

```bash
sudo dnf install -y curl
```

### 2.3 macOS

O macOS já traz curl. Para uma versão mais nova (com HTTP/3, por exemplo):

```bash
brew install curl
```
*Instala a versão do Homebrew. **Atenção:** por padrão ela fica "keg-only" e não substitui
a do sistema.*

```bash
echo 'export PATH="$(brew --prefix)/opt/curl/bin:$PATH"' >> ~/.zshrc && source ~/.zshrc
```
*Coloca a versão do brew antes da do sistema no PATH.*

**Verificação:** `which curl` deve apontar para `/opt/homebrew/opt/curl/bin/curl`
(Apple Silicon) ou `/usr/local/opt/curl/bin/curl` (Intel).

### 2.4 Windows

O Windows 10 (build 1803+) e o Windows 11 **já trazem** `curl.exe` em
`C:\Windows\System32\curl.exe`.

```powershell
curl.exe --version
```
*Note o `.exe` — ele é obrigatório no PowerShell. Ver §3.*

Para uma versão mais nova:
```powershell
winget install cURL.cURL
```

---

## 3. Windows: a pegadinha do curl no PowerShell

**Este é o problema número um de quem aprende APIs no Windows.** Vale uma seção inteira.

No PowerShell, `curl` é um **alias** (apelido) para `Invoke-WebRequest`, um comando
completamente diferente, com sintaxe incompatível.

```powershell
curl -H "Accept: application/json" https://api.github.com/repos/nodejs/node
# Invoke-WebRequest: Não é possível localizar um parâmetro posicional...
```

O comando falha, a mensagem não ajuda, e você perde uma hora achando que o problema é a API.

### As três soluções, em ordem de preferência

**A) Escreva sempre `curl.exe`** (recomendado — explícito e sem efeito colateral):
```powershell
curl.exe -H "Accept: application/json" https://api.github.com/repos/nodejs/node
```

**B) Remova o alias na sua sessão:**
```powershell
Remove-Item Alias:curl -Force
```
*Vale só na sessão atual. Para tornar permanente, adicione ao seu perfil:*
```powershell
notepad $PROFILE
# adicione a linha:  Remove-Item Alias:curl -Force -ErrorAction SilentlyContinue
```

**C) Use o WSL2** (a melhor experiência geral):
```powershell
wsl --install -d Ubuntu-24.04
```
*Instala o WSL2 com Ubuntu. Reinicie quando pedir. Dentro dele, tudo funciona como Linux.*

**Verificação:**
```powershell
wsl -l -v
# esperado: Ubuntu-24.04    Running    2     ← o "2" é a versão do WSL
```

> **Recomendação:** para este assunto, use **WSL2**. Todo comando deste material, de todo
> tutorial da internet e de toda resposta de Stack Overflow assume Unix. Se a política de
> TI proibir WSL, use a opção **A** e escreva `curl.exe` sempre.

**Detalhe adicional das aspas no Windows nativo:** o `cmd.exe` não entende aspas simples.
Onde este material escreve `-d '{"a":1}'`, no `cmd` use `-d "{\"a\":1}"`. No PowerShell,
prefira aspas simples externas ou um arquivo: `-d '@corpo.json'`.

---

## 4. jq — ler JSON sem enlouquecer

Respostas de API vêm em JSON, frequentemente em uma única linha de 40 KB. O `jq` formata,
filtra e transforma.

### Linux Debian/Ubuntu
```bash
sudo apt-get install -y jq
```

### Linux Fedora/RHEL
```bash
sudo dnf install -y jq
```

### macOS
```bash
brew install jq
```

### Windows
```powershell
winget install jqlang.jq
```

**Verificação (todos):**
```bash
jq --version
# esperado: jq-1.7.1 (ou superior)
```

**Teste real:**
```bash
curl -s https://api.github.com/repos/nodejs/node | jq '.name, .stargazers_count, .license.spdx_id'
```
```text
# esperado:
# "node"
# 115000        (número varia)
# "MIT"
```
*`-s` (silent) esconde a barra de progresso do curl, que sujaria a entrada do jq.*

**Se `jq` não estiver disponível**, há alternativas: `python3 -m json.tool` (formata, não
filtra) ou `node -e "console.log(JSON.stringify(JSON.parse(require('fs').readFileSync(0)),null,2))"`.

---

## 5. HTTPie (opcional, mas agradável)

Cliente de linha de comando com sintaxe muito mais legível que a do curl, saída colorida e
JSON formatado por padrão.

### Todas as plataformas, via pipx (recomendado)
```bash
pipx install httpie
```
*`pipx` instala aplicações Python isoladas, sem poluir o Python do sistema.*

Se você não tem `pipx`:
```bash
python3 -m pip install --user pipx && python3 -m pipx ensurepath
```

### Alternativas por gerenciador de pacotes
| Sistema | Comando |
|---|---|
| Debian/Ubuntu | `sudo apt-get install -y httpie` |
| Fedora | `sudo dnf install -y httpie` |
| macOS | `brew install httpie` |
| Windows | `winget install HTTPie.HTTPie` |

**Verificação:**
```bash
http --version
# esperado: 3.2.x (ou superior)
```

**A diferença, lado a lado:**
```bash
# curl
curl -s -X POST https://httpbin.org/post \
  -H 'Content-Type: application/json' \
  -d '{"nome":"Maria","idade":30}' | jq

# HTTPie — mesma coisa
http POST httpbin.org/post nome=Maria idade:=30
```
*No HTTPie, `chave=valor` vira string e `chave:=valor` vira JSON cru (número, booleano,
objeto). É a sintaxe que mais confunde no início e a que mais economiza depois.*

> **Opinião:** aprenda **curl** primeiro. Ele é o que você vai encontrar em toda
> documentação, em todo Stack Overflow e em todo script de CI. HTTPie é conforto para o
> dia a dia; curl é a língua franca.

---

## 6. Cliente gráfico: Bruno, Postman ou Hoppscotch

Para trabalhar sério, você vai querer salvar coleções de requisições, ambientes e variáveis.

| Ferramenta | Modelo | Onde salva as coleções | Nota |
|---|---|---|---|
| **Bruno** | open source, offline-first | **arquivos de texto na sua pasta** | ✅ **minha recomendação** |
| **Postman** | SaaS, plano gratuito limitado | na nuvem da Postman (por padrão) | o mais popular |
| **Insomnia** | open source com plano pago | local ou nuvem | boa alternativa |
| **Hoppscotch** | open source, web | navegador ou self-host | sem instalar |
| **Extensão REST Client (VS Code)** | open source | arquivos `.http` na sua pasta | ótima e minimalista |

### Por que Bruno primeiro

Bruno guarda as coleções em **arquivos de texto** (formato `.bru`) dentro do seu projeto.
Isso significa que elas entram no **Git**, aparecem no *code review*, e não dependem de
conta em serviço nenhum.

O Postman, por padrão, sincroniza suas coleções — **incluindo variáveis de ambiente, onde
as pessoas costumam guardar tokens** — para a nuvem da empresa. Já houve incidentes
públicos de coleções expostas com segredos dentro. Isso é configurável, mas o padrão não
ajuda.

### Instalação do Bruno

| Sistema | Comando |
|---|---|
| Linux (Debian/Ubuntu) | baixe o `.deb` em https://www.usebruno.com/downloads e `sudo apt install ./bruno_*.deb` |
| Linux (Snap) | `sudo snap install bruno` |
| macOS | `brew install --cask bruno` |
| Windows | `winget install Bruno.Bruno` |

**Verificação:** o aplicativo abre e permite criar uma *Collection*. Crie uma requisição
`GET https://api.github.com/repos/nodejs/node` e envie — deve retornar `200 OK`.

### Alternativa dentro do editor: REST Client

```bash
code --install-extension humao.rest-client
```

Crie um arquivo `requisicoes.http`:
```http
@base = https://api.github.com

### Buscar um repositório
GET {{base}}/repos/nodejs/node
Accept: application/vnd.github+json

### Buscar as tags
GET {{base}}/repos/nodejs/node/tags?per_page=5
```
Clique em *Send Request* acima de cada bloco. **O arquivo é texto, versiona no Git e vira
documentação executável.** É a opção mais simples que existe e a que eu mais uso.

---

## 7. Node.js

Necessário apenas para o [07-projeto-modelo/](07-projeto-modelo/README.md).
Se você for construir a API em outra linguagem, pule esta seção.

**Versão recomendada em 11/08/2026:** Node.js **24.x** — é o **Active LTS** desde
28/10/2025, entra em Maintenance em 20/10/2026 e chega ao fim de vida em 30/04/2028.
Node **22.x** está em Maintenance LTS e também funciona. **Evite** versões ímpares
(23, 25) — são de curta duração.

### 7.1 Linux e macOS — via nvm (recomendado)

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
```
*Instala o gerenciador de versões `nvm` no seu diretório pessoal (`~/.nvm`). Não usa sudo.*

Feche e reabra o terminal, ou:
```bash
source ~/.bashrc   # ou ~/.zshrc, conforme seu shell
```

```bash
nvm install 24 && nvm alias default 24
```
*Instala o Node 24 e o torna o padrão para novas sessões.*

**Verificação:**
```bash
node --version && npm --version
# esperado:
# v24.x.x
# 11.x.x  (ou superior)
```

**Se der `nvm: command not found`:** o instalador escreveu no `~/.bashrc`, mas você usa
zsh ou fish. Copie o bloco `export NVM_DIR=...` para o arquivo de perfil correto. Ver §11.

### 7.2 Windows

**Via WSL2:** siga a §7.1 dentro do Ubuntu. É o caminho recomendado.

**Nativo, via winget:**
```powershell
winget install OpenJS.NodeJS.LTS
```
Feche e reabra o PowerShell (o PATH só é relido em processo novo):
```powershell
node --version
# esperado: v24.x.x
```

Para múltiplas versões no Windows nativo, use `nvm-windows`
(https://github.com/coreybutler/nvm-windows) — **projeto diferente** do `nvm` do Unix,
com sintaxe parecida mas não idêntica.

### 7.3 Alternativas ao nvm

| Ferramenta | Vantagem |
|---|---|
| **fnm** | muito mais rápido; escrito em Rust; mesma ideia do nvm |
| **mise** | gerencia Node, Python, Go, Java etc. num `.tool-versions` só |
| **asdf** | idem, mais antigo |
| **Volta** | instala versões por projeto automaticamente |

---

## 8. Docker (opcional)

Útil para subir um banco de dados, uma fila ou uma API de teste sem instalar nada no host.

| Sistema | Como |
|---|---|
| Linux | https://docs.docker.com/engine/install/ (siga o guia da sua distro) |
| macOS | `brew install --cask docker` (Docker Desktop) ou `brew install colima docker` |
| Windows | `winget install Docker.DockerDesktop` (requer WSL2) |

**Verificação:**
```bash
docker --version && docker run --rm hello-world
```
```text
# esperado, ao final:
# Hello from Docker!
# This message shows that your installation appears to be working correctly.
```

**Se der `permission denied` no Linux:**
```bash
sudo usermod -aG docker $USER
```
*Adiciona seu usuário ao grupo docker. **Faça logout e login** — grupos só são relidos numa
sessão nova. Isso é preferível a rodar `sudo docker` sempre.*

> Nota de licença: o **Docker Desktop** exige assinatura paga para empresas acima de um
> certo porte. Alternativas gratuitas: **Podman**, **Colima**, **Rancher Desktop**, ou o
> Docker Engine direto no Linux. Ver [80-custos-e-licencas.md](80-custos-e-licencas.md).

---

## 9. Editor: VS Code + extensões

```bash
# macOS
brew install --cask visual-studio-code
# Windows
winget install Microsoft.VisualStudioCode
# Debian/Ubuntu: baixe o .deb em https://code.visualstudio.com e:
sudo apt install ./code_*.deb
```

**Extensões que valem para este assunto:**
```bash
code --install-extension humao.rest-client
code --install-extension redhat.vscode-yaml
code --install-extension 42Crunch.vscode-openapi
code --install-extension rangav.vscode-thunder-client
```
*REST Client (requisições em arquivo `.http`), YAML (OpenAPI é YAML), OpenAPI (validação e
preview do contrato), Thunder Client (cliente gráfico embutido).*

**Verificação:** crie um arquivo `teste.http`, escreva `GET https://api.github.com` e veja
o link *Send Request* aparecer acima da linha.

**Configuração útil para OpenAPI** (`settings.json`):
```json
{
  "yaml.schemas": {
    "https://spec.openapis.org/oas/3.1/schema/2022-10-07": ["openapi.yaml", "openapi.yml"]
  }
}
```
*Liga o autocomplete e a validação do contrato enquanto você digita.*

---

## 10. Ferramentas de contrato

Necessárias a partir de [17-contratos-e-documentacao.md](17-contratos-e-documentacao.md).

```bash
npm install -g @redocly/cli @stoplight/spectral-cli
```
*Redocly: valida, junta e gera documentação a partir de OpenAPI. Spectral: linter de
contrato com regras customizáveis.*

**Verificação:**
```bash
redocly --version    # esperado: 1.x.x ou superior
spectral --version   # esperado: 6.x.x ou superior
```

**Teste real:**
```bash
spectral lint https://raw.githubusercontent.com/OAI/OpenAPI-Specification/main/examples/v3.0/petstore.yaml
# esperado: uma lista de avisos (warnings) e "✖ N problems"
# Avisos são normais: o ruleset padrão é rigoroso.
```

Outras ferramentas úteis, instaláveis quando precisar:

| Ferramenta | Para quê |
|---|---|
| `openapi-generator-cli` | gerar clientes e servidores a partir do contrato (requer Java) |
| `oasdiff` | detectar mudanças **quebradoras** entre duas versões do contrato |
| `schemathesis` | teste automático baseado no contrato (fuzzing) — Python |
| `grpcurl` | o curl do gRPC |
| `websocat` | o curl do WebSocket |
| `k6` ou `oha` | teste de carga |

---

## 11. PATH e variáveis de ambiente

**O que é o PATH:** a lista de diretórios que o shell percorre, em ordem, procurando o
programa que você digitou. Se o diretório não está lá, você recebe "command not found"
mesmo com o arquivo instalado.

```bash
echo $PATH              # Linux, macOS, WSL
which -a curl jq node   # mostra TODAS as ocorrências de cada binário
```
```powershell
$env:Path -split ';'    # Windows PowerShell
Get-Command curl -All   # todas as ocorrências
```

**Se `which -a` mostrar mais de uma linha para o mesmo comando, você tem instalações
duplicadas.** A primeira ganha. É a causa de "atualizei mas a versão não muda".

### Onde colocar a linha de PATH, por shell

| Shell | Arquivo | Como saber se é o seu |
|---|---|---|
| bash | `~/.bashrc` (Linux) · `~/.bash_profile` (macOS) | `echo $SHELL` → `/bin/bash` |
| zsh | `~/.zshrc` | `echo $SHELL` → `/bin/zsh` (padrão do macOS) |
| fish | `~/.config/fish/config.fish` | `echo $SHELL` → `/usr/bin/fish` |
| PowerShell | `$PROFILE` (`notepad $PROFILE`) | — |

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc && source ~/.bashrc
```

> **Por que "não pegou" antes de reabrir o terminal:** variáveis de ambiente são copiadas
> do processo pai para o filho **no momento em que o filho nasce**. Um terminal já aberto
> tem uma cópia antiga do PATH. `source` relê o arquivo no processo atual e resolve.
> Isso não é peculiaridade de nenhuma ferramenta — é como processos funcionam em Unix desde
> os anos 70.

### Variáveis de ambiente específicas deste assunto

**A regra de ouro: chave de API nunca vai no código, nunca vai no Git, nunca vai no
histórico do shell.**

```bash
# ~/.bashrc ou ~/.zshrc — mas veja o aviso abaixo
export GITHUB_TOKEN="ghp_xxxxxxxxxxxx"
```
```bash
curl -H "Authorization: Bearer $GITHUB_TOKEN" https://api.github.com/user
```

**O problema do histórico do shell:** se você digitar o token direto no comando, ele fica
gravado em `~/.bash_history` em texto puro, para sempre.

**Três formas corretas de evitar isso:**

```bash
# 1. Um espaço antes do comando (com HISTCONTROL=ignorespace) não grava no histórico
 export TOKEN="segredo"
```
```bash
# 2. Ler de um arquivo com permissão restrita
echo "segredo" > ~/.tokens/github && chmod 600 ~/.tokens/github
export GITHUB_TOKEN="$(cat ~/.tokens/github)"
```
```bash
# 3. Arquivo .env por projeto, com .gitignore — o padrão da indústria
cat > .env <<'EOF'
GITHUB_TOKEN=ghp_xxxxxxxxxxxx
EOF
echo ".env" >> .gitignore
set -a && source .env && set +a   # exporta tudo do arquivo
```

> **Nunca comite um `.env`.** Comite um **`.env.example`** com as chaves e valores vazios,
> para o próximo desenvolvedor saber o que precisa preencher. Isso é convenção universal.

Variáveis que as ferramentas respeitam:

| Variável | Efeito |
|---|---|
| `HTTP_PROXY` / `HTTPS_PROXY` / `NO_PROXY` | proxy corporativo (§13) |
| `CURL_CA_BUNDLE` | CA customizada para o curl |
| `NODE_EXTRA_CA_CERTS` | CA customizada para o Node |
| `SSL_CERT_FILE` | CA customizada para muitas ferramentas |
| `NO_COLOR=1` | desliga cor na saída (útil em logs de CI) |

---

## 12. Permissões — por que não usar sudo

Se `npm install -g` deu `EACCES`, a saída óbvia parece ser `sudo npm install -g`. **Não faça.**

**Por que é problema, de verdade:**

1. Os arquivos passam a pertencer ao `root`. Toda atualização futura vai exigir `sudo`
   também, e um dia você vai esquecer e ficar com uma instalação meio-root, meio-sua — que
   quebra de formas difíceis de diagnosticar.
2. `npm install` executa **scripts arbitrários de pós-instalação** definidos pelos pacotes.
   Rodá-los como root dá a eles poder total sobre a máquina. É um vetor real de ataque de
   cadeia de suprimentos, não teoria.
3. O cache do npm (`~/.npm`) fica com arquivos de root, e depois seu usuário não consegue
   mais escrever nele.

**As três soluções corretas, em ordem:**

**A) Use um gerenciador de versões** (nvm, fnm, mise, Volta). O Node e todos os pacotes
globais ficam no seu diretório pessoal. O problema deixa de existir.

**B) Mude o prefixo global do npm:**
```bash
mkdir -p ~/.npm-global
npm config set prefix ~/.npm-global
echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.bashrc && source ~/.bashrc
```

**C) Não instale globalmente.** Use `npx` para ferramentas ocasionais:
```bash
npx @redocly/cli lint openapi.yaml
```
*Baixa, executa e descarta. Ideal para ferramentas que você usa uma vez por mês.*

**Se você já rodou `sudo npm`:**
```bash
sudo chown -R $(whoami) ~/.npm ~/.config
```

---

## 13. Rede corporativa: proxy, certificado, firewall

### 13.1 Proxy

```bash
export HTTP_PROXY="http://usuario:senha@proxy.empresa.com:8080"
export HTTPS_PROXY="$HTTP_PROXY"
export NO_PROXY="localhost,127.0.0.1,::1,.empresa.local"
```
*`NO_PROXY` com localhost é **obrigatório** — sem ele, testar sua própria API local
(`http://localhost:3000`) tenta passar pelo proxy e falha de forma incompreensível.*

Para o npm:
```bash
npm config set proxy http://proxy.empresa.com:8080
npm config set https-proxy http://proxy.empresa.com:8080
```

> Se a senha tiver caracteres especiais (`@`, `:`, `#`, `/`), codifique em percent-encoding:
> `@` → `%40`, `#` → `%23`. É a causa nº 1 de "configurei o proxy e mesmo assim falha".

**A armadilha que custa uma tarde:** nem toda ferramenta respeita essas variáveis.

| Ferramenta | Respeita `HTTP_PROXY`? |
|---|---|
| `curl`, `wget`, `git` | ✅ |
| `npm`, `pip` | ✅ (com a configuração própria também) |
| **`fetch` do Node.js** | ❌ **não** |
| `requests` do Python | ✅ |
| navegador | usa a configuração do sistema, não as variáveis |

O sintoma é desconcertante: `curl https://api.exemplo.com` funciona, o **mesmo endereço**
no seu código Node dá timeout, e você culpa o próprio código. A correção:

```javascript
import { ProxyAgent, setGlobalDispatcher } from 'undici';
if (process.env.HTTPS_PROXY) {
  setGlobalDispatcher(new ProxyAgent(process.env.HTTPS_PROXY));
}
```
*O `undici` é o motor do `fetch` do Node; para importá-lo como módulo, `npm i undici`.*

**Teste que distingue "sem rede" de "proxy não configurado":**
```bash
curl -s -o /dev/null -w 'curl: %{http_code}\n' https://api.github.com/
node -e "fetch('https://api.github.com/',{signal:AbortSignal.timeout(8000)}).then(r=>console.log('node:',r.status)).catch(e=>console.log('node FALHOU:',e.name))"
```
*Se o `curl` responde `200` e o Node falha, é proxy — não é a sua rede nem o seu código.*

### 13.2 Certificado interno (inspeção de TLS)

Empresas que inspecionam TLS substituem o certificado dos sites por um da CA interna.
As ferramentas rejeitam, com mensagens como:

```text
curl: (60) SSL certificate problem: unable to get local issuer certificate
Error: unable to verify the first certificate    (Node.js)
```

**Correto:**
```bash
export CURL_CA_BUNDLE=/caminho/para/ca-empresa.pem
export NODE_EXTRA_CA_CERTS=/caminho/para/ca-empresa.pem
export SSL_CERT_FILE=/caminho/para/ca-empresa.pem
```
*Adiciona a CA da empresa às autoridades confiáveis, **sem** desligar a verificação.*

**Errado, e por quê:**
```bash
curl -k https://...                        # NÃO
export NODE_TLS_REJECT_UNAUTHORIZED=0      # NÃO
```
`-k` (`--insecure`) desliga a verificação de certificado para aquela chamada. A variável do
Node desliga para **todas** as conexões do processo — inclusive as que baixam código que
você vai executar. Resolvem o sintoma abrindo um buraco real: com verificação desligada,
qualquer um na rede pode se passar pelo servidor e ler ou alterar o que trafega.

**Use `-k` apenas para diagnosticar por 30 segundos**, nunca em script, nunca em arquivo de
perfil, nunca em CI.

### 13.3 Firewall — o que precisa sair

| Destino | Porta | Para quê |
|---|---|---|
| qualquer host HTTPS | 443 | chamar APIs |
| `registry.npmjs.org` | 443 | npm |
| `github.com`, `raw.githubusercontent.com` | 443 | instaladores, specs |
| `registry-1.docker.io`, `auth.docker.io` | 443 | imagens Docker |
| **UDP 443** | 443/UDP | **HTTP/3 (QUIC)** — bloqueado em muitas redes corporativas |

> **Detalhe que gera diagnóstico errado:** HTTP/3 roda sobre **QUIC**, que usa **UDP**.
> Muitas redes corporativas bloqueiam UDP na saída. O cliente então cai de volta para
> HTTP/2 sobre TCP — o que funciona, mas adiciona latência à primeira tentativa. Se você
> medir "a API está lenta só na rede da empresa", teste com `curl --http2` forçado.

---

## 14. Convivência de versões

### Node
```bash
nvm install 22 && nvm install 24
nvm use 24              # nesta sessão
nvm alias default 24    # padrão para novas sessões
```
Por projeto, crie um `.nvmrc`:
```bash
echo "24" > .nvmrc
nvm use          # lê o .nvmrc do diretório atual
```

### Ferramentas de linha de comando
Prefira `npx <ferramenta>` a instalar globalmente: cada projeto usa a versão que declarou
no `package.json`, sem conflito.

### Versões de API que você consome
Não é sobre a sua máquina, mas é o mesmo problema: **fixe a versão da API externa** que
você chama.
```bash
curl -H "Accept: application/vnd.github+json" \
     -H "X-GitHub-Api-Version: 2022-11-28" \
     https://api.github.com/repos/nodejs/node
```
*Sem o cabeçalho de versão, você recebe "a mais recente" — e um dia ela muda sem aviso.
Ver [18-operacao-e-ciclo-de-vida.md](18-operacao-e-ciclo-de-vida.md) §4.*

---

## 15. Reprodutibilidade

Comprometa no Git, na raiz do projeto:

| Arquivo | Garante |
|---|---|
| `.nvmrc` | todo mundo no mesmo Node |
| `package.json` + `package-lock.json` | mesmas versões de dependência |
| `openapi.yaml` | o **contrato** da sua API, versionado |
| `.env.example` | quais variáveis existem (sem os valores) |
| `.gitignore` com `.env` e `node_modules/` | segredos e lixo fora do repositório |
| `requisicoes.http` ou coleção Bruno | requisições de exemplo, executáveis |
| `Dockerfile` / `compose.yaml` | ambiente idêntico entre local e CI |

Exemplo de `compose.yaml` para o projeto-modelo:
```yaml
services:
  api:
    build: .
    ports: ["3000:3000"]
    environment:
      NODE_ENV: production
      PORT: "3000"
    healthcheck:
      test: ["CMD", "node", "-e", "fetch('http://localhost:3000/health').then(r=>process.exit(r.ok?0:1)).catch(()=>process.exit(1))"]
      interval: 10s
      timeout: 3s
      retries: 3
```

---

## 16. Atualizar e voltar atrás

```bash
# curl e jq: pelo gerenciador de pacotes do sistema
sudo apt-get update && sudo apt-get upgrade curl jq

# Node
nvm install 24 --reinstall-packages-from=22
nvm alias default 24

# Voltar a uma versão específica de Node
nvm use 22

# Ferramentas npm globais
npm update -g
npm install -g @redocly/cli@1.25.0   # versão exata, para voltar atrás
```

**Verificação após qualquer atualização:** rode o checklist da §19 inteiro.
Uma atualização que quebra o ambiente é mais comum do que parece, e descobrir na hora é
mais barato que descobrir no meio de uma tarefa.

---

## 17. Desinstalar por completo

```bash
# Node instalado por nvm
nvm uninstall 24
rm -rf ~/.nvm                 # remove o nvm inteiro
# e apague o bloco NVM_DIR do seu ~/.bashrc / ~/.zshrc

# Pacotes npm globais e cache
npm ls -g --depth=0           # veja o que existe antes de apagar
rm -rf ~/.npm ~/.npm-global

# jq / curl (Debian/Ubuntu)
sudo apt-get remove --purge jq
# NÃO remova o curl do sistema: outras ferramentas dependem dele

# Bruno
brew uninstall --cask bruno            # macOS
sudo snap remove bruno                 # Linux snap
# coleções ficam onde VOCÊ salvou (são arquivos seus) — apague se quiser

# Docker
brew uninstall --cask docker           # macOS
# Linux: siga o guia da distro; lembre de `docker system prune -a --volumes`
```

**Restos que ficam para trás e ninguém lembra:**

```bash
rm -rf ~/.config/configstore     # muitos CLIs npm guardam config aqui
rm -rf ~/.cache/node-gyp
rm -rf ~/.docker
```

**E o mais importante: revogue os tokens.** Desinstalar a ferramenta **não** invalida uma
chave de API que você criou. Vá ao painel de cada serviço (GitHub → *Settings → Developer
settings → Personal access tokens*, etc.) e **revogue**. Faça isso ao devolver um
computador ou ao suspeitar de vazamento.

---

## 18. Solução de problemas

| Mensagem literal | Causa provável | Correção |
|---|---|---|
| `Invoke-WebRequest: Não é possível localizar um parâmetro posicional` | você usou `curl` no PowerShell, que é alias de outro comando | §3 — escreva `curl.exe`, ou use WSL |
| `curl: (6) Could not resolve host: api.exemplo.com` | DNS falhou, ou há um erro de digitação na URL | teste `ping`/`nslookup`; verifique proxy (§13.1) |
| `curl: (7) Failed to connect to ... port 443: Connection refused` | firewall, servidor fora do ar, ou porta errada | teste a mesma URL no navegador |
| `curl: (60) SSL certificate problem: unable to get local issuer certificate` | proxy corporativo com inspeção TLS | §13.2 — `CURL_CA_BUNDLE`. **Não** use `-k` permanente |
| `curl: (28) Operation timed out after 30000 milliseconds` | servidor lento ou rede bloqueada | aumente com `--max-time`; investigue a rede |
| `jq: error (at <stdin>:0): Cannot index string with "x"` | a resposta não é JSON (é HTML de erro, por exemplo) | rode sem o `jq` para ver o corpo cru; adicione `-i` no curl para ver os cabeçalhos |
| `parse error: Invalid numeric literal` (jq) | a saída do curl veio com a barra de progresso misturada | use `curl -s` |
| `command not found: jq` / `node` / `http` | binário fora do PATH, ou terminal não reaberto | §11 — `which -a`, reabra o terminal |
| `EACCES: permission denied ... /usr/lib/node_modules` | `npm -g` sem permissão | **não use sudo**. §12 |
| `Error: unable to verify the first certificate` (Node) | CA interna | `NODE_EXTRA_CA_CERTS` (§13.2) |
| `EADDRINUSE: address already in use :::3000` | já existe algo escutando naquela porta | `lsof -i :3000` (Unix) ou `netstat -ano \| findstr :3000` (Windows), e mate o processo — ou mude a porta |
| `Access to fetch at '...' has been blocked by CORS policy` | você chamou uma API de dentro do navegador e ela não permite | não é erro da API nem do seu código. Ver [12-http-por-dentro.md](12-http-por-dentro.md) §9 |
| `401 Unauthorized` mesmo com o token certo | cabeçalho errado (`Authorization: Bearer <token>`), token expirado, ou escopo insuficiente | `curl -v` e confira o cabeçalho enviado |
| `429 Too Many Requests` | você estourou o limite de chamadas | leia os cabeçalhos `RateLimit-*` / `Retry-After` e espere |

**Quando nada resolver, colete evidência antes de pedir ajuda:**

```bash
curl -v https://api.exemplo.com/recurso 2>&1 | tee debug.log
```
*`-v` (verbose) mostra a negociação TLS, os cabeçalhos enviados e recebidos, e o protocolo
usado. `tee` mostra na tela e grava no arquivo.*

```bash
curl -s -o /dev/null -w '%{http_code} %{time_total}s http/%{http_version}\n' https://api.exemplo.com/
# esperado: 200 0.184s http/2
```
*Diagnóstico em uma linha: status, tempo total e versão do protocolo.*

> **Antes de postar um log em qualquer lugar, revise-o.** `curl -v` imprime o cabeçalho
> `Authorization` inteiro. Já vi token de produção vazar em issue pública exatamente assim.

---

## 19. Checklist: ambiente pronto

Rode um por linha. Todos devem passar antes de ir para
[04-como-comecar.md](04-como-comecar.md).

```bash
curl --version              # curl 8.x, com HTTP2 em Features
jq --version                # jq-1.7.x
curl -s https://api.github.com/repos/nodejs/node | jq -r .full_name
                            # esperado: nodejs/node
curl -s -o /dev/null -w '%{http_code}\n' https://httpbin.org/status/200
                            # esperado: 200
```

Se você vai **construir** APIs, adicione:
```bash
node --version              # v24.x
npm --version               # 11.x
code --version              # 1.10x
npx @redocly/cli --version  # 1.x (baixa na hora, é normal demorar)
docker --version            # opcional
```

E, no editor: crie um `teste.http` com `GET https://api.github.com`, e confirme que o
*Send Request* aparece e funciona.

**Trilha de leitura pura:** basta o navegador. Você não precisa de nada da lista acima.

---

## Autoteste

1. Como fazer sua primeira chamada de API sem instalar absolutamente nada? Cite duas formas.
2. Por que `curl` falha no PowerShell, e quais são as três soluções?
3. Qual é o comando que mostra status, tempo e versão do protocolo numa linha?
4. Por que `sudo npm install -g` é má ideia? Dê dois motivos distintos.
5. Sua empresa inspeciona TLS. Qual variável resolve e qual **não** se deve usar — e por quê?
6. Por que `NO_PROXY` precisa incluir `localhost`?
7. Onde uma chave de API **nunca** deve ficar? Cite três lugares e a alternativa correta para cada.
8. Por que HTTP/3 pode falhar especificamente na rede da sua empresa?
9. O que fazer, além de desinstalar as ferramentas, ao devolver um computador?

---

### Fontes consultadas (11/08/2026)

- Node.js Release Working Group — cronograma de LTS — https://github.com/nodejs/Release
- NodeSource — *Node.js 24 Becomes LTS* — https://nodesource.com/blog/nodejs-24-becomes-lts
- endoflife.date — Node.js — https://endoflife.date/nodejs
- curl — documentação oficial — https://curl.se/docs/
- jq — manual — https://jqlang.github.io/jq/manual/
- Bruno — downloads — https://www.usebruno.com/downloads
- Docker — guia de instalação — https://docs.docker.com/engine/install/
