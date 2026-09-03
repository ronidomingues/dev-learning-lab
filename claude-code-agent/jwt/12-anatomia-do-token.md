# 12 · Anatomia do token — byte a byte

> Nível: intermediário · Medições executadas em 14/08/2026 (Node v24.18.0)
> Sem caixa-preta: aqui desmontamos um token real e remontamos à mão.

---

## 12.1 · O token que vamos dissecar

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0MiIsIm5vbWUiOiJBbmEiLCJleHAiOjIwMDAwMDAwMDB9.3BwXkLHns1aVhHlVVRZWgQ682fmT5R5EiMgrspR4GoE
```

**137 bytes**, três segmentos separados por `.` (`U+002E`, ponto final ASCII).

| # | Segmento | Caracteres | Bytes após decodificar |
|---|---|---|---|
| 1 | cabeçalho | 36 | 27 |
| 2 | payload | 56 | 42 |
| 3 | assinatura | 43 | 32 |

Repare na proporção: 27 bytes de JSON viram 36 caracteres. Base64 codifica 3 bytes em
4 caracteres — **33% de inchaço**, e o token paga isso em toda requisição HTTP.

---

## 12.2 · Base64url: por que este alfabeto

Base64 comum (RFC 4648 §4) usa 64 caracteres: `A–Z`, `a–z`, `0–9`, `+`, `/`, mais `=`
como preenchimento. Três dos 65 são um problema:

| Caractere | Onde quebra | Por quê |
|---|---|---|
| `+` | em URL | numa *query string*, `+` significa espaço |
| `/` | em URL | separador de caminho |
| `=` | em cookie, em URL | separador de par nome=valor |

**Base64url** (RFC 4648 §5) troca `+` → `-`, `/` → `_`, e remove o `=` final. O
resultado atravessa URL, cabeçalho HTTP, cookie e nome de arquivo sem escape.

```bash
# a conversão, à mão
printf '%s' '{"alg":"HS256","typ":"JWT"}' | openssl base64 -A
# esperado: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9   (aqui não houve + / =)

