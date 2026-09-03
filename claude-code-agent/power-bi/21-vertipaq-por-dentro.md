# 21 · VertiPaq por dentro

**Nível:** avançado
**Data:** 14/08/2026

Este é o capítulo que transforma "meu modelo está grande" de reclamação em diagnóstico.
Sem caixas-pretas: vamos ver como cada byte é armazenado e por que.

---

## 1. O ponto de partida: por que colunar

Duas formas de guardar a mesma tabela na memória:

```
POR LINHA (row store) — OLTP
┌────────────────────────────────────────────────────────────┐
│ 100001│2026-03-14│ 3│10│315,00 ‖ 100002│2026-03-15│ 7│ 4│428,00 ‖ ...
└────────────────────────────────────────────────────────────┘
  Ler "soma de Valor" exige percorrer TUDO, pulando 4 campos a cada 5.

POR COLUNA (column store) — OLAP
┌─────────────────────────┐
│ NF:     100001│100002│100003│...          │  ← contíguo
├─────────────────────────┤
│ Data:   2026-03-14│2026-03-15│...         │
├─────────────────────────┤
│ SK_Prod: 3│7│3│12│3│7│3│...               │
├─────────────────────────┤
│ Valor:  315,00│428,00│787,50│...          │  ← só isto é lido
└─────────────────────────┘
```

**Três ganhos, e o terceiro é o maior:**

1. **Menos I/O.** Somar `Valor` lê só a coluna `Valor`.
2. **Cache-friendly.** Bytes contíguos do mesmo tipo; o pré-buscador da CPU acerta sempre.
3. **Compressão brutal.** Valores de uma mesma coluna são **homogêneos** — mesmo tipo,
   poucos distintos, muita repetição. Numa linha, valores vizinhos são heterogêneos.
   Compressão explora redundância local, e a coluna tem redundância local de sobra.

---

## 2. As três técnicas de compressão

O VertiPaq aplica, coluna a coluna, uma combinação de três técnicas. **Ele escolhe
automaticamente**, com base em amostragem.

### 2.1 Value encoding (codificação por valor)

Para colunas **numéricas inteiras**. Armazena a diferença em relação a um valor base,
usando o mínimo de bits necessários.

```
Coluna original:   1.045.302   1.045.318   1.045.291   1.045.340
Mínimo: 1.045.291
Armazenado como:          11          27           0          49
                   ↑ cabe em 6 bits em vez de 21
```

Custo de leitura: **zero indireção**. É a codificação mais rápida.

### 2.2 Hash encoding / dictionary encoding

Para colunas de **texto** ou numéricas que não se prestam ao value encoding. Cria um
**dicionário** de valores distintos e armazena índices.

```
DICIONÁRIO                       COLUNA ARMAZENADA
┌────┬──────────────────────┐    ┌───┬───┬───┬───┬───┬───┐
│ 0  │ Tintas               │    │ 0 │ 2 │ 0 │ 1 │ 0 │ 2 │
│ 1  │ Vernizes             │    └───┴───┴───┴───┴───┴───┘
│ 2  │ Resinas              │      ↑ 2 bits por linha
│ 3  │ Solventes            │        (7 valores → 3 bits)
└────┴──────────────────────┘
```

Custo: uma indireção (consulta ao dicionário) na leitura, e o espaço do dicionário.
**É por isso que cardinalidade é o preço:** o dicionário cresce com o número de valores
**distintos**, não com o número de linhas.

### 2.3 Run-Length Encoding (RLE)

Comprime **sequências repetidas** em pares (valor, contagem).

```
Coluna ordenada:  A A A A A A B B B C C C C C C C C
RLE:              (A,6) (B,3) (C,8)
```

Numa coluna de 60 milhões de linhas com 7 valores distintos **e ordenada**, o RLE pode
reduzir a coluna a algumas dezenas de pares.

**RLE depende da ordem.** É aqui que entra a otimização mais interessante do motor.

---

## 3. A ordenação das linhas — o segredo

Durante o processamento, o VertiPaq **reordena as linhas** da tabela para maximizar a
eficácia do RLE em todas as colunas ao mesmo tempo.

