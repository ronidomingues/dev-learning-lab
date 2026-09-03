# 05 · Manual de uso — comandos, flags e atalhos

**Nível:** iniciante → intermediário · Referência consultável
**Base:** Claude Code **2.1.231** · verificado em 13/08/2026

Organizado **por tarefa**, não por ordem alfabética — é assim que você procura
na prática. Convenções: `<arg>` obrigatório, `[arg]` opcional.

> **A lista viva está sempre a um comando de distância.** Dentro da sessão,
> digite `/` para ver tudo o que está disponível *para você* (varia por
> plataforma, plano e ambiente), ou `/help`. Fora dela, `claude --help`.
> Esta página é o mapa comentado; a sessão é a verdade.

---

## Índice rápido

| Você quer… | Vá para |
|---|---|
| começar num repositório novo | [§1](#1-configurar-um-projeto) |
| trabalhar numa tarefa | [§2](#2-durante-a-tarefa) |
| controlar custo e contexto | [§3](#3-contexto-modelo-e-custo) |
| paralelizar | [§4](#4-trabalho-em-paralelo) |
| revisar antes de subir | [§5](#5-antes-de-entregar) |
| navegar entre conversas | [§6](#6-entre-sessões) |
| algo quebrou | [§7](#7-quando-algo-dá-errado) |
| estender o agente | [§8](#8-estender-mcp-skills-plugins-hooks) |
| rodar fora do terminal | [§9](#9-fora-do-terminal-nuvem-web-ci) |
| comandos do terminal (`claude …`) | [§10](#10-linha-de-comando) |
| flags | [§11](#11-flags-mais-usadas) |
| atalhos de teclado | [§12](#12-atalhos-de-teclado) |
| prefixos de entrada (`!`, `@`, `/`) | [§13](#13-prefixos-de-entrada) |
| o que saiu de linha | [§14](#14-obsoleto-e-removido) |

---

## 1. Configurar um projeto

| Comando | O que faz | Nota |
|---|---|---|
| `/init` | gera um `CLAUDE.md` inicial lendo o repositório | **revise e corte.** Ele escreve demais. |
| `/memory` | edita os `CLAUDE.md` e liga/desliga a memória automática | |
| `/permissions` | regras de allow / ask / deny | alias: `/allowed-tools` |
| `/mcp` | conecta e gerencia servidores MCP | `reconnect <servidor>`, `enable`/`disable` |
| `/hooks` | mostra os hooks configurados | leitura; edição é no `settings.json` |
| `/config [chave=valor]` | abre as configurações, ou define direto | `/config theme=dark`, `/config model=sonnet`, `/config --help` lista tudo |
| `/doctor` | diagnóstico completo, com correções propostas | **rode no primeiro dia e a cada mês.** Alias: `/checkup` |
| `/import [codex\|gemini]` | traz configuração de outro agente de código | `--dry-run` para espiar |
| `/statusline` | configura a barra de status | descreva o que quer |
| `/terminal-setup` | ajusta `Shift+Enter` e afins | só aparece em terminais que precisam |
| `/keybindings` | abre o arquivo de atalhos | |
| `/theme` | tema de cores, incluindo daltônicos | |
| `/install-github-app` | instala o app do GitHub e os workflows | |

## 2. Durante a tarefa

| Comando | O que faz |
|---|---|
| `/plan [descrição]` | entra em plan mode; opcionalmente já com a tarefa |
| `/btw [pergunta]` | pergunta lateral que **não** entra na conversa — ótimo para "que flag mesmo faz X?" sem poluir o contexto |
| `/goal <condição>` | define uma condição de conclusão; ele continua trabalhando entre turnos até bater. `/goal clear` cancela |
| `/subtask <tarefa>` | delega a um subagente que herda a conversa e devolve o resultado aqui |
| `/diff` | visualizador de diff das mudanças não commitadas e por turno |
| `/rewind` | volta código e/ou conversa a um ponto anterior. Aliases: `/undo`, `/checkpoint` |
| `/tasks` | lista o trabalho em segundo plano da sessão. Alias: `/bashes` |
| `/verify` | **[skill]** roda o app de verdade e observa o resultado, em vez de confiar em testes |
| `/run` | **[skill]** sobe e dirige o app do projeto |
| `/copy [N]` | copia a última resposta (ou a N-ésima) para a área de transferência |
| `/export [arquivo]` | exporta a conversa em texto |
| `/recap` | resumo de uma linha da sessão |
| `/focus` | modo de visualização enxuto (só em fullscreen) |

## 3. Contexto, modelo e custo

| Comando | O que faz | Quando |
|---|---|---|
| `/context [all]` | grade visual do que ocupa o contexto | **o comando mais subutilizado.** Rode quando ele começar a "esquecer" |
| `/compact [instruções]` | resume a conversa e libera espaço | `/compact foque nas mudanças de API` |
| `/autocompact [auto\|<tokens>]` | ajusta em que ponto o auto-compact dispara | ex.: `500k` |
| `/clear [nome]` | conversa nova, contexto vazio | **ao trocar de assunto.** Aliases: `/reset`, `/new` |
| `/model [modelo]` | troca de modelo e salva como padrão | `s` na lista troca só na sessão |
| `/effort [nível]` | `low`, `medium`, `high`, `xhigh`, `max`, `ultracode`, `auto` | vale mais que trocar de modelo, no geral |
| `/fast [on\|off]` | modo rápido (Opus, saída mais veloz, preço maior) | |
| `/advisor [modelo\|off]` | pareia um modelo consultor mais forte para decisões difíceis | |
| `/usage` | custo da sessão, limites do plano, quebra por skill/subagente/MCP | aliases: `/cost`, `/stats` |
| `/usage-credits` | configura ou pede créditos extras | |
| `/status` | versão, modelo, conta, conectividade | funciona enquanto ele responde |
| `/insights` | relatório HTML das suas sessões recentes | |

## 4. Trabalho em paralelo

| Comando | O que faz | Custo |
|---|---|---|
| `/background [prompt]` | destaca a sessão para rodar em segundo plano. Alias: `/bg` | 1 sessão |
| `/fork [prompt]` | copia a conversa para uma nova sessão de fundo; esta continua | 2 sessões |
| `/branch [nome]` | ramifica a conversa aqui e **muda** você para o ramo | 1 sessão |
| `/subtask <tarefa>` | subagente com o contexto atual; resultado volta para cá | + tokens |
| `/batch <instrução>` | **[skill]** quebra uma mudança grande em 5–30 unidades, cada uma num worktree isolado, cada uma abrindo um PR | **caro** |
| `/deep-research <pergunta>` | **[workflow]** leque de buscas na web, checagem cruzada, relatório citado | caro |
| `/workflows` | acompanha, pausa, retoma e salva workflows | |
| `/list-agents` | lista subagentes e sessões que o Claude pode mandar mensagem. Alias: `/peers` | |
| `/stop` | para a sessão de fundo à qual você está anexado | |

> Rodar várias sessões multiplica o consumo de tokens. `/usage` antes e
> depois, na primeira vez, para calibrar a intuição.

## 5. Antes de entregar

| Comando | O que faz |
|---|---|
| `/diff` | revisa as mudanças |
| `/code-review [nível] [--fix] [--comment] [pr#\|branch\|caminho]` | **[skill]** procura bugs de correção e limpezas. Níveis: `low`…`max`, e `ultra` (multiagente, na nuvem). Alias: `/review` |
| `/simplify [alvo]` | **[skill]** só qualidade — reuso, simplificação, eficiência, nível de abstração — e **aplica** as correções. Não caça bugs |
| `/security-review` | analisa o diff do branch em busca de vulnerabilidades. Exige remoto `origin` |
| `/autofix-pr [prompt]` | sessão na nuvem que vigia o PR e corrige quando o CI quebra ou chega review |
| `/install-github-app` | revisão automática de PR no repositório |

> **`/code-review` × `/simplify`:** o primeiro procura o que está **errado**;
> o segundo, o que está **feio**. Rode o primeiro sempre, o segundo quando
> sobrar tempo.

## 6. Entre sessões

| Comando | O que faz |
|---|---|
| `/resume [sessão]` | retoma por id, por nome, ou abre o seletor. Alias: `/continue` |
| `/clear [nome]` | nova conversa; o nome rotula a anterior no seletor |
| `/rename [nome]` | renomeia a sessão atual |
| `/teleport` | traz uma sessão da web para este terminal. Alias: `/tp` |
| `/remote-control` | permite controlar esta sessão local pelo claude.ai ou pelo app. Alias: `/rc` |
| `/desktop` | continua no app de desktop. Alias: `/app` |
| `/cd <caminho>` | move a sessão para outro diretório, mantendo a conversa e o cache |
| `/add-dir <caminho>` | dá acesso a um diretório extra sem mudar de sessão |
| `/team-onboarding` | gera um guia de setup da sua configuração para um colega |

## 7. Quando algo dá errado

| Comando | O que faz |
|---|---|
| `/doctor` | **comece por aqui.** Diagnostica instalação, PATH, settings inválidos, hooks lentos, `CLAUDE.md` inchado; propõe correções e pede confirmação |
| `/debug [descrição]` | **[skill]** liga o log de depuração daqui em diante e investiga |
| `/rewind` | desfaz código e/ou conversa |
| `/context` | quando ele "esquece" ou repete trabalho |
| `/bug [relato]` | reporta um bug com contexto da sessão (você escolhe quanto histórico). Alias: `/share` |
| `/feedback [relato]` | feedback de produto |
| `/release-notes` | changelog navegável — útil quando algo mudou de comportamento |
| `/reload-plugins [--force]` | recarrega plugins sem reiniciar |
| `/reload-skills` | re-escaneia as skills adicionadas em disco durante a sessão |
| `/heapdump` | snapshot de memória para diagnosticar consumo alto. **Não compartilhe o `.heapsnapshot`** — contém a conversa inteira e credenciais; só o `-diagnostics.json` |

## 8. Estender: MCP, skills, plugins, hooks

| Comando | O que faz |
|---|---|
| `/mcp` | lista, conecta, autentica servidores MCP |
| `/skills` | lista as skills; `t` ordena por custo em tokens; `Espaço` alterna visibilidade |
| `/plugin [list\|install\|enable\|disable]` | gerencia plugins |
| `/agents` | a partir da 2.1.198, apenas lembra onde ficam os arquivos de subagente (`.claude/agents/`). Para criar, **peça ao Claude** ou edite o arquivo |
| `/hooks` | mostra os hooks por evento |
| `/run-skill-generator` | **[skill]** escreve uma skill que ensina `/run` e `/verify` a subir o seu app |
| `/fewer-permission-prompts` | **[skill]** varre seus transcritos e propõe uma allowlist para reduzir perguntas |
| `/loop [intervalo] [prompt]` | **[skill]** roda um prompt repetidamente. `/loop 5m veja se o deploy terminou`. Sem intervalo, ele se autorregula. Alias: `/proactive` |
| `/schedule [descrição]` | rotinas agendadas que rodam na nuvem. Alias: `/routines` |
| `/claude-api [migrate\|prompt-audit]` | **[skill]** referência da Claude API; migra código para modelo novo; audita prompts datados |
| `/dataviz [pedido]` | **[skill]** guia de design para gráficos e dashboards |
| `/design-sync [dica]` | **[skill]** envia o design system React do repo para o Claude Design |

Prompts expostos por servidores MCP viram comandos automaticamente, no
formato `/mcp__<servidor>__<prompt>`.

## 9. Fora do terminal: nuvem, web, CI

| Comando | O que faz |
|---|---|
| `/web-setup` | conecta sua conta do GitHub ao Claude Code na web |
| `/remote-env` | escolhe o ambiente padrão dos agentes na nuvem |
| `/schedule` | cria rotinas agendadas na nuvem |
| `/autofix-pr` | sessão na nuvem que corrige o PR |
| `/mobile` | QR code do app. Aliases: `/ios`, `/android` |
| `/install-slack-app` | instala o app do Slack |
| `/chrome` | configura a integração com o Chrome |

## Utilidades e curiosidades

`/login` · `/logout` · `/exit` (alias `/quit`) · `/help` · `/color` ·
`/tui [default|fullscreen]` · `/scroll-speed` · `/voice [hold|tap|off]` ·
`/privacy-settings` · `/upgrade` · `/passes` · `/powerup` (lições
interativas — vale meia hora) · `/stickers` · `/radio` (rádio lo-fi) ·
`/setup-bedrock` · `/setup-vertex` · `/sandbox` · `/ide` · `/design-login`

---

## 10. Linha de comando

| Comando | O que faz |
|---|---|
| `claude` | sessão interativa |
| `claude "pergunta"` | sessão interativa já com o primeiro prompt |
| `claude -p "pergunta"` | responde e sai — **modo headless**, para scripts |
| `cat log.txt \| claude -p "explique"` | processa entrada canalizada |
| `claude -c` | continua a conversa mais recente deste diretório |
| `claude -r "<sessão>" "pergunta"` | retoma por id ou nome |
| `claude --from-pr 123` | retoma a sessão ligada a um PR |
| `claude update` | atualiza |
| `claude install [versão\|stable\|latest]` | instala/reinstala uma versão |
| `claude doctor` | diagnóstico somente-leitura, sem abrir sessão |
| `claude auth login \| logout \| status` | autenticação (`--console`, `--sso`, `--email`) |
| `claude setup-token` | token de longa duração para CI e scripts |
| `claude mcp` | configura servidores MCP fora da sessão |
| `claude mcp login <nome>` / `logout <nome>` | OAuth de um servidor MCP (`--no-browser` via SSH) |
| `claude plugin` | gerencia plugins (alias `claude plugins`) |
| `claude agents` | abre o **agent view**: painel de todas as sessões de fundo. `--json` para script |
| `claude attach <id>` / `logs <id>` / `stop <id>` / `rm <id>` / `respawn <id>` | controla sessões de fundo |
| `claude project purge [caminho]` | apaga todo o estado local de um projeto (`--dry-run` primeiro) |
| `claude remote-control` | servidor de Remote Control (sem sessão local) |
| `claude ultrareview [alvo]` | revisão multiagente na nuvem, não interativa (`--json`) |
| `claude import [codex\|gemini]` | importa configuração de outro agente |
| `claude daemon status \| stop --any` | supervisor das sessões de fundo |
| `claude gateway --config gateway.yaml` | gateway corporativo (SSO/telemetria) |
| `claude self-hosted-runner setup` | runner para ambientes auto-hospedados |

## 11. Flags mais usadas

`claude --help` **não lista todas**; a ausência ali não significa que a flag
não existe.

### Escolher modelo e esforço
```bash
claude --model claude-opus-5      # ou: opus, sonnet, haiku, fable
claude --effort xhigh             # low | medium | high | xhigh | max | ultracode
claude --fallback-model sonnet,haiku
```

### Permissões e ferramentas
```bash
claude --permission-mode plan     # default|manual, acceptEdits, plan, auto, dontAsk, bypassPermissions
claude --allowedTools "Bash(git log *)" "Read"
claude --disallowedTools "Bash(rm *)"
claude --tools "Bash,Edit,Read"   # restringe o conjunto de ferramentas embutidas
claude --dangerously-skip-permissions   # só em contêiner isolado
```

### Diretórios e isolamento
```bash
claude --add-dir ../lib ../apps
claude -w feature-auth            # worktree git isolado
claude -w '#1234'                 # worktree a partir de um PR
claude --worktree --tmux          # painéis tmux/iTerm2
```

### Automação e scripts
```bash
claude -p "resuma o diff" --output-format json
claude -p "..." --max-turns 5 --max-budget-usd 2.00
claude -p "..." --json-schema '{"type":"object", ...}'   # saída validada
claude -p "..." --output-format stream-json --verbose --include-partial-messages
claude --bare -p "..."            # modo mínimo: sem hooks, plugins, CLAUDE.md — parte rápido
```

### Sessões
```bash
claude -c                         # continuar a última
claude -r auth-refactor           # retomar por nome
claude -n "trabalho-de-quinta"    # nomear
claude --fork-session -r abc123   # retomar em cópia, preservando a original
claude --session-id <uuid>
```

### Diagnóstico e configuração
```bash
claude --debug='mcp,startup'      # o `=` é obrigatório para filtrar
claude --debug-file /tmp/cc.log
claude --safe-mode                # desliga TODA customização — é o teste de bissecção
claude --settings ./settings.json
claude --setting-sources user,project
claude --mcp-config ./mcp.json --strict-mcp-config
```

### Prompt de sistema
```bash
claude --append-system-prompt "Responda sempre em português do Brasil."
claude --append-system-prompt-file ./regras.txt
claude --system-prompt "Você é um revisor de SQL."       # SUBSTITUI o padrão
claude --system-prompt-file ./persona.txt                # idem
```

> **Acrescentar × substituir.** `--append-*` mantém as instruções de
> ferramenta, as regras de segurança e as convenções de código do prompt
> padrão, e adiciona as suas. `--system-prompt` joga **tudo** fora, e a
> responsabilidade pelo que faltar passa a ser sua. Use `--append-*` em 95%
> dos casos; `--system-prompt` só quando o agente não é um agente de código.

### Outros
```bash
claude --bg "investigue o teste instável"    # sessão de fundo
claude --cloud "corrija o bug de login"      # sessão na nuvem
claude --teleport
claude --chrome                              # integração com o navegador
claude --agent revisor                       # inicia a sessão como um subagente definido
claude --agents '{"revisor":{"description":"...","prompt":"..."}}'
claude --autocompact 500k
claude --ax-screen-reader                    # saída para leitor de tela
```

## 12. Atalhos de teclado

### Essenciais
| Atalho | O que faz |
|---|---|
| `Esc` | **interrompe** o Claude no meio do turno, preservando o que já foi feito |
| `Esc` `Esc` | limpa o rascunho; com o prompt vazio, abre o menu de rewind |
| `Shift+Tab` | alterna os modos de permissão (`Alt+M` em alguns Windows) |
| `Ctrl+C` | interrompe; com nada rodando, limpa a entrada; duas vezes, sai |
| `Ctrl+D` | sai (duas vezes em 800 ms) |
| `Ctrl+L` | redesenha a tela; duas vezes em fullscreen = `/clear` |
| `Ctrl+O` | abre o **visualizador de transcrito** — mostra as chamadas de ferramenta em detalhe. Use quando não entender o que ele fez |
| `Ctrl+R` | busca reversa no histórico de comandos |
| `Ctrl+B` | joga o comando ou agente atual para segundo plano |
| `Ctrl+T` | mostra/esconde a lista de tarefas do Claude |
| `Ctrl+G` | abre o prompt no seu editor (`$EDITOR`) |
| `Ctrl+V` | cola imagem da área de transferência (`Alt+V` no Windows/WSL) |
| `Ctrl+X Ctrl+K` (2×) | para **todos** os subagentes de fundo |
| `Ctrl+S` | guarda/restaura o rascunho do prompt |
| `Ctrl+Z` | suspende o processo (Unix); `fg` retoma |
| `Alt+P` / `Option+P` | troca de modelo sem perder o prompt |
| `Alt+T` / `Option+T` | liga/desliga o pensamento estendido |
| `Alt+O` / `Option+O` | liga/desliga o modo rápido |
| `?` (entrada vazia) | painel de ajuda dos atalhos |

### Edição da linha (padrão readline)
`Ctrl+A` início · `Ctrl+E` fim · `Ctrl+K` apaga até o fim ·
`Ctrl+U` apaga até o início · `Ctrl+W` apaga a palavra anterior ·
`Ctrl+Y` cola o que foi apagado · `Alt+B`/`Alt+F` navega por palavra ·
`Ctrl+_` desfaz a última edição

Modo Vim: ative em `/config` → **Editor mode** (o antigo `/vim` foi removido).

## 13. Prefixos de entrada

| Prefixo | Efeito |
|---|---|
| `/` no início | comando ou skill. Digite `/` sozinho para a lista filtrável |
| `!` no início | **modo shell**: roda o comando direto, coloca a saída no contexto e o Claude responde a ela. `!git log --oneline -20` |
| `@` | autocompletar caminho de arquivo. `@src/pedidos.py` referencia o arquivo |
| `:` | atalho de emoji (`:rocket:`) |
| `?` na entrada vazia | painel de atalhos |

> O `!` é subutilizado e resolve metade dos problemas de "ele não sabe o
> estado atual": `!npm test`, `!docker ps`, `!git status` — a saída entra no
> contexto de uma vez, sem ele precisar decidir rodar.

Encadeamento de skills (a partir da 2.1.199): `/skill-a /skill-b faça X`
carrega as duas e passa `faça X` como argumento para ambas. Até seis.

## 14. Obsoleto e removido

| Antigo | Situação | Use |
|---|---|---|
| `/vim` | removido na 2.1.92 | `/config` → Editor mode |
| `/pr-comments` | removido na 2.1.91 | peça direto ao Claude |
| `/ultraplan` | removido | plan mode (`Shift+Tab` ×2) |
| `/ultrareview` | vira alias | `/code-review ultra` |
| `/agents` (painel interativo) | desde a 2.1.198 só imprime um aviso | peça ao Claude, ou edite `.claude/agents/` |
| `--enable-auto-mode` | removido na 2.1.111 | `--permission-mode auto` |
| `--remote` | alias depreciado | `--cloud` |
| `/extra-usage` | renomeado | `/usage-credits` |

---

## Coisas que só quem usa há meses sabe

1. **`/btw` é o comando mais subestimado.** Pergunta lateral que não entra na
   conversa. Você não precisa mais escolher entre "perguntar e poluir o
   contexto" e "abrir outro terminal".
2. **Digite a correção sem apertar `Esc`.** Se você escrever e mandar enquanto
   ele trabalha, a mensagem é lida assim que a ferramenta atual termina, e ele
   ajusta antes do próximo passo. `Esc` cancela; digitar **redireciona**.
3. **`Ctrl+O` responde "por que ele fez isso?"** O transcrito expandido mostra
   cada chamada de ferramenta, com o modelo usado e o horário.
4. **`/context` antes de `/compact`.** Compactar sem olhar é remédio no
   escuro; às vezes o que está ocupando 40% é uma skill que você nem usa, e a
   correção é `/skills` + `Espaço`, não `/compact`.
5. **`--safe-mode` é bissecção de configuração.** "Quebrou e eu não sei o que
   foi": rode com `--safe-mode`; se funcionar, o culpado é sua customização,
   não o Claude Code.
6. **`/effort` mexe mais que `/model`.** Subir de `high` para `xhigh` em
   tarefa agêntica costuma render mais que trocar de modelo — e descer para
   `low` num subagente de leitura corta custo sem perda perceptível.
7. **`--bare` para scripts.** Pula hooks, plugins, LSP, `CLAUDE.md`. Um `-p`
   em CI parte muito mais rápido e sem surpresas de configuração.
8. **`/rewind` também resume.** Além de voltar código e conversa, dá para
   pedir um resumo a partir de uma mensagem selecionada.
9. **`claude -p` com `--json-schema` é a ponte para automação.** Você recebe
   JSON validado, não texto para regex.
10. **`git worktree` via `-w` é a forma limpa de paralelizar.** Duas sessões
    na mesma pasta se atropelam; `claude -w tarefa-a` e `claude -w tarefa-b`
    não.

---

## Autoteste

1. Diferença entre `/compact`, `/clear` e `/rewind`.
2. Você quer perguntar "qual a flag do pytest para parar no primeiro erro?"
   sem sujar a conversa. Qual comando?
3. `/code-review` × `/simplify`: o que cada um procura?
4. Qual a diferença prática entre `--append-system-prompt` e `--system-prompt`,
   e por que a segunda é arriscada?
5. Você quer trabalhar em duas tarefas ao mesmo tempo, no mesmo repositório,
   sem que uma sobrescreva a outra. Qual flag?
6. O que `Esc` faz diferente de digitar uma correção e mandar?
7. Sua configuração quebrou depois de instalar um plugin. Qual flag isola o
   problema em um comando?
8. Você quer que um script de CI receba JSON validado. Quais duas flags?
9. Onde você encontra a lista de comandos que está de fato disponível na sua
   máquina, hoje?

---

**Fontes consultadas em 13/08/2026:**
[Commands reference](https://code.claude.com/docs/en/commands),
[CLI reference](https://code.claude.com/docs/en/cli-reference),
[Interactive mode](https://code.claude.com/docs/en/interactive-mode); e a
saída de `claude --help` da versão 2.1.231 instalada localmente.
