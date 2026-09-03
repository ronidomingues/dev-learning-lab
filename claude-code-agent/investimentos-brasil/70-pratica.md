# 70 · Prática — laboratórios e gabaritos

**Nível: iniciante a avançado** · *Atualizado em 20/08/2026*

Teoria sem mão na massa não fixa. Os laboratórios estão em ordem crescente de
dificuldade. Os quatro primeiros não exigem investir dinheiro real.

---

## Laboratório 1 — Descubra o seu número (30 min, sem dinheiro)

**Objetivo:** produzir os dois números que decidem toda a sua alocação.

1. Baixe os extratos bancários e as faturas de cartão dos últimos 3 meses.
2. Some as **saídas** de cada mês. Tire a média. Este é o seu `despesa_mensal`.
3. Multiplique por 3, 6 e 12. Estes são os três tamanhos possíveis da sua reserva.
4. Liste todas as suas dívidas com a taxa mensal de cada uma. Converta para anual:
   `(1 + i_m)^12 − 1`.
5. Compare com **11,5% ao ano**, o rendimento líquido aproximado de um pós-fixado hoje.

**Entregável:**
```
despesa_mensal = R$ ______
reserva alvo (6 meses) = R$ ______
dívida mais cara = ____% a.a.   -> quitar antes de investir? (S/N)
```

**Critério de sucesso:** você consegue dizer, sem consultar nada, quanto precisa ter em
liquidez diária.

---

## Laboratório 2 — Reproduza as contas do curso (20 min)

```bash
cd 07-projeto-modelo
python3 -m unittest -v          # esperado: Ran 31 tests ... OK
python3 carteira.py --valor 6000 --prazos 30,180,365,730,1825
```

**Perguntas a responder pela saída:**

1. Em 30 dias, qual a diferença em reais entre a poupança e o melhor produto líquido?
2. Em que prazo a LCI isenta deixa de ser a melhor opção entre os produtos com liquidez?
3. Quanto o Fundo DI de 2% a.a. custa, em reais, contra o Tesouro Selic em 5 anos?
4. Qual produto tem o **maior retorno real** em 1.825 dias, e por que ele não é
   automaticamente a resposta certa?

---

## Laboratório 3 — Quebre o simulador (45 min)

**Objetivo:** entender que a resposta depende do cenário, não da regra de bolso.

```bash
cd 07-projeto-modelo
echo '{"SELIC_META": 0.02, "SELIC_OVER": 0.019, "CDI": 0.019, "IPCA_12M": 0.10}' > selic2.json
python3 carteira.py --config selic2.json --prazos 365
```

**Perguntas:**

1. Quantos produtos têm retorno **real positivo** nesse cenário?
2. A poupança sai da última posição? Por quê? (dica: leia a fórmula em
   `indicadores.poupanca_mensal`)
3. Rode agora com Selic a 20% e inflação a 12%. O que muda na ordem?
4. Escreva, em três frases, o que esses dois cenários provam sobre "onde investir".

---

## Laboratório 4 — Calcule imposto na mão (30 min)

Sem rodar o programa. Depois confira com ele.

| # | Situação | Calcule |
|---|---|---|
| 1 | R$ 10.000 em CDB, resgate em 200 dias, rendimento bruto R$ 700 | IOF, IR e líquido |
| 2 | R$ 5.000 em CDB, resgate em 15 dias, rendimento bruto R$ 28 | IOF, IR e líquido |
| 3 | R$ 20.000 em LCI, resgate em 400 dias, rendimento bruto R$ 2.100 | IR e líquido |
| 4 | Venda de R$ 18.000 em ações no mês, lucro de R$ 3.000 | imposto devido |
| 5 | Venda de R$ 23.000 em ações no mês, lucro de R$ 3.000 | imposto devido |

Conferência:
```bash
python3 -c "
import tributos as t
print(1, round(t.iof(700,200),2), round(t.imposto_renda(700,200),2), round(t.liquido(700,200),2))
print(2, round(t.iof(28,15),2), round(t.imposto_renda(28,15),2), round(t.liquido(28,15),2))
print(3, round(t.imposto_renda(2100,400,isento=True),2))
"
```

---

## Laboratório 5 — O teste dos R$ 100 (2 dias, com dinheiro real)

