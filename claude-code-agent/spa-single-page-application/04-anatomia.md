# 04 · Anatomia de uma SPA

**Nível: intermediário** · Pré-requisitos: `02`. JavaScript básico.

Aqui abrimos a caixa-preta. Ao final deste arquivo você terá construído uma SPA funcional **sem framework nenhum** — e entenderá exatamente o que React, Vue e Svelte estão fazendo por você.

---

## 1. O HTML que não tem nada

O ponto de partida de uma SPA clássica é este documento — e ele é literalmente tudo que o servidor entrega:

```html
<!doctype html>
<html lang="pt-BR">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Minha App</title>
    <link rel="stylesheet" href="/assets/app-a1b2c3.css">
  </head>
  <body>
    <div id="root"></div>                          <!-- vazio. A app inteira vive aqui. -->
    <script type="module" src="/assets/app-d4e5f6.js"></script>
  </body>
</html>
```

Observe o que **não** está aqui: conteúdo. Nenhum texto, nenhum dado, nenhuma estrutura. Se o JavaScript não rodar, o usuário vê uma página em branco — e um buscador vê um documento vazio.

Esse `<div id="root">` é o **ponto de montagem** (*mount point*). É o buraco onde a aplicação será enxertada.

> **Isto é a definição operacional de "shell de aplicação"**: um HTML mínimo, idêntico para toda rota, cujo único trabalho é carregar o JavaScript. Ele é cacheável para sempre, o que é a origem de uma das grandes vantagens da SPA — e da tela branca, que é sua grande desvantagem. Os arquivos `07` e `10` mostram como recuperar o conteúdo no HTML sem perder a SPA.

---

## 2. A sequência completa, do primeiro byte ao primeiro clique

Sete etapas. Cada uma pode ser o gargalo, e saber qual é é metade do trabalho de otimização (arquivo `09`).

```
[1] DNS + TCP + TLS          ~50–300 ms   antes de UM byte útil trafegar
[2] GET /  → shell HTML       ~20–100 ms   arquivo minúsculo, quase sempre em CDN
[3] parse do HTML → DOM        ~1 ms       são 12 linhas
     descobre CSS e JS, dispara os downloads
[4] baixa app.js               ~100–2000 ms  AQUI mora a dor: 200 KB a 2 MB
[5] parse + compila + executa  ~50–500 ms   custo de CPU, brutal em celular fraco
     o framework monta a árvore de componentes
     ── PRIMEIRA PINTURA: normalmente um esqueleto ou spinner ──
[6] fetch dos dados            ~50–500 ms   só COMEÇA agora — cascata sequencial
[7] re-render com os dados
     ── TELA ÚTIL ──
     ── e só então: interatividade ──
```

O ponto que fecha o argumento do arquivo `01`:

> Numa SPA pura, **as etapas 4, 5 e 6 são estritamente sequenciais**. O navegador não pode buscar dados que não sabe que precisa, e ele só descobre isso depois de executar o JavaScript que contém as rotas. Isso é uma **cascata** (*waterfall*) e é estrutural, não um bug de implementação.
>
> Num site tradicional, o servidor sabe imediatamente o que a URL `/produtos/42` precisa, busca no banco e manda tudo pronto na primeira resposta. Ele pula as etapas 4–6 inteiras para o primeiro paint.

Esta é a razão técnica precisa pela qual SSR existe (arquivo `07`).

---

## 3. As cinco peças de qualquer SPA

Independente de framework, toda SPA tem estas cinco peças. Elas são o esqueleto conceitual do resto do curso:

| # | Peça | Responsabilidade | Arquivo |
|---|---|---|---|
| 1 | **Bootstrap** | encontrar o mount point e iniciar a aplicação | aqui |
| 2 | **Roteador** | mapear URL → tela, e sincronizar com o histórico | `05` |
| 3 | **Estado** | guardar dados e notificar quem depende deles | `06` |
| 4 | **Renderização** | transformar estado em DOM, e atualizar quando mudar | `07`, `13` |
| 5 | **Camada de dados** | falar com o servidor, cachear, tratar erro e carregamento | `08` |

