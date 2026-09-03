# 90 · Bibliografia comentada

**Nível:** todos
**Data da consulta: 14/08/2026**

> **Política deste arquivo.** Não invento livro, edição, ISBN nem tradução. Onde eu não
> tenho certeza da existência de uma edição brasileira ou de um número de ISBN, **eu digo
> que não tenho** e recomendo conferir na editora. Um ISBN inventado é pior que nenhum.
>
> Marquei com **[GRÁTIS]** o que é **legalmente** gratuito — liberado pelo autor, em
> domínio público, ou com versão aberta oficial.

---

## 1. Os quatro essenciais

Se você comprar apenas quatro livros na vida para trabalhar com Power BI, são estes.

### 1.1 Russo, Marco; Ferrari, Alberto. **The Definitive Guide to DAX**. Microsoft Press, **3ª edição**.

**Subtítulo da 3ª edição:** *Mastering the semantic model expression language for Microsoft
Power BI, Fabric, and Excel*.

**Nível:** intermediário a pesquisa · **~700+ páginas**

**O que faz melhor que todos os outros:** explica **contexto de avaliação** com uma
profundidade e um rigor que não existem em nenhum outro lugar — nem em curso, nem em blog,
nem em documentação. Os capítulos sobre contexto de linha, contexto de filtro, transição
de contexto e `CALCULATE` são o material definitivo do campo.

**A 3ª edição** é descrita pelos próprios autores como um livro praticamente novo, com
pouco reaproveitamento da 2ª. Cobre recursos recentes, incluindo **inteligência de tempo
baseada em calendário** e **funções definidas pelo usuário (UDF)** — o que a torna a
edição relevante depois da GA das UDFs em junho de 2026.

**A 2ª edição (2019)** continua excelente e cobre 90% do que você usa no dia a dia. Se você
a encontrar barata, ela **não envelheceu** nos fundamentos — só não tem os recursos novos.

**Como ler:** não do começo ao fim. Leia os capítulos 1 a 5, depois pare e pratique um mês.
Volte para os capítulos de contexto de avaliação. Depois pratique outro mês. É um livro
para três leituras ao longo de dois anos, não para uma maratona.

**Edição em português:** **não tenho confirmação** de tradução brasileira. Confirme com a
editora.

---

### 1.2 Kimball, Ralph; Ross, Margy. **The Data Warehouse Toolkit: The Definitive Guide to Dimensional Modeling**. Wiley, **3ª edição, 2013**.

**Nível:** intermediário · **~600 páginas**

**Por que um livro de 2013 continua obrigatório:** porque modelagem dimensional é
**independente de ferramenta e de época**. Esquema estrela, granularidade, SCD, fatos
semiaditivos, dimensões degeneradas, fatos de granularidade mista — tudo o que
[`14-modelagem-dimensional.md`](14-modelagem-dimensional.md) resume vem daqui, com muito
mais profundidade e com estudos de caso por setor (varejo, estoque, financeiro, saúde,
telecom, educação).

**Envelheceu?** As partes sobre ETL e infraestrutura, sim. **O núcleo conceitual, não.**
É o livro mais atemporal desta lista.

**Como ler:** os capítulos 1 a 3 são obrigatórios. Depois, leia o capítulo do **seu setor**
e ignore os demais até precisar.

**Edição em português:** existem edições brasileiras de **edições anteriores** publicadas
no Brasil. **Não tenho confirmação** de que a 3ª edição tenha tradução. Confirme na editora
antes de comprar esperando português.

---

### 1.3 Russo, Marco; Ferrari, Alberto. **Optimizing DAX**. SQLBI, **2ª edição, 2022**.

**Nível:** avançado a pesquisa

**O que faz melhor:** ensina a **medir** antes de otimizar. Motor de fórmula versus motor
de armazenamento, leitura de *server timings*, plano de consulta, `CallbackDataID`,
materialização, cache. É a fonte do método de [`22-desempenho.md`](22-desempenho.md).

**Pré-requisito real:** ter lido o *Definitive Guide* e ter sofrido com uma medida lenta em
produção. Sem essa dor, o livro parece abstrato.

**Envelheceu?** Os princípios, não. Alguns detalhes de ferramenta mudaram.

---

### 1.4 Knaflic, Cole Nussbaumer. **Storytelling with Data: A Data Visualization Guide for Business Professionals**. Wiley, **2015**.

**Nível:** iniciante a intermediário

**O que faz melhor:** é o livro mais **acionável** sobre comunicação visual. Não é teoria
da percepção — é "remova isto, destaque aquilo, ordene assim". Os exemplos de antes e
depois são o núcleo do valor.

