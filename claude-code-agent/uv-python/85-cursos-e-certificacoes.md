# 85 · Cursos gratuitos e certificações

> **Nível:** todos · **Pesquisado na web em 31/08/2026.**
> Links podem expirar. Vídeos podem ser removidos. **Confira a data de publicação de cada
> curso antes de investir tempo** — material de uv anterior a agosto de 2024 descreve uma
> ferramenta que não existe mais (era só um substituto do `pip`, sem `uv init`, `uv add`
> nem `uv.lock`).

---

## 0. Aviso metodológico, para você não perder tempo

Existe pouquíssimo **curso** de uv, e muito **vídeo de introdução**. A razão é boa: o uv
é aprendido em horas, não em meses. A consequência é que:

- vídeos de 10 a 40 minutos cobrem 80% do que você usa no dia a dia;
- o restante está na **documentação oficial**, que é excelente e é onde eu mandaria você
  primeiro;
- e o que realmente falta em quase todo material é o **porquê** — que é o que este curso
  tenta preencher.

**Marquei abaixo o que verifiquei ser gratuito e o que só *parece*.** Não assisti a todos
os vídeos integralmente; avaliei por descrição, canal, data e reputação. Onde tenho
opinião firme, digo; onde não tenho, digo também.

---

## 1. 🇧🇷 Português (prioridade)

### 1.1 A referência: documentação oficial (em inglês, mas indispensável)

