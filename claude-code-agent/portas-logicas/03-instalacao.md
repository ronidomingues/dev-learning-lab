# 03 · Manual de instalação

**Nível:** iniciante · **Data de verificação:** 14/08/2026
**Ambiente onde os comandos Linux foram executados:** Ubuntu 22.04.5 LTS, x86_64

Este é um manual de campo. Cada passo tem: o comando exato, o que ele faz em uma linha,
a verificação com a saída esperada, e o que fazer se a saída for diferente.

---

## ⚡ Antes de tudo: você pode não precisar instalar nada

**Leia esta seção antes de baixar qualquer coisa.** Este assunto tem excelentes
ferramentas de navegador, e elas cobrem confortavelmente do [`01`](01-introducao-leigo.md)
ao [`20`](20-circuitos-combinacionais.md) — ou seja, a maior parte do curso.

| Ferramenta | URL | O que faz | Precisa de conta? |
|---|---|---|---|
| **CircuitVerse** | https://circuitverse.org/simulator | Simulador completo de circuitos digitais, arrasta-e-solta, salva na nuvem, exporta imagem. O mais próximo do Logisim no navegador. | Só para salvar |
| **Falstad Circuit Simulator** | https://www.falstad.com/circuit/ | Simulador **analógico e digital** — mostra elétrons se movendo. Insuperável para entender o transistor virando porta. | Não |
| **nandgame** | https://nandgame.com/ | Jogo que faz você construir um computador inteiro partindo de um relé, nível por nível. Sério e muito bem feito. | Não |
| **EDA Playground** | https://www.edaplayground.com/ | Roda Verilog/VHDL de verdade em simuladores profissionais, no navegador. | Sim, gratuita |
| **Digital JS / DigitalJS Online** | https://digitaljs.tilk.eu/ | Sintetiza Verilog e mostra o circuito de portas resultante. Excelente para ver "no que meu código virou". | Não |
| **Logisim-evolution no navegador** | https://logisim-evolution.github.io/ (versão web, quando disponível) | Versão reduzida. Confira a disponibilidade — o projeto principal é desktop. | Não |

**Recomendação:** comece pelo **nandgame** (2 horas divertidas que ensinam metade do curso)
e use o **CircuitVerse** para os laboratórios. Instale o Logisim só quando o navegador
ficar apertado — o que costuma acontecer no [`30-circuitos-sequenciais.md`](30-circuitos-sequenciais.md),
quando os circuitos ficam grandes.

> **Por que instalar então?** Três razões reais: (1) circuitos grandes travam no navegador;
> (2) Logisim tem subcircuitos hierárquicos e análise de circuito combinacional que os
> simuladores web não têm; (3) Verilog local é a ponte para FPGA e para o mundo profissional.

---

## Panorama do que se instala

Não é uma ferramenta só. São **cinco tecnologias**, e cada uma tem sua seção:

```mermaid
graph TD
    A[Java JDK 21+] --> B[Logisim-evolution 4.1.0]
    A --> C[Digital 0.31]
    D[Python 3.11+] --> E[projeto-modelo deste curso]
    F[Icarus Verilog 13.0] --> G[simulação de HDL]
    G --> H[GTKWave / Surfer]
    I[Editor: VS Code] --> G
    I --> E
    J[Vivado ou Quartus] -.opcional, só com FPGA física.-> K[placa real]
```

