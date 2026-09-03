# 13 · Claims — semântica exata de cada uma

> Nível: intermediário · Atualizado em 14/08/2026
> Referência: RFC 7519 §4, RFC 9068, OpenID Connect Core 1.0

O arquivo [05-manual-de-uso.md](05-manual-de-uso.md) tem a tabela para consulta
rápida. Aqui está o que cada claim **significa de verdade**, o que ela não garante, e
os erros que cada uma produz.

---

## 13.1 · A observação incômoda: todas são opcionais

A RFC 7519 §4.1 diz, sobre cada uma das sete claims registradas: *"Use of this claim
is OPTIONAL."* Sete vezes.

Isso significa que **o JSON `{}` é um JWT perfeitamente válido**. Sem emissor, sem
prazo, sem sujeito.

```bash
b64() { openssl base64 -A | tr '+/' '-_' | tr -d '='; }
H=$(printf '%s' '{"alg":"HS256"}' | b64)
P=$(printf '%s' '{}' | b64)
S=$(printf '%s' "$H.$P" | openssl dgst -sha256 -hmac "segredo-de-teste-com-32-bytes-ok" -binary | b64)
echo "$H.$P.$S"
# esperado: eyJhbGciOiJIUzI1NiJ9.e30.xxxx — um JWT válido pela RFC, e inútil
```

Por que a RFC fez isso? Porque o JWT foi projetado como **formato de transporte
genérico**, não como credencial de sessão. As claims de tempo e de origem fazem
sentido em quase todo uso real, mas não em todos — daí a especificação empurrar a
decisão para o perfil de uso.

A consequência é que a segurança do JWT depende de o **verificador** exigir o que a
especificação não exige. Esse é o assunto do RFC 8725 (*JWT Best Current Practices*)
e a razão de o [projeto-modelo](07-projeto-modelo/) recusar-se a rodar sem `iss`,
`aud` e `exp`.

**Regra deste material:** trate `iss`, `aud` e `exp` como obrigatórias. Sempre.

---

## 13.2 · `iss` — quem emitiu

**Tipo:** *StringOrURI*. **Emita sempre. Verifique sempre.**

```json
"iss": "https://auth.exemplo.com"
```

**O que significa:** o principal que emitiu e assinou este token.

**O que garante:** nada por si. `iss` é uma **string dentro do payload assinado** —
ela só tem valor porque a assinatura confere. Um atacante pode escrever qualquer
`iss` no token dele; o que ele não consegue é assiná-lo com a sua chave.

A relação correta é esta:

> A assinatura prova *que chave assinou*. O `iss` diz *quem afirma ser*. Verificar os
> dois juntos é o que amarra "esta chave pertence a este emissor".

**O erro que ele evita:** você aceita tokens de dois provedores (Google e um Keycloak
interno) e busca a chave pelo `kid`. Sem checar `iss`, um token do Google com `sub`
igual a um ID interno seu pode ser aceito como se fosse do Keycloak. Com `iss`
conferido, cada emissor tem seu conjunto de chaves e seu espaço de nomes.

**Cuidado com a barra final.** `https://conta.auth0.com/` e
`https://conta.auth0.com` são strings diferentes, e comparação de `iss` é
**exata, byte a byte** — não é comparação de URL. A Auth0 emite com barra final; o
Keycloak, sem. Metade dos "não sei por que não valida" na integração inicial é isso.

```js
// ❌ frágil
if (payload.iss.startsWith('https://conta.auth0.com')) { }
// ✅ pegue o valor do documento de descoberta e compare exato
if (payload.iss !== metadados.issuer) throw new Error('emissor inválido');
```

---

## 13.3 · `sub` — de quem o token fala

**Tipo:** *StringOrURI*. Único **dentro do escopo do emissor**.

```json
"sub": "27cbec8a-10c9-4ef1-8353-a3f738447f14"
```

**Três regras que economizam uma migração dolorosa:**

**1. Use um identificador interno e opaco.** Nunca e-mail, nunca CPF, nunca nome de
usuário. E-mail muda (casamento, troca de empresa, correção de digitação), e quando
muda, todo dado ligado a ele órfã.

**2. `sub` só é único dentro do `iss`.** O par `(iss, sub)` é a chave primária real
da identidade. Dois provedores podem, legitimamente, usar `sub: "1"`. Se você guarda
só o `sub` numa tabela e amanhã acrescenta um segundo provedor, duas pessoas
diferentes colidem na mesma conta. Guarde os dois campos.

**3. `sub` nem sempre é uma pessoa.** Num token de serviço-a-serviço, `sub` é o
serviço. Num token de aplicação (*client credentials*), é o `client_id`. Código que
assume "sub = usuário" quebra no dia em que o primeiro robô chama a API.

