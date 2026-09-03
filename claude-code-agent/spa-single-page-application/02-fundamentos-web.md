# 02 · Fundamentos da web

**Nível: iniciante** · Pré-requisitos: nenhum. Este arquivo constrói o vocabulário usado em todo o resto do curso.

Se você já sabe HTTP, DOM e event loop com segurança, pule para o `03`. Mas leia a seção 6 — ela é onde a maioria das pessoas tem um buraco.

---

## 1. Cliente, servidor e o pedido

A web é um protocolo de **pergunta e resposta**. Um lado pergunta (o **cliente**, normalmente seu navegador), o outro responde (o **servidor**, um computador ligado em algum lugar).

O idioma dessa conversa é o **HTTP** (*HyperText Transfer Protocol*). Uma pergunta HTTP se chama **requisição** (*request*) e tem esta forma:

```http
GET /produtos/42 HTTP/1.1
Host: loja.exemplo.com
Accept: text/html
Cookie: sessao=abc123
```

Leia linha por linha:

- `GET` é o **método** — o verbo. Diz a intenção.
- `/produtos/42` é o **caminho** (*path*) — qual recurso você quer.
- `Host:`, `Accept:`, `Cookie:` são **cabeçalhos** (*headers*) — metadados sobre o pedido.

A resposta tem forma parecida:

```http
HTTP/1.1 200 OK
Content-Type: text/html; charset=utf-8
Cache-Control: max-age=3600

<!doctype html><html>...
```

- `200` é o **código de status**. `2xx` deu certo, `3xx` redirecione, `4xx` você errou, `5xx` eu errei.
- Depois da linha em branco vem o **corpo** (*body*) — o conteúdo de fato.

### Os métodos que importam

| Método | Significado | Seguro? | Idempotente? |
|---|---|---|---|
| `GET` | leia algo, não mude nada | sim | sim |
| `POST` | crie / execute uma ação | não | não |
| `PUT` | substitua inteiramente | não | sim |
| `PATCH` | altere parcialmente | não | não |
| `DELETE` | remova | não | sim |

**Seguro** significa "não altera estado no servidor". **Idempotente** significa "fazer duas vezes tem o mesmo efeito que fazer uma vez".

> **Por que isso importa numa SPA:** só `GET` pode ser cacheado por navegadores, CDNs e proxies. Toda a estratégia de cache do arquivo `08` depende de você usar os verbos corretamente. Uma API que faz `POST /listarUsuarios` jogou fora, de graça, a camada de cache inteira da internet.

### Códigos de status que você vai encontrar

| Código | Nome | Quando aparece numa SPA |
|---|---|---|
| 200 | OK | tudo certo |
| 201 | Created | após criar um recurso via POST |
| 204 | No Content | sucesso sem corpo (ex.: DELETE) |
| 301 / 308 | Moved Permanently | redirect permanente, cacheado agressivamente |
| 302 / 307 | Found / Temporary Redirect | redirect temporário |
| 304 | Not Modified | seu cache ainda vale — resposta sem corpo, barata |
| 400 | Bad Request | você mandou lixo |
| 401 | Unauthorized | você não está autenticado (nome infeliz) |
| 403 | Forbidden | você está autenticado mas não pode |
| 404 | Not Found | não existe |
| 409 | Conflict | conflito de estado (edição concorrente) |
| 422 | Unprocessable | sintaxe ok, semântica inválida — validação |
| 429 | Too Many Requests | rate limit |
| 500 | Internal Server Error | quebrou do lado deles |
| 503 | Service Unavailable | fora do ar / sobrecarga |

O par 401/403 confunde todo mundo: **401 = "quem é você?", 403 = "sei quem você é e a resposta é não"**.

### Uma propriedade decisiva: HTTP não tem memória

HTTP é **stateless** — sem estado. O servidor, por padrão, não faz ideia de que a requisição de agora veio da mesma pessoa que a de um segundo atrás. Cada pedido chega do zero.

