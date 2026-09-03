# 16 · Contexto de avaliação — o capítulo

**Nível:** avançado
**Data:** 14/08/2026
**Tempo estimado:** leia devagar. Duas ou três sessões. Não adianta correr.

> Este é o ponto de virada do curso. Antes dele, você copia DAX da internet e reza.
> Depois dele, você escreve DAX e sabe por que funciona.
>
> Quase todo mundo empaca aqui, por volta da 40ª à 80ª hora de estudo. **Não é você. É o
> assunto.** A sintaxe do DAX é fácil de propósito; a semântica é profunda. Essa
> descontinuidade é o maior defeito de projeto da linguagem
> ([`11-historia.md`](11-historia.md) §10).

---

## 1. O problema, em um exemplo

```dax
Faturamento = SUM( fVendas[Valor] )
```

Uma expressão. Resultados diferentes:

```
┌──────────────────────┐
│  Faturamento         │   contexto: {}
│  R$ 167.700.759      │   → soma tudo
└──────────────────────┘

┌───────────┬──────────────┐
│ Categoria │ Faturamento  │   Linha "Tintas":  contexto = {Categoria="Tintas"}
├───────────┼──────────────┤   Linha "Resinas": contexto = {Categoria="Resinas"}
│ Tintas    │ 107.237.686  │
│ Resinas   │  21.207.771  │   TOTAL: contexto = {}  ← NÃO é a soma das linhas!
│ Total     │ 167.700.759  │      É a MESMA medida, com contexto vazio.
└───────────┴──────────────┘

Com segmentação "Ano = 2026" ativa:
┌───────────┬──────────────┐
│ Tintas    │  26.104.512  │   contexto = {Categoria="Tintas", Ano=2026}
└───────────┴──────────────┘
```

**A medida não muda. O contexto muda.** Tudo em DAX decorre disso.

---

## 2. As duas espécies de contexto

Existem exatamente **dois**, e confundi-los é a origem de praticamente todo erro em DAX.

### 2.1 Contexto de filtro (*filter context*)

> Conjunto de **filtros ativos** sobre as colunas do modelo, no momento da avaliação.

**Quem cria:**

| Origem | Exemplo |
|---|---|
| Linhas/colunas de uma matriz | `Categoria = "Tintas"` |
| Segmentação | `Ano = 2026` |
| Filtro de visual/página/relatório | `Regiao = "Sul"` |
| Cross-highlight (clique em outro visual) | |
| **`CALCULATE`** | `CALCULATE([M], dProduto[Linha]="Manutenção")` |
| RLS | `dVendedor[Equipe] = "Sul"` |
| A cláusula `EVALUATE ... ` numa consulta | |

**O que ele faz:** restringe quais linhas de cada tabela estão visíveis. Não existe
"linha atual"; existe um **conjunto** visível.

**Propaga** pelos relacionamentos, da dimensão para o fato.

### 2.2 Contexto de linha (*row context*)

> A noção de **"a linha atual"** de uma tabela.

**Quem cria:**

| Origem | Exemplo |
|---|---|
| **Coluna calculada** | Sempre existe: a coluna é avaliada linha a linha |
| **Iteradores (`X`)** | `SUMX`, `AVERAGEX`, `FILTER`, `ADDCOLUMNS`, `RANKX`… |

**O que ele faz:** permite referenciar `Tabela[Coluna]` e obter **o valor daquela linha**.

**O que ele NÃO faz — e este é o ponto crítico:**

> **Contexto de linha NÃO filtra nada.**

```dax
-- Numa coluna calculada de fVendas:
Coluna = SUM( fVendas[Valor] )
-- Resultado: o MESMO valor em todas as linhas — a soma da tabela inteira.
-- O contexto de linha não restringiu nada. Ele só diz "estamos na linha N".
```

Isso choca quem vem do Excel, onde estar numa linha implica estar restrito a ela. Em DAX,
não implica.

