# 12 · Build, deploy e infraestrutura

**Nível: avançado** · Pré-requisitos: `08`, `09`.

Do código-fonte aos bytes que chegam no navegador de alguém em produção. Esta camada é invisível quando funciona e é a causa de incidentes memoráveis quando não.

---

## 1. Por que existe um build

O navegador não executa TypeScript, JSX, Sass ou o grafo de milhares de módulos do `node_modules` de forma eficiente. O build resolve seis problemas:

1. **Transformar** — TS/JSX → JS que os navegadores-alvo entendem.
2. **Resolver** — transformar `import 'react'` num caminho real.
3. **Agrupar** — reunir milhares de módulos em poucos arquivos.
4. **Otimizar** — minificar, eliminar código morto, hoisting de escopo.
5. **Versionar** — nomes com hash para cache eterno seguro.
6. **Dividir** — chunks por rota e por dependência compartilhada.

---

## 2. Ferramentas em 2026

| Ferramenta | Papel | Situação |
|---|---|---|
| **Vite** | dev server + build | padrão de fato; ESM nativo em dev, Rollup/Rolldown no build |
| **Rolldown** | bundler em Rust | substituindo o Rollup dentro do Vite; ganho grande de velocidade |
| **esbuild** | transformador em Go | rápido; usado dentro de outras ferramentas |
| **SWC** | transformador em Rust | substituiu o Babel na maioria dos casos |
| **Turbopack** | bundler do Next.js | em Rust, foco em builds incrementais |
| **Rspack** | port do Webpack em Rust | migração barata para quem tem config Webpack grande |
| **Webpack** | bundler clássico | maduro, lento, ainda onipresente em legado |
| **Parcel** | zero-config | nicho |

A tendência é clara e vale registrar: **as ferramentas de JavaScript estão sendo reescritas em Rust e Go.** A diferença é de ordem de grandeza — um build que levava 90 s cai para 5 s, e o dev server que levava 30 s para subir passa a ser instantâneo. Isso muda o ritmo de trabalho, não só o número.

### O que torna o Vite diferente em desenvolvimento

```
Webpack (dev):  agrupa TUDO antes de servir a primeira página  → lento e piora com o projeto
Vite (dev):     serve módulos ESM nativos sob demanda           → constante, independe do tamanho
```

O navegador moderno entende `import`. O Vite serve cada módulo transformado individualmente e deixa o navegador montar o grafo. Só as dependências de `node_modules` são pré-agrupadas (com esbuild), porque elas mudam raramente e têm muitos arquivos pequenos.

---

## 3. Configuração de produção

```js
// vite.config.js
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  build: {
    target: 'es2022',
    sourcemap: 'hidden',            // gera, mas não referencia no bundle: envie ao Sentry
    rollupOptions: {
      output: {
        // separa dependências que mudam pouco: o usuário recacheia menos
        manualChunks: {
          vendor: ['react', 'react-dom'],
          graficos: ['d3', 'recharts'],
        },
      },
    },
    chunkSizeWarningLimit: 500,
  },
});
```

```
# .browserslistrc — define o alvo real. Não coloque navegadores mortos aqui.
> 0.5%
last 2 versions
not dead
```

O `browserslist` controla quanto o build precisa transpilar e quantos polyfills entram. Suportar navegadores irrelevantes penaliza **todos** os usuários com bytes extras.

### Tree shaking — e por que ele falha

Eliminação de código não usado. Depende de:

- **ES Modules** (`import`/`export`). CommonJS (`require`) é dinâmico demais para analisar.
- **Ausência de efeitos colaterais.** Declare no `package.json`:

```json
{ "sideEffects": false }
{ "sideEffects": ["*.css", "./src/polyfills.js"] }
```

```js
import { debounce } from 'lodash-es';   // ✅ só o debounce entra
import _ from 'lodash';                  // ❌ CommonJS, entra tudo (~70 KB)
```

Quando o tree shaking "não funciona", a causa quase sempre é uma dessas duas — não um bug do bundler.

---

## 4. Cache busting — o padrão de dois níveis

O problema fundamental do deploy de SPA: como fazer o usuário receber a versão nova sem que ele precise buscar tudo de novo toda vez?

```
dist/
├── index.html                    ← Cache-Control: no-cache      (nome fixo, sempre revalida)
└── assets/
    ├── app-a1b2c3d4.js           ← Cache-Control: immutable     (nome muda com o conteúdo)
    ├── vendor-e5f6g7h8.js        ← Cache-Control: immutable
    └── app-i9j0k1l2.css          ← Cache-Control: immutable
```

A lógica é elegante e vale entender: os assets têm o hash do conteúdo no nome, então **um arquivo com aquele nome nunca muda** — pode ser cacheado por um ano com segurança. O `index.html` tem nome fixo e por isso é sempre revalidado; é ele que aponta para os nomes novos. Uma revalidação barata (304, sem corpo) libera todo o resto.

