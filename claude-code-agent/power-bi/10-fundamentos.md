# 10 · Fundamentos — vocabulário e modelos mentais

**Nível:** iniciante
**Data:** 14/08/2026

Este arquivo constrói o vocabulário. Cada termo é definido **antes** de ser usado, e cada
conceito abstrato ganha um exemplo concreto logo depois. Se você pular este arquivo, tudo
o que vier depois soará como jargão.

---

## 1. O objeto central: a tabela

> **Tabela** — um conjunto de linhas com as mesmas colunas. Cada **linha** é uma ocorrência;
> cada **coluna** é um atributo com um tipo fixo.

```
fVendas
┌─────────┬────────────┬────────────┬────────────┬────────────┐
│   NF    │    Data    │ SK_Produto │ Quantidade │   Preco    │
├─────────┼────────────┼────────────┼────────────┼────────────┤
│ 100001  │ 2026-03-14 │      3     │     10     │   315,00   │  ← uma linha
│ 100001  │ 2026-03-14 │      7     │      4     │   428,00   │
│ 100002  │ 2026-03-15 │      3     │     25     │   315,00   │
└─────────┴────────────┴────────────┴────────────┴────────────┘
     ▲
   uma coluna
```

**Tudo no Power BI é tabela.** O resultado de uma consulta é tabela. Um filtro é uma
tabela. Uma medida é avaliada sobre tabelas. `CALCULATE` manipula tabelas. Quem pensa em
células (herança do Excel) trava; quem pensa em conjuntos e filtros avança.

---

## 2. Fato e dimensão — a distinção que organiza tudo

> **Tabela de fatos** (*fact table*) — registra **eventos que aconteceram**, com medidas
> numéricas. Cresce sem parar. Verbos: vendeu, produziu, pagou, mediu.
>
> **Tabela de dimensão** (*dimension table*) — descreve o **contexto** dos eventos.
> Cresce devagar ou nunca. Substantivos: produto, cliente, data, vendedor, equipamento.

Teste prático de dois segundos: **você conta ou você agrupa por?**

| Tabela | Você faz o quê? | É |
|---|---|---|
| Vendas | soma, conta | **fato** |
| Produto | agrupa por, filtra por | **dimensão** |
| Leituras de sensor | soma, média | **fato** |
| Instrumento | filtra por | **dimensão** |
| Data | filtra por, agrupa por | **dimensão** |

**Propriedades práticas que decorrem disso:**

| | Fato | Dimensão |
|---|---|---|
| Nº de linhas | milhões a bilhões | dezenas a milhões |
| Nº de colunas | poucas, estreitas | muitas, descritivas |
| Crescimento | contínuo | lento |
| Tipo predominante | números e chaves | texto e datas |
| No visual, vai para | valores | eixos, legendas, filtros |
| Convenção de nome | `fVendas`, `fct_vendas` | `dProduto`, `dim_produto` |

O erro estrutural mais caro no Power BI é misturar as duas coisas numa tabela grande
e achatada ("uma planilha com tudo"). O motivo está em
[`14-modelagem-dimensional.md`](14-modelagem-dimensional.md) e a comprovação, em
[`21-vertipaq-por-dentro.md`](21-vertipaq-por-dentro.md).

---

## 3. Granularidade

> **Granularidade** (*grain*) — o que **uma linha** da tabela de fatos representa.

Este é o conceito mais importante e menos discutido do BI. Antes de qualquer coisa,
complete a frase: *"nesta tabela, uma linha é ______"*.

| Frase | Granularidade |
|---|---|
| "uma linha é **um item de nota fiscal**" | NF + item |
| "uma linha é **uma nota fiscal**" | NF |
| "uma linha é **o total do dia por produto**" | dia + produto |
| "uma linha é **a leitura de um sensor por minuto**" | sensor + minuto |

**Três consequências, todas duras:**

