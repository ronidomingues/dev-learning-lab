# 07 · Estratégias de renderização

**Nível: intermediário → avançado** · Pré-requisitos: `04`.

Este é o arquivo central do curso. A pergunta "SPA ou não?" foi substituída, e a pergunta certa hoje é: **onde e quando cada pedaço do HTML é gerado?**

---

## 1. As duas perguntas que definem tudo

Toda estratégia de renderização é uma resposta a duas perguntas independentes:

1. **Onde o HTML é produzido?** No navegador, no servidor, ou na máquina de build?
2. **Quando?** Em tempo de build, a cada requisição, ou continuamente no cliente?

Cruzando as respostas:

|  | No build | Por requisição (servidor) | No cliente |
|---|---|---|---|
| **HTML inicial** | SSG | SSR | CSR |
| **Atualizações** | — | MPA (recarrega) | SPA |

E o mundo real combina as células. Praticamente todo framework sério em 2026 faz **SSR ou SSG para o HTML inicial + SPA para as atualizações**. Esse é o híbrido.

---

## 2. CSR — Client-Side Rendering (a SPA pura)

```
Servidor:  <div id="root"></div> + app.js
Navegador: baixa → executa → busca dados → pinta
```

```
Requisição │ Servidor │ Cliente
───────────┼──────────┼──────────────────────────────────
GET /      │ shell    │ █ baixa JS ███ executa ██ fetch ███ pinta
           │ 20ms     │ 0 ─────────────────────► 2.1s até útil
```

**A favor:** infraestrutura trivial (arquivos estáticos em CDN, sem servidor de aplicação), navegação subsequente instantânea, separação limpa entre front e back, custo de servidor perto de zero, funciona bem como app instalável.

**Contra:** o pior tempo até o primeiro conteúdo de todas as estratégias; tela branca se o JS falhar; SEO exige trabalho extra; a cascata JS → dados é estrutural (arquivo `04`, seção 2); todo o custo de CPU recai sobre o dispositivo do usuário — que pode ser um celular de entrada.

**Quando é a escolha certa, em 2026:**
- Aplicações atrás de login, onde SEO é irrelevante e a sessão é longa (painéis, ERPs, ferramentas internas, editores).
- Aplicações onde o "primeiro carregamento" acontece uma vez por semana e o que importa é a interação depois.
- Quando não há e não haverá servidor Node — só um bucket e um CDN.

Não é uma estratégia obsoleta. É uma estratégia com escopo bem definido.

---

## 3. SSR — Server-Side Rendering

O servidor executa os componentes e devolve HTML completo. O cliente exibe imediatamente e depois "liga" o JavaScript.

```
Requisição │ Servidor                    │ Cliente
───────────┼─────────────────────────────┼─────────────────────────────
GET /      │ busca dados ██ renderiza ██ │ █ pinta (0.4s VISÍVEL)
           │ 180ms                       │ ███ baixa JS ██ hidrata
           │                             │ ────────► 1.2s interativo
```

O usuário **vê** conteúdo em 400 ms em vez de 2,1 s. Mas atenção ao que isso significa exatamente:

> **SSR melhora drasticamente o tempo até *ver*. Melhora pouco, ou nada, o tempo até *interagir*.**
>
> O JavaScript ainda precisa ser baixado e executado para os botões funcionarem. Existe uma janela — o *uncanny valley* — em que a página está visível e parece pronta, mas cliques não fazem nada. Se essa janela for longa, a experiência é pior que um spinner honesto, porque frustra a expectativa.

### Hidratação

O processo de "ligar" o HTML do servidor ao JavaScript do cliente:

```jsx
// servidor
const html = renderToString(<App dados={dados} />);
res.send(`<div id="root">${html}</div>
          <script>window.__DADOS__=${serializar(dados)}</script>
          <script type="module" src="/app.js"></script>`);

// cliente
hydrateRoot(document.querySelector('#root'), <App dados={window.__DADOS__} />);
```

O React re-renderiza a árvore inteira em memória, **compara com o DOM existente** e, em vez de criar nós, apenas anexa os manipuladores de evento.

O custo é o ponto crítico e o motivo pelo qual metade da inovação recente do campo existe:

> **A hidratação executa praticamente todo o trabalho de renderização de novo, no cliente.** Você pagou pelo render no servidor e paga de novo no cliente. É por isso que a hidratação de páginas pesadas pode ser mais lenta que uma CSR — e é o problema que ilhas, RSC e resumabilidade atacam por caminhos diferentes.

### Erros de hidratação

Ocorrem quando o HTML do servidor difere do que o cliente renderiza. Causas clássicas:

