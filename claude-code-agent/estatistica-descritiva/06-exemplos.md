# 6. Exemplos — 14 casos completos e executados

`Nível: iniciante → avançado` · `Última atualização: 20/08/2026`
`Todo o código foi executado em Python 3.10.12 (Ubuntu 22.04.5) em 20/08/2026.`
`As saídas são reais, copiadas do terminal. Nada foi editado à mão.`
`Nenhuma biblioteca externa: só a biblioteca padrão.`

Cada exemplo segue o mesmo esqueleto: **problema → código completo → saída real →
o que isso ensina**. Os exemplos 8, 10, 11 e 12 são casos de produção reais ou reproduções
de estudos publicados.

| # | Exemplo | Medida em foco | Nível |
|---|---|---|---|
| 1 | Salário de uma empresa pequena | média × mediana × moda × aparada | iniciante |
| 2 | Velocidade média de ida e volta | média harmônica | iniciante |
| 3 | Rentabilidade de investimento | média geométrica | iniciante |
| 4 | Dois fornecedores, mesma média | desvio padrão, Cp | intermediário |
| 5 | Bebês, elefantes e milissegundos | coeficiente de variação | intermediário |
| 6 | Pesquisa eleitoral | erro padrão, margem de erro, tamanho de amostra | intermediário |
| 7 | Aluguel: IC da mediana sem fórmula | bootstrap | intermediário |
| 8 | 🏥 Cálculo renal (Charig, 1986) | paradoxo de Simpson | avançado |
| 9 | Quarteto de Anscombe | limites de qualquer resumo | intermediário |
| 10 | Elogio e crítica em pilotos | regressão à média | avançado |
| 11 | ⚙️ Cauda em microsserviços | percentis, "tail at scale" | avançado |
| 12 | 🏥 Painel de 20 exames | comparações múltiplas | avançado |
| 13 | Área de um terreno | propagação de incerteza | intermediário |
| 14 | Renda e escala logarítmica | assimetria, transformação | avançado |

---

## Exemplo 1 — O salário "médio" da empresa

**Problema.** Uma empresa com 15 funcionários quer publicar "o salário médio da nossa
equipe". O RH pede o número. Qual você entrega?

```python
import statistics as st

salarios = [2100, 2300, 2300, 2500, 2800, 3000, 3200, 3500,
            4000, 4500, 5200, 6000, 7500, 9000, 48000]

def media_aparada(d, prop=0.10):
    """Descarta os prop*n menores e os prop*n maiores, e tira a média do resto."""
    o = sorted(d)
    k = int(len(o) * prop)
    return st.mean(o[k:len(o)-k]) if len(o) - 2*k > 0 else st.mean(o)

n = len(salarios)
print(f"n = {n} funcionarios")
print(f"media           R$ {st.mean(salarios):>10,.2f}")
print(f"mediana         R$ {st.median(salarios):>10,.2f}")
print(f"moda            R$ {st.mode(salarios):>10,.2f}")
print(f"media aparada10%R$ {media_aparada(salarios):>10,.2f}")
print(f"folha total     R$ {sum(salarios):>10,.2f}")
print()
abaixo = sum(1 for s in salarios if s < st.mean(salarios))
print(f"funcionarios abaixo da media: {abaixo}/{n} ({100*abaixo/n:.0f}%)")
print(f"razao media/mediana: {st.mean(salarios)/st.median(salarios):.2f}")
```

```
n = 15 funcionarios
media           R$   7,060.00
mediana         R$   3,500.00
moda            R$   2,300.00
media aparada10%R$   4,292.31
folha total     R$ 105,900.00

funcionarios abaixo da media: 12/15 (80%)
razao media/mediana: 2.02
```

**O que isso ensina.** Quatro medidas de "valor típico", quatro respostas entre R$ 2.300 e
R$ 7.060 — para os mesmos dados, sem nenhuma delas estar errada. **80% da empresa ganha
menos que "a média".** O dono, com R$ 48.000, é 1 pessoa em 15 e move a média em R$ 3.000.

- Para "quanto ganha um funcionário típico": **mediana** (R$ 3.500).
- Para "quanto custa a folha": **média × n = total** (R$ 105.900) — só a média serve.
- A **média aparada** (R$ 4.292) é um meio-termo honesto: descarta os 10% extremos de cada
  lado. É a medida usada no cálculo do IPCA (núcleo por médias aparadas) e no ranking de
  esportes olímpicos com juízes. Ver [12-medidas-de-posicao.md](12-medidas-de-posicao.md).

---

## Exemplo 2 — Ida a 100 km/h, volta a 60 km/h

**Problema.** Você vai a 100 km/h e volta pelo mesmo caminho a 60 km/h. Qual foi a velocidade
média da viagem? (A resposta "80" está errada, e o erro tem nome.)

```python
import statistics as st

d = 120.0                      # km, cada trecho
v_ida, v_volta = 100.0, 60.0   # km/h

t_ida, t_volta = d/v_ida, d/v_volta
v_real = (2*d) / (t_ida + t_volta)

print(f"ida:    {d:.0f} km a {v_ida:.0f} km/h -> {t_ida:.2f} h")
print(f"volta:  {d:.0f} km a {v_volta:.0f} km/h -> {t_volta:.2f} h")
print(f"total:  {2*d:.0f} km em {t_ida+t_volta:.2f} h")
print()
print(f"media ARITMETICA das velocidades : {st.mean([v_ida, v_volta]):.2f} km/h  <- ERRADO")
print(f"media HARMONICA das velocidades  : {st.harmonic_mean([v_ida, v_volta]):.2f} km/h  <- CERTO")
print(f"velocidade media real (dist/tempo): {v_real:.2f} km/h")
```

```
ida:    120 km a 100 km/h -> 1.20 h
volta:  120 km a 60 km/h -> 2.00 h
total:  240 km em 3.20 h

media ARITMETICA das velocidades : 80.00 km/h  <- ERRADO
media HARMONICA das velocidades  : 75.00 km/h  <- CERTO
velocidade media real (dist/tempo): 75.00 km/h
```

**O que isso ensina.** Você passa **mais tempo** na velocidade menor, então ela pesa mais.
A média aritmética trataria os dois trechos como se durassem o mesmo tempo — e não duram.

