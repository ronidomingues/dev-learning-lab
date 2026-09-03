# 13 · Power Query e a linguagem M

**Nível:** intermediário
**Data:** 14/08/2026

Power Query é onde 60% do trabalho acontece e 5% da atenção é dada. Este capítulo trata
do que separa uma consulta que funciona de uma que continua funcionando daqui a dois anos.

---

## 1. O que é, em uma frase

> **Power Query** é um motor de ETL (*Extract, Transform, Load* — extrair, transformar,
> carregar) baseado numa linguagem funcional chamada **M**, em que cada transformação vira
> um passo gravado e reexecutável.

A palavra-chave é **reexecutável**. Você não corrige os dados — você **descreve como
corrigi-los**, e a descrição roda de novo a cada atualização, para sempre.

---

## 2. A linguagem M

### 2.1 Fatos que economizam horas

1. **M é *case-sensitive*.** `Table.SelectRows` funciona; `table.selectrows` não.
   Nomes de coluna também: `[Data]` ≠ `[data]`.
2. **M é funcional e imutável.** Não existe variável que muda; cada passo cria um valor
   novo. `let ... in ...` é uma lista de definições, não uma sequência de comandos.
3. **A ordem dos passos no `let` não define a ordem de execução.** A avaliação é
   **preguiçosa** (*lazy*) e guiada por dependência: o M calcula o que o `in` pede, e só
   isso.
4. **M é tipado.** `type text`, `Int64.Type`, `type nullable number`, `type table [...]`.
   Ignorar tipos é a origem de metade dos erros de carga.
5. **`each` é açúcar sintático para `(_) =>`.** `each [Valor] > 10` é
   `(_) => _[Valor] > 10`.

### 2.2 Anatomia de uma consulta

```powerquery
let
    // cada linha define um NOME = uma EXPRESSÃO
    Origem      = Sql.Database("srv", "vendas"),
    Tabela      = Origem{[Schema="dbo", Item="NotaFiscalItem"]}[Data],
    Filtrada    = Table.SelectRows(Tabela, each [Ano] >= 2024),
    Reduzida    = Table.SelectColumns(Filtrada, {"NF","Data","SKU","Qtd","Valor"}),
    Tipada      = Table.TransformColumnTypes(
                      Reduzida,
                      {{"Data", type date}, {"Qtd", Int64.Type}, {"Valor", type number}}
                  )
in
    Tipada    // ← o que a consulta devolve
```

Cada nome vira um item em **Etapas Aplicadas**. Renomear passos para algo legível é
documentação gratuita — e o M aceita nomes com espaço entre `#"aspas"`.

### 2.3 Os tipos de valor

| Tipo | Literal | Observação |
|---|---|---|
| `null` | `null` | Ausência de valor |
| `logical` | `true`, `false` | |
| `number` | `1`, `1.5`, `2.5e3` | Ponto flutuante; `Int64.Type` é subtipo |
| `text` | `"abc"` | Aspas duplas sempre |
| `date` / `time` / `datetime` / `datetimezone` / `duration` | `#date(2026,8,14)` | |
| `binary` | `File.Contents(...)` | |
| `list` | `{1, 2, 3}` | Chaves |
| `record` | `[a = 1, b = "x"]` | Colchetes |
| `table` | `#table(...)` | |
| `function` | `(x) => x * 2` | |

**A confusão nº 1:** `{ }` é lista, `[ ]` é registro, `( )` é chamada de função ou
agrupamento. No Excel e no DAX é tudo diferente. Erre uma vez e você não erra mais.

---

## 3. Query folding — a coisa mais importante deste capítulo

> **Query folding** (dobramento) — a capacidade do Power Query de traduzir seus passos em
> **uma única consulta nativa** executada pela fonte.

### 3.1 Por que importa tanto

Sem folding, para filtrar 2024 numa tabela de 400 milhões de linhas, o Power Query
**baixa as 400 milhões** e filtra na sua máquina. Com folding, ele envia:

```sql
SELECT NF, Data, SKU, Qtd, Valor FROM dbo.NotaFiscalItem WHERE Ano >= 2024
```

e recebe 40 milhões. A diferença entre 6 horas e 4 minutos — número real, do
[`06-exemplos.md`](06-exemplos.md) §14.