**Não confunda com `preferred_username` nem `name`.** Esses são para exibir na tela e
**mudam**. Usá-los como chave é o mesmo erro do e-mail, com um agravante: o usuário
costuma poder alterá-los sozinho, o que abre a porta para se passar por outra pessoa.

---

## 13.4 · `aud` — para quem o token vale

**Tipo:** *StringOrURI* **ou array de StringOrURI**. **Emita sempre. Verifique sempre.**

```json
"aud": "api-pedidos"
"aud": ["api-pedidos", "api-relatorios"]
```

**A regra da RFC 7519 §4.1.3:** se você não se reconhece na lista, **recuse**.

**Por que é a claim mais negligenciada e uma das mais importantes.** Num sistema com
vários serviços que compartilham o mesmo emissor, sem `aud` verificado:

```
Pessoa faz login → recebe token
       ↓
Envia esse token ao serviço de relatórios (que ela pode usar)
       ↓
O serviço de relatórios pega o MESMO token e chama o serviço de pagamentos
       ↓
Pagamentos verifica: assinatura ok, emissor ok, exp ok → ACEITA
```

O serviço de relatórios acabou de agir no serviço de pagamentos com a identidade da
pessoa. Isso se chama **ataque do servidor confuso** (*confused deputy*) e é
escalação de privilégio real. O `aud` é a defesa: o token diz explicitamente para
quem vale, e pagamentos recusa um token cuja audiência é "relatórios".

**A armadilha do array.** Verificar `aud` com igualdade quebra quando o valor é
array:

```js
// ❌ falha silenciosamente quando aud é array
if (payload.aud !== 'api-pedidos') recusar();

// ✅
const aud = payload.aud;
const ok = typeof aud === 'string' ? aud === 'api-pedidos'
                                   : Array.isArray(aud) && aud.includes('api-pedidos');
```

**Uso legítimo do array:** migração de nome. Emita
`"aud": ["nome-antigo", "nome-novo"]` durante a transição e ninguém quebra.

**Formato do valor.** Não há regra: alguns provedores usam um nome curto
(`api-pedidos`), outros uma URL (`https://api.exemplo.com`). A Auth0 usa a URL da
API; o Keycloak usa o `client_id`. Combine com quem emite e **fixe no código**.

---

## 13.5 · `exp` — quando morre

**Tipo:** NumericDate. **Emita sempre. Verifique sempre.**

```json
"exp": 1786726976
```

**Semântica exata (RFC 7519 §4.1.4):** o token **não deve** ser aceito *em ou depois*
do instante `exp`. A comparação é `agora >= exp` → recusa. No segundo exato de `exp`,
o token já morreu.

**Por que segundos e não milissegundos.** *NumericDate* é definido como o número de
segundos desde 1970-01-01T00:00:00Z. É o mesmo formato do `time_t` do POSIX, escolhido
porque já era o denominador comum de todas as linguagens em 2011.

**O bug mais perigoso do assunto:**

```js
exp: Date.now() + 900_000        // ❌ milissegundos
```

`Date.now()` devolve ~1.786.726.076.000. Interpretado como segundos, isso é o ano
**58.582**. O token nunca expira. Funciona perfeitamente em todos os testes e é uma
falha crítica em produção: um token roubado vale para sempre.

```js
exp: Math.floor(Date.now() / 1000) + 900   // ✅
```

**Detecção defensiva** — vale a pena no seu verificador:

```js
// nenhum token legítimo dura mais de 30 dias
const TETO = 30 * 86400;
if (payload.exp - (payload.iat ?? agora) > TETO) {
  throw new Error('vida do token acima do teto — provável bug de milissegundos');
}
```

**Tolerância de relógio.** Duas máquinas nunca têm o mesmo relógio. Uma tolerância
(*leeway*) de 60 s é o consenso: aceita-se o token por mais 60 s depois de `exp`.

| Tolerância | Quando faz sentido |
|---|---|
| 0 s | tudo na mesma máquina, ou NTP monitorado com deriva medida |
| **30–60 s** | **padrão sensato** |
| 300 s | ambientes com relógio notoriamente ruim (VMs antigas, IoT) |
| > 300 s | você está estendendo a vida do token, não tolerando desvio |

**Um token sem `exp`.** É válido pela RFC e é uma bomba. Recuse-o explicitamente. No
PyJWT: `options={"require": ["exp"]}`. No `golang-jwt/v5`:
`jwt.WithExpirationRequired()`. No projeto-modelo: erro `exp_ausente`.

---

## 13.6 · `nbf` — antes disso, não vale

**Tipo:** NumericDate. Opcional de verdade.

```json
"nbf": 1786730000
```

