# 85 · Cursos gratuitos e certificações

`Nível: todos` · **Pesquisado na web em 11/08/2026** · Este arquivo envelhece em ~1 ano.

> **Metodologia:** links e existência dos cursos verificados por busca em 11/08/2026. **Não
> assisti aos cursos**; a avaliação de qualidade combina reputação conhecida do autor/canal com o
> que a busca retornou. Trate as recomendações como ponto de partida, não como resenha. Datas de
> publicação e disponibilidade mudam — confirme antes de investir tempo. Onde não confirmei um
> detalhe, o texto diz isso.

Ordem de prioridade do preset: **português → inglês → francês**.

---

## 1. Português (Brasil e Portugal)

### Vídeo — gratuito

| Curso | Autor / Canal | Onde | Nível | Vale? |
|---|---|---|---|---|
| **Descomplicando o Docker** | Jefferson Fernando / **LINUXtips** | YouTube | iniciante→intermediário | **Sim.** A referência em PT-BR. Didático, prático, foco em quem vai operar de verdade. Há versões de anos diferentes; prefira a mais recente |
| **Docker do Zero** | **Fabrício Veronez** | YouTube | iniciante→intermediário | **Sim.** Um dos melhores comunicadores de DevOps em português; conecta bem Docker a CI/CD e nuvem |
| **Intensivão Docker (2h)** | vários (busca 2025) | YouTube | iniciante | Bom para uma visão geral rápida antes de aprofundar |
| **Curso de Docker Completo** | vários | YouTube (playlists) | iniciante | Qualidade varia por playlist; cheque data e conteúdo |

> **LINUXtips** também tem treinamentos pagos aprofundados (`Docker Essentials`, "Descomplicando"
> em plataforma própria). O material do YouTube é o gratuito e já leva longe. As **anotações da
> comunidade** sobre o "Descomplicando o Docker" estão em repositórios públicos no GitHub —
> úteis como resumo consultável.

### Texto e documentação em português

