# 14 · Estado da arte — agosto de 2026

**Nível: pesquisa** · Pré-requisitos: `07`, `13`.

Este arquivo tem prazo de validade curto. Ele separa deliberadamente **fato verificável**, **consenso do campo** e **opinião minha** — porque misturar as três é como se propaga folclore técnico.

---

## 1. O que é consenso hoje

Cinco afirmações que, em 2026, são posição majoritária e bem sustentada:

**1. Híbrido venceu.** A pergunta "SPA ou MPA" está encerrada. Server-first para o HTML inicial + navegação client-side depois é o padrão. Mais de 60% das aplicações React usam alguma forma de renderização mista. A discussão hoje é sobre **granularidade** — qual pedaço da página é estático, qual é streaming, qual é interativo.

**2. Reatividade fina venceu o Virtual DOM como modelo de execução.** Solid, Svelte 5 (runes), Angular (signals) e Vue convergiram. O React é a exceção notável — e responde com o compilador em vez de mudar o modelo. Os frameworks estão convergindo em quatro temas: reatividade fina, renderização server-first, otimização por compilador com TypeScript como padrão, e fluxos assistidos por IA.

**3. Compiladores em vez de anotação manual.** O React Compiler (estável no React 19) infere memoização e torna `useMemo`/`useCallback` manuais amplamente desnecessários. Svelte sempre foi compilado. A direção é uniforme: mover trabalho e decisão para o build.

**4. A infraestrutura de build migrou para linguagens nativas.** Vite (com Rolldown), Turbopack, Rspack, SWC, esbuild. Webpack e Babel são legado em manutenção.

**5. INP é a métrica que separa aplicações boas de ruins.** Substituiu o FID em 2024 e é onde SPAs mal construídas falham. RSC, reatividade fina e INP são apontados como os três eixos que mais visivelmente separam produtos bem arquitetados dos que sofrem em 2026.

---

## 2. O que está em disputa

### RSC: consolidado no topo, longe de universal

**Fatos:** ~48% dos usuários diários de React estão no React 19. Server Components aparecem em **~45% dos projetos novos**, mas apenas **~29% dos desenvolvedores** já os usaram; mais da metade tem sentimento positivo e **6% os citam explicitamente como ponto de dor**. Next.js é o único framework com suporte plenamente pronto para produção; Remix v3 adotou e ainda amadurece; construir do zero com Vite é possível e complexo. Ganhos relatados de tempo de render inicial na ordem de 2,4 s → 0,8 s em adoções com meta-framework.

**Em disputa:** se a complexidade da fronteira cliente/servidor compensa fora de aplicações com muito conteúdo e muitos dados; e o grau de acoplamento a um framework que ela impõe.

> **Opinião minha:** RSC é tecnicamente sólido e a direção está certa. Mas a fronteira "o que roda onde" é uma categoria conceitual nova, e categorias novas custam caro em times reais — em erros, em onboarding, em revisão de código. Para conteúdo público com muitos dados, o ganho é claro e mensurável. Para uma ferramenta interna atrás de login, o ganho é pequeno e a complexidade é real. **Adotar RSC não é sinal de maturidade técnica; adotá-lo onde ele resolve um problema seu, sim.**

### Signals no React

Há debate antigo sobre incorporar signals ao React. A posição do time do React tem sido: o compilador oferece boa parte do benefício sem quebrar o modelo mental de "re-execute e compare". Há uma proposta de signals para o próprio TC39 (padronizar no JavaScript), que avançaria a interoperabilidade entre frameworks.

> **Opinião minha:** signals padronizados na linguagem seriam mais transformadores que qualquer framework individual — bibliotecas de estado passariam a funcionar em qualquer framework. É a coisa mais interessante em andamento nesta área, e vale acompanhar.

### O peso do JavaScript

O bundle mediano continua crescendo, apesar de dez anos de discurso sobre performance. Ilhas e RSC reduzem onde são aplicados, mas a média sobe porque as aplicações fazem mais coisas.

> **Opinião minha:** este é um problema de incentivos, não de tecnologia. Ferramentas melhores não resolvem — a equipe adiciona funcionalidades até o orçamento estourar de novo. O que funciona é orçamento no CI que **falha o build** (arquivo `09`), porque transforma uma preferência em restrição.

### GraphQL

Estabilizou num nicho: vale quando há vários clientes heterogêneos sobre o mesmo backend. Para um único frontend, o custo raramente se paga. É uma correção coletiva em relação ao entusiasmo de 2018 — e um bom exemplo de tecnologia boa aplicada onde não cabia.

---

## 3. Panorama de frameworks

| Framework | Modelo | Situação em 2026 |
|---|---|---|
| **React** | VDOM + compilador | ~44,7% de adoção (Stack Overflow 2025). Dominante. RSC como direção oficial |
| **Vue** | reatividade fina | Vue 3 maduro, Vapor Mode reduzindo o runtime; forte na Ásia e Europa |
| **Angular** | signals + compilador | renascimento real: signals, standalone components, SSR decente. Forte em corporativo |
| **Svelte** | compilado, runes | excelente ergonomia e bundle mínimo; ecossistema menor |
| **Solid** | reatividade fina pura | o mais rápido em benchmarks; adoção de nicho, influência enorme |
| **Qwik** | resumível | tecnicamente admirável, adoção baixa; a tese está certa |
| **Astro** | ilhas | dominante para sites de conteúdo; integra qualquer framework |
| **HTMX / Hotwire** | hipermídia, HTML do servidor | nicho crescente e vocal: "e se você simplesmente não fizesse uma SPA?" |

