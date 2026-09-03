# 80 · Custos, tarifas e "licenças"

**Nível: iniciante a intermediário** · **Preços consultados em 20/08/2026** ·
*Moeda: BRL. Preços mudam — reveja a cada semestre.*

> **Nota sobre este arquivo.** "Licença" aqui tem dois sentidos: **(a)** as
> autorizações regulatórias que definem quem pode fazer o quê no mercado brasileiro —
> e o que isso significa para a sua proteção; e **(b)** a licença do software usado
> neste curso. Ambos estão cobertos.

---

## 1. O resumo: quanto custa investir R$ 6.000 hoje

| Item | Custo | Comentário |
|---|---|---|
| Abrir conta em corretora | **R$ 0** | gratuito nas principais; não exige cartão de crédito |
| Manutenção de conta | **R$ 0** | verifique a tabela de tarifas antes |
| Comprar Tesouro Selic | **R$ 0** de custódia até R$ 10 mil | isenção da taxa da B3 para Tesouro Selic |
| Comprar CDB/LCI/LCA | **R$ 0** de taxa explícita | o custo está embutido no *spread* — seção 4 |
| Comprar ETF/ação | corretagem R$ 0 em várias + **0,030%** da B3 | R$ 1,80 por R$ 6.000 negociados |
| Imposto de renda | **15% a 22,5%** do rendimento | o maior custo, de longe |
| IOF (se resgatar antes de 30 dias) | até 96% do rendimento | evitável |

**Conclusão numérica:** o custo explícito de investir R$ 6.000 em renda fixa hoje é
**praticamente zero**. O custo real é o imposto — e, se você escolher mal, a taxa de
administração. É por isso que este curso insiste tanto nesses dois.

---

## 2. Tabela de custos, por produto

### 2.1 Tesouro Direto

| Custo | Valor | Quem cobra | Observação |
|---|---|---|---|
| Taxa de custódia | **0,20% a.a.** | B3 | **isenta** para até R$ 10.000 em **Tesouro Selic** |
| Taxa da instituição | R$ 0 na maioria | corretora | algumas repassam ou cobram além; confira a tabela |
| Corretagem | R$ 0 | — | não existe corretagem no Tesouro Direto |
| **Quando é cobrada a custódia** | só no **resgate, vencimento ou pagamento de cupom** | B3 | mudou em 31/12/2024; antes era semestral |

**Efeito prático nos seus R$ 6.000:** se tudo estiver em Tesouro Selic, a custódia é
**zero**. Se estiver em Tesouro IPCA+ ou Prefixado, são R$ 12,00 por ano.

### 2.2 Renda fixa bancária (CDB, LCI, LCA)

| Custo | Valor |
|---|---|
| Taxa explícita | **R$ 0** |
| Custódia | R$ 0 no varejo |
| Custo real | o **spread**: a diferença entre o que o banco ganha emprestando e o que te paga |

**Como o custo aparece sem aparecer:** o mesmo CDB do mesmo emissor sai com taxas
diferentes em corretoras diferentes, porque cada distribuidor retém um pedaço
(*rebate*). Você nunca vê uma linha de custo; vê uma taxa menor. **Compare o mesmo
produto em duas instituições** — a diferença é o custo que você está pagando.

### 2.3 Fundos

| Custo | Faixa típica em 2026 | Comentário |
|---|---|---|
| Taxa de administração | 0,0% a 2,5% a.a. | **acima de 0,5% em fundo DI é indefensável** com Tesouro Selic disponível |
| Taxa de performance | 20% do que exceder o referencial | comum em multimercados; verifique a "linha d'água" |
| Taxa de entrada/saída | rara no varejo | se existir, fuja |
| Come-cotas | antecipação de IR em maio e novembro | custo indireto — ver [14-tributacao.md](14-tributacao.md) |

Impacto medido: 2% ao ano custam **R$ 4.320 em 10 anos** sobre R$ 6.000 — 22% do
patrimônio final ([exemplo 6](06-exemplos.md)).

### 2.4 Renda variável (B3, tarifas vigentes em 2026)

| Custo | Valor |
|---|---|
| Taxa de negociação | **0,0050%** do financeiro |
| Taxa de liquidação | **0,0250%** do financeiro |
| **Total B3 (à vista, pessoa física)** | **0,030%** |
| Corretagem | **R$ 0** em várias instituições; até ~R$ 20 por ordem nas que cobram |
| Custódia mensal | R$ 0 na maioria |

