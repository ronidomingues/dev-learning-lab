# 75 · Armadilhas, erros clássicos e mitos

**Nível:** todos · **Escrito em:** 19/08/2026

Vinte e cinco armadilhas e doze mitos. Cada uma com **o que é**, **por que
persiste** e **o que fazer**. As mais caras estão marcadas com 💸.

---

## Parte 1 · Armadilhas de método

### 1. 💸 Testar com um caso e generalizar

Você ajusta, o caso passa, você conclui que resolveu. **Persiste** porque o
retorno é imediato e agradável, e montar conjunto é tedioso. **Faça:** 20 casos
antes de qualquer conclusão.

### 2. 💸 Mudar várias coisas de uma vez

Ganho de 6 pontos, e você não sabe qual das quatro alterações produziu. Quando o
custo apertar, não saberá o que remover. **Faça:** uma mudança, uma medição.

### 3. Comemorar diferença dentro do ruído

15/20 contra 17/20 não é melhora demonstrada
([20 §20.4](20-avaliacao-e-evals.md)). **Persiste** porque porcentagem parece
precisa. **Faça:** intervalo de confiança, comparação pareada.

### 4. 💸 Superajustar ao conjunto de teste

Você olhou o mesmo conjunto 200 vezes; o prompt agora resolve **aquele**
conjunto. **Faça:** conjunto de validação separado, tocado raramente.

### 5. Conjunto de avaliação enviesado

Só casos que alguém achou interessantes. Métrica linda, produção ruim.
**Faça:** amostra aleatória do tráfego real.

### 6. 💸 Não olhar as saídas erradas, uma a uma

A métrica diz *quanto*; só o erro diz *por quê*. **Persiste** porque ler 20
saídas ruins é chato. **Faça:** uma hora por semana lendo erros. É a hora mais
produtiva da semana.

### 7. Olhar só a média

92% no geral e 40% no segmento que mais paga. **Faça:** fatie por segmento
sempre.

### 8. Testar sem repetição

O modelo é probabilístico. Rodou uma vez e deu certo não é resultado.
**Faça:** repita os casos críticos; conte a divergência.

---

## Parte 2 · Armadilhas de escrita

### 9. Instrução negativa

"Não seja prolixo" funciona pior que "no máximo 3 frases"
([12 §12.4](12-anatomia-de-um-prompt.md)). **Faça:** positiva e verificável.

### 10. Instrução enterrada em texto longo

40 páginas coladas e a pergunta no fim, sem separador. **Faça:** delimite; ponha
a instrução fora do bloco e repita-a no fim.

### 11. Conjunto de rótulos aberto

Pedir "classifique" sem listar as classes garante rótulo inventado.
**Faça:** conjunto fechado, com definição de cada item, e um `outro`.

### 12. Categoria sem definição

Listar `cobranca, bug, acesso` sem dizer o que cada uma abrange. Óbvio para
você; palavra solta para o modelo. **Faça:** uma linha de definição por
categoria.

### 13. Não tratar o caso vazio

Sem "use null quando não houver", o modelo preenche com algo plausível — e
plausível parece verdadeiro. **Faça:** diga o que fazer na ausência.

### 14. Prompt que cresce por acumulação

Cada incidente vira mais um parágrafo; ninguém remove nada. Dois anos depois,
3.000 tokens, dos quais 1.000 são inúteis. **Faça:** ablação periódica
([Lab 4](70-pratica.md)).

### 15. Regras contraditórias

"Seja conciso" e "explique detalhadamente cada decisão". O modelo escolhe uma,
aparentemente ao acaso, e você culpa o modelo. **Faça:** leia suas regras
procurando conflito antes de acusar.

### 16. Exemplos desbalanceados

8 de 10 exemplos da categoria A ensinam viés para A. **Faça:** balanceie, ou
desbalanceie sabendo.

---

## Parte 3 · Armadilhas de engenharia

### 17. 💸 Confiar no formato sem validar

Funcionou três vezes, você tirou o `try`. Quebra em produção, à noite.
**Faça:** validação sempre; falha tratada sempre.

### 18. 💸 `max_tokens` baixo demais

Trunca a saída no meio. Falha intermitente, só nos casos longos, invisível em
teste com entrada curta. **Faça:** dimensione com folga e **verifique o motivo
de parada** da resposta.

### 19. 💸 Cache invalidado sem ninguém notar

