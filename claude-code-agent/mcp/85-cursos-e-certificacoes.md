# 85 · Cursos e certificações

`Nível: todos` · **Pesquisado na web em 01/09/2026** · **Este arquivo envelhece: reconfira links e anos**

> Como ler as tabelas: **"Grátis de verdade"** = assistir **e** certificar sem pagar.
> **"Grátis para assistir"** = o conteúdo é aberto, o certificado é pago.
> Preços e disponibilidade mudam; o ano de publicação está marcado porque MCP mudou
> muito — material anterior a **julho de 2026** ensina o protocolo **com sessão e com
> `initialize`**, que **não existem mais**.

---

## ⚠️ Aviso que vale mais que qualquer link

A revisão **`2026-07-28`** removeu sessões, o handshake `initialize` e as requisições
iniciadas pelo servidor. **Praticamente todo curso publicado antes de agosto de 2026
ensina um protocolo que mudou.** Os conceitos (papéis, primitivas, capacidades, JSON-RPC)
continuam válidos; a **mecânica** não.

Ao assistir material de 2025 ou do primeiro semestre de 2026, faça a tradução:

| O curso ensina | Hoje é |
|---|---|
| `initialize` + `notifications/initialized` | **removido** → `_meta` por requisição + `server/discover` |
| `Mcp-Session-Id` | **removido** → handles explícitos |
| servidor manda `elicitation/create` | **MRTR** → `InputRequiredResult` |
| `GET` para fluxo SSE | **removido** → `subscriptions/listen` |
| `resources/subscribe` | **removido** → filtro em `subscriptions/listen` |
| `FastMCP` (Python) | `MCPServer` (SDK 2.x) |
| `@modelcontextprotocol/sdk` (TS) | `@modelcontextprotocol/server` + `/client` |

Mantenha [17 · Versionamento](17-versionamento-e-compatibilidade.md) aberto ao lado.

---

## 1. Português — Brasil e Portugal

### 1.1 Vídeo gratuito

