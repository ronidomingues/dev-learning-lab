# 15. Erro e incerteza — o coração da pergunta

`Nível: intermediário → avançado` · `🔑 arquivo central deste curso`
`Última atualização: 20/08/2026`
`Simulações executadas em Python 3.10.12 em 20/08/2026; as saídas são reais.`

> A pergunta que originou este material foi: *"o que são desvio padrão, média, mediana, **erro**
> e outras medidas — o que elas significam na realidade?"*.
> Este é o arquivo que responde à parte mais difícil dela.

---

## 15.1 Erro não é engano

Em português comum, "erro" é falha: alguém fez algo errado. Em estatística e metrologia:

> **Erro é a diferença entre o valor obtido e o valor verdadeiro.**
> Ele existe mesmo quando todo mundo fez tudo certo, e é **inevitável**.

Pesar cinco vezes o mesmo saco de arroz na mesma balança dá cinco números diferentes.
Ninguém errou. Essa variação **é** o erro, e ela é mensurável, previsível em distribuição e
— em parte — controlável.

Toda a estatística inferencial existe porque o erro existe. Se medir fosse exato e se você
pudesse medir tudo, este curso teria três páginas.

---

## 15.2 A taxonomia que resolve 90% das confusões

### Os dois tipos fundamentais

| | **Erro aleatório** | **Erro sistemático (viés)** |
|---|---|---|
| Comportamento | varia a cada medição, ora para mais, ora para menos | erra sempre para o mesmo lado |
| Média de muitas medições | tende a zero | **permanece** |
| Como se mede | desvio padrão, erro padrão | comparação com um padrão de referência |
| Como se reduz | **medir mais vezes** | calibrar, mudar o método, corrigir o desenho |
| Está no seu IC? | ✅ sim | ❌ **não** |

```
   PRECISO e EXATO        PRECISO, não exato      EXATO, não preciso      nem um nem outro
   (pouco aleatório,      (pouco aleatório,       (muito aleatório,
    pouco viés)            MUITO VIÉS)             pouco viés)

      ┌───────┐              ┌───────┐              ┌───────┐              ┌───────┐
      │   ●●  │              │       │ ●●           │  ●    │              │●     ●│
      │  ●◎●  │              │   ◎   │●●●           │ ◎   ● │              │   ◎   │
      │   ●   │              │       │              │●   ●  │              │ ●   ● │
      └───────┘              └───────┘              └───────┘              └───────┘

    é o que se quer      ⚠️ O PIOR CASO:        números "ruins" mas    obviamente ruim,
                          parece confiável,      honestos — o IC        e por isso menos
                          e o IC estreito         cobre a verdade         perigoso
                          NÃO cobre a verdade
```

**O segundo quadro é o mais perigoso de todos** e merece uma frase própria:

> Um instrumento **preciso e enviesado** produz números com muitas casas decimais, desvio
> padrão pequeno e intervalo de confiança estreito — todos errados. Nenhuma quantidade de
> dados corrige isso, e todos os indicadores de qualidade estatística dizem que está ótimo.

Balança 200 g descalibrada, pesquisa por telefone fixo em 2026, sensor com deriva térmica,
questionário que induz a resposta, amostra de voluntários: todos produzem viés. **Mais dados
apenas tornam a resposta errada mais precisa.**

### Exatidão × precisão × justeza

Vocabulário do [VIM](https://www.bipm.org/en/committees/jc/jcgm/publications) (Vocabulário
Internacional de Metrologia), útil porque separa três coisas que o português mistura:

- **Precisão** (*precision*) — concordância entre medições repetidas. Só sobre o erro aleatório.
- **Justeza** (*trueness*) — proximidade da média das medições ao valor verdadeiro. Só sobre o viés.
- **Exatidão** (*accuracy*) — as duas juntas.

Um relatório que diz "nossa medição é precisa" está afirmando **muito menos** do que o leitor
entende.

