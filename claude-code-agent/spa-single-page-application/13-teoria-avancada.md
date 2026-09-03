# 13 · Teoria avançada

**Nível: pesquisa** · Pré-requisitos: `04`, `06`, `07`. Árvores, grafos, complexidade assintótica.

Aqui descemos ao nível dos algoritmos. O objetivo é que você consiga **ler o código-fonte de um framework** e entender as decisões, em vez de aceitá-las.

---

## 1. O problema formal

Toda biblioteca de interface resolve a mesma coisa:

> Dado um estado `S` e uma função de renderização `f: S → Árvore`, manter o DOM sincronizado com `f(S)` conforme `S` muda ao longo do tempo, minimizando o trabalho.

O trabalho decompõe-se em duas partes:

```
custo total = custo de DESCOBRIR o que mudou + custo de APLICAR a mudança
```

O custo de aplicar tem um piso: se `k` nós precisam mudar, você paga `Ω(k)` operações de DOM. **Toda a competição entre frameworks é sobre o primeiro termo** — quão caro é descobrir o que mudou.

Três respostas, e é útil vê-las como pontos de um mesmo espectro:

| Estratégia | Custo de descoberta | Preço pago |
|---|---|---|
| **Virtual DOM** (React) | `O(n)` — compara a árvore | trabalho proporcional ao tamanho da árvore, não da mudança |
| **Reatividade fina** (Solid, Svelte, Vue) | `O(k)` — o grafo já sabe | overhead de manter o grafo de dependências |
| **Compilação** (Svelte, React Compiler) | `O(k)`, decidido no build | perda de dinamismo; análise estática limitada |

O ótimo teórico é `O(k)`. O React aceita `O(n)` deliberadamente, e a próxima seção explica por que essa escolha não foi irracional.

---

## 2. O algoritmo de reconciliação do React

### O problema de base

Comparar duas árvores ordenadas e produzir a menor sequência de edições é um problema clássico: o **tree edit distance**. Os melhores algoritmos exatos custam **O(n³)** — inviável para milhares de nós a cada quadro.

O React escapa disso com **duas heurísticas** que reduzem o custo a `O(n)`:

**Heurística 1 — tipos diferentes produzem árvores diferentes.**

```jsx
<div><Contador /></div>   →   <span><Contador /></span>
```

O React **não** tenta mover o `<Contador>`. Ele destrói a subárvore inteira e recria. O `<Contador>` perde todo o seu estado, mesmo sendo "o mesmo componente". É uma aproximação: gera trabalho extra em casos raros, e economiza a comparação cruzada de todos os filhos com todos os filhos.

**Heurística 2 — o desenvolvedor fornece identidade estável via `key`.**

Sem `key`, filhos são comparados **por posição**:

```jsx
// antes:  [A, B, C]      depois: [Z, A, B, C]      (inserção no início)
// por posição: A↔Z, B↔A, C↔B, +C  →  QUATRO operações, três delas destrutivas
```

Cada "comparação" que falha significa desmontar e remontar: o estado interno se perde, `<input>` perde o texto digitado, o foco se perde, animações reiniciam.

Com `key`, o React monta um mapa `chave → nó` e reconhece que A, B e C são os mesmos:

```jsx
// [A,B,C] → [Z,A,B,C] com keys: UMA inserção. Nada mais é tocado.
```

> **Por isso `key={index}` é um bug esperando acontecer.** Com índice, inserir no começo faz todas as chaves mudarem de dono — é exatamente equivalente a não ter chave. `key={index}` só é correto quando a lista **nunca** é reordenada, filtrada ou tem itens inseridos/removidos no meio. Se ela é estática, use índice à vontade; se não é, use um id estável do dado.

### O custo real

O React re-executa a função do componente inteiro e reconstrói sua subárvore virtual a cada render. É `O(n)` no tamanho da subárvore, mesmo que apenas um texto tenha mudado. A defesa é a **constante baixa**: criar objetos JS simples é ordens de grandeza mais barato que tocar o DOM. E a poda por memoização (`React.memo`, e agora o React Compiler) corta subárvores inteiras da comparação.

---

## 3. Fiber — renderização interrompível

