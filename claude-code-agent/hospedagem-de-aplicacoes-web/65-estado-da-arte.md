# 65 · Estado da arte — agosto de 2026

`Nível: avançado` · `Fotografia tirada em 18/08/2026`
`⚠️ Este é o arquivo que envelhece mais rápido do curso. Reavalie a cada 6 meses.`

O que mudou, o que está em disputa e o que ainda não tem resposta.

---

## 1. As seis mudanças que definiram 2024–2026

### 1.1 A camada gratuita encolheu, e ficou mais previsível

| Quando | O quê |
|---|---|
| 2024 | Fly.io encerra as franquias gratuitas |
| jan/2025 | ElephantSQL encerra as atividades |
| jul/2025 | AWS troca o free tier de 12 meses por **US$ 100–200 em créditos que expiram em 6 meses** |
| fev/2026 | Xata aposenta o plano "Lite" gratuito |
| abr/2026 | Netlify migra para **créditos** (300/mês no gratuito, com teto rígido) |

Contracorrente: **Cloudflare ampliou** o gratuito (D1, Hyperdrive com 100 mil consultas/dia,
Containers no plano pago de US$ 5), e **Neon, Supabase, Koyeb e Northflank** mantiveram planos
competitivos. A explicação está em [`55`](55-economia-do-gratuito.md): quem tem a
infraestrutura como resíduo de outro negócio pode ser generoso.

**A tendência de fundo — e é a mais importante para quem planeja:** o mercado está trocando
"limites generosos e imprevisíveis" por **"limites menores e previsíveis"**. Créditos e teto
rígido são piores para quem quer muito de graça e melhores para quem não pode receber uma
fatura surpresa.

### 1.2 O fim da guerra de licença do Redis

Março de 2024: Redis abandona a BSD (SSPL + RSAL). Uma semana depois: a Linux Foundation forka
e cria o **Valkey**. Maio de 2025: Redis 8 volta ao open source com **AGPLv3** (tri-licença).

**Situação em agosto de 2026:** Valkey 9.x é o padrão em Fedora, Ubuntu 26.04 LTS, Debian e
Arch; a AWS o adotou como padrão em ElastiCache e MemoryDB, com preço abaixo do Redis OSS.
Redis segue na linha 8.x, com módulos exclusivos (busca, JSON, vetores) que o Valkey não tem.

**Leitura:** a Redis Inc. recuperou a legitimidade open source, mas **perdeu o padrão de
fato** para as distribuições e para as nuvens. Detalhes em [`30`](30-catalogo-redis.md).

### 1.3 Postgres serverless virou commodity

A arquitetura de **separar computação de armazenamento** (Neon, Aurora Serverless v2,
Prisma Postgres) deixou de ser novidade. O que ela habilitou:

- **suspensão em segundos**, com custo próximo de zero quando ocioso;
- **ramificação do banco por *copy-on-write*** — um branch de banco por pull request, criado
  em segundos, é hoje prática comum;
- **escala de leitura independente da escala de escrita**.

O que ela **não** resolveu: a escrita continua com um primário, e a latência da primeira
consulta após suspensão continua existindo (~500 ms na Neon).

### 1.4 A borda encontrou o seu limite: o estado

Rodar código em 300 cidades é problema resolvido. Rodar **dado** em 300 cidades, não.
As tentativas em produção:

| Abordagem | Quem | O que resolve | O que não resolve |
|---|---|---|---|
| Pool + cache de consulta na borda | Cloudflare Hyperdrive | conexões e leitura repetida | escrita continua indo à origem |
| Banco pequeno na própria borda | Cloudflare D1 (SQLite) | leitura local rápida | tamanho, escrita, consulta complexa |
| Réplica embarcada | Turso (libSQL) | leitura local | não é PostgreSQL |
| KV eventualmente consistente | Workers KV | configuração, cache global | contador, trava, consistência |
| Objeto com estado e localidade única | Durable Objects | coordenação e consistência | a localidade fixa reintroduz latência |
| Relógio atômico global | Google Spanner | consistência externa de verdade | preço e amarração ao GCP |

