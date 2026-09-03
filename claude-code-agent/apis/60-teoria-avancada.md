# 60 · Teoria avançada

`Nível: pesquisa` · `Atualizado: 11/08/2026`

Os limites teóricos por trás das decisões práticas. Não é sobre como usar APIs — é sobre por
que certos problemas **não têm solução boa**, e por que as soluções que usamos são as
melhores possíveis, não escolhas arbitrárias.

Pré-requisitos: [10-fundamentos.md](10-fundamentos.md), [17](17-contratos-e-documentacao.md),
noções de sistemas distribuídos.

---

## 1. As oito falácias da computação distribuída

Formuladas na Sun Microsystems (Peter Deutsch e outros, ~1994–1997). São as suposições que
todo desenvolvedor faz e que são **todas falsas**.

| # | Falácia | Consequência de acreditar nela |
|---|---|---|
| 1 | A rede é confiável | sem retry, sem timeout, sem idempotência |
| 2 | A latência é zero | chamadas encadeadas; N+1 pela rede |
| 3 | A banda é infinita | payloads gigantes; sem paginação |
| 4 | A rede é segura | sem TLS, sem autenticação entre serviços |
| 5 | A topologia não muda | IPs fixos no código; sem service discovery |
| 6 | Há um administrador | ninguém sabe a configuração do todo |
| 7 | O custo de transporte é zero | serialização e egress ignorados no orçamento |
| 8 | A rede é homogênea | suposições sobre MTU, ordem e protocolo |

**Por que isto é teoria e não conselho:** cada falácia corresponde a uma **impossibilidade**,
não a um defeito de implementação. Redes particionam (teorema CAP); latência tem piso na
velocidade da luz; e a distinção entre "não chegou" e "chegou e a resposta se perdeu" é
**indecidível** para o emissor.

**A ligação com o artigo de Waldo et al. (1994)** — ver [11-historia.md](11-historia.md) §2:
chamada local e remota diferem em **latência**, **memória**, **falha parcial** e
**concorrência**. Nenhuma abstração elimina essas diferenças; ela só as esconde até o dia
em que aparecem.

---

## 2. Falha parcial: o problema que define sistemas distribuídos

**Definição.** Numa chamada local, ou tudo funciona ou o processo inteiro morre. Numa
chamada remota, **uma parte pode falhar enquanto o resto continua**.

### 2.1 A ambiguidade fundamental

Cliente envia requisição. Não recebe resposta. **Quais são os estados possíveis do servidor?**

```text
1. A requisição não chegou.                     → não aconteceu
2. Chegou, foi rejeitada antes de processar.    → não aconteceu
3. Chegou, processou, e caiu antes de responder.→ ACONTECEU
4. Chegou, processou, respondeu, e a resposta   → ACONTECEU
   se perdeu no caminho.
```

**Teorema (informal).** O emissor **não pode distinguir** esses quatro casos apenas pela
ausência de resposta.

**Prova esboçada.** A informação que distinguiria os casos está no receptor. Para obtê-la, o
emissor precisaria de outra mensagem — que está sujeita exatamente ao mesmo problema.
Regressão infinita. ∎

Esta é a **mesma estrutura** do problema dos dois generais (§3): confirmação exige
confirmação da confirmação, indefinidamente.

### 2.2 O que se faz na prática

Como não dá para **saber**, torna-se **irrelevante saber**:

| Estratégia | Como |
|---|---|
| **Idempotência** | repetir é inofensivo → retente sem precisar distinguir |
| **Consulta de estado** | "o pedido X existe?" — troca a ambiguidade por uma leitura |
| **Transação com id do cliente** | o cliente gera o id → a duplicata é detectável no banco |
| **Compensação** | assuma o pior e desfaça (padrão Saga) |

**As três primeiras convergem para a mesma coisa:** deslocar a decisão do **transporte**
(que não pode decidir) para o **estado** (que pode).

---

## 3. O problema dos dois generais

**Enunciado.** Dois generais precisam atacar simultaneamente. Só se comunicam por
mensageiros que podem ser capturados. Podem chegar a um acordo?

**Teorema.** **Não.** Não existe protocolo, com número finito de mensagens, que garanta o
acordo sobre um canal não confiável.

