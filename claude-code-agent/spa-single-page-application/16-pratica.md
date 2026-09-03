# 16 · Prática

**Nível: todos** · Sete laboratórios em ordem crescente. O primeiro é o mais importante do curso.

Ler sobre SPA e construir uma são coisas diferentes. Faça pelo menos o Laboratório 1 — ele torna concreto tudo que os arquivos `04`–`06` descrevem.

---

## Laboratório 1 — Uma SPA completa, sem framework

**Objetivo:** implementar as cinco peças do arquivo `04` num único arquivo HTML. Zero dependências, zero build.

Salve como `spa.html` e sirva com `npx serve` ou `python3 -m http.server` (abrir com `file://` quebra os módulos e a History API).

```html
<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>SPA do zero</title>
<style>
  body { font: 16px/1.6 system-ui, sans-serif; max-width: 46rem; margin: 2rem auto; padding: 0 1rem; }
  nav a { margin-right: 1rem; }
  [aria-current="page"] { font-weight: 700; text-decoration: none; }
  .sr-only { position:absolute; width:1px; height:1px; overflow:hidden; clip:rect(0,0,0,0); white-space:nowrap; }
  :focus-visible { outline: 2px solid currentColor; outline-offset: 2px; }
  .card { border: 1px solid #ccc; border-radius: 8px; padding: 1rem; margin: .5rem 0; }
  .erro { color: #b00; }
</style>
</head>
<body>

<a href="#main" class="sr-only">Pular para o conteúdo</a>

<nav aria-label="Principal">
  <a href="/">Início</a>
  <a href="/usuarios">Usuários</a>
  <a href="/sobre">Sobre</a>
</nav>

<main id="main" tabindex="-1"></main>
<div id="anunciador" aria-live="polite" aria-atomic="true" class="sr-only"></div>

<script type="module">
/* ─── PEÇA 3: sistema reativo (arquivo 04, seção 6) ─────────────────── */
let assinanteAtual = null;

function sinal(inicial) {
  let valor = inicial;
  const assinantes = new Set();
  return {
    get valor() { if (assinanteAtual) assinantes.add(assinanteAtual); return valor; },
    set valor(novo) {
      if (Object.is(valor, novo)) return;
      valor = novo;
      for (const f of [...assinantes]) f();
    },
  };
}

function efeito(fn) {
  const executar = () => { assinanteAtual = executar; try { fn(); } finally { assinanteAtual = null; } };
  executar();
}

/* ─── PEÇA 5: camada de dados com cache, dedupe e cancelamento ──────── */
const cache = new Map();

function consultar(chave, buscador, { ttl = 30_000 } = {}) {
  const agora = performance.now();
  const e = cache.get(chave);
  if (e && !e.pendente && agora - e.em < ttl) return Promise.resolve(e.dado);
  if (e?.pendente) return e.promessa;

  const promessa = buscador()
    .then(dado => { cache.set(chave, { dado, em: performance.now() }); return dado; })
    .catch(err => { cache.delete(chave); throw err; });

  cache.set(chave, { promessa, pendente: true, em: agora });
  return promessa;
}

/* ─── utilitário obrigatório: escape (arquivo 11) ───────────────────── */
const esc = (s) => String(s).replace(/[&<>"']/g,
  c => ({ '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;' }[c]));

/* ─── as telas ──────────────────────────────────────────────────────── */
const contador = sinal(0);

const telas = {
  async inicio() {
    return `<h1>Início</h1>
      <p>Contador reativo: <output id="saida"></output></p>
      <button id="mais">Incrementar</button>`;
  },

  async usuarios() {
    const lista = await consultar('usuarios',
      () => fetch('https://jsonplaceholder.typicode.com/users').then(r => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
      }));
    return `<h1>Usuários</h1>` + lista.map(u => `
      <article class="card">
        <h2><a href="/usuarios/${u.id}">${esc(u.name)}</a></h2>
        <p>${esc(u.email)}</p>
      </article>`).join('');
  },

  async usuario({ id }) {
    const u = await consultar(`usuario:${id}`,
      () => fetch(`https://jsonplaceholder.typicode.com/users/${encodeURIComponent(id)}`)
        .then(r => { if (!r.ok) throw new Error(`HTTP ${r.status}`); return r.json(); }));
    return `<h1>${esc(u.name)}</h1>
      <p>${esc(u.email)} · ${esc(u.phone)}</p>
      <p><a href="/usuarios">← Voltar</a></p>`;
  },

  async sobre() { return `<h1>Sobre</h1><p>SPA em ~120 linhas, sem framework.</p>`; },

  async naoEncontrado() { return `<h1>404</h1><p>Página não encontrada.</p>`; },
};

/* ─── PEÇA 2: roteador ──────────────────────────────────────────────── */
const rotas = [
  { padrao: '/',              ver: telas.inicio,   titulo: 'Início' },
  { padrao: '/usuarios',      ver: telas.usuarios, titulo: 'Usuários' },
  { padrao: '/usuarios/:id',  ver: telas.usuario,  titulo: 'Usuário' },
  { padrao: '/sobre',         ver: telas.sobre,    titulo: 'Sobre' },
];

