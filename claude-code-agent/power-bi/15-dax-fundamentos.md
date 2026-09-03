# 15 · DAX — fundamentos

**Nível:** intermediário
**Data:** 14/08/2026

DAX (*Data Analysis Expressions*) é a linguagem de cálculo do Power BI, do Analysis
Services Tabular e do Power Pivot no Excel. Este arquivo cobre sintaxe, tipos, as funções
que resolvem 90% dos casos e as decisões de projeto. O conceito que torna DAX difícil —
**contexto de avaliação** — tem arquivo próprio: [`16`](16-dax-contexto-de-avaliacao.md).

---

## 1. A armadilha das boas-vindas

```dax
Total = SUM( Vendas[Valor] )
```

Parece Excel. **Não é Excel.**

| | Excel | DAX |
|---|---|---|
| Unidade | célula (`A1`) | coluna inteira |
| Referência | posicional | por nome de tabela e coluna |
| Escopo | a planilha | o **contexto de avaliação** |
| Resultado | um valor por célula | um valor por contexto |
| Linha atual | implícita pela posição | existe só dentro de iteradores |

A sintaxe foi feita parecida **de propósito**, para atrair usuários de Excel
([`11-historia.md`](11-historia.md) §4). O custo é que a semântica surpreende: você escreve
algo que parece certo, o resultado é plausível, e está errado.

**Consequência prática:** desconfie de qualquer medida cujo resultado você não consegue
explicar em português. "Deu esse número porque..." — se você não completa a frase, não
publique.

---

## 2. Sintaxe essencial

### 2.1 Referências

```dax
Vendas[Valor]              -- coluna: Tabela[Coluna]
[Faturamento Total]        -- medida: sempre entre colchetes, sem nome de tabela
'Nome Com Espaço'[Coluna]  -- tabela com espaço: aspas simples
```

**Convenção do campo, e vale seguir:**

> Sempre qualifique **colunas** (`Vendas[Valor]`) e **nunca** qualifique **medidas**
> (`[Faturamento]`).

Não é preciosismo: torna o código legível de imediato — o que tem prefixo é coluna, o que
não tem é medida. Ferramentas como o *Best Practice Analyzer* do Tabular Editor conferem
isso automaticamente.

### 2.2 Operadores

| Categoria | Operadores |
|---|---|
| Aritméticos | `+ - * / ^` |
| Comparação | `= <> > >= < <=` |
| Texto | `&` (concatenação) |
| Lógicos | `&&` (E), `\|\|` (OU), `IN`, `NOT` |
| Tabela | `IN { }` |

```dax
Filtro = dProduto[Categoria] IN { "Tintas", "Vernizes", "Resinas" }
```

`IN` com chaves é mais legível que três `||` encadeados, e o motor trata igual.

### 2.3 Comentários

```dax
-- comentário de linha
// comentário de linha (as duas formas funcionam)
/* comentário
   de bloco */

/// Comentário de descrição: acima de um MEASURE na Exibição de Consulta DAX,
/// vira a DESCRIÇÃO da medida no modelo (recurso de julho/2026).
```

Use `///` religiosamente. A descrição aparece em tooltip no painel Dados, no Model
Explorer e para quem consumir o modelo pelo Excel. **É a única documentação que alguém
vai ler de fato**, porque está no lugar onde a dúvida acontece.

### 2.4 Tipos de dados

| Tipo DAX | Observação |
|---|---|
| Número Inteiro (Int64) | 64 bits com sinal |
| Número Decimal | Ponto flutuante 64 bits (IEEE 754) — **sujeito a erro de arredondamento** |
| Número Decimal Fixo (Currency) | 4 casas decimais **exatas**, inteiro por dentro |
| Data/Hora | Ponto flutuante desde 30/12/1899 |
| Booleano | `TRUE()` / `FALSE()` |
| Texto | Unicode |
| Binário | Não usável em medida |
| **BLANK** | Não é `NULL` nem `0`. Tem regras próprias |

**Alerta sobre dinheiro:** use **Decimal Fixo** para valores monetários sempre que a
soma precisar fechar ao centavo. Ponto flutuante acumula erro:
`0.1 + 0.2 <> 0.3` em qualquer linguagem IEEE 754, inclusive DAX.

### 2.5 `BLANK` — as regras que surpreendem

```dax
BLANK() + 5        = 5
BLANK() * 5        = BLANK()
BLANK() = 0        → TRUE     ← isto pega todo mundo
BLANK() = ""       → TRUE
ISBLANK( 0 )       → FALSE
5 / BLANK()        = Infinity (erro)
DIVIDE( 5, BLANK() ) = BLANK()
```

