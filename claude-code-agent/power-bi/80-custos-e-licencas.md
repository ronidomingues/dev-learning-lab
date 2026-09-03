# 80 · Custos e licenças

**Nível:** todos
**Data da consulta de preços: 14/08/2026**
**Câmbio usado: US$ 1,00 ≈ R$ 5,19** (cotação comercial de 14/08/2026; use a do dia)

> **Preço sem data é desinformação.** Este arquivo tem data em tudo. A Microsoft reajustou
> os preços do Power BI em abril de 2025, depois de dez anos sem mexer — pode reajustar de
> novo. **Confirme na fonte antes de decidir.**
>
> Separei o que veio da **página oficial da Microsoft** do que veio de **compilações de
> terceiros**. A diferença importa: números de terceiros variam por região e por
> interpretação.

---

## 1. Resposta rápida

| Você é… | Você paga |
|---|---|
| Estudante aprendendo sozinho | **R$ 0** — o Desktop é gratuito e completo |
| Analista que só constrói e não compartilha | **R$ 0** |
| Time de 10 pessoas compartilhando | 10 × Pro ≈ **US$ 140/mês** (≈ R$ 727/mês) |
| Empresa com 50 autores e 500 leitores | Capacidade **F64** + 50 Pro — ver §5 |
| Empresa que quer Fabric completo | A partir de ~**US$ 262/mês** (F2), mas veja §6 |

---

## 2. Licenças por usuário — **dados oficiais**

Da página oficial de preços do Power BI, consultada em **14/08/2026**:

| Plano | Preço | Em BRL (aprox.) |
|---|---|---|
| **Free** (Fabric Free) | **US$ 0** — sem cartão de crédito | R$ 0 |
| **Power BI Pro** | **US$ 14,00 por usuário/mês**, pago anualmente | ≈ R$ 73/usuário/mês |
| **Power BI Premium Per User (PPU)** | **US$ 24,00 por usuário/mês**, pago anualmente | ≈ R$ 125/usuário/mês |
| **Power BI Embedded** | preço variável — falar com vendas | — |

**Histórico** (importante para planejamento): até abril de 2025, Pro custava US$ 10 e PPU
custava US$ 20. O reajuste foi de **+40%** e **+20%**, respectivamente, e foi o primeiro
desde 2015.

**Incluído no Microsoft 365 E5:** o Power BI Pro vem incluído, sem cobrança separada.
Se sua empresa tem E5, **você provavelmente já tem Pro** e não sabe. Confira antes de
comprar.

### O que cada plano permite

| Recurso | Free | Pro | PPU |
|---|---|---|---|
| Power BI Desktop | ✔ | ✔ | ✔ |
| Publicar no **Meu workspace** | ✔ | ✔ | ✔ |
| **Compartilhar** com outra pessoa | ✘ | ✔ | ✔ |
| Consumir conteúdo de outros | ✘¹ | ✔ | ✔ |
| Workspaces de equipe | ✘ | ✔ | ✔ |
| Publicar apps | ✘ | ✔ | ✔ |
| Tamanho máximo do modelo | 1 GB | 1 GB | **100 GB** |
| Atualizações agendadas/dia | 8 | 8 | **48** |
| Duração máxima do refresh | 2 h | 2 h | 5 h |
| Atualização incremental | ✔ | ✔ | ✔ |
| Endpoint **XMLA** (leitura/gravação) | ✘ | ✘ | **✔** |
| Deployment pipelines | ✘ | ✘ | **✔** |
| Relatórios paginados | ✘ | ✘ | **✔** |
| Direct Lake | ✘ | ✘ | ✔ (com Fabric) |
| Copilot | ✘ | ✘ | conforme capacidade |

¹ *Exceção importante:* usuários **Free** conseguem **visualizar** conteúdo hospedado em
capacidade **F64 ou maior**, com a função Visualizador. É a regra que define toda a
economia do §5.

### A única forma de "compartilhar" sem licença

**Publicar na Web** — que torna o relatório **público na internet, sem login e indexável
por buscadores**. Não é compartilhamento; é publicação. Ver
[`24-seguranca-e-governanca.md`](24-seguranca-e-governanca.md) §5.

---

## 3. Onde a camada gratuita acaba

O plano **Free** é generoso e limitado de forma bem definida:

