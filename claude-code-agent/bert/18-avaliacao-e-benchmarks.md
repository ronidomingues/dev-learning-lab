# 18 · Avaliação — como saber se o modelo está bom (e não se enganar)

`Nível: intermediário` · `Última atualização: 12/08/2026`

O arquivo que separa quem entrega modelo que funciona de quem entrega número bonito.
A maioria dos fracassos de projeto de PLN não é técnica — é de medição.

---

## 1 · A acurácia mente

```
Detector de fraude. 1.000 transações, 10 são fraude.
Modelo: "nunca é fraude."
Acurácia: 99,0%
Fraudes detectadas: 0
```

Esse modelo tem uma linha de código e 99% de acurácia. É inútil. E variações dele são
publicadas em relatórios internos toda semana.

**Acurácia só é honesta quando as classes são equilibradas e os erros custam o mesmo.**
Nenhuma das duas condições costuma valer no mundo real.

---

## 2 · As métricas que importam

Tudo parte da matriz de confusão, para uma classe:

```
                      previsto
                  positivo  negativo
verdade positivo     VP        FN      ← FN: eu perdi um caso real
        negativo     FP        VN      ← FP: eu acusei quem não era
```

| Métrica | Fórmula | Pergunta que responde | Quando é a métrica certa |
|---|---|---|---|
| **Precisão** | VP / (VP+FP) | "quando digo sim, acerto quanto?" | falso positivo é caro (bloquear cliente legítimo) |
| **Recall** | VP / (VP+FN) | "de tudo que era sim, achei quanto?" | falso negativo é caro (deixar passar fraude, tumor) |
| **F1** | média harmônica das duas | equilíbrio | quando os dois erros importam parecido |
| **F1 macro** | média das F1 por classe | todas as classes valem igual | **padrão para multiclasse desbalanceada** |
| **F1 micro** | agrega antes de calcular | domina a classe grande | = acurácia em multiclasse de rótulo único |
| **F1 ponderada** | média pesada pelo suporte | meio-termo | relatórios gerenciais |
| **AUC-ROC** | separação em todos os limiares | qualidade independente do limiar | comparar modelos, não decidir |
| **AUC-PR** | idem, com precisão/recall | classes muito raras | **melhor que ROC quando < 5% positivos** |

**Por que média harmônica na F1, e não aritmética?** Porque a harmônica pune desequilíbrio.
Um modelo com precisão 1,0 e recall 0,0 (só acerta um caso, e acerta) teria média aritmética
0,5 — parece razoável, e é inútil. Média harmônica: 0,0. É o comportamento correto.

### O erro mais caro de todos: escolher a métrica depois de ver o resultado

Defina a métrica **antes** de treinar, derivada do custo real do erro no seu negócio. Trocar
para a métrica em que o modelo foi melhor é auto-engano, e você não vai nem perceber que fez.

---

## 3 · A matriz de confusão é obrigatória

Números agregados escondem tudo. Sempre imprima a matriz:

```
              CANCELAMENTO  COMERCIAL  FINANCEIRO  TECNICO
CANCELAMENTO             6          0           2        1
COMERCIAL                0          9           0        0
FINANCEIRO               0          0           9        0
TECNICO                  0          0           0        9
```

(Saída real do [projeto-modelo](07-projeto-modelo/README.md).)

O agregado diz "91,7% de acurácia". A matriz diz algo muito mais acionável: **todos os erros
estão numa linha só** — `CANCELAMENTO` perdeu 3 de 9, confundidos com `FINANCEIRO` e
`TECNICO`. Isso aponta para uma ação concreta: mais exemplos de cancelamento, ou revisar se a
fronteira entre "cancelar" e "cobrança indevida" está bem definida nos rótulos.

**Regra:** se você não olhou a matriz, você não avaliou o modelo. Olhou o placar.

---

## 4 · O limiar de decisão é uma decisão de negócio

O modelo produz probabilidade. Transformar em decisão exige um corte, e o corte padrão (0,5)
quase nunca é o certo.

```python
import numpy as np
from sklearn.metrics import precision_recall_curve

p, r, limiares = precision_recall_curve(y_true, probs_da_classe_positiva)
f1 = 2 * p * r / (p + r + 1e-9)
melhor = int(np.argmax(f1))
print(f"melhor limiar: {limiares[melhor]:.2f} → F1 {f1[melhor]:.3f} "
      f"(precisão {p[melhor]:.3f}, recall {r[melhor]:.3f})")
```

