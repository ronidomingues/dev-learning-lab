# 95 · Referências — fontes primárias, specs e onde verificar

`Nível: todos` · `Atualizado em 18/08/2026`

Tudo que foi consultado para escrever este curso, mais os lugares onde **você** deve conferir
quando os números aqui envelhecerem.

---

## 1. Documentação oficial das plataformas

Sempre a fonte final para preço e limite. **Blogs e comparativos, inclusive este material,
envelhecem; a página de preços do fornecedor, não.**

| Plataforma | Preços | Documentação |
|---|---|---|
| Render | render.com/pricing | render.com/docs (veja `/docs/free` e `/docs/regions`) |
| Railway | railway.com/pricing | docs.railway.com (`/pricing/plans`, `/reference/regions`) |
| Fly.io | fly.io/pricing | fly.io/docs (`/docs/about/pricing`, `/docs/reference/regions`) |
| Koyeb | koyeb.com/pricing | koyeb.com/docs (`/faqs/pricing`) |
| Northflank | northflank.com/pricing | northflank.com/docs |
| Cloudflare | cloudflare.com/plans | developers.cloudflare.com (workers, pages, d1, hyperdrive, r2) |
| Vercel | vercel.com/pricing | vercel.com/docs (`/limits`, `/plans/hobby`, `/limits/fair-use-guidelines`) |
| Netlify | netlify.com/pricing | docs.netlify.com (faturamento por créditos) |
| Neon | neon.com/pricing | neon.com/docs (`/introduction/regions`) |
| Supabase | supabase.com/pricing | supabase.com/docs (`/guides/platform/regions`, `/going-into-prod`) |
| Upstash | upstash.com/pricing/redis | upstash.com/docs |
| Redis Cloud | redis.io/pricing | redis.io/docs (planos Essentials) |
| Aiven | aiven.io/pricing | aiven.io/docs |
| Heroku | heroku.com/pricing | devcenter.heroku.com |
| AWS | aws.amazon.com/free | docs.aws.amazon.com |
| Google Cloud | cloud.google.com/free | cloud.google.com/docs |
| Oracle Cloud | oracle.com/cloud/free | docs.oracle.com/en-us/iaas/Content/FreeTier |
| Hetzner | hetzner.com/cloud | docs.hetzner.com |

**Páginas de status** (a primeira coisa a checar num incidente):
`status.render.com` · `status.railway.com` · `status.flyio.net` · `www.cloudflarestatus.com` ·
`www.vercel-status.com` · `status.supabase.com` · `status.neon.tech` · `status.upstash.com` ·
`health.aws.amazon.com/health/status` · `status.cloud.google.com`

---

## 2. Especificações e padrões

| Documento | O que define | Onde |
|---|---|---|
| **RFC 9110–9114** | HTTP semântica, HTTP/1.1, HTTP/2, HTTP/3, QUIC | rfc-editor.org |
| **RFC 8446** | TLS 1.3 | rfc-editor.org |
| **RFC 8555** | ACME (emissão automática de certificado) | rfc-editor.org |
| **RFC 1034 / 1035** | DNS — inclusive por que não existe CNAME no apex | rfc-editor.org |
| **RFC 6749 / 9068** | OAuth 2.0 e JWT como access token | veja [`jwt`](../jwt/00-MAPA.md) |
| **OCI Image & Runtime Spec** | o que é uma imagem de container | opencontainers.org |
| **CNCF Landscape** | o mapa (assustador) do ecossistema | landscape.cncf.io |
| **OpenTelemetry** | traces, métricas e logs padronizados | opentelemetry.io |
| **The Twelve-Factor App** | o que torna uma aplicação hospedável | 12factor.net |
| **RESP** (Redis Serialization Protocol) | o protocolo do Redis/Valkey | redis.io/docs/reference/protocol-spec |
| **PostgreSQL Frontend/Backend Protocol** | o protocolo do Postgres | postgresql.org/docs/current/protocol.html |

---

## 3. Papers e artigos citados neste curso

- Gilbert, S.; Lynch, N. — *Brewer's Conjecture and the Feasibility of Consistent, Available,
  Partition-Tolerant Web Services*. ACM SIGACT News, 2002.
