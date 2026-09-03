# 60 — Teoria avançada

Nível: pesquisa · Data: 13/08/2026

Nada aqui é necessário para usar SQL. Tudo aqui explica **por que** o SQL
funciona, onde estão os limites, e o que ninguém pode consertar.

---

## 1. Álgebra relacional

Uma **relação** R sobre atributos A₁…Aₙ com domínios D₁…Dₙ é um subconjunto do
produto cartesiano:

> R ⊆ D₁ × D₂ × … × Dₙ

Uma tupla é um elemento de R. Um conjunto — logo, sem duplicatas e sem ordem.

### Os operadores primitivos

| Operador | Notação | Definição |
|---|---|---|
| Seleção | σ_θ(R) | { t ∈ R : θ(t) } |
| Projeção | π_{A}(R) | { t[A] : t ∈ R } |
| Produto | R × S | { (r,s) : r ∈ R, s ∈ S } |
| União | R ∪ S | conjuntos compatíveis |
| Diferença | R − S | { t ∈ R : t ∉ S } |
| Renomeação | ρ_{a→b}(R) | |

Os demais são derivados:

- Junção: **R ⋈_θ S = σ_θ(R × S)**
- Interseção: **R ∩ S = R − (R − S)**
- Divisão (quantificação universal): **R ÷ S**

### Teorema de completude de Codd (1972)

> A álgebra relacional e o cálculo relacional (de tuplas, seguro) têm o **mesmo
> poder expressivo**.

Uma linguagem que expressa tudo que a álgebra expressa é chamada
***relationally complete***. É o critério mínimo que Codd estabeleceu para
julgar linguagens de consulta — e o SQL o satisfaz, com folga.

**Codd, E. F.** *Relational Completeness of Data Base Sublanguages*. IBM
Research Report RJ987, 1972.

### Onde o SQL diverge da álgebra

| Álgebra | SQL |
|---|---|
| Relação é **conjunto** | Tabela é **multiconjunto** (aceita duplicata) |
| Lógica de dois valores | **Três valores** (`NULL`) |
| Sem ordem | `ORDER BY` existe (mas só na saída final) |
| Sem agregação | `GROUP BY`, `SUM`, funções de janela |
| Sem recursão | `WITH RECURSIVE` |

Cada divergência foi uma escolha de engenharia, e cada uma tem um preço.
Duplicatas: economia de ordenação. `NULL`: representar ausência sem sentinela.
As duas foram criticadas por Codd, e Chris Date construiu uma carreira inteira
argumentando que o `NULL` do SQL é um erro que deveria ser substituído por
relações especiais. **Ele tem razão teoricamente, e perdeu na prática.**

---

## 2. Complexidade

### Consultas conjuntivas

Uma **consulta conjuntiva** (CQ) é um `SELECT-FROM-WHERE` com apenas
igualdades e `AND` — sem negação, sem união, sem agregação. Em Datalog, uma
regra sem negação.

| Problema | Complexidade |
|---|---|
| **Avaliação** de CQ (combinada: consulta + dados) | **NP-completa** |
| Avaliação de CQ (complexidade **de dados**: consulta fixa) | **AC⁰ ⊆ LOGSPACE** — polinomial |
| **Contenção** de CQ (Q₁ ⊆ Q₂ para todo banco?) | **NP-completa** (Chandra & Merlin, 1977) |
| Equivalência de CQ | NP-completa |
| Contenção com negação | **Indecidível** |

**O que isso significa na prática:** a complexidade *combinada* é
NP-completa — mas o que importa é a **complexidade de dados**, com a consulta
fixa e os dados crescendo, e essa é polinomial. É por isso que bancos
funcionam: sua consulta tem 10 linhas e a tabela tem 10⁹.

Chandra, A. K.; Merlin, P. M. *Optimal implementation of conjunctive queries in
relational data bases*. STOC 1977.

### Cotas e algoritmos ótimos de junção

Um dos resultados mais bonitos e mais recentes da área.

