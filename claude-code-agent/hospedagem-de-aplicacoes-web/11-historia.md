# 11 · História — de onde vieram estas plataformas

`Nível: intermediário` · `Atualizado em 18/08/2026`

História aqui não é curiosidade: é o que explica **por que as coisas são estranhas do jeito
que são**, e o que permite prever o que vai acontecer com a camada gratuita que você está
prestes a usar.

---

## Linha do tempo

```
1991 ─ primeiro site (CERN). Hospedar = ter um computador na internet.
1993 ─ CGI: o servidor passa a EXECUTAR programas por requisição.
1995 ─ PHP e a hospedagem compartilhada. FTP, cPanel, "seu site por R$ 15/mês".
1999 ─ VMware ESX populariza virtualização em x86.
2006 ─ AWS EC2 e S3. Nasce a nuvem: máquina por hora, via API.
2007 ─ Heroku (fundada). "git push heroku main" muda a expectativa de todo mundo.
2008 ─ Google App Engine. GitHub. Linux cgroups no kernel.
2010 ─ Node.js decola; Redis ganha tração; NoSQL na moda.
2011 ─ Twelve-Factor App. Heroku é comprada pela Salesforce. IPv4 esgota na IANA (3/fev).
2013 ─ DOCKER. Empacotar aplicação vira commodity. DigitalOcean populariza o VPS de US$ 5.
2014 ─ AWS Lambda: serverless de verdade. Kubernetes é liberado pelo Google.
2015 ─ Let's Encrypt: TLS gratuito e automático. Fim da desculpa para HTTP.
2016 ─ Zeit (depois Vercel) e Netlify: o "Jamstack". Deploy de frontend vira trivial.
2017 ─ Cloudflare Workers (beta). Isolates V8: serverless sem cold start de container.
2019 ─ Fly.io, Render e Railway começam a ocupar o vácuo deixado pelo Heroku estagnado.
2020 ─ Pandemia. Tráfego explode. Supabase nasce como "Firebase open source".
2022 ─ 28/nov: HEROKU MATA A CAMADA GRATUITA. Migração em massa para Render e Fly.
2023 ─ FinOps vira pauta: juros altos, fim do dinheiro barato, "cloud repatriation".
      Neon e PlanetScale popularizam banco serverless com separação computação/armazenamento.
2024 ─ mar: Redis troca BSD por SSPL/RSAL. A Linux Foundation forka: nasce o VALKEY.
      Fly.io encerra as franquias gratuitas. ElephantSQL anuncia encerramento.
2025 ─ mai: Redis 8 volta ao open source com AGPLv3 (tri-licença).
      jul: AWS reformula o free tier: créditos de US$ 100–200 e plano que EXPIRA em 6 meses.
      set: Data Act europeu entra em aplicação; taxas de troca de provedor com prazo de morte.
      Coolify/Dokploy consolidam a volta do VPS auto-hospedado.
2026 ─ fev: Xata aposenta o "Lite" gratuito. abr: Netlify migra para preço por créditos.
      Valkey 9 vira padrão nas distros e nos serviços gerenciados. Neon abre região sa-east-1.
      A camada gratuita encolhe em toda parte, e o VPS barato nunca esteve tão popular.
```

---

## 1. A era da hospedagem compartilhada (1995–2006)

Você alugava espaço num servidor Apache com PHP e MySQL, dividido com outras 500 pessoas.
Subia os arquivos por FTP. Tudo — código, banco, arquivos — numa máquina só.

**O que era bom:** simplicidade absoluta. R$ 15/mês. Não existia "deploy": existia copiar
arquivo.
**O que era ruim:** um vizinho barulhento derrubava seu site; sem controle de versão do
ambiente; escala vertical apenas; nenhuma reprodutibilidade.

*Por que o PHP dominou?* Porque ele encaixava perfeitamente nesse modelo: um arquivo `.php`
numa pasta virava uma página, sem processo de build, sem servidor de aplicação, sem deploy.
**Parada legítima: um trade-off entre elegância e atrito de distribuição — e o atrito venceu.**
Essa lição se repete: **a tecnologia que reduz o atrito de publicar vence a que é tecnicamente
superior**. Vale para o PHP em 1998, para o Heroku em 2010 e para a Vercel em 2018.

---

## 2. A nuvem (2006–2013)

Em 2006, a AWS lançou o **S3** (março) e o **EC2** (agosto). A mudança conceitual: **capacidade
computacional virou API**. Você deixou de comprar servidor e passou a alugar por hora, sem
contrato, sem vendedor.

Consequência econômica: **o custo fixo virou custo variável**. Uma startup podia começar
gastando US$ 50/mês e escalar para US$ 50.000 sem comprar nada. Isso, junto com o barateamento
dos frameworks, criou a década das startups de software.