# forçando um caso que mostra a diferença
printf '\xfb\xff\xfe' | openssl base64 -A
# esperado: +//+
printf '\xfb\xff\xfe' | openssl base64 -A | tr '+/' '-_' | tr -d '='
# esperado: -__-
```

**Por que remover o `=`?** O preenchimento existe para que o decodificador saiba
quantos bytes sobraram. Mas o comprimento da string já diz isso: resto 2 → falta 1
byte; resto 3 → faltam 2 bytes; resto 1 → **inválido**. O `=` é redundante, e a RFC
7515 §2 exige que ele seja omitido.

Consequência prática: um decodificador que exige preenchimento (várias bibliotecas
Python antigas) quebra em tokens legítimos. A correção é acrescentar `=` até o
comprimento virar múltiplo de 4.

```python
def de_base64url(s: str) -> bytes:
    import base64
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))
```

> **Não é criptografia.** Base64 é codificação, reversível por qualquer pessoa, sem
> chave. Alguém dizer "os dados estão em base64, então estão protegidos" é o mesmo
> que dizer que escrever de trás para frente protege um bilhete.

---

## 12.3 · Segmento 1 — o cabeçalho JOSE

```bash
echo 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9' | tr '_-' '/+' | base64 -d
# esperado: {"alg":"HS256","typ":"JWT"}
```

27 bytes de JSON. É chamado de **cabeçalho protegido** (*protected header*) porque
está coberto pela assinatura — alterar qualquer byte dele invalida o token.

Os parâmetros e o que fazer com cada um:

| Parâmetro | Confiança que você pode depositar |
|---|---|
| `alg` | **nenhuma para decidir** — só para conferir contra a sua lista |
| `typ` | nenhuma isolada — mas **verifique** que é o tipo que você espera |
| `kid` | é um **rótulo**, não um endereço. Use como chave de um mapa local |
| `crit` | se você não implementa o que está listado, **recuse o token** |
| `jwk`, `jku`, `x5u`, `x5c` | **desconfiança total** — é o remetente dizendo qual chave o valida |

A regra unificadora: **o cabeçalho é escrito por quem manda o token.** Trate-o como
entrada hostil, exatamente como você trata o corpo de um POST.

---

## 12.4 · Segmento 2 — o payload

```bash
echo 'eyJzdWIiOiI0MiIsIm5vbWUiOiJBbmEiLCJleHAiOjIwMDAwMDAwMDB9' | tr '_-' '/+' | base64 -d
# esperado: {"sub":"42","nome":"Ana","exp":2000000000}
```

**Num JWT**, o payload é obrigatoriamente um objeto JSON (não array, não número, não
`null`) codificado em UTF-8. Num JWS genérico poderia ser qualquer sequência de
bytes — inclusive uma imagem.

Três consequências que mordem:

**1. Não há esquema.** A RFC não define tipos além das sete claims registradas.
`"exp": "2000000000"` (string!) é JSON válido e vai ser recusado por bibliotecas
sérias e aceito por outras. Valide tipos.

**2. Chaves duplicadas são indefinidas.** `{"sub":"ana","sub":"admin"}` é JSON
tecnicamente válido, e cada analisador escolhe uma. Se um serviço lê a primeira e
outro lê a segunda, você tem um ataque. Bibliotecas modernas recusam; nem todas.

**3. Números grandes perdem precisão em JavaScript.** `JSON.parse` transforma tudo
em `double`. Um `sub` numérico maior que 2^53 vira outro número. Use string para
identificadores, sempre.

```js
JSON.parse('{"sub": 9007199254740993}').sub
// 9007199254740992  ← mudou de valor silenciosamente
```

---

## 12.5 · Segmento 3 — a assinatura

```bash
echo '3BwXkLHns1aVhHlVVRZWgQ682fmT5R5EiMgrspR4GoE' | tr '_-' '/+' | base64 -d | xxd
# esperado (32 bytes):
# 00000000: dc1c 1790 b1e7 b356 9584 7955 5516 5681
# 00000010: 0ebc d9f9 93e5 1e44 88c8 2bb2 9478 1a81
```

**Não é texto.** São 32 bytes binários — a saída do HMAC-SHA256 — apenas
transportados em base64url.

Tamanhos por algoritmo, **medidos**:

| `alg` | Assinatura (bytes) | No token (caracteres) |
|---|---|---|
| HS256 | 32 | 43 |
| ES256 | 64 | 86 |
| EdDSA (Ed25519) | 64 | 86 |
| RS256 (chave 2048) | **256** | **342** |

Um token RS256 carrega **300 caracteres a mais** que o mesmo token em ES256. Numa
SPA que faz 200 requisições por tela, isso é 60 KB de tráfego extra por tela, por
usuário. É o argumento mais concreto a favor do ES256.

---

## 12.6 · A entrada da assinatura — o detalhe que confunde todo mundo

A RFC 7515 chama de *JWS Signing Input*:

```
ASCII( BASE64URL(cabeçalho) || '.' || BASE64URL(payload) )
```

**Não é o JSON. É o texto já codificado, com o ponto no meio.**

```bash
# reconstruindo a assinatura do nosso token
H='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9'
P='eyJzdWIiOiI0MiIsIm5vbWUiOiJBbmEiLCJleHAiOjIwMDAwMDAwMDB9'
printf '%s' "$H.$P" | openssl dgst -sha256 -hmac "segredo-de-teste-com-32-bytes-ok" -binary \
  | openssl base64 -A | tr '+/' '-_' | tr -d '='
# esperado: 3BwXkLHns1aVhHlVVRZWgQ682fmT5R5EiMgrspR4GoE
```

Bate com o terceiro segmento. Você acabou de verificar um JWT com dois comandos de
shell.

**Por que assim?** Ver os [cinco porquês em 10-fundamentos](10-fundamentos.md#1011--os-cinco-porquês-por-que-a-assinatura-cobre-o-texto-base64-e-não-o-json).
Em uma frase: assinar o que trafega elimina a canonicalização, e com ela a família de
ataques em que *o que foi verificado não é o que foi usado*.

**A consequência prática que quase ninguém percebe:** dois tokens com o **mesmo
significado** e assinaturas diferentes podem coexistir. Se o emissor A serializa
`{"a":1,"b":2}` e o emissor B serializa `{"b":2,"a":1}`, são tokens diferentes, com
assinaturas diferentes, ambos válidos. Não há forma canônica de um JWT. Isso importa
quando você tenta usar o token como chave de cache ou de deduplicação — **use o `jti`,
nunca o token inteiro**.

---

## 12.7 · Montando um token do zero, à mão

Recapitulando o [04-como-comecar.md](04-como-comecar.md), agora com o porquê de cada
passo:

```bash
b64() { openssl base64 -A | tr '+/' '-_' | tr -d '='; }

# 1. cabeçalho: o mínimo é `alg`; `typ` é boa prática
H=$(printf '%s' '{"alg":"HS256","typ":"JWT"}' | b64)