Este é o laboratório mais importante do curso. Siga [04-como-comecar.md](04-como-comecar.md),
passos 1 e 2:

1. Aplique R$ 100 em Tesouro Selic ou Tesouro Reserva.
2. Anote **hora e data** da ordem e da liquidação.
3. Um dia útil depois, confirme a posição na Área do Investidor da B3.
4. Resgate R$ 50 e **cronometre** até o dinheiro estar na sua conta bancária.
5. Registre quanto de IOF foi cobrado.

**Entregável:**
```
Tempo real do resgate até a conta: ______ horas
IOF pago: R$ ______
A posição apareceu na B3? (S/N)
```

**Por que isso importa:** esse tempo medido, e não a promessa do site, é a liquidez da
sua reserva de emergência.

---

## Laboratório 6 — Compare uma oferta real (1 hora)

Pegue uma oferta de verdade — do app do seu banco ou da sua corretora.

1. Anote: produto, emissor (CNPJ), taxa, prazo, carência, FGC (sim/não).
2. Calcule o retorno **líquido** no seu prazo.
3. Compare com o Tesouro Selic no mesmo prazo.
4. Se for isento, use a tabela de equivalência do
   [05-manual-de-uso.md](05-manual-de-uso.md), seção 6.
5. Responda: **a diferença justifica o risco e a perda de liquidez?**

**Regra do laboratório:** se você não conseguir explicar em três frases de onde vem o
rendimento e quem paga se der errado, o exercício termina com "não invisto".

---

## Laboratório 7 — Escada de títulos (1 hora, papel)

Você tem R$ 40.000 e quer usar em 4 anos, mas não sabe exatamente quando.

1. Monte uma escada com quatro vencimentos anuais.
2. Escolha o produto de cada degrau (Tesouro, CDB, LCI) justificando por prazo e imposto.
3. Descreva o que você faz quando o primeiro degrau vencer.
4. Compare com "tudo num CDB de 4 anos": que riscos você trocou por quais?

---

## Laboratório 8 — Séries reais do Banco Central (avançado, 2 horas)

O BCB publica todas as séries pelo SGS, em API pública e gratuita.

```bash
# Selic diária (série 11), últimos 30 dias, em JSON
curl -s "https://api.bcb.gov.br/dados/serie/bcdata.sgs.11/dados/ultimos/30?formato=json"

# IPCA mensal (série 433)
curl -s "https://api.bcb.gov.br/dados/serie/bcdata.sgs.433/dados/ultimos/24?formato=json"

# CDI diário (série 12)
curl -s "https://api.bcb.gov.br/dados/serie/bcdata.sgs.12/dados/ultimos/30?formato=json"
```

**Exercícios:**

1. Acumule o CDI dos últimos 12 meses pelo produtório: `Π(1 + i_d/100)`.
2. Acumule o IPCA no mesmo período e calcule o **juro real realizado**.
3. Compare com o juro real que o curso usa (9,06%). Explique a diferença.
4. Escreva um script que atualize `indicadores.py` a partir dessas séries.

---

## Laboratório 9 — Sua política de investimento (1 hora)

Preencha o modelo da seção 7 de [24-carteira-e-alocacao.md](24-carteira-e-alocacao.md),
imprima, assine e guarde. Releia sempre que quiser mudar algo por causa de uma notícia.

**Critério de sucesso:** daqui a um ano, você consegue dizer se seguiu o que escreveu.

---

# Gabaritos comentados

## Autoteste do [01-introducao-leigo.md](01-introducao-leigo.md)

1. **Por que alguém paga para usar seu dinheiro, sem falar "juros".** Porque quem
   recebe pode usar esse dinheiro para produzir algo que vale mais depois; e porque
   você, ao abrir mão do consumo hoje e ao aceitar a chance de não receber de volta,
   precisa ser compensado por três coisas: espera, perda de poder de compra e risco.
2. **12% com inflação de 14%.** Perdeu. `1,12/1,14 − 1 = −1,75%` em termos reais. Note
   que a subtração ingênua daria −2%: o erro é pequeno aqui, mas cresce com as taxas.
3. **Quatro destinos:** governo, banco, empresa (emprestando), empresa (virando sócio).
   Só o último é renda variável.
