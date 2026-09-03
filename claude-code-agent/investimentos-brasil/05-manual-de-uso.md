# 05 · Manual de uso — referência consultável

**Nível: iniciante a intermediário** · *Atualizado em 20/08/2026*

Este arquivo é para **consulta**, não para leitura linear. Organizado por tarefa.

---

## 1. Como se lê a linguagem do mercado

Toda remuneração de renda fixa no Brasil se escreve de uma destas quatro formas:

| Notação | Nome | Significa | Você ganha mais se… |
|---|---|---|---|
| `110% do CDI` | pós-fixado | 110% de quanto render o CDI no período | os juros **subirem** |
| `CDI + 2,00%` | pós-fixado com spread | o CDI **mais** 2 pontos ao ano | os juros subirem |
| `14,20% a.a.` | prefixado | exatamente isso, aconteça o que acontecer | os juros **caírem** |
| `IPCA + 6,65%` | híbrido / indexado à inflação | a inflação do período **mais** 6,65% ao ano | você quer **proteção do poder de compra** |

**Armadilhas de leitura:**

- `IPCA + 6,65%` **não** é 4,44 + 6,65 = 11,09%. É `(1 + 0,0444) × (1 + 0,0665) − 1 = 11,39%`.
  Somar taxas é errado e o erro cresce quando as taxas são altas.
- `110% do CDI` **não** é "CDI + 10%". Se o CDI for 13,90%, é 15,29% — e não 23,90%.
- `a.a.` = ao ano · `a.m.` = ao mês · `a.d.` = ao dia · `p.p.` = pontos percentuais.
- **Ponto percentual ≠ porcentagem.** Sair de 10% para 12% é +2 p.p., mas +20%.
- Taxas de renda fixa brasileira são cotadas em **base 252 dias úteis**, não 360 ou 365.

**Conversões que você vai usar:**

```
mensal  -> anual :  (1 + i_m)^12 - 1
anual   -> mensal:  (1 + i_a)^(1/12) - 1
real    -> nominal: (1 + real) x (1 + inflação) - 1
nominal -> real   : (1 + nominal) / (1 + inflação) - 1     <- equação de Fisher
```

| Mensal | Anual equivalente |
|---|---|
| 0,5% | 6,17% |
| 0,67% | 8,34% |
| 1,0% | 12,68% |
| 1,1% | 14,03% |
| 2,0% | 26,82% |
| 3,0% | 42,58% |

Use a última linha como detector de fraude: quem promete "3% ao mês garantidos" está
prometendo 42,6% ao ano com garantia. Não existe.

---

## 2. Catálogo de produtos — ficha técnica

### 2.1 Renda fixa pública (Tesouro Direto)

| Título | Indexador | Serve para | Liquidez | IR | Custódia B3 |
|---|---|---|---|---|---|
| **Tesouro Reserva** | 100% Selic | reserva de emergência | 24×7, imediata | regressivo | confirmar na instituição |
| **Tesouro Selic** (LFT) | Selic + ágio pequeno | reserva, curto prazo | D+0 até 13h, senão D+1 | regressivo | 0,20% a.a. **isento até R$ 10 mil** |
| **Tesouro Prefixado** (LTN) | taxa fixa | apostar em queda de juros | D+1, com marcação a mercado | regressivo | 0,20% a.a. |
| **Tesouro Prefixado com Juros Semestrais** (NTN-F) | taxa fixa | renda periódica | D+1, marcação a mercado | regressivo, **a cada cupom** | 0,20% a.a. |
| **Tesouro IPCA+** (NTN-B Principal) | IPCA + taxa real | proteger poder de compra no longo prazo | D+1, marcação a mercado | regressivo | 0,20% a.a. |
| **Tesouro IPCA+ com Juros Semestrais** (NTN-B) | IPCA + taxa real | renda periódica indexada | D+1, marcação a mercado | regressivo, a cada cupom | 0,20% a.a. |
| **Tesouro Renda+** | IPCA + taxa real | aposentadoria: paga 240 parcelas mensais | D+1, com carência para o benefício | regressivo | isento até certo limite; confira |
| **Tesouro Educa+** | IPCA + taxa real | faculdade: paga 60 parcelas mensais | D+1 | regressivo | idem |

> **Risco soberano** significa: quem paga é o Tesouro Nacional. É o menor risco de
> crédito que existe em reais — o governo que emite a moeda da dívida sempre pode
> pagá-la em moeda. Isso **não** significa risco zero de perda: prefixados e IPCA+
> oscilam de preço antes do vencimento.

### 2.2 Renda fixa bancária

