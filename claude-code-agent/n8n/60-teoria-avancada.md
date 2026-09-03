# 60 · Teoria avançada — o que o n8n é, formalmente

`Nível: pesquisa` · `01/09/2026`

---

Este arquivo trata o n8n como objeto teórico: qual modelo de computação ele
implementa, quais garantias ele pode e não pode dar, e onde estão os limites
demonstráveis — não os de implementação.

---

## 1. O n8n é uma linguagem de fluxo de dados

Formalmente, um workflow é um **grafo dirigido acíclico rotulado**
`G = (V, E, λ)`:

- `V` = nós, cada um com um tipo, uma versão e uma configuração;
- `E ⊆ V × ℕ × V × ℕ` = arestas, ligando (nó de origem, índice da saída) a
  (nó de destino, índice da entrada);
- `λ` = a função de rotulação que associa a cada nó a sua função de transformação.

Cada nó é uma função `f : Item* → (Item*)ⁿ`, de uma **sequência** de itens para `n`
sequências (uma por saída). Não é `Item → Item`: o nó vê todos os itens de uma vez,
e é isso que permite Sort, Aggregate e Merge existirem.

Isso põe o n8n na família das **linguagens de dataflow**, ao lado de LabVIEW,
Max/MSP, Apache Beam e Airflow. A diferença é o modelo de disparo (a seguir).

### 1.1 Por que acíclico?

Um grafo com ciclo exige uma **condição de terminação** — algo que decida quando
parar. Modelos de dataflow com ciclo (as *Kahn Process Networks*, por exemplo)
resolvem isso com canais de capacidade infinita e semântica de processo contínuo,
o que exige que cada nó seja um processo vivo, não uma função que roda uma vez.

O n8n escolheu o modelo simples — **cada nó executa e produz** — e realiza a
repetição fora do grafo (nó `Loop Over Items`, com um fio de retorno tratado pelo
motor como reentrada controlada, não como ciclo do grafo). É uma decisão de
implementabilidade e de depurabilidade, não uma limitação teórica.

---

## 2. Modelo de disparo: por que não há paralelismo

Redes de dataflow clássicas disparam um nó **quando seus dados de entrada estão
disponíveis** (*data-driven*), o que permite paralelismo natural. O n8n usa outra
coisa: um **percurso em profundidade sobre uma pilha de nós**, ramo por ramo, com
desempate pela posição vertical no canvas.

Consequência formal: a ordem de execução é uma **linearização total** do grafo
compatível com a ordem parcial das dependências, escolhida deterministicamente.

**Duas consequências práticas:**

1. Não há concorrência **dentro** de uma execução. Um workflow com dois ramos
   independentes leva `t₁ + t₂`, não `max(t₁, t₂)`.
2. A execução é **reproduzível**: mesmo grafo, mesma entrada, mesma ordem.
   Isso é o que torna o histórico de execução legível como uma narrativa.

**Este é um trade-off deliberado: desempenho por depurabilidade.**
Para uma ferramenta cuja proposta central é "você vê o que aconteceu em cada
caixa", foi a escolha certa. Para processamento de alto volume, é o motivo pelo
qual ela é a ferramenta errada.

---

## 3. Item linking como relação de proveniência

O `pairedItem` define uma relação `⊳ ⊆ Itens × Itens`, onde `a ⊳ b` significa
"o item `a` contribuiu para o item `b`". O fecho transitivo dessa relação é a
**proveniência** (*data provenance*) do item.

A expressão `$('N').item`, avaliada no item `x`, resolve
`{ y ∈ saída(N) : y ⊳* x }` — e exige que esse conjunto tenha **exatamente um**
elemento. Quando tem zero (a cadeia foi rompida) ou mais de um (o item veio de
vários), o n8n falha com `Can't determine which item to use`.

**Por que falhar em vez de escolher?** Porque qualquer escolha seria arbitrária e
silenciosa — e um dado errado sem aviso é estritamente pior que um erro. Este é o
mesmo princípio de *fail fast* que justifica tipos estáticos: **detectar cedo a um
custo visível**.

