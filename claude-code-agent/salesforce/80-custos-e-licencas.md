# 80 · Custos e licenças

`Nível: todos` · **`Preços consultados em 11/08/2026`**
`Câmbio usado: US$ 1 ≈ R$ 5,11 (11/08/2026)`

> ⚠️ **Preço sem data é desinformação.** Todos os valores abaixo têm a data de consulta.
> Salesforce reajusta com frequência — houve um aumento de ~6% em Enterprise e Unlimited
> em **agosto de 2025**. Confirme na fonte antes de usar em orçamento.
>
> Os valores são de **tabela pública dos EUA**. Preço praticado no Brasil varia com câmbio,
> impostos, tamanho do contrato e negociação — descontos de 20% a 40% em contratos
> plurianuais grandes são comuns no mercado corporativo.

---

## 1. Sales Cloud — preços de tabela (11/08/2026)

| Edição | US$/usuário/mês | ≈ R$/usuário/mês | Cobrança |
|---|---|---|---|
| **Starter Suite** | 25 | ~128 | anual ou mensal |
| **Pro Suite** | 100 | ~511 | anual |
| **Enterprise** | **175** | ~894 | anual |
| **Unlimited** | 350 | ~1.789 | anual |
| **Agentforce 1 Sales** | 550 | ~2.811 | anual |

**Cenários concretos, só de licença Sales Cloud Enterprise:**

| Usuários | US$/ano | ≈ R$/ano |
|---|---|---|
| 10 | 21.000 | ~107 mil |
| 50 | 105.000 | ~537 mil |
| 200 | 420.000 | ~2,15 milhões |
| 1.000 | 2.100.000 | ~10,7 milhões |

**Service Cloud** tem estrutura de preço equivalente por edição. Precisar das duas
significa, na prática, licenças distintas ou um pacote combinado.

---

## 2. A linha divisória: Enterprise

| Recurso | Starter | Pro | **Enterprise** | Unlimited |
|---|---|---|---|---|
| Apex e triggers | ❌ | limitado | ✅ | ✅ |
| API completa | limitada | ✅ | ✅ | ✅ |
| Record Types | ❌ | limitado | ✅ | ✅ |
| Aprovações | ❌ | limitado | ✅ | ✅ |
| Sandboxes | ❌ | 1 Developer | Developer + Partial Copy | + Full Copy |
| Suporte 24/7 | ❌ | ❌ | pago (Premier) | incluído |

**Se o projeto envolve desenvolvimento, Enterprise é o piso.** Abaixo dela você não tem Apex
completo, nem sandbox utilizável, nem API sem restrição. É por isso que ela é a edição mais
vendida — e é o número que você deve usar em qualquer estimativa preliminar.

---

## 3. Agentforce e IA — o modelo por consumo

| Modelo | Preço (11/08/2026) |
|---|---|
| Por conversa | **US$ 2,00** por conversa |
| **Flex Credits** | **US$ 500 por 100.000 créditos** |
| — ação padrão | 20 créditos ≈ **US$ 0,10** |
| — ação de voz | 30 créditos ≈ **US$ 0,15** |
| Por usuário | a partir de **US$ 125/usuário/mês** |
| Incluído no topo | Agentforce 1 Sales, US$ 550/usuário/mês |

**Camada gratuita — Salesforce Foundations:** disponível a clientes **Enterprise ou
superior**, inclui **200.000 Flex Credits**, **250.000 créditos de Data Cloud**,
Agent Builder e Prompt Builder, sem custo adicional.

**Onde a camada gratuita acaba, em números:** 200.000 créditos ÷ 20 créditos por ação =
**10.000 ações**. Um agente de atendimento que executa 5 ações por conversa esgota isso em
**2.000 conversas**. Para uma central que atende 2.000 chamados por **dia**, a gratuidade
dura um dia.

