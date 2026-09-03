# 17 · Hooks — como fazer o agente obedecer de verdade

> **Nível:** intermediário → avançado · **Atualizado em:** 13/08/2026 · Claude Code 2.1.231

Hook é o único mecanismo com **garantia**. Tudo o mais — `CLAUDE.md`, skills, prompt de
sistema — é influência sobre um processo probabilístico. Hook é código que o Claude Code
executa em pontos fixos do ciclo de vida, independentemente do que o modelo decidiu.

> **A frase que resume o arquivo:** *contexto pede, permissão restringe, **hook obriga**.*

---

## 1. Anatomia

Três níveis de aninhamento:

```json
{
  "hooks": {
    "PostToolUse": [                              // 1. EVENTO
      {
        "matcher": "Edit|Write",                  // 2. FILTRO
        "hooks": [
          {                                       // 3. HANDLER
            "type": "command",
            "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/testar.sh",
            "args": [],
            "timeout": 120,
            "statusMessage": "rodando a suíte"
          }
        ]
      }
    ]
  }
}
```

Onde podem ser definidos: `~/.claude/settings.json` (você, todos os projetos),
`.claude/settings.json` (time, versionado), `.claude/settings.local.json` (você, aqui),
configuração gerenciada (organização), plugins (`hooks/hooks.json`), e no **frontmatter de
skills e subagentes** — nesse caso valem só enquanto aquele componente estiver ativo.

---

## 2. Eventos — os que importam primeiro

Existem cerca de trinta. Estes cinco resolvem 90% dos casos reais:

| Evento | Quando | Pode bloquear? | Uso canônico |
|---|---|---|---|
| **`PreToolUse`** | antes de executar uma ferramenta | **Sim** | negar acesso a segredo; reescrever comando |
| **`PostToolUse`** | depois de a ferramenta ter sucesso | Não (já rodou) | rodar teste/linter e **devolver o erro ao modelo** |
| **`SessionStart`** | ao abrir ou retomar | Não | injetar estado do repositório no contexto |
| **`UserPromptSubmit`** | ao enviar sua mensagem | **Sim** | injetar contexto automático; barrar prompts |
| **`Stop`** | quando o Claude vai terminar | **Sim** | exigir que uma condição seja cumprida antes de parar |

Os demais, por família:

- **Sessão**: `Setup`, `SessionEnd`, `PreCompact`, `PostCompact`, `ConfigChange`,
  `InstructionsLoaded`, `CwdChanged`, `DirectoryAdded`, `FileChanged`.
- **Ferramentas**: `PostToolUseFailure`, `PostToolBatch`, `PermissionRequest`, `PermissionDenied`.
- **Subagentes e tarefas**: `SubagentStart`, `SubagentStop`, `TaskCreated`, `TaskCompleted`, `TeammateIdle`.
- **Outros**: `Notification`, `MessageDisplay`, `StopFailure`, `UserPromptExpansion`,
  `WorktreeCreate`, `WorktreeRemove`, `Elicitation`, `ElicitationResult`.

---

## 3. Matchers

O campo `matcher` filtra quando o hook dispara. **A avaliação depende dos caracteres usados**:

| Valor | Interpretado como |
|---|---|
| `"*"`, `""` ou ausente | casa tudo |
| Só letras, dígitos, `_`, `-`, espaço, `,`, `\|` | string exata ou lista: `Bash`, `Edit\|Write` |
| Contém outros caracteres | **regex JavaScript**, sem âncora: `^Notebook`, `mcp__memory__.*` |

Contra o que cada evento casa:

| Evento | Casa contra | Exemplos |
|---|---|---|
| `PreToolUse`, `PostToolUse`, `PermissionRequest` | nome da ferramenta | `Bash`, `Edit\|Write`, `mcp__.*` |
| `SessionStart` | como a sessão começou | `startup`, `resume`, `clear`, `compact`, `fork` |
| `SessionEnd` | por que terminou | `clear`, `logout`, `prompt_input_exit`, … |
| `SubagentStart/Stop` | tipo do agente | `Explore`, `Plan`, nomes customizados |
| `PreCompact`/`PostCompact` | o que disparou | `manual`, `auto` |
| `FileChanged` | nomes literais de arquivo | `.envrc\|.env` |
| `Notification` | tipo | `permission_prompt`, `idle_prompt`, `agent_completed` |
| `UserPromptSubmit`, `Stop`, `PostToolBatch` | — (sempre dispara) | |