### 3.2 Como verificar

Botão direito na **última** etapa → **Exibir Consulta Nativa** (*View Native Query*).

| Resultado | Significado |
|---|---|
| Mostra SQL | Tudo dobrou até aqui ✔ |
| Opção cinza/desabilitada | O dobramento **parou** em algum passo anterior |

**Método para achar onde parou:** clique em cada etapa, de baixo para cima, até a opção
voltar a ficar habilitada. O passo seguinte àquele é o culpado.

Nas versões recentes há também o **indicador de dobramento** no painel de etapas:
ícones diferentes para "dobra", "pode dobrar", "não dobra".

### 3.3 O que dobra e o que não dobra

| Dobra (quase sempre) | Não dobra |
|---|---|
| Filtrar linhas | `Table.Buffer` |
| Remover/selecionar colunas | Adicionar coluna de índice |
| Renomear colunas | Coluna personalizada com função M sem equivalente SQL |
| Alterar tipo | Mesclar com fonte de outro tipo |
| Agrupar por | `Table.FromList` sobre resultado de API |
| Mesclar consultas da **mesma** fonte | Funções de texto exóticas (`Text.Proper` depende do provedor) |
| Acrescentar consultas da mesma fonte | Colunas condicionais complexas |
| Ordenar | Muitos conectores de arquivo (CSV/Excel não dobram — não há "fonte" para dobrar) |
| Remover duplicatas | `List.Generate` |

### 3.4 A regra de ouro

> **Ordene os passos: primeiro o que dobra, por último o que não dobra.**

Errado:

```powerquery
Origem      → Adicionar Índice → Filtrar Ano >= 2024 → Remover colunas
              ↑ quebra aqui       ↑ tudo daqui pra frente roda LOCALMENTE
```

Certo:

```powerquery
Origem → Filtrar Ano >= 2024 → Remover colunas → Adicionar Índice
                                                  ↑ só o último passo é local,
                                                    sobre um volume já reduzido
```

### 3.5 Quando não há folding possível

CSV, Excel, JSON e pastas **não dobram** — não existe um motor na outra ponta para receber
a consulta. Nesses casos:

- **filtre e reduza colunas o mais cedo possível** (menos memória no Mashup Engine);
- considere converter os arquivos para **Parquet** e usar um motor (DuckDB, Fabric
  Lakehouse) que dobre;
- lembre que "o mais à esquerda possível" pode significar **antes** do Power BI: um script
  Python/SQL que prepara o dado é frequentemente a melhor arquitetura.

---

## 4. Parâmetros — o que separa amador de profissional

Um `.pbix` com `C:\Users\joao\Downloads\vendas.xlsx` embutido não funciona em mais nenhuma
máquina. Parâmetros resolvem isso.

**Página Inicial → Gerenciar Parâmetros → Novo:**

| Parâmetro | Tipo | Uso |
|---|---|---|
| `PastaDados` | Texto | Caminho base dos arquivos |
| `Servidor` | Texto | Nome do servidor SQL (dev × prod) |
| `BaseDados` | Texto | Nome do banco |
| `AnoInicial` | Número | Corta o histórico durante o desenvolvimento |
| `RangeStart` / `RangeEnd` | Data/Hora | **Nomes obrigatórios** para atualização incremental |
| `Ambiente` | Lista | `Dev`/`Homolog`/`Prod` |

Uso:

```powerquery
let
    Origem = Sql.Database(Servidor, BaseDados),
    Tabela = Origem{[Schema="dbo", Item="Vendas"]}[Data],
    Filtrada = Table.SelectRows(Tabela, each Date.Year([Data]) >= AnoInicial)
in
    Filtrada
```

**Ganhos concretos:**

1. Trocar de dev para produção = mudar um parâmetro, não 12 consultas.
2. Desenvolver com 3 meses de dados e publicar com 5 anos (mude `AnoInicial` no Service).
3. Os *deployment pipelines* trocam parâmetros automaticamente entre estágios.

**No Service:** modelo semântico → Configurações → **Parâmetros**. Dá para alterar sem
republicar.

---

## 5. Funções personalizadas

Quando a mesma transformação se repete, faça uma função.

