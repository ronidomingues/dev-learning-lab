# 06 · Gerenciamento de estado

**Nível: intermediário** · Pré-requisitos: `04`.

Estado é o assunto onde mais tempo de engenharia é desperdiçado em SPAs — quase sempre por uma confusão categórica que este arquivo resolve na primeira seção.

---

## 1. A distinção que resolve 80% do problema

A pergunta "qual biblioteca de estado eu uso?" está mal formulada. A pergunta certa é **"que tipo de estado é este?"**, porque tipos diferentes exigem ferramentas diferentes.

| Tipo | Dono | Exemplos | Ferramenta certa |
|---|---|---|---|
| **De servidor** | o banco de dados | lista de produtos, perfil, pedidos | cache de consultas (TanStack Query, SWR, RSC) |
| **De URL** | a barra de endereços | filtros, página, aba, busca, id selecionado | o roteador / `URLSearchParams` |
| **Local de UI** | um componente | menu aberto, campo digitado, hover | `useState`, `signal` |
| **Global de cliente** | a aplicação | tema, idioma, carrinho offline, feature flags | store leve (Zustand, Jotai, Pinia, contexto) |
| **De formulário** | o formulário | valores, erros, "sujo", enviando | biblioteca de formulário |
| **De máquina** | um fluxo | wizard, checkout, upload | máquina de estados (XState) |

> **A causa raiz de quase todo "inferno de estado" que já vi é tratar estado de servidor como se fosse estado de cliente.**
>
> Você busca uma lista no `useEffect`, guarda num `useState`, sobe para um Redux global "porque outra tela precisa", e agora precisa manter manualmente sincronizado algo cuja fonte da verdade está em outra máquina. Você acabou de escrever um cache — mal, sem TTL, sem invalidação, sem dedupe, sem revalidação, sem tratamento de erro.
>
> Estado de servidor não é estado. É **cache de estado alheio**. Use uma ferramenta de cache.

Aplicando essa tabela, um aplicativo típico que "precisava de Redux" costuma ficar assim: 70% vira cache de consultas, 15% vai para a URL, 10% é `useState` local, e sobram 5% de estado global de verdade — que cabe em 20 linhas de store.

---

## 2. Estado local

O padrão de partida, e ele é o certo com muito mais frequência do que as pessoas acham.

```jsx
function Acordeao() {
  const [aberto, setAberto] = useState(false);
  return (
    <>
      <button aria-expanded={aberto} onClick={() => setAberto(a => !a)}>Detalhes</button>
      {aberto && <div>…</div>}
    </>
  );
}
```

Três regras que evitam a maior parte dos bugs de estado local:

**Regra 1 — não derive o que dá para calcular.**

```jsx
// ERRADO: dois estados que podem discordar
const [itens, setItens] = useState([]);
const [total, setTotal] = useState(0);        // vai dessincronizar. É questão de tempo.

// CERTO: uma fonte da verdade
const [itens, setItens] = useState([]);
const total = itens.reduce((s, i) => s + i.preco, 0);   // impossível divergir
```

Só memoize (`useMemo`) se medir e doer. Com o React Compiler estável no React 19, essa memoização é inferida automaticamente na maior parte dos casos.

**Regra 2 — modele estados impossíveis como impossíveis.**

```ts
// ERRADO: 2³ = 8 combinações, das quais 5 não fazem sentido
// (carregando E erro? dados E carregando?)
{ carregando: boolean; erro: Error | null; dados: T | null }

// CERTO: união discriminada — só existem 4 estados, todos válidos
type Estado<T> =
  | { status: 'ocioso' }
  | { status: 'carregando' }
  | { status: 'sucesso'; dados: T }
  | { status: 'erro'; erro: Error };
```

Isso não é preciosismo de tipagem. Cada estado impossível representável é um bug esperando a hora certa — a tela que mostra spinner e erro ao mesmo tempo, a que mostra dados velhos com mensagem de falha.

**Regra 3 — atualize com função quando depender do valor anterior.**

```jsx
setContador(c => c + 1);        // correto sob atualizações em lote
setContador(contador + 1);      // pode perder atualizações
```

---

## 3. Compartilhar estado: a escada

Quando dois componentes precisam do mesmo estado, suba na escada **um degrau por vez**. Pular degraus é a origem da complexidade acidental.

```
1. Elevar ao ancestral comum          ← resolve a maioria dos casos
2. Passar por props                   ← se a distância é curta
3. Composição / children              ← evita "prop drilling" sem contexto
4. Contexto                           ← estado raro que muda pouco (tema, usuário)
5. Store externa                      ← estado global que muda com frequência
6. Cache de consultas                 ← se for estado de SERVIDOR, pule para cá direto
```

### O degrau 3, que quase ninguém usa

