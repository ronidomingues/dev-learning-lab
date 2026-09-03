# 60 · Teoria avançada

`Nível: pesquisa` · `Atualizado em: 14/08/2026`

Este arquivo formaliza o que os anteriores trataram operacionalmente: o que significa uma
execução concorrente estar **correta**, por que a validação otimista garante correção, e onde
estão os limites teóricos.

Pré-requisitos: [`10-fundamentos.md`](10-fundamentos.md), [`15-isolamento-e-mvcc.md`](15-isolamento-e-mvcc.md),
e alguma familiaridade com grafos e relações de ordem.

---

## 1. Escalonamentos e serializabilidade

### 1.1 Definições

Uma **transação** `Tᵢ` é uma sequência finita de operações `rᵢ(x)` (ler o item `x`) e
`wᵢ(x)` (escrever `x`), terminada por `cᵢ` (commit) ou `aᵢ` (abort).

Um **escalonamento** (*schedule*) `S` sobre um conjunto de transações é uma ordenação total das
operações de todas elas que preserva a ordem interna de cada uma.

`S` é **serial** se, para todo par `Tᵢ`, `Tⱼ`, todas as operações de uma precedem todas as da
outra. Um escalonamento serial é correto por definição: é o que aconteceria se as transações
rodassem uma de cada vez.

Duas operações **conflitam** se: pertencem a transações diferentes, acessam o mesmo item, e
pelo menos uma é escrita. Os três pares conflitantes:

| Par | Nome | Por que importa |
|---|---|---|
| `rᵢ(x)` … `wⱼ(x)` | leitura-escrita (RW) | `Tᵢ` leu um valor que deixou de valer |
| `wᵢ(x)` … `rⱼ(x)` | escrita-leitura (WR) | `Tⱼ` depende de `Tᵢ` |
| `wᵢ(x)` … `wⱼ(x)` | escrita-escrita (WW) | a ordem final do valor depende da ordem |

### 1.2 Serializabilidade por conflito

`S` é **serializável por conflito** (*conflict-serializable*) se pode ser transformado num
escalonamento serial trocando apenas operações **não** conflitantes de posição.

**Teorema (Papadimitriou, 1979).** `S` é serializável por conflito se e somente se o seu
**grafo de precedência** for acíclico.

O grafo de precedência `G(S)` tem um nó por transação e uma aresta `Tᵢ → Tⱼ` quando existe uma
operação de `Tᵢ` que conflita e precede uma operação de `Tⱼ`.

```
r₁(x)  r₂(x)  w₁(x)  w₂(x)          — o lost update de 12-anatomia

   T1 ──RW──► T2      (r₁(x) antes de w₂(x))
   T2 ──RW──► T1      (r₂(x) antes de w₁(x))

grafo com ciclo  ⇒  NÃO é serializável
```

Este é o resultado que dá base formal ao curso inteiro: **o lost update é, precisamente, um
ciclo no grafo de precedência**. Não é uma questão de gosto ou de política; é uma execução
que não corresponde a nenhuma ordem sequencial.

### 1.3 Serializabilidade por visão

Uma noção mais fraca e mais permissiva: `S₁` e `S₂` são **equivalentes por visão** se cada
leitura lê o valor escrito pela mesma escrita nos dois, e a escrita final de cada item é a
mesma nos dois.

- Todo escalonamento serializável por conflito é serializável por visão.
- A recíproca é falsa: existem escalonamentos serializáveis por visão e não por conflito —
  aqueles com **escritas cegas** (escrever sem ter lido).
- **Decidir serializabilidade por visão é NP-completo** (Papadimitriou, 1979).

Consequência de engenharia: nenhum banco real usa serializabilidade por visão. Todos usam
serializabilidade por conflito, que é decidível em tempo polinomial. É um caso raro e claro de
um resultado de complexidade determinando o que os produtos fazem.

---

## 2. A validação otimista, formalmente

Seguindo Kung e Robinson (1981). Cada transação `T` mantém:

- `RS(T)` — o **conjunto de leitura**: itens lidos;
- `WS(T)` — o **conjunto de escrita**: itens escritos (em espaço privado);
- `tn(T)` — um número de transação, atribuído **no início da validação**.

### 2.1 Validação para trás (*backward validation*)

`T` valida com sucesso se, para **toda** transação `Tᵢ` com `tn(Tᵢ) < tn(T)` que confirmou
depois de `T` começar sua fase de leitura:

```
WS(Tᵢ) ∩ RS(T) = ∅
```

*"Nada do que eu li foi escrito por alguém que confirmou depois de eu começar."*

