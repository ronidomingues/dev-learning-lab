# Glossário

**Data:** 14/08/2026

Todos os termos técnicos usados neste curso. Termos em inglês aparecem como o campo os
usa, com a tradução ao lado. Ordem alfabética; use `Ctrl+F`.

---

## A

**Agregação (tabela de)** — tabela pequena pré-agregada que o motor usa automaticamente
quando a consulta não precisa do detalhe. Só funciona para agregações **decomponíveis**
(soma, contagem, mín, máx). Ver [`20`](20-modos-de-armazenamento.md) §7.

**Aditiva (medida)** — que pode ser somada em **todas** as dimensões (quantidade, valor).
Ver **semiaditiva** e **não aditiva**.

**ALLSELECTED** — modificador de filtro que remove os filtros vindos dos eixos do visual e
**preserva** os externos (segmentações). É a escolha certa para "% do total visível".

**ALM Toolkit** — ferramenta gratuita que compara e mescla modelos semânticos.

**Ambiguidade** — situação em que existe mais de um caminho de propagação de filtro entre
duas tabelas. Causada por filtro bidirecional. Ver [`60`](60-teoria-avancada.md) §2.

**Analysis Services (AS)** — o motor tabular da Microsoft. Roda dentro do Power BI Desktop
como `msmdsrv.exe` e na nuvem, sob o Service.

**App / aplicativo organizacional (*org app*)** — empacotamento de conteúdo para
distribuição, com **audiências** distintas. GA em julho/2026.

**AppSource** — loja de visuais customizados e aplicativos.

**Atualização incremental** — política que atualiza apenas as partições recentes.
Exige `RangeStart`/`RangeEnd` e *query folding*.

**Audiência** — subconjunto de conteúdo de um org app entregue a um grupo específico.

---

## B

**Best Practice Analyzer (BPA)** — analisador de boas práticas do Tabular Editor. Roda
dezenas de regras e aponta antipadrões. A ferramenta de qualidade com melhor retorno.

**Bidirecional (filtro)** — direção de filtro que propaga nos dois sentidos. Causa
ambiguidade; usar apenas com justificativa escrita.

**BLANK** — valor "vazio" do DAX. Não é `NULL` nem zero, mas `BLANK() = 0` devolve
verdadeiro. Ver [`15`](15-dax-fundamentos.md) §2.5.

**BI (Business Intelligence)** — práticas e ferramentas para transformar dados brutos em
informação confiável para decisão. Termo de Hans Peter Luhn, 1958.

**Bookmark** — ver **Indicador**.

**Bravo for Power BI** — ferramenta gratuita que analisa o modelo, formata DAX e gera
tabela de datas.

**Bridge (tabela ponte)** — tabela intermediária que resolve relacionamentos
muitos-para-muitos legítimos.

---

## C

**CALCULATE** — a função central do DAX. Modifica o contexto de filtro e dispara a
**transição de contexto**. **Substitui** filtros nas mesmas colunas, salvo `KEEPFILTERS`.

**CallbackDataID** — marcador nas consultas internas indicando que o motor de armazenamento
chamou o motor de fórmula linha a linha. Sinal de problema de desempenho.

**Camada semântica** — conjunto de definições oficiais (medidas, relacionamentos,
segurança) consumido por vários relatórios e ferramentas. Ver [`23`](23-servico-colaboracao-e-atualizacao.md) §2.

**Capacidade** — recurso computacional dedicado (F-SKU no Fabric) que hospeda conteúdo.

**Cardinalidade** — **(1)** do relacionamento: 1:*, *:1, 1:1, *:*. **(2)** de uma coluna:
número de valores distintos. O sentido (2) governa o tamanho e a velocidade do modelo.

**Certificado / Promovido** — níveis de endosso de um item no Service.

**Chave de negócio (*natural key*)** — identificador do mundo real: CNPJ, código de produto.

**Chave substituta (*surrogate key*, `SK_`)** — inteiro sequencial sem significado, criado
para o modelo. Comprime melhor e é estável.

**Coluna calculada** — coluna criada em DAX, avaliada **linha a linha no refresh** e
armazenada. Ocupa memória.

