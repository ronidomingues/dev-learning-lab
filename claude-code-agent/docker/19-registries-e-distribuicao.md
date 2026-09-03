# 19 · Registries, distribuição e cadeia de suprimentos

`Nível: intermediário → avançado` · `Última atualização: 11/08/2026`

Onde as imagens moram, como viajam e como você garante que a que roda em produção é a que você
construiu.

---

## 1. Como um registry funciona

Um registry OCI é uma API HTTP com um punhado de endpoints. Você pode falar com ele por `curl`.

```bash
# Token anônimo para uma imagem pública do Docker Hub
TOKEN=$(curl -s "https://auth.docker.io/token?service=registry.docker.io&scope=repository:library/alpine:pull" | jq -r .token)

# 1) Listar tags
curl -s -H "Authorization: Bearer $TOKEN" \
  https://registry-1.docker.io/v2/library/alpine/tags/list | jq

# 2) Buscar o manifesto (o índice multi-arch)
curl -s -H "Authorization: Bearer $TOKEN" \
  -H "Accept: application/vnd.oci.image.index.v1+json" \
  https://registry-1.docker.io/v2/library/alpine/manifests/3.20 | jq

# 3) Baixar uma camada (blob), por digest
curl -sL -H "Authorization: Bearer $TOKEN" \
  https://registry-1.docker.io/v2/library/alpine/blobs/sha256:<digest> -o camada.tar.gz
```

O protocolo (OCI Distribution Spec) tem essencialmente três recursos:

| Caminho | O que é |
|---|---|
| `/v2/<nome>/tags/list` | Tags do repositório |
| `/v2/<nome>/manifests/<ref>` | Manifesto, por tag ou digest |
| `/v2/<nome>/blobs/<digest>` | Um blob: camada ou config |

**Por que um `pull` costuma ser rápido:** o cliente pede o manifesto, compara os digests das
camadas com o que já tem no disco e **baixa somente o que falta**. Se você já tem
`node:22-alpine`, uma imagem sua baseada nela transfere só as suas camadas.

---

## 2. Os registries, comparados

| Registry | Endereço | Grátis para | Observações |
|---|---|---|---|
| **Docker Hub** | `docker.io` | Público ilimitado; 1 repositório privado no plano gratuito | **Limite de pull**: 10/h sem login, 100/h com conta gratuita |
| **GHCR** | `ghcr.io` | Público ilimitado; privado na cota do GitHub | Integração direta com Actions via `GITHUB_TOKEN` |
| **Quay.io** | `quay.io` | Público ilimitado | Escaneamento embutido (Clair) |
| **GitLab Registry** | `registry.gitlab.com` | Na cota do projeto | Integrado ao CI do GitLab |
| **AWS ECR** | `*.dkr.ecr.*.amazonaws.com` | Camada gratuita limitada | Cobra armazenamento e transferência |
| **Google Artifact Registry** | `*-docker.pkg.dev` | Camada gratuita limitada | Substituiu o GCR |
| **Azure ACR** | `*.azurecr.io` | Não | Três níveis de serviço |
| **Harbor** | auto-hospedado | Livre (Apache 2.0) | Replicação, políticas, escaneamento, quarentena |
| **`registry:2`** | auto-hospedado | Livre | Mínimo, sem interface |
| **Zot** | auto-hospedado | Livre | Registry OCI puro, leve |

### O limite do Docker Hub e o que fazer

Desde **1º de abril de 2025**:

| Situação | Limite |
|---|---|
| Sem autenticação | **10 pulls/hora**, por IP |
| Conta gratuita autenticada | **100 pulls/hora** |
| Pro / Team / Business | Ilimitado, sob uso justo |

O impacto real é em CI: um runner em IP compartilhado consome os 10 pulls em minutos e o
pipeline quebra com `toomanyrequests`.

**As quatro mitigações, em ordem de eficácia:**

