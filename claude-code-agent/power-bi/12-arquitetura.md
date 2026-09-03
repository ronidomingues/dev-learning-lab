# 12 · Arquitetura — as peças e o que roda onde

**Nível:** intermediário
**Data:** 14/08/2026

Saber **onde** cada coisa executa explica quase todo comportamento estranho: por que o
relatório é rápido no Desktop e lento na nuvem, por que a atualização falha só em
produção, por que uma medida funciona e outra estoura o tempo limite.

---

## 1. Visão geral

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  SUA MÁQUINA (Windows)                                                      │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │  POWER BI DESKTOP  (PBIDesktop.exe)                                   │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌────────────────────────────┐   │  │
│  │  │  Mashup      │  │ Analysis     │  │  Camada de relatório       │   │  │
│  │  │  Engine (M)  │─►│ Services     │◄─│  (WebView2 / Chromium)     │   │  │
│  │  │  Power Query │  │ (msmdsrv.exe)│  │  visuais, filtros, layout  │   │  │
│  │  └──────┬───────┘  │  VertiPaq +  │  └────────────────────────────┘   │  │
│  │         │          │  Motor DAX   │                                   │  │
│  │         │          └──────────────┘                                   │  │
│  └─────────┼───────────────────────────────────────────────────────────┬─┘  │
└────────────┼───────────────────────────────────────────────────────────┼────┘
             │ lê das fontes                                  publica    │
             ▼                                                           ▼
┌──────────────────────────┐              ┌────────────────────────────────────┐
│  FONTES DE DADOS         │              │  POWER BI SERVICE (nuvem)          │
│  SQL, Excel, API, SAP,   │              │  ┌──────────────────────────────┐  │
│  SharePoint, OneLake…    │◄─────────────┤  │ Capacidade (Fabric/Pro)      │  │
└──────────────────────────┘   gateway    │  │  · motor AS (mesmo código!)  │  │
             ▲                            │  │  · Mashup Engine             │  │
             │                            │  │  · agendador de refresh      │  │
   ┌─────────┴──────────┐                 │  └──────────────────────────────┘  │
   │  ON-PREMISES DATA  │                 │  workspaces · apps · segurança     │
   │  GATEWAY           │◄────────────────┤  XMLA endpoint · APIs REST         │
   │  (servidor da      │  Service Bus    └──────────┬─────────────────────────┘
   │   empresa)         │                            │
   └────────────────────┘                            ▼
                                    ┌────────────┬─────────────┬──────────────┐
                                    │  Navegador │   Mobile    │ Teams/Excel/ │
                                    │            │  iOS/Android│  PowerPoint  │
                                    └────────────┴─────────────┴──────────────┘