**Cota AGM** (Atserias, Grohe, Marx, 2008): dado o hipergrafo de uma consulta
de junção e os tamanhos das relações, existe uma cota superior justa para o
tamanho da saída, dada pela **cobertura fracionária de arestas**.

O exemplo canônico é a **junção triangular**:

```sql
SELECT * FROM R(a,b) JOIN S(b,c) USING (b) JOIN T(a,c) USING (a,c);
```

Com |R| = |S| = |T| = N, a saída tem no máximo **N^{3/2}**. Mas **todo plano
binário** (junte dois, depois o terceiro) produz um intermediário de tamanho
N² — assintoticamente pior que a saída final.

**Consequência:** existem consultas para as quais **nenhuma ordem de junção
binária é ótima**. É preciso um algoritmo diferente.

**Algoritmos *worst-case optimal join*** — Leapfrog Triejoin (Veldhuizen, 2014),
NPRR (Ngo, Porat, Ré, Rudolph, 2012) — atingem a cota AGM processando
**todos os atributos ao mesmo tempo**, não par a par.

**Estado de adoção em 2026:** implementados em bancos de grafo, em sistemas
de pesquisa (LogicBlox, RelationalAI) e no **DuckDB** para certos padrões. Os
bancos relacionais tradicionais (PostgreSQL, Oracle) **ainda usam apenas
junções binárias** — um resultado de 2012–2014 que a indústria levou uma
década para começar a absorver, e ainda parcialmente.

Este é o exemplo mais claro de teoria com consequência prática direta em SQL,
e é recente.

---

## 3. Dependências e formas normais

### Dependência funcional

X → Y significa: se duas tuplas concordam em X, concordam em Y.

**Axiomas de Armstrong** (1974) — sãos e completos:

1. **Reflexividade**: se Y ⊆ X então X → Y
2. **Aumento**: se X → Y então XZ → YZ
3. **Transitividade**: se X → Y e Y → Z então X → Z

Derivados: união, decomposição, pseudotransitividade.

**Fecho** X⁺ = todos os atributos determinados por X. Computável em tempo
linear, e é o algoritmo que decide se X é superchave.

### As formas normais

| FN | Condição | Elimina |
|---|---|---|
| 1FN | Valores atômicos | Listas dentro da célula |
| 2FN | 1FN + nenhum atributo não-primo depende de **parte** da chave | Redundância parcial |
| 3FN | 2FN + nenhuma dependência transitiva | Redundância transitiva |
| **BCNF** | Todo determinante é superchave | Anomalias restantes |
| 4FN | BCNF + sem dependência multivalorada não trivial | Produto cartesiano acidental |
| 5FN / PJNF | Toda dependência de junção é implicada por chaves | |
| 6FN | Sem dependência de junção não trivial | (Base do modelo temporal de Date) |

**O teorema desconfortável:** decomposição em 3FN sempre existe **preservando
dependências e sem perda de junção**. Decomposição em **BCNF** sempre existe
sem perda de junção, mas **nem sempre preservando dependências**.

Ou seja: há casos em que você escolhe entre BCNF e poder verificar todas as
restrições localmente. **Na prática, escolhe-se 3FN e verifica-se o resto na
aplicação** — e essa é a razão de a literatura industrial parar na 3FN.

---

## 4. Poder expressivo e o que o SQL não pode fazer

### O SQL padrão (sem recursão) não expressa fecho transitivo

Este é o resultado clássico. A consulta "existe um caminho de A até B em um
grafo de comprimento arbitrário" **não é expressável** em álgebra relacional
nem em SQL-92.

**Por quê:** a álgebra relacional é equivalente à **lógica de primeira ordem**
sobre estruturas finitas. E o fecho transitivo não é definível em primeira
ordem — provável pelo **teorema de Ehrenfeucht–Fraïssé** ou pela **lei
0-1 da lógica de primeira ordem**.

Foi exatamente essa limitação que motivou:
- `CONNECT BY` do Oracle (proprietário, anos 80);
- `WITH RECURSIVE` do **SQL:1999** — que adiciona um operador de ponto fixo e
  eleva o SQL ao poder do **Datalog com ponto fixo inflacionário**.

