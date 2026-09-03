# 65 · Estado da arte — agosto de 2026

`Nível: pesquisa` · **`Instantâneo de 11/08/2026`** · `Release: Summer '26 · API 67.0`

> ⚠️ **Este é o arquivo que envelhece mais rápido de todo o material.** Salesforce lança
> três releases por ano e muda preços com frequência. Se você está lendo isto em 2027,
> trate como registro histórico e confira as fontes ao final.

---

## 1. O que está no ar agora

| Item | Estado em 11/08/2026 |
|---|---|
| Release corrente | **Summer '26** |
| Versão de API | **67.0** |
| Próximo release | Winter '27 (previsto para outubro/2026) |
| Salesforce CLI | 2.146.x |
| Receita FY2026 | US$ 41,5 bilhões (+10% a/a) |
| Participação no mercado CRM (IDC, dado de 2025) | 20,0% — 1º lugar pelo 13º ano |

---

## 2. A mudança técnica mais importante: segurança do Apex em user mode

**O que mudou na API 67.0:**

1. **SOQL, SOSL, DML e métodos `Database.*` rodam em user mode por padrão.**
   Antes rodavam em system mode, ignorando FLS e permissões de objeto do usuário.
2. **Classes sem declaração de sharing são `with sharing` por padrão.**
   Antes eram `without sharing` na maioria dos contextos.
3. **`WITH SECURITY_ENFORCED` foi removida.** Classes em v67.0+ que a usem **não compilam**.
   O substituto é `WITH USER_MODE`.

**Por que isso é o marco do release:** inverte um padrão de 18 anos. O comportamento
anterior — inseguro por omissão — produziu, ao longo de quase duas décadas, uma quantidade
enorme de Apex que expõe dados que o usuário não deveria ver, quase sempre sem que ninguém
tenha tomado essa decisão conscientemente.

**Por que só agora, e por que amarrado à versão de API:** compatibilidade retroativa é
sagrada nesta plataforma. Mudar o padrão para todo o código existente quebraria uma
quantidade imensa de aplicações — inclusive pacotes gerenciados de terceiros — da noite
para o dia. Amarrar a mudança à versão de API do código é a única forma de fazer a
transição sem um evento de extinção.

**O que fazer:** ver a estratégia de migração em [15-apex.md](15-apex.md) §9.2.

---

## 3. Outras mudanças relevantes do Summer '26

| Mudança | O que significa |
|---|---|
| **Named Query API** chega a GA | consultas SOQL customizadas expostas como ações escaláveis para clientes REST **e para agentes de IA** |
| **GraphQL: encadeamento em mutations** | uma mutation pode referenciar qualquer campo devolvido por uma operação anterior na mesma requisição, não só o Id |
| **Managed Content GraphQL API** | acesso a conteúdo gerenciado por GraphQL |
| `Event` e `Task` na UI API | objetos de atividade passam a ser suportados pela User Interface API |
| **Retirada anunciada das APIs 31.0–40.0** | deprecação em **Summer '27**, retirada em **Summer '28** |

> **A Named Query API merece atenção estratégica.** Ela expõe consultas nomeadas e
> parametrizadas como ações — e o texto oficial menciona explicitamente agentes de IA como
> consumidores. É um sinal claro da direção: a plataforma está se reorganizando para que
> **agentes**, não só aplicações, sejam consumidores de primeira classe das APIs.

---

## 4. Agentforce: onde a aposta está

### 4.1 O estado do produto

Agentforce saiu de lançamento (set/2024) para produto com modelo de preço estabilizado em
três formas — conversa, créditos e assento (ver [20-clouds-e-produtos.md](20-clouds-e-produtos.md) §4).

A camada **Salesforce Foundations** dá, a clientes Enterprise ou superior, **200.000 Flex
Credits** e **250.000 créditos de Data Cloud** sem custo, com Agent Builder e Prompt Builder
incluídos. É uma estratégia de adoção clássica: eliminar a barreira de experimentação.

### 4.2 O que está em disputa técnica