**Prova por contradição.** Suponha um protocolo com o menor número de mensagens que resolve.
A **última** mensagem pode se perder. Se o protocolo funciona sem ela, ela era desnecessária
— contradizendo a minimalidade. Se não funciona sem ela, o emissor da última mensagem nunca
sabe se ela chegou, então ele não pode agir com certeza. ∎

**A consequência que afeta você todos os dias:** **não existe entrega exactly-once no
transporte.** As garantias possíveis são:

| Garantia | Significa | Como se obtém |
|---|---|---|
| **At-most-once** | nunca duplica; pode perder | envie e não retente |
| **At-least-once** | nunca perde; pode duplicar | retente até confirmar |
| **Exactly-once (efeito)** | o efeito ocorre uma vez | **at-least-once + idempotência** |

> **"Exactly-once" existe — mas no processamento, não na entrega.** Quando um fornecedor
> anuncia "exactly-once", ele está falando de at-least-once com deduplicação no consumidor.
> Isso é legítimo e útil; a formulação é que é enganosa.

---

## 4. Idempotência: formalização

**Definição.** Uma operação $f$ é idempotente sobre um estado $S$ quando

$$f(f(S)) = f(S)$$

para todo $S$ no domínio.

**Exemplos:**

| Operação | Idempotente? | Por quê |
|---|---|---|
| `saldo := 100` | ✅ | atribuição absoluta |
| `saldo := saldo - 10` | ❌ | depende do estado anterior |
| `DELETE /pedidos/42` | ✅ | ausente é ausente |
| `POST /pedidos` | ❌ | cria um novo a cada chamada |
| `POST /pedidos` **com chave** | ✅ | a chave torna a segunda chamada um no-op |

**A construção geral.** Dada uma operação $g$ não idempotente, construímos uma versão
idempotente $g_k$ com uma chave $k$:

$$
g_k(S) =
\begin{cases}
S & \text{se } k \in \text{Processadas}(S) \\
g(S) \cup \{k\} & \text{caso contrário}
\end{cases}
$$

**O ponto crítico — e é aqui que quase toda implementação erra.** A verificação
$k \in \text{Processadas}(S)$ e a aplicação de $g$ precisam ser **atômicas**. Se não forem:

```text
tempo →
Thread A:  verifica k ∉ P  ──────────────► aplica g, insere k
Thread B:        verifica k ∉ P ──────────► aplica g, insere k
                                    ↑
                     g foi aplicada DUAS vezes
```

**Por isso a garantia tem que estar numa constraint de unicidade do armazenamento.** Um
`SELECT` seguido de `INSERT` deixa a janela aberta; um `INSERT` com `UNIQUE` na chave faz o
banco rejeitar a segunda escrita, e a atomicidade vem do próprio banco.

**Corolário prático:** idempotência implementada em código de aplicação, sem apoio do
armazenamento, é **incorreta sob concorrência**. Ela funciona nos testes (sequenciais) e
falha em produção (concorrente) — o que a torna especialmente perigosa.

---

## 5. Teorema CAP e além

**CAP** (Brewer, 2000; formalizado por Gilbert & Lynch, 2002): um sistema distribuído não
pode oferecer simultaneamente

- **C**onsistência (toda leitura vê a última escrita),
- **A**vailability (toda requisição recebe resposta),
- **P**artition tolerance (funciona apesar de partições de rede).

**A leitura correta, que difere da popular:** partições **acontecem** — não são opcionais.
Logo, a escolha real é: **quando houver partição**, você prefere responder com dado
possivelmente velho (AP) ou recusar-se a responder (CP)?

**PACELC** (Abadi, 2012) completa e é mais útil:

> **Se** há **P**artição, escolha entre **A**vailability e **C**onsistency;
> **E**lse (operação normal), escolha entre **L**atência e **C**onsistência.

O "else" é o que importa no dia a dia: **mesmo sem partição**, consistência forte custa
latência, porque exige coordenação entre réplicas.

**Aplicação a APIs:**

| Decisão | Consequência |
|---|---|
| Ler de réplica de leitura | ganha latência, perde consistência (*read-your-writes* quebra) |
| Cache com `max-age=60` | ganha escala, aceita dado com até 60 s de atraso |
| Confirmar antes de propagar (`202`) | ganha disponibilidade, aceita consistência eventual |
| Transação distribuída (2PC) | ganha consistência, perde disponibilidade e latência |

