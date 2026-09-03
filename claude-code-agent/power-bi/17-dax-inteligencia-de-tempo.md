# 17 · Inteligência de tempo

**Nível:** avançado
**Data:** 14/08/2026

Análise de negócio é análise no tempo. "Vendemos 10 milhões" não diz nada; "vendemos 10
milhões, 12% acima do mesmo mês do ano passado, com o acumulado do ano 4% abaixo da meta"
diz tudo. Este capítulo cobre como se produz a segunda frase — e por que ela dá errado
com tanta frequência.

---

## 1. Pré-requisito absoluto: a tabela de datas

Nada aqui funciona sem uma tabela de datas correta. Os requisitos são **cinco**, e todos
são obrigatórios:

1. **Uma linha por dia**, sem lacunas.
2. **Anos civis inteiros** — de 1º de janeiro a 31 de dezembro. Não pode começar em março.
3. **Coluna de data única**, com tipo Data (não texto, não Data/Hora).
4. **Marcada como tabela de data** (Ferramentas de Tabela → Marcar como tabela de data).
5. **Relacionada** ao fato pela coluna de data.

**Por que anos inteiros?** Porque `DATESYTD` e `SAMEPERIODLASTYEAR` calculam deslocamentos
sobre o conjunto completo de datas da tabela. Se o calendário começa em 01/03/2024,
o "ano até a data" de março de 2025 compara com um período que não existe integralmente,
e o resultado fica silenciosamente errado.

**Por que marcar?** A marcação diz ao motor que aquela é *a* dimensão de tempo, e faz com
que as funções de tempo removam automaticamente os filtros das outras colunas da tabela
antes de aplicar o novo período. Sem a marcação, um filtro residual (por exemplo, um
`Mes = "mar"` de uma segmentação) interfere no deslocamento, e você obtém resultados que
parecem aleatórios.

**Como criar:** em DAX ([`04-como-comecar.md`](04-como-comecar.md) §4.2), em M
([`13-power-query-e-m.md`](13-power-query-e-m.md) §6.5), com o **Bravo for Power BI** (um
clique), ou — a melhor opção em empresa — **como uma tabela no data warehouse**,
compartilhada por todos os modelos.

### Desligue a data/hora automática

**Arquivo → Opções → Arquivo Atual → Carregamento de Dados → desmarcar Data/hora
automática.**

Ela cria uma tabela de datas oculta **para cada coluna de data do modelo**. Num modelo com
`DataPedido`, `DataEntrega`, `DataVencimento` e `DataPagamento`, são quatro tabelas
ocultas, com hierarquias duplicadas e desperdício de memória proporcional à cardinalidade
de cada uma.

---

## 2. As funções, organizadas por pergunta

### 2.1 "Quanto no mesmo período do ano passado?"

```dax
Faturamento AA =
CALCULATE( [Faturamento Líquido], SAMEPERIODLASTYEAR( dCalendario[Data] ) )
```

Equivalente, e mais flexível:

```dax
Faturamento AA = CALCULATE( [Faturamento Líquido], DATEADD( dCalendario[Data], -1, YEAR ) )
```

`DATEADD` aceita `DAY`, `MONTH`, `QUARTER`, `YEAR` e qualquer número de períodos.
`SAMEPERIODLASTYEAR` é só um atalho para `DATEADD(..., -1, YEAR)`.

**Sempre proteja contra a ausência de base de comparação:**

```dax
Δ % vs AA =
VAR Atual    = [Faturamento Líquido]
VAR Anterior = [Faturamento AA]
RETURN
    IF(
        NOT ISBLANK( Atual ) && NOT ISBLANK( Anterior ) && Anterior <> 0,
        DIVIDE( Atual - Anterior, Anterior )
    )
```

Sem isso, no primeiro ano da série `Atual - BLANK()` devolve `Atual` e o gráfico mostra
crescimento onde não houve comparação.

### 2.2 "Quanto acumulado no ano?"

```dax
Faturamento YTD = CALCULATE( [Faturamento Líquido], DATESYTD( dCalendario[Data] ) )
```