| Questão em aberto | Estado |
|---|---|
| **Confiabilidade de ação** | agentes acertam bem em tarefas delimitadas; ação irreversível sem revisão humana continua sendo risco não resolvido |
| **Custo previsível** | o modelo por consumo torna difícil orçar o ano; empresas estão aprendendo a estimar |
| **Grounding** | qualidade da resposta depende da qualidade dos dados — o que empurra a venda de Data 360 |
| **Avaliação** | como medir se um agente está bom? Métricas de avaliação de agentes são um problema aberto do setor, não da Salesforce |
| **Interoperabilidade** | há movimento no setor para protocolos abertos de conexão entre agentes e ferramentas (MCP e sucessores); a direção é de convergência |

### 4.3 Minha leitura, separada dos fatos

**Fatos:** o produto existe, tem clientes pagantes, e a Salesforce reorganizou preço,
roadmap e narrativa em torno dele.

**Opinião profissional:** a tecnologia entrega valor real em três classes de tarefa —
triagem e roteamento, resposta a partir de base de conhecimento, e preenchimento/enriquecimento
de dados. Nessas, ela é melhor que a alternativa humana em custo e latência.

Onde **não** vi funcionar de forma confiável: decisões de negócio irreversíveis sem revisão,
raciocínio sobre políticas complexas com muitas exceções, e qualquer coisa onde um erro
custe mais do que a economia gerada. O modelo mental útil é o de um estagiário rápido,
barato e incansável, que precisa de supervisão proporcional ao custo do erro.

**O risco financeiro que vejo subestimado:** o custo escala com **uso**, não com assentos.
Um caso de sucesso — o agente atendendo mais — aumenta a conta. Empresas acostumadas a
licença por usuário não têm o instinto de modelar isso, e a surpresa aparece no segundo ano.

---

## 5. Data 360 e a batalha pelo perfil unificado

O rebranding de Data Cloud para **Data 360** consolidou a posição do produto como camada
de dados da plataforma.

**A tese estratégica:** a IA só é útil com contexto; o contexto vem do perfil unificado do
cliente; quem controla o perfil unificado controla onde a IA opera.

**Os competidores diretos nessa camada:** Adobe Experience Platform, Microsoft
(Dynamics + Fabric), Google (Cloud + Ads), e as plataformas de dados puras
(Snowflake, Databricks) que estão subindo a pilha em direção à aplicação.

**O movimento técnico mais interessante é o *zero-copy***: em vez de copiar dados do
Snowflake/BigQuery/Databricks para dentro da Data 360, consultá-los onde estão. Isso ataca
a objeção número um do cliente ("não vou duplicar meu data warehouse") e reduz o custo de
armazenamento — ao preço de latência e de dependência da disponibilidade do outro lado.

**O que observar:** se o zero-copy virar o padrão do setor, o valor se desloca da posse do
dado para a **camada de semântica e ativação**. Isso é bom para quem tem a aplicação
(Salesforce) e ruim para quem tem só o armazenamento.

---

## 6. Hyperforce e residência de dados

A migração para nuvem pública continua. O que importa saber em 2026:

- permite escolher **região de residência** dos dados, atendendo LGPD, GDPR e regulações
  setoriais locais;
- **não muda** o modelo multi-inquilino, os governor limits nem o modelo de metadados;
- a migração de orgs existentes é feita pela Salesforce, com janela agendada.

Para o Brasil, a existência de região local é o argumento decisivo em setores regulados
(financeiro, saúde, governo). Confirme a disponibilidade e as condições diretamente com a
Salesforce — isso muda com frequência e não é algo para confiar em fonte secundária.

---

## 7. Tendências técnicas em curso

| Tendência | Direção | Confiança |
|---|---|---|
| **Segurança segura por padrão** | user mode, `with sharing` implícito, mais Release Updates de segurança | alta — já aconteceu |
| **APIs pensadas para agentes** | Named Query API, ações declarativas, ferramentas expostas a LLM | alta — é o eixo do roadmap |
| **GraphQL ganhando espaço** | encadeamento de mutations, mais objetos suportados | média-alta |
| **Zero-copy de dados** | menos ETL, mais federação | média-alta |
| **Retirada de tecnologia legada** | APIs 31–40, Workflow, Process Builder, Aura | alta — datas anunciadas |
| **Pressão de preço** | reajustes e produtos por consumo | alta |
| **Consumo substituindo assento** | Flex Credits, créditos de dados | média — coexiste com licença por usuário |

