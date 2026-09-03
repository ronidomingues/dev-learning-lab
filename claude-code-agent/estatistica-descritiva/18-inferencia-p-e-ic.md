# 18. Inferência — valor-p, intervalo de confiança e o que eles não dizem

`Nível: avançado` · `Última atualização: 20/08/2026`
`Simulações executadas em Python 3.10.12 em 20/08/2026; saídas reais.`

> Este arquivo está aqui porque a pergunta "o que é erro?" desemboca inevitavelmente em
> "então o resultado é significativo?". A resposta honesta exige desmontar o conceito mais mal
> compreendido da estatística.

---

## 18.1 A lógica do teste de hipótese

1. Você formula uma **hipótese nula** `H₀`: "não há efeito", "os grupos são iguais",
   "a moeda é honesta".
2. Calcula uma **estatística de teste** a partir dos dados.
3. Pergunta: **se `H₀` fosse verdadeira, com que frequência eu veria um resultado tão extremo
   quanto este, ou mais?** Essa frequência é o **valor-p**.
4. Se o valor-p for pequeno, os dados são improváveis sob `H₀` — o que sugere (não prova) que
   `H₀` é falsa.

É um argumento por absurdo probabilístico. E, como todo argumento por absurdo probabilístico,
ele **não é uma prova**: eventos improváveis acontecem.

---

## 18.2 O valor-p: a definição, e as seis coisas que ele não é

> **`p = P(dados tão extremos quanto estes, ou mais | H₀ verdadeira)`**

Repare na barra vertical e no que está de cada lado. O valor-p é a probabilidade **dos dados**,
supondo a hipótese. Não é a probabilidade da hipótese.

| Afirmação | Certa? | Por quê |
|---|---|---|
| "p = 0,03 → há 3% de chance de `H₀` ser verdadeira" | ❌ | Inverte a condicional. `P(D\|H) ≠ P(H\|D)` |
| "p = 0,03 → há 97% de chance de o efeito ser real" | ❌ | Mesmo erro |
| "p < 0,05 → o efeito é importante" | ❌ | O p não mede magnitude; com `n` grande, efeitos triviais dão p minúsculo |
| "p = 0,06 → não há efeito" | ❌ | Ausência de evidência ≠ evidência de ausência |
| "p = 0,04 e p = 0,06 são resultados opostos" | ❌ | São praticamente o mesmo resultado |
| "p = 0,03 → replicando, dá significativo em 97% das vezes" | ❌ | A probabilidade de replicação é bem menor, tipicamente ~50% |

> **A inversão da condicional é a raiz de tudo.** `P(chuva | nuvens)` é alta;
> `P(nuvens | chuva)` é ~1. São perguntas diferentes. O valor-p responde à primeira; todo mundo
> lê como se respondesse à segunda.

### O que o valor-p **não pode** dizer sozinho, e a matemática de por quê

Para saber `P(H₀ é falsa | dados)` você precisa de mais uma informação que o valor-p **não
contém**: quantas das hipóteses que você testa costumam ser verdadeiras (a **taxa de base**).

```python
print(f"{'% hip. verdadeiras':>19} {'poder':>7} {'VPP: P(verdadeira | p<0,05)':>30}")
for prior in [0.5, 0.2, 0.1, 0.05, 0.01]:
    for poder in [0.8, 0.3]:
        vp = prior * poder
        fp = (1 - prior) * 0.05
        print(f"{prior:>18.0%} {poder:>7.0%} {vp/(vp+fp):>29.1%}")
```

```
 % hip. verdadeiras   poder    VPP: P(verdadeira | p<0,05)
               50%     80%                         94.1%
               50%     30%                         85.7%
               20%     80%                         80.0%
               20%     30%                         60.0%
               10%     80%                         64.0%
               10%     30%                         40.0%
                5%     80%                         45.7%
                5%     30%                         24.0%
                1%     80%                         13.9%
                1%     30%                          5.7%
```

**Leia a última linha.** Num campo em que 1% das hipóteses testadas são verdadeiras e o poder
típico é 30% — descrição razoável de boa parte da pesquisa exploratória em ciências da vida —
um resultado com `p < 0,05` tem **5,7% de chance de ser verdadeiro**. O mesmo `p = 0,04` que
é evidência decente num campo maduro é praticamente ruído em outro.

**Este é o argumento inteiro de Ioannidis (2005)**, e ele é aritmética, não polêmica: o mesmo
valor-p significa coisas radicalmente diferentes dependendo do que se está testando.

---

## 18.3 Como o p-hacking acontece — medido

### Espiar os dados enquanto coleta

