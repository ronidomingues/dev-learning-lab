# 03 · Manual de instalação

**Nível:** iniciante
**Data desta verificação:** 14/08/2026
**Versão de referência:** Power BI Desktop de **julho/2026** (a mais recente segundo a
documentação oficial em 14/08/2026). O índice de pacotes do winget listava a build
`2.155.756.0`. O *change log* público que consultei estava atualizado até
`2.152.1057.0` (QFE de março/2026) — a Microsoft não republica o changelog todo mês.
Confira a sua com **Ajuda → Sobre**.

> **Aviso de honestidade.** Este manual foi escrito num ambiente **Linux (Ubuntu 22.04.5)**,
> onde o Power BI Desktop não roda. Os comandos e requisitos vêm da documentação oficial
> consultada na data acima e da minha prática, **mas os passos de instalação em Windows e
> macOS não foram executados nesta máquina**. Onde eu não vi a tela com meus olhos, o texto
> diz "esperado". Reporte divergências.

---

## 0. Comece por aqui: **você talvez não precise instalar nada hoje**

Antes do caminho longo, o caminho de 5 minutos. Isso existe e evita a desistência no
primeiro dia.

### 0.1 Power BI Service no navegador (funciona em Linux, macOS, ChromeOS, tablet)

1. Vá a **https://app.powerbi.com**.
2. Entre com uma conta **corporativa ou escolar**. (Conta pessoal `@gmail.com`/`@outlook.com`
   **não funciona** — ver §9.)
3. Crie um workspace e importe um arquivo CSV ou Excel.

**O que dá para fazer sem instalar nada:**

- importar arquivos e criar um modelo semântico;
- modelar na web: relacionamentos, medidas DAX, hierarquias, e desde 2026 até a
  **visão TMDL no navegador** (editor de código do modelo);
- criar e editar relatórios, painéis (*dashboards*), aplicativos organizacionais;
- agendar atualização de fontes na nuvem.

**O que exige o Desktop:**

- Power Query completo (o editor da web é mais limitado);
- alguns tipos de fonte e autenticação;
- desenvolvimento sério de relatório (produtividade muito maior);
- salvar `.pbix`/PBIP localmente e versionar em Git.

### 0.2 Outras rotas sem instalar

| Rota | Custo | Serve para |
|---|---|---|
| Windows 365 Cloud PC | assinatura mensal | **Suportado oficialmente**; Desktop completo pelo navegador |
| Azure Virtual Desktop | consumo Azure | **Suportado oficialmente** |
| Máquina Windows de terceiros (laboratório, faculdade) | — | Ótimo para o Bloco A |
| Power BI Mobile (iOS/Android) | grátis | Só consumo, não criação |

**Não use:** Citrix XenApp e outros VDIs publicando o Desktop como aplicativo — não é
suportado e apresenta bugs de renderização e WebView2.

---

## 1. Panorama: tudo o que se instala num ambiente de Power BI

Um erro comum de tutorial é instalar só o Desktop. Um ambiente real de trabalho tem
camadas. Instale nesta ordem; as marcadas com ★ são o mínimo viável.