**Cabe na camada gratuita:**
- todo o Power BI Desktop, sem restrição de recursos;
- conectar-se a qualquer fonte, modelar, escrever DAX, criar relatórios;
- publicar no **Meu workspace** e usar no navegador e no celular;
- consumir conteúdo hospedado em capacidade F64+;
- exportar para PDF, PowerPoint e Excel;
- salvar `.pbix` e PBIP localmente.

**Onde ela acaba — o ponto exato:**
> No instante em que **outra pessoa** precisa ver o seu relatório de forma privada.

Não há meio-termo, não há "até 3 usuários grátis", não há período de carência. É o
modelo de negócio: a ferramenta de autoria é isca; a distribuição é o produto.

**Consequência de planejamento:** o custo aparece exatamente no momento do sucesso —
quando o relatório provou valor e as pessoas querem acesso. Coloque isso no orçamento
**antes** de começar, não depois.

---

## 4. Capacidades Fabric (F-SKU)

> **Aviso de origem:** a página oficial de preços do Power BI não lista os valores dos
> F-SKU (remete à calculadora do Azure). Os números abaixo vêm de **compilações de
> terceiros consultadas em 14/08/2026** e devem ser tratados como **ordem de grandeza**.
> Preços variam por região (±10–15%) e por moeda. **Confirme na calculadora do Azure.**

| SKU | CU | Pay-as-you-go (mês) | Reservado 1 ano (mês) | BRL aprox. (PAYG) |
|---|---:|---:|---:|---:|
| **F2** | 2 | ≈ US$ 262 | ≈ US$ 156 | ≈ R$ 1.360 |
| F4 | 4 | ≈ US$ 525 | ≈ US$ 312 | ≈ R$ 2.725 |
| F8 | 8 | ≈ US$ 1.050 | ≈ US$ 623 | ≈ R$ 5.450 |
| F16 | 16 | ≈ US$ 2.100 | ≈ US$ 1.246 | ≈ R$ 10.900 |
| F32 | 32 | ≈ US$ 4.200 | ≈ US$ 2.491 | ≈ R$ 21.800 |
| **F64** ★ | 64 | ≈ US$ 8.410 | ≈ US$ 4.982 | ≈ R$ 43.650 |
| F128 | 128 | ≈ US$ 16.800 | ≈ US$ 9.964 | ≈ R$ 87.200 |

**Base de cálculo:** aproximadamente **US$ 0,18 por CU-hora** em regiões dos EUA, em
regime pay-as-you-go. A reserva anual economiza cerca de **40%** — a página oficial da
Microsoft menciona **40,5%** de economia na compra anual.

**O que muda com o tamanho do SKU:** tamanho máximo do modelo em memória, número de
consultas simultâneas, tamanho do refresh, e — o mais importante — o **corte do F64**.

### 4.1 A regra do F64 — a decisão econômica central

> **A partir do F64**, usuários **sem licença paga** podem **visualizar** conteúdo
> hospedado naquela capacidade (com a função Visualizador). Abaixo do F64, todo consumidor
> precisa de **Power BI Pro**.

Isso cria um degrau brutal no custo, e é a conta que todo gestor de BI precisa saber fazer:

| Nº de leitores | Só Pro (US$ 14 cada) | F64 (≈ US$ 8.410) | Vencedor |
|---:|---:|---:|---|
| 100 | US$ 1.400/mês | US$ 8.410/mês | **Pro** |
| 300 | US$ 4.200/mês | US$ 8.410/mês | **Pro** |
| **600** | **US$ 8.400/mês** | **US$ 8.410/mês** | **empate** |
| 1.000 | US$ 14.000/mês | US$ 8.410/mês | **F64** |
| 5.000 | US$ 70.000/mês | US$ 8.410/mês | **F64, com folga** |

**O ponto de equilíbrio fica em torno de 600 leitores** no regime pay-as-you-go, e cai
para cerca de **355 leitores** com reserva anual (US$ 4.982 ÷ US$ 14).

**Atenção:** mesmo com F64, os **autores** (quem publica) continuam precisando de **Pro**.
A conta real de uma empresa com 50 autores e 1.000 leitores é:

