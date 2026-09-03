# 95 · Referências — papers, docs, código e pessoas

`Nível: intermediário → pesquisa` · `Última atualização: 13/08/2026`

---

## 1. Artigos seminais

Ordenados cronologicamente. Onde o título é conhecido e o ano é firme, listo; onde tenho
dúvida sobre veículo ou número de página, cito só autor, título e ano.

| Ano | Autor(es) | Trabalho | Por que importa |
|---|---|---|---|
| 1949 | Alan Turing | *Checking a Large Routine* | primeira formulação da ideia de anexar asserções verificáveis a pontos do programa |
| 1970 | Edsger Dijkstra | *Notes on Structured Programming* | "testes mostram a presença de defeitos, nunca a ausência" |
| 1972 | David Parnas | *On the Criteria To Be Used in Decomposing Systems into Modules* | ocultação de informação — a raiz teórica da testabilidade |
| 1975 | Goodenough & Gerhart | *Toward a Theory of Test Data Selection* | primeira teoria formal de adequação; critérios confiáveis e válidos |
| 1978 | DeMillo, Lipton & Sayward | *Hints on Test Data Selection: Help for the Practicing Programmer* | **análise de mutação**; hipótese do programador competente |
| 1982 | Elaine Weyuker | *On Testing Non-testable Programs* | **problema do oráculo** |
| 1990 | Miller, Fredriksen & So | *An Empirical Study of the Reliability of UNIX Utilities* | o artigo que inventou o **fuzzing** |
| 1990 | Hamlet & Taylor | *Partition Testing Does Not Inspire Confidence* | crítica formal ao teste por partição |
| 1992 | A. Jefferson Offutt | *Investigations of the Software Testing Coupling Effect* | evidência empírica do efeito de acoplamento |
| 1998 | T. Y. Chen et al. | *Metamorphic Testing: A New Approach for Generating Next Test Cases* | teste metamórfico |
| 2000 | Mackinnon, Freeman & Craig | *Endo-Testing: Unit Testing with Mock Objects* | **inventa o mock object** |
| 2000 | Claessen & Hughes | *QuickCheck: A Lightweight Tool for Random Testing of Haskell Programs* (ICFP) | **teste baseado em propriedades** |
| ~2004 | Kuhn, Wallace & Gallo (NIST) | estudos sobre interação de fatores em falhas de software | base empírica do teste **pairwise** |
| 2007 | Martin Fowler | *Mocks Aren't Stubs* | nomeia a disputa clássica × mockista |
| 2009 | Mike Cohn | *Succeeding with Agile* (cap. sobre automação) | a **pirâmide de testes** |
| 2014 | Luo, Hariri, Eloussi & Marinov | *An Empirical Analysis of Flaky Tests* (FSE) | primeira caracterização sistemática de instabilidade |
| ~2016 | Fucci et al. | replicações sobre TDD | a ordem importa menos que a granularidade e a uniformidade do ciclo |
| 2026 | Ouedraogo, Kaboré et al. | *Prompt engineering in LLMs for automated unit test generation: A large-scale study* — [Empirical Software Engineering](https://link.springer.com/article/10.1007/s10664-026-10840-4) | estudo de larga escala comparando modelos e estratégias de prompt contra o EvoSuite |
| 2026 | — | *Enhancing Automated Unit Test Generation with LLMs: A Systematic Literature Review* — [ACM TOSEM](https://dl.acm.org/doi/10.1145/3802827) | revisão sistemática do campo |

> **Como encontrar:** a maior parte dos anteriores a 2000 está em bibliotecas digitais pagas
> (ACM DL, IEEE Xplore), mas quase todos têm cópia aberta na página pessoal dos autores ou em
> repositórios institucionais. Busque pelo título exato entre aspas.

---

## 2. Documentação oficial

### Python

| Recurso | Link |
|---|---|
| pytest — documentação | [docs.pytest.org](https://docs.pytest.org/) |
| pytest — changelog | [docs.pytest.org/en/stable/changelog.html](https://docs.pytest.org/en/stable/changelog.html) |
| pytest — história do projeto | [docs.pytest.org/en/stable/history.html](https://docs.pytest.org/en/stable/history.html) |
| `unittest` | [docs.python.org/3/library/unittest.html](https://docs.python.org/3/library/unittest.html) |
| `unittest.mock` | [docs.python.org/3/library/unittest.mock.html](https://docs.python.org/3/library/unittest.mock.html) |
| `doctest` | [docs.python.org/3/library/doctest.html](https://docs.python.org/3/library/doctest.html) |
| coverage.py | [coverage.readthedocs.io](https://coverage.readthedocs.io/) |
| Hypothesis | [hypothesis.readthedocs.io](https://hypothesis.readthedocs.io/) |
| uv | [docs.astral.sh/uv](https://docs.astral.sh/uv/) |

### JavaScript

| Recurso | Link |
|---|---|
| `node:test` — API | [nodejs.org/api/test.html](https://nodejs.org/api/test.html) |
| `node:assert` | [nodejs.org/api/assert.html](https://nodejs.org/api/assert.html) |
| Node — cobertura | [nodejs.org/learn/test-runner/collecting-code-coverage](https://nodejs.org/learn/test-runner/collecting-code-coverage) |
| Node — releases e cronograma | [nodejs.org/en/about/previous-releases](https://nodejs.org/en/about/previous-releases) |
| Vitest | [vitest.dev/guide](https://vitest.dev/guide/) · [browser mode](https://vitest.dev/guide/browser/) |
| Jest | [jestjs.io/docs/getting-started](https://jestjs.io/docs/getting-started) |
| Playwright | [playwright.dev/docs/intro](https://playwright.dev/docs/intro) |
| Testing Library | [testing-library.com](https://testing-library.com/) · [princípios](https://testing-library.com/docs/guiding-principles/) |
| fast-check (propriedades) | [fast-check.dev](https://fast-check.dev/) |

### Infraestrutura

| Recurso | Link |
|---|---|
| GitHub Actions | [docs.github.com/actions](https://docs.github.com/en/actions) |
| Testcontainers | [testcontainers.com](https://testcontainers.com/) |
| Stryker (mutação, JS) | [stryker-mutator.io](https://stryker-mutator.io/) |
| Cosmic Ray (mutação, Python) | [cosmic-ray.readthedocs.io](https://cosmic-ray.readthedocs.io/) |
| pre-commit | [pre-commit.com](https://pre-commit.com/) |

---

## 3. Normas e padrões

| Norma | Assunto | Observação |
|---|---|---|
| **ISO/IEC/IEEE 29119** | teste de software (partes 1 a 5) | substituiu a IEEE 829. **Controversa:** a comunidade context-driven fez campanha pública contra ela em 2014, argumentando que padroniza documentação em vez de eficácia. Conheça a controvérsia antes de citá-la como autoridade. |
| **DO-178C** | software aeronáutico | exige **MC-DC** para software de nível A |
| **IEC 62304** | software de dispositivo médico | exige rastreabilidade requisito → teste |
| **ISO 26262** | software automotivo | níveis ASIL, com exigências de cobertura por nível |
| **ISTQB Syllabus 4.0** | corpo de conhecimento do CTFL | gratuito em [istqb.org](https://www.istqb.org/) |
| **W3C WebDriver** | protocolo de automação de navegador | [w3.org/TR/webdriver2](https://www.w3.org/TR/webdriver2/) |

---

## 4. Código-fonte que vale ler

Ler o teste de projetos maduros ensina mais que muito tutorial.

| Projeto | O que observar | Link |
|---|---|---|
| **pytest** | os próprios testes do pytest; e como as fixtures são implementadas | [github.com/pytest-dev/pytest](https://github.com/pytest-dev/pytest) |
| **CPython** — `Lib/test/` | como se testa uma linguagem inteira | [github.com/python/cpython](https://github.com/python/cpython) |
| **Node.js** — `test/` | testes de runtime, e a implementação do `node:test` | [github.com/nodejs/node](https://github.com/nodejs/node) |
| **Vitest** | teste de uma ferramenta de teste — recursivo e instrutivo | [github.com/vitest-dev/vitest](https://github.com/vitest-dev/vitest) |
| **requests** (Python) | testes de cliente HTTP bem feitos | [github.com/psf/requests](https://github.com/psf/requests) |
| **SQLite** | a suíte tem cobertura de ramo próxima de 100 % e é declaradamente maior que o código | [sqlite.org/testing.html](https://www.sqlite.org/testing.html) |

> **A página de testes do SQLite** merece leitura à parte: é um dos relatos técnicos mais
> detalhados que existem sobre uma estratégia de teste completa — três suítes independentes,
> cobertura MC-DC, testes de falha de alocação, de corrupção de I/O e de *fuzzing*. É um
> exemplo extremo, e ver o extremo calibra o que é "normal".

---

## 5. Pessoas para acompanhar

| Pessoa | Contribuição | Onde |
|---|---|---|
| **Kent Beck** | SUnit, JUnit, XP, TDD | [kentbeck.com](https://www.kentbeck.com/) |
| **Martin Fowler** | vocabulário conceitual do campo | [martinfowler.com](https://martinfowler.com/) |
| **Michael Feathers** | código legado | escreve esparsamente |
| **Gerard Meszaros** | taxonomia de dublês | [xunitpatterns.com](http://xunitpatterns.com/) |
| **Vladimir Khorikov** | os quatro pilares | [enterprisecraftsmanship.com](https://enterprisecraftsmanship.com/) |
| **Kent C. Dodds** | Testing Library, Testing Trophy | [kentcdodds.com](https://kentcdodds.com/) |
| **David MacIver** | Hypothesis, teoria de *shrinking* | [drmaciver.com](https://drmaciver.com/) |
| **Holger Krekel** | criador do pytest | — |
| **Bruno Oliveira** | mantenedor do pytest, brasileiro | [github.com/nicoddemus](https://github.com/nicoddemus) |
| **Anthony Fu** | Vitest, Vite | [antfu.me](https://antfu.me/) |
| **James Bach / Cem Kaner** | escola context-driven; crítica ao excesso de processo | [satisfice.com](https://www.satisfice.com/) · [kaner.com](https://kaner.com/) |
| **Eduardo Mendes** (*dunossauro*) | conteúdo de Python em português | [YouTube](https://www.youtube.com/c/Dunossauro) |

---

## 6. Blogs e publicações periódicas

| Fonte | Idioma | Por quê |
|---|---|---|
| [Google Testing Blog](https://testing.googleblog.com/) | EN | prática em escala; arquivo de ~20 anos |
| [martinfowler.com](https://martinfowler.com/testing/) | EN | conceitos |
| [Enterprise Craftsmanship](https://enterprisecraftsmanship.com/) | EN | Khorikov, artigos sobre unitário |
| [Ministry of Testing](https://www.ministryoftesting.com/) | EN | comunidade de QA |
| [Increment — número sobre testes](https://increment.com/testing/) | EN | edição temática (Stripe), boa e gratuita |

---

## 7. Onde perguntar

| Lugar | Para quê |
|---|---|
| Stack Overflow — etiquetas `pytest`, `jestjs`, `vitest`, `playwright` | dúvida específica e reproduzível |
| GitHub Discussions dos próprios projetos | comportamento da ferramenta, e onde os mantenedores respondem |
| Discord/Slack do Vitest e do Playwright | dúvida rápida |
| Comunidades brasileiras de Python e de QA | em português |

**Como perguntar de forma que alguém consiga responder:** exemplo **mínimo e reproduzível**,
versões exatas (`pytest --version`, `node --version`), a saída **literal** do erro, e o que
você já tentou. Uma pergunta bem formulada costuma se responder sozinha no meio da escrita.

---

## 8. Como este material foi verificado

Para o leitor avaliar a confiabilidade do que leu:

| Item | Como foi verificado |
|---|---|
| projeto-modelo Python | **executado**: 190 testes, cobertura 98,7 %, pytest 9.1.1, Python 3.10.12 |
| projeto-modelo JavaScript | **executado**: 245 testes (`node:test`) + 52 (Vitest 4.1.10), Node v24.18.0 |
| exemplos do [06](06-exemplos.md) | **todos executados**; as saídas mostradas são as reais |
| experimento de mutação do [19](19-cobertura-e-metricas.md) | **executado**: 7 mutações aplicadas à mão, com resultados registrados |
| semânticas de igualdade do [17](17-javascript-vitest-jest.md) | **executadas** em Node e Vitest |
| versões de ferramenta | `npm view`, `--version` local, e páginas oficiais, em 12–13/08/2026 |
| preços | busca na web em 13/08/2026; a origem de cada número está declarada em [80](80-custos-e-licencas.md) |
| cursos | busca na web em 13/08/2026; onde não confirmei autor ou duração, está dito no texto |
| **não executado** | instalação em Windows e macOS; Jest 30; Playwright; Testcontainers; os laboratórios de [70](70-pratica.md) |

---

## Autoteste

1. Quem formulou o problema do oráculo, e em que ano?
2. Qual artigo inventou o mock object, e em que contexto?
3. Que artigo de 1972 é a raiz teórica da testabilidade, e por quê?
4. Por que a ISO/IEC/IEEE 29119 é controversa?
5. Qual norma exige MC-DC, e para que tipo de software?
6. Por que a página de testes do SQLite vale a leitura?
7. Como formular uma pergunta técnica que tem chance de ser respondida?
8. Quais partes deste material **não** foram executadas pelo autor?