```
┌─ CAMADA 1 · AUTORIA (na sua máquina) ───────────────────────────────┐
│ ★ Power BI Desktop            criar modelos e relatórios            │
│ ★ WebView2 Runtime            renderização interna (vem junto)      │
│ ★ .NET Framework 4.7.2+       pré-requisito (já vem no Windows)     │
│   Power BI Report Builder     relatórios paginados (pixel-perfect)  │
├─ CAMADA 2 · FERRAMENTAS EXTERNAS (opcionais, transformadoras) ──────┤
│   DAX Studio                  consultar, medir e depurar DAX (grátis)│
│   Tabular Editor 2            editar o modelo em massa (grátis, OSS) │
│   Tabular Editor 3            idem, com IDE completo (pago)          │
│   Bravo for Power BI          análise e tabela de datas (grátis)     │
│   ALM Toolkit                 comparar/mesclar modelos (grátis)      │
│   Power BI Helper / PBI Explorer  documentação e diffs (grátis)      │
├─ CAMADA 3 · CONECTIVIDADE (servidor da empresa) ────────────────────┤
│   On-premises data gateway    atualizar dados que estão on-premises  │
│   Drivers ODBC/OLE DB         Oracle, SAP HANA, DB2, PI System…      │
├─ CAMADA 4 · ENGENHARIA (quando você chega no `25`) ─────────────────┤
│   Git + VS Code               versionar PBIP/TMDL                    │
│   Extensões TMDL/DAX no VS Code                                      │
│   PowerShell + módulo MicrosoftPowerBIMgmt   automação e APIs        │
│   Python + semantic-link (sempy)  automação a partir de notebooks    │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 2. Windows — Power BI Desktop

Existem **quatro** métodos. A recomendação depende do seu caso e está na tabela.

| Método | Atualiza sozinho? | Precisa de admin? | Recomendado para |
|---|---|---|---|
| **Microsoft Store** | Sim, automático | **Não** | ★ **A maioria das pessoas**, e quem não tem admin |
| **Executável (.exe)** | Não (avisa) | Sim | Quem precisa fixar versão, ou máquina sem Store |
| **winget** | Manual (`winget upgrade`) | Sim | Quem gosta de linha de comando; reprodutível |
| **.msi extraído + Intune/SCCM** | Controlado por TI | Sim | Implantação corporativa em massa |

### 2.1 Método A — Microsoft Store (recomendado)

**Vantagens reais**, segundo a documentação oficial: atualização automática em segundo
plano; downloads menores (só os componentes alterados); **não exige privilégio de
administrador**; implantável via Microsoft Store for Business; e a versão da Store contém
**todos os idiomas**, detectando o idioma do Windows a cada abertura.

**Passo 1** — Abra a página do produto na Store.

```
https://aka.ms/pbidesktopstore
```

*O que faz: abre a ficha do Power BI Desktop na Microsoft Store.*

**Passo 2** — Clique em **Instalar** (*Install*) e aguarde (~1 GB de download).

**Passo 3** — Verificação:

```powershell
Get-AppxPackage -Name "Microsoft.MicrosoftPowerBIDesktop" | Select-Object Name, Version
```

*O que faz: lista o pacote instalado da Store e sua versão.*

```
# esperado (formato):
Name                              Version
----                              -------
Microsoft.MicrosoftPowerBIDesktop 2.155.756.0
```

**Se a saída for vazia:** o pacote não está instalado para o seu usuário. Abra a Store e
confira em *Biblioteca → Obter atualizações*. Se a Store estiver bloqueada por política de
grupo, use o Método B.

**Duas limitações da versão Store**, documentadas oficialmente:

1. Se você usa o conector **SAP**, talvez precise mover os arquivos do driver SAP para
   `C:\Windows\System32`.
2. Instalar pela Store **não copia as configurações** da versão `.exe`: você terá de
   reconectar as fontes recentes e reinserir credenciais.

### 2.2 Método B — Executável (.exe)

**Passo 1** — Baixe do Centro de Download oficial:

```
https://www.microsoft.com/download/details.aspx?id=58494
```

**Passo 2** — Escolha a versão **64 bits** (`PBIDesktopSetup_x64.exe`).

> **A versão de 32 bits não é mais suportada.** Se você tem uma instalação de 32 bits,
> ela não recebe mais atualizações nem suporte — migre.

**Passo 3** — Execute o instalador e aceite o contrato.

**Passo 4** — Verificação (PowerShell):

```powershell
(Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Microsoft Power BI Desktop").InstallLocation
```

*O que faz: mostra a pasta onde o Desktop foi instalado pelo `.exe`.*

```
# esperado (exemplo):
C:\Program Files\Microsoft Power BI Desktop\
```

**Passo 5** — Confirme a versão dentro do programa: **Ajuda → Sobre** (*Help → About*),
linha **Versão**.

#### Instalação silenciosa (para scripts e TI)

Parâmetros oficiais do instalador:

```powershell
PBIDesktopSetup_x64.exe -quiet -norestart ACCEPT_EULA=1 LANGUAGE=pt-BR INSTALLDESKTOPSHORTCUT=1
```

*O que faz: instala sem interface, sem reiniciar, aceitando a licença, em português do
Brasil, criando atalho na área de trabalho.*

| Opção | Efeito |
|---|---|
| `-q`, `-quiet`, `-s`, `-silent` | Instalação silenciosa |
| `-passive` | Só a barra de progresso |
| `-norestart` | Suprime a exigência de reinício |
| `-forcerestart` / `-promptrestart` | Reinicia sem perguntar / pergunta (padrão) |
| `-l<arquivo>`, `-log<arquivo>` | Grava log da instalação |
| `-uninstall` | Desinstala |
| `-repair` | Repara (ou instala, se ausente) |
| `ACCEPT_EULA=1` | Aceita a licença automaticamente |
| `ENABLECXP=1` | Adere ao programa de experiência do cliente (telemetria de uso) |
| `INSTALLDESKTOPSHORTCUT=1` | Cria atalho |
| `INSTALLLOCATION=<caminho>` | Pasta de instalação |
| `LANGUAGE=pt-BR` | Idioma padrão (senão usa o do Windows) |
| `DISABLE_UPDATE_NOTIFICATION=1` | Desliga o aviso de atualização |

### 2.3 Método C — winget

```powershell
winget install --exact --id Microsoft.PowerBI
```

*O que faz: instala a última versão publicada do Power BI Desktop pelo gerenciador de
pacotes do Windows.*

Versão fixa e silenciosa (útil em provisionamento reprodutível):

```powershell
winget install --id Microsoft.PowerBI --exact --version 2.155.756.0 --silent --accept-package-agreements --accept-source-agreements
```

Verificação:

```powershell
winget list --id Microsoft.PowerBI
```

```
# esperado:
Name                     Id                Version       Source
------------------------------------------------------------------
Microsoft Power BI Desktop  Microsoft.PowerBI  2.155.756.0  winget
```

**Erro conhecido:** `Installer hash does not match` — acontece quando a Microsoft
republica o instalador sem atualizar o manifesto. Contorno:
`winget install --id Microsoft.PowerBI --ignore-security-hash` (use **só** se você
confia na origem) ou aguarde o manifesto ser corrigido; alternativamente use o Método A.

### 2.4 Método D — extrair o `.msi` para implantação corporativa

Ferramentas de implantação (Intune, SCCM) às vezes exigem `.msi`. O instalador oficial é
`.exe`, mas contém `.msi` dentro. O procedimento **oficialmente documentado** usa o
WiX Toolset (produto de terceiros):

```powershell
# 1. Instale o WiX Toolset: https://wixtoolset.org/
# 2. Em um prompt de administrador, na pasta do WiX:
Dark.exe C:\PBIDesktopSetup_x64.exe -x C:\output
```

*O que faz: descompacta o instalador; os `.msi` ficam em `C:\output\AttachedContainer`.*

> **Restrição documentada:** atualizar uma instalação feita por `.exe` usando um `.msi`
> extraído **não é suportado**. Desinstale a versão antiga primeiro.
>
> **Restrição documentada:** instalar a versão `.msi` (obsoleta) e a versão da Store na
> mesma máquina (*side-by-side*) **não é suportado**. Desinstale manualmente antes.

### 2.5 WebView2 e .NET

Normalmente já estão presentes. Se faltarem:

```powershell
# WebView2 Runtime (Evergreen)
winget install --exact --id Microsoft.EdgeWebView2Runtime
```

*O que faz: instala o runtime de renderização que o Desktop usa para painéis internos,
diálogos de login e visuais.*

Verificação:

```powershell
Get-ChildItem "HKLM:\SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}" |
  ForEach-Object { (Get-ItemProperty $_.PSPath).pv }
```

```
# esperado: um número de versão, p.ex. 141.0.3537.85
```

**Sintoma clássico de WebView2 ausente ou quebrado:** telas em branco no Power BI Desktop,
diálogo de login que não abre, ou o erro literal
`Microsoft Edge can't read and write to its data directory`.

> **Limitação documentada:** o Power BI Desktop **não roda sob conta de sistema**
> (`SYSTEM`), porque o WebView2 não suporta contas de sistema. É a causa do erro acima em
> automações e agendadores de tarefa.

### 2.6 Power BI Report Builder (relatórios paginados)

Produto **separado**, para relatórios de página fixa (faturas, boletos, extratos):

```powershell
winget install --exact --id Microsoft.PowerBIReportBuilder
```

Não é obrigatório. Vale quando você precisa de saída paginada em PDF — ver
[`12-arquitetura.md`](12-arquitetura.md).

### 2.7 Power BI Desktop *for Report Server* — atenção

Se sua empresa usa **Power BI Report Server** (servidor local, sem nuvem), você precisa da
**versão específica** do Desktop "otimizada para Report Server", que segue o calendário do
servidor (janeiro/maio/setembro) e **não** o mensal. As duas versões podem coexistir na
mesma máquina.

```powershell
winget install --exact --id Microsoft.PowerBI.DesktopReportServer
```

> **Armadilha real:** abrir um `.pbix` do Report Server na versão mensal do Desktop e
> salvar **impede** a publicação de volta no Report Server. Confira sempre o título da
> janela: a versão de Report Server diz explicitamente isso.

---

## 3. Windows — as ferramentas externas que mudam o jogo

Nenhuma é obrigatória. **Opinião do autor:** DAX Studio e Tabular Editor 2 deveriam ser
instalados junto com o Desktop, no primeiro dia. Elas são a diferença entre "usar Power BI"
e "trabalhar com Power BI".

### 3.1 DAX Studio (grátis, código aberto)

Para escrever consultas DAX, medir tempo de execução, ver o plano de consulta, exportar
dados e rodar o **VertiPaq Analyzer** (que mostra o tamanho de cada coluna do modelo).

```powershell
winget install --exact --id DaxStudio.DaxStudio
```

Alternativa: baixar de `https://daxstudio.org`.

Verificação: abra o Power BI Desktop com um arquivo, depois abra o DAX Studio — ele deve
listar a instância local em *PBI / SSDT Model*. Se não listar, o Desktop não está aberto
com um arquivo carregado.

Uso em [`22-desempenho.md`](22-desempenho.md).

### 3.2 Tabular Editor 2 (grátis, código aberto)

Edita o modelo semântico diretamente: criar 40 medidas de uma vez, mover pastas, aplicar
formatação em massa, rodar **Best Practice Analyzer** (analisador de boas práticas),
e trabalhar com o formato de pasta compatível com PBIP.

Baixe de `https://github.com/TabularEditor/TabularEditor/releases` (versão portátil ou
instalador). Ele aparece na guia **Ferramentas Externas** do Desktop automaticamente.

> **Tabular Editor 3** é o produto comercial (edições Desktop, Business e Enterprise,
> por usuário, mensal ou anual com 17% de desconto — a página de preços consultada em
> 14/08/2026 não renderizou os valores; consulte `tabulareditor.com/pricing`).
> **A versão 2 continua gratuita, mantida e compatível** com o formato de pasta da 3.

### 3.3 Bravo for Power BI (grátis)

Analisa o modelo, formata DAX (usa o mesmo motor do DAX Formatter) e **gera uma tabela de
datas completa** com um clique — o que resolve o erro nº 1 de iniciante.

```
https://bravo.bi
```

### 3.4 ALM Toolkit (grátis)

Compara dois modelos e mescla diferenças (*schema diff*). Indispensável para promover
mudanças entre ambientes sem republicar tudo. `http://alm-toolkit.com`.

### 3.5 Onde as Ferramentas Externas ficam registradas

O Desktop lê arquivos `.pbitool.json` de:

```
C:\Program Files (x86)\Common Files\Microsoft Shared\Power BI Desktop\External Tools\
```

Se uma ferramenta não aparece na guia **Ferramentas Externas**, é aqui que se olha. Você
pode registrar as suas (por exemplo, um script PowerShell) criando um `.pbitool.json`.

---

## 4. macOS

**Não existe Power BI Desktop nativo para macOS.** Não é um bug de documentação; é uma
decisão de arquitetura (o Desktop hospeda o motor Analysis Services, que é Windows).

### 4.1 Caminho recomendado: Parallels Desktop + Windows 11 ARM (Apple Silicon)

**Passo 1** — Instale o Parallels Desktop (`https://www.parallels.com`). Versão paga,
assinatura anual.

**Passo 2** — Na criação da VM, escolha *Instalar Windows 11* — o Parallels baixa a
imagem ARM oficial.

**Passo 3** — Dentro do Windows, siga a §2 deste manual normalmente. O Desktop é x64 e roda
por **emulação** no Windows ARM; para cargas típicas de aprendizado e uso profissional
comum, o desempenho é adequado.

**Passo 4** — Verificação (no PowerShell da VM):

```powershell
[System.Environment]::Is64BitOperatingSystem
$env:PROCESSOR_ARCHITECTURE
```

```
# esperado em Windows 11 ARM:
True
ARM64
```

**Requisito documentado:** em **Windows on ARM**, o Power BI Desktop exige a atualização
cumulativa **2025-09 (KB5065789)**. Sem ela, sintomas variados de renderização e
inicialização. Rode o Windows Update **antes** de instalar o Desktop.

**Dimensionamento sugerido da VM:** 8 GB de RAM dedicados (mínimo 6), 4 vCPU, 80 GB de disco.

### 4.2 Alternativas em macOS

| Opção | Notas |
|---|---|
| VMware Fusion | Gratuito para uso pessoal desde 2024; suporte ARM funcional |
| UTM / QEMU | Grátis, mais trabalhoso, desempenho inferior |
| Boot Camp | **Só Macs Intel.** Não existe em Apple Silicon |
| Windows 365 Cloud PC | Sem VM local; **suportado oficialmente**; custo mensal |
| Só o Service no navegador | Ver §0.1 |

### 4.3 O que **não** fazer no macOS

- Wine/CrossOver: funciona parcialmente e quebra a cada atualização mensal.
- Confiar em "Power BI para Mac" de terceiros: são outras ferramentas de BI, não Power BI.

---

## 5. Linux

**Não existe Power BI Desktop para Linux**, e não há roadmap anunciado (14/08/2026).
As opções são as mesmas do macOS, sem Parallels:

### 5.1 KVM/QEMU com virt-manager (Debian/Ubuntu)

```bash
sudo apt update
sudo apt install -y qemu-kvm libvirt-daemon-system libvirt-clients bridge-utils virt-manager ovmf
```

*O que faz: instala o hipervisor KVM, os utilitários de gerenciamento e o firmware UEFI
(necessário para Windows 11).*

```bash
sudo systemctl enable --now libvirtd
sudo usermod -aG libvirt,kvm "$USER"
```

*O que faz: habilita o serviço e adiciona seu usuário aos grupos — **é preciso sair e
entrar na sessão** para o grupo valer.*

Verificação:

```bash
kvm-ok
```

```
# esperado:
INFO: /dev/kvm exists
KVM acceleration can be used
```

**Se aparecer `KVM acceleration can NOT be used`:** a virtualização está desligada na BIOS
(procure por *Intel VT-x*, *AMD-V* ou *SVM Mode*).

Windows 11 na VM exige **TPM 2.0 e Secure Boot**: no `virt-manager`, use firmware
**UEFI (OVMF)** e adicione um dispositivo TPM emulado (`swtpm`):

```bash
sudo apt install -y swtpm swtpm-tools
```

Fedora/RHEL:

```bash
sudo dnf install -y @virtualization virt-manager swtpm edk2-ovmf
sudo systemctl enable --now libvirtd
```

### 5.2 VirtualBox (mais simples, desempenho inferior)

```bash
sudo apt install -y virtualbox virtualbox-ext-pack
```

Funciona, mas o Windows 11 em VirtualBox costuma exigir contornos de TPM e a experiência
gráfica é pior. **Recomendação:** KVM em Linux, sempre que possível.

### 5.3 O que fazer no Linux **sem** VM

Boa parte do trabalho de dados **não** precisa do Desktop:

- **Power BI Service** no navegador (modelagem, medidas, TMDL na web, relatórios);
- **preparar os dados** com Python/DuckDB/SQL e entregar Parquet ou tabelas prontas
  (é aliás a melhor prática — ver [`13-power-query-e-m.md`](13-power-query-e-m.md));
- **editar TMDL/PBIP** em qualquer editor de texto: é tudo texto, e o Git funciona igual;
- **automatizar** com a API REST do Power BI e com XMLA via `pyadomd`/`semantic-link`.

**Este curso foi escrito assim**: o [`07-projeto-modelo/`](07-projeto-modelo/README.md)
gera os dados e o modelo em TMDL no Linux, e a etapa final (abrir no Desktop) fica
documentada como passo do usuário.

---

## 6. WSL2 — o mal-entendido

**WSL2 não roda o Power BI Desktop.** WSL2 é Linux dentro do Windows; o Desktop é uma
aplicação Windows. Se você está no Windows, instale o Desktop no Windows, ponto.

WSL2 **é** útil ao lado do Power BI, para:

- rodar Python/dbt/DuckDB que preparam os dados;
- rodar PostgreSQL/MySQL locais como fonte de estudo;
- usar Git com ferramentas Unix.

```powershell
wsl --install -d Ubuntu-24.04
```

*O que faz: instala o WSL2 com Ubuntu 24.04.*

```powershell
wsl --status
```

```
# esperado (trecho):
Versão padrão: 2
```

**Como o Power BI (Windows) enxerga um banco dentro do WSL2:** use `localhost` com a porta
publicada (WSL2 faz encaminhamento automático de `localhost` para o Windows). Se falhar,
descubra o IP do WSL com `hostname -I` dentro do Ubuntu e use esse IP.

---

## 7. On-premises data gateway (quando os dados não estão na nuvem)

Se o seu relatório publicado precisa atualizar a partir de um SQL Server que está na
sua empresa, alguém precisa instalar o **gateway**. Ele é o único componente do Power BI
que costuma exigir um servidor.

### 7.1 Qual modo instalar

| Modo | Quem usa | Limitações |
|---|---|---|
| **Standard (padrão / empresa)** | ★ Produção | Exige direitos de administrador e **conta corporativa**; atende vários usuários e vários serviços (Power BI, Power Apps, Power Automate, Azure Analysis Services) |
| **Personal (pessoal)** | Teste individual | **Só Power BI**, só atualização de importação, só o usuário que instalou. Não compartilha |

**Regra prática:** em produção, **sempre o Standard**. O modo pessoal cria um ponto único
de falha amarrado à máquina de uma pessoa — quando essa pessoa sai da empresa, todos os
relatórios param.

### 7.2 Instalação (Standard)

**Passo 1** — Baixe em `https://powerbi.microsoft.com/downloads/` → *On-premises data
gateway*. A Microsoft publica versões **mensais**; a de julho/2026 estava disponível em
14/08/2026.

**Passo 2** — Execute como administrador, escolha *On-premises data gateway (recommended)*.

**Passo 3** — Entre com a conta corporativa e **registre um novo gateway**. Guarde a
**chave de recuperação** num cofre de senhas: sem ela, o gateway não pode ser
restaurado noutra máquina.

**Passo 4** — Verificação:

```powershell
Get-Service -Name "PBIEgwService" | Select-Object Name, Status, StartType
```

*O que faz: mostra o estado do serviço Windows do gateway.*

```
# esperado:
Name          Status  StartType
----          ------  ---------
PBIEgwService Running Automatic
```

**Passo 5** — No Power BI Service: **Configurações → Gerenciar conexões e gateways** —
o gateway deve aparecer como **Online**.

### 7.3 Onde instalar o gateway (isto importa mais do que parece)

- **Não** instale na estação de trabalho do analista.
- Instale num **servidor sempre ligado**, próximo (em rede) da fonte de dados.
- Dimensione com folga: o gateway **descomprime e recomprime** dados durante a
  atualização; CPU e RAM importam. Ponto de partida: 8 vCPU / 16 GB.
- **Cluster de gateway** (dois ou mais nós) para alta disponibilidade — configure desde
  o começo; migrar depois dá trabalho.
- Portas de saída: TCP 443, 5671, 5672 e 9350–9354 para o Azure Service Bus. O gateway
  faz **conexões de saída**; não é preciso abrir porta de entrada no firewall.

---

## 8. PATH, variáveis de ambiente e permissões

### 8.1 O Power BI Desktop e o PATH

Diferente de ferramentas de linha de comando, **o Power BI Desktop não precisa estar no
PATH** para uso normal. Mas você vai querer chamá-lo por script:

```powershell
# Descobrir o executável (instalação .exe)
$pbi = Join-Path (Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Microsoft Power BI Desktop").InstallLocation "bin\PBIDesktop.exe"
$pbi
```

Adicionar ao PATH do usuário, de forma permanente:

```powershell
[Environment]::SetEnvironmentVariable(
  "Path",
  [Environment]::GetEnvironmentVariable("Path","User") + ";C:\Program Files\Microsoft Power BI Desktop\bin",
  "User")
```

*O que faz: acrescenta a pasta do executável ao PATH do usuário atual.*

> **Por que "não pegou"?** Variáveis de ambiente são lidas pelo processo **quando ele
> inicia**. Um terminal aberto antes da alteração continua com o valor antigo. Feche e
> reabra o terminal (e, para o Explorer e apps gráficos, faça logoff/logon). Isso vale
> para todo sistema operacional e é a dúvida mais frequente de quem começa.

Conferir:

```powershell
$env:Path -split ';' | Select-String "Power BI"
```

### 8.2 Variáveis e pastas que importam

| Caminho | O que guarda | Pode apagar? |
|---|---|---|
| `%LOCALAPPDATA%\Microsoft\Power BI Desktop\` | Cache, logs, configurações do usuário | Sim, com o Desktop fechado |
| `%LOCALAPPDATA%\Microsoft\Power BI Desktop\AnalysisServicesWorkspaces\` | **Espaço de trabalho do motor AS** — pode ocupar dezenas de GB | Sim, com o Desktop fechado |
| `%LOCALAPPDATA%\Microsoft\Power BI Desktop Store App\` | Idem, para a versão da Store | Sim |
| `%APPDATA%\Microsoft\Power BI Desktop\` | Credenciais e configurações persistentes | Cuidado: apaga credenciais salvas |
| `%USERPROFILE%\Documents\Power BI Desktop\Custom Connectors\` | Conectores `.mez` personalizados | Só se você souber o que são |

**Mudar a pasta de trabalho do motor** (útil quando `C:` é pequeno):
**Arquivo → Opções e configurações → Opções → Global → Dados carregados** →
*Local do diretório de dados*.

### 8.3 Permissões — o que exige admin e o que não

| Ação | Exige admin? |
|---|---|
| Instalar pela Microsoft Store | **Não** |
| Instalar pelo `.exe` ou winget | **Sim** |
| Instalar o gateway (Standard) | **Sim** |
| Instalar DAX Studio (instalador por usuário) | Não |
| Instalar Tabular Editor 2 portátil | Não |
| Registrar ferramenta externa em `Program Files` | Sim |

**Se sua TI não te dá admin** — situação comuníssima: use a **Store** para o Desktop e as
**versões portáteis** de DAX Studio e Tabular Editor 2, extraídas em
`%LOCALAPPDATA%\Programs\`. Você não precisa de admin para nada disso.

**Por que evitar instalar em pasta com permissão restrita:** o Desktop grava cache,
`AnalysisServicesWorkspaces` e logs constantemente; instalar num caminho onde o usuário
não tem escrita gera falhas intermitentes e difíceis de diagnosticar (arquivo que não
salva, atualização que trava em 99%).

---

## 9. Contas: a parte que mais barra o iniciante

### 9.1 O problema

O **Power BI Service não aceita contas pessoais** (`@gmail.com`, `@outlook.com`,
`@hotmail.com`, `@yahoo.com`). O cadastro exige uma conta de **organização** no
Microsoft Entra ID (antigo Azure Active Directory). Erro literal esperado:

```
That looks like a personal email address. Enter your work email address so we can
connect you with others in your company. And don't worry. We won't share your address
with anyone.
```

### 9.2 As saídas, em ordem de praticidade

1. **Use o e-mail do trabalho.** Se a empresa tem Microsoft 365, você provavelmente já
   consegue entrar em `app.powerbi.com` e obter a licença **Free** sozinho — a menos que o
   administrador tenha bloqueado a auto-inscrição.
2. **Microsoft 365 Developer Program.** Fornece um locatário de desenvolvimento com
   licenças. As regras de elegibilidade mudaram em 2024–2025 e hoje exigem, em geral,
   vínculo com o Visual Studio Enterprise/Professional — confira as condições atuais antes
   de contar com isso.
3. **Avaliação do Microsoft 365 Business Standard** (1 mês, ~25 usuários). Costuma pedir
   cartão de crédito para validação; **cancele antes do fim** se não quiser cobrança.
4. **Locatário próprio com domínio barato.** Registre um domínio (~R$ 40–60/ano),
   crie um locatário do Microsoft 365 e atribua a si mesmo a licença **Fabric (Free)**.
   É o que muitos profissionais fazem para ter laboratório permanente. Ver
   [`80-custos-e-licencas.md`](80-custos-e-licencas.md).

### 9.3 O que a conta **Free** permite

- Criar modelos e relatórios no **Meu workspace**;
- Consumir conteúdo hospedado em capacidade **F64 ou maior** (como *Viewer*);
- **Não** permite compartilhar de forma privada com outra pessoa (a única forma de
  compartilhamento sem licença paga é *Publicar na Web*, que torna o relatório **público
  na internet** — leia [`24-seguranca-e-governanca.md`](24-seguranca-e-governanca.md)
  antes de sequer pensar nisso).

---

## 10. Rede corporativa: proxy, certificado e firewall

### 10.1 Sintoma

Instalação vai bem, mas o login falha, os conectores não conectam, ou o erro literal
aparece:

```
Unable to connect. We encountered an error while trying to connect.
```
```
The underlying connection was closed: Could not establish trust relationship for the SSL/TLS secure channel.
```

### 10.2 Proxy

O Power BI Desktop usa a **configuração de proxy do Windows** (WinINET/WinHTTP), não uma
configuração própria. Verifique e configure:

```powershell
netsh winhttp show proxy
```

```
# esperado numa rede sem proxy:
Configurações de proxy WinHTTP atuais:  Acesso direto (sem servidor proxy).
```

Importar do Internet Explorer/Edge:

```powershell
netsh winhttp import proxy source=ie
```

Definir manualmente:

```powershell
netsh winhttp set proxy proxy-server="http=proxy.empresa.com:8080;https=proxy.empresa.com:8080" bypass-list="*.empresa.local;<local>"
```

*O que faz: configura o proxy para os componentes que usam WinHTTP e isenta os hosts internos.*

Para o **.NET** (usado por partes do Desktop), pode ser necessário editar o
`PBIDesktop.exe.config` na pasta de instalação, adicionando `<defaultProxy useDefaultCredentials="true" />`
em `<system.net>`. Faça backup do arquivo antes.

### 10.3 Certificado interno (inspeção TLS)

Redes com inspeção de TLS substituem o certificado do servidor por um emitido pela CA
interna. Se essa CA não estiver confiável na máquina, tudo quebra.

```powershell
# Importar a CA interna no repositório de Autoridades de Certificação Raiz Confiáveis
Import-Certificate -FilePath "C:\temp\CA-Empresa.cer" -CertStoreLocation Cert:\LocalMachine\Root
```

Verificação:

```powershell
Get-ChildItem Cert:\LocalMachine\Root | Where-Object Subject -like "*Empresa*"
```

### 10.4 Endereços que precisam estar liberados

Peça à segurança a liberação de (lista essencial; a completa está na documentação de
"Power BI URLs"):

```
*.powerbi.com          *.analysis.windows.net
*.pbidedicated.windows.net    *.fabric.microsoft.com
login.microsoftonline.com     *.msftauth.net
*.servicebus.windows.net      (portas 443, 5671, 5672, 9350-9354 — gateway)
*.blob.core.windows.net       *.dfs.fabric.microsoft.com
```

**Erro típico de firewall no gateway:** o serviço instala, mas fica *Offline* no portal.
Quase sempre são as portas do Service Bus bloqueadas. Contorno documentado: forçar o
gateway a usar **apenas HTTPS (443)** nas configurações do gateway — mais compatível,
um pouco mais lento.

---

## 11. Convivência de versões

| Combinação | Suportado? |
|---|---|
| Desktop mensal + Desktop for Report Server | **Sim**, lado a lado |
| Desktop `.exe` + Desktop da Store | **Não** (documentado) |
| Desktop `.msi` (obsoleto) + Store | **Não** (documentado) |
| Duas versões mensais diferentes | Não |
| Tabular Editor 2 + Tabular Editor 3 | Sim |

**Como voltar a uma versão anterior:** a Microsoft mantém um arquivo de builds mensais
(*Power BI Desktop monthly update archive*). Cuidado com a regra que quebra times:

> **Um arquivo salvo numa versão nova NÃO abre numa versão anterior.** E se você abrir um
> arquivo mais novo numa versão antiga e salvar, perde o que depende dos recursos novos.

**Consequência prática para equipes:** padronize a versão do Desktop de todo o time e
atualize todo mundo junto. É o motivo pelo qual muitas empresas usam o `.exe` com
`DISABLE_UPDATE_NOTIFICATION=1` em vez da Store com atualização automática.

**Aviso com prazo (documentado em julho/2026):** a partir de **outubro/2026**, usuários com
Power BI Desktop de **março/2026 ou anterior** deixam de conseguir salvar e compartilhar
arquivos no OneDrive e SharePoint (o seletor de arquivos antigo será desativado). Atualize.

---

## 12. Reprodutibilidade

Power BI não tem `package.json` nem `requirements.txt`. O que existe:

| Artefato | O que fixa | Onde |
|---|---|---|
| **PBIP + TMDL** | O modelo e o relatório como **texto versionável** | Ver [`25-ciclo-de-vida-e-devops.md`](25-ciclo-de-vida-e-devops.md) |
| Script de provisionamento (winget/Chocolatey) | As ferramentas da estação | Exemplo abaixo |
| `.pbit` (template) | Estrutura sem os dados | Arquivo → Exportar → Modelo do Power BI |
| Parâmetros do Power Query | Servidor/base por ambiente | [`13-power-query-e-m.md`](13-power-query-e-m.md) |

Script de provisionamento de estação (salve como `setup-bi.ps1`, execute como admin):

```powershell
# setup-bi.ps1 — provisiona uma estação de trabalho de BI
$ErrorActionPreference = "Stop"

$pacotes = @(
    "Microsoft.PowerBI",                 # Power BI Desktop
    "Microsoft.EdgeWebView2Runtime",     # runtime de renderização
    "DaxStudio.DaxStudio",               # análise e depuração de DAX
    "Microsoft.PowerBIReportBuilder",    # relatórios paginados
    "Git.Git",                           # versionamento
    "Microsoft.VisualStudioCode"         # edição de TMDL/PBIP
)

foreach ($p in $pacotes) {
    Write-Host "==> Instalando $p"
    winget install --exact --id $p --silent --accept-package-agreements --accept-source-agreements
}

Write-Host "`n==> Verificacao final"
winget list --id Microsoft.PowerBI
git --version
code --version
```

Verificação esperada ao final: três blocos de saída, sem erro. **Não executado nesta
máquina** (ambiente Linux) — trate como roteiro, não como comprovação.

---

## 13. Atualizar com segurança, e voltar atrás

### Atualizar

```powershell
# Store: automático. Forçar:
#   Store > Biblioteca > Obter atualizações

# winget:
winget upgrade --id Microsoft.PowerBI

# .exe: baixe a nova versão e instale por cima (não precisa desinstalar)
```

### Antes de atualizar, em ambiente profissional

1. **Faça backup dos `.pbix`/PBIP** — ou melhor, garanta que estão em Git.
2. Leia o *change log* e o *feature summary* do mês. Recursos em *preview* podem ser
   ligados por padrão e mudar comportamento.
3. Atualize **uma máquina primeiro**, abra os 3 relatórios mais críticos, e só então
   atualize o time.

### Voltar atrás

1. Desinstale a versão atual (§14).
2. Baixe a build desejada do *Power BI Desktop monthly update archive*.
3. **Lembre-se:** arquivos salvos na versão nova podem não abrir. Restaure o `.pbix` do
   backup, não o salvo pela versão nova.

### Desligar o aviso de atualização (empresas)

```powershell
New-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Microsoft Power BI Desktop" `
  -Name "DisableUpdateNotification" -Value 1 -PropertyType DWORD -Force
```

*Reinicie a máquina para valer.*

---

## 14. Desinstalar por completo

Desinstalar pelo painel de controle **deixa vários GB para trás**. O procedimento completo:

**Passo 1 — Remover o programa:**

```powershell
# Store:
Get-AppxPackage -Name "Microsoft.MicrosoftPowerBIDesktop" | Remove-AppxPackage

# .exe:
& "C:\Program Files\Microsoft Power BI Desktop\PBIDesktopSetup_x64.exe" -uninstall -quiet

# winget:
winget uninstall --id Microsoft.PowerBI
```

**Passo 2 — Apagar caches e configurações** (com o Desktop fechado):

```powershell
$alvos = @(
  "$env:LOCALAPPDATA\Microsoft\Power BI Desktop",
  "$env:LOCALAPPDATA\Microsoft\Power BI Desktop Store App",
  "$env:APPDATA\Microsoft\Power BI Desktop",
  "$env:LOCALAPPDATA\Temp\Power BI Desktop"
)
foreach ($a in $alvos) {
  if (Test-Path $a) { Write-Host "Removendo $a"; Remove-Item $a -Recurse -Force }
}
```

> **Atenção:** isso apaga **credenciais salvas de fontes de dados** e as configurações
> globais. É exatamente o que se quer numa desinstalação limpa, e exatamente o que você
> não quer fazer por engano.

**Passo 3 — Verificar sobras:**

```powershell
Get-ChildItem "$env:LOCALAPPDATA\Microsoft" -Filter "*Power BI*" -Directory
Get-Process -Name "msmdsrv","PBIDesktop" -ErrorAction SilentlyContinue
```

```
# esperado: nenhuma saída em ambos
```

**Se `msmdsrv` continuar rodando:** é o motor Analysis Services órfão de uma sessão
travada. `Stop-Process -Name msmdsrv -Force` e então repita o passo 2.

**Passo 4 — Gateway** (se instalado): Painel de Controle → *On-premises data gateway* →
Desinstalar. Depois remova `C:\Program Files\On-premises data gateway` e
`%LOCALAPPDATA%\Microsoft\On-premises data gateway`. **Antes disso, remova o gateway no
portal** (Configurações → Gerenciar conexões e gateways), senão ele fica órfão lá.

---

## 15. Requisitos reais de recursos (não os do papel)

| Recurso | Mínimo oficial | Realidade |
|---|---|---|
| RAM | 2 GB | 8 GB para sobreviver, **16 GB para trabalhar**, 32 GB para modelos grandes |
| Disco | ~1 GB | 20 GB livres: cache + `AnalysisServicesWorkspaces` + `.pbix` + temporários |
| CPU | 1 GHz x64 | Núcleos ajudam na atualização (paralelismo de consultas) e na compressão |
| Rede | — | A publicação envia o modelo inteiro; num `.pbix` de 500 MB e link de 10 Mbps, ~7 min |
| Licença | — | Desktop grátis; **compartilhar exige Pro/PPU/capacidade** |
| Cartão de crédito | — | **Não exigido** para o Desktop nem para a conta Fabric Free |

**Sintoma clássico de pouca RAM:** o Desktop fica lento e "engasga" ao trocar de página;
o Gerenciador de Tarefas mostra `msmdsrv.exe` com vários GB. Não é bug — é o modelo em
memória. Ver [`21-vertipaq-por-dentro.md`](21-vertipaq-por-dentro.md).

---

## 16. Solução de problemas — erros literais

| Mensagem literal | Causa provável | Correção |
|---|---|---|
| `Microsoft Edge can't read and write to its data directory` | WebView2 ausente/quebrado, ou execução sob conta de sistema | Reinstale o WebView2 Runtime (§2.5). **Nunca** execute o Desktop como `SYSTEM` — não é suportado |
| `We weren't able to restore the saved database to the model` | Versão do Desktop mais antiga que o arquivo, ou cache corrompido | Atualize para a versão mais recente; se persistir, apague `AnalysisServicesWorkspaces` com o Desktop fechado |
| `Installer hash does not match` (winget) | Manifesto do winget desatualizado após republicação do instalador | Use a Store (§2.1) ou `--ignore-security-hash` se confiar na origem |
| `That looks like a personal email address…` | Tentativa de criar conta do Service com e-mail pessoal | Use conta corporativa/escolar (§9) |
| `The underlying connection was closed: Could not establish trust relationship for the SSL/TLS secure channel` | Certificado interno de inspeção TLS não confiável | Importe a CA da empresa em `Cert:\LocalMachine\Root` (§10.3) |
| `Unable to connect. We encountered an error while trying to connect.` | Proxy/firewall, ou credencial errada na fonte | `netsh winhttp show proxy` (§10.2); depois Opções → Configurações da fonte de dados → Editar permissões |
| `The 'Microsoft.Mashup.OleDb.1' provider is not registered on the local machine` | Instalação parcial ou corrompida do mecanismo Mashup | Reparar: `PBIDesktopSetup_x64.exe -repair` |
| `This file was created by a newer version of Power BI Desktop and might not open correctly` | Arquivo salvo em build mais nova | Atualize o Desktop. **Não salve** por cima nesta versão antiga, ou perde metadados |
| `Não é possível instalar` / a Store não abre | Store bloqueada por política de grupo | Use o `.exe` (§2.2), ou peça à TI a implantação por Intune (§2.4) |
| Janela com grandes áreas pretas, texto borrado | Escala de exibição do Windows > 100% / bug de renderização | Windows: buscar "borrado" → *Permitir que o Windows corrija aplicativos desfocados*; e volte a escala para 100% |
| Diálogos que não fecham, botão fora da tela | Resolução abaixo do mínimo (1440×900) | Aumente a resolução; abaixo do mínimo **não é suportado** |
| Gateway aparece **Offline** no portal | Portas do Service Bus (5671, 5672, 9350–9354) bloqueadas | Libere as portas ou configure o gateway para usar só HTTPS (443) (§10.4) |

### Onde estão os logs

```
%LOCALAPPDATA%\Microsoft\Power BI Desktop\Traces\
%LOCALAPPDATA%\Microsoft\Power BI Desktop\FrownLogs\
```

O Desktop tem um caminho embutido: **Ajuda → Enviar um sorriso/carranca** (*Send a frown*),
que empacota os logs. Antes de abrir chamado, colete isso.

---

## 17. Checklist "ambiente pronto"

Rode/confira uma linha por vez. Se todas passarem, siga para [`04-como-comecar.md`](04-como-comecar.md).

```powershell
# 1. Windows 64 bits
[System.Environment]::Is64BitOperatingSystem            # esperado: True

# 2. Versão do Windows (>= 10)
(Get-CimInstance Win32_OperatingSystem).Caption         # esperado: Windows 10/11 ...

# 3. .NET Framework >= 4.7.2 (Release >= 461808)
(Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\NET Framework Setup\NDP\v4\Full").Release

# 4. Power BI Desktop instalado (Store)
Get-AppxPackage -Name "Microsoft.MicrosoftPowerBIDesktop" | Select Name,Version
#    ou (.exe)
(Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Microsoft Power BI Desktop").InstallLocation

# 5. Memória total (>= 8 GB recomendável)
[math]::Round((Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory/1GB,1)

# 6. Espaço livre em C: (>= 20 GB)
[math]::Round((Get-PSDrive C).Free/1GB,1)

# 7. Resolução (>= 1440x900)
Add-Type -AssemblyName System.Windows.Forms
[System.Windows.Forms.Screen]::PrimaryScreen.Bounds

# 8. Proxy
netsh winhttp show proxy
```

E, dentro do Power BI Desktop:

- [ ] **Ajuda → Sobre** mostra uma versão de 2026.
- [ ] **Arquivo → Opções → Global → Dados carregados**: *Detecção automática de data/hora*
      **desmarcada** (ver [`75-armadilhas.md`](75-armadilhas.md) nº 3).
- [ ] **Arquivo → Opções → Recursos de visualização**: você viu o que está em *preview*.
- [ ] Guia **Ferramentas Externas** mostra DAX Studio e Tabular Editor (se instalados).
- [ ] Login feito (canto superior direito mostra seu nome), se você tem conta.

---

## 18. Autoteste

1. Cite os quatro métodos de instalação no Windows e diga qual **não** exige admin.
2. Por que a versão de 32 bits não é mais uma opção?
3. Qual é a resolução mínima suportada, e o que acontece se você usar menos?
4. Você tem um MacBook M3. Descreva o caminho recomendado e a atualização do Windows que
   é pré-requisito documentado.
5. Explique em uma frase por que WSL2 não resolve o problema de rodar o Desktop no Linux.
6. Qual a diferença entre gateway *Standard* e *Personal*, e por que o Personal é
   perigoso em produção?
7. Você mudou o PATH e o comando continua não sendo encontrado. Por quê?
8. Depois de desinstalar pelo painel de controle, que pastas ainda ocupam disco?
9. O que acontece se você abrir, na versão de março, um `.pbix` salvo na versão de julho?
10. O gateway aparece "Offline" no portal, mas o serviço está "Running". Qual a primeira
    hipótese?

---

**Próximo:** [`04-como-comecar.md`](04-como-comecar.md) — do ambiente pronto ao primeiro
relatório publicado.

---

*Fontes consultadas em 14/08/2026: [Microsoft Learn — Download Power BI Desktop](https://learn.microsoft.com/en-us/power-bi/fundamentals/desktop-get-the-desktop) (métodos, requisitos mínimos, parâmetros de linha de comando, extração de MSI com WiX, virtualização, WebView2, conta de sistema); [Microsoft Learn — What's new, julho/2026](https://learn.microsoft.com/en-us/power-bi/fundamentals/whats-new) (aviso de outubro/2026 sobre o seletor de arquivos); [Microsoft Learn — Change log do Power BI Desktop](https://learn.microsoft.com/en-us/power-bi/fundamentals/desktop-change-log); [Microsoft Learn — Instalar o on-premises data gateway](https://learn.microsoft.com/en-us/data-integration/gateway/service-gateway-install); [winget.run — Microsoft.PowerBI](https://winget.run/pkg/Microsoft/PowerBI); [Tabular Editor — pricing](https://tabulareditor.com/pricing).*
