# 22 · Desempenho

**Nível:** avançado
**Data:** 14/08/2026

Este capítulo é sobre método. Otimizar por palpite é a norma no mercado e é desperdício:
sem medir, você conserta o que não estava quebrado e não descobre o gargalo real.

---

## 1. O método, em cinco passos

```
1. REPRODUZIR   → qual visual, qual clique, qual filtro? Quanto tempo, medido?
2. LOCALIZAR    → Analisador de Desempenho: qual visual e qual fase?
3. ISOLAR       → copie a consulta DAX para o DAX Studio
4. DIAGNOSTICAR → Server Timings: FE × SE; Query Plan
5. CORRIGIR     → uma mudança por vez, medindo depois de cada uma
```

**Regra:** nunca faça duas correções antes de medir. Você não saberá qual funcionou, e
uma delas pode ter piorado.

---

## 2. Onde o tempo se esconde

```
Tempo total percebido pelo usuário
├── ① Refresh (o dado chegar ao modelo)          ← 1× por dia
├── ② Consulta DAX (o número ser calculado)      ← toda interação ★
├── ③ Renderização (o visual desenhar)           ← toda interação ★
└── ④ Rede e navegador                           ← toda interação
```

②③④ são multiplicados por (usuários × interações). ① acontece uma vez por dia. **Comece
por ②.**

---

## 3. Analisador de Desempenho

**Guia Otimizar → Analisador de Desempenho → Iniciar gravação → interagir.**

Para cada visual, três números:

| Fase | Significa | Se estiver alto |
|---|---|---|
| **Consulta DAX** | O motor calculando | Problema de modelo ou de medida → §4 |
| **Exibição visual** | O visual desenhando | Muitos pontos/linhas; visual customizado pesado |
| **Outro** | Espera, sincronização, preparação | Muitos visuais competindo; segmentações complexas |

**Referências práticas** (não são padrões oficiais; são o que eu uso):

| Tempo de consulta | Leitura |
|---|---|
| < 100 ms | Excelente |
| 100–500 ms | Bom |
| 500 ms – 2 s | Aceitável, otimizável |
| 2–5 s | Ruim; o usuário percebe e reclama |
| > 5 s | Inaceitável em uso rotineiro |

**O botão que muda tudo:** ao lado de cada visual, **Copiar consulta**. Ele dá a consulta
DAX exata que o visual dispara. Cole no DAX Studio e você tem o problema isolado, sem
ruído de interface.

---

## 4. DAX Studio: motor de fórmula × motor de armazenamento

Esta é a distinção central do diagnóstico de DAX.

| | Motor de armazenamento (SE) | Motor de fórmula (FE) |
|---|---|---|
| O que faz | Varre colunas, agrega, filtra | Combina resultados, lógica complexa, iteração |
| Paralelo? | **Sim**, multithread | **Não**, single-thread |
| Opera sobre | Dados comprimidos | *Datacaches* materializados |
| Cacheável? | Sim (cache do SE) | Não |
| Velocidade relativa | Rápido | **Lento** |

**A regra de ouro:**

> Empurre o máximo de trabalho para o **SE**. Todo tempo gasto no **FE** é tempo caro.

### 4.1 Como medir

1. DAX Studio conectado ao modelo.
2. Ligue **Server Timings** e **Query Plan**.
3. Clique em **Clear Cache** (essencial — senão você mede o cache, não a consulta).
4. Execute a consulta.

Leitura da aba *Server Timings*:

```
Total     1.842 ms
SE        204 ms   (11%)   ← 3 consultas ao motor de armazenamento
FE      1.638 ms   (89%)   ← ⚠ PROBLEMA AQUI
SE CPU    612 ms           (paralelismo de 3,0×)
```

**89% no FE é o sintoma clássico** de: iteração sobre tabela grande, transição de contexto
em massa, ou lógica que o SE não consegue executar.

### 4.2 `CallbackDataID` — o sinal de alerta

Nas consultas xmSQL exibidas pelo Server Timings, procure por `CallbackDataID`.

```
SELECT SUM([CallbackDataID(...)]) FROM fVendas
```

Significa que o SE **teve de chamar o FE de volta**, linha a linha, para avaliar uma
expressão que ele não sabe executar. Isso destrói o paralelismo e desabilita o cache do SE.