Antes dos vídeos, um aviso honesto: **a documentação oficial do uv não tem tradução para
o português**. Ela é curta, direta e bem escrita. Se você lê inglês técnico razoavelmente,
vá lá primeiro:
[docs.astral.sh/uv](https://docs.astral.sh/uv/) — especialmente a seção *Guides*.

### 1.2 Vídeos em português — YouTube

| Título | Canal / autor | Link | Duração aprox. | Nível | Ano | Vale? |
|---|---|---|---|---|---|---|
| **UV: A ferramenta do Python que todo mundo está adotando** | Hashtag Programação | [youtube.com/watch?v=zjN-6Z0ltkg](https://www.youtube.com/watch?v=zjN-6Z0ltkg) | ~20 min | iniciante | 2025/2026 | ✅ **melhor porta de entrada em PT-BR**. Canal grande, didática clara, foca no fluxo prático |
| **Ambientes Virtuais com UV: aprenda a instalar e usar na prática** | — | [youtube.com/watch?v=06VPjPEd2uo](https://www.youtube.com/watch?v=06VPjPEd2uo) | ~25 min | iniciante | **maio/2026** | ✅ o mais recente que encontrei em PT; bom para instalação passo a passo |
| **UV: O gerenciador de pacotes Python incrivelmente rápido** | — | [youtube.com/watch?v=oP892pUFZqc](https://www.youtube.com/watch?v=oP892pUFZqc) | ~15 min | iniciante | set/2025 | ✅ panorama rápido; já cobre o modo projeto |
| **uv: gestão de pacotes em Python de forma simples** | — (🇵🇹 Portugal) | [youtube.com/watch?v=GAa5Ngo_5e4](https://www.youtube.com/watch?v=GAa5Ngo_5e4) | ~20 min | iniciante | 2025 | ✅ português europeu; boa alternativa de sotaque |
| **ADEUS PIP? Implementando projetos de IA em Python facilmente com UV** | — | [youtube.com/watch?v=6NHGbZzK6co](https://www.youtube.com/watch?v=6NHGbZzK6co) | ~20 min | iniciante | 2025 | 🟡 título sensacionalista; conteúdo útil se seu foco é IA/ML |

> **Como eu usaria:** assista **um** deles (o primeiro), faça o
> [04-como-comecar](04-como-comecar.md) deste curso, e vá para a documentação oficial.
> Assistir a cinco vídeos introdutórios é repetir a mesma hora cinco vezes.

### 1.3 Onde o uv aparece dentro de cursos maiores em PT-BR

| Curso | Autor | Link | Comentário |
|---|---|---|---|
| **FastAPI do Zero** | Eduardo Mendes (*dunossauro*) | [fastapidozero.dunossauro.com](https://fastapidozero.dunossauro.com/estavel/) | **Gratuito de verdade**, licença Creative Commons BY-NC-SA, financiado pela comunidade. A edição de 2026 cobre FastAPI 0.141, Pydantic 2.13, SQLAlchemy 2.0, Alembic, pytest, Docker, GitHub Actions e deploy no Fly.io, com Python 3.11 a 3.14. É o **melhor material técnico gratuito em português** que conheço para Python moderno. ⚠️ Confirme qual gerenciador de dependências a edição que você está lendo usa — o curso já usou Poetry, e o ecossistema migrou; a estrutura de aprendizado vale de qualquer forma |
| **Live de Python** | Eduardo Mendes | [youtube.com/@Dunossauro](https://www.youtube.com/@Dunossauro) | *lives* semanais, longas e profundas. Procure no canal por "empacotamento", "uv" e "dependências". É onde se aprende o **porquê**, não só o comando |
| **Curso em Vídeo — Python 3** | Gustavo Guanabara | [YouTube](https://www.youtube.com/playlist?list=PLHz_AreHm4dlKP6QQCekuIPky1CiwmdI6) | não cobre uv (é de Python básico), mas é o pré-requisito recomendado no [02-pre-requisitos](02-pre-requisitos.md) |
| **Programação Dinâmica** | Ju Amorim | [youtube.com/@ProgramacaoDinamica](https://www.youtube.com/@ProgramacaoDinamica) | canal forte em dados/Python; procure por conteúdo de ambiente e ferramentas |

---

## 2. 🇬🇧 Inglês

### 2.1 Documentação e guias oficiais (o melhor material que existe)

| Recurso | Link | Comentário |
|---|---|---|
| **uv — Guides** | [docs.astral.sh/uv/guides](https://docs.astral.sh/uv/guides/) | trilha oficial: instalar Python, rodar scripts, usar ferramentas, criar projetos, publicar pacotes. **Comece aqui.** ~2 h |
| **uv — Concepts** | [docs.astral.sh/uv/concepts](https://docs.astral.sh/uv/concepts/) | projetos, resolução, cache, versões de Python, índices. É a parte densa |
| **uv — CLI Reference** | [docs.astral.sh/uv/reference/cli](https://docs.astral.sh/uv/reference/cli/) | referência completa de comandos |
| **uv — Internals: Resolver** | [docs.astral.sh/uv/reference/internals/resolver](https://docs.astral.sh/uv/reference/internals/resolver/) | como o PubGrub funciona ali dentro. Raro e valioso |
| **Python Packaging User Guide** | [packaging.python.org](https://packaging.python.org/) | da PyPA; o material canônico sobre empacotamento, independente de ferramenta |
| **CHANGELOG do uv** | [github.com/astral-sh/uv/blob/main/CHANGELOG.md](https://github.com/astral-sh/uv/blob/main/CHANGELOG.md) | a forma mais confiável de se manter atualizado |

### 2.2 Vídeos e artigos

| Título | Autor / plataforma | Link | Duração | Nível | Ano | Vale? |
|---|---|---|---|---|---|---|
| **UV — A Faster, All-in-One Package Manager to Replace Pip and Venv** | Corey Schafer (YouTube) | [youtube.com/watch?v=AMdG7IjgSPM](https://www.youtube.com/watch?v=AMdG7IjgSPM) | ~40 min | iniciante–intermediário | abr/2025 | ✅ **a melhor introdução em vídeo que encontrei.** Corey Schafer é referência histórica em tutoriais de Python; ritmo e profundidade certos |
| **Mastering Python Dependency Management with UV Astral** | YouTube | [youtube.com/watch?v=f4_cxaParLQ](https://www.youtube.com/watch?v=f4_cxaParLQ) | ~30 min | intermediário | abr/2026 | ✅ mais recente; cobre o modo projeto e lock |
| **uv: A Complete Guide to Python's Fastest Package Manager** | pydevtools (texto) | [pydevtools.com/handbook/explanation/uv-complete-guide](https://pydevtools.com/handbook/explanation/uv-complete-guide/) | ~1 h de leitura | intermediário | 2026 | ✅ um dos melhores textos de referência; cobre migração |
| **Python UV: The Ultimate Guide** | DataCamp (texto) | [datacamp.com/tutorial/python-uv](https://www.datacamp.com/tutorial/python-uv) | ~40 min | iniciante | 2026 | 🟡 bom e gratuito para ler; a DataCamp usa isso como funil para cursos pagos |
| **Talk Python #476 — Unified Python packaging with uv** | Michael Kennedy com Charlie Marsh | [talkpython.fm/episodes/show/476](https://talkpython.fm/episodes/show/476/unified-python-packaging-with-uv) | ~1 h | intermediário | ago/2024 | ✅ **o criador explicando as decisões de projeto.** Ótimo para o "porquê" |
| **Talk Python #552 — Astral joins OpenAI** | Michael Kennedy com Charlie Marsh | [talkpython.fm/episodes/show/552](https://talkpython.fm/episodes/show/552/astral-joins-openai) | ~1 h | todos | 2026 | ✅ contexto essencial sobre a aquisição e o futuro |
| **Simon Willison — Thoughts on OpenAI acquiring Astral** | blog | [simonwillison.net/2026/mar/19/openai-acquiring-astral](https://simonwillison.net/2026/mar/19/openai-acquiring-astral/) | 10 min | todos | mar/2026 | ✅ análise equilibrada de alguém sem interesse comercial no assunto |

---

## 3. 🇫🇷 Francês

Material em francês sobre uv é **escasso** — mais escasso que em português. O que existe:

| Título | Tipo | Link | Nível | Ano | Comentário |
|---|---|---|---|---|---|
| **🚀 UV — L'outil qui remplace PIP en 10x plus rapide** | vídeo YouTube | [youtube.com/watch?v=otFi4KLMCXk](https://www.youtube.com/watch?v=otFi4KLMCXk) | iniciante | fev/2025 | ✅ o principal vídeo em francês que encontrei; ⚠️ é anterior a boa parte da evolução da ferramenta |
| **uv, le gestionnaire de projets Python ultra rapide** | artigo | [vidjinnangni.net/uv-python](https://vidjinnangni.net/uv-python/) | iniciante–intermediário | 2025/2026 | ✅ artigo bem escrito, cobre o modo projeto |
| **UV Cheatsheet — Gestionnaire Python Ultra-Rapide** | referência | [clearcode.fr/courses/programming/python/cheatsheet/uv](https://www.clearcode.fr/courses/programming/python/cheatsheet/uv) | todos | 2026 | ✅ folha de referência de comandos; útil para consulta |
| **Python UV : Le guide ultime du gestionnaire de paquets** | artigo | [datacamp.com/fr/tutorial/python-uv](https://www.datacamp.com/tutorial/python-uv) | iniciante | 2026 | 🟡 tradução do texto em inglês da DataCamp |
| **uv Python : 100x Plus Vite que pip, 12 Étapes** | artigo | [tech-insider.org/fr/uv-python-tutoriel-12-etapes-2026](https://tech-insider.org/fr/uv-python-tutoriel-12-etapes-2026/) | iniciante | 2026 | 🟡 título com número inflado (ver o mito M2 em [75-armadilhas](75-armadilhas.md)); conteúdo prático razoável |

> **Recomendação para quem estuda em francês:** o material é fino demais para ser sua
> fonte principal. Use-o como reforço e leia a documentação oficial em inglês. Se você
> quer Python geral em francês, o canal [Docstring](https://www.youtube.com/@Docstring)
> (Thibault Houdon) é a melhor referência gratuita que conheço.

---

## 4. Certificações

### 4.1 Existe certificação de uv?

**Não. Nenhuma.** Nem da Astral/OpenAI, nem da Python Software Foundation, nem de
terceiros. E, na minha opinião profissional, **isso está certo**: o uv é uma ferramenta
de uma tarde, não um corpo de conhecimento que justifique exame.

Se alguém lhe vender uma "certificação em uv", é venda de certificado, não de
conhecimento.

**O que substitui, e vale mais no mercado:**

1. Um repositório público seu com `pyproject.toml` limpo, `uv.lock` versionado, CI com
   `uv sync --locked`, e um Dockerfile com as camadas separadas corretamente.
2. Uma contribuição aceita em algum projeto — inclusive no próprio uv, cujas *issues*
   marcadas como `good first issue` são acessíveis.
3. Saber responder às perguntas do [70-pratica](70-pratica.md#autoavaliação-final).

### 4.2 Certificações de **Python** que fazem sentido

Se o seu objetivo é o currículo, certifique **Python**, não a ferramenta.

| Certificação | Emissor | Custo (31/08/2026) | Valor de mercado — avaliação franca |
|---|---|---|---|
| **freeCodeCamp — Certified Python Developer** | freeCodeCamp | **gratuita**, incluindo o exame | 🟡 **simbólica, mas honesta.** Baseada em 5 projetos avaliados por testes automatizados + exame de 90 questões. É pública e verificável. Anunciada em 15/12/2025; disponível também em espanhol. Não abre portas sozinha, mas os **projetos** que você produz abrem |
| **PCEP — Certified Entry-Level Python Programmer** | Python Institute (OpenEDG) | **US$ 69** (≈ R$ 358, ao câmbio de 31/08/2026); US$ 86 com repetição; US$ 95 com repetição + simulado | 🟡 reconhecida em processos formais e concursos; conteúdo é Python básico. Não é gratuita, apesar de muito material promocional sugerir que seja |
| **PCAP — Certified Associate** | Python Institute | ~US$ 295 (≈ R$ 1.530) | 🟡 nível intermediário; alguma tração em empresas que exigem certificação formal |
| **Certificados de conclusão** (Coursera, Udemy, DataCamp) | plataformas | grátis para assistir, **pago para certificar** | ❌ pouco peso real |

> **Minha opinião, dita sem rodeios:** no mercado brasileiro de desenvolvimento,
> **certificação de Python vale pouco** comparada a código público e a saber conversar
> sobre trade-offs numa entrevista. Ela pesa em três situações específicas: concurso
> público, empresa com política formal de certificação, e visto de trabalho que pontua
> credenciais. Fora disso, o tempo rende mais construindo algo.

### 4.3 Trilhas gratuitas de universidades

| Curso | Instituição | Link | Comentário |
|---|---|---|---|
| **CS50P — Introduction to Programming with Python** | Harvard (edX/OpenCourseWare) | [cs50.harvard.edu/python](https://cs50.harvard.edu/python/) | ✅ **gratuito para assistir e fazer**, com certificado gratuito do CS50 (o certificado verificado do edX é pago). Um dos melhores cursos de Python do mundo. Não cobre uv, mas é a base |
| **MIT 6.100L — Introduction to CS and Programming using Python** | MIT OpenCourseWare | [ocw.mit.edu](https://ocw.mit.edu/courses/6-100l-introduction-to-cs-and-programming-using-python-fall-2022/) | ✅ gratuito, sem certificado; rigoroso |
| **Python for Everybody** | University of Michigan (Charles Severance) | [py4e.com](https://www.py4e.com/) | ✅ gratuito, material aberto, tem versão em português |

---

## 5. Uma trilha de estudo recomendada

**Se você não sabe Python (~8 semanas):**
1. Curso em Vídeo ou CS50P — 6 semanas
2. Este curso, arquivos 01 a 07 — 1 semana
3. [70-pratica](70-pratica.md), labs 1 a 5 — 1 semana

**Se você já sabe Python (~2 semanas):**
1. Vídeo da Hashtag (20 min) ou do Corey Schafer (40 min)
2. Este curso, 01 → 07, fazendo tudo — 3 dias
3. Documentação oficial, seção *Guides* — 1 dia
4. Labs 1 a 10 — 4 dias
5. Migrar um projeto real (Lab 14) — 1 dia

**Se você já usa uv e quer profundidade (~2 semanas):**
1. Arquivos 10 a 21 deste curso
2. Talk Python #476 (as decisões de projeto)
3. [60-teoria-avancada](60-teoria-avancada.md) + a especificação do PubGrub
4. Documentação de *Internals: Resolver*
5. Uma contribuição no repositório do uv

---

## Autoteste

1. Existe certificação oficial de uv? Por que a resposta é a esperada?
2. Qual é o melhor material gratuito em português para Python moderno, e sob que licença?
3. Por que material de uv anterior a agosto de 2024 é enganoso?
4. Qual certificação de Python é genuinamente gratuita, incluindo o exame?
5. A PCEP é gratuita? Quanto custa, em reais?
6. Em quais três situações uma certificação de Python realmente pesa?
7. Onde encontrar a explicação oficial de como o resolvedor funciona?
8. Qual episódio de podcast traz o criador explicando as decisões de projeto?
9. Por que este arquivo recomenda assistir a **um** vídeo introdutório, e não a cinco?
10. Qual é a alternativa a uma certificação, segundo este curso — e por que vale mais?

---

**Fontes (pesquisadas na web em 31/08/2026):** buscas em português, inglês e francês por
cursos gratuitos de uv; páginas oficiais de
[docs.astral.sh/uv](https://docs.astral.sh/uv/),
[fastapidozero.dunossauro.com](https://fastapidozero.dunossauro.com/estavel/),
[freecodecamp.org — nova certificação de Python](https://www.freecodecamp.org/news/freecodecamps-new-python-certification-is-now-live/),
[pythoninstitute.org/pcep](https://pythoninstitute.org/pcep),
[cs50.harvard.edu/python](https://cs50.harvard.edu/python/),
[talkpython.fm](https://talkpython.fm/).
⚠️ Não assisti integralmente a todos os vídeos listados; a avaliação de qualidade
considera canal, data, descrição e reputação. Duração e ano são aproximados.

**Próximo:** [90-bibliografia.md](90-bibliografia.md)