### Uma taxonomia mais completa das fontes de erro

| Fonte | O que é | Mais dados resolvem? |
|---|---|---|
| **Erro de medição aleatório** | ruído do instrumento, do operador, do ambiente | ✅ sim |
| **Erro de medição sistemático** | calibração, deriva, método | ❌ não |
| **Erro amostral** | você olhou uma parte, não o todo | ✅ sim (com √n) |
| **Erro de cobertura** | sua lista de sorteio não contém toda a população | ❌ não |
| **Erro de não resposta** | quem responde difere de quem não responde | ❌ **não** |
| **Erro de processamento** | digitação, conversão, código | ❌ não (revisão resolve) |
| **Erro de especificação** | você mediu a coisa errada | ❌ não |
| **Erro de modelo** | a forma suposta não é a real | ❌ não |

> **Este quadro é a razão de a "margem de erro" ser tão mal compreendida.** Ela cobre apenas
> a linha "erro amostral". Todas as outras ficam de fora e não aparecem em número nenhum do
> relatório. Nas eleições americanas de 2016 e 2020, os erros das pesquisas foram muito
> maiores que as margens declaradas — não por amostras pequenas, mas por **não resposta
> diferencial**: certos perfis de eleitor atendiam menos ao telefone.

> **A regra que decorre disso, e que vale para a vida inteira:** *o erro que você consegue
> calcular quase nunca é o maior erro que você tem*. O número no relatório mede a parte fácil.

---

## 15.3 Desvio padrão × erro padrão — a confusão campeã

Esta é a confusão nº 1 em artigos publicados, relatórios de laboratório e apresentações
corporativas. Vale gastar uma página nela.

| | **Desvio padrão (DP, `s`)** | **Erro padrão da média (EP)** |
|---|---|---|
| Descreve a dispersão **de quê** | dos **dados** | da **média**, entre amostras |
| Fórmula | `√(Σ(xᵢ−x̄)²/(n−1))` | `s/√n` |
| Quando `n` cresce | **estabiliza** (converge para σ) | **diminui** (→ 0) |
| Responde a | "quão diferentes são os indivíduos?" | "quão bem conheço a média?" |
| Use em | descrever variabilidade | barra de erro, IC, teste |

### Medido

```python
import random, math, statistics as st
random.seed(314)

MU, SIGMA = 170.0, 8.0
print("populacao: alturas ~ N(170, 8) cm\n")
print(f"{'n':>6} {'DP das amostras':>16} {'DP das MEDIAS':>15} {'sigma/raiz(n)':>15}")
for n in [4, 10, 30, 100, 400]:
    REP = 4000
    medias, dps = [], []
    for _ in range(REP):
        am = [random.gauss(MU, SIGMA) for _ in range(n)]
        medias.append(sum(am) / n)
        dps.append(st.stdev(am))
    print(f"{n:>6} {st.mean(dps):>16.3f} {st.stdev(medias):>15.3f} {SIGMA/math.sqrt(n):>15.3f}")
```

```
populacao: alturas ~ N(170, 8) cm

     n  DP das amostras   DP das MEDIAS   sigma/raiz(n)
     4            7.405           3.963           4.000
    10            7.784           2.499           2.530
    30            7.917           1.451           1.461
   100            7.980           0.810           0.800
   400            7.992           0.393           0.400
```

Leia as duas colunas do meio lado a lado:

- **DP das amostras**: 7,4 → 7,8 → 7,9 → 8,0 → 8,0. **Estabiliza em σ = 8.** Faz sentido: as
  pessoas continuam tendo a mesma variedade de alturas, não importa quantas você meça.
- **DP das médias**: 3,96 → 2,50 → 1,45 → 0,81 → 0,39. **Cai sem parar**, e bate com `σ/√n`
  (última coluna) em todos os casos.

