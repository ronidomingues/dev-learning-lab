# 10 · Fundamentos — o vocabulário e os modelos mentais

**Nível: iniciante a intermediário** · *Atualizado em 20/08/2026*

Aqui as ideias ganham definição precisa. Tudo que vier depois no curso se apoia neste
arquivo.

---

## 1. Valor do dinheiro no tempo

**Definição.** R$ 1 hoje vale mais que R$ 1 amanhã. A taxa que iguala os dois é a
**taxa de juros**.

Formalmente, se `i` é a taxa por período:

```
VF = VP × (1 + i)^n          valor futuro de um valor presente
VP = VF / (1 + i)^n          valor presente de um valor futuro  ("desconto")
```

A segunda equação é a mais importante de todas as finanças. **Todo ativo vale a soma
dos seus fluxos futuros trazidos a valor presente.** Uma ação, um título, um imóvel,
uma empresa inteira: tudo é a mesma fórmula com fluxos diferentes.

```
        F1        F2              Fn
VP =  ------  +  ------  + ... + ------
      (1+i)     (1+i)²          (1+i)ⁿ
```

**Consequência imediata e não intuitiva:** se `i` sobe, `VP` cai — de tudo, ao mesmo
tempo. É por isso que quando o Banco Central sobe os juros, caem simultaneamente o
preço dos títulos longos, das ações, dos imóveis e das empresas de tecnologia (que têm
fluxos muito distantes no futuro e, portanto, mais sensíveis ao desconto). Não é
coincidência nem "humor do mercado": é o denominador da fração.

---

## 2. Juros simples e compostos

| Tipo | Fórmula | Onde aparece na vida real |
|---|---|---|
| Simples | `VF = VP × (1 + i×n)` | multas, alguns contratos antigos, juros de mora |
| Composto | `VF = VP × (1 + i)ⁿ` | **tudo mais**: investimentos, financiamentos, cartão |

**Por que o composto domina?** Porque o juro do período vira principal no período
seguinte. A função deixa de ser linear e vira exponencial. Nossa intuição é linear,
e por isso subestimamos sistematicamente os dois lados: o crescimento do investimento
e o crescimento da dívida.

**Regra dos 72** — atalho útil: `anos para dobrar ≈ 72 / taxa em %`. Funciona porque
`ln(2) ≈ 0,693` e, para taxas pequenas, `ln(1+i) ≈ i`; 69,3 arredondado para 72
(que tem mais divisores) dá um erro aceitável entre 5% e 20%.

**Conversão entre períodos — o erro mais comum do país:**

```
ERRADO:  1% ao mês = 12% ao ano
CERTO :  1% ao mês = (1,01)^12 - 1 = 12,68% ao ano
```

Quanto maior a taxa, maior o erro. A 3% ao mês, o erro é de 36% contra 42,58% — quase
sete pontos.

---

## 3. Inflação e a equação de Fisher

**Inflação** é a variação do nível geral de preços. No Brasil, medida principalmente
pelo **IPCA** (Índice Nacional de Preços ao Consumidor Amplo, calculado pelo IBGE
sobre famílias com renda de 1 a 40 salários mínimos em 16 regiões metropolitanas).
É o índice da **meta de inflação** perseguida pelo Banco Central.

Outros índices que você vai encontrar:

| Índice | Quem calcula | Mede | Onde aparece |
|---|---|---|---|
| **IPCA** | IBGE | preços ao consumidor | meta do BC, Tesouro IPCA+, correção de contratos |
| **INPC** | IBGE | preços para famílias de 1 a 5 salários mínimos | reajuste salarial, benefícios |
| **IGP-M** | FGV | atacado (60%), consumidor (30%), construção (10%) | aluguéis (em declínio de uso) |
| **INCC** | FGV | custo da construção | financiamento de imóvel na planta |

**Equação de Fisher (exata):**

```
(1 + nominal) = (1 + real) × (1 + inflação)

real = (1 + nominal) / (1 + inflação) - 1
```

A aproximação `real ≈ nominal − inflação` só funciona para taxas baixas. Com nominal
13,90% e inflação 4,44%: a aproximação dá 9,46%; a conta certa dá **9,06%**. Quatro
décimos de diferença, que em 20 anos viram muito dinheiro.

**Por que isso é o centro de tudo:** você não come rentabilidade nominal. Um país com
juro de 40% e inflação de 45% empobrece o poupador; um país com juro de 5% e inflação
de 1% enriquece. **O Brasil de 2026 tem juro real de ~9% — um dos maiores do mundo.**
A seção 8 explica por quê.

---

## 4. Risco — a palavra mais mal usada do mercado

O mercado financeiro usa "risco" para duas coisas diferentes, e confundi-las custa caro:

| | **Volatilidade** | **Risco de perda permanente** |
|---|---|---|
| O que é | o preço oscila | o dinheiro não volta |
| Exemplo | Tesouro IPCA+ cai 15% e depois sobe | banco quebra; empresa fecha; fraude |
| Se você esperar | recupera | não recupera |
| Como se mede | desvio-padrão dos retornos | probabilidade de inadimplência × perda dada a inadimplência |
| Como se controla | prazo compatível com o objetivo | qualidade do emissor, garantias, diversificação |