**Consenso emergente:** *código na borda, dado no centro, cache na borda*. Colocar dado na
borda só compensa quando ele é **pequeno, majoritariamente lido e tolerante a atraso**.

### 1.5 A volta do VPS virou movimento organizado

**Coolify v4.0** (maio de 2026) e **Dokploy** deram ao VPS experiência de PaaS. **Kamal**
(37signals) consolidou o deploy em servidores próprios como prática respeitável. A pauta
"repatriação de nuvem" saiu do blog e entrou em reunião de diretoria — puxada por juros altos e
pela percepção de que a fatura crescia mais rápido que a receita.

**Contra-movimento em 2026:** os provedores de VPS reajustaram. A **Hetzner aumentou preços em
1º de abril e novamente em 15 de junho de 2026**, alguns planos em 30% ou mais, alegando custo
de energia e de hardware. A vantagem continua enorme (5 a 20×), mas encolheu — e mostrou que
"barato para sempre" também não existe do outro lado.

### 1.6 Infraestrutura para agentes de IA — o segmento que nasceu

O que era nicho em 2024 virou linha de produto em 2026: **sandboxes efêmeros para executar
código gerado por modelos de linguagem**. Vercel Sandbox, Cloudflare Containers, E2B, Modal,
Daytona, Fly Machines por API. Requisitos distintos do deploy tradicional:

- criação em **menos de um segundo**, por API, aos milhares;
- isolamento forte (o código é não confiável **por definição**);
- vida útil de segundos a minutos;
- cobrança por milissegundo.

A Netlify chegou a incluir **inferência de IA** como um dos cinco medidores do seu modelo de
créditos. Esta é a fronteira comercial mais quente do setor em 2026 — e é, na prática, o
serverless original levado ao extremo: mais efêmero, mais isolado, mais barato por unidade.

---

## 2. O que está em disputa (sem vencedor definido)

### 2.1 Container × isolate × WASM

| | Container | Isolate V8 | WASM (WASI) |
|---|---|---|---|
| Roda qualquer linguagem | ✅ | ❌ (JS/WASM) | ⚠️ crescente |
| Cold start | 100 ms–3 s | **< 5 ms** | **< 5 ms** |
| Isolamento | namespaces (+ microVM) | sandbox de linguagem | sandbox de módulo |
| Maturidade | altíssima | alta | **em consolidação** |
| Ecossistema | universal | limitado | pequeno |

**WASM com WASI Preview 2 e o modelo de componentes** é a aposta de longo prazo: portabilidade
de container com partida de isolate. Em 2026 ainda é promessa parcial — o suporte a threads,
sockets e sistema de arquivos amadureceu, mas o ecossistema de bibliotecas está longe do de
Node ou Python. **Minha opinião: WASM ganha o nicho de plugins e funções pequenas nos próximos
três anos; container continua dominando o deploy de aplicações por bem mais tempo.**

### 2.2 Monolito × microsserviços

O pêndulo voltou para o **monolito modular**. Depois de uma década de microsserviços por
padrão, a leitura de 2024–2026 é que a maior parte das equipes pagou complexidade distribuída
(rede, observabilidade, consistência) sem colher o benefício correspondente. O caso público
mais citado é o da Amazon Prime Video, que em 2023 relatou economia de 90% ao consolidar um
pipeline serverless em um monólito.

**Leitura sóbria:** o erro não foi microsserviços; foi adotá-los antes de existir o problema
organizacional que eles resolvem — times independentes que não podem esperar uns pelos outros.

### 2.3 Nuvem grande × plataforma especializada × auto-hospedagem

Sem vencedor. As três coexistem e a escolha é de contexto, não de mérito. O que mudou é que
**mudar entre elas ficou mais fácil**, graças ao container e — a partir de 12/01/2027 na
Europa — à proibição de taxas de troca pelo Data Act.

---

## 3. O que NÃO mudou (e provavelmente não vai)

- **O banco relacional continua no centro.** Depois do ciclo NoSQL de 2010–2015, o PostgreSQL
  voltou a ser o padrão, e absorveu boa parte dos casos NoSQL (JSONB, arrays, `pgvector`).