> **O risco financeiro estrutural, e é o ponto mais importante deste arquivo:**
> **o custo escala com uso, não com assentos.** Se o agente for um sucesso e atender mais,
> a conta sobe. Empresas acostumadas a licença por usuário — um custo fixo e previsível —
> não têm o instinto de modelar isso, e a surpresa chega no segundo ano.
>
> Antes de contratar: estime volume mensal de conversas × ações por conversa × custo por
> ação, e projete para o cenário de **sucesso** (adoção alta), não para o piloto.

---

## 4. Data Cloud / Data 360

| Item | Valor aproximado (11/08/2026) |
|---|---|
| SKU inicial (Starter) | **~US$ 60.000/ano** (~R$ 307 mil) |
| Crescimento típico | frequentemente para seis dígitos em dólar |
| Custo total de uma implantação Agentforce + Data Cloud (mid-market, 1º ano) | estimativas de mercado citam **US$ 150 mil a US$ 600 mil** |

O consumo é medido em **créditos** de ingestão, processamento, ativação e consulta. É
difícil de estimar antes de implantar — e essa dificuldade é, ela mesma, um custo.

---

## 5. Add-ons e o que não está no preço da licença

| Add-on | Ordem de grandeza |
|---|---|
| **Salesforce Shield** (criptografia, monitoramento, audit trail) | percentual significativo sobre a licença |
| **Sandbox Full Copy adicional** | percentual do valor do contrato |
| **Armazenamento de dados extra** | cobrado por GB/mês — caro |
| **Chamadas de API extras** | pacote adicional |
| **Suporte Premier / Signature** | percentual do contrato (Premier tipicamente ~20–30%) |
| **CPQ / Revenue Cloud** | licença por usuário separada |
| **Marketing Cloud** | licença completamente separada, por contatos/e-mails |
| **MuleSoft** | licença por núcleo/conexão; alta |
| **Tableau** | licença por criador/explorador/visualizador |
| **Einstein / Agentforce** | por consumo, ver §3 |
| **Licenças de plataforma** (usuário que não usa CRM) | mais baratas que Sales/Service |
| **Experience Cloud** (portal) | por login ou por membro |

**Regra prática que uso para estimativa preliminar:** o custo total do primeiro ano fica,
tipicamente, entre **2× e 4×** o valor da licença — somando implantação, add-ons,
integrações e treinamento. Isso é uma heurística de campo, não um número oficial.

---

## 6. Os custos ocultos, um a um

### 6.1 Implantação

Consultoria custa, no Brasil, tipicamente entre **R$ 150 e R$ 500 por hora** conforme
senioridade e porte da consultoria (faixa de mercado observada; confirme com propostas).
Um projeto de porte médio consome 500 a 2.000 horas.

**Para 50 usuários:** implantação entre R$ 150 mil e R$ 600 mil — frequentemente **mais que
a licença do primeiro ano**.

### 6.2 Time interno

| Papel | Quando é necessário | Faixa salarial mensal no Brasil (estimativa de mercado, 2026) |
|---|---|---|
| Administrador | a partir de ~30 usuários | R$ 6 mil – R$ 14 mil |
| Desenvolvedor | quando há Apex/LWC | R$ 10 mil – R$ 22 mil |
| Arquiteto | orgs grandes ou multi-país | R$ 20 mil – R$ 40 mil |

> Essas faixas são estimativas de mercado e variam muito com região, modelo de contratação
> (CLT/PJ) e se o profissional atende cliente internacional — o que puxa os valores para
> cima de forma significativa. Trate como ordem de grandeza.

### 6.3 Treinamento

Usuário que não sabe usar não usa, e CRM sem adoção não gera retorno nenhum. Orce
treinamento formal e, principalmente, **acompanhamento nos primeiros 90 dias**.

### 6.4 Custo de saída — o mais subestimado de todos

Migrar para fora do Salesforce depois de 5 anos envolve:

- extrair dados **com relacionamentos e histórico** preservados;
- traduzir Apex, Flows, validações e layouts para outra plataforma (não há ferramenta que
  faça isso de forma confiável);
- refazer todas as integrações;
- retreinar todos os usuários;
- rodar os dois sistemas em paralelo durante a transição.

