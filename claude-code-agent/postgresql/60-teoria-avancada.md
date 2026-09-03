# 60 · Teoria avançada — álgebra relacional, complexidade e os limites

`Nível: pesquisa` · `Última atualização: 11/08/2026`

O que fundamenta o banco, o que ele **não pode** fazer, e o que custa quanto. Bancos de dados são
um dos poucos campos da computação com uma base matemática rigorosa — e vale conhecê-la.

---

## 1. Álgebra relacional — a matemática do SQL

Por baixo do SQL há uma álgebra formal, definida por Codd, com um punhado de operadores sobre
relações (tabelas). Cada consulta SQL se traduz numa expressão dessa álgebra — e é isso que permite
ao otimizador **reescrever** consultas para formas equivalentes mais baratas.

| Operador | Símbolo | SQL | O que faz |
|---|---|---|---|
| **Seleção** | σ (sigma) | `WHERE` | Filtra linhas por um predicado |
| **Projeção** | π (pi) | `SELECT col1, col2` | Escolhe colunas |
| **União** | ∪ | `UNION` | Junta duas relações compatíveis |
| **Diferença** | − | `EXCEPT` | Linhas de A que não estão em B |
| **Produto cartesiano** | × | `CROSS JOIN` | Todas as combinações |
| **Junção** | ⋈ | `JOIN` | Produto + seleção (combina por condição) |
| **Interseção** | ∩ | `INTERSECT` | Linhas em ambas |
| **Renomeação** | ρ (rho) | `AS` | Renomeia |

**Propriedade fundamental — o fechamento:** cada operador recebe relações e devolve uma relação.
Isso permite **compor** operações indefinidamente (o resultado de um JOIN pode entrar noutro), e é
por isso que subconsultas e CTEs funcionam.

**Por que isso importa na prática:** a álgebra tem **leis de equivalência**. Por exemplo,
"selecionar depois de juntar" equivale a "selecionar antes de juntar" (*predicate pushdown*):

```
   σ(condição em A)  (A ⋈ B)   ≡   (σ(condição em A) A) ⋈ B
```

Empurrar o filtro para antes do JOIN reduz o número de linhas juntadas — às vezes de milhões para
milhares. O otimizador aplica essas leis automaticamente. Quando você entende que o SQL é álgebra,
entende **por que** o planejador pode reordenar sua consulta sem mudar o resultado. Ver
[16-consultas-e-planejador.md](16-consultas-e-planejador.md).

---

## 2. Cálculo relacional e a completude de Codd

Codd definiu duas linguagens equivalentes:
- **Álgebra relacional** — *procedural*: você descreve as operações.
- **Cálculo relacional** — *declarativo*: você descreve o resultado com lógica de predicados
  (∀, ∃).

E provou o **Teorema de Codd**: as duas têm o **mesmo poder expressivo**. Isso não é curiosidade —
é a base teórica que garante que uma linguagem declarativa (o cálculo, do qual o SQL descende) pode
ser **traduzida** para operações executáveis (a álgebra) **sem perder poder**. É a prova de que
"dizer o quê" e "dizer o como" são intercambiáveis no modelo relacional. Sem esse teorema, não
haveria garantia de que todo SQL declarativo tem um plano de execução.

Uma linguagem com esse poder é dita **relacionalmente completa**. O SQL é mais que isso (tem
agregação, recursão, janelas), mas a completude relacional é o piso.

---

## 3. Os limites: o que a álgebra relacional NÃO pode expressar

A álgebra relacional pura tem um limite conhecido e importante: **ela não pode computar o fecho
transitivo**.

O fecho transitivo é "todos os alcançáveis a partir de um ponto seguindo relações" — o
organograma completo sob alguém, todos os componentes de um produto, todos os amigos-de-amigos. Com
os operadores básicos, você não consegue, porque não sabe **quantos** JOINs serão necessários (a
profundidade da hierarquia é desconhecida em tempo de escrita).

**A prova (esboço):** qualquer expressão da álgebra relacional tem um número **fixo** de
operadores. Mas o fecho transitivo de um grafo pode exigir um número de "passos" que depende do
**dado** (o comprimento do caminho mais longo), não da consulta. Logo, nenhuma expressão fixa o
computa para todos os grafos.

