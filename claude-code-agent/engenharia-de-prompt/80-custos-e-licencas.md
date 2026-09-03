# 80 · Custos e licenças

**Nível:** todos
**Preços consultados na web em 19/08/2026.** Câmbio de referência do dia:
**US$ 1 ≈ R$ 5,22**. Preço sem data é desinformação — se você está lendo isto
meses depois, **confirme antes de decidir**.

---

## 80.1 · Resumo em uma linha

> **Aprender engenharia de prompt custa zero.** Todo o material oficial de
> qualidade é gratuito, e o [projeto-modelo](07-projeto-modelo/README.md) deste
> curso roda offline. O custo aparece quando você vai para produção — e aí ele
> é de API, medido em tokens.

---

## 80.2 · O que custa e o que não custa

| Item | Custo | Observação |
|---|---|---|
| Estudar com este curso | **R$ 0** | provedor simulado roda sem chave |
| Documentação oficial dos fornecedores | **R$ 0** | e é o melhor material que existe |
| Anthropic Academy (cursos + certificados) | **R$ 0** | aberta em 02/03/2026 |
| Tutorial interativo de prompt da Anthropic | **R$ 0** | GitHub e Google Sheets |
| Learn Prompting, guia DAIR.AI | **R$ 0** | há trilha em português |
| Python, `anthropic`, `promptfoo`, `dspy`, `uv` | **R$ 0** | todos MIT / Apache-2.0 |
| Chatbot com camada gratuita | **R$ 0** | com cota diária |
| Google AI Studio (API com limite) | **R$ 0** | sem cartão |
| **API de produção** | **paga** | por token; ver abaixo |
| Assinatura de chatbot profissional | US$ 17–20/mês | ~R$ 89–104 |

---

## 80.3 · Assinaturas de chatbot (19/08/2026)

| Plano | Preço divulgado | ~BRL/mês | Para quem |
|---|---|---|---|
| Claude Free | US$ 0 | R$ 0 | experimentar |
| **Claude Pro** | US$ 17/mês no anual (US$ 200 à vista) ou **US$ 20** no mensal | ~R$ 89–104 | uso diário sério |
| Claude Max 5× | a partir de US$ 100/mês | ~R$ 522 | uso intensivo |
| Claude Team | US$ 20/assento no anual, US$ 25 no mensal | ~R$ 104–131 | equipes |
| Claude Enterprise | assento (US$ 20) + uso a preço de API | — | corporativo |
| ChatGPT Plus | ~US$ 20/mês (≈ R$ 104 no Brasil) | ~R$ 104 | comparação |
| Gemini (plano pago) | ≈ R$ 114/mês no Brasil | R$ 114 | comparação |

**Atenção brasileira:** cobrança internacional soma **IOF** e spread do cartão.
O que aparece na fatura fica tipicamente 5% a 10% acima da conversão direta.

**Você precisa de assinatura para aprender?** Não. É conforto, não requisito.

---

## 80.4 · API — o que realmente vai custar

Preços da Anthropic por **milhão de tokens**, 19/08/2026:

| Modelo | Entrada | Saída | ~BRL entrada | ~BRL saída |
|---|---|---|---|---|
| Claude Opus 5 | US$ 5,00 | US$ 25,00 | R$ 26,10 | R$ 130,50 |
| Claude Sonnet 5 | US$ 3,00 | US$ 15,00 | R$ 15,66 | R$ 78,30 |
| Claude Haiku 4.5 | US$ 1,00 | US$ 5,00 | R$ 5,22 | R$ 26,10 |

Modificadores:

| Modificador | Efeito |
|---|---|
| leitura de cache | ~0,1× o preço da entrada (**−90%**) |
| escrita no cache | ~1,25× o preço da entrada |
| lote assíncrono | **−50%** em entrada e saída |

**Ordem de grandeza para calibrar a intuição** (Opus 5, sem cache):

| Uso | Estimativa |
|---|---|
| um "olá mundo" com resposta curta | fração de centavo de dólar |
| rodar o conjunto de 22 casos do projeto-modelo | **< US$ 0,10** (~R$ 0,52) |
| 10 mil classificações de 1.000 tokens de entrada e 100 de saída | ~US$ 75 (~R$ 390) |
| o mesmo, com cache de 90% do prefixo + lote | **~US$ 15** (~R$ 78) |

Use a calculadora de [30 §30.2](30-custo-latencia-caching.md) para o seu caso.

**Exige cartão de crédito?** Sim, na API da Anthropic: você compra crédito
antecipado. **Não** exige no Google AI Studio nem no ollama local.

---

## 80.5 · Licenças

### As ferramentas

| Ferramenta | Licença | O que permite |
|---|---|---|
| SDK `anthropic` (Python/TS) | MIT | uso comercial livre |
| `promptfoo` | MIT | uso comercial livre |
| `dspy` | MIT | uso comercial livre |
| `uv` | MIT / Apache-2.0 | uso comercial livre |
| Python | PSF License | uso comercial livre |
| Node.js | MIT | uso comercial livre |

Nada aqui contamina o seu código. Não há GPL no caminho padrão.

### O modelo — e aqui muda a natureza da coisa

> **Você não licencia o modelo. Você contrata um serviço.** O que rege é o
> **termo de uso** do fornecedor, não uma licença de software.

