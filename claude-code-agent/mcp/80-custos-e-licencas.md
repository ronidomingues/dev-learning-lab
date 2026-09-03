# 80 · Custos e licenças

`Nível: intermediário` · **Preços consultados em 01/09/2026** · **Câmbio usado: USD 1,00 = BRL 5,19**

> **Preço sem data é desinformação.** Tudo aqui tem data. Reconfira antes de decidir —
> preço de LLM e de nuvem muda a cada trimestre.
>
> **Primeira linha, para não deixar dúvida:** *o protocolo MCP é gratuito, e os SDKs
> oficiais também.* Você não paga nada pelo MCP. Você paga por **tokens de LLM** e,
> se o servidor for remoto, por **hospedagem**.

---

## 1. Licenças

| Componente | Licença | O que permite |
|---|---|---|
| **Especificação e código do projeto** | **Apache-2.0** para código e contribuições de especificação novos; contribuições legadas mantêm **MIT**; documentação em **CC-BY-4.0** | uso comercial, modificação, distribuição, uso privado |
| Titular do direito autoral | **"Model Context Protocol a Series of LF Projects, LLC"** | — |
| SDK Python (`mcp` 2.1.1) | **MIT** | idem |
| SDK TypeScript (`@modelcontextprotocol/server` 2.0.0) | **MIT** | idem |
| MCP Inspector 2.4.0 | **MIT** | idem |

**O que Apache-2.0 acrescenta em relação a MIT:** concessão explícita de patente e uma
cláusula de encerramento dessa concessão se você processar alguém por patente sobre a
obra. Para uso corporativo isso é uma **vantagem**, não uma restrição — é uma das razões
pelas quais projetos da Linux Foundation usam Apache-2.0.

**O que nenhuma das duas exige:** abrir o código do **seu** servidor MCP. Você pode
escrever um servidor proprietário, vendê-lo, e não publicar nada. As licenças cobrem a
especificação e os SDKs, não o que você constrói com eles.

**Quem paga a conta do protocolo:** a Agentic AI Foundation (Linux Foundation), sustentada
por Anthropic, Block, OpenAI, e apoiadores como Google, Microsoft, AWS, Cloudflare e
Bloomberg. **O incentivo é claro e vale enunciar:** para todos eles, um padrão neutro de
conexão vale mais do que um conector proprietário — porque o valor está no modelo e na
nuvem, não no cabo. Enquanto esse cálculo se mantiver, o MCP continua gratuito.

---

## 2. O que custa zero

| Item | Custo |
|---|---|
| Especificação | **R$ 0** |
| SDKs oficiais (10 linguagens) | **R$ 0** |
| MCP Inspector | **R$ 0** |
| Publicar no MCP Registry | **R$ 0** |
| Rodar servidor **stdio** local | **R$ 0** (a energia do seu laptop) |
| Aprender MCP inteiro | **R$ 0** — o Inspector é host suficiente, **e não precisa de LLM nenhum** |

Isso não é retórica: **você pode dominar o protocolo, escrever servidor e cliente,
depurar a fita JSON-RPC e testar tudo sem gastar um centavo e sem conta em serviço
nenhum.** É a maior vantagem econômica de aprender MCP.

---

## 3. O que custa: tokens

Aqui mora o custo real. Toda ferramenta que você expõe consome contexto em **cada**
mensagem da conversa; todo resultado consome tokens.

### 3.1 Preços da API da Anthropic — consultados em 01/09/2026

Por **milhão de tokens**:

| Modelo | Entrada (USD) | Saída (USD) | Entrada (BRL) | Saída (BRL) |
|---|---|---|---|---|
| Claude Fable 5 | 10,00 | 50,00 | ~51,90 | ~259,50 |
| Claude Opus 5 | 5,00 | 25,00 | ~25,95 | ~129,75 |
| Claude Sonnet 5 | 2,00 | 10,00 | ~10,38 | ~51,90 |
| Claude Haiku 4.5 | 1,00 | 5,00 | ~5,19 | ~25,95 |

Descontos que mudam a conta:

| Mecanismo | Efeito |
|---|---|
| **Leitura de cache** | **10%** da tarifa de entrada |
| Escrita de cache | 1,25× (TTL de 5 min) ou 2× (TTL de 1 h) |
| **Batch API** | **−50%** em entrada **e** saída |

> A leitura de cache a 10% é o número mais importante desta página para quem opera MCP em
> escala. É por isso que a spec `2026-07-28` pede **ordem determinística** em `tools/list`
> e introduziu `ttlMs`: um catálogo estável e idêntico entre requisições acerta o cache de
> prompt, e o custo do catálogo cai para um décimo.

