# 17 · Configuração de servidores

**Nível:** intermediário → avançado · **Data:** 31/08/2026

Configuração real, completa e comentada, para nginx, Apache, Caddy, HAProxy, Node,
Python, Go e Java. Cada diretiva com a razão de existir — e o que quebra sem ela.

> **Antes de copiar qualquer coisa daqui:** gere a sua configuração em
> <https://ssl-config.mozilla.org/>, escolhendo a versão exata do seu servidor e do seu
> OpenSSL. É a fonte que os próprios projetos recomendam, e ela é atualizada quando as
> recomendações mudam. Este arquivo explica **por que** cada linha está lá — o gerador
> não explica.

---

## 1. Os três perfis da Mozilla

| Perfil | Suporta | Use quando |
|---|---|---|
| **Modern** | TLS 1.3 apenas | você controla os clientes (APIs internas, apps próprios) |
| **Intermediate** | TLS 1.2 + 1.3 | **padrão para a web pública** — cobre praticamente todo cliente em uso |
| **Old** | TLS 1.0+ | ❌ só com justificativa documentada e prazo para sair |

**Recomendação:** *Intermediate*, salvo se você souber exatamente por que quer outro.
*Modern* corta clientes reais (equipamentos embarcados, Java antigo, alguns aplicativos
de terceiros) e o ganho de segurança sobre *Intermediate* é pequeno.

---

## 2. nginx

Configuração completa e comentada. Testada no nginx 1.18+ (Ubuntu 22.04); onde uma
diretiva exige versão mais nova, está anotado.

```nginx
# ─── 1. HTTP: existe só para redirecionar e para o desafio ACME ──────────────
server {
    listen 80;
    listen [::]:80;
    server_name exemplo.com.br www.exemplo.com.br;

    # o desafio HTTP-01 do ACME precisa ser servido SEM redirecionar
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 301 https://$host$request_uri;
    }
}

# ─── 2. HTTPS ────────────────────────────────────────────────────────────────
server {
    listen 443 ssl;
    listen [::]:443 ssl;
    http2 on;                       # nginx ≥1.25.1. Antes: "listen 443 ssl http2;"
    # listen 443 quic reuseport;    # HTTP/3, nginx ≥1.25.0 compilado com quic
    server_name exemplo.com.br www.exemplo.com.br;

    # ── Certificado ──────────────────────────────────────────────────────────
    # FULLCHAIN, sempre. Usar cert.pem quebra clientes sem cache de intermediário.
    ssl_certificate         /etc/letsencrypt/live/exemplo.com.br/fullchain.pem;
    ssl_certificate_key     /etc/letsencrypt/live/exemplo.com.br/privkey.pem;
    # necessário para o stapling verificar a resposta OCSP:
    ssl_trusted_certificate /etc/letsencrypt/live/exemplo.com.br/chain.pem;

    # Dois certificados (ECDSA + RSA) para máxima compatibilidade sem perder
    # desempenho: clientes modernos pegam o ECDSA, antigos caem no RSA.
    # ssl_certificate     /etc/letsencrypt/live/exemplo.com.br-rsa/fullchain.pem;
    # ssl_certificate_key /etc/letsencrypt/live/exemplo.com.br-rsa/privkey.pem;

    # ── Protocolo e cifras ───────────────────────────────────────────────────
    ssl_protocols TLSv1.2 TLSv1.3;

    # Em TLS 1.3 quem escolhe é o cliente, e ele sabe melhor que você se tem
    # AES-NI. Forçar a ordem do servidor pode empurrar um celular para AES lento.
    ssl_prefer_server_ciphers off;

    # Lista Intermediate da Mozilla (só afeta TLS 1.2; o 1.3 tem suas 5 suites fixas)
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384;

    ssl_ecdh_curve X25519:prime256v1:secp384r1;

    # ── Sessões ──────────────────────────────────────────────────────────────
    ssl_session_cache   shared:MozSSL:10m;   # ~40.000 sessões por 10 MB
    ssl_session_timeout 1d;
    ssl_session_tickets off;                 # ver §2.1 — decisão importante

    # ── OCSP stapling ────────────────────────────────────────────────────────
    ssl_stapling on;
    ssl_stapling_verify on;
    resolver 1.1.1.1 8.8.8.8 valid=300s ipv6=off;   # SEM ISTO O STAPLING FALHA CALADO
    resolver_timeout 5s;

    # ── Cabeçalhos de segurança ──────────────────────────────────────────────
    add_header Strict-Transport-Security "max-age=63072000" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # ── Aplicação ────────────────────────────────────────────────────────────
    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;
        proxy_set_header Host              $host;
        proxy_set_header X-Real-IP         $remote_addr;
        proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;   # sem isto: conteúdo misto
        proxy_set_header Upgrade           $http_upgrade;
        proxy_set_header Connection        "upgrade";
    }
}
```

