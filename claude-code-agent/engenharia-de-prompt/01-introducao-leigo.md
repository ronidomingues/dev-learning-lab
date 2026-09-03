# 1 · O que é um Engenheiro de Prompt — explicado sem nenhum jargão

**Nível:** iniciante · **Escrito em:** 19/08/2026

---

## A analogia: o estagiário genial e amnésico

Imagine que você contratou um estagiário com estas características:

- Leu praticamente tudo que já foi escrito na internet. Sabe de medicina,
  direito romano, contabilidade, Python e culinária tailandesa.
- Trabalha 24 horas por dia, responde em três segundos e custa centavos.
- **Esquece tudo entre uma tarefa e outra.** Nada do que você falou ontem
  existe hoje.
- Nunca diz "não sei". Se não souber, **inventa** com a mesma confiança.
- Não pergunta nada. Se o pedido está ambíguo, ele escolhe uma interpretação
  em silêncio e segue.
- Faz *exatamente* o que você escreveu — inclusive quando o que você escreveu
  não é o que você quis dizer.

Agora responda: com um estagiário desses, **onde está o trabalho difícil?**

Não está em "saber a resposta" — ele já sabe. Está em **formular o pedido**:
dizer quem ele é nessa tarefa, o que exatamente você quer, em que formato,
com quais exemplos, com que material de apoio, e como você vai **conferir** se
o que voltou está certo antes de mandar para o cliente.

Isso é engenharia de prompt.

> **Prompt** (pronuncia-se "prómpt") é a palavra em inglês para *comando* ou
> *instrução*. É tudo aquilo que você entrega ao modelo de IA antes de ele
> responder: seu texto, os exemplos, os documentos anexados, as regras.

---

## A definição, em uma frase

> **Engenheiro de prompt é quem transforma uma tarefa vaga de linguagem
> natural em um sistema que produz o resultado certo de forma repetível,
> verificável e barata — usando um modelo de IA como peça.**

Repare nas quatro palavras que fazem o trabalho na frase: **repetível**,
**verificável**, **barata** e **sistema**.

- **Repetível.** Um prompt que funcionou uma vez não vale nada. O modelo é
  probabilístico: a mesma pergunta pode gerar respostas diferentes. Se em 100
  chamados ele acerta 97, isso é um resultado. Se você testou uma vez e gostou,
  isso é uma anedota.
- **Verificável.** Você precisa saber *quanto* ele acerta. Isso exige um
  conjunto de casos com a resposta certa anotada à mão e um programa que conta
  os acertos. Sem isso, você não está fazendo engenharia — está fazendo
  arte conceitual.
- **Barata.** Cada palavra que você manda ao modelo é cobrada. Um prompt com
  20 exemplos pode acertar 2% a mais e custar 4× mais. Às vezes vale; às vezes
  não. Decidir isso com número na mão faz parte do cargo.
- **Sistema.** Quase nunca é um prompt só. É um prompt que chama uma busca,
  que alimenta um segundo prompt, cuja saída passa por um validador, que
  aciona uma nova tentativa quando falha, tudo com registro do que aconteceu.

---

## O que NÃO é engenharia de prompt

Isto importa mais do que a definição, porque a palavra foi sequestrada.

| Não é | Por quê |
|---|---|
| **Decorar frases mágicas** ("aja como um especialista", "respire fundo") | funcionaram em modelos de 2023; em modelos de 2026 vão de inúteis a prejudiciais. Ver [75-armadilhas](75-armadilhas.md). |
| **Comprar/vender "1000 prompts prontos"** | prompt fora do contexto do seu problema, dos seus dados e da sua métrica não tem valor |
| **Ser "bom de conversar com o ChatGPT"** | é uso, e é ótimo saber — mas é o equivalente a "sei usar o Excel" em relação a "sou analista de dados" |
| **Um cargo isolado que só escreve texto** | ver [40-a-profissao](40-a-profissao.md): o cargo real inclui código, avaliação, custo e segurança |

E, com igual honestidade, também **não** é verdade que a profissão morreu.
O que morreu foi a versão de 2023 dela — a pessoa que só escrevia frases. Ver
[o mercado com números](40-a-profissao.md).

---

## Um exemplo concreto, do ruim ao bom

Tarefa real: sua empresa recebe 400 chamados de suporte por dia e precisa
mandá-los para a fila certa.

**Tentativa 1 — como quase todo mundo começa:**

```
Classifique este chamado de suporte: "Deu erro na hora de pagar e o valor
foi debitado do cartão mesmo assim."
```

O modelo responde:

```
Claro! Este chamado parece se tratar de um problema técnico relacionado ao
processamento de pagamentos. Sugiro classificá-lo como "Erro de Sistema —
Financeiro". Posso ajudar em algo mais?
```

Três problemas, e nenhum deles é "o modelo é burro":

1. A categoria não existe no seu sistema. Você tem quatro filas, e
   "Erro de Sistema — Financeiro" não é uma delas. **Você nunca disse quais
   eram.**
2. A resposta veio embrulhada em conversa. Seu programa esperava um dado,
   recebeu um bate-papo. **Você nunca disse o formato.**
