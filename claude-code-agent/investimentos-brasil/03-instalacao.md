# 03 · Instalação — deixando o ambiente pronto para investir

**Nível: iniciante** · *Pesquisado na web e testado em 20/08/2026*

> **Nota sobre este arquivo.** Aqui "instalar" tem dois sentidos, e os dois são cobertos:
> **(a)** o ambiente *financeiro* — abrir e configurar as contas e os acessos sem os
> quais você não consegue comprar nada; e **(b)** o ambiente *técnico* — Python e
> planilha, para rodar o [07-projeto-modelo](07-projeto-modelo/) e fazer suas próprias
> contas em vez de acreditar nas dos outros. Nenhum dos dois custa dinheiro.

---

## 0. Alternativa sem instalar nada — comece hoje

Se você quer aplicar **hoje** e resolver o resto depois, existe caminho:

| Quero | Sem instalar nada |
|---|---|
| Aplicar os R$ 6.000 agora | O **app do banco que você já usa**. Todo banco grande vende CDB de liquidez diária e fundo DI. Rende menos que o ótimo, mas rende ~13,9% a.a. em vez de 8,3% da poupança. Migre depois. |
| Simular quanto rende | [Simulador oficial do Tesouro Direto](https://www.tesourodireto.com.br/titulos/calculadora.htm) e a [calculadora do cidadão do BCB](https://www3.bcb.gov.br/CALCIDADAO/publico/exibirFormCorrecaoValores.do) — ambos no navegador, gratuitos |
| Comparar produtos | O [07-projeto-modelo](07-projeto-modelo/) roda em qualquer Python online (por exemplo, o console do [Python.org](https://www.python.org/shell/)) sem instalar nada |
| Estudar antes de decidir | [edu.b3.com.br](https://edu.b3.com.br) e os [cursos da CVM](https://conteudo.cvm.gov.br/menu/investidor/educacao/cursos.html) — gratuitos, no navegador |

**Recomendação profissional:** faça isso. Aplique hoje no CDB de liquidez diária do seu
próprio banco (confira que paga pelo menos 100% do CDI — muitos bancos grandes pagam
80% e isso é ruim), e use os próximos dias para montar o ambiente definitivo. Dinheiro
parado em conta corrente perde 1,1% ao mês de poder de compra em juro não ganho.
A pressa aqui é justificada; a pressa em escolher produto complicado não é.

---

## 1. Visão geral do que será instalado

```mermaid
flowchart LR
    subgraph Financeiro["Ambiente financeiro (obrigatório)"]
        A["Conta bancária<br/>+ Pix"] --> B["Conta em corretora<br/>ou banco de investimentos"]
        B --> C["Adesão ao<br/>Tesouro Direto"]
        B --> D["Área do Investidor<br/>B3 (conferência)"]
        A --> E["gov.br nível<br/>prata/ouro"]
        E --> F["Registrato / BCB<br/>(o que existe no seu CPF)"]
    end
    subgraph Tecnico["Ambiente técnico (opcional, recomendado)"]
        G["Python 3.10+"] --> H["07-projeto-modelo"]
        I["LibreOffice Calc<br/>ou Google Sheets"] --> J["Suas próprias contas"]
    end
```

| Componente | Obrigatório? | Custo | Tempo |
|---|---|---|---|
| Conta em corretora / banco de investimentos | **sim** | R$ 0 | 10–30 min (aprovação em até 2 dias úteis) |
| Adesão ao Tesouro Direto | sim, para títulos públicos | R$ 0 | 2 min, dentro da corretora |
| Conta gov.br nível prata ou ouro | não, mas muito útil | R$ 0 | 10 min |
| Área do Investidor da B3 | não, mas recomendada | R$ 0 | 5 min |
| Registrato (Banco Central) | não | R$ 0 | 5 min |
| Python 3.10+ | só para o projeto-modelo | R$ 0 | 5–15 min |
| Planilha | não | R$ 0 (LibreOffice/Sheets) | 5 min |

**Requisitos de hardware/rede:** qualquer celular Android 8+ ou iOS 15+, ou navegador
atualizado em qualquer computador. Consumo de dados desprezível. Não exige cartão de
crédito em lugar nenhum. Não exige valor mínimo de depósito nas corretoras listadas
abaixo.

---

## 2. Escolha da corretora — decida antes de instalar

Em 2026 **corretagem zero virou o padrão** no varejo brasileiro. Segundo levantamentos
de mercado de 2026, operam com corretagem zero para renda variável, entre outras:
Ágora, Banco do Brasil, C6 Bank, Clear, CM Capital, Inter, Íon (Itaú), Nubank, Rico e
Toro/Santander. Com o preço igualado, a decisão passou a ser **catálogo, plataforma e
conflito de interesse**.

### Critérios que realmente importam

| Critério | Como verificar | Por que importa |
|---|---|---|
| **Autorização do BCB/CVM** | Consulte em [bcb.gov.br](https://www.bcb.gov.br/estabilidadefinanceira/encontreinstituicao) e no [cadastro da CVM](https://sistemas.cvm.gov.br/) | Instituição não autorizada = seu dinheiro não tem nenhuma proteção legal |
| **Custódia de renda variável na B3** | Todo ativo em bolsa fica na **B3 em seu CPF**, não na corretora | Se a corretora quebrar, suas ações/FIIs continuam seus |
| **Cobra custódia no Tesouro Direto?** | A B3 cobra 0,20% a.a.; a corretora pode cobrar **taxa adicional** | Reportagens de 2026 indicam que Rico e BTG repassam a taxa da B3; algumas corretoras zeram a própria. Confira na tabela de tarifas antes de abrir |
| **Catálogo de renda fixa de terceiros** | Veja quantos emissores de CDB/LCI/LCA aparecem | Banco que só vende o CDB dele mesmo não tem concorrência interna, e paga menos |
| **Modelo de remuneração do assessor** | Pergunte, por escrito, quanto ele ganha no produto | Assessor é vendedor remunerado por comissão (Res. CVM 178/2023). Não é consultor. Isso não é crime, mas muda tudo |
| **Interface e suporte** | Teste antes de mandar valor grande | Você vai usar isso por anos |

### Recomendação honesta (opinião profissional, não consenso)

- **Para começar com R$ 6.000 e simplicidade:** o banco digital que você já usa
  (Nubank, Inter, C6) resolve. Menos atrito, você não abandona por preguiça.
- **Para ter o melhor catálogo de renda fixa e taxa competitiva:** uma corretora
  grande com prateleira de terceiros (XP, BTG, Rico, Genial, Órama, Toro).
- **O ganho de trocar de corretora é de segunda ordem** comparado ao ganho de sair da
  poupança/conta corrente. Não use a escolha da corretora como desculpa para adiar.
- **Duas contas é uma prática comum e boa:** uma no banco digital (reserva com liquidez)
  e uma na corretora (o resto). Também dilui risco operacional.

---

## 3. Instalação do ambiente financeiro, passo a passo

### 3.1 Abrir conta em corretora

**Passo 1 — baixe o aplicativo oficial.**

| Sistema | Como |
|---|---|
| **Android** | Google Play Store → busque o nome da corretora → confira o **desenvolvedor** (deve ser a instituição) e o número de downloads. Aplicativo clonado é vetor comum de golpe |
| **iOS (iPhone/iPad)** | App Store → mesma conferência |
| **Windows / macOS / Linux** | Todas as principais funcionam **pelo navegador**, sem instalar nada. Plataformas de trading dedicadas (Profit, MetaTrader) são para operação ativa e você **não precisa delas** |

Verificação imediata:
```
Abra o app. A tela inicial deve exibir o nome da instituição e um aviso
de que ela é autorizada a funcionar pelo Banco Central / CVM.
```
Se o app pedir para você instalar um APK de fora da loja, **desinstale e denuncie**.

**Passo 2 — cadastro.** Você vai fornecer CPF, nome completo, nome da mãe, data de
nascimento, endereço, profissão, renda mensal e patrimônio declarado.

> **Sobre declarar renda e patrimônio:** é exigência regulatória (suitability,
> Resolução CVM 30/2021), não curiosidade comercial. Declare a verdade — divergência
> grosseira trava a conta em análise de compliance.

**Passo 3 — foto do documento + selfie (prova de vida).** Use luz natural, sem óculos,
sem chapéu.

**Passo 4 — questionário de perfil de investidor (API/suitability).**
Obrigatório por regulação. Ele classifica você em conservador, moderado ou arrojado.

> **Opinião profissional:** o questionário mede muito mal o que se propõe a medir —
> ele pergunta o que você *acha* que faria numa queda, e quase todo mundo erra a
> própria resposta. Trate-o como formalidade. O que define de fato a sua alocação é o
> **prazo do objetivo**, não o resultado do teste ([ver 24-carteira](24-carteira-e-alocacao.md)).
> Um perfil "arrojado" não te obriga a nada; ele só libera produtos.

**Passo 5 — aguarde a aprovação.** De minutos a 2 dias úteis.

**Verificação:**
```
Conta aprovada = você consegue ver o número da sua conta e um saldo de R$ 0,00,
e a corretora informa os dados para transferência (chave Pix ou dados bancários
EM SEU PRÓPRIO NOME ou no CNPJ da corretora).
```
Se a conta de destino estiver no nome de **uma pessoa física qualquer**, é golpe. Pare.

**Passo 6 — ative a autenticação em dois fatores (2FA).**
Menu de segurança → 2FA por aplicativo autenticador (Google Authenticator, Authy,
Aegis no Android). Prefira **app autenticador a SMS** — SMS é vulnerável a troca de
chip (SIM swap), que é o golpe mais comum contra investidores no Brasil.

**Verificação:** saia da conta e entre de novo. Deve pedir o código de 6 dígitos.

**Passo 7 — transfira um valor pequeno primeiro.** R$ 10 por Pix. Confirme que
apareceu no saldo. **Só depois** mande os R$ 6.000. Este passo já evitou muito prejuízo.

### 3.2 Aderir ao Tesouro Direto

O Tesouro Direto é um **programa do Tesouro Nacional operado com a B3**; você compra
sempre através de uma instituição habilitada ("agente de custódia"), não direto do governo.

1. No app da corretora, procure **Tesouro Direto** → *Aderir* / *Habilitar*.
2. Aceite o termo de adesão.
3. A adesão é processada pela B3, normalmente no mesmo dia.

**Verificação:**
```
A tela de Tesouro Direto passa a exibir a lista de títulos com preço e taxa
(por exemplo: "Tesouro Selic 2031 — SELIC + 0,04% — mínimo R$ 1xx,xx").
Se ainda aparecer "Aderir", a habilitação não concluiu.
```

**Horários que você precisa saber:**

| Operação | Janela |
|---|---|
| Compra e venda com preços do dia | dias úteis, das 9h30 às 18h |
| Fora desse horário e fins de semana | você **pode** enviar ordem, mas ela executa com os preços da próxima abertura |
| **Tesouro Reserva** | 24×7, inclusive fins de semana e feriados (título novo, lançado em 11/05/2026) |
| Liquidação do resgate (Tesouro Selic e demais) | no mesmo dia útil, se solicitado até as 13h (D+0); senão D+1 |

### 3.3 Tesouro Reserva — o caminho mais curto para a reserva de emergência

Lançado em **11/05/2026** pelo Tesouro Nacional, B3 e Banco do Brasil. Características,
segundo o Tesouro e a cobertura de imprensa da época:

| Característica | Tesouro Reserva | Tesouro Selic |
|---|---|---|
| Rendimento | 100% da Selic | Selic + ágio/deságio pequeno |
| Aplicação mínima | **R$ 1,00** | ~R$ 189 (1% de um título, em 05/2026) |
| Negociação | **24×7**, inclusive fim de semana | dias úteis, 9h30–18h |
| Marcação a mercado | **não tem** | tem (oscilação pequena, mas existe) |
| Limite de aplicação | R$ 500 mil por investidor por mês | sem limite prático no varejo |
| Tributação | IR regressivo + IOF até 30 dias | idêntica |
| Disponibilidade em 08/2026 | **inicialmente só pelo Banco do Brasil**; outras instituições em implantação | todas as corretoras |

> **Verifique a disponibilidade antes de contar com ele.** Na data desta pesquisa
> (20/08/2026), o Tesouro Reserva estava disponível pelo Banco do Brasil, com outras
> instituições em fase de adesão. Se a sua corretora ainda não oferece, o
> **Tesouro Selic** faz o mesmo papel com diferença desprezível para R$ 6.000.

### 3.4 Conta gov.br (nível prata ou ouro)

Serve para o **Registrato**, para o **e-CAC** (declaração de IR) e para o Meu INSS.

1. Acesse [gov.br](https://www.gov.br/pt-br) → *Entrar com gov.br* → *Criar conta*.
2. Prefira criar **pelo aplicativo gov.br** com validação facial (reconhecimento pela
   base da CNH ou do TSE) — sai direto no nível **ouro**.
3. Alternativas para subir de nível: internet banking de banco credenciado, ou
   validação por certificado digital.

**Verificação:** entre em [gov.br](https://sso.acesso.gov.br) → *Meus dados* → o
selo deve dizer **Prata** ou **Ouro**. Nível **Bronze não abre** o Registrato.

### 3.5 Registrato (Banco Central) — descubra o que já existe no seu CPF

Relatório gratuito que lista **todas as suas contas, dívidas e chaves Pix** em qualquer
instituição do país. Antes de investir, use-o para achar conta esquecida, dívida
esquecida e relacionamento que você nem sabia que tinha.

1. [registrato.bcb.gov.br](https://registrato.bcb.gov.br) → entre com gov.br.
2. Emita "Relatório de Empréstimos e Financiamentos" e "Relatório de Contas".

**Verificação:** o PDF baixa com seu nome e CPF e a lista de instituições.

### 3.6 Área do Investidor da B3

Substituiu o antigo CEI. Mostra, direto da bolsa, **tudo que está registrado no seu
CPF** em custódia: ações, FIIs, ETFs, Tesouro Direto, e renda fixa privada registrada.

1. [b3.com.br → Área do Investidor](https://www.b3.com.br/pt_br/produtos-e-servicos/central-depositaria/canal-com-investidores/area-do-investidor/).
2. Cadastre-se com CPF e data de nascimento; crie senha; **ative o 2º fator**.

**Verificação:** depois de aplicar, seus títulos devem aparecer lá em até 1 dia útil.

> **Por que isso importa mais do que parece:** é a sua fonte **independente da
> corretora**. Se o que a corretora mostra no app não bate com o que a B3 mostra,
> você tem um problema sério e uma prova documental. Confira uma vez por trimestre.

---

## 4. Instalação do ambiente técnico

Necessário apenas para rodar o [07-projeto-modelo](07-projeto-modelo/) e os exemplos
de código. **Versão mínima: Python 3.10.** Testado em **Python 3.10.12, em 20/08/2026**.
O projeto usa **somente a biblioteca padrão** — nada de `pip install`, nada de
dependência que envelhece.

### 4.1 Linux — família Debian/Ubuntu

```bash
sudo apt update && sudo apt install -y python3 python3-venv
```
Instala o interpretador e o módulo de ambientes virtuais.

```bash
python3 --version
# esperado: Python 3.10.x ou superior
```
Se aparecer `Python 3.8.x` ou inferior, a distro está antiga. Use `pyenv` (seção 4.6)
ou o container (seção 4.7). Se aparecer `command not found`, o pacote não instalou —
rode `sudo apt install python3` de novo e leia a mensagem de erro.

### 4.2 Linux — família Fedora/RHEL

```bash
sudo dnf install -y python3
```

```bash
python3 --version
# esperado: Python 3.10.x ou superior
```

### 4.3 macOS

O macOS traz um Python de sistema que **não deve ser usado** para nada (é do sistema
operacional, e mexer nele quebra ferramentas da Apple). Instale o seu:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```
Instala o Homebrew, gerenciador de pacotes do macOS.

```bash
brew install python@3.12
```

```bash
python3 --version
# esperado: Python 3.12.x
```

**Apple Silicon (M1/M2/M3/M4) vs Intel:** o Homebrew instala em `/opt/homebrew` no
Apple Silicon e em `/usr/local` no Intel. Se `python3 --version` continuar mostrando a
versão velha do sistema, o PATH não está pegando o Homebrew:

```bash
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
source ~/.zprofile
```
(no Intel, troque `/opt/homebrew` por `/usr/local`).

### 4.4 Windows — nativo (caminho recomendado para quem só quer rodar o projeto)

```powershell
winget install --id Python.Python.3.12 -e
```
Instala o Python oficial via gerenciador de pacotes do Windows.

**Se preferir o instalador gráfico:** baixe em [python.org/downloads](https://www.python.org/downloads/)
e, na primeira tela, **marque a caixa "Add python.exe to PATH"**. Esquecer essa caixa
é a causa nº 1 de `python não é reconhecido como comando`.

```powershell
python --version
# esperado: Python 3.12.x
```

Se der `Python foi encontrado, mas não está instalado` e abrir a Microsoft Store,
o Windows está usando o *stub*. Desligue em:
*Configurações → Aplicativos → Configurações Avançadas de Aplicativos → Aliases de
execução de aplicativo* → desmarque `python.exe` e `python3.exe`.

### 4.5 Windows — WSL2 (recomendado se você também programa)

```powershell
wsl --install -d Ubuntu
```
Instala o subsistema Linux completo. Reinicie quando pedir e crie usuário e senha.

Depois, dentro do Ubuntu, siga a seção 4.1.

```bash
python3 --version
# esperado: Python 3.10.x ou superior
```

**Qual escolher?** Se o seu objetivo é só rodar o projeto-modelo, o Python nativo do
Windows basta e é mais simples. Se você já usa terminal, WSL2 evita a classe inteira
de problemas de caminho e permissão do Windows.

### 4.6 Conviver com várias versões (`pyenv` / `mise`)

Se você já tem outros projetos Python na máquina, não misture. Instale por versão:

```bash
curl https://pyenv.run | bash
```
Instala o pyenv, gerenciador de versões do Python.

Acrescente ao seu `~/.bashrc` (ou `~/.zshrc`):
```bash
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
```

```bash
exec $SHELL
pyenv install 3.12.5
pyenv local 3.12.5
python --version
# esperado: Python 3.12.5
```

O comando `pyenv local` cria um arquivo `.python-version` na pasta — é o seu
**arquivo de reprodutibilidade**: qualquer pessoa que clonar o projeto pega a mesma
versão.

### 4.7 Container (sem sujar a máquina)

```bash
docker run --rm -it -v "$PWD":/app -w /app python:3.12-slim python carteira.py
```
Roda o projeto num Python descartável, sem instalar nada permanentemente.

### 4.8 Planilha

| Sistema | Comando / caminho | Custo |
|---|---|---|
| Debian/Ubuntu | `sudo apt install -y libreoffice-calc` | R$ 0 |
| Fedora/RHEL | `sudo dnf install -y libreoffice-calc` | R$ 0 |
| macOS | `brew install --cask libreoffice` | R$ 0 |
| Windows | `winget install --id TheDocumentFoundation.LibreOffice -e` | R$ 0 |
| Qualquer um, sem instalar | [Google Sheets](https://sheets.google.com) | R$ 0 (exige conta Google) |

**Verificação:** abra o programa e digite em uma célula:
```
=VF(0,115;10;0;-6000)
```
Deve retornar **R$ 17.819,68** — os R$ 6.000 a 11,5% ao ano por 10 anos. (Em inglês a
função é `=FV(0.115;10;0;-6000)`.) Se retornar erro, o separador decimal do seu
sistema é ponto; troque as vírgulas por pontos.

---

## 5. PATH, variáveis de ambiente e permissões

### 5.1 O PATH e por que "não pegou"

`PATH` é a lista de pastas onde o terminal procura programas. Se o Python foi instalado
mas não está no PATH, o terminal jura que ele não existe.

```bash
echo $PATH
# esperado: uma lista separada por ':' contendo a pasta do python
```
```powershell
$env:PATH -split ';'
# Windows: procure uma linha terminando em \Python312\ e outra em \Python312\Scripts\
```

**Por que a alteração "não pegou":** o terminal lê o arquivo de perfil **uma vez, ao
abrir**. Editar o `.bashrc` com o terminal aberto não muda nada nele. Feche e abra, ou:

| Shell | Arquivo | Recarregar |
|---|---|---|
| bash (Linux) | `~/.bashrc` | `source ~/.bashrc` |
| zsh (macOS padrão) | `~/.zshrc` | `source ~/.zshrc` |
| bash de login (macOS) | `~/.zprofile` | `source ~/.zprofile` |
| PowerShell | `$PROFILE` (`notepad $PROFILE`) | `. $PROFILE` |

### 5.2 Permissões: por que `sudo pip install` é uma armadilha

```bash
sudo pip install alguma-coisa   # NÃO FAÇA ISSO
```

Motivo, sem misticismo: o `pip` como root escreve em `/usr/lib/python3/dist-packages`,
que é território do **gerenciador de pacotes da distro**. Na próxima atualização do
sistema, os dois brigam pelo mesmo arquivo e o resultado é um Python quebrado, às
vezes junto com ferramentas do sistema escritas em Python (no Fedora, o próprio `dnf`).
Desde o Python 3.11, o próprio pip recusa isso com `error: externally-managed-environment`
(PEP 668) — a mensagem de erro é o sistema te protegendo.

O caminho certo, quando você precisar de bibliotecas (o projeto-modelo **não precisa**):

```bash
python3 -m venv .venv && source .venv/bin/activate
```
Cria um ambiente isolado dentro da pasta do projeto. Nada fora dela é tocado.

```bash
which python
# esperado: /caminho/do/projeto/.venv/bin/python
```

No Windows: `.venv\Scripts\Activate.ps1`. Se der
`execução de scripts foi desabilitada neste sistema`, rode uma vez:
```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

### 5.3 Rede corporativa (proxy, certificado interno, firewall)

Se você está numa máquina de empresa:

```bash
export HTTPS_PROXY="http://usuario:senha@proxy.empresa:8080"
export NO_PROXY="localhost,127.0.0.1,::1"
```

Três armadilhas conhecidas:

1. **`no_proxy` malformado quebra clientes locais.** Se `NO_PROXY` não incluir
   `localhost,127.0.0.1`, ferramentas em Python tentam falar com o próprio computador
   através do proxy e falham com erro obscuro.
2. **Certificado interno (TLS interceptado).** Erros do tipo
   `SSL: CERTIFICATE_VERIFY_FAILED` significam que a empresa está inspecionando o
   tráfego. Aponte o Python para o CA da empresa:
   `export REQUESTS_CA_BUNDLE=/caminho/ca-empresa.pem`.
3. **Nunca acesse a corretora pela rede corporativa** se puder evitar. Não é paranoia:
   o tráfego é inspecionado por política, e a política é da empresa, não sua.

### 5.4 Segurança do ambiente financeiro — a parte que substitui "permissões"

Aqui o equivalente de "permissão de arquivo" é o **controle de acesso à sua conta**.
Checklist mínimo, e cada item já foi o ponto de falha de alguém:

- [ ] **2FA por app autenticador** (não SMS) na corretora, no banco e na B3.
- [ ] **Senha única** para financeiro, gerada por gerenciador de senhas (KeePassXC,
      Bitwarden, 1Password). Senha reaproveitada de site vazado é o vetor mais comum.
- [ ] **PIN/biometria** no celular, e o celular com bloqueio automático curto.
- [ ] **Chip com senha (PIN do SIM)** ativado — dificulta o golpe de SIM swap.
- [ ] **Alertas de movimentação** ligados por push e e-mail.
- [ ] **Nunca instale app fora da loja oficial**, nunca autorize acesso remoto
      (AnyDesk, TeamViewer) a pedido de "suporte". Nenhuma corretora liga pedindo isso.
- [ ] **Confira o CNPJ da conta de destino** antes de qualquer transferência.
- [ ] **Não invista por rede Wi-Fi pública** sem VPN.

---

## 6. Reprodutibilidade e "arquivo de versão"

No ambiente técnico:

| Arquivo | Para que serve |
|---|---|
| `.python-version` | fixa a versão do Python (pyenv/mise) |
| `.tool-versions` | equivalente do asdf/mise, para várias ferramentas |
| `Dockerfile` / `python:3.12-slim` | ambiente idêntico em qualquer máquina |

No ambiente financeiro o equivalente da reprodutibilidade é a **trilha documental**:

- Guarde os **informes de rendimentos** (chegam entre fevereiro e março de cada ano).
- Baixe o **extrato da Área do Investidor da B3** a cada trimestre, em PDF.
- Guarde as **notas de negociação** de renda variável — sem elas, o cálculo do imposto
  sobre ganho de capital em ações vira arqueologia.
- Mantenha uma planilha própria com data, valor, produto e emissor de cada aplicação.

Motivo prático: a Receita cruza os dados que os bancos entregam (e-Financeira) com a
sua declaração. Divergência cai em malha fina, e a prova é sua.

---

## 7. Atualizar, migrar e desinstalar

### 7.1 Atualizar

```bash
sudo apt update && sudo apt upgrade python3          # Debian/Ubuntu
brew upgrade python                                  # macOS
winget upgrade --id Python.Python.3.12 -e            # Windows
```

Voltar atrás, se algo quebrar: `pyenv local 3.10.12` fixa de volta a versão antiga.

### 7.2 Migrar de corretora sem vender nada (portabilidade)

Você **não precisa vender** para trocar de corretora. Peça **transferência de custódia**
(STVM, Solicitação de Transferência de Valores Mobiliários):

1. Abra a conta na corretora nova.
2. Peça na **corretora de destino** a transferência; ela puxa da origem.
3. Prazo típico: 2 a 10 dias úteis. Custo: em geral zero nas grandes; confira a tabela.
4. **Guarde o preço médio de compra** dos seus ativos — a corretora nova não recebe
   esse dado de forma confiável, e você precisa dele para calcular imposto.

### 7.3 Desinstalar por completo

**Ambiente técnico:**
```bash
sudo apt remove --purge python3-venv && sudo apt autoremove   # Debian/Ubuntu
brew uninstall python@3.12                                     # macOS
winget uninstall --id Python.Python.3.12 -e                    # Windows
```
Restos que ficam para trás e quase ninguém limpa:
```bash
rm -rf ~/.cache/pip ~/.local/lib/python3.*        # caches e pacotes de usuário
rm -rf ~/.pyenv                                    # se usou pyenv
```
No Windows: `%LOCALAPPDATA%\pip\Cache` e `%APPDATA%\Python`.

**Ambiente financeiro — encerrar conta em corretora:**
1. Zere a posição (venda ou transfira a custódia).
2. Saque o saldo para conta de mesma titularidade.
3. Peça encerramento formal por escrito, pelo canal oficial, e **guarde o protocolo**.
4. Confira na Área do Investidor da B3 que não sobrou custódia no seu CPF.
5. Guarde os informes de rendimento por **5 anos** — prazo de decadência do Fisco.

> Conta zerada e esquecida costuma não gerar custo, mas gera **obrigação declaratória**
> e, em algumas instituições, tarifa de manutenção depois de certo tempo. Encerre formalmente.

---

## 8. Solução de problemas

### 8.1 Ambiente financeiro

| Mensagem / sintoma | Causa provável | Correção |
|---|---|---|
| `Cadastro em análise` por mais de 2 dias úteis | divergência de dados com a Receita, ou selfie recusada | confira nome/mãe/nascimento exatamente como no CPF; refaça a selfie com luz natural |
| `CPF não regularizado` / `CPF suspenso` | pendência na Receita Federal | regularize em [receita.fazenda.gov.br](https://www.gov.br/receitafederal) — costuma ser declaração de IR em atraso |
| `Perfil não compatível com o produto` | o suitability te classificou como conservador e o produto é de risco maior | refaça o questionário com respostas verdadeiras, ou assine o termo de ciência de desenquadramento |
| Pix para a corretora **devolvido** | conta de destino em titularidade diferente (regra antilavagem) | transfira **apenas** de conta no seu próprio CPF |
| `Aderir ao Tesouro Direto` continua aparecendo | adesão ainda em processamento na B3 | aguarde 1 dia útil; se persistir, abra chamado na corretora |
| Ordem no Tesouro fica `Agendada` e não executa | enviada fora do horário (9h30–18h em dia útil) | aguarde a abertura; ou use Tesouro Reserva, que opera 24×7 |
| Valor do Tesouro IPCA+ **caiu** no extrato | marcação a mercado — normal, não é erro | se levar até o vencimento, a taxa contratada é honrada. Ver [12-renda-fixa.md](12-renda-fixa.md) |
| Posição não aparece na Área do Investidor da B3 | atraso de 1 dia útil, ou produto não custodiado na B3 (ex.: fundos, poupança) | aguarde; se for CDB e não aparecer, cobre a corretora **por escrito** |

### 8.2 Ambiente técnico

| Mensagem | Causa provável | Correção |
|---|---|---|
| `command not found: python3` (Linux/macOS) | não instalado, ou fora do PATH | seções 4.1–4.3; depois `echo $PATH` |
| `Python não é reconhecido como um comando interno` (Windows) | instalado sem "Add to PATH" | reinstale marcando a caixa, ou acrescente `%LOCALAPPDATA%\Programs\Python\Python312\` ao PATH |
| `error: externally-managed-environment` | pip tentando escrever no Python do sistema (PEP 668) | use `python3 -m venv .venv` — seção 5.2 |
| `EACCES: permission denied` / `Permission denied` | instalação global sem permissão | **não** resolva com `sudo`; use venv ou `--user` |
| `SSL: CERTIFICATE_VERIFY_FAILED` | proxy corporativo interceptando TLS | `export REQUESTS_CA_BUNDLE=/caminho/ca-empresa.pem` — seção 5.3 |
| `ModuleNotFoundError: No module named 'venv'` (Ubuntu) | Ubuntu separa o venv em outro pacote | `sudo apt install python3-venv` |
| Planilha: `=VF(...)` retorna `#NOME?` | separador/idioma da função | use `=FV(...)` ou troque `;` por `,` conforme o locale |

---

## 9. Checklist "ambiente pronto"

Financeiro:
- [ ] Conta em corretora ou banco de investimentos **aprovada**
- [ ] 2FA por aplicativo autenticador **ativo**
- [ ] Pix de teste de R$ 10 **enviado e confirmado no saldo**
- [ ] Adesão ao Tesouro Direto **concluída** (a lista de títulos aparece com preço)
- [ ] Conta gov.br em nível **prata ou ouro**
- [ ] Relatórios do **Registrato** emitidos e lidos
- [ ] Cadastro na **Área do Investidor da B3** feito, com 2º fator
- [ ] Senha exclusiva e guardada em gerenciador de senhas

Técnico (opcional):
```bash
python3 --version           # esperado: Python 3.10.x ou superior
python3 -c "print(round(6000*1.115**10, 2))"   # esperado: 17819.68
```

Se as duas linhas acima responderam certo e o checklist financeiro está todo marcado,
o ambiente está pronto. Vá para [04-como-comecar.md](04-como-comecar.md).

---

## Autoteste

1. Por que o app da corretora nunca deve ser instalado fora da loja oficial?
2. Qual é a diferença prática entre a garantia de um título público e a de um CDB?
3. O que é a Área do Investidor da B3 e por que conferi-la é diferente de olhar o app
   da corretora?
4. Por que 2FA por SMS é pior que por aplicativo autenticador?
5. O que faz o comando `python3 -m venv .venv` e por que ele é a resposta certa para
   `externally-managed-environment`?
6. Você quer trocar de corretora sem pagar imposto. Qual é o procedimento e qual dado
   você precisa guardar?
7. Sua ordem no Tesouro Direto ficou "agendada" às 20h de uma terça. O que aconteceu?
8. Cite três itens do checklist de segurança que protegem contra SIM swap.

---

**Fontes consultadas em 20/08/2026:** B3 — tarifas do Tesouro Direto (custódia de
0,20% a.a., isenção para até R$ 10 mil em Tesouro Selic) e página da Área do Investidor;
Tesouro Nacional — lançamento do Tesouro Reserva em 11/05/2026 (aplicação mínima de R$ 1,
negociação 24×7, sem marcação a mercado, limite de R$ 500 mil/mês, inicialmente pelo
Banco do Brasil); levantamentos de mercado de 2026 sobre corretoras com corretagem zero;
CVM — Resoluções 30/2021 (suitability) e 178/2023 (assessores). Links em
[95-referencias.md](95-referencias.md).

**Próximo:** [04-como-comecar.md](04-como-comecar.md)