```jsx
// TODAS erradas sob SSR:
<p>{new Date().toLocaleString()}</p>        // fusos/relógios diferentes
<p>{Math.random()}</p>                       // óbvio
<p>{window.innerWidth}</p>                   // window não existe no servidor
<p>{localStorage.getItem('tema')}</p>        // idem
```

O padrão correto para conteúdo que **só** pode existir no cliente:

```jsx
const [montado, setMontado] = useState(false);
useEffect(() => setMontado(true), []);
return <p>{montado ? new Date().toLocaleString() : null}</p>;
```

Ou, quando você aceita a diferença numa folha da árvore, `suppressHydrationWarning`.

**Serialização de dados é um vetor de XSS.** `JSON.stringify` pode produzir `</script>` dentro de uma string e fechar sua tag. Use uma função que escape `<`, `>`, `&`, U+2028 e U+2029 — ou uma biblioteca como `serialize-javascript`, `superjson` ou `devalue`. Arquivo `11`.

### SSR com streaming

Em vez de esperar todo o HTML ficar pronto, envie em pedaços conforme ficam disponíveis:

```jsx
// React 18+
renderToPipeableStream(<App />, { onShellReady() { res.pipe(...) } });

<Suspense fallback={<Esqueleto />}>
  <ComentariosLentos />     {/* chega depois, sem segurar o resto */}
</Suspense>
```

O navegador recebe e pinta o cabeçalho enquanto o servidor ainda consulta o banco para os comentários. O TTFB despenca e o LCP melhora, porque nada rápido fica refém do mais lento. Em 2026 isso é padrão nos meta-frameworks, não uma otimização exótica.

---

## 4. SSG — Static Site Generation

Renderiza no **build**. Sai HTML puro, servido de CDN.

```
Build (1x):  gera 5.000 arquivos HTML
Requisição:  CDN entrega em ~20ms. Sem servidor. Sem banco.
```

Imbatível em velocidade, custo e confiabilidade — não há o que cair. Limites: conteúdo igual para todos, e rebuild a cada mudança (o que fica proibitivo com dezenas de milhares de páginas, embora builds incrementais tenham melhorado muito).

Ideal para: documentação, blog, marketing, landing pages, catálogos que mudam pouco.

---

## 5. ISR / regeneração sob demanda

O híbrido entre SSG e SSR: gera estático, mas revalida em background.

```js
// Next.js
export const revalidate = 60;   // após 60s, a próxima visita dispara regeneração em background
```

A primeira visita após o prazo recebe a versão antiga (rápida) e **dispara** a regeneração. As seguintes recebem a nova. É *stale-while-revalidate* aplicado a páginas inteiras.

Some a isso a invalidação sob demanda — o CMS chama um webhook ao publicar e a página é regenerada na hora — e você tem o melhor custo-benefício disponível para conteúdo que muda de forma imprevisível.

---

## 6. Arquitetura de ilhas

Proposta pelo Astro (2021) e hoje amplamente copiada. A premissa é uma observação simples e correta:

> **A maior parte de uma página não é interativa.** Cabeçalho, texto, rodapé, imagens — nada disso precisa de JavaScript. Por que hidratar tudo?

```astro
---
const posts = await buscarPosts();     // roda no build/servidor, some do bundle
---
<Layout>
  <Cabecalho />                        <!-- HTML puro, 0 KB de JS -->
  <ListaPosts posts={posts} />         <!-- HTML puro, 0 KB de JS -->
  <Busca client:visible />             <!-- ILHA: hidrata só quando entra na viewport -->
  <Curtir client:idle />               <!-- ILHA: hidrata quando a thread estiver ociosa -->
</Layout>
```

Cada ilha hidrata **independentemente** e sob a diretiva que você escolher (`client:load`, `client:idle`, `client:visible`, `client:media`). Um site de conteúdo típico sai de ~300 KB de JS para ~15 KB.

Limitação real: ilhas não compartilham estado facilmente entre si — são árvores separadas. Para aplicações com estado global rico, o modelo não serve. Para sites de conteúdo com interatividade pontual, é o melhor que existe.

---

## 7. Resumabilidade (Qwik)

Ataca a hidratação pela raiz, com uma tese radical:

> Hidratar é **repetir** trabalho. Em vez disso, serialize o estado *e as referências de código* no HTML, e simplesmente **continue** de onde o servidor parou.

```html
<button on:click="./chunk-a7.js#handler_3">Curtir</button>
```

Nenhum JavaScript executa no carregamento. **Zero.** Ao clicar, o Qwik baixa aquele fragmento específico e o executa. O tempo até interativo torna-se essencialmente constante, independente do tamanho da aplicação.

