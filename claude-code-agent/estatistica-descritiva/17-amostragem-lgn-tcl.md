# 17. Amostragem, Lei dos Grandes Números e Teorema Central do Limite

`Nível: intermediário → avançado` · `Última atualização: 20/08/2026`
`Simulações executadas em Python 3.10.12 em 20/08/2026; saídas reais.`

> Por que uma colher basta para provar a sopa? Por que quase tudo, no fim, vira sino?
> E por que **mexer bem** importa mais que o tamanho da colher?

---

## 17.1 A pergunta que a amostragem responde

Você quer saber algo sobre 215 milhões de brasileiros e só pode falar com 2.000. A pergunta é:
**quando o pedaço representa o todo?**

Resposta curta e desconfortável: **quando o pedaço foi escolhido por sorteio, e não por
conveniência.** O tamanho vem depois — muito depois.

> **A sopa.** Para saber se a sopa está salgada, você **mexe bem** e prova **uma colher**.
> O tamanho da panela não muda o tamanho da colher necessária. Uma colher tirada da superfície
> de uma panela não mexida engana igualmente, seja a panela grande ou pequena.
> *Mexer bem = aleatorizar. Tamanho da colher = `n`.*

---

## 17.2 Tipos de amostragem

| Tipo | Como | Quando usar | Risco |
|---|---|---|---|
| **Aleatória simples** | todos com a mesma chance | quando existe uma lista completa | precisa da lista |
| **Sistemática** | a cada k-ésimo elemento | fila, linha de produção | 🚩 se houver periodicidade nos dados |
| **Estratificada** | sorteia dentro de subgrupos | grupos heterogêneos e conhecidos | precisa saber os estratos |
| **Por conglomerados** | sorteia grupos inteiros | dispersão geográfica, custo | 🚩 **aumenta** o erro |
| **Por cotas** | preenche cotas por perfil | pesquisa de mercado | ❌ **não é aleatória** |
| **Por conveniência** | quem estiver à mão | nunca, para inferir | ❌ viés desconhecido |
| **Voluntária** | quem quiser participar | nunca | ❌ pior de todas |

### As duas que merecem alerta explícito

**Amostragem por conglomerados aumenta o erro.** Se você sorteia 50 escolas e entrevista todos
os alunos de cada uma, os alunos da mesma escola se parecem entre si. Você tem, digamos,
5.000 questionários, mas muito menos informação **independente** do que 5.000 sorteios
individuais dariam. A perda é medida pelo **efeito de desenho** (*design effect*, `deff`), e o
tamanho de amostra **efetivo** é `n/deff`. Um `deff` de 2 significa que seus 5.000
questionários valem 2.500. Usar `s/√5000` nesse caso **subestima o erro pela metade**.

**Amostragem por cotas não é aleatória**, ainda que produza uma amostra "representativa" nos
perfis. O entrevistador escolhe *quem*, dentro da cota — e escolhe quem está disponível, quem
parece acessível, quem está no lugar em que ele está. As fórmulas de erro amostral **não se
aplicam**, embora sejam publicadas assim o tempo todo.

### A hierarquia dos vieses de seleção, do menor ao maior

1. **Sorteio perfeito com resposta total** — o ideal teórico, praticamente inexistente hoje.
2. **Sorteio com não resposta aleatória** — perde precisão, não introduz viés.
3. **Sorteio com não resposta diferencial** — 🚩 **viés**, e nenhuma fórmula o mede.
4. **Amostra por conveniência** — viés de tamanho desconhecido.
5. **Amostra voluntária** — quem se dá ao trabalho de responder é sistematicamente diferente.

