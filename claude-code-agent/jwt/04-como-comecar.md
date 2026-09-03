# 4 · Como começar — do ambiente pronto ao primeiro token

> Nível: iniciante · Comandos executados e verificados em 14/08/2026
> (Ubuntu 22.04.5, Node v24.18.0, OpenSSL 3.0.2)

Assume o ambiente do [03-instalacao.md](03-instalacao.md) pronto. Se
`node --version` e `openssl version` respondem, você está pronto.

Em 20 minutos você vai: **fabricar um JWT à mão no terminal**, quebrá-lo de
propósito, e depois subir uma API protegida de verdade.

---

## Passo 1 · Fabricar um JWT com o terminal, sem biblioteca nenhuma

Esta é a demonstração que faz a ficha cair. Um JWT não é mágica — são três textos
colados com ponto.

Abra um terminal e defina um atalho para codificar em base64url:

```bash
b64() { openssl base64 -A | tr '+/' '-_' | tr -d '='; }
```
> Codifica a entrada em base64, troca os caracteres proibidos em URL (`+` → `-`,
> `/` → `_`) e remove o preenchimento `=`. Isso é *exatamente* o que a especificação
> chama de base64url.

### 1.1 · O cabeçalho

```bash
H=$(printf '%s' '{"alg":"HS256","typ":"JWT"}' | b64)
echo "$H"
# esperado: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9
```

Ele diz duas coisas: o algoritmo de assinatura (`HS256`) e que isto é um JWT.

### 1.2 · O payload

```bash
P=$(printf '%s' '{"sub":"42","nome":"Ana","exp":2000000000}' | b64)
echo "$P"
# esperado: eyJzdWIiOiI0MiIsIm5vbWUiOiJBbmEiLCJleHAiOjIwMDAwMDAwMDB9
```

`sub` é quem é o sujeito do token, `exp` é quando ele morre (em segundos desde
01/01/1970 — `2000000000` cai em maio de 2033).

### 1.3 · A assinatura

```bash
SEG="segredo-de-teste-com-32-bytes-ok"
S=$(printf '%s' "$H.$P" | openssl dgst -sha256 -hmac "$SEG" -binary | b64)
echo "$S"
# esperado: 3BwXkLHns1aVhHlVVRZWgQ682fmT5R5EiMgrspR4GoE
```
> Calcula o HMAC-SHA256 dos **dois primeiros segmentos já codificados, com o ponto no
> meio**, usando o segredo. Repare que a entrada da assinatura é o texto
> `cabeçalho.payload`, não o JSON original — esse detalhe importa e é explicado em
> [12-anatomia-do-token.md](12-anatomia-do-token.md).

### 1.4 · O token

```bash
TOKEN="$H.$P.$S"
echo "$TOKEN"
# esperado:
# eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0MiIsIm5vbWUiOiJBbmEiLCJleHAiOjIwMDAwMDAwMDB9.3BwXkLHns1aVhHlVVRZWgQ682fmT5R5EiMgrspR4GoE
```

**Você acabou de emitir um JWT válido**, com `openssl` e `printf`. Confira em
<https://jwt.io> — cole o token e o segredo `segredo-de-teste-com-32-bytes-ok`, e o
site vai dizer *Signature Verified*.

### 1.5 · Verificação: como saber que deu certo

```bash
node -e '
const c = require("crypto");
const [h, p, s] = process.argv[1].split(".");
const esperada = c.createHmac("sha256", "segredo-de-teste-com-32-bytes-ok")
                  .update(h + "." + p).digest("base64url");
console.log("assinatura confere:", esperada === s);
console.log("payload:", Buffer.from(p, "base64url").toString());
' "$TOKEN"
```

```
# esperado:
# assinatura confere: true
# payload: {"sub":"42","nome":"Ana","exp":2000000000}
```

---

## Passo 2 · Quebrar o token de propósito

Agora o experimento que ensina mais que o anterior. Vamos tentar virar admin.

```bash
FALSO=$(printf '%s' '{"sub":"42","nome":"Ana","papel":"admin","exp":2000000000}' | b64)
TOKEN_FALSO="$H.$FALSO.$S"

node -e '
const c = require("crypto");
const [h, p, s] = process.argv[1].split(".");
const esperada = c.createHmac("sha256", "segredo-de-teste-com-32-bytes-ok")
                  .update(h + "." + p).digest("base64url");
console.log("assinatura confere:", esperada === s);
console.log("payload lido:", Buffer.from(p, "base64url").toString());
' "$TOKEN_FALSO"
```

```
# esperado:
# assinatura confere: false
# payload lido: {"sub":"42","nome":"Ana","papel":"admin","exp":2000000000}
```

Duas lições numa tela só:

