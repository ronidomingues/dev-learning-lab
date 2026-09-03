# 80 · Custos e licenças

**Nível:** intermediário
**Preços consultados em: 20/08/2026.** Câmbio usado: **US$ 1 = R$ 5,19**
(USD/BRL em 20/08/2026; faixa do mês: 5,05–5,25).

> **Preço sem data é desinformação.** Tudo aqui envelhece. Confira na fonte
> antes de decidir, especialmente porque o modelo de cobrança mudou em 2026.

> **Para brasileiros:** os valores em reais abaixo são a conversão direta. **A
> sua fatura será maior**: some IOF sobre compra internacional e o *spread*
> cambial do emissor do cartão (tipicamente 4% a 6% acima da cotação comercial,
> somando tudo). Multiplique por ~1,10 para uma estimativa realista de fatura.

---

## 1 · Roteiro do gratuito — comece sem gastar

| Serviço | O que dá | Limite | Cartão? |
|---|---|---|---|
| **GitHub Copilot Free** | Completar + chat/agente limitados | **2.000 completions/mês** | Não |
| **Gemini CLI** | Agente de terminal, código aberto | Camada gratuita com login Google | Não |
| **Claude Free** | Chat, geração de código, busca web | Limite diário baixo. **Não inclui Claude Code** | Não |
| **GitHub Codespaces** | Máquina Linux + VS Code no navegador | 60 h/mês, 15 GB | Não |
| **Google Cloud Shell** | Máquina Linux com editor | 50 h/semana | Não |
| **GitHub Student Pack** | Copilot Pro grátis | Enquanto matriculado | Não |

**Combinação para custo zero:** Codespaces + Copilot Free + Gemini CLI. Dá para
fazer o curso inteiro, inclusive os laboratórios.

**Onde o gratuito acaba:** trabalho agêntico sério. 2.000 *completions* somem em
uma semana de uso normal; camadas gratuitas de agente têm limite de requisição
por hora que você atinge numa tarefa média. O gratuito serve para **aprender**,
não para trabalhar.

---

## 2 · Assinaturas — preços de 20/08/2026

### Claude (Anthropic)

| Plano | Mensal | Anual (por mês) | Em R$/mês (mensal) | Claude Code? |
|---|---|---|---|---|
| Free | US$ 0 | — | R$ 0 | **Não** |
| Pro | US$ 20 | US$ 17 | ~R$ 104 | Sim |
| Max 5× | a partir de US$ 100 | — | ~R$ 519 | Sim |
| Max 20× | superior | — | — | Sim |
| Team (padrão) | US$ 25/assento | US$ 20/assento | ~R$ 130 | Sim |
| Team (premium) | US$ 125/assento | US$ 100/assento | ~R$ 649 | Sim |
| Enterprise | US$ 20/assento + uso a preço de API | — | — | Sim |

> **Atenção:** o plano **Free do Claude.ai não inclui o Claude Code.** É o erro
> de expectativa mais comum. O Claude Code exige Pro, Max, Team, Enterprise ou
> conta de Console (API).

### GitHub Copilot

**Mudança estrutural em 2026:** desde **01/06/2026** a cobrança é baseada em uso,
com créditos de IA (**1 crédito = US$ 0,01**). *Completions* são ilimitadas nos
planos pagos; chat e agente consomem créditos.

| Plano | Mensal | Em R$/mês | Créditos incluídos | Observação |
|---|---|---|---|---|
| Free | US$ 0 | R$ 0 | — | 2.000 completions/mês; chat e agente limitados |
| Pro | US$ 10 | ~R$ 52 | **US$ 15** em créditos | Completions ilimitadas |
| Pro+ | US$ 39 | ~R$ 202 | **US$ 70** em créditos | Modelos premium (inclui Opus); 4×+ o uso do Pro |
| Max | US$ 100 | ~R$ 519 | **US$ 200** em créditos | 2,9×+ o uso do Pro+ |

