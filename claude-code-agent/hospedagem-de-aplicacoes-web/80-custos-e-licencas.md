# 80 · Custos e licenças

`Nível: todos` · `**Preços consultados na web em 18/08/2026**`
`Câmbio usado: US$ 1 ≈ R$ 5,20 · € 1 ≈ R$ 6,10 (18/08/2026)`
`Some 3,5% de IOF e o spread do seu cartão em compras internacionais.`

> **Preço sem data é desinformação.** Todos os valores aqui têm a data acima. Confirme antes
> de decidir — este setor reajusta várias vezes ao ano (a Hetzner reajustou **duas vezes**
> só em 2026).

---

## 1. Tabela mestra — camadas gratuitas

| Serviço | O que dá de graça | Prazo | Cartão? | Onde acaba |
|---|---|---|---|---|
| **Cloudflare Workers** | 100 mil req/dia; 10 ms de CPU/invocação | permanente | não | CPU pesada; Node incompleto |
| **Cloudflare Pages** | estáticos **ilimitados**; funções compartilham a cota do Workers | permanente | não | builds mensais; 20 mil arquivos |
| **Cloudflare D1** | 5 mi linhas lidas/dia; 100 mil escritas/dia; 5 GB | permanente | não | escrita e tamanho |
| **Cloudflare Hyperdrive** | 100 mil consultas/dia | permanente | não | volume |
| **Cloudflare R2** | 10 GB; **egress zero** | permanente | não | operações de classe A |
| **Render** | 750 h/mês; dorme em 15 min | permanente | não | o sono; sem disco; sem shell |
| **Render Postgres** | 1 GB | **expira em 30 dias** | não | o prazo |
| **Render Key Value** | 25 MB, **sem persistência** | permanente | não | tamanho e volatilidade |
| **Railway** | US$ 1 de crédito/mês (após trial de US$ 5) | permanente | não no trial | o crédito acaba em dias |
| **Koyeb** | 1 serviço (512 MB, 0,1 vCPU, 2 GB SSD) + Postgres de 1 GB com 5 h ativas | permanente | não | 0,1 vCPU |
| **Northflank Sandbox** | 2 serviços + 1 banco + 2 crons, **sem dormir** | permanente | não | quantidade |
| **Neon** | 0,5 GB/projeto; 100 CU-h/mês; até 100 projetos | permanente | não | 0,5 GB |
| **Supabase** | 500 MB; 5 GB de saída; 50 mil MAU; 2 projetos | permanente | não | **pausa em 7 dias sem uso** |
| **Aiven** | 1 vCPU, 1 GB RAM, 1 GB disco (PG, MySQL, Valkey, OpenSearch, Kafka) | permanente | não | 1 GB |
| **Upstash Redis** | 256 MB; 500 mil comandos/mês; 10 GB de banda; 10 bancos | permanente | não | **os 500 mil comandos** |
| **Redis Cloud** | 30 MB; 30 conexões; 100 ops/s; 5 GB/mês | permanente | não | 30 MB |
| **Vercel Hobby** | 100 GB; 1 mi invocações; 4 CPU-h | permanente | não | **uso comercial proibido** |
| **Netlify** | 300 créditos/mês (≈20 deploys) | permanente | não | teto rígido: pausa |
| **GitHub Pages** | ~1 GB e ~100 GB/mês | permanente | não | sem backend; restrição comercial |
| **GitHub Actions** | 2.000 min/mês (privado); **ilimitado em repositório público** | permanente | não | minutos |
| **GitHub Codespaces** | 120 h-núcleo/mês + 15 GB (Free); 180 h + 20 GB (Pro) | permanente | não | horas |
| **Cloud Run** | 2 mi req/mês; 180 mil vCPU-s; 360 mil GiB-s | permanente | **sim** | só regiões dos EUA |
| **Oracle Always Free** | 2 OCPU ARM + 12 GB; 200 GB de disco; **10 TB de saída** | permanente | **sim** | capacidade; recuperação de ociosos |
| **AWS (conta nova)** | US$ 100 + US$ 100 em créditos | **expira em 6 meses** | **sim** | o prazo |
| **Google Cloud (conta nova)** | US$ 300 | 90 dias | **sim** | o prazo |
| **Firebase Spark** | 1 GB armazenado; 10 GB/mês transferidos | permanente | não (Hosting) | banda |
| **Deno Deploy** | 1 mi req/mês; 100 GB de saída; 1 GiB de KV | permanente | não | CPU de 50 ms/req |
| **Fly.io** | **nada** (trial de 2 h de VM ou 7 dias) | — | **sim** | — |
| **Heroku** | **nada** desde 28/11/2022 | — | sim | — |

---

## 2. Tabela mestra — preços pagos

### Backend / computação