1. **A adulteração foi detectada.** Sem o segredo, não há como recalcular a
   assinatura. É isso que o JWT garante.
2. **O payload adulterado foi lido normalmente.** O conteúdo nunca esteve escondido —
   ele só estava *lacrado*. Quem recebe precisa **verificar antes de usar**; um
   código que faz `JSON.parse(atob(...))` e confia no resultado não tem proteção
   nenhuma.

---

## Passo 3 · O ciclo de trabalho do dia a dia

Suba a API de verdade — o projeto-modelo, que roda sem instalar nada:

```bash
cd 07-projeto-modelo
node --test
# esperado: ... pass 54   fail 0
```

```bash
node src/servidor.js
# esperado:
# cofre-de-notas ouvindo em http://localhost:3000
#   emissor:   http://localhost:3000
#   audiencia: cofre-de-notas-api
#   kid ativa: E54wgNtjf8S0GLiPk_sVbt3epcuwkqG0EHSICTA2WNU
#   JWKS:      http://localhost:3000/.well-known/jwks.json
```

Em **outro terminal**:

```bash
# 1. registrar
curl -s -X POST localhost:3000/auth/registrar \
  -H 'content-type: application/json' \
  -d '{"email":"ana@exemplo.com","senha":"uma-senha-longa-2026"}'
# esperado: {"id":"...","email":"ana@exemplo.com","papeis":["usuario"]}
```

```bash
# 2. login — guarda a resposta
curl -s -X POST localhost:3000/auth/login \
  -H 'content-type: application/json' \
  -d '{"email":"ana@exemplo.com","senha":"uma-senha-longa-2026"}' > /tmp/sessao.json
cat /tmp/sessao.json
# esperado: {"token_type":"Bearer","access_token":"eyJ...","expires_in":900,"refresh_token":"..."}
```

```bash
AT=$(node -e "console.log(require('/tmp/sessao.json').access_token)")
RT=$(node -e "console.log(require('/tmp/sessao.json').refresh_token)")
```

```bash
# 3. rota protegida SEM token
curl -si localhost:3000/notas | head -4
# esperado:
# HTTP/1.1 401 Unauthorized
# ...
# www-authenticate: Bearer error="invalid_token", ...
```

```bash
# 4. rota protegida COM token
curl -s -X POST localhost:3000/notas \
  -H "authorization: Bearer $AT" -H 'content-type: application/json' \
  -d '{"texto":"comprar pao"}'
# esperado: {"id":"...","texto":"comprar pao","criadaEm":"2026-..."}
```

```bash
# 5. ver o que está dentro do SEU token
echo "$AT" | cut -d. -f2 | tr '_-' '/+' | base64 -d 2>/dev/null | jq .
# esperado:
# {
#   "iat": 1786726076,
#   "iss": "http://localhost:3000",
#   "sub": "27cbec8a-...",
#   "aud": "cofre-de-notas-api",
#   "exp": 1786726976,
#   "jti": "1852bd58-...",
#   "papeis": ["usuario"]
# }
```

Esse é o ciclo: **editar → rodar → chamar com `curl` → ler o token → repetir.**
Deixe os dois terminais abertos lado a lado. `Ctrl+C` e `node src/servidor.js` de
novo é o "recarregar" — a chave persiste em `dados/chaveiro.json`, então os tokens
emitidos antes continuam valendo depois do reinício.

> Quer recarregamento automático? `node --watch src/servidor.js`. Nativo, sem
> instalar nodemon.

---

## Passo 4 · Ver a rotação e a revogação funcionando

```bash
# renovar: devolve access novo E refresh novo (o antigo morre agora)
curl -s -X POST localhost:3000/auth/refresh \
  -H 'content-type: application/json' -d "{\"refresh_token\":\"$RT\"}" | jq .

# usar o refresh ANTIGO de novo → detecção de reuso
curl -s -X POST localhost:3000/auth/refresh \
  -H 'content-type: application/json' -d "{\"refresh_token\":\"$RT\"}"
# esperado: {"erro":"reuso_detectado","mensagem":"refresh token reutilizado; ..."}
```

```bash
# logout → o access token morre NA HORA
curl -s -X POST localhost:3000/auth/logout -H "authorization: Bearer $AT"
# esperado: {"ok":true,"accessRevogado":true,...}

curl -s localhost:3000/notas -H "authorization: Bearer $AT"
# esperado: {"erro":"token_revogado","mensagem":"este token foi revogado"}
```

Se alguém te disser que "com JWT não dá para deslogar", você acabou de ver o
contrário na sua tela. O que existe é um **custo**, e ele está explicado em
[17-ciclo-de-vida-sessao.md](17-ciclo-de-vida-sessao.md).

---

