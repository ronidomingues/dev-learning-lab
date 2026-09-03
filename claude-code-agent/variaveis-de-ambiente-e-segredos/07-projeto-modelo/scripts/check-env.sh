#!/usr/bin/env bash
# Compara as variáveis OBRIGATÓRIAS do .env.example com o ambiente atual.
# Sai com 1 se faltar alguma. Feito para o CI e para o passo anterior ao deploy.
#
# Convenção deste projeto: no .env.example, obrigatória = tem valor de exemplo
# preenchido; opcional = fica vazia, com o padrão anotado em comentário.
#
# Limitação conhecida: a remoção de comentário inline não entende '#' dentro
# de aspas. É aceitável porque isto lê o .env.example, não o .env real.
set -euo pipefail
cd "$(dirname "$0")/.."

EXEMPLO="${1:-.env.example}"
[[ -f "$EXEMPLO" ]] || { echo "não achei $EXEMPLO"; exit 1; }

obrigatorias() {
  sed -E 's/[[:space:]]+#.*$//; s/[[:space:]]+$//' "$1" \
    | grep -Ev '^[[:space:]]*(#|$)' \
    | sed -nE 's/^[[:space:]]*(export[[:space:]]+)?([A-Z][A-Z0-9_]*)=(.+)$/\2/p' \
    | sort -u
}

faltando=()
total=0
while read -r nome; do
  [[ -z "$nome" ]] && continue
  total=$((total + 1))
  var_file="${nome}_FILE"
  if [[ -z "${!nome:-}" && -z "${!var_file:-}" ]]; then
    faltando+=("$nome")
  fi
done < <(obrigatorias "$EXEMPLO")

if (( ${#faltando[@]} )); then
  echo "❌ Variáveis obrigatórias ausentes do ambiente:"
  for nome in "${faltando[@]}"; do
    printf '   • %s (ou %s_FILE)\n' "$nome" "$nome"
  done
  echo
  echo "Consulte $EXEMPLO."
  exit 1
fi
echo "✅ as $total variáveis obrigatórias de $EXEMPLO estão presentes"
