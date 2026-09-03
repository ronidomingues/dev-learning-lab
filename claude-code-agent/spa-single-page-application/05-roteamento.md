# 05 · Roteamento no cliente

**Nível: intermediário** · Pré-requisitos: `04`.

O roteador é a peça que **substitui o navegador**. Tudo que o navegador fazia de graça na navegação — histórico, foco, rolagem, título, indicador de carregamento, tratamento de erro, cancelamento — passa a ser sua responsabilidade. Este arquivo é o inventário completo dessa dívida e de como pagá-la.

---

## 1. A History API

Três operações e um evento. É toda a base.

```js
history.pushState(estado, '', '/produtos/42');    // adiciona entrada ao histórico
history.replaceState(estado, '', '/produtos/42'); // substitui a entrada atual
history.back(); history.forward(); history.go(-2);

addEventListener('popstate', (e) => { /* usuário usou voltar/avançar */ });
```

Detalhes que mordem:

- **`pushState` não dispara `popstate`.** Você navegou programaticamente, então você já sabe — renderize você mesmo. `popstate` é só para navegação do usuário. Esquecer isso gera o bug oposto: renderizar duas vezes.
- **O segundo argumento (título) é ignorado** por todos os navegadores. Use `document.title = ...`.
- **`estado` é serializado** com o algoritmo de clone estruturado e tem limite de tamanho (na prática, alguns MB; o Firefox impõe ~16 MB). Guarde ali coisas pequenas: posição de rolagem, índice de item selecionado. **Nunca** guarde dados de negócio.
- **`pushState` respeita a mesma origem.** Não dá para forjar uma URL de outro domínio.

**`push` ou `replace`?** Regra: `push` quando o usuário deveria poder voltar; `replace` quando não. Filtro digitado em campo de busca → `replace` (senão cada letra vira uma entrada no histórico e o botão voltar fica inutilizável). Abrir um item → `push`.

### A alternativa: roteamento por hash

```js
location.hash = '#/produtos/42';
addEventListener('hashchange', renderizar);
```

Funciona sem **nenhuma** configuração de servidor, porque o fragmento após `#` nunca é enviado ao servidor. Custo: URLs feias, SEO historicamente pior, e conflito com âncoras de página.

**Quando usar hash em 2026:** apenas quando você não controla o servidor — extensões de navegador, apps empacotados em arquivo, GitHub Pages sem configuração, páginas embutidas em sistemas legados. Fora disso, use a History API.

---

## 2. O casamento de rotas

### Sintaxe de padrões

```
/produtos                 estático
/produtos/:id             parâmetro dinâmico
/produtos/:id/avaliacoes  aninhado
/arquivos/*caminho        curinga (captura o resto)
/produtos/:id?            segmento opcional
/(admin)/painel           grupo que não aparece na URL (convenção de file-based routing)
```

### Especificidade — a regra que evita bugs sutis

Quando várias rotas casam, qual vence? A ordem correta, e a que todo roteador sério implementa:

```
1. segmentos estáticos       /produtos/novo
2. parâmetros dinâmicos      /produtos/:id
3. curingas                  /produtos/*
4. fallback 404
```

Se `/produtos/:id` fosse testada antes de `/produtos/novo`, a tela de criação nunca abriria — o roteador acharia que "novo" é um id. **Roteadores que casam na ordem de declaração** (como o Express) transferem esse cuidado para você; **roteadores que ordenam por especificidade** (React Router, os baseados em arquivos) resolvem sozinhos.

### Implementação com URLPattern

Desde ~2023 os navegadores oferecem uma API nativa que elimina a necessidade de regex artesanal:

```js
const padrao = new URLPattern({ pathname: '/produtos/:id/avaliacoes/:rev?' });
const r = padrao.exec('https://x.com/produtos/42/avaliacoes');
r.pathname.groups;   // { id: '42', rev: undefined }
```

Suporte: Chrome e Edge desde 2022, Safari 18 (2024), Firefox 2025. Em 2026 é utilizável com um polyfill pequeno para navegadores antigos.

Versão manual, para entender o que acontece por baixo:

