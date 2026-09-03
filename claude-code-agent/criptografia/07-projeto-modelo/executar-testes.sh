#!/usr/bin/env bash
# Roda a suíte inteira. Sem argumentos, sem dependências, sem rede.
set -euo pipefail
cd "$(dirname "$0")"
echo "== autoteste rápido das primitivas =="
python3 cofre.py autoteste
echo
echo "== suíte de testes =="
python3 -m unittest discover -s testes -t . "$@"
