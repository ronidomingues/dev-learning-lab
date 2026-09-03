# 10 · SEO e acessibilidade

**Nível: avançado** · Pré-requisitos: `02`, `05`, `07`.

Estes dois assuntos aparecem juntos por um motivo que não é organizacional: **eles quebram pela mesma causa raiz.** Buscadores e tecnologias assistivas foram construídos assumindo que o significado está no HTML. A SPA move o significado para dentro de um programa. As duas coisas sofrem juntas, e as correções se sobrepõem.

---

# Parte I — SEO

## 1. O que o buscador faz

```
Descoberta → Rastreamento (crawl) → Renderização → Indexação → Ranqueamento
```

O passo que interessa é a **renderização**. O Googlebot executa JavaScript — usa uma versão recente do Chromium — mas isso vem com três ressalvas que decidem tudo:

1. **A renderização é adiada.** Páginas que exigem JS entram numa fila separada. O atraso costuma ser de horas a dias. Para notícias, promoções e vagas, isso é fatal.
2. **Há orçamento.** Renderizar custa CPU. Sites grandes recebem uma fatia; páginas podem simplesmente não ser renderizadas.
3. **Os outros não executam JavaScript de forma confiável.** Bing melhorou, mas é irregular. E — o ponto que mudou o cálculo desde 2024 — **os rastreadores de LLMs e mecanismos de resposta majoritariamente não executam JavaScript**. Se o seu conteúdo só existe após o JS rodar, você está invisível para uma fatia crescente e cada vez mais relevante do tráfego de descoberta.

> **Conclusão prática, e ela é mais forte em 2026 do que era em 2020:** se conteúdo público precisa ser encontrado, **ele tem que estar no HTML da resposta**. SSR, SSG ou pré-renderização. Confiar na renderização de JS pelo buscador é uma aposta com prazo, e o prazo piorou.

Verificação em cinco segundos:

```bash
curl -s https://seusite.com/produtos/42 | grep -i "nome do produto"
# vazio? seu conteúdo não existe para quem não executa JS.
```

---

## 2. Os requisitos, em ordem de importância

### 2.1 URLs reais e únicas

Uma URL por conteúdo, estável, com History API (nunca hash para conteúdo público) e navegação por `<a href>` de verdade:

```html
<a href="/produtos/42">Ver produto</a>          <!-- rastreável -->
<div onclick="navegar('/produtos/42')">…</div>  <!-- invisível para o crawler -->
```

Isso vale mesmo com JavaScript interceptando o clique: o `href` precisa existir e funcionar sozinho.

### 2.2 Status HTTP corretos

O problema que o `try_files ... /index.html` cria (arquivo `05`, seção 6.5): toda URL inexistente responde **200 com o shell**. Isso é um *soft 404*, e o buscador acaba indexando lixo.

| Situação | Certo | Errado e comum |
|---|---|---|
| não existe | 404 | 200 com "não encontrado" na tela |
| mudou de lugar | 301 | link de cliente |
| exige login | 401/403 ou 200 com `noindex` | 200 com conteúdo vazio |
| fora do ar | 503 com `Retry-After` | 200 com erro na tela |

Só SSR resolve isso corretamente. Numa SPA pura, o paliativo é a rota 404 do cliente injetar `<meta name="robots" content="noindex">`.

### 2.3 Metadados por rota

```html
<title>Camiseta preta — Minha Loja</title>
<meta name="description" content="Camiseta 100% algodão…">
<link rel="canonical" href="https://loja.com/produtos/42">
<meta property="og:title" content="Camiseta preta">
<meta property="og:image" content="https://loja.com/img/42-og.jpg">
<meta name="twitter:card" content="summary_large_image">
```

**As tags Open Graph precisam estar no HTML inicial.** WhatsApp, Slack, Discord, LinkedIn e X não executam JavaScript ao gerar a pré-visualização de um link. Inserir OG por JavaScript não funciona — é um dos erros mais frequentes e mais fáceis de detectar (compartilhe o link consigo mesmo e veja).