Antes de recorrer a contexto por causa de *prop drilling*, tente composição:

```jsx
// ANTES: Pagina precisa passar `usuario` três níveis abaixo
<Pagina usuario={usuario} />

// DEPOIS: quem tem o dado renderiza quem precisa dele. Nada atravessa.
<Pagina barra={<Perfil usuario={usuario} />} />
```

Isso elimina a maior parte do prop drilling sem introduzir nenhuma abstração nova.

### O degrau 4 e sua armadilha

Contexto no React **não tem seletores**: qualquer mudança no valor do provedor re-renderiza **todos** os consumidores, mesmo os que só usam um campo que não mudou.

```jsx
// PROBLEMA: qualquer mudança em qualquer campo re-renderiza todo consumidor
<AppContext.Provider value={{ usuario, tema, carrinho, notificacoes }}>
```

Correções, em ordem de preferência:

1. **Divida em contextos por frequência de mudança.** `<TemaContext>` separado de `<CarrinhoContext>`.
2. **Separe valor de despachante.** O contexto de `dispatch` nunca muda, então quem só despacha nunca re-renderiza.
3. **Use uma store com seletores** (degrau 5). É para isso que elas existem.

E sempre estabilize o valor:

```jsx
const valor = useMemo(() => ({ usuario, entrar, sair }), [usuario]);
// sem isso, um objeto literal novo a cada render invalida todos os consumidores
```

---

## 4. Stores externas

### Zustand — o padrão de fato para estado global simples em React (2026)

```js
import { create } from 'zustand';

export const useCarrinho = create((set, get) => ({
  itens: [],
  adicionar: (produto) => set(s => {
    const existente = s.itens.find(i => i.id === produto.id);
    return existente
      ? { itens: s.itens.map(i => i.id === produto.id ? { ...i, qtd: i.qtd + 1 } : i) }
      : { itens: [...s.itens, { ...produto, qtd: 1 }] };
  }),
  remover: (id) => set(s => ({ itens: s.itens.filter(i => i.id !== id) })),
  total: () => get().itens.reduce((s, i) => s + i.preco * i.qtd, 0),
}));

// no componente — o SELETOR é o ponto: só re-renderiza se ESTE valor mudar
const total = useCarrinho(s => s.total());
const adicionar = useCarrinho(s => s.adicionar);
```

### Jotai — atômico

```js
const contadorAtom = atom(0);
const dobroAtom = atom(get => get(contadorAtom) * 2);   // derivado, recalcula sozinho
const [n, setN] = useAtom(contadorAtom);
```

Modelo bottom-up: você compõe átomos pequenos e as dependências são rastreadas automaticamente. Excelente quando o estado é naturalmente granular; pode virar sopa de átomos quando não é.

### Redux Toolkit — quando ainda faz sentido

Redux clássico foi a resposta certa para 2015, quando não havia cache de consultas e o contexto do React não existia. Hoje, **a maior parte do que motivava Redux é estado de servidor** e deve ir para a seção 5.

Redux Toolkit ainda se justifica quando você precisa de: histórico de ações auditável, undo/redo genérico, depuração por viagem no tempo, ou lógica de transição complexa e centralizada com muitos middlewares. Fora disso, é peso sem retorno.

### O `useSyncExternalStore`

O gancho que existe para conectar qualquer store externa ao React **sem rasgar** (*tearing* — dois componentes lendo valores diferentes da mesma fonte no mesmo render, algo possível com renderização concorrente). Toda store moderna o usa por baixo:

```js
const larguraJanela = useSyncExternalStore(
  (cb) => { addEventListener('resize', cb); return () => removeEventListener('resize', cb); },
  () => window.innerWidth,        // snapshot no cliente
  () => 1024                       // snapshot no servidor — obrigatório sob SSR
);
```

---

## 5. Estado de servidor — o cache de consultas

A categoria mais importante e a que mais gente implementa à mão sem perceber.

```jsx
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

function Produto({ id }) {
  const { data, isPending, error, isFetching } = useQuery({
    queryKey: ['produto', id],
    queryFn: ({ signal }) => fetch(`/api/produtos/${id}`, { signal }).then(r => r.json()),
    staleTime: 60_000,        // por 1 min, considera fresco e nem revalida
    gcTime: 5 * 60_000,       // após 5 min sem uso, descarta da memória
  });

  if (isPending) return <Esqueleto />;
  if (error) return <Erro erro={error} />;
  return <Detalhe produto={data} revalidando={isFetching} />;
}
```

O que você recebe de graça e teria que escrever:

- Cache por chave, com deduplicação de requisições simultâneas
- Revalidação no foco da janela, na reconexão e por intervalo
- *Stale-while-revalidate*: mostra o dado antigo instantaneamente **enquanto** busca o novo
- Cancelamento via `signal` quando o componente desmonta
- Retry com backoff exponencial
- Paginação e scroll infinito com dados anteriores preservados
- Atualização otimista com rollback automático