### 3.2 A conta que ninguém faz

Cenário realista, com Claude Sonnet 5 (USD 2,00 por milhão de tokens de entrada):

- 3 servidores MCP conectados, 15 ferramentas cada = **45 ferramentas**;
- descrição + schema de cada uma ≈ **150 tokens** → catálogo ≈ **6.750 tokens**;
- conversa com **20 idas ao modelo**.

| Situação | Tokens de catálogo | Custo (USD) | Custo (BRL) |
|---|---|---|---|
| Sem cache de prompt | 6.750 × 20 = 135.000 | **0,27** | **~1,40** |
| Com cache (10%) | ≈ 6.750 + 128.250 × 0,1 | **0,04** | **~0,20** |

Por conversa. Multiplique por usuários e por dia.

Agora o outro lado — **o custo dos resultados**:

| Resultado da ferramenta | Tokens aprox. | Custo por chamada (Sonnet 5) |
|---|---|---|
| `SELECT *` com 5.000 linhas | ~250.000 | **USD 0,50** ≈ **R$ 2,60** |
| 20 linhas paginadas | ~600 | USD 0,0012 ≈ R$ 0,006 |
| resumo + `resource_link` | ~80 | desprezível |

**Uma única chamada mal projetada custa mais que o catálogo inteiro de uma conversa.**
É por isso que [23 · Projeto de ferramentas](23-projeto-de-ferramentas.md) é um arquivo de
economia tanto quanto de engenharia.

### 3.3 Assinaturas (para o usuário final)

Consultado em 01/09/2026:

| Plano | USD/mês | BRL aprox. |
|---|---|---|
| Claude Pro | 20 | ~104 |
| Claude Max 5× | 100 | ~519 |
| Claude Max 20× | 200 | ~1.038 |

Para quem **usa** servidores MCP num host, a assinatura é o custo; não há cobrança
separada por MCP. Para quem **opera** um servidor remoto para terceiros, quem paga os
tokens é o usuário do host — você paga hospedagem e as APIs que consumir.

---

## 4. O que custa: hospedagem de servidor remoto

Um servidor MCP remoto é um serviço HTTP comum — e essa é a boa notícia econômica da
revisão `2026-07-28`. Preços consultados em **01/09/2026**; confirme antes de decidir.

| Plataforma | Camada gratuita | Onde ela acaba | Pago (aprox.) |
|---|---|---|---|
| **Cloudflare Workers** | sim | limite de tempo de execução por requisição; edge não guarda estado local | ~USD 5/mês (inclui ~10 M requisições); Pro a partir de ~USD 20 |
| **Render** | sim, **sem cartão** | o serviço **dorme após 15 min** de inatividade — primeira requisição fria | ~USD 7/mês (Starter, sempre ligado) |
| **Railway** | crédito de ~USD 1/mês | cobre poucas horas de execução | ~USD 5/mês (Hobby) |
| **Fly.io** | **não há mais** para novos usuários; exige cartão | — | ~USD 2/mês uma VM pequena; **USD 8–25/mês** na prática, com egress e reinícios |
| **Nuvem grande** (Lambda, Cloud Run, ACA) | camada gratuita generosa | egress e cold start | varia muito |
| **VPS** | não | — | USD 5–10/mês |

**Recomendações, com o raciocínio:**

- para servidor pequeno e sem estado, **Cloudflare Workers** tem a melhor economia (o SDK
  TypeScript tem transporte específico para *Web Standards*, que roda em Workers);
- se o servidor é Python e você quer o deploy mais simples a partir de um repositório,
  **Railway** ou **Render**;
- **cuidado com a camada gratuita que dorme**: a primeira requisição do usuário demora, o
  host pode dar timeout, e o modelo "conclui" que a ferramenta não funciona.

---

## 5. Custos ocultos

Os que aparecem depois da decisão:

| Custo | Onde dói |
|---|---|
| **Egress** | resultados grandes, muitos usuários. Em nuvem grande, egress costuma passar da computação |
| **Chamadas de API a jusante** | se o seu servidor envolve serviço pago, o modelo pode chamá-lo em laço. **Limite de taxa é economia, não só segurança** |
| **Token do catálogo** | o custo mais invisível: 45 ferramentas cobram em **toda** mensagem |
| **Resultados grandes** | ver §3.2 |
| **Manutenção do protocolo** | cinco revisões em vinte meses. A janela de 12 meses ajuda, mas o roadmap já prevê redesenhar `tools/call` |
| **Suporte** | usuário com host diferente, versão diferente, comportamento diferente |
| **Auditoria e conformidade** | log de toda chamada, com retenção — armazenamento e processo |
| **Aprisionamento no host** | recursos, prompts e extensões têm suporte desigual: o servidor "funciona" só em alguns clientes |
| **Segurança** | revisão de servidores de terceiro, sandbox, resposta a incidente |
| **Aprendizado** | 15–25 h para um servidor útil; +25–50 h se envolver OAuth ([02 §3](02-pre-requisitos.md)) |

