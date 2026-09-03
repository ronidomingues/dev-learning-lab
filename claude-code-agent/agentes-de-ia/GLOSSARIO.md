# Glossário

Todos os termos técnicos usados no curso. Termos em inglês aparecem como o
campo os usa, com a tradução. Ordem alfabética pelo termo em português quando
existe uso corrente.

---

**ACI (Agent–Computer Interface)** — a interface entre o agente e o computador:
o conjunto de ferramentas, os formatos de entrada e saída, as mensagens de
erro. Tese do SWE-agent (2024): com o modelo fixo, melhorar a ACI melhora o
desempenho de forma drástica. → [13](13-ferramentas-e-tool-use.md)

**Agente** — sistema em que um LLM decide, a cada passo, qual ação tomar,
executa por meio de ferramentas, observa o resultado e repete até concluir.
→ [10](10-fundamentos.md)

**Agent view** — painel do Claude Code (`claude agents`) que mostra todas as
sessões em segundo plano. → [16](16-subagentes-e-orquestracao.md)

**Alucinação** — saída plausível e falsa. Em agentes, a forma mais perigosa é
alegar ter feito algo que não fez ("falha silenciosa").

**Arnês (harness)** — o programa que embrulha o modelo: mantém histórico,
oferece ferramentas, executa pedidos, gerencia contexto, aplica permissões. O
Claude Code é um arnês. → [10](10-fundamentos.md)

**Atribuição de crédito (credit assignment)** — determinar qual passo de uma
trajetória causou o resultado. Difícil quando a recompensa é esparsa.
→ [60](60-teoria-avancada.md)

**Auto memory (memória automática)** — aprendizados que o Claude Code salva
sozinho entre sessões, indexados em `MEMORY.md`.
→ [14](14-contexto-memoria-compactacao.md)

**BDI (Belief–Desire–Intention)** — arquitetura clássica de agentes (crença,
desejo, intenção), anos 1980–90. Origem do vocabulário. → [11](11-historia.md)

**Cache de prompt** — reuso do prefixo repetido entre chamadas, cobrado a ~10%.
Depende de casamento **exato** do prefixo. → [14](14-contexto-memoria-compactacao.md)

**Checkpoint** — snapshot dos arquivos antes de uma edição, para desfazer
(`Esc Esc`, `/rewind`). Separado do git. → [04](04-como-comecar.md)

**`CLAUDE.md`** — arquivo de instruções do projeto, carregado em **toda**
sessão. → [14](14-contexto-memoria-compactacao.md)

**Compactação (compaction)** — resumir a conversa para liberar contexto. Perde
detalhe; por isso regras críticas vão para arquivo.
→ [14](14-contexto-memoria-compactacao.md)

**Composição de erro** — a probabilidade de uma trajetória de *n* passos estar
inteiramente correta cai como *pⁿ*, na ausência de recuperação.
→ [60](60-teoria-avancada.md)

**Contexto (context window)** — o texto que o modelo enxerga numa chamada.
Finito. 1 milhão de tokens nos modelos Claude atuais.

**Edição de contexto (context editing)** — **remover** resultados antigos de
ferramenta e blocos de pensamento do histórico. Diferente de compactar, que
**resume**. → [19](19-agent-sdk-e-agentes-proprios.md)

**Effort (esforço)** — parâmetro que controla profundidade de raciocínio e
gasto de tokens: `low`, `medium`, `high`, `xhigh`, `max`. Costuma render mais
que trocar de modelo. → [65](65-estado-da-arte.md)

**Falha silenciosa** — o agente relata sucesso e o trabalho não está feito. A
métrica mais subestimada da avaliação. → [20](20-avaliacao-e-benchmarks.md)

**Ferramenta (tool)** — função que você descreve ao modelo (nome, descrição,
esquema). O modelo **pede**; quem executa é o arnês.
→ [13](13-ferramentas-e-tool-use.md)

**Function calling / tool use** — a capacidade do modelo de emitir um pedido de
ferramenta estruturado e validado. Marco de 2023. → [11](11-historia.md)

**GAIA** — benchmark de assistente geral: raciocínio multi-passo com
ferramentas e web. → [20](20-avaliacao-e-benchmarks.md)

**Hook** — comando executado pelo Claude Code em pontos do ciclo de vida
(antes/depois de ferramenta, início/fim de sessão…). Determinístico: acontece
sempre. → [17](17-hooks-permissoes-seguranca.md)

**Injeção de prompt (prompt injection)** — conteúdo lido pelo agente contém
instruções que ele obedece. Problema em aberto, sem análogo ao escape de SQL.
→ [17](17-hooks-permissoes-seguranca.md), [60](60-teoria-avancada.md)

**`is_error`** — campo do `tool_result` que marca falha **como conteúdo**, para
o modelo ler e se corrigir, em vez de derrubar o laço.
→ [12](12-anatomia-do-loop-agentico.md)

**Laço agêntico (agentic loop)** — chamar o modelo → executar ferramentas →
devolver resultados → repetir, enquanto `stop_reason == "tool_use"`.
→ [12](12-anatomia-do-loop-agentico.md)

**LLM (Large Language Model)** — modelo de linguagem de grande porte. Função de
texto para texto, sem estado, sem execução.

**`lost in the middle`** — degradação da recuperação de informação posicionada
no meio de contextos longos. → [60](60-teoria-avancada.md)

**MCP (Model Context Protocol)** — protocolo aberto (JSON-RPC 2.0) para ligar
modelos a ferramentas e dados. Publicado pela Anthropic em nov/2024.
→ [15](15-mcp-model-context-protocol.md)

