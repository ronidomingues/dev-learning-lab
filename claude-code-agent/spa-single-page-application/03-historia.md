# 03 · História — por que a SPA existe

**Nível: iniciante** · Pré-requisitos: `02`.

Ninguém acordou um dia e inventou a SPA. Ela foi a resposta acumulada a uma série de frustrações concretas. Entender essa sequência é entender **quais problemas a SPA resolve de fato** — e, portanto, quando ela é a ferramenta errada.

---

## 1991–1995 · A web de documentos

Tim Berners-Lee cria a web no CERN para resolver um problema chato: físicos precisavam trocar artigos entre si com referências cruzadas. A web nasce como **um sistema de documentos interligados**, não como plataforma de aplicações. Cada página é um arquivo estático num disco.

**Isso não é trivia histórica.** É a raiz de quase tudo que dói numa SPA. O navegador, o HTTP, os buscadores, os leitores de tela — tudo foi projetado assumindo "documentos que chegam prontos". A SPA opera *contra a corrente* dessa arquitetura, e paga por isso em SEO, acessibilidade e complexidade.

---

## 1993–1998 · CGI e a página gerada

Surge o **CGI** (*Common Gateway Interface*): em vez de ler um arquivo do disco, o servidor **roda um programa** que imprime HTML. Nasce a web dinâmica. Depois vêm PHP (1995), ASP (1996), JSP (1999).

O modelo é o **MPA** — *Multi-Page Application*:

```
clique → requisição → servidor monta HTML inteiro → navegador descarta tudo e redesenha
```

Funciona bem. Ainda funciona bem hoje para muita coisa. Suas duas dores:

1. **Latência visível** a cada interação — a tela pisca, o usuário espera.
2. **Perda de contexto** — rolagem, foco, campos preenchidos, mídia tocando: tudo morre a cada clique.

---

## 1995–1999 · JavaScript e o DHTML

Brendan Eich escreve JavaScript em dez dias, na Netscape. O objetivo é modesto: validar formulários sem ida ao servidor e fazer imagens mudarem no hover.

Vem o **DHTML**, e com ele a primeira era das SPAs: navegação sem recarregar usando `<frameset>` e `<iframe>`. Um frame ficava fixo, outro trocava de conteúdo. **Conceitualmente já era uma SPA.** Na prática era um desastre: botão voltar quebrado, URLs impossíveis de compartilhar, buscadores perdidos, acessibilidade nula.

> Guarde este ponto: **os problemas centrais da SPA — histórico, URL, indexação — apareceram em 1996 e continuam sendo os mesmos em 2026.** As soluções melhoraram; os problemas não mudaram.

---

## 1999–2005 · XMLHttpRequest e o nascimento do AJAX

A Microsoft, construindo o Outlook Web Access, precisava buscar e-mails sem recarregar a página. Cria um controle ActiveX chamado `XMLHTTP` no IE5 (1999). Os outros navegadores copiam como `XMLHttpRequest`.

Isso é **a peça que faltava**: agora o JavaScript pode falar com o servidor sozinho, em segundo plano, e receber dados em vez de páginas.

Por cinco anos quase ninguém percebe a importância. Até que:

- **2004 — Gmail.** Prova que dá para fazer um cliente de e-mail completo no navegador, e que ele pode ser *melhor* que o desktop.
- **2005 — Google Maps.** Prova algo mais forte: existem interfaces **impossíveis** no modelo de páginas. Arrastar um mapa continuamente não tem equivalente em recarregamentos.
- **2005 —** Jesse James Garrett publica o ensaio *"Ajax: A New Approach to Web Applications"* e batiza a técnica. **AJAX** = *Asynchronous JavaScript and XML*. (O XML foi abandonado quase imediatamente em favor de JSON; o nome ficou.)

O setor inteiro muda de ideia em dezoito meses.

---

## 2006–2010 · jQuery e a era da manipulação direta

O problema prático: cada navegador implementava o DOM de um jeito diferente e incompatível. Escrever código que funcionasse em IE6, Firefox e Safari era tortura.

**jQuery** (John Resig, 2006) resolve isso com uma API única sobre todas as diferenças:

```js
$('#lista').load('/itens');            // busca HTML e injeta
$('.item').click(function () {         // funciona igual em todo navegador
  $(this).addClass('ativo').fadeIn();
});
```

jQuery domina absolutamente por quase uma década — no auge, mais de 70% dos sites da web. Foi uma das bibliotecas mais bem-sucedidas da história da computação.

**Mas o modelo jQuery tem um defeito estrutural, e entendê-lo explica todos os frameworks que vieram depois.**