**Edição em português:** **"Storytelling com Dados"**, publicado no Brasil pela **Alta
Books**. A tradução é adequada; alguns termos técnicos ficaram estranhos, mas não
comprometem.

**Limite honesto:** é raso em fundamentação teórica. Para o "por quê", vá para Cleveland,
Tufte ou Wilke (§3).

---

## 2. Power BI especificamente

### 2.1 Russo, Marco; Ferrari, Alberto. **Analyzing Data with Microsoft Power BI and Power Pivot for Excel**. Microsoft Press, **2017**.

**Nível:** iniciante a intermediário

**O que faz melhor:** é o melhor livro **de modelagem para quem usa Power BI**. Traduz
Kimball para o contexto do modelo tabular, com exemplos diretos.

**Envelheceu?** A interface, muito. **Os conceitos de modelagem, nada.** Ignore as capturas
de tela e leia o raciocínio.

**Opinião:** se você acha o Kimball intimidante, comece por este e volte ao Kimball depois.

---

### 2.2 Russo, Marco; Ferrari, Alberto. **Tabular Modeling in Microsoft SQL Server Analysis Services**. Microsoft Press, **2ª edição, 2017**.

**Nível:** avançado

**Para quem:** trabalha com o **endpoint XMLA**, Analysis Services, ou implantação
corporativa via ferramentas externas. É o modelo tabular por dentro, do ponto de vista de
quem administra.

**Envelheceu?** Sim, na superfície de produto. O núcleo (estrutura do modelo tabular,
processamento, partições) continua válido, e é a base para entender TMDL e XMLA.

---

### 2.3 Russo, Marco; Ferrari, Alberto. **DAX Patterns**. SQLBI, **2ª edição, 2020**.

**Nível:** intermediário a avançado

Catálogo de padrões prontos: inteligência de tempo, calendários personalizados, ABC,
segmentação dinâmica, análise de cesta, novos e recorrentes, orçamento.

**[GRÁTIS] — versão web:** o conteúdo dos padrões está disponível gratuitamente em
**`daxpatterns.com`**. O livro é a versão impressa e organizada do mesmo material.

**Como usar:** como referência, não como leitura. Quando precisar de um padrão, procure lá
antes de inventar.

---

### 2.4 Lachev, Teo. **Applied Microsoft Power BI**. Prologika.

**Nível:** iniciante a intermediário

Publicado em **edições anuais** — o autor relança o livro atualizado quase todo ano, o que
é raro e valioso num produto de cadência mensal.

**O que faz melhor:** cobre a **plataforma inteira**, incluindo administração, Report
Server, Embedded e governança — áreas que a maioria dos livros ignora.

**Verifique a edição** antes de comprar: uma edição de dois anos atrás já está defasada nas
partes de nuvem.

---

### 2.5 Livros brasileiros

Existem livros de Power BI publicados no Brasil, majoritariamente **introdutórios**.

**Minha avaliação honesta:** o mercado editorial brasileiro de Power BI é raso e envelhece
rápido, porque livro introdutório sobre ferramenta de cadência mensal fica desatualizado
antes de esgotar a primeira tiragem. **Para nível iniciante, prefira os cursos gratuitos
em vídeo de [`85-cursos-e-certificacoes.md`](85-cursos-e-certificacoes.md)**; para nível
intermediário e avançado, prefira os livros em inglês desta lista.

**Não listo títulos específicos porque não consegui verificar edições e disponibilidade
atuais na data desta consulta.** Se você conhece um bom, ele merece estar aqui.

---

## 3. Visualização de dados

### 3.1 Tufte, Edward. **The Visual Display of Quantitative Information**. Graphics Press, **2ª edição, 2001** (1ª de 1983).

**Nível:** todos

O livro fundador do campo. Introduz **razão dado-tinta**, *chartjunk* e o **fator de
mentira** (*lie factor*). É também um objeto bonito — Tufte edita os próprios livros com
cuidado tipográfico obsessivo.

**Envelheceu?** Os exemplos, sim (são anteriores à visualização digital). **A tese, não.**

**Ressalva:** Tufte é dogmático. Algumas de suas prescrições (eliminar toda grade, por
exemplo) foram questionadas por pesquisa posterior. Leia como filosofia, não como manual.

**Português:** não tenho confirmação de tradução brasileira.

---

### 3.2 Few, Stephen. **Show Me the Numbers: Designing Tables and Graphs to Enlighten**. Analytics Press, **2ª edição, 2012**.

**Nível:** iniciante a intermediário

Mais prático que Tufte, com regras claras e justificadas. O capítulo sobre **tabelas** é
o melhor que já li — e tabelas são o visual mais subestimado
([`18-visualizacao.md`](18-visualizacao.md) §3).