# 2. payload: claims. exp em SEGUNDOS.
P=$(printf '%s' "{\"sub\":\"42\",\"iat\":$(date +%s),\"exp\":$(($(date +%s)+900))}" | b64)

# 3. assinatura sobre "H.P", não sobre o JSON
S=$(printf '%s' "$H.$P" | openssl dgst -sha256 -hmac "segredo-de-teste-com-32-bytes-ok" -binary | b64)

echo "$H.$P.$S"
```

Note o `printf '%s'` em vez de `echo`: o `echo` acrescenta `\n`, e esse byte extra
entra no JSON e no cálculo do HMAC, produzindo um token que não valida em lugar
nenhum. Esse é o erro nº 1 de quem monta JWT em shell.

---

## 12.8 · A ordem de validação correta

A ordem não é estética — é segurança. Cada passo pressupõe o anterior.

```mermaid
flowchart TD
    A["token recebido"] --> B{"tem exatamente<br/>3 segmentos?"}
    B -->|não| X["recusa: malformado"]
    B --> C["decodifica o cabeçalho"]
    C --> D{"alg está na MINHA<br/>lista de aceitos?"}
    D -->|não| X2["recusa: alg não permitido"]
    D --> E{"typ é o esperado?"}
    E -->|não| X3["recusa: tipo errado"]
    E --> F["resolve a chave pelo kid<br/>(mapa LOCAL)"]
    F -->|kid desconhecido| X4["recusa: chave desconhecida"]
    F --> G{"assinatura confere?"}
    G -->|não| X5["recusa: assinatura inválida<br/>⚠️ ALERTA"]
    G --> H["SÓ AGORA decodifica<br/>o payload"]
    H --> I{"iss, aud conferem?"}
    I -->|não| X6["recusa: token de outro lugar"]
    I --> J{"exp e nbf ok<br/>(com tolerância)?"}
    J -->|não| X7["recusa: expirado / futuro"]
    J --> K{"jti está na<br/>lista de negação?"}
    K -->|sim| X8["recusa: revogado"]
    K --> L["aceita — use as claims"]
```

**A regra de ouro:** nada do payload é usado antes de a assinatura conferir. Ler o
`sub` para consultar o banco *antes* de verificar já é uma falha — você acabou de
executar uma consulta com dado controlado pelo atacante.

A única exceção legítima é ler o **`kid` do cabeçalho** antes de verificar, porque é
preciso para escolher a chave. Por isso o `kid` só pode ser usado como índice num
conjunto local que você já conhece; se ele virar caminho de arquivo ou URL, você
transformou a exceção numa porta.

---

## 12.9 · Anatomia comparada: JWS vs. JWE

```
JWS compacto (3 segmentos, 2 pontos)
  cabeçalho . payload . assinatura
  eyJhbGci...  .  eyJzdWIi...  .  3BwXkLH...
                 └─ LEGÍVEL POR QUALQUER UM ─┘

JWE compacto (5 segmentos, 4 pontos)
  cabeçalho . chave cifrada . IV . texto cifrado . tag
  eyJhbGci...  .  QR3F9x...  .  48V_...  .  9s2Kd...  .  XxA1...
                                          └─ ilegível ─┘
