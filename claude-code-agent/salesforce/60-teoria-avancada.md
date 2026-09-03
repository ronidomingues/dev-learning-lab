# 60 · Teoria avançada

`Nível: pesquisa` · `Atualizado: 11/08/2026`

Este arquivo trata dos problemas **teóricos** por trás das decisões de engenharia da
plataforma. Não é sobre como usar Salesforce — é sobre por que os problemas que ela resolve
são difíceis, e onde estão os limites que nenhuma implementação supera.

Pré-requisitos: [19-multitenancy-arquitetura.md](19-multitenancy-arquitetura.md), noções
de complexidade computacional, de bancos de dados e de sistemas distribuídos.

---

## 1. O problema do isolamento de performance

### 1.1 Formulação

Dado um conjunto de inquilinos $T = \{t_1, \dots, t_n\}$ compartilhando um recurso de
capacidade $C$, e uma carga $w_i(\tau)$ de cada inquilino no instante $\tau$, garanta que
o desempenho percebido por $t_i$ seja **independente** de $w_j$ para todo $j \neq i$.

Essa é a propriedade de **isolamento de performance**, e ela é, no caso geral,
**impossível de garantir de forma exata** com recursos compartilhados e capacidade finita.
A prova é trivial: se $\sum_i w_i > C$, alguém espera.

O que é possível é **degradação limitada e previsível**: garantir que $t_i$ receba pelo
menos uma fração $C/n$ da capacidade quando saturado, e mais quando houver folga. É o
conceito de *max-min fairness*.

### 1.2 As três famílias de solução

| Abordagem | Mecanismo | Custo | Onde aparece |
|---|---|---|---|
| **Particionamento estático** | reserve $C/n$ para cada um | desperdiça capacidade ociosa | VMs dedicadas |
| **Escalonamento justo dinâmico** | fila com pesos; preempção | precisa de preempção barata | CFS do Linux, WFQ em redes |
| **Orçamento com aborto** | conte o consumo, aborte ao estourar | trabalho perdido no aborto | **governor limits do Salesforce** |

**Por que a Salesforce escolheu a terceira?**

Escalonamento justo exige **preempção**: interromper uma execução e retomá-la depois.
Numa transação de banco, preemptar significa salvar e restaurar: pilha de execução,
cursores abertos, bloqueios adquiridos, buffers, estado do compilador. É caro e complexo,
e mantém bloqueios de banco vivos por um tempo indeterminado — que é exatamente o problema
que se queria evitar.

**Orçamento com aborto tem uma propriedade decisiva:** o custo do enforcement é
**O(1) por operação** — incrementar um contador e comparar. Isso o torna praticamente
gratuito, ao preço de descartar trabalho já feito quando o limite estoura.

**O trade-off formal:** trocar *eficiência* (trabalho perdido) por *previsibilidade* e
*custo de mecanismo*. Para um sistema com centenas de milhares de inquilinos e transações
tipicamente curtas, é a escolha correta — o trabalho perdido é raro e pequeno; o custo de
preempção seria pago em **toda** transação.

### 1.3 O que a literatura chama de "noisy neighbor"

O problema é bem estudado. Duas referências úteis:

- **Dominant Resource Fairness** (Ghodsi et al., NSDI 2011) — generaliza max-min fairness
  para múltiplos tipos de recurso (CPU, memória, I/O). É o que o Mesos e o YARN implementam.
- **Performance Isolation in Multi-Tenant Databases** — linha de trabalho sobre alocação de
  buffer pool, I/O e CPU em SGBDs compartilhados.

O modelo do Salesforce é mais grosseiro que qualquer um deles — e mais robusto justamente
por isso: não depende de estimativas de custo nem de previsão de carga, apenas de contagem.

---

## 2. Complexidade do modelo de sharing

### 2.1 O problema

Dado:
- $U$ usuários,
- $R$ registros,
- uma hierarquia de papéis $H$ (árvore de profundidade $d$),
- um conjunto $S$ de regras de compartilhamento,

determine, para cada par $(u, r)$, se $u$ pode acessar $r$.

**A abordagem ingênua** — materializar todos os pares — custa $O(|U| \cdot |R|)$ de espaço.
Numa org com 5.000 usuários e 50 milhões de registros, são $2{,}5 \times 10^{11}$ entradas.
Inviável.

### 2.2 A abordagem real

A Salesforce materializa **parcialmente**: a tabela `X__Share` guarda apenas os
compartilhamentos que **não** decorrem de regras derivadas na hora.