**A regra que resolve para sempre:** quando a grandeza é uma **razão** (km/h, itens/hora,
R$/kg) e você quer a média mantendo fixo o **numerador** (a distância), use **média
harmônica**. Se o que é fixo for o denominador (o tempo), use aritmética. Repare que o
resultado não depende de `d`: troque 120 por 5 ou por 5.000 e continua 75 km/h.

Onde isso aparece de verdade: P/L médio de uma carteira de ações, taxa média de erro por
requisição, densidade média, custo médio por unidade produzida.

---

## Exemplo 3 — +50%, −50%, +50%, −50%: você empatou?

**Problema.** Um fundo rendeu +50%, −50%, +50% e −50% em quatro anos. A média aritmética dos
retornos é 0%. Você recuperou seu dinheiro?

```python
import statistics as st

retornos = [+0.50, -0.50, +0.50, -0.50]
capital = 1000.0
for r in retornos:
    capital *= (1 + r)

fatores = [1 + r for r in retornos]

print("retornos anuais:", [f"{r:+.0%}" for r in retornos])
print(f"media aritmetica dos retornos: {st.mean(retornos):+.2%}  <- sugere 'empatou'")
print(f"capital final de R$ 1.000,00 : R$ {capital:,.2f}")
print(f"retorno acumulado real       : {capital/1000-1:+.2%}")
print()
g = st.geometric_mean(fatores)
print(f"media GEOMETRICA dos fatores : {g:.6f}  ->  {g-1:+.2%} ao ano")
print(f"conferencia: 1000 * {g:.6f}^4 = R$ {1000*g**4:,.2f}")
```

```
retornos anuais: ['+50%', '-50%', '+50%', '-50%']
media aritmetica dos retornos: +0.00%  <- sugere 'empatou'
capital final de R$ 1.000,00 : R$ 562.50
retorno acumulado real       : -43.75%

media GEOMETRICA dos fatores : 0.866025  ->  -13.40% ao ano
conferencia: 1000 * 0.866025^4 = R$ 562.50
```

**O que isso ensina.** Você **perdeu 43,75%**, e a média aritmética dos retornos disse "0%".
Não é sutileza: é a diferença entre ter R$ 1.000 e ter R$ 562,50.

Quando os efeitos se **multiplicam** (juros, crescimento, inflação, contágio), a média certa é
a **geométrica**: aquela que, aplicada repetidamente, chega ao mesmo lugar. A média aritmética
de retornos é **sempre ≥** a geométrica (desigualdade das médias), com igualdade só quando não
há variação nenhuma — o que significa que reportar a aritmética **sempre favorece** quem
vende o fundo. Isso não é acidente: é um viés com beneficiário, e é por isso que reguladores
como a SEC americana e a CVM exigem retorno acumulado, não média de retornos.

> **Regra:** somou? aritmética. Multiplicou? geométrica. Razão com numerador fixo? harmônica.
> Vale sempre: **harmônica ≤ geométrica ≤ aritmética.**

---

## Exemplo 4 — Dois fornecedores com exatamente a mesma média

**Problema.** Você compra eixos de 10,00 mm, tolerância de ±0,10 mm. Dois fornecedores
entregam lotes com média idêntica de 10,0000 mm. Qual você contrata?

```python
import statistics as st

A = [9.98, 10.02, 9.99, 10.01, 10.00, 9.97, 10.03, 10.00, 9.99, 10.01]
B = [9.60, 10.40, 9.75, 10.25, 10.00, 9.55, 10.45, 10.10, 9.80, 10.10]
LIE, LSE = 9.90, 10.10     # limites inferior e superior de especificacao

for nome, d in [("Fornecedor A", A), ("Fornecedor B", B)]:
    m, s = st.mean(d), st.stdev(d)
    fora = sum(1 for x in d if x < LIE or x > LSE)
    cp = (LSE - LIE) / (6*s)                # indice de capacidade do processo
    print(f"{nome}: media={m:.4f}  DP={s:.4f}  fora da especificacao={fora}/{len(d)}  Cp={cp:.2f}")
print()
print(f"Especificacao: {LIE} a {LSE} mm")
print("Mesma media. Decisao muda por completo pelo desvio padrao.")
```

```
Fornecedor A: media=10.0000  DP=0.0183  fora da especificacao=0/10  Cp=1.83
Fornecedor B: media=10.0000  DP=0.3180  fora da especificacao=7/10  Cp=0.10

Especificacao: 9.9 a 10.1 mm
Mesma media. Decisao muda por completo pelo desvio padrao.
```

**O que isso ensina.** É o exemplo mais direto de que **média sozinha não decide nada**.
O fornecedor B acerta a média e entrega 70% de peças refugadas.

O **Cp** (índice de capacidade) é a razão entre a largura da tolerância e a largura natural do
processo (6 desvios padrão, os ±3σ que contêm 99,73%). A indústria usa `Cp ≥ 1,33` como
mínimo e `Cp ≥ 1,67` para itens críticos. A = 1,83 (excelente); B = 0,10 (inviável).

> **Nota histórica.** Esse raciocínio — deslocar o foco da média para a variabilidade — é a
> contribuição de Walter Shewhart (Bell Labs, 1924) e depois de W. E. Deming no Japão do
> pós-guerra. Foi a base do controle estatístico de processo e, por tabela, do Seis Sigma
> (que quer `Cp = 2,0`). Ver [11-historia.md](11-historia.md).

---

## Exemplo 5 — Um desvio padrão de 492 é grande ou pequeno?

**Problema.** Você compara a variabilidade de três coisas em unidades diferentes.
Qual é a mais variável?

```python
import statistics as st

grupos = {
 "peso de recem-nascidos (kg)": [3.2, 3.5, 2.9, 3.8, 3.1, 3.4, 3.6, 3.0],
 "peso de elefantes (kg)"     : [4200, 5100, 3900, 4800, 4500, 5300, 4100, 4700],
 "tempo de resposta (ms)"     : [45, 120, 38, 210, 67, 95, 55, 180],
}

for nome, d in grupos.items():
    m, s = st.mean(d), st.stdev(d)
    print(f"{nome:30s} media={m:>9.2f}  DP={s:>9.2f}  CV={100*s/m:>5.1f}%")
print()
print("O DP dos elefantes e 500x maior que o dos bebes -- e isso nao diz nada.")
print("O CV mostra que o tempo de resposta e, de longe, o mais variavel.")
```

