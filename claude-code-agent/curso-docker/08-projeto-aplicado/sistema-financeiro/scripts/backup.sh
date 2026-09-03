#!/bin/sh
# Dump diário com retenção de 14 dias.
# Roda em loop dentro do container: sem cron, sem dependência do host.
set -eu

RETENCAO_DIAS=14
INTERVALO=86400   # 24h

export PGPASSWORD="$(cat /run/secrets/db_password)"

while true; do
    CARIMBO="$(date +%Y-%m-%d_%H%M%S)"
    ARQUIVO="/backup/financeiro_${CARIMBO}.sql.gz"

    echo "[backup] iniciando dump -> ${ARQUIVO}"
    if pg_dump -h db -U financeiro -d financeiro | gzip > "${ARQUIVO}"; then
        echo "[backup] concluído: $(du -h "${ARQUIVO}" | cut -f1)"
    else
        echo "[backup] ERRO no dump" >&2
        rm -f "${ARQUIVO}"
    fi

    # Um backup que nunca foi restaurado não é um backup — é esperança.
    # Teste a restauração periodicamente:
    #   gunzip -c arquivo.sql.gz | psql -h db -U financeiro -d teste_restore
    echo "[backup] limpando dumps com mais de ${RETENCAO_DIAS} dias"
    find /backup -name 'financeiro_*.sql.gz' -mtime "+${RETENCAO_DIAS}" -delete

    sleep "${INTERVALO}"
done
