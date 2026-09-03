# 20 · Ataques e defesas

> Nível: avançado · Atualizado em 14/08/2026
> Todo ataque desta página está **implementado como teste** em
> [07-projeto-modelo/test/jwt.test.js](07-projeto-modelo/test/jwt.test.js) e é
> executado a cada `node --test`.

**Contexto de uso.** Este material é para quem defende: implementar verificação
correta, escrever testes que provam a defesa, e auditar código próprio ou de sistemas
que você tem autorização para testar. É o mesmo conteúdo que a RFC 8725 e o OWASP
publicam abertamente, porque a defesa exige entender o ataque.

---

## 20.1 · O padrão por trás de quase tudo

Nenhum incidente conhecido com JWT quebrou HMAC-SHA256 ou ECDSA. **Todos** exploraram
o mesmo padrão:

> **O token diz como deve ser verificado, e quem manda o token é quem ataca.**

Guarde a lista de perguntas. Ela cobre a maioria dos ataques:

1. Quem escolhe o **algoritmo**? (deve ser você)
2. Quem escolhe a **chave**? (deve ser você)
3. O que é lido **antes** da verificação? (deve ser só o `kid`)
4. O que é verificado **além** da assinatura? (`iss`, `aud`, `exp`, `typ`)
5. Onde o token **vaza**? (log, URL, cache, `Referer`)

---

## 20.2 · `alg: none`

**O ataque.** A RFC 7515 define `none` como algoritmo válido ("JWS não seguro"). Um
token com `{"alg":"none"}` e terceiro segmento vazio é sintaticamente correto.

```bash
b64() { openssl base64 -A | tr '+/' '-_' | tr -d '='; }
H=$(printf '%s' '{"alg":"none","typ":"JWT"}' | b64)
P=$(printf '%s' '{"sub":"admin","papeis":["admin"],"exp":2000000000}' | b64)
echo "$H.$P."     # note o ponto final, com assinatura vazia
```

Bibliotecas com a API `verify(token, chave)` viam "sem assinatura", pulavam a
verificação e **retornavam sucesso**.

**Variações que reabrem a falha em código já corrigido:**

| Variação | Como escapa |
|---|---|
| `nOnE`, `NONE`, `None` | comparação de string sem normalizar caixa |
| `" none"` (espaço à frente) | comparação sem `trim`, ou regex sem âncora |
| `alg` ausente | código que trata `undefined` como "não precisa verificar" |
| `alg` como array `["none"]` | comparação frouxa (`==` em JS coage array de 1 elemento) |

**A defesa.** Lista fechada de algoritmos aceitos, no verificador. O `alg` do token é
**conferido**, nunca usado para escolher.

```js
if (!ALGORITMOS_ACEITOS.includes(cabecalho.alg)) throw new Error('alg não permitido');
```

Como a comparação é de igualdade contra uma lista de literais, `nOnE`, `" none"` e
`["none"]` falham automaticamente. **A defesa correta não precisa enumerar as
variações** — se você está escrevendo uma lista negra de variantes de "none", a
arquitetura já está errada.

---

## 20.3 · Confusão de algoritmo (RS256 → HS256)

**O ataque mais elegante do assunto.** O serviço verifica com RS256, usando a chave
**pública** do emissor — que é pública por definição, e está no JWKS.

O atacante:

1. baixa a chave pública em `/.well-known/jwks.json`;
2. monta um token com `{"alg":"HS256"}`;
3. calcula o HMAC usando **o texto da chave pública como segredo**;
4. envia.

O verificador ingênuo lê `alg: HS256`, pega "a chave" configurada — que é a chave
pública RSA — e a usa como segredo de HMAC. **Confere.**

```js
// o forjador (teste real, em test/jwt.test.js)
const pemPublico = publicKey.export({ type: 'spki', format: 'pem' });
const entrada = `${cabecalhoB64}.${payloadB64}`;
const forjada = createHmac('sha256', pemPublico).update(entrada).digest('base64url');
const tokenForjado = `${entrada}.${forjada}`;
```