```
peso de recem-nascidos (kg)    media=     3.31  DP=     0.31  CV=  9.5%
peso de elefantes (kg)         media=  4575.00  DP=   492.08  CV= 10.8%
tempo de resposta (ms)         media=   101.25  DP=    64.25  CV= 63.5%

O DP dos elefantes e 500x maior que o dos bebes -- e isso nao diz nada.
O CV mostra que o tempo de resposta e, de longe, o mais variavel.
```

**O que isso ensina.** Desvio padrão é **absoluto** e carrega a unidade; comparar 0,31 kg com
492 kg não responde nada. O **coeficiente de variação** (CV = s/x̄) é adimensional e permite a
comparação: bebês e elefantes variam quase igual em termos relativos (~10%), e o tempo de
resposta varia seis vezes mais.

⚠️ **Quando o CV é inválido** (e isso é esquecido o tempo todo):
- se a variável pode ser **zero ou negativa** — o CV explode ou muda de sinal;
- se a escala é **intervalar e não de razão**: o CV de temperaturas em °C e o das mesmas
  temperaturas em °F dão números diferentes, porque o zero de cada escala é arbitrário.
  Em Kelvin daria outro ainda. Nenhum dos três significa coisa alguma. Ver
  [10-fundamentos.md](10-fundamentos.md).

---

## Exemplo 6 — Por que toda pesquisa eleitoral tem ~2.000 entrevistados

**Problema.** Um instituto quer margem de erro de ±2 pontos. Quantas pessoas precisa ouvir?
E quanto custaria chegar a ±0,5 ponto?

```python
from statistics import NormalDist
import math

z = NormalDist().inv_cdf(0.975)
print(f"z para 95% de confianca: {z:.6f}")
print()
print(f"{'n':>7} {'EP(p=0,5)':>10} {'margem +-':>10}")
for n in [100, 400, 1000, 2000, 4000, 8000, 16000, 32000]:
    ep = math.sqrt(0.25/n)          # pior caso: p = 0,5 maximiza p(1-p)
    print(f"{n:>7} {ep:>10.5f} {100*z*ep:>9.2f}pp")
print()

p, n = 0.42, 2000
ep = math.sqrt(p*(1-p)/n)
print(f"Pesquisa: {p:.0%} de intencao de voto, n={n}")
print(f"  EP = {ep:.5f}  ->  margem = {100*z*ep:.2f} pontos percentuais")
print(f"  IC95% = [{100*(p-z*ep):.1f}% ; {100*(p+z*ep):.1f}%]")
print()
for alvo in [0.02, 0.01, 0.005]:
    n_nec = 0.25 * (z/alvo)**2
    print(f"  para margem de +-{100*alvo:.1f}pp seria preciso n = {math.ceil(n_nec):,}")
```

```
z para 95% de confianca: 1.959964

      n  EP(p=0,5)  margem +-
    100    0.05000      9.80pp
    400    0.02500      4.90pp
   1000    0.01581      3.10pp
   2000    0.01118      2.19pp
   4000    0.00791      1.55pp
   8000    0.00559      1.10pp
  16000    0.00395      0.77pp
  32000    0.00280      0.55pp

Pesquisa: 42% de intencao de voto, n=2000
  EP = 0.01104  ->  margem = 2.16 pontos percentuais
  IC95% = [39.8% ; 44.2%]

  para margem de +-2.0pp seria preciso n = 2,401
  para margem de +-1.0pp seria preciso n = 9,604
  para margem de +-0.5pp seria preciso n = 38,415
```

**O que isso ensina.** A tabela **é** a lei da raiz quadrada, em números: de 100 para 400
(4×) a margem cai de 9,8 para 4,9 (metade). De 400 para 1.600 (4×), cai pela metade de novo.

Isso explica dois fatos do mundo real:

1. **O padrão de ~2.000 entrevistados** é econômico, não estatístico. Em ±2,2 pontos, o custo
   marginal de precisão dispara: passar para ±1 ponto custa quase 5× mais entrevistas.
2. **Empate técnico.** 42% ± 2,2 e 40% ± 2,2 têm intervalos sobrepostos — a pesquisa não
   distingue os dois candidatos. Manchete que anuncia "A lidera com 2 pontos" está lendo
   ruído como sinal. (Rigorosamente, o teste correto é sobre a *diferença* entre proporções,
   cuja margem é ainda maior. Ver [18-inferencia-p-e-ic.md](18-inferencia-p-e-ic.md).)

⚠️ **O que essa margem NÃO cobre:** quem se recusa a responder, quem mente, quem não tem
telefone, e amostra mal desenhada. Isso é erro **sistemático**, e nenhuma fórmula o mede.
Em 2016 e 2020, os erros das pesquisas americanas foram muito maiores que a margem declarada
— por viés de não resposta, não por falta de tamanho de amostra.

---

## Exemplo 7 — Intervalo de confiança da mediana, sem fórmula nenhuma

**Problema.** Existe fórmula pronta para o erro padrão da média. Para a **mediana**, a fórmula
é feia e depende de suposições. Como obter um IC para a mediana sem nada disso?

**Resposta: bootstrap.** Reamostre seus próprios dados, com reposição, milhares de vezes, e
veja o quanto a medida balança.

```python
import random, statistics as st
random.seed(42)

alugueis = [1200,1350,1400,1450,1500,1500,1600,1650,1700,1800,
            1850,1900,2000,2100,2200,2400,2800,3200,4500,9000]
n = len(alugueis)
print(f"n = {n}   mediana observada = R$ {st.median(alugueis):,.2f}")
print(f"         media observada   = R$ {st.mean(alugueis):,.2f}")
print()

B = 10000
medianas, medias = [], []
for _ in range(B):
    reamostra = [random.choice(alugueis) for _ in range(n)]   # com reposicao
    medianas.append(st.median(reamostra))
    medias.append(st.mean(reamostra))

def ic(v, a=0.025):
    v = sorted(v)
    return v[int(a*len(v))], v[int((1-a)*len(v))-1]

lo_md, hi_md = ic(medianas)
lo_m,  hi_m  = ic(medias)
print(f"bootstrap com B = {B:,} reamostragens (semente 42)")
print(f"  EP da mediana = R$ {st.stdev(medianas):,.2f}   IC95% [R$ {lo_md:,.0f} ; R$ {hi_md:,.0f}]")
print(f"  EP da media   = R$ {st.stdev(medias):,.2f}   IC95% [R$ {lo_m:,.0f} ; R$ {hi_m:,.0f}]")
print()
print(f"  largura do IC da mediana: R$ {hi_md-lo_md:,.0f}")
print(f"  largura do IC da media  : R$ {hi_m-lo_m:,.0f}")
```