**Consequências:**

- Uma medida que devolve `BLANK` **some** do visual (a linha desaparece). Isso é bom
  (matriz limpa) e ruim (você não vê que faltou dado).
- `IF( [Medida] = 0, ... )` também captura `BLANK`. Se quiser distinguir, use `ISBLANK`.
- Para forçar a exibição de zero: `[Medida] + 0`.

---

## 3. As três coisas que você pode criar

| | Medida | Coluna calculada | Tabela calculada |
|---|---|---|---|
| Onde | Qualquer tabela (use `_Medidas`) | Numa tabela específica | No modelo |
| Quando avalia | Cada consulta | No refresh | No refresh |
| Contexto | Filtro | Linha | Nenhum |
| Ocupa memória | Não | Sim | Sim |
| Pode ir no eixo | Não | Sim | — |
| Devolve | Escalar (ou tabela, em contextos específicos) | Um valor por linha | Uma tabela |

**A regra de decisão**, repetida de [`10-fundamentos.md`](10-fundamentos.md) porque é
central:

> Se o resultado depende do que está filtrado, é **medida**.
> Se é um atributo fixo da linha, é **coluna**.
> Se você precisa de uma tabela que a fonte não fornece, é **tabela calculada** —
> e pergunte-se antes se não caberia no Power Query.

---

## 4. Iteradores — as funções com `X`

```dax
SUM( Vendas[Valor] )                          -- agrega uma coluna
SUMX( Vendas, Vendas[Qtd] * Vendas[Preco] )   -- itera e agrega uma expressão
```

`SUMX` percorre a tabela linha a linha, avalia a expressão em cada linha (criando um
**contexto de linha**) e soma os resultados.

**Por que não `SUM(Qtd) * SUM(Preco)`?** Porque soma-de-produtos ≠ produto-de-somas:

```
Qtd  Preço   Qtd×Preço
 10   100      1.000
  2   500      1.000
────────────────────────
 12   600      2.000   ← SUMX = 2.000
                7.200   ← SUM(Qtd)*SUM(Preço) = 12 × 600 (errado)
```

**Os iteradores principais:** `SUMX`, `AVERAGEX`, `MINX`, `MAXX`, `COUNTX`, `PRODUCTX`,
`CONCATENATEX`, `RANKX`, `MEDIANX`, `PERCENTILEX.INC`, `FILTER`, `ADDCOLUMNS`.

**Custo:** iterar 60 mil linhas é barato; iterar 400 milhões, não. O motor otimiza muitos
padrões de `SUMX` para executar no motor de armazenamento — mas expressões complexas caem
no motor de fórmula, que é sequencial. Ver [`22-desempenho.md`](22-desempenho.md).

---

## 5. `VAR` — não é opcional

```dax
-- ruim: repete o cálculo, ilegível
Δ % vs AA =
DIVIDE(
    [Faturamento Líquido] - CALCULATE( [Faturamento Líquido], SAMEPERIODLASTYEAR( dCalendario[Data] ) ),
    CALCULATE( [Faturamento Líquido], SAMEPERIODLASTYEAR( dCalendario[Data] ) )
)

-- bom
Δ % vs AA =
VAR Atual    = [Faturamento Líquido]
VAR Anterior = CALCULATE( [Faturamento Líquido], SAMEPERIODLASTYEAR( dCalendario[Data] ) )
RETURN
    DIVIDE( Atual - Anterior, Anterior )
```

**Três razões, e a terceira é a que importa:**

1. **Legibilidade.** Nomear os pedaços é documentação.
2. **Desempenho.** A variável é avaliada uma vez.
3. **Semântica.** Uma `VAR` é avaliada **no contexto onde foi declarada**, e o valor fica
   congelado. Isso muda o resultado, não só a velocidade.

Exemplo em que (3) decide tudo:

```dax
-- Errado: [Faturamento] dentro do FILTER é reavaliado no contexto de linha
Produtos acima da média =
COUNTROWS(
    FILTER(
        VALUES( dProduto[Produto] ),
        [Faturamento Líquido] > AVERAGEX( VALUES( dProduto[Produto] ), [Faturamento Líquido] )
    )
)

-- Certo: a média é calculada UMA vez, antes do filtro
Produtos acima da média =
VAR Media = AVERAGEX( VALUES( dProduto[Produto] ), [Faturamento Líquido] )
RETURN
    COUNTROWS(
        FILTER( VALUES( dProduto[Produto] ), [Faturamento Líquido] > Media )
    )
```

Na primeira versão, a média é recalculada dentro do contexto de cada produto — o que muda
o valor. É um bug sutil, plausível e difícil de detectar.

