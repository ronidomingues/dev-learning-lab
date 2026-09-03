# 70. Prática — 14 laboratórios com as mãos

`Nível: iniciante → avançado` · `Última atualização: 20/08/2026`
`Tudo roda em Python 3.10+ com a biblioteca padrão. Nada a instalar.`

> Ler sobre desvio padrão não ensina desvio padrão. **Simular** ensina.
> Cada laboratório tem: objetivo, roteiro, o que você deve observar, e um gabarito
> comentado. Faça antes de olhar o gabarito — a surpresa é o mecanismo de aprendizagem aqui.

| # | Laboratório | Ensina | Tempo |
|---|---|---|---|
| 1 | A gangorra | por que a média é o ponto de equilíbrio | 15 min |
| 2 | O detetive de assimetria | média × mediana como diagnóstico | 20 min |
| 3 | Mil moedas | intuição de aleatoriedade; LGN | 25 min |
| 4 | Fábrica de médias | 🔑 TCL e `EP = σ/√n` na tela | 40 min |
| 5 | O `n−1` que você não acreditava | correção de Bessel medida | 30 min |
| 6 | Quebrando estimadores | ponto de ruptura | 30 min |
| 7 | Bootstrap caseiro | IC de qualquer coisa | 40 min |
| 8 | O IC que mente | cobertura real × nominal | 40 min |
| 9 | Sua própria fábrica de p-hacking | como se produz falso positivo | 45 min |
| 10 | Simpson na sua mão | construir o paradoxo do zero | 40 min |
| 11 | O detector de outlier que erra | 1,5×IQR em dados assimétricos | 30 min |
| 12 | Dados reais do IBGE | análise completa ponta a ponta | 90 min |
| 13 | Auditoria de gráfico | ler visualização criticamente | 45 min |
| 14 | Reescreva um relatório | comunicar com honestidade | 60 min |

---

## Lab 1 — A gangorra (15 min)

**Objetivo:** sentir que a média é um ponto de equilíbrio físico, e a mediana não.

**Roteiro.**
1. Escreva uma função `desequilibrio(dados, c)` que devolva `sum(x - c for x in dados)`.
2. Para `dados = [2, 4, 9]`, teste `c` de 0 a 10 em passos de 0,5 e imprima o desequilíbrio.
3. Ache o `c` em que o desequilíbrio é zero.
4. Repita com `dados = [2, 4, 900]`.

**Observe:** o ponto de equilíbrio é sempre exatamente a média, e ele **sai de dentro do
intervalo onde estão a maioria dos dados** quando há um valor extremo.

**Extensão:** faça o mesmo com `sum(abs(x - c) ...)` e verifique que o mínimo cai na mediana.

<details><summary>Gabarito</summary>

```python
def desequilibrio(dados, c):
    return sum(x - c for x in dados)

for d in ([2, 4, 9], [2, 4, 900]):
    print("dados:", d)
    for i in range(0, 21):
        c = i * 0.5
        v = desequilibrio(d, c)
        print(f"   c={c:5.1f}  desequilibrio={v:+10.1f}" + ("   <== EQUILIBRIO" if abs(v) < 1e-9 else ""))
```
Com `[2,4,9]` o zero está em `c = 5`; com `[2,4,900]`, em `c = 302`. Repare que 302 não está
perto de nenhum dos três valores — a média deixou de descrever o conjunto.
</details>

---

## Lab 2 — O detetive de assimetria (20 min)

**Objetivo:** transformar a razão média/mediana num alarme automático.

**Roteiro.**
1. Escreva `diagnostico(dados)` que devolva média, mediana, razão, e uma frase de veredito
   (`"simétrico"`, `"assimétrico à direita"`, `"assimétrico à esquerda"`).
2. Teste com: salários do [exemplo 1](06-exemplos.md); alturas do [arquivo 04](04-como-comecar.md);
   `[1,2,3,4,5]`; `[1,2,3,4,100]`; `[-100,4,5,6,7]`.
3. Ajuste os limiares até que os vereditos batam com a sua intuição visual.

**Observe:** a razão é um detector muito mais barato e mais confiável que o coeficiente de
assimetria com `n` pequeno — e você acabou de reimplementar o principal aviso do
[projeto-modelo](07-projeto-modelo/README.md).

---

## Lab 3 — Mil moedas (25 min)

**Objetivo:** destruir a intuição errada de aleatoriedade.

**Roteiro.**
1. Escreva, **de cabeça**, uma sequência de 100 caras e coroas que "pareça aleatória". Guarde.
2. Gere 100 lançamentos de verdade com `random.choice("KC")`.
3. Para as duas sequências, calcule: a maior sequência de repetições consecutivas.
4. Simule 100.000 sequências de 100 lançamentos e veja a distribuição da maior repetição.

