# JWT — mapa do assunto

> **O que é um JSON Web Token, como se usa, como funciona por dentro — e quando não
> usar.** Do "a internet esquece você a cada clique" até ML-DSA pós-quântica e o
> teorema informal da revogação.
>
> Produzido em 14/08/2026 · 29 documentos + projeto executável · ~12.900 linhas

---

## Em uma frase

Um JWT é um crachá que **diz coisas** e é **difícil de falsificar** — mas que
**qualquer um consegue ler**, e que **ninguém consegue pedir de volta** antes da hora.

Essas três características explicam tudo: por que ele escala, por que ele vaza dados,
e por que deslogar alguém dá trabalho.

---

## O que você saberá ao final

**Prático**

- ler, emitir e verificar tokens em cinco linguagens, e no terminal com `openssl`;
- montar autenticação completa: login, renovação, rotação, revogação, logout de
  verdade;
- escolher entre `HS256`, `ES256`, `RS256` e `EdDSA` com argumento, não por hábito;
- publicar JWKS e **rotacionar chave sem derrubar ninguém**;
- decidir onde guardar o token no navegador, no celular e na CLI;
- integrar com um provedor OIDC real (Keycloak, Auth0, Entra ID);
- auditar uma implementação alheia com um checklist de 30 itens.

**Conceitual**

- por que a assinatura cobre o texto base64 e não o JSON — e o padrão que sofreu por
  não fazer assim;
- por que o campo `alg` é o pecado original do formato, e por que ainda produz CVEs
  em 2026;
- por que "JWT é stateless" é a frase que levou milhares de equipes a escolher
  errado;
- a diferença exata entre assinar e cifrar, e por que você quase nunca precisa de
  JWE;
- por que um refresh token não deveria ser um JWT;
- **quando um cookie de sessão comum é a resposta certa** — e por que isso é a maior
  parte dos casos.

**De pesquisa**

- o enunciado formal de EUF-CMA e a cadeia de reduções do HS256, elo por elo;
- por que duas assinaturas ECDSA com o mesmo `k` entregam a chave privada, em duas
  divisões;
- o teorema informal da revogação, e por que ele é de teoria da informação;
- SD-JWT (RFC 9901) e o problema de correlação que ele **não** resolve;
- por que o tamanho da assinatura pós-quântica é uma ameaça estrutural ao JWT em
  cabeçalho HTTP.

---

## Roteiro de leitura

### Só preciso entender hoje (1 h)

```
01 → 04 (passos 1 e 2) → 75 (a lista de mitos)
```

### Vou implementar esta semana (1 a 2 dias)

```
01 → 02 → 03 → 04 → 07-projeto-modelo → 06 → 13 → 17 → 18 → 75
```

### Quero dominar (2 a 3 semanas)

```
Bloco A inteiro
  → 10 → 11 → 12 → 13 → 14 → 16 → 17 → 18 → 19 → 20 → 21 → 22
  → 70 (laboratórios 1 a 8) → 75
```

### Quero decidir a arquitetura do sistema

```
21 (leia primeiro) → 17 → 19 → 22 → 70 (laboratório 12) → 80
```

### Quero atacar e defender

```
12 → 14 → 20 → 70 (laboratórios 1, 3, 9) → PortSwigger Academy → 75
```

### Pesquisa

```
14 → 60 → 65 → 95 (as RFCs) → 70 (laboratório 11)
```

---

## Os documentos

### Bloco A · Porta de entrada