```python
import random, math, statistics as st

def t_stat(a, b):
    na, nb = len(a), len(b)
    sp = ((na-1)*st.variance(a) + (nb-1)*st.variance(b)) / (na+nb-2)
    return (st.mean(a)-st.mean(b)) / math.sqrt(sp*(1/na + 1/nb))

REP, T = 2000, 1.96
random.seed(77)
sig = 0
for _ in range(REP):
    A = [random.gauss(0,1) for _ in range(50)]
    B = [random.gauss(0,1) for _ in range(50)]
    if abs(t_stat(A,B)) > T: sig += 1
print(f"  coleta fixa n=50             -> {100*sig/REP:5.1f}% de 'descobertas' (deveria ser 5%)")

for lim in (50, 200):
    random.seed(77)
    sig = 0
    for _ in range(REP):
        A = [random.gauss(0,1) for _ in range(10)]
        B = [random.gauss(0,1) for _ in range(10)]
        achou = abs(t_stat(A,B)) > T
        while not achou and len(A) < lim:
            A += [random.gauss(0,1) for _ in range(5)]
            B += [random.gauss(0,1) for _ in range(5)]
            if abs(t_stat(A,B)) > T: achou = True
        if achou: sig += 1
    print(f"  espia a cada 5 ate n={lim:<3}     -> {100*sig/REP:5.1f}% de 'descobertas' (deveria ser 5%)")
```

```
=== 'espiar os dados': parar de coletar quando der significativo ===
    (dois grupos IDENTICOS: nao existe efeito nenhum)

  coleta fixa n=50             ->   5.5% de 'descobertas' (deveria ser 5%)
  espia a cada 5 ate n=50      ->  20.2% de 'descobertas' (deveria ser 5%)
  espia a cada 5 ate n=200     ->  28.9% de 'descobertas' (deveria ser 5%)
```

**Os dois grupos são idênticos: não existe efeito nenhum.** Com coleta fixa, 5,5% de falsos
positivos — o esperado. Espiando a cada 5 observações e parando quando "der", **20,2%**.
Espiando até `n = 200`, **28,9%**.

Ninguém mentiu. Cada teste individual estava correto. O que quebrou foi a **regra de parada** —
e essa regra não aparece em lugar nenhum do artigo publicado.

> Esta é a prática de A/B testing em que "olhamos o painel todo dia e paramos quando ficar
> verde". Ela transforma um teste de 5% num teste de 20 a 30%. Empresas tomam decisões de
> produto assim todos os dias.
> **A solução existe e é técnica:** testes sequenciais com gasto de α (O'Brien-Fleming,
> Pocock) — usados em ensaios clínicos desde os anos 1970 — ou os **e-values** e confiança
> válida a qualquer momento, que permitem espiar quando quiser sem inflar o erro
> ([arquivo 65](65-estado-da-arte.md)).

### Testar várias coisas e reportar a melhor

```
  testando  1 variaveis ->   4.5% de chance de achar 'algo' (teorico 5.0%)
  testando  2 variaveis ->   9.9% de chance de achar 'algo' (teorico 9.8%)
  testando  5 variaveis ->  23.1% de chance de achar 'algo' (teorico 22.6%)
  testando 10 variaveis ->  39.8% de chance de achar 'algo' (teorico 40.1%)
  testando 20 variaveis ->  63.0% de chance de achar 'algo' (teorico 64.2%)
```

É o mesmo fenômeno dos 20 exames de sangue ([exemplo 12](06-exemplos.md)) e da mesma
aritmética: `1 − 0,95ᵏ`.

### O catálogo completo dos "graus de liberdade do pesquisador"

De Simmons, Nelson & Simonsohn (2011). Cada item, sozinho, é defensável; juntos elevam a taxa
de falso positivo acima de 60%:

- decidir quando parar de coletar **olhando o resultado**;
- testar duas variáveis dependentes e reportar a que funcionou;
- incluir ou excluir covariáveis conforme o efeito aparece;
- excluir outliers **depois** de ver o efeito;
- testar subgrupos até um dar significativo;
- escolher a transformação (log, raiz) que produz o menor p;
- reportar uma comparação entre três condições omitindo a terceira.

**O antídoto é procedimental, não estatístico:** pré-registro da análise, declaração de todas
as variáveis medidas, e distinção explícita entre exploratório e confirmatório.

---

## 18.4 Correções para comparações múltiplas

| Método | Controla | Rigor | Quando usar |
|---|---|---|---|
| **Bonferroni** | FWER (chance de ≥1 falso positivo) | muito conservador | poucos testes, alto custo de erro |
| **Holm** | FWER | uniformemente melhor que Bonferroni | sempre preferível a Bonferroni |
| **Benjamini-Hochberg** | FDR (proporção de falsos entre os positivos) | equilibrado | muitos testes, contexto exploratório |
| Nenhuma | — | — | **um** teste pré-registrado |

