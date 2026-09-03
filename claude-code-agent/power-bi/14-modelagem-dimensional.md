# 14 · Modelagem dimensional

**Nível:** intermediário
**Data:** 14/08/2026

> **Este é o capítulo mais importante do curso.**
>
> A diferença entre quem sofre com Power BI e quem não sofre é modelagem. Não é DAX, não é
> design, não é conhecer 200 funções. É saber organizar tabelas.
>
> Quase todo problema de "DAX difícil" é um problema de modelagem disfarçado. Quase todo
> problema de "Power BI lento" é um problema de modelagem disfarçado. Quase todo "número
> errado" é um problema de modelagem disfarçado.

---

## 1. O problema, mostrado

Você recebe isto:

```
VENDAS_COMPLETO.xlsx  — 60.000 linhas × 34 colunas
┌─────┬──────────┬──────────────────┬───────────┬─────┬──────────┬─────────┬──────┐
│ NF  │  Data    │ Produto          │ Categoria │ ... │ Cliente  │ Cidade  │ UF   │
├─────┼──────────┼──────────────────┼───────────┼─────┼──────────┼─────────┼──────┤
│ 101 │14/03/2026│ Tinta Epóxi 3,6L │ Tintas    │ ... │ Metal. X │São Paulo│ SP   │
│ 101 │14/03/2026│ Verniz PU 5L     │ Vernizes  │ ... │ Metal. X │São Paulo│ SP   │
│ 102 │15/03/2026│ Tinta Epóxi 3,6L │ Tintas    │ ... │ Const. Y │ Recife  │ PE   │
└─────┴──────────┴──────────────────┴───────────┴─────┴──────────┴─────────┴──────┘
```

Uma tabela grande e achatada. **Ela funciona.** Você arrasta `Categoria` e `Valor` e o
gráfico aparece. Por que mexer?

**Cinco motivos, todos concretos:**

1. **Memória.** `"Tinta Epóxi Bicomponente 3,6L"` (28 caracteres) repetido 8.000 vezes.
   O VertiPaq comprime bem, mas o custo é real e cresce com a cardinalidade combinada.
2. **Datas.** Sem tabela de datas separada, `SAMEPERIODLASTYEAR` não funciona
   corretamente e meses sem venda **somem** do gráfico.
3. **Consistência.** "São Paulo", "Sao Paulo", "SÃO PAULO" e "S. Paulo" viram quatro
   cidades. E não há um lugar para corrigir.
4. **Extensibilidade.** Chega uma segunda tabela de fatos (metas, estoque, orçamento). Com
   quê ela se conecta? Não há dimensão para compartilhar.
5. **Dados que não são de venda.** Um produto que nunca vendeu **não existe** neste
   arquivo. "Quais produtos não venderam este mês?" é inrespondível.

O item 5 é o mais profundo: **a tabela achatada só contém o que aconteceu**. Análise séria
depende de saber o que *não* aconteceu.

---

## 2. A solução: esquema estrela

```
                       ┌───────────────┐
                       │  dCalendario  │
                       │  Data (PK)    │
                       │  Ano, Mês...  │
                       └───────┬───────┘
                               │ 1
                               │
                               │ *
   ┌───────────────┐      ┌────▼─────────┐      ┌───────────────┐
   │   dProduto    │  1   │   fVendas    │   *  │   dCliente    │
   │ SK_Produto(PK)├─────►│ Data      FK │◄─────┤ SK_Cliente(PK)│
   │ Produto       │   *  │ SK_Produto FK│  1   │ Cliente       │
   │ Categoria     │      │ SK_Cliente FK│      │ Segmento      │
   │ Linha         │      │ SK_Vendedor  │      │ UF, Cidade    │
   └───────────────┘      │ Quantidade   │      └───────────────┘
                          │ Preço, Custo │
                          └──────┬───────┘
                                 │ *
                                 │ 1
                          ┌──────▼───────┐
                          │  dVendedor   │
                          └──────────────┘
```