Nenhuma informação secreta foi usada.

**A sutileza que reabre a falha:** o atacante precisa acertar a representação exata da
chave usada como segredo — PEM com ou sem quebra de linha final, DER, JWK. Bibliotecas
que tentam detectar "isto parece uma chave pública, então recuse HS256" por expressão
regular acabam sendo contornadas.

Foi exatamente isso na **CVE-2026-34950** (`fast-jwt`, CVSS 9,1, publicada em
06/04/2026): a regex que detectava a chave pública podia ser derrotada por um
**espaço em branco no início** da string. Uma falha corrigida anos antes voltou por
um caractere.

E na **CVE-2026-48526** (PyJWT anterior à 2.13.0): confusão de algoritmo quando a
aplicação valida com JWK cru e suporta famílias mistas de algoritmo.

**A defesa.**

1. Lista fechada de algoritmos — resolve sozinha, porque `HS256` não está na lista de
   um serviço que usa RS256.
2. Chave **tipada**: a resolução devolve um `KeyObject` assimétrico, e a função de
   HMAC recusa esse tipo.
3. Nunca aceitar famílias simétrica e assimétrica na mesma configuração.

```js
// no projeto-modelo, as duas defesas:
if (!algoritmos.includes(cabecalho.alg)) throw new ErroJwt('alg_nao_permitido');
// e normalizarSegredo() recusa um KeyObject, então mesmo com HS256 na lista falha
```

---

## 20.4 · Injeção por `kid`

O `kid` é um campo de texto controlado pelo atacante. Se ele for usado como
**endereço**, vira injeção.

### Travessia de caminho

```json
{"alg":"HS256","kid":"../../../../dev/null"}
```

Se o código faz `fs.readFileSync('/chaves/' + kid + '.pem')`, o atacante escolhe o
arquivo. `/dev/null` é **vazio** — então ele assina o token com string vazia como
segredo, e o token é aceito.

Outros alvos com conteúdo previsível: `/proc/sys/kernel/ostype` (`"Linux\n"`),
qualquer arquivo estático servido pela sua própria aplicação.

### SQL

```json
{"alg":"HS256","kid":"' UNION SELECT 'segredo-do-atacante' -- "}
```

Se o `kid` entra em concatenação de SQL, o atacante devolve a própria chave como
resultado da consulta. Uma injeção de SQL **na verificação da autenticação** — antes
de qualquer log de usuário, antes de qualquer sessão.

### Comando

`kid` interpolado em shell. Raro, catastrófico.

**A defesa, em uma frase:** `kid` é **rótulo**, nunca **endereço**. Use-o como chave
de um `Map` em memória, populado a partir do seu próprio JWKS.

```js
const chave = chaveiro.chaves.get(cabecalho.kid) ?? null;   // ✅ e acabou
```

---

## 20.5 · `jku`, `jwk`, `x5u`, `x5c` — o token trazendo a própria chave

Quatro parâmetros de cabeçalho que dizem **onde buscar** ou **qual é** a chave de
verificação.

```json
{"alg":"RS256","jwk":{"kty":"RSA","n":"<a chave do atacante>","e":"AQAB"}}
```

Se o verificador usa a chave que veio no token, ele valida a assinatura do atacante
contra a chave do atacante. **Sempre confere.**

Com `jku`, é uma URL:

```json
{"alg":"RS256","jku":"https://atacante.com/jwks.json"}
```

Dois estragos de uma vez: a chave falsa **e** uma requisição de saída do seu servidor
para um endereço escolhido pelo atacante — SSRF, que pode alcançar o serviço de
metadados da nuvem (`169.254.169.254`) e vazar credenciais de instância.

**A defesa:**