| Serviço | Plano | Preço/mês | ≈ BRL | O que inclui |
|---|---|---|---|---|
| Render | Starter | US$ 7 | R$ 36 | instância que não dorme |
| Render | Workspace Pro | US$ 25 | R$ 130 | assentos ilimitados, mais banda |
| Railway | Hobby | US$ 5 | R$ 26 | + US$ 5 de uso incluído |
| Railway | Pro | US$ 20 | R$ 104 | + US$ 20 de uso incluído |
| Fly.io | `shared-cpu-1x` 256 MB | ~US$ 2,02 | R$ 11 | pay-as-you-go |
| Fly.io | `shared-cpu-1x` 512 MB | ~US$ 3,32 | R$ 17 | |
| Fly.io | `shared-cpu-1x` 1 GB | ~US$ 5,92 | R$ 31 | |
| Cloudflare | Workers Paid | US$ 5 | R$ 26 | 10 mi req + 30 mi CPU-ms |
| Koyeb | Pro | US$ 29 | R$ 151 | + computação (US$ 10 incluídos) |
| Northflank | uso | US$ 0,01667/vCPU-h | — | + US$ 0,00833/GB-h |
| Vercel | Pro | US$ 20/assento | R$ 104 | + uso |
| Netlify | Pro | US$ 20 (fixo) | R$ 104 | membros ilimitados (desde 14/04/2026) |
| Heroku | Eco | US$ 5 | R$ 26 | 1.000 h compartilhadas, dorme em 30 min |
| Hetzner | CX23 | ~€ 5,49 | R$ 33 | 2 vCPU, 4 GB, 40 GB (+ IPv4 à parte) |
| Hetzner | CAX11 (ARM) | ~€ 5,99 | R$ 37 | 2 vCPU ARM, 4 GB |
| DigitalOcean | Basic | US$ 6 | R$ 31 | 1 vCPU, 1 GB |

### Banco de dados

| Serviço | Preço | ≈ BRL | Observação |
|---|---|---|---|
| Neon Launch | US$ 0,106/CU-h + US$ 0,35/GB-mês | — | sem mínimo mensal |
| Neon Scale | US$ 0,222/CU-h + US$ 0,35/GB-mês | — | 500 GB de saída inclusos |
| Supabase Pro | US$ 25 | R$ 130 | 8 GB, backup diário, sem pausa |
| Render Postgres | a partir de US$ 6–7 | R$ 31–36 | conforme o plano |
| Railway Postgres | por uso | — | consome o crédito do plano |
| AWS RDS `db.t4g.micro` | ~US$ 15 | R$ 78 | + disco + egress |
| Google Cloud SQL | ~US$ 10–15 | R$ 52–78 | **sem camada gratuita** |
| Postgres no VPS | € 0 adicional | — | você opera |

### Cache

| Serviço | Preço | ≈ BRL |
|---|---|---|
| Upstash pay-as-you-go | US$ 0,20/100 mil comandos + US$ 0,25/GB | — |
| Upstash fixo 250 MB | US$ 10 | R$ 52 |
| Upstash fixo 1 GB | US$ 20 | R$ 104 |
| Redis Cloud | a partir de ~US$ 5 | R$ 26 |
| Render Key Value pago | a partir de ~US$ 10 | R$ 52 |
| Valkey no VPS | € 0 adicional | — |

### Saída de dados (egress) — a linha que surpreende

| Provedor | Preço/GB | 1 TB/mês custa |
|---|---|---|
| **Cloudflare R2** | **US$ 0** | **US$ 0** |
| Fly.io (EUA/Europa) | US$ 0,02 | US$ 20 |
| **Fly.io (América do Sul)** | **US$ 0,04** | US$ 40 |
| Northflank | US$ 0,06 | US$ 60 |
| Neon (acima do incluso) | US$ 0,10 | US$ 100 |
| AWS (primeiras faixas) | ~US$ 0,09 | ~US$ 90 |
| Hetzner | incluído até a franquia (TB) | ~€ 0 |

---

## 3. Cenários de custo total

### Cenário A — projeto pessoal, 1.000 visitas/dia
```
Cloudflare Pages + Workers + Neon Free + Upstash Free
TOTAL: R$ 0,00
```

### Cenário B — SaaS pequeno, 200 usuários, 20 mil req/dia
```
Render Starter (API)         US$  7
Render Starter (worker)      US$  7
Supabase Pro (banco)         US$ 25
Upstash (uso)                US$  3
Sentry, UptimeRobot          US$  0
─────────────────────────────────────
TOTAL                        US$ 42/mês  ≈ R$ 218  (+IOF ≈ R$ 226)
```

