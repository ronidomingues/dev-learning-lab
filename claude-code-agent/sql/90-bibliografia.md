# 90 — Bibliografia comentada

Data: 13/08/2026 · Edições e disponibilidade gratuita confirmadas na web nesta data

Nenhum livro, ISBN ou edição foi inventado. Onde há incerteza sobre uma
edição específica, cito apenas autor e título e digo que é aproximado.

Legenda: **📖 gratuito legalmente** · 🇧🇷 edição em português

---

## 1. Para começar

### Beaulieu, Alan. **Learning SQL**. 3ª ed. O'Reilly, 2020.
- **Nível:** iniciante → intermediário
- **Faz melhor que os outros:** progressão didática limpa, sem pressa e sem
  paternalismo. Exemplos em MySQL.
- **Envelheceu?** Não no essencial; a 3ª edição cobre funções analíticas.
- 🇧🇷 há edições anteriores traduzidas como *Aprendendo SQL* (Novatec). A
  tradução é aceitável; o vocabulário técnico às vezes destoa do uso corrente.

### Molinaro, Anthony; De Graaf, Robert. **SQL Cookbook**. 2ª ed. O'Reilly, 2020.
- **Nível:** intermediário
- **Faz melhor:** é organizado por **problema**, não por comando — "como
  encontrar linhas duplicadas", "como preencher lacunas". E dá a solução em
  **cinco dialetos lado a lado**, o que é raríssimo.
- **Recomendação:** é o livro que fica aberto ao lado do teclado. A 2ª edição
  acrescentou funções de janela, que a 1ª (2005) não tinha.

### Guanabara, Gustavo. **material do Curso em Vídeo — MySQL**. 🇧🇷 📖
- Não é livro, mas o material de apoio em português é uma referência gratuita
  legítima para iniciantes. Ver [85](85-cursos-e-certificacoes.md).

---

## 2. Os que mudam como você escreve SQL

### Winand, Markus. **SQL Performance Explained**. Self-published, 2012. 📖
- **ISBN:** 978-3-9503078-2-5
- **Nível:** intermediário → avançado
- **📖 Gratuito na íntegra** em <https://use-the-index-luke.com> (o autor
  mantém o conteúdo aberto e vende o impresso)
- **Faz melhor que todos:** é **o** livro sobre índices. Explica B-tree,
  seletividade, ordem de colunas em índice composto, e por que sua consulta
  não usa o índice — cobrindo **Oracle, PostgreSQL, SQL Server, MySQL e DB2
  lado a lado**.
- **Envelheceu?** É de 2012 e continua atual, porque índices B-tree não
  mudaram. **O livro de melhor relação valor/tempo desta lista inteira.**
- Do mesmo autor: <https://modern-sql.com>, 📖 gratuito, sobre os recursos
  posteriores ao SQL-92 que a maioria das pessoas ignora.

### Karwin, Bill. **SQL Antipatterns, Volume 1: Avoiding the Pitfalls of Database Programming**. 2ª ed. Pragmatic Bookshelf, 2022.
- **Nível:** intermediário
- **Faz melhor:** cada capítulo é um erro real de modelagem ou consulta, com o
  nome, o sintoma, quando é aceitável, e a solução. Organizado em projeto
  lógico, projeto físico, consultas e desenvolvimento.
- Há um segundo volume, *More SQL Antipatterns* (Pragmatic Bookshelf), sobre
  otimização.
- **É o livro que evita os erros que este curso descreve em
  [75-armadilhas.md](75-armadilhas.md)** — com mais profundidade.

### Celko, Joe. **SQL for Smarties: Advanced SQL Programming**. 5ª ed. Morgan Kaufmann, 2014.
- **Nível:** avançado
- **Faz melhor:** pensar em conjuntos em vez de laços. Se você vem de
  programação procedural e escreve SQL como se fosse Python, este livro é a
  cura.
- **Envelheceu?** Em parte. O estilo é opinativo e por vezes datado, e alguns
  truques foram superados por funções de janela. **O modo de pensar continua
  valendo.**
- Do mesmo autor, *Joe Celko's Trees and Hierarchies in SQL for Smarties* —
  específico e ótimo se você precisa modelar hierarquias (estrutura de produto,
  hierarquia de equipamentos).

---

## 3. Teoria e fundamentos

