# 60 · Teoria avançada — o que se sabe, o que se supõe, e os limites

**Nível:** pesquisa · **Escrito em:** 19/08/2026

Aqui o material deixa de ser receita. Cada seção marca explicitamente o que é
**resultado estabelecido**, o que é **hipótese com evidência** e o que é
**opinião**. Se você vai defender uma escolha técnica numa reunião com pessoas
que leem paper, é este arquivo que sustenta.

---

## 60.1 · Por que o aprendizado em contexto funciona

**O fenômeno (estabelecido):** com exemplos no prompt, o desempenho melhora sem
qualquer atualização de pesos. Reprodutível em todas as famílias de modelo.

**O mecanismo (em disputa).** Três explicações principais, não excludentes:

### (a) Inferência bayesiana implícita

Proposta por Xie et al. (2021). O pré-treinamento produziria um modelo de
mistura sobre "tarefas latentes"; os exemplos do prompt funcionam como
evidência que faz a posteriori se concentrar na tarefa certa. O prompt não
ensina — **seleciona**.

Explica bem: por que exemplos com rótulo trocado ainda ajudam (a *forma* já
identifica a tarefa); por que poucos exemplos bastam; por que a formatação
importa tanto quanto o conteúdo.

### (b) Cabeças de indução

Olsson et al. (2022, Anthropic, *In-context Learning and Induction Heads*).
Identificaram circuitos concretos em transformers que implementam a regra
"achou `A B` antes? então, depois de `A`, preveja `B`". A formação dessas
cabeças coincide com um salto abrupto na capacidade de aprender em contexto.

**Status:** é a evidência mecanicista mais forte que existe — circuitos
observados, não inferidos. Explica cópia e padrão; explica menos bem tarefas
semânticas complexas. Linha ativa até 2026, com trabalhos recentes descrevendo
a estrutura das matrizes de peso que implementam essas cabeças.

### (c) Descida de gradiente implícita

von Oswald et al. (2023) e sucessores: em cenários controlados, a passagem
direta de um transformer com atenção linear **reproduz** passos de descida de
gradiente sobre os exemplos do contexto — o modelo estaria "treinando" um
modelo pequeno dentro da ativação.

**Status:** demonstrado em modelos de brinquedo e regressão linear. **Não
demonstrado** em modelos de linguagem de escala real. Trate como analogia
promissora, não como explicação do que acontece no Claude ou no GPT.

> **Opinião profissional:** as três descrevem partes do mesmo elefante. Para o
> trabalho prático, a (a) é a mais útil como modelo mental — pense em
> *selecionar uma tarefa latente*, não em *ensinar*. Isso muda o que você
> escreve: você passa a se perguntar "qual sinal identifica inequivocamente
> esta tarefa?" em vez de "como explico melhor?".

---

## 60.2 · Por que cadeia de pensamento aumenta a capacidade — de verdade

Este é o resultado mais bonito da área, porque é **teoria da computação**, não
psicologia.

**Estabelecido:** um transformer de profundidade fixa e precisão logarítmica,
gerando **um único token**, tem poder computacional limitado — pertence a uma
classe de circuitos de profundidade constante (essencialmente `TC⁰`). Existem
problemas — inclusive alguns bem simples, como avaliar certas composições
sequenciais — que **provadamente** não estão nessa classe.

**Estabelecido:** ao gerar tokens intermediários e realimentá-los, o modelo
ganha **computação serial**. Cada token gerado é um passo a mais de
processamento. Com número suficiente de passos intermediários, transformers com
cadeia de pensamento simulam classes bem maiores — até computação de tempo
polinomial (Merrill & Sabharwal, e trabalhos correlatos, 2023–2026).

**A consequência prática, e ela é forte:**

> Escrever passos intermediários **não** é um truque psicológico para o modelo
> "se concentrar". É a única forma de ele executar mais computação por resposta.
> A cadeia de pensamento **aumenta a classe de problemas solucionáveis**.

E daí decorre por que os modelos de 2025–2026 vieram com pensamento estendido
nativo: se o ganho é de computação serial, o lugar certo dele é dentro do
modelo, com orçamento controlado, e não implorado por prompt.