```text
Acesso(u, r) = Dono(u, r)
             ∨ AcimaNaHierarquia(u, dono(r))
             ∨ ∃ s ∈ S : s concede acesso a u sobre r
             ∨ ∃ linha em X__Share ligando u (ou um grupo de u) a r
             ∨ ImplicitSharing(u, r)
             ∨ ViewAllData(u) ∨ ModifyAllData(u) ∨ ViewAll(u, tipo(r))
```

O termo `AcimaNaHierarquia` é resolvido por **grupos materializados**: cada papel tem um
grupo "papel e subordinados", pré-calculado. A consulta vira uma verificação de pertinência
a grupo — $O(1)$ amortizado — em vez de uma travessia de árvore.

### 2.3 Por que o recálculo é caro

Quando algo muda estruturalmente — o dono de um registro, a posição de um usuário na
hierarquia, uma sharing rule —, é preciso recalcular as linhas materializadas afetadas.

**Custo aproximado de mover um usuário na hierarquia de papéis:**

$$O\big(|R_u| \times |D(u)| \times |S_{\text{afetadas}}|\big)$$

onde $|R_u|$ é o número de registros que ele possui e $|D(u)|$ o número de descendentes do
novo papel. Com $|R_u| = 500{.}000$ (ownership skew, ver
[12-modelo-de-dados.md](12-modelo-de-dados.md) §7.2) e uma hierarquia larga, esse produto
explode — e é literalmente por isso que a recomendação de manter o usuário de integração
**fora** da hierarquia existe. Não é superstição operacional: é o termo $|D(u)|$ indo a zero.

### 2.4 O trade-off de materialização

| Estratégia | Leitura | Escrita | Espaço |
|---|---|---|---|
| Tudo materializado | O(1) | $O(|U|)$ por registro | $O(|U| \cdot |R|)$ |
| Nada materializado | $O(|S| + d)$ por checagem | O(1) | O(1) |
| **Híbrido (Salesforce)** | O(1) amortizado | proporcional ao alcance da mudança | proporcional ao compartilhamento real |

É o mesmo trade-off de *view materializada* vs. *view virtual* em bancos de dados, aplicado
a controle de acesso. A escolha híbrida é a certa porque leitura é ordens de magnitude mais
frequente que mudança estrutural.

---

## 3. O otimizador de consultas sob multi-inquilino

### 3.1 Por que estatísticas globais não servem

Um otimizador clássico estima a seletividade de um predicado $p$ sobre uma tabela $T$ como

$$\text{sel}(p) = \frac{|\sigma_p(T)|}{|T|}$$

usando histogramas globais. Numa tabela compartilhada, $T = \bigcup_i T_i$ e as distribuições
$T_i$ são radicalmente diferentes: a org A pode ter 90% dos registros com
`Status__c = 'Ativo'` e a org B, 2%.

Usar a estatística global levaria a decisões erradas **para quase todos** os inquilinos —
o clássico problema de estimativa sob mistura de distribuições.

### 3.2 A solução: estatísticas por inquilino

A Salesforce mantém, por org e por objeto, a contagem de linhas e a distribuição dos campos
indexados. O otimizador calcula

$$\text{sel}_i(p) = \frac{|\sigma_p(T_i)|}{|T_i|}$$

e compara com os limiares (30%/15% para índice padrão; 10% para customizado).

**O custo dessa escolha:** manter estatísticas por (org × objeto × campo) é caro em espaço e
em atualização. Elas são atualizadas periodicamente, não em tempo real — o que significa
que **existe uma janela em que o otimizador decide com dados desatualizados**. É a explicação
mais provável para o fenômeno conhecido de "a consulta ficou lenta depois de uma carga
grande e melhorou sozinha no dia seguinte".

### 3.3 Limite teórico: seleção de plano é NP-difícil

A escolha da ordem de junção em consultas com $n$ relações é um problema clássico:
o número de ordens possíveis cresce como $\Omega(n!)$ para árvores lineares e mais rápido
para árvores em bushy. A otimização de consultas por programação dinâmica
(System R, Selinger et al., 1979) custa $O(2^n)$ em tempo e espaço.

**Isso ilumina uma decisão de projeto do SOQL.** Ao **eliminar joins arbitrários** e permitir
apenas travessia por relacionamentos declarados, a Salesforce reduz o espaço de planos de
exponencial para essencialmente **linear no número de relacionamentos percorridos**.

A restrição de expressividade não é preguiça — **é o que torna o custo de otimização
previsível num ambiente onde o otimizador roda milhões de vezes por hora para inquilinos
que não pagam por CPU de otimização.**