```
F64 reservado             ≈ US$ 4.982/mês
50 × Pro                  =  US$   700/mês
                            ─────────────
Total                     ≈ US$ 5.682/mês   ≈ R$ 29.490/mês
```

contra US$ 14.700/mês só com Pro. **Economia de ~61%.**

### 4.2 Armadilha do dimensionamento

O F64 resolve o problema de licença, mas você precisa que a **capacidade aguente a carga**.
Um F64 com 1.000 usuários fazendo consultas pesadas entra em *throttling* e degrada tudo.

**Sintoma:** "de repente ficou tudo lento e ninguém mudou nada."

**Prevenção:** instale o app **Fabric Capacity Metrics** desde o primeiro dia e monitore
*overload* e *carryforward*. Ver [`22-desempenho.md`](22-desempenho.md) §7.

---

## 5. Outras modalidades

### 5.1 Power BI Embedded

Para embutir relatórios no **seu** produto, para **seus** clientes.

| Cenário | Como funciona | Licença |
|---|---|---|
| **App owns data** | Sua aplicação autentica com uma identidade de serviço; o usuário final não tem conta no seu locatário | **Capacidade** (F-SKU) |
| **User owns data** | Cada usuário entra com a própria conta | Licença por usuário |

**Nota:** os antigos **A-SKU** foram absorvidos pela transição para F-SKU. Para projetos
novos, planeje com F-SKU.

**Custo escondido do Embedded:** desenvolvimento. Autenticação, tokens, *row-level security*
por cliente, ciclo de vida de workspaces por inquilino. Não é "colocar um iframe".

### 5.2 Power BI Report Server (on-premises)

Duas formas de licenciar:

1. **Power BI Premium / capacidade** — o direito de usar o Report Server vem junto;
2. **SQL Server Enterprise com Software Assurance** — direito incluído.

**Quando faz sentido:** restrição legal ou regulatória de que o dado não saia da empresa.

**O que você perde:** Fabric, Direct Lake, Copilot, dataflows, apps, pipelines de
implantação, e recursos com 6 a 12 meses de atraso. Ver
[`12-arquitetura.md`](12-arquitetura.md) §4.2.

### 5.3 Ferramentas de terceiros

| Ferramenta | Custo | Nota |
|---|---|---|
| **DAX Studio** | **Grátis**, código aberto | Essencial |
| **Tabular Editor 2** | **Grátis**, código aberto | Essencial. Continua mantido |
| **Tabular Editor 3** | Pago, assinatura por usuário (Desktop / Business / Enterprise), mensal ou anual com 17% de desconto | A página de preços consultada em 14/08/2026 não renderizou os valores; consulte `tabulareditor.com/pricing` |
| **Bravo for Power BI** | **Grátis** | Tabela de datas, formatação, análise |
| **ALM Toolkit** | **Grátis** | Comparação e mesclagem de modelos |
| **Measure Killer** | Freemium | Achar objetos não usados |
| **Visuais customizados (AppSource)** | Muitos gratuitos; vários pagos por usuário/ano | Avalie certificação e segurança |
| **PowerBI.Tips, Deneb, etc.** | Variados | — |

**Ponto que merece registro:** o ecossistema gratuito de ferramentas do Power BI é
excepcionalmente bom. DAX Studio, Tabular Editor 2 e Bravo são software profissional,
mantidos por pessoas da comunidade (Marco Russo, Alberto Ferrari, Daniel Otykier, Darren
Gosbell e outros), sem custo. Isso é raro e vale reconhecer.

---

## 6. Custos ocultos

O item da licença é o mais fácil de prever. Estes não são.

| Custo oculto | Ordem de grandeza | Como controlar |
|---|---|---|
| **Pessoa que mantém** | 0,3 a 2 FTE por área de negócio | O maior custo de todos, e o mais ignorado |
| **Servidor de gateway** | R$ 500 a 2.000/mês | Dimensione desde o começo; cluster |
| **Egress de nuvem** | Variável | DirectQuery para fontes na nuvem gera tráfego |
| **Custo de consulta na fonte** | Alto em Snowflake/BigQuery | **DirectQuery pode multiplicar sua conta de banco por 10** |
| **Treinamento** | R$ 500 a 5.000/pessoa | Comece pelos cursos gratuitos ([`85`](85-cursos-e-certificacoes.md)) |
| **Certificações** | ≈ US$ 165/exame | Ver [`85`](85-cursos-e-certificacoes.md) |
| **Consultoria de implantação** | R$ 20.000 a 500.000 | Avalie fazer internamente o primeiro projeto |
| **Migração de outra ferramenta** | Meses de trabalho | Não é conversão automática |
| **Retrabalho por má modelagem** | Incalculável | É por isso que [`14`](14-modelagem-dimensional.md) existe |
| **Reajuste de preço** | +40% aconteceu em 2025 | Revise licenciamento anualmente |
| **Capacidade superdimensionada** | Milhares/mês desperdiçados | Fabric Capacity Metrics |

