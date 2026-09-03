# 95 · Referências

`Nível: todos` · `Verificado em 11/08/2026`

Fontes primárias, ferramentas e pessoas. Tudo verificado na data acima.

---

## 1. Documentação oficial — a fonte da verdade

| Recurso | URL |
|---|---|
| **Salesforce Developers** (portal) | https://developer.salesforce.com |
| **Apex Developer Guide** | https://developer.salesforce.com/docs/atlas.en-us.apexcode.meta/apexcode/ |
| **Ordem de execução dos triggers** ⭐ | https://developer.salesforce.com/docs/atlas.en-us.apexcode.meta/apexcode/apex_triggers_order_of_execution.htm |
| **SOQL and SOSL Reference** | https://developer.salesforce.com/docs/atlas.en-us.soql_sosl.meta/soql_sosl/ |
| **Lightning Web Components Guide** | https://developer.salesforce.com/docs/component-library/documentation/lwc |
| **Component Library** (referência de componentes base) | https://developer.salesforce.com/docs/component-library/overview/components |
| **Lightning Design System (SLDS)** | https://www.lightningdesignsystem.com |
| **Salesforce DX Developer Guide** | https://developer.salesforce.com/docs/atlas.en-us.sfdx_dev.meta/sfdx_dev/ |
| **Salesforce CLI Command Reference** | https://developer.salesforce.com/docs/atlas.en-us.sfdx_cli_reference.meta/sfdx_cli_reference/ |
| **REST API Developer Guide** | https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/ |
| **Bulk API 2.0 Guide** | https://developer.salesforce.com/docs/atlas.en-us.api_asynch.meta/api_asynch/ |
| **Metadata API Guide** | https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/ |
| **Integration Patterns and Practices** ⭐ | https://developer.salesforce.com/docs/atlas.en-us.integration_patterns_and_practices.meta/integration_patterns_and_practices/ |
| **Governor Limits** ⭐ | https://developer.salesforce.com/docs/atlas.en-us.apexcode.meta/apexcode/apex_gov_limits.htm |
| **Salesforce Help** (admin, funcional) | https://help.salesforce.com |
| **Release Notes** | https://help.salesforce.com/s/articleView?id=release-notes.salesforce_release_notes.htm |
| **Salesforce Architects** ⭐ | https://architect.salesforce.com |
| **Well-Architected Framework** | https://architect.salesforce.com/well-architected |

⭐ = as cinco que eu manteria abertas o tempo todo.

---

## 2. Ferramentas

| Ferramenta | URL | Para quê |
|---|---|---|
| **Salesforce CLI** | https://developer.salesforce.com/tools/salesforcecli · https://www.npmjs.com/package/@salesforce/cli | terminal |
| **VS Code Extension Pack** | https://marketplace.visualstudio.com/items?itemName=salesforce.salesforcedx-vscode | IDE |
| **Code Builder** | https://developer.salesforce.com/tools/vscode/en/codebuilder/about | VS Code no navegador |
| **Salesforce Code Analyzer** | https://developer.salesforce.com/docs/platform/salesforce-code-analyzer/overview | análise estática |
| **Salesforce Inspector Reloaded** (extensão de navegador) | https://github.com/tprouvot/Salesforce-Inspector-reloaded | **indispensável** — inspecionar dados, metadados e permissões direto na org |
| **sfdx-git-delta** | https://github.com/scolladon/sfdx-git-delta | deploy incremental por diff de Git |
| **SFDMU** (data move utility) | https://github.com/forcedotcom/SFDX-Data-Move-Utility | migração de dados entre orgs |
| **fflib-apex-common** | https://github.com/apex-enterprise-patterns/fflib-apex-common | biblioteca dos Enterprise Patterns |
| **ApexMocks** | https://github.com/apex-enterprise-patterns/fflib-apex-mocks | mocking em testes Apex |
| **Salesforce Optimizer** | dentro da org: `Setup → Optimizer` | relatório de saúde da org, gratuito |
| **Salesforce Trust** | https://status.salesforce.com | status de instâncias, janelas de manutenção |
| **Workbench** | https://workbench.developerforce.com | SOQL, REST, metadados via navegador |
| **Postman — Salesforce collection** | https://www.postman.com/salesforce-developers | testar as APIs |

> **Se você instalar só uma ferramenta além da CLI, instale o Salesforce Inspector
> Reloaded.** Ele economiza mais tempo por dia que qualquer outra coisa: ver e editar
> campos que não estão no layout, exportar dados rápido, checar permissões de um campo,
> pular direto para o Setup de um objeto.

---

## 3. Código-fonte aberto da Salesforce

| Repositório | Licença | O que é |
|---|---|---|
| https://github.com/salesforce/lwc | **MIT** | o framework LWC — roda fora do Salesforce |
| https://github.com/forcedotcom/cli | BSD-3-Clause | a Salesforce CLI |
| https://github.com/forcedotcom/sfdx-core | BSD-3-Clause | biblioteca base da CLI |
| https://github.com/forcedotcom/code-analyzer | — | analisador estático |
| https://github.com/salesforce/design-system-react | BSD-3-Clause | SLDS em React |
| https://github.com/trailheadapps | — | **apps de exemplo oficiais** (LWC Recipes, E-Bikes, DreamHouse) |

