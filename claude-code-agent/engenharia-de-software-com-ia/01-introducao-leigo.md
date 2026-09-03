# 1 · O que é um dev que sabe usar IA — sem nenhum jargão

**Nível:** iniciante · **Escrito em:** 20/08/2026

---

## A pergunta que originou este curso

> *"O que é um dev que sabe usar IA?"*

A resposta curta, que o resto deste arquivo vai justificar:

> **É quem consegue verificar mais rápido do que a máquina consegue produzir.**

Repare no que essa frase **não** diz. Não diz "quem escreve prompts melhores".
Não diz "quem conhece mais ferramentas". Não diz "quem digita mais rápido".
Diz **verificar**. Guarde essa palavra; ela é o eixo de tudo aqui.

---

## Primeiro, o que é um "dev"

**Dev** é abreviação de *developer* — desenvolvedor de software. É a pessoa que
escreve as instruções que um computador executa. Essas instruções se chamam
**código**, e o conjunto de código de um sistema se chama **base de código**
(*codebase*).

O trabalho de um dev nunca foi só "digitar código". Sempre foi, em proporções
que variam:

| O que o dev faz | Fração do tempo (estimativa de ofício) |
|---|---|
| Entender o que precisa ser feito | 30% |
| Entender o código que já existe | 30% |
| Escrever código novo | 15% |
| Descobrir por que não funciona | 20% |
| Explicar para outras pessoas | 5% |

> **Opinião profissional, não consenso:** essas proporções são a minha leitura
> de décadas de observação, não um número medido. O ponto que importa é a ordem
> de grandeza: **escrever código sempre foi a menor fatia**. Quem acha que
> programar é digitar nunca programou por muito tempo.

---

## A analogia central: a serraria

Imagine uma marcenaria onde você fabrica móveis sob encomenda.

Durante 50 anos, o gargalo foi **cortar a madeira**. Serrar à mão é lento. Todo
mundo que quisesse produzir mais móveis investia em serrar melhor: serras mais
afiadas, técnicas melhores, aprendizes que serram.

Aí chega uma máquina que serra **200 vezes mais rápido que você**, 24 horas por
dia, e custa quase nada por corte.

Pergunta: você agora produz 200 vezes mais móveis?

**Não.** Porque agora o gargalo mudou de lugar. Ele foi para:

1. **Dizer à máquina o que cortar.** A máquina não sabe qual é o móvel. Ela
   corta exatamente o que você pediu — inclusive quando o que você pediu não é
   o que você quis dizer.
2. **Conferir o que ela cortou.** A máquina às vezes serra 3 centímetros fora
   e não avisa. O corte *parece* certo. Só na hora de montar você descobre.
3. **Montar, encaixar, acabar.** A máquina entrega peças, não móveis.
4. **Guardar o excesso.** Ela produz peças demais, e serragem demais, e agora
   a oficina está entulhada de coisas que ninguém pediu.

Um marceneiro que "sabe usar a máquina" **não é o que aperta o botão mais
vezes**. É o que:

- desenha a peça antes com medidas exatas (isso é **especificação**);
- construiu um **gabarito** que mede cada peça saindo da máquina, automaticamente
  (isso é **verificação**);
- sabe qual corte vale a pena mandar para a máquina e qual é mais rápido fazer
  à mão (isso é **julgamento**);
- mantém a oficina organizada para a máquina não se perder (isso é
  **arquitetura**).

Trocando os nomes, você tem o curso inteiro.

---

## O que a "máquina" é, em uma frase

A máquina, aqui, é um **modelo de linguagem** (*LLM*, de *Large Language
Model* — "modelo de linguagem grande").

> **Modelo de linguagem** é um programa que recebe um texto e chuta qual é o
> próximo pedaço de texto mais provável, repetidamente, até formar uma resposta.
> Ele foi treinado lendo uma quantidade absurda de texto — incluindo
> praticamente todo o código aberto do mundo.

Duas consequências que explicam quase tudo:

1. **Ele é ótimo naquilo que aparece muito no material que leu.** Um endpoint
   REST em Express, um teste em pytest, um `Dockerfile` para Node — isso ele
   faz melhor e mais rápido do que qualquer humano. Aparece milhões de vezes.
2. **Ele é péssimo — e perigosamente confiante — naquilo que é específico do
   seu sistema.** A regra de negócio que só a sua empresa tem, a gambiarra de
   2019 que ninguém pode mexer, a tabela cujo nome mente sobre o conteúdo. Ele
   nunca viu isso. Então ele **inventa algo plausível** e entrega com o mesmo
   tom de quem sabe.

