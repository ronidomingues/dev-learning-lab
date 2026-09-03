# 11 — História: como o SQL chegou aqui

Nível: iniciante → intermediário · Data: 13/08/2026

História não é enfeite. Quase toda coisa esquisita do SQL — e há muitas — tem
uma explicação histórica, e saber a explicação transforma "isso é bizarro" em
"ah, faz sentido". Este arquivo é a coleção dessas explicações.

---

## 1. Antes de 1970: navegar ponteiros

Os primeiros bancos de dados de verdade nasceram do programa Apollo. O **IMS**
da IBM (1966) foi construído para gerenciar a lista de materiais do foguete
Saturno V — milhões de peças em hierarquia. Ele guardava dados em **árvore**:
para achar um dado, o programa navegava do pai para o filho, seguindo ponteiros.

Depois veio o **modelo de rede**, formalizado pelo consórcio **CODASYL** (1969),
que permitia mais de um pai. Mais flexível, e mais complicado.

**Como era programar nisso:**

```cobol
MOVE 'R-101' TO REACTOR-ID.
FIND REACTOR RECORD BY KEY.
FIND FIRST BATCH WITHIN REACTOR-BATCH-SET.
PERFORM UNTIL END-OF-SET
    FIND NEXT BATCH WITHIN REACTOR-BATCH-SET
    ...
END-PERFORM.
```

Você escrevia o **caminho de acesso**. O programador era o otimizador. E o
custo real disso: mudou a estrutura física do arquivo? Reescreva e recompile
**todos** os programas que a tocam. Em 1970, uma empresa grande tinha centenas.

O problema não era desempenho — a navegação era rápida. O problema era
**manutenção**, e ele crescia com o tempo.

---

## 2. 1970: Codd publica

**Edgar Frank Codd** (1923–2003), inglês, piloto da RAF na Segunda Guerra,
matemático, funcionário da IBM. Em junho de 1970 publica em *Communications of
the ACM*:

> **"A Relational Model of Data for Large Shared Data Banks"** —
> Comm. ACM 13(6), pp. 377–387. Legalmente disponível:
> <https://dl.acm.org/doi/10.1145/362384.362685>

Onze páginas. É um dos artigos mais influentes da história da computação, e é
legível — se você tem base de matemática de engenharia, consegue lê-lo.

A tese: represente os dados como **relações matemáticas** (no sentido da teoria
dos conjuntos), e o programa deixa de precisar saber a estrutura física.

**A IBM ignorou.** Tinha o IMS vendendo bem, e uma linguagem declarativa
parecia um brinquedo acadêmico — lenta demais para o hardware da época, o que
era verdade. Codd passou anos fazendo lobby interno. O que finalmente moveu a
IBM foi a concorrência.

---

## 3. 1974: SEQUEL, e o nome que teve de mudar

No laboratório da IBM em San José, **Donald Chamberlin** e **Raymond Boyce**
projetam uma linguagem para o modelo de Codd. O nome: **SEQUEL** —
*Structured English Query Language*.

A ênfase em **English** era deliberada e é a chave para entender a linguagem
inteira: Chamberlin queria que **contadores e analistas**, não programadores,
escrevessem consultas. O cálculo relacional de Codd (`ALPHA`) era matemática
pura, ilegível para quem não era matemático. SEQUEL era matemática disfarçada
de inglês.

É por isso que se escreve `SELECT ... FROM ... WHERE ...` e não
`σ(π(R))`. **A sintaxe verbosa do SQL é uma decisão de acessibilidade tomada
em 1974, e funcionou:** é a única linguagem de computação que gente de
negócio, engenharia e laboratório escreve todo dia sem se considerar
programadora.

**Por que virou "SQL":** a empresa britânica *Hawker Siddeley* já tinha a marca
"SEQUEL". Trocaram para SQL. Até hoje metade do mundo pronuncia "síquel" (pelo
nome antigo) e a outra metade soletra "és-cu-éle". Nenhuma está errada.

