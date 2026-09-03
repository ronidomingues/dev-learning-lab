# Salesforce — Mapa do Assunto

`Nível: do zero absoluto ao de pesquisa` · `Última atualização: 11/08/2026`
`Plataforma na versão: Summer '26 · API 67.0 · Salesforce CLI 2.146.x`

---

## O que é este material

Um curso completo sobre **Salesforce**: o produto, a plataforma, a linguagem, a arquitetura
interna, a economia do ecossistema e a fronteira de pesquisa/produto em agosto de 2026.

Ele responde três perguntas na ordem em que elas realmente aparecem na vida de alguém:

1. **O que é isso e por que existe?** → Bloco A, arquivos `01` e `11`.
2. **Como eu começo hoje, sem gastar nada?** → Bloco A, arquivos `02` a `07`.
3. **Como isso funciona por dentro, e onde estão os limites?** → Blocos B e C.

Salesforce é um assunto **grande**. Ele não é uma linguagem, nem um framework, nem um
banco de dados — é um sistema operacional de negócio multi-inquilino com linguagem própria
(Apex), modelo de dados próprio (metadados + SOQL), modelo de segurança próprio
(perfis, sharing, campos), ciclo de release próprio (3 por ano) e uma economia própria
(licenças por usuário, créditos de IA, consultoria, certificações). Este material trata
de todos esses eixos, não só do código.

---

## O que você saberá ao final

- Explicar para um leigo o que Salesforce faz e por que uma empresa paga por isso.
- Criar uma org gratuita, instalar todo o ferramental e publicar código nela.
- Modelar dados na plataforma (objetos, campos, relacionamentos) e saber quando **não** usar Salesforce.
- Escrever Apex correto — com testes, bulk-safe, respeitando os *governor limits* — e LWC.
- Automatizar processos com Flow e saber quando Flow perde para Apex e vice-versa.
- Configurar segurança em camadas: perfis, permission sets, OWD, roles, sharing rules, FLS.
- Integrar Salesforce com o resto do mundo (REST, SOAP, Bulk, Streaming, GraphQL, Platform Events, MuleSoft).
- Operar um ciclo de DevOps real: source-tracked orgs, scratch orgs, packages, CI.
- Explicar a arquitetura multi-inquilino de dentro para fora: UDD, pivot tables, query optimizer, por que existem limites.
- Estimar custo de verdade — licença, add-on, Data Cloud, créditos Agentforce, consultoria, custo de saída.
- Escolher uma trilha de certificação e estudar de graça até ela.

---

## Roteiro de leitura

### Caminho rápido (fim de semana, "quero entender e mexer")
`01` → `02` → `03` → `04` → `06` → `07-projeto-modelo/` → `75`

### Caminho de administrador
`01` → `10` → `12` → `13` → `14` → `20` → `70` → `75` → `85`

### Caminho de desenvolvedor
`01` → `03` → `04` → `10` → `12` → `15` → `16` → `17` → `18` → `07-projeto-modelo/` → `70` → `75`

### Caminho de arquiteto / pesquisador
todo o Bloco B em ordem, com peso em `19` → `60` → `65`, depois `95`

### Caminho de quem decide compra
`01` → `11` → `20` → `80` → `75` → `65`

---

## Arquivos

### BLOCO A · Porta de entrada (01–09)

| Arquivo | Nível | Conteúdo |
|---|---|---|
| [01-introducao-leigo.md](01-introducao-leigo.md) | iniciante | O que é, para que serve, por que existe. Zero jargão. |
| [02-pre-requisitos.md](02-pre-requisitos.md) | iniciante | O que saber e ter antes. Tempo realista. Rota de resgate. |
| [03-instalacao.md](03-instalacao.md) | iniciante | Manual de campo: org, Node, CLI, VS Code, Git, Java, por SO. |
| [04-como-comecar.md](04-como-comecar.md) | iniciante | Do ambiente pronto ao primeiro Apex e primeiro LWC rodando. |
| [05-manual-de-uso.md](05-manual-de-uso.md) | intermediário | Referência consultável: `sf`, SOQL, Apex, metadados, Setup. |
| [06-exemplos.md](06-exemplos.md) | intermediário | 14 exemplos completos e executáveis, do trivial ao de produção. |
| [07-projeto-modelo/](07-projeto-modelo/README.md) | intermediário | App completo: gestão de chamados de manutenção. Roda de verdade. |

### BLOCO B · Núcleo (10–69)