1. **Você nunca desce abaixo da granularidade.** Se o fato é diário, não há resposta
   para "quanto vendemos às 14h". O dado não existe. Nenhum DAX resolve isso.
2. **Granularidades diferentes não se relacionam diretamente.** Vendas diárias e metas
   mensais precisam de uma dimensão compartilhada — o padrão do
   [`06-exemplos.md`](06-exemplos.md) §7.
3. **Agregar reduz o tamanho, mas fecha portas.** Trocar granularidade de item para nota
   pode reduzir o modelo em 5× — e impedir para sempre a análise por produto.

**Regra que uso:** guarde na granularidade mais fina que couber no orçamento de memória
e tempo. Depois agregue por cima. O contrário não tem volta.

---

## 4. Medida × coluna calculada

> **Coluna calculada** — uma coluna nova, calculada **linha a linha**, na hora do
> carregamento, e **armazenada** na memória do modelo.
>
> **Medida** — uma expressão avaliada **na hora da consulta**, no contexto do visual, e
> **não armazenada**.

```
COLUNA CALCULADA                          MEDIDA
─────────────────                         ──────
Calculada quando?  no refresh             a cada clique
Ocupa memória?     sim, 1 valor/linha     não
Vê o quê?          a linha atual          o contexto de filtro
Reage a filtro?    não                    sim
Pode ir no eixo?   sim                    não
Custo do refresh   maior                  zero
Custo da consulta  zero                   variável
```

**A regra de decisão, em uma frase:**

> **Se o resultado depende do que está filtrado, é medida. Se é um atributo da linha,
> é coluna.**

| Você quer | É |
|---|---|
| Faturamento da linha (`qtd × preço`) | Pode ser coluna, mas prefira medida com `SUMX` |
| Margem % | **Medida** (percentual não soma) |
| Faixa de preço do produto ("até R$ 100") | **Coluna** (atributo fixo, vai no eixo) |
| Ranking do produto | **Medida** (muda com o filtro) |
| Ano da data | **Coluna** na dimensão de datas |
| Ticket médio | **Medida** |
| Dias entre pedido e entrega | **Coluna** (atributo da linha) |

**Por que colunas calculadas são desaconselhadas em tabelas de fato:** elas ocupam memória
proporcional ao número de linhas e — pior — costumam comprimir mal, porque muitas vezes
têm alta cardinalidade. Uma coluna calculada numa tabela de 100 milhões de linhas pode
custar mais que a tabela original. Ver [`21`](21-vertipaq-por-dentro.md).

**Existe um terceiro:** a **coluna do Power Query**. Calculada em M, antes do carregamento,
e frequentemente **dobrada para a fonte** (o banco calcula). Quando a lógica não precisa
do modelo, prefira o Power Query — é o mais barato dos três.

---

## 5. Contexto — o conceito que separa iniciante de profissional

> **Contexto de avaliação** — o conjunto de filtros ativos no momento em que uma medida é
> calculada.

A mesma medida devolve valores diferentes em lugares diferentes **da mesma página**, e
isso não é bug: é o desenho.

```
Faturamento = SUM( fVendas[Valor] )

┌────────────────────────┐   Contexto: nenhum filtro
│  Faturamento           │   → soma tudo
│    R$ 167.700.759      │
└────────────────────────┘

┌──────────┬─────────────┐   Contexto de CADA CÉLULA:
│ Categoria│ Faturamento │   Categoria = "Tintas"
├──────────┼─────────────┤   → soma só as tintas
│ Tintas   │ 107.237.686 │
│ Resinas  │  21.207.771 │   Contexto: Categoria = "Resinas"
│ Total    │ 167.700.759 │   ← o TOTAL NÃO é a soma das linhas.
└──────────┴─────────────┘     É a medida recalculada SEM o filtro de categoria.
```

**A frase que resolve metade das dúvidas de DAX:**

