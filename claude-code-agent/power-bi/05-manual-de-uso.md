# 05 · Manual de uso — referência consultável

**Nível:** intermediário
**Data:** 14/08/2026 · Power BI Desktop de julho/2026
**Como usar:** este arquivo é para **consulta**, não para leitura linear. Organizado por
*tarefa*, não em ordem alfabética. Use `Ctrl+F`.

---

## Índice

1. [Anatomia da interface](#1-anatomia-da-interface)
2. [Atalhos de teclado](#2-atalhos-de-teclado)
3. [Tipos de arquivo](#3-tipos-de-arquivo)
4. [Power Query — por tarefa](#4-power-query--por-tarefa)
5. [Linguagem M — funções essenciais](#5-linguagem-m--funções-essenciais)
6. [DAX — por tarefa](#6-dax--por-tarefa)
7. [Visuais nativos — quando usar cada um](#7-visuais-nativos--quando-usar-cada-um)
8. [Formatação de números e datas](#8-formatação-de-números-e-datas)
9. [Power BI Service — operações](#9-power-bi-service--operações)
10. [Linha de comando, PowerShell e APIs](#10-linha-de-comando-powershell-e-apis)
11. [Ferramentas externas](#11-ferramentas-externas)
12. [Obsoleto — o que não usar mais](#12-obsoleto--o-que-não-usar-mais)
13. [Os atalhos que só quem usa há anos conhece](#13-os-atalhos-que-só-quem-usa-há-anos-conhece)

---

## 1. Anatomia da interface

### 1.1 As três exibições (barra à esquerda)

| Ícone | Exibição | Para que serve |
|---|---|---|
| 📊 | **Relatório** | Desenhar páginas, visuais, filtros |
| ▦ | **Tabela** (*Table*) | Ver os dados carregados, criar colunas/tabelas calculadas |
| 🔗 | **Modelo** | Relacionamentos, propriedades de campo, pastas de exibição |
| `DAX` | **Consulta DAX** (*DAX query view*) | Escrever consultas DAX ad hoc, testar medidas, definir medidas em lote |
| `TMDL` | **Visão TMDL** | Editar o modelo como **texto** (script) — poderosíssimo, ver [`25`](25-ciclo-de-vida-e-devops.md) |

### 1.2 Guias da faixa de opções

| Guia | O que tem de importante |
|---|---|
| **Página Inicial** | Obter dados · Transformar dados · Atualizar · Publicar · Nova medida |
| **Inserir** | Visuais · Caixa de texto · Botões · Imagem · Forma · Power Apps/Automate |
| **Modelagem** | Nova medida/coluna/tabela · Gerenciar funções (RLS) · Parâmetro *what-if* · Novo grupo |
| **Exibição** | Tema · Painéis (Filtros, Seleção, Indicadores, Sincronizar segmentações) · Layout móvel |
| **Otimizar** | **Pausar visuais** · Atualizar visuais · Analisador de Desempenho · Configurações de otimização |
| **Ajuda** | Sobre (versão!) · Exemplos · Enviar carranca (logs) |
| **Ferramentas Externas** | DAX Studio, Tabular Editor, Bravo, ALM Toolkit (se instalados) |

### 1.3 Painéis do lado direito (Exibição de Relatório)

| Painel | Conteúdo |
|---|---|
| **Filtros** | Filtros de visual, de página e de todas as páginas |
| **Visualizações** | Galeria de visuais + campos (*fields wells*) + formatação (pincel) + analítica (lupa) |
| **Dados** | Tabelas, colunas, medidas e hierarquias do modelo |
| **Seleção** | Ordem Z, mostrar/ocultar objetos, agrupamento |
| **Indicadores** (*Bookmarks*) | Estados salvos da página |
| **Sincronizar segmentações** | Que segmentação afeta que página |

---

## 2. Atalhos de teclado

### 2.1 Gerais (Desktop)

| Atalho | Ação |
|---|---|
| `Ctrl+S` / `Ctrl+Shift+S` | Salvar / Salvar como |
| `Ctrl+O` | Abrir |
| `Ctrl+Z` / `Ctrl+Y` | Desfazer / Refazer |
| `Ctrl+P` | Imprimir a página atual |
| `F1` | Ajuda |
| `Alt` | Mostra as *key tips* da faixa de opções |
| `F11` | Modo de foco / tela cheia |
| `Ctrl+F6` | Navegar entre painéis (acessibilidade) |
| `Ctrl+Shift+Q` | Pesquisar no menu ("diga-me o que quer fazer") |

### 2.2 Exibição de Relatório

| Atalho | Ação |
|---|---|
| `Ctrl+C` / `Ctrl+V` num visual | Copiar/colar visual — **funciona entre arquivos `.pbix` abertos** |
| `Ctrl+D` | Duplicar o objeto selecionado |
| `Ctrl+A` | Selecionar todos os visuais da página |
| `Ctrl+clique` | Adicionar à seleção |
| `Setas` / `Ctrl+setas` | Mover visual (grande / fino) |
| `Ctrl+Shift+F` | Painel de Filtros |
| `Alt+Shift+F10` | Menu do visual |
| `Alt+Shift+F11` | Modo "Mostrar dados" do visual |
| `Ctrl+Shift+E` | Adicionar página |
| `Ctrl+PgUp` / `Ctrl+PgDn` | Página anterior / próxima |
| `Ctrl+G` / `Ctrl+Shift+G` | Agrupar / desagrupar visuais |
| `Alt` + arrastar | Ignorar o alinhamento automático (*snap to grid*) |
| `Ctrl+clique` num link/botão | Ativar a ação do botão em modo de edição |

### 2.3 Editor de fórmulas DAX

| Atalho | Ação |
|---|---|
| `Shift+Enter` | Nova linha sem confirmar a fórmula |
| `Ctrl+Shift+M` | Formatar a expressão (usa o motor do DAX Formatter) |
| `Alt+Enter` | Confirmar |
| `Ctrl+Espaço` | Forçar o IntelliSense |
| `Ctrl+/` (DAX query view) | Comentar/descomentar |
| `///` acima de `MEASURE` | **(julho/2026)** Descrição da medida, gravada no modelo com *Atualizar modelo com alterações* |

### 2.4 Power Query

| Atalho | Ação |
|---|---|
| `Ctrl+Z` | Desfazer (só a última etapa) |
| `Alt+F4` | Fechar |
| `Ctrl+Alt+D` | Ir para o Editor Avançado (varia por versão) |
| Botão direito no cabeçalho | Menu de transformações da coluna |

### 2.5 Power BI Service (navegador)

| Atalho | Ação |
|---|---|
| `?` | Lista de atalhos da tela atual |
| `Ctrl+F` | Pesquisar no relatório (quando habilitado) |
| `Alt+Shift+F10` | Menu do visual |
| `F` sobre um visual | Modo de foco |

---

## 3. Tipos de arquivo

| Extensão | O que é | Contém dados? | Versionável em Git? |
|---|---|---|---|
| `.pbix` | Arquivo do Power BI Desktop (relatório + modelo + **dados**) | Sim | Não (binário) |
| `.pbit` | **Template**: mesma coisa **sem os dados** | Não | Não (binário), mas leve |
| `.pbip` | **Power BI Project**: ponteiro para pastas de texto | Não | **Sim** ★ |
| `.tmdl` | Tabular Model Definition Language — o modelo como texto | Não | **Sim** ★ |
| `.pbir` | Definição de relatório (PBIR), dentro do PBIP | Não | **Sim** |
| `.json` (theme) | Tema de relatório | Não | Sim |
| `.pbids` | Atalho de conexão a fonte de dados (útil para times) | Não | Sim |
| `.pbiviz` | Visual customizado empacotado | Não | Binário |
| `.rdl` | Relatório paginado (Report Builder) | Não | Sim (XML) |
| `.mez` | Conector personalizado (M) | Não | Binário |
| `.abf` | Backup do modelo tabular (via XMLA) | Sim | Não |

**Regra profissional:** projeto sério vive em **PBIP + TMDL**, versionado em Git.
`.pbix` é o formato de trabalho individual e de entrega rápida. Ver
[`25-ciclo-de-vida-e-devops.md`](25-ciclo-de-vida-e-devops.md).

---

## 4. Power Query — por tarefa

### 4.1 Conectar

| Quero… | Caminho |
|---|---|
| Um arquivo | Obter dados → Texto/CSV · Excel · XML · JSON · PDF · Parquet |
| **Uma pasta inteira de arquivos iguais** | Obter dados → **Pasta** → Combinar e Transformar ★ |
| Um banco | Obter dados → SQL Server · PostgreSQL · Oracle · MySQL · Snowflake · Databricks… |
| Uma API REST | Obter dados → **Web** (ou `Web.Contents` no editor avançado) |
| SharePoint | Obter dados → SharePoint Folder · SharePoint List |
| Outro modelo do Power BI | Obter dados → **Modelos semânticos do Power BI** (conexão dinâmica) |
| Um lakehouse do Fabric | Obter dados → OneLake data hub |
| Dataverse / Dynamics | Obter dados → Dataverse |

### 4.2 Limpar

| Quero… | Onde |
|---|---|
| Promover a primeira linha a cabeçalho | Transformar → **Usar Primeira Linha como Cabeçalho** |
| Remover linhas vazias / duplicadas | Página Inicial → Remover Linhas |
| Filtrar linhas | Seta no cabeçalho da coluna |
| Trocar valores | Transformar → **Substituir Valores** |
| Separar uma coluna | Transformar → **Dividir Coluna** (por delimitador, posição, maiúsculas…) |
| Juntar colunas | Adicionar Coluna → **Mesclar Colunas** |
| Extrair parte do texto | Adicionar Coluna → Extrair (primeiros/últimos N, entre delimitadores) |
| Corrigir tipo com localidade | Botão direito no cabeçalho → **Alterar Tipo → Usando Localidade** ★ |
| Preencher para baixo (células mescladas do Excel) | Transformar → **Preencher → Abaixo** ★ |
| Aparar espaços / limpar caracteres invisíveis | Transformar → Formatar → Cortar / Limpar |

### 4.3 Reestruturar

| Quero… | Onde | Cuidado |
|---|---|---|
| Transformar colunas em linhas (**despivotar**) | Selecionar colunas → Transformar → **Despivotar Colunas** ★★ | Use **"Despivotar Outras Colunas"** para o resultado não quebrar quando surgirem colunas novas |
| Transformar linhas em colunas (**pivotar**) | Transformar → Coluna Dinâmica | Raramente é o que se quer num modelo |
| Juntar tabelas lado a lado (`JOIN`) | Página Inicial → **Mesclar Consultas** | Tipo de junção importa; ver abaixo |
| Empilhar tabelas (`UNION`) | Página Inicial → **Acrescentar Consultas** | As colunas precisam ter o mesmo nome |
| Agrupar e agregar (`GROUP BY`) | Transformar → **Agrupar Por** | |
| Transpor | Transformar → Transpor | |

**Tipos de mesclagem** (equivalência com SQL):

| Power Query | SQL | Resultado |
|---|---|---|
| Externa Esquerda | `LEFT JOIN` | Todas da 1ª, correspondentes da 2ª |
| Externa Direita | `RIGHT JOIN` | Todas da 2ª |
| Externa Completa | `FULL OUTER JOIN` | Todas de ambas |
| Interna | `INNER JOIN` | Só as correspondentes |
| Anti Esquerda | `LEFT ... WHERE b IS NULL` | Só as da 1ª **sem** par ★ auditoria |
| Anti Direita | idem invertido | Só as da 2ª sem par ★ auditoria |

> **Truque de auditoria:** *Anti Esquerda* responde na hora "quais vendas têm um produto
> que não existe no cadastro?". Faça isso **sempre** antes de confiar num relacionamento.

### 4.4 Parametrizar e organizar

| Quero… | Onde |
|---|---|
| Um parâmetro (servidor, ano, caminho) | Página Inicial → **Gerenciar Parâmetros** ★ |
| Uma função reutilizável | Botão direito na consulta → **Criar Função** |
| Organizar as consultas | Botão direito → Mover para Grupo (pastas) |
| Não carregar uma consulta auxiliar no modelo | Botão direito → desmarcar **Habilitar carga** ★ |
| Ver a receita como código | Página Inicial → **Editor Avançado** |
| Ver as dependências | Exibição → **Dependências da Consulta** |

### 4.5 Query folding — a coisa mais importante do Power Query

> **Query folding** (dobramento de consulta) é a capacidade do Power Query de **traduzir
> suas etapas em uma única consulta nativa** (SQL, por exemplo) executada na fonte, em vez
> de baixar tudo e processar localmente.

**Como verificar:** botão direito numa etapa → **Exibir Consulta Nativa**
(*View Native Query*). Se estiver habilitado, a etapa dobra. Se estiver cinza, ali o
dobramento **parou** e tudo dali para baixo roda na sua máquina.

**Quebram o folding** (regra geral): `Table.Buffer`, adicionar índice, colunas
personalizadas com funções M sem equivalente SQL, mesclar com fonte de outro tipo,
`Table.AddColumn` com lógica complexa.

**Prática:** faça **primeiro** tudo o que dobra (filtro, remoção de coluna, tipo,
agrupamento), e **por último** o que não dobra. Detalhes em
[`13-power-query-e-m.md`](13-power-query-e-m.md).

---

## 5. Linguagem M — funções essenciais

M é *case-sensitive*, funcional e tem tipos. `each` é açúcar para `(_) =>`.

| Categoria | Função | Uso |
|---|---|---|
| Fonte | `Csv.Document`, `Excel.Workbook`, `Sql.Database`, `Web.Contents`, `Folder.Files`, `Json.Document` | Ler dados |
| Tabela | `Table.SelectRows(t, each [Col] > 10)` | Filtrar |
| | `Table.SelectColumns` / `Table.RemoveColumns` | Escolher colunas |
| | `Table.RenameColumns(t, {{"a","b"}})` | Renomear |
| | `Table.TransformColumnTypes(t, {{"Data", type date}})` | Tipar |
| | `Table.AddColumn(t, "Novo", each [a]*[b], type number)` | Coluna nova **com tipo** ★ |
| | `Table.Group(t, {"Chave"}, {{"Total", each List.Sum([Valor]), type number}})` | Agrupar |
| | `Table.NestedJoin` + `Table.ExpandTableColumn` | Mesclar |
| | `Table.Combine({t1, t2})` | Empilhar |
| | `Table.UnpivotOtherColumns(t, {"Chave"}, "Atributo", "Valor")` | Despivotar ★ |
| | `Table.Distinct`, `Table.Sort`, `Table.FirstN` | Óbvias |
| | `Table.Buffer(t)` | Materializa em memória — **quebra folding**, use com parcimônia |
| Texto | `Text.Trim`, `Text.Clean`, `Text.Upper`, `Text.Proper` | Normalizar |
| | `Text.BetweenDelimiters(s, "(", ")")` | Extrair |
| | `Text.Split(s, ";")` | Dividir |
| | `Text.PadStart(s, 5, "0")` | Zeros à esquerda |
| Data | `Date.From`, `Date.Year`, `Date.StartOfMonth`, `Date.AddDays` | Datas |
| | `Date.FromText(s, [Format="dd/MM/yyyy", Culture="pt-BR"])` | Conversão explícita ★ |
| Lista | `List.Sum`, `List.Max`, `List.Distinct`, `List.Contains` | Agregação |
| | `List.Dates(inicio, contagem, duracao)` | Gerar calendário em M |
| Erro | `try ... otherwise 0` | Tratamento de erro ★ |
| Valor | `Value.NativeQuery(fonte, "SELECT ...")` | SQL cru na fonte |

**Padrão de tratamento de erro que uso sempre:**

```powerquery
= Table.AddColumn(
    Origem,
    "ValorNumerico",
    each try Number.From([ValorTexto]) otherwise null,
    type nullable number
)
```

*Converte texto em número; onde falhar, devolve `null` em vez de derrubar a atualização
inteira. `null` é visível e auditável; um erro no meio da carga não é.*

---

## 6. DAX — por tarefa

Referência de bolso. A explicação **conceitual** está em
[`15`](15-dax-fundamentos.md), [`16`](16-dax-contexto-de-avaliacao.md) e
[`17`](17-dax-inteligencia-de-tempo.md).

### 6.1 Agregar

| Quero | Função | Nota |
|---|---|---|
| Somar uma coluna | `SUM( T[C] )` | |
| Somar uma expressão linha a linha | `SUMX( T, T[a] * T[b] )` | Iterador — cria contexto de linha |
| Média / mínimo / máximo | `AVERAGE`, `MIN`, `MAX` (+ variantes `X`) | |
| Contar linhas | `COUNTROWS( T )` | Preferir a `COUNT` |
| Contar valores distintos | `DISTINCTCOUNT( T[C] )` | Caro em colunas de alta cardinalidade |
| Contar não-vazios | `COUNT( T[C] )` | Ignora `BLANK` |
| Dividir com segurança | `DIVIDE( n, d [, alt] )` ★ | Nunca use `/` em medida |
| Primeiro/último valor | `FIRSTNONBLANK`, `LASTNONBLANK` | Semântica sutil |

### 6.2 Filtrar e modificar contexto

| Quero | Padrão |
|---|---|
| Calcular com um filtro extra | `CALCULATE( [M], T[C] = "X" )` |
| Filtro complexo | `CALCULATE( [M], FILTER( T, T[a] > T[b] ) )` |
| Remover todos os filtros | `CALCULATE( [M], ALL( T ) )` |
| Remover filtros de uma coluna só | `CALCULATE( [M], ALL( T[C] ) )` |
| Remover, mas manter os do visual | `ALLSELECTED( T )` ★ para % do total visível |
| Remover ignorando os filtros de linha da matriz | `ALLEXCEPT( T, T[Chave] )` |
| Manter só o que já estava | `KEEPFILTERS( T[C] = "X" )` |
| Filtrar por outra tabela | `TREATAS( { "A", "B" }, T[C] )` |
| Testar se há filtro | `ISFILTERED( T[C] )`, `HASONEVALUE( T[C] )`, `ISINSCOPE( T[C] )` |
| Ler o valor selecionado | `SELECTEDVALUE( T[C], "padrão" )` ★ |

**A regra de `CALCULATE` em uma frase:** ele **substitui** o filtro existente na mesma
coluna (a menos que você use `KEEPFILTERS`), e faz **transição de contexto** quando
avaliado dentro de um contexto de linha. Se essa frase não faz sentido ainda, leia
[`16-dax-contexto-de-avaliacao.md`](16-dax-contexto-de-avaliacao.md) — é *o* capítulo.

### 6.3 Inteligência de tempo

Exigem tabela de datas contínua e **marcada como tabela de data**.

| Quero | Função |
|---|---|
| Acumulado no ano | `TOTALYTD( [M], dCal[Date] )` ou `CALCULATE( [M], DATESYTD( dCal[Date] ) )` |
| Acumulado no trimestre/mês | `TOTALQTD`, `TOTALMTD` |
| Mesmo período do ano anterior | `CALCULATE( [M], SAMEPERIODLASTYEAR( dCal[Date] ) )` |
| Deslocar N períodos | `CALCULATE( [M], DATEADD( dCal[Date], -1, MONTH ) )` |
| Período anterior genérico | `PREVIOUSMONTH`, `PREVIOUSYEAR`, `PREVIOUSQUARTER` |
| Últimos 12 meses (MAT) | `CALCULATE( [M], DATESINPERIOD( dCal[Date], MAX(dCal[Date]), -12, MONTH ) )` |
| Do início até aqui | `CALCULATE( [M], DATESBETWEEN( dCal[Date], BLANK(), MAX(dCal[Date]) ) )` |
| Saldo em estoque (último valor do período) | `CLOSINGBALANCEMONTH( [M], dCal[Date] )` |
| **Calendário fiscal / 4-4-5** | Não use as funções acima — use colunas de índice. Ver [`17`](17-dax-inteligencia-de-tempo.md) §6 |

### 6.4 Relacionar e navegar

| Quero | Função |
|---|---|
| Buscar valor pela relação (lado 1) | `RELATED( dProduto[Categoria] )` |
| Tabela relacionada (lado *) | `RELATEDTABLE( fVendas )` |
| Ativar uma relação inativa | `CALCULATE( [M], USERELATIONSHIP( fV[DataEnvio], dCal[Date] ) )` ★ |
| Cruzar sem relação | `TREATAS` ou `CROSSFILTER` |
| Mudar direção do filtro pontualmente | `CROSSFILTER( T1[C], T2[C], BOTH )` |

### 6.5 Tabelas e variáveis

| Quero | Padrão |
|---|---|
| Guardar um resultado intermediário | `VAR X = ... RETURN ...` ★ **sempre** |
| Tabela virtual filtrada | `VAR T = FILTER( ALL(dProd), dProd[Custo] > 100 )` |
| Sumarizar | `SUMMARIZE( T, T[C], "Total", [M] )` — prefira `SUMMARIZECOLUMNS` |
| Tabela de valores | `VALUES( T[C] )`, `DISTINCT( T[C] )` |
| Top N | `TOPN( 10, T, [M], DESC )` |
| Ranking | `RANKX( ALL( dProd[Produto] ), [M], , DESC, DENSE )` |
| Gerar tabela | `CALENDAR`, `CALENDARAUTO`, `GENERATESERIES`, `ROW`, `DATATABLE` |
| União/interseção | `UNION`, `INTERSECT`, `EXCEPT`, `NATURALINNERJOIN` |
| **Função definida pelo usuário (UDF)** | `DEFINE FUNCTION` — recurso recente, ver [`65`](65-estado-da-arte.md) |

> **`VAR` não é opcional.** Além de deixar legível, `VAR` avalia **uma vez** no contexto em
> que foi declarada. Isso muda o resultado, não só o desempenho. É o erro sutil mais comum
> em DAX intermediário.

### 6.6 Lógica e texto

| Quero | Função |
|---|---|
| Condicional | `IF( cond, v, f )` · `SWITCH( TRUE(), c1, v1, c2, v2, padrão )` ★ |
| Tratar vazio | `COALESCE( a, b, 0 )` · `IF( ISBLANK(x), 0, x )` |
| Concatenar | `a & b` · `CONCATENATEX( T, T[C], ", " )` |
| Formatar | `FORMAT( v, "#,##0.00" )` — **cuidado: devolve texto** |
| Data em texto | `FORMAT( d, "MMM/yyyy", "pt-BR" )` |
| Comparar textos | `EXACT`, `CONTAINSSTRING`, `SEARCH`, `FIND` |

### 6.7 Cálculos visuais (*visual calculations*)

Recurso relativamente novo: DAX escrito **dentro do visual**, operando sobre a matriz já
calculada — resolve com uma linha coisas que exigiam contorções.

```dax
-- na guia do visual: Nova cálculo visual
Diferença = [Faturamento] - PREVIOUS( [Faturamento] )
% do Total = DIVIDE( [Faturamento], COLLAPSEALL( [Faturamento], ROWS ) )
Acumulado = RUNNINGSUM( [Faturamento] )
```

Funções disponíveis incluem `PREVIOUS`, `NEXT`, `FIRST`, `LAST`, `RUNNINGSUM`,
`MOVINGAVERAGE`, `RANGE`, `COLLAPSE`, `COLLAPSEALL`, `EXPAND`, `LOOKUP`.

**Novidade de julho/2026:** `LOOKUP` aceita o parâmetro opcional
`AssociatedColumnsBehavior` com valores `EXPLICIT` (padrão) e `INFERRED`; com `INFERRED`,
o motor deduz quais colunas de eixo são funcionalmente determinadas pelas coordenadas
fornecidas.

**Limitação:** cálculo visual vive no visual. Não é reutilizável nem consultável de fora.
Use para o "último quilômetro" de apresentação, não para regra de negócio.

---

## 7. Visuais nativos — quando usar cada um

| Visual | Use quando | **Não** use quando |
|---|---|---|
| **Cartão** / Cartão novo | Um KPI isolado | Precisa de contexto (ponha uma comparação) |
| **Barras / Colunas** | Comparar categorias ★ o mais confiável | Mais de ~15 categorias sem ordenação |
| **Linhas** | Evolução no tempo ★ | Categorias não ordenáveis |
| **Área / Área empilhada** | Composição ao longo do tempo | Mais de 3–4 séries (vira ilegível) |
| **Combinado (linhas e colunas)** | Duas grandezas de escalas diferentes | Quando induz correlação falsa |
| **Pizza / Rosca** | Nunca, quase | Mais de 3 fatias — use barras. Ver [`18`](18-visualizacao.md) |
| **Funil** | Etapas de um processo com perda | Categorias sem ordem natural |
| **Medidor** (*gauge*) | Progresso contra meta única | Ocupa muito espaço para pouca informação |
| **Mapa / Mapa Azure / Coroplético** | Geografia importa de verdade | Só porque "tem estado na tabela" |
| **Matriz** | Números precisos, várias dimensões ★ subestimada | Quando a pergunta é sobre padrão, não valor |
| **Tabela** | Detalhe, exportação | Como página principal |
| **Dispersão (scatter)** | Correlação entre duas medidas | Poucos pontos |
| **Cascata** (*waterfall*) | Explicar variação (ponte) ★ | Séries longas |
| **Treemap** | Proporção com muitas categorias | Comparação precisa |
| **Segmentação** | Filtro pelo usuário | Muitos valores sem busca |
| **Segmentação de botões** | Poucas opções, visual limpo | — |
| **Principais Influenciadores** | Explorar drivers ★ | Como prova causal — **não é** |
| **Árvore de Decomposição** | Análise exploratória guiada ★ | Relatório operacional fixo |
| **Perguntas e Respostas (Q&A)** | Público exploratório | Modelo mal nomeado (vai errar) |
| **Narrativa inteligente** | Resumo textual automático | Quando o texto precisa ser preciso |
| **Visuais de terceiros (AppSource)** | Necessidade específica real | Sem avaliar segurança e suporte |

**Novidade de julho/2026:** formatação condicional passou a valer também para **gráficos
de linha e para visuais com legenda** (barras, colunas, pizza, rosca), inclusive com cor
definida por uma única medida DAX — útil para manter a mesma cor de série em todo o
relatório.

---

## 8. Formatação de números e datas

Códigos de formato personalizados (**Ferramentas de Medida → Formato → Personalizado**):

| Código | Resultado para `1234567.891` |
|---|---|
| `#,##0` | `1.234.568` |
| `#,##0.00` | `1.234.567,89` |
| `R$ #,##0.00` | `R$ 1.234.567,89` |
| `#,##0,,"M"` | `1M` (cada vírgula final divide por mil) ★ |
| `#,##0,"k"` | `1.235k` |
| `0.0%` | (para `0.1234`) `12,3%` |
| `#,##0;(#,##0);"—"` | positivo; negativo entre parênteses; zero como travessão ★ |
| `+#,##0;-#,##0;0` | sinal explícito |

Datas (`FORMAT`):

| Código | Resultado |
|---|---|
| `dd/MM/yyyy` | `14/08/2026` |
| `MMM/yy` | `ago/26` (com cultura `"pt-BR"`) |
| `yyyy-MM` | `2026-08` ★ ordena como texto |
| `dddd` | `sexta-feira` |
| `Q` | `3` (trimestre) |

> **Alerta:** `FORMAT` devolve **texto**. Um eixo formatado com `FORMAT` ordena
> alfabeticamente e não faz aritmética. Formate na **propriedade de formato da medida**
> sempre que possível, e reserve `FORMAT` para rótulos.

**Cadeias de formato dinâmicas:** desde 2023 é possível dar a uma medida uma expressão de
formato que muda conforme o contexto (moeda por país, por exemplo) —
**Ferramentas de Medida → Formato → Dinâmico**.

---

## 9. Power BI Service — operações

### 9.1 Objetos

| Objeto | O que é |
|---|---|
| **Workspace** | Pasta colaborativa. Contém tudo. Tem funções: Admin, Membro, Colaborador, Visualizador |
| **Modelo semântico** (*semantic model*) | Antigo "conjunto de dados" (*dataset*): dados + relações + medidas |
| **Relatório** | Páginas e visuais sobre um modelo semântico |
| **Painel** (*dashboard*) | Mural de blocos fixados de vários relatórios (recurso legado; ver §12) |
| **Aplicativo organizacional** (*org app*) | Empacotamento para distribuição, com **audiências** distintas |
| **Fluxo de dados** (*dataflow* Gen1/Gen2) | Power Query na nuvem, reutilizável |
| **Datamart** | Modelo + SQL gerenciado (substituído na prática pelo Fabric Warehouse) |
| **Métrica / Scorecard** | Metas e acompanhamento |
| **Pipeline de implantação** | Dev → Teste → Produção |

### 9.2 Funções de workspace

| Função | Ver | Editar conteúdo | Publicar app | Gerenciar acesso |
|---|---|---|---|---|
| Visualizador | ✔ | ✘ | ✘ | ✘ |
| Colaborador | ✔ | ✔ | ✘ | ✘ |
| Membro | ✔ | ✔ | ✔ | parcial |
| Administrador | ✔ | ✔ | ✔ | ✔ |

### 9.3 Atualização de dados

| Tarefa | Onde |
|---|---|
| Atualizar agora | Modelo semântico → ⋯ → Atualizar agora |
| Agendar | Configurações do modelo → **Atualizar** → até **8×/dia** (Pro) ou **48×/dia** (PPU/capacidade) |
| Credenciais da fonte | Configurações → **Credenciais da fonte de dados** |
| Gateway | Configurações → **Conexão do gateway** |
| Atualização incremental | Definida no **Desktop** (parâmetros `RangeStart`/`RangeEnd`), aplicada no Service |
| Ver histórico e falhas | Configurações → Atualizar → **Histórico de atualização** ★ |
| Atualizar por API/XMLA | §10 |

### 9.4 Compartilhamento — as cinco formas, e o que cada uma custa

| Forma | Quem vê | Licença necessária |
|---|---|---|
| Compartilhar item direto | Pessoas específicas | Pro (você **e** eles) — ou capacidade F64+ |
| Workspace | Membros do workspace | Idem |
| **Aplicativo organizacional** | Audiências definidas ★ recomendado | Idem |
| **Publicar na Web** | **Qualquer pessoa na internet, sem login** ☠ | Nenhuma |
| Incorporar no Teams/SharePoint | Quem tem acesso ao item | Idem ao item |

> ☠ **"Publicar na Web" torna o relatório público e indexável por buscadores.** É a maior
> fonte de vazamento de dados corporativos com Power BI. Administradores devem **desligar**
> essa configuração de locatário por padrão. Ver
> [`24-seguranca-e-governanca.md`](24-seguranca-e-governanca.md).

### 9.5 Exportar

| Formato | De onde | Limite típico |
|---|---|---|
| PDF / PowerPoint | Relatório → Exportar | Layout fixo |
| Excel (dados resumidos) | Visual → ⋯ → Exportar dados | 150.000 linhas |
| Excel (dados subjacentes) | Idem, se permitido | 150.000 linhas |
| `.csv` | Visual → Exportar | 30.000 linhas (Service) |
| **Analisar no Excel** | Modelo semântico → ⋯ | Tabela dinâmica ao vivo ★ |
| Assinatura por e-mail | Relatório → Assinar | PDF/imagem agendado |

*Limites mudam; confira a documentação vigente antes de prometer a alguém.*

---

## 10. Linha de comando, PowerShell e APIs

### 10.1 Módulo PowerShell oficial

```powershell
Install-Module -Name MicrosoftPowerBIMgmt -Scope CurrentUser
Connect-PowerBIServiceAccount

Get-PowerBIWorkspace -Scope Organization -All          # listar workspaces
Get-PowerBIDataset  -WorkspaceId $id                    # listar modelos
Invoke-PowerBIRestMethod -Url "datasets/$dsId/refreshes" -Method Post   # disparar atualização
New-PowerBIReport -Path .\rel.pbix -WorkspaceId $id -ConflictAction CreateOrOverwrite
```

### 10.2 API REST (Fabric/Power BI)

Base: `https://api.powerbi.com/v1.0/myorg/` e `https://api.fabric.microsoft.com/v1/`.

| Tarefa | Endpoint |
|---|---|
| Listar workspaces | `GET /groups` |
| Listar modelos | `GET /groups/{id}/datasets` |
| Disparar atualização | `POST /groups/{id}/datasets/{dsId}/refreshes` |
| Status da atualização | `GET /groups/{id}/datasets/{dsId}/refreshes` |
| Publicar `.pbix` | `POST /groups/{id}/imports` |
| Exportar relatório | `POST /reports/{id}/ExportTo` |
| Metadados do locatário (scanner) | `POST /admin/workspaces/getInfo` ★ inventário |
| **CRUD de org apps e audiências** | Fabric REST — **novidade de julho/2026** |
| **CRUD de relatórios paginados** | Fabric REST — **novidade de julho/2026** |

### 10.3 XMLA endpoint

Permite tratar o modelo semântico publicado como um banco Analysis Services: conectar com
SSMS, DAX Studio, Tabular Editor, `pyadomd`; fazer *refresh* parcial de tabela ou partição;
fazer *backup*/*restore*.

```
powerbi://api.powerbi.com/v1.0/myorg/<NomeDoWorkspace>
```

**Requer capacidade** (PPU ou F-SKU) com *XMLA endpoint* em **Leitura/Gravação**.
É o que viabiliza o CI/CD sério — ver [`25`](25-ciclo-de-vida-e-devops.md).

### 10.4 Python (semantic link / SemPy)

Dentro de notebooks do Fabric:

```python
import sempy.fabric as fabric

fabric.list_workspaces()
fabric.list_datasets(workspace="Vendas")
df = fabric.evaluate_dax("Vendas", "EVALUATE SUMMARIZECOLUMNS(dCalendario[Ano], \"Fat\", [Faturamento Total])")
fabric.refresh_dataset("Vendas", refresh_type="full")
```

---

## 11. Ferramentas externas

| Ferramenta | Grátis? | Para quê | Onde entra no curso |
|---|---|---|---|
| **DAX Studio** | ✔ OSS | Consultas DAX, tempos, plano de consulta, VertiPaq Analyzer, exportação | [`22`](22-desempenho.md) |
| **Tabular Editor 2** | ✔ OSS | Edição em massa do modelo, Best Practice Analyzer, scripts C# | [`25`](25-ciclo-de-vida-e-devops.md) |
| **Tabular Editor 3** | ✘ pago | Idem, com IDE, depurador DAX, comparação | [`80`](80-custos-e-licencas.md) |
| **Bravo for Power BI** | ✔ | Analisar modelo, formatar DAX, gerar tabela de datas | [`17`](17-dax-inteligencia-de-tempo.md) |
| **ALM Toolkit** | ✔ | Comparar e mesclar modelos | [`25`](25-ciclo-de-vida-e-devops.md) |
| **DAX Formatter** (web) | ✔ | Formatar DAX (sqlbi.com) | — |
| **PBI Explorer / Power BI Helper** | ✔ | Diff de relatórios, documentação | [`25`](25-ciclo-de-vida-e-devops.md) |
| **Measure Killer** | freemium | Achar medidas e colunas não usadas | [`22`](22-desempenho.md) |
| **VS Code + extensões TMDL/DAX** | ✔ | Editar PBIP como código | [`25`](25-ciclo-de-vida-e-devops.md) |

---

## 12. Obsoleto — o que não usar mais

| Obsoleto / legado | Substituto | Desde |
|---|---|---|
| Power BI Desktop **32 bits** | 64 bits | Descontinuado em jan/2024 |
| Instalador `.msi` | `.exe` ou Microsoft Store | — |
| Termo "**conjunto de dados**" (*dataset*) | **modelo semântico** (*semantic model*) | Renomeado em 2023 |
| Termo "**fluxo de dados** Gen1" | Dataflow Gen2 (no Fabric) | 2023 |
| **Painéis** (*dashboards*) como principal entrega | Relatórios + **org apps com audiências** | Prática atual |
| Capacidades **P-SKU** (Premium) | **F-SKU** do Fabric | Transição concluída |
| "Aplicativos de workspace" clássicos | **Org apps** com audiências (GA em julho/2026) | 2025–2026 |
| Internet Explorer | Microsoft Edge | — |
| `POWER BI EMBEDDED A-SKU` para novos projetos | F-SKU | — |
| Visual "Cartão" antigo | **Novo cartão** (com múltiplos valores e formatação condicional melhor) | 2024 |
| Segmentação clássica de lista | **Segmentação de botões** (mais flexível) | 2024–2025 |
| `ADDCOLUMNS`+`SUMMARIZE` para agregar | `SUMMARIZECOLUMNS` | Prática desde ~2016 |
| `EARLIER()` | `VAR` | Prática desde ~2016 ★ |
| Seletor de arquivos antigo do OneDrive/SharePoint | Novo seletor | **Desativado em out/2026** para builds ≤ mar/2026 |
| Baixar `.pbix` de um modelo semântico esperando o relatório junto | Baixe do **relatório** | Mudou em julho/2026 |

> **Sobre `EARLIER()`:** ainda funciona, e você vai encontrá-la em código antigo. Não a
> escreva mais. `VAR` faz o mesmo com clareza. Se você **precisa** entender `EARLIER`,
> é porque está lendo código de 2015 — ver [`16`](16-dax-contexto-de-avaliacao.md) §8.

---

## 13. Os atalhos que só quem usa há anos conhece

Não estão em tutorial nenhum. Valem o preço do curso.

1. **`Ctrl+C`/`Ctrl+V` de visual entre dois `.pbix` abertos.** Copia o visual com toda a
   formatação. Se os campos existirem no destino, ele já vem funcionando. Economiza horas.

2. **Painel de Seleção + agrupar (`Ctrl+G`).** Agrupe os visuais de um "estado" e
   mostre/oculte o grupo inteiro com um indicador. É como se fazem relatórios com
   navegação sem 40 páginas.

3. **`Alt` enquanto arrasta** desliga o alinhamento à grade. Único jeito de posicionar
   visuais com precisão.

4. **Botão "Pausar visuais"** (guia Otimizar). Ao trabalhar num modelo lento, congela a
   renderização enquanto você faz 10 alterações, e só então atualiza. Poupa minutos por
   ciclo.

5. **Analisador de Desempenho → "Copiar consulta"**. Dá a consulta DAX exata que o visual
   dispara. Cole no DAX Studio e você tem o problema isolado. Este é *o* fluxo de
   diagnóstico — ver [`22`](22-desempenho.md).

6. **Grupos de cálculo** (Tabular Editor). Em vez de criar `Vendas YTD`, `Margem YTD`,
   `Custo YTD`… crie **um** grupo de cálculo com o item "YTD" que se aplica a qualquer
   medida. Reduz modelos de 300 medidas para 40. Ver [`17`](17-dax-inteligencia-de-tempo.md) §7.

7. **Parâmetros de campo** (*field parameters*). Deixa o **usuário escolher** qual dimensão
   ou qual medida o gráfico mostra, sem indicadores nem visuais duplicados.
   **Modelagem → Novo parâmetro → Campos**.

8. **`SELECTEDVALUE` com valor padrão** para títulos dinâmicos:
   `"Vendas de " & SELECTEDVALUE( dEstado[UF], "todos os estados" )`, ligado ao título do
   visual por formatação condicional (`fx`).

9. **Pastas de exibição** (*display folders*) nas propriedades do campo. Um modelo com 80
   medidas fica utilizável quando elas estão em pastas por assunto.

10. **`Ctrl+Shift+M` no editor DAX**: formata a expressão inteira. Código DAX formatado é a
    diferença entre uma medida legível e um pesadelo de uma linha só.

11. **Consulta DAX (DAX query view) com `DEFINE MEASURE`**: teste uma medida nova sem
    tocar no modelo, e só depois clique em **Atualizar modelo com alterações**. Desde
    julho/2026, comentários `///` acima do `MEASURE` viram **descrição** da medida.

12. **`.pbids`**: um arquivinho JSON que abre o Desktop já apontando para a fonte certa.
    Distribua para o time e ninguém mais digita nome de servidor errado.

---

## 14. Autoteste

1. Onde você verifica se uma etapa do Power Query faz *query folding*, e o que fazer com a resposta?
2. Qual a diferença prática entre `.pbix`, `.pbit` e `.pbip`? Qual vai para o Git?
3. Quando usar `ALL`, `ALLSELECTED` e `ALLEXCEPT`?
4. Por que `DIVIDE` em vez de `/`? E por que `VAR` não é só estética?
5. Que transformação do Power Query você usa para uma planilha com um mês por coluna, e
   qual variante evita quebrar quando surgir um mês novo?
6. Cite três formas de compartilhar no Service e a que nunca deveria estar habilitada.
7. O que o endpoint XMLA permite fazer que a interface não permite?
8. Cite três coisas obsoletas nesta lista e o que as substituiu.
9. Descreva o fluxo "Analisador de Desempenho → DAX Studio" em uma frase.
10. Para que servem parâmetros de campo, e qual problema de indicadores eles eliminam?

---

*Fontes consultadas em 14/08/2026: [Microsoft Learn — What's new (julho/2026)](https://learn.microsoft.com/en-us/power-bi/fundamentals/whats-new) (cálculos visuais `LOOKUP INFERRED`, comentários `///`, formatação condicional em linhas e legendas, org apps com audiências, TMDL na web, CRUD APIs); [Microsoft Learn — Power BI keyboard shortcuts](https://learn.microsoft.com/en-us/power-bi/create-reports/desktop-accessibility-keyboard-shortcuts); [Microsoft Learn — Power BI REST APIs](https://learn.microsoft.com/en-us/rest/api/power-bi/).*
