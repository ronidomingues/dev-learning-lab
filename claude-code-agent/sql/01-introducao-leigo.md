# 01 — O que é SQL, para um leigo total

Nível: iniciante · Data: 13/08/2026

Este arquivo não supõe **nada**. Nem programação, nem banco de dados, nem
inglês. Se você sabe usar uma planilha, já sabe mais do que o necessário para
ler daqui até o fim.

---

## 1. A cena que faz o SQL existir

Imagine o almoxarifado de uma fábrica.

No começo, o controle é um caderno. O almoxarife anota o que entra e o que sai.
Quando alguém pergunta "quanto ainda tem de soda cáustica?", ele folheia o
caderno e soma. Funciona — para um caderno, um almoxarife e uma pergunta por
dia.

Agora cresça a fábrica. São seis almoxarifados, quatro turnos, oito mil itens,
e as perguntas viram:

- Quanto de cada matéria-prima está com validade vencendo nos próximos 30 dias?
- Quais itens ficaram abaixo do estoque mínimo em algum momento do mês passado?
- Qual fornecedor entregou fora da especificação com mais frequência este ano?

Nenhuma dessas perguntas cabe em folhear um caderno. E repare no que elas têm
em comum: todas são a mesma estrutura — **filtre, cruze, agrupe, some, ordene**.

O SQL é uma linguagem inventada para escrever exatamente esse tipo de pergunta,
de um jeito que uma máquina consiga responder sozinha, sobre milhões de linhas,
em milissegundos.

---

## 2. A definição, agora que dá para entender

**SQL** (lê-se "és-cu-éle" no Brasil, ou "síquel" em inglês) quer dizer
*Structured Query Language* — Linguagem Estruturada de Consulta.

É a linguagem padrão para **guardar, alterar e perguntar coisas** a um banco de
dados relacional.

Um **banco de dados relacional** é, para todos os efeitos práticos, um conjunto
de **tabelas** — cada uma com colunas e linhas, exatamente como uma aba de
planilha — mais um conjunto de **regras** que garantem que os dados fazem
sentido, mais um **motor** capaz de responder perguntas cruzando essas tabelas.

Uma tabela de leituras de sensor de uma planta química se parece com isto:

| tag_id | ts (instante) | valor | unidade |
|---|---|---|---|
| TI-101 | 2026-07-01 10:00:00 | 179,8 | degC |
| TI-101 | 2026-07-01 10:01:00 | 180,3 | degC |
| PI-101 | 2026-07-01 10:00:00 | 2,71 | bar |

E uma pergunta em SQL sobre ela se parece com isto:

```sql
SELECT AVG(valor)
  FROM leitura
 WHERE tag_id = 'TI-101'
   AND ts >= '2026-07-01 10:00:00'
   AND ts <  '2026-07-01 11:00:00';
```

Leia em voz alta, palavra por palavra:

> **SELECIONE** a média do valor **DA** tabela leitura **ONDE** o tag é TI-101
> **E** o instante é a partir das 10:00 **E** anterior às 11:00.

É isso. Essa frase é um programa completo, e ela é literalmente inglês
estruturado. Foi projetada assim de propósito, e a seção 4 conta por quê.

---

## 3. A ideia central: você diz O QUÊ, não COMO

Esta é a característica que separa o SQL de quase tudo que você já viu.

Se fosse escrever isso em uma linguagem comum — Python, C, VBA — você teria que
dizer **como** fazer:

```python
# COMO fazer: passo a passo, você comanda cada etapa
soma = 0
n = 0
for linha in arquivo:                      # percorra tudo
    if linha.tag == "TI-101" and dentro_do_intervalo(linha.ts):
        soma += linha.valor                # some
        n += 1                             # conte
media = soma / n                           # divida
```

Em SQL você diz apenas **o quê** quer:

```sql
SELECT AVG(valor) FROM leitura WHERE tag_id = 'TI-101' AND ...;
```

Quem decide *como* — em que ordem ler, qual índice usar, se vale a pena usar
quatro núcleos do processador, se cabe na memória — é um componente do banco
chamado **otimizador de consultas** (*query optimizer*). Ele reescreve sua
pergunta em um plano de execução, e o faz melhor do que você faria à mão na
esmagadora maioria dos casos.

Isso chama-se **linguagem declarativa**. As consequências são grandes:

- Uma consulta escrita em 1995 continua rodando hoje, mais rápido, sem uma
  vírgula alterada — porque o otimizador melhorou por baixo dela.
- Você escreve muito menos, e escreve o que quer, não a mecânica.
- **Mas** você perde o controle direto do desempenho. Duas consultas que dão o
  mesmo resultado podem diferir mil vezes em tempo. Aprender SQL de verdade é,
  em boa parte, aprender a *cooperar* com o otimizador em vez de brigar com ele.

