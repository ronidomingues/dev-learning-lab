# 95 · Referências

**Verificado em 13/08/2026.** Todos os links foram alcançados na data. Nada
aqui foi inventado; onde não tenho certeza de um dado, ele está marcado.

---

## 1. Documentação oficial

### Claude Code — [code.claude.com/docs](https://code.claude.com/docs/)

| Página | Assunto | Usada em |
|---|---|---|
| [Overview](https://code.claude.com/docs/en/overview) | o que é | 01 |
| [How Claude Code works](https://code.claude.com/docs/en/how-claude-code-works) | laço agêntico, ferramentas, sessões | 10, 12 |
| [Advanced setup](https://code.claude.com/docs/en/setup) | instalação por SO, canais, desinstalação | 03 |
| [Troubleshoot installation](https://code.claude.com/docs/en/troubleshoot-install) | erros literais | 03 |
| [Authentication](https://code.claude.com/docs/en/authentication) | login, tokens | 03 |
| [Network configuration](https://code.claude.com/docs/en/network-config) | proxy, CA, mTLS | 03 |
| [Commands](https://code.claude.com/docs/en/commands) | **todos os comandos de barra** | 05 |
| [CLI reference](https://code.claude.com/docs/en/cli-reference) | comandos e flags do terminal | 05 |
| [Interactive mode](https://code.claude.com/docs/en/interactive-mode) | atalhos, prefixos | 05 |
| [Tools reference](https://code.claude.com/docs/en/tools-reference) | ferramentas embutidas | 13 |
| [Memory](https://code.claude.com/docs/en/memory) | `CLAUDE.md`, memória automática | 14 |
| [Explore the context window](https://code.claude.com/docs/en/context-window) | o que carrega e quando | 14 |
| [Prompt caching](https://code.claude.com/docs/en/prompt-caching) | cache no Claude Code | 14 |
| [MCP](https://code.claude.com/docs/en/mcp) · [MCP quickstart](https://code.claude.com/docs/en/mcp-quickstart) | servidores, escopos, tool search | 15 |
| [Sub-agents](https://code.claude.com/docs/en/sub-agents) | frontmatter, escopos | 16 |
| [Run agents in parallel](https://code.claude.com/docs/en/agents) | os quatro mecanismos | 16 |
| [Workflows](https://code.claude.com/docs/en/workflows) | workflows dinâmicos | 16 |
| [Worktrees](https://code.claude.com/docs/en/worktrees) | isolamento git | 16 |
| [Permissions](https://code.claude.com/docs/en/permissions) · [Permission modes](https://code.claude.com/docs/en/permission-modes) | regras e modos | 17 |
| [Hooks reference](https://code.claude.com/docs/en/hooks) · [Hooks guide](https://code.claude.com/docs/en/hooks-guide) | eventos, códigos de saída | 17 |
| [Sandboxing](https://code.claude.com/docs/en/sandboxing) · [Sandbox environments](https://code.claude.com/docs/en/sandbox-environments) | isolamento | 17 |
| [Security](https://code.claude.com/docs/en/security) | modelo de ameaça | 17 |
| [Skills](https://code.claude.com/docs/en/skills) | skills e comandos | 18 |
| [Plugins](https://code.claude.com/docs/en/plugins) · [Plugin marketplaces](https://code.claude.com/docs/en/plugin-marketplaces) | distribuição | 18 |
| [Headless](https://code.claude.com/docs/en/headless) | `-p`, automação | 06, 19 |
| [Agent SDK overview](https://code.claude.com/docs/en/agent-sdk/overview) | construir agentes | 19 |
| [Model configuration](https://code.claude.com/docs/en/model-config) | modelo, `effort`, auto-compact | 05, 65 |
| [Costs](https://code.claude.com/docs/en/costs) | rastrear e reduzir | 80 |
| [GitHub Actions](https://code.claude.com/docs/en/github-actions) | CI | 06 |
| [Glossary](https://code.claude.com/docs/en/glossary) | terminologia oficial | GLOSSARIO |
| [Changelog](https://code.claude.com/docs/en/changelog) | o que mudou | todos |

### Claude API — [platform.claude.com/docs](https://platform.claude.com/docs/)

Modelos e preços · Tool use · Adaptive thinking e `effort` · Structured
outputs · Prompt caching · Batches · Files API · Code execution · Memory tool ·
Tool search · Programmatic tool calling · MCP connector.

### MCP — [modelcontextprotocol.io](https://modelcontextprotocol.io/)

Especificação, SDKs oficiais (Python, TypeScript, e outros) e servidores de
referência: [github.com/modelcontextprotocol](https://github.com/modelcontextprotocol).

---

## 2. Artigos de engenharia da Anthropic

| Artigo | Data | Por que importa |
|---|---|---|
| [Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents) | dez/2024 | **A leitura fundamental.** Workflow × agente, cinco padrões, quando não construir |
| [Introducing the Model Context Protocol](https://www.anthropic.com/news/model-context-protocol) | nov/2024 | anúncio e motivação do MCP |
| [Claude Code best practices](https://code.claude.com/docs/en/best-practices) | contínuo | práticas do fabricante |

---

## 3. Papers

Em ordem cronológica. Os oito primeiros são os que eu leria, nesta ordem.

| Ano | Paper | arXiv | Por quê |
|---|---|---|---|
| 2017 | *Attention Is All You Need* | [1706.03762](https://arxiv.org/abs/1706.03762) | a arquitetura |
| 2022 | *Chain-of-Thought Prompting* (Wei et al.) | [2201.11903](https://arxiv.org/abs/2201.11903) | raciocínio explícito |
| 2022 | *MRKL Systems* (Karpas et al., AI21) | [2205.00445](https://arxiv.org/abs/2205.00445) | LLM + módulos externos |
| **2022** | ***ReAct*** (Yao et al.) | [2210.03629](https://arxiv.org/abs/2210.03629) | **o laço agêntico** |
| 2023 | *Toolformer* (Schick et al., Meta) | [2302.04761](https://arxiv.org/abs/2302.04761) | uso de ferramenta aprendido |
| 2023 | *Reflexion* (Shinn et al.) | [2303.11366](https://arxiv.org/abs/2303.11366) | aprender com a própria falha |
| 2023 | *Tree of Thoughts* (Yao et al.) | [2305.10601](https://arxiv.org/abs/2305.10601) | busca no espaço de raciocínio |
| 2023 | *Voyager* (Wang et al., NVIDIA) | [2305.16291](https://arxiv.org/abs/2305.16291) | verificação pelo ambiente, biblioteca de skills |
| 2023 | *Lost in the Middle* (Liu et al.) | [2307.03172](https://arxiv.org/abs/2307.03172) | limite de contexto longo |
| **2023** | ***SWE-bench*** (Jimenez et al.) | [2310.06770](https://arxiv.org/abs/2310.06770) | **como se mede** |
| 2024 | *SWE-agent* (Yang et al.) | [2405.15793](https://arxiv.org/abs/2405.15793) | **a tese da ACI** |
| 2024 | *OpenHands / OpenDevin* (Wang et al.) | [2407.16741](https://arxiv.org/abs/2407.16741) | plataforma aberta |
| 2024 | *AgentBench* (Liu et al.) | [2308.03688](https://arxiv.org/abs/2308.03688) | avaliação multi-ambiente |
| 2023 | *WebArena* (Zhou et al.) | [2307.13854](https://arxiv.org/abs/2307.13854) | agentes em ambiente web realista |
| 2023 | *GAIA* (Mialon et al.) | [2311.12983](https://arxiv.org/abs/2311.12983) | assistente geral |
| 2026 | *UTBoost: Rigorous Evaluation of Coding Agents on SWE-Bench* | [2506.09289](https://arxiv.org/pdf/2506.09289) | auditoria: soluções que passam por motivo errado |
| 2026 | *Holistic Agent Leaderboard* | [2510.11977](https://arxiv.org/pdf/2510.11977) | infraestrutura de avaliação |
| 2026 | *BenchJack* — auditoria de benchmarks de agente | [2605.12673](https://arxiv.org/pdf/2605.12673) | atalhos exploráveis em benchmarks |

**Clássicos fora de arXiv:**

- Turing, A. (1936). *On Computable Numbers…* — indecidibilidade da parada.
- Rice, H. G. (1953). *Classes of recursively enumerable sets and their
  decision problems* — propriedades semânticas são indecidíveis.
- Kaelbling, L., Littman, M. & Cassandra, A. (1998). *Planning and acting in
  partially observable stochastic domains*. **Artificial Intelligence**, 101.
- Wolpert, D. & Macready, W. (1997). *No Free Lunch Theorems for
  Optimization*. **IEEE Trans. Evolutionary Computation**, 1(1).
- Rao, A. & Georgeff, M. (1995). *BDI agents: from theory to practice*.

---

## 4. Código-fonte para ler

| Projeto | Licença | O que se aprende |
|---|---|---|
| [smolagents](https://github.com/huggingface/smolagents) | Apache 2.0 | o laço, mínimo e legível — **comece por aqui** |
| [Aider](https://github.com/Aider-AI/aider) | Apache 2.0 | edição de código, mapa de repositório |
| [OpenHands](https://github.com/All-Hands-AI/OpenHands) | MIT | plataforma completa com sandbox |
| [SWE-agent](https://github.com/SWE-agent/SWE-agent) | MIT | a ACI na prática |
| [Cline](https://github.com/cline/cline) | Apache 2.0 | agente dentro de IDE |
| [Goose](https://github.com/block/goose) | Apache 2.0 | MCP nativo |
| [servidores MCP de referência](https://github.com/modelcontextprotocol/servers) | MIT | como escrever um servidor |

---

## 5. Benchmarks e placares

| Benchmark | Onde |
|---|---|
| SWE-bench (e Verified, Pro, Multimodal) | [swebench.com](https://www.swebench.com/) |
| Terminal-Bench | [tbench.ai](https://www.tbench.ai/) |
| GAIA | Hugging Face |
| WebArena | [webarena.dev](https://webarena.dev/) |
| OSWorld | [os-world.github.io](https://os-world.github.io/) |

---

## 6. Pessoas e canais para acompanhar

| Quem | Onde | O quê |
|---|---|---|
| Anthropic Engineering | [anthropic.com/engineering](https://www.anthropic.com/engineering) | artigos de engenharia; o melhor da área |
| Simon Willison | [simonwillison.net](https://simonwillison.net/) | análise crítica, quase diária, sobre LLMs e agentes. Não vende nada |
| Hugging Face | [huggingface.co/blog](https://huggingface.co/blog) | agentes abertos, smolagents |
| Chip Huyen | [huyenchip.com](https://huyenchip.com/) | engenharia de sistemas com IA |
| Princeton NLP / SWE-bench | GitHub e site do projeto | avaliação de agentes de código |

---

## 7. Assuntos relacionados nesta pasta

| Assunto | Por que se conecta |
|---|---|
| [`testes-automatizados`](../testes-automatizados/00-MAPA.md) | verificação é o gargalo do laço agêntico |
| [`docker`](../docker/00-MAPA.md) | sandbox é a forma séria de dar autonomia |
| [`apis`](../apis/00-MAPA.md) | você vai chamar e expor APIs o tempo todo |
| [`bert`](../bert/00-MAPA.md) | como funciona o modelo por baixo |
| [`ethical-hacking`](../ethical-hacking/00-MAPA.md) | injeção de prompt, superfície de ataque |
| [`postgresql`](../postgresql/00-MAPA.md) | o banco que os seus servidores MCP vão consultar |

---

## Nota sobre verificação

Todos os links foram alcançados em **13/08/2026**. Os identificadores de arXiv
de 2017–2024 são estáveis e verificáveis. Os três artigos de 2026 (UTBoost,
Holistic Agent Leaderboard, BenchJack) foram encontrados por busca na web na
mesma data; confira o identificador antes de citar em trabalho formal.

Os números de benchmark citados no [65](65-estado-da-arte.md) vêm de
compilações públicas recolhidas por busca em 13/08/2026, **não** de execução
própria. Trate-os como indicativos, com as reservas descritas naquele arquivo.
