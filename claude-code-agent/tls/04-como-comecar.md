# 04 · Como começar — do ambiente pronto ao primeiro HTTPS

**Nível:** iniciante · **Data:** 31/08/2026
**Pré-requisito:** o checklist do [03-instalacao.md](03-instalacao.md#15-checklist-ambiente-pronto) passou.
Este arquivo **não repete a instalação** — se algo faltar, volte ao [03](03-instalacao.md).

**Sobre as saídas mostradas.** Tudo que envolve `localhost` foi **executado de
verdade** nesta máquina (Ubuntu 22.04.5, OpenSSL 3.0.2, Python 3.10.12, curl 7.81.0)
em 31/08/2026, e o texto está marcado com *saída real*. As saídas contra sites
públicos estão marcadas como *saída típica*: a máquina em que este material foi
escrito só alcança a internet por um proxy corporativo, que impede a conexão TLS
direta necessária para capturá-las. O **formato** é o real do OpenSSL 3.0.2; os
**valores** variam por site e por dia. Rode você mesmo — é o objetivo do arquivo.

---

## Em 10 minutos você vai ter

1. Espiado um handshake TLS real, de um site real.
2. Gerado uma chave privada e um certificado.
3. Subido um servidor HTTPS na sua máquina.
4. Visto o cliente **recusar** o certificado — e entendido por quê.
5. Visto o cliente **aceitar** — e entendido o que mudou.

---

## Passo 0 · Olhar antes de construir

```bash
echo | openssl s_client -connect example.com:443 -servername example.com -brief
```

`s_client` abre uma conexão TLS e conta tudo que aconteceu. O `echo |` fecha a
entrada logo em seguida, senão ele fica esperando você digitar HTTP à mão.
`-servername` envia o **SNI** (*Server Name Indication*), o campo que diz ao servidor
qual site você quer — sem ele, servidores que hospedam vários domínios no mesmo IP
não sabem qual certificado apresentar.

Saída típica (formato real; valores variam):

```
CONNECTION ESTABLISHED
Protocol version: TLSv1.3
Ciphersuite: TLS_AES_256_GCM_SHA384
Peer certificate: CN = *.example.com
Hash used: SHA256
Signature type: ECDSA
Verification: OK
Server Temp Key: X25519, 253 bits
```

Leia linha por linha — cada uma é um conceito do curso:

| Linha | O que significa | Aprofunda em |
|---|---|---|
| `Protocol version: TLSv1.3` | a versão negociada. Se aparecer 1.2, tudo bem; se aparecer 1.0/1.1, o servidor está desatualizado | [11](11-historia.md) |
| `Ciphersuite: TLS_AES_256_GCM_SHA384` | a cifra escolhida: AES de 256 bits em modo GCM, com SHA-384 na derivação de chaves | [14](14-criptografia-do-tls.md) |
| `Peer certificate: CN = *.example.com` | o nome no certificado que o servidor apresentou | [13](13-certificados-e-pki.md) |
| `Signature type: ECDSA` | o certificado é de curva elíptica, não RSA | [14](14-criptografia-do-tls.md) |
| `Verification: OK` | **a linha mais importante**: a cadeia foi validada até uma raiz que você confia | [13](13-certificados-e-pki.md) |
| `Server Temp Key: X25519, 253 bits` | a chave **efêmera** da troca Diffie–Hellman — descartada ao fim da sessão; é o que dá sigilo futuro | [12](12-handshake.md) |

Agora veja a mesma coisa dando errado, de propósito:

```bash
echo | openssl s_client -connect expired.badssl.com:443 -servername expired.badssl.com -brief 2>&1 | grep -i verif
# esperado: Verification error: certificate has expired
```

---

## Passo 1 · Uma chave privada

```bash
mkdir -p ~/lab-tls && cd ~/lab-tls
```

```bash
openssl genpkey -algorithm EC -pkeyopt ec_paramgen_curve:P-256 -out chave.pem
```
Gera uma chave privada de curva elíptica na curva P-256. É o padrão atual: chaves
menores, handshake mais rápido e segurança equivalente a RSA de 3072 bits.

```bash
ls -l chave.pem
# saída real: -rw------- 1 ronivaldo ronivaldo 241 ago 31 16:32 chave.pem
```

Duas coisas para reparar:

- **241 bytes.** Uma chave RSA de 2048 bits ocupa ~1700. Curva elíptica é compacta.
- **`-rw-------`** (modo 600). O OpenSSL cria assim de propósito. Se em algum momento
  você vir `-rw-r--r--` numa chave privada, corrija: `chmod 600 chave.pem`.

Espie o conteúdo:

```bash
head -1 chave.pem   # -----BEGIN PRIVATE KEY-----
openssl pkey -in chave.pem -noout -text | head -5
```

> **Se quiser RSA em vez de EC** (para compatibilidade com sistemas antigos):
> `openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:2048 -out chave.pem`.
> Prefira EC quando puder; RSA de 2048 continua seguro, mas é mais lento e maior.

---

## Passo 2 · Um certificado

O certificado é a chave **pública** + um nome + validade + a assinatura de alguém.
Aqui vamos assinar com a própria chave — um **certificado autoassinado**. Ele serve
para laboratório e para dentro de casa; ninguém no mundo confia nele, e é isso mesmo
que vamos observar no Passo 4.

```bash
openssl req -x509 -new -key chave.pem -days 30 -out cert.pem \
  -subj "/CN=localhost" \
  -addext "subjectAltName=DNS:localhost,IP:127.0.0.1"
```

| Parte | O que faz |
|---|---|
| `req -x509` | cria um certificado direto, sem passar por um pedido a uma CA |
| `-key chave.pem` | usa esta chave privada (assina com ela e publica a pública correspondente) |
| `-days 30` | validade |
| `-subj "/CN=localhost"` | o *Common Name*, campo legado |
| `-addext "subjectAltName=..."` | **o campo que realmente importa** |

> ### Por que o SAN e não o CN — e este é um "por quê" com resposta histórica
> Antigamente o nome do site ficava no **CN** (*Common Name*). O CN é um campo de
> texto livre herdado do padrão X.500 dos anos 1980, feito para nome de pessoa em
> diretório corporativo, não para nome de host. Ele só cabe **um** nome, e a
> ambiguidade gerou uma família inteira de ataques (nomes com byte nulo, como
> `banco.com\0.atacante.com`, que o parser da CA lia de um jeito e o navegador de outro).
> A RFC 2818 (2000) já dizia para preferir o **SAN** (*Subject Alternative Name*);
> a RFC 6125 (2011) formalizou; o **Chrome 58, em abril de 2017, passou a ignorar o
> CN por completo**. Desde então, **certificado sem SAN simplesmente não funciona**,
> por mais bonito que esteja o CN. Este é um caso claro de "por que é assim": uma
> decisão de projeto ruim dos anos 1990, corrigida por um navegador impondo o padrão
> na marra 17 anos depois.

Confira o que você criou:

```bash
openssl x509 -in cert.pem -noout -subject -issuer -dates -ext subjectAltName
```

Saída real:

```
subject=CN = localhost
issuer=CN = localhost
notBefore=Aug 31 19:32:24 2026 GMT
notAfter=Sep 30 19:32:24 2026 GMT
X509v3 Subject Alternative Name:
    DNS:localhost, IP Address:127.0.0.1
```

**`subject` igual a `issuer` é a definição de autoassinado.** Guarde esse sinal: ao
diagnosticar um problema alheio, comparar esses dois campos responde em um segundo
se o certificado veio de uma CA ou de alguém apressado.

---

## Passo 3 · Um servidor HTTPS

Vinte linhas de Python, sem nenhuma dependência externa:

```python
# arquivo: srv.py
import http.server, ssl

ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)   # contexto TLS no papel de servidor
ctx.load_cert_chain("cert.pem", "chave.pem")    # certificado + chave privada

srv = http.server.HTTPServer(("127.0.0.1", 8443),
                             http.server.SimpleHTTPRequestHandler)
srv.socket = ctx.wrap_socket(srv.socket, server_side=True)  # embrulha o socket em TLS

print("ouvindo em https://localhost:8443/")
srv.serve_forever()
```

```bash
python3 srv.py
```

Repare no que **não** está no código: nenhuma escolha de cifra, de versão, de curva.
O `ssl.SSLContext` do Python já vem com padrões sãos (TLS 1.2+ e o conjunto de cifras
do OpenSSL). Essa é uma boa notícia e uma armadilha: os padrões são bons hoje, mas
em produção você **deve** fixá-los explicitamente, porque o padrão muda com a versão
do runtime — veja [17-configuracao-de-servidores.md](17-configuracao-de-servidores.md).

Repare também na porta **8443** e não 443: portas abaixo de 1024 exigem root
([03 §8.3](03-instalacao.md#8-permissões--e-onde-sudo-estraga-tudo)).

---

## Passo 4 · O cliente recusa — e está certo

Em outro terminal:

```bash
curl https://localhost:8443/
```

Saída real:

```
curl: (60) SSL certificate problem: self-signed certificate
More details here: https://curl.se/docs/sslcerts.html
```

**Isto é um sucesso, não uma falha.** O curl fez exatamente o trabalho dele: pegou o
certificado, procurou o emissor (`CN=localhost`) na lista de raízes confiáveis do
sistema, não achou, e recusou. É o mesmo raciocínio do navegador quando mostra a
tela vermelha.

Erro 60 do curl é, disparado, o erro de TLS mais comum do mundo. Ele tem quatro
causas, e vale saber distingui-las:

| Mensagem completa | Causa |
|---|---|
| `self-signed certificate` | certificado assinado por ele mesmo, como o nosso |
| `unable to get local issuer certificate` | a CA raiz não está no seu repositório **ou** o servidor não mandou os intermediários |
| `certificate has expired` | passou do `notAfter` |
| `no alternative certificate subject name matches target host name` | o certificado é de outro nome |

> ### Nunca resolva isso com `-k`
> `curl -k` (ou `--insecure`) desliga a verificação e a conexão passa. Em laboratório,
> para um teste pontual, tudo bem. Como hábito, é a maneira mais eficiente de
> transformar TLS em teatro: você mantém a criptografia e joga fora a autenticação —
> ou seja, você fica com uma conversa privada **com um desconhecido**. Um atacante
> na rede simplesmente apresenta o certificado dele. Escreveremos isso de novo em
> [75-armadilhas.md](75-armadilhas.md), porque é a armadilha nº 1 do assunto.

---

## Passo 5 · O cliente aceita — e você entendeu por quê

Diga ao curl que, **para este teste**, o `cert.pem` é uma âncora de confiança:

```bash
curl --cacert cert.pem https://localhost:8443/
```

Saída real (o servidor lista o diretório):

```
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html>
<head>
...
```

E no terminal do servidor:

```
127.0.0.1 - - [31/Aug/2026 16:32:24] "GET / HTTP/1.1" 200 -
```

**O que mudou?** Nada na criptografia. Nada no servidor. Mudou **a lista de quem você
confia**. Essa é a lição central do TLS: a parte difícil nunca foi cifrar; foi decidir
em quem acreditar. Cifrar é matemática resolvida desde os anos 1970. Confiança é um
problema social que a PKI resolve de forma imperfeita e cara — assunto de
[13-certificados-e-pki.md](13-certificados-e-pki.md).

Confirme com o `s_client`:

```bash
echo | openssl s_client -connect 127.0.0.1:8443 -servername localhost -CAfile cert.pem -brief
```

Saída real:

```
CONNECTION ESTABLISHED
Protocol version: TLSv1.3
Ciphersuite: TLS_AES_256_GCM_SHA384
Peer certificate: CN = localhost
Hash used: SHA256
Signature type: ECDSA
Verification: OK
Server Temp Key: X25519, 253 bits
DONE
```

Note `Verification: OK` e `Server Temp Key: X25519` — seu servidorzinho de 20 linhas
negociou TLS 1.3 com troca de chaves em curva X25519 e AES-256-GCM. É literalmente a
mesma configuração criptográfica que um banco usa.

> Se você rodar sem `-servername`, o OpenSSL 3.0 imprime
> `Can't use SSL_get_servername` antes do resto. Não é erro: é o aviso de que nenhum
> SNI foi enviado e o servidor não pôde escolher certificado por nome. Sempre passe
> `-servername` ao testar hosts virtuais.

---

## Passo 6 · Sem aviso nenhum, com `mkcert`

O passo 5 exigiu passar `--cacert` em todo comando — insuportável no dia a dia.
O `mkcert` resolve criando uma CA local **que o seu sistema já confia**:

```bash
mkcert -install                       # uma vez por máquina
mkcert localhost 127.0.0.1 ::1        # emite o certificado
# esperado:
#   Created a new certificate valid for the following names 📜
#    - "localhost"
#    - "127.0.0.1"
#   The certificate is at "./localhost+2.pem" and the key at "./localhost+2-key.pem" ✅
```

```bash
ctx_cert=localhost+2.pem; ctx_key=localhost+2-key.pem
python3 - <<PY &
import http.server, ssl
ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ctx.load_cert_chain("$ctx_cert", "$ctx_key")
srv = http.server.HTTPServer(("127.0.0.1", 8443), http.server.SimpleHTTPRequestHandler)
srv.socket = ctx.wrap_socket(srv.socket, server_side=True)
srv.serve_forever()
PY
sleep 1
curl -sI https://localhost:8443/ | head -1
# esperado: HTTP/1.0 200 OK   — SEM --cacert, SEM -k
```

Abra `https://localhost:8443/` no navegador: cadeado, sem aviso.

**O que aconteceu:** o `mkcert -install` colocou a raiz dele no repositório de
confiança do seu sistema e dos navegadores. Do ponto de vista da sua máquina, essa
CA tem exatamente o mesmo poder que a DigiCert. É por isso que a chave dela é
perigosa ([03 §2.5](03-instalacao.md)) e por isso que é assim que um proxy corporativo
consegue ler seu tráfego ([03 §9](03-instalacao.md#9-rede-corporativa-proxy-e-certificado-interno)).

---

## O ciclo de trabalho do dia a dia

```
   ┌──────────────┐
   │ editar config│  nginx.conf / caddyfile / código
   └──────┬───────┘
          ▼
   ┌──────────────┐   nginx -t   |  caddy validate  |  python -c "import ssl"
   │  validar     │   ← pega 80% dos erros ANTES de derrubar o serviço
   └──────┬───────┘
          ▼
   ┌──────────────┐   systemctl reload nginx   (reload, não restart:
   │  recarregar  │    reload não derruba conexões existentes)
   └──────┬───────┘
          ▼
   ┌──────────────┐   curl -v https://...        ← o cliente vê o quê?
   │  verificar   │   openssl s_client -brief    ← o que foi negociado?
   └──────┬───────┘   testssl.sh https://...     ← está fraco em algum ponto?
          ▼
   ┌──────────────┐   journalctl -u nginx -f · tail -f /var/log/nginx/error.log
   │  depurar     │   SSLKEYLOGFILE + Wireshark (só em laboratório)
   └──────────────┘
```

Os quatro comandos que você vai usar mais que qualquer outro:

```bash
openssl s_client -connect HOST:443 -servername HOST -brief </dev/null   # o que foi negociado
openssl x509 -in cert.pem -noout -text                                  # o que diz o certificado
curl -vI https://HOST                                                    # o que o cliente real vê
nginx -t                                                                 # a config está válida?
```

---

## Os primeiros cinco erros de **uso** (não de instalação)

### 1. `curl: (60) ... unable to get local issuer certificate`, mas no navegador funciona

**Causa:** o servidor está enviando só o certificado folha, sem os **intermediários**.
O navegador tem cache de intermediários de visitas anteriores e/ou busca pelo campo
*AIA*; o curl não faz nada disso. Diagnóstico:

```bash
echo | openssl s_client -connect HOST:443 -servername HOST -showcerts 2>/dev/null | grep -c "BEGIN CERTIFICATE"
# 1 = só a folha → cadeia incompleta, conserte
# 2 ou 3 = folha + intermediário(s) → correto
```

**Correção:** aponte o servidor para o **fullchain**, não para o `cert.pem` sozinho.
No Let's Encrypt: use `fullchain.pem`, nunca `cert.pem`. É o erro nº 1 do mundo real.

### 2. `SSL: no alternative certificate subject name matches target host name`

Você acessou por um nome que não está no SAN. Frequentemente: certificado emitido
para `exemplo.com` e você acessou `www.exemplo.com`, ou acessou pelo IP.

```bash
openssl x509 -in cert.pem -noout -ext subjectAltName
```

**Correção:** reemita incluindo todos os nomes. Curinga (`*.exemplo.com`) cobre um
único nível — cobre `www.exemplo.com`, **não** cobre `a.b.exemplo.com` nem o
`exemplo.com` pelado.

### 3. `key values mismatch` ao iniciar o servidor

Você juntou a chave de um certificado com o certificado de outro. Comprove:

```bash
openssl x509 -noout -pubkey -in cert.pem  | openssl sha256
openssl pkey  -pubout    -in chave.pem    | openssl sha256
# os dois hashes têm de ser IDÊNTICOS
```

### 4. Alterou o certificado e "não mudou nada"

O servidor lê o certificado do disco **quando inicia**. Trocar o arquivo não faz
efeito até um `reload`. Além disso, o cliente pode estar **retomando a sessão**
(*session resumption*) — reuso de uma sessão TLS anterior sem novo handshake.
Para forçar handshake completo no teste: `curl --no-sessionid` ou
`openssl s_client -no_ticket`.

### 5. Funciona em `localhost` e falha do celular / de outra máquina

Três causas, nesta ordem de probabilidade: (a) o servidor está escutando só em
`127.0.0.1` — mude para `0.0.0.0`; (b) firewall; (c) a CA do `mkcert` só existe na
**sua** máquina — o celular não a conhece, e nem deve. Para testar em outros
dispositivos, use um certificado real ([16](16-acme-e-automacao.md)) ou instale a
raiz do mkcert no dispositivo de teste, conscientemente.

---

## Verificação final deste arquivo

```bash
cd ~/lab-tls
ls                                        # chave.pem cert.pem srv.py
openssl x509 -in cert.pem -noout -dates   # ainda dentro da validade
curl -s --cacert cert.pem https://localhost:8443/ >/dev/null && echo "OK: HTTPS local funcionando"
```

---

## Para onde ir agora

| Você quer… | Vá para |
|---|---|
| receitas prontas para tarefas concretas | [06-exemplos.md](06-exemplos.md) — 14 exemplos executáveis |
| uma aplicação inteira com CA própria e mTLS | [07-projeto-modelo/](07-projeto-modelo/README.md) |
| a referência de comandos | [05-manual-de-uso.md](05-manual-de-uso.md) |
| certificado de verdade, do Let's Encrypt | [16-acme-e-automacao.md](16-acme-e-automacao.md) |
| entender o que acabou de acontecer no fio | [12-handshake.md](12-handshake.md) |

---

## Autoteste

1. O que `Verification: OK` no `s_client` garante, exatamente?
2. Por que o SAN substituiu o CN, e desde quando o Chrome ignora o CN?
3. `subject` igual a `issuer` significa o quê?
4. O `curl` recusou seu certificado. Cite as quatro causas possíveis do erro 60.
5. Entre `curl -k` e `curl --cacert cert.pem`, qual usar em laboratório e por quê?
6. Você trocou o `cert.pem` e o servidor continua servindo o antigo. Duas explicações possíveis?
7. Por que o certificado do `mkcert` funciona sem aviso na sua máquina e falha no celular?
8. Como saber, em um comando, se um servidor está enviando a cadeia completa?
9. Por que os laboratórios usam a porta 8443 em vez da 443?

*Respostas: §Passo 0, §Passo 2 (caixa), §Passo 2, §Passo 4, §Passo 4/5, §Erro 4, §Passo 6, §Erro 1, §Passo 3.*

---

**Próximo:** [05-manual-de-uso.md](05-manual-de-uso.md) — a referência que você vai consultar por anos.