> **O caso clássico de bug:** o cliente faz `POST /pedidos`, recebe `201`, e imediatamente
> faz `GET /pedidos` — e o pedido não está lá, porque a leitura foi para uma réplica que
> ainda não replicou. É o problema de **read-your-writes**, e as soluções conhecidas são:
> rotear a leitura subsequente para o primário por um período, usar *sticky sessions* por
> usuário, ou devolver o recurso completo no `201` para o cliente não precisar reler.

---

## 6. Impossibilidade de consenso: FLP

**Teorema FLP** (Fischer, Lynch, Paterson, 1985). Num sistema **assíncrono** com pelo menos
um processo sujeito a falha por parada, **não existe algoritmo determinístico que garanta
consenso**.

**A intuição:** num sistema assíncrono não há limite superior para o atraso de mensagens.
Logo, um processo **lento** é indistinguível de um processo **morto**. Se você espera, pode
esperar para sempre; se desiste, pode desistir de alguém vivo.

**Como sistemas reais contornam:**

| Estratégia | Exemplo |
|---|---|
| Suposições de sincronia parcial | Raft, Paxos com detectores de falha por timeout |
| Aleatoriedade | consenso probabilístico |
| Abandonar o consenso forte | CRDTs, consistência eventual |

**A consequência para APIs:** **não existe commit atômico barato entre dois sistemas
independentes.** 2PC bloqueia se o coordenador cair; 3PC exige suposições de sincronia. É
por isso que a resposta padrão é **Saga com compensação** — que não é atômica, mas é
operável.

---

## 7. Transactional outbox e o padrão Saga

**O problema concreto:** gravar no banco **e** publicar um evento, atomicamente. Não dá:
são dois sistemas.

```text
❌ INSERT no banco; publicar no Kafka
   → falha entre os dois: o dado existe, ninguém foi avisado

❌ Publicar no Kafka; INSERT no banco
   → falha entre os dois: avisaram sobre algo que não existe
```

**A solução — transactional outbox:**

```sql
BEGIN;
  INSERT INTO pedidos (...) VALUES (...);
  INSERT INTO outbox (tipo, payload) VALUES ('PedidoCriado', '...');
COMMIT;                  -- UMA transação, UM banco: é atômico
```
Um processo separado lê a `outbox` e publica, marcando o que já publicou. Se ele publicar
duas vezes (porque caiu antes de marcar), o consumidor deduplica pelo id.

**Garantia resultante:** at-least-once + idempotência no consumidor = **efeito exactly-once**.
É a aplicação direta da §3 e da §4.

**Saga** generaliza isso para uma sequência de passos, cada um com uma **compensação**:

```text
Reservar estoque   →  Cobrar cartão  →  Agendar entrega
      ↓ falhou           ↓ falhou           ↓ falhou
  (nada a fazer)   liberar estoque    estornar + liberar
```

**O que se perde em relação a uma transação ACID:** não há **isolamento**. Existe um
intervalo em que o estoque está reservado e o cartão não foi cobrado — e outro cliente pode
observar esse estado intermediário. É consistência eventual com estados intermediários
visíveis, e o desenho do negócio precisa tolerá-los.

---

## 8. Compatibilidade de contratos é um problema de subtipagem

Esta seção conecta a evolução de APIs à teoria de tipos, e é a que mais muda como se pensa
sobre versionamento.

**Formulação.** Uma mudança de contrato de $C_1$ para $C_2$ é **compatível para trás**
(clientes antigos continuam funcionando) se e somente se

$$C_2 <: C_1$$

no sentido de subtipagem: todo valor válido segundo $C_2$ é aceitável onde $C_1$ era
esperado.

**A regra da variância** (Liskov) determina tudo:

| Posição | Regra | Em API |
|---|---|---|
| **Resposta** (saída, covariante) | pode ser **mais específica** | ✅ adicionar campo · ❌ remover campo |
| **Requisição** (entrada, contravariante) | pode ser **mais geral** | ✅ tornar opcional · ❌ tornar obrigatório |