**`trailheadapps/lwc-recipes`** merece destaque: é um catálogo de receitas de LWC, cada uma
mínima e executável. É a melhor referência prática de LWC que existe, e é gratuita.

---

## 4. Comunidade

| Recurso | URL | Por que |
|---|---|---|
| **Salesforce Stack Exchange** ⭐ | https://salesforce.stackexchange.com | a melhor fonte de respostas técnicas do ecossistema |
| **Trailblazer Community** | https://trailhead.salesforce.com/trailblazercommunity | grupos oficiais, inclusive em português |
| **Salesforce Ben** | https://www.salesforceben.com | o blog de referência: carreira, análise de release, guias |
| **Apex Hours** | https://www.apexhours.com | sessões técnicas gratuitas, conteúdo avançado |
| **Reddit r/salesforce** | https://reddit.com/r/salesforce | discussão franca sobre carreira e mercado |
| **Salesforce Developers (YouTube)** | https://www.youtube.com/@SalesforceDevs | onde a informação nova aparece primeiro |
| **Salesforce Brasil (YouTube)** | https://www.youtube.com/c/SalesforceBrasil | conteúdo institucional em português |

---

## 5. Blogs técnicos que valem acompanhar

| Blog | Foco |
|---|---|
| https://developer.salesforce.com/blogs | oficial de desenvolvedores |
| https://www.salesforceben.com | ecossistema, carreira, certificação |
| https://www.apexhours.com | técnico avançado |
| https://automationchampion.com | Flow e automação declarativa |
| https://www.jitendrazaa.com | integração, arquitetura, custos |
| https://architect.salesforce.com/decision-guides | guias de decisão de arquitetura, oficiais |

---

## 6. Pessoas de referência

Não é uma lista de "influencers" — são pessoas cujo trabalho técnico é substantivo e
verificável. Busque pelos nomes; os canais mudam.

| Pessoa | Contribuição |
|---|---|
| **Parker Harris** | cofundador e CTO; fala sobre a arquitetura da plataforma |
| **Andrew Fawcett** | autor de *Salesforce Platform Enterprise Architecture*; criador dos Enterprise Patterns e da `fflib` |
| **Dan Appleman** | autor de *Advanced Apex Programming*; análise profunda de limites e arquitetura |
| **Paul Battisson** | autor de *Mastering Apex Programming*; conteúdo técnico em vídeo |
| **Amit Chaudhary** | Apex Hours; um dos maiores volumes de conteúdo técnico gratuito do ecossistema |
| **Rakesh Gupta** | Automation Champion; a referência em Flow |
| **Jitendra Zaa** | integração, arquitetura e análise de custos |
| **Christophe Coenraets** | evangelismo técnico; muitos dos apps de exemplo |
| **René Winkelmeyer** | plataforma, APIs, segurança |

---

## 7. Fontes usadas na produção deste material

Todas consultadas em **11/08/2026**.

**Arquitetura e plataforma**
- Salesforce — *WHITEPAPER: The Force.com Multitenant Architecture* — https://www.developerforce.com/media/ForcedotcomBookLibrary/Force.com_Multitenancy_WP_101508.pdf
- Salesforce Developers — *Multi Tenant Architecture* (wiki) — https://developer.salesforce.com/ja/wiki/multi_tenant_architecture
- O'Reilly — *The Force.com Multitenant Architecture* (livro, 2008) — https://www.oreilly.com/library/view/the-force-com-multitenant/30000LTI00089/

**Release Summer '26 / API 67.0**
- Salesforce Developers Blog — *The Salesforce Developer's Guide to the Summer '26 Release* — https://developer.salesforce.com/blogs/2026/06/the-salesforce-developers-guide-to-the-summer-26-release
- Salesforce Blog — *Summer '26 Release Architect Highlights: Sharing, Security, and Agentic Integration* — https://www.salesforce.com/blog/summer-26-release-architect-highlights/
- conemis — *Salesforce Summer '26 Release API Updates: Version 67.0* — https://www.conemis.com/news/salesforce-summer-26-release-api-updates-version-67-0
- Salesforce Help — *Release Note Changes* — https://help.salesforce.com/s/articleView?id=release-notes.rn_change_log.htm

**Instalação e ferramentas**
- npm — `@salesforce/cli` — https://www.npmjs.com/package/@salesforce/cli
- Salesforce — *Salesforce CLI Setup Guide*, v67.0 Summer '26, atualizado em 24/07/2026 — https://resources.docs.salesforce.com/latest/latest/en-us/sfdc/pdf/sfdx_setup.pdf
- Salesforce Developers — *Supported Scratch Org Editions and Allocations* — https://developer.salesforce.com/docs/atlas.en-us.sfdx_dev.meta/sfdx_dev/sfdx_dev_scratch_orgs_editions_and_allocations.htm
- Salesforce Ben — *Get Started With Salesforce Scratch Orgs (Updated for 2026)* — https://www.salesforceben.com/salesforce-scratch-orgs/

