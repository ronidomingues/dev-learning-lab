# 80 — Custos e licenças

**Data da consulta de preços: 13/08/2026.** Preço sem data é desinformação;
esta seção envelhece em meses. Câmbio usado para a ordem de grandeza:
**US$ 1 ≈ R$ 5,40** (aproximado — confira o câmbio do dia antes de usar
qualquer número destes em proposta).

---

## A resposta curta

> **Aprender SQL custa R$ 0,00. Fazer tudo neste curso custa R$ 0,00.**
> O SQLite é domínio público, o PostgreSQL e o DuckDB são open-source
> permissivos, e o Python é gratuito. Nada aqui exige cadastro, e-mail ou
> cartão de crédito.

O custo aparece em três lugares, e nenhum deles é a linguagem:
**licença de banco proprietário** (Oracle, SQL Server), **nuvem** (computação,
armazenamento, egresso) e **pessoas** (o item mais caro, sempre).

---

## 1. Quem paga a conta do gratuito

Pergunta legítima. Software gratuito bom tem alguém pagando.

| Projeto | Quem sustenta |
|---|---|
| **SQLite** | Consórcio de patrocinadores (Bloomberg, Bentley Systems, Expensify) contratando suporte e testes. O código é domínio público; o **suporte é vendido** |
| **PostgreSQL** | Empresas que vendem serviço em cima: EDB, Crunchy Data, Percona, Cybertec, e as nuvens. Elas pagam os desenvolvedores centrais |
| **DuckDB** | DuckDB Labs (empresa dos autores, vende suporte e consultoria) + MotherDuck (produto na nuvem). Nasceu no CWI, instituto público holandês |
| **Python** | Python Software Foundation, patrocinada por grandes empresas |

**O risco real de cada modelo:** nenhum deles depende de uma única empresa que
possa mudar a licença de uma hora para outra — ao contrário do que aconteceu
com Redis (2024), Elasticsearch (2021), MongoDB (2018), Terraform (2023) e
outros que migraram de open-source para licença restritiva. **SQLite,
PostgreSQL e DuckDB não podem fazer isso**, por razões jurídicas: o SQLite não
tem copyright para revogar, e PostgreSQL e DuckDB têm copyright distribuído
entre centenas de contribuidores sob licenças irrevogáveis.

Isso não é detalhe. É a garantia de que o que você aprender continua
disponível.

---

## 2. Licenças

| Software | Licença | Uso comercial | Fechar o código | Obrigações |
|---|---|---|---|---|
| **SQLite** | **Domínio público** | Livre | Livre | **Nenhuma.** Nem atribuição |
| **PostgreSQL** | Licença PostgreSQL (tipo BSD/MIT) | Livre | Livre | Manter o aviso de copyright |
| **DuckDB** | MIT | Livre | Livre | Manter o aviso |
| **MySQL** | GPLv2 **ou** comercial | Livre para uso | **Não**, se distribuir vinculado | Licença dupla: distribuir produto fechado com MySQL embutido exige comprar |
| **MariaDB** (servidor) | GPLv2 | Livre | Idem | Bifurcação do MySQL, feita pelo autor original |
| **DB Browser for SQLite** | GPLv3 / MPL 2.0 | Livre | — | |
| **DBeaver Community** | Apache 2.0 | Livre | — | A versão Enterprise é paga |
| **Oracle / SQL Server / SAP HANA** | Proprietária | **Pago** | — | Ver abaixo |

**A pegadinha do MySQL** (licença dupla) só afeta quem **distribui** software
com MySQL embutido. Usar MySQL num servidor da empresa é livre. Mas se você
vende um produto empacotado com MySQL dentro, precisa da licença comercial —
e é por isso que muito produto embarcado usa SQLite ou PostgreSQL.

---

## 3. Bancos proprietários — os preços de lista

Preços de lista. **Ninguém paga o preço de lista**; desconto de 40–80% é
rotina em negociação corporativa. Servem para ordem de grandeza.

### Oracle Database (lista de abril/2026)

| Item | Preço | ≈ BRL |
|---|---|---|
| Enterprise Edition | **US$ 47.500 por processador** | ~R$ 257 mil |
| Named User Plus | US$ 950 por usuário (mín. 25/proc.) | ~R$ 5,1 mil |
| Opção Partitioning | US$ 11.500 por processador | ~R$ 62 mil |
| EE totalmente equipada | ~US$ 122.000 por processador | ~R$ 659 mil |
| Suporte anual | ~22% do valor de licença | |

⚠️ **"Processador" no Oracle não é o que você pensa.** É o número de núcleos
multiplicado por um "fator de núcleo" que depende do modelo do processador
(0,5 para x86 típico). Um servidor de 32 núcleos x86 conta como 16
processadores. **Fazer essa conta errado é o achado mais caro de auditoria de
licença que existe** — e a Oracle audita.

### Microsoft SQL Server 2025

