# 06 · Exemplos

**Nível:** iniciante → avançado
**Data:** 14/08/2026
**Formato:** cada exemplo tem **problema → solução completa → explicação → armadilha**.

> **Sobre "executável".** Em Power BI, "código executável" significa DAX e M completos que
> você cola e funcionam, mais os cliques necessários. Nenhum trecho abaixo tem `...`
> omitindo parte essencial. **Não foram executados nesta máquina** (ambiente Linux, ver
> [`00-MAPA.md`](00-MAPA.md)); são código que escrevo e uso há anos, revisado para a
> sintaxe vigente. Onde há risco de variação por versão, está anotado.

**Modelo assumido nos exemplos** (o mesmo do [`07-projeto-modelo/`](07-projeto-modelo/README.md)):

```
dCalendario[Date, Ano, NumMes, Mes, AnoMes, Trimestre]
dProduto[SK_Produto, Codigo, Produto, Categoria, Linha, CustoPadrao]
dCliente[SK_Cliente, CNPJ, Cliente, Segmento, UF, Cidade]
dVendedor[SK_Vendedor, Vendedor, Equipe, Email]
fVendas[Date, SK_Produto, SK_Cliente, SK_Vendedor, NF, Quantidade,
        PrecoUnitario, Desconto, CustoUnitario, Tipo]      -- Tipo: "Venda" | "Devolucao"
fMetas[Ano, NumMes, SK_Vendedor, MetaValor]
```

---

## Índice

| # | Exemplo | Nível |
|---|---|---|
| 1 | Faturamento, custo, margem — as três primeiras medidas | iniciante |
| 2 | Percentual do total (e as três respostas diferentes) | iniciante |
| 3 | Comparação com o ano anterior, sem furos | intermediário |
| 4 | Acumulado no ano e média móvel 12 meses | intermediário |
| 5 | Top N com "Outros" agrupado | intermediário |
| 6 | Curva ABC (Pareto) dinâmica | avançado |
| 7 | Metas em granularidade diferente do fato | avançado |
| 8 | Segmentação de clientes por RFM simplificado | avançado |
| 9 | Parâmetro *what-if*: simulador de desconto | intermediário |
| 10 | Duas datas na mesma tabela (`USERELATIONSHIP`) | avançado |
| 11 | Segurança por linha (RLS) dinâmica | avançado |
| 12 | Combinar 40 planilhas de uma pasta (M) | intermediário |
| 13 | Consumir uma API REST paginada (M) | avançado |
| 14 | **Caso real:** carga incremental de 400 milhões de linhas | produção |
| 15 | **Caso real:** relatório de OEE de uma planta industrial | produção |

---

## Exemplo 1 — Faturamento, custo, margem

**Problema.** Você tem preço, quantidade, desconto e custo por linha. Precisa das três
medidas fundamentais, e elas precisam funcionar em qualquer recorte.

**Solução.**

```dax
Faturamento Bruto =
SUMX( fVendas, fVendas[Quantidade] * fVendas[PrecoUnitario] )
```

```dax
Descontos =
SUMX( fVendas, fVendas[Quantidade] * fVendas[PrecoUnitario] * fVendas[Desconto] )
```

```dax
Faturamento Líquido = [Faturamento Bruto] - [Descontos]
```

```dax
Custo Total =
SUMX( fVendas, fVendas[Quantidade] * fVendas[CustoUnitario] )
```

```dax
Margem Bruta = [Faturamento Líquido] - [Custo Total]
```

```dax
Margem % = DIVIDE( [Margem Bruta], [Faturamento Líquido] )
```

**Explicação.**
`SUMX` é um **iterador**: percorre `fVendas` linha a linha, avalia a expressão em cada uma
e soma. Ele cria um **contexto de linha**, que é o que permite multiplicar duas colunas da
mesma linha. `SUM` sozinho não faria isso — `SUM(a) * SUM(b)` está errado, porque
soma-de-produtos ≠ produto-de-somas.

`Margem %` é **medida**, não coluna. Se fosse coluna, o total somaria percentuais.

**Armadilha.** Note que `Margem %` reutiliza `[Margem Bruta]` e `[Faturamento Líquido]` em
vez de repetir as fórmulas. Isso não é elegância: é **manutenibilidade**. No dia em que a
definição de "líquido" mudar (passar a descontar frete), você muda em **um** lugar. Medidas
que se referenciam formam uma árvore de dependência — desenhe-a de propósito.

---

## Exemplo 2 — Percentual do total, e as três respostas diferentes

**Problema.** "Qual o percentual de cada categoria no total?" Parece uma pergunta. São três.

**Solução.**

```dax
-- (a) % sobre o total de TUDO, ignorando qualquer filtro do relatório
% do Total Geral =
DIVIDE(
    [Faturamento Líquido],
    CALCULATE( [Faturamento Líquido], REMOVEFILTERS() )
)
```

```dax
-- (b) % sobre o total do que está VISÍVEL no visual (respeita segmentações)
% do Total Visível =
DIVIDE(
    [Faturamento Líquido],
    CALCULATE( [Faturamento Líquido], ALLSELECTED() )
)
```

```dax
-- (c) % sobre o total da linha-pai da hierarquia (numa matriz)
% do Pai =
VAR Pai =
    CALCULATE(
        [Faturamento Líquido],
        REMOVEFILTERS( dProduto[Produto] )
    )
RETURN
    DIVIDE( [Faturamento Líquido], Pai )
```

**Explicação.**
Todas as três dividem a mesma coisa; a diferença está no **denominador**, e o denominador
é sempre uma **manipulação de contexto de filtro**.

- `REMOVEFILTERS()` sem argumento apaga **todos** os filtros do modelo.
- `ALLSELECTED()` apaga os filtros vindos das linhas/colunas do visual, mas **preserva**
  os filtros externos (segmentações, filtros de página).
- `REMOVEFILTERS(coluna)` apaga só aquela coluna, deixando as outras da hierarquia.