function casar(padrao, caminho) {
  const p = padrao.split('/'), c = caminho.split('/');
  if (p.length !== c.length) return null;
  const params = {};
  for (let i = 0; i < p.length; i++) {
    if (p[i].startsWith(':')) params[p[i].slice(1)] = decodeURIComponent(c[i]);
    else if (p[i] !== c[i]) return null;
  }
  return params;
}

const main = document.querySelector('#main');
const anunciador = document.querySelector('#anunciador');
let geracao = 0;                                   // token contra race condition

async function renderizar(tipo = 'push') {
  const meuId = ++geracao;
  const caminho = location.pathname;

  // ordena por especificidade: estáticas antes de dinâmicas (arquivo 05, seção 2)
  const ordenadas = [...rotas].sort((a, b) =>
    (a.padrao.includes(':') ? 1 : 0) - (b.padrao.includes(':') ? 1 : 0));

  let rota = null, params = null;
  for (const r of ordenadas) {
    const m = casar(r.padrao, caminho);
    if (m) { rota = r; params = m; break; }
  }
  if (!rota) rota = { ver: telas.naoEncontrado, titulo: 'Não encontrado' };

  const timer = setTimeout(() => {                 // spinner só após 150ms
    if (meuId === geracao) main.innerHTML = '<p>Carregando…</p>';
  }, 150);

  try {
    const html = await rota.ver(params ?? {});
    if (meuId !== geracao) return;                 // fui superado: descarta
    main.innerHTML = html;
  } catch (err) {
    if (meuId !== geracao) return;
    main.innerHTML = `<p class="erro" role="alert">Erro: ${esc(err.message)}</p>`;
  } finally {
    clearTimeout(timer);
  }

  if (meuId !== geracao) return;

  // as obrigações do arquivo 05, seção 6
  document.title = `${rota.titulo} — SPA do zero`;
  main.focus({ preventScroll: true });
  anunciador.textContent = `${rota.titulo} carregado`;
  if (tipo === 'push') scrollTo(0, 0);
  for (const a of document.querySelectorAll('nav a')) {
    a.toggleAttribute('aria-current', a.getAttribute('href') === caminho);
    if (a.getAttribute('href') === caminho) a.setAttribute('aria-current', 'page');
  }

  ligarInterativos();
}

function ligarInterativos() {
  const saida = document.querySelector('#saida');
  if (saida) efeito(() => { saida.textContent = contador.valor; });
  document.querySelector('#mais')?.addEventListener('click', () => contador.valor++);
}

/* ─── PEÇA 1: bootstrap ─────────────────────────────────────────────── */
document.addEventListener('click', (e) => {
  const link = e.target.closest('a');
  if (!link) return;
  const url = new URL(link.href, location.href);
  if (url.origin !== location.origin) return;
  if (link.target === '_blank' || link.hasAttribute('download')) return;
  if (e.metaKey || e.ctrlKey || e.shiftKey || e.altKey || e.button !== 0) return;
  if (url.hash && url.pathname === location.pathname) return;   // âncora na mesma página
  e.preventDefault();
  if (url.href === location.href) return;
  history.pushState({}, '', url.pathname + url.search);
  renderizar('push');
});

