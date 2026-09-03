# 03 · Manual de instalação

**Nível:** iniciante · **Última atualização:** 14/08/2026
**Testado em:** Ubuntu 22.04.5 LTS, kernel 6.8.0-136-generic, x86_64, em 14/08/2026.
**Versões pesquisadas na web em 14/08/2026** (ver rodapé para as fontes).

---

## Leia isto antes de instalar qualquer coisa

**Uma parte grande deste curso não exige instalar nada.** Seu sistema já vem com a
ferramenta principal:

| Sistema | Já vem instalado | Basta digitar |
|---|---|---|
| Linux | `ss` (pacote `iproute2`, presente em toda distro moderna) | `ss -tulpn` |
| macOS | `lsof`, `netstat`, `nettop` | `lsof -nP -iTCP -sTCP:LISTEN` |
| Windows 10/11 | `netstat`, PowerShell `Get-NetTCPConnection` | `Get-NetTCPConnection -State Listen` |

Rode o comando da sua linha agora. Se ele funcionou, você já pode ir para
[`04-como-comecar.md`](04-como-comecar.md) e voltar aqui quando precisar de `nmap`.

O resto deste arquivo instala o **conjunto completo** — porque o assunto não é uma
ferramenta só, e quem instala só o `nmap` e assume o resto fica travado na primeira
divergência.

---

## O conjunto completo — o que cada peça faz e se você precisa dela

| Ferramenta | Para quê | Prioridade |
|---|---|---|
| **`ss`** (iproute2) | Listar sockets locais. Substituto moderno do `netstat`. | **Essencial** |
| **`lsof`** | Ligar socket a processo e a arquivo. Único caminho no macOS. | **Essencial** |
| **`nmap`** | Varrer portas pela rede, identificar serviço e versão. | **Essencial** |
| **`netcat`** (`nc`) | Abrir/testar uma porta à mão. O canivete. | **Muito útil** |
| **`socat`** | O canivete suíço do `nc`: túnel, redirecionamento, UNIX socket. | Útil |
| **`tcpdump`** | Ver os pacotes de verdade. Onde a teoria vira evidência. | Útil |
| **`Wireshark`** | Idem, com interface gráfica e decodificação. | Útil |
| **`curl`** | Testar HTTP em qualquer porta. | Muito útil |
| **`openssl`** | Testar TLS em qualquer porta. | Útil |
| **`fuser`** (psmisc) | "Quem está usando a porta 8080?" em um comando. | Útil |
| **`net-tools`** (`netstat`) | Legado. Instale só se scripts antigos dependerem. | Opcional |
| **Python 3.10+** | Rodar o projeto-modelo. | Necessário para o `07` |
| **`nftables`/`iptables`/`ufw`** | Ver e ajustar o firewall local. | Necessário para o `18` |

---

## Alternativa sem instalar nada

Ofereço isto **antes** do caminho longo de propósito: é o que evita desistência no primeiro dia.

### 1. Você já tem o suficiente (o caminho mais provável)

`ss`, `netstat`, `lsof` e PowerShell cobrem os blocos A e a maior parte do B. Comece por aí.

### 2. Laboratórios no navegador — zero instalação