| Recurso | Observação |
|---|---|
| [free-programming-books (PT-BR)](https://github.com/EbookFoundation/free-programming-books/blob/main/courses/free-courses-pt_BR.md) | Índice comunitário; seção de Docker/DevOps com links atualizados pela comunidade |
| Documentação oficial | A [docs.docker.com](https://docs.docker.com) **não** tem tradução oficial confiável em PT; use o original em inglês |

---

## 2. Inglês

### Vídeo — gratuito

| Curso | Autor / Plataforma | Nível | Vale? |
|---|---|---|---|
| **Docker Tutorial for Beginners (Full DevOps Course)** | **freeCodeCamp** (YouTube) | iniciante | **Sim.** Completo, com laboratórios acessíveis no navegador. Um dos melhores pontos de partida gratuitos |
| **Docker for the Absolute Beginner** | **KodeKloud** (Mumshad Mannambeth) | iniciante | **Sim.** A parte introdutória costuma ser gratuita; laboratórios interativos excelentes. É a origem do estilo "hands-on" da área |
| **Docker Full Course for Beginners** | freeCodeCamp / vários (2026) | iniciante | Atualizado; bom para ver os padrões atuais |
| **Free Learning Week** | **KodeKloud** | todos | Janelas periódicas de acesso gratuito a cursos + laboratórios pagos |

### Laboratórios interativos — gratuitos

| Recurso | O que é |
|---|---|
| [Play with Docker](https://labs.play-with-docker.com) | Terminal real no navegador; sessões de 4h. **Comece por aqui** |
| [Killercoda](https://killercoda.com) | Cenários guiados com terminal real |
| [KodeKloud labs](https://kodekloud.com) | Laboratórios interativos; alguns gratuitos |
| [Docker's own "Getting Started"](https://docs.docker.com/get-started/) | Tutorial oficial, prático |

### Texto — a fonte definitiva

A **documentação oficial** ([docs.docker.com](https://docs.docker.com)) é, honestamente, melhor
que a maioria dos cursos pagos: bem escrita, com trilha de aprendizado, e sempre atualizada.
Combine-a com prática no Play with Docker.

---

## 3. Francês

| Curso | Autor / Canal | Onde | Nível | Vale? |
|---|---|---|---|---|
| **Docker formation de A à Z** | **Xavki** (Xavier Pestel) | [YouTube](https://www.youtube.com/playlist?list=PLn6POgpklwWq0iz59-px2z-qjDdZKEvWd) | iniciante→avançado | **Sim.** ~30 vídeos, progressão clara. A melhor referência gratuita em francês; o canal tem trilha DevOps inteira |
| **Tutoriels Docker-Compose (FR)** | Xavki | [YouTube](https://www.youtube.com/playlist?list=PLn6POgpklwWqaC1pdx02SrrgOaL2ZL7G0) | intermediário | Continuação natural, focada em Compose |
| **Tutoriel Docker pour débutants (1h)** | vários | YouTube | iniciante | Panorama rápido |
| **Apprendre Docker — cours complet** | [devopssec.fr](https://devopssec.fr/category/apprendre-docker) | texto | iniciante→intermediário | Curso escrito, bem estruturado |
| **5 ressources gratuites (2026)** | [learnthings.fr](https://www.learnthings.fr/ressource-pour-vous-former-gratuitement-docker/) | agregador | — | Lista curada de recursos gratuitos |

---

## 4. Certificações — o mapa honesto

### Docker Certified Associate (DCA) — atenção ao estado

**Situação em 11/08/2026: confusa, e é preciso ser franco.** As fontes divergem:

- Parte relata que a **DCA foi descontinuada em 2026**, sem substituto direto anunciado pela
  Docker.
- Parte relata que a certificação **passou à Mirantis** (que adquiriu a Docker Enterprise em
  2019) e continuaria disponível para registro.

**O que fazer com isso:** **confirme o estado atual diretamente com a Mirantis/Docker antes de
estudar para a DCA.** Independentemente do estado administrativo, o mercado migrou: a competência
de container em produção hoje se sobrepõe fortemente a **Kubernetes**, e as certificações de
Kubernetes têm valor de mercado muito mais claro.

### As certificações que valem em 2026

Todas são da **Linux Foundation / CNCF**, práticas (você opera um cluster real na prova), e têm
reconhecimento de mercado sólido.

| Certificação | Foco | Formato | Preço (consultar) |
|---|---|---|---|
| **KCNA** — Kubernetes and Cloud Native Associate | Fundamentos (inclui containers) | Múltipla escolha, 90 min | **~US$ 250** (relatado; confirme) |
| **KCSA** — Kubernetes and Cloud Native Security Associate | Segurança cloud-native | Múltipla escolha | consultar |
| **CKA** — Certified Kubernetes Administrator | Operar clusters | **Prática**, 2h | consultar (tipicamente mais que KCNA) |
| **CKAD** — Certified Kubernetes Application Developer | Desenvolver para K8s | **Prática**, 2h | consultar |
| **CKS** — Certified Kubernetes Security Specialist | Segurança avançada (exige CKA) | **Prática**, 2h | consultar |

> **Preços das certificações mudam e há promoções frequentes** (Cyber Monday, bundles com
> treinamento, vouchers de eventos). O valor de ~US$ 250 para a KCNA foi o relatado na busca de
> 11/08/2026 — **confirme na [training.linuxfoundation.org](https://training.linuxfoundation.org)**.
> Todas incluem uma retentativa gratuita e um período de acesso a ambiente de treino.

### Trilha recomendada

```
   Docker (este material)  ──▶  KCNA  ──▶  CKA (ou CKAD, conforme o papel)  ──▶  CKS
        fundamento              porta        competência de mercado             especialização
        de container          de entrada      real e reconhecida                  em segurança
```

- **Começa em Docker** porque containers são o pré-requisito conceitual do resto.
- **KCNA** é a porta de entrada barata e de baixo risco (múltipla escolha), boa para validar
  fundamentos.
- **CKA/CKAD** são as que abrem porta no mercado, e são **práticas** — não se passa decorando.
- **CKS** é especialização, exige CKA vigente.

### Preparação gratuita para as certificações

| Recurso | Para qual | Custo |
|---|---|---|
| **KodeKloud** (cursos + labs) | KCNA, CKA, CKAD, CKS | Parte gratuita; assinatura para o completo |
| **Kubernetes docs / tutoriais oficiais** | Todas | Grátis |
| **killer.sh** | CKA, CKAD, CKS | **Duas sessões incluídas** ao comprar o exame — o simulador mais próximo da prova real |
| **CNCF curriculum (GitHub)** | Todas | Grátis; o programa oficial de cada exame |
| **"Kubernetes the Hard Way"** (Kelsey Hightower) | CKA e entendimento profundo | Grátis; monta um cluster do zero, à mão |

---

## 5. Trilha de estudo sugerida, do zero ao empregável

| Fase | O que fazer | Tempo | Custo |
|---|---|---|---|
| **1. Fundamentos** | Este material (blocos A e B) + Play with Docker | 2–4 semanas | US$ 0 |
| **2. Prática** | Os 10 laboratórios do [70-pratica.md](70-pratica.md) + um projeto seu | 2–4 semanas | US$ 0 |
| **3. Curso guiado** | LINUXtips ou Fabrício Veronez (PT) · freeCodeCamp ou KodeKloud (EN) | 1–2 semanas | US$ 0 |
| **4. Validação** | KCNA | 2–4 semanas de estudo | ~US$ 250 |
| **5. Mercado** | CKA/CKAD + orquestração ([25](25-orquestracao.md)) | 2–3 meses | preço do exame |

**Realismo:** só faça certificação se ela tiver função concreta (exigência de vaga, de cliente,
de promoção). Para *aprender*, o material gratuito + prática vale mais que qualquer certificado.
Para *sinalizar* competência no mercado, CKA/CKAD são as que o RH reconhece. KCNA é boa relação
custo-benefício como primeiro selo; DCA, no estado atual incerto, eu não priorizaria.

---

## 6. Certificadores gratuitos — existe algo de valor real?

**Resposta franca: certificados verdadeiramente gratuitos e com valor de mercado real
praticamente não existem em container/Kubernetes.** O que há:

| Tipo | Valor de mercado | Observação |
|---|---|---|
| Certificados de conclusão do YouTube/plataforma grátis | **Simbólico** | Servem para portfólio, não abrem porta sozinhos |
| Badges de "free learning week" | Simbólico a baixo | Marketing das plataformas |
| **CKA/CKAD/CKS/KCNA** (pagos) | **Real** | São os que o mercado reconhece |
| Cloud Skills Boost (Google), AWS Skill Builder | Baixo a médio | Bons para aprender; o certificado grátis vale pouco |

**Conclusão honesta:** o conhecimento é gratuito e abundante; a **sinalização reconhecida** é
paga. Não confunda "fiz um curso grátis com certificado" com "tenho uma credencial de mercado" —
são coisas diferentes, e o RH sabe a diferença.

---

## Autoteste

1. Qual é a melhor referência gratuita em vídeo para Docker em português, e por quê?
2. Por que a documentação oficial em inglês é recomendada mesmo para quem prefere português?
3. Qual é o estado da certificação DCA em agosto de 2026, e o que fazer diante dessa incerteza?
4. Ordene KCNA, CKA e CKS numa trilha e justifique a ordem.
5. Por que CKA/CKAD "não se passa decorando"?
6. Qual é a melhor referência gratuita em francês, e o que ela cobre?
7. Certificado gratuito de conclusão tem valor de mercado? Distinga "aprender" de "sinalizar".
8. Que ferramenta acompanha a compra do exame CKA e é o melhor simulador?
9. Monte uma trilha do zero ao empregável com tempo e custo por fase.
10. Por que começar por Docker antes de Kubernetes, mesmo mirando certificação de Kubernetes?

---

### Fontes consultadas (11/08/2026)

- [LINUXtips — Docker Essentials](https://linuxtips.io/treinamento/docker-essentials/) e anotações comunitárias do "Descomplicando o Docker" ([diogo-alves](https://github.com/diogo-alves/anotacoes-curso-descomplicando-o-docker-), [Pacheco95](https://github.com/Pacheco95/linuxtips-resumo-docker))
- [free-programming-books — cursos gratuitos PT-BR](https://github.com/EbookFoundation/free-programming-books/blob/main/courses/free-courses-pt_BR.md)
- [freeCodeCamp — Docker Full Course](https://www.freecodecamp.org/news/docker-full-course/) · [KodeKloud — Free Courses](https://kodekloud.com/free-courses) e [Free Learning Week](https://kodekloud.com/free-week)
- [Xavki — Docker formation de A à Z](https://www.youtube.com/playlist?list=PLn6POgpklwWq0iz59-px2z-qjDdZKEvWd) · [devopssec.fr — Apprendre Docker](https://devopssec.fr/category/apprendre-docker) · [learnthings.fr — 5 ressources gratuites 2026](https://www.learnthings.fr/ressource-pour-vous-former-gratuitement-docker/)
- [KodeKloud — Docker Certification guide](https://kodekloud.com/blog/docker-certification/) · [TrueCert — DCA Discontinued](https://truecert.co/blog/best-docker-certifications-2026/) · [Sailor.sh — KCNA Exam Guide 2026](https://sailor.sh/blog/kcna-exam-guide-2026/) — **fontes divergem sobre o estado da DCA; preço da KCNA (~US$ 250) a confirmar em [training.linuxfoundation.org](https://training.linuxfoundation.org)**