> O total de uma matriz **não** é a soma das linhas. É a mesma medida, avaliada num
> contexto diferente.

Isso explica por que `Margem %` no total não é a soma das margens, por que `RANKX` no
total dá 1, e por que somar percentuais dá 350%. Tudo isso é a mesma coisa vista de
ângulos diferentes.

Há **dois** tipos de contexto — filtro e linha — e uma operação que converte um no outro.
São o assunto de [`16-dax-contexto-de-avaliacao.md`](16-dax-contexto-de-avaliacao.md).

---

## 6. Relacionamento e propagação de filtro

> **Relacionamento** — uma ligação entre duas tabelas por uma coluna, que faz o filtro de
> uma **propagar** para a outra.

Anatomia:

```
   dProduto                                fVendas
┌──────────────┐                      ┌──────────────┐
│ SK_Produto   │ 1 ──────────────► *  │ SK_Produto   │
│ Produto      │      cardinalidade   │ Quantidade   │
│ Categoria    │      1 para muitos   │ Valor        │
└──────────────┘                      └──────────────┘
        │                                     ▲
        └── direção do filtro ────────────────┘
            (da dimensão para o fato)
```

Três propriedades definem cada relacionamento:

| Propriedade | Valores | O padrão certo |
|---|---|---|
| **Cardinalidade** | 1:*, *:1, 1:1, *:* | **1:*** (dimensão para fato) |
| **Direção do filtro** | única, ambas | **única** |
| **Ativa** | sim, não | ativa (a inativa se liga com `USERELATIONSHIP`) |

**O filtro desce, nunca sobe** (com direção única). Filtrar `Categoria = "Tintas"` em
`dProduto` filtra `fVendas`. Filtrar `fVendas` **não** filtra `dProduto`.

Isso é intencional e é a razão de o modelo em estrela funcionar. Filtro bidirecional
inverte isso e é a causa nº 1 de ambiguidade — ver
[`14-modelagem-dimensional.md`](14-modelagem-dimensional.md) §7.

---

## 7. Chave técnica × chave de negócio

> **Chave de negócio** (*natural key*) — identifica a entidade no mundo real: CNPJ, código
> de produto, matrícula.
>
> **Chave substituta** (*surrogate key*, `SK_`) — um inteiro sequencial sem significado,
> criado só para o modelo.

Por que usar substituta:

1. **Compressão.** Um inteiro de 3 dígitos comprime radicalmente melhor que
   `"12.345.678/0001-95"` repetido 60 mil vezes. O ganho é medido em
   [`21`](21-vertipaq-por-dentro.md).
2. **Estabilidade.** CNPJ muda (fusão, incorporação); código de produto é reaproveitado.
3. **Dimensões que mudam lentamente** (SCD tipo 2) só funcionam com chave substituta:
   duas versões do mesmo cliente, dois `SK`, o mesmo CNPJ.

**Armadilha real, presente no projeto-modelo:** com SCD tipo 2 ou recadastro, o mesmo
CNPJ tem duas `SK`. `DISTINCTCOUNT(SK_Cliente)` **infla** a contagem de clientes.
Conte a chave de negócio. Ver [`07-projeto-modelo/`](07-projeto-modelo/README.md), defeito 2.

---

## 8. Cardinalidade — a palavra com dois sentidos

Cuidado: no Power BI, "cardinalidade" quer dizer duas coisas.

**Sentido 1 — cardinalidade do relacionamento**: 1:*, *:1, 1:1, *:*.

**Sentido 2 — cardinalidade de uma coluna**: quantos **valores distintos** ela tem.

O sentido 2 é o que determina o tamanho e a velocidade do modelo. Regra empírica confiável:

> O tamanho de uma coluna no VertiPaq é governado pela **cardinalidade**, não pelo número
> de linhas.