Consequência técnica: como a máquina virou descartável, **o software precisou aprender a ser
descartável também**. Daí o Twelve-Factor (2011): configuração no ambiente, processos sem
estado, descartabilidade, paridade entre desenvolvimento e produção.

---

## 3. O Heroku e a expectativa que ele criou (2007–2022)

O Heroku fez uma coisa que parece pequena e mudou o setor: `git push heroku main`. Do commit ao
site no ar, sem tocar em servidor. Inventou o vocabulário que a indústria ainda usa: *dyno*,
*buildpack*, *add-on*, *slug*, *procfile*.

E deu **camada gratuita generosa**: um dyno web, um Postgres de 10 mil linhas, um Redis. Duas
gerações de programadores aprenderam a fazer deploy ali.

**Em 28 de novembro de 2022, o Heroku desligou tudo isso.** Sem gratuito. Motivo declarado:
abuso em escala (mineração de cripto, contas fraudulentas) e insustentabilidade econômica.
Motivo não declarado, e amplamente conjecturado: sob a Salesforce, o produto estagnou e virou
centro de custo.

**O que isso ensina, e é a lição mais importante deste capítulo:** *uma camada gratuita é uma
decisão de negócio revogável, não um direito.* Quem tinha o banco de produção no plano
gratuito teve **90 dias** para migrar. O substituto de hoje — Render, Railway, Neon — está
sujeito exatamente à mesma dinâmica.

O Heroku voltou com **Eco dynos a US$ 5/mês** (1.000 horas compartilhadas, com sono após 30
minutos) e **Mini Postgres/Redis**, mas o dano à confiança foi feito e a migração não voltou.

---

## 4. Docker e o container como unidade universal (2013–)

O Docker não inventou containers (LXC, Solaris Zones, FreeBSD jails vieram antes). Ele
inventou o **empacotamento reprodutível e compartilhável**: `Dockerfile`, imagem em camadas,
registro público, e um comando que roda igual em qualquer lugar.

**O impacto em hospedagem foi este:** o artefato de deploy deixou de ser específico da
plataforma. Antes, você fazia deploy "no formato Heroku". Depois do Docker, você faz deploy de
**uma imagem**, e ela roda no Render, no Fly, no Cloud Run, no Kubernetes ou no seu VPS.

> **É a razão pela qual "ter um Dockerfile" é a melhor apólice de seguro contra aprisionamento
> de fornecedor que existe.** Custa uma tarde e vale anos. Se você tirar uma única
> recomendação prática deste capítulo, que seja esta.

---

## 5. Serverless e a borda (2014–)

**AWS Lambda (2014)** levou o modelo ao extremo: nenhum servidor seu ligado; você paga por
invocação e por milissegundo. Entre requisições, não existe nada.

O preço: **cold start**. A primeira invocação depois de um período ocioso precisa criar o
ambiente. Na Lambda, de 100 ms a vários segundos (pior em JVM e .NET, melhor em Go e Node).

**Cloudflare Workers (2017)** atacou justamente isso trocando o container por um **isolate**
do V8 — o mesmo mecanismo que isola abas do Chrome. Um isolate inicia em poucos
milissegundos e consome ~3 MB. Em troca, você não roda "qualquer coisa": roda JavaScript e
WebAssembly, com API de plataforma própria (não é Node completo).

E surgiu a **borda** (*edge*): rodar não num data center, mas em centenas de cidades ao mesmo
tempo, perto do usuário. Ótimo para latência. **Péssimo para bancos de dados** — o dado
continua num lugar só, e código na borda longe do banco é *mais lento*, não mais rápido.
É o problema que gerou Hyperdrive, D1, Turso e a onda de "banco na borda" de 2023–2026.
Veja [`65-estado-da-arte.md`](65-estado-da-arte.md).

---

## 6. O ciclo econômico: a camada gratuita cresce e encolhe

Este é o padrão que se repete, e reconhecê-lo é o que permite prever.

```
   dinheiro barato (juros baixos)        juros altos / pressão por lucro
        │                                          │
        ▼                                          ▼
  camada gratuita generosa  ──── abuso ────►  cortes, verificação de identidade,
  (aquisição de cliente)         em massa     créditos temporários, fim do gratuito
        ▲                                          │
        └──────── nova empresa entra ◄─────────────┘
                  querendo participação de mercado
```

Evidências de 2022 a 2026:

