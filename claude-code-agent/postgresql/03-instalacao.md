# 03 · Manual de instalação — passo a passo, por sistema operacional

`Nível: iniciante` · `Manual de campo` · `Última atualização: 11/08/2026`

> **Versões de referência** (consultadas em **11/08/2026**):
> - **PostgreSQL 18** é a série estável atual. A 18.0 saiu em **25/09/2025**; a 18.3, em
>   **26/02/2026**. Use a **minor mais recente da série 18** disponível para o seu sistema.
> - **Versão mínima que ainda vale usar:** 14 (a 13 e anteriores estão em fim de vida ou perto).
>   Cada major é suportada por ~5 anos.
> - **Versão a evitar:** qualquer major fora de suporte (a
>   [política de versões](https://www.postgresql.org/support/versioning/) é pública). Não comece
>   um projeto novo em versão antiga.
>
> Onde não confirmei um número exato na data acima, o texto diz isso. Confie sempre na saída de
> `psql --version` e `SELECT version();` da sua máquina.

---

## Leia isto antes

Diferente de muitos softwares, o PostgreSQL tem **três coisas** que você precisa distinguir:

1. **O servidor** (`postgres`) — o programa que guarda os dados e atende conexões.
2. **O cliente** (`psql` e as bibliotecas) — o que você usa para falar com o servidor.
3. **O cluster de dados** — a pasta física onde os dados vivem (`initdb` a cria).

Você pode instalar só o cliente (para conectar a um servidor remoto) ou o conjunto completo. Este
manual instala o conjunto e, quando útil, uma interface gráfica.

### Índice

- [Alternativa sem instalar nada](#alternativa-sem-instalar-nada) ← **comece por aqui se tiver pressa**
- [Linux — Debian/Ubuntu](#linux--debianubuntu)
- [Linux — Fedora/RHEL](#linux--fedorarhelrocky)
- [macOS](#macos)
- [Windows](#windows)
- [Docker](#docker--o-caminho-descartável)
- [Interface gráfica](#interface-gráfica-pgadmin-e-dbeaver)
- [Primeiro acesso e senha](#primeiro-acesso-usuário-e-senha)
- [PATH e variáveis de ambiente](#path-e-variáveis-de-ambiente)
- [Conexão remota e pg_hba.conf](#conexão-remota-e-pg_hbaconf)
- [Convivência de versões](#convivência-de-versões)
- [Reprodutibilidade](#reprodutibilidade)
- [Atualizar e voltar atrás](#atualizar-e-voltar-atrás)
- [Desinstalar por completo](#desinstalar-por-completo)
- [Solução de problemas](#solução-de-problemas--erros-literais)
- [Checklist "ambiente pronto"](#checklist-ambiente-pronto)

---

## Alternativa sem instalar nada

**Comece aqui se você só quer escrever SQL hoje.** Estas opções levam 2 minutos e cobrem todo o
[04-como-comecar.md](04-como-comecar.md) e boa parte do [06-exemplos.md](06-exemplos.md).

| Opção | Link | O que dá | Limite |
|---|---|---|---|
| **Neon** | [neon.com](https://neon.com) | PostgreSQL real na nuvem, camada gratuita permanente | 0,5 GB, escala a zero quando ocioso |
| **Supabase** | [supabase.com](https://supabase.com) | PostgreSQL + interface web, camada gratuita | Projeto pausa após inatividade |
| **DB Fiddle** | [db-fiddle.com](https://www.db-fiddle.com) | Rodar SQL no navegador, escolhendo a versão do PG | Efêmero, sem persistência |
| **pgexercises** | [pgexercises.com](https://pgexercises.com) | Exercícios de SQL com PostgreSQL, no navegador | Só leitura/consulta |
| **Docker** | ver [seção Docker](#docker--o-caminho-descartável) | Servidor local descartável | Precisa de Docker instalado |

**Recomendação:** para aprender SQL, comece no **Neon** (nuvem gratuita permanente) ou no **DB
Fiddle** (zero cadastro) hoje, e instale localmente quando quiser aprender administração.

---

## Linux — Debian/Ubuntu

Testado em Ubuntu 24.04 e 26.04, em 11/08/2026. Há **duas fontes** de pacote:

| Fonte | Versão que entrega | Quando usar |
|---|---|---|
| Repositório da distro (`apt install postgresql`) | A que veio com o Ubuntu (pode estar atrás) | Simplicidade, se a versão servir |
| **Repositório oficial PGDG** | **A mais recente**, todas as majors, extensões | **Recomendado** — controle da versão |

### Método recomendado — repositório oficial PGDG

**Passo 1 — adicionar o repositório com o script oficial:**

```bash
sudo apt install -y postgresql-common
sudo /usr/share/postgresql-common/pgdg/apt.postgresql.org.sh
```
*O que faz:* instala o utilitário de gerência de múltiplas versões e roda o script oficial, que
detecta seu Ubuntu e configura o repositório PGDG com a chave de assinatura correta. O script é
interativo e confirma antes de agir.

```bash
apt-cache policy postgresql-18 | head -3
# esperado: linhas de "Candidato:" apontando para uma versão 18.x do repositório apt.postgresql.org
```

**Passo 2 — instalar o servidor (e o cliente, que vem junto):**

```bash
sudo apt install -y postgresql-18
```
*O que faz:* instala o servidor PostgreSQL 18, o cliente `psql`, e — importante no Debian/Ubuntu —
**cria e inicia automaticamente um cluster de dados** e um serviço `systemd`. Você já sai com um
banco rodando.

```bash
psql --version
# esperado: psql (PostgreSQL) 18.x
sudo systemctl status postgresql --no-pager
# esperado: active (exited)  — o serviço "wrapper" que gerencia os clusters
pg_lsclusters
# esperado: uma linha "18  main  5432  online ..."  ← cluster online na porta 5432
```
*Se `pg_lsclusters` mostrar "down":* `sudo pg_ctlcluster 18 main start`.

> **Peculiaridade Debian/Ubuntu:** ao contrário de outras distros, aqui o pacote **já cria e sobe
> um cluster** com o utilitário `pg_ctlcluster`/`pg_lsclusters`. Os arquivos de configuração ficam
> em `/etc/postgresql/18/main/`, não no diretório de dados. Isso confunde quem seguiu um tutorial
> de outra distro — no Debian/Ubuntu, edite a config em `/etc/postgresql/18/main/`.

### Método manual (deb822), se o script não puder rodar

```bash
sudo apt install -y curl ca-certificates
sudo install -d /usr/share/postgresql-common/pgdg
sudo curl -o /usr/share/postgresql-common/pgdg/apt.postgresql.org.asc --fail \
  https://www.postgresql.org/media/keys/ACCC4CF8.asc

sudo tee /etc/apt/sources.list.d/pgdg.sources > /dev/null <<EOF
Types: deb
URIs: https://apt.postgresql.org/pub/repos/apt
Suites: $(. /etc/os-release && echo "${VERSION_CODENAME}")-pgdg
Components: main
Signed-By: /usr/share/postgresql-common/pgdg/apt.postgresql.org.asc
EOF

sudo apt update && sudo apt install -y postgresql-18
```
> Codinomes suportados na data: `resolute` (26.04), `noble` (24.04), `jammy` (22.04). Se o
> `VERSION_CODENAME` da sua distro derivada não for reconhecido, fixe manualmente um suportado.

### Só o cliente (para conectar a um servidor remoto)

```bash
sudo apt install -y postgresql-client-18
```

---

## Linux — Fedora/RHEL/Rocky

Testado em Fedora 42 e Rocky 9, em 11/08/2026.

```bash
# 1) Repositório oficial PGDG (ajuste a versão do RHEL/Fedora na URL, se necessário)
sudo dnf install -y https://download.postgresql.org/pub/repos/yum/reporpms/EL-9-x86_64/pgdg-redhat-repo-latest.noarch.rpm
# No Fedora: use o repo específico do Fedora, conforme instruções em postgresql.org/download

# 2) Desabilitar o módulo padrão do sistema (senão ele entrega uma versão antiga)
sudo dnf -qy module disable postgresql

# 3) Instalar servidor + cliente
sudo dnf install -y postgresql18-server postgresql18

# 4) AQUI é diferente do Debian: você inicializa o cluster À MÃO
sudo /usr/pgsql-18/bin/postgresql-18-setup initdb
sudo systemctl enable --now postgresql-18
```
*O que faz:* no Fedora/RHEL, o pacote **não** cria o cluster automaticamente. O passo `initdb` o
cria, e o `systemctl enable --now` o inicia e habilita no boot.

```bash
sudo systemctl status postgresql-18 --no-pager
# esperado: active (running)
sudo -u postgres psql -c "SELECT version();"
# esperado: PostgreSQL 18.x on x86_64-...
```
> **SELinux** está ativo no Fedora/RHEL e pode bloquear caminhos de dados customizados. Se você
> mover o diretório de dados, precisará rotular o novo caminho — a tabela de erros cobre isso.

---

## macOS

> Há quatro caminhos; a diferença é ergonomia, não o banco.

| Método | Melhor para | Comando/onde |
|---|---|---|
| **Postgres.app** | Iniciantes; menos atrito | [postgresapp.com](https://postgresapp.com) — baixa um `.app`, clica em "Initialize" |
| **Homebrew** | Quem já usa Homebrew e quer CLI | `brew install postgresql@18` |
| **EDB installer** | Quem quer pgAdmin junto | [postgresql.org/download/macosx](https://www.postgresql.org/download/macosx/) |
| **Docker** | Descartar depois | ver [seção Docker](#docker--o-caminho-descartável) |

### Homebrew (recomendado para quem usa terminal)

```bash
# Instale o Homebrew, se não tiver
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

brew install postgresql@18
brew services start postgresql@18     # inicia agora e no login
```
*O que faz:* instala servidor + cliente e sobe um serviço que reinicia no login.

```bash
psql --version
# esperado: psql (PostgreSQL) 18.x
# No macOS via Homebrew, o superusuário padrão é o SEU usuário, não "postgres":
psql postgres
# esperado: entra no prompt psql, conectado ao banco 'postgres'
```
*Se `psql: command not found`:* o Homebrew de Apple Silicon instala em `/opt/homebrew/bin`;
garanta que está no PATH (ver [PATH](#path-e-variáveis-de-ambiente)). Fórmulas "keg-only" às vezes
exigem `brew link postgresql@18` ou adicionar `$(brew --prefix postgresql@18)/bin` ao PATH.

### Postgres.app (recomendado para iniciantes)

Baixe de [postgresapp.com](https://postgresapp.com), arraste para *Applications*, abra e clique em
**Initialize**. Para ter o `psql` no terminal, siga a instrução do app para adicionar ao PATH:

```bash
sudo mkdir -p /etc/paths.d && echo /Applications/Postgres.app/Contents/Versions/latest/bin \
  | sudo tee /etc/paths.d/postgresapp
# reabra o terminal
psql --version
```

---

## Windows

> **Recomendação:** para *aprender de verdade como é em produção*, use **WSL2** e siga a seção
> [Debian/Ubuntu](#linux--debianubuntu) dentro dele. Para simplicidade em Windows nativo, use o
> **instalador EDB**.

### Instalador EDB (Windows nativo)

1. Baixe de [postgresql.org/download/windows](https://www.postgresql.org/download/windows/) (o
   instalador é da EDB e inclui servidor, `psql`, **pgAdmin** e o Stack Builder).
2. Execute. Anote **a senha do usuário `postgres`** que você definir — você vai precisar dela, e
   recuperá-la depois dá trabalho.
3. Aceite a porta padrão **5432** e o *locale* padrão.
4. Ao final, o **pgAdmin** dá uma interface gráfica; o `psql` fica disponível no *SQL Shell
   (psql)* do menu Iniciar.

```powershell
# No PowerShell, se adicionou o bin ao PATH:
psql --version
# esperado: psql (PostgreSQL) 18.x
```
*Se `psql` não for reconhecido:* o instalador nem sempre põe no PATH. Adicione
`C:\Program Files\PostgreSQL\18\bin` às variáveis de ambiente do sistema, ou use o atalho *SQL
Shell (psql)*.

### WSL2 (recomendado para quem vai levar a sério)

```powershell
wsl --install -d Ubuntu    # como Administrador; reinicie se pedir
```
Depois, dentro do Ubuntu do WSL, siga a seção [Debian/Ubuntu](#linux--debianubuntu). Uma ressalva:
o WSL antigo não usa `systemd` por padrão. Inicie o cluster com
`sudo pg_ctlcluster 18 main start`, ou habilite systemd no `/etc/wsl.conf` (`[boot]\nsystemd=true`).

---

## Docker — o caminho descartável

Se você tem Docker (há um curso em [`../docker`](../docker/00-MAPA.md)), este é o jeito mais
rápido de subir e jogar fora.

```bash
docker run -d --name pg \
  -e POSTGRES_PASSWORD=senha \
  -e POSTGRES_DB=laboratorio \
  -p 127.0.0.1:5432:5432 \
  -v pgdata:/var/lib/postgresql/data \
  postgres:18

# Espere ficar pronto (a imagem reinicia uma vez na primeira inicialização)
until docker exec pg pg_isready -U postgres >/dev/null 2>&1; do sleep 1; done
echo "pronto"

# Entre no psql de dentro do container
docker exec -it pg psql -U postgres -d laboratorio
```
*O que cada parte faz:* `-e POSTGRES_PASSWORD` define a senha do superusuário (**obrigatória** na
imagem oficial); `-p 127.0.0.1:5432:5432` publica só no loopback (não exponha o banco na LAN);
`-v pgdata:/var/lib/postgresql/data` guarda os dados num volume que sobrevive ao container.

> **Sem volume, os dados morrem com o container.** Este é o erro nº 1 de quem usa Postgres no
> Docker. Ver [`../docker/15-armazenamento-e-volumes.md`](../docker/15-armazenamento-e-volumes.md).

---

## Interface gráfica (pgAdmin e DBeaver)

O terminal é o caminho para aprender, mas uma GUI ajuda a visualizar. Duas opções livres:

| Ferramenta | Perfil | Onde |
|---|---|---|
| **pgAdmin 4** | Oficial, focada em PostgreSQL, completa | [pgadmin.org](https://www.pgadmin.org) · vem no instalador EDB |
| **DBeaver** (Community) | Universal (vários bancos), muito usada | [dbeaver.io](https://dbeaver.io) |
| **psql** | Terminal, o que este curso usa | já vem com o servidor |

*Recomendação:* aprenda com o `psql` (é o que estará em todo servidor), e use DBeaver ou pgAdmin
para **visualizar** esquemas e resultados grandes. Não dependa da GUI para o que você deveria
saber fazer no terminal.

---

## Primeiro acesso: usuário e senha

O PostgreSQL cria um superusuário inicial chamado **`postgres`**. Como conectar difere por
sistema:

**Linux (Debian/Ubuntu/Fedora):** a instalação usa autenticação `peer` — o usuário do sistema
operacional `postgres` conecta como o `postgres` do banco, sem senha:

```bash
sudo -u postgres psql
# esperado: o prompt  postgres=#
```

Defina uma senha para poder conectar por rede/senha depois:
```sql
-- dentro do psql:
ALTER USER postgres PASSWORD 'uma-senha-forte';
\q
```

Crie seu próprio usuário e banco (melhor que usar o superusuário para tudo):
```bash
sudo -u postgres createuser --interactive --pwprompt seu_usuario
sudo -u postgres createdb -O seu_usuario meu_primeiro_banco
psql -U seu_usuario -d meu_primeiro_banco -h localhost
```

**macOS (Homebrew):** o superusuário é o **seu** usuário do sistema, não `postgres`:
```bash
psql postgres          # conecta como você mesmo
```

**Windows / Docker:** você definiu a senha do `postgres` na instalação; use-a:
```bash
psql -U postgres -h localhost
```

---

## PATH e variáveis de ambiente

### Conferir se o `psql` está no PATH

```bash
which psql            # Linux/macOS
# esperado: /usr/bin/psql, /opt/homebrew/bin/psql, etc.
```
```powershell
where.exe psql        # Windows
```

### Variáveis que o `psql` e as ferramentas leem

Definir estas evita digitar as mesmas opções toda vez:

| Variável | Para que | Exemplo |
|---|---|---|
| `PGHOST` | Servidor | `localhost` |
| `PGPORT` | Porta | `5432` |
| `PGUSER` | Usuário | `seu_usuario` |
| `PGDATABASE` | Banco padrão | `meu_banco` |
| `PGPASSWORD` | Senha (⚠️ evite — use `.pgpass`) | — |
| `DATABASE_URL` | String de conexão completa (usada por aplicações) | `postgres://usuario:senha@localhost:5432/banco` |

**A forma segura de guardar a senha** é o arquivo `~/.pgpass` (Linux/mac) ou `%APPDATA%\postgresql\pgpass.conf` (Windows):

```bash
echo "localhost:5432:meu_banco:seu_usuario:sua_senha" >> ~/.pgpass
chmod 600 ~/.pgpass     # OBRIGATÓRIO: o psql ignora o arquivo se as permissões forem abertas
```
*Por que `chmod 600`:* o `psql` recusa, por segurança, ler um `.pgpass` que outros usuários possam
ler. Se ele "ignora" sua senha, é quase sempre isto.

> **Nunca use `PGPASSWORD` em scripts versionados** — ela vaza no histórico do shell e na lista de
> processos. Prefira `.pgpass` ou um gerenciador de segredos.

### Por que a mudança de PATH "não pegou"

O arquivo de perfil (`~/.bashrc`, `~/.zshrc`) é lido **uma vez**, quando o shell inicia. Editá-lo
não afeta terminais já abertos. `source ~/.bashrc` relê na sessão atual; ou abra um terminal novo.

---

## Conexão remota e pg_hba.conf

Por padrão, o PostgreSQL só aceita conexões **locais**. Para aceitar de outras máquinas, dois
arquivos importam:

**1. `postgresql.conf`** — em quais interfaces escutar:
```conf
listen_addresses = '*'      # padrão é 'localhost'. '*' = todas as interfaces
```

**2. `pg_hba.conf`** — quem pode conectar, de onde, e como (*Host-Based Authentication*):
```conf
# TYPE  DATABASE  USER      ADDRESS         METHOD
host    all       all       192.168.1.0/24  scram-sha-256
```

Localização (varia por sistema):
```bash
sudo -u postgres psql -c "SHOW config_file;"    # onde está o postgresql.conf
sudo -u postgres psql -c "SHOW hba_file;"       # onde está o pg_hba.conf
```

Depois de editar, **recarregue**:
```bash
sudo -u postgres psql -c "SELECT pg_reload_conf();"
# ou: sudo systemctl reload postgresql
```

> ⚠️ **Segurança:** `listen_addresses = '*'` sem um `pg_hba.conf` restritivo e uma senha forte
> expõe o banco. Um Postgres na internet com senha fraca é comprometido em horas — varreduras
> automatizadas caçam a porta 5432. Detalhes em [20-seguranca.md](20-seguranca.md). Para
> desenvolvimento, mantenha `localhost` e conecte por SSH ou VPN.

O método `scram-sha-256` é o padrão moderno de autenticação por senha; evite `md5` (legado) e
`trust` (sem senha — só em socket local de laboratório).

---

## Convivência de versões

Ao contrário de muitos softwares, **você pode ter várias majors do PostgreSQL na mesma máquina** —
elas usam portas e diretórios de dados diferentes.

**Debian/Ubuntu** gerencia isso elegantemente:
```bash
pg_lsclusters
# lista todos os clusters de todas as versões, com porta e estado
sudo pg_ctlcluster 17 main stop      # para o cluster da 17
sudo pg_ctlcluster 18 main start     # inicia o da 18
```
Cada versão instala em `/usr/lib/postgresql/<versão>/` e cada cluster fica na sua porta (5432,
5433…).

**A migração de major** (levar os dados da 17 para a 18) **não** é automática — os formatos de
dados internos diferem entre majors. Duas formas:
```bash
# pg_upgrade: rápido, migra os arquivos no lugar (com --link)
sudo pg_upgradecluster 17 main       # utilitário do Debian que orquestra o pg_upgrade

# dump/restore: mais lento, mais seguro, funciona sempre
pg_dumpall -U postgres > tudo.sql    # do cluster antigo
psql -U postgres -f tudo.sql         # no cluster novo
```

> **Minor upgrade** (18.2 → 18.3) é indolor: mesmo formato de dados, só troca o binário e
> reinicia. **Major upgrade** (17 → 18) exige `pg_upgrade` ou dump/restore. Nunca confunda os
> dois.

---

## Reprodutibilidade

| Mecanismo | Como | O que garante |
|---|---|---|
| **Versão fixada** | `postgresql-18` (não "postgresql" genérico) | Mesma major |
| **Imagem fixada (Docker)** | `postgres:18.3` (não `postgres:latest`) | Mesma minor |
| **Scripts de esquema versionados** | `schema.sql` no Git | Estrutura idêntica |
| **Migrações** | Flyway, Liquibase, dbmate, ou `sqitch` | Evolução controlada e repetível do esquema |
| **`postgresql.conf` versionado** | Config no Git ou em ferramenta de infra | Mesmo comportamento entre máquinas |
| **`initdb` com locale explícito** | `initdb --locale=C --encoding=UTF8` | Ordenação e codificação previsíveis |

> **`latest` é uma armadilha** também aqui: `postgres:latest` no Docker pode pular de major sem
> aviso, e major upgrade não é automático — o container novo se recusa a subir sobre um diretório
> de dados de major diferente. Fixe a versão.

---

## Atualizar e voltar atrás

### Minor (segura, rotineira)
```bash
# Debian/Ubuntu
sudo apt update && sudo apt upgrade postgresql-18
sudo systemctl restart postgresql
# Fedora/RHEL
sudo dnf upgrade postgresql18-server
# macOS
brew upgrade postgresql@18
```
```bash
sudo -u postgres psql -c "SELECT version();"    # confirme a nova minor
```

### Major (planejada)
Sempre **faça backup antes** (`pg_dumpall`). Use `pg_upgrade`/`pg_upgradecluster` (rápido) ou
dump/restore (seguro). Teste num ambiente separado. Guarde o cluster antigo até validar o novo.

### Voltar atrás
Para minor, reinstale a versão anterior do pacote. Para major, **não há downgrade automático** —
você restaura do backup pré-atualização. É por isso que o backup antes do major upgrade não é
opcional.

---

## Desinstalar por completo

> **A remoção do pacote NÃO apaga os dados.** O diretório de dados fica para trás.

### Debian/Ubuntu
```bash
# 1) Veja onde estão os dados antes de decidir
pg_lsclusters
# 2) Remova pacotes E configuração
sudo apt purge -y 'postgresql-*'
sudo apt autoremove -y
# 3) Apague os dados — IRREVERSÍVEL (faça backup antes se houver algo a salvar)
sudo rm -rf /var/lib/postgresql /etc/postgresql /etc/postgresql-common
sudo deluser postgres 2>/dev/null || true
```

### Fedora/RHEL
```bash
sudo systemctl disable --now postgresql-18
sudo dnf remove -y 'postgresql18*'
sudo rm -rf /var/lib/pgsql       # ⚠️ apaga os dados
```

### macOS
```bash
brew services stop postgresql@18
brew uninstall postgresql@18
rm -rf /opt/homebrew/var/postgresql@18    # ⚠️ apaga os dados (Apple Silicon)
# Postgres.app: arraste o app para a Lixeira e apague ~/Library/Application Support/Postgres
```

### Windows
Painel de Controle → desinstalar PostgreSQL. O desinstalador pergunta se remove o diretório de
dados; se não, apague `C:\Program Files\PostgreSQL\18\data` manualmente.

---

## Solução de problemas — erros literais

| Mensagem (literal) | Causa provável | Correção |
|---|---|---|
| `psql: error: connection to server on socket "/var/run/postgresql/.s.PGSQL.5432" failed: No such file or directory` | O servidor não está rodando | `sudo systemctl start postgresql` · `pg_ctlcluster 18 main start` · abrir o Postgres.app |
| `psql: FATAL: role "seu_usuario" does not exist` | O usuário do banco não foi criado (o do SO ≠ o do banco) | `sudo -u postgres createuser --interactive seu_usuario` |
| `psql: FATAL: database "x" does not exist` | Banco não criado, ou nome errado | `createdb x` · `\l` no psql lista os bancos |
| `psql: FATAL: password authentication failed for user "x"` | Senha errada, ou `pg_hba.conf` exige senha e você não deu | Redefina com `ALTER USER x PASSWORD '...'` · confira o método no `pg_hba.conf` |
| `FATAL: Peer authentication failed for user "x"` | Método `peer`: o usuário do SO não bate com o do banco | Conecte com `-h localhost` (força `scram`), ou ajuste o `pg_hba.conf` |
| `could not connect to server: Connection refused ... 5432` | Servidor parado, ou `listen_addresses` não inclui a interface | Iniciar o serviço · ajustar `listen_addresses` e `pg_hba.conf` |
| `FATAL: no pg_hba.conf entry for host "..."` | O `pg_hba.conf` não permite aquele host/usuário/banco | Adicionar a linha `host` correspondente e `pg_reload_conf()` |
| `initdb: error: directory "..." exists but is not empty` | Tentou inicializar sobre um diretório já usado | Use outro diretório, ou remova o conteúdo (⚠️ apaga dados) |
| `FATAL: the database system is starting up` | Recuperação após queda; ainda subindo | Aguarde; veja o log em `/var/log/postgresql/` |
| `FATAL: database files are incompatible with server` | Diretório de dados de outra major | `pg_upgrade`/dump-restore; não misture majors no mesmo diretório |
| `WARNING: .pgpass ... permissions ... are too open` (senha ignorada) | `.pgpass` sem `chmod 600` | `chmod 600 ~/.pgpass` |
| `FATAL: sorry, too many clients already` | Excedeu `max_connections` | Feche conexões ociosas · use um *pooler* (PgBouncer) · aumente o limite |
| `ERROR: could not extend file ... No space left on device` | Disco cheio | Libere espaço; monitore o crescimento e o `pg_wal/` |

Sempre olhe o **log** — ele diz a verdade:
```bash
# Debian/Ubuntu
sudo tail -50 /var/log/postgresql/postgresql-18-main.log
# Fedora/RHEL
sudo tail -50 /var/lib/pgsql/18/data/log/*.log
```

---

## Checklist "ambiente pronto"

```bash
psql --version                                    # psql (PostgreSQL) 18.x
pg_isready                                         # ".../5432 - accepting connections"
psql -h localhost -U seu_usuario -d meu_banco -c "SELECT version();"   # PostgreSQL 18.x ...
psql -h localhost -U seu_usuario -d meu_banco -c "SELECT now();"       # data/hora atual
psql -h localhost -U seu_usuario -d meu_banco -c "CREATE TABLE t(x int); DROP TABLE t;"  # cria e apaga: sem erro
```

Cinco linhas sem erro = ambiente pronto. Siga para [04-como-comecar.md](04-como-comecar.md).

---

## Autoteste

1. Quais são as três coisas distintas que "instalar PostgreSQL" envolve (servidor, cliente,
   cluster)? O que cada uma é?
2. No Debian/Ubuntu o cluster já sobe sozinho; no Fedora/RHEL, não. Qual comando cria o cluster no
   Fedora?
3. No macOS via Homebrew, quem é o superusuário padrão do banco? E no Linux?
4. Por que seu `.pgpass` pode estar sendo "ignorado", e qual é a correção?
5. Qual é a diferença entre um minor upgrade (18.2→18.3) e um major upgrade (17→18) em termos de
   dados?
6. O que os arquivos `postgresql.conf` e `pg_hba.conf` controlam, respectivamente?
7. `sudo apt purge postgresql` libera o espaço em disco dos dados? Justifique.
8. Você recebe `Peer authentication failed`. O que aconteceu e como conectar mesmo assim?
9. Por que expor `listen_addresses = '*'` sem cuidado é um risco de segurança?
10. Qual é a alternativa para escrever SQL hoje sem instalar nada?

---

### Fontes consultadas (11/08/2026)

- [PostgreSQL — Linux downloads (Ubuntu)](https://www.postgresql.org/download/linux/ubuntu/) — repositório PGDG, script `apt.postgresql.org.sh` e método manual deb822
- [PostgreSQL — Downloads](https://www.postgresql.org/download/) e [macOS](https://www.postgresql.org/download/macosx/) · [Homebrew — postgresql@18](https://formulae.brew.sh/formula/postgresql@18)
- [PostgreSQL 18 release notes](https://www.postgresql.org/docs/18/release-18.html) — 18.0 em 25/09/2025; 18.3 em 26/02/2026 (fontes secundárias para a data da 18.3)
- [PostgreSQL — Versioning policy](https://www.postgresql.org/support/versioning/) — suporte de ~5 anos por major