**Erro nº 1 de matcher:** escrever `bash` em vez de `Bash`. É sensível a maiúsculas, e
falha em silêncio.

Filtro fino, sem regex, com a sintaxe de regras de permissão:

```json
{ "type": "command", "if": "Bash(rm *)", "command": "…", "args": [] }
```

---

## 4. Os cinco tipos de handler

| Tipo | O que é | Quando usar |
|---|---|---|
| `command` | script/binário; JSON no `stdin`, decisão no `stdout` | **quase sempre** |
| `http` | POST para uma URL; a resposta usa o mesmo esquema | política centralizada de organização |
| `mcp_tool` | chama ferramenta de um servidor MCP conectado | integração existente |
| `prompt` | um modelo rápido avalia e devolve sim/não | julgamento que regra fixa não expressa |
| `agent` | subagente com ferramentas decide | casos complexos (experimental) |

### Forma exec × forma shell — a pegadinha

```json
{ "type": "command", "command": "node", "args": ["${CLAUDE_PROJECT_DIR}/scripts/x.js", "--fix"] }
```
> **Forma exec** (com `args`): sem shell. Sem pipes, sem `&&`, sem globs. Mais previsível e
> mais seguro. Caminhos com espaço funcionam sem aspas.

```json
{ "type": "command", "command": "node \"${CLAUDE_PROJECT_DIR}\"/scripts/x.js --fix | tee /tmp/log" }
```
> **Forma shell** (sem `args`): passa pelo shell. Pipes e redirecionamentos funcionam.
> **Aspas duplas nos caminhos são obrigatórias**, ou um espaço no caminho quebra tudo.

Recomendação: prefira **exec** e ponha a complexidade dentro do script.

Campos úteis em qualquer handler: `timeout` (padrão 600 s; 30 s em `prompt`), `async` (não
bloqueia), `asyncRewake` (roda em background e acorda o Claude se sair com 2), `statusMessage`,
`shell` (`bash` ou `powershell`), `if`.

---

## 5. O contrato: entrada, saída, código de retorno

### Entrada (`stdin`, JSON)

```json
{
  "session_id": "abc123",
  "transcript_path": "/home/user/.claude/projects/.../transcript.jsonl",
  "cwd": "/home/user/projeto",
  "permission_mode": "default",
  "hook_event_name": "PreToolUse",
  "tool_name": "Bash",
  "tool_input": { "command": "npm test", "description": "Roda os testes" },
  "tool_use_id": "toolu_01ABC..."
}
```

### Códigos de saída — a tabela que evita horas de confusão

| Código | Significado | Comportamento |
|---|---|---|
| **0** | sucesso | `stdout` vai para o log de depuração. **Exceções:** em `UserPromptSubmit`, `UserPromptExpansion` e `SessionStart`, o `stdout` entra no **contexto do Claude** |
| **2** | erro **bloqueante** | Bloqueia nos eventos que suportam bloqueio. O `stderr` vai **para o Claude** |
| 1, 3, … | depende do `stdout` | Se houver JSON válido, a decisão é honrada; senão, erro não bloqueante e a ação segue |

> **`exit 1` NÃO bloqueia.** Este é o erro mais comum de quem escreve hook pela primeira vez:
> a convenção Unix diz que 1 é falha, mas aqui o único código que bloqueia sozinho é o **2**.

### Saída JSON

Campos universais:

```json
{
  "continue": false,
  "stopReason": "Build quebrado",
  "systemMessage": "aviso mostrado a você",
  "terminalSequence": "]9;4;;0"
}
```