**Managed Agents** — serviço da Anthropic em que a própria Anthropic roda o
laço **e** hospeda o contêiner de execução.
→ [19](19-agent-sdk-e-agentes-proprios.md)

**Modo de permissão** — `default`/`manual`, `acceptEdits`, `plan`, `auto`,
`dontAsk`, `bypassPermissions`. `Shift+Tab` alterna.
→ [17](17-hooks-permissoes-seguranca.md)

**No Free Lunch** — teorema (1997): promediado sobre todos os problemas, todos
os algoritmos empatam. Desempenho vem de viés adequado ao domínio.
→ [60](60-teoria-avancada.md)

**`pause_turn`** — `stop_reason` que indica que uma ferramenta do servidor
atingiu o limite de iterações. Reenvie a conversa para continuar.
→ [12](12-anatomia-do-loop-agentico.md)

**Pensamento adaptativo (adaptive thinking)** — o modelo decide sozinho quanto
raciocinar. Substitui o antigo `budget_tokens`, removido nos modelos atuais.
→ [12](12-anatomia-do-loop-agentico.md)

**Plan mode** — modo em que o agente explora e propõe sem editar nada.
`Shift+Tab` duas vezes. → [04](04-como-comecar.md)

**Plugin** — pacote instalável com skills, subagentes, hooks e servidores MCP,
distribuído por marketplace. → [18](18-skills-plugins-extensibilidade.md)

**POMDP** — Processo de Decisão de Markov Parcialmente Observável. O
enquadramento formal de um agente: ele nunca vê o estado real, só observações.
→ [60](60-teoria-avancada.md)

**PTC (programmatic tool calling)** — o modelo escreve um script que chama as
ferramentas; os resultados intermediários ficam no código, fora do contexto.
→ [13](13-ferramentas-e-tool-use.md)

**ReAct** — *Reasoning + Acting* (Yao et al., 2022). O paper que estabeleceu o
laço pensamento → ação → observação. → [11](11-historia.md)

**Recompensa hackeada (reward hacking)** — satisfazer a métrica sem resolver o
problema (desabilitar o teste, aumentar o timeout).
→ [20](20-avaliacao-e-benchmarks.md)

**Rice, teorema de** — toda propriedade semântica não trivial de programas é
indecidível. Logo, não existe verificador geral de correção.
→ [60](60-teoria-avancada.md)

**Sandbox** — ambiente isolado onde comandos do agente rodam sem alcançar o
resto do sistema. → [17](17-hooks-permissoes-seguranca.md)

**Sessão** — uma conversa com contexto próprio, persistida localmente em
`~/.claude/projects/`. → [05](05-manual-de-uso.md)

**Skill** — procedimento em Markdown carregado **sob demanda**; só a
`description` ocupa contexto até ser invocada.
→ [18](18-skills-plugins-extensibilidade.md)

**`stop_reason`** — por que o modelo parou: `end_turn`, `tool_use`,
`max_tokens`, `refusal`, `pause_turn`, `stop_sequence`. O laço é um `while
stop_reason == "tool_use"`. → [12](12-anatomia-do-loop-agentico.md)

**Subagente** — trabalhador com **contexto próprio**, criado dentro de uma
sessão, que devolve um resumo. Uso principal: isolar contexto.
→ [16](16-subagentes-e-orquestracao.md)

**SWE-bench** — benchmark de 2 294 issues reais do GitHub; o critério é os
testes do projeto passarem. `Verified` é o subconjunto de 500 validado por
humanos. → [20](20-avaliacao-e-benchmarks.md)

**Task budget (orçamento de tarefa)** — teto de tokens que o modelo **enxerga**
e usa para se organizar. Diferente de `max_tokens`, que é imposto e invisível
a ele. → [12](12-anatomia-do-loop-agentico.md)

**Terminal-Bench** — benchmark de tarefas de terminal ponta a ponta; mede o par
agente + modelo. → [20](20-avaliacao-e-benchmarks.md)

**Token** — unidade de fatiamento e cobrança do texto. Saída custa ~5× a
entrada.

**Tool runner** — utilitário do SDK da Claude API que roda o laço por você a
partir das suas funções. **Não confundir** com o Claude Agent SDK.
→ [19](19-agent-sdk-e-agentes-proprios.md)

**Tool search** — carregamento adiado de esquemas de ferramenta: só os nomes
ocupam contexto até o modelo precisar de uma.
→ [15](15-mcp-model-context-protocol.md)

**Trajetória** — a sequência de ações e observações de uma execução. O objeto
que se avalia num agente — não a resposta final.
→ [20](20-avaliacao-e-benchmarks.md)

**Turno (turn)** — uma iteração do laço: chamada ao modelo + ferramentas +
resultados.

**Verificação** — o sinal que diz ao agente se ele acertou (teste, compilador,
saída esperada). O gargalo de tudo. → [10](10-fundamentos.md)

**Workflow** — sistema em que **você** escreve o fluxo de controle e o LLM
preenche os passos. Previsível, barato, fácil de depurar. A maioria dos
problemas quer isto. → [10](10-fundamentos.md)

**Workflow dinâmico** — no Claude Code, um script que orquestra muitos
subagentes e cruza resultados. → [16](16-subagentes-e-orquestracao.md)

**Worktree** — checkout git adicional em outro diretório, para sessões
paralelas não se atropelarem. → [16](16-subagentes-e-orquestracao.md)

**ZDR (Zero Data Retention)** — retenção zero de dados, disponível para contas
Enterprise qualificadas. → [80](80-custos-e-licencas.md)