| Cabeçalho | O que fazer |
|---|---|
| `jwk` | **ignore sempre**. Não há caso de uso legítimo em JWT de autenticação |
| `jku` | ignore; se for realmente necessário, **lista branca de URLs exatas** |
| `x5u` | idem |
| `x5c` | só com validação completa de cadeia contra uma CA que você configurou |

**Contra-argumento honesto:** há usos legítimos de `jwk` — em DPoP (RFC 9449), a
prova carrega a chave pública do cliente no cabeçalho. Mas ali a chave é confirmada
contra a claim `cnf` do access token, e não é usada isoladamente. A regra "ignore
`jwk`" vale para o token de acesso; extensões que o usam definem o vínculo
separadamente.

---

## 20.6 · Segredo HMAC fraco — ataque offline

**O ataque.** Quem tem **um** token seu tem um par (mensagem, MAC). Pode testar
bilhões de segredos por segundo na própria GPU: sem tocar no seu servidor, sem log,
sem limite de tentativas.

Ferramentas prontas: `hashcat` (modo 16500), `jwt_tool`, `john`.

| Segredo | Entropia | Tempo até quebrar (GPU comum, 2026) |
|---|---|---|
| `secret` | ~0 (está em toda lista) | instantâneo |
| `minha-empresa-2026` | ~40 bits | minutos |
| `Xk9$mP2!qR7@` (12 chars) | ~70 bits | anos |
| `openssl rand -base64 32` | **256 bits** | inviável |

**A defesa:**

```bash
openssl rand -base64 32      # ✅ 32 bytes de aleatoriedade real
```

E nunca use HS256 quando ES256 resolve. Um segredo compartilhado entre 15 serviços é
15 lugares de onde ele pode vazar — e a auditoria não distingue qual deles emitiu um
token.

---

## 20.7 · Ataques de claim

| Ataque | Como funciona | Defesa |
|---|---|---|
| **Sem `exp`** | token eterno; a RFC permite | recuse token sem `exp` |
| **`exp` em milissegundos** | vira ano 58.000 | valide `exp - iat` contra um teto |
| **Token de outra audiência** | token válido de outro serviço aceito aqui | valide `aud` |
| **Token de outro emissor** | dois provedores, chaves num pote comum | valide `iss` e separe as chaves por emissor |
| **`id_token` como access token** | `aud` é o cliente, não a API | valide `typ: at+jwt` |
| **Chave JSON duplicada** | `{"sub":"ana","sub":"admin"}` — analisadores discordam | recuse duplicatas; use biblioteca que recusa |
| **`sub` numérico grande** | `JSON.parse` perde precisão acima de 2^53 | use string em identificadores |
| **Repetição (*replay*)** | token capturado reenviado | `jti` de uso único, ou vida muito curta, ou DPoP |
| **`nbf` no futuro** | token pré-datado usado antes da hora | valide `nbf` |

---

## 20.8 · Vazamento de token

O token é uma credencial. Onde ele vaza:

| Onde | Como | Defesa |
|---|---|---|
| **URL** (`?token=...`) | histórico, log de servidor, `Referer`, analytics | nunca em URL |
| **Log de aplicação** | `console.log(req.headers)` | filtro de redação; registre o `jti`, não o token |
| **Cache de proxy/CDN** | resposta com token sem `no-store` | `Cache-Control: no-store` em toda resposta com token |
| **`Referer`** | link externo a partir de página com token na URL | idem "nunca em URL"; `Referrer-Policy` |
| **Mensagem de erro** | *stack trace* com o token | não ecoe entrada em erro |
| **Repositório Git** | token de teste comitado | *pre-commit hook* que bloqueia padrões `eyJ` |
| **Site de depuração** | token de produção colado no jwt.io | use `jwt-cli`, offline |
| **HTML do SSR** | token no estado embutido, HTML cacheado pela CDN | nunca embuta credencial no HTML |
| **Ferramenta de APM** | coleta cabeçalhos automaticamente | configure a redação de `Authorization` |

