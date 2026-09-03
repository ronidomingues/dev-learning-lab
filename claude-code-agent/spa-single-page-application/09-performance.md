# 09 · Performance

**Nível: avançado** · Pré-requisitos: `02` (event loop e pipeline de renderização), `04`, `08`.

Performance não é uma etapa final de polimento. É uma **restrição de projeto**, e quase sempre é consequência de decisões arquiteturais tomadas meses antes. Este arquivo cobre como medir, o que medir, e o que efetivamente muda os números.

---

## 1. Core Web Vitals

Métricas do Google, fator de ranqueamento desde 2021, medidas em **usuários reais** — não no seu laptop.

| Métrica | O que mede | Bom | Ruim |
|---|---|---|---|
| **LCP** — Largest Contentful Paint | quando o maior elemento visível aparece | ≤ 2,5 s | > 4,0 s |
| **INP** — Interaction to Next Paint | latência da pior interação da sessão | ≤ 200 ms | > 500 ms |
| **CLS** — Cumulative Layout Shift | quanto a página pula sozinha | ≤ 0,1 | > 0,25 |

Métricas de apoio, úteis para diagnóstico:

- **TTFB** — tempo até o primeiro byte. Isola servidor/rede do resto.
- **FCP** — primeiro conteúdo pintado (às vezes só um spinner — cuidado).
- **TBT** — total blocking time. Proxy de laboratório para o INP.

O critério oficial é o **percentil 75** dos usuários reais. Sua média está sempre melhor que a realidade, porque a distribuição tem cauda longa: a mediana é um celular médio numa rede média; o p75 inclui o Android de entrada em 4G ruim.

> **INP substituiu o FID em março de 2024.** A mudança importa: o FID media apenas o atraso da *primeira* interação, e era fácil de enganar. O INP mede o tempo do clique **até a próxima pintura**, na pior interação da sessão inteira. É a métrica que efetivamente captura a sensação de "esse app é lento", e é onde SPAs mal construídas falham.

---

## 2. Medir antes de otimizar

### Laboratório — reprodutível, mas não é a realidade

```bash
npx lighthouse https://exemplo.com --preset=desktop --view
npx unlighthouse --site exemplo.com     # varre o site todo
```

No DevTools: aba **Performance** com *CPU throttling 4x* e *Network Fast 4G*. **Sem throttling, você está medindo o seu computador, não o do usuário** — este é o erro de medição mais comum que existe.

### Campo — a verdade

```js
import { onLCP, onINP, onCLS, onTTFB } from 'web-vitals';

function enviar(metrica) {
  navigator.sendBeacon('/api/vitals', JSON.stringify({
    nome: metrica.name,
    valor: metrica.value,
    avaliacao: metrica.rating,
    alvo: metrica.attribution?.interactionTarget,   // QUAL elemento causou o INP ruim
    rota: location.pathname,
    conexao: navigator.connection?.effectiveType,
  }));
}

onLCP(enviar); onINP(enviar); onCLS(enviar); onTTFB(enviar);
```

O campo `attribution` é o que transforma "o INP está em 480 ms" em "o INP está em 480 ms **por causa deste botão nesta rota**". Sem ele você está adivinhando.

Fontes de dados de campo: CrUX (Chrome User Experience Report, público, agregado), ou RUM próprio como acima.

---

## 3. Corrigindo o LCP

O LCP quase sempre é uma **imagem grande** ou um **bloco de texto**. Diagnostique nesta ordem:

```
LCP = TTFB + atraso de carga do recurso + tempo de carga + atraso de render
```

| Parte alta | Causa provável | Correção |
|---|---|---|
| TTFB | servidor lento, sem CDN, sem cache | CDN, cache de página, streaming SSR |
| atraso de carga | o recurso é descoberto tarde | `preload`, `fetchpriority`, evitar carregar imagem por JS |
| tempo de carga | imagem enorme | formato moderno, dimensionamento, compressão |
| atraso de render | JS/CSS bloqueando | CSS crítico inline, SSR |