### 2.3 A tabela que resume

| | Contexto de filtro | Contexto de linha |
|---|---|---|
| O que é | Conjunto de filtros | Ponteiro para a linha atual |
| Criado por | Visual, segmentação, `CALCULATE`, RLS | Coluna calculada, iteradores |
| Propaga por relação | **Sim** | **Não** |
| Filtra dados | **Sim** | **Não** |
| Permite `Tabela[Coluna]` direto | Não (precisa de agregação) | **Sim** |
| Pode haver vários aninhados | Não (há um só, composto) | **Sim** (iteradores aninhados) |

---

## 3. O contexto de linha não atravessa relações — quase

```dax
-- Coluna calculada em fVendas:
Categoria = dProduto[Categoria]     -- ✘ ERRO
```

Por quê? O contexto de linha existe em `fVendas`. Ele **não** propaga para `dProduto`.

**Solução no lado "muitos" → "um":**

```dax
Categoria = RELATED( dProduto[Categoria] )     -- ✔
```

`RELATED` segue a relação **para o lado 1** e traz o valor.

**Solução no lado "um" → "muitos":**

```dax
-- Coluna calculada em dProduto:
Total Vendido = SUMX( RELATEDTABLE( fVendas ), fVendas[Valor] )   -- ✔
```

`RELATEDTABLE` devolve as linhas do fato relacionadas àquela linha da dimensão. Por baixo,
`RELATEDTABLE` é `CALCULATETABLE(tabela)` — ou seja, **usa transição de contexto** (§4).

---

## 4. Transição de contexto — o conceito mais sutil do DAX

> **Transição de contexto** (*context transition*) — quando `CALCULATE` é avaliado dentro
> de um contexto de linha, ele **converte** esse contexto de linha em contexto de filtro.

### 4.1 O que isso significa na prática

```dax
-- Coluna calculada em dProduto:
Vendas do Produto = CALCULATE( SUM( fVendas[Valor] ) )
```

`CALCULATE` sem nenhum argumento de filtro parece inútil. Não é: ele dispara a transição.

O que acontece:
1. Existe um contexto de linha em `dProduto` (linha do produto X).
2. `CALCULATE` transforma isso num contexto de filtro: `dProduto[SK_Produto] = X` — e
   **todas as outras colunas daquela linha também**.
3. Esse filtro propaga por relação até `fVendas`.
4. `SUM` agrega só as vendas do produto X.

Sem `CALCULATE`, `SUM(fVendas[Valor])` daria o total geral em toda linha.

### 4.2 A regra de ouro

> **Toda medida referenciada dentro de um iterador tem `CALCULATE` implícito.**

```dax
SUMX( dProduto, [Faturamento Líquido] )
-- é equivalente a
SUMX( dProduto, CALCULATE( [Faturamento Líquido] ) )
```

**Isso explica** por que este padrão funciona:

```dax
Produtos acima de 1 milhão =
COUNTROWS( FILTER( VALUES( dProduto[Produto] ), [Faturamento Líquido] > 1000000 ) )
```

`FILTER` cria contexto de linha sobre os produtos; `[Faturamento Líquido]` (medida) tem
`CALCULATE` implícito; a transição filtra o fato para aquele produto. Sem transição de
contexto, esta medida devolveria "todos ou nenhum".

**E explica também** por que este outro **não** funciona como o esperado:

```dax
-- ✘ SUM não é medida: não há CALCULATE implícito, não há transição
Produtos acima de 1 milhão =
COUNTROWS( FILTER( VALUES( dProduto[Produto] ), SUM( fVendas[Valor] ) > 1000000 ) )
-- SUM devolve o total geral em toda linha → conta todos ou nenhum
```

**Corolário prático, e é uma regra que vale carregar:**

> Dentro de um iterador, prefira **medidas** a expressões de agregação cruas. A medida traz
> a transição de contexto de graça e é o que você quase sempre quer.

