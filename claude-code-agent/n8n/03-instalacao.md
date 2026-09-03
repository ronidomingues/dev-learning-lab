# 03 · Manual de instalação — passo a passo, por sistema operacional

`Nível: iniciante` · `Manual de campo` · `Pesquisado na web e testado em: 01/09/2026`

---

## Leia estas seis linhas antes de qualquer comando

1. **O caminho recomendado é Docker.** Não é preferência: o **n8n 3.0 (previsto para
   outubro de 2026)** deixa de suportar `npm install n8n` e `npx n8n`. Quem instalar
   por npm hoje terá de migrar.
   Fonte: [v3.0 Breaking changes](https://docs.n8n.io/changelog/v30-breaking-changes), consultado em 01/09/2026.
2. **Versões vigentes em 01/09/2026:** canal `stable` = **2.36.9**, canal `beta` = **2.37.6**,
   última tag publicada no GitHub = **2.38.1** (01/09/2026). O n8n lança uma versão menor
   quase toda semana.
3. **Versão mínima sensata:** qualquer 2.x. Evite 1.x novo em 2026 — está em fim de vida
   e a migração para 2.0 tem quebras (arquivo [23](23-ciclo-de-vida-e-versionamento.md)).
4. **Não precisa de conta nem de cartão** para o caminho autogerido.
5. **Windows: use WSL2.** A justificativa está na seção 4.3.
6. Se você só quer *ver* a ferramenta hoje, pule para
   [Alternativa sem instalar nada](#alternativa-sem-instalar-nada).

---

## Índice

- [0. Alternativa sem instalar nada](#alternativa-sem-instalar-nada)
- [1. O conjunto de tecnologias envolvido](#1-o-conjunto-de-tecnologias-envolvido)
- [2. Escolha do método](#2-escolha-do-método)
- [3. Instalar o Docker](#3-instalar-o-docker-pré-requisito-de-tudo)
  - [3.1 Linux Debian/Ubuntu](#31-linux--família-debianubuntu)
  - [3.2 Linux Fedora/RHEL](#32-linux--família-fedorarhelrocky)
  - [3.3 macOS](#33-macos-intel-e-apple-silicon)
  - [3.4 Windows](#34-windows-wsl2--o-caminho-recomendado)
- [4. Instalar o n8n](#4-instalar-o-n8n)
  - [4.1 Método A — one-line setup](#41-método-a--one-line-setup-o-mais-rápido)
  - [4.2 Método B — `docker run` mínimo](#42-método-b--docker-run-mínimo-para-entender-o-que-acontece)
  - [4.3 Método C — Docker Compose com Postgres](#43-método-c--docker-compose-com-postgres-o-que-você-quer-de-verdade)
  - [4.4 Método D — npm](#44-método-d--npm-legado-não-comece-por-aqui)
- [5. Tecnologias de apoio](#5-tecnologias-de-apoio)
- [6. PATH e variáveis de ambiente](#6-path-e-variáveis-de-ambiente)
- [7. Permissões](#7-permissões)
- [8. Rede corporativa: proxy, certificado interno, firewall](#8-rede-corporativa-proxy-certificado-interno-firewall)
- [9. Conviver com várias versões](#9-conviver-com-várias-versões)
- [10. Reprodutibilidade](#10-reprodutibilidade)
- [11. Atualizar — e voltar atrás](#11-atualizar--e-voltar-atrás)
- [12. Desinstalar por completo](#12-desinstalar-por-completo)
- [13. Solução de problemas (mensagens literais)](#13-solução-de-problemas-mensagens-literais)
- [14. Checklist "ambiente pronto"](#14-checklist-ambiente-pronto)

---

<a name="alternativa-sem-instalar-nada"></a>
## 0. Alternativa sem instalar nada

Ofereço isto **antes** do caminho longo de propósito: a maior causa de desistência
no primeiro dia é a instalação, não a ferramenta.

| Opção | Como | Custa? | Limite |
|---|---|---|---|
| **n8n Cloud (teste gratuito)** | [n8n.io/cloud](https://n8n.io/cloud/) → criar conta → instância pronta em ~2 minutos | Gratuito no teste; sem cartão para Starter/Pro | O teste tem limites de execução e prazo; depois vira assinatura |
| **GitHub Codespaces** | Abrir um repositório qualquer no Codespaces e rodar o `docker run` da seção 4.2 lá dentro | Camada gratuita mensal do GitHub | Some quando o Codespace é apagado |
| **Um VPS de US$ 4–6/mês** | Hetzner/DigitalOcean/Contabo + seção 4.3 | ~R$ 25–40/mês | É seu problema de segurança agora |
| **Máquina de outra pessoa** | Qualquer Linux com Docker onde você tenha acesso | — | — |

**Recomendação:** se você tem Docker na sua máquina, instale local — você aprende
mais e não depende de ninguém. Se não tem e não pode ter hoje, comece pelo Cloud
e volte a este arquivo quando puder. Os arquivos 04 em diante funcionam igual nos dois.

**Diferenças que importam entre Cloud e autogerido** (para não se surpreender):

| Recurso | Cloud | Autogerido |
|---|---|---|
| Módulos npm externos no node Code | ❌ não | ✅ sim (`NODES_EXTERNAL_...`) |
| Bibliotecas Python no node Code | ❌ não | ✅ com task runners |
| Variáveis de ambiente do host nas expressões | ❌ | ✅ (com cuidado — veja [22](22-seguranca.md)) |
| Fila/workers, Postgres próprio, backups | ❌ (o n8n cuida) | ✅ (você cuida) |
| HTTPS e domínio | ✅ pronto | Você configura |
| Preço | € 20+/mês | Custo do servidor |

---

## 1. O conjunto de tecnologias envolvido

Instalar "o n8n" não é instalar um programa. É montar uma pilha. Cada camada
abaixo ganha sua seção neste arquivo:

```
┌───────────────────────────────────────────────────────────┐
│  Navegador  (o editor é uma aplicação web)                │
├───────────────────────────────────────────────────────────┤
│  n8n        (Node.js — o motor + o editor)                │
├───────────────────────────────────────────────────────────┤
│  Banco      SQLite (padrão)  ou  PostgreSQL (produção)    │
│  Fila       Redis  (só em queue mode)                     │
│  Runners    task runners (executam o node Code isolado)   │
├───────────────────────────────────────────────────────────┤
│  Docker Engine + Docker Compose v2                        │
├───────────────────────────────────────────────────────────┤
│  Sistema operacional (Linux / macOS / Windows+WSL2)       │
└───────────────────────────────────────────────────────────┘
   Opcionais: proxy reverso (Caddy/Nginx/Traefik) + TLS,
              túnel (cloudflared/ngrok) para webhooks locais,
              editor de texto/Git para versionar os fluxos.
```

---

## 2. Escolha do método

| Método | Para quem | Prós | Contras | Recomendo? |
|---|---|---|---|---|
| **A · one-line setup** (`curl -fsSL https://get.n8n.io \| sh`) | Quem quer rodar hoje | Escreve o compose por você, já com sandbox de IA | Traz serviços que pesam (~4 GB RAM); menos transparente | ✅ para começar |
| **B · `docker run`** | Quem quer entender | Um comando, nada de mágica | Sem Postgres, sem fila; SQLite | ✅ para aprender |
| **C · Docker Compose** | Quem vai usar de verdade | Postgres, volumes, reinício automático, versionável em Git | Você escreve o arquivo | ✅ **destino final** |
| **D · npm** | Ninguém, a partir de agora | Sem Docker | **Some no n8n 3.0 (out/2026)** | ❌ |
| **E · Kubernetes / Helm** | Quem já tem cluster | Escala | Complexidade | Só se você já vive nele — veja [21](21-escala-e-producao.md) |

Este arquivo cobre A, B, C e D. E fica no arquivo [21](21-escala-e-producao.md).

---

## 3. Instalar o Docker (pré-requisito de tudo)

### 3.1 Linux — família Debian/Ubuntu

Testado em **Ubuntu 22.04.5 LTS**, em **01/09/2026**.

**Passo 1 — remover pacotes antigos conflitantes.** Distribuições trazem um
`docker.io` velho que confunde com o oficial.

```bash
for p in docker.io docker-doc docker-compose docker-compose-v2 podman-docker containerd runc; do sudo apt-get remove -y $p; done
```
> O que faz: remove versões antigas e o `docker-compose` v1 (Python), que **não**
> serve — o n8n exige o plugin `docker compose` v2.
> É normal ver "Package X is not installed"; ignore.

**Passo 2 — adicionar a chave e o repositório oficiais.**

```bash
sudo apt-get update && sudo apt-get install -y ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
```
> O que faz: baixa a chave pública com que a Docker Inc. assina os pacotes, para o
> `apt` conseguir verificar que o pacote é mesmo deles.

```bash
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
```
> O que faz: registra o repositório oficial da sua versão do Ubuntu.
> Em **Debian**, troque `ubuntu` por `debian` nas duas URLs.

**Passo 3 — instalar.**

```bash
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

**Passo 4 — verificar.**

```bash
docker --version
# esperado: Docker version 29.7.2, build a7dcaa6   (qualquer 24+ serve)

docker compose version
# esperado: Docker Compose version v5.5.0          (precisa começar com v2 ou maior)
```

> **Se a saída for diferente:**
> - `command not found: docker` → o passo 3 falhou. Releia a saída do `apt-get install`.
> - `docker-compose version 1.29...` → você tem o v1 (com hífen). Ele **não serve**.
>   Instale `docker-compose-plugin` e use `docker compose` (com espaço).

**Passo 5 — usar Docker sem `sudo`.** Veja a [seção 7](#7-permissões). Faça isso agora;
o restante deste arquivo assume que `docker ps` funciona sem `sudo`.

### 3.2 Linux — família Fedora/RHEL/Rocky

Testado com base na documentação oficial da Docker, consultada em 01/09/2026.

```bash
sudo dnf -y install dnf-plugins-core
sudo dnf config-manager --add-repo https://download.docker.com/linux/fedora/docker-ce.repo
sudo dnf install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo systemctl enable --now docker
```
> Em RHEL/Rocky/AlmaLinux, troque `fedora` por `rhel` na URL do repositório.
> `systemctl enable --now` liga o serviço agora **e** no próximo boot — no Ubuntu
> o pacote já faz isso; no Fedora, não.

```bash
docker --version && docker compose version
# esperado: as duas linhas de versão, sem erro
```

> **Atenção SELinux (Fedora/RHEL):** se um contêiner não consegue escrever numa
> pasta montada (`permission denied` dentro do contêiner, mas a pasta parece certa
> no host), o motivo quase sempre é SELinux. A correção é acrescentar `:Z` ao bind
> mount: `-v ./dados:/home/node/.n8n:Z`.

### 3.3 macOS (Intel e Apple Silicon)

**Caminho recomendado: Docker Desktop.**

1. Baixe em [docs.docker.com/desktop/install/mac-install](https://docs.docker.com/desktop/install/mac-install/).
   Escolha **Apple Silicon** se seu Mac é M1/M2/M3/M4; **Intel chip** caso contrário.
   Em dúvida: menu  → *Sobre este Mac* → se aparecer "Apple M...", é Apple Silicon.
2. Arraste para Aplicativos, abra, aceite os termos, espere a baleia ficar estável.

```bash
docker --version && docker compose version
# esperado: duas linhas de versão
```

**Alternativa sem Docker Desktop** (mais leve, sem a licença comercial do Desktop
— veja a nota abaixo): **Colima**.

```bash
brew install colima docker docker-compose
colima start --cpu 2 --memory 4
docker ps
# esperado: cabeçalho da tabela, sem erro
```
> Colima roda uma VM Linux enxuta. `--memory 4` é o mínimo confortável para o n8n.
> Após instalar `docker-compose` pelo Homebrew, confirme que `docker compose version`
> (com espaço) responde; se não, rode `mkdir -p ~/.docker/cli-plugins && ln -sfn $(brew --prefix)/opt/docker-compose/bin/docker-compose ~/.docker/cli-plugins/docker-compose`.

> **Nota de licença (importante em empresa):** o **Docker Desktop** exige assinatura
> paga para empresas acima de determinado porte (a Docker Inc. define o limiar; em
> 2026 ele gira em torno de 250 funcionários **ou** US$ 10 milhões de receita anual —
> **confirme no site da Docker antes de instalar na empresa**). O **Docker Engine no
> Linux é Apache 2.0 e gratuito**, e **Colima/Rancher Desktop** são alternativas
> gratuitas no macOS. Isso é custo oculto clássico: veja [80](80-custos-e-licencas.md).

### 3.4 Windows — WSL2 (o caminho recomendado)

**Por que WSL2 e não Windows nativo?** Quatro motivos concretos, não gosto pessoal:

1. **Permissões de arquivo.** A imagem do n8n roda como o usuário `node` (UID 1000)
   e exige permissão restrita no arquivo de configuração. O sistema de arquivos do
   Windows não expressa permissões POSIX; o n8n reclama ou ignora.
2. **Finais de linha.** Git no Windows converte `LF` para `CRLF` por padrão. Um
   `.sh` ou um `.env` com `CRLF` quebra dentro do contêiner Linux com erros crípticos.
3. **Desempenho de bind mount.** Montar `/mnt/c/...` dentro de um contêiner é
   ordens de grandeza mais lento que montar de dentro do WSL.
4. **Paridade com produção.** Seu servidor será Linux. Desenvolver em Linux elimina
   uma classe inteira de "na minha máquina funciona".

**Passo 1 — instalar o WSL2.** No PowerShell **como Administrador**:

```powershell
wsl --install -d Ubuntu
```
> O que faz: habilita os recursos do Windows necessários, instala o kernel do WSL2
> e a distribuição Ubuntu. **Reinicie** quando ele pedir.

```powershell
wsl --status
# esperado: "Versão padrão: 2"
```
> Se disser versão 1: `wsl --set-default-version 2` e reinstale a distro.

**Passo 2 — escolher entre duas configurações de Docker:**

| Configuração | Como | Quando |
|---|---|---|
| **Docker Desktop com backend WSL2** | Instalar o Docker Desktop para Windows e marcar *Use the WSL 2 based engine*; em *Settings → Resources → WSL Integration*, ligar sua distro | Você quer a interface gráfica e não se importa com a licença |
| **Docker Engine dentro do Ubuntu do WSL** | Abrir o Ubuntu e seguir a [seção 3.1](#31-linux--família-debianubuntu) igualzinho | Você quer gratuito e leve; **é o que eu faço** |

**Passo 3 — regra de ouro do WSL, e a que mais gente ignora:**

> **Mantenha os arquivos do projeto DENTRO do sistema de arquivos do Linux**
> (`~/n8n`, isto é, `\\wsl$\Ubuntu\home\voce\n8n`), **nunca** em `/mnt/c/Users/...`.
> Bind mounts atravessando essa fronteira são lentos e causam problemas de permissão.
> A própria documentação do n8n diz isso explicitamente.

```bash
# dentro do Ubuntu do WSL
cd ~ && mkdir -p n8n && cd n8n && pwd
# esperado: /home/<seu-usuario>/n8n
```

**Windows nativo, sem WSL** (só para constar): instale o Docker Desktop com backend
Hyper-V e siga os métodos B/C. Funciona para experimentar. Não recomendo para
trabalho — pelos quatro motivos acima.

---

## 4. Instalar o n8n

<a name="41-método-a--one-line-setup-o-mais-rápido"></a>
### 4.1 Método A — one-line setup (o mais rápido)

Substitui oficialmente o antigo `npx n8n`.

```bash
curl -fsSL https://get.n8n.io | sh
```
> O que faz: confere Docker e Compose v2, cria a pasta `./n8n`, escreve
> `compose.yml`, `.env` (com segredos aleatórios) e `searxng-settings.yml`,
> baixa as imagens e sobe tudo.

Saída esperada (formato conforme documentação oficial):

```
✓ Docker found (24.0.6)
✓ Docker Compose found (v2.24.0)
✓ Created ./n8n/compose.yml
✓ Created ./n8n/searxng-settings.yml
✓ Created ./n8n/.env (unique secrets generated)
Pulling images and starting (this can take a few minutes on first run)...
✓ Started n8n 2.32.0 and sandbox services

n8n is running at: http://localhost:5678
```

**Verificação:**

```bash
curl -sf http://localhost:5678/healthz && echo " OK"
# esperado: {"status":"ok"} OK
```

Abra <http://localhost:5678> e crie o usuário dono da instância (fica no **seu** banco).

> **Antes de rodar:** este método sobe também `sandbox-api` e `sandbox-runner-1`
> (Docker-dentro-de-Docker, `privileged: true`) para a IA. Pede **~4 GB de RAM livres**
> e **jamais** deve ter suas portas expostas na internet. Se você não quer o assistente
> de IA agora, use o [Método C](#43-método-c--docker-compose-com-postgres-o-que-você-quer-de-verdade),
> que é mais leve.

Comandos de manutenção que ele imprime:

```bash
docker compose -f ./n8n/compose.yml down          # parar
curl -fsSL https://get.n8n.io | sh -s -- --upgrade # atualizar
docker compose -f ./n8n/compose.yml down -v        # APAGA TODOS OS DADOS
```

<a name="42-método-b--docker-run-mínimo-para-entender-o-que-acontece"></a>
### 4.2 Método B — `docker run` mínimo (para entender o que acontece)

Troque `America/Sao_Paulo` pelo seu fuso, se for outro.

```bash
docker volume create n8n_data
```
> O que faz: cria um volume nomeado. É onde ficam o banco SQLite, a **chave de
> criptografia** e as configurações. Sem ele, você perde tudo ao remover o contêiner.

```bash
docker run -d \
  --name n8n \
  --restart unless-stopped \
  -p 5678:5678 \
  -e GENERIC_TIMEZONE="America/Sao_Paulo" \
  -e TZ="America/Sao_Paulo" \
  -e N8N_ENFORCE_SETTINGS_FILE_PERMISSIONS=true \
  -v n8n_data:/home/node/.n8n \
  n8nio/n8n:stable
```
> Linha a linha:
> - `-d` roda em segundo plano; `--restart unless-stopped` religa após reboot.
> - `-p 5678:5678` publica a porta do editor no seu computador.
> - `TZ` acerta o relógio do sistema dentro do contêiner; **`GENERIC_TIMEZONE`**
>   acerta o fuso que o **Schedule Trigger** usa. São coisas diferentes: esquecer
>   `GENERIC_TIMEZONE` é a causa nº 1 de "meu agendamento rodou 3 horas atrasado".
> - `N8N_ENFORCE_SETTINGS_FILE_PERMISSIONS=true` exige permissão restrita no
>   `config` (onde vive a chave de criptografia).
> - `:stable` fixa o canal estável em vez do `latest`.

**Verificação:**

```bash
docker ps --filter name=n8n --format '{{.Names}}\t{{.Status}}\t{{.Ports}}'
# esperado: n8n   Up 20 seconds   0.0.0.0:5678->5678/tcp

curl -sf http://localhost:5678/healthz
# esperado: {"status":"ok"}

docker logs n8n 2>&1 | tail -5
# esperado: uma linha "Editor is now accessible via: http://localhost:5678/"
```

> **Se a saída for diferente:**
> - `Error response from daemon: ... port is already allocated` → algo já usa a
>   5678. Troque para `-p 5679:5678` e acesse `http://localhost:5679`.
> - Contêiner reiniciando em laço → `docker logs n8n` mostra a causa. Veja a
>   [tabela de erros](#13-solução-de-problemas-mensagens-literais).

Em n8n **1.x** era preciso `-e N8N_RUNNERS_ENABLED=true`. Em **2.x** a variável está
depreciada e desnecessária — os task runners já são o padrão.

<a name="43-método-c--docker-compose-com-postgres-o-que-você-quer-de-verdade"></a>
### 4.3 Método C — Docker Compose com Postgres (o que você quer de verdade)

Este é o formato que você versiona em Git e leva para o servidor.

**Passo 1 — pasta do projeto.**

```bash
mkdir -p ~/n8n && cd ~/n8n
```

**Passo 2 — arquivo `.env`** (nunca comite este arquivo):

```bash
cat > .env <<'EOF'
# --- Banco ---
POSTGRES_USER=n8n
POSTGRES_PASSWORD=troque-esta-senha
POSTGRES_DB=n8n

# --- n8n ---
GENERIC_TIMEZONE=America/Sao_Paulo
TZ=America/Sao_Paulo
# Gere a sua com:  openssl rand -hex 32
N8N_ENCRYPTION_KEY=troque-por-32-bytes-em-hex
EOF
chmod 600 .env
```

```bash
openssl rand -hex 32
# esperado: 64 caracteres hexadecimais. Cole no N8N_ENCRYPTION_KEY.
```

> **A chave de criptografia é a peça mais importante do sistema.** É com ela que o
> n8n cifra as credenciais no banco. **Perdeu a chave = perdeu todas as credenciais**,
> mesmo com backup do banco. Guarde-a num gerenciador de segredos. Se você não
> definir a variável, o n8n gera uma na primeira execução e a grava em
> `~/.n8n/config` dentro do volume — o que também funciona, desde que você nunca
> perca o volume.

**Passo 3 — `compose.yml`:**

```yaml
volumes:
  n8n_data:
  db_data:

services:
  postgres:
    image: postgres:18
    restart: unless-stopped
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
      PGDATA: /var/lib/postgresql/data
    volumes:
      - db_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
      interval: 5s
      timeout: 5s
      retries: 10

  n8n:
    image: n8nio/n8n:stable
    restart: unless-stopped
    depends_on:
      postgres:
        condition: service_healthy
    ports:
      - "5678:5678"
    environment:
      DB_TYPE: postgresdb
      DB_POSTGRESDB_HOST: postgres
      DB_POSTGRESDB_PORT: "5432"
      DB_POSTGRESDB_DATABASE: ${POSTGRES_DB}
      DB_POSTGRESDB_USER: ${POSTGRES_USER}
      DB_POSTGRESDB_PASSWORD: ${POSTGRES_PASSWORD}
      N8N_ENCRYPTION_KEY: ${N8N_ENCRYPTION_KEY}
      GENERIC_TIMEZONE: ${GENERIC_TIMEZONE}
      TZ: ${TZ}
      N8N_ENFORCE_SETTINGS_FILE_PERMISSIONS: "true"
      # Higiene de dados: sem isto o banco cresce até encher o disco
      EXECUTIONS_DATA_PRUNE: "true"
      EXECUTIONS_DATA_MAX_AGE: "336"        # horas (14 dias)
      EXECUTIONS_DATA_PRUNE_MAX_COUNT: "50000"
    volumes:
      - n8n_data:/home/node/.n8n
```

> **`PGDATA: /var/lib/postgresql/data` não é decoração.** O Postgres 18 mudou o
> diretório de dados padrão. Sem essa linha, ele escreve fora do volume montado e
> **seu banco reaparece vazio no próximo boot**. A documentação do n8n destaca isso.

**Passo 4 — subir e verificar.**

```bash
docker compose up -d
docker compose ps
# esperado: postgres  ... (healthy) ; n8n  ... Up
```

```bash
curl -sf http://localhost:5678/healthz && echo " OK"
# esperado: {"status":"ok"} OK

docker compose logs n8n | grep -i "editor is now accessible"
# esperado: Editor is now accessible via: http://localhost:5678/
```

Abra <http://localhost:5678>.

> **Se `postgres` nunca fica `healthy`:** `docker compose logs postgres`.
> A causa mais comum é reaproveitar um volume criado por um Postgres de versão
> maior anterior: `database files are incompatible with server`. Nesse caso, ou
> volte a imagem para a versão antiga, ou faça `pg_dumpall` e restaure.

<a name="44-método-d--npm-legado-não-comece-por-aqui"></a>
### 4.4 Método D — npm (legado; não comece por aqui)

Só documentado para quem já tem uma instalação assim e precisa mantê-la até migrar.

```bash
node --version
# esperado: v20.x ou v22.x  (Node 20 LTS é o mínimo)

npm install -g n8n
n8n start
```
> Instalação global via `npm -g` costuma exigir `sudo` — e `sudo npm -g` é uma
> má ideia (veja a [seção 7](#7-permissões)). Use `nvm` para ter o Node numa pasta
> sua e dispensar o `sudo`.

**Este caminho deixa de existir no n8n 3.0 (outubro de 2026).** Planeje a migração
para o [Método C](#43-método-c--docker-compose-com-postgres-o-que-você-quer-de-verdade)
agora: exporte fluxos e credenciais (seção 10) e importe no contêiner.

---

## 5. Tecnologias de apoio

### 5.1 PostgreSQL

Já coberto pelo Método C. Instalação separada só se você usa um banco gerenciado:
crie o banco e o usuário e aponte `DB_POSTGRESDB_*` para ele.

```bash
# testar de fora se o banco responde (cliente psql instalado no host)
psql "postgresql://n8n:senha@localhost:5432/n8n" -c "select version();"
# esperado: uma linha com "PostgreSQL 18.x"
```

### 5.2 Redis (somente para queue mode)

Não instale agora. Você precisa dele quando for escalar; o passo a passo está em
[21-escala-e-producao.md](21-escala-e-producao.md). Em resumo, é mais um serviço
no `compose.yml` e três variáveis (`EXECUTIONS_MODE=queue`, `QUEUE_BULL_REDIS_HOST`,
`QUEUE_BULL_REDIS_PORT`) mais contêineres `n8n worker`.

### 5.3 Túnel para receber webhooks na sua máquina

Um webhook precisa que a internet alcance seu computador. Em casa, não alcança.

**Opção 1 — Cloudflare Tunnel (gratuito, sem conta para testes rápidos):**

```bash
docker run --rm --network host cloudflare/cloudflared:latest tunnel --url http://localhost:5678
# esperado: uma URL https://<algo>.trycloudflare.com impressa no terminal
```
Depois, informe essa URL ao n8n para que ele gere os endereços de webhook certos:

```yaml
    environment:
      WEBHOOK_URL: https://<algo>.trycloudflare.com/
      N8N_PROXY_HOPS: "1"
```
> `WEBHOOK_URL` diz ao n8n qual endereço público mostrar nos nós de webhook.
> Sem isso, ele mostra `http://localhost:5678/...`, que o serviço externo não alcança.
> `N8N_PROXY_HOPS` diz quantos proxies existem à frente, para o IP do cliente ser lido corretamente.

**Opção 2 — o túnel embutido (`--tunnel`).** Existe, é conveniente e a própria
documentação avisa: **é para desenvolvimento local, não é seguro em produção**.

### 5.4 Proxy reverso e HTTPS (produção)

Não exponha a porta 5678 na internet sem TLS: você estaria trafegando senhas em
texto claro. Caddy resolve com quatro linhas e certificado automático:

```
# Caddyfile
n8n.seudominio.com.br {
    reverse_proxy n8n:5678
}
```
E no serviço n8n do compose: `N8N_HOST=n8n.seudominio.com.br`,
`N8N_PROTOCOL=https`, `WEBHOOK_URL=https://n8n.seudominio.com.br/`,
`N8N_PROXY_HOPS=1`. Detalhes de segurança em [22-seguranca.md](22-seguranca.md).

### 5.5 Editor e Git (para versionar fluxos)

Fluxos são JSON. Um editor com realce de JSON e um repositório Git já bastam.
O n8n tem um recurso oficial de *source control* (Git), mas é **licenciado**
(planos pagos) — veja [23](23-ciclo-de-vida-e-versionamento.md) e [80](80-custos-e-licencas.md).
Na versão gratuita, versione exportando com a CLI (seção 10).

---

## 6. PATH e variáveis de ambiente

### 6.1 Por que "não pegou" antes de reabrir o terminal

Um processo herda as variáveis de ambiente **no momento em que nasce**. Editar
`.bashrc` não muda os terminais já abertos — muda os próximos. Por isso a regra
é: **feche e abra o terminal**, ou rode `source` no arquivo.

| Shell / SO | Arquivo | Recarregar sem fechar |
|---|---|---|
| bash (Linux, WSL) | `~/.bashrc` | `source ~/.bashrc` |
| zsh (macOS por padrão) | `~/.zshrc` | `source ~/.zshrc` |
| fish | `~/.config/fish/config.fish` | `source ~/.config/fish/config.fish` |
| PowerShell | `$PROFILE` (veja com `echo $PROFILE`) | `. $PROFILE` |

```bash
echo $PATH | tr ':' '\n'
# esperado: uma lista de pastas, uma por linha. É aqui que o shell procura comandos.
```

### 6.2 As variáveis do n8n

No caminho Docker, **você não mexe no PATH** — mexe no bloco `environment` do
compose. As que importam de saída:

| Variável | Para que serve | Cuidado |
|---|---|---|
| `N8N_ENCRYPTION_KEY` | Cifra as credenciais no banco | Perdeu = perdeu as credenciais |
| `GENERIC_TIMEZONE` | Fuso dos nós de agendamento | Esquecer causa horários errados |
| `TZ` | Fuso do sistema dentro do contêiner | Diferente do anterior |
| `WEBHOOK_URL` | Endereço público mostrado nos webhooks | Obrigatório atrás de proxy/túnel |
| `N8N_HOST`, `N8N_PROTOCOL`, `N8N_PORT` | Como o editor monta as URLs | |
| `DB_TYPE` e `DB_POSTGRESDB_*` | Banco | |
| `EXECUTIONS_DATA_PRUNE`, `EXECUTIONS_DATA_MAX_AGE` | Poda do histórico | **Sem isso o banco cresce sem parar** |
| `N8N_ENFORCE_SETTINGS_FILE_PERMISSIONS` | Exige `0600` no arquivo de config | |
| `N8N_BLOCK_ENV_ACCESS_IN_NODE` | Impede que expressões leiam `$env` | Ligue em ambiente multiusuário |

Lista completa e sempre atualizada:
[docs.n8n.io — Use environment variables](https://docs.n8n.io/deploy/host-n8n/configure-n8n/basic-configuration/use-environment-variables.md).

### 6.3 Armadilhas do arquivo `.env` no n8n 2.x

O n8n 2.0 atualizou a biblioteca que lê `.env`. Duas mudanças pegam gente:

- **Crase (`` ` ``)**: valores com crase agora precisam de aspas.
- **Multilinha**: o comportamento com valores de várias linhas mudou.

Se uma senha contém `#`, `$`, crase ou espaço, **ponha entre aspas simples**:
```bash
# senha com caracteres especiais: use aspas simples
POSTGRES_PASSWORD='se#nha$com espaco'
```
Melhor ainda: gere senhas sem esses caracteres (`openssl rand -hex 16`).

---

## 7. Permissões

### 7.1 Docker sem `sudo` (Linux e WSL)

Sintoma:

```
permission denied while trying to connect to the Docker daemon socket at unix:///var/run/docker.sock
```

Correção:

```bash
sudo usermod -aG docker $USER
```
> O que faz: põe você no grupo `docker`, que tem permissão no socket do daemon.

```bash
newgrp docker      # aplica o grupo neste terminal, sem deslogar
docker ps
# esperado: cabeçalho da tabela (CONTAINER ID  IMAGE ...), sem erro
```
> Se ainda falhar, **saia da sessão e entre de novo** (ou reinicie o WSL com
> `wsl --shutdown` no PowerShell). A lista de grupos de um processo também é
> herdada no nascimento.

> **Por que isso é um risco, e não só burocracia:** quem está no grupo `docker`
> pode subir um contêiner que monta `/` do host com privilégios. Na prática,
> **pertencer ao grupo `docker` equivale a ter root**. Em servidor compartilhado,
> prefira `rootless docker` ou `sudo` explícito. Não é paranoia: é a razão pela
> qual a instalação não faz isso sozinha.

### 7.2 Por que `sudo npm install -g` é problema

Três motivos concretos:

1. Os *lifecycle scripts* dos pacotes rodam **como root** durante a instalação —
   qualquer pacote da árvore de dependências executa código com poder total.
2. Os arquivos ficam com dono `root`, e depois `npm update` sem `sudo` falha com
   `EACCES`, criando o hábito de rodar tudo com `sudo`.
3. Mistura pacotes de usuário com o sistema; desinstalar deixa sujeira.

**Caminho certo:** use um gerenciador de versões (`nvm`, `fnm`, `mise`) que põe o
Node dentro do seu `$HOME`. Aí `npm -g` grava numa pasta sua e nada pede `sudo`.

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
source ~/.bashrc
nvm install 22
node --version
# esperado: v22.x.x
```

### 7.3 Permissão do arquivo de configuração do n8n

Com `N8N_ENFORCE_SETTINGS_FILE_PERMISSIONS=true`, o n8n exige `0600` em
`/home/node/.n8n/config` — é onde mora a chave de criptografia quando você não a
passa por variável. Se aparecer aviso sobre permissões:

```bash
docker compose exec n8n sh -c 'chmod 600 /home/node/.n8n/config && ls -l /home/node/.n8n/config'
# esperado: -rw------- 1 node node ... /home/node/.n8n/config
```

### 7.4 Dono do volume (o erro mais confuso de todos)

A imagem roda como o usuário `node` (UID 1000). Se você monta uma **pasta do host**
em vez de um volume nomeado, e a pasta pertence a outro UID, o n8n não consegue
escrever:

```bash
mkdir -p ~/n8n/dados && sudo chown -R 1000:1000 ~/n8n/dados
```
> Em Fedora/RHEL, some `:Z` ao bind mount por causa do SELinux (seção 3.2).
> **Recomendação: use volumes nomeados** (`n8n_data:`) e o problema não existe.

---

## 8. Rede corporativa: proxy, certificado interno, firewall

Se você está numa rede de empresa, esta seção é a diferença entre funcionar e
passar a tarde xingando.

### 8.1 O proxy tem que chegar ao **daemon**, não só ao seu shell

Erro clássico: `curl` funciona, `docker pull` trava. Motivo: `curl` lê
`HTTP_PROXY` do **seu** ambiente; o `docker pull` só pede ao **daemon** que baixe,
e o daemon é outro processo, com outro ambiente, iniciado pelo systemd.

**Correção (Linux com systemd):**

```bash
sudo mkdir -p /etc/systemd/system/docker.service.d
sudo tee /etc/systemd/system/docker.service.d/http-proxy.conf > /dev/null <<'EOF'
[Service]
Environment="HTTP_PROXY=http://proxy.empresa:3128"
Environment="HTTPS_PROXY=http://proxy.empresa:3128"
Environment="NO_PROXY=localhost,127.0.0.1,::1,.empresa.local"
EOF
sudo systemctl daemon-reload && sudo systemctl restart docker
```

```bash
sudo systemctl show --property=Environment docker
# esperado: mostra HTTP_PROXY/HTTPS_PROXY/NO_PROXY que você acabou de definir
docker pull hello-world && docker run --rm hello-world
# esperado: "Hello from Docker!"
```

**Docker Desktop:** *Settings → Resources → Proxies*.

### 8.2 `no_proxy` mal formatado quebra clientes

Armadilha específica e cruel: **`no_proxy` não aceita espaços depois das vírgulas**
em vários clientes (notadamente as bibliotecas HTTP de Python e alguns SDKs). Um
valor como:

```
no_proxy=localhost, 127.0.0.0/8, ::1        # ERRADO — tem espaços
```

faz o cliente tentar acessar `localhost` **através do proxy**, e a conexão a
`http://localhost:5678` falha de um jeito que parece problema do n8n. Escreva sem
espaços e cobrindo as duas grafias:

```bash
export no_proxy=localhost,127.0.0.1,::1,0.0.0.0
export NO_PROXY=$no_proxy
```

### 8.3 Certificado interno (TLS inspecionado)

Se a empresa inspeciona TLS, todo HTTPS que sai da sua máquina é reassinado por
uma CA interna. Resultado: `unable to get local issuer certificate` /
`self-signed certificate in certificate chain` dentro do contêiner.

Correção: injetar a CA no contêiner.

```yaml
    volumes:
      - ./ca-empresa.crt:/usr/local/share/ca-certificates/ca-empresa.crt:ro
    environment:
      NODE_EXTRA_CA_CERTS: /usr/local/share/ca-certificates/ca-empresa.crt
```
> `NODE_EXTRA_CA_CERTS` é a variável que o **Node.js** lê para acrescentar uma CA
> ao seu armazenamento próprio. Não confunda com o `update-ca-certificates` do
> sistema: o Node tem seu próprio conjunto embutido e ignora o do SO.

Isso é assunto do curso [`tls/`](../tls/00-MAPA.md).

### 8.4 Firewall e portas

| Porta | Para quê | Exponha? |
|---|---|---|
| 5678 | Editor + webhooks | Só via proxy reverso com TLS |
| 5432 | Postgres | **Nunca** para a internet |
| 6379 | Redis | **Nunca** para a internet |
| 8080/9090 | sandbox de IA | **Nunca** — roda privilegiado |

### 8.5 Registry espelhado

Se a empresa espelha o Docker Hub:

```json
// /etc/docker/daemon.json
{ "registry-mirrors": ["https://registry.empresa.local"] }
```
E `sudo systemctl restart docker`. Se as imagens vêm de um registry privado,
troque `n8nio/n8n:stable` por `registry.empresa.local/n8nio/n8n:2.36.9`.

---

## 9. Conviver com várias versões

**Com Docker, é trivial** — e é mais uma razão para preferir Docker:

```bash
docker run -d --name n8n-prod -p 5678:5678 -v n8n_prod:/home/node/.n8n n8nio/n8n:2.36.9
docker run -d --name n8n-teste -p 5679:5678 -v n8n_teste:/home/node/.n8n n8nio/n8n:2.38.1
```
> Volumes diferentes, portas diferentes, versões diferentes, zero conflito.
> Use isto para **testar a atualização antes de aplicar em produção**.

> **Regra que salva:** um volume tocado por uma versão mais nova **não volta**
> para a mais antiga. As migrações de banco do n8n são para frente apenas. Nunca
> aponte a versão nova para o volume de produção sem backup.

**Com npm**, use `nvm` para as versões do Node e `npm install -g n8n@2.36.9` para
fixar a do n8n. Mas veja o Método D: esse caminho está acabando.

---

## 10. Reprodutibilidade

### 10.1 Fixe a versão da imagem

```yaml
image: n8nio/n8n:2.36.9      # ✅ reprodutível
# image: n8nio/n8n:latest    # ❌ muda debaixo dos seus pés
# image: n8nio/n8n:stable    # 🟡 aceitável em dev; move com o tempo
```
Para rigor máximo, fixe pelo digest:

```bash
docker image inspect n8nio/n8n:2.36.9 --format '{{index .RepoDigests 0}}'
# esperado: n8nio/n8n@sha256:....  — use isso no compose
```

### 10.2 Versione o que é código, isole o que é segredo

```
n8n/
├── compose.yml        ← Git
├── .env.example       ← Git (sem valores reais)
├── .env               ← .gitignore  (segredos!)
└── workflows/*.json   ← Git (exportados pela CLI)
```

### 10.3 Exportar e importar fluxos e credenciais pela CLI

```bash
# exportar todos os fluxos, um arquivo por fluxo
docker compose exec n8n n8n export:workflow --all --separate --output=/home/node/.n8n/backup/
docker compose cp n8n:/home/node/.n8n/backup ./workflows
```

```bash
# importar de volta (em outra instância, por exemplo)
docker compose cp ./workflows n8n:/tmp/wf
docker compose exec n8n n8n import:workflow --separate --input=/tmp/wf
# esperado: uma linha "Successfully imported N workflows."
```

```bash
# credenciais — CUIDADO: --decrypted grava segredos em texto claro
docker compose exec n8n n8n export:credentials --all --decrypted --output=/tmp/cred.json
```
> Trate esse arquivo como se fosse uma senha mestra: `chmod 600`, use e apague.
> Sem `--decrypted`, o arquivo sai cifrado e só serve numa instância com a **mesma**
> `N8N_ENCRYPTION_KEY`.

### 10.4 Backup mínimo que presta

Três coisas, e **as três** são obrigatórias:

1. **O banco.** `docker compose exec postgres pg_dump -U n8n n8n | gzip > backup-$(date +%F).sql.gz`
2. **A chave de criptografia** (`N8N_ENCRYPTION_KEY` ou o volume `.n8n`).
3. **O `compose.yml` e o `.env`** (o `.env` num cofre de segredos).

Backup do banco sem a chave = backup inútil para as credenciais.

---

## 11. Atualizar — e voltar atrás

```bash
# 0) BACKUP primeiro (seção 10.4). Sem exceção.
cd ~/n8n
docker compose exec postgres pg_dump -U n8n n8n | gzip > backup-pre-update.sql.gz

# 1) leia as notas de versão entre a sua e a alvo
#    https://docs.n8n.io/changelog/release-notes

# 2) puxe e suba
docker compose pull
docker compose up -d

# 3) verifique
docker compose logs n8n | tail -20
curl -sf http://localhost:5678/healthz
```

**Voltar atrás:** troque a tag da imagem para a versão anterior **e restaure o
banco do backup**. Só trocar a imagem não basta, porque as migrações já rodaram.

```bash
gunzip -c backup-pre-update.sql.gz | docker compose exec -T postgres psql -U n8n -d n8n
```

**Migrações grandes (1.x → 2.x):** existe uma ferramenta oficial que varre a
instância e aponta incompatibilidades antes de você migrar —
[v2.0 Migration tool](https://docs.n8n.io/changelog/v20-migration-tool). Use-a.

---

## 12. Desinstalar por completo

### Docker

```bash
cd ~/n8n
docker compose down                 # para e remove os contêineres (dados ficam)
docker compose down -v              # ⚠️ REMOVE TAMBÉM OS VOLUMES = apaga tudo
docker rmi n8nio/n8n:stable postgres:18
rm -rf ~/n8n                        # arquivos de configuração
docker system prune -a --volumes    # ⚠️ limpa TUDO do Docker, não só n8n
```

O que fica para trás se você esquecer:

| Resíduo | Onde | Como remover |
|---|---|---|
| Volumes nomeados | `docker volume ls` | `docker volume rm n8n_data db_data` |
| Imagens | `docker images` | `docker rmi ...` |
| Rede do compose | `docker network ls` | `docker network rm n8n_default` |
| Túnel/cloudflared | contêiner separado | `docker rm -f <nome>` |

### npm

```bash
npm uninstall -g n8n
rm -rf ~/.n8n            # ⚠️ banco SQLite, chave de criptografia, credenciais
rm -rf ~/.cache/n8n ~/.npm/_cacache
```

> `~/.n8n` é o que a maioria esquece. Ele guarda a chave de criptografia e o banco
> SQLite com **suas credenciais cifradas**. Apagar sem backup é irreversível.

---

## 13. Solução de problemas (mensagens literais)

| Mensagem | Causa provável | Correção |
|---|---|---|
| `command not found: docker` | Docker não instalado, ou binário fora do PATH | Refaça a [seção 3](#3-instalar-o-docker-pré-requisito-de-tudo); confira `echo $PATH` |
| `permission denied while trying to connect to the Docker daemon socket` | Seu usuário não está no grupo `docker` | `sudo usermod -aG docker $USER && newgrp docker` ([7.1](#71-docker-sem-sudo-linux-e-wsl)) |
| `Cannot connect to the Docker daemon at unix:///var/run/docker.sock. Is the docker daemon running?` | Serviço parado (Linux) ou Docker Desktop fechado (macOS/Windows) | `sudo systemctl start docker`, ou abra o Docker Desktop |
| `docker: Error response from daemon: driver failed programming external connectivity ... port is already allocated` | Porta 5678 ocupada | `-p 5679:5678`, ou descubra o culpado: `sudo lsof -i :5678` |
| `Error: getaddrinfo EAI_AGAIN registry-1.docker.io` / `docker pull` trava | Daemon sem proxy configurado | [Seção 8.1](#81-o-proxy-tem-que-chegar-ao-daemon-não-só-ao-seu-shell) |
| `unable to get local issuer certificate` / `self-signed certificate in certificate chain` | CA interna da empresa não está no contêiner | `NODE_EXTRA_CA_CERTS` ([8.3](#83-certificado-interno-tls-inspecionado)) |
| `EACCES: permission denied, mkdir '/usr/lib/node_modules/n8n'` | `npm install -g` sem permissão | Use `nvm` em vez de `sudo` ([7.2](#72-por-que-sudo-npm-install--g-é-problema)) |
| `Error: EACCES: permission denied, open '/home/node/.n8n/config'` | Pasta montada com dono errado (UID ≠ 1000) | `sudo chown -R 1000:1000 <pasta>`, ou use volume nomeado ([7.4](#74-dono-do-volume-o-erro-mais-confuso-de-todos)) |
| `Permissions 0644 for n8n settings file are too wide` | Arquivo `config` com permissão frouxa | `chmod 600 /home/node/.n8n/config` ([7.3](#73-permissão-do-arquivo-de-configuração-do-n8n)) |
| `database files are incompatible with server` (log do postgres) | Volume escrito por um Postgres de versão maior diferente | `pg_dumpall` na versão antiga, restaurar na nova; não basta trocar a tag |
| Banco Postgres "reaparece vazio" após atualizar para o 18 | Faltou `PGDATA: /var/lib/postgresql/data` | Acrescente a linha ([4.3](#43-método-c--docker-compose-com-postgres-o-que-você-quer-de-verdade)) |
| `Mismatching encryption keys` / credenciais somem | `N8N_ENCRYPTION_KEY` mudou ou o volume `.n8n` foi trocado | Restaure a chave original; sem ela, as credenciais são irrecuperáveis |
| Webhook mostra `http://localhost:5678/...` e o serviço externo não chega | Falta `WEBHOOK_URL` | Defina `WEBHOOK_URL` e `N8N_PROXY_HOPS` ([5.3](#53-túnel-para-receber-webhooks-na-sua-máquina)) |
| Agendamento roda em horário errado | `GENERIC_TIMEZONE` não definido (padrão UTC) | Defina `GENERIC_TIMEZONE` **e** `TZ` |
| `Error: connect ECONNREFUSED 127.0.0.1:5432` | O n8n procurou o Postgres em `localhost` (dentro do próprio contêiner) | `DB_POSTGRESDB_HOST` deve ser o **nome do serviço** (`postgres`), não `localhost` |
| `docker-compose: command not found` mas `docker compose` funciona | Você tem só o plugin v2 | Use `docker compose` (com espaço). É o correto |
| Contêiner sobe e cai em laço, sem log claro | Falta de memória (OOM) | `docker stats`; suba a RAM; desligue o sandbox de IA |
| Funciona no Linux, falha no WSL | Bind mount atravessando `/mnt/c` | Mova o projeto para `~/` dentro do WSL ([3.4](#34-windows--wsl2-o-caminho-recomendado)) |
| `sandbox-runner-1` reiniciando com `... must be set` | Faltam variáveis do sandbox no `.env` | Confira `SANDBOX_RUNNER_API_KEYS` e `SANDBOX_RUNNER_REGISTRATION_TOKEN` |

---

## 14. Checklist "ambiente pronto"

Rode tudo. Só siga para o [04-como-comecar.md](04-como-comecar.md) quando todas
as linhas responderem o esperado.

```bash
docker --version
# esperado: Docker version 24.x ou superior

docker compose version
# esperado: Docker Compose version v2.x ou superior

docker ps
# esperado: cabeçalho da tabela, SEM "permission denied"

docker run --rm hello-world | head -2
# esperado: "Hello from Docker!"

df -h . | tail -1
# esperado: pelo menos 10G livres

curl -sf http://localhost:5678/healthz
# esperado: {"status":"ok"}

docker compose -f ~/n8n/compose.yml ps
# esperado: n8n Up; postgres (healthy) — se você usou o Método C
```

E, no navegador: <http://localhost:5678> abre o editor e você já criou o usuário dono.

---

## Autoteste

1. Por que Docker deixou de ser recomendação e virou requisito? A partir de qual
   versão, e em que mês?
2. Qual é a diferença entre `TZ` e `GENERIC_TIMEZONE`? Qual erro aparece se você
   esquecer a segunda?
3. O que acontece com suas credenciais se você perder o `N8N_ENCRYPTION_KEY`, mesmo
   tendo backup completo do banco?
4. Por que `curl` funciona atrás do proxy da empresa mas `docker pull` trava? Onde
   se conserta?
5. Um `no_proxy` com espaços depois das vírgulas causa qual sintoma concreto?
6. Por que `sudo npm install -g` é uma má prática? Dê dois motivos técnicos.
7. Estar no grupo `docker` equivale a quê, em termos de privilégio? Por quê?
8. Você atualizou de 2.36 para 2.38 e quer voltar. Basta trocar a tag da imagem?
   Justifique.
9. Para que serve `PGDATA` no serviço do Postgres 18, e o que acontece sem ele?
10. Cite três resíduos que ficam na máquina se você "desinstalar" o n8n só parando
    o contêiner.

---

*Fontes consultadas em 01/09/2026:*
- *[docs.n8n.io — Install options](https://docs.n8n.io/deploy/host-n8n/install-options.md)*
- *[docs.n8n.io — One-line setup](https://docs.n8n.io/deploy/host-n8n/install-options/one-line-setup.md)*
- *[docs.n8n.io — Install using Docker Compose](https://docs.n8n.io/deploy/host-n8n/install-options/install-using-docker-compose.md)*
- *[docs.n8n.io — Install with Docker](https://docs.n8n.io/deploy/host-n8n/install-options/install-with-docker.md)*
- *[docs.n8n.io — v3.0 Breaking changes](https://docs.n8n.io/changelog/v30-breaking-changes)*
- *[docs.n8n.io — Environment variables](https://docs.n8n.io/deploy/host-n8n/configure-n8n/basic-configuration/use-environment-variables.md)*
- *[docs.docker.com — Install Docker Engine](https://docs.docker.com/engine/install/)*
- *Tags e datas de release: [GitHub n8n-io/n8n releases](https://github.com/n8n-io/n8n/releases)*

*Anterior: [02-pre-requisitos.md](02-pre-requisitos.md) · Próximo: [04-como-comecar.md](04-como-comecar.md)*