**É por isso que:**
- adicionar campo na **resposta** é seguro (o cliente ignora o que não conhece);
- adicionar campo **obrigatório** na **requisição** quebra (o cliente antigo não o envia);
- **afrouxar** validação de entrada é seguro; **apertar** quebra;
- `additionalProperties: false` na entrada **inverte** isso: adicionar um campo à resposta
  continua seguro, mas o cliente que valida a resposta com `false` quebra.

**O incômodo teórico:** a regra é limpa, mas a **Lei de Hyrum** ([10](10-fundamentos.md) §1)
diz que o contrato **efetivo** não é o declarado — é o comportamento observável. Formalmente:

$$C_{\text{efetivo}} = C_{\text{declarado}} \cap \bigcap_{i} O_i$$

onde $O_i$ é o conjunto de comportamentos de que o cliente $i$ efetivamente depende.

Como $O_i$ é **desconhecido e inobservável** pelo provedor, a compatibilidade não é
verificável estaticamente no caso geral. Ferramentas como `oasdiff` verificam
$C_{\text{declarado}}$ — que é o melhor que se pode fazer mecanicamente, e é
**estritamente insuficiente**.

**A saída prática, e é uma aproximação, não solução:** *consumer-driven contract testing*
(Pact). Cada consumidor **declara** o seu $O_i$, e o provedor verifica contra a união deles.
Converte um problema inobservável num observável — ao custo de exigir cooperação de todos
os consumidores, o que só é viável dentro de uma organização.

---

## 9. Complexidade de consultas: por que GraphQL precisa de limites

**O problema.** Numa consulta GraphQL com aninhamento, o número de nós resolvidos pode
crescer **exponencialmente** na profundidade.

```graphql
{ usuario { amigos { amigos { amigos { amigos { nome } } } } } }
```

Com fator de ramificação médio $b$ e profundidade $d$, o número de nós é $O(b^d)$.
Com $b = 100$ e $d = 5$: $10^{10}$ nós. **Uma consulta de 6 linhas derruba o servidor.**

**Formalmente:** o problema de decidir se uma consulta arbitrária termina dentro de um
orçamento de recursos é, no caso geral com ciclos no grafo de tipos, **não decidível
estaticamente** sem conhecer os dados.

**Mitigações, todas aproximações:**

| Técnica | Limitação |
|---|---|
| **Depth limiting** | não captura consulta rasa e larga |
| **Complexity/cost analysis** (peso por campo) | os pesos são estimativas; não conhecem os dados |
| **Node limit** | corta no meio da execução; resposta parcial |
| **Persisted queries** (só consultas pré-aprovadas) | ✅ **a única defesa completa** — mas elimina a flexibilidade que é o ponto do GraphQL |
| **Timeout** | protege o servidor, não o banco |

> **O trade-off exposto:** GraphQL vende flexibilidade do cliente. Persisted queries — a
> única defesa que realmente funciona — **removem essa flexibilidade**. Na prática, APIs
> GraphQL públicas convergem para persisted queries ou para cost analysis conservadora, o
> que as aproxima funcionalmente de... um conjunto de endpoints REST. Isso não invalida
> GraphQL; explica por que ele brilha em contexto **interno**, onde o cliente é confiável.

**REST não tem esse problema** porque o servidor decide a forma da resposta. É o mesmo
trade-off de expressividade contra previsibilidade de custo que aparece em SOQL, em
consultas SQL de usuário final, e na restrição de interface uniforme do REST.

---

## 10. Limites teóricos, em uma tabela

| Problema | Limite | Consequência prática |
|---|---|---|
| Acordo sobre canal não confiável | **impossível** (dois generais) | não há exactly-once na entrega |
| Consenso assíncrono com uma falha | **impossível** (FLP) | timeouts e suposições de sincronia |
| C + A + P simultâneos | **impossível** (CAP) | consistência eventual nas integrações |
| Distinguir lento de morto | **impossível** em sistema assíncrono | todo timeout é um palpite |
| Commit atômico entre sistemas | possível, mas **bloqueante** (2PC) | outbox + saga |
| Verificar compatibilidade real de contrato | **inobservável** (Lei de Hyrum) | contract testing como aproximação |
| Limitar custo de consulta arbitrária | **indecidível** no caso geral | persisted queries ou heurística |
| Latência mínima entre dois pontos | **velocidade da luz** | ~30 ms São Paulo–Nova York, ida e volta |
| Detectar duplicata sem estado | **impossível** | idempotência exige armazenamento |

