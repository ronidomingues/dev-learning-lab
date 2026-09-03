#!/usr/bin/env bash
#
# sandbox.sh — laboratório completo de commits assinados, em pasta descartável.
#
# O que ele faz, em ordem: gera um par de chaves SSH e um par de chaves GPG
# *de brinquedo*, monta um repositório Git novo, assina commits pelos dois
# métodos, verifica as assinaturas, e então QUEBRA a verificação de cinco
# maneiras diferentes para você ver cada código de status com os próprios olhos.
#
# GARANTIA DE ISOLAMENTO — este script NÃO toca em nada seu:
#   • usa um GNUPGHOME próprio (não o seu ~/.gnupg);
#   • grava as chaves SSH na pasta de trabalho (não em ~/.ssh);
#   • só usa `git config` local, dentro do repositório de teste
#     (nunca `git config --global`);
#   • não fala com a rede, não sobe nada para o GitHub, não pede senha.
#
# Uso:
#   ./sandbox.sh                 # monta em pasta temporária e apaga no fim
#   ./sandbox.sh --manter        # monta e DEIXA a pasta para você explorar
#   ./sandbox.sh --dir /caminho  # monta num caminho escolhido por você
#
set -uo pipefail

# ─────────────────────────────────────────────────────────────────────────────
# Argumentos e pasta de trabalho
# ─────────────────────────────────────────────────────────────────────────────
MANTER=0
DIR=""
while [ $# -gt 0 ]; do
  case "$1" in
    --manter) MANTER=1; shift ;;
    --dir)    DIR="${2:-}"; MANTER=1; shift 2 ;;
    -h|--help) sed -n '2,26p' "$0"; exit 0 ;;
    *) echo "argumento desconhecido: $1" >&2; exit 2 ;;
  esac
done

if [ -n "$DIR" ]; then
  mkdir -p "$DIR" || exit 1
  WORK="$(cd "$DIR" && pwd)"
else
  WORK="$(mktemp -d "${TMPDIR:-/tmp}/commits-assinados.XXXXXX")"
fi

export GNUPGHOME="$WORK/gnupg"     # isola o chaveiro GPG deste laboratório
mkdir -p "$GNUPGHOME"; chmod 700 "$GNUPGHOME"
SSHDIR="$WORK/ssh";  mkdir -p "$SSHDIR";  chmod 700 "$SSHDIR"
REPO="$WORK/repo"
SIGNERS="$WORK/allowed_signers"

limpar() {
  if [ "$MANTER" -eq 1 ]; then
    echo
    echo "Pasta do laboratório mantida em: $WORK"
    echo "Para apagar tudo:  rm -rf '$WORK'"
  else
    # gpgconf mata o agente antes de remover a pasta; sem isso, sobra processo.
    gpgconf --kill all >/dev/null 2>&1
    rm -rf "$WORK"
  fi
}
trap limpar EXIT

# ─────────────────────────────────────────────────────────────────────────────
# Enfeites de saída
# ─────────────────────────────────────────────────────────────────────────────
if [ -t 1 ]; then B=$'\033[1m'; D=$'\033[2m'; R=$'\033[0m'; else B=""; D=""; R=""; fi
ato()  { echo; echo "${B}── $* ${R}"; }
nota() { echo "${D}   $*${R}"; }
cmd()  { echo "${D}   \$ $*${R}"; }

# Mostra o status de assinatura do commit indicado (padrão: HEAD).
# %G? devolve: G=boa · B=ruim · U=boa mas sem confiança · X=assinatura expirada
#              Y=feita por chave que depois expirou · R=chave revogada
#              E=não deu para checar · N=sem assinatura
status() { git -C "$REPO" log --format='   %h  [%G?]  %<(24)%GS  %s' -1 "${1:-HEAD}"; }

# ─────────────────────────────────────────────────────────────────────────────
ato "ATO 0 · Versões desta máquina"
# Todo o resto depende delas. SSH signing exige Git >= 2.34.
git --version
gpg --version | head -1
ssh -V 2>&1
nota "Git < 2.34 não tem 'gpg.format ssh'. Se for o seu caso, veja 03-instalacao.md."

# ─────────────────────────────────────────────────────────────────────────────
ato "ATO 1 · Gerar as chaves de brinquedo"
# -N "" = sem frase secreta. Numa chave de verdade, NUNCA faça isso;
# aqui é para o laboratório rodar sozinho, sem pinentry e sem interação.
cmd "ssh-keygen -t ed25519 -C ana@exemplo.dev -f $SSHDIR/id_assina -N ''"
ssh-keygen -t ed25519 -C "ana@exemplo.dev" -f "$SSHDIR/id_assina" -N "" -q
PUB="$(cat "$SSHDIR/id_assina.pub")"
echo "   chave pública SSH: $PUB"

cmd "gpg --quick-generate-key 'Ana Souza <ana@exemplo.dev>' ed25519 sign 2y"
gpg --batch --pinentry-mode loopback --passphrase '' \
    --quick-generate-key "Ana Souza <ana@exemplo.dev>" ed25519 sign 2y >/dev/null 2>&1