---

## 6. Alternativas gratuitas e abertas

| Em vez de… | Use | O que se perde |
|---|---|---|
| Claude (host pago) | **MCP Inspector** | nada, para aprender e depurar; não há modelo |
| Claude (host pago) | hosts open-source (Goose, entre outros) | maturidade e integrações |
| LLM comercial | modelo local (Ollama, llama.cpp) + host com MCP | qualidade de escolha de ferramenta cai bastante em modelos pequenos |
| Hospedagem paga | VPS próprio, ou servidor **stdio** | operação por sua conta / não funciona remoto |
| MCP Registry | distribuir por npm/PyPI/Docker | descoberta |

> **A alternativa gratuita que quase ninguém considera:** se todos os usuários estão na
> mesma máquina, **stdio resolve** e custa zero de hospedagem. A migração para HTTP deve
> ser motivada por multiusuário ou acesso remoto — não por elegância.

---

## 7. Como reduzir custo, em ordem de retorno

1. **Menos ferramentas.** 45 → 15 corta 2/3 do custo de catálogo em toda mensagem.
2. **Descrições enxutas, mas completas.** Diga o que não faz; não repita o schema.
3. **Ordem determinística + `ttlMs`.** Faz o cache de prompt acertar → **10%** da tarifa.
4. **Pagine.** É a diferença entre R$ 2,60 e R$ 0,006 por chamada.
5. **`resource_link`** em vez de embutir conteúdo.
6. **Limite de taxa** no servidor: impede o laço do modelo de esgotar a sua cota na API.
7. **Modelo menor onde couber.** Haiku 4.5 custa 1/5 de Sonnet 5 na entrada; para
   ferramentas simples e bem descritas, costuma bastar.
8. **Batch API** (−50%) para o que não é interativo.

---

## 8. Decisão de compra — quando MCP compensa

**Compensa quando:**

- há **mais de um consumidor** para a mesma capacidade (dois hosts, um host e um agente);
- o consumidor é de **terceiro** e você não controla o código dele;
- o conjunto de capacidades **muda** e você quer descoberta em tempo de execução;
- você já paga LLM e quer que ele alcance os seus sistemas.

**Não compensa quando:**

- só o **seu** aplicativo chama, e você controla os dois lados: chame a função direto;
- a tarefa é determinística e a sequência é conhecida: escreva um script;
- o volume de dados é grande e o valor de o modelo vê-los é baixo.

---

## 9. Autoteste

1. Sob que licença está a especificação do MCP hoje, e quem é o titular?
2. O que Apache-2.0 acrescenta em relação a MIT, e por que isso é bom para empresa?
3. Você precisa abrir o código do seu servidor MCP? Justifique pela licença.
4. Quem paga a conta do protocolo, e qual é o incentivo econômico por trás?
5. Quanto custa aprender MCP a fundo? Justifique.
6. Por que a leitura de cache a 10% é o número mais importante para quem opera em escala?
7. Compare o custo de um `SELECT *` de 5.000 linhas com o de 20 linhas paginadas, em reais.
8. Cite três custos ocultos e onde cada um dói.
9. Qual armadilha da camada gratuita afeta a experiência do usuário, e como?
10. Liste as três medidas de maior retorno para reduzir custo.

---

**Anterior:** [75 · Armadilhas](75-armadilhas.md) · **Próximo:** [85 · Cursos e certificações](85-cursos-e-certificacoes.md) · **Índice:** [00-MAPA](00-MAPA.md)

*Preços de API e assinaturas Anthropic, hospedagem e câmbio consultados na web em
**01/09/2026**; câmbio USD 1,00 = BRL 5,19. Licenças conferidas em: arquivo `LICENSE` do
repositório [modelcontextprotocol/modelcontextprotocol](https://github.com/modelcontextprotocol/modelcontextprotocol)
(Apache-2.0 para código e spec novos, MIT para contribuições legadas, CC-BY-4.0 para
documentação; titular "Model Context Protocol a Series of LF Projects, LLC");
metadados dos pacotes `mcp` 2.1.1 (MIT) e `@modelcontextprotocol/server` 2.0.0 (MIT)
lidos nesta máquina. Os cálculos de tokens da §3.2 são estimativas deste material, com as
premissas declaradas.*