| Coluna | Linhas | Distintos | Tamanho |
|---|---|---|---|
| `Categoria` | 60.621 | 7 | minúsculo |
| `SK_Produto` | 60.621 | 26 | minúsculo |
| `Data` | 60.621 | ~950 | pequeno |
| `NF` | 60.621 | 24.784 | grande |
| `PrecoUnitario` | 60.621 | ~40.000 | **enorme** |
| `Timestamp` com segundos | 60.621 | 60.621 | **catastrófico** |

**Consequência prática nº 1:** separe data e hora em duas colunas. Uma coluna
`DataHora` com segundos tem cardinalidade igual ao número de linhas — o pior caso
possível. Separada em `Data` (1.096 distintos) + `Hora` (86.400 distintos, ou 1.440 se
truncada em minutos), o modelo encolhe drasticamente.

**Consequência prática nº 2:** arredonde valores decimais para a precisão que o negócio
realmente usa. `315,0000001` e `315,00` custam o mesmo espaço na tela e ordens de
grandeza diferentes na memória.

---

## 9. Esquema estrela — o formato canônico

> **Esquema estrela** (*star schema*) — um fato central cercado por dimensões, cada uma a
> **um** relacionamento de distância.

```
              dCalendario
                   │
                   ▼
  dProduto ──►  fVendas  ◄── dCliente
                   ▲
                   │
              dVendedor
```

> **Floco de neve** (*snowflake*) — dimensões normalizadas em cadeia:
> `fVendas → dProduto → dCategoria → dDepartamento`.

**Recomendação profissional, e é consenso do campo:** use **estrela**, achate o floco.
O motivo não é estético:

1. O motor VertiPaq foi otimizado para estrela; consultas em estrela usam caminhos rápidos
   internos.
2. Cada salto adicional é mais uma propagação de filtro em tempo de consulta.
3. O usuário final entende estrela; ninguém entende floco.
4. A economia de espaço do floco é irrelevante — dimensões são pequenas, e o VertiPaq
   já comprime a repetição.

**Quando o floco se justifica:** dimensões gigantescas (milhões de linhas) com atributos
muito repetidos, ou quando a dimensão vem pronta e normalizada de um data warehouse
corporativo e replicar seria pior. É exceção, não regra.

---

## 10. Modelo semântico

> **Modelo semântico** (*semantic model*) — o pacote completo: tabelas + relacionamentos +
> medidas + hierarquias + formatos + segurança. Antes de 2023 chamava-se **dataset**
> (conjunto de dados).

O nome não é marketing: o modelo carrega **semântica**, ou seja, o significado dos dados.
Ele responde:

- *o que* é faturamento nesta empresa (deduz frete? inclui devolução?);
- *como* produto se relaciona com venda;
- *quem* pode ver o quê;
- *como* o número é formatado e nomeado.

**Por que isso importa mais do que parece:** um modelo semântico bem-feito é reutilizável.
Vários relatórios, o Excel, o Copilot, uma API e um notebook Python consomem **as mesmas
definições**. Sem ele, cada relatório redefine "faturamento" à sua maneira, e a empresa
passa a ter cinco números para a mesma pergunta.

Isso é o que se chama, na indústria, de **camada semântica** — e é a maior fonte de valor
duradouro do Power BI. Ver [`23`](23-servico-colaboracao-e-atualizacao.md) e
[`65`](65-estado-da-arte.md).

---

## 11. As três linguagens

Power BI usa **três** linguagens diferentes, e confundi-las é um clássico.

| | **M** (Power Query) | **DAX** | **SQL** |
|---|---|---|---|
| Onde vive | Editor do Power Query | Medidas, colunas, tabelas | Na fonte |
| Quando roda | **No refresh** | **Na consulta** | No refresh (se dobrar) |
| Paradigma | funcional, tipado, *case-sensitive* | funcional, expressões | declarativo |
| Serve para | **preparar** o dado | **analisar** o dado | ambos, na origem |
| Exemplo | `Table.SelectRows(t, each [x] > 5)` | `CALCULATE([Vendas], dProd[Cat]="Tintas")` | `SELECT ... WHERE` |
| Resultado | uma tabela | um valor escalar ou tabela | uma tabela |