**A regra de uma frase:**

> Uma tabela de fatos no centro, com **números e chaves**; dimensões ao redor, com
> **texto e atributos**; cada dimensão a **um salto** de distância.

### Como converter, na prática

Da tabela achatada para a estrela, no Power Query:

1. **Duplique** a consulta original tantas vezes quantas forem as dimensões.
2. Em cada cópia, **selecione só as colunas daquela entidade** e remova duplicatas.
   Ex.: `dProduto` = `Produto`, `Categoria`, `Linha`, `Custo` → Remover Duplicatas.
3. **Adicione uma chave substituta** (Adicionar Coluna → Coluna de Índice, começando em 1).
4. Na tabela de fatos, **mescle** com cada dimensão para trazer a `SK`, e depois **remova**
   as colunas descritivas.
5. Crie a `dCalendario` (ver [`13`](13-power-query-e-m.md) §6.5).
6. Monte os relacionamentos.

Leva de 30 minutos a 2 horas. É o melhor investimento de tempo em todo o projeto.

---

## 3. Projetando a tabela de fatos

### 3.1 Os quatro passos de Kimball

Kimball propôs em 1996 um roteiro de quatro decisões, nesta ordem. Ele continua sendo o
melhor que existe:

**1. Escolha o processo de negócio.** Vendas? Produção? Cobrança? Um processo por fato.

**2. Declare a granularidade.** Complete: *"uma linha desta tabela é ______"*.
Não avance sem isso. Errar aqui condena o projeto.

**3. Identifique as dimensões.** Pergunte: *"como as pessoas vão querer fatiar isso?"*
Por produto, por cliente, por data, por vendedor, por canal, por motivo.

**4. Identifique os fatos.** Os números que se somam: quantidade, valor, custo, duração.

### 3.2 Os três tipos de medida numérica

Distinção subestimada e que causa erro grave:

| Tipo | Soma em quais dimensões? | Exemplos |
|---|---|---|
| **Aditiva** | Todas | Quantidade vendida, valor, custo |
| **Semiaditiva** | Todas **menos tempo** | Saldo de estoque, saldo bancário, nº de funcionários |
| **Não aditiva** | Nenhuma | Percentual, razão, temperatura, pH, preço unitário |

**Por que importa.** Se `Estoque` (semiaditiva) for somado ao longo do tempo, você obtém
"estoque acumulado do trimestre" — um número que não significa nada. O correto é o
**último** valor do período:

```dax
Estoque Atual =
CALCULATE(
    SUM( fEstoque[Quantidade] ),
    LASTDATE( dCalendario[Data] )
)
```

ou, mais robusto:

```dax
Estoque Fim de Período =
CALCULATE( SUM( fEstoque[Quantidade] ), LASTNONBLANK( dCalendario[Data], 1 ) )
```

Para não aditivas: **nunca armazene o resultado; armazene os componentes.** Guarde
`Faturamento` e `Custo` e calcule `Margem %` como medida. Guardar `Margem %` por linha
garante um total errado.

**Exemplo do mundo químico** (que aparece em [`../sql/`](../sql/00-MAPA.md)): pH é
logarítmico. Média de pH é matematicamente errada — a média correta é sobre a concentração
de H⁺, convertida de volta. Um modelo que permite arrastar `pH` para "Média" está
convidando ao erro.

### 3.3 Os três tipos de tabela de fatos

| Tipo | Uma linha é | Exemplo |
|---|---|---|
| **Transacional** | um evento | um item de nota fiscal |
| **Snapshot periódico** | o estado num instante | saldo de estoque no fim de cada dia |
| **Snapshot acumulado** | um processo com etapas | um pedido, com colunas de data para cada etapa |

O terceiro é o menos conhecido e o mais útil para análise de processo (lead time, gargalo):
uma linha por pedido, com `DataPedido`, `DataAprovação`, `DataProdução`, `DataFaturamento`,
`DataEntrega`. A linha é **atualizada** conforme o pedido avança.

---

