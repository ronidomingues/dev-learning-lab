# 11 · Segurança

**Nível: avançado** · Pré-requisitos: `02`, `06`, `08`.

O princípio que organiza todo este arquivo, e que precisa ser interiorizado antes de qualquer técnica:

> **O cliente é território hostil.** Todo o código que você envia ao navegador é público, modificável e executável por qualquer pessoa. Todo dado que chega ao seu servidor vindo do cliente é potencialmente forjado. Nenhuma verificação feita no JavaScript conta como segurança — ela é experiência de usuário.

---

## 1. XSS — Cross-Site Scripting

A vulnerabilidade número um de aplicações web, e a mais grave numa SPA: um script injetado roda **com todos os privilégios da sua aplicação**.

### As três variantes

| Tipo | Origem | Exemplo |
|---|---|---|
| **Refletido** | vem na URL e volta na resposta | `?busca=<script>…` ecoado na tela |
| **Armazenado** | persistido no banco, servido a todos | comentário com script; o pior dos três |
| **Baseado em DOM** | o cliente escreve dado não confiável no DOM | `el.innerHTML = location.hash` |

Em SPAs, o tipo **DOM** é o dominante, porque toda a renderização acontece no cliente.

### Como acontece

```js
// TODAS exploráveis
el.innerHTML = dadoDoUsuario;
el.outerHTML = dadoDoUsuario;
document.write(dadoDoUsuario);
eval(dadoDoUsuario);
new Function(dadoDoUsuario)();
elemento.setAttribute('onclick', dadoDoUsuario);
location.href = dadoDoUsuario;          // javascript:alert(1)
```

```jsx
// React: seguro por padrão — escapa tudo em {}
<p>{dadoDoUsuario}</p>

// exceto aqui — o nome longo é um aviso deliberado dos autores
<div dangerouslySetInnerHTML={{ __html: dadoDoUsuario }} />
```

### Defesas, em camadas

**1. Não construa HTML por concatenação.** Use `textContent`, não `innerHTML`:

```js
el.textContent = dadoDoUsuario;   // sempre seguro: nunca interpreta como markup
```

**2. Se precisar de HTML rico, sanitize** — com uma biblioteca testada, jamais com regex própria:

```js
import DOMPurify from 'dompurify';
el.innerHTML = DOMPurify.sanitize(html, {
  ALLOWED_TAGS: ['b','i','em','strong','a','p','ul','ol','li','code'],
  ALLOWED_ATTR: ['href','title'],
});
```

Filtro de blacklist artesanal **sempre** falha. Há décadas de bypasses conhecidos: entidades HTML, codificação dupla, `<svg onload>`, `<img src=x onerror>`, mutation XSS. Não tente.

**3. Valide URLs antes de usá-las:**

```js
function urlSegura(u) {
  try {
    const url = new URL(u, location.origin);
    return ['http:', 'https:', 'mailto:'].includes(url.protocol) ? url.href : '#';
  } catch { return '#'; }
}
// bloqueia javascript:, data:, vbscript:
```

**4. Content Security Policy — a rede de proteção**

```http
Content-Security-Policy:
  default-src 'self';
  script-src 'self' 'nonce-r4nd0m123';
  style-src 'self' 'nonce-r4nd0m123';
  img-src 'self' data: https:;
  connect-src 'self' https://api.exemplo.com;
  frame-ancestors 'none';
  base-uri 'self';
  object-src 'none';
  require-trusted-types-for 'script';
```

```html
<script nonce="r4nd0m123">/* só executa com o nonce da requisição */</script>
```

Pontos que decidem se a CSP serve para algo:

- **O nonce precisa ser aleatório por requisição.** Um nonce fixo não protege nada.
- **`'unsafe-inline'` anula a proteção de script.** É o mais comum e o mais fatal dos erros de CSP.
- **`'strict-dynamic'`** é o caminho prático para SPAs com carregamento dinâmico de chunks: scripts carregados por um script confiável herdam a confiança.
- **`frame-ancestors 'none'`** previne clickjacking (substitui `X-Frame-Options`).
- Implante primeiro em **`Content-Security-Policy-Report-Only`** com `report-to`, colete violações por algumas semanas, e só então aplique.

**5. Trusted Types** — a defesa estrutural mais forte contra DOM XSS, disponível em navegadores Chromium:

```js
const politica = trustedTypes.createPolicy('padrao', {
  createHTML: (s) => DOMPurify.sanitize(s),
});
el.innerHTML = politica.createHTML(entrada);   // atribuir string crua passa a lançar erro
```

Com `require-trusted-types-for 'script'`, o navegador **proíbe** atribuir strings comuns a `innerHTML`. Isso transforma uma classe inteira de vulnerabilidades em erro de execução detectável.

---

## 2. Onde guardar o token — a decisão mais consequente

