# 06 · Exemplos — 13 casos com as contas feitas

**Nível: iniciante a intermediário** · *Todos os números executados em 20/08/2026*

Cada exemplo tem **problema → solução → explicação**. Todos os números desta página
foram **produzidos rodando o código**, não estimados. Você pode reproduzir qualquer
um deles:

```bash
cd 07-projeto-modelo
python3 carteira.py --valor 6000 --prazos 365
```

Cenário de todos os exemplos: **Selic 14,00% · CDI 13,90% · IPCA 12m 4,44% ·
IPCA esperado 5,02%**.

---

## Exemplo 1 — Onde colocar R$ 6.000 que podem ser necessários a qualquer momento

**Problema.** Reserva de emergência. Prioridade: poder sacar hoje. Segunda
prioridade: não perder para a inflação.

**Solução.** Comparação em 12 meses, líquida de tudo:

| Produto | Líquido | % a.a. líquido | % a.a. real | Saca quando? |
|---|---|---|---|---|
| CDB 110% CDI (banco médio) | R$ 756,86 | 12,61% | 7,83% | diária |
| LCI 88% CDI (isenta) | R$ 733,92 | 12,23% | 7,46% | **só após 6 meses** |
| Tesouro Selic | R$ 690,03 | 11,50% | 6,76% | D+0 até 13h |
| Tesouro Reserva / CDB 100% CDI | R$ 688,05 | 11,47% | 6,73% | imediata (24×7) |
| Fundo DI 0,50% a.a. | R$ 656,89 | 10,95% | 6,23% | D+0/D+1 |
| Fundo DI 2,00% a.a. | R$ 575,10 | 9,58% | 4,93% | D+0/D+1 |
| **Poupança** | **R$ 500,58** | **8,34%** | **3,74%** | imediata, mas só no aniversário |

**Explicação.** A LCI rende mais que o Tesouro, mas **não serve para reserva de
emergência** — tem carência de 6 meses. O CDB de 110% do CDI serve, se o emissor for
sólido e o valor estiver dentro do FGC. Para R$ 6.000, a diferença entre o primeiro e
o quarto colocado é de R$ 69 no ano; a diferença entre o primeiro e a poupança é de
**R$ 256**. Traduzindo: **sair da poupança vale 5× mais do que escolher perfeitamente
o produto**. Otimize a decisão grande primeiro.

---

## Exemplo 2 — O dia que vale R$ 25

**Problema.** Você aplicou R$ 6.000 em CDB de 100% do CDI. Precisa do dinheiro "por
volta de seis meses". Faz diferença resgatar no dia 180 ou no 181?

**Solução.**

| Dia do resgate | Rendimento bruto | IR | **Líquido** |
|---|---|---|---|
| 179 | R$ 395,45 | R$ 88,98 | R$ 306,47 |
| **180** | R$ 397,73 | R$ 89,49 | **R$ 308,24** |
| **181** | R$ 400,01 | R$ 80,00 | **R$ 320,01** |
| 360 | R$ 821,83 | R$ 164,37 | R$ 657,46 |
| **361** | R$ 824,26 | R$ 144,25 | **R$ 680,01** |
| 720 | R$ 1.756,22 | R$ 307,34 | R$ 1.448,88 |
| **721** | R$ 1.758,99 | R$ 263,85 | **R$ 1.495,14** |

**Explicação.** Esperar **um dia** no dia 180 rende R$ 11,77 a mais; no dia 360,
R$ 22,55; no dia 720, R$ 46,26. A alíquota cai de uma vez (22,5% → 20% → 17,5% → 15%)
e incide sobre **todo** o rendimento acumulado, não só sobre o do último dia. É a
maior taxa de retorno por 24 horas que existe legalmente no país — e é grátis. Antes
de qualquer resgate, olhe a data da aplicação.

```python
# reproduza:
import produtos as p
for d in (180, 181):
    print(d, round(p.PosFixadoCDI(percentual_cdi=1.0).simular(6000, d).liquido, 2))
# 180 308.24
# 181 320.01
```

---