**A regra de ouro sobre onde fazer cada coisa** — e ela é opinião forte, mas amplamente
compartilhada no campo:

> Faça o mais **à esquerda** possível: primeiro na fonte (SQL/view), depois no Power Query
> (M), e só então no modelo (DAX).

Motivos: a fonte tem índices e paralelismo; o M roda uma vez por refresh; o DAX roda a
cada clique de cada usuário. Uma transformação que custa 1 segundo no refresh e é usada
por 200 pessoas custa 200 segundos por dia se estiver em DAX.

**Exceção legítima:** cálculos que **dependem do contexto de filtro** só existem em DAX.
Nenhum SQL calcula "% do total visível no visual".

---

## 12. Modos de armazenamento — visão de sobrevoo

> **Import** — os dados são copiados e comprimidos na memória do Power BI.
> **DirectQuery** — nada é copiado; cada visual dispara uma consulta na fonte.
> **Direct Lake** — os dados ficam em Parquet/Delta no OneLake e são carregados em memória
> sob demanda, sem cópia prévia.
> **Dual** — a tabela é Import e DirectQuery ao mesmo tempo; o motor escolhe.
> **Composto** — tabelas em modos diferentes no mesmo modelo.

| | Import | DirectQuery | Direct Lake |
|---|---|---|---|
| Velocidade | ★★★★★ | ★★ | ★★★★ |
| Atualidade do dado | do último refresh | tempo real | quase tempo real |
| Volume suportado | limitado pela RAM | ilimitado | muito grande |
| Recursos de DAX | todos | limitados | quase todos |
| Complexidade | baixa | alta | média |
| Exige | — | fonte rápida | Fabric + OneLake |

**Recomendação:** comece com **Import**. Vá para DirectQuery quando não couber em memória
ou quando o requisito de tempo real for **real** (e ele quase nunca é). O capítulo
[`20-modos-de-armazenamento.md`](20-modos-de-armazenamento.md) trata a decisão a fundo.

---

## 13. Vocabulário do dia a dia

| Termo | Definição curta |
|---|---|
| **Workspace** | Pasta colaborativa no Service; contém modelos, relatórios, apps |
| **Relatório** | Conjunto de páginas com visuais, sobre um modelo semântico |
| **Painel** (*dashboard*) | Mural de blocos fixados de vários relatórios (recurso legado) |
| **App / org app** | Empacotamento de relatórios para distribuição, com audiências |
| **Segmentação** (*slicer*) | Visual de filtro operado pelo usuário |
| **Indicador** (*bookmark*) | Estado salvo da página (filtros + visibilidade) |
| **Drillthrough** | Navegar para outra página levando o contexto do clique |
| **Drill down** | Descer numa hierarquia dentro do mesmo visual |
| **Cross-highlight** | Clicar num visual destaca a parcela correspondente nos outros |
| **Gateway** | Serviço que dá à nuvem acesso a dados que estão on-premises |
| **Capacidade** | Recurso computacional dedicado (F-SKU) que hospeda conteúdo |
| **RLS / OLS** | Segurança em nível de linha / de objeto |
| **Refresh** | Atualização dos dados do modelo a partir das fontes |
| **PBIP / TMDL** | Formatos de texto do projeto e do modelo, versionáveis em Git |
| **XMLA endpoint** | Interface que expõe o modelo publicado como um servidor Analysis Services |

Glossário completo em [`GLOSSARIO.md`](GLOSSARIO.md).

---

## 14. Os cinco porquês: por que existe uma linguagem própria (DAX)?

1. **Por que não usar SQL para as medidas?**
   Porque SQL não conhece o conceito de "contexto do visual". Uma consulta SQL é escrita
   com seus filtros dentro; uma medida DAX é escrita **sem** filtros e recebe filtros de
   fora, diferentes a cada célula.