No modelo jQuery você escreve **instruções imperativas de mudança**: "adicione a classe ativo", "remova aquele nó", "esconda isso". O estado real da aplicação passa a viver **espalhado dentro do próprio DOM** — se um item está selecionado, isso está codificado na presença de uma classe CSS.

Com 3 estados possíveis, tudo bem. Com 12 estados que interagem, você precisa acertar **cada transição entre cada par de estados**. O número de caminhos cresce quadraticamente, e um deles sempre está errado. O sintoma clássico: "quando eu clico aqui *depois* de ter filtrado ali, a tela fica num estado impossível".

Esse é o problema que a próxima geração ataca.

---

## 2010–2014 · Frameworks e a virada declarativa

Chegam **Backbone.js** (2010), **AngularJS** (2010), **Ember** (2011), **Knockout**. A ideia comum: separar **estado** de **apresentação** e deixar o framework sincronizar os dois.

AngularJS introduz o *two-way data binding* — você declara o vínculo e ele se mantém sozinho:

```html
<input ng-model="nome">
<h1>Olá, {{nome}}</h1>   <!-- atualiza sozinho ao digitar -->
```

Foi mágico e vendeu o modelo. Também foi o pior defeito do AngularJS: o mecanismo (*dirty checking*, comparar tudo com tudo a cada ciclo) não escalava, e a bidirecionalidade tornava impossível saber **quem** causou uma mudança.

**2013 — React**, do Facebook. Traz três ideias que redefinem o campo:

1. **Interface como função pura do estado.** `UI = f(estado)`. Você não descreve transições; descreve **como a tela deve ser** para um dado estado. O framework calcula a diferença.
2. **Virtual DOM.** Renderiza para uma árvore leve em memória, compara com a anterior, aplica ao DOM real só o que mudou. (Analisado em profundidade no arquivo `13`.)
3. **Fluxo de dados unidirecional.** Dados descem, eventos sobem. Sempre dá para responder "quem mudou isso?".

A primeira ideia é a que ficou. Virtual DOM já é considerado, em 2026, uma escolha de implementação discutível — Svelte e Solid provam que dá para ter renderização declarativa sem ele, e mais rápido. Mas `UI = f(estado)` venceu tão completamente que hoje parece óbvio.

**2014 — Vue**, de Evan You: modelo declarativo do React com ergonomia de template do Angular, e adoção incremental.

---

## 2015–2020 · O auge, e o excesso

O ecossistema explode: Webpack, Babel, ES Modules, npm com centenas de milhares de pacotes, TypeScript ganhando tração, React Native levando o modelo para mobile.

E acontece o erro coletivo:

> **SPA vira o padrão para tudo.** Blogs, páginas institucionais, portais de notícia, documentação — coisas que são literalmente documentos — passam a ser construídas como aplicações.

O resultado, mensurável e documentado:

- Bundles de 2 a 5 MB de JavaScript para exibir texto.
- Telas brancas de vários segundos em 3G e celulares baratos — a realidade da maior parte do mundo.
- SEO quebrado, exigindo gambiarras de pré-renderização.
- Acessibilidade destruída pelo `<div onclick>`.
- Complexidade de build que consumia semanas de engenharia por projeto.

O Google reage criando as **Core Web Vitals** (2020) e as tornando fator de ranqueamento — uma resposta institucional direta à web ficar lenta demais. O arquivo `09` cobre essas métricas.

---

## 2016–2022 · O pêndulo volta: SSR e o híbrido

A saída não foi abandonar a SPA. Foi **juntar as duas coisas**.

**Next.js** (Vercel, 2016) populariza o modelo que domina até hoje:

1. O servidor renderiza o React em HTML e manda **a tela já pronta**. Rápida de ver, indexável, funciona sem JS.
2. O navegador recebe esse HTML, mostra imediatamente, baixa o JavaScript e o "acopla" ao HTML existente — a **hidratação** (*hydration*).
3. A partir daí, é uma SPA: navegação instantânea, nada pisca.

Aparecem Nuxt (Vue), SvelteKit, Remix, Angular Universal. Surgem também variações que atacam o custo da hidratação:

- **SSG** — gera o HTML no build, não a cada requisição.
- **ISR** — regenera páginas estáticas sob demanda, em background.
- **Arquitetura de ilhas** (Astro, 2021) — a página é HTML estático e **só os pedaços interativos** recebem JavaScript. Para sites de conteúdo, corta 90%+ do JS.
- **Resumabilidade** (Qwik, 2022) — elimina a hidratação: o estado do servidor é serializado no HTML e a execução *continua* no cliente em vez de recomeçar.

