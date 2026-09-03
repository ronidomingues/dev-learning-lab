#!/usr/bin/env bash
# test.sh — suite de verificacao do projeto-modelo.
# Confirma que (1) o crackme aceita as respostas certas e rejeita as erradas,
# em TODAS as variantes de compilacao, e (2) o solver automatico resolve os
# tres niveis. Sai com codigo 0 se tudo passa.
set -u

falhas=0
ok()   { echo "  [OK]   $1"; }
erro() { echo "  [FALHA] $1"; falhas=$((falhas+1)); }

# Respostas corretas (o gabarito). O nivel 3 aceita muitos seriais;
# usamos um valido conhecido para o teste positivo.
R1="engenharia-reversa-2026"
R2="GhidraRadare"
R3="0700-9998-0000"

# concede? <binario> <nivel> <tentativa>  -> 0 se "Acesso concedido"
concede() {
  "$1" "$2" "$3" 2>/dev/null | grep -q "Acesso concedido"
}

echo "== Compilando variantes =="
make --silent crackme crackme_stripped crackme_hard || { echo "compilacao falhou"; exit 1; }

for bin in ./crackme ./crackme_stripped ./crackme_hard; do
  echo "== Testando $bin =="

  # Positivos: respostas certas devem conceder
  concede "$bin" 1 "$R1" && ok "nivel 1 aceita a senha correta" \
                         || erro "nivel 1 NAO aceitou a senha correta"
  concede "$bin" 2 "$R2" && ok "nivel 2 aceita a senha correta" \
                         || erro "nivel 2 NAO aceitou a senha correta"
  concede "$bin" 3 "$R3" && ok "nivel 3 aceita um serial valido" \
                         || erro "nivel 3 NAO aceitou um serial valido"

  # Negativos: entradas erradas devem negar
  concede "$bin" 1 "errado"          && erro "nivel 1 aceitou senha ERRADA" \
                                     || ok "nivel 1 rejeita senha errada"
  concede "$bin" 2 "GhidraRadar"     && erro "nivel 2 aceitou senha ERRADA" \
                                     || ok "nivel 2 rejeita senha errada"
  concede "$bin" 3 "0000-0000-0000"  && erro "nivel 3 aceitou serial ERRADO" \
                                     || ok "nivel 3 rejeita serial errado (soma!=42)"
  concede "$bin" 3 "0001-9999-9998"  && erro "nivel 3 aceitou serial ERRADO" \
                                     || ok "nivel 3 rejeita serial errado (bloco1 nao mult 7)"
done

echo "== Testando o solver automatico (em crackme e crackme_stripped) =="
for bin in ./crackme ./crackme_stripped; do
  if python3 solver.py "$bin" 2>/dev/null | grep -q "nivel 3:.*CONFIRMADO"; then
    # confere que os tres foram confirmados
    n=$(python3 solver.py "$bin" 2>/dev/null | grep -c "CONFIRMADO")
    if [ "$n" -eq 3 ]; then ok "solver resolveu 3/3 em $bin"; else erro "solver resolveu $n/3 em $bin"; fi
  else
    erro "solver falhou em $bin"
  fi
done

echo
if [ "$falhas" -eq 0 ]; then
  echo "TODOS OS TESTES PASSARAM."
  exit 0
else
  echo "$falhas TESTE(S) FALHARAM."
  exit 1
fi
