# Glossário

> Todos os termos técnicos usados neste material, definidos.
> Termo em inglês quando é assim que o campo o usa, com a tradução ao lado.
> Atualizado em 14/08/2026.

---

## A

**AAD** (*Additional Authenticated Data*) — em cifra AEAD, dado que é autenticado mas
não cifrado. Num JWE, o cabeçalho protegido entra como AAD.

**access token** (token de acesso) — a credencial apresentada à API em toda
requisição. Curta (5–15 min), frequentemente um JWT. Ver [17](17-ciclo-de-vida-sessao.md).

**acr** (*Authentication Context Class Reference*) — claim do OIDC que indica o nível
de garantia da autenticação.

**AEAD** (*Authenticated Encryption with Associated Data*) — cifra que também
autentica. `A256GCM` é AEAD.

**alg** — parâmetro do cabeçalho JOSE que declara o algoritmo. **Nunca use este campo
para escolher como verificar** — apenas para conferir contra a sua lista.

**amr** (*Authentication Methods References*) — claim do OIDC com os métodos usados
(ex.: `["pwd","mfa"]`).

**assinatura digital** — valor calculado com uma chave privada que prova integridade e
autenticidade, e que qualquer um verifica com a chave pública.

**at_hash** — claim do OIDC que amarra um `id_token` ao access token emitido junto.

**at+jwt** — valor de `typ` para access token (RFC 9068).

**atenuação** (*attenuation*) — capacidade de derivar de um token uma versão **mais
restrita**, sem falar com o emissor. Macaroons e Biscuit têm; JWT não.

**aud** (*audience*) — claim que diz para quem o token vale. Se você não se reconhece
nela, **recuse**.

**AuthN / AuthZ** — abreviações de autenticação (quem é você) e autorização (o que
você pode).

**autenticação** — provar identidade. Acontece uma vez, no login.

**autorização** — decidir permissão. Acontece em toda requisição.

**azp** (*authorized party*) — claim do OIDC: qual cliente obteve o token. Pode
divergir de `aud`.

---

## B

**base64** — codificação de bytes em 64 caracteres imprimíveis. **Não é criptografia.**

**base64url** — variante com `-` e `_` no lugar de `+` e `/`, e sem o `=` de
preenchimento (RFC 4648 §5). É a que o JOSE usa.

**BCP** (*Best Current Practice*) — categoria de RFC que documenta a prática
recomendada. A RFC 8725 é a BCP do JWT.

**bearer token** (token ao portador) — quem o apresenta é aceito, sem provar mais
nada. Como uma nota de dinheiro. O modelo padrão do JWT.

**Bleichenbacher** — ataque de oráculo de padding contra RSA PKCS#1 v1.5 (1998).
Motivo da proibição de `RSA1_5`. Reapareceu como ROBOT em 2017.

---

## C

**CEK** (*Content Encryption Key*) — em JWE, a chave simétrica que cifra o conteúdo.
Ela mesma é cifrada para o destinatário.

**claim** (afirmação) — par nome/valor no payload. Uma afirmação **do emissor**, não
um fato.

**client credentials** — fluxo do OAuth para serviço↔serviço, sem usuário envolvido.

**cnf** (*confirmation*) — claim que amarra o token a uma chave do cliente. Usada por
DPoP e mTLS.

**confusão de algoritmo** — ataque em que o `alg` do token é trocado (tipicamente
RS256 → HS256) para que a chave pública seja usada como segredo de HMAC.

**cooldown** — intervalo mínimo entre rebuscas do JWKS. Defesa contra tempestade de
requisições.

**crit** (*critical*) — parâmetro do cabeçalho que lista extensões obrigatórias. Se
você não as implementa, **recuse o token**.

**CSRF** (*Cross-Site Request Forgery*) — outro site induz o navegador a enviar uma
requisição autenticada. Mitigado por `SameSite`.

**cty** (*content type*) — parâmetro que declara o tipo do conteúdo. `JWT` em token
aninhado.

---

## D

**denylist** (lista de negação) — conjunto de `jti` revogados antes do `exp`.

**detecção de reuso** — mecanismo que identifica um refresh token já consumido sendo
reapresentado, indicando bug ou roubo.

**deriva de relógio** (*clock skew*) — diferença entre relógios de máquinas
diferentes. Causa 401 intermitente.

**DER** — codificação binária de ASN.1. **Não** é o formato da assinatura ECDSA no
JWS (que usa P1363).

**DPoP** (*Demonstrating Proof-of-Possession*, RFC 9449) — amarra o token a uma chave
do cliente; um token roubado fica inútil.

**double submit cookie** — defesa contra CSRF: o mesmo valor num cookie legível e num
cabeçalho.

---

## E

**ECDSA** — assinatura sobre curva elíptica. `ES256` = ECDSA com P-256 e SHA-256.
Frágil se o nonce `k` se repetir.

**EdDSA** — assinatura de Edwards; `Ed25519` no JOSE (RFC 8037). Determinística e
resistente a canal lateral por projeto.