```bash
# 1) Autentique no CI (mais barato e imediato)
echo "$DOCKERHUB_TOKEN" | docker login -u "$DOCKERHUB_USER" --password-stdin

# 2) Espelho puxador (pull-through cache) na sua rede
docker run -d --name espelho -p 5000:5000 \
  -e REGISTRY_PROXY_REMOTEURL=https://registry-1.docker.io \
  -v espelho-dados:/var/lib/registry \
  registry:2
# e no /etc/docker/daemon.json:
# { "registry-mirrors": ["http://espelho.interno:5000"] }

# 3) Copie as imagens de que depende para o SEU registry
skopeo copy docker://docker.io/library/postgres:16 docker://ghcr.io/minhaorg/postgres:16

# 4) Use registries alternativos
#    public.ecr.aws/docker/library/postgres:16   · quay.io/...   · ghcr.io/...
```

---

## 3. Autenticação

```bash
echo "$TOKEN" | docker login -u USUARIO --password-stdin
echo "$TOKEN" | docker login ghcr.io -u USUARIO --password-stdin
aws ecr get-login-password --region us-east-1 | docker login --password-stdin \
  --username AWS 123456789.dkr.ecr.us-east-1.amazonaws.com
gcloud auth configure-docker us-central1-docker.pkg.dev
```

**Nunca use a senha da conta.** Use *Personal Access Token* com escopo mínimo — ele pode ser
revogado isoladamente e não dá acesso ao restante da conta.

### Onde a credencial fica, e o risco

```bash
cat ~/.docker/config.json
# { "auths": { "https://index.docker.io/v1/": { "auth": "dXNlcjp0b2tlbg==" } } }
echo "dXNlcjp0b2tlbg==" | base64 -d
# user:token   ← base64 NÃO é criptografia
```

Instale um *credential helper*:

| Sistema | Helper |
|---|---|
| Linux | `docker-credential-pass` (GPG) ou `docker-credential-secretservice` |
| macOS | `docker-credential-osxkeychain` (padrão com o Desktop) |
| Windows | `docker-credential-wincred` |

```json
// ~/.docker/config.json
{ "credsStore": "pass" }
```

---

## 4. Estratégia de tags

**A regra:** `latest` não significa "mais recente". É apenas a tag padrão quando nenhuma é dada,
e é reescrita a cada publicação. Em produção, é a causa de "ontem funcionava".

A estratégia que funciona:

```bash
IMG=ghcr.io/org/app
SHA=$(git rev-parse --short HEAD)
VER=$(cat VERSION)          # ex.: 1.4.2

docker build \
  -t $IMG:$VER \            # imutável, semântico  → o que produção referencia
  -t $IMG:1.4 \             # minor móvel          → recebe correções de patch
  -t $IMG:1 \               # major móvel          → recebe features compatíveis
  -t $IMG:sha-$SHA \        # rastreável ao commit → o que o CI usa
  -t $IMG:latest \          # conveniência de dev  → NUNCA em produção
  .
```

E o **deploy sempre por digest**:

```bash
DIGEST=$(docker buildx imagetools inspect $IMG:$VER --format '{{.Manifest.Digest}}')
docker run $IMG@$DIGEST
```

Por quê: tag é ponteiro mutável; digest é o conteúdo. Fazer deploy por tag é fazer deploy do
"que estiver lá quando o servidor puxar" — e é assim que um ataque de reescrita de tag chega à
produção.

