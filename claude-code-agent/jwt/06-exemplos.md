# 6 · Exemplos — do trivial ao de produção

> Nível: iniciante a avançado · Atualizado em 14/08/2026
> Código completo e executável. Nenhum `...` escondendo parte essencial.
> Os exemplos 1–4 e 9 foram **executados e verificados** em 14/08/2026
> (Node v24.18.0 / `jose` 6.2.8; Python 3.10.12 / PyJWT 2.13.0).

Preparo comum para os exemplos em JavaScript:

```bash
mkdir -p ~/laboratorio-jwt && cd ~/laboratorio-jwt && npm init -y && npm install jose
```

---

## Índice

| # | Exemplo | Nível |
|---|---|---|
| [1](#1--o-mínimo-que-funciona-hs256) | O mínimo que funciona (HS256) | trivial |
| [2](#2--es256-com-kid-e-jwks) | ES256 com `kid` e JWKS publicado | básico |
| [3](#3--tratar-erros-por-tipo) | Tratar erros por tipo | básico |
| [4](#4--python--pyjwt-com-validação-estrita) | Python / PyJWT com validação estrita | básico |
| [5](#5--middleware-para-express) | Middleware para Express | intermediário |
| [6](#6--verificar-token-de-um-provedor-externo-keycloak-auth0-entra-id) | Verificar token de provedor externo (JWKS remoto) | intermediário |
| [7](#7--rotação-de-chave-sem-derrubar-ninguém) | Rotação de chave sem derrubar ninguém | intermediário |
| [8](#8--cliente-de-navegador-com-renovação-automática) | Cliente de navegador com renovação automática | intermediário |
| [9](#9--java--spring-boot-como-resource-server) | Java / Spring Boot como *resource server* | intermediário |
| [10](#10--go--middleware-nethttp) | Go / middleware `net/http` | intermediário |
| [11](#11--verificação-na-borda-cloudflare-worker) | Verificação na borda (Cloudflare Worker) | avançado |
| [12](#12--produção-link-de-redefinição-de-senha-de-uso-único) | **Produção:** link de redefinição de senha de uso único | avançado |
| [13](#13--produção-token-de-serviço-para-serviço-com-escopo-mínimo) | **Produção:** token serviço-a-serviço com escopo mínimo | avançado |
| [14](#14--testar-código-que-consome-jwt) | Testar código que consome JWT | avançado |

---

## 1 · O mínimo que funciona (HS256)

**Problema:** emitir e conferir um token quando quem assina e quem verifica são o
mesmo serviço.

```js
// arquivo: 01-hs256.mjs   —   rode com: node 01-hs256.mjs
import { SignJWT, jwtVerify } from 'jose';

// HS256 exige no mínimo 32 bytes de aleatoriedade real.
// Em produção: process.env.JWT_SECRET, gerado com `openssl rand -base64 32`.
const segredo = new TextEncoder().encode('um-segredo-de-32-bytes-no-minimo!');

const token = await new SignJWT({ papeis: ['usuario'] })
  .setProtectedHeader({ alg: 'HS256', typ: 'at+jwt' })
  .setIssuer('https://auth.exemplo.com')
  .setAudience('api-pedidos')
  .setSubject('u-42')
  .setIssuedAt()
  .setExpirationTime('15m')
  .setJti(crypto.randomUUID())
  .sign(segredo);

console.log('token:', token);

const { payload } = await jwtVerify(token, segredo, {
  algorithms: ['HS256'],                     // lista fechada — nunca omita
  issuer: 'https://auth.exemplo.com',
  audience: 'api-pedidos',
  typ: 'at+jwt',
});

console.log('sujeito:', payload.sub, '| papéis:', payload.papeis);
```

```
# saída verificada:
# token: eyJhbGciOiJIUzI1NiIsInR5cCI6ImF0K2p3dCJ9...
# sujeito: u-42 | papéis: [ 'usuario' ]
```

**Explicação.** `setProtectedHeader` é obrigatório e é onde vive o `alg`. Os
`set*` de claims são atalhos para `iss`, `aud`, `sub`, `iat`, `exp`, `jti` — as
claims registradas da [tabela A.1](05-manual-de-uso.md#a--claims). O
`.sign()` devolve o token pronto.

**A limitação deste exemplo:** o mesmo segredo assina e verifica. No dia em que um
segundo serviço precisar validar esses tokens, você terá de dar a ele o poder de
forjá-los. Por isso o exemplo 2 existe.

---

## 2 · ES256 com `kid` e JWKS

**Problema:** vários serviços precisam verificar tokens que só um serviço emite.

```js
// arquivo: 02-es256.mjs
import { SignJWT, jwtVerify, generateKeyPair, exportJWK, calculateJwkThumbprint } from 'jose';

// --- lado do EMISSOR --------------------------------------------------------
const { privateKey, publicKey } = await generateKeyPair('ES256', { extractable: true });

const jwkPublico = await exportJWK(publicKey);
const kid = await calculateJwkThumbprint(jwkPublico);   // RFC 7638

// Este documento é o que você publica em /.well-known/jwks.json.
// Repare: só a parte PÚBLICA. O componente `d` (privado) nunca aparece aqui.
const jwks = { keys: [{ ...jwkPublico, kid, use: 'sig', alg: 'ES256' }] };
console.log('JWKS publicado:', JSON.stringify(jwks, null, 2));

const token = await new SignJWT({ scope: 'leitura escrita' })
  .setProtectedHeader({ alg: 'ES256', kid, typ: 'at+jwt' })
  .setIssuer('https://auth.exemplo.com')
  .setAudience('api-pedidos')
  .setSubject('u-42')
  .setIssuedAt()
  .setExpirationTime('15m')
  .sign(privateKey);

// --- lado do CONSUMIDOR (outro serviço, que só tem o JWKS) ------------------
import { createLocalJWKSet } from 'jose';
const chaves = createLocalJWKSet(jwks);

const { payload, protectedHeader } = await jwtVerify(token, chaves, {
  algorithms: ['ES256'],
  issuer: 'https://auth.exemplo.com',
  audience: 'api-pedidos',
});

console.log('kid usado:', protectedHeader.kid);
console.log('escopo:', payload.scope);
```

```
# saída verificada (kid abreviado):
# kid usado: DwpJrCSSZQxb...
# escopo: leitura escrita
```

**Por que o `kid` vem de um *thumbprint*.** Ele é derivado da própria chave pública,
por SHA-256 de um JSON canônico. Duas equipes que nunca se falaram chegam ao mesmo
`kid` para a mesma chave. `kid: "chave-de-agosto"` obriga coordenação humana; o
thumbprint, não.

---

## 3 · Tratar erros por tipo

**Problema:** "token inválido" é uma resposta inútil. Expirado, assinatura errada e
audiência errada exigem reações diferentes.

```js
// arquivo: 03-erros.mjs
import { jwtVerify, errors } from 'jose';

export async function conferir(token, chave, opcoes) {
  try {
    const { payload } = await jwtVerify(token, chave, opcoes);
    return { ok: true, payload };
  } catch (e) {
    if (e instanceof errors.JWTExpired) {
      // Rotina. O cliente deve renovar e tentar de novo.
      return { ok: false, status: 401, codigo: 'expirado', renovavel: true };
    }
    if (e instanceof errors.JWTClaimValidationFailed) {
      // iss/aud/nbf errados. Renovar NÃO resolve — o token é de outro lugar.
      return { ok: false, status: 403, codigo: `claim_${e.claim}`, renovavel: false };
    }
    if (e instanceof errors.JWSSignatureVerificationFailed) {
      // Isto NÃO é rotina. Alguém está mandando token forjado.
      alertaDeSeguranca({ evento: 'assinatura_invalida' });
      return { ok: false, status: 401, codigo: 'assinatura_invalida', renovavel: false };
    }
    if (e instanceof errors.JWKSNoMatchingKey) {
      // kid desconhecido: ou a rotação de chave falhou, ou é ataque.
      return { ok: false, status: 401, codigo: 'kid_desconhecido', renovavel: false };
    }
    if (e instanceof errors.JWSInvalid || e instanceof errors.JWTInvalid) {
      return { ok: false, status: 400, codigo: 'malformado', renovavel: false };
    }
    throw e;
  }
}

function alertaDeSeguranca(evento) { console.warn('[SEGURANÇA]', evento); }
```

```
# saída verificada, para um token expirado:
# e instanceof errors.JWTExpired → true, e.code → ERR_JWT_EXPIRED
```

**A distinção que importa.** *Expirado* acontece milhares de vezes por dia e é
normal. *Assinatura inválida* quase nunca acontece por acidente — merece alerta,
porque significa que alguém está tentando forjar. Se os dois viram a mesma linha de
log, você perdeu o sinal no ruído.

---

## 4 · Python / PyJWT com validação estrita

**Problema:** o padrão do PyJWT é permissivo demais — um token **sem** `exp` passa.

```python
# arquivo: 04_pyjwt.py    —    rode com: python 04_pyjwt.py
# requer: pip install "PyJWT[crypto]>=2.13.0"
import jwt, time, uuid
from cryptography.hazmat.primitives.asymmetric import ec

chave_privada = ec.generate_private_key(ec.SECP256R1())
chave_publica = chave_privada.public_key()

agora = int(time.time())
token = jwt.encode(
    {
        "iss": "https://auth.exemplo.com",
        "sub": "u-42",
        "aud": "api-pedidos",
        "exp": agora + 900,
        "iat": agora,
        "jti": str(uuid.uuid4()),
        "papeis": ["usuario"],
    },
    chave_privada,
    algorithm="ES256",
    headers={"kid": "k1", "typ": "at+jwt"},
)

payload = jwt.decode(
    token,
    chave_publica,
    algorithms=["ES256"],          # sem isto, o PyJWT levanta erro — e faz bem
    issuer="https://auth.exemplo.com",
    audience="api-pedidos",
    leeway=60,
    # A linha mais importante do arquivo: exige a presença das claims.
    options={"require": ["exp", "iat", "iss", "aud", "sub"]},
)
print("ok:", payload["sub"], payload["papeis"])

# Demonstração: o algoritmo errado é recusado, não "adivinhado".
try:
    jwt.decode(token, chave_publica, algorithms=["HS256"], audience="api-pedidos")
except jwt.InvalidAlgorithmError as e:
    print("alg errado recusado:", type(e).__name__)
```

```
# saída verificada:
# ok: u-42 ['usuario']
# alg errado recusado: InvalidAlgorithmError
```

**A armadilha:** `pip install pyjwt` sem `[crypto]` instala uma versão que só faz
HMAC. Você descobre ao tentar ES256 e receber
`NotImplementedError: Algorithm 'ES256' could not be found`.

---

## 5 · Middleware para Express

**Problema:** proteger rotas sem repetir a verificação em cada handler.

```js
// arquivo: 05-middleware.mjs
// npm install express jose
import express from 'express';
import { jwtVerify, createRemoteJWKSet, errors } from 'jose';

// UMA vez por processo. Criar dentro do handler = uma chamada de rede por
// requisição, e um belo problema de latência que ninguém entende.
const jwks = createRemoteJWKSet(
  new URL('https://auth.exemplo.com/.well-known/jwks.json'),
  { cacheMaxAge: 600_000, cooldownDuration: 30_000 },
);

const OPCOES = {
  algorithms: ['ES256'],
  issuer: 'https://auth.exemplo.com',
  audience: 'api-pedidos',
  clockTolerance: '60s',
  typ: 'at+jwt',
};

function autenticar(req, res, proximo) {
  const casou = /^Bearer (\S+)$/i.exec(req.get('authorization') ?? '');
  if (!casou) {
    res.set('WWW-Authenticate', 'Bearer realm="api-pedidos"');
    return res.status(401).json({ erro: 'sem_credencial' });
  }
  jwtVerify(casou[1], jwks, OPCOES)
    .then(({ payload }) => { req.auth = payload; proximo(); })
    .catch((e) => {
      const expirou = e instanceof errors.JWTExpired;
      res.set('WWW-Authenticate',
        `Bearer error="invalid_token", error_description="${expirou ? 'expired' : 'invalid'}"`);
      res.status(401).json({ erro: expirou ? 'expirado' : 'token_invalido' });
    });
}

// Autorização por escopo — separada da autenticação, de propósito.
function exigirEscopo(escopo) {
  return (req, res, proximo) => {
    const tem = (req.auth?.scope ?? '').split(' ').includes(escopo);
    if (!tem) {
      res.set('WWW-Authenticate', `Bearer error="insufficient_scope", scope="${escopo}"`);
      return res.status(403).json({ erro: 'sem_permissao' });
    }
    proximo();
  };
}

const app = express();
app.use(express.json());

app.get('/pedidos', autenticar, exigirEscopo('leitura'), (req, res) => {
  res.json({ de: req.auth.sub, pedidos: [] });
});

app.post('/pedidos', autenticar, exigirEscopo('escrita'), (req, res) => {
  res.status(201).json({ id: crypto.randomUUID(), de: req.auth.sub });
});

app.listen(3000, () => console.log('ouvindo em :3000'));
```

**A decisão de projeto:** `autenticar` e `exigirEscopo` são middlewares separados
porque autenticação e autorização são perguntas diferentes. Misturar as duas gera
código em que "quem é você" e "o que você pode" ficam entrelaçados, e revisar a
política de acesso vira arqueologia.

---

## 6 · Verificar token de um provedor externo (Keycloak, Auth0, Entra ID)

**Problema:** sua API precisa aceitar tokens emitidos por um provedor que você não
controla.

```js
// arquivo: 06-provedor-externo.mjs
import { createRemoteJWKSet, jwtVerify } from 'jose';

/**
 * Descoberta automática: o provedor publica um documento de metadados em
 * /.well-known/openid-configuration com a URL do JWKS. Buscar de lá em vez de
 * codificar a URL evita quebrar quando o provedor a mudar.
 */
async function montarVerificador({ emissor, audiencia, algoritmos = ['RS256'] }) {
  const metadados = await fetch(`${emissor}/.well-known/openid-configuration`)
    .then((r) => r.json());

  // Trave o emissor no valor que o próprio provedor declara — e confira que ele
  // bate com o que você configurou. Se não bater, alguém apontou você para o
  // provedor errado.
  if (metadados.issuer !== emissor) {
    throw new Error(`emissor divergente: configurado ${emissor}, declarado ${metadados.issuer}`);
  }

  const jwks = createRemoteJWKSet(new URL(metadados.jwks_uri), {
    cacheMaxAge: 600_000,
    cooldownDuration: 30_000,
  });

  return async function verificar(token) {
    const { payload } = await jwtVerify(token, jwks, {
      algorithms: algoritmos,          // NÃO aceite o que vier; fixe a lista
      issuer: emissor,
      audience: audiencia,
      clockTolerance: '60s',
    });
    return payload;
  };
}

// Keycloak
const verificarKeycloak = await montarVerificador({
  emissor: 'https://kc.exemplo.com/realms/producao',
  audiencia: 'api-pedidos',
});

// Auth0
// const verificar = await montarVerificador({
//   emissor: 'https://sua-conta.us.auth0.com/', audiencia: 'https://api.exemplo.com',
// });

const payload = await verificarKeycloak(process.argv[2]);
console.log('sujeito:', payload.sub, '| escopos:', payload.scope);
console.log('papéis do realm:', payload.realm_access?.roles);
```

**Três detalhes que separam isto de um tutorial.**

1. A URL do JWKS vem da descoberta, não está codificada.
2. `algorithms` é fixado por você. Se o provedor um dia começar a emitir com outro
   algoritmo, você quer um erro alto e claro, não uma aceitação silenciosa.
3. O `issuer` do metadado é conferido contra o configurado — barra o caso de alguém
   apontar sua aplicação para um provedor falso via configuração.

---

## 7 · Rotação de chave sem derrubar ninguém

**Problema:** trocar a chave de assinatura com tokens vivos em circulação.

```js
// arquivo: 07-rotacao.mjs
import { SignJWT, jwtVerify, generateKeyPair, exportJWK, calculateJwkThumbprint, createLocalJWKSet } from 'jose';

class Chaveiro {
  #chaves = new Map();   // kid -> { privada, publica, jwk, criadaEm }
  #kidAtiva = null;

  async adicionar() {
    const { privateKey, publicKey } = await generateKeyPair('ES256', { extractable: true });
    const jwk = await exportJWK(publicKey);
    const kid = await calculateJwkThumbprint(jwk);
    this.#chaves.set(kid, { privada: privateKey, publica: publicKey, jwk, criadaEm: Date.now() });
    this.#kidAtiva = kid;
    return kid;
  }

  // O JWKS lista TODAS as chaves válidas para verificação, não só a ativa.
  // É isso que faz a rotação ser invisível para quem consome.
  jwks() {
    return { keys: [...this.#chaves].map(([kid, c]) => ({ ...c.jwk, kid, use: 'sig', alg: 'ES256' })) };
  }

  assinar(claims) {
    return new SignJWT(claims)
      .setProtectedHeader({ alg: 'ES256', kid: this.#kidAtiva, typ: 'at+jwt' })
      .setIssuer('https://auth.exemplo.com').setAudience('api')
      .setIssuedAt().setExpirationTime('15m')
      .sign(this.#chaves.get(this.#kidAtiva).privada);
  }

  // Só aposente depois de expirar o token mais longo assinado por ela.
  aposentar(kid) {
    if (kid === this.#kidAtiva) throw new Error('rotacione antes de aposentar a ativa');
    this.#chaves.delete(kid);
  }
}

// --- a sequência correta ----------------------------------------------------
const chaveiro = new Chaveiro();
const kidA = await chaveiro.adicionar();
const tokenComA = await chaveiro.assinar({ sub: 'u-1' });

// 1. Gere a chave nova e PUBLIQUE o JWKS com as duas.
const kidB = await chaveiro.adicionar();
//    Espere o cache dos consumidores expirar (o `cacheMaxAge` deles).
const tokenComB = await chaveiro.assinar({ sub: 'u-2' });

// 2. Agora ambos verificam:
const chaves = createLocalJWKSet(chaveiro.jwks());
const opcoes = { algorithms: ['ES256'], issuer: 'https://auth.exemplo.com', audience: 'api' };
console.log('token antigo (kid A):', (await jwtVerify(tokenComA, chaves, opcoes)).payload.sub);
console.log('token novo   (kid B):', (await jwtVerify(tokenComB, chaves, opcoes)).payload.sub);

// 3. Depois de 15 min (a vida do access token), aposente a A.
chaveiro.aposentar(kidA);
console.log('chaves restantes:', chaveiro.jwks().keys.length);
```

**A ordem importa e é contraintuitiva.** Publique a chave nova **antes** de começar a
assinar com ela. Se você inverter, tokens com um `kid` que ninguém conhece começam a
circular, o consumidor vai buscar o JWKS, e — se ele tiver proteção contra tempestade
de requisições, que deve ter — vai recusar tokens legítimos por alguns minutos.

**Erro clássico:** apagar a chave antiga no mesmo instante da troca. Todo token vivo
assinado por ela morre, e o suporte recebe uma onda de "fui deslogado do nada".

---

## 8 · Cliente de navegador com renovação automática

**Problema:** o access token expira no meio da sessão e a pessoa não pode perceber.

```js
// arquivo: cliente.js  (roda no navegador)
/**
 * Guarda o access token em MEMÓRIA — nunca em localStorage.
 * O refresh token vive num cookie HttpOnly que o JS não enxerga; é o navegador
 * que o envia sozinho para /auth/refresh. Ver 18-onde-guardar-no-cliente.md.
 */
let accessToken = null;
let renovacaoEmCurso = null;   // deduplica renovações concorrentes

async function renovar() {
  // Se dez requisições falharem ao mesmo tempo, todas esperam a MESMA renovação.
  // Sem isto, dez chamadas simultâneas a /auth/refresh disparam a detecção de
  // reuso do servidor e derrubam a sessão — um bug real, difícil de diagnosticar.
  renovacaoEmCurso ??= (async () => {
    try {
      const r = await fetch('/auth/refresh', { method: 'POST', credentials: 'include' });
      if (!r.ok) { accessToken = null; window.location.href = '/login'; return null; }
      accessToken = (await r.json()).access_token;
      return accessToken;
    } finally {
      renovacaoEmCurso = null;
    }
  })();
  return renovacaoEmCurso;
}

export async function api(caminho, opcoes = {}) {
  accessToken ??= await renovar();

  const chamar = () => fetch(caminho, {
    ...opcoes,
    credentials: 'same-origin',
    headers: { ...opcoes.headers, authorization: `Bearer ${accessToken}` },
  });

  let resposta = await chamar();

  // 401 → renove UMA vez e repita. 403 → não adianta renovar, é falta de permissão.
  if (resposta.status === 401) {
    accessToken = await renovar();
    if (!accessToken) return resposta;
    resposta = await chamar();
  }
  return resposta;
}
```

**Uso:**

```js
import { api } from './cliente.js';
const r = await api('/notas');
console.log(await r.json());
```

**As três decisões que fazem isto funcionar na vida real:**

1. **Token em memória**, não em `localStorage`: um XSS não consegue lê-lo do disco, e
   ele morre ao fechar a aba.
2. **Deduplicação da renovação**: sem ela, uma tela que dispara 10 chamadas em
   paralelo aciona a detecção de reuso do servidor e derruba a sessão da pessoa. Esse
   bug é sutil e aparece só em produção, quando a rede fica lenta.
3. **Só repete uma vez.** Repetir em laço num 401 permanente vira ataque de negação
   de serviço contra o próprio servidor.

---

## 9 · Java / Spring Boot como *resource server*

**Problema:** validar tokens de um provedor OIDC numa API Spring, sem escrever
criptografia.

```xml
<!-- pom.xml -->
<dependency>
  <groupId>org.springframework.boot</groupId>
  <artifactId>spring-boot-starter-oauth2-resource-server</artifactId>
</dependency>
```

```yaml
# application.yml
spring:
  security:
    oauth2:
      resourceserver:
        jwt:
          # O Spring busca o JWKS por descoberta e cuida do cache e da rotação.
          issuer-uri: https://kc.exemplo.com/realms/producao
          audiences: api-pedidos
```

```java
// SegurancaConfig.java
package com.exemplo.api;

import org.springframework.context.annotation.*;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.oauth2.server.resource.authentication.JwtAuthenticationConverter;
import org.springframework.security.oauth2.server.resource.authentication.JwtGrantedAuthoritiesConverter;

@Configuration
public class SegurancaConfig {

  @Bean
  SecurityFilterChain filtros(HttpSecurity http) throws Exception {
    http
      .authorizeHttpRequests(a -> a
        .requestMatchers("/saude", "/.well-known/**").permitAll()
        .requestMatchers("/pedidos/**").hasAuthority("SCOPE_leitura")
        .anyRequest().authenticated())
      // API sem sessão: nada de cookie de sessão do servlet, nada de CSRF token.
      .csrf(csrf -> csrf.disable())
      .oauth2ResourceServer(o -> o.jwt(j -> j.jwtAuthenticationConverter(conversor())));
    return http.build();
  }

  /** Converte a claim `scope` em autoridades SCOPE_*. */
  private JwtAuthenticationConverter conversor() {
    var escopos = new JwtGrantedAuthoritiesConverter();
    escopos.setAuthorityPrefix("SCOPE_");
    escopos.setAuthoritiesClaimName("scope");
    var conversor = new JwtAuthenticationConverter();
    conversor.setJwtGrantedAuthoritiesConverter(escopos);
    return conversor;
  }
}
```

```java
// PedidosController.java
package com.exemplo.api;

import org.springframework.web.bind.annotation.*;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.oauth2.jwt.Jwt;
import java.util.Map;

@RestController
public class PedidosController {
  @GetMapping("/pedidos")
  public Map<String, Object> listar(@AuthenticationPrincipal Jwt jwt) {
    return Map.of("de", jwt.getSubject(), "escopos", jwt.getClaimAsString("scope"));
  }
}
```

**O que o Spring faz por você aqui:** descoberta do JWKS, cache das chaves, rotação,
validação de `iss`/`aud`/`exp`/`nbf` e tolerância de relógio (30 s por padrão). Não
escreva isso à mão em Java — a configuração acima é auditada e você não vai fazer
melhor.

**Ressalva honesta:** `audiences` só passou a existir como propriedade nas versões
recentes do Spring Boot 3. Em versões mais antigas, é preciso registrar um
`OAuth2TokenValidator` manualmente. Verifique a versão que você usa.

---

## 10 · Go / middleware `net/http`

```go
// arquivo: main.go
// go mod init exemplo && go get github.com/golang-jwt/jwt/v5
package main

import (
	"context"
	"crypto/ecdsa"
	"fmt"
	"net/http"
	"strings"
	"time"

	"github.com/golang-jwt/jwt/v5"
)

type chaveContexto string

const claimsNoContexto chaveContexto = "claims"

func autenticar(publica *ecdsa.PublicKey, proximo http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		cabecalho := r.Header.Get("Authorization")
		if !strings.HasPrefix(cabecalho, "Bearer ") {
			w.Header().Set("WWW-Authenticate", `Bearer realm="api"`)
			http.Error(w, `{"erro":"sem_credencial"}`, http.StatusUnauthorized)
			return
		}

		token, err := jwt.Parse(
			strings.TrimPrefix(cabecalho, "Bearer "),
			func(t *jwt.Token) (interface{}, error) { return publica, nil },
			// Estas quatro opções são a diferença entre seguro e inseguro:
			jwt.WithValidMethods([]string{"ES256"}),          // lista fechada de alg
			jwt.WithIssuer("https://auth.exemplo.com"),
			jwt.WithAudience("api-pedidos"),
			jwt.WithExpirationRequired(),                      // recusa token sem exp
			jwt.WithLeeway(60*time.Second),
		)
		if err != nil {
			w.Header().Set("WWW-Authenticate", `Bearer error="invalid_token"`)
			http.Error(w, fmt.Sprintf(`{"erro":%q}`, err.Error()), http.StatusUnauthorized)
			return
		}

		claims := token.Claims.(jwt.MapClaims)
		proximo.ServeHTTP(w, r.WithContext(context.WithValue(r.Context(), claimsNoContexto, claims)))
	})
}

func pedidos(w http.ResponseWriter, r *http.Request) {
	claims := r.Context().Value(claimsNoContexto).(jwt.MapClaims)
	fmt.Fprintf(w, `{"de":%q}`, claims["sub"])
}

func main() {
	var publica *ecdsa.PublicKey // carregue de arquivo ou do JWKS
	mux := http.NewServeMux()
	mux.Handle("/pedidos", autenticar(publica, http.HandlerFunc(pedidos)))
	http.ListenAndServe(":3000", mux)
}
```

> `jwt.WithValidMethods` **não é opcional**. Sem ela, a função de resolução de chave
> é chamada para qualquer `alg` que o token declarar, e você reabre a confusão de
> algoritmo. `jwt.WithExpirationRequired()` foi acrescentada na v5 justamente porque
> tokens sem `exp` passavam antes.

---

## 11 · Verificação na borda (Cloudflare Worker)

**Problema:** rejeitar token inválido antes que a requisição chegue ao seu servidor.

```js
// arquivo: worker.js  —  Cloudflare Workers / Deno Deploy / Vercel Edge
// A `jose` funciona aqui porque usa Web Crypto, não as APIs do Node.
// É exatamente por isso que ela substituiu a `jsonwebtoken` no mundo edge.
import { createRemoteJWKSet, jwtVerify } from 'jose';

let jwks;  // reaproveitado entre requisições no mesmo isolate — cache de graça

export default {
  async fetch(requisicao, ambiente) {
    jwks ??= createRemoteJWKSet(new URL(ambiente.JWKS_URL), { cacheMaxAge: 600_000 });

    const casou = /^Bearer (\S+)$/i.exec(requisicao.headers.get('authorization') ?? '');
    if (!casou) return json(401, { erro: 'sem_credencial' });

    let payload;
    try {
      ({ payload } = await jwtVerify(casou[1], jwks, {
        algorithms: ['ES256'],
        issuer: ambiente.EMISSOR,
        audience: ambiente.AUDIENCIA,
        clockTolerance: '60s',
      }));
    } catch {
      return json(401, { erro: 'token_invalido' });
    }

    // Repassa a identidade JÁ VERIFICADA à origem, e REMOVE o cabeçalho original
    // para que a origem não possa ser enganada por um Authorization forjado.
    const paraOrigem = new Request(requisicao);
    paraOrigem.headers.delete('authorization');
    paraOrigem.headers.set('x-usuario-id', payload.sub);
    paraOrigem.headers.set('x-usuario-escopos', payload.scope ?? '');

    return fetch(paraOrigem);
  },
};

const json = (status, corpo) =>
  new Response(JSON.stringify(corpo), { status, headers: { 'content-type': 'application/json' } });
```

> ⚠️ **O risco deste padrão:** a origem passa a confiar em `x-usuario-id`. Se alguém
> alcançar a origem sem passar pela borda, forja o cabeçalho e vira quem quiser. A
> origem **precisa** estar inacessível diretamente — por rede privada, por mTLS, ou
> por um segredo compartilhado que só a borda conhece. Já vi esse erro custar caro:
> uma migração de infraestrutura expôs a origem, e a autenticação inteira virou
> "escreva seu ID num cabeçalho".

---

## 12 · Produção: link de redefinição de senha de uso único

**Problema real:** o link vai por e-mail — um canal que não é seguro, fica no
histórico, é indexado por scanners corporativos e sobrevive em backups.

```js
// arquivo: 12-redefinir-senha.mjs
import { SignJWT, jwtVerify, errors } from 'jose';
import { createHash, randomUUID } from 'node:crypto';

const SEGREDO = new TextEncoder().encode(process.env.RESET_SECRET); // 32+ bytes

/**
 * Três defesas empilhadas, porque o canal (e-mail) é hostil:
 *
 *  1. `typ: "reset+jwt"` — este token não é aceito em nenhuma outra rota.
 *  2. `exp` de 15 minutos — janela curta.
 *  3. `svc` = hash do estado atual da senha. Assim que a senha muda, o hash
 *     muda, e o token deixa de valer AUTOMATICAMENTE. É o que torna o link de
 *     uso único sem precisar de tabela de tokens usados.
 */
function selo(usuario) {
  return createHash('sha256')
    .update(`${usuario.id}:${usuario.hashDaSenha}:${usuario.senhaAlteradaEm}`)
    .digest('base64url')
    .slice(0, 16);
}

export async function gerarLink(usuario, baseUrl) {
  const token = await new SignJWT({ svc: selo(usuario) })
    .setProtectedHeader({ alg: 'HS256', typ: 'reset+jwt' })
    .setIssuer('https://auth.exemplo.com')
    .setAudience('redefinicao-de-senha')
    .setSubject(usuario.id)
    .setIssuedAt()
    .setExpirationTime('15m')
    .setJti(randomUUID())
    .sign(SEGREDO);

  return `${baseUrl}/redefinir?t=${encodeURIComponent(token)}`;
}

export async function consumirLink(token, buscarUsuario) {
  let payload;
  try {
    ({ payload } = await jwtVerify(token, SEGREDO, {
      algorithms: ['HS256'],
      issuer: 'https://auth.exemplo.com',
      audience: 'redefinicao-de-senha',
      typ: 'reset+jwt',
      clockTolerance: '30s',
    }));
  } catch (e) {
    // Mensagem genérica de propósito: não conte ao atacante o que falhou.
    const codigo = e instanceof errors.JWTExpired ? 'link_expirado' : 'link_invalido';
    throw Object.assign(new Error(codigo), { codigo, status: 400 });
  }

  const usuario = await buscarUsuario(payload.sub);
  if (!usuario) throw Object.assign(new Error('link_invalido'), { status: 400 });

  // Aqui está o uso único: se a senha já mudou (por este link ou por outro
  // caminho), o selo não bate mais.
  if (selo(usuario) !== payload.svc) {
    throw Object.assign(new Error('link_ja_utilizado'), { codigo: 'link_ja_utilizado', status: 400 });
  }

  return usuario;
}
```

**Por que o `svc` e não uma tabela de tokens usados?** Uma tabela funciona e é
legítima. O `svc` resolve o mesmo problema sem estado novo, e resolve **de graça** um
caso que a tabela não cobre: se a pessoa trocar a senha por outro caminho (pelo
próprio painel), todos os links de redefinição pendentes morrem no mesmo instante.

**O que este exemplo tem de produção e os tutoriais não têm:** mensagem de erro
genérica, `typ` próprio, prazo curto, e invalidação automática. Um link de
redefinição com validade de 24 horas e sem uso único é uma das falhas mais comuns em
auditoria de aplicação web.

---

## 13 · Produção: token serviço-a-serviço com escopo mínimo

**Problema real:** o serviço de relatórios precisa ler pedidos. Dar a ele o token de
um usuário é errado (ele age em nome próprio) e dar um token eterno é pior.

```js
// arquivo: 13-servico-a-servico.mjs
import { SignJWT, jwtVerify, importPKCS8, importSPKI } from 'jose';
import { readFileSync } from 'node:fs';

/**
 * Padrão *client credentials* simplificado: o serviço se autentica com a
 * própria chave privada e recebe um token de vida curta, com escopo mínimo.
 *
 * Por que não uma chave de API eterna em variável de ambiente:
 *  - ela nunca expira, então vazamento é permanente até alguém perceber;
 *  - ela é a mesma em todos os ambientes, na prática;
 *  - ela não carrega escopo, então vaza acesso total;
 *  - ela aparece em `docker inspect`, em crash dump e em log de deploy.
 */
export class EmissorDeServico {
  #privada; #kid; #cache = new Map();

  static async criar({ caminhoChave, kid }) {
    const emissor = new EmissorDeServico();
    emissor.#privada = await importPKCS8(readFileSync(caminhoChave, 'utf8'), 'ES256');
    emissor.#kid = kid;
    return emissor;
  }

  /**
   * Cacheia o token e o reemite ANTES de expirar (aos 80% da vida). Sem essa
   * margem, uma requisição pega o token no último segundo, o relógio do outro
   * lado está 2 s adiantado, e você tem um 401 intermitente que ninguém
   * consegue reproduzir.
   */
  async tokenPara(destino, escopo) {
    const chaveCache = `${destino}|${escopo}`;
    const agora = Math.floor(Date.now() / 1000);
    const guardado = this.#cache.get(chaveCache);
    if (guardado && guardado.renovarEm > agora) return guardado.token;

    const vida = 300;                       // 5 minutos: curto de propósito
    const token = await new SignJWT({ scope: escopo })
      .setProtectedHeader({ alg: 'ES256', kid: this.#kid, typ: 'at+jwt' })
      .setIssuer('https://servico-relatorios.interno')
      .setAudience(destino)                 // um token por destino, não um coringa
      .setSubject('servico-relatorios')
      .setIssuedAt()
      .setExpirationTime(agora + vida)
      .sign(this.#privada);

    this.#cache.set(chaveCache, { token, renovarEm: agora + Math.floor(vida * 0.8) });
    return token;
  }
}

// --- lado de quem recebe ----------------------------------------------------
export async function verificadorDeServico({ caminhoChavePublica, minhaAudiencia }) {
  const publica = await importSPKI(readFileSync(caminhoChavePublica, 'utf8'), 'ES256');

  // Lista explícita de quem pode falar comigo e com qual escopo. Este mapa é o
  // documento de arquitetura mais útil que o sistema tem — e ele é código.
  const PERMITIDOS = {
    'servico-relatorios': ['pedidos:leitura'],
    'servico-faturamento': ['pedidos:leitura', 'pedidos:escrita'],
  };

  return async function verificar(token, escopoNecessario) {
    const { payload } = await jwtVerify(token, publica, {
      algorithms: ['ES256'],
      issuer: 'https://servico-relatorios.interno',
      audience: minhaAudiencia,
      clockTolerance: '30s',
      maxTokenAge: '10m',                    // barra token antigo repetido
    });

    const permitidos = PERMITIDOS[payload.sub] ?? [];
    if (!permitidos.includes(escopoNecessario)) {
      throw new Error(`servico ${payload.sub} nao tem ${escopoNecessario}`);
    }
    if (!(payload.scope ?? '').split(' ').includes(escopoNecessario)) {
      throw new Error(`token nao pediu o escopo ${escopoNecessario}`);
    }
    return payload;
  };
}
```

**Uso:**

```js
const emissor = await EmissorDeServico.criar({ caminhoChave: '/segredos/relatorios.pem', kid: 'rel-1' });
const token = await emissor.tokenPara('api-pedidos', 'pedidos:leitura');
await fetch('https://api-pedidos.interno/pedidos', {
  headers: { authorization: `Bearer ${token}` },
});
```

**A dupla verificação de escopo** — o que o serviço *pode* (a lista `PERMITIDOS`) e o
que ele *pediu* (a claim `scope`) — não é redundância. Ela implementa privilégio
mínimo: mesmo um serviço autorizado a escrever só consegue escrever se pediu esse
escopo naquele token. Se a chave dele vazar, o estrago fica limitado ao que os tokens
em circulação pediram.

---

## 14 · Testar código que consome JWT

**Problema:** testar rota protegida sem depender do provedor de identidade real.

```js
// arquivo: test/auxiliares.mjs
import { SignJWT, generateKeyPair, exportJWK, calculateJwkThumbprint, createLocalJWKSet } from 'jose';

/**
 * Fábrica de tokens para teste. O ponto: use um JWKS LOCAL, não a rede.
 * Um teste que bate no provedor real é lento, intermitente e falha quando a
 * rede cai — e você não pode emitir token expirado no provedor real de
 * propósito, que é justamente o caso que você mais precisa testar.
 */
export async function fabricaDeTokens({
  emissor = 'https://auth.teste',
  audiencia = 'api-teste',
} = {}) {
  const { privateKey, publicKey } = await generateKeyPair('ES256', { extractable: true });
  const jwk = await exportJWK(publicKey);
  const kid = await calculateJwkThumbprint(jwk);
  const jwks = { keys: [{ ...jwk, kid, use: 'sig', alg: 'ES256' }] };

  return {
    jwks,
    chaves: createLocalJWKSet(jwks),
    async emitir({ sub = 'u-teste', scope = 'leitura', vida = 900, ...extra } = {}) {
      const agora = Math.floor(Date.now() / 1000);
      return new SignJWT({ scope, ...extra })
        .setProtectedHeader({ alg: 'ES256', kid, typ: 'at+jwt' })
        .setIssuer(emissor).setAudience(audiencia).setSubject(sub)
        .setIssuedAt(agora).setExpirationTime(agora + vida)
        .sign(privateKey);
    },
    // Os casos que você NÃO consegue produzir no provedor real:
    async emitirExpirado(opcoes) { return this.emitir({ ...opcoes, vida: -60 }); },
    async emitirDeOutraAudiencia(opcoes) {
      const agora = Math.floor(Date.now() / 1000);
      return new SignJWT({ scope: 'leitura', ...opcoes })
        .setProtectedHeader({ alg: 'ES256', kid })
        .setIssuer(emissor).setAudience('outra-api').setSubject('u-teste')
        .setIssuedAt(agora).setExpirationTime(agora + 900)
        .sign(privateKey);
    },
    async emitirDeChaveErrada(opcoes) {
      const outra = await generateKeyPair('ES256', { extractable: true });
      const agora = Math.floor(Date.now() / 1000);
      return new SignJWT({ scope: 'leitura', ...opcoes })
        .setProtectedHeader({ alg: 'ES256', kid })   // mesmo kid, chave diferente!
        .setIssuer(emissor).setAudience(audiencia).setSubject('u-teste')
        .setIssuedAt(agora).setExpirationTime(agora + 900)
        .sign(outra.privateKey);
    },
  };
}
```

```js
// arquivo: test/rotas.test.mjs
import { test, before } from 'node:test';
import assert from 'node:assert/strict';
import { fabricaDeTokens } from './auxiliares.mjs';

let fabrica;
before(async () => { fabrica = await fabricaDeTokens(); });

test('aceita token válido', async () => {
  const r = await chamarApi('/pedidos', await fabrica.emitir());
  assert.equal(r.status, 200);
});

test('recusa token expirado', async () => {
  const r = await chamarApi('/pedidos', await fabrica.emitirExpirado());
  assert.equal(r.status, 401);
});

test('recusa token de outra audiência', async () => {
  const r = await chamarApi('/pedidos', await fabrica.emitirDeOutraAudiencia());
  assert.equal(r.status, 401);
});

test('recusa token assinado por outra chave com o mesmo kid', async () => {
  const r = await chamarApi('/pedidos', await fabrica.emitirDeChaveErrada());
  assert.equal(r.status, 401);
});

test('recusa escopo insuficiente com 403, não 401', async () => {
  const r = await chamarApi('/pedidos', await fabrica.emitir({ scope: 'nada' }), 'POST');
  assert.equal(r.status, 403);   // 401 aqui causaria laço de renovação no cliente
});
```

**A regra:** os testes que importam são os que produzem tokens que o provedor real
**nunca** emitiria — expirado, de outra audiência, assinado pela chave errada. É
neles que os bugs de autenticação moram. Um teste que só usa o token feliz não prova
nada além de que a biblioteca funciona.

---

## Autoteste

1. No exemplo 2, por que o `kid` é um *thumbprint* e não uma data?
2. Por que `createRemoteJWKSet` deve ser criado uma vez por processo?
3. No exemplo 7, qual é a ordem correta de rotação, e o que quebra se você inverter?
4. No exemplo 8, o que acontece se você remover a deduplicação de renovação e a tela
   disparar 10 chamadas paralelas?
5. No exemplo 11, qual é o risco de repassar `x-usuario-id` à origem, e como se
   protege contra ele?
6. No exemplo 12, o que o `svc` faz que uma tabela de tokens usados não faz?
7. No exemplo 13, por que verificar duas vezes o escopo (a lista de permitidos e a
   claim `scope`) não é redundância?
8. Cite três tokens que só uma fábrica de teste consegue produzir, e por que testá-los
   é mais importante que testar o caminho feliz.