Este é, na minha avaliação, o insight mais bonito da arquitetura: uma limitação da linguagem
que compra previsibilidade de custo no otimizador.

---

## 4. Consistência e transações

### 4.1 O que a plataforma garante

| Propriedade | Garantia |
|---|---|
| Atomicidade | ✅ dentro de uma transação Apex |
| Consistência | ✅ validation rules, constraints únicos, obrigatoriedade |
| Isolamento | parcial — ver abaixo |
| Durabilidade | ✅ após o commit |

**Sobre isolamento:** a Salesforce não expõe níveis de isolamento configuráveis. O
comportamento observável é próximo de *read committed* com bloqueios explícitos via
`FOR UPDATE`. Não há *serializable* garantido, e **não há transação distribuída** entre
a org e sistemas externos.

### 4.2 A impossibilidade fundamental

Não existe transação atômica entre dois sistemas independentes sem um protocolo de
coordenação (2PC, 3PC, Paxos commit). E protocolos de commit distribuído:

- **bloqueiam** na falha do coordenador (2PC);
- exigem controle de ambos os lados;
- custam múltiplos *round-trips*;
- na presença de partição de rede, esbarram no **teorema CAP** (Brewer, 2000; Gilbert &
  Lynch, 2002): não se pode ter consistência, disponibilidade e tolerância a partição
  simultaneamente.

**Por isso a plataforma proíbe callout com trabalho não commitado.** Ela não está tentando
implementar 2PC e falhando; está **recusando um problema que não tem solução barata**, e
empurrando o desenvolvedor para o padrão correto:

```text
Transactional Outbox:
  1. Numa única transação local: grave o dado E enfileire a intenção de notificar.
  2. Commite.
  3. Um processo separado lê a fila e notifica, com retentativa.
  4. O receptor deduplica por chave de idempotência.

Garantia resultante: at-least-once + idempotência = efeito exactly-once
```

Esse é o mesmo padrão descrito em *Designing Data-Intensive Applications* (Kleppmann) e
implementado em qualquer arquitetura de microsserviços séria. O Exemplo 13 de
[06-exemplos.md](06-exemplos.md) é uma implementação dele em Apex.

### 4.3 Por que "exactly-once" é impossível na entrega e possível no efeito

O resultado clássico: numa rede assíncrona com falhas, **não existe entrega exactly-once**.
Se o emissor não recebe o ACK, ele não pode distinguir entre "a mensagem não chegou" e
"a mensagem chegou e o ACK se perdeu". Reenviar pode duplicar; não reenviar pode perder.

A saída universal é mover a garantia do **transporte** para o **efeito**: entregue
*at-least-once* e torne a operação **idempotente**. A idempotência é o que transforma
duplicatas em no-ops.

E — este é o ponto que separa implementações corretas das ingênuas — a idempotência precisa
ser garantida por uma **constraint de unicidade no armazenamento**, não por um `SELECT`
antes do `INSERT`. Entre o select e o insert existe uma janela; concorrência encontra
janelas. É por isso que o campo `External Id` com `unique = true` é a peça central de toda
integração correta em Salesforce.

---

## 5. Limites teóricos que a plataforma encontra

| Problema | Limite | Consequência prática |
|---|---|---|
| Ordenação de junções | NP-difícil no caso geral | SOQL restringe a travessias declaradas |
| Isolamento de performance exato | impossível com recurso compartilhado finito | governor limits com aborto |
| Commit distribuído sem bloqueio | impossível (FLP, 1985) | outbox + idempotência |
| Consistência + disponibilidade + partição | teorema CAP | consistência eventual nas integrações |
| Detecção de terminação de programa | problema da parada | limites de tempo/CPU em vez de análise estática |
| Estimativa exata de cardinalidade | requer conhecer a distribuição | histogramas aproximados por inquilino |
| Alocação ótima sob demanda desconhecida | requer previsão do futuro | heurísticas e cotas |

**A linha de raciocínio geral:** onde há um limite teórico, a plataforma **substitui a
solução exata por uma heurística conservadora com falha explícita**. Ela prefere errar
recusando (query não seletiva, limite estourado) a errar aceitando e degradando todo mundo.

Isso é uma escolha de projeto defensável e coerente. É também a razão de a experiência do
desenvolvedor ser frustrante: **você encontra o "não" muito mais vezes do que encontraria
num sistema dedicado, porque o sistema está protegendo terceiros que você não vê.**

---

## 6. O problema da parada e os governor limits

Por que a plataforma não analisa estaticamente seu código e o rejeita se ele for consumir
demais?

