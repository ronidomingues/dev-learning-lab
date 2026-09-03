#!/usr/bin/env bash
# Roda a suíte inteira. Cria a PKI se ela não existir.
set -euo pipefail
cd "$(dirname "$0")"
[ -f pki/ca.crt ] || ./criar-pki.sh
exec python3 -m unittest discover -s testes -p "test_*.py" -v