> **O caso didático definitivo: o *Literary Digest*, 1936.** A revista enviou 10 milhões de
> cédulas e recebeu **2,4 milhões** de respostas — a maior pesquisa eleitoral já feita.
> Previu vitória folgada de Landon sobre Roosevelt. Roosevelt venceu com 61% dos votos, em
> uma das maiores goleadas da história americana. George Gallup, com **50 mil** entrevistados
> sorteados, acertou.
>
> Dois erros somados: a lista vinha de registros de telefone e de automóveis (viés de
> cobertura, em plena Depressão) e apenas quem se dispôs a responder respondeu (viés de não
> resposta). **2,4 milhões de respostas enviesadas perderam para 50 mil aleatórias.**
> Noventa anos depois, o erro se repete toda vez que alguém posta uma enquete no LinkedIn e
> trata o resultado como dado.

---

## 17.3 Lei dos Grandes Números — a média converge

> **LGN:** conforme `n` cresce, a média amostral converge para a média populacional.

```python
import random
random.seed(8)

soma = 0.0
for n in range(1, 1000001):
    soma += random.expovariate(1.0)          # media verdadeira = 1
    if n in (10, 100, 1000, 10000, 100000, 1000000):
        print(f"  n={n:>9}: media acumulada = {soma/n:.5f}   (verdadeira = 1)")
```

```
  n=       10: media acumulada = 1.41853   (verdadeira = 1)
  n=      100: media acumulada = 0.94538   (verdadeira = 1)
  n=     1000: media acumulada = 1.01464   (verdadeira = 1)
  n=    10000: media acumulada = 0.99382   (verdadeira = 1)
  n=   100000: media acumulada = 0.99549   (verdadeira = 1)
  n=  1000000: media acumulada = 0.99969   (verdadeira = 1)
```

### Três coisas que a LGN **não** diz

1. **Não diz que a convergência é rápida.** Com `n = 10` ainda estávamos 42% acima. A taxa é
   `1/√n`, que é **lenta**: para ganhar um dígito de precisão, você precisa de 100× mais dados.
2. **Não vale sempre.** Exige que a média exista. Com Cauchy, a média **não converge nunca**
   ([arquivo 14](14-forma-e-distribuicoes.md)). Com caudas muito pesadas, a convergência é tão
   lenta que na prática não acontece.
3. **Não corrige viés.** A LGN garante convergência para a média **da distribuição de onde
   você amostrou**. Se você amostrou da distribuição errada — só quem atende o telefone —
   converge lindamente para a resposta errada.

> **A falácia do apostador é o inverso da LGN.** Ela não diz que resultados passados serão
> "compensados". Se saírem 10 caras seguidas, a moeda não "deve" coroas. O que acontece é que
> os 10 excedentes são **diluídos** por milhões de lançamentos futuros, não cancelados.
> A LGN opera por diluição, não por compensação.

---

## 17.4 Teorema Central do Limite — quase tudo vira sino

> **TCL:** a soma (ou média) de muitas variáveis independentes, com variância finita, tende à
> distribuição **normal** — **qualquer que seja a distribuição de origem**.

### Medido, partindo de uma distribuição bem torta

```python
import random, math, statistics as st

def assim(d):
    n = len(d); m = st.mean(d); s = st.stdev(d)
    return (n / ((n-1)*(n-2))) * sum(((x-m)/s)**3 for x in d)

random.seed(2024)
REP = 20000
print("populacao MUITO assimetrica: exponencial(1) -- assimetria teorica 2, media 1\n")
for n in [1, 2, 5, 30, 100]:
    medias = [sum(random.expovariate(1.0) for _ in range(n)) / n for _ in range(REP)]
    print(f"n={n:>4}: media das medias={st.mean(medias):.4f}  DP={st.stdev(medias):.4f} "
          f"(teorico {1/math.sqrt(n):.4f})  assimetria={assim(medias):+.3f}")
```

```
populacao MUITO assimetrica: exponencial(1) -- assimetria teorica 2, media 1

n=   1: media das medias=1.0148  DP=1.0202 (teorico 1.0000)  assimetria=+2.025
n=   2: media das medias=0.9982  DP=0.7029 (teorico 0.7071)  assimetria=+1.372
n=   5: media das medias=1.0026  DP=0.4467 (teorico 0.4472)  assimetria=+0.910
n=  30: media das medias=0.9984  DP=0.1816 (teorico 0.1826)  assimetria=+0.379
n= 100: media das medias=0.9993  DP=0.0994 (teorico 0.1000)  assimetria=+0.176
```

