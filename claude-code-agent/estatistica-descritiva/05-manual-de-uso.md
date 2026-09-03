# 5. Manual de uso — notação, funções e equivalências

`Nível: intermediário` · `Referência consultável` · `Última atualização: 20/08/2026`
`Verificado em Python 3.10.12, NumPy 2.2.6, em 20/08/2026`

> Este arquivo tem duas metades, porque a estatística tem duas linguagens:
> a **notação matemática** (§5.1–5.3), que você precisa *ler*; e as **funções das ferramentas**
> (§5.4 em diante), que você precisa *escrever*. Consulte por tarefa, não leia de ponta a ponta.

---

## 5.1 Como se lê a notação do campo

### A convenção que organiza tudo: latim × grego

| Alfabeto | Refere-se a | Exemplos |
|---|---|---|
| **Grego** | **parâmetro** — o valor verdadeiro na população, quase sempre desconhecido | μ (mi), σ (sigma), ρ (rô), π, β, θ |
| **Latim** | **estatística** — o valor calculado da sua amostra, conhecido e sujeito a erro | x̄, s, r, p̂, b, θ̂ |

Essa distinção não é decoração: **é o assunto inteiro da inferência estatística**.
μ é o que você quer saber; x̄ é o que você conseguiu medir. A distância entre os dois é o
**erro** ([arquivo 15](15-erro-e-incerteza.md)).

O "chapéu" (^) marca *estimativa*: θ̂ (lê-se "teta chapéu") é o palpite para θ.

### Tabela de símbolos

| Símbolo | Lê-se | Significa |
|---|---|---|
| `n` | ene | tamanho da amostra |
| `N` | ene maiúsculo | tamanho da população |
| `xᵢ` | xis índice i | a i-ésima observação |
| `x̄` | xis barra | média **amostral** |
| `μ` | mi | média **populacional** |
| `s` | esse | desvio padrão amostral |
| `s²` | esse ao quadrado | variância amostral |
| `σ` | sigma (minúsculo) | desvio padrão populacional |
| `σ²` | sigma ao quadrado | variância populacional |
| `Σ` | sigma (maiúsculo) | somatório — "some tudo isso" |
| `Π` | pi (maiúsculo) | produtório — "multiplique tudo isso" |
| `x₍ᵢ₎` | xis entre parênteses | o i-ésimo valor **depois de ordenar** |
| `Md`, `x̃` | mediana, xis til | mediana |
| `Q₁, Q₂, Q₃` | quartis | 25%, 50% e 75% dos dados abaixo |
| `IQR` | *interquartile range* | Q₃ − Q₁, amplitude interquartil |
| `EP`, `SE`, `σx̄` | erro padrão | desvio padrão **da média** = s/√n |
| `CV` | coeficiente de variação | s / x̄ (adimensional) |
| `r` | erre | correlação amostral de Pearson |
| `ρ` | rô | correlação populacional |
| `p̂` | pê chapéu | proporção amostral |
| `α` | alfa | nível de significância (tipicamente 0,05) |
| `1−α` | — | nível de confiança (tipicamente 95%) |
| `E[X]` | esperança de xis | média teórica da variável aleatória X |
| `Var(X)` | variância de xis | dispersão teórica |
| `~` | "distribui-se como" | `X ~ N(μ, σ²)`: X segue normal |
| `≈` | aproximadamente | — |
| `∝` | proporcional a | — |
| `H₀`, `H₁` | agá zero, agá um | hipótese nula, alternativa |
| `iid` | — | independentes e identicamente distribuídas |

### A pegadinha de leitura mais comum

`N(μ, σ²)` — o segundo parâmetro é a **variância**, não o desvio padrão.
`N(100, 25)` significa média 100 e **desvio padrão 5**. Mas cuidado: R e Python usam a
convenção do desvio padrão nas funções (`rnorm(n, mean, sd)`, `NormalDist(mu, sigma)`).
**A notação do papel e a das ferramentas discordam.** Confira sempre — é fonte de erro por
fator de 5, 10, 100.

---

## 5.2 As fórmulas centrais, com tradução linha a linha

### Média

```
      1  n
x̄ = ─── Σ xᵢ
      n i=1
```
> "Some todos os valores e divida pela quantidade." Uma linha de código: `sum(x)/len(x)`.

### Variância e desvio padrão