```js
function compilar(padrao) {
  const nomes = [];
  const regex = new RegExp('^' + padrao
    .replace(/\/:([^/?]+)\?/g, (_, n) => { nomes.push(n); return '(?:/([^/]+))?'; })
    .replace(/\/:([^/]+)/g,    (_, n) => { nomes.push(n); return '/([^/]+)'; })
    .replace(/\/\*(\w+)/g,     (_, n) => { nomes.push(n); return '/(.*)'; })
    + '$');

  return (caminho) => {
    const m = regex.exec(caminho);
    if (!m) return null;
    return Object.fromEntries(nomes.map((n, i) => [n, m[i + 1] && decodeURIComponent(m[i + 1])]));
  };
}
```

> **Sempre `decodeURIComponent`** nos parâmetros. `/busca/caf%C3%A9` precisa virar `café`. E sempre **valide** o parâmetro antes de usá-lo — `:id` pode vir com qualquer coisa que o usuário digitar na barra de endereços, inclusive payload de XSS.

---

## 3. Rotas aninhadas e layouts

O modelo mental que todo roteador moderno adota: **a URL é um caminho numa árvore, e cada segmento corresponde a um nível de layout que persiste**.

```
/app/projetos/7/tarefas/3

  Layout raiz (cabeçalho, autenticação)
   └── Layout /app (menu lateral)
        └── Layout /projetos/:id (abas do projeto, carrega o projeto)
             └── Layout /tarefas (lista de tarefas)
                  └── Página /:tarefaId (detalhe)
```

Ao navegar de `/app/projetos/7/tarefas/3` para `/app/projetos/7/tarefas/9`, **apenas o nível mais interno remonta**. O menu lateral, as abas e a lista permanecem — com sua rolagem, seu estado, seu foco intactos.

Isso não é conforto: é a razão de ser da SPA. Um MPA recarregaria tudo.

```jsx
// React Router 7 — rotas aninhadas
<Route path="/app" element={<LayoutApp />}>
  <Route path="projetos/:id" element={<LayoutProjeto />}>
    <Route path="tarefas" element={<ListaTarefas />}>
      <Route path=":tarefaId" element={<DetalheTarefa />} />
    </Route>
  </Route>
</Route>
// <Outlet /> dentro de cada layout marca onde o filho é renderizado
```

### Roteamento baseado em arquivos

Next.js, Nuxt, SvelteKit, TanStack Router e Remix derivam a árvore de rotas da estrutura de diretórios:

```
app/
├── layout.tsx                    → layout raiz
├── page.tsx                      → /
└── projetos/
    ├── layout.tsx                → layout de /projetos/*
    ├── page.tsx                  → /projetos
    └── [id]/
        ├── page.tsx              → /projetos/:id
        └── tarefas/
            └── [tarefaId]/page.tsx  → /projetos/:id/tarefas/:tarefaId
```

**Vantagem:** a estrutura é auto-documentada, o code splitting sai de graça (cada arquivo é um módulo), e não há um arquivo central de rotas para manter em sincronia.
**Custo:** convenções mágicas de nomes (`[id]`, `(grupo)`, `_privado`, `@slot`) que você precisa decorar, e refatorar uma URL significa mover diretórios.

---

## 4. Code splitting por rota

Sem isso, o usuário baixa a aplicação inteira — inclusive o painel de administração que ele nunca verá — só para ver a página inicial. É a otimização de maior retorno numa SPA.

```js
// import() dinâmico: o bundler corta aqui automaticamente
const rotas = [
  { padrao: '/',          carregar: () => import('./paginas/Inicio.js') },
  { padrao: '/produtos/:id', carregar: () => import('./paginas/Produto.js') },
  { padrao: '/admin',     carregar: () => import('./paginas/Admin.js') },   // 400 KB que 99% nunca baixa
];
```

```jsx
// React
const Admin = lazy(() => import('./paginas/Admin'));
<Suspense fallback={<Esqueleto />}><Admin /></Suspense>
```

### O problema que o splitting cria: mais uma cascata

```
baixa app.js → executa → descobre a rota → baixa chunk-da-rota.js → executa → busca dados
```

Você trocou um bundle grande por três idas sequenciais. As três correções, em ordem de importância:

**1. Preload no hover/foco.** O usuário leva ~200–300 ms entre apontar e clicar. É tempo suficiente para baixar o chunk inteiro.

```js
document.addEventListener('pointerover', (e) => {
  const link = e.target.closest('a[href^="/"]');
  if (link) rotaPara(link.pathname)?.carregar();     // fica no cache do módulo
}, { passive: true });
```