Este é o ponto onde mais gente erra, e o erro é sempre o mesmo.

| Local | XSS lê? | Enviado automaticamente? | Veredito |
|---|---|---|---|
| `localStorage` | **sim, trivialmente** | não | ❌ evite |
| `sessionStorage` | **sim** | não | ❌ evite |
| Variável JS em memória | sim, se o script alcançar o escopo | não | ⚠️ aceitável para access token curto |
| Cookie `HttpOnly` + `Secure` + `SameSite` | **não** | sim | ✅ recomendado |

```http
Set-Cookie: sessao=abc; HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=3600
```

- `HttpOnly` — invisível ao JavaScript. É isto que derrota o roubo por XSS.
- `Secure` — só sobre HTTPS.
- `SameSite=Lax` — não é enviado em requisições cross-site, o que já mitiga a maior parte do CSRF. Use `Strict` para operações sensíveis; `None` (com `Secure`) só se você realmente precisar de cross-site.
- `__Host-` como prefixo do nome adiciona garantias extras (path `/`, sem `Domain`, obrigatoriamente `Secure`).

> **O argumento "localStorage é seguro se você não tiver XSS" está invertido.** Defesa em profundidade existe justamente porque você vai ter um XSS um dia — numa dependência transitiva, num trecho antigo, num componente de terceiro. Com `HttpOnly`, o XSS ainda é grave (o atacante pode agir *como* o usuário enquanto a página está aberta), mas ele **não sai com o token no bolso** para usar depois, de outro lugar, indefinidamente. A diferença entre um incidente contido e uma conta comprometida por semanas.

**Padrão híbrido**, comum em arquiteturas com API separada: access token de curta duração (5–15 min) em memória, refresh token em cookie `HttpOnly`. Ao recarregar a página, o cliente chama `/refresh` (o cookie vai sozinho) e recebe um novo access token que nunca toca o disco.

E cuide da concorrência do refresh — sem isso, dez requisições que recebem 401 ao mesmo tempo disparam dez refreshes:

```js
let refreshEmVoo = null;

async function comAuth(req) {
  let r = await req(acessoAtual);
  if (r.status === 401) {
    refreshEmVoo ??= fetch('/auth/refresh', { method: 'POST', credentials: 'include' })
      .then(x => x.json())
      .finally(() => { refreshEmVoo = null; });
    acessoAtual = (await refreshEmVoo).access;
    r = await req(acessoAtual);      // uma única retentativa
  }
  return r;
}
```

---

## 3. CSRF — Cross-Site Request Forgery

Um site malicioso faz o navegador do usuário enviar uma requisição autenticada ao seu servidor, aproveitando que os cookies vão automaticamente.

```html
<!-- em site-malvado.com, com o usuário logado no seu banco -->
<form action="https://banco.com/transferir" method="POST">
  <input name="para" value="atacante"><input name="valor" value="10000">
</form><script>document.forms[0].submit()</script>
```

**Só se aplica quando a autenticação é por cookie.** Se você manda o token num header `Authorization`, não há CSRF — o navegador não adiciona esse header sozinho.

Defesas, use pelo menos as duas primeiras:

1. **`SameSite=Lax` ou `Strict`** — padrão nos navegadores modernos; resolve a maior parte dos casos.
2. **Token anti-CSRF** — valor imprevisível em cada formulário/requisição de escrita, validado no servidor. O padrão *double submit cookie* é o mais simples de implementar em SPA.
3. **Verificar `Origin`/`Sec-Fetch-Site`** nas requisições de escrita.
4. **Nunca use `GET` para mutar estado.** Um `<img src="/deletar?id=5">` basta para explorar isso.

---

## 4. CORS — entendendo o que ele é e não é

CORS é frequentemente mal compreendido. Ele **não protege seu servidor**. Ele é o mecanismo pelo qual o navegador **relaxa** a Same-Origin Policy, permitindo que uma origem leia respostas de outra.

```http
Access-Control-Allow-Origin: https://app.exemplo.com
Access-Control-Allow-Credentials: true
Access-Control-Allow-Methods: GET, POST, PATCH, DELETE
Access-Control-Allow-Headers: Content-Type, Authorization
Access-Control-Max-Age: 86400
```

Erros graves e comuns:

```http
Access-Control-Allow-Origin: *                    # nunca com dados autenticados
Access-Control-Allow-Origin: null                  # explorável
```

Refletir a origem recebida sem validar contra uma lista permitida equivale a `*`. E lembre: `curl` ignora CORS por completo — **a autorização de verdade acontece no servidor, sempre.**

---

## 5. Autenticação: OAuth 2.0 e OIDC

Para SPAs, o fluxo correto em 2026 é **Authorization Code + PKCE**. O fluxo implícito (`response_type=token`) está **obsoleto** — ele expunha tokens na URL, onde vazam em logs, no histórico e no header `Referer`.

