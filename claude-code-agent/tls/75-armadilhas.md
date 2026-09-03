# 75 · Armadilhas e mitos

**Nível:** todos · **Data:** 31/08/2026

28 armadilhas que derrubam sistemas de verdade e 12 mitos que não morrem.
Ordenadas por **frequência com que causam incidente**, não por gravidade teórica.

---

## Parte I — As 28 armadilhas

### 🔴 Nível 1 — as que causam incidente esta semana em alguma empresa

#### 1. `cert.pem` em vez de `fullchain.pem`

O erro nº 1 do mundo. Funciona no seu Chrome (que tem cache de intermediário e busca
por AIA) e falha no `curl`, no Java, no Go, no Android e no cliente do seu parceiro.

```bash
echo | openssl s_client -connect HOST:443 -servername HOST -showcerts 2>/dev/null | grep -c "BEGIN CERT"
# 1 = errado · 2 ou 3 = certo
```

**Correção:** `ssl_certificate .../fullchain.pem;`. Sempre.

#### 2. `curl -k` / `verify=False` / `InsecureSkipVerify: true`

Você mantém a criptografia e joga fora a autenticação: uma conversa privada **com um
desconhecido**. Um atacante na rede apresenta o certificado dele e você aceita.

```bash
grep -rn "verify=False\|InsecureSkipVerify\|NODE_TLS_REJECT_UNAUTHORIZED\|rejectUnauthorized: *false\|CERT_NONE\|check_hostname *= *False" . \
  --include=*.py --include=*.js --include=*.ts --include=*.go --include=*.java
```

**Coloque esse `grep` no CI hoje.** É a maior relação custo-benefício deste arquivo.

#### 3. Certificado vencido

Continua sendo, disparado, o incidente mais frequente de TLS — e vai piorar: 200 dias
desde março de 2026, 100 em 2027, 47 em 2029.

**Correção:** ACME automatizado **e** monitoramento externo de validade
([06 Exemplo 2](06-exemplos.md)). Monitore o resultado, não o processo.

#### 4. Chave privada no Git

Acontece toda semana, em toda empresa. E `git rm` não resolve: fica no histórico, nos
clones, nos forks, no cache do GitHub.

```bash
git log --all --full-history --diff-filter=A --name-only | grep -Ei "\.key$|privkey|\.pem$"
```

**Correção:** trate como comprometida ([20 §9](20-desempenho-e-operacao.md)), gere
chave nova, revogue a antiga. Previna com `.gitignore`, `gitleaks` no CI e proteção de
segredos do provedor.

#### 5. Renovou e não recarregou

O servidor lê o certificado ao iniciar. Trocar o arquivo não faz efeito.

**Correção:** gancho de deploy no certbot ([16 §6](16-acme-e-automacao.md)), ou recarga
dentro da aplicação (`GetCertificate` no Go, `setSecureContext` no Node).

#### 6. Sem SAN, só CN

Navegadores ignoram o CN desde 2017 (Chrome 58).

```bash
openssl x509 -in c.pem -noout -ext subjectAltName || echo "SEM SAN — não vai funcionar"
```

#### 7. `verify_client optional` em vez de `on`

mTLS que aceita quem não tem certificado. O desenvolvedor acredita ter autenticação
mútua; não tem.

**Correção:** `on`/`require`, e um **teste automatizado que tenta sem certificado e
exige falha** ([projeto-modelo](07-projeto-modelo/README.md), teste 40).

#### 8. `requestCert: true` sem `rejectUnauthorized: true` (Node)

A mesma armadilha, na sintaxe do Node. Os dois andam juntos, sempre.

---

### 🟠 Nível 2 — as que causam incidente este trimestre

#### 9. Relógio errado

`certificate is not yet valid` ou `has expired` num certificado perfeitamente válido.
Comum em contêineres sem NTP, VMs suspensas e dispositivos embarcados.

**Correção:** NTP obrigatório; margem de alguns minutos no `notBefore` ao emitir.

#### 10. `X-Forwarded-Proto` esquecido

A aplicação acha que a requisição veio por HTTP, gera links `http://`, o navegador
bloqueia conteúdo misto, e o *loop* de redirecionamento aparece.

#### 11. `ssl_stapling on` sem `resolver`

Falha **em silêncio**. Você acredita ter stapling e não tem.

```bash
echo | openssl s_client -connect HOST:443 -servername HOST -status 2>&1 | grep -A2 "OCSP Response Status"
```

#### 12. Curinga achando que cobre tudo

`*.exemplo.com` **não** cobre `exemplo.com` nem `a.b.exemplo.com`.

#### 13. Volume do ACME não persistido em container

Cada restart pede certificado novo. Em poucos dias: `too many certificates already
issued`, e **7 dias sem HTTPS**.

#### 14. HSTS agressivo cedo demais

`max-age=63072000; includeSubDomains; preload` no primeiro dia, e um subdomínio antigo
em HTTP fica inacessível por **dois anos**, sem como cancelar.