**Qual usar?** Na dúvida, **(b)**. É o que o usuário espera: quando ele filtra "2026" e vê
"Tintas = 42%", ele quer 42% de 2026, não 42% de todos os anos. **Opinião do autor:** a
maioria dos relatórios usa (a) por acidente, e ninguém percebe até alguém filtrar.

**Armadilha.** `ALL()` e `REMOVEFILTERS()` são sinônimos funcionais quando usadas como
modificador de filtro. `REMOVEFILTERS` é mais legível porque diz o que faz; `ALL` também
serve como função de tabela. Prefira `REMOVEFILTERS` dentro de `CALCULATE`.

---

## Exemplo 3 — Comparação com o ano anterior, sem furos

**Problema.** Mostrar o crescimento contra o mesmo período do ano anterior, e não mostrar
número enganoso quando o período anterior não existe.

**Solução.**

```dax
Faturamento AA =
CALCULATE(
    [Faturamento Líquido],
    SAMEPERIODLASTYEAR( dCalendario[Date] )
)
```

```dax
Δ vs AA =
VAR Atual    = [Faturamento Líquido]
VAR Anterior = [Faturamento AA]
RETURN
    IF(
        NOT ISBLANK( Anterior ) && NOT ISBLANK( Atual ),
        Atual - Anterior
    )
```

```dax
Δ % vs AA =
VAR Atual    = [Faturamento Líquido]
VAR Anterior = [Faturamento AA]
RETURN
    IF(
        NOT ISBLANK( Anterior ) && Anterior <> 0,
        DIVIDE( Atual - Anterior, Anterior )
    )
```

```dax
-- Versão que ignora o mês corrente incompleto (evita a "queda" falsa do último mês)
Faturamento Líquido (meses fechados) =
VAR UltimoDiaFechado = EOMONTH( TODAY(), -1 )
RETURN
    CALCULATE(
        [Faturamento Líquido],
        KEEPFILTERS( dCalendario[Date] <= UltimoDiaFechado )
    )
```

**Explicação.**
`SAMEPERIODLASTYEAR` desloca o conjunto de datas do contexto atual em exatamente um ano.
Exige tabela de datas **contínua**, cobrindo anos inteiros, e **marcada como tabela de
data** — sem isso, ela mente em silêncio.

O `IF` com `ISBLANK` evita o vício clássico: no primeiro ano da série, `Anterior` é vazio,
`Atual - BLANK()` devolve `Atual`, e o gráfico exibe "crescimento de 100%" onde não houve
comparação alguma.

**Armadilha.** A medida do "mês corrente incompleto" resolve um problema político, não
técnico: no dia 5 do mês, o gráfico mostra uma queda vertical, o diretor entra em pânico,
e alguém perde a manhã explicando que faltam 25 dias. **Trate isso no modelo, não em
reunião.** Use `KEEPFILTERS` para *intersectar* com o filtro existente em vez de
substituí-lo.

---

## Exemplo 4 — Acumulado no ano e média móvel 12 meses

**Problema.** Suavizar sazonalidade e mostrar a tendência.

**Solução.**

```dax
Faturamento YTD =
CALCULATE( [Faturamento Líquido], DATESYTD( dCalendario[Date] ) )
```

```dax
-- Ano fiscal terminando em 30 de junho
Faturamento YTD Fiscal =
CALCULATE( [Faturamento Líquido], DATESYTD( dCalendario[Date], "06-30" ) )
```

```dax
-- MAT: Moving Annual Total (acumulado dos últimos 12 meses)
Faturamento MAT =
CALCULATE(
    [Faturamento Líquido],
    DATESINPERIOD(
        dCalendario[Date],
        MAX( dCalendario[Date] ),
        -12,
        MONTH
    )
)
```

```dax
-- Média móvel de 3 meses, alinhada ao fim do período
Média Móvel 3M =
VAR UltimaData = MAX( dCalendario[Date] )
VAR Janela =
    DATESINPERIOD( dCalendario[Date], UltimaData, -3, MONTH )
VAR NMeses =
    CALCULATE( DISTINCTCOUNT( dCalendario[AnoMes] ), Janela )
RETURN
    DIVIDE( CALCULATE( [Faturamento Líquido], Janela ), NMeses )
```

**Explicação.**
`DATESYTD` aceita um segundo argumento com o fim do ano fiscal no formato `"MM-DD"`. Isso
resolve 90% dos casos de calendário fiscal sem tabela auxiliar.

`DATESINPERIOD` é mais flexível que `PREVIOUSMONTH` e companhia porque você declara a
âncora e o tamanho da janela. É a função que uso em quase tudo que é "últimos N".

`Média Móvel 3M` divide pelo número de meses **efetivamente presentes**, não por 3 fixo.
Isso importa no começo da série, onde só há 1 ou 2 meses.

**Armadilha.** `MAX( dCalendario[Date] )` dentro da medida devolve a última data **do
contexto atual**. Se o visual está por mês, é o último dia daquele mês; se está no total,
é o último dia de todo o período. Esse comportamento é o que faz a medida funcionar em
qualquer granularidade — e é o que a torna incompreensível para quem não domina contexto.

---

## Exemplo 5 — Top N com "Outros" agrupado

**Problema.** Mostrar os 10 maiores clientes e agrupar o resto em "Outros", sem perder o
total.

**Solução.**

**Passo 1** — Crie um parâmetro numérico: **Modelagem → Novo parâmetro → Numérico**,
nome `N`, de 3 a 50, incremento 1, com segmentação na página.

**Passo 2** — Uma tabela calculada com a categoria de exibição:

```dax
Ranking Cliente =
VAR TopClientes =
    TOPN(
        SELECTEDVALUE( 'N'[N Valor], 10 ),
        ALLSELECTED( dCliente[Cliente] ),
        [Faturamento Líquido],
        DESC
    )
RETURN
    ...
```

Na prática, o padrão que funciona melhor é **uma medida que decide**, com uma tabela
auxiliar desconectada:

```dax
-- Tabela desconectada, criada com "Inserir dados"
-- dRotulo[Rotulo, Ordem]:  "Top N" / 1  ;  "Outros" / 2
```

```dax
Faturamento por Rótulo =
VAR TopN = SELECTEDVALUE( 'N'[N Valor], 10 )
VAR Rotulo = SELECTEDVALUE( dRotulo[Rotulo] )
VAR ClientesVisiveis = ALLSELECTED( dCliente[Cliente] )
VAR ComValor =
    ADDCOLUMNS( ClientesVisiveis, "@Fat", [Faturamento Líquido] )
VAR Topo = TOPN( TopN, ComValor, [@Fat], DESC )
RETURN
    SWITCH(
        Rotulo,
        "Top N",  SUMX( Topo, [@Fat] ),
        "Outros", SUMX( EXCEPT( ComValor, Topo ), [@Fat] )
    )
```

**Versão simples**, quando o visual já lista os clientes e você só quer marcar o resto:

```dax
Cliente Exibido =
VAR TopN = SELECTEDVALUE( 'N'[N Valor], 10 )
VAR Posicao =
    RANKX( ALLSELECTED( dCliente[Cliente] ), [Faturamento Líquido], , DESC, DENSE )
RETURN
    IF( Posicao <= TopN, SELECTEDVALUE( dCliente[Cliente] ), "Outros" )
```

**Explicação.**
`TOPN` devolve uma **tabela**. `EXCEPT` devolve a diferença entre duas tabelas. A soma das
duas partes é sempre o total — propriedade que você deve **verificar** antes de publicar.

**Armadilha.** `TOPN` não resolve empates: se houver empate na posição N, ele devolve
**mais** de N linhas. Documente ou desempate com uma coluna extra:
`TOPN( n, tabela, [Medida], DESC, dCliente[Cliente], ASC )`.

---

## Exemplo 6 — Curva ABC (Pareto) dinâmica

**Problema.** Classificar produtos em A (até 80% do faturamento acumulado), B (até 95%) e
C (o resto) — **recalculando conforme os filtros do usuário**.

**Solução.**

```dax
Faturamento Acumulado (Pareto) =
VAR ProdutosVisiveis =
    ADDCOLUMNS(
        ALLSELECTED( dProduto[Produto] ),
        "@Fat", [Faturamento Líquido]
    )
VAR FatAtual = [Faturamento Líquido]
VAR MaioresOuIguais =
    FILTER( ProdutosVisiveis, [@Fat] >= FatAtual )
RETURN
    SUMX( MaioresOuIguais, [@Fat] )
```

```dax
% Acumulado (Pareto) =
DIVIDE(
    [Faturamento Acumulado (Pareto)],
    CALCULATE( [Faturamento Líquido], ALLSELECTED( dProduto[Produto] ) )
)
```

```dax
Classe ABC =
VAR Acum = [% Acumulado (Pareto)]
RETURN
    SWITCH(
        TRUE(),
        ISBLANK( Acum ),  BLANK(),
        Acum <= 0.80,     "A",
        Acum <= 0.95,     "B",
        "C"
    )
```

```dax
-- Para usar a classe como filtro/eixo, agrupe as medidas por classe:
Faturamento Classe A =
VAR Produtos =
    ADDCOLUMNS( ALLSELECTED( dProduto[Produto] ), "@Fat", [Faturamento Líquido] )
VAR Total = SUMX( Produtos, [@Fat] )
VAR ComAcum =
    ADDCOLUMNS(
        Produtos,
        "@Acum", VAR f = [@Fat]
                 RETURN DIVIDE( SUMX( FILTER( Produtos, [@Fat] >= f ), [@Fat] ), Total )
    )
RETURN
    SUMX( FILTER( ComAcum, [@Acum] <= 0.80 ), [@Fat] )
```

**Explicação.**
O truque do Pareto em DAX é o *acumulado por ordem de grandeza*: para cada produto, some
todos os que faturam **mais ou igual** a ele. Isso reproduz a soma acumulada da curva sem
precisar de índice pré-calculado, e — crucialmente — **respeita os filtros**, porque parte
de `ALLSELECTED`.

**Armadilha.** Esta é uma medida **cara**: para cada linha do visual ela varre a tabela
virtual inteira. Com 50 produtos é instantâneo; com 200 mil SKUs, o visual trava. Nesse
caso, calcule a classe ABC **na origem** (SQL ou Power Query) aceitando que ela fique
estática, ou limite o visual a uma dimensão de baixa cardinalidade. Ver
[`22-desempenho.md`](22-desempenho.md).

---

## Exemplo 7 — Metas em granularidade diferente do fato

**Problema.** As vendas são diárias e por produto. As metas são **mensais e por vendedor**.
Você não pode relacionar as duas tabelas diretamente sem quebrar tudo.

**Solução.**

**Passo 1 — modelo.** Crie uma tabela `dMes` (uma linha por mês) e relacione:
`dMes[AnoMes] 1—* dCalendario[AnoMes]` e `dMes[AnoMes] 1—* fMetas[AnoMes]`.
Relacione também `dVendedor[SK_Vendedor] 1—* fMetas[SK_Vendedor]`.

Diagrama:

```
        dCalendario ──*── fVendas ──*── dProduto
             │                │
             │(AnoMes)        │(SK_Vendedor)
             ▼                ▼
           dMes ──*── fMetas ──*── dVendedor
```

**Passo 2 — medidas.**

```dax
Meta = SUM( fMetas[MetaValor] )
```

```dax
Atingimento % = DIVIDE( [Faturamento Líquido], [Meta] )
```

```dax
-- Meta proporcional aos dias decorridos do mês (para comparação justa no mês corrente)
Meta Proporcional =
VAR DiasNoContexto  = COUNTROWS( dCalendario )
VAR DiasNoMes =
    CALCULATE(
        COUNTROWS( dCalendario ),
        REMOVEFILTERS( dCalendario ),
        VALUES( dCalendario[AnoMes] )
    )
RETURN
    [Meta] * DIVIDE( DiasNoContexto, DiasNoMes )
```