| Edição | Preço (pacote de 2 núcleos) | ≈ BRL |
|---|---|---|
| Enterprise | **US$ 15.123** | ~R$ 81,7 mil |
| Standard | **US$ 3.945** | ~R$ 21,3 mil |
| **Express** | **Gratuito** | — |
| **Developer** | **Gratuito** (não-produção) | — |

Mínimo de 4 núcleos por processador. Preços de lista **inalterados desde
2022**.

**A Express merece nota:** gratuita, limite de 10 GB por banco, 1 GB de RAM,
1 processador. Para um banco de apoio de área de engenharia, **cabe** — e é
aprovada por qualquer TI porque é Microsoft.

### SAP HANA

Preço sob contrato, tipicamente vinculado ao contrato SAP. Se sua planta tem
SAP, o custo já está pago; o problema é acesso, não licença.

---

## 4. Nuvem

### PostgreSQL gerenciado

| Serviço | Camada gratuita | Entrada paga (ordem de grandeza) |
|---|---|---|
| **Neon** | 0,5 GB, projeto hiberna. **Sem cartão** | ~US$ 19/mês |
| **Supabase** | 500 MB, pausa após 1 semana inativa. **Sem cartão** | ~US$ 25/mês |
| **AWS RDS** | 12 meses de camada gratuita (db.t4g.micro) | ~US$ 15–30/mês para instância pequena |
| **AWS Aurora** | — | **15–40% acima** do RDS equivalente, **mais cobrança por E/S** |
| **Azure / Google Cloud SQL** | Crédito inicial | Comparável ao RDS |

⚠️ **O Aurora cobra E/S separadamente.** Para 100 milhões de operações de E/S
por mês, são ~US$ 20/mês só de E/S; para 2 bilhões, ~US$ 400/mês. Numa carga
de série temporal, que é de E/S intensiva, **essa linha pode dominar a fatura**
e não aparece em nenhuma calculadora simplificada.

### Data warehouse na nuvem

| Serviço | Modelo | Preço (13/08/2026) |
|---|---|---|
| **BigQuery** | Por TB **varrido** | ~US$ 6,25 por TiB, com camada gratuita mensal |
| **Snowflake** | Por crédito de computação | US$ 2–4/crédito sob demanda; US$ 1,50–2,50 com compromisso anual. Armazenamento ~US$ 23/TB/mês (AWS us-east) |
| **Databricks** | Por DBU + a instância da nuvem | Varia por camada; **você paga os dois** |

⚠️ **O modelo "por TB varrido" do BigQuery pune `SELECT *`.** Uma consulta que
lê 1 TB custa US$ 6,25. A mesma consulta pedindo três colunas em vez de
quarenta, sobre dado particionado, pode ler 20 GB e custar US$ 0,12. **Aqui,
saber SQL é literalmente dinheiro** — e é o argumento mais direto que existe
para o conteúdo de [21-indices-e-desempenho.md](21-indices-e-desempenho.md).

---

## 5. Custos ocultos

Os que não aparecem na proposta:

| Custo | Ordem de grandeza | Observação |
|---|---|---|
| **Egresso de dados** | US$ 0,05–0,12 por GB | Tirar dado da nuvem custa; **colocar é grátis**. Não é acidente |
| **Backup e retenção** | 20–100% do custo de armazenamento | Frequentemente esquecido no orçamento |
| **Alta disponibilidade** | **2× o custo de computação** | Réplica ociosa esperando |
| **Suporte** | 10–25% da licença/ano | Obrigatório na prática em banco proprietário |
| **Migração para fora** | Semanas a meses de trabalho | O verdadeiro custo do aprisionamento |
| **Treinamento** | R$ 3–15 mil por pessoa em curso oficial | Ou zero, com este material |
| **Tempo de pessoas** | **O maior de todos** | Um engenheiro-hora de R$ 120 × 8 h/mês de relatório manual = R$ 11,5 mil/ano, **por relatório** |

**A conta que justifica aprender SQL**, e que vale fazer com os seus números:

> Um relatório mensal que consome 8 horas de trabalho manual custa
> ~R$ 11,5 mil por ano. Automatizá-lo leva de 8 a 40 horas **uma vez**.
> Retorno em menos de um ano, e depois disso é lucro — sem contar que o
> relatório automatizado é reprodutível e auditável, e o manual não é.

---

## 6. Aprisionamento (*vendor lock-in*)

| Onde | Grau | Por quê |
|---|---|---|
| SQL padrão | **Baixo** | ~85% portátil |
| Procedimentos armazenados | **Alto** | PL/SQL, T-SQL e PL/pgSQL são linguagens diferentes |
| Recursos proprietários | Alto | `CONNECT BY`, tipos específicos, particionamento |
| Ferramentas de BI acopladas | Médio-alto | Modelo semântico não se exporta |
| Data warehouse na nuvem | **Alto** | Dado dentro do formato proprietário |
| **Parquet + Iceberg** | **Baixo** | O dado é seu, em formato aberto; troca-se o motor |