```
n = 20   mediana observada = R$ 1,825.00
         media observada   = R$ 2,355.00

bootstrap com B = 10,000 reamostragens (semente 42)
  EP da mediana = R$ 156.89   IC95% [R$ 1,550 ; R$ 2,150]
  EP da media   = R$ 383.52   IC95% [R$ 1,762 ; R$ 3,212]

  largura do IC da mediana: R$ 600
  largura do IC da media  : R$ 1,450
```

**O que isso ensina.** Duas coisas grandes.

**1. O bootstrap.** Dez linhas substituem um capítulo de teoria. A ideia (Bradley Efron, 1979)
é audaciosa e simples: *a sua amostra é a melhor estimativa que você tem da população; então
trate-a como se fosse a população e sorteie dela*. Funciona para praticamente qualquer
medida — mediana, quartil, razão, coeficiente de assimetria — inclusive as que não têm fórmula
fechada. É a técnica que a computação barata deu à estatística. Ver
[60-teoria-avancada.md](60-teoria-avancada.md).

**2. Neste conjunto, a mediana é mais precisa que a média.** O IC da mediana tem R$ 600 de
largura; o da média, R$ 1.450 — **2,4× mais incerto**. Contraria a intuição de quem aprendeu
que "a média é o estimador mais eficiente": isso vale para distribuição normal. Com cauda
pesada (aqui, um aluguel de R$ 9.000), a média absorve o extremo e passa a variar muito de
amostra para amostra. **Eficiência depende da distribuição, não é propriedade da medida.**

⚠️ Note que o IC da mediana tem degraus (R$ 1.550, R$ 2.150): com n = 20, a mediana só pode
assumir alguns valores. Bootstrap com `n` pequeno para medidas discretas é aproximado. Sempre
registre a **semente** — sem ela, o resultado não é reprodutível.

---

## Exemplo 8 — 🏥 Caso real: o tratamento que vence em todo grupo e perde no total

**Problema.** Dados reais de Charig et al. (1986), sobre tratamento de cálculo renal, citados
em toda a literatura de inferência causal. Dois tratamentos, dois tipos de cálculo.

```python
dados = {
  "calculos pequenos": {"A (cirurgia aberta)": (81, 87),  "B (percutanea)": (234, 270)},
  "calculos grandes" : {"A (cirurgia aberta)": (192, 263), "B (percutanea)": (55, 80)},
}

print("Charig et al. (1986) -- tratamento de calculo renal\n")
tot = {"A (cirurgia aberta)": [0, 0], "B (percutanea)": [0, 0]}
for grupo, trats in dados.items():
    print(f"{grupo}:")
    for t, (s, n) in trats.items():
        print(f"   {t:22s} {s:3d}/{n:3d} = {100*s/n:5.1f}% de sucesso")
        tot[t][0] += s
        tot[t][1] += n
    print()
print("AGREGADO (somando os dois grupos):")
for t, (s, n) in tot.items():
    print(f"   {t:22s} {s:3d}/{n:3d} = {100*s/n:5.1f}% de sucesso")
print()
print("A vence em pequenos, A vence em grandes, e B 'vence' no total.")
```

```
Charig et al. (1986) -- tratamento de calculo renal

calculos pequenos:
   A (cirurgia aberta)     81/ 87 =  93.1% de sucesso
   B (percutanea)         234/270 =  86.7% de sucesso

calculos grandes:
   A (cirurgia aberta)    192/263 =  73.0% de sucesso
   B (percutanea)          55/ 80 =  68.8% de sucesso

AGREGADO (somando os dois grupos):
   A (cirurgia aberta)    273/350 =  78.0% de sucesso
   B (percutanea)         289/350 =  82.6% de sucesso
```

**O que isso ensina.** Isto é o **paradoxo de Simpson**, e não é curiosidade acadêmica: aqui
ele decide qual cirurgia um paciente recebe.

A explicação está na coluna que ninguém olha — **quantos** pacientes há em cada célula.
O tratamento A foi aplicado majoritariamente a **cálculos grandes** (263 de 350 = 75%), que
são os casos difíceis; B ficou com os pequenos (270 de 350 = 77%), os fáceis. Ao somar, você
compara "A nos casos difíceis" com "B nos casos fáceis". O tamanho do cálculo é uma
**variável de confusão** (*confounder*): afeta tanto a escolha do tratamento quanto o
resultado.

**A pergunta certa não é "qual número está certo".** Os dois estão aritmeticamente corretos.
A pergunta é **causal**: "se eu, com um cálculo grande, escolher A ou B, o que acontece
comigo?". Essa pergunta se responde no estrato, não no agregado — porque a agregação embute a
decisão de quem indicou cada tratamento.

E há uma consequência incômoda, demonstrada por Judea Pearl: **nenhuma análise dos números
sozinha resolve o paradoxo.** Você precisa saber *como os dados foram gerados* — o que causa o
quê. Estatística descritiva não decide isso; ela apenas revela que há algo a decidir.
Ver [16-relacao-entre-variaveis.md](16-relacao-entre-variaveis.md) e
[65-estado-da-arte.md](65-estado-da-arte.md).

---

## Exemplo 9 — Quatro conjuntos, estatísticas idênticas, realidades opostas

**Problema.** F. J. Anscombe construiu, em 1973, quatro conjuntos de dados com praticamente
a mesma média, o mesmo desvio padrão, a mesma correlação e a mesma reta de regressão.
Eles não se parecem em nada.

