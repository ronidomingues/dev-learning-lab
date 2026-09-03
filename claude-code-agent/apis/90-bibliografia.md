# 90 · Bibliografia comentada

`Nível: todos` · `Verificado em 11/08/2026`

Regra deste arquivo: **nada inventado**. Onde não tenho certeza de edição ou ISBN, cito só
autor e título e digo que é aproximado.

---

## 1. Aviso antes da lista

Três verdades sobre bibliografia de APIs:

1. **As fontes primárias são gratuitas e melhores que a maioria dos livros.** RFC 9110, a
   tese de Fielding e o OWASP API Top 10 estão em [95-referencias.md](95-referencias.md) e
   custam zero.
2. **Livros de "como fazer API com o framework X" envelhecem em 2–3 anos.** Livros de
   **princípios** envelhecem em décadas. Invista dinheiro nos segundos.
3. **Os melhores livros deste tema não são sobre APIs.** São sobre sistemas distribuídos e
   design de software — porque é aí que estão os problemas difíceis.

---

## 2. Design de API

### **Web API Design: The Missing Link** — Apigee / Google
*E-book gratuito · ~75 páginas*

**Nível:** iniciante → intermediário. **Envelheceu?** Pouco; os princípios seguem válidos.

Curto, direto e opinativo sobre nomenclatura, versionamento, paginação, erros e
parcialidade de resposta. **É gratuito e cabe numa tarde.** Se você for ler uma coisa só
sobre design de API, leia isto — depois da tese do Fielding.

### **Designing Web APIs** — Brenda Jin, Saurabh Sahni, Amir Shevat
*O'Reilly · 2018*

**Nível:** intermediário. **Envelheceu?** Parcialmente — anterior ao RFC 9457 e ao OpenAPI 3.1.

Escrito por gente que operou APIs em Slack, Google e Yahoo. Forte no que costuma faltar:
webhooks, escolha entre REST e GraphQL, versionamento, **e a experiência de quem consome a
sua API**. É o livro que mais fala de "API como produto".

### **API Design Patterns** — JJ Geewax
*Manning · 2021*

**Nível:** intermediário → avançado. **Envelheceu?** Pouco.

Catálogo de padrões com nome e justificativa: paginação, operações longas, importação e
exportação, versionamento, *singleton sub-resources*. O autor trabalhou no Google e o livro
reflete o rigor daquelas *design guidelines*. **É o mais completo da lista** e o que eu
recomendaria a quem projeta APIs profissionalmente.

### **Build APIs You Won't Hate** — Phil Sturgeon
*Independente · há uma segunda obra/edição mais recente; verifique*

**Nível:** intermediário. **Envelheceu?** A primeira edição, sim, em partes.

