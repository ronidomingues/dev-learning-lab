# 03 — Manual de instalação

Nível: iniciante · **Data: 13/08/2026** · Versões atuais confirmadas na web nesta data

> **Leia isto antes de tudo.** Se você só quer aprender SQL, **provavelmente não
> precisa instalar nada**: se tem Python, já tem SQLite. Pule para a
> [seção 0](#0-o-caminho-mais-curto-voce-provavelmente-ja-tem-sql) — são dois
> comandos e você está consultando em 30 segundos. Este arquivo é longo porque
> cobre *todos* os caminhos, não porque o caminho seja longo.

**Versões de referência (confirmadas em 13/08/2026):**

| Ferramenta | Versão atual | Mínima aceitável | Evitar |
|---|---|---|---|
| SQLite | **3.53.4** (24/07/2026) | 3.25 (funções de janela) · 3.35 para `RETURNING` · **3.37 para `STRICT`** | < 3.25 |
| PostgreSQL | **18.6** (série 18 lançada em 25/09/2025) | 13 | ≤ 12 (fim de vida) |
| DuckDB | **1.5.5** | 1.0 | pré-1.0 (formato instável) |
| Python | 3.13.x | 3.8 | 2.x (morto desde 2020) |

Testado neste curso em: **Ubuntu 22.04.5 LTS, Python 3.10.12, SQLite 3.37.2
(embutido no Python), DuckDB 1.5.5, em 13/08/2026.** O que **não** foi executado
está marcado com ⚠️ ao longo do texto.

---

## Índice

- [0. O caminho mais curto](#0-o-caminho-mais-curto-voce-provavelmente-ja-tem-sql)
- [1. Sem instalar nada: navegador](#1-sem-instalar-nada-navegador)
- [2. SQLite](#2-sqlite-o-banco-deste-curso)
- [3. Python](#3-python)
- [4. Interface gráfica: DB Browser](#4-interface-grafica-db-browser-for-sqlite)
- [5. DuckDB](#5-duckdb-sql-analitico-sobre-csv-e-parquet)
- [6. PostgreSQL](#6-postgresql-o-padrao-de-mercado)
- [7. Editor e extensões](#7-editor-e-extensoes)
- [8. PATH e variáveis de ambiente](#8-path-e-variaveis-de-ambiente)
- [9. Permissões: quando NÃO usar sudo](#9-permissoes-quando-nao-usar-sudo)
- [10. Rede corporativa e máquina bloqueada](#10-rede-corporativa-e-maquina-bloqueada)
- [11. Conviver com várias versões](#11-conviver-com-varias-versoes)
- [12. Reprodutibilidade](#12-reprodutibilidade)
- [13. Atualizar e voltar atrás](#13-atualizar-e-voltar-atras)
- [14. Desinstalar por completo](#14-desinstalar-por-completo)
- [15. Tabela de erros literais](#15-tabela-de-erros-literais)
- [16. Checklist de ambiente pronto](#16-checklist-de-ambiente-pronto)

---

## 0. O caminho mais curto: você provavelmente já tem SQL

O SQLite vem **embutido na biblioteca padrão do Python** desde 2006. Se há
Python na máquina, há um banco SQL completo nela.

```bash
python3 -c "import sqlite3; print(sqlite3.sqlite_version)"
```

```
# esperado: 3.37.2 (ou qualquer 3.x)
```

Deu um número? **Pronto, o ambiente está instalado.** Teste agora:

```bash
python3 -c "import sqlite3; print(sqlite3.connect(':memory:').execute(\"SELECT 'SQL funcionando', 2+2\").fetchone())"
```

```
# esperado: ('SQL funcionando', 4)
```

**Se a saída for diferente:**

| Saída | Causa | Correção |
|---|---|---|
| `command not found: python3` | Python não instalado ou fora do PATH | [seção 3](#3-python) |
| `No module named sqlite3` | Python compilado sem SQLite (raro; acontece em `pyenv` sem `libsqlite3-dev`) | [seção 3.5](#35-erro-no-module-named-sqlite3) |
| No Windows, `python` abre a Microsoft Store | Alias de app do Windows | [seção 3.3](#33-windows) |

---

## 1. Sem instalar nada: navegador

Ofereço isto **antes** do caminho longo de propósito: é o que evita que alguém
desista no primeiro dia por causa de um instalador.

| Serviço | Endereço | O que é | Roda offline? |
|---|---|---|---|
| **SQLime** | <https://sqlime.org> | SQLite compilado para WebAssembly, roda no seu navegador | Sim, depois de carregar |
| **SQLite Online** | <https://sqliteonline.com> | Idem, com mais recursos e mais anúncios | Parcialmente |
| **DB Fiddle** | <https://www.db-fiddle.com> | PostgreSQL, MySQL, SQLite — no **servidor deles** | Não |
| **DuckDB Shell** | <https://shell.duckdb.org> | DuckDB em WebAssembly | Sim |

**Aviso sério, e leia antes de colar qualquer coisa:** SQLime e o shell do
DuckDB processam de fato no navegador, sem enviar dados ao servidor. O DB
Fiddle **envia**. Mesmo nos que processam localmente, **não cole dado de
produção da sua empresa em serviço web sem autorização formal** — a diferença
entre "a página promete que é local" e "a auditoria aceita isso" é grande, e
quem responde é você. Para dado real, use SQLite local.

Faça o [04-como-comecar.md](04-como-comecar.md) inteiro em um desses se
quiser. Instale depois, com calma.

---

## 2. SQLite: o banco deste curso

O SQLite é um **arquivo**. Não há servidor, não há serviço, não há porta de
rede, não há senha, não há usuário. Um banco é um arquivo `.db`; copiá-lo é
copiar o banco; apagá-lo é apagar o banco.

Isso tem uma consequência prática enorme para quem trabalha em indústria:
**instalar SQLite não é "instalar um banco de dados"** do ponto de vista da
política de TI. É baixar um executável de 2 MB. Peça assim.

### 2.1 O que exatamente instalar

Há duas coisas com o mesmo nome, e confundi-las é a fonte da maioria dos
problemas:

| | O que é | Precisa? |
|---|---|---|
| **biblioteca** `libsqlite3` | O motor. É o que o Python usa | Já vem com o Python |
| **cliente** `sqlite3` | O programa de linha de comando | Opcional, mas conveniente |

Você pode fazer o curso inteiro sem o cliente. Ele só é mais confortável para
explorar um banco.

### 2.2 Linux — família Debian/Ubuntu

```bash
sudo apt update
```
Atualiza a lista de pacotes disponíveis.

```bash
sudo apt install -y sqlite3
```
Instala o cliente de linha de comando.

```bash
sqlite3 --version
# esperado: 3.37.2 2022-01-06 ...   (no Ubuntu 22.04)
#           3.45.x ou superior      (no Ubuntu 24.04)
```

> ⚠️ **Não executado neste ambiente** (a máquina de escrita não tem `sudo`).
> A versão candidata foi confirmada com `apt-cache policy sqlite3`:
> `3.37.2-2ubuntu0.7` no Ubuntu 22.04. O caminho sem `sudo` da
> [seção 2.5](#25-linux-e-macos-sem-privilegio-de-administrador) **foi**
> executado.

**A versão do apt é antiga e isso importa?** O Ubuntu 22.04 entrega 3.37.2,
lançada em janeiro de 2022 — quatro anos e meio atrás. Para este curso, basta:
3.37 já tem funções de janela, CTEs, `STRICT`, `RETURNING` e `FILTER`. Se
precisar de recurso mais novo (`unixepoch()` exige 3.38; `->` para JSON exige
3.38), vá para a [seção 2.5](#25-linux-e-macos-sem-privilegio-de-administrador).

### 2.3 Linux — família Fedora/RHEL/Rocky

```bash
sudo dnf install -y sqlite
```
No Fedora o pacote do cliente chama-se `sqlite` (sem o "3"), e a biblioteca é
`sqlite-libs`. Em RHEL/Rocky/AlmaLinux 9, o mesmo comando.

```bash
sqlite3 --version
# esperado: 3.4x.x
```

> ⚠️ Não executado. Nome do pacote conferido na documentação da distribuição.

### 2.4 Métodos alternativos, e qual escolher

| Método | Quando usar | Prós | Contras |
|---|---|---|---|
| **Gerenciador do sistema** (`apt`, `dnf`, `brew`, `winget`) | Padrão. Comece por aqui | Atualiza junto com o sistema, sem esforço | Versão atrasada 1–4 anos |
| **Binário oficial** (zip do sqlite.org) | Precisa da versão nova, ou não tem `sudo` | Sempre a última versão; um arquivo só | Você atualiza na mão; **veja o problema de glibc abaixo** |
| **Via Python** | Você só quer usar SQL | Zero instalação | Sem cliente interativo |
| **Docker** | Ambiente reprodutível, CI | Isolado e idêntico em toda máquina | Precisa de Docker; atrito para uso diário |
| **Compilar do fonte** | Precisa de opção de compilação específica (FTS5, extensões, ICU) | Controle total | Precisa de compilador; 5–15 min |

**Recomendação:** gerenciador do sistema para quase todo mundo; Python puro se
a máquina é bloqueada; binário oficial se você precisa de SQLite ≥ 3.45.

### 2.5 Linux e macOS sem privilégio de administrador

Este caminho **foi executado** na escrita deste material — inclusive o erro.

```bash
mkdir -p ~/bin && cd ~/bin
curl -sSLO https://sqlite.org/2026/sqlite-tools-linux-x64-3530400.zip
```
Baixa o pacote oficial de ferramentas (~4,3 MB). O nome do arquivo codifica a
versão: `3530400` = 3.53.04. Confira o nome atual em
<https://sqlite.org/download.html> — ele muda a cada versão.

```bash
unzip -o sqlite-tools-linux-x64-3530400.zip
./sqlite3 --version
```

**No Ubuntu 22.04 isso falha, e o erro é este:**

```
./sqlite3: /lib/x86_64-linux-gnu/libm.so.6: version `GLIBC_2.38' not found
```

**Causa:** os binários oficiais do sqlite.org de 2026 são compilados contra
glibc 2.38 (Ubuntu 23.10+, Debian 13+). O Ubuntu 22.04 tem glibc 2.35. Confira
a sua com `ldd --version`.

**Correções, em ordem de preferência:**
1. Use o `sqlite3` do `apt` (3.37.2 basta para tudo neste curso).
2. Use o SQLite do Python (`python3 -c "import sqlite3"`) — é a mesma
   biblioteca, versão da distribuição, sem problema de glibc.
3. Compile do fonte ([seção 2.9](#29-compilar-do-fonte)) — resolve de vez.
4. Use `conda`/`micromamba`: `micromamba install -c conda-forge sqlite` traz
   binário compatível com glibc antigo. ⚠️ Não executado.

Esta é a lição geral: **binário oficial "portátil" não é portátil para trás.**
Vale para SQLite, Node, e quase tudo.

### 2.6 macOS

O macOS **já vem com SQLite** — mas com uma versão antiga e com o cliente
capado pela Apple.

```bash
sqlite3 --version
# no macOS 14/15: 3.43.x  (varia por versão do sistema)
```

Para a versão atual:

```bash
brew install sqlite
```
Instala via Homebrew. **Atenção:** o Homebrew instala como *keg-only*, ou seja,
**não** substitui o `sqlite3` do sistema no PATH. Para usar o novo:

```bash
echo 'export PATH="$(brew --prefix sqlite)/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
sqlite3 --version
# esperado: 3.53.4
```

- **Apple Silicon (M1–M4)**: o Homebrew instala em `/opt/homebrew`.
- **Intel**: instala em `/usr/local`. O `$(brew --prefix sqlite)` acima resolve
  os dois casos sem você precisar saber qual é.

Se não tem Homebrew:
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```
⚠️ Não executado. Instala o Homebrew; pede senha de administrador uma vez.

### 2.7 Windows — nativo

**Caminho recomendado: `winget`** (já vem no Windows 10 21H2+ e no Windows 11).

```powershell
winget install SQLite.SQLite
```

```powershell
sqlite3 --version
# esperado: 3.53.x
```

**Caminho manual** (sem `winget`, ou sem privilégio):

1. Baixe `sqlite-tools-win-x64-3530400.zip` em <https://sqlite.org/download.html>
   (ou `-arm64-` se for um Windows on ARM / Snapdragon).
2. Extraia para `C:\Users\SEU_USUARIO\bin` — **não** em `C:\Program Files`,
   que exige administrador.
3. Acrescente essa pasta ao PATH ([seção 8.3](#83-windows)).
4. Abra um **terminal novo** e teste `sqlite3 --version`.

Não precisa de administrador em nenhum passo.

> ⚠️ Nenhum caminho do Windows foi executado. Os nomes de arquivo foram
> conferidos em <https://sqlite.org/download.html> em 13/08/2026.

### 2.8 Windows — WSL2

**Quando usar WSL2 em vez do Windows nativo?**

| Use WSL2 se | Use Windows nativo se |
|---|---|
| Vai usar Postgres, Docker, ou ferramentas de Linux | Só quer SQLite e Python |
| Vai seguir tutoriais escritos para Linux | Precisa integrar com Excel/Power BI/COM |
| Quer o mesmo ambiente do servidor | O TI não permite virtualização |

**Recomendação:** para *este curso*, Windows nativo basta e é mais simples.
WSL2 vale a pena no dia em que você precisar do PostgreSQL.

```powershell
wsl --install -d Ubuntu-24.04
```
Instala o WSL2 com Ubuntu 24.04. **Exige administrador** e reinicialização.
Depois, dentro do Ubuntu, siga a [seção 2.2](#22-linux--familia-debianubuntu).

⚠️ Não executado.

**Armadilha do WSL2 que pega todo mundo:** um banco SQLite guardado em
`/mnt/c/...` (disco do Windows visto pelo Linux) fica **muito** mais lento e
pode corromper com bloqueio de arquivo. Guarde os bancos em `~/` dentro do
WSL. Se precisa acessar do Windows, use `\\wsl$\Ubuntu-24.04\home\voce\`.

### 2.9 Compilar do fonte

Só se precisar de opções de compilação específicas (FTS5 para busca textual,
extensões carregáveis, ICU para acentuação) ou de contornar o problema de glibc.

```bash
sudo apt install -y build-essential wget
wget https://sqlite.org/2026/sqlite-autoconf-3530400.tar.gz
tar xzf sqlite-autoconf-3530400.tar.gz
cd sqlite-autoconf-3530400
./configure --prefix=$HOME/.local CFLAGS="-DSQLITE_ENABLE_FTS5 -DSQLITE_ENABLE_MATH_FUNCTIONS"
make -j$(nproc)
make install
```
`--prefix=$HOME/.local` instala no seu diretório, sem `sudo` no `make install`.
Leva de 2 a 5 minutos.

```bash
~/.local/bin/sqlite3 --version
# esperado: 3.53.4
```

⚠️ Não executado neste ambiente.

---

## 3. Python

Necessário para rodar o [projeto-modelo](07-projeto-modelo/) e os arquivos
[24-sql-com-python.md](24-sql-com-python.md) e [70-pratica.md](70-pratica.md).

```bash
python3 --version
# esperado: Python 3.8.0 ou superior
```

### 3.1 Linux

Já vem instalado em toda distribuição moderna. Se faltar:

```bash
sudo apt install -y python3 python3-pip python3-venv      # Debian/Ubuntu
sudo dnf install -y python3 python3-pip                    # Fedora/RHEL
```

### 3.2 macOS

O macOS traz um Python antigo e reservado ao sistema. **Não use o do sistema.**

```bash
brew install python@3.13
python3 --version
# esperado: Python 3.13.x
```

### 3.3 Windows

```powershell
winget install Python.Python.3.13
```

Ou pelo instalador de <https://www.python.org/downloads/>. **Duas caixas que
precisam ser marcadas:**
- ☑ *Add python.exe to PATH* — senão nada funciona no terminal;
- ☑ *Install for me only* — não exige administrador.

**Armadilha clássica do Windows:** digitar `python` abre a Microsoft Store.
Isso é um "alias de execução de aplicativo" que a Microsoft instala. Desligue:
*Configurações → Aplicativos → Configurações avançadas de aplicativo → Aliases
de execução de aplicativo* → desmarque `python.exe` e `python3.exe`.

### 3.4 Bibliotecas opcionais

Para este curso, **nenhuma é obrigatória** — o projeto-modelo usa só a
biblioteca padrão. Para o dia a dia depois:

```bash
python3 -m pip install --user pandas duckdb sqlalchemy psycopg[binary]
```
`--user` instala no seu diretório, sem `sudo` — ver [seção 9](#9-permissoes-quando-nao-usar-sudo).

Melhor ainda, num ambiente virtual:

```bash
python3 -m venv .venv
source .venv/bin/activate          # Linux/macOS
.venv\Scripts\Activate.ps1         # Windows PowerShell
pip install pandas duckdb sqlalchemy
```

```bash
python3 -c "import duckdb, pandas; print(duckdb.__version__, pandas.__version__)"
# esperado (13/08/2026): 1.5.5 2.x.x
```
DuckDB 1.5.5 **foi** instalado e testado neste ambiente com
`pip3 install duckdb`.

### 3.5 Erro `No module named sqlite3`

Acontece quando o Python foi compilado sem a biblioteca de desenvolvimento do
SQLite — típico de `pyenv` em máquina sem `libsqlite3-dev`.

```bash
sudo apt install -y libsqlite3-dev          # Debian/Ubuntu
sudo dnf install -y sqlite-devel            # Fedora/RHEL
pyenv install 3.13.5                        # recompile DEPOIS de instalar
```

---

## 4. Interface gráfica: DB Browser for SQLite

Recomendo para quem nunca usou terminal. É gratuito, open-source (GPLv3 +
MPL 2.0), e roda em Windows, macOS e Linux: <https://sqlitebrowser.org>.

```bash
sudo apt install -y sqlitebrowser          # Debian/Ubuntu
brew install --cask db-browser-for-sqlite  # macOS
winget install DBBrowserForSQLite.DBBrowserForSQLite   # Windows
```

⚠️ Não executado.

**O que ele resolve:** ver as tabelas, clicar, filtrar, exportar CSV, e uma
aba "Executar SQL" para as consultas. É um bom apoio, não um substituto — o
objetivo aqui é você escrever SQL, não clicar.

**Alternativas**, todas gratuitas: **DBeaver Community** (multi-banco, pesado,
excelente), **Beekeeper Studio Community**, **Azure Data Studio** (bom para
SQL Server), **pgAdmin 4** (PostgreSQL).

---

## 5. DuckDB: SQL analítico sobre CSV e Parquet

Se você é engenheiro químico e tem CSVs grandes exportados do historiador,
**esta é provavelmente a ferramenta mais útil deste arquivo inteiro.** DuckDB
consulta CSV e Parquet **direto do disco, com SQL, sem carregar nada em
lugar nenhum**.

### 5.1 Instalação

```bash
# Linux e macOS — o jeito oficial
curl https://install.duckdb.org | sh
```

```bash
# macOS com Homebrew
brew install duckdb

# Windows
winget install DuckDB.cli
```

```powershell
# Windows PowerShell, script oficial (marcado como beta pelos autores)
powershell -NoExit iex (iwr "https://install.duckdb.org/install.ps1").Content
```

**Verificação:**
```bash
duckdb --version
# esperado: v1.5.5 (ou superior)
```

⚠️ Nenhum destes foi executado. O que **foi** executado e verificado é o
caminho via Python, abaixo — que dispensa instalar o CLI:

```bash
pip3 install duckdb
python3 -c "import duckdb; print(duckdb.__version__)"
# saída real neste ambiente: 1.5.5
```

**Sobre `curl ... | sh`:** você está executando um script vindo da internet.
É o método oficial e a fonte é confiável, mas se quiser conferir antes:
`curl https://install.duckdb.org -o inst.sh && less inst.sh && sh inst.sh`.
Em rede corporativa isso costuma ser bloqueado; use `pip install duckdb`.

### 5.2 Verificação com dado de verdade

```bash
python3 -c "
import duckdb
print(duckdb.sql('SELECT 42 AS resposta, version() AS v'))"
```
```
┌──────────┬─────────┐
│ resposta │    v    │
│  int32   │ varchar │
├──────────┼─────────┤
│       42 │ v1.5.5  │
└──────────┴─────────┘
```

---

## 6. PostgreSQL: o padrão de mercado

**Você não precisa dele para este curso.** Instale quando quiser um banco de
verdade, com servidor, usuários e concorrência — ou quando o trabalho exigir.
Há um curso inteiro de PostgreSQL nesta pasta:
[`../postgresql/00-MAPA.md`](../postgresql/00-MAPA.md).

### 6.1 O caminho mais fácil: Docker

```bash
docker run --name pg -e POSTGRES_PASSWORD=segredo -p 5432:5432 -d postgres:18
```
Sobe um PostgreSQL 18 num container. Nada é instalado no sistema; para remover,
`docker rm -f pg`.

```bash
docker exec -it pg psql -U postgres -c "SELECT version();"
# esperado: PostgreSQL 18.x on x86_64-pc-linux-gnu ...
```

### 6.2 Instalação nativa

```bash
# Debian/Ubuntu — repositório oficial do PostgreSQL, não o da distro
sudo apt install -y postgresql-common
sudo /usr/share/postgresql-common/pgdg/apt.postgresql.org.sh
sudo apt install -y postgresql-18 postgresql-client-18
```

```bash
# Fedora/RHEL
sudo dnf install -y postgresql-server postgresql
sudo postgresql-setup --initdb
sudo systemctl enable --now postgresql
```

```bash
# macOS — recomendo o Postgres.app, que é um clique
brew install postgresql@18
brew services start postgresql@18
```

```powershell
# Windows
winget install PostgreSQL.PostgreSQL.18
```

```bash
psql --version
# esperado: psql (PostgreSQL) 18.6
```

⚠️ Não executado. **Erro conhecido nesta máquina** ao chamar `psql` sem ter
servidor instalado, e que confunde muita gente:

```
Warning: No existing cluster is suitable as a default target.
Error: You must install at least one postgresql-client-<version> package
```

Isso é o *wrapper* do Debian dizendo que existe o pacote `postgresql-client`
genérico mas nenhum cliente versionado. Instale `postgresql-client-18`.

### 6.3 Nuvem gratuita, sem instalar

| Serviço | Camada gratuita (13/08/2026) | Cartão? |
|---|---|---|
| **Neon** | 0,5 GB, projeto que hiberna | Não |
| **Supabase** | 500 MB, pausa após 1 semana inativa | Não |
| **Aiven** | Plano gratuito de 1 mês | Sim |

Ver [80-custos-e-licencas.md](80-custos-e-licencas.md). E **não coloque dado
de produção da empresa em nuvem gratuita** — o mesmo aviso da seção 1.

---

## 7. Editor e extensões

Qualquer editor de texto serve. Para conforto real:

**VS Code** (gratuito) + estas extensões:

| Extensão | Publicador | Para quê |
|---|---|---|
| **SQLTools** | Matheus Teixeira | Conectar e rodar consultas dentro do editor |
| **SQLTools SQLite** | Matheus Teixeira | Driver de SQLite para o acima |
| **SQLite Viewer** | Florian Klampfer | Abrir `.db` e ver as tabelas |
| **Python** | Microsoft | Rodar o projeto-modelo |

```bash
code --install-extension mtxr.sqltools
code --install-extension mtxr.sqltools-driver-sqlite
```
⚠️ Não executado. Nomes conferidos no Marketplace.

**Formatação:** coloque isto em `settings.json` para o VS Code não brigar com
a indentação do SQL:

```json
{
  "[sql]": {
    "editor.tabSize": 2,
    "editor.insertSpaces": true
  }
}
```

---

## 8. PATH e variáveis de ambiente

**O que é o PATH:** uma lista de pastas que o terminal percorre, em ordem, ao
procurar um programa que você digitou. Se o programa não está em nenhuma delas,
você recebe `command not found` — mesmo que o arquivo exista no disco.

**Por que a mudança "não pegou":** cada terminal lê o PATH **uma vez, ao
abrir**. Editar o arquivo de perfil não muda o terminal que já está aberto.
Feche e abra, ou rode `source ~/.bashrc`.

### 8.1 Ver o PATH atual

```bash
echo $PATH                       # Linux e macOS
```
```powershell
$env:PATH -split ';'             # Windows PowerShell
```

### 8.2 Acrescentar uma pasta — Linux e macOS

Descubra qual é o seu shell:
```bash
echo $SHELL
# /bin/bash  → edite ~/.bashrc
# /bin/zsh   → edite ~/.zshrc   (padrão do macOS desde 2019)
```

```bash
echo 'export PATH="$HOME/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```
A primeira linha acrescenta permanentemente; a segunda aplica ao terminal atual.

```bash
which sqlite3
# esperado: /home/voce/bin/sqlite3  (ou /usr/bin/sqlite3)
```

**Ordem importa:** `$HOME/bin:$PATH` põe a sua pasta **antes**, e ela vence.
`$PATH:$HOME/bin` põe **depois**, e o do sistema vence. É assim que se escolhe
qual `sqlite3` roda quando há dois.

### 8.3 Windows

Interface gráfica: tecla ⊞ → digite "variáveis de ambiente" → *Editar as
variáveis de ambiente do sistema* → **Variáveis de Ambiente** → em *Variáveis
de usuário*, selecione `Path` → **Editar** → **Novo** → cole a pasta → OK em
todas as janelas → **abra um terminal novo**.

Por linha de comando, sem administrador:
```powershell
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";C:\Users\$env:USERNAME\bin", "User")
```
⚠️ Não executado. Altera o PATH **do usuário** (não do sistema) — por isso não
exige administrador. Abra um terminal novo depois.

**Verificação:**
```powershell
where.exe sqlite3
# esperado: C:\Users\voce\bin\sqlite3.exe
```

---

## 9. Permissões: quando NÃO usar sudo

Regra: **`sudo` só para o gerenciador de pacotes do sistema.** Para tudo mais,
instale no seu diretório de usuário.

### 9.1 O caso do `pip`

```bash
sudo pip install pandas          # ERRADO
```

Três razões concretas, não estéticas:

1. **Conflito com o gerenciador do sistema.** O `apt` também gerencia arquivos
   em `/usr/lib/python3/dist-packages`. O `pip` com `sudo` escreve por cima. Na
   próxima atualização do sistema os dois brigam, e ferramentas do próprio
   sistema operacional que dependem de Python param de funcionar. Já quebrou o
   `apt` de muita gente.
2. **Um `setup.py` malicioso roda como root.** Instalar um pacote executa código.
   Com `sudo`, esse código tem acesso à máquina inteira.
3. **É irreversível na prática.** Você perde o rastro do que instalou onde.

**Certo:**
```bash
python3 -m pip install --user pandas       # no seu diretório
# ou, melhor:
python3 -m venv .venv && source .venv/bin/activate && pip install pandas
```

Em distribuições novas (Ubuntu 24.04+, Fedora 38+) o `pip` global é bloqueado
de propósito, com este erro:

```
error: externally-managed-environment
```

Isso **não é um bug**: é a PEP 668 protegendo o Python do sistema. A resposta
certa é criar um ambiente virtual. A resposta errada, que a internet vai
sugerir, é `--break-system-packages` — e o nome da opção deveria ser aviso
suficiente.

### 9.2 Permissão no arquivo do banco SQLite

O SQLite precisa de permissão de escrita **na pasta**, não só no arquivo:
ele cria `banco.db-wal` e `banco.db-shm` ao lado.

```
Error: attempt to write a readonly database
```

Cause típica: o `.db` está numa pasta sem permissão, ou foi criado por outro
usuário, ou está em disco montado somente-leitura.

```bash
ls -l planta.db
# -rw-rw-r-- 1 voce voce 28618752 ago 13 13:06 planta.db
chmod u+w planta.db          # dá escrita ao dono
ls -ld .                     # confira também a PASTA
```

---

## 10. Rede corporativa e máquina bloqueada

O cenário real de quem trabalha em indústria. Em ordem do que tentar:

### 10.1 Proxy

```bash
export HTTP_PROXY=http://usuario:senha@proxy.empresa.com:8080
export HTTPS_PROXY=$HTTP_PROXY
export NO_PROXY=localhost,127.0.0.1,.empresa.com
```
⚠️ Senha em variável de ambiente aparece em `ps` e no histórico do shell. Se
puder, use proxy sem autenticação ou autenticação integrada.

Para o `pip`, permanentemente:
```bash
python3 -m pip config set global.proxy http://proxy.empresa.com:8080
```

Para o `apt`, crie `/etc/apt/apt.conf.d/95proxy`:
```
Acquire::http::Proxy "http://proxy.empresa.com:8080";
Acquire::https::Proxy "http://proxy.empresa.com:8080";
```

### 10.2 Certificado interno (inspeção TLS)

Erro típico:
```
SSL: CERTIFICATE_VERIFY_FAILED
```
A empresa intercepta HTTPS com um certificado próprio. Peça o `.crt` ao TI:

```bash
sudo cp empresa-ca.crt /usr/local/share/ca-certificates/
sudo update-ca-certificates
export PIP_CERT=/etc/ssl/certs/ca-certificates.crt
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
```

**Nunca** use `pip --trusted-host` ou `curl -k` como solução permanente: isso
desliga a verificação e passa a aceitar qualquer certificado, inclusive o de
um atacante. Como diagnóstico momentâneo, tudo bem; como configuração, não.

### 10.3 Registry espelhado

Muitas empresas mantêm espelho interno (Artifactory, Nexus):
```bash
python3 -m pip config set global.index-url https://nexus.empresa.com/repository/pypi/simple
```

### 10.4 Quando nada é permitido

Ordem prática:
1. **Python já instalado** → você já tem SQLite. Fim.
2. **Excel com Power Query** → sabe fazer `JOIN` e `GROUP BY`, e é aprovado em
   toda empresa. Não é SQL, mas é o mesmo raciocínio.
3. **O banco corporativo que você já acessa** (Oracle, SQL Server via o ERP)
   → peça acesso *somente-leitura* a uma réplica. É um pedido comum, e é como
   quase todo engenheiro de processo aprende SQL na prática.
4. **SQLime no navegador** → para estudar, com dado fictício.
5. **Sua máquina pessoal em casa** → para praticar com dado sintético (o
   [projeto-modelo](07-projeto-modelo/) existe exatamente para isso).

---

## 11. Conviver com várias versões

**SQLite:** não é problema. O binário é autocontido; ter três versões em três
pastas é normal. Quem manda é a ordem do PATH.

```bash
which -a sqlite3        # lista TODOS os sqlite3 do PATH, na ordem
```

Atenção a um detalhe que confunde: o `sqlite3` do CLI e o do Python podem ser
**versões diferentes** na mesma máquina, porque são binários diferentes.

```bash
sqlite3 --version                                    # a do CLI
python3 -c "import sqlite3; print(sqlite3.sqlite_version)"   # a do Python
```

**Python:** use um gerenciador de versões.

| Ferramenta | Plataforma | Comando |
|---|---|---|
| `pyenv` | Linux/macOS | `pyenv install 3.13.5 && pyenv local 3.13.5` |
| `mise` | Linux/macOS | `mise use python@3.13` |
| `uv` | todas | `uv python install 3.13` |
| `conda`/`micromamba` | todas | `micromamba create -n sql python=3.13` |

**PostgreSQL:** em Debian/Ubuntu, várias versões convivem por padrão
(`pg_lsclusters` lista, `pg_ctlcluster` controla), cada uma numa porta.

---

## 12. Reprodutibilidade

O objetivo: outra pessoa (ou você em seis meses) reproduzir seu ambiente.

**Fixe a versão do Python:**
```bash
echo "3.13.5" > .python-version         # lido por pyenv, mise, uv
```

**Fixe as dependências:**
```bash
pip freeze > requirements.txt
pip install -r requirements.txt
```

**Registre a versão do SQLite dentro do próprio banco.** Este é o truque que
salva auditoria:
```sql
CREATE TABLE meta_ambiente (
    chave TEXT PRIMARY KEY,
    valor TEXT
);
INSERT INTO meta_ambiente VALUES
    ('sqlite_version', sqlite_version()),
    ('criado_em',      datetime('now'));
```

O [projeto-modelo](07-projeto-modelo/) faz exatamente isso na tabela
`carga_log`, incluindo a **semente do gerador** — é o que permite reconstruir
o banco byte a byte.

**Container, quando precisa ser idêntico:**
```dockerfile
FROM python:3.13-slim
RUN apt-get update && apt-get install -y --no-install-recommends sqlite3 \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY . .
CMD ["python3", "scripts/gerar_dados.py"]
```
⚠️ Não construído neste ambiente (sem Docker).

---

## 13. Atualizar e voltar atrás

```bash
sudo apt update && sudo apt install --only-upgrade sqlite3    # Debian/Ubuntu
brew upgrade sqlite                                            # macOS
winget upgrade SQLite.SQLite                                   # Windows
pip install --upgrade duckdb                                   # Python
```

**Antes de atualizar qualquer coisa que toque seus bancos: faça backup.**

```bash
sqlite3 planta.db ".backup planta-backup-2026-08-13.db"
```
Este comando faz backup **a quente** (com o banco em uso), de forma
transacionalmente consistente. Copiar o arquivo com `cp` enquanto alguém
escreve pode gerar um arquivo corrompido.

**Voltar atrás:**
```bash
sudo apt install sqlite3=3.37.2-2ubuntu0.7      # versão específica
pip install duckdb==1.4.3                        # versão específica
```

**Compatibilidade de formato de arquivo:** o SQLite mantém compatibilidade de
formato desde 2004 — um banco de 2004 abre na 3.53 e vice-versa (desde que não
use recursos novos). É uma das maiores façanhas de engenharia de software em
uso, e o compromisso público é manter até 2050. O DuckDB **não** tem essa
garantia: bancos anteriores à 1.0 exigem conversão, e é por isso que a tabela
de versões manda evitar pré-1.0.

---

## 14. Desinstalar por completo

```bash
# Debian/Ubuntu — remove pacote E configuração
sudo apt purge sqlite3 && sudo apt autoremove

# Fedora/RHEL
sudo dnf remove sqlite

# macOS
brew uninstall sqlite

# Windows
winget uninstall SQLite.SQLite
```

**O que fica para trás e ninguém lembra:**

| Item | Onde | Como limpar |
|---|---|---|
| Histórico do cliente | `~/.sqlite_history` | `rm ~/.sqlite_history` |
| Configuração do cliente | `~/.sqliterc` | `rm ~/.sqliterc` |
| Linha no PATH | `~/.bashrc`, `~/.zshrc`, PATH do usuário no Windows | edite e remova a linha |
| Binários baixados à mão | `~/bin`, `~/.local/bin` | `rm ~/bin/sqlite3` |
| Cache do pip | `~/.cache/pip` | `pip cache purge` |
| Ambientes virtuais | `.venv` em cada projeto | `rm -rf .venv` |
| **Os seus bancos** | onde você os salvou | `find ~ -name "*.db"` — **confira antes de apagar** |
| Container do Postgres | Docker | `docker rm -f pg && docker volume prune` |

Cuidado com o último: `*.db` também é extensão de outros programas. **Olhe
antes de apagar.**

---

## 15. Tabela de erros literais

| Mensagem | Causa provável | Correção |
|---|---|---|
| `command not found: sqlite3` | Binário fora do PATH, ou não instalado | [Seção 8](#8-path-e-variaveis-de-ambiente). Confirme com `which -a sqlite3`. Se não instalou, [seção 2](#2-sqlite-o-banco-deste-curso) |
| `'sqlite3' não é reconhecido como um comando interno` | Idem, no Windows | Acrescente a pasta ao PATH e **abra um terminal novo** ([8.3](#83-windows)) |
| ``version `GLIBC_2.38' not found`` | Binário oficial novo em Linux antigo | Use o pacote do `apt`, ou o SQLite do Python, ou compile ([2.5](#25-linux-e-macos-sem-privilegio-de-administrador)). **Erro reproduzido na escrita deste material** |
| `No module named sqlite3` | Python compilado sem SQLite | Instale `libsqlite3-dev` e recompile ([3.5](#35-erro-no-module-named-sqlite3)) |
| `error: externally-managed-environment` | PEP 668: pip global bloqueado | Use `venv` ou `pip install --user` ([9.1](#91-o-caso-do-pip)) |
| `attempt to write a readonly database` | Sem permissão de escrita **na pasta** do `.db` | `chmod u+w` no arquivo **e** na pasta ([9.2](#92-permissao-no-arquivo-do-banco-sqlite)) |
| `database is locked` | Outro processo com transação aberta; ou banco em disco de rede/`/mnt/c` | Feche o outro cliente. Ative WAL: `PRAGMA journal_mode=WAL`. Nunca use SQLite em NFS/SMB |
| `SSL: CERTIFICATE_VERIFY_FAILED` | Inspeção TLS corporativa | Instale o certificado da empresa ([10.2](#102-certificado-interno-inspecao-tls)). Não use `-k` |
| `Could not fetch URL ... Connection timed out` | Proxy não configurado | [Seção 10.1](#101-proxy) |
| `unable to open database file` | Caminho errado, pasta inexistente, ou falta de permissão | Use caminho absoluto; `mkdir -p` na pasta; confira com `ls -ld` |
| `Error: near "STRICT": syntax error` | SQLite < 3.37 | Atualize, ou remova `STRICT` do DDL. `sqlite3 --version` para conferir |
| `no such function: unixepoch` | SQLite < 3.38 | Use `strftime('%s', ts)`. **Confirmado nesta máquina** (3.37.2) |
| `no such table: generate_series` | Extensão não compilada nesta build | Use CTE recursiva. **Confirmado nesta máquina** |
| `Warning: No existing cluster is suitable` (psql) | Cliente Postgres genérico sem cliente versionado | `apt install postgresql-client-18`. **Confirmado nesta máquina** |
| `psql: could not connect to server` | Servidor parado ou porta errada | `sudo systemctl status postgresql`; confira a porta com `pg_lsclusters` |
| `python` abre a Microsoft Store | Alias de execução do Windows | Desligue em *Aliases de execução de aplicativo* ([3.3](#33-windows)) |
| `Permission denied` ao rodar `./sqlite3` | Falta bit de execução | `chmod +x sqlite3` |
| `zsh: no matches found: *.db` | O shell tentou expandir o `*` | Ponha entre aspas: `"*.db"` |

---

## 16. Checklist de ambiente pronto

Rode um comando por linha. Todos precisam responder antes de ir para o
[04-como-comecar.md](04-como-comecar.md).

```bash
python3 --version
```
```bash
python3 -c "import sqlite3; print(sqlite3.sqlite_version)"
```
```bash
python3 -c "import sqlite3; print(sqlite3.connect(':memory:').execute('SELECT 1+1').fetchone())"
```
```bash
cd sql/07-projeto-modelo && python3 scripts/gerar_dados.py
```
```bash
python3 scripts/consultar.py 01
```
```bash
python3 -m unittest discover -s testes
```

Saídas esperadas:

```
Python 3.10.12                       (ou superior)
3.37.2                               (ou superior)
(2,)
Banco criado em .../planta.db  ...  344640 linhas
  bateladas | concluidas | ...  →  78 | 77 | ...
Ran 31 tests in 8.5s  OK
```

**Opcionais** (marque o que se aplica ao seu caminho):

```bash
sqlite3 --version                  # cliente de linha de comando
python3 -c "import duckdb; print(duckdb.__version__)"
psql --version                     # PostgreSQL
code --version                     # VS Code
```

Se os seis obrigatórios passaram, **o ambiente está pronto.**

---

## Autoteste

1. Por que "se você tem Python, já tem SQL"? O que exatamente vem embutido?
2. Qual a diferença entre a *biblioteca* SQLite e o *cliente* `sqlite3`?
3. Você baixou o binário oficial do sqlite.org e ele reclama de `GLIBC_2.38`.
   O que aconteceu, e quais são as quatro saídas?
4. Por que `sudo pip install` é errado? Dê as três razões, não uma.
5. Você mudou o PATH e o comando continua não encontrado. O que faltou?
6. Sua empresa intercepta HTTPS com certificado próprio. Qual é a correção
   certa e qual é a que a internet vai sugerir e você não deve usar?
7. Onde o SQLite deixa lixo depois de desinstalado? Cite três lugares.
8. Por que um banco SQLite em `/mnt/c/` dentro do WSL2 é má ideia?
9. Qual comando faz backup de um banco SQLite **em uso**, e por que `cp` não serve?

---

## Fontes consultadas

Todas em 13/08/2026:

- SQLite — página de downloads e nomes de arquivo: <https://sqlite.org/download.html> (3.53.4, 24/07/2026)
- SQLite — histórico de versões: <https://sqlite.org/changes.html>
- PostgreSQL — notas de versão: <https://www.postgresql.org/docs/release/> (18.6)
- DuckDB — instalação: <https://duckdb.org/install/> e <https://duckdb.org/docs/current/operations_manual/installing_duckdb/install_script>
- DB Browser for SQLite: <https://sqlitebrowser.org>
- PEP 668 (`externally-managed-environment`): <https://peps.python.org/pep-0668/>
- Verificações locais: `apt-cache policy sqlite3` → `3.37.2-2ubuntu0.7`;
  `ldd --version` → glibc 2.35; `pip3 install duckdb` → 1.5.5;
  download e execução do zip oficial do SQLite → erro de glibc reproduzido.

---

*Próximo: [04-como-comecar.md](04-como-comecar.md).*