Carimbo de data no topo do prompt de sistema; a conta é 10× a esperada e não há
sintoma visível. **Faça:** monitore os tokens lidos do cache.

### 20. 💸 Histórico crescendo sem limite

Custo cresce com o quadrado do tamanho da conversa. **Faça:** janela,
compactação ou memória externa.

### 21. 💸 Agente sem limite de passos

Uma tarefa de US$ 0,02 vira US$ 12 numa execução patológica. **Faça:** política
de parada e teto de passos.

### 22. Executar saída de modelo sem sandbox

SQL, shell, HTML gerados e executados direto. **Faça:** validar, escapar,
isolar, permissão mínima.

### 23. Dado de terceiro no prompt de sistema

Erro estrutural. **Faça:** instrução em `system`, dado em `user`, delimitado.

### 24. Segredo no prompt de sistema

Assuma que vaza. Já vazou de praticamente todo produto grande.
**Faça:** segredo fica no servidor, nunca no contexto.

### 25. Não versionar o prompt

"Estava melhor semana passada" e ninguém sabe o que mudou. **Faça:** arquivo no
git, um commit por mudança, métrica na mensagem.

---

## Parte 4 · Mitos

| # | Mito | Realidade |
|---|---|---|
| 1 | "Existe o prompt perfeito" | prompt é específico de modelo, tarefa, dado e métrica. O ativo é o conjunto de avaliação, não o texto |
| 2 | "Frases mágicas melhoram a resposta" | "respire fundo", gorjeta, ameaça: mensurável em 2023, ruído em 2026 |
| 3 | "Papel de especialista mundial ajuda" | papel **funcional** ajuda; papel inflacionário não, e puxa estilo pomposo |
| 4 | "Pense passo a passo é sempre bom" | superado por pensamento nativo; pode conflitar com o processo interno do modelo |
| 5 | "`temperature=0` dá determinismo" | não dá, e nunca deu ([10 §10.6](10-fundamentos.md)) |
| 6 | "Mais exemplos, melhor" | retorno decrescente e custo linear; 5 bem escolhidos batem 20 ao acaso |
| 7 | "Prompt bom é longo" | prompt bom é **específico**. Comprimento é efeito colateral, não meta |
| 8 | "O modelo entende o que eu quis dizer" | ele continua o texto mais provável. Ambiguidade sua vira erro dele |
| 9 | "Se eu pedir para não alucinar, ele não alucina" | reduz um pouco; a causa é estrutural ([10 §10.8](10-fundamentos.md)) |
| 10 | "Prompt de sistema é secreto" | é extraível; projete supondo que já vazou |
| 11 | "Injeção de prompt se resolve com uma boa instrução" | não se resolve por prompt; contenha na arquitetura |
| 12 | "Prompt engineering acabou" | o **título** está sumindo; a habilidade triplicou em exigência ([40](40-a-profissao.md)) |

---

## Parte 5 · Más práticas que persistem — e por quê

Vale entender o mecanismo social, porque ele explica por que os mitos não
morrem:

| Má prática | Por que persiste |
|---|---|
| coleções de "prompts prontos" | vendem bem; o comprador não tem como medir se funcionam |
| tutoriais com truques de 2023 | conteúdo antigo tem mais tráfego acumulado e continua ranqueando |
| "eu testei e ficou melhor" | testar direito exige conjunto rotulado; ninguém quer o trabalho |
| certificados sem projeto | dão sensação de progresso mensurável sem exigir medição real |
| copiar prompt de outro produto | parece atalho; o prompt reflete os dados e a métrica **daquele** produto, que você não tem |
| culpar o modelo | é mais confortável que revisar a própria especificação |

> **Um teste rápido de honestidade intelectual, para aplicar em qualquer
> conteúdo da área — inclusive neste curso:** o autor mostra **números**, com
> **quantos casos** foram medidos e **em qual modelo e data**? Se não mostra, é
> opinião. Opinião pode ser boa; só não é evidência.

---

## Autoteste

1. Por que "testar com um caso" é a armadilha mais comum, e o que a sustenta?
2. Cite as três armadilhas que aparecem direto na fatura.
3. Por que prompt que cresce por acumulação é um problema, e como se resolve?
4. Um colega diz que `temperature=0` deixa a saída determinística. Responda.
5. Por que "prompt engineering acabou" é meio verdade e meio mito?
6. Qual é o teste de honestidade intelectual para avaliar conteúdo da área?