---

## 2023–2026 · Servidor-primeiro e reatividade fina

Duas correntes independentes, ambas maduras hoje:

**Corrente 1 — mover trabalho de volta para o servidor.**
Os **React Server Components** (RSC) permitem que componentes rodem **exclusivamente no servidor**: seu código nunca vai para o navegador, mas eles podem acessar banco de dados diretamente e compor com componentes de cliente. Estabilizados no React 19, são o padrão do Next.js 15 e, em 2026, a recomendação oficial para aplicações novas de porte. Adoção real: **cerca de 45% dos projetos novos**, com **~29% dos desenvolvedores** tendo usado — ou seja, consolidado no topo do mercado, ainda longe de universal.

**Corrente 2 — trocar o Virtual DOM por reatividade fina.**
**Signals**: valores que sabem quem depende deles. Quando mudam, atualizam **exatamente** os nós do DOM afetados — sem re-renderizar componente nenhum, sem diffing de árvore. SolidJS provou o modelo, Svelte 5 o adotou nas *runes*, Angular o incorporou como API central, Vue sempre teve algo próximo. Em 2026 há convergência clara do campo nessa direção.

E uma terceira, transversal: **compiladores**. O React Compiler (estável no React 19) infere memoização automaticamente, tornando `useMemo` e `useCallback` manuais em grande parte desnecessários. A tendência geral é **mover trabalho do runtime para o tempo de build**.

---

## Linha do tempo condensada

```
1991  Web de documentos
1993  CGI — HTML gerado dinamicamente
1995  JavaScript (10 dias) · PHP
1996  Frames/iframes — a proto-SPA, com todos os problemas atuais
1999  XMLHttpRequest (IE5)
2004  Gmail — a prova de conceito
2005  Google Maps · ensaio "AJAX" · JSON substitui XML
2006  jQuery — a era imperativa
2008  History API — URLs reais sem recarregar
2010  Backbone · AngularJS
2013  React — UI = f(estado), Virtual DOM
2014  Vue
2015  Redux · Webpack · a era do "SPA para tudo"
2016  Next.js — SSR + hidratação vira mainstream
2019  Svelte 3 — compilador, sem VDOM
2020  Core Web Vitals — o Google reage à web lenta
2021  Astro — arquitetura de ilhas · Vite substitui Webpack
2022  Qwik — resumabilidade · SolidJS populariza signals
2023  RSC em produção (Next.js App Router)
2024  React 19 · Svelte 5 runes · signals no Angular
2026  Híbrido é consenso · RSC ~45% dos projetos novos · signals convergindo
```

---

## As cinco lições que a história ensina

1. **Cada geração resolveu a dor da anterior e criou uma nova.** Frames resolveram recarregamento e quebraram histórico. jQuery resolveu incompatibilidade e criou estado espalhado. React resolveu isso e criou peso de bundle. RSC resolve peso e cria complexidade de fronteira cliente/servidor. Não existe estado final.

2. **Os problemas fundamentais não mudaram desde 1996.** Histórico, URL, indexação, acessibilidade, tempo até a tela útil. Toda arquitetura nova precisa responder às mesmas cinco perguntas.

3. **A adoção sempre ultrapassa a adequação.** SPA foi aplicada onde não cabia por cinco anos. É razoável esperar que RSC esteja passando pelo mesmo agora — **esta é opinião profissional, não consenso**.

4. **A tendência de longo prazo é mover trabalho para longe do runtime do cliente** — para o build (compiladores), para o servidor (RSC, SSR), para a borda (edge). O JavaScript no dispositivo do usuário é o recurso mais caro e menos previsível da pilha.

5. **`UI = f(estado)` foi a única ideia que sobreviveu intacta.** Tudo mais — VDOM, hooks, bundlers, até a hidratação — foi substituído ou está sendo. A ideia declarativa não.

---

## Autoteste

1. Que problema concreto o Google Maps demonstrou ser **impossível** no modelo de páginas?
2. Por que o modelo do jQuery quebra conforme o número de estados cresce?
3. Qual das três ideias do React sobreviveu, e quais estão sendo abandonadas?
4. Por que a hidratação existe, e por que Qwik a considera um erro?
5. Se a tendência é mover trabalho para o servidor, o que sobra de motivo para a SPA existir? (Resposta no arquivo `07`.)

---

**Anterior:** [02 — Fundamentos da web](02-fundamentos-web.md) · **Próximo:** [04 — Anatomia de uma SPA](04-anatomia.md)
