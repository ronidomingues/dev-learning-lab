# 11 · História — de Ingres a PostgreSQL 18

`Nível: iniciante → intermediário` · `Última atualização: 11/08/2026`

Quase toda decisão "estranha" do PostgreSQL tem explicação histórica. Saber a história é o que
separa "é assim" de "é assim **porque**".

---

## Linha do tempo em uma tela

```
1970  Codd publica o modelo relacional         a teoria que funda tudo
1974  System R (IBM) e SEQUEL→SQL               a primeira implementação e a linguagem
1974  Ingres (Berkeley, Michael Stonebraker)    o avô do PostgreSQL
1979  Oracle v2                                  o primeiro relacional comercial de sucesso
1986  POSTGRES (Berkeley)                        Stonebraker recomeça: "post-Ingres"
1989  POSTGRES v1                                tipos estendidos, regras, sem SQL ainda
1994  Postgres95                                 acrescentam SQL; sai da universidade
1996  PostgreSQL 6.0                             renomeado; a comunidade assume
2000s PostgreSQL amadurece                        MVCC, WAL, PITR, tipos ricos
2005  Windows nativo (8.0)                        adoção corporativa cresce
2010  Replicação em streaming (9.0)               alta disponibilidade nativa
2014  JSONB (9.4)                                 documentos + relacional no mesmo banco
2016  Paralelismo de consulta (9.6)               usa vários núcleos
2017  Nova numeração: 10                          uma major por ano
2019  Particionamento maduro, pluggable storage (12)
2021  Ganha "DBMS of the Year" (2ª vez)           adoção dispara
2023  Explosão do pgvector                        PostgreSQL vira infraestrutura de IA
2025  PostgreSQL 18 (25/09)                       I/O assíncrona, uuidv7, OAuth, skip scan
2026  Série 18 é a estável atual
```

---

## Ato 1 — A pré-história relacional (1970–1985)

### Codd e a teoria (1970)

Edgar Codd, matemático da IBM, publica o modelo relacional (ver
[10-fundamentos.md](10-fundamentos.md)). A IBM, curiosamente, hesitou em adotá-lo — tinha o IMS
(hierárquico) vendendo bem, e o relacional ameaçava esse negócio. A tensão entre a teoria da casa
e o produto da casa atrasou a IBM.

### System R e a linguagem SQL (1974)

A IBM constrói o **System R** para provar a teoria de Codd. Dele nasce a linguagem **SEQUEL**
(*Structured English Query Language*), depois encurtada para **SQL** por questão de marca
registrada. System R introduziu o **otimizador de consultas baseado em custo** — a ideia de o banco
escolher sozinho o melhor plano — que é a alma de todo banco relacional até hoje.

### Ingres em Berkeley (1974)

Em paralelo, na Universidade da Califórnia em Berkeley, **Michael Stonebraker** e Eugene Wong
constroem o **Ingres**, outro banco relacional, com uma linguagem própria (QUEL). Ingres foi
academicamente influente e gerou empresas (Sybase, e daí o SQL Server da Microsoft, descendem dessa
linhagem). **Guarde o nome Stonebraker:** ele volta.

### Oracle comercializa (1979)

Larry Ellison lê os artigos do System R, percebe a oportunidade comercial que a IBM hesitava em
agarrar, e lança o Oracle — o primeiro banco relacional comercial de grande sucesso. A IBM só
lançaria o DB2 em 1983. **Lição que se repetiria:** quem executa a ideia vence quem a teve.

---

## Ato 2 — POSTGRES nasce (1986–1994)

### "Post-Ingres" (1986)

Stonebraker, insatisfeito com os limites do Ingres, recomeça em Berkeley um projeto chamado
**POSTGRES** — literalmente "post-Ingres". O objetivo não era só mais um relacional; era resolver o
que ele via como a maior limitação dos bancos da época: **eles só sabiam lidar com números e
texto**. Stonebraker queria um banco **extensível** — que o usuário pudesse ensinar tipos de dados
novos (geometria, por exemplo), operadores novos, e regras.

Essa ambição — **extensibilidade** — é o gene fundador do PostgreSQL, e explica por que, décadas
depois, ele consegue ganhar tipos como JSONB, PostGIS (geografia) e pgvector (IA) sem reescrever o
núcleo. **Nenhum concorrente foi projetado com essa flexibilidade no DNA.** É a razão técnica mais
profunda pela qual o PostgreSQL envelheceu tão bem.