**O padrão que atravessa a tabela:** onde há um limite teórico, a engenharia substitui a
**garantia** por uma **aproximação com falha explícita** — timeout em vez de detecção de
falha, idempotência em vez de exactly-once, consistência eventual em vez de forte. **APIs
bem projetadas expõem essa aproximação; mal projetadas fingem que a garantia existe.**

---

## 11. Questões em aberto

1. **Verificação formal de compatibilidade de contratos.** Dado $C_1$, $C_2$ e o **código**
   dos consumidores, decidir compatibilidade. Requer análise interprocedural entre
   repositórios e linguagens diferentes. Nada prático existe.

2. **Estimativa de custo de consulta antes da execução.** Fundamental para GraphQL e para
   qualquer API com consulta flexível. Estimadores baseados em estatísticas erram por ordens
   de grandeza em dados enviesados.

3. **Composição de SLOs.** Dado o SLO de cada serviço, calcular o do sistema é fácil para
   dependências independentes em série. Com dependências correlacionadas, retentativas e
   circuit breakers, **não existe modelo fechado**.

4. **Detecção automática de acoplamento semântico.** O acoplamento de formato é detectável
   (diff de schema). O semântico — o cliente reimplementou a sua regra — não é observável
   pelo provedor.

5. **APIs para agentes.** Com um LLM como consumidor, o "contrato" inclui a **descrição em
   linguagem natural**, que é ambígua por natureza. Como especificar e verificar uma API
   cujo consumidor interpreta linguagem natural? É um problema novo, aberto, e a área que eu
   consideraria mais promissora hoje.

6. **Idempotência distribuída sem armazenamento compartilhado.** Toda solução conhecida
   exige um ponto de deduplicação. Provar a necessidade desse ponto — ou encontrar uma
   construção que o dispense — é uma questão em aberto interessante.

---

## Autoteste

1. Cite as oito falácias. Qual delas corresponde a uma impossibilidade e não a um defeito?
2. Enuncie os quatro estados possíveis quando não se recebe resposta. Por que são indistinguíveis?
3. Esboce a prova do problema dos dois generais. Qual consequência ela tem para APIs?
4. Por que "exactly-once" existe no processamento e não na entrega?
5. Formalize idempotência. Onde exatamente a implementação ingênua falha sob concorrência?
6. Por que a garantia de idempotência precisa estar no armazenamento?
7. O que PACELC acrescenta ao CAP? Qual metade é mais relevante no dia a dia?
8. O que o FLP torna impossível? Como sistemas reais contornam?
9. Descreva o transactional outbox. Que garantia ele produz, combinado com o quê?
10. Explique a compatibilidade de contratos como subtipagem. Por que resposta e requisição têm regras opostas?
11. Por que a compatibilidade real é inobservável? Qual é a aproximação prática?
12. Por que persisted queries são a única defesa completa em GraphQL, e o que elas custam?

---

### Referências

- Deutsch, P. et al. — *The Eight Fallacies of Distributed Computing*, Sun Microsystems, ~1994
- Waldo, J. et al. — *A Note on Distributed Computing*, Sun Labs TR-94-29, 1994
- Fischer, M., Lynch, N., Paterson, M. — *Impossibility of Distributed Consensus with One Faulty Process*, JACM 32(2), 1985
- Gilbert, S., Lynch, N. — *Brewer's Conjecture and the Feasibility of Consistent, Available, Partition-Tolerant Web Services*, SIGACT News 33(2), 2002
- Abadi, D. — *Consistency Tradeoffs in Modern Distributed Database System Design (PACELC)*, IEEE Computer, 2012
- Liskov, B., Wing, J. — *A Behavioral Notion of Subtyping*, TOPLAS 16(6), 1994
- Kleppmann, M. — *Designing Data-Intensive Applications*, O'Reilly, 2017
- Richardson, C. — *Microservices Patterns* (outbox, saga), Manning, 2018
- Hardt, D. et al. — *Hyrum's Law* — https://www.hyrumslaw.com/