A assimetria vai de **+2,03 → +1,37 → +0,91 → +0,38 → +0,18**. Ela some proporcionalmente a
`1/√n`, exatamente como a teoria prevê. E o desvio padrão bate com `σ/√n` em todos os casos,
até a terceira casa.

Nos histogramas, o efeito é visível:

```
histograma das medias com n=1 (a propria exponencial):     histograma das medias com n=30:
      0.000 | ########################################          0.403 |
      1.046 | ##############                                    0.539 | ###
      2.091 | #####                                             0.675 | ##################
      3.137 | ##                                                0.811 | ######################################
      4.183 | #                                                 0.947 | ########################################
      5.228 |                                                   1.083 | ############################
      6.274 |                                                   1.219 | ############
      7.320 |                                                   1.355 | ####
      8.365 |                                                   1.491 | #
      9.411 |                                                   1.627 |
     10.457 |                                                   1.763 |
```

Uma curva que decai desde a origem virou um sino. **Nenhuma suposição sobre a origem foi
feita.**

### Por que isso é o teorema mais importante da estatística

Ele explica por que a normal está em toda parte **sem que ninguém tenha decidido isso**:
altura, erro de medição, ruído elétrico, resultado de qualquer processo aditivo. Tudo que é
**soma de muitos efeitos pequenos e independentes** converge para o sino.

E ele é o que autoriza a inferência: mesmo com dados de distribuição desconhecida, **a
distribuição da média é conhecida** — e a média é sobre o que queremos falar.

> **Cinco porquês.** *Por que somas viram normal?* Porque somar variáveis independentes
> corresponde a **convolver** suas distribuições, e a convolução repetida suaviza qualquer
> irregularidade. *Por que suaviza?* Porque cada convolução é uma média móvel ponderada, que
> apaga detalhes finos. *Por que converge para a normal, e não para outra coisa?* Porque a
> normal é o **ponto fixo** dessa operação: a convolução de duas normais é normal, e ela é a
> única forma estável com variância finita. *E se a variância for infinita?* Aí converge para
> outra família — as **distribuições estáveis de Lévy**, das quais a normal é o caso de
> variância finita e a Cauchy é outro caso. **Parada legítima: é um teorema de ponto fixo,
> não uma convenção.**

### Os limites do TCL — onde o "n ≥ 30" mente

A regra "n ≥ 30 basta" é ensinada como se fosse lei. **É uma regra de bolso, e ela falha:**

| Situação | `n` realmente necessário |
|---|---|
| população já quase simétrica | 5 a 10 |
| assimetria moderada (exponencial) | ~30 (a assimetria em `n=30` ainda foi +0,38) |
| assimetria forte (log-normal com σ alto) | centenas a milhares |
| proporções com `p` extremo (p = 0,01) | `n·p ≥ 10` → aqui, `n ≥ 1.000` |
| **cauda pesada com variância infinita** | **nunca converge** |
| dados **dependentes** (série temporal) | o TCL clássico não se aplica |

A regra do `n·p ≥ 10` merece destaque porque é violada rotineiramente: para estimar a
prevalência de algo que ocorre em 1% dos casos, `n = 100` dá em média **um** caso positivo, e
nenhuma normal descreve isso. Use intervalos exatos (Clopper-Pearson) ou Wilson.

---

## 17.5 De onde vem `EP = σ/√n`

Álgebra pura, em quatro linhas, usando só que **variâncias de independentes somam**
([arquivo 13](13-medidas-de-dispersao.md), §13.7):

