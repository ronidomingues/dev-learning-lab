# 16 · Configuração — `settings.json` e a hierarquia

> **Nível:** intermediário · **Atualizado em:** 13/08/2026 · Claude Code 2.1.231

Configuração de agente é código que ninguém compila. Ela falha em silêncio, e o sintoma é
sempre o mesmo: *"o Claude ignora o que eu configurei"*. Este arquivo cobre onde as coisas
ficam, quem vence quem, e como diagnosticar.

---

## 1. A hierarquia — quem vence quem

Do mais forte para o mais fraco:

| # | Escopo | Onde | Quem controla |
|---|---|---|---|
| 1 | **Gerenciado** | `/etc/claude-code/managed-settings.json` (Linux/WSL) · `/Library/Application Support/ClaudeCode/` (macOS) · `C:\Program Files\ClaudeCode\` · plist/registro/MDM · gateway | TI da organização |
| 2 | **Linha de comando** | `--settings`, `--permission-mode`, `--model`… | quem invoca |
| 3 | **Local do projeto** | `.claude/settings.local.json` | você, neste repositório (**no `.gitignore`**) |
| 4 | **Projeto** | `.claude/settings.json` | o time, versionado |
| 5 | **Usuário** | `~/.claude/settings.json` | você, em todos os projetos |

**Exceção que importa:** regras de permissão **somam** entre escopos em vez de substituir, e
configurações sensíveis à segurança honram o valor mais restritivo. Ou seja: você não anula
um `deny` da organização escrevendo `allow` no projeto.

Também há um drop-in `managed-settings.d/` com vários `*.json` mesclados em ordem alfabética
— útil para distribuir política por partes.

---

## 2. Onde fica cada tipo de coisa

| Recurso | Usuário | Projeto | Local |
|---|---|---|---|
| Configurações | `~/.claude/settings.json` | `.claude/settings.json` | `.claude/settings.local.json` |
| Subagentes | `~/.claude/agents/` | `.claude/agents/` | — |
| Skills | `~/.claude/skills/` | `.claude/skills/` | — |
| Comandos (formato antigo) | `~/.claude/commands/` | `.claude/commands/` | — |
| Regras | `~/.claude/rules/` | `.claude/rules/` | — |
| Servidores MCP | `~/.claude.json` | `.mcp.json` | `~/.claude.json` (por projeto) |
| Memória | `~/.claude/CLAUDE.md` | `CLAUDE.md` ou `.claude/CLAUDE.md` | `CLAUDE.local.md` |

**O que versionar:** `.claude/settings.json`, `.claude/agents/`, `.claude/skills/`,
`.claude/rules/`, `.mcp.json`, `CLAUDE.md`.
**O que não versionar:** `.claude/settings.local.json`, `CLAUDE.local.md`.

Modelo de `.gitignore`:

```gitignore
.claude/settings.local.json
.claude/agent-memory-local/
CLAUDE.local.md
```

---

## 3. As chaves que realmente importam

Existem dezenas. Estas são as que mudam o dia a dia.

### Modelo e esforço

```json
{
  "model": "claude-sonnet-5",
  "effortLevel": "high",
  "fallbackModel": ["claude-sonnet-5", "claude-haiku-4-5"],
  "availableModels": ["sonnet", "haiku"],
  "fastMode": true
}
```

`effortLevel` (`low` … `xhigh`) controla o raciocínio estendido: mais esforço, melhor
resultado em tarefa difícil, mais tokens de saída. `availableModels` é típica de organização
que quer conter custo. `fastMode` acelera a saída sem trocar de modelo.

### Permissões — ver [`15`](15-permissoes-e-modos.md)

```json
{
  "permissions": {
    "defaultMode": "acceptEdits",
    "allow": ["Bash(npm test)"],
    "ask": ["Bash(git push *)"],
    "deny": ["Read(./.env)", "Bash(curl *)"],
    "additionalDirectories": ["../biblioteca"]
  }
}
```

### Contexto e memória

```json
{
  "autoCompactEnabled": true,
  "autoCompactWindow": 500000,
  "autoMemoryEnabled": true,
  "claudeMdExcludes": ["**/monorepo/outro-time/CLAUDE.md"]
}
```

`claudeMdExcludes` salva vidas em monorepo: sem ele, os `CLAUDE.md` de todos os times acima
de você na árvore entram no seu contexto.

### Hooks — ver [`17`](17-hooks.md)

```json
{
  "hooks": {
    "PostToolUse": [{
      "matcher": "Edit|Write",
      "hooks": [{ "type": "command", "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/testar.sh", "args": [] }]
    }]
  }
}
```

### Ambiente

```json
{
  "env": {
    "DISABLE_AUTOUPDATER": "1",
    "CLAUDE_CODE_ENABLE_TELEMETRY": "1",
    "NODE_EXTRA_CA_CERTS": "/etc/ssl/certs/empresa.pem"
  }
}
```

O bloco `env` vale para todas as sessões, inclusive as abertas pelo editor — vantagem real
sobre exportar no `.bashrc`.

### Interface e sessão

```json
{
  "editorMode": "vim",
  "fileCheckpointingEnabled": true,
  "cleanupPeriodDays": 30,
  "autoUpdatesChannel": "stable",
  "minimumVersion": "2.1.200",
  "attribution": { "commit": "", "pr": "" }
}
```

`attribution` remove (ou personaliza) a linha de coautoria nos commits — pergunta frequente,
resposta de uma linha.

### Desligar coisas (times e ambientes restritos)

```json
{
  "disableBundledSkills": false,
  "disableAllHooks": false,
  "disableAgentView": false,
  "allowManagedPermissionRulesOnly": false,
  "disableSideloadFlags": true
}
```

`disableSideloadFlags` (só em configuração gerenciada) rejeita `--plugin-dir`,
`--plugin-url`, `--agents` e `--mcp-config` — impede que alguém injete configuração pela
linha de comando.

---

## 4. Validação e autocompletar

Ponha isto no topo de todo `settings.json`:

```json
{ "$schema": "https://json.schemastore.org/claude-code-settings.json" }
```

Seu editor passa a validar as chaves e a autocompletar. É a defesa mais barata contra o erro
de digitar `permission` em vez de `permissions` e não receber aviso nenhum.

---

## 5. O que recarrega sozinho e o que exige reiniciar

| Recarrega no meio da sessão | Só na abertura |
|---|---|
| `permissions` | `model` (use `/model` para trocar na hora) |
| `hooks` | `outputStyle` |
| `apiKeyHelper` e ajudantes de credencial | |
| Skills e agentes (com `/reload-skills`) | |

Esta tabela evita a confusão mais comum de depuração: você muda o modelo no arquivo, nada
acontece, e conclui que a configuração não funciona.

---

## 6. Depurar configuração

Ordem de diagnóstico, do mais barato ao mais caro:

```bash
claude doctor            # 1. erros de validação, chaves inválidas, saúde da instalação
```
```
/status                  # 2. quais fontes de configuração estão ativas nesta sessão
/context                 # 3. quais arquivos de memória carregaram de verdade
/permissions             # 4. regras efetivas depois da fusão de escopos
/hooks                   # 5. hooks realmente registrados
```
```bash
claude --debug='startup' # 6. o que aconteceu na inicialização
```

E, para o que nenhum desses cobre, o validador do projeto-modelo:

```bash
cd claude-code/07-projeto-modelo && npm run verificar
```

Ele checa exatamente as falhas silenciosas: JSON inválido, hook inexistente, hook sem
`chmod +x`, hook sem shebang, skill sem `description`, agente com `name` inválido, `deny`
vazio, `CLAUDE.md` inchado. Saída real em 13/08/2026: **17 verificações ok, 0 problemas**.

### As sete falhas silenciosas mais comuns

| Sintoma | Causa | Diagnóstico |
|---|---|---|
| Nada da minha configuração vale | JSON inválido (vírgula sobrando) | `claude doctor` |
| O hook não roda | Sem `chmod +x`, ou sem shebang | `npm run verificar` do projeto-modelo |
| O hook não roda (2) | Matcher errado (`bash` em vez de `Bash`) | `/hooks` |
| A skill não aparece | Falta `description`, ou pasta errada | `/reload-skills`, depois `/help` |
| O agente não é chamado | `name` com maiúscula, espaço ou `:` | `npm run verificar` |
| Meu `deny` não pegou | Escreveu no escopo errado, ou padrão sem `./` | `/permissions` |
| Mudei o modelo e nada | `model` só é lido na abertura | `/model` |

---

## 7. Configuração recomendada para começar

**Usuário — `~/.claude/settings.json`:**

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "permissions": {
    "deny": [
      "Read(./.env)", "Read(./.env.*)", "Read(./**/*.pem)",
      "Bash(rm -rf /*)", "Bash(curl * | sh)", "Bash(curl * | bash)"
    ]
  },
  "autoUpdatesChannel": "stable",
  "editorMode": "normal"
}
```