```
       1   n                                    ┌──────────────────────┐
s² = ───── Σ (xᵢ − x̄)²           s = √s²  =    │  1/(n−1) Σ(xᵢ − x̄)²
      n−1 i=1                                   └──────────────────────┘
```
> "Para cada valor, veja o quanto ele se afasta da média, eleve ao quadrado, some tudo,
> divida por n−1, e tire a raiz." A raiz existe só para voltar à unidade original.

Versão **populacional** (divide por `n`):

```
       1   N
σ² = ───  Σ (xᵢ − μ)²
       N  i=1
```

### Erro padrão da média

```
          s
EP(x̄) = ───
         √n
```
> "O quanto a **média** balança de amostra para amostra." É a fórmula mais importante deste
> curso inteiro, e o motivo de precisão custar caro: para reduzir o EP pela metade, `n` tem de
> **quadruplicar**.

### Intervalo de confiança de 95% para a média (n grande)

```
x̄ ± 1,96 × EP(x̄)
```
> O `1,96` vem da distribuição normal: 95% da área está a menos de 1,96 desvios do centro.
> Com `n` pequeno (< 30), troca-se 1,96 pelo valor da **t de Student** com `n−1` graus de
> liberdade. Ver [15](15-erro-e-incerteza.md) e [18](18-inferencia-p-e-ic.md).

### Escore-z (padronização)

```
      x − x̄
z = ────────
        s
```
> "A quantos desvios padrão da média este valor está." Torna comparáveis coisas de unidades
> diferentes: altura em metros e peso em quilos viram ambas "número de desvios".

### Coeficiente de variação

```
       s
CV = ─── (× 100 para %)
       x̄
```
> Dispersão **relativa** ao tamanho. Um desvio padrão de 5 cm é enorme para parafusos e
> irrelevante para árvores. Só faz sentido em escala de razão com valores positivos
> (ver [10-fundamentos.md](10-fundamentos.md)); é sem sentido para temperatura em °C.

### Correlação de Pearson

```
          Σ (xᵢ − x̄)(yᵢ − ȳ)
r = ──────────────────────────────
     √[Σ(xᵢ − x̄)²] · √[Σ(yᵢ − ȳ)²]
```
> "Covariância dividida pelos dois desvios padrão", o que a força a ficar entre −1 e +1.
> Mede **apenas relação linear**. Ver [16](16-relacao-entre-variaveis.md).

---

## 5.3 Convenções de escrita em relatório

| Situação | Forma correta | Forma errada e comum |
|---|---|---|
| média com dispersão | `média 24,3 (DP 3,1)` | `24,3 ± 3,1` sem dizer o que é ± |
| média com incerteza da média | `24,3 (EP 0,42)` ou `IC95% [23,5; 25,1]` | `24,3 ± 0,42` sem rótulo |
| mediana com dispersão | `mediana 22 (IQR 18–27)` | `mediana 22 ± 4` |
| proporção | `42% (IC95% 39–45%), n = 1.200` | `42%` sozinho |
| valor-p | `p = 0,032` | `p < 0,05` (perde informação); `p = 0,000` (nunca é zero — escreva `p < 0,001`) |
| tamanho de efeito | `d = 0,45 (IC95% 0,12–0,78)` | só o p |
| arredondamento | 2 a 3 algarismos significativos | copiar as 15 casas do computador |

> **Regra de ouro do relatório honesto:** `±` sozinho não quer dizer nada. **Sempre diga o que
> é:** desvio padrão, erro padrão, intervalo de confiança, amplitude ou incerteza expandida.
> Quatro coisas diferentes, mesmo símbolo. É a fonte nº 1 de leitura errada em artigos
> científicos e em relatórios de laboratório.

Padrão brasileiro (ABNT/INMETRO): **vírgula decimal** e **ponto como separador de milhar**
(`1.234,56`). Em código e em publicação internacional, o inverso. Não misture no mesmo
documento.

---

## 5.4 Python — biblioteca padrão (`statistics`)

Tudo verificado em Python 3.10.12. Nenhuma instalação necessária.

### Posição