- Abadi, D. — *Consistency Tradeoffs in Modern Distributed Database System Design*.
  IEEE Computer, 2012. (PACELC)
- Dean, J.; Barroso, L. A. — *The Tail at Scale*. Communications of the ACM, 2013.
- Vattani, A.; Chierichetti, F.; Lowenstein, K. — *Optimal Probabilistic Cache Stampede
  Prevention*. VLDB, 2015.
- Agache, A. et al. — *Firecracker: Lightweight Virtualization for Serverless Applications*.
  USENIX NSDI, 2020.
- Kleppmann, M. — *How to do distributed locking*, 2016 (e a resposta de Salvatore Sanfilippo).
- Stonebraker, M.; Rowe, L. — *The Design of POSTGRES*, 1986. (a origem do processo por conexão)

---

## 4. Legislação e regulação

| Norma | O que trata | Relevância |
|---|---|---|
| **Lei nº 13.709/2018 (LGPD)** | proteção de dados pessoais no Brasil | arts. 16, 18, 33–36, 37, 46, 48 |
| **Resolução CD/ANPD nº 19/2024** | Regulamento de Transferência Internacional de Dados; cláusulas-padrão contratuais | permite hospedar fora do Brasil com base contratual correta |
| **Regulamento (UE) 2023/2854 (Data Act)** | dados e serviços de computação em nuvem | **art. 29: fim das taxas de troca de provedor em 12/01/2027** |
| **Regulamento (UE) 2016/679 (GDPR)** | proteção de dados na UE | referência dos DPAs que você vai assinar |
| **Marco Civil da Internet (Lei nº 12.965/2014)** | guarda de registros de acesso | prazos de retenção de log |

---

## 5. Código-fonte que vale ler

| Projeto | Por quê |
|---|---|
| **PostgreSQL** (`git.postgresql.org`) | `src/backend/storage/` e `src/backend/access/` — como durabilidade é implementada |
| **Valkey** (`github.com/valkey-io/valkey`) | base de código pequena e legível; `t_string.c` e `expire.c` são um bom começo |
| **Firecracker** (`github.com/firecracker-microvm/firecracker`) | microVM em ~50 mil linhas de Rust |
| **Coolify** (`github.com/coollabsio/coolify`) | como uma PaaS é construída sobre Docker |
| **Dokploy** (`github.com/dokploy/dokploy`) | a mesma coisa, mais simples |
| **Caddy** (`github.com/caddyserver/caddy`) | TLS automático feito direito |
| **PgBouncer** (`github.com/pgbouncer/pgbouncer`) | pooling de conexões em C, pequeno e claro |

---

## 6. Pessoas e publicações para acompanhar

**Blogs de engenharia com escrita técnica de qualidade** (não são material de marketing):
- **Fly.io Blog** — redes, Firecracker, distribuição. Provavelmente a melhor escrita técnica
  entre plataformas.
- **Cloudflare Blog** — semana de aniversário (setembro) traz os lançamentos do ano.
- **Neon Blog** — Postgres serverless, separação computação/armazenamento.
- **Render / Railway changelogs** — para saber o que mudou de preço e limite.
- **Brendan Gregg** (brendangregg.com) — desempenho de sistemas.
- **Martin Kleppmann** (martin.kleppmann.com) — sistemas distribuídos.
- **Charity Majors** (charity.wtf) — observabilidade e operação, com opinião forte.
- **Julia Evans** (jvns.ca) — explicações ilustradas de rede, Linux e depuração.
- **Fabio Akita** (akitaonrails.com) — contexto e história, em português.
- **Xavki** (xavki.blog) — DevOps em francês, com profundidade.

**Agregadores úteis:** Hacker News (`news.ycombinator.com`), `lobste.rs`, `r/devops`,
`r/selfhosted`, `dev.to`, e o `getdeploying.com` para comparar plataformas.

---

## 7. Ferramentas de verificação

Coisas para rodar quando você quiser conferir um número em vez de acreditar:

```bash
dig +short seu-dominio.com.br            # DNS resolvido
dig +trace seu-dominio.com.br            # delegação inteira
curl -sI https://seu-dominio.com.br      # status e cabeçalhos
curl -sw '%{time_namelookup} %{time_connect} %{time_appconnect} %{time_total}\n' -o /dev/null https://...
mtr --report seu-host.com                # latência salto a salto
nc -zv host 5432                         # a porta está alcançável?
openssl s_client -connect host:443 -servername host   # certificado
autocannon -c 50 -d 30 -l URL            # carga e percentis
k6 run carga.js                          # carga com critérios de aprovação
psql "$DATABASE_URL" -c "SELECT version();"
redis-cli --tls -u "$REDIS_URL" INFO server
docker compose config                     # valida o compose antes de subir
render blueprints validate                # valida o render.yaml
flyctl config validate                    # valida o fly.toml
```

---

## 8. O que foi e o que não foi verificado ao escrever este curso

**Verificado com execução real** (Ubuntu 22.04.5, Node v24.18.0, x86_64, 18/08/2026):
- O [`07-projeto-modelo/`](07-projeto-modelo/README.md): **40 testes executados, 40 aprovados**;
  servidor no ar em modo memória; `/health`, `POST /api/links` e `/api/stats` conferidos por
  `curl`; encerramento gracioso por `SIGTERM` observado no log.
- Versões das ferramentas locais (git 2.34.1, Node v24.18.0, npm 12.0.1, Docker 29.1.3,
  Compose v5.5.0, curl 7.81.0, jq 1.6, Python 3.10.12).
- A mensagem de erro literal
  `Error: You must install at least one postgresql-client-<version> package`, reproduzida
  nesta máquina.

**Pesquisado na web em 18/08/2026** (não executado): todos os preços, limites de camada
gratuita, regiões, versões atuais, cursos e certificações. As fontes estão no rodapé de cada
arquivo.

**Não verificado, e declarado como tal:**
- Nenhum deploy real foi feito em Render, Railway, Fly.io, Koyeb, Northflank, Cloudflare,
  Vercel, Netlify, Neon, Supabase ou Upstash durante a escrita.
- O `Dockerfile` e o `compose.yaml` do projeto-modelo **não foram construídos**: o daemon do
  Docker não estava acessível no ambiente de escrita
  (`permission denied ... /var/run/docker.sock`).
- Os manifestos `render.yaml` e `fly.toml` seguem o esquema documentado, mas **não foram
  validados** com `render blueprints validate` nem `flyctl config validate`.
- Preços da Hetzner: a página oficial não expôs os valores ao ser consultada; os números
  vieram de agregadores e estão marcados como **aproximados** em
  [`20`](20-catalogo-backend-paas.md) e [`80`](80-custos-e-licencas.md).
- Latências para o Brasil são **ordens de grandeza típicas**, não medições feitas aqui.

---

## 9. Quando reavaliar este material

| Arquivo | Frequência | Gatilho |
|---|---|---|
| [`20`](20-catalogo-backend-paas.md), [`25`](25-catalogo-postgresql.md), [`30`](30-catalogo-redis.md), [`35`](35-catalogo-frontend.md), [`80`](80-custos-e-licencas.md) | **6 meses** | qualquer anúncio de mudança de preço |
| [`65`](65-estado-da-arte.md) | 6 meses | — |
| [`03`](03-instalacao.md), [`85`](85-cursos-e-certificacoes.md) | 12 meses | nova versão maior de Node, Docker ou PostgreSQL |
| [`45`](45-brasil-latencia-e-lgpd.md) | 12 meses | nova resolução da ANPD; abertura de região no Brasil |
| [`10`](10-fundamentos.md), [`11`](11-historia.md), [`12`](12-anatomia-de-um-deploy.md), [`60`](60-teoria-avancada.md) | raramente | — |

---

## Autoteste

1. Qual é a única fonte confiável para preço de plataforma, e por quê?
2. Qual RFC explica por que não existe `CNAME` no domínio raiz?
3. Qual artigo de 2013 explica por que o p99 importa mais que a média?
4. Que resolução da ANPD regula a transferência internacional de dados, e de quando é?
5. O que este curso **não** verificou, e por quê?
6. Quais arquivos devem ser reavaliados em seis meses, e o que dispara a reavaliação?