O React 15 reconciliava com **recursão síncrona**. Uma árvore grande significava uma tarefa longa e a página congelada (arquivo `02`, seção 6). A pilha de chamadas do JavaScript não é pausável.

O **Fiber** (React 16, 2017) reimplementa a árvore como uma **lista ligada percorrida iterativamente**, com o estado do percurso em estruturas próprias — uma pilha reificada, que pode ser guardada e retomada.

```js
// cada nó é um "fiber"
{ tipo, props, estado,
  filho, irmao, retorno,     // a árvore como lista ligada: dá para retomar de qualquer ponto
  flagsDeEfeito,
  alternate }                // a versão do render anterior (double buffering)
```

Duas fases:

```
FASE DE RENDER (interrompível, sem efeitos visíveis)
  percorre os fibers, calcula o que mudou, monta a lista de efeitos
  pode PARAR, ceder ao navegador e RETOMAR depois
  pode ser DESCARTADA se chegar algo mais urgente

FASE DE COMMIT (síncrona, atômica, não interrompível)
  aplica tudo ao DOM de uma vez
```

A separação é o que garante que o usuário **nunca** veja uma árvore meio atualizada. E é o que permite prioridades: uma digitação (urgente) interrompe a renderização de uma lista de resultados (transição), que é descartada e recomeçada com o valor novo.

```jsx
setBusca(v);                                 // urgente: sincrono
startTransition(() => setResultados(v));     // interrompível, descartável
```

**Double buffering** (`alternate`): existem duas árvores, a atual e a em construção. O React trabalha na segunda e troca os ponteiros no commit. É a mesma técnica de renderização gráfica, pela mesma razão — evitar exibir estado parcial.

**Custo do modelo:** o componente pode ser executado várias vezes para um único commit. É daí que vem a exigência de **funções de render puras**, e o `StrictMode` renderizar duas vezes em desenvolvimento existe para expor código que viola isso.

---

## 4. Reatividade fina — a alternativa

O modelo do Solid, do Svelte 5, do Vue e dos signals do Angular. A implementação mínima está no arquivo `04`, seção 6; aqui vamos ao que a versão de produção acrescenta.

### O grafo de dependências

```
      [sinal a]        [sinal b]
          │  ╲            │
          │   ╲           │
      [derivado c]   [derivado d]
              ╲        ╱
              [efeito e]  ─→ escreve num nó específico do DOM
```

Quando `a` muda, o sistema conhece **exatamente** o conjunto alcançável e só recomputa esse conjunto. `O(k)`, onde `k` é o número de dependentes reais.

### Os três problemas que uma implementação séria precisa resolver

**Problema 1 — o diamante (glitch).**

`a` alimenta `c` e `d`; ambos alimentam `e`. Se você propagar em profundidade ingenuamente, `e` roda duas vezes, e uma delas com `c` novo e `d` velho — um estado **inconsistente que nunca deveria existir**. Isso se chama *glitch*.

A solução é propagar em **ordem topológica**: atribua a cada nó uma altura no grafo, e processe por altura crescente. `e` só roda depois que `c` e `d` estabilizaram, e roda uma vez só.

**Problema 2 — propagação preguiçosa.**

Recomputar tudo imediatamente desperdiça trabalho para derivados que ninguém está lendo. A solução usada por Solid e Vue é **marcação em dois passos**: a mudança propaga apenas uma marca de "sujo" pelo grafo (barato), e o valor só é recomputado quando alguém efetivamente o lê. Se nada leu, nada foi computado.

**Problema 3 — vazamento de assinaturas.**

Dependências são **dinâmicas**: `() => cond.valor ? a.valor : b.valor` depende de `b` numa execução e não na outra. Se você não **limpar as assinaturas antigas antes de cada re-execução**, o efeito continua sendo notificado por `b` para sempre. Toda implementação correta descarta o conjunto de dependências e o reconstrói a cada execução.

```js
function efeito(fn) {
  const executar = () => {
    limparDependencias(executar);      // ESSENCIAL: senão vaza e notifica demais
    assinanteAtual = executar;
    try { fn(); } finally { assinanteAtual = null; }
  };
  executar();
}
```

### A consequência de design: componentes rodam uma vez

No Solid, um componente executa **uma única vez** na vida. Ele cria os efeitos que ligam sinais a nós do DOM, e nunca mais é chamado. Não há "re-render de componente" — só efeitos que atualizam nós específicos.