```js
// filtro de redação — o mínimo em qualquer log estruturado
const CAMPOS_SENSIVEIS = /authorization|cookie|token|secret|password|senha/i;
function limpar(objeto) {
  return Object.fromEntries(Object.entries(objeto).map(([k, v]) =>
    [k, CAMPOS_SENSIVEIS.test(k) ? '[REDIGIDO]' : v]));
}
```

```bash
# hook de pre-commit: bloqueia JWT comitado por acidente
grep -rEn 'eyJ[A-Za-z0-9_-]{10,}\.eyJ' --include='*' . && {
  echo "🚨 possível JWT no commit"; exit 1; }
```

---

## 20.9 · Ataques de aplicação

### *Confused deputy*

O serviço A recebe o token da pessoa e o reenvia ao serviço B. B aceita, e A acabou
de agir em B com a identidade da pessoa, para além do que deveria.

**Defesa:** `aud` específica por serviço. B recusa token cuja audiência é A. Para
chamadas legítimas entre serviços, use **troca de token** (RFC 8693) ou um token
próprio do serviço, com escopo mínimo — ver
[exemplo 13](06-exemplos.md#13--produção-token-de-serviço-para-serviço-com-escopo-mínimo).

### Escalação por confiança na borda

O gateway verifica o JWT e repassa `x-usuario-id` à origem. Se alguém alcançar a
origem diretamente, forja o cabeçalho e vira quem quiser.

**Defesa:** origem inacessível de fora (rede privada, mTLS, segredo compartilhado com
a borda), **e** remoção explícita dos cabeçalhos de identidade vindos do cliente na
borda.

### Autorização só no cliente

O front lê o token, vê `papeis: ["usuario"]` e esconde o botão de administrador.
A API não checa nada.

**Defesa:** o cliente decide o que **mostrar**; o servidor decide o que **permitir**.
Nunca o contrário. Esconder o botão não é autorização.

### Decodificar sem verificar no servidor

```js
const dados = JSON.parse(atob(token.split('.')[1]));  // ❌
if (dados.papel === 'admin') { /* qualquer um é admin */ }
```

Continua sendo encontrado em auditoria, em 2026. Por isso o projeto-modelo chama a
função de `decodificarSemVerificar` — se dói ler numa revisão de código, está
funcionando.

---

## 20.10 · Negação de serviço

| Ataque | Mecanismo | Defesa |
|---|---|---|
| **Tempestade de JWKS** | mil `kid` inventados → mil buscas ao emissor | *cooldown* no cliente JWKS |
| **Token gigante** | payload de 10 MB | limite de tamanho **antes** de analisar |
| **Bomba de JSON** | aninhamento profundo esgota a pilha | limite de profundidade; analisador com limites |
| **`p2c` alto em PBES2** | fator de trabalho controlado pelo atacante | teto no `p2c`; ou não aceite PBES2 |
| **Bomba de compressão em JWE** (`zip: DEF`) | 1 KB descomprime para 1 GB | limite de saída da descompressão |

```js
// limite de tamanho, antes de qualquer análise
if (token.length > 8192) throw new Error('token grande demais');
```

O `p2c` merece nota: em `PBES2-HS256+A128KW`, o cabeçalho traz o número de iterações
de derivação de chave. Um atacante pede 10 milhões e cada token custa segundos de CPU
do seu servidor. É o token dizendo quanto trabalho você deve fazer.

---

## 20.11 · Ataques de canal lateral

| Ataque | Onde | Defesa |
|---|---|---|
| **Temporização em comparação de MAC** | `===` para em bytes diferentes | `timingSafeEqual` |
| **Temporização em busca de usuário** | resposta mais rápida quando o e-mail não existe | tempo constante; mesma mensagem de erro |
| **Mensagem de erro reveladora** | "assinatura inválida" vs. "expirado" ao cliente | mensagem genérica ao cliente, detalhe no log |
| **Oráculo de padding** | `RSA1_5` no JWE | não use `RSA1_5` |

> **Ressalva honesta:** ataques de temporização por rede pública são difíceis (o ruído
> domina). Mas custam uma linha para evitar, e são fáceis quando o atacante está na
> mesma rede ou no mesmo host. Faça sempre.

---

## 20.12 · Checklist de auditoria

Para revisar qualquer implementação — a sua ou a herdada:

```
ALGORITMO
[ ] Lista fechada de `alg` aceitos, no código do verificador
[ ] `none` impossível por construção (não está na lista), não por lista negra
[ ] Famílias simétrica e assimétrica NÃO coexistem na mesma configuração
[ ] Segredo HMAC ≥ 32 bytes de aleatoriedade real (se houver HMAC)

CHAVE
[ ] `kid` usado só como índice de Map local
[ ] `jwk`, `jku`, `x5u` ignorados (ou lista branca explícita)
[ ] JWKS sem componente privado (teste automatizado)
[ ] Chave privada fora do repositório e do histórico do Git

CLAIMS
[ ] `iss` validado, comparação exata
[ ] `aud` validado, tratando string E array
[ ] `exp` obrigatório e validado, com tolerância ≤ 60 s
[ ] `typ` validado (`at+jwt` para access token)
[ ] Teto sanitário para `exp - iat`

ORDEM
[ ] Nada do payload é usado antes de a assinatura conferir
[ ] Comparação de MAC em tempo constante

CICLO DE VIDA
[ ] Access token ≤ 15 min
[ ] Refresh opaco, rotacionado, com detecção de reuso
[ ] Logout revoga access (jti) E refresh
[ ] Procedimento de rotação de chave testado

VAZAMENTO
[ ] Token nunca em URL
[ ] `Cache-Control: no-store` em respostas com token
[ ] Redação de `Authorization` em logs e no APM
[ ] Hook de pre-commit contra `eyJ...` no repositório

DOS
[ ] Limite de tamanho do token antes da análise
[ ] Cliente JWKS com cache e cooldown

TESTES
[ ] Existe teste que emite `alg: none` e espera recusa
[ ] Existe teste de confusão de algoritmo
[ ] Existe teste com `kid` de travessia de caminho
[ ] Existe teste de token expirado, de outra audiência e de chave errada
```

---

## 20.13 · Ferramentas

| Ferramenta | Para quê | Link |
|---|---|---|
| `jwt_tool` | análise e teste de ataques conhecidos | <https://github.com/ticarpi/jwt_tool> |
| `hashcat` (modo 16500) | força bruta de segredo HMAC — teste a força do **seu** | <https://hashcat.net> |
| `jwt-cli` | decodificar/verificar offline | <https://github.com/mike-engel/jwt-cli> |
| Burp Suite + JWT Editor | teste manual de aplicação web | <https://portswigger.net> |
| PortSwigger Web Security Academy | **laboratórios gratuitos** de ataques a JWT | <https://portswigger.net/web-security/jwt> |

Use-as no seu próprio sistema, ou onde você tem autorização escrita. Os laboratórios
do PortSwigger são ambientes feitos para isso e são gratuitos — é o melhor caminho
para praticar sem risco legal.

---

## Autoteste

1. Enuncie o padrão comum a quase todos os ataques a JWT.
2. Por que uma lista fechada de algoritmos derrota `nOnE`, `" none"` e `["none"]` sem
   precisar enumerá-los?
3. Descreva a confusão RS256→HS256. Que informação secreta o atacante precisa?
4. O que foi a CVE-2026-34950 e por que ela é instrutiva?
5. Por que `kid: "../../dev/null"` funciona como ataque?
6. Por que `jku` causa dois estragos, e qual é o segundo?
7. Por que um ataque offline contra segredo HMAC é mais perigoso que um online?
8. Descreva o *confused deputy* e a defesa.
9. Cite cinco lugares onde um token vaza sem ninguém perceber.
10. O que é o ataque do `p2c` alto, e o que ele tem em comum com o `alg` no token?