> **Uma frase para levar:** *o desvio padrão descreve as pessoas; o erro padrão descreve o
> quanto você sabe sobre elas.*

### Por que a confusão é sistemática, e não distração

Duas razões, e a segunda é desconfortável:

1. Os nomes e os símbolos são parecidos, e muitos softwares rotulam ambos como "±".
2. **O EP é sempre menor que o DP**, por um fator `√n`. Com `n = 100`, dez vezes menor.
   Barras de erro construídas com EP parecem dez vezes mais convincentes. Existe um incentivo
   silencioso para "confundir" sempre na mesma direção — e a literatura de metaciência mostra
   que a confusão de fato erra preferencialmente para esse lado.

**Regra de conduta:** toda vez que publicar `±`, escreva ao lado **o que é**: `(DP)`, `(EP)`,
`(IC95%)` ou `(amplitude)`. Quatro coisas diferentes, mesmo símbolo.

**Regra de escolha:**
- descrevendo **variabilidade** (quão diferentes são os pacientes/produtos/usuários) → **DP**;
- descrevendo **precisão da estimativa** (quão bem você conhece a média) → **EP** ou **IC**.

---

## 15.4 Intervalo de confiança: o que é e o que não é

### A construção

```
IC de 95% para a média:    x̄  ±  t₍₀,₉₇₅; n−1₎ · s/√n
```

Com `n` grande, `t → 1,96` e a fórmula vira `x̄ ± 1,96·EP`.

### O que ele significa (definição frequentista, e ela é escorregadia)

> **Se você repetisse todo o procedimento — sortear a amostra, calcular o intervalo —
> muitas vezes, 95% dos intervalos construídos conteriam o valor verdadeiro.**

A confiança é uma propriedade do **procedimento**, não deste intervalo específico. Depois de
calculado, o seu intervalo ou contém μ ou não contém; não há probabilidade envolvida, porque
μ não é aleatório.

### O que ele NÃO significa

| Interpretação comum | Está certa? |
|---|---|
| "há 95% de chance de μ estar neste intervalo" | ❌ tecnicamente errado (μ é fixo, não aleatório) |
| "95% dos dados estão neste intervalo" | ❌ **muito** errado — isso seria `x̄ ± 2s`, não `x̄ ± 2·EP` |
| "95% das médias futuras cairão aqui" | ❌ errado — isso seria um intervalo de **predição**, mais largo |
| "se o IC não contém zero, o efeito é importante" | ❌ significância ≠ importância |

> **Honestidade sobre a briga:** a interpretação "95% de chance de μ estar aqui" é o que quase
> todo mundo *quer* dizer, e é a interpretação correta do **intervalo de credibilidade
> bayesiano**, não do intervalo de confiança frequentista. Os dois costumam dar números muito
> parecidos na prática, com prior fraca. **Opinião declarada:** para comunicar a leigos, a
> distinção é quase sempre pedantismo que atrapalha; para escrever um artigo metodológico,
> é obrigatória. Saiba a diferença e escolha o registro conscientemente.

### Três intervalos que não são a mesma coisa

Confundi-los produz erro de ordem de grandeza:

| Intervalo | Fórmula (aprox.) | Responde a | Largura relativa |
|---|---|---|---|
| **de confiança** da média | `x̄ ± t·s/√n` | onde está a **média** verdadeira | mais estreito |
| **de predição** de uma nova observação | `x̄ ± t·s·√(1 + 1/n)` | onde cairá o **próximo** valor | muito mais largo |
| **de tolerância** | contém P% da população com confiança C% | onde está **a maioria** dos casos | mais largo ainda |

Com `n = 100`, `x̄ = 170` e `s = 8`: IC da média ≈ [168,4; 171,6]; intervalo de predição ≈
[154,1; 185,9]. **Dez vezes mais largo.** Um engenheiro que dimensionar uma porta pelo IC da
média projeta para a altura *média* da população, não para as pessoas.