```python
import statistics as st

x1 = [10, 8, 13, 9, 11, 14, 6, 4, 12, 7, 5]
y1 = [8.04, 6.95, 7.58, 8.81, 8.33, 9.96, 7.24, 4.26, 10.84, 4.82, 5.68]
y2 = [9.14, 8.14, 8.74, 8.77, 9.26, 8.10, 6.13, 3.10, 9.13, 7.26, 4.74]
y3 = [7.46, 6.77, 12.74, 7.11, 7.81, 8.84, 6.08, 5.39, 8.15, 6.42, 5.73]
x4 = [8, 8, 8, 8, 8, 8, 8, 19, 8, 8, 8]
y4 = [6.58, 5.76, 7.71, 8.84, 8.47, 7.04, 5.25, 12.50, 5.56, 7.91, 6.89]

conjuntos = [("I", x1, y1), ("II", x1, y2), ("III", x1, y3), ("IV", x4, y4)]

print(f"{'conj':>5} {'media x':>8} {'DP x':>6} {'media y':>8} {'DP y':>6} {'r':>7} {'inclin.':>8} {'interc.':>8}")
for nome, x, y in conjuntos:
    lr = st.linear_regression(x, y)
    print(f"{nome:>5} {st.mean(x):>8.2f} {st.stdev(x):>6.3f} {st.mean(y):>8.3f} {st.stdev(y):>6.3f} "
          f"{st.correlation(x,y):>7.3f} {lr.slope:>8.3f} {lr.intercept:>8.3f}")
print()

def scatter(x, y, titulo, L=34, A=11):
    """Dispersao em ASCII, sem nenhuma biblioteca grafica."""
    xmin, xmax, ymin, ymax = 3, 20, 3, 13.5
    grade = [[" "]*L for _ in range(A)]
    for a, b in zip(x, y):
        c = int((a-xmin)/(xmax-xmin)*(L-1))
        r = A-1-int((b-ymin)/(ymax-ymin)*(A-1))
        if 0 <= c < L and 0 <= r < A:
            grade[r][c] = "*"
    print(f"  {titulo}")
    for lin in grade:
        print("  |" + "".join(lin))
    print("  +" + "-"*L)

for nome, x, y in conjuntos:
    scatter(x, y, f"Conjunto {nome}")
```

```
 conj  media x   DP x  media y   DP y       r  inclin.  interc.
    I     9.00  3.317    7.501  2.032   0.816    0.500    3.000
   II     9.00  3.317    7.501  2.032   0.816    0.500    3.001
  III     9.00  3.317    7.500  2.030   0.816    0.500    3.002
   IV     9.00  3.317    7.501  2.031   0.817    0.500    3.002

  Conjunto I
  |                                  
  |                                  
  |                                  
  |                 *                
  |                     *            
  |           *   *                  
  |     *       *     *              
  |         *                        
  |   *                              
  | *     *                          
  |                                  
  +----------------------------------
  Conjunto II
  |                                  
  |                                  
  |                                  
  |                                  
  |                                  
  |           * * * * *              
  |       * *           *            
  |                                  
  |     *                            
  |   *                              
  | *                                
  +----------------------------------
  Conjunto III
  |                                  
  |                   *              
  |                                  
  |                                  
  |                                  
  |                     *            
  |             * * *                
  |       * * *                      
  | * * *                            
  |                                  
  |                                  
  +----------------------------------
  Conjunto IV
  |                                  
  |                               *  
  |                                  
  |                                  
  |                                  
  |         *                        
  |         *                        
  |         *                        
  |         *                        
  |                                  
  |                                  
  +----------------------------------
```

**O que isso ensina.** Sete estatísticas idênticas até a segunda casa, e quatro histórias
diferentes que qualquer pessoa distingue em meio segundo olhando o desenho:

- **I** — relação linear com ruído. A descrição estatística é adequada.
- **II** — relação **curva** (é uma parábola). A reta é a resposta errada para a pergunta certa.
- **III** — relação linear **perfeita** com **um** ponto discrepante que entorta a reta.
- **IV** — **não existe relação**: x é constante em 8, exceto por um único ponto em 19 que,
  sozinho, cria toda a correlação. Remova-o e `r` fica indefinido.

**A lição, dita sem meias palavras:** *resumo estatístico nunca substitui olhar os dados.*
Anscombe escreveu isso em 1973 justamente quando a computação começou a permitir calcular sem
olhar. A versão moderna do argumento é o **Datasaurus Dozen** (Matejka & Fitzmaurice, 2017),
que gera 13 conjuntos com as mesmas estatísticas até a segunda casa decimal — um deles é o
desenho de um dinossauro. Ver [20-visualizacao-de-medidas.md](20-visualizacao-de-medidas.md).

---

## Exemplo 10 — Por que o instrutor "descobriu" que elogio piora o desempenho

**Problema.** Instrutores da Força Aérea israelense relataram a Daniel Kahneman: *"quando
elogio um piloto por uma manobra excelente, o voo seguinte é pior; quando grito com um que
foi mal, o seguinte melhora. Logo, punição funciona e elogio atrapalha."*

Vamos simular um mundo em que **o instrutor não existe** e ver o que acontece.

```python
import random, statistics as st
random.seed(7)

N = 2000
habilidade = [random.gauss(100, 10) for _ in range(N)]          # o talento real, fixo
voo1 = [h + random.gauss(0, 10) for h in habilidade]            # desempenho = talento + sorte
voo2 = [h + random.gauss(0, 10) for h in habilidade]
pares = list(zip(voo1, voo2))

elogiados  = [(a, b) for a, b in pares if a >= 115]
criticados = [(a, b) for a, b in pares if a <= 85]

print(f"{N} pilotos. Habilidade real ~ N(100,10). Cada voo = habilidade + ruido N(0,10).")
print("NENHUM feedback foi dado. O instrutor nao existe.\n")
for nome, grupo in [("ELOGIADOS (voo1 >= 115)", elogiados),
                    ("CRITICADOS (voo1 <= 85)", criticados)]:
    m1 = st.mean(a for a, b in grupo)
    m2 = st.mean(b for a, b in grupo)
    print(f"{nome}: n={len(grupo)}")
    print(f"   voo 1 medio = {m1:.1f}")
    print(f"   voo 2 medio = {m2:.1f}   ({m2-m1:+.1f})")
print()
print("Elogiar 'piorou' e criticar 'melhorou' -- sem nenhuma causa. E so a media puxando de volta.")
print(f"correlacao entre voo1 e voo2: {st.correlation(voo1, voo2):.3f}")
```

```
2000 pilotos. Habilidade real ~ N(100,10). Cada voo = habilidade + ruido N(0,10).
NENHUM feedback foi dado. O instrutor nao existe.

ELOGIADOS (voo1 >= 115): n=298
   voo 1 medio = 121.5
   voo 2 medio = 110.3   (-11.2)
CRITICADOS (voo1 <= 85): n=291
   voo 1 medio = 77.7
   voo 2 medio = 89.4   (+11.7)

Elogiar 'piorou' e criticar 'melhorou' -- sem nenhuma causa. E so a media puxando de volta.
correlacao entre voo1 e voo2: 0.486
```

