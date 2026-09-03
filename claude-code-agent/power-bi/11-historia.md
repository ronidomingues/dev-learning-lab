# 11 · História — de 1958 ao Fabric

**Nível:** iniciante
**Data:** 14/08/2026

História não é enfeite. Quase toda esquisitice do Power BI — o nome "Power", a sintaxe do
DAX, a existência de duas linguagens, o Report Server, o Fabric — é resíduo de uma decisão
histórica. Saber a decisão explica a esquisitice.

---

## 1. Linha do tempo

```
1958  ─ Hans Peter Luhn (IBM) publica "A Business Intelligence System"
1970  ─ Codd formaliza o modelo relacional
1983  ─ Lotus 1-2-3 populariza a planilha eletrônica no PC
1985  ─ Excel (para Mac); 1987 para Windows
1992  ─ Kimball começa a difundir modelagem dimensional
1993  ─ Codd cunha o termo OLAP
1996  ─ Kimball publica "The Data Warehouse Toolkit"  ★ esquema estrela
1998  ─ Microsoft OLAP Services (depois SQL Server Analysis Services)
1997  ─ MDX, a linguagem de consulta de cubos
2005  ─ SSAS 2005 consolida o modelo multidimensional
2009  ─ POWERPIVOT para Excel 2010, com o motor VertiPaq e a linguagem DAX   ★★
2010  ─ Power Query (então "Data Explorer") e a linguagem M
2013  ─ "Power BI for Office 365" — suplementos do Excel na nuvem
2015  ─ POWER BI DESKTOP e app.powerbi.com — produto autônomo   ★★★
        Atualizações MENSAIS a partir daqui, sem parar
2016  ─ Power BI Embedded; Power BI Report Server (on-premises)
2017  ─ Gartner coloca a Microsoft como líder do Quadrante Mágico de BI
2019  ─ Premium; XMLA endpoint (leitura); modelos compostos
2020  ─ XMLA leitura/gravação; fluxos de dados; deployment pipelines
2021  ─ Premium Per User (PPU) — democratiza recursos "premium"
2022  ─ Datamarts; grupos de cálculo no Desktop
2023  ─ MICROSOFT FABRIC (GA em novembro): OneLake, Direct Lake,
        "dataset" vira "modelo semântico"                             ★★★★
        Copilot para Power BI (preview)
2024  ─ Fim do Desktop 32 bits (janeiro); Copilot em GA; PBIP e TMDL;
        cálculos visuais; migração P-SKU → F-SKU
2025  ─ Aumento de preço: Pro US$10→14, PPU US$20→24 (abril)
        Translytical task flows (escrita de volta na origem)
        Direct Lake no Desktop
2026  ─ Composite: Direct Lake + Import na mesma tabela (preview)
        TMDL na web; org apps com audiências em GA (julho)
        Agentes e "semantic model authoring skill"
```

---

## 2. 1958–1996: a pré-história

**1958 — o termo.** Hans Peter Luhn, pesquisador da IBM, publica *"A Business Intelligence
System"* no IBM Journal of Research and Development. A ideia: um sistema que dissemina
automaticamente informação para quem precisa dela. É notável que o termo tenha 68 anos e
ainda descreva o mesmo problema.

**1970 — o modelo relacional.** Edgar Codd define o modelo relacional. Décadas depois, é
ele quem cunha "OLAP" (1993) para nomear o que o modelo relacional **não** faz bem.

**A tensão fundadora do BI**, e ela existe até hoje:

| | OLTP (transacional) | OLAP (analítico) |
|---|---|---|
| Otimizado para | escrever e ler **uma** linha | agregar **milhões** de linhas |
| Armazenamento | por linha | por coluna (moderno) |
| Modelo | normalizado (3FN) | dimensional (estrela) |
| Consulta típica | "qual o saldo do cliente 4711?" | "qual a margem por região por trimestre?" |
| Concorrência | milhares de escritas/s | poucas leituras pesadas |

Rodar análise no banco transacional funciona até não funcionar. O BI nasceu dessa dor.

