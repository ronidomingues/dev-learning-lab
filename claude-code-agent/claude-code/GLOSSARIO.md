# Glossário — Claude Code

> **Atualizado em:** 13/08/2026 · Claude Code 2.1.231
> Ordem alfabética. Termos em inglês aparecem com a tradução na primeira ocorrência, como o
> campo os usa. Onde há link, ele aponta para o arquivo que desenvolve o conceito.

---

## A

**`acceptEdits`** — Modo de permissão que aprova edições de arquivo e comandos comuns de
sistema de arquivos (`mkdir`, `touch`, `rm`, `rmdir`, `mv`, `cp`, `sed`) sem perguntar.
Ver [`15`](15-permissoes-e-modos.md).

**Agente** — Um modelo de linguagem dentro de um laço: pensa, chama ferramenta, observa o
resultado, repete. Ver [`10`](10-fundamentos.md).

**Agent SDK** — Pacotes Python e TypeScript que expõem o mesmo laço, ferramentas e gestão de
contexto do Claude Code, para uso programático. Ver [`23`](23-headless-e-sdk.md).

**Agent Skills** — Especificação aberta de formato de skill (agentskills.io), portável entre
ferramentas. Aceita apenas parte dos campos de frontmatter do Claude Code.

**`AGENTS.md`** — Convenção de instruções usada por outros agentes. O Claude Code **não** o
lê; importe-o do `CLAUDE.md` com `@AGENTS.md`.

**`allow`** — Lista de regras de permissão que executam sem perguntar. Perde para `deny`.

**Alucinação** — Saída plausível e falsa. Consequência de o modelo prever o provável sem ter
sinal interno de "não sei". Ver [`10`](10-fundamentos.md).

**`args`** (hook) — Campo que ativa a **forma exec** de um hook de comando: sem shell, sem
pipes, mais previsível. Ver [`17`](17-hooks.md).

**Atenção** — Mecanismo do transformador que compara cada token com todos os outros. Custo
$O(n^2)$. Ver [`60`](60-teoria-avancada.md).

**`auto` (modo)** — Modo de permissão em que um classificador separado revisa as ações antes
de executar. Vira padrão em Pro, Max e Team a partir de 14/08/2026.

**Auto memory / memória automática** — Notas que o Claude escreve para si mesmo, em
`~/.claude/projects/<projeto>/memory/`. Ver [`13`](13-contexto-e-memoria.md).

---

## B

**`--bare`** — Flag que ignora hooks, skills, plugins, MCP, memória e `CLAUDE.md`. O modo
correto para CI. **Não lê credenciais OAuth.** Ver [`23`](23-headless-e-sdk.md).

**`bypassPermissions`** — Modo que pula toda checagem de permissão. Só dentro de contêiner.

**Batch API** — Processamento assíncrono com 50% de desconto. Não serve para uso interativo.

---

## C

**Cache de prompt** — Reuso do prefixo já processado do contexto. Leitura custa ~10% do
preço de entrada. Vida útil: 1 h em assinatura, 5 min com créditos ou chave de API.

**Caminho protegido** — Arquivo ou diretório cuja escrita **nunca** é auto-aprovada
(`.git`, `.bashrc`, `.npmrc`, `.mcp.json`…). Ver [`15`](15-permissoes-e-modos.md).

**CCU (Claude Consumption Unit)** — Unidade de faturamento em marketplaces de nuvem;
100 CCU = US$ 1,00.

**Checkpoint** — Fotografia dos arquivos antes de uma mudança, que habilita o `/rewind`.

**`CLAUDE.md`** — Arquivo de instruções do projeto, carregado em toda sessão. É **contexto**,
não configuração: pede, não obriga. Ver [`13`](13-contexto-e-memoria.md).

**`CLAUDE.local.md`** — Versão pessoal e não versionada do `CLAUDE.md`.

**`claudeMdExcludes`** — Padrões de `CLAUDE.md` a ignorar. Essencial em monorepo.

**Compactação** — Resumo automático do histórico quando o contexto se aproxima do limite.
O `CLAUDE.md` da raiz é reinjetado; o resto se perde. Ver [`12`](12-anatomia-de-uma-sessao.md).

**Contexto (janela de)** — Todo o texto que o modelo "vê" agora. Medido em tokens, com
tamanho máximo. A única memória que existe.

**`context: fork`** — Campo de frontmatter que faz uma skill rodar num subagente que herda a
conversa. Ver [`18`](18-skills-e-comandos.md).

**Créditos de uso** — Cobrança adicional que permite continuar além da cota do plano.

---

## D

**`deny`** — Regras de permissão que bloqueiam. **Vencem `allow` sempre**, em qualquer escopo.

