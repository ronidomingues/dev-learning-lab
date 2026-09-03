# 60 · Teoria avançada e limites

**Nível:** pesquisa · Atualizado em 13/08/2026

Este capítulo trata do que **não** dá para consertar com mais engenharia. Não
é pessimismo: saber onde está o muro é o que impede de gastar um trimestre
correndo nele.

---

## 1. O agente como POMDP

O enquadramento formal clássico. Um agente opera num **Processo de Decisão de
Markov Parcialmente Observável**, a sêxtupla ⟨*S, A, T, R, Ω, O*⟩:

| Símbolo | No agente de código |
|---|---|
| *S* — estados | o estado real do repositório, do sistema, do mundo |
| *A* — ações | chamadas de ferramenta |
| *T* — transição | o efeito de rodar um comando |
| *R* — recompensa | a tarefa foi resolvida? |
| *Ω* — observações | saídas de ferramenta, conteúdo de arquivo |
| *O* — modelo de observação | o que a saída revela sobre o estado |

**Parcialmente observável** é a palavra que carrega tudo: o agente nunca vê
*S*, só *Ω*. Ele mantém uma *crença* sobre o estado, construída a partir do
histórico. Duas consequências práticas caem direto daqui:

1. **Melhorar *O* costuma valer mais que melhorar a política.** Uma ferramenta
   que devolve o estado com precisão (o teste que falhou, com a linha e os
   valores) melhora o agente mais que um modelo melhor com observações pobres.
   Esta é a formalização da tese da ACI ([11](11-historia.md)).
2. **Contexto é o estado de crença.** Compactação é compressão com perdas do
   estado de crença — e por isso a informação que precisa sobreviver deve
   viver fora dele, num arquivo.

Resolver POMDPs de forma exata é PSPACE-difícil no caso finito, e indecidível
no caso geral com horizonte infinito. Ninguém "resolve" o POMDP: usa-se uma
política aproximada. O LLM **é** essa política aproximada.

---

## 2. Composição de erro

Se cada passo é independente e correto com probabilidade *p*, uma trajetória
de *n* passos tem probabilidade *pⁿ* de estar inteiramente correta:

| *p* | *n*=5 | *n*=10 | *n*=20 | *n*=50 |
|---|---|---|---|---|
| 0,95 | 77% | 60% | 36% | 8% |
| 0,99 | 95% | 90% | 82% | 61% |
| 0,999 | 99,5% | 99% | 98% | 95% |

O que a tabela diz é brutal: **99% de acerto por passo dá 61% de acerto numa
tarefa de 50 passos.** É por isso que agentes eram inúteis em 2023 — com *p* ≈
0,9, qualquer tarefa longa estava condenada.

Mas a tabela também mente, e a mentira é a parte interessante. Ela assume que
o erro é **absorvente**: uma vez errado, sempre errado. Agentes reais têm
**recuperação**. Se a probabilidade de detectar e corrigir um erro é *r*, o
processo vira uma cadeia de Markov com um estado "errado mas recuperável", e a
taxa de sucesso final passa a depender muito mais de *r* do que de *p*.

> **A consequência de engenharia é a mais importante do curso, e é
> contraintuitiva:** *aumentar r vale mais que aumentar p.* Um agente que erra
> mais mas percebe e conserta bate um agente mais preciso e cego. É por isso
> que a fase de **verificação** domina tudo, e por que "dê a ele um teste"
> supera "escolha um modelo melhor" com tanta frequência.

Corolário operacional: **fatiar a tarefa** substitui um *n* grande por vários
*n* pequenos com verificação entre eles. É a mesma matemática que justifica
integração contínua.

---

## 3. Atribuição de crédito

Quando uma trajetória de 40 passos falha, **qual passo foi o culpado?**

Esse é o *credit assignment problem*, e é difícil por três razões
independentes:

1. O erro pode ter sido no passo 3 e só se manifestar no 37.
2. Pode não haver passo errado: cada um localmente razoável, o conjunto
   inadequado (mínimo local).
3. O sinal de recompensa é **esparso** — um bit no fim de 40 ações.

Isso limita tanto o treinamento (RL em tarefas agênticas precisa de recompensa
densa ou de modelagem de recompensa) quanto a **depuração**. Quando você
diagnostica um agente que falhou, está resolvendo um problema de atribuição de
crédito na mão.

Mitigações reais: pontos de verificação intermediários (a recompensa fica
menos esparsa), asserções sobre a trajetória (não só sobre o resultado), e
registrar o `stop_reason` e o `usage` por volta.

---

## 4. Os limites de decidibilidade

### O problema da parada

Não existe algoritmo que decida, para todo programa e toda entrada, se ele
termina (Turing, 1936). Consequências diretas:

- Um agente não pode, em geral, decidir se um comando que ele vai rodar
  termina. Daí timeout — não como boa prática, mas como **necessidade
  teórica**.
- Um agente não pode decidir se **ele mesmo** vai terminar. Daí o limite de
  voltas.

### O teorema de Rice

Toda propriedade **não trivial e semântica** de programas é indecidível
(Rice, 1953). "Este código está correto?" é uma propriedade semântica não
trivial. Logo:

> **Não existe verificador geral de correção.** Nem por IA, nem por nada.

Isto não é uma limitação dos LLMs — é uma limitação da computação. O que
existe é verificação **parcial**: testes (verificam casos), tipos (verificam
uma classe de propriedades), provas (verificam o que você especificou),
análise estática (aproxima, com falsos positivos).