Decisão em `PreToolUse`:

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "Arquivo protegido."
  }
}
```

Reescrever a entrada da ferramenta (o truque mais subestimado):

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "allow",
    "updatedInput": { "command": "npm test 2>&1 | tail -40" }
  }
}
```

**Limite:** saídas de hook são cortadas em **10 mil caracteres**; acima disso, vão para
arquivo e o Claude recebe um preview com o caminho.

---

## 6. Os quatro hooks que valem a pena — testados

### 6.1 Bloquear escrita em segredo (`PreToolUse`)

Código completo e **executado** em
[`07-projeto-modelo/.claude/hooks/bloqueia-segredos.sh`](07-projeto-modelo/.claude/hooks/bloqueia-segredos.sh).

Saída real, com evento simulado, em 13/08/2026:

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "Arquivo de segredo (/home/x/projeto/.env) e protegido pelo hook bloqueia-segredos.sh."
  }
}
```

Com um caminho legítimo (`src/tarefas.js`), o hook não imprimiu nada e saiu com 0 — "sem
decisão, siga o fluxo normal".

### 6.2 Rodar a suíte depois de editar (`PostToolUse`) — **o de maior impacto**

Código completo em
[`07-projeto-modelo/.claude/hooks/testa-apos-edicao.sh`](07-projeto-modelo/.claude/hooks/testa-apos-edicao.sh).

Verificado nesta máquina: quebrando de propósito a prioridade padrão em `src/tarefas.js`,
o hook saiu com código 2 e entregou ao agente:

```
A suite quebrou depois de editar .../src/tarefas.js. Conserte antes de seguir.
--- saida do node --test (ultimas 40 linhas) ---
✖ cria tarefa com valores padrão (3.81658ms)
  AssertionError: 'baixa' !== 'media'
ℹ pass 19
ℹ fail 1
```

**Por que este é o hook que mais muda o resultado do dia:** ele fecha o laço de verificação
**dentro do turno**. Sem ele, quem descobre a quebra é você, minutos depois, e o agente já
perdeu o contexto do que fez. Com ele, o agente vê e conserta antes de responder.

Se a suíte for lenta, três saídas: rodar só os testes do arquivo tocado; usar `async: true`
com `asyncRewake: true`; ou trocar por `tsc --noEmit`/linter, que são mais rápidos.

### 6.3 Contexto do repositório na abertura (`SessionStart`)

Em `SessionStart`, o `stdout` **entra no contexto**. Código em
[`07-projeto-modelo/.claude/hooks/contexto-da-sessao.sh`](07-projeto-modelo/.claude/hooks/contexto-da-sessao.sh).

Saída real:

```
## Estado do repositório na abertura da sessão

- Branch: main
- Node: v24.18.0
- Arquivos modificados não commitados: 5
```

**Seja breve.** Cada linha aqui custa contexto em **toda** sessão. Três a cinco linhas é o
ponto ótimo; um `git log -50` aqui é desperdício permanente.

### 6.4 Filtrar saída volumosa (`PreToolUse` com `updatedInput`)

Reescreve `npm test` para mostrar só falhas — receita completa no [`06`](06-exemplos.md),
exemplo 11. Troca 10 mil linhas por 100. É a maior economia de contexto disponível por
15 linhas de bash.

---

## 7. Testar hooks sem abrir sessão — faça isto sempre

O contrato é `stdin` → `stdout` + código. Logo, é testável como qualquer script:

```bash
export CLAUDE_PROJECT_DIR="$PWD"

# deve BLOQUEAR
echo '{"hook_event_name":"PreToolUse","tool_name":"Write",
       "tool_input":{"file_path":"/x/.env"}}' | .claude/hooks/bloqueia-segredos.sh
echo "código de saída: $?"

# deve DEIXAR PASSAR
echo '{"hook_event_name":"PreToolUse","tool_name":"Edit",
       "tool_input":{"file_path":"'"$PWD"'/src/tarefas.js"}}' | .claude/hooks/bloqueia-segredos.sh
