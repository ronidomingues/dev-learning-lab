# 17 · Referências

**Nível: todos.**

Só material que eu efetivamente recomendaria. Marcado com ★ o que vale mais o tempo investido.

---

## Especificações e documentação normativa

Quando houver dúvida sobre comportamento, a spec é a autoridade — não o Stack Overflow.

- ★ **MDN Web Docs** — <https://developer.mozilla.org> · a referência prática de fato para HTML, CSS, JS e APIs do navegador. Comece sempre aqui.
- **HTML Living Standard** — <https://html.spec.whatwg.org> · inclui a History API e o modelo de sessão de navegação.
- **DOM Standard** — <https://dom.spec.whatwg.org>
- **Fetch Standard** — <https://fetch.spec.whatwg.org> · CORS e o modelo de requisição, definidos com precisão.
- **ECMAScript** — <https://tc39.es/ecma262/> · e <https://github.com/tc39/proposals> para o que vem (inclusive a proposta de Signals).
- **RFC 9110** — HTTP Semantics · <https://www.rfc-editor.org/rfc/rfc9110>
- **RFC 9111** — HTTP Caching · <https://www.rfc-editor.org/rfc/rfc9111>
- **RFC 6749 / RFC 7636** — OAuth 2.0 e PKCE
- **★ OAuth 2.0 for Browser-Based Apps** — <https://datatracker.ietf.org/doc/draft-ietf-oauth-browser-based-apps/> · a referência normativa sobre autenticação em SPA, incluindo o padrão BFF.
- **WCAG 2.2** — <https://www.w3.org/TR/WCAG22/>
- ★ **ARIA Authoring Practices Guide (APG)** — <https://www.w3.org/WAI/ARIA/apg/> · os padrões de teclado e ARIA para cada widget. Consulte antes de construir qualquer componente interativo.

---

## Documentação de frameworks

- ★ **react.dev** — a reescrita de 2023 é excelente material didático, não só referência. As seções *"You Might Not Need an Effect"* e *"Thinking in React"* valem por um livro.
- **Next.js** — <https://nextjs.org/docs> · a referência prática sobre RSC e App Router.
- ★ **Vue** — <https://vuejs.org/guide/> · a melhor documentação de reatividade que existe; útil mesmo para quem usa React.
- **Svelte** — <https://svelte.dev/docs> · e o tutorial interativo, que é modelo do gênero.
- ★ **SolidJS** — <https://docs.solidjs.com> · a explicação mais clara de reatividade fina.
- **Angular** — <https://angular.dev> · a documentação de signals é boa e independente do resto.
- **Astro** — <https://docs.astro.build> · arquitetura de ilhas.
- **TanStack Query** — <https://tanstack.com/query> · leia os *guides* mesmo se não for usar: são um curso sobre estado de servidor.
- **TanStack Router** — <https://tanstack.com/router> · roteamento com tipagem ponta a ponta.
- **Remix / React Router 7** — <https://reactrouter.com> · o modelo de loaders/actions.

---

## Performance

- ★ **web.dev** — <https://web.dev/performance> · mantido pelo time do Chrome. É a fonte primária de Core Web Vitals.
- ★ **"Optimize INP"** — <https://web.dev/articles/optimize-inp> · leitura obrigatória para SPAs.
- **Chrome DevTools docs** — <https://developer.chrome.com/docs/devtools> · aprender a usar o painel Performance rende mais que ler dez artigos.
- **CrUX** — <https://developer.chrome.com/docs/crux> · dados reais de campo, públicos.
- **"High Performance Browser Networking"**, Ilya Grigorik — <https://hpbn.co> · livro completo e gratuito. TCP, TLS, HTTP/2, latência. Envelheceu bem.
- **WebPageTest** — <https://webpagetest.org> · teste de dispositivos e redes reais.

---

## Segurança

- ★ **OWASP Top 10** — <https://owasp.org/www-project-top-ten/>
- ★ **OWASP Cheat Sheet Series** — <https://cheatsheetseries.owasp.org> · fichas práticas de XSS, CSRF, JWT, armazenamento no cliente. É o material mais denso por página desta lista.
- **Content Security Policy** — <https://web.dev/articles/strict-csp> · o guia do Google para CSP estrita com nonce.
- **Trusted Types** — <https://web.dev/articles/trusted-types>
- **PortSwigger Web Security Academy** — <https://portswigger.net/web-security> · laboratórios gratuitos e excelentes. A melhor forma de *entender* XSS é explorá-lo num ambiente controlado.

---

## Acessibilidade

- ★ **APG** (acima) — os padrões de widget.
- **WebAIM** — <https://webaim.org> · artigos práticos; o verificador de contraste é o padrão da indústria.
- **Inclusive Components**, Heydon Pickering — <https://inclusive-components.design> · como construir cada componente de forma acessível, com o raciocínio.
- **A11y Project Checklist** — <https://www.a11yproject.com/checklist/>
- **Deque axe DevTools** — extensão de navegador para auditoria.

---

## Livros

