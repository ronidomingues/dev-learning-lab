# 03 · Manual de instalação

`Nível: iniciante` · `Atualizado: 11/08/2026`
`Testado contra: Salesforce CLI 2.146.3 · Node.js 22.17 LTS · Summer '26 (API 67.0)`

Este é um manual de campo. Siga na ordem. **Cada passo tem um comando, o que ele faz,
uma verificação com a saída esperada, e o que fazer se a saída for diferente.**

Salesforce em si **não se instala** — a plataforma roda na nuvem da Salesforce e você a
acessa pelo navegador. O que se instala é o **ferramental de desenvolvimento local**.
Se você é administrador e não vai escrever código, precisa apenas da §2 (criar a org)
e pode pular para [04-como-comecar.md](04-como-comecar.md).

---

## Índice

1. [Sem instalar nada — comece hoje](#1-sem-instalar-nada--comece-hoje)
2. [Criar a org gratuita (obrigatório para todos)](#2-criar-a-org-gratuita-obrigatório-para-todos)
3. [Node.js](#3-nodejs)
4. [Salesforce CLI (`sf`)](#4-salesforce-cli-sf)
5. [Git](#5-git)
6. [Java (JDK) — o passo que todo mundo esquece](#6-java-jdk--o-passo-que-todo-mundo-esquece)
7. [VS Code + Salesforce Extension Pack](#7-vs-code--salesforce-extension-pack)
8. [Salesforce Code Analyzer (opcional, recomendado)](#8-salesforce-code-analyzer-opcional-recomendado)
9. [Conectar a CLI à sua org](#9-conectar-a-cli-à-sua-org)
10. [Docker / container (alternativa)](#10-docker--container-alternativa)
11. [PATH e variáveis de ambiente](#11-path-e-variáveis-de-ambiente)
12. [Permissões — por que não usar `sudo`](#12-permissões--por-que-não-usar-sudo)
13. [Rede corporativa: proxy, certificado, firewall](#13-rede-corporativa-proxy-certificado-firewall)
14. [Convivência de versões](#14-convivência-de-versões)
15. [Reprodutibilidade](#15-reprodutibilidade)
16. [Atualizar e voltar atrás](#16-atualizar-e-voltar-atrás)
17. [Desinstalar por completo](#17-desinstalar-por-completo)
18. [Solução de problemas](#18-solução-de-problemas)
19. [Checklist final: ambiente pronto](#19-checklist-final-ambiente-pronto)

---

## 1. Sem instalar nada — comece hoje

Leia esta seção antes de qualquer outra. Se o seu objetivo hoje é **entender e experimentar**,
você não precisa instalar coisa alguma, em nenhum sistema operacional.

| Opção | O que é | Custo | Limite |
|---|---|---|---|
| **Trailhead + Playground** | Plataforma oficial de ensino, com uma org descartável embutida em cada exercício | Grátis | Playground expira; não serve para projeto real |
| **Developer Console** | Editor de Apex/SOQL dentro da própria org, no navegador (Engrenagem → *Developer Console*) | Grátis | Editor pobre, sem Git, sem LWC moderno |
| **Code Builder** | VS Code completo rodando no navegador, com a CLI já instalada | Incluído em orgs elegíveis; há limite de horas | Depende da edição da org |
| **GitHub Codespaces** | Container Linux na nuvem; você instala a CLI dentro dele | Cota gratuita mensal para contas pessoais | Consome cota |

**Recomendação:** faça a §2 (criar a org — é obrigatória de qualquer jeito, e é web),
brinque no Developer Console por um dia, e só então volte e instale o ferramental local.
A instalação completa é um investimento de ~1 hora que só se paga quando você começa a
escrever código de verdade.

> **Opinião profissional:** a longo prazo, o ferramental local não é opcional. Quem fica
> no Developer Console não consegue usar Git, não consegue revisar código, não consegue
> automatizar deploy e acaba desenvolvendo direto em produção — que é a pior prática
> possível nesta plataforma. Instale, mas não precisa ser hoje.

---

## 2. Criar a org gratuita (obrigatório para todos)

Uma **org** (organização) é a sua instância de Salesforce: seus dados, sua configuração,
seu código. A **Developer Edition (DE)** é gratuita, permanente e não pede cartão de crédito.

### Passo 2.1 — Cadastro

1. Acesse **https://developer.salesforce.com/signup**
2. Preencha o formulário. Campos que importam:
   - **Email**: use um endereço que você controle e não vá perder. Ele fica ligado a essa
     org para sempre e **não pode ser reaproveitado em outra org DE**.
     Truque: `voce+sf1@gmail.com` funciona e é tratado como e-mail distinto.
   - **Username**: precisa ter **formato de e-mail**, mas **não precisa ser um e-mail real**.
     Convenção: `seunome@curso.dev.2026`. Ele é global e único em toda a Salesforce.
     Anote-o — é com ele que você faz login, não com o e-mail.
   - **Country/Region**: escolha o seu; define fuso horário e formato de moeda padrão.
3. Confirme o e-mail que chegará em minutos e defina a senha.

**Verificação:** você chega numa tela chamada *Setup* ou numa home de app Lightning.
No canto superior direito aparece seu nome.

**Se não chegar o e-mail:** confira a caixa de spam. Se em 15 minutos não vier, é quase
sempre porque aquele e-mail já foi usado em outra org DE — tente com `+sf2`.

### Passo 2.2 — Anote os três dados que você vai usar sempre

```text
URL de login : https://login.salesforce.com
Username     : seunome@curso.dev.2026
Senha        : (a que você definiu)
```

> A URL da sua org será algo como `https://orgfarm-abc123.develop.my.salesforce.com`.
> Chama-se **My Domain**. Você pode logar por ela ou pelo `login.salesforce.com`.

### Passo 2.3 — O que você ganhou

Uma org Developer Edition inclui, sem custo e sem prazo de validade:

| Recurso | Cota |
|---|---|
| Licenças de usuário | 2 (Salesforce) + licenças de plataforma extras |
| Armazenamento de dados | ~5 MB (é pouco — é para aprender, não para operar) |
| Armazenamento de arquivos | ~20 MB |
| Chamadas de API | 15.000 por período de 24 h |
| Objetos customizados | 400 |
| Apex, LWC, Flow, relatórios | Sem restrição funcional relevante |
| Dev Hub (para scratch orgs) | Ativável — dá 3 scratch orgs ativas e 6 criações/dia |

**Limitação importante e honesta:** a DE tem **5 MB de dados**. Você vai estourar isso se
carregar volume. Para testar com volume, use scratch orgs (§9.4) ou uma **trial org**
(30 dias, edição Enterprise, sem cartão) em https://www.salesforce.com/form/signup/freetrial-sales/

### Passo 2.4 — Ativar o Dev Hub (faça agora, é 1 minuto)

Necessário se você quiser usar **scratch orgs** — orgs descartáveis criadas por comando,
que são a forma moderna de desenvolver.

1. Na org, clique na engrenagem → **Setup**.
2. Na *Quick Find* (busca rápida à esquerda), digite `Dev Hub`.
3. Clique em **Dev Hub** e ligue **Enable Dev Hub**.

**Verificação:** o toggle fica verde/ativado. **Atenção: essa ação é irreversível** —
não há botão de desligar. Em uma org DE de estudo, isso não tem consequência ruim.

---

## 3. Node.js

A Salesforce CLI é distribuída como pacote Node. Você precisa do Node **apenas** se for
instalar a CLI via npm — os instaladores nativos (§4, método B) trazem o Node embutido.

**Versão recomendada em 11/08/2026:** Node.js **24.x** — é o **Active LTS** desde
28/10/2025 (entra em Maintenance em 20/10/2026, fim de vida em 30/04/2028).
O Node **22.x** está em **Maintenance LTS** e continua funcionando com a CLI; use-o apenas
se algo no seu ambiente exigir. **Evite** Node 18 e anteriores (fora de suporte) e evite
versões ímpares (23, 25) — são de curta duração.

### 3.1 Linux — família Debian/Ubuntu

O pacote `nodejs` dos repositórios do Debian/Ubuntu costuma estar **desatualizado**.
Use o repositório oficial NodeSource ou, melhor, um gerenciador de versões (§14).

**Método recomendado: `nvm`** (permite ter várias versões e não exige `sudo`)

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
```
*Baixa e instala o nvm no seu diretório pessoal (`~/.nvm`).*

Feche e reabra o terminal (ou `source ~/.bashrc`), depois:

```bash
nvm install --lts
```
*Instala a versão LTS mais recente do Node e a ativa.*

**Verificação:**
```bash
node --version && npm --version
# esperado: v22.x.x (ou superior)
#           10.x.x (ou superior)
```

**Se der `nvm: command not found`:** o instalador adiciona linhas ao `~/.bashrc`, mas se
você usa **zsh** ou **fish**, elas foram para o arquivo errado. Copie o bloco `export NVM_DIR=...`
do fim do `~/.bashrc` para o `~/.zshrc`. Ver §11.

**Método alternativo (sem nvm):**
```bash
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt-get install -y nodejs
```
*Adiciona o repositório oficial da NodeSource e instala o Node 22.*

### 3.2 Linux — família Fedora/RHEL/Rocky

```bash
sudo dnf module install nodejs:22/common
```
*Instala o Node 22 pelo sistema de módulos do dnf.*

Ou, preferencialmente, o mesmo `nvm` da §3.1 (funciona igual).

**Verificação:** idêntica à §3.1.

### 3.3 macOS (Intel e Apple Silicon)

**Método recomendado: Homebrew + nvm**

Se você não tem Homebrew:
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```
*Instala o Homebrew, o gerenciador de pacotes de facto do macOS.*

> Em **Apple Silicon** (M1–M4) o Homebrew instala em `/opt/homebrew`; em **Intel**, em
> `/usr/local`. O instalador diz, ao final, quais linhas adicionar ao seu perfil. **Adicione-as**,
> senão `brew` não será encontrado. Ver §11.

```bash
brew install nvm
mkdir -p ~/.nvm
```
*Instala o nvm e cria seu diretório de trabalho.*

Adicione ao `~/.zshrc` (o shell padrão do macOS desde o Catalina):
```bash
export NVM_DIR="$HOME/.nvm"
[ -s "$(brew --prefix)/opt/nvm/nvm.sh" ] && . "$(brew --prefix)/opt/nvm/nvm.sh"
```

Reabra o terminal e:
```bash
nvm install --lts
```

**Verificação:**
```bash
node --version
# esperado: v22.x.x
arch
# em Apple Silicon esperado: arm64  (se disser i386, você está sob Rosetta — ver abaixo)
```

**Se `arch` disser `i386` num Mac M-series:** seu Terminal está rodando sob Rosetta.
Feche-o, vá em *Finder → Aplicativos → Utilitários → Terminal → Obter Informações* e
**desmarque** "Abrir usando Rosetta". Rodar Node x86 emulado em ARM funciona, mas é
lento e causa erros estranhos em módulos nativos.

### 3.4 Windows

**Decisão primeiro: nativo ou WSL2?**

| | Windows nativo | **WSL2 (recomendado)** |
|---|---|---|
| Facilidade inicial | Maior | Exige um passo a mais |
| Compatibilidade com tutoriais | Média (comandos são de Linux/macOS) | Total |
| Velocidade de `npm install` | Mais lenta | Mais rápida |
| Problemas com caminho longo / antivírus | Comuns | Raros |
| Integração com VS Code | Boa | Excelente (extensão *WSL*) |

> **Recomendação:** use **WSL2**. O ecossistema Salesforce assume Unix em quase toda
> documentação de comunidade. A única razão para usar Windows nativo é política de TI
> que proíbe WSL.

**Instalar o WSL2** (PowerShell **como administrador**):
```powershell
wsl --install -d Ubuntu-24.04
```
*Instala o WSL2 com Ubuntu 24.04 LTS. Reinicie quando pedir.*

**Verificação:**
```powershell
wsl -l -v
# esperado: uma linha com  Ubuntu-24.04    Running    2
#           o "2" é a versão do WSL — se disser 1, rode: wsl --set-version Ubuntu-24.04 2
```

Depois, **dentro do Ubuntu**, siga a §3.1 (Debian/Ubuntu) normalmente.

**Windows nativo, se for o caso** — via winget (já vem no Windows 10 21H1+ e no 11):
```powershell
winget install OpenJS.NodeJS.LTS
```
*Instala o Node.js LTS com o gerenciador de pacotes oficial da Microsoft.*

Feche e reabra o PowerShell (o PATH só é relido em processo novo) e verifique:
```powershell
node --version
# esperado: v22.x.x
```

Para múltiplas versões no Windows nativo, use `nvm-windows`
(https://github.com/coreybutler/nvm-windows) — **projeto diferente** do `nvm` do Unix,
com sintaxe parecida mas não idêntica.

---

## 4. Salesforce CLI (`sf`)

A CLI é a ferramenta central: cria orgs, faz deploy, roda testes, consulta dados, gera código.

> **Aviso de nomenclatura — leia, poupa confusão.** Existiram dois executáveis:
> **`sfdx`** (antigo, pacote npm `sfdx-cli`) e **`sf`** (atual, pacote `@salesforce/cli`).
> O pacote `sfdx-cli` está **descontinuado e sem atualizações**. Use `@salesforce/cli`.
> Ele instala os dois binários — `sf` e um `sfdx` de compatibilidade — mas **escreva `sf`**.
> Tutoriais com `sfdx force:source:push` são de antes de 2023; o equivalente hoje é
> `sf project deploy start`. Se você já tinha o `sfdx-cli`, **desinstale antes** (§17).

**Versão em 11/08/2026:** 2.146.3.

### 4.1 Método A — npm (recomendado se você já tem Node)

Funciona igual em Linux, macOS, WSL e Windows.

```bash
npm install -g @salesforce/cli
```
*Instala a CLI globalmente a partir do registro npm.*

**Verificação:**
```bash
sf --version
# esperado: @salesforce/cli/2.146.3 linux-x64 node-v22.17.0
#           (número exato varia; o que importa é começar com @salesforce/cli/2.1)
```

**Se der `EACCES: permission denied`:** você está tentando escrever no diretório global do
sistema. **Não use `sudo`** — leia a §12 e corrija a causa.

**Se der `command not found: sf`:** o diretório de binários globais do npm não está no PATH.
Ver §11.

### 4.2 Método B — instalador nativo (recomendado se você não quer Node)

Traz o Node embutido; não depende de instalação prévia.

| Sistema | Como |
|---|---|
| **Windows** | Baixe o `.exe` de 64 bits em https://developer.salesforce.com/tools/salesforcecli e execute |
| **macOS** | Baixe o `.pkg` (há um para Apple Silicon e um para Intel) na mesma página |
| **Linux (tar.xz)** | Baixe o tarball, extraia e ponha `bin/` no PATH |

Linux por tarball, passo a passo:
```bash
mkdir -p ~/cli/sf && cd ~/cli/sf
wget https://developer.salesforce.com/media/salesforce-cli/sf/channels/stable/sf-linux-x64.tar.xz
tar xJf sf-linux-x64.tar.xz --strip-components 1
```
*Cria a pasta, baixa o pacote oficial e extrai já sem o diretório-raiz redundante.*

```bash
echo 'export PATH=~/cli/sf/bin:$PATH' >> ~/.bashrc && source ~/.bashrc
```
*Coloca o binário no PATH da sua sessão e das futuras.*

**Verificação:** `sf --version` → mesma saída da §4.1.

### 4.3 Método C — Homebrew (macOS/Linux)

```bash
brew install --cask sf
```
*Instala a CLI pelo Homebrew. Conveniente, mas costuma ficar alguns dias atrás do npm.*

### 4.4 Qual método usar

| Situação | Use |
|---|---|
| Você já tem Node e vai desenvolver LWC | **A (npm)** |
| Você é admin e só quer a CLI | **B (instalador nativo)** |
| Você usa Homebrew para tudo | **C** |
| CI/CD, pipeline | **A**, com versão fixada: `npm i -g @salesforce/cli@2.146.3` |
| Windows com política de TI restritiva | **B** (não exige permissão de escrita em diretório global npm) |

**Nunca misture métodos.** Ter a CLI por npm *e* por instalador na mesma máquina causa o
clássico "atualizei mas a versão não muda" — porque o PATH está pegando a outra cópia.

---

## 5. Git

### Linux Debian/Ubuntu
```bash
sudo apt-get update && sudo apt-get install -y git
```

### Linux Fedora/RHEL
```bash
sudo dnf install -y git
```

### macOS
```bash
brew install git
```
*O macOS já traz um Git via Command Line Tools, mas geralmente antigo. O do brew é atual.*

### Windows
```powershell
winget install Git.Git
```
*No WSL, use o comando do Ubuntu (§Debian) dentro do WSL — não o do Windows.*

**Verificação (todos):**
```bash
git --version
# esperado: git version 2.4x.x (2.30 ou superior serve)
```

**Configuração mínima obrigatória:**
```bash
git config --global user.name "Seu Nome"
git config --global user.email "voce@exemplo.com"
git config --global init.defaultBranch main
```
*Identidade dos commits e nome padrão do branch inicial.*

**Windows nativo — trate as quebras de linha antes que elas te mordam:**
```bash
git config --global core.autocrlf input
```
*Evita que arquivos de metadados Salesforce (XML) apareçam como "modificados por inteiro"
por causa de CRLF. É o motivo nº 1 de diff sujo em times mistos Windows/macOS.*

---

## 6. Java (JDK) — o passo que todo mundo esquece

**Por que é obrigatório:** o *Apex Language Server* (o que dá autocomplete, "ir para
definição" e erro em tempo real no VS Code) é escrito em Java. Sem JDK, a extensão de
Apex carrega e falha silenciosamente ou com uma mensagem críptica.

**Versão:** JDK **17 LTS** ou **21 LTS**. Recomendo 21. Use uma distribuição OpenJDK
(Temurin/Adoptium, Zulu, Corretto, Microsoft Build) — todas gratuitas.
**Evite o Oracle JDK** salvo se sua empresa já tiver a licença: os termos de uso comercial
mudaram e podem gerar cobrança.

### Linux Debian/Ubuntu
```bash
sudo apt-get install -y openjdk-21-jdk
```

### Linux Fedora/RHEL
```bash
sudo dnf install -y java-21-openjdk-devel
```

### macOS
```bash
brew install --cask temurin@21
```

### Windows
```powershell
winget install EclipseAdoptium.Temurin.21.JDK
```

**Verificação (todos):**
```bash
java -version
# esperado (na saída de erro padrão, é normal):
# openjdk version "21.0.x" 2026-xx-xx
```

### 6.1 Descobrir o caminho do JDK (você vai precisar dele na §7)

```bash
# Linux
readlink -f "$(which java)" | sed 's|/bin/java||'
# esperado: /usr/lib/jvm/java-21-openjdk-amd64

# macOS
/usr/libexec/java_home -v 21
# esperado: /Library/Java/JavaVirtualMachines/temurin-21.jdk/Contents/Home
```

```powershell
# Windows
Get-ChildItem "C:\Program Files\Eclipse Adoptium"
# esperado: uma pasta jdk-21.0.x-hotspot
```

Guarde esse caminho. **Ele não deve terminar em `/bin`.**

---

## 7. VS Code + Salesforce Extension Pack

### 7.1 Instalar o VS Code

| Sistema | Comando |
|---|---|
| Debian/Ubuntu | Baixe o `.deb` em https://code.visualstudio.com e `sudo apt install ./code_*.deb` |
| Fedora/RHEL | `sudo dnf install code` (após adicionar o repo da Microsoft) |
| macOS | `brew install --cask visual-studio-code` |
| Windows | `winget install Microsoft.VisualStudioCode` |

**Verificação:**
```bash
code --version
# esperado: 1.10x.x  (três linhas: versão, commit, arquitetura)
```

### 7.2 Instalar as extensões

```bash
code --install-extension salesforce.salesforcedx-vscode
```
*Instala o **Salesforce Extension Pack**: Apex, LWC, SOQL, Visualforce, Lightning, Core.*

Recomendadas junto:
```bash
code --install-extension salesforce.sfdx-code-analyzer-vscode
code --install-extension redhat.vscode-xml
```
*Analisador estático de código Salesforce e suporte a XML (todo metadado é XML).*

**Se você usa WSL:** instale também a extensão `ms-vscode-remote.remote-wsl` **no Windows**,
e instale o Extension Pack **dentro do WSL** (o VS Code pergunta; aceite "Install in WSL").
Extensão instalada no lado errado é a causa de metade dos problemas de WSL.

### 7.3 Apontar o JDK (o passo crítico)

1. No VS Code: `Ctrl+,` (ou `Cmd+,`) para abrir *Settings*.
2. Busque por `salesforcedx-vscode-apex.java.home`.
3. Cole o caminho obtido na §6.1.

Ou edite o `settings.json` diretamente (`Ctrl+Shift+P` → *Preferences: Open User Settings (JSON)*):

```json
{
  "salesforcedx-vscode-apex.java.home": "/usr/lib/jvm/java-21-openjdk-amd64"
}
```

> No Windows, escape as barras: `"C:\\Program Files\\Eclipse Adoptium\\jdk-21.0.4-hotspot"`.

**Verificação:** abra qualquer arquivo `.cls`. Na barra inferior deve aparecer, por alguns
segundos, *"Indexing Apex files"* e depois sumir sem erro. Digite `System.` dentro de um
método — o autocomplete deve abrir. Se não abrir, veja §18.

---

## 8. Salesforce Code Analyzer (opcional, recomendado)

Analisador estático oficial que roda PMD, ESLint, RetireJS e regras de segurança de fluxo
em cima do seu código. Vale instalar desde o primeiro dia — ensina boas práticas por osmose.

```bash
sf plugins install code-analyzer
```
*Instala o plugin oficial de análise estática na sua CLI.*

**Verificação:**
```bash
sf plugins
# esperado: uma lista contendo  code-analyzer 5.x.x
```

Uso, mais tarde:
```bash
sf code-analyzer run --workspace force-app --view detail
```
*Analisa a pasta de código e mostra as violações em detalhe.*

**Requer o JDK da §6.** Sem Java, o motor PMD não roda.

---

## 9. Conectar a CLI à sua org

### 9.1 Autorizar (login por navegador)

```bash
sf org login web --alias devorg --set-default
```
*Abre o navegador para você logar; guarda o token com o apelido `devorg` e o torna padrão.*

O navegador abre em `login.salesforce.com`. Entre com **username e senha da §2.2**.
Autorize o acesso. A aba diz que você pode fechá-la.

**Verificação:**
```bash
sf org list
```
```text
# esperado, algo como:
#  ALIAS    USERNAME                   ORG ID              STATUS
#  devorg   seunome@curso.dev.2026     00Dxx0000000000EAA  Connected
```

**Se o navegador não abrir** (servidor sem interface gráfica, WSL sem browser configurado):
```bash
sf org login device --alias devorg --set-default
```
*Mostra um código na tela; você abre a URL indicada em qualquer outro dispositivo e digita o código.*

**Se der `This site can't be reached — localhost:1717`:** o login web sobe um servidor
local temporário nessa porta. Firewall ou outro processo está bloqueando. Use
`--port 1719` ou o método `device` acima.

### 9.2 Testar de verdade

```bash
sf org display --target-org devorg
```
*Mostra os dados da conexão: instância, ID da org, token, versão da API.*

```bash
sf data query --query "SELECT Id, Name FROM Account LIMIT 5" --target-org devorg
```
*Executa uma consulta SOQL. Numa org DE nova, retorna as contas de exemplo.*

```text
# esperado:
#  ID                  NAME
#  ───────────────────────────────────
#  001xx000003DGb2AAG  Edge Communications
#  ...
#  Total number of records retrieved: 5.
```

Se isso funcionou, **seu ambiente está conectado**. É o marco mais importante deste arquivo.

### 9.3 Criar um projeto local

```bash
sf project generate --name meu-primeiro-projeto --template standard
cd meu-primeiro-projeto
```
*Cria a estrutura padrão de projeto Salesforce DX no diretório atual.*

**Verificação:**
```bash
ls
# esperado: README.md  config  force-app  package.json  sfdx-project.json  scripts
```

### 9.4 (Opcional) Primeira scratch org

Requer Dev Hub ativado (§2.4) e que a org autorizada na §9.1 seja o Dev Hub.

```bash
sf org create scratch --definition-file config/project-scratch-def.json \
  --alias scratch1 --duration-days 7 --set-default
```
*Cria uma org descartável de 7 dias a partir do arquivo de definição do projeto.*

**Verificação:** o comando termina com `Successfully created scratch org: 00Dxx...`.

**Cotas na Developer Edition:** 3 scratch orgs ativas ao mesmo tempo e 6 criações por dia.
Duração: 1 a 30 dias, padrão 7. Estourou? Delete uma: `sf org delete scratch -o scratch1`.

---

## 10. Docker / container (alternativa)

Útil para CI, para não sujar sua máquina, ou quando a TI não deixa instalar nada.

`Dockerfile`:
```dockerfile
FROM node:22-bookworm-slim

# JDK para o Apex Language Server e o Code Analyzer
RUN apt-get update \
 && apt-get install -y --no-install-recommends openjdk-21-jdk-headless git ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# Versão fixada: reprodutibilidade vale mais que estar na última
RUN npm install -g @salesforce/cli@2.146.3

WORKDIR /work
CMD ["bash"]
```

```bash
docker build -t sfdev:2026-08 .
docker run -it --rm -v "$PWD":/work -p 1717:1717 sfdev:2026-08
```
*Constrói a imagem e abre um shell com seu diretório montado. A porta 1717 é publicada
para o login web funcionar de dentro do container.*

**Verificação, dentro do container:** `sf --version` e `java -version`.

> Dentro de container, prefira `sf org login device` — é mais confiável que o fluxo de
> navegador. Para CI, use **JWT bearer flow** com certificado, nunca senha. Ver
> [18-devops-e-alm.md](18-devops-e-alm.md).

---

## 11. PATH e variáveis de ambiente

**O que é o PATH:** uma lista de diretórios que o shell percorre, em ordem, procurando o
programa que você digitou. Se o diretório do `sf` não está lá, o shell diz "command not found"
mesmo com o arquivo instalado no disco.

### Ver o PATH

```bash
echo $PATH          # Linux, macOS, WSL
```
```powershell
$env:Path -split ';'   # Windows PowerShell
```

### Descobrir qual binário está sendo usado

```bash
which -a sf     # Linux/macOS — o -a mostra TODAS as ocorrências
```
```powershell
Get-Command sf -All   # Windows
```
*Se aparecer mais de uma linha, você tem instalações duplicadas. A primeira ganha. Ver §17.*

### Descobrir onde o npm põe binários globais

```bash
npm config get prefix
# típico com nvm: /home/voce/.nvm/versions/node/v22.17.0
# típico sem nvm: /usr/local  (ou /usr — aí começam os problemas de permissão)
```
Os binários ficam em `<prefix>/bin`.

### Onde colocar a linha de PATH, por shell

| Shell | Arquivo | Como saber se é o seu |
|---|---|---|
| bash | `~/.bashrc` (Linux) · `~/.bash_profile` (macOS) | `echo $SHELL` → `/bin/bash` |
| zsh | `~/.zshrc` | `echo $SHELL` → `/bin/zsh` (padrão do macOS) |
| fish | `~/.config/fish/config.fish` | `echo $SHELL` → `/usr/bin/fish` |
| PowerShell | `$PROFILE` (`notepad $PROFILE`) | — |

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```
*Adiciona o diretório ao PATH permanentemente e recarrega o perfil na sessão atual.*

> **Por que "não pegou" antes de reabrir o terminal:** variáveis de ambiente são copiadas
> do processo pai para o filho **no momento em que o filho nasce**. Um terminal já aberto
> tem uma cópia antiga do PATH; editar o arquivo de perfil não altera processos vivos.
> `source` relê o arquivo no processo atual e resolve. Isso não é peculiaridade do
> Salesforce — é como processos funcionam em Unix desde os anos 70.

### Variáveis específicas da Salesforce CLI

| Variável | Para quê |
|---|---|
| `SF_LOG_LEVEL=debug` | Ligar log detalhado ao investigar um erro |
| `SF_DISABLE_TELEMETRY=true` | Desligar telemetria |
| `SF_AUTOUPDATE_DISABLE=true` | Impedir auto-atualização (essencial em CI) |
| `SF_USE_GENERIC_UNIX_KEYCHAIN=true` | Linux sem keychain gráfico: guarda o token em arquivo cifrado |
| `SF_TARGET_ORG` | Org padrão sem passar `-o` toda vez |
| `HTTP_PROXY` / `HTTPS_PROXY` / `NO_PROXY` | Rede corporativa — ver §13 |
| `NODE_EXTRA_CA_CERTS` | Certificado interno — ver §13 |

**Linux headless — a variável que salva:** sem ambiente gráfico, a CLI tenta usar
`libsecret` e falha com `Cannot read property 'getPassword' of undefined` ou similar.
```bash
echo 'export SF_USE_GENERIC_UNIX_KEYCHAIN=true' >> ~/.bashrc && source ~/.bashrc
```

---

## 12. Permissões — por que não usar `sudo`

Se `npm install -g` deu `EACCES`, a saída óbvia parece ser `sudo npm install -g`. **Não faça.**

**Por que é problema, de verdade:**

1. Os arquivos instalados passam a pertencer ao `root`. Toda atualização futura vai exigir
   `sudo` também, e um dia você vai esquecer e ficar com uma instalação meio-root, meio-sua
   — que quebra de formas difíceis de diagnosticar.
2. `npm install` executa **scripts arbitrários de pós-instalação** definidos pelos pacotes.
   Rodar isso como root dá a esses scripts poder total sobre a máquina. É um vetor real de
   ataque de cadeia de suprimentos, não teoria.
3. O cache do npm (`~/.npm`) fica com arquivos de root, e depois seu usuário não consegue
   mais escrever nele — gerando erros de permissão em instalações que nem usam `-g`.

**As três soluções corretas, em ordem de preferência:**

**A) Use um gerenciador de versões (melhor).** Com `nvm`, `fnm`, `mise` ou `asdf`, o Node e
todos os pacotes globais ficam no seu diretório pessoal. O problema deixa de existir.

**B) Mude o prefixo global do npm para dentro da sua casa:**
```bash
mkdir -p ~/.npm-global
npm config set prefix ~/.npm-global
echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.bashrc
source ~/.bashrc
```
*Passa a instalar pacotes globais no seu diretório, sem precisar de privilégio.*

**C) Use o instalador nativo da CLI (§4.2)**, que não depende do npm.

**Se você já rodou `sudo npm`** e quer consertar:
```bash
sudo chown -R $(whoami) ~/.npm ~/.config
```
*Devolve a você a posse do cache e da configuração do npm.*

---

## 13. Rede corporativa: proxy, certificado, firewall

### 13.1 Proxy

```bash
export HTTP_PROXY="http://usuario:senha@proxy.empresa.com:8080"
export HTTPS_PROXY="$HTTP_PROXY"
export NO_PROXY="localhost,127.0.0.1"
```
*A CLI e o npm respeitam essas variáveis. `NO_PROXY` com localhost é **obrigatório**,
senão o login web (que usa `localhost:1717`) tenta passar pelo proxy e falha.*

Para o npm, adicionalmente:
```bash
npm config set proxy http://proxy.empresa.com:8080
npm config set https-proxy http://proxy.empresa.com:8080
```

> Se a senha do proxy tiver caracteres especiais (`@`, `:`, `#`), codifique-os em
> percent-encoding: `@` → `%40`. É a causa nº 1 de "proxy configurado e mesmo assim falha".

### 13.2 Certificado interno (TLS interception)

Empresas que inspecionam TLS substituem o certificado dos sites por um emitido pela CA
interna. Node e a CLI rejeitam, com `UNABLE_TO_VERIFY_LEAF_SIGNATURE` ou
`SELF_SIGNED_CERT_IN_CHAIN`.

**Correto:**
```bash
export NODE_EXTRA_CA_CERTS=/caminho/para/ca-empresa.pem
```
*Adiciona a CA da empresa às autoridades confiáveis, sem desligar a verificação.*

**Errado, e por quê:**
```bash
export NODE_TLS_REJECT_UNAUTHORIZED=0   # NÃO FAÇA ISSO
```
Isso desliga a verificação de TLS para **todas** as conexões daquele processo — inclusive
as que baixam código que você vai executar. Resolve o sintoma criando um buraco real.
Use apenas para diagnosticar por 30 segundos, nunca em arquivo de perfil.

### 13.3 Firewall — domínios e portas a liberar

| Destino | Porta | Para quê |
|---|---|---|
| `*.salesforce.com` | 443 | Plataforma e APIs |
| `*.force.com`, `*.my.salesforce.com` | 443 | My Domain, Sites, Experience Cloud |
| `*.lightning.force.com` | 443 | Interface Lightning |
| `*.visualforce.com` | 443 | Páginas Visualforce e iframes de LWC |
| `registry.npmjs.org` | 443 | Instalação via npm |
| `developer.salesforce.com` | 443 | Download da CLI e plugins |
| `localhost` | 1717 | Callback do `sf org login web` |

A Salesforce publica as faixas de IP e o status das instâncias em
**https://status.salesforce.com** — é a página a mandar para a equipe de rede.

---

## 14. Convivência de versões

### Node — várias versões na mesma máquina

```bash
nvm install 20 && nvm install 22
nvm use 22            # nesta sessão
nvm alias default 22  # padrão para sessões futuras
```

Por projeto, crie um `.nvmrc`:
```bash
echo "22" > .nvmrc
nvm use    # lê o .nvmrc do diretório atual
```

Alternativas modernas: **fnm** (mais rápido), **mise** e **asdf** (gerenciam Node, Java e
outras ferramentas no mesmo arquivo `.tool-versions`).

### Salesforce CLI — versão fixa por projeto

A CLI é uma só na máquina. Se você precisa de versões diferentes por projeto, instale-a
como dependência de desenvolvimento e chame via `npx`:

```bash
npm install --save-dev @salesforce/cli@2.146.3
npx sf --version
```
*Fixa a versão no `package.json` do projeto; o `npx` usa a local em vez da global.*

### Múltiplas orgs ao mesmo tempo

Não há conflito: a CLI guarda todas as autorizações e você escolhe por alias.
```bash
sf org login web --alias prod
sf org login web --alias uat
sf config set target-org=uat        # padrão do projeto atual
sf project deploy start -o prod     # sobrescreve pontualmente
```

> **Prática que evita desastre:** nunca deixe uma org de **produção** como padrão. Um
> `sf project deploy start` distraído sem `-o` já derrubou muita gente.

### Java — várias versões

```bash
# Linux Debian/Ubuntu
sudo update-alternatives --config java
```
```bash
# macOS
export JAVA_HOME=$(/usr/libexec/java_home -v 21)
```
No VS Code, o que vale é a configuração `salesforcedx-vscode-apex.java.home` (§7.3),
que é independente do `java` do PATH — o que é bom: você pode ter Java 8 no PATH para
outro projeto e Java 21 para o Salesforce.

---

## 15. Reprodutibilidade

Comprometa no Git, na raiz do projeto:

| Arquivo | Conteúdo | Garante |
|---|---|---|
| `.nvmrc` | `22` | Todo mundo no mesmo Node |
| `package.json` + `package-lock.json` | deps travadas, incl. `@salesforce/cli` | Mesmas versões de ferramenta |
| `sfdx-project.json` | `sourceApiVersion: "67.0"` | Mesmo contrato de API |
| `config/project-scratch-def.json` | edição e features da scratch org | Orgs de dev idênticas |
| `.forceignore` | o que nunca subir/descer | Deploys previsíveis |
| `Dockerfile` (opcional) | imagem com versões fixas | Igualdade entre local e CI |

Exemplo mínimo de `sfdx-project.json`:
```json
{
  "packageDirectories": [{ "path": "force-app", "default": true }],
  "name": "meu-projeto",
  "namespace": "",
  "sfdcLoginUrl": "https://login.salesforce.com",
  "sourceApiVersion": "67.0"
}
```

> **`sourceApiVersion` é uma decisão, não um detalhe.** Ele define qual contrato da
> plataforma seu código assume. Subir de 66.0 para 67.0 **muda o comportamento do seu Apex**
> (user mode passa a ser o padrão — ver [15-apex.md](15-apex.md) §9). Mude de propósito,
> com testes, nunca por acidente.

---

## 16. Atualizar e voltar atrás

### Atualizar a CLI

```bash
sf update              # se instalada pelo instalador nativo
npm install -g @salesforce/cli@latest   # se instalada por npm
```

**Verificação:** `sf --version` mostra o número novo.

### Voltar para uma versão específica

```bash
npm install -g @salesforce/cli@2.140.0
```
*Instala exatamente aquela versão. Útil quando uma atualização quebra seu pipeline.*

```bash
sf update --version 2.140.0   # equivalente no instalador nativo
```

### Atualizar plugins

```bash
sf plugins update
sf plugins   # verifica as versões resultantes
```

### O que **nunca** é "voltar atrás": a org

Sua org é atualizada pela Salesforce, 3× por ano, e **você não pode recusar nem reverter**.
Você só escolhe a **janela** (há um período de preview em sandbox, semanas antes).
É a diferença mais importante entre esta plataforma e software que você hospeda.
Ver [18-devops-e-alm.md](18-devops-e-alm.md) §7.

---

## 17. Desinstalar por completo

### Salesforce CLI

```bash
npm uninstall -g @salesforce/cli
npm uninstall -g sfdx-cli        # o antigo, se existir
```

**Restos que ficam para trás e precisam sair na mão:**

```bash
# Linux / macOS / WSL
rm -rf ~/.sf ~/.sfdx ~/.local/share/sf ~/.cache/sf ~/.config/sf
```
*`~/.sf` e `~/.sfdx` guardam **tokens de autorização das suas orgs** — apagá-los desloga
tudo. Se sua intenção era só reinstalar, **não apague** essas duas.*

```powershell
# Windows
Remove-Item -Recurse -Force "$env:USERPROFILE\.sf", "$env:USERPROFILE\.sfdx"
Remove-Item -Recurse -Force "$env:LOCALAPPDATA\sf", "$env:LOCALAPPDATA\sfdx"
```

Instalador nativo: use *Adicionar ou remover programas* (Windows), ou
`sudo rm -rf /usr/local/sf /usr/local/bin/sf` (macOS/Linux).

**Verificação de que sumiu mesmo:**
```bash
which -a sf ; sf --version
# esperado: nenhuma saída de `which`, e "command not found" no segundo
```
*Se ainda encontrar, há outra instalação por outro método. Repita para o método certo.*

### Revogar o acesso do lado da org (importante)

Desinstalar a CLI não invalida os tokens no servidor. Para revogar de verdade:

```bash
sf org logout --target-org devorg
```
*Revoga o token daquela org.*

Ou, na org: **Setup → Connected Apps OAuth Usage → Salesforce CLI → Revoke**.
Faça isso ao devolver um notebook ou ao suspeitar de comprometimento.

### Node, Java, VS Code

```bash
nvm uninstall 22                          # Node instalado por nvm
sudo apt-get remove --purge openjdk-21-jdk # Java, Debian/Ubuntu
brew uninstall --cask visual-studio-code   # macOS
```
Configurações do VS Code ficam em `~/.config/Code` (Linux),
`~/Library/Application Support/Code` (macOS), `%APPDATA%\Code` (Windows).

---

## 18. Solução de problemas

| Mensagem literal | Causa provável | Correção |
|---|---|---|
| `command not found: sf` (ou `'sf' não é reconhecido...`) | Diretório de binários fora do PATH, ou terminal não reaberto | §11. Rode `npm config get prefix` e acrescente `<prefix>/bin` ao PATH; reabra o terminal |
| `EACCES: permission denied, mkdir '/usr/local/lib/node_modules/@salesforce'` | `npm -g` sem permissão de escrita | **Não use sudo.** §12 — nvm ou prefixo em `~/.npm-global` |
| `Java runtime could not be located` / autocomplete de Apex morto | JDK ausente ou `salesforcedx-vscode-apex.java.home` errado | §6 + §7.3. O caminho **não** deve terminar em `/bin` |
| `This org appears to have a problem with its OAuth configuration` | Token expirado ou revogado | `sf org logout -o devorg` e depois `sf org login web -o devorg` |
| `SELF_SIGNED_CERT_IN_CHAIN` / `UNABLE_TO_VERIFY_LEAF_SIGNATURE` | Proxy corporativo com inspeção TLS | §13.2 — `NODE_EXTRA_CA_CERTS`. **Não** use `NODE_TLS_REJECT_UNAUTHORIZED=0` |
| `localhost refused to connect` após `sf org login web` | Porta 1717 bloqueada/ocupada, ou `NO_PROXY` sem localhost | `sf org login device`, ou `--port 1719`, ou §13.1 |
| `Cannot read properties of undefined (reading 'getPassword')` | Linux sem keychain gráfico | `export SF_USE_GENERIC_UNIX_KEYCHAIN=true` (§11) |
| `sfdx-cli and @salesforce/cli cannot be installed at the same time` | Duas CLIs instaladas | `npm uninstall -g sfdx-cli` e reinstale `@salesforce/cli` |
| `INVALID_LOGIN: Invalid username, password, security token; or user locked out` | Login por senha sem *security token*, ou IP não confiável | Use `sf org login web` (OAuth, não pede token). Se precisar de senha, gere o token em *Settings → Reset My Security Token* e concatene após a senha |
| `Your session has expired` no meio de um deploy | Sessão longa ou org com timeout curto | Reautorize; para CI, use **JWT flow** em vez de senha |
| `Cannot find module 'xxx'` ao rodar `sf` | Instalação corrompida ou upgrade de Node com pacotes globais da versão antiga | Reinstale a CLI: `npm i -g @salesforce/cli --force` |
| `ENOENT: no such file or directory, open 'sfdx-project.json'` | Você não está na raiz de um projeto | `cd` para a pasta do projeto, ou `sf project generate` (§9.3) |
| `You do not have access to the scratch org feature` | Dev Hub não ativado na org autorizada | §2.4 — Setup → Dev Hub → Enable |
| `LimitExceeded: ActiveScratchOrgs` | Estourou as 3 scratch orgs ativas da DE | `sf org list` e depois `sf org delete scratch -o <alias>` |
| Diff do Git mostra todo o arquivo XML alterado | CRLF vs. LF | `git config --global core.autocrlf input` (§5) e recomite |

**Quando nada acima resolver, colete evidência antes de pedir ajuda:**
```bash
sf doctor
```
*Gera um diagnóstico completo: versões, plugins, variáveis de ambiente, conectividade.
É a primeira coisa que qualquer pessoa vai te pedir num fórum.*

```bash
SF_LOG_LEVEL=debug sf org list 2> debug.log
```
*Repete o comando com log detalhado e guarda em arquivo. Revise antes de postar —
o log pode conter tokens.*

---

## 19. Checklist final: ambiente pronto

Rode um por linha. Todos devem passar antes de você ir para
[04-como-comecar.md](04-como-comecar.md).

```bash
node --version          # v22.x ou superior
npm --version           # 10.x ou superior
java -version           # openjdk 21 (ou 17)
git --version           # 2.30 ou superior
code --version          # 1.10x
sf --version            # @salesforce/cli/2.14x
sf plugins              # deve listar code-analyzer, se instalado
sf org list             # sua org com STATUS = Connected
sf doctor               # sem erros críticos
sf data query --query "SELECT Id FROM Organization" -o devorg   # retorna 1 registro
```

E, no VS Code: abra um arquivo `.cls`, digite `System.deb` — o autocomplete deve sugerir
`System.debug`. Se sugerir, o Apex Language Server está vivo e você está pronto.

**Trilha de administrador:** basta que a org da §2 abra no navegador e que você chegue ao Setup.

---

## Autoteste

1. Qual a diferença entre `sfdx-cli` e `@salesforce/cli`? Qual usar em 2026?
2. Por que `sudo npm install -g` é uma má ideia? Dê dois motivos distintos.
3. Você instalou a CLI e o terminal diz `command not found: sf`. Quais dois comandos você roda para diagnosticar?
4. O autocomplete de Apex não funciona no VS Code. Qual é a causa mais provável e como confirmar?
5. Sua empresa inspeciona TLS. Qual variável resolve, e qual variável **não** se deve usar — e por quê?
6. Como se cria uma scratch org e quantas você pode ter ativas numa Developer Edition?
7. O que significa `sourceApiVersion: "67.0"` no `sfdx-project.json`, e por que mudá-la é uma decisão de risco?
8. Você vai devolver o notebook da empresa. Que passo, além de desinstalar a CLI, é obrigatório?

---

### Fontes consultadas (11/08/2026)

- npm — `@salesforce/cli` (versão 2.146.3) — https://www.npmjs.com/package/@salesforce/cli
- Salesforce — *Salesforce CLI Setup Guide*, versão 67.0 Summer '26, atualizado em 24/07/2026 — https://resources.docs.salesforce.com/latest/latest/en-us/sfdc/pdf/sfdx_setup.pdf
- Salesforce Developers — *Supported Scratch Org Editions and Allocations* — https://developer.salesforce.com/docs/atlas.en-us.sfdx_dev.meta/sfdx_dev/sfdx_dev_scratch_orgs_editions_and_allocations.htm
- Salesforce Ben — *Get Started With Salesforce Scratch Orgs (Updated for 2026)* — https://www.salesforceben.com/salesforce-scratch-orgs/
- Salesforce Developers — download da CLI — https://developer.salesforce.com/tools/salesforcecli