| # | Tecnologia | Obrigatória? | Tamanho em disco | Seção |
|---|---|---|---|---|
| 1 | Java JDK 21+ | se usar Logisim | ~330 MB | [§1](#1-java-jdk-21) |
| 2 | Logisim-evolution 4.1.0 | recomendada | ~120 MB | [§2](#2-logisim-evolution-410) |
| 3 | Digital 0.31 | opcional | ~60 MB | [§3](#3-digital-031-alternativa-leve) |
| 4 | Python 3.11+ | sim (projeto-modelo) | ~150 MB | [§4](#4-python-311) |
| 5 | Icarus Verilog + GTKWave | intermediário+ | ~80 MB | [§5](#5-icarus-verilog-e-gtkwave) |
| 6 | Editor de texto | sim | ~350 MB (VS Code) | [§6](#6-editor-de-texto) |
| 7 | Vivado / Quartus | **não** | **50–100 GB** | [§7](#7-fpga-proprietária--só-se-tiver-placa) |

---

## 1. Java (JDK 21+)

**Por que:** Logisim-evolution 4.1.0 é escrito em Java e **exige Java 21 ou superior**.
Java 17 **não serve** — é o erro nº 1 de instalação deste assunto (a versão 17 ainda é o
padrão de muitas distribuições LTS; foi o caso da máquina onde este manual foi escrito).

**Versão testada:** OpenJDK/Temurin **21 LTS**. Mínimo suportado: 21. Evite: 8, 11, 17 (velhos demais para o Logisim 4.x).

### 1.1 Linux — Debian / Ubuntu

```bash
sudo apt update && sudo apt install -y openjdk-21-jdk
```
*Instala o kit de desenvolvimento Java 21 do repositório da distribuição.*

Verificação:
```bash
java -version
# esperado (a saída vai para o stderr, é normal):
# openjdk version "21.0.x" 2026-xx-xx
```

**Se a saída for `openjdk version "17..."`** — você tem mais de um Java instalado e o
sistema está usando o antigo. Corrija a alternativa padrão:
```bash
sudo update-alternatives --config java
# escolha o número da linha que contém "java-21"
```

**Se disser `Unable to locate package openjdk-21-jdk`** (comum no Ubuntu 20.04 e mais antigos):
```bash
sudo apt install -y wget apt-transport-https gpg
wget -qO- https://packages.adoptium.net/artifactory/api/gpg/key/public \
  | sudo gpg --dearmor -o /usr/share/keyrings/adoptium.gpg
echo "deb [signed-by=/usr/share/keyrings/adoptium.gpg] https://packages.adoptium.net/artifactory/deb $(awk -F= '/^VERSION_CODENAME/{print$2}' /etc/os-release) main" \
  | sudo tee /etc/apt/sources.list.d/adoptium.list
sudo apt update && sudo apt install -y temurin-21-jdk
```
*Adiciona o repositório oficial da Eclipse Adoptium (o distribuidor de OpenJDK mais usado) e instala de lá.*

### 1.2 Linux — Fedora / RHEL / Rocky

```bash
sudo dnf install -y java-21-openjdk-devel
```
Verificação idêntica à anterior.

### 1.3 Linux — Arch

```bash
sudo pacman -S jdk21-openjdk
sudo archlinux-java set java-21-openjdk   # define como padrão
```

### 1.4 macOS (Intel e Apple Silicon)

Com Homebrew (instale o Homebrew antes, se não tiver — ver §6.2):
```bash
brew install --cask temurin@21
```
*Instala o Temurin JDK 21 no formato de aplicativo do macOS.*

Verificação:
```bash
java -version
/usr/libexec/java_home -V     # lista todos os JDKs instalados e onde estão
```

> **Apple Silicon (M1–M5):** o `brew install --cask temurin@21` já entrega o binário
> **ARM64 nativo** em Macs ARM. Não instale a versão x86_64 "por segurança" — ela roda
> sob Rosetta 2, fica ~30% mais lenta e não traz benefício nenhum aqui.

### 1.5 Windows (nativo)

```powershell
winget install EclipseAdoptium.Temurin.21.JDK
```
*Instala o Temurin JDK 21 pelo gerenciador de pacotes embutido no Windows 10/11.*

**Feche e reabra o PowerShell** (o instalador altera o PATH e a janela atual não enxerga a mudança).

Verificação:
```powershell
java -version
# esperado: openjdk version "21.0.x"
```

Sem `winget`? Baixe o instalador `.msi` em https://adoptium.net/temurin/releases/?version=21
e marque a opção **"Set JAVA_HOME variable"** durante a instalação.

### 1.6 Windows via WSL2

Se você usa WSL2, siga a receita **Debian/Ubuntu** (§1.1) *dentro* do WSL.
Para o Logisim abrir janela gráfica no WSL2, você precisa do WSLg (embutido no Windows 11
e no Windows 10 atualizado). Teste com:
```bash
echo $DISPLAY
# esperado: algo como :0 — se vier vazio, o WSLg não está ativo
```

> **Recomendação para Windows:** use o **Logisim nativo do Windows** (mais simples, sem
> camada gráfica extra) e o **WSL2 para Verilog** (onde as ferramentas Unix são muito
> melhores). Essa divisão é o caminho de menor atrito, e é o que uso.

---

## 2. Logisim-evolution 4.1.0

**O que é:** simulador de circuitos digitais com interface gráfica. Você arrasta portas,
liga fios com o mouse, clica em interruptores e vê os fios acenderem. É a ferramenta
didática mais usada do mundo neste assunto.

**Versão testada:** 4.1.0, publicada em **15/02/2026** (fonte: releases oficiais no GitHub, consultado em 14/08/2026).
**Mínimo:** 3.x ainda funciona. **Evite:** o `logisim` original (versão 2.7.1), que está nos
repositórios de várias distribuições — foi **abandonado em 2014** e o `logisim-evolution` é o
sucessor mantido pela comunidade. Instalar o pacote errado é a armadilha nº 2 desta página.

> ⚠️ **`sudo apt install logisim` instala o projeto morto de 2014.** Não faça isso.

### 2.1 Linux — Debian / Ubuntu (arquivo .deb oficial)

```bash
cd /tmp
wget https://github.com/logisim-evolution/logisim-evolution/releases/download/v4.1.0/logisim-evolution_4.1.0_amd64.deb
```
*Baixa o pacote oficial para Debian/Ubuntu em x86_64.*

```bash
sudo apt install -y ./logisim-evolution_4.1.0_amd64.deb
```
*Instala o pacote local resolvendo as dependências (use `apt install ./arquivo`, não `dpkg -i`, para que as dependências sejam resolvidas).*

Verificação:
```bash
logisim-evolution --version
# esperado: 4.1.0
```
Ou simplesmente procure "Logisim" no menu de aplicativos e abra.

### 2.2 Linux — Fedora / RHEL

```bash
cd /tmp
wget https://github.com/logisim-evolution/logisim-evolution/releases/download/v4.1.0/logisim-evolution-4.1.0-1.x86_64.rpm
sudo dnf install -y ./logisim-evolution-4.1.0-1.x86_64.rpm
```

### 2.3 Qualquer sistema com Java — o `.jar` universal

Funciona em Linux, macOS e Windows sem instalar nada de fato: é um único arquivo.

```bash
cd ~/Downloads
wget https://github.com/logisim-evolution/logisim-evolution/releases/download/v4.1.0/logisim-evolution-4.1.0-all.jar
java -jar logisim-evolution-4.1.0-all.jar
```
*Baixa o pacote autocontido e o executa sobre a JVM instalada no §1.*

**Este é o método que recomendo para quem só quer testar** — não mexe no sistema, e
"desinstalar" é apagar um arquivo.

### 2.4 macOS

```bash
cd ~/Downloads
# Apple Silicon (M1 a M5):
curl -LO https://github.com/logisim-evolution/logisim-evolution/releases/download/v4.1.0/logisim-evolution-4.1.0-aarch64.dmg
# Intel:
curl -LO https://github.com/logisim-evolution/logisim-evolution/releases/download/v4.1.0/logisim-evolution-4.1.0-x86_64.dmg
```
Abra o `.dmg` e arraste para *Aplicativos*.

**Se o macOS disser "não pode ser aberto porque é de um desenvolvedor não identificado":**
clique com o botão direito no aplicativo → **Abrir** → **Abrir** de novo no diálogo.
Isso cria uma exceção permanente. (O projeto é livre e não paga a assinatura de
desenvolvedor da Apple — o aviso é sobre assinatura, não sobre risco conhecido.)

Se persistir:
```bash
xattr -dr com.apple.quarantine /Applications/logisim-evolution.app
```
*Remove a marca de "baixado da internet" que dispara o Gatekeeper.*

### 2.5 Windows

```powershell
winget install --id logisim-evolution.logisim-evolution
```
Ou baixe o `.msi` em https://github.com/logisim-evolution/logisim-evolution/releases/tag/v4.1.0 —
use `logisim-evolution-4.1.0-amd64.msi` (Intel/AMD) ou `-aarch64.msi` (ARM, Surface Pro X e similares).

Verificação: abra pelo Menu Iniciar. A janela deve mostrar a barra de ferramentas com
os símbolos de porta à esquerda.

### 2.6 Teste funcional (faça, não pule)

1. Abra o Logisim.
2. Na árvore à esquerda, expanda **Gates** e clique em **AND Gate**.
3. Clique na tela para posicionar.
4. Pegue **Wiring → Pin** (entrada) duas vezes e ligue às entradas do AND.
5. Pegue **Wiring → Pin** e, nas propriedades, marque **Output? = Yes**; ligue à saída.
6. Clique na ferramenta **mãozinha (poke)** e clique nos pinos de entrada para alternar 0/1.

**Deu certo se:** a saída só fica verde-claro (1) quando as duas entradas estão em 1.
Se deu certo, você já reproduziu a seção 2 do [`01`](01-introducao-leigo.md).

---

## 3. Digital 0.31 (alternativa leve)

**O que é:** outro simulador em Java, do professor alemão Helmut Neemann. Mais leve e,
na minha opinião, com interface mais agradável e simulação em nível de porta mais didática
que a do Logisim. **Ponto fraco:** comunidade e material de curso muito menores — quase
todo tutorial de faculdade usa Logisim.

**Versão:** 0.31 (publicada em 03/09/2024 — o projeto está estável, não abandonado; simplesmente não precisou de release desde então). Requer Java 8+; funciona bem com o Java 21 do §1.

Todos os sistemas:
```bash
cd ~/Downloads
wget https://github.com/hneemann/Digital/releases/download/v0.31/Digital.zip
unzip Digital.zip -d Digital
java -jar Digital/Digital/Digital.jar
```
*Baixa, extrai e executa. Não instala nada no sistema.*

Verificação: a janela abre com uma tela quadriculada em branco e a barra de componentes no topo.

**Escolha entre os dois:** se você está seguindo uma disciplina de faculdade, use **Logisim**
(é o que os enunciados assumem). Se está estudando sozinho, experimente os dois numa tarde
e fique com o que agradar — os conceitos são idênticos.

---

## 4. Python 3.11+

**Por que:** o [`07-projeto-modelo/`](07-projeto-modelo/README.md) é Python puro, sem
nenhuma dependência externa. Ele funciona a partir do Python **3.9**; recomendo 3.11+ pela
velocidade e mensagens de erro melhores.

### 4.1 Linux

Já vem instalado em praticamente toda distribuição. Verifique primeiro:
```bash
python3 --version
# esperado: Python 3.9.x ou superior
```

Se faltar:
```bash
sudo apt install -y python3 python3-venv    # Debian/Ubuntu
sudo dnf install -y python3                 # Fedora/RHEL
```

### 4.2 macOS

O Python que vem com o macOS é velho e existe para uso interno do sistema — **não o use**.
```bash
brew install python@3.13
```
Verificação:
```bash
python3 --version
which python3
# esperado: /opt/homebrew/bin/python3 (Apple Silicon) ou /usr/local/bin/python3 (Intel)
```
**Se `which python3` responder `/usr/bin/python3`**, o PATH está pegando o Python do sistema.
Corrija adicionando o Homebrew ao início do PATH (ver §8).

### 4.3 Windows

```powershell
winget install Python.Python.3.13
```
Ou o instalador em python.org — e **marque a caixa "Add python.exe to PATH"** na primeira
tela. Essa caixa desmarcada é a causa de metade dos problemas de Python no Windows.

Verificação:
```powershell
python --version
# esperado: Python 3.13.x
```
**Se abrir a Microsoft Store** em vez de mostrar a versão: o Windows tem um "atalho de
aplicativo" fantasma. Desative em *Configurações → Aplicativos → Configurações avançadas
de aplicativos → Aliases de execução de aplicativo* → desligue `python.exe` e `python3.exe`.

### 4.4 Rodando o projeto-modelo (verificação real)

```bash
cd portas-logicas/07-projeto-modelo
python3 testes.py
# esperado, ao final: "76 testes, 76 aprovados, 0 falhas"
```

---

## 5. Icarus Verilog e GTKWave

**Por que:** a partir do [`40-da-porta-ao-computador.md`](40-da-porta-ao-computador.md),
desenhar circuito com o mouse deixa de ser viável — profissionais **descrevem** o hardware
em texto, numa linguagem de descrição de hardware (**HDL**, *hardware description language*).
Verilog é a mais usada na indústria; VHDL domina no meio acadêmico europeu e na área militar.

- **Icarus Verilog** (`iverilog`) — compilador/simulador Verilog livre.
- **GTKWave** — visualizador de formas de onda: mostra o valor de cada sinal ao longo do tempo.

**Versões:** Icarus Verilog **13.0** (upstream, publicado em 02/03/2026). Atenção: os
repositórios de distribuições LTS costumam trazer a **11.0** (é o caso do Ubuntu 22.04, verificado
em 14/08/2026). A 11.0 serve para tudo neste curso; a 13.0 tem melhor suporte a SystemVerilog.

### 5.1 Linux — Debian / Ubuntu

```bash
sudo apt install -y iverilog gtkwave
```
*Instala o simulador Verilog e o visualizador de ondas.*

Verificação:
```bash
iverilog -V | head -1
# esperado: Icarus Verilog version 11.0 (stable) — ou superior
gtkwave --version | head -1
# esperado: GTKWave Analyzer v3.3.x
```

### 5.2 Linux — Fedora / RHEL

```bash
sudo dnf install -y iverilog gtkwave
```

### 5.3 macOS

```bash
brew install icarus-verilog
brew install --cask gtkwave
```
> **No macOS, o GTKWave costuma dar trabalho** (depende de GTK e de Perl). Alternativa
> moderna e muito melhor: **Surfer** (https://surfer-project.org/), visualizador de ondas
> escrito em Rust, que roda inclusive no navegador. É o que uso hoje.

### 5.4 Windows

**Caminho recomendado: WSL2.** Instale o Ubuntu no WSL e siga §5.1:
```powershell
wsl --install -d Ubuntu
```
*Instala o WSL2 com Ubuntu. Reinicie quando pedir.*

**Caminho nativo** (se não quiser WSL): baixe o instalador não oficial em
http://bleyer.org/icarus/ — ele empacota `iverilog` + `gtkwave` para Windows. É mantido por
terceiro, e defasado em relação ao upstream. Funciona para este curso.

### 5.5 Teste funcional

Crie `porta.v`:
```verilog
// porta.v — testa AND, OR e XOR sobre todas as combinações
module porta;
  reg a, b;                      // reg: sinais que eu controlo no teste
  initial begin
    $dumpfile("porta.vcd");      // arquivo de ondas para o GTKWave
    $dumpvars(0, porta);
    $display(" a b | AND OR XOR");
    for (integer i = 0; i < 4; i = i + 1) begin
      {a, b} = i[1:0];           // percorre 00, 01, 10, 11
      #1;                        // espera 1 unidade de tempo
      $display(" %b %b |  %b   %b   %b", a, b, a & b, a | b, a ^ b);
    end
  end
endmodule
```

```bash
iverilog -o porta porta.v && ./porta
```
*Compila e executa. Saída esperada:*
```
 a b | AND OR XOR
 0 0 |  0   0   0
 0 1 |  0   1   1
 1 0 |  0   1   1
 1 1 |  1   1   0
```

Veja as ondas:
```bash
gtkwave porta.vcd
```
*Abre a janela; arraste os sinais `a` e `b` da lista da esquerda para a área de ondas.*

---

## 6. Editor de texto

### 6.1 VS Code (recomendado, todos os SOs)

```bash
# Debian/Ubuntu
sudo snap install code --classic
# Fedora
sudo dnf install -y code      # após habilitar o repositório da Microsoft
# macOS
brew install --cask visual-studio-code
# Windows
winget install Microsoft.VisualStudioCode
```

**Extensões que valem a pena para este assunto:**

| Extensão | Para quê |
|---|---|
| `mshr-h.veriloghdl` (Verilog-HDL/SystemVerilog) | destaque de sintaxe, ida à definição, lint |
| `ms-python.python` | rodar o projeto-modelo com um clique |
| `bierner.markdown-mermaid` | ver os diagramas deste curso renderizados |

Verificação:
```bash
code --version
# esperado: três linhas — versão, hash do commit, arquitetura
```

### 6.2 Homebrew (macOS) — se ainda não tiver

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```
*Instala o gerenciador de pacotes do macOS. Ao final, ele imprime dois ou três comandos
para adicionar ao seu `.zprofile` — **execute-os**, senão o `brew` não fica no PATH.*

---

## 7. FPGA proprietária — só se tiver placa

**Pule esta seção se você não tem uma placa FPGA na mesa.** São 50 a 100 GB de download e
horas de instalação para algo que este curso não exige em nenhum momento.

| Ferramenta | Fabricante | Licença gratuita | Tamanho | Placas |
|---|---|---|---|---|
| **AMD Vivado** (ex-Xilinx), edição Standard | AMD | sim, gratuita para dispositivos pequenos/médios | 60–100 GB | Basys 3, Arty, Nexys |
| **Intel Quartus Prime Lite** | Altera/Intel | sim, gratuita | 25–40 GB | DE10-Lite, Cyclone |
| **Gowin EDA Education** | Gowin | sim, exige cadastro | ~2 GB | Tang Nano |
| **Cadeia aberta: Yosys + nextpnr + IceStorm** | comunidade | **livre (ISC/MIT)** | ~500 MB | iCE40, ECP5, Gowin |

> **Opinião profissional:** se você vai comprar sua primeira placa para estudar, compre
> uma suportada pela **cadeia aberta** (iCE40 ou ECP5, ou Tang Nano com o `apicula`).
> Instalar 80 GB de Vivado para acender um LED é uma experiência que faz gente desistir
> de hardware. A cadeia aberta instala em 5 minutos:

```bash
# Debian/Ubuntu — cadeia de síntese aberta
sudo apt install -y yosys nextpnr-ice40 fpga-icestorm
```
Verificação:
```bash
yosys -V
# esperado: Yosys 0.x (git sha1 ...)
```

Preços de placas em [`80-custos-e-licencas.md`](80-custos-e-licencas.md).

---

## 8. PATH e variáveis de ambiente

O problema mais frequente e mais frustrante de qualquer instalação: você instalou,
mas o terminal diz que o comando não existe.

**O que é o PATH:** uma lista de pastas onde o sistema procura programas quando você
digita um nome. Se o programa está numa pasta fora da lista, ele "não existe" para o terminal.

Ver o PATH atual:
```bash
echo $PATH          # Linux e macOS
```
```powershell
$env:Path -split ';'   # Windows PowerShell
```

Descobrir de onde um comando está vindo:
```bash
which java iverilog python3    # Linux/macOS
```
```powershell
Get-Command java, python       # Windows
```

Adicionar uma pasta ao PATH permanentemente:

| SO / shell | Arquivo a editar | Linha a acrescentar |
|---|---|---|
| Linux, bash | `~/.bashrc` | `export PATH="$HOME/.local/bin:$PATH"` |
| Linux/macOS, zsh | `~/.zshrc` | `export PATH="$HOME/.local/bin:$PATH"` |
| macOS, login shell | `~/.zprofile` | `eval "$(/opt/homebrew/bin/brew shellenv)"` |
| Windows | Perfil do PowerShell (`$PROFILE`) | `$env:Path += ";C:\caminho\da\pasta"` |

Depois de editar, **recarregue** — ou a mudança "não pega":
```bash
source ~/.bashrc      # ou ~/.zshrc
```

> **Por que "não pegou" antes de reabrir o terminal?** Porque variáveis de ambiente são
> copiadas para o processo **no momento em que ele nasce**. Seu terminal já estava rodando
> quando o instalador mudou o arquivo de perfil; ele não relê nada sozinho. Não é bug,
> é como processos funcionam em qualquer sistema operacional desde os anos 1970.

**Variável específica deste assunto — `JAVA_HOME`:** algumas ferramentas Java a exigem.
```bash
export JAVA_HOME=$(dirname $(dirname $(readlink -f $(which java))))
echo $JAVA_HOME
# esperado: /usr/lib/jvm/java-21-openjdk-amd64 (ou similar)
```

---

## 9. Permissões — onde `sudo` ajuda e onde atrapalha

| Situação | Certo | Errado e por quê |
|---|---|---|
| Instalar pacote do sistema (`apt`, `dnf`, `pacman`) | **com `sudo`** | sem `sudo` não funciona mesmo |
| Homebrew no macOS | **sem `sudo`, nunca** | `sudo brew` corrompe as permissões do `/opt/homebrew` e o conserto é doloroso |
| `pip install` | `pip install --user` ou dentro de um venv | `sudo pip install` mistura pacotes seus com os do sistema; uma atualização do SO pode quebrar seu ambiente, ou o seu pacote pode quebrar ferramentas do sistema que dependem do Python |
| Rodar o Logisim | **usuário comum** | rodar simulador como root cria arquivos de projeto que depois você não consegue editar |
| Gravar FPGA por USB no Linux | adicionar regra `udev` | usar `sudo` toda vez é sintoma de regra faltando |

Regra `udev` para placas FPGA (evita `sudo` para sempre):
```bash
sudo usermod -aG plugdev $USER          # entra no grupo de dispositivos removíveis
# depois: faça logout e login de novo — grupos só valem em sessão nova
```

---

## 10. Rede corporativa (proxy, certificado, firewall)

Se você está atrás de proxy de empresa:

```bash
export http_proxy="http://usuario:senha@proxy.empresa:3128"
export https_proxy="$http_proxy"
export no_proxy="localhost,127.0.0.1,.empresa.local"
```
Para o `apt` valer também:
```bash
echo 'Acquire::http::Proxy "http://proxy.empresa:3128";' | sudo tee /etc/apt/apt.conf.d/95proxy
```

**Certificado interno (inspeção de TLS):** se o `wget`/`curl` reclamar de certificado,
adicione o certificado da empresa ao repositório do sistema — **não** desative a verificação:
```bash
sudo cp certificado-empresa.crt /usr/local/share/ca-certificates/
sudo update-ca-certificates
```
*Instalar o certificado é seguro e correto; usar `--no-check-certificate` desliga a
proteção para **todos** os downloads e é como estudantes acabam baixando binário adulterado.*

**Firewall:** o GitHub Releases (de onde vêm Logisim e Digital) usa
`objects.githubusercontent.com`. É comum a empresa liberar `github.com` e esquecer esse
domínio, e aí o download falha no meio. Peça a liberação dos dois.

---

## 11. Convivência de versões

| Ferramenta | Como ter duas versões |
|---|---|
| **Java** | `sudo update-alternatives --config java` (Linux) · `/usr/libexec/java_home -v 21` (macOS) · SDKMAN! (`sdk use java 21-tem`) |
| **Python** | `pyenv` (`pyenv install 3.13.0 && pyenv local 3.13.0`) ou `uv python install` |
| **Logisim** | Cada versão é um `.jar` separado. Guarde os dois e rode `java -jar` no que quiser. **É a forma mais simples que existe.** |
| **Icarus Verilog** | compile o upstream em `/opt/iverilog-13` e chame pelo caminho completo |
| **Vivado/Quartus** | instalam-se lado a lado por padrão, em pastas versionadas |

**Reprodutibilidade** — o que versionar junto com seus circuitos:

| Arquivo | Para quê |
|---|---|
| `.tool-versions` (mise/asdf) | fixa versões de Java e Python do projeto |
| `.circ` do Logisim | é XML — versione no git, o diff é legível |
| `Makefile` | registra os comandos exatos de simulação (é a documentação que não mente) |
| `requirements.txt` | mesmo vazio, documenta que o projeto não tem dependências |

---

## 12. Atualizar e voltar atrás

```bash
# Debian/Ubuntu — atualizar tudo do sistema
sudo apt update && sudo apt upgrade

# Logisim: baixe o novo .jar e mantenha o antigo — reverter é trocar o arquivo
# Homebrew
brew upgrade && brew cleanup
# Windows
winget upgrade --all
```

**Voltar a uma versão anterior:**
```bash
apt-cache madison iverilog                 # lista versões disponíveis
sudo apt install iverilog=11.0-1.1         # instala uma específica
sudo apt-mark hold iverilog                # impede atualização automática
```

> **Regra prática:** neste assunto, atualizar tem risco baixíssimo (as ferramentas são
> estáveis e os formatos de arquivo são compatíveis para trás). A exceção é o Logisim:
> um arquivo `.circ` salvo na 4.x pode não abrir na 3.x. **Salve uma cópia antes de
> atualizar se tiver trabalho importante.**

---

## 13. Desinstalar por completo

```bash
# Logisim-evolution (Debian/Ubuntu)
sudo apt remove --purge logisim-evolution
rm -rf ~/.logisim-evolution          # preferências e histórico

# Java
sudo apt remove --purge openjdk-21-jdk
rm -rf ~/.java                       # cache de preferências da JVM

# Icarus Verilog e GTKWave
sudo apt remove --purge iverilog gtkwave
rm -rf ~/.gtkwave                    # não existe em toda versão; ignore se não houver

# Python — pacotes instalados pelo usuário
rm -rf ~/.local/lib/python3.*        # ⚠️ apaga TODOS os pacotes de usuário
rm -rf ~/.cache/pip

# Limpeza geral (Debian/Ubuntu)
sudo apt autoremove --purge && sudo apt clean

# macOS
brew uninstall --zap --cask temurin@21   # --zap remove também as configurações
rm -rf ~/Library/Application\ Support/logisim-evolution

# Windows
winget uninstall EclipseAdoptium.Temurin.21.JDK
# resíduos: %APPDATA%\logisim-evolution e %LOCALAPPDATA%\Temp
```

**O que quase sempre fica para trás e ninguém lembra:**

| Resíduo | Onde | Tamanho típico |
|---|---|---|
| Preferências do Logisim | `~/.logisim-evolution` | < 1 MB |
| Cache do pip | `~/.cache/pip` | 100 MB – 2 GB |
| Downloads do Homebrew | `~/Library/Caches/Homebrew` | 1–10 GB |
| Instalações do Vivado | `/tools/Xilinx`, `~/.Xilinx` | **50–100 GB** |
| Arquivos `.vcd` de simulação | onde você rodou | **crescem sem limite** — um `$dumpvars` esquecido num loop longo já produziu arquivos de dezenas de GB |

---

## 14. Solução de problemas — mensagens literais

| Mensagem | Causa provável | Correção |
|---|---|---|
| `Error: A JNI error has occurred` seguido de `UnsupportedClassVersionError: ... has been compiled by a more recent version of the Java Runtime` | Java 17 (ou anterior) tentando rodar Logisim 4.x, que exige 21 | Instale o JDK 21 (§1) e confira com `java -version`; ajuste com `update-alternatives` |
| `command not found: logisim-evolution` | não está no PATH, ou você instalou só o `.jar` | Rode `java -jar logisim-evolution-4.1.0-all.jar`, ou veja §8 |
| `bash: iverilog: command not found` após `apt install` bem-sucedido | terminal aberto antes da instalação com cache de comandos | `hash -r` ou abra outro terminal |
| `E: Unable to locate package openjdk-21-jdk` | distribuição LTS antiga, sem Java 21 nos repositórios | Use o repositório Adoptium (§1.1, segundo bloco) |
| `dpkg: dependency problems prevent configuration of logisim-evolution` | instalou com `dpkg -i`, que não resolve dependências | `sudo apt install -f` e, da próxima, use `sudo apt install ./arquivo.deb` |
| `"logisim-evolution" não pode ser aberto porque a Apple não pode verificar...` | Gatekeeper do macOS: app sem assinatura paga | Botão direito → Abrir → Abrir; ou `xattr -dr com.apple.quarantine <app>` |
| `Cannot open display:` / `Unable to access X Display` (WSL2 ou SSH) | não há servidor gráfico acessível | Windows 11 com WSLg atualizado; via SSH use `ssh -X`; ou instale o VcXsrv |
| `Python was not found; run without arguments to install from the Microsoft Store` | alias fantasma do Windows tem precedência sobre o Python real | Desative os aliases (§4.3) e reabra o terminal |
| `zsh: permission denied: ./porta` | binário compilado sem permissão de execução | `chmod +x ./porta` |
| `ERROR: Unknown module type: <nome>` (Yosys) | módulo Verilog não encontrado — arquivo faltando na linha de comando | Passe **todos** os `.v` do projeto ao sintetizador |
| `Certificate verification failed` no `wget`/`curl` | proxy corporativo com inspeção de TLS | Instale o certificado da empresa (§10). **Não** use `--no-check-certificate` |

---

## 15. Checklist "ambiente pronto"

Rode um por linha. Se todos responderem, siga para o [`04-como-comecar.md`](04-como-comecar.md).

```bash
java -version                         # 21.x ou superior
logisim-evolution --version           # 4.1.0   (ou: java -jar logisim-evolution-4.1.0-all.jar abre a janela)
python3 --version                     # 3.9+
iverilog -V | head -1                 # 11.0+   (opcional neste momento)
gtkwave --version | head -1           # 3.3.x   (opcional neste momento)
code --version                        # opcional
```

E o teste que vale por todos:

```bash
cd portas-logicas/07-projeto-modelo && python3 testes.py
# esperado na última linha: 76 testes, 76 aprovados, 0 falhas
```

**Nada instalado e com pressa?** Abra https://nandgame.com/ e comece. Sério.

---

## Autoteste

1. Qual versão mínima de Java o Logisim-evolution 4.1.0 exige, e o que acontece se você usar a 17?
2. Por que `sudo apt install logisim` é uma armadilha?
3. Cite duas ferramentas que permitem estudar portas lógicas sem instalar nada.
4. Por que uma mudança no `.bashrc` só faz efeito num terminal novo?
5. Qual é o problema de `sudo pip install`?
6. No Windows, qual é a divisão recomendada entre nativo e WSL2, e por quê?
7. Você precisa instalar o Vivado para fazer este curso?
8. Que resíduo de desinstalação pode ocupar 100 GB?

*(Respostas: 1 — Java 21; com a 17 dá `UnsupportedClassVersionError`; 2 — instala o Logisim original abandonado em 2014, não o `logisim-evolution`; 3 — CircuitVerse, Falstad, nandgame, EDA Playground, DigitalJS; 4 — variáveis de ambiente são copiadas no nascimento do processo e o terminal aberto não relê o arquivo; 5 — mistura pacotes do usuário com os do sistema e pode quebrar ferramentas do SO; 6 — Logisim nativo, Verilog no WSL2, porque as ferramentas Unix de HDL são muito melhores; 7 — não; 8 — a instalação do Vivado/Quartus em `/tools/Xilinx`.)*

---

### Fontes consultadas (14/08/2026)

- Logisim-evolution — releases oficiais: https://github.com/logisim-evolution/logisim-evolution/releases — v4.1.0, publicada em 15/02/2026; nomes de arquivo verificados via API do GitHub.
- Digital (hneemann) — releases: https://github.com/hneemann/Digital/releases — v0.31, publicada em 03/09/2024.
- Icarus Verilog — releases: https://github.com/steveicarus/iverilog/releases — v13_0, publicada em 02/03/2026.
- Versões em repositório verificadas com `apt-cache policy` em Ubuntu 22.04.5 LTS, 14/08/2026: `iverilog 11.0-1.1`, `gtkwave 3.3.104-2build1`, `logisim 2.7.1~dfsg-4`.
- Eclipse Adoptium (Temurin JDK): https://adoptium.net/temurin/releases/
- CircuitVerse: https://circuitverse.org · Falstad: https://www.falstad.com/circuit/ · nandgame: https://nandgame.com/
