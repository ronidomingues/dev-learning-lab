# 85 · Cursos gratuitos e certificações

`Nível: todos` · **Pesquisado na web em 11/08/2026** · Este arquivo envelhece em ~1 ano.

> **Metodologia:** links e existência dos cursos verificados por busca em 11/08/2026. **Não
> assisti aos cursos**; a avaliação combina reputação do autor/plataforma com o que a busca
> retornou. Trate como ponto de partida, não como resenha. Confirme datas e disponibilidade antes
> de investir tempo. Onde não confirmei um detalhe, o texto diz isso.

Ordem de prioridade do preset: **português → inglês → francês**.

---

## 1. Português (Brasil e Portugal)

### Vídeo — gratuito

| Curso | Onde | Nível | Vale? |
|---|---|---|---|
| **Curso de PostgreSQL / Bancos de Dados** (playlists de canais de programação BR) | YouTube | iniciante→interm. | **Sim** para começar. Verifique a data — prefira material de 2024+ |
| **Curso Completo de SQL com PostgreSQL — Do Zero ao Avançado** (fev/2026) | [YouTube](https://www.youtube.com/watch?v=9cAKQWodpvM) | iniciante→interm. | Recente; bom para ver a sintaxe atual |
| **Curso de SQL: PostgreSQL, Python e Docker** (abr/2025) | [YouTube](https://www.youtube.com/watch?v=Q1OouIcI9YA) | iniciante | Conecta SQL a Python e Docker |
| **Introdução ao PostgreSQL / Curso de Postgres** | YouTube | iniciante | Panorama |

### Texto e prática em português

| Recurso | Observação |
|---|---|
| [DevMedia — Curso de PostgreSQL](https://www.devmedia.com.br/curso/curso-de-postgresql/1904) | Instalação, sintaxe, ferramentas; parte gratuita |
| Documentação oficial | **Não** tem tradução oficial confiável em PT; use o inglês, que é excelente |
| [free-programming-books (PT-BR)](https://github.com/EbookFoundation/free-programming-books/blob/main/courses/free-courses-pt_BR.md) | Índice comunitário de cursos, seção de bancos de dados |

> **Nota honesta:** o material gratuito de PostgreSQL em português é mais fragmentado que o de
> inglês. Muitos cursos "de SQL" servem, porque o SQL básico é comum a todos os bancos — só cuide
> das partes específicas do PostgreSQL (tipos, JSONB, índices, MVCC), onde vale complementar com a
> documentação oficial.

---

## 2. Inglês

### Documentação oficial — a melhor fonte, e é gratuita

A [**documentação oficial do PostgreSQL**](https://www.postgresql.org/docs/current/) é
**excepcional** — provavelmente a melhor documentação de qualquer banco de dados. O
[tutorial oficial](https://www.postgresql.org/docs/current/tutorial.html) leva do zero, e a
referência é completa e precisa. Se você só usar uma fonte, que seja esta.

### Vídeo e cursos interativos — gratuitos

| Curso | Onde | Nível | Vale? |
|---|---|---|---|
| **PostgreSQL Tutorial for Beginners** (freeCodeCamp) | YouTube | iniciante | **Sim.** Completo e bem produzido |
| **Learn PostgreSQL — Full Course** (várias edições) | YouTube | iniciante | Panorama prático |
| [**PostgreSQL Tutorial**](https://www.postgresqltutorial.com) | site | iniciante→avançado | Referência escrita, muito usada, com exemplos |
| [**pgexercises.com**](https://pgexercises.com) | site | interm. | **81 exercícios** interativos sobre um dataset, com soluções e explicações. Excelente para praticar SQL |
| [**SQLBolt**](https://sqlbolt.com), [**Mode SQL Tutorial**](https://mode.com/sql-tutorial) | site | iniciante | SQL geral, interativo |
| [**select star SQL**](https://selectstarsql.com) | site | iniciante | Livro interativo gratuito |

**pgexercises** merece destaque: praticar SQL resolvendo problemas reais, no navegador, é a forma
mais rápida de fixar. Faça-o em paralelo ao Bloco A deste material.

---

## 3. Francês

| Curso | Onde | Nível | Vale? |
|---|---|---|---|
| **PostgreSQL pour les (grands) débutants** (~4h) | [YouTube](https://www.youtube.com/playlist?list=PLTCE7CKb1F5BU62FCOIxCD4In0COnRY2R) | iniciante | **Sim.** Curso completo e gratuito, bem avaliado |
| **SQL & PostgreSQL — Tutoriel complet pour débutants** (WeWantCode) | YouTube | iniciante | Panorama |
| [**Cours et Fiches — PostgreSQL**](https://cours-et-fiches.com/programmation/postgresql/) | site | iniciante→avançado | 12 capítulos, incluindo JSONB, full-text, índices, extensões |
| [**postgresql.developpez.com**](https://postgresql.developpez.com/cours/) | site | vários | Comunidade francófona clássica de desenvolvimento |
| **Documentation PostgreSQL en français** | [docs](https://docs.postgresql.fr/) | referência | A comunidade francesa mantém **tradução da documentação oficial** — rara e valiosa |

> A comunidade francófona de PostgreSQL é forte (Dalibo, entre outros), e a
> [tradução francesa da documentação](https://docs.postgresql.fr/) é um recurso de qualidade que
> poucos idiomas têm.

---

## 4. Certificações

### A situação, com franqueza

**Não existe uma certificação "oficial" única do PostgreSQL** — o projeto é comunitário, sem uma
autoridade certificadora central (ao contrário de, digamos, a Oracle com suas certificações). As
que existem são de **empresas** do ecossistema:

| Certificação | Emissor | O que é | Preço (consultar) |
|---|---|---|---|
| **EDB Certified Associate** | EnterpriseDB | Nível fundamental: instalação, config, manutenção, segurança básica | consultar EDB |
| **EDB Certified Professional** | EnterpriseDB | DBA avançado; ~60 questões, 90 min, 70% para passar | **~US$ 200** (relatado; confirme) |
| Certificações de nuvem (AWS, Google, Azure) | provedores | Cobrem o banco gerenciado (RDS, Cloud SQL), não o PG puro | variável |
| Certificados de plataformas de curso | DataCamp, Coursera, Udemy | Conclusão de curso | valor do curso |

> **As certificações EDB** referem-se com frequência ao **EDB Postgres Advanced Server** (a
> distribuição comercial da EDB), não só ao PostgreSQL puro — verifique o escopo antes de estudar,
> se seu interesse é o PostgreSQL da comunidade.

### O veredito honesto

- **Para *aprender*:** a documentação oficial + pgexercises + prática valem mais que qualquer
  certificado. O conhecimento de PostgreSQL é abundante e gratuito.
- **Para *sinalizar* no mercado:** a certificação da **EDB** é a mais reconhecida especificamente
  para PostgreSQL, mas o reconhecimento é **moderado** — em muitas vagas, experiência comprovada e
  um bom portfólio pesam mais. Certificações de **nuvem** (AWS/Azure/GCP) costumam ter mais tração
  no RH quando o trabalho é sobre o banco gerenciado daquele provedor.
- **Certificados de conclusão de curso** (YouTube, plataformas grátis) têm valor **simbólico** —
  servem para portfólio, não abrem portas sozinhos.

*Recomendação:* invista em **saber fazer** (o Lab 10 deste material, um projeto real, contribuir
com uma dúvida bem resolvida no Stack Overflow) antes de investir em certificado. Se o mercado que
você mira valoriza um selo específico, tire o da EDB ou o de nuvem correspondente — mas depois de
saber, não no lugar de saber.

---

## 5. Trilha de estudo sugerida, do zero ao empregável

| Fase | O que fazer | Tempo | Custo |
|---|---|---|---|
| **1. Fundamentos** | Bloco A deste material + tutorial oficial + Neon grátis | 2–4 semanas | US$ 0 |
| **2. Prática** | pgexercises (81 exercícios) + os 10 labs do [70](70-pratica.md) | 2–4 semanas | US$ 0 |
| **3. Núcleo** | Bloco B (modelagem, índices, MVCC, planejador) + um livro ([90](90-bibliografia.md)) | 1–3 meses | US$ 0–30 |
| **4. Projeto real** | [projeto-modelo](07-projeto-modelo/README.md) ou um seu, ponta a ponta | 2–4 semanas | US$ 0 |
| **5. Sinalização (opcional)** | EDB Associate/Professional, ou cert de nuvem | conforme | preço do exame |

---

## Autoteste

1. Qual é a melhor fonte gratuita para aprender PostgreSQL, e por quê?
2. O que é o pgexercises, e por que fazê-lo em paralelo ao Bloco A?
3. Existe uma certificação "oficial" do PostgreSQL? Explique a situação.
4. O que a certificação EDB cobre, e qual é a ressalva sobre o escopo (Advanced Server)?
5. Certificado de conclusão de curso grátis tem valor de mercado? Distinga "aprender" de
   "sinalizar".
6. Qual é a melhor opção gratuita em francês, e o que a comunidade francófona oferece de raro?
7. Por que o material em português é mais fragmentado, e como compensar?
8. Quando uma certificação de nuvem faz mais sentido que a da EDB?
9. Monte uma trilha do zero ao empregável com tempo e custo por fase.
10. Por que "saber fazer" deve vir antes do certificado?

---

### Fontes consultadas (11/08/2026)

- [Documentação oficial do PostgreSQL](https://www.postgresql.org/docs/current/) e [tutorial](https://www.postgresql.org/docs/current/tutorial.html)
- [pgexercises.com](https://pgexercises.com) · [PostgreSQL Tutorial](https://www.postgresqltutorial.com) · freeCodeCamp (YouTube)
- [PostgreSQL pour les (grands) débutants (YouTube, FR)](https://www.youtube.com/playlist?list=PLTCE7CKb1F5BU62FCOIxCD4In0COnRY2R) · [Cours et Fiches (FR)](https://cours-et-fiches.com/programmation/postgresql/) · [Documentation PostgreSQL en français](https://docs.postgresql.fr/)
- [EDB — Certification Exams Catalog](https://www.enterprisedb.com/training/certification-exams) e [DataCamp — PostgreSQL Certification](https://www.datacamp.com/blog/postgre-sql-certification-everything-you-need-to-know) — **fontes sobre certificação; preço da EDB Professional (~US$ 200) a confirmar na EDB**