### Cenário C — o mesmo SaaS, com região no Brasil
```
Fly.io gru 512 MB × 2        US$  7
Neon Launch (~2 GB)          US$  8
Upstash                      US$  3
Cloudflare Pages             US$  0
─────────────────────────────────────
TOTAL                        US$ 18/mês  ≈ R$ 94   — e ~85× mais rápido para o usuário BR
```

### Cenário D — auto-hospedado
```
Hetzner CX33 (4 vCPU, 8 GB)  €  10
IPv4                         €   0,60
Backup no R2                 US$  1
─────────────────────────────────────
TOTAL EM DINHEIRO            ≈ R$ 70/mês
TOTAL REAL                   + 4 h/mês do seu tempo (≈ R$ 400 a R$ 100/h)
```

### Cenário E — o mesmo sistema na AWS, mal configurado
```
ECS Fargate 0,5 vCPU/1 GB    US$ 18
RDS db.t4g.micro Multi-AZ    US$ 30
ElastiCache t4g.micro        US$ 12
ALB                          US$ 18   ← quase ninguém prevê isto
NAT Gateway                  US$ 33   ← e MUITO menos isto
Egress 200 GB                US$ 18
─────────────────────────────────────
TOTAL                        US$ 129/mês ≈ R$ 671
```

> **O NAT Gateway da AWS é a linha de fatura mais notória do setor:** ~US$ 33/mês só por
> existir, mais US$ 0,045 por GB processado. Muita gente o cria sem saber, ao seguir um
> tutorial de VPC privada. Comparar "AWS" com "Render" sem contabilizar ALB e NAT é comparar
> coisas diferentes.

---

## 4. Licenças

### Do software que você hospeda

| Software | Licença (18/08/2026) | O que permite | Cuidado |
|---|---|---|---|
| **PostgreSQL** | **PostgreSQL License** (tipo BSD/MIT) | tudo, inclusive fechar e vender | nenhum. É das licenças mais permissivas que existem |
| **Redis 8** | **tri-licença**: AGPLv3 **ou** RSALv2 **ou** SSPLv1 | AGPL: uso livre, com obrigação de disponibilizar fonte de derivados servidos em rede | AGPL contamina serviço, não só binário |
| **Valkey** | **BSD 3-Cláusulas** | tudo | nenhum |
| **Dragonfly** | **BSL 1.1** | uso próprio; **não** oferecer como serviço concorrente | vira Apache 2.0 após o prazo. Leia antes de uso comercial |
| **Docker Engine** | Apache 2.0 | tudo | — |
| **Docker Desktop** | proprietária | **exige assinatura** em empresas com 250+ pessoas ou US$ 10 mi+ de receita | use Colima, Podman ou OrbStack |
| **Node.js** | MIT | tudo | — |
| **Nginx / Caddy** | BSD-2 / Apache 2.0 | tudo | — |
| **Coolify** | Apache 2.0 | tudo | há versão nuvem paga |
| **Dokploy** | Apache 2.0 | tudo | — |
| **Grafana / Loki** | AGPLv3 (desde 2021) | uso interno livre | oferecer como serviço exige atenção |
| **Terraform** | **BSL 1.1** (desde ago/2023) | uso próprio | **OpenTofu** (Linux Foundation, MPL 2.0) é o fork livre |
| **Elasticsearch** | SSPL/Elastic; **AGPLv3 desde 2024** | conforme a escolhida | **OpenSearch** (Apache 2.0) é o fork da AWS |

### O que "AGPL" significa na prática

A AGPLv3 fecha a brecha da GPL para software servido pela rede: **se você modifica e oferece o
software como serviço, precisa disponibilizar o código modificado aos usuários desse serviço.**

- **Usar** Redis 8 AGPL como banco da sua aplicação: **sem obrigação** — sua aplicação não é
  obra derivada do Redis, ela apenas fala com ele pela rede.
- **Modificar** o Redis e oferecê-lo como serviço: obrigação de disponibilizar o fonte.
- Muitos departamentos jurídicos corporativos **proíbem AGPL por precaução**, mesmo no primeiro
  caso. Se você trabalha numa empresa assim, use **Valkey (BSD)** e evite a conversa.

### Dos termos de uso — as cláusulas que pegam

| Serviço | Cláusula |
|---|---|
| **Vercel Hobby** | uso **não comercial e pessoal** apenas |
| **GitHub Pages** | não é hospedagem para negócio; destinado a sites pessoais/de projeto |
| Camadas gratuitas em geral | proibido minerar cripto, servir proxy/VPN, e frequentemente proibido teste de carga |
| Camadas gratuitas em geral | uma conta gratuita por pessoa; múltiplas contas para burlar limites é violação |

---

## 5. Custos ocultos — a lista completa