**A causa número um de LCP ruim em SPA** é estrutural e já foi explicada no arquivo `04`: o elemento LCP só existe **depois** que o JS baixa, executa e busca os dados. Nenhuma micro-otimização conserta isso — a correção é arquitetural: SSR, SSG ou ilhas (arquivo `07`).

Correções táticas quando você não pode mudar a arquitetura:

```html
<!-- imagem do LCP: descoberta cedo, prioridade alta, dimensões conhecidas -->
<link rel="preload" as="image" href="/heroi.webp" fetchpriority="high">
<img src="/heroi.webp" width="1200" height="600" fetchpriority="high"
     decoding="async" alt="…">
```

```html
<!-- NUNCA lazy-load na imagem do LCP: adia justamente o que você quer cedo -->
<img loading="lazy">   <!-- só para imagens ABAIXO da dobra -->
```

E fontes, causa frequente e subestimada de LCP e CLS:

```css
@font-face {
  font-family: 'Inter';
  src: url('/inter.woff2') format('woff2');
  font-display: swap;          /* mostra em fonte de sistema já, troca depois */
  size-adjust: 105%;           /* alinha as métricas e reduz o salto na troca */
}
```

```html
<link rel="preload" href="/inter.woff2" as="font" type="font/woff2" crossorigin>
```

---

## 4. Corrigindo o INP — a métrica das SPAs

INP é onde SPAs perdem. Ele decompõe em três partes:

```
INP = atraso de entrada + tempo de processamento + atraso de apresentação
      (thread ocupada)    (seu handler)            (render do navegador)
```

### 4.1 Quebrar as long tasks

Qualquer tarefa acima de 50 ms bloqueia a resposta a cliques (arquivo `02`, seção 6).

```js
// Quebrar trabalho longo, devolvendo o controle ao navegador
async function processar(itens) {
  for (let i = 0; i < itens.length; i++) {
    trabalhar(itens[i]);
    if (i % 50 === 0) await scheduler.yield();   // deixa o navegador respirar
  }
}
```

`scheduler.yield()` (Chrome 129+, 2024) é superior ao velho `await new Promise(r => setTimeout(r, 0))` porque **preserva a prioridade** da continuação — com `setTimeout` você vai para o fim da fila.

### 4.2 Separar urgente de não urgente

```jsx
const [busca, setBusca] = useState('');
const [resultadosDe, setResultadosDe] = useState('');
const [pendente, startTransition] = useTransition();

function aoDigitar(v) {
  setBusca(v);                                    // URGENTE: o campo responde já
  startTransition(() => setResultadosDe(v));      // NÃO URGENTE: pode ser interrompido
}
```

O React trata a segunda atualização como interrompível: se o usuário digitar de novo, o trabalho em curso é descartado. Isso é a renderização concorrente resolvendo um problema real de INP.

### 4.3 Mover CPU para fora da thread principal

```js
// Web Worker: parsing pesado, criptografia, processamento de imagem, cálculo
const worker = new Worker(new URL('./calculo.js', import.meta.url), { type: 'module' });
worker.postMessage({ dados });
worker.onmessage = (e) => setResultado(e.data);
```

Use `Comlink` para uma API decente em cima da troca de mensagens. Lembre: worker não acessa o DOM, e a serialização das mensagens tem custo (use `Transferable` para buffers grandes).

### 4.4 Virtualizar listas

Renderizar 5.000 linhas cria 5.000 nós, e cada interação precisa lidar com todos eles.

```jsx
import { useVirtualizer } from '@tanstack/react-virtual';
const v = useVirtualizer({ count: 10_000, getScrollElement: () => ref.current,
                           estimateSize: () => 40, overscan: 5 });
// renderiza ~20 linhas em vez de 10.000
```

### 4.5 Debounce e throttle nos lugares certos

