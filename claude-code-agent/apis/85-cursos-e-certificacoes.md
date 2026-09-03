# 85 · Cursos gratuitos e certificações

`Nível: todos` · **`Pesquisado na web em 11/08/2026`**

> ⚠️ Links de curso expiram e canais param de publicar. Tudo aqui foi verificado em
> **11/08/2026**. Se um link morrer, procure pelo título.

---

## 1. A informação mais importante deste arquivo

**Praticamente não existe certificação relevante em "APIs".**

Diferente de nuvem (AWS, Azure), Kubernetes (CKA) ou Salesforce, o mundo de APIs
**não tem** uma certificação que o mercado reconheça amplamente. O que existe é:

| Existe | Vale? |
|---|---|
| Certificados de conclusão de MOOC (Coursera, Udemy) | 🟡 sinalizam esforço; não são credenciais |
| Certificações de **fornecedor** (Postman, Apigee, MuleSoft, Kong) | 🟡 valem **dentro** daquele ecossistema |
| Certificações adjacentes (AWS, Azure, CKA, segurança) | ✅ têm valor de mercado |
| Uma "certificação REST" reconhecida | ❌ **não existe** |

> **A consequência prática, e é uma boa notícia:** neste assunto, **portfólio vale mais que
> certificado**, e a diferença é grande. Uma API pública sua, no GitHub, com contrato
> OpenAPI, testes e um README bom, demonstra mais do que qualquer certificado — e você a
> constrói fazendo o [70-pratica.md](70-pratica.md). Invista aí.

---

## 2. Fontes primárias — comece por elas

Nenhum curso supera as especificações, e elas são gratuitas.

| Fonte | Por que |
|---|---|
| **RFC 9110 — HTTP Semantics** — https://www.rfc-editor.org/rfc/rfc9110.html | a referência definitiva de métodos, status e cabeçalhos. **Se ler um só, leia este** |
| **RFC 9111 — HTTP Caching** | o cache que quase ninguém usa direito |
| **RFC 9457 — Problem Details** | erros padronizados, em 15 páginas |
| **MDN Web Docs (HTTP)** — https://developer.mozilla.org/pt-BR/docs/Web/HTTP | **em português**, excelente, prático |
| **Tese de Fielding, cap. 5** — https://ics.uci.edu/~fielding/pubs/dissertation/rest_arch_style.htm | ~30 páginas; a definição de REST |
| **OpenAPI Specification** — https://spec.openapis.org | o contrato |
| **OWASP API Security Top 10** — https://owasp.org/API-Security/ | os riscos reais, com exemplos |

> **RFC assusta e não deveria.** O RFC 9110 é bem escrito, organizado por tópico e mais
> claro que a maioria dos tutoriais. Leia a seção sobre métodos (§9) e a de status (§15) —
> são as duas mais úteis, e juntas dão umas 40 páginas.

---

## 3. Cursos gratuitos em **português**

### 3.1 Documentação e material de referência

| Recurso | Onde | Nota |
|---|---|---|
| **MDN Web Docs — HTTP, em pt-BR** | https://developer.mozilla.org/pt-BR/docs/Web/HTTP | **a melhor referência gratuita em português** sobre HTTP. Tradução boa e mantida |
| MDN — *Introdução ao HTTP* | https://developer.mozilla.org/pt-BR/docs/Web/HTTP/Overview | ponto de partida |
| **JSON, em português** | https://www.json.org/json-pt.html | o formato inteiro em meia página |

### 3.2 Cursos em vídeo

| Recurso | Onde | Formato | Nota |
|---|---|---|---|
| **Curso API REST Completo — iniciante** | YouTube — busque *"Curso API REST completo grátis iniciante"* | vídeo + desafios | há uma versão bastante difundida (publicada em 2022); **confira a data**, pois material anterior a 2023 não cobre RFC 9457 nem OpenAPI 3.1 |
| **Curso de FastAPI — REST API com Python** | YouTube (playlist) | vídeo | construção prática com Python; bom se você prefere Python a Node |
| **Testes de API REST** | YouTube (playlist com ~20 aulas) | vídeo | foco em teste e Postman; útil para QA |
| **Jornada do Dev — REST API** | https://jornadadodev.com.br/cursos/back-end/rest-api | texto/vídeo | trilha de back-end, do básico a autenticação |
| **Cursa — Testes de API Rest** | https://cursa.com.br | vídeo | gratuito, com certificado de conclusão |

### 3.3 O panorama honesto do português

O material em português é **fragmentado e mais raso** que o em inglês, e concentrado em
"como construir uma API com o framework X" — não em **design, contrato, evolução e
segurança**, que é onde está a dificuldade real.

> **Recomendação, com franqueza:** use a **MDN em português** como base de HTTP, e este
> material como o curso estruturado. Para os temas avançados (contrato, evolução, segurança,
> teoria), você **vai precisar** de inglês. Não existe, em agosto de 2026, um equivalente em
> português ao que o Fielding, o OWASP e os RFCs oferecem.
>
> Se o inglês for barreira: leia os RFCs com tradutor de página. O vocabulário é repetitivo
> e você se acostuma em duas semanas.

