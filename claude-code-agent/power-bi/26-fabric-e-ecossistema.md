# 26 · Microsoft Fabric e o ecossistema

**Nível:** avançado
**Data:** 14/08/2026

Em 2023 o Power BI foi embalado dentro de uma plataforma maior. Este capítulo explica o
que isso significa na prática, o que muda para quem já sabe Power BI, e — o mais
importante — **quando o Fabric não é para você**.

---

## 1. O que é o Fabric

> **Microsoft Fabric** — uma plataforma SaaS de dados que reúne, sob uma **única
> capacidade** e um **único armazenamento** (OneLake), workloads que antes eram produtos
> separados.

```
┌───────────────────────────────────────────────────────────────────────┐
│                        MICROSOFT FABRIC                               │
│                                                                       │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌─────────────┐  │
│  │   Data   │ │   Data   │ │   Data   │ │Real-Time │ │  POWER BI   │  │
│  │ Factory  │ │Engineering│ │ Science  │ │Intelligence│ │            │  │
│  │(pipelines│ │(lakehouse│ │(notebooks│ │(eventstream│ │(modelos e  │  │
│  │ dataflows│ │  Spark)  │ │  ML)     │ │  KQL)     │ │ relatórios)│  │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ └──────┬──────┘  │
│       └────────────┴────────────┴────────────┴──────────────┘         │
│                              ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │                          ONELAKE                                │  │
│  │  Um único data lake para o locatário inteiro.                   │  │
│  │  Formato aberto: Delta Lake sobre Parquet.                      │  │
│  │  Todo workload lê e escreve aqui. Sem cópias entre serviços.     │  │
│  └─────────────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────────────┘
```

**A tese do produto:** "one copy" — o dado é gravado uma vez, em formato aberto, e todos
os motores o leem no lugar, sem ETL entre ferramentas.

---

## 2. OneLake

> **OneLake** — um data lake único por locatário, construído sobre Azure Data Lake
> Storage Gen2, com formato **Delta Lake** (Parquet + log de transações).

**Características que importam:**

| Característica | Consequência |
|---|---|
| **Um por locatário** | Não há decisão de "onde criar o lake" |
| **Formato aberto (Delta/Parquet)** | Legível por Spark, DuckDB, Polars, pandas, Databricks — não é aprisionamento de formato |
| **Atalhos** (*shortcuts*) | Referencia dados de S3, ADLS, GCS **sem copiar** |
| **Espelhamento** (*mirroring*) | Replica bancos (Azure SQL, Cosmos, Snowflake, PostgreSQL) continuamente para o OneLake |
| **OneLake File Explorer** | Navega o lake como uma pasta do Windows |

**Opinião do autor:** o formato aberto é a decisão mais importante e a mais subestimada.
Delta/Parquet significa que, se você quiser sair do Fabric, os dados continuam legíveis por
qualquer ferramenta. Isso é o oposto do aprisionamento clássico de plataformas de BI, e
merece crédito.

---

## 3. Os itens do Fabric que interessam a quem faz BI

| Item | O que é | Quando usar |
|---|---|---|
| **Lakehouse** | Pastas de arquivos + tabelas Delta, com endpoint SQL de leitura | Dados brutos e curados; base de Direct Lake |
| **Warehouse** | Data warehouse SQL completo, com T-SQL e transações | Quando o time é de SQL e precisa de escrita |
| **Dataflow Gen2** | Power Query na nuvem, com destino de saída | ETL de baixo código |
| **Data pipeline** | Orquestração (herda do Azure Data Factory) | Agendamento e dependências |
| **Notebook** | PySpark, Python, SQL, R | Transformações complexas, ML |
| **Modelo semântico** | O de sempre — agora podendo ser Direct Lake | Camada de BI |
| **Eventstream / Eventhouse (KQL)** | Ingestão e consulta de eventos em tempo real | Telemetria, IoT, logs |
| **Data Activator** | Regras que disparam ações sobre eventos | Alertas acionáveis |
| **SQL database** | Banco operacional dentro do Fabric | Aplicações leves |

### Lakehouse × Warehouse — a dúvida mais comum

| | Lakehouse | Warehouse |
|---|---|---|
| Escrita | Spark, notebooks, dataflows | **T-SQL** |
| Leitura SQL | Endpoint **somente leitura** | Completa |
| Formato | Delta | Delta (gerenciado) |
| Público | engenheiro de dados | profissional de SQL/BI |
| Transações multi-tabela | limitadas | **sim** |

**Recomendação:** se seu time vem de SQL Server e pensa em T-SQL, **Warehouse**. Se vem
de Python/Spark e trabalha com arquivos, **Lakehouse**. Não é uma decisão irreversível —
ambos gravam Delta no OneLake.

---

## 4. Direct Lake — o elo com o Power BI

Já tratado em [`20-modos-de-armazenamento.md`](20-modos-de-armazenamento.md) §4.
O que importa aqui é o **posicionamento arquitetural**:

```
Fonte ──► Pipeline/Dataflow ──► Lakehouse (Delta) ──► Modelo Direct Lake ──► Relatório
                                     ▲
                                     └── notebooks, Spark, SQL também leem e escrevem
```

Nenhuma cópia entre a camada de dados e a camada de BI. O modelo semântico **aponta** para
os arquivos Delta.

**O que 2026 acrescentou:**

- **Direct Lake no Power BI Desktop** — editar esses modelos localmente.
- **Modelos compostos Direct Lake + Import** (preview) — a maior restrição prática caiu:
  agora dá para juntar tabelas do lakehouse com tabelas importadas de qualquer conector.
- **Criação de modelo Direct Lake por agente** (*semantic model authoring skill*).

---

## 5. Copilot, agentes e a camada de IA

### 5.1 O que existe

| Recurso | O que faz |
|---|---|
| **Copilot no Power BI** | Gera páginas de relatório, resume dados, escreve e explica DAX |
| **Copilot no Power Query** | Sugere transformações |
| **Copilot em notebooks** | Gera código PySpark/SQL |
| **Narrativa inteligente** | Resumo textual dinâmico dentro do relatório |
| **Semantic model authoring skill** | Um **agente** que cria um modelo semântico Direct Lake sobre um lakehouse |
| **Data agents** | Agentes que respondem perguntas sobre dados do Fabric |
| **AI Auto-Description** | Descrições automáticas para objetos do modelo |

### 5.2 O que funciona bem hoje (14/08/2026)

- **Explicar DAX existente.** Muito bom. Cole uma medida herdada de alguém e peça
  explicação.
- **Gerar DAX simples.** Bom para padrões conhecidos (YTD, variação, ranking).
- **Sugerir nomes e descrições.** Útil, revise.
- **Resumir o que está na tela.** Razoável.

### 5.3 O que ainda não funciona bem

- **DAX complexo com contexto de avaliação sutil.** Gera código plausível e errado. É o
  pior modo de falha possível: parece certo, compila, e devolve outro número.
- **Decisões de modelagem.** Ele não sabe a regra de negócio da sua empresa.
- **Qualidade de dados.** Não vai descobrir que suas devoluções estão com sinal trocado.
- **Julgamento sobre o que vale medir.**

### 5.4 A dependência que ninguém menciona

> **A qualidade de qualquer recurso de IA sobre o seu modelo é limitada pela qualidade do
> seu modelo.**

Nomes técnicos, tabelas sem descrição, colunas ambíguas, chaves expostas, medidas sem
formato — tudo isso degrada o Copilot exatamente como degrada o Q&A e como confunde um
analista humano novo.

**Isto é uma boa notícia**, e é a conclusão mais prática deste capítulo: o investimento que
melhora o Copilot é o mesmo que já valia a pena antes — **nomear bem, documentar com `///`,
ocultar o técnico, modelar em estrela**. A IA não substituiu a modelagem; ela aumentou o
retorno de fazê-la direito.

### 5.5 Responsabilidade

Quem publica o número responde por ele. "O Copilot escreveu a medida" não é defesa em
nenhuma reunião. Exija revisão humana de qualquer DAX gerado antes de ir para um modelo
certificado ([`24`](24-seguranca-e-governanca.md) §8).

---

## 6. Quando o Fabric **não** é para você

Seção que raramente aparece em material sobre Fabric.

| Situação | Recomendação |
|---|---|
| 20 usuários, um modelo de 500 MB, fontes em Excel e SQL | **Power BI Pro. Ponto.** O Fabric não acrescenta nada e custa ~20× mais |
| Sem equipe de dados | Uma plataforma com 8 workloads precisa de quem a opere |
| Já tem Databricks/Snowflake maduro e funcionando | Use Power BI sobre eles. Migrar por migrar destrói valor |
| Requisito de dados on-premises | Fabric é SaaS. O gateway ajuda, mas o dado processado vai para a nuvem |
| Orçamento apertado e previsível | Capacidade é custo fixo mensal; licença por usuário escala com o uso |

**Opinião do autor, e é opinião:** há uma pressão comercial real para tratar o Fabric como
o caminho natural de todo cliente de Power BI. Para a maioria das empresas médias
brasileiras, **não é**. O F2 mais barato custava, em 14/08/2026, cerca de US$ 262/mês
pay-as-you-go — mais que 18 licenças Pro. E o F2 é pequeno demais para as cargas que
justificariam o Fabric.

O ponto em que o Fabric passa a fazer sentido é razoavelmente identificável: quando você
tem **volume que não cabe em Import**, **mais de uma disciplina de dados** (engenharia +
BI + ciência), e **equipe para operar**. Antes disso, é complexidade sem contrapartida.

---

## 7. O ecossistema além da Microsoft

