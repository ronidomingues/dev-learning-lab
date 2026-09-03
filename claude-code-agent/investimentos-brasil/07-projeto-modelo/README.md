# Projeto-modelo · `simulador` — quanto sobra no seu bolso

**Nível: iniciante a intermediário** · *Testado em Python 3.10.12, em 20/08/2026*

Um programa pequeno, mas **inteiro**, que responde à única pergunta que importa
na hora de escolher onde investir:

> Dado **quanto** eu tenho, por **quanto tempo** e em **qual produto** —
> quanto sobra depois de imposto, IOF e taxas?

Ele existe porque a comparação que os bancos oferecem é a errada. "110% do CDI"
e "IPCA + 6,65%" e "0,5% ao mês" não são comparáveis entre si: têm bases,
tributações e prazos diferentes. Este programa põe tudo na mesma moeda —
**reais líquidos no seu prazo**.

---

## Pré-requisitos

- Python **3.10 ou superior** (instalação em [../03-instalacao.md](../03-instalacao.md), seção 4)
- Nada mais. **Zero dependências externas**, só a biblioteca padrão.

```bash
python3 --version
# esperado: Python 3.10.x ou superior
```

---

## Como rodar

```bash
cd 07-projeto-modelo
```

**1. Comparação padrão** — R$ 6.000 em cinco prazos:

```bash
python3 carteira.py
```

**2. Seu valor e seus prazos:**

```bash
python3 carteira.py --valor 20000 --prazos 90,365,1825
```

**3. Plano de alocação a partir da sua despesa mensal:**

```bash
python3 carteira.py plano --valor 6000 --despesa-mensal 2500
```

**4. Tabelas de imposto e a equivalência isento × tributado:**

```bash
python3 carteira.py impostos
```

**5. Exportar para planilha:**

```bash
python3 carteira.py --formato csv > comparacao.csv
```

**6. Cenário próprio** (e se a Selic cair para 10%?):

```bash
echo '{"SELIC_META": 0.10, "SELIC_OVER": 0.099, "CDI": 0.099}' > cenario_selic10.json
python3 carteira.py --config cenario_selic10.json --prazos 365
```

**7. Testes:**

```bash
python3 -m unittest -v
# esperado ao final: Ran 31 tests ... OK
```

```bash
python3 -m doctest tributos.py -v | tail -1
# esperado: Test passed.
```

---

## Saída real (executada em 20/08/2026)

```
Simulador de renda fixa — cenario de 2026-08-20
Selic 14,00% a.a. | CDI 13,90% a.a. | IPCA 12m 4,44% | valor simulado R$ 6.000,00

### Prazo: 365 dias (~12 meses)

produto                               liquido    % a.a.   real a.a.      IR+IOF     taxas  observacao
-----------------------------------------------------------------------------------------------------
CDB 120% CDI (banco pequeno)        R$ 825,66    13,76%       8,92%   R$ 175,14   R$ 0,00  RESGATE BLOQUEADO: carencia de 720 dias
CDB 110% CDI (banco medio)          R$ 756,86    12,61%       7,83%   R$ 160,55   R$ 0,00
LCI/LCA 88% CDI (isenta de IR)      R$ 733,92    12,23%       7,46%     R$ 0,00   R$ 0,00
Tesouro Prefixado 2029 (14,20%)     R$ 693,00    11,55%       6,81%   R$ 147,00  R$ 12,00
Tesouro Selic                       R$ 690,03    11,50%       6,76%   R$ 146,37   R$ 0,00
Tesouro Reserva                     R$ 688,05    11,47%       6,73%   R$ 145,95   R$ 0,00
CDB 100% CDI (banco grande)         R$ 688,05    11,47%       6,73%   R$ 145,95   R$ 0,00
Fundo DI (0,50% a.a.)               R$ 656,89    10,95%       6,23%   R$ 139,34  R$ 37,77  2 evento(s) de come-cotas
Tesouro IPCA+ 2035 (IPCA+6,65%)     R$ 584,29     9,74%       5,07%   R$ 123,94  R$ 12,00
Fundo DI caro (2,00% a.a.)          R$ 575,10     9,58%       4,93%   R$ 121,99  R$ 136,91  2 evento(s) de come-cotas
Poupanca                            R$ 500,58     8,34%       3,74%     R$ 0,00   R$ 0,00

  Melhor com resgate disponivel: CDB 110% CDI (banco medio) (R$ 756,86 liquidos, 12,61% a.a.)
  Diferenca para o pior da lista (Poupanca): R$ 256,28
```

---

## Estrutura de pastas

```
07-projeto-modelo/
├── README.md            você está aqui
├── indicadores.py       a fotografia do mercado: Selic, CDI, IPCA, taxas, FGC — cada um com fonte e data
├── tributos.py          IR regressivo, IOF de 30 dias, come-cotas, equivalência isento × tributado
├── produtos.py          os produtos da prateleira, cada um com seu rendimento, custo, garantia e carência
├── carteira.py          a interface de linha de comando: comparar, plano, impostos
└── test_simulador.py    31 testes: travam as REGRAS, não os indicadores
```

