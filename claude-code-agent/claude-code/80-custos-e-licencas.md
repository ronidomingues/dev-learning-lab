# 80 · Custos e licenças

> **Nível:** todos
> **📅 Preços consultados em 13/08/2026.** Preço sem data é desinformação — confira em
> [claude.com/pricing](https://claude.com/pricing) antes de decidir.
> **Câmbio usado:** US$ 1 ≈ **R$ 5,18** (cotação consultada em 13/08/2026). Os valores em
> BRL são **ordem de grandeza**, não cotação — o câmbio muda todo dia.

---

## 1. Os dois modelos de cobrança

| | **Assinatura** | **API (por uso)** |
|---|---|---|
| Como paga | mensalidade fixa | por token consumido |
| Previsibilidade | alta | baixa |
| Para quem | pessoa física, uso diário | automação, CI, times com controle centralizado |
| Limite | cotas com janelas móveis | limite de gasto configurável |

Dá para usar os dois: assinatura no terminal do dia a dia, chave de API na automação.

---

## 2. Planos de assinatura — 13/08/2026

Preços de [claude.com/pricing](https://claude.com/pricing), consultados em 13/08/2026.

| Plano | Mensal (USD) | Anual (USD/mês) | ≈ BRL/mês | Claude Code |
|---|---|---|---|---|
| **Free** | 0 | 0 | 0 | Listado como incluído, com limites muito apertados |
| **Pro** | **20** | 17 (US$ 200 à vista) | ≈ R$ 104 | Incluído |
| **Max 5×** | a partir de **100** | — | ≈ R$ 518 | Incluído |
| **Max 20×** | a partir de **100** | — | ≈ R$ 518+ | Incluído |
| **Team — assento padrão** | **25**/assento | 20/assento | ≈ R$ 130 | Incluído (+ Cowork) |
| **Team — assento premium** | **125**/assento | 100/assento | ≈ R$ 648 | Incluído |
| **Enterprise** | **20**/assento + uso | — | ≈ R$ 104 + uso | Incluído |

**Sobre o plano Free:** a página de preços lista Claude Code como incluído, mas as cotas são
apertadas o bastante para você esbarrar nelas em minutos de uso agêntico. **Trate como
demonstração, não como caminho de trabalho.** A documentação de instalação é mais direta:
diz que o Claude Code exige conta Pro, Max, Team, Enterprise ou Console.

**Como funciona a cota nos planos por assinatura:** janelas móveis de **5 horas** e
**semanal**, compartilhadas entre Claude Code, Claude chat e Cowork. Ao estourar, você vê
"You've hit your session limit" ou "your weekly limit", com a hora de reinício. Trocar de
modelo **não** restaura o acesso — as janelas são compartilhadas entre modelos.

**Créditos de uso** (*usage credits*) permitem continuar além da cota, cobrados à parte, com
limite de gasto configurável. Gerenciados por `/usage-credits`.

---

## 3. Preço por token — API, 13/08/2026

Valores por **milhão de tokens (MTok)**, de
[platform.claude.com/docs/en/about-claude/pricing](https://platform.claude.com/docs/en/about-claude/pricing),
consultado em 13/08/2026.

| Modelo | Entrada | Escrita de cache (5 min) | Escrita de cache (1 h) | **Leitura de cache** | Saída |
|---|---|---|---|---|---|
| **Fable 5** | US$ 10 | 12,50 | 20 | **1,00** | US$ 50 |
| **Opus 5** | US$ 5 | 6,25 | 10 | **0,50** | US$ 25 |
| **Opus 4.8 / 4.7 / 4.6 / 4.5** | US$ 5 | 6,25 | 10 | **0,50** | US$ 25 |
| **Sonnet 5** | US$ 2 | 2,50 | 4 | **0,20** | US$ 10 |
| **Sonnet 4.6 / 4.5** | US$ 3 | 3,75 | 6 | **0,30** | US$ 15 |
| **Haiku 4.5** | US$ 1 | 1,25 | 2 | **0,10** | US$ 5 |

Três leituras que valem dinheiro:

1. **Sonnet 5 custa 40% da entrada de Opus 5 e 40% da saída.** Para a maior parte do trabalho
   de código, a diferença de resultado não justifica a de preço. Use Opus onde o raciocínio é
   o gargalo.
2. **Leitura de cache custa 10% da entrada.** É a razão de sessão contínua sair mais barata.
   O cache de 5 min se paga depois de **uma** leitura; o de 1 h, depois de **duas**.
3. **Modelos 4.7 e posteriores usam um tokenizador novo que produz ~30% mais tokens para o
   mesmo texto.** Comparar preço por MTok entre gerações **sem** corrigir por isso subestima
   o custo dos mais novos. Poucos materiais mencionam; é armadilha real de planilha.

Janela de 1 M de tokens: sem preço diferenciado nos modelos 4.6+ — uma requisição de 900 mil
tokens é cobrada à mesma taxa por token de uma de 9 mil.

**Descontos:** Batch API dá **50%** em entrada e saída (não serve para uso interativo).
Fast mode é premium: US$ 10 entrada / US$ 50 saída em Opus 5 e 4.8.
`inference_geo: "us"` (residência de dados nos EUA) aplica multiplicador **1,1×**.

---

## 4. Quanto custa na vida real

**[fato, documentação oficial de custos consultada em 13/08/2026]**

| Métrica | Valor |
|---|---|
| Média por dev por **dia ativo** | **~US$ 13** (≈ R$ 67) |
| Média por dev por **mês** | **US$ 150–250** (≈ R$ 780–1.300) |
| 90% dos usuários | abaixo de US$ 30/dia ativo |
| Uso de fundo com sessão ociosa | tipicamente < US$ 0,04 por sessão |

**Medição real feita neste curso**, 13/08/2026, projeto-modelo, Opus 5 com janela de 1 M:

```json
{ "total_cost_usd": 0.1906005,
  "usage": { "input_tokens": 4, "cache_read_input_tokens": 47811,
             "cache_creation_input_tokens": 16300, "output_tokens": 147 } }
```

**US$ 0,19 (≈ R$ 0,99) para contar quantos testes há num arquivo.** Repare: 4 tokens de
entrada nova contra 47.811 de leitura de cache e 16.300 de escrita. **Você paga o contexto,
não a pergunta.** É a lição econômica central do curso, e ela está num JSON medido, não numa
opinião.

Comparação de decisão, fazendo a conta de cabeça: **Pro custa US$ 20/mês.** Se você usa 15
dias por mês a US$ 13/dia na API, seriam US$ 195. Para uso individual diário, **a assinatura
ganha com folga.** A API ganha em automação (que roda pouco e precisa de teto) e em
organizações que querem cobrança centralizada.

---

## 5. Onde o dinheiro vaza

| Vazamento | Por que acontece | Correção |
|---|---|---|
| **Sessão aberta o dia inteiro** | Todo o contexto é reenviado a cada turno | `/clear` entre tarefas |
| **Opus como padrão** | Ficou configurado e ninguém revisou | `/model sonnet`; Opus só no difícil |
| **Servidores MCP demais** | Definições em **toda** mensagem | `/mcp` para desabilitar; prefira CLI |
| **Saída de comando volumosa** | `npm test` verboso = dezenas de milhares de tokens | Hook que filtra ([`06`](06-exemplos.md), ex. 11) |
| **`CLAUDE.md` de 800 linhas** | Custa em toda sessão | Abaixo de 200 linhas |
| **Perda de cache** | Voltar depois de 1 h reprocessa tudo | Tarefas contínuas; `ENABLE_PROMPT_CACHING_1H=1` ao usar créditos |
| **Times de agentes** | **~7× o consumo** de uma sessão normal | Times pequenos, Sonnet nos companheiros, encerrar quem terminou |
| **Automação sem teto** | Laço patológico em CI | `--max-budget-usd`, `--max-turns` |
| **Tarefas agendadas** | Disparam mesmo com a sessão ociosa | Revise o que está agendado |

`/usage` mostra a atribuição por skill, subagente, plugin e servidor MCP, e sinaliza
comportamentos (contexto longo, perda de cache) acima de 10% do uso recente.

---

## 6. Licença

**Claude Code é software proprietário.** Não é código aberto. Regido pelos termos comerciais
(Team, Enterprise, API) ou de consumidor (Free, Pro, Max) da Anthropic.

| Item | Situação |
|---|---|
| Uso comercial | Permitido, dentro dos termos do plano |
| Código que você escreve com ele | **Seu.** A Anthropic não reivindica propriedade sobre a saída |
| Redistribuir o Claude Code | Não |
| Rodar sem internet | Não |
| Auditar o código-fonte | Não. Há verificação de integridade por assinatura GPG dos binários ([`03`](03-instalacao.md)) |
| Seus dados no treinamento | **Depende do plano e das suas configurações.** Confira em `/privacy-settings` — termos comerciais e de consumidor são documentos diferentes |
| Certificações | SOC 2 Tipo 2, ISO 27001 — [trust.anthropic.com](https://trust.anthropic.com) |

O que **é** aberto no entorno: o **Model Context Protocol** (padrão aberto), a especificação
**Agent Skills** e o marketplace de plugins da comunidade.

---

## 7. Custos ocultos

Os que ninguém coloca na planilha:

| Custo | Ordem de grandeza |
|---|---|
| **Tempo de revisão** | Provavelmente **maior que a assinatura**. Se cada dev revisa 1 h/dia a mais de código gerado, isso custa muito mais de R$ 104/mês |
| **Arrumar o repositório** | Testes, convenções, build rápido. É investimento, não desperdício — mas é real e vem antes |
| **Aprendizado** | 3–4 meses até o nível profissional ([`02`](02-pre-requisitos.md)) |
| **Manutenção da configuração** | Hooks e skills quebram quando o projeto muda |
| **Aprisionamento** | Sua configuração (hooks, skills, agentes) é específica do Claude Code. MCP e Agent Skills são portáveis; o resto não |
| **Egresso** | Não há taxa de saída, mas migrar a configuração para outro agente é trabalho manual |
| **Suporte** | Incluso no plano; canal humano varia por plano |

---

## 8. Alternativas gratuitas ou abertas

| Alternativa | Licença | O que se perde |
|---|---|---|
| **opencode** e agentes de terminal abertos | Aberta (MIT em vários casos) | Você traz sua chave de API — não é grátis de fato; a profundidade da plataforma (hooks, skills, subagentes) é menor |
| **Aider** | Apache 2.0 | Muito bom em edição guiada por git; menos capacidade agêntica ampla |
| **Continue.dev** | Apache 2.0 | Extensão de IDE; não é agente de terminal |
| **Modelos locais** (Ollama + modelo de código) | Variada | **Realmente gratuito** depois do hardware. Qualidade bem abaixo para trabalho agêntico; precisa de GPU boa |
| **Gemini CLI / Antigravity CLI** (Google) | Camada gratuita variável | Ecossistema e cotas diferentes; ver [`65`](65-estado-da-arte.md) |

**Se o orçamento é zero de verdade:** modelo local com Ollama é a única opção realmente
gratuita, e você deve calibrar a expectativa para bem abaixo. **[opinião]** Para aprendizado
de conceitos, funciona; para trabalho agêntico de verdade em 2026, ainda não.

**O que este curso ensina que é transferível:** engenharia de contexto, escada de garantia,
verificação automática, quando não usar. Nada disso é específico da ferramenta.

---

## 9. Quem paga a conta, e por quê

O preço reflete um custo real: cada turno é inferência em GPU cara. Não há versão "grátis
sustentável" porque não existe custo marginal zero — diferente de software tradicional, cada
uso consome computação.

Os incentivos do ecossistema, ditos abertamente:

- **Anthropic** ganha com uso. Isso alinha em parte (o produto precisa ser bom) e desalinha
  em parte (contexto maior gera mais receita). O cache e as ferramentas de redução de custo
  são evidência de que o alinhamento pesa mais — mas você é quem tem que medir.
- **Provedores de nuvem** (Bedrock, Google Cloud, Foundry) revendem inferência com margem.
- **Você** ganha se o tempo economizado valer mais que a assinatura — o que quase sempre
  ocorre, **desde que exista verificação automática** ([`25`](25-o-oficio-do-profissional.md)).

---

## Fontes consultadas

- [claude.com/pricing](https://claude.com/pricing) — planos e preços de assinatura, 13/08/2026.
- [platform.claude.com/docs/en/about-claude/pricing](https://platform.claude.com/docs/en/about-claude/pricing) — preços por token, cache, batch, fast mode, 13/08/2026.
- [code.claude.com/docs/en/costs](https://code.claude.com/docs/en/costs) — custo médio por dev, cotas, atribuição, 13/08/2026.
- Câmbio USD/BRL ≈ 5,18, consultado em 13/08/2026 (fontes de mercado; valor aproximado).
- Medição local com `claude -p --output-format json` no projeto-modelo, 13/08/2026.

---

## Autoteste

1. Quanto custa Pro, e quando a API compensa mais que a assinatura?
2. Por que leitura de cache custar 10% da entrada muda a estratégia de sessão?
3. O que muda no cálculo de custo entre gerações por causa do tokenizador novo?
4. No JSON medido, por que a pergunta custou US$ 0,19? Qual componente dominou?
5. Cite quatro vazamentos de dinheiro e a correção de cada um.
6. Claude Code é código aberto? O que **é** aberto no entorno?
7. Qual é provavelmente o maior custo oculto, e por que ele não aparece na planilha?
8. Qual é a única alternativa realmente gratuita, e o que se perde com ela?