```js
const debounce = (fn, ms) => { let t; return (...a) => { clearTimeout(t); t = setTimeout(() => fn(...a), ms); }; };
const throttle = (fn, ms) => { let ok = true; return (...a) => { if (!ok) return; ok = false; fn(...a); setTimeout(() => ok = true, ms); }; };
```

Debounce para busca (300 ms); throttle para `scroll` e `resize` — ou, melhor, `IntersectionObserver` e `ResizeObserver`, que não rodam na thread a cada evento.

E sempre `{ passive: true }` em listeners de `scroll`, `touchstart` e `wheel`: sem isso o navegador precisa esperar seu handler para saber se você vai chamar `preventDefault`, o que trava a rolagem.

---

## 5. Corrigindo o CLS

Conteúdo que se move depois de aparecer. Causas, em ordem de frequência:

**1. Imagens sem dimensão.**
```html
<img src="foto.jpg" width="800" height="600" alt="">   <!-- reserva o espaço -->
```
Com `width` e `height` no HTML, o navegador reserva a caixa via *aspect ratio* mesmo com CSS responsivo. Duas linhas que resolvem a maior parte dos CLS.

**2. Conteúdo injetado acima do existente** — banners, avisos de cookie, anúncios. Reserve o espaço com `min-height` ou use `position: fixed`/overlay.

**3. Fontes** — a troca de fonte de fallback para a definitiva reflui o texto. `size-adjust` e `font-display: swap` mitigam.

**4. Skeleton com tamanho diferente do conteúdo real.** Um esqueleto que não tem a altura do conteúdo troca um problema por outro.

**5. Animar `width`, `height`, `top`, `left`.** Anime `transform` e `opacity` — não disparam layout (arquivo `02`, seção 4).

```css
.item { will-change: transform; }   /* use com parcimônia: cada camada consome memória de GPU */
```

---

## 6. Orçamento de JavaScript

O recurso mais caro de uma SPA não é o download — é o **parse, compile e execute**, que é CPU, e CPU de celular de entrada é 5 a 10 vezes mais lenta que a do seu laptop.

Ordem de grandeza para orientar decisões:

| JS (comprimido) | Celular de entrada | Veredito |
|---|---|---|
| 50 KB | ~0,3 s | excelente |
| 170 KB | ~1,0 s | limite recomendado |
| 500 KB | ~3,0 s | problemático |
| 1 MB+ | ~6,0 s+ | inaceitável |

Coloque isso no CI, senão o bundle cresce sozinho:

```json
// package.json — size-limit
{ "size-limit": [{ "path": "dist/assets/*.js", "limit": "170 KB" }] }
```

### Analisar o que está lá dentro

```bash
npx vite-bundle-visualizer
npx source-map-explorer 'dist/assets/*.js'
```

Ofensores clássicos e suas substituições:

| Peso | Pacote | Alternativa |
|---|---|---|
| ~70 KB | `moment` | `date-fns` (tree-shakeable) ou `Intl.DateTimeFormat` nativo |
| ~70 KB | `lodash` inteiro | `lodash-es` com import nomeado, ou métodos nativos |
| variável | biblioteca de ícones inteira | importar só os ícones usados |
| ~500 KB+ | Chart.js/D3 completos | carregar sob demanda, ou usar módulos específicos do D3 |
| grande | `polyfill` para navegadores mortos | `browserslist` realista |

### Import dinâmico para o que é pesado e raro

```js
// carrega só quando o usuário abre o editor
const { default: Editor } = await import('./EditorRico.js');
```

---

## 7. Otimização de imagens

Imagens costumam ser a maior fatia dos bytes de uma página, e a mais fácil de reduzir.

```html
<picture>
  <source type="image/avif" srcset="foto-400.avif 400w, foto-800.avif 800w, foto-1600.avif 1600w"
          sizes="(max-width: 600px) 100vw, 50vw">
  <source type="image/webp" srcset="foto-400.webp 400w, foto-800.webp 800w, foto-1600.webp 1600w"
          sizes="(max-width: 600px) 100vw, 50vw">
  <img src="foto-800.jpg" width="800" height="600" alt="Descrição real"
       loading="lazy" decoding="async">
</picture>
```