Atalhos equivalentes: `TOTALYTD([M], dCalendario[Data])`, `TOTALQTD`, `TOTALMTD`.

**Ano fiscal** — segundo argumento com o fim do exercício:

```dax
Faturamento YTD Fiscal =
CALCULATE( [Faturamento Líquido], DATESYTD( dCalendario[Data], "06-30" ) )
```

Isso resolve a grande maioria dos calendários fiscais. Note o formato `"MM-DD"`.

### 2.3 "Quanto nos últimos N períodos?"

```dax
Faturamento MAT =
CALCULATE(
    [Faturamento Líquido],
    DATESINPERIOD( dCalendario[Data], MAX( dCalendario[Data] ), -12, MONTH )
)
```

`DATESINPERIOD(coluna, âncora, N, unidade)` é a função mais versátil do conjunto. Prefira-a
a `PREVIOUSMONTH`, `LASTQUARTER` e afins — ela é explícita e não depende de convenções.

### 2.4 "Do começo até aqui" (acumulado sem limite)

```dax
Faturamento Acumulado =
CALCULATE(
    [Faturamento Líquido],
    DATESBETWEEN( dCalendario[Data], BLANK(), MAX( dCalendario[Data] ) )
)
```

`BLANK()` como limite inferior significa "desde sempre".

### 2.5 "Qual o saldo no fim do período?" (semiaditivo)

Para estoque, saldo bancário, número de funcionários — grandezas que **não somam no
tempo**:

```dax
Estoque Fim de Período =
CALCULATE( SUM( fEstoque[Quantidade] ), LASTDATE( dCalendario[Data] ) )
```

Mais robusto, quando pode haver dias sem movimento:

```dax
Estoque Fim de Período =
CALCULATE(
    SUM( fEstoque[Quantidade] ),
    LASTNONBLANK( dCalendario[Data], CALCULATE( COUNTROWS( fEstoque ) ) )
)
```

Ou as funções dedicadas: `CLOSINGBALANCEMONTH`, `CLOSINGBALANCEQUARTER`,
`CLOSINGBALANCEYEAR`, e as variantes `OPENINGBALANCE*`.

### 2.6 "Média móvel"

```dax
Média Móvel 3M =
VAR Janela = DATESINPERIOD( dCalendario[Data], MAX( dCalendario[Data] ), -3, MONTH )
VAR N      = CALCULATE( DISTINCTCOUNT( dCalendario[AnoMes] ), Janela )
RETURN
    DIVIDE( CALCULATE( [Faturamento Líquido], Janela ), N )
```

Dividir pelos meses **efetivamente presentes** (e não por 3 fixo) evita o degrau no começo
da série.

---

## 3. As armadilhas do tempo

### 3.1 O mês corrente incompleto

**Sintoma:** no dia 3, o gráfico despenca. Diretoria entra em pânico.

```dax
Faturamento (meses fechados) =
VAR UltimoDiaFechado = EOMONTH( MAX( dCalendario[Data] ), -1 )
RETURN
    CALCULATE( [Faturamento Líquido], KEEPFILTERS( dCalendario[Data] <= UltimoDiaFechado ) )
```

**Melhor ainda** — uma coluna na `dCalendario` que marca se o período está fechado, e um
filtro de página. Assim o comportamento é visível e ajustável pelo usuário, em vez de
escondido numa medida.

### 3.2 A comparação injusta de dias úteis

Julho de 2026 tem 23 dias úteis; agosto tem 21. Comparar volumes brutos é enganoso.

```dax
Faturamento por Dia Útil =
VAR DiasUteis =
    CALCULATE( COUNTROWS( dCalendario ), dCalendario[DiaUtil] = "Sim" )
RETURN
    DIVIDE( [Faturamento Líquido], DiasUteis )
```

**Opinião do autor:** este indicador deveria estar em todo relatório mensal de vendas e
quase nunca está. Metade das "quedas" mensais que geram reunião são diferença de
calendário.