**Composto (modelo)** — modelo com tabelas em modos de armazenamento diferentes, ou que
estende um modelo semântico publicado.

**CONCATENATEX** — função que concatena valores de uma tabela; útil como `print()` para
depurar contexto.

**Contexto de avaliação** — conjunto de filtros ativos quando uma medida é calculada.
Divide-se em contexto de **filtro** e contexto de **linha**.

**Contexto de filtro** — conjunto de filtros sobre colunas. Propaga por relacionamento.

**Contexto de linha** — noção de "linha atual". Criado por colunas calculadas e
iteradores. **Não filtra nada.**

**Copilot** — assistente de IA integrado ao Power BI e ao Fabric.

**CROSSFILTER** — função que altera a direção de filtro de um relacionamento **apenas
dentro** de um `CALCULATE`. Alternativa segura ao bidirecional permanente.

**Cross-highlight** — comportamento em que clicar num visual destaca a parcela
correspondente nos outros, preservando o total.

**CU (*Capacity Unit*)** — unidade de consumo de capacidade do Fabric.

---

## D

**Dashboard (painel)** — no Power BI, um mural de blocos fixados de vários relatórios.
Recurso legado; a prática atual usa relatórios e org apps.

**Dataflow** — Power Query executado na nuvem, reutilizável por vários modelos. Gen1
(Power BI) e Gen2 (Fabric).

**Dataset** — nome antigo de **modelo semântico**. Renomeado em 2023.

**DAX (*Data Analysis Expressions*)** — linguagem de cálculo do modelo tabular. Criada em
2009 com o PowerPivot.

**DAX Studio** — ferramenta gratuita para consultar DAX, medir tempos, ver plano de
consulta e rodar o VertiPaq Analyzer.

**Delta Lake** — formato de tabela transacional sobre Parquet, usado pelo OneLake.
Licença Apache 2.0.

**Dicionário (*dictionary*)** — estrutura que mapeia índices para valores numa coluna
codificada por hash. Cresce com a **cardinalidade**.

**Dimensão** — tabela que descreve o contexto dos eventos (produto, cliente, data).
Cresce devagar; contém texto e atributos.

**Dimensão degenerada** — identificador de transação que fica na própria tabela de fatos
(ex.: número da nota fiscal).

**Direct Lake** — modo de armazenamento que lê arquivos Delta Parquet do OneLake
diretamente para a memória, sem cópia prévia nem consulta SQL.

**DirectQuery** — modo em que os dados permanecem na fonte e cada visual dispara uma
consulta.

**DISTINCTCOUNT** — contagem de valores distintos. Agregação **não decomponível**, e a
mais cara.

**DIVIDE** — divisão segura; devolve `BLANK` (ou um valor alternativo) em vez de erro
quando o denominador é zero. Use sempre.

**Drill down** — descer numa hierarquia dentro do mesmo visual.

**Drillthrough** — navegar para outra página levando o contexto do clique.

**Dual** — modo de armazenamento em que a tabela é Import **e** DirectQuery; o motor
escolhe por consulta.

---

## E

**EARLIER** — função obsoleta para acessar um contexto de linha externo. Substituída por
`VAR`. Ainda funciona por compatibilidade retroativa.

**Embedded** — modalidade para embutir relatórios em aplicações próprias.

**Endosso** — marcação de confiança de um item: *Promovido* ou *Certificado*.

**Entropia (de Shannon)** — limite teórico inferior da compressão sem perda. Explica por
que alta cardinalidade é cara por teorema. Ver [`60`](60-teoria-avancada.md) §5.

**Estrela (esquema)** — fato central cercado por dimensões, cada uma a um relacionamento
de distância. O formato canônico.

---

## F

**Fabric (Microsoft Fabric)** — plataforma SaaS que reúne Power BI, engenharia de dados,
ciência de dados e tempo real sob uma capacidade e um armazenamento (OneLake).

**Fabric IQ** — camada de contexto compartilhado sobre dados do OneLake, voltada a agentes.
Anunciada no Build 2026.

**Fallback (Direct Lake)** — queda automática para DirectQuery quando algo não é suportado
no Direct Lake. Precisa ser monitorado.

**Fato (tabela de)** — tabela que registra eventos, com medidas numéricas e chaves. Cresce
sem parar.