`canonical` é essencial em SPAs porque parâmetros de rastreamento (`?utm_source=...`) multiplicam a mesma página em dezenas de URLs.

### 2.4 Dados estruturados

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "Camiseta preta",
  "offers": { "@type": "Offer", "price": "79.00", "priceCurrency": "BRL",
              "availability": "https://schema.org/InStock" }
}
</script>
```

Habilita resultados enriquecidos (preço, estrelas, estoque, FAQ, breadcrumb) e — cada vez mais importante — é o que os mecanismos de resposta baseados em LLM leem com mais confiabilidade. Valide em `search.google.com/test/rich-results`.

### 2.5 Sitemap e robots

```xml
<url><loc>https://loja.com/produtos/42</loc><lastmod>2026-08-01</lastmod></url>
```

```
# robots.txt
User-agent: *
Allow: /
Disallow: /admin/
Sitemap: https://loja.com/sitemap.xml
```

Não bloqueie seus arquivos JS e CSS no robots.txt — o Googlebot precisa deles para renderizar. Foi prática comum anos atrás e ainda aparece em configurações herdadas.

---

## 3. Diagnóstico

| Ferramenta | Para quê |
|---|---|
| Search Console → Inspeção de URL | ver o **HTML renderizado** que o Google obteve |
| `curl` sem JS | ver o HTML bruto — o que os rastreadores sem JS veem |
| Rich Results Test | validar dados estruturados |
| Screaming Frog (modo JS) | rastrear o site inteiro como um buscador |
| Search Console → Cobertura | descobrir páginas não indexadas e o motivo |

---

# Parte II — Acessibilidade

## 4. Por que SPAs quebram

Um leitor de tela é um usuário que **não vê a tela**. Ele constrói um modelo do documento a partir da **árvore de acessibilidade**, derivada do DOM.

Numa navegação real, o navegador reseta tudo: anuncia o novo documento, move o foco, lê o título. Numa SPA, **nada disso acontece automaticamente**. Do ponto de vista do leitor de tela, a pessoa clicou num link e o documento continua exatamente o mesmo — só que agora com conteúdo diferente que ninguém avisou que mudou.

## 5. As cinco correções obrigatórias

### 5.1 Anunciar a mudança de rota

```js
function aposNavegar(titulo) {
  document.title = `${titulo} — Minha App`;

  const principal = document.querySelector('#conteudo');
  principal.setAttribute('tabindex', '-1');
  principal.focus({ preventScroll: true });        // move o foco

  document.querySelector('#anunciador').textContent = `${titulo} carregado`;
}
```

```html
<div id="anunciador" aria-live="polite" aria-atomic="true" class="sr-only"></div>
```

```css
.sr-only {
  position: absolute; width: 1px; height: 1px;
  padding: 0; margin: -1px; overflow: hidden;
  clip: rect(0,0,0,0); white-space: nowrap; border: 0;
}
```

Note: `display: none` **remove** do leitor de tela. Para esconder visualmente mantendo acessível, use a classe acima.

### 5.2 Gerenciar o foco

O foco é a posição do cursor de quem navega por teclado. Perdê-lo é o equivalente a jogar o mouse de alguém para fora da tela.

| Situação | O que fazer |
|---|---|
| Nova rota | foco no container do conteúdo principal |
| Modal abre | foco no primeiro elemento focável, e **prender** o foco dentro |
| Modal fecha | foco de volta ao elemento que o abriu |
| Item removido de lista | foco no item seguinte, ou no container |
| Erro de formulário | foco no primeiro campo com erro |
| Conteúdo expandido | foco permanece no gatilho; use `aria-expanded` |

```jsx
// Modal: use <dialog>, que dá trap de foco e Escape de graça
<dialog ref={ref} onClose={() => gatilhoRef.current?.focus()}>
  <h2>Confirmar</h2>
  <button onClick={() => ref.current.close()}>Fechar</button>