## Exemplo 3 — Por que resgatar em 10 dias parece um roubo

**Problema.** Você aplicou R$ 6.000 e precisou resgatar 10 dias depois. Rendeu quase nada. Foi golpe?

**Solução.** Não. Foi o IOF:

| Dia do resgate | Bruto | IOF | IR | **Líquido** |
|---|---|---|---|---|
| 1 | R$ 2,14 | R$ 2,05 | R$ 0,02 | **R$ 0,07** |
| 10 | R$ 21,43 | R$ 14,15 | R$ 1,64 | **R$ 5,65** |
| 20 | R$ 42,94 | R$ 14,17 | R$ 6,47 | **R$ 22,30** |
| 29 | R$ 62,37 | R$ 1,87 | R$ 13,61 | **R$ 46,88** |
| **30** | R$ 64,53 | **R$ 0,00** | R$ 14,52 | **R$ 50,01** |

**Explicação.** O IOF é regressivo por dia e **zera no 30º dia** (Decreto 6.306/2007).
No dia 1 ele leva 96% do rendimento; no dia 29, 3%. Repare no detalhe elegante: em
reais, o IOF é quase o mesmo no dia 10 (R$ 14,15) e no dia 20 (R$ 14,17) — a alíquota
cai na mesma proporção em que o rendimento cresce. **O principal nunca é tocado**:
você nunca resgata menos do que aplicou por causa de imposto.

**Implicação prática:** deixe qualquer aplicação passar de 30 dias sempre que possível.
Para dinheiro que pode sair a qualquer momento, isso é um argumento a favor de manter
um colchão em conta corrente remunerada — ou de aceitar o IOF como custo do improviso.

---

## Exemplo 4 — LCI isenta ou CDB tributado?

**Problema.** O gerente oferece um CDB de **105% do CDI** e uma LCI de **88% do CDI**.
"A LCI é isenta de imposto!" Qual é melhor?

**Solução.** Depende **exclusivamente do prazo**:

| Prazo | LCI 88% (isenta) | CDB 105% | CDB 100% | Vencedor |
|---|---|---|---|---|
| 180 dias | **R$ 351,35** | R$ 323,14 | R$ 308,24 | LCI |
| 365 dias | **R$ 733,92** | R$ 722,45 | R$ 688,05 | LCI, por pouco |
| 730 dias | R$ 1.557,61 | **R$ 1.597,33** | R$ 1.516,34 | CDB |
| 1.095 dias | R$ 2.482,06 | **R$ 2.574,80** | R$ 2.436,01 | CDB |

**Explicação.** A isenção vale **mais quando a alíquota é maior**, e a alíquota é maior
no curto prazo. Aos 180 dias, você foge de 22,5%; depois de 720 dias, só de 15%.
A fórmula que resolve isso de cabeça:

```
% do CDI equivalente = % do CDI isento / (1 - alíquota de IR)
88% / (1 - 0,225) = 113,5%   -> em 6 meses, a LCI empata com um CDB de 113,5%
88% / (1 - 0,150) = 103,5%   -> acima de 2 anos, empata com um CDB de 103,5%
```

**Regra de bolso:** para prazos curtos, isento ganha fácil; para prazos longos, o
tributado precisa oferecer pouco mais que o isento para ganhar. E some sempre a
carência à conta — LCI presa por 6 meses que você precisará em 3 não é uma opção,
é uma armadilha.

---

## Exemplo 5 — O aniversário da poupança

**Problema.** Você deixou R$ 6.000 na poupança e sacou no 59º dia. Quanto rendeu?

**Solução.**

| Dia do saque | Rendimento |
|---|---|
| 29 | **R$ 0,00** |
| 30 | R$ 40,20 |
| **59** | **R$ 40,20** |
| 60 | R$ 80,67 |
| 365 | R$ 500,58 |

**Explicação.** A poupança credita rendimento **só na data de aniversário mensal**.
Sacar no dia 59 entrega o mesmo que sacar no dia 30: os 29 dias do segundo mês foram
trabalhados de graça. É a única aplicação do país que pode render **zero** por 29 dias
de aplicação. Nenhum outro produto de renda fixa faz isso — todos rendem *pro rata die*.