**emissor** (*issuer*) — quem assina e emite o token. No OAuth, o *authorization
server*.

**enc** — em JWE, o algoritmo que cifra o conteúdo (distinto de `alg`).

**EUF-CMA** (*Existential Unforgeability under Chosen Message Attack*) — o padrão
formal de segurança para esquemas de assinatura.

**exp** (*expiration time*) — claim com o instante em que o token deixa de valer. Em
**segundos**.

---

## F

**família** (de refresh tokens) — todos os refresh descendentes de um mesmo login.
Queimada por inteiro ao detectar reuso.

**federação** — aceitar identidades emitidas por outra organização.

**filtro de Bloom** — estrutura probabilística de conjunto, com falsos positivos e
zero falsos negativos. Candidata a lista de negação de grande escala.

---

## G

**GCM** (*Galois/Counter Mode*) — modo AEAD do AES. Um par (chave, IV) **nunca** pode
se repetir.

---

## H

**HMAC** (*Hash-based Message Authentication Code*, RFC 2104) — MAC simétrico. `HS256`
= HMAC-SHA256. Quem verifica pode forjar.

**HSM** (*Hardware Security Module*) — dispositivo que guarda chaves e assina sem
jamais revelá-las.

**HttpOnly** — atributo de cookie que impede o JavaScript de lê-lo. Defesa central
contra XSS roubar o refresh token.

---

## I

**iat** (*issued at*) — quando o token foi emitido. Habilita idade máxima e
invalidação em massa.

**id_token** — token do OIDC que prova **quem é a pessoa**. Sempre um JWT. É para o
**cliente**, nunca para a API.

**IdP** (*Identity Provider*) — quem autentica pessoas e emite tokens.

**introspecção** (RFC 7662) — o recurso consulta o emissor para saber se um token
opaco é válido. A alternativa ao JWT.

**iss** (*issuer*) — claim que identifica o emissor. Comparação **exata**, byte a
byte.

**IV** (*Initialization Vector*) — valor público e único por operação de cifra.

---

## J

**JOSE** (*JavaScript Object Signing and Encryption*) — a família de padrões: JWS,
JWE, JWK, JWA.

**jku** (*JWK Set URL*) — parâmetro que aponta para um JWKS. ⚠️ o token dizendo onde
buscar sua própria chave. **Ignore.**

**jti** (*JWT ID*) — identificador único do token. Base da revogação e do log seguro.

**JWA** (RFC 7518) — o catálogo de algoritmos.

**JWE** (RFC 7516) — token **cifrado**. Cinco segmentos.

**JWK** (RFC 7517) — uma chave como objeto JSON.

**JWKS** (*JWK Set*) — documento com as chaves **públicas** do emissor, tipicamente em
`/.well-known/jwks.json`.

**JWS** (RFC 7515) — token **assinado**. Três segmentos. É o que quase todo mundo
chama de "JWT".

**JWS Signing Input** — a entrada exata da assinatura:
`ASCII(base64url(cabeçalho) || '.' || base64url(payload))`.

**JWT** (RFC 7519) — o conjunto de claims que vai dentro de um JWS (ou JWE). Não é um
formato de serialização.

**jwk** (parâmetro de cabeçalho) — a chave pública embutida no token. ⚠️ **nunca
confie.**

---

## K

**kid** (*key ID*) — identificador da chave que assinou. É **rótulo**, nunca
**endereço**.

**KMS** (*Key Management Service*) — serviço que guarda chaves e executa operações sem
revelá-las.

---

## L

**leeway** (tolerância) — folga na validação de tempo, para absorver deriva de
relógio. 60 s é o consenso.

**LGPD** — Lei Geral de Proteção de Dados. Relevante porque o payload de um JWT é
legível e costuma carregar dado pessoal.

---

## M

**MAC** (*Message Authentication Code*) — valor que prova integridade e autenticidade
com chave **simétrica**.

**Macaroons / Biscuit** — tokens com atenuação.

**MAU / MRU / DAU** — unidades de cobrança de serviços de identidade: usuários ativos
por mês, retidos por mês, ativos por dia. **Não são comparáveis entre si.**

**ML-DSA** — assinatura pós-quântica baseada em reticulados (FIPS 204). No JOSE pela
RFC 9964 (mai/2026). Assinatura de ~2,4 KB.

**mTLS** (RFC 8705) — TLS com certificado de cliente; amarra o token ao certificado.

---

## N

**nbf** (*not before*) — antes desse instante o token não vale.

**nested JWT** — um JWS assinado, colocado dentro de um JWE. Assina-se primeiro,
cifra-se depois.

**nonce** — valor usado uma única vez. No OIDC, o valor anti-repetição do `id_token`.
Em ECDSA, o `k` — cuja repetição derruba a chave.

**none** — algoritmo `alg` sem assinatura. **Nunca aceite.**

**NumericDate** — número de **segundos** desde 1970-01-01T00:00:00Z. Não
milissegundos.

---

## O

**OAuth 2.0** (RFC 6749) — framework de **autorização** delegada. Não é autenticação e
não define o formato do token.

