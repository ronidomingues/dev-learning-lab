# 95 · Referências

**Nível:** todos
**Data da consulta: 14/08/2026**

Documentação oficial, ferramentas, comunidade, pessoas e fontes primárias. Organizado por
**para que serve**, não em ordem alfabética.

---

## 1. Documentação oficial da Microsoft

### 1.1 Pontos de entrada

| Recurso | URL |
|---|---|
| Documentação do Power BI | `learn.microsoft.com/power-bi/` |
| Documentação em **português** | `learn.microsoft.com/pt-br/power-bi/` |
| Documentação do Microsoft Fabric | `learn.microsoft.com/fabric/` |
| Trilhas de treinamento | `learn.microsoft.com/training/` |
| Certificações | `learn.microsoft.com/credentials/` |

### 1.2 As páginas que você vai consultar de verdade

| Assunto | URL |
|---|---|
| **Novidades do mês** | `learn.microsoft.com/power-bi/fundamentals/whats-new` |
| **Change log do Desktop** (correções por build) | `learn.microsoft.com/power-bi/fundamentals/desktop-change-log` |
| **Arquivo de versões mensais** (baixar builds antigas) | `learn.microsoft.com/power-bi/fundamentals/desktop-latest-update-archive` |
| **Download e requisitos do Desktop** | `learn.microsoft.com/power-bi/fundamentals/desktop-get-the-desktop` |
| **Referência de funções DAX** | `learn.microsoft.com/dax/` |
| **Referência da linguagem M** | `learn.microsoft.com/powerquery-m/` |
| **Especificação do TMDL** | `learn.microsoft.com/analysis-services/tmdl/tmdl-overview` |
| **API REST do Power BI** | `learn.microsoft.com/rest/api/power-bi/` |
| **API REST do Fabric** | `learn.microsoft.com/rest/api/fabric/` |
| **Direct Lake** | `learn.microsoft.com/fabric/fundamentals/direct-lake-overview` |
| **Gateway de dados local** | `learn.microsoft.com/data-integration/gateway/` |
| **Limites e especificações** | procurar por "Power BI service limits" na documentação |
| **URLs a liberar no firewall** | procurar por "Power BI URLs" |
| **Guia de práticas de segurança** | `learn.microsoft.com/power-bi/guidance/` ★ |
| **Roadmap do produto** | `roadmap.fabric.microsoft.com` |
| **Ideias / feedback** | `ideas.fabric.microsoft.com` |

### 1.3 A seção mais subestimada: *Guidance*

`learn.microsoft.com/power-bi/guidance/`

A Microsoft mantém uma seção de **orientação de arquitetura e boas práticas**, separada da
documentação de referência. Ela cobre: esquema estrela, otimização de DAX, RLS,
planejamento de implantação (o *Power BI implementation planning*, que é extenso e sério),
e recomendações de modelagem.

**É de graça, é oficial, é bom, e quase ninguém lê.** Se você vai ler uma coisa da
documentação além do que precisa hoje, leia isso.

---

## 2. Ferramentas

| Ferramenta | Onde | Licença |
|---|---|---|
| **DAX Studio** | `daxstudio.org` · GitHub: `DaxStudio/DaxStudio` | MIT |
| **Tabular Editor 2** | GitHub: `TabularEditor/TabularEditor` | MIT |
| **Tabular Editor 3** | `tabulareditor.com` | comercial |
| **Bravo for Power BI** | `bravo.bi` · GitHub: `sql-bi/Bravo` | MIT |
| **ALM Toolkit** | `alm-toolkit.com` | MIT |
| **VertiPaq Analyzer** | embutido no DAX Studio · `sqlbi.com/tools/vertipaq-analyzer/` | — |
| **DAX Formatter** | `daxformatter.com` | serviço web gratuito |
| **Best Practice Analyzer — regras** | GitHub: `microsoft/Analysis-Services` (pasta `BestPracticeRules`) | ★ |
| **Measure Killer** | `en.brunner.bi` | freemium |
| **PBI Inspector / PBI Explorer** | GitHub | aberto |
| **Módulo PowerShell** | `MicrosoftPowerBIMgmt` na PowerShell Gallery | Microsoft |
| **semantic-link (SemPy)** | `pypi.org/project/semantic-link` | Microsoft |
| **Fabric CLI** | documentação do Fabric | Microsoft |
| **Extensões TMDL/DAX para VS Code** | Marketplace do VS Code | variadas |

