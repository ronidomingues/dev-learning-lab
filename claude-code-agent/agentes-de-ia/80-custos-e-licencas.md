# 80 · Custos e licenças

**Nível:** todos
**Preços consultados em 13/08/2026** em [claude.com/pricing](https://claude.com/pricing)
e na documentação da Anthropic.

⚠️ **Preço sem data é desinformação.** Tudo aqui tem a data acima. Confirme na
página oficial antes de decidir. Valores em USD; a conversão para BRL usa
US$ 1 ≈ R$ 5,40 e serve só para dar ordem de grandeza.

---

## 1. Assinaturas

| Plano | Mensal | Anual (por mês) | ≈ BRL/mês | Claude Code |
|---|---|---|---|---|
| Free | US$ 0 | — | — | ver a nota abaixo |
| **Pro** | US$ 20 | US$ 17 (US$ 200 à vista) | ≈ R$ 110 | incluído |
| **Max 5×** | US$ 100 | — | ≈ R$ 540 | incluído, 5× o Pro |
| **Max 20×** | US$ 200 | — | ≈ R$ 1 080 | incluído, 20× o Pro |
| **Team** (padrão) | US$ 25/assento | US$ 20/assento | ≈ R$ 110 | incluído |
| **Team** (premium) | US$ 125/assento | US$ 100/assento | ≈ R$ 540 | 5× o assento padrão |
| **Enterprise** | sob consulta (≈ US$ 20/assento + uso a preço de API) | — | — | incluído |

> **Divergência de fontes sobre o plano gratuito, em 13/08/2026.** A página de
> preços da Anthropic indica que o plano Free inclui Claude Code com uso
> limitado; a página *Advanced setup* da documentação afirma que "o plano
> gratuito do Claude.ai não inclui acesso ao Claude Code". Não consegui
> resolver a contradição sem uma conta gratuita para testar. **Trate o Free
> como insuficiente para uso real de qualquer forma** — o consumo de tokens do
> Claude Code é alto o bastante para esgotar qualquer camada gratuita em
> minutos — e confirme na página de preços antes de assumir.

**Como os limites funcionam.** A Anthropic **não publica cotas exatas de
tokens** para os planos de assinatura. O que se sabe:

- Multiplicadores: Pro = 1×, Max 5× = 5×, Max 20× = 20×.
- Há uma janela móvel de 5 horas e limites semanais.
- O consumo depende do tamanho da conversa, do modelo, do `effort` e das
  ferramentas usadas.
- Cada assinatura paga inclui Claude Code e os outros produtos Claude,
  **sacando do mesmo bolso de uso**.

Na prática: `/usage` é a única medida confiável do **seu** consumo.

**Como escolher.**

| Situação | Plano |
|---|---|
| Experimentar, uso ocasional | Pro |
| Uso diário, algumas horas | Pro, subindo para Max se bater no limite |
| Claude Code aberto o dia inteiro | Max 5× |
| Sessões paralelas, subagentes, `/batch` | Max 20× |
| Time com necessidade de administração | Team |
| Governança, ZDR, SSO | Enterprise |

Sinal prático de que é hora de subir: bater no aviso de limite mais de uma ou
duas vezes por semana.

---

## 2. API (pagamento por uso)

Preço por **milhão de tokens** (entrada / saída):

| Modelo | Contexto | Entrada | Saída |
|---|---|---|---|
| Claude Fable 5 | 1 M | US$ 10 | US$ 50 |
| **Claude Opus 5** | 1 M | US$ 5 | US$ 25 |
| Claude Opus 4.8 | 1 M | US$ 5 | US$ 25 |
| **Claude Sonnet 5** | 1 M | US$ 3 (intro. US$ 2 até 31/08/2026) | US$ 15 (intro. US$ 10) |
| Claude Sonnet 4.6 | 1 M | US$ 3 | US$ 15 |
| Claude Haiku 4.5 | 200 K | US$ 1 | US$ 5 |

**Três descontos que mudam a conta de verdade:**

| Mecanismo | Efeito |
|---|---|
| **Cache de prompt** | leitura ≈ 10% do preço de entrada; escrita 1,25× (TTL 5 min) ou 2× (1 h) |
| **Batches** | 50% de desconto para trabalho assíncrono |
| **Modelo menor onde cabe** | Haiku custa 1/5 do Opus na entrada |

O cache é o mais relevante para agentes: o prefixo (sistema + ferramentas +
histórico) repete a cada volta. Um agente com cache bem posicionado custa uma
fração do mesmo agente com um `datetime.now()` no prompt de sistema — e a
diferença não aparece como erro, só na fatura.

**Ordens de grandeza, com todas as ressalvas.** A variância é grande; use como
faixa, não como orçamento:

| Tarefa | Faixa típica |
|---|---|
| Pergunta sobre o repositório | US$ 0,05 – 0,30 |
| Corrigir um bug com teste | US$ 0,30 – 2,00 |
| Refatoração média (3–5 arquivos) | US$ 1 – 5 |
| Revisão de PR grande | US$ 1 – 4 |
| `/code-review ultra` (multiagente na nuvem) | mais alto; 3 execuções grátis em Pro/Max, depois créditos |
| Migração com `/batch` (30 unidades) | US$ 20 – 100+ |

Meça o **seu** caso: `/usage` antes e depois, ou `--max-budget-usd` para
limitar.

**Assinatura ou API?** Regra de bolso: uso diário e interativo compensa na
assinatura; automação, CI e cargas variáveis compensam na API, onde você paga
o que usa e consegue **teto por invocação** (`--max-budget-usd`), que a
assinatura não oferece.

---

## 3. Custos ocultos

| Custo | Por quê |
|---|---|
| **Tempo de revisão humana** | o maior de todos, e o que nunca aparece na planilha. Código que ninguém revisa é passivo |
| **Sessões paralelas** | 5 sessões = ~5× o consumo. `/batch` e workflows multiplicam mais |
| **Contexto inchado** | `CLAUDE.md` grande e MCPs demais são pagos em **toda** chamada |
| **Cache invalidado** | um timestamp no prompt de sistema pode triplicar o custo em silêncio |
| **Voltas desperdiçadas** | mensagem de erro ruim → o agente repete → você paga a repetição |
| **Retrabalho** | pedido vago → resultado errado → refazer |
| **Aprisionamento suave** | `CLAUDE.md`, skills, hooks e servidores MCP são específicos do Claude Code. Migrar exige reescrita |
| **Segurança e conformidade** | revisar servidores MCP, auditar, treinar o time |
| **Infraestrutura de avaliação** | montar e rodar a suíte de [20](20-avaliacao-e-benchmarks.md) |

**Sobre o aprisionamento, sendo específico:** o MCP é aberto e portátil — um
servidor MCP seu funciona com qualquer cliente que fale o protocolo. Já
`CLAUDE.md`, skills, subagentes, hooks e plugins são formatos do Claude Code.
Nenhum é difícil de reescrever, mas nenhum migra automaticamente. Se
portabilidade importa, invista nos servidores MCP e mantenha o resto enxuto.

---

## 4. Licenças

**Claude Code** é **software proprietário** da Anthropic, sob os termos
comerciais / de uso do consumidor da empresa. Não é código aberto. Você não
pode redistribuir, e o uso é vinculado a uma conta ativa.

**MCP** é a exceção importante: a especificação e os SDKs oficiais são
**abertos** (licença MIT). Você pode implementar cliente ou servidor
livremente, e a Anthropic não controla quem os usa.

**Claude Agent SDK** — biblioteca da Anthropic para construir agentes; use os
termos do repositório oficial como referência.

**O código que o agente escreve é seu**, conforme os termos de uso da
Anthropic. Confirme a redação vigente antes de decidir política corporativa —
e note que a questão jurídica de autoria de código gerado por IA (em especial
registrabilidade) continua em movimento em várias jurisdições, inclusive no
Brasil. Isso é observação, não aconselhamento jurídico.

---

## 5. Dados e privacidade

| Item | Onde está | Controle |
|---|---|---|
| Arquivos lidos, saídas de comando | vão para a API | `deny` de leitura, `--disallowedTools` |
| Transcritos das sessões | `~/.claude/projects/`, texto claro, local | `claude project purge` |
| Uso para treinamento | depende do plano e das configurações | `/privacy-settings`; Enterprise com ZDR |
| Telemetria | opcional | `DISABLE_TELEMETRY=1` |

**Retenção zero (ZDR)** está disponível para contas Enterprise qualificadas, e
desativa alguns recursos em troca. Rodar por **Amazon Bedrock, Google Cloud ou
Microsoft Foundry** é a outra rota para quem precisa que o tráfego passe pela
própria conta de nuvem — com o custo de perder alguns recursos (ver a tabela
de disponibilidade por plataforma na documentação).

---

## 6. Alternativas abertas

Se o custo, a licença ou a política inviabilizarem o Claude Code:

| Ferramenta | Licença | O que é | O que se perde |
|---|---|---|---|
| **[Aider](https://aider.chat/)** | Apache 2.0 | agente de código no terminal, multi-modelo | menos ferramentas, sem subagentes/hooks/skills |
| **[OpenHands](https://github.com/All-Hands-AI/OpenHands)** | MIT | plataforma de agentes com sandbox | mais complexo de operar |
| **[Cline](https://github.com/cline/cline)** | Apache 2.0 | extensão de VS Code, aceita modelo local | preso à IDE |
| **[Continue](https://continue.dev/)** | Apache 2.0 | assistente em IDE, configurável | menos agêntico |
| **[Goose](https://block.github.io/goose/)** (Block) | Apache 2.0 | agente com MCP nativo | ecossistema menor |
| **smolagents / LangGraph / CrewAI** | Apache/MIT | bibliotecas para construir o seu | você constrói tudo |

Com **modelos abertos** (Qwen, DeepSeek, Llama e sucessores) rodando local via
Ollama ou vLLM, o custo marginal por token vai a zero — pagando em hardware,
em latência e em capacidade, especialmente no uso de ferramentas de cauda
longa e em contexto longo.

**Quem paga a conta nas ferramentas abertas:** empresas que ganham em outra
camada (Block, All Hands, Anysphere) ou financiamento de risco. Isso importa
para prever longevidade — projeto sem modelo de receita nem fundação é aposta.

---

## 7. Reduzir custo, em ordem de retorno

1. **`/clear` ao trocar de assunto.** O maior ganho isolado.
2. **`CLAUDE.md` enxuto e poucos MCPs.** Custo fixo, pago sempre.
3. **Cache com prefixo estável.** Sem timestamps no prompt de sistema.
4. **`effort` calibrado.** `low` em subagente de leitura; `xhigh` só onde
   compensa.
5. **Modelo menor onde cabe.** Haiku para classificação e triagem.
6. **`--max-budget-usd` em tudo que é automático.** Teto conhecido.
7. **`| tail -50` nas saídas de comando.**
8. **Pedidos específicos.** Retrabalho é o desperdício mais caro.
9. **Batches** para o que não é interativo (50% de desconto).
10. **Meça.** `/usage`, `/insights`, e a suíte de avaliação com coluna de custo.

---

## Autoteste

1. Quanto custa o plano Pro, mensal e anual, na data desta consulta?
2. Por que a Anthropic não publica cotas exatas de token, e qual é a sua
   única medida confiável?
3. Quais são os três descontos da API, e qual importa mais para agentes?
4. Por que um `datetime.now()` no prompt de sistema é um custo oculto?
5. Qual é o maior custo oculto de todos, e por que não aparece na planilha?
6. O Claude Code é aberto? E o MCP?
7. Qual parte do seu investimento em configuração é portátil, e qual não é?
8. Cite duas alternativas abertas e o que se perde em cada uma.
9. Assinatura ou API para um job de CI que roda 200 vezes por dia? Por quê?

---

**Fontes consultadas em 13/08/2026:**
[claude.com/pricing](https://claude.com/pricing);
documentação da Anthropic sobre modelos, preços de API, cache de prompt e
Batches; [Advanced setup](https://code.claude.com/docs/en/setup) e
[Costs](https://code.claude.com/docs/en/costs); páginas oficiais dos projetos
abertos citados.
