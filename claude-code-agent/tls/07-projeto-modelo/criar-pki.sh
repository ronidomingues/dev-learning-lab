#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# criar-pki.sh — monta a PKI inteira do projeto, do zero.
#
# Produz, em ./pki/:
#   ca.crt / ca.key        a autoridade certificadora raiz
#   servidor.crt/.key      certificado do servidor (serverAuth)
#   admin.crt/.key         cliente com todos os poderes
#   leitor.crt/.key        cliente que só lê
#   escritor.crt/.key      cliente que lê e escreve
#   banido.crt/.key        cliente que será REVOGADO (para o teste de CRL)
#   vencido.crt/.key       cliente com validade no passado (teste de expiração)
#   intruso-ca.crt/.key    uma SEGUNDA CA, não confiada — teste de "outra CA"
#   intruso.crt/.key       cliente assinado pela CA intrusa, dizendo-se "admin"
#   ca.crl                 lista de revogação, contendo o "banido"
#   index.txt / serial     a base de dados da CA
#
# Idempotente: rode com --forcar para refazer tudo.
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail
cd "$(dirname "$0")"

CNF=pki/openssl-ca.cnf
DIAS_FOLHA=90
ORG="Cofre TLS"
q() { openssl "$@" 2>/dev/null; }

if [ -f pki/ca.key ] && [ "${1:-}" != "--forcar" ]; then
  echo "PKI já existe (use --forcar para refazer). Nada a fazer."
  exit 0
fi

