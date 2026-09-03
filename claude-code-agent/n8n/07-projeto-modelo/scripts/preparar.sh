#!/usr/bin/env bash
# Gera .env e a credencial do Postgres a partir dele. Idempotente:
# se os arquivos ja existem, nao sobrescreve.
set -euo pipefail
cd "$(dirname "$0")/.."

if [ ! -f .env ]; then
  SENHA="$(openssl rand -hex 16)"
  CHAVE="$(openssl rand -hex 32)"
  sed -e "s|^POSTGRES_PASSWORD=.*|POSTGRES_PASSWORD=${SENHA}|" \
      -e "s|^N8N_ENCRYPTION_KEY=.*|N8N_ENCRYPTION_KEY=${CHAVE}|" \
      .env.example > .env
  chmod 600 .env
  echo "✓ .env criado com senha e chave aleatorias"
else
  echo "· .env ja existe, mantido"
fi

# shellcheck disable=SC1091
set -a; . ./.env; set +a

if [ ! -f credenciais/postgres.json ]; then
  sed -e "s|\"password\": \".*\"|\"password\": \"${POSTGRES_PASSWORD}\"|" \
      -e "s|\"database\": \".*\"|\"database\": \"${POSTGRES_DB}\"|" \
      -e "s|\"user\": \".*\"|\"user\": \"${POSTGRES_USER}\"|" \
      credenciais/postgres.example.json > credenciais/postgres.json
  chmod 600 credenciais/postgres.json
  echo "✓ credenciais/postgres.json criado (NAO comite este arquivo)"
else
  echo "· credenciais/postgres.json ja existe, mantido"
fi