4. **Regra dos 72 a 9%:** 72/9 = **8 anos**. (Exato: `ln2/ln1,09 = 8,04` anos.)
5. **2% ao mês garantido.** As três perguntas: *(a)* De onde vem o rendimento —
   qual atividade econômica o gera? *(b)* Quem é o emissor, tem registro no BCB ou na
   CVM, e o produto tem FGC? *(c)* Por que essa pessoa está me oferecendo 26,8% ao ano
   se ela poderia pegar dinheiro no mercado a 14%? A terceira pergunta é a que derruba
   quase todos os esquemas.
6. **Poupança "não perde".** Não perde em reais, perde em poder de compra em relação
   às alternativas: rende 8,34% quando o mesmo risco paga 11,5% líquidos. A perda é o
   custo de oportunidade, que não aparece no extrato.
7. **R$ 6.000 e fatura de R$ 3.000.** Quita a fatura primeiro. O rotativo custa
   centenas de por cento ao ano; nenhum investimento legal chega perto. Só depois
   investe o que sobrou.

## Autoteste do [02-pre-requisitos.md](02-pre-requisitos.md)

1. Porque o retorno é **certo** e igual à taxa da dívida, e é isento de imposto (você
   não paga IR por "economizar juros"). É o único investimento com retorno garantido
   conhecido de antemão.
2. Sobre a **despesa**. Você precisa cobrir o que gasta enquanto a renda não volta —
   a renda, por definição, é o que sumiu.
3. Indispensáveis: juros compostos e porcentagem. Ajudam muito: Python e estatística.
4. De 100 a 200 horas de estudo **mais** cerca de 2 anos de convivência com o mercado,
   incluindo pelo menos uma queda.
5. Porque a variável que falta não é informação, é **experiência emocional**: você só
   descobre sua tolerância real a perda quando vê o próprio dinheiro caindo.
6. Sim. Sem reserva, os R$ 6.000 **são** a reserva. A única decisão que resta é o
   veículo, e ele deve ter liquidez diária e risco de crédito mínimo.
7. "Qual é o meu objetivo com este dinheiro?" Sem objetivo, não existe critério para
   dizer se uma alocação está certa ou errada.

## Autoteste do [04-como-comecar.md](04-como-comecar.md)

1. Para testar o mecanismo — ordem, liquidação, extrato, resgate, tempo até a conta —
   com risco desprezível. Confiança por evidência, não por promessa.
2. "Liquidez diária" = você pode pedir todo dia útil; o dinheiro chega em D+0 ou D+1.
   "Resgate imediato" = chega na hora, inclusive fim de semana. Tesouro Selic é o
   primeiro caso; Tesouro Reserva, o segundo.
3. IOF de resgate em menos de 30 dias (no 12º dia, 60% do rendimento), incidindo
   **sobre o rendimento**, nunca sobre o principal. O IR veio depois, sobre o que sobrou.
4. **Aporte automático mensal.** Remove a decisão, que é onde a maioria erra.
5. Precisa declarar sim, em "Rendimentos Isentos e Não Tributáveis". Isento ≠ não
   declarável; a Receita recebe os dados dos bancos pela e-Financeira.
6. Nada. Se foi comprado para levar ao vencimento, a taxa contratada será honrada; a
   queda é marcação a mercado. Vender é que transformaria a oscilação em prejuízo.
7. **Um, no máximo dois.** Com R$ 6.000, mais produtos aumentam trabalho e custo sem
   reduzir risco relevante.

---

## Autoavaliação final do curso

Você está pronto para decidir sozinho quando conseguir, **sem consultar nada**:

- [ ] Explicar a diferença entre retorno nominal e real, e calcular um a partir do outro
- [ ] Dizer qual produto serve para cada prazo de objetivo
- [ ] Calcular o líquido de uma oferta com IR e IOF
- [ ] Converter uma taxa isenta em equivalente tributada
- [ ] Explicar marcação a mercado a alguém que acha que foi roubado
- [ ] Dizer o que o FGC cobre, até quanto, e em quanto tempo paga
- [ ] Reconhecer quatro sinais de fraude
- [ ] Dizer por que o juro real brasileiro é alto, e por que isso não é permanente
- [ ] Escrever sua política de investimento e segui-la por 12 meses

---

**Próximo:** [75-armadilhas.md](75-armadilhas.md)
