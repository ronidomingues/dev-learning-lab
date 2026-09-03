# 65 · Estado da arte

**Nível:** pesquisa · **Instantâneo de 13/08/2026**

⚠️ Este é o arquivo que envelhece mais rápido do curso. Tudo aqui tem data.
Confirme antes de citar.

---

## 1. Modelos

Modelos Claude atuais, com contexto e preço por milhão de tokens
(entrada/saída), conforme a documentação da Anthropic consultada em
13/08/2026:

| Modelo | ID | Contexto | US$ /Mtok |
|---|---|---|---|
| Claude Fable 5 | `claude-fable-5` | 1 M | 10 / 50 |
| Claude Opus 5 | `claude-opus-5` | 1 M | 5 / 25 |
| Claude Opus 4.8 | `claude-opus-4-8` | 1 M | 5 / 25 |
| Claude Sonnet 5 | `claude-sonnet-5` | 1 M | 3 / 15 (intro. 2/10 até 31/08/2026) |
| Claude Haiku 4.5 | `claude-haiku-4-5` | 200 K | 1 / 5 |

O que mudou na forma de usar, em relação a 2024–2025 — e isso importa mais que
os nomes:

| Antes | Agora |
|---|---|
| `thinking: {enabled, budget_tokens: N}` | `thinking: {type: "adaptive"}` + `effort` |
| `temperature` / `top_p` para controlar estilo | **removidos** nos modelos recentes; controle por prompt |
| prefill do turno do assistente | **removido**; use saída estruturada |
| pensar era opcional | é adaptativo, e o próprio modelo decide quanto |

**`effort` é o parâmetro que mais rende hoje.** Em tarefa agêntica, subir de
`high` para `xhigh` costuma render mais que trocar de modelo; em subagentes de
leitura, `low` corta custo sem perda perceptível. Faça uma varredura de
`effort` na sua avaliação antes de comparar modelos.

---

## 2. Números de benchmark, com as reservas

| Benchmark | Melhor reportado (ago/2026) |
|---|---|
| SWE-bench Verified | Fable 5 ≈ 95%; Opus 4.8 ≈ 88,6% |
| SWE-bench Pro | Fable 5 ≈ 80,3%; Opus 4.8 ≈ 69,2% |
| Terminal-Bench v2 | reportado por par agente+modelo; ver o placar oficial |

**As reservas, que são o ponto:**

1. Auditorias independentes encontram fração relevante de soluções
   semanticamente erradas entre as "resolvidas" — reportagens de ago/2026
   citam ordens de ~20% em alguns sistemas. Trate como teto, não como
   expectativa.
2. Números de fornecedor usam o arnês do fornecedor. O par importa tanto
   quanto o modelo.
3. Contaminação cresce com o tempo desde a publicação do conjunto.

> **Consenso na área em 2026:** SWE-bench Verified está saturando e deixou de
> discriminar bem no topo. O interesse migrou para SWE-bench Pro,
> Terminal-Bench e avaliações privadas por domínio.

---

## 3. O que está estabelecido

- **MCP é o padrão de integração.** Publicado pela Anthropic em nov/2024,
  adotado por OpenAI, Google DeepMind e Microsoft ao longo de 2025.
- **Agentes de código funcionam** em correção de bugs, migrações mecânicas,
  revisão e escrita de testes — em repositórios com boa cobertura.
- **A distinção workflow × agente** é vocabulário comum, e o conselho
  "comece simples" sobreviveu ao hype.
- **Verificação é o gargalo**, não capacidade do modelo.
- **Contexto longo é commodity.** 1 milhão de tokens virou padrão; o problema
  passou a ser *usar bem*, não *caber*.
- **Uso de ferramentas é capacidade treinada**, não engenharia de prompt.

## 4. O que está em disputa