| Título | Autor / plataforma | Link | Duração | Nível | Ano | Vale o tempo? |
|---|---|---|---|---|---|---|
| **Model Context Protocol: Guia que todo Dev precisa saber** | YouTube | [assistir](https://www.youtube.com/watch?v=gc9MEMdOZxM) | ~vídeo único | iniciante | 2025 | **Sim, para a intuição.** Teoria + prática de servidores MCP. Ignore a mecânica de handshake |
| **MCP — Guia Definitivo para Iniciantes (exemplos práticos)** | YouTube | [assistir](https://www.youtube.com/watch?v=pBL3qOY2_Jw) | ~vídeo único | iniciante | 2025 | **Sim, para o primeiro servidor.** Constrói dois MCPs do zero, passo a passo |

> **Observação honesta.** O material em vídeo **em português** sobre MCP é escasso,
> raso e majoritariamente de 2025. Não há, até 01/09/2026, um curso em vídeo em português
> que cubra a revisão `2026-07-28`. **A recomendação profissional é: use o português para
> a intuição inicial e vá para o inglês para a profundidade.** Este curso que você está
> lendo existe em parte por causa dessa lacuna.

### 1.2 Texto gratuito, em português

| Título | Autor / plataforma | Link | Nível | Ano | Comentário |
|---|---|---|---|---|---|
| **Model Context Protocol (MCP): o guia definitivo do "conector universal" da IA** | Alura (artigo) | [ler](https://www.alura.com.br/artigos/model-context-protocol-mcp) | iniciante | 2026 | Boa introdução conceitual, em bom português técnico |
| **MCP: o que é, como funciona e principais diferenças** | Alura (artigo) | [ler](https://www.alura.com.br/artigos/mcp-o-que-e) | iniciante | 2026 | Complementa o anterior; foco em comparações |
| **MCP Model Context Protocol: tutorial completo para desenvolvedores** | CrazyStack | [ler](https://www.crazystack.com.br/mcp-model-context-protocol-explicado-desenvolvedores-leigos) | iniciante–intermediário | 2025–2026 | Tutorial em texto, com código |

### 1.3 Pago, em português

| Título | Plataforma | Modelo | Comentário |
|---|---|---|---|
| **Model Context Protocol (MCP)** | [Alura](https://www.alura.com.br/curso-online-model-context-protocol) | assinatura | Arquitetura e funcionamento, servidor e cliente, e construção visual com **n8n**. Bom se você já paga Alura |
| **MCP: otimização de agentes de IA com n8n** | Alura | assinatura | Low-code; ver [n8n](../n8n/00-MAPA.md) |
| **Engenharia de software na era da IA: MCP servers, tools e integrações** | Alura | assinatura | Node.js e TypeScript |
| **Curso Completo MCP — Aprende Model Context Protocol en 1 Día** | [Udemy](https://www.udemy.com/course/curso-completo-mcp-aprende-model-context-protocol/) | compra avulsa (espanhol) | Espanhol, não português. Útil se você lê espanhol |

---

## 2. Inglês

### 2.1 Grátis de verdade (assistir **e** certificar)

| Título | Instituição | Link | Duração | Nível | Ano | Certificado |
|---|---|---|---|---|---|---|
| **Introduction to Model Context Protocol** | **Anthropic Academy** | [anthropic.skilljar.com](https://anthropic.skilljar.com/introduction-to-model-context-protocol) | curto, autoguiado | iniciante–intermediário | 2026 | **Sim, oficial da Anthropic** |
| **Model Context Protocol: Advanced Topics** | **Anthropic Academy** | [anthropic.skilljar.com](https://anthropic.skilljar.com/model-context-protocol-advanced-topics) | autoguiado | avançado | 2026 | **Sim** |
| **MCP Course** | **Hugging Face** (em parceria com a **Anthropic**) | [huggingface.co/learn/mcp-course](https://huggingface.co/learn/mcp-course/unit0/introduction) | 5 capítulos, ~3–4 h/semana | iniciante–intermediário | 2025–2026 | **Sim, dois: fundamentos (Unidade 1) e conclusão (Unidades 2 e 3)** |
| **MCP for Beginners** | **Microsoft** | [github.com/microsoft/mcp-for-beginners](https://github.com/microsoft/mcp-for-beginners/) | currículo longo | iniciante–avançado | 2025–2026 | não emite, mas é o mais completo |

**Comentários francos:**

- **Anthropic Academy** (lançada em 02/03/2026, na plataforma Skilljar): é a fonte mais
  próxima de "oficial". Ensina servidores e clientes em Python e cobre as três primitivas
  com a distinção certa de **quem controla cada uma** — que é justamente o que a maioria
  dos tutoriais erra. Não exige conta Anthropic: basta um e-mail. Certificado emitido pela
  Skilljar, publicável no LinkedIn.
- **Hugging Face MCP Course**: cinco capítulos (Onboarding, Fundamentos, Caso de uso
  ponta a ponta, Caso de uso implantado, Bônus), com exercícios práticos em servidor
  hospedado. **Gratuito, certificação incluída.** Pré-requisitos: noção de LLM e agentes,
  familiaridade com desenvolvimento e APIs, uma linguagem de programação. Exemplos em
  Python e TypeScript. Parceiros: Anthropic, Gradio, Continue, Llama.cpp.
- **Microsoft MCP for Beginners**: **o maior currículo gratuito** e o único que não se
  prende a Python ou JavaScript — traz exemplos em .NET, Java, TypeScript, JavaScript,
  Rust e Python. Licença MIT, aberto a contribuições. O projeto final constrói um servidor
  PostgreSQL ao longo de 13 laboratórios, tratado como uma equipe de produção trataria.
  **É a minha recomendação para quem quer profundidade e tem tempo.**

### 2.2 Grátis para assistir

| Título | Instituição | Link | Duração | Nível | Ano | Observação |
|---|---|---|---|---|---|---|
| **MCP: Build Rich-Context AI Apps with Anthropic** | **DeepLearning.AI**, com Elie Schoppik (Anthropic) | [deeplearning.ai](https://www.deeplearning.ai/courses/mcp-build-rich-context-ai-apps-with-anthropic) | ~1 h 48 min, 11 aulas, 6 exemplos de código | iniciante–intermediário | 2025 | **Gratuito durante o beta da plataforma.** Sem certificado; só Python; não cobre padrões de produção. Quase todo o tempo é construindo — é o melhor uso de duas horas da lista |
| **Documentação oficial** | modelcontextprotocol.io | [docs](https://modelcontextprotocol.io/docs/2026-07-28/getting-started/intro) | — | todos | **2026** | **A única fonte garantidamente atualizada.** Tem trilha de aprendizado, guias de servidor e cliente, e tutoriais de segurança |
| **Introduction to Model Context Protocol** | Coursera | [coursera.org](https://www.coursera.org/learn/introduction-to-model-context-protocol) | curso curto | iniciante | 2026 | Gratuito para assistir; certificado pago |
| **Playlist MCP End-To-End Course 2026** | YouTube | [playlist](https://www.youtube.com/playlist?list=PL6tW9BrhiPTCDteflzehKS6Cn3a79-iCs) | série | iniciante–intermediário | 2026 | Qualidade variável; confira a data de cada vídeo |
| **Intro to MCP Servers — MCP with Python** | YouTube | [assistir](https://www.youtube.com/watch?v=DosHnyq78xY) | ~curso curto | iniciante | 2025 | Usa `FastMCP`, que virou `MCPServer` no SDK 2.x |

### 2.3 Agregadores

- **Class Central** — [lista de cursos de MCP](https://www.classcentral.com/subject/model-context-protocol),
  com centenas de itens de qualidade muito desigual. Útil para descobrir, ruim para escolher.
- **Class Central · 9 Best MCP Courses for 2026** — [lista curada](https://www.classcentral.com/report/best-mcp-courses/).
- **Scrimba · Best MCP Courses and Tutorials 2026** — [lista](https://scrimba.com/articles/best-mcp-tutorials-and-courses/).

---

## 3. Francês

| Título | Autor / plataforma | Link | Tipo | Nível | Ano | Comentário |
|---|---|---|---|---|---|---|
| **Comment créer un serveur MCP ?** | **Grafikart** | [vídeo](https://www.youtube.com/watch?v=SiPGgGoMNYg) · [artigo](https://grafikart.fr/tutoriels/mcp-ia-serveur-2292) | vídeo + texto, **gratuito** | iniciante–intermediário | 01/08/2025 | **A melhor referência gratuita em francês.** Grafikart é uma das fontes técnicas mais respeitadas em francês. Constrói um servidor MCP; o exemplo é em PHP/Laravel, o que é raro e interessante |
| **MCP (Model Context Protocol) — Guide Complet en Français** | Cours et Fiches | [ler](https://cours-et-fiches.com/programmation/mcp-protocol/) | texto, gratuito | iniciante | 2025–2026 | Guia de conceitos, em bom francês técnico |
| **MCP IA : le guide complet 2026** | Shubham Sharma | [ler](https://shubham-sharma.fr/articles/comprendre-mcp-protocol-ia/) | texto, gratuito | iniciante | 2026 | Panorama |
| **Tout savoir sur les MCP** | Florence Chatelot | [ler](https://florence-chatelot.fr/tout-savoir-sur-les-mcp-model-contexte-protocol/) | texto, gratuito | iniciante | 2025–2026 | Introdução conceitual |
| **Maîtrisez MCP : Contexte IA & Développement de Serveurs** | Udemy | [ver](https://www.udemy.com/course/maitrisez-mcp-model-context-protocol-ia-developpement-de-serveurs-mcp/) | **pago** | intermediário | 2025 | Servidores MCP em TypeScript com o SDK oficial |
| **Formation MCP** | Formation Facile (Anthony Cardinale) | [ver](https://www.formation-facile.fr/cours/mcp) | **pago** | intermediário–avançado | 2025–2026 | ~4 h, com certificado |
| **Formation MCP** | M2i Formation | [ver](https://www.m2iformation.fr/formation-mcp-model-context-protocol-connecter-et-controler-des-applications-et-des-donnees-a-partir-de-llm/IA-MCP/) | **pago**, presencial/à distância | profissional | 2025–2026 | Formação profissional francesa, com orçamento |

> **Avaliação honesta do material francês:** o Grafikart é excelente e gratuito, mas é um
> tutorial, não um curso. O restante gratuito é conceitual. **Não existe, em 01/09/2026,
> um curso em vídeo gratuito em francês que cubra o MCP em profundidade.**

---

## 4. Certificações

### 4.1 O que existe

| Emissor | Certificado | Custo | Exigência | Vale no mercado? |
|---|---|---|---|---|
| **Anthropic Academy** | conclusão de curso (Skilljar) | **grátis** | concluir o curso | **É o mais próximo de "oficial"**, por vir de quem criou o protocolo. Publicável no LinkedIn. É um certificado de conclusão, não um exame |
| **Hugging Face** | fundamentos (Un. 1) e conclusão (Un. 2–3) | **grátis** | concluir as unidades e os exercícios | Reconhecimento razoável na comunidade de IA. Exige entrega prática, o que vale mais que assistir |
| **Coursera / Udemy** | conclusão | pago | concluir | Baixo. Certificado de conclusão de plataforma |
| **Microsoft (MCP for Beginners)** | **não emite** | grátis | — | **O currículo vale mais que o certificado que ele não dá** |

### 4.2 Não existe certificação oficial do protocolo

Ponto importante e frequentemente confundido: **não há, em 01/09/2026, uma certificação
do MCP emitida pela Agentic AI Foundation ou pela Linux Foundation.** O que existe é:

- certificados de **conclusão de curso** (Anthropic, Hugging Face, plataformas);
- um **sistema de tiers para SDKs** — que classifica *implementações*, não pessoas;
- uma **suíte de testes de conformidade** para SDKs, mencionada no roadmap — de novo,
  para código, não para gente.

⚠️ **Cuidado com propaganda.** Circulam listas de "melhores certificações MCP para 2026"
em blogs de produto. Elas misturam certificado de conclusão de curso com certificação
profissional. **Nenhum certificado de MCP hoje tem valor de mercado comparável ao de,
digamos, uma AWS Solutions Architect.**

### 4.3 Opinião profissional sobre certificados

O que realmente convence alguém a te contratar para trabalhar com MCP, em ordem:

1. **Um servidor MCP público que você escreveu**, com testes, tratamento de erro e
   descrições bem feitas. Um repositório vale mais que qualquer certificado.
2. **Ter publicado no MCP Registry** sob namespace verificado.
3. **Saber explicar por que o protocolo virou sem estado em 2026** — separa quem entendeu
   de quem decorou.
4. **Saber discutir segurança** (tool poisoning, validação de audiência, token passthrough)
   com honestidade sobre o que não tem solução.
5. Só então, um certificado.

Se você tem 20 horas, use 4 num curso e 16 escrevendo um servidor de verdade.

---

## 5. Documentação e fontes primárias

Nada substitui:

| Recurso | Link | Para quê |
|---|---|---|
| **Especificação `2026-07-28`** | [spec](https://modelcontextprotocol.io/specification/2026-07-28) | a fonte da verdade |
| **Changelog** | [key changes](https://modelcontextprotocol.io/specification/2026-07-28/changelog) | o que mudou e por quê |
| **Guias de desenvolvimento** | [docs](https://modelcontextprotocol.io/docs/2026-07-28/develop/build-server) | construir servidor e cliente |
| **Boas práticas de segurança** | [security](https://modelcontextprotocol.io/docs/2026-07-28/tutorials/security/security_best_practices) | **leitura obrigatória** |
| **Blog oficial** | [blog](https://blog.modelcontextprotocol.io/) | releases e decisões |
| **Roadmap** | [roadmap](https://modelcontextprotocol.io/development/roadmap) | para onde vai |
| **SEPs** | [seps](https://modelcontextprotocol.io/seps/index) | o **porquê** de cada decisão |
| **Servidores de referência** | [github](https://github.com/modelcontextprotocol/servers) | ler código real |
| **Documentação dos SDKs** | [py](https://py.sdk.modelcontextprotocol.io) · [ts](https://ts.sdk.modelcontextprotocol.io) | API |

---

## 6. Trilha sugerida — 6 semanas, ~6 h/semana

| Semana | O quê | Fonte |
|---|---|---|
| **1** | Conceito e primeiro servidor | [01](01-introducao-leigo.md), [03](03-instalacao.md), [04](04-como-comecar.md) + **Anthropic Academy · Introduction** |
| **2** | Fundamentos e a fita JSON-RPC | [10](10-fundamentos.md), [12](12-arquitetura.md), [13](13-json-rpc-e-a-camada-base.md) + **Labs 1–4** de [70](70-pratica.md) |
| **3** | Primitivas e projeto de ferramentas | [15](15-primitivas-do-servidor.md), [23](23-projeto-de-ferramentas.md), [06](06-exemplos.md) + **Hugging Face, Unidade 1** |
| **4** | Projeto de verdade | [07 · projeto-modelo](07-projeto-modelo/README.md) + **Labs 5–8** + **Microsoft MCP for Beginners** (labs) |
| **5** | Transporte remoto e segurança | [14](14-transportes.md), [19](19-seguranca.md), [18](18-autorizacao.md) + **Labs 9, 12** |
| **6** | Produção e fronteira | [24](24-operacao-e-producao.md), [65](65-estado-da-arte.md) + **Anthropic Academy · Advanced Topics** + publicar no registry ([21](21-registro-e-distribuicao.md)) |

---

## 7. Autoteste

1. Por que material anterior a agosto de 2026 ensina uma mecânica que não existe mais? Cite três diferenças.
2. Quais cursos são **grátis de verdade**, com certificado incluso?
3. Qual é o maior currículo gratuito, e o que ele tem que os outros não têm?
4. Existe certificação oficial do MCP emitida pela Linux Foundation? O que existe, então?
5. Qual a melhor fonte gratuita em francês, e por que ela é interessante tecnicamente?
6. Qual é a lacuna mais evidente no material em português?
7. O que convence mais um empregador que um certificado? Cite os três primeiros itens.
8. Onde você encontra o **porquê** de cada decisão do protocolo?
9. Se você tem 20 horas, como distribuí-las?
10. Que armadilha existe nas listas de "melhores certificações MCP" publicadas em blogs?

---

**Anterior:** [80 · Custos e licenças](80-custos-e-licencas.md) · **Próximo:** [90 · Bibliografia](90-bibliografia.md) · **Índice:** [00-MAPA](00-MAPA.md)

*Todos os cursos, links, durações e modelos de certificação foram **pesquisados na web em
01/09/2026** e refletem o que estava publicado nessa data. Anos de publicação estão
marcados quando conhecidos. Links de vídeo e de plataforma podem expirar. As avaliações
("vale o tempo?") são opinião profissional deste material.*
