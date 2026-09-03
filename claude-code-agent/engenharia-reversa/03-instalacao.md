# 03 · Manual de Instalação — o arsenal completo

**Nível:** iniciante · **Pesquisado na web e testado em:** 03/09/2026
**Ambiente de referência:** Ubuntu 22.04.5 LTS · x86-64 · GCC 11.4 · GDB 12.1 · Python 3.10.12 · binutils 2.38 · OpenJDK 17/21

> Este é um **manual de campo**. Siga na ordem, verifique cada passo, e não pule a seção do
> seu sistema operacional. Um manual de instalação desatualizado é pior que nenhum, porque
> falha no meio — por isso **cada passo tem verificação e o que fazer se a saída for
> diferente**. As versões abaixo foram conferidas na web em 03/09/2026; nomes de pacote e
> números mudam, então confie na *verificação*, não no número exato.

---

## 0. Antes de tudo: comece hoje, sem instalar nada

Se você quer só *começar*, use estes ambientes no navegador — zero instalação, zero risco.
Instale o resto depois.

| Ferramenta online | O que faz | Link |
|---|---|---|
| **Compiler Explorer (godbolt.org)** | Vê, ao vivo, o assembly que seu C vira. Insubstituível para aprender. | https://godbolt.org |
| **Dogbolt (dogbolt.org)** | Roda vários **descompiladores** (Ghidra, angr, RetDec…) sobre um binário que você envia, e compara a saída. | https://dogbolt.org |
| **Decompiler Explorer** | Mesmo espírito, comparação de descompiladores. | https://dogbolt.org |
| **onlinedisassembler / ODA** | Desmontagem de bytes hex direto no navegador. | https://onlinedisassembler.com |
| **DECOMP / picoCTF webshell** | Ambiente Linux pronto no navegador para praticar. | https://picoctf.org |
| **GitHub Codespaces** | Um Ubuntu completo no navegador; instale o que quiser lá. | https://github.com/codespaces |

**Recomendação:** faça o [`04-como-comecar.md`](04-como-comecar.md) usando **Compiler
Explorer + Dogbolt** hoje, e monte a máquina local em paralelo seguindo o resto deste arquivo.
Isso evita a desistência do "não consegui instalar no primeiro dia".

---

## 1. Visão geral do arsenal

Você vai instalar por camadas. Nem tudo é necessário no dia 1.

| Camada | Ferramentas | Necessário quando |
|---|---|---|
| **Base (essencial)** | compilador (GCC/Clang), **binutils** (objdump, readelf, nm, strings), **file**, **GDB** | Desde o [`04`](04-como-comecar.md) |
| **Descompilador** | **Ghidra** (grátis, poderoso) ou **IDA Free** | Desde o [`04`](04-como-comecar.md) |
| **CLI de RE** | **radare2** / **rizin** + **Cutter** (GUI) | A partir do [`05`](05-manual-de-uso.md) |
| **Depuração turbinada** | **pwndbg** ou **GEF** (plugins do GDB) | A partir do [`15`](15-analise-dinamica.md) |
| **Python de RE** | Capstone, pwntools, angr, LIEF, pyelftools, Frida | Automação e labs avançados |
| **Dinâmica/instrumentação** | **Frida**, **ltrace**, **strace** | A partir do [`15`](15-analise-dinamica.md) |
| **Windows-alvo** | **x64dbg**, **dnSpy**, **PE-bear** | Ao reverter binários Windows/.NET |
| **Mobile/managed** | **jadx**, **apktool**, **ILSpy** | Android/Java/.NET ([`23`](23-mobile-e-managed.md)) |
| **Firmware** | **binwalk**, **QEMU** | Firmware/embarcados ([`22`](22-firmware-e-embarcados.md)) |