addEventListener('popstate', () => renderizar('pop'));
history.scrollRestoration = 'manual';
renderizar('push');
</script>
</body>
</html>
```

### Exercícios sobre o Laboratório 1

Faça na ordem. Cada um corresponde a uma seção do curso:

1. **Quebre o roteador de propósito.** Remova o listener de `popstate`. Navegue e clique em voltar. Observe: a URL muda, a tela não. É o bug mais comum de SPA, agora visível.
2. **Quebre a interceptação.** Remova a checagem de `e.metaKey`. Tente Ctrl+clique.
3. **Observe a race condition.** Adicione `await new Promise(r => setTimeout(r, 2000))` em `telas.usuarios`, depois **remova** o token `geracao` e clique rápido entre Usuários e Sobre. Reponha o token e veja a diferença.
4. **Restaure a rolagem.** Guarde `window.scrollY` num `Map` antes de sair e restaure no `pop`, dentro de um `requestAnimationFrame` (arquivo `05`, seção 6.2).
5. **Adicione um leitor de tela.** Ligue o VoiceOver (Cmd+F5) ou NVDA e navegue. Depois **remova** o `main.focus()` e o anunciador, e navegue de novo. Esta é a diferença que o arquivo `10` descreve — e sentir isso vale mais que lê-lo.
6. **Prove o XSS.** Troque `esc(u.name)` por `u.name` e faça um mock que devolva `{ name: '<img src=x onerror=alert(1)>' }`. Reponha o escape.
7. **Adicione code splitting.** Mova uma tela para um módulo separado e carregue-a com `import()`. Faça o preload no `pointerover` do link.

---

## Laboratório 2 — Reatividade fina completa

Estenda o sistema de sinais do Laboratório 1 com o que uma implementação de produção precisa (arquivo `13`, seção 4):

1. `derivado(fn)` com **avaliação preguiçosa** — só recomputa quando lido.
2. **Limpeza de dependências** antes de cada re-execução do efeito.
3. **Lote** (`lote(() => { a.valor=1; b.valor=2 })`) — os efeitos rodam uma vez ao final.
4. **Ordem topológica** — resolva o problema do diamante. Teste: `a → c`, `a → d`, `c,d → e`. O efeito `e` deve rodar **uma** vez por mudança de `a`, nunca com valores inconsistentes.
5. `aoLimpar(fn)` para descartar recursos quando o efeito é reexecutado ou destruído.

Compare seu resultado com `packages/solid/src/reactive/signal.ts` no repositório do Solid.

---

## Laboratório 3 — Virtual DOM e reconciliação

Implemente um VDOM mínimo:

```js
function h(tipo, props, ...filhos) { return { tipo, props: props ?? {}, filhos: filhos.flat() }; }
function diff(antigo, novo, paiDom, indice = 0) { /* seu código */ }
```

Requisitos:

1. Criar, remover e substituir nós quando o `tipo` difere.
2. Atualizar atributos e manipuladores de evento sem recriar o nó.
3. **Suporte a `key`** com reconciliação por mapa.
4. Compare no console o número de operações de DOM para `[A,B,C] → [Z,A,B,C]` **com** e **sem** key. Você vai ver 1 versus 4 (arquivo `13`, seção 2).

---

## Laboratório 4 — SSR na mão

Sem meta-framework, para entender o mecanismo:

1. Um servidor Node que renderiza a mesma função de template em string.
2. Serialize os dados em `window.__DADOS__` — com escape de `<`, `>`, U+2028 e U+2029 (arquivo `07`).
3. No cliente, "hidrate": em vez de recriar o DOM, apenas anexe os handlers.
4. **Introduza um erro de hidratação de propósito** (renderize `new Date()`) e observe.
5. Meça LCP e TTI antes e depois com o Lighthouse. Você vai ver o que o arquivo `07` afirma: o LCP melhora muito, o TTI quase nada.

---

## Laboratório 5 — Auditoria de performance

Pegue uma SPA existente — sua ou pública — e produza um relatório:

1. Lighthouse com throttling 4x. Registre LCP, INP, CLS, TBT.
2. Aba Network: **desenhe a cascata**. Marque cada dependência sequencial.
3. `npx source-map-explorer` no bundle. Liste os cinco maiores módulos.
4. Aba Performance: liste toda long task acima de 50 ms e sua origem.
5. Proponha três mudanças ordenadas por (impacto ÷ esforço).
6. **Implemente a primeira e meça de novo.** Sem a medição posterior, o exercício não vale.

---

## Laboratório 6 — Auditoria de acessibilidade

Na mesma aplicação:

1. `npx @axe-core/cli <url>` — registre as violações.
2. **Percorra o fluxo principal só com teclado.** Documente cada ponto onde travou.
3. **Percorra com leitor de tela.** Documente cada ponto onde não soube o que estava acontecendo.
4. Zoom 200%: o que quebra?
5. Compare a lista automática com a manual. A diferença é a lição do arquivo `10`, seção 7.

---

## Laboratório 7 — Projeto integrador

Construa uma aplicação completa e defenda cada decisão por escrito:

**Requisitos funcionais:** lista com busca, filtro e paginação (tudo na URL); página de detalhe; criar/editar com validação; autenticação com rota protegida; otimismo em uma ação; funcionamento offline para leitura.

**Requisitos não funcionais:** LCP ≤ 2,5 s e INP ≤ 200 ms com throttling 4x; JS inicial ≤ 170 KB comprimido; zero violações do axe; fluxo completo por teclado; conteúdo visível no `curl` (se for público); nenhum segredo no bundle; sem race condition ao navegar rápido.

**Entregável:** um `DECISOES.md` respondendo:

1. Qual estratégia de renderização e **por quê** (aplique a árvore do arquivo `07`).
2. Como cada categoria de estado foi classificada (tabela do arquivo `06`).
3. Onde o token vive e por quê (arquivo `11`).
4. Que cascatas existiam e como foram eliminadas (arquivo `08`).
5. O que ficou de fora do orçamento de performance e o que você cortou.

O `DECISOES.md` é o entregável mais valioso. Escrever a justificativa é o que transforma escolha em conhecimento.

---

## Como saber que você aprendeu

Você domina este assunto quando consegue:

- Explicar a SPA para um leigo em dois minutos, com uma analogia própria.
- Desenhar no quadro a sequência do primeiro byte à interatividade, e apontar o gargalo de um caso concreto.
- Implementar roteador, sinais e cache de dados sem consultar nada.
- Escolher a estratégia de renderização de um projeto e **defender a escolha** contra objeções.
- Pegar uma SPA lenta e, em uma hora, produzir um diagnóstico ordenado por impacto.
- Auditar acessibilidade com teclado e leitor de tela.
- Ler o código-fonte de um framework e entender **por que** ele fez cada escolha.
- Dizer "isto aqui não deveria ser uma SPA" quando for o caso — e explicar por quê.

---

**Anterior:** [15 — Armadilhas](15-armadilhas.md) · **Próximo:** [17 — Referências](17-referencias.md)
