# Hospedagem de Aplicações Web — Mapa do Assunto

`Nível: do zero absoluto ao de pesquisa` · `Última atualização: 18/08/2026`
`Preços, limites e planos consultados na web em 18/08/2026 — veja` [`80-custos-e-licencas.md`](80-custos-e-licencas.md)

---

## A pergunta que originou este material

> *"Quais são, hoje, as plataformas gratuitas e as melhores para hospedagem de sistemas web
> com backend, banco de dados PostgreSQL, banco de acesso rápido Redis e frontend?"*

A resposta curta está em [`40-arquiteturas-de-referencia.md`](40-arquiteturas-de-referencia.md).
Se você tem cinco minutos, leia só aquele arquivo. Se você vai **colocar dinheiro, tempo ou a
reputação de um sistema em produção** nessa decisão, leia o resto — porque a resposta curta
tem uma dúzia de condicionais que decidem se ela custa R$ 0 ou R$ 3.000 por mês.

---

## O que é este material

Um curso completo sobre **onde e como rodar um sistema web de quatro peças** — frontend,
backend, PostgreSQL e Redis — indo do "o que é um servidor" até a teoria de custo marginal
de plataformas multi-inquilino e o porquê econômico de camadas gratuitas existirem.

Ele responde, na ordem em que as perguntas aparecem na vida real:

1. **O que é hospedar, afinal?** → [`01`](01-introducao-leigo.md), [`10`](10-fundamentos.md), [`11`](11-historia.md)
2. **Como coloco isso no ar hoje, de graça?** → [`03`](03-instalacao.md) a [`07`](07-projeto-modelo/README.md)
3. **Quais são as plataformas, uma a uma, com números reais?** → [`20`](20-catalogo-backend-paas.md), [`25`](25-catalogo-postgresql.md), [`30`](30-catalogo-redis.md), [`35`](35-catalogo-frontend.md)
4. **Qual pilha eu escolho?** → [`40`](40-arquiteturas-de-referencia.md)
5. **E se meus usuários estão no Brasil?** → [`45`](45-brasil-latencia-e-lgpd.md)
6. **Como opero isso sem me arrepender?** → [`50`](50-operacao-e-ciclo-de-vida.md), [`75`](75-armadilhas.md)
7. **Por que é grátis? Quem paga?** → [`55`](55-economia-do-gratuito.md), [`80`](80-custos-e-licencas.md)
8. **O que é fronteira de pesquisa aqui?** → [`60`](60-teoria-avancada.md), [`65`](65-estado-da-arte.md)

Três ideias que o material repete porque são a origem de metade dos erros de quem escolhe
plataforma:

- **"Grátis" nunca é grátis: é subsidiado, limitado ou temporário — e você precisa saber qual dos três.**
  Camada gratuita não é caridade; é aquisição de cliente, e o dono pode encerrá-la (Heroku fez
  em 2022, Fly.io em 2024, Xata em 2026).
- **A parte cara não é o backend: é o estado.** Rodar código é barato e escala a zero.
  Guardar dados com durabilidade, backup e disponibilidade custa dinheiro sempre — 24 horas
  por dia, mesmo quando ninguém acessa. Toda camada gratuita é generosa com CPU e mesquinha
  com disco.
- **O maior custo oculto não está na fatura: é a migração.** Você escolhe uma plataforma por
  um fim de semana e convive com ela por três anos. O critério que mais importa é
  *quão fácil é sair*, não *quão fácil é entrar*.

---

## O que você saberá ao final

- Explicar a um leigo o que é hospedar um sistema e por que existem "quatro caixas" (frontend, backend, banco, cache).
- Distinguir IaaS, PaaS, CaaS, FaaS, BaaS e edge — e saber qual você está comprando.
- Instalar todo o ferramental de deploy (Docker, Node, `psql`, `redis-cli`, `git`, e as CLIs de sete plataformas) em Linux, macOS e Windows.
- Colocar um sistema completo de quatro peças no ar, de graça, em menos de uma hora.
- Ler a tabela de preços de qualquer plataforma e prever a fatura antes de receber.
- Escolher entre Render, Railway, Fly.io, Koyeb, Northflank, Cloud Run, Cloudflare e um VPS com Coolify — com critério, não por moda.
- Escolher entre Neon, Supabase, Aiven, Render e Postgres auto-hospedado — sabendo o que cada um cobra e quando pausa.
- Escolher entre Upstash, Redis Cloud, Valkey gerenciado e Redis auto-hospedado — e entender a confusão de licença Redis/Valkey de 2024–2025.
- Montar cinco arquiteturas de referência, de R$ 0 a alguns milhares por mês, com o gatilho de troca de cada uma.
- Estimar latência para usuários no Brasil e saber quais plataformas têm região em São Paulo.
- Operar: domínio, TLS, migrações, backup, segredos, CI/CD, observabilidade, rollback.
- Explicar por que cold start existe, por que pool de conexões do PostgreSQL é o gargalo escondido, e a matemática do dimensionamento.
- Saber o que envelheceu (Heroku free, ElephantSQL, Xata Lite) e o que está na fronteira (WASM no edge, Postgres serverless, sandboxes de agentes de IA).