**Causas comuns:**

| Padrão | Alternativa |
|---|---|
| `IF` dentro de `SUMX` sobre o fato | Filtrar antes com `CALCULATE` |
| `DIVIDE` dentro de iterador sobre o fato | Reestruturar |
| Funções de texto dentro de iterador | Calcular no Power Query |
| `SWITCH` complexo dentro de iterador | Coluna calculada ou reestruturação |
| Chamadas a medidas dentro de iterador sobre o fato | Iterar a dimensão |

### 4.3 O padrão de correção mais frequente

```dax
-- ❌ FE alto, CallbackDataID, itera 60 milhões de linhas
Vendas de Tintas =
SUMX(
    fVendas,
    IF( RELATED( dProduto[Categoria] ) = "Tintas",
        fVendas[Quantidade] * fVendas[PrecoUnitario],
        0 )
)

-- ✔ o filtro vai para o SE; a iteração fica sobre o subconjunto
Vendas de Tintas =
CALCULATE(
    SUMX( fVendas, fVendas[Quantidade] * fVendas[PrecoUnitario] ),
    dProduto[Categoria] = "Tintas"
)
```

A primeira versão avalia uma condição por linha, no FE. A segunda filtra no SE e itera
apenas o que sobrou. Em modelos grandes, a diferença é de uma ordem de grandeza.

---

## 5. Catálogo de problemas e correções

### 5.1 Medidas

| Sintoma | Causa | Correção |
|---|---|---|
| FE > 70% | Iteração sobre o fato | Itere a dimensão; filtre no `CALCULATE` |
| `CallbackDataID` | Lógica no iterador | Mover para `CALCULATE` ou Power Query |
| `DISTINCTCOUNT` lento | Alta cardinalidade | Contar chave inteira; ou pré-agregar |
| Muitas materializações grandes | `FILTER(fato, ...)` | `FILTER(VALUES(dim[col]), ...)` ou predicado simples |
| Medida lenta só no total | `ALLSELECTED` aninhado, `RANKX` global | Simplifique; considere calcular na origem |
| Medida lenta com muitas linhas no visual | Transição de contexto por linha | Reduza a granularidade do visual |
| Cascata de medidas com 8 níveis | Reavaliação repetida | Achate; use `VAR` |

### 5.2 Modelo

| Sintoma | Causa | Correção |
|---|---|---|
| Modelo grande | Alta cardinalidade | VertiPaq Analyzer ([`21`](21-vertipaq-por-dentro.md)) |
| Consultas lentas em geral | Floco de neve, relações demais | Achate para estrela |
| Lentidão ao filtrar | Bidirecional | Remova; use `CROSSFILTER` local |
| Refresh lento | Falta de folding | [`13`](13-power-query-e-m.md) §3 |
| Refresh lento | Tabelas/colunas calculadas | Mover para M ou para a fonte |
| Modelo grande demais para o SKU | Granularidade fina não usada | Agregações ([`20`](20-modos-de-armazenamento.md) §7) |

### 5.3 Relatório

| Sintoma | Causa | Correção |
|---|---|---|
| Página lenta | 15 visuais | Reduza para 5–8; use drillthrough |
| Lentidão ao clicar | Interações desnecessárias | Editar interações → Nenhum onde não faz sentido |
| Segmentação lenta | Milhares de itens | Suspensa com busca; ou hierárquica |
| Tabela lenta | 50 mil linhas no visual | Filtre; exportação é outro caminho |
| Tudo lento no Service, rápido no Desktop | Capacidade compartilhada ou saturada | Ver §7 |

---

## 6. Uma sessão de otimização, passo a passo

Exemplo do tipo de raciocínio, com um caso realista.

**Sintoma.** Página "Análise de Margem" leva 9 segundos para abrir.

**Passo 1 — Analisador de Desempenho:**

```
Matriz "Margem por Produto"     Consulta DAX  7.840 ms   Exibição   190 ms
Cartão "Margem %"                             120 ms                 15 ms
Gráfico "Margem por Mês"                      210 ms                 60 ms
Segmentação "Categoria"                        45 ms                 20 ms
```

Um visual responde por 87% do tempo. **Não otimize os outros.**

**Passo 2 — Copiar consulta → DAX Studio → Clear Cache → Run:**

