#!/usr/bin/env bash
# Gera os arquivos de secrets/ para o compose.yaml, com valores aleatórios.
# Só para DESENVOLVIMENTO local — em produção os valores vêm de outro lugar.
set -euo pipefail
cd "$(dirname "$0")/.."

umask 077
mkdir -p secrets && chmod 700 secrets

[[ -f secrets/session_secret ]] || openssl rand -base64 48 | tr -d '\n' > secrets/session_secret
[[ -f secrets/api_key ]]        || printf 'sk_test_%s' "$(openssl rand -hex 12)" > secrets/api_key
[[ -f secrets/database_url ]]   || printf 'memory://local' > secrets/database_url

chmod 600 secrets/*
ls -l secrets/
echo
echo "Chave de API para os testes:  $(cat secrets/api_key)"
echo "⚠️  secrets/ está no .gitignore. Confirme:  git check-ignore -v secrets/api_key"