**Observe:** sequências inventadas por humanos quase nunca têm repetições de 6 ou mais. Em
100 lançamentos reais, a maior repetição é tipicamente de **6 ou 7**, e passar de 5 é o caso
comum, não a exceção. É assim que se detecta dado fabricado.

<details><summary>Gabarito parcial</summary>

```python
import random
random.seed(1)

def maior_sequencia(s):
    melhor = atual = 1
    for i in range(1, len(s)):
        atual = atual + 1 if s[i] == s[i-1] else 1
        melhor = max(melhor, atual)
    return melhor

from collections import Counter
c = Counter(maior_sequencia([random.choice("KC") for _ in range(100)]) for _ in range(100000))
for k in sorted(c):
    print(f"  maior sequencia = {k:2d}: {100*c[k]/100000:5.2f}%")
```
</details>

---

## Lab 4 — 🔑 Fábrica de médias (40 min)

**O laboratório mais importante deste arquivo.** Se você fizer só um, faça este.

**Objetivo:** ver o Teorema Central do Limite e `EP = σ/√n` acontecerem.

**Roteiro.**
1. Escolha uma população **feia**: `random.expovariate(1)` ou `random.paretovariate(2)`.
2. Para `n` em `[1, 2, 5, 10, 30, 100, 400]`:
   - gere 20.000 amostras de tamanho `n` e guarde a **média** de cada uma;
   - calcule média das médias, desvio padrão das médias, e assimetria das médias;
   - compare o desvio padrão das médias com `σ/√n`.
3. Desenhe um histograma ASCII das médias para `n = 1` e `n = 30`.

**Observe:**
- a média das médias fica sempre em `μ` (não enviesada, para qualquer `n`);
- o desvio padrão das médias bate com `σ/√n` até a terceira casa;
- a assimetria some proporcionalmente a `1/√n`;
- **o histograma vira sino**, partindo de uma distribuição que não se parece nada com sino.

**Extensão importante:** repita com uma população **Cauchy**
(`math.tan(math.pi*(random.random()-0.5))`) e veja que **nada disso acontece**. Descubra por
quê em [14-forma-e-distribuicoes.md](14-forma-e-distribuicoes.md).

Código de referência em [17-amostragem-lgn-tcl.md](17-amostragem-lgn-tcl.md), §17.4.

---

## Lab 5 — O `n−1` que você não acreditava (30 min)

**Objetivo:** provar para si mesmo a correção de Bessel.

**Roteiro.**
1. Fixe `μ = 100`, `σ = 15`, então `σ² = 225`.
2. Para `n = 2`: gere 200.000 amostras. Para cada uma, calcule `Σ(xᵢ−x̄)²` e divida por `n` e
   por `n−1`. Tire a média das duas séries.
3. Repita para `n = 3, 5, 10, 30, 100`.
4. Acrescente uma terceira coluna: a média de `s = √(Σ(xᵢ−x̄)²/(n−1))`.

**Observe:**
- `/n` subestima sistematicamente, e com `n=2` dá exatamente **metade**;
- `/(n−1)` acerta 225 para todo `n` — isso é "não viesado" em ação;
- **mas `s` continua abaixo de 15**, mesmo com `n−1`. Descubra por quê em
  [60-teoria-avancada.md](60-teoria-avancada.md), §60.2.

Código em [13-medidas-de-dispersao.md](13-medidas-de-dispersao.md), §13.3.

---

## Lab 6 — Quebrando estimadores (30 min)

**Objetivo:** medir ponto de ruptura.

**Roteiro.**
1. Gere 1.000 valores de `N(100, 10)`.
2. Substitua `k%` deles por `10⁶`, para `k` em `[0, 1, 5, 10, 20, 30, 40, 49, 51]`.
3. Para cada nível, calcule: média, mediana, desvio padrão, MAD, média aparada a 10%,
   média aparada a 25%.
4. Monte a tabela.

**Observe:** cada estimador quebra **exatamente** no seu ponto de ruptura teórico. A aparada
a 10% aguenta 10%; a 25%, aguenta 25%; mediana e MAD aguentam até 49% e desmoronam em 51%.

Código em [19-robustez-e-outliers.md](19-robustez-e-outliers.md), §19.2.

---

## Lab 7 — Bootstrap caseiro (40 min)

**Objetivo:** obter IC para qualquer estatística.

**Roteiro.**
1. Escreva `bootstrap(dados, estatistica, B=10000, semente=42)` que devolva a lista de valores
   reamostrados.