**O que isso não diz:** que a cadeia escrita seja o raciocínio verdadeiro. A
computação acontece; a *narrativa* que o modelo produz sobre ela pode não
corresponder ao que determinou a resposta. Os dois fatos convivem — e é por isso
que a explicação do modelo é pista, não auditoria.

---

## 60.3 · Fragilidade a formato: o resultado que mais incomoda

**Estabelecido, e reproduzido várias vezes:** mudanças **semanticamente
irrelevantes** no prompt — separador (`:` contra ` - `), presença de espaço,
ordem dos exemplos, capitalização — produzem variações grandes de desempenho.
Sclar et al. (2023) mediram, em tarefas de classificação, faixas de dezenas de
pontos percentuais entre formatações equivalentes do **mesmo** prompt. Lu et al.
(2021) já haviam mostrado que a ordem dos exemplos altera o resultado de
próximo do estado da arte a próximo do acaso.

Consequências que quase ninguém tira, e deveria:

1. **Comparar dois prompts em uma formatação só é comparação enviesada.** O
   rigoroso é amostrar formatações e reportar média e dispersão.
2. **"O prompt A é melhor que o B"** frequentemente significa "o A caiu numa
   formatação de sorte".
3. **Isto é um argumento a favor da otimização automática**
   ([45](45-otimizacao-automatica.md)): a máquina explora esse espaço; você não.
4. Modelos maiores e mais recentes são **menos** sensíveis — o efeito diminuiu,
   mas há evidência de que **não desapareceu**.

---

## 60.4 · Calibração