| # | Arquivo | O que tem | Nível |
|---|---|---|---|
| 01 | [introducao-leigo](01-introducao-leigo.md) | a analogia da pulseira do parque; por que a web esquece você | iniciante |
| 02 | [pre-requisitos](02-pre-requisitos.md) | o que saber antes, tempo realista, rota de resgate | iniciante |
| 03 | [instalacao](03-instalacao.md) | manual de campo: Node, Python, Java, Go, OpenSSL, `jwt-cli`, Docker, por SO; PATH, permissões, proxy, desinstalação, 13 erros literais | iniciante |
| 04 | [como-comecar](04-como-comecar.md) | fabricar um JWT à mão no terminal, quebrá-lo, e subir a API | iniciante |
| 05 | [manual-de-uso](05-manual-de-uso.md) | referência: claims, algoritmos, receitas, OpenSSL, status HTTP, 10 atalhos de quem usa há anos | todos |
| 06 | [exemplos](06-exemplos.md) | **14 exemplos completos**, em JS, Python, Java e Go, incluindo dois de produção | todos |
| 07 | [**projeto-modelo/**](07-projeto-modelo/README.md) | API de notas com JWS implementado do zero, **54 testes, zero dependências** | intermediário |

### Bloco B · Núcleo

| # | Arquivo | O que tem | Nível |
|---|---|---|---|
| 10 | [fundamentos](10-fundamentos.md) | por valor × por referência, a família JOSE, as três garantias e as três que faltam | iniciante |
| 11 | [historia](11-historia.md) | de SAML ao SD-JWT; março de 2015 e o pecado original do `alg` | intermediário |
| 12 | [anatomia-do-token](12-anatomia-do-token.md) | byte a byte, com medições; a ordem de validação correta | intermediário |
| 13 | [claims-registradas](13-claims-registradas.md) | semântica exata de cada claim e o erro que cada uma produz | intermediário |
| 14 | [assinatura-jws](14-assinatura-jws.md) | HMAC, RSA, ECDSA, EdDSA — a criptografia do zero | intermediário |
| 15 | [criptografia-jwe](15-criptografia-jwe.md) | quando cifrar o token — e por que quase nunca | avançado |
| 16 | [chaves-jwk-jwks](16-chaves-jwk-jwks.md) | JWK, JWKS, `kid` por thumbprint, rotação sem downtime | intermediário |
| 17 | [ciclo-de-vida-sessao](17-ciclo-de-vida-sessao.md) | dois tokens, rotação com detecção de reuso, logout de verdade | intermediário |
| 18 | [onde-guardar-no-cliente](18-onde-guardar-no-cliente.md) | `localStorage` × cookie: a pergunta certa e a resposta honesta | intermediário |
| 19 | [jwt-no-oauth-e-oidc](19-jwt-no-oauth-e-oidc.md) | os três tokens, PKCE, `state` × `nonce`, erros de integração | intermediário |
| 20 | [ataques-e-defesas](20-ataques-e-defesas.md) | `alg:none`, confusão de algoritmo, `kid`, `jku`, DoS — com as CVEs de 2026 | avançado |
| 21 | [**quando-nao-usar**](21-quando-nao-usar.md) | ⭐ o arquivo mais útil: quando o cookie de sessão vence | intermediário |
| 22 | [operacao-em-producao](22-operacao-em-producao.md) | relógio, métricas, runbook de plantão, resposta a incidente | avançado |
| 60 | [teoria-avancada](60-teoria-avancada.md) | EUF-CMA, reduções, o teorema da revogação, problemas em aberto | pesquisa |
| 65 | [estado-da-arte](65-estado-da-arte.md) | SD-JWT, DPoP, ML-DSA, Transaction Tokens — agosto de 2026 | pesquisa |

### Bloco C · Prática e erros

| # | Arquivo | O que tem |
|---|---|---|
| 70 | [pratica](70-pratica.md) | **12 laboratórios**, do "fabrique um token à mão" ao "implemente SD-JWT" |
| 75 | [armadilhas](75-armadilhas.md) | **25 armadilhas, 12 mitos**, cheiros de código e por que persistem |

### Bloco D · Economia e ecossistema

| # | Arquivo | O que tem |
|---|---|---|
| 80 | [custos-e-licencas](80-custos-e-licencas.md) | licenças, custo de implementar você mesmo, Auth0/Clerk/Cognito/Keycloak, custos ocultos — **preços de 14/08/2026** |
| 85 | [cursos-e-certificacoes](85-cursos-e-certificacoes.md) | cursos gratuitos em **PT, EN e FR**, certificações que valem, e uma trilha de 34 h por R$ 0,00 |

### Bloco E · Fontes

| # | Arquivo | O que tem |
|---|---|---|
| 90 | [bibliografia](90-bibliografia.md) | livros comentados, o que é legalmente gratuito, o que envelheceu |
| 95 | [referencias](95-referencias.md) | todas as RFCs, registros IANA, ferramentas, código e pessoas |
| — | [GLOSSARIO](GLOSSARIO.md) | ~130 termos definidos |

---

## O projeto-modelo

[`07-projeto-modelo/`](07-projeto-modelo/README.md) — **`cofre-de-notas`**: uma API de
notas pessoais com autenticação JWT completa, **sem uma única dependência externa**.

O JWS é implementado do zero em `src/jwt.js` (~250 linhas comentadas), de propósito:
não sobra caixa-preta nenhuma. Em produção, use `jose` — e o README diz isso em
negrito.

```bash
cd 07-projeto-modelo
node --test          # 54 testes, metade deles ATAQUES
node src/servidor.js
```

**O que ele exercita:** registro com scrypt · access token ES256 de 15 min ·
refresh opaco com rotação e detecção de reuso · lista de negação por `jti` ·
logout que mata as duas credenciais · JWKS público · rotação de chave por CLI ·
autorização por papel · 401 com `WWW-Authenticate` correto.

**Verificado em 14/08/2026:** 54/54 testes passando; fluxo completo exercitado com
`curl` real (registrar → login → rota protegida → refresh → reuso detectado → logout →
token revogado); rotação de chave executada. O teste de thumbprint reproduz o **vetor
oficial da RFC 7638**.

---

## As três frases que resumem o assunto

1. **Um JWT não esconde nada — ele só impede que alguém mude o que está escrito.**
2. **O token é autocontido; o sistema em volta dele não é.**
3. **A criptografia do JWT nunca foi quebrada; todos os ataques contornaram a
   criptografia.**

---

## Status

| Bloco | Situação |
|---|---|
| **A · Porta de entrada** | ✅ completo — instalação por SO com versões testadas, 14 exemplos, projeto executável |
| **B · Núcleo** | ✅ completo — 16 documentos, do 10 ao 65 |
| **C · Prática e erros** | ✅ completo — 12 laboratórios, 25 armadilhas, 12 mitos |
| **D · Economia e ecossistema** | ✅ completo — preços e cursos pesquisados na web em 14/08/2026 |
| **E · Fontes** | ✅ completo — RFCs, IANA, ferramentas, bibliografia comentada |
| **Glossário** | ✅ ~130 termos |

**Nada pendente de estrutura.**

**Reavaliar:** [65-estado-da-arte](65-estado-da-arte.md) e
[80-custos-e-licencas](80-custos-e-licencas.md) a cada seis meses;
[03-instalacao](03-instalacao.md) e [85-cursos-e-certificacoes](85-cursos-e-certificacoes.md)
a cada ano, ou quando sair uma CVE relevante de biblioteca JWT.

**Base de verificação:** Node v24.18.0 · Python 3.10.12 · OpenSSL 3.0.2 ·
OpenJDK 17.0.19 · Docker 29.1.3 · Ubuntu 22.04.5 LTS · `jose` 6.2.8 · PyJWT 2.13.0.