**Mercado, preços e IA**
- Salesforce Newsroom — *Salesforce Named #1 CRM Provider by IDC Market Share* — https://www.salesforce.com/news/stories/idc-crm-market-share-ranking-2025/
- Salesforce (EU) — preços de Sales Cloud — https://www.salesforce.com/eu/sales/pricing/
- MarketBetter — *Salesforce Sales Cloud Pricing 2026* — https://marketbetter.ai/blog/salesforce-sales-cloud-pricing-breakdown-2026/
- SalesforceNegotiations — *Salesforce Pricing 2026: The Complete Enterprise Guide* — https://salesforcenegotiations.com/blog/salesforce-pricing-2026-complete-guide/
- Enterprise Dreamin' — *Agentforce Pricing Explained (2026)* — https://enterprisedreamin.org/articles/agentforce-pricing-explained-2026/
- getclientell — *Agentforce Pricing Explained: Flex Credits, Real Costs & Hidden Fees (2026)* — https://www.getclientell.com/guides/agentforce-pricing-explained
- Jitendra Zaa — *Salesforce Agentforce Credits & Cost Model: Complete Guide 2026* — https://www.jitendrazaa.com/blog/salesforce/salesforce-agentforce-credits-cost-model-complete-guide-2026/

**Certificações e cursos**
- Salesforce Ben — *Complete List of Salesforce Certifications 2026* — https://www.salesforceben.com/salesforce-certifications/
- Apex Hours — *Complete Salesforce Certifications List in 2026* — https://www.apexhours.com/salesforce-certifications/
- passitexams — *Salesforce Certification Cost 2026* — https://passitexams.com/articles/salesforce-certification-cost/
- s2-labs — *How Much Does Salesforce Certification Cost in 2026?* — https://s2-labs.com/blog/salesforce-certification-cost/
- Salesforce France — *Tutoriel Salesforce : formation en ligne gratuite* — https://www.salesforce.com/fr/small-business/salesforce-tutorial/
- YouTube — *Formation Salesforce Administrateur complète et gratuite (ADX201)* — https://www.youtube.com/playlist?list=PLDYZIiNbvhXz6WWB9bDJTrMjKqnk9FTQp

**História e contexto**
- Wikipedia — *Salesforce* — https://en.wikipedia.org/wiki/Salesforce

**Câmbio**
- Investing.com — USD/BRL em 11/08/2026 — https://br.investing.com/currencies/usd-brl

**Teoria (papers e livros)**
- Selinger, P. G. et al. *Access Path Selection in a Relational Database Management System.* SIGMOD, 1979.
- Fischer, M., Lynch, N., Paterson, M. *Impossibility of Distributed Consensus with One Faulty Process.* JACM, 1985.
- Gilbert, S., Lynch, N. *Brewer's Conjecture and the Feasibility of Consistent, Available, Partition-Tolerant Web Services.* SIGACT News, 2002.
- Ghodsi, A. et al. *Dominant Resource Fairness.* NSDI, 2011.
- Turing, A. *On Computable Numbers…* 1936.
- Kleppmann, M. *Designing Data-Intensive Applications.* O'Reilly, 2017.

---

## 8. Como verificar uma informação sobre Salesforce

Hierarquia de confiança, do mais para o menos confiável:

1. **Documentação oficial de desenvolvedor** (`developer.salesforce.com/docs`) — a verdade
   sobre comportamento técnico.
2. **Release Notes** — a verdade sobre o que mudou e quando.
3. **`sf <comando> --help`** — a verdade sobre a CLI. Frequentemente mais atual que a doc online.
4. **A própria org** — o teste definitivo. Nada supera reproduzir.
5. **Salesforce Stack Exchange** com resposta aceita e votada, e **verifique a data**.
6. **Blogs de referência** (§5).
7. **Blogs aleatórios e conteúdo gerado por IA** — trate como hipótese a verificar.

> **A regra que eu aplico:** se a informação envolve **número** (limite, preço, versão) ou
> **comportamento** (o que acontece quando…), vá até a fonte 1, 2 ou 4. Não confie em
> memória — nem na minha, nem na sua. A plataforma muda três vezes por ano.

---

## Autoteste

1. Quais cinco páginas da documentação oficial você manteria abertas o tempo todo?
2. Qual ferramenta de terceiros economiza mais tempo por dia, e o que ela faz?
3. Onde está o melhor catálogo prático de receitas de LWC?
4. Qual é a hierarquia de confiança para verificar uma informação técnica?
5. Por que `sf <comando> --help` é frequentemente mais confiável que a documentação online?
6. Qual repositório da Salesforce é MIT e utilizável fora da plataforma?