### Date, C. J. **An Introduction to Database Systems**. 8ª ed. Pearson, 2003.
- **Nível:** universitário
- O tratado clássico do modelo relacional. Date foi colega de Codd e o maior
  divulgador (e crítico) do SQL. 🇧🇷 *Introdução a Sistemas de Bancos de Dados*
  (Campus/Elsevier) — tradução da 8ª edição, boa.
- **Envelheceu?** No que trata de produtos, sim. Na teoria, não.

### Date, C. J. **SQL and Relational Theory: How to Write Accurate SQL Code**. 3ª ed. O'Reilly, 2015.
- Mais focado e mais útil que o anterior para quem já escreve SQL. É a
  argumentação de Date sobre por que o `NULL` do SQL é um erro, e como escrever
  SQL que se aproxima do modelo relacional correto.
- **Ressalva honesta:** Date é dogmático. Leia sabendo disso — as críticas são
  corretas, as recomendações às vezes são impraticáveis.

### Silberschatz, Korth, Sudarshan. **Database System Concepts**. 7ª ed. McGraw-Hill, 2020.
- O livro-texto padrão de graduação em todo o mundo. Cobre modelo relacional,
  SQL, projeto, armazenamento, indexação, transações, recuperação, distribuição.
- 🇧🇷 *Sistemas de Banco de Dados* (McGraw-Hill/Elsevier), edições anteriores.
- **Faz melhor:** abrangência. Se você quer **um** livro acadêmico, é este.

### Elmasri, Ramez; Navathe, Shamkant. **Fundamentals of Database Systems**. 7ª ed. Pearson, 2015.
- Concorrente direto do Silberschatz, com mais ênfase em modelagem conceitual
  (entidade-relacionamento).
- 🇧🇷 *Sistemas de Banco de Dados* (Pearson) — tradução amplamente usada em
  cursos brasileiros e razoável.

### Garcia-Molina, Ullman, Widom. **Database Systems: The Complete Book**. 2ª ed. Pearson, 2008.
- **Nível:** pesquisa
- Mais rigoroso e mais matemático que os dois anteriores; excelente em
  processamento e otimização de consultas. É o livro que acompanha o curso de
  Stanford citado em [85](85-cursos-e-certificacoes.md).

---

## 4. Sistemas, escala e arquitetura

### Kleppmann, Martin; Riccomini, Chris. **Designing Data-Intensive Applications**. 2ª ed. O'Reilly, **fevereiro de 2026**. 672 p.
- **ISBN da 2ª ed.:** 978-1-098-11906-5 (impresso)
- **Nível:** intermediário → avançado
- **Faz melhor que todos:** explica **por que** os sistemas de dados são como
  são — replicação, particionamento, transações, consenso, processamento de
  fluxo — com honestidade sobre os trade-offs e sem vender nada.
- A 2ª edição (2026) acrescenta sistemas nativos de nuvem e o impacto de IA.
- **Se você só puder ler um livro desta lista inteira, e não for sobre SQL
  especificamente, leia este.** A 1ª edição (2017) tem tradução 🇧🇷 como
  *Projetando Aplicações Intensivas em Dados* (Novatec).

### Petrov, Alex. **Database Internals**. O'Reilly, 2019.
- Como o motor funciona por dentro: B-trees, LSM-trees, WAL, protocolos de
  consenso. Para quem quer saber o que acontece abaixo do `SELECT`.

### Hellerstein, Stonebraker, Hamilton. **Architecture of a Database System**. Foundations and Trends in Databases, 2007. 📖
- **📖 Gratuito:** <https://dsf.berkeley.edu/papers/fntdb07-architecture.pdf>
- ~120 páginas. A melhor visão geral concisa da arquitetura de um SGBD que
  existe. Escrita por três dos maiores nomes da área.

---

## 5. Especificamente para dado de processo

Aviso honesto: **não existe um bom livro sobre SQL para engenharia de
processo.** Este curso existe em parte por isso. O que existe são livros de
cada assunto separado:

### Montgomery, Douglas C. **Introduction to Statistical Quality Control**. 8ª ed. Wiley, 2019.
- A referência de CEP: cartas de controle, regras de Nelson, Cp/Cpk,
  capacidade, planejamento de experimentos.