</dialog>
// ref.current.showModal()
```

Em 2026, `<dialog>` tem suporte universal e resolve corretamente trap de foco, `inert` no resto da página, e fechamento por Escape. Escrever um modal do zero em 2026 é quase sempre um erro.

E nunca remova o indicador de foco:

```css
:focus-visible { outline: 2px solid currentColor; outline-offset: 2px; }
/* NUNCA: *:focus { outline: none } */
```

### 5.3 HTML semântico antes de ARIA

```html
<!-- ERRADO: nada disso existe para teclado nem leitor de tela -->
<div class="btn" onclick="salvar()">Salvar</div>

<!-- CERTO: focável, ativável por Enter/Espaço, anunciado como botão -->
<button type="button" onclick="salvar()">Salvar</button>
```

A regra que resume o assunto: **a primeira regra do ARIA é não usar ARIA.** Se existe um elemento HTML nativo, use-o. ARIA não adiciona comportamento — só rótulos e estados. Um `<div role="button">` precisa que você implemente `tabindex`, `keydown` para Enter e Espaço, e o estado de pressionado. Você vai esquecer algum.

Estrutura de página que o leitor de tela usa para navegar:

```html
<body>
  <a href="#conteudo" class="pular">Pular para o conteúdo</a>
  <header><nav aria-label="Principal">…</nav></header>
  <main id="conteudo" tabindex="-1">
    <h1>Um h1 por página</h1>
    <section aria-labelledby="t1"><h2 id="t1">…</h2></section>
  </main>
  <footer>…</footer>
</body>
```

Hierarquia de títulos sem pular níveis (h1 → h2 → h3): é o índice pelo qual usuários de leitor de tela navegam o documento.

### 5.4 Anunciar estados dinâmicos

```html
<!-- carregando -->
<div aria-busy="true" aria-live="polite">Carregando resultados…</div>

<!-- resultados de busca -->
<div aria-live="polite">{n} resultados encontrados</div>

<!-- erro: assertive interrompe o que estiver sendo lido -->
<div role="alert">Falha ao salvar. Tente novamente.</div>

