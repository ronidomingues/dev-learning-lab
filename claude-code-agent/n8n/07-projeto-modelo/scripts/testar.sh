#!/usr/bin/env bash
# Exercita a API do projeto de ponta a ponta e confere os codigos de status.
# Uso: ./scripts/testar.sh [base_url]      (padrao: http://localhost:5678)
set -uo pipefail
BASE="${1:-http://localhost:5678}"
ID="P-$(date +%s)"
falhas=0

checar() { # checar <descricao> <esperado> <obtido>
  if [ "$2" = "$3" ]; then
    printf '  ✓ %-46s %s\n' "$1" "$3"
  else
    printf '  ✗ %-46s esperado %s, obtido %s\n' "$1" "$2" "$3"; falhas=$((falhas+1))
  fi
}

echo "== central-de-pedidos: teste de ponta a ponta =="
echo "   base: $BASE   pedido: $ID"
echo

echo "1) pedido valido -> 202"
COD=$(curl -s -o /tmp/cp1.json -w '%{http_code}' -X POST "$BASE/webhook/pedido" \
  -H 'Content-Type: application/json' \
  -d "{\"pedido_id\":\"$ID\",\"cliente\":\"Ana\",\"valor\":150.5,\"itens\":[{\"sku\":\"A\",\"qtd\":2}]}")
checar "POST /webhook/pedido (valido)" 202 "$COD"

echo "2) pedido invalido -> 400"
COD=$(curl -s -o /tmp/cp2.json -w '%{http_code}' -X POST "$BASE/webhook/pedido" \
  -H 'Content-Type: application/json' -d '{"cliente":"","valor":-1}')
checar "POST /webhook/pedido (invalido)" 400 "$COD"

echo "3) reenvio do MESMO pedido -> 202 e sem duplicar (idempotencia)"
COD=$(curl -s -o /tmp/cp3.json -w '%{http_code}' -X POST "$BASE/webhook/pedido" \
  -H 'Content-Type: application/json' \
  -d "{\"pedido_id\":\"$ID\",\"cliente\":\"Ana\",\"valor\":150.5,\"itens\":[{\"sku\":\"A\",\"qtd\":2}]}")
checar "POST /webhook/pedido (reenvio)" 202 "$COD"

sleep 2

echo "4) consulta do pedido -> 200"
COD=$(curl -s -o /tmp/cp4.json -w '%{http_code}' "$BASE/webhook/pedido?id=$ID")
checar "GET /webhook/pedido?id=$ID" 200 "$COD"

echo "5) consulta de pedido inexistente -> 404"
COD=$(curl -s -o /tmp/cp5.json -w '%{http_code}' "$BASE/webhook/pedido?id=NAO-EXISTE-999")
checar "GET /webhook/pedido?id=NAO-EXISTE-999" 404 "$COD"

echo "6) o banco tem exatamente UMA linha para $ID"
N=$(docker compose exec -T postgres psql -U "${POSTGRES_USER:-n8n}" -d "${POSTGRES_DB:-pedidos}" \
      -tAc "select count(*) from pedidos where pedido_id = '$ID';" 2>/dev/null | tr -d '[:space:]')
checar "linhas em pedidos para $ID" 1 "$N"

echo
if [ "$falhas" -eq 0 ]; then
  echo "== TUDO PASSOU =="
else
  echo "== $falhas VERIFICACAO(OES) FALHOU(RAM) =="
fi
exit "$falhas"