## 4. Projetando as dimensões

### 4.1 Regras

1. **Achatada, não normalizada.** `dProduto` contém `Categoria`, `Linha` e `Fabricante`
   como colunas — não como tabelas separadas.
2. **Texto legível, não código.** `"Proteção Industrial"`, não `"PI"`. A dimensão é a
   interface com o usuário.
3. **Chave substituta inteira** (`SK_`), oculta.
4. **Sem valores nulos.** Troque `null` por `"(não informado)"`. Nulo em atributo de
   dimensão vira "Em branco" no visual e não é filtrável de forma confiável.
5. **Um membro desconhecido**, com chave conhecida (`0` ou `-1` ou `999`), para receber
   fatos órfãos. É o padrão usado no [`07-projeto-modelo/`](07-projeto-modelo/README.md).
6. **Colunas de ordenação** para tudo que não ordena alfabeticamente
   (mês, faixa etária, prioridade), com `Classificar por Coluna`.

### 4.2 Dimensões que mudam com o tempo (SCD)

O cliente mudou de região. As vendas antigas devem aparecer na região antiga ou na nova?

| Tipo | Comportamento | Quando usar |
|---|---|---|
| **SCD 0** | Nunca muda | Data de nascimento |
| **SCD 1** | Sobrescreve | Correção de erro de digitação |
| **SCD 2** | Cria nova linha com vigência | **Histórico importa** (região do cliente, cargo) |
| **SCD 3** | Guarda "valor anterior" numa coluna | Só um nível de histórico |
| **SCD 4** | Tabela de histórico separada | Atributos que mudam muito |
| **SCD 6** | Híbrido 1+2+3 | "Ver como era" **e** "ver como é hoje" |

**SCD 2 na prática:**

```
dCliente
┌────┬──────────┬───────────┬─────────┬────────────┬────────────┬───────┐
│ SK │  CNPJ    │  Cliente  │ Regiao  │ VigenteDe  │ VigenteAte │ Atual │
├────┼──────────┼───────────┼─────────┼────────────┼────────────┼───────┤
│ 12 │ 11.222...│ Metal. X  │ Sudeste │ 2020-01-01 │ 2025-06-30 │ Não   │
│ 87 │ 11.222...│ Metal. X  │ Sul     │ 2025-07-01 │ 9999-12-31 │ Sim   │
└────┴──────────┴───────────┴─────────┴────────────┴────────────┴───────┘
```

O fato guarda a `SK` **vigente na data do evento**. Vendas de 2024 apontam para SK 12;
de 2026, para SK 87.

**A consequência que pega todo mundo:** `DISTINCTCOUNT(dCliente[SK])` conta 2 clientes
onde há 1. Conte o **CNPJ**. É exatamente o defeito nº 2 do projeto-modelo, e ele existe
lá justamente porque é o erro mais comum em modelos com histórico.

Para permitir as duas visões, adicione uma coluna `RegiaoAtual` (SCD 6): o usuário escolhe
analisar "como era" (`Regiao`) ou "como é hoje" (`RegiaoAtual`).

### 4.3 Dimensão degenerada

> **Dimensão degenerada** — um identificador de transação que fica **na própria tabela de
> fatos**, sem dimensão correspondente.

`NF` é o caso clássico. Não faz sentido criar `dNotaFiscal` só com o número. Deixe na
fato, torne visível, e use `DISTINCTCOUNT(fVendas[NF])` para contar notas.

### 4.4 Dimensão de papel múltiplo

Uma mesma dimensão usada em papéis diferentes: `DataPedido`, `DataEntrega`,
`DataVencimento` — todas apontando para `dCalendario`.

**Duas soluções, e ambas são legítimas:**

| Solução | Vantagem | Desvantagem |
|---|---|---|
| **Relações inativas + `USERELATIONSHIP`** | Uma só dimensão; modelo limpo | Não dá para pôr as duas datas em eixos diferentes do mesmo visual |
| **Duplicar a dimensão** (`dCalendarioEntrega`) | Independência total | Mais tabelas, dois conjuntos de segmentações, mais confusão |