Toda a noção de "estar logado" é uma construção **por cima** disso: o servidor manda um identificador (num cookie ou num token), e o cliente o reenvia em cada requisição. É por isso que autenticação é um assunto inteiro (arquivo `11`) e não um detalhe.

---

## 2. HTML: o documento

**HTML** (*HyperText Markup Language*) descreve **estrutura e significado** do conteúdo — não aparência.

```html
<!doctype html>
<html lang="pt-BR">
  <head>
    <meta charset="utf-8">
    <title>Minha loja</title>
  </head>
  <body>
    <h1>Camiseta preta</h1>
    <p>Algodão, R$ 79,00.</p>
    <button type="button">Comprar</button>
  </body>
</html>
```

Cada `<coisa>...</coisa>` é um **elemento**. Elementos aninham-se, formando uma **árvore**: `html` contém `body`, que contém `h1` e `p`.

A palavra-chave é **semântica**. `<h1>` não significa "texto grande" — significa "este é o título principal deste documento". `<button>` não significa "retângulo clicável" — significa "isto executa uma ação, é focável pelo teclado, é anunciado como botão por um leitor de tela e responde a Enter e Espaço".

> **Consequência prática, e uma das causas mais comuns de SPA inacessível:** quando você escreve `<div onclick="...">` em vez de `<button>`, você produz algo que *parece* um botão para quem enxerga e *não existe* para quem navega por teclado ou leitor de tela. O navegador dá acessibilidade de graça se você usar os elementos certos; se não usar, você terá que reimplementar tudo com ARIA — e vai fazer pior. Detalhado no arquivo `10`.

---

## 3. CSS: a apresentação

**CSS** (*Cascading Style Sheets*) diz como o HTML deve parecer.

```css
button { background: black; color: white; padding: 8px 16px; }
```

Para este curso, o que importa do CSS é uma propriedade: **CSS é bloqueante de renderização** (*render-blocking*). O navegador **não pinta nada** enquanto não tiver processado o CSS que ele considera necessário para a tela inicial — porque pintar antes causaria um "flash" de conteúdo sem estilo. Isso terá consequências diretas em performance (arquivo `09`).

---

## 4. O DOM: a árvore viva

Aqui está o conceito mais importante deste arquivo.

Quando o HTML chega, o navegador **não guarda o texto**. Ele **analisa** (*parse*) esse texto e constrói na memória uma estrutura de objetos chamada **DOM** — *Document Object Model*.

```
Document
 └── html
      ├── head
      │    └── title → "Minha loja"
      └── body
           ├── h1 → "Camiseta preta"
           ├── p  → "Algodão, R$ 79,00."
           └── button → "Comprar"
```

O ponto crucial:

> **O HTML é o texto inicial. O DOM é a estrutura viva.** Depois que o DOM existe, o HTML original é irrelevante — mudar o DOM muda a tela; mudar a string de HTML original não muda nada.

E o DOM é **programável**. O JavaScript pode lê-lo e alterá-lo:

```js
const titulo = document.querySelector('h1');   // acha o nó
titulo.textContent = 'Camiseta branca';        // muda — a tela atualiza na hora
const novo = document.createElement('p');      // cria um nó novo
novo.textContent = 'Frete grátis';
document.body.appendChild(novo);               // insere na árvore
```

**Esta é a base técnica de toda SPA.** Uma SPA é, no fundo, um programa que manipula o DOM em resposta a eventos e dados, em vez de pedir documentos novos ao servidor. Tudo mais — React, Vue, roteadores, estado — são abstrações construídas sobre estas quatro linhas.

### Os quatro custos da manipulação do DOM

Nem toda alteração custa o mesmo. O navegador trabalha em etapas:

1. **Recalculate style** — decidir quais regras CSS se aplicam a quais nós.
2. **Layout** (também chamado *reflow*) — calcular posição e tamanho de cada elemento. **Caro.**
3. **Paint** — desenhar pixels de cada camada.
4. **Composite** — juntar as camadas na tela. **Barato**, roda na GPU.