Escolha o limiar pelo **custo**, não pela F1:

```
Triagem de currículos    → recall alto (não perder bom candidato); revisão humana filtra
Bloqueio automático      → precisão alta (não bloquear cliente legítimo)
Moderação de conteúdo    → dois limiares: acima remove, abaixo ignora, no meio vai para humano
```

**Otimize o limiar na validação, nunca no teste.** Ajustar o limiar olhando o teste é
vazamento — o número final vira otimista.

---

## 5 · Divisão dos dados: os erros que inflam resultado

| Erro | Como acontece | Efeito |
|---|---|---|
| **Duplicatas** entre treino e teste | textos repetidos na base | modelo "acerta" por memorização |
| **Vazamento temporal** | dados futuros no treino, passados no teste | funciona no teste, falha em produção |
| **Vazamento de grupo** | mesmo cliente/documento nos dois lados | superestima generalização |
| **Divisão não estratificada** | classe rara some do teste | métrica sem sentido |
| **Reusar o teste** | ajustar hiperparâmetros olhando o teste | teste vira validação; resultado otimista |
| **Feature que entrega a resposta** | id, timestamp, prefixo do protocolo | acurácia absurda |

**Se o seu dado tem tempo, divida por tempo.** Treine no passado, teste no futuro. Divisão
aleatória em dado temporal é otimista e mente sobre produção — o modelo já viu o "futuro"
durante o treino.

### O baseline burro

Sempre meça, sempre reporte:

| Baseline | Custo de implementar |
|---|---|
| Classe majoritária | 1 linha |
| Palavra-chave / regex | 1 hora |
| **TF-IDF + regressão logística** | **5 linhas, 2 segundos de treino** |
| Zero-shot com modelo pronto | 3 linhas |

```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline

base = make_pipeline(TfidfVectorizer(ngram_range=(1, 2)), LogisticRegression(max_iter=1000))
base.fit(X_treino, y_treino)
print("baseline:", base.score(X_teste, y_teste))
```

Em tarefas de classificação de texto com vocabulário previsível, esse baseline chega
surpreendentemente perto do BERT — às vezes o alcança. Se o ganho do BERT for de 1 ou 2
pontos, pergunte se vale 440 MB, GPU, latência e complexidade operacional. Frequentemente não
vale, e admitir isso é sinal de maturidade, não de derrota.

---

## 6 · Intervalos de confiança: seu número tem barra de erro

Com 36 exemplos de teste, uma acurácia de 91,7% tem intervalo de confiança de 95% que vai de
cerca de **78% a 98%**. Reportar "91,7%" sem essa faixa dá uma impressão de precisão que o
dado não sustenta.

Estimativa por *bootstrap*, que funciona para qualquer métrica:

```python
import numpy as np
from sklearn.metrics import f1_score

def ic_bootstrap(y_true, y_pred, n=2000, semente=42):
    rng = np.random.default_rng(semente)
    y_true, y_pred = np.asarray(y_true), np.asarray(y_pred)
    amostras = [
        f1_score(y_true[i], y_pred[i], average="macro")
        for i in (rng.integers(0, len(y_true), len(y_true)) for _ in range(n))
    ]
    return np.percentile(amostras, [2.5, 97.5])

print("IC 95%% da F1 macro: %.3f a %.3f" % tuple(ic_bootstrap(y_true, y_pred)))
```

**Regra de bolso:** você precisa de algumas centenas de exemplos de teste **por classe** para
distinguir com segurança dois modelos que diferem em 1 ponto. Abaixo disso, "melhorei de 0,89
para 0,91" pode ser puro acaso.

E o mesmo vale para a semente: relate a média de 3 a 5 execuções, não a melhor. Reportar a
melhor de cinco é seleção de ruído — o número não se reproduz.

---

## 7 · Benchmarks públicos: para que servem e para que não servem

| Benchmark | O que mede | Estado em 2026 |
|---|---|---|
| **GLUE** (2018) | 9 tarefas de compreensão, inglês | saturado — modelos passaram do humano; serve como sanidade |
| **SuperGLUE** (2019) | versão difícil | também saturado |
| **SQuAD 1.1/2.0** | QA extrativo | ainda útil para QA; saturado no topo |
| **MTEB** | embeddings: 8 tipos de tarefa, dezenas de conjuntos | **a referência para busca/embeddings** |
| **XTREME / XGLUE** | multilíngue | referência para modelos multilíngues |
| **ASSIN 2** | similaridade e implicação em **português** | referência em PT |
| **PLUE / Portuguese benchmarks** | GLUE traduzido para PT | qualidade variável (é tradução automática) |