- 🇧🇷 *Introdução ao Controle Estatístico da Qualidade* (LTC) — tradução boa e
  amplamente adotada nos cursos brasileiros.
- **É o livro que fundamenta a seção 4 de
  [30-engenharia-quimica.md](30-engenharia-quimica.md).**

### Seborg, Edgar, Mellichamp, Doyle. **Process Dynamics and Control**. 4ª ed. Wiley, 2016.
- Controle de processo, com capítulos sobre monitoramento, detecção de falha e
  controle estatístico multivariado (PCA, PLS). O elo entre o dado que você
  consulta e o processo que o gerou.

### Romagnoli, José A.; Sánchez, Mabel C. **Data Processing and Reconciliation for Chemical Process Operations**. Academic Press, 1999.
- Reconciliação de dados e detecção de erro grosseiro em medidas de processo —
  a matemática por trás de "fazer o balanço fechar". Antigo, específico, e sem
  substituto óbvio.
- **Nível:** pós-graduação.

### Kimball, Ralph; Ross, Margy. **The Data Warehouse Toolkit**. 3ª ed. Wiley, 2013.
- Modelagem dimensional: fatos, dimensões, estrela, dimensões que mudam
  lentamente (SCD). É a origem do vocabulário usado em
  [19](19-ddl-e-modelagem.md) e [22](22-views-e-analitico.md).
- **Envelheceu?** O vocabulário e os padrões, não. As recomendações de
  tecnologia, sim.

---

## 6. Documentação como livro 📖

Às vezes o melhor "livro" é a documentação. Estas três são exemplares:

- **PostgreSQL Manual** — <https://www.postgresql.org/docs/current/> 📖
  Provavelmente a melhor documentação de software livre que existe. O
  capítulo de *Performance Tips* e o de *Indexes* são material didático de
  verdade. Também disponível em PDF, ~3.000 páginas.
- **SQLite Documentation** — <https://sqlite.org/docs.html> 📖
  Curta, direta, com páginas de projeto explicando **por que** cada decisão foi
  tomada. Leia *Quirks, Caveats and Gotchas* e *The SQLite Query Optimizer
  Overview*.
- **DuckDB Documentation** — <https://duckdb.org/docs/> 📖
  Moderna, com exemplos executáveis.

---

## 7. Se você só puder ler três

| Situação | Leia |
|---|---|
| Quer usar SQL no trabalho, hoje | **SQL Cookbook** (Molinaro) |
| Sua consulta está lenta | **SQL Performance Explained** (Winand) — 📖 gratuito |
| Quer entender sistemas de dados | **Designing Data-Intensive Applications** (Kleppmann & Riccomini, 2ª ed., 2026) |

E, se você é engenheiro químico, acrescente **Montgomery** — porque a parte
difícil não é o SQL, é saber qual pergunta vale fazer.

---

## Autoteste

1. Qual livro desta lista está integralmente disponível de graça, e sobre o
   quê?
2. Qual livro é organizado por problema, e não por comando?
3. Qual é a ressalva ao ler C. J. Date?
4. Por que o Winand continua atual mesmo sendo de 2012?
5. Qual livro cobre CEP e por que ele importa para este curso?
6. Existe um bom livro sobre SQL para engenharia de processo? O que fazer?
7. Qual documentação oficial funciona como livro didático?

---

## Fontes e verificação (13/08/2026)

- *SQL Antipatterns* 2ª ed. (2022), Pragmatic Bookshelf:
  <https://pragprog.com/titles/bksqla/sql-antipatterns/>
- *SQL Performance Explained*, ISBN 978-3-9503078-2-5, gratuito em
  <https://use-the-index-luke.com>
- *Designing Data-Intensive Applications* 2ª ed., fevereiro de 2026, 672 p.:
  <https://martin.kleppmann.com/2026/03/24/designing-data-intensive-applications-2e.html>
- *Architecture of a Database System*, gratuito:
  <https://dsf.berkeley.edu/papers/fntdb07-architecture.pdf>

⚠️ **Edições e traduções brasileiras:** confirmei a existência das traduções
citadas, mas **não** a edição exata em catálogo hoje. Antes de comprar,
verifique a edição vigente na editora — traduções costumam estar uma ou duas
edições atrás do original.

---

*Próximo: [95-referencias.md](95-referencias.md).*