---

## Roteiro de leitura

### Caminho relâmpago — "quero só a resposta" (30 min)
[`40`](40-arquiteturas-de-referencia.md) → [`80`](80-custos-e-licencas.md) → [`75`](75-armadilhas.md)

### Caminho do iniciante — "nunca fiz deploy" (um fim de semana)
[`01`](01-introducao-leigo.md) → [`02`](02-pre-requisitos.md) → [`03`](03-instalacao.md) → [`04`](04-como-comecar.md) → [`07`](07-projeto-modelo/README.md) → [`06`](06-exemplos.md) → [`75`](75-armadilhas.md)

### Caminho do desenvolvedor que vai decidir a pilha
[`10`](10-fundamentos.md) → [`12`](12-anatomia-de-um-deploy.md) → [`20`](20-catalogo-backend-paas.md) → [`25`](25-catalogo-postgresql.md) → [`30`](30-catalogo-redis.md) → [`35`](35-catalogo-frontend.md) → [`40`](40-arquiteturas-de-referencia.md) → [`45`](45-brasil-latencia-e-lgpd.md) → [`50`](50-operacao-e-ciclo-de-vida.md)

### Caminho de quem paga a conta (fundador, gestor, arquiteto)
[`01`](01-introducao-leigo.md) → [`40`](40-arquiteturas-de-referencia.md) → [`55`](55-economia-do-gratuito.md) → [`80`](80-custos-e-licencas.md) → [`45`](45-brasil-latencia-e-lgpd.md) → [`75`](75-armadilhas.md)

### Caminho de profundidade (SRE, pesquisador)
todo o Bloco B em ordem, com peso em [`50`](50-operacao-e-ciclo-de-vida.md) → [`60`](60-teoria-avancada.md) → [`65`](65-estado-da-arte.md), depois [`95`](95-referencias.md)

---

## Os arquivos

### Bloco A · Porta de entrada
| Arquivo | O que tem dentro |
|---|---|
| [`01-introducao-leigo.md`](01-introducao-leigo.md) | O que é hospedar, sem uma linha de jargão. A analogia do restaurante. |
| [`02-pre-requisitos.md`](02-pre-requisitos.md) | O que saber e ter antes. Tempo realista. Rota de resgate. |
| [`03-instalacao.md`](03-instalacao.md) | Manual de campo: Git, Node, Docker, `psql`, `redis-cli` e 7 CLIs de plataforma, nos 3 SOs. |
| [`04-como-comecar.md`](04-como-comecar.md) | Do ambiente pronto a uma URL pública funcionando, com verificação. |
| [`05-manual-de-uso.md`](05-manual-de-uso.md) | Referência por tarefa das CLIs (`render`, `railway`, `flyctl`, `vercel`, `wrangler`, `supabase`, `neonctl`, `gh`). |
| [`06-exemplos.md`](06-exemplos.md) | 14 receitas completas, do trivial ao caso de produção. |
| [`07-projeto-modelo/`](07-projeto-modelo/README.md) | **Encurtador de URLs** completo: API Node + PostgreSQL + Redis + frontend, testes, Docker Compose e 4 manifestos de deploy. |