**Diálogo de confiança** — Pergunta que aparece na primeira execução num diretório. Hooks de
projeto só rodam depois dele.

**`disable-model-invocation`** — Campo que impede o Claude de acionar uma skill sozinho.

**`disallowedTools`** — Ferramentas removidas de um subagente ou skill. Garantia estrutural,
diferente de pedir no prompt.

**`dontAsk`** — Modo que **nega** tudo que não estiver pré-aprovado. O modo correto para CI.

---

## E

**`Edit`** — Ferramenta de substituição exata em arquivo existente. Exige leitura prévia.

**Efeito de esforço (`effort`)** — Nível de raciocínio estendido (`low` … `max`). Mais
esforço, mais tokens de saída.

**`env`** — Bloco de `settings.json` com variáveis de ambiente para todas as sessões.

**Escada de garantia** — Modelo mental deste curso: `CLAUDE.md` → regras → skill →
permissão → hook, em ordem crescente de garantia. Ver [`25`](25-o-oficio-do-profissional.md).

**Escopo (de configuração)** — Gerenciado → linha de comando → local → projeto → usuário.
Regras de permissão **somam** entre escopos. Ver [`16`](16-configuracao.md).

**Exit 2** — O **único** código de saída que bloqueia por si só num hook. `exit 1` não
bloqueia. Ver [`17`](17-hooks.md).

---

## F

**Fast mode** — Saída mais rápida no mesmo modelo Opus, com preço premium.

**Ferramenta (*tool*)** — Ação que o modelo pode pedir. Executada pelo Claude Code na sua
máquina, nunca pelo modelo. Ver [`14`](14-ferramentas.md).

**Fork** — Subagente que herda todo o contexto da conversa. Também: `--fork-session`, que
retoma uma sessão com ID novo.

**Forma exec × forma shell** — Duas maneiras de declarar hook de comando; com `args` (exec,
sem shell) ou sem (shell, com pipes). Ver [`17`](17-hooks.md).

**Frontmatter** — Bloco YAML entre `---` no topo de skills, subagentes e regras.

---

## G–H

**`gh`** — CLI do GitHub. Costuma vencer o servidor MCP equivalente por custar zero de
contexto até o uso. Ver [`20`](20-mcp.md).

**Hook** — Código executado pelo Claude Code em pontos fixos do ciclo de vida. **O único
mecanismo com garantia total.** Ver [`17`](17-hooks.md).

---

## I–J

**`if` (hook)** — Campo que filtra a execução de um hook com a sintaxe de regras de permissão.

**Injeção de prompt** — Conteúdo lido pelo agente que contém instruções e é obedecido.
Problema **estrutural**, sem solução completa conhecida. Ver [`24`](24-seguranca.md).

**`isolation: worktree`** — Faz um subagente rodar em cópia isolada do repositório. Necessário
para escrita concorrente. Ver [`19`](19-subagentes.md).

**`--json-schema`** — Flag que força a saída a obedecer um JSON Schema. O que torna o agente
utilizável dentro de software. Ver [`23`](23-headless-e-sdk.md).

---

## L–M

**Laço agêntico** — O ciclo pensa → age → observa → repete. Ver [`10`](10-fundamentos.md).

**Lost in the middle** — Degradação medida da recuperação de informação posicionada no meio
de um contexto longo. Ver [`60`](60-teoria-avancada.md).

**LSP (Language Server Protocol)** — Inteligência de código: ir para definição, referências,
tipos. Substitui buscas textuais por navegação exata.

**Marketplace (de plugins)** — Repositório git com catálogo de plugins. Ver [`21`](21-plugins-e-marketplaces.md).

**Matcher** — Filtro de quando um hook dispara. Sensível a maiúsculas. Ver [`17`](17-hooks.md).

**`maxTurns`** — Teto de turnos de um subagente. Freio contra laço infinito.

**MCP (Model Context Protocol)** — Padrão aberto para conectar agentes a sistemas externos.
Único custo de contexto **recorrente**. Ver [`20`](20-mcp.md).

**`mcp__<servidor>__<ferramenta>`** — Nome de uma ferramenta MCP em regras e matchers.

**`MEMORY.md`** — Índice da memória automática. Só as primeiras 200 linhas (ou 25 KB) entram
em cada sessão.

**Modelo (LLM)** — Programa que prevê o próximo pedaço de texto. Sem estado entre chamadas.

**Modo de permissão** — `default`, `acceptEdits`, `plan`, `auto`, `dontAsk`,
`bypassPermissions`. Ver [`15`](15-permissoes-e-modos.md).

**Modo plano** — Modo somente-leitura em que o agente propõe antes de agir. **O hábito de
maior retorno.**

---

## N–P

