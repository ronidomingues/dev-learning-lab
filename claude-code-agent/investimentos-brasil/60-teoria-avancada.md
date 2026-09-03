# 60 · Teoria avançada — o que a pesquisa realmente diz

**Nível: pesquisa** · *Atualizado em 20/08/2026*

Este arquivo é para quem quer saber **por que** as recomendações do curso são o que
são, e onde a teoria falha. Exige familiaridade com média, variância e álgebra básica.

---

## 1. Média-variância: Markowitz (1952)

**A ideia.** Se você mede retorno pela esperança `E[R]` e risco pelo desvio-padrão `σ`,
a combinação de dois ativos tem:

```
E[Rp] = w·E[R1] + (1−w)·E[R2]

σp² = w²σ1² + (1−w)²σ2² + 2·w·(1−w)·ρ·σ1·σ2
```

O termo que muda tudo é `ρ`, a **correlação**. Se `ρ < 1`, o risco da carteira é
**menor que a média ponderada** dos riscos. Retorno é linear na combinação; risco não é.

**Essa é a base matemática da frase "diversificação é o único almoço grátis"** — e ela
é literalmente verdadeira: você reduz `σ` sem reduzir `E[R]`.

**O caso extremo:** com `ρ = −1` e pesos adequados, `σp = 0`. Existe na matemática, não
no mundo — mas mostra a direção.

**Fronteira eficiente.** O conjunto de carteiras que, para cada nível de risco,
maximiza o retorno esperado. Formalmente, resolve-se:

```
min  w'Σw     sujeito a   w'μ = alvo,   w'1 = 1
```

**As três críticas sérias, que a indústria omite:**

1. **Sensibilidade extrema aos insumos.** Pequenos erros em `μ` (retorno esperado)
   produzem carteiras absurdas. Como `μ` é estimado com enorme erro-padrão a partir de
   dados históricos, a "otimização" frequentemente maximiza o erro de estimação. Na
   prática, carteiras ingênuas (1/N) costumam performar comparavelmente ou melhor
   fora da amostra.
2. **Desvio-padrão não é risco.** Ele penaliza igualmente a alta e a queda, e assume
   simetria. Retornos financeiros têm **assimetria negativa** e **caudas gordas**
   (curtose alta): eventos extremos são muito mais frequentes do que a normal prevê.
3. **Correlações não são estáveis.** Elas **sobem para perto de 1 exatamente nas
   crises** — quando a diversificação seria mais necessária. Modelo estimado em tempos
   calmos superestima a proteção.

---

## 2. CAPM e o preço do risco

**Capital Asset Pricing Model** (Sharpe, Lintner, Mossin, anos 1960):

```
E[Ri] = Rf + βi · (E[Rm] − Rf)

           Cov(Ri, Rm)
βi  =     -------------
             Var(Rm)
```

**A tese:** só o risco **não diversificável** (β) é remunerado. Risco específico da
empresa não paga prêmio, porque você poderia tê-lo eliminado de graça.

**Consequência prática direta para você:** concentrar em poucas ações adiciona risco
**sem** adicionar retorno esperado. Essa é a justificativa teórica para preferir ETF de
índice quando o patrimônio é pequeno.

**Onde o CAPM falha empiricamente:** a relação entre β e retorno realizado é fraca — e
em várias amostras é **plana ou invertida** (as ações de β baixo entregam retorno
ajustado ao risco maior, a chamada anomalia de baixa volatilidade). O modelo é uma
lente conceitual excelente e um preditor medíocre.

---

## 3. Fatores: Fama-French e o que sobreviveu

Fama e French (1992, 1993) mostraram que dois fatores adicionais explicavam retornos
melhor que o β sozinho:

```
Ri − Rf = α + β(Rm−Rf) + s·SMB + h·HML + ε
```

- **SMB** (*small minus big*): empresas pequenas superaram grandes.
- **HML** (*high minus low*): empresas "baratas" por valor patrimonial/preço superaram
  as "caras".

Depois vieram **momentum** (Jegadeesh e Titman, 1993), **profitability** e
**investment** (modelo de cinco fatores, 2015), e um "zoológico de fatores" com
centenas de candidatos publicados.