| Custo | Quando aparece | Ordem de grandeza |
|---|---|---|
| **Egress** | quando o tráfego cresce | US$ 0 a 0,12/GB |
| **NAT Gateway / Load Balancer** (AWS/GCP) | ao usar rede privada | US$ 18 a 35/mês **cada** |
| **Backup e snapshot** | cobrados à parte na maioria | US$ 0,05 a 0,10/GB-mês |
| **Suporte** | quando você precisa | US$ 29 a 2.500/mês |
| **Migração** | ao trocar de fornecedor | 1 a 12 semanas de trabalho |
| **Seu tempo de operação** | todo mês | 0 a 8 h |
| **Curva de aprendizado** | no primeiro ano | 20 a 200 h por plataforma |
| **IOF (3,5%) e spread cambial** | toda fatura em dólar | +4% a 8% |
| **Variação cambial** | ao longo do ano | ±15% |
| **Assentos** | ao crescer a equipe | US$ 20 a 25 por pessoa/mês |
| **Observabilidade** | quando o gratuito acaba | US$ 20 a 200/mês |
| **E-mail transacional** | sempre esquecido | US$ 0 a 20/mês |

---

## 6. Alternativas gratuitas ou open source, e o que se perde

| Pago | Alternativa livre | O que se perde |
|---|---|---|
| Render / Railway | **Coolify** ou **Dokploy** num VPS | você opera tudo |
| Vercel | **Cloudflare Pages**, ou Next auto-hospedado | integração perfeita com Next |
| Supabase (nuvem) | **Supabase auto-hospedado** (Docker) | operação, escala, backup por sua conta |
| Redis Cloud | **Valkey** no VPS | gerenciamento, HA |
| Datadog / New Relic | **Grafana + Prometheus + Loki** | integração pronta e suporte |
| AWS RDS | PostgreSQL no VPS | failover automático, backup gerenciado |
| Terraform | **OpenTofu** | nada relevante; é fork compatível |
| Elasticsearch | **OpenSearch** | alguns recursos proprietários |
| GitHub Actions | **Forgejo Actions**, **Woodpecker CI** | ecossistema de ações prontas |

---

## 7. Se tudo o que você usa é gratuito, **quem paga a conta?**

Vale responder explicitamente:

- **Cloudflare**: a rede existe para o negócio de CDN, segurança e Zero Trust corporativo.
  Sua computação gratuita é resíduo de capacidade já paga. **Sustentável.**
- **Neon, Supabase, Render, Railway**: capital de risco + conversão de gratuitos em pagantes.
  **Sustentável enquanto o funil fechar.**
- **Oracle**: marketing e disputa por participação num mercado onde é distante do líder.
  **Sustentável enquanto for prioridade estratégica.**
- **GitHub**: pertence à Microsoft; gratuidade para código aberto é aquisição de
  desenvolvedores e, hoje, dado de treinamento e distribuição de produtos de IA.
- **Valkey, PostgreSQL, Coolify**: pagos por empresas que lucram com serviços em torno deles,
  e por trabalho voluntário. **A licença garante que ninguém pode tirar de você.**

**A conclusão prática:** software livre não pode ser revogado; serviço gratuito pode. Prefira
depender do primeiro sempre que a diferença de esforço for aceitável.

---

## Autoteste

1. Por que preço sem data é desinformação neste setor? Dê um exemplo de 2026.
2. Quanto custa 1 TB de egress na AWS, no Fly.io (América do Sul) e no R2?
3. Quais duas linhas de fatura tornam a AWS muito mais cara do que a comparação ingênua sugere?
4. O que a AGPLv3 exige, e quando ela **não** afeta quem apenas usa o Redis como banco?
5. Qual licença você escolhe se vende software que embute o servidor de cache?
6. Cite cinco custos ocultos e a ordem de grandeza de cada um.
7. Compare os cenários B e C: qual é mais barato e qual é mais rápido para o usuário brasileiro?
8. Para cada provedor gratuito que você usa, responda: **quem paga a conta?**

---

### Fontes consultadas (18/08/2026)

Páginas oficiais de preços e documentação, consultadas em 18/08/2026: Render, Railway, Fly.io,
Koyeb, Northflank, Cloudflare (Workers, Pages, D1, Hyperdrive, R2), Vercel, Netlify, Neon,
Supabase, Upstash, Redis, Aiven, Heroku, Oracle Cloud (Always Free), AWS (anúncio do novo Free
Tier de 15/07/2025), Google Cloud, Firebase, GitHub (Actions e Codespaces), Deno Deploy,
Hetzner (com os reajustes de 01/04/2026 e 15/06/2026), DigitalOcean.
Cotação USD/BRL de 18/08/2026 (≈ R$ 5,20) e IOF de 3,5% sobre câmbio.
Textos de licença: PostgreSQL License, BSD-3, AGPLv3, SSPLv1, RSALv2, BSL 1.1, Apache 2.0, MIT.