KEYID="$(gpg --list-secret-keys --with-colons | awk -F: '/^sec:/ {print $5; exit}')"
FPR="$(gpg --list-secret-keys --with-colons | awk -F: '/^fpr:/ {print $10; exit}')"
echo "   ID longo da chave GPG: $KEYID"
echo "   impressão digital:     $FPR"
nota "É o ID longo (16 hex) que vai em user.signingkey. A impressão digital (40 hex) também serve."

# ─────────────────────────────────────────────────────────────────────────────
ato "ATO 2 · Criar o repositório e configurar a identidade"
git init -q -b main "$REPO"
git -C "$REPO" config user.name  "Ana Souza"
git -C "$REPO" config user.email "ana@exemplo.dev"
nota "user.email é texto livre: o Git aceita qualquer coisa aqui. É exatamente por isso"
nota "que a assinatura existe — ela é o que amarra o commit a uma chave de verdade."

# ─────────────────────────────────────────────────────────────────────────────
ato "ATO 3 · Assinar com SSH"
git -C "$REPO" config gpg.format ssh
git -C "$REPO" config user.signingkey "$SSHDIR/id_assina.pub"   # o .PÚBLICO, sim
git -C "$REPO" config commit.gpgsign true
cmd "git config gpg.format ssh"
cmd "git config user.signingkey <caminho da chave PÚBLICA>"
cmd "git config commit.gpgsign true"
printf 'primeira linha\n' > "$REPO/arquivo.txt"
git -C "$REPO" add arquivo.txt
git -C "$REPO" commit -q -m "commit assinado com SSH"
echo "   antes de configurar o allowed_signers:"
status
nota "[U] = 'assinatura boa, mas não sei de quem'. O Git verificou a matemática,"
nota "e não tem como ligar aquela chave a uma pessoa. Falta o allowed_signers."

# ─────────────────────────────────────────────────────────────────────────────
ato "ATO 4 · O arquivo allowed_signers"
printf 'ana@exemplo.dev namespaces="git" %s\n' "$PUB" > "$SIGNERS"
git -C "$REPO" config gpg.ssh.allowedSignersFile "$SIGNERS"
echo "   $(cat "$SIGNERS")"
status
git -C "$REPO" log --show-signature -1 | sed -n '2p' | sed 's/^/   /'
nota "namespaces=\"git\" limita a chave a assinar objetos do Git. Sem isso, a mesma"
nota "assinatura valeria para qualquer coisa (arquivo, e-mail, o que for)."

# ─────────────────────────────────────────────────────────────────────────────
ato "ATO 5 · Assinar com GPG no mesmo repositório"
git -C "$REPO" config gpg.format openpgp
git -C "$REPO" config user.signingkey "$KEYID"
printf 'segunda linha\n' >> "$REPO/arquivo.txt"
git -C "$REPO" commit -q -am "commit assinado com GPG"
status
git -C "$REPO" log --show-signature -1 | sed -n '2,4p' | sed 's/^/   /'
nota "Mesmo repositório, dois métodos, os dois válidos. O que muda é só gpg.format."

# ─────────────────────────────────────────────────────────────────────────────
ato "ATO 6 · Como a assinatura fica dentro do objeto commit"
echo "   ── objeto do commit assinado por GPG:"
git -C "$REPO" cat-file commit HEAD | sed -n '1,9p' | sed 's/^/   /'
echo
echo "   ── objeto do commit assinado por SSH:"
git -C "$REPO" cat-file commit HEAD~1 | sed -n '1,8p' | sed 's/^/   /'
nota "O campo chama-se 'gpgsig' nos dois casos — herança histórica. O conteúdo é que"
nota "muda: BEGIN PGP SIGNATURE contra BEGIN SSH SIGNATURE."

# ─────────────────────────────────────────────────────────────────────────────
ato "ATO 7 · Commit sem assinatura"
git -C "$REPO" -c commit.gpgsign=false commit -q --allow-empty -m "commit sem assinatura"
status
nota "[N] = nenhuma assinatura. Não é erro: é o padrão do Git desde 2005."

# ─────────────────────────────────────────────────────────────────────────────
ato "ATO 8 · Adulterar um commit assinado"
# Reescrevemos o objeto commit à mão, mudando a mensagem e mantendo a assinatura.
# É o que um atacante faria ao tentar forjar histórico.
ALVO="$(git -C "$REPO" log --format='%H' --grep='SSH' -1)"
git -C "$REPO" cat-file commit "$ALVO" > "$WORK/original.txt"
sed 's/commit assinado com SSH/commit adulterado por terceiro/' \
    "$WORK/original.txt" > "$WORK/adulterado.txt"
FALSO="$(git -C "$REPO" hash-object -t commit -w --stdin < "$WORK/adulterado.txt")"
echo "   objeto forjado: $FALSO"
status "$FALSO"
echo "   ── git verify-commit:"
git -C "$REPO" verify-commit "$FALSO" 2>&1 | sed 's/^/   /'
nota "[B] = assinatura RUIM. Um byte alterado e a conta não fecha mais. Este é o"
nota "ponto inteiro do assunto: o histórico assinado é detectavelmente imutável."