```jsx
// Solid — isto roda UMA vez. O texto atualiza pelo efeito, não por re-execução.
function Contador() {
  const [n, setN] = createSignal(0);
  console.log('roda uma vez');
  return <button onClick={() => setN(n() + 1)}>{n()}</button>;
}
```

```jsx
// React — isto roda a cada mudança de estado
function Contador() {
  const [n, setN] = useState(0);
  console.log('roda toda vez');
  return <button onClick={() => setN(n + 1)}>{n}</button>;
}
```

É por isso que `n` é uma **função** no Solid (`n()`): a leitura precisa acontecer dentro do escopo de rastreamento, no momento certo. Não é capricho de sintaxe — é o mecanismo.

### O trade-off honesto

| | Virtual DOM | Reatividade fina |
|---|---|---|
| Descoberta | `O(n)` | `O(k)` |
| Memória | árvore virtual temporária | grafo permanente de dependências |
| Modelo mental | simples: re-execute e compare | mais sutil: onde o rastreamento acontece |
| Armadilhas | re-render desnecessário | perda de reatividade ao desestruturar |
| Interrompível | sim (Fiber) | difícil — as atualizações são síncronas e diretas |

A "perda de reatividade ao desestruturar" é a armadilha característica do modelo:

```js
const { nome } = props;    // ❌ leu AGORA, congelou o valor, quebrou o rastreamento
props.nome                 // ✅ lê no momento do uso, dentro do escopo rastreado
```

Todo framework de reatividade fina tem essa pegadinha, e ela é a principal fonte de bugs para quem vem do React.

---

## 5. Compiladores

A terceira via: decidir em **tempo de build** o que os outros decidem em tempo de execução.

### Svelte

```svelte
<script> let n = $state(0); </script>
<button on:click={() => n++}>{n}</button>
```

O compilador emite JavaScript imperativo direto:

```js
// aproximação do que sai
let n = 0;
const btn = document.createElement('button');
const txt = document.createTextNode(n);
btn.addEventListener('click', () => { n++; txt.data = n; });   // atualização cirúrgica
```

Não há runtime de framework para baixar, não há árvore virtual, não há grafo em memória. O código **é** a atualização. O runtime do Svelte é uma fração do de React ou Vue.

**Limite fundamental:** o compilador só pode otimizar o que consegue provar estaticamente. Componentes muito dinâmicos, `<svelte:component>` e composição em tempo de execução caem em caminhos genéricos e perdem parte do ganho. É um caso particular do limite geral da análise estática.

### React Compiler

Estável no React 19. Faz análise de fluxo de dados para inserir memoização automaticamente:

```jsx
// você escreve:
function Lista({ itens, filtro }) {
  const visiveis = itens.filter(i => i.tipo === filtro);
  return visiveis.map(i => <Item key={i.id} dado={i} />);
}
// o compilador insere o equivalente a useMemo em `visiveis` e memoiza os elementos
```

É uma mudança de filosofia relevante: o React sempre exigiu que o desenvolvedor otimizasse manualmente (`useMemo`, `useCallback`, `React.memo`), e agora infere. Isso remove uma das críticas mais consistentes ao modelo — e uma das principais fontes de código ruidoso.

O compilador é **conservador**: quando não consegue provar que uma expressão é pura, ele não memoiza. Código que viola as Regras dos Hooks ou muta props simplesmente não é otimizado (e o ESLint avisa).

---

## 6. Complexidade das operações de lista

Reordenar uma lista com chaves é, formalmente, encontrar a **menor sequência de movimentos** para transformar uma permutação em outra. O ótimo se reduz a encontrar a **maior subsequência crescente** (LIS) dos índices — os itens da LIS ficam parados, os demais se movem.

- LIS ótimo: `O(n log n)` com busca binária.
- Vue 3 usa exatamente isso no seu `patchKeyedChildren`.
- React usa uma heurística mais simples, `O(n)`, que não é ótima em movimentos mas evita o custo do LIS.

Na prática, o gargalo raramente é o algoritmo de diff — é o número de operações de DOM e o layout que elas disparam. Por isso **virtualização** (renderizar só o visível) vence qualquer otimização de diff em listas grandes: ela ataca o `k`, não o custo de descobrir o `k`.