Note também: mesmo no cenário mais favorável (365 dias completos), a poupança entrega
**R$ 500,58**, contra R$ 688,05 do CDB de 100% do CDI. Mesmo risco (ambos com FGC),
mesma liquidez, R$ 187 a menos.

**Por que ela ainda existe assim?** Porque a fórmula é definida em lei (Lei 12.703/2012):
0,5% ao mês + TR enquanto a Selic estiver acima de 8,5% a.a. Não é uma decisão do banco;
é um teto legal. O dinheiro da poupança financia crédito imobiliário a juro controlado —
alguém precisa pagar essa conta, e é o poupador. Ver [11-historia.md](11-historia.md).

---

## Exemplo 6 — O que uma taxa de administração de 2% faz em 10 anos

**Problema.** Seu banco oferece um fundo DI com taxa de administração de 2% ao ano.
"É pequeno, são só 2%." É pequeno?

**Solução.** R$ 6.000 por 10 anos:

| Onde | Valor final | Pago em taxas | Pago em IR |
|---|---|---|---|
| Tesouro Selic | **R$ 19.707,55** | R$ 0,00 | R$ 2.418,98 |
| Fundo DI 0,50% a.a. | R$ 17.470,98 | R$ 2.553,71 | R$ 2.024,29 |
| Fundo DI 2,00% a.a. | **R$ 15.387,10** | **R$ 5.005,34** | R$ 1.656,55 |

**Explicação.** A taxa de 2% ao ano custou **R$ 4.320** de patrimônio final — 22% de
tudo que você teria. E repare no detalhe perverso: o fundo caro pagou **menos IR**
(R$ 1.656 contra R$ 2.418), porque rendeu menos. A instituição transformou o seu
lucro em receita dela, e você ainda "economizou" imposto no processo.

A conta genérica: **uma taxa de x% ao ano corrói aproximadamente `1 − (1 − x)^n` do
seu patrimônio em n anos.** Com 1% ao ano em 20 anos, são 16,5% do patrimônio final —
R$ 8.726 sobre R$ 6.000 iniciais. Custo é a única variável do investimento que você
controla **com certeza**. Rentabilidade futura é hipótese; taxa é fato.

---

## Exemplo 7 — Quanto custa o come-cotas, isolado de tudo

**Problema.** Todo mundo diz que come-cotas é ruim. Mas ele não aumenta a alíquota
final — só antecipa. Então qual é o problema?

**Solução.** Um fundo com taxa de administração **zero**, contra um CDB com **exatamente
a mesma taxa bruta**. A única diferença entre os dois é o come-cotas:

| Prazo | Fundo (come-cotas) | CDB (sem) | Custo do come-cotas |
|---|---|---|---|
| 1 ano | R$ 684,67 | R$ 688,05 | R$ 3,38 |
| 5 anos | R$ 4.459,85 | R$ 4.676,62 | R$ 216,77 |
| 10 anos | R$ 12.234,77 | R$ 13.641,63 | **R$ 1.406,87** |

**Explicação.** O prejuízo não é o imposto — é o **juro que o imposto antecipado
deixou de render**. A cada maio e novembro, o fundo tira cotas suas para pagar 15%.
Esse dinheiro sai da máquina de juros compostos e nunca mais volta. Em 1 ano o efeito
é irrelevante (R$ 3); em 10 anos, come 10% do seu ganho.

**Conclusão prática:** come-cotas é irrelevante no curto prazo e caro no longo. Para
dinheiro de longo prazo, prefira produtos sem come-cotas: Tesouro Direto, CDB, LCI,
LCA, ações, ETFs, FIIs.

---

## Exemplo 8 — Pós-fixado ou IPCA+? A pergunta de 2026

**Problema.** A Selic está em 14% e o Focus projeta **13,75% no fim de 2026** e
**12,00% em 2027**. O Tesouro IPCA+ 2035 paga IPCA + 6,65%. Onde travar o dinheiro?

**Solução.** Depende de qual risco você quer **evitar**, não de qual retorno você quer:

| Você compra | Você fica exposto a | Você se protege de |
|---|---|---|
| Tesouro Selic / CDB pós | queda da Selic (rende menos amanhã) | tudo o mais; nunca perde nominalmente |
| Tesouro Prefixado 14,20% | inflação surpresa; alta de juros antes do vencimento | queda de juros — você travou 14,20% |
| Tesouro IPCA+ 6,65% | oscilação de preço no meio do caminho | **inflação**, qualquer que seja ela |

Se a Selic seguir a trajetória do Focus (13,75% → 12,00%) e a inflação ficar em 4,5%,
o pós-fixado entrega juro real caindo de ~9% para ~7% ao ano. O IPCA+ 2035 **trava
6,65% reais por nove anos**, aconteça o que acontecer com a Selic.

**Opinião profissional, e é opinião:** com juro real na casa de 6,5% a 7% ao ano em
título soberano de prazo longo, **travar uma parte é historicamente uma boa decisão** —
esse patamar apareceu poucas vezes na história do Tesouro Direto. Mas só vale para
dinheiro que você **não vai precisar antes do vencimento**. Se precisar, você vende
pelo preço do dia, e aí vale o exemplo 9.

---

## Exemplo 9 — Marcação a mercado: por que seu Tesouro IPCA+ "caiu 8%"

**Problema.** Você comprou Tesouro IPCA+ 2035 e três meses depois o extrato mostra
prejuízo. Você foi enganado?

**Solução.** Não. O preço de um título é o valor presente do que ele vai pagar. Se a
taxa de mercado sobe, o preço cai — **matematicamente, sem exceção**:

| Prazo até o vencimento | Taxa vai de 6,65% para… | Preço varia |
|---|---|---|
| 9 anos (IPCA+ 2035) | 7,65% | **−8,1%** |
| 9 anos | 5,65% | **+8,8%** |
| 19 anos (IPCA+ 2045) | 7,65% | **−16,2%** |
| 19 anos | 5,65% | **+19,6%** |

```python
# preço de um título sem cupom: P = VN / (1 + taxa)^prazo
anos, taxa_velha, taxa_nova = 9, 0.0665, 0.0765
variacao = ((1 + taxa_velha) / (1 + taxa_nova)) ** anos - 1
print(f"{variacao:+.1%}")   # -8.1%
```

**Explicação.** Quanto mais longo o título, mais o preço reage a variações de taxa —
isso se chama **duration**. Um IPCA+ 2045 tem cerca do dobro da sensibilidade de um
2035. Mas: **se você levar até o vencimento, recebe exatamente IPCA + 6,65% ao ano**,
independentemente de tudo que aconteceu no meio. A marcação a mercado só se
materializa em prejuízo se você **vender antes**.

O Tesouro Selic é a exceção: como o cupom acompanha a Selic diariamente, o preço não
oscila de forma relevante. **Por isso ele — e não o IPCA+ — é o veículo de reserva de
emergência.**

---

## Exemplo 10 — Aporte único de R$ 6.000 vs. R$ 500 por mês

**Problema.** Vale mais a pena aplicar R$ 6.000 de uma vez ou R$ 500 por mês?

**Solução.** Em 10 anos, a 11,5% líquidos ao ano:

| Estratégia | Total aportado | Valor final |
|---|---|---|
| R$ 6.000 uma vez | R$ 6.000 | R$ 17.819,68 |
| R$ 500 por mês | R$ 60.000 | **R$ 108.090,74** |

**Explicação.** A pergunta está mal formulada — e é assim que quase todo mundo a faz.
Não são alternativas: são coisas diferentes. **O aporte recorrente domina tudo.**
No aporte único, R$ 11.820 dos R$ 17.820 finais são juros (66%). No recorrente,
R$ 48.090 dos R$ 108.090 são juros (44%) — proporção menor, valor muito maior.

A lição: **a taxa de poupança mensal importa mais que a escolha do investimento.**
Escolher entre 11,47% e 12,61% ao ano muda pouco; poupar R$ 500 por mês em vez de
R$ 0 muda tudo. Se você tem R$ 6.000 e vai começar a poupar, comece pelo hábito, não
pelo produto.