**Minha regra:** `USERELATIONSHIP` quando a segunda data é secundária; duplicar quando as
duas são analiticamente equivalentes e usadas lado a lado. Ver
[`06-exemplos.md`](06-exemplos.md) §10.

---

## 5. Múltiplas tabelas de fatos

Regra absoluta:

> **Tabelas de fatos nunca se relacionam entre si.** Só com dimensões.

Errado:

```
fVendas ──────────► fMetas       ✘ ambiguidade, números inflados
```

Certo:

```
        dVendedor              dMes
       ╱     │    ╲          ╱     ╲
 fVendas     │     fMetas ◄─┘       └─► dCalendario ──► fVendas
```

Duas tabelas de fatos que compartilham dimensões formam um **constelação de fatos**
(*fact constellation*) ou **esquema em galáxia**. É o padrão normal em qualquer modelo
corporativo.

### O problema da granularidade diferente

`fVendas` é diária; `fMetas` é mensal. `dCalendario[AnoMes]` não é única (30 linhas por
mês) e não pode ser o lado "1".

**Solução canônica:** uma dimensão na granularidade mais grossa (`dMes`), que se relaciona
com as duas.

```
dMes ──1:*──► dCalendario ──1:*──► fVendas
  └──1:*──► fMetas ──*:1──► dVendedor
```

Implementação completa e comentada em
[`07-projeto-modelo/modelo/definition/relationships.tmdl`](07-projeto-modelo/modelo/definition/relationships.tmdl).

**O detalhe que quase ninguém acerta de primeira:** com direção única, filtrar
`dCalendario[Ano] = 2026` **não** chega a `fMetas` — o filtro só desce da dimensão para o
fato, e `dCalendario` está no lado "muitos" em relação a `dMes`. Duas saídas:

1. tornar `dMes ↔ dCalendario` **bidirecional** (aceitável aqui: é ponte
   dimensão-dimensão com caminho único, sem ambiguidade); ou
2. colocar os atributos de tempo em `dMes` e instruir o usuário a filtrar por lá.

Escolhi (1) no projeto-modelo, **com a justificativa escrita no próprio arquivo**. Toda
exceção a uma regra de projeto deve carregar seu porquê ao lado.

---

## 6. Relacionamentos muitos-para-muitos

### 6.1 O caso legítimo: tabela ponte

Um produto pertence a **várias** campanhas; uma campanha tem **vários** produtos.

**Errado:** relacionar `dProduto` a `dCampanha` com cardinalidade `*:*`.

**Certo:** uma tabela ponte (*bridge*) na granularidade da combinação:

```
   dProduto        bProdutoCampanha        dCampanha
  ┌─────────┐     ┌───────────────┐       ┌──────────┐
  │SK_Produto├─1:*►│ SK_Produto    │◄*:1──┤SK_Campanha│
  └─────────┘     │ SK_Campanha   │       └──────────┘
                  └───────────────┘
```

A ponte precisa de **filtro bidirecional** de `dProduto` para funcionar, ou de
`CROSSFILTER` nas medidas. E aí vem o alerta:

> **Com ponte muitos-para-muitos, os totais não somam.** Um produto em três campanhas
> aparece nas três, e a soma das campanhas é maior que o total. **Isso está correto** —
> mas precisa estar escrito no relatório, ou alguém vai reportar como bug todo mês.

### 6.2 O caso ilegítimo: chave duplicada

Se o Power BI propõe `*:*` ao criar uma relação com uma dimensão, **isso é um sintoma**,
não uma solução. Significa que a coluna do lado "1" tem valores repetidos.

**Faça:** Remover Duplicatas na dimensão, e descubra **por que** havia duplicata. Quase
sempre é SCD 2 mal implementada, cadastro duplicado ou granularidade errada.

Aceitar o `*:*` proposto pelo Power BI é a forma mais rápida de produzir números inflados
que ninguém entende.

