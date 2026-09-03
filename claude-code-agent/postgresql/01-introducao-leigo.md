# 01 · PostgreSQL para quem nunca ouviu falar

`Nível: iniciante` · `Sem jargão` · `Última atualização: 11/08/2026`

---

## O problema que existe antes de qualquer banco de dados

Imagine uma papelaria. No começo, o dono anota as vendas num caderno. Funciona — até o dia em
que ele precisa responder "quanto vendi de canetas azuis em março?" e tem que folhear 200
páginas à mão. Ou até dois funcionários escreverem no caderno ao mesmo tempo e um riscar o que o
outro anotou. Ou até o caderno cair na poça d'água.

Todo negócio que cresce descobre a mesma coisa: **guardar informação é fácil; guardar de um jeito
que você consiga encontrar, confiar e usar por muita gente ao mesmo tempo é difícil.**

Um **banco de dados** é a resposta a esse problema. E o PostgreSQL é um dos melhores bancos de
dados que existem — gratuito, aberto e usado desde um blog pessoal até os sistemas de bancos,
governos e das maiores empresas de tecnologia do mundo.

> **Definição informal:** um banco de dados é um programa cujo único trabalho é **guardar dados
> de forma organizada e devolvê-los rápido, sem perdê-los e sem se confundir quando muita gente
> mexe ao mesmo tempo.**

---

## A analogia da planilha que cresceu demais

Quase todo mundo já usou uma planilha (Excel, Google Sheets). Uma planilha é uma tabela: linhas e
colunas. Ela é ótima até três coisas acontecerem:

1. **Ela fica grande.** Um milhão de linhas e a planilha trava.
2. **Muita gente mexe junto.** Dois editando a mesma célula = confusão.
3. **Você tem várias planilhas que se relacionam.** Uma de clientes, uma de pedidos, uma de
   produtos. Manter tudo consistente à mão vira um pesadelo — apagou um cliente, e os pedidos
   dele ficam órfãos apontando para o nada.

O PostgreSQL é o que uma planilha gostaria de ser quando crescesse:

| | Planilha | PostgreSQL |
|---|---|---|
| Tamanho | trava com milhões de linhas | bilhões de linhas, sem suar |
| Uso simultâneo | um por vez, na prática | milhares de pessoas ao mesmo tempo |
| Relações entre tabelas | manuais e frágeis | garantidas pelo próprio banco |
| Perguntas complexas | fórmulas que ninguém entende | uma linguagem feita para perguntar (SQL) |
| Segurança do dado | "salvei antes de fechar?" | não perde dado nem se faltar luz no meio |

O nome técnico dessa categoria é **SGBD** — *Sistema de Gerenciamento de Banco de Dados*. É o
programa que administra os dados. O PostgreSQL é um SGBD.

---

## O que é "relacional"?

Você vai ouvir "banco de dados **relacional**" o tempo todo. A palavra assusta, mas a ideia é
simples e vem de uma observação de 1970.

Os dados do mundo real vêm em **coisas** que se **relacionam**: clientes *fazem* pedidos; pedidos
*contêm* produtos; produtos *pertencem* a categorias. Um banco relacional guarda cada tipo de
coisa numa **tabela** própria e registra as relações entre elas de forma explícita.

```
   CLIENTES                 PEDIDOS                    PRODUTOS
 ┌────┬────────┐         ┌────┬──────────┬──────┐    ┌────┬──────────┬───────┐
 │ id │ nome   │         │ id │ cliente  │ data │    │ id │ nome     │ preço │
 ├────┼────────┤         ├────┼──────────┼──────┤    ├────┼──────────┼───────┤
 │  1 │ Ana    │◀───┐    │ 10 │    1     │ 3/8  │    │  5 │ Caneta   │  2,50 │
 │  2 │ Bruno  │    └────┤ 11 │    1     │ 4/8  │    │  6 │ Caderno  │ 12,00 │
 └────┴────────┘         └────┴──────────┴──────┘    └────┴──────────┴───────┘
                            "o pedido 10 é da Ana"
```

A coluna `cliente` do pedido guarda o **id** do cliente (`1`), não o nome inteiro. Isso é uma
**chave estrangeira**: um apontamento de uma tabela para outra. O banco garante que você não
consiga criar um pedido para o cliente `99` se esse cliente não existir. Essa garantia — que a
planilha não tem — é metade do valor de um banco relacional.