**A recomendação estratégica de 2026:** guarde o histórico frio em **Parquet
com catálogo Iceberg**, no seu próprio armazenamento de objetos, e aponte o
motor que quiser (DuckDB, Trino, Spark, Snowflake). Isso reduz aprisionamento
de forma real e mensurável. Ver [65-estado-da-arte.md](65-estado-da-arte.md).

---

## 7. O caso específico do dado de planta

| Item | Custo típico |
|---|---|
| Licença de historiador (PI System, IP.21, PHD) | Dezenas a centenas de milhares de reais/ano, por tag ou por servidor |
| Licença de analítica (Seeq, TrendMiner) | Por usuário nomeado, na casa das dezenas de milhares de reais/ano |
| **PostgreSQL + TimescaleDB no servidor da empresa** | **R$ 0 de licença**; custo é hardware e o seu tempo |
| **DuckDB sobre exportação em Parquet** | **R$ 0** |

**Opinião profissional, declarada como opinião:** para a maioria das plantas,
a decisão certa **não** é substituir o historiador — ele funciona, está
validado, e a substituição é um projeto de anos com risco operacional. A
decisão certa é **extrair dele** para um banco aberto onde você possa cruzar
com LIMS, ERP, CMMS e apontamento. Isso custa quase nada em licença, resolve o
problema que o historiador não resolve, e não exige aprovação de investimento.

---

## 8. Alternativas gratuitas, e o que se perde

| Se você usa | Alternativa gratuita | O que perde |
|---|---|---|
| Oracle | PostgreSQL | RAC, Exadata, suporte 24×7 contratual, alguns recursos de partição |
| SQL Server | PostgreSQL | Integração com Active Directory, SSIS/SSRS, ferramental gráfico |
| SQL Server (pequeno) | **SQL Server Express** | Limite de 10 GB e 1 GB de RAM |
| Snowflake / BigQuery | DuckDB + Parquet | Escala além de uma máquina; concorrência de muitos usuários |
| Tableau / Power BI Pro | **Metabase**, **Apache Superset** | Polimento, integração com Office, suporte |
| Seeq / TrendMiner | PostgreSQL + Python + Grafana | Muito tempo de desenvolvimento e a análise exploratória fácil |
| PI System | TimescaleDB + coletor OPC-UA | Anos de validação, conectores prontos, suporte, e a confiança da operação |

**A honestidade sobre a última linha:** substituir um historiador validado por
uma pilha aberta é tecnicamente possível e organizacionalmente muito difícil.
Não recomendo como primeiro projeto.

---

## Autoteste

1. Quanto custa aprender e praticar tudo deste curso?
2. Quem paga a conta do SQLite, do PostgreSQL e do DuckDB?
3. Por que SQLite, PostgreSQL e DuckDB **não podem** mudar de licença como o
   Redis fez?
4. Qual a pegadinha da licença dupla do MySQL, e quem ela afeta?
5. Por que "processador" no Oracle não é o que parece, e por que isso é caro?
6. Por que o modelo do BigQuery pune `SELECT *`? Faça a conta.
7. Cite três custos ocultos de nuvem e a ordem de grandeza de cada.
8. Faça a conta do retorno de automatizar um relatório mensal manual.
9. Onde o aprisionamento é baixo e onde é alto? Qual a estratégia de 2026?
10. Você deve substituir o historiador da sua planta? Por quê?

---

## Fontes consultadas (13/08/2026)

- Oracle Technology Price List 2026 (via análise de terceiros) —
  <https://redresscompliance.com/oracle-technology-price-list.html>
- SQL Server 2025 pricing (Microsoft) —
  <https://cdn-dynmedia-1.microsoft.com/is/content/microsoftcorp/microsoft/bade/documents/products-and-services/en-us/cloud/SQL-Server-2025-Pricing.pdf>
- Snowflake / Databricks / BigQuery 2026 —
  <https://tech-insider.org/snowflake-vs-databricks-vs-bigquery-2026/> e
  <https://mammoth.io/blog/snowflake-pricing/>
- Amazon RDS e Aurora 2026 — <https://www.cloudzero.com/blog/rds-pricing/> e
  <https://cloudburn.io/blog/amazon-aurora-pricing>
- SQLite: copyright e domínio público — <https://sqlite.org/copyright.html>
- Licença PostgreSQL — <https://www.postgresql.org/about/licence/>

⚠️ Preços de Oracle e das plataformas de nuvem foram obtidos de compiladores
de terceiros, não de tabelas oficiais publicadas — a Oracle não publica preço
abertamente. Trate como **ordem de grandeza**, e peça proposta.

---

*Próximo: [85-cursos-e-certificacoes.md](85-cursos-e-certificacoes.md).*