Analogia honesta: pedir um táxi é declarativo ("me leve à Rua X, 120"); dirigir
é imperativo. O táxi geralmente escolhe um caminho melhor que o seu, exceto nos
dias em que ele escolhe uma avenida interditada e você fica preso. Boa parte
deste curso é aprender a reconhecer esses dias.

---

## 4. Por que SQL existe (a versão curta; a longa está no arquivo 11)

Em 1970, **Edgar F. "Ted" Codd**, matemático inglês trabalhando na IBM,
publicou um artigo de 11 páginas chamado *A Relational Model of Data for Large
Shared Data Banks*. Ele apontava um problema concreto: nos bancos de dados da
época, o programa precisava saber **onde e como** o dado estava fisicamente
gravado. Mudou o arquivo, quebraram todos os programas.

A proposta de Codd foi separar as duas coisas:

- **o que os dados significam** (relações — as tabelas, com regras matemáticas
  claras), de
- **como estão guardados** (arquivos, ponteiros, discos).

Isso se chama **independência de dados**, e é a razão de o modelo relacional
ter durado 56 anos e contando.

Na IBM, Donald Chamberlin e Raymond Boyce criaram em 1974 uma linguagem para
operar esse modelo. Chamaram de **SEQUEL** (*Structured English Query
Language*) — a ênfase em "English" era proposital: a linguagem foi desenhada
para que **quem não é programador** conseguisse escrever consultas. Por
conflito de marca registrada com uma empresa britânica, virou **SQL**.

Foi padronizada pela ANSI em 1986 e pela ISO em 1987, e continua sendo
atualizada — a edição vigente é **SQL:2023** (ISO/IEC 9075), que acrescentou
consultas em grafo de propriedades e JSON nativo.

O ponto de virada comercial foi 1979, quando uma empresa pequena chamada
*Relational Software* lançou o primeiro SQL comercial e depois adotou o nome
do produto: **Oracle**.

---

## 5. Onde SQL aparece na sua vida (e você não sabia)

- Todo aplicativo de celular que guarda algo localmente usa **SQLite** —
  o banco SQL mais implantado do planeta, com mais de um trilhão de cópias em
  uso. Está no Android, no iOS, no Firefox, no Chrome, em aviões, em carros.
- Todo sistema de gestão empresarial (**SAP**, **TOTVS**, **Oracle EBS**)
  guarda tudo em bancos SQL. Todo relatório desses sistemas é SQL por baixo.
- **Power BI**, **Tableau** e **Qlik** geram SQL a partir do que você arrasta
  na tela. Quando o relatório fica lento, o problema é o SQL gerado.
- O **PIMS** / historiador da sua planta (PI System, Aspen IP.21, Honeywell
  PHD) expõe interface SQL para relatórios e integrações.
- O **LIMS** do laboratório é um banco SQL com uma tela na frente.
- Cada consulta ao Google, ao banco, ao INSS, à Receita: SQL no meio do caminho.

---

## 6. Para que serve, concretamente, para um engenheiro químico

Esta é a resposta curta. O arquivo [30-engenharia-quimica.md](30-engenharia-quimica.md)
tem a resposta longa, com casos e código.

| Você quer | Hoje você provavelmente faz | Com SQL |
|---|---|---|
| Média horária de temperatura do último mês | Exporta CSV do historiador, abre no Excel, tabela dinâmica | Uma consulta de 4 linhas, roda em milissegundos |
| Comparar rendimento de 200 bateladas | Uma planilha por batelada, consolida na mão | Uma consulta, roda toda segunda-feira sozinha |
| Cruzar resultado de laboratório com condição de processo | Copia e cola entre dois sistemas | Uma junção (`JOIN`) |
| Achar todas as vezes que a temperatura passou do limite | Rola o gráfico do historiador com o olho | Um `WHERE` |
| Fechar balanço de massa do mês | Planilha com 30 abas | Um `GROUP BY` |
| Relatório mensal de OEE | Três dias de trabalho manual | Uma consulta agendada |

Os três motivos pelos quais isso importa mais do que parece:

1. **Escala.** O Excel trava por volta de 1 milhão de linhas. Um mês de dados
   de 200 tags a cada minuto são 8,6 milhões de linhas. SQL não pisca.
2. **Reprodutibilidade.** A planilha que o colega montou e ninguém entende é o
   maior passivo técnico de qualquer área de processo. Uma consulta SQL é um
   texto: versionável, revisável, auditável, e ela **diz o que faz**.
3. **Auditoria.** Quando o auditor da ANVISA, do FDA ou da ISO perguntar de
   onde saiu aquele número, "da minha planilha" é uma resposta ruim. "Desta
   consulta, contra esta base, com este critério escrito" é uma resposta boa.

---

## 7. O que SQL **não** é (para você não perder tempo)

- **SQL não é um banco de dados.** É a linguagem. O banco é o programa que a
  entende: PostgreSQL, SQLite, Oracle, SQL Server, MySQL, DuckDB.