| Produto | Quem emite | IR | Garantia | Carência mínima |
|---|---|---|---|---|
| **CDB** | banco | regressivo | FGC até R$ 250 mil | livre (existe com liquidez diária) |
| **RDB** | banco/financeira | regressivo | FGC até R$ 250 mil | normalmente **sem** resgate antecipado |
| **LCI** | banco (lastro imobiliário) | **isento** para PF | FGC até R$ 250 mil | **6 meses** (36 meses se indexada a índice de preços) |
| **LCA** | banco (lastro agro) | **isento** para PF | FGC até R$ 250 mil | **6 meses** (12 meses se indexada a índice de preços) |
| **Poupança** | banco | isento | FGC até R$ 250 mil | rendimento só no aniversário mensal |
| **LC** (letra de câmbio) | financeira | regressivo | FGC até R$ 250 mil | conforme emissão |

*Carências conforme Resolução CMN 5.215, de 22/05/2025.*

### 2.3 Renda fixa privada sem FGC

| Produto | Emissor | IR | Risco |
|---|---|---|---|
| **Debênture comum** | empresa | regressivo | crédito da empresa. **Sem FGC** |
| **Debênture incentivada** | empresa de infraestrutura | **isento** para PF (Lei 12.431/2011) | crédito da empresa. **Sem FGC** |
| **CRI / CRA** | securitizadora | **isento** para PF | crédito do lastro. **Sem FGC** |

> A isenção desses papéis foi alvo da MP 1.303/2025, que os tributaria em 5%. A MP
> **caducou em outubro de 2025** sem virar lei; a isenção **segue vigente** em
> agosto de 2026. É tema recorrente no Congresso — reveja antes de comprar prazo longo.

### 2.4 Fundos e renda variável (referência rápida)

| Produto | Tributação | Peculiaridade |
|---|---|---|
| **Fundo DI / renda fixa** | regressivo + **come-cotas** em maio e novembro | taxa de administração corrói; acima de 0,5% a.a. raramente se justifica |
| **Fundo multimercado** | regressivo + come-cotas | também taxa de performance (tipicamente 20% do que exceder o CDI) |
| **Fundo de ações** | **15% no resgate**, sem come-cotas | não tem isenção de R$ 20 mil |
| **Ação** | 15% sobre ganho; **isento até R$ 20 mil vendidos no mês** | imposto apurado e pago **por você** (DARF) |
| **ETF de ações** | 15% sobre ganho, **sem** a isenção de R$ 20 mil | DARF por sua conta |
| **FII** | 20% sobre ganho de capital; **dividendos isentos** se cumpridos os requisitos legais | dividendos mensais |
| **Day trade** | 20%, com 1% retido na fonte ("dedo-duro") | prejuízo só compensa com day trade |

---

## 3. Tributação — tabelas de consulta

### 3.1 IR regressivo (Lei 11.033/2004) — renda fixa e fundos

| Prazo da aplicação | Alíquota sobre o **rendimento** |
|---|---|
| até 180 dias | 22,5% |
| 181 a 360 dias | 20,0% |
| 361 a 720 dias | 17,5% |
| acima de 720 dias | 15,0% |

**Atalho de gente experiente:** o dia 181, o 361 e o 721 valem dinheiro. Resgatar no
dia 180 em vez do 181 custa 2,5 pontos do rendimento inteiro. Antes de resgatar,
**olhe a data da aplicação**. Sobre R$ 1.000 de rendimento, esperar um dia vale R$ 25.

### 3.2 IOF regressivo (Decreto 6.306/2007) — resgates em menos de 30 dias

| Dia | % do rendimento | Dia | % | Dia | % |
|---|---|---|---|---|---|
| 1 | 96% | 11 | 63% | 21 | 30% |
| 2 | 93% | 12 | 60% | 22 | 26% |
| 3 | 90% | 13 | 56% | 23 | 23% |
| 4 | 86% | 14 | 53% | 24 | 20% |
| 5 | 83% | 15 | 50% | 25 | 16% |
| 6 | 80% | 16 | 46% | 26 | 13% |
| 7 | 76% | 17 | 43% | 27 | 10% |
| 8 | 73% | 18 | 40% | 28 | 6% |
| 9 | 70% | 19 | 36% | 29 | 3% |
| 10 | 66% | 20 | 33% | **30** | **0%** |

O IOF incide **antes** do IR e reduz a base dele. Nunca incide sobre o principal.
LCI, LCA e poupança são isentas de IOF; a poupança tem sua própria punição
(o aniversário mensal).

### 3.3 Come-cotas

- Ocorre no **último dia útil de maio e de novembro**.
- Alíquota: **15%** em fundos de longo prazo, **20%** em fundos de curto prazo.
- O fundo "come" cotas suas para pagar o imposto — o saldo em R$ cai.
- No resgate, cobra-se apenas a **diferença** entre a alíquota da tabela regressiva e o
  que já foi antecipado.
- **Fundos de ações, ETFs, ações, FIIs, CDB, LCI, LCA e Tesouro Direto NÃO têm come-cotas.**

