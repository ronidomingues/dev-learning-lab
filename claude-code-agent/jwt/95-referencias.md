# 95 · Referências — specs, ferramentas, código e pessoas

> Nível: todos · Atualizado em 14/08/2026
> Tudo aqui é fonte primária ou ferramenta verificável.

---

## 95.1 · As RFCs — o núcleo do JOSE

Publicadas em bloco, em **19 de maio de 2015**.

| RFC | Título | Ler? |
|---|---|---|
| [**7519**](https://www.rfc-editor.org/rfc/rfc7519) | JSON Web Token (JWT) | ✅ **inteira**, ~30 páginas. É o documento do assunto |
| [**7515**](https://www.rfc-editor.org/rfc/rfc7515) | JSON Web Signature (JWS) | ✅ seções 1–5; os apêndices são vetores de teste úteis |
| [7516](https://www.rfc-editor.org/rfc/rfc7516) | JSON Web Encryption (JWE) | 🟡 só se for usar JWE |
| [**7517**](https://www.rfc-editor.org/rfc/rfc7517) | JSON Web Key (JWK) | ✅ curta e prática |
| [**7518**](https://www.rfc-editor.org/rfc/rfc7518) | JSON Web Algorithms (JWA) | ✅ como referência; §3.2 define os tamanhos mínimos de chave |
| [7520](https://www.rfc-editor.org/rfc/rfc7520) | Exemplos de proteção JOSE | 🟡 **vetores de teste** — ouro para quem implementa |
| [**7638**](https://www.rfc-editor.org/rfc/rfc7638) | JWK Thumbprint | ✅ 10 páginas; define o `kid` correto |
| [7797](https://www.rfc-editor.org/rfc/rfc7797) | JWS com payload não codificado | ⬜ raro; entenda por que é raro |
| [8037](https://www.rfc-editor.org/rfc/rfc8037) | Curvas CFRG (Ed25519) no JOSE | 🟡 se for usar EdDSA |

---

## 95.2 · Boas práticas — leia estas antes de escrever código

| RFC | Título | Por quê |
|---|---|---|
| [**8725**](https://www.rfc-editor.org/rfc/rfc8725) | **JWT Best Current Practices** (fev/2020) | ⭐ **A RFC mais útil do assunto.** 15 páginas. É o IETF dizendo "não faça o que a 7519 permite" |
| [**9700**](https://www.rfc-editor.org/rfc/rfc9700) | OAuth 2.0 Security BCP (jan/2025) | ⭐ mata o fluxo *implicit*, exige PKCE e rotação de refresh |
| [**9068**](https://www.rfc-editor.org/rfc/rfc9068) | JWT Profile for OAuth 2.0 Access Tokens (out/2021) | define `typ: at+jwt` e as claims de access token |

---

## 95.3 · OAuth 2.0 e OpenID Connect

| Referência | O que é |
|---|---|
| [RFC 6749](https://www.rfc-editor.org/rfc/rfc6749) | OAuth 2.0 — o framework |
| [RFC 6750](https://www.rfc-editor.org/rfc/rfc6750) | Bearer Token Usage — define `Authorization: Bearer` e o `WWW-Authenticate` |
| [RFC 7636](https://www.rfc-editor.org/rfc/rfc7636) | **PKCE** — obrigatório para todos os clientes |
| [RFC 7662](https://www.rfc-editor.org/rfc/rfc7662) | Token Introspection — a alternativa ao JWT |
| [RFC 7009](https://www.rfc-editor.org/rfc/rfc7009) | Token Revocation |
| [RFC 8414](https://www.rfc-editor.org/rfc/rfc8414) | Authorization Server Metadata — a descoberta |
| [RFC 8628](https://www.rfc-editor.org/rfc/rfc8628) | Device Authorization Grant — TV, console |
| [RFC 8693](https://www.rfc-editor.org/rfc/rfc8693) | Token Exchange — troca entre serviços |
| [RFC 7523](https://www.rfc-editor.org/rfc/rfc7523) | JWT como concessão e como autenticação de cliente |
| [OpenID Connect Core 1.0](https://openid.net/specs/openid-connect-core-1_0.html) | a especificação do `id_token`; §3.1.3.7 tem os 11 passos de validação |
| [OpenID Connect Discovery 1.0](https://openid.net/specs/openid-connect-discovery-1_0.html) | `/.well-known/openid-configuration` |
| [draft-ietf-oauth-v2-1](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-v2-1-15) | OAuth 2.1 — ainda rascunho (mar/2026) |

---

## 95.4 · Prova de posse e o estado da arte

| Referência | O que é |
|---|---|
| [**RFC 9449**](https://www.rfc-editor.org/rfc/rfc9449) | **DPoP** — prova de posse sem certificado |
| [RFC 8705](https://www.rfc-editor.org/rfc/rfc8705) | mTLS: autenticação de cliente e token amarrado ao certificado |
| [**RFC 9901**](https://www.rfc-editor.org/rfc/rfc9901) | **SD-JWT** — divulgação seletiva (19/11/2025) |
| [**RFC 9964**](https://datatracker.ietf.org/doc/rfc9964/) | **ML-DSA para JOSE e COSE** (mai/2026) |
| [draft-ietf-oauth-sd-jwt-vc](https://datatracker.ietf.org/doc/draft-ietf-oauth-sd-jwt-vc/) | credenciais verificáveis sobre SD-JWT |
| [draft-ietf-oauth-transaction-tokens](https://drafts.oauth.net/oauth-transaction-tokens/draft-ietf-oauth-transaction-tokens.html) | Transaction Tokens |
| [draft-oauth-transaction-tokens-for-agents](https://www.ietf.org/archive/id/draft-oauth-transaction-tokens-for-agents-04.html) | contexto de agente de IA nos tokens |
| [draft-ietf-oauth-identity-chaining](https://datatracker.ietf.org/doc/draft-ietf-oauth-identity-chaining/) | identidade entre domínios de confiança |
| [draft-ietf-jose-pq-composite-sigs](https://datatracker.ietf.org/doc/draft-ietf-jose-pq-composite-sigs/) | assinaturas híbridas clássica + pós-quântica |
| [draft-ietf-cose-falcon](https://datatracker.ietf.org/doc/draft-ietf-cose-falcon/) | FN-DSA para JOSE/COSE |

---

## 95.5 · Registros IANA — a fonte da verdade sobre nomes

Quando você quiser saber se uma claim ou um `alg` é registrado, é aqui:

| Registro | O que lista |
|---|---|
| [JSON Web Token Claims](https://www.iana.org/assignments/jwt/jwt.xhtml) | **todas** as claims registradas |
| [JOSE Algorithms](https://www.iana.org/assignments/jose/jose.xhtml) | todos os `alg` e `enc` válidos |
| [Media Types](https://www.iana.org/assignments/media-types/media-types.xhtml) | `application/at+jwt`, `dpop+jwt` etc. |
| [OAuth Parameters](https://www.iana.org/assignments/oauth-parameters/oauth-parameters.xhtml) | parâmetros do OAuth |

Consultar o registro de claims **antes** de inventar um nome próprio evita que a sua
claim colida com uma registrada no futuro.

---

## 95.6 · Bibliotecas — código-fonte que vale ler

| Biblioteca | Repositório | Por que ler o código |
|---|---|---|
| **`jose`** (JS) | [github.com/panva/jose](https://github.com/panva/jose) | ⭐ **a referência**. Código limpo, zero dependências. Ler `src/jws/` ensina JOSE |
| PyJWT | [github.com/jpadilla/pyjwt](https://github.com/jpadilla/pyjwt) | Python; veja o histórico das correções de confusão de algoritmo |
| Nimbus JOSE+JWT | [connect2id.com/products/nimbus-jose-jwt](https://connect2id.com/products/nimbus-jose-jwt) | a mais completa em Java; base do Spring Security |
| JJWT | [github.com/jwtk/jjwt](https://github.com/jwtk/jjwt) | Java; API fluente; separação api/impl |
| `golang-jwt/jwt` | [github.com/golang-jwt/jwt](https://github.com/golang-jwt/jwt) | Go; sucessor oficial do `dgrijalva/jwt-go` |
| **PASETO** | [github.com/paseto-standard/paseto-spec](https://github.com/paseto-standard/paseto-spec) | leia a **crítica ao JOSE** no README; é um bom argumento, bem escrito |
| **O [projeto-modelo](07-projeto-modelo/) deste curso** | aqui mesmo | ~350 linhas comentadas; todo o JWS sem caixa-preta |

---

## 95.7 · Ferramentas

| Ferramenta | Para quê | Link |
|---|---|---|
| **jwt.io** | inspecionar tokens (**nunca de produção**) | <https://jwt.io> |
| **jwt-cli** | decodificar e verificar **offline** | <https://github.com/mike-engel/jwt-cli> |
| **jwt_tool** | testar ataques conhecidos | <https://github.com/ticarpi/jwt_tool> |
| **hashcat** (modo 16500) | testar a força do **seu** segredo HMAC | <https://hashcat.net> |
| **Burp Suite + JWT Editor** | teste manual de aplicação | <https://portswigger.net> |
| **OpenSSL** | gerar, converter e inspecionar chaves | <https://www.openssl.org> |
| **mkjwk** | gerar JWK pelo navegador | <https://mkjwk.org> |
| **Keycloak** | IdP completo para laboratório | <https://www.keycloak.org> |
| **Suíte de conformidade OpenID** | testar a sua implementação OIDC | <https://openid.net/certification/> |

---

## 95.8 · Referências de segurança

| Recurso | O que é |
|---|---|
| [OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/) | as folhas de JWT, de sessão e de autenticação |
| [OWASP API Security Top 10](https://owasp.org/API-Security/) | API2:2023 é *Broken Authentication* |
| [**PortSwigger — JWT attacks**](https://portswigger.net/web-security/jwt) | ⭐ laboratórios interativos gratuitos |
| [NIST SP 800-63B](https://pages.nist.gov/800-63-3/sp800-63b.html) | diretrizes de autenticação digital: senhas, sessões, níveis de garantia |
| [NIST FIPS 204](https://csrc.nist.gov/pubs/fips/204/final) | ML-DSA — o padrão pós-quântico por trás da RFC 9964 |
| [CVE / NVD](https://nvd.nist.gov/) | busque por "JWT" periodicamente |

---

## 95.9 · Pessoas para acompanhar

Não é lista de influenciadores — são as pessoas que **escrevem os padrões e as
bibliotecas**.

| Pessoa | Papel | Onde |
|---|---|---|
| **Filip Skokan** | autor da `jose` e das bibliotecas OAuth de referência em JS | [github.com/panva](https://github.com/panva) |
| **Aaron Parecki** | coeditor do OAuth 2.1; autor de _OAuth 2.0 Simplified_ | [aaronparecki.com](https://aaronparecki.com) |
| **Mike Jones** | coautor das RFCs de JOSE e OIDC | [self-issued.info](https://self-issued.info/) |
| **Nat Sakimura** | coautor do JWT e do OIDC; presidente da OpenID Foundation | [sakimura.org](https://www.sakimura.org/) |
| **Justin Richer** | autor de RFCs do OAuth; autor de _OAuth 2 in Action_ | [justinsecurity.com](https://justinsecurity.com/) |
| **Neil Madden** | autor de _API Security in Action_ | [neilmadden.blog](https://neilmadden.blog/) |
| **Jean-Philippe Aumasson** | autor de _Serious Cryptography_; codesenhista do BLAKE3 | [aumasson.jp](https://aumasson.jp/) |
| **Daniel J. Bernstein** | Curve25519, Ed25519, ChaCha20 | [cr.yp.to](https://cr.yp.to/) |
| **Tim McLean** | o artigo de 2015 que definiu o assunto | [auth0.com/blog](https://auth0.com/blog/critical-vulnerabilities-in-json-web-token-libraries/) |

**O blog do Neil Madden** merece destaque: é o melhor material contínuo sobre
segurança de API e tokens que conheço, escrito por alguém que implementa e critica com
argumento.

---

## 95.10 · Grupos de trabalho do IETF

| Grupo | O que faz | Onde |
|---|---|---|
| **JOSE** | JWS, JWE, JWK, JWA e as extensões pós-quânticas | [datatracker.ietf.org/wg/jose/](https://datatracker.ietf.org/wg/jose/) |
| **OAUTH** | OAuth 2.x, DPoP, SD-JWT, Transaction Tokens | [datatracker.ietf.org/wg/oauth/](https://datatracker.ietf.org/wg/oauth/) |
| **COSE** | o equivalente ao JOSE em CBOR (IoT) | [datatracker.ietf.org/wg/cose/](https://datatracker.ietf.org/wg/cose/) |
| OpenID Foundation | OIDC, OpenID4VC, certificação | [openid.net](https://openid.net) |

As listas de discussão são públicas e arquivadas. Ler a discussão que originou uma
decisão de projeto é a forma mais direta de entender por que ela é como é — e é
exatamente onde busquei parte do que está em [11-historia.md](11-historia.md).

---

## 95.11 · Neste repositório

| Assunto | Relação com JWT |
|---|---|
| [apis](../apis/00-MAPA.md) | HTTP, REST, e o arquivo 16 é sobre segurança de API |
| [commits-assinados](../commits-assinados/00-MAPA.md) | assinatura digital, chaves, rotação — a mesma criptografia, outro uso |
| [ethical-hacking](../ethical-hacking/00-MAPA.md) | metodologia de teste de segurança |
| [docker](../docker/00-MAPA.md) | para subir Keycloak nos laboratórios |
| [postgresql](../postgresql/00-MAPA.md) | onde o refresh token e a lista de negação moram de verdade |
| [spa-single-page-application](../spa-single-page-application/00-MAPA.md) | o cliente que guarda o token |

---

## Autoteste

1. Qual é a RFC mais útil do assunto, e o que ela admite implicitamente?
2. Onde você confere se um nome de claim já é registrado?
3. Qual RFC define os tamanhos mínimos de chave, e em qual seção?
4. Qual RFC define `Authorization: Bearer` e o cabeçalho `WWW-Authenticate`?
5. Qual repositório vale ler para aprender JOSE lendo código?
6. O que a suíte de conformidade OpenID permite fazer de graça?
7. Cite três pessoas que escreveram tanto os padrões quanto as bibliotecas.
8. Onde encontrar a discussão que originou uma decisão de projeto do JWT?