```
lista de 10.000 itens:
  diff otimizado sobre 10.000 nós  → milissegundos de JS + layout de 10.000 nós
  virtualização com 20 nós          → microssegundos + layout de 20 nós
```

---

## 7. Limites teóricos

**Limite 1 — o custo do DOM é irredutível.** Se `k` nós mudam, você paga `Ω(k)` em operações de DOM, mais o layout que elas causam. Nenhum framework escapa disso. Só se escapa **não mudando** os nós (virtualização, `content-visibility`, memoização).

**Limite 2 — a análise estática é limitada.** Compiladores não podem provar propriedades arbitrárias de programas (é o Problema da Parada em roupa nova). Toda otimização de compilador é conservadora: na dúvida, não otimiza. Sempre haverá casos em que o desenvolvedor sabe algo que o compilador não consegue provar.

**Limite 3 — a thread única é uma barreira estrutural.** Não dá para paralelizar o DOM: as APIs são inerentemente sequenciais e o layout é global. Workers ajudam com computação, não com renderização. Isso não tem solução dentro do modelo atual da plataforma.

**Limite 4 — a latência de rede tem piso físico.** A velocidade da luz impõe ~30 ms para a volta São Paulo–Virgínia. Nenhum framework contorna isso; só arquitetura (edge, cache, otimismo, pré-busca) o esconde.

---

## 8. Um resultado interessante sobre hidratação

Vale formalizar por que a hidratação é tão cara:

```
Sem SSR:   custo = render_cliente(n)
Com SSR:   custo = render_servidor(n) + transferência(html) + hidratação(n)
```

E `hidratação(n) ≈ render_cliente(n)` — ela reexecuta os componentes para reconstruir a árvore em memória e anexar handlers. **O SSR não reduz o trabalho total do cliente; ele o reordena**, colocando pixels na tela antes.

As três famílias de solução atacam termos diferentes:

- **Ilhas**: reduz o `n` da hidratação para o subconjunto interativo. `hidratação(k)`, com `k << n`.
- **RSC**: reduz o `n` **e** o tamanho do bundle — componentes de servidor não têm contraparte no cliente.
- **Resumabilidade**: elimina o termo. `hidratação(n) → 0`, pagando serialização e carregamento sob demanda por interação.

Visto assim, as três não são concorrentes filosóficos: são otimizações de termos distintos da mesma equação, e podem coexistir. Isso é consistente com o que se observa em 2026 — RSC e signals sendo combinados em vez de disputados.

---

## 9. Leituras primárias

Para quem quer ir à fonte, e não a resumos:

- **Código do Solid** (`packages/solid/src/reactive/signal.ts`) — a implementação de reatividade fina mais legível que existe. É o melhor ponto de partida para entender o modelo de verdade.
- **`ReactFiberWorkLoop.js`** no repositório do React — dura, mas é onde o modelo de prioridades vive.
- **`patchKeyedChildren`** no Vue 3 — o LIS aplicado, com comentários.
- **Compilador do Svelte** — como uma AST vira código imperativo.
- **RFC dos React Server Components** — o documento de projeto, com as alternativas consideradas e rejeitadas.
- Referências completas em [`17-referencias.md`](17-referencias.md).

---

## 10. Autoteste

1. Por que o tree edit distance exato é inviável, e quais duas heurísticas o React usa para chegar a `O(n)`?
2. Por que `key={index}` numa lista reordenável é equivalente a não ter chave?
3. O que o Fiber muda estruturalmente para permitir interrupção, e por que a recursão do React 15 não permitia?
4. Por que a fase de commit precisa ser síncrona e atômica?
5. O que é um glitch num grafo reativo e como a ordem topológica o previne?
6. Por que efeitos precisam limpar dependências antes de cada execução?
7. Por que `n` é uma função no Solid?
8. Por que a virtualização vence qualquer otimização de algoritmo de diff em listas grandes?
9. Formalize por que SSR não reduz o trabalho total do cliente, e como cada uma das três soluções ataca um termo diferente.

---

**Anterior:** [12 — Build e deploy](12-build-deploy-infra.md) · **Próximo:** [14 — Estado da arte 2026](14-estado-da-arte.md)
