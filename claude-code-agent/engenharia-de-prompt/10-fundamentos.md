# 10 · Fundamentos — por que um prompt funciona

**Nível:** intermediário · **Escrito em:** 19/08/2026

Você não precisa saber treinar um modelo. Precisa saber o suficiente da
mecânica para **prever o comportamento dele** e parar de se surpreender. Este
arquivo entrega esse mínimo — e vai fundo o bastante para que as recomendações
dos outros arquivos deixem de ser superstição.

---

## 10.1 · O que o modelo faz, na íntegra

> Um modelo de linguagem recebe uma sequência de símbolos e devolve uma
> distribuição de probabilidade sobre **qual é o próximo símbolo**. Depois
> sorteia um, acrescenta à sequência, e repete.

É isso. Não há mais nada. Todo o resto — parecer que raciocina, seguir
instrução, escrever código, recusar pedido — é comportamento **emergente**
dessa única operação repetida.

Duas consequências que você vai usar todo dia:

1. **Tudo é continuação.** O modelo não distingue ontologicamente "sua
   instrução" de "o documento" de "a resposta dele". Tudo é um texto só, e ele
   continua esse texto. A distinção entre instrução e dado é uma **convenção
   aprendida no treinamento** — forte, mas não uma barreira. É por isso que
   injeção de prompt existe e é difícil de eliminar
   ([35](35-seguranca-e-injecao.md)).
2. **Não há estado.** Cada chamada começa do zero. "Memória" de conversa é
   você reenviando o histórico inteiro toda vez. Se a conversa tem 30 turnos,
   você está pagando pelos 30 a cada mensagem nova.

---

## 10.2 · Token: a unidade que o modelo enxerga

O modelo não vê letras nem palavras. Vê **tokens** — pedaços de texto de
tamanho variável, definidos por um algoritmo de compressão sobre o corpus de
treinamento (tipicamente *Byte Pair Encoding*).

Regras de bolso, com aviso: **variam por modelo e por idioma.**

| Texto | Tokens aproximados |
|---|---|
| 1 palavra comum em inglês | ~1 |
| 1 palavra comum em português | ~1,3 a 2 |
| 100 caracteres de português | ~30 |
| 1 página A4 de texto | ~600 a 800 |
| `implementação` | 2 a 4 tokens |

**Por que o português custa mais que o inglês?** Porque o vocabulário de
tokens é construído por frequência no corpus de treinamento, e há muito mais
inglês nele. Palavras portuguesas comuns acabam quebradas em pedaços. Isso é um
custo real, medível, e explica por que às vezes vale escrever o prompt de
sistema em inglês e a saída em português. *(Opinião: em modelos de 2026 a
diferença de qualidade sumiu; a diferença de custo diminuiu mas não zerou.
Meça no seu caso — o número exato depende do tokenizador.)*

**Isto explica três comportamentos que parecem burrice:**

- **Não conta caracteres nem letras direito.** "Quantos 'r' em morango?" é
  difícil porque ele não vê `m-o-r-a-n-g-o`, vê talvez `mor|ango`. Correção:
  não peça contagem — verifique por programa ([06, exemplo 4](06-exemplos.md)).
- **Erra aritmética longa.** Números viram tokens arbitrários; não há
  circuito de soma. Correção: dê uma ferramenta de cálculo
  ([25](25-ferramentas-e-agentes.md)).
- **Erra ortografia invertida, anagrama, acrósticos.** Mesma causa.

Contagem exata: use o endpoint de contagem de tokens do fornecedor. Estimativa
por `len(texto)//4` serve para ordem de grandeza e nada mais.

---

## 10.3 · Atenção: por que a posição importa

Cada token gerado "olha" para todos os anteriores e decide **quanto peso** dar
a cada um. Esse mecanismo — atenção — é o coração da arquitetura *Transformer*
(2017) e a razão de várias recomendações práticas.

Três efeitos com nome, todos com consequência direta no seu prompt:

| Efeito | O que é | O que fazer |
|---|---|---|
| **Recência** | o que está perto do fim pesa mais na próxima previsão | ponha o dado a processar por último; repita a instrução crítica no fim |
| **Primazia** | o começo do contexto também é privilegiado (é onde vive o "quem eu sou") | papel, regras e formato ficam no topo |
| **Perdido no meio** (*lost in the middle*, Liu et al., 2023) | informação no miolo de um contexto longo é recuperada com menos confiabilidade | não empurre 200 páginas; **recupere o trecho relevante** ([15](15-contexto-e-rag.md)) |

> **Cuidado com a data.** O efeito "perdido no meio" foi medido em modelos de
> 2023 e está bem mais ameno nos modelos de 2026 com janelas de 1 milhão de
> tokens. Ele não desapareceu, e o custo de mandar 200 páginas continua real.
> A recomendação prática ("recupere em vez de despejar") continua valendo — por
> custo e latência, mesmo quando a qualidade aguenta.

