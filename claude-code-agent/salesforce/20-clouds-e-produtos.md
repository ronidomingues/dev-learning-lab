# 20 · Clouds e produtos — o mapa do ecossistema

`Nível: intermediário` · `Atualizado: 11/08/2026`

"Salesforce" hoje é o nome de mais de trinta produtos. Este arquivo é o mapa, com a
informação que mais importa e que os materiais oficiais nunca dão: **o que nasceu dentro
da plataforma e o que foi comprado** — porque isso determina o quão integrado o produto
realmente é.

---

## 1. O núcleo — construído sobre a plataforma

| Produto | O que faz | Nativo? |
|---|---|---|
| **Sales Cloud** | funil, previsão, cotação, gestão de território | ✅ é o produto original |
| **Service Cloud** | chamados, filas, base de conhecimento, canais, telefonia | ✅ nativo |
| **Salesforce Platform** | construir apps próprios (o antigo Force.com) | ✅ é a plataforma |
| **Experience Cloud** | portais para clientes, parceiros e comunidades | ✅ nativo |
| **Field Service** | agendamento e despacho de técnicos em campo | ✅ nativo |
| **CPQ / Revenue Cloud** | configuração, precificação e cotação complexas | 🟡 base adquirida (SteelBrick, 2015) |
| **Einstein / Agentforce** | IA preditiva e agentes autônomos | ✅ nativo (com modelos de terceiros por trás) |

**O que "nativo" significa na prática:** mesmo modelo de dados, mesma segurança, mesmo Setup,
mesmas APIs, mesmo ciclo de release, mesmos governor limits. Você usa Apex, Flow e LWC neles.

---

## 2. Os adquiridos — mesma marca, outra natureza

| Produto | Origem | Ano | Nível de integração em 2026 |
|---|---|---|---|
| **Marketing Cloud** (Engagement) | ExactTarget | 2013 | 🔴 baixa — modelo de dados, linguagem (AMPscript/SSJS) e interface próprios |
| **Marketing Cloud Account Engagement** (ex-Pardot) | Pardot | 2012 | 🟡 média — mais próximo do core, mas ainda separado |
| **Commerce Cloud** | Demandware | 2016 | 🟡 média — B2C tem stack própria; B2B é mais integrado |
| **MuleSoft** | MuleSoft | 2018 | 🟡 produto separado, integrado por conectores |
| **Tableau** | Tableau | 2019 | 🟡 produto separado; Tableau Next aproxima |
| **Slack** | Slack | 2021 | 🟡 integração crescente, produto independente |
| **Heroku** | Heroku | 2010 | 🔴 plataforma completamente separada (PaaS) |
| **Industries / Vlocity** | Vlocity | 2020 | ✅ roda sobre a plataforma, como pacote gerenciado |

> **A pergunta que vale ouro numa negociação:** *"esse produto compartilha o modelo de dados
> e o Setup do core, ou é uma aplicação separada com integração por API?"*
>
> A resposta muda: o custo do projeto, o perfil de quem você precisa contratar, a
> complexidade da integração e a possibilidade de reusar o que você já construiu.
>
> **Marketing Cloud é o exemplo canônico.** Muita empresa compra achando que "é Salesforce"
> e descobre que precisa de um profissional com especialização própria, que Apex não serve
> ali, e que sincronizar dados com o CRM é um projeto por si só. Isso melhorou com o tempo,
> mas ainda é real em 2026.

---

## 3. Data Cloud / Data 360

O produto mais estratégico da empresa hoje.

**O que faz:**
1. **Ingere** dados de qualquer fonte — CRM, ERP, data warehouse, web, app, streaming.
2. **Harmoniza** num modelo canônico (*Data Model Objects*).
3. **Resolve identidade** — descobre que o "José Silva" da tabela A é o mesmo do sistema B.
4. **Calcula** métricas, segmentos e insights sobre o perfil unificado.
5. **Ativa** — devolve os dados ao CRM, ao marketing, aos agentes de IA e a sistemas externos.

**Zero-copy:** a Data 360 pode consultar dados **onde eles estão** (Snowflake, BigQuery,
Databricks, Redshift) sem copiá-los, via compartilhamento de dados. Isso reduz custo de
armazenamento e evita duplicar a verdade.

**Por que a Salesforce apostou tanto nisso:** agentes de IA úteis precisam de contexto. O
CRM sozinho vê uma fatia pequena do cliente. Quem controlar o **perfil unificado** controla
a camada onde a IA opera. É uma disputa direta com Adobe, Microsoft, Google e as próprias
plataformas de dados.