```bash
sudo nginx -t && sudo systemctl reload nginx
```

### 2.1 `ssl_session_tickets off` — a decisão explicada

Tickets de sessão cifram o estado da sessão com uma chave do servidor e o entregam ao
cliente. Vantagem: retomada sem estado, funciona em qualquer máquina do balanceador.

**O problema:** o nginx gera a chave de ticket ao **iniciar** e nunca a rotaciona.
Um servidor que roda há meses usa a mesma chave há meses. Se ela vazar (dump de
memória, invasão, backup), um atacante que gravou o tráfego decifra todas as sessões
retomadas — **anulando o sigilo futuro** que o ECDHE forneceu.

Duas saídas:

```nginx
ssl_session_tickets off;               # (a) simples: usa só o cache do servidor
```

```nginx
ssl_session_ticket_key /etc/nginx/ticket.1.key;   # (b) rotação explícita:
ssl_session_ticket_key /etc/nginx/ticket.2.key;   # a 1ª cifra, as demais só decifram
ssl_session_ticket_key /etc/nginx/ticket.3.key;
# um cron roda a cada 8h: gira os arquivos e faz reload
```

Use **(a)** salvo se você tiver vários nós atrás de um balanceador e a retomada
entre eles for medida como importante — e, nesse caso, implemente **(b)** de verdade.

### 2.2 mTLS no nginx

```nginx
    ssl_client_certificate /etc/nginx/pki/ca.crt;   # a CA que emite os clientes
    ssl_verify_client on;                            # OBRIGATÓRIO (não use "optional")
    ssl_verify_depth 2;
    ssl_crl /etc/nginx/pki/ca.crl;                   # revogação

    location /api/ {
        # repasse a identidade para a aplicação — ela faz a AUTORIZAÇÃO
        proxy_set_header X-Client-DN     $ssl_client_s_dn;
        proxy_set_header X-Client-Verify $ssl_client_verify;
        proxy_pass http://127.0.0.1:3000;
    }
```

> ⚠️ Se a aplicação confiar em `X-Client-DN`, o nginx **precisa** sobrescrever esse
> cabeçalho em toda requisição (o `proxy_set_header` acima faz isso). Caso contrário,
> um cliente pode enviá-lo sozinho e se declarar quem quiser. Este é um dos erros de
> mTLS mais comuns em produção.

---

## 3. Apache (httpd 2.4)

```apache
<VirtualHost *:80>
    ServerName exemplo.com.br
    Alias /.well-known/acme-challenge /var/www/certbot/.well-known/acme-challenge
    <Location "/.well-known/acme-challenge">
        Require all granted
    </Location>
    RedirectMatch 301 ^(?!/\.well-known/acme-challenge)(.*)$ https://exemplo.com.br$1
</VirtualHost>

<VirtualHost *:443>
    ServerName exemplo.com.br
    Protocols h2 http/1.1

    SSLEngine on
    SSLCertificateFile      /etc/letsencrypt/live/exemplo.com.br/fullchain.pem
    SSLCertificateKeyFile   /etc/letsencrypt/live/exemplo.com.br/privkey.pem

    SSLProtocol             -all +TLSv1.2 +TLSv1.3
    SSLHonorCipherOrder     off
    SSLCipherSuite          ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305
    SSLOpenSSLConfCmd       Curves X25519:prime256v1:secp384r1

    SSLUseStapling          on
    Header always set Strict-Transport-Security "max-age=63072000"

    # mTLS:
    # SSLCACertificateFile /etc/apache2/pki/ca.crt
    # SSLVerifyClient      require
    # SSLVerifyDepth       2
</VirtualHost>

# fora do VirtualHost — o cache de stapling é global:
SSLStaplingCache "shmcb:logs/ssl_stapling(32768)"
```