```nginx
location /assets/ {
  add_header Cache-Control "public, max-age=31536000, immutable";
}
location = /index.html {
  add_header Cache-Control "no-cache";
}
location / {
  try_files $uri $uri/ /index.html;      # fallback de SPA (arquivo 05)
}
```

### O bug clássico: chunk faltando após deploy

Cenário real e frequente: um usuário está com a aba aberta há duas horas. Você faz deploy. Ele clica num link que dispara `import('./Admin-a1b2.js')` — mas o build novo gerou `Admin-x9y8.js` e o arquivo antigo foi removido. A importação falha e a aplicação quebra.

Três defesas, use as três:

**1. Não remova os assets antigos imediatamente.** Mantenha as últimas 2–3 versões no bucket. Custa centavos.

**2. Trate a falha de import:**

```js
async function importarComRecuperacao(fn) {
  try { return await fn(); }
  catch (e) {
    if (sessionStorage.getItem('recarregou-por-chunk')) throw e;   // evita laço infinito
    sessionStorage.setItem('recarregou-por-chunk', '1');
    location.reload();
  }
}
```

**3. Avise sobre a versão nova**, em vez de recarregar à força no meio do trabalho do usuário:

```js
// service worker detectou atualização
if (registration.waiting) {
  mostrarBanner('Nova versão disponível', { acao: () => {
    registration.waiting.postMessage({ type: 'SKIP_WAITING' });
    location.reload();
  }});
}
```

Recarregar sozinho enquanto alguém preenche um formulário é uma forma de perder dados do usuário — evite.

---

## 5. Onde hospedar

| Arquitetura | Onde | Observação |
|---|---|---|
| SPA pura (CSR) | S3+CloudFront, Cloudflare Pages, Netlify, Vercel, GitHub Pages | só arquivos estáticos; barato e simples |
| SSG | idem | idem |
| SSR/ISR/RSC | Vercel, Netlify, Cloudflare Workers, Fly.io, Node em contêiner | precisa de runtime |
| Edge SSR | Cloudflare Workers, Deno Deploy, Vercel Edge | roda perto do usuário; runtime limitado (sem APIs Node completas) |

**Edge vale a pena quando?** Ele corta latência de rede — útil para público globalmente distribuído. Não ajuda se sua consulta vai a um banco numa única região: você aproxima a computação do usuário e afasta do dado, e o resultado pode ser pior. Edge rende quando o dado também está distribuído (KV, D1, réplicas regionais) ou quando o trabalho é leve (autenticação, redirecionamento, testes A/B, personalização de casca).

---

## 6. Pipeline de CI/CD

```yaml
name: deploy
on: { push: { branches: [main] } }

jobs:
  verificar:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 22, cache: npm }
      - run: npm ci                             # lockfile exato, não npm install
      - run: npm run typecheck
      - run: npm run lint
      - run: npm test -- --coverage
      - run: npm run build
      - run: npx size-limit                     # orçamento de bundle (arquivo 09)
      - run: npx playwright test                # e2e nos fluxos críticos
      - run: npx lhci autorun                   # regressão de performance

  publicar:
    needs: verificar
    steps:
      - run: npm run build
      - run: aws s3 sync dist/assets s3://bucket/assets --cache-control "public,max-age=31536000,immutable"
      - run: aws s3 cp dist/index.html s3://bucket/index.html --cache-control "no-cache"
      - run: aws cloudfront create-invalidation --paths "/index.html" "/"
      - run: npx sentry-cli sourcemaps upload --release=$GITHUB_SHA dist/
```

**A ordem do `s3 sync` importa e é uma pegadinha real:** publique os **assets primeiro** e o `index.html` **por último**. Se inverter, existe uma janela em que o HTML novo aponta para arquivos que ainda não subiram — e todo usuário que carregar nesse intervalo recebe uma aplicação quebrada.

---

## 7. Estratégias de deploy

| Estratégia | Como | Quando |
|---|---|---|
| **Direto** | substitui e pronto | projetos pequenos, baixo risco |
| **Blue-green** | dois ambientes, troca o roteamento | rollback instantâneo |
| **Canário** | 5% do tráfego na versão nova, aumenta se as métricas seguirem boas | mudanças arriscadas |
| **Feature flags** | código já publicado, ligado por configuração | desacopla deploy de release |

**Feature flags** merecem destaque: elas permitem publicar código desligado e ativá-lo gradualmente, por usuário ou por percentual, com desligamento instantâneo sem novo deploy. É a técnica que mais reduz o risco de release. Custo: dívida de flags antigas — estabeleça um prazo de limpeza, senão o código vira um labirinto de condicionais mortas.

---

## 8. Variáveis de ambiente

```js
// Vite: apenas o prefixo VITE_ é exposto ao cliente
import.meta.env.VITE_API_URL       // vai para o bundle, é PÚBLICO
import.meta.env.MODE               // 'development' | 'production'
```

**Isto é substituição em tempo de build, não leitura em tempo de execução.** Consequência: a mesma imagem/artefato não serve para vários ambientes — você precisa de um build por ambiente, o que quebra o princípio de "construa uma vez, promova o artefato".