Mudar `width` ou `top` dispara layout, paint e composite. Mudar `transform` ou `opacity` dispara **só composite** — por isso animações performáticas usam `transform`, não `left`. Isso reaparece no arquivo `09`.

### Layout thrashing — a armadilha clássica

Ler uma propriedade geométrica (`offsetHeight`, `getBoundingClientRect()`) força o navegador a **recalcular o layout imediatamente**, porque ele precisa dar a você um valor correto. Se você intercala leitura e escrita num laço:

```js
// PÉSSIMO — força um layout por iteração. O(n) reflows.
for (const el of elementos) {
  el.style.height = el.offsetHeight + 10 + 'px';   // lê, escreve, lê, escreve...
}

// BOM — agrupa leituras, depois escritas. 1 reflow.
const alturas = elementos.map(el => el.offsetHeight);       // todas as leituras
elementos.forEach((el, i) => el.style.height = alturas[i] + 10 + 'px');  // todas as escritas
```

Isso se chama **layout thrashing** e é uma das causas mais comuns de travamento em listas grandes.

---

## 5. JavaScript: o motor

**JavaScript** é a linguagem que o navegador executa. Criada em 1995 por Brendan Eich em dez dias — um fato que explica boa parte das suas esquisitices —, é hoje padronizada como **ECMAScript**, com uma revisão anual.

O mínimo que este curso assume:

```js
// valores e funções
const nome = 'Ana';
const soma = (a, b) => a + b;

// objetos e arrays
const usuario = { id: 1, nome: 'Ana' };
const lista = [1, 2, 3];
const dobro = lista.map(n => n * 2);            // [2, 4, 6]

// desestruturação e spread
const { id, nome: n } = usuario;
const copia = { ...usuario, nome: 'Bia' };      // cópia rasa com alteração

// módulos
export function util() {}
import { util } from './util.js';
```

E o conceito que realmente importa: **assincronia**.

```js
// Promise: um valor que ainda não existe, mas existirá (ou falhará)
async function carregarUsuario(id) {
  const resposta = await fetch(`/api/usuarios/${id}`);   // pausa aqui, não trava a página
  if (!resposta.ok) throw new Error(`HTTP ${resposta.status}`);
  return resposta.json();
}
```

`await` **não bloqueia a página**. Ele suspende *aquela função* e devolve o controle ao navegador, que segue respondendo a cliques e rolagem. Quando a resposta chega, a função retoma de onde parou. Entender por que isso funciona exige a próxima seção.

---

## 6. O event loop — a seção que quase ninguém domina

**JavaScript no navegador é single-threaded.** Existe **uma única thread** que executa seu código, calcula estilo, faz layout e pinta. Uma só.

A consequência é brutal e é a origem de metade dos problemas de performance de SPA:

> **Enquanto seu JavaScript está rodando, o navegador não pode pintar, não pode responder a cliques, não pode rolar a página.** Um cálculo de 300 ms é a página congelada por 300 ms.

Como então tudo parece funcionar ao mesmo tempo? Pelo **event loop**:

```
┌─────────────────────────────────────────────────┐
│  Call stack (a thread única)                    │
│  executa uma tarefa até o fim, sem interrupção  │
└────────────────┬────────────────────────────────┘
                 │ quando esvazia:
                 ▼
       ┌───────────────────────┐
       │ Microtask queue       │  ← Promises, queueMicrotask
       │ ESVAZIA COMPLETAMENTE │     (roda TUDO antes de seguir)
       └──────────┬────────────┘
                  ▼
       ┌───────────────────────┐
       │ Render (se for hora)  │  ← style → layout → paint → composite
       │ ~a cada 16,6 ms @60Hz │
       └──────────┬────────────┘
                  ▼
       ┌───────────────────────┐
       │ Macrotask queue       │  ← cliques, setTimeout, respostas de rede
       │ pega UMA e recomeça   │
       └───────────────────────┘
```