| Arquivo | Nível | Conteúdo |
|---|---|---|
| [10-fundamentos.md](10-fundamentos.md) | iniciante | Vocabulário, modelos mentais, o que é uma org, metadados vs. dados. |
| [11-historia.md](11-historia.md) | iniciante | 1999→2026. Que problema resolveu, o que veio antes, as aquisições. |
| [12-modelo-de-dados.md](12-modelo-de-dados.md) | intermediário | Objetos, campos, relacionamentos, SOQL/SOSL, skew, normalização. |
| [13-seguranca-e-compartilhamento.md](13-seguranca-e-compartilhamento.md) | intermediário | As 5 camadas. OWD, role hierarchy, sharing, FLS, Shield. |
| [14-automacao-declarativa.md](14-automacao-declarativa.md) | intermediário | Flow por dentro, ordem de execução, migração de Workflow/PB. |
| [15-apex.md](15-apex.md) | intermediário→avançado | A linguagem, triggers, testes, assíncrono, limites, v67 user mode. |
| [16-lightning-web-components.md](16-lightning-web-components.md) | intermediário→avançado | LWC, Locker/Lightning Web Security, wire, eventos, LWR. |
| [17-integracao-e-apis.md](17-integracao-e-apis.md) | avançado | REST, Bulk 2.0, Streaming, Platform Events, CDC, GraphQL, OAuth. |
| [18-devops-e-alm.md](18-devops-e-alm.md) | avançado | Sandboxes, scratch orgs, packages, CI/CD, DevOps Center. |
| [19-multitenancy-arquitetura.md](19-multitenancy-arquitetura.md) | avançado→pesquisa | UDD, pivot tables, query optimizer, por que os limites existem. |
| [20-clouds-e-produtos.md](20-clouds-e-produtos.md) | intermediário | Sales, Service, Data Cloud, Agentforce, MuleSoft, Tableau, Slack. |
| [60-teoria-avancada.md](60-teoria-avancada.md) | pesquisa | Isolamento de performance, escalonamento justo, provas e limites. |
| [65-estado-da-arte.md](65-estado-da-arte.md) | pesquisa | Agosto/2026: agentes, Data 360, MCP, o que está em disputa. |

### BLOCO C · Prática e erros (70–79)

| Arquivo | Nível | Conteúdo |
|---|---|---|
| [70-pratica.md](70-pratica.md) | todos | 10 laboratórios progressivos com critério de aprovação. |
| [75-armadilhas.md](75-armadilhas.md) | todos | Erros clássicos, mitos, más práticas e por que persistem. |

### BLOCO D · Economia e ecossistema (80–89)

| Arquivo | Nível | Conteúdo |
|---|---|---|
| [80-custos-e-licencas.md](80-custos-e-licencas.md) | todos | Preços com data, licenças, custo oculto, custo de saída. |
| [85-cursos-e-certificacoes.md](85-cursos-e-certificacoes.md) | todos | Cursos grátis PT/EN/FR e o mapa das certificações. |

### BLOCO E · Fontes (90–99)

| Arquivo | Nível | Conteúdo |
|---|---|---|
| [90-bibliografia.md](90-bibliografia.md) | todos | Livros com edição, nível e o que envelheceu. |
| [95-referencias.md](95-referencias.md) | todos | Docs oficiais, papers, repositórios, pessoas a seguir. |
| [GLOSSARIO.md](GLOSSARIO.md) | todos | Todo o jargão definido. |

---

## Status por bloco

| Bloco | Status | Observação |
|---|---|---|
| A · Porta de entrada | ✅ | 7 documentos + projeto-modelo executável |
| B · Núcleo | ✅ | 13 documentos, fundamentos → arquitetura interna → estado da arte |
| C · Prática e erros | ✅ | 10 laboratórios + catálogo de armadilhas |
| D · Economia | ✅ | Preços consultados em 11/08/2026 |
| E · Fontes | ✅ | Bibliografia e referências verificadas |
| Glossário | ✅ | ~150 termos |

Legenda: ✅ completo · 🟡 parcial · ⬜ pendente

---

## Aviso de validade

Salesforce lança **três releases por ano** (Spring, Summer, Winter) e muda preços com
frequência. Este material foi escrito sobre:

- **Release:** Summer '26 — **API 67.0**
- **Salesforce CLI:** 2.146.x
- **Data das consultas de preço e curso:** 11/08/2026
- **Câmbio usado para ordens de grandeza:** US$ 1 ≈ R$ 5,11 (11/08/2026)

O que envelhece mais rápido, em ordem: `80-custos-e-licencas.md` (meses),
`65-estado-da-arte.md` (meses), `03-instalacao.md` (releases), `85-cursos-e-certificacoes.md`
(um ano). O núcleo conceitual (`10`, `12`, `13`, `19`, `60`) envelhece em década.

---

## Autoteste do mapa

1. Salesforce é um CRM, uma plataforma ou os dois? Por que a resposta importa para o preço?
2. Quantos releases por ano a plataforma tem, e o que isso implica para o seu código?
3. Qual arquivo você leria primeiro se precisasse justificar a compra para um CFO?
4. Qual bloco você leria se seu Apex estivesse estourando limite em produção?
5. O que "API 67.0" identifica — o produto, o release, ou o contrato do seu código com a plataforma?
