# Glossário

Todo termo técnico usado no curso. O número entre parênteses indica onde o termo é desenvolvido.

---

## A

**AJAX** *(Asynchronous JavaScript and XML)* — técnica de buscar dados do servidor em segundo plano sem recarregar a página. O XML foi substituído por JSON; o nome ficou. (`03`)

**AbortController / AbortSignal** — mecanismo padrão para cancelar requisições e outras operações assíncronas. (`05`, `08`)

**API** *(Application Programming Interface)* — contrato pelo qual dois sistemas conversam. (`08`)

**ARIA** *(Accessible Rich Internet Applications)* — atributos que descrevem papel, estado e propriedades de elementos para tecnologias assistivas. Não adiciona comportamento. (`10`)

**Árvore de acessibilidade** — estrutura derivada do DOM que leitores de tela usam para descrever a página. (`10`)

**Assets** — arquivos estáticos servidos ao navegador: JS, CSS, imagens, fontes. (`12`)

**Atualização otimista** — aplicar a mudança na interface antes da confirmação do servidor, com rollback em caso de falha. (`06`, `08`)

## B

**BFF** *(Backend for Frontend)* — backend dedicado a um frontend, que guarda os tokens e expõe sessão por cookie. Elimina o problema de armazenar token no navegador. (`11`)

**Bundle** — arquivo resultante do agrupamento dos módulos da aplicação. (`12`)

**Bundler** — ferramenta que agrupa módulos: Vite, Webpack, Rollup, esbuild. (`12`)

**Brotli** — algoritmo de compressão, ~15–20% melhor que gzip para texto. (`08`)

## C

**Cache busting** — técnica de versionar nomes de arquivo (por hash) para permitir cache eterno com atualização confiável. (`12`)

**Cascata** *(waterfall)* — sequência de requisições onde cada uma só pode começar após a anterior terminar. O principal inimigo de performance em SPAs. (`04`, `08`)

**CDN** *(Content Delivery Network)* — rede de servidores distribuídos geograficamente que serve conteúdo do ponto mais próximo do usuário. (`12`)

**Chunk** — pedaço do bundle carregado separadamente, tipicamente por rota. (`05`, `12`)

**CLS** *(Cumulative Layout Shift)* — Core Web Vital que mede quanto a página se desloca sozinha. Bom ≤ 0,1. (`09`)

**Code splitting** — dividir o bundle para carregar sob demanda. (`05`, `09`)

**Commit (fase de)** — no React, a fase síncrona e atômica em que as mudanças são aplicadas ao DOM. (`13`)

**Core Web Vitals** — LCP, INP e CLS. Métricas do Google, fator de ranqueamento. (`09`)

**CORS** *(Cross-Origin Resource Sharing)* — mecanismo pelo qual o navegador relaxa a Same-Origin Policy. **Não** protege o servidor. (`11`)

**CRDT** *(Conflict-free Replicated Data Type)* — estrutura de dados que converge automaticamente sob edições concorrentes. Base da colaboração em tempo real. (`08`)

**CSP** *(Content Security Policy)* — header que restringe de onde recursos podem ser carregados e como scripts podem executar. Principal mitigação de XSS. (`11`)

**CSR** *(Client-Side Rendering)* — HTML gerado no navegador. A SPA pura. (`07`)

**CSRF** *(Cross-Site Request Forgery)* — ataque que induz o navegador do usuário a enviar requisições autenticadas. Só se aplica a autenticação por cookie. (`11`)

**Cursor (paginação por)** — paginação por ponteiro estável em vez de deslocamento numérico. Imune a inserções concorrentes. (`08`)

## D

**Debounce** — adiar a execução até que pare de haver eventos por um intervalo. Usado em campos de busca. (`09`)

**Dependência transitiva** — dependência de uma dependência. Executa com os mesmos privilégios do seu código. (`11`)

**Diff / Reconciliação** — processo de comparar duas árvores para determinar as mudanças mínimas. (`13`)

**DOM** *(Document Object Model)* — representação em memória, viva e programável, do documento. Base técnica de toda SPA. (`02`)

**Double buffering** — manter duas árvores (atual e em construção) e trocar os ponteiros ao final. Evita exibir estado parcial. (`13`)

## E

**Edge** — computação executada em servidores próximos ao usuário. (`12`)

**ESM** *(ECMAScript Modules)* — sistema de módulos nativo (`import`/`export`). Habilita tree shaking. (`02`, `12`)

**Efeito** — no modelo reativo, função que roda em resposta a mudanças nos sinais que ela lê. (`04`, `13`)

**Event loop** — mecanismo que coordena a execução de tarefas, microtasks e renderização na thread única. (`02`)

## F

