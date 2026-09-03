# 95 · Referências — documentação, specs, papers

> **Nível:** todos · **Verificado em:** 13/08/2026 · Claude Code 2.1.231
> Tudo aqui foi consultado ou acessado nesta data. Onde não pude verificar, está dito.

---

## 1. Documentação oficial — a fonte primária

**Base:** [code.claude.com/docs](https://code.claude.com/docs)
Índice completo em texto puro (útil para dar ao próprio agente):
`https://code.claude.com/docs/llms.txt`

> **Nota:** as URLs antigas em `docs.claude.com/en/docs/claude-code/*` redirecionam com
> **301** para `code.claude.com/docs/en/*`. Se você tem links antigos salvos, atualize.

### Páginas consultadas na produção deste curso (todas em 13/08/2026)

| Página | URL | Usada em |
|---|---|---|
| Advanced setup | `/docs/en/setup` | [`03`](03-instalacao.md) |
| CLI reference | `/docs/en/cli-reference` | [`05`](05-manual-de-uso.md), [`23`](23-headless-e-sdk.md) |
| Commands reference | `/docs/en/commands` | [`05`](05-manual-de-uso.md) |
| Interactive mode | `/docs/en/interactive-mode` | [`05`](05-manual-de-uso.md) |
| Tools reference | `/docs/en/tools-reference` | [`14`](14-ferramentas.md) |
| Memory | `/docs/en/memory` | [`13`](13-contexto-e-memoria.md) |
| Settings | `/docs/en/settings` | [`16`](16-configuracao.md) |
| Permission modes | `/docs/en/permission-modes` | [`15`](15-permissoes-e-modos.md) |
| Permissions | `/docs/en/permissions` | [`15`](15-permissoes-e-modos.md) |
| Hooks | `/docs/en/hooks` | [`17`](17-hooks.md) |
| Skills | `/docs/en/skills` | [`18`](18-skills-e-comandos.md) |
| Subagents | `/docs/en/sub-agents` | [`19`](19-subagentes.md) |
| MCP | `/docs/en/mcp` | [`20`](20-mcp.md) |
| Plugins | `/docs/en/plugins` | [`21`](21-plugins-e-marketplaces.md) |
| Headless / Agent SDK | `/docs/en/headless` | [`23`](23-headless-e-sdk.md) |
| Security | `/docs/en/security` | [`24`](24-seguranca.md) |
| Costs | `/docs/en/costs` | [`26`](26-times-e-escala.md), [`80`](80-custos-e-licencas.md) |

### Páginas citadas mas não abertas na íntegra

`/docs/en/sandboxing`, `/docs/en/devcontainer`, `/docs/en/agent-teams`, `/docs/en/worktrees`,
`/docs/en/monitoring-usage`, `/docs/en/analytics`, `/docs/en/github-actions`,
`/docs/en/agent-sdk/overview`, `/docs/en/plugin-marketplaces`, `/docs/en/plugins-reference`.
Referenciadas a partir das páginas consultadas. **Declarado por honestidade.**

### Outras fontes oficiais

| Recurso | URL |
|---|---|
| Preços de planos | [claude.com/pricing](https://claude.com/pricing) |
| Preços de API por token | [platform.claude.com/docs/en/about-claude/pricing](https://platform.claude.com/docs/en/about-claude/pricing) |
| Console (uso, chaves, limites) | [platform.claude.com](https://platform.claude.com) |
| Painel de Claude Code (API) | [platform.claude.com/claude-code](https://platform.claude.com/claude-code) |
| Anthropic Academy | [anthropic.skilljar.com](https://anthropic.skilljar.com/) |
| Trust Center (SOC 2, ISO 27001) | [trust.anthropic.com](https://trust.anthropic.com) |
| Centro de privacidade | [privacy.anthropic.com](https://privacy.anthropic.com) |
| Diretório de conectores | [claude.ai/directory](https://claude.ai/directory) |
| Claude Code na web | [claude.ai/code](https://claude.ai/code) |

---

## 2. Especificações e padrões abertos

| Spec | URL | Por que importa |
|---|---|---|
| **Model Context Protocol** | [modelcontextprotocol.io](https://modelcontextprotocol.io) | O protocolo do [`20`](20-mcp.md). Anunciado em nov/2024 |
| **Agent Skills** | [agentskills.io](https://agentskills.io) | Formato portável de skill ([`18`](18-skills-e-comandos.md)) |
| **JSON Schema** | [json-schema.org](https://json-schema.org) | Usado em `--json-schema` ([`23`](23-headless-e-sdk.md)) |
| **Esquema de settings do Claude Code** | `https://json.schemastore.org/claude-code-settings.json` | Validação e autocompletar ([`16`](16-configuracao.md)) |
| **OpenTelemetry** | [opentelemetry.io](https://opentelemetry.io) | Métricas por usuário ([`26`](26-times-e-escala.md)) |

---

## 3. Papers

Todos gratuitos no arXiv. Os cinco primeiros são os que realmente sustentam o
[`60-teoria-avancada.md`](60-teoria-avancada.md).

| Paper | Ano | Por que ler |
|---|---|---|
| Vaswani et al., **Attention Is All You Need** (arXiv:1706.03762) | 2017 | A arquitetura. A origem do custo $O(n^2)$ |
| Liu et al., **Lost in the Middle** (arXiv:2307.03172) | 2023 | Degradação posicional em contexto longo. Sustenta "curadoria vence tamanho" |
| Dao et al., **FlashAttention** (arXiv:2205.14135) | 2022 | Por que o ganho foi de constante, não de ordem |
| Gu & Dao, **Mamba** (arXiv:2312.00752) | 2023 | A alternativa recorrente mais séria à atenção |
| Yao et al., **ReAct** (arXiv:2210.03629) | 2022 | Formalização do laço raciocínio + ação — o laço agêntico |
| Jimenez et al., **SWE-bench** (arXiv:2310.06770) | 2023 | Como se mede agente de código, e os limites disso |
| Beltagy et al., **Longformer** (arXiv:2004.05150) | 2020 | Atenção esparsa: a tentativa e seu limite |
| Choromanski et al., **Performer** (arXiv:2009.14794) | 2020 | Atenção linear: idem |
| **UTBoost** (arXiv:2506.09289) | 2026 | Rigor na avaliação de agentes no SWE-bench |
| **Holistic Agent Leaderboard** (arXiv:2510.11977) | 2026 | Infraestrutura de avaliação de agentes |

Fundamentos clássicos, fora do arXiv:

- **A. M. Turing**, *On Computable Numbers…* (1936) — problema da parada.
- **H. G. Rice**, *Classes of Recursively Enumerable Sets and Their Decision Problems*,
  Transactions of the AMS (1953) — indecidibilidade de propriedades semânticas.
- **E. W. Dijkstra**, *Notes on Structured Programming* (1970) — "testes mostram a presença
  de bugs, nunca a ausência".

---

## 4. Segurança

| Recurso | URL |
|---|---|
| OWASP Top 10 for LLM Applications | [owasp.org](https://owasp.org/) |
| Programa de bug bounty do Claude Code | [HackerOne](https://hackerone.com/) (link específico na página de segurança da doc) |
| Chave de assinatura das versões | `https://downloads.claude.ai/keys/claude-code.asc` — impressão digital `31DDDE24DDFAB679F42D7BD2BAA929FF1A7ECACE` |

---

## 5. Este repositório

| Assunto | Por que é relevante aqui |
|---|---|
| [`../testes-automatizados/`](../testes-automatizados/00-MAPA.md) | **O pré-requisito nº 1.** Sem oráculo, agente não converge |
| [`../apis/`](../apis/00-MAPA.md) | HTTP, REST e MCP; base do projeto-modelo |
| [`../docker/`](../docker/00-MAPA.md) | Isolamento e contêineres para rodar o agente com segurança |
| [`../ethical-hacking/`](../ethical-hacking/00-MAPA.md) | Modelo de ameaça, OWASP, IA ofensiva |
| [`../bert/`](../bert/00-MAPA.md) | Como funciona um transformador por dentro |

---

## 6. Verificações locais feitas neste curso

Tudo abaixo foi **executado** nesta máquina em **13/08/2026** (Ubuntu 22.04.5 LTS):

| Comando | Saída real |
|---|---|
| `claude --version` | `2.1.231 (Claude Code)` |
| `node --version` | `v24.18.0` |
| `npm --version` | `12.0.1` |
| `git --version` | `git version 2.34.1` |
| `which claude` | `/home/ronivaldo/.local/bin/claude` |
| `claude -p "responda apenas com a palavra: pronto"` | `pronto` |
| `claude --bare -p "…"` (com login por assinatura) | `{"is_error":true, …, "result":"Not logged in · Please run /login"}` |
| `claude -p "…" --output-format json` | JSON com `total_cost_usd: 0.1906005`, `cache_read_input_tokens: 47811` |
| `node --test` (projeto-modelo) | **20 testes, 0 falhas** |
| `npm run verificar` (projeto-modelo) | **17 verificações ok, 0 problemas** |
| Hooks com evento JSON simulado | `deny` no caso de segredo; saída vazia + código 0 no caso legítimo; `exit 2` com `'baixa' !== 'media'` no caso de suíte quebrada |
| API do projeto-modelo com `curl` | 201 + `Location: /tarefas/1`; 400 `{"erro":"titulo é obrigatório"}` |

**O que não foi executado, e está declarado:** instalação em macOS e Windows; construção do
`Dockerfile` do [`03`](03-instalacao.md); exemplos 6, 7 e 14 do [`06`](06-exemplos.md);
o esqueleto de servidor MCP do [`20`](20-mcp.md); o roteiro interativo do projeto-modelo;
os 12 laboratórios do [`70`](70-pratica.md); o Agent SDK.

---

## 7. Fontes de terceiros usadas (e o ceticismo devido)

Para o panorama competitivo do [`65-estado-da-arte.md`](65-estado-da-arte.md), foram
consultados **agregadores**, não fontes primárias: morphllm.com, deployhq.com,
irenictech.com, lushbinary.com, llm-stats.com, entre outros encontrados em busca de
13/08/2026. Números de leaderboard citados a partir deles **não** foram verificados contra
fonte primária e estão marcados como tal no arquivo.

Para o [`85-cursos-e-certificacoes.md`](85-cursos-e-certificacoes.md), agregadores como
coursesity.com, scrimba.com, gptprompts.ai, pasqualepillitteri.it e spectrumailab.com foram
usados apenas para **localizar** cursos; os links do arquivo apontam para as fontes originais.

---

## 8. Como se manter atualizado

**[opinião]** Ordem de prioridade, do mais ao menos útil:

1. **`/release-notes`** dentro da sessão — o changelog da sua versão, interativo.
2. **A documentação oficial**, relida a cada 2–3 meses nas seções que você usa.
3. **`/insights`**, uma vez por mês: relatório sobre o **seu** uso, não sobre o campo.
4. **`llms.txt`** dado ao próprio agente, quando quiser saber se algo mudou.
5. Vídeos e blogs: por último. São os mais lentos a acompanhar e os mais propensos a repetir
   coisa obsoleta com confiança.

---

## Autoteste

1. Qual é a fonte primária, e para onde as URLs antigas redirecionam?
2. Cite os cinco papers que sustentam o [`60`](60-teoria-avancada.md) e o que cada um estabelece.
3. Qual é a impressão digital da chave de assinatura, e para que ela serve?
4. Que verificações locais este curso executou? Cite três e a saída real de cada.
5. O que este curso **não** executou, e por que declarar isso importa?
6. Por que os números de leaderboard do [`65`](65-estado-da-arte.md) estão marcados com ceticismo?
7. Qual é a melhor forma de se manter atualizado, e por que vídeos ficam por último?