**1996 — Kimball.** Ralph Kimball publica *The Data Warehouse Toolkit* e populariza o
**esquema estrela**. A tese: modele para a **compreensão do usuário e a velocidade da
consulta**, não para a economia de espaço. Foi controverso na época — normalização era
dogma. Kimball venceu na prática, e é por isso que
[`14-modelagem-dimensional.md`](14-modelagem-dimensional.md) ensina estrela e não 3FN.

**Por que Kimball venceu?** Não por elegância teórica — Bill Inmon, o rival, tinha a
arquitetura mais rigorosa. Kimball venceu porque **estrela é entendível por um analista de
negócio**, e porque o custo do disco caiu mais rápido que o custo do tempo humano. É um
trade-off econômico explícito, não um resultado matemático.

---

## 3. 1998–2005: a era dos cubos

A Microsoft entra com **OLAP Services** (1998), depois **SQL Server Analysis Services**
(SSAS). O modelo é **multidimensional**: cubos com dimensões, hierarquias e medidas
pré-agregadas. A linguagem de consulta é **MDX** (1997).

Funcionava, e funcionava bem. Dois problemas:

1. **MDX é difícil.** Sério, difícil de verdade. `Descendants`, `Crossjoin`, contextos de
   tupla. Poucos dominavam.
2. **Construir um cubo exigia TI.** Meses de projeto, um especialista, um servidor. O
   analista de negócio ficava na fila.

Isso criou uma demanda reprimida enorme: *"eu só quero cruzar essas duas planilhas sem
abrir chamado"*. Toda a década seguinte é a resposta a esse desejo.

---

## 4. 2009: PowerPivot — o nascimento real

**Este é o marco.** Em 2009, a Microsoft lança o **PowerPivot**, um suplemento **gratuito
do Excel 2010**, com três novidades que são o Power BI de hoje:

1. **VertiPaq** — um motor colunar em memória, com compressão agressiva. Permitia
   milhões de linhas dentro do Excel, numa época em que a planilha travava com 100 mil.
2. **DAX** — uma linguagem nova, deliberadamente parecida com fórmulas de Excel.
3. **Modelo com relacionamentos** — várias tabelas ligadas, em vez de um `PROCV` gigante.

**As três decisões de projeto de 2009 que você sente todo dia em 2026:**

| Decisão de 2009 | Consequência em 2026 |
|---|---|
| DAX com cara de Excel | Sintaxe acolhedora, semântica traiçoeira ([`16`](16-dax-contexto-de-avaliacao.md)) |
| Colunar em memória | Modelo limitado pela RAM; compressão como habilidade central ([`21`](21-vertipaq-por-dentro.md)) |
| Self-service, sem TI | Proliferação de modelos duplicados; governança como problema ([`24`](24-seguranca-e-governanca.md)) |

**Por que dentro do Excel?** Distribuição. A Microsoft tinha centenas de milhões de
usuários de Excel. Colocar o motor onde o público já estava foi uma jogada de mercado, não
de engenharia — e foi decisiva.

**2010 — Power Query.** Chamado inicialmente "Data Explorer", chega o motor de ETL com a
linguagem **M**. Aqui nasce a duplicidade de linguagens que confunde todo iniciante: **M
prepara, DAX analisa**. Nunca foram unificadas, e a essa altura não serão.

---

## 5. 2013–2015: a saída do Excel

"Power BI for Office 365" (2013) foi uma tentativa desajeitada: um punhado de suplementos
do Excel (PowerPivot, Power Query, Power View, Power Map) mais um site. Não pegou.

**Julho de 2015: Power BI Desktop e `app.powerbi.com`** como produto autônomo. Aqui a
Microsoft toma quatro decisões que definiram o mercado:

1. **O Desktop é gratuito.** Sem limite, sem prazo, sem cadastro obrigatório. Todo
   analista podia baixar e experimentar sem pedir autorização a ninguém.