**Fetch** — API padrão para requisições HTTP. Não rejeita em erros 4xx/5xx. (`08`)

**Fiber** — arquitetura interna do React que torna a renderização interrompível. (`13`)

**Feature flag** — chave que ativa funcionalidade sem novo deploy. Desacopla deploy de release. (`12`)

**FCP** *(First Contentful Paint)* — primeiro conteúdo pintado. (`09`)

**Fronteira de erro** *(error boundary)* — componente que captura erros de sua subárvore e exibe um fallback. (`06`)

## G

**Glitch** — estado inconsistente transitório num grafo reativo, quando um efeito roda com dependências parcialmente atualizadas. Prevenido por ordem topológica. (`13`)

**GraphQL** — linguagem de consulta que permite pedir exatamente os campos necessários. Custo: cache HTTP inutilizável. (`08`)

## H

**Hidratação** *(hydration)* — processo de anexar o JavaScript ao HTML vindo do servidor. Repete o trabalho de renderização. (`07`, `13`)

**History API** — `pushState`, `replaceState`, `popstate`. Permite mudar a URL sem requisição. Peça central da SPA. (`05`)

**HttpOnly** — atributo de cookie que o torna invisível ao JavaScript. Principal defesa contra roubo de sessão por XSS. (`11`)

## I

**IDOR** *(Insecure Direct Object Reference)* — falha de autorização em que um usuário acessa recurso de outro pela manipulação de identificadores. (`11`)

**Idempotente** — operação cujo efeito é o mesmo se executada uma ou várias vezes. Determina o que pode ser repetido com segurança. (`02`, `08`)

**Ilhas (arquitetura de)** — página majoritariamente estática com pedaços interativos hidratados independentemente. (`07`)

**INP** *(Interaction to Next Paint)* — Core Web Vital que mede a latência da pior interação da sessão. Substituiu o FID em 2024. Bom ≤ 200 ms. (`09`)

**ISR** *(Incremental Static Regeneration)* — páginas estáticas regeneradas em background após um prazo. (`07`)

## J

**JSON-LD** — formato de dados estruturados para buscadores e mecanismos de resposta. (`10`)

**JWT** *(JSON Web Token)* — token assinado. Deve ser validado no servidor; decodificá-lo no cliente não é autorização. (`11`)

## K

**key** — identidade estável de item de lista, usada na reconciliação. `key={index}` é bug em listas dinâmicas. (`13`)

## L

**Layout / Reflow** — cálculo de posição e tamanho dos elementos. A etapa cara do pipeline de renderização. (`02`)

**Layout thrashing** — intercalar leituras e escritas geométricas, forçando múltiplos reflows. (`02`)

**LCP** *(Largest Contentful Paint)* — Core Web Vital que mede quando o maior elemento visível aparece. Bom ≤ 2,5 s. (`09`)

**LIS** *(Longest Increasing Subsequence)* — algoritmo `O(n log n)` usado pelo Vue para minimizar movimentos de nós. (`13`)

**Long task** — tarefa de mais de 50 ms na thread principal. Bloqueia a resposta a interações. (`02`, `09`)

## M

**Microtask** — fila de maior prioridade (Promises), esvaziada completamente antes de qualquer renderização. (`02`)

**Microfrontend** — dividir o frontend em aplicações independentes. Resolve problema organizacional, a custo técnico alto. (`15`)

**MPA** *(Multi-Page Application)* — modelo tradicional: cada navegação busca um documento novo. (`03`)

## N

**Nonce** — valor aleatório por requisição, usado na CSP para autorizar scripts inline específicos. (`11`)

## O

**OAuth 2.0 / OIDC** — protocolos de autorização e autenticação. Para SPAs: Authorization Code + PKCE. (`11`)

**Open Graph** — meta tags que controlam a pré-visualização de links. Precisam estar no HTML inicial. (`10`)

**Ordem topológica** — ordenação de um grafo dirigido acíclico que garante que dependências sejam processadas antes dos dependentes. Previne glitches. (`13`)

**Over-fetching / Under-fetching** — receber mais campos que o necessário / precisar de várias requisições para montar uma tela. (`08`)

## P

**PKCE** *(Proof Key for Code Exchange)* — extensão do OAuth que torna seguro o fluxo de código em clientes públicos. (`11`)

**Polyfill** — código que implementa um recurso ausente no navegador. (`12`)

**popstate** — evento disparado ao usar voltar/avançar. Não dispara em `pushState`. (`05`)

**PPR** *(Partial Prerendering)* — casca estática do CDN com furos dinâmicos em streaming na mesma página. (`07`)

**Prop drilling** — passar props por muitos níveis até quem precisa. Frequentemente resolvível por composição. (`06`)