Se você precisa de um único artefato para dev/staging/prod, injete a configuração em **runtime**:

```html
<!-- index.html, preenchido pelo servidor ou por um script de entrada do contêiner -->
<script>window.__CONFIG__ = { apiUrl: "https://api.prod.exemplo.com" };</script>
```

E, repetindo o arquivo `11`: **nunca coloque segredo em variável exposta ao cliente.**

---

## 9. Observabilidade

Sem isso, você descobre os erros pelo suporte.

```js
import * as Sentry from '@sentry/react';

Sentry.init({
  dsn: '…',
  release: import.meta.env.VITE_COMMIT_SHA,      // liga o erro ao source map certo
  environment: import.meta.env.MODE,
  tracesSampleRate: 0.1,
  replaysOnErrorSampleRate: 1.0,                  // grava a sessão quando dá erro
  beforeSend(evento) {
    // remova PII antes de enviar
    delete evento.user?.email;
    return evento;
  },
});
```

Os quatro sinais que valem a pena coletar:

1. **Erros** — com source map, breadcrumbs, release e usuário afetado.
2. **Web Vitals de campo** — LCP, INP, CLS por rota (arquivo `09`).
3. **Falhas de API** — taxa de erro e latência por endpoint, vista do cliente. Frequentemente diverge do que o backend reporta, e a diferença é informação valiosa (rede, CORS, timeout de cliente).
4. **Eventos de negócio** — conversão, abandono. É o que conecta engenharia a resultado.

**Source maps:** gere com `sourcemap: 'hidden'`, envie ao Sentry no CI, e **não publique** no servidor web. Sem eles, o stack trace de produção é ilegível (`a.b.c is not a function` na linha 1, coluna 48219).

---

## 10. Service Worker e PWA

```js
// vite-plugin-pwa cobre a maior parte dos casos
VitePWA({
  registerType: 'prompt',            // avise; não recarregue sozinho
  workbox: {
    globPatterns: ['**/*.{js,css,html,woff2}'],
    runtimeCaching: [{
      urlPattern: /^https:\/\/api\./,
      handler: 'NetworkFirst',
      options: { cacheName: 'api', expiration: { maxAgeSeconds: 300 } },
    }],
  },
});
```

Avisos que valem por experiência:

- **Service Worker é difícil de desfazer.** Um SW com bug cacheia uma versão quebrada no dispositivo do usuário, e ele continua servindo mesmo depois de você corrigir o servidor. Tenha um caminho de "kill switch" (`registration.unregister()` + limpar caches) preparado **antes** de precisar dele.
- **Escopo importa.** Um SW em `/app/` não controla `/`.
- **Só funciona em HTTPS** (exceto `localhost`).
- Não faça cache-first do `index.html`: é assim que usuários ficam presos numa versão antiga para sempre.

---

## 11. Monorepo

```
apps/web · apps/admin · packages/ui · packages/api-client · packages/config
```

Ferramentas: **pnpm workspaces** (a instalação mais eficiente, por links), **Turborepo** ou **Nx** (cache de tarefas e execução afetada — só reconstrói o que mudou).

Vale quando: múltiplas aplicações compartilham código de verdade, e você quer mudanças atômicas atravessando pacotes. Não vale para uma aplicação só — é overhead de configuração sem retorno.

---

## 12. Checklist de deploy

- [ ] Assets com hash no nome, `immutable`; `index.html` com `no-cache`
- [ ] Assets publicados **antes** do `index.html`
- [ ] Fallback de SPA configurado (`try_files` / rewrites)
- [ ] Versões antigas de chunks mantidas por alguns deploys
- [ ] Falha de carregamento de chunk tratada, sem laço de reload
- [ ] Compressão Brotli ativa (inclusive nas respostas de API)
- [ ] Headers de segurança aplicados (arquivo `11`)
- [ ] Orçamento de bundle e Lighthouse no CI
- [ ] Source maps enviados ao monitoramento, não publicados
- [ ] Nenhum segredo no bundle (`grep` no `dist/`)
- [ ] Monitoramento de erro e de Web Vitals ativo com release marcada
- [ ] Rollback testado — não presumido
- [ ] Service Worker com estratégia de atualização e kill switch

---

## 13. Autoteste

1. Por que o dev server do Vite não fica mais lento conforme o projeto cresce?
2. Explique o padrão de cache de dois níveis e por que ele é seguro.
3. Por que publicar o `index.html` antes dos assets pode quebrar a aplicação?
4. Por que o tree shaking falha com `import _ from 'lodash'`?
5. Descreva o bug do chunk faltando e as três defesas.
6. Por que `VITE_API_URL` impede "construa uma vez, promova o artefato", e qual a alternativa?
7. Em que caso o edge SSR pode ser **mais lento** que uma região única?
8. Por que um Service Worker com bug é mais grave que um bug comum de deploy?

---

**Anterior:** [11 — Segurança](11-seguranca.md) · **Próximo:** [13 — Teoria avançada](13-teoria-avancada.md)