2. **Nuvem primeiro.** O Service é o produto; o Desktop é a ferramenta de autoria.
3. **US$ 9,99 por usuário/mês** para compartilhar — contra os US$ 70+/usuário/mês da
   concorrência. Um décimo do preço.
4. **Atualização mensal**, sem exceção, até hoje. Mais de 130 releases consecutivas.

**Opinião do autor:** o item 4 é subestimado. A cadência mensal criou uma percepção de
momentum imparável, transformou a comunidade em canal de marketing (todo mês há novidade
para postar) e, ao mesmo tempo, é a causa da fadiga real de quem trabalha com a
ferramenta — o `05-manual-de-uso.md` envelhece a cada quatro semanas.

O "Power" no nome é resíduo da era dos suplementos (PowerPivot, Power View, Power Query).
Hoje não significa nada; é história fossilizada.

---

## 6. 2016–2022: virando plataforma corporativa

O produto self-service precisou virar corporativo. Cada item abaixo existe para resolver
uma objeção real de um comprador grande:

| Recurso | Ano | A objeção que ele responde |
|---|---|---|
| Report Server | 2016 | "Não posso pôr dados na nuvem" (bancos, governo, saúde) |
| Embedded | 2016 | "Quero vender relatórios dentro do meu produto" |
| RLS | 2016 | "Cada gerente só pode ver sua região" |
| Premium (capacidade) | 2017 | "Tenho 5.000 leitores; não vou pagar por usuário" |
| Dataflows | 2018 | "Cinco analistas repetem a mesma limpeza" |
| XMLA endpoint | 2019–20 | "Preciso de ferramentas profissionais e CI/CD" |
| Modelos compostos | 2019 | "Preciso juntar um modelo corporativo com meu Excel" |
| Deployment pipelines | 2020 | "Cadê dev, homologação e produção?" |
| Rótulos de confidencialidade | 2020 | "Como controlo o dado exportado para Excel?" |
| PPU | 2021 | "Quero recursos premium sem comprar capacidade" |
| Grupos de cálculo (Desktop) | 2022 | "Tenho 300 medidas que são a mesma coisa com YTD" |

Note o padrão: **o produto nasceu bottom-up (analista) e passou sete anos adicionando o
que o top-down (TI corporativa) exigia.** Muita da complexidade de governança de hoje é
consequência dessa ordem invertida. Ferramentas que nasceram corporativas (Cognos,
MicroStrategy) tinham governança e sofreram para ganhar agilidade; o Power BI fez o
caminho oposto.

---

## 7. 2023: Microsoft Fabric — a reembalagem

Em maio de 2023 (GA em novembro), a Microsoft anuncia o **Microsoft Fabric**: uma
plataforma SaaS que reúne, sob uma única capacidade e um único armazenamento (**OneLake**),
o que antes eram produtos separados — Data Factory, Synapse, Data Activator e o próprio
Power BI.

**O que mudou de verdade:**

| Aspecto | Antes | Depois |
|---|---|---|
| Licenciamento | P-SKU (Power BI Premium) | **F-SKU** (Fabric), pago por CU |
| Armazenamento | cada serviço o seu | **OneLake**, um só, em Delta Parquet |
| Nome do "dataset" | conjunto de dados | **modelo semântico** |
| Novo modo | — | **Direct Lake** |
| Escopo do produto | BI | BI + engenharia + ciência + tempo real |

**O que NÃO mudou:** Power BI Desktop, DAX, Power Query, modelagem, relatórios, RLS.
Se você aprendeu Power BI em 2019, 90% continua válido.

**Direct Lake merece atenção** porque resolve uma tensão de 14 anos: Import é rápido mas
desatualizado; DirectQuery é atual mas lento. Direct Lake lê arquivos Delta Parquet
**diretamente do OneLake para a memória**, sob demanda, sem cópia prévia. Você fica perto
da velocidade do Import com a atualidade do DirectQuery. O custo: exige Fabric, e exige
que o dado esteja no OneLake em Delta. Ver [`26-fabric-e-ecossistema.md`](26-fabric-e-ecossistema.md).