A palavra "relacional", curiosamente, **não** vem de "as tabelas se relacionam" (embora se
relacionem). Vem da matemática: em teoria dos conjuntos, uma tabela **é** uma "relação". Voltamos
a isso em [10-fundamentos.md](10-fundamentos.md) — por ora, "relacional = organizado em tabelas
que se conectam" já serve.

---

## Como você conversa com o banco: SQL

Você não abre o PostgreSQL e clica em botões. Você **pergunta** a ele, numa linguagem chamada
**SQL** (*Structured Query Language*, "linguagem de consulta estruturada"). E o mais bonito: SQL
foi projetada para parecer quase inglês.

Quer os nomes de todos os clientes?

```sql
SELECT nome FROM clientes;
```

Quer só os clientes chamados Ana?

```sql
SELECT nome FROM clientes WHERE nome = 'Ana';
```

Quer somar o valor de todos os pedidos de cada cliente?

```sql
SELECT cliente, SUM(valor)
FROM pedidos
GROUP BY cliente;
```

Isso é o suficiente para você entender o que está acontecendo mesmo sem nunca ter estudado. **É
essa legibilidade que fez o SQL sobreviver 50 anos** e continuar sendo a forma como o mundo fala
com seus dados. Você aprende o básico numa tarde; a maestria leva anos — mas o básico já resolve
muita coisa.

---

## Então o que é o PostgreSQL, especificamente?

Existem muitos SGBDs relacionais: MySQL, SQL Server (Microsoft), Oracle, SQLite, e o PostgreSQL.
Todos falam SQL. O que distingue o PostgreSQL:

- **É livre e aberto.** Ninguém é dono. A licença permite usar para qualquer coisa, inclusive
  vender, sem pagar nada e sem pedir permissão. Não há uma empresa que possa te aumentar o preço
  amanhã (ao contrário de Oracle e SQL Server).
- **É extremamente correto.** A comunidade do PostgreSQL tem uma obsessão saudável por **não
  perder nem corromper dados**, nem em situações extremas (queda de energia, disco cheio, dois
  processos brigando). Essa reputação foi construída em décadas.
- **Faz muito mais que tabelas.** Ele guarda documentos JSON, coordenadas geográficas, vetores
  para inteligência artificial, texto para busca — e você estende o que ele sabe fazer. É quase
  uma plataforma, não só um "depósito de tabelas".
- **É maduro.** Nasceu em 1986 na Universidade da Califórnia em Berkeley. São ~40 anos de
  desenvolvimento. Ver [11-historia.md](11-historia.md).

> **"Postgres" ou "PostgreSQL"?** São a mesma coisa. O nome oficial é **PostgreSQL** (pronuncia-se
> "post-gres-Q-L", ou "post-gres" no dia a dia). "Postgres" é o apelido carinhoso, e vem do nome
> original do projeto. Use o que quiser; todo mundo entende.

---

## Um retrato do que ele faz, em 30 segundos

```sql
-- Cria uma tabela (uma vez)
CREATE TABLE tarefas (
    id      SERIAL PRIMARY KEY,     -- número que se autoincrementa
    titulo  TEXT NOT NULL,          -- obrigatório
    feita   BOOLEAN DEFAULT false,  -- padrão: não feita
    criada  TIMESTAMPTZ DEFAULT now()
);

-- Guarda dados
INSERT INTO tarefas (titulo) VALUES ('Aprender PostgreSQL');

-- Pergunta
SELECT titulo FROM tarefas WHERE feita = false;

-- Atualiza
UPDATE tarefas SET feita = true WHERE id = 1;

-- Remove
DELETE FROM tarefas WHERE id = 1;
```

Essas quatro operações — inserir, ler, atualizar, remover — têm até uma sigla: **CRUD** (*Create,
Read, Update, Delete*). Se você entende CRUD, entende 80% do que se faz com um banco no dia a dia.

---

## Para que as pessoas usam PostgreSQL de verdade

- **A base de quase todo aplicativo web e mobile.** Quando você posta uma foto, comenta, compra
  algo online — quase sempre há um banco relacional guardando aquilo, e muitas vezes é o
  PostgreSQL.