**Regra prática:** se uma expressão aparece duas vezes na sua medida, ela deveria ser
uma `VAR`. Se sua medida tem mais de 5 linhas sem `VAR`, ela está pedindo uma.

---

## 6. As 40 funções que resolvem 90%

### Agregação
`SUM` · `AVERAGE` · `MIN` · `MAX` · `COUNTROWS` · `DISTINCTCOUNT` · `DIVIDE`
`SUMX` · `AVERAGEX` · `MAXX` · `MINX` · `COUNTX`

### Filtro e contexto
`CALCULATE` ★★★ · `FILTER` · `ALL` · `ALLSELECTED` · `ALLEXCEPT` · `REMOVEFILTERS`
`KEEPFILTERS` · `VALUES` · `DISTINCT` · `SELECTEDVALUE` · `HASONEVALUE` · `ISINSCOPE`
`TREATAS` · `CROSSFILTER` · `USERELATIONSHIP`

### Tempo
`DATESYTD` · `SAMEPERIODLASTYEAR` · `DATEADD` · `DATESINPERIOD` · `DATESBETWEEN`
`EOMONTH` · `TODAY` · `DATEDIFF` · `CALENDAR`

### Relação
`RELATED` · `RELATEDTABLE` · `LOOKUPVALUE`

### Lógica e texto
`IF` · `SWITCH` · `COALESCE` · `ISBLANK` · `FORMAT` · `CONCATENATEX`

### Tabela
`ADDCOLUMNS` · `SUMMARIZECOLUMNS` · `TOPN` · `RANKX` · `EXCEPT` · `UNION` · `GENERATESERIES`

**Se você dominar `CALCULATE`, `FILTER`, `ALL`/`ALLSELECTED`, `VALUES` e `VAR`, você
escreve 90% do DAX profissional.** O resto é vocabulário.

---

## 7. `CALCULATE` — apresentação

`CALCULATE` merece um capítulo inteiro ([`16`](16-dax-contexto-de-avaliacao.md) §5), mas
você precisa da forma básica agora.

```dax
CALCULATE( <expressão>, <filtro1>, <filtro2>, ... )
```

*"Calcule a expressão, mas com o contexto de filtro modificado por estes filtros."*

```dax
Faturamento de Tintas =
CALCULATE( [Faturamento Líquido], dProduto[Categoria] = "Tintas" )
```

**Duas regras que você precisa memorizar hoje:**

**Regra 1 — `CALCULATE` SUBSTITUI o filtro na mesma coluna.**

Se o usuário filtrou "Vernizes" na segmentação e a medida diz
`CALCULATE([Fat], dProduto[Categoria] = "Tintas")`, o resultado é o de **Tintas**. O filtro
do usuário na coluna `Categoria` foi substituído, não somado.

Para **intersectar** em vez de substituir, use `KEEPFILTERS`:

```dax
CALCULATE( [Faturamento Líquido], KEEPFILTERS( dProduto[Categoria] = "Tintas" ) )
-- Com "Vernizes" selecionado, devolve BLANK — a interseção é vazia. Correto.
```

**Regra 2 — o argumento de filtro é açúcar sintático para uma tabela.**

```dax
CALCULATE( [Fat], dProduto[Categoria] = "Tintas" )
-- é internamente equivalente a:
CALCULATE( [Fat], FILTER( ALL( dProduto[Categoria] ), dProduto[Categoria] = "Tintas" ) )
```

Repare no `ALL`. **É daí que vem a substituição.** Entender essa equivalência é entender
`CALCULATE`.

---

## 8. Padrões básicos que você vai usar sempre

### Percentual sobre o total
```dax
% do Total = DIVIDE( [Faturamento], CALCULATE( [Faturamento], ALLSELECTED() ) )
```

### Valor de outra categoria
```dax
Faturamento de Tintas =
CALCULATE( [Faturamento], REMOVEFILTERS( dProduto ), dProduto[Categoria] = "Tintas" )
```

### Contar com condição
```dax
Clientes com compra acima de 100 mil =
COUNTROWS(
    FILTER( VALUES( dCliente[CNPJ] ), [Faturamento] > 100000 )
)
```

### Buscar valor de outra tabela sem relação
```dax
Meta do Vendedor =
LOOKUPVALUE(
    fMetas[MetaValor],
    fMetas[SK_Vendedor], SELECTEDVALUE( dVendedor[SK_Vendedor] ),
    fMetas[AnoMes],      SELECTEDVALUE( dMes[AnoMes] )
)
```