---

## Exemplo 11 — Quanto a bolsa precisa render para valer a pena

**Problema.** Vale a pena sair da renda fixa e ir para ações, hoje?

**Solução.** Ações pagam 15% de IR sobre o ganho (acima da isenção de R$ 20 mil/mês
em vendas). Para empatar com um pós-fixado de 11,47% líquido:

| Horizonte | Retorno **bruto** exigido das ações |
|---|---|
| 1 ano | 13,49% a.a. |
| 5 anos | 13,07% a.a. |
| 10 anos | 12,71% a.a. |

**Explicação.** Esse é o **custo de oportunidade** de correr risco no Brasil de 2026.
A bolsa precisa entregar ~13% ao ano só para **empatar** com um título público que não
oscila. E não basta empatar: para justificar o risco, ela precisa entregar um prêmio
por cima — historicamente se fala em 3 a 5 pontos percentuais de prêmio de risco.

Isso significa que, hoje, o "sarrafo" da renda variável no Brasil está por volta de
**16% a 18% ao ano**. É alto. É por isso que juro alto derruba a bolsa: com o ativo
sem risco pagando 14%, o dinheiro sai do risco. E é por isso que, quando a Selic cai,
a bolsa costuma subir — o sarrafo baixa.

**Isso não é argumento para nunca comprar ações.** É argumento para entender que o
prêmio precisa ser explícito na sua conta, e que **em 2026 a renda fixa brasileira é
uma concorrente dura**. Para R$ 6.000, a fatia de renda variável que faz sentido é
pequena e, se existir, deve ser em ETF de índice, não em ação escolhida a dedo.

---

## Exemplo 12 — Caso real: a liquidação do Banco Master e o FGC

**Problema.** Em 2024 e 2025, um banco médio oferecia CDBs a taxas muito acima da
concorrência (percentuais do CDI bem acima de 120%), distribuídos por várias
corretoras. Muita gente colocou dinheiro. O que aconteceu?

**Solução — o que de fato ocorreu.** O Banco Central decretou a **liquidação
extrajudicial do Banco Master em 18 de novembro de 2025** — o maior acionamento do
FGC na história do Sistema Financeiro Nacional. Segundo a cobertura da época:

- Quem estava **dentro** do limite de R$ 250 mil por CPF recebeu do FGC: os pagamentos
  começaram em **janeiro de 2026** e, em meados de fevereiro de 2026, já alcançavam
  cerca de **92%** do valor total previsto.
- O FGC cobre **principal + rendimento até a data da liquidação** (18/11/2025) —
  o rendimento **para** naquele dia.
- Quem estava **acima** de R$ 250 mil entrou na fila de credores da massa liquidanda,
  processo que pode levar **mais de 10 a 15 anos** — e sem garantia de receber tudo.
- CDB, LCI e LCA emitidos pelo banco foram cobertos **independentemente da corretora**
  pela qual foram comprados.

**Explicação — as cinco lições.**

1. **O FGC funciona.** Quem respeitou o limite recebeu. Isso não é pouco: é a diferença
   entre um susto e uma tragédia.
2. **O FGC não é instantâneo.** Meses até o dinheiro cair. Se aquele CDB era a sua
   reserva de emergência, você ficou sem reserva justamente no período de estresse.
   **Por isso reserva de emergência não vai para banco pequeno com taxa alta.**
3. **A taxa alta era o aviso.** O mercado precificava o risco corretamente. Quem
   perguntou "por que este banco paga tanto mais?" tinha a resposta disponível.
4. **O rendimento congela na liquidação.** Você não recebe juros do período em que
   esperou.
5. **O limite é por CPF e por conglomerado**, incluindo o rendimento acumulado — quem
   aplicou R$ 250 mil "cheios" ficou com o rendimento fora da cobertura.

---

## Exemplo 13 — Caso real: a dívida que nenhum investimento bate

**Problema.** Você tem R$ 6.000 para investir e R$ 3.000 rolando no cartão de crédito.

