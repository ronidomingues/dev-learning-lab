# 14. Forma e distribuições — o que a média e o desvio padrão não contam

`Nível: intermediário → avançado` · `Última atualização: 20/08/2026`
`Simulações executadas em Python 3.10.12 em 20/08/2026; as saídas são reais.`

> Posição e dispersão são dois números. Eles descrevem completamente uma distribuição
> **normal** — e apenas ela. Para todo o resto, falta a **forma**: para que lado ela pende,
> quão pesadas são as caudas, quantos picos tem.

---

## 14.1 Assimetria (*skewness*)

### O que é

Mede para que lado a distribuição se estende mais.

```
   ASSIMETRIA À DIREITA (positiva)      SIMÉTRICA        ASSIMETRIA À ESQUERDA (negativa)
        ▐▌                                 ▗▄▖                            ▐▌
        ▐▌▖                              ▗▟███▖                          ▗▐▌
        ▐███▄▖                          ▗██████▖                     ▗▄▄███▌
        ▐██████▄▄▄▖▁▁▁               ▗▄██████████▄▄▖          ▁▁▁▗▄▄██████▐▌
     ───┴──┴───────────────       ───┴─────┴─────┴───       ──────────────┴──┴───
        Mo Md  x̄                        Mo=Md=x̄                    x̄  Md Mo

     renda, tempo de resposta,                              nota de prova fácil,
     tamanho de cidade, preço                               idade ao morrer
```

**A ordem `Mo < Md < x̄` na assimetria à direita não é coincidência**: a média é puxada pela
cauda, a mediana resiste, a moda fica no pico. É por isso que o diagnóstico
`média/mediana > 1,2` funciona.

⚠️ Mas atenção: essa ordem é uma **regra empírica**, não um teorema. Existem distribuições
com assimetria positiva em que a mediana é maior que a média. São raras em dados reais, mas
existem — motivo pelo qual o diagnóstico do projeto-modelo usa a razão medida, e não uma
suposição.

### A fórmula

```
          n            ⎛ xᵢ − x̄ ⎞³
G₁ = ───────────── · Σ ⎜────────⎟
      (n−1)(n−2)       ⎝    s    ⎠
```

O **cubo** faz duas coisas de propósito: preserva o sinal (desvios negativos continuam
negativos) e amplifica os afastamentos grandes. Como está padronizado por `s`, é adimensional.

Leitura prática:

| \|G₁\| | Leitura |
|---|---|
| < 0,5 | aproximadamente simétrica |
| 0,5 a 1 | assimetria moderada |
| > 1 | assimetria forte — **não relate a média como valor típico** |

---

## 14.2 Curtose: o mito mais persistente da estatística descritiva

### O que quase todo livro diz (e está errado)

> "Curtose mede o achatamento da distribuição."

**Não mede.** Essa definição circula desde os anos 1940 e sobrevive em livros didáticos até
hoje. O que a curtose mede é **peso de cauda** — a propensão a produzir valores extremos.

O argumento decisivo é de Peter Westfall (*"Kurtosis as Peakedness, 1905–2014. R.I.P."*,
*The American Statistician*, 2014): a fórmula eleva os desvios padronizados à **quarta
potência**. Um valor a 3 desvios da média contribui com `3⁴ = 81`; um valor a 0,5 desvio
contribui com `0,5⁴ = 0,0625`. **A região central é aritmeticamente irrelevante para o
resultado.** A curtose é dominada pelas caudas, e por construção não pode estar medindo o pico.

```
          n(n+1)          ⎛ xᵢ − x̄ ⎞⁴      3(n−1)²
G₂ = ─────────────────· Σ ⎜────────⎟  −  ─────────────
      (n−1)(n−2)(n−3)     ⎝    s    ⎠      (n−2)(n−3)
```

O `−3` no final é o que a torna **curtose em excesso**: a normal passa a valer 0, servindo de
referência.

| G₂ | Nome | Significa |
|---|---|---|
| < 0 | platicúrtica | caudas **leves** — extremos raros (uniforme: −1,2) |
| ≈ 0 | mesocúrtica | como a normal |
| > 0 | leptocúrtica | caudas **pesadas** — extremos mais frequentes que na normal |