- **Cache continua sendo a otimização de melhor retorno.**
- **Backup continua sendo o único item irreversível.**
- **Latência da luz continua sendo latência da luz.**
- **A maior parte dos sistemas continua cabendo num único servidor.** Uma máquina de 2026 com
  8 núcleos e 32 GB atende, com folga, mais tráfego do que 95% dos sistemas em produção
  recebem.

---

## 4. O que observar nos próximos 12 meses

| Tema | O que observar | Por que importa |
|---|---|---|
| **PostgreSQL 19** | previsto para o segundo semestre de 2026 (Beta 3 saiu em 13/08/2026) | melhorias de I/O assíncrono e desempenho |
| **Postgres com threads** | discussão ativa; nada entregue até a v18 | mudaria a economia de conexões |
| **Data Act (UE)** | proibição de taxas de troca em **12/01/2027** | pode derrubar o custo de migração no mundo todo |
| **Créditos como modelo** | se outros seguirem a Netlify | previsibilidade × generosidade |
| **Preço de VPS** | novos reajustes (Hetzner já subiu duas vezes em 2026) | muda a conta da auto-hospedagem |
| **Sandboxes para agentes** | consolidação ou explosão de fornecedores | é onde o capital está indo |
| **Valkey × Redis** | se os módulos do Redis 8 mantêm alguém preso | decide o padrão da próxima década |
| **Certificados TLS de 47 dias** | cronograma do CA/Browser Forum até 2029 | automação deixa de ser opcional |

---

## 5. Previsões, declaradas como opinião

Não são fatos. São extrapolações fundamentadas, e ficam registradas com data para poderem ser
cobradas:

1. **Até 2028, pelo menos duas das camadas gratuitas citadas neste curso terão acabado ou
   encolhido pela metade.** Aposta: as sustentadas por capital de risco, não as da Cloudflare.
2. **O modelo de créditos com teto rígido vai se espalhar.** É melhor para o provedor
   (previsível) e vendável ao usuário como "sem fatura surpresa".
3. **A borda vai parar de tentar resolver o problema do estado geral** e se especializar em
   cache, autenticação, roteamento e transformação — que é o que ela faz bem.
4. **Postgres continuará ganhando.** Cada ano em que ele absorve mais casos de uso (vetores,
   séries temporais, filas) é um ano a menos de vida para bancos especializados de nicho.
5. **A auto-hospedagem vai continuar crescendo, mas menos do que o discurso sugere.** O
   gargalo é gente que saiba operar, não preço de servidor.

---

## Autoteste

1. Cite quatro camadas gratuitas que encolheram ou morreram entre 2024 e 2026, e uma que cresceu. Explique a diferença.
2. Qual é o consenso emergente sobre borda e estado, e por que a borda não resolve o caso geral?
3. Em que situação a Redis Inc. venceu e em que situação perdeu, depois da crise de licença?
4. Qual é o contra-movimento de 2026 à volta do VPS?
5. Que requisitos os sandboxes para agentes de IA têm que o deploy tradicional não tem?
6. Qual é a leitura sóbria do debate monolito × microsserviços?
7. Cite três coisas que não mudaram e provavelmente não vão mudar.
8. Escolha uma das cinco previsões e argumente contra ela.

---

### Fontes consultadas (18/08/2026)

- Netlify — *Credit-based pricing* (changelog de 14/04/2026)
- AWS — anúncio do novo Free Tier (15/07/2025)
- Redis — anúncios de licença (mar/2024 e mai/2025); Linux Foundation — Valkey 9.x
- Cloudflare — documentação de Workers, D1, Hyperdrive e Containers
- Hetzner — documentação sobre os reajustes de 01/04/2026 e 15/06/2026
- PostgreSQL — anúncio de 13/08/2026 (18.6, 17.11, 16.15, 15.19, 14.24 e 19 Beta 3)
- Coolify — anúncio da v4.0 (maio de 2026)
- Regulamento (UE) 2023/2854 (*Data Act*), art. 29
- CA/Browser Forum — cronograma de redução da validade de certificados TLS
- Relato público da Amazon Prime Video sobre consolidação de arquitetura (2023)
