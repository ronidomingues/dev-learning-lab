# 05 · Manual de uso — referência por tarefa

**Nível:** intermediário · **Data:** 31/08/2026
**Como usar este arquivo:** não leia do começo ao fim. Use o índice, ache a tarefa,
copie o comando. É a página que você vai deixar aberta numa aba por anos.

Verificado com OpenSSL 3.0.2 e curl 7.81.0. Onde a sintaxe muda em outra versão, está anotado.

---

## Índice por tarefa

**Inspecionar** — [1.1 certificado](#11-inspecionar-um-certificado) · [1.2 servidor remoto](#12-inspecionar-um-servidor-remoto) · [1.3 chave](#13-inspecionar-uma-chave) · [1.4 cadeia](#14-inspecionar-a-cadeia)
**Criar** — [2.1 chave](#21-gerar-uma-chave-privada) · [2.2 CSR](#22-gerar-um-csr) · [2.3 autoassinado](#23-certificado-autoassinado) · [2.4 CA própria](#24-ser-uma-ca)
**Converter** — [3 formatos](#3-converter-formatos)
**Testar** — [4.1 conexão](#41-testar-uma-conexão) · [4.2 versões e cifras](#42-descobrir-versões-e-cifras-aceitas) · [4.3 auditar](#43-auditoria-completa)
**Configurar** — [5 servidores](#5-configuração-mínima-por-servidor)
**Depurar** — [6 diagnóstico](#6-diagnóstico)
**Obsoleto** — [7 o que não usar mais](#7-obsoleto--o-que-não-usar-mais)
**Atalhos** — [8 truques de quem usa há anos](#8-atalhos-que-só-quem-usa-há-anos-conhece)

---

## 1. Inspecionar

### 1.1 Inspecionar um certificado

| Objetivo | Comando |
|---|---|
| tudo, legível | `openssl x509 -in cert.pem -noout -text` |
| só o essencial | `openssl x509 -in cert.pem -noout -subject -issuer -dates` |
| validade | `openssl x509 -in cert.pem -noout -dates` |
| nomes cobertos (**o que importa**) | `openssl x509 -in cert.pem -noout -ext subjectAltName` |
| número de série | `openssl x509 -in cert.pem -noout -serial` |
| impressão digital SHA-256 | `openssl x509 -in cert.pem -noout -fingerprint -sha256` |
| algoritmo da chave e tamanho | `openssl x509 -in cert.pem -noout -text \| grep -A2 "Public Key Algorithm"` |
| para que serve (extensões de uso) | `openssl x509 -in cert.pem -noout -ext keyUsage,extendedKeyUsage,basicConstraints` |
| vence em menos de 30 dias? | `openssl x509 -in cert.pem -noout -checkend 2592000; echo $?`  → `0` = ainda vale, `1` = vence |

```bash
# Vence em quantos dias? (útil em monitoramento)
exp=$(openssl x509 -in cert.pem -noout -enddate | cut -d= -f2)
echo $(( ( $(date -d "$exp" +%s) - $(date +%s) ) / 86400 )) dias
```

### 1.2 Inspecionar um servidor remoto

```bash
# resumo do que foi negociado
echo | openssl s_client -connect HOST:443 -servername HOST -brief

# o certificado que o servidor apresenta, em PEM
echo | openssl s_client -connect HOST:443 -servername HOST 2>/dev/null \
  | openssl x509 -out servidor.pem

# datas de validade, sem baixar nada
echo | openssl s_client -connect HOST:443 -servername HOST 2>/dev/null \
  | openssl x509 -noout -dates -subject -issuer

# a cadeia inteira que o servidor envia
echo | openssl s_client -connect HOST:443 -servername HOST -showcerts 2>/dev/null \
  | grep -E "^ *(s|i):"
```

Portas que não são 443 (e o `-starttls` que muita gente não conhece):

```bash
openssl s_client -connect smtp.exemplo.com:587 -starttls smtp     # SMTP submissão
openssl s_client -connect imap.exemplo.com:143  -starttls imap
openssl s_client -connect pop.exemplo.com:110   -starttls pop3
openssl s_client -connect db.exemplo.com:5432   -starttls postgres
openssl s_client -connect mysql.exemplo.com:3306 -starttls mysql
openssl s_client -connect ldap.exemplo.com:389  -starttls ldap
```

### 1.3 Inspecionar uma chave

```bash
openssl pkey -in chave.pem -noout -text          # funciona para RSA, EC, Ed25519
openssl pkey -in chave.pem -pubout               # extrai a chave pública
openssl pkey -in chave.pem -noout -text | head -1  # que tipo é
```

Conferir se a chave é a do certificado (o teste que resolve `key values mismatch`):

```bash
openssl x509 -noout -pubkey -in cert.pem | openssl sha256
openssl pkey  -pubout    -in chave.pem   | openssl sha256
# hashes idênticos = par correto
```

### 1.4 Inspecionar a cadeia

```bash
# validar uma cadeia local contra as raízes do sistema
openssl verify -untrusted intermediarios.pem cert.pem
# esperado: cert.pem: OK

# validar contra uma CA específica
openssl verify -CAfile ca.pem cert.pem

# quantos certificados um arquivo contém
grep -c "BEGIN CERTIFICATE" fullchain.pem
```

---

## 2. Criar

### 2.1 Gerar uma chave privada

| Tipo | Comando | Quando usar |
|---|---|---|
| **EC P-256** (padrão de hoje) | `openssl genpkey -algorithm EC -pkeyopt ec_paramgen_curve:P-256 -out chave.pem` | ✅ escolha padrão: rápida, pequena, aceita em todo lugar |
| EC P-384 | `openssl genpkey -algorithm EC -pkeyopt ec_paramgen_curve:P-384 -out chave.pem` | exigência regulatória de "192 bits de segurança" |
| RSA 2048 | `openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:2048 -out chave.pem` | compatibilidade com clientes velhos |
| RSA 4096 | `openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:4096 -out chave.pem` | raízes de CA de longa duração; **não** para servidor web (lento, sem ganho prático) |
| Ed25519 | `openssl genpkey -algorithm ED25519 -out chave.pem` | ótimo, mas **CAs públicas ainda não emitem**; use em PKI interna e SSH |
| com senha | `openssl genpkey -algorithm EC -pkeyopt ec_paramgen_curve:P-256 -aes-256-cbc -out chave.pem` | chave que ficará em disco compartilhado — mas então alguém tem de digitar a senha no boot |

### 2.2 Gerar um CSR

O **CSR** (*Certificate Signing Request*, pedido de assinatura de certificado) é o
que você manda para a CA: sua chave pública + os nomes que quer + uma prova de que
você tem a chave privada. **A chave privada nunca sai da sua máquina.**

```bash
openssl req -new -key chave.pem -out pedido.csr \
  -subj "/C=BR/ST=Sao Paulo/L=Sao Paulo/O=Minha Empresa/CN=exemplo.com.br" \
  -addext "subjectAltName=DNS:exemplo.com.br,DNS:www.exemplo.com.br"
```

```bash
openssl req -in pedido.csr -noout -text -verify   # confira ANTES de enviar
# esperado: "Certificate request self-signature verify OK" e o SAN correto
```

Gerar chave e CSR de uma vez:

```bash
openssl req -new -newkey ec -pkeyopt ec_paramgen_curve:P-256 -nodes \
  -keyout chave.pem -out pedido.csr \
  -subj "/CN=exemplo.com.br" -addext "subjectAltName=DNS:exemplo.com.br"
```
`-nodes` = *no DES*, ou seja, **não** proteja a chave com senha. Necessário para
servidor que inicia sozinho.

### 2.3 Certificado autoassinado

```bash
openssl req -x509 -new -key chave.pem -days 365 -out cert.pem \
  -subj "/CN=localhost" -addext "subjectAltName=DNS:localhost,IP:127.0.0.1"
```

Tudo de uma vez (chave + certificado):

```bash
openssl req -x509 -newkey rsa:2048 -nodes -days 365 \
  -keyout chave.pem -out cert.pem \
  -subj "/CN=localhost" -addext "subjectAltName=DNS:localhost"
```

### 2.4 Ser uma CA

```bash
# 1. chave e certificado da raiz
openssl genpkey -algorithm EC -pkeyopt ec_paramgen_curve:P-384 -out ca-chave.pem
openssl req -x509 -new -key ca-chave.pem -days 3650 -out ca-cert.pem \
  -subj "/CN=Minha CA Interna" \
  -addext "basicConstraints=critical,CA:TRUE,pathlen:0" \
  -addext "keyUsage=critical,keyCertSign,cRLSign"
```
`basicConstraints=CA:TRUE` é o que torna um certificado uma CA. `pathlen:0` impede
que ela emita outras CAs. Ambos `critical` — um cliente que não entenda a extensão
deve **recusar**, não ignorar.

```bash
# 2. assinar um CSR
openssl x509 -req -in pedido.csr -CA ca-cert.pem -CAkey ca-chave.pem \
  -CAcreateserial -days 90 -out cert.pem \
  -copy_extensions copyext \
  -extfile <(printf "subjectAltName=DNS:servico.interno\nkeyUsage=critical,digitalSignature\nextendedKeyUsage=serverAuth\nbasicConstraints=critical,CA:FALSE")
```

> ⚠️ **`-copy_extensions copyext` é perigoso se o CSR vier de terceiros**: quem
> mandou o CSR pode ter pedido `basicConstraints=CA:TRUE` e você acabou de emitir
> uma CA para ele. Em CA de verdade, **nunca copie extensões do CSR** — defina-as
> no `-extfile`, sempre. É por isso que o OpenSSL não copia por padrão.

O projeto completo de uma CA interna funcional está em
[07-projeto-modelo/](07-projeto-modelo/README.md) e a teoria em
[18-mtls-e-pki-interna.md](18-mtls-e-pki-interna.md).

---

## 3. Converter formatos

Você vai confundir esses formatos. Todo mundo confunde. Esta é a tabela de tradução.

| Formato | Extensão típica | O que é | Quem usa |
|---|---|---|---|
| **PEM** | `.pem` `.crt` `.cer` `.key` | Base64 entre `-----BEGIN X-----` e `-----END X-----` | Unix, nginx, Apache, OpenSSL — **o padrão de facto** |
| **DER** | `.der` `.cer` | os mesmos bytes, em binário puro | Java antigo, Windows, dispositivos embarcados |
| **PKCS#12 / PFX** | `.p12` `.pfx` | um "cofre" com chave + certificado + cadeia, protegido por senha | Windows, IIS, importação em navegador, importação de chave em Java |
| **PKCS#7 / P7B** | `.p7b` `.p7c` | só certificados (sem chave) | Windows, distribuição de cadeia |
| **JKS** | `.jks` | *Java KeyStore*, formato proprietário legado | Java antigo (`keytool`) — **obsoleto**, use PKCS#12 |
| **PKCS#8** | `.key` `.pem` | formato moderno de chave privada (`BEGIN PRIVATE KEY`) | tudo que é atual |
| **PKCS#1** | `.key` | formato antigo, só RSA (`BEGIN RSA PRIVATE KEY`) | legado |

```bash
# PEM → DER
openssl x509 -in cert.pem -outform der -out cert.der
# DER → PEM
openssl x509 -inform der -in cert.der -out cert.pem

# PEM (chave + cert + cadeia) → PKCS#12
openssl pkcs12 -export -out pacote.p12 -inkey chave.pem -in cert.pem -certfile cadeia.pem
# PKCS#12 → PEM (tudo)
openssl pkcs12 -in pacote.p12 -out tudo.pem -nodes
# PKCS#12 → só a chave / só os certificados
openssl pkcs12 -in pacote.p12 -nocerts -nodes -out chave.pem
openssl pkcs12 -in pacote.p12 -nokeys  -out certs.pem

# PKCS#7 → PEM
openssl pkcs7 -print_certs -in cadeia.p7b -out cadeia.pem

# PKCS#1 (BEGIN RSA PRIVATE KEY) → PKCS#8 (BEGIN PRIVATE KEY)
openssl pkey -in antiga.key -out nova.pem

# JKS → PKCS#12 (o caminho para sair do formato Java legado)
keytool -importkeystore -srckeystore loja.jks -destkeystore loja.p12 -deststoretype PKCS12
```

**Como identificar um arquivo desconhecido:**

```bash
head -1 arquivo
# -----BEGIN CERTIFICATE-----       → certificado PEM
# -----BEGIN PRIVATE KEY-----       → chave PKCS#8
# -----BEGIN RSA PRIVATE KEY-----   → chave PKCS#1 (RSA)
# -----BEGIN EC PRIVATE KEY-----    → chave EC (SEC1)
# -----BEGIN CERTIFICATE REQUEST--- → CSR
# -----BEGIN ENCRYPTED PRIVATE KEY- → chave com senha
# lixo binário                      → DER, PKCS#12 ou PKCS#7: use `file arquivo`
```

---

## 4. Testar

### 4.1 Testar uma conexão

```bash
curl -v https://HOST 2>&1 | grep -E "SSL|TLS|subject|issuer|ALPN"
curl -sI https://HOST                       # só os cabeçalhos
curl --tlsv1.3 --tls-max 1.3 -sI https://HOST   # forçar TLS 1.3
curl --tlsv1.2 --tls-max 1.2 -sI https://HOST   # forçar TLS 1.2
curl --resolve HOST:443:1.2.3.4 -sI https://HOST  # testar um IP específico sem mexer no /etc/hosts
curl --cert cli.pem --key cli-key.pem https://HOST   # mTLS
```

### 4.2 Descobrir versões e cifras aceitas

```bash
for v in ssl3 tls1 tls1_1 tls1_2 tls1_3; do
  printf "%-8s " "$v"
  echo | openssl s_client -connect HOST:443 -servername HOST -"$v" >/dev/null 2>&1 \
    && echo "ACEITA" || echo "recusa"
done
```

Saída desejável em 2026: `ssl3 recusa · tls1 recusa · tls1_1 recusa · tls1_2 ACEITA · tls1_3 ACEITA`.

```bash
nmap --script ssl-enum-ciphers -p 443 HOST     # lista tudo, com nota A–F por cifra
openssl ciphers -v 'HIGH:!aNULL'               # o que o SEU OpenSSL suporta
openssl ciphers -v -s -tls1_3                  # só as suites do TLS 1.3 (são 5)
```

### 4.3 Auditoria completa

```bash
testssl.sh https://HOST                  # relatório completo, ~3 min
testssl.sh --severity HIGH https://HOST  # só o que é grave
testssl.sh --jsonfile r.json https://HOST  # para automação/CI
```

Online, quando você não pode instalar nada: <https://www.ssllabs.com/ssltest/>.
Ele dá uma nota de A+ a F. **Perseguir A+ cegamente é armadilha** — veja
[75-armadilhas.md](75-armadilhas.md).

---

## 5. Configuração mínima por servidor

Configurações completas e comentadas estão em
[17-configuracao-de-servidores.md](17-configuracao-de-servidores.md). Aqui é o mínimo utilizável.

**nginx**

```nginx
server {
    listen 443 ssl;
    http2 on;                                  # nginx 1.25.1+; antes era "listen 443 ssl http2"
    server_name exemplo.com.br;

    ssl_certificate     /etc/letsencrypt/live/exemplo.com.br/fullchain.pem;  # FULLCHAIN, não cert.pem
    ssl_certificate_key /etc/letsencrypt/live/exemplo.com.br/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers off;             # em TLS 1.3 a preferência do cliente é melhor
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_session_cache shared:SSL:10m;
    ssl_session_tickets off;                   # tickets sem rotação quebram o sigilo futuro
    ssl_stapling on;
    ssl_stapling_verify on;

    add_header Strict-Transport-Security "max-age=63072000" always;
}
```

**Caddy** (o arquivo inteiro; ele obtém e renova o certificado sozinho)

```caddyfile
exemplo.com.br {
    reverse_proxy localhost:3000
}
```

**Apache**

```apache
<VirtualHost *:443>
    ServerName exemplo.com.br
    SSLEngine on
    SSLCertificateFile      /etc/letsencrypt/live/exemplo.com.br/fullchain.pem
    SSLCertificateKeyFile   /etc/letsencrypt/live/exemplo.com.br/privkey.pem
    SSLProtocol             -all +TLSv1.2 +TLSv1.3
    SSLHonorCipherOrder     off
    SSLUseStapling          on
</VirtualHost>
```

**Node.js**

```javascript
const https = require('node:https');
const fs = require('node:fs');
https.createServer({
  key:  fs.readFileSync('privkey.pem'),
  cert: fs.readFileSync('fullchain.pem'),
  minVersion: 'TLSv1.2',                 // NUNCA deixe no padrão em produção
}, (req, res) => res.end('ok\n')).listen(8443);
```

**Python**

```python
import ssl
ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ctx.minimum_version = ssl.TLSVersion.TLSv1_2
ctx.load_cert_chain("fullchain.pem", "privkey.pem")
```

**Go**

```go
srv := &http.Server{
    Addr: ":8443",
    TLSConfig: &tls.Config{MinVersion: tls.VersionTLS12},
}
srv.ListenAndServeTLS("fullchain.pem", "privkey.pem")
```

**Sempre gere a configuração pelo gerador da Mozilla** em vez de copiar de blog:
<https://ssl-config.mozilla.org/> — escolha o perfil **Intermediate** salvo se você
souber exatamente por que quer outro.

---

## 6. Diagnóstico

| Sintoma | Comando que responde |
|---|---|
| "não sei o que está sendo negociado" | `openssl s_client -connect H:443 -servername H -brief </dev/null` |
| "a cadeia está completa?" | `... -showcerts 2>/dev/null \| grep -c "BEGIN CERT"` |
| "que nomes esse certificado cobre?" | `openssl x509 -noout -ext subjectAltName -in c.pem` |
| "a chave bate com o certificado?" | §1.3 |
| "que versões o servidor aceita?" | §4.2 |
| "quando vence?" | `openssl x509 -noout -checkend 604800 -in c.pem` (1 semana) |
| "está revogado?" | `openssl ocsp` (§abaixo) ou consultar a CRL |
| "que certificados já emitiram para o meu domínio?" | <https://crt.sh/?q=exemplo.com.br> |
| "quero ver os bytes no fio" | `tshark -i any -f "port 443" -Y tls.handshake` |
| "quero decifrar o tráfego no Wireshark" | `export SSLKEYLOGFILE=/tmp/keys.log` antes de abrir o navegador/curl; aponte o Wireshark para esse arquivo |

Checar revogação por OCSP:

```bash
url=$(openssl x509 -in cert.pem -noout -ocsp_uri)
openssl ocsp -issuer cadeia.pem -cert cert.pem -url "$url" -no_nonce -text 2>&1 | grep -E "Cert Status|This Update"
# esperado: Cert Status: good
```

---

## 7. Obsoleto — o que não usar mais

| Não use | Por quê | Use no lugar |
|---|---|---|
| `openssl genrsa` | interface antiga, sem opções de provider | `openssl genpkey -algorithm RSA` |
| `openssl dsaparam`/DSA | tamanho de chave preso, dependente de aleatoriedade perfeita | ECDSA ou Ed25519 |
| `openssl dhparam` (grupos DH personalizados) | TLS 1.3 usa grupos nomeados; DH personalizado causou o Logjam | nada — deixe TLS 1.3 escolher |
| SSLv2, SSLv3, TLS 1.0, TLS 1.1 | quebrados (DROWN, POODLE, BEAST) e proibidos pela indústria desde 2020 | TLS 1.2 e 1.3 |
| RC4 | viés estatístico explorável | AES-GCM ou ChaCha20-Poly1305 |
| 3DES | bloco de 64 bits → ataque Sweet32 | AES |
| CBC com MAC-then-Encrypt | família Lucky13/BEAST/POODLE | AEAD (GCM, ChaCha20-Poly1305) |
| Cifras `EXPORT` | 40 bits por decreto do governo dos EUA nos anos 1990 → FREAK/Logjam | qualquer coisa moderna |
| Compressão TLS | ataque CRIME | desligada por padrão desde sempre |
| Renegociação insegura | CVE-2009-3555 | renegociação segura (RFC 5746) ou nada |
| `HPKP` (*Public Key Pinning* por cabeçalho) | tiro no pé garantido; removido dos navegadores em 2018 | Certificate Transparency + monitoramento |
| Certificado de validação estendida (**EV**) como diferencial visual | os navegadores removeram a barra verde em 2019 — não muda nada para o usuário | DV normal, e gaste o dinheiro em outra coisa |
| `keytool` com JKS | formato proprietário obsoleto | PKCS#12 |
| SHA-1 em certificado | colisão prática demonstrada (SHAttered, 2017) | SHA-256 |
| Chave RSA de 1024 bits | fatorável hoje por um Estado | 2048 mínimo, ou EC P-256 |

---

## 8. Atalhos que só quem usa há anos conhece

```bash
# 1. Ver o certificado de um site sem baixar arquivo nenhum, em uma linha
openssl s_client -connect exemplo.com:443 -servername exemplo.com </dev/null 2>/dev/null | openssl x509 -noout -text | less

# 2. Testar se a renovação vai funcionar ANTES de a hora chegar
certbot renew --dry-run

# 3. Monitorar validade de vários hosts (bom para cron)
for h in a.com b.com c.com; do
  d=$(echo | openssl s_client -connect "$h:443" -servername "$h" 2>/dev/null | openssl x509 -noout -enddate | cut -d= -f2)
  printf "%-20s %s\n" "$h" "$d"
done

# 4. Confirmar qual certificado o servidor manda para um SNI específico
#    (essencial quando um IP hospeda 50 sites)
openssl s_client -connect 1.2.3.4:443 -servername especifico.com </dev/null 2>/dev/null | openssl x509 -noout -subject

# 5. Gerar 20 certificados de teste sem digitar 20 vezes
for n in a b c; do
  openssl req -x509 -newkey ec -pkeyopt ec_paramgen_curve:P-256 -nodes -days 30 \
    -keyout "$n.key" -out "$n.crt" -subj "/CN=$n.local" -addext "subjectAltName=DNS:$n.local"
done

# 6. Ver o handshake byte a byte, sem Wireshark
openssl s_client -connect exemplo.com:443 -servername exemplo.com -trace </dev/null 2>&1 | head -80

# 7. Descobrir se o servidor exige certificado de cliente (mTLS)
echo | openssl s_client -connect HOST:443 -servername HOST 2>&1 | grep -A5 "Acceptable client certificate CA names"

# 8. Verificar a cadeia como o navegador faria, sem confiar no que o servidor mandou
openssl s_client -connect HOST:443 -servername HOST -verify_return_error -verify_hostname HOST </dev/null

# 9. Extrair só o intermediário de um fullchain
awk '/BEGIN/{n++} n==2' fullchain.pem > intermediario.pem

# 10. Achar todas as chaves privadas expostas numa árvore de diretórios
grep -rl "BEGIN.*PRIVATE KEY" . 2>/dev/null

# 11. Comparar dois certificados rapidamente
diff <(openssl x509 -in a.pem -noout -text) <(openssl x509 -in b.pem -noout -text)

# 12. Descobrir o que o cliente ANUNCIA (útil para depurar cliente antigo)
#     suba um servidor de eco de handshake:
openssl s_server -accept 8443 -cert cert.pem -key chave.pem -msg -state
```

**Variáveis de ambiente úteis no dia a dia:**

```bash
export SSLKEYLOGFILE=/tmp/keys.log   # só em laboratório: permite decifrar no Wireshark
export SSL_CERT_FILE=/caminho/ca.pem # troca as âncoras de confiança para este processo
```

---

## Autoteste

1. Qual comando mostra os nomes que um certificado cobre — e por que não basta olhar o CN?
2. Como provar, em dois comandos, que uma chave é a do certificado?
3. Qual a diferença entre PEM, DER e PKCS#12, e quando cada um aparece?
4. Por que `-copy_extensions copyext` é perigoso ao assinar CSR de terceiros?
5. Qual comando verifica se um certificado vence nos próximos 7 dias, com código de saída utilizável em script?
6. Cite cinco coisas da tabela de obsoletos e o motivo de cada uma.
7. Como testar TLS num servidor SMTP na porta 587?
8. Por que `ssl_prefer_server_ciphers off` é a recomendação em TLS 1.3?
9. Como descobrir se um servidor exige certificado de cliente?

*Respostas: §1.1 e §04 Passo 2, §1.3, §3, §2.4, §6, §7, §1.2, §5/[17](17-configuracao-de-servidores.md), §8.7.*

---

**Próximo:** [06-exemplos.md](06-exemplos.md) — 14 receitas completas.