```powerquery
// Consulta chamada: LimparTexto
let
    Funcao = (entrada as nullable text) as nullable text =>
        if entrada = null then null
        else
            let
                SemEspaco = Text.Trim(entrada),
                SemDuplo  = Text.Replace(SemEspaco, "  ", " "),
                Maiuscula = Text.Upper(SemDuplo)
            in
                if Maiuscula = "" then null else Maiuscula
in
    Funcao
```

Uso:

```powerquery
Table.TransformColumns(Origem, {{"UF", LimparTexto, type text}})
```

**Atalho:** botão direito numa consulta que use um parâmetro → **Criar Função**. O Power
Query gera a função e a consulta de exemplo.

**Padrão profissional:** uma pasta `_Funções` no painel de consultas, com
`Habilitar carga` **desmarcado** — funções não devem virar tabelas no modelo.

---

## 6. Padrões que resolvem 90% dos casos reais

### 6.1 Combinar arquivos de uma pasta

Ver [`06-exemplos.md`](06-exemplos.md) §12, com o código completo e comentado.

**Resumo do que o botão "Combinar Arquivos" automático faz de errado:**

- gera 4 consultas auxiliares confusas;
- usa o **primeiro** arquivo como amostra — se ele for atípico, tudo quebra;
- não filtra `~$` (temporários do Excel) — a atualização morre quando alguém deixa a
  planilha aberta;
- não guarda o nome do arquivo de origem;
- um arquivo corrompido derruba os outros 39.

Escreva à mão. São 20 linhas e você entende cada uma.

### 6.2 Despivotar

A transformação mais valiosa e menos conhecida. Converte "uma coluna por mês" (formato de
apresentação) em "uma linha por mês" (formato de análise).

```
ANTES (não modelável)                 DEPOIS (modelável)
┌────────┬─────┬─────┬─────┐          ┌────────┬───────┬───────┐
│Produto │ jan │ fev │ mar │          │Produto │  Mês  │ Valor │
├────────┼─────┼─────┼─────┤    →     ├────────┼───────┼───────┤
│ Epóxi  │ 100 │ 120 │ 90  │          │ Epóxi  │ jan   │  100  │
│ Verniz │  50 │  70 │ 60  │          │ Epóxi  │ fev   │  120  │
└────────┴─────┴─────┴─────┘          │ Epóxi  │ mar   │   90  │
                                      │ Verniz │ jan   │   50  │
                                      │ ...    │ ...   │  ...  │
                                      └────────┴───────┴───────┘
```

**Sempre use "Despivotar Outras Colunas"** (`Table.UnpivotOtherColumns`), selecionando as
colunas que **devem ficar**. Assim, quando abril aparecer no arquivo do mês que vem, ele é
despivotado automaticamente. Com "Despivotar Colunas" simples, abril fica de fora e
ninguém percebe.

### 6.3 Junção anti — a auditoria de 30 segundos

**Mesclar Consultas → Anti Esquerda**: devolve as linhas do fato que **não** têm
correspondente na dimensão.

Faça isso **antes** de criar qualquer relacionamento. Responde na hora: "existem vendas
com produto que não está no cadastro?". No projeto-modelo, isso encontra as 39 linhas
órfãs em segundos.

### 6.4 Tratamento de erro que não derruba a carga

```powerquery
Table.AddColumn(
    Origem,
    "ValorNumerico",
    each try Number.From([ValorTexto]) otherwise null,
    type nullable number
)
```

**Melhor ainda** — preservar o motivo do erro para auditoria:

```powerquery
let
    ComTentativa = Table.AddColumn(Origem, "Tentativa", each try Number.From([ValorTexto])),
    Resultado = Table.AddColumn(ComTentativa, "Valor",
                    each if [Tentativa][HasError] then null else [Tentativa][Value],
                    type nullable number),
    Motivo = Table.AddColumn(Resultado, "ErroConversao",
                    each if [Tentativa][HasError] then [Tentativa][Error][Message] else null,
                    type nullable text),
    Final = Table.RemoveColumns(Motivo, {"Tentativa"})
in
    Final
```

Isso alimenta a página de auditoria com **o texto exato do erro**, por linha. Nenhuma outra
técnica de Power Query dá tanto retorno.

### 6.5 Gerar uma tabela de datas em M

Alternativa a criá-la em DAX. Vantagem: fica disponível antes do carregamento e não pesa
no refresh do motor.