### Por que a t, e não 1,96, com `n` pequeno — medido

```python
import random, math, statistics as st
random.seed(7)

MU, SIGMA = 170.0, 8.0
T = {3: 4.3027, 5: 2.7764, 10: 2.2622, 30: 2.0452, 100: 1.9842}
print("=== cobertura real de intervalos nominais de 95% (20.000 repeticoes) ===")
print(f"{'n':>5} {'com z=1,96':>12} {'com t':>8}")
for n in [3, 5, 10, 30, 100]:
    REP = 20000
    ok_z = ok_t = 0
    for _ in range(REP):
        am = [random.gauss(MU, SIGMA) for _ in range(n)]
        m = sum(am) / n
        ep = st.stdev(am) / math.sqrt(n)
        if abs(m - MU) <= 1.959964 * ep:
            ok_z += 1
        if abs(m - MU) <= T[n] * ep:
            ok_t += 1
    print(f"{n:>5} {100*ok_z/REP:>11.1f}% {100*ok_t/REP:>7.1f}%")
```

```
=== cobertura real de intervalos nominais de 95% (20.000 repeticoes) ===
    n   com z=1,96    com t
    3        80.9%    94.9%
    5        88.0%    95.0%
   10        91.8%    94.9%
   30        94.2%    95.1%
  100        94.6%    95.0%
```

**Com `n = 3`, um "intervalo de 95%" construído com 1,96 cobre a verdade em 80,9% das vezes.**
Você anuncia 5% de chance de errar e erra 19% — quase quatro vezes mais. Com a t, 94,9%:
correto.

Essa é exatamente a correção que Gosset fez em 1908, e é a demonstração de por que
[o projeto-modelo](07-projeto-modelo/README.md) implementou a t inteira em vez de usar 1,96.

---

## 15.5 Margem de erro e a lei da raiz quadrada

**Margem de erro** = metade da largura do IC, normalmente em proporções:

```
margem = z · √( p(1−p) / n )
```

Para 95% e o pior caso `p = 0,5`, isso vira aproximadamente:

```
margem ≈ 0,98 / √n          →     regra de bolso:  margem ≈ 1/√n
```

| n | margem (95%) | regra de bolso `1/√n` |
|---|---|---|
| 100 | 9,8 pp | 10,0 pp |
| 400 | 4,9 pp | 5,0 pp |
| 1.000 | 3,1 pp | 3,2 pp |
| 2.000 | 2,2 pp | 2,2 pp |
| 10.000 | 1,0 pp | 1,0 pp |

**Guarde `1/√n`.** Ela dá a margem de erro de qualquer pesquisa de opinião de cabeça, com erro
menor que 3%.

### Os dois fatos contraintuitivos

**1. Para dobrar a precisão, quadruplique a amostra.** Ver
[exemplo 6 do arquivo 06](06-exemplos.md): de ±2 pp para ±1 pp, de 2.401 para 9.604 pessoas.
É por isso que institutos param em torno de 2.000: depois disso, precisão custa caro demais.

**2. O tamanho da população quase não importa.** A fórmula não tem `N`. Uma amostra de 1.000
mede o Brasil (215 milhões) com a mesma precisão com que mede uma cidade de 50 mil.

> **Cinco porquês, até a parada.** *Por que a população não importa?* Porque a variância da
> média amostral é `σ²/n`, e não há `N` nessa expressão. *Por que não há?* Porque cada sorteio
> independente traz a mesma quantidade de informação, seja a população grande ou pequena.
> *Sempre?* Não: se você amostra **sem reposição** uma fração grande da população, entra a
> correção de população finita, `√((N−n)/(N−1))`. *Quando isso importa?* Quando `n/N > 5%` —
> amostrar 200 de uma empresa de 1.000 pessoas. *E se `n = N`?* A correção zera o erro
> amostral: você fez um **censo**, e não há mais erro de amostragem (embora os outros
> continuem todos lá). **Parada legítima: é uma consequência algébrica da variância da soma.**