3. Ele classificou pela palavra "erro". O assunto real é uma cobrança
   indevida. **Você nunca disse como decidir em caso de ambiguidade.**

**Tentativa 2 — o mesmo modelo, o mesmo dia, prompt diferente:**

```
Você é o sistema de triagem de chamados da Acme Cloud.

<categorias>
- cobranca : fatura, boleto, cartão, estorno, valor cobrado, plano
- bug      : o produto não faz o que promete
- acesso   : login, senha, 2FA, conta bloqueada
- duvida   : pedido de orientação
</categorias>

<regras>
1. Escolha exatamente UMA categoria, apenas dentre as quatro acima.
2. Classifique pelo ASSUNTO, não pelas palavras que aparecem. Uma cobrança
   indevida é `cobranca` mesmo que o cliente escreva "erro".
</regras>

Responda com apenas o JSON, sem texto antes ou depois:
{"categoria": "...", "urgencia": "alta|normal", "resumo": "..."}
```

Resposta:

```json
{"categoria": "cobranca", "urgencia": "normal", "resumo": "Cobranca indevida apos falha no pagamento"}
```

Agora seu programa consegue usar isso. **Nada mudou no modelo. Mudou o pedido.**

E aqui vem a parte que separa o profissional do entusiasta: como você sabe que
a tentativa 2 é melhor? Você *acha*. Para *saber*, é preciso pegar 22 chamados
reais, anotar à mão a resposta certa de cada um, rodar as duas versões e contar.
É exatamente isso que o [projeto-modelo](07-projeto-modelo/README.md) deste
curso faz — e o resultado medido foi 0% contra 82%.

---

## Por que isso é preciso existir?

Porque um modelo de linguagem **não sabe qual é o seu problema**.

Ele foi treinado a prever a continuação mais provável de um texto, a partir de
tudo que se escreveu na internet. Ele é, literalmente, uma média gigantesca de
como as pessoas escrevem. Quando você pergunta algo vago, ele responde a
*média* das respostas para aquela vaguidão — que é quase sempre genérica,
prolixa e formatada para humano ler, não para programa consumir.

O prompt é o mecanismo pelo qual você **restringe** essa média até que o que
sobra seja o que você queria. Não é magia, é redução de espaço de busca.
[Por que isso funciona, mecanicamente](10-fundamentos.md).

---

## Um dia na vida (versão realista, 2026)

Nada de "escrevi um prompt genial de manhã". O dia de verdade:

- **09:00** — Um relatório aponta que a triagem começou a mandar chamados de
  cobrança para a fila de bugs. Você olha os 15 casos errados.
- **09:40** — Descobre que o padrão de escrita dos chamados mudou: o novo
  formulário do site prefixa tudo com "Erro relatado pelo usuário:". Seu prompt
  não previa isso.
- **10:30** — Escreve a correção, roda a suíte de avaliação nos 300 casos
  rotulados. Acerto sobe de 91% para 96%, mas dois casos que funcionavam
  quebraram. Investiga.
- **13:00** — Reunião: o financeiro quer cortar 30% do gasto com a API. Você
  mostra que trocar o modelo grande pelo pequeno derruba o acerto de 96% para
  88% — e que ativar cache de prompt corta 60% do custo sem perder nada.
- **15:00** — Alguém do time de segurança avisa que um usuário conseguiu fazer
  o bot de atendimento revelar o prompt de sistema. Você trabalha na defesa.
- **17:00** — Escreve o registro do que mudou e por quê. Sobe o prompt novo com
  o portão de CI verde.

Se isso soa mais como engenharia de software do que como escrita criativa,
é porque é.

---

## Como você se torna um, em uma frase

> Aprenda a **medir** antes de aprender a **escrever**.

Todo mundo faz o contrário: passa seis meses colecionando técnicas de prompt e
nunca constrói um conjunto de teste. Essas pessoas ficam presas no nível de
"eu acho que ficou melhor" para sempre.

O caminho deste curso, em quatro degraus:

1. **Usar** um modelo com competência (semanas 1–2).
2. **Medir** — montar conjunto rotulado e arnês de avaliação (semanas 3–6).
   É aqui que 90% desiste, e é aqui que está o emprego.
3. **Integrar** — código, saída estruturada, ferramentas, custo, segurança
   (meses 2–4).
4. **Otimizar** — automatizar a busca pelo prompt em vez de escrevê-lo à mão
   (meses 5+).

O plano detalhado, com tempo realista, está em
[02-pre-requisitos](02-pre-requisitos.md) e no [00-MAPA](00-MAPA.md).

---

## Autoteste

1. Por que "o modelo é burro" quase nunca é o diagnóstico certo quando uma
   resposta vem ruim?
2. Qual é a diferença entre um prompt que *funcionou* e um prompt que *é bom*?
3. Nas quatro palavras da definição (repetível, verificável, barata, sistema),
   qual delas é a que mais gente ignora — e qual é a consequência prática?
4. Dê um exemplo de melhoria de prompt que aumenta a qualidade **e** o custo.
   Como você decidiria se vale a pena?
5. Por que "decorar frases mágicas" não é engenharia de prompt?
6. Se você só pudesse construir uma coisa antes de escrever qualquer prompt,
   o que seria, e por quê?