**FE (*Formula Engine*, motor de fórmula)** — parte do motor que executa a lógica do DAX.
**Sequencial e lento.** Ver **SE**.

**Field parameter** — ver **Parâmetro de campo**.

**Formula Firewall** — proteção do Power Query que impede o envio de dados de uma fonte
privada para outra fonte.

**F-SKU** — SKUs de capacidade do Fabric (F2, F4, …, F64, …). Substituíram os P-SKU.

---

## G

**Gateway (*on-premises data gateway*)** — serviço que dá à nuvem acesso a dados que estão
na rede da empresa. Faz conexões **de saída**; não exige abrir porta de entrada.

**Granularidade (*grain*)** — o que **uma linha** da tabela de fatos representa. A primeira
pergunta de qualquer modelagem.

**Grupo de cálculo (*calculation group*)** — dimensão especial cujos membros são
modificações aplicáveis a **qualquer** medida. Elimina a explosão de medidas repetidas.

---

## H

**Hash encoding** — codificação por dicionário: guarda índices em vez dos valores.

**Hierarchy (estrutura de atributo)** — estrutura interna por coluna que permite agrupar e
ordenar. Custo escondido em colunas de alta cardinalidade.

---

## I

**Import** — modo de armazenamento em que os dados são copiados e comprimidos na memória
do modelo. O padrão, e a resposta certa na maioria dos casos.

**Indicador (*bookmark*)** — estado salvo de uma página: filtros, seleções, visibilidade.

**isAvailableInMdx** — propriedade de coluna que, desativada, remove a estrutura de
atributo. Economiza memória em chaves técnicas ocultas.

**Iterador** — função com sufixo `X` (`SUMX`, `AVERAGEX`, `FILTER`, `RANKX`) que percorre
uma tabela criando contexto de linha.

---

## K

**KEEPFILTERS** — modificador que faz `CALCULATE` **intersectar** em vez de substituir.

**Kimball, Ralph** — autor de *The Data Warehouse Toolkit* (1996) e popularizador da
modelagem dimensional.

---

## L

**Lakehouse** — item do Fabric que combina arquivos e tabelas Delta, com endpoint SQL de
leitura.

**Live connection (conexão dinâmica)** — relatório que consulta um modelo semântico
publicado, sem dados próprios.

---

## M

**M (linguagem)** — linguagem funcional do Power Query. *Case-sensitive*, tipada,
avaliação preguiçosa. Executa no **refresh**.

**Mashup Engine** — motor que executa o código M.

**Medida (*measure*)** — expressão DAX avaliada **na hora da consulta**, no contexto do
visual. Não ocupa memória. Não pode ir no eixo.

**Membro desconhecido** — linha explícita na dimensão (ex.: "(sem cadastro)") que recebe as
chaves órfãs do fato, evitando que as linhas sumam.

**Modelo semântico** — o pacote completo: tabelas, relacionamentos, medidas, hierarquias,
formatos e segurança. Antigo "dataset".

---

## N

**Não aditiva (medida)** — que não pode ser somada em nenhuma dimensão (percentual, razão,
pH). Nunca armazene o resultado; armazene os componentes.

---

## O

**OLAP (*Online Analytical Processing*)** — processamento analítico: agregar milhões de
linhas. Contrapõe-se a OLTP.

**OLS (*Object-Level Security*)** — segurança que esconde tabelas ou colunas inteiras de
determinados perfis. Configurada via Tabular Editor ou XMLA.

**OLTP (*Online Transaction Processing*)** — processamento transacional: ler e gravar uma
linha por vez.

**OneLake** — data lake único por locatário no Fabric, em Delta Parquet.

**Ontologia (Fabric IQ)** — extensão do modelo semântico com entidades de negócio, regras,
ações e sinais em tempo real. GA prevista após o Build 2026.

---

## P

**Paginated report (relatório paginado)** — relatório de página fixa, feito no Power BI
Report Builder, em formato RDL. Para faturas, boletos e documentos.

**Parâmetro (Power Query)** — valor nomeado usado em vez de caminho ou servidor fixo.
Alterável no Service sem republicar.