Curiosidade: o POSTGRES original **não usava SQL**. Tinha uma linguagem própria, POSTQUEL.

### Postgres95 e a chegada do SQL (1994)

Dois estudantes de Berkeley, Andrew Yu e Jolly Chen, substituem o POSTQUEL por **SQL** e liberam
como **Postgres95**. O projeto sai da universidade e ganha o mundo.

### PostgreSQL 6.0 e a comunidade (1996)

O nome "Postgres95" era ruim para o longo prazo. Renomearam para **PostgreSQL** (Postgres + SQL), e
— decisão crucial — a versão saltou para **6.0**, reconhecendo as cinco versões do POSTGRES
acadêmico. Mais importante que o nome: um grupo global de voluntários assumiu o desenvolvimento,
formando o **PostgreSQL Global Development Group (PGDG)**.

> **A decisão que definiu tudo:** o PostgreSQL nunca teve dono. Não há uma empresa "PostgreSQL
> Inc." que controle o projeto (ao contrário do MySQL, comprado pela Oracle). É governado por uma
> comunidade meritocrática, sob uma licença permissiva (a *PostgreSQL License*, parecida com a
> BSD/MIT). Isso o protegeu de ser comprado, fechado ou ter o preço aumentado — o destino que
> assombra usuários de Oracle e o que aconteceu com o MySQL.

---

## Ato 3 — A maturação silenciosa (2000–2016)

O PostgreSQL passou os anos 2000 fazendo, com disciplina, o trabalho difícil e sem glamour de se
tornar confiável ao ponto de rodar bancos e governos.

| Ano | Versão | Marco | Por que importou |
|---|---|---|---|
| 2001 | 7.1 | **WAL** (Write-Ahead Log) | Base da durabilidade e da recuperação de crash |
| 2005 | 8.0 | **Windows nativo**, savepoints, PITR | Recuperação a um ponto no tempo; adoção corporativa |
| 2005 | 8.0 | **MVCC** consolidado | Leitores não bloqueiam escritores — concorrência real |
| 2006 | 8.1–8.2 | Melhorias de desempenho e bitmap scans | Competitivo com os comerciais |
| 2010 | 9.0 | **Replicação em streaming** e hot standby | Alta disponibilidade nativa, sem ferramenta externa |
| 2012 | 9.2 | Índices *covering*, tipo `range`, JSON | Início da fama de "canivete suíço" |
| 2014 | 9.4 | **JSONB** | Documentos indexáveis: relacional + NoSQL num banco só |
| 2016 | 9.6 | **Paralelismo de consulta** | Uma consulta usa vários núcleos |

**A reputação construída nesse período:** *o banco que não perde dados*. Enquanto a onda NoSQL dos
anos 2010 prometia escala abrindo mão de garantias, o PostgreSQL manteve o ACID e provou que dava
para escalar sem sacrificá-lo. Muitos que migraram para NoSQL voltaram.

O JSONB (2014) foi um ponto de virada cultural: ele respondeu ao principal argumento dos bancos de
documentos ("preciso de flexibilidade de esquema") **sem** abrir mão do relacional. A partir dali,
"use PostgreSQL para tudo até provar que precisa de outra coisa" virou conselho comum.

---

## Ato 4 — A era moderna e a explosão (2017–2026)

### Nova numeração (2017)

A partir da versão **10**, o PostgreSQL adotou numeração de major anual (10, 11, 12...) e um
**ciclo de release previsível: uma major por ano**, tipicamente em setembro, com ~5 anos de suporte
cada. Antes, "9.6 → 10" confundia (era 9.5, 9.6, e daí 10, não 9.7). A simplificação ajudou o
planejamento de quem opera.

| Ano | Versão | Marco |
|---|---|---|
| 2017 | 10 | Replicação lógica, particionamento declarativo, paralelismo melhor |
| 2018 | 11 | Particionamento maduro, procedimentos armazenados, JIT |
| 2019 | 12 | *Pluggable storage*, `GENERATED` columns, melhorias de partição |
| 2020 | 13 | Deduplicação de índices B-tree, vacuum paralelo |
| 2021 | 14 | Melhorias de JSON, conexões mais leves, pipelining |
| 2022 | 15 | `MERGE`, compressão de WAL, melhorias de RLS |
| 2023 | 16 | Paralelismo e replicação lógica bidirecional aprimorados |
| 2024 | 17 | `JSON_TABLE`, melhorias de VACUUM e de gestão de memória |
| **2025** | **18** | **I/O assíncrona (AIO)**, `uuidv7()`, colunas geradas virtuais, autenticação OAuth, *skip scan*, `RETURNING OLD/NEW` |