**Consequência para agentes:** todo sinal de verificação é parcial, e a
distância entre "passou no teste" e "está correto" é uma distância que nenhuma
quantidade de inteligência fecha. Ela só se estreita com mais especificação —
e especificação completa é o programa.

### Não computabilidade da complexidade de Kolmogorov

A complexidade de Kolmogorov (o menor programa que produz uma saída) é não
computável. Logo, "escreva a solução mais simples" não é decidível — só
aproximável por heurística. Não espere de um agente uma noção formal de
simplicidade; espere gosto estatístico.

---

## 5. Injeção de prompt como problema fundamental

Em arquitetura de computadores, a separação entre instrução e dado é
estrutural — bit de execução na página, arquitetura Harvard, W^X. Em LLMs,
**instrução e dado compartilham o mesmo canal**: texto.

Isso não é um bug de implementação. É a propriedade que torna o modelo útil:
ele obedece a instruções em linguagem natural, venham de onde vierem. Um
modelo que ignorasse instruções vindas do conteúdo lido também ignoraria as
instruções legítimas que chegam por documento, arquivo ou ferramenta.

Não há, hoje, um análogo ao escape de SQL — não existe forma sintática de
marcar "isto é dado" que seja robusta, porque o modelo processa semântica, e
não sintaxe. As mitigações existentes são todas **probabilísticas**
(treinamento contra injeção, classificadores) ou **arquiteturais** (menor
privilégio, isolamento, humano no laço).

> Por isso o [17](17-hooks-permissoes-seguranca.md) insiste: **limite o
> estrago, não a probabilidade.** A probabilidade não vai a zero enquanto a
> arquitetura for essa.

---

## 6. O gargalo do contexto

**Custo.** A atenção do Transformer é O(n²) em tempo e memória no comprimento
da sequência (a menos de variantes aproximadas). Contexto longo é caro por
construção.

**Qualidade.** O efeito *lost in the middle* (Liu et al., 2023): a
recuperação de informação posicionada no meio de contextos longos degrada
sensivelmente em relação ao início e ao fim. Aumentar a janela não aumenta
proporcionalmente o uso efetivo dela.

Combinados: existe um ponto além do qual acrescentar contexto piora, mesmo
cabendo na janela. É a fundamentação teórica de por que **curadoria de
contexto** — `/clear`, subagentes, `CLAUDE.md` enxuto — é engenharia e não
economia mesquinha.

---

## 7. Nenhum almoço grátis, e o que isso significa aqui

O teorema *No Free Lunch* (Wolpert & Macready, 1997): promediado sobre todos
os problemas possíveis, todos os algoritmos de otimização têm o mesmo
desempenho. Desempenho vem de **viés adequado ao domínio**, não de
generalidade.

Aplicado a agentes: um agente de propósito geral não pode ser melhor que um
especializado **em média sobre todos os domínios**. Ele ganha porque o
subconjunto de tarefas que interessa aos humanos é minúsculo e altamente
estruturado — e o pré-treino codifica exatamente esse viés.

Consequência prática: **o seu prompt de sistema, as suas ferramentas e o seu
`CLAUDE.md` são viés injetado**, e é daí que sai o desempenho no seu domínio.
Não é "ajuda"; é o mecanismo.

---

## 8. O que está em aberto

| Problema | Estado em ago/2026 |
|---|---|
| Injeção de prompt | **aberto.** Mitigação, não solução |
| Atribuição de crédito em trajetórias longas | aberto; recompensa esparsa continua difícil |
| Avaliação sem hackeamento de recompensa | aberto; auditorias derrubam resultados publicados |
| Contexto verdadeiramente longo com uso efetivo | parcial; janela cresceu mais que a utilização |
| Memória entre sessões, seletiva e confiável | parcial; hoje é arquivo + heurística |
| Composição multiagente com ganho comprovado | contestado; muitos sistemas são pipelines caros |
| Calibração ("eu não sei") | melhorou muito, longe de resolvido |
| Custo previsível | aberto; a variância entre execuções é grande |

---

## 9. Leitura de fundo

- Turing (1936) — indecidibilidade da parada
- Rice (1953) — propriedades semânticas de programas
- Kaelbling, Littman & Cassandra (1998) — POMDPs
- Wolpert & Macready (1997) — No Free Lunch
- Russell & Norvig — *AIMA*, cap. 2 (agentes) e 17 (decisão sob incerteza)
- Liu et al. (2023) — *Lost in the Middle*
- Yao et al. (2022) — ReAct
- Jimenez et al. (2023) — SWE-bench

Referências completas em [95-referencias.md](95-referencias.md).

---

## Autoteste

1. Formalize um agente de código como POMDP. O que é *Ω* e por que
   "parcialmente observável" é a palavra decisiva?
2. Com *p* = 0,99 por passo e 50 passos, qual a taxa de sucesso sem
   recuperação? Por que a realidade é melhor que isso?
3. Enuncie a regra sobre *r* e *p*, e diga que decisão de engenharia ela muda.
4. O que o teorema de Rice implica sobre "IA que verifica se o código está
   correto"?
5. Por que timeout é necessidade teórica e não boa prática?
6. Por que injeção de prompt não tem análogo ao escape de SQL?
7. Explique *lost in the middle* e o que ele implica sobre janelas gigantes.
8. Como o No Free Lunch se aplica ao seu `CLAUDE.md`?
9. Escolha um problema em aberto da §8 e descreva um experimento que produziria
   evidência sobre ele.
