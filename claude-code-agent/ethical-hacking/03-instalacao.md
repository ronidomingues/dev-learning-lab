# 03 · Manual de instalação do laboratório

`Nível: iniciante` · `Última atualização: 12/08/2026`
`Testado em: Kali Linux 2026.2 · VirtualBox 7.2.14 · Docker Engine 29.x · Burp Suite 2026.4.x`

Este é o arquivo mais chato de escrever e o que mais salva iniciante. Siga na ordem.
Não improvise. Cada passo tem verificação com a saída esperada.

> ⚠️ **Antes de tudo.** O laboratório que você vai montar contém máquinas
> **intencionalmente vulneráveis**. Se elas ficarem acessíveis pela internet ou pela sua rede
> doméstica, você criou um problema real. A seção **§8 · Isolamento de rede** não é opcional —
> é a parte mais importante deste arquivo. Se ler só uma seção, leia aquela.

---

## Índice

1. [Alternativa sem instalar nada — comece hoje](#1-alternativa-sem-instalar-nada--comece-hoje)
2. [Visão geral: o que você vai instalar e por quê](#2-visão-geral-o-que-você-vai-instalar-e-por-quê)
3. [Passo 1 — Hipervisor (Linux, Windows, macOS)](#3-passo-1--hipervisor)
4. [Passo 2 — Kali Linux (a máquina de ataque)](#4-passo-2--kali-linux)
5. [Passo 3 — Alvos vulneráveis](#5-passo-3--alvos-vulneráveis)
6. [Passo 4 — Docker (alvos web modernos)](#6-passo-4--docker)
7. [Passo 5 — Ferramentas fora do Kali: Burp, Python, Go](#7-passo-5--ferramentas-fora-do-kali)
8. [**Isolamento de rede — obrigatório**](#8-isolamento-de-rede--obrigatório)
9. [PATH, variáveis de ambiente e permissões](#9-path-variáveis-de-ambiente-e-permissões)
10. [Rede corporativa: proxy, certificado, firewall](#10-rede-corporativa)
11. [Snapshots, atualização e como voltar atrás](#11-snapshots-atualização-e-como-voltar-atrás)
12. [Desinstalação completa](#12-desinstalação-completa)
13. [Solução de problemas — erros literais](#13-solução-de-problemas)
14. [Checklist "ambiente pronto"](#14-checklist-ambiente-pronto)

---

## 1. Alternativa sem instalar nada — comece hoje

**Leia isto antes de baixar 15 GB.** Você pode começar a praticar em 10 minutos, de graça,
sem instalar coisa alguma. Faça isso hoje e instale o laboratório local no fim de semana.

| Plataforma | O que oferece de graça | Precisa instalar? | Link |
|---|---|---|---|
| **PortSwigger Web Security Academy** | 250+ laboratórios web, o melhor material gratuito que existe sobre segurança web | Só o navegador (o Burp Community ajuda, mas boa parte funciona sem) | [portswigger.net/web-security](https://portswigger.net/web-security) |
| **TryHackMe** | Salas gratuitas + máquina Kali no navegador (o "AttackBox" tem cota mensal no plano free) | Nada | [tryhackme.com](https://tryhackme.com) |
| **Hack The Box** | Máquinas ativas e parte do HTB Academy | Só VPN, para as máquinas | [hackthebox.com](https://hackthebox.com) |
| **OverTheWire** | Wargames de Linux via SSH | Só um cliente SSH | [overthewire.org](https://overthewire.org) |
| **picoCTF** | CTF educacional da Carnegie Mellon, com *webshell* no navegador | Nada | [picoctf.org](https://picoctf.org) |
| **Root-Me** | 500+ desafios, interface em PT/EN/FR | Nada | [root-me.org](https://www.root-me.org) |

**Recomendação:** faça hoje o "Getting started" da PortSwigger Academy e o Bandit do
OverTheWire. Se depois de duas semanas você ainda estiver empolgado, aí sim monte o laboratório
local. Isso evita que você gaste um sábado instalando algo que vai abandonar.

**Quando o laboratório local é obrigatório:** para praticar Active Directory, ataques de rede
interna, wireless, e para ter algo que funcione sem internet. Também porque em um teste real
você vai montar ambiente — aprender a montar é parte da profissão.

---

## 2. Visão geral: o que você vai instalar e por quê

```mermaid
flowchart TB
    subgraph HOST["Seu computador (hospedeiro)"]
        HV["Hipervisor<br/>VirtualBox / VMware / KVM"]
        BURP["Burp Suite<br/>(pode ficar no host ou no Kali)"]
    end
    subgraph NET["Rede isolada — host-only / interna"]
        KALI["Kali Linux<br/>máquina de ataque<br/>192.168.56.10"]
        M2["Metasploitable 2<br/>alvo Linux clássico<br/>192.168.56.20"]
        DOCK["Docker no Kali<br/>Juice Shop · DVWA · WebGoat"]
        AD["(opcional)<br/>Windows Server<br/>laboratório AD"]
    end
    HV --> KALI
    HV --> M2
    HV --> AD
    KALI --> DOCK
    KALI -. "ataca" .-> M2
    KALI -. "ataca" .-> AD
```

| Componente | Para quê | Obrigatório? | Espaço |
|---|---|---|---|
| **Hipervisor** | Rodar as máquinas virtuais | Sim | ~500 MB |
| **Kali Linux** | Distribuição com ~600 ferramentas ofensivas pré-instaladas | Sim (ou Parrot) | ~25 GB |
| **Metasploitable 2** | Alvo Linux propositalmente vulnerável, clássico do ensino | Sim | ~2 GB |
| **Docker** | Subir alvos web modernos em um comando | Muito recomendado | ~2 GB + imagens |
| **Burp Suite Community** | Proxy de interceptação — a ferramenta nº 1 de web | Sim | ~1 GB (inclui Java) |
| **Windows Server + Win11 Eval** | Laboratório de Active Directory | Depois, quando chegar no `20` | ~80 GB |

**Total realista para começar: ~35 GB.** Com o laboratório AD: ~120 GB.

### Por que Kali e não outra distro?

| Distro | Quando escolher |
|---|---|
| **Kali Linux** | Padrão do mercado, mais documentação, é o que os cursos e certificações assumem. **Escolha esta se está em dúvida.** |
| **Parrot Security OS** | Mais leve, base Debian também, bom em máquina fraca. Ótima alternativa. |
| **BlackArch** | Baseada em Arch, ~2900 ferramentas. Para quem já domina Arch. Não é para iniciante. |
| **Ubuntu + ferramentas instaladas à mão** | O que muitos profissionais experientes usam no dia a dia. Você aprende mais, mas gasta tempo. Faça isso no ano 2, não no mês 1. |

> **Opinião profissional:** o Kali é uma *ferramenta de trabalho*, não um sistema operacional
> para viver. Ele é feito para rodar como root ou com sudo largo, atualiza agressivamente
> (rolling release) e quebra de vez em quando. Não use Kali como seu SO principal. Isso é
> consenso entre profissionais, apesar de ser o contrário do que os vídeos de YouTube sugerem.

---

## 3. Passo 1 — Hipervisor

**Hipervisor** é o software que cria e roda máquinas virtuais. Escolha um só.

| Opção | Custo (12/08/2026) | Plataformas | Recomendação |
|---|---|---|---|
| **VirtualBox 7.2.14** | Gratuito (GPLv3; o *Extension Pack* tem licença PUEL, gratuito só para uso pessoal/avaliação) | Windows, Linux, macOS Intel | **Padrão para iniciante.** Mais tutoriais. |
| **VMware Workstation Pro / Fusion Pro** | **Gratuito** para uso pessoal, educacional e comercial desde nov/2024 (Broadcom), sem suporte por ticket | Windows, Linux, macOS | Melhor desempenho de I/O. Boa escolha. |
| **KVM + virt-manager** | Gratuito, GPL | Só Linux | **Melhor opção em hospedeiro Linux.** Nativo do kernel, mais rápido. |
| **Hyper-V** | Incluso no Windows Pro/Enterprise | Windows | Funciona, mas conflita com VirtualBox/VMware. Evite misturar. |
| **UTM (QEMU)** | Gratuito | macOS Apple Silicon | Único caminho decente no M1–M4. Veja §3.4. |

### 3.1 Linux — família Debian/Ubuntu

**Caminho recomendado: KVM.** É nativo, mais rápido e não tem módulo de kernel de terceiro
para quebrar a cada atualização.

```bash
# 1. Verifica se o processador suporta virtualização (precisa ser > 0)
grep -Ec '(vmx|svm)' /proc/cpuinfo
# esperado: um número maior que 0 (ex.: 8)
# se der 0: habilite VT-x/AMD-V na BIOS e reinicie
```

```bash
# 2. Instala KVM, o gerenciador gráfico e as ferramentas de rede
sudo apt update && sudo apt install -y qemu-kvm libvirt-daemon-system libvirt-clients bridge-utils virt-manager
```

```bash
# 3. Coloca seu usuário nos grupos que permitem gerenciar VMs sem sudo
sudo usermod -aG libvirt,kvm "$USER"
```

```bash
# 4. FAÇA LOGOUT E LOGIN (ou reinicie). Grupos só valem na próxima sessão.
#    Depois, verifique:
groups | tr ' ' '\n' | grep -E 'libvirt|kvm'
# esperado: kvm
#           libvirt
```

```bash
# 5. Confirma que o serviço está de pé
systemctl is-active libvirtd
# esperado: active
```

```bash
# 6. Teste final
virsh list --all
# esperado: um cabeçalho de tabela vazio (Id  Nome  Estado) — sem erro de permissão
```

**Se o passo 6 der `failed to connect to the hypervisor`:** você não fez logout no passo 4.
Faça. É literalmente o erro mais comum aqui.

**Alternativa Debian/Ubuntu — VirtualBox** (se você prefere seguir tutoriais que usam VBox):

```bash
# Repositório oficial da Oracle — NÃO use o pacote do Ubuntu, costuma estar velho
wget -O- https://www.virtualbox.org/download/oracle_vbox_2016.asc \
  | sudo gpg --dearmor -o /usr/share/keyrings/oracle-vbox-2016.gpg
```
```bash
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/oracle-vbox-2016.gpg] https://download.virtualbox.org/virtualbox/debian $(lsb_release -cs) contrib" \
  | sudo tee /etc/apt/sources.list.d/virtualbox.list
```
```bash
sudo apt update && sudo apt install -y virtualbox-7.2
```
```bash
vboxmanage --version
# esperado: 7.2.14r... (ou superior)
```
```bash
# VirtualBox precisa do seu usuário no grupo vboxusers para USB funcionar
sudo usermod -aG vboxusers "$USER"   # exige logout/login
```

> **Secure Boot no Ubuntu quebra o VirtualBox.** Se aparecer
> `Kernel driver not installed (rc=-1908)`, os módulos do VBox não foram assinados. Ou você
> desabilita o Secure Boot na UEFI, ou assina os módulos com MOK. O KVM não tem esse problema —
> mais um motivo para preferi-lo no Linux.

### 3.2 Linux — família Fedora/RHEL

```bash
# KVM no Fedora — grupo de pacotes pronto
sudo dnf install -y @virtualization
```
```bash
sudo systemctl enable --now libvirtd
systemctl is-active libvirtd
# esperado: active
```
```bash
sudo usermod -aG libvirt "$USER"   # logout/login depois
```
```bash
virt-host-validate | grep -i "QEMU: Checking for hardware virtualization"
# esperado: QEMU: Checking for hardware virtualization                    : PASS
```

### 3.3 Windows 10/11

**Caminho recomendado: VMware Workstation Pro (gratuito) ou VirtualBox.**

1. Baixe:
   - VirtualBox: [virtualbox.org/wiki/Downloads](https://www.virtualbox.org/wiki/Downloads) → "Windows hosts"
   - VMware Workstation Pro: pelo portal da Broadcom (exige conta gratuita) —
     [support.broadcom.com](https://support.broadcom.com), busque *VMware Workstation Pro*.
2. Execute o instalador. Aceite os padrões. Ele vai avisar que a rede vai cair por alguns
   segundos — é normal, ele instala adaptadores virtuais.
3. Verifique no PowerShell:

```powershell
& "C:\Program Files\Oracle\VirtualBox\VBoxManage.exe" --version
# esperado: 7.2.14r...
```

**Conflito crítico no Windows:** Hyper-V, WSL2, Docker Desktop, Windows Sandbox, *Core
Isolation* e *Credential Guard* usam o hipervisor da Microsoft e **competem** com
VirtualBox/VMware. Sintoma: VMs lentíssimas, ou erro `VT-x is not available (VERR_VMX_NO_VMX)`.

Verifique:
```powershell
# Se disser "Um hipervisor foi detectado", o Hyper-V está ativo
systeminfo | Select-String -Pattern "Hyper-V"
```

Duas saídas possíveis:

- **Você quer usar WSL2 e Docker Desktop:** mantenha o Hyper-V. VirtualBox 7.x funciona nesse
  modo, mas mais devagar. Aceitável para começar.
- **Você quer desempenho máximo nas VMs:** desligue o Hyper-V. Em PowerShell **como
  administrador**:

```powershell
bcdedit /set hypervisorlaunchtype off
Disable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V-All -NoRestart
# reinicie a máquina
```
Para reverter: `bcdedit /set hypervisorlaunchtype auto` e reinicie.

**WSL2 é alternativa ao hipervisor?** Não para este laboratório. WSL2 é ótimo para *usar*
ferramentas Linux no Windows, mas a rede dele é NAT gerenciada pela Microsoft e complica
alvos vulneráveis e ataques de camada 2. Use VM de verdade.

### 3.4 macOS

**Intel:** VirtualBox ou VMware Fusion Pro (gratuito). Sem particularidades.

```bash
brew install --cask virtualbox
VBoxManage --version
```
Se o macOS bloquear, vá em *Ajustes do Sistema → Privacidade e Segurança* e clique em
*Permitir* para "Oracle". Depois reinicie o instalador.

**Apple Silicon (M1/M2/M3/M4) — leia com atenção.**
O processador é ARM64. Ele **não roda x86-64 nativamente**. Consequências:

| O que você quer | Funciona? | Como |
|---|---|---|
| Kali como atacante | ✅ Sim | Imagem **ARM64** do Kali no UTM ou VMware Fusion |
| Alvos x86 antigos (Metasploitable 2, muito VulnHub) | ⚠️ Só emulado | UTM em modo *Emulate*, com QEMU. **Muito lento** (5–20× mais devagar) |
| Alvos web em Docker | ✅ Sim | Muitas imagens têm build `arm64`; as que não têm rodam via Rosetta/QEMU |
| Laboratório Windows AD | ⚠️ Difícil | Windows 11 ARM funciona; Windows Server ARM é limitado |
| Exploração de binário x86 | ❌ Na prática, não | Use nuvem |

```bash
# Apple Silicon: instale o UTM
brew install --cask utm
```

**Minha recomendação para Apple Silicon:** use o Mac como cliente e coloque o laboratório em
outro lugar — TryHackMe/HTB no navegador, ou uma VPS barata (§ nota abaixo), ou um mini-PC x86
usado. Insistir em emular x86 no Mac vai fazer você odiar a área por lentidão que não é culpa
sua.

> **VPS como laboratório:** funciona para o Kali (uma máquina de ataque na nuvem), mas
> **nunca** suba alvos vulneráveis em VPS com IP público — eles serão comprometidos de verdade,
> em horas, e a responsabilidade é sua. Se usar VPS, mantenha os alvos numa rede privada e o
> acesso por VPN. Verifique também os termos do provedor: quase todos proíbem *scanning* de
> alvos externos, e você pode perder a conta.

---

## 4. Passo 2 — Kali Linux

### 4.1 Qual imagem baixar

O Kali oferece várias imagens. Para laboratório, use a **pré-construída para VM** — ela já vem
instalada, poupa 40 minutos e evita erro de particionamento.

| Imagem | Quando usar |
|---|---|
| **Virtual Machines** (`.7z` para VirtualBox/VMware) | ✅ **Use esta.** Pronta para importar. |
| **Installer** (`.iso`) | Instalação em disco real ou VM feita à mão. |
| **NetInstaller** (`.iso` pequeno) | Instalação mínima, baixa tudo da internet. |
| **Live** (`.iso`) | Rodar sem instalar, do pendrive. Útil para perícia. |
| **WSL** | Kali dentro do Windows. Sem GUI e sem rede de baixo nível. Complementar, não substituto. |
| **ARM64** | Raspberry Pi, Apple Silicon. |

Baixe em: [kali.org/get-kali/#kali-virtual-machines](https://www.kali.org/get-kali/#kali-virtual-machines)

### 4.2 Verificar a integridade do download — **não pule**

Você está baixando um sistema operacional que vai rodar com privilégio na sua máquina.
Verificar a assinatura não é paranoia; é higiene básica, e é constrangedor um profissional de
segurança não fazer.

```bash
# Linux/macOS — compare com o SHA256 publicado na página de download do Kali
sha256sum kali-linux-2026.2-virtualbox-amd64.7z
# esperado: o mesmo hash listado em https://www.kali.org/get-kali/
```
```powershell
# Windows PowerShell
Get-FileHash .\kali-linux-2026.2-virtualbox-amd64.7z -Algorithm SHA256
```

Se o hash não bater: **apague e baixe de novo**, de preferência do site oficial e não de espelho.

### 4.3 Importar a VM

**VirtualBox:**
```bash
# 1. Extraia o .7z (instale o p7zip se preciso: sudo apt install p7zip-full)
7z x kali-linux-2026.2-virtualbox-amd64.7z
```
Depois: VirtualBox → *Máquina* → *Adicionar…* → selecione o arquivo `.vbox` extraído.

**VMware:** extraia e abra o arquivo `.vmx`. Escolha "Copiei" quando ele perguntar se moveu
ou copiou (isso gera novos endereços MAC).

**KVM/virt-manager:** use a imagem `.qcow2` do Kali, ou converta o `.vmdk`:
```bash
qemu-img convert -O qcow2 kali-linux-2026.2-vmware-amd64.vmdk kali.qcow2
```

### 4.4 Ajustar recursos antes de ligar

| Recurso | Mínimo | Recomendado |
|---|---|---|
| RAM | 2048 MB | **4096 MB** |
| CPU | 2 | 2–4 |
| Vídeo | 64 MB, VMSVGA | 128 MB |
| Disco | 25 GB (o padrão da imagem) | 40 GB se for compilar coisas |
| Rede | ver §8 | **Host-only + NAT** |

Não dê mais da metade dos núcleos do hospedeiro para a VM — o hospedeiro precisa respirar.

### 4.5 Primeiro login e primeiras tarefas

As imagens oficiais pré-construídas vêm com usuário **`kali`** e senha **`kali`**.

```bash
# 1. TROQUE A SENHA. Agora. Antes de qualquer outra coisa.
passwd
```

```bash
# 2. Atualize tudo. O Kali é rolling release; a imagem já nasce alguns dias velha.
sudo apt update && sudo apt full-upgrade -y
# demora de 10 a 40 minutos na primeira vez. Se der erro de chave, veja §13.
```

```bash
# 3. Verifique a versão
cat /etc/os-release | head -3
# esperado: PRETTY_NAME="Kali GNU/Linux Rolling"
```
```bash
grep VERSION /etc/os-release
# esperado: VERSION="2026.2" (ou superior)
```

```bash
# 4. Confirme que as ferramentas essenciais estão lá
for t in nmap ffuf gobuster netexec sqlmap hydra john hashcat msfconsole; do
  printf '%-12s ' "$t"; command -v "$t" >/dev/null && echo OK || echo "FALTANDO"
done
# esperado: todas OK. As que faltarem, instale com: sudo apt install -y <nome>
```

```bash
# 5. Inicialize o banco do Metasploit (senão toda busca fica lenta)
sudo msfdb init
msfconsole -q -x "db_status; exit"
# esperado: [*] Connected to msf. Connection type: postgresql.
```

```bash
# 6. Instale o metapacote grande, se quiser tudo (opcional, ~10 GB)
sudo apt install -y kali-linux-large
```

**Metapacotes do Kali** — o que vem em cada um:

| Metapacote | Conteúdo | Tamanho aprox. |
|---|---|---|
| `kali-linux-core` | o mínimo | ~1 GB |
| `kali-linux-default` | o que vem na imagem padrão | ~10 GB |
| `kali-linux-large` | default + muita coisa a mais | ~20 GB |
| `kali-linux-everything` | tudo, ~600 ferramentas | ~50 GB |
| `kali-tools-web`, `kali-tools-wireless`, `kali-tools-windows-resources`… | por especialidade | varia |

Recomendação: fique no `default` e instale o que faltar sob demanda. `everything` enche o
disco de coisa que você nunca vai abrir.

### 4.6 Guest Additions / VMware Tools

Sem isso você não tem tela cheia nem copiar-e-colar entre hospedeiro e VM — e você vai
copiar e colar o dia inteiro.

```bash
# No Kali, ambos já vêm instalados nas imagens oficiais. Confirme:
systemctl is-active vboxservice        # VirtualBox
systemctl is-active vmtoolsd 2>/dev/null || systemctl is-active open-vm-tools  # VMware
# esperado: active (dependendo do hipervisor usado)
```

Se não estiver:
```bash
sudo apt install -y virtualbox-guest-x11     # VirtualBox
sudo apt install -y open-vm-tools-desktop    # VMware
sudo reboot
```

### 4.7 **Tire um snapshot agora**

```bash
# No hospedeiro, com a VM desligada (VirtualBox):
VBoxManage snapshot "Kali Linux 2026.2" take "base-limpa" --description "Kali atualizado, antes de qualquer bagunca"
```
Isto vai te salvar. Kali quebra. Você vai instalar algo que conflita. Com snapshot, voltar
custa 30 segundos; sem snapshot, custa uma tarde. Veja §11.

---

## 5. Passo 3 — Alvos vulneráveis

**Regra absoluta:** todo alvo desta seção vai na rede isolada da §8. Nenhum deles com acesso
à internet ou à sua rede doméstica.

### 5.1 Metasploitable 2 — o alvo Linux clássico

Ubuntu 8.04 recheado de serviços vulneráveis. Datado (2012), mas continua sendo o melhor
primeiro alvo porque quase tudo nele funciona e há material didático farto.

```bash
# 1. Baixe de: https://sourceforge.net/projects/metasploitable/files/Metasploitable2/
unzip metasploitable-linux-2.0.0.zip
```
Importe o `.vmdk` no seu hipervisor como disco de uma VM nova (Linux 64-bit, 512 MB RAM).

```
Usuário: msfadmin
Senha:   msfadmin
```

```bash
# Verificação — a partir do Kali, na mesma rede isolada:
ping -c 2 192.168.56.20
nmap -sV -p 21,22,80,445 192.168.56.20
# esperado: portas abertas, vsftpd 2.3.4, OpenSSH 4.7p1, Apache 2.2.8, Samba 3.X
```

### 5.2 Metasploitable 3 — mais moderno, mais trabalhoso

Versões Ubuntu 14.04 e Windows Server 2008. Construído com Vagrant + Packer, o que significa
que você monta a imagem em vez de baixá-la pronta. Vale a pena depois do 2.
Repositório: [github.com/rapid7/metasploitable3](https://github.com/rapid7/metasploitable3)

### 5.3 VulnHub — centenas de máquinas gratuitas

[vulnhub.com](https://www.vulnhub.com) — imagens `.ova` prontas, cada uma um desafio completo
com write-ups públicos. Comece por: **Basic Pentesting 1**, **Kioptrix Level 1**,
**Mr-Robot**, **DC-1**.

> **Cuidado real:** você está baixando VMs feitas por desconhecidos e executando-as. Isolamento
> de rede (§8) resolve o risco prático. Ainda assim, não coloque dado seu dentro delas e não
> use pastas compartilhadas com o hospedeiro.

### 5.4 Laboratório Active Directory (faça depois, no `20`)

Precisa de ~80 GB e 16 GB de RAM. Usa ISOs de avaliação legítimas e gratuitas da Microsoft
(180 dias):

- Windows Server 2022/2025 Evaluation → [microsoft.com/evalcenter](https://www.microsoft.com/en-us/evalcenter/evaluate-windows-server-2022)
- Windows 11 Enterprise Evaluation (90 dias) → mesmo portal

Montagem automatizada (recomendado, poupa dias):
- [**GOAD** — Game of Active Directory](https://github.com/Orange-Cyberdefense/GOAD): laboratório AD vulnerável, provisionado com Vagrant + Ansible. Padrão do mercado para estudo.
- [**Ludus**](https://ludus.cloud): provisionamento de laboratórios com um arquivo de configuração. Precisa de um servidor Proxmox.

Passo a passo em [`20-active-directory.md`](20-active-directory.md).

---

## 6. Passo 4 — Docker

Docker é o jeito mais rápido de ter alvos web modernos. Rode-o **dentro do Kali**, não no
hospedeiro — assim os contêineres nascem na rede isolada.

```bash
# No Kali (Debian-based) — o Kali empacota o docker.io nos próprios repositórios
sudo apt update && sudo apt install -y docker.io docker-compose-v2
```
```bash
sudo systemctl enable --now docker
systemctl is-active docker
# esperado: active
```
```bash
# Permitir usar docker sem sudo
sudo usermod -aG docker "$USER"
newgrp docker    # ou faça logout/login
```
```bash
docker run --rm hello-world
# esperado: "Hello from Docker!" seguido de um parágrafo explicativo
```

> **Sobre `usermod -aG docker`:** quem está no grupo `docker` é equivalente a root na máquina
> (é trivial montar `/` dentro de um contêiner). Numa VM de laboratório isso é aceitável.
> Num servidor de produção, **não é** — use `sudo docker` ou modo *rootless*. Vale saber a
> diferença, porque isso é um achado recorrente em pentest de infraestrutura.

### 6.1 Alvos web em um comando

```bash
# OWASP Juice Shop — o alvo web moderno de referência (Node/Angular, ~100 desafios)
docker run --rm -d -p 3000:3000 --name juice bkimminich/juice-shop
# acesse http://localhost:3000 no navegador do Kali
```
```bash
# DVWA — Damn Vulnerable Web Application (PHP, o clássico didático)
docker run --rm -d -p 8080:80 --name dvwa vulnerables/web-dvwa
# http://localhost:8080  — login: admin / password  → clique em "Create/Reset Database"
```
```bash
# WebGoat — tutorial guiado da OWASP, ótimo para entender a causa de cada falha
docker run --rm -d -p 8081:8080 -p 9090:9090 --name webgoat webgoat/webgoat
# http://localhost:8081/WebGoat
```
```bash
# Verificação geral
docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'
# esperado: três linhas, status "Up ..."
```
```bash
# Parar tudo quando terminar (economiza RAM)
docker stop juice dvwa webgoat
```

---

## 7. Passo 5 — Ferramentas fora do Kali

### 7.1 Burp Suite — obrigatório para web

O Kali já traz o **Burp Suite Community**. Confirme e, se quiser a versão mais nova:

```bash
burpsuite --version 2>/dev/null || echo "não instalado"
sudo apt install -y burpsuite
```

Ou baixe direto de [portswigger.net/burp/communitydownload](https://portswigger.net/burp/communitydownload)
(o instalador `.sh` traz o próprio Java — não precisa instalar JDK).

**Community × Professional** — a diferença que importa:

| Recurso | Community (grátis) | Professional (US$ 499/ano/usuário, preço de 12/08/2026) |
|---|---|---|
| Proxy, Repeater, Decoder | ✅ | ✅ |
| Intruder | ⚠️ com atraso artificial (inutilizável para força bruta séria) | ✅ sem limite |
| Scanner automático | ❌ | ✅ |
| Salvar projeto em disco | ❌ | ✅ |
| BApp Store completa | parcial | ✅ |

Para estudar, a Community basta — a PortSwigger Academy inteira é resolvível com ela.
Para trabalhar profissionalmente com web, a Professional se paga na primeira semana.
Alternativas gratuitas: **OWASP ZAP** (open source, completo) e **Caido** (moderno, tem
camada gratuita; ganhou tração forte em 2025–2026).

**Configurar o certificado do Burp (senão HTTPS não abre):**

1. Suba o Burp → *Proxy* → *Intercept is on/off* → ele escuta em `127.0.0.1:8080`.
2. Configure o navegador para usar `127.0.0.1:8080` como proxy HTTP/HTTPS.
   No Firefox do Kali, a extensão **FoxyProxy** já vem e facilita.
3. Com o proxy ativo, acesse `http://burpsuite` (sim, esse endereço literal) → *CA Certificate*
   → baixe `cacert.der`.
4. Firefox → *Configurações* → *Privacidade e Segurança* → *Certificados* → *Ver certificados*
   → *Autoridades* → *Importar* → marque "Confiar nesta CA para identificar sites".

```bash
# Verificação: com o proxy ligado, isto deve retornar 200 sem erro de TLS
curl -x http://127.0.0.1:8080 -k -s -o /dev/null -w '%{http_code}\n' https://example.com
# esperado: 200
```

> **Por que isso funciona:** o Burp faz um *man-in-the-middle* consigo mesmo — gera um
> certificado na hora para cada site e assina com a CA dele. Se o navegador não confiar nessa
> CA, ele acusa fraude (corretamente!). Você está ensinando o navegador a confiar num
> interceptador — que é exatamente o que você quer *no seu laboratório* e exatamente o que
> um atacante quer na sua máquina. Nunca deixe essa CA instalada no seu navegador de uso
> pessoal.

### 7.2 Ferramentas Python — use `pipx`, não `pip` global

O Debian/Kali marca o Python do sistema como "externally managed" (PEP 668). `pip install`
global vai falhar — e isso é proposital, porque quebrar o Python do sistema quebra o `apt`.

```bash
sudo apt install -y pipx
pipx ensurepath
# reabra o terminal para o PATH valer
```
```bash
# Exemplo: impacket (coleção essencial para AD/SMB/Kerberos)
pipx install impacket
```
```bash
psexec.py -h >/dev/null 2>&1 && echo OK || echo FALHOU
# esperado: OK
```

Para desenvolvimento e exploits que você baixa do GitHub, use ambiente virtual:
```bash
python3 -m venv ~/venvs/lab
source ~/venvs/lab/bin/activate
pip install requests pwntools
```

### 7.3 Ferramentas em Go

Muita ferramenta moderna de reconhecimento (do ProjectDiscovery, principalmente) é em Go.

```bash
sudo apt install -y golang-go
go version
# esperado: go version go1.2x.x linux/amd64
```
```bash
# O binário vai para ~/go/bin — precisa estar no PATH
echo 'export PATH="$PATH:$HOME/go/bin"' >> ~/.zshrc   # Kali usa zsh por padrão
source ~/.zshrc
```
```bash
go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest
```
```bash
httpx -version && subfinder -version && nuclei -version
# esperado: as três versões impressas
```

> **`subfinder` e `nuclei` só devem ser apontados para alvos autorizados.** Eles consultam
> serviços externos e tocam o alvo de verdade. Ver [`12`](12-etica-lei-e-contrato.md).

### 7.4 Listas de palavras (wordlists)

Sem lista boa, metade das ferramentas é inútil.

```bash
# SecLists — o padrão do mercado
sudo apt install -y seclists
ls /usr/share/seclists/
# esperado: Discovery  Fuzzing  IOCs  Miscellaneous  Passwords  Pattern-Matching  Payloads  Usernames  Web-Shells
```
```bash
# rockyou — a lista de senhas clássica, vem compactada no Kali
sudo gzip -d /usr/share/wordlists/rockyou.txt.gz 2>/dev/null
wc -l /usr/share/wordlists/rockyou.txt
# esperado: 14344392
```

---

## 8. Isolamento de rede — obrigatório

**Esta é a seção que separa um laboratório de um incidente.**

### 8.1 Os modos de rede e o que cada um faz

| Modo | VM enxerga a internet | VM enxerga sua rede doméstica | Sua rede enxerga a VM | Uso |
|---|---|---|---|---|
| **NAT** | ✅ | ❌ (só sai) | ❌ | Kali, para baixar ferramenta |
| **Host-only** | ❌ | ❌ | só o hospedeiro | ✅ **Rede do laboratório** |
| **Internal** | ❌ | ❌ | ❌ (nem o hospedeiro) | Isolamento máximo |
| **Bridged** | ✅ | ✅ | ✅ | ❌ **NUNCA para alvo vulnerável** |

**Bridged coloca a VM na sua rede real, com IP do seu roteador.** Um Metasploitable em modo
bridged é uma máquina com vsftpd vulnerável dentro da sua casa. Se você tem UPnP ou porta
encaminhada no roteador, ela vira acessível da internet. Isso já aconteceu com muita gente.

### 8.2 A configuração recomendada

```
Kali:            Adaptador 1 = NAT (internet)  +  Adaptador 2 = Host-only (laboratório)
Alvos:           Adaptador 1 = Host-only  APENAS
```

Assim o Kali baixa ferramenta pela internet e ataca os alvos pela rede isolada, e os alvos
não têm caminho para fora.

**VirtualBox — criar a rede host-only:**

```bash
# Cria a rede (o VirtualBox 7.x usa "hostonlynet" com nome, além do legado vboxnet0)
VBoxManage hostonlyif create
VBoxManage list hostonlyifs
# esperado: uma interface vboxnet0 com IP 192.168.56.1
```
```bash
# Anexa o segundo adaptador do Kali à rede host-only
VBoxManage modifyvm "Kali Linux 2026.2" --nic1 nat --nic2 hostonly --hostonlyadapter2 vboxnet0
```
```bash
# Alvo: SOMENTE host-only
VBoxManage modifyvm "Metasploitable2" --nic1 hostonly --hostonlyadapter1 vboxnet0
```

**VMware:** use `VMnet1` (host-only). Em *Virtual Network Editor*, desmarque
"Connect a host virtual adapter" se quiser isolamento total, e desmarque o DHCP se preferir
IPs fixos.

**KVM/libvirt:** crie uma rede com `forward mode='none'`:

```xml
<!-- salve como lab-isolada.xml -->
<network>
  <name>lab-isolada</name>
  <bridge name='virbr-lab' stp='on' delay='0'/>
  <ip address='192.168.56.1' netmask='255.255.255.0'>
    <dhcp><range start='192.168.56.100' end='192.168.56.200'/></dhcp>
  </ip>
</network>
```
```bash
virsh net-define lab-isolada.xml
virsh net-start lab-isolada
virsh net-autostart lab-isolada
virsh net-list --all
# esperado: lab-isolada  ativo  sim  sim
```

### 8.3 Verificação do isolamento — faça sempre

**A partir do alvo vulnerável** (login `msfadmin` no Metasploitable):

```bash
ping -c 2 8.8.8.8
# ESPERADO: falhar (100% packet loss ou "Network is unreachable")
# Se responder, o alvo tem internet. PARE e corrija o modo de rede.
```
```bash
ping -c 2 192.168.1.1     # troque pelo IP do SEU roteador doméstico
# ESPERADO: falhar.
# Se responder, o alvo enxerga sua casa. PARE e corrija.
```

**A partir do Kali:**
```bash
ip -brief addr
# esperado: duas interfaces com IP — ex.: eth0 10.0.2.15/24 (NAT) e eth1 192.168.56.10/24 (lab)
```
```bash
ping -c 2 192.168.56.20 && echo "alvo alcançável — OK"
```

### 8.4 Firewall do hospedeiro

Mesmo com host-only, feche a porta de casa:

```bash
# Linux — bloqueia tráfego vindo da rede do laboratório para serviços do host
sudo ufw deny in on vboxnet0
sudo ufw status verbose
```

E no roteador doméstico: confirme que não há **DMZ**, **UPnP** nem **port forwarding** ativos.
UPnP ligado é a forma mais comum de um laboratório vazar para a internet sem ninguém pedir.

---

## 9. PATH, variáveis de ambiente e permissões

### 9.1 Por que "o comando não é encontrado" mesmo depois de instalar

O `PATH` é a lista de pastas onde o shell procura executáveis. Se o binário está em
`~/go/bin` e essa pasta não está no `PATH`, o shell não acha — mesmo que o arquivo exista.

```bash
echo "$PATH" | tr ':' '\n'
# esperado: uma lista de pastas, uma por linha
```
```bash
# Onde está o binário, de verdade?
command -v nmap || find / -name nmap -type f 2>/dev/null | head
```

**Em qual arquivo de perfil editar:**

| Shell / SO | Arquivo | Observação |
|---|---|---|
| Kali (zsh, padrão) | `~/.zshrc` | Kali migrou para zsh na versão 2020.4 |
| Bash (Ubuntu, Debian) | `~/.bashrc` | Sessões interativas |
| Bash (login/SSH) | `~/.bash_profile` ou `~/.profile` | Por isso "funciona no terminal e não no SSH" |
| macOS | `~/.zshrc` | zsh é padrão desde o Catalina |
| Windows PowerShell | `$PROFILE` | `notepad $PROFILE`; crie o arquivo se não existir |

```bash
# Adicionar uma pasta ao PATH, de forma permanente (zsh)
echo 'export PATH="$PATH:$HOME/go/bin:$HOME/.local/bin"' >> ~/.zshrc
source ~/.zshrc     # ← a mudança só "pega" depois disto ou de reabrir o terminal
```

**Por que a mudança "não pegou":** cada terminal aberto tem sua própria cópia das variáveis
de ambiente, carregada quando ele iniciou. Editar o arquivo não afeta terminais já abertos.
`source` recarrega no terminal atual; reabrir o terminal resolve para os novos.

### 9.2 Permissões e `sudo` — onde `sudo` estraga

| Situação | Errado | Certo | Por quê |
|---|---|---|---|
| Ferramenta Python | `sudo pip install X` | `pipx install X` | `sudo pip` sobrescreve pacotes que o `apt` gerencia; o `apt` depois briga com arquivos que não conhece e você quebra o `python3` do sistema — que no Debian é usado por ferramentas administrativas. Recuperar é doloroso. |
| Ferramenta Node | `sudo npm -g install X` | `npm config set prefix ~/.npm-global` + PATH | Mesma lógica; além disso, `npm` roda *scripts* de instalação — como root, um pacote malicioso vira root imediato. |
| Clonar repositório | `sudo git clone` | `git clone` | Os arquivos ficam do root e você não consegue editar depois. |
| Rodar o Kali | logar como root | usuário `kali` + `sudo` | Desde 2020.1 o Kali usa usuário normal por padrão, justamente para reduzir o estrago de erro de digitação. |
| `nmap -sS` (SYN scan) | — | `sudo nmap -sS` | Este *precisa* de root: criar pacote TCP cru exige `CAP_NET_RAW`. Sem privilégio, o nmap silenciosamente cai para `-sT`, que é mais lento e mais visível. |
| Captura de pacote | `sudo wireshark` | grupo `wireshark` + `dumpcap` | Rodar GUI grande como root é superfície de ataque desnecessária: `sudo dpkg-reconfigure wireshark-common` e `sudo usermod -aG wireshark $USER`. |

---

## 10. Rede corporativa

Se você está atrás de proxy, firewall ou inspeção TLS da empresa:

```bash
# Proxy para o apt
sudo tee /etc/apt/apt.conf.d/95proxy >/dev/null <<'EOF'
Acquire::http::Proxy "http://usuario:senha@proxy.empresa.local:8080";
Acquire::https::Proxy "http://usuario:senha@proxy.empresa.local:8080";
EOF
```
```bash
# Proxy para o shell (coloque no ~/.zshrc)
export http_proxy="http://proxy.empresa.local:8080"
export https_proxy="$http_proxy"
export no_proxy="localhost,127.0.0.1,192.168.56.0/24"
```
```bash
# Certificado raiz interno (quando a empresa faz inspeção TLS)
sudo cp certificado-empresa.crt /usr/local/share/ca-certificates/
sudo update-ca-certificates
# esperado: "1 added, 0 removed; done."
```
```bash
# Python e Go têm armazéns próprios de certificado
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
export SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt
```

> **Aviso sério:** **não** faça laboratório ofensivo na rede da sua empresa sem autorização
> escrita da segurança dela. Rodar `nmap` na rede corporativa dispara alertas do SOC, e a
> conversa que vem depois pode terminar em desligamento por justa causa — mesmo que sua
> intenção fosse estudar. Use rede doméstica ou peça autorização formal, por e-mail, com
> escopo e janela definidos.

---

## 11. Snapshots, atualização e como voltar atrás

### 11.1 Snapshots — sua rede de segurança

```bash
# Criar (VirtualBox, VM desligada)
VBoxManage snapshot "Kali Linux 2026.2" take "antes-do-lab-AD"
```
```bash
# Listar
VBoxManage snapshot "Kali Linux 2026.2" list
```
```bash
# Restaurar
VBoxManage snapshot "Kali Linux 2026.2" restore "base-limpa"
```

**Quando tirar snapshot:** depois da instalação limpa e atualizada; antes de cada laboratório
novo; antes de instalar algo grande; antes de qualquer coisa com "vou tentar uma parada aqui".

**Custo:** cada snapshot ocupa a diferença desde o anterior. 5 snapshots de Kali podem somar
20 GB. Apague os antigos: `VBoxManage snapshot <vm> delete <nome>`.

### 11.2 Atualizar o Kali com segurança

```bash
sudo apt update && sudo apt full-upgrade -y
```
Use `full-upgrade`, não `upgrade`: o Kali é rolling e frequentemente precisa remover pacotes
para avançar; `upgrade` trava nesse ponto e deixa o sistema pela metade.

```bash
sudo apt autoremove --purge -y && sudo apt clean   # libera disco
```

**Se a atualização quebrar:** restaure o snapshot. É por isso que ele existe. Reinstalar Kali
por causa de atualização quebrada é a segunda causa mais comum de sábado perdido.

### 11.3 Voltar uma versão de ferramenta

```bash
apt list -a nmap                      # versões disponíveis
sudo apt install nmap=7.95+dfsg1-1    # instala versão específica
sudo apt-mark hold nmap               # impede que atualize de novo
sudo apt-mark unhold nmap             # libera
```

---

## 12. Desinstalação completa

### VirtualBox
```bash
# Linux
sudo apt purge -y 'virtualbox*' && sudo apt autoremove -y
rm -rf ~/VirtualBox\ VMs ~/.config/VirtualBox ~/.VirtualBox
```
```powershell
# Windows: Painel de Controle → Programas → Oracle VirtualBox → Desinstalar
Remove-Item -Recurse -Force "$env:USERPROFILE\VirtualBox VMs"
Remove-Item -Recurse -Force "$env:USERPROFILE\.VirtualBox"
```
**Fica para trás se você não apagar:** os discos das VMs (dezenas de GB), os adaptadores de
rede virtuais (removidos com o desinstalador) e as chaves de registro em
`HKCU\Software\Oracle`.

### Kali (VM)
Apague a VM pelo hipervisor **marcando "excluir todos os arquivos"**. Só remover da lista
deixa 25 GB no disco.

### Docker no Kali
```bash
docker system prune -a --volumes     # remove imagens, contêineres e volumes
sudo apt purge -y docker.io docker-compose-v2
sudo rm -rf /var/lib/docker /var/lib/containerd /etc/docker
sudo gpasswd -d "$USER" docker
```

### Ferramentas Python/Go
```bash
pipx uninstall-all
rm -rf ~/.local/pipx ~/go ~/venvs
```

### Certificado do Burp
Firefox → *Certificados* → *Autoridades* → busque "PortSwigger CA" → *Excluir*.
**Não esqueça deste.** Deixar a CA do Burp instalada num navegador de uso pessoal é um risco
real: qualquer coisa que use aquela chave privada (que é fixa por instalação) pode
interceptar seu tráfego HTTPS.

---

## 13. Solução de problemas

| Mensagem literal | Causa provável | Correção |
|---|---|---|
| `VT-x is not available (VERR_VMX_NO_VMX)` | Virtualização desligada na BIOS **ou** Hyper-V/WSL2 tomou o hipervisor | Habilite VT-x/AMD-V na UEFI; no Windows, `bcdedit /set hypervisorlaunchtype off` + reiniciar |
| `Kernel driver not installed (rc=-1908)` | Módulos do VirtualBox não carregados; comum com Secure Boot | `sudo /sbin/vboxconfig`; se persistir, desative Secure Boot ou assine os módulos com MOK |
| `Raw-mode is unavailable courtesy of Hyper-V` | Hyper-V ativo em paralelo | Mesma correção do primeiro caso |
| `E: Unable to locate package X` | `apt update` não rodou, ou repositório do Kali faltando | `sudo apt update`; confira `/etc/apt/sources.list` — deve conter `deb http://http.kali.org/kali kali-rolling main contrib non-free non-free-firmware` |
| `The following signatures were invalid: EXPKEYSIG ED444FF07D8D0BF6 Kali Linux Repository` | Chave de assinatura do Kali expirou (acontece a cada ciclo) | `sudo wget -q -O - https://archive.kali.org/archive-key.asc \| sudo gpg --dearmor -o /usr/share/keyrings/kali-archive-keyring.gpg` e `sudo apt update` |
| `error: externally-managed-environment` | PEP 668 — `pip` global bloqueado no Debian/Kali | Use `pipx install` ou um `venv`. **Não** use `--break-system-packages` a menos que saiba o que está quebrando |
| `permission denied while trying to connect to the Docker daemon socket` | Usuário fora do grupo `docker` | `sudo usermod -aG docker $USER` e **logout/login** (ou `newgrp docker`) |
| `command not found: httpx` (após `go install`) | `~/go/bin` fora do PATH | `echo 'export PATH="$PATH:$HOME/go/bin"' >> ~/.zshrc && source ~/.zshrc` |
| `EACCES: permission denied` (npm/pip) | Instalação global sem privilégio | Configure prefixo no `$HOME` em vez de usar `sudo` (§9.2) |
| Navegador: `SEC_ERROR_UNKNOWN_ISSUER` com o Burp ligado | CA do Burp não importada | §7.1, passos 3–4 |
| `You requested a scan type which requires root privileges` (nmap) | `-sS`, `-O`, `-sU` precisam de socket cru | `sudo nmap ...` |
| Metasploitable sem IP / `no route to host` | Adaptador em modo errado, ou DHCP da host-only desligado | Confira o modo de rede (§8) e ligue o DHCP da rede host-only, ou fixe IP em `/etc/network/interfaces` |
| VM extremamente lenta no macOS ARM | Emulação x86 via QEMU | Use imagem ARM64 ou mude para laboratório em nuvem (§3.4) |
| `msf6 > ` mas `db_status` diz `no database` | Banco do Metasploit não inicializado | `sudo msfdb init` |
| Kali sem áudio/tela cheia/copiar-colar | Guest Additions ausente | `sudo apt install -y virtualbox-guest-x11` ou `open-vm-tools-desktop` + reboot |

---

## 14. Checklist "ambiente pronto"

Rode um por linha. Todos devem passar antes de você ir para
[`04-como-comecar.md`](04-como-comecar.md).

```bash
# 1. Virtualização habilitada no hospedeiro
grep -Ec '(vmx|svm)' /proc/cpuinfo        # > 0
```
```bash
# 2. Kali atualizado
grep VERSION= /etc/os-release              # 2026.2 ou superior
```
```bash
# 3. Ferramentas essenciais presentes
for t in nmap ffuf sqlmap hydra john hashcat netexec msfconsole burpsuite; do
  printf '%-12s ' "$t"; command -v "$t" >/dev/null && echo OK || echo FALTANDO; done
```
```bash
# 4. Metasploit com banco
msfconsole -q -x "db_status; exit"         # Connected to msf
```
```bash
# 5. Duas interfaces de rede no Kali (NAT + host-only)
ip -brief addr | grep -c 'UP'              # >= 2
```
```bash
# 6. Alvo alcançável na rede isolada
ping -c 2 192.168.56.20                    # responde
```
```bash
# 7. Alvo SEM internet (rode DENTRO do alvo)
ping -c 2 8.8.8.8                          # DEVE FALHAR
```
```bash
# 8. Docker funcionando
docker run --rm hello-world | head -2      # Hello from Docker!
```
```bash
# 9. Burp interceptando HTTPS
curl -x http://127.0.0.1:8080 -k -s -o /dev/null -w '%{http_code}\n' https://example.com  # 200
```
```bash
# 10. Wordlists no lugar
wc -l /usr/share/wordlists/rockyou.txt     # 14344392
ls /usr/share/seclists/Discovery/Web-Content/ | head -3
```
```bash
# 11. Snapshot da base limpa existe
VBoxManage snapshot "Kali Linux 2026.2" list   # deve listar "base-limpa"
```

Passou nos 11? Ambiente pronto. → [`04-como-comecar.md`](04-como-comecar.md)

---

## Autoteste

1. Por que o alvo vulnerável **nunca** pode estar em modo *bridged*?
2. Qual é a diferença prática entre os modos *host-only* e *internal* do VirtualBox?
3. Por que `sudo pip install` é perigoso no Kali, e o que se usa no lugar?
4. Você instalou uma ferramenta com `go install` e o shell diz `command not found`.
   Qual é a causa e a correção, exatamente?
5. Por que o navegador acusa erro de certificado quando o Burp está ligado — e por que esse
   comportamento do navegador está *correto*?
6. Qual comando prova que a virtualização está habilitada no hospedeiro Linux?
7. Cite dois momentos em que você deve obrigatoriamente tirar um snapshot.
8. Por que `apt full-upgrade` e não `apt upgrade` no Kali?
9. Você tem um MacBook M3. Qual é o caminho recomendado e por quê?
10. Qual é a alternativa para começar hoje, sem instalar nada, e quando ela deixa de bastar?

---

### Fontes consultadas (12/08/2026)

- [Kali Linux 2026.2 Release — kali.org/blog](https://www.kali.org/blog/kali-linux-2026-2-release/)
- [Kali Linux Release History](https://www.kali.org/releases/)
- [Oracle VirtualBox — downloads](https://www.virtualbox.org/)
- [VMware Workstation Pro gratuito para uso pessoal e comercial (Broadcom)](https://blogs.vmware.com/workstation/2024/05/vmware-workstation-pro-now-available-free-for-personal-use.html)
- [Burp Suite Community Download — PortSwigger](https://portswigger.net/burp/communitydownload)
- [Metasploitable 2 — SourceForge](https://sourceforge.net/projects/metasploitable/files/Metasploitable2/)
- [GOAD — Game of Active Directory](https://github.com/Orange-Cyberdefense/GOAD)
- [OWASP Juice Shop](https://owasp.org/www-project-juice-shop/)