Do mesmo autor: **Information Dashboard Design** (2ª ed., 2013), especificamente sobre
painéis, e bastante crítico da maior parte do que se produz no mercado.

---

### 3.3 Wilke, Claus O. **Fundamentals of Data Visualization**. O'Reilly, **2019**. **[GRÁTIS]**

**Nível:** intermediário

Versão completa e legal disponível gratuitamente em **`clauswilke.com/dataviz`**, liberada
pelo autor.

**O que faz melhor:** equilibra teoria e prática, com bons capítulos sobre cor,
incerteza e distribuições. É o livro moderno de visualização mais bem estruturado que
conheço, e é gratuito.

---

### 3.4 Healy, Kieran. **Data Visualization: A Practical Introduction**. Princeton University Press, **2018**. **[GRÁTIS]**

**Nível:** intermediário

Versão online gratuita em **`socviz.co`**, liberada pelo autor.

Usa R e ggplot2 nos exemplos, mas os **capítulos 1 e 5** — sobre por que alguns gráficos
funcionam e outros não — valem independentemente da ferramenta.

---

### 3.5 Cleveland, William S. **The Elements of Graphing Data**. Hobart Press, edição revisada de **1994**.

**Nível:** avançado

Do autor do experimento de 1984 citado em [`18-visualizacao.md`](18-visualizacao.md) §2.
É a fonte primária da hierarquia de precisão perceptual. Denso, técnico, e a base
científica de quase tudo que os outros livros afirmam.

**O artigo original** (Cleveland & McGill, *JASA*, 1984) é mais curto e frequentemente
encontrável em repositórios acadêmicos.

---

### 3.6 Wexler, Steve; Shaffer, Jeffrey; Cotgreave, Andy. **The Big Book of Dashboards**. Wiley, **2017**.

**Nível:** intermediário

28 dashboards reais, cada um com o contexto de negócio, as decisões de projeto e as
críticas. **É o livro mais próximo de um estudo de casos** que existe no campo.

Os exemplos são majoritariamente em Tableau, mas as decisões são independentes de
ferramenta.

---

### 3.7 Cairo, Alberto. **How Charts Lie**. W. W. Norton, **2019**.

**Nível:** iniciante

Sobre como gráficos enganam — deliberadamente ou não. Curto, acessível e importante para
quem **produz** gráficos, não só para quem os consome.

Do mesmo autor: **The Truthful Art** (New Riders, 2016), mais completo e mais técnico.

**Português:** não tenho confirmação de tradução brasileira.

---

## 4. Fundamentos técnicos

### 4.1 Abadi, Daniel; Boncz, Peter; Harizopoulos, Stavros; et al. **The Design and Implementation of Modern Column-Oriented Database Systems**. *Foundations and Trends in Databases*, **2013**. **[GRÁTIS]**

**Nível:** pesquisa

Monografia acadêmica, disponível gratuitamente. É a explicação rigorosa de **por que**
armazenamento colunar funciona: compressão, execução vetorizada, materialização tardia,
*late materialization*, join colunar.

**É a fundamentação de [`21-vertipaq-por-dentro.md`](21-vertipaq-por-dentro.md).** Se você
quer entender o VertiPaq de verdade, e não apenas usá-lo, comece aqui.

---

### 4.2 Kleppmann, Martin. **Designing Data-Intensive Applications**. O'Reilly, **2017**.

**Nível:** avançado

Não é sobre Power BI. É sobre sistemas de dados em geral: replicação, particionamento,
transações, consistência, processamento em lote e em fluxo.

**Por que está aqui:** porque o Power BI é a ponta de um sistema de dados, e quase todo
problema difícil de BI é um problema de sistemas de dados aparecendo na ponta. O capítulo
sobre consistência ilumina [`60-teoria-avancada.md`](60-teoria-avancada.md) §7.

**Edição em português:** há edição brasileira publicada. Confirme a editora e o ano na
livraria.

---

### 4.3 Inmon, W. H. **Building the Data Warehouse**. Wiley, **4ª edição, 2005**.

**Nível:** intermediário

O "outro lado" do debate contra Kimball: data warehouse corporativo normalizado, com data
marts derivados.

**Por que ler:** porque entender a posição derrotada esclarece por que a vencedora venceu.
Ver [`11-historia.md`](11-historia.md) §2.

**Envelheceu?** Bastante. Leia por perspectiva histórica, não por prescrição.

---

## 5. Papers e artigos fundamentais **[GRÁTIS]**

Todos localizáveis em repositórios acadêmicos ou nos sites das publicações.