```powerquery
let
    Inicio = #date(2024, 1, 1),
    Fim    = #date(2026, 12, 31),
    NDias  = Duration.Days(Fim - Inicio) + 1,
    Lista  = List.Dates(Inicio, NDias, #duration(1,0,0,0)),
    Tabela = Table.FromList(Lista, Splitter.SplitByNothing(), {"Data"}),
    Tipada = Table.TransformColumnTypes(Tabela, {{"Data", type date}}),
    ComAno = Table.AddColumn(Tipada, "Ano", each Date.Year([Data]), Int64.Type),
    ComNum = Table.AddColumn(ComAno, "NumMes", each Date.Month([Data]), Int64.Type),
    ComMes = Table.AddColumn(ComNum, "Mes",
                 each Date.ToText([Data], [Format="MMM", Culture="pt-BR"]), type text),
    ComAM  = Table.AddColumn(ComMes, "AnoMes",
                 each Date.ToText([Data], [Format="yyyy-MM"]), type text),
    ComTri = Table.AddColumn(ComAM, "Trimestre",
                 each "T" & Text.From(Date.QuarterOfYear([Data])), type text),
    ComDU  = Table.AddColumn(ComTri, "DiaUtil",
                 each Date.DayOfWeek([Data], Day.Monday) < 5, type logical),
    ComIdx = Table.AddColumn(ComDU, "IndiceMes",
                 each (Date.Year([Data]) - Date.Year(Inicio)) * 12
                      + Date.Month([Data]) - 1, Int64.Type)
in
    ComIdx
```

**Melhoria profissional:** troque `Inicio`/`Fim` por parâmetros, ou derive-os da própria
tabela de fatos, para o calendário nunca ficar curto.

### 6.6 Consumir API paginada

Ver [`06-exemplos.md`](06-exemplos.md) §13, com os dois padrões (por página e por cursor)
e o alerta sobre **fonte dinâmica**, que impede a atualização agendada.

---

## 7. Dataflows — Power Query na nuvem

> **Dataflow** — uma consulta Power Query que roda **no Service** e grava o resultado, para
> ser reutilizado por vários modelos semânticos.

| Use quando | Não use quando |
|---|---|
| A mesma limpeza é repetida por 5 analistas | Só um modelo consome |
| Você quer separar "preparar" de "modelar" | A latência extra atrapalha |
| A fonte é lenta e você quer materializar | Você já tem um data warehouse decente |
| Quer que um analista consuma dado pronto sem acessar o banco | — |

**Gen1 × Gen2:** o Gen1 é o dataflow clássico do Power BI; o **Gen2** é do Fabric, grava em
OneLake, aceita destinos de saída e é o caminho atual.

**Opinião do autor:** dataflows são frequentemente usados como substituto de um data
warehouse que a empresa deveria ter. Funcionam, ficam lentos e viram uma cadeia de
dependências sem observabilidade. Se você está encadeando três dataflows, o problema não
é de Power BI — é de arquitetura de dados.

---

## 8. Erros comuns, com a mensagem literal

| Mensagem | Causa | Correção |
|---|---|---|
| `Expression.Error: A coluna 'X' da tabela não foi encontrada.` | Coluna renomeada ou ausente na origem | Etapas com nomes fixos quebram. Use `Table.SelectColumns(t, cols, MissingField.Ignore)` |
| `DataFormat.Error: Não foi possível converter em Número.` | Texto numa coluna numérica | `try ... otherwise null` (§6.4) e auditoria |
| `Formula.Firewall: A consulta 'X' referencia outras consultas...` | Níveis de privacidade incompatíveis entre fontes | Ajuste Opções → Privacidade → *Ignorar níveis de privacidade*, **ou** reestruture para não misturar fontes numa mesma consulta |
| `This dataset includes a dynamic data source...` | URL montada por concatenação em `Web.Contents` | Use os parâmetros `Query` e `RelativePath` (§[`06`](06-exemplos.md) §13) |
| `We couldn't authenticate with the credentials provided` | Credencial mudou ou expirou | Opções → Configurações da fonte de dados → Editar permissões |
| `The key didn't match any rows in the table` | `Origem{[Item="X"]}` com nome errado | Confira o nome exato do objeto na fonte |
| Atualização eterna, memória crescendo | Falta de folding + `Table.Buffer` mal usado | Verifique a consulta nativa (§3.2) |