### Bloco B · Núcleo
| Arquivo | O que tem dentro |
|---|---|
| [`10-fundamentos.md`](10-fundamentos.md) | Servidor, processo, porta, estado. IaaS→PaaS→CaaS→FaaS→BaaS→edge. Stateless vs. stateful. |
| [`11-historia.md`](11-historia.md) | Do CGI e da hospedagem compartilhada ao Heroku, ao Docker, ao serverless e à volta do VPS. |
| [`12-anatomia-de-um-deploy.md`](12-anatomia-de-um-deploy.md) | O que acontece entre o `git push` e a resposta HTTP. Build, imagem, health check, rollout, DNS, TLS. |
| [`20-catalogo-backend-paas.md`](20-catalogo-backend-paas.md) | 14 plataformas de backend, uma a uma, com limites e números de 18/08/2026. |
| [`25-catalogo-postgresql.md`](25-catalogo-postgresql.md) | 12 opções de PostgreSQL gerenciado e o que cada camada gratuita realmente entrega. |
| [`30-catalogo-redis.md`](30-catalogo-redis.md) | Redis, Valkey, Dragonfly e a crise de licença de 2024–2025. Quem oferece de graça. |
| [`35-catalogo-frontend.md`](35-catalogo-frontend.md) | CDN, static hosting e edge: Cloudflare, Vercel, Netlify, GitHub Pages, Firebase, Render. |
| [`40-arquiteturas-de-referencia.md`](40-arquiteturas-de-referencia.md) | **Cinco pilhas montadas**, com custo, limite de crescimento e gatilho de troca. |
| [`45-brasil-latencia-e-lgpd.md`](45-brasil-latencia-e-lgpd.md) | Quem tem região em São Paulo, quanto custa a distância em milissegundos, e o que a LGPD exige. |
| [`50-operacao-e-ciclo-de-vida.md`](50-operacao-e-ciclo-de-vida.md) | Domínio, TLS, segredos, migrações, backup, CI/CD, observabilidade, rollback, incidente. |
| [`55-economia-do-gratuito.md`](55-economia-do-gratuito.md) | Por que existe camada gratuita, quem paga, e como prever quando ela acaba. |
| [`60-teoria-avancada.md`](60-teoria-avancada.md) | Cold start, filas M/M/c, pool de conexões, autoescala como controle, CAP e custo marginal. |
| [`65-estado-da-arte.md`](65-estado-da-arte.md) | O que mudou até agosto de 2026 e o que está em disputa. |

### Bloco C · Prática e erros
| Arquivo | O que tem dentro |
|---|---|
| [`70-pratica.md`](70-pratica.md) | 12 laboratórios progressivos, do primeiro deploy ao teste de carga e ao rollback. |
| [`75-armadilhas.md`](75-armadilhas.md) | 32 erros clássicos e 8 mitos, com o custo de cada um. |

### Bloco D · Economia e ecossistema
| Arquivo | O que tem dentro |
|---|---|
| [`80-custos-e-licencas.md`](80-custos-e-licencas.md) | **Tabela mestra de preços**, consulta de 18/08/2026, em USD/EUR e ordem de grandeza em BRL. Licenças e custo oculto. |
| [`85-cursos-e-certificacoes.md`](85-cursos-e-certificacoes.md) | Cursos gratuitos PT/EN/FR pesquisados na web, e certificações que valem (e as que não valem). |

### Bloco E · Fontes
| Arquivo | O que tem dentro |
|---|---|
| [`90-bibliografia.md`](90-bibliografia.md) | Livros com edição e ano, o que envelheceu, o que é legalmente gratuito. |
| [`95-referencias.md`](95-referencias.md) | Docs oficiais, RFCs, papers, changelogs e pessoas para acompanhar. |
| [`GLOSSARIO.md`](GLOSSARIO.md) | ~150 termos definidos. |

---

## Status por bloco

| A | B | C | D | E | Glossário |
|---|---|---|---|---|---|
| ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

**Validade do material.** Este assunto envelhece mais rápido que qualquer outro desta pasta.
A parte conceitual (blocos `10`, `11`, `12`, `60`) vale por anos. As tabelas de preço e limite
(`20`, `25`, `30`, `35`, `80`) têm **prazo de validade de aproximadamente seis meses**.
Cada arquivo que envelhece traz a data no topo e as fontes no rodapé — confira antes de decidir
com base neles.

**O que foi executado durante a escrita:** o projeto-modelo roda localmente com Docker Compose
e tem 24 testes automatizados. O que **não** foi executado — deploy real em cada uma das 14
plataformas — está declarado no [`README do projeto-modelo`](07-projeto-modelo/README.md) e em
[`95-referencias.md`](95-referencias.md).

---

## Autoteste do mapa

1. Por que a parte cara de uma aplicação web moderna é o estado, e não o cômputo?
2. Qual arquivo você lê se quer apenas a recomendação final?
3. Qual é o prazo de validade prático das tabelas de preço deste material, e por quê?
4. Cite três camadas gratuitas que deixaram de existir entre 2022 e 2026.
5. Qual critério este material afirma ser o mais importante ao escolher plataforma — e por quê não é o preço?
