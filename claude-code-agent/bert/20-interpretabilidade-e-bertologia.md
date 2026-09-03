# 20 · BERTologia — o que o modelo realmente aprendeu

`Nível: avançado` · `Última atualização: 12/08/2026`

Entre 2019 e 2021 surgiu um subcampo inteiro dedicado a abrir o BERT e descobrir o que há lá
dentro. Ganhou o apelido de **BERTologia**, e produziu resultados que mudam a forma de usar o
modelo — não só curiosidades.

---

## 1 · Por que investigar?

Três motivos práticos, além da curiosidade:

1. **Confiar.** Se o modelo decide por um atalho espúrio, ele vai falhar de forma
   imprevisível — e você precisa saber disso antes do cliente.
2. **Consertar.** Saber *por que* errou aponta a correção certa: mais dados, dados
   diferentes, ou outra arquitetura.
3. **Explicar.** Setores regulados (crédito, saúde, RH) exigem justificativa da decisão
   automatizada — e a LGPD dá ao titular direito a revisão.

---

## 2 · O que cada camada aprende

O resultado mais citado da área (Tenney et al., 2019, *"BERT Rediscovers the Classical NLP
Pipeline"*): as camadas do BERT reproduzem, na ordem, o pipeline clássico de PLN que
linguistas computacionais montavam à mão nos anos 1990.

```
camadas  1–4    morfologia e sintaxe superficial (classe gramatical, limites de sintagma)
camadas  5–8    sintaxe profunda (dependências, papéis semânticos)
camadas  9–12   semântica, correferência, informação específica da tarefa
```

**Ninguém programou isso.** A hierarquia emergiu de treinar em MLM. É a evidência mais forte
de que a tarefa artificial de mascaramento captura estrutura linguística real.

**Consequência prática:**

- Para **NER e POS**, as camadas do meio (6–9) costumam dar embeddings melhores que a última.
- Para **similaridade de frases**, a última camada é excessivamente especializada; as
  penúltimas tendem a generalizar melhor.
- Ao **congelar camadas** no afinamento, congele as de baixo: são as mais genéricas e as que
  menos precisam mudar.

---

## 3 · As cabeças de atenção se especializam (e sobram)

Clark et al. (2019) catalogaram o comportamento das 144 cabeças do BERT-base. Encontraram
cabeças dedicadas a:

- olhar o **token seguinte** ou o **anterior** (posicionais puras);
- ligar **verbo ao objeto direto**;
- ligar **substantivo ao seu determinante**;
- resolver **correferência** (pronome → antecedente);
- olhar para `[SEP]` — a mais comum de todas, e a mais interessante.

**Por que tantas cabeças olham para o `[SEP]`?** A hipótese aceita: é uma operação de
"não fazer nada". A atenção **obriga** cada token a distribuir peso total 1 entre os outros —
não existe a opção de não atender. Quando uma cabeça não tem nada útil a fazer para aquele
token, ela despeja o peso num token semanticamente vazio. O `[SEP]` funciona como **lixeira de
atenção**.

Isso não é curiosidade inútil: modelos mais recentes acrescentam explicitamente um "token
nulo" ou permitem *attention sink*, justamente porque essa necessidade foi identificada aqui.

E o achado mais desconfortável (Michel et al., 2019): **a maioria das cabeças pode ser
removida sem perda significativa.** Em muitas camadas, uma única cabeça basta. Há redundância
massiva — o que abre espaço para poda (*pruning*) e explica por que modelos destilados
funcionam tão bem.

---

## 4 · Sondagem (*probing*): como se mede isso

A técnica padrão: congele o BERT, extraia os vetores, e treine um classificador **simples**
(regressão logística) para prever alguma propriedade linguística.

```
Se um classificador linear consegue prever "esta palavra é sujeito?"
a partir do vetor da camada 7 com 90% de acurácia,
então essa informação ESTÁ codificada linearmente ali.
```

**O problema metodológico, e é sério:** se a sonda for poderosa demais, ela pode *aprender* a
tarefa em vez de *ler* a informação. O controle correto (Hewitt & Liang, 2019) é medir a
**seletividade**: treine a mesma sonda com rótulos aleatórios; se ela também vai bem, a sonda
está aprendendo sozinha e o resultado não diz nada sobre o modelo.

É um cuidado que vale além da BERTologia: sempre que você "descobrir" que uma representação
contém informação, pergunte se não foi o seu detector que a inventou.

Resultado marcante dessa linha: Hewitt & Manning (2019) mostraram que existe uma
**transformação linear** do espaço do BERT em que a distância entre palavras corresponde à
distância na árvore sintática da frase. A árvore de análise sintática está lá dentro,
codificada geometricamente, sem que ninguém a tenha ensinado.

---

## 5 · A atenção **não** é explicação

Ponto importante, e contraintuitivo. É tentador mostrar o mapa de atenção como justificativa:
"o modelo olhou para esta palavra, por isso decidiu assim". Dois artigos de 2019 mostraram
que isso não se sustenta:

- **Jain & Wallace, *"Attention is not Explanation"*:** é possível construir distribuições de
  atenção completamente diferentes que produzem **exatamente a mesma predição**. Se várias
  explicações contraditórias levam ao mesmo resultado, nenhuma delas é *a* explicação.
- **Wiegreffe & Pinter, *"Attention is not not Explanation"*:** respondem que atenção carrega
  sinal útil, dependendo do que se entende por explicação.

**A posição defensável, e a que eu adoto:** a atenção mostra **para onde a informação fluiu**,
não **por que a decisão foi tomada**. Serve para depurar e formar hipóteses; não serve como
justificativa para um usuário, um auditor ou um regulador.

Para explicação de verdade, use métodos de atribuição:

| Método | Ideia | Custo |
|---|---|---|
| **Gradiente × entrada** | derivada da saída em relação a cada token | baratíssimo |
| **Integrated Gradients** | integra o gradiente ao longo de um caminho até uma linha de base | médio; teoricamente melhor fundamentado |
| **LIME** | aproxima localmente com um modelo simples, perturbando a entrada | caro |
| **SHAP** | valores de Shapley (teoria dos jogos) | caro, mas com propriedades garantidas |
| **Oclusão** | apaga cada palavra e mede o impacto | simples, intuitivo, e frequentemente o mais convincente para leigos |

Oclusão em cinco linhas, e funciona bem para mostrar a alguém:

```python
def importancia_por_oclusao(texto, prever):
    palavras = texto.split()
    base = prever(texto).confianca
    return sorted(
        ((p, base - prever(" ".join(palavras[:i] + palavras[i+1:])).confianca)
         for i, p in enumerate(palavras)),
        key=lambda x: -x[1],
    )
```

---

## 6 · Atalhos espúrios: o que o modelo realmente usa

O resultado mais útil para a prática. Modelos aprendem **correlações do conjunto de dados**,
não a tarefa que você imagina ter definido.

Casos documentados:

- **Inferência textual (NLI):** modelos aprendem que a palavra "not" na hipótese prevê
  "contradição", e acertam sem ler a premissa (Gururangan et al., 2018; McCoy et al., 2019).
- **QA:** modelos respondem pelo tipo da pergunta e pela proximidade das palavras, ignorando
  a pergunta em boa parte dos casos (Jia & Liang, 2017).
- **Classificação de sentimento:** aprender o nome do produto em vez da opinião.
- **Neste curso:** o classificador de chamados aprendeu que "nota fiscal" indica `FINANCEIRO`,
  e erra com 95% de confiança em "não consigo emitir nota fiscal, dá erro de certificado", que
  é claramente `TECNICO`
  ([projeto-modelo](07-projeto-modelo/README.md#o-que-este-modelo-não-faz-bem-limitações-honestas)).

**Como detectar atalhos no seu modelo:**

1. **Conjunto de teste adversarial** — reescreva 50 exemplos quebrando o atalho suspeito.
2. **Ablação de entrada** — remova metade do texto; se a acurácia mal cai, ele não usava
   aquela metade.
3. **Teste de invariância** — troque nome próprio, região, gênero. A predição não deveria
   mudar; se muda, você achou um viés.
4. **Ler os erros de maior confiança** — o método mais barato e mais eficaz de todos.

---

## 7 · Viés social

O modelo aprendeu do corpus, e o corpus é o mundo escrito com todos os seus vieses. Isso não
é opinião: é reprodutível em duas linhas.

```python
from transformers import pipeline
p = pipeline("fill-mask", model="neuralmind/bert-base-portuguese-cased")

for frase in ["O [MASK] cuidou das crianças.",
              "A [MASK] operou o paciente.",
              "A pessoa que mora na favela trabalha como [MASK]."]:
    print(frase, [r["token_str"] for r in p(frase)[:5]])
```

Rode e observe as associações de gênero, classe e região que aparecem. Elas vão para o seu
classificador junto com o resto.

**Onde isso vira dano concreto:** triagem de currículos, análise de crédito, moderação de
conteúdo, priorização de atendimento — qualquer decisão sobre pessoas.

**Mitigações, e a honestidade sobre elas:**

| Abordagem | Eficácia |
|---|---|
| Balancear os dados de afinamento | ajuda no que você mediu; não remove o viés do pré-treino |
| Remover atributos sensíveis do texto | fraco: proxies (nome, bairro, escola) permanecem |
| Debiasing no espaço de embeddings | reduz a medida, frequentemente sem reduzir o comportamento |
| **Auditar por subgrupo e medir** | **não corrige, mas é o único que torna o problema visível** |
| Manter humano na decisão | o mais eficaz na prática, e o mais caro |

Opinião profissional, explicitada: **não existe hoje técnica que "remova o viés" de um modelo
de linguagem.** Existem técnicas que reduzem métricas específicas de viés. Quem promete
neutralidade está vendendo. O que um profissional sério faz é medir por subgrupo, publicar o
resultado no model card, e desenhar o processo para que o erro seja recuperável.

---

## 8 · O que ainda não sabemos

Problemas em aberto, para calibrar o ceticismo:

- **Por que o pré-treino generaliza tão bem?** Há resultados parciais, nenhuma teoria completa.
- **Onde exatamente um fato fica guardado?** Há evidência de que as FFNs funcionam como
  memórias chave-valor, e técnicas de edição de conhecimento que às vezes funcionam — mas o
  mecanismo é mal compreendido.
- **Por que o afinamento é instável entre sementes?** Documentado, não explicado.
- **A "gramática" que o modelo aprende é a mesma dos linguistas?** As sondas encontram
  estruturas parecidas, mas isso pode ser artefato de estarmos procurando exatamente o que
  conhecemos.

---

## Autoteste

1. O que Tenney et al. descobriram sobre a ordem das camadas, e qual a consequência prática?
2. Por que tantas cabeças de atenção olham para o `[SEP]`?
3. O que significa a maioria das cabeças poder ser removida sem perda?
4. O que é probing, e qual é o controle metodológico que evita a armadilha da sonda poderosa?
5. Por que a atenção não é explicação? Qual foi o argumento de Jain & Wallace?
6. Cite três métodos de atribuição e o custo de cada um.
7. O que é um atalho espúrio? Dê o exemplo medido neste curso.
8. Liste quatro formas de detectar atalhos no seu modelo.
9. Por que "remover atributos sensíveis do texto" é uma mitigação fraca de viés?
10. Qual é a posição honesta sobre eliminar viés de modelos de linguagem hoje?

---

## Fontes

- Rogers, Kovaleva & Rumshisky (2020). *A Primer in BERTology*. [arXiv:2002.12327](https://arxiv.org/abs/2002.12327) — **leia este primeiro**
- Tenney, Das & Pavlick (2019). *BERT Rediscovers the Classical NLP Pipeline*. [arXiv:1905.05950](https://arxiv.org/abs/1905.05950)
- Clark et al. (2019). *What Does BERT Look At?* [arXiv:1906.04341](https://arxiv.org/abs/1906.04341)
- Michel, Levy & Neubig (2019). *Are Sixteen Heads Really Better than One?* [arXiv:1905.10650](https://arxiv.org/abs/1905.10650)
- Hewitt & Manning (2019). *A Structural Probe for Finding Syntax in Word Representations*. [aclanthology.org/N19-1419](https://aclanthology.org/N19-1419/)
- Hewitt & Liang (2019). *Designing and Interpreting Probes with Control Tasks*. [arXiv:1909.03368](https://arxiv.org/abs/1909.03368)
- Jain & Wallace (2019). *Attention is not Explanation*. [arXiv:1902.10186](https://arxiv.org/abs/1902.10186)
- Wiegreffe & Pinter (2019). *Attention is not not Explanation*. [arXiv:1908.04626](https://arxiv.org/abs/1908.04626)
- McCoy, Pavlick & Linzen (2019). *Right for the Wrong Reasons* (HANS). [arXiv:1902.01007](https://arxiv.org/abs/1902.01007)

---

*Anterior: [19-producao-e-otimizacao.md](19-producao-e-otimizacao.md) · Próximo: [60-teoria-avancada.md](60-teoria-avancada.md)*
