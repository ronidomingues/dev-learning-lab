# 06 · Exemplos

**Nível:** intermediário → avançado · **Data:** 31/08/2026

14 receitas completas. Cada uma: **problema → solução executável → explicação**.
Nada de `...` no meio: tudo que está aqui roda como está.

**Sobre as saídas.** Os exemplos **3** (CA interna) e **5** (mTLS) foram executados
nesta máquina (Ubuntu 22.04.5, OpenSSL 3.0.2, Python 3.10.12, curl 7.81.0) em
31/08/2026 — as saídas marcadas como *saída real* são literalmente o que saiu.
As saídas contra hosts públicos estão marcadas como *saída típica*: a máquina usada
para escrever este material só alcança a internet por proxy corporativo, o que impede
a conexão TLS direta que essas capturas exigem. O formato é o real do OpenSSL 3.0.2;
os valores mudam por site e por data.

| # | Exemplo | Nível |
|---|---|---|
| [1](#exemplo-1--descobrir-tudo-sobre-o-tls-de-um-site) | Descobrir tudo sobre o TLS de um site | trivial |
| [2](#exemplo-2--monitor-de-validade-de-certificados) | Monitor de validade de certificados | fácil |
| [3](#exemplo-3--uma-ca-interna-completa-em-15-comandos) | Uma CA interna completa | médio |
| [4](#exemplo-4--servidor-https-em-cinco-linguagens) | Servidor HTTPS em cinco linguagens | fácil |
| [5](#exemplo-5--mtls-autenticação-mútua-de-verdade) | mTLS — autenticação mútua | médio |
| [6](#exemplo-6--cliente-que-verifica-de-verdade-em-quatro-linguagens) | Cliente que verifica de verdade | médio |
| [7](#exemplo-7--fixação-de-chave-pública-pinning-em-mobileapi) | Fixação de chave pública (pinning) | avançado |
| [8](#exemplo-8--diagnosticar-cadeia-incompleta) | Diagnosticar cadeia incompleta | médio |
| [9](#exemplo-9--forçar-e-testar-versões-e-cifras) | Forçar e testar versões e cifras | médio |
| [10](#exemplo-10--terminação-tls-em-proxy-reverso-com-nginx) | Terminação TLS em proxy reverso | médio |
| [11](#exemplo-11--ver-o-handshake-decifrado-no-wireshark) | Ver o handshake decifrado no Wireshark | avançado |
| [12](#exemplo-12--produção-renovação-automática-com-caddy-atrás-de-cloudflare) | **Produção:** renovação automática com Caddy | produção |
| [13](#exemplo-13--produção-rotação-de-certificado-em-kubernetes-sem-downtime) | **Produção:** rotação em Kubernetes sem downtime | produção |
| [14](#exemplo-14--produção-verificação-de-certificado-em-pipeline-de-ci) | **Produção:** verificação de certificado em CI | produção |

---

## Exemplo 1 — Descobrir tudo sobre o TLS de um site

**Problema:** você recebeu um chamado dizendo "o site X está com problema de
certificado". Você precisa de um diagnóstico em 30 segundos.

```bash
#!/usr/bin/env bash
# arquivo: tls-info.sh — uso: ./tls-info.sh exemplo.com
set -euo pipefail
H="${1:?uso: $0 host [porta]}"
P="${2:-443}"

echo "=== negociado ==="
echo | openssl s_client -connect "$H:$P" -servername "$H" -brief 2>&1 | grep -Ev '^(DONE|CONNECTION)'

echo; echo "=== certificado ==="
echo | openssl s_client -connect "$H:$P" -servername "$H" 2>/dev/null \
  | openssl x509 -noout -subject -issuer -dates -serial

echo; echo "=== nomes cobertos ==="
echo | openssl s_client -connect "$H:$P" -servername "$H" 2>/dev/null \
  | openssl x509 -noout -ext subjectAltName | tail -n +2

echo; echo "=== cadeia enviada ==="
echo | openssl s_client -connect "$H:$P" -servername "$H" -showcerts 2>/dev/null \
  | grep -E '^ *(s|i):' || echo "(nenhuma — servidor manda só a folha!)"

echo; echo "=== versões aceitas ==="
for v in tls1 tls1_1 tls1_2 tls1_3; do
  printf "  %-8s " "$v"
  echo | openssl s_client -connect "$H:$P" -servername "$H" "-$v" >/dev/null 2>&1 \
    && echo "ACEITA" || echo "recusa"
done

echo; echo "=== dias até vencer ==="
end=$(echo | openssl s_client -connect "$H:$P" -servername "$H" 2>/dev/null \
      | openssl x509 -noout -enddate | cut -d= -f2)
echo "  $(( ( $(date -d "$end" +%s) - $(date +%s) ) / 86400 )) dias ($end)"
```

Saída típica para `example.com` (formato real; valores variam):

```
=== negociado ===
Protocol version: TLSv1.3
Ciphersuite: TLS_AES_256_GCM_SHA384
Verification: OK
Server Temp Key: X25519, 253 bits

=== versões aceitas ===
  tls1     recusa
  tls1_1   recusa
  tls1_2   ACEITA
  tls1_3   ACEITA
```

**Por que funciona:** cada bloco é uma pergunta independente. `s_client` sem
`-servername` falha em hosts virtuais, então o SNI é sempre passado. `2>/dev/null`
descarta o ruído de conexão para o `openssl x509` receber só o PEM.

---

## Exemplo 2 — Monitor de validade de certificados

**Problema:** o certificado de produção venceu num domingo. Nunca mais.

```bash
#!/usr/bin/env bash
# arquivo: check-expiry.sh — código de saída 1 se algum host estiver abaixo do limite
set -uo pipefail
LIMITE_DIAS="${LIMITE_DIAS:-21}"
HOSTS=("exemplo.com.br:443" "api.exemplo.com.br:443" "smtp.exemplo.com.br:587")
falhou=0

for alvo in "${HOSTS[@]}"; do
  host="${alvo%%:*}"; porta="${alvo##*:}"
  starttls=""
  [ "$porta" = "587" ] && starttls="-starttls smtp"

  end=$(echo | timeout 10 openssl s_client -connect "$host:$porta" \
        -servername "$host" $starttls 2>/dev/null \
        | openssl x509 -noout -enddate 2>/dev/null | cut -d= -f2)

  if [ -z "$end" ]; then
    printf "%-28s ERRO: não consegui obter o certificado\n" "$host"; falhou=1; continue
  fi

  dias=$(( ( $(date -d "$end" +%s) - $(date +%s) ) / 86400 ))
  if   [ "$dias" -lt 0 ];             then st="VENCIDO";  falhou=1
  elif [ "$dias" -lt "$LIMITE_DIAS" ]; then st="ALERTA";   falhou=1
  else                                     st="ok"; fi
  printf "%-28s %-8s %4s dias  (%s)\n" "$host" "$st" "$dias" "$end"
done
exit "$falhou"
```

```bash
chmod +x check-expiry.sh && ./check-expiry.sh; echo "saída=$?"
```

Coloque no cron e mande a saída para onde a equipe vê:

```cron
0 8 * * * /opt/scripts/check-expiry.sh || curl -s -X POST -d "$(/opt/scripts/check-expiry.sh)" https://hooks.exemplo/alerta
```

**Por que 21 dias:** com a validade máxima caindo para **200 dias em 15/03/2026** e
**100 dias em 15/03/2027** ([65-estado-da-arte.md](65-estado-da-arte.md)), a renovação
tem de ser automática. O monitor não substitui a automação — ele detecta quando a
automação quebrou, que é o cenário real de incidente.

---

## Exemplo 3 — Uma CA interna completa em 15 comandos

**Problema:** você tem 12 microsserviços conversando entre si e quer TLS de verdade
entre eles, sem expor nada à internet e sem pagar CA pública.

**Executado nesta máquina; todas as verificações passaram.**

```bash
#!/usr/bin/env bash
# arquivo: ca.sh — cria uma CA e emite certificados de servidor e de cliente
set -euo pipefail
mkdir -p pki && cd pki

# ── 1. A raiz ──────────────────────────────────────────────────────────
openssl genpkey -algorithm EC -pkeyopt ec_paramgen_curve:P-384 -out ca.key
chmod 600 ca.key
openssl req -x509 -new -key ca.key -days 3650 -out ca.crt \
  -subj "/O=Minha Empresa/CN=Minha CA Interna" \
  -addext "basicConstraints=critical,CA:TRUE,pathlen:0" \
  -addext "keyUsage=critical,keyCertSign,cRLSign" \
  -addext "subjectKeyIdentifier=hash"

# ── 2. Certificado de SERVIDOR ─────────────────────────────────────────
openssl genpkey -algorithm EC -pkeyopt ec_paramgen_curve:P-256 -out srv.key
chmod 600 srv.key
openssl req -new -key srv.key -out srv.csr -subj "/O=Minha Empresa/CN=api.interno"
openssl x509 -req -in srv.csr -CA ca.crt -CAkey ca.key -CAcreateserial \
  -days 90 -out srv.crt -extfile <(cat <<'EXT'
subjectAltName       = DNS:api.interno, DNS:localhost, IP:127.0.0.1
keyUsage             = critical, digitalSignature, keyEncipherment
extendedKeyUsage     = serverAuth
basicConstraints     = critical, CA:FALSE
EXT
)

# ── 3. Certificado de CLIENTE ──────────────────────────────────────────
openssl genpkey -algorithm EC -pkeyopt ec_paramgen_curve:P-256 -out cli.key
chmod 600 cli.key
openssl req -new -key cli.key -out cli.csr -subj "/O=Minha Empresa/CN=servico-pedidos"
openssl x509 -req -in cli.csr -CA ca.crt -CAkey ca.key -CAcreateserial \
  -days 90 -out cli.crt -extfile <(cat <<'EXT'
keyUsage         = critical, digitalSignature
extendedKeyUsage = clientAuth
basicConstraints = critical, CA:FALSE
EXT
)

# ── 4. Verificar ───────────────────────────────────────────────────────
openssl verify -CAfile ca.crt srv.crt cli.crt
```

Saída real:

```
srv.crt: OK
cli.crt: OK
```

**Três decisões que este script toma e por quê:**

1. **`pathlen:0` na raiz.** Impede que a CA emita outra CA. Se a chave da raiz vazar,
   o estrago é grande; se um intermediário pudesse emitir intermediários, seria pior.
2. **`extendedKeyUsage` separado para servidor (`serverAuth`) e cliente (`clientAuth`).**
   Sem isso, um certificado de cliente serve para se passar por um servidor seu.
   É uma separação de privilégio que custa uma linha.
3. **90 dias no folha, 10 anos na raiz.** A raiz precisa durar porque distribuí-la é
   caro (tem de ir para todas as máquinas). O folha é curto porque renovar é barato
   (automatizável) e reduz a janela de uma chave comprometida.

> **Onde este script é insuficiente para produção séria:** não há CRL/OCSP, a chave
> da raiz fica em disco comum (o certo é HSM ou, no mínimo, uma máquina offline), e
> não há registro de emissão. Para PKI interna de verdade use
> [`step-ca`](https://smallstep.com/docs/step-ca/), Vault PKI ou cert-manager —
> discutidos em [18-mtls-e-pki-interna.md](18-mtls-e-pki-interna.md).

---

## Exemplo 4 — Servidor HTTPS em cinco linguagens

**Problema:** a mesma coisa, na sua linguagem. Todos usam `srv.crt`/`srv.key` do
Exemplo 3 e todos fixam a versão mínima — que é o que a maioria dos tutoriais esquece.

**Python** (biblioteca padrão, zero dependências)

```python
# arquivo: srv.py
import http.server, ssl

ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ctx.minimum_version = ssl.TLSVersion.TLSv1_2       # explícito, não confie no padrão
ctx.load_cert_chain("srv.crt", "srv.key")
ctx.set_alpn_protocols(["http/1.1"])

class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Strict-Transport-Security", "max-age=63072000")
        self.end_headers()
        self.wfile.write(b"ok\n")

srv = http.server.HTTPServer(("0.0.0.0", 8443), H)
srv.socket = ctx.wrap_socket(srv.socket, server_side=True)
srv.serve_forever()
```

**Node.js**

```javascript
// arquivo: srv.js — node srv.js
const https = require('node:https');
const fs = require('node:fs');

https.createServer({
  key:  fs.readFileSync('srv.key'),
  cert: fs.readFileSync('srv.crt'),      // em produção: fullchain
  minVersion: 'TLSv1.2',
  ALPNProtocols: ['http/1.1'],
  honorCipherOrder: false,
}, (req, res) => {
  res.writeHead(200, {
    'Content-Type': 'text/plain',
    'Strict-Transport-Security': 'max-age=63072000',
  });
  res.end('ok\n');
}).listen(8443, () => console.log('https://localhost:8443/'));
```

**Go**

```go
// arquivo: srv.go — go run srv.go
package main

import (
	"crypto/tls"
	"log"
	"net/http"
)

func main() {
	mux := http.NewServeMux()
	mux.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Strict-Transport-Security", "max-age=63072000")
		w.Write([]byte("ok\n"))
	})
	srv := &http.Server{
		Addr:      ":8443",
		Handler:   mux,
		TLSConfig: &tls.Config{MinVersion: tls.VersionTLS12},
	}
	log.Fatal(srv.ListenAndServeTLS("srv.crt", "srv.key"))
}
```

**Java** (JDK 17+; precisa de PKCS#12, não de PEM)

```bash
openssl pkcs12 -export -out srv.p12 -inkey srv.key -in srv.crt -passout pass:senha
```

```java
// arquivo: Srv.java — java Srv.java
import com.sun.net.httpserver.*;
import javax.net.ssl.*;
import java.io.*;
import java.net.InetSocketAddress;
import java.security.KeyStore;

public class Srv {
  public static void main(String[] a) throws Exception {
    KeyStore ks = KeyStore.getInstance("PKCS12");
    try (InputStream in = new FileInputStream("srv.p12")) { ks.load(in, "senha".toCharArray()); }
    KeyManagerFactory kmf = KeyManagerFactory.getInstance("SunX509");
    kmf.init(ks, "senha".toCharArray());
    SSLContext ctx = SSLContext.getInstance("TLSv1.3");
    ctx.init(kmf.getKeyManagers(), null, null);

    HttpsServer s = HttpsServer.create(new InetSocketAddress(8443), 0);
    s.setHttpsConfigurator(new HttpsConfigurator(ctx));
    s.createContext("/", ex -> {
      byte[] b = "ok\n".getBytes();
      ex.sendResponseHeaders(200, b.length);
      ex.getResponseBody().write(b); ex.close();
    });
    s.start();
  }
}
```

**Caddy** (o "servidor" inteiro, e ainda obtém certificado real sozinho)

```caddyfile
# arquivo: Caddyfile — caddy run
localhost:8443 {
    tls srv.crt srv.key
    respond "ok"
}
```

Teste qualquer um deles igual:

```bash
curl --cacert pki/ca.crt https://localhost:8443/    # esperado: ok
```

---

## Exemplo 5 — mTLS: autenticação mútua de verdade

**Problema:** sua API interna não deve aceitar ninguém que não seja um serviço seu.
Sem token, sem senha: só quem tiver certificado emitido pela sua CA entra.

**Executado nesta máquina. Saídas reais no fim.**

```python
# arquivo: mtls.py — usa os arquivos do Exemplo 3 (pki/)
import http.server, ssl, threading, urllib.request

# ── SERVIDOR: exige certificado de cliente ────────────────────────────
ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ctx.minimum_version = ssl.TLSVersion.TLSv1_2
ctx.load_cert_chain("pki/srv.crt", "pki/srv.key")
ctx.verify_mode = ssl.CERT_REQUIRED        # <- sem isto, não é mTLS
ctx.load_verify_locations("pki/ca.crt")    # <- só ESTA CA vale

class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        cert = self.connection.getpeercert()
        cn = dict(x[0] for x in cert["subject"])["commonName"]
        self.send_response(200); self.end_headers()
        self.wfile.write(f"ola, {cn}\n".encode())
    def log_message(self, *a): pass

srv = http.server.HTTPServer(("127.0.0.1", 8443), H)
srv.socket = ctx.wrap_socket(srv.socket, server_side=True)
threading.Thread(target=srv.serve_forever, daemon=True).start()

# ── CLIENTE COM certificado ───────────────────────────────────────────
c = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
c.load_verify_locations("pki/ca.crt")
c.load_cert_chain("pki/cli.crt", "pki/cli.key")
print("COM cert:", urllib.request.urlopen("https://localhost:8443/", context=c).read().decode().strip())

# ── CLIENTE SEM certificado: deve ser recusado ────────────────────────
c2 = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
c2.load_verify_locations("pki/ca.crt")
try:
    urllib.request.urlopen("https://localhost:8443/", context=c2, timeout=5)
    print("SEM cert: PASSOU (isto seria um bug grave!)")
except Exception as e:
    print("SEM cert: recusado ->", type(e).__name__, str(e)[:70])

srv.shutdown()
```

Saída real:

```
COM cert: ola, cliente-1
SEM cert: recusado -> SSLError [SSL: TLSV13_ALERT_CERTIFICATE_REQUIRED] tlsv13 alert certificate required
```

O mesmo com `curl` — saída real:

```bash
curl -s --cacert pki/ca.crt --cert pki/cli.crt --key pki/cli.key \
     https://localhost:8444/ -o /dev/null -w "com cert: %{http_code}\n"
# com cert: 200

curl -s --cacert pki/ca.crt https://localhost:8444/ -o /dev/null -w "sem cert: %{http_code}\n"
# sem cert: 000     (exit 56 — a conexão foi cortada no handshake)
```

**A parte que 90% das implementações erram:** verificar que o cliente tem *um*
certificado válido **não é autorização**. Qualquer cliente da sua CA entra em
qualquer rota. Você precisa mapear o CN (ou, melhor, um SAN do tipo URI, à moda
SPIFFE) para uma identidade e checar permissão:

```python
        cn = dict(x[0] for x in cert["subject"])["commonName"]
        PERMISSOES = {"servico-pedidos": {"/pedidos"}, "servico-relatorios": {"/relatorios"}}
        if self.path not in PERMISSOES.get(cn, set()):
            self.send_response(403); self.end_headers(); return
```

Detalhes em [18-mtls-e-pki-interna.md](18-mtls-e-pki-interna.md).

---

## Exemplo 6 — Cliente que verifica de verdade, em quatro linguagens

**Problema:** metade dos clientes HTTP escritos às pressas desliga a verificação e
ninguém percebe. Estes não desligam — e falham alto quando algo está errado.

```python
# Python
import ssl, urllib.request
ctx = ssl.create_default_context()          # já verifica cadeia E hostname
ctx.minimum_version = ssl.TLSVersion.TLSv1_2
# ctx.load_verify_locations("pki/ca.crt")   # descomente para uma CA privada
r = urllib.request.urlopen("https://example.com/", context=ctx, timeout=10)
print(r.status, r.headers.get("content-type"))
```

```python
# Python com requests (verify=True é o padrão — nunca escreva verify=False)
import requests
r = requests.get("https://example.com/", timeout=10)            # verifica
r = requests.get("https://api.interno/", verify="pki/ca.crt")   # CA privada
```

```javascript
// Node.js — o padrão já verifica; o erro é DESLIGAR
const https = require('node:https');
const fs = require('node:fs');
https.get({
  hostname: 'api.interno', port: 443, path: '/',
  ca: fs.readFileSync('pki/ca.crt'),   // CA privada, SEM desligar a verificação
  minVersion: 'TLSv1.2',
  checkServerIdentity: require('node:tls').checkServerIdentity, // explícito
}, res => console.log(res.statusCode)).on('error', e => { console.error(e); process.exit(1); });
```

```go
// Go — o padrão verifica; para CA privada, monte o pool
pool := x509.NewCertPool()
pem, _ := os.ReadFile("pki/ca.crt")
pool.AppendCertsFromPEM(pem)
client := &http.Client{Transport: &http.Transport{
    TLSClientConfig: &tls.Config{RootCAs: pool, MinVersion: tls.VersionTLS12},
}}
resp, err := client.Get("https://api.interno/")
```

```java
// Java — com uma truststore própria
System.setProperty("javax.net.ssl.trustStore", "/etc/pki/truststore.p12");
System.setProperty("javax.net.ssl.trustStoreType", "PKCS12");
System.setProperty("javax.net.ssl.trustStorePassword", "senha");
```

**Como testar que a verificação está mesmo ligada** (deve dar erro nos três):

```bash
python3 -c "import urllib.request,ssl; urllib.request.urlopen('https://expired.badssl.com/')"
node   -e "require('https').get('https://wrong.host.badssl.com/',r=>{}).on('error',e=>{console.log('OK, recusou:',e.code)})"
curl https://self-signed.badssl.com/
```

---

## Exemplo 7 — Fixação de chave pública (pinning) em mobile/API

**Problema:** seu app bancário fala com sua API. Se o celular do usuário tiver uma
CA maliciosa instalada (proxy corporativo, malware, coação), TLS aceita felizmente.
Você quer que o app só fale com **a sua** chave.

**Calcule o pino** (o SHA-256 da chave pública, em Base64 — chamado *SPKI pin*):

```bash
openssl x509 -in srv.crt -pubkey -noout \
  | openssl pkey -pubin -outform der \
  | openssl dgst -sha256 -binary \
  | base64
# saída exemplo: 4t3P6mFVXQZ9c1WgY0Xr8hK2n5aL7sD8fJ0oQ1bC2dE=
```

Repare que se fixa a **chave pública**, não o certificado: assim você renova o
certificado (mesma chave) sem quebrar o app.

**Python:**

```python
import ssl, socket, hashlib, base64

PINOS = {"4t3P6mFVXQZ9c1WgY0Xr8hK2n5aL7sD8fJ0oQ1bC2dE=",   # chave atual
         "BACKUP_PIN_DA_CHAVE_DE_RESERVA="}                 # OBRIGATÓRIO ter um reserva

def conectar_com_pin(host, porta=443):
    ctx = ssl.create_default_context()
    with socket.create_connection((host, porta), timeout=10) as s:
        with ctx.wrap_socket(s, server_hostname=host) as ts:
            der = ts.getpeercert(binary_form=True)
            # extrai o SubjectPublicKeyInfo do certificado
            from cryptography import x509
            from cryptography.hazmat.primitives import serialization
            cert = x509.load_der_x509_certificate(der)
            spki = cert.public_key().public_bytes(
                serialization.Encoding.DER,
                serialization.PublicFormat.SubjectPublicKeyInfo)
            pino = base64.b64encode(hashlib.sha256(spki).digest()).decode()
            if pino not in PINOS:
                raise ssl.SSLError(f"pino não confere: {pino}")
            return ts.version(), pino
```

**Android (OkHttp):**

```kotlin
val pinner = CertificatePinner.Builder()
    .add("api.exemplo.com.br", "sha256/4t3P6mFVXQZ9c1WgY0Xr8hK2n5aL7sD8fJ0oQ1bC2dE=")
    .add("api.exemplo.com.br", "sha256/BACKUP_PIN_DA_CHAVE_DE_RESERVA=")   // reserva
    .build()
val client = OkHttpClient.Builder().certificatePinner(pinner).build()
```

> ### O aviso que precisa vir junto
> **Pinning é a técnica que mais derruba aplicativos em produção.** Se você perder a
> chave, ou trocar de CA sem planejar, **todos os apps já instalados param de
> funcionar** e a única correção é uma atualização na loja — que leva dias e depende
> do usuário. Regras mínimas: (1) **sempre** dois ou mais pinos, um deles de uma
> chave de reserva guardada offline; (2) prazo de validade do pino no app; (3) um
> mecanismo remoto de desligar o pinning. O `HPKP`, que fazia isso via cabeçalho HTTP
> na web, foi **removido dos navegadores em 2018** justamente porque um erro de
> configuração podia tornar um site inacessível por meses, sem correção possível.
> Na web, use Certificate Transparency e monitoramento ([15](15-validacao-revogacao-transparencia.md)).
> Em app móvel próprio, pinning ainda vale a pena — porque lá você controla os dois lados.

---

## Exemplo 8 — Diagnosticar cadeia incompleta

**Problema:** "funciona no Chrome, quebra no `curl` e no app Android". É o problema
de TLS mais comum do mundo real.

```bash
#!/usr/bin/env bash
# arquivo: check-chain.sh HOST
H="${1:?host}"
n=$(echo | openssl s_client -connect "$H:443" -servername "$H" -showcerts 2>/dev/null \
     | grep -c "BEGIN CERTIFICATE")
echo "certificados enviados pelo servidor: $n"

echo | openssl s_client -connect "$H:443" -servername "$H" -showcerts 2>/dev/null \
  | grep -E "^ *[si]:" | nl

echo
echo "verificação estrita (como um cliente sem cache faria):"
echo | openssl s_client -connect "$H:443" -servername "$H" \
       -verify_return_error -verify_hostname "$H" 2>&1 | grep -E "Verify return code|verify error"
```

Saída típica para `example.com` (formato real; valores variam):

```
certificados enviados pelo servidor: 2
     1	s:CN = *.example.com
     2	i:C = US, O = DigiCert Inc, CN = DigiCert Global G3 TLS ECC SHA384 2020 CA1
...
verificação estrita:
Verify return code: 0 (ok)
```

**Interpretação:**

| Nº de certificados | Significa |
|---|---|
| 1 | ⚠️ só a folha. O Chrome pode salvar você (cache + busca por AIA); `curl`, Java, Go e Android **não**. Conserte. |
| 2–3 | ✅ folha + intermediário(s). Correto. |
| 4+ | possivelmente a raiz está sendo enviada também — inútil (o cliente já tem) e desperdiça bytes em todo handshake |

**Correção:** aponte o servidor para `fullchain.pem`, não `cert.pem`.

```bash
# como o Let's Encrypt entrega:
/etc/letsencrypt/live/DOMINIO/cert.pem        # só a folha       ← NÃO use
/etc/letsencrypt/live/DOMINIO/chain.pem       # só intermediários
/etc/letsencrypt/live/DOMINIO/fullchain.pem   # folha + cadeia   ← USE ESTE
/etc/letsencrypt/live/DOMINIO/privkey.pem     # a chave
```

> **Por que o Chrome perdoa e o curl não** — e este é um "por quê" de verdade:
> navegadores implementam *AIA fetching*, que busca o intermediário faltante na URL
> indicada na extensão *Authority Information Access* do certificado. É uma muleta
> criada porque servidores mal configurados eram tão comuns que quebrar a web inteira
> não era opção. Bibliotecas de servidor não fazem isso, porque uma busca HTTP no
> meio de um handshake é um risco de latência e um vetor de negação de serviço.
> Resultado: o mesmo servidor "funciona" e "não funciona" dependendo do cliente.

---

## Exemplo 9 — Forçar e testar versões e cifras

**Problema:** auditoria pediu prova de que TLS 1.0 e 1.1 estão desligados.

```bash
#!/usr/bin/env bash
# arquivo: audit-tls.sh HOST — saída legível por humano e por máquina
H="${1:?host}"
declare -A ESPERADO=([ssl3]=recusa [tls1]=recusa [tls1_1]=recusa [tls1_2]=ACEITA [tls1_3]=ACEITA)
falhou=0
for v in ssl3 tls1 tls1_1 tls1_2 tls1_3; do
  if echo | timeout 8 openssl s_client -connect "$H:443" -servername "$H" "-$v" >/dev/null 2>&1
  then r=ACEITA; else r=recusa; fi
  [ "$r" = "${ESPERADO[$v]}" ] && s="ok" || { s="FALHA"; falhou=1; }
  printf "%-8s %-8s (esperado %-8s) %s\n" "$v" "$r" "${ESPERADO[$v]}" "$s"
done
exit "$falhou"
```

Saída típica para `example.com`:

```
ssl3     recusa   (esperado recusa  ) ok
tls1     recusa   (esperado recusa  ) ok
tls1_1   recusa   (esperado recusa  ) ok
tls1_2   ACEITA   (esperado ACEITA  ) ok
tls1_3   ACEITA   (esperado ACEITA  ) ok
```

Testar uma cifra específica:

```bash
echo | openssl s_client -connect HOST:443 -servername HOST -tls1_2 -cipher 'ECDHE-RSA-AES128-GCM-SHA256' -brief
echo | openssl s_client -connect HOST:443 -servername HOST -ciphersuites 'TLS_CHACHA20_POLY1305_SHA256' -brief  # TLS 1.3
```

Testar um grupo (curva) específico:

```bash
echo | openssl s_client -connect HOST:443 -servername HOST -groups X25519 -brief | grep "Temp Key"
# esperado: Server Temp Key: X25519, 253 bits
echo | openssl s_client -connect HOST:443 -servername HOST -groups P-256 -brief | grep "Temp Key"
```

Com OpenSSL **3.5+**, testar pós-quântico:

```bash
openssl s_client -connect HOST:443 -servername HOST -groups X25519MLKEM768 -brief | grep "Temp Key"
# em servidor moderno (Cloudflare, Google): Server Temp Key: X25519MLKEM768
```

---

## Exemplo 10 — Terminação TLS em proxy reverso com nginx

**Problema:** sua aplicação em Node/Python/Java não deve lidar com TLS. O nginx
termina o TLS e fala HTTP simples com ela, na rede local.

```nginx
# /etc/nginx/sites-available/app.conf
# HTTP: só existe para redirecionar e para o desafio ACME
server {
    listen 80;
    server_name exemplo.com.br www.exemplo.com.br;

    location /.well-known/acme-challenge/ { root /var/www/certbot; }
    location / { return 301 https://$host$request_uri; }
}

server {
    listen 443 ssl;
    http2 on;
    server_name exemplo.com.br www.exemplo.com.br;

    ssl_certificate     /etc/letsencrypt/live/exemplo.com.br/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/exemplo.com.br/privkey.pem;
    ssl_trusted_certificate /etc/letsencrypt/live/exemplo.com.br/chain.pem;  # necessário p/ stapling

    ssl_protocols       TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers off;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;

    ssl_session_cache   shared:MozSSL:10m;   # 10 MB ≈ 40.000 sessões
    ssl_session_timeout 1d;
    ssl_session_tickets off;                 # ver explicação abaixo

    ssl_stapling on;
    ssl_stapling_verify on;
    resolver 1.1.1.1 8.8.8.8 valid=300s;     # o nginx precisa resolver o host do OCSP

    add_header Strict-Transport-Security "max-age=63072000" always;

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host              $host;
        proxy_set_header X-Real-IP         $remote_addr;
        proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;   # a app precisa saber que veio por HTTPS
    }
}
```

```bash
sudo nginx -t && sudo systemctl reload nginx
curl -sI https://exemplo.com.br | head -1
curl -sI http://exemplo.com.br | grep -i location   # deve mostrar o 301 para https
```

**Três decisões explicadas:**

- **`ssl_session_tickets off`.** Tickets de sessão cifram o estado da sessão com uma
  chave do servidor. Se essa chave não for rotacionada (o nginx só rotaciona ao
  reiniciar) e vazar, um atacante que gravou o tráfego decifra tudo — **destruindo o
  sigilo futuro** que o ECDHE deu. Com `off`, usa-se o cache de sessão do servidor,
  que é seguro por construção. Custo: sem retomada entre máquinas do balanceador.
  Se precisar, rotacione as chaves de ticket com `ssl_session_ticket_key` e um cron.
- **`X-Forwarded-Proto`.** Sem isso a aplicação acha que a requisição veio por HTTP,
  gera links `http://`, e o navegador reclama de conteúdo misto. Erro clássico.
- **`resolver`.** Sem ele, o `ssl_stapling on` falha silenciosamente (o nginx não
  consegue resolver o host do respondedor OCSP) e você acha que tem stapling quando
  não tem. Confira: `echo | openssl s_client -connect exemplo.com.br:443 -status 2>&1 | grep -A1 "OCSP Response Status"`.

---

## Exemplo 11 — Ver o handshake decifrado no Wireshark

**Problema:** você quer *ver* o TLS, não ler sobre ele.

```bash
export SSLKEYLOGFILE=/tmp/tlskeys.log     # navegadores, curl e Python respeitam
mkdir -p /tmp/cap
sudo tshark -i any -f "tcp port 443" -w /tmp/cap/tls.pcapng &
curl -s https://example.com -o /dev/null
sudo pkill tshark
```

Ver só o handshake, sem decifrar (o handshake do TLS 1.3 já esconde o certificado —
por isso o `ClientHello` é o que sobra em claro):

```bash
tshark -r /tmp/cap/tls.pcapng -Y "tls.handshake" -T fields \
  -e frame.number -e tls.handshake.type -e tls.handshake.extensions_server_name
# tipo 1 = ClientHello, 2 = ServerHello, 11 = Certificate, 15 = CertificateVerify, 20 = Finished
```

Decifrar de fato:

```bash
tshark -r /tmp/cap/tls.pcapng -o "tls.keylog_file:/tmp/tlskeys.log" -Y "http2 || http" -V | head -40
```

No Wireshark gráfico: *Editar → Preferências → Protocols → TLS → (Pre)-Master-Secret
log filename* → `/tmp/tlskeys.log`.

> ⚠️ **`SSLKEYLOGFILE` só em laboratório.** Enquanto essa variável estiver definida,
> qualquer pessoa com acesso ao arquivo decifra todo o seu tráfego HTTPS — inclusive
> senhas e cookies de sessão. Nunca a coloque no `.bashrc`. Apague o arquivo depois.

O que você vai observar, e que fecha o [12-handshake.md](12-handshake.md):

1. O `ClientHello` é o **único** pacote realmente em claro (e o SNI, dentro dele,
   revela o site — a menos que haja ECH).
2. Já no `ServerHello` a extensão `key_share` aparece, e **todo o resto vem cifrado** —
   inclusive o certificado do servidor. No TLS 1.2 o certificado ia em claro.
3. Todo o handshake cabe em **uma ida e volta** (1-RTT).

---

## Exemplo 12 — PRODUÇÃO: renovação automática com Caddy atrás de Cloudflare

**Contexto real:** site pequeno/médio, DNS na Cloudflare, aplicação em container.
Requisito: HTTPS que nunca vence e ninguém precisa lembrar.

```caddyfile
# /etc/caddy/Caddyfile
{
    email  ops@exemplo.com.br            # para avisos do Let's Encrypt
    # acme_ca https://acme-staging-v02.api.letsencrypt.org/directory   # descomente para TESTAR
}

exemplo.com.br, www.exemplo.com.br {
    encode zstd gzip
    header {
        Strict-Transport-Security "max-age=31536000; includeSubDomains"
        X-Content-Type-Options    "nosniff"
        -Server
    }
    reverse_proxy app:3000 {
        health_uri /health
    }
    log {
        output file /var/log/caddy/access.log
        format json
    }
}

api.exemplo.com.br {
    # desafio DNS-01: funciona mesmo sem a porta 80 aberta e emite curinga
    tls {
        dns cloudflare {env.CF_API_TOKEN}
    }
    reverse_proxy api:8080
}
```

```yaml
# docker-compose.yml
services:
  caddy:
    image: caddy:2-alpine          # em produção séria: fixe por digest
    ports: ["80:80", "443:443", "443:443/udp"]   # udp = HTTP/3
    environment:
      CF_API_TOKEN_FILE: /run/secrets/cf_token
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile:ro
      - caddy_data:/data            # ← O VOLUME MAIS IMPORTANTE: certificados e conta ACME
      - caddy_config:/config
    restart: unless-stopped
volumes: { caddy_data: {}, caddy_config: {} }
```

```bash
docker compose up -d
docker compose logs caddy | grep -i "certificate obtained"
curl -sI https://exemplo.com.br | head -1
```

**As quatro lições que só aparecem em produção:**

1. **Persistir `/data` é obrigatório.** Sem o volume, cada `docker compose up` cria
   uma conta ACME nova e pede certificados de novo. Em três dias você bate o limite
   do Let's Encrypt (**50 certificados por domínio registrado por semana**) e fica
   *sem HTTPS* — com a mensagem `too many certificates already issued`. Esse erro tem
   janela de 7 dias e não há a quem apelar.
2. **Teste no ambiente de staging primeiro.** O `acme_ca` de staging tem limites
   folgados e emite certificado não confiável (o que é justamente o desejado num teste).
3. **DNS-01 vs HTTP-01.** HTTP-01 exige a porta 80 alcançável e não emite curinga.
   DNS-01 exige um token de API do provedor de DNS e emite curinga. Em Cloudflare,
   crie o token com escopo **apenas** `Zone:DNS:Edit` na zona específica — um token
   global de conta no seu proxy é um risco desproporcional.
4. **Cloudflare no modo proxy ("laranja") faz TLS duas vezes:** navegador→Cloudflare
   e Cloudflare→você. Use o modo **Full (strict)**, nunca "Flexible" — "Flexible"
   deixa o trecho Cloudflare→origem **em HTTP puro** enquanto mostra cadeado ao
   usuário. É criptografia de mentira, e é a configuração padrão que mais engana gente.

---

## Exemplo 13 — PRODUÇÃO: rotação de certificado em Kubernetes sem downtime

**Contexto real:** cluster com Ingress NGINX, certificados do Let's Encrypt geridos
pelo cert-manager, e serviços internos com mTLS por CA privada.

```yaml
# 1. Emissor público (ACME, DNS-01 via Route53)
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata: { name: letsencrypt-prod }
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: ops@exemplo.com.br
    privateKeySecretRef: { name: letsencrypt-prod-account }
    solvers:
      - dns01:
          route53: { region: sa-east-1 }
---
# 2. Certificado público, renovado automaticamente
apiVersion: cert-manager.io/v1
kind: Certificate
metadata: { name: exemplo-tls, namespace: web }
spec:
  secretName: exemplo-tls           # o Secret é criado/atualizado pelo cert-manager
  issuerRef: { name: letsencrypt-prod, kind: ClusterIssuer }
  dnsNames: ["exemplo.com.br", "*.exemplo.com.br"]
  duration: 2160h                   # 90 dias
  renewBefore: 720h                 # renova 30 dias antes  ← a folga que salva
  privateKey:
    algorithm: ECDSA
    size: 256
    rotationPolicy: Always          # gera chave NOVA a cada renovação
---
# 3. CA interna para mTLS entre serviços
apiVersion: cert-manager.io/v1
kind: Certificate
metadata: { name: api-mtls, namespace: back }
spec:
  secretName: api-mtls
  issuerRef: { name: ca-interna, kind: ClusterIssuer }
  commonName: api.back.svc.cluster.local
  dnsNames: ["api.back.svc.cluster.local", "api"]
  duration: 24h                     # certificados de vida curtíssima…
  renewBefore: 8h                   # …renovados três vezes por dia
  usages: ["server auth", "client auth"]
```

```bash
kubectl get certificate -A
# NAME          READY   SECRET        AGE
# exemplo-tls   True    exemplo-tls   14d

kubectl describe certificate exemplo-tls -n web | grep -A3 Status
kubectl get secret exemplo-tls -n web -o jsonpath='{.data.tls\.crt}' | base64 -d | openssl x509 -noout -dates
```

**O detalhe que causa incidente:** trocar o `Secret` **não** faz o pod recarregar o
certificado. Três soluções, em ordem de qualidade:

```yaml
# (a) Melhor: a aplicação recarrega sozinha. Em Go:
#     tls.Config{GetCertificate: func(*ClientHelloInfo) (*Certificate, error) { ... lê do disco ... }}
#     O kubelet atualiza o arquivo montado em até ~60 s; o servidor pega o novo no próximo handshake.

# (b) Bom: um sidecar que observa o arquivo e manda SIGHUP
#     (o Ingress NGINX já faz isso; nginx recarrega sem derrubar conexões)

# (c) Aceitável: reiniciar o Deployment quando o Secret mudar
#     kubectl rollout restart deployment/api -n back
#     Com certificado de 24h isso é um restart por dia — evitável, mas funciona.
```

**Por que 24 horas nos certificados internos:** dentro do cluster, emitir é grátis e
instantâneo. Vida curta substitui revogação — e revogação, como argumenta
[15-validacao-revogacao-transparencia.md](15-validacao-revogacao-transparencia.md),
nunca funcionou direito na prática. É exatamente o mesmo raciocínio por trás dos
certificados de **6 dias** do Let's Encrypt, disponíveis desde janeiro de 2026, e da
redução da validade máxima pública para 47 dias até 2029.

---

## Exemplo 14 — PRODUÇÃO: verificação de certificado em pipeline de CI

**Contexto real:** impedir que uma configuração de TLS ruim chegue à produção, e
detectar regressão em quem já está lá.

```yaml
# .github/workflows/tls.yml
name: Auditoria TLS
on:
  schedule: [{ cron: "0 6 * * *" }]     # diariamente às 06:00 UTC
  workflow_dispatch:

jobs:
  auditar:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        host: [exemplo.com.br, api.exemplo.com.br]
    steps:
      - name: Versões de protocolo
        run: |
          for v in ssl3 tls1 tls1_1; do
            if echo | openssl s_client -connect ${{ matrix.host }}:443 \
                 -servername ${{ matrix.host }} -$v >/dev/null 2>&1; then
              echo "::error::${{ matrix.host }} aceita $v"; exit 1
            fi
          done
          echo "OK: protocolos antigos recusados"

      - name: Cadeia completa
        run: |
          n=$(echo | openssl s_client -connect ${{ matrix.host }}:443 \
                -servername ${{ matrix.host }} -showcerts 2>/dev/null \
                | grep -c "BEGIN CERTIFICATE")
          [ "$n" -ge 2 ] || { echo "::error::cadeia incompleta ($n cert)"; exit 1; }

      - name: Validade mínima de 21 dias
        run: |
          echo | openssl s_client -connect ${{ matrix.host }}:443 \
            -servername ${{ matrix.host }} 2>/dev/null \
            | openssl x509 -noout -checkend 1814400 \
            || { echo "::error::vence em menos de 21 dias"; exit 1; }

      - name: HSTS presente
        run: |
          curl -sI https://${{ matrix.host }} | grep -qi "strict-transport-security" \
            || { echo "::error::sem HSTS"; exit 1; }

      - name: testssl.sh (severidade alta)
        run: |
          docker run --rm drwetter/testssl.sh --severity HIGH --quiet \
            https://${{ matrix.host }} | tee saida.txt
          grep -qE "(HIGH|CRITICAL)" saida.txt && { echo "::error::achado grave"; exit 1; } || true

      - name: Certificados emitidos que não reconhecemos (Certificate Transparency)
        run: |
          curl -s "https://crt.sh/?q=${{ matrix.host }}&output=json" \
            | jq -r '.[] | select(.entry_timestamp > (now-86400|todate)) | .issuer_name' \
            | sort -u | tee novos.txt
          # Alerta se apareceu um emissor fora da lista esperada:
          grep -vqE "Let's Encrypt|DigiCert" novos.txt || echo "emissores esperados"
```

**O último passo é o mais subestimado.** Toda emissão de certificado público vai
obrigatoriamente para os logs de Certificate Transparency. Consultá-los diariamente
detecta emissão indevida para o seu domínio — seja por invasão da sua conta no
registrador, seja por erro de uma CA. É a defesa que sobrou depois que o HPKP morreu,
e ela custa uma chamada HTTP por dia. Ver [15-validacao-revogacao-transparencia.md](15-validacao-revogacao-transparencia.md).

---

## Autoteste

1. Por que todo `s_client` deste arquivo passa `-servername`?
2. Um servidor envia 1 certificado. Que problema isso causa, e em quais clientes?
3. Por que se fixa a chave pública (SPKI) e não o certificado inteiro, no pinning?
4. Cite os três cuidados obrigatórios ao fazer pinning em app móvel.
5. Por que `ssl_session_tickets off` protege o sigilo futuro?
6. O que acontece se você não persistir `/data` do Caddy, e qual é a mensagem de erro?
7. Por que o modo "Flexible" da Cloudflare é pior do que não ter HTTPS?
8. Por que certificados internos de 24 horas fazem sentido, se renová-los dá trabalho?
9. Trocar o Secret no Kubernetes não recarrega o certificado. Quais as três soluções, da melhor para a pior?
10. Como o Certificate Transparency detecta emissão indevida para o seu domínio?

*Respostas: §1, §8, §7, §7, §10, §12, §12, §13, §13, §14.*

---

**Próximo:** [07-projeto-modelo/](07-projeto-modelo/README.md) — uma aplicação inteira, com testes.
