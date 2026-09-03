#!/usr/bin/env bash
# PreToolUse (matcher: Edit|Write) — barreira dura contra escrita em arquivos de segredo.
#
# Por que um hook e não uma linha no CLAUDE.md: CLAUDE.md é *contexto*, o modelo pode
# não seguir. Hook é código, roda sempre, e não depende do que o modelo decidiu.
#
# Contrato: recebe o JSON do evento em stdin; devolve JSON em stdout.
# Ver: https://code.claude.com/docs/en/hooks

set -euo pipefail

entrada="$(cat)"

# jq é o caminho recomendado. Sem jq, cai para um grep suficiente para o caso.
if command -v jq >/dev/null 2>&1; then
  caminho="$(printf '%s' "$entrada" | jq -r '.tool_input.file_path // ""')"
else
  caminho="$(printf '%s' "$entrada" | grep -o '"file_path"[[:space:]]*:[[:space:]]*"[^"]*"' | head -1 | sed 's/.*:[[:space:]]*"//; s/"$//')"
fi

case "$(basename "${caminho:-}")" in
  .env|.env.*|*.pem|*.key|id_rsa|credentials)
    cat <<JSON
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "Arquivo de segredo ($caminho) e protegido pelo hook bloqueia-segredos.sh."
  }
}
JSON
    exit 0
    ;;
esac

# Sem decisão: o fluxo normal de permissão continua.
exit 0