### Com recursão, o SQL é Turing-completo

`WITH RECURSIVE` mais aritmética torna o SQL Turing-completo. Já foram
implementados em SQL puro: máquinas de Turing, o jogo da vida, o conjunto de
Mandelbrot, resolvedores de sudoku.

**Consequência prática desconfortável:** decidir se uma consulta SQL recursiva
**termina** é indecidível (redução ao problema da parada). É por isso que
nenhum banco consegue avisar antes de rodar que a sua CTE recursiva vai rodar
para sempre — e por que a cláusula de parada é responsabilidade sua.

**Parada legítima da cadeia de porquês:** um teorema. Não há engenharia que
resolva.

### Hierarquia

```
lógica de 1ª ordem = álgebra relacional = SQL-92 (sem agregação)
      ⊂  + contagem/agregação
      ⊂  Datalog (ponto fixo)  =  SQL:1999 com WITH RECURSIVE
      ⊂  Turing-completo (com aritmética)
```

---

## 5. Otimização de consultas

### O problema

Dado um `SELECT`, encontrar o plano de execução de custo mínimo. É
**NP-difícil**: o número de ordens de junção de n relações é o número de
Catalan, e cresce como Ω(4ⁿ/n^{3/2}).

Para n = 12 relações, são mais de 4 milhões de árvores de junção só na forma
linear — mais ainda contando as em bushy tree.

### System R (Selinger et al., 1979)

O artigo que definiu como todo otimizador funciona até hoje:

1. **Programação dinâmica** sobre subconjuntos de relações.
2. **Modelo de custo** baseado em estatísticas (cardinalidade, seletividade).
3. **Ordens interessantes** (*interesting orders*): guarda-se o melhor plano
   por ordem de saída, porque uma ordem pode evitar uma ordenação depois.
4. **Heurísticas de poda**: só árvores lineares à esquerda (*left-deep*),
   reduzindo de Catalan para n!.

Selinger, P. G. et al. *Access Path Selection in a Relational Database
Management System*. SIGMOD 1979.

### Por que o otimizador erra

| Causa | Efeito |
|---|---|
| Suposição de **independência** entre predicados | Subestima cardinalidade quando as colunas são correlacionadas |
| Suposição de **uniformidade** na distribuição | Erra com dados enviesados |
| Estatísticas desatualizadas | Escolhe o plano de ontem |
| **Propagação de erro de cardinalidade** | Erro de 10× em três junções vira 1000× |

**O resultado experimental que define a área:** Leis et al., *How Good Are
Query Optimizers, Really?* (VLDB 2015), mediu que **estimativa de cardinalidade
é a fonte dominante de erro** — muito mais que o modelo de custo ou a busca de
planos. Otimizadores erram por ordens de grandeza rotineiramente, e ainda
assim produzem planos aceitáveis porque a função de custo é achatada perto do
ótimo.

**Fronteira atual:** otimização **adaptativa** (corrigir o plano durante a
execução, ao ver as cardinalidades reais) e **aprendida** (modelos de
aprendizado de máquina para estimar cardinalidade — Neo, Bao, Balsa). O
consenso de 2026 é que aprendizado ajuda em cargas repetitivas e é arriscado
em consultas novas; a adoção em produção é limitada. Ver
[65-estado-da-arte.md](65-estado-da-arte.md).

---

## 6. Transações e serializabilidade

### Serializabilidade

Uma execução concorrente é **serializável** se produz o mesmo resultado de
*alguma* execução sequencial.

- **Serializabilidade de conflito** (CSR): o grafo de precedência é acíclico.
  Decidível em tempo polinomial.
- **Serializabilidade de visão** (VSR): mais permissiva. Decidir se um
  escalonamento é VSR é **NP-completo**.

Por isso todo banco implementa CSR: VSR é mais expressiva e inviável de
verificar.

### Anomalias e níveis