### 4.3 O custo

Transição de contexto é **cara**. Ela reconstrói o contexto de filtro a cada iteração.
Iterar 1 milhão de linhas com transição significa 1 milhão de reconstruções.

Regra: itere sobre **dimensões** (poucas linhas), não sobre **fatos** (muitas).

```dax
-- ✘ transição de contexto 60 milhões de vezes
SUMX( fVendas, [Faturamento Líquido] )

-- ✔ transição 25 vezes
SUMX( VALUES( dProduto[Produto] ), [Faturamento Líquido] )
```

---

## 5. `CALCULATE` desmontado

### 5.1 A sintaxe e a ordem real

```dax
CALCULATE( <expressão>, <filtro1>, <filtro2>, ... )
```

**A ordem de execução, que não é a de leitura:**

```
1. Avalia os argumentos de filtro
   · no contexto ORIGINAL (de fora), NÃO no modificado
2. Faz a transição de contexto, se houver contexto de linha
3. Aplica os modificadores de filtro (ALL, REMOVEFILTERS, KEEPFILTERS, USERELATIONSHIP…)
4. Aplica os filtros do passo 1, SUBSTITUINDO os existentes nas mesmas colunas
5. Só então avalia a <expressão>, no novo contexto
```

O passo 1 é a fonte de metade das surpresas: os filtros são avaliados **antes** e **fora**
das mudanças que o próprio `CALCULATE` faz.

### 5.2 Substituir × intersectar

```dax
-- Usuário selecionou Categoria = "Vernizes" na segmentação

CALCULATE( [Fat], dProduto[Categoria] = "Tintas" )
-- → Faturamento de TINTAS. O filtro do usuário foi SUBSTITUÍDO.

CALCULATE( [Fat], KEEPFILTERS( dProduto[Categoria] = "Tintas" ) )
-- → BLANK. A interseção {Vernizes} ∩ {Tintas} é vazia.
```

**Qual é o certo?** Depende do que você quer dizer. Ambos têm uso:

- *"quanto vendemos de tintas, independentemente do que o usuário filtrou"* → substituir;
- *"dentro do que o usuário selecionou, quanto é tinta"* → `KEEPFILTERS`.

**Diga qual dos dois você quer, no nome da medida.** `Faturamento de Tintas (fixo)` versus
`Faturamento de Tintas (na seleção)`.

### 5.3 Por que substitui? A equivalência

```dax
CALCULATE( [Fat], dProduto[Categoria] = "Tintas" )
```
é açúcar sintático para:
```dax
CALCULATE( [Fat], FILTER( ALL( dProduto[Categoria] ), dProduto[Categoria] = "Tintas" ) )
```

**O `ALL` está lá.** É ele que remove o filtro existente na coluna antes de aplicar o novo.
Isso não é regra arbitrária: é a expansão literal da forma abreviada.

E `KEEPFILTERS` é:
```dax
CALCULATE( [Fat], FILTER( VALUES( dProduto[Categoria] ), dProduto[Categoria] = "Tintas" ) )
--                        ↑ VALUES respeita o contexto atual, ALL não
```

### 5.4 Filtro escalar × filtro de tabela

```dax
-- Filtro escalar (predicado simples) — o motor otimiza bem
CALCULATE( [Fat], fVendas[Quantidade] > 100 )

-- Filtro de tabela — materializa; use só quando necessário
CALCULATE( [Fat], FILTER( fVendas, fVendas[Quantidade] > fVendas[QuantidadeMinima] ) )
```

Use `FILTER(tabela, ...)` só quando o predicado envolve **duas colunas** ou uma **medida**.
Para tudo mais, o predicado simples é melhor.

---

## 6. Os modificadores de filtro