### 3.3 Datas futuras na tabela de fatos

Se a `dCalendario` vai até 2026 e há vendas com data de 2124 (defeito nº 4 do
projeto-modelo), essas linhas caem na "linha em branco" do relacionamento e somem dos
eixos temporais — **mas continuam no total**. Resultado: a soma dos meses não bate com o
total.

Trate na origem ou marque explicitamente, como faz o projeto-modelo.

### 3.4 Calendário curto demais

Se a `dCalendario` termina em 31/12/2026 e chega uma venda em 02/01/2027, ela some.
**Sempre gere o calendário a partir do mínimo e do máximo do fato**, com folga, ou até o
fim do ano corrente + 1.

### 3.5 Data/Hora em vez de Data

Uma coluna `datetime` com horas cria uma chave que não bate com a `dCalendario` (que tem
`00:00:00`). Resultado: **nenhuma linha se relaciona**. Converta para `date` no Power Query.

### 3.6 Filtro residual sem "marcar como tabela de data"

O caso clássico: uma segmentação de `Mes` ativa, e `SAMEPERIODLASTYEAR` devolvendo vazio.
A marcação faz o motor remover os outros filtros da tabela de datas antes do deslocamento.
Sem ela, o filtro de `Mes = "ago"` persiste e intersecta com o período deslocado.

---

## 4. Calendários não padrão

As funções nativas assumem o calendário gregoriano com meses civis. Quando o negócio usa
outro, elas **não servem** — e insistir nelas é a causa de erros que ninguém encontra.

### 4.1 Calendário fiscal simples (ano começa em outro mês)

Funciona com o segundo argumento de `DATESYTD` (§2.2), desde que os **meses** continuem
sendo meses civis.

Adicione colunas à `dCalendario`:

```dax
AnoFiscal = IF( MONTH([Data]) >= 7, YEAR([Data]) + 1, YEAR([Data]) )
MesFiscal = IF( MONTH([Data]) >= 7, MONTH([Data]) - 6, MONTH([Data]) + 6 )
```

### 4.2 Calendário 4-4-5 (varejo, indústria)

Semanas agrupadas em padrões de 4, 4 e 5 semanas por "mês". Um "mês" tem sempre 28 ou 35
dias e começa sempre na mesma semana.

**Aqui as funções nativas não funcionam.** A solução é aritmética de índices:

```dax
-- Na dCalendario: IndicePeriodo = número sequencial do período fiscal (0, 1, 2, ...)

Faturamento Período Anterior =
VAR PeriodoAtual = SELECTEDVALUE( dCalendario[IndicePeriodo] )
RETURN
    CALCULATE(
        [Faturamento Líquido],
        REMOVEFILTERS( dCalendario ),
        dCalendario[IndicePeriodo] = PeriodoAtual - 1
    )
```

```dax
Faturamento Ano Fiscal Anterior =
VAR PeriodoAtual = SELECTEDVALUE( dCalendario[IndicePeriodo] )
RETURN
    CALCULATE(
        [Faturamento Líquido],
        REMOVEFILTERS( dCalendario ),
        dCalendario[IndicePeriodo] = PeriodoAtual - 13   -- 13 períodos por ano
    )
```

```dax
-- YTD fiscal por índice
Faturamento YTD Fiscal =
VAR AnoAtual     = SELECTEDVALUE( dCalendario[AnoFiscal] )
VAR PeriodoAtual = SELECTEDVALUE( dCalendario[IndicePeriodo] )
RETURN
    CALCULATE(
        [Faturamento Líquido],
        REMOVEFILTERS( dCalendario ),
        dCalendario[AnoFiscal] = AnoAtual,
        dCalendario[IndicePeriodo] <= PeriodoAtual
    )
```

**O padrão geral, e ele vale para qualquer calendário exótico:**

> Coloque um **índice sequencial** na tabela de datas e faça a aritmética sobre o índice.
> É mais previsível, mais rápido e funciona para 4-4-5, 13 períodos, semanas ISO, ciclos
> de produção e qualquer coisa que o negócio invente.