**Confundir os dois leva aos dois erros clássicos:**
- Tratar volatilidade como risco → fugir de ações e de IPCA+ longo, e perder retorno de
  longo prazo por medo de oscilação que não te afetaria.
- Tratar risco permanente como volatilidade → comprar CDB de banco frágil pensando
  "se cair, eu espero" — e descobrir que não há o que esperar.

**Tipos de risco que você vai encontrar:**

| Risco | Definição | Quem tem |
|---|---|---|
| **Crédito** | o emissor não paga | CDB, debênture, CRI/CRA. Mínimo em título público |
| **Mercado** | o preço muda antes de você vender | prefixado, IPCA+, ações, FII |
| **Liquidez** | não há comprador ao preço justo quando você quer vender | debênture, CRI, FII pequeno, imóvel |
| **Inflação** | o retorno não acompanha os preços | prefixado, poupança |
| **Reinvestimento** | você recebe de volta e só consegue reaplicar a taxa menor | pós-fixado em queda de juros, títulos com cupom |
| **Câmbio** | a moeda muda de valor | investimento no exterior, empresa exportadora |
| **Operacional/fraude** | erro, golpe, corretora irregular | qualquer coisa mal escolhida |
| **Regulatório/tributário** | a lei muda | isenção de LCI/LCA, tributação de dividendos |

**O único risco que você não pode diversificar** é o do sistema inteiro — o chamado
risco sistemático. Todos os outros se reduzem com diversificação e qualidade de escolha.

---

## 5. Liquidez

**Definição.** Rapidez com que um ativo vira dinheiro **sem perda de valor**. As duas
partes da definição importam: um imóvel vira dinheiro em uma semana se você aceitar
metade do preço.

| Ativo | Liquidez |
|---|---|
| Conta corrente, Tesouro Reserva | imediata |
| Tesouro Selic, CDB de liquidez diária | D+0 / D+1 |
| Ações, ETFs, FIIs grandes | D+2 (vende hoje, recebe em 2 dias úteis) |
| LCI/LCA | após a carência (6 meses) |
| Debênture, CRI/CRA | mercado secundário estreito; pode levar dias e sair com deságio |
| FII pequeno | pode não haver comprador |
| Imóvel | meses |
| Participação em empresa fechada | anos, se houver |

**Prêmio de liquidez.** Ativos ilíquidos pagam mais **porque** são ilíquidos. Essa é
uma das poucas fontes legítimas de retorno extra disponíveis ao investidor pequeno:
aceitar prender o dinheiro por prazo que você realmente não vai precisar. O erro é
aceitar prêmio de iliquidez com dinheiro que você vai precisar.

---

## 6. A curva de juros

Juros não são um número: são uma **curva**, uma taxa para cada prazo.

```
taxa
 %  |
 15 |                    ___________  <- juros longos
    |          ________/
 14 |*________/
    |  ^ Selic (1 dia)
 13 |
    +---------------------------------------> prazo
      hoje   1a    2a    5a    10a   30a
```

- **Curva normal (ascendente):** prazo longo paga mais. É o formato usual, e reflete
  incerteza crescente.
- **Curva invertida:** curto paga mais que longo. Costuma indicar que o mercado espera
  **queda** de juros à frente — em geral por recessão. Em agosto de 2026, a curva
  brasileira está em transição: a Selic de 14,00% convive com prefixados de 2029 e 2031
  perto de 14,20% (dados de 14/08/2026), ou seja, quase plana.
- **O que a curva te diz:** a taxa longa embute a expectativa média das taxas curtas
  futuras **mais** um prêmio de prazo. Quando você compra um prefixado de 5 anos a
  14,20%, está apostando que a Selic média dos próximos 5 anos será **menor** que isso.

**O prêmio de risco fiscal.** No Brasil, uma parte da taxa longa não é expectativa de
inflação nem de Selic: é desconfiança sobre a trajetória da dívida pública. Quando
sai notícia fiscal ruim, os juros longos sobem sem que o Copom tenha feito nada. Foi
exatamente o que se viu em 14/08/2026, quando as taxas do Tesouro dispararam num dia
de estresse com saída de capital estrangeiro e alta do dólar.

---

## 7. Os quatro indicadores que você precisa conhecer

| Indicador | O que é | Valor em 20/08/2026 |
|---|---|---|
| **Selic (meta)** | taxa definida pelo Copom a cada ~45 dias; a taxa básica da economia | **14,00% a.a.** |
| **Selic over** | taxa efetiva das operações compromissadas com títulos públicos; remunera o Tesouro Selic | ~13,90% a.a. |
| **CDI** | taxa média dos empréstimos de um dia entre bancos; referência de quase toda renda fixa privada | **13,90% a.a.** |
| **IPCA** | inflação oficial | **4,44%** em 12 meses (julho/2026) |

**Por que CDI e Selic são quase iguais?** Porque um banco com dinheiro sobrando tem
duas opções: emprestar para outro banco (CDI) ou comprar título público do BC (Selic).
Se o CDI ficasse muito abaixo da Selic, ninguém emprestaria a outro banco. A
arbitragem cola as duas. O CDI fica alguns centésimos abaixo por conta do risco
bancário residual.