### A explosão do pgvector (2023–2026)

O evento externo que mais impulsionou o PostgreSQL na última década **não veio do banco** — veio da
IA. Com os modelos de linguagem (LLMs), surgiu a necessidade de guardar e buscar **embeddings**
(vetores de significado). A extensão **pgvector** permitiu fazer isso **dentro** do PostgreSQL, ao
lado dos dados de negócio, sem um banco vetorial separado.

O gene da extensibilidade de 1986 pagou o maior dividendo de sua história: enquanto surgiam
dezenas de "bancos vetoriais" novos, o PostgreSQL simplesmente **ganhou** a capacidade como
extensão, e levou junto tudo o que já tinha (transações, SQL, JOINs, confiabilidade). "Just use
Postgres" virou meme e estratégia. Ver [18-extensoes.md](18-extensoes.md) e
[65-estado-da-arte.md](65-estado-da-arte.md).

### O reconhecimento

O PostgreSQL foi eleito **"DBMS of the Year"** pelo DB-Engines múltiplas vezes (2017, 2018, 2020,
2023), e virou consistentemente o banco **mais desejado** e um dos mais usados nas pesquisas anuais
do Stack Overflow. De "o banco dos que entendem" passou a padrão da indústria.

---

## O que a história ensina

**1. Extensibilidade envelhece melhor que funcionalidade.** A aposta de Stonebraker em 1986 — um
banco que se pode *ensinar* — é por que o PostgreSQL absorveu JSON, geografia e IA sem se reinventar.
Os concorrentes tiveram que correr atrás; ele só instalou uma extensão.

**2. Governança sem dono protege o investimento.** O MySQL foi comprado pela Oracle e sua evolução
travou (gerando o fork MariaDB). O PostgreSQL, sem dono, não pode ser comprado nem fechado. Quem
construiu sobre ele em 2005 continua seguro em 2026.

**3. Correção paga a longo prazo.** A obsessão por ACID e por não perder dados custou velocidade em
alguns momentos e fez o Postgres parecer "conservador" na era NoSQL. Uma década depois, é
exatamente essa reputação que o tornou a escolha padrão.

**4. Quem executa vence quem tem a ideia.** A IBM teve a teoria (Codd) e hesitou; a Oracle
executou. Stonebraker teve a visão da extensibilidade; a comunidade PGDG a executou por 30 anos. A
lição vale para o PostgreSQL e contra ele.

---

## Autoteste

1. Qual limitação dos bancos da época o POSTGRES de 1986 queria resolver, e por que essa escolha
   foi decisiva 40 anos depois?
2. Quem é Michael Stonebraker e qual é a ligação entre Ingres e PostgreSQL?
3. O POSTGRES original usava SQL? O que mudou em 1994?
4. Por que a governança "sem dono" do PostgreSQL foi mais importante que qualquer funcionalidade?
   Compare com o destino do MySQL.
5. O que o JSONB (2014) representou culturalmente na disputa com os bancos NoSQL?
6. Que evento **externo ao banco** mais impulsionou o PostgreSQL na década de 2020, e por que o
   gene de 1986 foi decisivo nele?
7. O que mudou na numeração e no ciclo de release a partir da versão 10, e por quê?
8. Cite três marcos da versão 18 (2025).
9. Por que a reputação de "conservador" do PostgreSQL na era NoSQL acabou virando vantagem?
10. Que padrão histórico ("quem executa vence quem tem a ideia") aparece pelo menos duas vezes
    nesta história?

---

### Fontes consultadas (11/08/2026)

- [PostgreSQL — History](https://www.postgresql.org/docs/current/history.html) e [About](https://www.postgresql.org/about/) — cronologia oficial
- [PostgreSQL 18 release notes](https://www.postgresql.org/docs/18/release-18.html) — marcos da versão 18 (25/09/2025)
- [PostgreSQL — Versioning policy](https://www.postgresql.org/support/versioning/) — ciclo anual e ~5 anos de suporte