**O que isso ensina.** O efeito que o instrutor via era **real, mensurável e reprodutível**, e
sua explicação causal era completamente falsa. Isso é **regressão à média** (Francis Galton,
1886): um desempenho extremo é, quase sempre, talento + uma dose de sorte. A sorte não se
repete; o talento sim. Logo, o próximo desempenho volta em direção à média.

**A armadilha é estrutural, não uma distração do instrutor.** Sempre que você seleciona casos
por serem extremos e depois mede de novo, verá "melhora" nos piores e "piora" nos melhores —
mesmo que sua intervenção não faça absolutamente nada.

Onde isso já enganou gente séria, e continua enganando:

- **Radares em pontos de acidente.** Instalam-se onde houve pico de acidentes; a queda
  seguinte é atribuída ao radar. Parte dela seria regressão à média. (Isso não significa que
  radar não funcione — significa que sem grupo de controle você não sabe *quanto* funciona.)
- **Tratar quem teve colesterol muito alto num único exame.** Parte da "melhora" é o exame
  seguinte voltando ao normal.
- **Escolas que pioram depois de premiadas**; ações que caem depois de aparecerem na capa da
  revista; "maldição" do segundo álbum, do segundo ano do calouro, da capa do videogame.
- **O antídoto é sempre o mesmo: grupo de controle.** Sem ele, você não distingue efeito de
  regressão. Ver [18-inferencia-p-e-ic.md](18-inferencia-p-e-ic.md).

---

## Exemplo 11 — ⚙️ Caso real: por que a média do seu serviço é ótima e o usuário reclama

**Problema.** Cada microsserviço da sua arquitetura responde rápido em 99% das requisições.
Uma página chama vários deles. Qual é a experiência do usuário?

```python
print("Uma pagina que chama N microsservicos independentes.")
print("Cada servico responde rapido em 99% das vezes (p99 = lento).\n")
print(f"{'N servicos':>11} {'P(pagina rapida)':>18} {'P(usuario pega ao menos 1 lento)':>34}")
for N in [1, 2, 5, 10, 20, 50, 100]:
    rapida = 0.99**N
    print(f"{N:>11} {100*rapida:>17.2f}% {100*(1-rapida):>33.2f}%")
print()
print("Com 100 servicos, 63% das paginas encostam na cauda de alguem.")
print("A media de cada servico ficou otima. A experiencia do usuario, nao.")
```

```
Uma pagina que chama N microsservicos independentes.
Cada servico responde rapido em 99% das vezes (p99 = lento).

 N servicos   P(pagina rapida)   P(usuario pega ao menos 1 lento)
          1             99.00%                              1.00%
          2             98.01%                              1.99%
          5             95.10%                              4.90%
         10             90.44%                              9.56%
         20             81.79%                             18.21%
         50             60.50%                             39.50%
        100             36.60%                             63.40%

Com 100 servicos, 63% das paginas encostam na cauda de alguem.
A media de cada servico ficou otima. A experiencia do usuario, nao.
```

**O que isso ensina.** Este é o argumento de *"The Tail at Scale"* (Dean & Barroso,
Communications of the ACM, 2013) — um dos artigos mais influentes da engenharia de sistemas
distribuídos, e ele é, no fundo, um argumento estatístico.

Quando uma requisição do usuário depende de **muitos** subsistemas, a **cauda** de cada um
vira o **caso típico** do conjunto. O que era evento de 1% em um serviço torna-se evento de
63% na página. É por isso que times de infraestrutura sérios definem SLO em **p99 e p99,9**,
não em média — e por que o Google mede latência de cauda como métrica de produto.

**A lição estatística geral:** quando o resultado depende do **máximo** de várias variáveis
(e não da soma), a média de cada uma é quase irrelevante. Sistemas com muitas dependências
são governados por caudas. O mesmo raciocínio vale para prazo de projeto com várias tarefas
em série, para tempo de espera em pronto-socorro e para o cliente de uma cadeia logística
com 12 elos.

---

## Exemplo 12 — 🏥 Você é saudável e o exame deu alterado

**Problema.** Um check-up mede 20 parâmetros. Cada faixa de referência é construída para
conter os 95% centrais de pessoas saudáveis. Qual a chance de uma pessoa perfeitamente
saudável ter "alguma coisa alterada"?

```python
import random
random.seed(2026)

print("Painel de exames: cada exame tem faixa de referencia dos 95% centrais de gente saudavel.")
print("Logo, uma pessoa SAUDAVEL tem 5% de chance de 'alterar' em cada exame.\n")
print(f"{'nº exames':>10} {'P(ao menos 1 alterado)':>24}")
for k in [1, 5, 10, 20, 30, 50]:
    print(f"{k:>10} {100*(1-0.95**k):>23.1f}%")
print()

N, k = 100000, 20
alterados = [sum(1 for _ in range(k) if random.random() < 0.05) for _ in range(N)]
com_alteracao = sum(1 for a in alterados if a >= 1)
print(f"simulacao: {N:,} pessoas SAUDAVEIS, {k} exames cada (semente 2026)")
print(f"  com ao menos 1 exame 'alterado': {com_alteracao:,} ({100*com_alteracao/N:.1f}%)")
print(f"  media de exames alterados por pessoa: {sum(alterados)/N:.2f}")
```

```
Painel de exames: cada exame tem faixa de referencia dos 95% centrais de gente saudavel.
Logo, uma pessoa SAUDAVEL tem 5% de chance de 'alterar' em cada exame.

 nº exames   P(ao menos 1 alterado)
         1                     5.0%
         5                    22.6%
        10                    40.1%
        20                    64.2%
        30                    78.5%
        50                    92.3%

simulacao: 100,000 pessoas SAUDAVEIS, 20 exames cada (semente 2026)
  com ao menos 1 exame 'alterado': 64,092 (64.1%)
  media de exames alterados por pessoa: 1.00
```

**O que isso ensina.** **64% das pessoas saudáveis** terão pelo menos um exame fora da faixa,
e em média **exatamente 1 exame alterado por pessoa**. Não é erro do laboratório, não é
doença — é aritmética da definição de "faixa de referência".

Este é o **problema das comparações múltiplas**, e ele é o mesmo fenômeno em três disfarces:

- **Medicina:** check-up amplo gera falso alarme, que gera exame de confirmação, que gera
  biópsia. Chama-se *cascata diagnóstica*, e tem morbidade real associada.