O termo técnico para "inventar algo plausível" é **alucinação**
(*hallucination*). Não é bug: é o comportamento normal de um sistema que chuta
o próximo pedaço mais provável. Quando o provável coincide com o verdadeiro,
parece mágica. Quando não coincide, parece mágica também — e é aí que dói.

---

## O que mudou de verdade entre 2021 e 2026

Não foi "a IA ficou boa em programar". Foi mais específico que isso, e vale
enxergar em três degraus.

### Degrau 1 — Completar (2021–2023)

A IA sugeria o resto da linha enquanto você digitava. Você continuava dirigindo;
ela adivinhava o fim da frase. Ferramenta típica: GitHub Copilot na versão
original.

**O que exigiu do dev:** quase nada. Aceitar ou recusar sugestão.

### Degrau 2 — Conversar (2023–2024)

Você abria uma janela de chat, colava o código, descrevia o problema, recebia
uma resposta, e **copiava de volta na mão**. Ferramenta típica: ChatGPT.

**O que exigiu do dev:** saber descrever o problema e saber avaliar a resposta.
Aqui nasce a expressão *engenharia de prompt* — veja o curso
[engenharia-de-prompt](../engenharia-de-prompt/00-MAPA.md) desta mesma pasta.

### Degrau 3 — Agir (2024–2026)

A IA passou a **ter mãos**. Ela lê os seus arquivos, escreve neles, roda os
seus testes, lê o erro, corrige, roda de novo, faz um commit, abre um
*pull request*. Sozinha. Por horas.

> **Agente** é um modelo de linguagem preso num laço: *pensa → usa uma
> ferramenta → lê o resultado → pensa de novo*, até achar que terminou.
> As "ferramentas" são coisas banais: ler arquivo, escrever arquivo, rodar
> comando no terminal, buscar na web.

Ferramentas típicas: Claude Code, OpenAI Codex, Cursor, GitHub Copilot Agent,
Gemini CLI, Aider, Windsurf, Kiro.

**O que exigiu do dev:** tudo mudou. E é sobre isso que este curso trata.

---

## Por que o degrau 3 muda a natureza do trabalho

Nos degraus 1 e 2, você via cada linha antes de aceitá-la. A revisão era
gratuita porque estava embutida no ato de colar.

No degrau 3, a IA produz 400 linhas em oito minutos, em sete arquivos, e diz
"pronto, os testes passam".

Agora responda de verdade: **você leu as 400 linhas?**

Se leu, você gastou 40 minutos — e a IA não te economizou nada, só trocou
"escrever" por "ler", que é mais chato e menos confiável, porque ler código
que parece certo é o jeito mais eficiente de não enxergar o erro.

Se não leu, **você não sabe o que colocou no sistema**. E é aqui que mora todo
o desastre de 2025 e 2026: equipes que aumentaram a produção de código e
diminuíram o conhecimento sobre o próprio sistema.

### Isso não é teoria. Está medido.

| Medição | Número | Fonte |
|---|---|---|
| Devs experientes, tarefas reais, com IA vs. sem IA (início de 2025) | **19% mais lentos** com IA — enquanto *achavam* que estavam 20% mais rápidos | METR, jul/2025 |
| PRs assistidos por IA (percentil 75) | **2,6× maiores** (408 vs. 157 linhas) | LinearB, 2026 |
| Tempo de espera até alguém revisar um PR de agente | **5,3× maior** (1.055 vs. 201 minutos) | LinearB, 2026 |
| Código de IA que passa na revisão **sem modificação** | **32,7%** — contra 84,4% do código humano | LinearB, 2026 |
| Duplicação de blocos por milhão de linhas alteradas | 40,3 em 2023 → **73,0 em 2026** (+81%) | GitClear, 2026 |
| Código *movido* (sinal de refatoração) | 21% em 2022 → **3,8% em 2026** | GitClear, 2026 |
| Devs que usam IA | **84%** | Stack Overflow, pesquisa 2025 |
| Devs que **confiam** na saída da IA | **29%**, caindo 11 pontos em um ano | Stack Overflow, pesquisa 2025 |

Leia as duas últimas linhas juntas. **O uso subiu e a confiança caiu.** Isso não
é contradição: é exatamente o que acontece quando uma ferramenta é útil o
bastante para você não largar e errada o bastante para você não relaxar.

*(Todas as fontes com link estão em [95-referencias](95-referencias.md). O que
cada estudo mede e o que ele não mede está dissecado em
[24-produtividade-evidencia](24-produtividade-o-que-diz-a-evidencia.md) — porque
citar número sem entender a metodologia é o mesmo erro que estamos criticando.)*