**Bonferroni:** use `α/k`. Com 20 testes, `α = 0,0025`. Simples e correto, mas com muitos
testes perde quase todo o poder — você deixa de detectar efeitos reais.

**Benjamini-Hochberg (1995)** mudou o jogo em genômica, onde se testam 20.000 genes de uma vez.
A ideia: em vez de tentar evitar **qualquer** falso positivo, controle a **proporção** de
falsos entre os resultados que você declarar positivos. "Aceito que 5% da minha lista de
descobertas seja falsa" é uma promessa mais útil, e muito mais poderosa, que "aceito 5% de
chance de ter uma única falsa".

> **Opinião declarada:** a correção mais valiosa não é matemática, é de conduta —
> **declarar quantos testes foram feitos**. Um leitor informado ajusta a leitura sozinho. Um
> leitor que não sabe que houve 20 testes não tem defesa nenhuma.

---

## 18.5 O intervalo de confiança faz tudo o que o valor-p faz, e mais

Um IC de 95% contém exatamente os valores de `H₀` que **não** seriam rejeitados a `α = 0,05`.
Ou seja: **o IC contém o valor-p** — e ainda mostra magnitude e precisão.

| Você quer saber | Valor-p | IC |
|---|---|---|
| há evidência contra `H₀`? | ✅ | ✅ (o zero está dentro?) |
| qual o tamanho do efeito? | ❌ | ✅ |
| qual a precisão da estimativa? | ❌ | ✅ (a largura) |
| o efeito é praticamente relevante? | ❌ | ✅ (compare com o limiar que importa) |
| o estudo tinha poder? | ❌ | ✅ (IC largo = estudo fraco) |

### Os quatro desfechos, lidos corretamente

Suponha que o efeito mínimo com relevância prática seja **5 unidades**:

```
    0        5                                     leitura
    |        |
    ├──●──┤                    IC [1; 4]      → efeito existe, mas é IRRELEVANTE
         ├───●───┤             IC [4; 9]      → efeito existe e PODE ser relevante
  ├───────●───────┤            IC [-3; 12]    → ESTUDO INCONCLUSIVO (largo demais)
  ├─●─┤                        IC [-1; 1]     → efeito ausente ou desprezível (evidência de nulidade)
```

A terceira e a quarta linha são **completamente diferentes** e ambas produzem "p > 0,05".
Um estudo inconclusivo e um estudo que demonstra ausência de efeito relevante são coisas
opostas — e o valor-p sozinho não as distingue. **É por isso que a recomendação de reportar IC
não é preciosismo.**

---

## 18.6 Poder, erro tipo I, tipo II, S e M

| | `H₀` verdadeira | `H₀` falsa |
|---|---|---|
| **Rejeitou `H₀`** | ❌ erro tipo I (α) — falso positivo | ✅ acerto (poder = 1−β) |
| **Não rejeitou** | ✅ acerto | ❌ erro tipo II (β) — falso negativo |

- **α** é escolhido por você (tipicamente 0,05).
- **β** depende do tamanho do efeito, do `n` e da variabilidade. **Poder = 1 − β**; a convenção
  é buscar ≥ 80%.

Gelman e Carlin acrescentaram dois erros que importam mais na prática:

- **Erro tipo S (sinal):** você acerta que há efeito, mas erra o **sinal** dele. Com poder
  muito baixo, isso deixa de ser raro.
- **Erro tipo M (magnitude):** você acerta que há efeito, mas a estimativa está
  **muito inflada**. Isso é sistemático: com baixo poder, só as estimativas exageradas
  ultrapassam o limiar de significância.

> **Consequência prática de gente que decide orçamento:** estudos de baixo poder não são
> apenas "menos informativos". Eles produzem literatura **sistematicamente enviesada para
> cima**, o que faz efeitos pequenos parecerem grandes, orienta investimento errado, e depois
> falha na replicação. Um estudo subdimensionado é pior que nenhum estudo.

**Análise de poder pós-hoc** — calcular o poder depois de um resultado não significativo — é
matematicamente vazia: é apenas o valor-p reescrito em outra escala. O que vale é reportar o
IC, que já diz que efeitos o estudo conseguiria excluir.

---

## 18.7 O que fazer, na prática

### Se você está analisando

1. **Defina a análise antes de ver os dados.** Se não deu, diga que foi exploratória.
2. **Calcule o tamanho de amostra antes de coletar.**
3. **Reporte tamanho de efeito com IC**, sempre. O p é opcional.
4. **Declare quantas comparações foram feitas.**
5. **Nunca pare de coletar olhando o resultado** — a menos que use um método sequencial
   projetado para isso.