```

---

## 2. Power BI Desktop, por dentro

O Desktop **não é um programa**. São três motores num invólucro.

### 2.1 Mashup Engine (Power Query)

Executa código **M**. Conecta às fontes, transforma, e entrega tabelas ao motor tabular.

- Processo: dentro do `PBIDesktop.exe`, e também em `Microsoft.Mashup.Container.exe`
  (um contêiner por avaliação — é por isso que você vê vários no Gerenciador de Tarefas).
- Roda **no refresh**, não na consulta.
- Faz *query folding* quando possível: traduz suas etapas em SQL nativo.
- **Não** tem acesso ao modelo. M não conhece medidas nem relacionamentos.

### 2.2 Analysis Services em processo (`msmdsrv.exe`)

**Este é o coração.** É literalmente o mesmo motor do SQL Server Analysis Services, rodando
como um processo filho do Desktop.

- Guarda o modelo comprimido em memória (**VertiPaq**).
- Executa **DAX** (e também MDX, que é como o Excel consulta o modelo).
- Cria uma pasta de trabalho em
  `%LOCALAPPDATA%\Microsoft\Power BI Desktop\AnalysisServicesWorkspaces\` — que cresce e
  é a causa comum de disco cheio.
- Escuta numa **porta TCP aleatória em `localhost`**. É assim que DAX Studio, Tabular
  Editor e o Excel se conectam ao seu arquivo aberto.

**Consequência prática nº 1:** ao abrir um `.pbix`, o consumo de RAM não é do "programa" —
é do modelo. Um `.pbix` de 300 MB em disco pode ocupar 1,5 GB de RAM (o arquivo é
comprimido em ZIP por cima da compressão do VertiPaq).

**Consequência prática nº 2:** se o Desktop travar, `msmdsrv.exe` pode ficar órfão
segurando GB de RAM. `Stop-Process -Name msmdsrv -Force` resolve.

**Consequência prática nº 3:** é por isso que não existe Power BI Desktop para
macOS/Linux — o motor é Windows.

### 2.3 Camada de relatório (WebView2)

Os visuais são **HTML/JavaScript** renderizados por um Chromium embutido (WebView2). O
mesmo código que roda no navegador do Service roda dentro do Desktop.

Isso explica muita coisa:

- por que o Desktop pede o runtime WebView2 e falha com telas em branco sem ele;
- por que visuais customizados (`.pbiviz`) são pacotes JavaScript;
- por que o relatório fica idêntico no Desktop e no navegador;
- por que "escala de exibição acima de 100%" causa problemas de layout.

### 2.4 O fluxo de um clique

```
Você clica em "Sudeste" numa segmentação
   │
   ▼
1. Camada de relatório (JS) monta um novo contexto de filtro
   │
   ▼
2. Cada visual gera uma consulta DAX (SUMMARIZECOLUMNS...)
   │
   ▼
3. Motor de FÓRMULA (DAX) planeja: monta o plano lógico e o físico
   │
   ▼
4. Motor de ARMAZENAMENTO (VertiPaq) executa varreduras nas colunas
   │   · multithread, sobre dados comprimidos
   │   · devolve datacaches (resultados intermediários)
   ▼
5. Motor de fórmula combina os datacaches (single-thread!)
   │
   ▼
6. Resultado devolvido ao visual → renderização
```

**Essa divisão entre motor de fórmula (FE) e motor de armazenamento (SE) é a base de todo
diagnóstico de desempenho.** O SE é paralelo e rápido; o FE é sequencial e caro. Medida
lenta quase sempre = trabalho demais no FE. Ver [`22-desempenho.md`](22-desempenho.md).

---

## 3. Power BI Service

O que a nuvem faz:

| Função | Detalhe |
|---|---|
| **Hospedar modelos** | O mesmo motor AS, agora numa capacidade compartilhada ou dedicada |
| **Renderizar relatórios** | Mesmo código JS do Desktop |
| **Agendar atualizações** | Até 8×/dia no Pro; 48×/dia em PPU/capacidade |
| **Autenticar e autorizar** | Microsoft Entra ID; funções de workspace; RLS |
| **Distribuir** | Workspaces, org apps com audiências, Teams, SharePoint, e-mail |
| **Expor APIs** | REST (Power BI e Fabric) e **XMLA endpoint** |
| **Governar** | Rótulos de confidencialidade, configurações de locatário, auditoria |

### 3.1 Compartilhada × dedicada

| | Capacidade compartilhada (Pro) | Capacidade dedicada (PPU / F-SKU) |
|---|---|---|
| Recursos | multi-inquilino, sem garantia | reservados, previsíveis |
| Tamanho do modelo | **1 GB** por modelo | de 3 GB a 400 GB, conforme o SKU |
| Refresh | 8×/dia | 48×/dia |
| Tempo máximo de refresh | 2 h | 5 h |
| XMLA gravação | ✘ | ✔ |
| Atualização incremental | ✔ (com limites) | ✔ |
| Direct Lake | ✘ | ✔ |
| Leitores sem licença | ✘ | ✔ **só em F64+** |
| Paginated reports | ✘ | ✔ |

**Os dois limites que mais surpreendem:** o modelo de 1 GB no Pro e o **F64 como divisor**
para leitores sem licença. Detalhes em [`80-custos-e-licencas.md`](80-custos-e-licencas.md).

### 3.2 Relatório × modelo semântico — a separação que muda tudo

Ao publicar, você cria **dois** itens. Isso não é detalhe de implementação:

```
                     ┌───────────────────────────┐
                     │  MODELO SEMÂNTICO         │
                     │  "Vendas Corporativo"     │
                     │  · dados                  │
                     │  · relacionamentos        │
                     │  · 120 medidas            │
                     │  · RLS                    │
                     └────────┬──────────────────┘
            ┌─────────────────┼─────────────────┬──────────────────┐
            ▼                 ▼                 ▼                  ▼
   ┌────────────────┐ ┌──────────────┐ ┌──────────────┐ ┌────────────────┐
   │ Relatório      │ │ Relatório    │ │ Excel        │ │ Copilot /      │
   │ Diretoria      │ │ Comercial    │ │ (Analisar)   │ │ agente         │
   └────────────────┘ └──────────────┘ └──────────────┘ └────────────────┘