Refine com `pointerdown` (mais intencional) ou a Speculation Rules API para pré-renderizar de verdade:

```html
<script type="speculationrules">
{ "prerender": [{ "where": { "href_matches": "/produtos/*" }, "eagerness": "moderate" }] }
</script>
```

**2. `modulepreload` para as rotas prováveis.** Declara a dependência no HTML para o navegador buscar cedo:

```html
<link rel="modulepreload" href="/assets/pagina-inicio-a1b2.js">
```

**3. Buscar dados **em paralelo** com o código, não depois.** Esta é a ideia central dos *loaders* (Remix, React Router 7, TanStack Router): a rota declara de que dados precisa, e o roteador dispara código e dados simultaneamente.

```js
{
  padrao: '/produtos/:id',
  carregar: () => import('./paginas/Produto.js'),
  loader: ({ params, signal }) => fetch(`/api/produtos/${params.id}`, { signal }).then(r => r.json()),
}
// o roteador faz: Promise.all([carregar(), loader()]) — uma ida, não duas
```

> **Opinião profissional:** a migração de "componente busca seus próprios dados no `useEffect`" para "a rota declara seus dados" foi a maior melhoria arquitetural em SPAs na última década. Ela elimina cascatas por construção, permite cancelamento correto e torna possível pré-carregar. Se você mantém uma SPA que ainda busca dados dentro de `useEffect`, essa é a refatoração de maior retorno disponível.

---

## 5. Navegação concorrente e cancelamento

O usuário clica em A, e antes da resposta chegar, clica em B. Se você não tratar isso, a resposta de A pode chegar depois da de B e **sobrescrever a tela errada**. É uma condição de corrida clássica e passa despercebida em desenvolvimento (rede rápida) para aparecer em produção.

Duas defesas, use as duas:

```js
let navegacaoAtual = 0;
let controleAtual = null;

async function navegar(url) {
  const meuId = ++navegacaoAtual;      // defesa 1: token de geração
  controleAtual?.abort();               // defesa 2: aborta a anterior de verdade
  const controle = new AbortController();
  controleAtual = controle;

  try {
    const dados = await rota.loader({ signal: controle.signal });
    if (meuId !== navegacaoAtual) return;   // fui superado — descarta o resultado
    render(dados);
  } catch (e) {
    if (e.name === 'AbortError') return;    // cancelamento não é erro
    if (meuId === navegacaoAtual) renderErro(e);
  }
}
```

O `AbortController` economiza banda e trabalho de servidor; o token de geração protege contra tudo que não é abortável (trabalho já em memória, timers, promessas de terceiros).

---

## 6. As obrigações que o navegador cumpria e agora são suas

Esta seção é o núcleo prático do arquivo. Cada item abaixo é uma regressão real em relação a um site tradicional — e cada um é rotineiramente ignorado.

### 6.1 Foco — a mais negligenciada

Numa navegação real, o navegador move o foco para o topo do novo documento. Numa SPA, o foco fica **onde estava** — muitas vezes num link que já não existe. Para quem usa leitor de tela, **nada é anunciado**: a pessoa clica e não recebe nenhum sinal de que algo mudou.

```js
function aposNavegar(titulo) {
  const alvo = document.querySelector('#conteudo-principal');
  alvo.setAttribute('tabindex', '-1');   // torna focável por script, não por Tab
  alvo.focus({ preventScroll: true });
  anunciar(`${titulo} carregado`);       // região aria-live, para redundância
}
```

```html
<div aria-live="polite" aria-atomic="true" class="visualmente-oculto" id="anunciador"></div>
```

Vale a pena saber que existe a **Navigation API** (`navigation.addEventListener('navigate', ...)`, Chrome desde 2022), que trata SPAs como navegações de primeira classe e permite que o navegador restaure foco e rolagem corretamente. Ainda sem suporte universal em 2026 — Safari e Firefox chegaram depois —, mas é o futuro dessa área.

### 6.2 Rolagem

Regras que os usuários esperam sem saber que esperam:

- Navegar para uma rota nova → topo da página.
- Voltar/avançar → **restaurar a posição exata** onde a pessoa estava.
- Trocar apenas um parâmetro de busca (filtro, aba) → **não mexer** na rolagem.