---

## 7. Direção de filtro — a decisão mais perigosa

### 7.1 O padrão

Direção **única**, da dimensão para o fato. Sempre. Por padrão.

### 7.2 Por que bidirecional é tentador

Você tem `dProduto → fVendas ← dCliente` e quer uma segmentação de `dCliente` que só
mostre clientes que compraram tintas. Com direção única, ela mostra todos.

Ativar bidirecional em `dProduto → fVendas` resolve na hora.

### 7.3 Por que é perigoso

**Ambiguidade.** Com duas ou mais dimensões bidirecionais, existe mais de um caminho de
filtro entre duas tabelas. O motor precisa escolher — e a escolha pode não ser a que você
espera. Em casos claros, o Power BI recusa e mostra:

```
You can't create a direct relationship between ... because it would create ambiguity
between tables ...
```

Em casos sutis, ele **aceita** e devolve números silenciosamente errados.

**Desempenho.** Cada propagação bidirecional é trabalho extra em toda consulta.

**RLS.** Filtro bidirecional pode fazer a segurança vazar por caminhos inesperados. Este é
o risco mais grave, e é o motivo pelo qual a documentação da Microsoft recomenda revisar
todas as relações bidirecionais ao implementar RLS.

### 7.4 O que fazer em vez disso

| Necessidade | Solução sem bidirecional |
|---|---|
| Segmentação que só mostra o que existe | Nas opções do visual, "Mostrar itens sem dados" desligado, ou uma medida de filtro |
| Filtrar dimensão A pela dimensão B | Uma medida com `TREATAS` ou `CROSSFILTER` **local** |
| Ponte muitos-para-muitos | Bidirecional **só na ponte** (caso legítimo) |
| Duas dimensões que precisam se ver | Provavelmente falta uma dimensão comum |

`CROSSFILTER` dentro de `CALCULATE` é a alternativa profissional: liga o bidirecional
**apenas naquela medida**, de forma visível e reversível.

```dax
Clientes que compraram esta categoria =
CALCULATE(
    DISTINCTCOUNT( dCliente[CNPJ] ),
    CROSSFILTER( fVendas[SK_Cliente], dCliente[SK_Cliente], BOTH )
)
```

---

## 8. Sinais de que o seu modelo está errado

Um checklist de diagnóstico. Cada item é sintoma de um problema estrutural.

- [ ] Existe uma tabela com mais de 15 colunas de texto e milhões de linhas.
- [ ] Não existe tabela de datas própria, ou ela não está marcada.
- [ ] Existe relacionamento entre duas tabelas de fatos.
- [ ] Existem relações `*:*` que não são pontes deliberadas.
- [ ] Existem mais de uma ou duas relações bidirecionais.
- [ ] Existem colunas calculadas na tabela de fatos que poderiam estar no Power Query.
- [ ] Medidas usam `FILTER(tabela_de_fatos, ...)` com frequência.
- [ ] Existem tabelas que ninguém sabe explicar para que servem.
- [ ] O usuário precisa saber quais campos "podem" ser cruzados.
- [ ] Chaves técnicas (`ID`, `SK`) estão visíveis no painel Dados.
- [ ] O mesmo conceito de negócio aparece em duas tabelas com nomes diferentes.
- [ ] Você precisa explicar a alguém "esse número só funciona se você filtrar X primeiro".

Três ou mais marcados: pare e remodele. Vai custar menos que continuar.

---

## 9. Otimizações de modelo que valem ouro

Em ordem de retorno sobre esforço:

**1. Remova colunas que ninguém usa.** A mais eficaz e a mais ignorada. Cada coluna
carregada custa memória e tempo de refresh, use-se ou não. A ferramenta *Measure Killer*
ou o VertiPaq Analyzer identificam as candidatas.

**2. Reduza cardinalidade.**
- Separe `DataHora` em `Data` + `Hora`.
- Arredonde decimais para a precisão que o negócio usa.
- Substitua textos longos repetidos por chaves inteiras.

