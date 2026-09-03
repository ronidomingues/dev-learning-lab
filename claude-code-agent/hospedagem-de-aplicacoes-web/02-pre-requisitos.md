# 02 · Pré-requisitos

`Nível: iniciante` · `Atualizado em 18/08/2026`

Este arquivo diz **o que você precisa saber, ter e conseguir** antes de seguir para o
[`03-instalacao.md`](03-instalacao.md). É honesto sobre tempo. Se algo faltar, a
[seção 6](#6-rota-de-resgate) diz o que fazer.

---

## 1. Conhecimento indispensável

Sem isto, você vai travar no primeiro obstáculo e não vai saber nem o que perguntar.

| O que | Por que é indispensável | Onde aprender |
|---|---|---|
| **Usar um terminal** (`cd`, `ls`, `cat`, variáveis de ambiente, `Ctrl+C`) | Todo deploy passa por linha de comando. Painéis web escondem o essencial. | [MIT *Missing Semester*](https://missing.csail.mit.edu/) (EN, ~6 h) · [`variaveis-de-ambiente-e-segredos`](../variaveis-de-ambiente-e-segredos/01-introducao-leigo.md) desta pasta |
| **Git básico** (`clone`, `add`, `commit`, `push`, branch) | Praticamente toda plataforma moderna faz deploy a partir de um repositório Git. | [Pro Git](https://git-scm.com/book/pt-br/v2) (livro oficial, gratuito, em PT-BR) |
| **HTTP** (método, status, cabeçalho, corpo) | Você vai depurar 502, 504, CORS e redirecionamento. Sem isso é adivinhação. | [`apis`](../apis/00-MAPA.md) e [`portas-de-rede`](../portas-de-rede/00-MAPA.md) desta pasta |
| **Uma linguagem de backend** (Node, Python, Go, Java, PHP, Ruby…) | Você precisa ter *algo* para hospedar. O projeto-modelo usa **Node.js 22+**. | [`spa-single-page-application`](../spa-single-page-application/00-MAPA.md) para o lado do frontend |
| **SQL básico** (`SELECT`, `INSERT`, `JOIN`, chave primária) | Você vai criar tabelas e depurar consultas lentas. | [`sql`](../sql/00-MAPA.md) e [`postgresql`](../postgresql/00-MAPA.md) desta pasta |
| **Ler um `.env`** e entender por que segredo não vai para o Git | O erro de segurança nº 1 em deploy é commitar credencial. | [`variaveis-de-ambiente-e-segredos`](../variaveis-de-ambiente-e-segredos/01-introducao-leigo.md) |

## 2. Conhecimento que ajuda muito (mas não bloqueia)

| O que | O que ele destrava | Onde aprender |
|---|---|---|
| **Docker e containers** | Metade das plataformas aceita `Dockerfile`; sem ele você fica limitado ao que a plataforma detecta sozinha. | [`docker`](../docker/00-MAPA.md) e [`curso-docker`](../curso-docker/00-indice.md) desta pasta |
| **DNS** (A, AAAA, CNAME, TTL) | Apontar seu domínio próprio, entender por que "ainda não propagou". | [`50-operacao-e-ciclo-de-vida.md`](50-operacao-e-ciclo-de-vida.md), seção 2 |
| **TLS/HTTPS e certificados** | Entender o que a plataforma faz por você e por que às vezes falha. | [`jwt`](../jwt/00-MAPA.md) para o lado de autenticação; [`50`](50-operacao-e-ciclo-de-vida.md) para certificado |
| **Redis: comandos básicos** (`GET`, `SET`, `EXPIRE`, `INCR`) | Usar cache de verdade em vez de "guardar num dicionário na memória do processo". | [`05-manual-de-uso.md`](05-manual-de-uso.md), seção Redis |
| **CI/CD** (GitHub Actions) | Deploy automatizado, testes antes de subir, rollback. | [`testes-automatizados`](../testes-automatizados/00-MAPA.md) desta pasta |
| **Noções de custo em nuvem** (egress, vCPU-hora, GB-mês) | Ler tabela de preço sem levar susto. | [`80-custos-e-licencas.md`](80-custos-e-licencas.md) |

## 3. Ambiente e hardware

| Item | Mínimo | Recomendado | Observação |
|---|---|---|---|
| **Sistema operacional** | Linux (qualquer distro mantida), macOS 13+, Windows 10 22H2+ | Linux ou macOS; no Windows, **WSL2** | Windows nativo funciona, mas metade dos tutoriais assume shell POSIX |
| **RAM** | 8 GB | 16 GB | Docker Compose com Postgres + Redis + app consome ~1,5 GB |
| **Disco livre** | 15 GB | 40 GB | Imagens Docker crescem rápido; veja limpeza em [`03`](03-instalacao.md) |
| **Arquitetura** | x86-64 ou ARM64 | — | Apple Silicon (M1–M4) exige atenção com imagens `amd64`; veja [`75`](75-armadilhas.md), armadilha 11 |
| **Internet** | 5 Mbps | 30 Mbps+ | Build de imagem baixa centenas de MB |

## 4. Contas em serviços

Você vai precisar de contas. Estas são as que o material usa. **Nenhuma das marcadas com ✅
exige cartão de crédito para o plano gratuito** (verificado em 18/08/2026).

| Serviço | Para quê | Cartão exigido? | Link |
|---|---|---|---|
| **GitHub** | Guardar o código; quase toda plataforma faz deploy a partir dele | ✅ não | github.com |
| **Cloudflare** | Frontend (Pages), DNS, Workers | ✅ não | dash.cloudflare.com |
| **Render** | Backend gratuito | ✅ não | render.com |
| **Neon** | PostgreSQL gratuito, região São Paulo | ✅ não | neon.com |
| **Upstash** | Redis gratuito | ✅ não | upstash.com |
| **Supabase** | Alternativa de PostgreSQL + auth + storage | ✅ não | supabase.com |
| **Railway** | Alternativa de backend | ⚠️ o *trial* não exige; o plano Hobby (US$ 5) exige | railway.com |
| **Fly.io** | Alternativa de backend com região no Brasil | ⚠️ sim, desde 2024 | fly.io |
| **AWS / GCP / Azure** | Só se você for para o caminho "nuvem grande" | ⚠️ **sim, sempre** | — |

> **Aviso prático.** Serviços com camada gratuita sofrem abuso pesado (mineração de
> criptomoeda, spam, phishing). Por isso, **verificação por telefone, conta GitHub com
> histórico, ou cartão só para identificação** viraram norma entre 2024 e 2026. Se a sua conta
> for barrada na criação, quase sempre é filtro antifraude, não erro seu — veja
> [`75`](75-armadilhas.md), armadilha 30.

## 5. Tempo realista até cada nível

Números da minha experiência ensinando isto; assuma que você já tem os pré-requisitos
indispensáveis da seção 1. **São horas de estudo focado, não de calendário.**

| Nível | O que você consegue fazer | Tempo |
|---|---|---|
| **Primeiro deploy** | Um "hello world" público com URL HTTPS | **1 a 3 horas** |
| **Pilha de quatro peças no ar** | Frontend + backend + Postgres + Redis conversando, tudo gratuito | **6 a 12 horas** |
| **Deploy defensável** | Domínio próprio, TLS, migrações versionadas, backup testado, CI, variáveis de ambiente organizadas, logs | **30 a 60 horas** |
| **Escolher plataforma com critério** | Ler tabela de preço, prever fatura, comparar cinco alternativas, saber o gatilho de troca | **20 a 40 horas** (é o Bloco B deste material) |
| **Operar em produção com usuários pagantes** | Monitoramento, alerta, plano de rollback, resposta a incidente, capacidade planejada | **200 a 500 horas + pelo menos um incidente real** |
| **Nível de arquiteto/SRE** | Modelar custo, capacidade e confiabilidade; defender a decisão diante de auditoria | **2 a 5 anos** |

> **Honestidade sobre o último item:** não existe atalho. O que separa alguém que "sabe fazer
> deploy" de alguém que "sabe operar" é ter estado de plantão quando algo quebrou às 2h da
> manhã. Nenhum curso substitui isso — mas o [`70-pratica.md`](70-pratica.md) simula três
> incidentes de propósito para encurtar o caminho.

## 6. Rota de resgate

**Se falta terminal.** Faça só as aulas 1 e 2 do *Missing Semester* (2 h). Basta para começar.

**Se falta Git.** Você consegue fazer o primeiro deploy sem Git, subindo por CLI
(`render deploy`, `vercel`, `wrangler deploy`). Mas você não vai conseguir automatizar nada.
Invista 3 horas no Git antes de qualquer outra coisa — é o melhor retorno de tempo da lista.

**Se falta uma linguagem de backend.** Use o [`07-projeto-modelo/`](07-projeto-modelo/README.md)
deste material como ponto de partida: ele já vem pronto, roda, e você aprende alterando.

**Se falta SQL.** Faça o deploy usando o projeto-modelo (que já traz o esquema pronto) e
estude SQL em paralelo com [`sql`](../sql/00-MAPA.md). Não trave aqui.

**Se falta Docker.** Comece pelas plataformas que **não exigem** Docker: Render, Railway,
Vercel e Cloudflare detectam Node/Python automaticamente. Aprenda Docker depois — mas
aprenda, porque é ele que impede o aprisionamento de fornecedor.

**Se falta hardware.** Use **GitHub Codespaces** — a conta pessoal GitHub Free inclui
**120 horas-núcleo por mês** (o que dá ~60 h numa máquina de 2 núcleos) e **15 GB-mês** de
armazenamento; a GitHub Pro inclui 180 h e 20 GB-mês (verificado em 18/08/2026) ou **Gitpod**. Tudo neste material roda num Codespace.
Veja [`03-instalacao.md`](03-instalacao.md), seção "Alternativa sem instalar nada".

**Se falta cartão de crédito.** Todo o caminho principal deste material foi escolhido para
funcionar sem cartão. Você perde AWS, GCP, Azure, Fly.io e Railway pago — e não perde nada
essencial para aprender.

**Se falta tempo.** Faça só: [`01`](01-introducao-leigo.md) → [`04`](04-como-comecar.md) →
[`40`](40-arquiteturas-de-referencia.md). São ~4 horas e cobrem 80% do valor prático.

---

## Autoteste

1. Quais dos pré-requisitos da seção 1 você realmente tem? Seja honesto e liste os que faltam.
2. Por que Git é considerado indispensável e Docker apenas "ajuda muito"?
3. Quais serviços deste material exigem cartão de crédito e quais não exigem?
4. Quanto tempo, realisticamente, até você ter uma pilha de quatro peças no ar?
5. Você não tem máquina boa. Qual é a rota de resgate e qual o seu limite mensal nela?
6. Por que camadas gratuitas passaram a exigir verificação de identidade entre 2024 e 2026?
