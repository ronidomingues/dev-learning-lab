#!/usr/bin/env bash
#
# install.sh — instalação de primeira execução na máquina do CLIENTE.
#
# Este script É a resposta prática da pergunta que originou o curso:
# "o .env não vai; então como os segredos chegam ao servidor do cliente?"
# Resposta: alguém os informa UMA vez, num diálogo controlado, e o script
# os grava com o dono e a permissão certos, fora do diretório da aplicação
# e fora do Git.
#
# Propriedades de projeto (cada uma existe por um motivo, veja o README):
#   • idempotente — rodar duas vezes não estraga nada;
#   • `umask 077` desde o começo — nenhum arquivo nasce legível por outros;
#   • valida ANTES de gravar — nunca deixa configuração pela metade;
#   • segredo digitado não ecoa na tela nem entra no histórico do shell;
#   • SESSION_SECRET é GERADO, não perguntado: segredo que não viaja não vaza,
#     e cada instalação fica com um valor diferente.
#
# Uso:  sudo ./deploy/install.sh
set -euo pipefail

APP="cofre-de-recados"
DIR_APP="/opt/${APP}"
DIR_CONF="/etc/${APP}"
ARQ_ENV="${DIR_CONF}/env"
USUARIO="cofre"
AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

[[ $EUID -eq 0 ]] || { echo "Rode como root:  sudo $0"; exit 1; }
command -v node >/dev/null || { echo "Node.js não encontrado. Instale Node 22+ e rode de novo."; exit 1; }

VERSAO_NODE=$(node -p 'process.versions.node.split(".")[0]')
(( VERSAO_NODE >= 22 )) || { echo "Node 22+ é exigido (encontrado: $(node -v))."; exit 1; }

umask 077   # tudo criado a partir daqui nasce sem permissão para grupo/outros

# ── 1. usuário de sistema, sem shell e sem home ────────────────────────────
if ! id "$USUARIO" &>/dev/null; then
  useradd --system --no-create-home --shell /usr/sbin/nologin "$USUARIO"
  echo "• usuário de sistema '$USUARIO' criado"
fi

# ── 2. código da aplicação ─────────────────────────────────────────────────
install -d -m 755 -o root -g root "$DIR_APP"
cp -r "$AQUI/src" "$AQUI/package.json" "$DIR_APP/"
chown -R root:root "$DIR_APP"    # a aplicação NÃO pode alterar o próprio código
echo "• aplicação instalada em $DIR_APP"

# ── 3. diretório de configuração ───────────────────────────────────────────
install -d -m 750 -o root -g "$USUARIO" "$DIR_CONF"

if [[ -f "$ARQ_ENV" ]]; then
  echo "• configuração já existe em $ARQ_ENV — mantida"
  echo "  Para reconfigurar:  sudo mv $ARQ_ENV $ARQ_ENV.bak && sudo $0"
else
  echo
  echo "═══ Configuração do ${APP} ═══"
  echo "Os valores abaixo serão gravados em $ARQ_ENV (root:${USUARIO}, 640)."
  echo

  TMP="$(mktemp "${DIR_CONF}/.env.XXXXXX")"
  trap 'rm -f "$TMP"' EXIT

  perguntar() {   # $1=NOME  $2=pergunta  $3="secreto" (opcional)
    local valor
    while :; do
      if [[ "${3:-}" == "secreto" ]]; then
        read -rsp "  $2: " valor </dev/tty; echo
      else
        read -rp  "  $2: " valor </dev/tty
      fi
      [[ -n "$valor" ]] && break
      echo "  ⚠️  não pode ficar em branco."
    done
    printf '%s=%s\n' "$1" "$valor" >> "$TMP"
  }

  perguntar DATABASE_URL "URL do PostgreSQL (postgres://usuario:senha@host:5432/banco)"
  perguntar API_KEY      "Chave de API fornecida por nós" secreto

  # Gerado aqui: nunca trafega, é único desta instalação.
  printf 'SESSION_SECRET=%s\n' "$(openssl rand -base64 48 | tr -d '\n')" >> "$TMP"
  printf 'NODE_ENV=production\nPORT=8080\nLOG_LEVEL=info\n' >> "$TMP"

  echo
  echo "• validando antes de gravar…"
  if ! ( set -a; . "$TMP"; set +a; node "$DIR_APP/src/check-config.mjs" ); then
    echo "❌ Configuração inválida. NADA foi gravado. Rode de novo."
    exit 1
  fi

  mv "$TMP" "$ARQ_ENV"
  trap - EXIT
  chown root:"$USUARIO" "$ARQ_ENV"
  chmod 640 "$ARQ_ENV"
  echo "• configuração gravada em $ARQ_ENV"
fi

# ── 4. serviço ─────────────────────────────────────────────────────────────
install -m 644 -o root -g root "$AQUI/deploy/${APP}.service" "/etc/systemd/system/${APP}.service"
systemctl daemon-reload
systemctl enable --now "$APP"

sleep 2
if systemctl is-active --quiet "$APP"; then
  echo "• serviço ativo"
else
  echo "❌ o serviço não subiu. Veja:  journalctl -u $APP -n 50 --no-pager"
  exit 1
fi

cat <<FIM

✅ Instalação concluída.

   Configuração : $ARQ_ENV   (root:${USUARIO}, 640)
   Aplicação    : $DIR_APP
   Serviço      : systemctl status $APP
   Log          : journalctl -u $APP -f
   Diagnóstico  : sudo -u $USUARIO env \$(cat $ARQ_ENV | xargs) node $DIR_APP/src/check-config.mjs

⚠️  IMPORTANTE — leia e repasse ao responsável de TI do cliente:

   1. Faça backup de $ARQ_ENV. O SESSION_SECRET foi gerado agora e não existe
      em nenhum outro lugar. Perdê-lo desconecta os usuários (não perde dados).
   2. NÃO copie esse arquivo por e-mail, WhatsApp ou para dentro de $DIR_APP.
   3. NÃO adicione essas variáveis ao ~/.bashrc de ninguém.
   4. Para trocar a chave de API:
         sudo mv $ARQ_ENV $ARQ_ENV.bak && sudo $0
      e depois de confirmar que funcionou:  sudo shred -u $ARQ_ENV.bak

FIM