**OIDC** (OpenID Connect) — camada de **autenticação** sobre o OAuth 2.0.

**opaco** (token) — token sem estrutura nem significado; um ponteiro para estado no
servidor.

---

## P

**P1363** (IEEE 1363) — formato `r‖s` cru da assinatura ECDSA, de tamanho fixo. **É o
que o JWS exige.**

**PASETO** — alternativa ao JOSE, sem negociação de algoritmo. A versão do token
determina a criptografia.

**payload** — o segundo segmento do token; as claims. **Legível por qualquer um.**

**PKCE** (*Proof Key for Code Exchange*, RFC 7636) — protege o código de autorização
contra interceptação. Obrigatório para todos os clientes.

**pós-quântico** — criptografia resistente a computador quântico. Ver ML-DSA,
SLH-DSA, FN-DSA.

**PoP** (*proof of possession*) — o portador prova ter uma chave. Ver DPoP, mTLS.

**PRF** (*Pseudorandom Function*) — hipótese sob a qual a segurança do HMAC é provada.

**PS256** — RSA-PSS com SHA-256. Tecnicamente melhor que RS256; pouco adotado.

---

## R

**refresh token** — credencial de longa duração usada só para obter novos access
tokens. Deve ser **opaco** e guardado como hash.

**resource server** — o serviço que verifica o token e serve o recurso.

**revogação** — invalidar uma credencial antes do prazo. Difícil com JWT
autocontido — ver o [teorema informal da revogação](60-teoria-avancada.md#605--o-teorema-informal-da-revogação).

**ROM** (*Random Oracle Model*) — modelo idealizado em que o hash é uma função
verdadeiramente aleatória. Provas nele são evidência, não prova.

**rotação** — (de chave) trocar a chave de assinatura mantendo a antiga para
verificação; (de refresh) emitir um novo a cada uso.

**RS256** — RSA com PKCS#1 v1.5 e SHA-256. Interoperável; assinatura de 256 bytes.

---

## S

**SameSite** — atributo de cookie que controla o envio em contexto de outro site.
`Strict`, `Lax` ou `None`.

**scope** (escopo) — o que o **cliente** foi autorizado a fazer. String separada por
**espaço**.

**SD-JWT** (RFC 9901, nov/2025) — divulgação seletiva: o portador revela apenas
algumas claims, e o verificador ainda confere a assinatura do emissor.

**SSRF** (*Server-Side Request Forgery*) — induzir o servidor a fazer requisições a
endereços escolhidos pelo atacante. Risco do `jku`.

**stateless** (sem estado) — o HTTP é. O **token** JWT é autocontido; o **sistema**
que o usa quase nunca é.

**sub** (*subject*) — de quem o token fala. Único **dentro do emissor**. A chave real
é o par `(iss, sub)`.

**SUF-CMA** — versão mais forte de EUF-CMA, que proíbe também assinaturas alternativas
para a mesma mensagem.

---

## T

**thumbprint** (RFC 7638) — hash canônico de uma chave, usado como `kid`. Derivado da
própria chave, sem coordenação.

**tokensValidosDesde** — campo no usuário que invalida todos os tokens com `iat`
anterior. A revogação em massa mais barata que existe.

**Transaction Token** — rascunho do IETF: token interno de vida curta que propaga
identidade e contexto pela cadeia de microsserviços.

**typ** — parâmetro que declara o tipo do token. `at+jwt`, `dpop+jwt`, `reset+jwt`.
Firewall entre tipos.

---

## X

**x5c / x5t / x5u** — parâmetros de cabeçalho com certificado X.509 ou sua URL.
Mesmas ressalvas do `jku`.

**XSS** (*Cross-Site Scripting*) — execução de código do atacante na sua página.
Motivo pelo qual o refresh token deve estar em cookie `HttpOnly`.

**XML Signature Wrapping** — família de ataques contra assinatura XML, em que o
verificador valida um elemento e o processador lê outro. O problema que o JOSE
decidiu eliminar por projeto.

---

## Siglas de uma linha

| Sigla | Expansão |
|---|---|
| AEAD | Authenticated Encryption with Associated Data |
| BCP | Best Current Practice |
| CEK | Content Encryption Key |
| CRQC | Cryptographically Relevant Quantum Computer |
| DAU/MAU/MRU | Daily / Monthly Active User, Monthly Retained User |
| DPoP | Demonstrating Proof-of-Possession |
| EUF-CMA | Existential Unforgeability under Chosen Message Attack |
| HSM | Hardware Security Module |
| IdP | Identity Provider |
| JOSE | JavaScript Object Signing and Encryption |
| JWA/JWE/JWK/JWS/JWT | ver acima |
| KMS | Key Management Service |
| MAC | Message Authentication Code |
| OIDC | OpenID Connect |
| PKCE | Proof Key for Code Exchange |
| PoP | Proof of Possession |
| PRF | Pseudorandom Function |
| ROM | Random Oracle Model |
| SD-JWT | Selective Disclosure JWT |
| SSRF | Server-Side Request Forgery |
| XSS | Cross-Site Scripting |