| Função | O que faz | Quando usar |
|---|---|---|
| `ALL(T)` | Remove todos os filtros de `T` | Total geral |
| `ALL(T[C])` | Remove os filtros de uma coluna | % dentro de uma dimensão |
| `REMOVEFILTERS(...)` | Sinônimo de `ALL` como modificador, mais legível | ★ prefira este |
| `ALLEXCEPT(T, T[C])` | Remove tudo de `T` **exceto** `T[C]` | Manter uma coluna fixa |
| `ALLSELECTED(...)` | Remove filtros do visual, **mantém** os externos | ★ % do total visível |
| `ALLNOBLANKROW(...)` | Como `ALL`, sem a linha em branco de integridade | Casos com órfãos |
| `KEEPFILTERS(...)` | Intersecta em vez de substituir | Restringir dentro da seleção |
| `USERELATIONSHIP(a,b)` | Ativa uma relação inativa | Segunda data |
| `CROSSFILTER(a,b,dir)` | Muda a direção do filtro localmente | Alternativa ao bidirecional |

### `ALLSELECTED`, o mais mal-entendido

```dax
% do Total = DIVIDE( [Fat], CALCULATE( [Fat], ALLSELECTED() ) )
```

Numa matriz por categoria com segmentação `Ano = 2026`:

| Denominador | Resultado |
|---|---|
| `ALL()` | Total de **todos os anos** — percentuais pequenos e enganosos |
| `ALLSELECTED()` | Total de **2026** — o que o usuário espera ✔ |
| sem modificador | O próprio numerador → sempre 100% |

`ALLSELECTED` responde: *"o que estava visível antes de o visual aplicar seus próprios
eixos?"*. É a escolha certa em 80% dos casos de percentual.

**Aviso honesto:** a semântica exata de `ALLSELECTED` em cenários aninhados é
genuinamente complexa (envolve o conceito de *shadow filter context*). Se o seu caso é
simples — matriz + segmentação — ele faz o que você espera. Se você está aninhando
`ALLSELECTED` dentro de iteradores dentro de `CALCULATE`, **teste**, não deduza.

---

## 7. `VALUES`, `DISTINCT` e a linha em branco

```dax
VALUES( dProduto[Produto] )   -- valores distintos visíveis + a linha em branco, se houver órfãos
DISTINCT( dProduto[Produto] ) -- valores distintos visíveis, SEM a linha em branco
```

**A linha em branco** aparece automaticamente quando o fato tem chaves que não existem na
dimensão (violação de integridade referencial). No projeto-modelo, as 39 vendas com
`SK_Produto = 999` produziriam essa linha — se não tivéssemos criado o membro
desconhecido de propósito.

`VALUES` com uma única linha pode ser convertido em escalar automaticamente:

```dax
-- Se houver exatamente um valor, devolve o valor. Senão, ERRO.
Ano = VALUES( dCalendario[Ano] )

-- Versão segura, e a que você deve usar:
Ano = SELECTEDVALUE( dCalendario[Ano], "vários anos" )
```

`SELECTEDVALUE(coluna, alternativa)` é `IF(HASONEVALUE(coluna), VALUES(coluna),
alternativa)`. Use sempre a versão com alternativa explícita.

---

## 8. Iteradores aninhados e `EARLIER`

Quando há iteradores dentro de iteradores, existem **vários contextos de linha
simultâneos**.

```dax
-- Padrão antigo, com EARLIER
Acumulado =
SUMX(
    FILTER( T, T[Data] <= EARLIER( T[Data] ) ),
    T[Valor]
)
```

Dentro do `FILTER`, `T[Data]` refere-se ao contexto de linha **do `FILTER`**;
`EARLIER(T[Data])` refere-se ao contexto **de fora**, o do `SUMX`.

**Escreva assim, hoje:**

```dax
Acumulado =
VAR DataAtual = T[Data]           -- captura no contexto externo
RETURN
    SUMX( FILTER( T, T[Data] <= DataAtual ), T[Valor] )
```

