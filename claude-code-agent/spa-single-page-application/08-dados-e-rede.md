# 08 · Dados e rede

**Nível: intermediário → avançado** · Pré-requisitos: `02`, `06`.

Numa SPA, a rede é o gargalo dominante e o principal responsável pela sensação de lentidão. Este arquivo cobre como falar com o servidor, como não falar quando não precisa, e como não corromper a tela no caminho.

---

## 1. `fetch`, com tudo que ele precisa ter

O `fetch` ingênuo omite quatro coisas que sempre importam:

```js
async function api(caminho, { sinal, ...opcoes } = {}) {
  const r = await fetch(`/api${caminho}`, {
    ...opcoes,
    signal: sinal,                                     // 1. cancelamento
    headers: { 'Content-Type': 'application/json', ...opcoes.headers },
    credentials: 'include',                            // 2. envia cookies (se for esse o modelo)
  });

  if (!r.ok) {                                         // 3. fetch NÃO rejeita em 4xx/5xx
    const corpo = await r.json().catch(() => ({}));
    throw new ErroApi(r.status, corpo.mensagem ?? r.statusText, corpo);
  }

  if (r.status === 204) return null;                   // 4. sem corpo para parsear
  return r.json();
}

class ErroApi extends Error {
  constructor(status, mensagem, corpo) {
    super(mensagem);
    this.name = 'ErroApi';
    this.status = status;
    this.corpo = corpo;
  }
}
```

> **A pegadinha número um do `fetch`:** ele só rejeita a promessa em **falha de rede**. Um 500 é uma resposta bem-sucedida do ponto de vista dele. Quem esquece o `if (!r.ok)` acaba com `undefined` circulando pela aplicação e um erro dez camadas adiante, longe da causa.

Timeout — o `fetch` não tem um por padrão, e uma requisição pode ficar pendurada indefinidamente:

```js
const r = await fetch(url, { signal: AbortSignal.timeout(10_000) });

// combinando timeout com cancelamento por desmontagem:
const sinal = AbortSignal.any([AbortSignal.timeout(10_000), sinalDoComponente]);
```

`AbortSignal.timeout` e `AbortSignal.any` têm suporte amplo desde 2023–2024.

---

## 2. Modelos de API

### REST

O modelo dominante. Sua principal virtude não é elegância teórica — é **cacheabilidade**: `GET` com URL estável é cacheável pelo navegador, por proxies e por CDNs, de graça.

```
GET    /api/produtos?categoria=roupas&pagina=2
GET    /api/produtos/42
POST   /api/produtos
PATCH  /api/produtos/42
DELETE /api/produtos/42
```

Suas duas dores clássicas:

- **Over-fetching** — o endpoint devolve 40 campos e você usa 3.
- **Under-fetching / N+1** — você busca uma lista de pedidos e depois um `GET /usuarios/:id` para cada um. Trinta requisições para uma tela.

### GraphQL

Uma consulta, exatamente os campos necessários, atravessando relações:

```graphql
query {
  pedidos(primeiros: 20) {
    id total
    usuario { nome email }        # sem N+1: vem junto
    itens { produto { nome preco } quantidade }
  }
}
```

Resolve over e under-fetching. Custos reais: cache HTTP praticamente inutilizável (tudo é `POST /graphql`), então você precisa de cache normalizado no cliente (Apollo, urql, Relay); complexidade de servidor; e o risco de consultas maliciosamente profundas, exigindo análise de custo e limite de profundidade.

Em 2026 o GraphQL estabilizou num nicho claro: **vale quando há muitos clientes heterogêneos consumindo o mesmo backend** (web + iOS + Android + parceiros). Para um único frontend, o custo raramente se paga — e esta é uma correção coletiva em relação ao entusiasmo de 2018.

### tRPC

Para times TypeScript full-stack em monorepo: chamadas de procedimento com tipagem inferida ponta a ponta, sem geração de código nem esquema.

```ts
const produto = await trpc.produto.porId.query({ id: 42 });   // tipo inferido do servidor
```

Ótima ergonomia. Restrição: exige TypeScript nos dois lados e o mesmo repositório. Não serve para API pública.

### Server Actions

Se você usa RSC, boa parte da camada de API desaparece (arquivo `07`).

---

## 3. As cascatas — o inimigo principal

Cascata (*waterfall*) é toda sequência de requisições onde a próxima só pode começar depois que a anterior termina. É a diferença entre 300 ms e 1,8 s numa mesma tela.

### Cascata 1 — busca dentro de componente filho