<!-- campo com erro -->
<input id="email" aria-invalid="true" aria-describedby="err-email">
<p id="err-email" role="alert">E-mail inválido</p>
```

`polite` espera a leitura atual terminar; `assertive`/`role="alert"` interrompe. Use `assertive` só para o que é urgente — abusar dele torna a aplicação insuportável.

**A região `aria-live` precisa existir no DOM antes** do conteúdo mudar. Inserir o elemento já com texto frequentemente não é anunciado.

### 5.5 Respeitar as preferências do sistema

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

Movimento não é estética para quem tem distúrbio vestibular — pode causar náusea real. O mesmo vale para `prefers-color-scheme` e `prefers-contrast`.

---

## 6. Padrões de SPA que exigem cuidado extra

| Padrão | Problema | Correção |
|---|---|---|
| Scroll infinito | rodapé inalcançável; leitor de tela se perde | botão "carregar mais"; anunciar quantos itens chegaram |
| Toast/notificação | não é anunciado; some rápido demais | `role="status"`; não sumir sozinho se houver ação |
| Skeleton | leitor lê estrutura vazia sem sentido | `aria-busy="true"` no container; `aria-hidden` no esqueleto |
| Tabela virtualizada | contagem errada de linhas | `aria-rowcount` e `aria-rowindex` reais |
| Drag and drop | inacessível por teclado | alternativa por teclado ou menu "mover para" |
| Autocomplete | precisa do padrão combobox completo | use uma biblioteca headless testada |
| Menu customizado | sem navegação por setas | siga o padrão APG, ou use headless |

**Recomendação forte:** para componentes complexos (combobox, menu, tabs, tooltip, date picker), use bibliotecas *headless* que já implementaram os padrões da APG — **Radix UI**, **React Aria** (Adobe), **Headless UI**, **Ark UI**. A acessibilidade desses widgets envolve dezenas de detalhes de teclado e ARIA. Reimplementá-los é trabalho de meses feito pior.

---

## 7. Testar

```bash
npx @axe-core/cli https://exemplo.com
npx pa11y https://exemplo.com
```

```js
// no CI, com testing-library
import { axe } from 'jest-axe';
test('sem violações', async () => {
  const { container } = render(<Pagina />);
  expect(await axe(container)).toHaveNoViolations();
});
```

**Ferramentas automatizadas detectam cerca de 30–40% dos problemas reais.** Elas acham contraste, `alt` faltando, rótulo ausente. Não acham foco perdido, ordem ilógica, anúncio faltando na navegação, ou um fluxo impossível de completar por teclado.

O teste que vale mais que todos os outros, e leva dez minutos:

1. **Guarde o mouse.** Percorra o fluxo principal só com Tab, Shift+Tab, Enter, Espaço, setas e Escape. Se você não consegue completar uma compra, ninguém que depende de teclado consegue.
2. **Ligue um leitor de tela.** NVDA (Windows, grátis), VoiceOver (macOS/iOS, Cmd+F5), TalkBack (Android). Feche os olhos e navegue. É desconfortável na primeira vez e é o exercício mais esclarecedor que existe nesta área.
3. **Zoom em 200%.** Nada pode sumir ou exigir rolagem horizontal.

---

## 8. Conformidade

**WCAG 2.2** (2023) é a referência atual; **WCAG 3.0** segue em rascunho. Níveis A, AA, AAA — **AA é o alvo prático** e o exigido pela maioria das legislações.

Contexto legal em 2026: o *European Accessibility Act* entrou em vigor em junho de 2025 e alcança comércio eletrônico, bancos e transporte que operam na UE. Nos EUA, ADA + Section 508. No Brasil, a **LBI (Lei 13.146/2015)** exige acessibilidade em sites, e o **eMAG** rege o setor público federal. Isso deixou de ser boa vontade e passou a ser risco jurídico.

E, mais importante que o argumento legal: cerca de **1 em cada 6 pessoas** vive com alguma deficiência. Acessibilidade também beneficia quem está com o braço quebrado, no sol forte, com internet ruim, ou com 70 anos e presbiopia. Você está construindo para todos eles.

---

## 9. Checklist combinado

**SEO**
- [ ] O conteúdo aparece em `curl` sem JavaScript
- [ ] Cada conteúdo tem URL própria e estável, com `<a href>` real
- [ ] 404 retorna 404; redirects são 301/302 de servidor
- [ ] `<title>`, `description` e `canonical` por rota
- [ ] Open Graph **no HTML inicial**
- [ ] Dados estruturados JSON-LD validados
- [ ] `sitemap.xml` e `robots.txt`; JS/CSS não bloqueados
- [ ] Core Web Vitals no verde (arquivo `09`)

**Acessibilidade**
- [ ] Todo fluxo principal é completável só com teclado
- [ ] Foco visível em todo elemento interativo
- [ ] Mudança de rota move o foco e é anunciada
- [ ] Modais: trap de foco, Escape, retorno do foco ao fechar
- [ ] HTML semântico; ARIA só onde não há elemento nativo
- [ ] Um `h1` por página, hierarquia sem saltos
- [ ] `alt` significativo (ou `alt=""` se decorativa)
- [ ] Contraste ≥ 4,5:1 para texto normal, 3:1 para texto grande e componentes
- [ ] Erros de formulário associados por `aria-describedby` e anunciados
- [ ] `prefers-reduced-motion` respeitado
- [ ] Testado com leitor de tela real
- [ ] Zoom 200% sem perda de conteúdo

---

## 10. Autoteste

1. Por que SEO e acessibilidade quebram pela mesma causa numa SPA?
2. Por que meta tags Open Graph inseridas por JavaScript não funcionam?
3. O que é um soft 404, como uma SPA o produz e como corrigir?
4. Cite três coisas que o navegador faz numa navegação real e que a SPA precisa refazer.
5. Por que `<div onclick>` é pior que `<button>`? Liste tudo que se perde.
6. Qual a diferença entre `aria-live="polite"` e `role="alert"`?
7. Por que ferramentas automatizadas detectam só 30–40% dos problemas, e o que preenche o resto?
8. Por que o argumento sobre rastreadores de LLM fortalece o caso do SSR em 2026?

---

**Anterior:** [09 — Performance](09-performance.md) · **Próximo:** [11 — Segurança](11-seguranca.md)