Custo: exige um compilador que fatia o código em granularidade de função, serialização complexa (incluindo grafos de objetos com referências circulares) e um modelo mental diferente do resto do mercado. Em 2026 continua tecnicamente admirável e de nicho — a adoção não acompanhou a qualidade da ideia. **Vale estudar mesmo sem usar**, porque a tese está certa e outras ferramentas vão absorvê-la.

---

## 8. RSC — React Server Components

A mudança mais significativa do React desde os hooks, e o padrão do Next.js App Router.

**A ideia:** alguns componentes rodam **apenas no servidor**. Seu código nunca é enviado ao navegador. Eles podem acessar banco, ler arquivos, usar segredos — e compõem normalmente com componentes de cliente.

```jsx
// app/produtos/[id]/page.tsx — Server Component (padrão, sem diretiva)
import { db } from '@/lib/db';
import BotaoComprar from './BotaoComprar';

export default async function Pagina({ params }) {
  const produto = await db.produto.findUnique({ where: { id: params.id } });  // SQL direto
  return (
    <article>
      <h1>{produto.nome}</h1>
      <p>{produto.descricao}</p>
      <BotaoComprar id={produto.id} />    {/* fronteira: daqui pra baixo é cliente */}
    </article>
  );
}
```

```jsx
// BotaoComprar.tsx — Client Component
'use client';
export default function BotaoComprar({ id }) {
  const [n, setN] = useState(1);
  return <button onClick={() => comprar(id, n)}>Comprar {n}</button>;
}
```

O que muda de verdade:

| | Antes (SPA/SSR) | Com RSC |
|---|---|---|
| Código de busca de dados | vai para o bundle | fica no servidor |
| Bibliotecas pesadas (markdown, datas, ORM) | vão para o bundle | ficam no servidor |
| Acesso a banco | precisa de API intermediária | direto no componente |
| Cascata de dados | JS → rota → fetch | dados junto com o HTML |
| Segredos | impossível | naturais |

O bundle de uma página de conteúdo cai drasticamente porque a lógica de dados e as dependências de renderização de texto simplesmente **não existem** no cliente.

### As regras de fronteira

1. `'use client'` marca uma **fronteira**, não um arquivo isolado — tudo que ele importa também vai para o cliente.
2. Server Component pode renderizar Client Component. **O inverso não** — exceto passando como `children`, que é a válvula de escape importante:

```jsx
<ClienteInterativo>
  <ComponenteDeServidor />    {/* funciona: já foi renderizado, chega como children */}
</ClienteInterativo>
```

3. Props que cruzam a fronteira precisam ser **serializáveis**. Funções, classes e `Date`... (o `Date` funciona; funções não).
4. Server Components não têm estado, efeitos nem eventos. Não são componentes no sentido tradicional — são mais próximos de templates assíncronos.

### Server Actions

Mutações sem escrever API:

```jsx
// no Server Component
async function salvar(formData) {
  'use server';
  await db.produto.update({ where: { id }, data: { nome: formData.get('nome') } });
  revalidatePath(`/produtos/${id}`);
}
<form action={salvar}><input name="nome" /><button>Salvar</button></form>
```

Funciona **sem JavaScript** (é um `<form>` de verdade) e é aprimorado progressivamente quando o JS carrega. É a melhor concretização de aprimoramento progressivo que o React já teve.

**Aviso de segurança que muita gente ignora:** uma Server Action é um **endpoint HTTP público**. Qualquer pessoa pode chamá-la com qualquer payload. Autentique e valide **dentro** dela, sempre. Não confie em ela estar "escondida" atrás de um formulário.

### Onde RSC está em 2026

Números da pesquisa de campo: **~45% dos projetos novos** usam Server Components, mas só **~29% dos desenvolvedores** já os usaram; mais da metade tem opinião positiva, e **6% os citam explicitamente como ponto de dor**. Suporte de framework: Next.js é o único com suporte plenamente pronto para produção; Remix v3 adotou e ainda amadurece; fazer do zero com Vite é possível e trabalhoso.

**Minha leitura profissional:** RSC resolve problemas reais e a direção está certa. Mas ele adiciona uma fronteira conceitual nova — o que roda onde — que é a principal fonte de erro para times, e prende você a um framework. Para aplicações de conteúdo com bastante dado, o ganho é claro. Para uma ferramenta interna atrás de login, o ganho é pequeno e a complexidade é real. Não é obrigatório.

---

## 9. PPR — Partial Prerendering

A síntese mais recente: uma **única página** combina casca estática e furos dinâmicos.