2. Aplique a: média, mediana, desvio padrão, **coeficiente de variação**, **razão p90/p50**.
3. Para cada uma, calcule o IC percentílico de 95%.
4. Compare o IC bootstrap da média com o IC pela fórmula da t. Devem ser parecidos.
5. **Teste de falha:** aplique o bootstrap ao **máximo** dos dados. Olhe o resultado.

**Observe:** para a média, bootstrap e fórmula concordam — bom sinal. Para o máximo, o
bootstrap dá um resultado **claramente errado**: o limite superior do IC é sempre o próprio
máximo observado, porque nenhuma reamostra pode conter um valor maior. É o caso de
inconsistência de [60-teoria-avancada.md](60-teoria-avancada.md), §60.7, e vê-lo falhar vale
mais que ler sobre.

---

## Lab 8 — O IC que mente (40 min)

**Objetivo:** medir a diferença entre confiança nominal e cobertura real.

**Roteiro.**
1. Fixe `μ` conhecido. Para `n` em `[3, 5, 10, 30, 100]`, gere 20.000 amostras.
2. Para cada amostra, construa o IC de 95% de duas formas: com `1,96` e com o `t` correto.
3. Conte a fração de intervalos que contêm `μ`.
4. **Repita com população exponencial** em vez de normal.

**Observe:** com normal e `n=3`, o método com 1,96 cobre 81% em vez de 95%. Com população
**exponencial**, mesmo o `t` fica abaixo do nominal para `n` pequeno — porque a t supõe
normalidade da população, não só do estimador.

Código em [15-erro-e-incerteza.md](15-erro-e-incerteza.md), §15.4.

---

## Lab 9 — Sua própria fábrica de p-hacking (45 min)

**Objetivo:** produzir falsos positivos deliberadamente, para reconhecê-los depois.

**Roteiro.** Com dois grupos **idênticos** (nenhum efeito real), meça a taxa de falso positivo
sob cada estratégia:

| Estratégia | Taxa esperada se honesto |
|---|---|
| a) `n` fixo, um teste | 5% |
| b) espiar a cada 5 e parar quando der | 5% |
| c) testar 10 variáveis e reportar a melhor | 5% |
| d) testar 3 subgrupos | 5% |
| e) remover outliers só se ajudar | 5% |
| f) **todas juntas** | 5% |

**Observe:** cada item sozinho já eleva a taxa; combinados, ela passa de 50%. Nenhuma etapa
individual parece desonesta. Este é o argumento inteiro de Simmons, Nelson & Simonsohn (2011),
e você o reproduziu.

Código parcial em [18-inferencia-p-e-ic.md](18-inferencia-p-e-ic.md), §18.3.

---

## Lab 10 — Simpson na sua mão (40 min)

**Objetivo:** construir o paradoxo do zero, para nunca mais ser surpreendido por ele.

**Roteiro.**
1. Crie dois grupos (fácil/difícil) e dois tratamentos (A/B).
2. Escolha as taxas de sucesso de modo que **A vença em ambos os grupos**.
3. Escolha os tamanhos de cada célula de modo que **B vença no agregado**.
4. Verifique numericamente.
5. Agora **inverta**: mantenha as taxas e mude só os tamanhos, de modo que A também vença no
   agregado.

**Observe:** as taxas nunca mudaram. Só os **pesos**. O paradoxo é média ponderada
([arquivo 12](12-medidas-de-posicao.md), §12.7) com uma interpretação causal em cima.

**Pergunta final, sem resposta única:** você construiu os números. Qual é a resposta certa —
o estrato ou o agregado? Escreva a sua justificativa em três linhas e compare com
[16-relacao-entre-variaveis.md](16-relacao-entre-variaveis.md), §16.7.

---

## Lab 11 — O detector de outlier que erra (30 min)

**Objetivo:** medir a taxa de falso alarme da regra de Tukey.

**Roteiro.**
1. Gere 200.000 valores de: normal, uniforme, exponencial, log-normal.
2. Para cada conjunto (**todos limpos, sem nenhum outlier de verdade**), conte a fração marcada
   pela cerca `1,5×IQR` e pela `3×IQR`.
3. Repita aplicando a cerca **ao logaritmo** dos dados positivos.

**Observe:** 0,71% na normal (o valor para que Tukey calibrou) contra 7,74% na log-normal.
E ao aplicar no log, a taxa da log-normal cai para perto de 0,7% — o que mostra que o problema
nunca foi dos dados, foi da suposição de simetria embutida na régua.

Código em [19-robustez-e-outliers.md](19-robustez-e-outliers.md), §19.3.

---

## Lab 12 — Dados reais, ponta a ponta (90 min)