Prático, opinativo e engraçado. Forte em erros, paginação e nas decisões que causam
arrependimento. O autor é uma voz ativa na comunidade de APIs (APIs You Won't Hate) e no
IETF.

> **Nota de honestidade:** este título teve mais de uma edição/continuação ao longo dos anos
> e eu não tenho certeza de qual é a mais recente em 2026. Verifique antes de comprar.

### **RESTful Web APIs** — Leonard Richardson, Mike Amundsen, Sam Ruby
*O'Reilly · 2013*

**Nível:** intermediário → avançado. **Envelheceu?** Nas ferramentas, sim. Nos conceitos, não.

**É o livro que leva hipermídia a sério.** Richardson é o autor do modelo de maturidade.
Se você quer entender HATEOAS de verdade — e por que a maioria das APIs não o faz —, é aqui.
Aceite que várias tecnologias citadas não pegaram.

---

## 3. Sistemas distribuídos — os que mais importam

### **Designing Data-Intensive Applications** — Martin Kleppmann
*O'Reilly · 1ª ed. 2017* · *(uma 2ª edição está em preparação; confirme a disponibilidade)*

**Nível:** avançado. **Envelheceu?** Não.

**Se você só puder comprar um livro este ano, compre este.** Consistência, replicação,
particionamento, transações, idempotência, processamento de streams. É o que explica **por
que** as decisões de [60-teoria-avancada.md](60-teoria-avancada.md) são as únicas possíveis.
Não é sobre APIs, e é o livro mais importante para quem faz APIs.

### **Release It!** — Michael Nygard
*Pragmatic Bookshelf · 2ª ed. 2018*

**Nível:** intermediário → avançado. **Envelheceu?** Não.

Padrões de estabilidade: circuit breaker, bulkhead, timeout, *fail fast*, e os
**antipadrões** que derrubam sistemas. É a fonte dos padrões dos Exemplos 3 e 4 deste
material. Cheio de histórias reais de produção — o que o torna memorável.

### **Site Reliability Engineering** — Beyer, Jones, Petoff, Murphy (org.)
*O'Reilly · 2016 · **legalmente gratuito** em https://sre.google/books/*

**Nível:** intermediário → avançado. **Envelheceu?** Pouco.

SLI, SLO, error budget, alerta, postmortem sem culpa. Os capítulos sobre SLO e sobre
sobrecarga em cascata são diretamente aplicáveis a [18](18-operacao-e-ciclo-de-vida.md).
**Gratuito, online, completo.**

### **Microservices Patterns** — Chris Richardson
*Manning · 2018*

**Nível:** avançado. **Envelheceu?** Pouco.

Saga, transactional outbox, API composition, CQRS, API Gateway. É a referência dos padrões
de §7 de [60-teoria-avancada.md](60-teoria-avancada.md). Leia **depois** de decidir que
precisa de microsserviços, não antes.

### **Building Microservices** — Sam Newman
*O'Reilly · 2ª ed. 2021*

**Nível:** intermediário → avançado. **Envelheceu?** Não; a 2ª edição é bem atualizada.

Mais equilibrado que a média sobre **quando não usar** microsserviços. O capítulo sobre
comunicação entre serviços e o sobre decomposição valem sozinhos.

---

## 4. Segurança

### **The Web Application Hacker's Handbook** — Dafydd Stuttard, Marcus Pinto
*Wiley · 2ª ed. 2011*

**Nível:** avançado. **Envelheceu?** Parcialmente; as técnicas fundamentais, não.

O clássico de segurança web pela perspectiva do atacante. Anterior à era das APIs REST
modernas, mas os capítulos sobre autenticação, autorização e injeção continuam sendo a
melhor explicação disponível.

### **API Security in Action** — Neil Madden
*Manning · 2020*

**Nível:** avançado. **Envelheceu?** Pouco.

**O livro mais completo especificamente sobre segurança de API.** OAuth, JWT, mTLS,
capacidades, macaroons, autorização em microsserviços. Denso, prático e com código.

### **OWASP API Security Top 10** — OWASP
*Gratuito · edição 2023 · https://owasp.org/API-Security/*

**Nível:** todos. Curto, direto, com exemplo e defesa para cada risco. **Leia antes de
publicar qualquer API.**

---

## 5. Fundamentos que atravessam tudo

### **Refactoring** — Martin Fowler
*Addison-Wesley · 2ª ed. 2018 (exemplos em JavaScript)*

Não é sobre APIs, e é sobre a habilidade que você mais usa ao mantê-las.
**Há edição em português** (*Refatoração*, Bookman/Novatec — confirme a edição).

### **A Philosophy of Software Design** — John Ousterhout
*Yaknyam Press · 2ª ed. 2021*

**Nível:** intermediário. Curto (~190 páginas) e denso.

Sobre **profundidade de módulo** — interface pequena escondendo implementação grande. É
exatamente o critério para julgar uma API. O conceito de "*shallow module*" descreve com
precisão a API que espelha o banco.

### **Domain-Driven Design** — Eric Evans
*Addison-Wesley · 2003*

**Nível:** avançado. **Envelheceu?** O vocabulário, não. O livro é longo e difícil.

*Bounded context*, linguagem ubíqua, *aggregate*. É a base teórica de "modele o domínio,
não a tabela" ([14-design-de-api-rest.md](14-design-de-api-rest.md) §3).

> **Alternativa mais curta:** *Domain-Driven Design Distilled*, do Vaughn Vernon (2016), dá
> 80% do valor em 20% das páginas.

---

## 6. Artigos e papers essenciais — todos gratuitos

| Trabalho | Ano | Por que ler |
|---|---|---|
| **Fielding — tese, cap. 5** | 2000 | a definição de REST, ~30 páginas |
| **Fielding — *REST APIs must be hypertext-driven*** | 2008 | o protesto contra o uso do termo |
| **Waldo et al. — *A Note on Distributed Computing*** | 1994 | por que chamada remota ≠ chamada local |
| **Parnas — *On the Criteria...*** | 1972 | a origem intelectual de "esconda o que muda" |
| **Fischer, Lynch, Paterson — FLP** | 1985 | a impossibilidade do consenso assíncrono |
| **Gilbert & Lynch — CAP formalizado** | 2002 | o teorema, com rigor |
| **Abadi — PACELC** | 2012 | o que falta no CAP |
| **Liskov & Wing — subtipagem comportamental** | 1994 | a base de compatibilidade de contratos |

**Todos disponíveis gratuitamente.** Links em [95-referencias.md](95-referencias.md).

---

## 7. Legalmente gratuitos

| Título | Onde |
|---|---|
| **Site Reliability Engineering** e ***The SRE Workbook*** | https://sre.google/books/ |
| **Web API Design** (Apigee) | busque pelo título; distribuído pelo Google/Apigee |
| **RFCs** (todos) | https://www.rfc-editor.org/ |
| **Tese de Fielding** | https://ics.uci.edu/~fielding/pubs/dissertation/ |
| **OWASP** (todo o material) | https://owasp.org |
| **Zalando / Google / Microsoft API Guidelines** | ver [95-referencias.md](95-referencias.md) |
| **HTTP Archive Web Almanac** | https://almanac.httparchive.org |

**Esses sete recursos, somados, cobrem mais que qualquer livro pago da lista.**
Comece por eles.

---

## 8. Em português

O mercado editorial brasileiro **publica pouco** sobre design de API especificamente. Não
conheço um livro técnico em português sobre design de API que eu recomende com segurança —
e prefiro dizer isso a inventar um título.

**O que existe e vale, em português:**
- **MDN Web Docs (HTTP)**, traduzido e mantido — a melhor referência gratuita;
- traduções de clássicos de engenharia de software: *Refatoração* (Fowler), *Padrões de
  Projeto* (GoF, Bookman), *Código Limpo* (Martin), *Arquitetura Limpa* (Martin);
- **Casa do Código** e **Novatec** publicam sobre desenvolvimento web e back-end, com
  material sobre APIs dentro de livros de framework.

> **Sobre traduções:** edições da Bookman e da Novatec costumam ter qualidade aceitável.
> Ainda assim, se você lê inglês com conforto, prefira o original — a terminologia técnica
> traduzida frequentemente diverge do que a comunidade usa no dia a dia, e isso atrapalha
> na hora de buscar ajuda.

---

## 9. Como escolher

| Você quer | Leia |
|---|---|
| Entender REST de verdade | **Fielding, cap. 5** (gratuito) |
| Projetar uma API bem | **Geewax, *API Design Patterns*** |
| Um resumo curto e gratuito de design | **Apigee, *Web API Design*** |
| Entender por que integração é difícil | **Kleppmann** |
| Que a sua API não caia | **Nygard, *Release It!*** |
| Definir SLO e operar | **SRE Book** (gratuito) |
| Não ser hackeado | **OWASP** (gratuito) + **Madden** |
| Melhorar como projetista | **Ousterhout** |
| Referência do dia a dia | **RFC 9110** e **MDN** |

---

## Autoteste

1. Por que as fontes primárias superam a maioria dos livros neste assunto?
2. Qual livro você compraria se pudesse comprar só um, e por quê ele não é sobre APIs?
3. Qual é o livro mais completo especificamente sobre design de API?
4. Qual livro leva hipermídia a sério, e quem o escreveu?
5. Cite três recursos legalmente gratuitos que equivalem a livros.
6. Qual é a situação da bibliografia em português, e o que fazer?
7. Que critério distingue livro que envelhece em 2 anos de livro que envelhece em décadas?