**Tradução operacional:** curtose alta significa *"prepare-se para valores absurdos"*.
Retornos financeiros diários têm curtose em excesso tipicamente entre 3 e 10 — motivo pelo
qual modelos que supõem normalidade subestimam crises sistematicamente. Foi essa
subestimação, entre outras coisas, que quebrou o fundo LTCM em 1998.

### Medido

```python
import random, math, statistics as st

def assim(d):
    n = len(d); m = st.mean(d); s = st.stdev(d)
    return (n / ((n-1)*(n-2))) * sum(((x-m)/s)**3 for x in d)

def curt(d):
    n = len(d); m = st.mean(d); s = st.stdev(d)
    a = (n*(n+1)) / ((n-1)*(n-2)*(n-3))
    b = (3*(n-1)**2) / ((n-2)*(n-3))
    return a * sum(((x-m)/s)**4 for x in d) - b

random.seed(99)
N = 200000
casos = [
    ("normal",           [random.gauss(0, 1) for _ in range(N)],            "0", "0"),
    ("uniforme",         [random.uniform(0, 1) for _ in range(N)],          "0", "-1,2"),
    ("exponencial",      [random.expovariate(1.0) for _ in range(N)],       "2", "6"),
    ("log-normal(0,1)",  [math.exp(random.gauss(0, 1)) for _ in range(N)],  "6,18", "110,9"),
    ("Pareto(a=1,5)",    [random.paretovariate(1.5) for _ in range(N)],     "inf", "inf"),
]
print(f"{'distribuicao':>16} {'assimetria':>11} {'teorica':>8} {'curtose exc':>12} {'teorica':>8} {'cob.1DP':>8}")
for nome, d, ta, tc in casos:
    m, s = st.mean(d), st.stdev(d)
    cob = sum(1 for x in d if abs(x - m) <= s) / len(d)
    print(f"{nome:>16} {assim(d):>11.3f} {ta:>8} {curt(d):>12.3f} {tc:>8} {cob:>7.1%}")
```

```
    distribuicao  assimetria  teorica  curtose exc  teorica  cob.1DP
          normal       0.000        0        0.016        0   68.3%
        uniforme      -0.007        0       -1.201     -1,2   57.8%
     exponencial       1.993        2        5.832        6   86.5%
 log-normal(0,1)       5.759     6,18       73.401    110,9   90.9%
   Pareto(a=1,5)     375.858      inf   156538.941      inf   99.7%
```

Três leituras que valem mais que a tabela:

1. **Normal, uniforme e exponencial batem com a teoria** com 200 mil observações. Bom sinal:
   as fórmulas estão certas.
2. **A log-normal não bate: 5,76 medido contra 6,18 teórico; 73 contra 111.** E o erro é
   **para baixo**, sempre. Motivo: assimetria e curtose amostrais dependem dos extremos, e
   você raramente sorteia o extremo. **Com cauda pesada, essas medidas são sistematicamente
   subestimadas** — mesmo com `n` enorme.
3. **A Pareto(1,5) tem assimetria e curtose teoricamente infinitas**, e mesmo assim o
   computador cospe 375,86 e 156.538,94 sem reclamar. Números que **não existem** aparecendo
   como se fossem medições. Repita a simulação com outra semente e eles mudam completamente.

> **Regra profissional:** com `n < 100`, ou com suspeita de cauda pesada, **assimetria e
> curtose amostrais são indício, não medida**. Use-as como sinalizador ("olhe o histograma"),
> nunca como resultado a reportar com casas decimais.

---

## 14.3 As distribuições que você vai encontrar de verdade

### Normal (gaussiana)

**Quando aparece:** quando o resultado é a **soma** de muitos efeitos pequenos e independentes.
Erro de medição, altura, ruído térmico, média amostral de quase qualquer coisa (Teorema Central
do Limite — [arquivo 17](17-amostragem-lgn-tcl.md)).

**Quando não aparece:** praticamente todo o resto. Renda, preços, tempos de resposta, tamanho
de arquivo, número de seguidores, população de cidades, duração de chamadas.