O Power BI não vive isolado. O que costuma orbitá-lo em arquiteturas reais:

| Camada | Ferramentas comuns |
|---|---|
| Ingestão | Fivetran, Airbyte, Azure Data Factory, Fabric pipelines |
| Armazenamento | Snowflake, Databricks, BigQuery, Redshift, Postgres, OneLake |
| Transformação | **dbt**, Dataflow Gen2, Spark, SQL |
| Orquestração | Airflow, Dagster, Fabric pipelines |
| Qualidade | Great Expectations, dbt tests, **scripts próprios** |
| Catálogo/linhagem | Microsoft Purview, DataHub, OpenMetadata |
| BI | **Power BI**, Tableau, Looker, Metabase |
| Camada semântica | Modelo do Power BI, dbt Semantic Layer, Cube |

**A tendência mais relevante para quem faz BI:** a camada de transformação migrou para
**dbt + SQL na fonte**, e o Power BI recebe tabelas já modeladas em estrela. Isso é uma
melhoria genuína — o trabalho pesado fica onde há testes, versionamento e paralelismo, e o
modelo do Power BI fica fino, rápido e fácil de manter.

**Se você está começando hoje:** aprender SQL e um pouco de dbt vale mais para a sua
carreira de BI do que dominar as 300 funções do DAX. Ver
[`../sql/00-MAPA.md`](../sql/00-MAPA.md).

---

## 8. Os cinco porquês: por que a Microsoft criou o Fabric?

1. **Por que reembalar produtos que já funcionavam?**
   Porque o cliente corporativo tinha de comprar, integrar e operar cinco produtos
   separados (Power BI, Synapse, Data Factory, Databricks-concorrente, Stream Analytics),
   cada um com seu armazenamento e seu modelo de custo.

2. **Por que isso era um problema comercial?**
   Porque a concorrência — Databricks e Snowflake — vendia **uma** plataforma que fazia
   quase tudo, com uma conta e um contrato. Quem vende cinco peças perde para quem vende
   uma solução.

3. **Por que o armazenamento único (OneLake) é o núcleo da resposta?**
   Porque o custo real de integração não é de licença: é de **mover dados entre sistemas**.
   Cada cópia é um pipeline para manter, uma latência, um ponto de divergência. Eliminar
   as cópias elimina a maior parte do trabalho de integração.

4. **Por que escolher um formato aberto (Delta/Parquet) em vez de proprietário?**
   **Trade-off comercial explícito.** Um formato proprietário aprisionaria melhor, mas
   perderia os clientes que já usam Spark, Databricks e ferramentas abertas — que são
   exatamente os clientes de maior porte. A Microsoft trocou aprisionamento por
   elegibilidade.

5. **Parada legítima — economia de plataforma.**
   A decisão decorre de uma dinâmica de mercado bem conhecida: em plataformas, o vencedor
   é quem **reduz o custo de integração** para o cliente, não quem tem o melhor componente
   isolado. É a mesma lógica que fez o Office vencer produtos individualmente melhores nos
   anos 1990, e a mesma que explica por que o Power BI venceu o Tableau
   ([`11-historia.md`](11-historia.md) §9). **A Microsoft é muito boa nisso.**

---

## 9. Autoteste

1. O que é o Fabric, em uma frase? Qual é a tese "one copy"?
2. O que é o OneLake e por que o formato aberto importa?
3. Diferencie Lakehouse e Warehouse, e diga como escolher.
4. Explique o posicionamento arquitetural do Direct Lake.
5. Cite duas coisas que o Copilot faz bem e duas que ele faz mal.
6. Por que "a qualidade da IA é limitada pela qualidade do modelo" é uma boa notícia?
7. Cite três situações em que o Fabric **não** é a escolha certa.
8. Qual é o ponto em que o Fabric passa a fazer sentido?
9. Qual tendência do ecossistema mais afeta quem faz BI, e o que estudar por causa dela?
10. Explique, com economia de plataforma, por que a Microsoft criou o Fabric.

---

**Próximo:** [`27-alternativas.md`](27-alternativas.md) — quando não usar Power BI.

---

*Fontes consultadas em 14/08/2026: [Microsoft Learn — Direct Lake overview](https://learn.microsoft.com/en-us/fabric/fundamentals/direct-lake-overview); [Microsoft Learn — Power BI Semantic Model Authoring skill](https://learn.microsoft.com/en-us/power-bi/developer/agentic/semantic-model-authoring-skill-overview); [Fabric Community — composite semantic models com Direct Lake](https://community.fabric.microsoft.com/t5/Power-BI-Updates-Blog/Deep-dive-into-composite-semantic-models-with-Direct-Lake-and/ba-p/5173943); preço de F2 conforme compilações de terceiros e a [calculadora do Azure](https://azure.microsoft.com/pricing/calculator/) — ver [`80-custos-e-licencas.md`](80-custos-e-licencas.md).*