**O custo:** o SKU inicial de Data 360 é da ordem de **US$ 60.000/ano**, e cresce com
consumo (créditos de ingestão, processamento e ativação). Ver
[80-custos-e-licencas.md](80-custos-e-licencas.md).

---

## 4. Agentforce

Lançado em setembro de 2024, é a aposta atual da empresa.

**O que é:** um framework para construir **agentes autônomos** que executam tarefas dentro
do Salesforce, com quatro peças:

| Peça | Papel |
|---|---|
| **Agent Builder** | define os *tópicos* (o que o agente sabe fazer) e as *instruções* |
| **Ações** | o que o agente pode executar: Flow, Apex, Prompt Template, API, MuleSoft |
| **Grounding** | os dados que ele consulta — org, Data 360, base de conhecimento |
| **Einstein Trust Layer** | mascaramento de PII, retenção zero pelo provedor de modelo, auditoria, detecção de toxicidade |

**O modelo mental honesto:** um agente é um LLM com (a) um conjunto de ferramentas
declaradas, (b) instruções em linguagem natural e (c) acesso mediado aos seus dados. A
diferença em relação a montar isso você mesmo é que a Salesforce entrega o encanamento —
autenticação, permissões, auditoria, conectores e a camada de confiança — já pronto e
integrado à segurança da org.

**O modelo de preço mudou várias vezes**, o que por si só diz algo sobre a maturidade.
Em 11/08/2026 convivem três formas:

| Modelo | Preço aproximado |
|---|---|
| Por conversa | **US$ 2,00** por conversa |
| **Flex Credits** | **US$ 500 por 100.000 créditos**; ação padrão = 20 créditos (US$ 0,10); ação de voz = 30 créditos (US$ 0,15) |
| Por usuário | a partir de **US$ 125/usuário/mês** |
| Incluído no topo | **Agentforce 1 Sales** a US$ 550/usuário/mês |

**Camada gratuita:** o **Salesforce Foundations** dá, a clientes Enterprise ou superior,
**200.000 Flex Credits**, **250.000 créditos de Data Cloud**, Agent Builder e Prompt Builder
sem custo. É o suficiente para provar valor — e é claramente desenhado para isso.

> **Minha avaliação profissional, separada dos fatos acima:** a tecnologia funciona melhor
> do que o ceticismo natural sugere, **em casos bem delimitados** — triagem de chamados,
> respostas a partir de base de conhecimento, preenchimento de dados, qualificação inicial.
> O que ainda não vi funcionar de forma confiável são agentes tomando decisões de negócio
> irreversíveis sem revisão humana. Trate como um estagiário competente e rápido que precisa
> de supervisão, não como um funcionário autônomo. E note que o custo escala com **uso**, não
> com assentos — o que muda completamente a modelagem financeira do projeto.

---

## 5. Ferramentas de desenvolvimento e análise

| Produto | Para quê |
|---|---|
| **Salesforce CLI (`sf`)** | tudo, pelo terminal |
| **Code Builder** | VS Code no navegador |
| **DevOps Center** | pipeline de deploy orientado a admins, gratuito |
| **Salesforce Code Analyzer** | análise estática (PMD, ESLint, RetireJS, fluxo de segurança) |
| **Heroku** | rodar código que não cabe em Apex (Node, Python, Go, Java, Ruby) |
| **Tableau / Tableau Next / CRM Analytics** | BI e visualização |
| **Reports & Dashboards** | relatórios nativos, gratuitos, e onde 90% das necessidades morrem |

**Sobre Heroku:** é a válvula de escape oficial para computação pesada, bibliotecas
externas e processos longos. O padrão é: dados e processo de negócio no Salesforce,
computação pesada no Heroku, integrados por API ou **Heroku Connect** (sincronização
bidirecional com Postgres).

---

## 6. Como escolher: as perguntas certas

### 6.1 Sales Cloud ou Service Cloud?

| Você precisa de | Cloud |
|---|---|
| Funil, previsão, cotação, território | **Sales** |
| Chamados, filas, SLA, base de conhecimento, telefonia, chat | **Service** |
| Ambos | ambas as licenças, ou uma edição que inclua as duas |

Os objetos são compartilhados (`Account`, `Contact`). A diferença está nos objetos
específicos (`Opportunity` vs. `Case`), nas funcionalidades e no **preço da licença**.

### 6.2 Preciso mesmo de Data 360?

| Sinal | Precisa? |
|---|---|
| Os dados de cliente estão em 1 ou 2 sistemas | não — integre direto |
| Existem 5+ fontes e ninguém sabe qual é a verdade | provavelmente sim |
| Quer usar Agentforce com contexto além do CRM | sim, na prática é pré-requisito |
| Orçamento anual de seis dígitos disponível | é o que o produto custa |