Literatura relacionada: proveniência de dados (Buneman, Khanna, Tan, *Why and
Where: A Characterization of Data Provenance*, ICDT 2001) distingue proveniência
*why* (quais entradas contribuíram) de *where* (de qual campo veio o valor).
O `pairedItem` implementa uma aproximação da proveniência *why*, no nível do item.

---

## 4. Garantias de entrega e o teorema que não dá para burlar

**Afirmação:** em um sistema com comunicação não confiável, é **impossível**
garantir entrega exatamente-uma-vez de ponta a ponta.

**Esboço do argumento (o problema dos dois generais).** O emissor manda `M` e
espera confirmação. Se a confirmação não chega, ele não consegue distinguir
"`M` se perdeu" de "`M` chegou e a confirmação se perdeu". Reenviar arrisca
duplicar; não reenviar arrisca perder. Nenhum protocolo finito resolve o dilema,
porque toda mensagem adicional herda o mesmo problema.

**Consequência para o n8n:** o que existe é *at-least-once* (reenvio do provedor +
retry do worker + reprocessamento de execução órfã). *Exactly-once* observável só
se obtém com **idempotência no receptor** — motivo pelo qual o
[projeto-modelo](07-projeto-modelo/README.md) põe a garantia numa `PRIMARY KEY`, e
não em um `if`.

**Corolário útil:** discussões sobre "a ferramenta X garante exactly-once" são,
sem exceção, sobre *effectively-once* — at-least-once mais deduplicação em algum
ponto. Vale para Kafka, para filas e para o n8n.

---

## 5. O modelo de execução é Turing-completo?

Sim, e de forma quase trivial: o node Code executa JavaScript arbitrário. Mesmo
sem ele, o conjunto {IF, Loop Over Items, `staticData`} dá teste condicional,
repetição e memória mutável — o suficiente para simular uma máquina de registradores.

**Por que isso importa na prática?** Porque implica que **não existe análise
estática completa de workflows**: não dá para decidir, em geral, se um fluxo
termina, quantas chamadas de API vai fazer, ou se toca um dado sensível.
É o problema da parada. Toda ferramenta de análise de fluxo é necessariamente
aproximada — e é por isso que os limites operacionais do n8n são **dinâmicos**
(timeout de execução, timeout de tarefa, limite de concorrência, teto de páginas),
e não verificações prévias.

Esta é uma **parada legítima** na regra dos cinco porquês: o limite é matemático,
não de engenharia.

---

## 6. Complexidade e custo

Para um workflow com `n` nós e `k` itens no maior fio:

| Grandeza | Ordem |
|---|---|
| Tempo | `O(Σᵢ custo(vᵢ) · kᵢ)` — dominado pelos nós de I/O |
| Memória de pico | `O(max sobre os fios de (kᵢ · tamanho do item))`, mais o `runData` acumulado |
| Armazenamento por execução | `O(Σᵢ kᵢ · tamanho do item)` — **soma sobre todos os nós** |

A terceira linha é a que surpreende: o custo de disco de uma execução é a **soma**
dos dados de todos os nós, não o tamanho do dado final. Um fluxo de 20 nós que
carrega 5 MB pode gravar ~100 MB por execução. É a explicação formal de por que a
poda de execuções é obrigatória ([21](21-escala-e-producao.md)).

---

## 7. O limite arquitetural, enunciado com precisão

> **O n8n materializa integralmente a saída de cada nó antes de executar o
> seguinte.** Não há avaliação preguiçosa nem streaming.

Isso é forçado por três requisitos simultâneos que a ferramenta assume:

1. Nós agregadores (Sort, Aggregate, Merge) **precisam** do conjunto completo.
2. A interface **precisa** mostrar a tabela de saída de cada nó.
3. A retentativa a partir de um nó **precisa** da entrada dele preservada.

Qualquer um dos três, isolado, já impede streaming verdadeiro. Os três juntos
tornam a escolha inevitável.

**Portanto:** o n8n é ótimo para `k` pequeno e `n` grande (muitos passos, poucos
itens) e ruim para `k` grande e `n` pequeno (poucos passos, muitos itens).
Este é o critério objetivo para decidir se a ferramenta serve. Para `k` grande,
o lugar certo do trabalho é o banco de dados, uma ferramenta de ETL, ou um
programa — e o n8n pode continuar **orquestrando** isso.