**O estado do debate em 2026, honestamente:**
- Boa parte dos fatores publicados **não replica** fora da amostra original — é o
  problema de *p-hacking* e da crise de replicação, documentado por Harvey, Liu e Zhu
  ("...and the Cross-Section of Expected Returns", 2016).
- Fatores que sobrevivem melhor à crítica: **momentum**, **qualidade/rentabilidade** e,
  com ressalvas grandes, **valor**.
- **Value** passou por mais de uma década de desempenho ruim depois de 2007 — tempo
  suficiente para quebrar a convicção de qualquer investidor real, mesmo que a
  premissa esteja certa.

**Implicação para o investidor pessoa física brasileiro:** *factor investing* exige
horizonte longo, custo baixo, disciplina extrema e tolerância a períodos longos de
desempenho inferior. Com R$ 6.000 e juro real de 9% na renda fixa, o custo de
oportunidade dessa complexidade é alto.

---

## 4. Eficiência de mercado

**Hipótese do mercado eficiente** (Fama, 1970), em três formas:

| Forma | Afirma que os preços já refletem | Consequência |
|---|---|---|
| **Fraca** | todo o histórico de preços | análise técnica não gera retorno anormal persistente |
| **Semiforte** | toda informação pública | análise fundamentalista pública não gera alfa persistente |
| **Forte** | toda informação, inclusive privada | nem insider ganha (empiricamente falso) |

**O paradoxo de Grossman-Stiglitz (1980):** se os preços refletissem *toda* a
informação, ninguém teria incentivo para buscar informação — e então os preços deixariam
de refleti-la. Logo, **o mercado não pode ser perfeitamente eficiente em equilíbrio**.
Precisa haver retorno suficiente para pagar quem pesquisa. Eficiência é um limite
assintótico, não um estado.

**O que a evidência sustenta com solidez:** depois de custos, a **maioria dos gestores
ativos não supera o índice de referência de forma persistente**, e a persistência
observada entre períodos é fraca. Relatórios do tipo SPIVA documentam isso em vários
mercados, inclusive no Brasil. Isso não prova que ninguém consegue — prova que **é
difícil identificar quem consegue *antes*, e não depois**.

---

## 5. Estrutura a termo da taxa de juros

A curva `y(t)` decompõe-se, em teoria, em:

```
taxa longa = média esperada das taxas curtas futuras + prêmio de prazo
```

**Modelos clássicos:**

| Modelo | Ideia | Limitação |
|---|---|---|
| **Expectativas puras** | prêmio de prazo = 0 | rejeitado empiricamente |
| **Preferência por liquidez** | prêmio positivo e crescente com o prazo | não explica curvas invertidas |
| **Vasicek (1977)** | taxa curta com reversão à média, Ornstein-Uhlenbeck | admite taxa negativa |
| **Cox-Ingersoll-Ross (1985)** | difusão com `√r`, taxa não negativa | ajuste imperfeito |
| **Nelson-Siegel / Svensson** | ajuste paramétrico da curva (nível, inclinação, curvatura) | descritivo, não estrutural. **É o padrão de mercado, inclusive na ANBIMA** |

**Duration e convexidade** — o que você usa de fato:

```
              1     Σ t·CFt/(1+y)^t
Duration =   ---  · ----------------           (Macaulay)
              P

D_mod = D / (1 + y)

ΔP/P ≈ − D_mod·Δy + ½·C·(Δy)²
```

O segundo termo, a **convexidade** `C`, é positivo para títulos comuns — por isso a
alta de preço com queda de juros é maior que a queda com alta equivalente. Medido no
[12-renda-fixa.md](12-renda-fixa.md), seção 3: para um IPCA+ de 19 anos, −16,2% contra
+19,6%.

---

## 6. Dimensionamento de posição: Kelly e utilidade

**Critério de Kelly** — a fração `f*` do capital que maximiza a taxa de crescimento
logarítmico:

```
f* = (p·b − q) / b        (aposta binária)
f* ≈ (μ − r) / σ²         (aproximação contínua)
```

Com prêmio de risco de 5% e volatilidade de 25%: `f* ≈ 0,05/0,0625 = 0,8`, isto é,
80% em risco. **Ninguém usa Kelly cheio**, por dois motivos sólidos:

1. A volatilidade do próprio Kelly é brutal — quedas de 50% são esperadas no caminho.
2. `μ` é estimado com erro enorme. Superestimar `μ` leva a sobrealavancagem, e a
   penalidade é assimétrica (você quebra).

Na prática usa-se "meio Kelly" ou menos. E a lição transferível é conceitual:
**o tamanho da posição deve ser função do prêmio esperado dividido pelo quadrado da
incerteza** — quanto menos certeza, muito menos posição.

**Utilidade e aversão ao risco.** Com utilidade CRRA `U(W) = W^(1−γ)/(1−γ)`, a alocação
ótima em risco de um investidor de horizonte longo é `w* = (μ−r)/(γσ²)`. Para
`γ` entre 3 e 5 (faixa típica estimada) e os números brasileiros de 2026 — prêmio de
risco doméstico comprimido por uma taxa livre de risco real de ~9% — **a solução ótima
tem pouca renda variável.** A teoria concorda com a recomendação prática deste curso,
e por um motivo específico e datado: `r` está anormalmente alto.

---

## 7. O problema brasileiro em três equações

**(a) Por que juro real alto derruba o valor dos ativos:**

```
P = Σ CFt / (1+r+prêmio)^t      →  ∂P/∂r < 0, com efeito maior em fluxos distantes
```

**(b) Por que o juro real alto é fiscalmente instável (dinâmica da dívida):**

```
Δ(D/Y) = (r − g)·(D/Y) − superávit primário/Y
```

Se a taxa real `r` supera o crescimento real `g`, a razão dívida/PIB cresce **mesmo com
primário equilibrado**. Com `r ≈ 9%` e `g ≈ 2%` (Focus projeta PIB de 1,98% em 2026), a
diferença `r − g` é de cerca de 7 pontos percentuais — enorme. É a raiz técnica do
prêmio de risco fiscal embutido na curva longa.

**(c) Por que isso limita quanto tempo a anomalia dura:**

O mesmo `r − g` alto que te paga bem torna a trajetória insustentável no longo prazo.
Ou o superávit primário aumenta, ou `r` cai, ou a dívida cresce até forçar um ajuste
(por inflação, por reestruturação ou por reforma). **Nenhum dos três cenários mantém
juro real de 9% para sempre.** Essa é a razão teórica — e não apenas prudencial — para
travar parte do juro real longo hoje via Tesouro IPCA+, em vez de assumir que o
pós-fixado continuará pagando isto indefinidamente.

---

## 8. Fronteiras abertas em 2026

| Tema | Pergunta em aberto |
|---|---|
| **Prêmio de risco de ações** | é 3%, 5% ou 6%? A estimativa depende do período e do método, e a incerteza é maior que a própria magnitude |
| **Fatores** | quantos sobrevivem à correção para múltiplos testes? Há convergência para "poucos" |
| **Aprendizado de máquina em previsão de retorno** | ganhos reais existem em *cross-section*, mas encolhem depois de custos de transação; risco de sobreajuste é o problema central |
| **Prêmio de prazo no Brasil** | quanto da taxa longa é expectativa e quanto é risco fiscal? Decomposições divergem bastante |
| **Ativos privados e iliquidez** | o "prêmio de iliquidez" é remuneração ou artefato de marcação suavizada? |
| **Tokenização e microestrutura** | liquidação atômica muda a estrutura de custos e riscos de contraparte |

---

## Autoteste

1. Mostre por que `σp` é menor que a média ponderada quando `ρ < 1`.
2. Por que otimização média-variância com dados históricos costuma produzir carteiras
   ruins fora da amostra?
3. Enuncie o paradoxo de Grossman-Stiglitz e sua consequência para a gestão ativa.
4. O CAPM diz que risco específico não é remunerado. Que decisão prática isso implica
   para quem tem R$ 6.000?
5. Calcule `f*` de Kelly com prêmio de 4% e volatilidade de 20%. Por que não usá-lo cheio?
6. Escreva a dinâmica da dívida e explique por que `r − g ≈ 7 p.p.` é um problema.
7. Por que a convexidade beneficia o detentor de título longo?
8. Cite duas razões teóricas — não prudenciais — para não assumir que o juro real de
   9% é permanente.

---

**Próximo:** [65-estado-da-arte.md](65-estado-da-arte.md)