```
Total   7.912 ms
SE        340 ms  (4%)
FE      7.572 ms  (96%)   ⚠
```

**Passo 3 — Server Timings:** três consultas xmSQL, uma delas com `CallbackDataID`, e uma
materialização de 4,2 milhões de linhas.

**Passo 4 — olhar a medida:**

```dax
Margem % Ajustada =
DIVIDE(
    SUMX(
        fVendas,
        VAR c = RELATED( dProduto[CustoPadrao] )
        VAR real = fVendas[CustoUnitario]
        RETURN
            fVendas[Quantidade] *
            ( fVendas[PrecoUnitario] - IF( real > c * 1.2, c, real ) )
    ),
    [Faturamento Líquido]
)
```

**Diagnóstico:** `IF` com `RELATED` dentro de `SUMX` sobre 60 milhões de linhas. Cada linha
exige buscar o custo padrão pela relação e avaliar uma condição — trabalho que o SE não
executa, logo `CallbackDataID`.

**Passo 5 — correção:** a regra "usar custo padrão quando o real exceder 20%" é um
**atributo da linha**, não depende de filtro. Ela pertence ao Power Query:

```powerquery
Table.AddColumn(
    ComProduto,
    "CustoAjustado",
    each if [CustoUnitario] > [CustoPadrao] * 1.2 then [CustoPadrao] else [CustoUnitario],
    type number
)
```

E a medida vira:

```dax
Margem % Ajustada =
DIVIDE(
    SUMX( fVendas, fVendas[Quantidade] * ( fVendas[PrecoUnitario] - fVendas[CustoAjustado] ) ),
    [Faturamento Líquido]
)
```

**Passo 6 — medir de novo.** O padrão esperado: FE despenca, SE assume, o `CallbackDataID`
desaparece. O custo é uma coluna a mais no modelo — troca quase sempre vantajosa.

> **Declaração honesta:** os tempos acima são **ilustrativos**, para mostrar a forma do
> raciocínio e a leitura das ferramentas. Não foram medidos nesta máquina (ambiente
> Linux, sem Power BI Desktop). O que é fato verificável é o **mecanismo**: `IF` com
> `RELATED` dentro de iterador sobre a tabela de fatos produz `CallbackDataID` e trabalho
> no motor de fórmula. Meça o seu caso.

**A lição geral, essa sim sem ressalva:**

> Quando uma regra não depende do contexto de filtro, ela **não pertence a uma medida**.
> Ela pertence ao Power Query ou à fonte.

---

## 7. Desempenho no Service

O relatório é rápido no Desktop e lento na nuvem. Causas possíveis:

| Causa | Como verificar |
|---|---|
| Capacidade compartilhada (Pro) sob carga | Sem métricas; teste em horários diferentes |
| Capacidade dedicada saturada | **App Fabric Capacity Metrics** ★ |
| *Throttling* por consumo excessivo | Idem — procure por *overload* e *carryforward* |
| Gateway sobrecarregado (DirectQuery) | Logs do gateway; CPU do servidor |
| RLS custosa | Teste como usuário com e sem RLS |
| Rede/latência do usuário | Teste de outro local |

**O app *Fabric Capacity Metrics*** é obrigatório em qualquer capacidade dedicada. Ele
mostra consumo por item, picos e eventos de throttling. Sem ele, você está adivinhando.

**Sobre throttling:** capacidades Fabric usam *smoothing* — o consumo é distribuído no
tempo. Se você estoura sistematicamente, entra em *carryforward* e depois em throttling,
que degrada tudo. O sintoma é "de repente ficou tudo lento e ninguém mudou nada".

---

## 8. Desempenho de refresh

| Prática | Ganho |
|---|---|
| **Query folding** | Altíssimo ([`13`](13-power-query-e-m.md) §3) |
| **Atualização incremental** | Altíssimo ([`06`](06-exemplos.md) §14) |
| Reduzir colunas | Alto |
| Eliminar tabelas/colunas calculadas | Alto |
| Refresh paralelo (aumentar avaliações simultâneas) | Médio (pressiona a fonte) |
| Refresh por partição via XMLA | Alto (controle fino) |
| Desligar "atualizar em segundo plano" no desenvolvimento | Produtividade |

**Ordem de investigação quando o refresh está lento:**