# ─────────────────────────────────────────────────────────────────────────────
ato "ATO 9 · A armadilha do allowed_signers (leia com atenção)"
printf 'roberto@outraempresa.com namespaces="git" %s\n' "$PUB" > "$SIGNERS"
echo "   allowed_signers agora diz que esta chave é do Roberto:"
echo "   $(cut -c1-60 "$SIGNERS")..."
git -C "$REPO" log --format='   %h  [%G?]  autor=%an <%ae>  assinante=%GS' -1 HEAD~2
nota "Olhe de novo: o autor é a Ana, o Git diz [G] (boa) e aponta o Roberto como"
nota "assinante. O Git NÃO confere se o assinante bate com o autor do commit —"
nota "ele só informa que nome consta no seu arquivo para aquela chave."
nota "Quem faz esse casamento é o GitHub, e só ele. Veja 15-verificacao-no-github.md."
printf 'ana@exemplo.dev namespaces="git" %s\n' "$PUB" > "$SIGNERS"

# ─────────────────────────────────────────────────────────────────────────────
ato "ATO 10 · Validade com data no allowed_signers"
printf 'ana@exemplo.dev namespaces="git",valid-before="20250101" %s\n' "$PUB" > "$SIGNERS"
echo "   com valid-before=20250101 (no passado):"
git -C "$REPO" log --show-signature -1 HEAD~2 2>&1 | sed -n '2,3p' | sed 's/^/   /'
status HEAD~2
printf 'ana@exemplo.dev namespaces="git" %s\n' "$PUB" > "$SIGNERS"
nota "É assim que se aposenta uma chave SSH sem invalidar o passado: em vez de apagar"
nota "a linha, você põe valid-before na data em que a chave saiu de uso."

# ─────────────────────────────────────────────────────────────────────────────
ato "ATO 11 · Tag assinada"
git -C "$REPO" config gpg.format ssh
git -C "$REPO" config user.signingkey "$SSHDIR/id_assina.pub"
git -C "$REPO" tag -s v1.0.0 -m "release 1.0.0"
git -C "$REPO" tag -v v1.0.0 2>&1 | sed -n '1,2p' | sed 's/^/   /'
nota "Tag assinada é o que realmente importa numa release: é o carimbo de 'este"
nota "código é o que eu publiquei'. Muita gente assina commit e esquece a tag."

# ─────────────────────────────────────────────────────────────────────────────
ato "ATO 12 · Hook que recusa commit não assinado"
install -m 755 "$(dirname "$0")/../hooks/pre-commit" "$REPO/.git/hooks/pre-commit" 2>/dev/null || {
  cat > "$REPO/.git/hooks/pre-commit" <<'HOOK'
#!/usr/bin/env bash
[ "$(git config --get commit.gpgsign)" = "true" ] || {
  echo "recusado: commit.gpgsign não está ligado neste repositório" >&2; exit 1; }
HOOK
  chmod 755 "$REPO/.git/hooks/pre-commit"
}
echo "   tentando commitar com commit.gpgsign=false:"
git -C "$REPO" -c commit.gpgsign=false commit -q --allow-empty -m "tentativa" 2>&1 | sed 's/^/   /'
echo "   (código de saída: $?)"
nota "Hook local é conveniência, não segurança: qualquer um passa por cima com"
nota "--no-verify. A trava de verdade é do lado do servidor — veja 18-politica-de-equipe.md."

# ─────────────────────────────────────────────────────────────────────────────
ato "ATO 13 · Auditoria do histórico (o que você rodaria na CI)"
rm -f "$REPO/.git/hooks/pre-commit"
"$(dirname "$0")/auditar-historico.sh" "$REPO" || true

# ─────────────────────────────────────────────────────────────────────────────
ato "ATO 14 · merge.verifySignatures"
git -C "$REPO" checkout -q -b feature
printf 'terceira\n' >> "$REPO/arquivo.txt"
git -C "$REPO" -c commit.gpgsign=false commit -q -am "trabalho sem assinar"
git -C "$REPO" checkout -q main
echo "   tentando mesclar um ramo cuja ponta não está assinada:"
git -C "$REPO" -c merge.verifySignatures=true merge --no-ff feature -m "merge" 2>&1 \
  | head -2 | sed 's/^/   /'
nota "merge.verifySignatures só olha a PONTA do ramo, não o ramo inteiro."

# ─────────────────────────────────────────────────────────────────────────────
ato "RESUMO · o histórico do laboratório"
git -C "$REPO" log --format='   %h  [%G?]  %s' | sed 's/$//'
echo
echo "   Legenda:  G=boa · B=RUIM · U=boa, assinante desconhecido · N=sem assinatura"
echo "             X=assinatura expirada · Y=feita por chave que depois expirou"
echo "             R=chave revogada · E=não foi possível checar"