### Título dinâmico
```dax
Título =
"Vendas de " & SELECTEDVALUE( dCliente[UF], "todos os estados" ) &
" — " & SELECTEDVALUE( dCalendario[Ano], "todos os anos" )
```
Ligue ao título do visual com o botão `fx` (formatação condicional).

### Semáforo
```dax
Cor do KPI =
SWITCH(
    TRUE(),
    ISBLANK( [Atingimento %] ), "#CCCCCC",
    [Atingimento %] >= 1,       "#1B7F3B",
    [Atingimento %] >= 0.9,     "#B8860B",
    "#B00020"
)
```
Aplique em Formato → Cor → `fx` → Formatação por campo.

### Ranking
```dax
Posição = RANKX( ALLSELECTED( dProduto[Produto] ), [Faturamento], , DESC, DENSE )
```

---

## 9. Erros que quase todo mundo comete

### 9.1 `/` em vez de `DIVIDE`

```dax
Margem % = [Margem] / [Faturamento]     -- ✘ erro se Faturamento = 0
Margem % = DIVIDE( [Margem], [Faturamento] )   -- ✔ devolve BLANK
```

### 9.2 Somar percentuais

`Margem %` como **coluna calculada** faz o total somar percentuais. Use medida sempre.

### 9.3 `FILTER` sobre a tabela de fatos

```dax
-- ✘ itera 60 milhões de linhas
CALCULATE( [Fat], FILTER( fVendas, fVendas[Valor] > 1000 ) )

-- ✔ filtra a coluna (o motor otimiza)
CALCULATE( [Fat], fVendas[Valor] > 1000 )

-- ✔✔ melhor ainda: filtre a dimensão
CALCULATE( [Fat], dProduto[Categoria] = "Tintas" )
```

`FILTER(tabela, ...)` materializa a tabela inteira. Reserve-o para quando o filtro
depender de uma **medida** (`FILTER(VALUES(dProduto[Produto]), [Fat] > 1000)`).

### 9.4 `FORMAT` num eixo

`FORMAT` devolve **texto**. Um eixo de texto ordena alfabeticamente e não faz aritmética.
Formate na propriedade de formato da medida.

### 9.5 Medida que devolve texto e depois é usada como filtro

Medidas não filtram. Se você quer segmentar por "Classe ABC", precisa de uma tabela
desconectada com os rótulos ([`06-exemplos.md`](06-exemplos.md) §8).

### 9.6 Confundir `COUNT` com `COUNTROWS`

`COUNT(coluna)` ignora `BLANK`. `COUNTROWS(tabela)` conta todas as linhas. Para "quantas
vendas", use `COUNTROWS(fVendas)`.

### 9.7 `EARLIER`

```dax
-- ✘ código de 2015
Acumulado = SUMX( FILTER( T, T[Data] <= EARLIER( T[Data] ) ), T[Valor] )

-- ✔ com VAR
Acumulado =
VAR DataAtual = T[Data]
RETURN SUMX( FILTER( T, T[Data] <= DataAtual ), T[Valor] )
```

`EARLIER` ainda funciona (compatibilidade retroativa). Não escreva mais. Se você precisa
lê-lo, veja [`16`](16-dax-contexto-de-avaliacao.md) §8.

---

## 10. Estilo — como escrever DAX que outra pessoa entende

Convenção estabelecida por Marco Russo e Alberto Ferrari (SQLBI), adotada pelo campo e
implementada no DAX Formatter:

```dax
Faturamento Líquido Últimos 12 Meses =
VAR UltimaData =
    MAX ( dCalendario[Data] )
VAR Janela =
    DATESINPERIOD (
        dCalendario[Data],
        UltimaData,
        -12,
        MONTH
    )
VAR Resultado =
    CALCULATE (
        [Faturamento Líquido],
        Janela
    )
RETURN
    Resultado
```

Regras:

1. **Uma vírgula por linha** quando a função tem vários argumentos.
2. **`VAR` para cada conceito**, com nome em português significativo.
3. **`RETURN` sozinho na linha.**
4. **Indentação por nível de aninhamento.**
5. **`Ctrl+Shift+M`** formata automaticamente. Use antes de todo commit.
6. **Prefixo nas variáveis de tabela** para distinguir de escalares (`VAR _tProdutos = ...`).

**Opinião do autor:** DAX de uma linha só é a maior fonte de dívida técnica em Power BI.
Uma medida de 15 linhas bem formatada é lida em 30 segundos; a mesma medida em uma linha
custa 10 minutos e um erro.

---

## 11. Onde escrever DAX