Isso é um problema de otimização combinatória: ordenar para favorecer uma coluna pode
prejudicar outra. O motor usa heurísticas e testa um número limitado de permutações
(configurável em cenários avançados via `MaxSegmentSizeRows` e afins).

**Duas consequências práticas:**

1. **Colunas de alta cardinalidade estragam a festa.** Uma coluna com valores quase todos
   distintos (`NF`, `Timestamp`, `GUID`) não comprime por RLE **e** dificulta encontrar
   uma ordem boa para as outras.
2. **Remover uma coluna inútil melhora a compressão das que ficam.** Não é apenas o espaço
   dela que você economiza — é a liberdade de ordenação que você devolve ao motor.

**Este é o argumento técnico por trás de "remova colunas que ninguém usa".**

---

## 4. Segmentos e paralelismo

A tabela é dividida em **segmentos** (por padrão, cerca de 1 milhão de linhas cada; 8
milhões em capacidades). Cada segmento é comprimido de forma independente e pode ser
varrido por um núcleo diferente.

```
fVendas (60 milhões de linhas)
┌──────────┬──────────┬──────────┬─────┬──────────┐
│ Seg 1    │ Seg 2    │ Seg 3    │ ... │ Seg 60   │
│ 1M linhas│ 1M linhas│ 1M linhas│     │ 1M linhas│
└─────┬────┴─────┬────┴─────┬────┴─────┴─────┬────┘
      │ core 1   │ core 2   │ core 3         │ core N
      └──────────┴──────────┴────────────────┘
                     ▼
              resultado parcial → combinação
```

**Consequências:**

- Mais núcleos = varredura mais rápida (até o limite de memória e do SKU).
- Tabelas pequenas (< 1 segmento) não se beneficiam de paralelismo.
- A **primeira** amostragem de compressão é feita no primeiro segmento; dados atípicos no
  começo da tabela podem levar a escolhas ruins de codificação para toda a tabela.

---

## 5. O que realmente ocupa espaço

Cada coluna tem **quatro** estruturas:

| Estrutura | O que é | Cresce com |
|---|---|---|
| **Data** | Os valores codificados | Nº de linhas × bits por valor |
| **Dictionary** | Mapa índice → valor | **Cardinalidade** |
| **Hierarchy** (*attribute hierarchy*) | Estrutura de ordenação/agrupamento por valor | **Cardinalidade** |
| **Relationship** | Estruturas de junção | Cardinalidade da chave |

**A "hierarchy" é o custo escondido.** Cada coluna ganha, por padrão, uma estrutura interna
que permite agrupar e ordenar por ela. Em colunas de altíssima cardinalidade que **nunca
são usadas em visuais** (um ID técnico, por exemplo), essa estrutura é puro desperdício.

Ela pode ser desabilitada por coluna (`isAvailableInMdx = false`, via Tabular Editor).
Ganho típico: **5% a 20%** do tamanho do modelo em modelos com muitas chaves. Cuidado: a
coluna deixa de ser utilizável em MDX (Excel) e como eixo.

---

## 6. Medindo: VertiPaq Analyzer

A ferramenta que transforma tudo isso em ação. Vem embutido no **DAX Studio**
(guia *Advanced* → *View Metrics*) e também existe como pasta de trabalho separada.

O que ele mostra, por coluna:

| Métrica | O que significa | O que fazer |
|---|---|---|
| **Cardinality** | Valores distintos | O número que governa tudo |
| **Total Size** | Data + Dictionary + Hierarchy | O alvo |
| **% Table** | Participação na tabela | Ordene por aqui |
| **Data Size** | Só os valores | |
| **Dictionary Size** | Só o dicionário | Alto = cardinalidade alta em texto |
| **Hierarchy Size** | A estrutura de atributo | Alto e coluna não usada = candidata a `isAvailableInMdx=false` |
| **Encoding** | VALUE ou HASH | HASH em coluna numérica pode indicar tipo errado |
| **RI Violations** | Chaves órfãs | Deve ser zero |