```dax
-- Aviso explícito quando o usuário pede meta numa granularidade que não existe
Meta (com aviso) =
IF(
    ISINSCOPE( dProduto[Produto] ),
    "não há meta por produto",
    FORMAT( [Meta], "#,##0.00" )
)
```

**Explicação.**
Duas tabelas de fatos em granularidades diferentes se conectam por **dimensões
compartilhadas** (aqui: mês e vendedor). Esse é o padrão canônico de Kimball para *fatos de
granularidade mista*, e o Power BI o implementa naturalmente porque o filtro flui das
dimensões para os fatos.

**Armadilha.** A tentação é relacionar `fVendas` diretamente a `fMetas`. Não faça.
Fato-com-fato produz relações muitos-para-muitos, ambiguidade de caminho e números
inflados. A regra: **fatos nunca se relacionam entre si; só com dimensões.**

A medida "com aviso" resolve o problema humano: sem ela, o usuário arrasta produto e vê
a meta do vendedor repetida em cada linha, achando que é meta por produto. Um número
errado sem aviso é pior que um erro.

---

## Exemplo 8 — Segmentação RFM simplificada

**Problema.** Classificar clientes por Recência, Frequência e Valor monetário.

**Solução.**

```dax
Recência (dias) =
VAR UltimaCompra = CALCULATE( MAX( fVendas[Date] ), fVendas[Tipo] = "Venda" )
VAR Referencia   = CALCULATE( MAX( dCalendario[Date] ), ALLSELECTED( dCalendario ) )
RETURN
    IF( NOT ISBLANK( UltimaCompra ), DATEDIFF( UltimaCompra, Referencia, DAY ) )
```

```dax
Frequência (nº de NFs) =
CALCULATE( DISTINCTCOUNT( fVendas[NF] ), fVendas[Tipo] = "Venda" )
```

```dax
Valor (ticket médio) =
DIVIDE( [Faturamento Líquido], [Frequência (nº de NFs)] )
```

```dax
Segmento RFM =
VAR R = [Recência (dias)]
VAR F = [Frequência (nº de NFs)]
VAR M = [Faturamento Líquido]
VAR MedianaM =
    MEDIANX( ALLSELECTED( dCliente[Cliente] ), [Faturamento Líquido] )
RETURN
    SWITCH(
        TRUE(),
        ISBLANK( R ),                       "Sem compra no período",
        R <= 30  && F >= 6 && M >= MedianaM, "Campeão",
        R <= 90  && F >= 3,                  "Fiel",
        R <= 90,                             "Recente",
        R <= 180,                            "Em risco",
        "Perdido"
    )
```

**Explicação.**
`MEDIANX` sobre `ALLSELECTED` estabelece um corte **relativo à base visível**, e não um
número mágico fixo. Isso mantém a segmentação válida quando a empresa cresce.

**Armadilha.** `Segmento RFM` é uma medida que devolve **texto**. Isso significa que você
**não pode usá-la como eixo** de um gráfico nem como filtro — medidas não filtram. Para
contar clientes por segmento, você precisa de uma tabela desconectada com os rótulos e
uma medida que conte:

```dax
Clientes no Segmento =
VAR Alvo = SELECTEDVALUE( dSegmentoRFM[Segmento] )
RETURN
    COUNTROWS(
        FILTER(
            ALLSELECTED( dCliente[Cliente] ),
            [Segmento RFM] = Alvo
        )
    )
```

Este é o padrão **"segmentação dinâmica"**, e é caro: avalia a medida uma vez por cliente.
Com 5 mil clientes, aceitável. Com 500 mil, calcule na origem.

---

## Exemplo 9 — Parâmetro *what-if*: simulador de desconto

**Problema.** "E se déssemos 5% a mais de desconto? Quanto perderíamos de margem?"

**Solução.**

**Passo 1** — **Modelagem → Novo parâmetro → Numérico**:
nome `Desconto Extra`, de `0` a `0,20`, incremento `0,01`, valor padrão `0`.
Isso gera automaticamente uma tabela calculada e uma medida:

```dax
Desconto Extra = GENERATESERIES( 0, 0.2, 0.01 )
```
```dax
Desconto Extra Valor = SELECTEDVALUE( 'Desconto Extra'[Desconto Extra], 0 )
```

**Passo 2** — Medidas de simulação:

```dax
Faturamento Simulado =
VAR Extra = [Desconto Extra Valor]
RETURN
    SUMX(
        fVendas,
        fVendas[Quantidade]
            * fVendas[PrecoUnitario]
            * ( 1 - fVendas[Desconto] - Extra )
    )
```

```dax
Margem Simulada = [Faturamento Simulado] - [Custo Total]
```

```dax
Impacto na Margem = [Margem Simulada] - [Margem Bruta]
```

```dax
Margem % Simulada = DIVIDE( [Margem Simulada], [Faturamento Simulado] )
```

```dax
-- Volume adicional necessário para manter a margem em reais
Volume Extra Necessário % =
VAR MargemAtual   = [Margem Bruta]
VAR MargemUnitSim =
    DIVIDE( [Margem Simulada], [Quantidade Vendida] )
RETURN
    IF(
        MargemUnitSim > 0,
        DIVIDE( MargemAtual, MargemUnitSim ) / [Quantidade Vendida] - 1
    )
```

**Explicação.**
O parâmetro *what-if* é uma **tabela desconectada**: ela não tem relação com nada, e seu
único papel é ser filtrada pelo usuário e lida por `SELECTEDVALUE`. Esse padrão —
tabela desconectada + `SELECTEDVALUE` — resolve toda simulação, seleção de métrica e
troca de cenário no Power BI.

**Armadilha.** A última medida (`Volume Extra Necessário %`) responde à pergunta que o
comercial **realmente** deveria fazer: "quanto a mais eu preciso vender para o desconto se
pagar?". A resposta costuma ser assustadora e é o melhor argumento contra descontos
lineares. **Opinião do autor:** um simulador que só mostra a perda é metade do trabalho;
mostre também o que seria necessário para compensá-la.