---

## 4. Cursos gratuitos em **inglês**

| Recurso | Onde | Formato | Por que vale |
|---|---|---|---|
| **MDN Web Docs — HTTP** | https://developer.mozilla.org/en-US/docs/Web/HTTP | texto | a referência prática |
| **freeCodeCamp** | https://www.freecodecamp.org · YouTube | curso longo, texto+vídeo | cursos de várias horas sobre APIs REST, gratuitos e completos |
| **Postman Learning Center** | https://learning.postman.com | texto+vídeo | ótimo em fundamentos de consumo e teste, mesmo se você não usar Postman |
| **Apigee — *Web API Design*** (e-book) | Google/Apigee | e-book gratuito | **um dos melhores textos curtos sobre design de API** que existem |
| **Zalando RESTful API Guidelines** | https://opensource.zalando.com/restful-api-guidelines/ | texto | **guia de estilo real de uma empresa grande**, público e detalhado. Leitura obrigatória |
| **Google API Design Guide** | https://cloud.google.com/apis/design | texto | como o Google projeta APIs; opinativo e fundamentado |
| **Microsoft REST API Guidelines** | https://github.com/microsoft/api-guidelines | texto | outra referência corporativa aberta |
| **OWASP API Security Top 10** | https://owasp.org/API-Security/ | texto | os riscos, com exemplos e defesas |
| **web.dev / HTTP Archive Web Almanac** | https://almanac.httparchive.org | relatório anual | dados reais de adoção de HTTP |
| **GraphQL — tutorial oficial** | https://graphql.org/learn/ | texto | se for usar GraphQL |
| **gRPC — documentação e quickstarts** | https://grpc.io/docs/ | texto+código | idem para gRPC |

> **Os três guias corporativos (Zalando, Google, Microsoft) são o recurso mais subestimado
> desta lista.** Eles mostram decisões reais, com justificativa, tomadas por times que
> mantêm APIs em escala há anos. Valem mais que a maioria dos cursos pagos, e são gratuitos.

---

## 5. Cursos gratuitos em **francês**

| Recurso | Onde | Nota |
|---|---|---|
| **OpenClassrooms — *Adoptez les API REST pour vos projets web*** | https://openclassrooms.com/fr/courses/6573181-adoptez-les-api-rest-pour-vos-projets-web | curso estruturado e completo. **Gratuito para assistir** com conta; o certificado é pago |
| **OpenClassrooms — *Débutez avec les API REST*** | https://openclassrooms.com/us/courses/6031886-debutez-avec-les-api-rest | introdução |
| **MDN em francês** | https://developer.mozilla.org/fr/docs/Web/HTTP | mesma qualidade da versão inglesa |
| **MOOC Francophone** | https://mooc-francophone.com | agrega cursos francófonos gratuitos |
| **Grafikart** | https://grafikart.fr | canal francês consistente de desenvolvimento web, com conteúdo sobre API |

> **O OpenClassrooms é o melhor material estruturado em francês** sobre APIs REST. O modelo
> é "gratuito para estudar, pago para certificar" — e, dado que a certificação não vale
> muito neste assunto (§1), estudar de graça é a escolha racional.

---

## 6. Certificações — o mapa honesto

### 6.1 De fornecedor

| Certificação | Emissor | Custo aproximado | Vale? |
|---|---|---|---|
| **Postman API Fundamentals Student Expert** | Postman | **gratuito** | 🟡 bom como primeiro marco; reconhecimento limitado |
| **Postman — trilhas de certificação** | Postman | gratuito a baixo | 🟡 útil se o time usa Postman |
| **Google Cloud — Apigee API Engineer** | Google | pago | ✅ **dentro** do ecossistema Apigee |
| **MuleSoft Certified Developer** | Salesforce/MuleSoft | pago | ✅ vale muito **em vagas de MuleSoft** |
| **Kong Certified Developer / Administrator** | Kong | pago | 🟡 nicho |
| **Tyk, WSO2 e outros** | fornecedor | varia | 🟡 nicho |

**A regra:** certificação de fornecedor vale **se** você trabalha (ou quer trabalhar) com
aquele fornecedor. Fora disso, o retorno é baixo.

### 6.2 Adjacentes que valem mais

Se o seu objetivo é empregabilidade, estas têm reconhecimento real e cobrem APIs como parte:

| Certificação | Por que ajuda |
|---|---|
| **AWS Solutions Architect Associate** | cobre API Gateway, Lambda, integração |
| **Azure Developer Associate (AZ-204)** | cobre API Management |
| **CKA / CKAD** (Kubernetes) | onde APIs rodam |
| **CompTIA Security+ / OSCP** | segurança, incluindo web e API |
| **Certificações de Kafka / Confluent** | arquitetura orientada a eventos |

### 6.3 O que realmente demonstra competência