**3. Desligue "Data/hora automática".** Cria uma tabela de datas oculta **por coluna de
data**. Em modelos reais, dezenas de por cento do arquivo.

**4. Oculte tudo que é técnico.** Não é cosmética: um modelo que expõe 200 campos é um
modelo que será usado errado.

**5. Use `SK` inteiras em vez de chaves de texto.** Ganho de compressão e de velocidade de
junção.

**6. Agregue quando a granularidade fina não for usada.** Se ninguém analisa por item de
NF, agregue por NF. 5× menos linhas.

**7. Tabelas de agregação** (*aggregations*). Para modelos grandes: uma tabela pequena
pré-agregada que o motor usa automaticamente quando a consulta não pede detalhe. Recurso
avançado, ganho enorme. Ver [`22-desempenho.md`](22-desempenho.md).

---

## 10. Os cinco porquês: por que estrela é melhor que uma tabela achatada?

1. **Por que não uma tabela só, se funciona?**
   Porque uma tabela só não contém as entidades que não participaram de nenhum evento
   (produto sem venda), não dá lugar para uma segunda tabela de fatos, e obriga a repetir
   texto descritivo em toda linha.

2. **Por que a repetição de texto é ruim, se o VertiPaq comprime?**
   Comprime, mas o custo não é zero: cada coluna tem seu dicionário e sua estrutura de
   índice. E, mais importante, a **cardinalidade combinada** de uma tabela larga reduz a
   eficácia da ordenação interna — o VertiPaq escolhe uma ordem de linhas que otimiza a
   compressão global, e mais colunas de alta cardinalidade pioram esse compromisso.

3. **Por que o motor é mais rápido em estrela?**
   Porque o VertiPaq tem caminhos otimizados para o padrão "filtrar dimensões pequenas,
   varrer fato grande". Ele materializa os valores selecionados da dimensão, converte em
   um filtro sobre a coluna de chave do fato (inteiros densos) e varre. Junções em
   cadeia (floco) ou padrões arbitrários não têm esse tratamento.

4. **Por que a chave do fato precisa ser inteira e densa para isso funcionar?**
   Porque o VertiPaq pode usar *value encoding* em inteiros densos — armazenar a diferença
   em relação a um valor base, com pouquíssimos bits por valor — e comparar filtros com
   operações de bits, sem consultar dicionário. Chave de texto força *hash encoding* e uma
   indireção a cada linha.

5. **Parada legítima — arquitetura de hardware.**
   No fundo, tudo isso é para **caber no cache da CPU e ler bytes contíguos**. A varredura
   de uma coluna comprimida de inteiros é uma operação vetorizável, sequencial, previsível
   pelo pré-buscador do processador. Estrela é a forma de organizar dados que maximiza a
   chance de o motor fazer exatamente isso. Não é convenção: é consequência de como
   memória e CPU funcionam. Ver [`21-vertipaq-por-dentro.md`](21-vertipaq-por-dentro.md).

---

## 11. Autoteste

1. Cite os cinco problemas de uma tabela grande e achatada, e diga qual é o mais profundo.
2. Quais são os quatro passos de Kimball, na ordem?
3. Diferencie medida aditiva, semiaditiva e não aditiva, com um exemplo de cada.
4. Por que nunca se deve armazenar `Margem %` como coluna?
5. O que é SCD tipo 2 e qual erro de contagem ele causa?
6. Por que duas tabelas de fatos nunca devem se relacionar diretamente?
7. Descreva a solução para relacionar um fato diário e um fato mensal.
8. Quando um relacionamento muitos-para-muitos é legítimo, e o que acontece com os totais?
9. Cite três riscos do filtro bidirecional e a alternativa profissional.
10. Liste cinco otimizações de modelo em ordem de retorno.
11. Explique, em termos de hardware, por que o esquema estrela é rápido.

---

**Próximo:** [`15-dax-fundamentos.md`](15-dax-fundamentos.md) — a linguagem de cálculo.