echo "código de saída: $?"
```

**Todo hook precisa dos dois testes.** O segundo — o que deve passar — é o que pega o hook
paranoico que bloqueia tudo, e esse é bem mais comum do que o hook permissivo demais.

---

## 8. Armadilhas

| Armadilha | O que acontece | Correção |
|---|---|---|
| Esquecer `chmod +x` | Falha silenciosa | `chmod +x .claude/hooks/*.sh`; valide com o script do projeto-modelo |
| Esquecer o shebang | Idem | `#!/usr/bin/env bash` na primeira linha |
| Usar `exit 1` esperando bloqueio | Não bloqueia | Use `exit 2`, ou JSON de decisão |
| Matcher `bash` minúsculo | Nunca dispara | `Bash` |
| Hook lento em `PostToolUse` | Cada edição custa a suíte inteira | `async`, ou filtre por arquivo |
| Hook que imprime muito | Corte em 10 mil caracteres | `tail -40` |
| Caminho relativo | Falha ao mudar de diretório | `${CLAUDE_PROJECT_DIR}/...` |
| Forma shell sem aspas | Quebra com espaço no caminho | Aspas duplas, ou forma exec com `args` |
| Hook que edita arquivo em `PostToolUse` | O agente não vê a mudança e reescreve por cima | Faça o hook **reportar**, não corrigir em silêncio |

---

## 9. Segurança dos próprios hooks

Hooks executam com **as suas** permissões, sem sandbox e sem confirmação. Um hook malicioso
num repositório clonado é execução arbitrária de código.

Defesas em vigor:

- Hooks de projeto só rodam depois do **diálogo de confiança** do diretório (o mesmo vale
  para hooks em frontmatter de skill/agente, a partir da 2.1.218).
- `disableAllHooks: true` desliga tudo.
- `allowManagedHooksOnly` restringe a hooks da organização.
- Hooks HTTP exigem que a URL case com `allowedHttpHookUrls`.
- Variáveis `OTEL_*` são removidas dos subprocessos.

**Prática recomendada:** ao clonar repositório de terceiros, leia `.claude/settings.json`
**antes** de abrir o Claude Code nele. É o `curl | bash` da era dos agentes — e merece o
mesmo grau de desconfiança.

---

## 10. Os cinco porquês: por que meu hook não roda?

1. **Por que ele não roda?**
   Nove em dez vezes: falta `chmod +x`, falta shebang, ou o matcher está errado.
2. **Por que falha em silêncio em vez de avisar?**
   Porque uma falha de hook não deve derrubar a sessão: o padrão é "erro não bloqueante,
   a ação continua". A mensagem vai para o log de depuração, não para a tela.
3. **Por que não mostrar na tela?**
   Poluição: uma sessão com hooks em vários eventos viraria um mural de avisos. A decisão foi
   privilegiar o fluxo de trabalho.
4. **Como eu vejo, então?**
   `claude --debug` mostra a execução dos hooks; `/hooks` mostra o que está registrado; e o
   validador do projeto-modelo pega as causas mecânicas antes de você abrir a sessão.
5. **Por que isso me custou uma hora?**
   Porque configuração de agente não tem compilador. Foi exatamente por isso que este curso
   traz um validador executável. *(Parada legítima: decisão de projeto sobre ruído × silêncio.)*

---

## Autoteste

1. Enuncie a frase que resume o papel de hooks entre os mecanismos de controle.
2. Cite os cinco eventos mais úteis e um uso real de cada.
3. Por que `exit 1` não bloqueia? Qual código bloqueia?
4. Em quais eventos o `stdout` do hook entra no contexto do Claude?
5. Explique forma exec × forma shell. Qual preferir, e por quê?
6. O que `updatedInput` permite fazer, e por que é a maior economia de contexto disponível?
7. Quais dois testes todo hook deveria ter, e qual problema o segundo pega?
8. Por que um hook não deveria corrigir arquivos em silêncio em `PostToolUse`?
9. Por que ler `.claude/settings.json` antes de abrir o Claude Code num repositório clonado?