---

## Então: o que é, afinal, um dev que sabe usar IA?

Vou dar a definição em camadas, da mais curta para a mais útil.

### Em uma frase

> Quem **converte julgamento humano em verificação automática** rápido o
> bastante para poder aceitar trabalho de máquina sem perder o controle do
> sistema.

### Em cinco comportamentos observáveis

Se você quiser identificar essa pessoa numa equipe — ou virar essa pessoa —
procure por isto:

1. **Ela escreve o critério antes do código.** Antes de pedir qualquer coisa,
   ela sabe dizer como vai saber se voltou certo. Frequentemente escreve o teste
   primeiro, e deixa a IA fazer o resto passar.
2. **Ela não confia; ela mede.** Nunca diz "a IA disse que funciona". Diz "rodei,
   passou, e o teste cobre o caso que me preocupava".
3. **Ela sabe o que *não* delegar.** Não manda para a IA aquilo que ela mesma
   não conseguiria avaliar. Essa é a regra de ouro, e está formulada de propósito
   no negativo.
4. **Ela prepara o terreno.** Investe em coisas chatas — testes rápidos, tipos,
   `lint`, `AGENTS.md`, comandos de build que funcionam de primeira — porque cada
   uma delas é um sensor que o agente usa para se corrigir sozinho.
5. **Ela mantém o modelo mental do sistema.** Consegue explicar, sem abrir o
   editor, como o sistema funciona. Se não consegue, ela sabe que perdeu o
   controle e para para recuperar.

### Em uma escala

Existe uma progressão real, e ela não é sobre ferramentas:

| Nível | Nome | O que a pessoa faz | O que a limita |
|---|---|---|---|
| **L0** | Recusa | Não usa, por princípio ou por medo | Fica para trás em tarefas repetitivas |
| **L1** | Autocompleta | Aceita sugestão de linha | Ganho pequeno, risco pequeno |
| **L2** | Conversa | Pergunta, cola, adapta | Ganho médio; erra em coisa específica do sistema |
| **L3** | **Delega com verificação** | Define escopo, delega, confere com teste | **Aqui começa o ganho real** |
| **L4** | Projeta o ambiente | Torna o repositório legível e verificável por máquina | Precisa de autonomia técnica |
| **L5** | Opera em escala | Coordena vários agentes, muda o processo do time | Precisa de mandato organizacional |

A maior parte do mercado, em agosto de 2026, está em **L2 se achando L4**. Esse
é o diagnóstico central deste curso, e o arquivo
[25-niveis-do-dev-com-ia](25-niveis-do-dev-com-ia.md) transforma esta tabela numa
rubrica com evidências concretas para você se autoavaliar honestamente.

---

## Três mal-entendidos que precisam morrer agora

### "Sabe usar IA = sabe fazer prompt"

Falso, e o mercado já corrigiu isso. Prompt é a parte mais fácil e a que
envelhece mais rápido: cada geração de modelo torna prompt elaborado menos
necessário. O que **não** envelhece é saber definir o problema e provar o
resultado.

Analogia: em 1995, "saber usar computador" significava decorar comandos do DOS.
Isso evaporou. O que sobreviveu foi saber organizar informação.

### "Vibe coding é o futuro do trabalho profissional"

**Vibe coding** é um termo cunhado por Andrej Karpathy em fevereiro de 2025 e
eleito palavra do ano pelo dicionário Collins em novembro de 2025. Descreve
programar conversando, aceitando tudo, sem ler o código — nas palavras dele,
"esquecer que o código existe".

É uma técnica **legítima e excelente** para: protótipo descartável, provar uma
ideia num sábado, script que roda uma vez, aprender uma biblioteca nova.

É **irresponsável** para: qualquer coisa que outra pessoa vai manter, que
processa dinheiro, que guarda dado de terceiro, ou que precisa funcionar daqui
a dois anos.

A distinção não é moral, é econômica: vibe coding troca **custo de escrita** por
**custo de manutenção**. Se o código morre amanhã, o troco é ótimo. Se ele vive
cinco anos, você acabou de contrair uma dívida com juros compostos.

### "IA vai substituir o dev"

A previsão que eu assino, e que é opinião, não fato: **não substitui o ofício;
destrói a fatia mais fácil dele.**

O que evapora é a tarefa média, bem definida, com muito exemplo público:
CRUD, boilerplate, conversão de formato, teste óbvio, ajuste de CSS. Isso já
está evaporando.

O que fica mais valioso, e não menos:

- **decidir o que construir** (quase todo desperdício em software é construir a
  coisa errada muito bem);
- **encarar sistema legado hostil** — a IA se perde exatamente onde não há
  exemplo público;
- **responder por consequência**: quando o sistema cai às 3h da manhã, ninguém
  aceita "o agente escreveu";
- **arquitetar para que o problema não volte**.

O efeito colateral cruel, e é preciso dizer: **a porta de entrada da profissão
ficou mais estreita**. O trabalho júnior clássico — a tarefa pequena e
supervisionada — é exatamente o que a IA faz melhor. O
[26-carreira-e-mercado](26-carreira-e-mercado.md) trata disso de frente, sem
consolo de LinkedIn.

---

## O paradoxo que você precisa carregar

Duas afirmações verdadeiras ao mesmo tempo:

> **1.** Quanto mais você sabe programar, mais a IA te acelera.
> **2.** Quanto mais a IA te acelera, menos você pratica programar.

A primeira é sobre capacidade de julgar: você só extrai valor de uma resposta
que você conseguiria ter avaliado. A segunda é sobre atrofia: julgamento é
músculo, e músculo que não trabalha encolhe.

Não existe solução limpa para isso. Existe disciplina: escolher deliberadamente
o que fazer à mão para não perder a capacidade de conferir o resto. Trato disso
em [75-armadilhas](75-armadilhas.md), na seção sobre *erosão de competência*.

---

## O que você vai aprender neste curso

Concretamente, ao terminar:

- Instalar e operar as ferramentas atuais (agosto de 2026), nos três sistemas
  operacionais, sem depender de nenhuma delas em particular.
- Escrever uma especificação que um agente consegue executar sem inventar.
- Montar o **portão de verificação** que decide se o que voltou entra ou não.
- Revisar código gerado por máquina — que exige um método diferente de revisar
  código humano, porque os erros ficam em lugares diferentes.
- Projetar repositório e arquitetura para serem legíveis por agente.
- Reconhecer e defender contra as ameaças novas: injeção indireta de prompt,
  pacote alucinado (*slopsquatting*), vazamento de segredo por agente.
- Ler a evidência sobre produtividade sem ser enganado por vendedor nem por
  cético.
- Saber quanto custa, em dólar e em real, e onde o custo escapa.

E, no meio do caminho, construir um projeto que **é** a lição:
[07-projeto-modelo](07-projeto-modelo/README.md) é um portão de verificação de
código gerado por IA, executável, com testes, que detecta pacote alucinado,
segredo vazado e critério de aceitação não coberto.

---

## Se você é leigo total em programação

Este arquivo você conseguiu ler. Os próximos exigem saber programar — não muito,
mas alguma coisa. O [02-pre-requisitos](02-pre-requisitos.md) diz exatamente o
que, quanto tempo leva, e o que fazer se faltar.

Uma advertência honesta, contra a propaganda: **não, a IA não te dispensa de
aprender a programar.** Ela te dispensa de *digitar*. São coisas diferentes.
Quem tenta pular a etapa de entender chega a um sistema de 5.000 linhas que
funciona, que ninguém entende, e que na primeira mudança inesperada vira um
muro. Já vi isso acontecer dezenas de vezes; agora acontece em semanas em vez de
anos.

---

## Autoteste

1. Por que "sabe usar IA" **não** é o mesmo que "sabe escrever prompt"?
2. A serraria ganhou uma máquina 200× mais rápida. Onde foi parar o gargalo, e
   qual é o equivalente disso em software?
3. Um agente entregou 400 linhas em 8 minutos, com testes passando. Quais são as
   duas saídas ruins possíveis, e por que ambas são ruins?
4. O estudo da METR mediu devs 19% mais lentos com IA, mas eles se achavam 20%
   mais rápidos. Qual é a lição prática dessa diferença — independentemente de o
   número ainda valer hoje?
5. Em que situação o *vibe coding* é a escolha profissional **certa**? Em que
   situação é irresponsável? Qual é o critério que separa as duas?
6. Enuncie a regra de ouro da delegação, na forma negativa.
7. Explique o paradoxo entre "quanto mais você sabe, mais a IA acelera" e
   "quanto mais a IA acelera, menos você pratica". Por que não há solução limpa?
8. O uso de IA subiu para 84% e a confiança caiu para 29%. Por que isso não é
   uma contradição?

---

**Próximo:** [02-pre-requisitos](02-pre-requisitos.md) — o que você precisa saber
antes, quanto tempo leva de verdade, e a rota de resgate se faltar algo.