Vamos construir as cinco, do zero.

---

## 4. Peça 1 — Bootstrap

```js
// app.js — o ponto de entrada
import { criarRoteador } from './roteador.js';
import { rotas } from './rotas.js';

const raiz = document.querySelector('#root');
const roteador = criarRoteador(rotas, raiz);
roteador.iniciar();
```

É só isso. O ponto de entrada de qualquer SPA — inclusive as feitas em React — é essencialmente estas quatro linhas. O equivalente em React 19:

```js
import { createRoot } from 'react-dom/client';
createRoot(document.querySelector('#root')).render(<App />);
```

---

## 5. Peça 2 — Roteamento (o mínimo viável)

O roteador precisa fazer três coisas: (a) descobrir a rota atual pela URL, (b) interceptar cliques em links internos, (c) reagir ao botão voltar.

```js
// roteador.js
export function criarRoteador(rotas, raiz) {
  async function renderizar() {
    const caminho = location.pathname;
    const rota = rotas.find(r => r.testar(caminho)) ?? rotas.find(r => r.padrao);

    raiz.innerHTML = '<div class="carregando">Carregando…</div>';
    try {
      const params = rota.extrair?.(caminho) ?? {};
      const html = await rota.ver(params);
      raiz.innerHTML = html;
      document.title = rota.titulo ?? 'Minha App';
    } catch (erro) {
      raiz.innerHTML = `<p role="alert">Erro: ${escapar(erro.message)}</p>`;
    }
  }

  function navegar(url) {
    history.pushState({}, '', url);   // muda a URL SEM pedir nada ao servidor
    renderizar();
  }

  return {
    iniciar() {
      // (b) intercepta cliques em links internos
      document.addEventListener('click', (e) => {
        const link = e.target.closest('a');
        if (!link) return;
        const url = new URL(link.href, location.href);
        if (url.origin !== location.origin) return;         // link externo: deixa o navegador
        if (link.target === '_blank' || link.hasAttribute('download')) return;
        if (e.metaKey || e.ctrlKey || e.shiftKey || e.button !== 0) return;  // abrir em nova aba
        e.preventDefault();
        navegar(url.pathname + url.search);
      });

      // (c) reage a voltar/avançar
      addEventListener('popstate', renderizar);

      renderizar();   // (a) rota inicial
    },
    navegar,
  };
}

const escapar = (s) => String(s).replace(/[&<>"']/g,
  c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
```

Cinco coisas para notar, porque cada uma é um bug real que aparece em SPAs de produção:

1. **`history.pushState`** é a peça central. Ela altera a URL e o histórico **sem nenhuma requisição**. Foi ela que tornou SPAs viáveis de verdade em 2008.
2. **`e.preventDefault()` só depois de verificar tudo.** Interceptar Ctrl+clique quebra "abrir em nova aba" — um dos bugs mais irritantes e mais comuns de SPA.
3. **`popstate`** dispara no voltar/avançar. Sem esse listener, o botão voltar muda a URL e não muda a tela: o clássico "voltar quebrado".
4. **`document.title`** precisa ser atualizado manualmente. O navegador fazia isso de graça; agora é seu problema. Vale para meta tags, `lang`, favicon.
5. **`escapar()`.** Toda vez que você monta HTML por concatenação, você abre uma porta de XSS. Frameworks escapam por padrão; código próprio, não. Arquivo `11`.

E o que **falta** neste roteador — cada item é uma seção do arquivo `05`: restaurar posição de rolagem, mover o foco para o novo conteúdo (acessibilidade), cancelar navegações concorrentes, rotas aninhadas, carregamento sob demanda, e o `_redirects`/rewrite no servidor sem o qual recarregar `/sobre` dá 404.

---

## 6. Peça 3 — Estado reativo (30 linhas)

O coração de todo framework é este padrão: **um valor que sabe quem depende dele**.