```

Conte os pontos:

```bash
echo "$TOKEN" | tr -cd '.' | wc -c
# 2 → JWS (assinado, legível)
# 4 → JWE (cifrado)
```

Ver [15-criptografia-jwe.md](15-criptografia-jwe.md).

---

## 12.10 · Tamanho: por que importa mais do que parece

O token vai em **toda** requisição, no cabeçalho `Authorization`.

| Conteúdo | Tamanho típico |
|---|---|
| mínimo útil (`iss`, `sub`, `aud`, `exp`, `iat`, ES256) | ~250 B |
| com `jti` e 3 papéis | ~400 B |
| com 20 permissões detalhadas | ~1,2 KB |
| `id_token` do Azure AD/Entra com grupos | **2 a 8 KB** |

Limites que você vai encontrar:

| Onde | Limite padrão | O que acontece ao estourar |
|---|---|---|
| nginx | 8 KB no total dos cabeçalhos | **400 Bad Request**, sem explicação |
| Apache | 8 KB por cabeçalho | 400 |
| AWS ALB | 16 KB no total | 400 |
| API Gateway (AWS) | 10 KB | 400 |
| Cookie (por navegador) | ~4 KB | o cookie é **silenciosamente descartado** |
| URL | ~2 KB no IE/Edge antigo | truncamento |

O caso do cookie é o mais cruel: nada falha, nada aparece no log, o cookie
simplesmente não é gravado, e a pessoa "não consegue logar" — só em algumas contas,
as que têm muitos grupos.

**Regra prática:** ponha um teste no CI que falha se o token passar de ~1,5 KB. Você
descobre no *pull request*, não em produção às 3 da manhã.

**Como encolher:**

| Técnica | Ganho | Custo |
|---|---|---|
| Trocar RS256 por ES256 | −300 B | precisa que todos os consumidores suportem ES256 |
| Nomes de claim curtos (`p` em vez de `permissions`) | 10–30% | legibilidade |
| Papéis em vez de permissões (`admin` em vez de 40 permissões) | grande | o recurso precisa saber o que "admin" significa |
| Bitmask de permissões (`"p": 1023`) | grande | acopla os números ao código |
| Tirar do token o que o recurso já sabe (nome, e-mail, avatar) | grande | uma consulta ao perfil quando for exibir |
| Referência em vez de valor para o excesso | grande | volta a ter consulta — ver [21](21-quando-nao-usar.md) |

---

## 12.11 · Autópsia de um token real

Um `id_token` do Google, com os valores substituídos:

```json
// cabeçalho
{
  "alg": "RS256",
  "kid": "c9afda3682ebf09eb3055c1c4bd39b751fbf8195",
  "typ": "JWT"
}
```
```json
// payload
{
  "iss": "https://accounts.google.com",
  "azp": "1234-abc.apps.googleusercontent.com",
  "aud": "1234-abc.apps.googleusercontent.com",
  "sub": "110169484474386276334",
  "email": "pessoa@exemplo.com",
  "email_verified": true,
  "at_hash": "HK6E_P6Dh8Y93mRNtsDB1Q",
  "name": "Pessoa Exemplo",
  "picture": "https://lh3.googleusercontent.com/a/...",
  "given_name": "Pessoa",
  "family_name": "Exemplo",
  "locale": "pt-BR",
  "iat": 1786726076,
  "exp": 1786729676,
  "nonce": "n-0S6_WzA2Mj"
}
```

Sete observações de quem já leu muitos desses:

1. **`RS256`, não ES256.** Google, Microsoft e Auth0 usam RS256 por
   interoperabilidade máxima — bibliotecas antigas e SDKs corporativos suportam RSA
   antes de qualquer outra coisa. O preço são os 342 caracteres de assinatura.
2. **`sub` é um número em string, e é opaco.** Não é o e-mail. Use-o como chave
   primária do usuário no seu banco: o e-mail muda, o `sub` não.
3. **`azp` ≠ `aud`.** Aqui coincidem, mas `azp` é a *parte autorizada* (quem obteve
   o token) e `aud` é a audiência. Em cenário multi-cliente, divergem.
4. **`email_verified`.** Sem ele, o `email` não prova nada. Aceitar um e-mail não
   verificado para casar contas é o vetor clássico de tomada de conta.
5. **`nonce`** é o valor anti-repetição que **você** enviou no início do fluxo. Se
   não conferir que voltou igual, o fluxo OIDC está quebrado.
6. **`at_hash`** amarra este `id_token` ao access token que veio junto — impede
   trocar um pelo outro.
7. **Uma hora de validade** (`exp - iat = 3600`). Longo para um token que é consumido
   uma vez, no login. Consuma e descarte; não use `id_token` como credencial de API.

---

## Autoteste

1. Quantos bytes tem a assinatura de um token ES256? E RS256? Qual a diferença no
   tamanho final do token?
2. Por que o `=` de preenchimento é removido, e qual bug isso causa em
   decodificadores descuidados?
3. Qual é exatamente a entrada do cálculo da assinatura? Escreva a fórmula.
4. Por que `echo` em vez de `printf '%s'` estraga um JWT montado em shell?
5. Dois tokens com as mesmas claims podem ter assinaturas diferentes e ambos serem
   válidos. Por quê, e que consequência prática isso tem?
6. Na ordem de validação, qual é a única informação que pode ser lida antes de
   verificar a assinatura, e por quê ela não é um furo?
7. Como distinguir um JWS de um JWE olhando o token em um segundo?
8. Um usuário com muitos grupos no Entra ID "não consegue logar", sem erro nenhum no
   log. Qual é a hipótese mais provável?
9. No `id_token` do Google, por que `email_verified` importa tanto?