O projeto de pesquisa que implementou tudo isso chamou-se **System R** (1974–
1979). Dele saiu não só o SQL, mas o **otimizador baseado em custo** (o artigo
de Selinger et al., 1979) e o gerenciador de transações — as duas peças de
engenharia que fazem bancos relacionais funcionarem até hoje. Ver
[95-referencias.md](95-referencias.md).

---

## 4. 1977–1979: Ellison lê o artigo e vende antes da IBM

**Larry Ellison**, Bob Miner e Ed Oates fundam a *Software Development
Laboratories*. Ellison lê os artigos do System R — publicados abertamente pela
IBM — e percebe o que a IBM não percebeu: dá para vender isso **agora**.

Em 1979 lançam o **Oracle V2** (não houve V1; começaram na 2 para parecer mais
maduro — é a história que a própria empresa conta). Primeiro banco relacional
comercial. A IBM só lança o **SQL/DS** em 1981 e o **DB2** em 1983.

A empresa se renomeia com o nome do produto: **Oracle**.

**A lição, que se repete até hoje:** quem publica a pesquisa nem sempre é quem
captura o valor. A IBM inventou o modelo relacional, o SQL, o otimizador de
custo e o log de transações — e o mercado de bancos relacionais foi da Oracle.

---

## 5. 1986–2023: a padronização

| Edição | Ano | O que trouxe de importante |
|---|---|---|
| SQL-86 | 1986 | Primeiro padrão ANSI; basicamente o núcleo do System R |
| SQL-89 | 1989 | Integridade referencial (`FOREIGN KEY`) |
| **SQL-92** | 1992 | O grande. `JOIN` explícito, `CAST`, subconsultas, `CASE`, tipos de data. **É o que a maioria das pessoas chama de "SQL"** |
| SQL:1999 | 1999 | Gatilhos, tipos definidos pelo usuário, **CTEs recursivas**, `ROLLUP`/`CUBE` |
| SQL:2003 | 2003 | **Funções de janela** (`OVER`), XML, `MERGE`, colunas geradas |
| SQL:2006 | 2006 | XQuery |
| SQL:2008 | 2008 | `TRUNCATE`, `FETCH FIRST`, `INSTEAD OF` |
| SQL:2011 | 2011 | **Tabelas temporais** (versionamento por período) |
| SQL:2016 | 2016 | **JSON**, casamento de padrão em linha (`MATCH_RECOGNIZE`), funções polimórficas |
| SQL:2019 | 2019 | Arrays multidimensionais |
| **SQL:2023** | 2023 | **SQL/PGQ** (consulta em grafo de propriedades), tipo `JSON` nativo, `UNIQUE NULLS DISTINCT` |

Fonte: ISO/IEC 9075. Uma correção técnica ao SQL/PGQ, a
**ISO/IEC 9075-16:2023/Cor 1:2026**, foi publicada em agosto de 2026.

### Fatos incômodos sobre o padrão

1. **Ele é pago.** O texto oficial custa da ordem de CHF 200 por parte, e são
   várias partes. Existe uma linguagem de programação usada por milhões de
   pessoas cuja especificação a maioria dessas pessoas nunca leu porque é
   caro. Os rascunhos finais (*drafts*) circulam gratuitamente e são
   praticamente idênticos — ver [95-referencias.md](95-referencias.md).
2. **Nenhum banco implementa tudo.** Nem perto. O padrão tem centenas de
   recursos opcionais organizados em pacotes de conformidade.
3. **O padrão frequentemente ratifica o que já existia.** Funções de janela
   estavam em produtos anos antes de 2003. `LIMIT` é universal, existe desde
   sempre, e **nunca** entrou no padrão — o padrão adotou
   `OFFSET ... FETCH FIRST`, que quase ninguém escreve.

Ver [23-dialetos.md](23-dialetos.md) para o que isso significa na prática.

---

## 6. Os produtos, em ordem de nascimento