**PWA** *(Progressive Web App)* — aplicação web instalável, com service worker e manifesto. (`12`)

## R

**Race condition** — resultado que depende da ordem de chegada de operações concorrentes. Comum em navegação rápida. (`05`, `08`)

**RSC** *(React Server Components)* — componentes que executam apenas no servidor; seu código não vai ao cliente. (`07`)

**Reatividade fina** *(fine-grained reactivity)* — modelo em que cada valor conhece seus dependentes e atualiza exatamente os nós afetados. Custo `O(k)`. (`04`, `13`)

**Refresh token rotation** — emitir novo refresh token a cada uso e revogar a família se um antigo reaparecer. (`11`)

**Resumabilidade** — serializar o estado e as referências de código no HTML para continuar a execução no cliente sem hidratar. (`07`)

**REST** — estilo arquitetural baseado em recursos e verbos HTTP. Sua virtude central é a cacheabilidade. (`08`)

## S

**SameSite** — atributo de cookie que controla envio em contexto cross-site. Principal mitigação de CSRF. (`11`)

**Sanitização** — remover construções perigosas de HTML não confiável antes de inseri-lo no DOM. (`11`)

**Semântica (HTML)** — usar elementos pelo significado, não pela aparência. Base de acessibilidade e SEO. (`02`, `10`)

**Service Worker** — script proxy entre a aplicação e a rede. Base de offline e PWA. Difícil de desfazer quando quebra. (`08`, `12`)

**Signal** *(sinal)* — valor reativo que rastreia quem depende dele. (`04`, `13`)

**Sinal derivado** — valor computado a partir de outros sinais, recalculado automaticamente. (`04`)

**Soft 404** — página inexistente que responde 200. Efeito colateral do fallback de SPA. (`05`, `10`)

**Source map** — mapeamento do código minificado para o original. Envie ao monitoramento, não publique. (`12`)

**SPA** *(Single Page Application)* — aplicação que carrega um documento uma vez e atualiza a tela por manipulação do DOM. (`01`)

**SRI** *(Subresource Integrity)* — hash que garante que um script externo não foi alterado. (`11`)

**SSE** *(Server-Sent Events)* — canal unidirecional servidor→cliente sobre HTTP. Reconecta sozinho. Subestimado. (`08`)

**SSG** *(Static Site Generation)* — HTML gerado no build. (`07`)

**SSR** *(Server-Side Rendering)* — HTML gerado no servidor a cada requisição. (`07`)

**Stale-while-revalidate** — servir o dado em cache imediatamente e revalidar em background. (`08`)

**Stateless** — sem memória entre requisições. Propriedade fundamental do HTTP. (`02`)

**Streaming SSR** — enviar o HTML em pedaços conforme fica pronto. (`07`)

## T

**Tearing** — dois componentes lendo valores diferentes da mesma fonte no mesmo render. Prevenido por `useSyncExternalStore`. (`06`)

**Throttle** — limitar a frequência de execução a no máximo uma vez por intervalo. (`09`)

**Transição** *(transition)* — no React, atualização de baixa prioridade, interrompível e descartável. (`09`, `13`)

**Tree shaking** — eliminar código não utilizado no build. Exige ESM e ausência de efeitos colaterais. (`12`)

**Trusted Types** — API que proíbe atribuir strings cruas a sinks perigosos como `innerHTML`. (`11`)

**TTFB** *(Time To First Byte)* — tempo até o primeiro byte da resposta. (`09`)

## U

**Union discriminada** — tipo que representa apenas estados válidos, eliminando combinações impossíveis. (`06`)

**URLPattern** — API nativa de casamento de padrões de URL. (`05`)

## V

**Virtualização** — renderizar apenas os itens visíveis de uma lista longa. Vence qualquer otimização de diff. (`09`, `13`)

**Virtual DOM** — árvore leve em memória comparada com a anterior para derivar mudanças no DOM real. Custo `O(n)`. (`13`)

**View Transitions API** — transições animadas entre estados e documentos, nativas do navegador. (`14`)

## W

**WCAG** *(Web Content Accessibility Guidelines)* — diretrizes de acessibilidade. Nível AA é o alvo prático. (`10`)

**Web Worker** — thread paralela sem acesso ao DOM. Para computação pesada. (`02`, `09`)

**WebSocket** — canal bidirecional persistente. Exige reconexão, heartbeat e ressincronização próprios. (`08`)

## X

**XSS** *(Cross-Site Scripting)* — injeção de script que executa com os privilégios da aplicação. Em SPAs, o tipo baseado em DOM é o dominante. (`11`)

---

**Voltar ao [Mapa do curso](00-MAPA.md).**