Três regras que decorrem daí:

**Regra 1 — uma tarefa roda até o fim.** Nada a interrompe. Um `for` de 10 milhões de iterações trava tudo até terminar.

**Regra 2 — microtasks têm prioridade e podem matar de fome.** A fila de microtasks é esvaziada *inteira* antes de qualquer renderização. Uma microtask que agenda outra microtask, indefinidamente, **congela a página para sempre** — o navegador nunca chega à etapa de render.

**Regra 3 — a renderização só acontece entre tarefas.** Por isso:

```js
elemento.style.opacity = 0;
elemento.style.opacity = 1;
// O usuário NUNCA vê opacity 0. Nada foi pintado entre as duas linhas —
// a mesma tarefa ainda está rodando. O navegador só pinta o estado final.
```

Este é o motivo pelo qual "mudar o DOM muitas vezes seguidas" não é caro por si só: o navegador coalesce as mudanças e pinta uma vez. O que é caro é **forçar layout no meio** (seção 4).

### O orçamento de 16 milissegundos

Numa tela de 60 Hz, você tem **16,6 ms por quadro** para fazer tudo: rodar JS, estilo, layout, paint. Passou disso, um quadro é perdido e o usuário percebe travamento. Em telas de 120 Hz, 8,3 ms.

Uma tarefa acima de **50 ms** é oficialmente uma **long task** e é o que arruína a métrica INP (arquivo `09`).

Escapatórias quando você realmente precisa calcular muito:

- **Web Workers** — outra thread de verdade. Não têm acesso ao DOM, comunicam-se por mensagem.
- **Fatiar o trabalho** — processar em lotes, devolvendo o controle entre eles (`scheduler.yield()`, ou `setTimeout(…, 0)` no modelo antigo).
- **`requestIdleCallback`** — rodar trabalho não urgente quando a thread estiver ociosa.
- **Concorrência do framework** — o modo concorrente do React fatia a renderização automaticamente (arquivo `13`).

---

## 7. Os quatro passos, do zero à tela

Juntando tudo, o que acontece quando você digita uma URL:

1. **DNS** — traduz `loja.exemplo.com` num endereço IP.
2. **TCP + TLS** — abre a conexão e negocia a criptografia (o `https`). Custa idas e voltas.
3. **HTTP** — envia a requisição, recebe a resposta.
4. **Parse + render** — o navegador lê o HTML construindo o DOM, encontra referências a CSS e JS, busca-as, monta a árvore de renderização, calcula layout, pinta.

Um detalhe do passo 4 que importa muito: quando o parser encontra `<script src="...">` **sem atributo**, ele **para tudo** — porque o script pode chamar `document.write()` e alterar o próprio HTML sendo lido. Por isso existem:

- `defer` — baixa em paralelo, executa depois do HTML pronto, **na ordem** declarada. É o padrão certo para a maioria dos casos.
- `async` — baixa em paralelo, executa assim que chegar, **fora de ordem**. Para scripts independentes (analytics).
- `type="module"` — comporta-se como `defer` automaticamente.

```html
<script defer src="/app.js"></script>   <!-- não bloqueia o parser -->
```

---

## 8. Autoteste

1. Por que `POST /buscarProdutos` é um erro de design, mesmo funcionando?
2. Qual a diferença entre HTML e DOM? Por que ela é a base de toda SPA?
3. Por que o código abaixo não faz o texto piscar?
   ```js
   el.textContent = 'A'; el.textContent = 'B';
   ```
4. Por que ler `offsetHeight` dentro de um laço que também escreve estilos é lento?
5. Se JavaScript é single-threaded, como uma animação continua rodando enquanto você espera um `fetch`?
6. O que acontece se uma microtask agendar outra microtask para sempre?

---

**Anterior:** [01 — Introdução para leigos](01-introducao-leigo.md) · **Próximo:** [03 — História](03-historia.md)