---

## O que cada decisão de projeto ensina

| Decisão | O que ela ensina |
|---|---|
| **`indicadores.py` separado, com `Fonte` e data** | Indicador sem data é desinformação. O mesmo código, com a Selic de 2020 (2%) em vez da de 2026 (14%), daria conselho oposto. Se você não sabe a data do número, não sabe o número. |
| **Imposto num módulo próprio, com a lei citada** | O produto é escolhido pelo líquido, e o líquido é definido por lei — que muda. Quando a lei mudar (a MP 1.303/2025 quase mudou), você troca um arquivo, não o programa inteiro. |
| **IOF cobrado antes do IR, e reduzindo a base dele** | Essa ordem é a lei e quase nenhum simulador da internet acerta. Um teste garante isso: `test_iof_reduz_a_base_do_ir`. |
| **Poupança que só conta meses cheios** | O "aniversário mensal" é a maior pegadinha do produto mais popular do país: resgatar no dia 29 zera o mês. Modelado em código, fica impossível esquecer. |
| **`carencia_dias` marcando `RESGATE BLOQUEADO`** | O produto que rende mais na tabela pode ser aquele que você não pode sacar. Rendimento sem liquidez não é comparável a rendimento com liquidez — o programa se recusa a declarar vencedor um produto travado. |
| **Custódia da B3 só sobre o que excede R$ 10 mil** | A isenção existe e muda a conta para quem tem pouco. Regra de negócio real, com teste de fronteira. |
| **Come-cotas simulado em caixa, não como fórmula** | O prejuízo do come-cotas não é o imposto: é o **juro que as cotas retiradas deixariam de render**. Só simulando o fluxo isso aparece. |
| **IPCA+ usando `(1+real)×(1+inflação)`** | Somar taxas é errado, e o erro cresce com o valor das taxas. Um teste explicita: `test_ipca_mais_usa_produto_e_nao_soma`. |
| **`--config` com validação de faixa** | Toda entrada externa é hostil até prova em contrário. O programa recusa `"CDI": 14` (que seria 1.400%) porque quem escreveu quis dizer `0.14`. |
| **Testes que travam regras, não valores** | Indicador muda toda semana; lei muda a cada anos. Testar o indicador daria falha semanal e ninguém olharia mais para os testes. |
| **Zero dependências** | Este programa vai rodar em 2031 sem `pip install` de nada. Dependência é dívida. |

---

## O que o programa **não** faz — e por quê

Um modelo honesto declara suas fronteiras:

- **Não considera dias úteis reais.** Converte dias corridos em úteis pela razão média
  252/365. A diferença contra o cálculo exato da B3 aparece na terceira casa decimal.
- **Não modela marcação a mercado.** Tesouro IPCA+ e Prefixado são simulados como se
  carregados até o vencimento na taxa contratada. Antes do vencimento, o preço oscila —
  e pode oscilar muito ([ver 12-renda-fixa.md](../12-renda-fixa.md)).
- **Não modela risco de crédito.** O CDB de 120% do CDI aparece na tabela como se o
  pagamento fosse certo. Não é: é por isso que ele paga 120%. O FGC cobre até
  R$ 250 mil por CPF e por instituição, com teto de R$ 1 milhão a cada 4 anos — e
  o pagamento leva semanas.
- **Não modela renda variável.** Ação e FII não têm retorno previsível; simulá-los com
  um número fixo seria mentira com aparência de matemática.
- **Não sabe da sua vida.** Não é recomendação de investimento. É uma calculadora
  honesta, e nada mais.

---

## Exercícios sobre o projeto

1. Rode `python3 carteira.py --prazos 179,180,181`. Explique o degrau que aparece.
2. Crie um cenário com a Selic em 8% e outro em 20%. Em qual deles a poupança deixa de
   ser a pior opção da lista? Por quê?
3. Acrescente em `produtos.py` uma classe `CDBLiquidezDiariaEscalonada`, que paga 90%
   do CDI nos primeiros 90 dias e 105% depois. Escreva o teste antes.
4. O `FundoDI` cobra taxa de administração mas não taxa de performance. Implemente-a
   (20% do que exceder o CDI) e mostre quanto ela custa em 5 anos.
5. Modifique o `cmd_plano` para aceitar `--objetivo` e `--prazo-objetivo` e sugerir o
   produto por prazo, em vez do texto fixo.
6. O modelo de come-cotas usa 182 dias. Implemente o calendário real (maio e novembro)
   e meça a diferença para um aporte feito em 1º de junho.
7. Escreva um teste que falharia se alguém trocasse `(1+real)*(1+inflação)-1` pela soma.

---

**Voltar para:** [../00-MAPA.md](../00-MAPA.md) · **Antes:** [../06-exemplos.md](../06-exemplos.md) · **Depois:** [../10-fundamentos.md](../10-fundamentos.md)