| Função | O que faz | Exemplo → resultado |
|---|---|---|
| `mean(d)` | média aritmética | `mean([1,2,3,4])` → `2.5` |
| `fmean(d)` | igual, mais rápida, sempre `float` | `fmean([1,2,3,4])` → `2.5` |
| `geometric_mean(d)` | média geométrica (taxas, crescimento) | `geometric_mean([1.1,1.2,0.9])` → `1.059105…` |
| `harmonic_mean(d)` | média harmônica (velocidades, taxas por unidade) | `harmonic_mean([60,40])` → `48.0` |
| `median(d)` | mediana (interpola se `n` par) | `median([1,2,3,4])` → `2.5` |
| `median_low(d)` | o menor dos dois centrais — devolve um dado real | `median_low([1,2,3,4])` → `2` |
| `median_high(d)` | o maior dos dois centrais | `median_high([1,2,3,4])` → `3` |
| `median_grouped(d, interval)` | mediana de dados agrupados em classes | — |
| `mode(d)` | moda (a primeira, se houver empate) | `mode([1,1,2,2,3])` → `1` |
| `multimode(d)` | **todas** as modas | `multimode([1,1,2,2,3])` → `[1, 2]` |
| `quantiles(d, n=4)` | corta em `n` partes iguais | ver §5.6 |

### Dispersão

| Função | Divide por | Use quando |
|---|---|---|
| `stdev(d)` | `n − 1` | os dados são uma **amostra** (o caso normal) |
| `pstdev(d)` | `n` | os dados são a **população inteira** |
| `variance(d)` | `n − 1` | idem, sem a raiz |
| `pvariance(d)` | `n` | idem |

### Relação entre duas variáveis (Python 3.10+)

| Função | Devolve |
|---|---|
| `covariance(x, y)` | covariância amostral |
| `correlation(x, y)` | r de Pearson |
| `linear_regression(x, y)` | `LinearRegression(slope=…, intercept=…)` |

```python
>>> import statistics as st
>>> st.correlation([1,2,3,4,5], [2,4,5,4,5])
0.7745966692414834
>>> st.linear_regression([1,2,3,4,5], [2,4,5,4,5])
LinearRegression(slope=0.6, intercept=2.2)
```

### Distribuição normal sem instalar SciPy

`NormalDist` resolve 90% do que se pede a uma tabela z, e quase ninguém sabe que existe:

```python
>>> from statistics import NormalDist
>>> qi = NormalDist(mu=100, sigma=15)
>>> qi.cdf(130)              # proporção abaixo de 130
0.9772498680518208
>>> qi.inv_cdf(0.975)        # o valor que deixa 97,5% abaixo
129.39945977879109
>>> NormalDist().inv_cdf(0.975)   # o famoso 1,96
1.959963984540054
```
> Foi assim que o `1,96` das fórmulas apareceu. Ele não é mágico nem arbitrário: é o ponto
> que deixa 2,5% em cada cauda da normal padrão.

---

## 5.5 Equivalências entre ferramentas

**Tabela de consulta rápida.** Coluna por ferramenta, linha por tarefa.

| Tarefa | Python (`statistics`) | NumPy | pandas | R | Planilha (pt-BR) | SQL |
|---|---|---|---|---|---|---|
| média | `mean(x)` | `np.mean(x)` | `s.mean()` | `mean(x)` | `=MÉDIA(A:A)` | `AVG(x)` |
| mediana | `median(x)` | `np.median(x)` | `s.median()` | `median(x)` | `=MED(A:A)` | `PERCENTILE_CONT(0.5)` |
| moda | `mode(x)` | — | `s.mode()` | — (usar `table`) | `=MODO(A:A)` | `MODE()` (alguns bancos) |
| **DP amostral (n−1)** | `stdev(x)` | `np.std(x, ddof=1)` | `s.std()` | `sd(x)` | `=DESVPAD.A(A:A)` | `STDDEV_SAMP(x)` |
| **DP populacional (n)** | `pstdev(x)` | `np.std(x)` | `s.std(ddof=0)` | — | `=DESVPAD.P(A:A)` | `STDDEV_POP(x)` |
| variância amostral | `variance(x)` | `np.var(x, ddof=1)` | `s.var()` | `var(x)` | `=VAR.A(A:A)` | `VAR_SAMP(x)` |
| quartil | `quantiles(x)` | `np.percentile(x,[25,50,75])` | `s.quantile([.25,.5,.75])` | `quantile(x)` | `=QUARTIL(A:A;1)` | `PERCENTILE_CONT(0.25)` |
| mín / máx | `min` / `max` | `np.min` / `np.max` | `s.min()` | `min` / `max` | `=MÍNIMO` / `=MÁXIMO` | `MIN` / `MAX` |
| contagem | `len(x)` | `x.size` | `s.count()` | `length(x)` | `=CONT.NÚM(A:A)` | `COUNT(x)` |
| correlação | `correlation(x,y)` | `np.corrcoef(x,y)[0,1]` | `df.corr()` | `cor(x,y)` | `=CORREL(A:A;B:B)` | `CORR(x,y)` |
| resumo completo | — | — | `df.describe()` | `summary(x)` | — | — |