1. Alguma consulta perdeu o folding? (a mais provável)
2. Há tabela calculada grande?
3. A fonte está lenta? (teste a mesma consulta direto no banco)
4. A rede/gateway é o gargalo?
5. Há colunas de altíssima cardinalidade encarecendo a compressão?

---

## 9. Ferramentas — resumo

| Ferramenta | Para quê |
|---|---|
| **Analisador de Desempenho** (nativo) | Localizar o visual culpado; copiar a consulta |
| **DAX Studio** | Server Timings, Query Plan, Clear Cache, VertiPaq Analyzer |
| **VertiPaq Analyzer** | Tamanho e cardinalidade por coluna |
| **Tabular Editor + Best Practice Analyzer** | Detectar antipadrões automaticamente ★ |
| **Measure Killer** | Achar medidas e colunas não usadas |
| **Fabric Capacity Metrics** | Consumo e throttling da capacidade |
| **Log do gateway** | Diagnóstico de DirectQuery on-premises |

**O Best Practice Analyzer merece destaque:** ele roda dezenas de regras (mantidas pela
comunidade, com contribuição de Michael Kovalsky e outros) e aponta, em segundos, colunas
sem `summarizeBy`, relações bidirecionais, colunas de alta cardinalidade, uso de
`EARLIER`, medidas sem formato e dezenas de outros itens. **Rodá-lo em qualquer modelo
existente é a coisa de melhor custo-benefício deste capítulo.**

---

## 10. Os cinco porquês: por que o motor de fórmula é single-thread?

1. **Por que o FE não é paralelo, se isso resolveria tanta coisa?**
   Porque ele executa a **árvore de operadores** do DAX, que é sequencial por natureza —
   cada operador consome o resultado do anterior.

2. **Por que não paralelizar a árvore?**
   Porque as dependências entre operadores são arbitrárias e dinâmicas. Uma expressão DAX
   pode ter iteradores aninhados, transições de contexto e referências cruzadas entre
   ramos. Detectar automaticamente quais partes são independentes é caro e, em muitos
   casos, indecidível.

3. **Por que o SE consegue ser paralelo então?**
   Porque as operações do SE são **restritas e uniformes**: varrer um segmento de coluna,
   aplicar um predicado simples, agregar. São *embaraçosamente paralelas* — cada segmento
   é independente e o resultado se combina por associatividade.

4. **Por que não expandir o SE para fazer mais coisas?**
   É exatamente o que a Microsoft vem fazendo há anos: cada versão empurra mais padrões
   de DAX para o SE. Mas há um limite — no extremo, o SE teria de ser um interpretador
   completo de DAX, e aí seria o FE, com o mesmo problema.

5. **Parada legítima — trade-off entre expressividade e paralelismo.**
   Existe uma tensão fundamental entre **poder expressivo** e **paralelizabilidade**.
   Linguagens restritas (álgebra relacional, MapReduce, operações vetoriais) paralelizam
   bem; linguagens gerais, não. O DAX escolheu ser expressivo. A arquitetura de dois
   motores é a tentativa de ter os dois: um núcleo restrito e paralelo, com uma camada
   geral e sequencial por cima. **Sua habilidade como profissional é justamente manter o
   trabalho no núcleo restrito.**

---

## 11. Autoteste

1. Descreva os cinco passos do método.
2. Por que otimizar consulta importa mais que otimizar refresh?
3. O que o botão "Copiar consulta" do Analisador de Desempenho permite?
4. Diferencie FE e SE em quatro aspectos.
5. O que significa `CallbackDataID` e o que causá-lo?
6. Reescreva `SUMX(fVendas, IF(RELATED(dProduto[Categoria])="Tintas", ..., 0))` de forma
   otimizada, e explique por que a nova versão é melhor.
7. Por que "Clear Cache" antes de medir é essencial?
8. O relatório é rápido no Desktop e lento no Service. Cite três causas e como verificar.
9. O que é throttling numa capacidade Fabric e qual o sintoma?
10. Qual é a lição geral do caso de otimização da §6?
11. Explique por que o SE paraleliza e o FE não, e qual é o trade-off de fundo.

---

**Próximo:** [`23-servico-colaboracao-e-atualizacao.md`](23-servico-colaboracao-e-atualizacao.md)
— do arquivo local ao produto compartilhado.