### Mutações e invalidação

```jsx
const qc = useQueryClient();

const { mutate } = useMutation({
  mutationFn: (dados) => fetch(`/api/produtos/${id}`, {
    method: 'PATCH', body: JSON.stringify(dados),
    headers: { 'Content-Type': 'application/json' },
  }).then(r => { if (!r.ok) throw new Error(`HTTP ${r.status}`); return r.json(); }),

  // atualização otimista
  onMutate: async (novo) => {
    await qc.cancelQueries({ queryKey: ['produto', id] });   // evita sobrescrita por resposta em voo
    const anterior = qc.getQueryData(['produto', id]);
    qc.setQueryData(['produto', id], old => ({ ...old, ...novo }));
    return { anterior };                                      // contexto para o rollback
  },
  onError: (_e, _v, ctx) => qc.setQueryData(['produto', id], ctx.anterior),   // desfaz
  onSettled: () => qc.invalidateQueries({ queryKey: ['produto', id] }),        // reconcilia com a verdade
});
```

O trio `onMutate` / `onError` / `onSettled` é o padrão canônico de atualização otimista: aplique já, desfaça se falhar, reconcilie sempre. Vale a pena decorá-lo.

### Desenho de chaves de cache

```js
['produtos']                                   // tudo de produtos
['produtos', 'lista', { filtros, pagina }]     // uma listagem específica
['produtos', 'detalhe', id]                    // um item
```

Chaves hierárquicas permitem invalidação por prefixo: `invalidateQueries({ queryKey: ['produtos'] })` derruba tudo relacionado. **Inclua na chave todo parâmetro que muda a resposta** — inclusive o id do usuário, se a resposta depender de quem pergunta. Cache vazado entre usuários é um incidente de segurança, não um bug de performance.

---

## 6. Estado de formulário

Formulário tem particularidades que justificam ferramenta própria: validação, campos tocados, "sujo", envio, erros do servidor, arrays dinâmicos.

```jsx
// React Hook Form + Zod — combinação padrão em 2026
const esquema = z.object({
  email: z.string().email('E-mail inválido'),
  senha: z.string().min(8, 'Mínimo 8 caracteres'),
});

const { register, handleSubmit, formState: { errors, isSubmitting } } =
  useForm({ resolver: zodResolver(esquema) });

<form onSubmit={handleSubmit(enviar)} noValidate>
  <label htmlFor="email">E-mail</label>
  <input id="email" {...register('email')}
         aria-invalid={!!errors.email}
         aria-describedby={errors.email ? 'err-email' : undefined} />
  {errors.email && <p id="err-email" role="alert">{errors.email.message}</p>}
  <button disabled={isSubmitting}>Entrar</button>
</form>
```

Dois pontos que separam formulário bom de ruim:

**Controlado vs. não controlado.** Componente controlado re-renderiza a cada tecla. Em formulários grandes isso é perceptível. React Hook Form usa campos **não controlados** com refs justamente por isso — o valor vive no DOM, e o React só é envolvido no envio e na validação.

**Validação no cliente é conveniência; no servidor é obrigação.** Sempre valide nos dois lados. Idealmente **com o mesmo esquema** compartilhado (é o principal argumento a favor do Zod em projetos TypeScript full-stack).

---

## 7. Máquinas de estado

Quando o fluxo tem transições que **não** podem acontecer em qualquer ordem — checkout, wizard, upload, conexão de mídia —, uma máquina de estados explícita elimina uma classe inteira de bugs.

```js
import { createMachine } from 'xstate';

const checkout = createMachine({
  initial: 'carrinho',
  states: {
    carrinho:   { on: { AVANCAR: 'endereco' } },
    endereco:   { on: { AVANCAR: 'pagamento', VOLTAR: 'carrinho' } },
    pagamento:  { on: { PAGAR: 'processando', VOLTAR: 'endereco' } },
    processando:{ on: { OK: 'concluido', FALHA: 'pagamento' } },   // não dá para "voltar" daqui
    concluido:  { type: 'final' },
  },
});
```

O ganho não é a biblioteca — é a **explicitação**. Um usuário não consegue clicar em "pagar" duas vezes, nem voltar durante o processamento, porque essas transições **não existem**. Com booleanos soltos (`estaProcessando`, `foiPago`, `temErro`), esses caminhos existem e alguém vai encontrá-los.

Use quando: mais de 4 estados que interagem, ou quando "clicar duas vezes rápido" quebra algo.

---

## 8. Persistência