```jsx
// PÉSSIMO: o filho só existe depois do pai, então só busca depois
function Perfil({ id }) {
  const { data: usuario } = useQuery(['u', id], () => api(`/usuarios/${id}`));
  if (!usuario) return <Spinner />;
  return <Pedidos usuarioId={usuario.id} />;     // e SÓ ENTÃO começa a segunda busca
}
```

```jsx
// BOM: as duas partem juntas
function Perfil({ id }) {
  const [usuario, pedidos] = useQueries({ queries: [
    { queryKey: ['u', id],  queryFn: () => api(`/usuarios/${id}`) },
    { queryKey: ['p', id],  queryFn: () => api(`/usuarios/${id}/pedidos`) },
  ]});
}
```

### Cascata 2 — código antes dos dados

Resolvida pelos loaders de rota (arquivo `05`, seção 4): o roteador dispara `import()` e `loader()` em paralelo.

### Cascata 3 — autenticação antes de tudo

```
GET /me → 200 → só então GET /dados
```

Correção: emita o estado de sessão no HTML inicial (SSR), ou use um cookie que o servidor já resolve, ou dispare as duas e trate o 401.

### Como enxergar cascatas

Aba **Network** do DevTools, com throttling ativado. Barras que começam escalonadas em diagonal = cascata. Barras que começam alinhadas = paralelo. É um diagnóstico de cinco segundos que quase ninguém faz.

---

## 4. Cache HTTP — a camada de graça

Antes de qualquer cache em JavaScript, use o que o protocolo já oferece.

```http
Cache-Control: public, max-age=31536000, immutable      # assets com hash no nome
Cache-Control: private, no-cache                        # HTML: sempre revalida
Cache-Control: private, max-age=0, must-revalidate      # dados de usuário
Cache-Control: public, max-age=60, stale-while-revalidate=300
ETag: "a1b2c3"
```

O padrão de dois níveis que todo deploy correto usa (arquivo `12`):

| Recurso | Política | Motivo |
|---|---|---|
| `/assets/app-a1b2c3.js` | `max-age=31536000, immutable` | o nome muda quando o conteúdo muda |
| `/index.html` | `no-cache` | precisa apontar para os assets novos |
| `/api/*` | curto + `ETag` | dado muda |

**Revalidação condicional** — barata, devolve 304 sem corpo:

```http
GET /api/produtos/42
If-None-Match: "a1b2c3"
→ 304 Not Modified                # zero bytes de corpo
```

**`stale-while-revalidate`** é a diretiva mais subutilizada do HTTP: serve o cache imediatamente **e** revalida em background. O usuário nunca espera; o dado se atualiza sozinho. Vale para assets, para respostas de API e para páginas em CDN.

---

## 5. Cache no cliente — camadas e política

```
1. Cache HTTP do navegador     ← de graça, respeita os headers
2. Cache de consultas (memória) ← TanStack Query/SWR: dedupe, SWR, invalidação
3. Cache normalizado            ← Apollo/Relay: entidades por id, coerência global
4. Cache persistente            ← IndexedDB/Cache API: sobrevive a recarregamento, base do offline
```

### Normalizado ou por documento?

**Por documento** (TanStack Query): a resposta é guardada inteira, sob a chave da consulta. Simples, previsível. Problema: o mesmo produto aparece em `['lista']` e em `['produto', 42]`; atualizar um não atualiza o outro.

**Normalizado** (Apollo, Relay): as respostas são desmontadas em entidades por `__typename:id`, e todas as consultas leem do mesmo grafo. Atualizar o produto 42 atualiza todas as telas de uma vez. Custo: complexidade real, e você precisa ensinar o cache a lidar com listas, paginação e mutações que criam ou removem itens.

Recomendação prática: **comece por documento e invalide por prefixo**. Só vá para normalizado quando a incoerência entre telas virar um problema recorrente e mensurável — o que acontece, mas menos do que se imagina.

### Stale-while-revalidate no cliente

```
Estado do dado:  FRESCO ──(staleTime)──► VELHO ──(gcTime)──► COLETADO
                 usa direto            usa E revalida       busca de novo
```

Ajuste `staleTime` pela natureza do dado: catálogo de produtos, minutos; saldo bancário, zero. O padrão `staleTime: 0` de muitas bibliotecas é conservador — revalida em toda montagem. Para dados que mudam devagar, aumentá-lo é a otimização de rede mais barata que existe.

---

## 6. Atualizações otimistas

Aplicar a mudança na tela **antes** da confirmação do servidor. A diferença entre uma interface que parece instantânea e uma que parece lenta.

O padrão canônico está no arquivo `06`, seção 5. O que importa entender é a disciplina em torno dele:

**Use quando:** a operação quase sempre dá certo (curtir, marcar como lido, arrastar um cartão, editar um campo), e desfazer é visualmente inofensivo.

**Não use quando:** a falha tem consequência séria ou o resultado é imprevisível — pagamento, transferência, exclusão definitiva, qualquer coisa com efeito colateral externo. Mostrar "pago" e reverter é pior do que esperar 800 ms.

**Sempre:** cancele consultas em voo antes de escrever no cache (`cancelQueries`), guarde o valor anterior para o rollback, e reconcilie com o servidor no `onSettled`. E comunique a falha claramente — reverter em silêncio faz o usuário achar que o clique não registrou.

---

## 7. Paginação

| Técnica | Como | Vantagem | Problema |
|---|---|---|---|
| **Offset** | `?limite=20&offset=40` | trivial, permite pular para a página N | lento em tabelas grandes; **itens duplicados ou pulados** se algo for inserido entre requisições |
| **Cursor** | `?limite=20&depois=cursor_abc` | estável sob inserções, rápido no banco | não dá para pular para a página 7 |

Para scroll infinito e feeds, **use cursor**. Offset em feed produz o bug clássico de itens repetidos, que aparece exatamente quando o conteúdo é ativo — e é difícil de reproduzir em desenvolvimento.

```jsx
const { data, fetchNextPage, hasNextPage, isFetchingNextPage } = useInfiniteQuery({
  queryKey: ['feed'],
  queryFn: ({ pageParam, signal }) =>
    api(`/feed?limite=20${pageParam ? `&depois=${pageParam}` : ''}`, { sinal: signal }),
  initialPageParam: null,
  getNextPageParam: (ultima) => ultima.proximoCursor ?? undefined,
});
```

Acompanhe scroll infinito de **virtualização** (renderizar só o que está visível — TanStack Virtual) quando a lista passa de algumas centenas de itens. Sem isso, o DOM cresce sem limite e a página trava progressivamente.

E ofereça sempre um botão "carregar mais" além do gatilho automático: scroll infinito puro é inacessível por teclado e torna o rodapé inalcançável.

---

## 8. Tempo real

| Tecnologia | Direção | Quando usar |
|---|---|---|
| **Polling** | cliente pergunta | simples, tolerante a atraso; comece por aqui |
| **SSE** | servidor → cliente | notificações, feeds, streaming de LLM. Reconecta sozinho, é HTTP puro |
| **WebSocket** | bidirecional | chat, colaboração, jogos. Precisa de heartbeat e reconexão manuais |
| **WebRTC** | par a par | áudio/vídeo/dados com latência mínima |
| **WebTransport** | bidirecional sobre HTTP/3 | sucessor do WebSocket; adoção crescente em 2026 |

**SSE é subestimado.** Para o caso comum — o servidor empurra atualizações e o cliente não precisa responder pelo mesmo canal — ele é HTTP normal, atravessa proxies sem drama, reconecta automaticamente com `Last-Event-ID`, e não exige infraestrutura especial:

```js
const es = new EventSource('/api/eventos');
es.addEventListener('pedido:atualizado', (e) => {
  qc.setQueryData(['pedido', JSON.parse(e.data).id], JSON.parse(e.data));
});
```

WebSocket, se você usar, precisa de: reconexão com backoff exponencial e *jitter*, heartbeat para detectar conexões zumbis (comuns atrás de proxies corporativos), fila de mensagens enquanto desconectado, e ressincronização de estado ao reconectar — porque você perdeu eventos. Nenhuma dessas quatro coisas vem de graça e todas são necessárias em produção.

---

## 9. Offline e sincronização

```js
// Service Worker — cache-first para assets, network-first para dados
self.addEventListener('fetch', (e) => {
  const url = new URL(e.request.url);
  if (url.pathname.startsWith('/assets/')) {
    e.respondWith(caches.match(e.request).then(r => r ?? fetch(e.request)));
  } else if (url.pathname.startsWith('/api/')) {
    e.respondWith(
      fetch(e.request)
        .then(r => { const c = r.clone(); caches.open('api').then(x => x.put(e.request, c)); return r; })
        .catch(() => caches.match(e.request))       // offline: serve o último conhecido
    );
  }
});
```

Escrita offline é onde mora a dificuldade real. Fila de mutações em IndexedDB, reenvio ao voltar a conexão (`Background Sync`), e — o problema difícil — **resolução de conflito** quando dois dispositivos editaram o mesmo dado. As opções:

- **Last-write-wins** — simples, perde dados silenciosamente. Aceitável para preferências.
- **Bloqueio otimista** com versão/ETag — detecta o conflito e devolve 409 para o usuário resolver. É o padrão sensato para a maioria dos casos.
- **CRDTs** (Yjs, Automerge) — convergem automaticamente sem servidor autoritativo. É o que sustenta edição colaborativa em tempo real. Poderoso e complexo; use uma biblioteca madura, jamais implemente do zero.

---

## 10. O transporte

**HTTP/2 e HTTP/3** multiplexam várias requisições numa conexão, o que eliminou a necessidade de concatenar arquivos por causa do limite de 6 conexões do HTTP/1.1. Isso não significa que requisições são grátis — cada uma ainda tem latência, e uma cascata de 30 chamadas continua sendo 30 idas e voltas.

**Compressão:** Brotli para assets estáticos (~15–20% melhor que gzip). Zstandard vem ganhando suporte e é mais rápido de descomprimir. Verifique que sua CDN comprime também as respostas de API em JSON — é comum estar desligado.

**Priorização:** use `fetchpriority="high"` na imagem do LCP e `preconnect` para origens de terceiros que você sabe que vai usar:

```html
<link rel="preconnect" href="https://api.exemplo.com" crossorigin>
<img src="/heroi.webp" fetchpriority="high" width="1200" height="600" alt="…">
```

---

## 11. Padrões de erro

Distinga os tipos, porque a resposta correta é diferente para cada um:

```js
function classificar(erro) {
  if (erro.name === 'AbortError')   return 'cancelado';     // não é erro: ignore
  if (erro.name === 'TimeoutError') return 'timeout';       // retry
  if (!navigator.onLine)            return 'offline';       // avise e enfileire
  if (erro instanceof TypeError)    return 'rede';          // retry com backoff
  if (erro.status === 401)          return 'sessao';        // renove ou redirecione
  if (erro.status === 403)          return 'permissao';     // não adianta tentar de novo
  if (erro.status === 404)          return 'inexistente';   // idem
  if (erro.status === 409)          return 'conflito';      // peça resolução ao usuário
  if (erro.status === 422)          return 'validacao';     // mostre nos campos
  if (erro.status === 429)          return 'limite';        // respeite Retry-After
  if (erro.status >= 500)           return 'servidor';      // retry com backoff
  return 'desconhecido';
}
```

**Retry só para o que é transitório** (rede, timeout, 5xx, 429). Repetir um 403 é desperdício garantido. E retry **apenas em requisições idempotentes** — repetir um `POST /pagamentos` pode cobrar duas vezes. Para `POST` não idempotente, use uma **chave de idempotência**:

```js
fetch('/api/pagamentos', {
  method: 'POST',
  headers: { 'Idempotency-Key': idDaTentativa },   // o servidor deduplica
  body: JSON.stringify(dados),
});
```

Backoff exponencial com jitter, para não sincronizar todos os clientes num pico:

```js
const espera = Math.min(30_000, 2 ** tentativa * 1000) * (0.5 + Math.random() * 0.5);
```

---

## 12. Checklist

- [ ] `if (!r.ok)` em todo `fetch` — ou uma camada que já o faça
- [ ] `AbortSignal` em toda requisição ligada a um componente ou rota
- [ ] Timeout explícito
- [ ] Nenhuma cascata evitável (verificado na aba Network com throttling)
- [ ] `Cache-Control` correto: assets imutáveis com hash, HTML `no-cache`
- [ ] `staleTime` ajustado por tipo de dado, não deixado no padrão
- [ ] Chaves de cache incluem **tudo** que muda a resposta, inclusive o usuário
- [ ] Otimismo apenas onde a falha é inofensiva, com rollback e aviso
- [ ] Paginação por cursor em feeds; virtualização em listas longas
- [ ] Retry só em erros transitórios e requisições idempotentes; backoff com jitter
- [ ] Chave de idempotência em `POST` com efeito financeiro ou externo
- [ ] Reconexão, heartbeat e ressincronização, se usar WebSocket
- [ ] Estratégia explícita de conflito, se houver escrita offline

---

## 13. Autoteste

1. Por que `fetch` não rejeita em erro 500, e qual bug isso causa?
2. Explique as três cascatas da seção 3 e a correção de cada uma.
3. Em que situação `stale-while-revalidate` faz o usuário nunca esperar?
4. Quando cache normalizado se paga, e qual o custo?
5. Por que offset produz itens duplicados num feed e cursor não?
6. Quando SSE é preferível a WebSocket?
7. Por que retry em `POST` pode ser perigoso, e como tornar seguro?
8. Cite dois casos onde atualização otimista é a escolha errada.

---

**Anterior:** [07 — Renderização](07-renderizacao.md) · **Próximo:** [09 — Performance](09-performance.md)