O artigo **Berenson et al., *A Critique of ANSI SQL Isolation Levels*
(SIGMOD 1995)** mostrou que as definições do padrão ANSI são **ambíguas e
incompletas** — em particular, que `REPEATABLE READ` como definido não impede
a anomalia de *write skew*, e que "snapshot isolation" (que a maioria dos
bancos implementa) **não corresponde a nenhum dos níveis do padrão**.

**Write skew**, o exemplo canônico e assustador: duas transações leem que há
dois operadores de plantão, cada uma decide que pode liberar *um*, e as duas
confirmam. Resultado: zero operadores. Nenhuma transação viu dado sujo; a
restrição foi violada mesmo assim.

**Serializable Snapshot Isolation (SSI)** — Cahill, Röhm, Fekete (SIGMOD 2008)
— resolve isso detectando padrões de dependência perigosos e abortando uma das
transações. É o que o **PostgreSQL implementa desde a 9.1** no nível
`SERIALIZABLE`, e é uma das melhores implementações de teoria de bancos em
produto aberto.

### Distribuição

- **Teorema CAP** (Brewer 2000; Gilbert & Lynch 2002): na presença de partição
  de rede, escolha entre consistência e disponibilidade. **Frequentemente mal
  citado** — não diz que se escolhem "duas de três"; diz que, *durante uma
  partição*, C e A são incompatíveis.
- **PACELC** (Abadi, 2012): refinamento útil — na partição (P), escolha entre
  A e C; **senão** (E), entre latência (L) e consistência (C). Descreve melhor
  os sistemas reais.
- **FLP** (Fischer, Lynch, Paterson, 1985): consenso é impossível em sistema
  assíncrono com **uma** falha. Por isso todo protocolo real (Paxos, Raft) usa
  suposições parciais de sincronia e detecção de falha por tempo.

---

## 7. Fronteiras abertas

| Problema | Estado em 2026 |
|---|---|
| Estimativa de cardinalidade | Não resolvido. Abordagens aprendidas são promissoras e instáveis |
| Otimização adaptativa | Parcial; poucos bancos em produção |
| *Worst-case optimal joins* em bancos tradicionais | Adoção lenta; presente em DuckDB e sistemas de grafo |
| Consulta sobre dado criptografado | Criptografia homomórfica ainda impraticável; enclaves são o compromisso atual |
| Processamento de fluxo com semântica de SQL | Flink SQL, Materialize; semântica de janela e de tempo de evento ainda diverge entre sistemas |
| Consulta em grafo integrada | SQL/PGQ padronizado em 2023, corrigido em ago/2026; PostgreSQL 19 implementando |
| Aprendizado de índice | Índices aprendidos (Kraska et al., 2018) ainda não substituíram B-trees em produção |
| Texto natural → SQL | Alta acurácia em bancadas simples, baixa em esquemas reais. Ver [65](65-estado-da-arte.md) |

---

## Autoteste

1. Enuncie os seis operadores primitivos da álgebra relacional.
2. O que significa uma linguagem ser *relationally complete*?
3. Cite quatro divergências entre a álgebra relacional e o SQL, com a razão de
   cada uma.
4. Complexidade combinada × complexidade de dados: por que a segunda é a que
   importa?
5. Explique a cota AGM com o exemplo da junção triangular. Por que ela mostra
   que planos binários podem ser subótimos?
6. Enuncie os três axiomas de Armstrong.
7. Qual o dilema entre 3FN e BCNF?
8. Por que fecho transitivo não é expressável em SQL-92? Qual resultado prova?
9. Por que decidir a terminação de uma CTE recursiva é indecidível?
10. Segundo Leis et al. (2015), qual é a fonte dominante de erro nos
    otimizadores?
11. O que é *write skew* e por que `REPEATABLE READ` não o impede?
12. Enuncie o teorema CAP corretamente, e diga qual é o erro comum de citação.

---

*Referências completas em [95-referencias.md](95-referencias.md).
Próximo: [65-estado-da-arte.md](65-estado-da-arte.md).*
