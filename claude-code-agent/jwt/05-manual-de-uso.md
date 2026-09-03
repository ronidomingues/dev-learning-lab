# 5 · Manual de uso — referência consultável

> Nível: iniciante a avançado · Atualizado em 14/08/2026
> Organizado **por tarefa**, não por ordem alfabética. Use o índice.

---

## Índice

- [A · Claims: a tabela que você vai consultar toda semana](#a--claims)
- [B · Cabeçalho JOSE](#b--cabeçalho-jose)
- [C · Algoritmos: qual escolher](#c--algoritmos-qual-escolher)
- [D · Receitas por tarefa — `jose` (JavaScript)](#d--receitas-por-tarefa--jose-javascript)
- [E · Receitas por tarefa — PyJWT](#e--receitas-por-tarefa--pyjwt)
- [F · OpenSSL: gerar e converter chaves](#f--openssl-gerar-e-converter-chaves)
- [G · Terminal: inspecionar tokens](#g--terminal-inspecionar-tokens)
- [H · Códigos de status e cabeçalhos HTTP](#h--códigos-de-status-e-cabeçalhos-http)
- [I · Tempos de vida: valores de referência](#i--tempos-de-vida-valores-de-referência)
- [J · O que está obsoleto](#j--o-que-está-obsoleto)
- [K · Atalhos que só quem usa há anos conhece](#k--atalhos-que-só-quem-usa-há-anos-conhece)

---

## A · Claims

*Claim* = uma afirmação dentro do payload. Um par nome/valor.

### A.1 · Claims registradas (RFC 7519 §4.1)

São sete, todas opcionais pela especificação — e **isso é um problema da
especificação**, não uma liberdade sua. Trate `iss`, `aud` e `exp` como
obrigatórios.

| Claim | Nome | Tipo | O que significa | Recomendação |
|---|---|---|---|---|
| `iss` | *issuer* | string (URI) | quem emitiu | **sempre emita e sempre verifique** |
| `sub` | *subject* | string | de quem o token fala. Único dentro do emissor | sempre; use um ID interno, nunca e-mail |
| `aud` | *audience* | string **ou array** | para quem o token vale | **sempre emita e sempre verifique** |
| `exp` | *expiration time* | NumericDate | a partir daí não vale mais | **sempre**; token sem `exp` é token eterno |
| `nbf` | *not before* | NumericDate | antes disso não vale | só se você tem caso de uso |
| `iat` | *issued at* | NumericDate | quando foi emitido | sempre — habilita a verificação de idade máxima |
| `jti` | *JWT ID* | string | identificador único do token | sempre que precisar revogar |

**NumericDate** = número de **segundos** (não milissegundos) desde
1970-01-01T00:00:00Z, ignorando segundos bissextos. Pode ser fracionário.

```bash
# agora, em NumericDate
date +%s
# esperado: 1786726076

# converter NumericDate para data legível
date -d @1786726976            # Linux
date -r 1786726976             # macOS
node -e 'console.log(new Date(1786726976*1000).toISOString())'
```

### A.2 · Claims públicas comuns (do OpenID Connect)

Definidas na especificação do OIDC, registradas na IANA. Aparecem sobretudo em
`id_token`.

| Claim | Significado | Cuidado |
|---|---|---|
| `name`, `given_name`, `family_name` | nome da pessoa | **dado pessoal — vai para os logs** |
| `email` | e-mail | idem; e só confie se `email_verified` for `true` |
| `email_verified` | booleano | sem ele, `email` não prova nada |
| `preferred_username` | nome de exibição | **muda com o tempo — nunca use como chave** |
| `picture` | URL do avatar | — |
| `locale`, `zoneinfo` | idioma, fuso | — |
| `auth_time` | quando a pessoa autenticou de fato | útil para exigir reautenticação |
| `nonce` | valor anti-repetição do fluxo OIDC | **verifique** que bate com o que você enviou |
| `acr`, `amr` | nível e método de autenticação (ex.: `mfa`) | use para exigir 2FA em rota sensível |
| `azp` | para qual cliente o token foi emitido | verifique em cenário multi-cliente |

### A.3 · Claims de access token (RFC 9068)

| Claim | Significado |
|---|---|
| `scope` | string com escopos separados por **espaço**: `"leitura escrita"` |
| `client_id` | qual aplicação obteve o token |
| `roles`, `groups`, `entitlements` | autorização — formato livre |
| `cnf` | *confirmation*: prende o token a uma chave (DPoP/mTLS) — ver [65](65-estado-da-arte.md) |

### A.4 · Suas próprias claims

Você pode inventar as que quiser. Duas convenções:

```json
{ "https://suaempresa.com/departamento": "financeiro" }   // com namespace — evita colisão futura
{ "departamento": "financeiro" }                          // sem namespace — mais curto
```

A RFC recomenda o namespace. Na prática, quase todo mundo usa nome curto em token
interno e namespace quando o token atravessa organizações. O Auth0 **exige**
namespace em claims personalizadas.

> **Regra de ouro do payload:** cada byte aqui é pago em **toda** requisição HTTP da
> aplicação, para sempre. Um token de 4 KB × 200 requisições por página × milhões de
> usuários é tráfego real e latência real. Coloque o mínimo.

---

## B · Cabeçalho JOSE

| Parâmetro | Significado | Notas |
|---|---|---|
| `alg` | algoritmo de assinatura | **obrigatório**. Nunca use este campo para *escolher* como verificar |
| `typ` | tipo do token | `JWT` genérico; `at+jwt` para access token (RFC 9068); `dpop+jwt`; `secevent+jwt` |
| `kid` | qual chave assinou | essencial para rotação. É só um identificador — nunca um caminho |
| `cty` | tipo do conteúdo | `JWT` quando há um JWT dentro de outro (*nested*) |
| `crit` | extensões obrigatórias | se você não entende o que está listado aqui, **recuse o token** |
| `jku` | URL do JWKS | ⚠️ **perigoso**: o token dizendo onde buscar a chave que o valida |
| `jwk` | a chave embutida no token | ⚠️ **nunca confie**: é o atacante mandando a própria chave |
| `x5u`, `x5c`, `x5t` | certificado X.509 | mesmas ressalvas de `jku`/`jwk` |
| `enc`, `zip` | só em JWE | ver [15-criptografia-jwe.md](15-criptografia-jwe.md) |

---

## C · Algoritmos: qual escolher

### C.1 · Tabela de decisão

| `alg` | Tipo | Tamanho da assinatura | Use quando |
|---|---|---|---|
| **`EdDSA`** (Ed25519) | assimétrico | 64 B | melhor escolha técnica hoje; suporte um pouco menor em bibliotecas antigas |
| **`ES256`** | assimétrico (P-256) | 64 B | **padrão recomendado**: suporte universal, assinatura curta |
| `ES384`, `ES512` | assimétrico | 96 B, 132 B | exigência regulatória de curva maior |
| **`RS256`** | assimétrico (RSA) | **256 B** (chave 2048) | interoperabilidade máxima; é o que quase todo provedor OIDC usa |
| `PS256` | assimétrico (RSA-PSS) | 256 B | melhor que RS256 tecnicamente (padding com prova de segurança), pouco adotado |
| **`HS256`** | simétrico | 32 B | **só** quando quem assina e quem verifica são o mesmo serviço |
| `HS384`, `HS512` | simétrico | 48 B, 64 B | raramente necessário |
| `none` | — | 0 | **nunca.** Ver [20-ataques-e-defesas.md](20-ataques-e-defesas.md) |

### C.2 · A pergunta que decide entre HS e ES

> **Quem precisa verificar este token?**

- **Só o serviço que o emitiu** → `HS256` serve, e é mais simples.
- **Qualquer outro serviço, agora ou no futuro** → `ES256`.

Com HMAC, dar a alguém o poder de *verificar* é dar o poder de *forjar* — é a mesma
chave. É uma decisão difícil de reverter depois que 15 serviços já compartilham o
segredo. Minha recomendação profissional: **comece com ES256 mesmo quando HS256
bastaria**. O custo é uma tarde; o custo de migrar depois é um trimestre.

### C.3 · Tamanhos mínimos de chave

| Algoritmo | Mínimo | Por quê |
|---|---|---|
| HS256 | **32 bytes** de aleatoriedade real | RFC 7518 §3.2. Senha digitada não serve: é adivinhável offline |
| HS384 / HS512 | 48 / 64 bytes | idem |
| RS256 | **2048 bits** | abaixo disso é quebrável; 3072 para prazo longo |
| ES256 | P-256 | ~128 bits de segurança |

```bash
# gerar um segredo HMAC correto
openssl rand -base64 32
# esperado: 44 caracteres, ex.: 8Kj2...=
```

---

## D · Receitas por tarefa — `jose` (JavaScript)

Versão 6.2.8 (14/08/2026). `npm install jose`.

### Assinar

```js
import { SignJWT } from 'jose';

const token = await new SignJWT({ papeis: ['usuario'] })   // claims próprias
  .setProtectedHeader({ alg: 'ES256', kid: 'chave-2026-08', typ: 'at+jwt' })
  .setIssuer('https://auth.exemplo.com')
  .setAudience('api-pedidos')
  .setSubject('u-42')
  .setIssuedAt()
  .setExpirationTime('15m')      // aceita '15m', '2h', '7d', ou um NumericDate
  .setJti(crypto.randomUUID())
  .sign(chavePrivada);
```

### Verificar

```js
import { jwtVerify } from 'jose';

const { payload, protectedHeader } = await jwtVerify(token, chavePublica, {
  algorithms: ['ES256'],                   // OBRIGATÓRIO na prática
  issuer: 'https://auth.exemplo.com',
  audience: 'api-pedidos',
  clockTolerance: '60s',
  typ: 'at+jwt',
  maxTokenAge: '1h',                       // opcional: idade máxima desde iat
});
```

### Verificar com JWKS remoto (o caso mais comum em produção)

```js
import { createRemoteJWKSet, jwtVerify } from 'jose';

// Criado UMA VEZ, no início do processo. Ele cacheia e reobtém sozinho
// quando aparece um kid desconhecido — com proteção contra tempestade de
// requisições. Criar dentro do handler é o erro clássico: faz uma chamada de
// rede por requisição.
const jwks = createRemoteJWKSet(
  new URL('https://auth.exemplo.com/.well-known/jwks.json'),
  { cacheMaxAge: 600_000, cooldownDuration: 30_000 },
);

const { payload } = await jwtVerify(token, jwks, {
  algorithms: ['RS256'],
  issuer: 'https://auth.exemplo.com',
  audience: 'api-pedidos',
});
```

### Gerar e exportar chaves

```js
import { generateKeyPair, exportJWK, exportPKCS8, exportSPKI, calculateJwkThumbprint } from 'jose';

const { privateKey, publicKey } = await generateKeyPair('ES256', { extractable: true });
const jwkPublico = await exportJWK(publicKey);
const kid = await calculateJwkThumbprint(jwkPublico);      // RFC 7638
const pemPrivado = await exportPKCS8(privateKey);
const pemPublico = await exportSPKI(publicKey);
```

### Importar chave existente

```js
import { importPKCS8, importSPKI, importJWK } from 'jose';

const privada = await importPKCS8(pemPrivado, 'ES256');
const publica = await importSPKI(pemPublico, 'ES256');
const deJwk   = await importJWK(jwkPublico, 'ES256');
const segredo = new TextEncoder().encode(process.env.JWT_SECRET);  // HMAC
```

### Decodificar sem verificar (só para depurar / ler o `kid`)

```js
import { decodeJwt, decodeProtectedHeader } from 'jose';
const payload   = decodeJwt(token);              // NÃO valida nada
const cabecalho = decodeProtectedHeader(token);  // para descobrir o kid
```

### Tratar erros por tipo

```js
import { errors } from 'jose';

try {
  await jwtVerify(token, chave, opcoes);
} catch (e) {
  if (e instanceof errors.JWTExpired)          return renovar();          // 401, cliente renova
  if (e instanceof errors.JWTClaimValidationFailed) return recusar(403);  // aud/iss errado
  if (e instanceof errors.JWSSignatureVerificationFailed) return alertar(); // suspeito!
  if (e instanceof errors.JWKSNoMatchingKey)   return recusar(401);       // kid desconhecido
  throw e;
}
```

Distinguir "expirou" de "assinatura inválida" é importante: o primeiro é rotina, o
segundo merece alerta de segurança.

---

## E · Receitas por tarefa — PyJWT

Versão ≥ 2.13.0 (por causa da CVE-2026-48526). `pip install "PyJWT[crypto]>=2.13.0"`.

```python
import jwt, time, uuid

# --- assinar ---
token = jwt.encode(
    {
        "iss": "https://auth.exemplo.com",
        "sub": "u-42",
        "aud": "api-pedidos",
        "exp": int(time.time()) + 900,
        "iat": int(time.time()),
        "jti": str(uuid.uuid4()),
        "papeis": ["usuario"],
    },
    chave_privada,
    algorithm="ES256",
    headers={"kid": "chave-2026-08", "typ": "at+jwt"},
)

# --- verificar ---
payload = jwt.decode(
    token,
    chave_publica,
    algorithms=["ES256"],          # OBRIGATÓRIO — sem isto o PyJWT levanta erro
    issuer="https://auth.exemplo.com",
    audience="api-pedidos",
    leeway=60,
    options={"require": ["exp", "iat", "iss", "aud", "sub"]},
)

# --- JWKS remoto ---
cliente = jwt.PyJWKClient("https://auth.exemplo.com/.well-known/jwks.json",
                          cache_keys=True, lifespan=600)
chave = cliente.get_signing_key_from_jwt(token).key

# --- só o cabeçalho, para achar o kid ---
cabecalho = jwt.get_unverified_header(token)
```

> `options={"require": [...]}` é o recurso mais subutilizado do PyJWT. Sem ele, um
> token **sem** `exp` passa alegremente na validação.

---

## F · OpenSSL: gerar e converter chaves

```bash
# --- EC P-256 (ES256) — o recomendado -------------------------------------
openssl ecparam -name prime256v1 -genkey -noout -out privada-ec.pem
openssl ec -in privada-ec.pem -pubout -out publica-ec.pem
chmod 600 privada-ec.pem
```

```bash
# --- Ed25519 (EdDSA) — o mais moderno -------------------------------------
openssl genpkey -algorithm ed25519 -out privada-ed.pem
openssl pkey -in privada-ed.pem -pubout -out publica-ed.pem
```

```bash
# --- RSA 2048 (RS256) — o mais interoperável ------------------------------
openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:2048 -out privada-rsa.pem
openssl rsa -in privada-rsa.pem -pubout -out publica-rsa.pem
```

```bash
# --- segredo HMAC (HS256) -------------------------------------------------
openssl rand -base64 32
```

```bash
# --- inspecionar ----------------------------------------------------------
openssl pkey -in privada-ec.pem -text -noout      # detalhes da chave
openssl pkey -in privada-ec.pem -pubout -outform DER | openssl dgst -sha256
```

```bash
# --- converter PKCS#1 (BEGIN RSA PRIVATE KEY) para PKCS#8 (BEGIN PRIVATE KEY)
openssl pkcs8 -topk8 -nocrypt -in antiga-pkcs1.pem -out nova-pkcs8.pem
```
> Quase toda biblioteca moderna quer **PKCS#8** (`-----BEGIN PRIVATE KEY-----`). Se a
> sua chave começa com `-----BEGIN RSA PRIVATE KEY-----`, é PKCS#1 e precisa desta
> conversão. Sintoma sem converter: `error:0909006C:PEM routines:get_name:no start line`.

---

## G · Terminal: inspecionar tokens

```bash
# payload de um token na variável $AT
echo "$AT" | cut -d. -f2 | tr '_-' '/+' | base64 -d 2>/dev/null | jq .

# cabeçalho
echo "$AT" | cut -d. -f1 | tr '_-' '/+' | base64 -d 2>/dev/null | jq .

# quando expira, em data legível
echo "$AT" | cut -d. -f2 | tr '_-' '/+' | base64 -d 2>/dev/null \
  | jq -r '.exp | todate'

# quanto falta, em segundos
echo "$AT" | cut -d. -f2 | tr '_-' '/+' | base64 -d 2>/dev/null \
  | jq --argjson agora "$(date +%s)" '.exp - $agora'
```

Com `jwt-cli` instalado:

```bash
jwt decode "$AT"                                    # formatado
jwt decode -j "$AT" | jq .payload                   # JSON puro
jwt verify --alg ES256 --secret @publica-ec.pem "$AT"
jwt encode --alg HS256 --secret "$SEG" --exp=+15m --sub u-42 '{"papeis":["admin"]}'
```

---

## H · Códigos de status e cabeçalhos HTTP

| Situação | Status | `WWW-Authenticate` |
|---|---|---|
| Sem cabeçalho `Authorization` | **401** | `Bearer realm="api"` |
| Token malformado, expirado ou assinatura inválida | **401** | `Bearer error="invalid_token", error_description="..."` |
| Token válido, mas sem permissão para a operação | **403** | `Bearer error="insufficient_scope", scope="escrita"` |
| Token válido, mas o recurso é de outra pessoa | **403** (ou 404, para não revelar existência) | — |

**401 vs. 403 é a confusão mais comum.** 401 = "não sei quem você é (ou não acredito)
— tente autenticar de novo". 403 = "sei quem você é e a resposta é não — não adianta
tentar de novo". Um cliente que recebe 401 renova o token; um que recebe 403 não
deve. Trocar os dois causa laço infinito de renovação.

```http
Authorization: Bearer eyJhbGciOiJFUzI1NiIsInR5cCI6ImF0K2p3dCJ9...
Cache-Control: no-store
```

`Cache-Control: no-store` em **toda** resposta que contenha token: sem isso, um proxy
intermediário pode guardar e servir o token de uma pessoa para outra.

---

## I · Tempos de vida: valores de referência

Não são lei; são o consenso do mercado em 2026, e o ponto de partida honesto.

| Token | Vida típica | Por quê |
|---|---|---|
| Access token (web/mobile) | **5 a 15 min** | não é revogável até expirar; a janela de estrago é o tempo de vida |
| Access token (serviço↔serviço, rede fechada) | 1 a 24 h | risco menor, custo de renovação alto |
| `id_token` (OIDC) | 5 a 60 min | consumido uma vez, no login |
| Refresh token (cliente confidencial) | 30 a 90 dias | fica no servidor |
| Refresh token (SPA/mobile, com rotação) | 8 h a 30 dias | rotação + detecção de reuso |
| Token de "esqueci a senha" | **15 min**, uso único | vai por e-mail, que não é canal seguro |
| Token de convite | 24 h a 7 dias | conveniência vence |
| Token de verificação de e-mail | 24 h | idem |
| Token de máquina (CI, cron) | mais curto possível | costuma virar segredo eterno esquecido em variável de ambiente |

**Tolerância de relógio:** 60 s é o padrão sensato. Zero é defensável se você mede a
deriva NTP. Acima de 300 s você está, na prática, estendendo a vida do token.

---

## J · O que está obsoleto

| Obsoleto | Substituto | Desde / por quê |
|---|---|---|
| `alg: none` em código de produção | qualquer algoritmo real | sempre foi má ideia; existe na RFC só para JWT dentro de JWE |
| `dgrijalva/jwt-go` (Go) | `golang-jwt/jwt/v5` | projeto abandonado em 2021, com CVE |
| `io.jsonwebtoken:jjwt` monolítico (Java) | `jjwt-api` + `jjwt-impl` + `jjwt-jackson` | separação api/impl |
| `jsonwebtoken` (npm) para projeto novo | `jose` | cripto síncrona, sem ESM, sem JWE/JWKS |
| `node-jose` | `jose` | não mantida ativamente |
| Guardar refresh token em `localStorage` | cookie `HttpOnly` + `SameSite` | XSS lê `localStorage`; ver [18](18-onde-guardar-no-cliente.md) |
| Fluxo *implicit* do OAuth 2.0 (token na URL) | *authorization code* + PKCE | proibido pela RFC 9700 (jan/2025) |
| `RS256` com chave de 1024 bits | ≥ 2048, ou ES256 | quebrável |
| JWT como identificador de sessão de site tradicional | cookie de sessão comum | ver [21](21-quando-nao-usar.md) |

---

## K · Atalhos que só quem usa há anos conhece

**1. `typ` como firewall entre tipos de token.** `at+jwt` para access, `dpop+jwt`
para prova DPoP, `secevent+jwt` para eventos de segurança. Verificar `typ` impede a
classe inteira de ataques de "token de um tipo aceito como outro" — inclusive o
clássico de mandar um `id_token` onde se espera um access token.

**2. `aud` como array serve para migração.** Ao renomear um serviço, emita com
`"aud": ["nome-antigo", "nome-novo"]` durante a transição. Ninguém quebra.

**3. `kid` com *thumbprint* RFC 7638, não com data.** `kid: "2026-08"` obriga
coordenação humana. O thumbprint é derivado da própria chave: duas partes que nunca
se falaram chegam ao mesmo `kid`. O projeto-modelo faz assim, e o teste reproduz o
vetor oficial da RFC.

**4. Sempre publique JWKS, mesmo com uma chave só.** Custa 20 linhas hoje e é a
diferença entre rotacionar chave numa tarde e rotacionar chave num projeto de
trimestre.

**5. `nbf` para agendamento.** Token emitido agora, válido só a partir de meia-noite:
útil para virada de contrato, liberação de recurso, janela de manutenção.

**6. `iat` + `maxTokenAge` para exigir reautenticação.** Um token pode estar dentro
da validade e ainda assim ser velho demais para uma operação sensível (transferir
dinheiro). Combine com `auth_time` do OIDC.

**7. Faça o log do `jti`, nunca do token.** O `jti` permite rastrear a requisição até
a sessão sem que o log vire um repositório de credenciais vivas.

**8. Comprima a lista de permissões.** `"p":"rwx"` em vez de
`"permissions":["read","write","execute"]`. Parece exagero — não é, quando o token
vai em toda requisição de uma SPA que faz 200 chamadas por tela.

**9. Cheque o tamanho do token no CI.** Um teste que falha se o token passar de
~1,5 KB evita a descoberta em produção de que o cabeçalho estourou o limite do nginx
(padrão: 8 KB no total dos cabeçalhos).

**10. Guarde os tokens de teste num arquivo, não no histórico do shell.** Tokens em
`~/.bash_history` são credenciais em texto puro num arquivo que o backup copia.

---

## Autoteste

1. Quais três claims você deve tratar como obrigatórias, mesmo a RFC dizendo que
   todas são opcionais?
2. `exp` está em segundos ou milissegundos? Qual comando converte para data legível?
3. Qual pergunta única decide entre HS256 e ES256?
4. Por que `createRemoteJWKSet` deve ser criado uma vez por processo, e não dentro do
   handler da requisição?
5. Quando responder 401 e quando responder 403? O que um cliente bem-feito faz
   diferente em cada caso?
6. Sua chave privada começa com `-----BEGIN RSA PRIVATE KEY-----` e a biblioteca
   recusa. O que é isso e qual o comando de conversão?
7. Cite três coisas obsoletas neste ecossistema e o que as substituiu.
8. Para que serve `typ: "at+jwt"`, e que ataque ele bloqueia?