O custo real do come-cotas não é o imposto — é o **juro sobre o imposto antecipado**,
que você deixa de ganhar. Ver a medição em [06-exemplos.md](06-exemplos.md), exemplo 7.

### 3.4 Isenções vigentes para pessoa física (agosto de 2026)

| Isento | Base legal |
|---|---|
| LCI, LCA | Lei 11.033/2004, art. 3º; Lei 11.076/2004 |
| CRI, CRA | Lei 11.033/2004, art. 3º |
| Debêntures incentivadas | Lei 12.431/2011 |
| Poupança | Lei 8.981/1995, art. 68 |
| Dividendos de FII (com requisitos: ≥ 50 cotistas, cotas negociadas em bolsa, cotista com < 10% do fundo) | Lei 11.033/2004, art. 3º |
| Venda de até R$ 20 mil em **ações** por mês (não vale para ETF nem day trade) | Lei 11.033/2004 |

E o que **mudou** em 2026: a Lei 15.270/2025 ampliou a isenção do IRPF para renda
mensal de até R$ 5.000, criou o IRPF mínimo para altas rendas e passou a reter **10%
na fonte** sobre dividendos que excedam R$ 50 mil por mês pagos por uma mesma empresa
a uma mesma pessoa física. Para quem investe R$ 6.000, o efeito prático é nulo — mas
é a mudança tributária relevante do ano.

---

## 4. Fundo Garantidor de Créditos (FGC) — o que é e o que não é

| Item | Regra vigente (2026) |
|---|---|
| Cobertura | **R$ 250.000 por CPF, por instituição** (ou por conglomerado financeiro) |
| Teto global | **R$ 1.000.000 por CPF a cada 4 anos** |
| O que cobre | conta corrente, poupança, CDB, RDB, LC, LCI, LCA, letras hipotecárias |
| O que **não** cobre | Tesouro Direto (não precisa), fundos de investimento, ações, FII, debêntures, CRI, CRA, previdência |
| Inclui rendimentos? | sim, principal **+** rendimento até a data da liquidação |
| Prazo de pagamento | não há prazo legal fixo; na prática, semanas a meses |
| Quem paga | os próprios bancos, via contribuição mensal — **não é o Tesouro** |

**Mudança de 2026:** a partir de junho de 2026 entraram em vigor regras do CMN que
criam o **Ativo de Referência (AR)** — bancos que captam muito com produtos cobertos
pelo FGC mas têm ativos de baixa qualidade passam a ser obrigados a alocar parte dos
recursos em títulos públicos. É uma resposta regulatória direta ao caso de liquidação
de banco de 2025. Efeito para você: menos emissores exóticos pagando taxas absurdas.

**Como usar o FGC na prática:**

- Some **principal + rendimento projetado** ao decidir quanto colocar num emissor.
  Aplicar exatos R$ 250 mil significa deixar o rendimento fora da cobertura.
- Bancos do **mesmo conglomerado** contam como um só. Confira o CNPJ do emissor.
- Com R$ 6.000, o FGC não é restrição — é conforto. Não distribua o valor por vários
  bancos "por causa do FGC": não há motivo.

---

## 5. Calendário do investidor

| Quando | O quê |
|---|---|
| A cada ~45 dias, 8 vezes por ano | **Reunião do Copom** — define a Selic. Calendário publicado pelo BCB com um ano de antecedência |
| Toda segunda-feira, pela manhã | **Boletim Focus** — projeções do mercado para Selic, IPCA, PIB e câmbio |
| Por volta do dia 10 de cada mês | **IPCA** do mês anterior (IBGE) |
| Último dia útil de **maio** e de **novembro** | **Come-cotas** em fundos |
| Fevereiro a março | **Informes de rendimento** das instituições |
| Março a maio | **Declaração do IRPF** |
| Até o último dia útil do mês seguinte | **DARF** de ganho em ações/ETF/FII, se houve lucro tributável |
| 9h30 às 18h, dias úteis | Janela de preços do Tesouro Direto (exceto Tesouro Reserva, 24×7) |
| 10h às 17h (+ after market 17h30–18h) | Pregão da B3 |

---

## 6. Fórmulas de bolso

```
Valor futuro:            VF = VP x (1 + i)^n
Regra dos 72:            anos para dobrar ≈ 72 / taxa_anual_em_%
Juro real (Fisher):      real = (1 + nominal) / (1 + inflação) - 1
Taxa nominal do IPCA+:   nominal = (1 + real) x (1 + IPCA) - 1
Isento -> tributado:     % equivalente = % isento / (1 - alíquota_IR)
Rendimento líquido:      líquido = bruto x (1 - IOF%) x (1 - IR%)
Reserva de emergência:   despesa_mensal x meses (3 a 12, conforme estabilidade)
```

