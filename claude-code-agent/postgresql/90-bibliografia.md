# 90 · Bibliografia comentada

`Nível: todos` · `Última atualização: 11/08/2026`

Livros com autor, edição e para que nível servem. **Nada aqui foi inventado**: onde não tenho
certeza de edição ou ISBN, cito só autor e título e digo que é aproximado. Confirme a edição mais
recente antes de comprar — livros de tecnologia envelhecem, e a documentação oficial gratuita é,
muitas vezes, melhor que qualquer livro pago.

---

## 1. Para aprender do zero

### PostgreSQL: Up and Running — Regina Obe e Leo Hsu

- **Editora:** O'Reilly (a 3ª ed. cobre versões modernas; confirme se há edição mais recente)
- **Nível:** iniciante → intermediário
- **Por que ler:** uma introdução prática e direta ao **uso e à administração** do PostgreSQL,
  escrita por dois especialistas muito respeitados (também autores de referência sobre PostGIS).
  Boa para quem quer ser produtivo rápido, cobrindo os recursos que distinguem o Postgres.
- **Ressalva:** cada edição acompanha uma versão; confira o quão atual é a que você pegar.

### The Art of PostgreSQL — Dimitri Fontaine

- **Autor:** Dimitri Fontaine (contribuidor do PostgreSQL)
- **Onde:** [theartofpostgresql.com](https://theartofpostgresql.com) (autopublicado)
- **Nível:** iniciante → avançado
- **Por que ler:** o melhor livro para **pensar em SQL** — não só a sintaxe, mas como usar o poder
  do banco para mover a lógica dos dados para dentro dele, com clareza e correção. Muda a forma
  como você escreve consultas. Foco em **desenvolvedores**, não em DBAs.
- **Ressalva:** é pago (autopublicado). Vale para quem já sabe o básico e quer subir de nível.

---

## 2. Para ir a fundo (administração e interno)

### PostgreSQL: Introduction and Concepts — Bruce Momjian

- **Autor:** Bruce Momjian (um dos fundadores e figura central da comunidade PostgreSQL)
- **Nível:** iniciante → intermediário
- **Por que ler:** um clássico didático de um dos "pais" do projeto. Momjian também mantém
  **apresentações técnicas gratuitas e excelentes** em [momjian.us/presentations](https://momjian.us/main/presentations/)
  — sobre MVCC, locking, internals — que valem tanto quanto muitos livros.
- **Ressalva:** o livro em si é datado; as apresentações online do autor são atualizadas e
  gratuitas. Prefira-as para o conteúdo interno.

### PostgreSQL 14 Internals — Egor Rogov

- **Autor:** Egor Rogov (Postgres Professional)
- **Nível:** avançado → referência
- **Por que ler:** **a** referência sobre o funcionamento interno — MVCC, VACUUM, WAL, o
  planejador, índices, bloqueios — explicado com profundidade e clareza raras. Se você quer
  realmente entender o "por baixo" ([15](15-transacoes-e-mvcc.md), [16](16-consultas-e-planejador.md),
  [17](17-arquitetura-interna.md)), é este.
- **Gratuito?** **Sim, legalmente.** A Postgres Professional disponibiliza o PDF completo em
  [postgrespro.com/community/books/internals](https://postgrespro.com/community/books/internals).
  Um dos melhores recursos gratuitos que existem sobre o tema. (A edição é da versão 14; o núcleo
  interno muda pouco entre versões — continua valiosíssimo para o PG 18.)

### PostgreSQL – Architecture et notions avancées — Guillaume Lelarge e Julien Rouhaud

- **Idioma:** francês
- **Nível:** avançado
- **Por que ler:** arquitetura e internals em francês, por dois grandes contribuidores da
  comunidade francófona (Dalibo). Raro ter material desse nível fora do inglês.

---

## 3. Para desempenho e otimização

### High Performance PostgreSQL — (O'Reilly, edição recente)

- **Nível:** intermediário → avançado
- **Por que ler:** tuning, índices, planejador, monitoramento — o lado de fazer o banco voar em
  produção. Verifique a edição/autoria mais recente ao comprar (há títulos de desempenho de
  PostgreSQL de diferentes autores e anos; prefira o que cobre PG 14+).
- **Ressalva:** livros de desempenho envelhecem com as versões; complemente com a documentação e
  com [21-administracao-e-operacao.md](21-administracao-e-operacao.md).

### Mastering PostgreSQL (Hans-Jürgen Schönig) e o blog da Cybertec

- **Nível:** intermediário → avançado
- **Por que ler:** Schönig (Cybertec) escreve sobre recursos avançados; o
  [blog da Cybertec](https://www.cybertec-postgresql.com/en/blog/) é uma das melhores fontes
  gratuitas e atualizadas sobre tuning e recursos novos.

---

## 4. SQL e modelagem (não específico do PostgreSQL)

### SQL Performance Explained — Markus Winand

- **Onde:** [use-the-index-luke.com](https://use-the-index-luke.com) (versão web **gratuita**)
- **Nível:** intermediário
- **Por que ler:** **a** melhor explicação sobre índices e desempenho de SQL, agnóstica de banco (com
  exemplos de PostgreSQL). Se você lê **uma** coisa sobre índices além do [14](14-indices.md), leia
  o site do Winand. Clareza excepcional.
- **Gratuito?** O conteúdo completo está no site; o livro em papel é pago.

### Designing Data-Intensive Applications — Martin Kleppmann

- **Editora:** O'Reilly (2017; há 2ª edição em preparação — confira)
- **Nível:** intermediário → avançado
- **Por que ler:** não é sobre PostgreSQL, mas é **o** livro sobre os fundamentos de sistemas de
  dados — replicação, particionamento, transações, consistência, o que vem depois de um banco só.
  Contextualiza tudo do [19](19-replicacao-e-alta-disponibilidade.md) e do [60](60-teoria-avancada.md).
  Um dos melhores livros técnicos da geração.

### Database Design for Mere Mortals — Michael Hernandez

- **Nível:** iniciante
- **Por que ler:** modelagem e normalização explicadas para quem está começando, sem jargão
  matemático. Bom complemento ao [12-modelo-relacional-e-sql.md](12-modelo-relacional-e-sql.md).

---

## 5. Os clássicos teóricos

### Fundamentals of Database Systems — Elmasri e Navathe · Database System Concepts — Silberschatz, Korth, Sudarshan

- **Nível:** universitário → referência
- **Por que ler:** os dois livros-texto canônicos de bancos de dados, usados em cursos de
  graduação. Cobrem o modelo relacional, álgebra, normalização, transações e teoria com rigor. Se
  você quer a base formal do [60-teoria-avancada.md](60-teoria-avancada.md), é aqui.
- **Ressalva:** densos, acadêmicos, caros. São referência, não leitura de cabeceira.

---

## 6. O que é legalmente gratuito

| Obra | Onde |
|---|---|
| **PostgreSQL 14 Internals** — Egor Rogov | [postgrespro.com/community/books/internals](https://postgrespro.com/community/books/internals) |
| **Documentação oficial** (a melhor de qualquer banco) | [postgresql.org/docs](https://www.postgresql.org/docs/current/) |
| **Apresentações do Bruce Momjian** | [momjian.us/presentations](https://momjian.us/main/presentations/) |
| **Use The Index, Luke!** — Markus Winand | [use-the-index-luke.com](https://use-the-index-luke.com) |
| **Blog da Cybertec** e da Crunchy Data | atualizado, prático |
| **PostgreSQL Wiki** | [wiki.postgresql.org](https://wiki.postgresql.org) |

---

## 7. Recomendação por perfil

| Você é… | Leia, nesta ordem |
|---|---|
| **Iniciante total** | Documentação oficial (tutorial) + PostgreSQL: Up and Running |
| **Desenvolvedor** | The Art of PostgreSQL + Use The Index, Luke! |
| **Quem quer o interno** | PostgreSQL 14 Internals (grátis) + apresentações do Momjian |
| **DBA / operação** | High Performance PostgreSQL + blog da Cybertec + docs |
| **Arquiteto** | Designing Data-Intensive Applications + o interno |
| **Base teórica** | Elmasri & Navathe ou Silberschatz + [60](60-teoria-avancada.md) |

---

## 8. O que **não** recomendo

- **Livros de "PostgreSQL em 24 horas" genéricos** — raramente vão além do que o tutorial oficial
  gratuito cobre melhor.
- **Qualquer livro anterior a ~2018** como fonte principal de recursos — perde JSONB moderno,
  particionamento declarativo, melhorias de MVCC, e as versões 12–18. Bom para os fundamentos
  (que não mudam), ruim para o que é atual. O **interno** (Rogov, Momjian) envelhece devagar; o de
  **recursos e desempenho** envelhece rápido.
- **Material que ainda ensina `money`, `SERIAL` como recomendação, ou ignora `TIMESTAMPTZ`** —
  sinal de desatualização.

---

## Autoteste

1. Qual livro você recomendaria a um iniciante total, e qual recurso gratuito o complementa?
2. Qual é o melhor livro para "pensar em SQL" como desenvolvedor?
3. Qual é a melhor referência sobre o funcionamento interno, e onde obtê-la de graça?
4. Por que "Designing Data-Intensive Applications" aparece numa bibliografia de PostgreSQL?
5. Onde está a melhor explicação gratuita sobre índices, e quem a escreveu?
6. Cite três recursos legalmente gratuitos e de alta qualidade.
7. Por que a documentação oficial pode ser melhor que um livro pago?
8. Que sinais indicam que um material de PostgreSQL está desatualizado?
9. Qual tipo de livro (interno ou de recursos/desempenho) envelhece mais devagar, e por quê?
10. Monte uma trilha de leitura para quem quer entender o PostgreSQL "por baixo".