- **SQL não é linguagem de programação de propósito geral.** Você não escreve
  um simulador de coluna de destilação em SQL. (Tecnicamente dá — com SQL
  recursivo ele é Turing-completo — mas seria uma escolha ruim. Ver
  [60-teoria-avancada.md](60-teoria-avancada.md).)
- **SQL não substitui Python, MATLAB ou Aspen.** Ele *alimenta* essas
  ferramentas. O padrão profissional é: SQL para trazer e agregar o dado certo,
  Python/MATLAB para o cálculo pesado e o gráfico.
- **SQL não é igual em todos os bancos.** Existe um padrão ISO, e todo mundo o
  segue *quase*. O núcleo (uns 80%) é idêntico; as bordas divergem. Ver
  [23-dialetos.md](23-dialetos.md).
- **"NoSQL" não é o inimigo do SQL.** É uma família de bancos não relacionais
  (MongoDB, Redis, Cassandra) para problemas diferentes. E, ironia registrada,
  a maioria deles acabou ganhando uma linguagem de consulta parecida com SQL.

---

## 8. Um exemplo do começo ao fim, sem nada instalado

Se quiser sentir o gosto agora, sem instalar nada, abra
<https://sqlime.org> ou <https://sqliteonline.com> e cole:

```sql
-- Cria uma tabela de leituras de um reator
CREATE TABLE leitura (
    tag_id TEXT,
    ts     TEXT,
    valor  REAL
);

-- Coloca seis leituras
INSERT INTO leitura VALUES
  ('TI-101', '2026-07-01 10:00:00', 179.8),
  ('TI-101', '2026-07-01 10:01:00', 180.3),
  ('TI-101', '2026-07-01 10:02:00', 196.4),
  ('PI-101', '2026-07-01 10:00:00',   2.71),
  ('PI-101', '2026-07-01 10:01:00',   2.74),
  ('PI-101', '2026-07-01 10:02:00',   3.42);

-- Pergunta 1: média e pico de cada instrumento
SELECT tag_id, AVG(valor) AS media, MAX(valor) AS pico
  FROM leitura
 GROUP BY tag_id;
```

Resultado:

```
tag_id | media             | pico
-------+-------------------+------
PI-101 | 2.956666666666667 | 3.42
TI-101 | 185.5             | 196.4
```

(A quantidade de casas decimais que aparece depende do cliente que você usa —
o `sqlite3` de linha de comando, o Python e o navegador formatam o mesmo
número de jeitos ligeiramente diferentes. O número é o mesmo; a impressão, não.
Isso já é uma primeira lição sobre ponto flutuante: ver
[17-tipos-e-nulos.md](17-tipos-e-nulos.md).)

```sql
-- Pergunta 2: quando a temperatura passou de 195 °C?
SELECT ts, valor
  FROM leitura
 WHERE tag_id = 'TI-101'
   AND valor > 195;
```

```
ts                  | valor
--------------------+------
2026-07-01 10:02:00 | 196.4
```

Você acabou de criar um banco, carregar dados, agregar e filtrar. Isso é,
literalmente, o que se faz o dia inteiro com SQL — só que com mais linhas e
mais tabelas.

---

## 9. Quanto tempo leva para aprender

Honestamente, e sem otimismo de vendedor de curso:

| Nível | O que você consegue fazer | Tempo realista |
|---|---|---|
| Sobrevivência | `SELECT`, `WHERE`, `ORDER BY`, `GROUP BY` numa tabela | 4 a 8 horas |
| Útil no trabalho | `JOIN` de 2–3 tabelas, subconsultas, datas | 20 a 40 horas |
| Autônomo | CTEs, funções de janela, ler plano de execução | 80 a 150 horas |
| Avançado | Modelagem, índices, transações, otimização | 1 a 2 anos de uso real |
| Especialista | Interno do motor, teoria relacional, escala | 5+ anos |

Para um engenheiro químico que quer parar de depender de exportar CSV, o alvo
é o nível "útil no trabalho": **de 20 a 40 horas**, e a maior parte disso é
prática, não leitura. Ver [02-pre-requisitos.md](02-pre-requisitos.md).

---

## Autoteste

1. Explique com suas palavras a diferença entre "linguagem declarativa" e
   "linguagem imperativa", usando um exemplo que não seja o do táxi.
2. O que Codd propôs separar em 1970, e por que isso importava?
3. Por que a linguagem se chamou originalmente SEQUEL, e o que o nome revela
   sobre a intenção dos autores?
4. Cite três lugares onde SQL está rodando agora sem que ninguém veja.
5. Dê um exemplo, do seu trabalho, de uma pergunta que hoje você responde no
   Excel e que caberia numa consulta SQL.
6. Por que "SQL não é um banco de dados" — o que é o quê?
7. Se o otimizador escolhe o "como", por que ainda é preciso saber otimizar?

---

*Próximo: [02-pre-requisitos.md](02-pre-requisitos.md) — o que ter e saber antes
de começar. Ou pule direto para [03-instalacao.md](03-instalacao.md) se já tem
pressa.*