**Atalho radical:** se não quiser montar nada, baixe **REMnux** (Linux pronto para análise
de malware, https://remnux.org) ou **Kali Linux** — vêm com quase tudo. Ver seção 12.

---

## 2. Base essencial (compilador, binutils, GDB, file)

Esta é a camada sem a qual nada funciona. É pequena e rápida.

### 2.1 Linux — família Debian/Ubuntu

```bash
sudo apt update
```
Atualiza a lista de pacotes disponíveis.

```bash
sudo apt install -y build-essential gdb binutils file xxd
```
Instala GCC/G++/make (`build-essential`), o depurador (`gdb`), objdump/readelf/nm/strings
(`binutils`), o identificador de arquivos (`file`) e o visualizador hex (`xxd`).

**Verificação:**
```bash
gcc --version    # esperado: gcc (Ubuntu 11.x ...) 11.x ou superior
gdb --version    # esperado: GNU gdb (Ubuntu 12.x ...) 12.x ou superior
objdump --version
file --version   # esperado: file-5.41 ou superior
```
**Se `command not found`:** o pacote não instalou. Refaça o `apt install` e leia o erro do
`apt` — quase sempre é falta de internet ou espelho fora do ar.

### 2.2 Linux — família Fedora/RHEL

```bash
sudo dnf install -y gcc gcc-c++ make gdb binutils file vim-common
```
`vim-common` traz o `xxd`. Verificação idêntica à seção 2.1.

### 2.3 macOS (Intel e Apple Silicon)

O compilador vem com as **Command Line Tools** da Apple (que fornecem `clang`, não `gcc`):
```bash
xcode-select --install
```
Abre um instalador gráfico; aceite. Instala `clang`, `make`, e o **`otool`/`nm`** da Apple.

Para as ferramentas GNU (objdump/readelf de verdade) e o GDB, use o **Homebrew**:
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```
Instala o gerenciador de pacotes Homebrew.

```bash
brew install binutils gdb
```
> **Apple Silicon (M1/M2/M3/M4):** o Homebrew instala em `/opt/homebrew` (Intel usa
> `/usr/local`). Os binutils GNU ficam com prefixo `g` (`gobjdump`, `greadelf`) para não
> colidir com os da Apple. **GDB tem suporte instável em Apple Silicon** — no Mac ARM,
> prefira o **LLDB** (já vem com o Xcode) para depuração. Em Mac ARM você estará revertendo
> binários ARM64 (Mach-O), o que é ótimo, mas alguns binários x86-64 exigem Rosetta 2:
> `softwareupdate --install-rosetta`.

**Verificação (Apple Silicon):**
```bash
clang --version
gobjdump --version   # binutils via brew
lldb --version
```

### 2.4 Windows

**Caminho recomendado: WSL2.** Reverter binários Linux no Windows sem WSL é sofrimento;
com WSL2 você tem um Ubuntu de verdade.

```powershell
wsl --install -d Ubuntu
```
Executado no **PowerShell como Administrador**. Instala o WSL2 e uma imagem Ubuntu. Reinicie
se pedir. Depois, **dentro do Ubuntu do WSL**, siga a seção 2.1.

**Verificação:**
```powershell
wsl --status    # esperado: "Versão padrão: 2"
wsl -l -v       # lista distros; STATE deve ser Running/Stopped, VERSION 2
```
**Se `wsl` não é reconhecido:** atualize o Windows (WSL exige Windows 10 2004+ ou Windows
11) e rode `wsl --update`.

**Para reverter binários *Windows* (.exe PE):** você quer ferramentas nativas do Windows —
**x64dbg** e **Ghidra** rodam em Windows nativo (seções 4 e 8). Muitos profissionais usam
**os dois**: Ghidra/x64dbg no Windows nativo para alvos PE, e WSL para alvos ELF.

---

## 3. PATH e variáveis de ambiente — leia antes de reclamar que "não pegou"

Metade dos "não funciona" é PATH. **PATH** é a lista de pastas onde o shell procura
comandos. Se você baixou uma ferramenta para uma pasta fora do PATH, o shell não a acha.

**Ver o PATH atual:**
```bash
echo $PATH
```
Mostra pastas separadas por `:`.

**Adicionar uma pasta ao PATH** (ex.: onde você extraiu o Ghidra ou o radare2):
```bash
echo 'export PATH="$HOME/ferramentas/ghidra:$PATH"' >> ~/.bashrc
source ~/.bashrc
```
- A **primeira linha** grava a mudança no arquivo de perfil do shell.
- Qual arquivo? **`~/.bashrc`** (bash, padrão no Ubuntu), **`~/.zshrc`** (zsh, padrão no
  macOS moderno), ou o **`$PROFILE`** no PowerShell.
- **Por que a mudança "não pega"?** Porque o arquivo de perfil só é lido quando um novo
  shell abre. Ou rode `source ~/.bashrc`, ou feche e reabra o terminal. **Este é o erro nº 1
  de iniciante.**

**No PowerShell (Windows nativo):**
```powershell
$env:Path += ";C:\ferramentas\ghidra"     # só nesta sessão
# permanente:
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";C:\ferramentas\ghidra", "User")
```

---

## 4. Permissões — o caminho certo, e por que `sudo` errado dá dor de cabeça

**Regra:** instale ferramentas de sistema com o gerenciador de pacotes (`apt`/`dnf`/`brew`),
que já cuida das permissões. **Nunca** rode `pip install` global com `sudo`, nem `npm -g`
com `sudo`.

- **Por que `sudo pip install` é problema (não só "não deve"):** ele mistura pacotes
  instalados por você com os que o sistema operacional gerencia via `apt`. Numa atualização
  do SO, o gerenciador e o pip disputam os mesmos arquivos e **quebram o Python do sistema** —
  um estado difícil de reverter. A correção certa é isolar em ambiente virtual:
```bash
python3 -m venv ~/re-venv          # cria um Python isolado
source ~/re-venv/bin/activate      # ativa (o prompt ganha "(re-venv)")
pip install capstone pwntools      # instala só aqui, sem sudo, sem risco
```
Ou use **pipx** para ferramentas de linha de comando: `pipx install <ferramenta>`.

- **Binários que você baixou** (Ghidra, radare2 compilado, x64dbg): não precisam de `sudo`
  para rodar. Se um script pedir permissão de execução: `chmod +x arquivo` — nunca `sudo`
  para *executar* algo do seu próprio diretório home.

---

## 5. Python de RE (Capstone, pwntools, angr, LIEF, pyelftools, ropper)

O ecossistema de automação é Python. **Sempre em ambiente virtual** (seção 4). Este curso
usa o **`uv`** (gerenciador de pacotes Python rápido — há [`uv-python`](../uv-python/) nesta
pasta) ou o `venv`+`pip` clássico.

### Com uv (recomendado, mais rápido)
```bash
uv venv ~/re-venv && source ~/re-venv/bin/activate
uv pip install capstone==5.0.9 pwntools==4.15.0 angr==9.3.4 lief==1.0.0 pyelftools==0.33 ropper==1.13.13 frida-tools==14.10.4 flare-capa==9.4.0
```
Cada pacote: **Capstone** (motor de desmontagem), **pwntools** (canivete de exploração/CTF),
**angr** (execução simbólica), **LIEF** (ler/modificar ELF/PE/Mach-O), **pyelftools** (parse
de ELF em Python puro), **ropper** (achar gadgets ROP), **frida-tools** (CLI do Frida),
**flare-capa** (identifica capacidades de um binário).

### Com venv+pip clássico
```bash
python3 -m venv ~/re-venv && source ~/re-venv/bin/activate
pip install --upgrade pip
pip install capstone pwntools angr lief pyelftools ropper frida-tools flare-capa
```
> **angr é grande** (traz Z3, o solucionador SMT) e pode levar minutos e ~500 MB. Se falhar
> a compilação, instale as ferramentas de build primeiro: `sudo apt install python3-dev
> build-essential`.

**Verificação:**
```bash
python3 -c "import capstone; print('capstone', capstone.__version__)"
# esperado: capstone 5.0.9 (ou superior)
python3 -c "import angr; print('angr', angr.__version__)"
# esperado: angr 9.3.x
frida --version   # esperado: 17.17.0 (ou superior)
```
**Versões testadas em 03/09/2026 (PyPI):** capstone 5.0.9, pwntools 4.15.0, angr 9.3.4,
LIEF 1.0.0, pyelftools 0.33, ropper 1.13.13, frida 17.17.0, flare-capa 9.4.0.

---

## 6. GDB turbinado — pwndbg ou GEF

O GDB puro é espartano. Um plugin transforma a experiência. **Escolha um** (não instale os
dois no mesmo perfil — eles brigam).

### pwndbg (recomendado para RE/exploração)
```bash
git clone https://github.com/pwndbg/pwndbg ~/pwndbg
cd ~/pwndbg && ./setup.sh
```
Clona e configura; ele mesmo escreve a linha no seu `~/.gdbinit`.

### GEF (alternativa, um único arquivo)
```bash
bash -c "$(curl -fsSL https://gef.blah.cat/sh)"
```

**Verificação:** abra `gdb` e observe o prompt colorido `pwndbg>` ou `gef➤`. Rode
`gdb /bin/ls`, depois `start` — você deve ver registradores, pilha e desmontagem
automaticamente.
**Se abrir o GDB comum:** o `~/.gdbinit` não foi lido; confira se o arquivo existe e tem a
linha `source .../gdbinit.py`.

---

## 7. radare2 / rizin + Cutter

**radare2** é o framework de RE em linha de comando mais usado no mundo livre. **rizin** é
um fork focado em estabilidade e API limpa; **Cutter** é a GUI do rizin. Escolha a família —
os comandos são quase idênticos. O curso mostra os dois.

### radare2 — instalar do git (recomendado; o do apt costuma ser antigo)
```bash
git clone https://github.com/radareorg/radare2 ~/radare2
~/radare2/sys/install.sh
```
Compila e instala. **Nunca instale o radare2 com `sudo pip`** — ele tem instalador próprio.

**Verificação:**
```bash
r2 -version   # esperado: radare2 6.2.0 (ou superior), testado em 03/09/2026
```

### rizin (via pacote)
```bash
# Ubuntu/Debian: baixe o .deb da release e instale
# https://github.com/rizinorg/rizin/releases  (v0.9.1, 29/06/2026)
sudo dpkg -i rizin_0.9.1_amd64.deb
rizin -version   # esperado: rizin 0.9.1
```

### Cutter (GUI) — AppImage, roda em qualquer distro
```bash
# baixe de https://github.com/rizinorg/cutter/releases (v2.5.0, 30/06/2026)
chmod +x Cutter-v2.5.0-Linux-x86_64.AppImage
./Cutter-v2.5.0-Linux-x86_64.AppImage
```
No macOS/Windows há `.dmg` e `.zip` nas releases. **Verificação:** a janela do Cutter abre e
você consegue carregar um binário.

---

## 8. Ghidra — o descompilador gratuito da NSA (o mais importante)

**Ghidra** é grátis, open-source (Apache 2.0) e tem um descompilador excelente. É a peça
central do curso. Escrito em Java — **exige JDK 21+**.

### 8.1 Instalar o Java (JDK 21) — pré-requisito do Ghidra

**Ubuntu/Debian:**
```bash
sudo apt install -y openjdk-21-jdk
```
**Fedora:**
```bash
sudo dnf install -y java-21-openjdk-devel
```
**macOS:**
```bash
brew install openjdk@21
```
**Windows:** baixe o instalador do **Adoptium Temurin 21** (https://adoptium.net) e instale.

**Verificação (todos os SOs):**
```bash
java -version
# esperado: openjdk version "21.x.x" — DEVE ser 21 ou superior
```
**Se aparecer 17 ou menos:** o Ghidra 12.x **não roda**. No Ubuntu, escolha a versão:
`sudo update-alternatives --config java` e selecione a 21. (O ambiente de referência deste
curso tinha Java 17 instalado; foi preciso adicionar o 21.)

### 8.2 Baixar e extrair o Ghidra

```bash
cd ~/ferramentas
wget https://github.com/NationalSecurityAgency/ghidra/releases/download/Ghidra_12.1.3_build/ghidra_12.1.3_PUBLIC_20260817.zip
```
Baixa a release **12.1.3** (18/08/2026, ~543 MB). **Sempre confira o número atual** em
https://github.com/NationalSecurityAgency/ghidra/releases — o link acima envelhece.

**Verifique a integridade** (o SHA-256 é publicado na página da release):
```bash
sha256sum ghidra_12.1.3_PUBLIC_20260817.zip
# compare com o valor publicado na release do GitHub
```
**Por que conferir?** Você está baixando uma ferramenta que vai analisar código
possivelmente malicioso; um download corrompido ou adulterado é o pior começo.

```bash
unzip ghidra_12.1.3_PUBLIC_20260817.zip
```
Extrai para `ghidra_12.1.3_PUBLIC/`. Ghidra **não instala** — roda da pasta extraída.

### 8.3 Rodar
```bash
cd ghidra_12.1.3_PUBLIC
./ghidraRun        # Linux/macOS
# Windows: ghidraRun.bat
```
Na primeira execução, aceite os termos. A janela do **Ghidra Project Manager** abre.

**Verificação:** `File → New Project`, depois `File → Import File`, escolha `/bin/ls`,
aceite a análise automática. Se a janela do **CodeBrowser** abrir mostrando funções
descompiladas, **está funcionando**. Isso é feito passo a passo no [`04`](04-como-comecar.md).

**PATH (opcional):** para chamar `ghidraRun` de qualquer lugar, adicione a pasta ao PATH
(seção 3). Para o modo **headless** (automação sem GUI), o script é
`support/analyzeHeadless` — usado no [`05`](05-manual-de-uso.md).

> **Python no Ghidra:** o Ghidra moderno usa **PyGhidra** (Python 3 de verdade) em vez do
> antigo Jython. Para scripting Python 3, instale `pip install pyghidra` no seu venv e o
> Ghidra o detecta. O Jython virou uma extensão opcional (`File → Install Extensions`).

---

## 9. IDA Free — a alternativa comercial, versão gratuita

**IDA** é o padrão histórico da indústria (caro — ver [`80`](80-custos-e-licencas.md)). A
**IDA Free** é gratuita, com decompilador x86/x64 na nuvem, boa para aprender o fluxo IDA.

- Baixe em https://hex-rays.com/ida-free (Windows, Linux, macOS).
- **Windows:** rode o instalador `.exe`. **Linux:** rode o `.run` (`chmod +x` antes).
  **macOS:** monte o `.dmg`.
- Exige aceitar a licença (não é cadastro pago). **Verificação:** abra a IDA Free, carregue
  um binário, pressione `F5` sobre uma função para ver o pseudocódigo do decompilador.

**Recomendação:** aprenda com **Ghidra** (grátis e completo). Conheça a IDA Free para não
ficar perdido quando encontrar tutoriais/empregos que a usam. Não gaste com IDA Pro para
aprender.

---

## 10. Ferramentas por alvo específico

Instale só quando chegar no assunto correspondente.

### 10.1 Instrumentação dinâmica — Frida, ltrace, strace
```bash
# strace já pode estar; ltrace e frida:
sudo apt install -y ltrace strace        # Debian/Ubuntu
pip install frida-tools                   # dentro do venv (seção 5)
```
`strace` mostra chamadas de sistema; `ltrace` mostra chamadas de biblioteca; **Frida**
injeta JavaScript em processos vivos (Linux, Windows, macOS, Android, iOS).
**Verificação:** `frida --version` → 17.17.0; `strace /bin/true` mostra as syscalls.

### 10.2 Windows-alvo — x64dbg, dnSpy, PE-bear (rodam no Windows)
- **x64dbg** (grátis, open-source): depurador de PE. Baixe o snapshot em
  https://github.com/x64dbg/x64dbg/releases (2026.05.27). Extraia e rode `x96dbg.exe`.
- **dnSpy / dnSpyEx** (grátis): descompila **.NET** e permite editar/depurar. Baixe de
  https://github.com/dnSpyEx/dnSpy/releases (v6.6.0, 20/06/2026).
- **PE-bear** / **CFF Explorer**: inspecionar cabeçalhos PE.

### 10.3 Android/Java/.NET managed
```bash
# jadx: descompilador Android APK -> Java
# baixe de https://github.com/skylot/jadx/releases (v1.5.6) ou:
sudo apt install -y jadx        # se disponível na sua distro
# apktool (desmonta/remonta APK):
sudo apt install -y apktool
```
- **jadx-gui** para a interface. **apktool** para recursos e smali.
- **ILSpy** (multiplataforma, .NET): https://github.com/icsharpcode/ILSpy/releases (v11.0).
- Precisa do **JDK** (seção 8.1) — já instalado.

### 10.4 Firmware/embarcados — binwalk, QEMU
```bash
sudo apt install -y qemu-user qemu-system binwalk
```
**binwalk** (v3.1.0) extrai sistemas de arquivos de imagens de firmware; **QEMU** emula
arquiteturas (ARM, MIPS) para rodar binários que não são da sua CPU.
**Verificação:** `binwalk --help`; `qemu-arm --version`.

### 10.5 Utilitários que valem ouro
```bash
pip install ropper                        # gadgets ROP (já na seção 5)
sudo apt install -y patchelf              # editar o interpretador/rpath de um ELF
# checksec (mostra proteções de um binário):
pip install pwntools                      # traz o comando 'checksec'
# upx (packer comum; útil para (des)empacotar):
sudo apt install -y upx-ucl               # ou baixe upx 5.2.1 do GitHub
```

---

## 11. Reprodutibilidade — congele o ambiente

Para não sofrer com "funcionava na outra máquina":

- **Python:** grave as versões exatas. `pip freeze > requirements.txt` (ou `uv pip freeze`).
  Recrie com `pip install -r requirements.txt`.
- **Versão do Python/ferramentas:** um arquivo `.tool-versions` (mise/asdf) ou `.python-version`.
- **Container:** a forma mais reprodutível. Um `Dockerfile` (ou use REMnux/Kali em imagem)
  garante o mesmo ambiente em qualquer lugar. Ver [`docker`](../docker/) e
  [`curso-docker`](../curso-docker/) nesta pasta.

Exemplo de container mínimo de RE:
```dockerfile
FROM ubuntu:22.04
RUN apt-get update && apt-get install -y \
    build-essential gdb binutils file xxd python3-pip radare2 ltrace strace \
    && rm -rf /var/lib/apt/lists/*
RUN pip3 install capstone pwntools pyelftools ropper
WORKDIR /work
```
```bash
docker build -t re-lab . && docker run -it --rm -v "$PWD":/work re-lab bash
```

---

## 12. Distros prontas — o atalho profissional

Em vez de instalar peça por peça, use uma distribuição que já traz tudo:

| Distro | Foco | Onde |
|---|---|---|
| **REMnux** | Análise de **malware** e RE. Traz Ghidra, radare2, YARA, capa, floss, etc. | https://remnux.org |
| **Kali Linux** | Pentest + RE. Traz muitas ferramentas, mas menos focada em RE que REMnux. | https://kali.org |
| **FLARE VM** | Windows para RE/malware (script que instala tudo num Windows). | https://github.com/mandiant/flare-vm |

Rode qualquer uma **numa VM** (VirtualBox/VMware/UTM). Para malware, isole a rede.

---

## 13. Atualizar e voltar atrás

- **Pacotes do sistema:** `sudo apt update && sudo apt upgrade`. Para desfazer um pacote:
  `sudo apt install pacote=versão-antiga`.
- **Python (venv):** `pip install -U ferramenta`. Para voltar: `pip install ferramenta==versão`.
  Como está tudo no venv, no pior caso você **apaga o venv e recria** — sem tocar no sistema.
- **Ghidra/radare2 baixados:** atualizar = baixar a nova versão em outra pasta e apontar o
  PATH para ela. Voltar = apontar o PATH de volta. Guarde a versão antiga até confirmar.
- **Projetos do Ghidra são compatíveis para frente, não para trás**: um projeto salvo no
  12.1 **não abre** num Ghidra mais antigo. Não atualize no meio de um trabalho crítico sem
  backup do projeto.

---

## 14. Desinstalar por completo

- **apt/dnf:** `sudo apt remove --purge pacote && sudo apt autoremove`. O `--purge` remove
  também os arquivos de configuração.
- **venv Python:** `deactivate` e `rm -rf ~/re-venv`. Some tudo, inclusive caches em
  `~/.cache/pip`.
- **Ghidra/radare2/Cutter baixados:** `rm -rf` a pasta. **Restos escondidos:** Ghidra guarda
  configurações e projetos em `~/.config/ghidra` e onde você salvou o `.gpr`; radare2 em
  `~/.config/radare2` e `~/.local/share/radare2`. Apague-os para limpeza total.
- **pwndbg/GEF:** apague a pasta clonada e **remova a linha `source ...`** do `~/.gdbinit`.
- **Homebrew (macOS):** `brew uninstall pacote`.

---

## 15. Solução de problemas — erros literais

| Mensagem (literal) | Causa provável | Correção |
|---|---|---|
| `bash: r2: command not found` | Binário não está no PATH | Adicione a pasta ao PATH (seção 3) e `source ~/.bashrc` |
| `Error: Java runtime ... version 21 or greater` (Ghidra) | JDK antigo (17 ou menos) | Instale JDK 21 e selecione-o com `update-alternatives --config java` |
| `EACCES: permission denied` / `Permission denied` ao rodar | Falta bit de execução, ou tentou `sudo` onde não devia | `chmod +x arquivo`; **não** use `sudo` para rodar do seu home |
| `ERROR: Could not build wheels for capstone` | Falta compilador/headers do Python | `sudo apt install python3-dev build-essential` e reinstale no venv |
| `ptrace: Operation not permitted` (GDB/strace) | Restrição do kernel a ptrace (Yama) | `echo 0 | sudo tee /proc/sys/kernel/yama/ptrace_scope` (temporário) |
| `externally-managed-environment` (pip) | pip global bloqueado no Debian/Ubuntu novos | Use um **venv** (seção 4/5) — nunca `pip install` global |
| `qemu: uncaught target signal 11` | Rodando binário de outra arch sem o QEMU certo | Instale `qemu-user` e use `qemu-arm`/`qemu-mips` conforme a arch |
| `This app can't run on your PC` (x64dbg) | Baixou a versão x86 num Windows x64 (ou vice-versa) | Use `x96dbg.exe`, que escolhe a versão certa |
| Cutter/AppImage: `dlopen(): error loading libfuse.so.2` | Falta FUSE para AppImage | `sudo apt install libfuse2` |
| Frida: `Failed to establish connection` (Android) | `frida-server` não roda no dispositivo/arch errada | Suba o `frida-server` correto no alvo; ver [`23`](23-mobile-e-managed.md) |

---

## 16. Checklist — ambiente pronto

Rode um por linha. Todos devem responder sem erro antes de ir para o [`04`](04-como-comecar.md):

```bash
gcc --version                 # compilador
gdb --version                 # depurador
objdump --version             # binutils
file /bin/ls                  # identificação de binário
python3 -c "import capstone"  # motor de desmontagem (sem saída = ok)
frida --version               # instrumentação dinâmica
r2 -version                   # radare2 (ou: rizin -version)
java -version                 # deve ser 21+ (para o Ghidra)
```
E, uma vez:
```bash
gdb /bin/ls -batch -ex 'start' -ex 'info registers rip' -ex 'quit'
# deve imprimir o valor de RIP — confirma que o GDB depura de verdade
```

**Tudo verde?** Vá para [`04-como-comecar.md`](04-como-comecar.md) e reverta sua primeira função.

---

## Autoteste

1. Você extraiu o radare2 numa pasta mas `r2` dá "command not found". Qual é a causa quase
   certa e a correção exata?
2. Por que **não** se instala pacotes Python de RE com `sudo pip install`? O que se usa no lugar?
3. O Ghidra 12.x reclama de Java. Qual versão mínima ele exige e como você troca a versão ativa?
4. Qual a diferença prática entre `strace` e `ltrace`?
5. Cite o ambiente **sem instalar nada** que você usaria para (a) ver o assembly de um C e
   (b) comparar descompiladores sobre um binário.
6. Como você garante que o mesmo ambiente Python de RE seja recriado em outra máquina?
7. Você vai analisar um malware. Que distro pronta usaria, e qual cuidado de rede tomaria?
8. Onde o Ghidra deixa arquivos escondidos que uma desinstalação por `rm -rf` da pasta não remove?

---

*Fontes consultadas em 03/09/2026:* releases oficiais no GitHub (Ghidra 12.1.3, radare2
6.2.0, rizin 0.9.1, Cutter 2.5.0, x64dbg 2026.05.27, jadx 1.5.6, dnSpyEx 6.6.0, ILSpy 11.0,
upx 5.2.1, pwndbg 2026.07.29), PyPI (frida 17.17.0, capstone 5.0.9, angr 9.3.4, pwntools
4.15.0, LIEF 1.0.0, pyelftools 0.33), documentação de instalação do Ghidra (WhatsNew 12.1:
exige JDK 21, Python 3.9–3.14 para o depurador), hex-rays.com (IDA Free), remnux.org.