**Isso é normalmente um projeto de 1 a 3 anos e custo comparável ao da implantação
original — ou maior.** É o principal ativo estratégico da Salesforce e o principal risco
do cliente. Entrar sabendo disso é diferente de descobrir depois.

### 6.5 Armazenamento

Data storage é caro por GB. Anexos, e-mails registrados e histórico crescem sozinhos.
Planeje arquivamento **antes** de precisar dele — ver
[12-modelo-de-dados.md](12-modelo-de-dados.md) §8.

### 6.6 Backup

O plano padrão **não garante** restauração ponto a ponto. Existe um serviço pago
(Salesforce Backup & Restore) e ferramentas de terceiros (Own/OwnBackup, Odaseva, Gearset).
Um export semanal via Bulk API é o mínimo defensável, e é gratuito — mas é uma cópia, não
um plano de recuperação.

---

## 7. Licenças de software: o que é aberto e o que não é

| Componente | Licença | O que você pode fazer |
|---|---|---|
| **Plataforma Salesforce** | proprietária, SaaS | usar conforme o contrato. Sem código-fonte, sem auto-hospedagem |
| **Seu código Apex/LWC** | **seu** | você é o dono; mas ele só roda no Salesforce |
| **Salesforce CLI** | **BSD-3-Clause** (código aberto) | usar, modificar, redistribuir |
| **LWC (framework)** | **MIT** (open source) — https://github.com/salesforce/lwc | usar **fora** do Salesforce, em qualquer projeto web |
| **Lightning Design System (SLDS)** | **BSD-3-Clause** | usar fora da plataforma |
| **Salesforce Code Analyzer** | código aberto | usar e estender |
| **Apps do AppExchange** | varia | ler a licença de cada um |

**O detalhe que quase ninguém sabe:** o **LWC é open source sob MIT** e roda fora do
Salesforce. Você pode usar o framework num projeto web comum. Isso significa que o
conhecimento de LWC é **transferível** — diferente do de Apex.

**A pergunta que importa sobre propriedade:** o código que você escreve é seu, mas ele é
**inútil fora da plataforma**, porque depende do modelo de dados, das APIs e do runtime
da Salesforce. Propriedade legal sem portabilidade técnica não protege contra lock-in.

---

## 8. Alternativas e o que se perde ao trocar

| Alternativa | Custo relativo | O que você perde | O que você ganha |
|---|---|---|---|
| **Microsoft Dynamics 365** | similar ou menor | ecossistema e mão de obra maiores | integração com Microsoft 365 |
| **HubSpot** | menor no início | profundidade de customização e escala | simplicidade, tempo até o valor |
| **Zoho CRM** | **muito menor** | ecossistema, maturidade corporativa | custo |
| **Pipedrive** | muito menor | tudo além de vendas | foco e simplicidade |
| **Odoo** (open source) | baixo (self-host) | suporte, escala corporativa | controle total, sem lock-in |
| **SuiteCRM** (open source, AGPL) | baixo | ecossistema e modernidade | código aberto |
| **ERPNext / Frappe** (open source) | baixo | foco em CRM | ERP+CRM integrados |
| **Construir do zero** | alto e crescente | tudo pronto | controle e portabilidade totais |

> **Minha recomendação honesta, por porte:**
> - **até ~10 usuários:** Salesforce quase nunca compensa. HubSpot, Pipedrive ou Zoho.
> - **10 a 50:** depende da complexidade do processo. Se for simples, alternativas ganham.
> - **50+ com processo complexo e muitas integrações:** Salesforce começa a se justificar.
> - **empresa regulada, multinacional, com auditoria pesada:** Salesforce ou Dynamics.
>
> O erro mais caro que vejo é empresa pequena comprando Salesforce porque "é o líder de
> mercado" e depois não tendo orçamento para implantar direito. Uma org mal implantada é
> pior que planilha, porque custa caro **e** ninguém usa.

---

## 9. Como reduzir custo, de verdade

1. **Negocie o contrato plurianual.** Descontos relevantes são padrão em compromissos de
   3 anos. Peça a proposta de 1 e de 3 anos e compare.