```
1. Cliente gera verificador aleatório e seu desafio SHA-256
2. Redireciona para o provedor com code_challenge, state e nonce
3. Usuário autentica
4. Provedor devolve um code na URL de retorno
5. Cliente troca code + code_verifier por tokens (o code sozinho é inútil sem o verificador)
```

```js
const verificador = base64url(crypto.getRandomValues(new Uint8Array(32)));
const desafio = base64url(await crypto.subtle.digest('SHA-256', new TextEncoder().encode(verificador)));
sessionStorage.setItem('pkce', verificador);        // efêmero, por aba
sessionStorage.setItem('state', estadoAleatorio);   // valide na volta: previne CSRF de login
```

O que checar sempre:

- **Valide o `state`** na volta. Sem isso, há CSRF no fluxo de login.
- **Valide o `nonce`** dentro do ID token.
- **Valide a assinatura, o `iss`, o `aud` e o `exp`** do JWT — **no servidor**. Decodificar um JWT no cliente serve para exibir o nome do usuário, nunca para autorizar.
- **Use a Refresh Token Rotation**, com detecção de reuso: se um refresh token já usado reaparecer, revogue a família inteira. É a defesa contra token roubado.

**Padrão BFF (Backend for Frontend)** — a recomendação mais robusta hoje quando você controla o backend: o SPA nunca vê token nenhum. Ele fala com um backend próprio via cookie de sessão `HttpOnly`, e esse backend guarda os tokens OAuth e fala com as APIs. Elimina de uma vez o problema de armazenamento de token no navegador.

---

## 6. Autorização

```js
// Cliente: EXPERIÊNCIA DE USUÁRIO. Evita mostrar o que falharia.
{usuario.papeis.includes('admin') && <BotaoExcluir />}
```

```js
// Servidor: SEGURANÇA. Obrigatório, em toda requisição, sem exceção.
app.delete('/api/produtos/:id', async (req, res) => {
  const u = await autenticar(req);                      // quem é
  if (!u) return res.status(401).end();
  if (!podeExcluir(u, req.params.id)) return res.status(403).end();   // pode?
  // …
});
```

Falhas de autorização (IDOR — *Insecure Direct Object Reference*) são a categoria mais comum em aplicações reais, e a mais fácil de introduzir numa SPA: o desenvolvedor esconde o botão e esquece de verificar no endpoint.

```js
// VULNERÁVEL: qualquer usuário lê o pedido de qualquer outro
app.get('/api/pedidos/:id', async (req, res) => res.json(await db.pedido.find(req.params.id)));

// CORRETO: o escopo do dono faz parte da consulta
app.get('/api/pedidos/:id', async (req, res) => {
  const p = await db.pedido.findFirst({ where: { id: req.params.id, usuarioId: req.usuario.id } });
  if (!p) return res.status(404).end();     // 404, não 403: não revela existência
  res.json(p);
});
```

E **filtre os campos na saída**. Devolver o objeto do banco inteiro vaza `senhaHash`, `stripeCustomerId`, `notasInternas`. Use um serializador explícito, nunca `res.json(entidadeDoBanco)`.

---

## 7. A cadeia de suprimentos

Uma SPA típica tem centenas a milhares de dependências transitivas. Cada uma executa com os mesmos privilégios do seu código. Incidentes reais — `event-stream`, `ua-parser-js`, `node-ipc`, os ataques de typosquatting e as ondas de comprometimento de tokens de mantenedores — mostraram que este é um vetor ativo, não teórico.

```bash
npm audit --audit-level=high
npx osv-scanner .
npm ci --ignore-scripts          # scripts de instalação são um vetor comum
```

Práticas que reduzem materialmente o risco:

- **Lockfile commitado**, sempre. `npm ci`, nunca `npm install` no CI.
- **`--ignore-scripts`** por padrão; libere apenas os pacotes que realmente precisam.
- **Fixe versões** de dependências críticas; revise atualizações em vez de aceitar `^` cegamente.
- **Atualize com atraso deliberado** — pacotes comprometidos costumam ser detectados em horas ou dias. Esperar uma semana antes de adotar uma versão nova elimina boa parte do risco, praticamente de graça.
- **Renovate/Dependabot** com revisão humana, não merge automático.
- **SRI** para scripts servidos por CDN externa:

```html
<script src="https://cdn.exemplo.com/lib.js"
        integrity="sha384-…" crossorigin="anonymous"></script>
```

- **Minimize dependências.** A dependência mais segura é a que você não instalou. Uma função de 20 linhas copiada e entendida é preferível a um pacote com 40 dependências transitivas.

---

## 8. Headers de segurança