**Solução.**

| Situação | Resultado em 12 meses |
|---|---|
| R$ 3.000 no rotativo do cartão a 14% a.m. (381,8% a.a.) | dívida vira **R$ 14.453,71** |
| R$ 3.000 no rotativo a 8% a.m. (151,8% a.a.) | dívida vira **R$ 7.554,51** |
| R$ 6.000 no melhor CDB da lista | rende **R$ 756,86** |

> **Nota de precisão:** desde a Lei 14.690/2023, o total de juros e encargos do
> rotativo do cartão não pode ultrapassar 100% do valor original da dívida — ou seja,
> a dívida de R$ 3.000 não vira R$ 14.453 na prática: ela é travada em R$ 6.000 e
> migra para parcelamento. A conta acima mostra a **taxa contratual**, que é o que
> importa para a comparação: mesmo com o teto, é a dívida mais cara que você pode ter.

**Explicação.** Não há debate. Investir R$ 6.000 rendendo 12,6% enquanto R$ 3.000
crescem à taxa mais cara do mercado é destruir patrimônio com aparência de disciplina
financeira.
**Quitar a dívida é um investimento com retorno garantido, isento de imposto, igual à
taxa da dívida** — e nenhuma aplicação legal no Brasil chega perto disso.

A ordem correta, sempre: **(1)** quitar dívida cara, **(2)** reserva de emergência,
**(3)** objetivos de médio prazo, **(4)** longo prazo e risco. Pular etapa é a forma
mais comum e mais cara de errar em finanças pessoais — mais cara do que escolher o
produto errado, mais cara do que errar o timing do mercado.

---

## Como reproduzir tudo isto

```bash
cd 07-projeto-modelo
python3 carteira.py --valor 6000 --prazos 30,180,365,730,1825   # exemplos 1, 2, 6
python3 carteira.py impostos                                     # exemplo 4
python3 -m unittest -v                                           # 31 testes, todos passam
```

Para mudar o cenário (e ver como as conclusões mudam):

```bash
echo '{"SELIC_META": 0.02, "SELIC_OVER": 0.019, "CDI": 0.019, "IPCA_12M": 0.10}' > selic2.json
python3 carteira.py --config selic2.json --prazos 365
```

Com Selic a 2% e inflação a 10% — o Brasil de 2020 — **todos os produtos desta página
passam a ter retorno real negativo**. É o teste mais instrutivo do simulador: mostra
que a resposta de hoje não é a resposta de sempre.

---

## Autoteste

1. Por que a LCI vence o CDB em 6 meses e perde em 2 anos?
2. O IOF do dia 10 e o do dia 20 são quase iguais em reais. Por quê?
3. Qual é o custo real do come-cotas, e por que ele cresce com o prazo?
4. Um fundo caro pagou menos IR que um barato. Isso é bom para você?
5. Seu Tesouro IPCA+ 2045 caiu 16%. O que aconteceu com a taxa de mercado, e o que
   acontece se você segurar até 2045?
6. Quanto a bolsa precisa render, bruto, para empatar com 11,47% líquido em 5 anos?
7. Quem tinha R$ 400 mil no Banco Master recebeu quanto do FGC, e quando?
8. Você tem R$ 6.000 e R$ 3.000 no rotativo. Escreva a ordem das operações.
9. Rode o simulador com Selic a 2%. Qual produto passa a ter o melhor retorno **real**?
   Ele é positivo?

---

**Próximo:** [07-projeto-modelo/README.md](07-projeto-modelo/README.md) — o simulador
que produziu todos estes números.

**Fontes consultadas em 20/08/2026:** valores calculados pelo projeto-modelo deste
curso; Banco Central e cobertura de imprensa sobre a liquidação extrajudicial do Banco
Master (18/11/2025) e os pagamentos do FGC iniciados em janeiro de 2026; Boletim Focus
de 17/08/2026 (Selic 13,75% em 2026 e 12,00% em 2027); taxas do Tesouro Direto de
14/08/2026. Links em [95-referencias.md](95-referencias.md).