Implicações que costumam pegar equipes de surpresa:

| Questão | O que verificar |
|---|---|
| **Propriedade da saída** | os principais fornecedores atribuem a saída ao cliente; confirme no seu contrato |
| **Uso dos seus dados para treino** | em planos de API costuma ser negado por padrão; **confirme por escrito** |
| **Retenção** | por quanto tempo os prompts ficam armazenados; há configurações de retenção zero em planos corporativos |
| **Uso proibido** | toda política tem lista de usos vedados; violar suspende a conta |
| **Disponibilidade** | não há garantia implícita; SLA é contratual |
| **Mudança de modelo** | o fornecedor pode depreciar o modelo que você usa — planeje migração |

### Modelos abertos

Modelos com pesos abertos (Llama, Mistral, Qwen e outros) têm licenças
**próprias e diferentes entre si** — algumas restringem uso comercial acima de
certa escala, outras exigem atribuição. **Leia a licença do modelo específico
antes de usar comercialmente.** "Aberto" não é sinônimo de "livre".

---

## 80.6 · Custos ocultos

O que não aparece na tabela de preços e aparece no fim do trimestre:

| Custo oculto | Como se manifesta | Mitigação |
|---|---|---|
| 💸 **Cache invalidado** | conta 10× a estimada, sem sintoma | monitorar tokens lidos de cache |
| 💸 **Histórico reenviado** | custo cresce com o quadrado da conversa | janela, compactação |
| 💸 **Retentativas por formato inválido** | cada falha é uma chamada inteira paga | saída estruturada, validação |
| 💸 **Agente sem teto de passos** | cauda de custo brutal em poucos casos | política de parada |
| **Avaliação em CI** | US$ 2–5 por PR × 200 PRs/mês | conjunto reduzido no PR |
| **Tempo humano de rotulagem** | o maior custo real, e não entra em planilha nenhuma | reaproveitar produção, rotular por amostragem |
| **Migração de modelo** | reavaliar e reajustar tudo a cada geração | manter a suíte automatizada |
| **Aprisionamento de fornecedor** | prompt e ferramentas ajustados a uma API | abstrair o provedor (o [projeto-modelo](07-projeto-modelo/provedor.py) mostra como, em 30 linhas) |
| **Egresso e observabilidade** | plataformas cobram por traço armazenado | amostrar em vez de guardar tudo |

**O maior de todos é o tempo humano de rotulagem.** Ninguém orça, todo mundo
paga.

---

## 80.7 · Alternativas gratuitas e o que se perde

| Em vez de | Use | O que perde |
|---|---|---|
| API paga, para estudar | provedor simulado do projeto-modelo | não mede prompt de verdade — mede o arnês |
| API paga, para protótipo | Google AI Studio (gratuito com limite) | limite de requisições; modelo diferente |
| API paga, para volume | ollama local | qualidade, velocidade e janela menores |
| plataforma de avaliação | seu script + promptfoo | painéis e colaboração |
| assinatura de chatbot | camada gratuita | cota e modelos menores |
| curso pago | Anthropic Academy + Learn Prompting | nada relevante — sério |

---

## 80.8 · Quem paga a conta do que é gratuito

Vale entender os incentivos, porque eles explicam a qualidade e a durabilidade:

- **Documentação e cursos dos fornecedores são gratuitos** porque quem sabe
  usar bem consome mais tokens. O interesse é alinhado com o seu — e por isso
  o material é honestamente bom. O viés é que ele fala do produto **deles**.
- **`promptfoo`, `dspy` e SDKs são abertos** porque adoção vira padrão de fato,
  e padrão de fato vira receita a jusante. Com a aquisição do promptfoo pela
  OpenAI (09/03/2026), esse incentivo passou a ser de um fornecedor de modelos
  — vale acompanhar.
- **Sites de "1000 prompts prontos" são gratuitos** porque vivem de anúncio e
  de venda de curso. O incentivo é tráfego, não correção. É por isso que a
  qualidade média deles é ruim.

---

## Autoteste

1. Qual é o custo real de aprender engenharia de prompt até o nível 2?
2. Por que o modelo não é "licenciado" para você, e o que isso muda?
3. Cite quatro custos ocultos e a mitigação de cada um.
4. Qual é o maior custo real de um projeto sério, e por que não aparece em
   planilha?
5. Por que a documentação dos fornecedores é gratuita e boa — e qual é o viés
   dela?
6. Você quer prototipar sem cartão de crédito. Quais são as opções e o que se
   perde?

---

### Fontes consultadas (19/08/2026)

- Claude — página de preços — <https://claude.com/pricing>
- Preços de API (entrada/saída por milhão de tokens), documentação do fornecedor
- TechTudo, *Quanto custa usar IA em 2026* (jun/2026) — <https://www.techtudo.com.br/guia/2026/06/quanto-custa-usar-ia-em-2026-compare-precos-do-chatgpt-gemini-claude-e-mais-edsoftwares.ghtml>
- Cotação USD/BRL de 19/08/2026 (≈ R$ 5,22) — <https://investidor10.com.br/moedas/usd/>
- OpenAI, aquisição do promptfoo (09/03/2026) — <https://openai.com/index/openai-to-acquire-promptfoo/>