---

## Exemplo 10 — Duas datas na mesma tabela

**Problema.** `fVendas` tem `DataPedido` e `DataEntrega`. Você só pode ter **uma** relação
ativa com `dCalendario`.

**Solução.**

**Passo 1** — No modelo, crie as duas relações:
- `dCalendario[Date] → fVendas[DataPedido]` — **ativa** (linha sólida);
- `dCalendario[Date] → fVendas[DataEntrega]` — **inativa** (linha tracejada).

**Passo 2** — Medidas:

```dax
Faturamento por Pedido = [Faturamento Líquido]
```

```dax
Faturamento por Entrega =
CALCULATE(
    [Faturamento Líquido],
    USERELATIONSHIP( dCalendario[Date], fVendas[DataEntrega] )
)
```

```dax
Prazo Médio de Entrega (dias) =
AVERAGEX(
    fVendas,
    DATEDIFF( fVendas[DataPedido], fVendas[DataEntrega], DAY )
)
```

```dax
% Entregue no Prazo =
VAR NoPrazo =
    CALCULATE(
        COUNTROWS( fVendas ),
        FILTER(
            fVendas,
            DATEDIFF( fVendas[DataPedido], fVendas[DataEntrega], DAY ) <= 5
        )
    )
RETURN
    DIVIDE( NoPrazo, COUNTROWS( fVendas ) )
```

**Explicação.**
`USERELATIONSHIP` ativa uma relação inativa **apenas dentro daquele `CALCULATE`**. É a
solução limpa para o *role-playing dimension* (dimensão que faz vários papéis).

**Alternativa** — duplicar a `dCalendario` como `dCalendarioEntrega`. Vantagem: o usuário
pode colocar as duas datas em eixos diferentes no **mesmo** visual. Desvantagem: mais uma
tabela, mais confusão, dois conjuntos de segmentações. **Minha regra:** use
`USERELATIONSHIP` quando a segunda data é secundária; duplique a dimensão quando as duas
datas são analiticamente equivalentes e usadas lado a lado.

**Armadilha.** `USERELATIONSHIP` **não funciona** se a relação estiver com direção de
filtro cruzada "Ambos" em certas configurações, nem em modelos DirectQuery com
`ASSUMEREFERENTIALINTEGRITY` mal configurado. Se a medida não muda nada, verifique se a
relação inativa existe mesmo — é o erro mais comum.

---

## Exemplo 11 — Segurança por linha (RLS) dinâmica

**Problema.** Cada vendedor deve ver só as próprias vendas; cada gerente, as da equipe;
o diretor, tudo. Sem criar 40 relatórios.

**Solução.**

**Passo 1 — tabela de segurança.** Crie `dSeguranca` com:

| Email | SK_Vendedor | Escopo |
|---|---|---|
| ana@empresa.com | 12 | Vendedor |
| bruno@empresa.com | 13 | Vendedor |
| carla@empresa.com | 0 | Equipe Sul |
| diretor@empresa.com | 0 | Tudo |

**Passo 2** — **Modelagem → Gerenciar funções → Criar** função `Vendas Restritas`,
com esta expressão na tabela `dVendedor`:

```dax
VAR UsuarioAtual = USERPRINCIPALNAME()
VAR Escopo =
    LOOKUPVALUE( dSeguranca[Escopo], dSeguranca[Email], UsuarioAtual )
VAR VendedorDoUsuario =
    LOOKUPVALUE( dSeguranca[SK_Vendedor], dSeguranca[Email], UsuarioAtual )
RETURN
    SWITCH(
        Escopo,
        "Tudo",     TRUE(),
        "Vendedor", dVendedor[SK_Vendedor] = VendedorDoUsuario,
        "Equipe Sul", dVendedor[Equipe] = "Sul",
        FALSE()
    )
```

**Passo 3 — teste antes de publicar.**
**Modelagem → Exibir como** → marque a função e digite um e-mail em "Outro usuário".

**Passo 4 — no Service:** modelo semântico → **Segurança** → atribua os usuários/grupos
à função. **Sem esse passo, a RLS não faz nada.**

**Passo 5 — oculte a tabela de segurança:**

```dax
-- Não basta ocultar visualmente. Aplique também uma regra que a esvazie:
-- na mesma função, na tabela dSeguranca:
dSeguranca[Email] = USERPRINCIPALNAME()
```

**Explicação.**
`USERPRINCIPALNAME()` devolve o UPN de quem está consultando o modelo no Service. No
Desktop, devolve a conta local — por isso o teste com "Exibir como" existe.

O filtro é aplicado em `dVendedor` (a **dimensão**), e propaga para `fVendas` pela
relação. **Sempre filtre a dimensão, nunca o fato**: é mais rápido (menos linhas para
avaliar) e mais fácil de auditar.

**Armadilhas — e estas são graves:**

1. **RLS não protege o arquivo `.pbix`.** Quem tem acesso ao arquivo tem todos os dados.
   RLS é segurança **de consumo no Service**, não de posse.
2. **RLS não se aplica a quem tem função de Admin/Membro/Colaborador no workspace.** Só a
   Visualizadores. Colocar um usuário restrito como "Membro" anula a segurança inteira.
3. **`ALL()` numa medida pode furar a RLS?** Não — RLS é aplicada antes e não pode ser
   removida por `REMOVEFILTERS` numa medida. Mas **medidas mal escritas revelam totais por
   inferência** (por exemplo, "% do total geral" revela o total da empresa). Pense em
   *canais laterais*.
4. **Desempenho:** RLS complexa é reavaliada a cada consulta. `LOOKUPVALUE` numa tabela de
   50 mil linhas por consulta é caro. Ver [`24-seguranca-e-governanca.md`](24-seguranca-e-governanca.md).

---

## Exemplo 12 — Combinar 40 planilhas de uma pasta (M)