2. **Compre no fim do trimestre fiscal.** O ano fiscal da Salesforce termina em **janeiro**;
   o poder de negociação é maior perto do fechamento de trimestre.
3. **Audite licenças ociosas todo ano.** Empresas costumam pagar por usuários desligados.
   `Setup → Company Information` mostra as licenças usadas vs. contratadas.
4. **Use a licença certa por perfil.** Quem não usa CRM pode ter licença de plataforma, mais
   barata.
5. **Não compre add-on antes de precisar.** Shield, Premier, sandboxes extras — compre
   quando a dor aparecer.
6. **Arquive dados.** Storage extra é caro; Big Object e arquivamento externo são baratos.
7. **Comece pelo Trailhead e por uma DE.** Todo o aprendizado deste curso custa zero.
8. **Prefira Reports e Dashboards nativos** antes de comprar BI.
9. **Modele o Agentforce pelo cenário de sucesso**, não pelo piloto.

---

## 10. Aprender custa zero — o que é realmente gratuito

| Recurso | Custo | Limitação |
|---|---|---|
| **Trailhead** | grátis, para sempre | nenhuma relevante |
| **Developer Edition** | grátis, permanente | ~5 MB de dados, 15.000 chamadas de API/dia |
| **Trailhead Playground** | grátis | expira; não serve para projeto real |
| **Trial org** (30 dias) | grátis, sem cartão | 30 dias, edição Enterprise |
| **Documentação oficial** | grátis | — |
| **Trailblazer Community** | grátis | — |
| **Salesforce CLI, LWC, SLDS** | open source | — |

**Quem paga essa conta?** A Salesforce, deliberadamente. Ela investe em formar mão de obra
porque a escassez de profissionais é o gargalo de venda de licenças. Cada pessoa que
aprende de graça aumenta a probabilidade de uma empresa escolher Salesforce. Não é
filantropia — é a estratégia comercial mais bem executada do setor. Ver
[11-historia.md](11-historia.md) §4.

---

## Autoteste

1. Qual é o preço de tabela da Sales Cloud Enterprise em 11/08/2026, e qual a data da consulta?
2. Por que a Enterprise é o piso para projetos com desenvolvimento?
3. Quantas ações cabem nos 200.000 Flex Credits gratuitos? Quantas conversas isso representa?
4. Por que o modelo de preço do Agentforce muda a natureza do risco financeiro?
5. Qual é a heurística de estimativa do custo total do primeiro ano?
6. Por que o custo de saída é o custo mais subestimado, e o que ele envolve?
7. Qual componente do ecossistema é MIT e roda fora do Salesforce? Por que isso importa?
8. Para uma empresa de 8 usuários, você recomendaria Salesforce? Justifique.
9. Quem paga a conta do Trailhead e da Developer Edition, e por quê?

---

### Fontes consultadas (11/08/2026)

- Salesforce (EU) — página oficial de preços de Sales Cloud — https://www.salesforce.com/eu/sales/pricing/
- MarketBetter — *Salesforce Sales Cloud Pricing 2026: From $25 to $550/User* — https://marketbetter.ai/blog/salesforce-sales-cloud-pricing-breakdown-2026/
- SalesforceNegotiations — *Salesforce Pricing 2026: The Complete Enterprise Guide* — https://salesforcenegotiations.com/blog/salesforce-pricing-2026-complete-guide/
- Enterprise Dreamin' — *Agentforce Pricing Explained (2026)* — https://enterprisedreamin.org/articles/agentforce-pricing-explained-2026/
- getclientell — *Agentforce Pricing Explained: Flex Credits, Real Costs & Hidden Fees (2026)* — https://www.getclientell.com/guides/agentforce-pricing-explained
- Jitendra Zaa — *Salesforce Agentforce Credits & Cost Model: Complete Guide 2026* — https://www.jitendrazaa.com/blog/salesforce/salesforce-agentforce-credits-cost-model-complete-guide-2026/
- GitHub — salesforce/lwc (licença MIT) — https://github.com/salesforce/lwc
- Investing.com — cotação USD/BRL em 11/08/2026 — https://br.investing.com/currencies/usd-brl