| Debate | Lados |
|---|---|
| **Multiagente vale a pena?** | "isolamento de contexto e independência de julgamento são ganhos reais" × "a maioria é pipeline caro fantasiado" |
| **Autonomia longa é utilizável?** | sessões de horas funcionam em demo; em produção a maioria fatia e revisa |
| **Framework ou direto na API?** | LangGraph/CrewAI/AutoGen × "o laço tem 30 linhas, e o framework esconde onde dói" |
| **Benchmarks públicos medem algo?** | comparam fornecedores × não preveem seu resultado |
| **Modelo local é viável para agente?** | melhorou muito × ainda atrás em uso de ferramentas de cauda longa e em contexto |
| **Quanta especificação prescrever?** | roteiro passo a passo × objetivo e restrições; a evidência de 2026 favorece o segundo em tarefas de julgamento |

---

## 5. Fronteiras de pesquisa

**Segurança e injeção de prompt.** O problema em aberto mais consequente. Ver
[60 §5](60-teoria-avancada.md#5-injeção-de-prompt-como-problema-fundamental).
Linhas ativas: separação de canais por arquitetura, classificadores de
instrução em conteúdo, capacidades tipadas, e — a que mais funciona hoje —
menor privilégio estrutural.

**Avaliação honesta.** Como medir sem que o agente hackeie a métrica.
Auditoria de benchmark virou subárea (UTBoost, BenchJack e afins). A tendência
é medir a **trajetória**, não só o resultado.

**Memória.** Como um agente decide o que lembrar, o que esquecer e o que
consultar. Hoje: arquivos e heurística. As direções incluem memória
episódica, consolidação, e memória como recurso gerenciado em vez de arquivo.

**Aprendizado em uso.** O agente melhora com a experiência **naquele
repositório**? Skills escritas pelo próprio agente e memória de trajetórias
apontam nessa direção; ainda não há solução consolidada.

**Uso de computador.** Agentes que operam interface gráfica — para tudo que
não tem API. Melhorou muito com visão em alta resolução, e continua caro em
tokens e frágil a mudança de layout.

**Custo previsível.** A variância entre execuções da mesma tarefa é grande o
bastante para atrapalhar orçamento. Orçamentos de tarefa que o modelo enxerga
são um passo; previsibilidade real, não.

**Composição.** Como compor agentes com garantia de que o todo é melhor que a
parte. Hoje é empírico, caso a caso.

---

## 6. Sinais para vigiar nos próximos meses

1. **Benchmarks que medem trajetória** e não só resultado.
2. **Defesa de injeção que não seja "menor privilégio"** — seria uma mudança
   de patamar.
3. **Custo por tarefa caindo** mais rápido que capacidade subindo.
4. **Padronização de avaliação** (o equivalente ao MCP, mas para medir).
5. **Modelos abertos** fechando a distância em uso de ferramentas.
6. **Regulação** com exigência de auditoria de ações de agente.

---

## 7. Como não se enganar

- **Demo ≠ produto.** Toda demo é o melhor caso de N tentativas.
- **Benchmark ≠ seu repositório.**
- **Sem arnês, o número não significa nada.**
- **Custo é a métrica esquecida.** Pergunte sempre "quanto custou por tarefa?"
- **"Autônomo" quase sempre quer dizer "com humano no laço em algum ponto".**
  Pergunte onde.
- **Se ninguém mostra a taxa de falha, ela existe.**

---

## Autoteste

1. Qual parâmetro rende mais hoje em tarefa agêntica, e como você mediria isso?
2. Cite três reservas ao ler "88% no SWE-bench Verified".
3. Liste três coisas estabelecidas e três em disputa.
4. Por que injeção de prompt é a fronteira mais consequente?
5. O que mudaria se aparecesse uma defesa contra injeção que não fosse menor
   privilégio?
6. Por que "contexto longo é commodity" mudou a natureza do problema?
7. Um fornecedor anuncia 92% num benchmark. Quais cinco perguntas você faz?

---

**Fontes consultadas em 13/08/2026:** documentação da Anthropic (modelos,
preços, parâmetros de `thinking`/`effort`); placares e análises públicas de
SWE-bench Verified, SWE-bench Pro e Terminal-Bench v2 recolhidos por busca na
web em 13/08/2026 (ver [95-referencias.md](95-referencias.md)); artigos de
auditoria de benchmark (UTBoost, arXiv 2506.09289; BenchJack, arXiv
2605.12673).