## Os primeiros cinco erros de uso (não de instalação)

Todo mundo comete os cinco. Reconheça-os agora e economize um dia.

### 1. Esquecer a palavra `Bearer`

```bash
curl -s localhost:3000/notas -H "authorization: $AT"        # ❌ 401
curl -s localhost:3000/notas -H "authorization: Bearer $AT" # ✅
```

O cabeçalho `Authorization` carrega um *esquema* seguido do valor. Sem
`Bearer `, o servidor não sabe o que fazer com aquilo. Sintoma: 401 num token que
você jura estar certo.

### 2. Confundir segundos com milissegundos no `exp`

```js
exp: Date.now() + 900          // ❌ ERRADO — Date.now() dá MILISSEGUNDOS
exp: Math.floor(Date.now()/1000) + 900   // ✅ segundos
```

O `exp` é definido como *NumericDate*: **segundos** desde 01/01/1970. Usar
milissegundos gera um token que expira no ano **58.000**. Ele funciona lindamente nos
seus testes e é uma falha de segurança grave em produção — um token roubado vale para
sempre. Este é, na minha experiência, o bug mais comum e mais perigoso de quem começa.

Verificação rápida de qualquer token:

```bash
node -e 'console.log(new Date(2000000000*1000).toISOString())'
# esperado: 2033-05-18T03:33:20.000Z   — se der ano 58000, você usou milissegundos
```

### 3. Decodificar em vez de verificar

```js
const dados = JSON.parse(atob(token.split('.')[1]));   // ❌ NÃO valida nada
if (dados.papel === 'admin') { /* qualquer um vira admin */ }
```

Decodificar é ler; verificar é conferir a assinatura. No navegador, decodificar é
legítimo (para mostrar o nome do usuário na tela); **no servidor, decodificar sem
verificar é uma porta aberta**. Repare no nome deliberadamente longo da função no
projeto-modelo: `decodificarSemVerificar`. Se doer ler, está funcionando.

### 4. Não passar a lista de algoritmos ao verificar

```js
jwt.verify(token, chave)                          // ❌ perigoso em várias bibliotecas
jwt.verify(token, chave, { algorithms: ['ES256'] }) // ✅
```

Sem a lista, algumas bibliotecas leem o `alg` do próprio token para decidir como
verificá-lo — e quem manda o token controla esse campo. É a **confusão de
algoritmo**, e ela derrubou bibliotecas reais em 2026 (CVE-2026-34950,
CVE-2026-48526). Detalhes em [20-ataques-e-defesas.md](20-ataques-e-defesas.md).

### 5. Não conferir `iss` e `aud`

Um token perfeitamente válido, assinado pela chave certa, **emitido para outro
serviço**, passa na sua verificação se você só checa a assinatura. Em arquitetura de
microsserviços isso vira escalada de privilégio: o token do serviço de relatórios
(que só lê) é aceito pelo serviço de pagamentos.

```js
jwtVerify(token, chave, { issuer: 'https://auth.exemplo.com', audience: 'api-pagamentos' })
```

No projeto-modelo, `verificar()` **se recusa a rodar** sem `emissor` e `audiencia`.
Foi decisão de projeto: se é fácil esquecer, torne impossível.

---

## Onde ir depois

| Você quer… | Vá para |
|---|---|
| dez receitas prontas, em cinco linguagens | [06-exemplos.md](06-exemplos.md) |
| a referência de comandos e claims | [05-manual-de-uso.md](05-manual-de-uso.md) |
| ler o código do projeto que você acabou de rodar | [07-projeto-modelo/README.md](07-projeto-modelo/README.md) |
| entender de verdade o que aconteceu | [10-fundamentos.md](10-fundamentos.md) |
| saber onde guardar o token no navegador | [18-onde-guardar-no-cliente.md](18-onde-guardar-no-cliente.md) |

---

## Autoteste

1. Fabrique um JWT no terminal com `exp` daqui a 60 segundos. Que comando você usa
   para calcular esse valor?
2. Você alterou o payload de um token e a assinatura passou a não conferir. Mesmo
   assim, o servidor conseguiu **ler** o payload alterado. Por quê, e o que isso
   ensina?
3. Qual é a entrada exata do cálculo do HMAC: o JSON do payload, ou outra coisa?
4. Um colega escreve `exp: Date.now() + 3600`. Qual é o bug, e por que ele passa
   despercebido em todos os testes?
5. Qual a diferença entre *decodificar* e *verificar* um token? Em que situação
   decodificar sem verificar é aceitável?
6. Por que passar a lista de algoritmos na verificação é obrigatório, e não um
   detalhe de estilo?
7. Dois microsserviços usam a mesma chave de assinatura. O que impede o token de um
   ser aceito pelo outro?