6. **Não dicotomize.** `p = 0,049` e `p = 0,051` são o mesmo resultado.

### Se você está lendo

1. **Procure o `n`.** Se não estiver lá, desconfie de tudo.
2. **Procure o IC.** Só o p? Peça o IC.
3. **Pergunte quantas coisas foram testadas.** Se o artigo não diz, presuma que foram muitas.
4. **Pergunte pelo tamanho do efeito em unidades reais.** "Reduziu o risco em 50%" pode
   significar de 2 em 10.000 para 1 em 10.000.
5. **Pergunte pela taxa de base.** É um campo em que hipóteses costumam se confirmar?
6. **Cheque se houve pré-registro.**

### Uma nota sobre risco relativo × risco absoluto

Esta é a manipulação estatisticamente honesta mais eficaz que existe, e ela está em todo lugar:

| | Grupo A | Grupo B |
|---|---|---|
| Risco | 2 em 10.000 | 1 em 10.000 |
| **Redução relativa** | — | **50%** |
| **Redução absoluta** | — | **0,01 ponto percentual** |
| **NNT** (número necessário para tratar) | — | **10.000** |

Os três números descrevem o mesmo fato. "Reduz o risco pela metade" é verdadeiro e vende;
"é preciso tratar 10.000 pessoas para evitar um caso" é verdadeiro e informa. **Sempre exija
o risco absoluto e o NNT.**

---

## Autoteste

1. Escreva a definição exata do valor-p, prestando atenção na barra condicional.
2. `p = 0,03`. Qual a probabilidade de `H₀` ser falsa?
3. Num campo com 1% de hipóteses verdadeiras e poder de 30%, quanto vale `p < 0,05`?
4. Por que espiar os dados e parar quando "der" elevou o falso positivo de 5% para 29%?
5. Qual é o antídoto contra o p-hacking — e por que ele não é estatístico?
6. Diferença entre controlar FWER e controlar FDR. Quando cada um?
7. Dois resultados não significativos: IC [−3; 12] e IC [−1; 1]. São a mesma coisa?
8. O que é erro tipo M, e por que ele torna estudos de baixo poder ativamente danosos?
9. Análise de poder pós-hoc: por que é vazia?
10. "Reduz o risco em 50%." Que dois números você pede em seguida?

<details><summary>Respostas</summary>

1. `p = P(dados tão extremos quanto os observados, ou mais | H₀ verdadeira)`. É probabilidade
   **dos dados dada a hipótese** — não da hipótese dados os dados.
2. **Não dá para saber** só com o valor-p. Depende da taxa de base (quantas hipóteses no seu
   campo costumam ser verdadeiras) e do poder do estudo.
3. **5,7%** de chance de o resultado ser verdadeiro. Praticamente ruído — o mesmo p que seria
   evidência razoável num campo maduro.
4. Porque cada "espiada" é uma nova oportunidade de o ruído cruzar o limiar. Com muitas
   oportunidades, a probabilidade de pelo menos uma cruzar é muito maior que 5%. É o problema
   de comparações múltiplas disfarçado de regra de parada.
5. **Pré-registro** e **declaração completa** do que foi medido e testado. Não é estatístico
   porque o problema não é de cálculo, é de **liberdade de escolha não declarada** — e nenhuma
   fórmula recupera informação que não foi registrada.
6. **FWER** controla a chance de **ao menos um** falso positivo (Bonferroni, Holm) — use com
   poucos testes e alto custo de erro. **FDR** controla a **proporção** de falsos entre os
   positivos declarados (Benjamini-Hochberg) — use em contexto exploratório com muitos testes,
   como genômica.
7. **Não.** O primeiro é **inconclusivo** (o estudo não excluiu nem efeito grande nem nulo);
   o segundo é **evidência de ausência** de efeito relevante. Opostos, e o valor-p não os
   distingue.
8. **Erro tipo M (magnitude):** com baixo poder, apenas estimativas exageradas ultrapassam o
   limiar, então os efeitos publicados são sistematicamente inflados. Isso enviesa a
   literatura inteira para cima, mesmo sem má-fé, e orienta decisões erradas.
9. Porque, dado um `n` e um resultado, o poder pós-hoc é uma função monótona do próprio
   valor-p — não acrescenta informação nenhuma. O que informa é o **IC**.
10. O **risco absoluto** (de quanto para quanto) e o **NNT** (quantas pessoas é preciso tratar
    para evitar um caso).

</details>

---

**Próximo:** [19-robustez-e-outliers.md](19-robustez-e-outliers.md) — o que fazer com o valor
esquisito.