**Para que servem:** filtrar candidatos, comparar arquiteturas em condições padronizadas,
publicar artigo.

**Para que não servem:** decidir o seu modelo. Três razões concretas:

1. **Contaminação.** Modelos treinados em toda a web muito provavelmente viram os conjuntos de
   teste. Ninguém sabe medir isso direito.
2. **Otimização para o placar.** Um número que vira alvo deixa de ser boa medida
   (lei de Goodhart, e vale literalmente aqui).
3. **Distribuição diferente.** MTEB mede recuperação em Wikipédia e artigos científicos. Se o
   seu texto é chamado de suporte com erro de digitação, a correlação é fraca.

**50 exemplos rotulados do seu próprio problema valem mais que qualquer leaderboard.**

---

## 8 · Avaliar além da métrica

Um modelo aprovado no número pode ser inaceitável em produção. Verifique:

| Dimensão | Como testar |
|---|---|
| **Robustez** | erro de digitação, MAIÚSCULAS, sem acento, emoji, texto muito curto/longo |
| **Viés** | troque nome/gênero/região na mesma frase — a predição muda? |
| **Calibração** | entre os casos com 90% de confiança, ele acerta ~90%? (*expected calibration error*) |
| **Fora de distribuição** | texto de outro assunto — ele responde com confiança alta? (spoiler: sim) |
| **Latência de cauda** | p95 e p99, não a média — a média esconde o que o usuário sente |
| **Deriva** | a distribuição de entrada de hoje é a mesma de 6 meses atrás? |

O teste de calibração é o mais esquecido e o mais útil quando existe limiar de decisão. Redes
neurais modernas são sistematicamente **mais confiantes do que acertam** (Guo et al., 2017),
e a correção padrão (*temperature scaling*) é uma linha de código: divida os logits por uma
temperatura ajustada na validação.

---

## 9 · Fichamento do modelo (*model card*)

Antes de entregar, escreva meia página com:

- **Para que serve** e, mais importante, **para que não serve**
- Dados de treino: origem, período, volume, como foram rotulados
- Métrica no teste, **com intervalo de confiança**
- Matriz de confusão
- Limitações conhecidas e vieses medidos
- Limiar recomendado e por quê
- Data de treino e **data de revalidação** sugerida

Isso não é burocracia. É o que impede que, daqui a um ano, alguém use seu classificador de
chamados para triar currículos e descubra tarde demais que ele nunca foi feito para isso.

---

## Autoteste

1. Por que 99% de acurácia pode ser um modelo inútil? Dê o exemplo.
2. Quando você prefere precisão a recall? Dê um caso de cada.
3. Por que a F1 usa média harmônica?
4. Qual é a diferença entre F1 macro e F1 micro, e quando cada uma?
5. O que a matriz de confusão do projeto-modelo revelou que a acurácia escondia?
6. Onde otimizar o limiar de decisão — treino, validação ou teste? Por quê?
7. Cite três formas de vazamento de dados e como cada uma infla o resultado.
8. Qual o baseline burro para classificação de texto, e por que ele deve sempre ser medido?
9. Sua acurácia é 91,7% em 36 exemplos. Qual é a faixa plausível, aproximadamente?
10. Por que não escolher modelo pelo topo do MTEB?
11. O que é calibração e como corrigi-la?

---

## Fontes

- Wang et al. (2018). *GLUE*. [arXiv:1804.07461](https://arxiv.org/abs/1804.07461)
- Rajpurkar et al. (2016, 2018). *SQuAD 1.1 / 2.0*. [rajpurkar.github.io/SQuAD-explorer](https://rajpurkar.github.io/SQuAD-explorer/)
- Muennighoff et al. (2022). *MTEB*. [arXiv:2210.07316](https://arxiv.org/abs/2210.07316)
- Guo et al. (2017). *On Calibration of Modern Neural Networks*. [arXiv:1706.04599](https://arxiv.org/abs/1706.04599)
- Real, Fonseca & Gonçalo Oliveira (2020). *ASSIN 2*. [sites.google.com/view/assin2](https://sites.google.com/view/assin2)
- [scikit-learn — Model evaluation](https://scikit-learn.org/stable/modules/model_evaluation.html)

---

*Anterior: [17-familia-bert.md](17-familia-bert.md) · Próximo: [19-producao-e-otimizacao.md](19-producao-e-otimizacao.md)*
