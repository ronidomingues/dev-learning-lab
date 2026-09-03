# 35 · Catálogo — onde hospedar o **frontend**

`Nível: iniciante a intermediário` · `Consultado na web em 18/08/2026`

Boa notícia: **esta é a peça mais fácil e mais barata de hospedar**. Arquivos estáticos não
têm estado, são cacheáveis e o custo marginal de servi-los é próximo de zero. Por isso a
competição é feroz e as camadas gratuitas são generosas de verdade.

---

## Resumo executivo

| Serviço | Gratuito | Limite prático do gratuito | Uso comercial? | Funções no servidor? |
|---|---|---|---|---|
| **Cloudflare Pages** | ✅ | **requisições a arquivos estáticos ilimitadas**; funções compartilham 100 mil req/dia com Workers | ✅ sim | ✅ Pages Functions |
| **GitHub Pages** | ✅ | 1 GB de site, ~100 GB/mês de banda (limites *soft*), 10 builds/h | ⚠️ só para sites que apoiam o projeto | ❌ |
| **Netlify** | ✅ | **300 créditos/mês, com teto rígido** (deploy de produção custa 15 créditos) | ✅ sim | ✅ Functions |
| **Vercel** | ✅ Hobby | 100 GB de transferência, 1 mi de req de borda, 1 mi de invocações, 4 CPU-h | ❌ **proibido** no Hobby | ✅ Functions |
| **Render Static Sites** | ✅ | conta contra a banda e os minutos de build do workspace | ✅ sim | ❌ |
| **Firebase Hosting** | ✅ Spark | 1 GB armazenado, 10 GB/mês transferidos | ✅ sim | ⚠️ Functions exigem o plano Blaze |
| **Cloudflare R2 + Workers** | ✅ | 10 GB de armazenamento, **egress zero** | ✅ sim | ✅ |
| **GitLab Pages / Codeberg Pages** | ✅ | limites modestos | ✅ | ❌ |
| **Surge.sh** | ✅ | projetos ilimitados, sem HTTPS em domínio próprio no gratuito | ✅ | ❌ |
| **Azure Static Web Apps** | ✅ Free | 100 GB/mês de banda, 2 domínios | ✅ | ✅ (limitadas) |

---

## 1. Cloudflare Pages — **a recomendação padrão**

**Por quê.** No plano gratuito, **requisições a arquivos estáticos são gratuitas e
ilimitadas** — não há teto de banda, nem de visitas. Isso é raro e é o principal motivo da
recomendação. O site é servido pela rede da Cloudflare, com presença em centenas de cidades,
**incluindo várias no Brasil** (São Paulo, Rio, Fortaleza, Porto Alegre e outras).

Inclui, sem custo: TLS automático, domínio próprio, deploy por Git, *preview* por branch,
HTTP/3, compressão Brotli, proteção contra DDoS.

**Pages Functions** (código no servidor, junto do site) compartilham a cota do Workers:
**100 mil requisições/dia** no gratuito.

**Limites que existem:** builds mensais limitados no gratuito, tamanho máximo de arquivo
(25 MB por arquivo) e número máximo de arquivos por deploy (20.000).

**Veredito.** Se o seu frontend é estático ou uma SPA, **este é o melhor lugar, e o gratuito
provavelmente basta para sempre**. A integração com Workers, R2, D1 e Hyperdrive faz do
conjunto Cloudflare a pilha gratuita mais coerente de 2026.

---

## 2. Vercel

Insuperável para **Next.js** — a empresa mantém o framework, e recursos como ISR, RSC e
otimização de imagem funcionam sem configuração.

**Hobby (gratuito):** 100 GB de *Fast Data Transfer*, 1 milhão de requisições de borda,
1 milhão de invocações, 4 CPU-horas ativas, 360 GB-horas de memória, 200 projetos, 5.000
transformações de imagem. **Ao estourar, o projeto pausa** — não vira fatura.

**⚠️ A pegadinha que mais gente ignora:** as *fair use guidelines* dizem que **o Hobby é para
uso não comercial e pessoal**. Um SaaS, uma loja, um blog com anúncios ou um site de cliente
exigem o **Pro, a US$ 20 por assento/mês**. Contas já foram suspensas por isso.

**Outra restrição do Hobby:** não é possível conectar projeto do Hobby a repositório
pertencente a **organização** do GitHub — só a repositório pessoal.

**Veredito.** Use pelo Next.js e por projeto pessoal. Para site comercial, ou você paga o Pro
ou vai para a Cloudflare. A cobrança da Vercel (CPU ativa, memória provisionada, transferência
regional) é a mais difícil de prever do mercado — leia
[`80-custos-e-licencas.md`](80-custos-e-licencas.md) antes de crescer.

---

## 3. Netlify — e a mudança de 2026

Em **14 de abril de 2026**, a Netlify migrou para **preço por créditos** e eliminou a cobrança
por assento (o Pro virou **US$ 20/mês fixos, com membros ilimitados**).

**Gratuito:** **300 créditos por mês, com teto rígido** — ao acabar, os sites pausam até o
próximo ciclo. Créditos são consumidos por cinco medidores: deploys de produção (**15 créditos
por deploy**), computação, banda, requisições web e inferência de IA. Na prática, **300
créditos ≈ 20 deploys de produção por mês**, mais o consumo dos outros medidores.

**Veredito.** O modelo novo é mais **previsível** (não há fatura surpresa) e menos **generoso**
(20 deploys por mês é pouco para quem integra continuamente). Se você faz deploy a cada
commit, esta é uma mudança grande. A Netlify continua ótima em forms, identidade e funções —
mas para um site estático puro, a Cloudflare é mais barata e mais folgada.