**Problema.** Todo mês chega um `.xlsx` novo numa pasta de rede, sempre com o mesmo
layout. Você quer que o relatório absorva os novos sozinho.

**Solução completa em M** (Editor Avançado):

```powerquery
let
    // 1. Parâmetro de caminho — troque por um parâmetro de verdade em produção
    CaminhoPasta = "\\servidor\bi\vendas\",

    // 2. Lista os arquivos da pasta
    Fonte = Folder.Files( CaminhoPasta ),

    // 3. Filtra: só .xlsx, ignorando temporários do Excel (~$) e ocultos
    Filtrados = Table.SelectRows(
        Fonte,
        each Text.EndsWith( Text.Lower( [Extension] ), ".xlsx" )
             and not Text.StartsWith( [Name], "~$" )
             and not Text.StartsWith( [Name], "." )
    ),

    // 4. Função que extrai a aba "Dados" de um arquivo binário
    LerArquivo = ( conteudo as binary ) as table =>
        let
            Livro = Excel.Workbook( conteudo, true ),
            Aba   = Table.SelectRows( Livro, each [Name] = "Dados" ),
            Dados = if Table.IsEmpty( Aba ) then #table( {}, {} ) else Aba{0}[Data]
        in
            Dados,

    // 5. Aplica a função a cada arquivo, guardando o nome do arquivo como coluna
    ComTabelas = Table.AddColumn(
        Filtrados,
        "Dados",
        each try LerArquivo( [Content] ) otherwise #table( {}, {} ),
        type table
    ),

    // 6. Mantém só o que interessa e expande
    Reduzido = Table.SelectColumns( ComTabelas, { "Name", "Dados" } ),
    Expandido = Table.ExpandTableColumn(
        Reduzido,
        "Dados",
        { "Data", "Produto", "Quantidade", "Valor" },
        { "Data", "Produto", "Quantidade", "Valor" }
    ),

    // 7. Tipagem explícita, com localidade declarada
    Tipado = Table.TransformColumnTypes(
        Expandido,
        {
            { "Name",       type text },
            { "Produto",    type text },
            { "Quantidade", Int64.Type },
            { "Valor",      type number }
        }
    ),
    ComData = Table.TransformColumnTypes(
        Tipado,
        { { "Data", type date } },
        "pt-BR"
    ),

    // 8. Remove linhas totalmente vazias (rodapé de planilha)
    SemVazias = Table.SelectRows(
        ComData,
        each not ( [Data] = null and [Produto] = null and [Valor] = null )
    ),

    // 9. Renomeia a coluna de origem — rastreabilidade
    Final = Table.RenameColumns( SemVazias, { { "Name", "ArquivoOrigem" } } )
in
    Final
```

**Explicação.**
Os pontos que separam este código de um tutorial:

- **`~$` e ocultos filtrados**: arquivos temporários do Excel derrubam a atualização
  inteira quando alguém deixa a planilha aberta. É o problema nº 1 desse padrão.
- **`try ... otherwise`**: um arquivo corrompido não derruba os outros 39.
- **`ArquivoOrigem` preservada**: quando um número estiver errado, você sabe de qual
  arquivo veio. **Sempre carregue a origem.**
- **Localidade explícita** na conversão de data.
- **Nada de "Combinar Arquivos" automático**: aquele botão gera 4 consultas auxiliares e
  uma função `Transformar Arquivo` que quebra quando o primeiro arquivo é atípico. Este
  código faz o mesmo, de forma legível e depurável.

**Armadilha.** Pasta de rede + Power BI Service = você precisa de **gateway**, e o serviço
do gateway precisa ter permissão de leitura no compartilhamento. Verifique isso **antes**
de prometer atualização automática. Uma alternativa muito melhor: mover os arquivos para
SharePoint/OneDrive e usar o conector nativo, sem gateway.

---

## Exemplo 13 — Consumir uma API REST paginada (M)

**Problema.** Um sistema expõe `https://api.exemplo.com/v1/pedidos?page=1&per_page=200`,
com o total de páginas no cabeçalho da resposta. Você precisa de todas as páginas.

**Solução.**

```powerquery
let
    // Parâmetros — em produção, use Gerenciar Parâmetros
    BaseUrl  = "https://api.exemplo.com/v1/pedidos",
    PorPagina = 200,
    Token = "SEU_TOKEN",     // em produção: credencial da fonte, NUNCA em texto aqui

    // 1. Função que busca uma página e devolve o registro JSON
    BuscarPagina = ( pagina as number ) as record =>
        let
            Resposta = Web.Contents(
                BaseUrl,
                [
                    Query   = [ page = Text.From( pagina ), per_page = Text.From( PorPagina ) ],
                    Headers = [ #"Authorization" = "Bearer " & Token,
                                #"Accept"        = "application/json" ]
                ]
            ),
            Json = Json.Document( Resposta )
        in
            Json,

    // 2. Primeira página, para descobrir o total
    Primeira = BuscarPagina( 1 ),
    TotalRegistros = Primeira[total]?  ?? 0,
    TotalPaginas = Number.RoundUp( TotalRegistros / PorPagina ),

    // 3. Lista de páginas a buscar
    Paginas = if TotalPaginas <= 1 then { 1 } else { 1 .. TotalPaginas },

    // 4. Busca todas e concatena os itens
    TodasAsListas = List.Transform( Paginas, each BuscarPagina( _ )[data] ),
    ItensCombinados = List.Combine( TodasAsListas ),

    // 5. Converte a lista de registros em tabela
    Tabela = Table.FromList( ItensCombinados, Splitter.SplitByNothing(), null, null, ExtraValues.Error ),
    Expandida = Table.ExpandRecordColumn(
        Tabela,
        "Column1",
        { "id", "created_at", "customer_id", "total_amount", "status" },
        { "IDPedido", "DataCriacao", "IDCliente", "Valor", "Status" }
    ),

    // 6. Tipos — data ISO 8601 vem como texto
    Tipada = Table.TransformColumnTypes(
        Expandida,
        {
            { "IDPedido",   Int64.Type },
            { "IDCliente",  Int64.Type },
            { "Valor",      type number },
            { "Status",     type text }
        }
    ),
    ComData = Table.AddColumn(
        Tipada,
        "Data",
        each Date.From( DateTimeZone.From( [DataCriacao] ) ),
        type date
    ),
    Final = Table.RemoveColumns( ComData, { "DataCriacao" } )
in
    Final
```

