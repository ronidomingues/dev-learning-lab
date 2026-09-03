#!/usr/bin/env bash
# PostToolUse (matcher: Edit|Write) — roda a suíte depois que um arquivo de src/ ou test/
# muda, e devolve a falha *para o Claude*, não para você.
#
# Efeito prático: o agente descobre que quebrou algo no mesmo turno, sem você digitar nada.
# Custo: alguns segundos por edição. Se a suíte for lenta, filtre por arquivo ou use `async`.

set -uo pipefail

entrada="$(cat)"

if command -v jq >/dev/null 2>&1; then
  caminho="$(printf '%s' "$entrada" | jq -r '.tool_input.file_path // ""')"
else
  caminho="$(printf '%s' "$entrada" | grep -o '"file_path"[[:space:]]*:[[:space:]]*"[^"]*"' | head -1 | sed 's/.*:[[:space:]]*"//; s/"$//')"
fi

# Só interessa código do projeto.
case "$caminho" in
  *"/src/"*.js|*"/test/"*.js) ;;
  *) exit 0 ;;
esac

cd "${CLAUDE_PROJECT_DIR:-.}"

saida="$(node --test 2>&1)"
codigo=$?

if [ $codigo -ne 0 ]; then
  # Exit 2 em PostToolUse não bloqueia (o tool já rodou), mas manda o stderr para o Claude.
  {
    echo "A suite quebrou depois de editar $caminho. Conserte antes de seguir."
    echo "--- saida do node --test (ultimas 40 linhas) ---"
    printf '%s\n' "$saida" | tail -40
  } >&2
  exit 2
fi

exit 0