### 🚨 As três armadilhas de padrão (*default*) que geram números diferentes

Este quadro sozinho já pagou o tempo de leitura deste arquivo.

| Ferramenta | Padrão do desvio padrão | Consequência |
|---|---|---|
| `statistics.stdev` (Python) | `n − 1` | ✅ amostral |
| **`np.std`** (NumPy) | **`n`** | ❌ populacional — **precisa de `ddof=1`** |
| `pandas.Series.std` | `n − 1` | ✅ amostral |
| `R: sd()` | `n − 1` | ✅ amostral |
| Excel `DESVPAD.A` | `n − 1` | ✅ amostral |
| SQL `STDDEV()` | depende do banco | ⚠️ PostgreSQL = amostral; outros variam |

**NumPy e pandas discordam por padrão**, e as duas bibliotecas convivem no mesmo script.
`df['x'].std()` e `np.std(df['x'])` devolvem números diferentes para a mesma coluna. Não é
bug: é uma escolha de padrão de cada projeto, feita em épocas e por comunidades diferentes.
Escreva `ddof` explicitamente **sempre** — em código de produção, `np.std(x, ddof=1)` é
autodocumentação, não pedantismo.

```python
# comportamento verificado em NumPy 2.2.6, 20/08/2026:
>>> import numpy as np
>>> x = np.array([2., 4., 4., 4., 5., 5., 7., 9.])
>>> x.std()            # ddof=0
2.0
>>> x.std(ddof=1)
2.138089935299395
```

---

## 5.6 Quantis: o mesmo dado, nove respostas diferentes

Não existe **uma** definição de quantil. Existem nove, catalogadas por Hyndman & Fan (1996),
e cada ferramenta escolheu a sua. Isso surpreende quase todo mundo.

Terceiro quartil de `[2, 4, 4, 4, 5, 5, 7, 9]`, **medido em NumPy 2.2.6 em 20/08/2026**:

| Método (`np.percentile(..., method=)`) | Q₃ | Quem usa esse por padrão |
|---|---|---|
| `linear` (**tipo 7**) | **5,50** | **NumPy, pandas, R, Excel `PERCENTIL.INC`, Google Sheets** |
| `lower` | 5,00 | — |
| `higher` | 7,00 | — |
| `nearest` | 5,00 | percentis de "vizinho mais próximo", comum em monitoração |
| `midpoint` | 6,00 | — |
| `inverted_cdf` (tipo 1) | 5,00 | definição de livro-texto de função quantílica |
| `hazen` (tipo 5) | 6,00 | hidrologia |
| `weibull` (tipo 6) | 6,50 | **`statistics.quantiles` do Python (padrão), Excel `PERCENTIL.EXC`, SPSS, Minitab** |
| `median_unbiased` (tipo 8) | 6,17 | recomendação de Hyndman & Fan |
| `normal_unbiased` (tipo 9) | 6,13 | quando se supõe normalidade |

**O mesmo Q₃ vale entre 5,00 e 7,00 — variação de 40%, com os mesmos oito números.**

```python
# Python: os dois métodos disponíveis na biblioteca padrão
>>> import statistics as st
>>> d = [2, 4, 4, 4, 5, 5, 7, 9]
>>> st.quantiles(d, n=4)                        # padrão: 'exclusive' (tipo 6)
[4.0, 4.5, 6.5]
>>> st.quantiles(d, n=4, method='inclusive')    # tipo 7 — igual a NumPy/R/Excel
[4.0, 4.5, 5.5]
```

**O que fazer na prática:**

1. Com `n` grande (> 200), a diferença some. Não perca tempo.
2. Com `n` pequeno, **declare o método** no relatório. "Q₃ = 5,5 (tipo 7)" é reprodutível;
   "Q₃ = 5,5" não é.