> **O nome é uma armadilha pedagógica.** "Normal" sugere "o usual", e Quetelet a popularizou
> exatamente com essa leitura ([arquivo 11](11-historia.md)). Karl Pearson lamentou por escrito
> ter ajudado a fixar o termo. Poincaré resumiu a ironia: *os matemáticos acreditam na normal
> porque acham que é um fato experimental; os experimentais acreditam porque acham que é um
> teorema matemático.*

### Log-normal

**Quando aparece:** quando o resultado é o **produto** de muitos efeitos — ou seja, quando os
efeitos são **percentuais**, não aditivos. Renda, preço de ativos, tamanho de cidades, tempo de
resposta, duração de tarefas, concentração de poluentes.

Propriedades que valem decorar:

- `log(X)` é normal — por isso o log "endireita" esses dados
  ([exemplo 14](06-exemplos.md), onde a cobertura de 1 DP voltou de 83% para 67,8%);
- **a média geométrica é a mediana** — por isso `exp(média do log)` estima o caso típico;
- `média > mediana > moda`, sempre, e a distância entre elas cresce com a dispersão.

**Como reconhecer:** média/mediana bem acima de 1, CV alto, e o histograma vira sino ao aplicar
log. É a distribuição mais comum em dados socioeconômicos e de sistemas.

### Exponencial

**Quando aparece:** tempo **até** um evento sem memória — próxima chegada, próxima falha,
tempo entre requisições.

**Propriedade que assusta:** a **falta de memória**. Se o tempo médio de espera é 5 minutos e
você já esperou 10, o tempo esperado até o próximo evento continua sendo 5 minutos. A espera
já cumprida não conta.

Consequência: `média = desvio padrão` (CV = 1 sempre). Se você mede tempos entre eventos e o
CV der perto de 1, provavelmente o processo é Poisson.

### Poisson

**Quando aparece:** **contagem** de eventos raros em um intervalo fixo — acidentes por mês,
defeitos por lote, chegadas por minuto, mutações por gene.

**Propriedade que a define:** `média = variância`. Isso dá um teste de sanidade poderoso e
gratuito: calcule variância/média. Se der ≈ 1, Poisson descreve bem. Se der muito acima de 1,
há **superdispersão** — os eventos se agrupam (um acidente causa outro; um defeito indica lote
ruim), e o modelo certo é binomial negativa. Ignorar superdispersão produz intervalos de
confiança estreitos demais, e essa é uma falha comum em análise de contagens.

### Uniforme

Todos os valores igualmente prováveis. Aparece pouco em dados naturais e muito em
**simulação** e em **arredondamento**. Curtose em excesso −1,2 (caudas leves: não há extremos).

Se seus dados reais parecem uniformes, desconfie de artefato — arredondamento, truncamento,
dado sintético ou gerador de teste esquecido em produção.

### Pareto e a lei de potência

**Quando aparece:** riqueza, tamanho de cidade, vendas de livros, popularidade, tamanho de
arquivo, danos de catástrofe, número de conexões numa rede.

```python
random.seed(1)
rendas = sorted((random.paretovariate(1.16) for _ in range(100000)), reverse=True)
tot = sum(rendas)
for p in (0.01, 0.05, 0.10, 0.20, 0.50):
    k = int(p * len(rendas))
    print(f"  os {p:.0%} maiores detem {sum(rendas[:k])/tot:.1%} do total")
```

```
  os 1% maiores detem 46.1% do total
  os 5% maiores detem 61.5% do total
  os 10% maiores detem 69.1% do total
  os 20% maiores detem 77.5% do total
  os 50% maiores detem 89.7% do total
```

Os 20% maiores detêm 77,5% do total: é a **regra 80/20** de Pareto, aparecendo por construção.
(O expoente 1,16 é justamente o que produz o 80/20 exato; o desvio de 77,5% para 80% é a
flutuação amostral com `n = 100.000`.)

**O que isso implica e quase ninguém internaliza:** em distribuição de lei de potência,
**a média não descreve nada** — nem o típico (para isso, mediana) nem o total (para isso, a
cauda). Existe até uma faixa de expoentes em que a **variância é infinita** (`α ≤ 2`) e outra
em que a **média é infinita** (`α ≤ 1`). Não é abstração: para seguros de catástrofe e danos
cibernéticos, os expoentes estimados ficam perigosamente perto de 1, o que significa que o
"prêmio médio esperado" pode não existir como número.