Repare: o Pro dá US$ 15 de crédito por US$ 10 — a assinatura é mais barata que
o crédito que inclui, e a conta fecha porque a maioria não consome tudo.

### Cursor

| Plano | Mensal | Em R$/mês | Observação |
|---|---|---|---|
| Hobby | US$ 0 | R$ 0 | Requisições de agente limitadas |
| Pro | US$ 20 | ~R$ 104 | Limites estendidos de agente |
| Pro+ | US$ 60 | ~R$ 311 | 3× os limites do Pro |
| Ultra | US$ 200 | ~R$ 1.038 | 20× os limites do Pro |
| Teams | US$ 40/usuário | ~R$ 208 | Bugbot, SSO, análises |
| Teams Premium | — | — | 5× os limites do padrão |

> A **própria documentação do Cursor** indica que usuários diários de agente
> ficam mais perto de **US$ 60–100/mês** que dos US$ 20 do plano base. Se você
> orçou US$ 20 e usa agente todo dia, o seu orçamento está errado.

---

## 3 · API — preço por token (Claude, 20/08/2026)

Por **milhão de tokens** (MTok). Valores da documentação oficial.

| Modelo | Entrada | Escrita cache 5 min | Escrita cache 1 h | **Leitura de cache** | Saída |
|---|---|---|---|---|---|
| Claude Fable 5 | US$ 10 | US$ 12,50 | US$ 20 | US$ 1 | US$ 50 |
| Claude Opus 5 / 4.8 / 4.7 / 4.6 / 4.5 | US$ 5 | US$ 6,25 | US$ 10 | US$ 0,50 | US$ 25 |
| **Claude Sonnet 5** | **US$ 2** | US$ 2,50 | US$ 4 | US$ 0,20 | **US$ 10** |
| Claude Sonnet 4.6 / 4.5 | US$ 3 | US$ 3,75 | US$ 6 | US$ 0,30 | US$ 15 |
| Claude Haiku 4.5 | US$ 1 | US$ 1,25 | US$ 2 | US$ 0,10 | US$ 5 |

**Descontos e multiplicadores:**

| Mecanismo | Efeito |
|---|---|
| **Leitura de cache** | **0,1×** o preço de entrada — a maior economia disponível |
| **Batch API** | **−50%** em entrada e saída (assíncrono) |
| Residência de dados US (`inference_geo: "us"`) | **1,1×** em tudo (modelos 4.6+) |
| Fast mode (Opus 5 / 4.8) | US$ 10 entrada / US$ 50 saída |
| Janela de 1 M tokens | Preço padrão em modelos 4.6+ (sem sobretaxa) |
| Busca web | US$ 10 por 1.000 buscas |
| Execução de código | 1.550 h grátis/mês, depois US$ 0,05/h por container |

> **Nota de 2026 que confunde a conta:** os modelos Claude 4.7 e posteriores
> usam um tokenizador novo que produz **~30% mais tokens** para o mesmo texto.
> Ao trocar de geração, recalibre a linha de base de custo antes de concluir que
> algo ficou mais caro.

---

## 4 · Quanto custa de verdade

### Uma tarefa típica de agente

Trabalho de meia hora, ~15 idas e voltas, contexto médio de 60 mil tokens de
entrada por passo (com cache) e 3 mil de saída por passo.

| Modelo | Estimativa |
|---|---|
| Haiku 4.5 | ~US$ 0,30 (~R$ 1,60) |
| Sonnet 5 | ~US$ 0,70 (~R$ 3,60) |
| Opus 5 | ~US$ 1,80 (~R$ 9,30) |

**Compare com o seu custo:** meia hora de um dev sênior no Brasil custa
tipicamente entre R$ 60 e R$ 120 (custo total para a empresa). Mesmo o modelo
mais caro sai **entre 6 e 13 vezes mais barato** que o tempo que ele economiza —
**se** economizar.

> **Este é o ponto que mais gente erra ao gerir custo de IA:** o denominador não
> é o orçamento de ferramentas, é o custo da hora de engenharia. Economizar
> US$ 1 de API gastando 10 minutos a mais é prejuízo.