3. Se precisa que Python e Excel batam, use `method='inclusive'` no Python e `PERCENTIL.INC`
   no Excel.
4. Nunca compare quantis calculados por ferramentas diferentes sem antes conferir o método.
   Já houve relatório contestado em auditoria por causa disso.

---

## 5.7 Receitas por tarefa

### Resumo de cinco números (o que o boxplot desenha)

```python
import statistics as st

def resumo_cinco(d):
    q = st.quantiles(d, n=4, method='inclusive')
    return {"min": min(d), "Q1": q[0], "mediana": q[1], "Q3": q[2], "max": max(d)}

print(resumo_cinco([2, 4, 4, 4, 5, 5, 7, 9]))
# {'min': 2, 'Q1': 4.0, 'mediana': 4.5, 'Q3': 5.5, 'max': 9}
```

### Erro padrão e IC de 95%

```python
import statistics as st
from statistics import NormalDist

def ic95_media(d):
    n = len(d)
    m, s = st.mean(d), st.stdev(d)
    ep = s / n**0.5
    z = NormalDist().inv_cdf(0.975)          # 1,959963984540054
    return m, ep, (m - z*ep, m + z*ep)

m, ep, (lo, hi) = ic95_media([12, 15, 11, 14, 13, 12, 16, 14, 13, 15])
print(f"média {m:.2f}  EP {ep:.3f}  IC95% [{lo:.2f}; {hi:.2f}]")
# média 13.50  EP 0.500  IC95% [12.52; 14.48]
```
> ⚠️ Com `n = 10` o correto é usar a **t de Student** (que daria um intervalo ~13% mais largo),
> não a normal. A versão certa está em [15-erro-e-incerteza.md](15-erro-e-incerteza.md).

### Detectar outliers pela regra 1,5 × IQR

```python
import statistics as st

def outliers_iqr(d, k=1.5):
    q1, _, q3 = st.quantiles(d, n=4, method='inclusive')
    iqr = q3 - q1
    lo, hi = q1 - k*iqr, q3 + k*iqr
    return [x for x in d if x < lo or x > hi], (lo, hi)

print(outliers_iqr([10, 12, 11, 13, 12, 11, 60]))
# ([60], (8.75, 14.75))
```
> ⚠️ Esta regra **marca candidatos**, não culpados. Em dados assimétricos ela acusa valores
> perfeitamente normais. Ver [19-robustez-e-outliers.md](19-robustez-e-outliers.md).

### Média ponderada

```python
def media_ponderada(valores, pesos):
    if len(valores) != len(pesos):
        raise ValueError("valores e pesos com tamanhos diferentes")
    return sum(v*p for v, p in zip(valores, pesos)) / sum(pesos)

# nota final: prova 40%, trabalho 30%, participação 30%
print(media_ponderada([7.5, 8.0, 9.0], [0.4, 0.3, 0.3]))
# 8.1
```

### Soma numericamente estável (para muitos dados)

```python
import math
valores = [0.1] * 10_000_000
print(sum(valores))       # 999999.9998389754  ← erro acumulado
print(math.fsum(valores)) # 1000000.0          ← exato
```
> Somar 10 milhões de floats acumula erro de arredondamento. `math.fsum` (algoritmo de
> Shewchuk) e `statistics.fmean` são exatos. NumPy usa soma em pares (*pairwise*), que reduz
> muito o erro sem custo. Ver [75-armadilhas.md](75-armadilhas.md).

---

## 5.8 O que está obsoleto

| Obsoleto | Substituto | Desde |
|---|---|---|
| `DESVPAD()` / `STDEV()` sem sufixo (Excel) | `DESVPAD.A` / `STDEV.S` | Excel 2010 |
| `PERCENTIL()` sem sufixo | `PERCENTIL.INC` / `PERCENTIL.EXC` | Excel 2010 |
| `np.float`, `np.int`, `np.bool` | `float`, `int`, `bool` do Python | removidos no NumPy 1.24 |
| `interpolation=` em `np.percentile` | `method=` | NumPy 1.22 |
| `df.append()` (pandas) | `pd.concat([...])` | removido no pandas 2.0 |
| `scipy.stats.mode` com `keepdims` implícito | passar `keepdims` explícito | SciPy 1.9 |
| Reportar só `p < 0,05` | reportar `p` exato **+ tamanho de efeito + IC** | recomendação da ASA, 2016 |
| "erro provável" (0,6745 σ) | desvio padrão e IC | ~1930 |
| Tabelas z e t impressas | `NormalDist`, `scipy.stats` | qualquer computador |