A analogia da sopa continua sendo a melhor: para saber se está salgada, você mexe bem e prova
uma colher. O tamanho da panela não muda o tamanho da colher. **Mexer bem** — a amostra ser
realmente aleatória — é que muda tudo.

---

## 15.6 Propagação de incerteza

Você mede grandezas e combina. Como a incerteza se propaga?

| Operação | Combine | Por quê |
|---|---|---|
| `z = x ± y` | incertezas **absolutas** em quadratura: `u_z = √(u_x² + u_y²)` | variâncias somam |
| `z = x·y` ou `x/y` | incertezas **relativas** em quadratura: `u_z/z = √((u_x/x)² + (u_y/y)²)` | idem, em escala log |
| `z = xⁿ` | `u_z/z = \|n\|·u_x/x` | idem |
| `z = a·x` | `u_z = \|a\|·u_x` | escala |
| `z = f(x)` geral | `u_z ≈ \|f'(x)\|·u_x` | linearização (método delta) |

**Nunca some incertezas.** Somar supõe que os erros sempre conspiram na mesma direção — o
pior caso, não o caso típico. No [exemplo 13 do arquivo 06](06-exemplos.md), somar superestimou
a incerteza da área em 33%.

⚠️ **Tudo isso exige independência.** Se as medidas compartilham a mesma fonte de viés — mesma
trena, mesmo operador, mesma temperatura, mesmo modelo — há covariância, e a fórmula
**subestima**. Erro sistemático compartilhado nunca se cancela.

### Incerteza tipo A e tipo B (GUM)