```js
history.scrollRestoration = 'manual';   // desliga a tentativa (ruim) do navegador

const posicoes = new Map();

function antesDeSair(chave) { posicoes.set(chave, window.scrollY); }

function depoisDeRenderizar(chave, tipo) {
  if (tipo === 'pop') {
    const y = posicoes.get(chave) ?? 0;
    requestAnimationFrame(() => scrollTo(0, y));   // após o layout do novo conteúdo
  } else if (tipo === 'push') {
    scrollTo(0, 0);
  }
}
```

O `requestAnimationFrame` é essencial: restaurar antes do layout do conteúdo novo rola para uma página que ainda não tem altura. Para conteúdo que carrega assíncrono, você pode precisar esperar as imagens (use `content-visibility` e dimensões explícitas para que a altura seja conhecida antes).

### 6.3 Título e metadados

```js
document.title = `${produto.nome} — Minha Loja`;
document.documentElement.lang = idioma;
document.querySelector('link[rel=canonical]').href = location.href;
```

Isso não é cosmético: o título é o que o leitor de tela anuncia ao trocar de página, é o texto da entrada no histórico, e é o nome do favorito.

### 6.4 Estados de carregamento e erro

O navegador tinha uma barra de progresso. Você precisa de:

- **Indicador de progresso** — mas com atraso de ~150–200 ms antes de aparecer, senão navegações rápidas produzem um flash irritante.
- **Estado pendente sem tela branca.** O padrão moderno (React `useTransition`, `startTransition`) é **manter a tela antiga visível** e marcá-la como ocupada, em vez de trocá-la por um spinner. É melhor experiência e melhor CLS.
- **Fronteira de erro por rota** — falha de carregamento de chunk, 404, 500, offline. Cada uma com recuperação própria.

```js
// falha de carregamento de chunk após deploy: causa clássica, tratamento específico
try {
  await import('./paginas/Admin.js');
} catch (e) {
  // o chunk antigo sumiu do CDN porque houve deploy. Recarregar resolve.
  location.reload();
}
```

### 6.5 Recarregar `/sobre` sem dar 404

O bug número um de quem publica uma SPA pela primeira vez. O servidor recebe `GET /sobre`, procura um arquivo `sobre.html`, não acha, retorna 404. O roteador nunca chegou a rodar.

A correção é sempre a mesma: **servir o `index.html` para qualquer caminho que não seja um arquivo real**.

```nginx
# nginx
location / {
  try_files $uri $uri/ /index.html;
}
```

```
# Netlify — _redirects
/*  /index.html  200
```

```json
// Vercel — vercel.json
{ "rewrites": [{ "source": "/(.*)", "destination": "/index.html" }] }
```

```apache
# Apache — .htaccess
RewriteEngine On
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule . /index.html [L]
```

Cuidado com o efeito colateral: com essa regra, uma URL genuinamente inexistente responde **200 com o shell**, não 404. Buscadores odeiam isso (chama-se *soft 404*). A correção é a rota de 404 do cliente definir uma meta tag `noindex` — ou, melhor, usar SSR e retornar o status correto (arquivo `10`).

---

## 7. Guardas de rota e autenticação

```js
{
  padrao: '/admin/*',
  guarda: async ({ url }) => {
    const usuario = await sessao.obter();
    if (!usuario) return { redirecionar: `/login?proximo=${encodeURIComponent(url)}` };
    if (!usuario.papeis.includes('admin')) return { redirecionar: '/403' };
    return true;
  },
}
```

Três avisos que valem mais que a implementação:

1. **Guarda de cliente é experiência de usuário, não segurança.** Qualquer pessoa pode desabilitar seu JavaScript ou chamar sua API direto com `curl`. **A autorização real acontece no servidor, em toda requisição, sempre.** Guarda no cliente só evita mostrar uma tela que falharia. Arquivo `11`.
2. **Sempre `encodeURIComponent` no parâmetro de retorno** — e, ao usá-lo, **valide que é um caminho interno**. Redirecionar para um valor arbitrário vindo da URL é a vulnerabilidade de *open redirect*.
3. **Use `replace` no redirecionamento de login**, não `push`. Senão o botão voltar leva o usuário de volta à tela de login num laço.

---

## 8. A URL como estado

Subestimado, e talvez a decisão de design mais valiosa deste arquivo:

> **Todo estado que o usuário esperaria poder compartilhar, favoritar ou recuperar com o botão voltar deve viver na URL.**