Espelho do `exp`: o token **não deve** ser aceito antes de `nbf`. A comparação usa a
mesma tolerância.

**Quando serve de verdade:**

- token emitido hoje para valer a partir da virada de um contrato;
- liberação agendada de um recurso;
- janela de manutenção em que um token administrativo passa a valer.

**Quando atrapalha:** emitir com `nbf = iat` e tolerância zero. Se o relógio de quem
verifica estiver 2 s atrasado, o token acabado de emitir é recusado como "ainda não
válido" — um erro que parece impossível e some sozinho. Se você não tem caso de uso,
**não emita `nbf`**.

---

## 13.7 · `iat` — quando nasceu

**Tipo:** NumericDate. Emita sempre.

Não expressa validade — expressa **idade**. É o que habilita três coisas:

**1. Idade máxima independente do `exp`.** Uma operação sensível (transferir dinheiro,
trocar e-mail) pode exigir um token emitido há menos de 5 minutos, mesmo que ele valha
por 15.

```js
await jwtVerify(token, chave, { ...opcoes, maxTokenAge: '5m' });
```

**2. Invalidação em massa sem lista de negação.** Guarde no usuário um campo
`tokensValidosDesde`. Ao trocar a senha ou detectar comprometimento, ponha o instante
atual ali. Todo token com `iat` anterior é recusado — **um campo, todos os tokens
daquela pessoa mortos**, sem lista, sem Redis.

```js
if (payload.iat < usuario.tokensValidosDesde) throw new Error('token invalidado');
```

Este é o truque mais custo-benefício do assunto, e quase nenhum tutorial menciona.

**3. Diagnóstico.** `exp - iat` diz a vida configurada; `agora - iat` diz há quanto
tempo o token circula.

---

## 13.8 · `jti` — identificador único

**Tipo:** string. Emita quando precisar revogar ou auditar.

```json
"jti": "1852bd58-61c5-452b-b6e5-bb2359f280c0"
```

Precisa ser único o suficiente para que a probabilidade de repetição seja
desprezível: UUIDv4 ou 16+ bytes aleatórios em base64url. **Não use contador
sequencial** — vaza volume de emissão e permite adivinhar tokens vizinhos.

**Três usos:**

1. **Revogação.** A lista de negação guarda `jti` até o `exp` correspondente. Como
   uma entrada só precisa viver o tempo restante do token, a lista fica pequena: com
   access token de 15 min, ela guarda no máximo 15 minutos de logouts.
2. **Uso único.** Token de redefinição de senha, de convite, de confirmação: registre
   o `jti` consumido e recuse a segunda apresentação.
3. **Correlação em log.** Registre o `jti`, **nunca o token**. Você rastreia a
   requisição até a sessão sem transformar o log num repositório de credenciais vivas.

---

## 13.9 · Claims do OpenID Connect

Aparecem sobretudo no `id_token`. As que têm pegadinha:

| Claim | O que é | A pegadinha |
|---|---|---|
| `email` | e-mail | **não confie sem `email_verified: true`** |
| `email_verified` | booleano | é o campo que separa "e-mail" de "e-mail provado" |
| `preferred_username` | nome de exibição | muda; o usuário costuma poder alterar |
| `name`, `given_name`, `family_name` | nome | dado pessoal — vai para todo log |
| `nonce` | anti-repetição do fluxo | **confira** que é o valor que você enviou |
| `auth_time` | quando a pessoa realmente autenticou | ≠ `iat`: um token renovado tem `iat` novo e `auth_time` antigo |
| `acr` / `amr` | nível e método de autenticação | use para exigir MFA (`"amr": ["mfa"]`) em rota sensível |
| `azp` | quem obteve o token | verifique em cenário multi-cliente |
| `at_hash` | amarra o `id_token` ao access token | impede trocar um pelo outro |

**O ataque de tomada de conta por e-mail não verificado**, porque vale escrever por
extenso:

1. seu sistema casa contas por `email`;
2. alguém cria uma conta num provedor OIDC que **não verifica e-mail** usando o
   endereço da vítima;
3. faz login no seu sistema com esse provedor;
4. seu sistema vê o e-mail conhecido e entrega a conta da vítima.

A defesa é uma linha: `if (!payload.email_verified) recusar()`. E, preferencialmente,
não casar contas por e-mail — casar por `(iss, sub)` e pedir confirmação explícita.

---

## 13.10 · Claims de access token (RFC 9068)

| Claim | Formato | Nota |
|---|---|---|
| `scope` | string, separada por **espaço**: `"leitura escrita"` | não é array; separar por vírgula é erro comum |
| `client_id` | string | qual aplicação obteve |
| `roles`, `groups`, `entitlements` | array | autorização; formato livre |
| `cnf` | objeto | *confirmation*: prende o token a uma chave (DPoP, mTLS) |
| `auth_time`, `acr`, `amr` | — | mesma semântica do OIDC |