- **AVIF** — melhor compressão (~50% menor que JPEG), codificação lenta. Suporte universal desde 2024.
- **WebP** — bom equilíbrio, suporte total.
- **`srcset` + `sizes`** — não mande uma imagem de 1600px para uma tela de 400px.
- **`loading="lazy"`** — abaixo da dobra, nunca no LCP.
- **`content-visibility: auto`** — pula layout e paint de seções fora da tela:

```css
.secao-longa { content-visibility: auto; contain-intrinsic-size: auto 500px; }
```

---

## 8. O metaproblema: performance percebida

O número não é a experiência. Duas páginas com o mesmo LCP podem parecer muito diferentes.

- **Esqueletos** com a forma do conteúdo real parecem mais rápidos que spinners, porque comunicam o que vem.
- **Retorno imediato** em toda interação: se algo leva mais de 100 ms, mostre reconhecimento antes.
- **Otimismo** (arquivo `08`) elimina espera percebida por completo.
- **Preload no hover** (arquivo `05`) transforma 300 ms em zero.
- **Manter a tela antiga** durante a transição (`useTransition`) parece mais rápido do que trocar por um spinner — e evita CLS.
- **Ordem de revelação:** mostre o que existe assim que existe, em vez de esperar tudo.

E um princípio que vale mais que a lista: **latência consistente é melhor que latência média baixa com variância alta.** Uma interface previsivelmente em 200 ms é percebida como melhor que uma que oscila entre 50 e 800 ms.

---

## 9. Ordem de ataque

Quando alguém diz "o app está lento", siga esta ordem — ela vai do maior retorno para o menor:

1. **Meça no campo.** Descubra qual métrica, qual rota, qual dispositivo. Sem isso você vai otimizar a coisa errada.
2. **Verifique a arquitetura.** LCP ruim numa SPA pura é o modelo, não o código. Nenhuma micro-otimização substitui SSR/SSG quando é esse o caso.
3. **Cascatas de rede.** DevTools → Network com throttling. Costuma ser o maior ganho isolado.
4. **Tamanho do bundle.** Analise, corte, divida por rota, carregue o raro sob demanda.
5. **Long tasks.** Performance → tarefas acima de 50 ms. Quebre, adie, mande para worker.
6. **Imagens.** Formato, dimensionamento, `srcset`, lazy fora da dobra.
7. **CLS.** Dimensões explícitas, espaço reservado, `transform` em animações.
8. **Micro-otimizações de render.** Memoização, virtualização. **Por último**, e só com medição — com o React Compiler, boa parte disso é automática.
9. **Trave o resultado no CI.** Orçamento de bundle e Lighthouse CI, senão a regressão volta em duas semanas.

```yaml
# CI — impede regressão
- run: npx size-limit
- run: npx lhci autorun --collect.url=https://preview.exemplo.com
```

---

## 10. Autoteste

1. Por que medir sem CPU throttling produz conclusões erradas?
2. Por que o INP substituiu o FID, e por que ele é a métrica mais reveladora para SPAs?
3. Decomponha o LCP em quatro partes e dê uma correção para cada.
4. Por que o LCP ruim de uma SPA pura é um problema arquitetural e não de código?
5. Qual a diferença entre `scheduler.yield()` e `setTimeout(fn, 0)`?
6. Por que `{ passive: true }` importa em listeners de scroll?
7. Por que animar `left` é pior que animar `transform`?
8. Duas telas têm LCP de 2,0 s, mas uma parece mais rápida. Cite três razões possíveis.

---

**Anterior:** [08 — Dados e rede](08-dados-e-rede.md) · **Próximo:** [10 — SEO e acessibilidade](10-seo-acessibilidade.md)