Mais claro, mesma semântica, e sem depender de uma função cujo nome não explica nada.
`EARLIER` existe só por compatibilidade retroativa; você vai encontrá-la em código de
2015 e precisa saber ler.

---

## 9. Um passo a passo completo

Vamos avaliar esta medida numa célula específica.

```dax
% da Categoria =
DIVIDE(
    [Faturamento Líquido],
    CALCULATE( [Faturamento Líquido], REMOVEFILTERS( dProduto[Produto] ) )
)
```

**Cenário:** matriz com `Categoria` nas linhas e `Produto` aninhado; segmentação
`Ano = 2026`; célula do produto "Tinta Epóxi 3,6L" dentro da categoria "Tintas".

```
PASSO 1 · Contexto de filtro da célula
   { dCalendario[Ano] = 2026,
     dProduto[Categoria] = "Tintas",
     dProduto[Produto] = "Tinta Epóxi Bicomponente 3,6L" }

PASSO 2 · Numerador: [Faturamento Líquido]
   Avaliado no contexto acima.
   O filtro propaga dProduto → fVendas e dCalendario → fVendas.
   → R$ 8.421.033,50   (exemplo)

PASSO 3 · Denominador: CALCULATE(..., REMOVEFILTERS(dProduto[Produto]))
   3a. Modificador REMOVEFILTERS remove o filtro de Produto:
       { Ano = 2026, Categoria = "Tintas" }
       ← Categoria PERMANECE. Só Produto foi removido.
   3b. Avalia [Faturamento Líquido] nesse contexto
       → R$ 26.104.512,00   (todas as tintas de 2026)

PASSO 4 · DIVIDE(8.421.033,50 ; 26.104.512,00) = 32,3%
```

**Leia-se:** *"esta tinta é 32,3% do faturamento de tintas em 2026"*.

Se tivéssemos usado `REMOVEFILTERS(dProduto)` (a tabela inteira, sem especificar coluna), o
denominador seria **todos os produtos** de 2026 — e o número significaria outra coisa
completamente diferente. Um caractere muda a pergunta que o relatório responde.

---

## 10. Como depurar contexto

Sequência que uso, nesta ordem exata:

**1. Ponha o resultado numa matriz e desagregue.** Números errados revelam o padrão
quando você desce a granularidade.

**2. Decomponha em medidas intermediárias.** Cada `VAR` vira uma medida temporária. Coloque
todas lado a lado na matriz. O erro aparece na coluna onde o valor deixa de fazer sentido.

**3. Compare linha com total.** Se as linhas estão certas e o total errado, o problema é
**contexto**, não aritmética.

**4. Use `CONCATENATEX` para "imprimir" o contexto:**

```dax
Debug Contexto =
"Categorias: " & CONCATENATEX( VALUES( dProduto[Categoria] ), dProduto[Categoria], ", " ) &
" | Anos: " & CONCATENATEX( VALUES( dCalendario[Ano] ), dCalendario[Ano], ", " ) &
" | Linhas de fVendas visíveis: " & FORMAT( COUNTROWS( fVendas ), "#,0" )
```

Coloque isso num cartão ou numa coluna da matriz. É o `print()` do DAX, e é a técnica de
depuração mais subutilizada que existe.

**5. Use a Exibição de Consulta DAX** com `EVALUATE` para ver a tabela crua:

```dax
EVALUATE
SUMMARIZECOLUMNS(
    dProduto[Categoria],
    dCalendario[Ano],
    "Fat",  [Faturamento Líquido],
    "Debug", [Debug Contexto]
)
```

**6. DAX Studio** para o plano de consulta, quando o problema for desempenho e não valor.

---

## 11. Os cinco porquês: por que o total não é a soma das linhas?

1. **Por que o total de uma matriz difere da soma visível?**
   Porque a célula de total é a **mesma medida avaliada num contexto diferente** — o
   contexto sem o filtro da linha. Não há nenhuma operação de soma entre as células.