### O *Formula Firewall*, explicado

É o erro mais odiado do Power Query. O motor impede que dados de uma fonte "privada"
sejam enviados como filtro para outra fonte, para evitar vazamento — por exemplo, mandar
CPFs de um Excel local para uma API pública numa cláusula `WHERE`.

**É uma proteção legítima com uma mensagem péssima.** As saídas, em ordem de qualidade:

1. **Reestruture:** separe em duas consultas — uma que só lê a fonte A e outra que só lê
   a B — e combine numa terceira.
2. Classifique as fontes com o mesmo nível de privacidade.
3. Em último caso, desligue a verificação (Opções → Arquivo Atual → Privacidade). Entenda
   que você está abrindo mão de uma proteção real.

---

## 9. Desempenho no Power Query

| Prática | Ganho |
|---|---|
| Reduzir colunas **no primeiro passo possível** | Alto |
| Filtrar linhas cedo | Alto |
| Preservar o folding | **Altíssimo** |
| Evitar `Table.Buffer` (só quando realmente necessário) | Alto |
| Remover a etapa "Alterado Tipo" automática do CSV e tipar uma vez, no fim | Médio |
| Desabilitar "Habilitar carga" em consultas auxiliares | Médio |
| Desabilitar a atualização em segundo plano durante o desenvolvimento | Médio |
| Evitar mesclagens em cadeia sobre tabelas grandes | Alto |
| Substituir muitas colunas condicionais por uma tabela de-para + mesclagem | Médio |

**A ferramenta de diagnóstico:** guia **Ferramentas** → **Iniciar Diagnóstico** no Editor
do Power Query. Gera uma tabela com tempo por operação. Subutilizada e muito útil.

---

## 10. Os cinco porquês: por que o Power Query existe se já existe SQL?

1. **Por que não escrever SQL direto?**
   Porque nem toda fonte é um banco. Excel, CSV, SharePoint, API REST, PDF e pastas não
   falam SQL.

2. **Por que não converter tudo para um banco primeiro?**
   Porque isso exige um processo de engenharia de dados, um servidor e uma equipe — que é
   justamente o que o *self-service BI* de 2009 queria evitar. O Power Query é a
   materialização daquela decisão de produto.

3. **Por que uma linguagem funcional e não algo mais familiar?**
   Porque as transformações precisam ser **composáveis e reordenáveis** para o motor poder
   analisá-las e traduzi-las em SQL (folding). Numa linguagem imperativa com efeitos
   colaterais, essa análise seria muito mais difícil — em muitos casos, impossível.

4. **Por que o folding é possível numa linguagem funcional?**
   Porque cada passo é uma transformação pura sobre uma tabela, e o motor reconhece
   padrões conhecidos (`Table.SelectRows` → `WHERE`, `Table.Group` → `GROUP BY`) e os
   compõe numa árvore que vira uma consulta única.

5. **Parada legítima — propriedade matemática.**
   O folding funciona porque **composição de funções puras é analisável**. É o mesmo
   princípio que sustenta otimizadores de consulta relacional desde os anos 1970: se você
   descreve *o que* quer em vez de *como* fazer, alguém pode reescrever o *como*. Quando
   você usa uma função M que o motor não sabe traduzir, quebra a analisabilidade — e o
   folding morre ali.

---

## 11. Autoteste

1. Em que momento o código M executa? E o DAX?
2. Como você verifica se uma etapa faz *query folding*, e como acha onde ele parou?
3. Qual a regra de ouro sobre a ordem dos passos?
4. Por que CSV e Excel não dobram?
5. Cite três problemas do botão "Combinar Arquivos" automático.
6. Por que usar "Despivotar Outras Colunas" em vez de "Despivotar Colunas"?
7. O que uma junção Anti Esquerda responde em 30 segundos?
8. O que é o *Formula Firewall*, por que ele existe e qual a melhor saída?
9. Por que uma URL concatenada em `Web.Contents` impede a atualização agendada?
10. Explique por que o folding só é possível porque M é funcional.

---

**Próximo:** [`14-modelagem-dimensional.md`](14-modelagem-dimensional.md) — o capítulo mais
importante do curso.