---

## 5.9 Atalhos que só quem usa há anos conhece

1. **`describe()` é o primeiro comando, nunca o último.** `df.describe()` (pandas) ou
   `summary(x)` (R) em 1 segundo revelam unidade errada, valor ausente e faixa impossível.
   Mas ele **não** mostra assimetria nem multimodalidade — para isso, histograma.
2. **Compare `mean` e `median` por reflexo.** Razão fora da faixa 0,9–1,1 significa
   assimetria; não relate a média sem dizer isso.
3. **`n` é obrigatório em qualquer número que você publique.** "4,7 estrelas" sem o `n` é
   propaganda, não medição.
4. **Um desvio padrão maior que a média, em dados positivos, é sinal de alerta.** Ou há
   outlier, ou a distribuição é de cauda pesada (log-normal, Pareto) e a média não descreve nada.
5. **`CV > 1` em dados positivos** costuma indicar que você deveria trabalhar em escala
   logarítmica.
6. **`np.errstate` e `pd.options.mode.chained_assignment`** existem para você *ver* os avisos,
   não para silenciá-los. Silenciar aviso numérico é a forma mais eficiente de publicar um
   número errado.
7. **Guarde a semente:** `random.seed(42)` / `np.random.default_rng(42)`. Simulação sem
   semente registrada não é reprodutível, e simulação não reprodutível não é evidência.
8. **`math.fsum` em vez de `sum`** quando forem mais de ~1 milhão de valores ou houver mistura
   de magnitudes muito diferentes.
9. **Cheque `len()` antes e depois de qualquer filtro.** Perdeu 30% das linhas sem perceber?
   Acontece toda semana, com todo mundo.
10. **Prefira `float` explícito na leitura.** Deixar o pandas inferir tipo é conveniente até o
    dia em que uma coluna com um `"N/A"` vira texto inteiro e a média some sem erro.

---

## Autoteste

1. O que distingue μ de x̄, e por que a distinção é o assunto central da estatística?
2. `N(100, 25)` — qual é o desvio padrão?
3. `np.std(x)` e `df['x'].std()` na mesma coluna: por que dão números diferentes?
4. Quantas definições de quantil existem, e qual é o padrão do NumPy, do R e do Excel?
5. Escreva corretamente, num relatório, uma média de 24,3 com desvio padrão 3,1 e n = 40.
6. De onde vem o número 1,96?
7. Por que `math.fsum` existe?
8. Qual a diferença entre `median` e `median_low`, e quando `median_low` é preferível?

<details><summary>Respostas</summary>

1. μ é o parâmetro **populacional** (verdadeiro, desconhecido); x̄ é a **estatística amostral**
   (calculada, conhecida, com erro). Toda a inferência é sobre o que x̄ permite afirmar a
   respeito de μ.
2. **5.** O segundo argumento na notação `N(μ, σ²)` é a variância. As funções de software, ao
   contrário, costumam pedir o desvio padrão.
3. Padrões diferentes de `ddof`: NumPy usa 0 (populacional), pandas usa 1 (amostral).
   Escreva `ddof` explicitamente.
4. Nove (Hyndman & Fan, 1996). NumPy, pandas, R e Excel `PERCENTIL.INC` usam o **tipo 7**;
   `statistics.quantiles` do Python e Excel `PERCENTIL.EXC` usam o **tipo 6**.
5. `média 24,3 (DP 3,1; n = 40)` — ou, se o objetivo é a precisão da média,
   `24,3 (EP 0,49; IC95% 23,3–25,3)`. Nunca `24,3 ± 3,1` sem rótulo.
6. É `NormalDist().inv_cdf(0.975)`: o ponto da normal padrão que deixa 2,5% em cada cauda.
7. Porque somar muitos `float` acumula erro de arredondamento; `fsum` faz a soma exata.
8. `median` interpola quando `n` é par (pode devolver valor inexistente nos dados);
   `median_low` devolve sempre **um dado real**. Prefira `median_low` quando o valor precisa
   existir de fato: um item de estoque, um paciente, uma categoria.

</details>

---

**Próximo:** [06-exemplos.md](06-exemplos.md) — 12 exemplos completos e executados.