**Explicação e avisos sérios.**

- **`Web.Contents` com `Query` e `Headers` separados**, e não a URL concatenada. Isso é
  obrigatório para o Power BI reconhecer a fonte de dados e permitir a atualização
  agendada no Service. URL montada com `&` em texto gera o erro
  `This dataset includes a dynamic data source...` na publicação.
- **Nunca deixe o token no código.** Aqui está para o exemplo ficar completo. Em produção:
  use o tipo de autenticação da fonte (Anônimo com chave em cabeçalho requer a opção
  `ApiKeyName`, ou credencial Web API), ou o Azure Key Vault via gateway.
- **`?? 0` e `[total]?`**: o `?` devolve `null` em vez de erro quando o campo não existe;
  `??` é o operador de coalescência. Sem isso, uma resposta atípica quebra a carga.
- **Paginação sequencial é lenta.** 300 páginas × 400 ms = 2 minutos por atualização.
  Se a API oferecer um endpoint de exportação em massa ou filtro por data, use-o.

**Armadilha.** APIs com **paginação por cursor** (`next_url`) não cabem neste padrão —
elas exigem `List.Generate`, que é o recurso de laço do M:

```powerquery
Paginas = List.Generate(
    () => [ pagina = BuscarPagina( 1 ), continua = true ],
    each [continua],
    each [ pagina = Json.Document( Web.Contents( [pagina][next_url] ) ),
           continua = [pagina][next_url] <> null ],
    each [pagina][data]
)
```

---

## Exemplo 14 — Caso real: carga incremental de 400 milhões de linhas

**Contexto real.** Historiador de processo de uma planta química: 8 instrumentos, leitura
por minuto, 8 anos de histórico. Cerca de 400 milhões de linhas no SQL Server. Uma carga
completa levava 6 horas e falhava por timeout duas vezes por semana.

**Diagnóstico.** Carga completa diária de dados **imutáveis**. 99,97% do trabalho era
recarregar o que não mudou.

**Solução — atualização incremental.**

**Passo 1 — parâmetros obrigatórios** (nomes exatos, `RangeStart` e `RangeEnd`,
tipo Data/Hora):

```powerquery
// Gerenciar Parâmetros → Novo
// RangeStart : Data/Hora : 01/01/2026 00:00:00
// RangeEnd   : Data/Hora : 01/02/2026 00:00:00
```

**Passo 2 — filtro na consulta, **antes** de qualquer outra transformação:**

```powerquery
let
    Fonte = Sql.Database( "srv-historiador", "PIArchive",
                          [ CommandTimeout = #duration( 0, 2, 0, 0 ) ] ),
    Tabela = Fonte{[Schema="dbo", Item="Leituras"]}[Data],

    // O filtro TEM de usar >= e <  (nunca >= e <=, senão duplica na fronteira)
    Incremental = Table.SelectRows(
        Tabela,
        each [Timestamp] >= RangeStart and [Timestamp] < RangeEnd
    ),

    Reduzida = Table.SelectColumns(
        Incremental,
        { "Timestamp", "TagId", "Valor", "Qualidade" }
    ),
    Tipada = Table.TransformColumnTypes(
        Reduzida,
        { { "Timestamp", type datetime }, { "TagId", Int64.Type },
          { "Valor", type number }, { "Qualidade", Int64.Type } }
    )
in
    Tipada
```

**Passo 3 — verificar o folding.** Botão direito na última etapa → **Exibir Consulta
Nativa**. Deve mostrar algo como:

```sql
select [Timestamp], [TagId], [Valor], [Qualidade]
from [dbo].[Leituras]
where [Timestamp] >= @P1 and [Timestamp] < @P2
```

**Se "Exibir Consulta Nativa" estiver cinza, pare.** Sem folding, a atualização incremental
baixa a tabela inteira para filtrar localmente — o oposto do objetivo.

**Passo 4 — política.** Botão direito na tabela → **Atualização incremental**:

- Arquivar dados a partir de: **8 anos**
- Atualizar incrementalmente os dados nos últimos: **10 dias**
- ☑ Obter apenas as linhas de dados alteradas (exige coluna de detecção de alteração)
- ☑ Somente atualização completa após a publicação

**Passo 5 — publique e faça a primeira atualização no Service.** A primeira leva horas
(cria as partições); as seguintes, minutos.

**Resultado medido no caso real:**

| Métrica | Antes | Depois |
|---|---|---|
| Tempo de atualização | ~6 h | ~4 min |
| Falhas por timeout | 2/semana | 0 em 6 meses |
| Tamanho do modelo | 11,2 GB | 9,8 GB (particionado) |
| Janela de manutenção | madrugada inteira | irrelevante |

**Lições que valem mais que o procedimento:**

1. **O filtro tem de dobrar.** Tudo depende disso.
2. **`>=` e `<`, nunca `<=`.** A fronteira duplica linhas, e ninguém percebe por meses.
3. **A primeira atualização no Service é longa e pode estourar o limite de tempo do
   Pro (2 h).** Em capacidade, use o endpoint XMLA para atualizar partição por partição.
4. **Não dá para "desfazer" facilmente.** Mudar a política costuma exigir atualização
   completa. Planeje as faixas com folga.
5. **O maior ganho não foi o tempo** — foi parar de acordar às 3h para reprocessar.

---

## Exemplo 15 — Caso real: OEE de uma linha de produção

**Contexto real.** Planta de resinas em batelada. A diretoria queria OEE
(*Overall Equipment Effectiveness*, eficiência global do equipamento) por linha, por turno
e por motivo de parada, atualizado de hora em hora.