| Ano | Produto | Notas |
|---|---|---|
| 1979 | **Oracle** | Primeiro comercial; ainda o mais caro e o mais entrincheirado em ERP |
| 1983 | **IBM DB2** | Ainda dominante em mainframe bancário |
| 1989 | **SQL Server** | Nasceu como Sybase licenciado à Microsoft; separaram em 1994 |
| 1995 | **MySQL** | Rápido e simples; motor da web dos anos 2000 |
| 1996 | **PostgreSQL** | Vem do POSTGRES de Michael Stonebraker (Berkeley, 1986); ganhou SQL em 1994 e o nome em 1996 |
| 2000 | **SQLite** | D. Richard Hipp, para um navio da Marinha americana que não podia depender de servidor. Domínio público |
| 2009 | **MongoDB, Redis, Cassandra** | A onda NoSQL |
| 2010 | **TimescaleDB / InfluxDB** | Séries temporais |
| 2019 | **DuckDB** | CWI (Amsterdã); "o SQLite da análise" |

### Três histórias que valem contar

**SQLite (2000).** D. Richard Hipp trabalhava em software para o destróier
USS Oscar Austin. O sistema usava Informix, e quando o banco de dados caía, o
programa caía junto — num navio, no mar. Hipp escreveu um banco que fosse uma
biblioteca dentro do programa, sem servidor, sem administrador. Colocou em
**domínio público** (não é open-source com licença; é literalmente sem
copyright). Hoje é o software de banco de dados mais implantado do mundo, com
mais de um trilhão de bancos em uso, e os autores mantêm uma suíte de testes
com cobertura de 100% de ramificações (*branch coverage*) — algo raríssimo em
software de qualquer tipo.

**PostgreSQL.** Michael Stonebraker fez o Ingres (1974) em Berkeley, depois o
POSTGRES (1986) — "post-Ingres". O POSTGRES tinha sua própria linguagem, o
QUEL, que era **tecnicamente melhor** que o SQL segundo a maioria dos
especialistas da época. Perdeu mesmo assim, porque o SQL virou padrão. Em 1994
dois estudantes trocaram o QUEL por SQL e nasceu o Postgres95, depois
PostgreSQL. **É o exemplo canônico de que o padrão vence a qualidade técnica**
— e, por sinal, Stonebraker ganhou o Turing Award em 2014.

**A onda NoSQL (2009–2015).** A promessa era: bancos relacionais não escalam,
esquemas rígidos atrapalham, junções são lentas, o futuro é sem SQL. Dez anos
depois o placar é claro: os problemas de escala eram reais para um punhado de
empresas (Google, Facebook) e imaginários para 99% das outras; muita gente
descobriu da pior forma que "sem esquema" significa "esquema implícito
espalhado pelo código do aplicativo"; e quase todo produto NoSQL sobrevivente
ganhou uma linguagem de consulta parecida com SQL. O próprio nome foi
reinterpretado de "No SQL" para "**Not Only** SQL" — o que é uma retirada
estratégica com estilo.

---

## 7. Por que o SQL é esquisito: as explicações históricas

Esta é a parte prática do arquivo.

| Esquisitice | Explicação |
|---|---|
| `NULL` com lógica de três valores | Codd queria distinguir "não se aplica" de "desconhecido" e propôs **dois** marcadores diferentes. O comitê aprovou um só, com semântica ambígua. Codd achou isso um erro grave e escreveu contra até o fim da vida |
| Ordem de escrita ≠ ordem de execução | `SELECT` vem primeiro porque em inglês se diz "selecione X de Y". Legibilidade venceu coerência formal, em 1974 |
| Duplicatas permitidas | Remover duplicata exige ordenar. Em 1974 isso era caro demais para fazer sempre |
| `SELECT *` existe | Conveniência de terminal interativo dos anos 70. Todo mundo sabe que é ruim em produção e ninguém consegue tirar |
| `COUNT(*)` vs `COUNT(col)` | Consequência direta do `NULL`: uma conta linhas, a outra conta valores |
| `LIMIT` não é padrão | Cada fabricante inventou o seu antes do padrão existir. Quando o ISO padronizou `FETCH FIRST`, já era tarde |
| Junção implícita `FROM a, b` | Era a única forma até o SQL-92. Sobrevive por inércia e por código velho |
| Aspas simples ≠ duplas | Herdado do padrão: `'valor'` e `"identificador"`. O MySQL relaxou isso e ensinou o hábito errado a uma geração |
| `MERGE` só em 2003 | Cada banco tinha o seu (`REPLACE`, `UPSERT`, `ON DUPLICATE KEY`). O padrão chegou depois e não substituiu |
| SQLite aceita texto em coluna `INTEGER` | Decisão consciente de "tipagem dinâmica" de Hipp em 2000. Reconhecida como problemática; a saída foi criar `STRICT` em 2021, sem quebrar 20 anos de bancos |

