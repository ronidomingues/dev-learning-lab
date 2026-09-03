# 90 · Bibliografia comentada

`Nível: todos` · **Verificada na web em 01/09/2026**

> **Regra deste arquivo:** nada de livro, ISBN ou edição inventados. O que não foi
> confirmado está marcado como **não confirmado**, ou citado só por autor e título.
>
> **Aviso que vale para toda a seção 1:** o MCP mudou de forma profunda em **28/07/2026**.
> **Todo livro publicado antes disso ensina um protocolo com sessão, com handshake
> `initialize` e com requisições iniciadas pelo servidor — mecânica que não existe mais.**
> Os conceitos continuam válidos; a mecânica, não. Ver [17](17-versionamento-e-compatibilidade.md).

---

## 1. Livros sobre MCP

Campo novo: o primeiro livro é de 2025. Não existe ainda um "clássico".

### 1.1 Publicados

| Livro | Autor | Editora | Data | Nível | Comentário |
|---|---|---|---|---|---|
| **Learn Model Context Protocol with Python: Build agentic systems in Python with the new standard for AI capabilities** | Christoffer Noring (com Dan Wahlin no e-book) | **Packt** | **27/10/2025**, ~304 p. ISBN 978-1806103232 (papel), 978-1806103225 (e-book) | iniciante–intermediário | O mais didático em Python. **Ensina a era com `initialize` e `FastMCP`.** Leia pelos conceitos; traduza a mecânica pela tabela de [17 §8](17-versionamento-e-compatibilidade.md). Repositório de código no [GitHub da Packt](https://github.com/PacktPublishing/Learn-Model-Context-Protocol-with-Python) |
| **The MCP Standard: A Developer's Guide to Building Universal AI Tools with the Model Context Protocol** | Srinivasan Sekar | **Apress** (Springer) | **fevereiro de 2026** (e-book 06/02, capa mole 07/02) | intermediário | Guia prático de servidores e clientes **em TypeScript**, com o SDK oficial. Anterior à revisão `2026-07-28` |
| **AI Agents with MCP: Model Context Protocol for Building Clients, Servers, and End-to-End Agents** | Kyle Stratis | **O'Reilly** | **03/11/2026** | intermediário | **O mais recente da lista.** Pela data, é o único com chance real de cobrir a revisão `2026-07-28` — **confirme o sumário antes de comprar** |
| **Model Context Protocol for LLMs: Build secure, scalable, and context-aware AI agents using a standardized protocol** | Naveen Krishnan | **Packt** | 2026 · ISBN 978-1806662272 | intermediário | Ênfase em segurança e escala. Data exata **não confirmada** |
| **AI Agents in Action, Second Edition** | Micheal Lanham | **Manning** | 2026 | intermediário | Não é livro **de** MCP: é de agentes, com MCP como um capítulo. Usa a analogia do "USB-C" |

**Recomendação, com o raciocínio:**

- se você quer **um livro em Python hoje** e aceita traduzir a mecânica: **Noring (Packt)**;
- se você quer **TypeScript**: **Sekar (Apress)**;
- se você pode **esperar e conferir**: **Stratis (O'Reilly, nov/2026)** é o único com data
  posterior à reescrita;
- **opinião honesta:** nenhum livro substitui a especificação neste momento. O campo se
  move mais rápido do que o ciclo editorial. **Use livro para intuição e estrutura; use a
  spec para a verdade.**

### 1.2 O que não existe

Não há, em 01/09/2026:

- livro sobre MCP **em português**;
- livro que cubra a revisão `2026-07-28` com certeza confirmada;
- livro acadêmico de referência sobre o protocolo.

---

## 2. Fundamentos de que o MCP depende

Estes **não** envelheceram, e explicam o MCP melhor que qualquer livro sobre MCP.

### 2.1 Protocolos e sistemas distribuídos

| Livro | Autor | Editora / ano | Por que ler | Gratuito? |
|---|---|---|---|---|
| **Designing Data-Intensive Applications** | Martin Kleppmann | O'Reilly, 2017 (**2ª ed. em preparação**) | Os capítulos sobre entrega de mensagem, idempotência e consistência explicam [60 §1](60-teoria-avancada.md) melhor que qualquer coisa. **Continua valendo integralmente** | não. Tradução PT-BR pela Novatec: *"Projetando Aplicações Intensivas em Dados"* — tradução boa |
| **Distributed Systems** (3ª ed.) | Maarten van Steen & Andrew Tanenbaum | os autores, 2017 | Referência acadêmica sólida sobre comunicação e coordenação | **Sim — os autores liberam o PDF** em [distributed-systems.net](https://www.distributed-systems.net/index.php/books/ds3/) |
| **Computer Networks** (6ª ed.) | Tanenbaum, Feamster & Wetherall | Pearson, 2021 | Base de HTTP, TLS, camadas. Tradução PT-BR *"Redes de Computadores"* pela Pearson | não |

### 2.2 Segurança

| Livro / documento | Autor | Ano | Por que ler | Gratuito? |
|---|---|---|---|---|
| **OAuth 2 in Action** | Justin Richer & Antonio Sanso | Manning, 2017 | O melhor livro didático de OAuth. Anterior ao OAuth 2.1, mas os conceitos e ataques (**inclusive o delegado confuso**) são os do [18](18-autorizacao.md) e do [19](19-seguranca.md) | não |
| **API Security in Action** | Neil Madden | Manning, 2020 | Token, audiência, escopo, capacidade — exatamente o vocabulário do MCP | não |
| **The Confused Deputy** | Norm Hardy | ACM OSR, 1988 | **4 páginas.** O artigo original. Leia antes de [19 §2](19-seguranca.md) | **sim**, amplamente disponível |
| **Programming Semantics for Multiprogrammed Computations** | Jack Dennis & Earl Van Horn | CACM, 1966 | A origem da segurança por capacidade | **sim**, na ACM DL e em espelhos |
| **Security Policies and Security Models** | Goguen & Meseguer | IEEE S&P, 1982 | Não interferência — o arcabouço de [60 §6.1](60-teoria-avancada.md) | **sim**, em espelhos |
| **Model Context Protocol (MCP): Security Design Considerations for AI-Driven Automation** | **NSA / AI Security Center** | **20/05/2026** | **A primeira orientação estatal sobre segurança de MCP.** Curta, densa, endereçada a quem opera em produção | **sim** — [NSA](https://www.nsa.gov/Press-Room/Press-Releases-Statements/Press-Release-View/Article/4496698/nsa-releases-security-design-considerations-for-ai-driven-automation-leveraging/) |

### 2.3 Projeto de API e de protocolo

| Livro | Autor | Editora / ano | Por que ler |
|---|---|---|---|
| **RESTful Web APIs** | Leonard Richardson & Mike Amundsen | O'Reilly, 2013 | Sobre **affordances** e descoberta — o problema que o MCP resolve com `tools/list` |
| **Release It!** (2ª ed.) | Michael Nygard | Pragmatic Bookshelf, 2018 | Timeout, disjuntor, degradação. Todo o [24](24-operacao-e-producao.md) sai daqui |
| **The Art of Unix Programming** | Eric S. Raymond | Addison-Wesley, 2003 | "Escreva programas que fazem uma coisa bem" e "texto é o formato universal" — os princípios de projeto nº 1 e 2 do MCP, escritos vinte anos antes | **sim**, [catb.org/~esr/writings/taoup/html/](http://www.catb.org/~esr/writings/taoup/html/) |

### 2.4 LLMs e agentes

| Recurso | Autor | Ano | Comentário |
|---|---|---|---|
| **Prompt Injection** (série de artigos) | Simon Willison | 2022–2026 | **Leitura essencial.** Willison cunhou o termo e documentou o problema desde o começo. Explica melhor que qualquer paper por que [60 §2](60-teoria-avancada.md) é um problema aberto. **Gratuito**, em [simonwillison.net/tags/prompt-injection/](https://simonwillison.net/tags/prompt-injection/) |
| **Language Server Protocol · Specification** | Microsoft | contínuo | O antepassado direto do MCP. Ler os dois lado a lado é o melhor exercício de projeto de protocolo que existe. **Gratuito**, em [microsoft.github.io/language-server-protocol](https://microsoft.github.io/language-server-protocol/) |
| **Building Effective Agents** | Anthropic (engenharia) | 2024 | Curto e prático sobre quando um agente é a escolha certa. **Gratuito** |

---

## 3. O que ler, na ordem, se você tem pouco tempo

| Se você tem… | Leia |
|---|---|
| **1 hora** | Este curso, arquivos [01](01-introducao-leigo.md) e [10](10-fundamentos.md) |
| **1 dia** | A [especificação `2026-07-28`](https://modelcontextprotocol.io/specification/2026-07-28) inteira. Ela é curta e é a fonte da verdade |
| **1 fim de semana** | \+ [Boas práticas de segurança do MCP](https://modelcontextprotocol.io/docs/2026-07-28/tutorials/security/security_best_practices) + a série de Simon Willison sobre injeção de prompt |
| **1 mês** | \+ um dos livros da §1.1 + Kleppmann (capítulos de mensageria) |
| **Quer profundidade real** | \+ Hardy (1988) + Dennis & Van Horn (1966) + a spec do LSP + os SEPs [2575](https://modelcontextprotocol.io/seps/2575-stateless-mcp) e [2322](https://modelcontextprotocol.io/seps/2322-MRTR) |

---

## 4. Nota sobre o campo acadêmico

Existe uma literatura crescente de **segurança de MCP** em pré-publicações (arXiv, 2025–2026):
taxonomias de ataque (*tool poisoning*, *shadowing*, *rug pull*, *line jumping*), análise
com taint em servidores, toolkits de análise, e trabalho sobre ocultação de metadados por
blocos TAG do Unicode.

**Duas ressalvas profissionais:**

1. **São pré-publicações.** Muitas não passaram por revisão por pares. A qualidade varia
   enormemente, e várias reembalam o mesmo conjunto de ataques já documentado pela
   Invariant Labs em abril de 2025.
2. **Não há ainda um artigo canônico sobre o protocolo em si.** O que existe de melhor é
   a própria especificação e os SEPs — que são, na prática, os documentos de projeto.

Se você for pesquisar, comece pelos **SEPs**: eles trazem motivação, alternativas
consideradas e decisão, que é exatamente o que um artigo de projeto teria.

---

## 5. Autoteste

1. Por que **todo** livro sobre MCP publicado antes de agosto de 2026 precisa de tradução mental?
2. Qual livro sobre MCP tem a melhor chance de cobrir a revisão atual, e por quê?
3. Existe livro sobre MCP em português? E cobrindo `2026-07-28`?
4. Qual documento de 4 páginas, de 1988, explica o ataque da seção 2 do arquivo 19?
5. Quais livros desta bibliografia são legalmente gratuitos? Cite ao menos três.
6. Que livro de 2003 antecipou os princípios de projeto nº 1 e 2 do MCP?
7. Por que a especificação é melhor que qualquer livro, hoje?
8. Qual foi a primeira orientação estatal sobre segurança de MCP, e de quando?
9. Que ressalvas fazer à literatura acadêmica atual sobre MCP?
10. Se você tem um dia, o que lê?

---

**Anterior:** [85 · Cursos e certificações](85-cursos-e-certificacoes.md) · **Próximo:** [95 · Referências](95-referencias.md) · **Índice:** [00-MAPA](00-MAPA.md)

*Edições, ISBNs e datas dos livros da §1.1 conferidos na web em 01/09/2026 (Packt, Apress/
Springer, O'Reilly, Amazon). Onde a confirmação não foi possível, o texto diz **não
confirmado**. Os livros da §2 são obras conhecidas, citadas por autor, título, editora e
ano; edições e traduções indicadas onde verificadas. Nenhum ISBN foi inferido.*