---

## 10.4 · Aprendizado em contexto: por que exemplos funcionam

Quando você põe exemplos no prompt, **nada é treinado**. Os pesos do modelo não
mudam. O que acontece é o que se chama **aprendizado em contexto**
(*in-context learning*): os exemplos deslocam a distribuição de probabilidade
do que vem a seguir.

Intuição: o modelo viu, no treinamento, bilhões de trechos com a forma
"exemplo, exemplo, exemplo, próximo item no mesmo padrão". Ao encontrar essa
forma no seu prompt, a continuação mais provável é *seguir o padrão*. Você não
ensinou a tarefa — você **selecionou** o comportamento que já estava lá.

Isso explica achados que parecem paradoxais e que valem como aviso:

- Exemplos com **rótulos trocados** ainda ajudam (Min et al., 2022): boa parte
  do ganho vem da *forma* — que existe uma entrada, que existe uma saída, e
  qual é o formato dela — e não do conteúdo correto do rótulo. Não use isso
  como desculpa para rotular mal: o conteúdo correto ajuda **também**, e mais
  ainda nos modelos atuais.
- **Formatação consistente** entre exemplos e caso real importa tanto quanto os
  exemplos em si.
- Exemplo de **caso fácil** ensina pouco: o modelo já acertava. O ganho está na
  fronteira ([05 §5.5](05-manual-de-uso.md#55--ensinar-por-exemplo-few-shot)).

---

## 10.5 · Por que ele obedece instrução

Um modelo apenas pré-treinado **não obedece** — ele continua o texto. Se você
escrevesse "Traduza para o francês:", um modelo cru poderia continuar com mais
exercícios de tradução, em vez de traduzir.

A obediência vem de duas etapas posteriores de treinamento:

1. **Ajuste por instrução** (*instruction tuning*): treinar em pares
   (instrução, resposta boa). Ensina o formato "pedido → atendimento".
2. **Aprendizado por preferência** (RLHF e sucessores): humanos comparam
   respostas, um modelo de recompensa aprende a preferência, o modelo é
   ajustado para maximizá-la.

**Consequência direta e pouco confortável:** o modelo foi otimizado para
produzir respostas que *humanos avaliadores gostam*. Isso instala vieses
sistemáticos que você combate no prompt o tempo todo:

| Viés instalado no treinamento | Como se manifesta | Contramedida no prompt |
|---|---|---|
| bajulação (*sycophancy*) | concorda com você mesmo quando você está errado | "Discorde de mim se eu estiver errado"; não revele a resposta que você espera |
| prolixidade | resposta longa foi preferida por avaliadores | limite explícito e verificado |
| cordialidade | preâmbulos, "ótima pergunta!" | supressão explícita de preâmbulo |
| aversão a dizer "não sei" | inventa em vez de admitir lacuna | dar permissão explícita: "responda NÃO ENCONTRADO se não estiver no documento" |

> **A regra dos cinco porquês, aplicada.** Por que o modelo é prolixo? Porque
> foi ajustado por preferência humana. Por que a preferência humana premia
> prolixidade? Porque, em comparação lado a lado, avaliadores tendem a escolher
> a resposta mais completa e detalhada. Por que tendem? Porque comprimento
> correlaciona com esforço percebido, e avaliar profundidade dá trabalho.
> Por que isso não foi corrigido? Foi, parcialmente, com rubricas melhores e
> penalização de tamanho — mas é um **trade-off econômico**: rotulagem
> cuidadosa custa caro e escala mal. **Parada legítima: economia da anotação.**

---

## 10.6 · Amostragem: por que a resposta muda

Tendo a distribuição do próximo token, é preciso **escolher** um. Como escolher
é a amostragem:

| Estratégia | O que faz | Efeito |
|---|---|---|
| gulosa (*greedy*) | sempre o mais provável | repetitivo, travado em laços |
| **temperatura** | achata (>1) ou aguça (<1) a distribuição | mais criativo × mais previsível |
| **top-p** (núcleo) | sorteia só entre os candidatos que somam p de probabilidade | corta a cauda absurda |
| **top-k** | sorteia entre os k mais prováveis | idem, por contagem |

> **Aviso de 2026:** nos modelos Claude mais novos (Opus 5, Sonnet 5, família
> 4.6+), `temperature`, `top_p` e `top_k` **foram removidos** — mandá-los
> devolve erro 400. O controle passou a ser o nível de esforço (`effort`) e o
> pensamento adaptativo. Outros fornecedores mantêm os parâmetros clássicos.

**Mito importante:** "`temperature=0` dá determinismo". Não dá. Mesmo com
amostragem gulosa, a saída varia entre execuções por causa de não-associatividade
de ponto flutuante, de *batching* variável no servidor, de escolha de kernel na
GPU e de mistura de especialistas roteando diferente. **Você nunca teve
determinismo.** Consequência prática: um teste de prompt que exige igualdade
exata de string é um teste instável. Avalie por propriedade, ou repita e conte.
Ver [20-avaliacao-e-evals](20-avaliacao-e-evals.md).

---

## 10.7 · Janela de contexto

A **janela de contexto** é o total de tokens que cabem numa chamada: prompt de
sistema + histórico + documentos + ferramentas + resposta.

Modelos de 2026 chegam a 1 milhão de tokens (~2.500 páginas). Mas:

| O limite técnico | O limite prático |
|---|---|
| 1 M tokens | você paga por todos, toda chamada |
| a informação cabe | a atenção se dilui em contexto muito longo |
| o histórico inteiro cabe | latência sobe com o tamanho da entrada |
| — | conteúdo irrelevante **atrapalha**: é ruído competindo por atenção |

Daí a disciplina que hoje se chama **engenharia de contexto**: decidir o que
entra na janela é, em 2026, mais importante do que a redação da instrução. Ver
[15-contexto-e-rag](15-contexto-e-rag.md) e [65-estado-da-arte](65-estado-da-arte.md).

---

## 10.8 · Alucinação: a causa raiz

Alucinar não é falha do modelo. É **o funcionamento normal** aplicado a um caso
onde ele não tem base.

Aplicando os cinco porquês:

1. Por que ele inventa? Porque a operação dele é gerar a continuação mais
   provável — e continuação plausível é o objetivo, não veracidade.
2. Por que não diz "não sei"? Porque "não sei" quase nunca é a continuação mais
   provável de uma pergunta no corpus de treinamento; e porque a preferência
   humana penalizou respostas evasivas.
3. Por que ele soa confiante ao errar? Porque confiança é traço de **estilo**
   do texto gerado, independente da correção do conteúdo. A distribuição
   interna pode até estar incerta; o texto de saída não carrega isso.
4. Por que não dá para consertar por prompt? Dá para **reduzir** muito
   (fornecer a fonte, exigir citação, permitir "não encontrado"). Não dá para
   eliminar, porque não há, na arquitetura, um mecanismo que distinga "eu sei
   isto" de "isto é plausível".
5. Por que a arquitetura é assim? Porque o objetivo de treinamento é prever o
   próximo token, e essa função de perda não tem nenhum termo para veracidade.
   **Parada legítima: é uma propriedade matemática do objetivo de treinamento.**

Contramedidas, em ordem de eficácia medida:

1. **Dar a fonte no contexto** (RAG) e proibir uso de conhecimento externo.
2. **Exigir citação verificável** — e verificar por programa se o trecho citado
   existe mesmo no documento.
3. **Permitir explicitamente a lacuna**: "escreva NÃO ENCONTRADO".
4. **Verificar afirmações fora do modelo** (busca, banco, cálculo).
5. Segunda chamada de conferência — ajuda, e é o mais fraco dos cinco, porque
   o verificador tem os mesmos vieses do gerador.

---

## 10.9 · Um mapa mental que funciona

Pense no modelo como uma **superfície de probabilidade gigantesca** de todos os
textos possíveis. O prompt é o ponto de partida na superfície. Regiões dessa
superfície contêm texto competente, e outras contêm texto medíocre — as duas
foram aprendidas, porque a internet tem as duas.

Prompt engineering é **navegação**: escolher um ponto de partida cuja
vizinhança seja majoritariamente a região que você quer.

Isso explica de forma unificada:

- por que **papel** funciona: "você é o sistema de triagem da Acme" põe você na
  região dos textos técnicos operacionais, longe da região dos textos de blog;
- por que **exemplos** funcionam: eles estreitam a vizinhança;
- por que **formato** funciona: restringe as continuações admissíveis;
- por que **contexto irrelevante atrapalha**: arrasta o ponto de partida para
  uma vizinhança pior;
- por que **frases mágicas pararam de funcionar**: nos modelos atuais, o ajuste
  por instrução já coloca você na região boa; empurrar mais não move nada.

---

## Autoteste

1. Enuncie em uma frase a única operação que um modelo de linguagem realiza.
2. Por que o modelo erra "quantos 'r' em morango" e por que isso não é
   burrice?
3. O que é aprendizado em contexto — e por que exemplos com rótulo trocado
   ainda ajudam um pouco?
4. De onde vem a prolixidade do modelo? Desça pelo menos três "porquês".
5. `temperature=0` garante saída idêntica? Justifique e diga a consequência
   para seus testes.
6. Cite dois efeitos de posição e o que cada um implica na montagem do prompt.
7. Por que alucinação não pode ser eliminada por prompt? Qual é a parada
   legítima dessa cadeia de porquês?
8. Se a janela é de 1 milhão de tokens, por que ainda vale a pena recuperar
   só o trecho relevante? Dê três motivos.