| Serviço | O que dá para fazer | Grátis? |
|---|---|---|
| [TryHackMe](https://tryhackme.com/) | Salas "Nmap", "Network Fundamentals" com máquina no navegador | Sim, com limite de tempo diário |
| [Hack The Box Academy](https://academy.hackthebox.com/) | Módulo "Network Enumeration with Nmap" | Módulos introdutórios grátis |
| [OverTheWire — Bandit](https://overthewire.org/wargames/bandit/) | Exercícios com `nc` e portas por SSH | Sim, totalmente |
| [Katacoda-like: killercoda.com](https://killercoda.com/) | Terminal Linux root descartável no navegador | Sim |

### 3. Container descartável (se você tem Docker)

```bash
docker run --rm -it --net=host --cap-add=NET_RAW --cap-add=NET_ADMIN \
  instrumentisto/nmap sh
```

Um comando, e você tem `nmap` com privilégio de rede sem sujar sua máquina.
`--net=host` faz o container enxergar as portas do host — é isso que torna o teste útil,
e é também por que você **não** deve deixar esse container rodando.

### 4. Alvo público autorizado para praticar

`scanme.nmap.org` — mantido pelo projeto Nmap exatamente para isso. Use com moderação
(sem `-T5`, sem varredura completa repetida). É o **único** alvo público que este material
recomenda.

---

## Linux

### Debian / Ubuntu / Mint / Pop!_OS

```bash
sudo apt update
```
> Atualiza a lista de pacotes disponíveis. Sem isto, o `apt install` pode instalar versão velha ou falhar.

```bash
sudo apt install -y iproute2 lsof nmap netcat-openbsd socat tcpdump psmisc curl
```
> Instala o conjunto essencial de uma vez. `iproute2` normalmente já está — o `apt` avisa e segue.

Verificação, um comando por linha, com a saída esperada:

```bash
ss -V
# esperado: ss utility, iproute2-5.15.0   (o número varia; qualquer 4.x+ serve)
```
```bash
lsof -v 2>&1 | head -2
# esperado: lsof version information:   /   revision: 4.93.2
```
```bash
nmap --version | head -1
# esperado: Nmap version 7.80 ( https://nmap.org )   ou superior
```
```bash
nc -h 2>&1 | head -1
# esperado: OpenBSD netcat (Debian patchlevel 1.218-4ubuntu1)
```
```bash
tcpdump --version 2>&1 | head -1
# esperado: tcpdump version 4.99.1
```

**Se a saída for diferente:** `command not found` significa que o pacote não instalou —
role até a tabela de erros no fim deste arquivo.

#### Uma armadilha real do Ubuntu 22.04 com o Nmap

Rode isto:

```bash
dpkg -l nmap | grep '^ii'
```

Na máquina onde este curso foi escrito, a saída **real** foi:

```
ii  nmap  7.91+dfsg1+really7.80+dfsg1-2ubuntu0.1  amd64  The Network Mapper
```

Leia com atenção: `7.91+really7.80`. O Ubuntu empacotou a 7.91, descobriu um problema, e
**reverteu para a 7.80 de 2019** mantendo o número maior no nome do pacote para o `apt` não
se confundir. Ou seja: `apt install nmap` no Ubuntu 22.04 te dá uma versão de **2019**.

A versão atual da série é a **7.991** (a 7.99 saiu em 26/03/2026). A diferença importa: a
base de detecção de serviços e as assinaturas de sistema operacional evoluíram muito nesses
sete anos. Para o curso, a 7.80 basta. Para trabalho sério de segurança, instale do fonte
ou de um repositório mais atual (ver abaixo).

**Como conferir a idade da sua base de detecção:**

```bash
grep -m1 -i 'version\|Id:' /usr/share/nmap/nmap-service-probes | head -2
```

### Fedora / RHEL / Rocky / AlmaLinux

```bash
sudo dnf install -y iproute lsof nmap nmap-ncat socat tcpdump psmisc curl
```
> No Fedora, o pacote do `ss` chama-se `iproute` (sem o "2"), e o netcat é o `nmap-ncat` — que é o `ncat` do projeto Nmap, com sintaxe ligeiramente diferente do `nc` da OpenBSD. Ver [`05-manual-de-uso.md`](05-manual-de-uso.md).

```bash
ss -V ; nmap --version | head -1 ; ncat --version 2>&1 | head -1
# esperado: as três linhas com versão, sem "command not found"
```

### Arch / Manjaro

```bash
sudo pacman -S --needed iproute2 lsof nmap gnu-netcat socat tcpdump psmisc curl
```
> `--needed` evita reinstalar o que já está lá. O Arch entrega versões atuais — aqui você tem o Nmap recente sem esforço.

### Alpine (útil em containers)

```bash
apk add --no-cache iproute2 lsof nmap nmap-ncat socat tcpdump curl
```
> `--no-cache` não guarda o índice de pacotes: é o que mantém a imagem pequena. Note que o Alpine **não** traz `ss` por padrão nem `bash`.

### openSUSE

```bash
sudo zypper install iproute2 lsof nmap netcat-openbsd socat tcpdump psmisc curl
```

### Compilar o Nmap do fonte (quando o pacote da distro é velho demais)

Faça isto só se você precisar da detecção de serviços atual.

```bash
sudo apt install -y build-essential libssl-dev libpcap-dev
```
> Compilador, cabeçalhos de TLS e da libpcap. Sem `libpcap-dev` você compila um Nmap sem varredura SYN.

```bash
cd /tmp && curl -LO https://nmap.org/dist/nmap-7.99.tar.bz2
```
> Baixa o fonte. Confira em https://nmap.org/download.html qual é a versão atual antes de fixar o número.

```bash
curl -LO https://nmap.org/dist/sigs/nmap-7.99.tar.bz2.asc
gpg --keyserver keyserver.ubuntu.com --recv-keys 436D66AB9A798425FDA0E3F801AF9F036B9355D0
gpg --verify nmap-7.99.tar.bz2.asc nmap-7.99.tar.bz2
# esperado: "Good signature from "Nmap Project Signing Key""
```
> **Não pule isto.** Você está prestes a compilar código com privilégio. A chave está publicada em https://nmap.org/book/install.html — confira a impressão digital lá antes de confiar na que está acima.

```bash
tar xjf nmap-7.99.tar.bz2 && cd nmap-7.99
./configure --prefix=/usr/local && make -j"$(nproc)" && sudo make install
```
> `--prefix=/usr/local` instala fora do território do gerenciador de pacotes — assim a versão da distro e a sua não brigam.

```bash
hash -r ; nmap --version | head -1
# esperado: Nmap version 7.99 ( https://nmap.org )
```
> `hash -r` limpa o cache de caminhos do shell. Sem ele, o bash continua chamando o `nmap` antigo mesmo depois de instalar o novo — e você jura que a instalação falhou.

**Convivência das duas versões:**

```bash
which -a nmap
# esperado: /usr/local/bin/nmap  e  /usr/bin/nmap
```

O primeiro da lista vence. Para chamar o antigo de propósito: `/usr/bin/nmap --version`.

---

## macOS

**Não executado:** não havia máquina macOS no ambiente de escrita. Os comandos abaixo vêm da
documentação oficial do Homebrew e do Nmap (ver `95-referencias.md`). Confira antes de
confiar cegamente.

### O que já vem

```bash
lsof -nP -iTCP -sTCP:LISTEN
netstat -an | grep LISTEN
nettop            # interativo, por processo
```

Repare que o macOS **não tem `ss`** e o `netstat` dele é o do BSD, com flags diferentes das
do Linux. `netstat -tulpn` **não funciona** no macOS — é a causa nº 1 de frustração de quem
vem do Linux. O equivalente é `lsof`.

### Instalar o Homebrew (se ainda não tiver)

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```
> Instala o gerenciador de pacotes. Ele **não** pede root para si, mas pede sua senha para criar `/opt/homebrew` (Apple Silicon) ou `/usr/local` (Intel).

**Apple Silicon (M1/M2/M3/M4):** o Homebrew instala em `/opt/homebrew`, que **não está no
PATH por padrão**. Este é o erro de instalação nº 1 no macOS moderno:

```bash
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"
```
> A primeira linha torna permanente; a segunda aplica **agora**, sem fechar o terminal.
> Em Mac Intel o caminho é `/usr/local/bin/brew` e normalmente já está no PATH.

```bash
brew --version
# esperado: Homebrew 4.x.x
```

### Instalar o conjunto

```bash
brew install nmap lsof socat wireshark
```
> O `nc` do macOS já existe (é o da Apple, derivado do OpenBSD). O `tcpdump` também.
> `brew install wireshark` instala a versão de linha de comando (`tshark`); para a interface
> gráfica use `brew install --cask wireshark`.

```bash
nmap --version | head -1
# esperado: Nmap version 7.9x ( https://nmap.org )
```

### Detalhe do macOS que confunde quem vem do Linux

O macOS **usa a porta 5000 e a 7000 para o AirPlay Receiver** desde o Monterey (2021).
Se seu servidor de desenvolvimento em Flask não sobe na 5000, não é bug do Flask: é o
`ControlCenter` da Apple ocupando. Confirme com:

```bash
lsof -nP -iTCP:5000 -sTCP:LISTEN
```

Solução: desligue em *Ajustes do Sistema → Geral → AirDrop e Handoff → Receptor AirPlay*,
ou use outra porta.

---

## Windows

### Caminho recomendado, e por quê

| Caminho | Quando usar | Recomendação |
|---|---|---|
| **PowerShell nativo** | Inventariar portas do **próprio Windows** | ✅ Use sempre para isto |
| **Nmap nativo (+ Npcap)** | Varrer a rede a partir do Windows | ✅ Use para isto |
| **WSL2** | Seguir o curso, usar `ss`, ler `/proc`, rodar o projeto-modelo | ✅ **Melhor caminho geral** |

**A recomendação honesta:** instale o **WSL2** para acompanhar o curso e o **Nmap nativo**
para varrer a rede. Os dois convivem sem conflito.

**Por que não só o WSL2:** o WSL2 roda numa máquina virtual leve com **rede própria**
(NAT). As portas que você vê com `ss` dentro do WSL **não são** as portas do Windows.
Um `Get-NetTCPConnection` no Windows e um `ss -tulpn` no WSL respondem sobre máquinas
diferentes. Confundir os dois faz você "não achar" o serviço que está bem ali.

> *Nota:* nas versões mais recentes do WSL existe um modo de rede espelhada
> (`networkingMode=mirrored` no `.wslconfig`) que aproxima os dois mundos. Se o seu WSL
> tiver esse modo ativo, a distinção acima muda — verifique com `wsl --version` e a
> documentação da Microsoft antes de assumir.

### O que já vem no Windows

```powershell
Get-NetTCPConnection -State Listen | Select-Object LocalAddress,LocalPort,OwningProcess
```
> Lista as portas TCP em escuta. Note: **`Get-NetTCPConnection` não mostra UDP.**

```powershell
Get-NetUDPEndpoint | Select-Object LocalAddress,LocalPort,OwningProcess
```
> Para UDP existe um cmdlet separado. Esquecer disto é o erro clássico no Windows.

```powershell
netstat -ano | findstr LISTENING
```
> Alternativa antiga, ainda útil: `-a` todas, `-n` numérico, `-o` mostra o PID.

Cruzar PID com nome de processo:

```powershell
Get-NetTCPConnection -State Listen |
  Select-Object LocalAddress, LocalPort,
    @{Name='Processo';Expression={(Get-Process -Id $_.OwningProcess).ProcessName}} |
  Sort-Object LocalPort | Format-Table -AutoSize
```
> Este é o comando que você vai usar 90 % das vezes no Windows. Guarde-o.
> Para ver processos de **outros** usuários, abra o PowerShell **como administrador**.

### Instalar o Nmap no Windows

**Método recomendado — WinGet:**

```powershell
winget install --id Insecure.Nmap -e
```
> `-e` exige correspondência exata do identificador, evitando instalar um pacote parecido.

**Método alternativo — instalador oficial:** baixe de https://nmap.org/download.html o
`nmap-<versão>-setup.exe`. Confira o hash SHA-256 publicado na mesma página.

**Npcap é obrigatório.** O instalador do Nmap oferece instalá-lo. Aceite. Sem o Npcap,
o Nmap no Windows perde varredura SYN, detecção de SO e qualquer coisa que use pacote bruto.
A versão atual do Npcap é a **1.88** (06/05/2026).

> **Sobre a licença do Npcap:** ele é gratuito para uso pessoal e interno, mas **não** é
> software livre, e redistribuí-lo dentro de um produto comercial exige licença paga.
> Detalhes em [`80-custos-e-licencas.md`](80-custos-e-licencas.md). É a única peça deste
> conjunto com essa restrição — vale saber antes de embutir num produto.

Verificação (abra um terminal **novo**):

```powershell
nmap --version
# esperado: Nmap version 7.9x ( https://nmap.org )
```

Se der `nmap : O termo 'nmap' não é reconhecido`, o PATH não foi recarregado. Feche e
reabra o PowerShell. Se persistir, veja a seção de PATH abaixo.

### Instalar o WSL2

```powershell
wsl --install -d Ubuntu-24.04
```
> Instala o WSL2 com o Ubuntu 24.04. Precisa de PowerShell **como administrador** e de uma reinicialização.

```powershell
wsl --status
# esperado: Versão padrão: 2
```

Dentro do WSL, siga a seção Debian/Ubuntu deste arquivo.

**Ponte entre os dois mundos** — chamar comando do Windows de dentro do WSL:

```bash
powershell.exe -Command "Get-NetTCPConnection -State Listen | Select LocalPort" 
```
> Roda no Windows, imprime no terminal do WSL. É como você compara os dois inventários sem trocar de janela.

### Instalar o Wireshark no Windows

```powershell
winget install --id WiresharkFoundation.Wireshark -e
```
> Versão estável atual: **4.6.6**. O instalador traz o Npcap junto.

---

## PATH e variáveis de ambiente

Esta seção resolve a classe de problema mais comum e mais mal diagnosticada:
*"eu instalei, mas o comando não existe"*.

### O que é o PATH, em uma frase

Uma lista de diretórios que o shell percorre, **em ordem**, procurando o programa que você
digitou. Se o binário não está em nenhum deles, você recebe `command not found` — mesmo
que o arquivo exista no disco.

### Conferir

```bash
echo "$PATH" | tr ':' '\n'        # Linux/macOS
```
```powershell
$env:PATH -split ';'              # Windows PowerShell
```

### Descobrir qual binário está sendo usado

```bash
which -a nmap        # todos os candidatos, na ordem de precedência
type -a nmap         # idem, no bash, e mostra se é alias ou função
```
```powershell
Get-Command nmap -All
```

### Corrigir — em qual arquivo mexer

| Shell / Sistema | Arquivo | Vale para |
|---|---|---|
| bash (Linux) | `~/.bashrc` | sessões interativas |
| bash (login/SSH) | `~/.bash_profile` ou `~/.profile` | sessões de login |
| zsh (padrão do macOS) | `~/.zshrc` (interativo), `~/.zprofile` (login) | |
| fish | `~/.config/fish/config.fish` | |
| Windows | `$PROFILE` (`notepad $PROFILE`), ou Variáveis de Ambiente do sistema | |

```bash
echo 'export PATH="/usr/local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```
> A primeira linha grava; a segunda aplica **na sessão atual**.

### Por que "a mudança não pegou"

Três causas, nesta ordem de frequência:

1. **Você não reabriu o terminal.** Arquivos de perfil são lidos na abertura do shell,
   não continuamente. `source ~/.bashrc` resolve sem fechar.
2. **O shell guardou o caminho antigo em cache.** O bash memoriza onde achou cada comando.
   Corrija com `hash -r`. É o motivo de você instalar uma versão nova e continuar vendo a
   antiga.
3. **Você editou o arquivo errado.** Terminal gráfico lê `.bashrc`; sessão SSH lê
   `.bash_profile`. Se funciona em um e não no outro, é isso.

---

## Permissões — o que exige privilégio, e o caminho certo

### O que exige root e por quê

| Operação | Exige | Motivo técnico |
|---|---|---|
| Ver PID de processo alheio no `ss -p` | root | `/proc/<pid>/fd` de outro usuário não é legível |
| `nmap -sS` (SYN scan) | root | Precisa forjar pacote bruto (`CAP_NET_RAW`) |
| `nmap -sU`, `-O` | root | Idem |
| `tcpdump` | root ou grupo | Precisa modo promíscuo na interface |
| Escutar em porta < 1024 | root ou capability | Restrição histórica do Unix |
| Ler/alterar firewall | root | |

### Escutar abaixo de 1024 — o caminho certo, e o errado

O erro literal, reproduzido nesta máquina:

```
PermissionError errno 13 Permission denied
```

**O caminho errado:** rodar o serviço inteiro como root. Todo o processo passa a ter
poder total na máquina só para poder usar o número 80. Se ele for comprometido, o
atacante herda root. Esse acoplamento — "quero um número baixo, logo preciso de poder
absoluto" — é a origem de uma quantidade enorme de incidentes.

**Os quatro caminhos certos, em ordem de preferência:**

```bash
# 1. Capability específica no binário (Linux): dá SÓ o poder de abrir porta baixa
sudo setcap 'cap_net_bind_service=+ep' /usr/bin/python3.10
getcap /usr/bin/python3.10
# esperado: /usr/bin/python3.10 cap_net_bind_service=ep
```
> Cuidado: isto vale para **todo** programa Python daquele binário. Prefira aplicar no
> binário do seu serviço, não no interpretador compartilhado.

```bash
# 2. systemd faz o bind como root e entrega o socket já aberto ao serviço não-privilegiado
#    (socket activation). É a solução mais limpa em servidor Linux moderno.
#    Ver: man systemd.socket
```

```bash
# 3. Baixar o limite do sistema inteiro (kernel >= 4.11)
sudo sysctl net.ipv4.ip_unprivileged_port_start=80
# esperado: net.ipv4.ip_unprivileged_port_start = 80
```
> Vale para a máquina toda até reiniciar. Para tornar permanente, `/etc/sysctl.d/`.
> É o que muitos containers fazem.

```bash
# 4. Rode em porta alta e ponha um proxy reverso (nginx, Caddy) na frente na 80/443
```
> É o que a maior parte da produção faz de verdade, e resolve TLS e log de quebra.

### Por que `sudo` com gerenciador de pacotes de linguagem é problema

`sudo npm install -g`, `sudo pip install` — a tentação aparece quando dá `EACCES`.
O problema não é filosófico: um script de instalação (`postinstall`) de qualquer pacote
roda **com seus privilégios**. Com `sudo`, um pacote comprometido tem root. Além disso,
arquivos passam a pertencer ao root e depois quebram atualizações do usuário.

Caminho certo: `pipx`, ambiente virtual (`python3 -m venv`), ou `npm config set prefix ~/.npm-global`.

---

## Rede corporativa

Se você está numa máquina de empresa, leia isto **antes** de rodar qualquer coisa.

### Proxy

```bash
export http_proxy="http://proxy.empresa.com:3128"
export https_proxy="http://proxy.empresa.com:3128"
export no_proxy="localhost,127.0.0.1,.empresa.com"
```
> Necessário para `apt`, `curl`, `pip`. O `apt` **não** lê essas variáveis quando roda por
> `sudo` — configure em `/etc/apt/apt.conf.d/95proxy`:
> `Acquire::http::Proxy "http://proxy.empresa.com:3128";`

**O `nmap` ignora proxy.** Ele fala direto com a rede. Se seu tráfego precisa passar pelo
proxy, a varredura simplesmente não chegará ao destino — e você verá tudo como "filtrada".

### Certificado interno (inspeção TLS)

Se a empresa inspeciona TLS, o `curl` vai falhar com:

```
curl: (60) SSL certificate problem: unable to get local issuer certificate
```

Corrija instalando o certificado da empresa — **nunca** com `curl -k` em produção:

```bash
sudo cp empresa-ca.crt /usr/local/share/ca-certificates/
sudo update-ca-certificates
# esperado: 1 added, 0 removed; done.
```

### ⚠️ Varredura em rede corporativa dispara alertas

Isto não é teoria. Um `nmap` na faixa da empresa aciona IDS/EDR e gera incidente. Mesmo
sendo você o administrador. Mesmo em `10.x.x.x`.

**O procedimento profissional:** avise o time de segurança **antes**, por escrito, com
janela de tempo, faixa de IP e IP de origem. Leva cinco minutos e evita uma conversa
muito pior depois. Se não existe time de segurança, avise seu gestor por e-mail — o e-mail
é o registro.

---

## Convivência de versões

| Situação | Como resolver |
|---|---|
| Nmap da distro (velho) + Nmap do fonte (novo) | Instale o do fonte em `/usr/local`. `which -a nmap` mostra os dois; o primeiro vence. Chame o outro pelo caminho completo. |
| `netstat` e `ss` | Convivem sem conflito, pacotes diferentes (`net-tools` e `iproute2`). |
| `nc` OpenBSD × `ncat` do Nmap × `nc` GNU | **Sintaxes diferentes e incompatíveis.** Descubra qual você tem: `nc -h 2>&1 \| head -1`. Ver [`05-manual-de-uso.md`](05-manual-de-uso.md). |
| Python do sistema × do `pyenv`/`uv` | O projeto-modelo usa só a biblioteca padrão; qualquer 3.10+ serve. |

---

## Reprodutibilidade

Para que outra pessoa (ou você daqui a um ano) tenha o mesmo ambiente:

**Container, o caminho mais confiável:**

```dockerfile
# Dockerfile — ambiente do curso "portas-de-rede"
FROM ubuntu:24.04
RUN apt-get update && apt-get install -y --no-install-recommends \
      iproute2 lsof nmap netcat-openbsd socat tcpdump psmisc curl python3 \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /lab
CMD ["/bin/bash"]
```

```bash
docker build -t portas-lab .
docker run --rm -it --net=host --cap-add=NET_RAW --cap-add=NET_ADMIN portas-lab
```
> **Não executado** no ambiente de escrita (sem Docker disponível). O `Dockerfile` segue o
> padrão usado no assunto [`docker`](../docker/00-MAPA.md) desta pasta.

**Registrar o que você tem:**

```bash
{ ss -V; lsof -v 2>&1|head -2; nmap --version|head -1; uname -a; } > ambiente.txt
```

---

## Atualizar e voltar atrás

```bash
sudo apt update && sudo apt install --only-upgrade nmap
```
> Atualiza só o Nmap.

```bash
apt-cache policy nmap        # mostra a versão instalada e as candidatas
sudo apt install nmap=7.80-1  # volta a uma versão específica (o nome exato vem do comando acima)
```

Compilado do fonte:

```bash
cd /tmp/nmap-7.99 && sudo make uninstall
```
> O `make uninstall` do Nmap funciona — o que é raro e generoso. Muitos projetos não têm.

---

## Desinstalar por completo

```bash
sudo apt purge -y nmap lsof socat tcpdump netcat-openbsd
sudo apt autoremove -y
```
> `purge` (e não `remove`) apaga também os arquivos de configuração.

O que **fica para trás** e o `apt` não remove:

```bash
rm -rf ~/.nmap ~/.zenmap                # perfis e histórico do Zenmap
sudo rm -rf /usr/share/nmap             # base de detecção (~25 MB), se sobrar
sudo rm -rf /usr/local/share/nmap /usr/local/bin/nmap   # se você compilou do fonte
```

Windows:

```powershell
winget uninstall Insecure.Nmap
winget uninstall Insecure.Npcap      # o Npcap NÃO sai junto — remova explicitamente
```

macOS:

```bash
brew uninstall nmap && brew cleanup
```

**Verificar que sumiu:**

```bash
which -a nmap ; echo "saída vazia = removido"
```

---

## Requisitos reais

| Item | Valor |
|---|---|
| Disco | Nmap ~30 MB (a base `nmap-service-probes` é a maior parte) · Wireshark ~250 MB · WSL2 + Ubuntu ~2 GB |
| Memória | Irrelevante para `ss`/`lsof`. Nmap com `-p-` em `/16` pode passar de 1 GB. |
| Arquitetura | x86_64 e ARM64 suportados por tudo aqui |
| Licença/conta | **Nenhuma ferramenta deste curso exige cadastro ou cartão de crédito.** Exceção: Npcap tem restrição comercial (ver `80`). |
| Internet | Só para instalar. O curso inteiro roda offline contra `127.0.0.1`. |

---

## Solução de problemas — mensagens literais

| Mensagem | Causa provável | Correção |
|---|---|---|
| `command not found: ss` | `iproute2` ausente (Alpine, container mínimo) ou você está no macOS | `apt install iproute2` · no macOS use `lsof` |
| `netstat: command not found` | `net-tools` foi removido das distros modernas de propósito | Use `ss`. Se precisar do legado: `apt install net-tools` |
| `You requested a scan type which requires root privileges.` | `nmap -sS`, `-sU` ou `-O` sem root | Use `sudo nmap ...`, ou troque para `-sT` (connect scan, sem privilégio) |
| `dnet: Failed to open device eth0` | Nmap sem Npcap (Windows) ou sem permissão de interface | Instale o Npcap · no Linux, `sudo` |
| `nmap: command not found` **depois** de instalar | PATH não recarregado, ou cache do shell | Reabra o terminal · `hash -r` · `which -a nmap` |
| `bind: Address already in use` | Outro processo já tem a porta, **ou** TIME_WAIT de um socket anterior | `ss -tulpn \| grep :<porta>` · use `SO_REUSEADDR` · ver [`13`](13-tcp-por-dentro.md) |
| `bind: Permission denied` (porta < 1024) | Restrição de porta privilegiada | `setcap`, `sysctl ip_unprivileged_port_start`, ou porta alta + proxy |
| `Note: Host seems down. If it is really up, but blocking ping probes, try -Pn` | O alvo não responde a ping (Windows bloqueia por padrão) | `nmap -Pn <alvo>` |
| `Strange read error from 127.0.0.1 (32 - 'Broken pipe')` | Serviço fechou a conexão durante a sondagem — comum com proxy interceptando | Não é erro seu. Ver o caso real no [projeto-modelo](07-projeto-modelo/README.md) |
| `Too many open files` | Paralelismo acima do `ulimit -n` | `ulimit -n 8192` · reduza `--min-parallelism` / `-P` |
| `TCPDUMP: You don't have permission to capture on that device` | Sem `CAP_NET_RAW` | `sudo tcpdump` · ou `sudo dpkg-reconfigure wireshark-common` + grupo `wireshark` |
| `curl: (7) Failed to connect to localhost port 8080: Connection refused` | Ninguém escuta ali — ou escuta em outro IP | `ss -tulpn \| grep 8080`. Se aparece `127.0.0.1:8080` e você chamou pelo IP externo, é bind restrito. |
| `Get-NetTCPConnection : ... não é reconhecido` | PowerShell antigo (v2) ou Windows sem o módulo NetTCPIP | Use `netstat -ano`. Atualize o PowerShell. |

---

## Checklist — ambiente pronto

Rode um por linha. Todos devem responder sem erro.

```bash
ss -V
```
```bash
lsof -v 2>&1 | head -1
```
```bash
nmap --version | head -1
```
```bash
nc -h 2>&1 | head -1
```
```bash
curl --version | head -1
```
```bash
python3 --version
```
```bash
ss -tulpn | head -5
```
```bash
nmap -sT -p 80,443 127.0.0.1
```
```bash
cd 07-projeto-modelo && python3 testes.py 2>&1 | tail -3
# esperado: Ran 41 tests ... OK
```

Se os nove passaram, siga para [`04-como-comecar.md`](04-como-comecar.md).

---

## Fontes consultadas

Pesquisado na web em **14/08/2026**:

- [Nmap — Change Log](https://nmap.org/changelog.html) e [Nmap — Download](https://nmap.org/download.html) — versão 7.991 atual; 7.99 lançada em 26/03/2026.
- [Npcap](https://npcap.com/) — versão 1.88, de 06/05/2026; licença com restrição comercial.
- [Wireshark — Download](https://www.wireshark.org/download.html) — 4.6.6 estável.
- [IANA — Service Name and Transport Protocol Port Number Registry](https://www.iana.org/assignments/service-names-port-numbers) — atualizado em 11/08/2026.

Verificado localmente em **14/08/2026**, Ubuntu 22.04.5: `iproute2 5.15.0-1ubuntu2.2`,
`lsof 4.93.2`, `nmap 7.91+dfsg1+really7.80+dfsg1-2ubuntu0.1`, `netcat-openbsd 1.218-4ubuntu1`,
`tcpdump 4.99.1-3ubuntu0.2`, `net-tools 1.60+git20181103`, `psmisc 23.4-2build3`,
`curl 7.81.0`, `OpenSSL 3.0.2`, `Python 3.10.12`.

---

## Autoteste

1. Você está num container Alpine e `ss` não existe. O que aconteceu e qual a saída?
2. Por que `apt install nmap` no Ubuntu 22.04 entrega uma versão de 2019? Como você
   descobriria isso sem consultar a internet?
3. Você instalou o Nmap do fonte, mas `nmap --version` mostra a versão antiga. Duas causas
   possíveis, dois comandos que resolvem.
4. Um serviço precisa escutar na porta 443. Enumere quatro formas de conseguir isso **sem**
   rodar o processo inteiro como root, e diga qual você escolheria em um servidor Linux moderno.
5. No macOS, `netstat -tulpn` devolve erro. Por quê, e qual é o comando equivalente?
6. Por que `ss -tulpn` dentro do WSL2 não mostra as portas dos programas do Windows?
7. O que é o Npcap, por que o Nmap no Windows precisa dele, e qual é a pegadinha da licença?

---

*Próximo: [`04-como-comecar.md`](04-como-comecar.md) — do ambiente pronto ao primeiro inventário.*