---

## 8. A regra dos cinco porquês: por que o juro brasileiro é tão alto?

Esta é a pergunta central para quem investe no Brasil. Vamos até o fundo.

**1. Por que o juro real brasileiro é ~9% enquanto o americano é ~2%?**
Porque o Copom fixa a Selic em 14% com inflação de 4,44%.

**2. Por que o Copom precisa de uma Selic tão alta para controlar a inflação?**
Porque a **transmissão da política monetária é fraca**: uma parte grande do crédito na
economia brasileira não responde à Selic. Crédito direcionado (habitacional pela
poupança, rural, BNDES) tem taxa administrada; benefícios e contratos são indexados;
e o crédito livre é curto. Sobre a fatia que responde, o BC precisa apertar muito mais.

**3. Por que existe tanto crédito direcionado e indexação?**
Decisões históricas documentadas. A indexação generalizada foi a forma que o Brasil
achou de conviver com a hiperinflação dos anos 1980 e início dos 1990 — correção
monetária em tudo, do salário ao aluguel. O Plano Real (1994) desindexou os preços,
mas **não desindexou tudo**: a poupança manteve sua fórmula, o crédito imobiliário
manteve seu funding subsidiado, o salário mínimo manteve regra de reajuste real.

**4. Por que essas amarras não foram removidas depois de 1994?**
Aqui há duas respostas honestas, e elas são **trade-offs políticos explícitos**:
(a) cada amarra protege um grupo organizado — poupadores, mutuários, aposentados,
setor rural — e removê-la tem custo eleitoral concentrado com benefício difuso;
(b) parte delas cumpre função social real (crédito habitacional acessível), e o
debate é sobre quem paga a conta, não sobre se ela existe. **Quem paga é o tomador de
crédito livre e, no caso da poupança, o próprio poupador.**

**5. Por que o prêmio de risco fiscal é tão persistente?**
Porque a dívida pública brasileira é grande, cara e de prazo relativamente curto, e
uma parcela relevante dela é **indexada à própria Selic** (as LFTs). Isso cria um laço:
quando o BC sobe os juros para conter inflação, a despesa financeira do governo sobe
junto, piorando o quadro fiscal que alimenta o prêmio de risco. Poucos países têm essa
característica no mesmo grau.

**Onde a cadeia para.** Chegamos a três paradas legítimas: uma **decisão histórica
documentada** (a arquitetura de indexação herdada da hiperinflação e apenas
parcialmente desmontada em 1994), um **trade-off político-econômico explícito**
(quem paga o crédito subsidiado), e uma **restrição estrutural** (composição e prazo
da dívida pública). Não há "é assim porque sim" em nenhum degrau.

**A consequência prática para você, que é o ponto:** o investidor brasileiro é pago
excepcionalmente bem para correr risco baixo. **Essa é uma anomalia mundial, e é
racional aproveitá-la enquanto durar** — sem confundi-la com lei da natureza. Ela é o
sintoma de um problema, não uma virtude do país.

---

## 9. Modelos mentais para levar

1. **Todo ativo é fluxo de caixa descontado.** Se você não sabe qual é o fluxo, você
   não sabe o que comprou.
2. **Retorno é a compensação por três coisas: tempo, inflação e risco.** Retorno acima
   dos pares significa risco acima dos pares. Sempre.
3. **Custo é certo; retorno é hipótese.** Otimize o que é certo.
4. **Prazo do objetivo define o produto.** Não é o perfil de investidor: é a data em
   que você vai precisar do dinheiro.
5. **Volatilidade não é risco quando o prazo é longo. Iliquidez não é risco quando o
   dinheiro não é necessário. Ambas viram risco na hora errada.**
6. **Diversificação é a única "refeição grátis"** — reduz risco sem reduzir retorno
   esperado, desde que os ativos não andem juntos.
7. **O comportamento supera a técnica.** A maior perda do investidor médio não vem de
   escolher o produto errado, e sim de comprar na euforia e vender no pânico.

---

## Autoteste

1. Escreva a fórmula do valor presente e explique por que a alta de juros derruba
   simultaneamente títulos longos, ações e imóveis.
2. Converta 1,5% ao mês para ao ano, corretamente. Qual seria o erro da conta ingênua?
3. Nominal 13,90%, inflação 4,44%. Calcule o juro real exato e diga qual o erro da
   subtração simples.
4. Dê um exemplo de volatilidade que **não** é risco e um de risco que **não** aparece
   como volatilidade.
5. Por que o CDI é quase igual à Selic? O que aconteceria se ficasse muito abaixo?
6. O que uma curva de juros invertida sugere sobre as expectativas do mercado?
7. Percorra os cinco porquês do juro alto brasileiro e diga qual é o tipo de cada parada
   final (lei física, decisão histórica, trade-off econômico ou convenção).
8. Cite três riscos que a diversificação reduz e um que ela não reduz.

---

**Próximo:** [11-historia.md](11-historia.md)