```

**Um modelo, muitos consumidores.** Isso é a **camada semântica corporativa** e é a
diferença entre uma empresa com um número e uma empresa com cinco. Como se implementa:
[`23-servico-colaboracao-e-atualizacao.md`](23-servico-colaboracao-e-atualizacao.md).

Quem consome um modelo publicado usa **conexão dinâmica** (*live connection*): o relatório
não tem dados próprios, só consulta o modelo. Isso significa que ele **herda** as medidas,
a RLS e as atualizações.

---

## 4. As outras peças

### 4.1 Power BI Mobile

Apps nativos iOS/Android/Windows. Consomem, não criam.

- Suporta **layout de telefone** definido no Desktop (Exibição → Layout móvel).
  Sem ele, o relatório aparece "encolhido" e ilegível.
- Alertas de dados, anotação e compartilhamento.
- **Novidade de julho/2026:** audiências de org apps chegaram ao mobile.

### 4.2 Power BI Report Server

Servidor instalado **na empresa**, sem nuvem. Existe para bancos, governo, saúde e
empresas com restrição legal de dados.

| Ganha | Perde |
|---|---|
| Dados nunca saem da empresa | Sem Copilot, sem Fabric, sem Direct Lake |
| Controle total de versão | Recursos com ~6–12 meses de atraso |
| Sem custo por usuário (usa licença de capacidade ou SQL Server EE+SA) | Sem dataflows, sem apps, sem pipelines |
| Hospeda também relatórios paginados (`.rdl`) | Exige um Desktop **de versão específica** |

**Armadilha grave:** o Desktop "for Report Server" segue o calendário do servidor
(janeiro/maio/setembro), não o mensal. Abrir um `.pbix` do Report Server na versão mensal
e salvar **impede** a publicação de volta. Ver [`03-instalacao.md`](03-instalacao.md) §2.7.

### 4.3 Power BI Embedded

Relatórios dentro do **seu** aplicativo, para os **seus** clientes.

Dois cenários, e confundi-los custa caro:

| Cenário | Quem vê | Licença |
|---|---|---|
| **App owns data** | Clientes externos, sem conta no seu locatário | Capacidade (F-SKU); token de aplicação |
| **User owns data** | Usuários internos com conta e licença | Licença por usuário |

Ver [`80-custos-e-licencas.md`](80-custos-e-licencas.md).

### 4.4 Relatórios paginados (Power BI Report Builder)

Produto separado, herdeiro do SQL Server Reporting Services. Linguagem: **RDL**, com
expressões em VB.NET; consultas em SQL/DAX/MDX.

**Use quando** o requisito é *pixel-perfect* e paginado: fatura, boleto, extrato,
relatório regulatório de 400 páginas, exportação para PDF com quebras exatas.

**Não use** para análise interativa. É outra ferramenta com outra filosofia.

---

## 5. O gateway, em detalhe

> **On-premises data gateway** — um serviço Windows que faz a ponte entre a nuvem e dados
> que estão dentro da empresa.

### 5.1 Como funciona (e por que não precisa abrir porta de entrada)

```
Power BI Service                  Azure Service Bus              Gateway
(nuvem)                           (relay)                        (empresa)
    │                                   │                            │
    │  "atualize o modelo X"            │  ◄────── conexão de SAÍDA ─┤
    ├──────────────────────────────────►│          persistente        │
    │                                   ├───────────────────────────►│
    │                                   │   entrega a instrução       │
    │                                   │                            ├──► SQL Server
    │                                   │◄───────────────────────────┤    (rede interna)
    │◄──────────────────────────────────┤   devolve os dados          │
    │      dados criptografados         │   (comprimidos)             │