**Opinião do autor, e é opinião:** o Fabric é, em partes iguais, uma evolução técnica real
(OneLake e Direct Lake são bons) e um movimento comercial para vender capacidade a quem só
queria BI. O F2 mais barato custava, em 14/08/2026, cerca de US$ 262/mês — muito acima do
que uma pequena empresa gastava com Power BI Pro. Para quem tem 20 usuários e um modelo
de 500 MB, o Fabric não acrescenta nada e o Pro continua sendo a resposta certa.

---

## 8. 2024–2026: a fase atual

**2024 — o ano da engenharia.** PBIP e TMDL tornam o modelo e o relatório **texto
versionável**. Isso encerra a maior crítica técnica ao produto: "não dá para versionar".
Também chegam os **cálculos visuais**, que resolvem em uma linha problemas que exigiam
DAX contorcionista.

**2025 — o ano da conta.** Em abril, a Microsoft aumenta os preços pela primeira vez desde
2015: Pro de US$ 10 para **US$ 14** (+40%), PPU de US$ 20 para **US$ 24** (+20%). É o fim
da era do "um décimo do preço do Tableau" — agora é cerca de um quinto. Também em 2025
chegam os *translytical task flows*: botões no relatório que **escrevem** de volta na
origem, quebrando a premissa de 16 anos de que BI é somente leitura.

**2026 — o ano do agente.** O que a documentação de 2026 mostra:

- **Modelo composto com Direct Lake + Import** na mesma tabela (preview);
- **TMDL na web** — editar o modelo como código no navegador, com recursos de IDE;
- **Org apps com audiências** em GA (julho/2026), aposentando na prática os apps clássicos;
- **APIs REST de CRUD** para org apps, audiências e relatórios paginados;
- **Semantic model authoring skill** — um agente que **cria modelos semânticos** sobre um
  lakehouse, gerando um modelo Direct Lake;
- comentários `///` no DAX virando descrição de medida — pequeno, mas revelador: a
  documentação passou a ser código.

---

## 9. Os concorrentes, e por que a história deles importa

| Ferramenta | Origem | Posição em 2026 |
|---|---|---|
| **Tableau** | 2003, spin-off de Stanford (Polaris) | Comprada pela Salesforce (2019). Ainda a melhor experiência de exploração visual; perdeu mercado por preço |
| **QlikView / Qlik Sense** | 1993, Suécia | Motor associativo elegante; ficou nichado |
| **Looker** | 2012, comprada pelo Google (2019) | Camada semântica em código (LookML) — influenciou toda a indústria |
| **MicroStrategy / Cognos / BO** | anos 1990 | Legado corporativo em manutenção |
| **Metabase / Superset** | 2015 / 2016 | Open source; ganharam espaço em startups |
| **dbt + camada semântica** | 2016 | Mudou o campo: "métricas como código", versionadas |

**A lição estratégica**, e ela vale além do BI: o Tableau era tecnicamente superior em
visualização em 2015 e continua sendo melhor em exploração livre. Perdeu porque a
Microsoft chegou com preço um décimo menor, distribuição pronta dentro do Office 365 e uma
ferramenta de autoria gratuita. **Ferramenta superior perde para ferramenta já
instalada.**

E uma lição de humildade: em 2015, ninguém dava nada pelo Power BI — era considerado o
"Tableau dos pobres". Dez anos depois, é o padrão de fato do mercado corporativo. Vale
lembrar disso antes de descartar qualquer ferramenta nova por ser tosca.

---

## 10. Os cinco porquês: por que M e DAX são linguagens separadas?

1. **Por que não uma linguagem só?**
   Porque nasceram em projetos diferentes, com objetivos diferentes: DAX em 2009 para o
   PowerPivot (analisar); M em 2010 para o Data Explorer (preparar). Não foram desenhadas
   uma para a outra.