**Parâmetro de campo (*field parameter*)** — tabela que permite ao **usuário** escolher qual
medida ou qual dimensão o visual mostra.

**Parquet** — formato colunar comprimido, base do Delta Lake. Apache 2.0.

**Pareto (curva ABC)** — classificação por concentração: classe A até 80% acumulados,
B até 95%, C o restante.

**Partição** — subdivisão de uma tabela do modelo, usada em atualização incremental e em
refresh seletivo via XMLA.

**PBIP (*Power BI Project*)** — formato de projeto em pasta com arquivos de **texto**,
versionável em Git.

**PBIR** — formato de texto da definição do **relatório**, dentro do PBIP.

**PBIX** — arquivo binário do Power BI Desktop, contendo relatório, modelo e dados.

**Pipeline de implantação** — mecanismo do Service que promove conteúdo entre
Desenvolvimento, Teste e Produção, com regras de troca de parâmetros.

**PowerPivot** — suplemento do Excel lançado em 2009, com o VertiPaq e o DAX. A origem do
Power BI.

**Power Query** — motor de ETL do Power BI, baseado na linguagem M.

**PPU (*Premium Per User*)** — licença por usuário com recursos de capacidade.

**Publicar na Web** — recurso que torna um relatório **público na internet, sem login**.
Maior fonte de vazamento; deve ser desabilitado no locatário.

---

## Q

**Q&A (Perguntas e Respostas)** — consulta ao modelo em linguagem natural. Sua qualidade
mede a qualidade da nomenclatura do modelo.

**Query folding (dobramento)** — tradução dos passos do Power Query numa consulta nativa
executada pela fonte. Verificável em "Exibir Consulta Nativa".

---

## R

**RangeStart / RangeEnd** — parâmetros de **nome obrigatório** para atualização incremental.

**Refresh (atualização)** — carga dos dados da fonte para o modelo.

**RELATED / RELATEDTABLE** — funções que atravessam relacionamentos dentro de um contexto
de linha (para o lado 1 e para o lado *, respectivamente).

**REMOVEFILTERS** — sinônimo mais legível de `ALL` quando usado como modificador de filtro.

**Report Server (Power BI Report Server)** — servidor instalado na empresa, sem nuvem.
Exige uma versão específica do Desktop.

**RLE (*Run-Length Encoding*)** — compressão de sequências repetidas em pares
(valor, contagem). Depende da ordem das linhas.

**RLS (*Row-Level Security*)** — segurança em nível de linha. Aplica-se apenas a
**Visualizadores**; não protege o arquivo `.pbix`.

---

## S

**SCD (*Slowly Changing Dimension*)** — dimensão que muda com o tempo. Tipo 1 sobrescreve;
tipo 2 cria nova linha com vigência.

**SE (*Storage Engine*, motor de armazenamento)** — parte do motor que varre e agrega
colunas comprimidas. **Paralelo e rápido.** Ver **FE**.

**Segmentação (*slicer*)** — visual de filtro operado pelo usuário.

**Segmentação dinâmica** — padrão em que uma tabela desconectada com rótulos é combinada
com uma medida que classifica. Necessário porque medidas não filtram.

**SELECTEDVALUE** — devolve o valor único da coluna no contexto, ou uma alternativa.

**Semiaditiva (medida)** — soma em todas as dimensões **exceto tempo** (estoque, saldo).
Use o último valor do período.

**Sensitivity label (rótulo de confidencialidade)** — marcação do Microsoft Purview,
herdada por arquivos exportados. A única proteção que vale fora do Power BI.

**SUMMARIZECOLUMNS** — função de tabela usada pelas consultas geradas pelos visuais.

---

## T

**Tabela calculada** — tabela criada em DAX, materializada no refresh.

**Tabela de datas** — dimensão de tempo contínua, cobrindo anos civis inteiros, marcada
como tabela de data. Pré-requisito da inteligência de tempo.

**Tabular Editor** — ferramenta externa para editar o modelo. A versão 2 é gratuita e de
código aberto; a 3 é comercial.

**Throttling** — degradação imposta quando uma capacidade excede o consumo permitido.
Sintoma: "ficou tudo lento e ninguém mudou nada".