### Um mês de uso intenso, por perfil

| Perfil | Estimativa mensal |
|---|---|
| Aprendendo (algumas horas por semana) | US$ 0–20 (R$ 0–104) |
| Uso diário, modo 3 (editar) | US$ 20–60 (R$ 104–311) |
| Uso diário, modo 4 (agente) | US$ 60–200 (R$ 311–1.038) |
| Uso intenso, vários agentes | US$ 200–600 (R$ 1.038–3.114) |
| Time de 10 pessoas | US$ 1.500–4.000 (R$ 7.785–20.760) |

O time de 10 pessoas gasta **menos de 5% do custo do time**. Isso significa que
otimizar gasto de IA raramente é o problema certo.

### Onde o dinheiro escapa

| Vazamento | Correção |
|---|---|
| Sessões longas sem `/clear` | Entrada reenviada a cada passo, cara |
| Cache invalidado por editar `AGENTS.md` no meio | Estabilize o prefixo |
| Modelo caro para tarefa mecânica | `/model` para a classe adequada |
| Agente em laço improdutivo | Interrompa na segunda tentativa sem progresso |
| Colar arquivos "por garantia" | Deixe ele buscar |
| Pedir arquivo inteiro reescrito | Peça o diff |
| Agente sem limite de passos em CI | Sempre `timeout-minutes` |

---

## 5 · Custos ocultos

| Custo | Ordem de grandeza | Comentário |
|---|---|---|
| **IOF + spread cambial** | +8% a +10% sobre o preço | Real e recorrente para quem paga do Brasil |
| **Revisão adicional** | Tempo de engenharia | +91% de tempo de revisão em times com adoção intensa. **É o maior custo oculto e ninguém o contabiliza** |
| **Retrabalho** | Tempo | Só 32,7% do código de IA passa sem modificação |
| **Dívida estrutural** | Anos | Duplicação +81% desde 2023; a conta vem na manutenção |
| **Formação** | Semanas por pessoa | 2–4 meses até L3 |
| **Aprisionamento em ferramenta** | Migração | `AGENTS.md` é portátil; fluxo proprietário de SDD não é |
| **Conformidade** | Jurídico | Revisão de contrato, DPA, política |
| **Incidente de segurança** | Imprevisível | Ver [22](22-seguranca.md) |

> **A segunda linha merece ênfase.** Se a sua equipe gasta US$ 2.000/mês em IA e
> 30 horas a mais por mês em revisão, o custo real da revisão (≈ R$ 3.000) é
> maior que o da ferramenta. Contabilizar só a assinatura é enganar a si mesmo.

---

## 6 · Licenças das ferramentas

| Ferramenta | Licença | O que permite |
|---|---|---|
| **Gemini CLI** | Apache 2.0 | Uso comercial, modificação, redistribuição |
| **Aider** | Apache 2.0 | Idem |
| **OpenAI Codex CLI** | Aberta (ver repositório) | Cliente aberto; o modelo é serviço pago |
| **Claude Code** | Proprietária | Uso conforme os termos; exige assinatura |
| **GitHub Copilot** | Proprietária | Idem |
| **Cursor / Windsurf** | Proprietária (fork de VS Code, MIT) | O editor deriva de código MIT; as partes de IA são proprietárias |
| **GitHub Spec Kit** | Aberta | Templates e CLI |
| **AGENTS.md** | Especificação aberta | Agentic AI Foundation / Linux Foundation |
| **`portao`** (deste curso) | Livre para uso | Zero dependências |

**A distinção que importa:** o **cliente** aberto não torna o **modelo** aberto.
Gemini CLI e Aider são Apache 2.0 e continuam falando com um serviço pago e
proprietário. O que você ganha com o cliente aberto é: auditar o que ele envia,
trocar de provedor, e não depender de uma empresa para o seu fluxo de trabalho.

---

## 7 · Modelos abertos e execução local