**Projeto — `.claude/settings.json`** (exemplo completo e verificado em
[`07-projeto-modelo/.claude/settings.json`](07-projeto-modelo/.claude/settings.json)):

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "permissions": {
    "allow": ["Bash(npm test)", "Bash(npm run lint)", "Bash(git diff *)", "Bash(git status *)"],
    "ask": ["Bash(git push *)"],
    "deny": ["Bash(npm install *)", "Read(./.env)"]
  },
  "hooks": {
    "PostToolUse": [{
      "matcher": "Edit|Write",
      "hooks": [{ "type": "command", "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/testar.sh", "args": [], "timeout": 120 }]
    }]
  }
}
```

Comece por aí. Acrescente quando a dor aparecer, não antes — configuração especulativa
envelhece mal e ninguém do time entende por que ela existe.

---

## Autoteste

1. Ordene os cinco escopos de configuração. Qual é a exceção à regra de precedência?
2. O que versionar e o que colocar no `.gitignore`?
3. Para que serve `claudeMdExcludes`, e em que tipo de repositório é indispensável?
4. Qual chave muda no meio da sessão e qual exige reinício? Dê um exemplo de cada.
5. Qual é a vantagem do bloco `env` sobre exportar no `.bashrc`?
6. Cite quatro falhas silenciosas de configuração e como diagnosticar cada uma.
7. Por que `$schema` no topo do arquivo economiza tempo?
8. O que `disableSideloadFlags` impede, e por que uma organização iria querer isso?