**Porque isso é o problema da parada** (Turing, 1936). Determinar se um programa arbitrário
termina — e, a fortiori, quanto ele consome — é **indecidível** no caso geral.

As opções reais são:

| Opção | Viável? | Por quê |
|---|---|---|
| Análise estática exata | ❌ | indecidível |
| Análise estática conservadora | 🟡 | rejeitaria muito programa legítimo (falsos positivos) |
| Linguagem total (sem recursão irrestrita nem laços ilimitados) | 🟡 | reduz drasticamente a expressividade; ninguém aceitaria |
| **Medição em tempo de execução com aborto** | ✅ | decidível, O(1) por operação, sem falso positivo |

A quarta é a única prática. E note que ela dá uma garantia mais forte que a análise
estática daria: **não importa o que o código faça, o consumo é limitado**. Análise estática
poderia ser enganada; um contador não pode.

**É por isso que Apex tem `LimitException` e não um verificador de recursos em tempo de
compilação.** Não é falta de sofisticação — é a consequência direta de um resultado de 1936.

---

## 7. Questões em aberto

Problemas que continuam sem solução satisfatória, na plataforma e na literatura:

1. **Estimativa de custo de transação antes da execução.** Não há como um desenvolvedor
   saber, antes de rodar, se um Flow com 40 elementos sobre 200 registros vai estourar CPU.
   Ferramentas de *profiling* preditivo para linguagens com esse perfil de execução são um
   problema aberto.

2. **Recálculo incremental de sharing.** Hoje, mudanças estruturais disparam recálculos de
   custo aproximadamente proporcional ao alcance. Há trabalho acadêmico sobre manutenção
   incremental de views materializadas (IVM) que se aplicaria, mas não sob a restrição de
   fazê-lo online, em produção, sem janela.

3. **Isolamento de performance com garantia formal.** Os limites atuais são heurísticos e
   uniformes. Um sistema com SLO por inquilino, verificável formalmente, não existe em
   escala.

4. **Verificação de agentes de IA.** Com o Agentforce executando ações no CRM, como se
   **prova** que um agente não vai executar uma ação destrutiva? O Trust Layer aplica
   filtros e políticas, mas não há garantia formal de comportamento de um LLM. É o problema
   aberto mais urgente do produto atual.

5. **Migração automática entre plataformas.** Traduzir Apex+Flow+metadados para outra
   plataforma é, no caso geral, tradução entre linguagens com semânticas de execução
   diferentes — sem garantia de preservação. Se isso for resolvido, o lock-in do setor muda
   de natureza. É, na minha opinião, o eixo de pesquisa com maior impacto econômico potencial.

---

## Autoteste

1. Por que isolamento de performance exato é impossível com recurso compartilhado finito?
2. Compare as três famílias de solução de isolamento. Por que "orçamento com aborto" foi a escolha?
3. Por que materializar todos os pares (usuário, registro) é inviável? Qual é o híbrido usado?
4. Deduza o custo de mover um usuário na hierarquia de papéis. Ligue isso ao *ownership skew*.
5. Por que estatísticas globais não servem a um otimizador multi-inquilino?
6. Explique como a restrição de joins em SOQL reduz o custo de otimização. Por que isso importa aqui mais que num banco comum?
7. Por que não existe entrega exactly-once, e como se obtém o **efeito** exactly-once?
8. Por que a idempotência precisa ser garantida por constraint e não por `SELECT` antes de `INSERT`?
9. Ligue os governor limits ao problema da parada. Por que a medição em runtime dá uma garantia mais forte que a análise estática?
10. Escolha uma das cinco questões em aberto e argumente por que ela é difícil.

---

### Referências

- Selinger, P. G. et al. *Access Path Selection in a Relational Database Management System.* SIGMOD, 1979.
- Fischer, M., Lynch, N., Paterson, M. *Impossibility of Distributed Consensus with One Faulty Process.* JACM, 1985.
- Gilbert, S., Lynch, N. *Brewer's Conjecture and the Feasibility of Consistent, Available, Partition-Tolerant Web Services.* SIGACT News, 2002.
- Ghodsi, A. et al. *Dominant Resource Fairness: Fair Allocation of Multiple Resource Types.* NSDI, 2011.
- Turing, A. *On Computable Numbers, with an Application to the Entscheidungsproblem.* 1936.
- Kleppmann, M. *Designing Data-Intensive Applications.* O'Reilly, 2017.
- Salesforce. *The Force.com Multitenant Architecture* (whitepaper), 2008 — https://www.developerforce.com/media/ForcedotcomBookLibrary/Force.com_Multitenancy_WP_101508.pdf