2. **Por que o Power BI não soma as células, que seria o intuitivo?**
   Porque somar células só faria sentido para medidas aditivas. Para `Margem %`, `Ticket
   Médio`, `DISTINCTCOUNT` ou `RANKX`, a soma das linhas é matematicamente sem sentido.

3. **Por que não somar quando é aditivo e recalcular quando não é?**
   Porque o motor **não tem como saber** se uma expressão arbitrária é aditiva. Isso é
   equivalente a decidir uma propriedade semântica de um programa qualquer — e, em geral,
   é indecidível (é uma instância do teorema de Rice; ver [`60`](60-teoria-avancada.md)).

4. **Por que não pedir ao autor que declare se é aditiva?**
   Seria possível, e algumas ferramentas fazem algo assim. Mas uma declaração que o motor
   não pode verificar vira uma promessa que alguém quebra — e o resultado seria um número
   errado com aparência de correto, que é o pior tipo de erro. A escolha do DAX é ter
   **uma** regra, sempre válida.

5. **Parada legítima — consistência semântica escolhida sobre intuição.**
   A regra "sempre reavalia" é uniforme, previsível e correta em todos os casos.
   O preço é que ela contraria a intuição de quem vem de planilha. **Opinião do autor:**
   é a decisão certa. Um modelo de cálculo com exceções seria impossível de raciocinar
   sobre, e o BI corporativo depende exatamente disso — de poder confiar que a mesma
   medida significa a mesma coisa em qualquer lugar.

---

## 12. Resumo em dez frases

1. Uma medida é uma **regra**, não um número.
2. Todo número nasce de **uma medida + um contexto**.
3. Contexto de filtro **restringe**; contexto de linha **aponta**.
4. Contexto de linha **não filtra nada**.
5. Contexto de filtro **propaga** por relação; contexto de linha **não**.
6. `CALCULATE` **modifica** o contexto de filtro e **converte** contexto de linha em
   contexto de filtro (transição).
7. Toda medida dentro de um iterador tem `CALCULATE` implícito.
8. `CALCULATE` **substitui** filtros na mesma coluna; `KEEPFILTERS` **intersecta**.
9. `ALLSELECTED` é quase sempre o que você quer para "% do total".
10. O total é a mesma medida com contexto diferente. **Nunca** é a soma das linhas.

---

## 13. Autoteste

1. Quais são os dois tipos de contexto? Quem cria cada um?
2. Por que `SUM(fVendas[Valor])` numa coluna calculada de `fVendas` devolve sempre o mesmo
   valor?
3. Por que `dProduto[Categoria]` numa coluna calculada de `fVendas` dá erro, e como resolver?
4. Explique transição de contexto e diga como se dispara.
5. Por que `SUMX(dProduto, [Faturamento])` funciona mas
   `COUNTROWS(FILTER(VALUES(dProduto[Produto]), SUM(fVendas[Valor]) > 0))` não faz o que
   se espera?
6. Descreva as cinco etapas da ordem de execução de `CALCULATE`.
7. Expanda `CALCULATE([Fat], dProduto[Categoria]="Tintas")` na forma com `FILTER`.
   Onde está o `ALL` e o que ele causa?
8. Diferencie `ALL`, `ALLSELECTED` e `ALLEXCEPT` com um exemplo de uso para cada.
9. Qual a diferença entre `VALUES` e `DISTINCT`, e de onde vem a linha em branco?
10. Reescreva um `EARLIER` usando `VAR` e explique por quê.
11. Explique, com o teorema de Rice, por que o motor não pode "somar quando for aditivo".
12. Descreva a técnica de depuração com `CONCATENATEX`.

---

**Próximo:** [`17-dax-inteligencia-de-tempo.md`](17-dax-inteligencia-de-tempo.md) — tempo,
que é onde tudo o que você aprendeu aqui é exercitado ao mesmo tempo.