echo "→ limpando"
rm -rf pki/novos pki/index.txt* pki/serial* pki/crlnumber* pki/*.crt pki/*.key pki/*.csr pki/*.crl pki/*.pem
mkdir -p pki/novos
: > pki/index.txt
echo 1000 > pki/serial
echo 1000 > pki/crlnumber

# ── 1. A CA raiz ─────────────────────────────────────────────────────────────
echo "→ [1/7] criando a CA raiz (EC P-384, 10 anos)"
q genpkey -algorithm EC -pkeyopt ec_paramgen_curve:P-384 -out pki/ca.key
chmod 600 pki/ca.key
q req -x509 -new -key pki/ca.key -days 3650 -out pki/ca.crt \
  -config "$CNF" -extensions v3_ca -subj "/O=$ORG/CN=Cofre TLS Root CA"

# ── 2. Função auxiliar de emissão ────────────────────────────────────────────
# emitir <nome> <CN> <perfil> [opções extras do `openssl ca`]
emitir() {
  local nome="$1" cn="$2" perfil="$3"; shift 3
  q genpkey -algorithm EC -pkeyopt ec_paramgen_curve:P-256 -out "pki/$nome.key"
  chmod 600 "pki/$nome.key"
  q req -new -key "pki/$nome.key" -out "pki/$nome.csr" \
       -config "$CNF" -subj "/O=$ORG/CN=$cn"
  q ca -batch -config "$CNF" -extensions "$perfil" \
       -in "pki/$nome.csr" -out "pki/$nome.crt" "$@"
  rm -f "pki/$nome.csr"
}

# ── 3. O servidor ────────────────────────────────────────────────────────────
echo "→ [2/7] emitindo o certificado do servidor"
# Quando se passa -extfile, a opção -extensions aponta para uma seção DENTRO
# desse arquivo. Por isso repetimos o perfil aqui, acrescentando o SAN — que é
# a única parte que muda de certificado para certificado.
cat > pki/san-servidor.cnf <<'SAN'
[ v3_servidor ]
basicConstraints       = critical, CA:FALSE
keyUsage               = critical, digitalSignature, keyEncipherment
extendedKeyUsage       = serverAuth
subjectKeyIdentifier   = hash
authorityKeyIdentifier = keyid:always
crlDistributionPoints  = URI:http://localhost:8080/ca.crl
subjectAltName         = DNS:localhost, DNS:cofre.interno, IP:127.0.0.1
SAN
q genpkey -algorithm EC -pkeyopt ec_paramgen_curve:P-256 -out pki/servidor.key
chmod 600 pki/servidor.key
q req -new -key pki/servidor.key -out pki/servidor.csr -config "$CNF" \
     -subj "/O=$ORG/CN=cofre.interno"
q ca -batch -config "$CNF" -extensions v3_servidor -days "$DIAS_FOLHA" \
     -extfile pki/san-servidor.cnf \
     -in pki/servidor.csr -out pki/servidor.crt
rm -f pki/servidor.csr

# ── 4. Os clientes legítimos ─────────────────────────────────────────────────
echo "→ [3/7] emitindo clientes: admin, escritor, leitor"
emitir admin    "admin"    v3_cliente -days "$DIAS_FOLHA"
emitir escritor "escritor" v3_cliente -days "$DIAS_FOLHA"
emitir leitor   "leitor"   v3_cliente -days "$DIAS_FOLHA"

# ── 5. O que será revogado ───────────────────────────────────────────────────
echo "→ [4/7] emitindo 'banido' (será revogado a seguir)"
emitir banido "banido" v3_cliente -days "$DIAS_FOLHA"

# ── 6. Um certificado já vencido ─────────────────────────────────────────────
# `openssl ca` aceita datas absolutas: emitimos um certificado cuja validade
# terminou ontem. É a forma limpa de testar expiração sem mexer no relógio.
echo "→ [5/7] emitindo 'vencido' (validade no passado)"
INI=$(date -u -d "60 days ago" +%y%m%d%H%M%SZ)
FIM=$(date -u -d "1 day ago"   +%y%m%d%H%M%SZ)
emitir vencido "vencido" v3_cliente -startdate "$INI" -enddate "$FIM"

# ── 7. Uma CA intrusa (não confiada pelo servidor) ───────────────────────────
echo "→ [6/7] criando a CA intrusa e um cliente dela"
q genpkey -algorithm EC -pkeyopt ec_paramgen_curve:P-256 -out pki/intruso-ca.key
q req -x509 -new -key pki/intruso-ca.key -days 3650 -out pki/intruso-ca.crt \
  -config "$CNF" -extensions v3_ca -subj "/O=Intruso SA/CN=CA do Atacante"
q genpkey -algorithm EC -pkeyopt ec_paramgen_curve:P-256 -out pki/intruso.key
q req -new -key pki/intruso.key -out pki/intruso.csr -config "$CNF" \
  -subj "/O=Intruso SA/CN=admin"          # <- repare: ele se diz "admin"
q x509 -req -in pki/intruso.csr -CA pki/intruso-ca.crt -CAkey pki/intruso-ca.key \
  -CAcreateserial -days 90 -out pki/intruso.crt \
  -extfile <(printf "extendedKeyUsage=clientAuth\nbasicConstraints=critical,CA:FALSE")
rm -f pki/intruso.csr

# ── 8. Revogar e gerar a CRL ─────────────────────────────────────────────────
echo "→ [7/7] revogando 'banido' e gerando a CRL"
q ca -config "$CNF" -revoke pki/banido.crt -crl_reason keyCompromise
q ca -config "$CNF" -gencrl -out pki/ca.crl
cat pki/ca.crt pki/ca.crl > pki/ca-com-crl.pem

# ── Verificação ──────────────────────────────────────────────────────────────
echo
echo "=== verificação ==="
openssl verify -CAfile pki/ca.crt pki/servidor.crt pki/admin.crt pki/leitor.crt pki/escritor.crt
echo -n "intruso contra a nossa CA (deve FALHAR): "
{ openssl verify -CAfile pki/ca.crt pki/intruso.crt 2>&1 || true; } | tail -1
echo -n "banido com checagem de CRL (deve FALHAR): "
{ openssl verify -crl_check -CAfile pki/ca-com-crl.pem pki/banido.crt 2>&1 || true; } | tail -1
echo -n "admin com checagem de CRL (deve passar):  "
{ openssl verify -crl_check -CAfile pki/ca-com-crl.pem pki/admin.crt 2>&1 || true; } | tail -1
echo
# `-updatedb` varre a base e marca como E (expired) o que passou da validade.
# Sem esse passo o 'vencido' continua aparecendo como V — a CA não descobre
# sozinha que o tempo passou.
q ca -config "$CNF" -updatedb || true
echo "base de emissão (pki/index.txt) — V=válido, R=revogado, E=expirado:"
awk -F'\t' '{printf "  estado=%s  serie=%-42s %s\n", $1, $4, $6}' pki/index.txt
echo
echo "PKI pronta em ./pki/"