Em R$ 6.000 negociados: **R$ 1,80** de B3. Day trade tem tabela própria e mais cara.

### 2.5 Previdência privada

| Custo | Faixa | Comentário |
|---|---|---|
| Taxa de administração | 0,3% a 2,5% a.a. | **acima de ~0,6% costuma anular o benefício fiscal** |
| Taxa de carregamento | 0% a 5% de cada aporte | **recuse**. Existem planos com zero |
| Taxa de saída | 0% a 3% | idem |

### 2.6 O que é gratuito de verdade

| Serviço | Custo |
|---|---|
| Área do Investidor da B3 | R$ 0 |
| Registrato (BCB) | R$ 0 |
| Conta gov.br | R$ 0 |
| Simulador do Tesouro Direto | R$ 0 |
| Calculadora do Cidadão (BCB) | R$ 0 |
| Séries do BCB via API SGS | R$ 0, sem cadastro |
| Dados históricos do Tesouro Direto | R$ 0, em CSV |
| O [07-projeto-modelo](07-projeto-modelo/) deste curso | R$ 0, sem dependências |

---

## 3. "Corretagem zero": quem paga a conta?

A corretagem foi a zero e nada é de graça. As receitas migraram para:

| Fonte | Como funciona | Você percebe? |
|---|---|---|
| **Spread de renda fixa** | a corretora compra o CDB a 112% do CDI e te vende a 105% | não |
| **Rebate de fundos** | parte da taxa de administração volta para o distribuidor | não |
| **Float** | o dinheiro parado na sua conta da corretora rende para ela | não |
| **Câmbio** | spread na remessa internacional | pouco |
| **Juros de conta margem / crédito** | empréstimo com garantia de ativos | sim, se usar |
| **Comissão de ofertas (IPO, CRI, debênture)** | quem emite paga o distribuidor | não |

**Implicação prática:** "taxa zero" torna o custo **invisível**, não inexistente. A
defesa é comparar o mesmo produto em duas instituições e olhar a taxa **líquida** que
chega a você.

---

## 4. Custos ocultos que ninguém lista

| Custo oculto | Onde aparece | Como reduzir |
|---|---|---|
| **Spread de compra e venda** | Tesouro Direto e, muito maior, no secundário de debêntures/CRI | não vender antes do vencimento |
| **Deságio de liquidez** | vender papel ilíquido com pressa | só comprar ilíquido com prazo certo |
| **Custo de oportunidade** | dinheiro parado em conta corrente | aplicar no mesmo dia |
| **Custo tributário do giro** | cada resgate reinicia a tabela regressiva | rebalancear por aporte |
| **Aprisionamento (lock-in)** | carência, prazo, plano de previdência com carregamento | ler antes de assinar |
| **Custo do seu tempo** | otimizar 3 pontos de CDI em R$ 6.000 vale R$ 20/ano | ignorar micro-otimizações |
| **Custo emocional** | acompanhar o mercado diariamente | reduzir a frequência |

---

## 5. Licenças e autorizações — quem pode fazer o quê

Este é o "licenciamento" que protege o seu dinheiro:

| Atividade | Exige | Órgão | Como verificar |
|---|---|---|---|
| Operar como banco, financeira ou corretora | autorização de funcionamento | **BCB** | [Encontre uma instituição](https://www.bcb.gov.br/estabilidadefinanceira/encontreinstituicao) |
| Distribuir valores mobiliários | registro | **CVM** | [sistemas.cvm.gov.br](https://sistemas.cvm.gov.br/) |
| **Assessor de investimentos** | credenciamento; remunerado por **comissão** | CVM (Res. 178/2023) | consulta pública da CVM |
| **Consultor de valores mobiliários** | registro; remunerado por **honorário do cliente** | CVM (Res. 19/2021) | consulta pública da CVM |
| **Analista de valores mobiliários** | registro (na prática, via APIMEC/CNPI) | CVM (Res. 20/2021) | consulta pública |
| **Gestor de recursos** | autorização | CVM (Res. 21/2021) | consulta pública |
| Vender seguro e previdência aberta | autorização | **SUSEP** | site da SUSEP |

**A distinção que muda a sua vida financeira:**

- **Assessor** (antigo agente autônomo) trabalha **para a corretora** e é remunerado
  pelo que você compra. Não pode fazer recomendação personalizada de carteira.
- **Consultor** é remunerado **por você** e tem dever fiduciário. Pode recomendar.

Nenhum dos dois é ilegítimo — mas confundi-los é caríssimo. **Se a orientação é
gratuita, o produto está pagando por ela.**

---

## 6. Licença do material e do software deste curso

| Item | Situação |
|---|---|
| Textos deste curso | material de estudo pessoal; use e adapte livremente |
| Código do [07-projeto-modelo](07-projeto-modelo/) | escrito do zero, **sem dependências de terceiros**, sem restrição de uso |
| Python | licença PSF, gratuita, permite uso comercial |
| LibreOffice | Mozilla Public License 2.0, gratuita |
| Dados do BCB, IBGE, Tesouro e B3 | públicos e gratuitos; verifique os termos de cada portal para redistribuição comercial |

**Custo total para reproduzir tudo neste curso: R$ 0,00.**

---

## 7. Quanto custa se certificar (referência de preços, 2026)

Detalhes e avaliação de utilidade em [85-cursos-e-certificacoes.md](85-cursos-e-certificacoes.md).

| Certificação | Preço de inscrição | Fonte/data |
|---|---|---|
| **Nova CPA** (ANBIMA, substitui CPA-10) | **R$ 225,00** + taxa anual de atualização de **R$ 115,00** | ANBIMA, valores divulgados para 2026 |
| **C-Pro R** e **C-Pro I** (ANBIMA, sucedem a CEA) | **R$ 500,00** cada | ANBIMA, 2026 |
| CFG, CGA, CGE (gestão) | sem alteração anunciada para 2026 | ANBIMA |
| CFA (global, três níveis) | centenas a mais de mil dólares por nível, mais taxa de inscrição no programa | CFA Institute |
| Cursos da B3, CVM, ANBIMA Edu | **R$ 0** | portais oficiais |

> **Opinião profissional:** certificação é requisito **profissional** (para quem vai
> trabalhar distribuindo produtos), não requisito para investir bem o próprio dinheiro.
> Nenhuma certificação te fará ganhar mais como investidor pessoa física. Se o objetivo
> é cuidar do seu dinheiro, o conteúdo gratuito da B3, da CVM e do BCB cobre com folga —
> e este curso cobre o resto.

---

## 8. Comparação honesta de alternativas gratuitas

| Se você usaria… | Alternativa gratuita | O que se perde |
|---|---|---|
| Fundo DI de banco (0,5%–2% a.a.) | Tesouro Selic ou Tesouro Reserva | nada; ganha-se rendimento |
| Consultoria paga | este curso + simuladores oficiais | acompanhamento personalizado e responsabilidade profissional |
| Plataforma paga de análise | dados da B3, CVM, RI das empresas, séries do BCB | conveniência e agregação |
| Curso pago de investimentos | B3 Educação, CVM, ANBIMA Edu | certificado com marca, e pouco mais |
| Planilha paga de controle | LibreOffice/Sheets + o simulador deste curso | suporte |

---

## Autoteste

1. Qual é o custo explícito de manter R$ 6.000 em Tesouro Selic por um ano? E em
   Tesouro IPCA+?
2. "Corretagem zero" — cite três fontes de receita que substituíram a corretagem.
3. Qual a diferença de remuneração entre assessor e consultor, e por que isso importa
   para você?
4. Um fundo DI cobra 1,5% ao ano. Estime o custo em 10 anos sobre R$ 6.000.
5. Você negocia R$ 6.000 em BOVA11. Quanto paga de B3?
6. Por que taxa de carregamento em previdência é pior que taxa de administração alta?
7. Quanto custa a nova CPA da ANBIMA em 2026, e ela te ajuda a investir melhor?
8. Cite três custos ocultos e como evitá-los.

---

**Fontes consultadas em 20/08/2026:** B3 — tarifas de ações e fundos (negociação
0,0050% + liquidação 0,0250% = 0,030%) e tarifas do Tesouro Direto (custódia de
0,20% a.a., isenção até R$ 10 mil em Tesouro Selic, cobrança por evento desde
31/12/2024); ANBIMA — divulgação de preços das novas certificações de distribuição para
2026 (CPA R$ 225,00 e atualização anual R$ 115,00; C-Pro R e C-Pro I a R$ 500,00);
Resoluções CVM 19/2021, 20/2021, 21/2021 e 178/2023. Links em
[95-referencias.md](95-referencias.md).

**Próximo:** [85-cursos-e-certificacoes.md](85-cursos-e-certificacoes.md)