**O custo mais subestimado, com folga, é o primeiro.** Um Power BI corporativo sem alguém
dedicado a mantê-lo vira, em 18 meses, um cemitério de relatórios quebrados que ninguém
confia. Orçamento de BI que só prevê licença está errado por construção.

**O segundo mais subestimado é o custo de consulta na fonte com DirectQuery.** Já vi conta
de data warehouse triplicar em um mês depois de um relatório DirectQuery ganhar 200
usuários. Meça antes.

---

## 7. Licenças de software (o outro sentido de "licença")

| Componente | Licença | O que permite |
|---|---|---|
| Power BI Desktop | **Proprietária, gratuita** | Uso comercial permitido; sem redistribuição |
| Power BI Service | Proprietária, assinatura | — |
| DAX Studio | **MIT** (código aberto) | Uso e modificação livres |
| Tabular Editor 2 | **MIT** | Idem |
| Tabular Editor 3 | Proprietária, comercial | — |
| Bravo for Power BI | **MIT** | — |
| ALM Toolkit | **MIT** | — |
| Formato **Delta Lake / Parquet** (OneLake) | **Apache 2.0** ★ | Seus dados são legíveis por qualquer ferramenta |
| DAX e M (as linguagens) | Especificação proprietária | Sem implementação alternativa |

**O item mais estratégico da tabela é o Delta/Parquet.** Se você sair do Fabric, os dados
continuam legíveis por Spark, DuckDB, pandas, Polars ou Databricks. Isso reduz muito o
aprisionamento de **dados** — mas não o de **lógica**: DAX e M não têm equivalente fora do
ecossistema Microsoft.

**Mitigação de aprisionamento, e é a mais valiosa deste arquivo:**

> Mantenha as **regras de negócio estáveis na fonte**, em SQL versionado. Deixe no DAX
> apenas o que **depende do contexto de visualização**. Um modelo fino sobre um data
> warehouse bem feito é substituível em semanas; um modelo com 300 medidas contendo regras
> que não existem em lugar nenhum é um casamento sem divórcio.

---

## 8. Alternativas gratuitas ou open source

| Ferramenta | Licença | O que você ganha | O que perde |
|---|---|---|---|
| **Metabase** | AGPL (+ edição paga) | Sem licença por usuário; rápido de subir; SQL direto | Sem modelo em memória; camada semântica fraca |
| **Apache Superset** | Apache 2.0 | Muito flexível; muitos gráficos | Operação complexa; curva íngreme |
| **Redash** | BSD | Simples, focado em SQL | Recursos limitados |
| **Grafana** | AGPL | Excelente para séries temporais e observabilidade | Não é BI de negócio |
| **Streamlit / Dash / Observable** | Apache/MIT | Controle total | Você reimplementa tudo |
| **Excel** | Proprietária (já paga) | Todo mundo sabe usar | Não escala nem governa |

**O que se perde ao trocar Power BI por open source, em uma lista honesta:**

1. o **modelo em memória** com compressão — desempenho passa a depender do seu banco;
2. a **camada semântica** com medidas reutilizáveis e RLS integrada;
3. o **autosserviço**: o usuário de negócio não constrói nada sozinho no Metabase/Superset;
4. a integração com Excel, Teams e Office;
5. o **mercado de profissionais** — no Brasil, encontrar quem saiba Power BI é ordens de
   grandeza mais fácil.

**O que se ganha:** ausência de licença por usuário, portabilidade, e nenhuma dependência
de Windows.