```bash
sudo apachectl configtest && sudo systemctl reload apache2
```

---

## 4. Caddy

```caddyfile
{
    email ops@exemplo.com.br
    servers {
        protocols h1 h2 h3
    }
}

exemplo.com.br {
    encode zstd gzip
    header {
        Strict-Transport-Security "max-age=63072000"
        X-Content-Type-Options    "nosniff"
        -Server
    }
    reverse_proxy localhost:3000
}

# mTLS
api.exemplo.com.br {
    tls {
        client_auth {
            mode                 require_and_verify
            trust_pool file /etc/caddy/pki/ca.crt
        }
    }
    reverse_proxy localhost:8080 {
        header_up X-Client-CN {http.request.tls.client.subject}
    }
}
```

O Caddy usa, por padrão: TLS 1.2+, só cifras AEAD, curvas modernas, OCSP stapling,
HSTS quando apropriado, e obtenção/renovação automática. **A configuração padrão dele
é melhor que a maioria das configurações escritas à mão.**

---

## 5. HAProxy

```haproxy
global
    ssl-default-bind-options ssl-min-ver TLSv1.2 no-tls-tickets
    ssl-default-bind-ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305
    ssl-default-bind-ciphersuites TLS_AES_128_GCM_SHA256:TLS_AES_256_GCM_SHA384:TLS_CHACHA20_POLY1305_SHA256
    tune.ssl.default-dh-param 2048

frontend web
    # o arquivo do bind precisa conter chave + fullchain CONCATENADOS
    bind :443 ssl crt /etc/haproxy/certs/exemplo.pem alpn h2,http/1.1
    bind :80
    http-request redirect scheme https unless { ssl_fc }
    http-response set-header Strict-Transport-Security "max-age=63072000"
    default_backend app

backend app
    server app1 127.0.0.1:3000 check
    # TLS até a origem, verificando de verdade:
    # server app1 10.0.0.5:8443 ssl verify required ca-file /etc/haproxy/pki/ca.crt check
```

```bash
haproxy -c -f /etc/haproxy/haproxy.cfg && systemctl reload haproxy
```

**Peculiaridade do HAProxy:** o arquivo do `crt` é **chave privada + certificado +
cadeia, concatenados no mesmo `.pem`**. Diferente de todo o resto. Monte com:

```bash
cat privkey.pem fullchain.pem > /etc/haproxy/certs/exemplo.pem
chmod 600 /etc/haproxy/certs/exemplo.pem
```

---

## 6. Aplicações

### Node.js

```javascript
const https = require('node:https');
const tls   = require('node:tls');
const fs    = require('node:fs');

const opcoes = {
  key:  fs.readFileSync('/etc/letsencrypt/live/ex/privkey.pem'),
  cert: fs.readFileSync('/etc/letsencrypt/live/ex/fullchain.pem'),
  minVersion: 'TLSv1.2',          // NUNCA confie no padrão em produção
  honorCipherOrder: false,        // o cliente escolhe (ver §2)
  ALPNProtocols: ['h2', 'http/1.1'],

  // mTLS:
  // ca: fs.readFileSync('/etc/pki/ca.crt'),
  // requestCert: true,
  // rejectUnauthorized: true,    // sem isto, requestCert é decorativo
};

const srv = https.createServer(opcoes, (req, res) => {
  res.writeHead(200, { 'Strict-Transport-Security': 'max-age=63072000' });
  res.end('ok\n');
});

// Recarga do certificado sem restart (importante com validade curta):
setInterval(() => {
  try {
    srv.setSecureContext({
      key:  fs.readFileSync('/etc/letsencrypt/live/ex/privkey.pem'),
      cert: fs.readFileSync('/etc/letsencrypt/live/ex/fullchain.pem'),
    });
  } catch (e) { console.error('recarga do certificado falhou', e); }
}, 6 * 60 * 60 * 1000);

srv.listen(8443);
```