**O fluxo de otimização, em cinco passos:**

1. Abra o VertiPaq Analyzer e **ordene por Total Size, decrescente**.
2. Olhe as **10 primeiras colunas**. Em modelos reais, elas costumam ser 60–80% do total.
3. Para cada uma pergunte: **é usada? precisa dessa precisão? precisa dessa granularidade?**
4. Aplique a correção (remover, arredondar, dividir, trocar por chave).
5. Reprocesse e meça de novo.

**Esse fluxo, aplicado por duas horas, tipicamente reduz um modelo em 30–60%.** É o melhor
retorno por hora que existe em Power BI.

---

## 7. As otimizações, em ordem de retorno

### 7.1 Remover colunas não usadas — o campeão

Toda coluna carregada custa, seja usada ou não. Em modelos reais, é comum que 30–50% das
colunas nunca apareçam em visual nem medida algum.

Ferramentas: **Measure Killer**, ou o relatório de metadados via
`INFO.VIEW.COLUMNS()`/DMVs no DAX Studio.

### 7.2 Separar Data de Hora

```
❌ DataHora  (datetime com segundos)   → cardinalidade = nº de linhas
✔ Data      (date)                    → ~1.100 valores
✔ Hora      (time truncada em minuto) → 1.440 valores
```

Em modelos de IoT e de historiador industrial, esta única mudança já reduziu modelos pela
metade em casos que acompanhei. E, além do espaço, ela **viabiliza a relação com a
`dCalendario`**, que não funciona com `datetime`.

### 7.3 Arredondar decimais

`315,0000001` e `315,00` custam a mesma coisa na tela e ordens de grandeza diferentes na
memória, porque a cardinalidade explode. Arredonde para a precisão que o negócio usa —
e considere o tipo **Decimal Fixo** (Currency), que é internamente inteiro.

### 7.4 Chaves inteiras em vez de texto

`SK_Cliente = 4711` versus `CNPJ = "12.345.678/0001-95"`, repetido 60 mil vezes. A chave
inteira usa *value encoding* (sem dicionário, sem indireção) e acelera as junções.

### 7.5 Desligar a data/hora automática

Uma tabela de datas oculta **por coluna de data**. Em modelos com 4 colunas de data,
são 4 tabelas com 8 colunas cada, invisíveis no painel.

### 7.6 Reduzir granularidade quando possível

Se ninguém analisa por item de NF, agregue por NF. Reduz linhas por um fator de 2 a 5.
**Decisão irreversível** — avalie com cuidado ([`10-fundamentos.md`](10-fundamentos.md) §3).

### 7.7 `isAvailableInMdx = false` em chaves técnicas

Via Tabular Editor, nas colunas `SK_*` que estão ocultas e nunca são usadas como eixo.
Ganho de 5–20% em modelos com muitas chaves.

### 7.8 Desabilitar medidas implícitas

Impede que o usuário arraste uma coluna numérica direto para o visual. Melhora a
governança e é **pré-requisito prático** para grupos de cálculo funcionarem bem.

---

## 8. Um exemplo numérico

Modelo hipotético, mas com proporções realistas: fato de 50 milhões de linhas.

**Antes:**

| Coluna | Cardinalidade | Tamanho | % |
|---|---:|---:|---:|
| `Timestamp` (datetime, segundos) | 43.200.000 | 1.180 MB | **47%** |
| `IDTransacao` (GUID em texto) | 50.000.000 | 720 MB | **29%** |
| `Valor` (decimal, 8 casas) | 12.400.000 | 310 MB | 12% |
| `SK_Produto` | 4.200 | 62 MB | 2% |
| demais 18 colunas | — | 240 MB | 10% |
| **Total** | | **2.512 MB** | |

**Depois:**

| Mudança | Resultado |
|---|---|
| `Timestamp` → `Data` + `Hora` (minuto) | 1.180 MB → 71 MB |
| `IDTransacao` removida (não usada em nenhum visual) | 720 MB → 0 |
| `Valor` arredondado para 2 casas | 310 MB → 96 MB |
| **Total** | **2.512 MB → 469 MB (−81%)** |