**A conta que ninguém faz:** "grátis" ignora hospedagem, atualização, monitoramento e
sustentação. Para 50 usuários, meia pessoa dedicada custa mais que 50 licenças Pro. Open
source compensa quando o público é grande, técnico, e você já tem time de infraestrutura.

---

## 9. Cinco cenários com a conta feita

*(Câmbio de 14/08/2026: US$ 1,00 ≈ R$ 5,19. Valores mensais.)*

### Cenário A — Você, estudando
**Custo: R$ 0.** Desktop + conta Fabric Free. Se precisar publicar, veja
[`03-instalacao.md`](03-instalacao.md) §9 sobre obter um locatário.

### Cenário B — Pequena empresa, 12 pessoas
12 × Pro = **US$ 168/mês ≈ R$ 872/mês**.
Se já tiverem Microsoft 365 E5, **R$ 0 adicional**. Verifique antes de comprar.

### Cenário C — Média empresa, 25 autores e 250 leitores
275 × Pro = **US$ 3.850/mês ≈ R$ 19.980/mês**.
F64 não compensa (custaria mais). **Fique no Pro.**

### Cenário D — Grande empresa, 60 autores e 1.500 leitores
```
F64 reservado 1 ano        ≈ US$ 4.982/mês
60 × Pro                   =  US$   840/mês
Gateway (2 nós)            ≈ US$   400/mês
                             ──────────────
Total                      ≈ US$ 6.222/mês  ≈ R$ 32.290/mês
```
Contra 1.560 × Pro = US$ 21.840/mês. **Economia de ~71%.**
Some 1 a 2 pessoas dedicadas — o custo real fica bem acima da linha de licença.

### Cenário E — Software house embutindo relatórios
F-SKU dimensionado pela carga (comece pequeno e monitore) + desenvolvimento de
autenticação e multi-inquilino. **O desenvolvimento costuma custar mais que a capacidade
no primeiro ano.**

---

## 10. Checklist antes de assinar qualquer coisa

- [ ] Verifiquei se já temos Pro incluído no Microsoft 365 E5.
- [ ] Contei **autores** e **leitores** separadamente.
- [ ] Calculei o ponto de equilíbrio do F64 para o nosso número de leitores.
- [ ] Comparei pay-as-you-go com reserva anual (≈40% de diferença).
- [ ] Orcei o **servidor de gateway**, se houver fonte on-premises.
- [ ] Estimei o custo de **consulta na fonte** se formos usar DirectQuery.
- [ ] Alocei **pessoas** para manter — não só licenças.
- [ ] Confirmei os preços na fonte oficial **na data de hoje**.
- [ ] Documentei quem revisa o licenciamento e com que periodicidade (sugestão: anual).

---

## 11. Autoteste

1. Quanto custa Pro e PPU por usuário/mês, em 14/08/2026? Quanto custavam antes de abril
   de 2025?
2. Exatamente onde acaba a camada gratuita?
3. Qual é a única forma de "compartilhar" sem licença, e por que ela é perigosa?
4. O que muda a partir do F64, e qual é o ponto de equilíbrio em número de leitores?
5. Autores precisam de licença mesmo com F64? Qual?
6. Cite os três custos ocultos mais subestimados.
7. Que licença tem o formato de armazenamento do OneLake, e por que isso importa?
8. Qual é a mitigação mais valiosa contra aprisionamento?
9. Cite cinco coisas que se perde ao trocar Power BI por open source.
10. Numa empresa de 250 leitores, F64 compensa? Faça a conta.

---

*Fontes consultadas em 14/08/2026 — **oficiais**: [Microsoft — Power BI pricing](https://www.microsoft.com/en-us/power-platform/products/power-bi/pricing) (Free, Pro US$ 14, PPU US$ 24, Embedded, reserva anual com 40,5% de economia). **Terceiros** (ordem de grandeza, confirmar na [calculadora do Azure](https://azure.microsoft.com/pricing/calculator/)): compilações de preços de F-SKU e a taxa de ~US$ 0,18/CU-hora; preço do exame PL-300 (US$ 165). **Câmbio**: cotação comercial USD/BRL de 14/08/2026 (≈ 5,19). **Licenças de ferramentas**: [Tabular Editor — pricing](https://tabulareditor.com/pricing); repositórios de DAX Studio, Tabular Editor 2, Bravo e ALM Toolkit no GitHub.*
