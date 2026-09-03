# 13 · Técnicas do núcleo — o que funciona, por quê, e a que custo

**Nível:** intermediário → avançado · **Escrito em:** 19/08/2026

O [05](05-manual-de-uso.md) diz *como escrever*. Este arquivo diz **por que
funciona, quanto custa, quando falha e o que a evidência sustenta** — inclusive
quando a evidência é fraca.

Cada técnica traz uma ficha:

> **Mecanismo** · **Ganho típico** · **Custo** · **Modo de falha** · **Status em 08/2026**

---

## 13.1 · Zero-shot bem especificado

Pedir sem exemplos, mas com papel, regras e formato exatos.

> **Mecanismo:** o ajuste por instrução já mapeou "pedido bem formado →
> atendimento". Você não precisa demonstrar o que já foi treinado.
> **Ganho:** é a linha de base. **Custo:** o menor de todos.
> **Falha:** julgamento sutil, vocabulário próprio da empresa, casos de
> fronteira. **Status:** primeira coisa a tentar, sempre.

**Regra de ouro:** só acrescente técnica quando o zero-shot bem especificado
falhar **de forma medida**. A maioria dos prompts elaborados que circulam por
aí resolve um problema que o zero-shot já resolvia.

---

## 13.2 · Few-shot (exemplos no prompt)

> **Mecanismo:** aprendizado em contexto ([10 §10.4](10-fundamentos.md)) — os
> exemplos estreitam a distribuição de continuações prováveis.
> **Ganho:** grande em formato e em julgamento de fronteira; medido em 9 pontos
> percentuais no [projeto-modelo](07-projeto-modelo/README.md) (82% → 91%).
> **Custo:** linear em tokens, **em toda chamada**. 8 exemplos de 60 tokens =
> 480 tokens fixos por requisição.
> **Falha:** exemplos enviesados ensinam o viés; exemplos fáceis não ensinam
> nada; o modelo copia o estilo, inclusive os defeitos.
> **Status:** a técnica mais duradoura da área. Vale desde 2020.

**Como escolher os exemplos, na prática:** rode o conjunto de avaliação, colete
os **erros**, agrupe por tipo, e escreva um exemplo por tipo de erro. Isso é
few-shot dirigido por dado, e é o que separa 5 exemplos que valem de 20 que
não valem.

**Variante avançada:** seleção dinâmica por similaridade
([06, exemplo 10](06-exemplos.md)). Ganha acerto, perde cache.

---

## 13.3 · Cadeia de pensamento e decomposição

> **Mecanismo:** cada token gerado entra no contexto do próximo. Escrever o
> raciocínio **cria os passos intermediários como contexto** para a conclusão.
> O modelo literalmente não tem onde "pensar" além do que escreve — exceto nos
> modelos com pensamento nativo, que têm um espaço reservado para isso.
> **Ganho:** era enorme em 2022; hoje, **pequeno ou nulo** nos modelos com
> raciocínio nativo — eles já fazem isso internamente.
> **Custo:** tokens de saída, que são os mais caros (5× a entrada, tipicamente).
> **Falha:** o raciocínio escrito é *plausível*, não necessariamente o processo
> real que levou à resposta. Não o trate como auditoria.
> **Status:** **use o pensamento nativo da API**. A frase "pense passo a passo"
> só continua útil em modelos pequenos e locais.

O que **continua** valendo é a **decomposição explícita**, que é outra coisa:

```
Antes de responder, preencha:
1. Fatos presentes no contrato: ...
2. Cláusulas aplicáveis: ...
3. Conclusão: ...
```

Isso não serve para o modelo pensar melhor — serve para **você poder auditar
onde ele errou**, e para poder testar cada etapa. É engenharia de
observabilidade disfarçada de técnica de prompt.

---

## 13.4 · Autoconsistência (votação)

Gere N respostas independentes e fique com a mais frequente.

> **Mecanismo:** erros de amostragem são idiossincráticos; a resposta correta
> tende a ser um atrator comum. **Ganho:** real em tarefas de resposta única e
> verificável. **Custo:** **N vezes**. Com N=5, você multiplicou a conta por 5.
> **Falha:** não corrige viés sistemático — se o modelo erra sempre da mesma
> forma, as 5 execuções concordam no erro, e você fica **mais confiante e
> igualmente errado**.
> **Status:** nicho. Justifica-se quando o erro custa muito mais que 5×.

**Uso adjacente e mais útil:** rodar N vezes **não** para votar, mas para
**medir instabilidade**. Um caso em que 5 execuções divergem é um caso que o
seu prompt não especificou bem. Divergência é diagnóstico gratuito.

---

## 13.5 · Autocrítica e revisão

Segunda chamada: "critique a resposta abaixo segundo estes critérios e produza
uma versão corrigida."