```

**Ponto crucial:** o gateway abre a conexão **de dentro para fora**. Nenhuma porta de
entrada precisa ser aberta no firewall — argumento decisivo em conversa com segurança.

Portas de **saída** necessárias: TCP 443, 5671, 5672 e 9350–9354. Se só 443 estiver
liberada, é possível forçar o modo "somente HTTPS" (mais lento, mais compatível).

### 5.2 Onde o gateway entra e onde não entra

| Cenário | Precisa de gateway? |
|---|---|
| Fonte na nuvem (Azure SQL, Snowflake público, API) | Não |
| SQL Server na rede da empresa | **Sim** |
| Arquivo em `C:\` da sua máquina | **Sim** (e é péssima ideia) |
| Arquivo em pasta de rede `\\servidor\` | **Sim** |
| Arquivo no SharePoint Online / OneDrive for Business | Não |
| Import de dados já atualizados | Só no refresh |
| DirectQuery para fonte on-premises | **Sim, a cada consulta** ★ |

**A linha ★ é a que derruba projetos:** com DirectQuery, o gateway participa de **toda
consulta de todo usuário**. Um gateway subdimensionado vira gargalo instantâneo. Se você
vai usar DirectQuery on-premises, dimensione o gateway como um servidor de produção e use
**cluster** (dois ou mais nós) desde o começo.

### 5.3 Dimensionamento

Ponto de partida: **8 vCPU / 16 GB RAM / SSD**, num servidor sempre ligado, na mesma rede
da fonte. O gateway descomprime e recomprime dados durante o refresh — é trabalho de CPU
e memória, não só de rede.

---

## 6. Onde cada coisa executa — tabela de referência

| Operação | Onde executa | Quando |
|---|---|---|
| Passos do Power Query | Mashup Engine (Desktop ou capacidade) — ou **na fonte**, se dobrar | Refresh |
| Coluna do Power Query | Idem | Refresh |
| Coluna calculada (DAX) | Motor AS | Refresh (depois do M) |
| Tabela calculada (DAX) | Motor AS | Refresh |
| **Medida (DAX)** | Motor AS (FE + SE) | **Toda consulta** |
| Cálculo visual | Motor AS, sobre a matriz do visual | Toda consulta |
| RLS | Motor AS, antes de tudo | Toda consulta |
| Renderização | WebView2 / navegador | Toda interação |
| Formatação condicional | Depende: DAX no motor, cores no cliente | Ambos |
| Exportação para Excel | Service | Sob demanda |

**A leitura estratégica desta tabela:** tudo que estiver na linha "toda consulta" é
multiplicado pelo número de usuários × interações. Otimizar refresh economiza minutos por
dia; otimizar medida economiza horas por dia.

---

## 7. Ordem de carregamento — por que isso derruba modelos

Durante um refresh, a ordem é rígida:

```
1. Power Query avalia as consultas (paralelo, com limite configurável)
2. Dados são carregados e comprimidos pelo VertiPaq
3. Colunas calculadas são avaliadas
4. Tabelas calculadas são avaliadas
5. Relacionamentos são construídos
6. Hierarquias e estruturas auxiliares são construídas
```

**Consequências:**

- Coluna calculada **não pode** referenciar uma tabela calculada que dependa dela
  (referência circular).
- Uma tabela calculada que dependa de outra tabela calculada adiciona uma rodada.
- Tabelas calculadas grandes **retardam todo refresh**, sempre. Se puder calcular no M ou
  na fonte, calcule lá.
- `CALENDARAUTO()` varre **todas** as colunas de data do modelo. Numa modelagem
  desatenta, isso gera uma tabela de datas de 1900 a 2999.

---

## 8. Limites que você vai encontrar

Números vigentes em 14/08/2026; a Microsoft os revisa — confirme antes de prometer.

| Limite | Valor |
|---|---|
| Tamanho do modelo (Pro) | 1 GB |
| Tamanho do modelo (PPU) | 100 GB |
| Tamanho do modelo (F-SKU) | de 3 GB (F2) a 400 GB (F2048) |
| Refreshes agendados (Pro) | 8/dia |
| Refreshes agendados (PPU/capacidade) | 48/dia |
| Duração máxima de refresh (Pro) | 2 h |
| Duração máxima de refresh (capacidade) | 5 h |
| Upload de `.pbix` pela interface | 1 GB |
| Linhas exportadas para Excel (resumido) | 150.000 |
| Linhas exportadas para `.csv` | 30.000 |
| Linhas devolvidas por uma consulta DAX de visual | 1.000.000 |
| Cardinalidade de coluna | ~1,999 bilhão de valores distintos |
| Colunas por tabela | 16.000 |
| Timeout de consulta DAX no Service | 225 s (visual) |

---

## 9. Os cinco porquês: por que o Desktop precisa do Analysis Services em processo?

1. **Por que não calcular direto no arquivo?**
   Porque DAX exige um motor com índices, dicionários e planos de consulta. Não é
   aritmética sobre um arquivo.

2. **Por que não usar um serviço remoto?**
   Porque a autoria precisa ser **interativa**: você cria uma medida e vê o resultado em
   milissegundos. Latência de rede tornaria a experiência insuportável.

3. **Por que reaproveitar o SSAS em vez de escrever um motor mais leve?**
   Por consistência semântica. O modelo criado no Desktop precisa se comportar
   **exatamente** igual depois de publicado. Dois motores diferentes divergiriam em casos
   de borda — e casos de borda em DAX são muitos. Reusar o mesmo código elimina uma classe
   inteira de bugs "funciona no meu Desktop".

4. **Por que isso impede a versão para macOS/Linux?**
   Porque `msmdsrv.exe` é um binário Windows com décadas de dependências da plataforma.
   Portá-lo seria um projeto do tamanho de reescrever o SSAS.

5. **Parada legítima — trade-off de engenharia assumido.**
   A Microsoft trocou portabilidade por consistência. A aposta é que o cliente-alvo
   (empresa que já usa Microsoft 365 e Windows) não sente falta. **Opinião do autor:** foi
   a decisão certa em 2015 e é um problema crescente em 2026, à medida que a autoria
   migra para o navegador — o que, aliás, é exatamente o que a Microsoft vem fazendo com
   a modelagem na web e o TMDL na web.

---

## 10. Autoteste

1. Quais são os três motores dentro do Power BI Desktop e o que cada um faz?
2. Por que o Desktop consome tanta RAM? Qual processo é o responsável?
3. Como o DAX Studio se conecta ao seu arquivo aberto?
4. Descreva o caminho de um clique numa segmentação até o número na tela.
5. Qual a diferença entre motor de fórmula e motor de armazenamento, e por que ela importa?
6. Por que publicar cria dois itens, e qual a consequência arquitetural disso?
7. Em que situação o gateway participa de **toda consulta** e não só do refresh?
8. Por que o gateway não exige abrir porta de entrada no firewall?
9. Cite três coisas que executam "a cada consulta" e explique por que otimizá-las importa
   mais que otimizar o refresh.
10. Por que não existe Power BI Desktop para macOS? Dê a razão técnica, não a comercial.

---

**Próximo:** [`13-power-query-e-m.md`](13-power-query-e-m.md) — conectar e transformar.