**Correção.** Se a condição vale para toda `Tᵢ` anterior, então `T` pode ser posicionada
depois de todas elas numa ordem serial: nenhuma leitura de `T` foi invalidada, e as escritas
de `T` só se tornam visíveis no fim. Não há aresta `T → Tᵢ` no grafo de precedência para
nenhuma `Tᵢ` anterior, logo não há ciclo envolvendo `T`. ∎ (esboço)

**Propriedade assimétrica, e é a que importa na prática:** a vítima é sempre a transação
**mais nova**. Uma transação longa acumula mais transações confirmadas no seu intervalo, logo
maior chance de interseção. Formalmente, se as confirmações chegam a uma taxa `λ` e `T` dura
`D`, a chance de conflito cresce com `λ·D`.

**Corolário operacional:** transações longas com escrita podem sofrer *starvation* — nunca
conseguir confirmar. Nenhum aumento no número de tentativas resolve, porque a causa é a
duração. As soluções reais são: (a) encurtar a transação, (b) separar leitura de escrita,
(c) dar prioridade crescente a quem já falhou muitas vezes, (d) cair para pessimista depois
de `k` falhas — a técnica de **escalonamento adaptativo** (seção 5).

### 2.2 Validação para a frente (*forward validation*)

`T` valida com sucesso se, para toda `Tⱼ` ainda **em execução**:

```
WS(T) ∩ RS(Tⱼ) = ∅
```

*"Nada do que eu vou escrever está sendo lido por alguém em andamento."*

Diferença crucial: aqui há **escolha de vítima**. `T` pode abortar a si mesma ou abortar as
`Tⱼ` conflitantes. Isso permite políticas — priorizar transações longas, priorizar as que já
falharam antes, priorizar as interativas — que a validação para trás não permite.

Custo: é preciso conhecer os conjuntos de leitura das transações **em curso**, o que exige
manter estrutura compartilhada e sincronizá-la. Por isso a validação para trás domina nas
implementações simples, e a para a frente aparece em sistemas em memória onde o custo é menor.

### 2.3 O `UPDATE ... WHERE version = ?` como validação

Onde o padrão prático se encaixa na teoria:

| Teoria | Prática |
|---|---|
| `RS(T)` | `{a linha lida}` — um único item |
| `WS(T)` | `{a mesma linha}` |
| validação | `AND version = ?` |
| `tn(T)` | implícito na ordem de execução dos `UPDATE` no banco |
| atomicidade validação+escrita | o lock interno de linha do comando |