**Correção:** o roteiro de [17 §9](17-configuracao-de-servidores.md) — 300 s → 1 dia →
2 anos → `includeSubDomains` → `preload`.

#### 15. Cadeia com a raiz incluída

Não quebra nada, mas desperdiça bytes em **todo** handshake. Envie folha + intermediários.

#### 16. Certificado interno emitido por CA pública

O nome do host vai para os logs de Certificate Transparency, **permanentemente**.
`homologacao-financeiro.exemplo.com.br` vira alvo público.

**Correção:** curinga, ou CA interna.

#### 17. `sslmode=require` no PostgreSQL

Cifra sem verificar identidade. Use `verify-full`. Vale o análogo no MySQL
(`VERIFY_IDENTITY`) e no MongoDB.

#### 18. Cookie de sessão sem `Secure`

Vai também em requisições HTTP. TLS não protege o que sai por fora dele.

#### 19. Confiar em `X-Client-DN` sem sobrescrever no proxy

Se o proxy não sobrescreve o cabeçalho em toda requisição, o cliente o envia sozinho e
se declara quem quiser. Autenticação de mTLS anulada por um cabeçalho HTTP.

#### 20. Chave privada com permissão frouxa

```bash
find /etc -name "*.key" -o -name "privkey*.pem" 2>/dev/null | xargs -r ls -l | awk '$1 ~ /^-...r..r../'
```

---

### 🟡 Nível 3 — as sutis, que mordem quando você menos espera

#### 21. Tickets de sessão sem rotação

O nginx gera a chave ao iniciar e nunca a troca. Se ela vazar, o sigilo futuro do
ECDHE é anulado para todas as sessões retomadas ([17 §2.1](17-configuracao-de-servidores.md)).

#### 22. 0-RTT em requisição não idempotente

Dados de 0-RTT **podem ser repetidos**, por construção. Um `POST /transferir` em 0-RTT
pode ser reexecutado por um atacante que capturou o pacote.

#### 23. Pinning sem pino de reserva

Perdeu a chave? Todos os apps instalados param, e a correção é uma atualização na loja
— dias, dependendo do usuário. **Sempre dois ou mais pinos**, um deles offline.

#### 24. `copy_extensions = copyext` ao assinar CSR de terceiros

Quem manda o CSR escolhe as próprias extensões, inclusive `CA:TRUE`. Você acabou de
emitir uma autoridade certificadora para quem pediu um certificado de cliente.

#### 25. Reutilizar a chave ao reemitir

`certbot renew` gera chave nova por padrão; `--reuse-key` não. Se você reemite após um
comprometimento **com a mesma chave**, não corrigiu nada.

#### 26. Verificar a cadeia e esquecer o nome

O código valida a cadeia, o OpenSSL diz OK, e o certificado é de **outro domínio**.
Em Python, `SSLContext(PROTOCOL_TLS_CLIENT)` liga `check_hostname`; `SSLContext(PROTOCOL_TLS)` não.

#### 27. Uma CA por dois ambientes

Um certificado de homologação vale em produção. Separe por intermediário, e restrinja
com `nameConstraints` ([18 §4.2](18-mtls-e-pki-interna.md)).

#### 28. Achar que "rede interna é confiável"

Serviço interno em HTTP puro "porque está na VPC". Um contêiner comprometido lê tudo
que passa. Zero trust não é moda: é a admissão de que o perímetro não existe mais.

---

## Parte II — Os 12 mitos

### Mito 1 — "Cadeado = site confiável"

**Falso.** Cadeado significa: a conversa é privada e é com o dono daquele domínio.
Um site de golpe emite certificado gratuito em segundos e tem cadeado. O cadeado diz
**com quem** você fala, não se essa pessoa é honesta.

### Mito 2 — "SSL e TLS são coisas diferentes"

São o mesmo protocolo em épocas diferentes. SSL é o nome de 1994–1996; TLS, desde 1999.
"Certificado SSL" é vocabulário fossilizado do mercado.

### Mito 3 — "HTTPS protege meus dados"

Protege **em trânsito**. No servidor, os dados são decifrados. Servidor invadido, banco
sem criptografia, log com dados sensíveis — TLS não ajudou em nada.

### Mito 4 — "Com HTTPS ninguém sabe quais sites eu acesso"

O IP de destino é visível. O SNI também, na esmagadora maioria dos casos. E o DNS
costuma ser em claro. O ECH corrige o SNI, mas só virou RFC em março de 2026 e tem
adoção baixa ([65 §4](65-estado-da-arte.md)).

### Mito 5 — "Preciso comprar certificado"

Falso desde 2015. Let's Encrypt emite de graça, automatizado, aceito por todos os
navegadores. E é a maior CA do mundo em volume.

### Mito 6 — "Certificado EV é mais seguro"