> **`requestCert: true` sem `rejectUnauthorized: true` é uma armadilha clássica:**
> o servidor pede o certificado, aceita qualquer um (ou nenhum), e o desenvolvedor
> acredita ter mTLS. Os dois andam juntos.

### Python

```python
import ssl

ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ctx.minimum_version = ssl.TLSVersion.TLSv1_2
ctx.load_cert_chain("fullchain.pem", "privkey.pem")
ctx.set_alpn_protocols(["h2", "http/1.1"])
ctx.options |= ssl.OP_NO_COMPRESSION

# mTLS:
# ctx.verify_mode = ssl.CERT_REQUIRED
# ctx.load_verify_locations("ca.pem")
# ctx.verify_flags |= ssl.VERIFY_CRL_CHECK_LEAF
```

Exemplo completo e testado: [07-projeto-modelo/servidor.py](07-projeto-modelo/README.md).

### Go

```go
cfg := &tls.Config{
    MinVersion:       tls.VersionTLS12,
    CurvePreferences: []tls.CurveID{tls.X25519, tls.CurveP256},
    NextProtos:       []string{"h2", "http/1.1"},

    // recarga sem restart: o certificado é lido a cada handshake
    GetCertificate: func(*tls.ClientHelloInfo) (*tls.Certificate, error) {
        c, err := tls.LoadX509KeyPair("fullchain.pem", "privkey.pem")
        return &c, err
    },

    // mTLS:
    // ClientAuth: tls.RequireAndVerifyClientCert,
    // ClientCAs:  pool,
}
srv := &http.Server{Addr: ":8443", TLSConfig: cfg}
log.Fatal(srv.ListenAndServeTLS("", ""))
```

Em Go, `GetCertificate` é a forma idiomática de recarregar sem reiniciar — e com
certificados de 6 dias isso deixa de ser luxo. (Em produção, faça cache com
verificação de mtime; ler do disco em todo handshake é caro.)

### Java

```bash
# Java não lê PEM: converta para PKCS#12
openssl pkcs12 -export -out servidor.p12 -inkey privkey.pem -in fullchain.pem \
  -name servidor -passout pass:SENHA
```

```properties
# application.properties (Spring Boot)
server.port=8443
server.ssl.key-store=/etc/pki/servidor.p12
server.ssl.key-store-type=PKCS12
server.ssl.key-store-password=SENHA
server.ssl.enabled-protocols=TLSv1.3,TLSv1.2
# mTLS:
# server.ssl.client-auth=need
# server.ssl.trust-store=/etc/pki/truststore.p12
```

**A pegadinha do Java:** ele tem repositório de confiança **próprio** (`cacerts`),
independente do sistema. Uma CA interna instalada no Linux **não** é vista pelo Java:

```bash
keytool -importcert -alias minha-ca -file ca.crt \
  -keystore "$JAVA_HOME/lib/security/cacerts" -storepass changeit -noprompt
```

---

## 7. Terminação: onde o TLS termina, e o que isso implica

```
(a) TLS até o servidor de aplicação
    cliente ══TLS══════════════════════════► app
    ✅ ninguém no meio lê   ❌ a app gasta CPU; certificado em cada instância

(b) Terminação no proxy (o mais comum)
    cliente ══TLS══► nginx ──HTTP em claro──► app
    ✅ simples, certificado num lugar só   ❌ o trecho interno é legível
       — aceitável apenas se esse trecho for a mesma máquina ou uma rede confiável

(c) Reencriptação (TLS de ponta a ponta com terminação intermediária)
    cliente ══TLS══► nginx ══TLS══► app
    ✅ nada em claro   ❌ mais CPU, mais certificados; é o modelo de zero trust

(d) Passthrough (o proxy não decifra)
    cliente ══════════TLS═══════════► app   (o proxy só encaminha bytes por SNI)
    ✅ o proxy nunca vê nada   ❌ o proxy não pode rotear por URL, nem inspecionar
```

**Recomendação:** (b) quando proxy e aplicação estão na mesma máquina ou no mesmo pod;
(c) quando atravessam a rede — inclusive dentro do seu data center. "Rede interna é
confiável" é um pressuposto que envelheceu mal.

---

## 8. Verificar o que você configurou