| Lugar | Quando |
|---|---|
| Barra de fórmulas do Desktop | Medidas simples, correções rápidas |
| **Exibição de Consulta DAX** | Testar sem tocar no modelo; `DEFINE MEASURE`; criar em lote ★ |
| **Tabular Editor** | Criar 40 medidas de uma vez; scripts; Best Practice Analyzer ★ |
| **DAX Studio** | Medir tempo, ver plano de consulta, depurar ★ |
| Visão TMDL (Desktop ou web) | Editar o modelo como texto, incluindo medidas |
| VS Code + extensão | Trabalhar no PBIP versionado |

O fluxo profissional: escreva na Exibição de Consulta DAX, teste, meça no DAX Studio,
grave no modelo, versione no PBIP.

---

## 12. Funções definidas pelo usuário (UDF)

Recurso recente da linguagem: definir funções próprias, reutilizáveis.

```dax
DEFINE
    FUNCTION VariacaoPercentual = (Atual: NUMERIC, Anterior: NUMERIC) =>
        IF(
            NOT ISBLANK( Anterior ) && Anterior <> 0,
            DIVIDE( Atual - Anterior, Anterior )
        )

EVALUATE
    { VariacaoPercentual( 120, 100 ) }
```

**Por que importa:** elimina a repetição de padrões (variação %, YTD, tratamento de
blank) que hoje se copia entre 30 medidas. É a evolução mais significativa da linguagem
em anos.

**Estado em 14/08/2026:** disponível, com suporte crescente nas ferramentas. Verifique a
disponibilidade na sua versão e no seu ambiente de destino antes de depender disso em
produção. Ver [`65-estado-da-arte.md`](65-estado-da-arte.md).

---

## 13. Os cinco porquês: por que uma medida não pode ser usada como eixo?

1. **Por que não posso arrastar uma medida para o eixo do gráfico?**
   Porque um eixo precisa de um **conjunto de valores conhecido antes do cálculo**, e uma
   medida só produz valor **depois** que o contexto está definido.

2. **Por que o contexto precisa vir antes?**
   Porque o motor monta a consulta assim: primeiro determina as combinações de eixos
   (um produto de valores das colunas), depois avalia as medidas em cada combinação. Se a
   medida definisse o eixo, haveria dependência circular.

3. **Por que não iterar todas as combinações possíveis e agrupar pelo resultado?**
   Porque o espaço de resultados de uma medida é **contínuo e desconhecido**. Não há um
   conjunto finito de "valores de faturamento" para formar um eixo. E, mesmo restringindo,
   o custo seria proibitivo.

4. **Por que o Power BI não faz isso automaticamente para casos pequenos?**
   Porque a semântica ficaria inconsistente: funcionaria em 500 linhas e falharia em 5
   milhões. Uma linguagem que muda de comportamento conforme o volume é pior que uma que
   recusa sempre.

5. **Parada legítima — limite do modelo de avaliação.**
   Isso decorre diretamente do desenho: o contexto de filtro é **entrada** da medida, não
   saída. Inverter exigiria um modelo de avaliação diferente — recursivo, com ponto fixo —
   que é o que linguagens de planilha fazem (e é a razão de planilhas terem referência
   circular e iteração). É um trade-off de projeto assumido, não uma limitação de
   implementação.

**A saída prática** para quando você precisa disso: uma tabela desconectada com os rótulos
desejados e uma medida que decide a que rótulo cada linha pertence — o padrão de
**segmentação dinâmica** ([`06-exemplos.md`](06-exemplos.md) §8).

---

## 14. Autoteste

1. Cite três diferenças entre uma fórmula de Excel e uma medida DAX.
2. Por que qualificar colunas e não qualificar medidas?
3. `BLANK() = 0` é verdadeiro ou falso? Que problema isso causa?
4. Por que `SUM(Qtd) * SUM(Preço)` está errado, e o que usar?
5. Dê a razão **semântica** (não a de desempenho) para usar `VAR`.
6. Explique a regra 1 de `CALCULATE` e como contorná-la.
7. Traduza `CALCULATE([Fat], dProduto[Categoria]="Tintas")` na sua forma com `FILTER`.
   O que o `ALL` implícito faz?
8. Por que `FILTER(fVendas, ...)` é ruim e quando é inevitável?
9. Quando usar `COUNT` e quando usar `COUNTROWS`?
10. Por que não se deve mais usar `EARLIER`?
11. Explique por que uma medida não pode ir no eixo, em termos do modelo de avaliação.

---

**Próximo:** [`16-dax-contexto-de-avaliacao.md`](16-dax-contexto-de-avaliacao.md) — **o**
capítulo. É onde a maioria empaca, e é onde você deixa de copiar DAX e passa a escrever.