### Cauchy — a distribuição em que a média não converge

```python
import random, math
random.seed(5)

soma = 0.0
print(f"{'n':>9} {'media acumulada':>18}")
for n in range(1, 1000001):
    soma += math.tan(math.pi * (random.random() - 0.5))   # amostra de Cauchy
    if n in (10, 100, 1000, 10000, 100000, 1000000):
        print(f"{n:>9} {soma/n:>18.4f}")
```

```
        n    media acumulada
       10             0.8128
      100            -2.1893
     1000            -1.0063
    10000            -5.7588
   100000             2.0056
  1000000            -0.2187
```

**Um milhão de observações e a média ainda pula de −5,76 para +2,01.** Não é lentidão de
convergência: a média da Cauchy **não existe**, e a Lei dos Grandes Números não se aplica.
A média de `n` amostras Cauchy tem exatamente a mesma distribuição de **uma única** amostra —
coletar mais dados não melhora nada.

**Isso não é curiosidade acadêmica.** A Cauchy é a razão de duas normais centradas em zero.
Toda vez que você calcula uma **razão** de duas quantidades ruidosas — ganho/custo, melhoria
percentual, eficiência, "quantas vezes melhor" — está flertando com esse comportamento. Se o
denominador pode chegar perto de zero, a razão tem cauda pesadíssima, e média e desvio padrão
dela são **números sem significado**. Use mediana.

---

## 14.4 Multimodalidade: quando nenhuma medida de posição serve

Se o histograma tem dois picos, quase sempre há **duas populações misturadas**:

- tempos de resposta: acertos de cache × ida ao banco de dados;
- alturas: homens × mulheres;
- notas: quem estudou × quem não estudou;
- preços: promoção × preço cheio;
- latência de rede: mesmo datacenter × outro continente.

**A média cai no vale entre os dois picos** — um valor que quase nenhuma observação tem.
Foi exatamente esse o erro do "homem médio" ([arquivo 11](11-historia.md)).

**O que fazer:** identificar a variável que separa os grupos e **descrever cada um**.
Se ela não estiver nos dados, diga isso explicitamente: *"a distribuição é bimodal; o resumo
por uma medida única não é adequado"* é uma conclusão legítima e honesta.

**Como detectar sem gráfico**, três sinais baratos:
1. razão `s / MAD escalado` alta sem outliers visíveis;
2. cobertura de 1 DP muito **abaixo** de 68% (os dados se afastam do centro dos dois lados);
3. curtose em excesso **negativa** com assimetria próxima de zero.

Mas o melhor detector continua sendo o **histograma**. É de graça.

---

## 14.5 Transformações — e o preço de cada uma

| Transformação | Corrige | Cuidado |
|---|---|---|
| `log(x)` | assimetria à direita, efeitos multiplicativos | exige `x > 0`; voltar não devolve a média |
| `log1p(x)` = `log(1+x)` | idem, com zeros | distorce valores pequenos |
| `√x` | assimetria moderada, contagens | mais suave que o log |
| `1/x` | assimetria muito forte | inverte a ordem; interpretação difícil |
| Box-Cox | escolhe a potência automaticamente | exige `x > 0`; o λ ótimo é estimado dos dados |
| Yeo-Johnson | como Box-Cox, aceita zeros e negativos | menos interpretável |
| posto (*rank*) | qualquer assimetria | descarta toda a magnitude |

### A armadilha da volta

**`exp(média do log) ≠ média.`** No [exemplo 14](06-exemplos.md), a diferença foi de 25%:
R$ 2.852,74 contra R$ 3.810,38.

- Se a pergunta é sobre o **caso típico**, `exp(média do log)` (= média geométrica) é ótima.
- Se a pergunta é sobre o **total** (folha, arrecadação, carga), você precisa da média
  aritmética **na escala original**, e o log não serve. Existe uma correção (o "smearing" de
  Duan, 1983), e ela depende de suposições.

> **Recomendação, e é opinião:** transforme para **entender** e para **modelar**; volte à
> escala original para **comunicar**. Ninguém toma decisão em log-reais. E quando reportar em
> escala transformada, diga qual medida está reportando — "renda mediana", "média geométrica" —
> nunca "média" sem qualificação.