**Sobre o Best Practice Analyzer:** o repositório `microsoft/Analysis-Services` hospeda o
conjunto de regras mantido pela comunidade (com contribuição destacada de Michael
Kovalsky). Baixe o `BPARules.json` e use no Tabular Editor. É, por hora investida, a
melhor ferramenta de qualidade que existe no ecossistema.

---

## 3. Referências de linguagem

| Recurso | O que é |
|---|---|
| **`dax.guide`** ★ | Referência de **todas** as funções DAX, mantida pela SQLBI. Melhor que a documentação oficial: mostra parâmetros, contexto, compatibilidade por produto e observações de desempenho |
| **`daxpatterns.com`** ★ | Padrões de DAX completos e gratuitos: inteligência de tempo, calendários personalizados, ABC, segmentação dinâmica, cesta de compras, orçamento |
| `learn.microsoft.com/dax/` | Referência oficial |
| `learn.microsoft.com/powerquery-m/` | Referência oficial de M |
| **`sqlbi.com/articles/`** | Artigos técnicos profundos, muitos deles melhores que capítulos de livro |
| **`daxformatter.com`** | Formatador online (o mesmo motor do `Ctrl+Shift+M`) |

**Se você marcar apenas dois favoritos deste arquivo, marque `dax.guide` e
`daxpatterns.com`.**

---

## 4. Comunidade

| Recurso | Observação |
|---|---|
| **Microsoft Fabric Community** (`community.fabric.microsoft.com`) | Fórum oficial. Onde saem os *Feature Summary* mensais |
| **Power BI Updates Blog** (na comunidade) | Resumo mensal de recursos ★ |
| **Fabric Updates Blog** | Novidades da plataforma |
| **r/PowerBI** (Reddit) | Discussão franca, inclusive crítica |
| **Stack Overflow** — tags `powerbi`, `dax`, `powerquery` | Problemas específicos |
| **Power BI User Groups (PUG)** | Encontros locais; há grupos brasileiros |
| **`#PowerBI` no LinkedIn** | Ruído alto, sinal ocasional |

**Comunidades brasileiras:** existem grupos ativos no Telegram, no WhatsApp e no LinkedIn.
Não listo links porque grupos migram e expiram; procure por "Power BI Brasil" nas
plataformas.

---

## 5. Blogs e pessoas que vale acompanhar

**Critério:** técnico, consistente há anos, e disposto a dizer quando algo é ruim.

| Pessoa / Blog | Foco |
|---|---|
| **Marco Russo e Alberto Ferrari** (`sqlbi.com`) | DAX, modelo tabular, desempenho. **A referência mundial** |
| **Adam Saxton e Patrick LeBlanc** (Guy in a Cube) | Novidades, administração, resolução de problemas |
| **Chris Webb** (`blog.crossjoin.co.uk`) | Power Query, M, desempenho, DirectQuery. Profundíssimo |
| **Reza Rad** (`radacad.com`) | Amplo, muitos tutoriais e entrevistas |
| **Kasper de Jonge** (`kasperonbi.com`) | Interno do produto; trabalha na Microsoft |
| **Daniel Otykier** | Tabular Editor, TMDL |
| **Michael Kovalsky** | Best Practice Analyzer, governança |
| **Phil Seamark** (`dax.tips`) | Truques e visualizações de plano de consulta |
| **Imke Feldmann** (`thebiccountant.com`) | Power Query e M avançados |
| **Melissa de Korte, Curbal (Ruth Pozuelo)** | Didática de DAX e visuais |

**Nota:** esta lista reflete quem eu acompanho e considero confiável. Não é exaustiva, e
há gente excelente fora dela — inclusive em português.

---

## 6. Fontes primárias citadas neste curso

Para quem quer ir à origem.