---

## 8. Comparação formal com Airflow e Temporal

| | n8n | Apache Airflow | Temporal |
|---|---|---|---|
| Unidade | item (dado) | tarefa (comando) | atividade (função) |
| O que trafega | os dados | referências/XCom pequeno | argumentos serializados |
| Disparo | percurso em pilha | escalonador com dependências | replay determinístico do histórico |
| Paralelismo intra-execução | **não** | sim | sim |
| Durabilidade | execução no banco | metadados no banco | **event sourcing completo** |
| Retomada após queda | do início, ou pela fila | por tarefa | **do ponto exato** |
| Autor típico | analista/dev | engenheiro de dados | engenheiro de software |

**Temporal é o contraponto teoricamente mais interessante.** Ele grava um
histórico de eventos e, ao retomar, **reexecuta o código de forma determinística**
até o ponto da falha, restaurando o estado. É uma garantia mais forte que a do n8n
— e custa: o código precisa ser determinístico, toda I/O precisa passar por
atividades, e não existe interface visual de arrastar caixas.

Não são concorrentes: resolvem problemas em pontos diferentes do espectro
"acessibilidade × garantia". Escolher entre eles é escolher qual das duas
propriedades vale mais no seu contexto.

---

## 9. Problemas em aberto (na minha leitura do campo)

1. **Análise estática útil apesar da indecidibilidade.** Dá para provar, com
   aproximação conservadora, que um fluxo não vaza PII para fora, ou que faz no
   máximo `N` chamadas? Há trabalho em *taint analysis* que se aplicaria.
2. **Composição verificável.** Sub-workflows não têm contrato declarado. Um
   sistema de tipos leve sobre a forma dos itens tornaria a composição segura —
   e é a lacuna mais visível da ferramenta hoje.
3. **Retomada por nó.** Retomar do ponto exato, como o Temporal, sem exigir
   determinismo do usuário. Provavelmente exigiria *snapshot* por nó — caro em
   armazenamento, mas os custos mudaram desde que a decisão original foi tomada.
4. **Semântica de agentes.** Quando um LLM escolhe o próximo passo, o "grafo" é
   construído em tempo de execução. As noções de proveniência e reprodutibilidade
   deste arquivo **não se aplicam diretamente**. É a fronteira teórica mais quente
   do campo em 2026, e ninguém tem uma resposta boa ainda.
5. **Teste de fluxos com efeito colateral.** Não há uma teoria boa de *mocking*
   para workflows visuais. `Pin data` é um paliativo manual.

---

## Autoteste

1. Escreva a definição formal de um workflow como grafo.
2. Por que a assinatura de um nó é `Item* → (Item*)ⁿ` e não `Item → Item`?
3. Por que grafos com ciclo exigiriam um modelo de execução diferente?
4. Que tipo de ordem a execução v1 impõe sobre o grafo?
5. Enuncie a relação que o `pairedItem` define e o que `$('N').item` resolve.
6. Esboce o argumento dos dois generais e sua consequência para o n8n.
7. O n8n é Turing-completo? Que consequência prática isso tem para análise de fluxos?
8. Por que o custo de armazenamento de uma execução é uma **soma** sobre os nós?
9. Enuncie o limite arquitetural e os três requisitos que o forçam.
10. Qual garantia o Temporal dá que o n8n não dá, e qual é o preço?
11. Por que a noção de proveniência deste arquivo não se aplica bem a agentes de IA?

---

*Referências: Kahn, G. (1974) "The Semantics of a Simple Language for Parallel
Programming"; Dennis, J. (1974) "First Version of a Data Flow Procedure Language";
Buneman, Khanna & Tan (2001) "Why and Where: A Characterization of Data Provenance",
ICDT; Gray, J. & Lamport, L. sobre consenso e o problema dos dois generais.
Ver [90-bibliografia.md](90-bibliografia.md).*

*Anterior: [25-api-e-integracao-externa.md](25-api-e-integracao-externa.md) · Próximo: [65-estado-da-arte.md](65-estado-da-arte.md)*