```bash
nginx -t                                         # sintaxe
curl -sI https://exemplo.com.br | head -1        # o cliente enxerga?
curl -sI http://exemplo.com.br | grep -i location # redireciona?
echo | openssl s_client -connect exemplo.com.br:443 -servername exemplo.com.br -brief
echo | openssl s_client -connect exemplo.com.br:443 -servername exemplo.com.br -status 2>&1 | grep -A2 "OCSP Response"
curl -sI https://exemplo.com.br | grep -i strict-transport   # HSTS presente?
curl -s --http2 -o /dev/null -w "%{http_version}\n" https://exemplo.com.br  # HTTP/2?
testssl.sh --severity HIGH https://exemplo.com.br
```

E a auditoria externa: <https://www.ssllabs.com/ssltest/>.

---

## 9. HSTS — com o aviso que precisa vir junto

```nginx
add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
```

HSTS diz ao navegador: "pelos próximos N segundos, **nunca** fale comigo por HTTP, e
**não deixe o usuário ignorar** aviso de certificado". Fecha o ataque de *SSL stripping*
(rebaixar a primeira conexão, em HTTP, antes do redirecionamento).

> ### O caminho sem volta
> - `includeSubDomains` aplica a regra a **todos** os subdomínios. Se algum deles
>   ainda roda em HTTP (um sistema legado, um painel interno), ele **fica inacessível**
>   — e você não tem como cancelar nos navegadores que já receberam o cabeçalho, a não
>   ser esperando o `max-age` expirar.
> - `preload` submete seu domínio a uma **lista embutida no código dos navegadores**.
>   Sair dela leva **meses** e depende de novas versões chegarem aos usuários.
>
> **Roteiro seguro:** comece com `max-age=300` (5 min), sem `includeSubDomains`. Confirme
> que **tudo** funciona por HTTPS, inclusive subdomínios. Suba para `max-age=86400`,
> depois para 2 anos. Só então considere `includeSubDomains`, e só depois disso `preload`.
> Ir direto para `max-age=63072000; includeSubDomains; preload` é a receita para dois anos
> de dor de cabeça a partir de um subdomínio esquecido.

---

## 10. Checklist de produção

```
[ ] fullchain.pem (não cert.pem)
[ ] TLS 1.2 + 1.3, nada abaixo
[ ] ssl_prefer_server_ciphers off
[ ] renovação automática funcionando (certbot renew --dry-run)
[ ] gancho de recarga após renovar, testado
[ ] monitoramento externo de validade, com alerta
[ ] HTTP → HTTPS com 301 (exceto /.well-known/acme-challenge/)
[ ] HSTS, começando com max-age curto
[ ] OCSP stapling ligado E VERIFICADO (com resolver configurado)
[ ] chave privada com modo 600, dono correto, fora do Git
[ ] X-Forwarded-Proto repassado à aplicação
[ ] em mTLS: verify_client on (não optional) e cabeçalhos de identidade sobrescritos
[ ] registro CAA publicado
[ ] monitoramento de Certificate Transparency ativo
[ ] nginx -t / apachectl configtest no pipeline de CI
```

---

## Autoteste

1. Qual perfil da Mozilla usar por padrão, e por que não o *Modern*?
2. Por que `ssl_prefer_server_ciphers off` em TLS 1.3?
3. Explique por que `ssl_session_tickets off` protege o sigilo futuro, e a alternativa.
4. O que acontece se você configurar `ssl_stapling on` sem `resolver`?
5. Por que `X-Forwarded-Proto` é obrigatório atrás de proxy?
6. Em mTLS por proxy, por que os cabeçalhos de identidade precisam ser sobrescritos?
7. Qual é a diferença entre `requestCert` e `rejectUnauthorized` no Node?
8. Descreva os quatro modelos de terminação e quando usar cada um.
9. Quais são os dois riscos irreversíveis do HSTS, e qual é o roteiro seguro?
10. Por que uma CA instalada no Linux não é vista pelo Java?
11. Como o HAProxy espera o arquivo de certificado, e por que isso surpreende?

*Respostas: §1, §2, §2.1, §2 (falha calada), §2, §2.2, §6, §7, §9, §6, §5.*

---

**Próximo:** [18-mtls-e-pki-interna.md](18-mtls-e-pki-interna.md) — autenticação mútua em escala.
