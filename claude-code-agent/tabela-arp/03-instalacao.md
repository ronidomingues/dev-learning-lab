# 03 · Instalação — manual de campo

> **Nível:** iniciante
> **Data:** 14/08/2026
>
> **Leia primeiro este parágrafo.** Para **ler** a tabela ARP você provavelmente **não precisa
> instalar nada**: as ferramentas de leitura (`arp`, `ip neigh`, `Get-NetNeighbor`) já vêm de
> fábrica em Windows, macOS e toda distribuição Linux. Este arquivo instala o que vai **além**
> da leitura — captura de pacotes (Wireshark/tcpdump), varredura ativa (arp-scan, nmap),
> monitoramento (arpwatch), scripting (Scapy) e um **laboratório isolado** (Docker ou VMs) onde
> você pode fazer tudo, inclusive os experimentos de ataque, sem tocar em rede alheia.

---

## Índice

1. [O que instalar, e o que já existe](#1-o-que-instalar-e-o-que-ja-existe)
2. [Alternativa sem instalar nada](#2-alternativa-sem-instalar-nada)
3. [Linux — Debian/Ubuntu](#3-linux--debianubuntu)
4. [Linux — Fedora/RHEL](#4-linux--fedorarhel)
5. [macOS](#5-macos)
6. [Windows (nativo e WSL2)](#6-windows-nativo-e-wsl2)
7. [PATH, permissões e captura sem root](#7-path-permissoes-e-captura-sem-root)
8. [Scapy — o ARP programável](#8-scapy--o-arp-programavel)
9. [O laboratório isolado (Docker e VMs)](#9-o-laboratorio-isolado)
10. [Rede corporativa: proxy e restrições](#10-rede-corporativa)
11. [Atualizar, reverter, desinstalar](#11-atualizar-reverter-desinstalar)
12. [Solução de problemas](#12-solucao-de-problemas)
13. [Checklist de ambiente pronto](#13-checklist-de-ambiente-pronto)

---

## 1. O que instalar, e o que já existe

O "conjunto de tecnologias" deste assunto, com o papel de cada peça:

| Ferramenta | Para que serve | Já vem instalado? |
|---|---|---|
| **`ip` (iproute2)** | ler/alterar a tabela de vizinhos no Linux (o comando moderno) | **sim**, em todo Linux atual |
| **`arp` (net-tools)** | idem, comando legado; e o padrão em Windows/macOS | Linux: às vezes; Win/macOS: **sim** |
| **`Get-NetNeighbor`** | ler/alterar a tabela no Windows (PowerShell moderno) | **sim**, Windows 8+ |
| **`tcpdump`** | capturar pacotes ARP no terminal | Linux/macOS: quase sempre |
| **Wireshark** | capturar e dissecar pacotes com interface gráfica | **não** |
| **`arping`** | enviar um ARP request manual a um IP | **não** (pacote `iputils-arping`) |
| **`arp-scan`** | varrer o segmento inteiro com ARP e listar quem responde | **não** |
| **`nmap`** | varredura de rede; usa ARP no segmento local | **não** |
| **`arpwatch`** | vigiar a rede e alertar quando um par IP↔MAC muda | **não** |
| **Scapy (Python)** | montar pacotes ARP byte a byte, em código | **não** |
| **Docker** ou **VirtualBox** | montar o laboratório isolado | **não** |

Recomendação por perfil:

- **"só quero entender e diagnosticar"** → nada a instalar. Vá para o [04](04-como-comecar.md).
- **"quero ver o pacote"** → instale `tcpdump` (leve) ou Wireshark (gráfico).
- **"quero mapear a rede"** → `arp-scan` e/ou `nmap`.
- **"quero experimentar ataque/defesa com segurança"** → o laboratório do §9.

---

## 2. Alternativa sem instalar nada

Antes do caminho longo: você pode começar **hoje**, sem instalar e sem risco.

### 2.1 Ferramentas nativas (recomendado)

Abra o terminal e rode o que já existe:

```bash
# Linux
ip neigh show

# macOS
arp -a -n

# Windows (PowerShell)
Get-NetNeighbor
```

Isso já entrega o [04](04-como-comecar.md) inteiro e boa parte do [05](05-manual-de-uso.md).

### 2.2 Containers de rede online (sem instalar nada localmente)

- **Google Cloud Shell** (`shell.cloud.google.com`, grátis, exige conta Google): uma máquina
  Linux no navegador com `ip`, `tcpdump`, `arp-scan` a um `sudo apt install` de distância.
  A tabela ARP dela reflete a rede virtual do Google — pobre, mas real.
- **Killercoda / Play with Docker** (`labs.play-with-docker.com`, grátis, exige conta Docker):
  ambiente Docker no navegador; ideal para o laboratório do §9.2 sem instalar Docker na sua
  máquina. As sessões expiram em ~4 h — **link temporário**.
- **tutorialspoint / webminal**: terminais Linux online, úteis para os comandos de leitura.

> Limitação honesta: ambientes na nuvem raramente deixam você fazer *broadcast* real de camada
> 2 nem colocar a placa em modo promíscuo, então **captura de ARP de outros hosts** costuma não
> funcionar. Para isso, o laboratório local do §9 é insubstituível.

---

## 3. Linux — Debian/Ubuntu

> **Testado em:** Ubuntu 22.04.5 LTS, kernel 6.8.0-136, em 14/08/2026.
> Família Debian: Debian 12/13, Ubuntu 22.04/24.04, Linux Mint, Pop!_OS, Kali.

### 3.1 O que já está lá

```bash
ip -V
# esperado: ip utility, iproute2-5.15.0, libbpf 0.5.0  (ou superior)
```
Se aparecer versão, **está instalado** — é o essencial. Se `command not found`:
```bash
sudo apt update && sudo apt install -y iproute2
```

### 3.2 Ferramentas de leitura extra e captura

```bash
sudo apt update
```
Atualiza a lista de pacotes. Faça sempre antes de instalar.

```bash
sudo apt install -y net-tools iputils-arping tcpdump arp-scan
```
Instala, em ordem: o comando legado `arp`; o `arping`; o `tcpdump`; e o `arp-scan`.

Verificação, uma por uma, com a saída esperada:

```bash
arp -V
# esperado: net-tools 1.60+git...  (linha "arp ... net-tools")
arping -V
# esperado: arping utility, iputils ...
tcpdump --version
# esperado: tcpdump version 4.99.1 ...  (libpcap embaixo)
arp-scan --version
# esperado: arp-scan 1.9.7 ...
```
*(as quatro saídas acima são as reais desta máquina)*

Se qualquer uma der `command not found`, o pacote não instalou — releia o §12.

### 3.3 arpwatch (monitor de mudanças, opcional)

```bash
sudo apt install -y arpwatch
```
Instala o daemon que registra pares IP↔MAC e alerta quando um muda (assinatura de ARP
spoofing). Configuração e uso no [18-seguranca](18-seguranca.md) §5.

### 3.4 Wireshark (gráfico, opcional)

```bash
sudo apt install -y wireshark
```
Durante a instalação aparece uma tela perguntando *"Should non-superusers be able to capture
packets?"* — **responda `Yes`**. Isso é o que permite capturar sem `sudo` (detalhes no §7.2).

```bash
sudo usermod -aG wireshark "$USER"
```
Adiciona o seu usuário ao grupo `wireshark`. **A mudança só vale após você sair e entrar de
novo** (logout/login) — não basta fechar o terminal. Confira depois com:

```bash
groups | tr ' ' '\n' | grep wireshark
# esperado: wireshark
```

Versão disponível no Ubuntu 22.04: **Wireshark 3.6.2**. A série atual upstream é a **4.6.x**
(4.6.8 em ago/2026, com correções de segurança). Para a versão nova:

```bash
sudo add-apt-repository -y ppa:wireshark-dev/stable
sudo apt update && sudo apt install -y wireshark
```

---

## 4. Linux — Fedora/RHEL

> **Família:** Fedora 40/41/42, RHEL 9/10, Rocky, AlmaLinux, CentOS Stream.
> Gerenciador: `dnf` (RHEL 7 antigo: `yum`, mesma sintaxe).

```bash
ip -V
```
Já vem instalado (pacote `iproute`). Se faltar: `sudo dnf install -y iproute`.

```bash
sudo dnf install -y net-tools iputils tcpdump arp-scan
```
`net-tools` traz o `arp`; `iputils` traz o `arping`; os outros dois têm o mesmo nome do
Debian. Verificação idêntica à do §3.2.

```bash
sudo dnf install -y wireshark      # inclui a GUI
sudo usermod -aG wireshark "$USER" # logout/login depois
```

`arpwatch`:
```bash
sudo dnf install -y arpwatch
```

> **Nota Fedora/SELinux:** com SELinux em *enforcing*, alguns daemons (arpwatch) podem ser
> bloqueados. Se algo não iniciar, verifique com `sudo ausearch -m avc -ts recent` e ajuste a
> política, ou rode em modo *permissive* só para testar (`sudo setenforce 0`, reversível).

---

## 5. macOS

> **Testado conceitualmente para:** macOS 14 (Sonoma) e 15 (Sequoia), Intel e Apple Silicon.
> A diferença Intel/ARM **não importa** aqui: todas as ferramentas são universais.
> *(Nota de transparência: este material foi produzido em Linux; os comandos macOS vêm da
> documentação oficial e da experiência, não de execução nesta sessão — declarado.)*

### 5.1 O que já está lá

macOS traz BSD `arp`, `ndp`, `netstat`, `tcpdump` e `ping` de fábrica. **Não** traz `ip` nem
`arp-scan`.

```bash
arp -a -n
# lista a tabela ARP; -n evita resolução de nomes (mais rápido e literal)
tcpdump --version
# esperado: tcpdump version 4.99.x ...
```

### 5.2 Homebrew (recomendado para o resto)

Se ainda não tem o Homebrew:
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```
Instala o gerenciador de pacotes de facto do macOS. No Apple Silicon ele instala em
`/opt/homebrew`; no Intel, em `/usr/local`. Ele avisa se precisar ajustar o PATH — **siga a
instrução impressa no fim** (é o §7.1).

```bash
brew install arp-scan nmap wireshark
```
`wireshark` via `brew install` instala a **versão de linha de comando** (`tshark`, `dumpcap`).
Para a interface gráfica:
```bash
brew install --cask wireshark
```

Verificação:
```bash
arp-scan --version   # esperado: arp-scan 1.10.x
nmap --version       # esperado: Nmap version 7.9x
```

### 5.3 Capturar no macOS

O macOS exige que o dispositivo de captura (`/dev/bpf*`) seja acessível. A instalação do
Wireshark (cask) instala um helper **ChmodBPF** que ajusta isso e pede sua senha de
administrador uma vez. Sem ele, capturar exige `sudo tcpdump`.

---

## 6. Windows (nativo e WSL2)

> **Testado conceitualmente para:** Windows 10 22H2 e Windows 11 24H2.
> **Caminho recomendado: WSL2** para os capítulos práticos, **nativo** para leitura rápida.
> Por quê: as ferramentas Linux (`ip`, `arp-scan`, `tcpdump`, Scapy) são muito superiores e
> o laboratório do §9 roda melhor; o Windows nativo é ótimo para `arp -a` e `Get-NetNeighbor`,
> mas pobre para captura e scripting.

### 6.1 Nativo — o que já existe

Abra **PowerShell** (não precisa ser admin para ler):

```powershell
arp -a
```
O comando `arp` clássico existe desde o Windows NT. Lista por interface.

```powershell
Get-NetNeighbor
```
O cmdlet moderno (Windows 8+). Mais rico: mostra o estado (`Reachable`, `Stale`, etc.),
filtrável e scriptável. **Para alterar** a tabela, abra o PowerShell **como administrador**.

`netsh` ainda funciona (`netsh interface ipv4 show neighbors`) mas a Microsoft o considera
legado — prefira `Get-NetNeighbor`.

### 6.2 Nativo — instalar ferramentas extras

Com **winget** (já vem no Windows 10 21H2+ e no 11):

```powershell
winget install WiresharkFoundation.Wireshark
winget install Insecure.Nmap
```
O instalador do Wireshark oferece o **Npcap** — a biblioteca de captura. **Aceite instalá-lo**;
sem Npcap não há captura no Windows. O Nmap também traz o Npcap embutido.

### 6.3 WSL2 (recomendado para a prática)

```powershell
wsl --install
```
Instala o WSL2 com Ubuntu por padrão. **Reinicie** quando ele pedir. Depois, dentro do Ubuntu
do WSL, siga **exatamente o §3** deste arquivo.

> **Aviso de rede no WSL2:** por padrão o WSL2 usa uma rede **NAT** virtualizada, então a
> tabela ARP que você vê lá dentro é a da rede interna do WSL, **não** a da sua rede física.
> Para ARP real da sua LAN, use o Windows nativo (§6.1), ou ative o modo de rede *mirrored*
> (`.wslconfig` com `networkingMode=mirrored`, disponível no Windows 11) — nesse modo o WSL
> compartilha a pilha de rede do Windows e a tabela reflete a LAN física.

---

## 7. PATH, permissões e captura sem root

### 7.1 PATH — quando o comando "não é encontrado" mesmo instalado

Sintoma: você instalou, mas `arp-scan` dá `command not found`.

Causa nº 1: o binário está num diretório que não está no `PATH`. Vários utilitários de rede
ficam em `/usr/sbin`, que **não** está no PATH de usuário comum em algumas distros.

```bash
echo $PATH | tr ':' '\n'
# procure se /usr/sbin e /sbin aparecem
ls -l /usr/sbin/arp-scan   # confirme onde o binário está
```

Correção — adicione ao seu perfil (`~/.bashrc` para bash, `~/.zshrc` para zsh):

```bash
echo 'export PATH="$PATH:/usr/sbin:/sbin"' >> ~/.bashrc
source ~/.bashrc
```
`source` recarrega o arquivo **na sessão atual**. Sem ele, a mudança só "pega" ao abrir um
terminal novo — essa é a causa nº 1 de "editei e não mudou nada".

No **macOS com Homebrew no Apple Silicon**, o PATH precisa de `/opt/homebrew/bin`:
```bash
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
```

### 7.2 Permissões — o certo e o errado com `sudo`

Regra geral:

| Ação | Precisa de privilégio? |
|---|---|
| **Ler** a tabela (`ip neigh show`, `arp -a`) | não |
| **Alterar** a tabela (`ip neigh add/del`) | sim (root/admin) |
| **Enviar** ARP com `arping` | sim (abre socket raw) |
| **Capturar** pacotes | sim — **mas há um jeito certo sem virar root** |
| **Varrer** com `arp-scan`/`nmap -sn` na LAN | sim (socket raw) |

O jeito **errado** e o **certo** de capturar sem root:

- ❌ **Errado:** rodar tudo com `sudo`, inclusive o Wireshark gráfico. Rodar uma GUI enorme
  como root é risco de segurança real — qualquer falha no dissecador vira falha como root, e
  os dissecadores do Wireshark já tiveram dezenas de CVEs (a própria 4.6.8 de ago/2026 corrige
  31 falhas).
- ✅ **Certo (Linux):** dar ao binário de captura a *capability* específica, em vez de todo o
  poder de root:
  ```bash
  sudo setcap cap_net_raw,cap_net_admin+eip $(which dumpcap)
  ```
  Concede **só** o direito de abrir sockets raw a esse binário. É o que a resposta `Yes` na
  instalação do Wireshark (§3.4) configura para você via o grupo `wireshark`.
- Para dar essa capacidade a um comando pontual (ex.: `arp-scan`) sem `sudo` toda vez:
  ```bash
  sudo setcap cap_net_raw+ep $(which arp-scan)
  ```

> **Por que não usar `sudo pip install` / `sudo npm -g`?** (aparece no §8.) Instalar pacotes
> Python/Node como root polui os diretórios do sistema, pode quebrar pacotes gerenciados pela
> distro e, se um pacote malicioso rodar código de instalação, ele roda **como root**. Use
> ambiente virtual (`venv`) ou `pipx` — mostrado no §8.

---

## 8. Scapy — o ARP programável

**Scapy** é uma biblioteca Python para montar, enviar e dissecar pacotes byte a byte. É o
que transforma o [12-anatomia-do-pacote](12-anatomia-do-pacote.md) de teoria em prática:
você monta um ARP request campo a campo e vê a resposta chegar.

### 8.1 Instalação isolada (recomendada) — pipx

```bash
# Debian/Ubuntu
sudo apt install -y pipx
pipx install scapy
```
`pipx` instala cada aplicação Python em seu próprio ambiente, sem sujar o sistema nem exigir
`sudo pip`. Verificação:
```bash
scapy -H 2>/dev/null; python3 -c "import scapy; print(scapy.__version__)"
```

### 8.2 Alternativa — venv (para usar como biblioteca no seu projeto)

```bash
python3 -m venv ~/.venvs/arp     # cria o ambiente
source ~/.venvs/arp/bin/activate # ativa (o prompt muda)
pip install scapy                # instala só dentro dele
python3 -c "from scapy.all import ARP; print('ok')"
```
Para sair do ambiente: `deactivate`.

### 8.3 Alternativa da distro (mais simples, versão mais antiga)

```bash
sudo apt install -y python3-scapy    # Ubuntu 22.04: Scapy 2.4.4
```

> Scapy **envia pacotes raw**, então os scripts que transmitem exigem `sudo` **ou** a
> *capability* do §7.2 no interpretador. Ler/dissecar não exige.

---

## 9. O laboratório isolado

Aqui você monta uma rede de brinquedo, sob seu controle total, onde pode fazer **qualquer
coisa** — inclusive os experimentos de envenenamento de cache do
[18-seguranca](18-seguranca.md) — sem tocar em rede de terceiros e sem risco legal.

### 9.1 Opção A — três VMs no VirtualBox (a mais fiel)

Necessária para os labs de ataque, porque simula camada 2 de verdade.

```bash
# Ubuntu/Debian
sudo apt install -y virtualbox
# Fedora
sudo dnf install -y VirtualBox
# macOS/Windows: baixe de virtualbox.org (instalador oficial)
```

Passos (resumo; roteiro completo no [70-pratica](70-pratica.md) lab 8):

1. Crie **uma rede interna** chamada `arplab`: no VirtualBox, cada VM → *Configurações → Rede →
   Conectado a: **Rede Interna** → Nome: `arplab`*. Rede interna **não** tem saída para a
   Internet nem para a sua LAN — é o isolamento que você quer.
2. Crie 3 VMs leves (Alpine ou Ubuntu Server), todas na rede `arplab`.
3. Dê IPs fixos na mesma sub-rede: `192.168.99.10/24`, `.11`, `.12`.
4. A partir daí, `ping`, `arp-scan`, Wireshark e os ataques rodam sem afetar ninguém.

### 9.2 Opção B — Docker (a mais rápida)

Suficiente para **ver ARP acontecer** entre dois hosts; ótima para o
[07-projeto-modelo](07-projeto-modelo/).

Instale o Docker (veja o assunto [docker](../docker/00-MAPA.md) desta pasta para o manual
completo por SO). Depois:

```bash
docker network create --driver bridge arplab
# cria uma rede bridge isolada, com seu próprio segmento e broadcast
```
```bash
docker run --rm -it --name h1 --network arplab --cap-add=NET_ADMIN alpine sh
# em outro terminal:
docker run --rm -it --name h2 --network arplab --cap-add=NET_ADMIN alpine sh
```
`--cap-add=NET_ADMIN` é o que permite **alterar** a tabela dentro do container (sem isso você
só lê). Dentro de cada container:
```sh
apk add --no-cache iproute2 iputils tcpdump   # Alpine usa apk
ip neigh show
ping h2         # do h1; observe a tabela se preencher
```

> **Cuidado com o Docker no ataque:** por padrão, uma bridge Docker isola razoavelmente, mas
> **não** é uma barreira de segurança forte para experimentos de spoofing. Para ataque, prefira
> a Opção A (VMs em rede interna). Para *observar* ARP, o Docker basta.

### 9.3 Opção C — namespaces de rede (Linux puro, zero instalação extra)

O truque mais elegante: dois "hosts" virtuais dentro do próprio kernel, sem VM nem container.

```bash
sudo ip netns add h1
sudo ip netns add h2
sudo ip link add veth1 type veth peer name veth2
sudo ip link set veth1 netns h1
sudo ip link set veth2 netns h2
sudo ip -n h1 addr add 10.0.0.1/24 dev veth1
sudo ip -n h2 addr add 10.0.0.2/24 dev veth2
sudo ip -n h1 link set veth1 up
sudo ip -n h2 link set veth2 up
sudo ip netns exec h1 ping -c1 10.0.0.2      # gera ARP
sudo ip netns exec h1 ip neigh show          # veja a entrada aprendida
```
Limpeza: `sudo ip netns del h1; sudo ip netns del h2`. Roteiro comentado no
[70-pratica](70-pratica.md) lab 7.

---

## 10. Rede corporativa

Se você está atrás de um proxy corporativo, os instaladores de pacote podem falhar.

**apt (Debian/Ubuntu):**
```bash
# arquivo /etc/apt/apt.conf.d/95proxy
Acquire::http::Proxy "http://usuario:senha@proxy.empresa:8080";
Acquire::https::Proxy "http://usuario:senha@proxy.empresa:8080";
```

**pipx/pip e Homebrew** respeitam as variáveis de ambiente:
```bash
export http_proxy=http://proxy.empresa:8080
export https_proxy=http://proxy.empresa:8080
```
Adicione ao `~/.bashrc` se for permanente.

**Certificado interno (TLS interceptado):** se `pip`/`brew` reclamam de certificado, o proxy
corporativo está inspecionando TLS. A correção **certa** é adicionar o certificado raiz da
empresa ao *trust store* do sistema (`update-ca-certificates` no Debian). Não desative a
verificação de certificado — isso te deixa vulnerável ao ataque que este curso ensina a
detectar.

> **Nota especial:** `arp-scan`, `nmap -sn` e captura promíscua **disparam alertas** em redes
> corporativas monitoradas (IDS). Combine com a equipe de segurança antes, ou use o
> laboratório do §9. Varrer a rede da empresa sem avisar pode custar seu emprego — e, se não
> houver autorização, é o art. 154-A de novo.

---

## 11. Atualizar, reverter, desinstalar

### Atualizar
```bash
# Debian/Ubuntu
sudo apt update && sudo apt upgrade -y net-tools iproute2 tcpdump arp-scan wireshark
# Fedora
sudo dnf upgrade -y iproute net-tools tcpdump arp-scan wireshark
# macOS
brew upgrade
# Windows
winget upgrade --all
```

### Reverter uma versão problemática (apt)
```bash
apt-cache policy tcpdump           # veja as versões disponíveis
sudo apt install tcpdump=4.99.1-3ubuntu0.2   # fixe uma versão específica
```

### Desinstalar por completo
```bash
# Debian/Ubuntu — remove pacote + arquivos de configuração
sudo apt purge -y arp-scan arpwatch wireshark
sudo apt autoremove -y             # remove dependências que ficaram órfãs
```
Artefatos que ficam para trás e você deve limpar à mão:
```bash
# grupo criado pelo Wireshark
sudo groupdel wireshark 2>/dev/null
# capabilities aplicadas manualmente (§7) — revertem ao reinstalar, mas para limpar:
sudo setcap -r $(which dumpcap) 2>/dev/null
# dados do arpwatch
sudo rm -rf /var/lib/arpwatch
# ambiente do pipx/venv
pipx uninstall scapy; rm -rf ~/.venvs/arp
# rede e containers do lab Docker
docker network rm arplab; docker ps -aq | xargs -r docker rm -f
# namespaces do §9.3
sudo ip netns del h1 2>/dev/null; sudo ip netns del h2 2>/dev/null
```

`iproute2` e `net-tools` **não devem ser removidos** — são parte da base do sistema e outras
coisas dependem deles.

---

## 12. Solução de problemas

Mensagens de erro **literais**, causa e correção. Os cinco (e mais alguns) erros mais comuns:

| Mensagem | Causa provável | Correção |
|---|---|---|
| `bash: arp-scan: command not found` | binário em `/usr/sbin`, fora do PATH; ou não instalado | `ls /usr/sbin/arp-scan`; se existe, §7.1; se não, reinstale |
| `arp-scan: WARNING: Cannot open MAC/Vendor file ...` | base OUI não encontrada | reinstale o pacote; ou passe `--macfile` apontando para `ieee-oui.txt` |
| `You don't have permission to capture on that device` (Wireshark/tcpdump) | usuário sem `cap_net_raw`; falta grupo `wireshark` | §7.2; e faça **logout/login** após `usermod -aG` |
| `Operation not permitted` ao rodar `ip neigh add` | alteração exige root | prefixe `sudo`; ou, no container, `--cap-add=NET_ADMIN` |
| `arping: socket: Operation not permitted` | socket raw sem privilégio | `sudo arping ...` ou `setcap cap_net_raw+ep $(which arping)` |
| `E: Unable to locate package arp-scan` | lista de pacotes desatualizada; ou repositório `universe` desabilitado | `sudo apt update`; no Ubuntu, `sudo add-apt-repository universe` |
| `E: Could not get lock /var/lib/dpkg/lock-frontend` | outro apt rodando (ex.: atualização automática) | aguarde, ou `sudo lsof /var/lib/dpkg/lock-frontend` e finalize o processo |
| `neighbour: arp_cache: neighbor table overflow!` (no `dmesg`) | tabela de vizinhos cheia — rede grande demais ou varredura agressiva | aumente `gc_thresh1/2/3` ([14](14-a-tabela-por-dentro.md) §7); ou segmente a rede |
| `Npcap ... not installed` (Windows, Wireshark) | captura sem a lib | reinstale o Wireshark e **aceite o Npcap**; ou `winget install Insecure.Npcap` |
| WSL2: `arp -a` mostra só o gateway NAT | rede NAT do WSL, não a LAN física | use PowerShell nativo, ou modo `mirrored` (§6.3) |

---

## 13. Checklist de ambiente pronto

Rode cada linha; se todas responderem, o ambiente está pronto para o
[04-como-comecar](04-como-comecar.md).

```bash
# Leitura (o essencial — deve funcionar sem sudo)
ip neigh show          >/dev/null && echo "OK ler tabela (Linux)"      # ou: arp -a
# Identidade da máquina
ip -br addr show       >/dev/null && echo "OK ver IP/máscara"
ip route | grep -q default && echo "OK ver gateway"
# Captura (se instalou)
command -v tcpdump     >/dev/null && echo "OK tcpdump"
# Varredura (se instalou)
command -v arp-scan    >/dev/null && echo "OK arp-scan"
command -v arping      >/dev/null && echo "OK arping"
# Scripting (se instalou)
python3 -c "import scapy" 2>/dev/null && echo "OK Scapy" || echo "Scapy: opcional, ver §8"
# Laboratório (escolha um)
command -v docker      >/dev/null && echo "OK Docker (lab §9.2)"
command -v ip          >/dev/null && echo "OK namespaces (lab §9.3, zero instalação)"
```

Mínimo absoluto para prosseguir: a **primeira linha** funcionar. Todo o resto é opcional e
pode ser instalado quando o capítulo correspondente pedir.

---

## Autoteste

1. Você só quer **ler** a tabela ARP. Precisa instalar alguma coisa? Em qual dos três sistemas?
2. Por que é má ideia rodar o Wireshark gráfico com `sudo`, e qual é a alternativa correta?
3. Você instalou `arp-scan` mas o terminal diz `command not found`. Quais são as duas causas
   mais prováveis e como distingue uma da outra?
4. Qual a diferença prática, para este curso, entre a rede NAT e a rede *mirrored* do WSL2?
5. Por que preferir `pipx`/`venv` a `sudo pip install` para o Scapy?
6. Você quer testar ARP spoofing sem risco legal. Qual das três opções de laboratório do §9
   escolhe, e por quê?
7. Editou o `~/.bashrc` para corrigir o PATH e o comando continua não sendo encontrado no
   terminal já aberto. O que faltou?

---

**Fontes consultadas (14/08/2026):** versões locais reais (`iproute2 5.15.0`, `net-tools
1.60`, `tcpdump 4.99.1`, `arp-scan 1.9.7`, `nmap` local, Ubuntu 22.04.5); `apt-cache policy`
para candidatos (`iputils-arping 3:20211215`, `wireshark 3.6.2`, `arpwatch 2.1a15`,
`python3-scapy 2.4.4`); documentação Microsoft `Get-NetNeighbor`; notas de versão do Wireshark
(4.6.8, ago/2026) e do Nmap (7.991, 05/08/2026), pesquisadas na web.

**Próximo:** [04-como-comecar.md](04-como-comecar.md)
