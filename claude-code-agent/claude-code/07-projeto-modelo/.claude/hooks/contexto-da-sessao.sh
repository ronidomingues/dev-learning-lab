#!/usr/bin/env bash
# SessionStart — o stdout deste hook entra no contexto do Claude.
# Serve para dar ao agente o estado do repositório sem gastar um turno de ferramenta.
#
# Regra de ouro: seja curto. Cada linha aqui é custo de contexto em TODA sessão.

set -uo pipefail
cd "${CLAUDE_PROJECT_DIR:-.}"

echo "## Estado do repositório na abertura da sessão"
echo
echo "- Branch: $(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo 'sem git')"
echo "- Node: $(node --version 2>/dev/null || echo 'ausente')"

sujos="$(git status --porcelain 2>/dev/null | wc -l | tr -d ' ')"
echo "- Arquivos modificados não commitados: ${sujos}"

exit 0