Sobre a última linha: o movimento HTMX/Hotwire merece atenção mesmo de quem não vai adotá-lo. A crítica que ele faz — que uma fração grande de aplicações "SPA" resolveria seus requisitos com HTML do servidor e trocas parciais, com uma fração do código — está **frequentemente correta**. Vale como calibragem, mesmo que a resposta final seja outra.

---

## 4. Fronteiras técnicas ativas

Coisas de fato novas ou em movimento:

**View Transitions API.** Transições animadas entre estados e entre documentos, nativas do navegador. A versão cross-document funciona até em MPAs, dando a MPAs a suavidade que era argumento exclusivo de SPA. Chromium desde 2023; suporte se ampliando.

```js
document.startViewTransition(() => atualizarDOM());
```

**Navigation API.** Trata navegação de SPA como cidadã de primeira classe: intercepta, gerencia foco e rolagem corretamente, expõe estado de navegação. Resolve nativamente boa parte do arquivo `05`. Suporte ainda incompleto.

**Speculation Rules API.** Pré-busca e pré-renderização declarativas, controladas pelo navegador com heurísticas de custo.

**Partial Prerendering.** Casca estática do CDN + furos dinâmicos em streaming, na mesma página. A fronteira ativa da renderização.

**WebAssembly no frontend.** Nichos reais (edição de imagem, CAD, planilhas, criptografia, execução de modelos). A integração com o DOM continua sendo o atrito principal.

**IA no desenvolvimento e no produto.** Geração de código mudou o custo relativo de escrever versus manter — o que **aumenta** o valor de código simples e legível, e diminui o valor de abstrações elaboradas que economizam digitação. Nos produtos, interfaces com streaming de LLM tornaram SSE e renderização incremental habilidades comuns em vez de exóticas.

---

## 5. Como avaliar o que vem a seguir

Vale mais que qualquer lista de tecnologias, porque continua funcionando quando a lista envelhecer. Sete perguntas para qualquer coisa nova:

1. **Que problema real isto resolve?** Se você não consegue nomear a dor concreta, não é para você ainda.
2. **Qual o custo escondido?** Toda solução move complexidade; ela nunca desaparece. Onde ela foi parar?
3. **Como responde às cinco perguntas eternas?** URL, histórico, indexação, acessibilidade, tempo até útil (arquivo `03`).
4. **Qual a estratégia de saída?** Se em dois anos isso for abandonado, quanto custa sair?
5. **Quem mantém, e sob qual incentivo?** Projeto de empresa segue a estratégia da empresa. Projeto de uma pessoa segue a vida dessa pessoa.
6. **Como isso degrada?** Sob rede ruim, CPU fraca, JavaScript falho, tela pequena, leitor de tela.
7. **O benchmark corresponde ao seu caso?** Quase todo benchmark de framework mede renderização de listas grandes — que raramente é o gargalo de uma aplicação real.

---

## 6. Três previsões, explicitamente incertas

Marcadas como opinião, para que você possa cobrar depois:

**1. Signals serão padronizados no JavaScript, e isso será mais importante que qualquer framework atual.** Estado interoperável entre frameworks muda o formato do ecossistema.

**2. O modelo "escreva tudo em React e resolva depois" continuará perdendo espaço para escolhas por página.** O mesmo produto usando Astro no marketing, RSC no catálogo e SPA pura no painel deixará de ser exceção.

**3. A hidratação será lembrada como uma solução transitória.** A tese da resumabilidade está certa; a questão é quem a implementa de forma que o mercado adote. Aposto que será absorvida por um framework grande, não que o Qwik vença.

---

## 7. O que **não** mudou, e provavelmente não vai mudar

Este é o conteúdo mais durável do arquivo:

- **HTTP continua sem estado.** Toda sessão é construção sua.
- **O DOM continua caro.** Mudar menos continua sendo a otimização soberana.
- **A thread principal continua única.** Trabalho longo continua congelando a página.
- **A luz continua com a mesma velocidade.** Latência tem piso físico.
- **`UI = f(estado)` continua sendo a ideia certa** — treze anos depois, nada a substituiu.
- **As cinco perguntas eternas continuam sendo as mesmas** de 1996.
- **Simplicidade continua sendo subestimada.** A maior parte dos problemas de arquitetura que encontro em auditorias é complexidade adotada sem um problema correspondente.

Se você aprender apenas uma coisa deste curso, que seja esta última.

---

## 8. Autoteste

1. Quais cinco afirmações são consenso em 2026?
2. Por que ~45% de adoção em projetos novos e ~29% de desenvolvedores que usaram não são números contraditórios?
3. Por que signals padronizados no TC39 seriam mais impactantes que um framework novo?
4. Que crítica o movimento HTMX/Hotwire faz, e por que ela merece consideração?
5. Como a View Transitions API enfraquece um dos argumentos históricos a favor de SPA?
6. Aplique as sete perguntas da seção 5 a uma tecnologia que você esteja considerando.
7. Quais itens da seção 7 não mudaram desde 1996, e por quê?

---

**Fontes consultadas para este arquivo (agosto de 2026):**
[State of React 2025–2026](https://strapi.io/blog/state-of-react-2025-key-takeaways) ·
[Frontend trends 2026](https://www.netguru.com/blog/front-end-trends) ·
[The State of Server Components in 2026](https://www.pkgpulse.com/guides/state-of-server-components-2026) ·
[RSC in Production: Benefits, Pitfalls and Best Practices for 2026](https://www.growin.com/blog/react-server-components/) ·
[SSR Trends in 2026](https://www.sencha.com/blog/what-are-the-emerging-trends-in-server-side-rendering-for-a-javascript-framework/) ·
[What's Next for React in 2026](https://www.telerik.com/blogs/whats-next-react-2026)

---

**Anterior:** [13 — Teoria avançada](13-teoria-avancada.md) · **Próximo:** [15 — Armadilhas e mitos](15-armadilhas.md)
