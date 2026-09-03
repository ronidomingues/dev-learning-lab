#!/usr/bin/env bash
#
# auditar-historico.sh — reprova o histórico se houver commit sem assinatura válida.
#
# Serve para dois usos:
#   1. na sua máquina, para saber em que estado está um repositório;
#   2. na CI, como porta de qualidade — sai com código 1 se algo reprovar.
#
# Uso:
#   ./auditar-historico.sh                      # repositório atual, todo o histórico
#   ./auditar-historico.sh /caminho/do/repo     # outro repositório
#   ./auditar-historico.sh . origin/main..HEAD  # só o intervalo indicado (o normal em CI)
#
# Variáveis de ambiente:
#   ACEITAR_U=1   aceita [U] (assinatura boa, assinante fora do allowed_signers).
#                 Útil em CI, onde você quase nunca tem o allowed_signers montado.
#   IGNORAR_MERGE=1  ignora commits de merge (o servidor cria alguns não assinados).
#
set -uo pipefail

REPO="${1:-.}"
INTERVALO="${2:-HEAD}"
ACEITAR_U="${ACEITAR_U:-0}"
IGNORAR_MERGE="${IGNORAR_MERGE:-0}"

git -C "$REPO" rev-parse --git-dir >/dev/null 2>&1 || {
  echo "erro: '$REPO' não é um repositório Git" >&2; exit 2; }

FILTRO=()
[ "$IGNORAR_MERGE" = "1" ] && FILTRO=(--no-merges)

reprovados=0
total=0

# %H hash · %G? status da assinatura · %an autor · %GS assinante · %s assunto
while IFS='|' read -r hash st autor assinante assunto; do
  total=$((total + 1))
  ok=0
  case "$st" in
    G) ok=1 ;;
    U) [ "$ACEITAR_U" = "1" ] && ok=1 ;;
  esac
  if [ "$ok" -eq 1 ]; then
    printf '  ok    %s  [%s]  %s\n' "${hash:0:9}" "$st" "$assunto"
  else
    reprovados=$((reprovados + 1))
    printf '  FALHA %s  [%s]  %s  (autor: %s)\n' "${hash:0:9}" "$st" "$assunto" "$autor"
  fi
done < <(git -C "$REPO" log "${FILTRO[@]}" --format='%H|%G?|%an|%GS|%s' "$INTERVALO")

echo
if [ "$reprovados" -gt 0 ]; then
  echo "  $reprovados de $total commit(s) sem assinatura válida."
  exit 1
fi
echo "  $total commit(s), todos com assinatura válida."
exit 0