Três mudanças, uma tarde de trabalho, um modelo que passa a caber em Pro.

> **Aviso:** os números acima são **ilustrativos**, construídos para mostrar as proporções
> típicas. Não foram medidos nesta máquina. Meça o seu com o VertiPaq Analyzer — as
> proporções costumam ser parecidas, os valores absolutos nunca são.

---

## 9. O que o VertiPaq **não** faz bem

Honestidade sobre os limites:

| Situação | Por quê |
|---|---|
| Colunas com valores quase todos distintos | Nenhuma técnica comprime |
| Texto livre longo (descrições, comentários) | Dicionário gigante; considere não carregar |
| Muitas tabelas pequenas em floco | Cada salto é trabalho de junção |
| `DISTINCTCOUNT` em coluna de alta cardinalidade | Exige materializar; é a agregação mais cara |
| Dados que mudam a cada minuto | O modelo inteiro é reprocessado (salvo incremental/Direct Lake) |
| Cálculos linha a linha complexos em medidas | Cai no motor de fórmula, que é sequencial |

---

## 10. Os cinco porquês: por que cardinalidade importa mais que o número de linhas?

1. **Por que uma coluna com 60 milhões de linhas e 7 valores é minúscula?**
   Porque o dicionário tem 7 entradas e cada linha guarda um índice de 3 bits — e, se as
   linhas estiverem ordenadas, o RLE reduz tudo a 7 pares.

2. **Por que a mesma tabela com uma coluna de 60 milhões de valores distintos é enorme?**
   Porque o dicionário precisa guardar 60 milhões de valores, cada índice precisa de 26
   bits, e o RLE não comprime nada — não há sequências repetidas.

3. **Por que o RLE não funciona sem repetição?**
   Porque RLE é, literalmente, "valor + quantas vezes seguidas". Sem repetição, o par
   `(valor, 1)` ocupa **mais** que o valor sozinho. O motor detecta isso e não aplica RLE.

4. **Por que não usar um algoritmo de compressão de propósito geral, como gzip?**
   Porque o objetivo não é só reduzir bytes — é **consultar sem descomprimir**. O VertiPaq
   varre e agrega diretamente sobre a representação comprimida. Gzip exigiria descomprimir
   tudo antes de qualquer operação, e aí a compressão viraria custo, não benefício.

5. **Parada legítima — teoria da informação.**
   No limite, a **entropia de Shannon** estabelece um piso: uma coluna com N valores
   igualmente prováveis e distintos precisa de pelo menos log₂(N) bits por valor. Nenhum
   algoritmo, nem hoje nem nunca, comprime abaixo disso sem perder informação. Alta
   cardinalidade é cara **por um teorema**, não por limitação de implementação. É a
   parada mais legítima que existe.

**Corolário prático:** quando você reduz cardinalidade (separando data e hora, arredondando
decimais), você não está "enganando o compressor" — está **reduzindo genuinamente a
quantidade de informação** que precisa ser guardada, aceitando que a precisão descartada
não tinha valor de negócio. É uma decisão de modelagem, e ela deve ser consciente.

---

## 11. Autoteste

1. Cite os três ganhos do armazenamento colunar e diga qual é o maior.
2. Descreva as três técnicas de compressão e quando cada uma é escolhida.
3. Por que o RLE depende da ordem das linhas, e o que o motor faz a respeito?
4. Por que remover uma coluna inútil melhora a compressão das outras?
5. Quais são as quatro estruturas de uma coluna, e qual é o "custo escondido"?
6. Descreva o fluxo de cinco passos com o VertiPaq Analyzer.
7. Por que separar `DataHora` em `Data` + `Hora` tem dois benefícios distintos?
8. Cite três situações em que o VertiPaq comprime mal.
9. Por que não usar gzip em vez das técnicas do VertiPaq?
10. Explique, com entropia de Shannon, por que alta cardinalidade é cara por teorema.

---

**Próximo:** [`22-desempenho.md`](22-desempenho.md) — do diagnóstico à correção.