O guia internacional [GUM](https://www.bipm.org/en/committees/jc/jcgm/publications)
(*Guide to the Expression of Uncertainty in Measurement*) classifica:

- **Tipo A** — avaliada por métodos **estatísticos**: você repetiu a medição e calculou `s/√n`.
- **Tipo B** — avaliada por **qualquer outro meio**: certificado de calibração do fabricante,
  resolução do instrumento, julgamento técnico, experiência.

A **incerteza combinada** junta as duas em quadratura; a **incerteza expandida** multiplica
pelo fator de abrangência `k` (tipicamente `k = 2`, para ~95%).

> **Por que isso importa fora do laboratório:** o GUM formaliza uma ideia que a estatística
> aplicada frequentemente ignora — que **incerteza que você não mediu ainda é incerteza**.
> A resolução da sua régua, o arredondamento do sistema, a definição ambígua da variável: tudo
> isso entra na conta, mesmo sem `n` para calcular. Ignorar tipo B e reportar apenas `s/√n` é
> declarar precisão que você não tem.

---

## 15.7 Algarismos significativos: não reporte precisão que você não tem

```python
>>> import statistics as st
>>> st.mean([1.62, 1.70, 1.58])
1.6333333333333335
```

Suas fitas métricas medem centímetros. Reportar `1,6333333333333335 m` afirma precisão de
0,1 nanômetro — cerca de um átomo.

**Regras práticas:**

1. O resultado não pode ter mais algarismos significativos que a **medida mais grosseira** que
   entrou nele.
2. Em multiplicação e divisão, o número de algarismos significativos do resultado é o do fator
   com menos.
3. Em soma e subtração, a **casa decimal** do resultado é a do termo menos preciso.
4. **Quando há incerteza calculada** (regra do GUM, e é a melhor): a incerteza fica com 1 ou 2
   algarismos significativos, e o valor é arredondado **na mesma casa**.
   `308,6100 ± 1,4078 m²` → `(308,6 ± 1,4) m²`.
5. Guarde todos os dígitos **durante** a conta; arredonde **só no fim**. Arredondar no meio
   propaga erro.

⚠️ E lembre-se de que o `round` do Python arredonda meio para o par (`round(2,5) = 2`,
`round(3,5) = 4`) e que `round(2.675, 2)` dá `2.67`, porque 2,675 não existe exatamente em
binário. Ver [75-armadilhas.md](75-armadilhas.md).

---

## 15.8 Viés e variância: o erro total se decompõe

Para um estimador `θ̂` de um parâmetro `θ`, o **erro quadrático médio** decompõe-se
exatamente em:

```
EQM(θ̂) = E[(θ̂ − θ)²] = Viés(θ̂)² + Var(θ̂)
                          └ sistemático ┘  └ aleatório ┘
```

Duas consequências grandes:

**1. Às vezes vale aceitar viés para reduzir variância.** Um estimador ligeiramente enviesado
com variância muito menor pode ter EQM menor — ou seja, **errar menos na prática** — que um
não enviesado. É o fundamento de regularização (ridge, lasso), de estimadores de encolhimento
(James-Stein) e de metade do aprendizado de máquina moderno.

**2. Não enviesado não é sinônimo de bom.** A obsessão com "não enviesado" é um hábito de
livro-texto; o que importa é o erro total. O [arquivo 60](60-teoria-avancada.md) trata disso
com rigor.

Em aprendizado de máquina, a mesma decomposição aparece como:

- **alto viés** = modelo simples demais = *underfitting*;
- **alta variância** = modelo complexo demais = *overfitting*;
- e há um terceiro termo, o **erro irredutível** — o ruído do próprio fenômeno, que nenhum
  modelo elimina. Prometer previsão melhor que o erro irredutível é vender o impossível.

---

## 15.9 Como relatar incerteza — um manual de meia página

| Situação | Forma correta |
|---|---|
| descrever variabilidade | `média 24,3 (DP 3,1; n = 40)` |
| precisão da estimativa | `24,3 (IC95% 23,3–25,3)` |
| dados assimétricos | `mediana 22 (IQR 18–27); p95 = 41; n = 40` |
| proporção | `42% (IC95% 39–45%), n = 1.200` |
| medição física | `(308,6 ± 1,4) m², k = 2 (~95%)` |
| comparação entre grupos | `diferença 4,2 (IC95% 0,8–7,6)` — **o IC da diferença**, não dois ICs |
| efeito nulo | `diferença 0,3 (IC95% −2,1 a 2,7)` — "não detectamos diferença; o estudo não exclui efeitos de até 2,7" |

**Cinco regras de conduta:**

1. **Nunca publique `±` sem dizer o que é.**
2. **Sempre publique `n`.** "4,7 estrelas" sem `n` é propaganda.
3. **Prefira IC a valor-p.** O IC contém o p e ainda mostra a magnitude e a precisão.
4. **Nunca escreva `p = 0,000`.** Escreva `p < 0,001`.
5. **"Não significativo" não é "não há efeito".** Diga qual efeito o seu estudo conseguiria
   detectar. Um estudo pequeno não detecta quase nada, e isso é uma limitação sua, não uma
   descoberta sobre o mundo.

> **A regra dos dois ICs sobrepostos** merece destaque porque erra na direção contrária ao
> intuitivo: dois intervalos que **se sobrepõem** podem, ainda assim, corresponder a uma
> diferença estatisticamente significativa. A comparação correta é sobre o IC **da diferença**,
> nunca sobre a sobreposição visual de dois ICs separados.

---

## 15.10 O checklist do relato honesto

Antes de publicar qualquer número, responda:

- [ ] Este número é uma **estimativa** ou o valor exato de uma população?
- [ ] Qual é o `n`?
- [ ] Qual é a incerteza, e ela está **rotulada**?
- [ ] Que fontes de erro **não** estão nessa incerteza (não resposta, cobertura, viés)?
- [ ] A precisão exibida corresponde à precisão real do instrumento?
- [ ] Se é comparação, calculei o IC **da diferença**?
- [ ] Se usei simulação, registrei a **semente**?
- [ ] Se a distribuição é assimétrica, estou relatando **mediana** em vez de média?
- [ ] Alguém que ler isso vai entender o que **não** foi medido?

---

## Autoteste

1. Sua balança marca 300 g a mais. Pesar 1.000 vezes e tirar a média resolve? Qual é o nome do
   problema?
2. Explique, em uma frase, a diferença entre DP e EP.
3. Por que o DP das amostras estabiliza em 8 enquanto o DP das médias cai para 0,39?
4. "Há 95% de chance de μ estar neste intervalo." Por que isso é tecnicamente errado, e por que
   quase todo mundo diz assim?
5. Com `n = 3`, um intervalo construído com 1,96 cobre a verdade quantas vezes em 100?
6. Uma pesquisa com 1.000 pessoas tem margem de ±3 pp. Qual a margem com 4.000? E com 250?
7. Por que a margem de erro quase não depende do tamanho da população — e quando ela depende?
8. Dois lados medidos com ±1% cada. Qual a incerteza relativa da área? Por que não 2%?
9. O que são incertezas tipo A e tipo B, e por que ignorar a tipo B é desonesto?
10. Você quer dimensionar uma porta. Usa o IC da média das alturas ou o intervalo de predição?
11. Escreva `308,6100 ± 1,4078 m²` como deve ser reportado.
12. Dois ICs se sobrepõem. A diferença é necessariamente não significativa?

<details><summary>Respostas</summary>

1. **Não.** É **erro sistemático (viés)**. A média de mil pesagens converge para "peso + 300 g"
   com precisão excelente e exatidão zero. Só calibração resolve.
2. O DP descreve o espalhamento **dos dados**; o EP descreve o espalhamento **da média entre
   amostras** — é o DP dividido por `√n`.
3. Porque a variedade das pessoas não muda com `n` (o DP estima σ, que é fixo), enquanto a
   média fica mais bem determinada a cada observação nova — sua dispersão é `σ/√n`.
4. Porque μ é **fixo**, não aleatório: depois de calculado, o intervalo contém ou não contém μ.
   A confiança é do procedimento. Todo mundo diz assim porque é a interpretação do **intervalo
   de credibilidade bayesiano**, que é o que se quer dizer — e que costuma dar quase o mesmo
   número.
5. **80,9 vezes** (medido em 20.000 repetições). Você anuncia 5% de erro e comete 19%.
6. Com 4.000: **±1,5 pp** (metade, por quadruplicar). Com 250: **±6 pp** (dobro, por dividir
   por 4).
7. Porque a variância da média amostral é `σ²/n` e não contém `N`. Ela **passa** a depender
   quando você amostra sem reposição uma fração grande da população (`n/N > 5%`): entra a
   correção de população finita `√((N−n)/(N−1))`.
8. `√(1² + 1²) ≈ 1,41%`. Não é 2% porque **variâncias** somam, não desvios — os erros são
   catetos de um triângulo retângulo.
9. **Tipo A** é avaliada estatisticamente (repetições, `s/√n`); **tipo B**, por outros meios
   (calibração, resolução do instrumento, julgamento). Ignorar a tipo B declara uma precisão
   que você não tem, porque incerteza que você não mediu continua existindo.
10. **Intervalo de predição** — e, rigorosamente, um **intervalo de tolerância** para o
    percentil alto da população. O IC da média projetaria a porta para a altura média, o que
    deixaria metade das pessoas de fora.
11. `(308,6 ± 1,4) m²` — a incerteza com 2 algarismos significativos, o valor arredondado na
    mesma casa.
12. **Não necessariamente.** Dois ICs sobrepostos ainda podem corresponder a diferença
    significativa. A comparação correta é o IC **da diferença**.

</details>

---

**Próximo:** [16-relacao-entre-variaveis.md](16-relacao-entre-variaveis.md) — covariância,
correlação e por que correlação não é causa.