| Quando | O que | Direção |
|---|---|---|
| nov/2022 | Heroku encerra todos os planos gratuitos | ↓ |
| 2023 | Railway substitui o gratuito por US$ 5 de crédito único | ↓ |
| jan/2025 | ElephantSQL encerra as atividades | ↓ |
| 2024 | Fly.io encerra as franquias gratuitas | ↓ |
| jul/2025 | AWS troca o free tier de 12 meses por créditos que expiram em 6 meses | ↓ |
| fev/2026 | Xata aposenta o plano "Lite" gratuito | ↓ |
| abr/2026 | Netlify migra para créditos: 300/mês no gratuito, com teto rígido | ↓ (mais previsível, menos generoso) |
| 2023–2026 | Cloudflare **amplia** o gratuito (D1, Hyperdrive, Containers) | ↑ |
| 2024–2026 | Neon, Supabase e Koyeb mantêm gratuito competitivo | → |

**Leitura:** a Cloudflare cresce a camada gratuita porque o custo marginal dela é quase nulo
(a rede já existe para o negócio de CDN e segurança) e porque o objetivo é ocupar o mercado de
computação. As demais cortam porque computação é o produto principal e sai caro. **Sempre
pergunte: para esta empresa, o que eu uso de graça é resíduo de outro negócio ou é o negócio?**
Camada gratuita que é resíduo dura. Camada gratuita que é o produto, não.

---

## 7. A volta do VPS (2023–2026)

O movimento mais interessante dos últimos três anos é um retrocesso aparente: **gente saindo da
nuvem gerenciada e voltando para uma máquina alugada**.

O gatilho foi público: em 2022–2023 a 37signals (Basecamp, HEY) documentou a saída da AWS
alegando economia da ordem de milhões de dólares por ano, e liberou o **Kamal**, ferramenta de
deploy em servidores próprios. Em paralelo, **Coolify** e **Dokploy** deram ao VPS a
experiência de PaaS — deploy por `git push`, TLS automático, banco em um clique.

A conta que move isso é brutal: um VPS de 4 vCPU e 8 GB por ~€ 8/mês entrega o que custaria
10 a 20 vezes mais numa PaaS. **O que você paga em troca:** atualizar SO, aplicar correções de
segurança, monitorar, fazer backup, e estar disponível quando quebrar.

> **Minha opinião, declarada:** a volta do VPS é real e saudável, mas é frequentemente vendida
> com uma conta incompleta. Some ao aluguel: 3 a 6 horas por mês de manutenção, o custo de um
> incidente por ano e o risco de perder tudo se o backup nunca foi testado. Para **uma pessoa
> só**, isso costuma valer a pena até uns US$ 100/mês de fatura gerenciada. Acima disso, a
> conta vira favorável ao VPS mesmo com o tempo contabilizado. Abaixo, PaaS ganha.

---

## 8. O que a história permite prever

Não é adivinhação; é extrapolação de padrão, e está declarado como **opinião fundamentada**:

1. **Camadas gratuitas vão continuar encolhendo** em quem vende computação, e crescendo em
   quem vende outra coisa (Cloudflare) ou quem está comprando participação de mercado.
2. **O banco de dados vai ser a última coisa a ficar gratuita**, porque é a única com custo
   fixo real por cliente.
3. **Container continuará sendo o formato universal** por mais uma década. Quem tem
   `Dockerfile` migra em uma tarde.
4. **A borda vai encontrar o seu limite no estado.** Código distribuído é fácil; dado
   distribuído é o problema difícil, e não há solução mágica no horizonte.
5. **A regulação vai apertar o aprisionamento** (Data Act europeu; taxas de troca proibidas a
   partir de 12/01/2027), o que deve baratear migração — e portanto reduzir o poder de
   barganha das nuvens grandes.

---

## Autoteste

1. O que o Heroku inventou, e qual foi a lição de 28 de novembro de 2022?
2. Por que o PHP dominou a era da hospedagem compartilhada, e que princípio geral isso ilustra?
3. O que exatamente o Docker inventou, se containers já existiam?
4. Por que Cloudflare Workers têm cold start muito menor que AWS Lambda — e o que se perde nessa troca?
5. Explique o ciclo econômico da camada gratuita e use-o para julgar a Cloudflare e a Railway.
6. Quais foram os gatilhos da volta do VPS, e qual é a conta que costuma faltar nessa comparação?
7. Cite três camadas gratuitas que deixaram de existir entre 2022 e 2026 e o que cada uma ensina.

---

### Fontes consultadas (18/08/2026)

- Heroku Blog — *Heroku's Next Chapter* (2022) e *New Low-Cost Plans* (Eco e Mini dynos)
- AWS — anúncio de 15/07/2025 sobre o novo Free Tier com créditos
- Redis — anúncio de licença de mar/2024 e retorno ao open source com AGPLv3 em mai/2025
- Linux Foundation — anúncio do fork Valkey (2024) e linha 9.x (2025–2026)
- Netlify — *Credit-based pricing* (changelog de 14/04/2026)
- Fly.io — comunicações sobre o fim das franquias gratuitas (2024)
- 37signals — série pública sobre saída da nuvem (2022–2023) e projeto Kamal
- Twelve-Factor App (2011)