2. **Por que não unificaram depois?**
   Porque executam em **momentos diferentes** e sobre **coisas diferentes**. M roda no
   refresh, sobre tabelas ainda não carregadas, e precisa gerar SQL para a fonte
   (*folding*). DAX roda na consulta, sobre um modelo em memória, e precisa entender
   contexto de filtro. Uma linguagem que fizesse os dois bem seria pior nos dois.

3. **Por que M precisa gerar SQL?**
   Porque a alternativa — baixar tudo e filtrar localmente — é inviável em qualquer volume
   sério. Empurrar o trabalho para a fonte é a única estratégia que escala.

4. **Por que DAX não pode simplesmente virar SQL também?**
   Porque a semântica de contexto de filtro não tem equivalente em SQL padrão. `CALCULATE`
   com `ALLSELECTED` depende do que está visível no visual — informação que não existe no
   modelo relacional.

5. **Parada legítima — decisão histórica com custo assumido.**
   A Microsoft manteve duas linguagens sabendo do custo pedagógico. A alternativa
   (reescrever tudo numa linguagem só) quebraria compatibilidade com dez anos de modelos
   em produção. **É o preço da compatibilidade retroativa**, e é o mesmo motivo pelo qual
   `EARLIER()` ainda funciona em 2026.

---

## 11. O que a história ensina para quem está aprendendo hoje

1. **O que é estável vale mais.** Esquema estrela (1996), contexto de avaliação (2009) e
   compressão colunar (2009) não mudaram. A interface muda todo mês. Invista o seu tempo
   de estudo na proporção inversa da taxa de mudança.

2. **O que hoje é "avançado" será padrão.** Grupos de cálculo, PBIP, TMDL e Direct Lake
   seguem o mesmo caminho que RLS e Power Query seguiram: de exótico a obrigatório em
   ~3 anos.

3. **Preço é estratégia, e ele muda.** Quem construiu um plano de custos em 2015 tomou um
   aumento de 40% em 2025. Reveja licenciamento anualmente
   ([`80-custos-e-licencas.md`](80-custos-e-licencas.md)).

4. **Reembalagem acontece.** "Dataset" virou "modelo semântico"; "Premium" virou "Fabric".
   Aprenda o **conceito**, não o nome comercial. O conceito sobrevive à campanha de
   marketing.

---

## 12. Autoteste

1. Quem cunhou "Business Intelligence", em que ano, e no sentido de quê?
2. Qual a diferença fundamental entre OLTP e OLAP, e por que ela deu origem ao BI?
3. Por que Kimball venceu Inmon na prática? Dê o argumento econômico.
4. O que o PowerPivot (2009) trouxe de novo, em três itens?
5. Por que o DAX foi feito parecido com Excel, e qual foi o preço dessa decisão?
6. Cite as quatro decisões de 2015 que definiram o mercado de BI.
7. O que o Microsoft Fabric mudou e o que **não** mudou para quem já sabia Power BI?
8. O que é Direct Lake e qual tensão de 14 anos ele tenta resolver?
9. Por que o Tableau perdeu mercado sendo tecnicamente melhor em visualização?
10. Por que M e DAX nunca foram unificadas? Dê o motivo técnico e o histórico.

---

**Próximo:** [`12-arquitetura.md`](12-arquitetura.md) — as peças e o que roda onde.

---

*Fontes consultadas em 14/08/2026: [Microsoft Learn — What's new (julho/2026)](https://learn.microsoft.com/en-us/power-bi/fundamentals/whats-new); [Microsoft Learn — histórico mensal](https://learn.microsoft.com/en-us/power-bi/fundamentals/desktop-latest-update-archive); [Microsoft — preços](https://www.microsoft.com/en-us/power-platform/products/power-bi/pricing); [Microsoft Learn — Direct Lake](https://learn.microsoft.com/en-us/fabric/fundamentals/direct-lake-overview); [Microsoft Learn — Semantic model authoring skill](https://learn.microsoft.com/en-us/power-bi/developer/agentic/semantic-model-authoring-skill-overview). O artigo de Luhn é "A Business Intelligence System", IBM Journal of Research and Development, v.2, n.4, 1958.*