**Opinião do autor:** eu uso índices mesmo em calendários gregorianos normais, para
comparações de período anterior. As funções nativas são convenientes, mas o índice é
explícito e nunca me surpreendeu.

### 4.3 Semanas ISO

`WEEKNUM` com o segundo argumento `21` devolve a semana ISO 8601, mas o "ano da semana ISO"
não é o ano civil (1º de janeiro pode pertencer à semana 52 do ano anterior). Calcule na
origem ou no Power Query, com cuidado.

---

## 5. Grupos de cálculo — a solução para a explosão de medidas

### 5.1 O problema

Você tem 12 medidas base (`Faturamento`, `Custo`, `Margem`, `Quantidade`…) e precisa de
cada uma em 6 variações de tempo (`YTD`, `AA`, `Δ`, `Δ%`, `MAT`, `Média Móvel`).

**12 × 6 = 72 medidas**, todas quase idênticas. Manutenção impossível: mudou a regra do
YTD? Altere 12 lugares.

### 5.2 A solução

> **Grupo de cálculo** (*calculation group*) — uma dimensão especial cujos membros são
> **modificações aplicáveis a qualquer medida**.

Você cria **um** grupo, "Tempo", com 6 itens. Um item é assim:

```dax
-- Item: "YTD"
CALCULATE( SELECTEDMEASURE(), DATESYTD( dCalendario[Data] ) )
```

```dax
-- Item: "Ano Anterior"
CALCULATE( SELECTEDMEASURE(), SAMEPERIODLASTYEAR( dCalendario[Data] ) )
```

```dax
-- Item: "Δ %"
VAR Atual = SELECTEDMEASURE()
VAR Anterior = CALCULATE( SELECTEDMEASURE(), SAMEPERIODLASTYEAR( dCalendario[Data] ) )
RETURN
    IF(
        NOT ISBLANK( Atual ) && NOT ISBLANK( Anterior ) && Anterior <> 0,
        DIVIDE( Atual - Anterior, Anterior )
    )
```

`SELECTEDMEASURE()` é um marcador: "a medida que estiver no visual". O grupo funciona
com **qualquer** medida.

**Resultado: 12 medidas + 6 itens = 18 objetos, em vez de 72.**

E o usuário ganha uma segmentação "Tempo" com que monta as combinações que quiser.

### 5.3 Formato dinâmico

Um problema: `Δ %` é percentual, mas a medida base é moeda. Resolve-se com a **cadeia de
formato** do item:

```dax
-- Propriedade "Format string expression" do item "Δ %"
"0.0%;-0.0%;0.0%"
```

```dax
-- E do item "YTD", herdando o formato da medida:
SELECTEDMEASUREFORMATSTRING()
```

### 5.4 Onde se cria

**No Desktop:** Exibição de Modelo → Cálculos → Novo grupo de cálculo (disponível
desde 2022).
**No Tabular Editor:** mais confortável para grupos grandes.

### 5.5 Avisos honestos

1. **Ordem de aplicação.** Com dois grupos de cálculo (por exemplo, "Tempo" e "Moeda"), a
   ordem de precedência importa e precisa ser definida explicitamente. Erre e os
   resultados ficam sutis e errados.
2. **Nem tudo funciona bem.** Grupos de cálculo interagem de forma complexa com medidas
   implícitas (arrastar uma coluna numérica direto para o visual) — por isso a recomendação
   de **desabilitar medidas implícitas** no modelo.
3. **Curva de aprendizado.** É um recurso avançado. Não o introduza no primeiro projeto.

**Ainda assim:** é a maior alavanca de produtividade em modelagem que existe hoje no
Power BI. Um modelo corporativo maduro sem grupo de cálculo é quase sempre um modelo com
300 medidas redundantes.

---

## 6. Parâmetros de campo — deixar o usuário escolher

Complementa os grupos de cálculo pelo outro lado: o usuário escolhe **qual dimensão** ou
**qual medida** o visual mostra.

**Modelagem → Novo parâmetro → Campos.**