Em ordem de peso, na minha experiência avaliando pessoas:

1. **Uma API pública sua**, com contrato OpenAPI, testes, tratamento de erro e README bom.
2. **Contribuição a projeto aberto** relacionado (uma correção num cliente, um exemplo, uma
   melhoria de documentação).
3. **Um texto seu** explicando uma decisão de design de API que você tomou e por quê.
4. **Saber responder ao vivo:** "por que 401 e não 403 aqui?", "como você garante que esse
   POST não duplica?", "essa mudança quebra clientes?".
5. Certificados de MOOC.

> **O item 4 é o filtro real em entrevista técnica.** As perguntas deste material —
> especialmente os autotestes de [13](13-rest-e-restful.md), [14](14-design-de-api-rest.md),
> [16](16-seguranca.md) e [19](19-como-escolher.md) — são literalmente as perguntas que se
> faz. Treine respondê-las em voz alta.

---

## 7. Roteiro de estudo

### Trilha "consumir APIs" — 3 a 4 semanas, ~8 h/semana

| Semana | O quê |
|---|---|
| 1 | [01](01-introducao-leigo.md), [03](03-instalacao.md), [04](04-como-comecar.md) + MDN HTTP (visão geral) + **Lab 1** |
| 2 | [12-http-por-dentro.md](12-http-por-dentro.md) + [05](05-manual-de-uso.md) + **Lab 3** |
| 3 | [13](13-rest-e-restful.md), [19](19-como-escolher.md) + **Lab 2** |
| 4 | [16-seguranca.md](16-seguranca.md) §1–3 + [75](75-armadilhas.md) + revisão |

### Trilha "construir APIs" — 3 meses, ~10 h/semana

| Mês | O quê |
|---|---|
| 1 | Tudo da trilha de consumo + [10](10-fundamentos.md) + [14](14-design-de-api-rest.md) + **Lab 4** |
| 2 | [17](17-contratos-e-documentacao.md) + [16](16-seguranca.md) completo + **Labs 5, 6 e 7** + [07-projeto-modelo/](07-projeto-modelo/README.md) |
| 3 | [15](15-estilos-e-protocolos.md) + [18](18-operacao-e-ciclo-de-vida.md) + **Labs 8, 9 e 10** + **projeto final** |

### Trilha "arquitetura" — some ao acima

[11](11-historia.md) → [60](60-teoria-avancada.md) → [65](65-estado-da-arte.md) →
Zalando/Google guidelines → *Designing Data-Intensive Applications*.

---

## 8. Comunidades

| Onde | O quê |
|---|---|
| **Stack Overflow** | perguntas técnicas pontuais |
| **APIs You Won't Hate** — https://apisyouwonthate.com | comunidade e conteúdo de design de API |
| **r/webdev**, **r/api** (Reddit) | discussão prática |
| **OpenAPI Initiative (Slack/GitHub)** | discussões da especificação |
| **OWASP** (capítulos locais, inclusive no Brasil) | segurança |
| **Comunidades brasileiras** (Discord, Telegram) de back-end e de cada linguagem | dúvida em português |
| **IETF HTTP Working Group** (lista pública) | onde o HTTP é decidido; leitura, não participação |

---

## Autoteste

1. Por que praticamente não existe certificação relevante em APIs? O que isso implica para você?
2. Qual é o único RFC que você leria se pudesse ler só um? Quais seções?
3. Qual é a melhor referência gratuita de HTTP em português?
4. Qual é o panorama honesto do material em português, e o que fazer a respeito?
5. Por que os guias de Zalando, Google e Microsoft são recursos subestimados?
6. Quando uma certificação de fornecedor vale a pena?
7. Cite, em ordem, o que realmente demonstra competência em APIs.
8. Qual item dessa lista é o filtro real em entrevista, e como treiná-lo?

---

### Fontes consultadas (11/08/2026)

- MDN Web Docs — https://developer.mozilla.org/pt-BR/docs/Web/HTTP
- IETF — RFC 9110 e correlatos — https://www.rfc-editor.org/
- OpenClassrooms — *Adoptez les API REST pour vos projets web* — https://openclassrooms.com/fr/courses/6573181-adoptez-les-api-rest-pour-vos-projets-web
- MOOC Francophone — https://mooc-francophone.com/cours/utilisez-des-api-rest-dans-vos-projets-web/
- Jornada do Dev — *Curso de REST API* — https://jornadadodev.com.br/cursos/back-end/rest-api
- Cursa — *Curso de Testes de API Rest* — https://cursa.com.br
- Class Central — catálogo de cursos de REST API — https://www.classcentral.com/subject/rest-apis
- Zalando RESTful API Guidelines — https://opensource.zalando.com/restful-api-guidelines/
- Google API Design Guide — https://cloud.google.com/apis/design
- Microsoft REST API Guidelines — https://github.com/microsoft/api-guidelines
- OWASP API Security Top 10 — https://owasp.org/API-Security/
- Postman Learning Center — https://learning.postman.com
