# 70 · Prática — 12 laboratórios

**Nível:** iniciante → avançado · **Data:** 31/08/2026
**Pré-requisito:** o checklist de [03-instalacao.md](03-instalacao.md#15-checklist-ambiente-pronto).

Laboratórios progressivos, com **objetivo**, **passos**, **verificação** e **o que você
deveria ter aprendido**. Faça na ordem. Cada um leva de 10 a 40 minutos.

> Todos usam `localhost` e portas altas. Nenhum exige domínio, servidor público ou
> dinheiro. Os laboratórios 9 e 12 exigem uma máquina que você controla — e são os
> únicos que devem ser feitos **exclusivamente** na sua própria rede.

| # | Laboratório | Nível | Tempo |
|---|---|---|---|
| [1](#lab-1--anatomia-de-um-certificado) | Anatomia de um certificado | iniciante | 15 min |
| [2](#lab-2--o-cadeado-quebrado) | O cadeado quebrado (badssl) | iniciante | 15 min |
| [3](#lab-3--sua-primeira-ca) | Sua primeira CA | iniciante | 25 min |
| [4](#lab-4--o-handshake-no-fio) | O handshake no fio | intermediário | 30 min |
| [5](#lab-5--decifrar-o-próprio-tráfego) | Decifrar o próprio tráfego | intermediário | 30 min |
| [6](#lab-6--quebrar-de-propósito) | Quebrar de propósito (6 falhas) | intermediário | 40 min |
| [7](#lab-7--mtls-do-zero) | mTLS do zero | intermediário | 30 min |
| [8](#lab-8--revogação-que-funciona) | Revogação que funciona | avançado | 25 min |
| [9](#lab-9--acme-de-verdade) | ACME de verdade (staging) | intermediário | 30 min |
| [10](#lab-10--auditoria-de-configuração) | Auditoria de configuração | intermediário | 25 min |
| [11](#lab-11--medir-o-custo-do-tls) | Medir o custo do TLS | avançado | 30 min |
| [12](#lab-12--mitm-controlado) | MITM controlado (na sua rede) | avançado | 40 min |

---

## Lab 1 — Anatomia de um certificado

**Objetivo:** ler um certificado sem medo.

```bash
mkdir -p ~/labs-tls/01 && cd ~/labs-tls/01
openssl req -x509 -newkey ec -pkeyopt ec_paramgen_curve:P-256 -nodes -days 30 \
  -keyout k.pem -out c.pem -subj "/O=Lab/CN=teste.local" \
  -addext "subjectAltName=DNS:teste.local,DNS:www.teste.local,IP:127.0.0.1"
```

Responda, **usando comandos**, e anote as respostas:

1. Quem é o `subject`? E o `issuer`? O que a igualdade entre eles significa?
2. Que nomes o certificado cobre? (dica: **não** olhe o CN)
3. Qual é o algoritmo e o tamanho da chave?
4. Quando vence? Quantos dias faltam?
5. Qual é a impressão digital SHA-256?
6. Ele pode assinar outros certificados?

```bash
openssl x509 -in c.pem -noout -subject -issuer
openssl x509 -in c.pem -noout -ext subjectAltName
openssl x509 -in c.pem -noout -text | grep -A3 "Public Key Algorithm"
openssl x509 -in c.pem -noout -dates -checkend 2592000; echo "checkend=$?"
openssl x509 -in c.pem -noout -fingerprint -sha256
openssl x509 -in c.pem -noout -ext basicConstraints
```

**Verificação:** você consegue responder as seis sem consultar o [05](05-manual-de-uso.md).

**Aprendizado:** o certificado é um documento legível; a informação que importa está
nas **extensões**, não no `subject`.

---

## Lab 2 — O cadeado quebrado

**Objetivo:** ver cada modo de falha com os próprios olhos, e associar cada erro à causa.

O site <https://badssl.com/> mantém dezenas de subdomínios deliberadamente quebrados.

```bash
for h in expired wrong.host self-signed untrusted-root incomplete-chain \
         revoked no-subject sha1-intermediate; do
  printf "%-22s " "$h"
  curl -sS -o /dev/null "https://$h.badssl.com/" 2>&1 | head -1 || true
done
```

Depois abra três deles no navegador e compare a **mensagem que o usuário vê** com a
mensagem do curl. Anote: qual é mais clara? Qual dá mais informação para diagnosticar?

Agora o mais instrutivo:

```bash
curl -sS -o /dev/null "https://incomplete-chain.badssl.com/" ; echo "curl: $?"
# e no navegador: funciona?
```

**Verificação:** você deve conseguir explicar por que `incomplete-chain` falha no curl
e (frequentemente) funciona no navegador.

**Aprendizado:** erro de TLS quase nunca é "o TLS está quebrado". É sempre um dos
quatro: nome, validade, cadeia, confiança. E clientes diferentes são rígidos de formas
diferentes ([04 §Erro 1](04-como-comecar.md)).

---

## Lab 3 — Sua primeira CA

**Objetivo:** ser a autoridade certificadora e sentir o poder (e o risco) disso.

Use o script do [06 Exemplo 3](06-exemplos.md) ou, melhor, o do
[projeto-modelo](07-projeto-modelo/README.md):

```bash
cd caminho/para/tls/07-projeto-modelo
./criar-pki.sh --forcar
```

Depois **explique** cada uma destas saídas:

```bash
openssl x509 -in pki/ca.crt       -noout -ext basicConstraints,keyUsage
openssl x509 -in pki/servidor.crt -noout -ext extendedKeyUsage,subjectAltName
openssl x509 -in pki/admin.crt    -noout -ext extendedKeyUsage
openssl verify -CAfile pki/ca.crt pki/servidor.crt
awk -F'\t' '{print $1, $6}' pki/index.txt
```

**Desafio:** emita um certificado para `novo-servico.interno`, válido por 7 dias,
e faça `openssl verify` passar. (Dica: `emitir()` dentro do `criar-pki.sh`.)

**Verificação:** `openssl verify -CAfile pki/ca.crt novo.crt` retorna `OK`.

**Aprendizado:** uma CA é um par de chaves e uma **disciplina de processo**. A parte
difícil não é assinar — é registrar, restringir e conseguir revogar.

---

## Lab 4 — O handshake no fio

**Objetivo:** ver as mensagens do handshake, na ordem, com seus tamanhos.

```bash
cd ~/labs-tls/01
python3 -c "
import http.server,ssl,threading,time
ctx=ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER); ctx.load_cert_chain('c.pem','k.pem')
s=http.server.HTTPServer(('127.0.0.1',8443),http.server.SimpleHTTPRequestHandler)
s.socket=ctx.wrap_socket(s.socket,server_side=True)
threading.Thread(target=s.serve_forever,daemon=True).start(); time.sleep(60)
" &
sleep 1

sudo tshark -i lo -f "tcp port 8443" -w /tmp/hs.pcapng &
sleep 1
curl -s --cacert c.pem https://localhost:8443/ >/dev/null
sleep 1; sudo pkill tshark
```

```bash
tshark -r /tmp/hs.pcapng -Y tls.handshake -T fields \
  -e frame.number -e tls.handshake.type -e tls.record.length
# 1  = ClientHello        2  = ServerHello
# 8  = EncryptedExtensions  11 = Certificate
# 15 = CertificateVerify  20 = Finished
```

E o mesmo, sem Wireshark:

```bash
openssl s_client -connect 127.0.0.1:8443 -servername localhost \
  -CAfile c.pem -trace </dev/null 2>&1 | grep -E "^(Sent|Received) Record" -A3 | head -50
```

**Perguntas:** quantas mensagens você vê **em claro**? A partir de qual ponto o
`tshark` deixa de identificar o conteúdo? Onde está o certificado?

**Verificação:** você identifica `ClientHello` e `ServerHello` em claro, e observa que
o certificado **não** aparece legível (TLS 1.3 o cifra).

**Aprendizado:** [12-handshake.md](12-handshake.md) deixa de ser teoria.

---

## Lab 5 — Decifrar o próprio tráfego

**Objetivo:** entender o que `SSLKEYLOGFILE` faz — e por que ele é perigoso.

```bash
export SSLKEYLOGFILE=/tmp/keys.log
rm -f /tmp/keys.log
sudo tshark -i lo -f "tcp port 8443" -w /tmp/dec.pcapng &
sleep 1
curl -s --cacert ~/labs-tls/01/c.pem https://localhost:8443/ >/dev/null
sleep 1; sudo pkill tshark
cat /tmp/keys.log     # olhe: são os segredos da sessão, em texto
```

```bash
# sem as chaves: só bytes cifrados
tshark -r /tmp/dec.pcapng -Y "tls.app_data" | head -3
# com as chaves: o HTTP aparece
tshark -r /tmp/dec.pcapng -o "tls.keylog_file:/tmp/keys.log" -Y http -V | head -30
```

```bash
unset SSLKEYLOGFILE && rm -f /tmp/keys.log     # LIMPE
```

**Verificação:** você viu a requisição HTTP em texto claro dentro de uma captura de
tráfego TLS.

**Aprendizado:** quem tiver esse arquivo lê tudo. **Nunca** defina `SSLKEYLOGFILE`
no seu perfil de shell. E entenda que a mesma técnica é o que um proxy de inspeção faz,
por outros meios.

---

## Lab 6 — Quebrar de propósito

**Objetivo:** provocar seis falhas e reconhecer a mensagem de erro de cada uma.
**Este é o laboratório mais útil do arquivo.** Diagnosticar rápido é a habilidade prática.

Para cada item: provoque, anote a mensagem **literal**, explique a causa, conserte.

```bash
cd ~/labs-tls && mkdir -p 06 && cd 06

# (1) Nome errado ──────────────────────────────────────────────────────────
openssl req -x509 -newkey ec -pkeyopt ec_paramgen_curve:P-256 -nodes -days 30 \
  -keyout k1.pem -out c1.pem -subj "/CN=outro.local" -addext "subjectAltName=DNS:outro.local"
# suba um servidor com ele e acesse por https://localhost:8443/
# ESPERADO: "no alternative certificate subject name matches target host name"

# (2) Vencido ──────────────────────────────────────────────────────────────
# use o pki/vencido.crt do projeto-modelo, ou emita com -enddate no passado
# ESPERADO: "certificate has expired"

# (3) Chave trocada ────────────────────────────────────────────────────────
openssl genpkey -algorithm EC -pkeyopt ec_paramgen_curve:P-256 -out k2.pem
# tente subir o servidor com c1.pem + k2.pem
# ESPERADO: "key values mismatch"

# (4) Cadeia incompleta ────────────────────────────────────────────────────
# sirva só o cert.pem (sem intermediário) do projeto-modelo em vez do fullchain
# ESPERADO no cliente: "unable to get local issuer certificate"

# (5) Sem SAN (só CN) ──────────────────────────────────────────────────────
openssl req -x509 -newkey ec -pkeyopt ec_paramgen_curve:P-256 -nodes -days 30 \
  -keyout k5.pem -out c5.pem -subj "/CN=localhost"       # SEM -addext
# ESPERADO: o cliente recusa mesmo com o CN "certo"

# (6) TLS antigo ───────────────────────────────────────────────────────────
curl --tlsv1.0 --tls-max 1.0 https://localhost:8443/
# ESPERADO: erro de versão/protocolo
```

**Verificação:** você tem uma tabela pessoal com seis linhas: mensagem → causa → correção.
Compare com a tabela do [03 §14](03-instalacao.md#14-solução-de-problemas--erros-literais).

**Aprendizado:** você diagnostica 90% dos incidentes reais de TLS pela mensagem.

---

## Lab 7 — mTLS do zero

**Objetivo:** exigir certificado do cliente e ver o "não" acontecer no handshake.

```bash
cd caminho/para/tls/07-projeto-modelo
python3 servidor.py &
sleep 1
./cliente.py --como admin   saude      # 200
./cliente.py --como leitor  criar "x"  # 403  ← autorização, não autenticação
./cliente.py --como intruso saude      # HTTP 0 ← barrado no handshake
kill %1
```

**Desafio 1:** troque `ctx.verify_mode = ssl.CERT_REQUIRED` por `ssl.CERT_OPTIONAL`
em `servidor.py`. Rode `./cliente.py --como anonimo saude`. O que acontece?
Por que isso é um bug grave, e não uma "flexibilidade"?

**Desafio 2:** rode a suíte de testes e leia a classe `TesteAtaques`. Escreva **um teste
novo**: um cliente que apresenta o certificado do **servidor** como se fosse de cliente.
Ele deve falhar. Por quê? (dica: `extendedKeyUsage`)

**Verificação:** `./executar-testes.sh` continua em `OK` depois de você reverter o desafio 1.

**Aprendizado:** a diferença entre `CERT_REQUIRED` e `CERT_OPTIONAL` é a diferença
entre mTLS e teatro.

---

## Lab 8 — Revogação que funciona

**Objetivo:** revogar de verdade e ver a recusa.

```bash
cd caminho/para/tls/07-projeto-modelo

# 1. Com a CRL ligada, o "banido" é recusado
python3 servidor.py & sleep 1
./cliente.py --como banido saude        # certificate revoked
kill %1

# 2. Com a CRL DESLIGADA, ele entra
COFRE_CHECAR_CRL=0 python3 servidor.py & sleep 1
./cliente.py --como banido saude        # 200  ← a CRL era decoração
kill %1

# 3. Revogue o "escritor" e regenere a CRL
openssl ca -config pki/openssl-ca.cnf -revoke pki/escritor.crt -crl_reason superseded
openssl ca -config pki/openssl-ca.cnf -gencrl -out pki/ca.crl
cat pki/ca.crt pki/ca.crl > pki/ca-com-crl.pem

python3 servidor.py & sleep 1
./cliente.py --como escritor saude      # agora recusado
kill %1
```

```bash
openssl crl -in pki/ca.crl -noout -text | grep -A2 "Serial Number"
awk -F'\t' '$1=="R"{print "revogado:", $6}' pki/index.txt
```

**Verificação:** dois seriais na CRL, dois `R` no `index.txt`, dois clientes recusados.

**Aprendizado:** gerar CRL e **checar** CRL são coisas diferentes — e a checagem é uma
linha de código. Note também o `Next Update`: sua revogação só chega a quem baixa a CRL
depois da próxima publicação. Agora releia [15](15-validacao-revogacao-transparencia.md).

---

## Lab 9 — ACME de verdade (staging)

**Objetivo:** obter um certificado real, sem risco de bater em limite.
**Requer:** um domínio que você controla e uma máquina alcançável na porta 80 **ou**
acesso de API ao DNS.

```bash
sudo certbot certonly --standalone --staging \
  -d SEU.DOMINIO --agree-tos -m voce@exemplo.com --non-interactive
```

```bash
sudo openssl x509 -in /etc/letsencrypt/live/SEU.DOMINIO/cert.pem -noout -issuer -dates
# esperado: issuer com "(STAGING)" — é isso mesmo, e é bom
sudo ls -l /etc/letsencrypt/live/SEU.DOMINIO/
# cert.pem  chain.pem  fullchain.pem  privkey.pem  ← saiba o que é cada um
```

```bash
sudo certbot renew --dry-run
sudo systemctl list-timers | grep certbot
```

**Desafio:** aponte o nginx para `cert.pem` (errado) e depois para `fullchain.pem`
(certo). Compare com:

```bash
echo | openssl s_client -connect SEU.DOMINIO:443 -servername SEU.DOMINIO -showcerts 2>/dev/null | grep -c "BEGIN CERT"
```

**Verificação:** 1 certificado com `cert.pem`, 2 ou mais com `fullchain.pem`.

**Aprendizado:** o erro nº 1 do mundo real, provocado e corrigido por você.

---

## Lab 10 — Auditoria de configuração

**Objetivo:** auditar um servidor como um avaliador faria.

```bash
git clone --depth 1 https://github.com/testssl/testssl.sh.git ~/testssl.sh
~/testssl.sh/testssl.sh --quiet --protocols --server-defaults https://SEU.DOMINIO
```

Depois, à mão, com o script do [06 Exemplo 9](06-exemplos.md):

```bash
./audit-tls.sh SEU.DOMINIO
```

E online: <https://www.ssllabs.com/ssltest/>.

**Perguntas:** onde os três discordam? Qual dá o diagnóstico mais acionável?
Qual achado do SSL Labs você **não** vai corrigir, e por quê?

**Verificação:** você produz um relatório de uma página, com achado, severidade e ação
— separando o que é risco real do que é ruído para melhorar nota.

**Aprendizado:** ferramentas dão nota; **você** dá contexto. Perseguir A+ sem entender
é a armadilha nº 8 do [75](75-armadilhas.md).

---

## Lab 11 — Medir o custo do TLS

**Objetivo:** substituir a crença "TLS é lento" por números seus.

```bash
openssl speed -seconds 2 ecdsap256 rsa2048
openssl speed -seconds 2 -evp aes-128-gcm
openssl speed -seconds 2 -evp chacha20-poly1305
```

Handshakes por segundo, de verdade:

```bash
openssl s_time -connect localhost:8443 -CAfile ~/labs-tls/01/c.pem -new  -time 5
openssl s_time -connect localhost:8443 -CAfile ~/labs-tls/01/c.pem -reuse -time 5
```

**Compare** `-new` (handshake completo) com `-reuse` (sessão retomada). Anote a razão.

Latência ponta a ponta:

```bash
for i in 1 2 3; do
  curl -o /dev/null -s -w "dns:%{time_namelookup} conn:%{time_connect} tls:%{time_appconnect} total:%{time_total}\n" \
    https://SEU.DOMINIO/
done
```

`time_appconnect - time_connect` é **exatamente o custo do handshake TLS**.

**Verificação:** você sabe dizer, com número, quantos handshakes/s a sua máquina
sustenta e quanto a retomada economiza.

**Aprendizado:** o custo está no handshake, e ele é medível ([20 §1](20-desempenho-e-operacao.md)).

---

## Lab 12 — MITM controlado

> ⚠️ **Faça isto apenas na sua própria máquina ou na sua própria rede de laboratório,
> com dispositivos seus.** Interceptar tráfego de terceiros sem autorização é crime no
> Brasil (Lei 12.737/2012, e Marco Civil da Internet). O objetivo aqui é **defensivo**:
> entender como a interceptação funciona para reconhecê-la e se defender dela.

**Objetivo:** ver, na prática, o que acontece quando uma CA é instalada na máquina.

```bash
pipx install mitmproxy || pip install --user mitmproxy
mitmproxy --listen-port 8080 &
```

**Passo 1 — sem confiar na CA do mitmproxy:**

```bash
curl -x http://127.0.0.1:8080 https://example.com/
# ESPERADO: erro de certificado. É o TLS funcionando.
```

**Passo 2 — confiando nela (apenas para este comando, sem instalar no sistema):**

```bash
curl -x http://127.0.0.1:8080 --cacert ~/.mitmproxy/mitmproxy-ca-cert.pem https://example.com/
# ESPERADO: funciona — e o mitmproxy mostra a requisição inteira, em claro
```

**Observe** na interface do mitmproxy: cabeçalhos, cookies, corpo. Tudo legível.

```bash
echo | openssl s_client -proxy 127.0.0.1:8080 -connect example.com:443 2>/dev/null | openssl x509 -noout -issuer
# issuer = mitmproxy   ← a assinatura da interceptação
```

**Verificação:** você viu que basta **uma CA confiável a mais** para que o TLS
continue "funcionando" enquanto alguém lê tudo.

**Aprendizado:** esta é exatamente a mecânica do proxy corporativo
([03 §9](03-instalacao.md#9-rede-corporativa-proxy-e-certificado-interno)), do Superfish,
e do que o *pinning* tenta impedir ([06 Exemplo 7](06-exemplos.md)). E é o motivo pelo
qual "cadeado = seguro" é falso: a segurança depende de **em quem a sua máquina confia**.

Limpe ao terminar:

```bash
pkill mitmproxy
```

---

## Trilha sugerida

| Você é… | Faça |
|---|---|
| iniciante | 1 → 2 → 3 → 6 |
| dev de aplicação | 1 → 2 → 6 → 7 → 11 |
| sysadmin / SRE | 3 → 6 → 8 → 9 → 10 → 11 |
| segurança | todos, com ênfase em 5, 6, 8, 12 |

---

## Autoteste geral

1. Cite os quatro modos de falha de certificado que o Lab 2 exercita.
2. Por que `incomplete-chain` falha no curl e funciona no navegador?
3. O que muda entre gerar uma CRL e **checar** uma CRL?
4. `SSLKEYLOGFILE` — o que faz, e por que jamais deixá-lo no `.bashrc`?
5. `CERT_OPTIONAL` em vez de `CERT_REQUIRED`: qual é a consequência exata?
6. Qual comando do curl mede isoladamente o custo do handshake TLS?
7. Por que o Lab 12 prova que "cadeado ≠ seguro"?
8. Depois do Lab 6, escreva de memória três mensagens de erro e suas causas.

---

**Próximo:** [75-armadilhas.md](75-armadilhas.md) — os erros que todo mundo comete.
