#!/usr/bin/env bash
# backup.sh — backup lógico da biblioteca, com verificação.
# Uso:  DB_SENHA=... ./scripts/backup.sh
set -euo pipefail

DESTINO="${1:-./backups}"
mkdir -p "$DESTINO"
CARIMBO=$(date +%Y-%m-%d_%H%M%S)
ARQUIVO="$DESTINO/biblioteca_${CARIMBO}.dump"

echo "fazendo backup para $ARQUIVO"

# -Fc = formato custom (comprimido, restaurável seletivamente com pg_restore).
# Rodamos pg_dump DENTRO do container do banco, para não depender de client local.
docker compose exec -T db \
  pg_dump -U biblioteca -d biblioteca -Fc > "$ARQUIVO"

# Verificação: o dump não pode estar vazio nem corrompido.
if [ ! -s "$ARQUIVO" ]; then
  echo "ERRO: dump vazio" >&2
  rm -f "$ARQUIVO"
  exit 1
fi
# pg_restore --list lê o índice do dump; falha se corrompido.
docker compose exec -T db pg_restore --list /dev/stdin < "$ARQUIVO" > /dev/null \
  || { echo "ERRO: dump corrompido" >&2; rm -f "$ARQUIVO"; exit 1; }

echo "ok: $(du -h "$ARQUIVO" | cut -f1)"

# Retenção: mantém os 7 mais recentes.
ls -1t "$DESTINO"/biblioteca_*.dump 2>/dev/null | tail -n +8 | xargs -r rm -f

# Para RESTAURAR num banco limpo:
#   docker compose exec -T db pg_restore -U biblioteca -d biblioteca --clean --if-exists < backup.dump