---

## 14.6 Como diagnosticar a forma em 30 segundos

Sem gráfico, só com números:

| Sinal | Suspeita |
|---|---|
| `média/mediana` > 1,2 | assimetria à direita (log-normal, Pareto) |
| `média/mediana` < 0,83 | assimetria à esquerda |
| `s > média` (dados positivos) | cauda pesada ou outlier dominante |
| `s / MAD` > 1,5 | outliers ou caudas pesadas |
| cobertura de 1 DP > 76% | caudas pesadas |
| cobertura de 1 DP < 60% | caudas leves ou **bimodalidade** |
| `variância / média` ≈ 1 (contagens) | Poisson |
| `variância / média` ≫ 1 (contagens) | superdispersão — eventos se agrupam |
| `s ≈ média` (tempos positivos) | exponencial |
| curtose em excesso > 3 | prepare-se para valores extremos |
| máximo ≫ p99 | cauda de lei de potência |

Com gráfico, é mais rápido ainda: **histograma + ECDF**, dez segundos. Ver
[20-visualizacao-de-medidas.md](20-visualizacao-de-medidas.md).

---

## Autoteste

1. Curtose mede achatamento? Qual é o argumento decisivo?
2. Por que a assimetria amostral de uma log-normal deu 5,76 quando a teórica é 6,18?
3. A simulação Pareto(1,5) devolveu assimetria 375,86. O que está errado nessa frase?
4. Renda é log-normal. Qual medida estima melhor o "caso típico"? E o total?
5. Você conta acidentes por mês e obtém média 4 e variância 16. O que isso indica?
6. Tempo médio de espera é 5 min e você já esperou 10. Quanto falta esperar, em média?
7. Por que a média de amostras Cauchy não converge, e o que isso ensina sobre razões?
8. Histograma bimodal: qual é a resposta correta, e qual é a resposta errada mais comum?
9. `exp(média do log)` é a média? O que é?
10. Numa Pareto com α = 1,16, quanto os 20% maiores detêm? Que "regra" é essa?

<details><summary>Respostas</summary>

1. **Não.** A fórmula eleva os desvios padronizados à 4ª potência, e valores próximos do
   centro (|z| < 1) contribuem com quase nada, enquanto |z| = 3 contribui com 81. A medida é
   dominada pelas caudas e não pode estar medindo o pico (Westfall, 2014).
2. Porque medidas de forma dependem dos extremos, e a amostra raramente contém o extremo.
   Com cauda pesada, assimetria e curtose amostrais são **sistematicamente subestimadas**.
3. Que a Pareto(1,5) tem assimetria **infinita** — o número 375,86 não mede nada, é um artefato
   da amostra. Outra semente daria outro número completamente diferente.
4. Típico: **mediana**, ou equivalentemente a **média geométrica** (`exp(média do log)`).
   Total: **média aritmética na escala original** — e só ela.
5. `variância/média = 4 ≫ 1`: **superdispersão**. Os acidentes se agrupam; Poisson não serve,
   e usar Poisson produziria intervalos de confiança estreitos demais.
6. **5 minutos.** A exponencial não tem memória: o tempo já esperado não conta.
7. Porque a Cauchy não tem média definida (a integral não converge) e a Lei dos Grandes
   Números não se aplica. Lição: **razões de quantidades ruidosas**, cujo denominador pode
   chegar perto de zero, têm caudas desse tipo — use mediana, nunca média.
8. **Correta:** identificar a variável que separa os dois grupos e descrever cada um; ou
   declarar explicitamente que um resumo único não é adequado. **Errada:** relatar a média,
   que cai no vale entre os picos e não descreve praticamente ninguém.
9. É a **média geométrica**, que numa log-normal coincide com a **mediana**. Não é a média
   aritmética — no exemplo 14 a diferença foi de 25%.
10. **77,5%** na simulação (≈ 80% teóricos). É a **regra 80/20** de Pareto, e ela não é uma
    observação empírica isolada: sai por construção do expoente da distribuição.

</details>

---

**Próximo:** [15-erro-e-incerteza.md](15-erro-e-incerteza.md) — o coração da pergunta que
originou este curso.
