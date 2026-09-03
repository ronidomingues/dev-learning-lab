# 90 · Bibliografia comentada

> **Nível:** todos · **Verificado em:** 31/08/2026
> **Aviso importante:** **não existe livro sobre uv.** A ferramenta tem dois anos e meio,
> e livros levam de um a dois anos para sair — quando saem, o uv já mudou de versão minor
> várias vezes. O que existe são livros sobre **empacotamento, projeto e ferramental
> Python**, dentro dos quais o uv é um capítulo ou uma menção.
>
> Nenhum livro, ISBN ou edição foi inventado. Onde não pude confirmar o ano exato, digo
> isso explicitamente em vez de chutar.

---

## 1. O que ler primeiro (e é gratuito)

### A documentação oficial do uv
[docs.astral.sh/uv](https://docs.astral.sh/uv/) · **gratuita** · inglês

Não é livro, mas é o material mais completo e mais atualizado que existe. As seções
*Guides* e *Concepts* juntas dão duas a três horas de leitura e cobrem mais do que
qualquer livro cobrirá pelos próximos dois anos.

### Python Packaging User Guide
[packaging.python.org](https://packaging.python.org/) · **gratuito** · PyPA · inglês

O material canônico sobre empacotamento Python, independente de ferramenta. É onde estão
as explicações neutras de sdist, wheel, metadados, publicação e ambientes virtuais. Leia
a seção *Discussions* — é onde os trade-offs são discutidos honestamente.

### As PEPs
[peps.python.org](https://peps.python.org/) · **gratuito** · inglês

O texto normativo. Densas, mas as relevantes são curtas: 517, 518, 621, 723 e 735 se leem
em uma tarde e explicam **por que** o `pyproject.toml` tem a forma que tem.

---

## 2. Livros sobre ferramental e empacotamento

### ⭐ Hypermodern Python Tooling — Claudio Jolowicz
**O'Reilly Media, 1ª edição, 2024. ISBN 978-1-098-13958-2.**
*Building Reliable Workflows for an Evolving Python Ecosystem*

| | |
|---|---|
| **Nível** | intermediário → avançado |
| **Melhor em** | ser o **único** livro que trata a cadeia de ferramentas moderna como um sistema coerente: ambientes, dependências, testes, tipos, lint, CI, publicação |
| **Cobre uv?** | sim, mas como **um entre vários** (trata também Poetry, Rye, Hatch, Nox, pytest, mypy, pre-commit, Ruff) |
| **Envelheceu?** | **parcialmente.** É de 2024, antes de o uv consolidar o modo projeto e antes do Rye ser descontinuado em favor do uv. Os **princípios** continuam válidos; alguns comandos e recomendações de ferramenta, não |
| **Gratuito?** | não. O autor mantém o blog e o template *Hypermodern Python* gratuitos |
| **Autor** | engenheiro sênior na Cloudflare, comantenedor do Nox, ativo na comunidade |
| **Edição em português** | não conheço |

**Minha avaliação:** se você vai comprar **um** livro depois deste curso, é este. Leia
sabendo que o capítulo de gerenciadores de dependência está datado, e que este curso é
mais atual naquilo especificamente.

### Publishing Python Packages — Dane Hillard
**Manning, 2023. ISBN 978-1-61729-991-9 (impresso); 978-1-63835-168-9 (eletrônico).**
*Test, share, and automate your projects*

| | |
|---|---|
| **Nível** | intermediário |
| **Melhor em** | o ciclo completo de **publicar**: estrutura, metadados, testes, documentação, versionamento, automação, PyPI |
| **Cobre uv?** | ❌ **não** — é anterior à ferramenta. Usa `setuptools`, `flit`, `tox` |
| **Envelheceu?** | os **conceitos** não; as ferramentas, sim |
| **Gratuito?** | não; a Manning costuma liberar o primeiro capítulo |
| **Site** | [pypackages.com](https://pypackages.com/) |
| **Edição em português** | não conheço |

**Quando vale:** se o seu problema é *publicar bibliotecas*, e você quer o processo
completo (incluindo documentação e política de versionamento), não só os comandos.
Traduza mentalmente as ferramentas para o uv usando o
[18-publicacao](18-publicacao-e-build-backend.md).

---

## 3. Livros de Python que dão a base

### ⭐ Python Fluente — Luciano Ramalho
**2ª edição.** Original: *Fluent Python*, O'Reilly, 2022, ISBN 978-1-492-05635-5.
**Edição brasileira: Novatec, 2ª edição, 2023.**

| | |
|---|---|
| **Nível** | intermediário → avançado |
| **Melhor em** | ensinar a **pensar em Python**, e não apenas a escrever Python com sotaque de outra linguagem |
| **Tradução** | ✅ **excelente** — o autor é brasileiro e escreveu o original em inglês; a edição da Novatec é cuidadosa |
| **Envelheceu?** | não; a 2ª edição cobre até 3.10/3.11 e o conteúdo é conceitual |
| **Relação com uv** | nenhuma direta — é o Python que você vai empacotar |

**É o melhor livro de Python em português que existe.** Se você só sabe o básico, este é
o próximo passo, antes de qualquer coisa sobre ferramental.

### Python Distilled — David Beazley
**Addison-Wesley Professional, 2021. ISBN 978-0-13-417327-6.**

| | |
|---|---|
| **Nível** | intermediário |
| **Melhor em** | densidade. É o Python essencial, sem gordura, por alguém que escreve sobre a linguagem há 25 anos |
| **Envelheceu?** | pouco |
| **Edição em português** | não conheço |

### Robust Python — Patrick Viafore
**O'Reilly, 2021. ISBN 978-1-098-10066-7.**
*Write Clean and Maintainable Code*

| | |
|---|---|
| **Nível** | intermediário → avançado |
| **Melhor em** | anotações de tipo, contratos e projeto para manutenção de longo prazo |
| **Relação com este curso** | contexto para `uv check` e para o `ty` |
| **Edição em português** | não conheço |

### Architecture Patterns with Python — Harry Percival e Bob Gregory
**O'Reilly, 2020. ISBN 978-1-492-05203-6.**

| | |
|---|---|
| **Nível** | avançado |
| **Melhor em** | arquitetura de aplicações Python: repositórios, unidade de trabalho, eventos |
| **Gratuito?** | ✅ **sim, legalmente** — o texto completo está em [cosmicpython.com](https://www.cosmicpython.com/), liberado pelos autores |
| **Edição em português** | não conheço |

---

## 4. Fundamentos teóricos (para o [60-teoria-avancada](60-teoria-avancada.md))

### Managing the Complexity of Large Free and Open Source Package-Based Software Distributions
**Mancinelli, Boender, Di Cosmo, Vouillon, Durak, Leroy, Treinen.**
*Proceedings of ASE 2006 (21st IEEE/ACM International Conference on Automated Software
Engineering).* **Gratuito** — disponível em repositórios acadêmicos abertos (HAL, INRIA).

O artigo que estabeleceu a formulação de resolução de dependências como problema de
satisfatibilidade, no contexto do Debian. Origem do projeto EDOS/Mancoosi. **É a
referência canônica para a NP-completude.**

### PubGrub: Next-Generation Version Solving — Natalie Weizenbaum
**Documentação do `pub` (Dart), 2018.** **Gratuito:**
[github.com/dart-lang/pub/blob/master/doc/solver.md](https://github.com/dart-lang/pub/blob/master/doc/solver.md)

Não é livro nem artigo revisado por pares: é uma especificação técnica escrita com
clareza excepcional. Se você quer entender o algoritmo que o uv usa, **é a fonte
primária**, e é acessível a quem tem lógica proposicional básica.

### Handbook of Satisfiability — Biere, Heule, van Maaren, Walsh (eds.)
**IOS Press, 2ª edição, 2021. ISBN 978-1-64368-160-3.**

Referência de mil e tantas páginas sobre SAT. Você quer os capítulos sobre **CDCL** e
**aprendizado de cláusulas** — é a teoria por trás do PubGrub. **Livro caro e denso;
consulte em biblioteca universitária.** A 1ª edição (2009) circula gratuitamente em
alguns repositórios institucionais.

### The Purely Functional Software Deployment Model — Eelco Dolstra
**Tese de doutorado, Universidade de Utrecht, 2006. Gratuita:**
[edolstra.github.io/pubs/phd-thesis.pdf](https://edolstra.github.io/pubs/phd-thesis.pdf)

A tese que originou o Nix. Vale para entender uma **abordagem alternativa** ao problema:
em vez de resolver conflitos, torná-los impossíveis. Longa, mas os capítulos 1 a 3 dão o
argumento.

### Minimal Version Selection — Russ Cox
**2018. Gratuito:** [research.swtch.com/vgo-mvs](https://research.swtch.com/vgo-mvs)

O argumento do Go para **não** usar um resolvedor. Leitura curta, provocativa e
importante: mostra que o problema pode ser redefinido em vez de resolvido. Discutido no
[60-teoria-avancada](60-teoria-avancada.md#6-modelos-alternativos-e-por-que-o-python-não-os-usa).

---

## 5. Artigos e ensaios que valem mais que muitos livros

Todos **gratuitos**:

| Título | Autor | Ano | Por que ler |
|---|---|---|---|
| [uv: Python packaging in Rust](https://astral.sh/blog/uv) | Charlie Marsh / Astral | 2024 | o documento fundador; a ambição declarada |
| [uv: Unified Python packaging](https://astral.sh/blog/uv-unified-python-packaging) | Astral | 2024 | o momento em que o uv virou o que é hoje |
| [Should You Use Upper Bound Version Constraints?](https://iscinumpy.dev/post/bound-version-constraints/) | Henry Schreiner | 2021 | **leitura obrigatória.** Muda como você escreve dependências |
| [Thoughts on OpenAI acquiring Astral](https://simonwillison.net/2026/mar/19/openai-acquiring-astral/) | Simon Willison | 2026 | análise equilibrada da aquisição |
| [Why aren't we uv yet?](https://aleyan.com/blog/2026-why-arent-we-uv-yet/) | Aleyan | 2026 | dados de adoção real, não impressão |
| [Dependency Confusion](https://medium.com/@alex.birsan/dependency-confusion-4a5d60fec610) | Alex Birsan | 2021 | o ataque que motiva o `explicit = true` |

---

## 6. O que **não** comprar

Sendo direto, para você não gastar mal:

- **Qualquer livro anterior a 2024 que prometa "gerenciamento moderno de dependências
  Python".** O campo mudou; você vai aprender `pipenv` ou o Poetry de 2019.
- **Cursos pagos de uv em plataformas de marketplace.** Não vi nenhum que cubra mais que
  a documentação oficial gratuita, e vários são transcrições dela.
- **Livros de "Python para iniciantes" se você já programa em outra linguagem.**
  Vá direto ao *Python Fluente* ou ao *Python Distilled*.

---

## 7. Uma ordem de leitura sugerida

**Se você quer usar bem:**
1. Este curso, 01 a 07
2. Documentação oficial do uv — *Guides*
3. *Hypermodern Python Tooling* (com a ressalva sobre o capítulo de dependências)

**Se você quer entender por dentro:**
1. Este curso, 10 a 21
2. Python Packaging User Guide — *Discussions*
3. PEPs 517, 518, 621, 723, 735, 751
4. A especificação do PubGrub
5. Este curso, 60
6. Mancinelli et al. (2006)

**Se você quer o Python, não a ferramenta:**
1. *Python Fluente*, 2ª ed. (Novatec)
2. *Robust Python*
3. *Architecture Patterns with Python* (gratuito)

---

## Autoteste

1. Por que não existe livro sobre uv, e qual é o substituto?
2. Qual é o único livro que trata o ferramental moderno como sistema — e qual é a
   ressalva ao lê-lo hoje?
3. Cite três materiais **legalmente gratuitos** desta lista e o que cada um cobre.
4. Qual livro de Python em português tem a melhor tradução, e por quê?
5. Qual é a fonte primária para entender o algoritmo de resolução do uv?
6. Qual artigo muda a forma como você escreve dependências, e qual é a tese dele?
7. Qual leitura mostra um modelo em que a resolução é **evitada** em vez de resolvida?
8. Que tipo de livro este arquivo recomenda **não** comprar, e por quê?
9. Onde está a referência canônica para a NP-completude de resolução de dependências?
10. Monte sua ordem de leitura para os próximos dois meses e justifique.

---

**Verificação:** títulos, editoras, anos e ISBNs conferidos em 31/08/2026 nas páginas dos
editores e em catálogos ([oreilly.com](https://www.oreilly.com/),
[manning.com](https://www.manning.com/), [novatec.com.br](https://novatec.com.br/)).
Onde a edição em português não está listada, foi porque **não confirmei a existência** —
não porque ela não exista. Nenhum ISBN foi reproduzido de memória sem conferência.

**Próximo:** [95-referencias.md](95-referencias.md)