Filtros, ordenação, página, aba ativa, termo de busca, item selecionado num painel mestre-detalhe. Se está num `useState`, o usuário não consegue mandar o link para um colega — e essa é uma reclamação constante em ferramentas internas.

```js
// ler
const p = new URLSearchParams(location.search);
const filtros = { q: p.get('q') ?? '', pagina: Number(p.get('pagina') ?? 1) };

// escrever, sem poluir o histórico
function atualizarFiltros(novos) {
  const p = new URLSearchParams(location.search);
  for (const [k, v] of Object.entries(novos)) {
    if (v === '' || v == null) p.delete(k); else p.set(k, String(v));
  }
  history.replaceState({}, '', `${location.pathname}?${p}`);   // replace: digitar não gera histórico
}
```

Combine com *debounce* para campos de texto (300 ms é o valor usual) e use `push` apenas quando o usuário confirmar uma ação que ele gostaria de desfazer com o botão voltar.

O que **não** deve ir para a URL: token, dado sensível (URLs vazam em logs, no `Referer` e no histórico compartilhado), e estado efêmero de UI (se um acordeão está aberto).

---

## 9. Panorama de roteadores em 2026

| Roteador | Modelo | Dados | Tipagem | Observação |
|---|---|---|---|---|
| **React Router 7** | config ou arquivos | loaders/actions | boa | fundiu-se com o Remix; a escolha padrão em React |
| **TanStack Router** | config tipada | loaders integrados | **excelente** | tipagem ponta a ponta de params e search; search params como estado de primeira classe |
| **Next.js App Router** | arquivos | RSC + server actions | boa | roteador acoplado ao framework; padrão de fato em React |
| **Vue Router 4** | config | guards | boa | maduro, previsível |
| **SvelteKit** | arquivos | `load` (server/universal) | ótima | o modelo de dados mais limpo do mercado, na minha avaliação |
| **Angular Router** | config | resolvers | ótima | o mais completo em guardas; verboso |
| **Nuxt** | arquivos | `useAsyncData` | boa | equivalente Vue do Next |

Critério prático de escolha: **se a tipagem dos parâmetros de rota importa muito para você, TanStack Router é sensivelmente melhor que o resto**. Se você já usa um meta-framework, use o roteador dele — trocar cria mais problema do que resolve.

---

## 10. Checklist de roteador correto

Use isto para auditar qualquer SPA, inclusive as suas:

- [ ] Recarregar uma URL profunda funciona (rewrite configurado no servidor)
- [ ] Botão voltar e avançar funcionam em toda navegação
- [ ] Ctrl/Cmd+clique abre em nova aba
- [ ] Clique com botão do meio abre em nova aba
- [ ] Links externos, `target="_blank"` e `download` não são interceptados
- [ ] O foco vai para o conteúdo novo a cada navegação
- [ ] A mudança de página é anunciada por leitor de tela
- [ ] A rolagem vai ao topo em navegação nova e é **restaurada** no voltar
- [ ] `document.title` muda a cada rota
- [ ] Navegações concorrentes são canceladas — sem race condition
- [ ] Cada rota tem estado de carregamento (com atraso) e de erro
- [ ] Falha de carregamento de chunk após deploy é tratada
- [ ] Filtros, busca, ordenação e paginação vivem na URL
- [ ] Rotas privadas têm guarda **e** o servidor valida autorização de verdade
- [ ] O parâmetro de redirecionamento pós-login é validado (sem open redirect)
- [ ] 404 do cliente marca `noindex` (ou o SSR retorna 404 real)

---

## 11. Autoteste

1. Por que `pushState` não dispara `popstate`, e que bug aparece se você achar que dispara?
2. Você tem `/produtos/novo` e `/produtos/:id`. Em que ordem devem ser testadas e por quê?
3. Quais três coisas devem acontecer com foco, rolagem e título a cada navegação?
4. Explique a race condition da seção 5 e por que `AbortController` sozinho não basta.
5. Por que um filtro de busca deve usar `replaceState` e não `pushState`?
6. Uma guarda de rota impede um usuário comum de acessar `/admin`. Isso é segurança? Justifique.
7. Você configurou `try_files ... /index.html`. Que problema de SEO isso cria e como resolver?

---

**Anterior:** [04 — Anatomia](04-anatomia.md) · **Próximo:** [06 — Gerenciamento de estado](06-estado.md)
