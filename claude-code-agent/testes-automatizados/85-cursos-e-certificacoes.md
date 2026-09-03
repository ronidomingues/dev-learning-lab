# 85 · Cursos gratuitos e certificações

`Nível: todos` · `Pesquisado na web em 13/08/2026`

> **Links expiram e cursos mudam.** Tudo aqui foi encontrado por busca em 13/08/2026. Onde
> não consegui confirmar autor, duração ou ano, digo isso explicitamente em vez de inventar.
> Confira antes de investir tempo.

---

## Como usar este arquivo

1. **Você já sabe programar e quer aprender a testar?** Comece pela seção 1 (português) ou 2
   (inglês) e pule as certificações.
2. **Você quer trabalhar como QA?** Leia a seção 5 antes de gastar dinheiro com certificação
   — a franqueza sobre o valor de mercado está lá.
3. **Você quer o caminho mais curto?** Este material + o
   [projeto-modelo](07-projeto-modelo/README.md) + os
   [12 laboratórios](70-pratica.md) cobrem mais chão do que a maioria dos cursos pagos.

---

## 1. Português — Brasil e Portugal

### 1.1 Gratuitos de verdade

| Curso | Autor / plataforma | Link | Formato | Nível | Vale? |
|---|---|---|---|---|---|
| **Live de Python — Testes com Python (uma introdução geral)** | Eduardo Mendes (*dunossauro*) · YouTube | [youtube.com/watch?v=5hL9T3jintE](https://www.youtube.com/watch?v=5hL9T3jintE) | live longa | iniciante–intermediário | **Sim.** Eduardo é referência na comunidade Python brasileira; formato de live, denso, sem edição. Bom para ver alguém pensando em voz alta. |
| **Curso de Selenium com Python** | Eduardo Mendes (*dunossauro*) | [dunossauro.github.io/curso-python-selenium](https://dunossauro.github.io/curso-python-selenium/) | site + vídeos + repositório | intermediário | **Sim, com ressalva.** Totalmente grátis, licença aberta, e emite certificado. Ressalva: Selenium é a escolha de ontem para web nova — hoje se usaria Playwright. O conteúdo sobre *como pensar* automação de navegador continua válido. |
| **Testes automatizados com Pytest — o guia introdutório** | Canal *PIP* · YouTube | [youtube.com/watch?v=uVM9vPu2z0g](https://www.youtube.com/watch?v=uVM9vPu2z0g) | vídeo único | iniciante | Sim, para o primeiro contato. Não substitui prática. |
| **Testes automatizados no Next.js com Vitest e Playwright** | Otávio Miranda | [lista de cursos gratuitos do autor](https://gist.github.com/luizomf/289f1aa3d957ac03a238bd8f8c7054af) | série no YouTube | intermediário | **Sim**, e é dos poucos materiais em português que usa **Vitest e Playwright** — a pilha atual, não a de 2018. |
| **Curso COMPLETO de QA — do manual básico até automatizador** | playlist no YouTube | [playlist](https://www.youtube.com/playlist?list=PLFqZckg9_2x0JqYfTvVCd5QNoDm4xFRHF) | playlist longa | iniciante | Serve como panorama de carreira QA. *Não consegui confirmar autor e número de vídeos na consulta.* |
| **Curso Analista de Testes — QA** | playlist no YouTube | [playlist](https://www.youtube.com/playlist?list=PLQ3tGxEilbe4xOBBhnBr7-TQgp4U0Js9D) | playlist | iniciante | Panorama de teste manual e processo. *Autor não confirmado.* |
| **Curso de Testes de Software para iniciantes — CTFL** | playlist no YouTube | [playlist](https://www.youtube.com/playlist?list=PLx6gdu4s3nkf4OcLZ--TgMCHr22H7TDCs) | playlist | iniciante | Útil **se** o seu objetivo for a prova do CTFL. Para escrever testes de verdade, não é o caminho. |

### 1.2 Documentação oficial em português

| Recurso | Link | Observação |
|---|---|---|
| **Python — tutorial oficial (pt-BR)** | [docs.python.org/pt-br/3/tutorial](https://docs.python.org/pt-br/3/tutorial/) | tradução oficial, boa qualidade |
| **MDN Web Docs (pt-BR)** | [developer.mozilla.org/pt-BR](https://developer.mozilla.org/pt-BR/) | tradução parcial; o conteúdo de JS é bom |
| **Documentação do pytest** | [docs.pytest.org](https://docs.pytest.org/) | **só em inglês** |
| **Documentação do Playwright** | [playwright.dev](https://playwright.dev/) | **só em inglês** |

> **Realidade que vale dizer:** a documentação central do campo — pytest, Vitest, Playwright,
> Node — **não tem tradução para português**. Ler inglês técnico não é opcional para chegar a
> nível autônomo. Comece pelos vídeos em português e migre para a documentação em inglês o
> quanto antes; o vocabulário é pequeno e repetitivo.

### 1.3 Pagos que aparecem sempre (para você saber o que está avaliando)

| Curso | Plataforma | Observação honesta |
|---|---|---|
| **Domine Pytest: Testes de Software com Python** | [Udemy](https://www.udemy.com/course/domine-pytest/) | conteúdo razoável; a Udemy vive em promoção — nunca pague o preço cheio |
| **Alura — Testes automatizados / TDD com Python** | Alura (assinatura) | boa didática, trilha estruturada; assinatura mensal |
| **Formação em Teste de Software (~120 h)** | [Iterasys](https://iterasys.com.br/pt/formacao-em-teste-de-software) | voltada a carreira QA: PyTest, Postman, Robot Framework, Selenium, Appium; pago |

**Opinião:** nenhum desses ensina o que o [capítulo 20](20-testabilidade-e-design.md) ensina —
como tornar testável um código que não é. Essa é a lacuna sistemática dos cursos de teste em
português, e é onde a maioria das pessoas trava.

---

## 2. Inglês

### 2.1 Gratuitos, e bons

| Recurso | Autor / plataforma | Link | Por que vale |
|---|---|---|---|
| **Test Automation University** | Applitools | [testautomationu.applitools.com](https://testautomationu.applitools.com/) | **A melhor coisa gratuita do campo.** Dezenas de cursos com instrutores reconhecidos, laboratórios práticos, trilhas por ferramenta (Playwright, Cypress, Python, Java). Dá *badges*, créditos e certificado por curso — **não** por trilha. Financiado pela Applitools, que vende ferramenta de teste visual: espere alguma promoção do produto deles. |
| **Documentação do pytest** | pytest-dev | [docs.pytest.org](https://docs.pytest.org/) | densa e completa; a seção "How-to guides" é subutilizada |
| **Documentação do Playwright** | Microsoft | [playwright.dev/docs/intro](https://playwright.dev/docs/intro) | uma das melhores documentações de ferramenta que existem hoje |
| **Documentação do Vitest** | equipe Vitest | [vitest.dev/guide](https://vitest.dev/guide/) | clara, com exemplos executáveis |
| **Node.js — Test runner** | Node.js | [nodejs.org/api/test.html](https://nodejs.org/api/test.html) | referência da API; leia junto com [learn/test-runner](https://nodejs.org/learn/test-runner/collecting-code-coverage) |
| **Testing Library — Guiding Principles** | Kent C. Dodds e comunidade | [testing-library.com](https://testing-library.com/docs/guiding-principles/) | são 3 parágrafos que mudam como você testa interface |
| **Google Testing Blog** | Google | [testing.googleblog.com](https://testing.googleblog.com/) | arquivo com quase 20 anos; a série "Testing on the Toilet" é ouro em pílulas |
| **Martin Fowler — artigos sobre teste** | martinfowler.com | [martinfowler.com/testing](https://martinfowler.com/testing/) | *Mocks Aren't Stubs*, *Test Pyramid*, *Eradicating Non-Determinism in Tests* |

### 2.2 Universidades abertas

| Curso | Instituição | Observação |
|---|---|---|
| **Software Testing and Automation** (especialização) | University of Minnesota, via Coursera | grátis para assistir (*audit*); certificado pago |
| **Introduction to Software Testing** | via Coursera / edX (várias ofertas) | idem — o modelo "grátis para assistir, pago para certificar" é a regra em MOOC |
| **CS50** | Harvard, via edX | não é de testes, mas a seção sobre depuração e ferramentas é boa base |

> **Distinção que importa:** MOOC "gratuito" quase sempre significa **grátis para assistir,
> pago para certificar**. Class Central ([classcentral.com](https://www.classcentral.com/))
> é o melhor agregador para filtrar por "free" de verdade.

---

## 3. Francês

| Curso | Plataforma | Link | Observação |
|---|---|---|---|
| **Testez votre projet Python** | OpenClassrooms | [openclassrooms.com/fr/courses/7155841](https://openclassrooms.com/fr/courses/7155841-testez-votre-projet-python) | Cobre `unittest`, **pytest** e **TDD**. Acesso gratuito ao conteúdo (vídeos, quizzes, capítulos) com conta; o certificado é do plano pago. Bem estruturado. |
| **Testez vos applications front-end avec JavaScript** | OpenClassrooms | [openclassrooms.com/fr/courses/7159306](https://openclassrooms.com/us/courses/7159306-testez-vos-applications-front-end-avec-javascript) | **Jest**, testes unitários, e um capítulo de **end-to-end**. |
| **Initiez-vous au test et à la qualité logicielle** | OpenClassrooms | [openclassrooms.com/fr/courses/7365096](https://openclassrooms.com/us/courses/7365096-initiez-vous-au-test-et-a-la-qualite-logicielle) | Panorama de qualidade e do papel do testador; teste funcional e exploratório. Bom complemento não técnico. |
| **Testez votre code Java** | OpenClassrooms | [openclassrooms.com/en/courses/6100311](https://openclassrooms.com/en/courses/6100311-testez-votre-code-java-pour-realiser-des-applications-de-qualite) | Unitário, integração, ponta a ponta e TDD, em Java. |

**Avaliação:** o OpenClassrooms é, de longe, o melhor material gratuito estruturado em francês
sobre o assunto — e a trilha Python cobre exatamente o que este curso cobre no Bloco A. Se
você lê francês, é uma alternativa legítima ao material em inglês.

---

## 4. Canais e fontes que se mantêm

| Fonte | Idioma | O que é |
|---|---|---|
| **Google Testing Blog** | EN | prática de engenharia em escala |
| **martinfowler.com** | EN | os artigos conceituais de referência |
| **Test Automation University** | EN | cursos em vídeo, gratuitos |
| **dunossauro (Eduardo Mendes)** | PT-BR | lives longas de Python, incluindo testes |
| **Otávio Miranda** | PT-BR | cursos gratuitos, pilha atual (Vitest, Playwright) |
| **OpenClassrooms** | FR | trilhas estruturadas |
| **Class Central** | EN | agregador para achar o que é realmente gratuito |

---

## 5. Certificações — e a conversa franca sobre elas

### 5.1 ISTQB / BSTQB — Certified Tester Foundation Level (CTFL)

**O que é.** A certificação de teste mais reconhecida do mundo. No Brasil, o board é o
**BSTQB**; em Portugal, o **PSTQB**. Baseada no **syllabus 4.0**.

**Formato** (confirmado na página oficial do BSTQB em 13/08/2026):

| Item | Valor |
|---|---|
| questões | 40, múltipla escolha |
| pontuação | 1 ponto por questão, 40 no total |
| aprovação | **26 pontos (65 %)** |
| duração | 60 min (+25 % para quem não é falante nativo do idioma da prova) |
| idioma | disponível em português |

**Preço.** Não consegui confirmar o valor oficial vigente na página do BSTQB — ela remete a
uma loja sem preço exposto. Relatos de candidatos e páginas de parceiros em 2026 mencionam
valores da ordem de **R$ 680** para o exame nacional, e cerca de **US$ 95 + câmbio** em
algumas modalidades por parceiro. **Trate isso como ordem de grandeza, não como preço** —
confirme em [bstqb.online](https://bstqb.online/ctfl) ou pelo contato oficial do board.

**Vale a pena?** Depende inteiramente do seu objetivo, e aqui vai a resposta franca:

| Se você quer... | Vale? |
|---|---|
| **passar em filtro de RH** para vaga de QA, principalmente em consultoria e empresa grande | **Sim.** É frequentemente exigida, e é o motivo real de a maioria das pessoas fazer. |
| trabalhar em **empresa europeia** ou em consultoria internacional | Sim — a exigência é mais comum lá. |
| **aprender a escrever testes automatizados** | **Não.** O syllabus é sobre **processo, terminologia e gestão de teste**, não sobre escrever código de teste. Você pode passar no CTFL sem nunca ter escrito um `assert`. |
| ser contratado como **desenvolvedor** | Não. Praticamente nenhum processo seletivo de desenvolvimento pede. |

**Opinião profissional, declarada como opinião:** o CTFL é um certificado de **vocabulário e
processo**. Ele tem valor de mercado real como credencial de entrada em QA no Brasil, e valor
técnico baixo para quem já programa. Se o seu objetivo é escrever bons testes, o dinheiro do
exame rende mais em um livro ([90-bibliografia.md](90-bibliografia.md)) e o tempo rende mais
nos [laboratórios](70-pratica.md).

**Níveis acima:** Advanced (Test Analyst, Test Manager, Technical Test Analyst) e Expert.
Custam mais, exigem o Foundation, e são procurados sobretudo por quem segue carreira de
gestão de qualidade.

**Preparação gratuita:** o **syllabus oficial e o glossário do ISTQB são gratuitos** e são a
fonte definitiva da prova. Baixe-os antes de comprar qualquer curso preparatório. As
playlists de CTFL da seção 1.1 cobrem o mesmo conteúdo.

### 5.2 Certificações de ferramenta

| Certificação | Emissor | Custo | Valor de mercado |
|---|---|---|---|
| **Test Automation University** (por curso) | Applitools | grátis | baixo como credencial; **alto como aprendizado** |
| certificações de fornecedor (Cypress, Katalon, Tricentis, etc.) | os próprios fornecedores | varia | reconhecidas só dentro do ecossistema daquela ferramenta |
| **Certificados de MOOC** (Coursera, edX) | universidade parceira | pago | baixo isoladamente; útil compondo um perfil |

### 5.3 O que realmente vale como credencial

Ordem observada de peso em processo seletivo técnico, do maior para o menor:

1. **Um repositório público com uma suíte de testes que você escreveu** — de preferência com
   CI verde, cobertura visível e testes que demonstram julgamento (fronteiras, dublês,
   contrato). Isso conversa por si.
2. **Contribuição a projeto aberto**, especialmente corrigindo um bug **com o teste que o
   reproduz**.
3. **Saber explicar trade-offs numa entrevista** — por que mock aqui e fake ali, por que
   este teste é de integração, por que a cobertura daquele módulo é 60 % de propósito.
4. Certificação.

Se você fizer os [12 laboratórios](70-pratica.md) e publicar o resultado, você produz o item
1 — que é o que mais pesa.

---

## 6. Trilha sugerida, do zero ao autônomo, gastando R$ 0

| Etapa | O que fazer | Tempo |
|---|---|---|
| 1 | [01](01-introducao-leigo.md) → [04](04-como-comecar.md) deste material | 2 h |
| 2 | Live de Python sobre testes (dunossauro) **ou** OpenClassrooms "Testez votre projet Python" | 4 h |
| 3 | [06-exemplos.md](06-exemplos.md) — reproduza os 12 exemplos na sua máquina | 6 h |
| 4 | [10](10-fundamentos.md), [12](12-tipos-e-piramide.md), [13](13-teste-unitario-a-fundo.md), [14](14-dubles-de-teste.md) | 6 h |
| 5 | Laboratórios 1 a 7 de [70-pratica.md](70-pratica.md) | 15 h |
| 6 | Test Automation University — 2 cursos da trilha da sua ferramenta | 8 h |
| 7 | [20-testabilidade-e-design.md](20-testabilidade-e-design.md) + **Lab 8** | 6 h |
| 8 | Rode e leia o [projeto-modelo](07-projeto-modelo/README.md) inteiro; faça os exercícios do README | 8 h |
| 9 | [19](19-cobertura-e-metricas.md) + Labs 9 a 12 | 10 h |
| 10 | Aplique num projeto seu, com CI ([21](21-ci-e-automacao.md)) | contínuo |

**Total ≈ 65 horas** até o nível autônomo, sem gastar nada.

---

## Autoteste

1. Qual é o melhor recurso gratuito em inglês, e qual é o conflito de interesse dele?
2. Por que a trilha do OpenClassrooms é a melhor opção gratuita em francês?
3. Por que ler inglês técnico não é opcional neste campo?
4. O que o CTFL certifica de fato, e o que ele **não** certifica?
5. Você quer aprender a escrever testes automatizados. O CTFL é o caminho? Justifique.
6. Qual é o material oficial gratuito para preparar o CTFL?
7. Qual credencial pesa mais que uma certificação num processo técnico, e por quê?
8. O que "curso gratuito" costuma significar em MOOC, e como filtrar?
9. Qual é a lacuna sistemática dos cursos de teste em português?

---

## Fontes consultadas (13/08/2026)

- [Test Automation University — Applitools](https://testautomationu.applitools.com/) · [Certificate](https://testautomationu.applitools.com/certificate/) · [Learning Paths](https://testautomationu.applitools.com/learningpaths.html)
- [70+ Test Automation University Courses — Class Central](https://www.classcentral.com/provider/tau)
- [Curso de Selenium com Python — Eduardo Mendes](https://dunossauro.github.io/curso-python-selenium/) · [Certificado](https://dunossauro.github.io/curso-python-selenium/certificado.html)
- [Live de Python #1 — Testes com Python](https://www.youtube.com/watch?v=5hL9T3jintE)
- [Cursos gratuitos de Otávio Miranda (lista)](https://gist.github.com/luizomf/289f1aa3d957ac03a238bd8f8c7054af)
- [Testes automatizados com Pytest — canal PIP](https://www.youtube.com/watch?v=uVM9vPu2z0g)
- [OpenClassrooms — Testez votre projet Python](https://openclassrooms.com/fr/courses/7155841-testez-votre-projet-python) · [Front-end avec JavaScript](https://openclassrooms.com/us/courses/7159306-testez-vos-applications-front-end-avec-javascript) · [Initiez-vous au test et à la qualité logicielle](https://openclassrooms.com/us/courses/7365096-initiez-vous-au-test-et-a-la-qualite-logicielle)
- [BSTQB — Foundation Level (CTFL)](https://bstqb.online/ctfl) *(formato da prova confirmado; preço não exposto na página)*
- [PSTQB — Certificações (Portugal)](https://pstqb.pt/en/certificacoes/)
- [Iterasys — Formação em Teste de Software](https://iterasys.com.br/pt/formacao-em-teste-de-software)