```js
// localStorage — síncrono, ~5–10 MB, string apenas, BLOQUEIA a thread
localStorage.setItem('tema', 'escuro');

// sessionStorage — igual, mas morre ao fechar a aba

// IndexedDB — assíncrono, centenas de MB, objetos estruturados. Use idb-keyval por sanidade.
import { get, set } from 'idb-keyval';
await set('rascunho', { texto, atualizadoEm: Date.now() });

// Cache API — respostas HTTP, base do offline com service worker
const cache = await caches.open('v1');
await cache.put(requisicao, resposta);
```

Regras práticas:

- **Nunca guarde token de autenticação em `localStorage`.** Qualquer XSS o lê. Arquivo `11`.
- **`localStorage` é síncrono** — ler 2 MB de JSON no boot bloqueia a thread principal e atrasa o LCP. Já vi isso ser a causa raiz de "o app demora 800 ms para aparecer".
- **Versione o que você persiste.** Ao mudar a forma do dado, o usuário ainda tem a forma antiga guardada. Sem `{ versao: 3, dados }` e migração, você quebra a sessão de quem já usava.
- **Persista o mínimo.** Estado de servidor persistido vira dado velho servido com confiança.

---

## 9. Fronteiras de erro

Sem elas, um erro em qualquer componente derruba a árvore inteira: tela branca.

```jsx
import { ErrorBoundary } from 'react-error-boundary';

<ErrorBoundary
  FallbackComponent={({ error, resetErrorBoundary }) => (
    <div role="alert">
      <p>Algo deu errado nesta seção.</p>
      <button onClick={resetErrorBoundary}>Tentar de novo</button>
    </div>
  )}
  onError={(erro, info) => registrarNoSentry(erro, info)}
>
  <PainelDeGraficos />
</ErrorBoundary>
```

Onde colocar: **uma por região independente da tela**, não uma só na raiz. Se o widget de notificações quebrar, o resto da aplicação deve continuar funcionando.

Limitação importante: fronteiras de erro do React **não capturam** erros em manipuladores de evento, código assíncrono, `setTimeout` ou SSR. Para esses, você precisa de `try/catch` e dos listeners globais:

```js
addEventListener('error', reportar);
addEventListener('unhandledrejection', reportar);
```

---

## 10. Árvore de decisão

```
O dado vem do servidor e o servidor é o dono?
├── SIM → cache de consultas (TanStack Query / SWR / RSC). PARE.
└── NÃO
    └── O usuário deveria conseguir compartilhar/favoritar este estado?
        ├── SIM → URL (search params). PARE.
        └── NÃO
            └── Mais de um componente precisa?
                ├── NÃO → useState / signal local. PARE.
                └── SIM
                    └── Estão próximos na árvore?
                        ├── SIM → eleve ao ancestral comum, ou componha. PARE.
                        └── NÃO
                            └── Muda com frequência?
                                ├── NÃO (tema, usuário, locale) → contexto. PARE.
                                └── SIM → store com seletores (Zustand/Jotai). PARE.
```

Se você chegou ao último nó com muita coisa, releia a seção 1: provavelmente é estado de servidor disfarçado.

---

## 11. Armadilhas frequentes

| Armadilha | Sintoma | Correção |
|---|---|---|
| Estado de servidor em store global | sincronização manual, dado velho, código de cache caseiro | cache de consultas |
| Estado derivado guardado | dois valores que discordam | calcule na renderização |
| Contexto com objeto novo a cada render | re-render de tudo, app lento sem causa aparente | `useMemo` no valor; divida contextos |
| `useEffect` para sincronizar dois estados | laços de atualização, renders extras | derive, não sincronize |
| Booleanos em vez de união discriminada | spinner e erro juntos na tela | modele estados válidos |
| Tudo global "por precaução" | acoplamento total, nada é testável isolado | comece local, suba um degrau por vez |
| Mutar estado direto | UI não atualiza (React) ou atualiza demais | trate como imutável, ou use Immer |
| Persistir sem versionar | app quebra para usuários antigos após deploy | `{ versao, dados }` + migração |

---

## 12. Autoteste

1. Por que "estado de servidor não é estado"? Que consequência prática isso tem?
2. Quais três coisas devem ir para a URL num painel com filtros e paginação?
3. Por que o contexto do React re-renderiza consumidores que não usam o campo alterado, e quais as duas correções?
4. Escreva a união discriminada de um estado de requisição e diga quantos estados impossíveis ela elimina em relação a três booleanos.
5. No padrão de atualização otimista, para que serve o `onMutate` retornar `{ anterior }`?
6. Por que `localStorage` pode atrasar o LCP?
7. Quando uma máquina de estados vale o custo?

---

**Anterior:** [05 — Roteamento](05-roteamento.md) · **Próximo:** [07 — Estratégias de renderização](07-renderizacao.md)