**Objetivo:** fazer uma análise completa com dados públicos, incluindo a parte suja.

**Roteiro.**
1. Baixe um conjunto real, pequeno e público. Sugestões brasileiras:
   - **IBGE / SIDRA** — <https://sidra.ibge.gov.br> (população, renda, PIB municipal)
   - **Portal Brasileiro de Dados Abertos** — <https://dados.gov.br>
   - **DATASUS / TabNet** — <https://datasus.saude.gov.br>
   - **INEP** — microdados do ENEM e do Censo Escolar
   - **Portal da Transparência** — <https://portaldatransparencia.gov.br>
2. Escolha **uma** variável numérica e responda, por escrito:
   - qual é a **unidade de observação**? é a certa para a pergunta?
   - quantas linhas você perdeu na leitura, e por quê?
   - a distribuição é assimétrica? qual é a razão média/mediana?
   - há outliers? de que tipo (erro, unidade, outra população, cauda)?
   - qual é a incerteza da sua estimativa? isso é população ou amostra?
3. Rode o [projeto-modelo](07-projeto-modelo/README.md) sobre o arquivo e **compare os avisos
   dele com o seu próprio diagnóstico**.
4. Escreva **três frases** que descrevem os dados honestamente.

**Observe:** com dados reais, 80% do trabalho é limpeza e decisão, não cálculo. É assim mesmo,
e nenhum curso que use só dados sintéticos prepara para isso.

> ⚠️ Praticamente todo dado municipal brasileiro é assimétrico com cauda pesada, porque São
> Paulo existe. Com ~5.570 municípios e ~203 milhões de habitantes (Censo 2022), a **média** de
> população municipal fica em torno de 36 mil, enquanto a **mediana** fica na casa dos 11 mil
> (número aproximado — confira na fonte). Relatar a média como "município típico" erra por um
> fator próximo de 3. Confirme os dois números com os dados que você baixar: é o primeiro
> exercício deste laboratório.

---

## Lab 13 — Auditoria de gráfico (45 min)

**Objetivo:** treinar leitura crítica de visualização.

**Roteiro.** Encontre **cinco** gráficos publicados (jornal, relatório de empresa, artigo,
rede social). Para cada um, responda:

1. O eixo Y começa em zero? Deveria?
2. O `n` está informado?
3. Se há `±`, está dito o que é?
4. A escala é linear ou log? Está marcado?
5. Se é mapa, mostra contagem ou taxa?
6. Se compara grupos, os grupos são comparáveis?
7. **Qual gráfico diferente mostraria o mesmo dado de forma mais honesta?**

**Observe:** a pergunta 7 é a que mais ensina. Redesenhar mentalmente é como se aprende a
desenhar.

---

## Lab 14 — Reescreva um relatório (60 min)

**Objetivo:** o produto final de todo este curso é uma frase honesta.

**Roteiro.**
1. Pegue um trecho real com números — release de empresa, matéria de jornal, resumo de artigo.
2. Liste tudo que **falta**: `n`, incerteza, definição da medida, denominador, período,
   comparações não declaradas.
3. Reescreva o trecho de forma honesta.
4. Compare o tamanho dos dois textos.

**Observe:** o texto honesto é tipicamente **50 a 100% mais longo**, e é isso que explica boa
parte da desonestidade estatística: honestidade custa espaço e atenção do leitor.

**Exemplo, para calibrar:**

> ❌ "Nosso produto aumentou a produtividade em 40%."
>
> ✅ "Em um piloto com 12 equipes durante 6 semanas, a mediana de tarefas concluídas por
> semana subiu de 20 para 28 (+40%; IC95% de +12% a +71%). Não houve grupo de controle, então
> parte do ganho pode vir de efeito de novidade ou de regressão à média — as equipes
> escolhidas para o piloto tinham desempenho abaixo da média."

Repare que a segunda versão continua sendo uma boa notícia. Ela só é uma boa notícia
**verificável**.

---

## Como saber que a prática funcionou

Você consegue, sem consultar:

- [ ] explicar por que a média é a gangorra e a mediana é a fila;
- [ ] dizer por que `n−1`, em duas linguagens diferentes (viés e graus de liberdade);
- [ ] derivar `EP = σ/√n`;
- [ ] escrever um bootstrap em dez linhas;
- [ ] dizer três coisas que o valor-p não é;
- [ ] listar as quatro origens de um outlier e a ação para cada;
- [ ] reconhecer o paradoxo de Simpson quando ele aparecer;
- [ ] escrever uma frase de relatório que não mente.

---

**Próximo:** [75-armadilhas.md](75-armadilhas.md) — o arquivo com o maior retorno por minuto
de leitura de todo o curso.