2. **Por que isso é necessário?**
   Porque o modelo de interação é o inverso do relatório tradicional. No relatório
   tradicional, alguém escreve uma consulta por número. Num relatório interativo, **o
   usuário compõe filtros em tempo de execução**, e a mesma expressão precisa valer para
   qualquer combinação. Isso exige uma linguagem em que o filtro seja *ambiente*, não
   argumento.

3. **Por que não estender o SQL para isso?**
   Foi tentado (MDX, em 1997, para cubos OLAP). MDX é mais poderoso e muito mais difícil.
   O DAX nasceu em 2009 com um objetivo declarado de produto: ser **aprendível por quem
   sabe Excel**. Daí a sintaxe de funções com vírgulas, `IF`, `SUM`, e a ausência de
   `SELECT`.

4. **Por que a facilidade era prioridade sobre o poder?**
   **Decisão histórica documentada.** O PowerPivot (2009) foi construído para
   *self-service BI*: tirar o BI do departamento de TI e colocá-lo no analista de negócio.
   O público-alvo era o usuário de Excel, e a linguagem foi desenhada para ele. Amir Netz
   e a equipe do Analysis Services descreveram isso publicamente à época.

5. **Parada legítima — trade-off de produto assumido.**
   O resultado é uma linguagem enganosamente fácil: a sintaxe é acolhedora, a semântica é
   profunda. É por isso que tanta gente escreve DAX errado com confiança. A curva não é
   suave: ela é plana por 40 horas e depois vertical, no contexto de avaliação.
   **Opinião do autor:** essa descontinuidade é o maior defeito de projeto do DAX, e é o
   preço que se pagou pela adoção em massa. Valeu a pena para a Microsoft; custa caro a
   cada analista, individualmente.

---

## 15. Modelos mentais que vale carregar

**1. O modelo é uma despensa; a medida é uma receita; o visual é o prato.**
Organizar a despensa é o trabalho invisível que decide tudo.

**2. Filtro flui morro abaixo, da dimensão para o fato.**
Quando um número não muda ao filtrar, pergunte primeiro: o filtro chegou lá?

**3. Todo número tem um contexto. Nenhum número existe sozinho.**
"Faturamento = 1 milhão" é meia informação. De quando? De quem? Do quê?

**4. O total não é a soma das linhas.**
Guarde isso. Vai salvar horas.

**5. Cardinalidade é o preço.**
Quando o modelo estiver grande ou lento, procure a coluna de maior cardinalidade antes de
qualquer outra coisa.

**6. Faça o mais à esquerda possível.**
Fonte > Power Query > DAX. Nessa ordem.

**7. Se você não consegue explicar a medida em uma frase de português, ela está errada
ou o modelo está.**

---

## 16. Autoteste

1. Dê o teste de dois segundos para distinguir fato de dimensão.
2. Complete: "nesta tabela de fatos, uma linha é ______". Por que essa frase importa?
3. Quando usar coluna calculada e quando usar medida? Dê a regra em uma frase.
4. Por que o total de uma matriz não é a soma das linhas?
5. Numa relação `dProduto` 1—* `fVendas` com direção única, filtrar `fVendas` filtra
   `dProduto`? Por quê?
6. Explique a diferença entre chave de negócio e chave substituta, e cite um problema real
   causado por confundi-las.
7. Qual dos dois sentidos de "cardinalidade" determina o tamanho do modelo?
8. Por que separar `DataHora` em `Data` + `Hora`?
9. Ordene M, DAX e SQL por "quando executam" e diga onde fazer uma transformação e por quê.
10. Por que o DAX foi desenhado para parecer com Excel, e qual foi o custo dessa decisão?

---

**Próximo:** [`11-historia.md`](11-historia.md) — como chegamos até aqui.