### Quando faz sentido

| Situação | Vale? |
|---|---|
| Dado que **não pode** sair da rede (defesa, saúde, jurídico sob sigilo) | **Sim.** É o caso legítimo |
| Volume altíssimo e previsível de tarefa simples | Talvez, com hardware amortizado |
| "Economizar" | **Não.** Some hardware, energia e o seu tempo |
| Trabalho agêntico de ponta | **Não** em hardware de consumo, em 08/2026 |

### O custo real de rodar local

| Item | Ordem de grandeza |
|---|---|
| GPU capaz de modelo grande | R$ 15.000 – R$ 60.000+ |
| Energia | R$ 100 – 400/mês em uso contínuo |
| Tempo de engenharia (montar, atualizar, servir) | Semanas |
| Qualidade | Abaixo dos modelos de ponta em trabalho agêntico |

**Ponto de equilíbrio:** com US$ 200/mês (~R$ 1.038) de API, uma GPU de
R$ 30.000 leva **quase 30 meses** para se pagar — sem contar energia, tempo e a
perda de qualidade. E, nesses 30 meses, os modelos de nuvem terão avançado
várias gerações.

**Conclusão honesta:** rode local por **privacidade**, não por economia.

---

## 8 · Como decidir

```
Você está aprendendo?
  └── Sim → Copilot Free + Gemini CLI + Codespaces. Custo R$ 0.

Você usa todo dia, profissionalmente?
  ├── Prefere IDE → Cursor Pro (US$ 20) e observe: pode virar US$ 60–100
  ├── Prefere terminal → Claude Pro (US$ 20) ou Max (US$ 100) se bater no limite
  └── Já tem GitHub → Copilot Pro (US$ 10) é o melhor custo-benefício de entrada

Você delega tarefas longas várias vezes ao dia?
  └── Max / Ultra (US$ 100–200). Teto de gasto previsível.

Você constrói produto com modelos?
  └── API direta, com cache e Batch. Ver agentes-de-ia/ e engenharia-de-prompt/.

Dado não pode sair da rede?
  └── Modelo local ou nuvem privada. Aceite a perda de qualidade.
```

**Recomendação para quem está começando, e é opinião:** comece com **Copilot
Free** por duas semanas. Depois assine **um** plano de US$ 20 da ferramenta que
você mais usou. Não assine três. Aprender uma ferramenta bem rende mais que
experimentar cinco.

---

## Fontes consultadas — 20/08/2026

- https://claude.com/pricing
- https://platform.claude.com/docs/en/about-claude/pricing
- https://github.com/features/copilot/plans
- https://cursor.com/pricing
- Câmbio USD/BRL: br.investing.com/currencies/usd-brl (20/08/2026)
- LinearB 2026 Benchmarks (tempo de revisão, taxa de aceitação)
- GitClear 2026 (duplicação)

---

## Autoteste

1. Qual é a combinação de custo zero para fazer o curso inteiro? Onde ela acaba?
2. Por que o plano Free do Claude.ai frustra quem quer usar Claude Code?
3. O que mudou na cobrança do GitHub Copilot em 01/06/2026?
4. Quanto custa a leitura de cache em relação ao preço de entrada? Como
   conseguir acerto de cache?
5. Uma tarefa de meia hora com Opus custa ~R$ 9,30. Por que isso é barato, e
   qual é o denominador correto da conta?
6. Cite quatro lugares por onde o dinheiro escapa.
7. Qual é o maior custo oculto e por que ninguém o contabiliza?
8. Cliente open source significa modelo open source? O que você ganha com o
   cliente aberto?
9. Faça a conta do ponto de equilíbrio de rodar modelo local. Qual é a conclusão
   honesta?
10. Quanto some ao preço em dólar para estimar a fatura de um cartão brasileiro?

---

**Anterior:** [75-armadilhas](75-armadilhas.md) ·
**Próximo:** [85-cursos-e-certificacoes](85-cursos-e-certificacoes.md)