---

## 8. E o modelo relacional vai morrer?

Cinquenta e seis anos depois do artigo de Codd, o SQL é a linguagem de
programação mais usada que não é considerada linguagem de programação.
Sobreviveu a quatro ondas que prometeram substituí-lo: bancos orientados a
objetos (anos 90), XML (2000s), NoSQL (2010s) e o "data lake sem esquema"
(2015–2020, que virou "lakehouse com esquema e SQL em cima" — ou seja, o
relacional de novo, com nome novo).

**A razão de sobreviver não é técnica, é econômica:** há milhões de pessoas
que sabem SQL, trilhões de linhas guardadas em bancos SQL, e décadas de
otimizador acumulado. O custo de trocar é astronômico e o ganho é marginal.
Isso é *lock-in* de ecossistema, e é tão real quanto lock-in de fornecedor.

**Opinião profissional, declarada como opinião:** o SQL vai continuar sendo a
interface por muito mais tempo, mas cada vez menos gente vai *escrever* SQL à
mão — vai ser gerado por ferramenta de BI, por camada semântica, e por modelos
de linguagem. Isso torna **ler e auditar** SQL mais importante que escrevê-lo,
não menos. Quem só sabe escrever será substituído; quem sabe julgar se a
consulta gerada está certa, não. Ver [65-estado-da-arte.md](65-estado-da-arte.md).

---

## Linha do tempo

```
1966  IMS (IBM) — modelo hierárquico, programa Apollo
1969  CODASYL — modelo de rede
1970  ██ Codd publica o modelo relacional
1974  SEQUEL (Chamberlin & Boyce) · System R começa
1976  Modelo entidade-relacionamento (Peter Chen)
1979  ██ Oracle V2 — primeiro comercial
1979  Artigo de Selinger — otimizador baseado em custo
1981  Codd ganha o Turing Award
1986  ██ SQL-86 (ANSI) · POSTGRES em Berkeley
1987  ISO adota
1992  ██ SQL-92 — o "SQL clássico"
1995  MySQL
1996  PostgreSQL (nome atual)
1999  SQL:1999 — CTE recursiva, gatilhos
2000  ██ SQLite
2003  SQL:2003 — ██ funções de janela
2009  Onda NoSQL
2011  SQL:2011 — tabelas temporais
2016  SQL:2016 — JSON
2019  DuckDB
2023  ██ SQL:2023 — SQL/PGQ (grafos), JSON nativo
2026  Correção técnica do SQL/PGQ (ago/2026) · Postgres 18 implementando PGQ
```

---

## Autoteste

1. Que problema concreto o modelo relacional resolveu, e por que ele não era
   um problema de desempenho?
2. Por que a linguagem se chamou SEQUEL, e o que isso explica sobre a sintaxe
   que você escreve hoje?
3. Por que o nome mudou para SQL?
4. Por que a IBM inventou o SQL e a Oracle ficou com o mercado?
5. Qual edição do padrão introduziu funções de janela, e por que isso demorou?
6. Por que o PostgreSQL abandonou o QUEL, que era tecnicamente melhor?
7. Que problema real fez o SQLite nascer?
8. Explique historicamente **três** esquisitices do SQL.
9. O que a onda NoSQL prometeu e o que de fato entregou?
10. Por que o modelo relacional sobreviveu — a razão é técnica ou econômica?

---

*Próximo: [12-consulta-select.md](12-consulta-select.md).*