---

## 4. GitHub Pages

Gratuito, direto do repositório, com domínio próprio e TLS. Limites documentados como *soft*:
site de até 1 GB, ~100 GB de banda por mês, 10 builds por hora.

**Restrição importante:** os termos do GitHub Pages destinam o serviço a sites **pessoais, de
organização e de projeto**, e desencorajam uso comercial primário (loja, SaaS). É permitido um
site institucional que apoie um projeto; não é permitido usar como hospedagem de um negócio.

**Veredito.** Perfeito para documentação, portfólio e página de projeto open source. Sem
funções no servidor — se precisar de API, combine com Cloudflare Workers.

---

## 5. Firebase Hosting

**Spark (gratuito):** 1 GB armazenado e **10 GB de transferência por mês**. CDN global, TLS
automático, deploy por CLI.

**Mudança recente:** desde **3 de fevereiro de 2026**, o Cloud Storage for Firebase passou a
seguir as regras do Google Cloud Storage, o que **exige conta de faturamento vinculada** para
criar um bucket, mesmo permanecendo na faixa "Always Free". Hosting em si continua no Spark.

**Veredito.** Faz sentido se você já usa Firestore ou Firebase Auth. Os 10 GB/mês de banda são
o limite real e apertado — um site com imagens pesadas consome isso rápido.

---

## 6. O que realmente importa na escolha (e quase ninguém verifica)

Além de preço:

| Critério | Por que importa | Quem se sai bem |
|---|---|---|
| **Presença no Brasil** | 20 ms contra 150 ms para o primeiro byte | Cloudflare, Vercel, Netlify (todas com PoP no BR) |
| **Cabeçalhos de cache configuráveis** | é o que faz o site ser rápido de verdade | Cloudflare (`_headers`), Netlify (`_headers`), Vercel (`vercel.json`) |
| **Redirecionamentos e SPA fallback** | sem isso, atualizar a página numa rota da SPA dá 404 | todos, com sintaxe diferente |
| **Preview por branch** | revisar visualmente antes de publicar | Cloudflare, Vercel, Netlify |
| **Limite de arquivos/tamanho** | projetos com muitos assets estouram | Cloudflare: 20.000 arquivos, 25 MB cada |
| **Rollback em um clique** | o que salva um deploy ruim | todos os grandes |
| **Uso comercial permitido** | evita suspensão | ⚠️ Vercel Hobby e GitHub Pages têm restrição |

**O arquivo `_headers` da Cloudflare/Netlify — o que separa um site rápido de um site lento:**

```
# public/_headers
/assets/*
  Cache-Control: public, max-age=31536000, immutable

/index.html
  Cache-Control: public, max-age=0, must-revalidate

/*
  X-Frame-Options: DENY
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
```

**Por que essa combinação exata:** ferramentas de build (Vite, Next, Webpack) geram nomes de
arquivo com hash (`app-a1b2c3.js`). Nome com hash **nunca** muda de conteúdo, então pode ser
cacheado para sempre (`immutable`, 1 ano). O `index.html`, que aponta para esses nomes,
**nunca** pode ser cacheado — senão o usuário fica preso na versão antiga depois de um deploy.
Errar isso é a causa nº 1 de "fiz deploy e o usuário continua vendo o site velho".

---

## 7. SPA, SSR, SSG: onde cada um pode morar

| Arquitetura | Precisa de servidor? | Onde hospedar |
|---|---|---|
| **SPA** (React/Vue puro) | não | qualquer static host. Cloudflare Pages |
| **SSG** (Astro, Hugo, Jekyll, Next `output: export`) | não | qualquer static host |
| **SSR** (Next, Nuxt, SvelteKit, Remix) | **sim** | Vercel, Netlify, Cloudflare (com adaptador), Render, Fly |
| **ISR** (regeneração incremental) | sim, com cache persistente | Vercel nativamente; outros com adaptador |
| **Ilhas** (Astro com hidratação parcial) | quase não | static host + funções pontuais |

Detalhes conceituais em [`spa-single-page-application`](../spa-single-page-application/00-MAPA.md).

> **Regra prática:** se o seu frontend precisa de SSR, ele deixou de ser "frontend" para efeito
> de hospedagem — passou a ser um **backend que devolve HTML**, com todos os custos disso
> (cold start, CPU, escala). Escolha essa complexidade conscientemente. Muitos sites que usam
> SSR não precisam dele.

---

## 8. Autoteste

1. Por que o frontend é a peça mais barata de hospedar?
2. O que a Cloudflare Pages oferece de graça que nenhuma outra iguala?
3. Quem, exatamente, é proibido de usar o plano Hobby da Vercel?
4. O que mudou na Netlify em abril de 2026 e por que isso pode ser ruim para quem faz CI?
5. Explique a combinação de `Cache-Control` do arquivo `_headers` e o bug que ela evita.
6. Em que momento um "frontend" passa a ser, para efeito de hospedagem, um backend?
7. Quais dois serviços deste capítulo têm restrição de uso comercial?

---

### Fontes consultadas (18/08/2026)

- Cloudflare — *Pages Functions Pricing* (estáticos ilimitados; 100 mil req/dia compartilhadas) e *Workers Pricing*
- Vercel — *Limits*, *Hobby Plan*, *Fair Use Guidelines* (uso comercial) — vercel.com/docs
- Netlify — *Credit-based pricing plans* e changelog de 14/04/2026 — netlify.com
- GitHub — *GitHub Pages limits* e termos de uso
- Firebase — página de preços (Spark) e nota sobre o Cloud Storage a partir de 03/02/2026
- Render — *Static Sites* e cotas do workspace