| Referência | Onde aparece neste curso |
|---|---|
| Luhn, H. P. "A Business Intelligence System". *IBM Journal of R&D*, v.2, n.4, 1958 | [`01`](01-introducao-leigo.md), [`11`](11-historia.md) |
| Codd, E. F. "A Relational Model of Data for Large Shared Data Banks". *CACM*, 1970 | [`11`](11-historia.md) |
| Codd, E. F.; Codd, S. B.; Salley, C. T. "Providing OLAP to User-Analysts", 1993 | [`11`](11-historia.md) |
| Kimball, R.; Ross, M. *The Data Warehouse Toolkit*, 3ª ed., Wiley, 2013 | [`14`](14-modelagem-dimensional.md) |
| Shannon, C. E. "A Mathematical Theory of Communication". *BSTJ*, 1948 | [`21`](21-vertipaq-por-dentro.md), [`60`](60-teoria-avancada.md) |
| Cleveland, W. S.; McGill, R. "Graphical Perception…". *JASA*, v.79, n.387, 1984 | [`18`](18-visualizacao.md) |
| Stevens, S. S. "On the Psychophysical Law". *Psychological Review*, 1957 | [`18`](18-visualizacao.md) |
| Tufte, E. *The Visual Display of Quantitative Information*, 1983 | [`18`](18-visualizacao.md) |
| Rice, H. G. "Classes of Recursively Enumerable Sets…". *Trans. AMS*, 1953 | [`16`](16-dax-contexto-de-avaliacao.md), [`60`](60-teoria-avancada.md) |
| Dinur, I.; Nissim, K. "Revealing Information While Preserving Privacy". *PODS*, 2003 | [`60`](60-teoria-avancada.md) |
| Dwork, C. "Differential Privacy". *ICALP*, 2006 | [`60`](60-teoria-avancada.md) |
| Gilbert, S.; Lynch, N. "Brewer's Conjecture…". *SIGACT News*, 2002 | [`60`](60-teoria-avancada.md) |
| Abadi, D.; Boncz, P.; Harizopoulos, S. et al. *The Design and Implementation of Modern Column-Oriented Database Systems*, 2013 | [`21`](21-vertipaq-por-dentro.md), [`60`](60-teoria-avancada.md) |
| Stonebraker, M. et al. "C-Store: A Column-oriented DBMS". *VLDB*, 2005 | [`21`](21-vertipaq-por-dentro.md) |
| Dijkstra, E. W. "On the role of scientific thought", 1974 (separação de responsabilidades) | [`23`](23-servico-colaboracao-e-atualizacao.md) |

---

## 7. Especificações e formatos

| Formato | Especificação |
|---|---|
| **TMDL** | `learn.microsoft.com/analysis-services/tmdl/tmdl-overview` |
| **TMSL** (JSON, para XMLA) | `learn.microsoft.com/analysis-services/tmsl/` |
| **PBIP / PBIR** | Documentação de "Power BI Desktop projects" |
| **Delta Lake** | `delta.io` — Apache 2.0 |
| **Apache Parquet** | `parquet.apache.org` — Apache 2.0 |
| **XMLA** | Especificação aberta (originalmente XML for Analysis) |
| **OData** | `odata.org` — usado por vários conectores |
| **RDL** (relatórios paginados) | Documentação do SQL Server Reporting Services |
| **Formato de tema (JSON)** | `learn.microsoft.com/power-bi/create-reports/desktop-report-themes` |

---

## 8. Fontes específicas consultadas para este curso

Todas verificadas em **14/08/2026**. Onde um arquivo depende de uma delas, o rodapé
daquele arquivo repete a citação.

**Microsoft (oficial):**