- **Ciência:** testar 20 hipóteses e publicar a que deu `p < 0,05` produz literatura falsa por
  construção. É o mecanismo por trás da **crise de replicação** (ver
  [65-estado-da-arte.md](65-estado-da-arte.md)) e do clássico de John Ioannidis, *"Why Most
  Published Research Findings Are False"* (2005).
- **Negócios:** um painel com 40 indicadores sempre terá 2 "piorando significativamente" nesta
  semana. Reagir a cada um é gastar a organização perseguindo ruído.

**Correções existem** — Bonferroni (dividir α pelo número de testes), Benjamini-Hochberg
(controlar a taxa de falsas descobertas) — e estão em
[18-inferencia-p-e-ic.md](18-inferencia-p-e-ic.md). Mas a correção mais importante é de
conduta: **declare quantas coisas você olhou.** Um resultado "significativo" entre 20 testes
não é a mesma evidência que o mesmo resultado numa hipótese única declarada de antemão.

---

## Exemplo 13 — Quanto mede um terreno, com honestidade

**Problema.** Você mede um terreno com trena, precisão de ±5 cm em cada lado. Qual é a área,
com sua incerteza? (Somar as incertezas está errado.)

```python
import math

L, uL = 25.40, 0.05    # comprimento e sua incerteza, em metros
W, uW = 12.15, 0.05    # largura e sua incerteza

A = L * W
uA_rel = math.sqrt((uL/L)**2 + (uW/W)**2)     # produto: incertezas RELATIVAS em quadratura
uA = A * uA_rel

P = 2*(L + W)
uP = 2*math.sqrt(uL**2 + uW**2)               # soma: incertezas ABSOLUTAS em quadratura

print(f"comprimento = {L:.2f} +- {uL:.2f} m   (incerteza relativa {100*uL/L:.3f}%)")
print(f"largura     = {W:.2f} +- {uW:.2f} m   (incerteza relativa {100*uW/W:.3f}%)")
print()
print(f"AREA      = L x W = {A:.4f} m2")
print(f"  incerteza relativa = sqrt({100*uL/L:.3f}%^2 + {100*uW/W:.3f}%^2) = {100*uA_rel:.3f}%")
print(f"  incerteza absoluta = {uA:.4f} m2")
print(f"  reportar: A = ({A:.1f} +- {uA:.1f}) m2")
print()
print(f"PERIMETRO = 2(L+W) = {P:.4f} m")
print(f"  incerteza = 2*sqrt({uL}^2 + {uW}^2) = {uP:.4f} m")
print(f"  reportar: P = ({P:.2f} +- {uP:.2f}) m")
print()
print(f"ERRADO: somar incertezas -> area {A:.2f} +- {A*(uL/L + uW/W):.4f} m2 (superestima {100*((uL/L+uW/W)/uA_rel-1):.0f}%)")
```

```
comprimento = 25.40 +- 0.05 m   (incerteza relativa 0.197%)
largura     = 12.15 +- 0.05 m   (incerteza relativa 0.412%)

AREA      = L x W = 308.6100 m2
  incerteza relativa = sqrt(0.197%^2 + 0.412%^2) = 0.456%
  incerteza absoluta = 1.4078 m2
  reportar: A = (308.6 +- 1.4) m2

PERIMETRO = 2(L+W) = 75.1000 m
  incerteza = 2*sqrt(0.05^2 + 0.05^2) = 0.1414 m
  reportar: P = (75.10 +- 0.14) m

ERRADO: somar incertezas -> area 308.61 +- 1.8775 m2 (superestima 33%)
```

**O que isso ensina.** Incertezas **independentes** se combinam **em quadratura** (raiz da
soma dos quadrados), não somando. O motivo é o mesmo do desvio padrão: variâncias se somam,
desvios padrão não. Somar as incertezas supõe que os dois erros sempre conspiram no mesmo
sentido — o que seria o pior caso, não o caso típico.

Duas regras práticas de propagação, que cobrem 90% dos casos:

| Operação | Como combinar |
|---|---|
| soma ou subtração (`z = x ± y`) | incertezas **absolutas** em quadratura: `u_z = √(u_x² + u_y²)` |
| produto ou divisão (`z = x·y` ou `x/y`) | incertezas **relativas** em quadratura: `u_z/z = √((u_x/x)² + (u_y/y)²)` |
| potência (`z = xⁿ`) | `u_z/z = |n| · u_x/x` |

Repare também no **arredondamento**: o resultado é reportado como `308,6 ± 1,4`, não
`308,6100 ± 1,4078`. Se a incerteza está na casa das unidades, casas além disso são ficção.
Regra do [GUM](https://www.bipm.org/en/committees/jc/jcgm/publications) (o guia internacional
de expressão de incerteza): a incerteza vai com 1 ou 2 algarismos significativos, e o valor é
arredondado na mesma casa. Ver [15-erro-e-incerteza.md](15-erro-e-incerteza.md).

⚠️ **Quando a quadratura falha:** se as duas medidas forem **correlacionadas** (mesma trena
descalibrada, mesmo operador, mesma temperatura), há um termo de covariância e a fórmula
subestima. Erro sistemático compartilhado não se cancela nunca.

---

## Exemplo 14 — A renda, o logaritmo e a regra dos 68% que volta a funcionar

**Problema.** Rendas não têm formato de sino. O que acontece com as medidas usuais — e por que
economistas falam em "log da renda"?

```python
import math, statistics as st, random
random.seed(1)

# rendas simuladas de uma distribuicao log-normal (o formato tipico de renda)
rendas = sorted(round(math.exp(random.gauss(7.9, 0.8)), 2) for _ in range(500))

m, md = st.mean(rendas), st.median(rendas)
print(f"n = {len(rendas)}")
print(f"media      = R$ {m:>10,.2f}")
print(f"mediana    = R$ {md:>10,.2f}")
print(f"razao m/md = {m/md:.3f}")
print(f"DP         = R$ {st.stdev(rendas):>10,.2f}   CV = {st.stdev(rendas)/m:.2f}")
print(f"minimo/max = R$ {min(rendas):,.2f} / R$ {max(rendas):,.2f}")
dentro = sum(1 for x in rendas if abs(x-m) <= st.stdev(rendas))
print(f"dentro de 1 DP: {100*dentro/len(rendas):.1f}%  (a regra do sino previa 68%)")
print()

logs = [math.log(x) for x in rendas]
ml, sl = st.mean(logs), st.stdev(logs)
dentro_l = sum(1 for x in logs if abs(x-ml) <= sl)
print("depois de aplicar logaritmo:")
print(f"  media(log)   = {ml:.4f}   mediana(log) = {st.median(logs):.4f}   razao = {ml/st.median(logs):.4f}")
print(f"  DP(log)      = {sl:.4f}")
print(f"  dentro de 1 DP: {100*dentro_l/len(logs):.1f}%   <- agora a regra do sino funciona")
print()
print(f"  exp(media do log) = R$ {math.exp(ml):,.2f}  <- media GEOMETRICA, proxima da mediana")
print(f"  media geometrica  = R$ {st.geometric_mean(rendas):,.2f}")
```