### 6.3 Construir na plataforma ou fora?

| Construa **na** plataforma | Construa **fora** |
|---|---|
| processo de negócio com muitos usuários internos | volume altíssimo, baixa latência |
| forte dependência dos dados do CRM | computação pesada, ML, imagem |
| regras que mudam com frequência | produto voltado ao consumidor final, em escala |
| poucos usuários licenciados, alto valor por usuário | milhões de usuários anônimos |
| requisito de auditoria e segurança corporativa | requisito de portabilidade |

---

## 7. Edições — o que muda

| Recurso | Starter | Pro | **Enterprise** | Unlimited |
|---|---|---|---|---|
| Preço/usuário/mês (Sales Cloud, 11/08/2026) | US$ 25 | US$ 100 | **US$ 175** | US$ 350 |
| Apex e triggers | ❌ | limitado | ✅ | ✅ |
| API completa | limitada | ✅ | ✅ | ✅ |
| Objetos customizados | poucos | mais | 2.000 | mais |
| Record Types | ❌ | limitado | ✅ | ✅ |
| Sandboxes | ❌ | 1 Developer | Developer + Partial | + Full Copy |
| Aprovações | ❌ | limitado | ✅ | ✅ |
| Suporte 24/7 | ❌ | ❌ | pago | incluído |

**A linha divisória prática é a Enterprise.** Abaixo dela você não tem Apex completo, nem
sandbox utilizável, nem API sem restrição. Se o projeto envolve desenvolvimento, Enterprise
é o piso — e é por isso que ela é a edição mais vendida.

---

## 8. AppExchange

O marketplace, com milhares de aplicativos e componentes.

| Categoria | Exemplos de uso |
|---|---|
| Ferramentas de dev | Copado, Gearset, ApexMocks |
| Qualidade de dados | deduplicação, enriquecimento, validação de CNPJ/CPF |
| Documentos | geração de PDF, assinatura eletrônica |
| Verticais | soluções para saúde, educação, finanças, imobiliário |
| Localização Brasil | nota fiscal, integração bancária, boleto, cálculo fiscal |

**Como avaliar um app antes de instalar:**

1. **É gerenciado?** Se sim, você não vê nem altera o código.
2. **Consome limites da sua org?** Triggers e jobs do pacote gastam **os seus** limites.
3. **Há certificação de segurança?** Todo app passa por revisão da Salesforce, mas o rigor
   varia com o tipo de acesso solicitado.
4. **Qual o modelo de preço?** Por usuário, por org, por volume?
5. **Como se desinstala?** Alguns deixam dados e metadados órfãos.
6. **Quantos objetos e campos ele cria?** Eles contam contra os **seus** limites de org.
7. **Quem mantém?** Uma empresa de dois desenvolvedores é um risco de continuidade real.

> **Conselho ganho na prática:** instale sempre primeiro numa **sandbox**, e cheque
> `Setup → Apex Jobs` e o consumo de limites por uma semana antes de levar a produção.
> Um pacote mal escrito consumindo CPU nas suas transações é um problema que você não
> consegue corrigir — só remover.

---

## 9. Autoteste

1. Qual a diferença prática entre um produto nativo e um adquirido? Dê um exemplo de cada.
2. Por que Marketing Cloud é o exemplo canônico de produto pouco integrado?
3. O que a Data 360 faz, em cinco passos, e por que ela é estratégica para a IA?
4. Quais são as quatro peças do Agentforce e o que cada uma faz?
5. Quais são os três modelos de preço do Agentforce em 11/08/2026, e o que a camada gratuita inclui?
6. Por que a Enterprise é a linha divisória prática entre as edições?
7. Cite quatro perguntas que você faria antes de instalar um app do AppExchange.
8. Quando construir fora da plataforma? Dê três critérios.

---

### Fontes consultadas (11/08/2026)

- Salesforce (EU) — preços de Sales Cloud — https://www.salesforce.com/eu/sales/pricing/
- Enterprise Dreamin' — *Agentforce Pricing Explained (2026)* — https://enterprisedreamin.org/articles/agentforce-pricing-explained-2026/
- Jitendra Zaa — *Salesforce Agentforce Credits & Cost Model: Complete Guide 2026* — https://www.jitendrazaa.com/blog/salesforce/salesforce-agentforce-credits-cost-model-complete-guide-2026/
- Wikipedia — *Salesforce* (aquisições e valores) — https://en.wikipedia.org/wiki/Salesforce