**Criptograficamente idêntico** ao DV. A barra verde que o justificava foi removida do
Chrome e do Firefox em 2019. Se alguma norma exige, cumpra; como escolha técnica, não
se sustenta ([13 §6](13-certificados-e-pki.md)).

### Mito 7 — "RSA-4096 é mais seguro que EC P-256"

RSA-4096 tem ~152 bits de segurança; EC P-256 tem ~128. A diferença é irrelevante na
prática (2^128 já é inatingível), e o RSA-4096 é **muito** mais lento e maior.
Para servidor web, ECDSA P-256 é a escolha certa. Chaves grandes viraram sinônimo de
segurança por analogia com senhas — a analogia é falsa.

### Mito 8 — "Preciso de A+ no SSL Labs"

A nota é uma ferramenta, não um objetivo. Chegar a A+ desligando TLS 1.2 pode cortar
clientes reais. Entenda cada achado e decida com contexto. **Um A com renovação
automática vale mais que um A+ renovado à mão.**

### Mito 9 — "TLS deixa o site lento"

O Google mediu <1% de CPU adicional ao ligar HTTPS no Gmail em 2010. Hoje a cifra
simétrica roda a ~5,5 GB/s por núcleo ([20 §1](20-desempenho-e-operacao.md)). O custo
está no handshake, e a retomada de sessão o elimina.

### Mito 10 — "TLS 1.3 é retrocompatível, é só ligar"

É, sim, e você deve ligar. Mas há efeitos: alguns *middlebox* antigos quebram,
`ssl_ciphers` não afeta o TLS 1.3 (as suites são fixas), e as opções de retomada mudam.
Teste, não presuma.

### Mito 11 — "mTLS resolve autenticação e autorização"

Resolve **autenticação**. Sem uma camada de autorização, todo cliente da sua CA acessa
todo endpoint ([18 §2](18-mtls-e-pki-interna.md)).

### Mito 12 — "Certificado autoassinado é inseguro"

A criptografia é **idêntica**. O que falta é um terceiro atestando a identidade — o que
não importa quando **você** é as duas pontas e distribui a âncora de confiança
conscientemente (PKI interna, mTLS, IoT provisionado). O que é inseguro é
**clicar em "aceitar risco"** num autoassinado que você não emitiu.

---

## Autoauditoria em 12 comandos

```bash
# 1. cadeia completa?
echo | openssl s_client -connect HOST:443 -servername HOST -showcerts 2>/dev/null | grep -c "BEGIN CERT"
# 2. quando vence?
echo | openssl s_client -connect HOST:443 -servername HOST 2>/dev/null | openssl x509 -noout -dates
# 3. protocolos antigos desligados?
for v in tls1 tls1_1; do echo | openssl s_client -connect HOST:443 -"$v" >/dev/null 2>&1 && echo "$v ACEITO — corrija"; done
# 4. HSTS?
curl -sI https://HOST | grep -i strict-transport-security
# 5. stapling?
echo | openssl s_client -connect HOST:443 -servername HOST -status 2>&1 | grep -c "OCSP Response Status: successful"
# 6. verificação desligada no código?
grep -rn "verify=False\|InsecureSkipVerify\|rejectUnauthorized: *false\|CERT_NONE" . --include=*.py --include=*.js --include=*.go
# 7. chave no Git?
git log --all --full-history --diff-filter=A --name-only | grep -Ei "\.key$|privkey"
# 8. permissões das chaves
find /etc -name "*.key" -o -name "privkey*.pem" 2>/dev/null | xargs -r ls -l
# 9. renovação funciona?
sudo certbot renew --dry-run
# 10. CAA publicado?
dig +short CAA HOST
# 11. quem emitiu para o meu domínio? (CT)
curl -s "https://crt.sh/?q=HOST&output=json" | head -c 500
# 12. auditoria completa
testssl.sh --severity HIGH https://HOST
```

---

## Autoteste

1. Por que `cert.pem` funciona no Chrome e falha no curl?
2. O que exatamente `curl -k` desliga, e o que sobra?
3. Qual armadilha vai piorar com a validade de 47 dias em 2029?
4. `verify_client optional` — qual é a consequência exata, e como testá-la?
5. Por que `ssl_stapling on` sem `resolver` é pior que não ter stapling?
6. Quais são os dois riscos irreversíveis do HSTS?
7. Por que emitir certificado público para um host interno é um problema?
8. Por que `sslmode=require` não é seguro?
9. Desmonte o mito 7 (RSA-4096 vs EC P-256) com números.
10. Por que um certificado autoassinado **não** é criptograficamente inseguro?
11. Por que "A+ no SSL Labs" pode ser um objetivo ruim?
12. Escolha três armadilhas do nível 1 e diga como você as preveniria no seu CI.

*Respostas: §1, §2, §3, §7, §11, §14, §16, §17, Mito 7, Mito 12, Mito 8, §2/§3/§4.*

---

**Próximo:** [80-custos-e-licencas.md](80-custos-e-licencas.md).