- [Download Power BI Desktop](https://learn.microsoft.com/en-us/power-bi/fundamentals/desktop-get-the-desktop) — métodos de instalação, requisitos mínimos, parâmetros de linha de comando, extração de MSI, virtualização, WebView2, conta de sistema
- [What's new — julho/2026](https://learn.microsoft.com/en-us/power-bi/fundamentals/whats-new) — recursos do mês e o prazo de outubro/2026
- [Change log do Power BI Desktop](https://learn.microsoft.com/en-us/power-bi/fundamentals/desktop-change-log)
- [Arquivo de atualizações mensais](https://learn.microsoft.com/en-us/power-bi/fundamentals/desktop-latest-update-archive)
- [Direct Lake overview](https://learn.microsoft.com/en-us/fabric/fundamentals/direct-lake-overview)
- [Direct Lake no Power BI Desktop](https://learn.microsoft.com/en-us/fabric/fundamentals/direct-lake-power-bi-desktop)
- [Semantic model authoring skill](https://learn.microsoft.com/en-us/power-bi/developer/agentic/semantic-model-authoring-skill-overview)
- [Instalar o on-premises data gateway](https://learn.microsoft.com/en-us/data-integration/gateway/service-gateway-install)
- [Microsoft Certified: Power BI Data Analyst Associate](https://learn.microsoft.com/en-us/credentials/certifications/power-bi-data-analyst-associate/)
- [Course PL-300T00-A](https://learn.microsoft.com/en-us/training/courses/pl-300t00)
- [Power BI — página de preços](https://www.microsoft.com/en-us/power-platform/products/power-bi/pricing)
- [Azure Blog — Build 2026: agentic apps com Fabric](https://azure.microsoft.com/en-us/blog/microsoft-build-2026-building-agentic-apps-with-microsoft-fabric-and-microsoft-databases/)

**Comunidade Fabric (oficial da plataforma, blog de produto):**

- [DAX User-Defined Functions (Generally Available)](https://community.fabric.microsoft.com/t5/Power-BI-Updates-Blog/DAX-User-Defined-Functions-Generally-Available/ba-p/5185738)
- [Power BI June 2026 Feature Summary](https://community.fabric.microsoft.com/t5/Power-BI-Updates-Blog/Power-BI-June-2026-Feature-Summary/ba-p/5193264)
- [Composite semantic models com Direct Lake e tabelas Import](https://community.fabric.microsoft.com/t5/Power-BI-Updates-Blog/Deep-dive-into-composite-semantic-models-with-Direct-Lake-and/ba-p/5173943)
- [Fabric IQ — camada de contexto compartilhado](https://community.fabric.microsoft.com/t5/Fabric-Updates-Blog/Fabric-IQ-The-shared-context-layer-for-AI-agents-and-real-time/ba-p/5191678)

**Terceiros (tratados como aproximação, sempre marcados no texto):**

- [winget.run — Microsoft.PowerBI](https://winget.run/pkg/Microsoft/PowerBI) — identificador e build do pacote
- [Tabular Editor — pricing](https://tabulareditor.com/pricing) — estrutura de edições
- Compilações de preços de F-SKU do Fabric (várias fontes) — ordem de grandeza; confirmar na [calculadora do Azure](https://azure.microsoft.com/pricing/calculator/)
- Cotação comercial USD/BRL de 14/08/2026 (≈ 5,19)
- Preço do exame PL-300 (US$ 165) — a Microsoft não publica valor único

**Cursos e formação:**

- [Fundação Bradesco — Escola Virtual](https://www.ev.org.br/cursos/introducao-a-analise-de-dados-microsoft-power-bi)
- [SQLBI — Start learning DAX for free](https://www.sqlbi.com/articles/start-learning-dax-for-free/)
- [SQLBI — Introducing DAX video course](https://www.sqlbi.com/p/introducing-dax-video-course/)
- [SQLBI — The Definitive Guide to DAX, Third Edition](https://www.sqlbi.com/books/the-definitive-guide-to-dax-third-edition/)
- [Coursera — Microsoft Power BI Data Analyst Professional Certificate](https://www.coursera.org/professional-certificates/microsoft-power-bi-data-analyst)
- Playlists em francês: [Formation Complète Power BI GRATUITE](https://www.youtube.com/playlist?list=PL-7Ue_1Wto-ZdrFKOxcUalrqc3-CxezU_) · [COURS POWER BI EN FRANCAIS GRATUIT](https://www.youtube.com/playlist?list=PLwfDxSdhDUn6znOJ7xfSFMuMWmLbqs_U3)

---

## 9. Assuntos relacionados nesta pasta

| Assunto | Por que interessa a quem faz Power BI |
|---|---|
| [`../sql/00-MAPA.md`](../sql/00-MAPA.md) | **O pré-requisito de maior retorno.** Inclui um bloco de aplicações em engenharia química |
| [`../postgresql/00-MAPA.md`](../postgresql/00-MAPA.md) | Modelagem relacional, índices, planejador — a fonte dos seus dados |
| [`../apis/00-MAPA.md`](../apis/00-MAPA.md) | Consumir APIs no Power Query; usar a API REST do Power BI |
| [`../docker/00-MAPA.md`](../docker/00-MAPA.md) | Subir bancos de teste; ambientes reprodutíveis |
| [`../commits-assinados/00-MAPA.md`](../commits-assinados/00-MAPA.md) | Base de Git, necessária para PBIP/TMDL |
| [`../testes-automatizados/00-MAPA.md`](../testes-automatizados/00-MAPA.md) | A mentalidade de teste que falta ao BI |
| [`../agentes-de-ia/00-MAPA.md`](../agentes-de-ia/00-MAPA.md) | Contexto para Copilot, agentes e MCP sobre modelos semânticos |

---

## 10. Como manter este arquivo vivo

| Item | Revisar a cada |
|---|---|
| Links da documentação oficial | 6 meses (a Microsoft reorganiza URLs) |
| Ferramentas e versões | 6 meses |
| Blogs e pessoas | 1 ano |
| Fontes primárias | nunca (são estáveis) |
| Preços e cursos | ver [`80`](80-custos-e-licencas.md) e [`85`](85-cursos-e-certificacoes.md) |