**Tabela de equivalência isento × tributado** (a mais útil de todas):

| Produto isento paga | Empata com um tributado de… (até 180d) | (181–360d) | (361–720d) | (>720d) |
|---|---|---|---|---|
| 80% do CDI | 103,2% | 100,0% | 97,0% | 94,1% |
| 85% do CDI | 109,7% | 106,2% | 103,0% | 100,0% |
| 88% do CDI | 113,5% | 110,0% | 106,7% | 103,5% |
| 90% do CDI | 116,1% | 112,5% | 109,1% | 105,9% |
| 95% do CDI | 122,6% | 118,7% | 115,2% | 111,8% |

*(Gerada por `python3 carteira.py impostos` no [07-projeto-modelo](07-projeto-modelo/).)*

---

## 7. Atalhos que só quem usa há anos conhece

1. **Compre no dia 1º, resgate depois do dia 181.** As fronteiras do IR e do IOF valem
   mais que quase toda escolha de produto para prazos curtos.
2. **Tesouro Selic acima de R$ 10 mil paga custódia; abaixo, não.** Se você tem
   R$ 40 mil de reserva, faz sentido dividir entre Tesouro Selic (até 10 mil) e CDB
   de liquidez diária.
3. **Antes de comprar CDB, compare com a LCI do mesmo banco pela tabela de equivalência.**
   Metade das vezes a LCI ganha, e o gerente ofereceu o CDB.
4. **Taxa de administração de fundo DI acima de 0,3% a.a. é indefensável** com Tesouro
   Selic existindo. Acima de 1%, é transferência de renda de você para a instituição.
5. **Marcação a mercado só te machuca se você vender.** Título levado ao vencimento
   entrega a taxa contratada, ponto.
6. **Compare `IPCA+` com o "juro real projetado"**, não com o CDI atual. São regimes
   diferentes de risco.
7. **Ao pedir cotação de renda fixa numa corretora, pergunte a taxa "líquida de
   rebate".** Existe comissão embutida na taxa que você recebe.
8. **A B3 é a sua auditoria.** Se não está na Área do Investidor, questione por escrito.
9. **Guarde o preço médio das ações antes de trocar de corretora.** Ninguém guarda por você.
10. **Nunca resgate no dia 29 da poupança.** Espere o aniversário: um dia vale um mês inteiro.

---

## 8. O que está obsoleto

| Obsoleto | Substituto | Desde |
|---|---|---|
| CEI (Canal Eletrônico do Investidor) | **Área do Investidor da B3** | 2021 |
| Cobrança **semestral** da custódia do Tesouro Direto | cobrança só em resgate, vencimento ou cupom | 31/12/2024 |
| Carência de **9 meses** em LCI/LCA sem índice de preços | **6 meses** | Resolução CMN 5.215, 22/05/2025 |
| "Fundo DI é onde se guarda a reserva" | Tesouro Selic / Tesouro Reserva / CDB de liquidez diária | desde que a taxa de custódia caiu e surgiram CDBs a 100% do CDI |
| Poupança como padrão do brasileiro | qualquer pós-fixado a 100% do CDI | matematicamente, desde sempre; culturalmente, em curso |
| Tributação uniforme de 17,5%/18% da MP 1.303/2025 | **não entrou em vigor** — a MP caducou em outubro de 2025 | 10/2025 |

---

## Autoteste

1. `IPCA + 6,65%` com IPCA de 5% dá quanto de taxa nominal? Mostre a conta.
2. Qual alíquota de IR incide num resgate no 361º dia? E no 360º?
3. Você tem R$ 250 mil num CDB e ele rendeu R$ 30 mil. O banco quebra. Quanto o FGC paga?
4. Uma LCA paga 85% do CDI. A partir de qual % do CDI um CDB de 2 anos passa a ser melhor?
5. Cite três produtos sem come-cotas e dois com.
6. Por que "somar" IPCA e a taxa real dá um número errado, e o erro é para mais ou para menos?
7. Qual mudança regulatória de 2025 encurtou a carência de LCI e LCA, e para quanto?
8. Por que a custódia do Tesouro Direto pode ser zero para você e não para outra pessoa?

---

**Fontes consultadas em 20/08/2026:** Lei 11.033/2004 (IR regressivo e isenções);
Decreto 6.306/2007 (IOF); Lei 12.431/2011 (debêntures incentivadas); Lei 15.270/2025
(IRPF e dividendos); Resolução CMN 5.215/2025 (carência LCI/LCA); regras e tarifas do
Tesouro Direto e da B3; FGC — limites vigentes e novas regras de captação em vigor
desde junho de 2026; Câmara dos Deputados — perda de eficácia da MP 1.303/2025.
Links em [95-referencias.md](95-referencias.md).

**Próximo:** [06-exemplos.md](06-exemplos.md)
