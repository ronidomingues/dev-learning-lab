# SPA — Single Page Application · Mapa do Curso

**Assunto:** aplicações de página única (SPA) — o que são, como funcionam por dentro, quando usar, quando não usar, e o que substituiu boa parte delas.
**Última revisão:** agosto de 2026.

---

## Para quem é este material

Três leitores ao mesmo tempo:

- Quem **nunca ouviu falar** de SPA e quer entender do que se trata → leia `01` e pare quando estiver satisfeito.
- Quem **constrói interfaces web** e quer entender a máquina por baixo → leia do `02` ao `12`.
- Quem quer **profundidade de pesquisa** — algoritmos de reconciliação, modelos de reatividade, limites teóricos → leia `13` e `14`.

---

## Pré-requisitos

| Para ler... | Você precisa saber... |
|---|---|
| `01` | nada |
| `02`–`03` | nada (o arquivo constrói o vocabulário) |
| `04`–`08` | JavaScript básico (variáveis, funções, objetos, async) |
| `09`–`12` | o acima + noção de HTTP e linha de comando |
| `13`–`14` | o acima + estruturas de dados (árvores, grafos) e complexidade assintótica |

Se faltar JavaScript, o `02` cobre o mínimo indispensável — mas não substitui aprender a linguagem.

---

## Roteiro de leitura

| # | Arquivo | Nível | O que você ganha |
|---|---|---|---|
| 00 | *este arquivo* | — | orientação |
| 01 | [Introdução para leigos](01-introducao-leigo.md) | iniciante | entender o que é uma SPA sem nenhum jargão |
| 02 | [Fundamentos da web](02-fundamentos-web.md) | iniciante | HTTP, HTML, DOM, JavaScript, event loop — o chão onde tudo pisa |
| 03 | [História](03-historia.md) | iniciante | de 1991 a 2026: por que a SPA surgiu, reinou e foi parcialmente destronada |
| 04 | [Anatomia de uma SPA](04-anatomia.md) | intermediário | o que acontece do primeiro byte até a tela pintada |
| 05 | [Roteamento no cliente](05-roteamento.md) | intermediário | History API, rotas aninhadas, code splitting por rota |
| 06 | [Gerenciamento de estado](06-estado.md) | intermediário | estado local, global, de servidor, de URL — e como não se afogar |
| 07 | [Estratégias de renderização](07-renderizacao.md) | intermediário/avançado | CSR, SSR, SSG, ISR, hidratação, ilhas, streaming, RSC |
| 08 | [Dados e rede](08-dados-e-rede.md) | intermediário/avançado | REST, GraphQL, cache, waterfalls, otimismo, tempo real |
| 09 | [Performance](09-performance.md) | avançado | Core Web Vitals, orçamento de bundle, LCP/INP/CLS, medição real |
| 10 | [SEO e acessibilidade](10-seo-acessibilidade.md) | avançado | como SPAs quebram buscadores e leitores de tela — e como consertar |
| 11 | [Segurança](11-seguranca.md) | avançado | XSS, CSRF, onde guardar token, CSP, OAuth/PKCE |
| 12 | [Build, deploy e infraestrutura](12-build-deploy-infra.md) | avançado | bundlers, CDN, edge, cache busting, versionamento de assets |
| 13 | [Teoria avançada](13-teoria-avancada.md) | pesquisa | VDOM e reconciliação, reatividade fina, compiladores, complexidade |
| 14 | [Estado da arte 2026](14-estado-da-arte.md) | pesquisa | o que é consenso hoje, o que está em disputa, o que vem a seguir |
| 15 | [Armadilhas e mitos](15-armadilhas.md) | todos | erros clássicos, folclore que persiste e por quê |
| 16 | [Prática](16-pratica.md) | todos | laboratórios com as mãos, do "SPA em 40 linhas" ao app completo |
| 17 | [Referências](17-referencias.md) | todos | livros, specs, papers, docs, pessoas |
| — | [Glossário](GLOSSARIO.md) | todos | todo termo técnico deste curso, definido |

---

## O que você vai saber ao final

1. Explicar para qualquer pessoa o que é uma SPA e por que ela existe.
2. Descrever, passo a passo e sem caixas-pretas, o que acontece entre digitar a URL e a tela ficar utilizável.
3. Implementar um roteador client-side, um sistema de reatividade e um cache de dados **do zero**, sem framework.
4. Escolher com fundamento entre SPA, MPA, SSR, SSG e arquiteturas híbridas para um projeto real — e defender a escolha.
5. Diagnosticar e corrigir problemas de performance, SEO, acessibilidade e segurança específicos de SPAs.
6. Entender como React, Vue, Svelte, Solid e Angular resolvem o mesmo problema por caminhos diferentes, e o custo de cada caminho.
7. Ler a literatura atual do campo e acompanhar para onde ele está indo.

---

## Aviso de honestidade intelectual

Este curso **não** vende SPA como resposta universal. Entre 2013 e 2020 o setor tratou SPA como padrão-ouro para tudo, o que produziu uma geração de sites lentos, inacessíveis e desnecessariamente complexos. A posição defendida aqui, e argumentada com evidência nos arquivos `07`, `09` e `14`:

> **SPA é uma técnica excelente para um subconjunto real de problemas — aplicações com sessão longa, estado rico no cliente e interação intensa. Aplicada fora desse subconjunto, ela cobra caro e entrega pouco.**

Onde isso for opinião profissional e não consenso do campo, está marcado no texto.