**O modelo:**

```
dCalendario ──*── fProducao ──*── dProduto
dTurno ───────*──┤            └──*── dLinha
dCalendario ──*── fParadas ──*── dMotivoParada
                     └──────*── dLinha
```

**As medidas — OEE é o produto de três fatores:**

```dax
-- ---------- DISPONIBILIDADE ----------
Tempo Programado (min) =
SUMX(
    fProducao,
    fProducao[MinutosProgramados]
)
```

```dax
Tempo Parado (min) = SUM( fParadas[DuracaoMin] )
```

```dax
Tempo Parado Planejado (min) =
CALCULATE( [Tempo Parado (min)], dMotivoParada[Planejada] = TRUE() )
```

```dax
Tempo Operando (min) =
[Tempo Programado (min)] - [Tempo Parado (min)]
```

```dax
Disponibilidade % =
DIVIDE(
    [Tempo Operando (min)],
    [Tempo Programado (min)] - [Tempo Parado Planejado (min)]
)
```

```dax
-- ---------- DESEMPENHO ----------
Produção Real (kg) = SUM( fProducao[QuantidadeKg] )
```

```dax
Capacidade Teórica (kg) =
SUMX(
    fProducao,
    RELATED( dProduto[TaxaNominalKgMin] ) * fProducao[MinutosOperando]
)
```

```dax
Desempenho % =
MIN( 1, DIVIDE( [Produção Real (kg)], [Capacidade Teórica (kg)] ) )
```

```dax
-- ---------- QUALIDADE ----------
Produção Aprovada (kg) =
CALCULATE( [Produção Real (kg)], fProducao[StatusQualidade] = "Aprovado" )
```

```dax
Qualidade % = DIVIDE( [Produção Aprovada (kg)], [Produção Real (kg)] )
```

```dax
-- ---------- OEE ----------
OEE % = [Disponibilidade %] * [Desempenho %] * [Qualidade %]
```

```dax
-- Classificação, com a referência de classe mundial (85%)
OEE Classificação =
VAR v = [OEE %]
RETURN
    SWITCH(
        TRUE(),
        ISBLANK( v ), BLANK(),
        v >= 0.85, "Classe mundial",
        v >= 0.60, "Aceitável",
        v >= 0.40, "Baixo",
        "Crítico"
    )
```

```dax
-- Pareto de perdas: quanto cada motivo de parada custou em kg não produzidos
Perda por Parada (kg) =
SUMX(
    fParadas,
    fParadas[DuracaoMin] * RELATED( dLinha[TaxaNominalKgMin] )
)
```

**Decisões de projeto que fizeram diferença — e por quê:**

1. **`MIN(1, ...)` no Desempenho.** Sensor de vazão com erro de calibração produzia
   desempenho de 118%, e o OEE passava de 100%. Fisicamente impossível. Limitar em 1 é uma
   **decisão consciente de negócio**, documentada na descrição da medida — não é
   maquiagem, é reconhecer que a taxa nominal do cadastro está desatualizada. A alternativa
   honesta (e que também implementamos) foi uma medida `Alertas de Taxa Nominal` que
   **lista os produtos** onde isso acontece, para o PCP corrigir o cadastro.

2. **Paradas planejadas fora do denominador da Disponibilidade.** Existe divergência
   metodológica real aqui: a definição original de Nakajima exclui paradas planejadas;
   muitas implementações de TEEP as incluem. Escolhemos excluir e **escrevemos isso no
   relatório**, numa caixa de texto. Sem essa nota, cada reunião recomeçava a discussão.

3. **Duas tabelas de fato (`fProducao`, `fParadas`) em granularidades diferentes**, ligadas
   por dimensões compartilhadas — exatamente o padrão do Exemplo 7.

4. **Atualização de hora em hora**, não em tempo real. Tempo real teria exigido DirectQuery
   contra o historiador, degradando o sistema de controle. **Ninguém toma decisão de
   OEE em segundos.** Ver [`20-modos-de-armazenamento.md`](20-modos-de-armazenamento.md).

**O que deu errado, e a lição.** Na primeira versão, a Disponibilidade dava >100% em
alguns turnos: paradas registradas com duração maior que o tempo programado, porque o
operador lançava a parada no turno errado. **Nenhum ajuste de DAX conserta dado
inconsistente.** A solução foi uma página de **auditoria de dados** no próprio relatório,
listando as inconsistências com nome do turno e do apontador. A qualidade do apontamento
melhorou em três semanas — não pelo relatório de OEE, mas pelo relatório de erros.

> **Lição geral, e provavelmente a mais valiosa deste arquivo:** todo projeto de BI sério
> precisa de uma página de auditoria que mostre o que está **errado nos dados**. Ela é a
> primeira que você constrói e a última que alguém elogia.

---

## Autoteste

1. Por que `SUMX(t, a*b)` e não `SUM(a) * SUM(b)`?
2. Quais são as três respostas possíveis para "% do total", e como se escolhe?
3. Por que `Δ % vs AA` precisa de um `IF` com `ISBLANK`?
4. Qual o padrão para conectar duas tabelas de fatos em granularidades diferentes?
5. Por que uma medida que devolve texto não pode ser usada como eixo?
6. O que é uma "tabela desconectada" e em quais dois exemplos deste arquivo ela apareceu?
7. Na atualização incremental, por que `>=` e `<` em vez de `>=` e `<=`?
8. Como você verifica se o filtro incremental está dobrando (*folding*)?
9. Cite duas coisas que a RLS **não** protege.
10. No exemplo do OEE, por que `MIN(1, ...)` é uma decisão de negócio e não um truque?
11. Por que o Exemplo 12 filtra arquivos que começam com `~$`?
12. Por que `Web.Contents` deve receber `Query` e `Headers` como parâmetros em vez de uma
    URL concatenada?

---

**Próximo:** [`07-projeto-modelo/`](07-projeto-modelo/README.md) — um projeto inteiro,
executável, com defeitos plantados de propósito.