**Estabelecido:** a confiança que o modelo **declara em texto** ("estou 90%
seguro") é mal calibrada — correlaciona com o acerto, mas longe do ideal, e
costuma ser sistematicamente otimista.

**Estabelecido:** a probabilidade interna do token (quando o fornecedor a
expõe) é bem mais calibrada que a confiança verbalizada — e o ajuste por
preferência humana **piora** a calibração do modelo base, um resultado
documentado desde o relatório técnico do GPT-4 (2023).

**Consequências:**

- Usar confiança declarada como limiar de automação de alto risco é
  imprudente sem calibração empírica.
- **Calibração empírica é fácil e quase ninguém faz:** agrupe as respostas por
  faixa de confiança declarada e meça o acerto real de cada faixa. Se a faixa
  "0,9" acerta 70%, você já sabe o fator de correção — e passa a ter um limiar
  defensável.

---

## 60.5 · Otimização de prompt como problema formal

**O problema.** Encontrar `p*` que maximize `E[m(f(p, x), y)]` sobre a
distribuição real de entradas, onde `f` é o modelo, `m` a métrica, `p` o prompt.

**As dificuldades, todas estabelecidas:**

| Dificuldade | Consequência |
|---|---|
| espaço discreto, combinatório, sem gradiente acessível | não dá para derivar; busca é a única saída |
| `f` é caixa-preta e muda sem aviso (o fornecedor atualiza) | `p*` de ontem pode não ser o de hoje |
| `m` é ruidosa (amostragem, tamanho de amostra) | otimizar ruído é fácil e sedutor |
| a distribuição real desloca com o tempo | superajuste ao conjunto é o modo de falha padrão |

**As abordagens, por família:**

| Família | Ideia | Precisa de |
|---|---|---|
| gradiente sobre tokens (AutoPrompt, 2020) | busca discreta guiada por gradiente | acesso aos pesos |
| prompts contínuos (*prompt tuning*, 2021) | otimizar vetores, não texto | acesso ao modelo |
| busca com modelo no laço (MIPROv2, GEPA) | propor variações e testar | só a API |
| gradientes textuais (TextGrad) | crítica em linguagem natural como "derivada" | só a API |

**Resultado relevante de 2026:** o GEPA (ICLR 2026, *oral*) mostra que reflexão
em linguagem natural + fronteira de Pareto supera aprendizado por reforço em
várias tarefas com **até 35× menos execuções**. A leitura teórica: **feedback em
linguagem natural carrega muito mais informação por execução do que um escalar
de recompensa.** Um número diz "foi ruim"; uma frase diz "foi ruim porque
confundiu cobrança com bug quando apareceu a palavra erro".

---

## 60.6 · Limites duros

Coisas que **nenhum prompt** resolve. Saber isto evita meses de trabalho
perdido:

1. **Capacidade do modelo.** Prompt seleciona comportamento existente; não cria
   capacidade ausente. Se o modelo não sabe a área, nenhuma redação faz nascer
   o conhecimento.
2. **Conhecimento fora do corte de treinamento.** Só entra por contexto ou
   ferramenta.
3. **Computação por token.** Sem passos intermediários, há problemas fora do
   alcance (§60.2). O limite é matemático.
4. **Aritmética exata e contagem em escala.** Use ferramenta.
5. **Determinismo.** Não existe ([10 §10.6](10-fundamentos.md)).
6. **Separação instrução/dado.** Não existe garantia arquitetural
   ([35](35-seguranca-e-injecao.md)).
7. **Verificação de verdade.** O modelo não tem acesso ao mundo. Verificar é
   função de sistema externo.
8. **Limite estatístico da sua avaliação.** Com n casos, há um piso de
   incerteza. Você não pode afirmar 1 ponto percentual com 50 casos, por mais
   bem escrito que esteja o relatório.

---

## 60.7 · Problemas em aberto (agosto de 2026)

1. **Por que o aprendizado em contexto funciona em escala real?** As três
   explicações do §60.1 não se unificaram.
2. **Como medir "qualidade" sem humano no laço?** Todo juiz automático herda o
   viés do modelo que julga. Circularidade não resolvida.
3. **Defesa com garantia contra injeção indireta.** Não existe. É, na minha
   opinião, o problema aberto mais urgente da área aplicada.
4. **Transferência de prompt entre modelos.** Prompt otimizado para um modelo
   costuma degradar em outro. Não há teoria de por quê nem de como corrigir.
5. **Interpretabilidade do prompt otimizado.** Máquinas produzem prompts que
   funcionam e ninguém explica. Em domínio regulado, isso é bloqueante.
6. **Avaliação de agentes de horizonte longo.** Como pontuar uma trajetória de
   200 passos em que o resultado final é parcialmente certo?

---

## Autoteste

1. Descreva as três explicações do aprendizado em contexto e o status de
   evidência de cada uma.
2. Por que a cadeia de pensamento aumenta a **classe de problemas** solucionáveis?
   Qual é o argumento formal?
3. Por que isso não implica que a cadeia escrita seja o raciocínio real?
4. O que a fragilidade a formato implica para a forma como você compara dois
   prompts?
5. Por que a confiança verbalizada é mal calibrada, e como se corrige na
   prática?
6. Por que feedback textual supera recompensa escalar em otimização de prompt?
7. Liste quatro limites que nenhum prompt resolve.

---

### Referências

- Vaswani et al., *Attention Is All You Need*, 2017 — arXiv:1706.03762
- Brown et al., *Language Models are Few-Shot Learners*, 2020 — arXiv:2005.14165
- Shin et al., *AutoPrompt*, 2020
- Lu et al., *Fantastically Ordered Prompts and Where to Find Them*, 2021
- Xie et al., *An Explanation of In-context Learning as Implicit Bayesian Inference*, 2021
- Olsson et al., *In-context Learning and Induction Heads*, Anthropic / Transformer Circuits, 2022
- Wei et al., *Chain-of-Thought Prompting*, 2022 — arXiv:2201.11903
- Min et al., *Rethinking the Role of Demonstrations*, 2022
- von Oswald et al., *Transformers Learn In-Context by Gradient Descent*, 2023
- Merrill & Sabharwal, *The Expressive Power of Transformers with Chain of Thought*, 2023–2024
- Sclar et al., *Quantifying Language Models' Sensitivity to Spurious Features in Prompt Design*, 2023
- Liu et al., *Lost in the Middle*, 2023 — arXiv:2307.03172
- Khattab et al., *DSPy*, 2023 — arXiv:2310.03714
- Agrawal et al., *GEPA: Reflective Prompt Evolution Can Outperform Reinforcement Learning*, arXiv:2507.19457 — ICLR 2026 (oral)

**Nota de honestidade:** os identificadores arXiv acima só aparecem onde foram
conferidos. Para os demais, procure por autor e título — não copie número de
referência que ninguém verificou, inclusive de mim.