```
x̄ = (1/n)·(x₁ + x₂ + … + xₙ)

Var(x̄) = (1/n²)·Var(x₁ + … + xₙ)        [Var(a·X) = a²·Var(X)]
        = (1/n²)·(σ² + σ² + … + σ²)      [independência: variâncias somam]
        = (1/n²)·(n·σ²)
        = σ²/n

DP(x̄) = σ/√n
```

**Aí está toda a lei da raiz quadrada.** O `√` aparece porque somamos **variâncias** (não
desvios) e depois tiramos a raiz uma única vez no final.

Duas consequências que decorrem disso e nada mais:

- **Quadruplicar `n` reduz o erro pela metade.**
- **`N` não aparece na conta** — o tamanho da população é irrelevante, exceto quando se amostra
  sem reposição uma fração grande dela (correção de população finita, `n/N > 5%`).

⚠️ **A palavra "independência" carrega tudo.** Em série temporal, em conglomerados, em medidas
repetidas do mesmo indivíduo, os dados **não** são independentes, as variâncias não somam
simplesmente, e `σ/√n` **subestima** o erro — às vezes por um fator grande. Este é
provavelmente o erro de inferência mais comum em dados de sistemas e de negócios: tratar
5.000 requisições da mesma hora como 5.000 observações independentes.

---

## 17.6 Quanto `n` eu preciso?

### Para estimar uma proporção com margem `m`

```
n = p(1−p)·(z/m)²        com p = 0,5 no pior caso  →  n ≈ (z/2m)²  ≈  1/m²
```

| Margem desejada | `n` (95%, pior caso) |
|---|---|
| ±10 pp | 97 |
| ±5 pp | 385 |
| ±3 pp | 1.068 |
| ±2 pp | 2.401 |
| ±1 pp | 9.604 |

### Para estimar uma média com margem `m`

```
n = (z·σ/m)²
```

Exige um palpite de `σ`. De onde tirar? De um estudo-piloto, da literatura, ou da regra de
bolso `σ ≈ amplitude/4` (que vem da regra dos 95% em ±2σ).

### Para detectar uma diferença (cálculo de poder)

```
n por grupo ≈ 16/d²      onde d = diferença / desvio padrão (d de Cohen),
                         para 80% de poder e α = 0,05
```

| `d` (tamanho do efeito) | `n` por grupo |
|---|---|
| 0,2 (pequeno) | ~400 |
| 0,5 (médio) | ~64 |
| 0,8 (grande) | ~25 |

> **Faça este cálculo ANTES de coletar.** Um estudo com poder de 30% desperdiça o trabalho de
> todo mundo: se o efeito existir, você provavelmente não o detectará; e se detectar, o efeito
> estimado estará **superestimado** (só passam no filtro da significância as estimativas
> exageradas — é o "erro tipo M", de magnitude, de Gelman e Carlin). Análise de poder *depois*
> de um resultado não significativo (*post hoc power*) é matematicamente vazia: é apenas uma
> retradução do valor-p.

---

## 17.7 Bootstrap: a alternativa quando não há fórmula

Quando a estatística de interesse não é a média — mediana, quartil, razão, coeficiente de
Gini, diferença entre percentis — não há `σ/√n` para usar.

O **bootstrap** ([exemplo 7 do arquivo 06](06-exemplos.md)) resolve por simulação: trate a
amostra como população, reamostre com reposição, veja o quanto a estatística varia.

**O que ele supõe, e é preciso dizer:**

- que a **amostra representa a população** (se houver viés de seleção, o bootstrap o reproduz
  fielmente — ele não conserta nada);
- que as observações são **independentes** (para séries temporais existe o *block bootstrap*);
- que `n` não é minúsculo (com `n < 10`, o bootstrap é instável, e para medidas discretas dá
  intervalos "em degraus").

**O que ele não supõe:** nenhuma forma de distribuição. É essa a virtude.

---

## 17.8 Checklist de amostragem

