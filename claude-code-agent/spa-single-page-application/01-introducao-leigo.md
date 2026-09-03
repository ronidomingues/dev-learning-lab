# 01 · Introdução para leigos

**Nível: iniciante** · Pré-requisitos: nenhum.

---

## 1. A analogia do restaurante

Imagine dois restaurantes que servem exatamente a mesma comida.

**Restaurante A — o clássico.**
Você senta. Pede a entrada. O garçom vai à cozinha, e a cozinha monta **uma bandeja completa**: entrada, prato, talheres, toalha de mesa, decoração, tudo. Traz a bandeja inteira e monta sua mesa do zero na sua frente.
Aí você pede o prato principal. O garçom **desmonta toda a mesa**, leva embora, volta à cozinha, e traz **outra bandeja completa** — com toalha nova, decoração nova, talheres novos, e o prato principal. Tudo é remontado do zero.
Você pede a sobremesa. Mesma coisa: mesa desmontada, bandeja nova, tudo remontado.

**Restaurante B — o moderno.**
Você senta. Na primeira vez, o garçom traz **a mesa montada inteira e mais um carrinho de apoio** ao seu lado, com utensílios, molhos, guardanapos e um cardápio interativo. Isso demora um pouco mais que no restaurante A.
Mas a partir daí: você pede o prato principal, e o garçom traz **só o prato**. A toalha continua ali. A decoração continua ali. Sua taça de vinho pela metade continua exatamente onde estava.
Sobremesa? Só a sobremesa chega. Nada é desmontado.

O Restaurante A é um **site tradicional** (o nome técnico é *Multi-Page Application*, MPA).
O Restaurante B é uma **SPA** — *Single Page Application*, ou "aplicação de página única".

A troca é essa, e o resto deste curso é detalhar suas consequências:
**a SPA paga mais caro na primeira visita para pagar quase nada em todas as visitas seguintes.**

---

## 2. O que "página" significa aqui

Quando você usa a internet, seu navegador (Chrome, Firefox, Safari) faz basicamente uma coisa: pede documentos a computadores distantes e os desenha na tela.

Cada documento desses é uma **página**. Ela chega escrita numa linguagem chamada HTML, que descreve conteúdo e estrutura: "isto é um título", "isto é um parágrafo", "isto é um botão".

Num site tradicional, **cada clique num link busca um documento novo**. Você vê isso acontecer: a tela pisca em branco, o indicador de carregamento gira, a página inteira é substituída. Sua barra de rolagem volta ao topo. Se você tinha um vídeo tocando, ele morre.

Numa SPA, o navegador carrega **uma única página HTML, uma vez só, e nunca mais a substitui**. Todo o resto — abrir um e-mail, trocar de aba, filtrar uma lista — é feito por um programa em JavaScript que já está rodando dentro dessa página e que **reescreve pedaços da tela** conforme necessário.

Daí o nome: uma única página, para a vida toda da sua sessão.

---

## 3. Você já usa SPAs o dia inteiro

Alguns exemplos que quase certamente você conhece:

| Aplicação | O que denuncia que é uma SPA |
|---|---|
| **Gmail** | você abre um e-mail e a lista lateral não recarrega; a tela nunca pisca |
| **Google Maps** | você arrasta o mapa e ele se move continuamente, sem recarregar nada |
| **Trello / Notion** | você arrasta um cartão e ele se move na hora, sem esperar o servidor |
| **Spotify Web** | você navega entre artistas e **a música não para** — isso é o sinal mais claro de todos |
| **Figma** | edição colaborativa em tempo real, impossível em recarregamentos de página |

E exemplos de sites que tipicamente **não** são SPAs (ou não deveriam ser):

- Um blog. Um portal de notícias. Uma página de documentação. A Wikipédia.
- Uma loja virtual na parte de catálogo e produto (o carrinho e o checkout são outra conversa).

Note o padrão. **SPAs brilham onde você fica muito tempo dentro e interage muito.** Sites de conteúdo, onde você chega pelo Google, lê e vai embora, ganham pouco e perdem bastante.

---

## 4. O truque central, sem jargão

Como a SPA troca a tela sem trocar a página?

Três peças:

**Peça 1 — o programa fica.**
Junto com a página inicial, chega um programa em JavaScript. Ele não morre entre uma tela e outra, porque a página nunca é substituída. Ele fica vivo, guardando na memória quem você é, o que você já carregou, onde você estava.

**Peça 2 — ele pede só os dados, não a página.**
Quando você clica em "abrir e-mail", o programa não pede ao servidor uma página nova. Ele pede **só o conteúdo daquele e-mail** — o texto puro, sem toalha de mesa nem decoração. Isso é muitas vezes menor e chega muito mais rápido.

**Peça 3 — ele redesenha só o que mudou.**
Com o dado em mãos, o programa reescreve **apenas a região da tela** que precisa mudar. O menu lateral, o cabeçalho, sua rolagem, seu vídeo tocando — nada disso é tocado.

Uma quarta peça, menos óbvia mas essencial:

**Peça 4 — ele mente para a barra de endereços (do jeito certo).**
Se a página nunca muda, por que a URL muda quando você navega? Porque o navegador oferece uma ferramenta (a *History API*) que permite ao programa **alterar a URL exibida e o histórico de navegação sem buscar nada**. É isso que faz o botão "voltar" funcionar e que permite copiar o link de uma tela específica. Uma SPA que não faz isso direito é uma SPA quebrada — e isso é comum. Voltaremos a esse ponto várias vezes.

---

## 5. O preço

Nada disso é de graça. Os quatro custos principais, em linguagem simples:

**Custo 1 — a primeira visita é mais lenta.**
Antes de você ver qualquer coisa útil, o navegador precisa baixar o programa inteiro, executá-lo, deixá-lo pedir os dados e só então desenhar. No modelo tradicional, o servidor manda a tela já pronta. É a diferença entre receber um móvel montado e receber uma caixa da IKEA com as ferramentas.

**Custo 2 — sem JavaScript, não há nada.**
Se o JavaScript falhar — conexão ruim, um erro no código, um bloqueador agressivo, um navegador antigo — o usuário fica olhando uma tela branca. No site tradicional, o HTML já é o conteúdo; ele funciona mesmo se todo o resto quebrar.

**Custo 3 — buscadores e leitores de tela sofrem.**
O Google e as tecnologias assistivas foram construídos assumindo que o conteúdo está no HTML. Quando o conteúdo só existe depois que um programa roda, ambos precisam de trabalho extra para funcionar — e às vezes não funcionam. Detalhado no arquivo `10`.

**Custo 4 — você reconstrói o navegador dentro do navegador.**
Navegação, histórico, botão voltar, título da aba, rolagem, tratamento de erro, indicador de carregamento: o navegador já faz tudo isso de graça, há trinta anos, muito bem. Numa SPA, **você passa a ser responsável por reimplementar cada uma dessas coisas** — e por mantê-las corretas para sempre. Este é o custo mais subestimado da carreira de muita gente.

---

## 6. Onde estamos em 2026

A discussão amadureceu. Por volta de 2015–2020, "fazer SPA" virou padrão para praticamente qualquer site, inclusive blogs — o que foi um erro coletivo caro. Desde então o pêndulo voltou, e o consenso atual não é "SPA sim" nem "SPA não", mas **híbrido**:

> O servidor manda a primeira tela **já pronta** (rápida de ver, funciona sem JavaScript, buscadores leem).
> Depois, o programa assume no cliente e dali em diante a experiência é de SPA (nada pisca, tudo é instantâneo).

Você ganha os dois lados. É o que fazem, hoje, praticamente todas as ferramentas modernas — Next.js, Nuxt, SvelteKit, Remix, Angular SSR. O arquivo `07` disseca exatamente como isso funciona, e o `14` mapeia onde o campo está agora.

---

## 7. Autoteste

Se você consegue responder isto, o arquivo cumpriu seu papel:

1. Por que a música não para quando você navega no Spotify Web?
2. Por que a primeira abertura do Gmail demora mais que a abertura de um blog?
3. Por que um blog pessoal provavelmente **não** deveria ser uma SPA?
4. Se a página nunca é substituída, por que a URL muda?
5. O que acontece com uma SPA se o JavaScript não carregar?

---

**Próximo:** [02 — Fundamentos da web](02-fundamentos-web.md) · monta o vocabulário técnico real (HTTP, DOM, event loop) que todo o resto do curso usa.