- ★ **"Refactoring UI"**, Adam Wathan & Steve Schoger · design de interface para quem não é designer. Retorno prático imediato.
- ★ **"Designing Data-Intensive Applications"**, Martin Kleppmann · não é sobre frontend, mas os capítulos sobre replicação e consistência são o que você precisa para entender cache, offline e conflito de verdade.
- **"You Don't Know JS Yet"**, Kyle Simpson · gratuito no GitHub. A referência para os fundamentos da linguagem.
- **"Inclusive Design Patterns"**, Heydon Pickering
- **"Web Performance in Action"**, Jeremy Wagner
- **"Building Micro-Frontends"**, Luca Mezzalira · leia antes de decidir; a melhor exposição dos custos.

---

## Artigos e documentos históricos

- ★ **"Ajax: A New Approach to Web Applications"**, Jesse James Garrett (2005) · o texto que batizou a técnica. Vale ler o original.
- ★ **React Server Components RFC** — <https://github.com/reactjs/rfcs/blob/main/text/0188-server-components.md> · o documento de projeto, com as alternativas rejeitadas.
- **"The Cost of JavaScript"**, Addy Osmani · a análise que fundamenta os orçamentos de bundle.
- **"Rich Harris — Have Single-Page Apps Ruined the Web?"** · a defesa mais bem articulada do modelo híbrido, pelo autor do Svelte.
- **"Islands Architecture"**, Jason Miller (2020) · a proposta original.
- **"A Guide to Streaming SSR"** — documentação do React sobre `renderToPipeableStream`.
- **"You Might Not Need an Effect"** — react.dev · corrige o erro mais comum em código React.

---

## Código-fonte que vale ler

Aprender lendo implementações é subestimado. Em ordem de dificuldade:

1. ★ **SolidJS** — `packages/solid/src/reactive/signal.ts` · a reatividade fina mais legível que existe (~500 linhas com comentários).
2. **Preact** — <https://github.com/preactjs/preact> · um VDOM completo em ~4 KB. Muito mais legível que o React.
3. **Vue 3** — `packages/runtime-core/src/renderer.ts` · procure `patchKeyedChildren` para ver o LIS aplicado.
4. **Zustand** — ~100 linhas úteis. Mostra que uma store não precisa ser complicada.
5. **Svelte** — o compilador: como uma AST vira código imperativo.
6. **React** — `ReactFiberWorkLoop.js` · duro, mas é onde o modelo de prioridades vive.

---

## Dados e pesquisas anuais

Úteis para calibrar percepção — o que o Twitter diz não é o que o mercado faz.

- **State of JS** — <https://stateofjs.com>
- **State of React** — <https://stateofreact.com>
- **Stack Overflow Developer Survey** — <https://survey.stackoverflow.co>
- **HTTP Archive Web Almanac** — <https://almanac.httparchive.org> · ★ dados reais sobre milhões de sites. O antídoto mais eficaz contra folclore.
- **Can I Use** — <https://caniuse.com> · suporte de recursos por navegador.
- **Baseline** — <https://web.dev/baseline> · quando um recurso pode ser considerado seguro de usar.

---

## Pessoas que vale acompanhar

Não pelo entusiasmo — pela qualidade do raciocínio, inclusive quando discordam entre si:

- **Dan Abramov** — modelo mental do React, RSC.
- **Rich Harris** — Svelte; a crítica mais lúcida ao excesso de SPA.
- **Ryan Carniato** — Solid; escreve os melhores artigos técnicos sobre reatividade e renderização.
- **Addy Osmani** — performance, custo do JavaScript.
- **Jake Archibald** — internals do navegador, service workers, event loop. Sua palestra *"In The Loop"* é a melhor explicação do event loop que existe.
- **Una Kravets / Adam Argyle** — CSS moderno e plataforma.
- **Heydon Pickering** — acessibilidade, com humor.
- **Kent C. Dodds** — testes e padrões de React.
- **Evan You** — Vue, Vite.
- **Miško Hevery** — Qwik, resumabilidade.

---

## Ferramentas

**Desenvolvimento:** Vite · TypeScript · Biome ou ESLint+Prettier · Zod
**Testes:** Vitest · Testing Library · Playwright · MSW (mock de rede) · jest-axe
**Performance:** Lighthouse CI · size-limit · source-map-explorer · WebPageTest · web-vitals
**Acessibilidade:** axe DevTools · pa11y · NVDA · VoiceOver
**Segurança:** npm audit · osv-scanner · securityheaders.com · Observatory
**Observabilidade:** Sentry · OpenTelemetry

---

## Como continuar estudando

1. **Vá à fonte.** Um artigo de blog é a interpretação de alguém. A spec e o código-fonte são a coisa.
2. **Leia código de framework.** Uma hora lendo o Solid ensina mais sobre reatividade que dez artigos.
3. **Meça em vez de acreditar.** Inclusive o que este curso afirma — quase tudo aqui é verificável no seu próprio projeto.
4. **Construa o pequeno para entender o grande.** Um roteador de 80 linhas explica o React Router inteiro.
5. **Acompanhe quem discorda.** O debate entre Dan Abramov e Rich Harris ensina mais que concordar com qualquer um dos dois.
6. **Prefira o durável.** HTTP, DOM, event loop e complexidade continuarão valendo em 2040. O framework da moda, não.

---

**Anterior:** [16 — Prática](16-pratica.md) · **Índice:** [00 — Mapa](00-MAPA.md) · **Glossário:** [GLOSSARIO.md](GLOSSARIO.md)