**O que a comparação revela:** o padrão prático faz validação para trás com `RS` e `WS` de
**tamanho um**. Isso explica exatamente a limitação de [`10 §2.1`](10-fundamentos.md#21-write-skew-o-buraco-que-ninguém-vê):
o *write skew* é um conflito RW envolvendo itens **diferentes** — `RS(T)` contém `y` e
`WS(T)` contém `x`. Com `RS` reduzido a `{x}`, a interseção com a escrita alheia em `y` é
vazia por construção, e a anomalia passa.

**Para detectar write skew é preciso rastrear o conjunto de leitura inteiro.** É precisamente
o que o SSI faz — e é por isso que ele custa memória de *predicate locks*.

---

## 3. SSI: serializabilidade sobre instantâneos

O `SNAPSHOT ISOLATION` (SI) permite escalonamentos não serializáveis. Fekete, Liarokapis,
O'Neil, O'Neil e Shasha (2005) caracterizaram exatamente quando:

**Teorema.** Toda execução não serializável sob SI contém um ciclo no grafo de dependências
com **duas arestas RW consecutivas** (*dangerous structure*), formando o padrão:

```
T1 ──rw──► T2 ──rw──► T3
```

onde `T2` é *pivô*, e `T3` confirma antes de `T1` e `T2` (podendo `T1 = T3`).

Cahill, Röhm e Fekete (2008) transformaram isso em algoritmo: rastreie apenas as arestas RW
de entrada e de saída de cada transação (dois bits por transação, mais os *predicate locks*
para descobrir as arestas), e aborte quando o padrão aparecer.

**Propriedades:**

- **Correção:** nenhuma anomalia passa — todo ciclo contém a estrutura perigosa.
- **Falsos positivos:** aborta transações que teriam sido seguras. A estrutura perigosa é
  condição **necessária**, não suficiente. Este é o preço, e ele é fundamental — detectar
  ciclos reais exigiria manter o grafo inteiro.
- **Custo espacial:** rastrear leituras exige *predicate locks*. Sob pressão de memória, o
  PostgreSQL **degrada a granularidade** (linha → página → tabela), o que aumenta os falsos
  positivos exatamente quando o sistema está mais carregado — uma realimentação que vale
  conhecer antes de encontrar em produção.

---

## 4. Limites teóricos

Cinco resultados que delimitam o que é possível. Nenhum é evitável por engenharia melhor.

### 4.1 Não existe controle de concorrência ótimo online

Escolher, em tempo de execução, entre abortar `T₁` ou `T₂` de modo a maximizar a vazão exige
saber o que cada uma ainda vai fazer. É um problema **online** clássico: qualquer algoritmo
determinístico tem uma razão competitiva limitada em relação ao ótimo offline.

**Consequência:** toda política de aborto é heurística. "Qual é o melhor CC?" é uma pergunta
mal posta sem especificar a carga.

### 4.2 Serializabilidade por visão é NP-completo

Já visto em §1.3. Determina o que os produtos implementam.

### 4.3 O teorema CAP e a coordenação

Sob partição de rede, você escolhe entre consistência e disponibilidade. Optimistic locking
que exige uma autoridade única **escolhe consistência**: durante a partição, o lado sem
autoridade não pode escrever com segurança.

O resultado mais fino é o **CALM** (*Consistency As Logical Monotonicity*, Hellerstein &
Alvaro): um programa distribuído tem implementação **coordination-free** se e somente se for
expressável de forma **monotônica** — o que se computou não é invalidado por dados que chegam
depois.

Consequência direta e prática: **operações monotônicas** (adicionar a um conjunto, incrementar
um contador que só sobe) não precisam de coordenação, e é exatamente por isso que os CRDTs
funcionam. **Operações não monotônicas** (verificar se um conjunto está vazio, garantir saldo
≥ 0) exigem coordenação, e nenhum CRDT resolve. Não é limitação de implementação; é teorema.

### 4.4 O limite de vazão do OCC sob contenção

Com `n` transações concorrentes sobre `m` itens uniformemente distribuídos, a probabilidade
de uma transação de tamanho `k` não conflitar é aproximadamente

```
P(sucesso) ≈ (1 − k/m)^(n−1)
```

Para `k` fixo, `P` decai **exponencialmente** com `n`. A vazão útil é `n · P(sucesso) / T`,
função que cresce, atinge um máximo e depois **cai**: é o *thrashing*. O ponto de máximo fica
em torno de `n* ≈ m/k`.

Interpretação prática: **existe um número ótimo de transações concorrentes**, e ultrapassá-lo
reduz a vazão. É a justificativa teórica para limitar concorrência (*admission control*) em
vez de deixar entrar tudo — e explica por que aumentar o *pool* de conexões às vezes piora o
desempenho.

### 4.5 Impossibilidade de detectar o passado

Um token de versão informa **que** algo mudou, nunca **o quê** nem **por quê**. Reconstruir a
intenção de uma escrita a partir do estado final é impossível em geral — a função de estado
não é injetiva (muitos caminhos levam ao mesmo estado).

É a razão teórica pela qual sistemas que querem merge de qualidade guardam **operações**, e
não estados: CRDTs, *event sourcing* e o `git` armazenam o histórico de mudanças porque a
informação necessária ao merge não está no estado final.

---

## 5. Fronteiras de pesquisa em OCC

O que se estuda hoje, com os problemas em aberto.

### 5.1 OCC adaptativo

Escolher entre otimista e pessimista **por transação**, em tempo de execução, com base no
histórico. Linha de trabalho consolidada (`Adaptive optimistic concurrency control for
heterogeneous workloads`, VLDB 2019; `Mostly-optimistic concurrency control`, VLDB 2016).

Ideia central: comece otimista; depois de `k` abortos da mesma transação, escale para
pessimista, garantindo progresso. Resolve o *starvation* de §2.1.

**Em aberto:** qual `k`, e como aprender a política sem sofrer com a mudança de carga.

### 5.2 Validação em escala de muitos núcleos

Em máquinas com centenas de núcleos, a própria validação vira gargalo: o contador global de
transações é um ponto de serialização. Trabalhos como Silo e TicToc atacam isso com
*epoch-based* e timestamps calculados a partir dos dados, evitando o contador central.

### 5.3 OCC geo-replicado por épocas

Trabalhos recentes tratam OCC entre regiões agrupando transações em **épocas** e validando em
lote, amortizando a latência de ida e volta entre continentes por muitas transações.
Ver [*Epoch-based Optimistic Concurrency Control in Geo-replicated Databases*](https://arxiv.org/pdf/2602.21566).

### 5.4 Híbrido determinístico + OCC

O sistema roda Calvin (determinístico, ordena antes de executar) para as transações cujo
conjunto de leitura/escrita é conhecido de antemão, e OCC para as demais, no **mesmo** banco.
O trabalho HDCC (VLDB, vol. 18) relata ganhos de até 3,1× sobre abordagens híbridas
anteriores, com mecanismos de *lock-sharing*, validação global e intercalação de dois logs.

**Em aberto:** decidir automaticamente qual transação vai para qual caminho.

### 5.5 Controle de concorrência aprendido

A fronteira mais recente: tratar a escolha de política como função aprendível a partir da
carga observada. Promissor e imaturo — os riscos conhecidos são o comportamento sob carga
fora da distribuição de treino e a dificuldade de dar garantias de correção quando a política
é uma rede neural. **Opinião:** a correção precisa continuar vindo do mecanismo, com o modelo
escolhendo apenas entre políticas todas corretas. Um modelo que possa violar serializabilidade
não é utilizável em banco de dados.

---

## 6. Exercícios teóricos

1. Desenhe o grafo de precedência de `r₁(x) r₂(y) w₁(y) w₂(x)` e classifique-o. Que anomalia é?
2. Prove que todo escalonamento serializável por conflito é serializável por visão.
3. Construa um escalonamento serializável por visão e não por conflito (dica: escrita cega).
4. Mostre que a validação para trás com `|RS| = |WS| = 1` não detecta write skew.
5. Com `m = 1000` itens, `k = 3` itens por transação, calcule `n*` e `P(sucesso)` em `n*`.
6. Explique, com o CALM, por que um contador CRDT que só incrementa dispensa coordenação e um
   contador com piso zero não dispensa.
7. Por que a estrutura perigosa do SSI é condição necessária e não suficiente? Dê o custo
   dessa escolha.
8. Argumente por que reconstruir a intenção a partir do estado final é impossível, e o que
   isso implica para o projeto de sistemas com merge.

---

## Autoteste

1. Enuncie o teorema do grafo de precedência e aplique-o ao lost update.
2. Por que nenhum banco usa serializabilidade por visão?
3. Escreva a condição de validação para trás e a de validação para a frente.
4. Qual é a assimetria da validação para trás, e que problema prático ela cria?
5. O que é a estrutura perigosa do SSI?
6. Enuncie o resultado CALM e dê uma consequência prática.
7. Por que a vazão do OCC tem um máximo e depois cai?
8. Que informação está nas operações e não está no estado final?

---

## Fontes consultadas (14/08/2026)

- [Kung & Robinson — *On optimistic methods for concurrency control*, ACM TODS 6(2), 1981](https://dl.acm.org/doi/10.1145/319566.319567) · [cópia aberta](https://www.cs.cmu.edu/~dga/15-712/F07/lectures/12-optimism.pdf)
- Papadimitriou — *The serializability of concurrent database updates*, JACM 26(4), 1979
- Berenson et al. — *A Critique of ANSI SQL Isolation Levels*, SIGMOD 1995
- Fekete, Liarokapis, O'Neil, O'Neil, Shasha — *Making Snapshot Isolation Serializable*, ACM TODS 30(2), 2005
- Cahill, Röhm, Fekete — *Serializable Isolation for Snapshot Databases*, SIGMOD 2008
- [Larson et al. — *High-Performance Concurrency Control Mechanisms for Main-Memory Databases*, VLDB 2011](https://arxiv.org/pdf/1201.0228)
- [*Adaptive optimistic concurrency control for heterogeneous workloads*, PVLDB 12(5)](https://dl.acm.org/doi/10.14778/3303753.3303763)
- [*Mostly-optimistic concurrency control for highly contended dynamic workloads on a thousand cores*, PVLDB 10(2)](https://dl.acm.org/doi/10.14778/3015274.3015276)
- [*Improving Optimistic Concurrency Control Through Transaction Batching and Operation Reordering*, PVLDB 12(2)](http://www.vldb.org/pvldb/vol12/p169-ding.pdf)
- [*A Hybrid Approach to Integrating Deterministic and Non-Deterministic Concurrency Control (HDCC)*, PVLDB 18](https://www.vldb.org/pvldb/vol18/p1376-lu.pdf)
- [*Epoch-based Optimistic Concurrency Control in Geo-replicated Databases*, arXiv](https://arxiv.org/pdf/2602.21566)
- Hellerstein & Alvaro — *Keeping CALM: When Distributed Consistency is Easy*, CACM 2020