```dax
-- Gerado automaticamente, e editável:
Métrica =
{
    ( "Faturamento",  NAMEOF('_Medidas'[Faturamento Líquido]), 0 ),
    ( "Margem",       NAMEOF('_Medidas'[Margem Bruta]),        1 ),
    ( "Quantidade",   NAMEOF('_Medidas'[Quantidade Vendida]),  2 ),
    ( "Ticket Médio", NAMEOF('_Medidas'[Ticket Médio]),        3 )
}
```

Arraste `Métrica` para o eixo de valores do visual e adicione uma segmentação. O usuário
troca a métrica sem que você precise de indicadores, visuais duplicados ou 4 páginas.

O mesmo funciona para dimensões:

```dax
Dimensão =
{
    ( "Categoria", NAMEOF(dProduto[Categoria]), 0 ),
    ( "Produto",   NAMEOF(dProduto[Produto]),   1 ),
    ( "UF",        NAMEOF(dCliente[UF]),        2 ),
    ( "Vendedor",  NAMEOF(dVendedor[Vendedor]), 3 )
}
```

**Combinação poderosa:** parâmetro de campo (qual métrica) + grupo de cálculo (qual
variação de tempo) + um único gráfico = 24 análises numa página.

---

## 7. Os cinco porquês: por que `SAMEPERIODLASTYEAR` exige uma tabela de datas separada?

1. **Por que não usar a coluna de data da própria tabela de fatos?**
   Porque a tabela de fatos só tem as datas em que **houve** evento. Um mês sem venda
   simplesmente não existe nela.

2. **Por que isso quebra o deslocamento?**
   Porque a função opera assim: pega o conjunto de datas do contexto atual, desloca cada
   uma em um ano, e devolve o conjunto resultante. Se o conjunto original tem lacunas, o
   deslocado também tem — e você compara períodos de tamanhos diferentes sem perceber.

3. **Por que o motor não preenche as lacunas sozinho?**
   Porque ele não tem como saber qual é o intervalo "correto". Deve ir até hoje? Até o fim
   do ano? Até a última data com dados? Cada resposta é válida em algum negócio, e nenhuma
   é universalmente certa.

4. **Por que a tabela precisa cobrir anos civis inteiros?**
   Porque `DATESYTD` calcula "do início do ano até a data atual" tomando o início do ano
   **como existente na tabela**. Se a tabela começa em março, o "início do ano" é março, e
   o YTD de todo mês fica errado — sem nenhum aviso.

5. **Parada legítima — o dado que não está lá.**
   No fundo, tudo isso é uma instância do problema mais geral do BI: **um sistema só sabe
   o que foi registrado**. A tabela de datas existe para materializar o tempo que passou
   independentemente de ter havido evento. É a mesma razão pela qual você precisa de uma
   dimensão de produtos para responder "quais produtos não venderam". O dado que não está
   lá é sempre o mais difícil de analisar — e o mais importante.

---

## 8. Autoteste

1. Cite os cinco requisitos de uma tabela de datas para inteligência de tempo.
2. Por que a tabela precisa cobrir anos civis inteiros?
3. O que "marcar como tabela de data" muda no comportamento do motor?
4. Por que desligar "Data/hora automática"?
5. Escreva `Faturamento AA` de duas formas equivalentes.
6. Por que `Δ %` precisa de proteção contra `BLANK`?
7. Como se resolve um ano fiscal que termina em 30 de junho?
8. Por que as funções nativas não servem para 4-4-5, e qual é o padrão que serve?
9. Explique a medida "por dia útil" e por que ela deveria ser padrão.
10. O que é um grupo de cálculo? Quantos objetos ele economiza no exemplo 12 × 6?
11. O que `SELECTEDMEASURE()` representa?
12. Para que serve um parâmetro de campo, e como ele se combina com grupos de cálculo?

---

**Próximo:** [`18-visualizacao.md`](18-visualizacao.md) — a parte que todo mundo acha que
é o assunto principal, e que só funciona depois de tudo isto.