---

## 8. O que observar nos próximos 12 meses

1. **Winter '27** (outubro/2026): quais Release Updates de segurança serão impostos, e o
   que muda na API 68.0.
2. **A conta do Agentforce nos primeiros clientes de escala.** Os primeiros casos públicos
   de custo real por consumo vão calibrar as expectativas do mercado inteiro.
3. **A migração das APIs 31–40.** A deprecação em Summer '27 é o prazo real para empresas
   com integrações antigas. Levantar os consumidores leva meses.
4. **Adoção de user mode.** Quantas orgs vão efetivamente subir a versão de API do código —
   e quantos incidentes de segurança latentes isso vai revelar.
5. **Concorrência na camada de dados.** Se Snowflake/Databricks subirem a pilha até a
   aplicação, o argumento de "traga tudo para a Data 360" enfraquece.
6. **Preço.** Depois do reajuste de ~6% em agosto/2025, a questão é se a Salesforce
   consegue continuar subindo sem acelerar avaliações de migração.

---

## 9. O que **não** mudou, e provavelmente não vai mudar

Vale registrar, porque é onde vale investir tempo de aprendizado:

- o modelo **multi-inquilino** e os **governor limits**;
- **metadados como dados** — a ideia central da plataforma;
- as **cinco camadas de segurança**;
- a **ordem de execução**;
- **três releases por ano**, sem opção de recusa;
- **75% de cobertura de teste** para produção;
- **Apex** como linguagem, com a sintaxe que tem.

Quem estudar essas sete coisas terá conhecimento útil em 2036. Quem estudar a interface do
Agent Builder de 2026 terá conhecimento útil por dois anos. Distribua seu tempo de estudo
de acordo.

---

## Autoteste

1. Qual é a mudança técnica mais importante do Summer '26 e por que ela é histórica?
2. Por que a mudança de user mode foi amarrada à versão de API do código?
3. O que é a Named Query API e por que ela sinaliza a direção estratégica da plataforma?
4. Quais são os três modelos de preço do Agentforce, e qual risco financeiro eles introduzem?
5. O que é zero-copy na Data 360, que objeção ele ataca e qual é o custo?
6. Qual é o prazo de deprecação e retirada das APIs 31.0–40.0?
7. Cite três coisas que não mudaram e provavelmente não vão mudar. Por que isso deve guiar seu estudo?

---

### Fontes consultadas (11/08/2026)

- Salesforce Developers Blog — *The Salesforce Developer's Guide to the Summer '26 Release* — https://developer.salesforce.com/blogs/2026/06/the-salesforce-developers-guide-to-the-summer-26-release
- Salesforce Blog — *Summer '26 Release Architect Highlights: Sharing, Security, and Agentic Integration* — https://www.salesforce.com/blog/summer-26-release-architect-highlights/
- conemis — *Salesforce Summer '26 Release API Updates: What Developers Need to Know About API Version 67.0* — https://www.conemis.com/news/salesforce-summer-26-release-api-updates-version-67-0
- Salesforce Help — *Release Note Changes* — https://help.salesforce.com/s/articleView?id=release-notes.rn_change_log.htm
- Salesforce Newsroom — *Salesforce Named #1 CRM Provider by IDC Market Share* — https://www.salesforce.com/news/stories/idc-crm-market-share-ranking-2025/
- Enterprise Dreamin' — *Agentforce Pricing Explained (2026)* — https://enterprisedreamin.org/articles/agentforce-pricing-explained-2026/
- Jitendra Zaa — *Salesforce Agentforce Credits & Cost Model: Complete Guide 2026* — https://www.jitendrazaa.com/blog/salesforce/salesforce-agentforce-credits-cost-model-complete-guide-2026/
