# 05 · Manual de uso — referência de comandos

> **Nível:** todos · **Atualizado em:** 13/08/2026 · **Base:** Claude Code **2.1.231**,
> documentação oficial consultada em 13/08/2026.
>
> ⚠️ **Este é o arquivo que envelhece mais rápido do curso.** Comandos entram e saem a cada
> poucas semanas. A fonte da verdade da **sua** versão é sempre `/help` (dentro da sessão) e
> `claude --help` (fora dela). Se algo aqui não existir na sua instalação, acredite na sua
> instalação.

Organizado **por tarefa**, não em ordem alfabética — é assim que se consulta de verdade.

---

## Mapa rápido: onde fica cada coisa

| Você quer… | Onde |
|---|---|
| Abrir, retomar, automatizar → [CLI](#1-cli--o-que-se-digita-no-terminal) |
| Controlar a conversa em andamento → [comandos de barra](#2-comandos-de-barra-por-tarefa) |
| Editar mais rápido → [atalhos de teclado](#3-atalhos-de-teclado) |
| Entender o que o agente pode fazer → [ferramentas](#4-ferramentas-embutidas) |
| Mudar comportamento permanente → [configuração](16-configuracao.md) |

---

## 1. CLI — o que se digita no terminal

### 1.1 Subcomandos

| Comando | O que faz |
|---|---|
| `claude` | Abre sessão interativa na pasta atual |
| `claude "pergunta"` | Abre sessão já com um primeiro prompt |
| `claude -p "pergunta"` | Roda **sem interface**, imprime a resposta e sai |
| `cat arq \| claude -p "…"` | Processa entrada canalizada (limite: 10 MB) |
| `claude -c` | Continua a conversa mais recente desta pasta |
| `claude -r "<sessão>" "…"` | Retoma sessão por ID ou nome |
| `claude update` | Atualiza agora |
| `claude install [versão\|stable\|latest]` | Instala/reinstala versão específica ou canal |
| `claude doctor` | **Diagnóstico.** Instalação, configuração, erros de settings |
| `claude auth login \| logout \| status` | Autenticação (`--console` para conta de API) |
| `claude setup-token` | Gera token de longa duração para CI |
| `claude mcp …` | Gerencia servidores MCP ([`20`](20-mcp.md)) |
| `claude plugin …` | Gerencia plugins ([`21`](21-plugins-e-marketplaces.md)) |
| `claude agents` | Painel de sessões em segundo plano |
| `claude attach <id>` / `logs <id>` / `stop <id>` / `rm <id>` / `respawn <id>` | Controle de sessões em background |
| `claude daemon status \| stop --any` | Supervisor das sessões em background |
| `claude import [codex\|gemini]` | Importa configuração de outro agente de código |
| `claude project purge [caminho]` | Apaga todo o estado local de um projeto |
| `claude remote-control` | Servidor de Remote Control (controlar esta sessão de outro dispositivo) |
| `claude gateway` | Gateway auto-hospedado (corporativo) |
| `claude self-hosted-runner` | Runner para ambiente auto-hospedado |
| `claude auto-mode defaults \| reset` | Regras do classificador do modo automático |
| `claude ultrareview [alvo]` | Revisão multiagente na nuvem, não interativa |

### 1.2 Flags que você realmente vai usar

| Flag | Para quê |
|---|---|
| `-p`, `--print` | Modo não interativo |
| `--output-format text\|json\|stream-json` | Formato da saída |
| `--json-schema '<schema>'` | Força a saída a obedecer um JSON Schema |
| `--allowedTools "Read,Bash(git diff *)"` | Pré-aprova ferramentas (sintaxe de regras de permissão) |
| `--disallowedTools "…"` | Nega ferramentas |
| `--permission-mode plan\|acceptEdits\|auto\|dontAsk\|bypassPermissions` | Modo inicial |
| `--model claude-sonnet-5` | Modelo da sessão |
| `--effort low\|medium\|high\|xhigh\|max` | Esforço de raciocínio (custo × qualidade) |
| `--fallback-model sonnet,haiku` | Cai para outro modelo se o primeiro falhar |
| `--add-dir ../lib ../apps` | Amplia a fronteira de leitura/escrita |
| `--continue`, `-c` / `--resume`, `-r` | Continuar / retomar |
| `--fork-session` | Retoma criando um ID novo, sem sujar a sessão original |
| `--bare` | **Ignora** hooks, skills, plugins, MCP, memória e `CLAUDE.md`. O modo certo para CI |
| `--safe-mode` | Inicia sem nenhuma personalização |
| `--append-system-prompt "…"` / `--system-prompt "…"` | Acrescenta ao / substitui o prompt de sistema |
| `--max-turns 3` | Teto de turnos agênticos |
| `--max-budget-usd 5.00` | Teto de gasto da invocação |
| `--settings ./s.json` / `--setting-sources user,project` | De onde vem a configuração |
| `--mcp-config ./mcp.json` / `--strict-mcp-config` | MCP explícito |
| `--agents '{"revisor":{…}}'` | Define subagentes na hora |
| `--bg`, `--background` | Roda como agente em segundo plano |
| `--cloud` | Cria/aciona sessão na web |
| `--ide` / `--chrome` | Conecta ao editor / ao Chrome |
| `--debug='mcp,startup'` / `--debug-file <path>` | Depuração |
| `--verbose` | Necessário com `stream-json` |
| `-n`, `--name "trabalho-x"` | Nomeia a sessão (facilita `--resume`) |
| `--dangerously-skip-permissions` | **Desliga o freio.** Só dentro de contêiner ([`24`](24-seguranca.md)) |

> **Nota sobre `--bare`:** ele não lê credenciais OAuth. Comprovado nesta máquina: rodar
> `claude --bare -p "…"` com login por assinatura devolveu
> `{"is_error":true,…,"result":"Not logged in · Please run /login"}`. Em `--bare`, defina
> `ANTHROPIC_API_KEY`. A documentação avisa que `--bare` deve virar o padrão de `-p` no futuro.

---

## 2. Comandos de barra, por tarefa

Digitados no **começo** da mensagem. `/help` lista os da sua versão.

### 2.1 Conversa e contexto — os que mais importam

| Comando | O que faz | Quando usar |
|---|---|---|
| `/clear [nome]` | Zera o contexto e começa conversa nova | **Toda vez que muda de assunto** |
| `/compact [instruções]` | Resume o histórico para liberar espaço | Perto do limite, mas quer continuar a mesma tarefa |
| `/context [all]` | Mostra, em grade colorida, o que ocupa o contexto | Quando está lento, caro ou "esquecendo" |
| `/usage` (= `/cost`) | Uso de tokens, custo e barras do plano | Controle de gasto |
| `/resume [nome]` | Volta a uma conversa anterior | Retomar trabalho de ontem |
| `/rewind [turnos\|nome]` | **Desfaz código e conversa** até um checkpoint | Errou feio |
| `/branch [nome]` | Ramifica a conversa para tentar outro caminho | Explorar alternativa sem perder o atual |
| `/fork [prompt]` | Copia a conversa para uma sessão em background | Paralelizar |
| `/btw [pergunta]` | Pergunta paralela que **não** entra no contexto | Dúvida lateral sem poluir |
| `/recap` / `/status` | Resumo da sessão / estado atual | Retomar depois de um café |
| `/export [arquivo]` | Exporta a conversa em texto | Registro, auditoria |
| `/copy [N]` | Copia a última resposta | — |

### 2.2 Trabalho

| Comando | O que faz |
|---|---|
| `/plan [descrição]` | Entra em modo plano (só leitura, propõe antes de agir) |
| `/goal [condição\|clear]` | Define um objetivo que persiste entre turnos |
| `/diff` | Visualizador interativo das mudanças não commitadas |
| `/review`, `/code-review [nível] [--fix] [--comment] [alvo]` | Revisão de diff ou PR |
| `/security-review` | Varredura de segurança no diff do branch |
| `/verify [--fix]` | Verificação de correção do código |
| `/simplify` | Limpeza: reuso, simplificação, eficiência |
| `/subtask [prompt]` | Entrega um trabalho lateral a um subagente |
| `/tasks` | Lista trabalhos em segundo plano |
| `/background [prompt]` | Manda a sessão atual para segundo plano |
| `/batch <instrução>` | Mudança em larga escala, decomposta em worktrees paralelos |
| `/loop [intervalo] [prompt]` | Repete um prompt em intervalo |
| `/deep-research <pergunta>` | Pesquisa na web com várias frentes e síntese citada |

### 2.3 Configuração e extensão

| Comando | O que faz |
|---|---|
| `/config` (= `/settings`), `/config chave=valor` | Interface de configuração |
| `/permissions` | Regras de allow / ask / deny |
| `/model [modelo]` | Troca o modelo e salva como padrão |
| `/effort` | Nível de esforço de raciocínio |
| `/fast [on\|off]` | Modo rápido (mesmo Opus, saída mais veloz) |
| `/memory` | Edita `CLAUDE.md` e gerencia memória automática |
| `/init` | Gera o `CLAUDE.md` inicial analisando o repositório |
| `/agents` | Configuração de subagentes |
| `/hooks` | Ver os hooks configurados |
| `/mcp [reconnect\|enable\|disable]` | Servidores MCP |
| `/plugin [subcomando]` | Plugins |
| `/reload-skills`, `/reload-plugins [--force]` | Recarrega sem reiniciar |
| `/add-dir <caminho>`, `/cd <caminho>` | Amplia / muda o diretório de trabalho |
| `/keybindings` | Abre o arquivo de atalhos |
| `/doctor` | Diagnóstico com correções sugeridas |
| `/insights` | Relatório HTML sobre como você tem usado a ferramenta |
| `/fewer-permission-prompts` | Analisa o histórico e propõe lista de permissões |

### 2.4 Integrações e utilidades

| Comando | O que faz |
|---|---|
| `/ide` | Integração com o editor |
| `/install-github-app` | Instala o app do GitHub no repositório |
| `/install-slack-app` | Instala o app do Slack |
| `/chrome` | Integração com o Chrome |
| `/remote-control [detach]`, `/desktop`, `/teleport`, `/mobile`, `/web` | Mover a sessão entre dispositivos e superfícies |
| `/autofix-pr [prompt]` | Sessão na web que vigia um PR e empurra correções |
| `/login`, `/logout`, `/privacy-settings` | Conta e privacidade |
| `/release-notes`, `/feedback`, `/exit` | Miscelânea |
| `/powerup` | Lições interativas sobre recursos |

### 2.5 Prefixos de entrada

| Prefixo | Efeito |
|---|---|
| `/` no começo | Comando ou skill |
| `!` no começo | **Modo shell**: roda o comando e coloca a saída no contexto |
| `@` | Autocompletar de caminho de arquivo — inclui o arquivo na mensagem |
| `#` no começo | Atalho para gravar algo na memória |
| `:` | Emoji por código (`:rocket:`) |
| `?` com entrada vazia | Painel de atalhos |

> `!npm test` é subestimado: você roda, o agente vê a saída, e **nenhuma permissão de
> ferramenta foi gasta** — porque quem rodou foi você.

---

## 3. Atalhos de teclado

### Gerais

| Atalho | O que faz |
|---|---|
| `Esc` | **Interrompe o Claude**, ou fecha diálogo |
| `Esc` `Esc` | Limpa o rascunho, ou rebobina (`/rewind`) |
| `Shift+Tab` | Alterna modos de permissão (`Alt+M` em certos Windows) |
| `Ctrl+C` | Interrompe, ou limpa a entrada |
| `Ctrl+D` | Sai da sessão |
| `Ctrl+L` | Redesenha a tela |
| `Ctrl+O` | Abre/fecha o visualizador de transcrição |
| `Ctrl+R` | Busca reversa no histórico |
| `Ctrl+G` ou `Ctrl+X Ctrl+E` | Abre a entrada no seu editor |
| `Ctrl+T` | Mostra/esconde a lista de tarefas do Claude |
| `Ctrl+B` | Manda tarefas para segundo plano |
| `Ctrl+S` | Guarda/restaura o rascunho do prompt |
| `Ctrl+V` (`Cmd+V` no iTerm2, `Alt+V` no Windows/WSL) | Cola **imagem** da área de transferência |
| `Ctrl+X Ctrl+K` | Para todos os subagentes em segundo plano |
| `Option/Alt+P` | Troca de modelo |
| `Option/Alt+T` | Liga/desliga raciocínio estendido |
| `Option/Alt+O` | Liga/desliga o modo rápido |
| `↑` / `↓` | Histórico de comandos |

### Edição de linha (estilo readline)

| Atalho | O que faz |
|---|---|
| `Ctrl+A` / `Ctrl+E` | Começo / fim da linha |
| `Ctrl+K` / `Ctrl+U` | Apaga até o fim / até o começo |
| `Ctrl+W` | Apaga a palavra anterior |
| `Ctrl+Y` | Cola o que foi apagado |
| `Alt+B` / `Alt+F` | Palavra para trás / para frente |
| `Ctrl+_` | Desfaz a última edição da entrada |

> No macOS, os atalhos com `Alt/Option` exigem configurar **Option como Meta** no terminal.

### Modo vim

Ative com `editorMode: "vim"` no `settings.json` ou `/config`. Suporta `Esc`, `i`, `I`,
`a`, `A`, `o`, `O`, `v`, `V`, movimentos `h j k l w e b 0 $ ^ gg G`, e operadores usuais.

### Visualizador de transcrição (`Ctrl+O`)

| Tecla | O que faz |
|---|---|
| `?` | Painel de atalhos |
| `{` / `}` | Pula para o prompt anterior / seguinte |
| `[` | Escreve a conversa no scrollback nativo do terminal (permite `Cmd+F`) |
| `v` | Abre a conversa no `$EDITOR` |
| `q`, `Esc` | Sai |

### Entrada de várias linhas

| Como | Onde funciona |
|---|---|
| `\` + `Enter` | Todos os terminais |
| `Option+Enter` | macOS |
| `Shift+Enter` | Depois de `/terminal-setup` |

---

## 4. Ferramentas embutidas

O que o agente pode fazer. Os nomes são **exatamente** as strings usadas em regras de
permissão, listas de ferramentas de subagentes e matchers de hooks.

| Ferramenta | O que faz | Pede permissão? |
|---|---|---|
| `Read` | Lê arquivos (texto, imagem, PDF, notebook) | Não, dentro do diretório de trabalho |
| `Glob` | Encontra arquivos por padrão | Não (idem) |
| `Grep` | Busca conteúdo (ripgrep) | Não (idem) |
| `Edit` | Edição pontual em arquivo existente | **Sim** |
| `Write` | Cria ou sobrescreve arquivo | **Sim** |
| `NotebookEdit` | Edita células de Jupyter | **Sim** |
| `Bash` | Executa comandos de shell | **Sim** (há um conjunto embutido só-leitura que passa direto) |
| `PowerShell` | Idem, em PowerShell (Windows) | **Sim** |
| `WebFetch` | Busca uma URL e responde sobre ela | **Sim** |
| `WebSearch` | Busca na web | **Sim** |
| `Agent` | Cria um subagente ([`19`](19-subagentes.md)) | Não |
| `Skill` | Executa uma skill ([`18`](18-skills-e-comandos.md)) | Não |
| `Task*` (`TaskCreate/List/Get/Update/Stop/Output`) | Fila de tarefas e trabalhos em background | Não |
| `TodoWrite` | Lista de afazeres da sessão | Não |
| `AskUserQuestion` | Faz pergunta de múltipla escolha a você | — |
| `EnterPlanMode` / `ExitPlanMode` | Entra/sai do modo plano | — |
| `EnterWorktree` / `ExitWorktree` | Worktree git isolado ([`22`](22-git-github-e-ci.md)) | — |
| `Monitor` | Roda comando em segundo plano e observa | **Sim** |
| `LSP` | Inteligência de código via language server | Não |
| `ToolSearch` | Carrega sob demanda o esquema de ferramentas adiadas (MCP) | Não |
| `SendMessage` / `ListAgents` | Fala com outras sessões e subagentes | — |
| `Cron*` (`Create/List/Delete`) | Tarefas agendadas | **Sim** |
| `WebFetch`/`WebSearch`/`Artifact`/`PushNotification`/`SendUserFile` | Saída para fora da máquina | **Sim** |
| `mcp__<servidor>__<ferramenta>` | Ferramentas de servidores MCP | **Sim**, por padrão |

Detalhes de custo e de escolha em [`14-ferramentas.md`](14-ferramentas.md).

---

## 5. Sintaxe de regras de permissão

Usada em `settings.json`, em `--allowedTools`, no campo `if` de hooks e em `/permissions`.

```
NomeDaFerramenta(padrão)
```

| Regra | Casa com |
|---|---|
| `Read` | qualquer uso da ferramenta |
| `Bash(npm test)` | **exatamente** `npm test` |
| `Bash(npm run test *)` | qualquer coisa começando com `npm run test ` |
| `Bash(git diff*)` | também casa `git diff-index` — **o espaço antes do `*` importa** |
| `Edit(./src/**)` | arquivos sob `src/` do diretório de trabalho |
| `Edit(**/src/**)` | `src/` em qualquer profundidade |
| `Read(./.env)` | um arquivo específico |
| `mcp__github__*` | todas as ferramentas de um servidor MCP |

Regras de ouro:

1. **`deny` vence `allow`**, sempre, em qualquer escopo.
2. Regras **somam** entre escopos (usuário + projeto + local + gerenciado), em vez de substituir.
3. Comandos encadeados (`a && b`) são avaliados **um a um**; o conteúdo de `$(...)` e de
   crases também é verificado.

---

## 6. Variáveis de ambiente

| Variável | Efeito |
|---|---|
| `ANTHROPIC_API_KEY` | Autenticação por chave |
| `DISABLE_AUTOUPDATER=1` | Congela a versão |
| `DISABLE_AUTO_COMPACT=1` | Desliga a compactação automática |
| `CLAUDE_CODE_AUTO_COMPACT_WINDOW` | Limiar de compactação, em tokens |
| `MAX_THINKING_TOKENS` | Teto de raciocínio (modelos de orçamento fixo) |
| `CLAUDE_CODE_EFFORT_LEVEL` | Esforço padrão |
| `CLAUDE_CODE_ENABLE_TELEMETRY=1` + `OTEL_*` | Métricas ([`26`](26-times-e-escala.md)) |
| `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1` | Desliga a memória automática |
| `CLAUDE_CODE_DISABLE_BUNDLED_SKILLS=1` | Desliga as skills embutidas |
| `CLAUDE_CODE_USE_POWERSHELL_TOOL=1` | Habilita a ferramenta PowerShell |
| `CLAUDE_CODE_GIT_BASH_PATH` | Caminho do Git Bash no Windows |
| `USE_BUILTIN_RIPGREP=0` | Usa o ripgrep do sistema (musl) |
| `HTTPS_PROXY`, `NO_PROXY`, `NODE_EXTRA_CA_CERTS` | Rede corporativa |
| `ENABLE_PROMPT_CACHING_1H=1` | Mantém cache de 1 h ao usar créditos de uso |

Dentro de hooks, ainda existem `CLAUDE_PROJECT_DIR`, `CLAUDE_PLUGIN_ROOT`,
`CLAUDE_PLUGIN_DATA`, `CLAUDE_EFFORT`, `CLAUDE_CODE_REMOTE`.

---

## 7. Obsoleto ou renomeado — não use

| Antigo | Situação | Use |
|---|---|---|
| `--enable-auto-mode` | **Removido** na 2.1.111 | `--permission-mode auto` |
| `--remote` | Apelido obsoleto | `--cloud` |
| `/ultrareview` | Apelido obsoleto | `/code-review ultra` |
| `.claude/commands/*.md` | **Não** obsoleto, mas superado | `.claude/skills/<nome>/SKILL.md` — faz o mesmo e mais ([`18`](18-skills-e-comandos.md)) |
| Assistente interativo do `/agents` | Removido na 2.1.198 | Peça ao Claude, ou escreva o `.md` à mão |
| `npm update -g @anthropic-ai/claude-code` | Respeita a faixa semver e pode não atualizar | `npm install -g @anthropic-ai/claude-code@latest` |

---

## 8. Atalhos que só quem usa há tempo conhece

1. **`!comando`** roda no seu shell e injeta a saída no contexto — sem gastar permissão de
   ferramenta e sem o agente decidir o comando. Ótimo para dar exatamente o dado que ele precisa.
2. **`/btw`** faz uma pergunta paralela que não entra no contexto da tarefa. Para quando você
   quer saber algo sem sujar a sessão.
3. **`Esc` `Esc`** rebobina **código e conversa** — é diferente de `git checkout`, porque
   também tira da cabeça do modelo o caminho errado que ele tomou.
4. **`--fork-session`** ao retomar: você continua uma sessão sem contaminá-la, e pode voltar
   à original depois.
5. **`/compact <instruções>`** aceita instruções: `/compact foque nas decisões de API e nos
   testes` preserva o que importa e joga fora o resto.
6. **`/context all`** mostra a grade completa, inclusive o custo das definições de
   ferramentas MCP. É o diagnóstico que revela por que sua sessão está cara.
7. **`Ctrl+O`, depois `[`** joga a conversa no scrollback nativo do terminal — aí `Cmd+F`,
   `tmux copy-mode` e afins passam a funcionar.
8. **`claude -n "nome"`** nomeia a sessão; `claude -r "nome"` retoma sem caçar UUID.
9. **`/insights`** gera um relatório HTML sobre os seus próprios padrões de uso: onde você
   perde tempo, o que costuma dar errado. Vale rodar uma vez por mês.
10. **`--max-budget-usd`** em qualquer automação. Um laço agêntico sem teto num script de CI
    é uma fatura esperando para acontecer.

---

## Fontes consultadas

- *Commands reference*: https://code.claude.com/docs/en/commands (13/08/2026)
- *CLI reference*: https://code.claude.com/docs/en/cli-reference (13/08/2026)
- *Interactive mode*: https://code.claude.com/docs/en/interactive-mode (13/08/2026)
- *Tools reference*: https://code.claude.com/docs/en/tools-reference (13/08/2026)
- *Settings*: https://code.claude.com/docs/en/settings (13/08/2026)
- Verificação local: `claude --version` → `2.1.231 (Claude Code)`; comportamento de
  `--bare` sem `ANTHROPIC_API_KEY` reproduzido nesta máquina em 13/08/2026.

---

## Autoteste

1. Qual é a fonte da verdade sobre os comandos da **sua** versão, e por que não este arquivo?
2. Explique a diferença entre `/clear` e `/compact`. Quando cada um?
3. O que `--bare` desliga, e qual é a pegadinha de autenticação que ele traz?
4. `Bash(git diff *)` e `Bash(git diff*)` — qual a diferença e por que ela importa?
5. Se `allow` e `deny` conflitam, quem vence? E entre escopos, o que acontece?
6. Para que serve o prefixo `!`, e qual a vantagem sobre pedir ao agente para rodar o comando?
7. Cite três comandos removidos ou renomeados e seus substitutos.
8. Qual comando mostra por que sua sessão está cara?