**Como o SQL resolveu isso:** acrescentando **recursão** (`WITH RECURSIVE`, ver
[06-exemplos.md, exemplo 7](06-exemplos.md#7-hierarquia-com-cte-recursiva)), que vai **além** da
álgebra relacional pura. É por isso que hierarquias exigem CTE recursiva e não um JOIN comum — não
é falta de recurso do PostgreSQL, é um **limite matemático** do modelo relacional básico, contornado
por uma extensão deliberada da linguagem.

---

## 4. Teoria da normalização e dependências funcionais

A normalização ([12](12-modelo-relacional-e-sql.md)) tem base formal em **dependências funcionais**.
Uma dependência funcional `X → Y` significa "o valor de X determina unicamente o valor de Y" (o CPF
determina o nome; o pedido não determina o e-mail do cliente).

As formas normais são definidas em termos delas:
- **2FN:** nenhum atributo não-chave depende de **parte** de uma chave composta.
- **3FN:** nenhum atributo não-chave depende de **outro atributo não-chave** (dependência
  transitiva).
- **BCNF:** para toda dependência `X → Y`, X é uma superchave.

**O resultado teórico importante:** existe um algoritmo (a partir do conjunto de dependências
funcionais) que **decompõe** um esquema em 3FN de forma que (a) preserva as dependências e (b) não
perde informação (a decomposição é reversível por JOIN — *lossless join*). A normalização não é
arte subjetiva; é um procedimento com garantias formais. O que é arte é decidir **quando parar** e
desnormalizar por desempenho — essa é uma escolha de engenharia, não de matemática.

---

## 5. Complexidade das operações

| Operação | Custo | Observação |
|---|---|---|
| Busca em B-tree | O(log n) | Por isso índices escalam a bilhões de linhas |
| Seq scan | O(n) | Ler a tabela toda |
| Hash join | O(n + m) | Linear, se a tabela hash cabe na memória |
| Sort-merge join | O(n log n + m log m) | Dominado pela ordenação |
| Nested loop join | O(n × m) | Quadrático — o que "explode" sem índice |
| Ordenação | O(n log n) | Limite inferior para ordenação por comparação |
| Agregação com hash | O(n) | Uma passada |

**O join é o coração do custo.** Um nested loop sobre duas tabelas de um milhão de linhas é 10¹²
operações — inviável. Com um índice no lado interno, cada busca vira O(log m), e o total cai para
O(n log m). É por isso que **indexar colunas de JOIN** é a otimização de maior impacto: transforma
um custo quadrático em quase-linear.

**A explosão intermediária:** o resultado de um JOIN pode ser muito maior que as tabelas de entrada
(no pior caso, o produto). Uma consulta com cinco JOINs mal ordenados pode gerar bilhões de linhas
intermediárias que são depois filtradas. Por isso a **ordem dos JOINs** — decidida pelo otimizador
com base em estimativas de cardinalidade — importa tanto, e por que estimativas erradas
(estatísticas velhas) produzem planos catastróficos.

---

## 6. CAP, ACID e os limites da distribuição

O **teorema CAP** (Brewer, provado formalmente por Gilbert e Lynch, 2002) diz: um sistema
distribuído não pode garantir simultaneamente as três:

- **C**onsistência (toda leitura vê a última escrita)
- **A**vailability (disponibilidade — toda requisição recebe resposta)
- **P**artition tolerance (tolerância a partições de rede)

Como partições de rede **acontecem** (cabos caem), na prática você escolhe, **durante** uma
partição, entre C e A.

**Onde o PostgreSQL se encaixa:** um PostgreSQL single-node é **CA** no sentido de que não é
distribuído — não há partição interna a tolerar. Com replicação:
- **Assíncrona** tende a **AP**: as réplicas continuam respondendo, mas podem servir dados
  levemente atrasados (abre mão de C).
- **Síncrona** tende a **CP**: garante consistência, mas se a réplica síncrona fica inacessível, as
  escritas podem **parar** (abre mão de A) até resolver.

Isso conecta com a escolha de [19-replicacao-e-alta-disponibilidade.md](19-replicacao-e-alta-disponibilidade.md):
síncrona vs. assíncrona **é** a escolha CAP durante uma partição, com nomes diferentes.

> **A nuance que a versão popular do CAP esconde:** "consistência" no CAP (linearizabilidade) é
> mais forte que o "C" de ACID (integridade das constraints). E "disponibilidade" tem graus. Os
> sistemas reais (incluindo o PostgreSQL distribuído e concorrentes como CockroachDB, Yugabyte)
> vivem num espectro de trade-offs de latência × consistência, não numa escolha binária. O teorema
> PACELC (Abadi) refina isso: *se* há partição (P), escolha entre A e C; *senão* (E), escolha entre
> latência (L) e consistência (C). Mesmo sem falhas, há um trade-off latência × consistência — o que
> descreve melhor a realidade de um banco replicado.

---

## 7. Serializabilidade e o SSI do PostgreSQL

O nível de isolamento `SERIALIZABLE` promete que transações concorrentes produzem um resultado
**equivalente a alguma execução serial** delas (uma após a outra). Garantir isso classicamente
exigia **bloqueio de dois níveis** (2PL — *two-phase locking*), que trava muito e serializa demais.

O PostgreSQL implementa **SSI** (*Serializable Snapshot Isolation*), baseado em pesquisa de Cahill,
Röhm e Fekete (2008). A ideia: rodar com snapshots do MVCC (rápido, sem travar leituras) e
**detectar** as dependências perigosas entre transações que poderiam quebrar a serializabilidade —
abortando uma delas apenas quando um ciclo real de conflito se forma.

O resultado teórico: **serializabilidade completa com o desempenho do MVCC**, ao custo de abortar
algumas transações (que a aplicação deve retentar). É uma das implementações mais elegantes de
isolamento em produção, e um exemplo de teoria de banco (grafos de dependência de serialização)
diretamente aplicada. Ver [15-transacoes-e-mvcc.md](15-transacoes-e-mvcc.md).

---

## 8. Problemas em aberto e fronteiras teóricas

| Problema | Estado |
|---|---|
| **Estimativa de cardinalidade** | Continua sendo o calcanhar de Aquiles dos otimizadores. Estimar quantas linhas um JOIN de múltiplas condições correlacionadas produz é notoriamente difícil, e erros geram planos ruins. Pesquisa ativa com *machine learning* para estimativas |
| **Otimização de junções** | Encontrar a ordem ótima de N JOINs é NP-difícil; otimizadores usam programação dinâmica até ~12 tabelas e heurísticas (GEQO no PostgreSQL) além disso |
| **Consistência × latência em escala global** | O trade-off do PACELC não tem "solução"; só pontos diferentes no espectro (Spanner usa relógios atômicos para chegar perto de CA; a maioria não pode) |
| **HTAP** (transacional + analítico no mesmo banco) | Unificar cargas OLTP e OLAP sem uma prejudicar a outra é uma fronteira ativa (armazenamento colunar, índices híbridos) |
| **Busca vetorial exata em escala** | Índices como HNSW são **aproximados**; busca exata dos k-vizinhos em altíssima dimensão esbarra na "maldição da dimensionalidade" |
| **Aprendizado no otimizador** | Otimizadores que aprendem com execuções passadas ainda são pesquisa, não produção estável |

---

## 9. Leituras primárias

| Trabalho | Por que |
|---|---|
| Codd (1970), *A Relational Model of Data for Large Shared Data Banks*, CACM | O artigo fundador. Curto e legível |
| Codd (1972), *Relational Completeness of Data Base Sublanguages* | O teorema da equivalência álgebra ≡ cálculo |
| Chamberlin & Boyce (1974), *SEQUEL* | A origem do SQL |
| Selinger et al. (1979), *Access Path Selection in a Relational Database Management System* | O artigo que criou a otimização baseada em custo — a base do planejador |
| Gilbert & Lynch (2002), *Brewer's Conjecture and the Feasibility of Consistent, Available, Partition-Tolerant Web Services* | A prova formal do CAP |
| Cahill, Röhm, Fekete (2008), *Serializable Isolation for Snapshot Databases* | A base do SSI do PostgreSQL |
| Abadi (2012), *Consistency Tradeoffs in Modern Distributed Database System Design* | PACELC, o refinamento do CAP |
| Stonebraker et al. (1986), *The Design of POSTGRES* | O projeto original; a tese da extensibilidade |

Referências completas em [95-referencias.md](95-referencias.md).

---

## Autoteste

1. Cite quatro operadores da álgebra relacional e seu equivalente em SQL.
2. O que é o "fechamento" da álgebra relacional, e por que ele permite compor consultas?
3. O que o Teorema de Codd (álgebra ≡ cálculo) garante sobre o SQL declarativo?
4. Por que a álgebra relacional pura não computa o fecho transitivo, e como o SQL contorna isso?
5. O que é uma dependência funcional, e como as formas normais se definem a partir dela?
6. Por que o nested loop join "explode", e por que indexar colunas de JOIN é tão impactante?
7. Enuncie o teorema CAP e explique como replicação síncrona vs. assíncrona é uma escolha CAP.
8. O que o PACELC acrescenta ao CAP, e por que descreve melhor um banco replicado real?
9. O que é o SSI do PostgreSQL, e qual problema clássico (do 2PL) ele resolve?
10. Cite dois problemas em aberto na teoria de bancos de dados e por que são difíceis.