```http
Content-Security-Policy: …                                   # ver seção 1
Strict-Transport-Security: max-age=63072000; includeSubDomains; preload
X-Content-Type-Options: nosniff
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: camera=(), microphone=(), geolocation=(), interest-cohort=()
Cross-Origin-Opener-Policy: same-origin
Cross-Origin-Resource-Policy: same-origin
Cross-Origin-Embedder-Policy: require-corp                   # necessário p/ SharedArrayBuffer
```

Verifique em `securityheaders.com` e `observatory.mozilla.org`.

`X-Frame-Options` foi substituído por `frame-ancestors` na CSP, mas mantê-lo não custa nada para navegadores antigos.

---

## 9. Segredos no cliente

```js
// TUDO isto é público. O bundle é baixável e legível por qualquer pessoa.
const API_KEY = 'sk_live_abc123';              // ❌ vazado
const chave = process.env.VITE_STRIPE_SECRET;  // ❌ o bundler INLINE isso no código
```

Variáveis com prefixo `VITE_`, `NEXT_PUBLIC_`, `REACT_APP_` são **substituídas literalmente no bundle**. Não existe segredo no cliente — só existe segredo no servidor.

O que **pode** ir para o cliente: chaves publicáveis desenhadas para isso (`pk_live_` do Stripe, chave anônima do Supabase com RLS ativo, ID do Google Analytics). O que **nunca** pode: qualquer chave secreta, credencial de banco, token de serviço.

Se vazou: **rotacione imediatamente**. Remover do código não basta — está no histórico do git, no cache do CDN, no navegador de quem já baixou.

E confira o que vai junto no deploy:

```bash
# procure segredos no bundle antes de publicar
grep -rE "(sk_live|secret|password|BEGIN PRIVATE KEY)" dist/
```

Source maps em produção: úteis para depurar erros reais, mas expõem seu código-fonte. O padrão sensato é **gerá-los e enviá-los ao Sentry, sem publicá-los no servidor web**.

---

## 10. Outras superfícies

**`postMessage`** — sempre valide a origem:

```js
addEventListener('message', (e) => {
  if (e.origin !== 'https://parceiro-confiavel.com') return;   // sem isso, qualquer site injeta
  processar(e.data);
});
```

**`target="_blank"`** — use `rel="noopener noreferrer"` (padrão nos navegadores modernos, mas seja explícito).

**Prototype pollution** — mesclar JSON não confiável em objetos pode contaminar `Object.prototype`:

```js
if (['__proto__','constructor','prototype'].includes(chave)) continue;
```

**Redirecionamento aberto** — valide destinos vindos da URL (arquivo `05`, seção 7).

**Clickjacking** — `frame-ancestors 'none'`.

**Vazamento em URL** — nunca coloque token, senha ou dado sensível em query string. Vaza no `Referer`, nos logs do servidor, no histórico e em analytics.

---

## 11. Checklist

- [ ] Nenhum `innerHTML` com dado não confiável; sanitização por DOMPurify onde houver HTML rico
- [ ] CSP com nonce por requisição, sem `unsafe-inline`; implantada primeiro em report-only
- [ ] Trusted Types onde houver suporte
- [ ] Token de sessão em cookie `HttpOnly; Secure; SameSite`, **nunca** em `localStorage`
- [ ] Refresh concorrente deduplicado; rotação com detecção de reuso
- [ ] CSRF mitigado por `SameSite` **e** token anti-CSRF nas escritas
- [ ] CORS com lista de origens permitidas; nunca `*` com credenciais
- [ ] OAuth com Authorization Code + PKCE; `state` e `nonce` validados; implícito não usado
- [ ] Autorização verificada **no servidor** em todo endpoint; escopo do dono na consulta
- [ ] Saída filtrada por serializador explícito
- [ ] Nenhum segredo no bundle (verificado com `grep`)
- [ ] Headers de segurança completos
- [ ] Lockfile commitado, `npm ci`, `--ignore-scripts`, auditoria no CI
- [ ] `postMessage` valida origem
- [ ] Source maps enviados ao monitoramento, não publicados

---

## 12. Autoteste

1. Por que "o cliente é território hostil" invalida validação apenas no front?
2. Por que XSS baseado em DOM é o tipo dominante em SPAs?
3. Por que `HttpOnly` muda a gravidade de um XSS, mesmo sem impedi-lo?
4. Por que CSRF não se aplica quando o token vai no header `Authorization`?
5. CORS protege seu servidor? Justifique.
6. Por que o fluxo implícito do OAuth foi abandonado?
7. O que acontece com `VITE_MINHA_CHAVE` no build?
8. O que é IDOR, e por que responder 404 em vez de 403 pode ser melhor?

---

**Anterior:** [10 — SEO e acessibilidade](10-seo-acessibilidade.md) · **Próximo:** [12 — Build, deploy e infraestrutura](12-build-deploy-infra.md)