A RFC 9068 também exige `typ: "at+jwt"` no cabeçalho e a validação de `aud`. Vale
seguir mesmo em sistema fechado: `typ` impede que um `id_token` seja aceito onde se
espera access token.

---

## 13.11 · Suas próprias claims

**Com namespace** (recomendado pela RFC, obrigatório na Auth0):

```json
{ "https://exemplo.com/departamento": "financeiro" }
```

**Sem namespace** (mais curto, aceitável em sistema fechado):

```json
{ "departamento": "financeiro" }
```

Três regras:

1. **Nunca use um nome que possa virar registrado.** `role`, `groups`, `admin`,
   `permissions` são candidatos naturais a registro futuro na IANA. Se um dia forem
   registrados com semântica diferente da sua, você tem um conflito silencioso.
2. **Nomes curtos.** Cada byte é pago em toda requisição.
3. **Nada de dado pessoal ou secreto.** O payload é público para quem tem o token.

---

## 13.12 · Os cinco porquês: por que `exp` é obrigatório na prática, se a RFC diz que é opcional?

**1. Por que exigir `exp` se a RFC não exige?**
Porque um token sem `exp` é uma credencial eterna, e credenciais eternas não podem
ser retiradas de circulação.

**2. Por que não posso simplesmente revogar quando precisar?**
Porque a revogação de um JWT exige consultar uma lista a cada requisição — o que
elimina a única vantagem real do formato, que é a verificação local. A lista de
negação só é barata porque as entradas expiram; sem `exp`, ela cresce para sempre.

**3. Por que a lista precisa ser pequena?**
Porque ela é consultada em toda requisição de toda API. Uma estrutura consultada
milhões de vezes por minuto precisa caber em memória. Uma lista que só cresce
inviabiliza isso em meses.

**4. Por que a RFC deixou `exp` opcional, então?**
Porque o JWT foi projetado como formato de transporte genérico, não como credencial
de sessão. Há usos legítimos sem prazo: um JWT que carrega um documento assinado, um
crachá de longa duração dentro de um JWE com controle externo. A RFC descreve o
**formato**; o perfil de uso é que impõe as regras.

**5. Por que isso não foi corrigido em onze anos?**
Porque tornar `exp` obrigatório quebraria a compatibilidade com todo token e toda
implementação existente. O IETF escolheu o caminho de publicar uma **BCP** — a RFC
8725 — em vez de alterar a RFC 7519.

**Parada legítima:** decisão histórica documentada. A RFC 7519 (mai/2015) definiu um
formato genérico; a RFC 8725 (fev/2020) reconheceu por escrito que o uso real exige
mais rigor do que o formato impõe. É o padrão admitindo a própria permissividade sem
poder desfazê-la.

---

## 13.13 · Receita de validação completa

O conjunto mínimo que um verificador sério aplica:

```js
const { payload } = await jwtVerify(token, chaves, {
  algorithms: ['ES256'],                    // lista fechada
  issuer: 'https://auth.exemplo.com',       // exato, byte a byte
  audience: 'api-pedidos',                  // eu me reconheço aqui?
  clockTolerance: '60s',
  typ: 'at+jwt',                            // é o tipo certo de token?
  maxTokenAge: '1h',                        // não é velho demais?
  requiredClaims: ['sub', 'jti'],
});

// depois da biblioteca, o que só você sabe:
if (armazem.jtiRevogado(payload.jti)) throw new Error('revogado');
if (payload.iat < usuario.tokensValidosDesde) throw new Error('invalidado em massa');
if (payload.exp - payload.iat > 30 * 86400) throw new Error('vida absurda');
```

---

## Autoteste

1. `{}` é um JWT válido pela RFC 7519? O que isso implica para quem verifica?
2. Por que `iss` não prova nada sozinho, e o que o torna útil?
3. Por que `https://conta.auth0.com/` e `https://conta.auth0.com` causam falha de
   validação, e como se evita isso?
4. Descreva o ataque do *confused deputy* que o `aud` bloqueia.
5. Qual é a chave primária real de uma identidade federada, e por que `sub` sozinho
   não basta?
6. Escreva o cálculo correto de `exp` para 15 minutos. Qual o erro comum, e por que
   ele passa em todos os testes?
7. Como invalidar **todos** os tokens de um usuário sem lista de negação?
8. Qual a diferença entre `iat` e `auth_time`, e quando ela importa?
9. Descreva o ataque de tomada de conta por e-mail não verificado, e a defesa.
10. `scope` é array ou string? Qual o separador?