- **Sistemas financeiros e governamentais**, onde perder ou corromper um dado é inaceitável.
- **Análise de dados** — responder perguntas complexas sobre grandes volumes.
- **Aplicações de mapa e geolocalização** (com a extensão PostGIS — o PostgreSQL é o melhor banco
  de dados geográfico livre que existe).
- **Aplicações de inteligência artificial** — guardar e buscar "vetores" de similaridade (com a
  extensão pgvector), o que explodiu com os modelos de linguagem.
- **Homelab e projetos pessoais** — é o banco padrão de boa parte do que se auto-hospeda.

---

## Onde o PostgreSQL **não** é a melhor escolha

Honestidade desde o começo — nenhuma ferramenta serve para tudo:

- **Um app de celular offline, simples, sem servidor** → **SQLite** é melhor (um arquivo único,
  sem servidor rodando). Aliás, o SQLite é o banco mais instalado do planeta, e está no seu
  celular agora.
- **Cache que precisa ser absurdamente rápido e pode ser perdido** → **Redis** (guarda em
  memória) complementa, não substitui.
- **Volume gigantesco de dados só para ler, tipo análise de petabytes** → bancos "colunares"
  (ClickHouse, BigQuery) podem ganhar em nichos específicos.
- **Você não precisa de garantias fortes e quer só um cache de documentos flexível** → às vezes um
  banco de documentos serve, embora o PostgreSQL faça JSON tão bem que essa fronteira quase
  sumiu.

*Opinião profissional, e não é consenso universal, mas está perto:* **na dúvida, comece com
PostgreSQL.** Ele é a escolha padrão sensata para a imensa maioria dos projetos, e o custo de
trocar depois — se você realmente precisar — é menor que o custo de escolher errado um banco
exótico no começo.

---

## O vocabulário mínimo, tudo definido

| Termo | Definição de uma linha |
|---|---|
| **Banco de dados** | Coleção organizada de dados; também, o programa que a gerencia |
| **SGBD** | *Sistema de Gerenciamento de Banco de Dados* — o programa (ex.: PostgreSQL) |
| **Relacional** | Organizado em tabelas que se conectam por chaves |
| **Tabela** | Uma grade de linhas e colunas, sobre um tipo de coisa |
| **Linha** (registro/tupla) | Um item na tabela: um cliente, um pedido |
| **Coluna** (campo/atributo) | Uma propriedade: nome, preço, data |
| **Chave primária** | A coluna que identifica cada linha de forma única (o `id`) |
| **Chave estrangeira** | Uma coluna que aponta para a chave primária de outra tabela |
| **SQL** | A linguagem com que você fala com o banco |
| **Consulta** (*query*) | Uma pergunta ou comando em SQL |
| **CRUD** | *Create, Read, Update, Delete* — as quatro operações básicas |
| **Índice** | Uma estrutura que faz o banco encontrar dados rápido (como o índice de um livro) |
| **Transação** | Um conjunto de operações que acontecem "tudo ou nada" |
| **Servidor** | O processo do PostgreSQL rodando, esperando conexões |
| **Cliente** | O programa que se conecta ao servidor (ex.: `psql`, sua aplicação) |

Glossário completo em [GLOSSARIO.md](GLOSSARIO.md).

---

## O que fazer agora

1. Só quer experimentar sem instalar nada → [03-instalacao.md](03-instalacao.md), seção
   "Alternativa sem instalar nada".
2. Quer instalar → [02-pre-requisitos.md](02-pre-requisitos.md), depois
   [03-instalacao.md](03-instalacao.md).
3. Quer entender o modelo por trás antes de mexer → [10-fundamentos.md](10-fundamentos.md).

---

## Autoteste

1. Explique, sem usar a palavra "banco de dados", o problema que o PostgreSQL resolve.
2. Cite três coisas que uma planilha não faz bem e um banco relacional faz.
3. O que é uma chave estrangeira, e que garantia ela dá que a planilha não dá?
4. O que significa CRUD? Dê o comando SQL de cada uma das quatro operações.
5. "PostgreSQL" e "Postgres" são coisas diferentes? E "relacional" vem de quê?
6. Cite dois casos em que o PostgreSQL **não** é a melhor escolha, e o que usar no lugar.
7. Por que "na dúvida, comece com PostgreSQL" é uma recomendação razoável?