**Oráculo** — Mecanismo automático que decide se o resultado está certo: teste, compilador,
linter. Sem oráculo, o agente para no plausível. Ver [`25`](25-o-oficio-do-profissional.md).

**`-p` / `--print`** — Modo não interativo. Ver [`23`](23-headless-e-sdk.md).

**`paths:`** — Frontmatter de regra ou skill que limita o carregamento a arquivos que casam
com padrões. **A camada mais subutilizada.** Ver [`13`](13-contexto-e-memoria.md).

**Permissão** — Decisão sobre executar, perguntar ou negar uma ação. Ver [`15`](15-permissoes-e-modos.md).

**Plugin** — Pacote com skills, agentes, hooks, MCP, LSP, monitores e binários, distribuível
por marketplace. Ver [`21`](21-plugins-e-marketplaces.md).

**`PostToolUse`** — Evento de hook após uma ferramenta ter sucesso. **O de maior impacto**,
porque devolve a falha ao agente. Ver [`17`](17-hooks.md).

**`PreToolUse`** — Evento de hook antes da execução. Pode negar ou **reescrever a entrada**.

**Prompt de sistema** — Texto de instrução base, antes de tudo. Alterável com
`--append-system-prompt` / `--system-prompt`.

---

## R–S

**Regras (`.claude/rules/`)** — Arquivos markdown de convenção, com ou sem `paths:`.

**`/rewind`** — Rebobina **código e conversa** até um checkpoint. Diferente de `git checkout`.

**Sandbox** — Isolamento de sistema de arquivos e rede para comandos de shell. macOS, Linux
e WSL2; **não** no Windows nativo. Ver [`24`](24-seguranca.md).

**Sessão** — Uma conversa, com contexto próprio, do `claude` ao `/clear` ou à saída.

**`settings.json`** — Arquivo de configuração. Hierarquia em [`16`](16-configuracao.md).

**Skill** — Procedimento em markdown carregado **sob demanda**. Substitui e engloba os
comandos personalizados. Ver [`18`](18-skills-e-comandos.md).

**`SKILL.md`** — Arquivo principal de uma skill.

**Subagente** — Sessão-filha com contexto e ferramentas próprios, que devolve só o resumo.
Ver [`19`](19-subagentes.md).

**SWE-bench Verified** — Conjunto de 500 issues reais do GitHub, validadas por humanos,
usado para avaliar agentes de código. Mede tarefas **com oráculo**.

---

## T–Z

**Time de agentes** — Várias sessões coordenadas. Experimental; consome **~7×** mais tokens.

**Token** — Pedaço de palavra. Unidade de cobrança, de memória e de tempo.
~1 token para cada 3–4 caracteres em português.

**`ToolSearch`** — Ferramenta que carrega sob demanda o esquema de ferramentas adiadas (MCP).

**Transformador (*transformer*)** — Arquitetura de rede neural por trás dos LLMs atuais.
Origem do custo quadrático.

**Turno** — Uma ida ao modelo. `num_turns` no JSON de saída conta isso.

**`updatedInput`** — Campo de saída de hook `PreToolUse` que **reescreve** a entrada da
ferramenta. A maior economia de contexto disponível. Ver [`17`](17-hooks.md).

**`--verbose`** — Necessário com `--output-format stream-json`.

**Worktree** — Cópia adicional de um repositório git, em outro diretório e outro branch,
compartilhando o mesmo `.git`. Base do paralelismo com escrita. Ver [`22`](22-git-github-e-ci.md).

---

## Símbolos e prefixos da entrada

| Símbolo | Significado |
|---|---|
| `/` | Comando ou skill (só no começo da mensagem) |
| `!` | Modo shell: roda no seu shell e injeta a saída no contexto |
| `@` | Caminho de arquivo (autocompletar), ou recurso MCP (`@servidor:recurso`) |
| `#` | Grava na memória |
| `:` | Emoji por código |
| `?` | Painel de atalhos (com entrada vazia) |
| `$ARGUMENTS`, `$1` | Argumentos dentro de uma skill |
| `${CLAUDE_PROJECT_DIR}` | Raiz do projeto (hooks e skills) |
| `${CLAUDE_SKILL_DIR}` | Pasta da skill |

---

## Siglas

| Sigla | Significado |
|---|---|
| **CLI** | *Command-Line Interface* — interface de linha de comando |
| **LLM** | *Large Language Model* — modelo de linguagem grande |
| **LSP** | *Language Server Protocol* |
| **MCP** | *Model Context Protocol* |
| **MTok** | Milhão de tokens (unidade de preço) |
| **OTel** | OpenTelemetry |
| **RPM / TPM** | Requisições / tokens por minuto |
| **SAST** | *Static Application Security Testing* |
| **SDK** | *Software Development Kit* |
| **WSL** | *Windows Subsystem for Linux* |