```jsx
export const experimental_ppr = true;

export default function Pagina() {
  return (
    <>
      <Cabecalho />                                  {/* estático, do CDN, instantâneo */}
      <Suspense fallback={<EsqueletoCarrinho />}>
        <Carrinho />                                 {/* dinâmico, streaming, por usuário */}
      </Suspense>
    </>
  );
}
```

O CDN entrega a casca imediatamente; o conteúdo pessoal chega em streaming no mesmo response. Você deixa de escolher entre "a página inteira é estática" e "a página inteira é dinâmica" — a decisão passa a ser por região. Em 2026 é a fronteira ativa dessa área.

---

## 10. Comparação direta

| Estratégia | TTFB | Ver conteúdo | Interagir | JS enviado | SEO | Infra |
|---|---|---|---|---|---|---|
| **CSR** | ★★★★★ | ★☆☆☆☆ | ★★☆☆☆ | alto | ★★☆☆☆ | trivial |
| **SSR** | ★★★☆☆ | ★★★★☆ | ★★★☆☆ | alto | ★★★★★ | servidor |
| **SSR + streaming** | ★★★★★ | ★★★★★ | ★★★☆☆ | alto | ★★★★★ | servidor |
| **SSG** | ★★★★★ | ★★★★★ | ★★★☆☆ | médio | ★★★★★ | CDN |
| **ISR** | ★★★★★ | ★★★★★ | ★★★☆☆ | médio | ★★★★★ | servidor+CDN |
| **Ilhas** | ★★★★★ | ★★★★★ | ★★★★★ | **mínimo** | ★★★★★ | CDN |
| **Resumível** | ★★★★★ | ★★★★★ | ★★★★★ | ~zero | ★★★★★ | servidor |
| **RSC + PPR** | ★★★★★ | ★★★★★ | ★★★★☆ | baixo | ★★★★★ | servidor+CDN |

Leia com cuidado: "interagir" penaliza tudo que hidrata. É exatamente por isso que ilhas e resumabilidade existem.

---

## 11. Como escolher — árvore de decisão

```
O conteúdo é público e o SEO importa?
├── NÃO (app atrás de login)
│   └── A sessão é longa e a interação intensa?
│       ├── SIM → CSR (SPA pura). É o caso legítimo. Invista em code splitting.
│       └── NÃO → considere MPA/SSR: menos complexidade pelo mesmo resultado.
└── SIM
    └── O conteúdo muda com que frequência?
        ├── Raramente → SSG (Astro, se for majoritariamente conteúdo → ilhas)
        ├── Periodicamente → ISR / revalidação sob demanda
        └── Por usuário / tempo real → SSR com streaming
            └── Há muita interatividade?
                ├── Pouca e localizada → ilhas
                └── Muita → RSC + Client Components (+ PPR se disponível)
```

**Heurística que uso na prática:** comece pelo mais estático que atenda o requisito e só suba um degrau quando um requisito concreto obrigar. O caminho inverso — começar com a arquitetura mais poderosa "porque pode precisar" — é como se produz o excesso descrito no arquivo `03`.

---

## 12. A pergunta honesta: SPA ainda faz sentido?

Sim, com escopo. A SPA pura continua sendo a escolha certa quando:

- O SEO é irrelevante (tudo atrás de autenticação).
- A sessão dura horas e o custo do carregamento inicial se amortiza.
- O estado do cliente é rico e persistente entre telas (editores, DAWs, CADs, planilhas, mapas).
- Você precisa funcionar offline.
- Não há infraestrutura de servidor e não vai haver.

E deixou de ser a escolha certa quando o site é, essencialmente, **conteúdo com alguma interatividade** — que é a maioria dos sites da web. Para esses, o híbrido servidor-primeiro entrega melhor experiência com menos código.

---

## 13. Autoteste

1. Por que SSR melhora muito o "tempo até ver" e pouco o "tempo até interagir"?
2. O que é o *uncanny valley* da hidratação e por que pode ser pior que um spinner?
3. Cite três causas de erro de hidratação e o padrão que as resolve.
4. Qual observação sobre páginas reais justifica a arquitetura de ilhas?
5. Qual é a tese da resumabilidade, e por que ela torna o tempo até interativo independente do tamanho da app?
6. Por que um Client Component não pode importar um Server Component, mas pode recebê-lo como `children`?
7. Por que uma Server Action precisa validar autenticação internamente?
8. Para um blog pessoal com uma caixa de comentários, qual estratégia você escolheria e por quê?

---

**Anterior:** [06 — Estado](06-estado.md) · **Próximo:** [08 — Dados e rede](08-dados-e-rede.md)