Automatize com `docker/metadata-action` (exemplo completo em
[06-exemplos.md](06-exemplos.md#12-produção--pipeline-de-ci-completo-no-github-actions)).

---

## 5. Cadeia de suprimentos: o assunto de 2026

A pergunta deixou de ser "esta imagem funciona?" e passou a ser **"esta imagem é a que eu acho
que é, construída a partir do que eu acho, sem componente vulnerável conhecido?"**.

### As quatro perguntas e as quatro respostas

| Pergunta | Artefato | Ferramenta |
|---|---|---|
| O que tem dentro? | **SBOM** (*Software Bill of Materials*) | `syft`, `docker buildx --sbom` |
| Tem vulnerabilidade conhecida? | Relatório de escaneamento | `trivy`, `grype`, `docker scout` |
| Quem construiu, a partir de quê? | **Atestado de proveniência (SLSA)** | `--provenance=true` |
| É mesmo de quem diz ser? | **Assinatura** | `cosign` |

### SBOM

```bash
docker buildx build --sbom=true --provenance=true -t org/app:1.0 --push .
docker buildx imagetools inspect org/app:1.0 --format '{{json .SBOM}}' | jq '.SPDX.packages | length'

# Ou gere separadamente
syft org/app:1.0 -o spdx-json > sbom.json
syft org/app:1.0 -o cyclonedx-json > sbom-cdx.json
```

Formatos: **SPDX** (Linux Foundation, ISO) e **CycloneDX** (OWASP). Ambos são aceitos; escolha um
e seja consistente.

Por que importa: quando sai um Log4Shell, a pergunta "quais das nossas 400 imagens têm log4j
2.14?" precisa ser respondida em minutos, não em semanas. Com SBOM, é uma consulta.

### Escaneamento

```bash
trivy image --severity HIGH,CRITICAL --ignore-unfixed org/app:1.0
grype org/app:1.0
docker scout cves org/app:1.0
docker scout recommendations org/app:1.0   # sugere base menos vulnerável
```

**Sobre `--ignore-unfixed`:** falhar o pipeline por uma CVE que **não tem correção publicada**
só ensina a equipe a ignorar o scanner. Falhe pelo que é corrigível; monitore o resto.

**Sobre falsos positivos:** scanners olham versões de pacote, não uso. Uma CVE numa biblioteca
que seu código nunca chama continua sendo reportada. Use `.trivyignore` com **justificativa e
data de revisão** — nunca um ignore silencioso e eterno.

### Assinatura com cosign (keyless)

```bash
# Assina usando OIDC — SEM chave privada para vazar
cosign sign --yes ghcr.io/org/app@sha256:abc...

# Verifica: exige que tenha sido construída por AQUELE workflow daquele repositório
cosign verify ghcr.io/org/app@sha256:abc... \
  --certificate-identity-regexp "https://github.com/org/app/.github/workflows/.*" \
  --certificate-oidc-issuer "https://token.actions.githubusercontent.com"
```

O modelo *keyless* usa o Fulcio (CA de curta duração) e o Rekor (log público de transparência,
somente-anexação) do projeto Sigstore. Você troca "guardar uma chave privada para sempre" por
"provar identidade no momento da assinatura" — que é um problema muito mais fácil de operar bem.

### Aplicação de política

De nada adianta assinar se ninguém verifica. Em Kubernetes, um *admission controller*:

```yaml
# Kyverno
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: exigir-assinatura
spec:
  validationFailureAction: Enforce
  rules:
    - name: verificar-imagens
      match:
        resources: { kinds: [Pod] }
      verifyImages:
        - imageReferences: ["ghcr.io/org/*"]
          attestors:
            - entries:
                - keyless:
                    subject: "https://github.com/org/*"
                    issuer: "https://token.actions.githubusercontent.com"
```

Alternativas: Sigstore Policy Controller, OPA Gatekeeper, Notary v2/Notation.

---

## 6. Registry próprio

### Mínimo, para laboratório

```bash
docker run -d --name registry -p 5000:5000 --restart unless-stopped \
  -v registry-dados:/var/lib/registry registry:2

docker tag app:1.0 localhost:5000/app:1.0
docker push localhost:5000/app:1.0
curl -s localhost:5000/v2/_catalog | jq
```

Sem TLS, só funciona via `localhost` ou com `insecure-registries` no daemon — que desliga a
verificação e só é aceitável em rede isolada de laboratório.

### Com TLS e autenticação

```yaml
services:
  registry:
    image: registry:2
    environment:
      REGISTRY_AUTH: htpasswd
      REGISTRY_AUTH_HTPASSWD_REALM: "Registry"
      REGISTRY_AUTH_HTPASSWD_PATH: /auth/htpasswd
      REGISTRY_STORAGE_DELETE_ENABLED: "true"   # sem isto, não dá para apagar nada
    volumes:
      - ./auth:/auth:ro
      - registry-dados:/var/lib/registry
    networks: [interna]

  proxy:
    image: caddy:2-alpine        # termina o TLS com certificado automático
    ports: ["443:443"]
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile:ro
      - caddy-dados:/data
    networks: [interna, borda]
```

```bash
docker run --rm --entrypoint htpasswd httpd:2 -Bbn usuario senha > auth/htpasswd
```

### Harbor, quando a organização cresce

Harbor acrescenta o que falta no `registry:2`: interface web, projetos com controle de acesso,
replicação entre regiões, escaneamento com quarentena automática, políticas de retenção,
assinatura, proxy cache e quotas. É o padrão de fato para registry auto-hospedado corporativo.

### Retenção — o custo que ninguém prevê

Registries crescem sem parar. Cada build de CI deixa uma imagem.

```bash
# Apagar por digest (exige REGISTRY_STORAGE_DELETE_ENABLED=true)
curl -X DELETE https://registry/v2/app/manifests/sha256:abc...
# E depois a coleta de lixo, que só roda com o registry parado ou em modo somente leitura:
docker exec registry bin/registry garbage-collect /etc/docker/registry/config.yml
```

Política sensata: manter todas as tags semânticas, os últimos N builds por branch, e apagar
`sha-*` com mais de 30 dias. ECR, GAR, ACR e Harbor têm regras declarativas de ciclo de vida —
configure-as **no primeiro dia**, não quando a conta chegar.

---

## 7. Transferir imagens sem registry

```bash
# Máquina sem rede (air-gapped)
docker save app:1.0 | gzip > app.tar.gz
# ... transfira por pendrive ...
gunzip -c app.tar.gz | docker load

# Direto por SSH
docker save app:1.0 | ssh usuario@destino 'docker load'

# skopeo: copia entre registries SEM baixar para o daemon local
skopeo copy docker://docker.io/library/nginx:alpine docker://registry.interno/nginx:alpine
skopeo copy --all docker://origem/app:1.0 docker://destino/app:1.0   # --all = todas as arquiteturas
skopeo inspect docker://nginx:alpine       # inspeciona sem baixar
```

`skopeo` é subutilizado e resolve bem três problemas: espelhar imagens para registry interno,
inspecionar sem `pull`, e copiar preservando digest e assinaturas.

---

## 8. Boas práticas de distribuição

1. **Deploy por digest**, sempre. Tag serve para humano.
2. **Um registry por ambiente**, ou ao menos projetos separados com permissões distintas.
3. **Espelhe as imagens de terceiros** de que você depende. Elas podem sumir — já sumiram.
4. **Assine no CI e verifique na admissão.** Assinar sem verificar é teatro.
5. **SBOM e proveniência em todo build de produção.** Custa uma flag.
6. **Retenção configurada desde o primeiro dia.**
7. **Escaneie no push e periodicamente** — CVEs novas aparecem em imagens antigas que não
   mudaram.
8. **Nunca publique imagem construída na máquina de alguém.** Só o CI publica; assim há
   proveniência.

---

## Autoteste

1. Quais são os três recursos essenciais da API de um registry OCI?
2. Por que um `docker pull` de uma imagem sua costuma transferir pouco, mesmo sendo grande?
3. Quais são os limites de pull do Docker Hub hoje, e quais são as quatro mitigações?
4. Por que `latest` em produção é um problema, e o que usar no lugar?
5. Explique a diferença entre tag e digest no contexto de um ataque de reescrita de tag.
6. Quais são as quatro perguntas de cadeia de suprimentos e o artefato que responde cada uma?
7. Por que a assinatura *keyless* do cosign é operacionalmente melhor que uma chave privada?
8. Qual é o problema de assinar imagens sem um *admission controller* verificando?
9. Por que `--ignore-unfixed` no scanner é pragmatismo e não relaxamento?
10. Você precisa espelhar 50 imagens públicas para um registry interno sem encher o disco local.
    Qual ferramenta usa e por quê?

---

### Fontes consultadas (11/08/2026)

- [Docker Docs — Usage and rate limits](https://docs.docker.com/docker-hub/usage/) e [GitLab Support — Docker Hub rate limiting](https://support.gitlab.com/hc/en-us/articles/20028360858140-Docker-Hub-rate-limiting-impacts-GitLab-pipelines) — 10/hora sem autenticação, 100/hora com conta gratuita, vigente desde 01/04/2025