```js
// reativo.js — implementação mínima de signals
let assinanteAtual = null;

export function sinal(valorInicial) {
  let valor = valorInicial;
  const assinantes = new Set();

  return {
    get valor() {
      if (assinanteAtual) assinantes.add(assinanteAtual);  // rastreia a dependência
      return valor;
    },
    set valor(novo) {
      if (Object.is(valor, novo)) return;                   // sem mudança, sem trabalho
      valor = novo;
      for (const f of [...assinantes]) f();                 // notifica
    },
  };
}

export function efeito(fn) {
  const executar = () => {
    assinanteAtual = executar;    // "estou lendo — anote-me como dependente"
    try { fn(); } finally { assinanteAtual = null; }
  };
  executar();
}

export function derivado(fn) {
  const s = sinal(undefined);
  efeito(() => { s.valor = fn(); });   // recalcula sozinho quando as fontes mudam
  return { get valor() { return s.valor; } };
}
```

Uso:

```js
const contador = sinal(0);
const dobro = derivado(() => contador.valor * 2);

efeito(() => {
  document.querySelector('#saida').textContent = `${contador.valor} → ${dobro.valor}`;
});

contador.valor = 5;   // o efeito roda sozinho. Nada mais precisou ser dito.
```

**Estas 30 linhas são, conceitualmente, o motor do Vue, do SolidJS, do Svelte 5 e dos signals do Angular.** As implementações reais acrescentam: limpeza de assinaturas mortas, lote de atualizações (*batching*), detecção de ciclos, ordenação topológica para evitar recomputações intermediárias, e propagação preguiçosa. Mas a ideia é exatamente esta.

Note o contraste com o React: o React **não** rastreia dependências assim. Ele re-executa o componente inteiro e compara o resultado (arquivo `13`). É a diferença entre "sei exatamente o que mudou" e "descubro comparando".

---

## 7. Peça 4 — Renderização (três abordagens)

Com estado reativo, como pintar a tela? Há três famílias, em ordem crescente de sofisticação:

**A — Substituir tudo (`innerHTML`).** Simples, e o que fizemos no roteador acima.
Custo: destrói e recria todos os nós. Perde foco, perde rolagem, perde estado de `<input>`, perde vídeo tocando, reinicia animações. Aceitável para trocar de rota; inaceitável para atualizar uma lista.

**B — Atualização cirúrgica (reatividade fina).** Cada sinal sabe qual nó do DOM ele controla, e escreve direto nele.

```js
const nome = sinal('Ana');
const el = document.querySelector('#nome');
efeito(() => { el.textContent = nome.valor; });   // toca UM nó de texto, só
```

Custo próximo do ótimo teórico. É o modelo de Solid, Svelte 5 e Vue. Exige que o framework saiba, em tempo de compilação ou de criação, qual expressão pertence a qual nó.

**C — Virtual DOM.** Renderiza uma árvore de objetos leves, compara com a anterior, aplica a diferença.

```js
// o que o JSX vira
{ tipo: 'ul', filhos: itens.map(i => ({ tipo: 'li', filhos: [i.nome], chave: i.id })) }
```

Custo: comparar a árvore inteira a cada mudança — mas com constantes baixas, e sem exigir que o framework saiba de antemão quem depende de quê. É o modelo do React. O arquivo `13` analisa o algoritmo, sua complexidade e por que `key` é obrigatório.

---

## 8. Peça 5 — Camada de dados

O ingênuo, que todo mundo escreve primeiro:

```js
async function carregarProduto(id) {
  const r = await fetch(`/api/produtos/${id}`);
  return r.json();
}
```

Os seis problemas que isso tem, e que a existência de bibliotecas como TanStack Query e SWR se justifica por resolver:

1. **Sem cache** — voltar para a mesma tela rebusca tudo.
2. **Sem deduplicação** — três componentes pedindo o mesmo produto disparam três requisições.
3. **Sem cancelamento** — o usuário navega para fora e a resposta antiga chega depois, sobrescrevendo a tela nova. *Race condition* real e comum.
4. **Sem estados** — carregando, erro, revalidando: você reimplementa em cada tela.
5. **Sem revalidação** — o dado envelhece silenciosamente.
6. **Sem retry** — uma falha de rede transitória vira erro permanente na cara do usuário.

Uma versão que resolve cache, dedupe e cancelamento em ~25 linhas:

```js
const cache = new Map();

export function consultar(chave, buscador, { ttl = 30_000 } = {}) {
  const agora = performance.now();
  const entrada = cache.get(chave);

  if (entrada && agora - entrada.em < ttl) return entrada.promessa;   // fresco: reusa
  if (entrada?.pendente) return entrada.promessa;                     // em voo: dedupe

  const controle = new AbortController();
  const promessa = buscador(controle.signal)
    .then(dado => { cache.set(chave, { dado, em: performance.now() }); return dado; })
    .catch(erro => { cache.delete(chave); throw erro; });

  cache.set(chave, { promessa, pendente: true, em: agora, cancelar: () => controle.abort() });
  return promessa;
}

export function invalidar(prefixo) {
  for (const k of cache.keys()) if (k.startsWith(prefixo)) cache.delete(k);
}
```

O arquivo `08` desenvolve isso até *stale-while-revalidate*, atualização otimista e reconciliação de mutações.

---

## 9. O ciclo de vida em regime

Montada a aplicação, ela entra num laço que roda até o usuário fechar a aba:

```
   ┌──────────────────────────────────────────────┐
   │  evento (clique, tecla, rede, timer)         │
   └───────────────────┬──────────────────────────┘
                       ▼
              muda o estado
                       ▼
        o sistema reativo notifica os dependentes
                       ▼
         calcula o que precisa mudar no DOM
                       ▼
            aplica ao DOM (dentro de um frame)
                       ▼
        navegador: style → layout → paint → composite
                       ▼
   └──────────────── volta a esperar ─────────────┘
```

O trabalho de um framework é fazer os passos do meio serem **corretos** (nunca mostrar estado inconsistente) e **rápidos** (caber nos 16,6 ms do arquivo `02`).

---

## 10. Onde a SPA de verdade fica maior

O que separa o exemplo acima de uma aplicação real, com ponteiro para onde cada coisa é tratada:

| Preocupação | Por que dói | Onde |
|---|---|---|
| Rotas aninhadas e layouts | menu que não remonta ao trocar de aba interna | `05` |
| Code splitting | não baixar a app inteira para ver uma tela | `05`, `09` |
| Foco e rolagem na navegação | acessibilidade e a sensação de "voltar" correto | `05`, `10` |
| Estado de servidor vs. de cliente | a distinção que resolve 80% da confusão sobre estado | `06` |
| Fronteiras de erro | um componente quebrado não pode apagar a tela toda | `06` |
| Autenticação e renovação de token | 401 no meio da sessão, refresh concorrente | `11` |
| Cache busting de assets | usuário preso numa versão antiga após deploy | `12` |
| Fallback de SPA no servidor | recarregar `/sobre` retornando 404 | `05`, `12` |
| Observabilidade | erro em produção sem stack trace legível (source maps) | `12` |
| i18n, tema, offline | cada um vira uma decisão de arquitetura | `15` |

---

## 11. Prática

No arquivo [`16-pratica.md`](16-pratica.md), o **Laboratório 1** monta uma SPA completa com as cinco peças acima, em um único arquivo HTML, sem nenhuma dependência. Recomendo fazê-lo antes de seguir para o `05` — o resto do curso fica muito mais concreto depois.

---

## 12. Autoteste

1. Por que as etapas 4, 5 e 6 da seção 2 são sequenciais, e por que isso é estrutural e não um defeito de implementação?
2. O que exatamente `history.pushState` faz — e o que ele explicitamente **não** faz?
3. Por que interceptar todo clique em `<a>` sem verificar `e.metaKey` é um bug?
4. Nas 30 linhas de `sinal()`, em que momento a dependência é registrada? Por que ela precisa ser registrada na **leitura**, e não na escrita?
5. Cite três coisas que `raiz.innerHTML = ...` destrói e que o usuário percebe.
6. Uma requisição de uma tela que o usuário já abandonou chega e sobrescreve a tela atual. Que nome tem esse bug e qual das seis falhas da seção 8 o causa?

---

**Anterior:** [03 — História](03-historia.md) · **Próximo:** [05 — Roteamento no cliente](05-roteamento.md)