| Referência | Por que importa |
|---|---|
| **Luhn, H. P.** "A Business Intelligence System". *IBM Journal of R&D*, 1958 | A origem do termo, e uma leitura curta e surpreendente |
| **Codd, E. F.** "A Relational Model of Data for Large Shared Data Banks". *CACM*, 1970 | O fundamento de tudo |
| **Codd, E. F.; Codd, S.; Salley, C.** "Providing OLAP to User-Analysts", 1993 | Onde "OLAP" foi cunhado |
| **Shannon, C. E.** "A Mathematical Theory of Communication". *Bell System Technical Journal*, 1948 | O limite teórico da compressão ([`60`](60-teoria-avancada.md) §5) |
| **Cleveland, W. S.; McGill, R.** "Graphical Perception". *JASA*, 1984 | A hierarquia de precisão perceptual ([`18`](18-visualizacao.md) §2) |
| **Stevens, S. S.** "On the Psychophysical Law". *Psychological Review*, 1957 | Por que área é uma codificação ruim |
| **Rice, H. G.** "Classes of Recursively Enumerable Sets…". *Trans. AMS*, 1953 | Indecidibilidade de propriedades semânticas |
| **Dinur, I.; Nissim, K.** "Revealing Information While Preserving Privacy". *PODS*, 2003 | O limite matemático da RLS ([`60`](60-teoria-avancada.md) §8) |
| **Dwork, C.** "Differential Privacy". *ICALP*, 2006 | A resposta da literatura, e por que o BI não a adota |
| **Gilbert, S.; Lynch, N.** "Brewer's Conjecture…". *SIGACT News*, 2002 | A formalização do CAP |
| **Stonebraker, M. et al.** "C-Store: A Column-oriented DBMS". *VLDB*, 2005 | O ancestral acadêmico dos motores colunares comerciais |

---

## 6. O que **não** recomendo

Franqueza, para poupar seu dinheiro:

| Categoria | Por quê |
|---|---|
| Livros de "Power BI passo a passo" com muitas capturas de tela | Desatualizam em meses. Use vídeo gratuito |
| Livros que prometem "domine em 24 horas" | Ver [`02-pre-requisitos.md`](02-pre-requisitos.md) §3 para o tempo real |
| Livros só de "receitas de DAX" sem teoria | Você copia sem entender. Prefira `daxpatterns.com`, que é grátis |
| Edições antigas de livros sobre a **nuvem** | O Service muda todo mês |
| Livros sobre Fabric escritos em 2023–2024 | O produto mudou substancialmente desde então |

---

## 7. Ordem de leitura sugerida

```
Iniciante
  └─ Storytelling with Data (Knaflic)
      └─ Analyzing Data with Power BI (Russo/Ferrari, 2017)

Intermediário
  └─ The Data Warehouse Toolkit, caps. 1–3 (Kimball/Ross)
      └─ The Definitive Guide to DAX, caps. 1–5 (Russo/Ferrari)
          └─ ── PRATIQUE 2 MESES ──
              └─ The Definitive Guide to DAX, capítulos de contexto de avaliação
                  └─ Fundamentals of Data Visualization (Wilke) [GRÁTIS]

Avançado
  └─ Optimizing DAX (Russo/Ferrari)
      └─ Column-Oriented Database Systems (Abadi et al.) [GRÁTIS]
          └─ Designing Data-Intensive Applications (Kleppmann)

Pesquisa
  └─ Os papers da §5 [GRÁTIS]
```

**A pausa de dois meses no meio não é enfeite.** Os capítulos de contexto de avaliação só
fazem sentido depois que você bateu a cabeça em problemas reais. Ler antes é desperdício.

---

## 8. Autoteste

1. Qual livro é a referência definitiva sobre contexto de avaliação, e em qual edição?
2. Por que um livro de modelagem de 2013 continua obrigatório?
3. Qual livro de visualização é legalmente gratuito e bem estruturado?
4. Onde encontrar padrões de DAX gratuitamente?
5. Qual é o pré-requisito real para o *Optimizing DAX* fazer sentido?
6. Por que ler Inmon se Kimball venceu?
7. Qual monografia gratuita fundamenta o capítulo sobre o VertiPaq?
8. Cite três papers e o que cada um fundamenta neste curso.
9. Que tipo de livro sobre Power BI **não** vale a pena comprar, e por quê?
10. Por que a ordem de leitura sugerida tem uma pausa de dois meses no meio?

---

*Verificações feitas em 14/08/2026: existência e edição do* The Definitive Guide to DAX, 3rd Edition *(Microsoft Press / SQLBI) e dos recursos gratuitos* Start learning DAX for free *e* daxpatterns.com*. Demais obras listadas a partir de edições conhecidas e estáveis; **ISBNs foram deliberadamente omitidos** para não arriscar erro. Onde não confirmei tradução brasileira, o texto diz explicitamente que não confirmei.*