> **Mecanismo:** avaliar é mais fácil que gerar — e a resposta a criticar já
> está no contexto, então o modelo pode compará-la com os critérios em vez de
> construir do zero.
> **Ganho:** bom quando há **critério objetivo** ("todo número citado existe na
> ficha?"). Fraco quando o critério é vago ("melhore o texto").
> **Custo:** dobra as chamadas.
> **Falha:** o crítico tem os mesmos vieses do gerador. Se ele não sabia a
> resposta, não vai descobrir criticando. Pode inclusive **piorar** um texto
> que já estava certo, porque ele foi instruído a encontrar problemas.
> **Status:** vale com rubrica específica; não vale como "revise por favor".

**Melhoria com custo baixo:** dê ao crítico **informação nova** que o gerador
não tinha — resultado de um validador, saída de uma busca, o esquema violado.
Aí ele tem de onde tirar a correção. Crítica sem informação nova é ruído caro.

---

## 13.6 · Encadeamento (*prompt chaining*)

> **Mecanismo:** cada chamada tem um objetivo só e um contexto enxuto; a
> atenção não se divide entre tarefas concorrentes.
> **Ganho:** grande em tarefas heterogêneas (extrair + decidir + redigir).
> **Custo:** latência somada, mais chamadas, mais código, mais modos de falha.
> **Falha:** **propagação de erro** — se a etapa 1 extraiu errado, as etapas
> seguintes trabalham com lixo e não têm como saber.
> **Status:** padrão de arquitetura consolidado.

Mitigação obrigatória: **validação entre etapas**. Se a saída da etapa 1 não
passa no validador, pare ali; não deixe o erro andar pelo pipeline.

---

## 13.7 · Rubrica

Transformar julgamento em escala com âncoras.

```
Correção factual:
2 = nenhuma afirmação contradiz a base
1 = uma afirmação imprecisa, sem consequência prática
0 = qualquer afirmação factualmente errada
```

> **Mecanismo:** substitui uma escala contínua e vaga por poucas classes com
> definição operacional. Reduz drasticamente a variância entre execuções.
> **Ganho:** é o que torna avaliação por modelo utilizável.
> **Custo:** escrever a rubrica dá trabalho — e é trabalho que **precisa** ser
> feito com quem entende do negócio.
> **Falha:** rubrica sem âncora ("nota de 1 a 10 para qualidade") não reduz
> variância nenhuma; só produz números de aparência científica.
> **Status:** essencial. Ver [20-avaliacao-e-evals](20-avaliacao-e-evals.md).

Regra prática: **escala curta (0–2 ou 0–3), âncora textual em cada ponto, um
critério por dimensão.** Escala de 1 a 10 é um gerador de ruído.

---

## 13.8 · Priming de formato pela própria estrutura

Terminar o prompt com o início da estrutura esperada:

```
...
Responda no formato dos exemplos.

entrada: "O boleto veio errado"
saida:
```

> **Mecanismo:** a continuação mais provável de `saida:` é o conteúdo do
> campo — não uma saudação. Suprime preâmbulo pela **forma**, não pela ordem.
> **Ganho:** pequeno e barato.
> **Custo:** quase zero.
> **Falha:** confunde-se com o *prefill* de resposta do assistente — que é
> outra coisa, e que **foi removida** nos modelos Claude 4.6+ (erro 400). O
> priming descrito aqui está no **turno do usuário**, e continua válido.
> **Status:** vale, com a distinção acima entendida.

---

## 13.9 · Delegação a ferramenta

Quando a tarefa tem resposta verificável fora do modelo — cálculo, consulta,
data de hoje, conversão — **não peça ao modelo; dê a ferramenta**.

> **Mecanismo:** troca geração probabilística por execução determinística.
> **Ganho:** de "às vezes erra" para "não erra", na parte delegada.
> **Custo:** implementar e proteger a ferramenta; mais uma rodada de chamada.
> **Falha:** o modelo escolhe a ferramenta errada ou preenche parâmetro errado
> — quase sempre porque a **descrição** da ferramenta é ruim
> ([05 §5.9](05-manual-de-uso.md#59--ferramentas-e-agentes)).
> **Status:** o padrão de 2026. Ver [25](25-ferramentas-e-agentes.md).

**Heurística:** se você consegue escrever a função em Python, escreva a função.
Cada tarefa determinística que você tira do modelo é um modo de falha a menos.

---

## 13.10 · Tabela de decisão

| Sintoma medido | Primeira coisa a tentar |
|---|---|
| formato varia | saída estruturada da API; se indisponível, esquema literal + supressão de preâmbulo |
| inventa dado | fornecer fonte no contexto + permitir "NÃO ENCONTRADO" + verificar citação |
| erra casos de fronteira | few-shot dirigido pelos erros medidos |
| usa vocabulário errado | conjunto fechado com definição de cada termo |
| erra conta ou data | ferramenta |
| resposta longa demais | limite numérico + verificação + corte automático |
| inconsistente entre execuções | especificar o critério que está ambíguo; não é "aumentar a insistência" |
| bom no teste, ruim em produção | seu conjunto de avaliação não representa a produção — o problema é o conjunto |
| caro demais | cache, modelo menor com cascata, menos exemplos, lote |
| lento demais | streaming, modelo menor, menos etapas na cadeia, menos tokens de saída |

**A última linha da tabela é a mais importante da página:** quando o
comportamento em produção não bate com a avaliação, **o defeito está na
avaliação**, não no prompt. Corrija o conjunto primeiro.

---

## Autoteste

1. Por que "pense passo a passo" perdeu valor, e o que continua valendo da
   decomposição explícita?
2. Autoconsistência com N=5 falha em qual situação — e por que ela é
   perigosa exatamente aí?
3. O que torna a autocrítica útil em vez de ruído caro?
4. Qual é o principal risco do encadeamento e qual é a mitigação obrigatória?
5. Por que escala de 1 a 10 é pior que 0 a 2 numa rubrica?
6. Qual é a diferença entre priming de formato e *prefill* do assistente, e
   por que ela importa em 2026?
7. Seu prompt vai bem no teste e mal em produção. Onde está o defeito?
