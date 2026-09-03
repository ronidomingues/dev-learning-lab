# 30 · Entrega em produção — o que fazer com o `.env`, por cenário

`Nível: intermediário a avançado` · `Atualizado em: 14/08/2026`

**Este é o arquivo que responde diretamente à pergunta que originou o curso.**
Se você veio pelo índice, comece aqui e volte aos fundamentos depois.

---

## 0. A resposta, em três frases

1. **O arquivo `.env` não vai.** Ele fica na sua máquina, no `.gitignore`, e morre ali.
2. **O conteúdo vai** — por um canal escolhido conforme onde o sistema roda, e
   sempre de forma que o valor **já esteja no ambiente** quando o processo iniciar.
3. **O código não muda.** Ele lê `process.env` / `os.environ` / `getenv()` e nunca
   sabe de onde veio. É por isso que o mesmo artefato roda em todo lugar.

A tabela de decisão:

| Onde o sistema vai rodar | O que substitui o `.env` | Seção |
|---|---|---|
| VPS/servidor próprio com systemd | `EnvironmentFile` 640, ou `LoadCredential` | [§2](#2-servidor-linux-com-systemd), [§3](#3-systemd-loadcredential--a-melhor-opção-que-quase-ninguém-usa) |
| Contêiner solto (Docker) | `-e` + arquivo montado com `_FILE` | [§4](#4-docker) |
| Docker Compose / Swarm | `secrets:` | [§5](#5-docker-compose-e-swarm) |
| Kubernetes | `Secret` + External Secrets Operator | [§6](#6-kubernetes) |
| PaaS (Heroku, Render, Railway, Fly, Vercel) | painel/CLI do provedor | [§7](#7-paas) |
| Serverless (Lambda, Cloud Run, Functions) | configuração da função + cofre | [§8](#8-serverless) |
| Hospedagem compartilhada de PHP | `.env` fora do `public_html`, 600 | [16-php.md §5](16-php.md) |
| **Máquina do cliente (on-premise)** | instalador que pergunta e grava | [55-entrega-ao-cliente.md](55-entrega-ao-cliente.md) |
| Windows Server | variáveis do serviço / DPAPI | [§9](#9-windows-server) |

---

## 1. O princípio comum a todos os cenários

```
      ┌──────────────────────────────────────────────────────────┐
      │  QUEM COLOCA A VARIÁVEL      │   QUEM LÊ                 │
      │  (muda por ambiente)         │   (nunca muda)            │
      ├──────────────────────────────┼───────────────────────────┤
      │  --env-file (dev)            │                           │
      │  systemd EnvironmentFile     │                           │
      │  docker run -e               │──►  process.env.X         │
      │  Compose secrets             │     os.environ["X"]       │
      │  K8s Secret                  │     getenv("X")           │
      │  painel do PaaS              │                           │
      │  cofre (Vault/AWS/GCP)       │                           │
      │  instalador no cliente       │                           │
      └──────────────────────────────┴───────────────────────────┘
                                            ▲
                          esta coluna é o CONTRATO: o .env.example
```

E os quatro critérios para julgar qualquer mecanismo:

| Critério | Pergunta |
|---|---|
| **Confidencialidade** | quem consegue ler o valor? (usuários do SO, imagem, backup, log) |
| **Rotação** | trocar o valor exige reiniciar? derruba o serviço? |
| **Auditoria** | dá para saber **quem leu** e **quando**? |
| **Bootstrap** | como o segredo chega lá **na primeira vez**? |

O último é o mais esquecido, e tem nome: o **problema do segredo zero**
([60-teoria-avancada.md §4](60-teoria-avancada.md)).

---

## 2. Servidor Linux com systemd

O caminho mais comum fora da nuvem gerenciada, e uma resposta **legítima e final**
para a maioria dos sistemas pequenos e médios. Não tenha vergonha dele.

```bash
sudo useradd --system --no-create-home --shell /usr/sbin/nologin minhaapp
sudo install -d -m 750 -o root -g minhaapp /etc/minha-app
```

```bash
sudo install -m 640 -o root -g minhaapp /dev/null /etc/minha-app/env
sudo tee /etc/minha-app/env > /dev/null <<'EOF'
DATABASE_URL=postgres://app:senha-real@db.interno:5432/loja
API_KEY=sk_live_xxxxxxxxxxxxxxxx
PORT=8080
EOF
```

```bash
ls -l /etc/minha-app/env
# esperado: -rw-r----- 1 root minhaapp ... /etc/minha-app/env
```

**Leia essa permissão com atenção — ela é a metade do trabalho:**

| | Quem | Pode |
|---|---|---|
| dono | `root` | ler e **escrever** |
| grupo | `minhaapp` | **só ler** |
| outros | todos os demais usuários | **nada** |

A aplicação lê e **não pode alterar** a própria configuração. Se ela for comprometida
por uma falha de execução remota, o atacante não consegue plantar valores ali.

A unit completa está em
[07-projeto-modelo/deploy/cofre-de-recados.service](07-projeto-modelo/deploy/cofre-de-recados.service).
Os três detalhes que separam quem já sofreu:

```ini
ExecStartPre=/usr/bin/node /opt/app/src/check-config.mjs   # falha ANTES de abrir porta
RestartPreventExitStatus=78                                # não reinicia em loop eterno
EnvironmentFile=/etc/minha-app/env                         # sem "-": obrigatório
```

**Verificação — o que o processo realmente recebeu:**

```bash
sudo cat /proc/$(pgrep -u minhaapp -f 'node /opt/app')/environ | tr '\0' '\n' | grep -c DATABASE_URL
# esperado: 1
```

### O que este modelo resolve e o que não resolve

| Critério | Avaliação |
|---|---|
| Confidencialidade | 🟡 boa contra outros usuários; **nula** contra root e contra `/proc/PID/environ` |
| Rotação | 🔴 exige `systemctl restart` — há queda de conexões |
| Auditoria | 🔴 nenhuma. Ninguém sabe quem leu o arquivo |
| Bootstrap | 🟡 manual: alguém digitou ou copiou uma vez |
| Custo | 🟢 zero |
| Complexidade | 🟢 mínima |

**Quando isto basta:** um ou poucos servidores, uma equipe pequena, nenhuma exigência
de conformidade, rotação anual aceitável. Ou seja: a maioria dos sistemas do mundo.

### Erros comuns aqui

```ini
Environment="DATABASE_URL=postgres://app:senha@db/loja"   # ❌ aparece em `systemctl show`
```

`systemctl show minha-app -p Environment` mostra o que está na unit — e a unit é
`644`, legível por todos. **Use `Environment=` só para o que não é segredo.**

```bash
export DATABASE_URL=...   # no ~/.bashrc   ❌
```

O systemd não lê `~/.bashrc`. E o `~/.bashrc` vaza em `history`, em `ps e` e para
todo processo interativo. Ver [10-fundamentos.md §4](10-fundamentos.md).

---

## 3. systemd `LoadCredential` — a melhor opção que quase ninguém usa

Disponível desde o systemd 247 (2020). É a resposta mais limpa para servidor Linux,
e é subestimada porque quase não aparece em tutoriais.

```ini
[Service]
LoadCredential=api_key:/etc/minha-app/api_key
LoadCredential=db_url:/etc/minha-app/db_url
Environment="API_KEY_FILE=%d/api_key"     # %d expande para o diretório das credenciais
Environment="DATABASE_URL_FILE=%d/db_url"
ExecStart=/usr/bin/node /opt/app/src/app.mjs
```

O que o systemd faz:

1. lê os arquivos **como root**, antes de largar privilégios;
2. copia o conteúdo para um `tmpfs` privado do serviço (`/run/credentials/<unit>/`),
   com permissão **`0400` só para o usuário do serviço**;
3. exporta `$CREDENTIALS_DIRECTORY`, que `%d` expande;
4. **apaga tudo quando o serviço para**.

### Por que isto é melhor que `EnvironmentFile`

| | `EnvironmentFile` | `LoadCredential` |
|---|---|---|
| Aparece em `/proc/PID/environ` | **sim** | **não** — só o caminho aparece |
| Herdado por subprocessos | **sim**, o valor | só o caminho (o filho precisa de permissão para ler) |
| Vai para relatório de crash / APM | frequentemente | não |
| Persiste em disco | sim, em `/etc` | não — `tmpfs`, some no stop |
| Isolamento por serviço | não | **sim**: cada unit vê só as suas |
| Suporta criptografia em repouso | não | **sim**: `systemd-creds encrypt` (com TPM2) |
| Combina com o padrão `_FILE` | — | **perfeitamente** |

E o passo seguinte, com TPM2:

```bash
sudo systemd-creds encrypt --name=api_key api_key.txt /etc/minha-app/api_key.cred
```

```ini
LoadCredentialEncrypted=api_key:/etc/minha-app/api_key.cred
```

O arquivo em disco agora está **criptografado com uma chave selada no TPM da máquina**.
Copiá-lo para outro servidor não adianta: ele só decifra naquele hardware.
Isso resolve, para servidor físico, boa parte do problema do segredo zero — de graça,
sem cofre, sem rede.

> **Opinião profissional:** se você entrega em Linux moderno e o
> [projeto-modelo](07-projeto-modelo/README.md) já implementa o padrão `_FILE`
> (implementa), migrar de `EnvironmentFile` para `LoadCredential` é uma tarde de
> trabalho e o melhor retorno de segurança por hora investida em todo este curso.

---

## 4. Docker

### O que **não** fazer

```dockerfile
ENV API_KEY=sk_live_xxx          # ❌ grava na CAMADA. Fica na imagem PARA SEMPRE.
ARG TOKEN                         # ❌ aparece em `docker history`
```

```bash
docker history --no-trunc minha-imagem | grep -i 'sk_live'
# se aparecer, o segredo está em toda cópia dessa imagem, em todo registry
```

Camada de imagem é **imutável**. Um `RUN rm segredo.txt` numa camada seguinte
**não apaga** o conteúdo da camada anterior.

### O que fazer

```bash
# 1) variável direta — para o que NÃO é segredo
docker run -e PORT=8080 -e LOG_LEVEL=info minha-app

# 2) repassar do host sem escrever o valor no comando (não vai para o histórico do shell)
docker run -e API_KEY minha-app

# 3) arquivo — cômodo, mas TODO o conteúdo vira ambiente
docker run --env-file /etc/minha-app/env minha-app

# 4) ⭐ segredo como ARQUIVO montado + padrão _FILE
docker run \
  -v /etc/minha-app/secrets:/run/secrets:ro \
  -e API_KEY_FILE=/run/secrets/api_key \
  -e DATABASE_URL_FILE=/run/secrets/database_url \
  minha-app
```

A opção 4 é a recomendada, e o [projeto-modelo](07-projeto-modelo/src/config.mjs)
já a suporta. Vantagens já tabuladas em [06-exemplos.md #7](06-exemplos.md):
não aparece em `docker inspect`, não em `/proc/PID/environ`, não é herdado por
filhos, e **pode ser rotacionado sem recriar o contêiner**.

### Segredo em tempo de **build**

```dockerfile
# syntax=docker/dockerfile:1.7
RUN --mount=type=secret,id=npmrc,target=/root/.npmrc npm ci --omit=dev
```

```bash
docker build --secret id=npmrc,src=$HOME/.npmrc -t minha-app .
```

O segredo é montado só durante aquele `RUN` e **não vira camada**. É a única forma
correta de usar token de registry privado num build.

### Verificação obrigatória antes de publicar uma imagem

```bash
docker history --no-trunc minha-app | grep -iE 'secret|token|password|key='
docker inspect -f '{{json .Config.Env}}' minha-app
docker run --rm --entrypoint sh minha-app -c 'ls -la /app; cat /app/.env 2>/dev/null'
```

O terceiro comando pega o erro mais comum: `.dockerignore` sem `.env`, e o
`COPY . .` levou o arquivo para dentro da imagem. Adicione **`.git`** também — sem
ele, o histórico inteiro do repositório entra, incluindo aquele `.env` que você
commitou e removeu há dois anos.

---

## 5. Docker Compose e Swarm

```yaml
services:
  app:
    image: minha-app
    environment:
      PORT: "8080"
      API_KEY_FILE: /run/secrets/api_key
    secrets: [api_key]

secrets:
  api_key:
    file: ./secrets/api_key        # compose local
    # external: true               # Swarm: gerenciado pelo cluster
```

Diferença importante:

- **`docker compose`** (uma máquina): `secrets:` é apenas um *bind mount* de arquivo
  em `/run/secrets/`. Simples, e o arquivo existe em disco no host.
- **Swarm**: os segredos são armazenados **criptografados no log Raft** do cluster,
  transmitidos por TLS mútuo apenas aos nós que rodam aquele serviço, e montados em
  `tmpfs`. Nunca tocam o disco do nó.

```bash
printf 'senha-real' | docker secret create db_password -
docker service update --secret-add db_password minha-app
```

⚠️ **Segredo do Swarm é imutável.** Rotacionar exige criar `db_password_v2`, atualizar
o serviço e remover o antigo. Isso é chato de propósito: força a técnica de
sobreposição de [45-rotacao-e-ciclo-de-vida.md](45-rotacao-e-ciclo-de-vida.md).

---

## 6. Kubernetes

### O mal-entendido fundador

```bash
kubectl get secret app-secrets -o jsonpath='{.data.DB_PASSWORD}' | base64 -d
```

**Base64 é codificação, não criptografia.** Sem configuração adicional, o valor está
em texto legível no etcd e em **qualquer backup do etcd**.

```yaml
# /etc/kubernetes/enc/config.yaml — no kube-apiserver
apiVersion: apiserver.config.k8s.io/v1
kind: EncryptionConfiguration
resources:
  - resources: ["secrets"]
    providers:
      - kms:                       # ⭐ KMS v2
          apiVersion: v2
          name: meu-kms
          endpoint: unix:///tmp/kms.sock
      - identity: {}               # fallback para ler o que já existe sem criptografia
```

⚠️ **KMS v1 está obsoleto desde o Kubernetes 1.28 e desativado por padrão desde o
1.29. Use KMS v2.** Se não houver KMS, `aescbc` ou `secretbox` já são infinitamente
melhores que nada — mas aí a chave de criptografia fica no disco do nó de controle,
o que só move o problema um degrau.

### Injetar: variável vs. volume

```yaml
# (a) como variável de ambiente — simples, e com as desvantagens de sempre
envFrom:
  - secretRef: { name: app-secrets }

# (b) ⭐ como volume — permite ROTAÇÃO SEM REINICIAR O POD
volumes:
  - name: secrets
    secret: { secretName: app-secrets }
containers:
  - volumeMounts:
      - { name: secrets, mountPath: /run/secrets, readOnly: true }
    env:
      - { name: API_KEY_FILE, value: /run/secrets/api_key }
```

**A diferença é decisiva:** o kubelet **atualiza automaticamente** um Secret montado
como volume quando ele muda (com atraso de até ~1 minuto). Combinado com o código de
recarga de [06-exemplos.md #14](06-exemplos.md), você troca a credencial **sem
reiniciar um único pod**. Como variável de ambiente, o valor é congelado no `execve`
e exige recriar o pod.

### Quem consegue ler

```bash
kubectl auth can-i get secrets --namespace producao
```

Quem tem `get secrets` no namespace lê **todos** os segredos dele. E quem tem
permissão de criar um Pod pode montar qualquer Secret e imprimi-lo. Portanto:
**RBAC por namespace é a fronteira de segurança real**, não o objeto Secret.

### External Secrets Operator (ESO)

Projeto CNCF (sandbox desde julho de 2022; em junho de 2026 na linha 2.x).
Sincroniza segredos de um cofre externo para Secrets do Kubernetes.

```yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata: { name: app-secrets }
spec:
  refreshInterval: 1h
  secretStoreRef: { name: aws-secrets, kind: ClusterSecretStore }
  target: { name: app-secrets }
  data:
    - secretKey: API_KEY
      remoteRef: { key: producao/minha-app, property: api_key }
```

Assim a **fonte da verdade** é o cofre (com auditoria, versionamento e rotação), e o
Kubernetes recebe uma cópia sincronizada. É o padrão dominante hoje.

Alternativas: **Sealed Secrets** (Bitnami — criptografa para uma chave do cluster,
permitindo versionar o `SealedSecret` no Git) e o **Secrets Store CSI Driver**
(monta direto do cofre, sem criar objeto Secret).

---

## 7. PaaS

```bash
heroku config:set DATABASE_URL='postgres://...' -a minha-app
fly secrets set API_KEY=sk_live_xxx
netlify env:set API_KEY sk_live_xxx
vercel env add API_KEY production
```

O melhor cenário do ponto de vista de esforço: o provedor guarda, criptografa e
injeta. Cuidados que continuam sendo seus:

| Cuidado | Por quê |
|---|---|
| Quem tem acesso ao painel **lê tudo** | revise a lista de colaboradores trimestralmente |
| Ex-funcionário no time | remover o acesso **não** rotaciona o que ele já viu |
| Log de build pode ecoar a variável | nunca `echo $API_KEY` em script de deploy |
| Vercel/Netlify: variável de **build** vs. **runtime** | ver [20-frontend-e-build-time.md](20-frontend-e-build-time.md) |
| Aprisionamento | exportar tudo antes de migrar: `heroku config -s > backup.env` |

---

## 8. Serverless

### AWS Lambda

```bash
aws lambda update-function-configuration \
  --function-name minha-funcao \
  --environment 'Variables={LOG_LEVEL=info,SECRETS_ID=prod/minha-app}'
```

⚠️ As variáveis de ambiente do Lambda são criptografadas em repouso com KMS, mas
ficam **visíveis em texto** para qualquer um com `lambda:GetFunctionConfiguration` —
uma permissão comum demais em políticas mal escritas.

**O padrão correto:** guarde apenas o **ponteiro** (`SECRETS_ID`) na variável, e
busque o valor do cofre na inicialização, com cache:

```javascript
// fora do handler = executa uma vez por instância fria, não por invocação
const segredos = await carregarSegredos(process.env.SECRETS_ID);

export async function handler(evento) {
  // aqui os segredos já estão em memória
}
```

Sem esse cache, a US$ 0,05 por 10.000 chamadas do Secrets Manager, uma função com
tráfego alto gera conta de milhares de dólares — e bate no limite de vazão da API.
Use a extensão de cache do Lambda (*AWS Parameters and Secrets Lambda Extension*).

### Google Cloud Run

```bash
gcloud run deploy minha-app \
  --set-env-vars LOG_LEVEL=info \
  --set-secrets API_KEY=minha-chave:latest \
  --set-secrets /run/secrets/db=db-url:latest    # ⭐ montado como ARQUIVO
```

O Cloud Run monta o segredo direto do Secret Manager, como variável **ou** como
arquivo. Prefira arquivo, pelas razões de sempre.

---

## 9. Windows Server

```powershell
# variável de ambiente do serviço (Registro)
Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Services\MinhaApp" `
  -Name Environment -Value @("PORT=8080","LOG_LEVEL=info")
```

⚠️ **Não use `setx` para segredo.** Ele grava no Registro em texto puro, e o valor
fica legível por qualquer processo do usuário — e persiste depois do reboot.

O mecanismo próprio da plataforma é a **DPAPI**:

```powershell
# criptografa para a conta da MÁQUINA — só decifra nesta máquina
$b = [System.Text.Encoding]::UTF8.GetBytes("senha-real")
$c = [System.Security.Cryptography.ProtectedData]::Protect($b, $null, 'LocalMachine')
[System.IO.File]::WriteAllBytes("C:\ProgramData\MinhaApp\api_key.bin", $c)
```

É o análogo do `systemd-creds` do §3: o arquivo cifrado não serve em outra máquina.
Para .NET, o caminho idiomático é o *Data Protection API* do ASP.NET Core com o
repositório de chaves em disco protegido por DPAPI.

Em geral, a recomendação prática: **rode em WSL2 ou em contêiner Linux** se puder.
O ferramental deste assunto é muito mais maduro em Unix.

---

## 10. Comparação final

| Mecanismo | Confidencialidade | Rotação | Auditoria | Custo | Complexidade |
|---|---|---|---|---|---|
| `.env` no servidor (0600) | 🟡 | 🔴 reinício | 🔴 | 🟢 | 🟢 |
| systemd `EnvironmentFile` | 🟡 | 🔴 reinício | 🔴 | 🟢 | 🟢 |
| systemd `LoadCredential` | 🟢 | 🟡 reinício | 🔴 | 🟢 | 🟢 |
| systemd `LoadCredentialEncrypted` + TPM | 🟢🟢 | 🟡 | 🔴 | 🟢 | 🟡 |
| Docker `-e` | 🔴 `inspect` | 🔴 recriar | 🔴 | 🟢 | 🟢 |
| Docker/Compose `secrets:` + `_FILE` | 🟢 | 🟢 sem reinício | 🔴 | 🟢 | 🟡 |
| K8s Secret como variável | 🟡 (com KMS v2) | 🔴 recriar pod | 🟡 audit log | 🟢 | 🟡 |
| K8s Secret como volume | 🟢 (com KMS v2) | 🟢 automático | 🟡 | 🟢 | 🟡 |
| Painel de PaaS | 🟢 | 🟡 redeploy | 🟡 | 🟢 | 🟢 |
| Cofre gerenciado (AWS/GCP/Azure) | 🟢 | 🟢 | 🟢 | 🟡 | 🟡 |
| Vault/OpenBao com credencial dinâmica | 🟢🟢 | 🟢🟢 automática | 🟢🟢 | 🟡 | 🔴 |

**Como escolher, honestamente:**

```
Quantos servidores?
├── 1–3, equipe pequena, sem conformidade
│     → systemd LoadCredential (ou EnvironmentFile 640). ACABOU.
│       Não monte cofre. O tempo é melhor gasto em backup e monitoramento.
├── contêineres numa máquina
│     → Compose secrets: + padrão _FILE
├── Kubernetes
│     → Secret como volume + KMS v2 + External Secrets Operator
├── nuvem gerenciada
│     → o cofre da própria nuvem (menor atrito, IAM já integrado)
└── conformidade (PCI, LGPD sensível, SOC 2) ou dezenas de serviços
      → Vault/OpenBao com credencial dinâmica
```

**A escolha errada mais comum não é escolher pouco — é escolher demais.** Um Vault em
alta disponibilidade para três servidores é um segundo sistema crítico para operar,
com o seu próprio problema de destravamento (*unseal*), o seu próprio backup e a sua
própria chance de virar o motivo de uma indisponibilidade. Ver
[75-armadilhas.md](75-armadilhas.md).

---

## Autoteste

1. Enuncie em três frases o que se faz com o `.env` ao entregar em produção.
2. Por que `Environment=` na unit do systemd não serve para segredo?
3. Cite três vantagens do `LoadCredential` sobre o `EnvironmentFile`.
4. O que `systemd-creds encrypt` com TPM2 resolve do problema do segredo zero?
5. Por que `ENV API_KEY=x` num Dockerfile é irreversível?
6. Por que um Secret do Kubernetes montado como volume permite rotação sem reiniciar, e como variável não?
7. Qual a diferença entre `secrets:` no Compose local e no Swarm?
8. Por que buscar o segredo do AWS Secrets Manager dentro do handler do Lambda é um erro caro?
9. Quem consegue ler todos os Secrets de um namespace do Kubernetes?
10. Para três servidores e uma equipe de dois, o que você recomendaria, e por que **não** um cofre?

---

**Fontes consultadas em 14/08/2026:** freedesktop.org/software/systemd (systemd.exec,
systemd-creds) · docs.docker.com/engine/swarm/secrets · kubernetes.io/docs (Encrypting
Confidential Data at Rest, KMS provider) · external-secrets.io · docs.aws.amazon.com
(Lambda environment variables) · cloud.google.com/run/docs/configuring/secrets.

**Próximo:** [35-ci-cd.md](35-ci-cd.md) · Voltar ao [mapa](00-MAPA.md)
