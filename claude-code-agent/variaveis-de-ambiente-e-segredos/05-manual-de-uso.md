# 05 · Manual de uso — referência consultável

`Nível: iniciante a intermediário` · `Atualizado em: 14/08/2026`

Organizado **por tarefa**, para consulta rápida. Use o índice.

| § | Tarefa |
|---|---|
| [1](#1-no-shell) | Ver, definir e remover variáveis no shell |
| [2](#2-sintaxe-do-arquivo-env) | Sintaxe do arquivo `.env` |
| [3](#3-ler-variável-no-código-por-linguagem) | Ler variável no código, por linguagem |
| [4](#4-carregar-um-env-por-linguagem) | Carregar um `.env`, por linguagem |
| [5](#5-injetar-variáveis-no-processo-em-produção) | Injetar variáveis em produção |
| [6](#6-docker-e-compose) | Docker e Compose |
| [7](#7-kubernetes) | Kubernetes |
| [8](#8-cicd) | CI/CD |
| [9](#9-sops) | SOPS |
| [10](#10-vault--openbao-cli) | Vault / OpenBao CLI |
| [11](#11-gitleaks) | gitleaks |
| [12](#12-inspecionar-e-depurar) | Inspecionar e depurar |
| [13](#13-convenções-de-nomes) | Convenções de nomes |
| [14](#14-obsoleto--o-que-substituiu) | **Obsoleto e o que substituiu** |

---

## 1. No shell

### Unix (bash / zsh)

| Tarefa | Comando |
|---|---|
| Listar todas | `printenv` ou `env` |
| Ver uma | `printenv PATH` ou `echo $PATH` |
| Ver uma, com segurança para segredo | `printenv TOKEN \| head -c 4; echo '...'` |
| Definir só para a sessão | `export VAR=valor` |
| Definir só para **um** comando | `VAR=valor comando` |
| Definir sem exportar (só o shell vê, filhos não) | `VAR=valor` |
| Remover | `unset VAR` |
| Rodar com ambiente **limpo** | `env -i comando` |
| Rodar sem uma variável específica | `env -u TOKEN comando` |
| Carregar um `.env` no shell atual | `set -a; source .env; set +a` |
| Ver o ambiente de **outro** processo | `cat /proc/<PID>/environ \| tr '\0' '\n'` |
| Contar quantas existem | `printenv \| wc -l` |

> `set -a` faz toda atribuição subsequente ser exportada automaticamente; `set +a`
> desliga. É o jeito canônico de carregar um `.env` no shell — mas cuidado: `source`
> **executa** o arquivo, então um `.env` malicioso com `$(rm -rf ~)` roda de verdade.
> Use só em `.env` que você escreveu.

### PowerShell

| Tarefa | Comando |
|---|---|
| Listar | `Get-ChildItem Env:` |
| Ver uma | `$env:PATH` |
| Definir na sessão | `$env:VAR = "valor"` |
| Definir para **um** comando | `$env:VAR="v"; comando` (não há prefixo como no bash) |
| Remover | `Remove-Item Env:VAR` |
| Persistir para o usuário | `[Environment]::SetEnvironmentVariable("VAR","v","User")` |
| Persistir para a máquina | `[Environment]::SetEnvironmentVariable("VAR","v","Machine")` (exige admin) |

### CMD (legado)

```cmd
set VAR=valor          :: sessão atual
setx VAR valor         :: persistente — só vale em janelas NOVAS
echo %VAR%
```

---

## 2. Sintaxe do arquivo `.env`

> ⚠️ **Não existe especificação oficial de `.env`.** Cada biblioteca implementa o seu
> dialeto, e eles **divergem** em aspas, multilinha e expansão. O que segue é o
> subconjunto que funciona igual em praticamente todas. Detalhes e divergências:
> [12-formato-dotenv.md](12-formato-dotenv.md).

```bash
# comentário de linha inteira

# --- básico: o subconjunto seguro ---
CHAVE=valor
PORT=3000
DEBUG=false

# --- espaços ao redor do = ---
# a maioria aceita, algumas não. NÃO USE.
CHAVE = valor        # ⚠️ evite

# --- valor com espaço: aspas obrigatórias ---
MENSAGEM="olá mundo"

# --- valor com # : aspas obrigatórias, senão vira comentário ---
SENHA="abc#123"

# --- aspas simples: SEM interpolação, na maioria das libs ---
LITERAL='sem $expansao'

# --- expansão: NÃO é universal ---
BASE=https://api.exemplo.com
URL=${BASE}/v1        # funciona: python-dotenv, phpdotenv, dotenv+dotenv-expand
                      # NÃO funciona: --env-file nativo do Node

# --- multilinha (chave privada): suportado por dotenv, python-dotenv, phpdotenv ---
CHAVE_PRIVADA="-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBg...
-----END PRIVATE KEY-----"

# --- prefixo export: aceito por várias libs, e torna o arquivo "sourceável" ---
export API_KEY=abc
```

### Tabela de compatibilidade

| Recurso | Node `--env-file` | `dotenv` (Node) | `python-dotenv` | `phpdotenv` |
|---|:---:|:---:|:---:|:---:|
| Comentário `#` | ✅ | ✅ | ✅ | ✅ |
| Aspas duplas | ✅ | ✅ | ✅ | ✅ |
| Aspas simples (literal) | ✅ | ✅ | ✅ | ✅ |
| Multilinha entre aspas | ✅ | ✅ | ✅ | ✅ |
| `export ` no início | ✅ | ✅ | ✅ | ✅ |
| Expansão `${VAR}` | ❌ | só com `dotenv-expand` | ✅ | ✅ |
| Sobrescrever variável já existente | ❌ | só com `override:true` | só com `override=True` | só `createMutable` |
| Arquivo ausente | erro (use `--env-file-if-exists`) | silencioso | silencioso | `safeLoad()` silencioso |

**Regra de sobrevivência:** escreva o `.env` no subconjunto que funciona em todos —
`CHAVE=valor`, sem espaços, sem expansão, aspas só quando indispensável.

---

## 3. Ler variável no código, por linguagem

| Linguagem | Ler | Com padrão | Listar tudo |
|---|---|---|---|
| **Node** | `process.env.VAR` | `process.env.VAR ?? 'padrão'` | `process.env` |
| **Python** | `os.environ['VAR']` (KeyError se faltar) | `os.getenv('VAR', 'padrão')` | `os.environ` |
| **PHP** | `getenv('VAR')` ou `$_ENV['VAR']` | `getenv('VAR') ?: 'padrão'` | `getenv()` |
| **Java** | `System.getenv("VAR")` | `System.getenv().getOrDefault("VAR","p")` | `System.getenv()` |
| **Go** | `os.Getenv("VAR")` | `os.LookupEnv("VAR")` devolve `(valor, existe)` | `os.Environ()` |
| **Ruby** | `ENV['VAR']` | `ENV.fetch('VAR','padrão')` | `ENV` |
| **C#/.NET** | `Environment.GetEnvironmentVariable("VAR")` | `?? "padrão"` | `Environment.GetEnvironmentVariables()` |
| **Rust** | `std::env::var("VAR")` → `Result` | `.unwrap_or("p".into())` | `std::env::vars()` |
| **Bash** | `$VAR` | `${VAR:-padrão}` | `printenv` |

**Diferença que morde:** `os.environ['X']` (Python) **lança exceção** se faltar;
`process.env.X` (Node) devolve `undefined` silenciosamente. A primeira falha rápido —
é a melhor. Em Node, implemente a falha rápida você mesmo
(ver [06-exemplos.md #3](06-exemplos.md)).

**Cuidado em PHP:** `getenv()` e `$_ENV` **não são a mesma coisa**.
`$_ENV` só é preenchido se `variables_order` no `php.ini` incluir `E` — e a
configuração padrão de muitas distribuições é `GPCS`, **sem o E**. Detalhe em
[16-php.md](16-php.md).

---

## 4. Carregar um `.env`, por linguagem

| Plataforma | Sem biblioteca | Com biblioteca |
|---|---|---|
| **Node ≥ 20.6** | `node --env-file=.env app.js` | `import 'dotenv/config'` |
| **Node ≥ 22.9** | `node --env-file-if-exists=.env app.js` (não falha se faltar) | `require('dotenv').config({path:'/abs/.env'})` |
| **Node ≥ 21.7 (no código)** | `process.loadEnvFile('.env')` | — |
| **Python** | — | `from dotenv import load_dotenv; load_dotenv()` |
| **Python (tipado)** | — | `pydantic_settings.BaseSettings` com `env_file=".env"` |
| **PHP** | — | `Dotenv\Dotenv::createImmutable(__DIR__)->safeLoad()` |
| **Laravel / Symfony** | já vem carregado | `php artisan config:cache` em produção |
| **Java/Spring** | `application.yml` com `${VAR}` | `spring-dotenv` |
| **Go** | — | `github.com/joho/godotenv` |
| **Ruby/Rails** | — | gem `dotenv-rails` |
| **Qualquer uma, via shell** | `set -a; . ./.env; set +a; ./app` | — |
| **Qualquer uma, via `env`** | `env $(grep -v '^#' .env \| xargs) ./app` | ⚠️ quebra com espaços no valor |

Flags relevantes do Node:

| Flag | Desde | O que faz |
|---|---|---|
| `--env-file=.env` | 20.6.0 | carrega; **erro** se o arquivo não existir |
| `--env-file-if-exists=.env` | 22.9.0 | carrega se existir; ignora se não — **o certo em produção** |
| `--env-file` repetido | 20.6.0 | vários arquivos; o **último** vence entre eles |
| `process.loadEnvFile(path)` | 21.7.0 | mesma coisa, chamado de dentro do código |

---

## 5. Injetar variáveis no processo em produção

Referência rápida; o raciocínio está em [30-entrega-em-producao.md](30-entrega-em-producao.md).

### systemd

```ini
# /etc/systemd/system/minha-app.service
[Service]
Environment="PORT=8080"
Environment="NODE_ENV=production"
EnvironmentFile=/etc/minha-app/env          # falha se faltar
EnvironmentFile=-/etc/minha-app/env.local   # o "-" torna opcional
ExecStart=/usr/bin/node /opt/minha-app/src/app.js
User=appuser
```

| Comando | O que faz |
|---|---|
| `sudo systemctl daemon-reload` | recarrega a unit depois de editá-la — **sempre** |
| `sudo systemctl restart minha-app` | reinicia (só assim as variáveis novas valem) |
| `systemctl show minha-app -p Environment` | mostra as variáveis **da unit** |
| `sudo cat /proc/$(pgrep -f minha-app)/environ \| tr '\0' '\n'` | mostra o ambiente **real** do processo |

⚠️ O `EnvironmentFile` do systemd **não é um shell**: `VAR=$OUTRA` não expande, e
aspas são interpretadas de forma própria. Uma linha por variável, sem `export`.

### Docker

| Tarefa | Comando |
|---|---|
| Uma variável | `docker run -e PORT=8080 img` |
| Repassar do shell atual | `docker run -e TOKEN img` (sem `=`, pega do host) |
| Arquivo | `docker run --env-file ./prod.env img` |
| Segredo em arquivo (melhor) | `docker run -v /run/secrets:/run/secrets:ro -e DB_PASSWORD_FILE=/run/secrets/db img` |
| Ver o que a imagem já traz | `docker inspect -f '{{json .Config.Env}}' img` |
| Ver o de um contêiner rodando | `docker exec container printenv` |

### Compose

```yaml
services:
  app:
    image: minha-app
    environment:
      PORT: "8080"
      DB_PASSWORD_FILE: /run/secrets/db_password
    env_file:
      - path: ./.env
        required: false          # Compose v2.24+
    secrets:
      - db_password

secrets:
  db_password:
    file: ./secrets/db_password.txt
```

### PaaS

| Plataforma | Comando |
|---|---|
| Heroku | `heroku config:set CHAVE=valor -a app` |
| Vercel | `vercel env add NOME production` |
| Netlify | `netlify env:set NOME valor` |
| Render / Railway / Fly | painel, ou `fly secrets set CHAVE=valor` |
| Cloud Run | `gcloud run deploy --set-env-vars K=V --set-secrets K2=secret:latest` |
| AWS Lambda | `aws lambda update-function-configuration --environment 'Variables={K=V}'` |

---

## 6. Docker e Compose

| Preciso… | Faça |
|---|---|
| Passar segredo para o **build** | `docker build --secret id=npmrc,src=$HOME/.npmrc .` e no Dockerfile `RUN --mount=type=secret,id=npmrc ...` |
| **Nunca** | `ARG TOKEN` + `ENV TOKEN` — fica gravado na camada da imagem, para sempre |
| Ver se vazei segredo numa imagem | `docker history --no-trunc img` e `dive img` |
| Segredo em runtime, jeito bom | `secrets:` do Compose/Swarm → aparece como arquivo em `/run/secrets/<nome>` |
| Ler esse arquivo no app | padrão `VAR_FILE` — ver [06-exemplos.md #7](06-exemplos.md) |

---

## 7. Kubernetes

```bash
kubectl create secret generic app-secrets \
  --from-literal=DB_PASSWORD='senha' \
  --from-file=./chave.pem
```

```yaml
envFrom:
  - secretRef: { name: app-secrets }
# ou, uma a uma:
env:
  - name: DB_PASSWORD
    valueFrom:
      secretKeyRef: { name: app-secrets, key: DB_PASSWORD }
# ou como arquivo montado (preferível: permite rotação sem reiniciar o pod)
volumeMounts:
  - { name: secrets, mountPath: /etc/secrets, readOnly: true }
```

| Comando | Nota |
|---|---|
| `kubectl get secret app-secrets -o jsonpath='{.data.DB_PASSWORD}' \| base64 -d` | **base64 não é criptografia** |
| `kubectl auth can-i get secrets` | quem consegue ler consegue ler **tudo** do namespace |

🚨 **Secret do Kubernetes é base64, não criptografia.** Sem `EncryptionConfiguration`
no `kube-apiserver`, o valor está em texto legível no etcd e em qualquer backup dele.
Desde o Kubernetes 1.28 o KMS v1 está obsoleto e desde o 1.29 vem desativado por
padrão — **use KMS v2**. Detalhes em [30-entrega-em-producao.md §6](30-entrega-em-producao.md).

---

## 8. CI/CD

### GitHub Actions

```yaml
steps:
  - name: Deploy
    env:
      API_TOKEN: ${{ secrets.API_TOKEN }}     # do cofre do repositório
    run: ./deploy.sh
```

| Tarefa | Como |
|---|---|
| Definir segredo | Settings → Secrets and variables → Actions, ou `gh secret set NOME` |
| Segredo de organização | reaproveitado por vários repositórios |
| Variável **não** secreta | `vars.NOME` (não é mascarada nos logs) |
| Mascarar valor calculado em runtime | `echo "::add-mask::$VALOR"` |
| **Sem segredo de longa duração (melhor)** | OIDC: `permissions: id-token: write` + role da nuvem |
| Ambiente com aprovação manual | `environment: production` com reviewers |

⚠️ **`pull_request` de fork não recebe segredos** — é proteção, não bug.
E `pull_request_target` **recebe**: nunca faça checkout do código do fork nesse
gatilho, é uma via clássica de exfiltração de segredo de CI.

---

## 9. SOPS

| Tarefa | Comando |
|---|---|
| Criptografar no lugar | `sops --encrypt --in-place segredos.yaml` |
| Descriptografar para a tela | `sops --decrypt segredos.yaml` |
| Editar (decifra, abre editor, recifra) | `sops segredos.yaml` |
| Rodar um comando com os valores no ambiente | `sops exec-env segredos.yaml './app'` |
| Escrever num arquivo temporário e passar o caminho | `sops exec-file segredos.yaml 'app --config {}'` |
| Trocar de chave / adicionar destinatário | `sops updatekeys segredos.yaml` |
| Criptografar só o que casar com o padrão | `sops -e --encrypted-regex '^(senha\|token)$' f.yaml` |

Configuração do repositório em `.sops.yaml`:

```yaml
creation_rules:
  - path_regex: .*\.enc\.yaml$
    age: age1abc...,age1def...      # chaves públicas de quem pode decifrar
```

---

## 10. Vault / OpenBao CLI

A CLI do OpenBao é `bao`; a do Vault é `vault`. Os subcomandos são os mesmos.

| Tarefa | Comando |
|---|---|
| Apontar para o servidor | `export BAO_ADDR=https://cofre.exemplo.com` |
| Entrar | `bao login -method=userpass username=maria` |
| Gravar segredo | `bao kv put secret/minha-app DB_PASSWORD=senha` |
| Ler | `bao kv get secret/minha-app` |
| Ler só um campo (para script) | `bao kv get -field=DB_PASSWORD secret/minha-app` |
| Ler em JSON | `bao kv get -format=json secret/minha-app` |
| Versão anterior | `bao kv get -version=2 secret/minha-app` |
| Apagar (soft) / destruir | `bao kv delete` / `bao kv destroy -versions=3` |
| **Credencial dinâmica de banco** | `bao read database/creds/somente-leitura` |
| Renovar concessão | `bao lease renew <lease_id>` |
| Cifrar sem guardar (Transit) | `bao write transit/encrypt/chave plaintext=$(base64 <<< "oi")` |

O grande diferencial que justifica um cofre: **credencial dinâmica**. O Vault cria um
usuário no banco **na hora**, com validade de 1 hora, só para aquela aplicação.
Se vazar, expira sozinha. Detalhes em [40-cofres-de-segredos.md](40-cofres-de-segredos.md).

---

## 11. gitleaks

| Tarefa | Comando |
|---|---|
| Escanear histórico inteiro | `gitleaks git .` |
| Escanear só o que está para ser commitado | `gitleaks protect --staged` |
| Escanear diretório sem Git | `gitleaks dir .` |
| Relatório | `gitleaks git . -f json -r relatorio.json` |
| Regras próprias | `gitleaks git . -c .gitleaks.toml` |
| Ignorar falso positivo | comentário `# gitleaks:allow` na linha, ou `.gitleaksignore` |

---

## 12. Inspecionar e depurar

| Preciso saber… | Comando |
|---|---|
| O que o processo **realmente** recebeu | `cat /proc/<PID>/environ \| tr '\0' '\n'` |
| Idem, em macOS | `ps eww -p <PID>` |
| Qual `.env` foi carregado (Node) | `node -e "console.log(process.env)" --env-file=.env \| grep MINHA` |
| Se o `.env` tem CRLF (arquivo de Windows) | `file .env` → se disser "CRLF", rode `dos2unix .env` |
| Se há espaço invisível no fim do valor | `printenv VAR \| cat -A` → `$` marca o fim da linha |
| Quantos bytes tem o segredo | `printenv TOKEN \| wc -c` (compare com o esperado, sem imprimir o valor) |
| Comparar dois ambientes | `diff <(printenv \| sort) <(ssh servidor printenv \| sort)` |

🚨 **`/proc/<PID>/environ` é legível pelo dono do processo e pelo root.** Ou seja:
**variável de ambiente não é secreta contra quem já está na máquina como root**.
Isso é limite fundamental do modelo, não falha de implementação. Ver
[60-teoria-avancada.md §2](60-teoria-avancada.md).

---

## 13. Convenções de nomes

| Regra | Exemplo | Por quê |
|---|---|---|
| MAIÚSCULAS com `_` | `DATABASE_URL` | convenção Unix desde os anos 1970; minúsculas são reservadas por convenção para variáveis de shell |
| Prefixo da aplicação | `LOJA_DB_HOST` | evita colisão com variáveis do sistema |
| Do geral para o específico | `DB_POOL_MAX` | agrupa na listagem alfabética |
| Sufixo `_FILE` para caminho de segredo | `DB_PASSWORD_FILE` | padrão de fato em imagens Docker oficiais |
| Sufixo `_URL` para URL completa | `REDIS_URL` | um valor em vez de cinco |
| **Não** comece com dígito, não use `-` | `2FA_KEY` ❌ → `TWO_FACTOR_KEY` | `export 2FA=1` é erro de sintaxe em bash |
| Booleano explícito | `FEATURE_X=true` | e leia comparando com a string `"true"` |

**Nomes reservados que você não deve sobrescrever:** `PATH`, `HOME`, `USER`, `SHELL`,
`LANG`, `TMPDIR`, `PWD`, `TERM`, `LD_PRELOAD`, `LD_LIBRARY_PATH`, `NODE_OPTIONS`,
`PYTHONPATH`, `http_proxy`.

> 🚨 `LD_PRELOAD` e `NODE_OPTIONS` **executam código**. Se um atacante controla o
> ambiente do seu processo, ele executa código no seu processo. Por isso serviços
> que recebem variáveis de fonte não confiável precisam de **lista de permissão**,
> nunca de lista de bloqueio.

---

## 14. Obsoleto — e o que substituiu

| Prática antiga | Estado | Substituto |
|---|---|---|
| `config.php` / `settings.py` com senha, versionado | ❌ morto desde ~2012 | variáveis de ambiente |
| `dotenv` em Node só para carregar arquivo | 🟡 desnecessário em Node ≥ 20.6 | `--env-file` nativo |
| `.env` enviado por `scp` como único mecanismo | 🟡 aceitável em projeto pequeno, insuficiente em equipe | systemd `EnvironmentFile` + cofre |
| `git-crypt` | 🟡 mantido, mas parado | **SOPS + age** |
| GPG para criptografar `.env` | 🟡 funciona, é dolorido | **age** |
| Kubernetes Secret sem criptografia no etcd | ❌ inaceitável desde ~2019 | `EncryptionConfiguration` com **KMS v2** |
| KMS v1 do Kubernetes | ❌ obsoleto desde 1.28, desligado desde 1.29 | KMS v2 |
| Chave de acesso estática da AWS no CI | ❌ evitável desde 2021 | **OIDC** com role temporária |
| `docker build --build-arg TOKEN=...` | ❌ vaza na imagem | `--mount=type=secret` (BuildKit) |
| Vault sob MPL 2.0 | 🟡 congelado na 1.14 | **OpenBao** (MPL 2.0, Linux Foundation) ou Vault BUSL |
| `REACT_APP_SECRET` no front | ❌ nunca funcionou | proxy no servidor — ver [20](20-frontend-e-build-time.md) |

---

## Autoteste

1. Qual comando mostra o ambiente real de um processo já em execução no Linux?
2. Qual a diferença entre `--env-file` e `--env-file-if-exists` no Node, e qual usar em produção?
3. Por que `$_ENV` pode vir vazio em PHP mesmo com o `.env` carregado?
4. Em Compose, qual a diferença entre `environment:` e `secrets:`?
5. Por que `docker build --build-arg` não serve para segredo?
6. O que `sops exec-env` faz, e por que é melhor que `sops -d > .env`?
7. Cite duas variáveis de ambiente que **executam código** e por que isso importa.
8. Por que `pull_request` de um fork não recebe os segredos do repositório?

---

**Próximo:** [06-exemplos.md](06-exemplos.md) · Voltar ao [mapa](00-MAPA.md)