```
n = 500
media      = R$   3,810.38
mediana    = R$   2,886.69
razao m/md = 1.320
DP         = R$   3,144.01   CV = 0.83
minimo/max = R$ 265.87 / R$ 23,915.44
dentro de 1 DP: 83.0%  (a regra do sino previa 68%)

depois de aplicar logaritmo:
  media(log)   = 7.9560   mediana(log) = 7.9679   razao = 0.9985
  DP(log)      = 0.7806
  dentro de 1 DP: 67.8%   <- agora a regra do sino funciona

  exp(media do log) = R$ 2,852.74  <- media GEOMETRICA, proxima da mediana
  media geometrica  = R$ 2,852.74
```

**O que isso ensina.** Três resultados medidos, não afirmados:

1. **Na escala original, a regra dos 68% erra feio: deu 83%.** O desvio padrão foi inflado
   pela cauda direita e passou a "cobrir" gente demais. Não foi azar da simulação: é o que a
   assimetria faz.
2. **Depois do logaritmo, deu 67,8%** — praticamente os 68% teóricos. O log **não conserta os
   dados**; ele revela que a estrutura multiplicativa deles é que era o problema. Renda,
   preços, tamanho de cidade, tempo de resposta, visualizações de vídeo: tudo isso é gerado
   por processos multiplicativos, e em escala log vira sino.
3. **`exp(média do log)` = média geométrica**, e ela fica perto da mediana. Isso vale
   exatamente para a log-normal: a média geométrica **é** a mediana. Por isso "renda média
   geométrica" é uma medida mais representativa que a aritmética — e por isso o **IDH da ONU**
   passou, em 2010, a usar média geométrica em vez de aritmética para combinar seus três
   componentes.

⚠️ **Duas ressalvas honestas:**
- `log(0)` não existe. Dados com zeros exigem outra transformação (`log1p`, raiz quadrada,
  Box-Cox com deslocamento) — e cada escolha tem consequências.
- **Voltar da escala log é traiçoeiro.** `exp(média do log)` **não** é a média original
  (aqui: R$ 2.852,74 contra R$ 3.810,38, 25% menor). Se a pergunta é sobre o **total**
  (arrecadação, folha, carga), você precisa da média aritmética, e o log não serve. Ver
  [14-forma-e-distribuicoes.md](14-forma-e-distribuicoes.md).

---

## Autoteste

1. Por que 80% dos funcionários do Exemplo 1 ganham menos que a média?
2. Você anda 10 km a 5 km/h e 10 km a 20 km/h. Qual média usar, e por quê?
3. Um fundo rendeu +80% e −45%. A média aritmética é +17,5%. O investidor ganhou dinheiro?
4. Dois processos com a mesma média: qual informação decide a compra?
5. Por que não se pode comparar o desvio padrão de pesos de bebês com o de elefantes?
6. Uma pesquisa quer sair de ±3 pontos para ±1 ponto. O custo aumenta quanto, mais ou menos?
7. No Exemplo 7, por que a mediana teve intervalo de confiança mais estreito que a média?
8. No Exemplo 8, os dois números (por estrato e agregado) estão corretos. O que decide qual usar?
9. No Exemplo 10, o instrutor observou um efeito real. Onde exatamente ele errou?
10. Seu serviço tem p99 = 50 ms e a página chama 30 serviços. Que fração das páginas encosta na cauda?
11. Você mede dois lados com ±1% cada. Qual a incerteza da área?
12. Por que aplicar log a rendas fez a regra dos 68% voltar a funcionar?

<details><summary>Respostas</summary>

1. Porque a distribuição é assimétrica à direita: um salário de R$ 48.000 puxa a média para
   cima sem mover a maioria. Em distribuição assimétrica, a média **não** divide o grupo ao meio.
2. **Harmônica** — a distância é fixa e o tempo varia; você passa mais tempo no trecho lento.
   Resultado: 8 km/h, não 12,5.
3. **Não.** 1,80 × 0,55 = 0,99 → perdeu 1%. A média geométrica dos fatores é
   √0,99 ≈ 0,995, ou −0,5% ao ano.
4. O **desvio padrão** (ou o Cp). Média igual com dispersões diferentes muda tudo:
   no Exemplo 4, um fornecedor entrega 0% de refugo e o outro 70%.
5. Porque o desvio padrão carrega a unidade e a escala. Compare o **coeficiente de variação**,
   que é adimensional — e só se a escala for de razão.
6. **Cerca de 9 vezes** (a razão dos quadrados: 3² / 1² = 9). Do exemplo: 1.068 → 9.604
   entrevistas.
7. Porque a amostra tem cauda pesada (um aluguel de R$ 9.000). A média absorve o extremo e
   varia muito entre reamostras; a mediana o ignora. Eficiência depende da distribuição.
8. A **pergunta causal** e o conhecimento de como os dados foram gerados. Como o tamanho do
   cálculo afeta tanto o tratamento escolhido quanto o desfecho, a comparação válida é
   **dentro do estrato**. Nenhum critério puramente numérico resolve isso.
9. Na **atribuição causal**. O efeito (voo pior depois de elogio) existe e se reproduz; a
   causa não é o elogio, é a regressão à média. Faltou grupo de controle.
10. `1 − 0,99³⁰ ≈ 26%`. Um quarto das páginas encosta na cauda de algum serviço.
11. `√(1² + 1²) ≈ 1,41%` — não 2%. Incertezas independentes somam em quadratura.
12. Porque renda é gerada por um processo **multiplicativo**; o log converte multiplicação em
    soma, e somas de muitos efeitos tendem à normal (Teorema Central do Limite). A regra dos
    68% é uma propriedade da normal, não dos dados em si.

</details>

---

**Próximo:** [07-projeto-modelo/](07-projeto-modelo/README.md) — um programa completo que lê
um CSV e produz um relatório estatístico que **se recusa a mentir**.