**TMDL (*Tabular Model Definition Language*)** — linguagem de texto que descreve o modelo
semântico. Base do versionamento em Git.

**TMSL** — a variante JSON, usada em operações XMLA.

**TOPN** — devolve as N primeiras linhas por uma expressão. Não resolve empates.

**Transição de contexto** — conversão de contexto de linha em contexto de filtro,
disparada por `CALCULATE` (inclusive o implícito em medidas dentro de iteradores).

**TREATAS** — aplica valores de uma tabela como filtro em outra coluna, sem relacionamento.

---

## U

**UDF (*User-Defined Function*) em DAX** — função definida pelo usuário. **GA em
junho/2026**, com parâmetros opcionais e dicas de tipo.

**USERELATIONSHIP** — ativa uma relação inativa dentro de um `CALCULATE`.

**USERPRINCIPALNAME** — devolve o UPN de quem consulta o modelo. Base da RLS dinâmica.

---

## V

**VALUES / DISTINCT** — devolvem os valores distintos visíveis de uma coluna. `VALUES`
inclui a linha em branco de integridade referencial; `DISTINCT`, não.

**VAR** — declaração de variável em DAX. Avaliada **uma vez**, no contexto onde foi
declarada. Não é opcional: muda a semântica, não só o desempenho.

**Value encoding** — codificação que guarda a diferença em relação a um valor base, com o
mínimo de bits. Sem indireção; a mais rápida.

**VertiPaq** — o motor colunar em memória do modelo tabular. Criado em 2009.

**VertiPaq Analyzer** — ferramenta (embutida no DAX Studio) que mostra tamanho e
cardinalidade por coluna. A base de qualquer otimização de modelo.

**Visual calculation (cálculo visual)** — DAX escrito dentro do visual, operando sobre a
matriz já calculada. Funções como `PREVIOUS`, `RUNNINGSUM`, `COLLAPSEALL`, `LOOKUP`.

---

## W

**Warehouse (Fabric)** — data warehouse SQL completo dentro do Fabric, com T-SQL e
transações.

**WebView2** — runtime Chromium usado pelo Power BI Desktop para renderizar visuais e
diálogos. Sua ausência causa telas em branco.

**Workspace** — unidade de organização e colaboração no Service. Tem funções: Admin,
Membro, Colaborador, Visualizador.

---

## X

**XMLA endpoint** — interface que expõe o modelo semântico publicado como um servidor
Analysis Services. Permite SSMS, Tabular Editor, refresh por partição e CI/CD. Exige
capacidade (PPU ou F-SKU).

---

## Y

**YTD (*Year to Date*)** — acumulado do ano até a data. `DATESYTD` / `TOTALYTD`.

---

## Siglas rápidas

| Sigla | Significado |
|---|---|
| **ABC** | Classificação por concentração (Pareto) |
| **BI** | Business Intelligence |
| **BPA** | Best Practice Analyzer |
| **CU** | Capacity Unit |
| **DAX** | Data Analysis Expressions |
| **ETL** | Extract, Transform, Load |
| **FE / SE** | Formula Engine / Storage Engine |
| **GA** | General Availability (disponibilidade geral) |
| **MAT** | Moving Annual Total (acumulado móvel de 12 meses) |
| **MDX** | Multidimensional Expressions |
| **OEE** | Overall Equipment Effectiveness |
| **OLS / RLS** | Object-Level / Row-Level Security |
| **OLTP / OLAP** | Transacional / Analítico |
| **PBIP / PBIR / PBIX / PBIT** | Formatos de projeto, relatório, arquivo e template |
| **PPU** | Premium Per User |
| **RDL** | Report Definition Language |
| **RFM** | Recência, Frequência, Valor monetário |
| **RLE** | Run-Length Encoding |
| **SCD** | Slowly Changing Dimension |
| **SK** | Surrogate Key (chave substituta) |
| **SKU** | Stock Keeping Unit (aqui, o tamanho da capacidade) |
| **TMDL / TMSL** | Tabular Model Definition / Scripting Language |
| **UDF** | User-Defined Function |
| **UPN** | User Principal Name |
| **XMLA** | XML for Analysis |
| **YTD / QTD / MTD** | Year / Quarter / Month to Date |