- [ ] A amostra foi **sorteada**, ou é conveniência disfarçada?
- [ ] Qual é a **população-alvo**, e a minha lista de sorteio a cobre? (erro de cobertura)
- [ ] Qual foi a **taxa de resposta**? Quem não respondeu difere de quem respondeu?
- [ ] Há **conglomerados** ou dependência? Calculei o efeito de desenho?
- [ ] Usei **pesos**? Então `s/√n` não vale.
- [ ] Fiz o cálculo de tamanho **antes** de coletar?
- [ ] A margem que vou publicar cobre só o erro **amostral** — e eu disse isso?

---

## Autoteste

1. Por que 2,4 milhões de respostas erraram e 50 mil acertaram em 1936?
2. Enuncie a Lei dos Grandes Números e diga três coisas que ela **não** garante.
3. A média de exponenciais com `n=30` teve assimetria +0,38. O que isso mostra sobre "n ≥ 30"?
4. Derive `EP = σ/√n` em quatro linhas.
5. Por que o tamanho da população não entra na fórmula do erro — e quando entra?
6. Você amostra 50 escolas e entrevista todos os alunos. Por que `s/√n` está errado?
7. Amostragem por cotas é aleatória? Pode-se publicar margem de erro?
8. Quantas pessoas para margem de ±2 pp? E de ±1 pp?
9. O que é "erro tipo M" e por que ele torna estudos de baixo poder perigosos?
10. O bootstrap dispensa quais suposições — e quais ele **não** dispensa?

<details><summary>Respostas</summary>

1. Porque as 2,4 milhões vieram de uma lista enviesada (donos de telefone e automóvel em plena
   Depressão) **e** de quem se dispôs a responder. Viés de cobertura + não resposta. As 50 mil
   de Gallup foram **sorteadas**. Tamanho não compensa viés.
2. **LGN:** a média amostral converge para a média populacional conforme `n` cresce. **Não**
   garante: convergência rápida (é `1/√n`); convergência sempre (falha se a média não existir,
   como na Cauchy); correção de viés (converge para a média da distribuição de onde você
   realmente amostrou).
3. Que "n ≥ 30" é regra de bolso, não teorema. Com assimetria de origem igual a 2, `n = 30`
   ainda deixa +0,38 de assimetria na distribuição da média. Com assimetria forte, é preciso
   centenas ou milhares.
4. `Var(x̄) = Var(Σxᵢ/n) = (1/n²)Var(Σxᵢ) = (1/n²)(nσ²) = σ²/n`; logo `DP(x̄) = σ/√n`.
   O passo crítico é `Var(Σxᵢ) = nσ²`, que exige **independência**.
5. Porque `Var(x̄) = σ²/n` não contém `N`: cada sorteio independente carrega a mesma informação.
   `N` entra quando se amostra **sem reposição** uma fração grande da população (`n/N > 5%`),
   via a correção de população finita.
6. Porque alunos da mesma escola se parecem: as observações **não são independentes**. O
   tamanho efetivo é `n/deff`, e usar `n` bruto subestima o erro.
7. **Não** é aleatória — o entrevistador escolhe quem, dentro da cota. As fórmulas de erro
   amostral não se aplicam, embora sejam publicadas assim rotineiramente.
8. ±2 pp: **2.401**. ±1 pp: **9.604**. Quadruplicar `n` para dobrar a precisão.
9. **Erro tipo M (magnitude):** quando o poder é baixo, apenas as estimativas exageradas
   ultrapassam o limiar de significância. O efeito publicado é, portanto, sistematicamente
   **superestimado** — e a literatura resultante engana mesmo sem nenhuma fraude.
10. **Dispensa** qualquer suposição sobre a forma da distribuição. **Não dispensa**: que a
    amostra represente a população (viés de seleção é reproduzido fielmente), que as
    observações sejam independentes, e que `n` não seja minúsculo.

</details>

---

**Próximo:** [18-inferencia-p-e-ic.md](18-inferencia-p-e-ic.md) — o valor-p, o que ele é, e as
seis coisas que ele não é.
